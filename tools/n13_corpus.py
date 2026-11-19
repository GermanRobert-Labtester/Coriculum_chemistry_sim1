#!/usr/bin/env python3
"""N13 end-to-end verification corpus for Topic 4 energy-path, Hess-cycle,
and Maxwell-Boltzmann distribution figures, curve-generation extension,
and frozen energy conventions contract.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from leak_scan import scan_figure_record, scan_figures_dataset  # noqa: E402
from validate_figures import (  # noqa: E402
    ENERGY_CONTRACT_PATH,
    FIGURES_T12_PATH,
    FIGURES_T23_PATH,
    FIGURES_T4_PATH,
    FIGURE_SCHEMA_PATH,
    _generate_curve_python,
    validate_figures,
)
from validate_n06_shell import validate_shell  # noqa: E402
from validate_n07_map import validate_all as validate_n07_map  # noqa: E402
from validate_n08_layers import validate_all as validate_n08_layers  # noqa: E402
from validate_terms import validate_all as validate_terms  # noqa: E402

CORPUS_RECORD_PATH = 'evidence/N13_CORPUS_RECORD.json'


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f'N13 corpus assertion failed: {msg}')


def _run_node_curve_check(repo_root: Path, cm: dict[str, Any]) -> dict[str, Any]:
    js = (
        "const fs = require('fs'), vm = require('vm');\n"
        "const cm = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sb.globalThis = sb; vm.createContext(sb);\n"
        "vm.runInContext(fs.readFileSync('src/figure-framework.js', 'utf8'), sb);\n"
        "process.stdout.write(JSON.stringify(sb.SimFigures.generateCurvePoints(cm)));\n"
    )
    proc = subprocess.run(
        ['node', '-e', js],
        input=json.dumps(cm),
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


def run_corpus(repo_root: Path = DEST) -> dict[str, Any]:
    # 1. Main validation over merged N11+N12+N13 figures
    fig_report = validate_figures(repo_root=repo_root)
    _assert(fig_report['status'] == 'PASS', f"validate_figures failed: {fig_report['errors']}")
    _assert(fig_report['figures_count'] == 29, f"Expected 29 figures, got {fig_report['figures_count']}")
    _assert(fig_report['t4_slots_closed'] == 11, f"Expected 11/11 T4 slots closed, got {fig_report['t4_slots_closed']}")

    t4_data = load_json(repo_root / FIGURES_T4_PATH)
    t4_figs = t4_data['figures']
    t4_by_id = {r['id']: r for r in t4_figs}
    _assert(len(t4_figs) == 10, f'Expected 10 T4 figures, got {len(t4_figs)}')

    # 2. Subtask A.1.1 — Curve generation fixtures & negative parameter checks
    exo_cm = t4_by_id['FIG-T4-ENERGY-EXOTHERMIC']['series'][0]['curve_model']
    mb_cm = t4_by_id['FIG-T4-MB-TWO-TEMP-COMPARE']['series'][0]['curve_model']
    py_exo_1 = _generate_curve_python(exo_cm)
    py_exo_2 = _generate_curve_python(exo_cm)
    js_exo = _run_node_curve_check(repo_root, exo_cm)
    _assert(
        canonical_json_bytes(py_exo_1['points']) == canonical_json_bytes(py_exo_2['points'])
        == canonical_json_bytes(js_exo['points']),
        'Energy curve points Python/JS determinism mismatch',
    )

    py_mb_1 = _generate_curve_python(mb_cm)
    py_mb_2 = _generate_curve_python(mb_cm)
    js_mb = _run_node_curve_check(repo_root, mb_cm)
    _assert(
        canonical_json_bytes(py_mb_1['points']) == canonical_json_bytes(py_mb_2['points'])
        == canonical_json_bytes(js_mb['points']),
        'MB curve points Python/JS determinism mismatch',
    )

    # Scratch negative curve fixtures
    neg_unknown_cm = copy.deepcopy(t4_data)
    neg_unknown_cm['figures'][0]['series'][0]['curve_model']['function_class'] = 'spline_unknown_fn'
    rep_unk = validate_figures(repo_root=repo_root, figures_data=neg_unknown_cm, check_rendered_burettes=False)
    _assert(
        rep_unk['status'] == 'FAIL' and any('FIG-T4-ENERGY-EXOTHERMIC' in e and 'E_FIG_UNKNOWN_CURVE_CLASS' in e for e in rep_unk['errors']),
        f"Expected E_FIG_UNKNOWN_CURVE_CLASS on FIG-T4-ENERGY-EXOTHERMIC, got {rep_unk['errors']}",
    )

    neg_bad_param = copy.deepcopy(t4_data)
    neg_bad_param['figures'][0]['series'][0]['curve_model']['params']['E_ts_kj_mol'] = 50.0  # <= E_r=70.0
    rep_bad_p = validate_figures(repo_root=repo_root, figures_data=neg_bad_param, check_rendered_burettes=False)
    _assert(
        rep_bad_p['status'] == 'FAIL' and any('FIG-T4-ENERGY-EXOTHERMIC' in e and 'E_FIG_BAD_CURVE_PARAMS' in e for e in rep_bad_p['errors']),
        f"Expected E_FIG_BAD_CURVE_PARAMS on FIG-T4-ENERGY-EXOTHERMIC, got {rep_bad_p['errors']}",
    )

    # 3. Subtask A.1.2 — Energy sign-convention recompute & scratch sign-flip failure + C10/C05 honesty note
    neg_sign_flip = copy.deepcopy(t4_data)
    neg_sign_flip['figures'][0]['energy_spec']['declared_delta_h_kj_mol'] = '+70.0'
    rep_sign = validate_figures(repo_root=repo_root, figures_data=neg_sign_flip, check_rendered_burettes=False)
    _assert(
        rep_sign['status'] == 'FAIL' and any('FIG-T4-ENERGY-EXOTHERMIC' in e and 'E_FIG_ENTHALPY_SIGN_MISMATCH' in e for e in rep_sign['errors']),
        f"Expected E_FIG_ENTHALPY_SIGN_MISMATCH on scratch sign flip, got {rep_sign['errors']}",
    )

    cat_rec = t4_by_id['FIG-T4-ENERGY-CATALYZED']
    c10_note = cat_rec.get('c10_honesty_note_lv', '')
    _assert('V-08' in c10_note and 'C05' in c10_note and 'C10' in c10_note and '23' in c10_note, 'Missing C05/V-08/C10 catalase honesty note')

    # 4. Subtask B.1.1 — Hess cycle sum check, reverse-traversal trap, & scratch unbalanced cycle failure
    neg_hess = copy.deepcopy(t4_data)
    fecl3_idx = next(i for i, r in enumerate(neg_hess['figures']) if r['id'] == 'FIG-T4-HESS-FECL3')
    neg_hess['figures'][fecl3_idx]['hess_spec']['direct_path']['dh_kj_mol'] = '-350.0'
    rep_hess = validate_figures(repo_root=repo_root, figures_data=neg_hess, check_rendered_burettes=False)
    _assert(
        rep_hess['status'] == 'FAIL' and any('FIG-T4-HESS-FECL3' in e and 'E_FIG_HESS_UNBALANCED' in e for e in rep_hess['errors']),
        f"Expected E_FIG_HESS_UNBALANCED on scratch unbalanced cycle, got {rep_hess['errors']}",
    )

    # 5. Subtask B.1.2 — Maxwell-Boltzmann honesty & scratch exaggerated tail-claim failure
    neg_mb = copy.deepcopy(t4_data)
    mb_idx = next(i for i, r in enumerate(neg_mb['figures']) if r['id'] == 'FIG-T4-MB-TWO-TEMP-COMPARE')
    neg_mb['figures'][mb_idx]['mb_model_spec']['tail_ratio'] = '12.5'
    rep_mb = validate_figures(repo_root=repo_root, figures_data=neg_mb, check_rendered_burettes=False)
    _assert(
        rep_mb['status'] == 'FAIL' and any('FIG-T4-MB-TWO-TEMP-COMPARE' in e and 'E_FIG_MB_HONESTY' in e for e in rep_mb['errors']),
        f"Expected E_FIG_MB_HONESTY on exaggerated tail ratio, got {rep_mb['errors']}",
    )

    # 6. Subtask B.1.3 — V-06 scope-note copy lint & broken citation negative checks
    neg_scope = copy.deepcopy(t4_data)
    neg_scope['figures'][mb_idx]['scope_note_lv'] = 'Tvēruma piezīme (V-06): šis ir universāls slieksnis visām reakcijām.'
    rep_scope = validate_figures(repo_root=repo_root, figures_data=neg_scope, check_rendered_burettes=False)
    _assert(
        rep_scope['status'] == 'FAIL' and any('FIG-T4-MB-TWO-TEMP-COMPARE' in e and 'E_FIG_SCOPE_OVERGENERALIZATION' in e for e in rep_scope['errors']),
        f"Expected E_FIG_SCOPE_OVERGENERALIZATION, got {rep_scope['errors']}",
    )

    neg_anchor = copy.deepcopy(t4_data)
    neg_anchor['figures'][0]['citations']['master_anchor'] = 'fig-nonexistent-t4'
    rep_anchor = validate_figures(repo_root=repo_root, figures_data=neg_anchor, check_rendered_burettes=False)
    _assert(
        rep_anchor['status'] == 'FAIL' and any('FIG-T4-ENERGY-EXOTHERMIC' in e and 'E_FIG_BROKEN_ANCHOR' in e for e in rep_anchor['errors']),
        f"Expected E_FIG_BROKEN_ANCHOR, got {rep_anchor['errors']}",
    )

    # 7. Subtask C.1.1 — Leak scan over all 29 figures + planted Hess practice leak
    leak_report = scan_figures_dataset(repo_root=repo_root)
    _assert(leak_report['status'] == 'PASS' and leak_report['flags_count'] == 0, f'Leak scan failed: {leak_report}')
    terms_data = load_json(repo_root / 'data/terms.json')
    terms_by_key = {e['key']: e for e in terms_data['terms']}
    grammar = terms_data['unit_grammar']

    hess_prac = copy.deepcopy(t4_by_id['FIG-T4-HESS-PRACTICE-SYNTH'])
    hess_prac_clean = scan_figure_record(hess_prac, hess_prac['answer_targets'], terms_by_key=terms_by_key, grammar=grammar)
    _assert(hess_prac_clean['outcome'] == 'PASS', f'Expected clean PASS on FIG-T4-HESS-PRACTICE-SYNTH, got {hess_prac_clean}')

    hess_prac_leaked = copy.deepcopy(hess_prac)
    hess_prac_leaked['hess_spec']['direct_path']['label_lv'] = 'Tiešais ceļš: −219,0 kJ/mol'
    hess_prac_leak_res = scan_figure_record(hess_prac_leaked, hess_prac_leaked['answer_targets'], terms_by_key=terms_by_key, grammar=grammar)
    _assert(
        hess_prac_leak_res['outcome'] == 'FAIL' and len(hess_prac_leak_res['leaks']) >= 1,
        f'Expected FAIL on planted Hess practice leak, got {hess_prac_leak_res}',
    )

    # 8. Build-gate refusal on invalid T4 file (artifact not written)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        bad_t4_file = tmp_path / 'bad_figures_t4.json'
        out_html = tmp_path / 'refused_simulator.html'
        bad_t4_file.write_text(json.dumps(neg_hess, ensure_ascii=False), encoding='utf-8')
        proc_refuse = subprocess.run(
            [sys.executable, 'tools/build.py', '--figures-t4', str(bad_t4_file), '--out', str(out_html)],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            check=False,
        )
        _assert(proc_refuse.returncode != 0 and not out_html.exists(), 'build.py must refuse invalid T4 figures and not write artifact')

    # 9. Two-run deterministic build parity (fresh build vs canonical output/simulator.html)
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        b_html, b_man = tmp_path / 'simulator.html', tmp_path / 'build-manifest.json'
        subprocess.run([sys.executable, 'tools/build.py', '--out', str(b_html), '--manifest-out', str(b_man)], cwd=str(repo_root), check=True, capture_output=True)
        _assert(sha256_file(b_html) == sha256_file(repo_root / 'output/simulator.html'), 'Two-build HTML SHA-256 mismatch')
        m1, m2 = load_json(b_man), load_json(repo_root / 'output/build-manifest.json')
        m1['output'] = m2['output']
        _assert(canonical_json_bytes(m1) == canonical_json_bytes(m2), 'Two-build manifest canonical mismatch')

    # 10. Runtime check_n13_runtime.js + prior regression checks
    proc_rt = subprocess.run(['node', 'tools/check_n13_runtime.js', '--json'], cwd=str(repo_root), capture_output=True, text=True, check=True)
    rt_report = json.loads(proc_rt.stdout)
    _assert(rt_report['status'] == 'PASS' and rt_report['smoke']['passed'] == 7, 'check_n13_runtime failed')

    for script in ('tools/check_n10_runtime.js', 'tools/check_n11_runtime.js', 'tools/check_n12_runtime.js'):
        subprocess.run(['node', script], cwd=str(repo_root), check=True, capture_output=True)

    shell_rep = validate_shell(repo_root / 'output/simulator.html', repo_root=repo_root)
    terms_rep = validate_terms(repo_root=repo_root)
    n07_rep = validate_n07_map(repo_root=repo_root)
    n08_rep = validate_n08_layers(repo_root=repo_root)
    _assert(shell_rep['status'] == 'PASS' and terms_rep['status'] == 'PASS' and n07_rep['status'] == 'PASS' and n08_rep['status'] == 'PASS', 'Prior validator failed')

    # 11. Sub-budget accounting
    t12_bytes = len(canonical_json_bytes(load_json(repo_root / FIGURES_T12_PATH)))
    t23_bytes = len(canonical_json_bytes(load_json(repo_root / FIGURES_T23_PATH)))
    t4_bytes = len(canonical_json_bytes(t4_data))
    merged_fig_bytes = fig_report['canonical_bytes']
    fig_fw_bytes = (repo_root / 'src/figure-framework.js').stat().st_size
    leak_js_bytes = (repo_root / 'src/leak-scan.js').stat().st_size
    figure_ceiling = 140 * 1024  # 143,360 B

    manifest = load_json(repo_root / 'output/build-manifest.json')
    energy_contract = load_json(repo_root / ENERGY_CONTRACT_PATH)
    energy_contract_bytes = canonical_json_bytes(energy_contract)

    return {
        'schema_version': 1,
        'task': 'N13',
        'status': 'PASS',
        'build': {
            'build_id': manifest['build_id'],
            'output_bytes': manifest['output_bytes'],
            'output_sha256': manifest['output_sha256'],
            'manifest_sha256': sha256_file(repo_root / 'output/build-manifest.json'),
            'two_build_parity': True,
        },
        'digests': {
            'figure_schema_sha256': sha256_bytes(canonical_json_bytes(load_json(repo_root / FIGURE_SCHEMA_PATH))),
            'figures_t4_file_sha256': sha256_file(repo_root / FIGURES_T4_PATH),
            'figures_t4_canonical_sha256': sha256_bytes(canonical_json_bytes(t4_data)),
            'figures_island_merged_sha256': fig_report['canonical_sha256'],
            'energy_conventions_contract_file_sha256': sha256_file(repo_root / ENERGY_CONTRACT_PATH),
            'energy_conventions_contract_canonical_sha256': sha256_bytes(energy_contract_bytes),
            'figure_framework_js_sha256': sha256_file(repo_root / 'src/figure-framework.js'),
            'terms_canonical_sha256': manifest['terms_island']['digest'],
            'concept_summaries_sha256': sha256_file(repo_root / 'data/concept_summaries.json'),
        },
        'curve_generation': {
            'registered_classes': ['energy_profile_single_barrier', 'maxwell_boltzmann_3d'],
            'python_js_point_parity': True,
            'table': fig_report['curve_generation_table'],
            'negative_tests': {
                'unknown_class_rejected': 'E_FIG_UNKNOWN_CURVE_CLASS',
                'bad_params_rejected': 'E_FIG_BAD_CURVE_PARAMS',
            },
        },
        'energy_sign_fidelity': {
            'table': fig_report['energy_sign_table'],
            'scratch_sign_flip_rejected_id': 'FIG-T4-ENERGY-EXOTHERMIC',
            'c10_honesty_note_lv': c10_note,
        },
        'hess_cycle_verification': {
            'table': fig_report['hess_cycle_table'],
            'scratch_unbalanced_rejected_id': 'FIG-T4-HESS-FECL3',
        },
        'mb_honesty_verification': {
            'table': fig_report['mb_honesty_table'],
            'scratch_exaggerated_claim_rejected_id': 'FIG-T4-MB-TWO-TEMP-COMPARE',
        },
        'v06_scope_and_n10_labels': {
            'label_checks': fig_report['label_checks'],
            'unit_checks': fig_report['unit_checks'],
            'v06_scope_table': fig_report['v06_scope_table'],
            'scratch_overgeneralization_rejected_id': 'FIG-T4-MB-TWO-TEMP-COMPARE',
            'scratch_broken_anchor_rejected_id': 'FIG-T4-ENERGY-EXOTHERMIC',
        },
        'leak_scan': {
            'total_scanned': leak_report['figures_scanned'],
            'gradeable_count': leak_report['gradeable_figures'],
            'exempt_count': leak_report['exempt_figures'],
            'flags_count': leak_report['flags_count'],
            'hess_practice_synth_outcome': hess_prac_clean['outcome'],
            'hess_practice_planted_leak_caught': True,
        },
        'runtime_verification': rt_report,
        'sub_budget_accounting': {
            't12_canonical_bytes': t12_bytes,
            't23_canonical_bytes': t23_bytes,
            't4_canonical_bytes': t4_bytes,
            'merged_figures_island_bytes': merged_fig_bytes,
            'figure_ceiling_bytes': figure_ceiling,
            'figures_island_share_pct': round(merged_fig_bytes * 100.0 / figure_ceiling, 2),
            't4_data_share_of_ceiling_pct': round(t4_bytes * 100.0 / figure_ceiling, 2),
            'figure_framework_js_bytes': fig_fw_bytes,
            'leak_scan_js_bytes': leak_js_bytes,
            'runtime_js_code_bytes': shell_rep['byte_accounting']['runtime_js_code_bytes'],
            'runtime_js_ceiling_bytes': 220 * 1024,
        },
    }


def main() -> int:
    rec = run_corpus(DEST)
    out_path = DEST / CORPUS_RECORD_PATH
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        f"n13_corpus PASS: figures={rec['runtime_verification']['total_figures']} (T4=10), "
        f"curves={len(rec['curve_generation']['table'])}, hess={len(rec['hess_cycle_verification']['table'])}, "
        f"mb={len(rec['mb_honesty_verification']['table'])}, t4_bytes={rec['sub_budget_accounting']['t4_canonical_bytes']}B, "
        f"merged_fig={rec['sub_budget_accounting']['merged_figures_island_bytes']}B/{rec['sub_budget_accounting']['figure_ceiling_bytes']}B, "
        f"js_code={rec['sub_budget_accounting']['runtime_js_code_bytes']}B/225280B"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
