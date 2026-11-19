#!/usr/bin/env node
/**
 * N10 runtime harness: executes output/simulator.html in a Node VM and verifies:
 * - #sim-terms load, class counts, and fixed lookup vector
 * - Missing-key named error (never silent empty string)
 * - Truncation / empty / missing island degradation (#sim-terms-error + E_TERMS_NOT_LOADED)
 * - IUPAC alternate name pair rendering (masters' form primary, IUPAC secondary)
 * - Single-sourcing across all consuming views in one pass
 * - JS unit-grammar parser & dimension mismatch rejections (including mL/mg vs density)
 * - Full-document rendered term scan + nested-unit check (C.1.1)
 * - Phase III (N11-N15) scratch figure-label contract proof (parse, resolve, render, degrade)
 * - In-file smoke vector SMK-N10-TERMS-GRAMMAR-LOOKUP (4/4 smoke vectors PASS)
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
    focus() {}
  };
}

function makeDocument(islands, termKeyPairs) {
  const nodes = Object.create(null);
  const body = makeNode('body', 'body');
  const docEl = makeNode('html', 'html');
  docEl.appendChild(body);

  function add(id, tag, initialText, termKey, parent) {
    const n = makeNode(tag, id);
    if (initialText) n.textContent = initialText;
    if (termKey) n.setAttribute('data-term-key', termKey);
    if (id.endsWith('-error') || id.endsWith('-status')) {
      if (id !== 'theme-status') n.hidden = true;
    }
    nodes[id] = n;
    (parent || body).appendChild(n);
    return n;
  }

  // Islands
  ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors', 'sim-terms'].forEach((id) => {
    const n = add(id, 'script', islands[id] !== undefined ? islands[id] : '');
    n.setAttribute('type', 'application/json');
  });

  // Errors & statuses
  ['sim-coverage-error', 'sim-conventions-error', 'sim-bank-error', 'sim-golden-vectors-error', 'sim-terms-error'].forEach((id) => add(id, 'div'));
  ['sim-conventions-status', 'sim-bank-status', 'sim-golden-vectors-status', 'sim-terms-status', 'sim-smoke-status'].forEach((id) => add(id, 'p'));

  // Shell elements with data-term-key matching src/shell.html
  const nav = add('sim-nav', 'nav');
  for (const [id, key, txt] of termKeyPairs) {
    const parent = key.startsWith('nav.') ? nav : body;
    add(id, key.startsWith('nav.') ? 'a' : 'div', txt, key, parent);
  }

  // Views & drawers
  add('sakums-oficialas-temas', 'ol');
  add('coverage-nav', 'nav');
  add('coverage-list', 'div');
  add('coverage-total', 'strong', '64');
  add('theme-toggle', 'button', 'Tumšais režīms');
  add('theme-status', 'p', 'Pašreizējā krāsu shēma: gaišā.');
  add('karte', 'div');
  add('concept-drawer-backdrop', 'div').hidden = true;
  add('concept-drawer', 'aside').hidden = true;
  add('concept-drawer-topic', 'p');
  add('concept-drawer-breadcrumb', 'p');
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

  // Index by id dynamically for nodes created by views (e.g. karte-btn-P5-07)
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
    createElement(tag) { return makeNode(tag, ''); },
    getElementById(id) { return nodes[id] || findById(body, id); }
  };
  return { doc, nodes };
}

function extractArtifact(html) {
  const islandIds = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors', 'sim-terms'];
  const islands = {};
  for (const id of islandIds) {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '">([\\s\\S]*?)</script>');
    const m = re.exec(html);
    if (!m) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = m[1].replace(/<\\\//g, '</');
  }
  const termKeyPairs = [];
  const tkRe = /id="([^"]+)"[^>]*data-term-key="([^"]+)"[^>]*>([^<]*)</g;
  let m;
  while ((m = tkRe.exec(html)) !== null) {
    termKeyPairs.push([m[1], m[2], m[3]]);
  }
  // Also catch data-term-key on nav links where href precedes data-term-key without id
  const navRe = /href="#([a-z]+)"[^>]*data-term-key="(nav\.[^"]+)"[^>]*>([^<]*)</g;
  while ((m = navRe.exec(html)) !== null) {
    termKeyPairs.push(['nav-link-' + m[1], m[2], m[3]]);
  }
  const scripts = [];
  const pat = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  while ((m = pat.exec(html)) !== null) scripts.push(m[1]);
  assert(scripts.length === 1, 'Expected 1 executable script in output/simulator.html');
  return { islands, termKeyPairs, bootstrap: scripts[0] };
}

function runInVm(islands, termKeyPairs, bootstrap) {
  const { doc, nodes } = makeDocument(islands, termKeyPairs);
  const sandbox = {
    document: doc,
    console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean, RegExp
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document: doc, nodes, sandbox };
}

function collectTermKeyNodes(node, out) {
  if (!node) return;
  const k = node.getAttribute('data-term-key');
  if (k) out.push({ id: node.id, key: k, text: node.textContent });
  for (let i = 0; i < node.childNodes.length; i += 1) collectTermKeyNodes(node.childNodes[i], out);
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, termKeyPairs, bootstrap } = extractArtifact(html);
  assert(termKeyPairs.length >= 15, 'Expected >=15 data-term-key elements in shell.html, got ' + termKeyPairs.length);

  // 1. Baseline load & counts
  const base = runInVm(islands, termKeyPairs, bootstrap);
  const T = base.sandbox.SimTerms;
  const loaded = T.getDefault();
  const parsedTerms = JSON.parse(islands['sim-terms']);
  assert(loaded && loaded.total === parsedTerms.terms.length && loaded.total >= 174, 'Expected >= 174 entries matching #sim-terms, got ' + (loaded && loaded.total));
  assert(!base.nodes['sim-terms-status'].hidden, '#sim-terms-status should be visible');

  // 2. Missing-key named error (never empty string)
  let missingErr = null;
  try {
    T.lookup('does.not.exist');
  } catch (e) {
    missingErr = { name: e.name, code: e.code, message: e.message };
  }
  assert(missingErr && missingErr.code === 'E_TERMS_MISSING_KEY', 'Missing key did not throw E_TERMS_MISSING_KEY');

  // 3. IUPAC pair path
  const iupacPrimary = T.lookup('iupac.acetic_acid');
  const iupacPair = T.lookup('iupac.acetic_acid', { mode: 'iupac' });
  const iupacThermo = T.lookup('iupac.first_law_sign', { mode: 'iupac' });
  assert(iupacPrimary === 'etiķskābe', 'Primary IUPAC entry must be masters form');
  assert(iupacPair === 'etiķskābe (IUPAC: etānskābe)', 'IUPAC pair rendering mismatch: ' + iupacPair);
  assert(iupacThermo === 'Q = ΔU + A (kursa zīmju konvencija) (IUPAC: ΔU = q + w (IUPAC konvencija, w = −A))', 'Thermo IUPAC pair mismatch');

  // 4. Truncation & empty degradation
  const truncIslands = Object.assign({}, islands, { 'sim-terms': '{"island_id":"sim-terms","terms":[' });
  const truncVm = runInVm(truncIslands, termKeyPairs, bootstrap);
  const truncErrBox = truncVm.nodes['sim-terms-error'];
  assert(!truncErrBox.hidden && truncErrBox.textContent.includes('E_TERMS_JSON') && truncErrBox.textContent.includes('#sim-terms'),
    'Truncated #sim-terms did not display named error');
  let unloadedErr = null;
  try {
    truncVm.sandbox.SimTerms.lookup('nav.sakums');
  } catch (e) {
    unloadedErr = { code: e.code, message: e.message };
  }
  assert(unloadedErr && unloadedErr.code === 'E_TERMS_NOT_LOADED', 'Lookup after truncated load did not throw E_TERMS_NOT_LOADED');

  const emptyIslands = Object.assign({}, islands, { 'sim-terms': '   ' });
  const emptyVm = runInVm(emptyIslands, termKeyPairs, bootstrap);
  assert(!emptyVm.nodes['sim-terms-error'].hidden && emptyVm.nodes['sim-terms-error'].textContent.includes('E_TERMS_EMPTY'),
    'Empty #sim-terms did not display E_TERMS_EMPTY');

  // 5. Single-sourcing across consuming views in one pass
  const editedTerms = JSON.parse(islands['sim-terms']);
  const sentinels = {
    'nav.prakse': 'SENTINELA_PRAKSE_N10',
    'objectives.map_link_short': 'SENTINELA_KARTE_N10',
    'settings.theme.to_dark': 'SENTINELA_TUMSAIS_N10',
    'hint.drawer.close': 'SENTINELA_AIZVERT_N10',
    'hint.practice.help_button': 'SENTINELA_PALIDZIBA_N10'
  };
  for (const entry of editedTerms.terms) {
    if (sentinels[entry.key]) entry.text_lv = sentinels[entry.key];
  }
  const singleVm = runInVm(Object.assign({}, islands, { 'sim-terms': JSON.stringify(editedTerms) }), termKeyPairs, bootstrap);
  const helpBtn = singleVm.sandbox.SimHintDrawer.renderHelpControl(
    singleVm.nodes['prakse-help-slot'],
    { mode: 'practice', familyId: 'FAM-1C', buttonId: 'n10-ss-help-btn' },
    singleVm.document
  );
  const singleSourceResult = {
    nav_updated: singleVm.nodes['nav-link-prakse'].textContent === sentinels['nav.prakse'],
    coverage_view_updated: singleVm.nodes['coverage-list'].textContent.includes(sentinels['objectives.map_link_short']),
    theme_toggle_updated: singleVm.nodes['theme-toggle'].textContent === sentinels['settings.theme.to_dark'],
    hint_drawer_close_updated: singleVm.nodes['hint-drawer-close'].textContent === sentinels['hint.drawer.close'],
    hint_help_btn_updated: Boolean(helpBtn && helpBtn.textContent === sentinels['hint.practice.help_button'])
  };
  assert(Object.values(singleSourceResult).every(Boolean), 'Single-sourcing failed: ' + JSON.stringify(singleSourceResult));

  // 6. JS unit-grammar parse & dimension rejections
  const validUnits = ['g/mol', 'mg/mL', 'J/(mol·K)', 'L/(mol·cm)', '(mol/L)^2', 's^-1', '% (m/V)'];
  const parsedValid = validUnits.map((u) => ({ unit: u, dim: T.parseUnit(u).dimensionVector }));
  const invalidUnits = [
    ['ml', 'E_UNIT_UNKNOWN_ELEMENT'],
    ['J/mol·K', 'E_UNIT_AMBIGUOUS_DENOMINATOR'],
    ['g//mol', 'E_UNIT_MALFORMED_SEPARATOR'],
    ['', 'E_UNIT_EMPTY']
  ];
  const invalidUnitResults = invalidUnits.map(([u, wantCode]) => {
    let gotCode = null;
    try { T.parseUnit(u); } catch (e) { gotCode = e.code; }
    assert(gotCode === wantCode, `Unit ${u}: expected ${wantCode}, got ${gotCode}`);
    return { unit: u, error_code: gotCode };
  });
  let flippedCode = null;
  try { T.checkDimension('mL/mg', 'density'); } catch (e) { flippedCode = e.code; }
  assert(flippedCode === 'E_UNIT_DIMENSION_MISMATCH', 'mL/mg must fail density check');
  let molDensityCode = null;
  try { T.checkDimension('mol/L', 'density'); } catch (e) { molDensityCode = e.code; }
  assert(molDensityCode === 'E_UNIT_DIMENSION_MISMATCH', 'mol/L must fail density check');

  // 7. Full-document rendered term scan + nested unit check (C.1.1)
  const domTermNodes = [];
  collectTermKeyNodes(base.document.body, domTermNodes);
  const dynamicTitleKeys = new Set(['drawer.concept.title', 'drawer.concept.back', 'hint.drawer.title']);
  for (const dn of domTermNodes) {
    const expectedText = T.lookup(dn.key);
    assert(dn.text.length > 0, `DOM key ${dn.key} rendered empty text`);
    if (!dynamicTitleKeys.has(dn.key)) {
      assert(dn.text === expectedText, `DOM key ${dn.key} rendered mismatch: ${dn.text}`);
    }
  }
  // Verify clean-document applyToDocument sets every data-term-key verbatim
  const cleanDocEnv = makeDocument(islands, termKeyPairs);
  const appliedCount = T.applyToDocument(cleanDocEnv.doc, loaded);
  assert(appliedCount === domTermNodes.length, `applyToDocument updated ${appliedCount} != ${domTermNodes.length}`);
  const cleanNodes = [];
  collectTermKeyNodes(cleanDocEnv.doc.body, cleanNodes);
  for (const cn of cleanNodes) {
    assert(cn.text === T.lookup(cn.key), `Clean applyToDocument mismatch on ${cn.key}: ${cn.text}`);
  }
  const nestedChecked = [];
  for (const e of loaded.terms) {
    const nu = T.extractNestedUnits(e.text_lv, e, loaded);
    for (const u of nu) {
      const parsed = e.dimension ? T.checkDimension(u, e.dimension, loaded) : T.parseUnit(u, loaded);
      nestedChecked.push({ key: e.key, text_lv: e.text_lv, extracted_unit: u, dim: parsed.dimensionVector });
    }
  }
  assert(nestedChecked.some((x) => x.key === 'qty.density_with_unit_label' && x.extracted_unit === 'g/mL'),
    'Nested unit check did not inspect qty.density_with_unit_label');
  // Negative nested-unit corner case
  const badNestedEntry = { key: 'qty.bad_nested', class: 'quantities', text_lv: 'šķīduma blīvums ρ (mL/mg)', dimension: 'density' };
  const badNestedExtracted = T.extractNestedUnits(badNestedEntry.text_lv, badNestedEntry, loaded);
  let badNestedCode = null;
  try { T.checkDimension(badNestedExtracted[0], badNestedEntry.dimension, loaded); } catch (e) { badNestedCode = e.code; }
  assert(badNestedCode === 'E_UNIT_DIMENSION_MISMATCH', 'Bad nested unit mL/mg not caught');

  // 8. Scratch Figure-Label Contract Proof (C.1.2) for Phase III (N11-N15)
  const figSpecs = [
    { kind: 'axis', key: 'fig.axis.concentration_mol_l' },
    { kind: 'axis', key: 'qty.density_with_unit_label' },
    { kind: 'axis', key: 'fig.axis.absorbance_a' },
    { kind: 'legend', key: 'fig.legend.catalyzed' },
    { kind: 'annotation', key: 'fig.annot.no_extrapolation' }
  ];
  const figResolved = figSpecs.map((s) => T.resolveFigureLabel(s));
  assert(figResolved[0].text === 'Molārā koncentrācija c (mol/L)', 'Axis label mismatch');
  assert(figResolved[1].text === 'šķīduma blīvums ρ (g/mL)', 'Nested axis label must not duplicate (g/mL)');
  assert(figResolved[3].text === 'Katalizēta reakcija', 'Legend label mismatch');
  assert(figResolved[4].text === 'Ārpus standartu lineārā diapazona ekstrapolācija nav pieļaujama', 'Annotation mismatch');

  const figDegrade = [];
  for (const [label, spec, wantCode] of [
    ['missing_key', { kind: 'axis', key: 'fig.axis.missing' }, 'E_TERMS_MISSING_KEY'],
    ['bad_unit', { kind: 'axis', key: 'fig.axis.time_s', unit: 'J/mol·K' }, 'E_UNIT_AMBIGUOUS_DENOMINATOR'],
    ['dim_mismatch', { kind: 'axis', key: 'qty.density', unit: 'mol/L' }, 'E_UNIT_DIMENSION_MISMATCH']
  ]) {
    let got = null;
    try { T.resolveFigureLabel(spec); } catch (e) { got = e.code; }
    assert(got === wantCode, `Figure degrade ${label}: expected ${wantCode}, got ${got}`);
    figDegrade.push({ case: label, error_code: got });
  }

  // 9. Smoke vector check
  const smokeReport = base.sandbox.SimSmoke.lastReport;
  assert(smokeReport && smokeReport.status === 'PASS' && smokeReport.total >= 4 && smokeReport.passed === smokeReport.total &&
    smokeReport.vectors.some((v) => v.id === 'SMK-N10-TERMS-GRAMMAR-LOOKUP' && v.status === 'PASS'),
    'Expected >=4 smoke vectors PASS with SMK-N10-TERMS-GRAMMAR-LOOKUP, got ' + JSON.stringify(smokeReport));

  const report = {
    schema_version: 1,
    task: 'N10',
    artifact: 'n10-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    status: 'PASS',
    baseline: {
      total_entries: loaded.total,
      counts_by_class: loaded.countsByClass,
      status_visible: !base.nodes['sim-terms-status'].hidden,
      status_text: base.nodes['sim-terms-status'].textContent
    },
    missing_key_error: missingErr,
    iupac_pair_fixture: {
      primary: iupacPrimary,
      on_request_pair: iupacPair,
      thermo_pair: iupacThermo
    },
    degradation: {
      truncated_error_text: truncErrBox.textContent,
      unloaded_lookup_error: unloadedErr,
      empty_error_text: emptyVm.nodes['sim-terms-error'].textContent
    },
    single_sourcing: singleSourceResult,
    unit_grammar: {
      valid_parsed: parsedValid,
      invalid_rejected: invalidUnitResults,
      flipped_ml_per_mg_density: flippedCode,
      mol_per_l_density: molDensityCode
    },
    full_document_scan: {
      dom_term_key_count: domTermNodes.length,
      nested_units_checked: nestedChecked,
      bad_nested_unit_caught: badNestedCode
    },
    figure_label_contract_proof: {
      resolved: figResolved.map((r) => ({ kind: r.kind, key: r.key, unit: r.unit, text: r.text })),
      degraded: figDegrade
    },
    smoke_report: smokeReport
  };

  process.stdout.write(JSON.stringify(report, null, 2) + '\n');
}

main();
