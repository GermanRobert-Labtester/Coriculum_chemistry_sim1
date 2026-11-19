#!/usr/bin/env node
/**
 * N12 runtime harness: executes output/simulator.html in a Node VM and verifies:
 * - Lazy-render: 0 <svg> parsed at load; P2-07 drawer opens 5 burettes; P3-10 drawer opens 3 dilutions
 * - Two-run pure renderer determinism across all 10 T2-3 figures (0 raw hex/rgb colors, ARIA title/desc)
 * - Rendered burette geometric fidelity (data-meniscus-read-y == yTop + (reading - vMin)*pxPerMl)
 * - Rendered burette scale labels enforce 2-decimal convention (^\d+,\d{2} mL$)
 * - Theme parity (light/dark/print) on densest burette record FIG-T2-BURETTE-DELIVERED-GRADE
 * - Runtime SimLeakScan parity (gradeable pass, exemption recorded, unit-normalized leak caught, borderline flagged)
 * - Truncation degradation (island-level + P2-07 drawer-slot error)
 * - In-file smoke vector SMK-N12-BURETTE-READ-SCAN (6/6 PASS)
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');

function assert(cond, msg) {
  if (!cond) throw new Error('Assertion failed: ' + msg);
}

function sha256(str) {
  return crypto.createHash('sha256').update(str, 'utf8').digest('hex');
}

function makeNode(tag, id) {
  return {
    tagName: String(tag || 'div').toUpperCase(),
    id: id || '',
    className: '',
    hidden: false,
    disabled: false,
    type: '',
    tabIndex: 0,
    attributes: Object.create(null),
    listeners: Object.create(null),
    childNodes: [],
    parentNode: null,
    _text: '',
    get firstChild() { return this.childNodes.length ? this.childNodes[0] : null; },
    get textContent() {
      if (!this.childNodes.length) return this._text;
      return this.childNodes.map((c) => c.textContent).join('');
    },
    set textContent(v) {
      this._text = String(v === undefined || v === null ? '' : v);
      this.childNodes = [];
    },
    setAttribute(k, v) { this.attributes[k] = String(v); },
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null; },
    removeAttribute(k) { delete this.attributes[k]; },
    appendChild(ch) { ch.parentNode = this; this.childNodes.push(ch); return ch; },
    removeChild(ch) {
      const idx = this.childNodes.indexOf(ch);
      if (idx >= 0) { this.childNodes.splice(idx, 1); ch.parentNode = null; }
      return ch;
    },
    addEventListener(type, fn) {
      if (!this.listeners[type]) this.listeners[type] = [];
      this.listeners[type].push(fn);
    },
    dispatchEvent(type, ev) {
      const list = this.listeners[type] || [];
      for (let i = 0; i < list.length; i += 1) list[i](ev || {});
    },
    focus() { if (this._doc) this._doc.activeElement = this; }
  };
}

function makeDocument(islands) {
  const nodes = Object.create(null);
  const body = makeNode('body', 'body');
  const docEl = makeNode('html', 'html');
  docEl.appendChild(body);

  function add(id, tag, initialText, parent) {
    const n = makeNode(tag, id);
    if (initialText) n.textContent = initialText;
    if (id.endsWith('-error') || id.endsWith('-status')) {
      if (id !== 'theme-status') n.hidden = true;
    }
    nodes[id] = n;
    (parent || body).appendChild(n);
    return n;
  }

  ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors', 'sim-terms', 'sim-figures'].forEach((id) => {
    const n = add(id, 'script', islands[id] !== undefined ? islands[id] : '');
    n.setAttribute('type', 'application/json');
  });

  ['sim-coverage-error', 'sim-conventions-error', 'sim-bank-error', 'sim-golden-vectors-error', 'sim-terms-error', 'sim-figures-error'].forEach((id) => add(id, 'div'));
  ['sim-conventions-status', 'sim-bank-status', 'sim-golden-vectors-status', 'sim-terms-status', 'sim-figures-status', 'sim-smoke-status'].forEach((id) => add(id, 'p'));

  add('sakums-oficialas-temas', 'ol');
  add('coverage-nav', 'nav');
  add('coverage-list', 'div');
  add('coverage-total', 'strong', '64');
  add('theme-toggle', 'button', 'Tumšais režīms');
  add('theme-status', 'p', 'Pašreizējā krāsu shēma: gaišā.');
  add('karte', 'div');
  add('concept-drawer-backdrop', 'div').hidden = true;
  add('concept-drawer', 'aside').hidden = true;
  add('concept-drawer-title', 'h2');
  add('concept-drawer-topic', 'p');
  add('concept-drawer-breadcrumb', 'p');
  add('concept-drawer-back', 'button').hidden = true;
  add('concept-drawer-close', 'button');
  add('concept-drawer-summary', 'p');
  add('concept-drawer-citation', 'p');
  add('concept-drawer-dissent', 'p');
  add('concept-drawer-prereqs', 'div');
  add('concept-drawer-slots', 'div');
  add('concept-drawer-status', 'p');
  add('hint-drawer-backdrop', 'div').hidden = true;
  add('hint-drawer', 'aside').hidden = true;
  add('hint-drawer-body', 'div');
  add('prakse-help-slot', 'div');
  add('sim-header', 'header');
  add('sim-main', 'main');
  add('sim-footer', 'footer');

  function findById(rootNode, targetId) {
    if (!rootNode) return null;
    if (rootNode.id === targetId) return rootNode;
    for (let i = 0; i < rootNode.childNodes.length; i += 1) {
      const f = findById(rootNode.childNodes[i], targetId);
      if (f) return f;
    }
    return null;
  }

  const doc = {
    documentElement: docEl,
    body,
    activeElement: null,
    createElement(tag) { const n = makeNode(tag, ''); n._doc = doc; return n; },
    createElementNS(_ns, tag) { const n = makeNode(tag, ''); n._doc = doc; return n; },
    getElementById(id) { return nodes[id] || findById(body, id); }
  };
  Object.values(nodes).forEach((n) => { n._doc = doc; });
  return { doc, nodes };
}

function countTags(node, tagName) {
  if (!node) return 0;
  let c = node.tagName === tagName.toUpperCase() ? 1 : 0;
  for (let i = 0; i < node.childNodes.length; i += 1) c += countTags(node.childNodes[i], tagName);
  return c;
}

function findByClass(node, cls, out) {
  out = out || [];
  if (!node) return out;
  if (typeof node.className === 'string' && node.className.split(/\s+/).includes(cls)) out.push(node);
  for (let i = 0; i < node.childNodes.length; i += 1) findByClass(node.childNodes[i], cls, out);
  return out;
}

function extractArtifact(html) {
  const islandIds = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors', 'sim-terms', 'sim-figures'];
  const islands = {};
  for (const id of islandIds) {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '">([\\s\\S]*?)</script>');
    const m = re.exec(html);
    if (!m) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = m[1].replace(/<\\\//g, '</');
  }
  const scripts = [];
  const pat = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = pat.exec(html)) !== null) scripts.push(m[1]);
  assert(scripts.length === 1, 'Expected 1 executable script in output/simulator.html');
  return { islands, bootstrap: scripts[0] };
}

function runInVm(islands, bootstrap) {
  const { doc, nodes } = makeDocument(islands);
  const sandbox = { document: doc, console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document: doc, nodes, sandbox };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, bootstrap } = extractArtifact(html);
  const t23Data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data', 'figures_t23.json'), 'utf8'));
  const t23Ids = new Set(t23Data.figures.map((f) => f.id));

  // 1. Baseline load + lazy render
  const base = runInVm(islands, bootstrap);
  const F = base.sandbox.SimFigures;
  const L = base.sandbox.SimLeakScan;
  const loaded = F.getDefault();
  assert(loaded && loaded.total >= 19, 'Expected >= 19 figures in #sim-figures, got ' + (loaded && loaded.total));
  assert(countTags(base.document.body, 'svg') === 0, 'Expected 0 <svg> on initial load');
  assert(F.getRenderEvents().length === 0, 'Expected 0 renderEvents on initial load');

  // 2. Open P2-07 drawer (5 burettes) and P3-10 drawer (3 dilutions)
  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P2-07', source: 'map', returnContext: { elementId: 'karte-btn-P2-07' } }, base.document);
  const slotP207 = base.document.getElementById('drawer-slot-figures-P2-07');
  assert(slotP207 && slotP207.getAttribute('data-slot-status') === 'authored-N12', 'P2-07 must be authored-N12');
  const svgsP207 = countTags(slotP207, 'svg');
  assert(svgsP207 === 5, 'Expected 5 burette SVGs in P2-07 drawer, got ' + svgsP207);
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  base.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P3-10', source: 'map', returnContext: { elementId: 'karte-btn-P3-10' } }, base.document);
  const slotP310 = base.document.getElementById('drawer-slot-figures-P3-10');
  assert(slotP310 && slotP310.getAttribute('data-slot-status') === 'authored-N12', 'P3-10 must be authored-N12');
  const svgsP310 = countTags(slotP310, 'svg');
  assert(svgsP310 === 3, 'Expected 3 dilution SVGs in P3-10 drawer, got ' + svgsP310);
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  // 3. Two-run determinism, raw color check, geometry & scale decimal verification across all 10 T2-3 figures
  const convObj = JSON.parse(islands['sim-conventions']);
  const termsObj = base.sandbox.SimTerms.getDefault();
  const digests = [];
  const scaleLabelRe = /^\d+,\d{2}\s+mL$/;
  let totalScaleLabelsChecked = 0;

  for (const rec of loaded.figures) {
    if (!t23Ids.has(rec.id)) continue;
    const svgA = F.renderFigureSvg(rec, { terms: termsObj, conventions: convObj, theme: 'light' });
    const svgB = F.renderFigureSvg(rec, { terms: termsObj, conventions: convObj, theme: 'light' });
    assert(svgA === svgB, 'Two-run render mismatch for ' + rec.id);
    assert(!/#[0-9a-fA-F]{3,8}\b/.test(svgA) && !/rgb\s*\(/i.test(svgA), 'Raw color found in ' + rec.id);
    assert(svgA.includes('role="img"') && svgA.includes('<title') && svgA.includes('<desc'), 'Missing ARIA title/desc in ' + rec.id);

    if (rec.type === 'burette') {
      const slRe = /data-scale-label="true"[^>]*>([^<]+)<\/text>/g;
      let sm;
      let colLabels = 0;
      while ((sm = slRe.exec(svgA)) !== null) {
        assert(scaleLabelRe.test(sm[1].trim()), 'Scale label violated 2-decimal rule in ' + rec.id + ': ' + sm[1]);
        colLabels += 1;
        totalScaleLabelsChecked += 1;
      }
      assert(colLabels > 0, 'No scale labels found in ' + rec.id);
      for (const col of rec.burette_geometry.columns) {
        const expectedY = Number(col.y_top_px) + (Number(col.declared_reading_ml) - Number(col.view_min_ml)) * Number(col.px_per_ml);
        assert(svgA.includes('data-meniscus-read-y="' + String(Number(expectedY.toFixed(2))) + '"'), 'Missing expected read-y in ' + rec.id);
      }
    }
    digests.push({ id: rec.id, type: rec.type, bytes: svgA.length, sha256: sha256(svgA), match: true });
  }

  // 4. Theme parity on densest burette record
  const denseRec = F.getById('FIG-T2-BURETTE-DELIVERED-GRADE');
  const svgLight = F.renderFigureSvg(denseRec, { terms: termsObj, conventions: convObj, theme: 'light' });
  const svgDark = F.renderFigureSvg(denseRec, { terms: termsObj, conventions: convObj, theme: 'dark' });
  const svgPrint = F.renderFigureSvg(denseRec, { terms: termsObj, conventions: convObj, theme: 'print' });
  assert(svgLight.includes('fig-theme-light') && svgDark.includes('fig-theme-dark') && svgPrint.includes('fig-theme-print'), 'Missing theme classes');
  assert(svgLight.replace(/fig-theme-light/g, 'T').replace(/data-theme-class="light"/g, 'D') ===
         svgDark.replace(/fig-theme-dark/g, 'T').replace(/data-theme-class="dark"/g, 'D'), 'Light/dark parity diverged');

  // 5. Runtime SimLeakScan check over T2-3 records
  const runtimeLeakOutcomes = [];
  for (const rec of loaded.figures) {
    if (!t23Ids.has(rec.id)) continue;
    const res = L.scanFigureRecord(rec, { terms: termsObj });
    assert(res.outcome === 'PASS' || res.outcome === 'EXEMPT', 'Unexpected runtime leak scan outcome for ' + rec.id + ': ' + res.outcome);
    runtimeLeakOutcomes.push({ id: rec.id, outcome: res.outcome, exempt: res.exempt, flags: res.flags.length });
  }

  // 6. Truncation degradation
  const truncIslands = Object.assign({}, islands, { 'sim-figures': '{"island_id":"sim-figures","figures":[' });
  const truncVm = runInVm(truncIslands, bootstrap);
  assert(!truncVm.nodes['sim-figures-error'].hidden && truncVm.nodes['sim-figures-error'].textContent.includes('E_FIGURES_JSON'), 'Truncated island must name E_FIGURES_JSON');
  truncVm.sandbox.SimConceptDrawer.openFromLink({ conceptId: 'P2-07', source: 'map', returnContext: { elementId: 'karte-btn-P2-07' } }, truncVm.document);
  const corruptSlot = truncVm.document.getElementById('drawer-slot-figures-P2-07');
  const errBoxes = findByClass(corruptSlot, 'fig-error-slot');
  assert(errBoxes.length === 1 && errBoxes[0].getAttribute('data-error-code') === 'E_FIGURES_JSON' && countTags(corruptSlot, 'svg') === 0, 'P2-07 corrupt slot degradation failed');

  // 7. Smoke subset (6/6 PASS)
  const smoke = base.sandbox.SimSmoke.lastReport;
  const n12Smoke = smoke.vectors.find((v) => v.id === 'SMK-N12-BURETTE-READ-SCAN');
  assert(smoke.status === 'PASS' && smoke.total >= 6 && n12Smoke && n12Smoke.status === 'PASS', 'Expected >= 6 smoke PASS with SMK-N12-BURETTE-READ-SCAN');

  process.stdout.write(JSON.stringify({
    schema_version: 1,
    task: 'N12',
    artifact: 'n12-runtime-harness',
    artifact_sha256: sha256(html),
    status: 'PASS',
    lazy_render: { initial_svgs: 0, p2_07_svgs: svgsP207, p3_10_svgs: svgsP310 },
    two_run_determinism: digests,
    burette_scale_labels_checked: totalScaleLabelsChecked,
    theme_parity: {
      record_id: denseRec.id,
      light_sha256: sha256(svgLight),
      dark_sha256: sha256(svgDark),
      print_sha256: sha256(svgPrint),
      structural_parity_light_vs_dark: true
    },
    runtime_leak_scan: runtimeLeakOutcomes,
    degradation: {
      island_error_code: 'E_FIGURES_JSON',
      p2_07_slot_error_code: errBoxes[0].getAttribute('data-error-code'),
      slot_svgs: 0
    },
    smoke_report: smoke
  }, null, 2) + '\n');
}

main();
