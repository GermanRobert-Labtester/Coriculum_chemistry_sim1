#!/usr/bin/env python3
"""N23 build gate: the grading-policy island, the classification totality, the
score matrix and the no-local-knowledge contract test.

This gate is the build's N23 checkpoint (GRADING_FORMAT §11, gate 19). It
refuses the build when:

- ``data/grading_policy.json`` is not the frozen shape: wrong schema/island id,
  a missing verdict rule, a slot state outside the declared vocabulary, missing
  honesty/analytics/binding rules, self-test fixtures that do not add up under
  the island's own declared rules, or a missing N23-C01 / N22-C06-resolution
  conflict record;
- ``data/feedback_classification.json`` leaves any frozen vocabulary value
  unmapped (N17 taxonomy classes and their signatures, the fallback signature,
  the conservation signature MC-1C-01, the N19 signature registry, the N18 error
  class vocabulary, the N23 slot-state vocabulary, every bank
  ``misconception_signatures`` value), or a remediation concept/chain/term id
  does not resolve, or a priority is not an int. The classification island is
  authored in parallel; while it is absent the sweep is PENDING, never FAIL;
- ``tools/fixtures/n23_score_matrix.json`` binds an instance whose rubric sum
  differs from the authoritative slot points (the loud N23-C01 guard, named by
  slot and instance), or its hand-computed expectations do not add up;
- ``src/grading.ts`` (and ``src/feedback.ts`` when it exists) carries a numeric
  literal that could be a tolerance, a unit factor or a mass — outside the
  declared SHA-256 block the only allowed numeric literals are -1, 0 and 1 — or
  reaches an engine through a global instead of the frozen context.

Usage:
    python3 tools/validate_n23_grading.py --report evidence/N23_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

ROOT = DEST
OWNER = 'N23'
POLICY_PATH = 'data/grading_policy.json'
CLASSIFICATION_PATH = 'data/feedback_classification.json'
SCORE_MATRIX_PATH = 'tools/fixtures/n23_score_matrix.json'
EXAM_POLICY_PATH = 'data/exam_policy.json'
RESPONSE_TYPES_PATH = 'data/response_types.json'
TAXONOMY_PATH = 'data/engine_taxonomy.json'
METHOD_PATH = 'data/method_engine_contract.json'
GRAPH_PATH = 'data/graph_scoring_contract.json'
GOLDEN_PROTOCOL_PATH = 'data/golden_vector_protocol.json'
TERMS_PATH = 'data/terms.json'
ANCHOR_PATH = 'data/anchor_registry.json'
SUMMARIES_PATH = 'data/concept_summaries.json'
CHAINS_PATH = 'data/chains.json'
BANK_DIR = 'data/bank'
GRADING_TS = 'src/grading.ts'
FEEDBACK_TS = 'src/feedback.ts'

ISLAND_ID = 'sim-grading-policy'
CLASSIFICATION_ID = 'sim-feedback-classification'
STATES = ['graded', 'incomplete', 'invalid', 'unattempted', 'manual_pending']
STATUSES = ['awarded', 'denied', 'pending']
SCORE_FORMS = ['FX-N23-FULL', 'FX-N23-PARTIAL', 'FX-N23-ZERO', 'FX-N23-MIXED']
SELF_TEST_IDS = ['SF-N23-FULL', 'SF-N23-PARTIAL', 'SF-N23-MALFORMED']
EVENT_TYPES = ['session-completed', 'task-answered', 'remediation-state']
MODULE_ERRORS = [
    'E_GRADING_POLICY_INVALID', 'E_GRADING_SCHEMA', 'E_GRADING_STATE',
    'E_GRADING_BINDING_UNKNOWN', 'E_GRADING_BINDING_POINTS', 'E_GRADING_UNKNOWN_VERDICT',
    'E_GRADING_CONTEXT', 'E_FEEDBACK_UNMAPPED', 'E_FEEDBACK_REMEDIATION_UNRESOLVED',
]
ENGINE_GLOBALS = ['SimEngines', 'SimGraphScoring', 'SimMethodEngine',
                  'SimInputsRegistry', 'SimInputsIntegration']
CONTEXT_KEYS = ['quantity', 'method', 'graph', 'inputsRegistry', 'inputsIntegration']
ALLOWED_NUMBERS = {'-1', '0', '1'}


# --------------------------------------------------------------------- helpers

def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _bank(repo_root: Path) -> dict[str, dict[str, Any]]:
    bank: dict[str, dict[str, Any]] = {}
    for path in sorted((repo_root / BANK_DIR).glob('*.json')):
        document = load_json(path)
        for question in document.get('questions', []):
            bank[question['question_id']] = question
    return bank


def _rubric_split(instance: dict[str, Any]) -> tuple[float, float]:
    """The frozen engines' split: auto/mixed minus the external bindings."""
    auto = 0.0
    pending = 0.0
    for item in instance.get('rubric', []):
        grading = item.get('grading')
        binding = item.get('engine_binding')
        machine = grading in ('auto', 'mixed') and binding not in ('self-assessed', 'human-review')
        if machine:
            auto += float(item.get('points', 0))
        else:
            pending += float(item.get('points', 0))
    return auto, pending


def _number(value: float) -> float:
    return float(value)


