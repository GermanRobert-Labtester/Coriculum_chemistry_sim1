#!/usr/bin/env node
/* N30 runtime harness (bounded practice paths):
 *   A.1   policy validation vs live N20 counts (scratch overlong fails naming the topic),
 *         digest determinism (difficulty-declared + difficulty-absent), no-repeat and
 *         current-session exclusion invariants, three entry points over one engine
 *   B.1   shortage triad (eligibility / filter / history exhaustion), skip chain,
 *         grading-to-mastery chain, hint contract + exam-mode boundary
 *   C.1   Phase VI journey (self-assess -> queue -> practice -> miss -> remediate ->
 *         retry -> revise, day boundary mid-journey) + fresh-process replay + smoke
 *
 * Usage:
 *   node tools/check_n30_runtime.js [--repo-root .] [--record PATH] [--trace-out PATH]
 *   node tools/check_n30_runtime.js --replay-only --repo-root .
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

function parseArgs(argv) {
  const args = { repoRoot: path.resolve(__dirname, '..'), record: null, traceOut: null, replayOnly: false };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--trace-out') { args.traceOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--replay-only') { args.replayOnly = true; }
  }
  return args;
}

const readJson = (f) => JSON.parse(fs.readFileSync(f, 'utf8'));
const sha256 = (t) => crypto.createHash('sha256').update(String(t), 'utf8').digest('hex');
const clone = (v) => JSON.parse(JSON.stringify(v));

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

/* ------------------------------------------------------------ minimal DOM */

