#!/usr/bin/env node
/* N28 runtime harness: remediation queue coalescing & no-rewind, policy-driven
 * resolution (confirm_required vs one_correct_resolves), 4-variant cyclic retry
 * + N20 ephemeral fallback, end-to-end classification loop trace, nullable-chain
 * corner case, on-read dangling-link failure, bounded-path discipline, fresh-
 * process replay determinism, opt-in store round-trip + erase privacy audit,
 * and built-artifact smoke check.
 *
 * Usage:
 *   node tools/check_n28_runtime.js [--repo-root .] [--record PATH] [--trace-out PATH] [--privacy-out PATH]
 *   node tools/check_n28_runtime.js --replay-only --repo-root .
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

function parseArgs(argv) {
  const args = {
    repoRoot: path.resolve(__dirname, '..'),
    record: null,
    traceOut: null,
    privacyOut: null,
    replayOnly: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--trace-out') { args.traceOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--privacy-out') { args.privacyOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--replay-only') { args.replayOnly = true; }
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
    documentElement: new Node('html', ''),
    body: new Node('body', ''),
    activeElement: null,
    createElement(tag) { return new Node(tag, ''); },
    createElementNS(_ns, tag) { return new Node(tag, ''); },
    getElementById(id) { return registry[id] || null; },
    querySelector() { return null; },
    querySelectorAll(sel) {
      const m = /^\.([A-Za-z0-9_-]+)$/.exec(sel);
      if (!m) { return []; }
      const cls = m[1];
      const out = [];
      function walk(node) {
        if (node.className && node.className.split(/\s+/).indexOf(cls) >= 0) { out.push(node); }
        for (let i = 0; i < node.childNodes.length; i += 1) { walk(node.childNodes[i]); }
      }
      walk(doc.body);
      return out;
    },
  };

  const ids = [
    ['sim-header', 'header'], ['sim-main', 'main'], ['sim-footer', 'footer'],
    ['theme-toggle', 'button'], ['theme-status', 'p'],
    ['atskats', 'section'], ['atskats-honesty-note', 'p'], ['atskats-storage-notice', 'p'],
    ['atskats-zero-notice', 'p'], ['atskats-sessions-count', 'p'], ['atskats-outcomes-correct', 'p'],
    ['atskats-outcomes-first-pass', 'p'], ['atskats-remediation-count', 'p'],
    ['atskats-topics-table', 'table'], ['atskats-topics-body', 'tbody'],
    ['atskats-forms-list', 'ul'], ['atskats-remediation-wrap', 'div'],
    ['atskats-remediation-heading', 'h3'], ['atskats-remediation-honesty', 'p'],
    ['sim-remediation-error', 'p'], ['atskats-remediation-status', 'p'],
    ['atskats-remediation-list', 'ul'], ['atskats-remediation-chain-host', 'div'],
    ['atskats-remediation-retry-host', 'div'], ['atskats-remediation-resolved-details', 'details'],
    ['atskats-remediation-resolved-summary', 'summary'], ['atskats-remediation-resolved-list', 'ul'],
    ['atskats-mastery-wrap', 'div'], ['atskats-mastery-summary', 'div'], ['atskats-mastery-topics', 'div'],
    ['atskats-mastery-fresh-note', 'p'], ['atskats-outcomes-list', 'ul'],
    ['prakse', 'section'], ['prakse-mastery-topics', 'div'],
    ['settings-storage-slot', 'div'], ['store-consent-copy', 'p'], ['store-opt-in-toggle', 'button'],
    ['store-status', 'p'], ['store-notice', 'p'], ['store-export-btn', 'button'], ['store-export-status', 'p'],
    ['store-erase-request', 'button'], ['store-erase-confirm-box', 'div'], ['store-erase-prompt', 'p'],
    ['store-erase-confirm', 'button'], ['store-erase-cancel', 'button'],
    ['concept-drawer-backdrop', 'div'], ['concept-drawer', 'aside'], ['concept-drawer-title', 'h2'],
    ['concept-drawer-topic', 'p'], ['concept-drawer-breadcrumb', 'p'], ['concept-drawer-back', 'button'],
    ['concept-drawer-close', 'button'], ['concept-drawer-summary', 'p'], ['concept-drawer-citation', 'p'],
    ['concept-drawer-dissent', 'p'], ['concept-drawer-prereqs', 'div'], ['concept-drawer-slots', 'div'],
    ['concept-drawer-status', 'p'],
    ['chain-index', 'div'], ['sim-chains-error', 'p'],
    ['sim-mastery-error', 'p'], ['sim-smoke-status', 'p'],
  ];
  ids.forEach(([id, tag]) => {
    const n = new Node(tag, id);
    doc.body.appendChild(n);
  });

  Object.keys(islands || {}).forEach((id) => {
    const n = new Node('script', id);
    n.setAttribute('type', 'application/json');
    n.textContent = typeof islands[id] === 'string' ? islands[id] : JSON.stringify(islands[id]);
    doc.body.appendChild(n);
  });

  return doc;
}

function buildIslands(repoRoot) {
  const bankQuestions = [];
  const bankDir = path.join(repoRoot, 'data/bank');
  fs.readdirSync(bankDir).sort().forEach((fn) => {
    if (!fn.endsWith('.json')) { return; }
    const data = readJson(path.join(bankDir, fn));
    const qs = Array.isArray(data) ? data : (data.questions || data.instances || []);
    qs.forEach((q) => bankQuestions.push(q));
  });
  const familyTemplates = {};
  const ftDir = path.join(repoRoot, 'data/family_templates');
  fs.readdirSync(ftDir).sort().forEach((fn) => {
    if (!fn.endsWith('.json')) { return; }
    const data = readJson(path.join(ftDir, fn));
    const fams = Array.isArray(data) ? data : (data.families || []);
    fams.forEach((f) => { familyTemplates[f.family_id] = f; });
  });
  const figures = [];
  ['figures_t12.json', 'figures_t23.json', 'figures_t4.json', 'figures_t5.json', 'figures_t67.json'].forEach((fn) => {
    const p = path.join(repoRoot, 'data', fn);
    if (fs.existsSync(p)) {
      const d = readJson(p);
      (d.figures || []).forEach((f) => figures.push(f));
    }
  });
  return {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-conventions': readJson(path.join(repoRoot, 'data/conventions.json')),
    'sim-bank': { island_id: 'sim-bank', questions: bankQuestions },
    'sim-terms': readJson(path.join(repoRoot, 'data/terms.json')),
    'sim-chains': readJson(path.join(repoRoot, 'data/chains.json')),
    'sim-figures': { island_id: 'sim-figures', figures },
    'sim-method-cards': readJson(path.join(repoRoot, 'data/method_cards.json')),
    'sim-method-engine': readJson(path.join(repoRoot, 'data/method_engine_contract.json')),
    'sim-analytics': readJson(path.join(repoRoot, 'data/analytics_schema.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
    'sim-remediation-policy': readJson(path.join(repoRoot, 'data/remediation_policy.json')),
    'sim-family-templates': { island_id: 'sim-family-templates', families: familyTemplates },
    __conceptSummaries: readJson(path.join(repoRoot, 'data/concept_summaries.json')),
    __anchorRegistry: readJson(path.join(repoRoot, 'data/anchor_registry.json')),
  };
}

function createInstrumentedEnv(backing) {
  const accessLog = [];
  const networkLog = [];
  let seq = 0;
  let phase = 'init';
  const storage = {
    getItem(k) {
      seq += 1;
      const val = Object.prototype.hasOwnProperty.call(backing, k) ? backing[k] : null;
      accessLog.push({ seq, phase, operation: 'getItem', key: String(k), bytes: val ? Buffer.byteLength(String(val), 'utf8') : 0 });
      return val;
    },
    setItem(k, v) {
      seq += 1;
      const s = String(v);
      backing[String(k)] = s;
      accessLog.push({ seq, phase, operation: 'setItem', key: String(k), bytes: Buffer.byteLength(s, 'utf8'), _value: s });
    },
    removeItem(k) {
      seq += 1;
      delete backing[String(k)];
      accessLog.push({ seq, phase, operation: 'removeItem', key: String(k), bytes: 0 });
    },
  };
  const trap = (name) => () => { networkLog.push({ phase, api: name }); throw new Error('Network disabled'); };
  return {
    storage, accessLog, networkLog,
    setPhase(p) { phase = p; },
    networkTraps: {
      fetch: trap('fetch'),
      XMLHttpRequest: function () { trap('XMLHttpRequest')(); },
      WebSocket: function () { trap('WebSocket')(); },
      navigator: { sendBeacon: trap('sendBeacon') },
    },
  };
}

function loadSandbox(repoRoot, env, islands) {
  const sandbox = {
    console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
    encodeURIComponent, decodeURIComponent, unescape, atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    TextDecoder, Uint8Array,
    performance: { now: () => 0 },
    localStorage: env ? env.storage : null,
    fetch: env ? env.networkTraps.fetch : undefined,
    XMLHttpRequest: env ? env.networkTraps.XMLHttpRequest : undefined,
    WebSocket: env ? env.networkTraps.WebSocket : undefined,
    navigator: env ? env.networkTraps.navigator : undefined,
    CONCEPT_DRAWER_DATA: islands ? islands.__conceptSummaries : null,
    ANCHOR_REGISTRY: islands ? islands.__anchorRegistry : null,
    COVERAGE_INVARIANTS: { total: 64, perTopic: { '1': 9, '2': 10, '3': 11, '4': 11, '5': 10, '6': 8, '7': 5 } },
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  const files = [
    'src/coverage-loader.js',
    'src/conventions-loader.js',
    'src/terms-loader.js',
    'src/prng.js',
    'src/figure-framework.js',
    'src/concept-drawer.js',
    'src/chain-view.js',
    'src/variant-templates.js',
    'src/variant-engine.js',
    'src/compiled/store.js',
    'src/compiled/mastery.js',
    'src/compiled/analytics.js',
    'src/compiled/remediation.js',
  ];
  for (const rel of files) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sandbox, { filename: rel });
  }
  return sandbox;
}

function makeGradedRecord(sb, params) {
  const rec = {
    record_kind: 'graded-record',
    session: { form_id: params.form_id || 'PRACTICE', session_id: params.session_id || 'SES-1', elapsed_ms: 12000 },
    totals: {
      auto_points: params.correct ? 2 : (params.partial ? 1 : 0),
      auto_max_points: 2,
      pending_external_points: 0,
      pending_max_points: 0,
    },
    slots: [{
      slot_id: params.slot_id || 'S1',
      topic: params.topic,
      family_id: params.family_id,
      type_id: params.type_id || 'Q07',
      instance_id: params.instance_id,
      outcome_ids: params.outcome_ids,
      state: 'graded',
      verdict_class: params.correct ? 'correct' : (params.partial ? 'partial' : 'incorrect'),
      criteria: [{
        criterion_id: 'C1',
        status: params.correct ? 'awarded' : 'denied',
        verdict_class: params.correct ? 'correct' : 'incorrect',
        error_class: params.correct ? null : 'concept_error',
      }],
      task: {
        auto_points: params.correct ? 2 : (params.partial ? 1 : 0),
        auto_max_points: 2,
        pending_points: 0,
      },
    }],
    feedback: params.feedback_items ? { items: params.feedback_items } : { items: [] },
  };
  rec.digest = sb.SimStore.digestOf(rec);
  return rec;
}

function runLoopTrace(repoRoot, islands) {
  const backing = Object.create(null);
  const env = createInstrumentedEnv(backing);
  const sb = loadSandbox(repoRoot, env, islands);
  const doc = makeDom(islands);
  sb.document = doc;
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  sb.SimConceptDrawer.init(doc, { coverage: cov, summaries: islands.__conceptSummaries, registry: islands.__anchorRegistry });
  sb.SimChains.init(doc);
  sb.SimVariantEngine.load(sb.SimFamilyTemplates, islands['sim-conventions']);

  const analyticsApp = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: cov, probeExisting: false });
  const masteryApp = sb.SimMastery.init(doc, { coverage: cov, bank: islands['sim-bank'], store: analyticsApp.store });
  const pathState = { remaining: 3, limit: 3, used: 0, exhausted: false };
  const remApp = sb.SimRemediation.init(doc, {
    coverage: cov,
    bank: islands['sim-bank'],
    chains: islands['sim-chains'],
    store: analyticsApp.store,
    practicePath: pathState,
  });

  const steps = [];
  function snapStep(stepName, extra) {
    const snap = remApp.getSnapshot();
    const domCount = doc.getElementById('atskats-remediation-count').textContent;
    const domRows = doc.getElementById('atskats-remediation-list').childNodes.filter((n) => n.className.includes('remediation-item'));
    const mState = analyticsApp.store.getState().mastery ? analyticsApp.store.getState().mastery.outcomes['P6-01'].state : 'unseen';
    const rec = {
      seq: steps.length + 1,
      step: stepName,
      active_count: snap.active_count,
      open_count: snap.open_count,
      retried_count: snap.retried_count,
      resolved_count: snap.resolved_count,
      dom_remediation_count: domCount,
      dom_active_rows: domRows.length,
      p6_01_mastery_state: mState,
      queue_digest: snap.digest,
      extra: extra || null,
    };
    rec.step_digest = sha256(canonical(rec));
    steps.push(rec);
    return rec;
  }

  // Step 1: Scripted miss on classification task Q07 (FAM-6A, COL1-6-6A-A-01)
  const missRec = makeGradedRecord(sb, {
    session_id: 'SES-LOOP-1',
    slot_id: 'S6-1',
    topic: 6,
    family_id: 'FAM-6A',
    type_id: 'Q07',
    instance_id: 'COL1-6-6A-A-01',
    outcome_ids: ['P6-01', 'P6-02', 'P6-04'],
    correct: false,
    feedback_items: [{
      slot_id: 'S6-1',
      signature_id: 'MC-6A-01',
      remediation: { concept_ids: ['P6-01', 'P6-02', 'P6-04'], chain_ids: ['EX12'] },
    }],
  });
  const missDigestBefore = missRec.digest;
  analyticsApp.ingestGradedRecord(missRec);
  remApp.refresh();
  const missDigestAfter = sb.SimStore.digestOf(missRec);
  const entryId = remApp.getSnapshot().active_entries[0].id;
  const domSlug = entryId.replace(/[^A-Za-z0-9_-]+/g, '-');
  snapStep('1_miss_classification_q07', {
    entry_id: entryId,
    instance_id: 'COL1-6-6A-A-01',
    original_digest_preserved: missDigestBefore === missDigestAfter,
  });

  // Step 2: Anchor open (N07 concept drawer opened at P6-01)
  doc.getElementById('rem-anchor-btn-' + domSlug).click();
  const drawerOpenState = sb.SimConceptDrawer.getState();
  const drawerTrace = sb.SimConceptDrawer.getTrace();
  sb.SimConceptDrawer.close(doc, { quiet: true });
  const drawerClosedState = sb.SimConceptDrawer.getState();
  snapStep('2_anchor_open_and_return', {
    drawer_open: drawerOpenState.isOpen,
    drawer_concept_id: drawerOpenState.activeConceptId,
    drawer_source: drawerOpenState.activeSource,
    drawer_closed_after_return: !drawerClosedState.isOpen,
    restored_focus_id: drawerTrace[drawerTrace.length - 1] ? drawerTrace[drawerTrace.length - 1].restoredToId : null,
  });

  // Step 3: Chain open (N16 reveal component initial collapsed state recorded)
  doc.getElementById('rem-chain-btn-' + domSlug).click();
  const chainHost = doc.getElementById('atskats-remediation-chain-host');
  const chainArticle = chainHost.childNodes[1].childNodes[0];
  snapStep('3_chain_open_initial_state', {
    chain_id: chainHost.getAttribute('data-chain-id'),
    chain_revealed_count: chainArticle.getAttribute('data-revealed-count'),
    chain_revealed_all: chainArticle.getAttribute('data-revealed-all'),
    return_btn_id: doc.getElementById('atskats-remediation-chain-return').id,
  });

  // Step 4: Return to queue
  doc.getElementById('atskats-remediation-chain-return').click();
  snapStep('4_return_to_queue', {
    chain_host_hidden: chainHost.hidden,
    active_focus_id: doc.activeElement ? doc.activeElement.id : null,
  });

  // Step 5: Retry with alternate variant (must select B, never A)
  let capturedHandoff = null;
  const launchRes = sb.SimRemediation.launchRetry(doc, analyticsApp.store, entryId, {
    bankQuestions: islands['sim-bank'].questions,
    practicePath: pathState,
    practiceStarter: (h) => { capturedHandoff = h; return { started: true }; },
  });
  snapStep('5_retry_alternate_variant', {
    selected_instance_id: capturedHandoff.selected_instance_id,
    selected_variant_id: capturedHandoff.selected_variant_id,
    selection_source: capturedHandoff.selection_source,
    excluded_instance_ids: capturedHandoff.excluded_instance_ids,
    path_remaining_after: launchRes.remaining_after,
  });

  // Step 6: Correct verdict on alternate variant -> mastery advance + queue advance to 'retried'
  const retryRec = makeGradedRecord(sb, {
    session_id: 'SES-LOOP-RETRY',
    slot_id: 'RETRY-1',
    topic: 6,
    family_id: 'FAM-6A',
    type_id: 'Q07',
    instance_id: capturedHandoff.selected_instance_id,
    outcome_ids: ['P6-01', 'P6-02', 'P6-04'],
    correct: true,
  });
  const retryResult = remApp.recordRetryVerdict(entryId, retryRec, { day: 10 });
  const retriedRow = doc.getElementById('rem-item-' + domSlug);
  snapStep('6_retry_correct_mastery_and_queue_advance', {
    verdict: retryResult.verdict,
    queue_state: retryResult.entry.state,
    policy_mode: retryResult.policy_mode,
    verbatim_evidence_copy_present: retriedRow.textContent.includes(sb.SimRemediation.ONE_CORRECT_EVIDENCE_COPY_LV),
    mastery_state_after: retryResult.mastery_state,
  });

  // Step 7: Explicit resolve action in #atskats
  doc.getElementById('rem-resolve-btn-' + domSlug).click();
  const resolvedList = doc.getElementById('atskats-remediation-resolved-list');
  snapStep('7_explicit_resolve', {
    resolved_dom_count: resolvedList.childNodes.length,
    resolved_reason: remApp.getSnapshot().resolved_entries[0].resolved_reason,
    resolved_reason_lv: remApp.getSnapshot().resolved_entries[0].resolved_reason_lv,
  });

  const traceDigest = sha256(canonical(steps));
  return {
    schema_version: 1,
    task: 'N28',
    trace_id: 'FX-N28-CLASSIFICATION-LOOP',
    family_id: 'FAM-6A',
    outcome_id: 'P6-01',
    steps_count: steps.length,
    trace_digest: traceDigest,
    final_queue_digest: steps[steps.length - 1].queue_digest,
    steps,
  };
}

function main() {
  const args = parseArgs(process.argv);
  const repoRoot = args.repoRoot;
  const islands = buildIslands(repoRoot);

  if (args.replayOnly) {
    const trace = runLoopTrace(repoRoot, islands);
    process.stdout.write(JSON.stringify({
      trace_digest: trace.trace_digest,
      final_queue_digest: trace.final_queue_digest,
      steps_count: trace.steps_count,
    }));
    return;
  }

  const results = {};
  const failures = [];
  function check(id, ok, detail) {
    results[id] = { status: ok ? 'PASS' : 'FAIL', detail: detail || null };
    if (!ok) { failures.push(id + ': ' + JSON.stringify(detail)); }
  }

  /* ------------------------------ A.1.1 Coalescing + resolved no-resurrect */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.document = doc;
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });
    const store = sb.SimStore.createStore({ optIn: false, doc });

    const r1 = sb.SimRemediation.addMiss(store, {
      slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01'],
      instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ m: 1 }),
    }, { doc, registries: reg });
    const r2 = sb.SimRemediation.addMiss(store, {
      slot_id: 'S6-2', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01', 'P6-02'],
      instance_id: 'COL1-6-6A-B-01', signature_id: 'MC-6A-02', concept_ids: ['P6-02'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ m: 2 }),
    }, { doc, registries: reg });
    const r3 = sb.SimRemediation.addMiss(store, {
      slot_id: 'S6-3', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01', 'P6-04'],
      instance_id: 'COL1-6-6A-C-01', signature_id: 'MC-6A-01', concept_ids: ['P6-04'], chain_ids: [],
      graded_digest: sb.SimStore.digestValue({ m: 3 }),
    }, { doc, registries: reg });

    const q1 = store.getState().remediation_queue;
    const coalescedOk = q1.length === 1 &&
      r1.action === 'created' && r2.action === 'coalesced' && r3.action === 'coalesced' &&
      r3.entry.miss_count === 3 &&
      r3.entry.concept_ids.join(',') === 'P6-01,P6-02,P6-04' &&
      r3.entry.chain_ids.join(',') === 'EX12' &&
      r3.entry.signature_ids.join(',') === 'MC-6A-01,MC-6A-02';

    // Partial verdict enters queue too
    const partialRec = makeGradedRecord(sb, {
      session_id: 'SES-PARTIAL', slot_id: 'S4-2', topic: 4, family_id: 'FAM-4B', type_id: 'Q02',
      instance_id: 'COL1-4-4B-A-01', outcome_ids: ['P4-02'], correct: false, partial: true,
      feedback_items: [{ slot_id: 'S4-2', signature_id: 'MC-4B-01', remediation: { concept_ids: ['P4-02'], chain_ids: ['EX08'] } }],
    });
    sb.SimAnalytics.ingestGradedRecord(store, partialRec);
    const partialAdded = store.getState().remediation_queue.some((e) => e.family_id === 'FAM-4B' && e.state === 'open');

    // Resolve FAM-6A entry, then miss again -> MUST open new entry, NOT resurrect resolved one
    const resolvedBefore = sb.SimRemediation.resolveEntry(store, r3.entry.id, { doc }).resolved;
    const r4 = sb.SimRemediation.addMiss(store, {
      slot_id: 'S6-4', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01'],
      instance_id: 'COL1-6-6A-D-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ m: 4 }),
    }, { doc, registries: reg });
    const qAfter = store.getState().remediation_queue;
    const oldStillResolved = qAfter.find((e) => e.id === r3.entry.id);
    const noResurrectOk = r4.action === 'created' &&
      r4.entry.id !== r3.entry.id &&
      r4.entry.miss_count === 1 &&
      r4.entry.state === 'open' &&
      oldStillResolved && oldStillResolved.state === 'resolved' &&
      oldStillResolved.miss_count === 3 &&
      oldStillResolved.resolved_seq === resolvedBefore.resolved_seq;

    check('a11_coalescing_partial_and_no_rewind', coalescedOk && partialAdded && noResurrectOk, {
      coalescedOk, partialAdded, noResurrectOk,
      miss_count_coalesced: r3.entry.miss_count,
      new_entry_id: r4.entry.id,
      resolved_entry_miss_count: oldStillResolved ? oldStillResolved.miss_count : null,
    });
  }

  /* ------------------------------ A.1 Policy-driven resolve (confirm vs auto) */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.document = doc;
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });
    const basePol = sb.SimRemediation.loadPolicy(doc).policy;

    // 1. Default confirm_required policy
    const st1 = sb.SimStore.createStore({ optIn: false, doc });
    const m1 = sb.SimRemediation.addMiss(st1, {
      slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01'],
      instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ p: 1 }),
    }, { doc, registries: reg }).entry;
    const retryOkRec = makeGradedRecord(sb, {
      session_id: 'SES-POL-1', slot_id: 'RETRY-1', topic: 6, family_id: 'FAM-6A', type_id: 'Q07',
      instance_id: 'COL1-6-6A-B-01', outcome_ids: ['P6-01'], correct: true,
    });
    const resConfirm = sb.SimRemediation.recordRetryVerdict(st1, m1.id, retryOkRec, { doc, policy: basePol, coverage: cov });

    // 2. Scratch one_correct_resolves policy variant
    const autoPol = JSON.parse(JSON.stringify(basePol));
    autoPol.resolution_policy.mode = 'one_correct_resolves';
    autoPol.resolution_policy.auto_resolve_on_correct_retry = true;
    const st2 = sb.SimStore.createStore({ optIn: false, doc });
    const m2 = sb.SimRemediation.addMiss(st2, {
      slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01'],
      instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ p: 1 }),
    }, { doc, registries: reg }).entry;
    const resAuto = sb.SimRemediation.recordRetryVerdict(st2, m2.id, retryOkRec, { doc, policy: autoPol, coverage: cov });

    check('a1_policy_driven_resolution',
      resConfirm.entry.state === 'retried' &&
      resConfirm.entry.resolved_seq === null &&
      resConfirm.policy_copy_lv === sb.SimRemediation.ONE_CORRECT_EVIDENCE_COPY_LV &&
      resAuto.entry.state === 'resolved' &&
      resAuto.entry.resolved_reason === 'auto_one_correct' &&
      resAuto.entry.resolved_seq !== null,
      {
        confirm_state: resConfirm.entry.state,
        confirm_copy: resConfirm.policy_copy_lv,
        auto_state: resAuto.entry.state,
        auto_reason: resAuto.entry.resolved_reason,
      });
  }

  /* ------------------------------ A.1.2 4-retry cyclic selection + ephemeral */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.SimVariantEngine.load(sb.SimFamilyTemplates, islands['sim-conventions']);
    const bankQs = islands['sim-bank'].questions;
    const failedId = 'COL1-6-6A-A-01';
    const entry = {
      id: 'FAM-6A::P6-01',
      family_id: 'FAM-6A',
      outcome_id: 'P6-01',
      instance_id: failedId,
      attempted_instance_ids: [failedId],
      attempted_variant_ids: ['A'],
      last_retry_instance_id: null,
      last_retry_variant_id: null,
      retry_count: 0,
    };

    const picks = [];
    for (let step = 1; step <= 5; step += 1) {
      const sel = sb.SimRemediation.selectRetryInstance(entry, bankQs, { doc });
      picks.push({
        step,
        source: sel.source,
        variant_id: sel.variant_id,
        instance_id: sel.instance_id,
        persisted: sel.source === 'ephemeral' ? sel.instance.extensions.data.ephemeral.persisted : true,
      });
      entry.retry_count += 1;
      entry.attempted_instance_ids.push(sel.instance_id);
      entry.attempted_variant_ids.push(sel.variant_id);
      entry.last_retry_instance_id = sel.instance_id;
      entry.last_retry_variant_id = sel.variant_id;
    }

    const neverReServedFailed = picks.every((p) => p.instance_id !== failedId);
    const allDistinct = new Set(picks.map((p) => p.instance_id)).size === picks.length;
    const cyclicVariantsOk = picks.map((p) => p.variant_id).join(',') === 'B,C,D,A,B';
    const sourcesOk = picks[0].source === 'bank' && picks[1].source === 'bank' && picks[2].source === 'bank' &&
      picks[3].source === 'ephemeral' && picks[4].source === 'ephemeral' &&
      picks[3].persisted === false;

    check('a12_four_retry_selection_and_ephemeral',
      neverReServedFailed && allDistinct && cyclicVariantsOk && sourcesOk,
      { failedId, picks });
  }

  /* ------------------------------ B.1 Loop trace + A.1.3 #atskats matching */
  const loopTrace = runLoopTrace(repoRoot, islands);
  const traceOk = loopTrace.steps.length === 7 &&
    loopTrace.steps[0].active_count === 1 && loopTrace.steps[0].dom_remediation_count === '1' &&
    loopTrace.steps[1].extra.drawer_open === true && loopTrace.steps[1].extra.drawer_concept_id === 'P6-01' &&
    loopTrace.steps[1].extra.drawer_closed_after_return === true &&
    loopTrace.steps[2].extra.chain_id === 'EX12' && loopTrace.steps[2].extra.chain_revealed_count === '0' &&
    loopTrace.steps[3].extra.chain_host_hidden === true &&
    loopTrace.steps[4].extra.selected_instance_id === 'COL1-6-6A-B-01' &&
    loopTrace.steps[5].extra.queue_state === 'retried' && loopTrace.steps[5].extra.verbatim_evidence_copy_present === true &&
    loopTrace.steps[5].p6_01_mastery_state === 'learning' && loopTrace.steps[5].dom_remediation_count === '1' &&
    loopTrace.steps[6].resolved_count === 1 && loopTrace.steps[6].active_count === 0 && loopTrace.steps[6].dom_remediation_count === '0';
  check('b1_end_to_end_classification_loop_trace', traceOk, {
    trace_digest: loopTrace.trace_digest,
    steps_count: loopTrace.steps.length,
    final_active: loopTrace.steps[6].active_count,
    final_resolved: loopTrace.steps[6].resolved_count,
  });

  /* ------------------------------ B.1.1 Nullable chain link corner case */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.document = doc;
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });
    const store = sb.SimStore.createStore({ optIn: false, doc });
    const m = sb.SimRemediation.addMiss(store, {
      slot_id: 'S1-2', topic: 1, family_id: 'FAM-1A', outcome_id: 'P1-02', outcome_ids: ['P1-02', 'P1-03'],
      instance_id: 'COL1-1-1A-A-01', signature_id: 'MC-1A-01', concept_ids: ['P1-02'], chain_ids: [],
      graded_digest: sb.SimStore.digestValue({ nullChain: 1 }),
    }, { doc, registries: reg }).entry;
    sb.SimRemediation.renderQueue(doc, store, { registries: reg, coverage: cov });
    const row = doc.getElementById('atskats-remediation-list').childNodes[0];
    const handoff = sb.SimRemediation.buildStudyHandoff(m, 'anchor', reg, { returnElementId: 'rem-anchor-btn-FAM-1A-P1-02' });
    const noChainBtns = doc.querySelectorAll('.remediation-chain-btn').length === 0;
    const anchorBtns = doc.querySelectorAll('.remediation-anchor-btn').length === 1;
    check('b11_nullable_chain_anchor_only',
      row.getAttribute('data-has-chain') === 'false' && handoff.chain_id === null && noChainBtns && anchorBtns,
      { family_id: m.family_id, chain_id: handoff.chain_id, noChainBtns, anchorBtns });
  }

  /* ------------------------------ B.1.2 On-read dangling anchor/chain fails loudly */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.document = doc;
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });
    const store = sb.SimStore.createStore({ optIn: false, doc });
    store.update((draft) => {
      draft.remediation_queue.push({
        id: 'FAM-6A::P9-99-BROKEN-ANCHOR',
        slot_id: 'S9-1',
        topic: 6,
        family_id: 'FAM-6A',
        outcome_id: 'P9-99-BROKEN-ANCHOR',
        outcome_ids: ['P9-99-BROKEN-ANCHOR'],
        instance_id: 'COL1-6-6A-A-01',
        concept_ids: ['P9-99-BROKEN-ANCHOR'],
        chain_ids: [],
        graded_digest: 'deadbeef',
        state: 'open',
      });
    });
    const err = captureError(() => sb.SimRemediation.renderQueue(doc, store, { registries: reg, coverage: cov }));
    const errBox = doc.getElementById('sim-remediation-error');
    const caughtLoudly = Boolean(
      err && err.code === 'E_REMEDIATION_DANGLING_LINK' &&
      err.message.includes('P9-99-BROKEN-ANCHOR') &&
      errBox.hidden === false &&
      errBox.textContent.includes('P9-99-BROKEN-ANCHOR')
    );
    check('b12_dangling_anchor_on_read_fails_loudly', caughtLoudly, { error: err, domError: errBox.textContent });
  }

  /* ------------------------------ B.1.3 Bounded practice path exhaustion */
  {
    const sb = loadSandbox(repoRoot, null, islands);
    const doc = makeDom(islands);
    sb.document = doc;
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });
    const store = sb.SimStore.createStore({ optIn: false, doc });
    const entry = sb.SimRemediation.addMiss(store, {
      slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01'],
      instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ bound: 1 }),
    }, { doc, registries: reg }).entry;

    const pathState = { remaining: 1, limit: 3, used: 2, exhausted: false };
    const r1 = sb.SimRemediation.launchRetry(doc, store, entry.id, { bankQuestions: islands['sim-bank'].questions, practicePath: pathState });
    const r2 = sb.SimRemediation.launchRetry(doc, store, entry.id, { bankQuestions: islands['sim-bank'].questions, practicePath: pathState });
    const retryHost = doc.getElementById('atskats-remediation-retry-host');
    check('b13_bounded_path_respects_exhaustion',
      r1.status === 'LAUNCHED' && r1.remaining_after === 0 && pathState.used === 3 &&
      r2.status === 'PATH_EXHAUSTED' && r2.bound_respected === true && r2.bypassed === false &&
      r2.handoff === null && retryHost.getAttribute('data-retry-status') === 'PATH_EXHAUSTED',
      { first: { status: r1.status, remaining: r1.remaining_after }, second: { status: r2.status, reason: r2.reason_lv } });
  }

  /* ------------------------------ C.1.1 Fresh-process replay determinism */
  {
    const childRaw = execFileSync(
      process.execPath,
      [__filename, '--replay-only', '--repo-root', repoRoot],
      { encoding: 'utf8' }
    );
    const child = JSON.parse(childRaw);
    check('c11_fresh_process_replay_determinism',
      child.trace_digest === loopTrace.trace_digest &&
      child.final_queue_digest === loopTrace.final_queue_digest &&
      child.steps_count === loopTrace.steps_count,
      { in_process_digest: loopTrace.trace_digest, fresh_process_digest: child.trace_digest });
  }

  /* ------------------------------ C.1.1 Populated queue round-trip, erase & privacy */
  let privacyAudit = null;
  {
    const backing = Object.create(null);
    const env = createInstrumentedEnv(backing);
    const sb = loadSandbox(repoRoot, env, islands);
    const doc = makeDom(islands);
    const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
    const reg = sb.SimRemediation.buildRegistries(doc, { coverage: cov });

    env.setPhase('default-memory-session');
    const app = sb.SimAnalytics.init(doc, { storage: env.storage, coverage: cov, probeExisting: false });
    const rem = sb.SimRemediation.init(doc, { coverage: cov, bank: islands['sim-bank'], store: app.store });
    rem.addMiss({
      slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01', 'P6-02'],
      instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
      graded_digest: sb.SimStore.digestValue({ priv: 1 }),
    });
    const memKeys = Object.keys(backing);
    const memWrites = env.accessLog.filter((e) => e.operation === 'setItem').length;

    env.setPhase('opt-in-persist-and-reload');
    app.store.setOptIn(true, env.storage);
    const d1 = app.store.getDigest();
    const qSnap1 = rem.getSnapshot();

    const env2 = createInstrumentedEnv(backing);
    const sb2 = loadSandbox(repoRoot, env2, islands);
    const doc2 = makeDom(islands);
    const app2 = sb2.SimAnalytics.init(doc2, { storage: env2.storage, coverage: cov, probeExisting: true });
    const rem2 = sb2.SimRemediation.init(doc2, { coverage: cov, bank: islands['sim-bank'], store: app2.store });
    const d2 = app2.store.getDigest();
    const qSnap2 = rem2.getSnapshot();

    env.setPhase('erase-and-verify');
    app.store.requestErase();
    app.store.confirmErase();
    rem.refresh();
    const keysAfterErase = Object.keys(backing);
    const domCountAfterErase = doc.getElementById('atskats-remediation-count').textContent;

    const allowedKeys = new Set(sb.SimStore.SCHEMA_KEYS);
    const outliers = env.accessLog.filter((e) => !allowedKeys.has(e.key));
    const analyticsSchema = islands['sim-analytics'];
    const recordedQueueFields = (analyticsSchema.store_contract && analyticsSchema.store_contract.remediation_queue_fields) || [];

    privacyAudit = {
      schema_version: 1,
      task: 'N28',
      status: (memKeys.length === 0 && memWrites === 0 && d1 === d2 && qSnap1.digest === qSnap2.digest &&
               outliers.length === 0 && env.networkLog.length === 0 && keysAfterErase.length === 0 &&
               domCountAfterErase === '0' && recordedQueueFields.length > 0)
        ? 'PASS' : 'FAIL',
      storage_keys: sb.SimStore.SCHEMA_KEYS,
      remediation_queue_fields: recordedQueueFields,
      memory_phase_writes: memWrites,
      roundtrip_store_digest: d1,
      roundtrip_queue_digest: qSnap1.digest,
      outlier_keys: outliers,
      network_attempts_count: env.networkLog.length,
      keys_after_erase: keysAfterErase,
      dom_count_after_erase: domCountAfterErase,
    };

    check('c11_store_roundtrip_erase_and_privacy', privacyAudit.status === 'PASS', {
      memWrites, d1, d2, qDigest1: qSnap1.digest, qDigest2: qSnap2.digest,
      keysAfterErase, domCountAfterErase, queueFieldsCount: recordedQueueFields.length,
    });
  }

  /* ------------------------------ C.1.3 Built-artifact smoke check */
  const artifactPath = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(artifactPath)) {
    const html = fs.readFileSync(artifactPath, 'utf8');
    const islandIds = [
      'sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms', 'sim-golden-vectors',
      'sim-terms', 'sim-analytics', 'sim-mastery-policy', 'sim-scheduler-policy',
      'sim-remediation-policy', 'sim-figures', 'sim-chains', 'sim-engines',
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
      atob: (s) => Buffer.from(s, 'base64').toString('binary'),
      TextDecoder, Uint8Array,
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
    const smoke = artSb.SimSmoke ? artSb.SimSmoke.lastReport : null;
    const n28Vec = smoke && smoke.vectors ? smoke.vectors.find((v) => v.id === 'SMK-N28-REMEDIATION-WALK') : null;
    check('c13_built_artifact_smoke',
      Boolean(smoke && smoke.status === 'PASS' && n28Vec && n28Vec.status === 'PASS' && artEnv.networkLog.length === 0),
      { total: smoke ? smoke.total : 0, passed: smoke ? smoke.passed : 0, n28Vec });
  } else {
    check('c13_built_artifact_smoke', false, { reason: 'output/simulator.html missing' });
  }

  const report = {
    schema_version: 1,
    task: 'N28',
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks: results,
    failures,
  };

  if (args.record) {
    const outPath = path.isAbsolute(args.record) ? args.record : path.join(repoRoot, args.record);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }
  if (args.traceOut) {
    const tPath = path.isAbsolute(args.traceOut) ? args.traceOut : path.join(repoRoot, args.traceOut);
    fs.mkdirSync(path.dirname(tPath), { recursive: true });
    fs.writeFileSync(tPath, JSON.stringify(loopTrace, null, 2) + '\n', 'utf8');
  }
  if (args.privacyOut && privacyAudit) {
    const pPath = path.isAbsolute(args.privacyOut) ? args.privacyOut : path.join(repoRoot, args.privacyOut);
    fs.mkdirSync(path.dirname(pPath), { recursive: true });
    fs.writeFileSync(pPath, JSON.stringify(privacyAudit, null, 2) + '\n', 'utf8');
  }

  console.log('N28 runtime: ' + report.status + ' (' + Object.keys(results).length + ' checks, ' + failures.length + ' failures)');
  for (const f of failures) {
    console.error('  FAIL:', f);
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
