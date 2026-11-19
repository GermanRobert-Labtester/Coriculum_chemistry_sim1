#!/usr/bin/env python3
"""N18 corpus: verdict tables, cross-language parity, the pointer/keyboard parity
matrix, the verdict replay proof, the inherited-rule fixtures, the budget
measurement and two-run parity.

Run: python3 tools/n18_corpus.py
     python3 tools/n18_corpus.py --out /tmp/n18_second.json
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
import graph_scoring_engine as gse  # noqa: E402
from validate_graph_scoring import validate as validate_graph_scoring  # noqa: E402
from validate_n06_shell import validate_shell  # noqa: E402

ROOT = DEST
OUT = ROOT / 'evidence'
ARTIFACT = ROOT / 'output' / 'simulator.html'
MANIFEST = ROOT / 'output' / 'build-manifest.json'
HARNESS = ROOT / 'tools' / 'check_n18_runtime.js'
ENGINE_JS = ROOT / 'src' / 'graph-scoring-engine.js'
ENGINE_PY = ROOT / 'tools' / 'graph_scoring_engine.py'
CONTRACT = ROOT / 'data' / 'graph_scoring_contract.json'


def island_text(island_id: str) -> str:
    html = ARTIFACT.read_text(encoding='utf-8')
    match = re.search(r'<script\s+type="application/json"\s+id="' + island_id +
                      r'"[^>]*>([\s\S]*?)</script>', html)
    if not match:
        raise SystemExit('missing island #' + island_id)
    return match.group(1).replace('<\\/', '</')


def digest_rows(rows: list[dict[str, Any]]) -> str:
    return sha256_bytes(gse.canonical_projection(rows).encode('utf-8'))


def python_rows(engine: gse.GraphScoringEngine, contract: dict[str, Any],
                figures: dict[str, dict[str, Any]], golden: dict[str, Any]) -> dict[str, Any]:
    """The same row projections the JavaScript harness emits."""
    n05_rows = []
    for vector in golden['vectors']:
        if vector.get('status') == 'retired' or vector['instance'].get('payload_class') != 'graph':
            continue
        verdict = engine.score_reading({'kind': 'n05_payload', 'instance': vector['instance']},
                                       vector['submission'], vector['instance']['rubric'])
        expected = vector['expected']
        ok = all(verdict[key] == expected[key] for key in (
            'verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
            'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points'))
        n05_rows.append({
            'id': vector['vector_id'], 'status': 'PASS' if ok else 'FAIL',
            'verdict_class': verdict['verdict_class'], 'error_class': verdict['error_class'],
            'tolerance_class': vector['instance']['payload']['target_readout']['tolerance_class'],
            'tolerance_mode': 'absolute',
            'deviation': verdict['assessed_geometry']['deviation'],
            'tolerance': verdict['assessed_geometry']['tolerance'],
        })

    stratum_rows = []
    parity_rows = []
    vectors = contract['graph_vectors']
    for vector in vectors['reading_vectors']:
        verdict = engine.score_reading(
            {'kind': 'figure', 'figure_id': vector['figure_id'],
             'criterion_shape': vector['criterion_shape']},
            vector['submission'], vector['rubric'])
        expected = vector['expected']
        ok = (verdict['verdict_class'] == expected['verdict_class']
              and verdict['error_class'] == expected['error_class']
              and verdict['machine_checked_points'] == expected['awarded_points'])
        stratum_rows.append({
            'id': vector['id'], 'kind': 'reading', 'status': 'PASS' if ok else 'FAIL',
            'verdict_class': verdict['verdict_class'], 'error_class': verdict['error_class'],
            'criterion_shape': vector['criterion_shape'],
            'deviation': verdict['assessed_geometry']['deviation'],
            'tolerance': verdict['assessed_geometry']['tolerance'],
        })
    for vector in vectors['drawing_vectors']:
        context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
        record = figures[context['figure_id']]
        pointer_payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
        keyboard_payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'keyboard')
        pointer_digest = gse.canonical_digest(pointer_payload)
        keyboard_digest = gse.canonical_digest(keyboard_payload)
        equal = pointer_digest == keyboard_digest
        pointer_verdict = engine.score_drawing(record, pointer_payload, vector['rubric'])
        keyboard_verdict = engine.score_drawing(record, keyboard_payload, vector['rubric'])
        expected = vector['expected']
        ok = (pointer_verdict['verdict_class'] == expected['verdict_class']
              and pointer_verdict['error_class'] == expected['error_class']
              and pointer_verdict['machine_checked_points'] == expected['awarded_points'])
        parity_ok = equal and pointer_verdict['verdict_class'] == keyboard_verdict['verdict_class'] \
            and pointer_verdict['error_class'] == keyboard_verdict['error_class']
        stratum_rows.append({
            'id': vector['id'], 'kind': 'drawing', 'status': 'PASS' if ok and parity_ok else 'FAIL',
            'verdict_class': pointer_verdict['verdict_class'],
            'error_class': pointer_verdict['error_class'],
            'criterion_shape': context['criterion_shape'],
            'checks': pointer_verdict['assessed_geometry']['checks'],
            'max_deviation': pointer_verdict['assessed_geometry']['max_deviation'],
            'excluded_points': len(pointer_verdict['assessed_geometry']['excluded_points']),
        })
        parity_rows.append({
            'id': vector['id'], 'status': 'PASS' if parity_ok else 'FAIL',
            'pointer_digest': pointer_digest, 'keyboard_digest': keyboard_digest,
            'point_count': len(pointer_payload['points']),
            'verdict': pointer_verdict['verdict_class'] + '/' + pointer_verdict['error_class'],
        })

    validity_rows = []
    for case in vectors['validity_corpus']:
        if case['family'] == 'drawing':
            context = contract['capture_contract']['capture_contexts'][case['capture_context']]
            record = figures[context['figure_id']]
            payload = engine.capture(case['capture_context'], case['target_geometry'], 'pointer')
            verdict = engine.score_drawing(record, payload, [
                {'criterion_id': 'C1_DRAW', 'grading': 'auto', 'points': 3.0}])
        else:
            verdict = engine.score_reading(
                {'kind': 'figure', 'figure_id': case['figure_id'],
                 'criterion_shape': case['criterion_shape']},
                case['submission'], [{'criterion_id': 'C1_READ', 'grading': 'auto', 'points': 2.0}])
        validity_rows.append({
            'id': case['id'], 'case': case['case'],
            'status': 'PASS' if verdict['error_class'] == case['expected_class'] else 'FAIL',
            'expected_class': case['expected_class'], 'actual_class': verdict['error_class'],
            'verdict_class': verdict['verdict_class'],
            'awarded_points': verdict['machine_checked_points'],
        })

    payload_rows = []
    for case in vectors['payload_validation_corpus']:
        actual = None
        try:
            engine.validate_payload(case['payload'])
        except gse.GraphError as exc:
            actual = exc.code
        payload_rows.append({
            'id': case['id'], 'case': case['case'],
            'status': 'PASS' if actual == case['expected_class'] else 'FAIL',
            'expected_class': case['expected_class'], 'actual_class': actual,
        })

    replay_rows = []
    for vector in [vectors['reading_vectors'][0], vectors['reading_vectors'][1],
                   vectors['drawing_vectors'][1], vectors['drawing_vectors'][4]]:
        if vector['family'] == 'reading':
            verdict = engine.score_reading(
                {'kind': 'figure', 'figure_id': vector['figure_id'],
                 'criterion_shape': vector['criterion_shape']},
                vector['submission'], vector['rubric'])
        else:
            context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
            record = figures[context['figure_id']]
            payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
            verdict = engine.score_drawing(record, payload, vector['rubric'])
        replayed = engine.replay_verdict(verdict)
        ok = (replayed.get('verdict_class') == verdict['verdict_class']
              and replayed.get('error_class') == verdict['error_class'])
        replay_rows.append({
            'id': vector['id'], 'status': 'PASS' if ok else 'FAIL',
            'original': verdict['verdict_class'] + '/' + verdict['error_class'],
            'replayed': str(replayed.get('verdict_class')) + '/' + str(replayed.get('error_class')),
        })

    # The full verdict records, canonically projected: the cross-language
    # comparison must reproduce the whole record, not only the summary rows.
    verdict_records: dict[str, str] = {}
    for vector in golden['vectors']:
        if vector.get('status') == 'retired' or vector['instance'].get('payload_class') != 'graph':
            continue
        verdict = engine.score_reading({'kind': 'n05_payload', 'instance': vector['instance']},
                                       vector['submission'], vector['instance']['rubric'])
        verdict_records[vector['vector_id']] = gse.canonical_projection(verdict)
    for vector in vectors['reading_vectors']:
        verdict = engine.score_reading(
            {'kind': 'figure', 'figure_id': vector['figure_id'],
             'criterion_shape': vector['criterion_shape']},
            vector['submission'], vector['rubric'])
        verdict_records[vector['id']] = gse.canonical_projection(verdict)
    for vector in vectors['drawing_vectors']:
        context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
        record = figures[context['figure_id']]
        payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
        verdict = engine.score_drawing(record, payload, vector['rubric'])
        verdict_records[vector['id']] = gse.canonical_projection(verdict)

    return {
        'n05': n05_rows, 'stratum': stratum_rows, 'validity': validity_rows,
        'payload': payload_rows, 'parity': parity_rows, 'replay': replay_rows,
        'verdict_records': verdict_records,
        'capture_cross': capture_rows(engine, contract, figures),
    }


def js_round(value: float) -> int:
    """JavaScript's Math.round: halves go towards +infinity."""
    return math.floor(value + 0.5)


