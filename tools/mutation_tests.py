#!/usr/bin/env python3
"""N36 Mutation Testing Harness & Corpus Validator.

Validates the declared mutant corpus against real sources, runs each mutant
inside an isolated scratch copy of tools/ and src/, verifies strict digest
hygiene (plus nonexistent-function and unrestored-leak fixtures), and produces
the kill table.

Usage:
    python3 tools/mutation_tests.py [--repo-root PATH] [--corpus PATH]
                                    [--report PATH] [--json]
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CORPUS = 'data/mutant_corpus.json'


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digests(root: Path, rel_paths: list[str]) -> dict[str, str]:
    return {rel: _sha256_file(root / rel) for rel in sorted(set(rel_paths))}


def _find_function_in_file(path: Path, func_name: str) -> bool:
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.py':
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return True
        return False
    if path.suffix == '.js':
        return bool(re.search(rf'\bfunction\s+{re.escape(func_name)}\s*\(', text))
    return False


def validate_corpus(repo_root: Path, corpus: dict[str, Any]) -> list[str]:
    """Validate every mutant's file, function, and exact unique target snippet."""
    errors: list[str] = []
    mutants = corpus.get('mutants', [])
    if not mutants:
        errors.append('Corpus contains zero mutants')
        return errors
    for m in mutants:
        mid = m.get('id', '<unknown>')
        rel = m.get('file', '')
        func = m.get('function', '')
        target = m.get('target', '')
        fpath = repo_root / rel
        if not fpath.exists():
            errors.append(f'{mid}: missing file {rel}')
            continue
        if not _find_function_in_file(fpath, func):
            errors.append(f'{mid}: function {func!r} not found in {rel}')
        text = fpath.read_text(encoding='utf-8')
        count = text.count(target)
        if count != 1:
            errors.append(f'{mid}: target snippet in {rel} matched {count} times (expected 1)')
    return errors


def _run_nonexistent_func_fixture(repo_root: Path) -> dict[str, Any]:
    """B.1.1 scratch fixture: mutant pointing at nonexistent function must be rejected by name."""
    scratch_corpus = {
        'mutants': [
            {
                'id': 'FIX-MUT-BAD-FUNC',
                'file': 'tools/quantity_engine.py',
                'function': 'nonexistent_function_n36',
                'target': '        if diff <= abs_tol:',
                'replacement': '        if diff >= abs_tol:',
            }
        ]
    }
    errs = validate_corpus(repo_root, scratch_corpus)
    detected = any('nonexistent_function_n36' in e for e in errs)
    return {
        'id': 'FIX-MUT-NONEXISTENT-FUNC',
        'detected': detected,
        'errors_reported': errs,
    }


def _check_hygiene(expected_digests: dict[str, str], scratch_root: Path) -> list[str]:
    actual = _tree_digests(scratch_root, list(expected_digests.keys()))
    leaks: list[str] = []
    for rel, exp in expected_digests.items():
        if actual.get(rel) != exp:
            leaks.append(rel)
    return leaks


def _run_leak_fixture(repo_root: Path, corpus: dict[str, Any]) -> dict[str, Any]:
    """B.1.2 leak fixture: deliberately unrestored scratch run must be flagged by exit digest check."""
    m0 = corpus['mutants'][0]
    rel = m0['file']
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / 'scratch'
        (scratch / Path(rel).parent).mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / rel, scratch / rel)
        expected = _tree_digests(scratch, [rel])
        # Deliberately apply mutant without restoring
        text = (scratch / rel).read_text(encoding='utf-8')
        (scratch / rel).write_text(text.replace(m0['target'], m0['replacement'], 1), encoding='utf-8')
        leaks = _check_hygiene(expected, scratch)
    return {
        'id': 'FIX-MUT-LEAK',
        'detected': rel in leaks,
        'flagged_files': leaks,
    }


