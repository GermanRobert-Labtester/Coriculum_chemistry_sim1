#!/usr/bin/env python3
"""N18 graph scoring engine (Python authoring twin of src/graph-scoring-engine.js).

The engine grades two families of graph work declared in
data/graph_scoring_contract.json:

  reading  - a marked point on a rendered figure, scored against the figure
             record's declared tolerance fields (the tolerance class is named by
             the record or by this contract and its value is resolved from
             #sim-conventions at scoring time, never copied into a record);
  drawing  - a drawn line or curve segment on declared axes, scored against the
             criterion shape (the N14 declared true parameters or the N15/N14
             declared model), with the N15 no-extrapolation rule inherited
             verbatim: geometry beyond the declared span is neither accepted nor
             rejected, it is simply not assessed.

Validity rules run before any numeric comparison, so an unphysical submission
returns a validity class with its reason instead of a numeric score against an
absurd geometry.  The capture payload is device-agnostic by construction: the
pointer path and the keyboard path produce the same payload structure, so the
scorer cannot tell which device drew the line.

The engine consumes only data/conventions.json, data/graph_scoring_contract.json
and the figure records (data/figures_*.json).  It declares no tolerance value,
no unit factor and no model coefficient of its own.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

CONTRACT_PATH = 'data/graph_scoring_contract.json'
CONVENTIONS_PATH = 'data/conventions.json'
FIGURE_PATHS = ('data/figures_t5.json', 'data/figures_t67.json')

NUMBER_RE = re.compile(r'^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?$')
PAYLOAD_SCHEMA_ID = 'sim-graph-draw-v1'
ORACLE_VERSION = '1.0.0'


class GraphError(ValueError):
    """A named failure with a validity class and a check name."""

    def __init__(self, code: str, message: str, detail: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.detail = detail or {}

    def as_dict(self) -> dict[str, Any]:
        return {'code': self.code, 'message': str(self), 'detail': self.detail}


# --------------------------------------------------------------------------- helpers
def parse_number(raw: Any) -> float | None:
    """Parse a Latvian or ASCII decimal literal into a float, or None."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    if not isinstance(raw, str):
        return None
    text = raw.strip().replace(' ', '')
    if not text or not NUMBER_RE.match(text):
        return None
    try:
        return float(text.replace(',', '.'))
    except ValueError:
        return None


def q12(value: float) -> float:
    """Quantize to the declared capture quantum: 12 decimal places.

    The JavaScript twin uses ``Number(value.toFixed(12))``, which parses the
    same decimal string, so both languages produce the identical double.
    """
    if value == 0:
        return 0.0
    return float(f'{float(value):.12f}')


def canonical_number(value: Any) -> str:
    """Render a number in the declared canonical projection (12 decimals)."""
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return f'{float(value):.12f}'


