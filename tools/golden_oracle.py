#!/usr/bin/env python3
"""N05 Independent Golden Oracle.

Grades a frozen question instance + student submission directly against
data/conventions.json rules using Python stdlib only (Decimal, Fraction, ast,
json, re, hashlib). Shares ZERO code with any simulator engine (N17-N19).

Import manifest is structurally enforced: no simulator engine or runtime
modules are imported.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
from typing import Any

ORACLE_VERSION = '1.0.0'
ALLOWED_STDLIB_IMPORTS = frozenset({
    '__future__',
    'argparse',
    'ast',
    'decimal',
    'fractions',
    'hashlib',
    'json',
    'pathlib',
    're',
    'sys',
    'typing',
})

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONVENTIONS_PATH = REPO_ROOT / 'data/conventions.json'

SUPERSCRIPT_MAP = str.maketrans({
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁻': '-', '⁺': '+',
})

SCI_CROSS_RE = re.compile(
    r'^\s*([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))\s*(?:[×x*]\s*10\s*(?:\^\s*([+-]?\d+)|([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)))\s*$'
)
PLAIN_OR_E_RE = re.compile(
    r'^\s*([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?)\s*$'
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha256_canonical(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def verify_import_manifest(oracle_path: Path | None = None) -> dict[str, Any]:
    """Parse this file's AST and prove only allowed stdlib modules are imported."""
    target = oracle_path or Path(__file__).resolve()
    tree = ast.parse(target.read_text(encoding='utf-8'), filename=str(target))
    found_imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found_imports.append(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found_imports.append(node.module.split('.')[0])
    unique = sorted(set(found_imports))
    disallowed = [mod for mod in unique if mod not in ALLOWED_STDLIB_IMPORTS]
    return {
        'oracle_script': str(target.name),
        'oracle_version': ORACLE_VERSION,
        'oracle_digest': sha256_file(target),
        'imports': unique,
        'disallowed_imports': disallowed,
        'independent_of_engines': len(disallowed) == 0,
    }


def _decimal_from_fraction(frac: Fraction) -> Decimal:
    # Exact when denominator is 2^a * 5^b (all SI metric powers of 10);
    # falls back to 28-digit Decimal division otherwise.
    return Decimal(frac.numerator) / Decimal(frac.denominator)


def round_half_up_decimals(value: Decimal, decimals: int) -> Decimal:
    quant = Decimal(10) ** (-decimals)
    return value.quantize(quant, rounding=ROUND_HALF_UP)


def round_half_up_sig_figs(value: Decimal, sig_figs: int) -> Decimal:
    if value == 0:
        return Decimal('0')
    adj = value.adjusted()
    decimals = sig_figs - 1 - adj
    if decimals >= 0:
        quant = Decimal(10) ** (-decimals)
        return value.quantize(quant, rounding=ROUND_HALF_UP)
    scale = Decimal(10) ** (-decimals)
    return (value / scale).quantize(Decimal('1'), rounding=ROUND_HALF_UP) * scale


def count_significant_figures(mantissa: str) -> int:
    s = mantissa.strip().lstrip('+-')
    if '.' in s:
        digits = s.replace('.', '').lstrip('0')
        return len(digits) if digits else 1
    digits = s.lstrip('0').rstrip('0')
    return len(digits) if digits else 1


def parse_numeric_literal(raw: Any) -> tuple[Decimal | None, int | None, str | None]:
    """Parse Latvian/ASCII numeric string into (Decimal, sig_figs, error_class)."""
    if raw is None:
        return None, None, 'BLANK_RESPONSE'
    if isinstance(raw, bool):
        return None, None, 'UNREADABLE_INPUT'
    if isinstance(raw, (int, float)):
        text = str(raw)
    elif isinstance(raw, str):
        text = raw.strip()
    else:
        return None, None, 'UNREADABLE_INPUT'

    if not text:
        return None, None, 'BLANK_RESPONSE'

    # Reject NaN, Infinity, code tokens, or mixed comma+dot separators.
    lowered = text.lower()
    if any(tok in lowered for tok in ('nan', 'inf', 'eval', 'function', ';', '=')):
        return None, None, 'UNREADABLE_INPUT'
    if ',' in text and '.' in text:
        return None, None, 'UNREADABLE_INPUT'

    normalized = text.replace('−', '-').replace('\u2212', '-').replace('\u00a0', '').replace(' ', '')

    sci_match = SCI_CROSS_RE.match(normalized)
    if sci_match:
        mant_raw = sci_match.group(1).replace(',', '.')
        exp_raw = sci_match.group(2) or sci_match.group(3).translate(SUPERSCRIPT_MAP)
        try:
            mant_dec = Decimal(mant_raw)
            exp_int = int(exp_raw)
            val = mant_dec * (Decimal(10) ** exp_int)
            return val, count_significant_figures(mant_raw), None
        except (InvalidOperation, ValueError):
            return None, None, 'UNREADABLE_INPUT'

    plain_match = PLAIN_OR_E_RE.match(normalized)
    if plain_match:
        canon = plain_match.group(1).replace(',', '.')
        mant_part = re.split(r'[eE]', canon)[0]
        try:
            val = Decimal(canon)
            if not val.is_finite():
                return None, None, 'UNREADABLE_INPUT'
            return val, count_significant_figures(mant_part), None
        except InvalidOperation:
            return None, None, 'UNREADABLE_INPUT'

    return None, None, 'UNREADABLE_INPUT'


def _norm_unit(unit: str) -> str:
    return ' '.join(unit.strip().split())


def resolve_unit_transform(conventions: dict[str, Any], from_unit: str, to_unit: str) -> tuple[str, Fraction, Fraction]:
    """Return (status, factor, offset) where target = value * factor + offset.

    status is one of: 'ok', 'blocked', 'incompatible'.
    """
    src = _norm_unit(from_unit)
    dst = _norm_unit(to_unit)
    if src == dst:
        return 'ok', Fraction(1, 1), Fraction(0, 1)

    unit_sys = conventions['unit_system']
    # 1. Explicit blocked conversion pairs (e.g. V-04 mg <-> L).
    for conv in unit_sys['conversions']:
        if conv.get('conversion_class') == 'blocked':
            c_from = _norm_unit(conv['from'])
            c_to = _norm_unit(conv['to'])
            if (src == c_from and dst == c_to) or (src == c_to and dst == c_from):
                return 'blocked', Fraction(0, 1), Fraction(0, 1)

    # 2. Direct conversion entries (multiplicative or offset).
    for conv in unit_sys['conversions']:
        if conv.get('conversion_class') == 'blocked':
            continue
        c_from = _norm_unit(conv['from'])
        c_to = _norm_unit(conv['to'])
        if conv.get('conversion_class') == 'offset':
            off = Fraction(conv['offset']['num'], conv['offset']['den'])
            if src == c_from and dst == c_to:
                return 'ok', Fraction(1, 1), off
            if src == c_to and dst == c_from:
                return 'ok', Fraction(1, 1), -off
        else:
            fac = Fraction(conv['factor']['num'], conv['factor']['den'])
            if src == c_from and dst == c_to:
                return 'ok', fac, Fraction(0, 1)
            if src == c_to and dst == c_from:
                return 'ok', Fraction(1, 1) / fac, Fraction(0, 1)

    # 3. Declared numeric composition chains (direct or exact inverse).
    for chain in unit_sys['chains']:
        if chain.get('kind') == 'symbolic':
            continue
        c_from = _norm_unit(chain['from'])
        c_to = _norm_unit(chain['to'])
        fac = Fraction(chain['factor']['num'], chain['factor']['den'])
        off_obj = chain.get('offset') or {'num': 0, 'den': 1}
        off = Fraction(off_obj['num'], off_obj['den'])
        if src == c_from and dst == c_to:
            return 'ok', fac, off
        if src == c_to and dst == c_from and off == 0:
            return 'ok', Fraction(1, 1) / fac, Fraction(0, 1)

    # 4. Two-step BFS over non-offset multiplicative edges in conventions.
    adj: dict[str, list[tuple[str, Fraction]]] = {}
    for conv in unit_sys['conversions']:
        if conv.get('conversion_class') != 'multiplicative':
            continue
        u = _norm_unit(conv['from'])
        v = _norm_unit(conv['to'])
        f = Fraction(conv['factor']['num'], conv['factor']['den'])
        adj.setdefault(u, []).append((v, f))
        adj.setdefault(v, []).append((u, Fraction(1, 1) / f))

    queue: list[tuple[str, Fraction]] = [(src, Fraction(1, 1))]
    visited = {src}
    while queue:
        cur, acc = queue.pop(0)
        for nxt, edge_f in adj.get(cur, []):
            if nxt == dst:
                return 'ok', acc * edge_f, Fraction(0, 1)
            if nxt not in visited:
                visited.add(nxt)
                queue.append((nxt, acc * edge_f))

    return 'incompatible', Fraction(0, 1), Fraction(0, 1)


def get_tolerance_entry(conventions: dict[str, Any], tolerance_class: str) -> dict[str, Any]:
    for entry in conventions['tolerances']['quantity_classes']:
        if entry['id'] == tolerance_class:
            return entry
    raise KeyError(f'Unknown tolerance_class in conventions: {tolerance_class!r}')


def _compute_expected_decimal(payload: dict[str, Any], givens: dict[str, Any], conventions: dict[str, Any]) -> Decimal:
    if 'unrounded_expected' in givens and 'round_mode' in givens:
        raw = Decimal(str(givens['unrounded_expected']))
        rule = conventions['rounding']['rule']
        if rule != 'half_up':
            raise ValueError(f'Unsupported conventions rounding rule: {rule!r}')
        if givens['round_mode'] == 'decimal_places':
            return round_half_up_decimals(raw, int(givens['round_digits']))
        if givens['round_mode'] == 'significant_figures':
            return round_half_up_sig_figs(raw, int(givens['round_digits']))
    return Decimal(str(payload['expected_value']))


def _grade_numeric_value(
    submitted_raw: Any,
    submitted_unit: str,
    expected_dec: Decimal,
    target_unit: str,
    tolerance_class: str,
    expected_sig_figs: int | None,
    givens: dict[str, Any],
    conventions: dict[str, Any],
) -> dict[str, Any]:
    val_dec, parsed_sf, parse_err = parse_numeric_literal(submitted_raw)
    if parse_err is not None or val_dec is None:
        return {'ok': False, 'error_class': parse_err or 'UNREADABLE_INPUT', 'sig_figs_ok': False}

    # Check percentage basis rule (N03 percentage_basis / V-02).
    if givens.get('requires_explicit_basis'):
        u_norm = _norm_unit(submitted_unit)
        pct_cfg = conventions['percentage_basis']
        if u_norm == '%' and pct_cfg.get('unlabeled_percent') == 'withhold scoring':
            return {'ok': False, 'error_class': 'UNLABELED_PERCENT_BASIS', 'sig_figs_ok': False}

    status, factor, offset = resolve_unit_transform(conventions, submitted_unit, target_unit)
    if status in ('blocked', 'incompatible'):
        return {'ok': False, 'error_class': 'DIMENSIONAL_INCONSISTENCY', 'sig_figs_ok': False}

    converted = val_dec * _decimal_from_fraction(factor) + _decimal_from_fraction(offset)
    tol_entry = get_tolerance_entry(conventions, tolerance_class)
    abs_tol = Decimal(str(tol_entry['absolute']['value']))

    diff = abs(converted - expected_dec)
    within_tol = diff <= abs_tol
    sig_figs_ok = True if expected_sig_figs is None else (parsed_sf == expected_sig_figs)

    if within_tol:
        return {
            'ok': True,
            'error_class': 'NONE',
            'converted_value': str(converted),
            'abs_diff': str(diff),
            'tolerance_used': str(abs_tol),
            'sig_figs_ok': sig_figs_ok,
        }

    # V-04 density-defect diagnosis: off by declared density factor rho.
    if 'density_g_per_ml' in givens and 'density_defect_op' in givens:
        rho = Decimal(str(givens['density_g_per_ml']))
        defect_expected = expected_dec / rho if givens['density_defect_op'] == 'divide' else expected_dec * rho
        if abs(converted - defect_expected) <= abs_tol:
            return {
                'ok': False,
                'error_class': 'DIMENSIONAL_INCONSISTENCY',
                'converted_value': str(converted),
                'abs_diff': str(diff),
                'tolerance_used': str(abs_tol),
                'sig_figs_ok': sig_figs_ok,
            }

    return {
        'ok': False,
        'error_class': 'OUT_OF_TOLERANCE',
        'converted_value': str(converted),
        'abs_diff': str(diff),
        'tolerance_used': str(abs_tol),
        'sig_figs_ok': sig_figs_ok,
    }


def _check_ordering(submitted: list[str], correct: list[str], partial_rules: list[dict[str, Any]] | None) -> bool:
    if len(submitted) != len(correct) or set(submitted) != set(correct):
        return False
    free_groups: list[set[str]] = []
    for rule in partial_rules or []:
        if isinstance(rule, dict) and rule.get('type') == 'free_order_group':
            free_groups.append(set(rule.get('item_ids', [])))

    for s_item, c_item in zip(submitted, correct):
        if s_item == c_item:
            continue
        in_same_free = any(s_item in grp and c_item in grp for grp in free_groups)
        if not in_same_free:
            return False
    return True


def grade_vector(instance: dict[str, Any], submission: dict[str, Any], conventions: dict[str, Any],
                 conventions_digest: str | None = None, oracle_digest: str | None = None) -> dict[str, Any]:
    """Grade one frozen instance + submission directly against conventions."""
    payload_class = instance['payload_class']
    payload = instance['payload']
    givens = instance.get('givens') or {}
    rubric = instance['rubric']

    auto_items = [r for r in rubric if r['grading'] in ('auto', 'mixed') and r['engine_binding'] not in ('self-assessed', 'human-review')]
    pending_items = [r for r in rubric if r not in auto_items]

    awarded_criteria: list[dict[str, Any]] = []
    machine_points = Decimal('0')
    pending_points = Decimal('0')
    max_points = Decimal('0')
    primary_error = 'NONE'

    for item in pending_items:
        pts = Decimal(str(item['points']))
        max_points += pts
        pending_points += pts
        awarded_criteria.append({
            'criterion_id': item['criterion_id'],
            'status': 'pending',
            'awarded_points': 0.0,
            'pending_points': float(pts),
            'max_points': float(pts),
        })

    if payload_class == 'numeric':
        expected_dec = _compute_expected_decimal(payload, givens, conventions)
        raw_val = submission.get('value')
        sub_unit = submission.get('unit', payload['unit'])
        res = _grade_numeric_value(
            submitted_raw=raw_val,
            submitted_unit=sub_unit,
            expected_dec=expected_dec,
            target_unit=payload['unit'],
            tolerance_class=payload['tolerance_class'],
            expected_sig_figs=payload.get('sig_figs'),
            givens=givens,
            conventions=conventions,
        )
        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            if item['criterion_id'].endswith('_SIGFIG'):
                passed = bool(res.get('ok') and res.get('sig_figs_ok'))
            else:
                passed = bool(res.get('ok'))
            awarded = pts if passed else Decimal('0')
            machine_points += awarded
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'awarded' if passed else 'denied',
                'awarded_points': float(awarded),
                'pending_points': 0.0,
                'max_points': float(pts),
            })
        if not res['ok']:
            primary_error = res['error_class']
        elif any(c['status'] == 'denied' for c in awarded_criteria):
            primary_error = 'SIG_FIG_MISMATCH'

    elif payload_class == 'graph':
        tr = payload['target_readout']
        xs = [Decimal(str(p['x'])) for p in payload['points']]
        x_min, x_max = min(xs), max(xs)
        out_of_span = False
        if 'x' in submission and submission['x'] is not None:
            x_dec, _, x_err = parse_numeric_literal(submission['x'])
            if x_err is not None or x_dec is None:
                primary_error = x_err or 'UNREADABLE_INPUT'
                out_of_span = True
            elif x_dec < x_min or x_dec > x_max:
                primary_error = 'OUT_OF_DOMAIN_EXTRAPOLATION'
                out_of_span = True

        if out_of_span:
            res_ok = False
        else:
            expected_dec = Decimal(str(tr['expected_value']))
            res = _grade_numeric_value(
                submitted_raw=submission.get('value'),
                submitted_unit=submission.get('unit', tr['unit']),
                expected_dec=expected_dec,
                target_unit=tr['unit'],
                tolerance_class=tr['tolerance_class'],
                expected_sig_figs=None,
                givens=givens,
                conventions=conventions,
            )
            res_ok = bool(res['ok'])
            if not res_ok:
                primary_error = res['error_class']

        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            awarded = pts if res_ok else Decimal('0')
            machine_points += awarded
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'awarded' if res_ok else 'denied',
                'awarded_points': float(awarded),
                'pending_points': 0.0,
                'max_points': float(pts),
            })

    elif payload_class == 'option_select':
        selected = submission.get('selected_ids')
        if not selected:
            primary_error = 'BLANK_RESPONSE'
            matched = False
        else:
            matched = set(selected) == set(payload['correct_ids']) and len(selected) == len(set(selected))
            if not matched:
                primary_error = 'WRONG_OPTION_SELECTION'
        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            awarded = pts if matched else Decimal('0')
            machine_points += awarded
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'awarded' if matched else 'denied',
                'awarded_points': float(awarded),
                'pending_points': 0.0,
                'max_points': float(pts),
            })

    elif payload_class == 'ordering':
        order = submission.get('order')
        if not order:
            primary_error = 'BLANK_RESPONSE'
            matched = False
        else:
            matched = _check_ordering(order, payload['correct_order'], payload.get('partial_order_rules'))
            if not matched:
                primary_error = 'WRONG_ORDER'
        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            awarded = pts if matched else Decimal('0')
            machine_points += awarded
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'awarded' if matched else 'denied',
                'awarded_points': float(awarded),
                'pending_points': 0.0,
                'max_points': float(pts),
            })

    elif payload_class == 'matching':
        pairs = submission.get('pairs')
        if not pairs:
            primary_error = 'BLANK_RESPONSE'
            pair_map: dict[str, str] = {}
            duplicate_left = False
        else:
            pair_map = {}
            duplicate_left = False
            for p in pairs:
                lid = p.get('left_id')
                rid = p.get('right_id')
                if lid in pair_map:
                    duplicate_left = True
                pair_map[lid] = rid
        expected_map = {p['left_id']: p['right_id'] for p in payload['correct_pairs']}
        all_matched = (not duplicate_left) and (pair_map == expected_map)

        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            cid = item['criterion_id']
            # Support per-pair criterion IDs like C1_L1 as well as whole-matching C1_MATCH.
            if '_PAIR_' in cid:
                left_id = cid.split('_PAIR_', 1)[1]
                passed = (not duplicate_left) and (pair_map.get(left_id) == expected_map.get(left_id))
            else:
                passed = all_matched
            awarded = pts if passed else Decimal('0')
            machine_points += awarded
            awarded_criteria.append({
                'criterion_id': cid,
                'status': 'awarded' if passed else 'denied',
                'awarded_points': float(awarded),
                'pending_points': 0.0,
                'max_points': float(pts),
            })
        if pairs and not all_matched:
            primary_error = 'WRONG_PAIRING'

    elif payload_class == 'method':
        # Self-assessed / pending method items: never parse free text or match keywords.
        text_val = submission.get('text')
        if pending_items and not auto_items:
            if isinstance(text_val, str) and text_val.strip() == '':
                primary_error = 'BLANK_RESPONSE'
                # Blank response earns zero (even self-assessed blank has 0 pending).
                pending_points = Decimal('0')
                for c in awarded_criteria:
                    c['status'] = 'denied'
                    c['pending_points'] = 0.0
        for item in auto_items:
            pts = Decimal(str(item['points']))
            max_points += pts
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'denied',
                'awarded_points': 0.0,
                'pending_points': 0.0,
                'max_points': float(pts),
            })
    else:
        raise ValueError(f'Unsupported payload_class for oracle: {payload_class!r}')

    awarded_criteria.sort(key=lambda c: c['criterion_id'])
    auto_max = sum(Decimal(str(r['points'])) for r in auto_items)
    if not auto_items and pending_items:
        verdict_class = 'incorrect' if primary_error == 'BLANK_RESPONSE' else 'pending_self_assessment'
    elif machine_points == auto_max and auto_max > 0:
        verdict_class = 'auto_passed_pending_review' if pending_items else 'correct'
    elif machine_points > 0:
        verdict_class = 'partial'
    else:
        verdict_class = 'incorrect'

    c_dig = conventions_digest or sha256_canonical(conventions)
    o_dig = oracle_digest or sha256_file(Path(__file__).resolve())
    return {
        'verdict_class': verdict_class,
        'error_class': primary_error,
        'awarded_criteria': awarded_criteria,
        'machine_checked_points': float(machine_points),
        'self_assessed_points': 0.0,
        'human_reviewed_points': 0.0,
        'pending_points': float(pending_points),
        'max_points': float(max_points),
        'oracle_version': ORACLE_VERSION,
        'oracle_digest': o_dig,
        'conventions_digest': c_dig,
    }


