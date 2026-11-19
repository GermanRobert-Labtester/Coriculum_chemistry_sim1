#!/usr/bin/env python3
"""N20 review workflow gate for the frozen practice bank.

Every instance that enters the frozen bank must pass the review workflow:
``authored -> validated -> recomputed -> reviewed -> accepted``. The gate is
mechanical wherever it can be and honest about the rest.

Mechanical checks, re-run on every gate invocation (never trusted from a
previous run):

``schema``
    the N04 instance schema (``data/question_schema.json``), plus the
    cross-island vocabulary (outcome ids, tolerance classes);
``range_compliance``
    every drawn value inside its declared range and on its declared step
    grid, every conventions reference resolving, and the seed reproducing the
    frozen instance byte for byte;
``n17_recompute``
    every derived value recomputed through the N17 quantity engine from the
    *frozen* inputs, with the dimension of the declared unit checked against
    the dimension N17 computes and the answer compared inside the tolerance
    class that will grade it;
``n12_leak_scan``
    the N12 scanner over the instance's own learner-facing surfaces with the
    instance's own key values as answer tokens, with reasoned exemptions;
``accessibility_structure``
    a structural check (unique option ids, id-based matching, labelled input
    fields). Renderer-level assistive-technology and visual acceptance is
    explicitly *not* claimed here; that belongs to N22/N34.

The human step is the sign-off line. It is recorded as the N20 task author's
preparation-pass sign-off. It is **not** an RSU instructor acceptance and it
does not claim any official examination status.

Modes:
    (default)              the build gate: re-run every check and refuse the
                           build when any instance is not in the accepted state;
    ``--review``           run the checks and promote the passing instances to
                           the accepted state, writing the evidence records;
    ``--prove-scratch-refusal``
                           copy the bank into a scratch directory, add one
                           unreviewed instance and show that the gate refuses
                           it by id.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import sys
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import leak_scan  # noqa: E402
import quantity_engine  # noqa: E402
from validate_bank import _collect_bank_files  # noqa: E402
from variant_engine import (  # noqa: E402
    SCALE,
    VariantEngineError,
    canonical_bytes,
    derive_seed,
    ephemeral_seed,
    fixed_to_decimal_text,
    instantiate,
    load_templates,
    sha256_bytes,
    template_digest,
)

BANK_DIR = Path('data/bank')
TEMPLATE_DIR = Path('data/family_templates')
EVIDENCE = Path('evidence')
REVIEW_DATE = '2026-11-18'

REVIEW_STAGES = ['authored', 'validated', 'recomputed', 'reviewed', 'accepted']
REVIEW_CHECKS = ['schema', 'range_compliance', 'n17_recompute', 'n12_leak_scan',
                 'accessibility_structure']

SIGN_OFF = {
    'role': 'N20 uzdevuma autors — preparācijas caurja parakstīšana',
    'date': REVIEW_DATE,
    'authority': 'PROPOSED training policy (N20). Nav RSU instruktora pieņemums '
                 'un nav oficiāla eksāmena apstiprinājums.',
    'scope_lv': 'Parakstīts tikai N20 sagatavošanas caurjam: shēmas atbilstība, '
                ' diapazonu atbilstība, N17 pārrēķins, N12 noplūdes skans un '
                'struktūras pieejamības pārbaude.',
    'statement_lv': 'Pārbaudīju, ka šis uzdevums atbilst deklarētajām diapazoniem, '
                    'ka tā atbildes ir neatkarīgi pārrēķinātas caur N17 un ka '
                    'atslēgšanas tekstā nav atbildes noplūdes bez pamatojuma.',
}

# Relative tolerance for comparing a recomputed intermediate with the frozen
# display text. The display precision is the tighter bound; the slack only
# absorbs the difference between exact decimal arithmetic (N17) and the fixed
# -point rounding of the variant engine.
RECOMPUTE_EPSILON = Decimal('1e-12')


class ReviewError(RuntimeError):
    """Named failure of the review workflow."""


# --------------------------------------------------------------------- inputs

def load_bank(repo_root: Path, bank_dir: Path) -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []
    for path in _collect_bank_files(repo_root / bank_dir):
        raw = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(raw, dict) and isinstance(raw.get('questions'), list):
            instances.extend(raw['questions'])
        elif isinstance(raw, list):
            instances.extend(raw)
        else:
            instances.append(raw)
    return instances


def variant_index(templates: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for family in templates:
        for variant in family['variants']:
            index[(family['family_id'], variant['variant_id'])] = variant
    return index


def template_by_family(templates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {family['family_id']: family for family in templates}


# ------------------------------------------------------------- learner surface

def learner_facing_text(instance: dict[str, Any]) -> list[tuple[str, str]]:
    """The surfaces a learner can read *before* answering.

    Answer-key fields (the expected value, the display of the answer, the
    substep answers, the correct ids, the correct pairs, the method steps'
    expected texts) are deliberately excluded: they are the key, not the
    prompt.
    """
    payload = instance['payload']
    cls = instance['payload_class']
    surfaces: list[tuple[str, str]] = [
        ('stem', instance['stem_lv']),
        ('feedback.correct', instance['feedback_lv'].get('correct', '')),
        ('feedback.incorrect', instance['feedback_lv'].get('incorrect', '')),
    ]
    if instance['feedback_lv'].get('hint'):
        surfaces.append(('feedback.hint', instance['feedback_lv']['hint']))
    for key, value in (instance.get('givens') or {}).items():
        surfaces.append((f'givens.{key}', str(value)))
    if cls == 'option_select':
        for option in payload['options']:
            surfaces.append(('option', option['text_lv']))
        for distractor in payload.get('distractors') or []:
            surfaces.append(('distractor', distractor['rationale_lv']))
        if payload.get('justification_prompt_lv'):
            surfaces.append(('justification', payload['justification_prompt_lv']))
    elif cls == 'ordering':
        for item in payload['items']:
            surfaces.append(('item', item['text_lv']))
        surfaces.append(('explanation', payload.get('explanation_prompt_lv', '')))
    elif cls == 'matching':
        for item in payload['left_items']:
            surfaces.append(('left_item', item['text_lv']))
        for item in payload['right_items']:
            surfaces.append(('right_item', item['text_lv']))
    elif cls == 'method':
        for step in payload['steps']:
            surfaces.append(('method_step', step['prompt_lv']))
        surfaces.append(('explanation', payload.get('explanation_prompt_lv', '')))
    elif cls == 'graph':
        surfaces.append(('axis.x', payload['x_axis']['label_lv']))
        surfaces.append(('axis.y', payload['y_axis']['label_lv']))
        for index, point in enumerate(payload.get('points') or []):
            surfaces.append((f'point.{index}.x', str(point['x'])))
            surfaces.append((f'point.{index}.y', str(point['y'])))
    elif cls == 'numeric':
        for field in payload.get('input_fields') or []:
            surfaces.append(('input_label', field['label_lv']))
    return [(name, text) for name, text in surfaces if str(text).strip()]


def answer_tokens(instance: dict[str, Any]) -> list[dict[str, Any]]:
    """The instance's own key values, as N12 answer tokens."""
    payload = instance['payload']
    cls = instance['payload_class']
    tokens: list[dict[str, Any]] = []
    question_id = instance['question_id']

    def numeric_token(value: Any, unit: str, source: str) -> None:
        try:
            dec = Decimal(str(value))
        except Exception:
            return
        raw = str(value)
        tokens.append({'raw': raw, 'norm': raw.replace('.', ','), 'source': source,
                       'kind': 'numeric', 'value': dec, 'unit': unit or ''})
        if unit:
            tokens.append({'raw': f'{raw} {unit}', 'norm': f'{raw} {unit}'.replace('.', ','),
                           'source': source, 'kind': 'numeric_unit', 'value': dec, 'unit': unit})

    if cls == 'numeric':
        numeric_token(payload['expected_value'], payload.get('unit', ''), question_id)
    elif cls == 'graph':
        readout = payload['target_readout']
        numeric_token(readout['expected_value'], readout.get('unit', ''), question_id)
    elif cls == 'option_select':
        correct = set(payload.get('correct_ids') or [])
        for option in payload['options']:
            if option['option_id'] in correct:
                tokens.append({'raw': option['text_lv'], 'norm': option['text_lv'],
                               'source': question_id, 'kind': 'text'})
    elif cls == 'method':
        for step in payload.get('steps') or []:
            expected = step.get('expected')
            if isinstance(expected, str) and len(expected) >= 4:
                tokens.append({'raw': expected, 'norm': expected, 'source': question_id,
                               'kind': 'text'})
    return tokens


