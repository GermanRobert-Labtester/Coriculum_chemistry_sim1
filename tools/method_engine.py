#!/usr/bin/env python3
"""N19 method verdict engines: ordering, matching, sequence and the self-assessment boundary.

One interpretation authority grades the three non-numeric response types the N04
schema declares. Every comparison is structural: a step id, a position, a pair
identity. No engine reads the learner's wording, and no engine contains a
similarity, keyword or case-folding routine — the source scan in
tools/validate_method_cards.py proves that mechanically.

The Python twin in this module and the runtime twin in src/method-engine.js are
kept byte-compatible in behaviour: tools/n19_corpus.py compares their verdict
records across the whole N19 vector set.

The module consumes only data/method_engine_contract.json and the #sim-terms
island. It declares no signature, no feedback string and no vocabulary of its
own: a wrong step resolves to a signature declared by the method card, and the
signature resolves to a feedback key that exists in #sim-terms.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

CONTRACT_PATH = 'data/method_engine_contract.json'
CARDS_PATH = 'data/method_cards.json'
TERMS_PATH = 'data/terms.json'

# The canonical projection renders every number with this many decimals, so the
# Python twin and the JavaScript twin produce the same digest bytes.
CANONICAL_DECIMALS = 6

ORDERING = 'ordering'
MATCHING = 'matching'
SEQUENCE = 'sequence'
SELF_ASSESSMENT = 'self_assessment'

# The single string operation the engine performs on learner text. It is a
# blankness test on the self-assessment path only; nothing else touches text.
BLANK_FIELDS = ('text',)

PROSE_FIELDS = (
    'text_lv', 'note_lv', 'reasoning_lv', 'statement_lv', 'prompt_lv', 'title_lv',
    'subtitle_lv', 'misconception_note_lv', 'expected_summary_lv', 'order_citation_lv',
    'entry_lv', 'quantity_lv', 'text',
)


class MethodEngineError(ValueError):
    """Raised when a spec or submission cannot be interpreted structurally."""


def canonical_number(value: Any) -> str:
    """Numbers are projected with fixed decimals so both twins agree byte for byte."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, int):
        value = float(value)
    return '%.*f' % (CANONICAL_DECIMALS, value)