def grade_corpus(vectors_doc: dict[str, Any], conventions: dict[str, Any]) -> dict[str, Any]:
    c_dig = sha256_canonical(conventions)
    o_dig = sha256_file(Path(__file__).resolve())
    results = []
    for vec in vectors_doc.get('vectors', []):
        if vec.get('status') == 'retired':
            continue
        verdict = grade_vector(
            instance=vec['instance'],
            submission=vec['submission'],
            conventions=conventions,
            conventions_digest=c_dig,
            oracle_digest=o_dig,
        )
        results.append({
            'vector_id': vec['vector_id'],
            'verdict': verdict,
        })
    return {
        'schema_version': 1,
        'oracle_version': ORACLE_VERSION,
        'oracle_digest': o_dig,
        'conventions_digest': c_dig,
        'graded_count': len(results),
        'results': results,
        'results_sha256': sha256_canonical(results),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vectors', default=str(REPO_ROOT / 'data/golden_vectors.json'))
    parser.add_argument('--conventions', default=str(DEFAULT_CONVENTIONS_PATH))
    parser.add_argument('--manifest', action='store_true', help='Print import manifest JSON')
    parser.add_argument('--json', action='store_true', help='Print oracle grading JSON')
    args = parser.parse_args(argv)

    if args.manifest:
        print(json.dumps(verify_import_manifest(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    conventions = json.loads(Path(args.conventions).read_text(encoding='utf-8'))
    vectors_doc = json.loads(Path(args.vectors).read_text(encoding='utf-8'))
    out = grade_corpus(vectors_doc, conventions)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f'PASS oracle: {out["graded_count"]} vectors graded, results_sha256={out["results_sha256"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
