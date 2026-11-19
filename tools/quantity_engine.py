#!/usr/bin/env python3
"""N17 quantity / conservation engines and four-class error taxonomy (Python twin).

This is the authoring twin of src/quantity-engine.js. It consumes data/conventions.json
and data/engine_taxonomy.json exclusively: every mass, constant, conversion factor,
tolerance and plausibility bound is read from those islands at load time. The module
contains no local copy of a scientific constant, and ``no_local_constants`` proves it.

The oracle in tools/golden_oracle.py shares no code with this module. Agreement with
the frozen N05 corpus is evidence, not tautology.
"""
from __future__ import annotations

import ast
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

TAXONOMY_PATH = 'data/engine_taxonomy.json'
CONVENTIONS_PATH = 'data/conventions.json'
TERMS_PATH = 'data/terms.json'
ORACLE_EXPECTED_FIELDS = (
    'verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
    'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points',
    'oracle_version', 'oracle_digest', 'conventions_digest',
)

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
NUMBER_TOKEN_RE = re.compile(r'(?<![\w.])\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?![\w.])')


class EngineError(ValueError):
    """A named failure with a taxonomy class, signature and feedback key."""

    def __init__(self, code: str, message: str, *, signature: str = '', feedback_key: str = '',
                 n05_error: str = '', detail: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.signature = signature
        self.feedback_key = feedback_key
        self.n05_error = n05_error
        self.detail = detail or {}

    def as_dict(self) -> dict[str, Any]:
        return {
            'code': self.code, 'message': str(self), 'signature': self.signature,
            'feedback_key': self.feedback_key, 'n05_error': self.n05_error,
            'detail': self.detail,
        }


class Engine:
    """Single conventions-consuming calculation authority."""

    def __init__(self, conventions: dict[str, Any], taxonomy: dict[str, Any],
                 terms: dict[str, Any] | None = None) -> None:
        self.conventions = conventions
        self.taxonomy = taxonomy
        self.terms = terms or {}
        self.errors: list[dict[str, Any]] = taxonomy['error_taxonomy']['classes']
        self.by_error = {e['id']: e for e in self.errors}
        self.rank = {e['id']: int(e['rank']) for e in self.errors}
        self.n05_map: dict[str, tuple[str, str, str]] = {}
        for entry in self.errors:
            for n05 in entry['n05_error_classes']:
                self.n05_map[n05] = (entry['id'], entry['signature'], entry['feedback_key'])
        self.fallback = taxonomy['error_taxonomy']['fallback']
        self.plausibility = {r['id']: r for r in taxonomy['plausibility_rules']}
        self.domain_rules = {r['id']: r for r in taxonomy['domain_rules']}
        self.grammar = self.terms.get('unit_grammar') or {}
        self.term_by_key = {t['key']: t for t in self.terms.get('terms', [])}
        self.ledger: list[dict[str, Any]] = []
        self._assert_consumption()

    # ------------------------------------------------------------------ setup
    def _assert_consumption(self) -> None:
        for path in self.taxonomy['conventions_consumption']['paths']:
            node: Any = self.conventions
            for part in path.split('.'):
                if isinstance(node, dict) and part in node:
                    node = node[part]
                elif isinstance(node, list) and part.isdigit() and int(part) < len(node):
                    node = node[int(part)]
                else:
                    raise EngineError('UNREADABLE_INPUT', f'Conventions path did not resolve: {path}')
        if not self.grammar.get('elements'):
            # The grammar may be supplied by the runtime term island; the Python
            # twin also carries a minimal element table parsed from the same island
            # when load() is used. Direct construction without terms is allowed.
            self.grammar = {'elements': [], 'dimensions': {}, 'dimensionless_tokens': []}

    # --------------------------------------------------------------- dimensions
    def _normalize_exponent(self, token: str) -> int:
        if not token:
            return 1
        translated = token.translate(SUPERSCRIPT_MAP)
        if translated and (translated.isdigit() or (translated.startswith('-') and translated[1:].isdigit())):
            return int(translated)
        if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
            return int(token)
        raise EngineError('UNREADABLE_INPUT', f'Unreadable unit exponent: {token!r}')

    def parse_unit(self, unit: str | None) -> dict[str, int]:
        """Parse an N10-grammar unit expression into a dimension-exponent vector."""
        if unit is None or str(unit).strip() == '':
            raise EngineError('UNREADABLE_INPUT', 'Missing unit expression.')
        dims = self.grammar.get('dimensions') or {}
        tokens = self.grammar.get('elements') or []
        if not tokens:
            raise EngineError('UNREADABLE_INPUT', 'Unit grammar elements unavailable in #sim-terms.')
        symbol_to_dim: dict[str, dict[str, int]] = {
            str(t['symbol']): dict(t['dimension_vector']) for t in tokens
        }
        symbols = sorted(symbol_to_dim, key=len, reverse=True)
        dimensionless = set(self.grammar.get('dimensionless_tokens') or [])
        raw = ' '.join(str(unit).strip().split()).replace('×', '·').replace('*', '·')
        if raw in dimensionless:
            return {}
        # Leading parenthesised whole expression is not part of the declared grammar;
        # only grouped denominators are supported.
        if raw.count('(') or raw.count(')'):
            if raw.count('(') != 1 or raw.count(')') != 1 or '(' not in raw or ')' not in raw:
                raise EngineError('UNREADABLE_INPUT', f'Unsupported unit grouping: {unit!r}')
            left, rest = raw.split('(', 1)
            group, right = rest.split(')', 1)
            if '/' not in left:
                raise EngineError('UNREADABLE_INPUT', f'Unsupported unit grouping: {unit!r}')
            numerator = left.split('/', 1)[0].strip()
            denominator = group.strip() + ' ' + right.strip()
        elif '/' in raw:
            numerator, denominator = raw.split('/', 1)
        else:
            numerator, denominator = raw, ''

        result: dict[str, int] = {}

        def absorb(expr: str, sign: int) -> None:
            parts = [p.strip() for p in expr.split('·') if p.strip()]
            if not parts:
                raise EngineError('UNREADABLE_INPUT', f'Empty unit factor in {unit!r}')
            for part in parts:
                symbol = part
                exponent = 1
                m = re.match(r'^(.*?)\^([+-]?\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)$', part)
                if m:
                    symbol = m.group(1).strip()
                    exponent = self._normalize_exponent(m.group(2))
                else:
                    m = re.match(r'^(.*?)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)$', part)
                    if m and m.group(1) in symbol_to_dim:
                        symbol = m.group(1)
                        exponent = self._normalize_exponent(m.group(2))
                if symbol in dimensionless:
                    continue
                found = next((s for s in symbols if symbol == s), None)
                if found is None:
                    raise EngineError('UNREADABLE_INPUT', f'Unknown unit symbol: {symbol!r}')
                for dim, power in symbol_to_dim[found].items():
                    result[dim] = result.get(dim, 0) + sign * exponent * int(power)

        absorb(numerator, 1)
        if denominator.strip():
            absorb(denominator, -1)
        return {k: v for k, v in result.items() if v != 0}

    @staticmethod
    def dim_key(dimension: dict[str, int]) -> tuple[tuple[str, int], ...]:
        return tuple(sorted((k, v) for k, v in dimension.items() if v != 0))

    # -------------------------------------------------------------- quantities
    class Quantity:
        def __init__(self, value: Decimal, unit: str, dimension: dict[str, int], sig_figs: int | None,
                     ledger: list[dict[str, Any]] | None = None) -> None:
            self.value = value
            self.unit = unit
            self.dimension = dimension
            self.sig_figs = sig_figs
            self.ledger = ledger if ledger is not None else []

        def as_dict(self) -> dict[str, Any]:
            return {
                'value': str(self.value), 'unit': self.unit,
                'dimension': self.dim_key(self.dimension),
                'sig_figs': self.sig_figs, 'ledger': list(self.ledger),
            }

    def quantity(self, value: Any, unit: str, sig_figs: int | None = None) -> Quantity:
        dec, parsed_sf, err = self.parse_numeric(value)
        if err:
            raise self._error_for(err, detail={'raw': value, 'unit': unit})
        dimension = self.parse_unit(unit)
        return self.Quantity(dec, ' '.join(str(unit).split()), dimension,
                             sig_figs if sig_figs is not None else parsed_sf)

    def _error_for(self, n05_error: str, detail: dict[str, Any] | None = None,
                   signature: str | None = None, feedback_key: str | None = None) -> EngineError:
        mapped = self.n05_map.get(n05_error)
        class_id, sig, key = mapped if mapped else (
            self.fallback.get('code', 'UNREADABLE_INPUT'),
            signature or self.fallback['signature'],
            feedback_key or self.fallback['feedback_key'],
        )
        return EngineError(class_id, f'{n05_error}: calculation refused by the dimension gate',
                           signature=signature or sig, feedback_key=feedback_key or key,
                           n05_error=n05_error, detail=detail)

    def _record(self, operation: str, inputs: list[str], outputs: list[str]) -> None:
        self.ledger.append({'operation': operation, 'inputs': inputs, 'outputs': outputs})

    def add(self, a: Quantity, b: Quantity) -> Quantity:
        if self.dim_key(a.dimension) != self.dim_key(b.dimension):
            err = self._error_for('DIMENSIONAL_INCONSISTENCY', {
                'left': self.dim_key(a.dimension), 'right': self.dim_key(b.dimension), 'operation': 'add'})
            raise err
        if a.unit != b.unit:
            b = self.convert(b, a.unit)
        self._record('add', [f'{a.value} {a.unit}', f'{b.value} {b.unit}'],
                     [f'{a.value + b.value} {a.unit}'])
        return self.Quantity(a.value + b.value, a.unit, dict(a.dimension), min(a.sig_figs or 99, b.sig_figs or 99))

    def multiply(self, a: Quantity, b: Quantity) -> Quantity:
        dim = dict(a.dimension)
        for k, v in b.dimension.items():
            dim[k] = dim.get(k, 0) + v
        self._record('multiply', [f'{a.value} {a.unit}', f'{b.value} {b.unit}'], [f'{a.value * b.value} {a.unit}·{b.unit}'])
        return self.Quantity(a.value * b.value, f'{a.unit}·{b.unit}', dim, min(a.sig_figs or 99, b.sig_figs or 99))

    def divide(self, a: Quantity, b: Quantity) -> Quantity:
        dim = dict(a.dimension)
        for k, v in b.dimension.items():
            dim[k] = dim.get(k, 0) - v
        if b.value == 0:
            raise self._error_for('PHYSICALLY_IMPLAUSIBLE', {'operation': 'divide', 'divisor': '0'})
        self._record('divide', [f'{a.value} {a.unit}', f'{b.value} {b.unit}'], [f'{a.value / b.value} {a.unit}/{b.unit}'])
        return self.Quantity(a.value / b.value, f'{a.unit}/{b.unit}', dim, min(a.sig_figs or 99, b.sig_figs or 99))

    def dimension_gate(self, quantities: list[Quantity], expected_dimension: str | None = None) -> dict[str, Any]:
        keys = [self.dim_key(q.dimension) for q in quantities]
        if expected_dimension:
            want = self.dim_key(self.parse_unit(expected_dimension))
            if any(k != want for k in keys):
                raise self._error_for('DIMENSIONAL_INCONSISTENCY', {
                    'expected': want, 'actual': keys, 'operation': 'gate'})
        if len(set(keys)) > 1:
            raise self._error_for('DIMENSIONAL_INCONSISTENCY', {
                'actual': keys, 'operation': 'gate'})
        entry = {'operation': 'dimension_gate', 'dimensions': keys, 'status': 'CLOSED'}
        self.ledger.append(entry)
        return entry

    def resolve_unit_transform(self, from_unit: str, to_unit: str) -> tuple[str, Fraction, Fraction]:
        src, dst = ' '.join(from_unit.split()), ' '.join(to_unit.split())
        if src == dst:
            return 'ok', Fraction(1, 1), Fraction(0, 1)
        system = self.conventions['unit_system']
        for conv in system['conversions']:
            if conv.get('conversion_class') != 'blocked':
                continue
            a, b = ' '.join(conv['from'].split()), ' '.join(conv['to'].split())
            if (src, dst) in ((a, b), (b, a)):
                return 'blocked', Fraction(0, 1), Fraction(0, 1)
        for conv in system['conversions']:
            if conv.get('conversion_class') == 'blocked':
                continue
            a, b = ' '.join(conv['from'].split()), ' '.join(conv['to'].split())
            if conv.get('conversion_class') == 'offset':
                off = Fraction(conv['offset']['num'], conv['offset']['den'])
                if (src, dst) == (a, b):
                    return 'ok', Fraction(1, 1), off
                if (src, dst) == (b, a):
                    return 'ok', Fraction(1, 1), -off
            else:
                factor = Fraction(conv['factor']['num'], conv['factor']['den'])
                if (src, dst) == (a, b):
                    return 'ok', factor, Fraction(0, 1)
                if (src, dst) == (b, a):
                    return 'ok', Fraction(1, 1) / factor, Fraction(0, 1)
        for chain in system['chains']:
            if chain.get('kind') == 'symbolic':
                continue
            if not chain.get('factor'):
                continue
            a, b = ' '.join(chain['from'].split()), ' '.join(chain['to'].split())
            factor = Fraction(chain['factor']['num'], chain['factor']['den'])
            off_obj = chain.get('offset') or {'num': 0, 'den': 1}
            off = Fraction(off_obj['num'], off_obj['den'])
            if (src, dst) == (a, b):
                return 'ok', factor, off
            if (src, dst) == (b, a) and off == 0:
                return 'ok', Fraction(1, 1) / factor, Fraction(0, 1)
        adjacency: dict[str, list[tuple[str, Fraction]]] = {}
        for conv in system['conversions']:
            if conv.get('conversion_class') != 'multiplicative':
                continue
            a, b = ' '.join(conv['from'].split()), ' '.join(conv['to'].split())
            factor = Fraction(conv['factor']['num'], conv['factor']['den'])
            adjacency.setdefault(a, []).append((b, factor))
            adjacency.setdefault(b, []).append((a, Fraction(1, 1) / factor))
        queue: list[tuple[str, Fraction]] = [(src, Fraction(1, 1))]
        visited = {src}
        while queue:
            current, acc = queue.pop(0)
            for nxt, edge in adjacency.get(current, []):
                if nxt == dst:
                    return 'ok', acc * edge, Fraction(0, 1)
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, acc * edge))
        return 'incompatible', Fraction(0, 1), Fraction(0, 1)

    def _fraction_decimal(self, fraction: Fraction) -> Decimal:
        return Decimal(fraction.numerator) / Decimal(fraction.denominator)

    def convert(self, quantity: Quantity, to_unit: str) -> Quantity:
        status, factor, offset = self.resolve_unit_transform(quantity.unit, to_unit)
        if status in ('blocked', 'incompatible'):
            raise self._error_for('DIMENSIONAL_INCONSISTENCY', {
                'from': quantity.unit, 'to': to_unit, 'status': status})
        value = quantity.value * self._fraction_decimal(factor) + self._fraction_decimal(offset)
        entry = {
            'operation': 'convert', 'from': quantity.unit, 'to': to_unit,
            'factor': f'{factor.numerator}/{factor.denominator}',
            'offset': f'{offset.numerator}/{offset.denominator}',
            'input_dimension': self.dim_key(quantity.dimension),
            'output_dimension': self.parse_unit(to_unit) and self.dim_key(self.parse_unit(to_unit)),
        }
        if self.dim_key(quantity.dimension) != self.dim_key(self.parse_unit(to_unit)):
            raise self._error_for('DIMENSIONAL_INCONSISTENCY', {'conversion': entry})
        self._record('convert', [f'{quantity.value} {quantity.unit}'], [f'{value} {to_unit}'])
        return self.Quantity(value, to_unit, self.parse_unit(to_unit), quantity.sig_figs,
                             quantity.ledger + [entry])

    # ------------------------------------------------------------------ parsing
    @staticmethod
    def count_sig_figs(mantissa: str) -> int:
        s = mantissa.strip().lstrip('+-')
        if '.' in s:
            digits = s.replace('.', '').lstrip('0')
            return len(digits) if digits else 1
        digits = s.lstrip('0').rstrip('0')
        return len(digits) if digits else 1

    def parse_numeric(self, raw: Any) -> tuple[Decimal | None, int | None, str | None]:
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
        lowered = text.lower()
        if any(tok in lowered for tok in ('nan', 'inf', 'eval', 'function', ';', '=')):
            return None, None, 'UNREADABLE_INPUT'
        if ',' in text and '.' in text:
            return None, None, 'UNREADABLE_INPUT'
        normalized = text.replace('−', '-').replace('\u2212', '-').replace('\u00a0', '').replace(' ', '')
        sci = SCI_CROSS_RE.match(normalized)
        if sci:
            mant = sci.group(1).replace(',', '.')
            exp_raw = sci.group(2) or sci.group(3).translate(SUPERSCRIPT_MAP)
            try:
                value = Decimal(mant) * (Decimal(10) ** int(exp_raw))
                return value, self.count_sig_figs(mant), None
            except (InvalidOperation, ValueError):
                return None, None, 'UNREADABLE_INPUT'
        plain = PLAIN_OR_E_RE.match(normalized)
        if plain:
            canon = plain.group(1).replace(',', '.')
            mant = re.split(r'[eE]', canon)[0]
            try:
                value = Decimal(canon)
                if not value.is_finite():
                    return None, None, 'UNREADABLE_INPUT'
                return value, self.count_sig_figs(mant), None
            except InvalidOperation:
                return None, None, 'UNREADABLE_INPUT'
        return None, None, 'UNREADABLE_INPUT'

    @staticmethod
    def round_half_up(value: Decimal, digits: int, mode: str) -> Decimal:
        if mode == 'decimal_places':
            quant = Decimal(10) ** (-digits)
            return value.quantize(quant, rounding=ROUND_HALF_UP)
        if value == 0:
            return Decimal('0')
        decimals = digits - 1 - value.adjusted()
        quant = Decimal(10) ** (-decimals)
        return value.quantize(quant, rounding=ROUND_HALF_UP)

    # ----------------------------------------------------------------- grading
    def _expected_decimal(self, payload: dict[str, Any], givens: dict[str, Any]) -> Decimal:
        if 'unrounded_expected' in givens and 'round_mode' in givens:
            raw = Decimal(str(givens['unrounded_expected']))
            mode = givens['round_mode']
            if mode == 'decimal_places':
                return self.round_half_up(raw, int(givens['round_digits']), mode)
            if mode == 'significant_figures':
                return self.round_half_up(raw, int(givens['round_digits']), mode)
        return Decimal(str(payload['expected_value']))

    def _tolerance(self, tolerance_class: str) -> Decimal:
        for entry in self.conventions['tolerances']['quantity_classes']:
            if entry['id'] == tolerance_class:
                return Decimal(str(entry['absolute']['value']))
        raise self._error_for('UNREADABLE_INPUT', {'tolerance_class': tolerance_class})

    def grade_numeric(self, payload: dict[str, Any], givens: dict[str, Any],
                      submission: dict[str, Any], expected: Decimal,
                      expected_sig_figs: int | None) -> dict[str, Any]:
        raw = submission.get('value')
        submitted_unit = submission.get('unit', payload['unit'])
        value, sig_figs, parse_err = self.parse_numeric(raw)
        if parse_err or value is None:
            return {'ok': False, 'error_class': parse_err or 'UNREADABLE_INPUT', 'sig_figs_ok': False}
        if givens.get('requires_explicit_basis') and ' '.join(submitted_unit.split()) == '%':
            cfg = self.conventions['percentage_basis']
            if cfg.get('unlabeled_percent') == 'withhold scoring':
                return {'ok': False, 'error_class': 'UNLABELED_PERCENT_BASIS', 'sig_figs_ok': False}
        try:
            status, factor, offset = self.resolve_unit_transform(submitted_unit, payload['unit'])
        except EngineError:
            return {'ok': False, 'error_class': 'DIMENSIONAL_INCONSISTENCY', 'sig_figs_ok': False}
        if status in ('blocked', 'incompatible'):
            return {'ok': False, 'error_class': 'DIMENSIONAL_INCONSISTENCY', 'sig_figs_ok': False}
        converted = value * self._fraction_decimal(factor) + self._fraction_decimal(offset)
        abs_tol = self._tolerance(payload['tolerance_class'])
        diff = abs(converted - expected)
        sf_ok = True if expected_sig_figs is None else sig_figs == expected_sig_figs
        result = {
            'converted_value': str(converted), 'abs_diff': str(diff),
            'tolerance_used': str(abs_tol), 'sig_figs_ok': sf_ok,
            'tolerance_source': f"tolerances.quantity_classes[id={payload['tolerance_class']}]",
        }
        if diff <= abs_tol:
            result.update({'ok': True, 'error_class': 'NONE'})
            return result
        if 'density_g_per_ml' in givens and 'density_defect_op' in givens:
            rho = Decimal(str(givens['density_g_per_ml']))
            defect = expected / rho if givens['density_defect_op'] == 'divide' else expected * rho
            if abs(converted - defect) <= abs_tol:
                result.update({'ok': False, 'error_class': 'DIMENSIONAL_INCONSISTENCY'})
                return result
        result.update({'ok': False, 'error_class': 'OUT_OF_TOLERANCE'})
        return result

    def grade(self, instance: dict[str, Any], submission: dict[str, Any],
              oracle_version: str = '1.0.0', oracle_digest: str = '',
              conventions_digest: str | None = None) -> dict[str, Any]:
        payload_class = instance['payload_class']
        payload = instance['payload']
        givens = instance.get('givens') or {}
        rubric = instance['rubric']
        auto = [r for r in rubric if r['grading'] in ('auto', 'mixed')
                and r['engine_binding'] not in ('self-assessed', 'human-review')]
        pending = [r for r in rubric if r not in auto]
        criteria: list[dict[str, Any]] = []
        machine = Decimal('0')
        pending_points = Decimal('0')
        maximum = Decimal('0')
        primary = 'NONE'

        for item in pending:
            pts = Decimal(str(item['points']))
            maximum += pts
            pending_points += pts
            criteria.append({'criterion_id': item['criterion_id'], 'status': 'pending',
                             'awarded_points': 0.0, 'pending_points': float(pts), 'max_points': float(pts)})

        if payload_class in ('numeric', 'graph'):
            if payload_class == 'graph':
                target = payload['target_readout']
                xs = [Decimal(str(p['x'])) for p in payload['points']]
                xmin, xmax = min(xs), max(xs)
                outside = False
                if submission.get('x') is not None:
                    x_val, _, x_err = self.parse_numeric(submission['x'])
                    if x_err:
                        primary, outside = x_err, True
                    elif x_val < xmin or x_val > xmax:
                        primary, outside = 'OUT_OF_DOMAIN_EXTRAPOLATION', True
                effective_submission = submission if outside else {
                    'value': submission.get('value'), 'unit': submission.get('unit', target['unit'])}
                if outside:
                    res = {'ok': False, 'error_class': primary}
                else:
                    res = self.grade_numeric(target, givens, effective_submission,
                                             Decimal(str(target['expected_value'])), None)
                used_payload = target
            else:
                used_payload = payload
                res = self.grade_numeric(payload, givens, submission,
                                         self._expected_decimal(payload, givens), payload.get('sig_figs'))
            if not res['ok']:
                primary = res['error_class']
            for item in auto:
                pts = Decimal(str(item['points']))
                maximum += pts
                if item['criterion_id'].endswith('_SIGFIG'):
                    passed = bool(res.get('ok') and res.get('sig_figs_ok'))
                else:
                    passed = bool(res.get('ok'))
                awarded = pts if passed else Decimal('0')
                machine += awarded
                criteria.append({'criterion_id': item['criterion_id'],
                                 'status': 'awarded' if passed else 'denied',
                                 'awarded_points': float(awarded), 'pending_points': 0.0,
                                 'max_points': float(pts)})
            if res['ok'] and any(c['status'] == 'denied' for c in criteria):
                primary = 'SIG_FIG_MISMATCH'

        elif payload_class == 'option_select':
            selected = submission.get('selected_ids')
            matched = bool(selected) and set(selected) == set(payload['correct_ids']) and len(selected) == len(set(selected))
            if not selected:
                primary = 'BLANK_RESPONSE'
            elif not matched:
                primary = 'WRONG_OPTION_SELECTION'
            machine, maximum = self._structural_criteria(criteria, auto, matched, machine, maximum)
        elif payload_class == 'ordering':
            order = submission.get('order')
            matched = bool(order) and self._check_order(order, payload['correct_order'], payload.get('partial_order_rules'))
            if not order:
                primary = 'BLANK_RESPONSE'
            elif not matched:
                primary = 'WRONG_ORDER'
            machine, maximum = self._structural_criteria(criteria, auto, matched, machine, maximum)
        elif payload_class == 'matching':
            pairs = submission.get('pairs')
            pair_map: dict[str, str] = {}
            duplicate = False
            for pair in pairs or []:
                lid = pair.get('left_id')
                if lid in pair_map:
                    duplicate = True
                pair_map[lid] = pair.get('right_id')
            expected_map = {p['left_id']: p['right_id'] for p in payload['correct_pairs']}
            all_matched = (not duplicate) and pair_map == expected_map
            if not pairs:
                primary = 'BLANK_RESPONSE'
            elif not all_matched:
                primary = 'WRONG_PAIRING'
            for item in auto:
                pts = Decimal(str(item['points']))
                maximum += pts
                cid = item['criterion_id']
                if '_PAIR_' in cid:
                    left = cid.split('_PAIR_', 1)[1]
                    passed = (not duplicate) and pair_map.get(left) == expected_map.get(left)
                else:
                    passed = all_matched
                awarded = pts if passed else Decimal('0')
                machine += awarded
                criteria.append({'criterion_id': cid, 'status': 'awarded' if passed else 'denied',
                                 'awarded_points': float(awarded), 'pending_points': 0.0, 'max_points': float(pts)})
        elif payload_class == 'method':
            text = submission.get('text')
            if pending and not auto and isinstance(text, str) and not text.strip():
                primary = 'BLANK_RESPONSE'
                pending_points = Decimal('0')
                for c in criteria:
                    c['status'] = 'denied'
                    c['pending_points'] = 0.0
            for item in auto:
                pts = Decimal(str(item['points']))
                maximum += pts
                criteria.append({'criterion_id': item['criterion_id'], 'status': 'denied',
                                 'awarded_points': 0.0, 'pending_points': 0.0, 'max_points': float(pts)})
        else:
            raise self._error_for('UNREADABLE_INPUT', {'payload_class': payload_class})

        criteria.sort(key=lambda c: c['criterion_id'])
        auto_max = sum(Decimal(str(r['points'])) for r in auto)
        if not auto and pending:
            verdict = 'incorrect' if primary == 'BLANK_RESPONSE' else 'pending_self_assessment'
        elif machine == auto_max and auto_max > 0:
            verdict = 'auto_passed_pending_review' if pending else 'correct'
        elif machine > 0:
            verdict = 'partial'
        else:
            verdict = 'incorrect'

        class_id, signature, feedback_key = self.n05_map.get(primary, ('NONE', '', ''))
        result = {
            'verdict_class': verdict, 'error_class': primary, 'awarded_criteria': criteria,
            'machine_checked_points': float(machine), 'self_assessed_points': 0.0,
            'human_reviewed_points': 0.0, 'pending_points': float(pending_points),
            'max_points': float(maximum), 'oracle_version': oracle_version,
            'oracle_digest': oracle_digest,
            'conventions_digest': conventions_digest or sha256_bytes(canonical_json_bytes(self.conventions)),
            'taxonomy_class': class_id, 'signature': signature, 'feedback_key': feedback_key,
            'feedback_text': self.feedback(class_id),
            'tolerance_source': self._tolerance(payload.get('tolerance_class', 'mass')) and
            f"tolerances.quantity_classes[id={payload.get('tolerance_class', 'mass')}]",
        }
        return result

    def _structural_criteria(self, criteria: list[dict[str, Any]], auto: list[dict[str, Any]],
                             matched: bool, machine: Decimal, maximum: Decimal) -> tuple[Decimal, Decimal]:
        for item in auto:
            pts = Decimal(str(item['points']))
            maximum += pts
            awarded = pts if matched else Decimal('0')
            machine += awarded
            criteria.append({'criterion_id': item['criterion_id'],
                             'status': 'awarded' if matched else 'denied',
                             'awarded_points': float(awarded), 'pending_points': 0.0,
                             'max_points': float(pts)})
        return machine, maximum

    @staticmethod
    def _check_order(submitted: list[str], correct: list[str], rules: list[dict[str, Any]] | None) -> bool:
        if len(submitted) != len(correct) or set(submitted) != set(correct):
            return False
        free: list[set[str]] = []
        for rule in rules or []:
            if isinstance(rule, dict) and rule.get('type') == 'free_order_group':
                free.append(set(rule.get('item_ids', [])))
        for a, b in zip(submitted, correct):
            if a != b and not any(a in g and b in g for g in free):
                return False
        return True

    # ------------------------------------------------------------- conservation
    def check_conservation(self, record: dict[str, Any]) -> dict[str, Any]:
        tolerance_rule = next(r for r in self.taxonomy['conservation']['rules']
                              if r['id'] == 'mass_in_equals_mass_out')
        source = tolerance_rule['tolerance_source']
        node: Any = self.conventions
        for part in source.split('.'):
            selector = re.match(r'^(.+?)\[id=([^\]]+)\]$', part)
            if selector:
                node = next(item for item in node[selector.group(1)] if item['id'] == selector.group(2))
            else:
                node = node[part] if not part.isdigit() else node[int(part)]
        tolerance = Decimal(str(node))
        total_in = sum((Decimal(str(s['mass_g'])) for s in record['species_in']), Decimal('0'))
        total_out = sum((Decimal(str(s['mass_g'])) for s in record['species_out']), Decimal('0'))
        delta = total_in - total_out
        balanced = abs(delta) <= tolerance
        mole_rule = next(r for r in self.taxonomy['conservation']['rules']
                         if r['id'] == 'moles_by_stoichiometry')
        rel_tol = Decimal(str(mole_rule['relative_tolerance']))
        extents = [Decimal(str(s.get('moles', 0))) / Decimal(str(s['nu']))
                   for s in record['species_in'] + record['species_out'] if s.get('nu') is not None]
        mole_delta = max(extents) - min(extents)
        moles_ok = mole_delta <= rel_tol * max(Decimal('1'), max(extents))
        verdict = 'BALANCED' if balanced and moles_ok else 'IMBALANCED'
        signature = '' if verdict == 'BALANCED' else self.taxonomy['conservation']['imbalance_signature']
        return {
            'verdict': verdict, 'signature': signature, 'mass_in': str(total_in),
            'mass_out': str(total_out), 'delta': str(delta), 'mole_delta': str(mole_delta),
            'tolerance': str(tolerance), 'tolerance_source': source,
            'relative_tolerance': str(rel_tol), 'balanced': balanced, 'moles_ok': moles_ok,
        }

    # ------------------------------------------------------------ classification
    def classify(self, case: dict[str, Any]) -> dict[str, Any]:
        trace: list[str] = []
        raw = case.get('raw')
        unit = case.get('unit')
        expected_unit = case.get('expected_unit')
        value, _sf, parse_err = self.parse_numeric(raw)
        if parse_err:
            trace.append(parse_err)
            return self._class_result(parse_err, trace, {'raw': raw, 'reason': 'unreadable literal'})
        trace.append('literal parsed')
        try:
            src_dim = self.parse_unit(unit)
            dst_dim = self.parse_unit(expected_unit) if expected_unit else src_dim
        except EngineError as err:
            trace.append('unit grammar failed')
            return self._class_result(err.n05_error or 'UNREADABLE_INPUT', trace,
                                      {'unit': unit, 'reason': 'unit grammar'})
        trace.append('unit grammar parsed')
        if self.dim_key(src_dim) != self.dim_key(dst_dim):
            trace.append('dimension mismatch')
            return self._class_result('DIMENSIONAL_INCONSISTENCY', trace,
                                      {'unit': unit, 'expected_unit': expected_unit,
                                       'dimensions': [self.dim_key(src_dim), self.dim_key(dst_dim)]})
        status, factor, offset = self.resolve_unit_transform(str(unit), str(expected_unit))
        if status in ('blocked', 'incompatible'):
            trace.append(f'transform {status}')
            return self._class_result('DIMENSIONAL_INCONSISTENCY', trace,
                                      {'unit': unit, 'expected_unit': expected_unit, 'status': status})
        converted = value * self._fraction_decimal(factor) + self._fraction_decimal(offset)
        trace.append('unit transform closed')
        rule_id = case.get('rule_id')
        if rule_id and rule_id in self.plausibility:
            rule = self.plausibility[rule_id]
            lower, upper = rule.get('min'), rule.get('max')
            inclusive = bool(rule.get('inclusive', True))
            below = lower is not None and (converted < Decimal(str(lower)) if inclusive else converted <= Decimal(str(lower)))
            above = upper is not None and (converted > Decimal(str(upper)) if inclusive else converted >= Decimal(str(upper)))
            if below or above:
                trace.append(f'plausibility {rule_id}')
                n05 = 'UNLABELED_PERCENT_BASIS' if rule_id == 'percent_basis_required' else 'OUT_OF_TOLERANCE'
                return self._class_result(n05, trace, {'rule_id': rule_id, 'value': str(converted),
                                                      'source': rule['source'],
                                                      'conventions_ref': rule['conventions_ref']})
        span = case.get('span')
        if span:
            x = Decimal(str(case.get('x', converted)))
            lo, hi = Decimal(str(span['min'])), Decimal(str(span['max']))
            if x < lo or x > hi:
                trace.append('outside declared span')
                return self._class_result('OUT_OF_DOMAIN_EXTRAPOLATION', trace,
                                          {'x': str(x), 'span': span, 'rule': case.get('domain_rule', 'calibration_span')})
        trace.append('in domain')
        return {'taxonomy_class': 'NONE', 'signature': 'NONE', 'feedback_key': '',
                'feedback_text': '', 'n05_error_class': 'NONE', 'precedence_trace': trace,
                'rule_sources': [], 'value': str(converted)}

    def _class_result(self, n05_error: str, trace: list[str], detail: dict[str, Any]) -> dict[str, Any]:
        class_id, signature, key = self.n05_map.get(n05_error, (
            self.fallback.get('code', 'UNREADABLE_INPUT'),
            self.fallback['signature'], self.fallback['feedback_key']))
        sources = []
        for rid in [detail.get('rule_id'), detail.get('rule')]:
            if rid in self.plausibility:
                sources.append(self.plausibility[rid]['source'])
            if rid in self.domain_rules:
                sources.append(self.domain_rules[rid]['source_contract'])
        return {
            'taxonomy_class': class_id, 'signature': signature, 'feedback_key': key,
            'feedback_text': self.feedback(class_id), 'n05_error_class': n05_error,
            'precedence_trace': trace, 'rule_sources': sources, 'detail': detail,
        }

    def feedback(self, class_id: str) -> str:
        if class_id in self.by_error:
            key = self.by_error[class_id]['feedback_key']
        elif class_id == 'NONE':
            return ''
        else:
            key = self.fallback['feedback_key']
        entry = self.term_by_key.get(key)
        if not entry:
            raise self._error_for('UNREADABLE_INPUT', {'feedback_key': key, 'term_island': 'sim-terms'})
        return entry['text_lv']

    # --------------------------------------------------------------- assurance
    def no_local_constants(self, source_texts: dict[str, str]) -> dict[str, Any]:
        forbidden: set[str] = set()
        for group in ('atomic_masses', 'compound_molar_masses', 'constants'):
            node = self.conventions[group]
            values = node.get('values', node) if isinstance(node, dict) else node
            if isinstance(values, dict):
                candidates = [v.get('value', v) if isinstance(v, dict) else v for v in values.values()]
            else:
                candidates = [v.get('value', v) if isinstance(v, dict) else v for v in values]
            for value in candidates:
                try:
                    dec = Decimal(str(value))
                    if dec.is_finite() and dec != 0 and (dec % 1 != 0 or abs(dec) < 1):
                        forbidden.add(str(dec.normalize()))
                except InvalidOperation:
                    continue
        for conv in self.conventions['unit_system']['conversions']:
            factor = conv.get('factor')
            if factor:
                dec = Decimal(factor['num']) / Decimal(factor['den'])
                if dec != 0 and (dec % 1 != 0 or abs(dec) < 1):
                    forbidden.add(str(dec.normalize()))
        findings: list[dict[str, str]] = []
        for name, text in source_texts.items():
            for token in NUMBER_TOKEN_RE.findall(text):
                try:
                    normalized = str(Decimal(token).normalize())
                except InvalidOperation:
                    continue
                if normalized in forbidden:
                    findings.append({'source': name, 'literal': token, 'conventions_value': normalized})
        return {
            'status': 'PASS' if not findings else 'FAIL',
            'forbidden_values': sorted(forbidden), 'findings': findings,
            'rule': self.taxonomy['conventions_consumption']['no_local_constants_rule'],
        }

    def oracle_view(self, verdict: dict[str, Any]) -> dict[str, Any]:
        return {k: verdict[k] for k in ORACLE_EXPECTED_FIELDS if k in verdict}


def load(repo_root: Path | None = None) -> Engine:
    root = repo_root or DEST
    return Engine(load_json(root / CONVENTIONS_PATH), load_json(root / TAXONOMY_PATH),
                  load_json(root / TERMS_PATH))


def no_local_constants_ast(source_text: str) -> list[str]:
    """List numeric literals in a Python engine source (used by the validator)."""
    tree = ast.parse(source_text)
    return [str(node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)]


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    engine = load()
    report = {
        'status': 'PASS',
        'conventions_digest': sha256_bytes(canonical_json_bytes(engine.conventions)),
        'taxonomy_digest': sha256_bytes(canonical_json_bytes(engine.taxonomy)),
        'classes': [c['id'] for c in engine.errors],
        'precedence_rule': engine.taxonomy['error_taxonomy']['precedence_rule_verbatim'],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) if args.json
          else f"PASS quantity-engine: {len(engine.errors)} classes, conventions consumed from #sim-conventions")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
