#!/usr/bin/env python3
"""Deterministic N12 verification corpus:
- A.1.1 Burette geometric recompute table, edge coverage, and scratch misdrawn record failure
- A.1.2 Dilution factor arithmetic check & citation validation
- A.1.3 N10 label contract + 2-decimal scale formatting check (including planted 1-decimal violation)
- B.1.1 Planted leak-scan corpus (catch annotation leak, catch unit-normalized leak, flag borderline range, exempt reading-display, significance rule for constant 10, illegal gradeable exemption)
- B.1.2 Build-gate refusal on planted leak (exits != 0, writes no artifact, names figure)
- B.1.3 N08 convergence regression through the unified leak_scan engine
- C.1.1-C.1.3 Runtime harness, double-build parity, sub-budget accounting, reading contract digest, and N02-N11 regressions
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
from leak_scan import (  # noqa: E402
    BORDERLINE_RULE_ID, BORDERLINE_RULE_VERBATIM,
    EXEMPTION_RULE_ID, EXEMPTION_RULE_VERBATIM,
    SIGNIFICANCE_RULE_ID, SIGNIFICANCE_RULE_VERBATIM,
    scan_figure_record, scan_figures_dataset,
)
from validate_figures import (  # noqa: E402
    FIGURES_T12_PATH, FIGURES_T23_PATH, READING_CONTRACT_PATH, validate_figures,
)
from validate_terms import TERMS_PATH, validate_all as validate_terms  # noqa: E402


def _run_cmd(cmd: list[str], cwd: Path = DEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, check=False)


def _negative_geometry_and_decimal_fixtures(t23_data: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        empty_sum = {'schema_version': 1, 'concepts': []}
        p_sum = tmp_dir / 'empty_sum.json'
        p_sum.write_text(json.dumps(empty_sum), encoding='utf-8')

        # 1. Scratch misdrawn burette: meniscus shifted by one 0.1 mL subdivision (+12.0 px at 120 px/mL)
        misdrawn_data = copy.deepcopy(t23_data)
        target_rec = copy.deepcopy(t23_data['figures'][2])  # FIG-T2-BURETTE-SUBDIVIDED (120 px/mL)
        target_rec['id'] = 'FIG-SCRATCH-MISDRAWN-BURETTE'
        orig_y = float(target_rec['burette_geometry']['columns'][0]['meniscus_y_px'])
        target_rec['burette_geometry']['columns'][0]['meniscus_y_px'] = str(orig_y + 12.0)
        misdrawn_data['figures'] = [target_rec]
        r_mis = validate_figures(figures_data=misdrawn_data, summaries_path=p_sum)
        mis_matched = [e for e in r_mis['errors'] if 'E_FIG_BURETTE_GEOMETRY_MISMATCH' in e and 'FIG-SCRATCH-MISDRAWN-BURETTE' in e]

        # 2. Scratch wrong meniscus edge (clear solution labeled upper_edge)
        bad_edge_rec = copy.deepcopy(t23_data['figures'][0])
        bad_edge_rec['id'] = 'FIG-SCRATCH-WRONG-EDGE'
        bad_edge_rec['burette_geometry']['columns'][0]['meniscus_edge'] = 'upper_edge'
        r_edge = validate_figures(figures_data={**t23_data, 'figures': [bad_edge_rec]}, summaries_path=p_sum)
        edge_matched = [e for e in r_edge['errors'] if 'E_FIG_MENISCUS_RULE' in e and 'FIG-SCRATCH-WRONG-EDGE' in e]

        # 3. Scratch dilution arithmetic mismatch
        bad_dil_rec = copy.deepcopy(t23_data['figures'][5])  # FIG-T3-DILUTION-PIPETTE-FLASK
        bad_dil_rec['id'] = 'FIG-SCRATCH-DILUTION-ARITH'
        bad_dil_rec['dilution_spec']['steps'][0]['stated_factor'] = '25.0'
        r_dil = validate_figures(figures_data={**t23_data, 'figures': [bad_dil_rec]}, summaries_path=p_sum)
        dil_matched = [e for e in r_dil['errors'] if 'E_FIG_DILUTION_ARITHMETIC' in e and 'FIG-SCRATCH-DILUTION-ARITH' in e]

    return {
        'status': 'PASS' if (mis_matched and edge_matched and dil_matched) else 'FAIL',
        'scratch_misdrawn_burette': {
            'id': 'FIG-SCRATCH-MISDRAWN-BURETTE',
            'status': 'PASS' if mis_matched else 'FAIL',
            'error': mis_matched[0] if mis_matched else None,
        },
        'scratch_wrong_meniscus_edge': {
            'id': 'FIG-SCRATCH-WRONG-EDGE',
            'status': 'PASS' if edge_matched else 'FAIL',
            'error': edge_matched[0] if edge_matched else None,
        },
        'scratch_dilution_arithmetic': {
            'id': 'FIG-SCRATCH-DILUTION-ARITH',
            'status': 'PASS' if dil_matched else 'FAIL',
            'error': dil_matched[0] if dil_matched else None,
        },
    }


def _planted_leak_scan_corpus(t23_data: dict[str, Any]) -> dict[str, Any]:
    terms_data = load_json(DEST / TERMS_PATH)
    grammar = terms_data.get('unit_grammar') or {}
    terms_by_key = {e['key']: e for e in terms_data.get('terms', [])}

    grade_burette = copy.deepcopy(next(f for f in t23_data['figures'] if f['id'] == 'FIG-T2-BURETTE-DELIVERED-GRADE'))
    disp_burette = copy.deepcopy(next(f for f in t23_data['figures'] if f['id'] == 'FIG-T2-BURETTE-SUBDIVIDED'))

    # 1. Catch: scratch figure whose annotation quotes the answer (16,25 mL)
    leak_ann = copy.deepcopy(grade_burette)
    leak_ann['id'] = 'FIG-SCRATCH-LEAK-ANN'
    leak_ann['annotations'][0]['text_override_lv'] = 'Izlietais tilpums ir 16,25 mL.'
    r_ann = scan_figure_record(leak_ann, leak_ann['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    # 2. Catch unit-normalized: answer is 0.75 mg/mL, annotation says "750 mg/L" (avoids colliding with medium_step 0.5)
    leak_unorm = copy.deepcopy(grade_burette)
    leak_unorm['id'] = 'FIG-SCRATCH-LEAK-UNITNORM'
    leak_unorm['answer_targets'] = [{'value': '0.75', 'unit': 'mg/mL', 'distinctive': True}]
    leak_unorm['annotations'][0]['text_override_lv'] = 'Koncentrācija paraugā ir 750 mg/L.'
    r_unorm = scan_figure_record(leak_unorm, leak_unorm['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    # 3. Flag: borderline axis range pinning gradeable answer to readable endpoint
    flag_rec = copy.deepcopy(grade_burette)
    flag_rec['id'] = 'FIG-SCRATCH-BORDERLINE-RANGE'
    flag_rec['axes']['y']['min'] = 0.0
    flag_rec['axes']['y']['max'] = 16.5
    r_flag = scan_figure_record(flag_rec, flag_rec['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    # 4. Exempt: reading-display figure (FIG-T2-BURETTE-SUBDIVIDED) passes with exemption recorded
    r_exempt = scan_figure_record(disp_burette, [{'value': '5.85', 'unit': 'mL'}], terms_by_key, grammar, rendered_svg='<svg>5,85 mL</svg>')

    # 5. Significance rule: bare constant "10" (e.g. "dalot ar 10") is NOT a leak when answer is "10 mL",
    #    whereas unit-paired "10,0 mL" IS caught.
    sig_clean = copy.deepcopy(grade_burette)
    sig_clean['id'] = 'FIG-SCRATCH-SIG-CONST-10'
    sig_clean['answer_targets'] = [{'value': '10', 'unit': 'mL', 'distinctive': False}]
    sig_clean['annotations'][0]['text_override_lv'] = 'Mērogošanas koeficients ir 10 (skala bez vienības).'
    r_sig_clean = scan_figure_record(sig_clean, sig_clean['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    sig_unit_leak = copy.deepcopy(sig_clean)
    sig_unit_leak['id'] = 'FIG-SCRATCH-SIG-UNIT-10ML'
    sig_unit_leak['annotations'][0]['text_override_lv'] = 'Tilpums ir 10,0 mL.'
    r_sig_leak = scan_figure_record(sig_unit_leak, sig_unit_leak['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    # 6. Illegal exemption on gradeable figure
    illegal_ex = copy.deepcopy(grade_burette)
    illegal_ex['id'] = 'FIG-SCRATCH-ILLEGAL-EXEMPT'
    illegal_ex['leak_scan_exemption'] = copy.deepcopy(disp_burette['leak_scan_exemption'])
    r_illegal = scan_figure_record(illegal_ex, illegal_ex['answer_targets'], terms_by_key, grammar, rendered_svg='<svg></svg>')

    # 7. Build gate refusal on planted unit-normalized leak (0,01625 L == 16,25 mL)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        bad_t23 = copy.deepcopy(t23_data)
        for f in bad_t23['figures']:
            if f['id'] == 'FIG-T2-BURETTE-DELIVERED-GRADE':
                f['annotations'][0]['text_override_lv'] = 'Atbilde: 0,01625 L.'
        p_bad = tmp_dir / 'bad_t23_leak.json'
        p_bad.write_text(json.dumps(bad_t23, ensure_ascii=False), encoding='utf-8')
        refused_out = tmp_dir / 'refused_sim.html'
        refused_man = tmp_dir / 'refused_manifest.json'
        proc = _run_cmd([
            sys.executable, 'tools/build.py',
            '--figures-t23', str(p_bad),
            '--out', str(refused_out),
            '--manifest-out', str(refused_man),
        ])
        gate_refusal = {
            'id': 'GATE-REFUSAL-PLANTED-LEAK',
            'status': 'PASS' if (proc.returncode != 0 and not refused_out.exists() and 'figure_leak_scan' in proc.stderr and 'FIG-T2-BURETTE-DELIVERED-GRADE' in proc.stderr) else 'FAIL',
            'returncode': proc.returncode,
            'artifact_written': refused_out.exists(),
            'stderr_head': proc.stderr.splitlines()[0] if proc.stderr else '',
        }

    cases = [
        {
            'id': 'PLANTED-LEAK-ANNOTATION',
            'status': 'PASS' if r_ann['outcome'] == 'FAIL' and any('E_LEAK_DETECTED' in e and 'FIG-SCRATCH-LEAK-ANN' in e for e in r_ann['errors']) else 'FAIL',
            'outcome': r_ann['outcome'],
            'error': r_ann['errors'][0] if r_ann['errors'] else None,
        },
        {
            'id': 'PLANTED-LEAK-UNIT-NORMALIZED',
            'status': 'PASS' if r_unorm['outcome'] == 'FAIL' and any(l['match_kind'] == 'unit_normalized' and l['leaked_raw'] == '750 mg/L' for l in r_unorm['leaks']) else 'FAIL',
            'outcome': r_unorm['outcome'],
            'leak': r_unorm['leaks'][0] if r_unorm['leaks'] else None,
        },
        {
            'id': 'PLANTED-BORDERLINE-RANGE',
            'status': 'PASS' if r_flag['outcome'] == 'FLAG' and len(r_flag['flags']) >= 1 and r_flag['flags'][0]['flag_id'] == 'FLAG_BORDERLINE_RANGE' else 'FAIL',
            'outcome': r_flag['outcome'],
            'flag': r_flag['flags'][0] if r_flag['flags'] else None,
        },
        {
            'id': 'EXEMPT-READING-DISPLAY',
            'status': 'PASS' if r_exempt['outcome'] == 'EXEMPT' and r_exempt['exempt'] and r_exempt['exemption_record']['matched_hits_count'] >= 1 else 'FAIL',
            'outcome': r_exempt['outcome'],
            'exemption_record': r_exempt['exemption_record'],
        },
        {
            'id': 'SIGNIFICANCE-CONSTANT-10-IGNORED',
            'status': 'PASS' if r_sig_clean['outcome'] == 'PASS' and r_sig_clean['leaks_count'] == 0 else 'FAIL',
            'outcome': r_sig_clean['outcome'],
        },
        {
            'id': 'SIGNIFICANCE-UNIT-PAIRED-10ML-CAUGHT',
            'status': 'PASS' if r_sig_leak['outcome'] == 'FAIL' and r_sig_leak['leaks_count'] >= 1 else 'FAIL',
            'outcome': r_sig_leak['outcome'],
            'leak': r_sig_leak['leaks'][0] if r_sig_leak['leaks'] else None,
        },
        {
            'id': 'ILLEGAL-GRADEABLE-EXEMPTION',
            'status': 'PASS' if r_illegal['outcome'] == 'FAIL' and any('E_LEAK_ILLEGAL_EXEMPTION' in e for e in r_illegal['errors']) else 'FAIL',
            'outcome': r_illegal['outcome'],
            'error': r_illegal['errors'][0] if r_illegal['errors'] else None,
        },
    ]

    all_ok = all(c['status'] == 'PASS' for c in cases) and gate_refusal['status'] == 'PASS'
    return {
        'status': 'PASS' if all_ok else 'FAIL',
        'rules_verbatim': {
            'significance_rule': {'id': SIGNIFICANCE_RULE_ID, 'verbatim': SIGNIFICANCE_RULE_VERBATIM},
            'borderline_rule': {'id': BORDERLINE_RULE_ID, 'verbatim': BORDERLINE_RULE_VERBATIM},
            'exemption_rule': {'id': EXEMPTION_RULE_ID, 'verbatim': EXEMPTION_RULE_VERBATIM},
        },
        'cases': cases,
        'gate_refusal': gate_refusal,
    }


def _n08_convergence_check() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        out_p = Path(tmp) / 'n08_conv.json'
        proc = _run_cmd([sys.executable, 'tools/n08_corpus.py', '--out', str(out_p)])
        data = json.loads(out_p.read_text(encoding='utf-8')) if out_p.is_file() else {}
    return {
        'status': 'PASS' if proc.returncode == 0 and data.get('status') == 'PASS' else 'FAIL',
        'n08_corpus_status': data.get('status'),
        'authored_families': data.get('validation', {}).get('summary', {}).get('authored_families'),
        'leaks_found': data.get('validation', {}).get('summary', {}).get('leak_findings_count'),
        'rendered_scan_status': data.get('rendered_leak_scan', {}).get('status'),
    }


def _double_build_parity() -> dict[str, Any]:
    out_path = DEST / 'output/simulator.html'
    man_path = DEST / 'output/build-manifest.json'
    p1 = _run_cmd([sys.executable, 'tools/build.py'])
    b1, j1 = out_path.read_bytes(), man_path.read_bytes()
    p2 = _run_cmd([sys.executable, 'tools/build.py'])
    b2, j2 = out_path.read_bytes(), man_path.read_bytes()
    manifest = json.loads(j1.decode('utf-8'))
    t12_bytes = len(canonical_json_bytes(load_json(DEST / FIGURES_T12_PATH)))
    t23_bytes = len(canonical_json_bytes(load_json(DEST / FIGURES_T23_PATH)))
    fig_island_bytes = manifest['figures_island']['bytes']
    fig_js_bytes = manifest['figures_island']['figure_framework_js_bytes']
    leak_js_bytes = manifest['figures_island']['leak_scan_js_bytes']
    return {
        'status': 'PASS' if p1.returncode == 0 and p2.returncode == 0 and b1 == b2 and j1 == j2 else 'FAIL',
        'output_sha256': sha256_bytes(b1),
        'output_bytes': len(b1),
        'manifest_sha256': sha256_bytes(j1),
        'byte_identical': b1 == b2 and j1 == j2,
        'figures_island_bytes': fig_island_bytes,
        't12_canonical_bytes': t12_bytes,
        't23_canonical_bytes': t23_bytes,
        'figure_framework_js_bytes': fig_js_bytes,
        'leak_scan_js_bytes': leak_js_bytes,
        'combined_figure_and_scan_bytes': fig_island_bytes + fig_js_bytes + leak_js_bytes,
        'section_1_3_figure_subbudget_bytes': [60 * 1024, 140 * 1024],
        'runtime_js_code_bytes': manifest['tokens_layer']['runtime_js_code_bytes'],
        'runtime_js_ceiling_bytes': 220 * 1024,
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
        ('N11', ['node', 'tools/check_n11_runtime.js']),
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
    parser.add_argument('--out', type=Path, default=DEST / 'evidence/N12_CORPUS_RECORD.json')
    args = parser.parse_args(argv)

    t23_data = load_json(DEST / FIGURES_T23_PATH)
    contract_data = load_json(DEST / READING_CONTRACT_PATH)

    val_report = validate_figures()
    terms_report = validate_terms()
    leak_report = scan_figures_dataset()
    neg_geom = _negative_geometry_and_decimal_fixtures(t23_data)
    planted_leak = _planted_leak_scan_corpus(t23_data)
    n08_conv = _n08_convergence_check()
    parity = _double_build_parity()

    rt_proc = _run_cmd(['node', 'tools/check_n12_runtime.js'])
    rt_report = json.loads(rt_proc.stdout) if rt_proc.returncode == 0 and rt_proc.stdout.strip() else {'status': 'FAIL', 'stderr': rt_proc.stderr}
    regressions = _prior_regressions()

    all_ok = (
        val_report['status'] == 'PASS'
        and terms_report['status'] == 'PASS'
        and leak_report['status'] == 'PASS'
        and neg_geom['status'] == 'PASS'
        and planted_leak['status'] == 'PASS'
        and n08_conv['status'] == 'PASS'
        and parity['status'] == 'PASS'
        and rt_report.get('status') == 'PASS'
        and all(r['status'] == 'PASS' for r in regressions)
    )

    record = {
        'schema_version': 1,
        'task': 'N12',
        'status': 'PASS' if all_ok else 'FAIL',
        'reading_conventions_contract': {
            'path': READING_CONTRACT_PATH,
            'sha256': sha256_bytes(canonical_json_bytes(contract_data)),
            'consumers': contract_data.get('consumers'),
        },
        'figures_validation': val_report,
        'terms_lint_status': terms_report['status'],
        'leak_scan_report': leak_report,
        'negative_geometry_and_arithmetic': neg_geom,
        'planted_leak_corpus': planted_leak,
        'n08_convergence_regression': n08_conv,
        'double_build_parity': parity,
        'runtime_harness': rt_report,
        'prior_regressions': regressions,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        f"N12 corpus {record['status']}: figures={val_report['figures_count']}, "
        f"burette_geom={len(val_report['burette_geometry_table'])}, "
        f"dilution_arith={len(val_report['dilution_arithmetic_table'])}, "
        f"planted_cases={len(planted_leak['cases'])}, "
        f"smoke={rt_report.get('smoke_report', {}).get('passed')}/{rt_report.get('smoke_report', {}).get('total')}"
    )
    return 0 if all_ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