function makeDom(islands) {
  const registry = Object.create(null);
  function Node(tagName, id) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = []; this.parentNode = null; this.attributes = Object.create(null);
    this.listeners = Object.create(null); this.className = ''; this._id = '';
    this.hidden = false; this.disabled = false; this.type = ''; this.value = ''; this.checked = false;
    this.tabIndex = 0; this._text = '';
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
  Object.defineProperty(Node.prototype, 'firstChild', { get() { return this.childNodes.length ? this.childNodes[0] : null; } });
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
  Node.prototype.dispatchEvent = function (t, ev) { (this.listeners[t] || []).forEach((fn) => fn(ev || { type: t })); return true; };
  Node.prototype.click = function () { this.dispatchEvent('click', { type: 'click' }); };
  Node.prototype.focus = function () { doc.activeElement = this; };
  const doc = {
    documentElement: new Node('html', ''), body: new Node('body', ''), activeElement: null,
    createElement(tag) { return new Node(tag, ''); },
    createElementNS(_n, tag) { return new Node(tag, ''); },
    getElementById(id) { return registry[id] || null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
  };
  const ids = [
    ['sim-header', 'header'], ['sim-main', 'main'], ['sim-footer', 'footer'],
    ['prakse', 'section'], ['prakse-error', 'div'], ['prakse-filter-type', 'select'], ['prakse-filter-unattempted', 'input'],
    ['prakse-tema-1', 'article'], ['prakse-tema-2', 'article'], ['prakse-tema-3', 'article'], ['prakse-tema-4', 'article'],
    ['prakse-tema-5', 'article'], ['prakse-tema-6', 'article'], ['prakse-tema-7', 'article'],
    ['prakse-runner', 'div'], ['prakse-runner-title', 'h4'], ['prakse-runner-progress', 'p'], ['prakse-shortage-banner', 'div'],
    ['prakse-exhausted-panel', 'div'], ['prakse-runner-item-host', 'div'], ['prakse-help-slot', 'div'],
    ['prakse-runner-chain-host', 'div'], ['prakse-runner-term-host', 'div'], ['prakse-runner-feedback', 'div'],
    ['prakse-runner-controls', 'div'], ['prakse-submit-btn', 'button'], ['prakse-skip-btn', 'button'],
    ['prakse-next-btn', 'button'], ['prakse-end-btn', 'button'], ['prakse-summary', 'div'],
    ['atskats-remediation-list', 'ul'], ['atskats-remediation-retry-host', 'div'], ['atskats-remediation-status', 'p'],
    ['atskats-remediation-count', 'p'], ['sim-remediation-error', 'p'],
    ['sim-smoke-status', 'p'],
  ];
  ids.forEach(([id, tag]) => doc.body.appendChild(new Node(tag, id)));
  Object.keys(islands || {}).forEach((id) => {
    const n = new Node('script', id);
    n.setAttribute('type', 'application/json');
    n.textContent = typeof islands[id] === 'string' ? islands[id] : JSON.stringify(islands[id]);
    doc.body.appendChild(n);
  });
  return doc;
}

function loadBank(repoRoot) {
  const dir = path.join(repoRoot, 'data/bank');
  const out = [];
  fs.readdirSync(dir).filter((f) => f.endsWith('.json')).sort().forEach((f) => {
    const raw = readJson(path.join(dir, f));
    if (Array.isArray(raw.questions)) { out.push(...raw.questions); }
  });
  return out;
}

function buildIslands(repoRoot, bank) {
  const figs = [];
  ['data/figures_t12.json', 'data/figures_t23.json', 'data/figures_t4.json', 'data/figures_t5.json', 'data/figures_t67.json'].forEach((rel) => {
    const d = readJson(path.join(repoRoot, rel));
    if (Array.isArray(d.figures)) { figs.push(...d.figures); }
  });
  const rd = (rel) => readJson(path.join(repoRoot, rel));
  return {
    'sim-coverage': rd('data/coverage.json'),
    'sim-conventions': rd('data/conventions.json'),
    'sim-terms': rd('data/terms.json'),
    'sim-bank': { island_id: 'sim-bank', schema_version: 1, bank_version: '1.0.0-n20', status: 'frozen-reviewed-bank', questions: bank },
    'sim-chains': rd('data/chains.json'),
    'sim-analytics': rd('data/analytics_schema.json'),
    'sim-mastery-policy': rd('data/mastery_policy.json'),
    'sim-scheduler-policy': rd('data/scheduler_policy.json'),
    'sim-remediation-policy': rd('data/remediation_policy.json'),
    'sim-revision-policy': rd('data/revision_policy.json'),
    'sim-practice-policy': rd('data/practice_policy.json'),
    'sim-grading-policy': rd('data/grading_policy.json'),
    'sim-feedback-classification': rd('data/feedback_classification.json'),
    'sim-exam-policy': rd('data/exam_policy.json'),
    'sim-response-types': rd('data/response_types.json'),
    'sim-engines': rd('data/engine_taxonomy.json'),
    'sim-graph-scoring': rd('data/graph_scoring_contract.json'),
    'sim-method-cards': rd('data/method_cards.json'),
    'sim-method-engine': rd('data/method_engine_contract.json'),
    'sim-figures': { island_id: 'sim-figures', figures: figs },
    __conceptSummaries: rd('data/concept_summaries.json'),
    __anchorRegistry: rd('data/anchor_registry.json'),
  };
}

function loadEnv(repoRoot, bankOverride) {
  const bank = bankOverride || loadBank(repoRoot);
  const islands = buildIslands(repoRoot, bank);
  const doc = makeDom(islands);
  const netLog = [];
  const sb = {
    console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
    encodeURIComponent, decodeURIComponent, unescape, atob: (s) => Buffer.from(s, 'base64').toString('binary'),
    TextDecoder, Uint8Array, performance: { now: () => 0 },
    document: doc,
    CONCEPT_DRAWER_DATA: islands.__conceptSummaries, ANCHOR_REGISTRY: islands.__anchorRegistry,
    COVERAGE_INVARIANTS: { total: 64, perTopic: { '1': 9, '2': 10, '3': 11, '4': 11, '5': 10, '6': 8, '7': 5 } },
    fetch() { netLog.push('fetch'); throw new Error('Network forbidden'); },
    XMLHttpRequest: function () { netLog.push('XHR'); throw new Error('Network forbidden'); },
    WebSocket: function () { netLog.push('WS'); throw new Error('Network forbidden'); },
  };
  sb.globalThis = sb; sb.window = sb;
  vm.createContext(sb);
  [
    'src/coverage-loader.js', 'src/conventions-loader.js', 'src/terms-loader.js', 'src/prng.js',
    'src/chain-view.js', 'src/variant-templates.js', 'src/variant-engine.js',
    'src/quantity-engine.js', 'src/graph-scoring-engine.js', 'src/method-engine.js',
    'src/compiled/session.js', 'src/compiled/exam.js', 'src/compiled/inputs/registry.js',
    'src/compiled/inputs/integration.js', 'src/compiled/grading.js', 'src/compiled/feedback.js',
    'src/compiled/store.js', 'src/compiled/analytics.js', 'src/compiled/mastery.js',
    'src/compiled/scheduler.js', 'src/compiled/remediation.js', 'src/compiled/revision.js',
    'src/compiled/practice.js',
  ].forEach((rel) => vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sb, { filename: rel }));

  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  sb.SimTerms.setDefault(sb.SimTerms.load(doc));
  sb.SimEngines.load(doc);
  sb.SimInputsRegistry.load(islands['sim-response-types'], islands['sim-terms']);
  sb.SimGraphScoring.load(doc);
  const methodEngine = new sb.SimMethodEngine.MethodEngine(islands['sim-method-engine'], islands['sim-terms']);
  const method = Object.create(methodEngine);
  method.MethodEngine = sb.SimMethodEngine.MethodEngine;
  method.specForVector = sb.SimMethodEngine.specForVector;
  method.sha256 = sb.SimMethodEngine.sha256;

  const qById = Object.create(null);
  bank.forEach((q) => { qById[q.question_id] = q; });
  const termsMap = Object.create(null);
  (islands['sim-terms'].terms || []).forEach((e) => { termsMap[e.key] = e.text_lv; });

  const gradingContext = {
    quantity: sb.SimEngines, method, graph: sb.SimGraphScoring,
    inputsRegistry: sb.SimInputsRegistry, inputsIntegration: sb.SimInputsIntegration,
    figures: sb.SimGraphScoring.state.figures, examPolicy: islands['sim-exam-policy'],
    bank: { instancesById: qById }, terms: termsMap,
    oracle: { oracle_version: 'n30-practice/v1', oracle_digest: sha256('n30'), conventions_digest: sha256(canonical(islands['sim-conventions'])) },
  };
  return { sb, doc, islands, cov, bank, qById, gradingContext, netLog, termsMap };
}

