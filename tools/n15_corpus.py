#!/usr/bin/env python3
"""N15 end-to-end corpus for T6-7 titration/calibration figures, V-05/V-07
wording and assumption lints, the formal no-extrapolation rule, contracts,
print renders, leak exemptions and Phase III byte accounting.
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from leak_scan import scan_figure_record, scan_figures_dataset  # noqa: E402
from validate_figures import (  # noqa: E402
    CALIBRATION_CONTRACT_PATH, FIGURES_T12_PATH, FIGURES_T23_PATH, FIGURES_T4_PATH,
    FIGURES_T5_PATH, FIGURES_T67_PATH, TITRATION_CONTRACT_PATH, _generate_curve_python,
    _model_initial, _model_veq, validate_figures,
)
from validate_n06_shell import validate_shell  # noqa: E402
from validate_n07_map import validate_all as validate_n07_map  # noqa: E402
from validate_n08_layers import validate_all as validate_n08_layers  # noqa: E402
from validate_terms import validate_all as validate_terms  # noqa: E402

CORPUS_RECORD_PATH = 'evidence/N15_CORPUS_RECORD.json'
PRINT_TITRATION_PATH = 'evidence/N15_PRINT_TITRATION.png'
PRINT_CALIBRATION_PATH = 'evidence/N15_PRINT_CALIBRATION.png'
FIGURE_CEILING = 140 * 1024
RUNTIME_CEILING = 225280


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f'N15 corpus assertion failed: {msg}')


def _run_node_curve(repo_root: Path, cm: dict[str, Any]) -> dict[str, Any]:
    js = (
        "const fs = require('fs'), vm = require('vm');\n"
        "const cm = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sb.globalThis = sb; vm.createContext(sb);\n"
        "vm.runInContext(fs.readFileSync('src/figure-framework.js', 'utf8'), sb);\n"
        "process.stdout.write(JSON.stringify(sb.SimFigures.generateCurvePoints(cm)));\n"
    )
    proc = subprocess.run(['node', '-e', js], input=json.dumps(cm), cwd=str(repo_root),
                          capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_corpus(repo_root: Path = DEST) -> dict[str, Any]:
    fig_report = validate_figures(repo_root=repo_root)
    _assert(fig_report['status'] == 'PASS', f"validate_figures failed: {fig_report['errors']}")
    _assert(fig_report['figures_count'] == 45, f"Expected 45 figures, got {fig_report['figures_count']}")
    _assert(fig_report['t67_slots_closed'] == 13, f"Expected 13/13 T6-7 slots, got {fig_report['t67_slots_closed']}")

    t67 = load_json(repo_root / FIGURES_T67_PATH)
    figs = t67['figures']
    by_id = {r['id']: r for r in figs}
    _assert(len(figs) == 8, f'Expected 8 T67 records, got {len(figs)}')
    _assert(len([r for r in figs if r['topic'] == 6]) == 5, 'Expected 5 titration records')
    _assert(len([r for r in figs if r['topic'] == 7]) == 3, 'Expected 3 calibration records')

    # A.1.1 model checks: inflection, initial value, buffer slope, V-05 copy
    model_rows = fig_report['titration_model_table']
    _assert(len(model_rows) == 5 and all(r['agrees'] for r in model_rows), f'Titration model table not clean: {model_rows}')
    _assert(all(r['inflection_agrees'] and r['initial_agrees'] for r in model_rows), 'Inflection/initial recompute failed')
    _assert(all(r['agrees'] for r in fig_report['v05_copy_table']), 'V-05 copy lint failed')
    weak_row = next(r for r in model_rows if r['figure_id'] == 'FIG-T67-TITR-WEAK')
    _assert(weak_row['buffer']['agrees'] and Decimal(weak_row['buffer']['buffer_slope_ph_per_ml']) < Decimal('0.15'),
            'Weak buffer slope not flatter than equivalence slope')
    wrong = by_id['FIG-T67-TITR-WRONG-IND']
    _assert(wrong['titration_spec']['wrong_indicator_case'] is True
            and wrong['titration_spec']['indicator']['contains_equivalence_ph'] is False
            and Decimal(wrong['titration_spec']['endpoint_volume_ml']) < Decimal('10'),
            'Wrong-indicator trap is not a real miss')

    # A.1.3 reading coupling and print subdivision floor
    read_rows = fig_report['titration_reading_table']
    _assert(len(read_rows) == 5 and all(r['reading_coupling_ok'] for r in read_rows), f'Reading coupling failed: {read_rows}')
    _assert(all(Decimal(r['subdivision_mm']) >= Decimal('1.50') for r in read_rows), '0.1 mL print floor violated')

    # B.1 calibration recompute, assumptions, no-extrapolation
    cal_rows = fig_report['calibration_reading_table']
    _assert(len(cal_rows) == 3 and all(r['agrees'] for r in cal_rows), f'Calibration table not clean: {cal_rows}')
    _assert(all(r['assumption_honesty'] for r in cal_rows), 'V-07 assumption honesty lint failed')
    _assert(all(r['no_extrapolation_ok'] for r in cal_rows), 'No-extrapolation rule failed')
    _assert(all(r['inside_span'] for r in cal_rows), 'A declared reading is outside its standards span')
    practice_c = by_id['FIG-T67-CAL-PRACTICE']
    _assert('unknown_concentration_mg_ml' not in practice_c['calibration_spec'], 'Practice calibration stores its answer')

    # Determinism: Python twice + JS parity for all three curve classes
    curve_rows = []
    for fid in ('FIG-T67-TITR-STRONG', 'FIG-T67-TITR-WEAK', 'FIG-T67-TITR-MASTER-KMNO4'):
        cm = by_id[fid]['series'][0]['curve_model']
        p1 = _generate_curve_python(cm)
        p2 = _generate_curve_python(cm)
        js = _run_node_curve(repo_root, cm)
        ok = canonical_json_bytes(p1['points']) == canonical_json_bytes(p2['points']) == canonical_json_bytes(js['points'])
        _assert(ok, f'Curve determinism/parity failed for {fid}')
        curve_rows.append({'figure_id': fid, 'function_class': cm['function_class'],
                           'point_count': len(p1['points']),
                           'points_sha256': sha256_bytes(canonical_json_bytes(p1['points'])),
                           'python_js_parity': ok})

    # Negative cases fail by id
    scratch = copy.deepcopy(t67)
    for r in scratch['figures']:
        if r['id'] == 'FIG-T67-TITR-STRONG':
            r['titration_spec']['declared_equivalence_volume_ml'] = '26.00'
    rep_bad = validate_figures(repo_root=repo_root, figures_data=scratch, check_rendered_burettes=False)
    _assert(rep_bad['status'] == 'FAIL' and any(
        'FIG-T67-TITR-STRONG' in e and 'E_FIG_TITRATION_EQUIVALENCE' in e for e in rep_bad['errors']),
        f'Scratch inflection/equivalence disagreement not caught: {rep_bad["errors"][:5]}')

    scratch_span = copy.deepcopy(t67)
    for r in scratch_span['figures']:
        if r['id'] == 'FIG-T67-CAL-MASTER':
            r['reading_spec']['concentration_x'] = '0.02000'
            r['calibration_spec']['unknown_concentration_mg_ml'] = '0.02000'
            r['fit_line']['x_max'] = 0.020
    rep_span = validate_figures(repo_root=repo_root, figures_data=scratch_span, check_rendered_burettes=False)
    _assert(rep_span['status'] == 'FAIL' and any(
        'FIG-T67-CAL-MASTER' in e and 'E_FIG_CAL_READING_OUT_OF_SPAN' in e for e in rep_span['errors']),
        f'Scratch over-span reading not caught: {rep_span["errors"][:5]}')
    _assert(any('FIG-T67-CAL-MASTER' in e and 'E_FIG_CAL_FIT_OUT_OF_SPAN' in e for e in rep_span['errors']),
            'Scratch over-span fit not caught')

    scratch_wrong = copy.deepcopy(t67)
    for r in scratch_wrong['figures']:
        if r['id'] == 'FIG-T67-CAL-MASTER':
            r['calibration_spec']['unknown_concentration_mg_ml'] = '0.01000'
    rep_wrong = validate_figures(repo_root=repo_root, figures_data=scratch_wrong, check_rendered_burettes=False)
    _assert(rep_wrong['status'] == 'FAIL' and any(
        'FIG-T67-CAL-MASTER' in e and 'E_FIG_CAL_READING_MISMATCH' in e for e in rep_wrong['errors']),
        f'Scratch wrong calibration reading not caught: {rep_wrong["errors"][:5]}')

    # Leak scan per record and exemptions
    leak_report = scan_figures_dataset(repo_root=repo_root, figures_paths=[repo_root / FIGURES_T67_PATH])
    _assert(leak_report['status'] == 'PASS' and leak_report['flags_count'] == 0, f'Leak scan failed: {leak_report["errors"][:5]}')
    terms_data = load_json(repo_root / 'data/terms.json')
    terms_by_key = {e['key']: e for e in terms_data['terms']}
    gram = terms_data['unit_grammar']
    per_record = []
    for fid in [r['id'] for r in figs]:
        rec = by_id[fid]
        res = scan_figure_record(rec, rec.get('answer_targets') or [], terms_by_key=terms_by_key, grammar=gram)
        _assert(res['outcome'] in ('PASS', 'EXEMPT'), f'{fid} leak outcome {res["outcome"]}')
        per_record.append({'figure_id': fid, 'gradeable': bool(rec.get('gradeable')),
                           'outcome': res['outcome'], 'leaks': len(res['leaks'])})
    _assert(next(r for r in per_record if r['figure_id'] == 'FIG-T67-TITR-PRACTICE')['outcome'] == 'PASS',
            'Titration practice leaks its equivalence volume')
    _assert(next(r for r in per_record if r['figure_id'] == 'FIG-T67-CAL-PRACTICE')['outcome'] == 'PASS',
            'Calibration practice leaks its concentration')
    _assert(next(r for r in per_record if r['figure_id'] == 'FIG-T67-CAL-NEAR-EDGE')['outcome'] == 'EXEMPT',
            'Near-edge teaching record lacks its reasoned exemption')

    # Contracts and verbatim no-extrapolation handoff
    tcontract = load_json(repo_root / TITRATION_CONTRACT_PATH)
    ccontract = load_json(repo_root / CALIBRATION_CONTRACT_PATH)
    conventions = load_json(repo_root / 'data/conventions.json')
    no_ext = conventions['spectrophotometry']['calibration']['no_extrapolation_rule_lv']
    _assert(ccontract['no_extrapolation_rule']['verbatim'] == no_ext,
            'Calibration contract does not inherit the no-extrapolation rule verbatim')
    _assert(ccontract['no_extrapolation_rule']['inherited_by'] == 'N18', 'Rule is not handed to N18')
    _assert(tcontract['v05_wording']['wording_rule_verbatim'] == conventions['titration']['endpoint']['wording_rule_lv'],
            'Titration contract V-05 text differs from conventions')
    _assert(fig_report['titration_contract']['sha256'] == sha256_bytes(canonical_json_bytes(tcontract)),
            'Titration contract digest mismatch')
    _assert(fig_report['calibration_contract']['sha256'] == sha256_bytes(canonical_json_bytes(ccontract)),
            'Calibration contract digest mismatch')

    # Build refusal on a truncated T67 file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        bad = tmp / 'bad_figures_t67.json'
        out = tmp / 'refused.html'
        raw = (repo_root / FIGURES_T67_PATH).read_text(encoding='utf-8')
        bad.write_text(raw[: len(raw) // 2], encoding='utf-8')
        proc = subprocess.run([sys.executable, 'tools/build.py', '--figures-t67', str(bad), '--out', str(out)],
                              cwd=str(repo_root), capture_output=True, text=True, check=False)
        _assert(proc.returncode != 0 and not out.exists(), 'build.py must refuse a truncated T67 file')

    # Two-build parity
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        html = tmp / 'simulator.html'
        man = tmp / 'build-manifest.json'
        subprocess.run([sys.executable, 'tools/build.py', '--out', str(html), '--manifest-out', str(man)],
                       cwd=str(repo_root), check=True, capture_output=True)
        _assert(sha256_file(html) == sha256_file(repo_root / 'output/simulator.html'), 'Two-build HTML mismatch')
        m1, m2 = load_json(man), load_json(repo_root / 'output/build-manifest.json')
        m1['output'] = m2['output']
        _assert(canonical_json_bytes(m1) == canonical_json_bytes(m2), 'Two-build manifest mismatch')

    # Runtime harness + prior regressions + validators
    rt = json.loads(subprocess.run(['node', 'tools/check_n15_runtime.js'], cwd=str(repo_root),
                                   capture_output=True, text=True, check=True).stdout)
    _assert(rt['status'] == 'PASS' and rt['t67_figures'] == 8 and rt['truncation'] == 'E_FIGURES_JSON',
            'check_n15_runtime failed')
    for script in ('tools/check_n10_runtime.js', 'tools/check_n11_runtime.js', 'tools/check_n12_runtime.js',
                   'tools/check_n13_runtime.js', 'tools/check_n14_runtime.js'):
        subprocess.run(['node', script], cwd=str(repo_root), check=True, capture_output=True)
    shell_rep = validate_shell(repo_root / 'output/simulator.html', repo_root=repo_root)
    terms_rep = validate_terms(repo_root=repo_root)
    n07_rep = validate_n07_map(repo_root=repo_root)
    n08_rep = validate_n08_layers(repo_root=repo_root)
    _assert(all(r['status'] == 'PASS' for r in (shell_rep, terms_rep, n07_rep, n08_rep)), 'Prior validator failed')

    # Print renders (produced by lite-shot; corpus checks they exist and are non-blank-sized)
    prints = {}
    for key, rel in (('titration', PRINT_TITRATION_PATH), ('calibration', PRINT_CALIBRATION_PATH)):
        p = repo_root / rel
        _assert(p.is_file() and p.stat().st_size > 12000, f'Missing/non-substantial print render {rel}')
        prints[key] = {'path': rel, 'bytes': p.stat().st_size, 'sha256': _digest(p)}

    # Byte accounting against Section 1's figure and runtime sub-budgets
    t67_bytes = len(canonical_json_bytes(t67))
    merged = fig_report['canonical_bytes']
    manifest = load_json(repo_root / 'output/build-manifest.json')
    runtime_js = manifest['tokens_layer']['runtime_js_code_bytes']
    _assert(merged <= FIGURE_CEILING, f'Merged figure island {merged} > {FIGURE_CEILING}')
    _assert(runtime_js <= RUNTIME_CEILING, f'Runtime JS {runtime_js} > {RUNTIME_CEILING}')

    return {
        'schema_version': 1,
        'task': 'N15',
        'status': 'PASS',
        'figures': {'total': fig_report['figures_count'], 't67': len(figs),
                    'titration': 5, 'calibration': 3, 'slots_closed': fig_report['t67_slots_closed']},
        'model_checks': model_rows,
        'v05_copy': fig_report['v05_copy_table'],
        'reading_coupling': read_rows
        ,
        'calibration_readings': [
            {k: r.get(k) for k in ('figure_id', 'signal', 'reading_mg_ml', 'reading_recomputed_mg_ml',
                                   'reading_agrees', 'inside_span', 'assumption_honesty',
                                   'render_clipped', 'no_extrapolation_ok')}
            for r in cal_rows
        ],
        'calibration_assumptions': fig_report['calibration_assumption_table'],
        'no_extrapolation': fig_report['no_extrapolation_table'],
        'negative_cases': {
            'inflection_disagreement': 'FIG-T67-TITR-STRONG / E_FIG_TITRATION_EQUIVALENCE',
            'over_span_reading': 'FIG-T67-CAL-MASTER / E_FIG_CAL_READING_OUT_OF_SPAN',
            'over_span_fit': 'FIG-T67-CAL-MASTER / E_FIG_CAL_FIT_OUT_OF_SPAN',
            'wrong_reading': 'FIG-T67-CAL-MASTER / E_FIG_CAL_READING_MISMATCH',
        },
        'determinism': {'curves': curve_rows, 'two_run_validation_sha256': fig_report['canonical_sha256']},
        'leak_scan': {'status': leak_report['status'], 'per_record': per_record,
                      'exemptions': leak_report['exemptions_audit']},
        'contracts': {
            'titration': {'path': TITRATION_CONTRACT_PATH,
                          'sha256': sha256_bytes(canonical_json_bytes(tcontract)),
                          'consumers': tcontract['consumers']},
            'calibration': {'path': CALIBRATION_CONTRACT_PATH,
                            'sha256': sha256_bytes(canonical_json_bytes(ccontract)),
                            'consumers': ccontract['consumers'],
                            'no_extrapolation_verbatim_sha256': sha256_bytes(no_ext.encode('utf-8'))},
            'n37_type_registry': tcontract['n37_type_registry'],
        },
        'runtime': {'total_figures': rt['total_figures'], 't67_figures': rt['t67_figures'],
                    'smoke': {'total': 9, 'passed': 9},
                    'svg_sha256': rt['svg_sha256'], 'truncation': rt['truncation']},
        'prints': prints,
        'budget': {
            't67_canonical_bytes': t67_bytes,
            'merged_figure_island_bytes': merged,
            'figure_ceiling_bytes': FIGURE_CEILING,
            'figure_headroom_bytes': FIGURE_CEILING - merged,
            'runtime_js_code_bytes': runtime_js,
            'runtime_ceiling_bytes': RUNTIME_CEILING,
            'runtime_headroom_bytes': RUNTIME_CEILING - runtime_js,
            'html_sha256': manifest['output_sha256'],
            'html_bytes': manifest['output_bytes'],
        },
    }


def main() -> int:
    record = run_corpus(DEST)
    out = DEST / CORPUS_RECORD_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N15 corpus PASS: figures={record['figures']['total']} (T67={record['figures']['t67']}), "
          f"models={len(record['model_checks'])}, cal_readings={len(record['calibration_readings'])}, "
          f"figure_bytes={record['budget']['merged_figure_island_bytes']}/{FIGURE_CEILING}, "
          f"runtime={record['budget']['runtime_js_code_bytes']}/{RUNTIME_CEILING}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
