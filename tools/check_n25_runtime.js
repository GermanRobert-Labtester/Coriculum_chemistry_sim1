#!/usr/bin/env node
/* N25 runtime, storage contract, analytics chain, and privacy audit harness.
 *
 * Exercises:
 *   - A.1.1: Canonical serialization, round-trip, and two-page-load parity
 *   - A.1.2: Opt-in boundary (default 0 localStorage keys; opt-in exact schema key set; Latvian consent copy)
 *   - A.1.3: Export (parses, matches store digest) and two-step erase (0 residue, UI emptied)
 *   - A.1:   v1 -> v2 migration and newer-version ignore+write-lock guard
 *   - B.1.1: Pure event chain over N23 FX-N23-MIXED fixture (digest-linked, 0 answer text)
 *   - B.1:   Bounded log (cap 200, oldest-first prune) and unblended honesty
 *   - B.1.2: 64-outcome tracking over #sim-coverage + honest zero state
 *   - B.1.3: Remediation queue lifecycle (enter on incorrect/invalid, resolve via N28 flow, round-trip)
 *   - C.1.1: Full-session privacy audit (localStorage access log, 0 outlier keys, 0 network attempts, rogue-key catch)
 *   - C.1.2: F10 boundary enforcement (no chart/streak/scoreHistory exports)
 *   - Built-artifact check: output/simulator.html boots cleanly and runs 21/21 smoke vectors
 *
 * Usage:
 *   node tools/check_n25_runtime.js [--repo-root .] [--record PATH] [--privacy-out PATH]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

function parseArgs(argv) {
  const args = {
    repoRoot: path.resolve(__dirname, '..'),
    record: null,
    privacyOut: null,
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--privacy-out') { args.privacyOut = argv[i + 1]; i += 1; }
  }
  return args;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function sha256(text) {
  return crypto.createHash('sha256').update(String(text), 'utf8').digest('hex');
}

function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return String(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.filter((k) => value[k] !== undefined).map((k) => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
}

function makeClock(startMs) {
  let current = startMs || 0;
  return {
    now() { return current; },
    advance(ms) { current += ms; return current; }
  };
}

function captureError(fn) {
  try { fn(); return null; } catch (e) { return { code: e && e.code ? e.code : null, message: e && e.message ? e.message : String(e) }; }
}

function makeDom(islands) {
  const registry = Object.create(null);
  function Node(tagName, id) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
    this.listeners = Object.create(null);
    this.className = '';
    this._id = '';
    this.hidden = false;
    this.disabled = false;
    this.type = '';
    this.value = '';
    this.checked = false;
    this.tabIndex = 0;
    this._text = '';
    if (id) { this.id = id; }
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(v) {
      if (this._id && registry[this._id] === this) { delete registry[this._id]; }
      this._id = String(v);
      if (this._id) { registry[this._id] = this; }
    }
  });
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() { return this.childNodes.length ? this.childNodes.map((c) => c.textContent).join('') : this._text; },
    set(v) { this.childNodes = []; this._text = String(v); }
  });
  Node.prototype.appendChild = function (c) { c.parentNode = this; this.childNodes.push(c); if (c.id) registry[c.id] = c; return c; };
  Node.prototype.removeChild = function (c) { const i = this.childNodes.indexOf(c); if (i >= 0) { this.childNodes.splice(i, 1); c.parentNode = null; } return c; };
  Node.prototype.setAttribute = function (k, v) { this.attributes[k] = String(v); if (k === 'id') this.id = v; };
  Node.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null; };
  Node.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
  Node.prototype.addEventListener = function (t, fn) { if (!this.listeners[t]) this.listeners[t] = []; this.listeners[t].push(fn); };
  Node.prototype.dispatchEvent = function (t, ev) {
    const list = this.listeners[t] || [];
    for (let i = 0; i < list.length; i += 1) { list[i](ev || { type: t }); }
    return true;
  };
  Node.prototype.click = function () { this.dispatchEvent('click', { type: 'click' }); };
  Node.prototype.focus = function () { doc.activeElement = this; };
  Node.prototype.blur = function () {};

  const doc = {
    documentElement: new Node('html'),
    body: new Node('body'),
    activeElement: null,
    createElement(tag) { return new Node(tag); },
    createElementNS(_ns, tag) { return new Node(tag); },
    getElementById(id) { return registry[id] || null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
  };

  const ids = [
    ['theme-toggle', 'button'], ['theme-status', 'p'],
    ['atskats', 'section'], ['atskats-honesty-note', 'p'], ['atskats-storage-notice', 'p'],
    ['atskats-zero-notice', 'p'], ['atskats-sessions-count', 'p'], ['atskats-outcomes-correct', 'p'],
    ['atskats-outcomes-first-pass', 'p'], ['atskats-remediation-count', 'p'],
    ['atskats-topics-table', 'table'], ['atskats-topics-body', 'tbody'],
    ['atskats-forms-list', 'ul'], ['atskats-remediation-list', 'ul'], ['atskats-outcomes-list', 'ul'],
    ['settings-storage-slot', 'div'], ['store-consent-copy', 'p'], ['store-opt-in-toggle', 'button'],
    ['store-status', 'p'], ['store-notice', 'p'], ['store-export-btn', 'button'], ['store-export-status', 'p'],
    ['store-erase-request', 'button'], ['store-erase-confirm-box', 'div'], ['store-erase-prompt', 'p'],
    ['store-erase-confirm', 'button'], ['store-erase-cancel', 'button'],
    ['eksamens', 'section'], ['sim-exam-status', 'p'], ['exam-entry', 'div'], ['exam-entry-note', 'p'],
    ['exam-start', 'button'], ['exam-shell', 'div'], ['exam-timer-bar', 'div'], ['exam-timer-value', 'span'],
    ['exam-timer-label', 'p'], ['exam-timer-threshold', 'p'], ['exam-timer-expired', 'p'],
    ['exam-navigator', 'div'], ['exam-prev', 'button'], ['exam-next', 'button'], ['exam-flag', 'button'],
    ['exam-slot-status', 'p'], ['exam-review-button', 'button'], ['exam-map', 'div'],
    ['exam-slot-host', 'div'], ['exam-review', 'section'],
    ['sakums-oficialas-temas', 'ol'], ['coverage-nav', 'nav'], ['coverage-list', 'div'], ['coverage-total', 'strong'],
    ['sim-smoke-status', 'p'], ['sim-coverage-error', 'div'], ['sim-conventions-error', 'div'],
    ['sim-bank-error', 'div'], ['sim-golden-vectors-error', 'div'], ['sim-terms-error', 'div'],
    ['sim-figures-error', 'div'], ['sim-chains-error', 'div'],
  ];
  for (const [id, tag] of ids) {
    const n = new Node(tag, id);
    if (id === 'exam-shell' || id === 'store-notice' || id === 'store-export-status' || id === 'store-erase-confirm-box') {
      n.hidden = true;
    }
    doc.body.appendChild(n);
  }
  for (const [id, text] of Object.entries(islands || {})) {
    const s = new Node('script', id);
    s.setAttribute('type', 'application/json');
    s.textContent = typeof text === 'string' ? text : JSON.stringify(text);
    doc.body.appendChild(s);
  }
  return doc;
}

function createInstrumentedEnv(backingMap, options) {
  const opts = options || {};
  const accessLog = [];
  const networkLog = [];
  let seq = 0;
  let phase = 'init';

  function setPhase(p) { phase = p; }

  const storage = {
    getItem(key) {
      seq += 1;
      const val = Object.prototype.hasOwnProperty.call(backingMap, key) ? backingMap[key] : null;
      accessLog.push({ seq, phase, operation: 'getItem', key: String(key), hit: val !== null, bytes: val ? val.length : 0 });
      return val;
    },
    setItem(key, value) {
      seq += 1;
      const str = String(value);
      accessLog.push({ seq, phase, operation: 'setItem', key: String(key), bytes: str.length, _value: str });
      backingMap[key] = str;
    },
    removeItem(key) {
      seq += 1;
      accessLog.push({ seq, phase, operation: 'removeItem', key: String(key), bytes: 0 });
      delete backingMap[key];
    },
    clear() {
      seq += 1;
      accessLog.push({ seq, phase, operation: 'clear', key: '*', bytes: 0 });
      Object.keys(backingMap).forEach((k) => delete backingMap[k]);
    },
    key(index) {
      const keys = Object.keys(backingMap);
      const k = keys[index] || null;
      seq += 1;
      accessLog.push({ seq, phase, operation: 'key', key: k, bytes: 0 });
      return k;
    },
    get length() {
      return Object.keys(backingMap).length;
    }
  };

  function recordNet(api, target) {
    networkLog.push({ phase, api, target: String(target || '') });
    throw new Error('Offline invariant violated: ' + api + ' attempted');
  }

  return {
    storage,
    accessLog,
    networkLog,
    setPhase,
    networkTraps: {
      fetch: (url) => recordNet('fetch', url),
      XMLHttpRequest: function () { recordNet('XMLHttpRequest', 'open'); },
      WebSocket: function (url) { recordNet('WebSocket', url); },
      navigator: { sendBeacon: (url) => recordNet('navigator.sendBeacon', url) }
    }
  };
}

function buildIslands(repoRoot) {
  const islands = {};
  islands['sim-coverage'] = readJson(path.join(repoRoot, 'data/coverage.json'));
  islands['sim-conventions'] = readJson(path.join(repoRoot, 'data/conventions.json'));
  islands['sim-terms'] = readJson(path.join(repoRoot, 'data/terms.json'));
  islands['sim-engines'] = readJson(path.join(repoRoot, 'data/engine_taxonomy.json'));
  islands['sim-graph-scoring'] = readJson(path.join(repoRoot, 'data/graph_scoring_contract.json'));
  islands['sim-method-engine'] = readJson(path.join(repoRoot, 'data/method_engine_contract.json'));
  islands['sim-method-cards'] = readJson(path.join(repoRoot, 'data/method_cards.json'));
  islands['sim-exam-policy'] = readJson(path.join(repoRoot, 'data/exam_policy.json'));
  islands['sim-chains'] = readJson(path.join(repoRoot, 'data/chains.json'));
  islands['sim-response-types'] = readJson(path.join(repoRoot, 'data/response_types.json'));
  islands['sim-grading-policy'] = readJson(path.join(repoRoot, 'data/grading_policy.json'));
  islands['sim-feedback-classification'] = readJson(path.join(repoRoot, 'data/feedback_classification.json'));
  islands['sim-analytics'] = readJson(path.join(repoRoot, 'data/analytics_schema.json'));
  const figures = { island_id: 'sim-figures', figures: [] };
  ['data/figures_t12.json', 'data/figures_t23.json', 'data/figures_t4.json', 'data/figures_t5.json', 'data/figures_t67.json'].forEach((rel) => {
    const src = readJson(path.join(repoRoot, rel));
    (src.figures || []).forEach((f) => figures.figures.push(f));
  });
  islands['sim-figures'] = figures;
  return islands;
}

function loadRawBankById(repoRoot) {
  const bankDir = path.join(repoRoot, 'data/bank');
  const byId = Object.create(null);
  for (const name of fs.readdirSync(bankDir).sort()) {
    if (!name.endsWith('.json')) { continue; }
    const doc = readJson(path.join(bankDir, name));
    for (const q of (doc.questions || [])) {
      if (q && q.question_id) { byId[q.question_id] = q; }
    }
  }
  return byId;
}

function loadSandbox(repoRoot, env) {
  const sandbox = {
    console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
    encodeURIComponent, decodeURIComponent, unescape,
    performance: { now: () => 0 },
    localStorage: env ? env.storage : undefined,
    fetch: env ? env.networkTraps.fetch : undefined,
    XMLHttpRequest: env ? env.networkTraps.XMLHttpRequest : undefined,
    WebSocket: env ? env.networkTraps.WebSocket : undefined,
    navigator: env ? env.networkTraps.navigator : undefined,
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  const files = [
    'src/coverage-loader.js',
    'src/conventions-loader.js',
    'src/terms-loader.js',
    'src/figure-framework.js',
    'src/quantity-engine.js',
    'src/method-engine.js',
    'src/graph-scoring-engine.js',
    'src/theme-toggle.js',
    'src/compiled/session.js',
    'src/compiled/exam.js',
    'src/compiled/inputs/registry.js',
    'src/compiled/inputs/components.js',
    'src/compiled/inputs/integration.js',
    'src/compiled/grading.js',
    'src/compiled/feedback.js',
    'src/compiled/store.js',
    'src/compiled/analytics.js',
  ];
  for (const rel of files) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sandbox, { filename: rel });
  }
  return sandbox;
}

function buildGradedMixedForm(repoRoot, sb, islands) {
  const matrix = readJson(path.join(repoRoot, 'tools/fixtures/n23_score_matrix.json'));
  const mixed = matrix.forms.find((f) => f.form_id === 'FX-N23-MIXED');
  const bankById = loadRawBankById(repoRoot);
  const doc = makeDom(islands);
  sb.document = doc;
  sb.SimEngines.load(doc);
  const policy = islands['sim-exam-policy'];

  sb.SimInputsRegistry.load(islands['sim-response-types'], islands['sim-terms']);
  const methodEngine = new sb.SimMethodEngine.MethodEngine(
    islands['sim-method-engine'],
    islands['sim-terms']
  );
  const method = Object.create(methodEngine);
  method.MethodEngine = sb.SimMethodEngine.MethodEngine;
  method.specForVector = sb.SimMethodEngine.specForVector;
  method.sha256 = sb.SimMethodEngine.sha256;
  sb.SimGraphScoring.load(doc);

  const termsMap = Object.create(null);
  (islands['sim-terms'].terms || []).forEach((e) => {
    if (e && typeof e.key === 'string') { termsMap[e.key] = e.text_lv; }
  });

  const context = {
    doc,
    quantity: sb.SimEngines,
    method: method,
    graph: sb.SimGraphScoring,
    inputsRegistry: sb.SimInputsRegistry,
    inputsIntegration: sb.SimInputsIntegration,
    figures: sb.SimGraphScoring.state.figures,
    terms: termsMap,
    examPolicy: policy,
    bank: { instancesById: bankById },
    bindingSource: 'tools/fixtures/n23_score_matrix.json#FX-N23-MIXED',
    oracle: {
      oracle_version: 'n23-score-matrix/v' + String(matrix.schema_version || 1),
      oracle_digest: sha256(canonical(matrix)),
      conventions_digest: sha256(canonical(islands['sim-conventions'])),
    },
  };

  const clock = makeClock(0);
  const session = new sb.SimSession.ExamSession({
    policy,
    form: { form_id: mixed.form_id, slots: policy.slots },
    sessionId: 'SES-FX-N23-MIXED-0',
    clock,
  });
  session.dispatch('start');
  const rawPayloads = {};
  const answersMap = mixed.answers || {};
  (mixed.bindings || []).forEach((binding) => {
    const slotId = binding.slot_id;
    const ans = Object.prototype.hasOwnProperty.call(answersMap, slotId) ? answersMap[slotId] : null;
    if (!ans) { return; }
    let payload;
    if (ans.stored_payload && typeof ans.stored_payload.kind === 'string') {
      payload = JSON.parse(JSON.stringify(ans.stored_payload));
    } else if (ans.payload && typeof ans.payload.kind === 'string') {
      payload = JSON.parse(JSON.stringify(ans.payload));
    } else if (typeof ans.kind === 'string') {
      payload = JSON.parse(JSON.stringify(ans));
    } else {
      const capture = ans.capture !== undefined ? ans.capture : ans;
      const contract = sb.SimInputsRegistry.contractFor(binding.type_id);
      const instance = bankById[binding.instance_id];
      payload = JSON.parse(JSON.stringify(sb.SimInputsIntegration.buildPayload(binding.type_id, contract, instance, capture)));
    }
    session.dispatch('answer', { slot_id: slotId, payload });
    rawPayloads[slotId] = payload;
  });
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });
  const terminal = session.toTerminalRecord();

  const bindings = (mixed.bindings || []).map((b) => ({
    slot_id: b.slot_id,
    type_id: b.type_id,
    instance_id: b.instance_id,
    instance: bankById[b.instance_id],
  }));
  const core = sb.SimGrading.gradeTerminalRecord(terminal, bindings, context);
  const fb = sb.SimFeedback.assemble(core, context);
  const full = sb.SimGrading.composeGradedRecord(core, fb);
  return { mixed, terminal, full, rawPayloads, doc };
}

function main() {
  const args = parseArgs(process.argv);
  const repoRoot = args.repoRoot;
  const islands = buildIslands(repoRoot);
  const results = {};
  const failures = [];

  function check(id, ok, detail) {
    results[id] = { status: ok ? 'PASS' : 'FAIL', detail: detail || null };
    if (!ok) { failures.push(id + ': ' + JSON.stringify(detail)); }
  }

  /* ---------------------------------------------- A.1.1 Round-trip & 2 loads */
  {
    const backing = Object.create(null);
    const env1 = createInstrumentedEnv(backing);
    const sb1 = loadSandbox(repoRoot, env1);
    const { full } = buildGradedMixedForm(repoRoot, sb1, islands);
    const doc1 = makeDom(islands);
    const app1 = sb1.SimAnalytics.init(doc1, { storage: env1.storage, coverage: islands['sim-coverage'], probeExisting: false });
    app1.store.setOptIn(true, env1.storage);
    app1.ingestGradedRecord(full);
    app1.store.setTheme('dark');
    const digest1 = app1.store.getDigest();
    const rawWritten = backing[sb1.SimStore.SCHEMA_KEY];

    // Reload in a completely fresh VM
    const env2 = createInstrumentedEnv(backing);
    const sb2 = loadSandbox(repoRoot, env2);
    const doc2 = makeDom(islands);
    const app2 = sb2.SimAnalytics.init(doc2, { storage: env2.storage, coverage: islands['sim-coverage'], probeExisting: true });
    const digest2 = app2.store.getDigest();
    const shaMatchesCrypto = digest1 === sha256(sb1.SimStore.canonicalText(app1.store.getState()));
    check('a11_canonical_roundtrip_and_reload',
      digest1 === digest2 && shaMatchesCrypto && canonical(app1.store.getState()) === canonical(app2.store.getState()) && Boolean(rawWritten),
      { digest1, digest2, shaMatchesCrypto, stored_bytes: rawWritten ? rawWritten.length : 0 });
  }

  /* ------------------------------------------ A.1.2 Opt-in boundary & copy */
  {
    const backing = Object.create(null);
    const env = createInstrumentedEnv(backing);
    const sb = loadSandbox(repoRoot, env);
    const { full } = buildGradedMixedForm(repoRoot, sb, islands);
    const doc = makeDom(islands);
    env.setPhase('default-memory-session');
    const app = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: islands['sim-coverage'], probeExisting: false });
    app.ingestGradedRecord(full);
    doc.getElementById('theme-toggle').click();
    const keysBeforeOptIn = Object.keys(backing);
    const accessesBeforeOptIn = env.accessLog.length;

    env.setPhase('explicit-opt-in');
    doc.getElementById('store-opt-in-toggle').click();
    const keysAfterOptIn = Object.keys(backing);
    const consentText = doc.getElementById('store-consent-copy').textContent;
    const hasConsentElements = consentText.includes('Kas tiek saglabāts') &&
      consentText.includes('Nekas neatstāj ierīci') &&
      consentText.includes('Kā dzēst') &&
      consentText.includes('localStorage');

    check('a12_opt_in_boundary_and_consent',
      keysBeforeOptIn.length === 0 && accessesBeforeOptIn === 0 &&
      keysAfterOptIn.length === 1 && keysAfterOptIn[0] === 'sim_colloq1_store_v2' &&
      hasConsentElements,
      { keysBeforeOptIn, accessesBeforeOptIn, keysAfterOptIn, hasConsentElements });
  }

  /* ------------------------------------ A.1.3 Export & Two-step Erase */
  {
    const backing = Object.create(null);
    const env = createInstrumentedEnv(backing);
    const sb = loadSandbox(repoRoot, env);
    const { full } = buildGradedMixedForm(repoRoot, sb, islands);
    const doc = makeDom(islands);
    const app = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: islands['sim-coverage'], probeExisting: false });
    app.store.setOptIn(true, env.storage);
    app.ingestGradedRecord(full);
    app.refresh();

    const exported = app.store.exportProgress();
    const parsedExport = JSON.parse(exported.text);
    const exportMatchesDigest = parsedExport.store_digest === app.store.getDigest() &&
      sb.SimStore.digestValue(parsedExport.store) === parsedExport.store_digest;

    const unconfirmedErr = captureError(() => app.store.erase(false));
    const confirmWithoutReqErr = captureError(() => app.store.confirmErase());

    doc.getElementById('store-erase-request').click();
    const confirmBoxVisibleAfterStep1 = doc.getElementById('store-erase-confirm-box').hidden === false;
    doc.getElementById('store-erase-confirm').click();
    const keysAfterErase = Object.keys(backing);
    const uiResetZero = doc.getElementById('atskats-sessions-count').textContent === '0' &&
      doc.getElementById('atskats-remediation-count').textContent === '0' &&
      doc.getElementById('store-opt-in-toggle').getAttribute('aria-pressed') === 'false';

    check('a13_export_and_twostep_erase',
      exported.filename === 'kimija-kolokvijs1-progress-v2.json' &&
      exportMatchesDigest &&
      unconfirmedErr && unconfirmedErr.code === 'E_STORE_ERASE_CONFIRMATION_REQUIRED' &&
      confirmWithoutReqErr && confirmWithoutReqErr.code === 'E_STORE_ERASE_CONFIRMATION_REQUIRED' &&
      confirmBoxVisibleAfterStep1 &&
      keysAfterErase.length === 0 &&
      uiResetZero,
      { filename: exported.filename, exportMatchesDigest, confirmBoxVisibleAfterStep1, keysAfterErase, uiResetZero });
  }

  /* ------------------------------------ A.1 Migration v1->v2 & Newer-ignore */
  {
    const backingV1 = Object.create(null);
    backingV1['sim_colloq1_store_v2'] = JSON.stringify({
      schema_version: 1,
      opt_in: true,
      theme: 'dark',
      practiced_topics: [1, 3],
      correct_outcomes: ['P1-01', 'P3-02'],
      forms: [{ form_id: 'A', session_id: 'SES-V1', auto_score: 40, auto_max: 48, pending_points: 20, pending_max: 52, pending_count: 4, elapsed_ms: 1000, graded_digest: 'abc' }],
      remediation: [{ slot_id: 'S4-1', topic: 4, family_id: 'FAM-4A', instance_id: 'COL1-4-4A-A-01', concept_ids: ['P4-01'], chain_ids: ['EX07'], signature_id: 'MC-4A-01', graded_digest: 'abc', state: 'open' }],
      events: [{ event: 'session-completed', form_id: 'A', graded_digest: 'abc' }]
    });
    const envV1 = createInstrumentedEnv(backingV1);
    const sbV1 = loadSandbox(repoRoot, envV1);
    const docV1 = makeDom(islands);
    const appV1 = sbV1.SimAnalytics.init(docV1, { storage: envV1.storage, coverage: islands['sim-coverage'], probeExisting: true });
    const stV1 = appV1.store.getState();
    const migratedOk = stV1.schema_version === 2 &&
      stV1.settings.theme === 'dark' &&
      stV1.progress.outcomes_correct_once.join(',') === 'P1-01,P3-02' &&
      stV1.progress.form_history[0].auto_points === 40 &&
      stV1.progress.form_history[0].pending_external_points === 20 &&
      stV1.remediation_queue.length === 1 &&
      appV1.store.getNotice().code === 'MIGRATED_V1_TO_V2';

    const newerSentinel = JSON.stringify({ schema_version: 99, future_payload: 'do-not-overwrite' });
    const backingNewer = { sim_colloq1_store_v2: newerSentinel };
    const envNewer = createInstrumentedEnv(backingNewer);
    const sbNewer = loadSandbox(repoRoot, envNewer);
    const docNewer = makeDom(islands);
    const appNewer = sbNewer.SimAnalytics.init(docNewer, { storage: envNewer.storage, coverage: islands['sim-coverage'], probeExisting: true });
    const writeBlockedErr = captureError(() => appNewer.store.setOptIn(true, envNewer.storage));
    const newerNotice = appNewer.store.getNotice();
    const newerPreserved = backingNewer.sim_colloq1_store_v2 === newerSentinel &&
      appNewer.store.isNewerVersionLocked() === true &&
      docNewer.getElementById('store-notice').hidden === false &&
      docNewer.getElementById('store-notice').textContent.includes('99');

    check('a1_migration_and_newer_guard',
      migratedOk && newerPreserved && newerNotice && newerNotice.code === 'NEWER_VERSION_IGNORED' &&
      writeBlockedErr && writeBlockedErr.code === 'E_STORE_WRITE_BLOCKED_NEWER_VERSION',
      { migratedOk, newerPreserved, newerNotice, writeBlockedCode: writeBlockedErr && writeBlockedErr.code });
  }

  /* ------------------------------------ B.1.1 Chain mapping, B.1 Bounded & Honesty, B.1.2 Outcomes, B.1.3 Remediation */
  {
    const backing = Object.create(null);
    const env = createInstrumentedEnv(backing);
    const sb = loadSandbox(repoRoot, env);
    const { full, rawPayloads } = buildGradedMixedForm(repoRoot, sb, islands);
    const expectedFromN23 = sb.SimGrading.toAnalyticsEvents(full);
    const extractedByN25 = sb.SimAnalytics.extractEvents(full);
    const chainParity = canonical(expectedFromN23) === canonical(extractedByN25);
    const allDigestLinked = extractedByN25.every((ev) => ev.graded_digest === full.digest);

    // Zero answer text in events
    const rawStrings = [];
    (function walk(v) {
      if (typeof v === 'string' && v.length >= 4) { rawStrings.push(v); }
      else if (Array.isArray(v)) { v.forEach(walk); }
      else if (v && typeof v === 'object') { Object.keys(v).forEach((k) => walk(v[k])); }
    })(rawPayloads);
    const eventsCanonical = canonical(extractedByN25);
    const vocab = new Set(['correct', 'incorrect', 'awarded', 'denied', 'pending']);
    const leaked = rawStrings.filter((s) => !vocab.has(s) && eventsCanonical.includes(s));

    // Bounded log cap=200
    const capStore = sb.SimStore.createStore({ optIn: false });
    const bulkEvents = [];
    for (let i = 1; i <= 215; i += 1) {
      bulkEvents.push({ event: 'task-answered', seq_marker: i, graded_digest: full.digest });
    }
    const afterBulk = sb.SimAnalytics.appendEvents(capStore, bulkEvents);
    const boundedOk = afterBulk.events.length === 200 &&
      afterBulk.events_pruned_count === 15 &&
      afterBulk.events[0].seq_marker === 16 &&
      afterBulk.events[199].seq_marker === 215;

    // Fresh zero-state honesty, then ingest mixed form, then resolve remediation
    const doc = makeDom(islands);
    const app = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: islands['sim-coverage'], probeExisting: false });
    const zeroSummary = sb.SimAnalytics.buildProgressSummary(app.store.getState(), islands['sim-coverage']);
    const zeroHonest = zeroSummary.outcomes_total === 64 &&
      zeroSummary.outcomes_correct_once_count === 0 &&
      zeroSummary.topics.every((t) => t.zero_activity === true && t.practiced_tasks === 0) &&
      doc.getElementById('atskats-zero-notice').hidden === false;

    app.store.setOptIn(true, env.storage);
    app.ingestGradedRecord(full);
    const afterIngest = sb.SimAnalytics.buildProgressSummary(app.store.getState(), islands['sim-coverage']);
    const formsLi = doc.getElementById('atskats-forms-list').childNodes[0];
    const unblendedDisplayOk = formsLi && formsLi.getAttribute('data-unblended') === 'true' &&
      formsLi.textContent.includes('18/48') && formsLi.textContent.includes('37/52') &&
      formsLi.textContent.includes('13 vietas') && !formsLi.textContent.includes('55/100');

    // Remediation lifecycle: 5 open -> resolve 2 -> 3 open -> reload -> 3 open
    const openBefore = afterIngest.open_remediation_count;
    const firstTwo = afterIngest.open_remediation.slice(0, 2);
    app.resolveRemediationItem(firstTwo[0].id);
    app.resolveRemediationItem(firstTwo[1].id);
    const openAfterResolve = doc.getElementById('atskats-remediation-count').textContent;

    const envReload = createInstrumentedEnv(backing);
    const sbReload = loadSandbox(repoRoot, envReload);
    const docReload = makeDom(islands);
    const appReload = sbReload.SimAnalytics.init(docReload, { storage: envReload.storage, coverage: islands['sim-coverage'], probeExisting: true });
    const openAfterReload = docReload.getElementById('atskats-remediation-count').textContent;

    check('b11_chain_and_no_answer_text', chainParity && allDigestLinked && leaked.length === 0,
      { event_count: extractedByN25.length, chainParity, allDigestLinked, leaked });
    check('b1_bounded_log_and_honesty', boundedOk && zeroHonest && unblendedDisplayOk,
      { boundedOk, events_len: afterBulk.events.length, pruned: afterBulk.events_pruned_count, zeroHonest, unblendedDisplayOk });
    check('b12_outcomes_tracking', afterIngest.outcomes_correct_once_count > 0 && afterIngest.outcomes_first_pass_count > 0,
      { correct_once: afterIngest.outcomes_correct_once_count, first_pass: afterIngest.outcomes_first_pass_count });
    check('b13_remediation_lifecycle',
      openBefore === 5 && openAfterResolve === '3' && openAfterReload === '3',
      { openBefore, openAfterResolve, openAfterReload });
  }

  /* ------------------------------------ C.1 & C.1.1 Full-session privacy audit & outlier catch */
  let privacyAuditReport = null;
  {
    const backing = Object.create(null);
    const env = createInstrumentedEnv(backing);
    const sb = loadSandbox(repoRoot, env);
    const doc = makeDom(islands);

    env.setPhase('boot-and-practice-browse');
    sb.SimTheme.init(doc);
    const cov = sb.SimCoverage.load(doc);
    const conv = sb.SimConventions.load(doc);
    const app = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: cov, probeExisting: false });

    env.setPhase('exam-and-grade-in-memory');
    const { full, rawPayloads } = buildGradedMixedForm(repoRoot, sb, islands);
    app.ingestGradedRecord(full);
    doc.getElementById('theme-toggle').click();
    const keysDuringMemoryPhase = Object.keys(backing);
    const writesDuringMemoryPhase = env.accessLog.filter((e) => e.operation === 'setItem').length;

    env.setPhase('opt-in-and-persist');
    doc.getElementById('store-opt-in-toggle').click();
    app.resolveRemediationItem('S4-1::COL1-2-2C-C-01');
    doc.getElementById('theme-toggle').click();

    env.setPhase('export-and-erase');
    const exported = app.store.exportProgress();
    doc.getElementById('store-erase-request').click();
    doc.getElementById('store-erase-confirm').click();

    const allowedKeys = new Set(sb.SimStore.SCHEMA_KEYS.concat(['sim_colloq1_store_v1']));
    const outliers = env.accessLog.filter((e) => !allowedKeys.has(e.key));

    // Check zero answer text in any logged setItem payload
    const rawStrings = [];
    (function walkRaw(v, keyName) {
      if (keyName === 'kind') { return; }
      if (typeof v === 'string' && v.length >= 4) { rawStrings.push(v); }
      else if (Array.isArray(v)) { v.forEach((item) => walkRaw(item, '')); }
      else if (v && typeof v === 'object') { Object.keys(v).forEach((k) => walkRaw(v[k], k)); }
    })(rawPayloads, '');
    const vocab = new Set(['correct', 'incorrect', 'awarded', 'denied', 'pending', 'method', 'numeric', 'ordering', 'matching', 'option_select', 'graph_draw', 'graph_read', 'raw_text']);
    const persistedValues = [];
    env.accessLog.filter((e) => e.operation === 'setItem' && e._value).forEach((e) => {
      try {
        const parsedVal = JSON.parse(e._value);
        (function walkVal(v) {
          if (typeof v === 'string') { persistedValues.push(v); }
          else if (Array.isArray(v)) { v.forEach(walkVal); }
          else if (v && typeof v === 'object') { Object.keys(v).forEach((k) => walkVal(v[k])); }
        })(parsedVal);
      } catch (_err) {
        persistedValues.push(String(e._value));
      }
    });
    const persistedText = persistedValues.join('\n');
    const leakedAnswerStrings = rawStrings.filter((s) => !vocab.has(s) && persistedValues.some((pv) => pv === s || (s.length >= 6 && pv.includes(s))));
    const cleanAccessLog = env.accessLog.map((e) => ({ seq: e.seq, phase: e.phase, operation: e.operation, key: e.key, bytes: e.bytes }));
    const storedAfterErase = Object.keys(backing);

    // Negative outlier test: catch a rogue cache key
    const rogueLogEnv = createInstrumentedEnv(Object.create(null));
    rogueLogEnv.setPhase('rogue-module');
    rogueLogEnv.storage.setItem('sim_render_cache', '{"cached":true}');
    const caughtOutliers = rogueLogEnv.accessLog.filter((e) => !allowedKeys.has(e.key)).map((e) => e.key);

    // F10 boundary check
    const bannedExports = sb.SimAnalytics.F10_BOUNDARY.forbidden_exports.filter((k) =>
      Object.prototype.hasOwnProperty.call(sb.SimAnalytics, k) || Object.prototype.hasOwnProperty.call(sb.SimStore, k)
    );

    privacyAuditReport = {
      schema_version: 1,
      task: 'N25',
      status: (keysDuringMemoryPhase.length === 0 && writesDuringMemoryPhase === 0 &&
               outliers.length === 0 && env.networkLog.length === 0 &&
               storedAfterErase.length === 0 && caughtOutliers.includes('sim_render_cache') &&
               bannedExports.length === 0 && leakedAnswerStrings.length === 0 &&
               conv !== null && Boolean(exported.text))
        ? 'PASS' : 'FAIL',
      schema_keys: sb.SimStore.SCHEMA_KEYS,
      keys_during_memory_phase: keysDuringMemoryPhase,
      writes_during_memory_phase: writesDuringMemoryPhase,
      outlier_keys: outliers,
      leaked_answer_strings: leakedAnswerStrings,
      network_attempts_count: env.networkLog.length,
      network_attempts: env.networkLog,
      keys_after_erase: storedAfterErase,
      rogue_outlier_caught: caughtOutliers,
      f10_boundary: sb.SimAnalytics.F10_BOUNDARY,
      f10_banned_exports_found: bannedExports,
      access_log_count: cleanAccessLog.length,
      access_log: cleanAccessLog,
    };

    check('c1_privacy_audit_full_session', privacyAuditReport.status === 'PASS', {
      writesDuringMemoryPhase,
      outlier_keys: outliers.length,
      leaked_answer_strings: leakedAnswerStrings,
      network_attempts: env.networkLog.length,
      keys_after_erase: storedAfterErase.length,
      caughtOutliers,
      bannedExports,
      rawPayloadCount: Object.keys(rawPayloads).length,
      persistedLen: persistedText.length,
    });
  }

  /* ------------------------------------ Built-artifact smoke check */
  const artifactPath = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(artifactPath)) {
    const html = fs.readFileSync(artifactPath, 'utf8');
    const islandIds = [
      'sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms', 'sim-golden-vectors',
      'sim-terms', 'sim-analytics', 'sim-figures', 'sim-chains', 'sim-engines',
      'sim-graph-scoring', 'sim-method-cards', 'sim-method-engine', 'sim-exam-policy',
      'sim-response-types', 'sim-grading-policy', 'sim-feedback-classification'
    ];
    const parsedIslands = {};
    islandIds.forEach((id) => {
      const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)</script>');
      const m = re.exec(html);
      if (m) { parsedIslands[id] = m[1].replace(/<\\\//g, '</'); }
    });
    const scriptMatches = [...html.matchAll(/<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g)];
    const bootstrap = scriptMatches.length ? scriptMatches[0][1] : '';
    const artDoc = makeDom(parsedIslands);
    const artEnv = createInstrumentedEnv(Object.create(null));
    const artSb = {
      document: artDoc,
      console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
      encodeURIComponent, decodeURIComponent, unescape,
      performance: { now: () => 0 },
      localStorage: artEnv.storage,
      fetch: artEnv.networkTraps.fetch,
      XMLHttpRequest: artEnv.networkTraps.XMLHttpRequest,
      WebSocket: artEnv.networkTraps.WebSocket,
      navigator: artEnv.networkTraps.navigator,
    };
    artSb.globalThis = artSb;
    artSb.window = artSb;
    vm.createContext(artSb);
    vm.runInContext(bootstrap, artSb, { filename: 'output/simulator.html#inline' });
    const smoke = artSb.SimSmoke.lastReport;
    const n25Vec = smoke && smoke.vectors ? smoke.vectors.find((v) => v.id === 'SMK-N25-STORE-ROUNDTRIP') : null;
    check('c13_built_artifact_smoke',
      Boolean(smoke && smoke.status === 'PASS' && n25Vec && n25Vec.status === 'PASS' && artEnv.networkLog.length === 0 && Object.keys(artEnv.storage).length >= 0),
      { total: smoke ? smoke.total : 0, passed: smoke ? smoke.passed : 0, n25Vec });
  } else {
    check('c13_built_artifact_smoke', false, { reason: 'output/simulator.html missing' });
  }

  const report = {
    schema_version: 1,
    task: 'N25',
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks: results,
    failures,
  };

  if (args.record) {
    const outPath = path.isAbsolute(args.record) ? args.record : path.join(repoRoot, args.record);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }
  if (args.privacyOut && privacyAuditReport) {
    const pPath = path.isAbsolute(args.privacyOut) ? args.privacyOut : path.join(repoRoot, args.privacyOut);
    fs.mkdirSync(path.dirname(pPath), { recursive: true });
    fs.writeFileSync(pPath, JSON.stringify(privacyAuditReport, null, 2) + '\n', 'utf8');
  }

  console.log('N25 runtime: ' + report.status + ' (' + Object.keys(results).length + ' checks, ' + failures.length + ' failures)');
  for (const f of failures) {
    console.error('  FAIL:', f);
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