def canonical_projection(value: Any) -> str:
    """Declared canonical projection: sorted keys, no whitespace, fixed decimals.

    The JavaScript twin implements the same rule, so a digest over a verdict
    table is comparable across the two languages.
    """
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return canonical_number(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return '[' + ','.join(canonical_projection(item) for item in value) + ']'
    if isinstance(value, dict):
        parts = []
        for key in sorted(value):
            parts.append(json.dumps(str(key), ensure_ascii=False) + ':' +
                         canonical_projection(value[key]))
        return '{' + ','.join(parts) + '}'
    raise TypeError(f'Not canonicalizable: {type(value)!r}')


def adjusted_exponent(value: float) -> int:
    """Decimal exponent of the most significant digit (Decimal.adjusted)."""
    return Decimal(repr(float(value))).adjusted()


def sig_figs_of(value: float) -> int:
    """Significant figures of the shortest decimal representation."""
    text = repr(float(value))
    if 'e' in text or 'E' in text:
        mantissa = text.partition('e')[0]
    else:
        mantissa = text
    digits = mantissa.replace('-', '').replace('.', '').lstrip('0')
    return max(1, len(digits))


def canonical_digest(value: Any) -> str:
    """SHA-256 over the declared canonical projection of a value."""
    return sha256_bytes(canonical_projection(value).encode('utf-8'))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# --------------------------------------------------------------------------- engine
class GraphScoringEngine:
    """One conventions-consuming graph scoring authority."""

    def __init__(self, conventions: dict[str, Any], contract: dict[str, Any],
                 figures: dict[str, dict[str, Any]] | None = None) -> None:
        self.conventions = conventions
        self.contract = contract
        self.figures = figures or {}
        self.tolerance_classes = {
            entry['id']: entry for entry in conventions['tolerances']['quantity_classes']
        }
        self.conversions = conventions['unit_system']['conversions']
        self.shapes = contract['criterion_shapes']
        self.contexts = contract['capture_contract']['capture_contexts']
        self.validity_rank = {
            entry['id']: int(entry['rank']) for entry in contract['validity_rules']['classes']
        }
        self.payload_schema = contract['capture_contract']['payload_schema']
        self.conventions_digest = sha256_bytes(canonical_json_bytes(conventions))
        self.contract_digest = sha256_bytes(canonical_json_bytes(contract))

    # ------------------------------------------------------------- tolerances
    def resolve_tolerance(self, tolerance_class: str, mode: str, value: float | None = None,
                          sig_figs: int | None = None) -> dict[str, Any]:
        """Resolve a tolerance from #sim-conventions at scoring time."""
        entry = self.tolerance_classes.get(tolerance_class)
        if entry is None:
            raise GraphError('E_GRAPH_UNKNOWN_TOLERANCE_CLASS',
                             f'Unknown tolerance class: {tolerance_class!r}',
                             {'tolerance_class': tolerance_class})
        cited = [{
            'kind': 'tolerance_class',
            'id': tolerance_class,
            'unit': entry.get('unit'),
            'mode': mode,
            'absolute_value': entry['absolute']['value'],
            'significant_figures_policy': (entry.get('significant_figures') or {}).get('mode'),
        }]
        if mode == 'absolute':
            tolerance = float(entry['absolute']['value'])
        elif mode == 'significant_figures':
            if value is None:
                raise GraphError('E_GRAPH_TOLERANCE_MODE_NEEDS_VALUE',
                                 'significant_figures mode needs a reference value',
                                 {'tolerance_class': tolerance_class})
            if value == 0:
                tolerance = 0.0
            else:
                exponent = adjusted_exponent(value)
                digits = int(sig_figs) if sig_figs else sig_figs_of(value)
                tolerance = 0.5 * (10.0 ** (exponent - digits + 1))
        else:
            raise GraphError('E_GRAPH_UNKNOWN_TOLERANCE_MODE',
                             f'Unknown tolerance mode: {mode!r}', {'mode': mode})
        return {'tolerance': tolerance, 'value': value, 'sig_figs': sig_figs, 'cited': cited}

    def unit_factor(self, from_unit: str | None, to_unit: str | None) -> float:
        """Multiplicative factor between two declared units."""
        src = ' '.join((from_unit or '').split())
        dst = ' '.join((to_unit or '').split())
        if src == dst:
            return 1.0
        for conv in self.conversions:
            a = ' '.join(str(conv.get('from', '')).split())
            b = ' '.join(str(conv.get('to', '')).split())
            if (src, dst) in ((a, b), (b, a)) and conv.get('conversion_class') == 'blocked':
                raise GraphError('E_GRAPH_BLOCKED_UNIT',
                                 f'Blocked conversion {src} -> {dst}', {'from': src, 'to': dst})
        for conv in self.conversions:
            if conv.get('conversion_class') == 'blocked':
                continue
            if conv.get('conversion_class') == 'offset':
                continue
            factor = conv.get('factor')
            if not factor:
                continue
            a = ' '.join(str(conv.get('from', '')).split())
            b = ' '.join(str(conv.get('to', '')).split())
            if (src, dst) == (a, b):
                return factor['num'] / factor['den']
            if (src, dst) == (b, a):
                return factor['den'] / factor['num']
        raise GraphError('E_GRAPH_UNIT_UNRESOLVED',
                         f'No declared conversion {src} -> {dst}', {'from': src, 'to': dst})

    # ---------------------------------------------------------------- capture
    def _model_value(self, model: str, params: dict[str, Any], x: float) -> float:
        order = int(params['order'])
        k = float(params['k'])
        c0 = float(params['C0_mol_l'])
        if order == 0:
            return max(0.0, c0 - k * x)
        if order == 1:
            return c0 * math.exp(-k * x)
        if order == 2:
            return c0 / (1.0 + k * c0 * x)
        raise GraphError('E_GRAPH_UNKNOWN_MODEL', f'Unknown model: {model!r}', {'model': model})

    def _grid_points(self, grid: dict[str, Any]) -> list[float]:
        x_min = float(grid['x_min'])
        x_max = float(grid['x_max'])
        step = float(grid['step'])
        if step <= 0 or x_max < x_min:
            raise GraphError('E_GRAPH_BAD_GRID', 'Declared grid is not usable', {'grid': grid})
        count = int(round((x_max - x_min) / step)) + 1
        return [q12(x_min + index * step) for index in range(count)]

    def _raw_path(self, context: dict[str, Any], geometry: dict[str, Any],
                  device: str) -> list[tuple[float, float]]:
        kind = geometry.get('kind')
        if kind == 'empty':
            return []
        if kind == 'line':
            slope = float(geometry['slope'])
            intercept = float(geometry['intercept'])
            x_min = float(geometry['x_min'])
            x_max = float(geometry['x_max'])
            points = [(x_min, q12(slope * x_min + intercept)), (x_max, q12(slope * x_max + intercept))]
            return self._densify(points, context, device)
        if kind == 'polyline':
            points = [(float(x), float(y)) for x, y in geometry['points']]
            return self._densify(points, context, device)
        if kind == 'model':
            params = geometry['params']
            grid_x = self._grid_points(context['grid'])
            points = [(x, q12(self._model_value(geometry['model'], params, x))) for x in grid_x]
            return self._densify(points, context, device)
        raise GraphError('E_GRAPH_UNKNOWN_GEOMETRY', f'Unknown geometry kind: {kind!r}',
                         {'kind': kind})

    def _densify(self, points: list[tuple[float, float]], context: dict[str, Any],
                 device: str) -> list[tuple[float, float]]:
        """Pointer paths are sampled finely; keyboard paths walk the declared points."""
        if device != 'pointer' or len(points) < 2:
            return [(q12(x), q12(y)) for x, y in points]
        step = float(context['grid']['step']) / 10.0
        out: list[tuple[float, float]] = []
        for index in range(len(points) - 1):
            x0, y0 = points[index]
            x1, y1 = points[index + 1]
            span = abs(x1 - x0)
            count = max(1, int(math.ceil(span / step))) if span > 0 else 1
            for step_index in range(count):
                ratio = step_index / count
                out.append((q12(x0 + (x1 - x0) * ratio), q12(y0 + (y1 - y0) * ratio)))
        out.append((q12(points[-1][0]), q12(points[-1][1])))
        return out

    def _project(self, path: list[tuple[float, float]], grid: dict[str, Any]) -> list[dict[str, float]]:
        """Resample a raw path onto the declared grid (linear interpolation)."""
        if len(path) < 2:
            return [{'x': q12(x), 'y': q12(y)} for x, y in path]
        values: dict[float, float] = {}
        for index in range(len(path) - 1):
            x0, y0 = path[index]
            x1, y1 = path[index + 1]
            if x1 == x0:
                continue
            low, high = (x0, x1) if x0 <= x1 else (x1, x0)
            for grid_x in self._grid_points(grid):
                if low - 1e-12 <= grid_x <= high + 1e-12:
                    ratio = (grid_x - x0) / (x1 - x0)
                    values[grid_x] = y0 + (y1 - y0) * ratio
        if not values:
            return []
        ordered = sorted(values.keys())
        return [{'x': q12(x), 'y': q12(values[x])} for x in ordered]

    @staticmethod
    def _reversals(path: list[tuple[float, float]]) -> int:
        if len(path) < 3:
            return 0
        reversals = 0
        direction = 0
        for index in range(len(path) - 1):
            delta = path[index + 1][0] - path[index][0]
            if delta == 0:
                continue
            sign = 1 if delta > 0 else -1
            if direction != 0 and sign != direction:
                reversals += 1
            direction = sign
        return reversals

    def keyboard_increments(self, context_id: str) -> dict[str, float]:
        """The declared keyboard increments for a capture context.

        coarse_x is the grid step, so every grid point is reachable; coarse_y
        is the y axis step.  The fine steps are a tenth of the corresponding
        step and are never coarser than half the declared tolerance band of
        the assessed axis, so the keyboard path cannot be structurally
        penalised relative to the pointer path.  The rule is
        N18-CAPTURE-KEY-01.
        """
        context = self.contexts.get(context_id)
        if context is None:
            raise GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT',
                             f'Unknown capture context: {context_id!r}', {'context': context_id})
        keyboard = context.get('keyboard') or {}
        if 'y_axis_step' not in keyboard:
            raise GraphError('E_GRAPH_BAD_CAPTURE_CONTEXT',
                             'Capture context declares no keyboard increments',
                             {'context': context_id})
        coarse_x = float(context['grid']['step'])
        fine_x = coarse_x / 10.0
        x_band = keyboard.get('x_tolerance_band')
        if x_band is not None:
            fine_x = min(fine_x, float(x_band) / 2.0)
        coarse_y = float(keyboard['y_axis_step'])
        fine_y = coarse_y / 10.0
        y_band = keyboard.get('y_tolerance_band')
        if y_band is not None:
            fine_y = min(fine_y, float(y_band) / 2.0)
        return {
            'coarse_x': q12(coarse_x), 'fine_x': q12(fine_x),
            'coarse_y': q12(coarse_y), 'fine_y': q12(fine_y),
        }

    def capture_path(self, context_id: str, path: list[tuple[float, float]]) -> dict[str, Any]:
        """Build the device-agnostic capture payload from a raw path.

        The raw path is the ordered list of points the learner drew or walked.
        Pointer and keyboard input both arrive here, so the payload cannot
        reveal which device produced it.
        """
        context = self.contexts.get(context_id)
        if context is None:
            raise GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT',
                             f'Unknown capture context: {context_id!r}', {'context': context_id})
        quantized = [(q12(x), q12(y)) for x, y in path]
        payload = {
            'schema_id': PAYLOAD_SCHEMA_ID,
            'kind': context['kind'],
            'points': self._project(quantized, context['grid']),
            'axes': context['axes'],
            'span': context['span'],
            'grid': context['grid'],
            'path_reversals': self._reversals(quantized),
        }
        return self.validate_payload(payload)

    def capture(self, context_id: str, geometry: dict[str, Any],
                device: str = 'pointer') -> dict[str, Any]:
        """Build the device-agnostic capture payload from a declared geometry."""
        context = self.contexts.get(context_id)
        if context is None:
            raise GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT',
                             f'Unknown capture context: {context_id!r}', {'context': context_id})
        path = self._raw_path(context, geometry, device)
        payload = {
            'schema_id': PAYLOAD_SCHEMA_ID,
            'kind': context['kind'],
            'points': self._project(path, context['grid']),
            'axes': context['axes'],
            'span': context['span'],
            'grid': context['grid'],
            'path_reversals': self._reversals(path),
        }
        return self.validate_payload(payload)

    def validate_payload(self, payload: Any) -> dict[str, Any]:
        """Validate the frozen capture payload schema; fail by name."""
        if not isinstance(payload, dict):
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload is not an object',
                             {'check': 'payload_schema'})
        if payload.get('schema_id') != PAYLOAD_SCHEMA_ID:
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED',
                             f'Payload schema_id must be {PAYLOAD_SCHEMA_ID!r}',
                             {'check': 'payload_schema'})
        if payload.get('kind') not in ('line', 'segment'):
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload kind is not declared',
                             {'check': 'payload_schema'})
        points = payload.get('points')
        if not isinstance(points, list):
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload points must be an array',
                             {'check': 'payload_points'})
        for point in points:
            if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload point needs x and y',
                                 {'check': 'payload_points'})
            for key in ('x', 'y'):
                value = point[key]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload point coordinate is not numeric',
                                     {'check': 'payload_points'})
                if not math.isfinite(float(value)):
                    raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload point coordinate is not finite',
                                     {'check': 'payload_points'})
        axes = payload.get('axes')
        if not isinstance(axes, dict) or 'x' not in axes or 'y' not in axes:
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axes are missing',
                             {'check': 'payload_axes'})
        for axis in ('x', 'y'):
            bounds = axes.get(axis)
            if not isinstance(bounds, dict) or 'min' not in bounds or 'max' not in bounds:
                raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axis bounds are missing',
                                 {'check': 'payload_axes'})
            if float(bounds['min']) > float(bounds['max']):
                raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axis bounds are inverted',
                                 {'check': 'payload_axes'})
        span = payload.get('span')
        if not isinstance(span, dict) or 'x_min' not in span or 'x_max' not in span:
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span is missing',
                             {'check': 'payload_span'})
        if float(span['x_min']) > float(span['x_max']):
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span is inverted',
                             {'check': 'payload_span'})
        if span.get('edge_rule') != 'inclusive':
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span edge_rule must be inclusive',
                             {'check': 'payload_span'})
        grid = payload.get('grid')
        if not isinstance(grid, dict) or 'x_min' not in grid or 'x_max' not in grid or 'step' not in grid:
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload grid is missing',
                             {'check': 'payload_span'})
        if float(grid['x_min']) > float(grid['x_max']) or float(grid['step']) <= 0:
            raise GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload grid is not usable',
                             {'check': 'payload_span'})
        return payload

    # --------------------------------------------------------------- criteria
    def figure_record(self, figure_id: str) -> dict[str, Any]:
        record = self.figures.get(figure_id)
        if record is None:
            raise GraphError('E_GRAPH_UNKNOWN_FIGURE', f'Unknown figure: {figure_id!r}',
                             {'figure_id': figure_id})
        return record

    def _record_line(self, record: dict[str, Any]) -> dict[str, Any]:
        line = record.get('fit_line') or (record.get('grading_reference') or {}).get('fit_line')
        if not line:
            raise GraphError('E_GRAPH_NO_CRITERION', 'Record declares no fit line',
                             {'figure_id': record.get('id')})
        return line

    def _record_span(self, record: dict[str, Any]) -> dict[str, Any]:
        span = record.get('span')
        if span:
            return {'x_min': float(span['x_min']), 'x_max': float(span['x_max']),
                    'edge_rule': span.get('edge_rule', 'inclusive')}
        model = None
        for series in record.get('series', []):
            if series.get('curve_model'):
                model = series['curve_model']
                break
        if model:
            params = model.get('params', {})
            if 't_min_s' in params and 't_max_s' in params:
                return {'x_min': float(params['t_min_s']), 'x_max': float(params['t_max_s']),
                        'edge_rule': 'inclusive'}
            if 'V_max_ml' in params:
                return {'x_min': 0.0, 'x_max': float(params['V_max_ml']), 'edge_rule': 'inclusive'}
        axes = record.get('axes', {})
        return {'x_min': float(axes.get('x', {}).get('min', 0.0)),
                'x_max': float(axes.get('x', {}).get('max', 0.0)), 'edge_rule': 'inclusive'}

    def _record_axes(self, record: dict[str, Any]) -> dict[str, dict[str, float]]:
        axes = record.get('axes', {})
        return {
            'x': {'min': float(axes.get('x', {}).get('min', 0.0)), 'max': float(axes.get('x', {}).get('max', 0.0))},
            'y': {'min': float(axes.get('y', {}).get('min', 0.0)), 'max': float(axes.get('y', {}).get('max', 0.0))},
        }

    def _reading_criterion(self, source: dict[str, Any]) -> dict[str, Any]:
        """Resolve the reading criterion for a payload instance or a figure record."""
        kind = source.get('kind')
        if kind == 'n05_payload':
            instance = source['instance']
            payload = instance['payload']
            readout = payload['target_readout']
            xs = [float(point['x']) for point in payload['points']]
            cited = [{
                'kind': 'contract_rule', 'id': 'N18-N05-INHERIT-01',
                'source': 'tools/golden_oracle.py (payload_class=graph branch)',
            }]
            return {
                'criterion_id': source.get('criterion_id', instance.get('question_id', 'n05-graph')),
                'shape': 'n05_payload_readout',
                'criterion_kind': 'constant',
                'assessed_axis': 'y',
                'position_axis': 'x',
                'expected_value': float(readout['expected_value']),
                'expected_unit': readout.get('unit', ''),
                'tolerance_class': readout['tolerance_class'],
                'tolerance_mode': 'absolute',
                'sig_figs': None,
                'span': {'x_min': min(xs), 'x_max': max(xs), 'edge_rule': 'inclusive'},
                'axes': None,
                'position': None,
                'position_fixed': False,
                'cited': cited,
                'answer_cross_check': None,
            }
        if kind != 'figure':
            raise GraphError('E_GRAPH_UNKNOWN_SOURCE', f'Unknown reading source: {kind!r}',
                             {'kind': kind})
        record = self.figure_record(source['figure_id'])
        shape_name = source['criterion_shape']
        shape = self.shapes['reading'].get(shape_name)
        if shape is None:
            raise GraphError('E_GRAPH_UNKNOWN_SHAPE', f'Unknown reading shape: {shape_name!r}',
                             {'shape': shape_name})
        axes = self._record_axes(record)
        span = self._record_span(record)
        cited = [{'kind': 'contract_rule', 'id': 'N18-SHAPE-' + shape_name,
                  'source': 'data/graph_scoring_contract.json#/criterion_shapes/reading/' + shape_name}]
        criterion: dict[str, Any] = {
            'criterion_id': source['figure_id'],
            'shape': shape_name,
            'assessed_axis': shape['assessed_axis'],
            'position_axis': shape['position_axis'],
            'expected_value': None,
            'expected_unit': '',
            'tolerance_class': '',
            'tolerance_mode': shape.get('tolerance_mode', 'absolute'),
            'sig_figs': shape.get('sig_figs'),
            'span': span,
            'axes': axes,
            'position': None,
            'position_fixed': False,
            'cited': cited,
            'answer_cross_check': None,
        }
        if shape_name == 'calibration_line_signal_absolute' or shape_name == 'calibration_line_signal_sigfigs':
            line = self._record_line(record)
            criterion['criterion_kind'] = 'line_function'
            criterion['slope'] = float(line['slope'])
            criterion['intercept'] = float(line.get('intercept', 0) or 0)
            criterion['expected_unit'] = record['axes']['y'].get('unit') or ''
            criterion['tolerance_class'] = shape['tolerance_class']
            criterion['tolerance_source'] = shape['tolerance_source']
        elif shape_name == 'calibration_line_concentration':
            line = self._record_line(record)
            calibration = record.get('calibration_spec', {})
            signal = float(calibration['unknown_signal'])
            slope = float(line['slope'])
            intercept = float(line.get('intercept', 0) or 0)
            if calibration.get('model') == 'through_zero_fixed_intercept':
                expected = signal / slope
            else:
                expected = (signal - intercept) / slope
            criterion['criterion_kind'] = 'inverse_line_function'
            criterion['slope'] = slope
            criterion['intercept'] = intercept
            criterion['expected_value'] = q12(expected)
            criterion['expected_unit'] = record['axes']['x'].get('unit') or ''
            criterion['tolerance_class'] = record['tolerance_coupling']['tolerance_class']
            criterion['tolerance_source'] = 'tolerances.quantity_classes[id=' + \
                criterion['tolerance_class'] + ']'
            criterion['position'] = signal
            criterion['position_fixed'] = True
            targets = record.get('answer_targets') or []
            if targets:
                criterion['answer_cross_check'] = {'declared': targets[0].get('value'),
                                                   'unit': targets[0].get('unit'),
                                                   'recomputed': q12(expected)}
        elif shape_name == 'titration_equivalence_volume':
            targets = record.get('answer_targets') or []
            if not targets:
                raise GraphError('E_GRAPH_NO_CRITERION',
                                 'Titration record declares no answer target',
                                 {'figure_id': record.get('id')})
            criterion['criterion_kind'] = 'constant'
            criterion['expected_value'] = float(targets[0]['value'])
            criterion['expected_unit'] = targets[0].get('unit') or record['axes']['x'].get('unit') or ''
            criterion['tolerance_class'] = shape['tolerance_class']
            criterion['tolerance_source'] = shape['tolerance_source']
        else:
            raise GraphError('E_GRAPH_UNKNOWN_SHAPE', f'Unsupported reading shape: {shape_name!r}',
                             {'shape': shape_name})
        return criterion

    def _drawing_criterion(self, record: dict[str, Any]) -> dict[str, Any]:
        """Resolve the drawing criterion (criterion shape) of a figure record."""
        if record.get('tolerance_fields', {}).get('slope'):
            shape_name = 'kinetics_linearization_line'
            fields = record['tolerance_fields']
            line = self._record_line(record)
            cited = [{'kind': 'record_tolerance_field', 'id': 'tolerance_fields.slope',
                      'conventions_ref': fields['slope'].get('conventions_ref'),
                      'mode': fields['slope'].get('tolerance_mode'),
                      'tolerance_class': fields['slope'].get('tolerance_class')}]
            for name in ('intercept', 'point_acceptance'):
                field = fields.get(name)
                if field:
                    cited.append({'kind': 'record_tolerance_field', 'id': 'tolerance_fields.' + name,
                                  'conventions_ref': field.get('conventions_ref'),
                                  'mode': field.get('tolerance_mode'),
                                  'tolerance_class': field.get('tolerance_class')})
            return {
                'criterion_id': record['id'],
                'shape': shape_name,
                'criterion_kind': 'line',
                'slope': float(line['slope']),
                'intercept': float(line.get('intercept', 0) or 0),
                'fields': fields,
                'sample_count': self.shapes['drawing'][shape_name].get('sample_count', 11),
                'span': self._record_span(record),
                'axes': self._record_axes(record),
                'monotonicity': None,
                'curvature': None,
                'cited': cited,
                'kind': 'line',
            }
        if record.get('calibration_spec') and (record.get('fit_line') or
                                               (record.get('grading_reference') or {}).get('fit_line')):
            shape_name = 'calibration_line_draw'
            shape = self.shapes['drawing'][shape_name]
            line = self._record_line(record)
            standards = []
            for series in record.get('series', []):
                for point in series.get('points', []):
                    standards.append(float(point['x']))
            return {
                'criterion_id': record['id'],
                'shape': shape_name,
                'criterion_kind': 'line',
                'slope': float(line['slope']),
                'intercept': float(line.get('intercept', 0) or 0),
                'fields': {
                    'point_acceptance': {
                        'tolerance_class': shape['tolerance_class'],
                        'tolerance_mode': shape['tolerance_mode'],
                        'conventions_ref': 'CIT-C7-CALIB',
                    }
                },
                'sample_x': standards,
                'sample_count': None,
                'span': self._record_span(record),
                'axes': self._record_axes(record),
                'monotonicity': None,
                'curvature': None,
                'cited': [{'kind': 'contract_rule', 'id': 'N18-SHAPE-' + shape_name,
                           'source': 'data/graph_scoring_contract.json#/criterion_shapes/drawing/' + shape_name}],
                'kind': 'line',
            }
        model = None
        for series in record.get('series', []):
            if series.get('curve_model'):
                model = series['curve_model']
                break
        if model and model.get('function_class') == 'kinetics_decay':
            shape_name = 'kinetics_decay_segment'
            shape = self.shapes['drawing'][shape_name]
            coupling = record.get('tolerance_coupling', {})
            return {
                'criterion_id': record['id'],
                'shape': shape_name,
                'criterion_kind': 'model',
                'model': model,
                'fields': {
                    'point_acceptance': {
                        'tolerance_class': coupling.get('tolerance_class'),
                        'tolerance_mode': shape.get('tolerance_mode', 'absolute'),
                        'conventions_ref': coupling.get('conventions_ref'),
                    }
                },
                'sample_count': shape.get('sample_count', 11),
                'span': self._record_span(record),
                'axes': self._record_axes(record),
                'monotonicity': shape.get('monotonicity'),
                'curvature': shape.get('curvature'),
                'cited': [{'kind': 'contract_rule', 'id': 'N18-SHAPE-' + shape_name,
                           'source': 'data/graph_scoring_contract.json#/criterion_shapes/drawing/' + shape_name}],
                'kind': 'segment',
            }
        raise GraphError('E_GRAPH_NO_CRITERION',
                         'Record declares no drawable criterion shape',
                         {'figure_id': record.get('id')})

    # ---------------------------------------------------------------- scoring
    def _criteria_from_rubric(self, rubric: list[dict[str, Any]] | None) -> tuple[list[dict[str, Any]],
                                                                                 list[dict[str, Any]]]:
        items = rubric or []
        auto = [item for item in items
                if item.get('grading') in ('auto', 'mixed')
                and item.get('engine_binding') not in ('self-assessed', 'human-review')]
        pending = [item for item in items if item not in auto]
        return auto, pending

    def _assemble_verdict(self, family: str, criterion_id: str, verdict_class: str,
                          error_class: str, awarded: bool, rubric: list[dict[str, Any]] | None,
                          cited: list[dict[str, Any]], criterion: dict[str, Any],
                          geometry: dict[str, Any], validity: dict[str, Any],
                          capture: dict[str, Any] | None,
                          replay: dict[str, Any]) -> dict[str, Any]:
        auto, pending = self._criteria_from_rubric(rubric)
        awarded_criteria: list[dict[str, Any]] = []
        machine_points = 0.0
        pending_points = 0.0
        max_points = 0.0
        for item in pending:
            points = float(item.get('points', 0.0))
            max_points += points
            pending_points += points
            awarded_criteria.append({
                'criterion_id': item['criterion_id'], 'status': 'pending',
                'awarded_points': 0.0, 'pending_points': points, 'max_points': points,
            })
        for item in auto:
            points = float(item.get('points', 0.0))
            max_points += points
            given = points if awarded else 0.0
            machine_points += given
            awarded_criteria.append({
                'criterion_id': item['criterion_id'],
                'status': 'awarded' if awarded else 'denied',
                'awarded_points': given, 'pending_points': 0.0, 'max_points': points,
            })
        awarded_criteria.sort(key=lambda entry: entry['criterion_id'])
        return {
            'verdict_class': verdict_class,
            'error_class': error_class,
            'awarded_criteria': awarded_criteria,
            'machine_checked_points': machine_points,
            'self_assessed_points': 0.0,
            'human_reviewed_points': 0.0,
            'pending_points': pending_points,
            'max_points': max_points,
            'oracle_version': ORACLE_VERSION,
            'oracle_digest': self.contract.get('oracle_digest', ORACLE_VERSION),
            'conventions_digest': self.conventions_digest,
            'family': family,
            'criterion_id': criterion_id,
            'criterion_shape': criterion.get('shape'),
            'cited_entries': cited,
            'criterion': criterion,
            'assessed_geometry': geometry,
            'validity': validity,
            'capture': capture,
            'replay': replay,
        }

    # -- reading -------------------------------------------------------------
    def score_reading(self, source: dict[str, Any], submission: dict[str, Any],
                      rubric: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Score a marked reading against the figure's declared criterion."""
        criterion = self._reading_criterion(source)
        cited = list(criterion['cited'])
        cited.append({'kind': 'contract_rule', 'id': 'N18-TOLERANCE-01',
                      'source': 'data/graph_scoring_contract.json#/tolerance_resolution'})
        cited.append({'kind': 'inherited_rule', 'id': 'N15-NOEXTRAP-01',
                      'source': 'data/calibration_contract.json#/no_extrapolation_rule'})
        cited.append({'kind': 'inherited_rule', 'id': 'N14-SPAN-01',
                      'source': 'data/kinetics_linearization_contract.json#/span_rule'})

        assessed_axis = criterion['assessed_axis']
        position_axis = criterion['position_axis']
        validity_trace: list[dict[str, Any]] = []
        assessed_value: float | None = None
        position: float | None = None
        submitted_unit: str | None = None

        if source.get('kind') == 'n05_payload':
            raw_value = submission.get('value')
            assessed_value = parse_number(raw_value)
            if assessed_value is None:
                return self._invalid_reading(criterion, cited, rubric, 'UNREADABLE_INPUT',
                                              'submission_value', validity_trace)
            submitted_unit = submission.get('unit', criterion['expected_unit'])
            if 'x' in submission and submission['x'] is not None:
                position = parse_number(submission['x'])
                if position is None:
                    return self._invalid_reading(criterion, cited, rubric, 'UNREADABLE_INPUT',
                                                  'submission_x', validity_trace)
        else:
            raw_assessed = submission.get(assessed_axis)
            raw_position = submission.get(position_axis)
            assessed_value = parse_number(raw_assessed)
            position = parse_number(raw_position)
            if assessed_value is None or position is None:
                return self._invalid_reading(criterion, cited, rubric, 'UNREADABLE_INPUT',
                                              'submission_point', validity_trace)

        # --- validity: the mark must lie on the figure ------------------------
        axes = criterion.get('axes')
        if axes:
            for axis_name, value in (('x', position if position_axis == 'x' else assessed_value),
                                      ('y', position if position_axis == 'y' else assessed_value)):
                bounds = axes[axis_name]
                if value < bounds['min'] or value > bounds['max']:
                    validity_trace.append({'check': 'axis_range', 'axis': axis_name,
                                            'value': value, 'bounds': bounds, 'result': 'fail'})
                    return self._invalid_reading(criterion, cited, rubric,
                                                  'E_GRAPH_OUT_OF_AXIS_RANGE', 'axis_range',
                                                  validity_trace, assessed_value, position)
        validity_trace.append({'check': 'axis_range', 'result': 'pass'})

        # --- domain: the inherited no-extrapolation rule ----------------------
        # The declared span is always an x-axis range, so the span check applies
        # to the x coordinate of the marked point, whichever axis carries it.
        span = criterion['span']
        x_value = assessed_value if assessed_axis == 'x' else position
        if x_value is not None and (x_value < span['x_min'] or x_value > span['x_max']):
            validity_trace.append({'check': 'span', 'x': x_value,
                                    'span': span, 'result': 'fail'})
            return self._invalid_reading(criterion, cited, rubric,
                                          'OUT_OF_DOMAIN_EXTRAPOLATION', 'span', validity_trace,
                                          assessed_value, position)
        validity_trace.append({'check': 'span', 'span': span, 'result': 'pass'})

        # --- tolerance --------------------------------------------------------
        expected = criterion.get('expected_value')
        if criterion['criterion_kind'] == 'line_function':
            expected = q12(criterion['slope'] * (position if position is not None else 0.0) + criterion['intercept'])
        elif criterion['criterion_kind'] == 'inverse_line_function':
            signal = position if position is not None else 0.0
            if criterion.get('intercept') is None:
                expected = q12(signal / criterion['slope'])
            else:
                expected = q12((signal - criterion['intercept']) / criterion['slope'])
        if expected is None:
            raise GraphError('E_GRAPH_NO_EXPECTED_VALUE', 'Reading criterion has no expected value',
                             {'criterion_id': criterion['criterion_id']})

        tolerance_class = criterion['tolerance_class']
        tolerance_mode = criterion['tolerance_mode']
        resolved = self.resolve_tolerance(tolerance_class, tolerance_mode, value=expected,
                                          sig_figs=criterion.get('sig_figs'))
        cited.extend(resolved['cited'])
        tolerance = resolved['tolerance']

        assessed_unit = criterion['expected_unit']
        class_unit = (self.tolerance_classes.get(tolerance_class) or {}).get('unit')
        if class_unit and assessed_unit and class_unit != assessed_unit:
            factor = self.unit_factor(class_unit, assessed_unit)
            tolerance = q12(tolerance * factor)
            cited.append({'kind': 'contract_rule', 'id': 'N18-UNIT-' + class_unit + '->' + assessed_unit,
                          'source': 'conventions.unit_system.conversions',
                          'factor': factor})

        if source.get('kind') == 'n05_payload':
            target_unit = criterion['expected_unit']
            if submitted_unit is not None and ' '.join(submitted_unit.split()) != ' '.join(target_unit.split()):
                factor = self.unit_factor(submitted_unit, target_unit)
                assessed_value = q12(assessed_value * factor)
                cited.append({'kind': 'contract_rule', 'id': 'N18-UNIT-' + submitted_unit + '->' + target_unit,
                              'source': 'conventions.unit_system.conversions', 'factor': factor})
        deviation = abs(assessed_value - expected)
        within = deviation <= tolerance
        cited.append({'kind': 'contract_rule', 'id': 'N18-CITED-ENTRY-01',
                      'source': 'data/graph_scoring_contract.json#/cited_entry_rule'})

        geometry = {
            'assessed_axis': assessed_axis,
            'position_axis': position_axis,
            'assessed_value': q12(assessed_value),
            'expected_value': q12(expected),
            'position': q12(position) if position is not None else None,
            'deviation': q12(deviation),
            'tolerance': tolerance,
            'within_tolerance': bool(within),
            'span': span,
            'answer_cross_check': criterion.get('answer_cross_check'),
        }
        replay = {
            'family': 'reading',
            'criterion': {
                'criterion_kind': criterion['criterion_kind'],
                'expected_value': q12(expected),
                'slope': criterion.get('slope'),
                'intercept': criterion.get('intercept'),
                'tolerance_class': tolerance_class,
                'tolerance_mode': tolerance_mode,
                'sig_figs': criterion.get('sig_figs'),
                'tolerance': tolerance,
                'assessed_axis': assessed_axis,
                'position_axis': position_axis,
                'span': span,
            },
            'geometry': {
                'assessed_value': q12(assessed_value),
                'position': q12(position) if position is not None else None,
            },
            'cited_entries': cited,
        }
        validity = {'class': None, 'reason_lv': None, 'trace': validity_trace}
        return self._assemble_verdict(
            'reading', criterion['criterion_id'],
            'correct' if within else 'incorrect',
            'NONE' if within else 'OUT_OF_TOLERANCE',
            within, rubric, cited, criterion, geometry, validity, None, replay)

    def _invalid_reading(self, criterion: dict[str, Any], cited: list[dict[str, Any]],
                         rubric: list[dict[str, Any]] | None, error_class: str, check: str,
                         trace: list[dict[str, Any]], assessed_value: float | None = None,
                         position: float | None = None) -> dict[str, Any]:
        trace.append({'check': check, 'result': 'fail', 'error_class': error_class})
        validity = {'class': error_class, 'reason_lv': None, 'trace': trace}
        geometry = {'assessed_axis': criterion.get('assessed_axis'),
                    'position_axis': criterion.get('position_axis'),
                    'assessed_value': q12(assessed_value) if assessed_value is not None else None,
                    'expected_value': None,
                    'position': q12(position) if position is not None else None,
                    'deviation': None, 'tolerance': None, 'within_tolerance': False,
                    'span': criterion.get('span')}
        replay = {
            'family': 'reading',
            'criterion': {
                'criterion_kind': criterion.get('criterion_kind'),
                'criterion_id': criterion.get('criterion_id'),
                'span': criterion.get('span'),
                'axes': criterion.get('axes'),
                'assessed_axis': criterion.get('assessed_axis'),
                'position_axis': criterion.get('position_axis'),
            },
            'geometry': {
                'assessed_value': q12(assessed_value) if assessed_value is not None else None,
                'position': q12(position) if position is not None else None,
            },
            'error_class': error_class,
            'cited_entries': cited,
        }
        return self._assemble_verdict('reading', criterion['criterion_id'], 'incorrect', error_class,
                                      False, rubric, cited, criterion, geometry, validity, None, replay)

    # -- drawing -------------------------------------------------------------
    def score_drawing(self, record: dict[str, Any], payload: Any,
                      rubric: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        """Score a drawn line or curve segment against the criterion shape."""
        try:
            payload = self.validate_payload(payload)
        except GraphError as exc:
            raise exc
        criterion = self._drawing_criterion(record)
        cited = list(criterion['cited'])
        cited.append({'kind': 'contract_rule', 'id': 'N18-TOLERANCE-01',
                      'source': 'data/graph_scoring_contract.json#/tolerance_resolution'})
        cited.append({'kind': 'inherited_rule', 'id': 'N14-SPAN-01',
                      'source': 'data/kinetics_linearization_contract.json#/span_rule'})
        cited.append({'kind': 'inherited_rule', 'id': 'N15-NOEXTRAP-01',
                      'source': 'data/calibration_contract.json#/no_extrapolation_rule'})

        points = [{'x': float(p['x']), 'y': float(p['y'])} for p in payload['points']]
        validity_trace: list[dict[str, Any]] = []

        # rank 2: empty submission
        if len(points) < 2:
            validity_trace.append({'check': 'point_count', 'count': len(points), 'result': 'fail'})
            return self._invalid_drawing(criterion, cited, rubric, 'E_GRAPH_EMPTY_SUBMISSION',
                                         'point_count', validity_trace, points)
        validity_trace.append({'check': 'point_count', 'count': len(points), 'result': 'pass'})

        # rank 3: the mark must lie on the figure
        axes = criterion['axes']
        for point in points:
            for axis_name in ('x', 'y'):
                value = point[axis_name]
                bounds = axes[axis_name]
                if value < bounds['min'] or value > bounds['max']:
                    validity_trace.append({'check': 'axis_range', 'axis': axis_name, 'value': value,
                                            'bounds': bounds, 'result': 'fail'})
                    return self._invalid_drawing(criterion, cited, rubric, 'E_GRAPH_OUT_OF_AXIS_RANGE',
                                                 'axis_range', validity_trace, points)
        validity_trace.append({'check': 'axis_range', 'result': 'pass'})

        # the assessed geometry: the span rule, inclusive at the boundary
        span = criterion['span']
        assessed = [point for point in points if span['x_min'] <= point['x'] <= span['x_max']]
        excluded = [point for point in points if not (span['x_min'] <= point['x'] <= span['x_max'])]
        if not assessed:
            validity_trace.append({'check': 'assessed_geometry', 'span': span, 'result': 'empty'})
            validity = {'class': 'NOT_ASSESSED', 'reason_lv': None, 'trace': validity_trace}
            geometry = {
                'assessed_x_range': None, 'points': [], 'excluded_points': excluded,
                'sample_x': [], 'deviations': [], 'max_deviation': None,
                'slope': None, 'intercept': None, 'checks': {},
            }
            replay = {'family': 'drawing', 'criterion': self._replay_criterion(criterion),
                      'geometry': {'points': points}, 'cited_entries': cited}
            return self._assemble_verdict('drawing', criterion['criterion_id'], 'not_assessed',
                                          'NOT_ASSESSED', False, rubric, cited, criterion,
                                          geometry, validity, self._capture_meta(payload), replay)
        validity_trace.append({'check': 'assessed_geometry', 'span': span, 'count': len(assessed),
                                'result': 'pass'})

        # rank 4: the direction must match the criterion
        drawn_slope, drawn_intercept = self._fit_line(assessed)
        criterion_slope = criterion.get('slope')
        if criterion_slope is not None and criterion_slope != 0:
            if (drawn_slope >= 0) != (criterion_slope > 0) or drawn_slope == 0:
                validity_trace.append({'check': 'slope_sign', 'drawn_slope': drawn_slope,
                                        'criterion_slope': criterion_slope, 'result': 'fail'})
                return self._invalid_drawing(criterion, cited, rubric, 'E_GRAPH_WRONG_DIRECTION',
                                             'slope_sign', validity_trace, points)
        validity_trace.append({'check': 'slope_sign', 'drawn_slope': drawn_slope,
                                'criterion_slope': criterion_slope, 'result': 'pass'})

        # rank 5: the path must not double back over itself
        if int(payload.get('path_reversals', 0)) > 0:
            validity_trace.append({'check': 'path_reversals',
                                    'reversals': payload.get('path_reversals'), 'result': 'fail'})
            return self._invalid_drawing(criterion, cited, rubric, 'E_GRAPH_DOUBLE_BACK',
                                         'path_reversals', validity_trace, points)
        validity_trace.append({'check': 'path_reversals', 'reversals': payload.get('path_reversals'),
                                'result': 'pass'})

        # rank 6: the segment must be monotone in the declared direction
        monotonicity = criterion.get('monotonicity')
        if monotonicity:
            ys = [point['y'] for point in assessed]
            if monotonicity == 'decreasing':
                monotone = all(ys[index + 1] <= ys[index] + 1e-12 for index in range(len(ys) - 1))
            else:
                monotone = all(ys[index + 1] >= ys[index] - 1e-12 for index in range(len(ys) - 1))
            if not monotone:
                validity_trace.append({'check': 'monotonicity', 'monotonicity': monotonicity,
                                        'result': 'fail'})
                return self._invalid_drawing(criterion, cited, rubric, 'E_GRAPH_NON_MONOTONIC',
                                             'monotonicity', validity_trace, points)
            validity_trace.append({'check': 'monotonicity', 'monotonicity': monotonicity, 'result': 'pass'})

        # --- the criterion comparison ---------------------------------------
        sample_x = self._sample_x(criterion, assessed)
        criterion_y = []
        for x in sample_x:
            if criterion['criterion_kind'] == 'model':
                criterion_y.append(q12(self._model_value('kinetics_decay',
                                                          criterion['model']['params'], x)))
            else:
                criterion_y.append(q12(criterion['slope'] * x + criterion['intercept']))
        drawn_y = [q12(self._interpolate(assessed, x)) for x in sample_x]
        deviations = [q12(abs(drawn - truth)) for drawn, truth in zip(drawn_y, criterion_y)]
        max_deviation = max(deviations) if deviations else 0.0

        checks: dict[str, bool] = {}
        tolerances: dict[str, float] = {}
        resolved_fields = self._resolve_fields(criterion, cited)
        for name, resolved in resolved_fields.items():
            tolerances[name] = resolved['tolerance']
            cited.extend(resolved['cited'])
        if 'slope' in resolved_fields:
            checks['slope'] = abs(drawn_slope - criterion['slope']) <= tolerances['slope'] + 1e-12
        if 'intercept' in resolved_fields:
            checks['intercept'] = abs(drawn_intercept - criterion['intercept']) <= tolerances['intercept'] + 1e-12
        if 'point_acceptance' in resolved_fields:
            checks['point_acceptance'] = max_deviation <= tolerances['point_acceptance'] + 1e-12
        accepted = all(checks.values()) if checks else False

        cited.append({'kind': 'contract_rule', 'id': 'N18-CITED-ENTRY-01',
                      'source': 'data/graph_scoring_contract.json#/cited_entry_rule'})
        geometry = {
            'assessed_x_range': {'x_min': q12(assessed[0]['x']), 'x_max': q12(assessed[-1]['x'])},
            'points': assessed,
            'excluded_points': excluded,
            'excluded_note_lv': 'Ģeometrija ārpus deklarētā diapazona netiek vērtēta (N14-SPAN-01, N15-NOEXTRAP-01).',
            'sample_x': sample_x,
            'criterion_y': criterion_y,
            'drawn_y': drawn_y,
            'deviations': deviations,
            'max_deviation': max_deviation,
            'slope': q12(drawn_slope),
            'intercept': q12(drawn_intercept),
            'checks': checks,
            'tolerances': tolerances,
        }
        replay = {
            'family': 'drawing',
            'criterion': self._replay_criterion(criterion),
            'geometry': {
                'points': assessed,
                'sample_x': sample_x,
                'criterion_y': criterion_y,
                'drawn_y': drawn_y,
                'slope': q12(drawn_slope),
                'intercept': q12(drawn_intercept),
            },
            'cited_entries': cited,
        }
        validity = {'class': None, 'reason_lv': None, 'trace': validity_trace}
        return self._assemble_verdict('drawing', criterion['criterion_id'],
                                      'correct' if accepted else 'incorrect',
                                      'NONE' if accepted else 'OUT_OF_TOLERANCE',
                                      accepted, rubric, cited, criterion, geometry, validity,
                                      self._capture_meta(payload), replay)

    def _invalid_drawing(self, criterion: dict[str, Any], cited: list[dict[str, Any]],
                         rubric: list[dict[str, Any]] | None, error_class: str, check: str,
                         trace: list[dict[str, Any]], points: list[dict[str, float]]) -> dict[str, Any]:
        trace.append({'check': check, 'result': 'fail', 'error_class': error_class})
        validity = {'class': error_class, 'reason_lv': None, 'trace': trace}
        geometry = {
            'assessed_x_range': None, 'points': points, 'excluded_points': [],
            'sample_x': [], 'deviations': [], 'max_deviation': None,
            'slope': None, 'intercept': None, 'checks': {},
        }
        replay = {'family': 'drawing', 'criterion': self._replay_criterion(criterion),
                  'geometry': {'points': points}, 'cited_entries': cited}
        return self._assemble_verdict('drawing', criterion['criterion_id'], 'incorrect', error_class,
                                      False, rubric, cited, criterion, geometry, validity, None, replay)

    def _capture_meta(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            'digest': canonical_digest(payload),
            'kind': payload.get('kind'),
            'point_count': len(payload.get('points') or []),
            'grid': payload.get('grid'),
            'span': payload.get('span'),
            'device_agnostic': True,
        }

    @staticmethod
    def _fit_line(points: list[dict[str, float]]) -> tuple[float, float]:
        count = len(points)
        mean_x = sum(point['x'] for point in points) / count
        mean_y = sum(point['y'] for point in points) / count
        sxy = sum((point['x'] - mean_x) * (point['y'] - mean_y) for point in points)
        sxx = sum((point['x'] - mean_x) ** 2 for point in points)
        if sxx == 0:
            return 0.0, mean_y
        slope = sxy / sxx
        return slope, mean_y - slope * mean_x

    @staticmethod
    def _interpolate(points: list[dict[str, float]], x: float) -> float:
        if len(points) == 1:
            return points[0]['y']
        if x <= points[0]['x']:
            return points[0]['y']
        if x >= points[-1]['x']:
            return points[-1]['y']
        for index in range(len(points) - 1):
            x0, y0 = points[index]['x'], points[index]['y']
            x1, y1 = points[index + 1]['x'], points[index + 1]['y']
            if x0 <= x <= x1:
                if x1 == x0:
                    return y0
                return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        return points[-1]['y']

    def _sample_x(self, criterion: dict[str, Any], assessed: list[dict[str, float]]) -> list[float]:
        if criterion.get('sample_x'):
            span = criterion['span']
            return [q12(x) for x in criterion['sample_x'] if span['x_min'] <= x <= span['x_max']]
        count = int(criterion.get('sample_count') or 11)
        x_min = assessed[0]['x']
        x_max = assessed[-1]['x']
        if x_max <= x_min:
            return [q12(x_min)]
        return [q12(x_min + (x_max - x_min) * index / (count - 1)) for index in range(count)]

    def _resolve_fields(self, criterion: dict[str, Any],
                        cited: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
        resolved: dict[str, dict[str, Any]] = {}
        # The field names are sorted: the shipped island stores its keys sorted,
        # the source files do not, and the citation order must not depend on it.
        for name in sorted(criterion.get('fields') or {}):
            field = (criterion.get('fields') or {})[name]
            mode = field.get('tolerance_mode', 'absolute')
            reference = criterion.get('slope') if name == 'slope' else (
                criterion.get('intercept') if name == 'intercept' else None)
            if name == 'point_acceptance' and reference is None:
                reference = criterion.get('slope')
            entry = self.resolve_tolerance(field['tolerance_class'], mode, value=reference,
                                           sig_figs=field.get('sig_figs'))
            if mode == 'absolute' and field.get('abs_value') is not None:
                declared = float(field['abs_value'])
                if abs(declared - entry['tolerance']) > 1e-12:
                    raise GraphError('E_GRAPH_TOLERANCE_DRIFT',
                                     'Record tolerance field drifted from the conventions entry',
                                     {'field': name, 'declared': declared,
                                      'resolved': entry['tolerance'],
                                      'tolerance_class': field['tolerance_class']})
            resolved[name] = entry
        return resolved

    def _replay_criterion(self, criterion: dict[str, Any]) -> dict[str, Any]:
        replay = {
            'criterion_id': criterion['criterion_id'],
            'shape': criterion.get('shape'),
            'criterion_kind': criterion.get('criterion_kind'),
            'slope': criterion.get('slope'),
            'intercept': criterion.get('intercept'),
            'model': criterion.get('model'),
            'span': criterion.get('span'),
            'fields': criterion.get('fields'),
            'sample_x': criterion.get('sample_x'),
            'sample_count': criterion.get('sample_count'),
            'monotonicity': criterion.get('monotonicity'),
        }
        return replay

    # ----------------------------------------------------------------- replay
    def replay_verdict(self, verdict: dict[str, Any]) -> dict[str, Any]:
        """Rebuild a verdict from the verdict record alone."""
        replay = verdict.get('replay') or {}
        family = replay.get('family')
        criterion = replay.get('criterion') or {}
        geometry = replay.get('geometry') or {}
        if family == 'reading':
            error_class = replay.get('error_class')
            assessed = geometry.get('assessed_value')
            position = geometry.get('position')
            span = criterion.get('span') or {}
            axes = criterion.get('axes')
            if error_class:
                if error_class == 'OUT_OF_DOMAIN_EXTRAPOLATION':
                    x_value = assessed if criterion.get('assessed_axis') == 'x' else position
                    outside = (x_value is not None and x_value < span.get('x_min', float('-inf'))
                               or x_value is not None and x_value > span.get('x_max', float('inf')))
                    return {'replayable': True, 'verdict_class': 'incorrect',
                            'error_class': 'OUT_OF_DOMAIN_EXTRAPOLATION' if outside else 'REPLAY_MISMATCH'}
                if error_class == 'E_GRAPH_OUT_OF_AXIS_RANGE' and axes:
                    values = {'x': position if criterion.get('position_axis') == 'x' else assessed,
                              'y': position if criterion.get('position_axis') == 'y' else assessed}
                    outside = False
                    for axis_name, value in values.items():
                        bounds = axes.get(axis_name) or {}
                        if value is None:
                            continue
                        if value < bounds.get('min', float('-inf')) or value > bounds.get('max', float('inf')):
                            outside = True
                    return {'replayable': True, 'verdict_class': 'incorrect',
                            'error_class': 'E_GRAPH_OUT_OF_AXIS_RANGE' if outside else 'REPLAY_MISMATCH'}
                return {'replayable': False, 'verdict_class': None, 'error_class': error_class}
            expected = criterion.get('expected_value')
            tolerance = criterion.get('tolerance')
            if criterion.get('criterion_kind') == 'line_function' and position is not None:
                expected = q12(criterion['slope'] * position + criterion['intercept'])
            elif criterion.get('criterion_kind') == 'inverse_line_function' and position is not None:
                expected = q12((position - (criterion.get('intercept') or 0)) / criterion['slope'])
            deviation = abs(assessed - expected)
            within = deviation <= tolerance + 1e-12
            return {'replayable': True, 'verdict_class': 'correct' if within else 'incorrect',
                    'error_class': 'NONE' if within else 'OUT_OF_TOLERANCE',
                    'deviation': q12(deviation)}
        if family == 'drawing':
            checks = {}
            fields = criterion.get('fields') or {}
            if 'slope' in fields:
                checks['slope'] = abs(geometry.get('slope') - criterion['slope']) <= \
                    self.resolve_tolerance(fields['slope']['tolerance_class'],
                                           fields['slope'].get('tolerance_mode', 'absolute'),
                                           value=criterion.get('slope'),
                                           sig_figs=fields['slope'].get('sig_figs'))['tolerance'] + 1e-12
            if 'intercept' in fields:
                checks['intercept'] = abs(geometry.get('intercept') - criterion['intercept']) <= \
                    self.resolve_tolerance(fields['intercept']['tolerance_class'],
                                           fields['intercept'].get('tolerance_mode', 'absolute'),
                                           value=criterion.get('intercept'),
                                           sig_figs=fields['intercept'].get('sig_figs'))['tolerance'] + 1e-12
            if 'point_acceptance' in fields:
                deviations = [abs(drawn - truth)
                              for drawn, truth in zip(geometry.get('drawn_y') or [],
                                                      geometry.get('criterion_y') or [])]
                checks['point_acceptance'] = (max(deviations) if deviations else 0.0) <= \
                    self.resolve_tolerance(fields['point_acceptance']['tolerance_class'],
                                           fields['point_acceptance'].get('tolerance_mode', 'absolute'),
                                           value=criterion.get('slope'),
                                           sig_figs=fields['point_acceptance'].get('sig_figs'))['tolerance'] + 1e-12
            accepted = all(checks.values()) if checks else False
            return {'verdict_class': 'correct' if accepted else 'incorrect',
                    'error_class': 'NONE' if accepted else 'OUT_OF_TOLERANCE',
                    'checks': checks}
        raise GraphError('E_GRAPH_UNKNOWN_REPLAY', f'Unknown replay family: {family!r}',
                         {'family': family})


# --------------------------------------------------------------------------- loader
def load_figures(paths: tuple[str, ...] = FIGURE_PATHS,
                 repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    root = repo_root or DEST
    figures: dict[str, dict[str, Any]] = {}
    for relative in paths:
        document = load_json(root / relative)
        for record in document['figures']:
            figures[record['id']] = record
    return figures


def load(repo_root: Path | None = None) -> GraphScoringEngine:
    root = repo_root or DEST
    conventions = load_json(root / CONVENTIONS_PATH)
    contract = load_json(root / CONTRACT_PATH)
    figures = load_figures(repo_root=root)
    engine = GraphScoringEngine(conventions, contract, figures)
    engine.conventions_digest = sha256_bytes(canonical_json_bytes(conventions))
    return engine


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    engine = load(Path(args.repo_root))
    print(json.dumps({
        'status': 'PASS',
        'contract': CONTRACT_PATH,
        'figures': len(engine.figures),
        'tolerance_classes': len(engine.tolerance_classes),
        'capture_contexts': len(engine.contexts),
        'reading_shapes': sorted(engine.shapes['reading']),
        'drawing_shapes': sorted(engine.shapes['drawing']),
        'conventions_digest': engine.conventions_digest,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