# ------------------------------------------------------------- range compliance

def check_range_compliance(instance: dict[str, Any], variant: dict[str, Any],
                           conventions: dict[str, Any]) -> dict[str, Any]:
    """Every drawn value inside its declared range; every reference resolving."""
    problems: list[str] = []
    checked = 0
    draws = {d['param_id']: d for d in instance['extensions']['data']['draws']}
    for param in list(variant.get('parameters') or []):
        record = draws.get(param['param_id'])
        if record is None:
            problems.append(f"param {param['param_id']} nav atrasta zīmējumu ierakstā.")
            continue
        if param['kind'] == 'int':
            value = Decimal(str(record['value']).replace(',', '.'))
            low = Decimal(param['min']) / (Decimal(10) ** param['decimals'])
            high = Decimal(param['max']) / (Decimal(10) ** param['decimals'])
            step = Decimal(param['step']) / (Decimal(10) ** param['decimals'])
            if value < low or value > high:
                problems.append(f"param {param['param_id']} vērtība {value} ārpus diapazona [{low}, {high}].")
            offset = (value - low) / step
            if offset != offset.to_integral_value():
                problems.append(f"param {param['param_id']} vērtība {value} nav uz deklarētā soļa režģa.")
            checked += 1
        elif param['kind'] == 'constant':
            try:
                resolved = resolve_reference(conventions, param['conventions_ref'])
            except VariantEngineError as error:
                problems.append(f"param {param['param_id']}: {error}")
                continue
            if str(resolved) != str(record['value']).rstrip('0').rstrip('.') and \
                    Decimal(str(resolved)) != Decimal(str(record['value']).replace(',', '.')):
                problems.append(f"param {param['param_id']} atbilst konvencijām nav "
                                f"{resolved}, bet bankā ir {record['value']}.")
            checked += 1
        elif param['kind'] == 'fixed':
            # A fixed factor is declared in display units, exactly like a drawn
            # parameter, so the declared number is scaled by its own decimals
            # before it is compared with the value the bank recorded.
            declared = (Decimal(str(param['value']))
                        / (Decimal(10) ** int(param.get('decimals', 0))))
            if declared != _decimal(record['value']):
                problems.append(f"param {param['param_id']} fiksētā vērtība nesakrīt ar banku.")
            checked += 1
    return {'status': 'PASS' if not problems else 'FAIL', 'checked': checked,
            'problems': problems}


def resolve_reference(conventions: dict[str, Any], ref: str) -> str:
    from variant_engine import resolve_convention
    return resolve_convention(conventions, ref)


# -------------------------------------------------------------- N17 recompute

def _decimal(text: Any) -> Decimal:
    return Decimal(str(text).replace(',', '.'))


def _quantity(engine: quantity_engine.Engine, value: Decimal, unit: str):
    return engine.quantity(format(value, 'f'), unit)