def _prepare_scratch_repo(repo_root: Path, scratch_root: Path) -> None:
    """Create an isolated scratch workspace: copy tools/ and src/, symlink read-only data/output/evidence."""
    shutil.copytree(repo_root / 'tools', scratch_root / 'tools', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(repo_root / 'src', scratch_root / 'src')
    for ro_dir in ('data', 'docs', 'output', 'evidence'):
        src_dir = repo_root / ro_dir
        if src_dir.exists():
            (scratch_root / ro_dir).symlink_to(src_dir)


def run_mutations(repo_root: Path = DEFAULT_ROOT, corpus_path: Path | None = None) -> dict[str, Any]:
    t0 = time.monotonic()
    cpath = corpus_path or (repo_root / DEFAULT_CORPUS)
    corpus = json.loads(cpath.read_text(encoding='utf-8'))

    validation_errors = validate_corpus(repo_root, corpus)
    bad_func_fixture = _run_nonexistent_func_fixture(repo_root)
    leak_fixture = _run_leak_fixture(repo_root, corpus)

    mutants = corpus.get('mutants', [])
    target_files = sorted({m['file'] for m in mutants})
    real_before = _tree_digests(repo_root, target_files)

    kill_table: list[dict[str, Any]] = []
    hygiene_failures: list[str] = []

    if not validation_errors:
        with tempfile.TemporaryDirectory() as tmp:
            scratch = Path(tmp) / 'repo'
            scratch.mkdir(parents=True, exist_ok=True)
            _prepare_scratch_repo(repo_root, scratch)
            scratch_expected = _tree_digests(scratch, target_files)

            for m in mutants:
                mid = m['id']
                rel = m['file']
                kind = m.get('kind', 'killable')
                fpath = scratch / rel
                orig_text = fpath.read_text(encoding='utf-8')
                mutated_text = orig_text.replace(m['target'], m['replacement'], 1)

                man_file = Path(tmp) / f'{mid}_manifest.json'
                try:
                    fpath.write_text(mutated_text, encoding='utf-8')
                    proc = subprocess.run(
                        [
                            sys.executable,
                            str(scratch / 'tools/property_tests.py'),
                            '--repo-root', str(scratch),
                            '--manifest', str(man_file),
                        ],
                        capture_output=True, text=True, cwd=str(scratch),
                    )
                finally:
                    fpath.write_text(orig_text, encoding='utf-8')

                leaks = _check_hygiene(scratch_expected, scratch)
                if leaks:
                    hygiene_failures.append(f'{mid}: unrestored files {leaks}')

                manifest = json.loads(man_file.read_text(encoding='utf-8')) if man_file.exists() else {}
                killers = [t['id'] for t in manifest.get('tests', []) if t.get('status') != 'PASS']
                if proc.returncode != 0 and not killers:
                    killers = ['SUBPROCESS_EXIT_NONZERO']

                if kind == 'equivalent':
                    verdict = 'EQUIVALENT' if not killers else 'UNEXPECTED_KILL'
                else:
                    verdict = 'KILLED' if killers else 'SURVIVED'

                kill_table.append({
                    'id': mid,
                    'file': rel,
                    'function': m['function'],
                    'kind': kind,
                    'expected_killer_class': m['expected_killer_class'],
                    'actual_killers': killers,
                    'verdict': verdict,
                    'equivalence_analysis': m.get('equivalence_analysis', ''),
                    'hygiene_clean': not leaks,
                })

    real_after = _tree_digests(repo_root, target_files)
    real_untouched = real_before == real_after

    killed_count = sum(1 for r in kill_table if r['verdict'] == 'KILLED')
    equivalent_count = sum(1 for r in kill_table if r['verdict'] == 'EQUIVALENT')
    survived_count = sum(1 for r in kill_table if r['verdict'] in ('SURVIVED', 'UNEXPECTED_KILL'))
    killable_total = sum(1 for m in mutants if m.get('kind', 'killable') == 'killable')

    all_ok = (
        not validation_errors
        and bad_func_fixture['detected']
        and leak_fixture['detected']
        and not hygiene_failures
        and real_untouched
        and killed_count == killable_total
        and survived_count == 0
    )

    return {
        'schema_version': 1,
        'task': 'N36',
        'status': 'PASS' if all_ok else 'FAIL',
        'corpus_sha256': _sha256_file(cpath),
        'total_mutants': len(mutants),
        'killable_mutants': killable_total,
        'killed_count': killed_count,
        'equivalent_count': equivalent_count,
        'survived_count': survived_count,
        'validation_errors': validation_errors,
        'nonexistent_func_fixture': bad_func_fixture,
        'leak_fixture': leak_fixture,
        'hygiene_failures': hygiene_failures,
        'real_sources_untouched': real_untouched,
        'duration_ms': round((time.monotonic() - t0) * 1000.0, 3),
        'kill_table': kill_table,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(DEFAULT_ROOT))
    parser.add_argument('--corpus', default=DEFAULT_CORPUS)
    parser.add_argument('--report', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    cpath = Path(args.corpus)
    if not cpath.is_absolute():
        cpath = root / cpath

    report = run_mutations(repo_root=root, corpus_path=cpath)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"{report['status']} N36 mutation suite: killed={report['killed_count']}/{report['killable_mutants']}, "
            f"equivalent={report['equivalent_count']}, survived={report['survived_count']}, "
            f"hygiene={'CLEAN' if report['real_sources_untouched'] and not report['hygiene_failures'] else 'DIRTY'}, "
            f"duration={report['duration_ms']}ms"
        )
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
