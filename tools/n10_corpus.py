#!/usr/bin/env python3
"""Deterministic N10 verification corpus:
- Island validation, unit-grammar fixtures, and stub-closure check (incl. missed-key corner case)
- Planted-failure lint corpus + prose-exemption fixture + nested-unit corner case
- Build-gate refusal (no artifact written, first failure named) + clean build
- Full-document rendered term scan + N10 runtime harness
- Double-build parity + byte accounting + prior-phase regressions (N02..N08)
"""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_terms import (  # noqa: E402
    TERMS_PATH,
    UnitGrammarError,
    check_dimension_match,
    check_stub_closure,
    parse_unit,
    scan_rendered_document,
    validate_all,
)


def _run_cmd(cmd: list[str], cwd: Path = DEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _grammar_fixtures(terms_data: dict[str, Any]) -> dict[str, Any]:
    grammar = terms_data['unit_grammar']
    valid_inputs = ['g/mol', 'mg/mL', 'J/(mol·K)', 'L/(mol·cm)', '(mol/L)^2', 's^-1', '% (m/V)']
    valid_out: list[dict[str, Any]] = []
    for u in valid_inputs:
        parsed = parse_unit(u, grammar)
        valid_out.append({'unit': u, 'kind': parsed['kind'], 'dimension_vector': parsed['dimension_vector']})

    invalid_specs = [
        ('unknown_element_xyz', 'xyz', None, 'E_UNIT_UNKNOWN_ELEMENT'),
        ('unknown_lowercase_ml', 'ml', None, 'E_UNIT_UNKNOWN_ELEMENT'),
        ('malformed_double_slash', 'g//mol', None, 'E_UNIT_MALFORMED_SEPARATOR'),
        ('malformed_asterisk', 'J/(mol*K)', None, 'E_UNIT_MALFORMED_SEPARATOR'),
        ('ambiguous_denominator', 'J/mol·K', None, 'E_UNIT_AMBIGUOUS_DENOMINATOR'),
        ('flipped_ml_per_mg_for_density', 'mL/mg', 'density', 'E_UNIT_DIMENSION_MISMATCH'),
        ('molar_conc_for_density', 'mol/L', 'density', 'E_UNIT_DIMENSION_MISMATCH'),
    ]
    invalid_out: list[dict[str, Any]] = []
    all_ok = True
    for name, u, dim, want_code in invalid_specs:
        if dim is not None:
            ok, err, _ = check_dimension_match(u, dim, grammar)
            passed = (not ok) and (err is not None) and (want_code in err)
            invalid_out.append({'case': name, 'unit': u, 'dimension': dim, 'status': 'PASS' if passed else 'FAIL', 'error': err})
            if not passed:
                all_ok = False
        else:
            try:
                parse_unit(u, grammar)
                all_ok = False
                invalid_out.append({'case': name, 'unit': u, 'status': 'FAIL', 'error': 'unexpected parse'})
            except UnitGrammarError as exc:
                passed = exc.code == want_code
                if not passed:
                    all_ok = False
                invalid_out.append({'case': name, 'unit': u, 'status': 'PASS' if passed else 'FAIL', 'error_code': exc.code, 'error': str(exc)})

    return {
        'status': 'PASS' if all_ok else 'FAIL',
        'valid_fixtures': valid_out,
        'invalid_fixtures': invalid_out,
    }


def _planted_corpus_and_gate_refusals(terms_data: dict[str, Any]) -> dict[str, Any]:
    by_key = {e['key']: e for e in terms_data['terms']}
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        def norm_err(msg: str | None) -> str | None:
            return msg.replace(str(tmp_dir), '<tmp>') if msg else None

        # 1. Stub-closure corner case: missed authoring key listed by key and task
        bad_n09_stub = {
            'schema_version': 1,
            'owner': 'N09',
            'target_closure_task': 'N10',
            'keys': [
                {'key': 'feedback.correct', 'text_lv': 'Pareizi'},
                {'key': 'feedback.missed_n09_key', 'text_lv': 'Neiekļauta atslēga'},
            ],
        }
        p_stub = tmp_dir / 'bad_n09_stub.json'
        p_stub.write_text(json.dumps(bad_n09_stub, ensure_ascii=False), encoding='utf-8')
        closure_bad = check_stub_closure(by_key, n09_stubs_path=p_stub)
        results.append({
            'id': 'NEG-STUB-MISSED-KEY',
            'status': 'PASS' if closure_bad['status'] == 'FAIL' and any(m['task'] == 'N09' and m['key'] == 'feedback.missed_n09_key' for m in closure_bad['missing_entries']) else 'FAIL',
            'missing_entries': closure_bad['missing_entries'],
        })

        # 2. Planted invalid unit string in extra data
        p_bad_unit = tmp_dir / 'planted_bad_unit.json'
        p_bad_unit.write_text(json.dumps({'items': [{'id': 'X1', 'unit': 'J/mol·K'}]}, ensure_ascii=False), encoding='utf-8')
        r_unit = validate_all(extra_data_paths=[p_bad_unit])
        results.append({
            'id': 'NEG-PLANTED-INVALID-UNIT',
            'status': 'PASS' if r_unit['status'] == 'FAIL' and any('E_UNIT_AMBIGUOUS_DENOMINATOR' in e for e in r_unit['errors']) else 'FAIL',
            'error': norm_err(r_unit['errors'][0] if r_unit['errors'] else None),
        })

        # 3. Planted unknown term key
        p_bad_key = tmp_dir / 'planted_unknown_key.json'
        p_bad_key.write_text(json.dumps({'items': [{'id': 'X2', 'term_key': 'term.does_not_exist'}]}, ensure_ascii=False), encoding='utf-8')
        r_key = validate_all(extra_data_paths=[p_bad_key])
        results.append({
            'id': 'NEG-PLANTED-UNKNOWN-KEY',
            'status': 'PASS' if r_key['status'] == 'FAIL' and any('E_TERMS_UNKNOWN_KEY' in e and 'term.does_not_exist' in e for e in r_key['errors']) else 'FAIL',
            'error': norm_err(r_key['errors'][0] if r_key['errors'] else None),
        })

        # 4. Planted dimension mismatch (density term carrying mol/L)
        bad_terms_dim = copy.deepcopy(terms_data)
        for e in bad_terms_dim['terms']:
            if e['key'] == 'qty.density':
                e['unit'] = 'mol/L'
        p_bad_dim = tmp_dir / 'planted_dim_mismatch.json'
        p_bad_dim.write_text(json.dumps(bad_terms_dim, ensure_ascii=False), encoding='utf-8')
        r_dim = validate_all(terms_path=p_bad_dim)
        results.append({
            'id': 'NEG-PLANTED-DIMENSION-MISMATCH',
            'status': 'PASS' if r_dim['status'] == 'FAIL' and any('E_UNIT_DIMENSION_MISMATCH' in e and 'qty.density' in e for e in r_dim['errors']) else 'FAIL',
            'error': r_dim['errors'][0] if r_dim['errors'] else None,
        })

        # 5. Planted bad nested unit in quantity text_lv (C.1.1)
        bad_terms_nest = copy.deepcopy(terms_data)
        for e in bad_terms_nest['terms']:
            if e['key'] == 'qty.density_with_unit_label':
                e['text_lv'] = 'šķīduma blīvums ρ (mL/mg)'
        p_bad_nest = tmp_dir / 'planted_bad_nested.json'
        p_bad_nest.write_text(json.dumps(bad_terms_nest, ensure_ascii=False), encoding='utf-8')
        r_nest = validate_all(terms_path=p_bad_nest)
        results.append({
            'id': 'NEG-PLANTED-NESTED-UNIT',
            'status': 'PASS' if r_nest['status'] == 'FAIL' and any('E_UNIT_DIMENSION_MISMATCH' in e and 'nested' in e for e in r_nest['errors']) else 'FAIL',
            'error': r_nest['errors'][0] if r_nest['errors'] else None,
        })

        # 6. Prose-exemption corner case: free-text prose quoting unit slips passes by design
        p_prose = tmp_dir / 'prose_exemption.json'
        p_prose.write_text(json.dumps({
            'items': [{
                'id': 'PROSE-1',
                'term_key': 'feedback.incorrect',
                'feedback_lv': 'Uzmanību: tekstā bieži kļūdaini raksta ml vai J/mol*K vai apgriež mL/mg.',
            }],
        }, ensure_ascii=False), encoding='utf-8')
        r_prose = validate_all(extra_data_paths=[p_prose])
        results.append({
            'id': 'EDGE-PROSE-EXEMPTION',
            'status': 'PASS' if r_prose['status'] == 'PASS' else 'FAIL',
            'exempt_prose_fields': r_prose['lint']['exempt_prose_fields'],
        })

        # 7. Build-gate refusal on planted failing dataset (must exit != 0, write NO artifact, name first failure)
        refusal_out = tmp_dir / 'refused_sim.html'
        refusal_man = tmp_dir / 'refused_manifest.json'
        proc_gate = _run_cmd([
            sys.executable, 'tools/build.py',
            '--terms', str(p_bad_dim),
            '--out', str(refusal_out),
            '--manifest-out', str(refusal_man),
        ])
        results.append({
            'id': 'GATE-REFUSAL-DIMENSION-MISMATCH',
            'status': 'PASS' if proc_gate.returncode != 0 and not refusal_out.exists() and 'terminology' in proc_gate.stderr and 'E_UNIT_DIMENSION_MISMATCH' in proc_gate.stderr else 'FAIL',
            'returncode': proc_gate.returncode,
            'artifact_written': refusal_out.exists(),
            'stderr_head': proc_gate.stderr.splitlines()[0] if proc_gate.stderr else '',
        })

        # 8. Build-gate refusal via --extra-data (planted invalid unit + unknown key)
        refusal_out2 = tmp_dir / 'refused_sim2.html'
        refusal_man2 = tmp_dir / 'refused_manifest2.json'
        proc_gate2 = _run_cmd([
            sys.executable, 'tools/build.py',
            '--extra-data', str(p_bad_unit),
            '--out', str(refusal_out2),
            '--manifest-out', str(refusal_man2),
        ])
        results.append({
            'id': 'GATE-REFUSAL-EXTRA-DATA-UNIT',
            'status': 'PASS' if proc_gate2.returncode != 0 and not refusal_out2.exists() and 'terminology' in proc_gate2.stderr else 'FAIL',
            'returncode': proc_gate2.returncode,
            'artifact_written': refusal_out2.exists(),
            'stderr_head': norm_err(proc_gate2.stderr.splitlines()[0] if proc_gate2.stderr else ''),
        })

    return {
        'status': 'PASS' if all(r['status'] == 'PASS' for r in results) else 'FAIL',
        'fixtures': results,
    }


def _double_build_parity() -> dict[str, Any]:
    out_path = DEST / 'output/simulator.html'
    man_path = DEST / 'output/build-manifest.json'
    p1 = _run_cmd([sys.executable, 'tools/build.py'])
    b1, j1 = out_path.read_bytes(), man_path.read_bytes()
    p2 = _run_cmd([sys.executable, 'tools/build.py'])
    b2, j2 = out_path.read_bytes(), man_path.read_bytes()
    manifest = json.loads(j1.decode('utf-8'))
    return {
        'status': 'PASS' if p1.returncode == 0 and p2.returncode == 0 and b1 == b2 and j1 == j2 else 'FAIL',
        'output_sha256': sha256_bytes(b1),
        'output_bytes': len(b1),
        'manifest_sha256': sha256_bytes(j1),
        'byte_identical': b1 == b2 and j1 == j2,
        'terms_island_bytes': manifest['terms_island']['bytes'],
        'terms_loader_js_bytes': manifest['terms_island']['terms_loader_js_bytes'],
        'runtime_js_bytes': manifest['tokens_layer']['runtime_js_bytes'],
        'css_bytes': manifest['tokens_layer']['css_bytes'],
    }


def _prior_regressions() -> list[dict[str, Any]]:
    checks = [
        ('N02', ['node', 'tools/check_coverage_runtime.js', '--json']),
        ('N03', ['node', 'tools/check_conventions_runtime.js']),
        ('N05', ['node', 'tools/check_golden_vectors_runtime.js']),
        ('N06', ['node', 'tools/check_n06_runtime.js']),
        ('N07', ['node', 'tools/check_n07_runtime.js']),
        ('N08', ['node', 'tools/check_n08_runtime.js']),
    ]
    out: list[dict[str, Any]] = []
    for owner, cmd in checks:
        proc = _run_cmd(cmd)
        out.append({
            'owner': owner,
            'command': ' '.join(cmd),
            'status': 'PASS' if proc.returncode == 0 else 'FAIL',
            'returncode': proc.returncode,
        })
    return out


def run_corpus() -> dict[str, Any]:
    terms_data = load_json(DEST / TERMS_PATH)
    val_report = validate_all()
    grammar_fixtures = _grammar_fixtures(terms_data)
    planted = _planted_corpus_and_gate_refusals(terms_data)
    parity = _double_build_parity()
    html_scan = scan_rendered_document(DEST / 'output/simulator.html', terms_data)

    rt_proc = _run_cmd(['node', 'tools/check_n10_runtime.js'])
    if rt_proc.returncode != 0:
        raise RuntimeError(f"check_n10_runtime.js failed:\n{rt_proc.stderr}\n{rt_proc.stdout}")
    rt_data = json.loads(rt_proc.stdout)

    regressions = _prior_regressions()

    all_ok = (
        val_report['status'] == 'PASS'
        and grammar_fixtures['status'] == 'PASS'
        and planted['status'] == 'PASS'
        and parity['status'] == 'PASS'
        and html_scan['status'] == 'PASS'
        and rt_data['status'] == 'PASS'
        and all(r['status'] == 'PASS' for r in regressions)
    )

    return {
        'schema_version': 1,
        'task': 'N10',
        'status': 'PASS' if all_ok else 'FAIL',
        'validation': val_report,
        'grammar_fixtures': grammar_fixtures,
        'planted_corpus': planted,
        'html_scan': html_scan,
        'runtime_fixtures': rt_data,
        'double_build_parity': parity,
        'prior_phase_regressions': regressions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run deterministic N10 corpus.')
    parser.add_argument('--out', type=Path, default=DEST / 'evidence/N10_CORPUS_RECORD.json')
    args = parser.parse_args(argv)

    record = run_corpus()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N10 corpus: {record['status']} -> {args.out} (sha256={sha256_file(args.out)})")
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