/* ---------------------------------------------------------------- helpers */

function selectedAnswer(env, item, correct) {
  const p = item.payload || {};
  let selected;
  if (correct) { selected = (p.correct_ids || []).slice(); }
  else {
    const wrong = (p.options || []).map((o) => o.option_id).filter((id) => (p.correct_ids || []).indexOf(id) < 0);
    selected = wrong.length ? [wrong[0]] : (p.correct_ids || []).slice(0, 1);
  }
  const contract = env.sb.SimInputsRegistry.contractFor(item.type_id);
  const capture = { selected };
  if (p.requires_justification) { capture.justification = 'Pamatojums treniņam.'; }
  return clone(env.sb.SimInputsIntegration.buildPayload(item.type_id, contract, item, capture));
}

function newStore(env) { return env.sb.SimStore.createStore({ optIn: false, doc: env.doc }); }

function masteryMap(env, store) {
  const mp = env.sb.SimMastery.loadPolicy(env.doc);
  return { map: env.sb.SimMastery.readFromStore(store, env.cov, mp.policy, mp.digest), policy: mp.policy, digest: mp.digest };
}

function pathOptions(env, store, extra) {
  return Object.assign({
    doc: env.doc, store, coverage: env.cov, bankQuestions: env.bank, gradingContext: env.gradingContext,
    sessionAnsweredIds: [],
  }, extra || {});
}

function pathOf(env, entry, history, bank, extra) {
  const P = env.sb.SimPractice;
  const loaded = P.loadPolicy(env.doc, { bankQuestions: env.bank, responseTypes: env.islands['sim-response-types'] });
  return P.computePracticePath(Object.assign({
    entryOrRequest: entry, bankQuestions: bank || env.bank, policy: loaded.policy, coverage: env.cov,
    responseTypes: env.islands['sim-response-types'], history: history || null, doc: env.doc,
  }, extra || {}));
}

/* ------------------------------------------------------------ the journey */

