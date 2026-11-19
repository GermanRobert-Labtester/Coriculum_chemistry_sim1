#!/usr/bin/env python3
"""N18 graph scoring build gate.

Validates the frozen graph scoring contract, the conventions consumption proof,
the N05 reading vectors verdict-for-verdict, the S3-N18 stratum (reading and
drawing), the validity corpus, the capture payload validation corpus, the
pointer/keyboard payload parity, the verdict replay proof and the inherited
no-extrapolation rule.

The JavaScript twin's parity is proven after assembly by
tools/check_n18_runtime.js and recorded in evidence/N18_CORPUS_RECORD.json by
tools/n18_corpus.py.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file,
)
import graph_scoring_engine as gse  # noqa: E402
from validate_golden_vectors import GOLDEN_VECTORS_PATH, PROTOCOL_PATH  # noqa: E402

CONTRACT_PATH = gse.CONTRACT_PATH
CONVENTIONS_PATH = gse.CONVENTIONS_PATH
PYTHON_ENGINE = 'tools/graph_scoring_engine.py'
JS_ENGINE = 'src/graph-scoring-engine.js'
JS_CAPTURE = 'src/graph-capture.js'
CALIBRATION_CONTRACT = 'data/calibration_contract.json'
KINETICS_CONTRACT = 'data/kinetics_linearization_contract.json'
READING_CONTRACT = 'data/reading_conventions_contract.json'
EXPECTED_VALIDITY_CLASSES = {
    'E_GRAPH_PAYLOAD_MALFORMED', 'E_GRAPH_EMPTY_SUBMISSION', 'E_GRAPH_OUT_OF_AXIS_RANGE',
    'E_GRAPH_WRONG_DIRECTION', 'E_GRAPH_DOUBLE_BACK', 'E_GRAPH_NON_MONOTONIC',
}


def _active_vectors(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [v for v in doc.get('vectors', []) if v.get('status') != 'retired']


def _graph_vectors(golden: dict[str, Any]) -> list[dict[str, Any]]:
    return [v for v in _active_vectors(golden) if v['instance'].get('payload_class') == 'graph']


def _rubric(vector: dict[str, Any]) -> list[dict[str, Any]]:
    """The N05 protocol keeps the rubric inside the instance half."""
    if 'rubric' in vector:
        return vector.get('rubric') or []
    instance = vector.get('instance') or {}
    return instance.get('rubric') or []


def _keyboard_check(contract: dict[str, Any], conventions: dict[str, Any],
                    figures: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Check the declared keyboard increments against their derivation.

    The capture component reads the increments from the engine and the engine
    derives them from the contract, so the derivation is checked against the
    declared examples rather than copied. The fine step must also never be
    coarser than half the declared tolerance band of the assessed axis: the
    keyboard path cannot be structurally penalised relative to the pointer
    path.
    """
    errors: list[str] = []
    increment_examples = {
        row['capture_context']: row
        for row in contract['capture_contract']['keyboard_increments']['keyboard_increment_examples']
    }
    rows: list[dict[str, Any]] = []
    for context_id, context in contract['capture_contract']['capture_contexts'].items():
        keyboard = context.get('keyboard')
        if not keyboard or 'y_axis_step' not in keyboard:
            errors.append(f'capture context {context_id} declares no keyboard increments')
            continue
        try:
            derived = gse.GraphScoringEngine(conventions, contract, figures).keyboard_increments(context_id)
        except gse.GraphError as exc:
            errors.append(f'capture context {context_id} keyboard increments failed: {exc.code}')
            continue
        declared = increment_examples.get(context_id)
        if declared is None:
            errors.append(f'capture context {context_id} has no declared increment example')
            continue
        fields = (('coarse_x', 'coarse_x_value'), ('fine_x', 'fine_x_value'),
                  ('coarse_y', 'coarse_y_value'), ('fine_y', 'fine_y_value'))
        mismatched = [name for name, example_key in fields
                      if abs(derived[name] - float(declared[example_key])) > 1e-12]
        if mismatched:
            errors.append(f'capture context {context_id} keyboard increments disagree with the '
                          f'declared example: {mismatched}')
        for axis in ('x', 'y'):
            band = keyboard.get(f'{axis}_tolerance_band')
            if band is None:
                continue
            fine = derived[f'fine_{axis}']
            if fine > float(band) / 2.0 + 1e-12:
                errors.append(f'capture context {context_id} fine {axis} step {fine} is coarser than '
                              f'half the declared tolerance band {band}')
        rows.append({
            'capture_context': context_id, 'status': 'FAIL' if mismatched else 'PASS',
            'coarse_x': derived['coarse_x'], 'fine_x': derived['fine_x'],
            'coarse_y': derived['coarse_y'], 'fine_y': derived['fine_y'],
        })
    for context_id in sorted(increment_examples):
        if context_id not in contract['capture_contract']['capture_contexts']:
            errors.append(f'the increment example names an unknown capture context: {context_id}')
    return rows, errors


