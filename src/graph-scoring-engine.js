/* N18 graph scoring engine — runtime twin of tools/graph_scoring_engine.py.
 *
 * Grades two families of graph work declared in #sim-graph-scoring:
 *   reading  — a marked point on a rendered figure, scored against the figure
 *              record's declared tolerance fields (the tolerance class is named
 *              by the record or by the contract; its value is resolved from
 *              #sim-conventions at scoring time, never copied into a record);
 *   drawing  — a drawn line or curve segment on declared axes, scored against
 *              the criterion shape, with the N15 no-extrapolation rule inherited
 *              verbatim: geometry beyond the declared span is neither accepted
 *              nor rejected, it is simply not assessed.
 *
 * Validity rules run before any numeric comparison. The capture payload is
 * device-agnostic by construction: the pointer path and the keyboard path
 * produce the same payload structure, so the scorer cannot tell which device
 * drew the line.
 *
 * The module consumes only #sim-conventions, #sim-figures and
 * #sim-graph-scoring. It declares no tolerance value, no unit factor and no
 * model coefficient of its own.
 */
(function (root) {
'use strict';

var CONTRACT_ID = 'sim-graph-scoring';
var FIGURES_ID = 'sim-figures';
var CONVENTIONS_ID = 'sim-conventions';
var PAYLOAD_SCHEMA_ID = 'sim-graph-draw-v1';
var ORACLE_VERSION = '1.0.0';
var DECIMALS = 12;
var NUMBER_RE = /^[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?$/;

var state = { conventions: null, contract: null, figures: null, loadError: null };

function GraphError(code, message, detail) {
  var error = new Error(message || code);
  error.code = code;
  error.detail = detail || {};
  error.name = 'GraphError';
  return error;
}

/* ------------------------------------------------------------------ helpers */
function parseNumber(raw) {
  if (typeof raw === 'boolean') { return null; }
  if (typeof raw === 'number') { return isFinite(raw) ? raw : null; }
  if (typeof raw !== 'string') { return null; }
  var text = raw.replace(/\s+/g, '');
  if (!text || !NUMBER_RE.test(text)) { return null; }
  var value = parseFloat(text.replace(',', '.'));
  return isFinite(value) ? value : null;
}

/* The declared capture quantum: 12 decimal places. */
function q12(value) {
  var number = Number(value);
  if (!isFinite(number)) { return number; }
  if (number === 0) { return 0; }
  return Number(number.toFixed(DECIMALS));
}

function adjustedExponent(value) {
  var text = Number(value).toExponential();
  var index = text.indexOf('e');
  if (index < 0) { return 0; }
  return parseInt(text.slice(index + 1), 10);
}

function sigFigsOf(value) {
  var text = Number(value).toExponential();
  var mantissa = text.split('e')[0].replace('-', '').replace('.', '');
  mantissa = mantissa.replace(/0+$/, '');
  return Math.max(1, mantissa.length);
}

/* The declared canonical projection: sorted keys, no whitespace, fixed decimals. */
function canonicalNumber(value) {
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  return Number(value).toFixed(DECIMALS);
}

function canonicalProjection(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return canonicalNumber(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) {
    var items = [];
    for (var i = 0; i < value.length; i += 1) { items.push(canonicalProjection(value[i])); }
    return '[' + items.join(',') + ']';
  }
  if (typeof value === 'object') {
    var keys = Object.keys(value).sort();
    var parts = [];
    for (var k = 0; k < keys.length; k += 1) {
      parts.push(JSON.stringify(keys[k]) + ':' + canonicalProjection(value[keys[k]]));
    }
    return '{' + parts.join(',') + '}';
  }
  return 'null';
}

function canonicalDigest(value) { return sha256(canonicalProjection(value)); }

/* A compact SHA-256 over UTF-8 text. */
var SHA_K = [
  0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
  0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
  0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
  0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
  0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
  0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
  0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
  0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
];

function sha256(text) {
  var bytes = [];
  var encoded = unescape(encodeURIComponent(text));
  for (var i = 0; i < encoded.length; i += 1) { bytes.push(encoded.charCodeAt(i) & 0xff); }
  var bitLength = bytes.length * 8;
  bytes.push(0x80);
  while (bytes.length % 64 !== 56) { bytes.push(0); }
  var high = Math.floor(bitLength / 0x100000000);
  var low = bitLength >>> 0;
  bytes.push((high >>> 24) & 0xff, (high >>> 16) & 0xff, (high >>> 8) & 0xff, high & 0xff);
  bytes.push((low >>> 24) & 0xff, (low >>> 16) & 0xff, (low >>> 8) & 0xff, low & 0xff);
  var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  var w = new Array(64);
  for (var block = 0; block < bytes.length; block += 64) {
    for (var t = 0; t < 16; t += 1) {
      w[t] = ((bytes[block + t * 4] << 24) | (bytes[block + t * 4 + 1] << 16) |
        (bytes[block + t * 4 + 2] << 8) | bytes[block + t * 4 + 3]) >>> 0;
    }
    for (var j = 16; j < 64; j += 1) {
      var g0 = (w[j - 15] >>> 7 | w[j - 15] << 25) ^ (w[j - 15] >>> 18 | w[j - 15] << 14) ^ (w[j - 15] >>> 3);
      var g1 = (w[j - 2] >>> 17 | w[j - 2] << 15) ^ (w[j - 2] >>> 19 | w[j - 2] << 13) ^ (w[j - 2] >>> 10);
      w[j] = (w[j - 16] + g0 + w[j - 7] + g1) >>> 0;
    }
    var a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
    for (var m = 0; m < 64; m += 1) {
      var s1 = (e >>> 6 | e << 26) ^ (e >>> 11 | e << 21) ^ (e >>> 25 | e << 7);
      var ch = (e & f) ^ (~e & g);
      var temp1 = (hh + s1 + ch + SHA_K[m] + w[m]) >>> 0;
      var s0 = (a >>> 2 | a << 30) ^ (a >>> 13 | a << 19) ^ (a >>> 22 | a << 10);
      var maj = (a & b) ^ (a & c) ^ (b & c);
      var temp2 = (s0 + maj) >>> 0;
      hh = g; g = f; f = e; e = (d + temp1) >>> 0; d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }
    h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0; h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
    h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0; h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
  }
  var hex = '';
  for (var z = 0; z < 8; z += 1) { hex += ('00000000' + h[z].toString(16)).slice(-8); }
  return hex;
}

/* -------------------------------------------------------------------- loader */
function readIsland(doc, id) {
  var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(id) : null;
  if (!node) { throw GraphError('E_GRAPH_ISLAND_MISSING', 'Island #' + id + ' was not found.', { island: id }); }
  var raw = node.textContent !== undefined ? node.textContent : node.innerText;
  if (typeof raw !== 'string' || !raw.trim()) {
    throw GraphError('E_GRAPH_ISLAND_EMPTY', 'Island #' + id + ' is empty.', { island: id });
  }
  try { return JSON.parse(raw); } catch (error) {
    throw GraphError('E_GRAPH_ISLAND_JSON', 'Island #' + id + ' holds broken JSON.', { island: id });
  }
}

/* The island bytes are the canonical JSON the build emitted; reversing the
 * script-escaping restores them, so the digest matches the Python twin. */
function islandDigest(doc, id) {
  var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(id) : null;
  if (!node) { return ''; }
  var raw = node.textContent !== undefined ? node.textContent : node.innerText;
  if (typeof raw !== 'string') { return ''; }
  return sha256(raw.replace(/<\\\//g, '</'));
}

function load(doc) {
  var conventions = readIsland(doc, CONVENTIONS_ID);
  var contract = readIsland(doc, CONTRACT_ID);
  var figures = readIsland(doc, FIGURES_ID);
  if (contract.island_id !== CONTRACT_ID) {
    throw GraphError('E_GRAPH_ISLAND_ID', 'Island id mismatch for #' + CONTRACT_ID + '.', { island: CONTRACT_ID });
  }
  var byId = {};
  var list = figures.figures || [];
  for (var i = 0; i < list.length; i += 1) { byId[list[i].id] = list[i]; }
  state.conventions = conventions;
  state.contract = contract;
  state.figures = byId;
  state.conventionsDigest = islandDigest(doc, CONVENTIONS_ID);
  state.contractDigest = islandDigest(doc, CONTRACT_ID);
  state.loadError = null;
  return { conventions: conventions, contract: contract, figures: byId,
    conventionsDigest: state.conventionsDigest, contractDigest: state.contractDigest };
}

function ensureLoaded(doc) {
  if (!state.conventions || !state.contract || !state.figures) { load(doc); }
  return state;
}

function toleranceClass(id) {
  var list = state.conventions.tolerances.quantity_classes;
  for (var i = 0; i < list.length; i += 1) { if (list[i].id === id) { return list[i]; } }
  throw GraphError('E_GRAPH_UNKNOWN_TOLERANCE_CLASS', 'Unknown tolerance class: ' + id, { tolerance_class: id });
}

/* ------------------------------------------------------------------ engine */
var Engine = {
  resolveTolerance: function (toleranceClassId, mode, value, sigFigs) {
    var entry = toleranceClass(toleranceClassId);
    var cited = [{
      kind: 'tolerance_class', id: toleranceClassId, unit: entry.unit, mode: mode,
      absolute_value: entry.absolute.value,
      significant_figures_policy: (entry.significant_figures || {}).mode || null
    }];
    var tolerance;
    if (mode === 'absolute') {
      tolerance = Number(entry.absolute.value);
    } else if (mode === 'significant_figures') {
      if (value === null || value === undefined) {
        throw GraphError('E_GRAPH_TOLERANCE_MODE_NEEDS_VALUE', 'significant_figures mode needs a reference value',
          { tolerance_class: toleranceClassId });
      }
      if (Number(value) === 0) {
        tolerance = 0;
      } else {
        var exponent = adjustedExponent(value);
        var digits = sigFigs ? Number(sigFigs) : sigFigsOf(value);
        tolerance = 0.5 * Math.pow(10, exponent - digits + 1);
      }
    } else {
      throw GraphError('E_GRAPH_UNKNOWN_TOLERANCE_MODE', 'Unknown tolerance mode: ' + mode, { mode: mode });
    }
    return { tolerance: tolerance, value: value, sig_figs: sigFigs || null, cited: cited };
  },

  unitFactor: function (fromUnit, toUnit) {
    var src = String(fromUnit === null || fromUnit === undefined ? '' : fromUnit).replace(/\s+/g, ' ').trim();
    var dst = String(toUnit === null || toUnit === undefined ? '' : toUnit).replace(/\s+/g, ' ').trim();
    if (src === dst) { return 1; }
    var conversions = state.conventions.unit_system.conversions;
    var i;
    for (i = 0; i < conversions.length; i += 1) {
      var blocked = conversions[i];
      var ba = String(blocked.from || '').replace(/\s+/g, ' ').trim();
      var bb = String(blocked.to || '').replace(/\s+/g, ' ').trim();
      if (blocked.conversion_class === 'blocked' && ((src === ba && dst === bb) || (src === bb && dst === ba))) {
        throw GraphError('E_GRAPH_BLOCKED_UNIT', 'Blocked conversion ' + src + ' -> ' + dst, { from: src, to: dst });
      }
    }
    for (i = 0; i < conversions.length; i += 1) {
      var conv = conversions[i];
      if (conv.conversion_class === 'blocked' || conv.conversion_class === 'offset') { continue; }
      if (!conv.factor) { continue; }
      var a = String(conv.from || '').replace(/\s+/g, ' ').trim();
      var b = String(conv.to || '').replace(/\s+/g, ' ').trim();
      if (src === a && dst === b) { return Number(conv.factor.num) / Number(conv.factor.den); }
      if (src === b && dst === a) { return Number(conv.factor.den) / Number(conv.factor.num); }
    }
    throw GraphError('E_GRAPH_UNIT_UNRESOLVED', 'No declared conversion ' + src + ' -> ' + dst, { from: src, to: dst });
  },

  modelValue: function (model, params, x) {
    var order = Number(params.order);
    var k = Number(params.k);
    var c0 = Number(params.C0_mol_l);
    if (order === 0) { return Math.max(0, c0 - k * x); }
    if (order === 1) { return c0 * Math.exp(-k * x); }
    if (order === 2) { return c0 / (1 + k * c0 * x); }
    throw GraphError('E_GRAPH_UNKNOWN_MODEL', 'Unknown model: ' + model, { model: model });
  },

  gridPoints: function (grid) {
    var xMin = Number(grid.x_min);
    var xMax = Number(grid.x_max);
    var step = Number(grid.step);
    if (!(step > 0) || xMax < xMin) {
      throw GraphError('E_GRAPH_BAD_GRID', 'Declared grid is not usable', { grid: grid });
    }
    var count = Math.round((xMax - xMin) / step) + 1;
    var out = [];
    for (var index = 0; index < count; index += 1) { out.push(q12(xMin + index * step)); }
    return out;
  },

  rawPath: function (context, geometry, device) {
    var kind = geometry.kind;
    if (kind === 'empty') { return []; }
    var points = [];
    var i;
    if (kind === 'line') {
      var slope = Number(geometry.slope);
      var intercept = Number(geometry.intercept);
      var xMin = Number(geometry.x_min);
      var xMax = Number(geometry.x_max);
      points = [[xMin, q12(slope * xMin + intercept)], [xMax, q12(slope * xMax + intercept)]];
      return Engine.densify(points, context, device);
    }
    if (kind === 'polyline') {
      for (i = 0; i < geometry.points.length; i += 1) {
        points.push([Number(geometry.points[i][0]), Number(geometry.points[i][1])]);
      }
      return Engine.densify(points, context, device);
    }
    if (kind === 'model') {
      var gridX = Engine.gridPoints(context.grid);
      for (i = 0; i < gridX.length; i += 1) {
        points.push([gridX[i], q12(Engine.modelValue(geometry.model, geometry.params, gridX[i]))]);
      }
      return Engine.densify(points, context, device);
    }
    throw GraphError('E_GRAPH_UNKNOWN_GEOMETRY', 'Unknown geometry kind: ' + kind, { kind: kind });
  },

  densify: function (points, context, device) {
    if (device !== 'pointer' || points.length < 2) {
      var plain = [];
      for (var p = 0; p < points.length; p += 1) { plain.push([q12(points[p][0]), q12(points[p][1])]); }
      return plain;
    }
    var step = Number(context.grid.step) / 10;
    var out = [];
    for (var index = 0; index < points.length - 1; index += 1) {
      var x0 = points[index][0], y0 = points[index][1];
      var x1 = points[index + 1][0], y1 = points[index + 1][1];
      var span = Math.abs(x1 - x0);
      var count = span > 0 ? Math.max(1, Math.ceil(span / step)) : 1;
      for (var stepIndex = 0; stepIndex < count; stepIndex += 1) {
        var ratio = stepIndex / count;
        out.push([q12(x0 + (x1 - x0) * ratio), q12(y0 + (y1 - y0) * ratio)]);
      }
    }
    out.push([q12(points[points.length - 1][0]), q12(points[points.length - 1][1])]);
    return out;
  },

  project: function (path, grid) {
    if (path.length < 2) {
      var single = [];
      for (var s = 0; s < path.length; s += 1) { single.push({ x: q12(path[s][0]), y: q12(path[s][1]) }); }
      return single;
    }
    var gridX = Engine.gridPoints(grid);
    var values = new Map();
    for (var index = 0; index < path.length - 1; index += 1) {
      var x0 = path[index][0], y0 = path[index][1];
      var x1 = path[index + 1][0], y1 = path[index + 1][1];
      if (x1 === x0) { continue; }
      var low = x0 <= x1 ? x0 : x1;
      var high = x0 <= x1 ? x1 : x0;
      for (var g = 0; g < gridX.length; g += 1) {
        if (gridX[g] >= low - 1e-12 && gridX[g] <= high + 1e-12) {
          var ratio = (gridX[g] - x0) / (x1 - x0);
          values.set(gridX[g], y0 + (y1 - y0) * ratio);
        }
      }
    }
    if (!values.size) { return []; }
    var keys = Array.from(values.keys()).sort(function (a, b) { return a - b; });
    var out = [];
    for (var k = 0; k < keys.length; k += 1) { out.push({ x: q12(keys[k]), y: q12(values.get(keys[k])) }); }
    return out;
  },

  reversals: function (path) {
    if (path.length < 3) { return 0; }
    var reversals = 0;
    var direction = 0;
    for (var index = 0; index < path.length - 1; index += 1) {
      var delta = path[index + 1][0] - path[index][0];
      if (delta === 0) { continue; }
      var sign = delta > 0 ? 1 : -1;
      if (direction !== 0 && sign !== direction) { reversals += 1; }
      direction = sign;
    }
    return reversals;
  },

  /* The declared keyboard increments for a capture context.
   *
   * coarse_x is the grid step, so every grid point is reachable; coarse_y is
   * the y axis step. The fine steps are a tenth of the corresponding step and
   * are never coarser than half the declared tolerance band of the assessed
   * axis, so the keyboard path cannot be structurally penalised relative to
   * the pointer path. The rule is N18-CAPTURE-KEY-01.
   */
  keyboardIncrements: function (contextId) {
    var context = state.contract.capture_contract.capture_contexts[contextId];
    if (!context) {
      throw GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT', 'Unknown capture context: ' + contextId, { context: contextId });
    }
    var keyboard = context.keyboard || {};
    if (keyboard.y_axis_step === undefined || keyboard.y_axis_step === null) {
      throw GraphError('E_GRAPH_BAD_CAPTURE_CONTEXT',
        'Capture context declares no keyboard increments', { context: contextId });
    }
    var coarseX = Number(context.grid.step);
    var fineX = coarseX / 10;
    if (keyboard.x_tolerance_band !== null && keyboard.x_tolerance_band !== undefined) {
      fineX = Math.min(fineX, Number(keyboard.x_tolerance_band) / 2);
    }
    var coarseY = Number(keyboard.y_axis_step);
    var fineY = coarseY / 10;
    if (keyboard.y_tolerance_band !== null && keyboard.y_tolerance_band !== undefined) {
      fineY = Math.min(fineY, Number(keyboard.y_tolerance_band) / 2);
    }
    return {
      coarse_x: q12(coarseX), fine_x: q12(fineX),
      coarse_y: q12(coarseY), fine_y: q12(fineY)
    };
  },

  capturePath: function (contextId, path) {
    /* Build the device-agnostic capture payload from a raw path. The raw path
     * is the ordered list of points the learner drew or walked; pointer and
     * keyboard input both arrive here, so the payload cannot reveal which
     * device produced it. */
    var context = state.contract.capture_contract.capture_contexts[contextId];
    if (!context) {
      throw GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT', 'Unknown capture context: ' + contextId, { context: contextId });
    }
    var quantized = path.map(function (point) { return [q12(point[0]), q12(point[1])]; });
    return Engine.validatePayload({
      schema_id: PAYLOAD_SCHEMA_ID,
      kind: context.kind,
      points: Engine.project(quantized, context.grid),
      axes: context.axes,
      span: context.span,
      grid: context.grid,
      path_reversals: Engine.reversals(quantized)
    });
  },

  capture: function (contextId, geometry, device) {
    var context = state.contract.capture_contract.capture_contexts[contextId];
    if (!context) {
      throw GraphError('E_GRAPH_UNKNOWN_CAPTURE_CONTEXT', 'Unknown capture context: ' + contextId, { context: contextId });
    }
    var path = Engine.rawPath(context, geometry, device || 'pointer');
    var payload = {
      schema_id: PAYLOAD_SCHEMA_ID,
      kind: context.kind,
      points: Engine.project(path, context.grid),
      axes: context.axes,
      span: context.span,
      grid: context.grid,
      path_reversals: Engine.reversals(path)
    };
    return Engine.validatePayload(payload);
  },

  validatePayload: function (payload) {
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload is not an object', { check: 'payload_schema' });
    }
    if (payload.schema_id !== PAYLOAD_SCHEMA_ID) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload schema_id must be ' + PAYLOAD_SCHEMA_ID,
        { check: 'payload_schema' });
    }
    if (payload.kind !== 'line' && payload.kind !== 'segment') {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload kind is not declared', { check: 'payload_schema' });
    }
    if (!Array.isArray(payload.points)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload points must be an array', { check: 'payload_points' });
    }
    for (var i = 0; i < payload.points.length; i += 1) {
      var point = payload.points[i];
      if (!point || typeof point !== 'object' || !('x' in point) || !('y' in point)) {
        throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload point needs x and y', { check: 'payload_points' });
      }
      for (var axis = 0; axis < 2; axis += 1) {
        var key = axis === 0 ? 'x' : 'y';
        var value = point[key];
        if (typeof value !== 'number' || !isFinite(value)) {
          throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload point coordinate is not numeric',
            { check: 'payload_points' });
        }
      }
    }
    if (!payload.axes || typeof payload.axes !== 'object' || !payload.axes.x || !payload.axes.y) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axes are missing', { check: 'payload_axes' });
    }
    var axes = ['x', 'y'];
    for (var a = 0; a < axes.length; a += 1) {
      var bounds = payload.axes[axes[a]];
      if (!bounds || !('min' in bounds) || !('max' in bounds)) {
        throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axis bounds are missing', { check: 'payload_axes' });
      }
      if (Number(bounds.min) > Number(bounds.max)) {
        throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload axis bounds are inverted', { check: 'payload_axes' });
      }
    }
    if (!payload.span || typeof payload.span !== 'object' || !('x_min' in payload.span) || !('x_max' in payload.span)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span is missing', { check: 'payload_span' });
    }
    if (Number(payload.span.x_min) > Number(payload.span.x_max)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span is inverted', { check: 'payload_span' });
    }
    if (payload.span.edge_rule !== 'inclusive') {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload span edge_rule must be inclusive', { check: 'payload_span' });
    }
    if (!payload.grid || typeof payload.grid !== 'object' || !('x_min' in payload.grid) ||
      !('x_max' in payload.grid) || !('step' in payload.grid)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload grid is missing', { check: 'payload_span' });
    }
    if (Number(payload.grid.x_min) > Number(payload.grid.x_max)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload grid is not usable', { check: 'payload_span' });
    }
    if (!(Number(payload.grid.step) > 0)) {
      throw GraphError('E_GRAPH_PAYLOAD_MALFORMED', 'Payload grid is not usable', { check: 'payload_span' });
    }
    return payload;
  },

  figureRecord: function (figureId) {
    var record = state.figures[figureId];
    if (!record) {
      throw GraphError('E_GRAPH_UNKNOWN_FIGURE', 'Unknown figure: ' + figureId, { figure_id: figureId });
    }
    return record;
  },

  recordLine: function (record) {
    var line = record.fit_line || (record.grading_reference || {}).fit_line;
    if (!line) { throw GraphError('E_GRAPH_NO_CRITERION', 'Record declares no fit line', { figure_id: record.id }); }
    return line;
  },

  recordSpan: function (record) {
    if (record.span) {
      return {
        x_min: Number(record.span.x_min), x_max: Number(record.span.x_max),
        edge_rule: record.span.edge_rule || 'inclusive'
      };
    }
    var model = null;
    var series = record.series || [];
    for (var i = 0; i < series.length; i += 1) { if (series[i].curve_model) { model = series[i].curve_model; break; } }
    if (model) {
      var params = model.params || {};
      if ('t_min_s' in params && 't_max_s' in params) {
        return { x_min: Number(params.t_min_s), x_max: Number(params.t_max_s), edge_rule: 'inclusive' };
      }
      if ('V_max_ml' in params) {
        return { x_min: 0, x_max: Number(params.V_max_ml), edge_rule: 'inclusive' };
      }
    }
    var axes = record.axes || {};
    return {
      x_min: Number((axes.x || {}).min || 0), x_max: Number((axes.x || {}).max || 0), edge_rule: 'inclusive'
    };
  },

  recordAxes: function (record) {
    var axes = record.axes || {};
    return {
      x: { min: Number((axes.x || {}).min || 0), max: Number((axes.x || {}).max || 0) },
      y: { min: Number((axes.y || {}).min || 0), max: Number((axes.y || {}).max || 0) }
    };
  },

  readingCriterion: function (source) {
    if (source.kind === 'n05_payload') {
      var instance = source.instance;
      var payload = instance.payload;
      var readout = payload.target_readout;
      var xs = payload.points.map(function (point) { return Number(point.x); });
      var min = Math.min.apply(null, xs);
      var max = Math.max.apply(null, xs);
      return {
        criterion_id: source.criterion_id || instance.question_id || 'n05-graph',
        shape: 'n05_payload_readout',
        criterion_kind: 'constant',
        assessed_axis: 'y',
        position_axis: 'x',
        expected_value: Number(readout.expected_value),
        expected_unit: readout.unit === undefined ? '' : readout.unit,
        tolerance_class: readout.tolerance_class,
        tolerance_mode: 'absolute',
        sig_figs: null,
        span: { x_min: min, x_max: max, edge_rule: 'inclusive' },
        axes: null,
        position: null,
        position_fixed: false,
        cited: [{ kind: 'contract_rule', id: 'N18-N05-INHERIT-01', source: 'tools/golden_oracle.py (payload_class=graph branch)' }],
        answer_cross_check: null
      };
    }
    if (source.kind !== 'figure') {
      throw GraphError('E_GRAPH_UNKNOWN_SOURCE', 'Unknown reading source: ' + source.kind, { kind: source.kind });
    }
    var record = Engine.figureRecord(source.figure_id);
    var shapeName = source.criterion_shape;
    var shape = state.contract.criterion_shapes.reading[shapeName];
    if (!shape) {
      throw GraphError('E_GRAPH_UNKNOWN_SHAPE', 'Unknown reading shape: ' + shapeName, { shape: shapeName });
    }
    var criterion = {
      criterion_id: source.figure_id,
      shape: shapeName,
      assessed_axis: shape.assessed_axis,
      position_axis: shape.position_axis,
      expected_value: null,
      expected_unit: '',
      tolerance_class: '',
      tolerance_mode: shape.tolerance_mode || 'absolute',
      sig_figs: shape.sig_figs || null,
      span: Engine.recordSpan(record),
      axes: Engine.recordAxes(record),
      position: null,
      position_fixed: false,
      cited: [{
        kind: 'contract_rule', id: 'N18-SHAPE-' + shapeName,
        source: 'data/graph_scoring_contract.json#/criterion_shapes/reading/' + shapeName
      }],
      answer_cross_check: null
    };
    if (shapeName === 'calibration_line_signal_absolute' || shapeName === 'calibration_line_signal_sigfigs') {
      var line = Engine.recordLine(record);
      criterion.criterion_kind = 'line_function';
      criterion.slope = Number(line.slope);
      criterion.intercept = Number(line.intercept === undefined || line.intercept === null ? 0 : line.intercept);
      criterion.expected_unit = (record.axes.y || {}).unit || '';
      criterion.tolerance_class = shape.tolerance_class;
      criterion.tolerance_source = shape.tolerance_source;
    } else if (shapeName === 'calibration_line_concentration') {
      var calLine = Engine.recordLine(record);
      var calibration = record.calibration_spec || {};
      var signal = Number(calibration.unknown_signal);
      var calSlope = Number(calLine.slope);
      var calIntercept = Number(calLine.intercept === undefined || calLine.intercept === null ? 0 : calLine.intercept);
      var expected = calibration.model === 'through_zero_fixed_intercept'
        ? signal / calSlope : (signal - calIntercept) / calSlope;
      criterion.criterion_kind = 'inverse_line_function';
      criterion.slope = calSlope;
      criterion.intercept = calIntercept;
      criterion.expected_value = q12(expected);
      criterion.expected_unit = (record.axes.x || {}).unit || '';
      criterion.tolerance_class = record.tolerance_coupling.tolerance_class;
      criterion.tolerance_source = 'tolerances.quantity_classes[id=' + criterion.tolerance_class + ']';
      criterion.position = signal;
      criterion.position_fixed = true;
      var targets = record.answer_targets || [];
      if (targets.length) {
        criterion.answer_cross_check = {
          declared: targets[0].value, unit: targets[0].unit, recomputed: q12(expected)
        };
      }
    } else if (shapeName === 'titration_equivalence_volume') {
      var answerTargets = record.answer_targets || [];
      if (!answerTargets.length) {
        throw GraphError('E_GRAPH_NO_CRITERION', 'Titration record declares no answer target', { figure_id: record.id });
      }
      criterion.criterion_kind = 'constant';
      criterion.expected_value = Number(answerTargets[0].value);
      criterion.expected_unit = answerTargets[0].unit || (record.axes.x || {}).unit || '';
      criterion.tolerance_class = shape.tolerance_class;
      criterion.tolerance_source = shape.tolerance_source;
    } else {
      throw GraphError('E_GRAPH_UNKNOWN_SHAPE', 'Unsupported reading shape: ' + shapeName, { shape: shapeName });
    }
    return criterion;
  },

  drawingCriterion: function (record) {
    var fields = record.tolerance_fields || {};
    if (fields.slope) {
      var shapeName = 'kinetics_linearization_line';
      var line = Engine.recordLine(record);
      var cited = [{
        kind: 'record_tolerance_field', id: 'tolerance_fields.slope',
        conventions_ref: fields.slope.conventions_ref, mode: fields.slope.tolerance_mode,
        tolerance_class: fields.slope.tolerance_class
      }];
      ['intercept', 'point_acceptance'].forEach(function (name) {
        if (fields[name]) {
          cited.push({
            kind: 'record_tolerance_field', id: 'tolerance_fields.' + name,
            conventions_ref: fields[name].conventions_ref, mode: fields[name].tolerance_mode,
            tolerance_class: fields[name].tolerance_class
          });
        }
      });
      return {
        criterion_id: record.id, shape: shapeName, criterion_kind: 'line',
        slope: Number(line.slope),
        intercept: Number(line.intercept === undefined || line.intercept === null ? 0 : line.intercept),
        fields: fields,
        sample_count: state.contract.criterion_shapes.drawing[shapeName].sample_count || 11,
        span: Engine.recordSpan(record), axes: Engine.recordAxes(record),
        monotonicity: null, curvature: null, cited: cited, kind: 'line'
      };
    }
    if (record.calibration_spec && (record.fit_line || (record.grading_reference || {}).fit_line)) {
      var calShape = 'calibration_line_draw';
      var calShapeSpec = state.contract.criterion_shapes.drawing[calShape];
      var calLine = Engine.recordLine(record);
      var standards = [];
      var series = record.series || [];
      series.forEach(function (entry) {
        (entry.points || []).forEach(function (point) { standards.push(Number(point.x)); });
      });
      return {
        criterion_id: record.id, shape: calShape, criterion_kind: 'line',
        slope: Number(calLine.slope),
        intercept: Number(calLine.intercept === undefined || calLine.intercept === null ? 0 : calLine.intercept),
        fields: {
          point_acceptance: {
            tolerance_class: calShapeSpec.tolerance_class,
            tolerance_mode: calShapeSpec.tolerance_mode,
            conventions_ref: 'CIT-C7-CALIB'
          }
        },
        sample_x: standards, sample_count: null,
        span: Engine.recordSpan(record), axes: Engine.recordAxes(record),
        monotonicity: null, curvature: null,
        cited: [{
          kind: 'contract_rule', id: 'N18-SHAPE-' + calShape,
          source: 'data/graph_scoring_contract.json#/criterion_shapes/drawing/' + calShape
        }],
        kind: 'line'
      };
    }
    var model = null;
    var modelSeries = record.series || [];
    for (var i = 0; i < modelSeries.length; i += 1) {
      if (modelSeries[i].curve_model) { model = modelSeries[i].curve_model; break; }
    }
    if (model && model.function_class === 'kinetics_decay') {
      var segShape = 'kinetics_decay_segment';
      var segSpec = state.contract.criterion_shapes.drawing[segShape];
      var coupling = record.tolerance_coupling || {};
      return {
        criterion_id: record.id, shape: segShape, criterion_kind: 'model',
        model: model,
        fields: {
          point_acceptance: {
            tolerance_class: coupling.tolerance_class,
            tolerance_mode: segSpec.tolerance_mode || 'absolute',
            conventions_ref: coupling.conventions_ref
          }
        },
        sample_count: segSpec.sample_count || 11,
        span: Engine.recordSpan(record), axes: Engine.recordAxes(record),
        monotonicity: segSpec.monotonicity, curvature: segSpec.curvature,
        cited: [{
          kind: 'contract_rule', id: 'N18-SHAPE-' + segShape,
          source: 'data/graph_scoring_contract.json#/criterion_shapes/drawing/' + segShape
        }],
        kind: 'segment'
      };
    }
    throw GraphError('E_GRAPH_NO_CRITERION', 'Record declares no drawable criterion shape', { figure_id: record.id });
  },

  criteriaFromRubric: function (rubric) {
    var items = rubric || [];
    var auto = [];
    var pending = [];
    items.forEach(function (item) {
      var isAuto = (item.grading === 'auto' || item.grading === 'mixed') &&
        item.engine_binding !== 'self-assessed' && item.engine_binding !== 'human-review';
      if (isAuto) { auto.push(item); } else { pending.push(item); }
    });
    return { auto: auto, pending: pending };
  },

  assembleVerdict: function (family, criterionId, verdictClass, errorClass, awarded, rubric,
    cited, criterion, geometry, validity, capture, replay) {
    var split = Engine.criteriaFromRubric(rubric);
    var awardedCriteria = [];
    var machinePoints = 0;
    var pendingPoints = 0;
    var maxPoints = 0;
    split.pending.forEach(function (item) {
      var points = Number(item.points || 0);
      maxPoints += points;
      pendingPoints += points;
      awardedCriteria.push({
        criterion_id: item.criterion_id, status: 'pending',
        awarded_points: 0, pending_points: points, max_points: points
      });
    });
    split.auto.forEach(function (item) {
      var points = Number(item.points || 0);
      maxPoints += points;
      var given = awarded ? points : 0;
      machinePoints += given;
      awardedCriteria.push({
        criterion_id: item.criterion_id, status: awarded ? 'awarded' : 'denied',
        awarded_points: given, pending_points: 0, max_points: points
      });
    });
    awardedCriteria.sort(function (a, b) {
      return a.criterion_id < b.criterion_id ? -1 : (a.criterion_id > b.criterion_id ? 1 : 0);
    });
    return {
      verdict_class: verdictClass, error_class: errorClass, awarded_criteria: awardedCriteria,
      machine_checked_points: machinePoints, self_assessed_points: 0, human_reviewed_points: 0,
      pending_points: pendingPoints, max_points: maxPoints,
      oracle_version: ORACLE_VERSION,
      oracle_digest: (state.contract && state.contract.oracle_digest) || ORACLE_VERSION,
      conventions_digest: state.conventionsDigest || '',
      family: family, criterion_id: criterionId, criterion_shape: criterion.shape,
      cited_entries: cited, criterion: criterion, assessed_geometry: geometry,
      validity: validity, capture: capture, replay: replay
    };
  },

  invalidReading: function (criterion, cited, rubric, errorClass, check, trace, assessedValue, position) {
    trace.push({ check: check, result: 'fail', error_class: errorClass });
    var validity = { class: errorClass, reason_lv: null, trace: trace };
    var geometry = {
      assessed_axis: criterion.assessed_axis, position_axis: criterion.position_axis,
      assessed_value: assessedValue === null || assessedValue === undefined ? null : q12(assessedValue),
      expected_value: null,
      position: position === null || position === undefined ? null : q12(position),
      deviation: null, tolerance: null, within_tolerance: false, span: criterion.span
    };
    var replay = {
      family: 'reading',
      criterion: {
        criterion_kind: criterion.criterion_kind, criterion_id: criterion.criterion_id,
        span: criterion.span, axes: criterion.axes,
        assessed_axis: criterion.assessed_axis, position_axis: criterion.position_axis
      },
      geometry: {
        assessed_value: assessedValue === null || assessedValue === undefined ? null : q12(assessedValue),
        position: position === null || position === undefined ? null : q12(position)
      },
      error_class: errorClass, cited_entries: cited
    };
    return Engine.assembleVerdict('reading', criterion.criterion_id, 'incorrect', errorClass, false,
      rubric, cited, criterion, geometry, validity, null, replay);
  },

  scoreReading: function (source, submission, rubric) {
    var criterion = Engine.readingCriterion(source);
    var cited = criterion.cited.slice();
    cited.push({ kind: 'contract_rule', id: 'N18-TOLERANCE-01', source: 'data/graph_scoring_contract.json#/tolerance_resolution' });
    cited.push({ kind: 'inherited_rule', id: 'N15-NOEXTRAP-01', source: 'data/calibration_contract.json#/no_extrapolation_rule' });
    cited.push({ kind: 'inherited_rule', id: 'N14-SPAN-01', source: 'data/kinetics_linearization_contract.json#/span_rule' });

    var assessedAxis = criterion.assessed_axis;
    var positionAxis = criterion.position_axis;
    var trace = [];
    var assessedValue = null;
    var position = null;
    var submittedUnit = null;

    if (source.kind === 'n05_payload') {
      assessedValue = parseNumber(submission.value);
      if (assessedValue === null) {
        return Engine.invalidReading(criterion, cited, rubric, 'UNREADABLE_INPUT', 'submission_value', trace);
      }
      submittedUnit = submission.unit === undefined ? criterion.expected_unit : submission.unit;
      if ('x' in submission && submission.x !== null && submission.x !== undefined) {
        position = parseNumber(submission.x);
        if (position === null) {
          return Engine.invalidReading(criterion, cited, rubric, 'UNREADABLE_INPUT', 'submission_x', trace);
        }
      }
    } else {
      assessedValue = parseNumber(submission[assessedAxis]);
      position = parseNumber(submission[positionAxis]);
      if (assessedValue === null || position === null) {
        return Engine.invalidReading(criterion, cited, rubric, 'UNREADABLE_INPUT', 'submission_point', trace);
      }
    }

    var axes = criterion.axes;
    if (axes) {
      var coordinate = {
        x: positionAxis === 'x' ? position : assessedValue,
        y: positionAxis === 'y' ? position : assessedValue
      };
      var axisNames = ['x', 'y'];
      for (var i = 0; i < axisNames.length; i += 1) {
        var name = axisNames[i];
        var value = coordinate[name];
        var bounds = axes[name];
        if (value < bounds.min || value > bounds.max) {
          trace.push({ check: 'axis_range', axis: name, value: value, bounds: bounds, result: 'fail' });
          return Engine.invalidReading(criterion, cited, rubric, 'E_GRAPH_OUT_OF_AXIS_RANGE', 'axis_range',
            trace, assessedValue, position);
        }
      }
    }
    trace.push({ check: 'axis_range', result: 'pass' });

    var span = criterion.span;
    var xValue = assessedAxis === 'x' ? assessedValue : position;
    if (xValue !== null && xValue !== undefined && (xValue < span.x_min || xValue > span.x_max)) {
      trace.push({ check: 'span', x: xValue, span: span, result: 'fail' });
      return Engine.invalidReading(criterion, cited, rubric, 'OUT_OF_DOMAIN_EXTRAPOLATION', 'span',
        trace, assessedValue, position);
    }
    trace.push({ check: 'span', span: span, result: 'pass' });

    var expected = criterion.expected_value;
    if (criterion.criterion_kind === 'line_function') {
      expected = q12(criterion.slope * (position === null ? 0 : position) + criterion.intercept);
    } else if (criterion.criterion_kind === 'inverse_line_function') {
      var signal = position === null ? 0 : position;
      expected = q12((signal - (criterion.intercept === null || criterion.intercept === undefined ? 0 : criterion.intercept)) / criterion.slope);
    }
    if (expected === null || expected === undefined) {
      throw GraphError('E_GRAPH_NO_EXPECTED_VALUE', 'Reading criterion has no expected value',
        { criterion_id: criterion.criterion_id });
    }

    var resolved = Engine.resolveTolerance(criterion.tolerance_class, criterion.tolerance_mode, expected, criterion.sig_figs);
    cited = cited.concat(resolved.cited);
    var tolerance = resolved.tolerance;

    var assessedUnit = criterion.expected_unit;
    var classEntry = toleranceClass(criterion.tolerance_class);
    if (classEntry.unit && assessedUnit && classEntry.unit !== assessedUnit) {
      var factor = Engine.unitFactor(classEntry.unit, assessedUnit);
      tolerance = q12(tolerance * factor);
      cited.push({
        kind: 'contract_rule', id: 'N18-UNIT-' + classEntry.unit + '->' + assessedUnit,
        source: 'conventions.unit_system.conversions', factor: factor
      });
    }

    if (source.kind === 'n05_payload') {
      var targetUnit = criterion.expected_unit;
      if (submittedUnit !== null && submittedUnit !== undefined &&
        String(submittedUnit).replace(/\s+/g, ' ').trim() !== String(targetUnit).replace(/\s+/g, ' ').trim()) {
        var convertFactor = Engine.unitFactor(submittedUnit, targetUnit);
        assessedValue = q12(assessedValue * convertFactor);
        cited.push({
          kind: 'contract_rule', id: 'N18-UNIT-' + submittedUnit + '->' + targetUnit,
          source: 'conventions.unit_system.conversions', factor: convertFactor
        });
      }
    }
    var deviation = Math.abs(assessedValue - expected);
    var within = deviation <= tolerance;
    cited.push({ kind: 'contract_rule', id: 'N18-CITED-ENTRY-01', source: 'data/graph_scoring_contract.json#/cited_entry_rule' });

    var geometry = {
      assessed_axis: assessedAxis, position_axis: positionAxis,
      assessed_value: q12(assessedValue), expected_value: q12(expected),
      position: position === null || position === undefined ? null : q12(position),
      deviation: q12(deviation), tolerance: tolerance, within_tolerance: within,
      span: span, answer_cross_check: criterion.answer_cross_check
    };
    var replay = {
      family: 'reading',
      criterion: {
        criterion_kind: criterion.criterion_kind, expected_value: q12(expected),
        slope: criterion.slope === undefined ? null : criterion.slope,
        intercept: criterion.intercept === undefined ? null : criterion.intercept,
        tolerance_class: criterion.tolerance_class, tolerance_mode: criterion.tolerance_mode,
        sig_figs: criterion.sig_figs, tolerance: tolerance,
        assessed_axis: assessedAxis, position_axis: positionAxis, span: span
      },
      geometry: {
        assessed_value: q12(assessedValue),
        position: position === null || position === undefined ? null : q12(position)
      },
      cited_entries: cited
    };
    return Engine.assembleVerdict('reading', criterion.criterion_id,
      within ? 'correct' : 'incorrect', within ? 'NONE' : 'OUT_OF_TOLERANCE', within,
      rubric, cited, criterion, geometry, { class: null, reason_lv: null, trace: trace }, null, replay);
  },

  invalidDrawing: function (criterion, cited, rubric, errorClass, check, trace, points) {
    trace.push({ check: check, result: 'fail', error_class: errorClass });
    var validity = { class: errorClass, reason_lv: null, trace: trace };
    var geometry = {
      assessed_x_range: null, points: points, excluded_points: [], sample_x: [], deviations: [],
      max_deviation: null, slope: null, intercept: null, checks: {}
    };
    var replay = {
      family: 'drawing', criterion: Engine.replayCriterion(criterion),
      geometry: { points: points }, cited_entries: cited
    };
    return Engine.assembleVerdict('drawing', criterion.criterion_id, 'incorrect', errorClass, false,
      rubric, cited, criterion, geometry, validity, null, replay);
  },

  captureMeta: function (payload) {
    return {
      digest: canonicalDigest(payload), kind: payload.kind,
      point_count: (payload.points || []).length, grid: payload.grid, span: payload.span,
      device_agnostic: true
    };
  },

  fitLine: function (points) {
    var count = points.length;
    var sumX = 0, sumY = 0, i;
    for (i = 0; i < count; i += 1) { sumX += points[i].x; sumY += points[i].y; }
    var meanX = sumX / count, meanY = sumY / count;
    var sxy = 0, sxx = 0;
    for (i = 0; i < count; i += 1) {
      sxy += (points[i].x - meanX) * (points[i].y - meanY);
      sxx += (points[i].x - meanX) * (points[i].x - meanX);
    }
    if (sxx === 0) { return { slope: 0, intercept: meanY }; }
    var slope = sxy / sxx;
    return { slope: slope, intercept: meanY - slope * meanX };
  },

  interpolate: function (points, x) {
    if (points.length === 1) { return points[0].y; }
    if (x <= points[0].x) { return points[0].y; }
    if (x >= points[points.length - 1].x) { return points[points.length - 1].y; }
    for (var index = 0; index < points.length - 1; index += 1) {
      var x0 = points[index].x, y0 = points[index].y;
      var x1 = points[index + 1].x, y1 = points[index + 1].y;
      if (x0 <= x && x <= x1) {
        if (x1 === x0) { return y0; }
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0);
      }
    }
    return points[points.length - 1].y;
  },

  sampleX: function (criterion, assessed) {
    var span = criterion.span;
    if (criterion.sample_x && criterion.sample_x.length) {
      return criterion.sample_x
        .filter(function (x) { return x >= span.x_min && x <= span.x_max; })
        .map(function (x) { return q12(x); });
    }
    var count = Number(criterion.sample_count || 11);
    var xMin = assessed[0].x, xMax = assessed[assessed.length - 1].x;
    if (xMax <= xMin) { return [q12(xMin)]; }
    var out = [];
    for (var index = 0; index < count; index += 1) {
      out.push(q12(xMin + (xMax - xMin) * index / (count - 1)));
    }
    return out;
  },

  resolveFields: function (criterion) {
    var resolved = {};
    var fields = criterion.fields || {};
    /* The field names are sorted: the shipped island stores its keys sorted,
     * the source files do not, and the citation order must not depend on it. */
    Object.keys(fields).sort().forEach(function (name) {
      var field = fields[name];
      var mode = field.tolerance_mode || 'absolute';
      var reference = null;
      if (name === 'slope') { reference = criterion.slope; }
      else if (name === 'intercept') { reference = criterion.intercept; }
      else if (criterion.slope !== undefined && criterion.slope !== null) { reference = criterion.slope; }
      var entry = Engine.resolveTolerance(field.tolerance_class, mode, reference, field.sig_figs);
      if (mode === 'absolute' && field.abs_value !== undefined && field.abs_value !== null) {
        if (Math.abs(Number(field.abs_value) - entry.tolerance) > 1e-12) {
          throw GraphError('E_GRAPH_TOLERANCE_DRIFT', 'Record tolerance field drifted from the conventions entry',
            { field: name, declared: Number(field.abs_value), resolved: entry.tolerance, tolerance_class: field.tolerance_class });
        }
      }
      resolved[name] = entry;
    });
    return resolved;
  },

  replayCriterion: function (criterion) {
    return {
      criterion_id: criterion.criterion_id, shape: criterion.shape,
      criterion_kind: criterion.criterion_kind,
      slope: criterion.slope === undefined ? null : criterion.slope,
      intercept: criterion.intercept === undefined ? null : criterion.intercept,
      model: criterion.model === undefined ? null : criterion.model,
      span: criterion.span, fields: criterion.fields || null,
      sample_x: criterion.sample_x || null, sample_count: criterion.sample_count || null,
      monotonicity: criterion.monotonicity || null
    };
  },

  scoreDrawing: function (record, payload, rubric) {
    payload = Engine.validatePayload(payload);
    var criterion = Engine.drawingCriterion(record);
    var cited = criterion.cited.slice();
    cited.push({ kind: 'contract_rule', id: 'N18-TOLERANCE-01', source: 'data/graph_scoring_contract.json#/tolerance_resolution' });
    cited.push({ kind: 'inherited_rule', id: 'N14-SPAN-01', source: 'data/kinetics_linearization_contract.json#/span_rule' });
    cited.push({ kind: 'inherited_rule', id: 'N15-NOEXTRAP-01', source: 'data/calibration_contract.json#/no_extrapolation_rule' });

    var points = payload.points.map(function (point) { return { x: Number(point.x), y: Number(point.y) }; });
    var trace = [];

    if (points.length < 2) {
      trace.push({ check: 'point_count', count: points.length, result: 'fail' });
      return Engine.invalidDrawing(criterion, cited, rubric, 'E_GRAPH_EMPTY_SUBMISSION', 'point_count', trace, points);
    }
    trace.push({ check: 'point_count', count: points.length, result: 'pass' });

    var axes = criterion.axes;
    var outside = false;
    for (var i = 0; i < points.length && !outside; i += 1) {
      var axisNames = ['x', 'y'];
      for (var a = 0; a < axisNames.length; a += 1) {
        var name = axisNames[a];
        var value = points[i][name];
        var bounds = axes[name];
        if (value < bounds.min || value > bounds.max) {
          trace.push({ check: 'axis_range', axis: name, value: value, bounds: bounds, result: 'fail' });
          outside = true;
          break;
        }
      }
    }
    if (outside) {
      return Engine.invalidDrawing(criterion, cited, rubric, 'E_GRAPH_OUT_OF_AXIS_RANGE', 'axis_range', trace, points);
    }
    trace.push({ check: 'axis_range', result: 'pass' });

    var span = criterion.span;
    var assessed = points.filter(function (point) { return point.x >= span.x_min && point.x <= span.x_max; });
    var excluded = points.filter(function (point) { return !(point.x >= span.x_min && point.x <= span.x_max); });
    if (!assessed.length) {
      trace.push({ check: 'assessed_geometry', span: span, result: 'empty' });
      var geometry = {
        assessed_x_range: null, points: [], excluded_points: excluded, sample_x: [], deviations: [],
        max_deviation: null, slope: null, intercept: null, checks: {}
      };
      var replay = {
        family: 'drawing', criterion: Engine.replayCriterion(criterion),
        geometry: { points: points }, cited_entries: cited
      };
      return Engine.assembleVerdict('drawing', criterion.criterion_id, 'not_assessed', 'NOT_ASSESSED', false,
        rubric, cited, criterion, geometry, { class: 'NOT_ASSESSED', reason_lv: null, trace: trace },
        Engine.captureMeta(payload), replay);
    }
    trace.push({ check: 'assessed_geometry', span: span, count: assessed.length, result: 'pass' });

    var fit = Engine.fitLine(assessed);
    var drawnSlope = fit.slope, drawnIntercept = fit.intercept;
    var criterionSlope = criterion.slope === undefined ? null : criterion.slope;
    if (criterionSlope !== null && criterionSlope !== 0) {
      if ((drawnSlope >= 0) !== (criterionSlope > 0) || drawnSlope === 0) {
        trace.push({ check: 'slope_sign', drawn_slope: drawnSlope, criterion_slope: criterionSlope, result: 'fail' });
        return Engine.invalidDrawing(criterion, cited, rubric, 'E_GRAPH_WRONG_DIRECTION', 'slope_sign', trace, points);
      }
    }
    trace.push({ check: 'slope_sign', drawn_slope: drawnSlope, criterion_slope: criterionSlope, result: 'pass' });

    if (Number(payload.path_reversals || 0) > 0) {
      trace.push({ check: 'path_reversals', reversals: payload.path_reversals, result: 'fail' });
      return Engine.invalidDrawing(criterion, cited, rubric, 'E_GRAPH_DOUBLE_BACK', 'path_reversals', trace, points);
    }
    trace.push({ check: 'path_reversals', reversals: payload.path_reversals, result: 'pass' });

    if (criterion.monotonicity) {
      var monotone = true;
      for (var m = 1; m < assessed.length; m += 1) {
        if (criterion.monotonicity === 'decreasing') {
          if (assessed[m].y > assessed[m - 1].y + 1e-12) { monotone = false; break; }
        } else if (assessed[m].y < assessed[m - 1].y - 1e-12) { monotone = false; break; }
      }
      if (!monotone) {
        trace.push({ check: 'monotonicity', monotonicity: criterion.monotonicity, result: 'fail' });
        return Engine.invalidDrawing(criterion, cited, rubric, 'E_GRAPH_NON_MONOTONIC', 'monotonicity', trace, points);
      }
      trace.push({ check: 'monotonicity', monotonicity: criterion.monotonicity, result: 'pass' });
    }

    var sampleX = Engine.sampleX(criterion, assessed);
    var criterionY = [];
    var drawnY = [];
    var deviations = [];
    for (var s = 0; s < sampleX.length; s += 1) {
      var truth = criterion.criterion_kind === 'model'
        ? q12(Engine.modelValue('kinetics_decay', criterion.model.params, sampleX[s]))
        : q12(criterion.slope * sampleX[s] + criterion.intercept);
      var drawn = q12(Engine.interpolate(assessed, sampleX[s]));
      criterionY.push(truth);
      drawnY.push(drawn);
      deviations.push(q12(Math.abs(drawn - truth)));
    }
    var maxDeviation = deviations.length ? Math.max.apply(null, deviations) : 0;

    var checks = {};
    var tolerances = {};
    var resolvedFields = Engine.resolveFields(criterion);
    Object.keys(resolvedFields).forEach(function (name) {
      tolerances[name] = resolvedFields[name].tolerance;
      cited = cited.concat(resolvedFields[name].cited);
    });
    if ('slope' in resolvedFields) {
      checks.slope = Math.abs(drawnSlope - criterion.slope) <= tolerances.slope + 1e-12;
    }
    if ('intercept' in resolvedFields) {
      checks.intercept = Math.abs(drawnIntercept - criterion.intercept) <= tolerances.intercept + 1e-12;
    }
    if ('point_acceptance' in resolvedFields) {
      checks.point_acceptance = maxDeviation <= tolerances.point_acceptance + 1e-12;
    }
    var accepted = Object.keys(checks).length ? Object.keys(checks).every(function (key) { return checks[key]; }) : false;

    cited.push({ kind: 'contract_rule', id: 'N18-CITED-ENTRY-01', source: 'data/graph_scoring_contract.json#/cited_entry_rule' });
    var drawingGeometry = {
      assessed_x_range: { x_min: q12(assessed[0].x), x_max: q12(assessed[assessed.length - 1].x) },
      points: assessed, excluded_points: excluded,
      excluded_note_lv: 'Ģeometrija ārpus deklarētā diapazona netiek vērtēta (N14-SPAN-01, N15-NOEXTRAP-01).',
      sample_x: sampleX, criterion_y: criterionY, drawn_y: drawnY, deviations: deviations,
      max_deviation: maxDeviation, slope: q12(drawnSlope), intercept: q12(drawnIntercept),
      checks: checks, tolerances: tolerances
    };
    var drawingReplay = {
      family: 'drawing', criterion: Engine.replayCriterion(criterion),
      geometry: {
        points: assessed, sample_x: sampleX, criterion_y: criterionY, drawn_y: drawnY,
        slope: q12(drawnSlope), intercept: q12(drawnIntercept)
      },
      cited_entries: cited
    };
    return Engine.assembleVerdict('drawing', criterion.criterion_id,
      accepted ? 'correct' : 'incorrect', accepted ? 'NONE' : 'OUT_OF_TOLERANCE', accepted,
      rubric, cited, criterion, drawingGeometry, { class: null, reason_lv: null, trace: trace },
      Engine.captureMeta(payload), drawingReplay);
  },

  replayVerdict: function (verdict) {
    var replay = verdict.replay || {};
    var family = replay.family;
    var criterion = replay.criterion || {};
    var geometry = replay.geometry || {};
    if (family === 'reading') {
      var errorClass = replay.error_class || null;
      var assessed = geometry.assessed_value;
      var position = geometry.position === undefined ? null : geometry.position;
      var span = criterion.span || {};
      var axes = criterion.axes;
      if (errorClass) {
        if (errorClass === 'OUT_OF_DOMAIN_EXTRAPOLATION') {
          var xValue = criterion.assessed_axis === 'x' ? assessed : position;
          var out = xValue !== null && xValue !== undefined &&
            (xValue < span.x_min || xValue > span.x_max);
          return {
            replayable: true, verdict_class: 'incorrect',
            error_class: out ? 'OUT_OF_DOMAIN_EXTRAPOLATION' : 'REPLAY_MISMATCH'
          };
        }
        if (errorClass === 'E_GRAPH_OUT_OF_AXIS_RANGE' && axes) {
          var coordinate = {
            x: criterion.position_axis === 'x' ? position : assessed,
            y: criterion.position_axis === 'y' ? position : assessed
          };
          var outOfRange = false;
          ['x', 'y'].forEach(function (name) {
            var value = coordinate[name];
            if (value === null || value === undefined) { return; }
            var bounds = axes[name] || {};
            if (value < bounds.min || value > bounds.max) { outOfRange = true; }
          });
          return {
            replayable: true, verdict_class: 'incorrect',
            error_class: outOfRange ? 'E_GRAPH_OUT_OF_AXIS_RANGE' : 'REPLAY_MISMATCH'
          };
        }
        return { replayable: false, verdict_class: null, error_class: errorClass };
      }
      var expected = criterion.expected_value;
      var tolerance = criterion.tolerance;
      if (criterion.criterion_kind === 'line_function' && position !== null) {
        expected = q12(criterion.slope * position + criterion.intercept);
      } else if (criterion.criterion_kind === 'inverse_line_function' && position !== null) {
        expected = q12((position - (criterion.intercept || 0)) / criterion.slope);
      }
      var deviation = Math.abs(assessed - expected);
      var within = deviation <= tolerance + 1e-12;
      return {
        replayable: true, verdict_class: within ? 'correct' : 'incorrect',
        error_class: within ? 'NONE' : 'OUT_OF_TOLERANCE', deviation: q12(deviation)
      };
    }
    if (family === 'drawing') {
      var checks = {};
      var fields = criterion.fields || {};
      if (fields.slope) {
        checks.slope = Math.abs(geometry.slope - criterion.slope) <=
          Engine.resolveTolerance(fields.slope.tolerance_class, fields.slope.tolerance_mode || 'absolute',
            criterion.slope, fields.slope.sig_figs).tolerance + 1e-12;
      }
      if (fields.intercept) {
        checks.intercept = Math.abs(geometry.intercept - criterion.intercept) <=
          Engine.resolveTolerance(fields.intercept.tolerance_class, fields.intercept.tolerance_mode || 'absolute',
            criterion.intercept, fields.intercept.sig_figs).tolerance + 1e-12;
      }
      if (fields.point_acceptance) {
        var devs = [];
        var drawn = geometry.drawn_y || [];
        var truth = geometry.criterion_y || [];
        for (var d = 0; d < drawn.length && d < truth.length; d += 1) { devs.push(Math.abs(drawn[d] - truth[d])); }
        checks.point_acceptance = (devs.length ? Math.max.apply(null, devs) : 0) <=
          Engine.resolveTolerance(fields.point_acceptance.tolerance_class,
            fields.point_acceptance.tolerance_mode || 'absolute', criterion.slope,
            fields.point_acceptance.sig_figs).tolerance + 1e-12;
      }
      var accepted = Object.keys(checks).length ?
        Object.keys(checks).every(function (key) { return checks[key]; }) : false;
      return {
        verdict_class: accepted ? 'correct' : 'incorrect',
        error_class: accepted ? 'NONE' : 'OUT_OF_TOLERANCE', checks: checks
      };
    }
    throw GraphError('E_GRAPH_UNKNOWN_REPLAY', 'Unknown replay family: ' + family, { family: family });
  }
};