function runJourney(env) {
  const { sb, cov, bank } = env;
  const store = newStore(env);
  const steps = [];
  const rec = (name, data) => steps.push({ step: steps.length + 1, name, ...data });
  const mastery = () => masteryMap(env, store);
  const stateOf = (oid) => mastery().map.outcomes[oid].state;

  const fam = 'FAM-4A';
  const target = cov.outcomes.find((o) => (o.bindings.practice_families || []).indexOf(fam) >= 0).id;
  const mBase = mastery();
  rec('start', { mastery_digest: sb.SimMastery.digestOfMap(mBase.map), target_outcome: target, state: stateOf(target) });

  /* 1. N29 self-assessment: never moves mastery */
  const loadedRev = sb.SimRevision.loadPolicy(env.doc);
  const card = sb.SimRevision.buildSelfAssessmentCardModel(target, { doc: env.doc, store, coverage: cov, policy: loadedRev.policy });
  const ratings = {}; ratings[card.criteria[0].criterion_id] = 'not_yet';
  sb.SimRevision.saveSelfAssessment(store, target, { ratings, note: 'Pirms prakses' }, { coverage: cov, policy: loadedRev.policy, doc: env.doc });
  rec('self_assess', { mastery_digest: sb.SimMastery.digestOfMap(mastery().map), mastery_unchanged: sb.SimMastery.digestOfMap(mastery().map) === steps[0].mastery_digest });

  /* 2. A prior miss on day 5 puts the outcome in the queue (N26 -> N27) */
  const prior = { kind: 'criterion_verdict', outcome_id: target, verdict: 'incorrect', day: 5 };
  store.update((draft) => {
    const cur = sb.SimMastery.normalizeStateMap(draft.mastery, cov, mBase.policy, mBase.digest);
    draft.mastery = sb.SimMastery.reduce(cur, [prior], mBase.policy);
  });
  const schedPol = sb.SimScheduler.loadPolicy(env.doc).policy;
  const queueAt = (day) => sb.SimScheduler.selectQueue({ masteryMap: mastery().map, coverage: cov, date: day, policy: schedPol, bankQuestions: bank, doc: env.doc });
  const q10 = queueAt(10);
  const item10 = q10.queue.find((i) => i.outcome_id === target);
  rec('queue_day10', { queue_ids: q10.queue.map((i) => i.outcome_id), target_reason: item10 ? item10.reason_code : null, target_rank: q10.queue.findIndex((i) => i.outcome_id === target), queue_digest: q10.digest });

  /* 3. Queue entry -> practice path (N27 -> N30) with an outcome-focused type filter */
  const handoff = sb.SimScheduler.buildPracticeHandoff(item10, bank, cov);
  handoff.filters.response_types = ['Q07', 'Q14'];
  const runner = sb.SimPractice.startPath(handoff, pathOptions(env, store, { day: 10 }));
  const p1 = runner.path;
  rec('path_from_queue', { entry: p1.entry_source, true_length: p1.true_length, items: p1.item_ids, digest: p1.digest });

  /* 4. Practice: first item wrong (miss -> N28), second skipped, end early */
  const first = runner.currentItem();
  const r1 = runner.submitAnswer(selectedAnswer(env, first, false));
  rec('practice_miss', {
    instance: first.question_id, verdict: r1.record.verdict_class,
    mastery_effects: r1.mastery_effects, remediation_effects: r1.remediation_effects.map((e) => ({ family: e.family_id, state: e.state, action: e.action || null })),
    mastery_after: stateOf(target),
  });
  const skipped = runner.currentItem();
  runner.skipCurrent();
  const sum1 = runner.endEarly();
  rec('practice_end', { attempted: sum1.attempted_count, incorrect: sum1.incorrect_count, skipped: sum1.skipped_count, skipped_instance: skipped ? skipped.question_id : null, status: sum1.status });

  /* 5. Day boundary (10 -> 12): the queue changes by the declared overdue rule */
  const q12 = queueAt(12);
  const t10 = q10.queue.find((i) => i.outcome_id === target);
  const t12 = q12.queue.find((i) => i.outcome_id === target);
  const lastDay = mastery().map.outcomes[target].last_practiced_day;
  const interval = 1; // box 1 interval (state learning -> box 1)
  rec('day_boundary', {
    queue_day10_digest: q10.digest, queue_day12_digest: q12.digest, queues_differ: q10.digest !== q12.digest,
    last_practiced_day: lastDay, box_interval_days: interval,
    expected_overdue_day12: Math.max(0, (12 - lastDay) - interval),
    observed_overdue_day12: t12 ? t12.overdue_days : null,
    reason_day10: t10 ? t10.reason_code : null, reason_day12: t12 ? t12.reason_code : null,
  });

  /* 6. N28 remediation queue -> alternate-variant retry -> N30 path */
  const rem = store.getState().remediation_queue.filter((e) => e.state !== 'resolved');
  rec('remediation_queue', { open: rem.length, ids: rem.map((e) => e.id), families: rem.map((e) => e.family_id) });
  let retryRes = null;
  if (rem.length > 0) {
    const built = sb.SimRemediation.buildRetryHandoff(rem[0], bank, { doc: env.doc });
    const rr = sb.SimPractice.startPath(built.handoff, pathOptions(env, store, { day: 12 }));
    const item = rr.currentItem();
    const res = rr.submitAnswer(selectedAnswer(env, item, true));
    retryRes = res;
    const after = store.getState().remediation_queue.find((e) => e.id === rem[0].id);
    rec('remediation_retry', {
      entry_source: rr.path.entry_source, retry_instance: item.question_id, selection_source: built.handoff.selection_source,
      excluded: built.handoff.excluded_instance_ids, path_digest: rr.path.digest, verdict: res.record.verdict_class,
      entry_state_after: after.state, retry_count: after.retry_count, mastery_after: stateOf(target),
    });
  }

  /* 7. N29 revision view reflects everything */
  const vm2 = sb.SimRevision.buildRevisionViewModel({ doc: env.doc, store, coverage: cov, masteryMap: mastery().map, bankQuestions: bank, policy: loadedRev.policy });
  let row = null;
  vm2.topics.forEach((t) => t.outcomes.forEach((o) => { if (o.outcome_id === target) { row = o; } }));
  rec('revision_view', {
    total_outcomes: vm2.total_outcomes, outcome_state: row.mastery.effective_state,
    self_rated: row.self_assessment.rated_count, practice_available: row.affordances.practice_available,
  });

  const journeyDigest = sha256(canonical(steps));
  return { steps, digest: journeyDigest, mastery_digest: sb.SimMastery.digestOfMap(mastery().map), store_digest: sb.SimStore.digestValue(store.getState()), retry: retryRes ? true : false, target };
}

/* -------------------------------------------------------------------- main */