def validate(repo_root: Path = DEST, contract_path: Path | None = None,
             conventions_path: Path | None = None, golden_path: Path | None = None,
             protocol_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    contract_file = contract_path or (repo_root / CONTRACT_PATH)
    conventions_file = conventions_path or (repo_root / CONVENTIONS_PATH)
    golden_file = golden_path or (repo_root / GOLDEN_VECTORS_PATH)
    protocol_file = protocol_path or (repo_root / PROTOCOL_PATH)

    for required in (contract_file, conventions_file, golden_file, protocol_file,
                     repo_root / PYTHON_ENGINE, repo_root / JS_ENGINE,
                     repo_root / JS_CAPTURE,
                     repo_root / CALIBRATION_CONTRACT, repo_root / KINETICS_CONTRACT,
                     repo_root / READING_CONTRACT):
        if not required.exists():
            errors.append(f'Missing graph scoring artifact: {required}')
    if errors:
        return {'status': 'FAIL', 'errors': errors}

    contract = load_json(contract_file)
    conventions = load_json(conventions_file)
    golden = load_json(golden_file)
    protocol = load_json(protocol_file)

    # -- contract structure -------------------------------------------------
    if contract.get('island_id') != 'sim-graph-scoring':
        errors.append('contract island_id must be sim-graph-scoring')
    if contract.get('owner') != 'N18':
        errors.append('contract owner must be N18')
    if contract.get('status') != 'frozen-contract-for-N20-N22-N23-N33':
        errors.append('contract status is not the frozen N18 status')
    stratum = contract.get('graph_vectors', {}).get('stratum')
    if stratum != 'S3-N18':
        errors.append('graph_vectors stratum must be S3-N18')
    if 'S3-N18' not in protocol.get('stratum_registry', {}):
        errors.append('the N05 protocol declares no S3-N18 stratum')
    if protocol['stratum_registry'].get('S3-N18', {}).get('owner') != 'N18':
        errors.append('the N05 protocol assigns S3-N18 to another owner')

    validity_classes = {entry['id'] for entry in contract['validity_rules']['classes']}
    if validity_classes != EXPECTED_VALIDITY_CLASSES:
        errors.append(f'validity class vocabulary drifted: {sorted(validity_classes)}')
    ranks = sorted(int(entry['rank']) for entry in contract['validity_rules']['classes'])
    if ranks != [1, 2, 3, 4, 5, 6]:
        errors.append('validity class ranks must be exactly 1..6')
    for required_key in ('precedence_rule_verbatim', 'domain_class', 'tolerance_class', 'not_assessed_class'):
        if not contract['validity_rules'].get(required_key):
            errors.append(f'validity_rules is missing {required_key}')

    tolerance_classes = {entry['id'] for entry in conventions['tolerances']['quantity_classes']}
    cited_classes: set[str] = set()
    for family in ('reading', 'drawing'):
        for shape_name, shape in contract['criterion_shapes'][family].items():
            if shape.get('tolerance_class'):
                cited_classes.add(shape['tolerance_class'])
    for class_id in sorted(cited_classes):
        if class_id not in tolerance_classes:
            errors.append(f'criterion shape cites an unknown tolerance class: {class_id}')

    figures = gse.load_figures(repo_root=repo_root)
    for context_id, context in contract['capture_contract']['capture_contexts'].items():
        if context['figure_id'] not in figures:
            errors.append(f'capture context {context_id} names an unknown figure')
            continue
        record = figures[context['figure_id']]
        axes = gse.GraphScoringEngine(conventions, contract, figures)._record_axes(record)
        for axis in ('x', 'y'):
            if abs(axes[axis]['min'] - float(context['axes'][axis]['min'])) > 1e-12 or \
               abs(axes[axis]['max'] - float(context['axes'][axis]['max'])) > 1e-12:
                errors.append(f'capture context {context_id} axes disagree with the figure record')
        span = gse.GraphScoringEngine(conventions, contract, figures)._record_span(record)
        if abs(span['x_min'] - float(context['span']['x_min'])) > 1e-12 or \
           abs(span['x_max'] - float(context['span']['x_max'])) > 1e-12:
            errors.append(f'capture context {context_id} span disagrees with the figure record')
        grid = context['grid']
        if float(grid['step']) <= 0 or float(grid['x_max']) < float(grid['x_min']):
            errors.append(f'capture context {context_id} declares an unusable grid')
        # the grid must place a point exactly on the span edge (the inclusive edge rule)
        span_edge = float(context['span']['x_max'])
        reach = (span_edge - float(grid['x_min'])) / float(grid['step'])
        if abs(reach - round(reach)) > 1e-9:
            errors.append(f'capture context {context_id} grid does not land on the inclusive span edge')

    # -- the declared keyboard increments ------------------------------------
    # The capture component reads the increments from the engine, and the
    # engine derives them from the contract. The declared examples are the
    # expected values, so the derivation is checked rather than copied.
    keyboard_rows, keyboard_errors = _keyboard_check(contract, conventions, figures)
    errors.extend(keyboard_errors)

    # -- the inherited rule text --------------------------------------------
    calibration_contract = load_json(repo_root / CALIBRATION_CONTRACT)
    kinetics_contract = load_json(repo_root / KINETICS_CONTRACT)
    no_extrap = calibration_contract['no_extrapolation_rule']['verbatim']
    conventions_rule = conventions['spectrophotometry']['calibration']['no_extrapolation_rule_lv']
    if no_extrap != conventions_rule:
        errors.append('the calibration contract and the conventions island disagree on the no-extrapolation rule')
    if contract['inherited_rules']['no_extrapolation']['verbatim'] != no_extrap:
        errors.append('the N18 contract does not inherit the no-extrapolation rule verbatim')
    if contract['inherited_rules']['span_edge']['edge_rule'] != kinetics_contract['span_rule']['edge_rule']:
        errors.append('the N18 contract does not inherit the N14 span edge rule')
    if contract['inherited_rules']['span_edge']['edge_semantics_lv'] != \
       kinetics_contract['span_rule']['edge_semantics_lv']:
        errors.append('the N18 contract does not inherit the N14 span edge semantics verbatim')

    engine = gse.GraphScoringEngine(conventions, contract, figures)
    engine.conventions_digest = sha256_bytes(canonical_json_bytes(conventions))
    engine.contract_digest = sha256_bytes(canonical_json_bytes(contract))

    # -- the N05 reading vectors, verdict for verdict -------------------------
    n05_rows: list[dict[str, Any]] = []
    for vector in _graph_vectors(golden):
        try:
            verdict = engine.score_reading(
                {'kind': 'n05_payload', 'instance': vector['instance']},
                vector['submission'], _rubric(vector))
        except gse.GraphError as exc:
            n05_rows.append({'vector_id': vector['vector_id'], 'status': 'FAIL',
                             'error_class': exc.code, 'detail': exc.detail})
            errors.append(f"{vector['vector_id']} raised {exc.code}")
            continue
        expected = vector['expected']
        ok = all(verdict[key] == expected[key] for key in (
            'verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
            'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points'))
        n05_rows.append({
            'vector_id': vector['vector_id'], 'status': 'PASS' if ok else 'FAIL',
            'verdict_class': verdict['verdict_class'], 'error_class': verdict['error_class'],
            'tolerance_class': vector['instance']['payload']['target_readout']['tolerance_class'],
            'tolerance_mode': 'absolute',
            'deviation': verdict['assessed_geometry'].get('deviation'),
            'tolerance': verdict['assessed_geometry'].get('tolerance'),
            'cited_entries': [entry['id'] for entry in verdict['cited_entries']],
        })
        if not ok:
            errors.append(f"{vector['vector_id']} graded {verdict['verdict_class']}/"
                          f"{verdict['error_class']}, expected {expected['verdict_class']}/"
                          f"{expected['error_class']}")

    # -- the S3-N18 stratum ---------------------------------------------------
    stratum_rows: list[dict[str, Any]] = []
    tolerance_mode_rows: list[dict[str, Any]] = []
    graph_vectors = contract['graph_vectors']
    for vector in graph_vectors['reading_vectors']:
        verdict = engine.score_reading(
            {'kind': 'figure', 'figure_id': vector['figure_id'],
             'criterion_shape': vector['criterion_shape']},
            vector['submission'], _rubric(vector))
        expected = vector['expected']
        ok = (verdict['verdict_class'] == expected['verdict_class']
              and verdict['error_class'] == expected['error_class']
              and verdict['machine_checked_points'] == expected['awarded_points'])
        geometry = verdict['assessed_geometry']
        stratum_rows.append({
            'vector_id': vector['id'], 'kind': 'reading',
            'status': 'PASS' if ok else 'FAIL',
            'verdict_class': verdict['verdict_class'], 'error_class': verdict['error_class'],
            'criterion_shape': vector['criterion_shape'],
            'deviation': geometry.get('deviation'), 'tolerance': geometry.get('tolerance'),
        })
        tolerance_mode_rows.append({
            'vector_id': vector['id'], 'mode': verdict['criterion']['tolerance_mode'],
            'tolerance_class': verdict['criterion']['tolerance_class'],
            'tolerance': geometry.get('tolerance'), 'deviation': geometry.get('deviation'),
        })
        if not ok:
            errors.append(f"{vector['id']} graded {verdict['verdict_class']}/{verdict['error_class']}, "
                          f"expected {expected['verdict_class']}/{expected['error_class']}")

    parity_rows: list[dict[str, Any]] = []
    for vector in graph_vectors['drawing_vectors']:
        context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
        record = figures[context['figure_id']]
        pointer_payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
        keyboard_payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'keyboard')
        pointer_digest = gse.canonical_digest(pointer_payload)
        keyboard_digest = gse.canonical_digest(keyboard_payload)
        equal = pointer_digest == keyboard_digest
        if not equal:
            errors.append(f"{vector['id']}: pointer and keyboard payloads differ")
        verdict = engine.score_drawing(record, pointer_payload, _rubric(vector))
        keyboard_verdict = engine.score_drawing(record, keyboard_payload, _rubric(vector))
        expected = vector['expected']
        ok = (verdict['verdict_class'] == expected['verdict_class']
              and verdict['error_class'] == expected['error_class']
              and verdict['machine_checked_points'] == expected['awarded_points'])
        if not ok:
            errors.append(f"{vector['id']} graded {verdict['verdict_class']}/{verdict['error_class']}, "
                          f"expected {expected['verdict_class']}/{expected['error_class']}")
        if (keyboard_verdict['verdict_class'] != verdict['verdict_class']
                or keyboard_verdict['error_class'] != verdict['error_class']):
            errors.append(f"{vector['id']}: pointer and keyboard verdicts diverge")
        geometry = verdict['assessed_geometry']
        stratum_rows.append({
            'vector_id': vector['id'], 'kind': 'drawing',
            'status': 'PASS' if ok and equal else 'FAIL',
            'verdict_class': verdict['verdict_class'], 'error_class': verdict['error_class'],
            'criterion_shape': context['criterion_shape'],
            'checks': geometry.get('checks'), 'max_deviation': geometry.get('max_deviation'),
            'excluded_points': len(geometry.get('excluded_points') or []),
        })
        tolerance_mode_rows.append({
            'vector_id': vector['id'],
            'mode': 'significant_figures' if 'kinetics_linearization_line' in context['criterion_shape']
                    or 'sigfigs' in context['criterion_shape'] else 'absolute',
            'tolerance_class': (verdict['criterion'].get('fields', {}).get('slope', {}) or {})
            .get('tolerance_class') or verdict['criterion'].get('tolerance_class'),
            'tolerance': (geometry.get('tolerances') or {}).get('slope')
            or (geometry.get('tolerances') or {}).get('point_acceptance'),
            'deviation': geometry.get('max_deviation'),
        })
        parity_rows.append({
            'vector_id': vector['id'], 'status': 'PASS' if equal else 'FAIL',
            'pointer_digest': pointer_digest, 'keyboard_digest': keyboard_digest,
            'point_count': len(pointer_payload['points']),
            'verdict': verdict['verdict_class'] + '/' + verdict['error_class'],
        })

    modes = {row['mode'] for row in tolerance_mode_rows}
    if not {'absolute', 'significant_figures'} <= modes:
        errors.append(f'both tolerance modes must be exercised: {sorted(modes)}')

    # -- the validity corpus --------------------------------------------------
    validity_rows: list[dict[str, Any]] = []
    for case in graph_vectors['validity_corpus']:
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
        ok = verdict['error_class'] == case['expected_class']
        row = {
            'id': case['id'], 'case': case['case'], 'status': 'PASS' if ok else 'FAIL',
            'expected_class': case['expected_class'], 'actual_class': verdict['error_class'],
            'verdict_class': verdict['verdict_class'],
            'awarded_points': verdict['machine_checked_points'],
            'trace': verdict['validity']['trace'],
        }
        if case.get('also_detected'):
            row['also_detected'] = case['also_detected']
            row['precedence_note_lv'] = case['note_lv']
        validity_rows.append(row)
        if not ok:
            errors.append(f"{case['id']} graded {verdict['error_class']}, expected {case['expected_class']}")

    # -- the capture payload validation corpus --------------------------------
    payload_rows: list[dict[str, Any]] = []
    for case in graph_vectors['payload_validation_corpus']:
        try:
            engine.validate_payload(case['payload'])
            payload_rows.append({'id': case['id'], 'case': case['case'], 'status': 'FAIL',
                                 'expected_class': case['expected_class'], 'actual_class': None})
            errors.append(f"{case['id']}: a malformed payload did not fail by name")
        except gse.GraphError as exc:
            ok = exc.code == case['expected_class']
            payload_rows.append({'id': case['id'], 'case': case['case'],
                                 'status': 'PASS' if ok else 'FAIL',
                                 'expected_class': case['expected_class'], 'actual_class': exc.code,
                                 'check': exc.detail.get('check')})
            if not ok:
                errors.append(f"{case['id']} failed as {exc.code}, expected {case['expected_class']}")

    # -- the verdict replay proof ---------------------------------------------
    replay_rows: list[dict[str, Any]] = []
    samples = [graph_vectors['reading_vectors'][0], graph_vectors['reading_vectors'][1],
               graph_vectors['drawing_vectors'][1], graph_vectors['drawing_vectors'][4]]
    for vector in samples:
        if vector['family'] == 'reading':
            verdict = engine.score_reading(
                {'kind': 'figure', 'figure_id': vector['figure_id'],
                 'criterion_shape': vector['criterion_shape']},
                vector['submission'], _rubric(vector))
        else:
            context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
            record = figures[context['figure_id']]
            payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
            verdict = engine.score_drawing(record, payload, _rubric(vector))
        replayed = engine.replay_verdict(verdict)
        ok = (replayed.get('verdict_class') == verdict['verdict_class']
              and replayed.get('error_class') == verdict['error_class'])
        replay_rows.append({
            'vector_id': vector['id'], 'status': 'PASS' if ok else 'FAIL',
            'original': verdict['verdict_class'] + '/' + verdict['error_class'],
            'replayed': str(replayed.get('verdict_class')) + '/' + str(replayed.get('error_class')),
        })
        if not ok:
            errors.append(f"{vector['id']}: the verdict did not replay from its own record")

    # -- the no-extrapolation inheritance fixtures -----------------------------
    inheritance_rows: list[dict[str, Any]] = []
    edge_vector = next(v for v in graph_vectors['drawing_vectors'] if v['id'] == 'GV-S3-T7-Q11-03')
    beyond_vector = next(v for v in graph_vectors['drawing_vectors'] if v['id'] == 'GV-S3-T7-Q11-02')
    for vector, expectation in ((edge_vector, 'edge point assessed'),
                                (beyond_vector, 'beyond-span geometry not assessed')):
        context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
        record = figures[context['figure_id']]
        payload = engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
        verdict = engine.score_drawing(record, payload, _rubric(vector))
        geometry = verdict['assessed_geometry']
        excluded = geometry.get('excluded_points') or []
        if expectation == 'edge point assessed':
            ok = verdict['error_class'] == 'OUT_OF_TOLERANCE' and geometry['max_deviation'] > 0
        else:
            ok = verdict['error_class'] == 'NONE' and len(excluded) >= 1
        inheritance_rows.append({
            'vector_id': vector['id'], 'expectation': expectation,
            'status': 'PASS' if ok else 'FAIL',
            'verdict': verdict['verdict_class'] + '/' + verdict['error_class'],
            'excluded_points': len(excluded), 'max_deviation': geometry.get('max_deviation'),
            'rule_verbatim': no_extrap,
        })
        if not ok:
            errors.append(f"{vector['id']}: the inherited no-extrapolation rule fixture did not hold")

    # -- the scratch negatives -------------------------------------------------
    scratch_rows: list[dict[str, Any]] = []
    for scratch in graph_vectors.get('scratch', []):
        mutated = copy.deepcopy(conventions)
        for entry in mutated['tolerances']['quantity_classes']:
            if entry['id'] == scratch['mutate']['tolerance_class']:
                entry['absolute']['value'] = scratch['mutate']['absolute_value']
                break
        scratch_engine = gse.GraphScoringEngine(mutated, contract, figures)
        failed_id = None
        failure_class = None
        for vector in _active_vectors(golden):
            if vector['vector_id'] != scratch['fails_vector_id']:
                continue
            try:
                verdict = scratch_engine.score_reading(
                    {'kind': 'n05_payload', 'instance': vector['instance']},
                    vector['submission'], _rubric(vector))
                if verdict['error_class'] != 'NONE' or verdict['verdict_class'] != 'correct':
                    failed_id = vector['vector_id']
                    failure_class = verdict['error_class']
            except gse.GraphError as exc:
                failed_id = vector['vector_id']
                failure_class = exc.code
        for vector in graph_vectors['drawing_vectors']:
            if vector['id'] != scratch['fails_vector_id']:
                continue
            context = contract['capture_contract']['capture_contexts'][vector['capture_context']]
            record = figures[context['figure_id']]
            payload = scratch_engine.capture(vector['capture_context'], vector['target_geometry'], 'pointer')
            try:
                verdict = scratch_engine.score_drawing(record, payload, _rubric(vector))
                if verdict['verdict_class'] != 'correct' or verdict['error_class'] != 'NONE':
                    failed_id = vector['id']
                    failure_class = verdict['error_class']
            except gse.GraphError as exc:
                failed_id = vector['id']
                failure_class = exc.code
        ok = failed_id == scratch['fails_vector_id']
        scratch_rows.append({
            'id': scratch['id'], 'case': scratch['case'], 'status': 'PASS' if ok else 'FAIL',
            'fails_vector_id': failed_id, 'failure_class': failure_class,
            'expected_class': scratch.get('expected_class'),
        })
        if not ok:
            errors.append(f"{scratch['id']}: the scratch mutation did not fail by vector id")

    # -- the keyboard scratch negatives ---------------------------------------
    keyboard_scratch_rows: list[dict[str, Any]] = []
    for scratch in graph_vectors.get('keyboard_scratch', []):
        mutated = copy.deepcopy(contract)
        context = mutated['capture_contract']['capture_contexts'][scratch['mutate']['capture_context']]
        context['keyboard']['y_tolerance_band'] = scratch['mutate']['y_tolerance_band']
        _, scratch_errors = _keyboard_check(mutated, conventions, figures)
        expected_fragment = scratch.get('expected_error_contains', '')
        failed_context = scratch['fails_capture_context']
        matched = [message for message in scratch_errors
                   if failed_context in message and expected_fragment in message]
        ok = bool(matched)
        keyboard_scratch_rows.append({
            'id': scratch['id'], 'case': scratch['case'], 'status': 'PASS' if ok else 'FAIL',
            'fails_capture_context': failed_context,
            'error': matched[0] if matched else None,
            'expected_error_contains': expected_fragment,
        })
        if not ok:
            errors.append(f"{scratch['id']}: the keyboard mutation was not caught by the band rule")

    digests = {
        'contract': sha256_bytes(canonical_json_bytes(contract)),
        'conventions': sha256_bytes(canonical_json_bytes(conventions)),
        'python_engine': sha256_file(repo_root / PYTHON_ENGINE),
        'js_engine': sha256_file(repo_root / JS_ENGINE),
        'js_capture': sha256_file(repo_root / JS_CAPTURE),
        'golden_corpus': sha256_bytes(canonical_json_bytes(golden)),
    }
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'task': 'N18',
        'summary': {
            'n05_graph_vectors': len(n05_rows),
            'n05_pass': sum(1 for row in n05_rows if row['status'] == 'PASS'),
            'stratum_vectors': len(stratum_rows),
            'stratum_pass': sum(1 for row in stratum_rows if row['status'] == 'PASS'),
            'validity_cases': len(validity_rows),
            'validity_pass': sum(1 for row in validity_rows if row['status'] == 'PASS'),
            'payload_cases': len(payload_rows),
            'payload_pass': sum(1 for row in payload_rows if row['status'] == 'PASS'),
            'parity_pairs': len(parity_rows),
            'parity_pass': sum(1 for row in parity_rows if row['status'] == 'PASS'),
            'replay_samples': len(replay_rows),
            'replay_pass': sum(1 for row in replay_rows if row['status'] == 'PASS'),
            'inheritance_fixtures': len(inheritance_rows),
            'inheritance_pass': sum(1 for row in inheritance_rows if row['status'] == 'PASS'),
            'keyboard_contexts': len(keyboard_rows),
            'keyboard_pass': sum(1 for row in keyboard_rows if row['status'] == 'PASS'),
            'keyboard_scratch_cases': len(keyboard_scratch_rows),
            'keyboard_scratch_pass': sum(1 for row in keyboard_scratch_rows if row['status'] == 'PASS'),
            'scratch_cases': len(scratch_rows),
            'scratch_pass': sum(1 for row in scratch_rows if row['status'] == 'PASS'),
            'tolerance_modes': sorted(modes),
        },
        'n05_rows': n05_rows,
        'stratum_rows': stratum_rows,
        'tolerance_mode_rows': tolerance_mode_rows,
        'validity_rows': validity_rows,
        'payload_rows': payload_rows,
        'parity_rows': parity_rows,
        'replay_rows': replay_rows,
        'inheritance_rows': inheritance_rows,
        'scratch_rows': scratch_rows,
        'keyboard_scratch_rows': keyboard_scratch_rows,
        'keyboard_rows': keyboard_rows,
        'inherited_rule_verbatim': no_extrap,
        'span_edge_verbatim': kinetics_contract['span_rule']['edge_semantics_lv'],
        'precedence_rule_verbatim': contract['validity_rules']['precedence_rule_verbatim'],
        'digests': digests,
    }