def _negate(engine: quantity_engine.Engine, quantity):
    """Negate a quantity without re-parsing its unit.

    A composed unit such as ``mol/1`` is a display string, not a parseable
    unit expression, so the engine's own quantity type is used to carry the
    sign instead of parsing the unit a second time.
    """
    return engine.Quantity(-quantity.value, quantity.unit,
                            dict(quantity.dimension), quantity.sig_figs)


def _unit_of(spec: dict[str, Any]) -> str:
    unit = str(spec.get('unit') or '').strip()
    return unit or '1'


def recompute_instance(engine: quantity_engine.Engine, conventions: dict[str, Any],
                       instance: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    """Recompute every derived value through the N17 quantity engine.

    The inputs are the *frozen* values of the instance, not a fresh draw, so
    the check is independent of the variant engine's arithmetic: N17 works in
    exact decimals with a dimension vector, the variant engine works in
    fixed-point integers. A disagreement in either the number or the
    dimension is a failure.
    """
    draws = {d['param_id']: d for d in instance['extensions']['data']['draws']}
    units: dict[str, str] = {}
    values: dict[str, Any] = {}
    records: list[dict[str, Any]] = []
    problems: list[str] = []

    for spec in list(variant.get('parameters') or []):
        pid = spec['param_id']
        record = draws.get(pid)
        if record is None:
            problems.append(f'iegūme {pid} nav bankas ierakstā.')
            continue
        unit = _unit_of(spec)
        units[pid] = unit
        if spec['kind'] == 'constant':
            resolved = Decimal(resolve_reference(conventions, spec['conventions_ref']))
        elif spec['kind'] == 'choice':
            continue
        else:
            resolved = _decimal(record['value'])
        try:
            values[pid] = _quantity(engine, resolved, unit)
        except Exception as error:  # noqa: BLE001 - reported, not swallowed
            problems.append(f'iegūme {pid}: {error}')

    for spec in list(variant.get('derived') or []):
        if spec.get('kind') in ('constant', 'fixed'):
            pid = spec['param_id']
            record = draws.get(pid)
            if record is None:
                problems.append(f'iegūme {pid} nav bankas ierakstā.')
                continue
            unit = _unit_of(spec)
            units[pid] = unit
            if spec['kind'] == 'constant':
                resolved = Decimal(resolve_reference(conventions, spec['conventions_ref']))
            else:
                resolved = _decimal(record['value'])
            try:
                values[pid] = _quantity(engine, resolved, unit)
            except Exception as error:  # noqa: BLE001
                problems.append(f'iegūme {pid}: {error}')
            continue

        vid = spec['value_id']
        unit = _unit_of(spec)
        units[vid] = unit
        op = spec['op']
        args = [values.get(a) for a in spec['args']]
        if any(a is None for a in args):
            problems.append(f'atvasinājums {vid}: argumenti nav atrisināti.')
            continue
        try:
            result = _apply_op(engine, op, args, unit)
        except Exception as error:  # noqa: BLE001
            problems.append(f'atvasinājums {vid} ({op}): {error}')
            continue
        # The declared unit must match the dimension N17 computed.
        try:
            declared = engine.parse_unit(unit)
        except Exception as error:  # noqa: BLE001
            problems.append(f'atvasinājums {vid}: deklarētā vienība {unit!r} nav parsējama ({error}).')
            continue
        if engine.dim_key(result.dimension) != engine.dim_key(declared):
            problems.append(
                f'atvasinājums {vid}: dimensija {engine.dim_key(result.dimension)} '
                f'nesakrīt ar deklarēto vienību {unit!r} '
                f'({engine.dim_key(declared)}).')
            continue
        frozen_text = instance['extensions']['data']['derived']
        frozen = next((d['value'] for d in frozen_text if d['value_id'] == vid), None)
        if frozen is None:
            problems.append(f'atvasinājums {vid} nav bankas ierakstā.')
            continue
        decimals = int(spec.get('display_decimals', spec.get('decimals', 6)))
        tolerance = Decimal(10) ** (-decimals) / 2 + RECOMPUTE_EPSILON
        difference = abs(result.value - _decimal(frozen))
        values[vid] = result
        records.append({
            'value_id': vid,
            'op': op,
            'args': list(spec['args']),
            'engine_path': spec.get('engine_path'),
            'declared_unit': unit,
            'frozen_value': frozen,
            'recomputed_value': format(result.value, 'f'),
            'difference': format(difference, 'f'),
            'tolerance': format(tolerance, 'f'),
            'within_tolerance': difference <= tolerance,
            'status': 'PASS' if difference <= tolerance else 'FAIL',
        })
        if difference > tolerance:
            problems.append(f'atvasinājums {vid}: pārrēķins {format(result.value, "f")} '
                            f'diferencē no {frozen} par {format(difference, "f")}.')

    answer = _check_answer(engine, instance, variant, values, records)
    if answer:
        problems.extend(answer['problems'])
    status = 'PASS' if not problems else 'FAIL'
    return {'status': status, 'values': records, 'answer': answer, 'problems': problems}


def _add_in_declared(engine: quantity_engine.Engine, left, right, unit: str):
    """Add two quantities presented in the declared unit.

    The N17 engine converts the second operand into the first operand's unit
    string, and a composed unit is not a parseable unit expression. Both
    operands are therefore presented in the unit the template declares, after
    the dimension gate confirmed that both are compatible with it.
    """
    declared = engine.parse_unit(unit)
    for operand in (left, right):
        if engine.dim_key(operand.dimension) != engine.dim_key(declared):
            raise ReviewError(f'dimensija {engine.dim_key(operand.dimension)} nesakrīt '
                              f'ar deklarēto vienību {unit!r}.')
    return engine.add(_quantity(engine, left.value, unit),
                       _quantity(engine, right.value, unit))


def _apply_op(engine: quantity_engine.Engine, op: str, args: list[Any],
              unit: str) -> Any:
    """Apply one recipe operation with the N17 quantity engine.

    ``unit`` is the unit the template declares for the result. It is used
    where the N17 engine needs a common unit to add two quantities: the
    engine's ``add`` converts the second operand into the first operand's
    *unit string*, and a composed unit such as ``L/(mol)·mol/L`` is not a
    parseable unit expression, so the operands are presented in the declared
    unit instead. The dimension gate still applies: the caller checks that
    the computed dimension equals the dimension of the declared unit, so a
    wrong declared unit is still a failure.
    """
    if op == 'identity':
        return args[0]
    if op == 'add':
        return _add_in_declared(engine, args[0], args[1], unit)
    if op == 'sub':
        return _add_in_declared(engine, args[0], _negate(engine, args[1]), unit)
    if op == 'mul':
        return engine.multiply(args[0], args[1])
    if op == 'div':
        return engine.divide(args[0], args[1])
    if op == 'mul_div':
        return engine.divide(engine.multiply(args[0], args[1]), args[2])
    if op == 'lin':
        product = engine.multiply(args[0], args[1])
        declared = engine.parse_unit(unit)
        if engine.dim_key(product.dimension) != engine.dim_key(declared):
            raise ReviewError('lin: produkta dimensija nesakrīt ar deklarēto vienību.')
        if engine.dim_key(args[2].dimension) != engine.dim_key(declared):
            raise ReviewError('lin: brīvā locekļa dimensija nesakrīt ar deklarēto vienību.')
        return engine.add(_quantity(engine, product.value, unit),
                           _quantity(engine, args[2].value, unit))
    if op == 'pow_int':
        exponent = int(args[1].value)
        result = engine.quantity('1', args[0].unit)
        for _ in range(exponent):
            result = engine.multiply(result, args[0])
        return result
    if op == 'percent':
        hundred = engine.quantity('100', '1')
        return engine.divide(engine.multiply(args[0], hundred), args[1])
    if op == 'negate':
        return _negate(engine, args[0])
    if op == 'round_decimals':
        digits = int(args[1].value)
        rounded = engine.round_half_up(args[0].value, digits, 'decimal_places')
        return _quantity(engine, rounded, unit)
    if op == 'log10_pow10':
        # N17 has no transcendental function, so the check is the identity
        # itself: the argument must be an exact power of ten and the result
        # must be its integer exponent. An approximation is never accepted.
        value = args[0].value
        if value <= 0 or value != value.to_integral_value():
            raise ReviewError('log10_pow10 argumentam jābūt pozitīvam veselam skaitlim.')
        integer = int(value)
        magnitude = integer
        zeros = 0
        while magnitude % 10 == 0:
            magnitude //= 10
            zeros += 1
        if magnitude != 1:
            raise ReviewError('log10_pow10 argumentam jābūt precīza desmitkārta.')
        if Decimal(10) ** zeros != value:
            raise ReviewError('log10_pow10 identitāte 10^n = arguments fails.')
        return _quantity(engine, Decimal(zeros), unit)
    raise ReviewError(f'Nezināma receptes operācija: {op}')


def _check_answer(engine: quantity_engine.Engine, instance: dict[str, Any],
                  variant: dict[str, Any], values: dict[str, Any],
                  records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Compare the recomputed answer with the frozen expected value."""
    payload = instance['payload']
    cls = instance['payload_class']
    if cls == 'numeric':
        expected = payload['expected_value']
        tolerance_class = payload.get('tolerance_class')
        unit = payload.get('unit', '')
    elif cls == 'graph':
        readout = payload['target_readout']
        expected = readout['expected_value']
        tolerance_class = readout.get('tolerance_class')
        unit = readout.get('unit', '')
    else:
        return None

    answers = [spec for spec in variant.get('derived') or []
               if spec.get('role') == 'answer' and spec.get('kind') not in ('constant', 'fixed')]
    if not answers:
        return {'status': 'FAIL', 'problems': ['nav atrasta atbildes loma atvasinājums.']}
    spec = answers[0]
    value = values.get(spec['value_id'])
    if value is None:
        return {'status': 'FAIL', 'problems': [f'atbildes vērtība {spec["value_id"]} nav pārrēķināta.']}
    tolerance = engine._tolerance(tolerance_class) if tolerance_class else Decimal('0')
    # The frozen expected value is the computed value rounded to the declared
    # significant figures (the N05 corpus pattern). The rounding is N17's
    # authority: rounding the recomputed value here and comparing it with the
    # frozen expected value proves that the variant engine and N17 agree on
    # the rounded answer, not only on the raw number.
    sig_figs = int(payload.get('sig_figs') or 0)
    rounded = engine.round_half_up(value.value, sig_figs, 'significant_figures') if sig_figs else value.value
    difference = abs(rounded - Decimal(str(expected)))
    within = difference <= tolerance
    problems = [] if within else [
        f'atbilde {spec["value_id"]}: N17 noapalojums {format(rounded, "f")} '
        f'diferencē no bankas atbildes {expected} par {format(difference, "f")} '
        f'(tolerances.quantity_classes[{tolerance_class}] = {tolerance}).']
    return {
        'status': 'PASS' if within else 'FAIL',
        'value_id': spec['value_id'],
        'engine_path': spec.get('engine_path'),
        'tolerance_class': tolerance_class,
        'tolerance': format(tolerance, 'f'),
        'sig_figs': sig_figs,
        'frozen_expected': str(expected),
        'recomputed_raw': format(value.value, 'f'),
        'recomputed_rounded': format(rounded, 'f'),
        'difference': format(difference, 'f'),
        'within_tolerance': within,
        'problems': problems,
    }


# ------------------------------------------------------------- accessibility

def check_accessibility_structure(instance: dict[str, Any]) -> dict[str, Any]:
    """Structural accessibility checks that can be made without a renderer."""
    payload = instance['payload']
    cls = instance['payload_class']
    problems: list[str] = []
    if cls == 'option_select':
        ids = [o['option_id'] for o in payload['options']]
        if len(ids) != len(set(ids)):
            problems.append('opciju identifikatori nav unikāli.')
        if not all(str(o.get('text_lv') or '').strip() for o in payload['options']):
            problems.append('dažām opcijām nav teksta.')
        if not all(str(d.get('rationale_lv') or '').strip() for d in payload.get('distractors') or []):
            problems.append('dažiem skaidrojumiem nav teksta.')
    elif cls == 'matching':
        left = [i['id'] for i in payload['left_items']]
        right = [i['id'] for i in payload['right_items']]
        if len(left) != len(set(left)) or len(right) != len(set(right)):
            problems.append('sasaistīšanas identifikatori nav unikāli.')
        if set(p['left_id'] for p in payload['correct_pairs']) != set(left):
            problems.append('sasaistīšanas pāri neaptver visus kreisos vienumus.')
        if set(p['right_id'] for p in payload['correct_pairs']) != set(right):
            problems.append('sasaistīšanas pāri neaptver visus labos vienumus.')
    elif cls == 'ordering':
        ids = [i['item_id'] for i in payload['items']]
        if len(ids) != len(set(ids)):
            problems.append('kārtošanas vienumu identifikatori nav unikāli.')
        if sorted(payload['correct_order']) != sorted(ids):
            problems.append('kārtošanas atbilde neaptver visus vienumus.')
    elif cls == 'numeric':
        for field in payload.get('input_fields') or []:
            if not str(field.get('label_lv') or '').strip():
                problems.append(f"ievades laukam {field.get('field_id')} nav ievades etiķetes.")
            if field.get('kind') not in ('number', 'unit', 'text'):
                problems.append(f"ievades laukam {field.get('field_id')} ir nezināms veids.")
    elif cls == 'method':
        for step in payload.get('steps') or []:
            if not str(step.get('prompt_lv') or '').strip():
                problems.append(f"metodes solim {step.get('step_id')} nav teksta.")
    return {'status': 'PASS' if not problems else 'FAIL', 'problems': problems,
            'renderer_acceptance': 'not claimed here — deferred to N22/N34'}


# ---------------------------------------------------------------- leak scan

def check_leak_scan(instance: dict[str, Any], grammar: dict[str, Any],
                    exemption: dict[str, Any] | None) -> dict[str, Any]:
    """Run the N12 scanner over the instance's own learner-facing surfaces.

    Two things are recorded:

    * **leaks** — a key value of the instance found in a learner-facing
      surface. A leak is a failure unless it is covered by a declared
      exemption with a reason code from the N12 set, a Latvian reason and an
      explicit scope;
    * **borderline proximities** — the N12 borderline rule applied to a graph
      instance: an answer that lies within two axis steps of a value labelled
      on the plot. A proximity is not a leak, but it is the case the learner
      has to interpolate, so it is recorded and must be declared.
    """
    tokens = answer_tokens(instance)
    findings: list[dict[str, Any]] = []
    for name, text in learner_facing_text(instance):
        for finding in leak_scan.scan_text_for_leaks(
                instance['family_id'], instance['question_id'], text, tokens,
                surface=name, grammar=grammar):
            findings.append(finding)
    borderline = check_borderline_proximity(instance)
    declared = _validate_exemption(exemption, findings)
    if declared and declared['reason_code'] == 'EXEMPT_GIVEN_INPUT' and not declared['exempted_values']:
        # The exempted value is one of the instance's own given inputs, whose
        # value is drawn; the effective list is therefore resolved per
        # instance and recorded with the finding.
        declared = dict(declared, exempted_values=_given_values(instance))
    exempted: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    for finding in findings:
        if _covered_by(finding, declared):
            exempted.append(dict(finding, exemption_reason_code=declared['reason_code'],
                                 exemption_reason_lv=declared['reason_lv']))
        else:
            remaining.append(finding)
    unused = []
    if declared and not exempted:
        unused.append({'note': 'Deklarētais atviegums neatbilst nevienam konstatētam '
                                'noplūdes gadījumam; tas fiksētā, ka robežgadījums '
                                'tika novērtēts, bet noplūde netika konstatēta.'})
    status = 'PASS' if not remaining else 'FAIL'
    return {
        'status': status,
        'findings': remaining,
        'exempted_findings': exempted,
        'borderline': borderline,
        'declared_exemption': declared,
        'unused_exemption': unused,
        'tokens': len(tokens),
    }


def _validate_exemption(exemption: dict[str, Any] | None,
                        findings: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Check the bank-level exemption contract and return the declaration."""
    if not exemption:
        return None
    if not isinstance(exemption, dict) or not exemption.get('exempt'):
        return None
    code = exemption.get('reason_code')
    reason = str(exemption.get('reason_lv') or '').strip()
    values = list(exemption.get('exempted_values') or [])
    surfaces = list(exemption.get('exempted_surfaces') or [])
    problems: list[str] = []
    if code not in leak_scan.ALLOWED_EXEMPTION_CODES:
        problems.append(f'nezināms atvieguma kods {code!r}.')
    if len(reason) < 20:
        problems.append('atvieguma iemesls īsāks par 20 rakstzīmēm.')
    if not values and not surfaces and code != 'EXEMPT_GIVEN_INPUT':
        problems.append('atviegumam jānorāda vai nu exempted_values, vai exempted_surfaces.')
    if code == 'EXEMPT_GIVEN_INPUT' and not values and not surfaces:
        # The exempted value is the instance's own given input; it is resolved
        # per instance because a drawn value differs from seed to seed.
        pass
    if problems:
        raise ReviewError('atvieguma deklarācija nav derīga: ' + '; '.join(problems))
    return {'reason_code': code, 'reason_lv': reason,
            'exempted_values': values, 'exempted_surfaces': surfaces}


def _norm(text: Any) -> str:
    return ' '.join(str(text or '').replace(',', '.').split()).lower()


def _given_values(instance: dict[str, Any]) -> list[str]:
    """The instance's own given inputs, as written values."""
    return [str(value) for value in (instance.get('givens') or {}).values()]


def _first_number(text: Any) -> Decimal | None:
    match = re.search(r'-?\d+(?:[.,]\d+)?', str(text or ''))
    if not match:
        return None
    try:
        return Decimal(match.group(0).replace(',', '.'))
    except Exception:
        return None


def _covered_by(finding: dict[str, Any], declared: dict[str, Any] | None) -> bool:
    if not declared:
        return False
    surface = finding.get('surface')
    surfaces = declared.get('exempted_surfaces') or []
    values = declared.get('exempted_values') or []
    candidates = [finding.get('leaked_raw'), finding.get('target_raw'),
                  finding.get('leaked_norm')]
    if surfaces and surface in surfaces:
        if not values:
            return True
    for value in values:
        wanted = _norm(value)
        for candidate in candidates:
            if candidate and _norm(candidate) == wanted:
                return True
    if declared['reason_code'] == 'EXEMPT_GIVEN_INPUT':
        # The exempted value is a given input; the match is on the number, so
        # that a drawn value and its rendered form agree.
        given_numbers = [_first_number(value) for value in values]
        for candidate in candidates:
            number = _first_number(candidate)
            if number is None:
                continue
            for given in given_numbers:
                if given is not None and abs(given - number) < Decimal('1e-12'):
                    return True
    return False


def check_borderline_proximity(instance: dict[str, Any]) -> dict[str, Any]:
    """The N12 borderline rule applied to a graph instance.

    A graph answer that lies within two axis steps of a value labelled on the
    plot is a borderline proximity: the learner has to interpolate between
    labelled values rather than read one off. The rule is reported, not
    enforced — a declared exemption records that the proximity is intended.
    """
    payload = instance['payload']
    if instance['payload_class'] != 'graph':
        return {'status': 'NOT_APPLICABLE', 'proximities': []}
    readout = payload['target_readout']
    try:
        answer = Decimal(str(readout['expected_value']))
    except Exception:
        return {'status': 'NOT_APPLICABLE', 'proximities': []}
    points = payload.get('points') or []
    proximities: list[dict[str, Any]] = []
    for axis in ('x', 'y'):
        values: list[Decimal] = []
        for point in points:
            try:
                values.append(Decimal(str(point[axis])))
            except Exception:
                continue
        if len(values) < 2:
            continue
        steps = sorted(values[i + 1] - values[i] for i in range(len(values) - 1))
        step = steps[0]
        if step == 0:
            continue
        for value in values:
            distance = abs(answer - value)
            if distance <= 2 * step:
                proximities.append({
                    'axis': axis,
                    'labelled_value': str(value),
                    'answer': str(answer),
                    'step': str(step),
                    'distance': str(distance),
                    'rule': leak_scan.BORDERLINE_RULE_ID,
                })
    return {
        'status': 'BORDERLINE' if proximities else 'CLEAR',
        'proximities': proximities,
        'rule': leak_scan.BORDERLINE_RULE_ID,
    }


# ------------------------------------------------------- grading alignment

def check_grading_alignment(engine: quantity_engine.Engine,
                            instance: dict[str, Any]) -> dict[str, Any]:
    """Grade a correct submission with the engine that owns the type.

    The submission is what a learner would write: the expected value rounded
    to the declared significant figures. Submitting the raw full-precision
    number would fail the significant-figure criterion, which is the engine
    working as frozen — not a defect in the bank.
    """
    payload = instance['payload']
    cls = instance['payload_class']
    rubric = instance['rubric']
    has_pending = any(
        r.get('grading') not in ('auto', 'mixed')
        or r.get('engine_binding') in ('self-assessed', 'human-review')
        for r in rubric)
    if cls == 'numeric':
        submission = {'value': _learner_number(engine, payload['expected_value'],
                                                int(payload.get('sig_figs') or 0)),
                      'unit': payload.get('unit', '')}
        expected = 'auto_passed_pending_review' if has_pending else 'correct'
    elif cls == 'graph':
        readout = payload['target_readout']
        submission = {'value': readout['expected_value'], 'unit': readout.get('unit', '')}
        expected = 'auto_passed_pending_review' if has_pending else 'correct'
    elif cls == 'option_select':
        submission = {'selected_ids': list(payload['correct_ids'])}
        expected = 'auto_passed_pending_review' if has_pending else 'correct'
    elif cls == 'ordering':
        submission = {'order': list(payload['correct_order'])}
        expected = 'auto_passed_pending_review' if has_pending else 'correct'
    elif cls == 'matching':
        submission = {'pairs': [dict(p) for p in payload['correct_pairs']]}
        expected = 'auto_passed_pending_review' if has_pending else 'correct'
    elif cls == 'method':
        submission = {'text': 'atbilde'}
        expected = 'pending_self_assessment'
    else:
        return {'status': 'FAIL', 'problem': f'nepazīms payload klase {cls}'}
    verdict = engine.grade(instance, submission)
    actual = verdict['verdict_class']
    ok = actual == expected
    return {
        'status': 'PASS' if ok else 'FAIL',
        'payload_class': cls,
        'submission': submission,
        'expected_verdict': expected,
        'actual_verdict': actual,
        'error_class': verdict['error_class'],
        'machine_checked_points': verdict['machine_checked_points'],
        'pending_points': verdict['pending_points'],
        'max_points': verdict['max_points'],
    }


def _learner_number(engine: quantity_engine.Engine, value: Any, sig_figs: int) -> str:
    """The answer as a learner would write it, with the declared precision."""
    dec = Decimal(str(value))
    if sig_figs:
        dec = engine.round_half_up(dec, sig_figs, 'significant_figures')
    text = format(dec, 'f')
    if sig_figs and engine.count_sig_figs(text) != sig_figs:
        # A whole number with trailing zeros cannot carry the declared
        # precision in plain notation; report it instead of hiding it.
        candidate = format(dec, 'E')
        if engine.count_sig_figs(candidate) == sig_figs:
            text = candidate
    return text


# ------------------------------------------------------------------ the gate

def review_instance(engine: quantity_engine.Engine, conventions: dict[str, Any],
                    grammar: dict[str, Any], instance: dict[str, Any],
                    variant: dict[str, Any]) -> dict[str, Any]:
    checks = {
        'range_compliance': check_range_compliance(instance, variant, conventions),
        'n17_recompute': recompute_instance(engine, conventions, instance, variant),
        'n12_leak_scan': check_leak_scan(instance, grammar, variant.get('leak_scan_exemption')),
        'accessibility_structure': check_accessibility_structure(instance),
        'grading_alignment': check_grading_alignment(engine, instance),
    }
    failed = [name for name, report in checks.items() if report.get('status') != 'PASS']
    return {
        'question_id': instance['question_id'],
        'family_id': instance['family_id'],
        'variant_id': instance['variant_id'],
        'type_id': instance['type_id'],
        'payload_class': instance['payload_class'],
        'status': 'PASS' if not failed else 'FAIL',
        'failed_checks': failed,
        'checks': checks,
    }


def accepted_state(instance: dict[str, Any]) -> dict[str, Any]:
    """The review state an accepted instance carries."""
    workflow = {
        'state': 'accepted',
        'stages': list(REVIEW_STAGES),
        'checks': list(REVIEW_CHECKS),
        'sign_off': dict(SIGN_OFF),
    }
    # A deep copy, not a JSON round-trip: a freshly instantiated instance
    # carries the canonical number literals, and a JSON round-trip would turn
    # them into floats and silently change the bytes the digest covers.
    updated = copy.deepcopy(instance)
    updated['review'] = {'content': 'passed', 'source': 'passed',
                         'calculation': 'passed', 'accessibility': 'passed'}
    updated['extensions']['data']['review_workflow'] = workflow
    return updated


def pending_state(instance: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(instance)
    updated['review'] = {'content': 'pending', 'source': 'pending',
                         'calculation': 'pending', 'accessibility': 'pending'}
    updated['extensions']['data'].pop('review_workflow', None)
    return updated


def review_state_ok(instance: dict[str, Any]) -> tuple[bool, str]:
    review = instance.get('review') or {}
    for field in ('content', 'source', 'calculation', 'accessibility'):
        if review.get(field) != 'passed':
            return False, f'review.{field} ir {review.get(field)!r}, nevis "passed".'
    workflow = (instance.get('extensions') or {}).get('data', {}).get('review_workflow')
    if not isinstance(workflow, dict):
        return False, 'review_workflow trūkst.'
    if workflow.get('state') != 'accepted':
        return False, f'review_workflow.state ir {workflow.get("state")!r}, nevis "accepted".'
    sign_off = workflow.get('sign_off') or {}
    if not str(sign_off.get('statement_lv') or '').strip():
        return False, 'review_workflow.sign_off.statement_lv trūkst.'
    if not str(sign_off.get('role') or '').strip():
        return False, 'review_workflow.sign_off.role trūkst.'
    return True, ''


# ------------------------------------------------------------------ commands

def run_review(repo_root: Path, bank_dir: Path) -> dict[str, Any]:
    """Run every check over the bank and promote the passing instances."""
    templates = load_templates(repo_root / TEMPLATE_DIR)
    index = variant_index(templates)
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    terms = json.loads((repo_root / 'data/terms.json').read_text(encoding='utf-8'))
    grammar = terms['unit_grammar']
    engine = quantity_engine.load(repo_root)

    instances = load_bank(repo_root, bank_dir)
    workflow: list[dict[str, Any]] = []
    recompute_records: list[dict[str, Any]] = []
    leak_records: list[dict[str, Any]] = []
    promoted: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for instance in instances:
        key = (instance['family_id'], instance['variant_id'])
        variant = index.get(key)
        if variant is None:
            failures.append({'question_id': instance['question_id'],
                             'problem': 'nav atrasta ģimeņa veidota šablonā.'})
            continue
        record = review_instance(engine, conventions, grammar, instance, variant)
        workflow.append(record)
        recompute_records.append({
            'question_id': instance['question_id'],
            'family_id': instance['family_id'],
            'variant_id': instance['variant_id'],
            'engine_path': instance['extensions']['data'].get('engine_path'),
            'recompute': record['checks']['n17_recompute'],
            'answer': record['checks']['n17_recompute'].get('answer'),
        })
        leak_records.append({
            'question_id': instance['question_id'],
            'family_id': instance['family_id'],
            'variant_id': instance['variant_id'],
            'leak_scan': record['checks']['n12_leak_scan'],
        })
        if record['status'] == 'PASS':
            promoted.append(accepted_state(instance))
        else:
            failures.append({'question_id': instance['question_id'],
                             'failed_checks': record['failed_checks'],
                             'problems': [p for check in record['checks'].values()
                                          for p in check.get('problems', [])]})

    # Write the accepted state back, grouped per family file.
    by_family: dict[str, list[dict[str, Any]]] = {}
    for instance in promoted:
        by_family.setdefault(instance['family_id'], []).append(instance)
    for path in _collect_bank_files(repo_root / bank_dir):
        raw = json.loads(path.read_text(encoding='utf-8'))
        family_id = path.stem
        questions = raw.get('questions') if isinstance(raw, dict) else raw
        if family_id not in by_family:
            continue
        updated = []
        for question in questions:
            match = next((q for q in by_family[family_id]
                          if q['question_id'] == question['question_id']), None)
            updated.append(match if match is not None else pending_state(question))
        payload = {'island_id': 'sim-bank', 'questions': updated}
        path.write_bytes(canonical_bytes(payload) + b'\n')

    report = {
        'status': 'PASS' if not failures else 'FAIL',
        'instances': len(instances),
        'promoted': len(promoted),
        'failures': failures,
        'workflow': workflow,
    }
    _write_evidence(repo_root, report, recompute_records, leak_records)
    return report


def _write_evidence(repo_root: Path, report: dict[str, Any],
                    recompute_records: list[dict[str, Any]],
                    leak_records: list[dict[str, Any]]) -> None:
    evidence = repo_root / EVIDENCE
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'N20_REVIEW_WORKFLOW.json').write_text(
        json.dumps({'schema_version': 1, 'owner': 'N20', 'status': report['status'],
                    'instances': report['instances'], 'promoted': report['promoted'],
                    'stages': REVIEW_STAGES, 'checks': REVIEW_CHECKS,
                    'sign_off': SIGN_OFF,
                    'workflow': report['workflow']},
                   ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (evidence / 'N20_RECOMPUTE_RECORD.json').write_text(
        json.dumps({'schema_version': 1, 'owner': 'N20',
                    'authority': 'N17 quantity engine (tools/quantity_engine.py)',
                    'instances': recompute_records},
                   ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    (evidence / 'N20_LEAK_SCAN_RECORD.json').write_text(
        json.dumps({'schema_version': 1, 'owner': 'N20',
                    'authority': 'N12 leak scanner (tools/leak_scan.py)',
                    'exemption_codes': sorted(leak_scan.ALLOWED_EXEMPTION_CODES),
                    'instances': leak_records},
                   ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run_gate(repo_root: Path, bank_dir: Path) -> dict[str, Any]:
    """The build gate: refuse the bank unless every instance is accepted."""
    templates = load_templates(repo_root / TEMPLATE_DIR)
    index = variant_index(templates)
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    terms = json.loads((repo_root / 'data/terms.json').read_text(encoding='utf-8'))
    grammar = terms['unit_grammar']
    engine = quantity_engine.load(repo_root)

    instances = load_bank(repo_root, bank_dir)
    violations: list[dict[str, Any]] = []
    for instance in instances:
        key = (instance['family_id'], instance['variant_id'])
        variant = index.get(key)
        if variant is None:
            violations.append({'question_id': instance['question_id'],
                               'code': 'E_REVIEW_NO_TEMPLATE',
                               'message': 'nav atrasta ģimeņa veidota šablonā.'})
            continue
        ok, reason = review_state_ok(instance)
        if not ok:
            violations.append({'question_id': instance['question_id'],
                               'code': 'E_REVIEW_NOT_ACCEPTED', 'message': reason})
            continue
        record = review_instance(engine, conventions, grammar, instance, variant)
        if record['status'] != 'PASS':
            violations.append({
                'question_id': instance['question_id'],
                'code': 'E_REVIEW_CHECK_FAILED',
                'message': f"neveiksmīgas pārbaudes: {record['failed_checks']}",
                'problems': [p for check in record['checks'].values()
                             for p in check.get('problems', [])],
            })
    return {
        'status': 'PASS' if not violations else 'FAIL',
        'instances': len(instances),
        'violations': violations,
        'template_digest': template_digest(templates),
        'review_stages': list(REVIEW_STAGES),
        'review_checks': list(REVIEW_CHECKS),
    }


def prove_scratch_refusal(repo_root: Path, bank_dir: Path) -> dict[str, Any]:
    """Show that the gate refuses an unreviewed scratch instance, by id.

    The scratch bank is a copy of the frozen bank with one instance whose
    review state was reset. The gate reads the templates and the conventions
    from the real repository root and the bank from the scratch directory, so
    the only thing that differs from the accepted bank is the one instance.
    """
    scratch = Path(tempfile.mkdtemp(prefix='n20-scratch-'))
    try:
        target = scratch / 'bank'
        shutil.copytree(repo_root / bank_dir, target)
        instances = load_bank(scratch, Path('bank'))
        scratch_instance = json.loads(json.dumps(instances[0]))
        scratch_instance['question_id'] = 'COL1-1-1A-ZZ-99'
        scratch_instance['family_id'] = 'FAM-1A'
        scratch_instance['variant_id'] = 'A'
        scratch_instance['review'] = {'content': 'pending', 'source': 'pending',
                                      'calculation': 'pending', 'accessibility': 'pending'}
        scratch_instance['extensions']['data'].pop('review_workflow', None)
        (target / 'FAM-1A.json').write_bytes(
            canonical_bytes({'island_id': 'sim-bank',
                             'questions': [scratch_instance] + instances[1:5]}) + b'\n')
        report = run_gate(repo_root, target)
        refused = [v for v in report['violations']
                   if v.get('question_id') == 'COL1-1-1A-ZZ-99']
        return {
            'status': 'PASS' if report['status'] == 'FAIL' and refused else 'FAIL',
            'gate_status': report['status'],
            'scratch_question_id': 'COL1-1-1A-ZZ-99',
            'refusal': refused,
            'violations': report['violations'][:5],
        }
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--bank', default=str(BANK_DIR))
    parser.add_argument('--review', action='store_true',
                        help='Run the checks and promote the passing instances.')
    parser.add_argument('--prove-scratch-refusal', action='store_true',
                        help='Show the gate refusing an unreviewed scratch instance.')
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    bank_dir = Path(args.bank)

    try:
        if args.prove_scratch_refusal:
            report = prove_scratch_refusal(repo_root, bank_dir)
        elif args.review:
            report = run_review(repo_root, bank_dir)
        else:
            report = run_gate(repo_root, bank_dir)
    except (VariantEngineError, ReviewError, quantity_engine.EngineError) as error:
        print(f'FAIL n20_bank_review: {error}', file=sys.stderr)
        return 2

    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                        encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