root.SimGraphScoring = {
  ISLAND_ID: CONTRACT_ID,
  PAYLOAD_SCHEMA_ID: PAYLOAD_SCHEMA_ID,
  ORACLE_VERSION: ORACLE_VERSION,
  load: load,
  state: state,
  resolveTolerance: function (toleranceClass, mode, value, sigFigs) { return Engine.resolveTolerance(toleranceClass, mode, value, sigFigs); },
  unitFactor: function (from, to) { return Engine.unitFactor(from, to); },
  capture: function (contextId, geometry, device) { return Engine.capture(contextId, geometry, device); },
  capturePath: function (contextId, path) { return Engine.capturePath(contextId, path); },
  keyboardIncrements: function (contextId) { return Engine.keyboardIncrements(contextId); },
  validatePayload: function (payload) { return Engine.validatePayload(payload); },
  scoreReading: function (source, submission, rubric) { return Engine.scoreReading(source, submission, rubric); },
  scoreDrawing: function (record, payload, rubric) { return Engine.scoreDrawing(record, payload, rubric); },
  replayVerdict: function (verdict) { return Engine.replayVerdict(verdict); },
  canonicalProjection: canonicalProjection,
  canonicalDigest: canonicalDigest,
  sha256: sha256,
  q12: q12
};

if (typeof module !== 'undefined' && module.exports) { module.exports = root.SimGraphScoring; }
})(typeof globalThis !== 'undefined' ? globalThis : this);
