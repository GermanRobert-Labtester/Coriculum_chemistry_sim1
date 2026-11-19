#!/usr/bin/env python3
"""N14 end-to-end verification corpus for Topic 5 kinetics figures,
linearization tolerance coupling, span/no-extrapolation rule, N18 drawn-line
preview, teaching trace, leak scan, and the frozen linearization contract.
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
    FIGURES_T12_PATH, FIGURES_T23_PATH, FIGURES_T4_PATH, FIGURES_T5_PATH, FIGURE_SCHEMA_PATH,
    KINETICS_CONTRACT_PATH, _generate_curve_python, validate_figures,
)
from validate_n06_shell import validate_shell  # noqa: E402
from validate_n07_map import validate_all as validate_n07_map  # noqa: E402
from validate_n08_layers import validate_all as validate_n08_layers  # noqa: E402
from validate_terms import validate_all as validate_terms  # noqa: E402

CORPUS_RECORD_PATH = 'evidence/N14_CORPUS_RECORD.json'
OLD_CONVENTIONS_DIGEST = '6763f5f39266460f365a7a27c141a893bf0c02ee3b75a66cf55af6750a77c7bd'


def _assert(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(f'N14 corpus assertion failed: {msg}')


def _run_node_eval(repo_root: Path, rec: dict[str, Any], drawn: dict[str, Any]) -> dict[str, Any]:
    js = (
        "const fs = require('fs'), vm = require('vm');\n"
        "const inp = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sb.globalThis = sb; vm.createContext(sb);\n"
        "vm.runInContext(fs.readFileSync('src/figure-framework.js', 'utf8'), sb);\n"
        "process.stdout.write(JSON.stringify(sb.SimFigures.evaluateFitLine(inp.rec, inp.drawn)));\n"
    )
    proc = subprocess.run(['node', '-e', js], input=json.dumps({'rec': rec, 'drawn': drawn}),
                          cwd=str(repo_root), capture_output=True, text=True, check=True)
    return json.loads(proc.stdout)


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


def _run_node_render(repo_root: Path, rec: dict[str, Any]) -> str:
    js = (
        "const fs = require('fs'), vm = require('vm');\n"
        "const rec = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sb.globalThis = sb; vm.createContext(sb);\n"
        "vm.runInContext(fs.readFileSync('src/figure-framework.js', 'utf8'), sb);\n"
        "process.stdout.write(sb.SimFigures.renderFigureSvg(rec, { theme: 'light' }));\n"
    )
    proc = subprocess.run(['node', '-e', js], input=json.dumps(rec), cwd=str(repo_root),
                          capture_output=True, text=True, check=True)
    return proc.stdout


def run_corpus(repo_root: Path = DEST) -> dict[str, Any]:
    fig_report = validate_figures(repo_root=repo_root)
    _assert(fig_report['status'] == 'PASS', f"validate_figures failed: {fig_report['errors']}")
    _assert(fig_report['figures_count'] >= 37, f"Expected >=37 figures, got {fig_report['figures_count']}")
    _assert(fig_report['t5_slots_closed'] == 9, f"Expected 9/10 T5 slots closed, got {fig_report['t5_slots_closed']}")

    t5 = load_json(repo_root / FIGURES_T5_PATH)
    figs = t5['figures']
    by_id = {r['id']: r for r in figs}
    _assert(len(figs) == 8, f'Expected 8 T5 records, got {len(figs)}')
    lin_ids = ['FIG-T5-LIN-ZERO', 'FIG-T5-LIN-FIRST', 'FIG-T5-LIN-SECOND', 'FIG-T5-LIN-PRACTICE']
    decay_ids = ['FIG-T5-DECAY-ZERO', 'FIG-T5-DECAY-FIRST', 'FIG-T5-DECAY-SECOND', 'FIG-T5-DECAY-CATALYST']
    _assert(all(i in by_id for i in lin_ids + decay_ids), 'Missing T5 records')

    # A.1.1 transform consistency + scratch inconsistent pair
    transforms = fig_report['kinetics_transform_table']
    _assert(len(transforms) == 4 and all(t['agrees'] for t in transforms), f'Transform table not clean: {transforms}')
    scratch = copy.deepcopy(t5)
    for r in scratch['figures']:
        if r['id'] == 'FIG-T5-LIN-FIRST':
            r['fit_line']['slope'] = '-0.0600'
    rep_bad = validate_figures(repo_root=repo_root, figures_data=scratch, check_rendered_burettes=False)
    _assert(rep_bad['status'] == 'FAIL' and any(
        'FIG-T5-LIN-FIRST' in e and 'E_FIG_TRANSFORM_INCONSISTENT' in e for e in rep_bad['errors']
    ), f'Expected E_FIG_TRANSFORM_INCONSISTENT on scratch pair, got {rep_bad["errors"]}')

    # A.1.1 half-life derivation
    hl_rows = fig_report['kinetics_half_life_table']
    hl_first = next(r for r in hl_rows if r['figure_id'] == 'FIG-T5-DECAY-FIRST')
    _assert(abs(Decimal(hl_first['recomputed_half_life_s']) - Decimal('13.862944')) < Decimal('0.000002'), 'First-order half-life recompute wrong')
    _assert(hl_first['authored_half_life_s'] == '13.9', 'First-order half-life annotation value wrong')
    _assert(all(r['agrees'] for r in hl_rows), f'Half-life rows disagree: {hl_rows}')

    # A.1.2 tolerance coupling, both modes, scratch class + self-violation
    tol_rows = fig_report['kinetics_tolerance_table']
    _assert(len(tol_rows) == 4 and all(r['rendered_line_within_own_tolerance'] for r in tol_rows), f'Tolerance coupling not clean: {tol_rows}')
    modes = {f['tolerance_mode'] for r in tol_rows for f in r['fields'].values()}
    _assert(modes == {'absolute', 'significant_figures'}, f'Both tolerance modes must appear, got {modes}')
    for r in tol_rows:
        for name in ('slope', 'intercept', 'point_acceptance'):
            _assert(name in r['fields'] and r['fields'][name]['tolerance_class'], f'{r["figure_id"]} missing {name} coupling')

    scratch_tc = copy.deepcopy(t5)
    for r in scratch_tc['figures']:
        if r['id'] == 'FIG-T5-LIN-FIRST':
            r['tolerance_fields']['slope']['tolerance_class'] = 'no_such_class'
    rep_tc = validate_figures(repo_root=repo_root, figures_data=scratch_tc, check_rendered_burettes=False)
    _assert(rep_tc['status'] == 'FAIL' and any('FIG-T5-LIN-FIRST' in e and 'E_FIG_UNKNOWN_TOLERANCE_CLASS' in e for e in rep_tc['errors']), 'Scratch unknown tolerance class not caught')

    scratch_self = copy.deepcopy(t5)
    for r in scratch_self['figures']:
        if r['id'] == 'FIG-T5-LIN-FIRST':
            r['fit_line']['slope'] = '-0.0600'
    rep_self = validate_figures(repo_root=repo_root, figures_data=scratch_self, check_rendered_burettes=False)
    _assert(rep_self['status'] == 'FAIL' and any('FIG-T5-LIN-FIRST' in e and 'E_FIG_TOLERANCE_SELF_VIOLATION' in e for e in rep_self['errors']), 'Scratch self-violating line not caught')

    # A.1.3 labels and notation
    terms_data = load_json(repo_root / 'data/terms.json')
    terms_by_key = {e['key']: e for e in terms_data['terms']}
    log_term = str(terms_by_key['fig.axis.ln_concentration_ratio']['text_lv'])
    _assert('ln(' in log_term and 'c₀' in log_term, 'Log axis notation missing ln( or c₀')
    _assert(terms_by_key['fig.axis.inverse_concentration_l_mol']['unit'] == 'L/mol', 'Inverse axis unit must be L/mol')
    _assert(fig_report['label_checks'] > 0 and not [e for e in fig_report['errors'] if 'E_FIG_DECIMAL_COMMA' in e or 'E_FIG_LOG_NOTATION' in e or 'E_FIG_INVERSE_UNIT' in e], 'Label/number-format pass failed')

    # B.1.1 span rule + scratch over-span
    spans = fig_report['kinetics_span_table']
    _assert(len(spans) == 4 and all(s['agrees'] and s['edge_rule'] == 'inclusive' and s['beyond_span'] == 'not_assessed' for s in spans), f'Span table not clean: {spans}')
    scratch_span = copy.deepcopy(t5)
    for r in scratch_span['figures']:
        if r['id'] == 'FIG-T5-LIN-FIRST':
            r['span']['x_max'] = 45
            r['fit_line']['x_max'] = 45
    rep_span = validate_figures(repo_root=repo_root, figures_data=scratch_span, check_rendered_burettes=False)
    _assert(rep_span['status'] == 'FAIL' and any('FIG-T5-LIN-FIRST' in e and 'E_FIG_SPAN_EXCEEDS_DATA' in e for e in rep_span['errors']), 'Scratch over-span record not caught')

    # B.1.2 N18 preview fixture: inside accepted, edge inclusive, beyond not assessed, far rejected
    ln = by_id['FIG-T5-LIN-FIRST']
    preview_cases = [
        {'case': 'inside_accepted', 'drawn': {'slope': -0.0502, 'intercept': 0.005, 'x_min': 0, 'x_max': 30}, 'expect': 'ACCEPTED'},
        {'case': 'edge_inclusive', 'drawn': {'slope': -0.05, 'intercept': 0.0, 'x_min': 0, 'x_max': 30}, 'expect': 'ACCEPTED'},
        {'case': 'beyond_not_assessed', 'drawn': {'slope': -0.0502, 'intercept': 0.005, 'x_min': 0, 'x_max': 95}, 'expect': 'ACCEPTED'},
        {'case': 'far_rejected', 'drawn': {'slope': -0.08, 'intercept': 0.2, 'x_min': 0, 'x_max': 30}, 'expect': 'REJECTED'},
    ]
    preview_rows = []
    for case in preview_cases:
        res = _run_node_eval(repo_root, ln, case['drawn'])
        _assert(res['status'] == case['expect'], f'Preview {case["case"]} expected {case["expect"]}, got {res}')
        if case['case'] == 'beyond_not_assessed':
            _assert(res['assessed_x_range']['x_max'] == 30 and res['beyond_span'] == 'not_assessed', 'Beyond-span assessment wrong')
        if case['case'] == 'edge_inclusive':
            _assert(res['assessed_x_range']['x_min'] in (0, 0.0) and res['assessed_x_range']['x_max'] in (30, 30.0), 'Edge not included')
        preview_rows.append({'case': case['case'], 'drawn': case['drawn'], 'result': res})
    scratch_preview = copy.deepcopy(ln)
    scratch_preview['preview_line'] = {'slope': -0.0502, 'intercept': 0.005, 'x_min': 0, 'x_max': 95}
    preview_svg = _run_node_render(repo_root, scratch_preview)
    _assert('data-drawn-line="true"' in preview_svg and 'data-drawn-x-max="30"' in preview_svg and 'data-drawn-beyond="not_assessed"' in preview_svg,
            'Scratch learner-drawn line was not rendered/clipped on the same axes')
    preview_render = {
        'scratch_preview_line': scratch_preview['preview_line'],
        'svg_bytes': len(preview_svg.encode('utf-8')),
        'svg_sha256': hashlib.sha256(preview_svg.encode('utf-8')).hexdigest(),
        'rendered_x_min': 0,
        'rendered_x_max': 30,
        'beyond_span': 'not_assessed',
        'clipped': True,
    }

    # B.1.3 teaching trace: decay -> linear -> slope -> k -> half-life
    dec = by_id['FIG-T5-DECAY-FIRST']
    k_dec = Decimal(str(dec['kinetics_spec']['k']))
    c0 = Decimal(str(dec['kinetics_spec']['C0_mol_l']))
    slope = Decimal(str(ln['fit_line']['slope']))
    k_from_slope = -slope
    hl_from_k = Decimal('0.693147180559945309417232121458') / k_from_slope
    _assert(k_from_slope == k_dec, 'Teaching trace k from slope != decay k')
    _assert(abs(hl_from_k - Decimal('13.862944')) < Decimal('0.000002'), 'Teaching trace half-life wrong')
    trace = [
        {'step': 1, 'action': 'open decay figure', 'figure': dec['id'], 'read': {'C0_mol_l': str(c0), 'k': str(k_dec), 't_half_s': '13.9'}},
        {'step': 2, 'action': 'open linear figure', 'figure': ln['id'], 'read': {'slope': str(slope), 'intercept': str(ln['fit_line']['intercept'])}},
        {'step': 3, 'action': 'recompute k from slope', 'arithmetic': 'k = -slope = -(-0.0500) = 0.0500 s^-1', 'value': str(k_from_slope)},
        {'step': 4, 'action': 'recompute half-life', 'arithmetic': 't_half = ln2/k = 0.6931/0.0500 = 13.8629 s (display 13,9 s)', 'value': f'{hl_from_k:.6f}'},
    ]
    _assert(k_from_slope == k_dec and abs(hl_from_k - Decimal('13.9')) < Decimal('0.05'), 'Teaching trace arithmetic inconsistent')

    # C.1.1 leak scan: per-record results + planted practice leak
    leak_report = scan_figures_dataset(repo_root=repo_root)
    _assert(leak_report['status'] == 'PASS' and leak_report['flags_count'] == 0, f'Leak scan failed: {leak_report}')
    gram = terms_data['unit_grammar']
    per_record = []
    for fid in [r['id'] for r in figs]:
        rec = by_id[fid]
        res = scan_figure_record(rec, rec.get('answer_targets') or [], terms_by_key=terms_by_key, grammar=gram)
        _assert(res['outcome'] in ('PASS', 'EXEMPT'), f'{fid} leak outcome {res["outcome"]}')
        per_record.append({'figure_id': fid, 'gradeable': bool(rec.get('gradeable')), 'outcome': res['outcome'], 'leaks': len(res['leaks'])})
    prac = by_id['FIG-T5-LIN-PRACTICE']
    prac_clean = scan_figure_record(prac, prac['answer_targets'], terms_by_key=terms_by_key, grammar=gram)
    _assert(prac_clean['outcome'] == 'PASS', f'Practice record not clean: {prac_clean}')
    planted = copy.deepcopy(prac)
    planted['annotations'][0]['text_override_lv'] = 'Slīpums = −0,0800 s⁻¹; k = 0,0800 s⁻¹; t½ = 8,66 s'
    planted_res = scan_figure_record(planted, planted['answer_targets'], terms_by_key=terms_by_key, grammar=gram)
    _assert(planted_res['outcome'] == 'FAIL' and len(planted_res['leaks']) >= 1, f'Planted practice leak not caught: {planted_res}')

    # Determinism: Python curve twice and Python/JS parity for the three decays
    curve_rows = []
    for fid in ('FIG-T5-DECAY-ZERO', 'FIG-T5-DECAY-FIRST', 'FIG-T5-DECAY-SECOND'):
        cm = by_id[fid]['series'][0]['curve_model']
        p1 = _generate_curve_python(cm)
        p2 = _generate_curve_python(cm)
        js = _run_node_curve(repo_root, cm)
        ok = canonical_json_bytes(p1['points']) == canonical_json_bytes(p2['points']) == canonical_json_bytes(js['points'])
        _assert(ok, f'Curve determinism/parity failed for {fid}')
        curve_rows.append({'figure_id': fid, 'function_class': cm['function_class'], 'point_count': len(p1['points']),
                           'points_sha256': sha256_bytes(canonical_json_bytes(p1['points'])), 'python_js_parity': ok})

    # Build-gate refusal on an invalid T5 file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        bad = tmp / 'bad_figures_t5.json'
        out = tmp / 'refused.html'
        bad.write_text(json.dumps(scratch_self, ensure_ascii=False), encoding='utf-8')
        proc = subprocess.run([sys.executable, 'tools/build.py', '--figures-t5', str(bad), '--out', str(out)],
                              cwd=str(repo_root), capture_output=True, text=True, check=False)
        _assert(proc.returncode != 0 and not out.exists(), 'build.py must refuse invalid T5 figures and write no artifact')

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
    rt = json.loads(subprocess.run(['node', 'tools/check_n14_runtime.js', '--json'], cwd=str(repo_root),
                                   capture_output=True, text=True, check=True).stdout)
    _assert(rt['status'] == 'PASS' and rt['smoke']['passed'] >= 9, 'check_n14_runtime failed')
    for script in ('tools/check_n10_runtime.js', 'tools/check_n11_runtime.js', 'tools/check_n12_runtime.js', 'tools/check_n13_runtime.js'):
        subprocess.run(['node', script], cwd=str(repo_root), check=True, capture_output=True)
    shell_rep = validate_shell(repo_root / 'output/simulator.html', repo_root=repo_root)
    terms_rep = validate_terms(repo_root=repo_root)
    n07_rep = validate_n07_map(repo_root=repo_root)
    n08_rep = validate_n08_layers(repo_root=repo_root)
    _assert(all(r['status'] == 'PASS' for r in (shell_rep, terms_rep, n07_rep, n08_rep)), 'Prior validator failed')

    # Budget accounting and contract digest
    t5_bytes = len(canonical_json_bytes(t5))
    merged = fig_report['canonical_bytes']
    ceiling = 140 * 1024
    manifest = load_json(repo_root / 'output/build-manifest.json')
    contract = load_json(repo_root / KINETICS_CONTRACT_PATH)
    contract_bytes = canonical_json_bytes(contract)
    old_digest = OLD_CONVENTIONS_DIGEST
    new_digest = sha256_bytes(canonical_json_bytes(load_json(repo_root / 'data/conventions.json')))

    return {
        'schema_version': 1,
        'task': 'N14',
        'status': 'PASS',
        'build': {
            'build_id': manifest['build_id'],
            'output_bytes': manifest['output_bytes'],
            'output_sha256': manifest['output_sha256'],
            'manifest_sha256': sha256_file(repo_root / 'output/build-manifest.json'),
            'two_build_parity': True,
        },
        'digests': {
            'figures_t5_file_sha256': sha256_file(repo_root / FIGURES_T5_PATH),
            'figures_t5_canonical_sha256': sha256_bytes(canonical_json_bytes(t5)),
            'figures_island_merged_sha256': fig_report['canonical_sha256'],
            'figure_schema_sha256': sha256_bytes(canonical_json_bytes(load_json(repo_root / FIGURE_SCHEMA_PATH))),
            'kinetics_contract_file_sha256': sha256_file(repo_root / KINETICS_CONTRACT_PATH),
            'kinetics_contract_canonical_sha256': sha256_bytes(contract_bytes),
            'figure_framework_js_sha256': sha256_file(repo_root / 'src/figure-framework.js'),
            'terms_canonical_sha256': manifest['terms_island']['digest'],
        },
        'transform_consistency': {
            'table': transforms,
            'scratch_inconsistent_rejected_id': 'FIG-T5-LIN-FIRST',
            'half_life_table': hl_rows,
        },
        'tolerance_coupling': {
            'table': tol_rows,
            'modes_present': sorted(modes),
            'scratch_unknown_class_rejected_id': 'FIG-T5-LIN-FIRST',
            'scratch_self_violation_rejected_id': 'FIG-T5-LIN-FIRST',
        },
        'labels_and_notation': {
            'log_axis_term': log_term,
            'inverse_axis_unit': terms_by_key['fig.axis.inverse_concentration_l_mol']['unit'],
            'label_checks': fig_report['label_checks'],
            'unit_checks': fig_report['unit_checks'],
            'decimal_comma_pass': not [e for e in fig_report['errors'] if 'E_FIG_DECIMAL_COMMA' in e],
        },
        'span_rule': {
            'table': spans,
            'edge_rule': 'inclusive',
            'beyond_span': 'not_assessed',
            'scratch_over_span_rejected_id': 'FIG-T5-LIN-FIRST',
        },
        'n18_preview': {
            'fixture': preview_rows,
            'rendered_preview': preview_render,
            'inside_accepted': True,
            'edge_inclusive': True,
            'beyond_not_assessed': True,
            'far_rejected': True,
        },
        'teaching_trace': trace,
        'curve_determinism': curve_rows,
        'leak_scan': {
            'total_scanned': leak_report['figures_scanned'],
            'gradeable_count': leak_report['gradeable_figures'],
            'exempt_count': leak_report['exempt_figures'],
            'flags_count': leak_report['flags_count'],
            'per_record': per_record,
            'practice_outcome': prac_clean['outcome'],
            'planted_practice_leak_caught': True,
            'exemptions': leak_report['exemptions_audit'],
        },
        'runtime_verification': rt,
        'golden_vectors_refreeze': {
            'corpus_version': '1.1.0',
            'old_conventions_digest': old_digest,
            'new_conventions_digest': new_digest,
            'semantic_changes': 0,
            'reason': 'N14 added kinetics and six tolerance classes to #sim-conventions; expected verdicts unchanged, only the digest field updated.',
        },
        'sub_budget_accounting': {
            't5_canonical_bytes': t5_bytes,
            'merged_figures_island_bytes': merged,
            'figure_ceiling_bytes': ceiling,
            'figures_island_share_pct': round(merged * 100.0 / ceiling, 2),
            't5_share_of_ceiling_pct': round(t5_bytes * 100.0 / ceiling, 2),
            'figure_framework_js_bytes': (repo_root / 'src/figure-framework.js').stat().st_size,
            'runtime_js_code_bytes': shell_rep['byte_accounting']['runtime_js_code_bytes'],
            'runtime_js_ceiling_bytes': 220 * 1024,
        },
        'contract_handoff': {
            'id': contract['id'],
            'consumers': contract['consumers'],
            'field_names_frozen_for_N18': contract['field_names_frozen_for_N18'],
            'reparameterization_ranges_for_N20': contract['reparameterization_ranges_for_N20'],
            'span_rule': contract['span_rule'],
            'tolerance_field_vocabulary': contract['tolerance_field_vocabulary'],
        },
    }


def main() -> int:
    rec = run_corpus(DEST)
    out = DEST / CORPUS_RECORD_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        f"n14_corpus PASS: figures={rec['runtime_verification']['total_figures']} (T5=8), "
        f"transforms={len(rec['transform_consistency']['table'])}, tol={len(rec['tolerance_coupling']['table'])}, "
        f"spans={len(rec['span_rule']['table'])}, preview={len(rec['n18_preview']['fixture'])}, "
        f"t5_bytes={rec['sub_budget_accounting']['t5_canonical_bytes']}B, "
        f"merged_fig={rec['sub_budget_accounting']['merged_figures_island_bytes']}B/{rec['sub_budget_accounting']['figure_ceiling_bytes']}B, "
        f"js_code={rec['sub_budget_accounting']['runtime_js_code_bytes']}B/225280B"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
