/* N12 runtime-side figure leak-scan checker (authoring/build/self-check over figure data & SVG only; never scans learner input). */
(function (root) {
  'use strict';

  var RULES = {
    significance: 'N12-LEAK-SIG-01',
    borderline: 'N12-LEAK-BORDER-01',
    exemption: 'N12-LEAK-EXEMPT-01'
  };
  var ALLOWED_EXEMPT = {
    EXEMPT_READING_DISPLAY: 1,
    EXEMPT_WORKED_DERIVATION: 1,
    EXEMPT_GIVEN_INPUT: 1
  };
  var COMMON_BARE = {
    '0': 1, '1': 1, '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1,
    '10': 1, '100': 1, '1000': 1, '0.1': 1, '0.01': 1, '0.001': 1, '273.15': 1, '298.15': 1
  };
  var SCALE = {
    kg: 1000, g: 1, mg: 0.001, 'm\u00b3': 1000, 'dm\u00b3': 1, L: 1, mL: 0.001, 'cm\u00b3': 0.001,
    mol: 1, mmol: 0.001, '\u00b5mol': 1e-6, kJ: 1000, J: 1, s: 1, min: 60,
    m: 1, cm: 0.01, mm: 0.001, nm: 1e-9, K: 1, '\u00b0C': 1, C: 1, V: 1, kPa: 1000, A: 1, pH: 1
  };

  function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }

  function normText(s) {
    return String(s === undefined || s === null ? '' : s)
      .toLowerCase().trim()
      .replace(/\u00a0/g, ' ').replace(/\u2212/g, '-')
      .replace(/(\d),(\d)/g, '$1.$2').replace(/\s+/g, ' ');
  }

  function toNum(v) {
    if (typeof v === 'boolean' || v === null || v === undefined) return null;
    var n = Number(String(v).trim().replace(/\u00a0/g, '').replace(/\u2212/g, '-').replace(',', '.'));
    return isFinite(n) ? n : null;
  }

  function basisTag(u) {
    if (u.indexOf('(m/m)') !== -1) return 'pct_mm';
    if (u.indexOf('(m/V)') !== -1 || u.indexOf('(m/v)') !== -1) return 'pct_mv';
    if (u.indexOf('(V/V)') !== -1 || u.indexOf('(v/v)') !== -1) return 'pct_vv';
    return u.trim() === '%' ? 'pct_bare' : '';
  }

  function sameDim(a, b) {
    var ka = Object.keys(a || {}).sort(), kb = Object.keys(b || {}).sort();
    if (ka.length !== kb.length) return false;
    for (var i = 0; i < ka.length; i += 1) if (ka[i] !== kb[i] || a[ka[i]] !== b[kb[i]]) return false;
    return true;
  }

  function normalizeQuantity(val, unitStr, terms) {
    var num = toNum(val);
    var u = String(unitStr || '').trim();
    if (num === null || !u) return null;
    if (u === '%' || u === '% (m/m)' || u === '% (m/V)' || u === '% (V/V)' || u === '1' || u === 'fraction' || u === 'fraction (m/V)' || u === 'ppm') {
      return {
        rawValue: String(val), rawUnit: u,
        canonicalValue: u === 'ppm' ? num * 1e-6 : (u.charAt(0) === '%' ? num * 0.01 : num),
        dimensionVector: {},
        basisTag: u === 'ppm' ? 'ppm_or_fraction' : (u.charAt(0) === '%' ? basisTag(u) : 'dimensionless')
      };
    }
    var T = root.SimTerms;
    if (!T || typeof T.parseUnit !== 'function') return null;
    var parsed;
    try { parsed = T.parseUnit(u, terms); } catch (e) { return null; }
    var sc = 1, i, t;
    for (i = 0; i < parsed.numerator.length; i += 1) {
      t = parsed.numerator[i];
      if (!has(SCALE, t.element)) return null;
      sc *= Math.pow(SCALE[t.element], t.exponent);
    }
    for (i = 0; i < parsed.denominator.length; i += 1) {
      t = parsed.denominator[i];
      if (!has(SCALE, t.element)) return null;
      sc /= Math.pow(SCALE[t.element], t.exponent);
    }
    return {
      rawValue: String(val), rawUnit: u,
      canonicalValue: num * sc,
      dimensionVector: parsed.dimensionVector || {},
      basisTag: ''
    };
  }

  function extractQuantities(text, terms) {
    var clean = String(text || '').replace(/<[^>]+>/g, ' ');
    var re = /(?:^|[^A-Za-z0-9.])([\u2212\-]?\d+(?:[.,]\d+)?)\s*(%\s*\([mVv]\/[mVv]\)|%|[A-Za-z\u00b5\u00b0][A-Za-z0-9\u00b5\u00b0\u00b3\u00b2\u00b9\u207b\u00b9\u207b\u00b2\u207b\u00b3^\/\u00b7()]*)/g;
    var out = [], m;
    while ((m = re.exec(clean)) !== null) {
      var u = m[2].trim().replace(/[.,;:)]+$/, '').replace(/%\s*\(/, '% (');
      var nq = normalizeQuantity(m[1], u, terms);
      if (nq) { nq.matchedText = m[1] + ' ' + u; out.push(nq); }
    }
    return out;
  }

  function numForms(val, distinctive) {
    var out = [], n = Number(val);
    if (!isFinite(n)) return out;
    if (Math.floor(n) === n) {
      var s = String(Math.round(n));
      if (Math.abs(n) >= 10 && !has(COMMON_BARE, s)) out.push(s);
      if (!has(COMMON_BARE, s)) { out.push(n.toFixed(1)); out.push(n.toFixed(2)); }
      else if (distinctive) out.push(n.toFixed(2));
    } else {
      var cand = [String(n), n.toFixed(1), n.toFixed(2), n.toFixed(3)];
      for (var i = 0; i < cand.length; i += 1) {
        if (cand[i] !== String(n) && cand[i].replace(/[-.]/g, '').replace(/^0+/, '').length < 2) continue;
        if (!has(COMMON_BARE, cand[i]) && out.indexOf(cand[i]) === -1) out.push(cand[i]);
        var tr = cand[i].indexOf('.') !== -1 ? cand[i].replace(/0+$/, '').replace(/\.$/, '') : cand[i];
        if (tr && !has(COMMON_BARE, tr) && out.indexOf(tr) === -1) out.push(tr);
      }
    }
    return out;
  }

  function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function scanSurface(fid, surface, text, targets, terms) {
    var norm = normText(String(text || '').replace(/<[^>]+>/g, ' '));
    var findings = [], seen = Object.create(null);
    var exts = terms ? extractQuantities(text, terms) : [];
    for (var i = 0; i < targets.length; i += 1) {
      var tgt = targets[i];
      var forms = toNum(tgt.value) !== null ? numForms(toNum(tgt.value), Boolean(tgt.distinctive)) : [];
      for (var j = 0; j < forms.length; j += 1) {
        var f = forms[j];
        if (has(COMMON_BARE, f) || /^-?\d$/.test(f)) continue;
        var re = new RegExp('(^|[^a-z0-9.])' + escapeRe(f) + '(?![a-z0-9]|\\.\\d)');
        if (re.test(norm) && !seen[surface + ':' + f]) {
          seen[surface + ':' + f] = 1;
          findings.push({ errorId: 'E_LEAK_DETECTED', surface: surface, matchKind: 'numeric', figureId: fid, leakedRaw: f, targetRaw: tgt.value + ' ' + (tgt.unit || '') });
        }
      }
      if (tgt.unit && terms) {
        var tn = normalizeQuantity(tgt.value, tgt.unit, terms);
        if (tn) {
          for (var k = 0; k < exts.length; k += 1) {
            var ex = exts[k];
            if (sameDim(ex.dimensionVector, tn.dimensionVector) && ex.basisTag === tn.basisTag) {
              var tol = Math.max(1e-9, Math.abs(tn.canonicalValue) * 1e-6);
              if (Math.abs(ex.canonicalValue - tn.canonicalValue) <= tol && !seen[surface + ':u:' + ex.matchedText]) {
                seen[surface + ':u:' + ex.matchedText] = 1;
                findings.push({ errorId: 'E_LEAK_DETECTED', surface: surface, matchKind: 'unit_normalized', figureId: fid, leakedRaw: ex.matchedText, targetRaw: tgt.value + ' ' + tgt.unit });
              }
            }
          }
        }
      }
    }
    return findings;
  }

  function checkBorderline(rec, targets, terms) {
    if (!rec.gradeable) return [];
    var ranges = [], flags = [];
    var axes = rec.axes || {};
    ['x', 'y'].forEach(function (k) {
      if (axes[k] && axes[k].min !== undefined && axes[k].max !== undefined) {
        ranges.push({ axis: 'axes.' + k, min: Number(axes[k].min), max: Number(axes[k].max), step: Number(axes[k].step || 0), unit: axes[k].unit || '' });
      }
    });
    var bg = rec.burette_geometry || {};
    (bg.columns || []).forEach(function (col) {
      if (col.view_min_ml !== undefined && col.view_max_ml !== undefined) {
        ranges.push({ axis: 'burette.' + (col.id || 'col'), min: Number(col.view_min_ml), max: Number(col.view_max_ml), step: Number(bg.division_ml || 0.1), unit: 'mL' });
      }
    });
    for (var i = 0; i < ranges.length; i += 1) {
      var r = ranges[i], span = r.max - r.min;
      if (!(span > 0)) continue;
      for (var j = 0; j < targets.length; j += 1) {
        var tgt = targets[j], tv = toNum(tgt.value);
        if (tv === null) continue;
        var tInAxis = null;
        if (!r.unit && (!tgt.unit || tgt.unit === '1')) tInAxis = tv;
        else if (r.unit && tgt.unit && terms) {
          var tn = normalizeQuantity(tv, tgt.unit, terms), an = normalizeQuantity(1, r.unit, terms);
          if (tn && an && sameDim(tn.dimensionVector, an.dimensionVector) && tn.basisTag === an.basisTag && an.canonicalValue) {
            tInAxis = tn.canonicalValue / an.canonicalValue;
          }
        }
        if (tInAxis === null) continue;
        var pos = (tInAxis - r.min) / span;
        if ((pos >= -0.001 && pos <= 0.02) || (pos >= 0.98 && pos <= 1.001) || (r.step > 0 && span <= r.step * 2 && pos >= 0 && pos <= 1)) {
          flags.push({ flagId: 'FLAG_BORDERLINE_RANGE', ruleId: RULES.borderline, figureId: rec.id, axis: r.axis, targetValue: tv + ' ' + (tgt.unit || ''), normalizedPosition: pos.toFixed(4) });
        }
      }
    }
    return flags;
  }

  function scanFigureRecord(rec, options) {
    options = options || {};
    var terms = options.terms || (root.SimTerms && root.SimTerms.getDefault ? root.SimTerms.getDefault() : null);
    var targets = (options.targets || rec.answer_targets || []).slice();
    var ex = rec.leak_scan_exemption;
    var errors = [], exNorms = [], isExempt = false;
    if (ex && ex.exempt) {
      if (rec.gradeable) errors.push(rec.id + ': [E_LEAK_ILLEGAL_EXEMPTION] Gradeable figure cannot exempt answer targets.');
      else if (!has(ALLOWED_EXEMPT, ex.reason_code) || !ex.reason_lv || ex.reason_lv.trim().length < 20 || !Array.isArray(ex.exempted_values) || !ex.exempted_values.length) {
        errors.push(rec.id + ': [E_LEAK_BAD_EXEMPTION] Invalid exemption metadata.');
      } else {
        isExempt = true;
        for (var i = 0; i < ex.exempted_values.length; i += 1) {
          var ev = ex.exempted_values[i], nq = normalizeQuantity(ev.value, ev.unit || '1', terms);
          if (nq) exNorms.push(nq);
        }
      }
    }
    var cleanData = {};
    Object.keys(rec).forEach(function (k) { if (k !== 'answer_targets' && k !== 'leak_scan_exemption' && k !== 'grading_reference') cleanData[k] = rec[k]; });
    var anns = (rec.annotations || []).map(function (a) {
      if (a.text_override_lv) return a.text_override_lv;
      if (terms && a.annotation_key && root.SimTerms) { try { return root.SimTerms.lookup(a.annotation_key, null, terms); } catch (e) { return a.annotation_key; } }
      return a.annotation_key || '';
    }).join(' | ');
    var svg = options.renderedSvg !== undefined ? options.renderedSvg :
      (root.SimFigures && typeof root.SimFigures.renderFigureSvg === 'function' ? root.SimFigures.renderFigureSvg(rec, { terms: terms, theme: 'light' }) : '');

    var raw = [].concat(
      scanSurface(rec.id, 'data', JSON.stringify(cleanData), targets, terms),
      scanSurface(rec.id, 'annotations', anns, targets, terms),
      svg ? scanSurface(rec.id, 'rendered', svg, targets, terms) : []
    );
    var leaks = [], exemptedHits = [];
    for (var j = 0; j < raw.length; j += 1) {
      var fnd = raw[j], matchedEx = false;
      if (isExempt) {
        var qs = extractQuantities(fnd.targetRaw || fnd.leakedRaw, terms);
        for (var q = 0; q < qs.length && !matchedEx; q += 1) {
          for (var e = 0; e < exNorms.length; e += 1) {
            if (sameDim(qs[q].dimensionVector, exNorms[e].dimensionVector) && qs[q].basisTag === exNorms[e].basisTag &&
                Math.abs(qs[q].canonicalValue - exNorms[e].canonicalValue) <= Math.max(1e-9, Math.abs(exNorms[e].canonicalValue) * 1e-6)) {
              matchedEx = true; break;
            }
          }
        }
      }
      if (matchedEx) exemptedHits.push(fnd);
      else { leaks.push(fnd); errors.push(rec.id + ': [E_LEAK_DETECTED] (' + fnd.surface + ') ' + fnd.leakedRaw); }
    }
    var flags = checkBorderline(rec, targets, terms);
    var outcome = errors.length ? 'FAIL' : (isExempt ? 'EXEMPT' : (flags.length ? 'FLAG' : 'PASS'));
    return { figureId: rec.id, outcome: outcome, leaks: leaks, flags: flags, exempt: isExempt, exemptedHitsCount: exemptedHits.length, errors: errors };
  }

  root.SimLeakScan = {
    RULES: RULES,
    normalizeQuantity: normalizeQuantity,
    extractQuantities: extractQuantities,
    scanFigureRecord: scanFigureRecord
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.SimLeakScan;
})(typeof globalThis !== 'undefined' ? globalThis : this);