def canonical_projection(value: Any) -> str:
    """The declared canonical projection: sorted keys, no whitespace, fixed decimals."""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return canonical_number(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return '[' + ','.join(canonical_projection(item) for item in value) + ']'
    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            parts.append(json.dumps(str(key), ensure_ascii=False) + ':' + canonical_projection(value[key]))
        return '{' + ','.join(parts) + '}'
    return 'null'


def canonical_json_bytes(value: Any) -> bytes:
    return canonical_projection(value).encode('utf-8')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_of(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def _is_blank(text: Any) -> bool:
    """The one and only text operation: is the recorded answer empty?

    Whitespace-only counts as blank. Content is never inspected.
    """
    if not isinstance(text, str):
        return True
    return text.strip() == ''


class MethodEngine:
    """Grades ordering, matching, sequence and self-assessment submissions."""

    def __init__(self, contract: dict[str, Any], terms: dict[str, Any]) -> None:
        self.contract = contract
        self.terms_by_key = {t['key']: t for t in terms.get('terms', [])}
        self.signature_registry = {
            entry['signature']: entry for entry in contract.get('signature_registry', [])
        }
        self._feedback_cache: dict[str, str] = {}

    # -- feedback ------------------------------------------------------------
    def feedback_text(self, key: str | None) -> str:
        """Resolve a feedback key against #sim-terms. Never invents a string."""
        if not key:
            return ''
        if key in self._feedback_cache:
            return self._feedback_cache[key]
        entry = self.terms_by_key.get(key)
        if entry is None:
            raise MethodEngineError(f'feedback key {key!r} does not resolve in #sim-terms')
        text = entry.get('text_lv', '') or ''
        self._feedback_cache[key] = text
        return text

    def signature_note(self, signature: str | None) -> str:
        """The registry note for a misconception signature, if it is registered."""
        if not signature:
            return ''
        entry = self.signature_registry.get(signature)
        return entry.get('note_lv', '') if entry else ''

    # -- spec builders -------------------------------------------------------
    def spec_from_instance(self, instance: dict[str, Any]) -> dict[str, Any]:
        """Normalise an N04 instance into an engine spec."""
        payload = instance.get('payload') or {}
        payload_class = instance.get('payload_class')
        rubric = instance.get('rubric') or []
        default_signature = None
        signatures = instance.get('misconception_signatures') or []
        if signatures:
            default_signature = signatures[0]

        if payload_class == ORDERING:
            item_ids = [item['item_id'] for item in payload.get('items', [])]
            free_groups = []
            for rule in payload.get('partial_order_rules') or []:
                if isinstance(rule, dict) and rule.get('type') == 'free_order_group':
                    free_groups.append(list(rule.get('item_ids', [])))
            return {
                'kind': ORDERING,
                'engine': 'N19-ordering',
                'item_ids': item_ids,
                'correct_order': list(payload.get('correct_order', [])),
                'free_groups': free_groups,
                'step_meta': {},
                'default_signature': default_signature,
                'rubric': rubric,
                'source_ref': instance.get('question_id'),
            }
        if payload_class == MATCHING:
            correct_pairs = {p['left_id']: p['right_id'] for p in payload.get('correct_pairs', [])}
            return {
                'kind': MATCHING,
                'engine': 'N19-matching',
                'left_items': [{'id': item['id'], 'text_lv': item.get('text_lv', '')}
                               for item in payload.get('left_items', [])],
                'right_items': [{'id': item['id'], 'text_lv': item.get('text_lv', '')}
                                for item in payload.get('right_items', [])],
                'correct_pairs': correct_pairs,
                'pair_meta': {},
                'default_signature': default_signature,
                'rubric': rubric,
                'source_ref': instance.get('question_id'),
            }
        if payload_class == 'method':
            return {
                'kind': SELF_ASSESSMENT,
                'engine': 'N19-self',
                'rubric': rubric,
                'default_signature': default_signature,
                'source_ref': instance.get('question_id'),
            }
        raise MethodEngineError(f'payload_class {payload_class!r} is not graded by the N19 engines')

    def spec_from_card(self, card: dict[str, Any], kind: str, prompt_id: str | None = None,
                       rubric: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Normalise a method card into an engine spec."""
        steps = card.get('steps', [])
        item_ids = [step['step_id'] for step in steps]
        step_meta = {}
        for step in steps:
            step_meta[step['step_id']] = {
                'signature': step.get('misconception_signature'),
                'note_lv': step.get('misconception_note_lv', ''),
                'feedback_key': step.get('feedback_key'),
            }
        free_groups = [list(group['step_ids']) for group in card.get('free_order_groups', [])]
        default_signature = None
        for step in steps:
            if step.get('misconception_signature'):
                default_signature = step['misconception_signature']
                break

        if kind == ORDERING:
            return {
                'kind': ORDERING,
                'engine': 'N19-ordering',
                'item_ids': item_ids,
                'correct_order': item_ids[:],
                'free_groups': free_groups,
                'step_meta': step_meta,
                'default_signature': default_signature,
                'rubric': rubric or [],
                'card_id': card.get('card_id'),
                'source_ref': card.get('card_id'),
            }
        if kind == MATCHING:
            matching = card.get('matching')
            if not matching:
                raise MethodEngineError(f'card {card.get("card_id")!r} declares no matching exercise')
            correct_pairs = {p['left_id']: p['right_id'] for p in matching['correct_pairs']}
            pair_meta = {
                p['left_id']: {
                    'signature': p.get('misconception_signature'),
                    'note_lv': p.get('note_lv', ''),
                    'feedback_key': p.get('feedback_key'),
                }
                for p in matching['correct_pairs']
            }
            return {
                'kind': MATCHING,
                'engine': 'N19-matching',
                'left_items': matching['left_items'],
                'right_items': matching['right_items'],
                'correct_pairs': correct_pairs,
                'pair_meta': pair_meta,
                'default_signature': default_signature,
                'rubric': rubric or [],
                'card_id': card.get('card_id'),
                'source_ref': card.get('card_id'),
            }
        if kind == SEQUENCE:
            prompts = card.get('sequence_prompts', [])
            chosen = None
            for prompt in prompts:
                if prompt_id is None or prompt['prompt_id'] == prompt_id:
                    chosen = prompt
                    break
            if chosen is None:
                raise MethodEngineError(f'card {card.get("card_id")!r} has no sequence prompt {prompt_id!r}')
            distractors = {
                d['step_id']: {
                    'signature': d.get('misconception_signature'),
                    'note_lv': d.get('note_lv', ''),
                }
                for d in chosen.get('distractors', [])
            }
            return {
                'kind': SEQUENCE,
                'engine': 'N19-sequence',
                'acceptance_step_ids': list(chosen.get('acceptance_step_ids', [])),
                'distractors': distractors,
                'step_meta': step_meta,
                'default_signature': default_signature,
                'rubric': rubric or [],
                'card_id': card.get('card_id'),
                'prompt_id': chosen['prompt_id'],
                'source_ref': f"{card.get('card_id')}#{chosen['prompt_id']}",
            }
        if kind == SELF_ASSESSMENT:
            return {
                'kind': SELF_ASSESSMENT,
                'engine': 'N19-self',
                'rubric': rubric or [],
                'default_signature': default_signature,
                'card_id': card.get('card_id'),
                'source_ref': card.get('card_id'),
            }
        raise MethodEngineError(f'unsupported card engine kind {kind!r}')

    # -- rubric helpers ------------------------------------------------------
    @staticmethod
    def _split_rubric(rubric: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        auto_items = [r for r in rubric
                      if r.get('grading') in ('auto', 'mixed')
                      and r.get('engine_binding') not in ('self-assessed', 'human-review')]
        pending_items = [r for r in rubric if r not in auto_items]
        return auto_items, pending_items

    def _criterion(self, criterion_id: str, status: str, points: float, max_points: float,
                   pending_points: float = 0.0) -> dict[str, Any]:
        return {
            'criterion_id': criterion_id,
            'status': status,
            'awarded_points': float(points),
            'pending_points': float(pending_points),
            'max_points': float(max_points),
        }

    def _envelope(self, spec: dict[str, Any], verdict_class: str, error_class: str,
                  awarded: list[dict[str, Any]], machine_points: float, pending_points: float,
                  max_points: float, diagnostics: dict[str, Any],
                  submission: dict[str, Any]) -> dict[str, Any]:
        awarded = sorted(awarded, key=lambda c: c['criterion_id'])
        return {
            'engine': spec.get('engine', 'N19'),
            'kind': spec['kind'],
            'verdict_class': verdict_class,
            'error_class': error_class,
            'awarded_criteria': awarded,
            'machine_checked_points': float(machine_points),
            'self_assessed_points': 0.0,
            'human_reviewed_points': 0.0,
            'pending_points': float(pending_points),
            'max_points': float(max_points),
            'diagnostics': diagnostics,
            'replay': {
                'spec_digest': digest_of(spec),
                'submission_digest': digest_of(submission),
                'source_ref': spec.get('source_ref'),
            },
        }

    @staticmethod
    def _verdict_class(machine_points: float, auto_max: float, pending_points: float,
                       has_pending: bool, error_class: str) -> str:
        if auto_max <= 0 and has_pending:
            return 'incorrect' if error_class == 'BLANK_RESPONSE' else 'pending_self_assessment'
        if machine_points == auto_max and auto_max > 0:
            return 'auto_passed_pending_review' if has_pending else 'correct'
        if machine_points > 0:
            return 'partial'
        return 'incorrect'

    # -- ordering ------------------------------------------------------------
    def grade_ordering(self, spec: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        rubric = spec.get('rubric') or []
        auto_items, pending_items = self._split_rubric(rubric)
        correct_order = list(spec.get('correct_order', []))
        item_ids = list(spec.get('item_ids', []))
        free_groups = [set(g) for g in spec.get('free_groups', [])]
        step_meta = spec.get('step_meta') or {}
        default_signature = spec.get('default_signature')

        order = submission.get('order')
        order = list(order) if isinstance(order, (list, tuple)) else []

        awarded: list[dict[str, Any]] = []
        pending_points = 0.0
        max_points = 0.0
        for item in pending_items:
            points = float(item.get('points', 0.0))
            max_points += points
            pending_points += points
            awarded.append(self._criterion(item['criterion_id'], 'pending', 0.0, points, points))

        per_step: list[dict[str, Any]] = []
        signatures: list[str] = []
        remediation: list[dict[str, Any]] = []
        remediation_seen: dict[tuple[str, str], bool] = {}
        wrong_positions: list[int] = []
        error_class = 'NONE'

        if not order:
            error_class = 'BLANK_RESPONSE'
            matched = False
        else:
            is_permutation = len(order) == len(correct_order) and set(order) == set(correct_order)
            matched = is_permutation
            for index in range(max(len(correct_order), len(order))):
                submitted_id = order[index] if index < len(order) else None
                expected_id = correct_order[index] if index < len(correct_order) else None
                status = 'correct'
                if submitted_id is None:
                    status = 'missing_step'
                elif submitted_id not in item_ids:
                    status = 'unknown_step'
                elif submitted_id != expected_id:
                    same_group = any(submitted_id in g and expected_id in g for g in free_groups)
                    status = 'free_order_equivalent' if same_group else 'misplaced'
                if status in ('correct', 'free_order_equivalent'):
                    per_step.append(self._step_diagnostic(index, submitted_id, expected_id, status,
                                                         step_meta, default_signature))
                    continue
                matched = False
                wrong_positions.append(index)
                submitted_meta = step_meta.get(submitted_id) if submitted_id else None
                expected_meta = step_meta.get(expected_id) if expected_id else None
                for meta in (submitted_meta, expected_meta):
                    signature = (meta or {}).get('signature') or default_signature
                    if signature and signature not in signatures:
                        signatures.append(signature)
                per_step.append(self._step_diagnostic(index, submitted_id, expected_id, status,
                                                     step_meta, default_signature))
                for step_id in (submitted_id, expected_id):
                    if not step_id:
                        continue
                    meta = step_meta.get(step_id)
                    if not meta:
                        continue
                    entry = {
                        'card_id': spec.get('card_id'),
                        'step_id': step_id,
                        'misconception_signature': meta.get('signature') or default_signature,
                        'note_lv': meta.get('note_lv', ''),
                        'feedback_key': meta.get('feedback_key'),
                        'feedback_text': self.feedback_text(meta.get('feedback_key')),
                    }
                    key = (str(entry['card_id']), str(entry['step_id']))
                    if key not in remediation_seen:
                        remediation_seen[key] = True
                        remediation.append(entry)
            if not matched and error_class == 'NONE':
                error_class = 'WRONG_ORDER'

        machine_points = 0.0
        auto_max = 0.0
        for item in auto_items:
            points = float(item.get('points', 0.0))
            auto_max += points
            criterion_id = item['criterion_id']
            passed = matched
            if '_STEP_' in criterion_id and per_step:
                step_id = criterion_id.split('_STEP_', 1)[1]
                step_status = next((s['status'] for s in per_step if s['step_id'] == step_id), None)
                passed = step_status in ('correct', 'free_order_equivalent')
            awarded_points = points if passed else 0.0
            machine_points += awarded_points
            max_points += points
            awarded.append(self._criterion(criterion_id, 'awarded' if passed else 'denied',
                                           awarded_points, points))

        diagnostics = {
            'per_step': per_step,
            'wrong_positions': wrong_positions,
            'signatures': sorted(signatures),
            'remediation': remediation,
        }
        verdict_class = self._verdict_class(machine_points, auto_max, pending_points,
                                            bool(pending_items), error_class)
        return self._envelope(spec, verdict_class, error_class, awarded, machine_points,
                              pending_points, max_points, diagnostics, submission)

    def _step_diagnostic(self, index: int, submitted_id: str | None, expected_id: str | None,
                         status: str, step_meta: dict[str, Any],
                         default_signature: str | None) -> dict[str, Any]:
        meta = step_meta.get(submitted_id or '') or step_meta.get(expected_id or '') or {}
        signature = meta.get('signature') or default_signature
        feedback_key = meta.get('feedback_key')
        return {
            'position': index,
            'step_id': submitted_id,
            'expected_step_id': expected_id,
            'status': status,
            'misconception_signature': signature,
            'misconception_note_lv': meta.get('note_lv', ''),
            'feedback_key': feedback_key,
            'feedback_text': self.feedback_text(feedback_key),
        }

    # -- matching ------------------------------------------------------------
    def grade_matching(self, spec: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        rubric = spec.get('rubric') or []
        auto_items, pending_items = self._split_rubric(rubric)
        correct_pairs = spec.get('correct_pairs') or {}
        pair_meta = spec.get('pair_meta') or {}
        default_signature = spec.get('default_signature')
        right_ids = {item['id'] for item in spec.get('right_items', [])}

        pairs = submission.get('pairs')
        pairs = list(pairs) if isinstance(pairs, (list, tuple)) else []

        awarded: list[dict[str, Any]] = []
        pending_points = 0.0
        max_points = 0.0
        for item in pending_items:
            points = float(item.get('points', 0.0))
            max_points += points
            pending_points += points
            awarded.append(self._criterion(item['criterion_id'], 'pending', 0.0, points, points))

        pair_map: dict[str, str] = {}
        left_counts: dict[str, int] = {}
        right_counts: dict[str, int] = {}
        for pair in pairs:
            if not isinstance(pair, dict):
                continue
            left_id = pair.get('left_id')
            right_id = pair.get('right_id')
            if left_id is None:
                continue
            left_counts[left_id] = left_counts.get(left_id, 0) + 1
            if right_id is not None:
                right_counts[right_id] = right_counts.get(right_id, 0) + 1
            pair_map[left_id] = right_id
        duplicate_left = any(count > 1 for count in left_counts.values())

        per_pair: list[dict[str, Any]] = []
        signatures: list[str] = []
        remediation: list[dict[str, Any]] = []
        remediation_seen: dict[tuple[str, str], bool] = {}
        pair_statuses: dict[str, str] = {}

        for left_id in correct_pairs:
            expected_right = correct_pairs[left_id]
            count = left_counts.get(left_id, 0)
            submitted_right = pair_map.get(left_id)
            if count == 0:
                status = 'unmatched'
            elif count > 1:
                status = 'repeated_left'
            elif submitted_right not in right_ids:
                status = 'unknown_right'
            elif right_counts.get(submitted_right, 0) > 1:
                status = 'repeated_right'
            elif submitted_right != expected_right:
                status = 'wrong_pair'
            else:
                status = 'correct'
            pair_statuses[left_id] = status
            meta = pair_meta.get(left_id) or {}
            signature = meta.get('signature') or default_signature
            if status != 'correct' and signature and signature not in signatures:
                signatures.append(signature)
            per_pair.append({
                'left_id': left_id,
                'submitted_right_id': submitted_right,
                'expected_right_id': expected_right,
                'status': status,
                'misconception_signature': signature,
                'misconception_note_lv': meta.get('note_lv', ''),
                'feedback_key': meta.get('feedback_key'),
                'feedback_text': self.feedback_text(meta.get('feedback_key')),
            })
            if status != 'correct' and (meta.get('signature') or default_signature):
                entry = {
                    'card_id': spec.get('card_id'),
                    'step_id': left_id,
                    'misconception_signature': signature,
                    'note_lv': meta.get('note_lv', ''),
                    'feedback_key': meta.get('feedback_key'),
                    'feedback_text': self.feedback_text(meta.get('feedback_key')),
                }
                key = (str(entry['card_id']), str(entry['step_id']))
                if key not in remediation_seen:
                    remediation_seen[key] = True
                    remediation.append(entry)

        all_matched = (not duplicate_left) and bool(pairs) and pair_map == correct_pairs
        error_class = 'NONE'
        if not pairs:
            error_class = 'BLANK_RESPONSE'
        elif not all_matched:
            error_class = 'WRONG_PAIRING'

        machine_points = 0.0
        auto_max = 0.0
        for item in auto_items:
            points = float(item.get('points', 0.0))
            auto_max += points
            criterion_id = item['criterion_id']
            if '_PAIR_' in criterion_id:
                left_id = criterion_id.split('_PAIR_', 1)[1]
                passed = (not duplicate_left) and pair_map.get(left_id) == correct_pairs.get(left_id)
            else:
                passed = all_matched
            awarded_points = points if passed else 0.0
            machine_points += awarded_points
            max_points += points
            awarded.append(self._criterion(criterion_id, 'awarded' if passed else 'denied',
                                           awarded_points, points))

        diagnostics = {
            'per_pair': per_pair,
            'pair_statuses': pair_statuses,
            'signatures': sorted(signatures),
            'remediation': remediation,
        }
        verdict_class = self._verdict_class(machine_points, auto_max, pending_points,
                                            bool(pending_items), error_class)
        return self._envelope(spec, verdict_class, error_class, awarded, machine_points,
                              pending_points, max_points, diagnostics, submission)

    # -- sequence ------------------------------------------------------------
    def grade_sequence(self, spec: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        rubric = spec.get('rubric') or []
        auto_items, pending_items = self._split_rubric(rubric)
        acceptance = list(spec.get('acceptance_step_ids', []))
        distractors = spec.get('distractors') or {}
        step_meta = spec.get('step_meta') or {}
        default_signature = spec.get('default_signature')

        next_step_id = submission.get('next_step_id')
        awarded: list[dict[str, Any]] = []
        pending_points = 0.0
        max_points = 0.0
        for item in pending_items:
            points = float(item.get('points', 0.0))
            max_points += points
            pending_points += points
            awarded.append(self._criterion(item['criterion_id'], 'pending', 0.0, points, points))

        error_class = 'NONE'
        signatures: list[str] = []
        remediation: list[dict[str, Any]] = []
        if not next_step_id:
            error_class = 'BLANK_RESPONSE'
            status = 'blank'
            signature = default_signature
            note = ''
            feedback_key = None
        elif next_step_id in acceptance:
            status = 'accepted'
            signature = default_signature
            note = ''
            feedback_key = None
        elif next_step_id in distractors:
            status = 'distractor'
            entry = distractors[next_step_id]
            signature = entry.get('signature') or default_signature
            note = entry.get('note_lv', '')
            feedback_key = (step_meta.get(next_step_id) or {}).get('feedback_key')
            error_class = 'WRONG_ORDER'
        else:
            status = 'unknown'
            signature = default_signature
            note = ''
            feedback_key = None
            error_class = 'WRONG_ORDER'

        if status not in ('accepted', 'blank') and signature and signature not in signatures:
            signatures.append(signature)
        if status not in ('accepted', 'blank'):
            meta = step_meta.get(next_step_id) or {}
            remediation.append({
                'card_id': spec.get('card_id'),
                'step_id': next_step_id,
                'misconception_signature': signature,
                'note_lv': note or meta.get('note_lv', ''),
                'feedback_key': feedback_key or meta.get('feedback_key'),
                'feedback_text': self.feedback_text(feedback_key or meta.get('feedback_key')),
            })

        passed = status == 'accepted'
        machine_points = 0.0
        auto_max = 0.0
        for item in auto_items:
            points = float(item.get('points', 0.0))
            auto_max += points
            awarded_points = points if passed else 0.0
            machine_points += awarded_points
            max_points += points
            awarded.append(self._criterion(item['criterion_id'], 'awarded' if passed else 'denied',
                                           awarded_points, points))

        diagnostics = {
            'per_step': [{
                'submitted_step_id': next_step_id,
                'status': status,
                'accepted_step_ids': acceptance,
                'misconception_signature': signature,
                'misconception_note_lv': note,
                'feedback_key': feedback_key,
                'feedback_text': self.feedback_text(feedback_key),
            }],
            'signatures': sorted(signatures),
            'remediation': remediation,
        }
        verdict_class = self._verdict_class(machine_points, auto_max, pending_points,
                                            bool(pending_items), error_class)
        return self._envelope(spec, verdict_class, error_class, awarded, machine_points,
                              pending_points, max_points, diagnostics, submission)

    # -- self assessment -----------------------------------------------------
    def grade_self_assessment(self, spec: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        """Record a self-assessed answer. The text is recorded, never parsed."""
        rubric = spec.get('rubric') or []
        auto_items, pending_items = self._split_rubric(rubric)
        text = submission.get('text')
        blank = _is_blank(text)

        awarded: list[dict[str, Any]] = []
        pending_points = 0.0
        max_points = 0.0
        error_class = 'NONE'
        for item in pending_items:
            points = float(item.get('points', 0.0))
            max_points += points
            if blank:
                awarded.append(self._criterion(item['criterion_id'], 'denied', 0.0, points, 0.0))
            else:
                pending_points += points
                awarded.append(self._criterion(item['criterion_id'], 'pending', 0.0, points, points))
        if blank:
            error_class = 'BLANK_RESPONSE'
        machine_points = 0.0
        for item in auto_items:
            points = float(item.get('points', 0.0))
            max_points += points
            awarded.append(self._criterion(item['criterion_id'], 'denied', 0.0, points, 0.0))

        diagnostics = {
            'per_step': [],
            'per_pair': [],
            'text_recorded': True,
            'text_parsed': False,
            'signatures': [],
            'remediation': [],
        }
        verdict_class = self._verdict_class(machine_points, sum(float(r.get('points', 0.0)) for r in auto_items),
                                            pending_points, bool(pending_items), error_class)
        return self._envelope(spec, verdict_class, error_class, awarded, machine_points,
                              pending_points, max_points, diagnostics, submission)

    # -- dispatch ------------------------------------------------------------
    def grade(self, spec: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        kind = spec.get('kind')
        if kind == ORDERING:
            return self.grade_ordering(spec, submission)
        if kind == MATCHING:
            return self.grade_matching(spec, submission)
        if kind == SEQUENCE:
            return self.grade_sequence(spec, submission)
        if kind == SELF_ASSESSMENT:
            return self.grade_self_assessment(spec, submission)
        raise MethodEngineError(f'unsupported engine kind {kind!r}')

    def grade_instance(self, instance: dict[str, Any], submission: dict[str, Any]) -> dict[str, Any]:
        return self.grade(self.spec_from_instance(instance), submission)

    @staticmethod
    def oracle_view(record: dict[str, Any]) -> dict[str, Any]:
        """The subset of a verdict record that the frozen N05 oracle also produces."""
        return {
            'verdict_class': record['verdict_class'],
            'error_class': record['error_class'],
            'awarded_criteria': record['awarded_criteria'],
            'machine_checked_points': record['machine_checked_points'],
            'self_assessed_points': record['self_assessed_points'],
            'human_reviewed_points': record['human_reviewed_points'],
            'pending_points': record['pending_points'],
            'max_points': record['max_points'],
        }


def spec_for_vector(engine: MethodEngine, cards_by_id: dict[str, dict[str, Any]],
                    vector: dict[str, Any]) -> dict[str, Any]:
    """Build the graded spec of one contract vector.

    ``spec_source`` declares where the spec comes from:

    * ``card`` (the default) — the card's own step metadata, free-order groups
      and pair metadata are merged into the vector's declared overrides. The
      card stays the single place where a step's signature and note live.
    * ``self_contained`` — the vector's spec is used verbatim (the scratch
      negatives, which must not inherit a card's free-order group).
    """
    spec = json.loads(json.dumps(vector.get('spec') or {}))
    source = vector.get('spec_source', 'card')
    if source == 'self_contained':
        return spec
    card = cards_by_id.get(vector.get('card_id'))
    if card is None:
        raise MethodEngineError(f'vector {vector.get("id")!r} names an unknown card')
    steps = card.get('steps', [])
    step_meta = {
        step['step_id']: {
            'signature': step.get('misconception_signature'),
            'note_lv': step.get('misconception_note_lv', ''),
            'feedback_key': step.get('feedback_key'),
        }
        for step in steps
    }
    default_signature = None
    for step in steps:
        if step.get('misconception_signature'):
            default_signature = step['misconception_signature']
            break
    spec.setdefault('card_id', card.get('card_id'))
    spec.setdefault('default_signature', default_signature)
    kind = spec.get('kind')
    if kind == ORDERING:
        spec.setdefault('step_meta', step_meta)
        if 'free_groups' not in spec:
            spec['free_groups'] = [list(g['step_ids']) for g in card.get('free_order_groups', [])]
    elif kind == MATCHING:
        matching = card.get('matching') or {}
        spec.setdefault('pair_meta', {
            p['left_id']: {
                'signature': p.get('misconception_signature'),
                'note_lv': p.get('note_lv', ''),
                'feedback_key': p.get('feedback_key'),
            }
            for p in matching.get('correct_pairs', [])
        })
    elif kind == SEQUENCE:
        spec.setdefault('step_meta', step_meta)
    return spec
