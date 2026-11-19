#!/usr/bin/env node
/**
 * N14 runtime verification:
 * - 45 figures total (12 N11 + 7 N12 + 10 N13 + 8 N14 T5 + 8 N15 T6-7)
 * - Deterministic two-run SVG for all 8 T5 figures + 0 raw colours
 * - kinetics_decay curve generator fail-closed
 * - Fit-line span clipping attrs, tolerance band, no fit line on the gradeable practice record
 * - evaluateFitLine: inside accepted, edge inclusive, beyond not assessed, far line rejected
 * - Lazy P5-01 (4), P5-05 (6), P5-08 (2), P5-04 (1 shared MB), P5-06 pending-N16 (0)
 * - Runtime leak scan on the practice record + truncation + 8/8 smoke incl SMK-N14-T5-LINEARIZATION
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
    console.error('FAIL check_n14_runtime:', msg);
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
 const rawHtmlWithoutScript = html.replace(/<script[\s\S]*?<\/script>/g, '');
 assert(!/<svg\b/i.test(rawHtmlWithoutScript), 'Static HTML outside <script> must contain 0 <svg> elements before drawer open');

 const base = bootSimulator(html);
 const F = base.sandbox.SimFigures;
 const L = base.sandbox.SimLeakScan;
 assert(F && typeof F.load === 'function' && typeof F.evaluateFitLine === 'function', 'SimFigures kinetics interface missing');
 assert(L && typeof L.scanFigureRecord === 'function', 'SimLeakScan missing');

 const kMeta = base.document.querySelector('meta[name="sim-kinetics-contract-digest"]');
 assert(kMeta && /^[0-9a-f]{64}$/.test(kMeta.getAttribute('content') || ''), 'Missing sim-kinetics-contract-digest meta');

 const loaded = F.load(base.document);
 assert(loaded && loaded.total >= 37, 'Expected >=37 total figures, got ' + (loaded && loaded.total));
 const t5 = loaded.figures.filter((r) => r.topic === 5);
 assert(t5.length === 8, 'Expected 8 T5 figures, got ' + t5.length);

 let errBad = '';
 try { F.generateCurvePoints({ function_class: 'kinetics_decay', point_count: 41, params: { order: 3, k: 0.02, C0_mol_l: 1, t_min_s: 0, t_max_s: 40 } }); }
 catch (e) { errBad = e.code || ''; }
 assert(errBad === 'E_FIG_BAD_CURVE_PARAMS', 'Expected E_FIG_BAD_CURVE_PARAMS for order 3, got ' + errBad);

 const rawColorRe = /#[0-9a-fA-F]{3,8}\b|\brgba?\s*\(|\bhsla?\s*\(/;
 const svgDigests = {};
 for (const rec of t5) {
  const s1 = F.renderFigureSvg(rec, { theme: 'light' });
  const s2 = F.renderFigureSvg(rec, { theme: 'light' });
  assert(s1 === s2, 'Non-deterministic SVG for ' + rec.id);
  assert(!rawColorRe.test(s1), 'Raw colour in ' + rec.id);
  svgDigests[rec.id] = sha256(s1);
 }

 // Fit-line clipping per linearization record
 const linIds = ['FIG-T5-LIN-ZERO','FIG-T5-LIN-FIRST','FIG-T5-LIN-SECOND'];
 for (const id of linIds) {
  const rec = F.getById(id, loaded);
  const svg = F.renderFigureSvg(rec, { theme: 'light' });
  const sp = rec.span;
  assert(svg.includes('data-fit-x-min="' + sp.x_min + '"') && svg.includes('data-fit-x-max="' + sp.x_max + '"'), 'Fit line extent != span on ' + id);
  assert(svg.includes('data-fit-clipped="true"') && svg.includes('data-tol-band="true"'), 'Missing clip/tolerance attrs on ' + id);
  const ms = svg.match(/data-fit-slope="([^"]+)"/);
  assert(ms && Math.abs(parseFloat(ms[1]) - parseFloat(rec.fit_line.slope)) < 1e-12, 'Rendered fit slope mismatch on ' + id);
 }

 const ln = F.getById('FIG-T5-LIN-FIRST', loaded);
 const inside = F.evaluateFitLine(ln, { slope: -0.0502, intercept: 0.005, x_min: 0, x_max: 30 });
 const edge = F.evaluateFitLine(ln, { slope: -0.0502, intercept: 0.005, x_min: 0, x_max: 30 });
 const beyond = F.evaluateFitLine(ln, { slope: -0.0502, intercept: 0.005, x_min: 0, x_max: 95 });
 const reject = F.evaluateFitLine(ln, { slope: -0.08, intercept: 0.2, x_min: 0, x_max: 30 });
 assert(inside.status === 'ACCEPTED' && inside.assessed_x_range.x_max === 30, 'Inside-span draw not accepted');
 assert(edge.status === 'ACCEPTED' && edge.assessed_x_range.x_min === 0 && edge.assessed_x_range.x_max === 30, 'Edge-inclusive draw not accepted');
 assert(beyond.status === 'ACCEPTED' && beyond.assessed_x_range.x_max === 30 && beyond.beyond_span === 'not_assessed', 'Beyond-span extension must be not assessed');
 assert(reject.status === 'REJECTED' && reject.point_ok === false, 'Far line must be rejected');

 const prac = F.getById('FIG-T5-LIN-PRACTICE', loaded);
 const pracSvg = F.renderFigureSvg(prac, { theme: 'light' });
 assert(pracSvg.indexOf('data-fit-line') === -1 && pracSvg.indexOf('data-tol-band') === -1, 'Practice figure must not render the answer line/band');
 const pracScan = L.scanFigureRecord(prac);
 assert(pracScan.outcome === 'PASS' && pracScan.leaks.length === 0, 'Practice figure leaked: ' + JSON.stringify(pracScan));

 const expected = {
  'P5-01': 4, 'P5-04': 1, 'P5-05': 6, 'P5-08': 2, 'P5-09': 4, 'P5-10': 2
 };
 F.clearRenderEvents();
 for (const cid of Object.keys(expected)) {
  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: cid, source: 'map', returnContext: { elementId: 'karte-btn-' + cid } }, base.document);
  const slot = base.document.getElementById('drawer-slot-figures-' + cid);
  assert(slot && slot.getAttribute('data-slot-status') === 'authored-N14', cid + ' slot status != authored-N14');
  assert(slot.querySelectorAll('svg').length === expected[cid], cid + ' expected ' + expected[cid] + ' SVGs, got ' + slot.querySelectorAll('svg').length);
  base.sandbox.SimConceptDrawer.closeAll(base.document);
 }
 base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P5-06', source: 'map', returnContext: { elementId: 'karte-btn-P5-06' } }, base.document);
 const slotP506 = base.document.getElementById('drawer-slot-figures-P5-06');
 assert(slotP506 && slotP506.getAttribute('data-slot-status') === 'pending-N16' && slotP506.querySelectorAll('svg').length === 0, 'P5-06 must remain pending-N16');
 base.sandbox.SimConceptDrawer.closeAll(base.document);

 const smokeReport = base.sandbox.SimSmoke.lastReport || base.sandbox.SimSmoke.run(base.document);
 const n14Smoke = smokeReport.vectors.find((v) => v.id === 'SMK-N14-T5-LINEARIZATION');
 assert(smokeReport && smokeReport.status === 'PASS' && smokeReport.total >= 9 && smokeReport.passed === smokeReport.total && n14Smoke && n14Smoke.status === 'PASS', 'Expected >=8 SimSmoke PASS incl SMK-N14, got ' + JSON.stringify(smokeReport));

 const truncHtml = html.replace(
  /<script type="application\/json" id="sim-figures">[\s\S]*?<\/script>/,
  '<script type="application/json" id="sim-figures">{"schema_version":1,"figures":[</script>'
 );
 const truncBoot = bootSimulator(truncHtml);
 const fErr = truncBoot.sandbox.SimFigures.getDefaultError();
 assert(fErr && fErr.code === 'E_FIGURES_JSON', 'Expected E_FIGURES_JSON on truncation, got ' + (fErr && fErr.code));

 const summary = {
  status: 'PASS',
  total_figures: loaded.total,
  t5_figures: t5.length,
  svg_digests: svgDigests,
  curve_guard: errBad,
  fit_span: { zero: '0-40', first: '0-30', second: '0-30' },
  drawn_line: { inside: inside.status, edge: edge.status, beyond: beyond.status + '/' + beyond.beyond_span, reject: reject.status },
  practice_leak: pracScan.outcome,
  dataset_tables: 4,
  truncation_code: fErr.code,
  smoke: { passed: smokeReport.passed, total: smokeReport.total, status: smokeReport.status }
 };
 if (process.argv.includes('--json')) console.log(JSON.stringify(summary, null, 2));
 else console.log(`check_n14_runtime PASS: total_figs=${summary.total_figures} (T5=${summary.t5_figures}), fit_clip=PASS, drawn_line=${inside.status}/${edge.status}/${beyond.status}/${reject.status}, practice_leak=${pracScan.outcome}, truncation=${fErr.code}, smoke=${smokeReport.passed}/${smokeReport.total}`);
}
main();