def keyboard_path(start: list[float], moves: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """The keyboard path of the capture component, in the Python twin.

    Mirrors src/graph-capture.js: the active point is stepped by the declared
    increments, and a movement that does not change x updates the current
    point instead of adding a vertex (N18-CAPTURE-PATH-01).
    """
    active = [gse.q12(start[0]), gse.q12(start[1])]
    path: list[list[float]] = [list(active)]
    for dx, dy in moves:
        active = [gse.q12(active[0] + dx), gse.q12(active[1] + dy)]
        if path[-1][0] == active[0]:
            path[-1] = list(active)
        else:
            path.append(list(active))
    return [(point[0], point[1]) for point in path]


def capture_rows(engine: gse.GraphScoringEngine, contract: dict[str, Any],
                 figures: dict[str, Any]) -> list[dict[str, Any]]:
    """The keyboard-side capture rows, in the Python twin.

    The pointer side of the parity is a browser input detail (the sampling
    threshold); the keyboard side is fully determined by the declared
    increments, so this is the part the twin can reproduce.
    """
    contexts = contract['capture_contract']['capture_contexts']
    rows: list[dict[str, Any]] = []
    for context_id in sorted(contexts):
        derived = engine.keyboard_increments(context_id)
        rows.append({
            'id': f'CAP-INC-{context_id}', 'kind': 'increments',
            'coarse_x': derived['coarse_x'], 'fine_x': derived['fine_x'],
            'coarse_y': derived['coarse_y'], 'fine_y': derived['fine_y'],
        })

    context_id = 'CAP-T67-CAL-PRACTICE'
    increments = engine.keyboard_increments(context_id)

    # CP-01: the diagonal walk of a line whose slope is a multiple of the
    # declared fine-step ratio.
    slope = increments['fine_y'] / increments['fine_x']
    steps = int(round((0.016 - 0) / increments['fine_x']))
    moves = [(increments['fine_x'], increments['fine_y'])] * steps
    payload = engine.capture_path(context_id, keyboard_path([0, 0], moves))
    rows.append({'id': 'CAP-PARITY-01', 'kind': 'payload_parity',
                 'keyboard_digest': gse.canonical_digest(payload)})

    # CP-02: the placed walk of the true calibration line, with the y placed
    # at the finest declared increment.
    slope = 25.02
    grid_step = float(contexts[context_id]['grid']['step'])
    moves = []
    y = 0.0
    for cell in range(8):
        moves.append((increments['coarse_x'], 0))
        target = slope * (grid_step * (cell + 1))
        count = js_round((target - y) / increments['fine_y'])
        for _ in range(abs(count)):
            moves.append((0, increments['fine_y'] if count >= 0 else -increments['fine_y']))
        y = gse.q12(y + count * increments['fine_y'])
    payload = engine.capture_path(context_id, keyboard_path([0, 0], moves))
    record = figures[contexts[context_id]['figure_id']]
    verdict = engine.score_drawing(record, payload,
                                   [{'criterion_id': 'C1_DRAW', 'grading': 'auto', 'points': 3.0}])
    rows.append({
        'id': 'CAP-PARITY-02', 'kind': 'verdict_parity',
        'keyboard_digest': gse.canonical_digest(payload),
        'keyboard_deviation': verdict['assessed_geometry']['max_deviation'],
        'keyboard_verdict': f"{verdict['verdict_class']}/{verdict['error_class']}",
    })

    # CP-03: the reading mark, walked with the keyboard.
    moves = [(increments['coarse_x'], 0)] * 4 + [(0, increments['fine_y'])] * 134
    path = keyboard_path([0, 0], moves)
    mark = engine.capture_path(context_id, [[path[-1][0], path[-1][1]]])
    rows.append({'id': 'CAP-PARITY-03', 'kind': 'mark_parity',
                 'keyboard_digest': gse.canonical_digest(mark)})
    return rows


def compacted_engine_bytes() -> int:
    proc = subprocess.run(
        [sys.executable, '-c',
         'import sys;sys.path.insert(0,"tools");from tools.build import compact_js_source;'
         'print(compact_js_source(open("src/graph-scoring-engine.js",encoding="utf-8").read()),end="")'],
        cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit('compacted engine measurement failed: ' + proc.stderr[:300])
    return len(proc.stdout.encode('utf-8'))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT / 'N18_CORPUS_RECORD.json'))
    args = parser.parse_args(argv)

    report = validate_graph_scoring(repo_root=ROOT)
    if report['status'] != 'PASS':
        print('FAIL graph scoring gate:', report['errors'][:5], file=sys.stderr)
        return 1
    report2 = validate_graph_scoring(repo_root=ROOT)
    validation_parity = gse.canonical_projection(report) == gse.canonical_projection(report2)

    harness = subprocess.run(['node', str(HARNESS)], cwd=str(ROOT), capture_output=True, text=True)
    if harness.returncode != 0:
        print('FAIL runtime harness:', (harness.stderr or '')[:800], file=sys.stderr)
        return 1
    runtime = json.loads(harness.stdout)
    if runtime['status'] != 'PASS':
        print('FAIL runtime status', file=sys.stderr)
        return 1

    engine = gse.load()
    contract = load_json(CONTRACT)
    figures = gse.load_figures(repo_root=ROOT)
    golden = load_json(ROOT / 'data' / 'golden_vectors.json')
    py = python_rows(engine, contract, figures, golden)
    js = runtime['rows']

    compared = {}
    cross_status = 'PASS'
    for table in ('n05', 'stratum', 'capture_cross', 'validity', 'payload', 'parity', 'replay'):
        py_digest = digest_rows(py[table])
        js_digest = digest_rows(js[table])
        same = py_digest == js_digest
        if not same:
            cross_status = 'FAIL'
        compared[table] = {
            'python_digest': py_digest, 'javascript_digest': js_digest,
            'status': 'PASS' if same else 'FAIL', 'rows': len(py[table]),
        }
    # The full verdict records must match record for record.
    js_records = runtime.get('verdict_records') or {}
    record_diffs = []
    for vector_id, projection in sorted(py['verdict_records'].items()):
        if js_records.get(vector_id) != projection:
            record_diffs.append(vector_id)
    compared['verdict_records'] = {
        'python_digest': digest_rows([py['verdict_records'][k] for k in sorted(py['verdict_records'])]),
        'javascript_digest': digest_rows([js_records[k] for k in sorted(js_records)]),
        'status': 'PASS' if not record_diffs else 'FAIL',
        'rows': len(py['verdict_records']),
        'differing_vector_ids': record_diffs,
    }
    if record_diffs:
        cross_status = 'FAIL'
    if cross_status != 'PASS':
        print('FAIL cross-language parity', compared, file=sys.stderr)
        return 1

    py2 = python_rows(engine, contract, figures, golden)
    corpus_parity = {table: digest_rows(py[table]) == digest_rows(py2[table])
                     for table in ('n05', 'stratum', 'capture_cross', 'validity', 'payload',
                                   'parity', 'replay')}
    corpus_parity['verdict_records'] = py['verdict_records'] == py2['verdict_records']

    html = ARTIFACT.read_text(encoding='utf-8')
    shell = validate_shell(html_text=html, repo_root=ROOT)
    manifest = load_json(MANIFEST)
    compiled = compacted_engine_bytes()
    ceiling = shell['byte_accounting']['runtime_js_ceiling_bytes']
    budget = {
        'runtime_js_code_bytes': shell['byte_accounting']['runtime_js_code_bytes'],
        'runtime_js_ceiling_bytes': ceiling,
        'runtime_js_headroom_bytes': ceiling - shell['byte_accounting']['runtime_js_code_bytes'],
        'runtime_js_declared_band_bytes': [120 * 1024, 220 * 1024],
        'graph_scoring_island_bytes': manifest['graph_scoring_island']['bytes'],
        'graph_scoring_island_digest': manifest['graph_scoring_island']['digest'],
        'engine_compiled_bytes': compiled,
        'engine_source_bytes': ENGINE_JS.stat().st_size,
        'engine_compiled_share_of_ceiling': round(compiled / ceiling, 6),
        'engine_compiled_share_of_declared_band': round(compiled / (220 * 1024), 6),
        'artifact_bytes': manifest['output_bytes'],
        'artifact_sha256': manifest['output_sha256'],
        'graph_scoring_gate': next(g['summary'] for g in manifest['gates'] if g['id'] == 'graph_scoring'),
        'status': 'PASS',
        'note': ('The Section 1.3 runtime-JS code ceiling was already 83 bytes from its limit before N18, '
                 'so the graph scoring module ships as src/graph-scoring-engine.js, is validated by '
                 'gate 14, and its contract and vectors ship in #sim-graph-scoring. The runtime harness '
                 'loads the module directly against the shipped islands. N31 must lazy-load or '
                 're-budget before inlining it.'),
    }

    record = {
        'schema_version': 1, 'task': 'N18', 'status': 'PASS',
        'validation': {
            'status': report['status'], 'summary': report['summary'],
            'digests': report['digests'], 'errors': report['errors'],
        },
        'validation_parity': validation_parity,
        'vectors': {
            'n05_rows': report['n05_rows'],
            'stratum_rows': report['stratum_rows'],
            'tolerance_mode_rows': report['tolerance_mode_rows'],
        },
        'validity': {
            'rows': report['validity_rows'],
            'precedence_rule_verbatim': report['precedence_rule_verbatim'],
            'corner_case': next((row for row in report['validity_rows'] if row['id'] == 'VAL-N18-05'), None),
        },
        'payload_validation': {'rows': report['payload_rows']},
        'parity_matrix': {
            'rows': py['parity'],
            'device_agnostic_rule_verbatim':
                contract['capture_contract']['device_agnostic_rule_verbatim'],
            'keyboard_increment_rule_verbatim':
                contract['capture_contract']['keyboard_increments']['rule_verbatim'],
            'keyboard_increment_examples':
                contract['capture_contract']['keyboard_increments']['keyboard_increment_examples'],
        },
        'replay': {'rows': report['replay_rows'],
                   'rule_verbatim': contract['verdict_record']['replay_rule_verbatim']},
        'inheritance': {
            'rows': report['inheritance_rows'],
            'rule_verbatim': report['inherited_rule_verbatim'],
            'edge_verbatim': report['span_edge_verbatim'],
            'assertion_verbatim': contract['inheritance_check']['assertion_verbatim'],
        },
        'keyboard': {
            'rows': report['keyboard_rows'],
            'scratch_rows': report['keyboard_scratch_rows'],
            'path_merge_rule_verbatim':
                contract['capture_contract']['path_merge_rule_verbatim'],
            'keyboard_trace_rule_verbatim':
                contract['capture_contract']['keyboard_trace_rule_verbatim'],
            'capture_rows': runtime['rows']['capture'],
            'capture_cross_rows': py['capture_cross'],
        },
        'scratch': {'rows': report['scratch_rows']},
        'cross_language': {'status': cross_status, 'tables': compared},
        'corpus_parity': corpus_parity,
        'budget': budget,
        'smoke': runtime['smoke_summary'],
        'smoke_digest': runtime['smoke']['vectors'][0]['details']['digest'],
        'runtime': {'status': runtime['status'], 'parity': runtime['parity'],
                    'counts': runtime['counts'], 'digests': runtime['digests'],
                    'artifact_sha256': runtime['artifact_sha256']},
        'handoff': {
            'n20': 'criterion shapes, tolerance resolution and the reparameterization bounds',
            'n22': 'the sim-graph-draw-v1 payload schema and the input semantics',
            'n23': 'the verdict record schema, the cited-entry rule and the validity precedence',
            'n33': 'the keyboard increments, the assessment grid and the device-agnostic payload',
            'n31': 'inline or lazy-load src/graph-scoring-engine.js and src/graph-capture.js after the budget decision',
        },
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': record['status'], 'out': str(out), 'bytes': out.stat().st_size,
        'sha256': sha256_file(out), 'validation_parity': validation_parity,
        'cross_language': cross_status, 'corpus_parity': corpus_parity,
        'n05': f"{report['summary']['n05_pass']}/{report['summary']['n05_graph_vectors']}",
        'stratum': f"{report['summary']['stratum_pass']}/{report['summary']['stratum_vectors']}",
        'validity': f"{report['summary']['validity_pass']}/{report['summary']['validity_cases']}",
        'payload': f"{report['summary']['payload_pass']}/{report['summary']['payload_cases']}",
        'parity': f"{report['summary']['parity_pass']}/{report['summary']['parity_pairs']}",
        'replay': f"{report['summary']['replay_pass']}/{report['summary']['replay_samples']}",
        'keyboard': f"{report['summary']['keyboard_pass']}/{report['summary']['keyboard_contexts']}",
        'keyboard_scratch': f"{report['summary']['keyboard_scratch_pass']}/"
                            f"{report['summary']['keyboard_scratch_cases']}",
        'scratch': f"{report['summary']['scratch_pass']}/{report['summary']['scratch_cases']}",
        'engine_compiled_bytes': compiled,
        'runtime_js_headroom_bytes': budget['runtime_js_headroom_bytes'],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
