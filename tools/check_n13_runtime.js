#!/usr/bin/env node
/**
 * N13 runtime verification:
 * - Lazy rendering of T4 figures in concept drawers (P4-01..P4-11 authored-N13; P5-01 pending-N14)
 * - Deterministic two-run SVG digests for all 10 T4 figures + 0 raw hex/rgb colors
 * - Fail-closed curve generator validation (E_FIG_UNKNOWN_CURVE_CLASS, E_FIG_BAD_CURVE_PARAMS)
 * - Maxwell-Boltzmann geometric tail-boundary == threshold-line match & peak shift/flattening in SVG
 * - Hess cycle closure & reverse-arrow traversal attributes in SVG
 * - Runtime SimLeakScan on FIG-T4-HESS-PRACTICE-SYNTH and FIG-T4-ENERGY-GRADE-READING + planted leak
 * - Truncated #sim-figures graceful error banner
 * - 7/7 smoke subset vectors including SMK-N13-T4-HESS-CURVE
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
    console.error('FAIL check_n13_runtime:', msg);
    process.exit(1);
  }
}

function sha256(str) {
  return crypto.createHash('sha256').update(str, 'utf8').digest('hex');
}

function createDomFromHtml(html) {
  const elementsById = new Map();
  const bodyChildren = [];
  const headMeta = new Map();

  function makeEl(tag, attrs = {}) {
    const el = {
      tagName: String(tag || 'DIV').toUpperCase(),
      id: attrs.id || '',
      className: attrs.class || '',
      textContent: '',
      innerHTML: '',
      hidden: Boolean(attrs.hidden),
      style: {},
      dataset: {},
      attributes: new Map(),
      children: [],
      parentNode: null,
      listeners: {},
      setAttribute(k, v) {
        const s = String(v);
        this.attributes.set(k, s);
        if (k === 'id') {
          this.id = s;
          elementsById.set(s, this);
        } else if (k === 'class') {
          this.className = s;
        } else if (k === 'hidden') {
          this.hidden = true;
        } else if (k.startsWith('data-')) {
          const camel = k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
          this.dataset[camel] = s;
        }
      },
      getAttribute(k) {
        if (k === 'id') return this.id || null;
        if (k === 'class') return this.className || null;
        return this.attributes.has(k) ? this.attributes.get(k) : null;
      },
      hasAttribute(k) {
        return this.attributes.has(k) || (k === 'hidden' && this.hidden);
      },
      removeAttribute(k) {
        this.attributes.delete(k);
        if (k === 'hidden') this.hidden = false;
      },
      appendChild(child) {
        if (!child) return child;
        child.parentNode = this;
        this.children.push(child);
        if (child.id) elementsById.set(child.id, child);
        return child;
      },
      removeChild(child) {
        const idx = this.children.indexOf(child);
        if (idx >= 0) this.children.splice(idx, 1);
        return child;
      },
      addEventListener(ev, fn) {
        (this.listeners[ev] = this.listeners[ev] || []).push(fn);
      },
      focus() {},
       scrollIntoView() {},
      get firstChild() {
        return this.children[0] || null;
      },
      querySelector(sel) {
        return this.querySelectorAll(sel)[0] || null;
      },
      querySelectorAll(sel) {
        const out = [];
        function walk(node) {
          for (const ch of node.children || []) {
            if (matches(ch, sel)) out.push(ch);
            walk(ch);
          }
        }
        walk(this);
        return out;
      }
    };
    for (const [k, v] of Object.entries(attrs)) {
      el.setAttribute(k, v);
    }
    return el;
  }

  function matches(el, sel) {
    if (!sel) return false;
    if (sel.startsWith('#')) return el.id === sel.slice(1);
    if (sel.startsWith('.')) return (el.className || '').split(/\s+/).includes(sel.slice(1));
    if (sel === 'svg') return el.tagName === 'SVG';
    if (sel === '[data-slot-kind="figures"]') return el.getAttribute('data-slot-kind') === 'figures';
    return el.tagName === sel.toUpperCase();
  }

  const metaRe = /<meta\s+name="([^"]+)"\s+content="([^"]*)"/g;
  let mm;
  while ((mm = metaRe.exec(html)) !== null) {
    headMeta.set(mm[1], mm[2]);
  }

  const idTagRe = /<([a-zA-Z0-9]+)\b([^>]*?\bid="([^"]+)"[^>]*)>/g;
  let m;
  while ((m = idTagRe.exec(html)) !== null) {
    const [, tag, attrStr, id] = m;
    if (tag.toLowerCase() === 'script') continue;
    const attrs = { id };
    const clsM = attrStr.match(/\bclass="([^"]*)"/);
    if (clsM) attrs.class = clsM[1];
    if (/\bhidden\b/.test(attrStr)) attrs.hidden = true;
    const dataRe = /\b(data-[a-z0-9-]+)="([^"]*)"/g;
    let dm;
    while ((dm = dataRe.exec(attrStr)) !== null) {
      attrs[dm[1]] = dm[2];
    }
    const el = makeEl(tag, attrs);
    elementsById.set(id, el);
    bodyChildren.push(el);
  }

  const jsonScriptRe = /<script\s+type="application\/json"\s+id="([^"]+)">([\s\S]*?)<\/script>/g;
  let jm;
  while ((jm = jsonScriptRe.exec(html)) !== null) {
    const el = makeEl('script', { id: jm[1], type: 'application/json' });
    el.textContent = jm[2];
    elementsById.set(jm[1], el);
  }

  const documentElement = makeEl('html', { lang: 'lv', 'data-theme': 'light' });
  const body = makeEl('body');
  body.children = bodyChildren;

  const document = {
    documentElement,
    body,
    createElement(tag) {
      return makeEl(tag);
    },
    createElementNS(_ns, tag) {
      return makeEl(tag);
    },
    getElementById(id) {
      return elementsById.get(id) || null;
    },
    querySelector(sel) {
      const mMeta = sel.match(/^meta\[name="([^"]+)"\]$/);
      if (mMeta) {
        const val = headMeta.get(mMeta[1]);
        return val !== undefined ? { getAttribute: (k) => (k === 'content' ? val : null) } : null;
      }
      if (sel.startsWith('#')) return elementsById.get(sel.slice(1)) || null;
      return body.querySelector(sel);
    },
    querySelectorAll(sel) {
      return body.querySelectorAll(sel);
    },
    addEventListener() {}
  };

  return { document, elementsById, headMeta };
}

function bootSimulator(html) {
  const { document, elementsById, headMeta } = createDomFromHtml(html);
  const execRe = /<script>([\s\S]*?)<\/script>/;
  const ex = html.match(execRe);
  assert(ex && ex[1], 'Missing executable <script> in simulator.html');

  const sandbox = {
    window: null,
    document,
    console,
    Date,
    Math,
    JSON,
    Error,
    TypeError,
    RangeError,
    String,
    Number,
    Boolean,
    Array,
    Object,
    Map,
    Set,
    RegExp,
    parseInt,
    parseFloat,
    isNaN,
    isFinite,
    setTimeout: (fn) => { fn(); return 1; },
    clearTimeout: () => {}
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(ex[1], sandbox);
  return { sandbox, document, elementsById, headMeta };
}

function main() {
  assert(fs.existsSync(HTML_PATH), 'output/simulator.html not found');
  const html = fs.readFileSync(HTML_PATH, 'utf8');

  // 0. Initial static HTML has 0 <svg> tags (lazy_slot=true)
  const rawHtmlWithoutScript = html.replace(/<script[\s\S]*?<\/script>/g, '');
  assert(!/<svg\b/i.test(rawHtmlWithoutScript), 'Static HTML outside <script> must contain 0 <svg> elements before drawer open');

  const base = bootSimulator(html);
  const F = base.sandbox.SimFigures;
  const L = base.sandbox.SimLeakScan;
  assert(F && typeof F.load === 'function' && typeof F.generateCurvePoints === 'function', 'SimFigures curve extension missing');
  assert(L && typeof L.scanFigureRecord === 'function', 'SimLeakScan missing');

  const energyMeta = base.document.querySelector('meta[name="sim-energy-contract-digest"]');
  assert(energyMeta && /^[0-9a-f]{64}$/.test(energyMeta.getAttribute('content') || ''), 'Missing or invalid sim-energy-contract-digest meta');

  const loaded = F.load(base.document);
  assert(loaded && loaded.total >= 37, 'Expected >=37 total figures (12 N11 + 7 N12 + 10 N13 + 8 N14 + N15), got ' + (loaded && loaded.total));
  const t4Figs = loaded.figures.filter((r) => r.topic === 4);
  assert(t4Figs.length === 10, 'Expected 10 T4 figures, got ' + t4Figs.length);

  // 1. Fail-closed curve generation checks
  let errUnknown = '';
  let errBadBarrier = '';
  let errBadMb = '';
  try {
    F.generateCurvePoints({ function_class: 'cubic_spline_unknown', point_count: 30, params: {} });
  } catch (e) {
    errUnknown = e.code || '';
  }
  try {
    F.generateCurvePoints({
      function_class: 'energy_profile_single_barrier',
      point_count: 61,
      params: { x_min: 0, x_max: 1, x_ts: 0.48, plateau_frac: 0.12, E_r_kj_mol: 90, E_ts_kj_mol: 70, E_p_kj_mol: 0 }
    });
  } catch (e) {
    errBadBarrier = e.code || '';
  }
  try {
    F.generateCurvePoints({
      function_class: 'maxwell_boltzmann_3d',
      point_count: 193,
      params: { T_K: 300, R_kj_mol_k: 0.008314, E_min_kj_mol: 0, E_max_kj_mol: 24, Ea_threshold_kj_mol: 30 }
    });
  } catch (e) {
    errBadMb = e.code || '';
  }
  assert(errUnknown === 'E_FIG_UNKNOWN_CURVE_CLASS', 'Expected E_FIG_UNKNOWN_CURVE_CLASS, got ' + errUnknown);
  assert(errBadBarrier === 'E_FIG_BAD_CURVE_PARAMS', 'Expected E_FIG_BAD_CURVE_PARAMS on barrier<=reactant, got ' + errBadBarrier);
  assert(errBadMb === 'E_FIG_BAD_CURVE_PARAMS', 'Expected E_FIG_BAD_CURVE_PARAMS on Ea>=E_max, got ' + errBadMb);

  // 2. Two-run determinism + 0 raw hex/rgb colors across all 10 T4 figures
  const rawColorRe = /#[0-9a-fA-F]{3,8}\b|\brgba?\s*\(|\bhsla?\s*\(/;
  const svgDigests = {};
  for (const rec of t4Figs) {
    const s1 = F.renderFigureSvg(rec, { theme: 'light' });
    const s2 = F.renderFigureSvg(rec, { theme: 'light' });
    assert(s1 === s2, 'Non-deterministic SVG for ' + rec.id);
    assert(!rawColorRe.test(s1), 'Raw color literal found in rendered SVG for ' + rec.id);
    svgDigests[rec.id] = sha256(s1);
  }

  // 3. Maxwell-Boltzmann geometric tail == threshold & peak shift/flattening + light/dark/print parity
  for (const mbId of ['FIG-T4-MB-TWO-TEMP-COMPARE', 'FIG-T4-MB-BARRIER-SCOPE']) {
    const rec = F.getById(mbId, loaded);
    const svgL = F.renderFigureSvg(rec, { theme: 'light' });
    const svgD = F.renderFigureSvg(rec, { theme: 'dark' });
    const svgP = F.renderFigureSvg(rec, { theme: 'print' });
    assert(svgL.includes('fig-theme-light') && svgD.includes('fig-theme-dark') && svgP.includes('fig-theme-print'), 'Theme class missing on ' + mbId);

    const thrM = svgL.match(/data-threshold-x="([^"]+)"/);
    const tailMs = [...svgL.matchAll(/data-tail-start-x="([^"]+)"/g)].map((m) => m[1]);
    assert(thrM && tailMs.length === 2 && tailMs.every((v) => v === thrM[1]), 'Tail start x != threshold x on ' + mbId);

    const peakXs = [...svgL.matchAll(/data-peak-x="([^"]+)"/g)].map((m) => parseFloat(m[1]));
    const peakYs = [...svgL.matchAll(/data-peak-y="([^"]+)"/g)].map((m) => parseFloat(m[1]));
    assert(peakXs.length === 2 && peakXs[1] > peakXs[0], 'MB peak must shift right at higher T on ' + mbId);
    assert(peakYs.length === 2 && peakYs[1] > peakYs[0], 'MB peak must flatten (larger SVG y) at higher T on ' + mbId);
  }

  // 4. Hess cycle SVG checks (closure & reverse-arrow traversal)
  const svgRev = F.renderFigureSvg(F.getById('FIG-T4-HESS-REVERSE-TRAP', loaded), { theme: 'light' });
  assert(svgRev.includes('data-hess-traversal="reverse"') && svgRev.includes('fig-hess-reverse'), 'Reverse-trap Hess figure missing reverse traversal marker');
  assert(svgRev.includes('data-hess-closure="true"'), 'Reverse-trap Hess figure missing closure box');

  // 5. Lazy drawer activation for P4-01, P4-03, P4-06 and authored-N14 P5-01
  F.clearRenderEvents();
  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P4-01', source: 'map', returnContext: { elementId: 'karte-btn-P4-01' } }, base.document);
  const slotP401 = base.document.getElementById('drawer-slot-figures-P4-01');
  assert(slotP401 && slotP401.getAttribute('data-slot-status') === 'authored-N13', 'P4-01 slot status != authored-N13');
  assert(slotP401.querySelectorAll('svg').length === 2 && F.getRenderEvents().length === 2, 'Expected 2 lazy-rendered SVGs in P4-01 drawer');
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P4-03', source: 'map', returnContext: { elementId: 'karte-btn-P4-03' } }, base.document);
  const slotP403 = base.document.getElementById('drawer-slot-figures-P4-03');
  assert(slotP403 && slotP403.querySelectorAll('svg').length === 4, 'Expected 4 Hess SVGs in P4-03 drawer');
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P4-06', source: 'map', returnContext: { elementId: 'karte-btn-P4-06' } }, base.document);
  const slotP406 = base.document.getElementById('drawer-slot-figures-P4-06');
  assert(slotP406 && slotP406.querySelectorAll('svg').length === 3, 'Expected 3 SVGs in P4-06 drawer');
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P5-01', source: 'map', returnContext: { elementId: 'karte-btn-P5-01' } }, base.document);
  const slotP501 = base.document.getElementById('drawer-slot-figures-P5-01');
  assert(slotP501 && slotP501.getAttribute('data-slot-status') === 'authored-N14', 'P5-01 must be authored-N14');
  assert(slotP501.querySelectorAll('svg').length === 4, 'Expected 4 T5 figures in P5-01 drawer');
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  // 6. Runtime SimLeakScan on T4 gradeable records + planted leak
  const recHessGrade = F.getById('FIG-T4-HESS-PRACTICE-SYNTH', loaded);
  const recEnergyGrade = F.getById('FIG-T4-ENERGY-GRADE-READING', loaded);
  const scanHess = L.scanFigureRecord(recHessGrade);
  const scanEnergy = L.scanFigureRecord(recEnergyGrade);
  assert(scanHess.outcome === 'PASS' && scanHess.leaks.length === 0 && scanHess.flags.length === 0, 'FIG-T4-HESS-PRACTICE-SYNTH failed runtime leak scan');
  assert(scanEnergy.outcome === 'PASS' && scanEnergy.leaks.length === 0 && scanEnergy.flags.length === 0, 'FIG-T4-ENERGY-GRADE-READING failed runtime leak scan');

  const plantedHess = JSON.parse(JSON.stringify(recHessGrade));
  plantedHess.hess_spec.direct_path.label_lv = 'Tiešais ceļš: −219,0 kJ/mol';
  const scanPlanted = L.scanFigureRecord(plantedHess);
  assert(scanPlanted.outcome === 'FAIL' && scanPlanted.leaks.length >= 1, 'Runtime SimLeakScan missed planted -219,0 kJ/mol leak');

  // 7. Smoke subset (7/7 PASS)
  const smokeReport = base.sandbox.SimSmoke.lastReport || base.sandbox.SimSmoke.run(base.document);
  const n13Smoke = smokeReport.vectors.find((v) => v.id === 'SMK-N13-T4-HESS-CURVE');
  assert(smokeReport && smokeReport.status === 'PASS' && smokeReport.total >= 8 && smokeReport.passed === smokeReport.total && n13Smoke && n13Smoke.status === 'PASS', 'Expected >=8 SimSmoke PASS with SMK-N13-T4-HESS-CURVE, got ' + JSON.stringify(smokeReport));

  // 8. Truncation degradation on #sim-figures
  const truncHtml = html.replace(
    /<script type="application\/json" id="sim-figures">[\s\S]*?<\/script>/,
    '<script type="application/json" id="sim-figures">{"schema_version":1,"figures":[</script>'
  );
  const truncBoot = bootSimulator(truncHtml);
  const fErr = truncBoot.sandbox.SimFigures.getDefaultError();
  assert(fErr && fErr.code === 'E_FIGURES_JSON', 'Expected E_FIGURES_JSON on truncated #sim-figures, got ' + (fErr && fErr.code));
  const errBanner = truncBoot.document.getElementById('sim-figures-error');
  assert(errBanner && !errBanner.hidden && errBanner.textContent.includes('E_FIGURES_JSON'), 'Expected visible #sim-figures-error banner on truncation');

  const summary = {
    status: 'PASS',
    total_figures: loaded.total,
    t4_figures: t4Figs.length,
    svg_digests: svgDigests,
    curve_fail_closed: { unknown_class: errUnknown, bad_barrier: errBadBarrier, bad_mb: errBadMb },
    leak_scan_runtime: {
      hess_grade: scanHess.outcome,
      energy_grade: scanEnergy.outcome,
      planted_caught: scanPlanted.outcome === 'FAIL'
    },
    truncation_code: fErr.code,
    smoke: { passed: smokeReport.passed, total: smokeReport.total, status: smokeReport.status }
  };

  if (process.argv.includes('--json')) {
    console.log(JSON.stringify(summary, null, 2));
  } else {
    console.log(
      `check_n13_runtime PASS: total_figs=${summary.total_figures} (T4=${summary.t4_figures}), ` +
      `curve_guards=PASS, mb_geom=PASS, hess_closure=PASS, leak_scan=PASS, truncation=${summary.truncation_code}, smoke=${summary.smoke.passed}/${summary.smoke.total}`
    );
  }
}

main();
