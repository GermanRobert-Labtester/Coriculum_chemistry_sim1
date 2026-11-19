/* N10 terminology island & unit-grammar runtime loader (#sim-terms). */
(function (root) {
  'use strict';
  var ID = 'sim-terms', SUP = { '\u00b9': 1, '\u00b2': 2, '\u00b3': 3, '\u207b\u00b9': -1, '\u207b\u00b2': -2, '\u207b\u00b3': -3 };
  var SUPK = ['\u207b\u00b3', '\u207b\u00b2', '\u207b\u00b9', '\u00b3', '\u00b2', '\u00b9'];
  var SKIP = { 'C/C₀': 1, 'c/c₀': 1, 'C₀/C₀': 1, 'm/m': 1, 'm/V': 1, 'V/V': 1, pH: 1, '\u03b5': 1, 'H\u2083O\u207a': 1, 'HCl(aq)': 1, 'NH\u2083(aq)': 1, N06: 1, N07: 1, N08: 1, N10: 1, N25: 1, N30: 1, N34: 1, PROPOSED: 1, 'k\u0101pnes': 1, 'Erlenmeijera kolba': 1, 're\u0123istr\u0113ts iztr\u016bkums': 1, 'informat\u012bva atz\u012bme, bez soda punktiem': 1, 'nav autom\u0101tiski p\u0101rbaud\u012bts': 1, 'kursa z\u012bmju konvencija': 1, 'dim\u0113rs N\u2082O\u2084': 1 };
  var def = null;
  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
  function TermsError(c, m, d) {
    this.name = 'TermsError'; this.code = c; this.message = '[' + c + '] ' + m; this.details = d || {};
    if (Error.captureStackTrace) Error.captureStackTrace(this, TermsError); else this.stack = (new Error(this.message)).stack;
  }
  TermsError.prototype = Object.create(Error.prototype); TermsError.prototype.constructor = TermsError;
  function fail(c, m, d) { throw new TermsError(c, m, d); }
  function req(ok, c, m, d) { if (!ok) fail(c, m, d); }
  function bal(s) { var d = 0, i; for (i = 0; i < s.length; i++) { if (s[i] === '(') d++; else if (s[i] === ')' && --d < 0) return false; } return d === 0; }
  function getG(isl) { var s = isl || def; req(s && s.unit_grammar, 'E_TERMS_NOT_LOADED', '#sim-terms nav ielādēta.', { island: ID }); return s.unit_grammar; }
  function elMap(g) {
    if (g._elMap) return g._elMap;
    var m = Object.create(null), els = g.elements || [], i;
    for (i = 0; i < els.length; i++) if (els[i] && els[i].symbol) m[els[i].symbol] = els[i];
    return m;
  }
  function pTok(tok, els, raw) {
    req(tok && !/\s|[*;,]/.test(tok), 'E_UNIT_MALFORMED_SEPARATOR', tok + ' (' + raw + ')', { unit: raw });
    if (has(els, tok)) return { element: tok, exponent: 1 };
    if (tok.indexOf('^') !== -1) {
      var p = tok.split('^');
      req(p.length === 2 && p[0] && /^[-+]?[1-9][0-9]*$/.test(p[1]), 'E_UNIT_BAD_EXPONENT', tok, { unit: raw });
      req(has(els, p[0]), 'E_UNIT_UNKNOWN_ELEMENT', p[0], { unit: raw, element: p[0] });
      return { element: p[0], exponent: parseInt(p[1], 10) };
    }
    for (var k = 0; k < SUPK.length; k++) {
      var s = SUPK[k];
      if (tok.length > s.length && tok.slice(tok.length - s.length) === s) {
        var b = tok.slice(0, tok.length - s.length);
        req(has(els, b), 'E_UNIT_UNKNOWN_ELEMENT', b, { unit: raw, element: b });
        return { element: b, exponent: SUP[s] };
      }
    }
    fail('E_UNIT_UNKNOWN_ELEMENT', tok, { unit: raw, element: tok });
  }
  function splitP(expr, els, raw) {
    req(expr && !/[*.]/.test(expr) && expr[0] !== '\u00b7' && expr[expr.length - 1] !== '\u00b7' && expr.indexOf('\u00b7\u00b7') === -1, 'E_UNIT_MALFORMED_SEPARATOR', raw, { unit: raw });
    return expr.split('\u00b7').map(function (t) { return pTok(t, els, raw); });
  }
  function accSide(side, sign, els, dv, used, um) {
    for (var j = 0; j < side.length; j++) {
      var t = side[j], e = t.exponent * sign, vec = els[t.element].dimension_vector || {}, ax;
      if (!um[t.element]) { um[t.element] = 1; used.push(t.element); }
      for (ax in vec) if (has(vec, ax)) dv[ax] = (dv[ax] || 0) + vec[ax] * e;
    }
  }
  function parseUnit(u, isl) {
    var g = getG(isl);
    req(typeof u === 'string' && u.trim(), 'E_UNIT_EMPTY', 'Tukša vienība.', { unit: u });
    req(u === u.trim(), 'E_UNIT_WHITESPACE', u, { unit: u });
    req(bal(u), 'E_UNIT_UNBALANCED_PARENS', u, { unit: u });
    if ((g.dimensionless_tokens || []).indexOf(u) !== -1) return { raw: u, kind: 'dimensionless', numerator: [], denominator: [], dimensionVector: {}, elements: [] };
    var els = elMap(g), pm = u.match(/^\((.+)\)(\^[-+]?[1-9][0-9]*|[\u00b9\u00b2\u00b3]|\u207b\u00b9|\u207b\u00b2|\u207b\u00b3)$/);
    if (pm && bal(pm[1])) {
      var inn = parseUnit(pm[1], { unit_grammar: g }), oe = pm[2][0] === '^' ? parseInt(pm[2].slice(1), 10) : SUP[pm[2]], sd = {}, k;
      for (k in inn.dimensionVector) if (has(inn.dimensionVector, k) && inn.dimensionVector[k] * oe) sd[k] = inn.dimensionVector[k] * oe;
      return { raw: u, kind: 'composed', numerator: inn.numerator.map(function (t) { return { element: t.element, exponent: t.exponent * oe }; }), denominator: inn.denominator.map(function (t) { return { element: t.element, exponent: t.exponent * oe }; }), dimensionVector: sd, elements: inn.elements.slice() };
    }
    var sl = [], d = 0, i;
    for (i = 0; i < u.length; i++) { if (u[i] === '(') d++; else if (u[i] === ')') d--; else if (u[i] === '/' && d === 0) sl.push(i); }
    req(sl.length <= 1, 'E_UNIT_MALFORMED_SEPARATOR', u, { unit: u });
    var num = [], den = [];
    if (sl.length === 1) {
      var ns = u.slice(0, sl[0]), ds = u.slice(sl[0] + 1);
      req(ns && ds && !/\s|[()]/.test(ns) && !/\s/.test(ds), 'E_UNIT_MALFORMED_SEPARATOR', u, { unit: u });
      num = splitP(ns, els, u);
      if (ds[0] === '(' && ds[ds.length - 1] === ')' && bal(ds.slice(1, -1))) {
        var ind = ds.slice(1, -1);
        req(!/[\/()]/.test(ind), 'E_UNIT_MALFORMED_SEPARATOR', u, { unit: u });
        den = splitP(ind, els, u);
      } else {
        req(!/[()]/.test(ds), 'E_UNIT_MALFORMED_SEPARATOR', u, { unit: u });
        req(!/[\u00b7*]/.test(ds), 'E_UNIT_AMBIGUOUS_DENOMINATOR', u, { unit: u });
        den = splitP(ds, els, u);
      }
    } else {
      req(!/[\s()]/.test(u), 'E_UNIT_MALFORMED_SEPARATOR', u, { unit: u });
      num = splitP(u, els, u);
    }
    var dv = {}, used = [], um = Object.create(null);
    accSide(num, 1, els, dv, used, um); accSide(den, -1, els, dv, used, um);
    var clean = {}, ak;
    for (ak in dv) if (has(dv, ak) && dv[ak] !== 0) clean[ak] = dv[ak];
    return { raw: u, kind: 'composed', numerator: num, denominator: den, dimensionVector: clean, elements: used };
  }
  function sameDim(a, b) {
    var ka = Object.keys(a || {}).filter(function (k) { return a[k] !== 0; }).sort();
    var kb = Object.keys(b || {}).filter(function (k) { return b[k] !== 0; }).sort();
    if (ka.length !== kb.length) return false;
    for (var i = 0; i < ka.length; i++) if (ka[i] !== kb[i] || a[ka[i]] !== b[kb[i]]) return false;
    return true;
  }
  function checkDimension(u, dim, isl) {
    var g = getG(isl), dims = g.dimensions || {};
    req(has(dims, dim), 'E_UNIT_UNKNOWN_DIMENSION', dim, { dimension: dim });
    var parsed = parseUnit(u, { unit_grammar: g });
    req(sameDim(parsed.dimensionVector, dims[dim]), 'E_UNIT_DIMENSION_MISMATCH', dim + ' != ' + u, { dimension: dim, unit: u });
    return parsed;
  }
  function load(doc) {
    doc = doc || root.document;
    var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(ID) : null;
    req(node, 'E_TERMS_MISSING', '#sim-terms nav atrasta.', { island: ID });
    var raw = node.textContent !== undefined ? node.textContent : node.innerText;
    req(typeof raw === 'string' && raw.trim(), 'E_TERMS_EMPTY', '#sim-terms ir tukša.', { island: ID });
    var data;
    try { data = JSON.parse(raw); } catch (e) { fail('E_TERMS_JSON', '#sim-terms nederīgs JSON.', { island: ID, cause: String(e.message || e) }); }
    req(data && typeof data === 'object' && !Array.isArray(data), 'E_TERMS_SHAPE', '#sim-terms nav objekts.', { island: ID });
    req(data.island_id === ID, 'E_TERMS_ID', '#sim-terms island_id neatbilst.', { island: ID, found: data.island_id });
    req(data.schema_version === 1 && data.status === 'authored', 'E_TERMS_SHAPE', '#sim-terms versija/statuss.', { island: ID });
    req(data.unit_grammar && Array.isArray(data.unit_grammar.elements) && data.unit_grammar.dimensions, 'E_TERMS_GRAMMAR', '#sim-terms gramatika.', { island: ID });
    req(Array.isArray(data.terms) && data.terms.length, 'E_TERMS_EMPTY', '#sim-terms tukšs.', { island: ID });
    var byKey = Object.create(null), byClass = Object.create(null), counts = { terms: 0, quantities: 0, instruments: 0, interface: 0, iupac: 0 };
    for (var i = 0; i < data.terms.length; i++) {
      var e = data.terms[i];
      req(e && typeof e.key === 'string' && e.key, 'E_TERMS_SHAPE', 'Trūkst atslēgas: ' + i, { island: ID });
      req(!has(byKey, e.key), 'E_TERMS_DUPLICATE_KEY', e.key, { island: ID, key: e.key });
      req(typeof e.text_lv === 'string' && e.text_lv.trim(), 'E_TERMS_EMPTY_TEXT', e.key, { island: ID, key: e.key });
      byKey[e.key] = e;
      if (!byClass[e.class]) byClass[e.class] = [];
      byClass[e.class].push(e);
      if (has(counts, e.class)) counts[e.class]++;
    }
    var g = Object.assign({}, data.unit_grammar); g._elMap = elMap(g);
    return { schema_version: 1, island_id: ID, status: data.status, language: data.language || 'lv', rules: data.rules || {}, unit_grammar: g, terms: data.terms.slice(), byKey: byKey, byClass: byClass, countsByClass: counts, total: data.terms.length };
  }
  function setDefault(isl) { def = isl || null; return def; }
  function getDefault() { return def; }
  function getEntry(key, isl) {
    var s = isl || def;
    req(s && s.byKey, 'E_TERMS_NOT_LOADED', '#sim-terms nav ielādēta.', { island: ID, key: key });
    req(typeof key === 'string' && has(s.byKey, key), 'E_TERMS_MISSING_KEY', 'Trūkst "' + String(key) + '" (#sim-terms).', { island: ID, key: key });
    return s.byKey[key];
  }
  function lookup(key, opt, isl) {
    opt = opt || {};
    var e = getEntry(key, isl), mode = opt.mode || 'primary';
    if (mode === 'record') return Object.assign({}, e);
    if (mode === 'iupac') { req(e.iupac_name, 'E_TERMS_NO_IUPAC_PAIR', key, { island: ID, key: key }); return (e.primary_lv || e.text_lv) + ' (IUPAC: ' + e.iupac_name + ')'; }
    return e.primary_lv || e.text_lv;
  }
  function extractNestedUnits(txt, entry, isl) {
    var out = [];
    if (typeof txt !== 'string' || txt.indexOf('(') === -1) return out;
    var els = elMap(getG(isl)), re = /\(([^()]+)\)/g, m;
    while ((m = re.exec(txt)) !== null) {
      var inn = m[1].trim();
      if (!inn || SKIP[inn] || inn.indexOf('IUPAC:') === 0 || inn.indexOf('N25') === 0 || inn.indexOf('N34') === 0) continue;
      var hasOp = /[/\u00b7^*]/.test(inn) && inn.indexOf(' ') === -1;
      var qU = entry && entry.class === 'quantities' && (has(els, inn) || /^[A-Za-z\u00b5\u00b0][A-Za-z0-9\u00b3\u00b2\u00b9\u207b^*/\u00b7-]*$/.test(inn));
      if (hasOp || qU) out.push(inn);
    }
    return out;
  }
  function resolveFigureLabel(spec, isl) {
    req(spec && typeof spec === 'object', 'E_FIG_LABEL_SPEC', 'Spec nav objekts.', {});
    req(spec.kind === 'axis' || spec.kind === 'legend' || spec.kind === 'annotation', 'E_FIG_LABEL_KIND', String(spec.kind), { kind: spec.kind });
    var e = getEntry(spec.key, isl), lbl = lookup(spec.key, { mode: spec.iupac ? 'iupac' : 'primary' }, isl);
    var u = spec.unit !== undefined ? spec.unit : e.unit, dim = spec.dimension !== undefined ? spec.dimension : e.dimension, pu = null;
    if (u !== null && u !== undefined && u !== '') pu = dim ? checkDimension(u, dim, isl) : parseUnit(u, isl);
    else req(u !== '', 'E_UNIT_EMPTY', spec.key, { key: spec.key });
    var nest = extractNestedUnits(lbl, e, isl);
    for (var i = 0; i < nest.length; i++) if (dim) checkDimension(nest[i], dim, isl); else parseUnit(nest[i], isl);
    var txt = (u && lbl.indexOf('(' + u + ')') === -1) ? (lbl + ' (' + u + ')') : lbl;
    return { kind: spec.kind, key: spec.key, label: lbl, unit: u || null, parsedUnit: pu, text: txt };
  }
  function walk(n, fn) { if (!n) return; fn(n); var c = n.childNodes || []; for (var i = 0; i < c.length; i++) walk(c[i], fn); }
  function ga(n, a) { return typeof n.getAttribute === 'function' ? n.getAttribute(a) : (n.attributes && n.attributes[a]); }
  function applyToDocument(doc, isl) {
    doc = doc || root.document; var s = isl || def; if (!doc || !s) return 0; var u = 0;
    walk(doc.body || doc.documentElement || doc, function (n) {
      var k = ga(n, 'data-term-key');
      if (k) { n.textContent = lookup(k, { mode: ga(n, 'data-term-mode') || 'primary' }, s); u++; }
    });
    return u;
  }
  function renderStatus(doc, isl) {
    doc = doc || root.document; var n = doc && doc.getElementById ? doc.getElementById('sim-terms-status') : null; if (!n || !isl) return;
    var c = isl.countsByClass;
    n.textContent = 'Terminoloģijas sala (#sim-terms): ' + isl.total + ' šķirkļi (' + c.terms + '/' + c.quantities + '/' + c.instruments + '/' + c.interface + '/' + c.iupac + ').';
    n.hidden = false;
  }
  function renderError(doc, err) {
    doc = doc || root.document; var b = doc && doc.getElementById ? doc.getElementById('sim-terms-error') : null; if (!b) return;
    b.textContent = 'Terminoloģijas salas kļūda (' + (err && err.code ? err.code : 'E_TERMS_ERROR') + '): ' + (err && err.message ? err.message : String(err));
    b.hidden = false;
  }
  root.SimTerms = { ISLAND_ID: ID, TermsError: TermsError, load: load, setDefault: setDefault, getDefault: getDefault, getEntry: getEntry, lookup: lookup, parseUnit: parseUnit, checkDimension: checkDimension, extractNestedUnits: extractNestedUnits, resolveFigureLabel: resolveFigureLabel, applyToDocument: applyToDocument, renderStatus: renderStatus, renderError: renderError };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.SimTerms;
})(typeof globalThis !== 'undefined' ? globalThis : this);
