#!/usr/bin/env node
/* N26 runtime, pure reducer, fresh-process replay, store migration, view honesty,
 * 3-profile render fixtures, end-to-end FX-N23-MIXED integration, and built-artifact
 * smoke harness.
 *
 * Usage:
 *   node tools/check_n26_runtime.js [--repo-root .] [--record PATH] [--fixtures-out PATH]
 *   node tools/check_n26_runtime.js --replay-only --repo-root .
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
    fixturesOut: null,
    replayOnly: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--fixtures-out') { args.fixturesOut = argv[i + 1]; i += 1; }
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
    getElementById(id) { return registry[id] || null; },
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
    _registry: registry,
  };
  doc.documentElement.setAttribute('data-theme', 'light');
  doc.documentElement.appendChild(doc.body);

  Object.keys(islands || {}).forEach((id) => {
    const s = new Node('script', id);
    s.setAttribute('type', 'application/json');
    s.textContent = typeof islands[id] === 'string' ? islands[id] : JSON.stringify(islands[id]);
    doc.body.appendChild(s);
  });

  const ids = [
    'sim-coverage-error', 'sim-mastery-error',
    'atskats', 'atskats-honesty-note', 'atskats-storage-notice', 'atskats-zero-notice',
    'atskats-sessions-count', 'atskats-outcomes-correct', 'atskats-outcomes-first-pass',
    'atskats-remediation-count', 'atskats-topics-body', 'atskats-forms-list',
    'atskats-remediation-list', 'atskats-outcomes-list',
    'atskats-mastery-wrap', 'atskats-mastery-heading', 'atskats-mastery-honesty',
    'atskats-mastery-fresh-note', 'atskats-mastery-summary', 'atskats-mastery-topics',
    'prakse', 'prakse-mastery-panel', 'prakse-mastery-honesty', 'prakse-mastery-topics',
    'store-consent-copy', 'store-opt-in-toggle', 'store-status', 'store-notice',
    'store-export-btn', 'store-export-status', 'store-erase-request',
    'store-erase-confirm-box', 'store-erase-prompt', 'store-erase-confirm', 'store-erase-cancel',
    'theme-toggle', 'theme-status', 'sim-smoke-status'
  ];
  ids.forEach((id) => {
    if (!registry[id]) { doc.body.appendChild(new Node('div', id)); }
  });
  return doc;
}

function createStorage(initial) {
  const backing = Object.create(null);
  if (initial) {
    Object.keys(initial).forEach((k) => { backing[k] = String(initial[k]); });
  }
  const log = [];
  const api = {
    getItem(k) { log.push({ op: 'getItem', key: String(k) }); return Object.prototype.hasOwnProperty.call(backing, k) ? backing[k] : null; },
    setItem(k, v) { log.push({ op: 'setItem', key: String(k) }); backing[String(k)] = String(v); },
    removeItem(k) { log.push({ op: 'removeItem', key: String(k) }); delete backing[String(k)]; },
    get length() { return Object.keys(backing).length; },
    key(i) { return Object.keys(backing)[i] || null; },
  };
  return { storage: api, backing, log };
}

function loadMasteryStandalone(repoRoot, islands, backingStorage) {
  const doc = makeDom(islands);
  const netLog = [];
  const sb = {
    document: doc,
    console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
    encodeURIComponent, decodeURIComponent, unescape,
    localStorage: backingStorage || null,
    fetch: (u) => { netLog.push(u); throw new Error('Network forbidden'); },
    XMLHttpRequest: function () { netLog.push('XHR'); throw new Error('Network forbidden'); },
    WebSocket: function () { netLog.push('WS'); throw new Error('Network forbidden'); },
    COVERAGE_INVARIANTS: { total: 64, perTopic: { '1': 9, '2': 10, '3': 11, '4': 11, '5': 10, '6': 8, '7': 5 } },
  };
  sb.globalThis = sb;
  sb.window = sb;
  vm.createContext(sb);
  const files = [
    'src/coverage-loader.js',
    'src/bank-loader.js',
    'src/compiled/store.js',
    'src/compiled/analytics.js',
    'src/compiled/mastery.js',
  ];
  for (const rel of files) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sb, { filename: rel });
  }
  return { sb, doc, netLog };
}

function scriptedWalkEvents() {
  return [
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 4 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 5 },
    { kind: 'decay', outcome_id: 'P1-01', days_inactive: 14 },
  ];
}

function runReplayOnly(repoRoot) {
  const islands = {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
  };
  const { sb, doc } = loadMasteryStandalone(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const loaded = sb.SimMastery.loadPolicy(doc);
  let state = sb.SimMastery.createInitialStateMap(cov, loaded.policy, loaded.digest);
  const steps = [];
  for (const ev of scriptedWalkEvents()) {
    state = sb.SimMastery.reduce(state, [ev], loaded.policy);
    steps.push({ event: ev, state: state.outcomes['P1-01'].state, streak: state.outcomes['P1-01'].consecutive_correct });
  }
  const digest = sb.SimMastery.digestOfMap(state);
  process.stdout.write(JSON.stringify({ digest, steps }));
}

function loadAllBankQuestions(repoRoot) {
  const bankDir = path.join(repoRoot, 'data/bank');
  const files = fs.readdirSync(bankDir).filter((f) => f.endsWith('.json')).sort();
  const questions = [];
  for (const f of files) {
    const raw = readJson(path.join(bankDir, f));
    if (Array.isArray(raw.questions)) { questions.push(...raw.questions); }
  }
  return questions;
}

function buildIslands(repoRoot) {
  return {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-conventions': readJson(path.join(repoRoot, 'data/conventions.json')),
    'sim-terms': readJson(path.join(repoRoot, 'data/terms.json')),
    'sim-analytics': readJson(path.join(repoRoot, 'data/analytics_schema.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
    'sim-grading-policy': readJson(path.join(repoRoot, 'data/grading_policy.json')),
    'sim-feedback-classification': readJson(path.join(repoRoot, 'data/feedback_classification.json')),
    'sim-exam-policy': readJson(path.join(repoRoot, 'data/exam_policy.json')),
    'sim-response-types': readJson(path.join(repoRoot, 'data/response_types.json')),
    'sim-engines': readJson(path.join(repoRoot, 'data/engine_taxonomy.json')),
    'sim-graph-scoring': readJson(path.join(repoRoot, 'data/graph_scoring_contract.json')),
    'sim-method-cards': readJson(path.join(repoRoot, 'data/method_cards.json')),
    'sim-method-engine': readJson(path.join(repoRoot, 'data/method_engine_contract.json')),
    'sim-figures': (() => {
      const figs = [];
      for (const rel of ['data/figures_t12.json', 'data/figures_t23.json', 'data/figures_t4.json', 'data/figures_t5.json', 'data/figures_t67.json']) {
        const d = readJson(path.join(repoRoot, rel));
        if (Array.isArray(d.figures)) { figs.push(...d.figures); }
      }
      return { island_id: 'sim-figures', figures: figs };
    })(),
    'sim-golden-vectors': readJson(path.join(repoRoot, 'data/golden_vectors.json')),
  };
}

function runMixedFixture(repoRoot, islands) {
  const { sb, doc } = loadMasteryStandalone(repoRoot, islands, null);
  const fullFiles = [
    'src/prng.js',
    'src/conventions-loader.js',
    'src/terms-loader.js',
    'src/quantity-engine.js',
    'src/graph-scoring-engine.js',
    'src/method-engine.js',
    'src/compiled/session.js',
    'src/compiled/inputs/registry.js',
    'src/compiled/inputs/integration.js',
    'src/compiled/grading.js',
    'src/compiled/feedback.js',
  ];
  for (const rel of fullFiles) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sb, { filename: rel });
  }
  const matrix = readJson(path.join(repoRoot, 'tools/fixtures/n23_score_matrix.json'));
  const mixed = matrix.forms.find((f) => f.form_id === 'FX-N23-MIXED');
  const questions = loadAllBankQuestions(repoRoot);
  const qById = Object.create(null);
  for (const q of questions) { qById[q.question_id] = q; }

  sb.SimEngines.load(doc);
  sb.SimInputsRegistry.load(islands['sim-response-types'], islands['sim-terms']);
  const methodEngine = new sb.SimMethodEngine.MethodEngine(islands['sim-method-engine'], islands['sim-terms']);
  const method = Object.create(methodEngine);
  method.MethodEngine = sb.SimMethodEngine.MethodEngine;
  method.specForVector = sb.SimMethodEngine.specForVector;
  method.sha256 = sb.SimMethodEngine.sha256;
  sb.SimGraphScoring.load(doc);

  const termsMap = Object.create(null);
  (islands['sim-terms'].terms || []).forEach((e) => {
    if (e && typeof e.key === 'string') { termsMap[e.key] = e.text_lv; }
  });

  const examPolicy = islands['sim-exam-policy'];
  const context = {
    doc,
    quantity: sb.SimEngines,
    method,
    graph: sb.SimGraphScoring,
    inputsRegistry: sb.SimInputsRegistry,
    inputsIntegration: sb.SimInputsIntegration,
    figures: sb.SimGraphScoring.state.figures,
    terms: termsMap,
    examPolicy,
    bank: { instancesById: qById },
    bindingSource: 'tools/fixtures/n23_score_matrix.json#FX-N23-MIXED',
    oracle: {
      oracle_version: 'n23-score-matrix/v' + String(matrix.schema_version || 1),
      oracle_digest: sha256(canonical(matrix)),
      conventions_digest: sha256(canonical(islands['sim-conventions'])),
    },
  };

  const session = new sb.SimSession.ExamSession({
    policy: examPolicy,
    form: { form_id: mixed.form_id, slots: examPolicy.slots },
    sessionId: 'SES-FX-N23-MIXED-0',
    clock: { now: () => 0 },
  });
  session.dispatch('start');
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
      const instance = qById[binding.instance_id];
      payload = JSON.parse(JSON.stringify(sb.SimInputsIntegration.buildPayload(binding.type_id, contract, instance, capture)));
    }
    session.dispatch('answer', { slot_id: slotId, payload });
  });
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });
  const terminal = session.toTerminalRecord();

  const bindings = (mixed.bindings || []).map((b) => ({
    slot_id: b.slot_id,
    type_id: b.type_id,
    instance_id: b.instance_id,
    instance: qById[b.instance_id],
  }));
  const core = sb.SimGrading.gradeTerminalRecord(terminal, bindings, context);
  const fb = sb.SimFeedback.assemble(core, context);
  const fullRecord = sb.SimGrading.composeGradedRecord(core, fb);
  return { fullRecord, qById };
}

function collectNodeText(node) {
  if (!node) { return ''; }
  if (node.childNodes && node.childNodes.length) {
    return node.childNodes.map(collectNodeText).join(' ');
  }
  return node._text || '';
}

function main() {
  const args = parseArgs(process.argv);
  if (args.replayOnly) {
    runReplayOnly(args.repoRoot);
    return;
  }

  const repoRoot = args.repoRoot;
  const results = {};
  const failures = [];
  function check(id, ok, detail) {
    results[id] = { status: ok ? 'PASS' : 'FAIL', ...(detail || {}) };
    if (!ok) { failures.push(id + ': ' + JSON.stringify(detail || {})); }
  }

  const islands = buildIslands(repoRoot);
  const bankQuestions = loadAllBankQuestions(repoRoot);
  islands['sim-bank'] = { island_id: 'sim-bank', schema_version: 1, bank_version: '1.0.0-n20', status: 'frozen-reviewed-bank', questions: bankQuestions };

  const { sb, doc, netLog } = loadMasteryStandalone(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const loaded = sb.SimMastery.loadPolicy(doc);
  const policy = loaded.policy;

  /* A.1 — Unreachable-state scratch policy must fail naming the state */
  const scratchUnreachable = JSON.parse(JSON.stringify(policy));
  scratchUnreachable.states.push({
    id: 'stranded_vault',
    order: 99,
    label_lv: 'Iestrēdzis stāvoklis',
    icon: '✕',
    entry_rule: { kind: 'transition', from_states: ['mastered'] },
    exit_paths: [{ event: 'criterion_verdict', condition: 'correct', to_state: 'mastered' }],
    regression_rule: { event: 'incorrect', to_state: 'learning' },
  });
  const unreachRep = sb.SimMastery.validatePolicy(scratchUnreachable);
  check('a1_unreachable_state_fixture',
    !unreachRep.valid && unreachRep.unreachable_states.indexOf('stranded_vault') >= 0 &&
    unreachRep.errors.some((e) => e.indexOf('stranded_vault') >= 0),
    { unreachable_states: unreachRep.unreachable_states, errors: unreachRep.errors }
  );

  /* A.1.2 — Per-criterion mapping totality across all 28 families / 112 instances */
  const mappingReport = sb.SimMastery.verifyBankCriterionMapping(bankQuestions, cov);
  const unmappedErr = captureError(() => {
    sb.SimMastery.resolveCriterionOutcomes({ question_id: 'SCRATCH-1', family_id: 'FAM-NONE', outcome_ids: [] }, { criterion_id: 'C_ORPHAN' }, cov);
  });
  check('a12_criterion_mapping_totality',
    mappingReport.families_covered.length === 28 &&
    mappingReport.total_instances === 112 &&
    mappingReport.total_criteria === 267 &&
    mappingReport.unmapped.length === 0 &&
    unmappedErr && unmappedErr.code === 'E_MASTERY_UNMAPPED_CRITERION',
    {
      families: mappingReport.families_covered.length,
      instances: mappingReport.total_instances,
      criteria: mappingReport.total_criteria,
      unmapped: mappingReport.unmapped.length,
      negative_code: unmappedErr ? unmappedErr.code : null,
    }
  );

  /* A.1.3 — Pure reducer transition fixtures + partial task + double-run parity */
  const s0 = sb.SimMastery.createInitialStateMap(cov, policy, loaded.digest);
  const events = scriptedWalkEvents();
  const trace = [{ step: 0, state: s0.outcomes['P1-01'].state, streak: s0.outcomes['P1-01'].consecutive_correct }];
  let cur = s0;
  for (let i = 0; i < events.length; i += 1) {
    cur = sb.SimMastery.reduce(cur, [events[i]], policy);
    trace.push({
      step: i + 1,
      event: events[i].kind === 'decay' ? 'decay(' + events[i].days_inactive + 'd)' : events[i].verdict,
      state: cur.outcomes['P1-01'].state,
      streak: cur.outcomes['P1-01'].consecutive_correct,
    });
  }
  const expectedPath = ['unseen', 'learning', 'learning', 'near_mastered', 'near_mastered', 'mastered', 'needs_review'];
  const actualPath = trace.map((t) => t.state);
  const cur2 = sb.SimMastery.reduce(s0, events, policy);
  const dRun1 = sb.SimMastery.digestOfMap(cur);
  const dRun2 = sb.SimMastery.digestOfMap(cur2);

  // Recovery from needs_review -> near_mastered -> mastered, and regression near_mastered -> learning, and miss in mastered -> needs_review
  const recovered = sb.SimMastery.reduce(cur, [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 20 }], policy);
  const regressed = sb.SimMastery.reduce(recovered, [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 21 }], policy);
  const missMastered = sb.SimMastery.reduce(
    sb.SimMastery.reduce(s0, events.slice(0, 5), policy),
    [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 6 }],
    policy
  );
  // Partial task: criterion 1 awarded (P3-01), criterion 2 denied (P3-02), criterion 3 pending (P3-03)
  const partialEvents = sb.SimMastery.extractCriterionEvents({
    record_kind: 'graded-record',
    digest: '0'.repeat(64),
    slots: [{
      slot_id: 'S3-PARTIAL',
      state: 'graded',
      criteria: [
        { criterion_id: 'C1', status: 'awarded', grading: 'auto', outcome_ids: ['P3-01'] },
        { criterion_id: 'C2', status: 'denied', grading: 'auto', outcome_ids: ['P3-02'] },
        { criterion_id: 'C3', status: 'pending', grading: 'self', outcome_ids: ['P3-03'] },
      ],
    }],
  }, cov, { day: 1 });
  const partialMap = sb.SimMastery.reduce(s0, partialEvents, policy);

  check('a13_reducer_transitions_and_determinism',
    JSON.stringify(actualPath) === JSON.stringify(expectedPath) &&
    dRun1 === dRun2 &&
    recovered.outcomes['P1-01'].state === 'near_mastered' &&
    regressed.outcomes['P1-01'].state === 'learning' &&
    missMastered.outcomes['P1-01'].state === 'needs_review' &&
    partialMap.outcomes['P3-01'].state === 'learning' &&
    partialMap.outcomes['P3-01'].consecutive_correct === 1 &&
    partialMap.outcomes['P3-02'].state === 'learning' &&
    partialMap.outcomes['P3-02'].consecutive_correct === 0 &&
    partialMap.outcomes['P3-03'].state === 'unseen',
    {
      path: actualPath,
      digest_run1: dRun1,
      digest_run2: dRun2,
      recovery: recovered.outcomes['P1-01'].state,
      regression: regressed.outcomes['P1-01'].state,
      miss_in_mastered: missMastered.outcomes['P1-01'].state,
      partial: {
        P3_01: partialMap.outcomes['P3-01'],
        P3_02: partialMap.outcomes['P3-02'],
        P3_03: partialMap.outcomes['P3-03'],
      },
      trace,
    }
  );

  /* C.1.1 — Fresh-process replay + interleaved reverse-direction independence */
  const replayRaw = execFileSync('node', [__filename, '--replay-only', '--repo-root', repoRoot], { encoding: 'utf8' });
  const replayParsed = JSON.parse(replayRaw);

  const interleaveEvents = [
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'incorrect', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 4 },
  ];
  const interReduced = sb.SimMastery.reduce(s0, interleaveEvents, policy);
  const p1Solo = sb.SimMastery.reduce(s0, interleaveEvents.filter((e) => e.outcome_id === 'P1-01'), policy);
  const p4Solo = sb.SimMastery.reduce(s0, interleaveEvents.filter((e) => e.outcome_id === 'P4-02'), policy);
  check('c11_fresh_replay_and_interleaved_independence',
    replayParsed.digest === dRun1 &&
    interReduced.outcomes['P1-01'].state === 'mastered' &&
    interReduced.outcomes['P4-02'].state === 'near_mastered' &&
    canonical(interReduced.outcomes['P1-01']) === canonical(p1Solo.outcomes['P1-01']) &&
    canonical(interReduced.outcomes['P4-02']) === canonical(p4Solo.outcomes['P4-02']),
    {
      in_process_digest: dRun1,
      fresh_process_digest: replayParsed.digest,
      interleaved_P1_01: interReduced.outcomes['P1-01'].state,
      interleaved_P4_02: interReduced.outcomes['P4-02'].state,
    }
  );

  /* B.1 & B.1.1 — Store migration, round-trip, reload, newer-version lock, erase */
  const preMasteryV2 = {
    schema_version: 2,
    storage_kind: 'sim-colloq1-store',
    settings: { opt_in: true, theme: 'light' },
    progress: { topics: {}, outcomes: {}, outcomes_correct_once: [], outcomes_first_pass: [], form_history: [] },
    remediation_queue: [],
    events: [],
    events_pruned_count: 0,
  };
  const migBacking = createStorage({ sim_colloq1_store_v2: JSON.stringify(preMasteryV2) });
  const migEnv = loadMasteryStandalone(repoRoot, islands, migBacking.storage);
  const migStore = migEnv.sb.SimStore.createStore({ optIn: true, storage: migBacking.storage, doc: migEnv.doc });
  const migMap = migEnv.sb.SimMastery.readFromStore(migStore, cov, policy, loaded.digest);
  const migAllUnseen = Object.keys(migMap.outcomes).length === 64 &&
    Object.values(migMap.outcomes).every((e) => e.state === 'unseen');

  const newerBacking = createStorage({ sim_colloq1_store_v2: JSON.stringify({ schema_version: 99, future_payload: 'keep' }) });
  const newerEnv = loadMasteryStandalone(repoRoot, islands, newerBacking.storage);
  const newerStore = newerEnv.sb.SimStore.createStore({ probeExisting: true, storage: newerBacking.storage, doc: newerEnv.doc });
  const newerWriteErr = captureError(() => newerStore.setOptIn(true, newerBacking.storage));
  const newerPreserved = JSON.parse(newerBacking.backing.sim_colloq1_store_v2).schema_version === 99;

  // Round-trip + reload + erase
  const rtBacking = createStorage();
  const rtEnv1 = loadMasteryStandalone(repoRoot, islands, rtBacking.storage);
  const rtStore1 = rtEnv1.sb.SimStore.createStore({ optIn: true, storage: rtBacking.storage, doc: rtEnv1.doc });
  rtEnv1.sb.SimMastery.writeToStore(rtStore1, cur);
  const storeDigest1 = rtStore1.getDigest();
  const masteryDigest1 = rtEnv1.sb.SimMastery.digestOfMap(rtEnv1.sb.SimMastery.readFromStore(rtStore1, cov, policy, loaded.digest));

  const rtEnv2 = loadMasteryStandalone(repoRoot, islands, rtBacking.storage);
  const rtStore2 = rtEnv2.sb.SimStore.createStore({ probeExisting: true, storage: rtBacking.storage, doc: rtEnv2.doc });
  const storeDigest2 = rtStore2.getDigest();
  const masteryDigest2 = rtEnv2.sb.SimMastery.digestOfMap(rtEnv2.sb.SimMastery.readFromStore(rtStore2, cov, policy, loaded.digest));

  rtStore2.requestErase();
  rtStore2.confirmErase();
  const afterEraseMap = rtEnv2.sb.SimMastery.readFromStore(rtStore2, cov, policy, loaded.digest);
  const afterEraseUnseen = Object.values(afterEraseMap.outcomes).every((e) => e.state === 'unseen');

  check('b11_store_migration_roundtrip_and_erase',
    migAllUnseen &&
    newerStore.isNewerVersionLocked() &&
    newerWriteErr && newerWriteErr.code === 'E_STORE_WRITE_BLOCKED_NEWER_VERSION' &&
    newerPreserved &&
    storeDigest1 === storeDigest2 &&
    masteryDigest1 === masteryDigest2 &&
    masteryDigest1 === dRun1 &&
    Object.keys(rtBacking.backing).length === 0 &&
    afterEraseUnseen,
    {
      pre_mastery_all_unseen: migAllUnseen,
      newer_version_error: newerWriteErr ? newerWriteErr.code : null,
      roundtrip_store_digest: storeDigest1,
      roundtrip_mastery_digest: masteryDigest1,
      keys_after_erase: Object.keys(rtBacking.backing).length,
      after_erase_all_unseen: afterEraseUnseen,
    }
  );

  /* B.1.2 — View renderers: 3 learner profiles + unavailable corner case + icon+text + honesty */
  const availAll = sb.SimMastery.computeAvailability(cov, bankQuestions, policy);

  // Profile 1: Fresh
  const freshMap = sb.SimMastery.createInitialStateMap(cov, policy, loaded.digest);
  // Profile 2: Mid-progress
  const midEvents = [
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'incorrect', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-02', verdict: 'correct', day: 1 },
    { kind: 'decay', outcome_id: 'P4-02', days_inactive: 15 },
  ];
  const midMap = sb.SimMastery.reduce(freshMap, midEvents, policy);
  // Profile 3: Near-complete
  const nearCompleteEvents = [];
  const allOids = Object.keys(freshMap.outcomes).sort();
  for (let i = 0; i < allOids.length; i += 1) {
    const oid = allOids[i];
    if (i < 54) {
      for (let k = 0; k < 4; k += 1) { nearCompleteEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 }); }
    } else if (i < 60) {
      nearCompleteEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 });
      nearCompleteEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 });
    } else if (i < 62) {
      for (let k = 0; k < 4; k += 1) { nearCompleteEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 1 }); }
      nearCompleteEvents.push({ kind: 'decay', outcome_id: oid, days_inactive: 14 });
    } else {
      nearCompleteEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'incorrect', day: 5 });
    }
  }
  const nearMap = sb.SimMastery.reduce(freshMap, nearCompleteEvents, policy);

  // Corner case: Topic 7 pending review -> zero eligible instances for P7-01..P7-05
  const pendingBank = bankQuestions.map((q) => {
    if (q.topic === 7) {
      const copy = JSON.parse(JSON.stringify(q));
      copy.review = { accessibility: 'pending', calculation: 'passed', content: 'passed', source: 'passed' };
      return copy;
    }
    return q;
  });
  const availPendingT7 = sb.SimMastery.computeAvailability(cov, pendingBank, policy);

  const freshAtskats = sb.SimMastery.renderAtskats(doc, cov, freshMap, policy, availAll);
  const freshPrakse = sb.SimMastery.renderPrakse(doc, cov, freshMap, policy, availAll);
  const freshRenderedText = collectNodeText(doc.getElementById('atskats-mastery-wrap')) + ' ' + collectNodeText(doc.getElementById('prakse-mastery-panel'));
  const iconNodes = doc.querySelectorAll('.mastery-icon');
  const labelNodes = doc.querySelectorAll('.mastery-state-label');
  const forbiddenRe = /\b(?:sertifik[aā]t\w*|akredit[eē]t\w*|ofici[aā]li\s+apstiprin\w*|garant[eē]\w*|ofici[aā]l[aā]\s+atz[iī]me)\b/i;

  const midAtskats = sb.SimMastery.buildAtskatsViewModel(cov, midMap, policy, availAll);
  const midPrakse = sb.SimMastery.buildPrakseViewModel(cov, midMap, policy, availAll);
  const nearAtskats = sb.SimMastery.buildAtskatsViewModel(cov, nearMap, policy, availAll);
  const nearPrakse = sb.SimMastery.buildPrakseViewModel(cov, nearMap, policy, availAll);
  const unavailAtskats = sb.SimMastery.renderAtskats(doc, cov, freshMap, policy, availPendingT7);
  const unavailPrakse = sb.SimMastery.renderPrakse(doc, cov, freshMap, policy, availPendingT7);
  const t7Rows = unavailPrakse.topics[6].outcomes;
  const t7AllUnavailable = t7Rows.length === 5 && t7Rows.every((r) =>
    r.effective_state === 'unavailable' &&
    r.available === false &&
    r.label_lv === policy.availability_copy_lv.unavailable_label_lv &&
    typeof r.reason_lv === 'string' && r.reason_lv.length > 0
  );

  check('b12_view_profiles_honesty_and_unavailable',
    freshAtskats.is_fresh === true &&
    freshAtskats.counts.unseen === 64 &&
    freshPrakse.counts.unseen === 64 &&
    midAtskats.counts.mastered === 1 &&
    midAtskats.counts.needs_review === 1 &&
    midAtskats.counts.near_mastered === 1 &&
    midAtskats.counts.learning === 1 &&
    nearAtskats.counts.mastered === 54 &&
    t7AllUnavailable &&
    unavailAtskats.counts.unavailable === 5 &&
    iconNodes.length >= 128 &&
    labelNodes.length >= 128 &&
    !forbiddenRe.test(freshRenderedText) &&
    !forbiddenRe.test(collectNodeText(doc.getElementById('prakse-mastery-panel'))),
    {
      fresh_counts: freshAtskats.counts,
      mid_counts: midAtskats.counts,
      near_counts: nearAtskats.counts,
      unavailable_t7_counts: unavailPrakse.topics[6].counts,
      icon_nodes: iconNodes.length,
      label_nodes: labelNodes.length,
    }
  );

  /* B.1.3 — End-to-end integration: FX-N23-MIXED -> reducer -> store -> views re-render */
  const { fullRecord } = runMixedFixture(repoRoot, islands);
  const e2eBacking = createStorage();
  const e2eEnv = loadMasteryStandalone(repoRoot, islands, e2eBacking.storage);
  const appAnalytics = e2eEnv.sb.SimAnalytics.init(e2eEnv.doc, { coverage: cov, storage: e2eBacking.storage, probeExisting: false });
  const appMastery = e2eEnv.sb.SimMastery.init(e2eEnv.doc, { coverage: cov, bank: islands['sim-bank'], store: appAnalytics.store });
  appAnalytics.ingestGradedRecord(fullRecord);

  // Hand-computed expectation for FX-N23-MIXED criterion sequence
  const expectedMixed = e2eEnv.sb.SimMastery.reduce(
    e2eEnv.sb.SimMastery.createInitialStateMap(cov, policy, loaded.digest),
    e2eEnv.sb.SimMastery.extractCriterionEvents(fullRecord, cov),
    policy
  );
  const storedAfterE2e = appMastery.readFromStore();
  const renderedSummaryText = collectNodeText(e2eEnv.doc.getElementById('atskats-mastery-summary'));
  const renderedPrakseT5 = collectNodeText(e2eEnv.doc.getElementById('prakse-mastery-topic-5'));

  check('b13_end_to_end_mixed_session',
    e2eEnv.sb.SimMastery.digestOfMap(storedAfterE2e) === e2eEnv.sb.SimMastery.digestOfMap(expectedMixed) &&
    storedAfterE2e.outcomes['P1-05'].state === 'near_mastered' &&
    storedAfterE2e.outcomes['P5-05'].state === 'near_mastered' &&
    storedAfterE2e.outcomes['P2-01'].state === 'learning' &&
    storedAfterE2e.outcomes['P2-01'].consecutive_correct === 1 &&
    storedAfterE2e.outcomes['P6-01'].state === 'learning' &&
    storedAfterE2e.outcomes['P6-01'].consecutive_correct === 0 &&
    storedAfterE2e.outcomes['P4-02'].state === 'learning' &&
    storedAfterE2e.outcomes['P1-02'].state === 'unseen' &&
    storedAfterE2e.outcomes['P1-08'].state === 'unseen' &&
    renderedSummaryText.indexOf('Gandrīz apgūts: 5') >= 0 &&
    renderedPrakseT5.indexOf('P5-05') >= 0 &&
    netLog.length === 0 && e2eEnv.netLog.length === 0,
    {
      e2e_mastery_digest: e2eEnv.sb.SimMastery.digestOfMap(storedAfterE2e),
      expected_digest: e2eEnv.sb.SimMastery.digestOfMap(expectedMixed),
      rendered_summary: renderedSummaryText,
      sample_outcomes: {
        P1_05: storedAfterE2e.outcomes['P1-05'].state,
        P5_05: storedAfterE2e.outcomes['P5-05'].state,
        P2_01: storedAfterE2e.outcomes['P2-01'].state,
        P6_01: storedAfterE2e.outcomes['P6-01'].state,
        P4_02: storedAfterE2e.outcomes['P4-02'].state,
        P1_02_self_only: storedAfterE2e.outcomes['P1-02'].state,
        P1_08_pending_only: storedAfterE2e.outcomes['P1-08'].state,
      },
    }
  );

  /* C.1.3 — Built-artifact smoke check with #sim-mastery-policy inlined */
  const artifactPath = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(artifactPath)) {
    const html = fs.readFileSync(artifactPath, 'utf8');
    const allIslandIds = [
      'sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms', 'sim-golden-vectors',
      'sim-terms', 'sim-analytics', 'sim-mastery-policy', 'sim-figures', 'sim-chains',
      'sim-engines', 'sim-graph-scoring', 'sim-method-cards', 'sim-method-engine',
      'sim-exam-policy', 'sim-response-types', 'sim-grading-policy', 'sim-feedback-classification'
    ];
    const parsedIslands = {};
    allIslandIds.forEach((id) => {
      const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)</script>');
      const m = re.exec(html);
      if (m) { parsedIslands[id] = m[1].replace(/<\\\//g, '</'); }
    });
    const scriptMatches = [...html.matchAll(/<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g)];
    const bootstrap = scriptMatches.length ? scriptMatches[0][1] : '';
    const artDoc = makeDom(parsedIslands);
    const artBacking = createStorage();
    const artNet = [];
    const artSb = {
      document: artDoc,
      console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
      encodeURIComponent, decodeURIComponent, unescape,
      performance: { now: () => 0 },
      localStorage: artBacking.storage,
      fetch: (u) => { artNet.push(u); throw new Error('Network forbidden'); },
      XMLHttpRequest: function () { artNet.push('XHR'); throw new Error('Network forbidden'); },
      WebSocket: function () { artNet.push('WS'); throw new Error('Network forbidden'); },
    };
    artSb.globalThis = artSb;
    artSb.window = artSb;
    vm.createContext(artSb);
    vm.runInContext(bootstrap, artSb, { filename: 'output/simulator.html#inline' });
    const smoke = artSb.SimSmoke.lastReport;
    const n26Vec = smoke && smoke.vectors ? smoke.vectors.find((v) => v.id === 'SMK-N26-MASTERY-WALK') : null;
    check('c13_built_artifact_smoke',
      Boolean(parsedIslands['sim-mastery-policy']) &&
      Boolean(smoke && smoke.status === 'PASS' && n26Vec && n26Vec.status === 'PASS' && artNet.length === 0 && Object.keys(artBacking.backing).length === 0),
      {
        total_smoke_vectors: smoke ? smoke.total : 0,
        passed_smoke_vectors: smoke ? smoke.passed : 0,
        n26Vec,
        fresh_prakse_rendered: collectNodeText(artDoc.getElementById('prakse-mastery-topic-1')).indexOf('Nav mēģināts') >= 0,
      }
    );
  } else {
    check('c13_built_artifact_smoke', false, { reason: 'output/simulator.html missing' });
  }

  const report = {
    schema_version: 1,
    task: 'N26',
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks: results,
    failures,
  };

  if (args.record) {
    const outPath = path.isAbsolute(args.record) ? args.record : path.join(repoRoot, args.record);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }
  if (args.fixturesOut) {
    const fixPath = path.isAbsolute(args.fixturesOut) ? args.fixturesOut : path.join(repoRoot, args.fixturesOut);
    fs.mkdirSync(path.dirname(fixPath), { recursive: true });
    fs.writeFileSync(fixPath, JSON.stringify({
      schema_version: 1,
      owner: 'N26',
      note: 'Deterministic view render fixtures for three learner profiles plus the unavailable-outcome corner case (also serves as N32 visual test data).',
      profiles: {
        fresh: { atskats: freshAtskats, prakse: freshPrakse },
        mid_progress: { atskats: midAtskats, prakse: midPrakse },
        near_complete: { atskats: nearAtskats, prakse: nearPrakse },
        unavailable_topic7_corner: { atskats: unavailAtskats, prakse: unavailPrakse },
      },
    }, null, 2) + '\n', 'utf8');
  }

  console.log('N26 runtime: ' + report.status + ' (' + Object.keys(results).length + ' checks, ' + failures.length + ' failures)');
  for (const f of failures) {
    console.error('  FAIL:', f);
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