function main() {
  const args = parseArgs(process.argv);
  const repoRoot = args.repoRoot;
  if (args.replayOnly) {
    const env = loadEnv(repoRoot);
    const j = runJourney(env);
    process.stdout.write(JSON.stringify({ digest: j.digest, mastery_digest: j.mastery_digest, store_digest: j.store_digest }));
    return;
  }

  const results = {};
  const failures = [];
  function check(id, ok, detail) {
    results[id] = { status: ok ? 'PASS' : 'FAIL', ...(detail || {}) };
    if (!ok) { failures.push(id + ': ' + JSON.stringify(detail || {})); }
  }

  const env = loadEnv(repoRoot);
  const { sb, cov, bank, qById } = env;
  const P = sb.SimPractice;
  const policy = P.loadPolicy(env.doc, { bankQuestions: bank, responseTypes: env.islands['sim-response-types'] }).policy;

  /* A.1 policy validation vs live counts */
  const liveElig = {};
  bank.forEach((q) => { if (P.isReviewEligible(q, false)) { liveElig[q.topic] = (liveElig[q.topic] || 0) + 1; } });
  const scratch = clone(policy);
  scratch.topic_lengths['3'].declared_length = liveElig[3] + 1;
  const scratchRes = P.validatePolicy(scratch, { bankQuestions: bank, responseTypes: env.islands['sim-response-types'] });
  check('A1_policy_live_counts', Object.keys(liveElig).length === 7 && P.validatePolicy(policy, { bankQuestions: bank, responseTypes: env.islands['sim-response-types'] }).valid
    && !scratchRes.valid && scratchRes.errors.some((e) => e.indexOf('topic 3') >= 0),
    { live_eligible: liveElig, declared: Object.fromEntries(Object.entries(policy.topic_lengths).map(([k, v]) => [k, v.declared_length])), scratch_errors: scratchRes.errors });

  /* A.1 determinism: difficulty-declared and difficulty-absent */
  const t3a = pathOf(env, { entry_source: 'topic_browse', topic: 3 });
  const t3b = pathOf(env, { entry_source: 'topic_browse', topic: 3 });
  const noDiff = bank.map((q) => { const c = clone(q); delete c.difficulty; return c; });
  const n1 = pathOf(env, { entry_source: 'topic_browse', topic: 3 }, null, noDiff);
  const n2 = pathOf(env, { entry_source: 'topic_browse', topic: 3 }, null, noDiff);
  const diffRank = { foundational: 0, application: 1, transfer: 2 };
  const monotone = t3a.items.every((it, i) => i === 0 || diffRank[t3a.items[i - 1].difficulty] <= diffRank[it.difficulty]);
  const familyOrdered = n1.items.every((it, i) => i === 0 || (n1.items[i - 1].family_id + n1.items[i - 1].variant_id) <= (it.family_id + it.variant_id));
  check('A1_determinism', t3a.digest === t3b.digest && n1.digest === n2.digest && t3a.difficulty_mode === 'declared' && n1.difficulty_mode === 'absent_family_order' && monotone && familyOrdered && t3a.true_length === 8,
    { declared_digest: t3a.digest, absent_digest: n1.digest, declared_mode: t3a.difficulty_mode, absent_mode: n1.difficulty_mode, ordering_monotone: monotone, family_order: familyOrdered });

  /* A.1.2 no-repeat + half-history exclusion + session exclusion */
  const t1all = bank.filter((q) => q.topic === 1).map((q) => q.question_id).sort();
  const half = t1all.filter((_, i) => i % 2 === 0);
  const unHalf = pathOf(env, { entry_source: 'topic_browse', topic: 1, filters: { topic: 1, unattempted_only: true } }, { attempted_instance_ids: half });
  const noOverlap = unHalf.item_ids.every((id) => half.indexOf(id) < 0);
  const unique = new Set(unHalf.item_ids).size === unHalf.item_ids.length;
  const allowed = new Set(t1all.filter((id) => half.indexOf(id) < 0));
  const sessionIds = unHalf.item_ids.slice(0, 2);
  const withSession = pathOf(env, { entry_source: 'topic_browse', topic: 1 }, { session_answered_ids: sessionIds });
  check('A1_no_repeat_exclusions', noOverlap && unique && unHalf.item_ids.every((id) => allowed.has(id)) && unHalf.excluded_count === half.length
    && withSession.item_ids.every((id) => sessionIds.indexOf(id) < 0) && withSession.excluded_count === 2,
    { history_size: half.length, excluded: unHalf.excluded_count, path: unHalf.item_ids, session_excluded: sessionIds, session_path_excludes: withSession.item_ids.every((id) => sessionIds.indexOf(id) < 0) });

  /* A.1.3 three entry points over one engine */
  const schedPol = sb.SimScheduler.loadPolicy(env.doc).policy;
  const mm = masteryMap(env, newStore(env));
  const queue = sb.SimScheduler.selectQueue({ masteryMap: mm.map, coverage: cov, date: 10, policy: schedPol, bankQuestions: bank, doc: env.doc });
  const handoff = sb.SimScheduler.buildPracticeHandoff(queue.queue[0], bank, cov);
  const schedPath = pathOf(env, handoff);
  const entryTopic = pathOf(env, { entry_source: 'topic_browse', topic: handoff.topic, filters: { topic: handoff.topic, outcome_id: handoff.outcome_id } });
  const storeR = newStore(env);
  const missInst = qById['COL1-4-4A-A-01'];
  const added = sb.SimRemediation.addMiss(storeR, {
    slot_id: 'S4-1', topic: 4, family_id: 'FAM-4A', outcome_id: cov.outcomes.find((o) => (o.bindings.practice_families || []).indexOf('FAM-4A') >= 0).id,
    outcome_ids: missInst.outcome_ids, instance_id: missInst.question_id, concept_ids: [missInst.outcome_ids[0]], chain_ids: [], graded_digest: sb.SimStore.digestValue({ n30: 'entry' }),
  }, { doc: env.doc });
  const built = sb.SimRemediation.buildRetryHandoff(added.entry, bank, { doc: env.doc });
  const retryPath = pathOf(env, built.handoff);
  check('A1_three_entry_points', schedPath.entry_source === 'scheduler_queue' && entryTopic.entry_source === 'topic_browse' && retryPath.entry_source === 'remediation_retry'
    && retryPath.true_length === 1 && retryPath.items[0].family_id === 'FAM-4A' && retryPath.item_ids[0] !== missInst.question_id
    && schedPath.items.every((it) => it.outcome_ids.indexOf(handoff.outcome_id) >= 0) && P.computePracticePath.length === 1,
    { scheduler: { outcome: handoff.outcome_id, length: schedPath.true_length, digest: schedPath.digest },
      topic_browse: { length: entryTopic.true_length, digest: entryTopic.digest },
      remediation_retry: { family: 'FAM-4A', retry_instance: retryPath.item_ids[0], excluded: built.handoff.excluded_instance_ids, digest: retryPath.digest },
      single_engine_function: 'SimPractice.computePracticePath' });

  /* B.1 shortage triad */
  const pend = bank.map((q) => clone(q));
  let cnt = 0;
  pend.forEach((q) => { if (q.topic === 1 && cnt < 12) { q.review.content = 'pending'; cnt += 1; } });
  const sPend = pathOf(env, { entry_source: 'topic_browse', topic: 1 }, null, pend);
  const sFilter = pathOf(env, { entry_source: 'topic_browse', topic: 1, filters: { topic: 1, response_types: ['Q06'] } });
  const allT1 = t1all;
  const sExh = pathOf(env, { entry_source: 'topic_browse', topic: 1, filters: { topic: 1, unattempted_only: true } }, { attempted_instance_ids: allT1 });
  const pendIds = new Set(pend.filter((q) => q.review.content === 'pending').map((q) => q.question_id));
  check('B1_shortage_triad',
    sPend.true_length === 4 && sPend.shortage_reason === 'pending_review' && /4 no 6/.test(sPend.shortage_copy_lv) && /gaida recenziju/.test(sPend.shortage_copy_lv) && sPend.item_ids.every((id) => !pendIds.has(id))
    && sFilter.true_length === 2 && sFilter.shortage_reason === 'filter_shortage' && new Set(sFilter.item_ids).size === 2
    && sExh.true_length === 0 && sExh.shortage_reason === 'history_exhausted' && sExh.exit_options && /1 \/ 3 \/ 7/.test(sExh.shortage_copy_lv) && /efemēr/.test(sExh.shortage_copy_lv)
    && /Leitner/.test(sExh.exit_options.scheduler_intervals_note_lv) && sExh.exit_options.ephemeral_available === true,
    { eligibility: { length: sPend.true_length, reason_copy: sPend.shortage_copy_lv, pending_excluded: sPend.pending_review_count },
      filter: { length: sFilter.true_length, reason_copy: sFilter.shortage_copy_lv },
      exhausted: { length: sExh.true_length, copy: sExh.shortage_copy_lv, exits: sExh.exit_options } });

  /* B.1.1 exhausted state renders without dead end */
  const exStore = newStore(env);
  const exRunner = P.createRunner(sExh, { doc: env.doc, store: exStore, coverage: cov, bankQuestions: bank });
  const exPanel = env.doc.getElementById('prakse-exhausted-panel');
  const exText = exPanel.textContent + ' ' + env.doc.getElementById('prakse-shortage-banner').textContent;
  check('B1_exhausted_exit_dignity', exRunner.snapshot().status === 'exhausted' && !exPanel.hidden && /Leitner/.test(exText) && /efemēr/.test(exText) && env.doc.getElementById('prakse-ephemeral-btn') !== null,
    { status: exRunner.snapshot().status, panel_text: exText });

  /* B.1 skip chain: three skips -> three skipped, zero incorrect */
  const skStore = newStore(env);
  const skMastery = sb.SimMastery.digestOfMap(masteryMap(env, skStore).map);
  const skRunner = P.startPath({ entry_source: 'topic_browse', topic: 1 }, pathOptions(env, skStore));
  skRunner.skipCurrent(); skRunner.skipCurrent(); skRunner.skipCurrent();
  const skSum = skRunner.getSummary();
  const skRem = skStore.getState().remediation_queue.length;
  check('B1_skip_chain', skSum.skipped_count === 3 && skSum.incorrect_count === 0 && skSum.attempted_count === 0 && skSum.records.filter((r) => r.status === 'skipped' && r.verdict_class === null).length === 3
    && sb.SimMastery.digestOfMap(masteryMap(env, skStore).map) === skMastery && skRem === 0,
    { skipped: skSum.skipped_count, incorrect: skSum.incorrect_count, mastery_unchanged: true, remediation_entries: skRem });

  /* B.1.2 grading chain parity: practice verdict == independent N23->N26 recompute */
  const chStore = newStore(env);
  const chRunner = P.startPath({ entry_source: 'topic_browse', topic: 4, filters: { topic: 4, response_types: ['Q07'] } }, pathOptions(env, chStore, { day: 3 }));
  const chItem = chRunner.currentItem();
  const before = masteryMap(env, chStore);
  const chRes = chRunner.submitAnswer(selectedAnswer(env, chItem, true));
  const full = chRes.full_record;
  const mp = sb.SimMastery.loadPolicy(env.doc);
  const events = sb.SimMastery.extractCriterionEvents(full, cov, { day: 3 });
  const independent = sb.SimMastery.reduce(before.map, events, mp.policy);
  const after = masteryMap(env, chStore);
  const taskEvents = chStore.getState().events.filter((e) => e.event === 'task-answered');
  check('B1_grading_chain', sb.SimMastery.digestOfMap(after.map) === sb.SimMastery.digestOfMap(independent) && events.length > 0 && taskEvents.length === 1
    && full.record_kind === 'graded-record' && sb.SimGrading.digestOf(Object.assign({}, full, { digest: undefined })) !== undefined && chStore.getState().practice_history.attempted_instance_ids.indexOf(chItem.question_id) >= 0,
    { instance: chItem.question_id, verdict: chRes.record.verdict_class, mastery_events: events.length, mastery_digest_after: sb.SimMastery.digestOfMap(after.map), independent_matches: true, graded_digest: full.digest });

  /* B.1.3 hint contract + exam boundary in runner context */
  const pathT1 = pathOf(env, { entry_source: 'topic_browse', topic: 1 });
  const help = P.describeHelpContract(pathT1.items[0], { mode: 'practice', doc: env.doc, coverage: cov });
  const examErr = captureError(() => P.describeHelpContract(pathT1.items[0], { mode: 'exam', doc: env.doc, coverage: cov }));
  const rnr = P.createRunner(pathT1, { doc: env.doc, store: newStore(env), coverage: cov, bankQuestions: bank, mode: 'practice' });
  const helpDom = env.doc.getElementById('prakse-runner-help');
  const helpMarkers = helpDom ? helpDom.childNodes.map((n) => n.getAttribute('data-sim-component')).filter(Boolean) : [];
  const examReg = sb.SimExam.createModeRegistry(env.islands['sim-exam-policy'].view_discipline);
  examReg.setMode('exam');
  const examForbids = ['hint', 'chain', 'term-lookup'].every((c) => !examReg.isAllowed(c));
  check('B1_hint_and_mode_boundary', help.help_enabled && helpMarkers.indexOf('hint') >= 0 && helpMarkers.indexOf('term-lookup') >= 0 && examErr && examErr.code === 'E_MODE_COMPONENT_NOT_ALLOWED' && examForbids && !!rnr,
    { practice_markers: helpMarkers, exam_error: examErr, exam_forbids_help: examForbids, chain_for_family: help.chain_id });

  /* C.1 journey + replay */
  const journey = runJourney(env);
  const j2 = runJourney(loadEnv(repoRoot));
  const replay = JSON.parse(execFileSync('node', [__filename, '--replay-only', '--repo-root', repoRoot], { encoding: 'utf8' }));
  const byName = Object.fromEntries(journey.steps.map((s) => [s.name, s]));
  const db = byName.day_boundary;
  check('C1_journey_modules', byName.self_assess.mastery_unchanged && byName.queue_day10.target_rank === 0 && byName.path_from_queue.entry === 'scheduler_queue'
    && byName.practice_miss.verdict !== 'correct' && byName.practice_end.skipped === 1 && byName.practice_end.incorrect >= 1
    && byName.remediation_queue.open >= 1 && byName.remediation_retry && byName.remediation_retry.entry_source === 'remediation_retry'
    && ['correct', 'auto_passed_pending_review'].indexOf(byName.remediation_retry.verdict) >= 0 && byName.remediation_retry.entry_state_after === 'retried'
    && byName.revision_view.total_outcomes === 64 && byName.revision_view.self_rated >= 1,
    { steps: journey.steps.map((s) => s.name) });
  check('C1_day_boundary_declared_rule', db.queues_differ && db.expected_overdue_day12 === db.observed_overdue_day12 && db.observed_overdue_day12 > 0,
    { queue_day10_digest: db.queue_day10_digest, queue_day12_digest: db.queue_day12_digest, expected_overdue: db.expected_overdue_day12, observed_overdue: db.observed_overdue_day12, reason_day10: db.reason_day10, reason_day12: db.reason_day12 });
  check('C1_replay_parity', journey.digest === j2.digest && journey.digest === replay.digest && journey.mastery_digest === replay.mastery_digest && journey.store_digest === replay.store_digest,
    { journey_digest: journey.digest, in_process_rerun: j2.digest, fresh_process: replay.digest, mastery_digest: journey.mastery_digest, store_digest: journey.store_digest });

  /* privacy / network */
  check('C1_no_network', env.netLog.length === 0, { attempts: env.netLog.length });

  /* smoke vector over the built artifact when present */
  let smoke = { status: 'SKIPPED' };
  const artifact = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(artifact)) {
    const html = fs.readFileSync(artifact, 'utf8');
    const islandMatches = {};
    const reIsland = /<script\s+type="application\/json"\s+id="([^"]+)">([\s\S]*?)<\/script>/g;
    let im;
    while ((im = reIsland.exec(html)) !== null) {
      islandMatches[im[1]] = im[2].replace(/<\\\//g, '</');
    }
    const builtDoc = makeDom(islandMatches);
    const scriptMatches = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
    const execScript = scriptMatches.length ? scriptMatches[scriptMatches.length - 1][1] : '';
    const builtSb = {
      console,
      document: builtDoc,
      window: null,
      Object, Array, String, Number, Boolean, BigInt, Math, JSON, Date, RegExp, Error, TypeError, RangeError, Map, Set,
      parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent, unescape,
      atob: (s) => Buffer.from(s, 'base64').toString('binary'),
      TextDecoder, Uint8Array,
      performance: { now: () => 0 },
    };
    builtSb.window = builtSb;
    builtSb.globalThis = builtSb;
    vm.createContext(builtSb);
    vm.runInContext(execScript, builtSb, { filename: 'output/simulator.html' });
    const smokeReport = builtSb.SimSmoke.run(builtDoc, {
      coverage: builtSb.SimCoverage.load(builtDoc, builtSb.COVERAGE_INVARIANTS),
      expected: builtSb.COVERAGE_INVARIANTS,
      onLoad: true,
    });
    const n30Vec = (smokeReport.vectors || []).find((v) => v.id === 'SMK-N30-PRACTICE-PATH');
    smoke = {
      status: smokeReport.status === 'PASS' && n30Vec && n30Vec.status === 'PASS' ? 'PASS' : 'FAIL',
      total: smokeReport.total,
      passed: smokeReport.passed,
      n30_vector: n30Vec || null,
    };
    if (smoke.status !== 'PASS') { failures.push('artifact: ' + JSON.stringify(smoke)); }
  }
  results.artifact = smoke;

  /* in-file smoke vector executed against the shared env */
  const smokeSrc = fs.readFileSync(path.join(repoRoot, 'src/smoke-subset.js'), 'utf8');
  vm.runInContext(smokeSrc, env.sb, { filename: 'src/smoke-subset.js' });
  const sm = env.sb.SimSmoke.vectors.find((v) => v.id === 'SMK-N30-PRACTICE-PATH');
  const smOut = sm ? sm.run(env.doc, { coverage: cov }) : { status: 'FAIL', reason: 'vector missing' };
  check('C1_smoke_vector', smOut.status === 'PASS', smOut);

  const record = {
    schema_version: 1, task: 'N30', status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks: results, failures,
    journey: { digest: journey.digest, steps: journey.steps.length, mastery_digest: journey.mastery_digest, store_digest: journey.store_digest },
  };
  if (args.record) { fs.mkdirSync(path.dirname(path.resolve(args.record)), { recursive: true }); fs.writeFileSync(args.record, JSON.stringify(record, null, 2) + '\n'); }
  if (args.traceOut) { fs.mkdirSync(path.dirname(path.resolve(args.traceOut)), { recursive: true }); fs.writeFileSync(args.traceOut, JSON.stringify({ digest: journey.digest, replay_digest: replay.digest, steps: journey.steps }, null, 2) + '\n'); }
  process.stdout.write('N30 runtime: ' + record.status + ' (' + Object.keys(results).length + ' checks, journey ' + journey.digest.slice(0, 16) + ')\n');
  failures.forEach((f) => process.stderr.write('  FAIL ' + f + '\n'));
  process.exit(failures.length === 0 ? 0 : 1);
}

main();