def _strip_comments(text: str) -> str:
    """Remove comments while preserving line breaks; strings are respected."""
    out: list[str] = []
    i = 0
    length = len(text)
    in_string: str | None = None
    while i < length:
        char = text[i]
        if in_string is not None:
            out.append(char)
            if char == '\\' and i + 1 < length:
                out.append(text[i + 1])
                i += 2
                continue
            if char == in_string:
                in_string = None
            i += 1
            continue
        if char in ("'", '"', '`'):
            in_string = char
            out.append(char)
            i += 1
            continue
        if char == '/' and i + 1 < length and text[i + 1] == '/':
            while i < length and text[i] != '\n':
                i += 1
            continue
        if char == '/' and i + 1 < length and text[i + 1] == '*':
            i += 2
            while i + 1 < length and not (text[i] == '*' and text[i + 1] == '/'):
                if text[i] == '\n':
                    out.append('\n')
                i += 1
            i += 2
            continue
        out.append(char)
        i += 1
    return ''.join(out)


def _line_of(text: str, index: int) -> int:
    return text.count('\n', 0, index) + 1


# ------------------------------------------------------------------ 1. policy

def apply_declared_rules(policy: dict[str, Any], fixture: dict[str, Any]) -> tuple[float, float]:
    """Apply the island's declared slot-state and status rules in pure arithmetic."""
    state = fixture.get('slot_state', 'graded')
    if state not in STATES:
        raise ValueError(f'unknown slot_state {state!r}')
    auto = 0.0
    pending = 0.0
    for row in fixture.get('criteria', []):
        status = row.get('status')
        if status not in STATUSES:
            raise ValueError(f'unknown criterion status {status!r} for {row.get("criterion_id")}')
        if state == 'manual_pending':
            effective = 'pending'
        elif state in ('invalid', 'incomplete', 'unattempted'):
            effective = 'denied'
        else:
            effective = status
        points = float(row.get('points', 0))
        if effective == 'awarded':
            auto += points
        elif effective == 'pending':
            pending += points
        elif points and effective != 'denied':
            raise ValueError(f'status {effective!r} is not declared')
    return auto, pending


