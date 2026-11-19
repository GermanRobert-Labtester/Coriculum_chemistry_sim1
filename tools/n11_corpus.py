#!/usr/bin/env python3
"""Deterministic N11 verification corpus:
- Format spec & valid scratch record fixture + malformed-record corpus (one failure per class, each named)
- Build-gate refusal on malformed figure dataset (exits != 0, writes no artifact)
- T1-2 citation validation, tolerance-coupling + optionality rule, and independent Decimal recompute table
- N11 runtime harness (lazy-render, determinism, theme parity, truncation + slot degradation, 5/5 smoke)
- Double-build parity, Section 1.3 figure sub-budget accounting, and prior-phase regressions (N02..N10)
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
from validate_figures import FIGURES_T12_PATH, FIGURE_SCHEMA_PATH, validate_figures  # noqa: E402


def _run_cmd(cmd: list[str], cwd: Path = DEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _format_and_malformed_corpus(t12_data: dict[str, Any]) -> dict[str, Any]:
    base_rec = copy.deepcopy(t12_data['figures'][0])
    # Valid scratch record passing
    scratch_valid = copy.deepcopy(base_rec)
    scratch_valid['id'] = 'FIG-SCRATCH-VALID'
    scratch_valid['concept_ids'] = ['P1-02']
    scratch_valid_data = {
        'schema_version': 1,
        'format_version': 1,
        'island_id': 'sim-figures',
        'status': 'authored',
        'owner': 'N11',
        'figures': [scratch_valid],
    }
    # Check against validate_figures (note: full summaries cross-check requires all 18 N11 slots, so use empty summaries copy for isolated format check)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        empty_sum = {'schema_version': 1, 'concepts': []}
        p_sum = tmp_dir / 'empty_sum.json'
        p_sum.write_text(json.dumps(empty_sum), encoding='utf-8')

        r_valid = validate_figures(figures_data=scratch_valid_data, summaries_path=p_sum)

        def run_neg(case_id: str, mutator, expected_code: str) -> dict[str, Any]:
            bad_data = copy.deepcopy(scratch_valid_data)
            mutator(bad_data['figures'][0])
            rep = validate_figures(figures_data=bad_data, summaries_path=p_sum)
            matched = [e for e in rep['errors'] if expected_code in e]
            return {
                'id': case_id,
                'expected_code': expected_code,
                'status': 'PASS' if rep['status'] == 'FAIL' and len(matched) > 0 else 'FAIL',
                'error': matched[0] if matched else (rep['errors'][0] if rep['errors'] else None),
            }

        def mut_unknown_type(r: dict[str, Any]) -> None:
            r['type'] = 'pie_3d_unknown'

        def mut_unknown_term(r: dict[str, Any]) -> None:
            r['title_key'] = 'fig.title.does_not_exist'

        def mut_bad_unit(r: dict[str, Any]) -> None:
            r['axes']['y']['unit'] = 'J/mol·K'

        def mut_bad_tolerance(r: dict[str, Any]) -> None:
            r['tolerance_coupling']['tolerance_class'] = 'nonexistent_tol_class'

        def mut_missing_desc(r: dict[str, Any]) -> None:
            r['id'] = 'FIG-SCRATCH-NODESC'
            r['description_lv'] = ''

        def mut_unlabeled_pct(r: dict[str, Any]) -> None:
            r['axes']['y']['unit'] = '%'
            r['percentage_basis'] = None

        def mut_broken_anchor(r: dict[str, Any]) -> None:
            r['citations']['master_anchor'] = 'neeksistejoss-enkurs'

        def mut_recompute_mismatch(r: dict[str, Any]) -> None:
            r['derived_values'][0]['value'] = '99.9'

        def mut_missing_measured_tol(r: dict[str, Any]) -> None:
            r['tolerance_coupling'] = None

        negatives = [
            run_neg('NEG-UNKNOWN-TYPE', mut_unknown_type, 'E_FIG_UNKNOWN_TYPE'),
            run_neg('NEG-UNRESOLVED-TERM-KEY', mut_unknown_term, 'E_TERMS_UNKNOWN_KEY'),
            run_neg('NEG-UNIT-GRAMMAR-FAIL', mut_bad_unit, 'E_UNIT_AMBIGUOUS_DENOMINATOR'),
            run_neg('NEG-UNRESOLVED-TOLERANCE', mut_bad_tolerance, 'E_FIG_UNKNOWN_TOLERANCE_CLASS'),
            run_neg('NEG-MISSING-DESCRIPTION', mut_missing_desc, 'E_FIG_MISSING_DESCRIPTION'),
            run_neg('NEG-UNLABELED-PERCENT', mut_unlabeled_pct, 'E_FIG_UNLABELED_PERCENT'),
            run_neg('NEG-BROKEN-ANCHOR', mut_broken_anchor, 'E_FIG_BROKEN_ANCHOR'),
            run_neg('NEG-RECOMPUTE-MISMATCH', mut_recompute_mismatch, 'E_FIG_RECOMPUTE_MISMATCH'),
            run_neg('NEG-MISSING-MEASURED-TOLERANCE', mut_missing_measured_tol, 'E_FIG_MISSING_TOLERANCE'),
        ]

        # Build-gate refusal on planted malformed T1-2 file
        bad_t12 = copy.deepcopy(t12_data)
        bad_t12['figures'][0]['type'] = 'unknown_chart'
        p_bad_t12 = tmp_dir / 'bad_figures_t12.json'
        p_bad_t12.write_text(json.dumps(bad_t12, ensure_ascii=False), encoding='utf-8')
        refused_out = tmp_dir / 'refused_sim.html'
        refused_man = tmp_dir / 'refused_manifest.json'
        gate_proc = _run_cmd([
            sys.executable, 'tools/build.py',
            '--figures', str(p_bad_t12),
            '--out', str(refused_out),
            '--manifest-out', str(refused_man),
        ])
        gate_refusal = {
            'id': 'GATE-REFUSAL-UNKNOWN-TYPE',
            'status': 'PASS' if gate_proc.returncode != 0 and not refused_out.exists() and 'figures' in gate_proc.stderr and 'E_FIG_UNKNOWN_TYPE' in gate_proc.stderr else 'FAIL',
            'returncode': gate_proc.returncode,
            'artifact_written': refused_out.exists(),
            'stderr_head': gate_proc.stderr.splitlines()[0] if gate_proc.stderr else '',
        }

    return {
        'status': 'PASS' if r_valid['status'] == 'PASS' and all(n['status'] == 'PASS' for n in negatives) and gate_refusal['status'] == 'PASS' else 'FAIL',
        'valid_scratch_status': r_valid['status'],
        'malformed_corpus': negatives,
        'gate_refusal': gate_refusal,
    }


def _double_build_parity() -> dict[str, Any]:
    out_path = DEST / 'output/simulator.html'
    man_path = DEST / 'output/build-manifest.json'
    p1 = _run_cmd([sys.executable, 'tools/build.py'])
    b1, j1 = out_path.read_bytes(), man_path.read_bytes()
    p2 = _run_cmd([sys.executable, 'tools/build.py'])
    b2, j2 = out_path.read_bytes(), man_path.read_bytes()
    manifest = json.loads(j1.decode('utf-8'))
    fig_island_bytes = manifest['figures_island']['bytes']
    fig_js_bytes = manifest['figures_island']['figure_framework_js_bytes']
    return {
        'status': 'PASS' if p1.returncode == 0 and p2.returncode == 0 and b1 == b2 and j1 == j2 else 'FAIL',
        'output_sha256': sha256_bytes(b1),
        'output_bytes': len(b1),
        'manifest_sha256': sha256_bytes(j1),
        'byte_identical': b1 == b2 and j1 == j2,
        'figures_island_bytes': fig_island_bytes,
        'figure_framework_js_bytes': fig_js_bytes,
        't12_combined_figure_bytes': fig_island_bytes + fig_js_bytes,
        'section_1_3_figure_subbudget_bytes': [60 * 1024, 140 * 1024],
        'runtime_js_code_bytes': manifest['tokens_layer']['runtime_js_code_bytes'],
        'css_bytes': manifest['tokens_layer']['css_bytes'],
    }


def _prior_regressions() -> list[dict[str, Any]]:
    checks = [
        ('N02', ['node', 'tools/check_coverage_runtime.js', '--json']),
        ('N03', ['node', 'tools/check_conventions_runtime.js']),
        ('N05', ['node', 'tools/check_golden_vectors_runtime.js']),
        ('N06', ['node', 'tools/check_n06_runtime.js', '--json']),
        ('N07', ['node', 'tools/check_n07_runtime.js', '--json']),
        ('N08', ['node', 'tools/check_n08_runtime.js']),
        ('N10', ['node', 'tools/check_n10_runtime.js']),
    ]
    out: list[dict[str, Any]] = []
    for owner, cmd in checks:
        proc = _run_cmd(cmd)
        out.append({
            'owner': owner,
            'command': ' '.join(cmd),
            'status': 'PASS' if proc.returncode == 0 else 'FAIL',
        })
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=DEST / 'evidence/N11_CORPUS_RECORD.json')
    args = parser.parse_args(argv)

    t12_data = load_json(DEST / FIGURES_T12_PATH)
    schema_data = load_json(DEST / FIGURE_SCHEMA_PATH)
    val_report = validate_figures()
    format_corpus = _format_and_malformed_corpus(t12_data)
    parity = _double_build_parity()

    rt_proc = _run_cmd(['node', 'tools/check_n11_runtime.js'])
    rt_report = json.loads(rt_proc.stdout) if rt_proc.returncode == 0 and rt_proc.stdout.strip() else {'status': 'FAIL', 'stderr': rt_proc.stderr}
    regressions = _prior_regressions()

    all_ok = (
        val_report['status'] == 'PASS'
        and format_corpus['status'] == 'PASS'
        and parity['status'] == 'PASS'
        and rt_report.get('status') == 'PASS'
        and all(r['status'] == 'PASS' for r in regressions)
    )

    record = {
        'schema_version': 1,
        'task': 'N11',
        'status': 'PASS' if all_ok else 'FAIL',
        'figure_schema_digest': sha256_bytes(canonical_json_bytes(schema_data)),
        'figures_t12_validation': val_report,
        'format_and_malformed_corpus': format_corpus,
        'double_build_parity': parity,
        'runtime_harness': rt_report,
        'prior_regressions': regressions,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N11 corpus {record['status']}: records={val_report['figures_count']}, recomputed={len(val_report['recompute_table'])}, malformed={len(format_corpus['malformed_corpus'])}, smoke={rt_report.get('smoke_report', {}).get('passed')}/{rt_report.get('smoke_report', {}).get('total')}")
    return 0 if all_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
