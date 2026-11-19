#!/usr/bin/env python3
"""Deterministic N08 verification corpus: negative fixtures, rendered leak scan,
build gate refusal, double-build parity, runtime harness and prior-phase regressions.
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
from validate_n08_layers import (  # noqa: E402
    EXAMPLES_PATH, GOLDEN_VECTORS_PATH, RECALL_LAYERS_PATH,
    extract_family_answer_tokens, scan_text_for_leaks, validate_all,
)


def _run_cmd(cmd: list[str], cwd: Path = DEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _negative_fixtures() -> list[dict[str, Any]]:
    base = load_json(DEST / RECALL_LAYERS_PATH)
    results: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        # 1. Unknown concept id
        bad_concept = copy.deepcopy(base)
        bad_concept['families'][0]['layers'][1]['concept_id'] = 'P9-99'
        p1 = tmp_dir / 'bad_concept.json'
        p1.write_text(json.dumps(bad_concept, ensure_ascii=False), encoding='utf-8')
        r1 = validate_all(layers_path=p1)
        results.append({
            'id': 'NEG-BAD-CONCEPT',
            'status': 'PASS' if r1['status'] == 'FAIL' and any('P9-99' in e for e in r1['errors']) else 'FAIL',
            'error': r1['errors'][0] if r1['errors'] else None,
        })

        # 2. Unresolved citation
        bad_cit = copy.deepcopy(base)
        bad_cit['families'][2]['layers'][2]['citation'] = {'kind': 'convention', 'id': 'CIT-DOES-NOT-EXIST'}
        p2 = tmp_dir / 'bad_cit.json'
        p2.write_text(json.dumps(bad_cit, ensure_ascii=False), encoding='utf-8')
        r2 = validate_all(layers_path=p2)
        results.append({
            'id': 'NEG-BAD-CITATION',
            'status': 'PASS' if r2['status'] == 'FAIL' and any('CIT-DOES-NOT-EXIST' in e for e in r2['errors']) else 'FAIL',
            'error': r2['errors'][0] if r2['errors'] else None,
        })

        # 3. Planted data leak (8,00 g in FAM-1C)
        planted_leak = copy.deepcopy(base)
        for fam in planted_leak['families']:
            if fam['family_id'] == 'FAM-1C':
                fam['layers'][2]['text_lv'] += ' Piemēram, masa ir 8,00 g.'
        p3 = tmp_dir / 'planted_leak.json'
        p3.write_text(json.dumps(planted_leak, ensure_ascii=False), encoding='utf-8')
        r3 = validate_all(layers_path=p3)
        results.append({
            'id': 'NEG-PLANTED-DATA-LEAK',
            'status': 'PASS' if r3['status'] == 'FAIL' and any('E_LEAK_DETECTED' in e and 'FAM-1C' in e for e in r3['errors']) else 'FAIL',
            'error': r3['errors'][0] if r3['errors'] else None,
        })

        # 4. Depth rule violation (FAM-1A one_step=4)
        bad_depth = copy.deepcopy(base)
        bad_depth['families'][0]['max_depth_by_variant_class']['one_step'] = 4
        p4 = tmp_dir / 'bad_depth.json'
        p4.write_text(json.dumps(bad_depth, ensure_ascii=False), encoding='utf-8')
        r4 = validate_all(layers_path=p4)
        results.append({
            'id': 'NEG-DEPTH-RULE-VIOLATION',
            'status': 'PASS' if r4['status'] == 'FAIL' and any('depth rule' in e.lower() for e in r4['errors']) else 'FAIL',
            'error': r4['errors'][0] if r4['errors'] else None,
        })

        # 5. Build gate refusal on planted leak (must exit 1 and write NO artifact)
        refusal_out = tmp_dir / 'refused_sim.html'
        refusal_man = tmp_dir / 'refused_manifest.json'
        proc = _run_cmd([
            sys.executable, 'tools/build.py',
            '--recall-layers', str(p3),
            '--out', str(refusal_out),
            '--manifest-out', str(refusal_man),
        ])
        results.append({
            'id': 'GATE-REFUSAL-PLANTED-LEAK',
            'status': 'PASS' if proc.returncode != 0 and not refusal_out.exists() and 'recall_layers' in proc.stderr else 'FAIL',
            'returncode': proc.returncode,
            'artifact_written': refusal_out.exists(),
            'stderr_head': proc.stderr.splitlines()[0] if proc.stderr else '',
        })

    return results


def _rendered_leak_scan(rendered_families: list[dict[str, str]]) -> dict[str, Any]:
    gv = load_json(DEST / GOLDEN_VECTORS_PATH)
    ex = load_json(DEST / EXAMPLES_PATH)
    tokens_by_fam = extract_family_answer_tokens(gv, ex)

    findings: list[dict[str, Any]] = []
    for item in rendered_families:
        fid = item['family_id']
        findings.extend(
            scan_text_for_leaks(fid, 'rendered', item['rendered_text'], tokens_by_fam.get(fid, []), surface='rendered')
        )

    # Edge case: degenerate-parameter formula symbols must NOT false-positive
    formula_edge_text = 'A = ε·l·c; l = 1 cm; ΔfH° = 0; c₁·V₁ = c₂·V₂; 1. Virziena norāde; 4. Risinājuma pirmais solis.'
    edge_findings = scan_text_for_leaks('FAM-1C', 'edge-formula', formula_edge_text, tokens_by_fam.get('FAM-1C', []), surface='rendered')

    # Planted rendered leak must fail by name
    planted_rendered_text = '4. Risinājuma pirmais solis. Aprēķinātais rezultāts ir 8.00 g.'
    planted_findings = scan_text_for_leaks('FAM-1C', 'planted-rendered', planted_rendered_text, tokens_by_fam.get('FAM-1C', []), surface='rendered')

    return {
        'status': 'PASS' if not findings and not edge_findings and len(planted_findings) >= 1 else 'FAIL',
        'scanned_families': len(rendered_families),
        'clean_findings_count': len(findings),
        'formula_symbol_edge_case_findings': len(edge_findings),
        'planted_rendered_leak_caught': len(planted_findings) >= 1,
        'planted_rendered_leak_sample': planted_findings[0] if planted_findings else None,
    }


def _double_build_parity() -> dict[str, Any]:
    out_path = DEST / 'output/simulator.html'
    man_path = DEST / 'output/build-manifest.json'
    p1 = _run_cmd([sys.executable, 'tools/build.py'])
    b1, j1 = out_path.read_bytes(), man_path.read_bytes()
    p2 = _run_cmd([sys.executable, 'tools/build.py'])
    b2, j2 = out_path.read_bytes(), man_path.read_bytes()
    return {
        'status': 'PASS' if p1.returncode == 0 and p2.returncode == 0 and b1 == b2 and j1 == j2 else 'FAIL',
        'output_sha256': sha256_bytes(b1),
        'output_bytes': len(b1),
        'manifest_sha256': sha256_bytes(j1),
        'byte_identical': b1 == b2 and j1 == j2,
    }


def _prior_regressions() -> list[dict[str, Any]]:
    checks = [
        ('N02', ['node', 'tools/check_coverage_runtime.js', '--json']),
        ('N03', ['node', 'tools/check_conventions_runtime.js']),
        ('N05', ['node', 'tools/check_golden_vectors_runtime.js']),
        ('N06', ['node', 'tools/check_n06_runtime.js']),
        ('N07', ['node', 'tools/check_n07_runtime.js']),
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
    val_report = validate_all()
    neg_results = _negative_fixtures()

    rt_proc = _run_cmd(['node', 'tools/check_n08_runtime.js'])
    if rt_proc.returncode != 0:
        raise RuntimeError(f"check_n08_runtime.js failed:\n{rt_proc.stderr}\n{rt_proc.stdout}")
    rt_data = json.loads(rt_proc.stdout)

    rendered_scan = _rendered_leak_scan(rt_data['renderedFamilies'])
    parity = _double_build_parity()
    regressions = _prior_regressions()

    # Summarize runtime without huge renderedFamilies strings
    rt_summary = {k: v for k, v in rt_data.items() if k != 'renderedFamilies'}

    all_ok = (
        val_report['status'] == 'PASS'
        and all(n['status'] == 'PASS' for n in neg_results)
        and rt_data['status'] == 'PASS'
        and rendered_scan['status'] == 'PASS'
        and parity['status'] == 'PASS'
        and all(r['status'] == 'PASS' for r in regressions)
    )

    return {
        'schema_version': 1,
        'task': 'N08',
        'status': 'PASS' if all_ok else 'FAIL',
        'validation': val_report,
        'negative_fixtures': neg_results,
        'rendered_leak_scan': rendered_scan,
        'runtime_fixtures': rt_summary,
        'double_build_parity': parity,
        'prior_phase_regressions': regressions,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run deterministic N08 corpus.')
    parser.add_argument('--out', type=Path, default=DEST / 'evidence/N08_CORPUS_RECORD.json')
    args = parser.parse_args(argv)

    record = run_corpus()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N08 corpus: {record['status']} -> {args.out} (sha256={sha256_file(args.out)})")
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
