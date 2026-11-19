#!/usr/bin/env node
/* N27 runtime, Leitner box round-trip, day-clock, property fixtures (determinism,
 * cap, exclusion, tie-break, fresh learner), N24 availability exclusion, term-keyed
 * render fixture, end-to-end N30 handoff + post-session recompute, and built-artifact
 * smoke harness.
 *
 * Usage:
 *   node tools/check_n27_runtime.js [--repo-root .] [--record PATH] [--render-out PATH]
 *   node tools/check_n27_runtime.js --determinism-only --repo-root .
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
    renderOut: null,
    determinismOnly: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--render-out') { args.renderOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--determinism-only') { args.determinismOnly = true; }
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
    'sim-coverage-error', 'sim-mastery-error', 'sim-scheduler-error',
    'atskats', 'atskats-mastery-wrap', 'atskats-mastery-heading', 'atskats-mastery-honesty',
    'atskats-mastery-fresh-note', 'atskats-mastery-summary', 'atskats-mastery-topics',
    'prakse', 'prakse-scheduler-panel', 'prakse-scheduler-heading', 'prakse-scheduler-honesty',
    'prakse-scheduler-status', 'prakse-scheduler-queue', 'prakse-scheduler-topics', 'prakse-scheduler-handoff',
    'prakse-mastery-panel', 'prakse-mastery-honesty', 'prakse-mastery-topics',
    'sim-smoke-status'
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
  const api = {
    getItem(k) { return Object.prototype.hasOwnProperty.call(backing, k) ? backing[k] : null; },
    setItem(k, v) { backing[String(k)] = String(v); },
    removeItem(k) { delete backing[String(k)]; },
    get length() { return Object.keys(backing).length; },
    key(i) { return Object.keys(backing)[i] || null; },
  };
  return { storage: api, backing };
}

function loadSchedulerStandalone(repoRoot, islands, backingStorage) {
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
    'src/terms-loader.js',
    'src/bank-loader.js',
    'src/compiled/store.js',
    'src/compiled/analytics.js',
    'src/compiled/mastery.js',
    'src/compiled/scheduler.js',
  ];
  for (const rel of files) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sb, { filename: rel });
  }
  return { sb, doc, netLog };
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

function buildDeterminismState(sb, cov, mLoaded) {
  const base = sb.SimMastery.createInitialStateMap(cov, mLoaded.policy, mLoaded.digest);
  const events = [
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'incorrect', day: 5 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 6 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 6 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'decay', outcome_id: 'P4-01', days_inactive: 14 },
    { kind: 'criterion_verdict', outcome_id: 'P5-05', verdict: 'correct', day: 11 },
  ];
  return sb.SimMastery.reduce(base, events, mLoaded.policy);
}

function runDeterminismOnly(repoRoot) {
  const islands = {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-terms': readJson(path.join(repoRoot, 'data/terms.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
    'sim-scheduler-policy': readJson(path.join(repoRoot, 'data/scheduler_policy.json')),
  };
  const { sb, doc } = loadSchedulerStandalone(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const mLoaded = sb.SimMastery.loadPolicy(doc);
  const sLoaded = sb.SimScheduler.loadPolicy(doc);
  const stateMap = buildDeterminismState(sb, cov, mLoaded);
  const sel = sb.SimScheduler.selectQueue({
    masteryMap: stateMap,
    coverage: cov,
    date: 12,
    policy: sLoaded.policy,
    doc,
  });
  process.stdout.write(JSON.stringify({
    digest: sel.digest,
    queue_ids: sel.queue.map((q) => q.outcome_id),
    queue: sel.queue,
  }));
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
  if (args.determinismOnly) {
    runDeterminismOnly(args.repoRoot);
    return;
  }

  const repoRoot = args.repoRoot;
  const results = {};
  const failures = [];
  function check(id, ok, detail) {
    results[id] = { status: ok ? 'PASS' : 'FAIL', ...(detail || {}) };
    if (!ok) { failures.push(id + ': ' + JSON.stringify(detail || {})); }
  }

  const islands = {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-conventions': readJson(path.join(repoRoot, 'data/conventions.json')),
    'sim-terms': readJson(path.join(repoRoot, 'data/terms.json')),
    'sim-analytics': readJson(path.join(repoRoot, 'data/analytics_schema.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
    'sim-scheduler-policy': readJson(path.join(repoRoot, 'data/scheduler_policy.json')),
  };
  const bankQuestions = loadAllBankQuestions(repoRoot);
  islands['sim-bank'] = { island_id: 'sim-bank', schema_version: 1, bank_version: '1.0.0-n20', status: 'frozen-reviewed-bank', questions: bankQuestions };

  const { sb, doc, netLog } = loadSchedulerStandalone(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const mLoaded = sb.SimMastery.loadPolicy(doc);
  const sLoaded = sb.SimScheduler.loadPolicy(doc);
  const sPolicy = sLoaded.policy;
  const mPolicy = mLoaded.policy;
  const termsMap = sb.SimScheduler.resolveTermsMap(doc);

  /* A.1.1 — Non-increasing interval pair fails naming boxes */
  const scratchBad = JSON.parse(JSON.stringify(sPolicy));
  scratchBad.boxes[1].interval_days = 1; // box 1 = 1d, box 2 = 1d
  const badRep = sb.SimScheduler.validatePolicy(scratchBad);
  check('a11_non_increasing_interval_refusal',
    !badRep.valid &&
    badRep.non_increasing_pairs.length === 1 &&
    badRep.errors.some((e) => e.indexOf('box 1') >= 0 && e.indexOf('box 2') >= 0),
    { non_increasing_pairs: badRep.non_increasing_pairs, errors: badRep.errors }
  );

  /* A.1.2 — Injectable day-clock contract: two dates a week apart yield different queues */
  const d1Iso = '2026-11-10';
  const d2Iso = '2026-11-17';
  const dayNov08 = sb.SimScheduler.toDayNumber('2026-11-08');
  const dayNov09 = sb.SimScheduler.toDayNumber('2026-11-09');
  const clock1 = sb.SimScheduler.createFixedDayClock(d1Iso);
  const clock2 = sb.SimScheduler.createFixedDayClock(d2Iso);
  const defClock = sb.SimScheduler.defaultDayClock();

  const clockBase = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const clockMap = sb.SimMastery.reduce(clockBase, [
    // P1-01: learning (box 1, 1d), practiced Nov 08 -> overdue 1d on Nov 10, 8d on Nov 17
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: dayNov08 },
    // P2-01: near_mastered (box 2, 3d), practiced Nov 08 -> NOT due on Nov 10 (2d<3d), overdue 6d on Nov 17
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'correct', day: dayNov08 },
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'correct', day: dayNov08 },
    // P3-01: mastered (box 3, 7d), practiced Nov 08 -> NOT due on Nov 10 (2d<7d), overdue 2d on Nov 17
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: dayNov08 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: dayNov08 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: dayNov08 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: dayNov08 },
    // P4-01: near_mastered (box 2, 3d), practiced Nov 09 -> NOT due on Nov 10 (1d<3d), overdue 5d on Nov 17
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: dayNov09 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: dayNov09 },
  ], mPolicy);

  const qWeek1 = sb.SimScheduler.selectQueue({ masteryMap: clockMap, coverage: cov, clock: clock1, policy: sPolicy, bankQuestions, doc });
  const qWeek2 = sb.SimScheduler.selectQueue({ masteryMap: clockMap, coverage: cov, clock: clock2, policy: sPolicy, bankQuestions, doc });
  const w1Overdue = qWeek1.queue.filter((x) => x.reason_code === 'overdue').map((x) => x.outcome_id);
  const w2Overdue = qWeek2.queue.filter((x) => x.reason_code === 'overdue').map((x) => x.outcome_id);
  const invalidDateErr = captureError(() => sb.SimScheduler.toDayNumber('2026-02-30'));

  check('a12_day_clock_week_apart_fixture',
    typeof defClock.todayDay() === 'number' &&
    /^\d{4}-\d{2}-\d{2}$/.test(defClock.todayIso()) &&
    invalidDateErr && invalidDateErr.code === 'E_SCHEDULER_INVALID_DATE' &&
    qWeek1.digest !== qWeek2.digest &&
    w1Overdue.length === 1 && w1Overdue[0] === 'P1-01' &&
    w2Overdue.length === 4 && w2Overdue.join(',') === 'P1-01,P2-01,P4-01,P3-01',
    {
      date_week1: d1Iso,
      date_week2: d2Iso,
      week1_overdue: w1Overdue,
      week2_overdue: w2Overdue,
      week1_queue: qWeek1.queue.map((q) => ({ id: q.outcome_id, reason: q.reason_code, overdue_days: q.overdue_days })),
      week2_queue: qWeek2.queue.map((q) => ({ id: q.outcome_id, reason: q.reason_code, overdue_days: q.overdue_days })),
      invalid_date_error: invalidDateErr ? invalidDateErr.code : null,
    }
  );

  /* A.1.3 — Box mapping & mastery transition round trip */
  const rtEvents = [
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 2 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 3 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 4 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 5 },
    { kind: 'decay', outcome_id: 'P1-01', days_inactive: 14 },
    { kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 20 },
  ];
  let rtCur = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const rtSteps = [{ state: rtCur.outcomes['P1-01'].state, event: 'initial', day: null }];
  for (const ev of rtEvents) {
    rtCur = sb.SimMastery.reduce(rtCur, [ev], mPolicy);
    rtSteps.push({
      state: rtCur.outcomes['P1-01'].state,
      event: ev.kind === 'decay' ? 'decay(14d)' : ev.verdict,
      day: ev.day || null,
    });
  }
  const boxHistory = sb.SimScheduler.traceBoxHistory(rtSteps, sPolicy);
  const boxNums = boxHistory.map((b) => b.box);
  check('a13_box_mapping_round_trip',
    JSON.stringify(boxNums) === JSON.stringify([1, 1, 1, 2, 2, 3, 1, 1]) &&
    boxHistory[5].state === 'mastered' && boxHistory[5].box === 3 &&
    boxHistory[6].state === 'needs_review' && boxHistory[6].box === 1 &&
    boxHistory[7].state === 'learning' && boxHistory[7].box === 1,
    { box_history: boxHistory }
  );

  /* B.1 & B.1.1 — Property fixture set: determinism (2 runs + fresh process), cap, exclusion, tie-break, fresh learner */
  const detMap = buildDeterminismState(sb, cov, mLoaded);
  const det1 = sb.SimScheduler.selectQueue({ masteryMap: detMap, coverage: cov, date: 12, policy: sPolicy, doc });
  const det2 = sb.SimScheduler.selectQueue({ masteryMap: detMap, coverage: cov, date: 12, policy: sPolicy, doc });
  const freshChild = JSON.parse(execFileSync('node', [__filename, '--determinism-only', '--repo-root', repoRoot], { encoding: 'utf8' }));

  // Cap: 15 overdue outcomes -> exactly queue_cap (5)
  const capEvents = [];
  const fifteenIds = cov.outcomes.slice(0, 15).map((o) => o.id);
  fifteenIds.forEach((oid, idx) => {
    capEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'incorrect', day: 1 + (idx % 3) });
  });
  const capMap = sb.SimMastery.reduce(sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest), capEvents, mPolicy);
  const capRes = sb.SimScheduler.selectQueue({ masteryMap: capMap, coverage: cov, date: 20, policy: sPolicy, bankQuestions, doc });

  // Exclusion: P1-01 maximally overdue, marked unavailable in scratch availability map -> never appears
  const scratchAvail = {};
  cov.outcomes.forEach((o) => { scratchAvail[o.id] = { available: o.id !== 'P1-01', eligible_count: o.id !== 'P1-01' ? 4 : 0 }; });
  const exclRes = sb.SimScheduler.selectQueue({ masteryMap: capMap, coverage: cov, date: 20, policy: sPolicy, availability: scratchAvail, doc });

  // Tie-break: 5 outcomes with exact equal overdueness inserted in scrambled order
  const tieBase = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const tieScrambled = ['P6-03', 'P2-05', 'P1-09', 'P4-02', 'P3-01'];
  const tieEvents = tieScrambled.map((oid) => ({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'incorrect', day: 4 }));
  const tieMap = sb.SimMastery.reduce(tieBase, tieEvents, mPolicy);
  const tieRes = sb.SimScheduler.selectQueue({ masteryMap: tieMap, coverage: cov, date: 10, policy: sPolicy, bankQuestions, doc });
  const tieIds = tieRes.queue.map((q) => q.outcome_id);

  // Fresh learner: all 64 unseen -> non-empty queue in topic order (P1-01..P1-05)
  const freshMap = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const freshRes = sb.SimScheduler.selectQueue({ masteryMap: freshMap, coverage: cov, date: 1, policy: sPolicy, bankQuestions, doc });
  const freshIds = freshRes.queue.map((q) => q.outcome_id);

  // Least-recently-practiced tier: all 64 practiced today/recently, none overdue -> oldest practiced first
  const lrpEvents = [];
  cov.outcomes.forEach((o, idx) => {
    lrpEvents.push({ kind: 'criterion_verdict', outcome_id: o.id, verdict: 'correct', day: 10 });
    if (idx < 60) {
      // Advance first 60 to mastered (box 3, interval 7d) at day 10..12
      lrpEvents.push({ kind: 'criterion_verdict', outcome_id: o.id, verdict: 'correct', day: 11 });
      lrpEvents.push({ kind: 'criterion_verdict', outcome_id: o.id, verdict: 'correct', day: 11 });
      lrpEvents.push({ kind: 'criterion_verdict', outcome_id: o.id, verdict: 'correct', day: 12 });
    }
  });
  // Actually keep P7-01..P7-04 practiced on day 12 (mastered, box 3 -> due day 19),
  // P1-01..P1-05 practiced on day 15 (mastered, box 3 -> due day 22) and all others on day 16
  const lrpBase = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const lrpEv2 = [];
  cov.outcomes.forEach((o) => {
    let d = 16;
    if (o.id === 'P7-02' || o.id === 'P7-01' || o.id === 'P5-04' || o.id === 'P3-03' || o.id === 'P2-04') { d = 12; }
    for (let k = 0; k < 4; k += 1) { lrpEv2.push({ kind: 'criterion_verdict', outcome_id: o.id, verdict: 'correct', day: d }); }
  });
  const lrpMap = sb.SimMastery.reduce(lrpBase, lrpEv2, mPolicy);
  const lrpRes = sb.SimScheduler.selectQueue({ masteryMap: lrpMap, coverage: cov, date: 17, policy: sPolicy, bankQuestions, doc });
  const lrpIds = lrpRes.queue.map((q) => q.outcome_id);

  check('b11_property_fixtures_and_fresh_corner',
    det1.digest === det2.digest &&
    det1.digest === freshChild.digest &&
    capRes.queue.length === 5 &&
    !exclRes.queue.some((q) => q.outcome_id === 'P1-01') &&
    exclRes.excluded.some((e) => e.outcome_id === 'P1-01' && e.reason_code === 'unavailable') &&
    tieIds.join(',') === 'P1-09,P2-05,P3-01,P4-02,P6-03' &&
    freshIds.join(',') === 'P1-01,P1-02,P1-03,P1-04,P1-05' &&
    freshRes.queue.every((q) => q.overdue_days === 0 && q.reason_code === 'new' && q.box === 1) &&
    lrpIds.join(',') === 'P2-04,P3-03,P5-04,P7-01,P7-02' &&
    lrpRes.queue.every((q) => q.reason_code === 'least_recently_practiced'),
    {
      determinism_digests: { run1: det1.digest, run2: det2.digest, fresh_process: freshChild.digest },
      cap_output: capRes.queue.map((q) => ({ outcome_id: q.outcome_id, overdue_days: q.overdue_days })),
      exclusion_output: {
        queue_ids: exclRes.queue.map((q) => q.outcome_id),
        excluded_ids: exclRes.excluded.map((e) => e.outcome_id),
      },
      tie_break_output: tieRes.queue.map((q) => ({ outcome_id: q.outcome_id, overdue_days: q.overdue_days })),
      fresh_learner_output: freshRes.queue.map((q) => ({ outcome_id: q.outcome_id, reason_code: q.reason_code, box: q.box })),
      least_recently_practiced_output: lrpRes.queue.map((q) => ({ outcome_id: q.outcome_id, last_practiced_day: q.last_practiced_day, reason_code: q.reason_code })),
    }
  );

  /* B.1.2 — N24 form-eligible family availability integration fixture */
  const t7PendingBank = bankQuestions.map((q) => {
    if (q.topic === 7) {
      const clone = JSON.parse(JSON.stringify(q));
      clone.review = { accessibility: 'pending', calculation: 'passed', content: 'passed', source: 'passed' };
      return clone;
    }
    return q;
  });
  const famAvailT7 = sb.SimScheduler.computeFamilyAvailability(cov, t7PendingBank, sPolicy, termsMap);
  // Make P7-01..P7-05 maximally overdue in mastery map, yet excluded because families are unreviewed
  const t7OverdueEvents = ['P7-01', 'P7-02', 'P7-03', 'P7-04', 'P7-05'].map((oid) => ({
    kind: 'criterion_verdict', outcome_id: oid, verdict: 'incorrect', day: 1
  }));
  const t7OverdueMap = sb.SimMastery.reduce(freshMap, t7OverdueEvents, mPolicy);
  const t7ExclQueue = sb.SimScheduler.selectQueue({
    masteryMap: t7OverdueMap,
    coverage: cov,
    date: 20,
    policy: sPolicy,
    familyAvailability: famAvailT7.by_family,
    doc,
  });
  const t7ExcludedIds = t7ExclQueue.excluded.map((e) => e.outcome_id).sort();

  check('b12_n24_family_availability_exclusion',
    !famAvailT7.by_family['FAM-7A'].available &&
    !famAvailT7.by_family['FAM-7B'].available &&
    !t7ExclQueue.queue.some((q) => q.topic === 7) &&
    t7ExcludedIds.join(',') === 'P7-01,P7-02,P7-03,P7-04,P7-05' &&
    t7ExclQueue.excluded.every((e) => e.reason_code === 'unavailable' && typeof e.reason_lv === 'string' && e.reason_lv.length > 0),
    {
      unreviewed_t7_families: ['FAM-7A', 'FAM-7B', 'FAM-7C', 'FAM-7D'].map((f) => ({ family: f, available: famAvailT7.by_family[f].available, pending: famAvailT7.by_family[f].pending_count })),
      excluded_outcomes: t7ExclQueue.excluded,
      offered_queue_ids: t7ExclQueue.queue.map((q) => q.outcome_id),
    }
  );

  /* B.1.3 — Term-keyed Latvian render fixture (also doubles as N32 test data) */
  const renderBase = sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest);
  const renderMap = sb.SimMastery.reduce(renderBase, [
    // P4-01: needs_review (box 1, 1d), last_practiced day 1 -> overdue by 18d at day 20
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
    { kind: 'decay', outcome_id: 'P4-01', days_inactive: 14 },
    // P2-01: learning (box 1, 1d), practiced day 16 -> overdue by 3d at day 20
    { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'incorrect', day: 16 },
    // P3-01: near_mastered (box 2, 3d), practiced day 17 -> due_today at day 20
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 17 },
    { kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 17 },
  ], mPolicy);
  const renderSel = sb.SimScheduler.selectQueue({
    masteryMap: renderMap,
    coverage: cov,
    date: '2026-11-19',
    policy: sPolicy,
    bankQuestions,
    doc,
  });
  // Actually use integer day 20 so last_practiced_day 1/16/17 aligns cleanly
  const renderSelDay20 = sb.SimScheduler.selectQueue({
    masteryMap: renderMap,
    coverage: cov,
    date: 20,
    policy: sPolicy,
    bankQuestions,
    doc,
  });
  const renderVm = sb.SimScheduler.renderPrakseQueue(doc, renderSelDay20, sPolicy, { coverage: cov, bankQuestions });
  const renderKeysOk = renderSelDay20.queue.every((q) => Boolean(termsMap[q.reason_key]) && q.reason_lv.indexOf('{') < 0);
  const renderReasons = renderSelDay20.queue.map((q) => q.reason_code);

  check('b13_term_keyed_render_fixture',
    renderSelDay20.queue.length === 5 &&
    renderKeysOk &&
    renderReasons.join(',') === 'overdue,overdue,due_today,new,new' &&
    Boolean(renderVm && renderVm.queue.length === 5),
    {
      queue_reasons: renderSelDay20.queue.map((q) => ({ outcome_id: q.outcome_id, reason_code: q.reason_code, reason_key: q.reason_key, reason_lv: q.reason_lv })),
      render_digest: renderSelDay20.digest,
    }
  );

  /* C.1 & C.1.1 — End-to-end practice entry handoff + post-session queue recomputation */
  const e2eBacking = createStorage();
  const e2eEnv = loadSchedulerStandalone(repoRoot, islands, e2eBacking.storage);
  const e2eDate = '2026-11-19';
  const e2eDay = e2eEnv.sb.SimScheduler.toDayNumber(e2eDate);
  const e2ePrevDay = e2eEnv.sb.SimScheduler.toDayNumber('2026-11-15');
  const e2eClock = e2eEnv.sb.SimScheduler.createFixedDayClock(e2eDate);

  const e2eStore = e2eEnv.sb.SimStore.createStore({ optIn: true, storage: e2eBacking.storage, doc: e2eEnv.doc });
  // Seed mastery state: P1-05 learning (last practiced 4 days ago -> overdue by 3d), P2-01 learning (last practiced 2 days ago -> overdue by 1d)
  const seededMap = e2eEnv.sb.SimMastery.reduce(
    e2eEnv.sb.SimMastery.createInitialStateMap(cov, mPolicy, mLoaded.digest),
    [
      { kind: 'criterion_verdict', outcome_id: 'P1-05', verdict: 'correct', day: e2ePrevDay },
      { kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'incorrect', day: e2eDay - 2 },
    ],
    mPolicy
  );
  e2eEnv.sb.SimMastery.writeToStore(e2eStore, seededMap);

  const startedHandoffs = [];
  e2eEnv.sb.SimPractice = {
    startPath(handoff) {
      startedHandoffs.push(handoff);
      return { path_id: 'PATH-' + handoff.outcome_id, count: handoff.filters.instance_ids.length };
    },
  };
  const e2eMasteryApp = e2eEnv.sb.SimMastery.init(e2eEnv.doc, { coverage: cov, bank: islands['sim-bank'], store: e2eStore });
  const e2eSchedApp = e2eEnv.sb.SimScheduler.init(e2eEnv.doc, {
    coverage: cov,
    bank: islands['sim-bank'],
    store: e2eStore,
    masteryApp: e2eMasteryApp,
    clock: e2eClock,
  });

  const beforeQueue = e2eSchedApp.getLastSelection().queue.map((q) => q.outcome_id);
  // Simulate learner clicking the first recommended item button in #prakse-scheduler-queue
  const firstLi = e2eEnv.doc.getElementById('prakse-scheduler-queue').childNodes[0];
  const acceptBtn = firstLi.childNodes[1].childNodes[1];
  acceptBtn.click();

  const handoff = startedHandoffs[0];
  const forbiddenKeyFields = ['payload', 'rubric', 'derived', 'draws', 'expected', 'correct_ids', 'feedback_lv', 'misconception_signatures'];
  const handoffJson = JSON.stringify(handoff || {});
  const leakedFields = forbiddenKeyFields.filter((fk) => handoff && (Object.prototype.hasOwnProperty.call(handoff, fk) || Object.prototype.hasOwnProperty.call(handoff.filters || {}, fk)));

  // Complete bounded practice session on P1-05 (1 correct graded criterion on e2eDate -> P1-05 advances to near_mastered on e2eDay)
  e2eMasteryApp.ingestGradedRecord({
    record_kind: 'graded-record',
    digest: '1'.repeat(64),
    slots: [{
      slot_id: 'PRAC-P1-05-1',
      state: 'graded',
      criteria: [{ criterion_id: 'C1', status: 'awarded', grading: 'auto', outcome_ids: ['P1-05'] }],
    }],
  }, e2eDay);

  const afterQueueSel = e2eEnv.sb.SimScheduler.renderFromStore(e2eEnv.doc, e2eStore, cov, { bankQuestions });
  const afterQueue = afterQueueSel.queue.map((q) => q.outcome_id);
  const afterDomQueueText = collectNodeText(e2eEnv.doc.getElementById('prakse-scheduler-queue'));
  const postMastery = e2eMasteryApp.readFromStore();

  check('c11_e2e_practice_handoff_and_recompute',
    beforeQueue[0] === 'P1-05' &&
    beforeQueue[1] === 'P2-01' &&
    startedHandoffs.length === 1 &&
    handoff.contract === 'N27-to-N30-practice-entry' &&
    handoff.outcome_id === 'P1-05' &&
    handoff.filters.instance_ids.length > 0 &&
    leakedFields.length === 0 &&
    handoffJson.indexOf('correct_ids') < 0 &&
    postMastery.outcomes['P1-05'].state === 'near_mastered' &&
    postMastery.outcomes['P1-05'].last_practiced_day === e2eDay &&
    afterQueue[0] === 'P2-01' &&
    afterQueue.indexOf('P1-05') < 0 &&
    afterDomQueueText.indexOf('P2-01') >= 0,
    {
      before_queue: beforeQueue,
      handoff,
      leaked_fields: leakedFields,
      post_p1_05_state: postMastery.outcomes['P1-05'].state,
      after_queue: afterQueue,
    }
  );

  /* C.1.3 — Built-artifact smoke check with #sim-scheduler-policy inlined */
  const artifactPath = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(artifactPath)) {
    const html = fs.readFileSync(artifactPath, 'utf8');
    const allIslandIds = [
      'sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms', 'sim-golden-vectors',
      'sim-terms', 'sim-analytics', 'sim-mastery-policy', 'sim-scheduler-policy',
      'sim-figures', 'sim-chains', 'sim-engines', 'sim-graph-scoring', 'sim-method-cards',
      'sim-method-engine', 'sim-exam-policy', 'sim-response-types', 'sim-grading-policy',
      'sim-feedback-classification'
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
    const n27Vec = smoke && smoke.vectors ? smoke.vectors.find((v) => v.id === 'SMK-N27-SCHEDULER-QUEUE') : null;
    const renderedQueue = artDoc.getElementById('prakse-scheduler-queue');
    check('c13_built_artifact_smoke',
      Boolean(parsedIslands['sim-scheduler-policy']) &&
      Boolean(smoke && smoke.status === 'PASS' && n27Vec && n27Vec.status === 'PASS') &&
      Boolean(renderedQueue && renderedQueue.childNodes.length === 5) &&
      artNet.length === 0 && Object.keys(artBacking.backing).length === 0 && netLog.length === 0,
      {
        total_smoke_vectors: smoke ? smoke.total : 0,
        passed_smoke_vectors: smoke ? smoke.passed : 0,
        n27Vec,
        rendered_queue_items: renderedQueue ? renderedQueue.childNodes.length : 0,
      }
    );
  } else {
    check('c13_built_artifact_smoke', false, { reason: 'output/simulator.html missing' });
  }

  const report = {
    schema_version: 1,
    task: 'N27',
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks: results,
    failures,
  };

  if (args.record) {
    const outPath = path.isAbsolute(args.record) ? args.record : path.join(repoRoot, args.record);
    fs.mkdirSync(path.dirname(outPath), { recursive: true });
    fs.writeFileSync(outPath, JSON.stringify(report, null, 2) + '\n', 'utf8');
  }
  if (args.renderOut) {
    const renPath = path.isAbsolute(args.renderOut) ? args.renderOut : path.join(repoRoot, args.renderOut);
    fs.mkdirSync(path.dirname(renPath), { recursive: true });
    fs.writeFileSync(renPath, JSON.stringify({
      schema_version: 1,
      owner: 'N27',
      note: 'Deterministic 5-item Leitner practice queue render fixture with term-keyed Latvian reasons (also serves as N32 visual test data).',
      selection: renderSelDay20,
      view_model: renderVm,
    }, null, 2) + '\n', 'utf8');
  }

  console.log('N27 runtime: ' + report.status + ' (' + Object.keys(results).length + ' checks, ' + failures.length + ' failures)');
  for (const f of failures) {
    console.error('  FAIL:', f);
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
