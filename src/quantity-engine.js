(function (root) {
'use strict';
/* N17 runtime engine. Same logic as tools/quantity_engine.py, consuming only
 * #sim-conventions, #sim-terms and #sim-engines. No local scientific constants. */
var CONVENTIONS_ID = 'sim-conventions';
var TERMS_ID = 'sim-terms';
var TAXONOMY_ID = 'sim-engines';
var state = { conventions: null, taxonomy: null, terms: null, grammar: null };

function fail(code, message) { var e = new Error(message); e.code = code; return e; }
function round12(x) { return Number(x.toFixed(12)); }
function normUnit(u) { return String(u == null ? '' : u).trim().replace(/\s+/g, ' '); }
function dimKey(d) {
  var keys = Object.keys(d || {}).filter(function (k) { return d[k] !== 0; }).sort();
  return keys.map(function (k) { return k + ':' + d[k]; });
}
function dimEqual(a, b) { return JSON.stringify(dimKey(a)) === JSON.stringify(dimKey(b)); }

var SUP = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','⁻':'-','⁺':'+'};
function translateExp(token) {
  if (!token) return 1;
  if (/^[+-]?\d+$/.test(token)) return parseInt(token, 10);
  var out = '', i;
  for (i = 0; i < token.length; i += 1) out += (SUP[token[i]] !== undefined ? SUP[token[i]] : token[i]);
  if (/^[+-]?\d+$/.test(out)) return parseInt(out, 10);
  throw fail('E_ENG_UNIT', 'Unreadable unit exponent: ' + token);
}

function load(doc) {
  if (state.conventions) return state.conventions;
  doc = doc || root.document;
  function island(id) {
    if (!doc || !doc.getElementById) throw fail('E_ENG_MISSING', 'Island #' + id + ' nav atrasta.');
    var node = doc.getElementById(id);
    if (!node) throw fail('E_ENG_MISSING', 'Island #' + id + ' nav atrasta.');
    try { return JSON.parse(node.textContent || ''); }
    catch (error) { throw fail('E_ENG_JSON', 'Island #' + id + ' nav derīgs JSON.'); }
  }
  var conventions = island(CONVENTIONS_ID);
  var terms = island(TERMS_ID);
  var taxonomy = island(TAXONOMY_ID);
  if (!conventions.unit_system || !Array.isArray(conventions.unit_system.conversions) ||
      !taxonomy.error_taxonomy || !Array.isArray(taxonomy.error_taxonomy.classes) ||
      !terms.unit_grammar || !Array.isArray(terms.unit_grammar.elements)) {
    throw fail('E_ENG_SHAPE', 'Nepareiza dzinēja salu forma.');
  }
  state.conventions = conventions;
  state.terms = terms;
  state.taxonomy = taxonomy;
  state.grammar = terms.unit_grammar;
  return conventions;
}

function classes() { load(); return state.taxonomy.error_taxonomy.classes; }
function n05Map() {
  var out = Object.create(null), list = classes(), i, j;
  for (i = 0; i < list.length; i += 1) {
    for (j = 0; j < list[i].n05_error_classes.length; j += 1) {
      out[list[i].n05_error_classes[j]] = {
        taxonomy_class: list[i].id, signature: list[i].signature, feedback_key: list[i].feedback_key
      };
    }
  }
  return out;
}
function fallback() { return state.taxonomy.error_taxonomy.fallback; }

function parseUnit(unit) {
  load();
  if (unit === null || unit === undefined || !String(unit).trim()) throw fail('E_ENG_UNREADABLE', 'Trūkst vienības izteiksmes.');
  var symbols = Object.create(null), list = state.grammar.elements, i;
  for (i = 0; i < list.length; i += 1) symbols[String(list[i].symbol)] = list[i].dimension_vector || {};
  var dimensionless = {};
  (state.grammar.dimensionless_tokens || []).forEach(function (t) { dimensionless[t] = true; });
  var raw = normUnit(unit).replace(/×/g, '·').replace(/\*/g, '·');
  if (dimensionless[raw]) return {};
  var numerator = raw, denominator = '';
  if (raw.indexOf('(') >= 0 || raw.indexOf(')') >= 0) {
    var lp = raw.indexOf('('), rp = raw.indexOf(')');
    if (lp < 0 || rp < 0 || raw.indexOf('(', lp + 1) >= 0 || raw.indexOf(')', rp + 1) >= 0) {
      throw fail('E_ENG_UNREADABLE', 'Neatbalstīta vienību grupa: ' + unit);
    }
    var left = raw.slice(0, lp), group = raw.slice(lp + 1, rp), right = raw.slice(rp + 1);
    if (left.indexOf('/') < 0) throw fail('E_ENG_UNREADABLE', 'Neatbalstīta vienību grupa: ' + unit);
    numerator = left.split('/')[0].trim();
    denominator = group.trim() + ' ' + right.trim();
  } else if (raw.indexOf('/') >= 0) {
    var parts = raw.split('/');
    numerator = parts[0];
    denominator = parts.slice(1).join('/');
  }
  var result = Object.create(null);
  function absorb(expr, sign) {
    var pieces = expr.split('·').filter(function (p) { return p.trim(); });
    if (!pieces.length) throw fail('E_ENG_UNREADABLE', 'Tukšs vienības faktors: ' + unit);
    pieces.forEach(function (piece0) {
      var piece = piece0.trim(), symbol = piece, exponent = 1;
      var m = /^(.*?)\^([+-]?\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)$/.exec(piece);
      if (m) { symbol = m[1].trim(); exponent = translateExp(m[2]); }
      else {
        m = /^(.*?)([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)$/.exec(piece);
        if (m && symbols[m[1]]) { symbol = m[1]; exponent = translateExp(m[2]); }
      }
      if (dimensionless[symbol]) return;
      if (!symbols[symbol]) throw fail('E_ENG_UNREADABLE', 'Nezināms vienības simbols: ' + symbol);
      var vec = symbols[symbol];
      Object.keys(vec).forEach(function (k) {
        result[k] = (result[k] || 0) + sign * exponent * vec[k];
      });
    });
  }
  absorb(numerator, 1);
  if (denominator.trim()) absorb(denominator, -1);
  Object.keys(result).forEach(function (k) { if (result[k] === 0) delete result[k]; });
  return result;
}

function classifyError(n05, detail) {
  var mapped = n05Map()[n05] || {
    taxonomy_class: (fallback().code || 'UNREADABLE_INPUT'),
    signature: fallback().signature,
    feedback_key: fallback().feedback_key
  };
  var err = fail('E_ENG_' + n05, n05 + ': aprēķins apturēts ar dimensiju vārtiem.');
  err.taxonomy_class = mapped.taxonomy_class;
  err.signature = mapped.signature;
  err.feedback_key = mapped.feedback_key;
  err.n05_error = n05;
  err.detail = detail || {};
  return err;
}

var NUMBER_RE = /^([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))$/;
var SCI_RE = /^([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+))\s*(?:[×x*]\s*10\s*(?:\^\s*([+-]?\d+)|([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+)))$/;
var E_RE = /^([+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+))$/;
function sigFigs(mantissa) {
  var s = String(mantissa).replace(/^[+-]/, '');
  if (s.indexOf('.') >= 0) {
    var d = s.replace('.', '').replace(/^0+/, '');
    return d.length ? d.length : 1;
  }
  var x = s.replace(/^0+/, '').replace(/0+$/, '');
  return x.length ? x.length : 1;
}
function parseNumeric(raw) {
  if (raw === null || raw === undefined) return { error: 'BLANK_RESPONSE' };
  if (typeof raw === 'boolean') return { error: 'UNREADABLE_INPUT' };
  var text = typeof raw === 'number' ? String(raw) : (typeof raw === 'string' ? raw.trim() : '');
  if (!text) return { error: 'BLANK_RESPONSE' };
  var low = text.toLowerCase();
  ['nan', 'inf', 'eval', 'function', ';', '='].forEach(function (t) {
    if (low.indexOf(t) >= 0) text = '!';
  });
  if (text === '!') return { error: 'UNREADABLE_INPUT' };
  if (text.indexOf(',') >= 0 && text.indexOf('.') >= 0) return { error: 'UNREADABLE_INPUT' };
  var normalized = text.replace(/[−]/g, '-').replace(/\u00a0/g, '').replace(/ /g, '');
  var m = SCI_RE.exec(normalized);
  if (m) {
    var mant = m[1].replace(',', '.'), exp = m[2] !== undefined ? parseInt(m[2], 10) : translateExp(m[3] || '0');
    var val = Number(mant) * Math.pow(10, exp);
    if (!isFinite(val)) return { error: 'UNREADABLE_INPUT' };
    return { value: val, sig_figs: sigFigs(mant) };
  }
  m = E_RE.exec(normalized) || NUMBER_RE.exec(normalized);
  if (m) {
    var canon = m[1].replace(',', '.');
    var value = Number(canon);
    if (!isFinite(value)) return { error: 'UNREADABLE_INPUT' };
    var mantissa = canon.split(/[eE]/)[0];
    return { value: value, sig_figs: sigFigs(mantissa) };
  }
  return { error: 'UNREADABLE_INPUT' };
}

function fraction(num, den) { return { num: Number(num), den: Number(den) }; }
function fractionValue(f) { return f.num / f.den; }
function resolveUnitTransform(fromUnit, toUnit) {
  load();
  var src = normUnit(fromUnit), dst = normUnit(toUnit);
  if (src === dst) return { status: 'ok', factor: fraction(1, 1), offset: fraction(0, 1) };
  var conversions = state.conventions.unit_system.conversions, chains = state.conventions.unit_system.chains, i;
  for (i = 0; i < conversions.length; i += 1) {
    var c = conversions[i];
    if (c.conversion_class !== 'blocked') continue;
    var a = normUnit(c.from), b = normUnit(c.to);
    if ((src === a && dst === b) || (src === b && dst === a)) {
      return { status: 'blocked', factor: fraction(0, 1), offset: fraction(0, 1) };
    }
  }
  for (i = 0; i < conversions.length; i += 1) {
    var d = conversions[i];
    if (d.conversion_class === 'blocked') continue;
    var x = normUnit(d.from), y = normUnit(d.to);
    if (d.conversion_class === 'offset') {
      var off = fraction(d.offset.num, d.offset.den);
      if (src === x && dst === y) return { status: 'ok', factor: fraction(1, 1), offset: off };
      if (src === y && dst === x) return { status: 'ok', factor: fraction(1, 1), offset: fraction(-off.num, off.den) };
    } else {
      var f = fraction(d.factor.num, d.factor.den);
      if (src === x && dst === y) return { status: 'ok', factor: f, offset: fraction(0, 1) };
      if (src === y && dst === x) return { status: 'ok', factor: fraction(f.den, f.num), offset: fraction(0, 1) };
    }
  }
  for (i = 0; i < chains.length; i += 1) {
    var ch = chains[i];
    if (ch.kind === 'symbolic' || !ch.factor) continue;
    var p = normUnit(ch.from), q = normUnit(ch.to);
    var cf = fraction(ch.factor.num, ch.factor.den);
    var co = ch.offset || { num: 0, den: 1 };
    if (src === p && dst === q) return { status: 'ok', factor: cf, offset: fraction(co.num, co.den) };
    if (src === q && dst === p && co.num === 0) return { status: 'ok', factor: fraction(cf.den, cf.num), offset: fraction(0, 1) };
  }
  var adj = Object.create(null);
  conversions.forEach(function (e) {
    if (e.conversion_class !== 'multiplicative') return;
    var u = normUnit(e.from), v = normUnit(e.to), f = fraction(e.factor.num, e.factor.den);
    if (!adj[u]) adj[u] = []; if (!adj[v]) adj[v] = [];
    adj[u].push({ to: v, factor: f });
    adj[v].push({ to: u, factor: fraction(f.den, f.num) });
  });
  var queue = [{ unit: src, factor: fraction(1, 1) }], visited = Object.create(null);
  visited[src] = true;
  while (queue.length) {
    var cur = queue.shift();
    (adj[cur.unit] || []).forEach(function (edge) {
      var acc = fraction(cur.factor.num * edge.factor.num, cur.factor.den * edge.factor.den);
      if (edge.to === dst) { queue.length = 0; queue.push({ unit: dst, factor: acc, done: true }); }
      else if (!visited[edge.to]) { visited[edge.to] = true; queue.push({ unit: edge.to, factor: acc }); }
    });
    if (queue.length && queue[0].done) return { status: 'ok', factor: queue[0].factor, offset: fraction(0, 1) };
  }
  return { status: 'incompatible', factor: fraction(0, 1), offset: fraction(0, 1) };
}

function quantity(raw, unit, sigFigsOverride) {
  var parsed = parseNumeric(raw);
  if (parsed.error) throw classifyError(parsed.error, { raw: raw, unit: unit });
  return { value: parsed.value, unit: normUnit(unit), dimension: parseUnit(unit),
    sig_figs: sigFigsOverride !== undefined && sigFigsOverride !== null ? sigFigsOverride : parsed.sig_figs,
    ledger: [] };
}
function record(q, operation, inputs, output) {
  q.ledger.push({ operation: operation, inputs: inputs, outputs: [output] });
  return q;
}
function convert(q, toUnit) {
  var transform = resolveUnitTransform(q.unit, toUnit);
  if (transform.status !== 'ok') throw classifyError('DIMENSIONAL_INCONSISTENCY',
    { from: q.unit, to: toUnit, status: transform.status });
  var outDim = parseUnit(toUnit);
  if (!dimEqual(q.dimension, outDim)) throw classifyError('DIMENSIONAL_INCONSISTENCY',
    { from: q.unit, to: toUnit, dimensions: [dimKey(q.dimension), dimKey(outDim)] });
  var value = round12(q.value * fractionValue(transform.factor) + fractionValue(transform.offset));
  return record({ value: value, unit: normUnit(toUnit), dimension: outDim, sig_figs: q.sig_figs,
    ledger: q.ledger.slice() }, 'convert',
    [q.value + ' ' + q.unit], value + ' ' + toUnit);
}
function add(a, b) {
  if (!dimEqual(a.dimension, b.dimension)) throw classifyError('DIMENSIONAL_INCONSISTENCY', {
    left: dimKey(a.dimension), right: dimKey(b.dimension), operation: 'add' });
  if (a.unit !== b.unit) b = convert(b, a.unit);
  return record({ value: round12(a.value + b.value), unit: a.unit, dimension: a.dimension,
    sig_figs: Math.min(a.sig_figs || 99, b.sig_figs || 99), ledger: a.ledger.slice() },
    'add', [a.value + ' ' + a.unit, b.value + ' ' + b.unit], (a.value + b.value) + ' ' + a.unit);
}
function multiply(a, b) {
  var dim = Object.assign({}, a.dimension);
  Object.keys(b.dimension).forEach(function (k) { dim[k] = (dim[k] || 0) + b.dimension[k]; });
  return record({ value: round12(a.value * b.value), unit: a.unit + '·' + b.unit, dimension: dim,
    sig_figs: Math.min(a.sig_figs || 99, b.sig_figs || 99), ledger: a.ledger.slice() },
    'multiply', [a.value + ' ' + a.unit, b.value + ' ' + b.unit], (a.value * b.value) + ' combined');
}
function divide(a, b) {
  if (b.value === 0) throw classifyError('PHYSICALLY_IMPLAUSIBLE', { operation: 'divide', divisor: '0' });
  var dim = Object.assign({}, a.dimension);
  Object.keys(b.dimension).forEach(function (k) { dim[k] = (dim[k] || 0) - b.dimension[k]; });
  return record({ value: round12(a.value / b.value), unit: a.unit + '/' + b.unit, dimension: dim,
    sig_figs: Math.min(a.sig_figs || 99, b.sig_figs || 99), ledger: a.ledger.slice() },
    'divide', [a.value + ' ' + a.unit, b.value + ' ' + b.unit], (a.value / b.value) + ' combined');
}
function dimensionGate(quantities, expectedUnit) {
  var keys = quantities.map(function (q) { return JSON.stringify(dimKey(q.dimension)); });
  if (expectedUnit) {
    var want = JSON.stringify(dimKey(parseUnit(expectedUnit)));
    if (keys.some(function (k) { return k !== want; })) throw classifyError('DIMENSIONAL_INCONSISTENCY',
      { expected: want, actual: keys, operation: 'gate' });
  }
  if (keys.filter(function (k, i) { return keys.indexOf(k) === i; }).length > 1) {
    throw classifyError('DIMENSIONAL_INCONSISTENCY', { actual: keys, operation: 'gate' });
  }
  return { operation: 'dimension_gate', dimensions: keys, status: 'CLOSED' };
}

function expectedDecimal(payload, givens) {
  if (givens.unrounded_expected !== undefined && givens.round_mode !== undefined) {
    var raw = Number(givens.unrounded_expected), digits = Number(givens.round_digits);
    if (givens.round_mode === 'decimal_places') return round12(Number(raw.toFixed(digits)));
    if (raw === 0) return 0;
    var decs = digits - 1 - Math.floor(Math.log10(Math.abs(raw)));
    return round12(Number(raw.toFixed(Math.max(0, decs))));
  }
  return Number(payload.expected_value);
}
function toleranceFor(toleranceClass) {
  var list = state.conventions.tolerances.quantity_classes, i;
  for (i = 0; i < list.length; i += 1) if (list[i].id === toleranceClass) return Number(list[i].absolute.value);
  throw classifyError('UNREADABLE_INPUT', { tolerance_class: toleranceClass });
}
function gradeNumeric(payload, givens, submission, expected, expectedSigFigs) {
  var parsed = parseNumeric(submission.value);
  if (parsed.error) return { ok: false, error_class: parsed.error, sig_figs_ok: false };
  var submittedUnit = submission.unit !== undefined ? submission.unit : payload.unit;
  if (givens.requires_explicit_basis && normUnit(submittedUnit) === '%' &&
      state.conventions.percentage_basis.unlabeled_percent === 'withhold scoring') {
    return { ok: false, error_class: 'UNLABELED_PERCENT_BASIS', sig_figs_ok: false };
  }
  var tr = resolveUnitTransform(submittedUnit, payload.unit);
  if (tr.status !== 'ok') return { ok: false, error_class: 'DIMENSIONAL_INCONSISTENCY', sig_figs_ok: false };
  var converted = round12(parsed.value * fractionValue(tr.factor) + fractionValue(tr.offset));
  var tol = toleranceFor(payload.tolerance_class);
  var diff = round12(Math.abs(converted - expected));
  var sfOk = expectedSigFigs === undefined || expectedSigFigs === null ? true : parsed.sig_figs === expectedSigFigs;
  var result = { converted_value: String(converted), abs_diff: String(diff), tolerance_used: String(tol),
    sig_figs_ok: sfOk, tolerance_source: 'tolerances.quantity_classes[id=' + payload.tolerance_class + ']' };
  if (diff <= tol) { result.ok = true; result.error_class = 'NONE'; return result; }
  if (givens.density_g_per_ml !== undefined && givens.density_defect_op !== undefined) {
    var rho = Number(givens.density_g_per_ml);
    var defect = givens.density_defect_op === 'divide' ? expected / rho : expected * rho;
    if (round12(Math.abs(converted - defect)) <= tol) {
      result.ok = false; result.error_class = 'DIMENSIONAL_INCONSISTENCY'; return result;
    }
  }
  result.ok = false; result.error_class = 'OUT_OF_TOLERANCE'; return result;
}
function checkOrder(submitted, correct, rules) {
  if (!submitted || submitted.length !== correct.length) return false;
  var a = submitted.slice().sort().join('|'), b = correct.slice().sort().join('|');
  if (a !== b) return false;
  var free = [];
  (rules || []).forEach(function (r) { if (r.type === 'free_order_group') free.push(r.item_ids || []); });
  for (var i = 0; i < submitted.length; i += 1) {
    if (submitted[i] === correct[i]) continue;
    var ok = free.some(function (g) { return g.indexOf(submitted[i]) >= 0 && g.indexOf(correct[i]) >= 0; });
    if (!ok) return false;
  }
  return true;
}
function criterion(id, points, status) {
  return { criterion_id: id, status: status,
    awarded_points: status === 'awarded' ? Number(points) : 0.0,
    pending_points: status === 'pending' ? Number(points) : 0.0, max_points: Number(points) };
}
function canonicalVerdict(instance, submission, res, criteria, machine, maximum, pendingPoints, primary, autoMax) {
  var verdict;
  if (autoMax === 0) verdict = primary === 'BLANK_RESPONSE' ? 'incorrect' : 'pending_self_assessment';
  else if (machine === autoMax) verdict = pendingPoints > 0 ? 'auto_passed_pending_review' : 'correct';
  else if (machine > 0) verdict = 'partial';
  else verdict = 'incorrect';
  void res; void criteria; void submission; void instance; void maximum;
  return { verdict_class: verdict, error_class: primary, awarded_criteria: criteria,
    machine_checked_points: machine, self_assessed_points: 0.0, human_reviewed_points: 0.0,
    pending_points: pendingPoints, max_points: maximum };
}
function grade(instance, submission, options) {
  load();
  var pc = instance.payload_class, payload = instance.payload, givens = instance.givens || {}, i;
  var rubric = instance.rubric;
  var auto = rubric.filter(function (r) {
    return (r.grading === 'auto' || r.grading === 'mixed') &&
      r.engine_binding !== 'self-assessed' && r.engine_binding !== 'human-review';
  });
  var pending = rubric.filter(function (r) { return auto.indexOf(r) < 0; });
  var criteria = [], machine = 0, maximum = 0, pendingPoints = 0, primary = 'NONE', res = null;
  pending.forEach(function (item) {
    var p = Number(item.points); maximum += p; pendingPoints += p;
    criteria.push(criterion(item.criterion_id, p, 'pending'));
  });
  if (pc === 'numeric' || pc === 'graph') {
    var used = payload, sub = submission;
    if (pc === 'graph') {
      var target = payload.target_readout;
      var xs = payload.points.map(function (p) { return Number(p.x); });
      var xmin = Math.min.apply(null, xs), xmax = Math.max.apply(null, xs);
      var bad = false;
      if (submission.x !== undefined && submission.x !== null) {
        var px = parseNumeric(submission.x);
        if (px.error) { primary = px.error; bad = true; }
        else if (px.value < xmin || px.value > xmax) { primary = 'OUT_OF_DOMAIN_EXTRAPOLATION'; bad = true; }
      }
      if (bad) res = { ok: false, error_class: primary };
      else res = gradeNumeric(target, givens, { value: submission.value, unit: submission.unit !== undefined ? submission.unit : target.unit },
        Number(target.expected_value), null);
      used = target;
    } else {
      res = gradeNumeric(used, givens, submission, expectedDecimal(used, givens), used.sig_figs);
    }
    if (!res.ok) primary = res.error_class;
    auto.forEach(function (item) {
      var p = Number(item.points); maximum += p;
      var passed = item.criterion_id.slice(-7) === '_SIGFIG' ? Boolean(res.ok && res.sig_figs_ok) : Boolean(res.ok);
      if (passed) machine += p;
      criteria.push(criterion(item.criterion_id, p, passed ? 'awarded' : 'denied'));
    });
    if (res.ok && criteria.some(function (c) { return c.status === 'denied'; })) primary = 'SIG_FIG_MISMATCH';
    void used;
  } else if (pc === 'option_select') {
    var sel = submission.selected_ids;
    var matched = Boolean(sel && sel.length) && sel.length === payload.correct_ids.length &&
      payload.correct_ids.every(function (id) { return sel.indexOf(id) >= 0; });
    if (!sel || !sel.length) primary = 'BLANK_RESPONSE'; else if (!matched) primary = 'WRONG_OPTION_SELECTION';
    auto.forEach(function (item) { var p = Number(item.points); maximum += p; if (matched) machine += p;
      criteria.push(criterion(item.criterion_id, p, matched ? 'awarded' : 'denied')); });
  } else if (pc === 'ordering') {
    var order = submission.order;
    var ok = Boolean(order && order.length) && checkOrder(order, payload.correct_order, payload.partial_order_rules);
    if (!order || !order.length) primary = 'BLANK_RESPONSE'; else if (!ok) primary = 'WRONG_ORDER';
    auto.forEach(function (item) { var p = Number(item.points); maximum += p; if (ok) machine += p;
      criteria.push(criterion(item.criterion_id, p, ok ? 'awarded' : 'denied')); });
  } else if (pc === 'matching') {
    var pairs = submission.pairs || [], map = Object.create(null), dup = false;
    pairs.forEach(function (pair) { if (map[pair.left_id] !== undefined) dup = true; map[pair.left_id] = pair.right_id; });
    var expectedMap = Object.create(null);
    payload.correct_pairs.forEach(function (p) { expectedMap[p.left_id] = p.right_id; });
    var all = !dup && Object.keys(expectedMap).every(function (k) { return map[k] === expectedMap[k]; }) &&
      Object.keys(map).length === Object.keys(expectedMap).length;
    if (!pairs.length) primary = 'BLANK_RESPONSE'; else if (!all) primary = 'WRONG_PAIRING';
    auto.forEach(function (item) {
      var p = Number(item.points); maximum += p;
      var passed;
      if (item.criterion_id.indexOf('_PAIR_') >= 0) {
        var left = item.criterion_id.split('_PAIR_')[1];
        passed = !dup && map[left] === expectedMap[left];
      } else passed = all;
      if (passed) machine += p;
      criteria.push(criterion(item.criterion_id, p, passed ? 'awarded' : 'denied'));
    });
  } else if (pc === 'method') {
    var text = submission.text;
    if (pending.length && !auto.length && typeof text === 'string' && !text.trim()) {
      primary = 'BLANK_RESPONSE'; pendingPoints = 0;
      criteria.forEach(function (c) { c.status = 'denied'; c.pending_points = 0; });
    }
    auto.forEach(function (item) { var p = Number(item.points); maximum += p;
      criteria.push(criterion(item.criterion_id, p, 'denied')); });
  } else throw classifyError('UNREADABLE_INPUT', { payload_class: pc });
  criteria.sort(function (a, b) { return a.criterion_id < b.criterion_id ? -1 : 1; });
  var autoMax = auto.reduce(function (sum, item) { return sum + Number(item.points); }, 0);
  var out = canonicalVerdict(instance, submission, res, criteria, round12(machine),
    round12(maximum), round12(pendingPoints), primary, round12(autoMax));
  options = options || {};
  out.oracle_version = options.oracle_version || '1.0.0';
  out.oracle_digest = options.oracle_digest || '';
  out.conventions_digest = options.conventions_digest || '';
  var mapped = n05Map()[primary] || { taxonomy_class: 'NONE', signature: '', feedback_key: '' };
  out.taxonomy_class = mapped.taxonomy_class;
  out.signature = mapped.signature;
  out.feedback_key = mapped.feedback_key;
  out.feedback_text = feedback(mapped.taxonomy_class);
  out.tolerance_source = res && res.tolerance_source ? res.tolerance_source :
    'tolerances.quantity_classes[id=' + (payload.tolerance_class || 'mass') + ']';
  return out;
}

function checkConservation(record) {
  load();
  var rules = state.taxonomy.conservation.rules;
  var massRule = rules.filter(function (r) { return r.id === 'mass_in_equals_mass_out'; })[0];
  var moleRule = rules.filter(function (r) { return r.id === 'moles_by_stoichiometry'; })[0];
  var tol = toleranceFor('mass');
  var totalIn = record.species_in.reduce(function (a, s) { return a + Number(s.mass_g); }, 0);
  var totalOut = record.species_out.reduce(function (a, s) { return a + Number(s.mass_g); }, 0);
  var delta = round12(totalIn - totalOut);
  var extents = record.species_in.concat(record.species_out).filter(function (s) {
    return s.nu !== null && s.nu !== undefined;
  }).map(function (s) {
    return Number(s.moles || 0) / Number(s.nu || 1);
  });
  var moleDelta = round12(Math.max.apply(null, extents) - Math.min.apply(null, extents));
  var relTol = Number(moleRule.relative_tolerance);
  var molesOk = moleDelta <= relTol * Math.max(1, Math.max.apply(null, extents));
  var balanced = Math.abs(delta) <= tol && molesOk;
  return { verdict: balanced ? 'BALANCED' : 'IMBALANCED',
    signature: balanced ? '' : state.taxonomy.conservation.imbalance_signature,
    mass_in: String(totalIn), mass_out: String(totalOut), delta: String(delta),
    mole_delta: String(moleDelta), tolerance: String(tol),
    tolerance_source: massRule.tolerance_source, relative_tolerance: String(relTol),
    balanced: balanced, moles_ok: molesOk };
}

function classResult(n05, trace, detail) {
  var mapped = n05Map()[n05] || { taxonomy_class: fallback().code || 'UNREADABLE_INPUT',
    signature: fallback().signature, feedback_key: fallback().feedback_key };
  var sources = [];
  [detail.rule_id, detail.rule].forEach(function (rid) {
    var plaus = state.taxonomy.plausibility_rules.filter(function (r) { return r.id === rid; })[0];
    var domain = state.taxonomy.domain_rules.filter(function (r) { return r.id === rid; })[0];
    if (plaus) sources.push(plaus.source);
    if (domain) sources.push(domain.source_contract);
  });
  return { taxonomy_class: mapped.taxonomy_class, signature: mapped.signature,
    feedback_key: mapped.feedback_key, feedback_text: feedback(mapped.taxonomy_class),
    n05_error_class: n05, precedence_trace: trace, rule_sources: sources, detail: detail };
}
function classify(caseData) {
  load();
  var trace = [], parsed = parseNumeric(caseData.raw);
  if (parsed.error) { trace.push(parsed.error); return classResult(parsed.error, trace, { raw: caseData.raw, reason: 'unreadable literal' }); }
  trace.push('literal parsed');
  var srcDim, dstDim;
  try {
    srcDim = parseUnit(caseData.unit);
    dstDim = caseData.expected_unit ? parseUnit(caseData.expected_unit) : srcDim;
  } catch (error) {
    trace.push('unit grammar failed');
    return classResult('UNREADABLE_INPUT', trace, { unit: caseData.unit, reason: 'unit grammar' });
  }
  trace.push('unit grammar parsed');
  if (!dimEqual(srcDim, dstDim)) {
    trace.push('dimension mismatch');
    return classResult('DIMENSIONAL_INCONSISTENCY', trace,
      { unit: caseData.unit, expected_unit: caseData.expected_unit, dimensions: [dimKey(srcDim), dimKey(dstDim)] });
  }
  var tr = resolveUnitTransform(caseData.unit, caseData.expected_unit);
  if (tr.status !== 'ok') {
    trace.push('transform ' + tr.status);
    return classResult('DIMENSIONAL_INCONSISTENCY', trace,
      { unit: caseData.unit, expected_unit: caseData.expected_unit, status: tr.status });
  }
  var converted = round12(parsed.value * fractionValue(tr.factor) + fractionValue(tr.offset));
  trace.push('unit transform closed');
  var rule = state.taxonomy.plausibility_rules.filter(function (r) { return r.id === caseData.rule_id; })[0];
  if (rule) {
    var lower = rule.min, upper = rule.max, inclusive = rule.inclusive !== false;
    var below = lower !== undefined && (inclusive ? converted < Number(lower) : converted <= Number(lower));
    var above = upper !== undefined && (inclusive ? converted > Number(upper) : converted >= Number(upper));
    if (below || above) {
      trace.push('plausibility ' + rule.id);
      return classResult(rule.id === 'percent_basis_required' ? 'UNLABELED_PERCENT_BASIS' : 'OUT_OF_TOLERANCE', trace,
        { rule_id: rule.id, value: String(converted), source: rule.source, conventions_ref: rule.conventions_ref });
    }
  }
  if (caseData.span) {
    var x = Number(caseData.x !== undefined ? caseData.x : converted);
    if (x < Number(caseData.span.min) || x > Number(caseData.span.max)) {
      trace.push('outside declared span');
      return classResult('OUT_OF_DOMAIN_EXTRAPOLATION', trace, { x: String(x), span: caseData.span,
        rule: caseData.domain_rule || 'calibration_span' });
    }
  }
  trace.push('in domain');
  return { taxonomy_class: 'NONE', signature: 'NONE', feedback_key: '', feedback_text: '',
    n05_error_class: 'NONE', precedence_trace: trace, rule_sources: [], value: String(converted) };
}

function feedback(classId) {
  load();
  var list = classes(), key = '', i;
  for (i = 0; i < list.length; i += 1) if (list[i].id === classId) key = list[i].feedback_key;
  if (!key && classId !== 'NONE') key = fallback().feedback_key;
  if (!key) return '';
  var entries = state.terms.terms, entry = null;
  for (i = 0; i < entries.length; i += 1) if (entries[i].key === key) { entry = entries[i]; break; }
  if (!entry) throw classifyError('UNREADABLE_INPUT', { feedback_key: key, term_island: TERMS_ID });
  return entry.text_lv;
}

function declaredConstants() { load(); return Object.create(null); }
function consumptionPaths() { load(); return state.taxonomy.conventions_consumption.paths.slice(); }
function precedenceRule() { load(); return state.taxonomy.error_taxonomy.precedence_rule_verbatim; }
function sha256(text) {
  if (root.SimFigures && typeof root.SimFigures.sha256Utf8 === 'function') return root.SimFigures.sha256Utf8(text);
  throw fail('E_ENG_SHA', 'SHA-256 helper unavailable (load SimFigures first).');
}
function renderError(doc, error) {
  var node = doc && doc.getElementById ? doc.getElementById('sim-engines-error') : null;
  if (node) { node.textContent = 'Aprēķinu dzinēja kļūda (' + (error.code || 'E_ENG') + '): ' + (error.message || error); node.hidden = false; }
}
function init(doc) {
  try { load(doc); return state.conventions; }
  catch (error) { renderError(doc, error); return null; }
}
root.SimEngines = {
  ISLAND_ID: TAXONOMY_ID, load: load, init: init, parseUnit: parseUnit, parseNumeric: parseNumeric,
  quantity: quantity, convert: convert, add: add, multiply: multiply, divide: divide,
  dimensionGate: dimensionGate, grade: grade, gradeNumeric: gradeNumeric,
  checkConservation: checkConservation, classify: classify, feedback: feedback,
  declaredConstants: declaredConstants, consumptionPaths: consumptionPaths,
  precedenceRule: precedenceRule, classes: classes, sha256: sha256,
  renderError: renderError, resolveUnitTransform: resolveUnitTransform
};
if (typeof module !== 'undefined' && module.exports) module.exports = root.SimEngines;
})(typeof globalThis !== 'undefined' ? globalThis : this);
