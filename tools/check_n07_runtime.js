#!/usr/bin/env node
/* N07 runtime harness: executes the shipped script from output/simulator.html
 * in a minimal DOM supporting focus, activeElement, Tab/Escape events, and
 * nested drawer walking to prove:
 *  - Layout determinism (2 runs -> identical digest), diamond fixture,
 *    Topic-3 11-node wide-layer wrap fixture, and JS cycle detection
 *  - Semantic check: 64 keyboard-focusable node buttons, 127 named edge links,
 *    20 cross-topic connections, 7 ASCII anchor graphs
 *  - Drawer focus-sequence fixture (invoke -> tab cycle -> close -> restore)
 *  - Nested-drawer restore fixture (inner close restores outer chain link)
 *  - Prerequisite depth cap (DEFAULT_CHAIN_DEPTH=2) + expand toggle
 *  - Direct-link entry with zero map state present (remediation consumer N28)
 *  - Scripted walk trace + two-run parity + --walk-only fresh-process replay
 *  - In-file smoke vector SMK-N07-MAP-DRAWER-WALK PASS
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function canonicalStringify(value) {
  if (Array.isArray(value)) {
    return '[' + value.map((v) => canonicalStringify(v)).join(',') + ']';
  }
  if (value && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalStringify(value[k])).join(',') + '}';
  }
  return JSON.stringify(value);
}

function makeDocument(islands, opts) {
  opts = opts || {};
  const includeMap = opts.includeMap !== false;
  const registryById = Object.create(null);

  const doc = {
    documentElement: null,
    activeElement: null,
    createElement(tag) {
      return new Node(tag);
    },
    getElementById(id) {
      if (registryById[id]) return registryById[id];
      return findById(doc.body, id);
    },
    _nodes: registryById
  };

  function findById(rootNode, id) {
    if (!rootNode) return null;
    if (rootNode.id === id) return rootNode;
    for (let i = 0; i < rootNode.childNodes.length; i += 1) {
      const found = findById(rootNode.childNodes[i], id);
      if (found) return found;
    }
    return null;
  }

  function Node(tagName) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
    this.listeners = Object.create(null);
    this.className = '';
    this._id = '';
    this.hidden = false;
    this.disabled = false;
    this._text = '';
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(val) {
      if (this._id && registryById[this._id] === this) {
        delete registryById[this._id];
      }
      this._id = String(val);
      if (this._id) {
        registryById[this._id] = this;
      }
    }
  });
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() {
      if (this.childNodes.length) {
        return this.childNodes.map((child) => child.textContent).join('');
      }
      return this._text;
    },
    set(value) {
      this.childNodes = [];
      this._text = String(value);
    }
  });
  Node.prototype.appendChild = function (child) {
    child.parentNode = this;
    this.childNodes.push(child);
    if (child.id) registryById[child.id] = child;
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const index = this.childNodes.indexOf(child);
    if (index >= 0) {
      this.childNodes.splice(index, 1);
      child.parentNode = null;
    }
    return child;
  };
  Node.prototype.setAttribute = function (name, value) {
    this.attributes[name] = String(value);
  };
  Node.prototype.getAttribute = function (name) {
    return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
  };
  Node.prototype.removeAttribute = function (name) {
    delete this.attributes[name];
  };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (type, eventObj) {
    const list = this.listeners[type] || [];
    for (let i = 0; i < list.length; i += 1) {
      list[i](eventObj || {});
    }
  };
  Node.prototype.focus = function () {
    doc.activeElement = this;
  };
  Node.prototype.blur = function () {
    if (doc.activeElement === this) {
      doc.activeElement = doc.body;
    }
  };

  doc.documentElement = new Node('html');
  doc.body = new Node('body');
  doc.activeElement = doc.body;

  const spec = [
    ['sim-coverage', 'script'],
    ['sim-conventions', 'script'],
    ['sim-bank', 'script'],
    ['sim-golden-vectors', 'script'],
    ['sim-header', 'header'],
    ['sim-main', 'main'],
    ['sim-footer', 'footer'],
    ['sakums-oficialas-temas', 'ol'],
    ['coverage-nav', 'nav'],
    ['coverage-list', 'div'],
    ['coverage-total', 'strong'],
    ['theme-toggle', 'button'],
    ['theme-status', 'p'],
    ['sim-smoke-status', 'p'],
    ['sim-coverage-error', 'div'],
    ['sim-conventions-error', 'div'],
    ['sim-conventions-status', 'p'],
    ['sim-bank-error', 'div'],
    ['sim-bank-status', 'p'],
    ['sim-golden-vectors-error', 'div'],
    ['sim-golden-vectors-status', 'p'],
    ['concept-drawer-backdrop', 'div'],
    ['concept-drawer', 'aside'],
    ['concept-drawer-topic', 'p'],
    ['concept-drawer-title', 'h2'],
    ['concept-drawer-back', 'button'],
    ['concept-drawer-close', 'button'],
    ['concept-drawer-breadcrumb', 'p'],
    ['concept-drawer-summary', 'p'],
    ['concept-drawer-citation', 'p'],
    ['concept-drawer-dissent', 'p'],
    ['concept-drawer-prereqs', 'div'],
    ['concept-drawer-slots', 'div'],
    ['concept-drawer-status', 'p']
  ];
  if (includeMap) {
    spec.push(['karte', 'div']);
  }

  spec.forEach(([id, tag]) => {
    const node = new Node(tag);
    node.id = id;
    if (id.endsWith('-error') || id.endsWith('-status') ||
        id === 'concept-drawer-backdrop' || id === 'concept-drawer' ||
        id === 'concept-drawer-back' || id === 'concept-drawer-breadcrumb' ||
        id === 'concept-drawer-dissent') {
      if (id !== 'theme-status' && id !== 'concept-drawer-status') {
        node.hidden = true;
      }
    }
    doc.body.appendChild(node);
  });

  // Wire drawer hierarchy so focusables walk cleanly inside #concept-drawer
  const backdrop = registryById['concept-drawer-backdrop'];
  const drawer = registryById['concept-drawer'];
  backdrop.appendChild(drawer);
  [
    'concept-drawer-topic', 'concept-drawer-title', 'concept-drawer-back',
    'concept-drawer-close', 'concept-drawer-breadcrumb', 'concept-drawer-summary',
    'concept-drawer-citation', 'concept-drawer-dissent', 'concept-drawer-prereqs',
    'concept-drawer-slots', 'concept-drawer-status'
  ].forEach((cid) => {
    drawer.appendChild(registryById[cid]);
  });

  Object.keys(islands).forEach((id) => {
    if (registryById[id]) {
      registryById[id].textContent = islands[id];
    }
  });

  return doc;
}

function extractArtifact(html) {
  const islandIds = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors'];
  const islands = {};
  islandIds.forEach((id) => {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '">([\\s\\S]*?)</script>');
    const m = re.exec(html);
    if (!m) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = m[1].replace(/<\\\//g, '</');
  });
  const scripts = [];
  const pattern = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    scripts.push(match[1]);
  }
  if (scripts.length !== 1) {
    throw new Error('Expected 1 executable script in output/simulator.html, found ' + scripts.length);
  }
  return { islands, bootstrap: scripts[0] };
}

function runInVm(islands, bootstrap, opts) {
  const document = makeDocument(islands, opts);
  const sandbox = { document, console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document, sandbox };
}

function collectMatching(node, pred, out) {
  out = out || [];
  if (pred(node)) out.push(node);
  for (let i = 0; i < node.childNodes.length; i += 1) {
    collectMatching(node.childNodes[i], pred, out);
  }
  return out;
}

function runScriptedWalk(env) {
  const doc = env.document;
  const drawer = env.sandbox.SimConceptDrawer;
  drawer.closeAll(doc);
  drawer.clearTrace();

  // 1. Focus & open mid-graph concept P5-07 from map
  const startBtn = doc.getElementById('karte-btn-P5-07');
  startBtn.focus();
  startBtn.dispatchEvent('click');

  // 2. Expand full chain if toggle exists (P5-07 reaches depth 3: P1-03 -> P1-05)
  const toggleBtn = doc.getElementById('concept-drawer-chain-toggle');
  if (toggleBtn) {
    toggleBtn.dispatchEvent('click');
  }

  // 3. Open deepest prerequisite (P1-05 at depth 3)
  const deepBtn = doc.getElementById('drawer-prereq-btn-P1-05');
  deepBtn.dispatchEvent('click');

  // 4. Walk back to outer drawer (P5-07)
  doc.getElementById('concept-drawer-close').dispatchEvent('click');
  const afterBackFocus = doc.activeElement ? doc.activeElement.id : null;

  // 5. Close outer drawer back to map
  doc.getElementById('concept-drawer-close').dispatchEvent('click');
  const afterMapRestoreFocus = doc.activeElement ? doc.activeElement.id : null;

  // 6. Jump to cross-topic edge target (P1-06 -> P3-02) and close
  const crossBtn = doc.getElementById('karte-cross-open-P1-06-P3-02');
  crossBtn.focus();
  crossBtn.dispatchEvent('click');
  doc.getElementById('concept-drawer').dispatchEvent('keydown', {
    key: 'Escape',
    preventDefault: () => {}
  });
  const afterCrossRestoreFocus = doc.activeElement ? doc.activeElement.id : null;

  const trace = drawer.getTrace();
  const payload = {
    trace,
    checkpoints: {
      afterBackFocus,
      afterMapRestoreFocus,
      afterCrossRestoreFocus,
      finalState: drawer.getState()
    }
  };
  return {
    payload,
    digest: sha256(canonicalStringify(payload))
  };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, bootstrap } = extractArtifact(html);
  const env = runInVm(islands, bootstrap);

  if (process.argv.includes('--walk-only')) {
    const walk = runScriptedWalk(env);
    process.stdout.write(JSON.stringify(walk, null, 2) + '\n');
    return;
  }

  const failures = [];
  const checks = {};

  // 1. Layout determinism, diamond fixture, wide-layer fixture, JS cycle check
  const cov = env.sandbox.SimCoverage.load(env.document, env.sandbox.COVERAGE_INVARIANTS);
  const layout1 = env.sandbox.SimConceptMap.computeLayout(cov);
  const layout2 = env.sandbox.SimConceptMap.computeLayout(cov);
  const digest1 = sha256(canonicalStringify(layout1));
  const digest2 = sha256(canonicalStringify(layout2));

  const diamond = env.sandbox.SimConceptMap.computeLayout({
    topics: [{ topic: 1, name_lv: 'Diamond' }],
    outcomes: [
      { id: 'D', topic: 1, statement_lv: 'D', master_anchor: 'd', prerequisites: ['B', 'C'] },
      { id: 'C', topic: 1, statement_lv: 'C', master_anchor: 'c', prerequisites: ['A'] },
      { id: 'B', topic: 1, statement_lv: 'B', master_anchor: 'b', prerequisites: ['A'] },
      { id: 'A', topic: 1, statement_lv: 'A', master_anchor: 'a', prerequisites: [] }
    ]
  });
  const diamondLayers = {
    A: diamond.nodesById.A.layer,
    B: diamond.nodesById.B.layer,
    C: diamond.nodesById.C.layer,
    D: diamond.nodesById.D.layer
  };
  const diamondLayer1Order = diamond.topics[0].layers[1].nodes.map((n) => n.id);

  const wideOutcomes = [];
  for (let i = 1; i <= 11; i += 1) {
    wideOutcomes.push({
      id: 'P3-' + String(i).padStart(2, '0'),
      topic: 3,
      statement_lv: 'Item ' + i,
      master_anchor: 'n5',
      prerequisites: []
    });
  }
  const wideLayout = env.sandbox.SimConceptMap.computeLayout({
    topics: [{ topic: 3, name_lv: 'Wide Topic 3' }],
    outcomes: wideOutcomes
  });
  const wideRowSizes = wideLayout.topics[0].layers[0].rows.map((r) => r.length);

  let cycleErrorCode = null;
  try {
    env.sandbox.SimConceptMap.computeLayout({
      topics: [{ topic: 1, name_lv: 'Cycle' }],
      outcomes: [
        { id: 'A', topic: 1, statement_lv: 'A', master_anchor: 'a', prerequisites: ['B'] },
        { id: 'B', topic: 1, statement_lv: 'B', master_anchor: 'b', prerequisites: ['A'] }
      ]
    });
  } catch (err) {
    cycleErrorCode = err.code || err.name;
  }

  checks.layout = {
    deterministic: digest1 === digest2,
    layout_digest: digest1,
    nodes: layout1.totalNodes,
    edges: layout1.totalEdges,
    cross_topic_edges: layout1.crossTopicEdgeCount,
    diamond_layers: diamondLayers,
    diamond_layer1_order: diamondLayer1Order,
    wide_layer_wrapped: wideLayout.topics[0].layers[0].wrapped,
    wide_layer_row_sizes: wideRowSizes,
    cycle_rejected_code: cycleErrorCode
  };
  if (!checks.layout.deterministic) failures.push('layout computation not deterministic');
  if (JSON.stringify(diamondLayers) !== JSON.stringify({ A: 0, B: 1, C: 1, D: 2 })) failures.push('diamond layers mismatch');
  if (JSON.stringify(diamondLayer1Order) !== JSON.stringify(['B', 'C'])) failures.push('diamond tie-break order mismatch');
  if (!checks.layout.wide_layer_wrapped || JSON.stringify(wideRowSizes) !== JSON.stringify([3, 3, 3, 2])) {
    failures.push('wide layer wrap rule mismatch');
  }
  if (cycleErrorCode !== 'E_MAP_CYCLE') failures.push('JS cycle check did not throw E_MAP_CYCLE');

  // 2. Semantic check on rendered #karte
  const karte = env.document.getElementById('karte');
  const nodeBtns = collectMatching(karte, (n) => n.tagName === 'BUTTON' && n.getAttribute('data-concept-open') && n.id.startsWith('karte-btn-'));
  const edgeLinks = collectMatching(karte, (n) => n.tagName === 'A' && n.getAttribute('data-edge-from') && !n.id.startsWith('karte-edge-'));
  const crossSection = env.document.getElementById('karte-starptemu-saites');
  const crossLinks = collectMatching(crossSection, (n) => n.tagName === 'A' && n.getAttribute('data-edge-kind') === 'cross-topic');
  const allButtonsLabelled = nodeBtns.every((b) => Boolean(b.getAttribute('aria-label')));
  const allEdgesAnnounced = edgeLinks.every((a) => Boolean(a.getAttribute('aria-label')) && a.getAttribute('href').startsWith('#karte-'));
  const asciiGraphs = [1, 2, 3, 4, 5, 6, 7].filter((t) => {
    const pre = env.document.getElementById('karte-ascii-tema-' + t);
    return pre && pre.textContent.includes('ASCII enkuru grafs');
  });

  checks.semantic = {
    node_buttons_count: nodeBtns.length,
    all_buttons_labelled: allButtonsLabelled,
    edge_links_count: edgeLinks.length,
    all_edges_announced: allEdgesAnnounced,
    cross_topic_links_count: crossLinks.length,
    ascii_graphs_count: asciiGraphs.length
  };
  if (nodeBtns.length !== 64 || !allButtonsLabelled) failures.push('semantic node button check failed');
  if (edgeLinks.length !== 127 || !allEdgesAnnounced) failures.push('semantic edge link check failed');
  if (crossLinks.length !== 20) failures.push('expected 20 cross-topic edge links');
  if (asciiGraphs.length !== 7) failures.push('expected 7 ASCII anchor graphs');

  // 3. Focus-sequence fixture & Tab cycling
  const focusSeq = [];
  const p101Btn = env.document.getElementById('karte-btn-P1-01');
  p101Btn.focus();
  focusSeq.push({ step: 'invoke', activeId: env.document.activeElement.id });
  p101Btn.dispatchEvent('click');
  focusSeq.push({ step: 'opened', activeId: env.document.activeElement.id });

  const focusables = env.sandbox.SimConceptDrawer.getFocusableInsideDrawer(env.document);
  const lastFocusable = focusables[focusables.length - 1];
  lastFocusable.focus();
  let tabPrevented = false;
  env.document.getElementById('concept-drawer').dispatchEvent('keydown', {
    key: 'Tab',
    shiftKey: false,
    preventDefault: () => { tabPrevented = true; }
  });
  focusSeq.push({ step: 'tab-wrap-forward', activeId: env.document.activeElement.id, prevented: tabPrevented });

  env.document.getElementById('concept-drawer-close').dispatchEvent('click');
  focusSeq.push({ step: 'closed-restore', activeId: env.document.activeElement.id });

  checks.focus_sequence = focusSeq;
  if (focusSeq[1].activeId !== 'concept-drawer-close' || !tabPrevented ||
      focusSeq[2].activeId !== focusables[0].id || focusSeq[3].activeId !== 'karte-btn-P1-01') {
    failures.push('focus-sequence fixture failed');
  }

  // 4. Nested-drawer restore fixture
  const nestedSeq = [];
  p101Btn.focus();
  p101Btn.dispatchEvent('click');
  nestedSeq.push({ step: 'outer-open', concept: env.sandbox.SimConceptDrawer.getState().activeConceptId, activeId: env.document.activeElement.id });
  const innerTrigger = env.document.getElementById('drawer-prereq-btn-P1-03');
  innerTrigger.focus();
  innerTrigger.dispatchEvent('click');
  nestedSeq.push({ step: 'inner-open', concept: env.sandbox.SimConceptDrawer.getState().activeConceptId, stackDepth: env.sandbox.SimConceptDrawer.getState().stackDepth, activeId: env.document.activeElement.id });
  env.document.getElementById('concept-drawer-close').dispatchEvent('click');
  nestedSeq.push({ step: 'inner-close-restore', concept: env.sandbox.SimConceptDrawer.getState().activeConceptId, stackDepth: env.sandbox.SimConceptDrawer.getState().stackDepth, activeId: env.document.activeElement.id });
  env.document.getElementById('concept-drawer-close').dispatchEvent('click');
  nestedSeq.push({ step: 'outer-close-restore', isOpen: env.sandbox.SimConceptDrawer.getState().isOpen, activeId: env.document.activeElement.id });

  checks.nested_restore = nestedSeq;
  if (nestedSeq[1].stackDepth !== 2 || nestedSeq[2].activeId !== 'drawer-prereq-btn-P1-03' ||
      nestedSeq[3].isOpen || nestedSeq[3].activeId !== 'karte-btn-P1-01') {
    failures.push('nested-drawer restore fixture failed');
  }

  // 5. Direct-link entry with NO map state present (fresh VM with includeMap=false)
  const noMapEnv = runInVm(islands, bootstrap, { includeMap: false });
  const remBtn = noMapEnv.document.createElement('button');
  remBtn.id = 'rem-link-P4-10';
  noMapEnv.document.body.appendChild(remBtn);
  remBtn.focus();
  noMapEnv.sandbox.SimConceptDrawer.openFromLink({
    conceptId: 'P4-10',
    source: 'N28',
    returnContext: { elementId: 'rem-link-P4-10', triggerEl: remBtn }
  }, noMapEnv.document);
  const directOpenedTitle = noMapEnv.document.getElementById('concept-drawer-title').textContent;
  const directCitation = noMapEnv.document.getElementById('concept-drawer-citation').textContent;
  noMapEnv.document.getElementById('concept-drawer-close').dispatchEvent('click');
  const directRestoredId = noMapEnv.document.activeElement ? noMapEnv.document.activeElement.id : null;

  checks.direct_link_no_map = {
    map_element_exists: Boolean(noMapEnv.document.getElementById('karte')),
    opened_title: directOpenedTitle,
    citation_has_ch7: directCitation.includes('#ch7'),
    restored_focus_id: directRestoredId
  };
  if (checks.direct_link_no_map.map_element_exists || !directOpenedTitle.startsWith('P4-10') ||
      !checks.direct_link_no_map.citation_has_ch7 || directRestoredId !== 'rem-link-P4-10') {
    failures.push('direct-link no-map entry fixture failed');
  }

  // 6. Scripted walk trace (two runs in process)
  const walkA = runScriptedWalk(env);
  const walkB = runScriptedWalk(env);
  checks.walk_trace = {
    run_a_digest: walkA.digest,
    run_b_digest: walkB.digest,
    identical: walkA.digest === walkB.digest,
    events_count: walkA.payload.trace.length,
    checkpoints: walkA.payload.checkpoints,
    trace: walkA.payload.trace
  };
  if (!checks.walk_trace.identical) failures.push('scripted walk trace not deterministic across two runs');

  // 7. In-file smoke vector check
  const smokeReport = env.sandbox.SimSmoke.run(env.document, { coverage: cov, expected: env.sandbox.COVERAGE_INVARIANTS });
  const n07Vec = (smokeReport.vectors || []).find((v) => v.id === 'SMK-N07-MAP-DRAWER-WALK');
  checks.smoke_vector = n07Vec || null;
  if (!n07Vec || n07Vec.status !== 'PASS') {
    failures.push('in-file smoke vector SMK-N07-MAP-DRAWER-WALK failed');
  }

  const report = {
    schema_version: 1,
    task: 'N07',
    artifact: 'n07-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks,
    failures
  };

  if (process.argv.includes('--json')) {
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');
  } else {
    process.stdout.write(report.status + ' n07-runtime\n');
    process.stdout.write('  layout: ' + checks.layout.nodes + ' nodes, ' + checks.layout.edges + ' edges (' + checks.layout.cross_topic_edges + ' cross), digest=' + checks.layout.layout_digest.slice(0, 16) + '...\n');
    process.stdout.write('  diamond: ' + JSON.stringify(diamondLayers) + ', wide-wrap: ' + JSON.stringify(wideRowSizes) + ', cycle: ' + cycleErrorCode + '\n');
    process.stdout.write('  semantic: ' + nodeBtns.length + ' node buttons, ' + edgeLinks.length + ' edge links, ' + asciiGraphs.length + ' ASCII graphs\n');
    process.stdout.write('  nested restore: ' + nestedSeq[2].activeId + ' -> ' + nestedSeq[3].activeId + '\n');
    process.stdout.write('  direct-link no-map: ' + checks.direct_link_no_map.restored_focus_id + '\n');
    process.stdout.write('  walk digest: ' + walkA.digest.slice(0, 16) + '... (' + walkA.payload.trace.length + ' events, parity=' + checks.walk_trace.identical + ')\n');
    process.stdout.write('  smoke: ' + (n07Vec ? n07Vec.status + ' (' + n07Vec.id + ')' : 'MISSING') + '\n');
    for (const f of failures) process.stdout.write('  - ' + f + '\n');
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