def format_summary(report: dict[str, Any]) -> str:
    s = report.get('summary', {})
    return (f"{report['status']} graph scoring: {s.get('n05_pass', 0)}/{s.get('n05_graph_vectors', 0)} N05 reading, "
            f"{s.get('stratum_pass', 0)}/{s.get('stratum_vectors', 0)} S3-N18, "
            f"{s.get('validity_pass', 0)}/{s.get('validity_cases', 0)} validity, "
            f"{s.get('payload_pass', 0)}/{s.get('payload_cases', 0)} payload, "
            f"{s.get('parity_pass', 0)}/{s.get('parity_pairs', 0)} parity, "
            f"{s.get('replay_pass', 0)}/{s.get('replay_samples', 0)} replay, "
            f"{s.get('keyboard_pass', 0)}/{s.get('keyboard_contexts', 0)} keyboard, "
            f"{s.get('keyboard_scratch_pass', 0)}/{s.get('keyboard_scratch_cases', 0)} keyboard scratch, "
            f"{s.get('scratch_pass', 0)}/{s.get('scratch_cases', 0)} scratch, "
            f"{len(report.get('errors', []))} errors")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--report', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    root = Path(args.repo_root)
    report = validate(repo_root=root)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) if args.json
          else format_summary(report))
    if report['status'] != 'PASS':
        for err in report['errors'][:20]:
            print(f'  - {err}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
