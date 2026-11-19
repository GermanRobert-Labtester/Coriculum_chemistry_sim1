#!/usr/bin/env node
/**
 * N15 runtime verification for the built T6-7 figure island:
 * - 45 figures total (8 N15 T6-7)
 * - deterministic two-run SVG for all 8 T67 records, no raw colours
 * - titration curve peak/inflection agreement, V-05 copy, wrong-indicator trap
 * - reading strip 0.1 mL attributes and calibration span/reading rendering
 * - practice leak scans + planted leaks
 * - truncated island degrades at JSON parse
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const HTML_PATH = path.join(ROOT, 'output', 'simulator.html');

function assert(cond, msg) {
  if (!cond) {
    console.error('FAIL check_n15_runtime:', msg);
    process.exit(1);
  }
}
function sha256(str) {
  return crypto.createHash('sha256').update(str, 'utf8').digest('hex');
}
function island(html, id) {
  const re = new RegExp('<script[^>]*id="' + id + '"[^>]*>([\\s\\S]*?)<\\/script>');
  const m = html.match(re);
  assert(m, 'missing island ' + id);
  return m[1];
}
function loadSandbox() {
  const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };
  sb.globalThis = sb;
  vm.createContext(sb);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'src/terms-loader.js'), 'utf8'), sb);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'src/figure-framework.js'), 'utf8'), sb);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'src/leak-scan.js'), 'utf8'), sb);
  return sb;
}
function inflectionX(points) {
  let bx = 0, bd = -1;
  for (let i = 0; i < points.length - 1; i += 1) {
    const d = Math.abs(points[i + 1].y - points[i].y);
    if (d > bd) { bd = d; bx = (points[i].x + points[i + 1].x) / 2; }
  }
  return bx;
}
function copyText(rec) {
  return [rec.subtitle_lv, rec.description_lv, rec.scope_note_lv]
    .concat((rec.annotations || []).map(a => a.text_override_lv || ''))
    .join(' ').toLowerCase();
}

const html = fs.readFileSync(HTML_PATH, 'utf8');
const sb = loadSandbox();
const termsData = JSON.parse(island(html, 'sim-terms'));
const terms = sb.SimTerms.load({ getElementById(id) { return id === 'sim-terms' ? { textContent: JSON.stringify(termsData) } : null; } });
const figuresIsland = JSON.parse(island(html, 'sim-figures'));
const all = figuresIsland.figures || [];
assert(all.length >= 45, 'expected >=45 figures, got ' + all.length);
const t67 = all.filter(r => (r.id || '').indexOf('FIG-T67-') === 0);
assert(t67.length === 8, 'expected 8 T67 figures, got ' + t67.length);
const byId = Object.fromEntries(t67.map(r => [r.id, r]));

const svg = {};
for (const rec of t67) {
  const a = sb.SimFigures.renderFigureSvg(rec, { terms, theme: 'print' });
  const b = sb.SimFigures.renderFigureSvg(rec, { terms, theme: 'print' });
  assert(a === b, 'non-deterministic render: ' + rec.id);
  assert(!/#[0-9a-fA-F]{3,6}\b|rgb\(/.test(a), 'raw colour in render: ' + rec.id);
  svg[rec.id] = a;
}

const strong = byId['FIG-T67-TITR-STRONG'];
const weak = byId['FIG-T67-TITR-WEAK'];
const wrong = byId['FIG-T67-TITR-WRONG-IND'];
const practiceT = byId['FIG-T67-TITR-PRACTICE'];
const calMaster = byId['FIG-T67-CAL-MASTER'];
const calEdge = byId['FIG-T67-CAL-NEAR-EDGE'];
const calPractice = byId['FIG-T67-CAL-PRACTICE'];

const modelRows = [];
for (const id of ['FIG-T67-TITR-STRONG', 'FIG-T67-TITR-WEAK', 'FIG-T67-TITR-MASTER-KMNO4', 'FIG-T67-TITR-PRACTICE']) {
  const rec = byId[id];
  const cm = rec.series[0].curve_model;
  const g = sb.SimFigures.generateCurvePoints(cm);
  const declared = rec.titration_spec.declared_equivalence_volume_ml;
  const displayed = declared ? Number(declared) : g.peak.x;
  const infl = inflectionX(g.points);
  assert(Math.abs(infl - displayed) <= 0.15, id + ' inflection ' + infl + ' != ' + displayed);
  assert(g.points.length === 401, id + ' point count');
  modelRows.push({ id, veq: g.peak.x, declared: displayed, inflection: infl });
}

assert(svg['FIG-T67-TITR-STRONG'].indexOf('data-indicator-band="true"') >= 0, 'strong band missing');
assert(svg['FIG-T67-TITR-STRONG'].indexOf('data-equivalence-x="25.00"') >= 0, 'strong equivalence marker');
assert(svg['FIG-T67-TITR-STRONG'].indexOf('data-strip-reading-ml="25.00"') >= 0, 'strong strip reading');
assert(svg['FIG-T67-TITR-STRONG'].indexOf('data-indicator-y-min="8.2"') >= 0, 'strong band min');
assert(svg['FIG-T67-TITR-WEAK'].indexOf('data-buffer-region="true"') >= 0, 'weak buffer region');
assert(svg['FIG-T67-TITR-WEAK'].indexOf('data-half-equivalence-x="12.50"') >= 0, 'weak half-equivalence');
assert(svg['FIG-T67-TITR-WRONG-IND'].indexOf('data-endpoint-x="7.77"') >= 0, 'wrong endpoint marker');
assert(svg['FIG-T67-TITR-WRONG-IND'].indexOf('data-indicator-y-min="3.1"') >= 0, 'wrong band');
assert(svg['FIG-T67-CAL-MASTER'].indexOf('data-fit-x-max="0.016"') >= 0, 'cal master fit span');
assert(svg['FIG-T67-CAL-MASTER'].indexOf('data-reading-dot="true"') >= 0, 'cal master reading dot');
assert(svg['FIG-T67-CAL-NEAR-EDGE'].indexOf('data-reading-x="0.01549"') >= 0, 'near-edge reading x');
assert(svg['FIG-T67-CAL-PRACTICE'].indexOf('data-reading-dot') < 0, 'practice calibration leaks reading');
assert(svg['FIG-T67-CAL-PRACTICE'].indexOf('data-signal-marker="true"') >= 0, 'practice signal marker');

const v05Rows = [];
for (const rec of [strong, weak, wrong, byId['FIG-T67-TITR-MASTER-KMNO4']]) {
  const txt = copyText(rec);
  const eq = /ekvivalences\s+punkt/.test(txt);
  const ep = /beigu\s+punkt/.test(txt);
  const why = txt.indexOf('titrlēšanas kļūda') >= 0 || txt.indexOf('nav ekvivalences punkts') >= 0;
  assert(eq && ep && why, rec.id + ' V-05 wording');
  v05Rows.push({ id: rec.id, equivalence: eq, endpoint: ep, explained: why });
}
assert(/neatbilst/.test(copyText(wrong)), 'wrong-indicator annotation must name the mismatch');

const scanPracticeT = sb.SimLeakScan.scanFigureRecord(practiceT, { terms });
const scanPracticeC = sb.SimLeakScan.scanFigureRecord(calPractice, { terms });
assert(scanPracticeT.outcome === 'PASS', 'titration practice leak: ' + scanPracticeT.outcome);
assert(scanPracticeC.outcome === 'PASS', 'calibration practice leak: ' + scanPracticeC.outcome);
function planted(rec, text) {
  const p = JSON.parse(JSON.stringify(rec));
  p.annotations = [{ id: 'p', annotation_key: 'fig.annot.t67_scope', text_override_lv: text }];
  return sb.SimLeakScan.scanFigureRecord(p, { terms });
}
const plantT = planted(practiceT, 'Atbilde: 20,45 mL.');
const plantC = planted(calPractice, 'Atbilde: 0,01459 mg/mL.');
assert(plantT.outcome === 'FAIL', 'planted titration leak not caught');
assert(plantC.outcome === 'FAIL', 'planted calibration leak not caught');

const rawFigs = island(html, 'sim-figures');
const cut = rawFigs.slice(0, Math.floor(rawFigs.length / 2));
let truncCode = 'NO_ERROR';
try { JSON.parse(cut); } catch (e) { truncCode = 'E_FIGURES_JSON'; }
assert(truncCode === 'E_FIGURES_JSON', 'truncated island did not degrade');

const report = {
  status: 'PASS',
  total_figures: all.length,
  t67_figures: t67.length,
  determinism: { records: t67.length, two_run: true },
  models: modelRows,
  v05: v05Rows,
  wrong_indicator: true,
  calibration: { master_reading: true, near_edge_reading: true, practice_no_reading: true },
  leak: { titration: scanPracticeT.outcome, calibration: scanPracticeC.outcome, planted_titration: plantT.outcome, planted_calibration: plantC.outcome },
  truncation: truncCode,
  svg_sha256: Object.fromEntries(t67.map(r => [r.id, sha256(svg[r.id])])),
};
console.log(JSON.stringify(report));
