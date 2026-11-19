#!/usr/bin/env node
/**
 * N11 runtime harness: executes output/simulator.html in a Node VM and verifies:
 * - Lazy-render mechanism: 0 <svg> parsed on load; off-screen deferred slots stay unparsed until viewport/drawer entry
 * - Concept drawer slot closure for T1-2 (P1-01..P1-09, P2-01..P2-06, P2-08..P2-10; P2-07 remains pending-N12)
 * - Two-run pure renderer determinism across all 9 T1-2 records (identical SHA-256 digests, zero raw colors)
 * - Theme parity (light vs dark) and print-theme render (fig-theme-print)
 * - Truncation degradation (island-level #sim-figures-error + slot-level error inside open concept drawer)
 * - In-file smoke vector SMK-N11-FIGURE-FRAMEWORK (5/5 smoke vectors PASS)
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
    createElement(tag) {
      const n = makeNode(tag, '');
      n._doc = doc;
      return n;
    },
    createElementNS(_ns, tag) {
      const n = makeNode(tag, '');
      n._doc = doc;
      return n;
    },
    getElementById(id) { return nodes[id] || findById(body, id); }
  };
  Object.values(nodes).forEach((n) => { n._doc = doc; });
  return { doc, nodes };
}

function countTags(node, tagName) {
  if (!node) return 0;
  let c = node.tagName === tagName.toUpperCase() ? 1 : 0;
  for (let i = 0; i < node.childNodes.length; i += 1) {
    c += countTags(node.childNodes[i], tagName);
  }
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
  const sandbox = {
    document: doc,
    console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean, RegExp
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document: doc, nodes, sandbox };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, bootstrap } = extractArtifact(html);

  // 1. Baseline load + lazy-render initial state (0 <svg> parsed at load)
  const base = runInVm(islands, bootstrap);
  const F = base.sandbox.SimFigures;
  const loaded = F.getDefault();
  assert(loaded && loaded.total >= 9, 'Expected >= 9 figures in #sim-figures, got ' + (loaded && loaded.total));
  assert(!base.nodes['sim-figures-status'].hidden, '#sim-figures-status must be visible');
  const initialSvgCount = countTags(base.document.body, 'svg');
  assert(initialSvgCount === 0, 'Expected 0 <svg> elements parsed on initial load, got ' + initialSvgCount);
  assert(F.getRenderEvents().length === 0, 'Expected 0 renderEvents on initial load');

  // 2. Deferred off-screen slot fixture: remains unparsed until viewport-enter activation
  const offscreenSlot = base.document.createElement('div');
  offscreenSlot.id = 'test-offscreen-slot';
  base.document.body.appendChild(offscreenSlot);
  const deferRes = F.mountSlot(base.document, offscreenSlot, 'P2-08', ['FIG-T2-PLOT-NACL-DENSITY'], { defer: true });
  assert(deferRes.pendingCount === 1 && deferRes.renderedCount === 0, 'Off-screen deferred slot must stay pending');
  assert(countTags(offscreenSlot, 'svg') === 0, 'Off-screen deferred slot must contain 0 <svg> before reveal');
  const card = offscreenSlot.childNodes[0];
  assert(card.getAttribute('data-lazy-state') === 'pending', 'Card must have data-lazy-state=pending');
  const activated = F.activateLazySlot(base.document, card, F.getById('FIG-T2-PLOT-NACL-DENSITY'), { conceptId: 'P2-08', trigger: 'viewport-enter' });
  assert(activated === true, 'activateLazySlot should return true');
  assert(card.getAttribute('data-lazy-state') === 'rendered', 'Card must transition to rendered');
  assert(countTags(offscreenSlot, 'svg') === 1, 'Activated card must contain 1 <svg>');
  const viewportEvent = F.getRenderEvents()[F.getRenderEvents().length - 1];
  assert(viewportEvent && viewportEvent.trigger === 'viewport-enter', 'Expected viewport-enter render event');
  F.clearRenderEvents();
  base.document.body.removeChild(offscreenSlot);

  // 3. Concept drawer slot closure for P1-01 (renders only P1-01 figures on open)
  const triggerP101 = base.document.getElementById('karte-btn-P1-01');
  base.sandbox.SimConceptDrawer.openFromLink({
    conceptId: 'P1-01',
    source: 'map',
    returnContext: { elementId: 'karte-btn-P1-01', triggerEl: triggerP101 }
  }, base.document);
  const slotP101 = base.document.getElementById('drawer-slot-figures-P1-01');
  assert(slotP101 && slotP101.getAttribute('data-slot-status') === 'authored-N11', 'P1-01 figures slot must be authored-N11');
  const svgsInP101 = countTags(slotP101, 'svg');
  assert(svgsInP101 === 3, 'Expected 3 rendered <svg> in P1-01 drawer slot, got ' + svgsInP101);
  assert(F.getRenderEvents().length === 3, 'Expected 3 lazy renderEvents on P1-01 drawer open');

  // P5-01 is now authored-N14 (N14 kinetics figures); P2-07 N12, P4-01 N13
  base.sandbox.SimConceptDrawer.openFromLink({
    conceptId: 'P5-01',
    source: 'map',
    returnContext: { elementId: 'karte-btn-P5-01' }
  }, base.document);
  const slotP501 = base.document.getElementById('drawer-slot-figures-P5-01');
  assert(slotP501 && slotP501.getAttribute('data-slot-status') === 'authored-N14', 'P5-01 must be authored-N14');
  assert(countTags(slotP501, 'svg') === 4, 'Expected 4 T5 figures in P5-01 drawer, got ' + countTags(slotP501, 'svg'));
  base.sandbox.SimConceptDrawer.closeAll(base.document);

  // 4. Two-run renderer determinism over full T1-2 set + raw color scan
  const convObj = JSON.parse(islands['sim-conventions']);
  const termsObj = base.sandbox.SimTerms.getDefault();
  const runDigests = [];
  for (const rec of loaded.figures) {
    const svgA = F.renderFigureSvg(rec, { terms: termsObj, conventions: convObj, theme: 'light' });
    const svgB = F.renderFigureSvg(rec, { terms: termsObj, conventions: convObj, theme: 'light' });
    assert(svgA === svgB, 'Two-run render mismatch for ' + rec.id);
    assert(!/#[0-9a-fA-F]{3,8}\b/.test(svgA) && !/rgb\s*\(/i.test(svgA), 'Raw color found in ' + rec.id);
    assert(svgA.includes('role="img"') && svgA.includes('<title') && svgA.includes('<desc'), 'Missing ARIA title/desc in ' + rec.id);
    runDigests.push({ id: rec.id, type: rec.type, bytes: svgA.length, sha256_run_a: sha256(svgA), sha256_run_b: sha256(svgB), match: true });
  }

  // 5. Theme parity (light vs dark) + print-theme render
  const repRec = F.getById('FIG-T1-COMP-NACL-BASES');
  const svgLight = F.renderFigureSvg(repRec, { terms: termsObj, conventions: convObj, theme: 'light' });
  const svgDark = F.renderFigureSvg(repRec, { terms: termsObj, conventions: convObj, theme: 'dark' });
  const svgPrint = F.renderFigureSvg(repRec, { terms: termsObj, conventions: convObj, theme: 'print' });
  assert(svgLight.includes('fig-theme-light') && svgDark.includes('fig-theme-dark') && svgPrint.includes('fig-theme-print'), 'Theme classes missing');
  assert(svgLight.replace(/fig-theme-light/g, 'T').replace(/data-theme-class="light"/g, 'D') ===
         svgDark.replace(/fig-theme-dark/g, 'T').replace(/data-theme-class="dark"/g, 'D'), 'Light/dark parity structure diverged');

  // 6. Truncation degradation (island-level + drawer-slot level when island is corrupt)
  const truncIslands = Object.assign({}, islands, { 'sim-figures': '{"island_id":"sim-figures","figures":[' });
  const truncVm = runInVm(truncIslands, bootstrap);
  assert(!truncVm.nodes['sim-figures-error'].hidden, '#sim-figures-error must be visible on truncation');
  assert(truncVm.nodes['sim-figures-error'].textContent.includes('E_FIGURES_JSON'), 'Truncated island must name E_FIGURES_JSON');

  // Open P1-01 drawer while #sim-figures is corrupt: drawer must NOT crash and slot must show honest error
  truncVm.sandbox.SimConceptDrawer.openFromLink({
    conceptId: 'P1-01',
    source: 'map',
    returnContext: { elementId: 'karte-btn-P1-01' }
  }, truncVm.document);
  assert(truncVm.sandbox.SimConceptDrawer.getState().isOpen === true, 'Concept drawer must still open when figure island is corrupt');
  const corruptSlot = truncVm.document.getElementById('drawer-slot-figures-P1-01');
  const errBoxes = findByClass(corruptSlot, 'fig-error-slot');
  assert(errBoxes.length === 1 && errBoxes[0].getAttribute('data-error-code') === 'E_FIGURES_JSON', 'Corrupt drawer slot must show E_FIGURES_JSON');
  assert(countTags(corruptSlot, 'svg') === 0, 'Corrupt drawer slot must have 0 half-drawn <svg> elements');

  // 7. In-file smoke vector check
  const smoke = base.sandbox.SimSmoke.lastReport;
  const n11Smoke = smoke.vectors.find((v) => v.id === 'SMK-N11-FIGURE-FRAMEWORK');
  assert(smoke.status === 'PASS' && smoke.total >= 5 && n11Smoke && n11Smoke.status === 'PASS', 'Smoke subset did not pass with SMK-N11-FIGURE-FRAMEWORK');

  const report = {
    schema_version: 1,
    task: 'N11',
    artifact: 'n11-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    status: 'PASS',
    lazy_render: {
      initial_svg_count: initialSvgCount,
      offscreen_pending_before_reveal: true,
      viewport_enter_activated: activated,
      drawer_open_p1_01_svgs: svgsInP101,
      p5_01_slot_status: slotP501.getAttribute('data-slot-status')
    },
    two_run_determinism: runDigests,
    theme_parity: {
      record_id: repRec.id,
      light_sha256: sha256(svgLight),
      dark_sha256: sha256(svgDark),
      print_sha256: sha256(svgPrint),
      structural_parity_light_vs_dark: true
    },
    degradation: {
      island_error_visible: !truncVm.nodes['sim-figures-error'].hidden,
      island_error_text: truncVm.nodes['sim-figures-error'].textContent,
      drawer_still_opens_when_corrupt: true,
      slot_error_code: errBoxes[0].getAttribute('data-error-code'),
      slot_error_text: errBoxes[0].textContent,
      slot_svg_count: 0
    },
    smoke_report: smoke
  };

  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
}

main();