def check_policy(repo_root: Path, island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    detail: dict[str, Any] = {'source': POLICY_PATH, 'checks': {}}
    checks = detail['checks']

    def need(condition: bool, message: str, name: str) -> bool:
        checks[name] = bool(condition)
        if not condition:
            errors.append(message)
        return bool(condition)

    need(island.get('schema_version') == 1, 'grading_policy: schema_version must be 1', 'schema_version')
    need(island.get('island_id') == ISLAND_ID, f'grading_policy: island_id must be {ISLAND_ID}', 'island_id')
    need(island.get('owner') == OWNER, 'grading_policy: owner must be N23', 'owner')
    need(isinstance(island.get('epistemic_note'), str) and 'PROPOSED' in island.get('epistemic_note', ''),
         'grading_policy: the epistemic note must label the policy PROPOSED', 'proposed_label')

    rubric = island.get('rubric_policy') if isinstance(island.get('rubric_policy'), dict) else {}
    verdict_rules = rubric.get('verdict_rules') if isinstance(rubric.get('verdict_rules'), dict) else {}

    protocol = load_json(repo_root / GOLDEN_PROTOCOL_PATH)
    graph = load_json(repo_root / GRAPH_PATH)
    frozen_verdicts = set(protocol.get('verdict_classes', [])) | set(
        graph.get('verdict_record', {}).get('verdict_classes', []))
    frozen_verdicts |= {'not_assessed'}
    detail['frozen_verdict_classes'] = sorted(frozen_verdicts)
    need(set(verdict_rules) == frozen_verdicts,
         'grading_policy: verdict_rules must cover exactly ' + ','.join(sorted(frozen_verdicts))
         + ' (got ' + ','.join(sorted(verdict_rules)) + ')', 'verdict_totality')
    for name, rule in verdict_rules.items():
        need(isinstance(rule, dict) and isinstance(rule.get('count'), str) and rule.get('count'),
             f'grading_policy: verdict rule {name} needs a non-empty count', f'verdict_count:{name}')
    need(isinstance(rubric.get('unknown_verdict_rule'), str) and rubric.get('unknown_verdict_rule'),
         'grading_policy: unknown_verdict_rule is missing', 'unknown_verdict_rule')

    status_rules = rubric.get('criterion_status_rules') if isinstance(rubric.get('criterion_status_rules'), dict) else {}
    need(set(status_rules) == set(STATUSES),
         'grading_policy: criterion_status_rules must be exactly awarded,denied,pending', 'criterion_statuses')
    state_rules = rubric.get('slot_state_rules') if isinstance(rubric.get('slot_state_rules'), dict) else {}
    need(set(state_rules) == set(STATES),
         'grading_policy: slot_state_rules must declare exactly ' + ','.join(STATES), 'slot_states')
    for state in STATES:
        need(isinstance(state_rules.get(state), str) and state_rules.get(state),
             f'grading_policy: slot_state_rules.{state} must be a non-empty sentence', f'slot_state:{state}')

    routing = rubric.get('pre_grade_routing') if isinstance(rubric.get('pre_grade_routing'), dict) else {}
    need(routing.get('manual_pending_types') == ['Q03', 'Q05'],
         'grading_policy: manual_pending_types must be exactly Q03,Q05', 'manual_pending_types')
    need(isinstance(routing.get('unattempted_error_class'), str) and routing.get('unattempted_error_class'),
         'grading_policy: unattempted_error_class is missing', 'unattempted_error_class')
    need(isinstance(routing.get('manual_pending_error_class'), str) and routing.get('manual_pending_error_class'),
         'grading_policy: manual_pending_error_class is missing', 'manual_pending_error_class')
    response_types = load_json(repo_root / RESPONSE_TYPES_PATH)
    for type_id in routing.get('manual_pending_types', []):
        contract = response_types.get('types', {}).get(type_id, {})
        binding = contract.get('grading_binding', {})
        need(binding.get('class') == 'pending',
             f'grading_policy: {type_id} is declared manual but its grading_binding.class is not pending',
             f'manual_binding:{type_id}')

    need(isinstance(rubric.get('points_rule_verbatim_lv'), str) and rubric.get('points_rule_verbatim_lv'),
         'grading_policy: points_rule_verbatim_lv is missing', 'points_rule')
    need('PROPOSED' in str(rubric.get('points_rule_verbatim_lv', '')),
         'grading_policy: points_rule_verbatim_lv must label the policy PROPOSED', 'points_rule_proposed')
    need(isinstance(rubric.get('engine_bindings'), list) and rubric.get('engine_bindings'),
         'grading_policy: engine_bindings is missing', 'engine_bindings')

    honesty = island.get('honesty_accounting') if isinstance(island.get('honesty_accounting'), dict) else {}
    exam_policy = load_json(repo_root / EXAM_POLICY_PATH)
    form_max = honesty.get('form_max_points')
    need(form_max == exam_policy.get('exam', {}).get('total_points'),
         'grading_policy: form_max_points must equal exam_policy.exam.total_points', 'form_max_points')
    need(honesty.get('unblended') is True, 'grading_policy: honesty_accounting.unblended must be true', 'unblended')
    terms = load_json(repo_root / TERMS_PATH)
    term_keys = {entry.get('key') for entry in terms.get('terms', [])}
    copy_keys = honesty.get('display_copy_keys') if isinstance(honesty.get('display_copy_keys'), list) else []
    missing_copy = [key for key in copy_keys if key not in term_keys]
    need(bool(copy_keys) and not missing_copy,
         'grading_policy: display_copy_keys do not resolve in #sim-terms: ' + ','.join(missing_copy),
         'display_copy_keys')
    detail['display_copy_keys'] = len(copy_keys)

    binding_rule = island.get('binding_rule') if isinstance(island.get('binding_rule'), dict) else {}
    need(binding_rule.get('slot_points_authoritative') is True,
         'grading_policy: binding_rule.slot_points_authoritative must be true', 'slot_points_authoritative')
    need(binding_rule.get('conflict_ref') == 'N23-C01',
         'grading_policy: binding_rule.conflict_ref must be N23-C01', 'conflict_ref')
    need('E_GRADING_BINDING_POINTS' in str(binding_rule.get('mismatch_rule', '')),
         'grading_policy: binding_rule.mismatch_rule must name E_GRADING_BINDING_POINTS', 'mismatch_rule')

    analytics = island.get('analytics_contract') if isinstance(island.get('analytics_contract'), dict) else {}
    need(analytics.get('event_types') == EVENT_TYPES,
         'grading_policy: analytics event_types must be ' + ','.join(EVENT_TYPES), 'event_types')
    need(isinstance(analytics.get('no_answer_text_rule'), str) and analytics.get('no_answer_text_rule'),
         'grading_policy: analytics no_answer_text_rule is missing', 'no_answer_text_rule')

    fixtures = island.get('self_test_fixtures') if isinstance(island.get('self_test_fixtures'), list) else []
    fixture_ids = [fixture.get('id') for fixture in fixtures if isinstance(fixture, dict)]
    need(fixture_ids == SELF_TEST_IDS,
         'grading_policy: self_test_fixtures must be SF-N23-FULL,SF-N23-PARTIAL,SF-N23-MALFORMED', 'self_test_ids')
    fixture_rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        if not isinstance(fixture, dict):
            continue
        name = fixture.get('id')
        criteria = fixture.get('criteria') if isinstance(fixture.get('criteria'), list) else []
        total = sum(float(row.get('points', 0)) for row in criteria)
        expected = fixture.get('expected') if isinstance(fixture.get('expected'), dict) else {}
        need(total == float(fixture.get('slot_points', -1)),
             f'grading_policy: {name} criterion points {total} != slot_points {fixture.get("slot_points")}',
             f'{name}:slot_points')
        try:
            auto, pending = apply_declared_rules(island, fixture)
        except ValueError as error:
            errors.append(f'grading_policy: {name} cannot be applied: {error}')
            continue
        need(_number(auto) == _number(expected.get('auto', -1))
             and _number(pending) == _number(expected.get('pending_external', -1)),
             f'grading_policy: {name} expected totals do not match the declared rules '
             f'(got {auto}/{pending})', f'{name}:expected')
        fixture_rows.append({'id': name, 'slot_points': fixture.get('slot_points'),
                             'auto': auto, 'pending_external': pending})
    detail['self_test_fixtures'] = fixture_rows

    conflicts = island.get('conflicts') if isinstance(island.get('conflicts'), list) else []
    conflict_ids = {conflict.get('id') for conflict in conflicts if isinstance(conflict, dict)}
    need('N23-C01' in conflict_ids, 'grading_policy: conflicts must record N23-C01', 'conflict:N23-C01')
    need('N22-C06-resolution' in conflict_ids,
         'grading_policy: conflicts must record N22-C06-resolution', 'conflict:N22-C06-resolution')
    detail['conflicts'] = sorted(conflict_ids)

    canonical = canonical_json_bytes(island)
    detail['digest'] = sha256_bytes(canonical)
    detail['bytes'] = len(canonical)
    return detail


# ----------------------------------------------------------- 2. classification

def check_classification(
    repo_root: Path,
    policy: dict[str, Any],
    bank: dict[str, dict[str, Any]],
    errors: list[str],
    pending: list[str],
) -> dict[str, Any]:
    path = repo_root / CLASSIFICATION_PATH
    if not path.exists():
        pending.append('classification: data/feedback_classification.json is not authored yet '
                       '(island sim-feedback-classification missing)')
        return {'status': 'PENDING', 'reason': 'data/feedback_classification.json is absent'}
    island = load_json(path)
    detail: dict[str, Any] = {'status': 'CHECKED', 'source': CLASSIFICATION_PATH, 'checks': {}}
    checks = detail['checks']

    def need(condition: bool, message: str, name: str) -> bool:
        checks[name] = bool(condition)
        if not condition:
            errors.append(message)
        return bool(condition)

    need(island.get('schema_version') == 1, 'classification: schema_version must be 1', 'schema_version')
    need(island.get('island_id') == CLASSIFICATION_ID,
         f'classification: island_id must be {CLASSIFICATION_ID}', 'island_id')
    need(island.get('owner') == OWNER, 'classification: owner must be N23', 'owner')
    mapping = island.get('mapping') if isinstance(island.get('mapping'), list) else []
    need(bool(mapping), 'classification: mapping is empty', 'mapping_present')

    taxonomy = load_json(repo_root / TAXONOMY_PATH)
    method = load_json(repo_root / METHOD_PATH)
    graph = load_json(repo_root / GRAPH_PATH)
    terms = load_json(repo_root / TERMS_PATH)

    classes = taxonomy.get('error_taxonomy', {}).get('classes', [])
    fallback = taxonomy.get('error_taxonomy', {}).get('fallback', {})
    conservation = taxonomy.get('conservation', {})
    required_signatures: set[str] = set()
    for entry in classes:
        if entry.get('signature'):
            required_signatures.add(entry['signature'])
    if fallback.get('signature'):
        required_signatures.add(fallback['signature'])
    if conservation.get('imbalance_signature'):
        required_signatures.add(conservation['imbalance_signature'])
    for entry in method.get('signature_registry', []):
        if entry.get('signature'):
            required_signatures.add(entry['signature'])
    for question in bank.values():
        for signature in question.get('misconception_signatures', []):
            required_signatures.add(signature)

    required_error_classes: set[str] = {'NONE'}
    for entry in classes:
        required_error_classes.update(entry.get('n05_error_classes', []))
    required_error_classes.update(graph.get('verdict_record', {}).get('error_class_vocabulary', []))
    declared_states = set((policy.get('rubric_policy') or {}).get('slot_state_rules') or {})
    required_states = declared_states if declared_states else set(STATES)

    term_keys = {entry.get('key') for entry in terms.get('terms', [])}
    anchor = load_json(repo_root / ANCHOR_PATH)
    summaries = load_json(repo_root / SUMMARIES_PATH)
    chains = load_json(repo_root / CHAINS_PATH)
    anchor_ids = {entry.get('concept_id') for entry in anchor.get('concepts', [])}
    summary_ids = {entry.get('id') for entry in summaries.get('concepts', [])}
    concept_ids = anchor_ids | summary_ids
    chain_ids = {entry.get('id') for entry in chains.get('chains', [])}

    mapped_signatures: set[str] = set()
    mapped_errors: set[str] = set()
    mapped_states: set[str] = set()
    durations: dict[str, int] = {}
    priorities_ok = True
    feedback_ok = True
    concepts_ok = True
    chains_ok = True
    names_ok = True
    unresolved_concepts: set[str] = set()
    unresolved_chains: set[str] = set()
    unresolved_terms: set[str] = set()

    for index, row in enumerate(mapping):
        if not isinstance(row, dict):
            errors.append(f'classification: mapping[{index}] is not an object')
            continue
        kind = row.get('match_kind')
        value = row.get('match_value')
        label = f'mapping[{index}] {kind}:{value}'
        if kind not in ('signature', 'error_class', 'slot_state'):
            errors.append(f'classification: {label} has an unknown match_kind')
            continue
        if not isinstance(value, str) or not value:
            errors.append(f'classification: {label} has no match_value')
            continue
        if kind == 'signature':
            mapped_signatures.add(value)
        elif kind == 'error_class':
            mapped_errors.add(value)
        else:
            mapped_states.add(value)
        priority = row.get('priority')
        if not isinstance(priority, int) or isinstance(priority, bool):
            priorities_ok = False
            errors.append(f'classification: {label} priority is not an int')
        key = row.get('feedback_key')
        if not isinstance(key, str) or key not in term_keys:
            feedback_ok = False
            unresolved_terms.add(str(key))
        misconception = row.get('misconception_name')
        if not isinstance(misconception, dict) or not isinstance(misconception.get('island'), str):
            names_ok = False
            errors.append(f'classification: {label} misconception_name is not an object with an island')
        remediation = row.get('remediation') if isinstance(row.get('remediation'), dict) else {}
        for concept in remediation.get('concept_ids', []):
            if concept not in concept_ids:
                concepts_ok = False
                unresolved_concepts.add(str(concept))
        for chain in remediation.get('chain_ids', []):
            if chain not in chain_ids:
                chains_ok = False
                unresolved_chains.add(str(chain))
        note = row.get('specificity_note_lv')
        if not isinstance(note, str) or not note:
            errors.append(f'classification: {label} specificity_note_lv is empty')

    missing_signatures = sorted(required_signatures - mapped_signatures)
    missing_errors = sorted(required_error_classes - mapped_errors)
    missing_states = sorted(required_states - mapped_states)
    need(not missing_signatures,
         'classification: unmapped misconception signatures: ' + ','.join(missing_signatures[:20]),
         'signature_totality')
    need(not missing_errors,
         'classification: unmapped error classes: ' + ','.join(missing_errors), 'error_class_totality')
    need(not missing_states,
         'classification: unmapped slot states: ' + ','.join(missing_states), 'slot_state_totality')
    need(priorities_ok, 'classification: every priority must be an int', 'priority_int')
    need(feedback_ok, 'classification: unresolved feedback keys: ' + ','.join(sorted(unresolved_terms)),
         'feedback_keys')
    need(names_ok, 'classification: misconception_name entries are malformed', 'misconception_names')
    need(concepts_ok, 'classification: unresolved remediation concept ids: '
         + ','.join(sorted(unresolved_concepts)), 'remediation_concepts')
    need(chains_ok, 'classification: unresolved remediation chain ids: '
         + ','.join(sorted(unresolved_chains)), 'remediation_chains')

    ordering = island.get('ordering_rule') if isinstance(island.get('ordering_rule'), dict) else {}
    need(ordering.get('rule') == 'priority-ascending-then-match_value',
         'classification: ordering_rule.rule must be priority-ascending-then-match_value', 'ordering_rule')
    unmapped_rule = island.get('unmapped_rule')
    unmapped_ok = (isinstance(unmapped_rule, str) and bool(unmapped_rule)) or (
        isinstance(unmapped_rule, dict) and isinstance(unmapped_rule.get('rule_lv'), str)
        and bool(unmapped_rule.get('rule_lv')))
    need(unmapped_ok, 'classification: unmapped_rule is missing', 'unmapped_rule')

    canonical = canonical_json_bytes(island)
    detail['digest'] = sha256_bytes(canonical)
    detail['mapping_rows'] = len(mapping)
    detail['required'] = {
        'signatures': len(required_signatures),
        'error_classes': len(required_error_classes),
        'slot_states': len(required_states),
    }
    detail['mapped'] = {
        'signatures': len(mapped_signatures & required_signatures),
        'error_classes': len(mapped_errors & required_error_classes),
        'slot_states': len(mapped_states & required_states),
    }
    return detail


# ------------------------------------------------------------- 3. score matrix

def check_score_matrix(
    repo_root: Path,
    exam_policy: dict[str, Any],
    bank: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    path = repo_root / SCORE_MATRIX_PATH
    if not path.exists():
        errors.append(f'score matrix: {SCORE_MATRIX_PATH} does not exist')
        return {'status': 'FAIL'}
    fixture = load_json(path)
    detail: dict[str, Any] = {'source': SCORE_MATRIX_PATH, 'forms': {}}
    if fixture.get('schema_version') != 1:
        errors.append('score matrix: schema_version must be 1')
    if fixture.get('owner') != OWNER:
        errors.append('score matrix: owner must be N23')
    slots = {slot['slot_id']: float(slot['points']) for slot in exam_policy.get('slots', [])}
    slot_order = [slot['slot_id'] for slot in exam_policy.get('slots', [])]
    detail['slot_count'] = len(slots)

    forms = fixture.get('forms') if isinstance(fixture.get('forms'), list) else []
    form_ids = [form.get('form_id') for form in forms if isinstance(form, dict)]
    if form_ids != SCORE_FORMS:
        errors.append('score matrix: forms must be exactly ' + ','.join(SCORE_FORMS)
                      + ' (got ' + ','.join(str(name) for name in form_ids) + ')')

    for form in forms:
        if not isinstance(form, dict):
            continue
        name = form.get('form_id')
        form_detail: dict[str, Any] = {'slot_points': 0.0, 'bindings': 0, 'rubric_sum_checked': 0}
        bindings = form.get('bindings') if isinstance(form.get('bindings'), list) else []
        binding_slots = [row.get('slot_id') for row in bindings if isinstance(row, dict)]
        if binding_slots != slot_order:
            errors.append(f'score matrix {name}: bindings must cover the 21 slots in form order')
        if len(bindings) != len(slots):
            errors.append(f'score matrix {name}: {len(bindings)} bindings for {len(slots)} slots')
        answers = form.get('answers') if isinstance(form.get('answers'), dict) else {}
        expected = form.get('expected') if isinstance(form.get('expected'), dict) else {}
        expected_slots = expected.get('slots') if isinstance(expected.get('slots'), dict) else {}
        expected_totals = expected.get('totals') if isinstance(expected.get('totals'), dict) else {}

        for row in bindings:
            if not isinstance(row, dict):
                errors.append(f'score matrix {name}: a binding is not an object')
                continue
            slot_id = row.get('slot_id')
            type_id = row.get('type_id')
            instance_id = row.get('instance_id')
            form_detail['bindings'] += 1
            if slot_id not in slots:
                errors.append(f'score matrix {name}: binding names unknown slot {slot_id}')
                continue
            instance = bank.get(instance_id)
            if instance is None:
                errors.append(f'score matrix {name}: slot {slot_id} binds unknown instance {instance_id}')
                continue
            if instance.get('type_id') != type_id:
                errors.append(f'score matrix {name}: slot {slot_id} type {type_id} != instance '
                              f'{instance_id} type {instance.get("type_id")}')
            rubric_sum = sum(float(item.get('points', 0)) for item in instance.get('rubric', []))
            form_detail['slot_points'] += slots[slot_id]
            form_detail['rubric_sum_checked'] += 1
            if abs(rubric_sum - slots[slot_id]) > 1e-9:
                errors.append(
                    f'score matrix {name}: E_GRADING_BINDING_POINTS slot {slot_id} ({slots[slot_id]}) '
                    f'!= instance {instance_id} rubric sum ({rubric_sum}) [N23-C01]')
            auto_max, pending_max = _rubric_split(instance)
            want = expected_slots.get(slot_id) or {}
            if abs(float(want.get('auto_max', -1)) - auto_max) > 1e-9:
                errors.append(f'score matrix {name}: slot {slot_id} expected auto_max '
                              f'{want.get("auto_max")} != rubric split {auto_max}')
            if abs(float(want.get('pending_max', -1)) - pending_max) > 1e-9:
                errors.append(f'score matrix {name}: slot {slot_id} expected pending_max '
                              f'{want.get("pending_max")} != rubric split {pending_max}')

        for slot_id, answer in answers.items():
            if slot_id not in slots:
                errors.append(f'score matrix {name}: answer for unknown slot {slot_id}')
                continue
            if not isinstance(answer, dict) or not ('capture' in answer or 'stored_payload' in answer):
                errors.append(f'score matrix {name}: answer {slot_id} has neither capture nor stored_payload')

        if set(expected_slots) != set(slots):
            errors.append(f'score matrix {name}: expected.slots must cover exactly the 21 slots')

        sums = {
            'auto_points': 0.0, 'auto_max_points': 0.0,
            'pending_external_points': 0.0, 'pending_max_points': 0.0,
            'denied_points': 0.0, 'zeroed_points': 0.0,
        }
        counts = {state: 0 for state in STATES}
        for slot_id in slots:
            row = expected_slots.get(slot_id)
            if not isinstance(row, dict):
                continue
            state = row.get('state')
            if state not in STATES:
                errors.append(f'score matrix {name}: slot {slot_id} state {state!r} is not declared')
                continue
            counts[state] += 1
            sums['auto_points'] += float(row.get('auto', 0))
            sums['auto_max_points'] += float(row.get('auto_max', 0))
            sums['pending_external_points'] += float(row.get('pending', 0))
            sums['pending_max_points'] += float(row.get('pending_max', 0))
            sums['denied_points'] += float(row.get('denied', 0))
            sums['zeroed_points'] += float(row.get('zeroed', 0))
            auto = float(row.get('auto', 0))
            auto_max = float(row.get('auto_max', 0))
            pending = float(row.get('pending', 0))
            pending_max = float(row.get('pending_max', 0))
            if auto > auto_max + 1e-9:
                errors.append(f'score matrix {name}: slot {slot_id} auto {auto} > auto_max {auto_max}')
            if pending > pending_max + 1e-9:
                errors.append(f'score matrix {name}: slot {slot_id} pending {pending} > '
                              f'pending_max {pending_max}')
            if auto_max + pending_max > slots[slot_id] + 1e-9:
                errors.append(f'score matrix {name}: slot {slot_id} maxima exceed slot points')

        for key, value in sums.items():
            if abs(float(expected_totals.get(key, -1)) - value) > 1e-9:
                errors.append(f'score matrix {name}: totals.{key} declared '
                              f'{expected_totals.get(key)} != recomputed {value}')
        for state, count in counts.items():
            key = f'slots_{state}'
            if expected_totals.get(key) != count:
                errors.append(f'score matrix {name}: totals.{key} declared '
                              f'{expected_totals.get(key)} != {count}')
        accounted = (sums['auto_points'] + sums['pending_external_points']
                     + sums['denied_points'] + sums['zeroed_points'])
        form_max = float(expected_totals.get('form_max_points', -1))
        if abs(accounted - form_max) > 1e-9:
            errors.append(f'score matrix {name}: awarded+pending+denied+zeroed {accounted} '
                          f'!= form_max_points {form_max}')
        if abs(sums['auto_max_points'] + sums['pending_max_points'] - form_max) > 1e-9:
            errors.append(f'score matrix {name}: auto_max + pending_max != form_max_points')
        form_detail['totals'] = {key: float(expected_totals.get(key, 0)) for key in
                                 ('auto_points', 'pending_external_points', 'denied_points',
                                  'zeroed_points', 'form_max_points')}
        form_detail['states'] = counts
        detail['forms'][name] = form_detail

    mixed = next((form for form in forms if form.get('form_id') == 'FX-N23-MIXED'), None)
    if mixed:
        slots_expected = mixed.get('expected', {}).get('slots', {})
        kinds = {row.get('state') for row in slots_expected.values() if isinstance(row, dict)}
        if not {'invalid', 'incomplete', 'unattempted', 'manual_pending'} <= kinds:
            errors.append('score matrix FX-N23-MIXED must contain invalid, incomplete, '
                          'unattempted and manual_pending slots')
        answers = mixed.get('answers', {})
        numeric = answers.get('S4-1', {}).get('capture', {}).get('fields', {}).get('m', '')
        if not isinstance(numeric, str) or not re.search(r'\d+\.\d{3},\d+$', numeric):
            errors.append('score matrix FX-N23-MIXED: the mixed-separator numeric twin '
                          '(both . and ,) is missing from S4-1')
        else:
            detail['mixed_separator'] = numeric
    detail['status'] = 'CHECKED'
    return detail


# --------------------------------------------------------------- 4. source scan

def _mask_digest_region(text: str) -> tuple[str, str]:
    """Blank out a declared digest implementation before the numeric scan.

    grading.ts declares its block with N23-DIGEST-BEGIN/END markers; a sibling
    module that legitimately carries its own SHA-256 (feedback.ts) is recognised
    by a comment naming SHA-256 plus the `sha256` function that follows it.
    Only the hash arithmetic is exempt: the returned `mode` says which rule was
    used so the report can show it. Positions are kept by blanking with spaces
    and preserving newlines, so line numbers stay true.
    """
    def blank(start: int, end: int) -> str:
        chunk = text[start:end]
        return text[:start] + ''.join('\n' if ch == '\n' else ' ' for ch in chunk) + text[end:]

    begin = text.find('N23-DIGEST-BEGIN')
    end_marker = text.find('N23-DIGEST-END')
    if begin >= 0 and end_marker > begin:
        start = text.rfind('/*', 0, begin)
        if start < 0:
            start = begin
        stop = text.find('*/', end_marker)
        stop = len(text) if stop < 0 else stop + 2
        return blank(start, stop), 'n23-markers'
    for match in re.finditer(r'/\*[\s\S]*?\*/', text):
        block = match.group(0)
        if 'SHA-256' not in block and 'SHA256' not in block:
            continue
        start = match.start()
        function_at = text.find('function sha256', match.end())
        if function_at < 0:
            return blank(start, match.end()), 'sha256-comment'
        brace = text.find('{', function_at)
        if brace < 0:
            return blank(start, match.end()), 'sha256-comment'
        depth = 0
        stop = brace
        for index in range(brace, len(text)):
            char = text[index]
            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    stop = index + 1
                    break
        return blank(start, stop), 'sha256-comment+function'
    return text, 'none'


def _scan_source(path: Path, errors: list[str], pending: list[str], check_feedback: bool) -> dict[str, Any]:
    """The no-local-knowledge contract test.

    grading.ts is held to the strict rule the module documents: outside its
    declared SHA-256 block the only numeric literals are -1, 0 and 1. A sibling
    feedback.ts (authored in parallel) is held to the frozen GRADING_FORMAT
    rule: no float literal other than 0/1/100, and no large integer that could
    be a unit factor or a molar mass.
    """
    rel = _rel(path)
    if not path.exists():
        if check_feedback:
            pending.append(f'source scan: {rel} is not authored yet (feedback module in parallel)')
            return {'status': 'PENDING', 'reason': f'{rel} is absent'}
        errors.append(f'source scan: {rel} does not exist')
        return {'status': 'FAIL'}
    text = path.read_text(encoding='utf-8')
    stripped = _strip_comments(text)
    detail: dict[str, Any] = {'source': rel, 'numeric_literals': [], 'globals': []}

    masked, digest_mode = _mask_digest_region(text)
    stripped = _strip_comments(masked)
    scanned = stripped
    detail['digest_block'] = digest_mode
    if not check_feedback and digest_mode != 'n23-markers':
        errors.append(f'source scan {rel}: exactly one N23-DIGEST-BEGIN/N23-DIGEST-END pair is required')

    strict = not check_feedback
    float_re = re.compile(r'(?<![\w.$])-?\d[\d_]*(?:\.\d+)(?:[eE][+-]?\d+)?')
    exponent_re = re.compile(r'(?<![\w.$])-?\d[\d_]*[eE][+-]?\d+')
    integer_re = re.compile(r'(?<![\w.$])-?\d[\d_]*')
    allowed_float = {'0.0', '1.0', '100.0'}
    seen: set[tuple[int, str]] = set()

    def flag(line: int, token: str) -> None:
        if (line, token) in seen:
            return
        seen.add((line, token))
        detail['numeric_literals'].append({'line': line, 'token': token})
        reason = ('only -1, 0, 1 are allowed outside the declared SHA-256 block'
                  if strict else 'no float literal other than 0/1/100 and no unit-factor integer')
        errors.append(f'source scan {rel}:{line}: numeric literal {token!r} is not allowed ({reason})')

    for match in float_re.finditer(scanned):
        token = match.group(0)
        if token in allowed_float:
            continue
        flag(_line_of(scanned, match.start()), token)
    for match in exponent_re.finditer(scanned):
        token = match.group(0)
        if token in {'0', '1', '100'}:
            continue
        flag(_line_of(scanned, match.start()), token)
    for match in integer_re.finditer(scanned):
        token = match.group(0)
        if match.start() > 0 and scanned[match.start() - 1] in '.eE':
            continue
        if token in ('0', '1', '100'):
            continue
        if strict and token in ('-1',):
            continue
        if not strict and token.lstrip('-').isdigit() and abs(int(token)) <= 100:
            continue
        flag(_line_of(scanned, match.start()), token)

    for name in ENGINE_GLOBALS:
        for match in re.finditer(r'\b' + re.escape(name) + r'\b', scanned):
            line = _line_of(scanned, match.start())
            detail['globals'].append({'line': line, 'name': name})
            errors.append(f'source scan {rel}:{line}: engine global {name} is referenced directly; '
                          'engines are reached only through the frozen context')

    if strict:
        missing_context = [key for key in CONTEXT_KEYS if f"'{key}'" not in scanned]
        if missing_context:
            errors.append(f'source scan {rel}: context keys not declared: ' + ','.join(missing_context))
        for error_id in MODULE_ERRORS:
            if error_id not in text:
                errors.append(f'source scan {rel}: frozen error id {error_id} is not declared')
        if "ISLAND_ID = 'sim-grading-policy'" not in text:
            errors.append(f'source scan {rel}: SimGrading.ISLAND_ID is not sim-grading-policy')
        for api_name in ('loadPolicy', 'gradeTerminalRecord', 'applyRubricPolicy',
                         'composeGradedRecord', 'toAnalyticsEvents', 'canonicalText', 'digestOf'):
            if api_name not in text:
                errors.append(f'source scan {rel}: frozen API name {api_name} is missing')

    detail['status'] = 'CHECKED'
    detail['bytes'] = len(text.encode('utf-8'))
    return detail


# -------------------------------------------------------------------- the gate

def run_gate(repo_root: Path = ROOT, island_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    pending: list[str] = []
    policy_path = island_path or (repo_root / POLICY_PATH)
    if not policy_path.exists():
        return {'schema_version': 1, 'owner': OWNER, 'gate': 'grading', 'status': 'FAIL',
                'errors': [f'{_rel(policy_path)} does not exist'], 'pending': []}
    policy = load_json(policy_path)
    exam_policy = load_json(repo_root / EXAM_POLICY_PATH)
    bank = _bank(repo_root)

    policy_detail = check_policy(repo_root, policy, errors)
    classification_detail = check_classification(repo_root, policy, bank, errors, pending)
    matrix_detail = check_score_matrix(repo_root, exam_policy, bank, errors)
    grading_scan = _scan_source(repo_root / GRADING_TS, errors, pending, check_feedback=False)
    feedback_scan = _scan_source(repo_root / FEEDBACK_TS, errors, pending, check_feedback=True)

    status = 'FAIL' if errors else ('PENDING' if pending else 'PASS')
    checks = {
        'policy': policy_detail.get('checks', {}),
        'classification': classification_detail.get('checks', {}),
        'score_matrix': matrix_detail.get('forms', {}),
        'source_scan': {
            'grading': grading_scan,
            'feedback': feedback_scan,
        },
    }
    failed = [name for name, value in checks['policy'].items() if value is False]
    failed += [name for name, value in checks['classification'].items() if value is False]
    return {
        'schema_version': 1,
        'owner': OWNER,
        'gate': 'grading',
        'status': status,
        'islands': {
            'policy': {'id': policy.get('island_id'), 'digest': policy_detail.get('digest'),
                       'bytes': policy_detail.get('bytes')},
            'classification': {'status': classification_detail.get('status'),
                               'digest': classification_detail.get('digest'),
                               'rows': classification_detail.get('mapping_rows')},
        },
        'frozen_verdict_classes': policy_detail.get('frozen_verdict_classes', []),
        'conflicts': policy_detail.get('conflicts', []),
        'self_test_fixtures': policy_detail.get('self_test_fixtures', []),
        'slot_states': STATES,
        'score_forms': matrix_detail.get('forms', {}),
        'slot_count': matrix_detail.get('slot_count'),
        'mixed_separator': matrix_detail.get('mixed_separator'),
        'classification': classification_detail,
        'source_scan': {'grading': grading_scan, 'feedback': feedback_scan},
        'checks': checks,
        'failed_checks': failed,
        'pending': pending,
        'errors': errors,
        'notes_lv': [
            'Šis vārti nepalaiž tools/build.py un nekompilē TypeScript: oficiālā kompilācija un '
            '19. vārtu reģistrācija pieder koordinētājam.',
            'Klasifikācijas sala tiek autora paralēli; kamēr tā nav, tās pārbaude ir PENDING, nevis FAIL.',
            'Punktu matrica ir skriptēta datu kopa, nevis eksāmena forma; tā pārbauda vērtēšanas '
            'kodolu, nevis N24 komplektēšanu.',
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='write the machine-readable report to this path')
    parser.add_argument('--policy', default=None, help='validate this grading-policy file instead')
    args = parser.parse_args(argv)
    policy_path = Path(args.policy) if args.policy else None
    report = run_gate(ROOT, policy_path)

    if args.report:
        path = Path(args.report)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                        encoding='utf-8')

    if report['status'] == 'FAIL':
        for error in report.get('errors', []):
            print(f'  - {error}', file=sys.stderr)
        print('FAIL n23 grading gate', file=sys.stderr)
        return 1
    policy = report['islands']['policy']
    print(f"{report['status']} n23 grading gate: policy {policy['bytes']} B, "
          f"{len(report['self_test_fixtures'])} self-test fixtures, "
          f"{len(report['score_forms'])} score forms, "
          f"classification {report['islands']['classification']['status'].lower()}, "
          f"pending {len(report['pending'])}")
    for note in report.get('pending', []):
        print(f'  ~ {note}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
