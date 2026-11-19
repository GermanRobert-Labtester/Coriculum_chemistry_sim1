#!/usr/bin/env node
/* N29 runtime harness:
 *   A.1.1: 3 learner profiles (fresh, mid_progress, near_complete) + self-rated-unattempted & Topic 7 unavailable corner cases
 *   A.1.2: Affordance resolution + dangling-anchor scratch failure
 *   A.1.3: Per-topic summary lines + Latvian copy lint
 *   B.1:   Separation invariants (distinct DOM/state sources, mastery digest unchanged, N12 key-leak scan)
 *   B.1.1: Single-sourced criterion names (scratch rubric rename propagates identically to SimFeedback & SimRevision)
 *   B.1.2: Keyboard-complete <select> API + ARIA live announcements
 *   B.1.3: Store round-trip, in-memory default, opt-in, 500/501 note boundary, two-step erase
 *   C.1.1: 3-way determinism (two in-process + fresh child process --replay-only) + Honesty Audit Table
 *   C.1.3: Built-artifact smoke check (25/25 incl. SMK-N29-REVISION-PANEL) + N30 practice-entry handoff
 *
 * Usage:
 *   node tools/check_n29_runtime.js [--repo-root .] [--record PATH] [--profiles-out PATH] [--baseline-out PATH] [--audit-out PATH]
 *   node tools/check_n29_runtime.js --replay-only --repo-root .
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
    profilesOut: null,
    baselineOut: null,
    auditOut: null,
    replayOnly: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--profiles-out') { args.profilesOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--baseline-out') { args.baselineOut = argv[i + 1]; i += 1; }
    else if (argv[i] === '--audit-out') { args.auditOut = argv[i + 1]; i += 1; }
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

function collectNodeText(node) {
  if (!node) { return ''; }
  if (node.childNodes && node.childNodes.length) {
    return node.childNodes.map(collectNodeText).join(' ');
  }
  return node._text || '';
}

function makeDom(islands, globals) {
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
    this.selected = false;
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
  Node.prototype.dispatchEvent = function (evOrType, evObj) {
    const t = typeof evOrType === 'string' ? evOrType : (evOrType && evOrType.type ? evOrType.type : '');
    const ev = evObj || (typeof evOrType === 'object' ? evOrType : { type: t, target: this });
    if (!ev.target) { ev.target = this; }
    const list = this.listeners[t] || [];
    for (let i = 0; i < list.length; i += 1) { list[i](ev); }
    return true;
  };
  Node.prototype.click = function () { this.dispatchEvent('click', { type: 'click', target: this }); };
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
    ['atskats-revision-wrap', 'div'], ['atskats-revision-heading', 'h3'], ['atskats-revision-honesty', 'p'],
    ['sim-revision-error', 'p'], ['atskats-revision-status', 'p'], ['atskats-revision-panel', 'div'],
    ['atskats-revision-chain-host', 'div'], ['atskats-revision-handoff', 'div'], ['atskats-self-assessment-host', 'div'],
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
  ids.forEach(([id, tag]) => { doc.body.appendChild(new Node(tag, id)); });

  Object.keys(islands || {}).forEach((id) => {
    const n = new Node('script', id);
    n.setAttribute('type', 'application/json');
    n.textContent = typeof islands[id] === 'string' ? islands[id] : JSON.stringify(islands[id]);
    doc.body.appendChild(n);
  });

  if (globals) {
    doc._globals = globals;
  }
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
  return {
    'sim-coverage': readJson(path.join(repoRoot, 'data/coverage.json')),
    'sim-conventions': readJson(path.join(repoRoot, 'data/conventions.json')),
    'sim-terms': readJson(path.join(repoRoot, 'data/terms.json')),
    'sim-bank': { island_id: 'sim-bank', schema_version: 1, bank_version: '1.0.0-n20', status: 'frozen-reviewed-bank', questions: bankQuestions },
    'sim-chains': readJson(path.join(repoRoot, 'data/chains.json')),
    'sim-method-cards': readJson(path.join(repoRoot, 'data/method_cards.json')),
    'sim-grading-policy': readJson(path.join(repoRoot, 'data/grading_policy.json')),
    'sim-feedback-classification': readJson(path.join(repoRoot, 'data/feedback_classification.json')),
    'sim-analytics': readJson(path.join(repoRoot, 'data/analytics_schema.json')),
    'sim-mastery-policy': readJson(path.join(repoRoot, 'data/mastery_policy.json')),
    'sim-scheduler-policy': readJson(path.join(repoRoot, 'data/scheduler_policy.json')),
    'sim-remediation-policy': readJson(path.join(repoRoot, 'data/remediation_policy.json')),
    'sim-revision-policy': readJson(path.join(repoRoot, 'data/revision_policy.json')),
    'sim-concept-summaries': readJson(path.join(repoRoot, 'data/concept_summaries.json')),
    'sim-anchor-registry': readJson(path.join(repoRoot, 'data/anchor_registry.json')),
  };
}

function createStorage() {
  const backing = Object.create(null);
  const writes = [];
  return {
    backing,
    writes,
    storage: {
      getItem(k) { return Object.prototype.hasOwnProperty.call(backing, k) ? backing[k] : null; },
      setItem(k, v) { writes.push({ op: 'set', key: k }); backing[k] = String(v); },
      removeItem(k) { writes.push({ op: 'remove', key: k }); delete backing[k]; },
    },
  };
}

function loadSandbox(repoRoot, islands, storage) {
  const doc = makeDom(islands);
  const summaries = readJson(path.join(repoRoot, 'data/concept_summaries.json'));
  const anchorReg = readJson(path.join(repoRoot, 'data/anchor_registry.json'));
  const sb = {
    console,
    document: doc,
    window: null,
    localStorage: storage || undefined,
    COVERAGE_INVARIANTS: { total: 64, perTopic: { 1: 9, 2: 10, 3: 11, 4: 11, 5: 10, 6: 8, 7: 5 } },
    CONCEPT_DRAWER_DATA: summaries,
    ANCHOR_REGISTRY: anchorReg,
    Object, Array, String, Number, Boolean, Math, JSON, Date, RegExp, Error, TypeError, RangeError,
    parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent, unescape,
  };
  sb.window = sb;
  sb.globalThis = sb;
  vm.createContext(sb);

  const files = [
    'src/coverage-loader.js',
    'src/terms-loader.js',
    'src/conventions-loader.js',
    'src/prng.js',
    'src/leak-scan.js',
    'src/chain-view.js',
    'src/concept-drawer.js',
    'src/compiled/feedback.js',
    'src/compiled/store.js',
    'src/compiled/analytics.js',
    'src/compiled/mastery.js',
    'src/compiled/remediation.js',
    'src/compiled/revision.js',
  ];
  files.forEach((rel) => {
    const code = fs.readFileSync(path.join(repoRoot, rel), 'utf8');
    vm.runInContext(code, sb, { filename: rel });
  });
  return { sb, doc };
}

function buildMasteryProfiles(sb, cov, masteryPol, masteryPolDigest) {
  const freshMap = sb.SimMastery.createInitialStateMap(cov, masteryPol, masteryPolDigest);
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
  const midMap = sb.SimMastery.reduce(freshMap, midEvents, masteryPol);

  const nearEvents = [];
  const allOids = Object.keys(freshMap.outcomes).sort();
  for (let i = 0; i < allOids.length; i += 1) {
    const oid = allOids[i];
    if (i < 54) {
      for (let k = 0; k < 4; k += 1) { nearEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 }); }
    } else if (i < 60) {
      nearEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 });
      nearEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 5 });
    } else if (i < 62) {
      for (let k = 0; k < 4; k += 1) { nearEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'correct', day: 1 }); }
      nearEvents.push({ kind: 'decay', outcome_id: oid, days_inactive: 14 });
    } else {
      nearEvents.push({ kind: 'criterion_verdict', outcome_id: oid, verdict: 'incorrect', day: 5 });
    }
  }
  const nearMap = sb.SimMastery.reduce(freshMap, nearEvents, masteryPol);

  return { freshMap, midMap, nearMap };
}

function buildFullRevisionScenario(repoRoot, islands) {
  const { sb, doc } = loadSandbox(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const masteryPolLoaded = sb.SimMastery.loadPolicy(doc);
  const remPolLoaded = sb.SimRemediation.loadPolicy(doc);
  const revPolLoaded = sb.SimRevision.loadPolicy(doc);
  const store = sb.SimStore.createStore({ optIn: false, doc });

  const { midMap } = buildMasteryProfiles(sb, cov, masteryPolLoaded.policy, masteryPolLoaded.digest);
  store.update((draft) => { draft.mastery = midMap; });

  sb.SimRemediation.addMiss(store, {
    slot_id: 'S3-1',
    topic: 3,
    family_id: 'FAM-3A',
    instance_id: 'COL1-3-3A-A-01',
    outcome_ids: ['P3-01'],
    signature_id: 'MC-3A-02',
    concept_ids: ['P3-01'],
    chain_ids: ['EX05'],
    graded_digest: sha256('full-rev-miss-p301'),
  }, { doc, coverage: cov, policy: remPolLoaded.policy });

  sb.SimRevision.saveSelfAssessment(store, 'P1-01', {
    ratings: { C1_VALUE: 'confident', C2_SIGFIG: 'with_effort' },
    note: 'Pārbaudīju stehiometriskos koeficientus.'
  }, { doc, coverage: cov, policy: revPolLoaded.policy });

  /* Corner case A.1.1: self-rated BEFORE practicing (P1-02 has 0 graded attempts) */
  sb.SimRevision.saveSelfAssessment(store, 'P1-02', {
    ratings: { C1_PHASE: 'not_yet' },
    note: 'Vēl jāsakārto fāžu piemēri.'
  }, { doc, coverage: cov, policy: revPolLoaded.policy });

  const vm = sb.SimRevision.renderRevisionPanel(doc, {
    store,
    coverage: cov,
    policy: revPolLoaded.policy,
  });
  const cardP101 = sb.SimRevision.buildSelfAssessmentCardModel('P1-01', {
    doc,
    store,
    coverage: cov,
    policy: revPolLoaded.policy,
  });
  const audit = sb.SimRevision.buildHonestyAudit(vm, cardP101);
  return { sb, doc, store, cov, vm, cardP101, audit };
}

function runReplayOnly(repoRoot) {
  const islands = buildIslands(repoRoot);
  const res = buildFullRevisionScenario(repoRoot, islands);
  process.stdout.write(JSON.stringify({
    view_model_digest: res.vm.digest,
    card_digest: res.cardP101.digest,
    audit_status: res.audit.status,
    audit_digest: sha256(canonical(res.audit)),
  }));
}

function collectAnswerTargets(bankQuestions) {
  const targets = [];
  for (let i = 0; i < bankQuestions.length; i += 1) {
    const q = bankQuestions[i];
    const p = q.payload || {};
    if (p.expected_value !== undefined && p.expected_value !== null) {
      const n = Number(String(p.expected_value).replace(',', '.'));
      if (isFinite(n) && Math.abs(n) >= 10) {
        targets.push({ qid: q.question_id, value: String(p.expected_value), unit: p.expected_unit || '' });
      }
    }
    if (Array.isArray(p.correct_ids)) {
      p.correct_ids.forEach((cid) => {
        if (typeof cid === 'string' && cid.length >= 6) {
          targets.push({ qid: q.question_id, value: cid, unit: '' });
        }
      });
    }
    if (Array.isArray(p.steps)) {
      p.steps.forEach((st) => {
        if (st && typeof st.expected === 'string' && st.expected.length >= 12) {
          targets.push({ qid: q.question_id, value: st.expected, unit: '' });
        }
      });
    }
  }
  return targets;
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
  const bankQuestions = islands['sim-bank'].questions;
  const { sb, doc } = loadSandbox(repoRoot, islands, null);
  const cov = sb.SimCoverage.load(doc, sb.COVERAGE_INVARIANTS);
  const masteryPolLoaded = sb.SimMastery.loadPolicy(doc);
  const revPolLoaded = sb.SimRevision.loadPolicy(doc);
  const revPolicy = revPolLoaded.policy;

  /* ------------------------------------------------ A.1.1 & A.1.3 Profiles */
  const { freshMap, midMap, nearMap } = buildMasteryProfiles(sb, cov, masteryPolLoaded.policy, masteryPolLoaded.digest);
  const availAll = sb.SimMastery.computeAvailability(cov, bankQuestions, masteryPolLoaded.policy);

  const pendingBank = bankQuestions.map((q) => {
    if (q.topic === 7) {
      const copy = JSON.parse(JSON.stringify(q));
      copy.review = { accessibility: 'pending', calculation: 'passed', content: 'passed', source: 'passed' };
      return copy;
    }
    return q;
  });
  const availPendingT7 = sb.SimMastery.computeAvailability(cov, pendingBank, masteryPolLoaded.policy);

  const storeSelfOnly = sb.SimStore.createStore({ optIn: false, doc });
  sb.SimRevision.saveSelfAssessment(storeSelfOnly, 'P1-02', {
    ratings: { C1_PHASE: 'confident', C2_REASON: 'with_effort' },
    note: 'Pašvērtējums pirms prakses.'
  }, { doc, coverage: cov, policy: revPolicy });

  const vmFresh = sb.SimRevision.renderRevisionPanel(doc, {
    store: sb.SimStore.createStore({ optIn: false, doc }),
    coverage: cov,
    masteryMap: freshMap,
    availability: availAll,
    policy: revPolicy,
  });
  const vmSelfBeforePractice = sb.SimRevision.renderRevisionPanel(doc, {
    store: storeSelfOnly,
    coverage: cov,
    masteryMap: freshMap,
    availability: availAll,
    policy: revPolicy,
  });
  const vmMid = sb.SimRevision.renderRevisionPanel(doc, {
    store: sb.SimStore.createStore({ optIn: false, doc }),
    coverage: cov,
    masteryMap: midMap,
    availability: availAll,
    policy: revPolicy,
  });
  const vmNear = sb.SimRevision.renderRevisionPanel(doc, {
    store: sb.SimStore.createStore({ optIn: false, doc }),
    coverage: cov,
    masteryMap: nearMap,
    availability: availAll,
    policy: revPolicy,
  });
  const vmT7Unavail = sb.SimRevision.renderRevisionPanel(doc, {
    store: sb.SimStore.createStore({ optIn: false, doc }),
    coverage: cov,
    masteryMap: freshMap,
    availability: availPendingT7,
    bankQuestions: pendingBank,
    policy: revPolicy,
  });

  const p102SelfRow = vmSelfBeforePractice.topics[0].outcomes[1];
  const t7Rows = vmT7Unavail.topics[6].outcomes;
  const allT7Unavail = t7Rows.length === 5 && t7Rows.every((r) =>
    r.mastery.effective_state === 'unavailable' &&
    r.availability.available === false &&
    r.affordances.practice_available === false &&
    typeof r.availability.reason_lv === 'string' && r.availability.reason_lv.length > 0
  );

  const forbiddenEndorsementRe = /\b(?:sertifik[aā]t\w*|akredit[eē]t\w*|ofici[aā]li\s+apstiprin\w*|garant[eē]\w*|ofici[aā]l[aā]\s+atz[iī]me)\b/i;
  const renderedPanelText = collectNodeText(doc.getElementById('atskats-revision-wrap'));
  const allRows64 = (vm) => {
    const ids = [];
    vm.topics.forEach((tp) => tp.outcomes.forEach((o) => ids.push(o.outcome_id)));
    return ids.length === 64 && new Set(ids).size === 64;
  };

  check('a11_a13_three_profiles_and_corner_cases',
    allRows64(vmFresh) &&
    allRows64(vmMid) &&
    allRows64(vmNear) &&
    vmFresh.counts.unseen === 64 &&
    vmFresh.topics.every((t) => t.is_empty_topic === true && typeof t.empty_notice_lv === 'string') &&
    vmMid.counts.mastered === 1 &&
    vmMid.topics[0].outcomes[0].mastery.last_practiced_day === 3 &&
    vmNear.counts.mastered === 54 &&
    p102SelfRow.outcome_id === 'P1-02' &&
    p102SelfRow.mastery.effective_state === 'unseen' &&
    p102SelfRow.mastery.attempts === 0 &&
    p102SelfRow.self_assessment.rated_count === 2 &&
    allT7Unavail &&
    !forbiddenEndorsementRe.test(renderedPanelText),
    {
      fresh_counts: vmFresh.counts,
      mid_counts: vmMid.counts,
      near_counts: vmNear.counts,
      p102_self_before_practice: {
        mastery_state: p102SelfRow.mastery.effective_state,
        attempts: p102SelfRow.mastery.attempts,
        rated_count: p102SelfRow.self_assessment.rated_count,
      },
      t7_unavailable_count: vmT7Unavail.topics[6].counts.unavailable,
    }
  );

  /* ------------------------------------------------ A.1.2 Dangling anchor */
  const scratchCov = JSON.parse(JSON.stringify(cov));
  scratchCov.outcomes[0].master_anchor = 'broken_anchor_xyz';
  const danglingErr = captureError(() => {
    sb.SimRevision.renderRevisionPanel(doc, {
      store: storeSelfOnly,
      coverage: scratchCov,
      policy: revPolicy,
    });
  });
  check('a12_dangling_anchor_fails_loudly',
    danglingErr !== null &&
    danglingErr.code === 'E_REVISION_DANGLING_ANCHOR' &&
    danglingErr.message.indexOf('broken_anchor_xyz') >= 0 &&
    danglingErr.message.indexOf('P1-01') >= 0,
    { error: danglingErr }
  );

  /* ------------------------------------------------ B.1 Separation & Leak Scan */
  const sepStore = sb.SimStore.createStore({ optIn: false, doc });
  sepStore.update((draft) => { draft.mastery = midMap; });
  const digestBefore = sb.SimMastery.digestOfMap(sb.SimMastery.readFromStore(sepStore, cov, masteryPolLoaded.policy, masteryPolLoaded.digest));

  sb.SimRevision.saveSelfAssessment(sepStore, 'P1-01', {
    ratings: { C1_VALUE: 'not_yet', C2_SIGFIG: 'with_effort' },
    note: 'Šis ir mans paša vērtējums.'
  }, { doc, coverage: cov, policy: revPolicy });

  const digestAfter = sb.SimMastery.digestOfMap(sb.SimMastery.readFromStore(sepStore, cov, masteryPolLoaded.policy, masteryPolLoaded.digest));
  const vmSep = sb.SimRevision.renderRevisionPanel(doc, {
    store: sepStore,
    coverage: cov,
    policy: revPolicy,
  });

  const p101RowEl = doc.getElementById('atskats-rev-row-P1-01');
  const p101Text = collectNodeText(p101RowEl);
  const masteryBadges = doc.querySelectorAll('.revision-mastery-badge');
  const selfBadges = doc.querySelectorAll('.revision-self-badge');
  const distinctDisplaySources = masteryBadges.length === 64 && selfBadges.length === 64 &&
    masteryBadges[0].getAttribute('data-source') === 'mastery-n26' &&
    selfBadges[0].getAttribute('data-source') === 'self-assessment-f07' &&
    p101Text.indexOf('Apgūts (pašmācībā)') >= 0 &&
    p101Text.indexOf('Pašvērtējums (F07): 2 no') >= 0;

  /* N12 key-leak scan across all 64 rendered F07 cards */
  const answerTargets = collectAnswerTargets(bankQuestions);
  const leakHits = [];
  for (let i = 0; i < cov.outcomes.length; i += 1) {
    const oid = cov.outcomes[i].id;
    const cm = sb.SimRevision.buildSelfAssessmentCardModel(oid, { doc, store: sepStore, coverage: cov, policy: revPolicy });
    const cardText = JSON.stringify(cm.criteria);
    for (let k = 0; k < cm.criteria.length; k += 1) {
      if (Object.prototype.hasOwnProperty.call(cm.criteria[k], 'points') ||
          Object.prototype.hasOwnProperty.call(cm.criteria[k], 'expected') ||
          Object.prototype.hasOwnProperty.call(cm.criteria[k], 'grading')) {
        leakHits.push({ oid, kind: 'rubric_internal_field' });
      }
    }
    for (let t = 0; t < answerTargets.length; t += 1) {
      const tgt = answerTargets[t];
      if (tgt.value.length >= 6 && cardText.indexOf(tgt.value) >= 0) {
        leakHits.push({ oid, kind: 'answer_key_leak', value: tgt.value });
      }
    }
  }

  check('b1_separation_and_leak_scan',
    digestBefore === digestAfter &&
    distinctDisplaySources &&
    leakHits.length === 0,
    {
      mastery_digest_before: digestBefore,
      mastery_digest_after: digestAfter,
      mastery_badges: masteryBadges.length,
      self_badges: selfBadges.length,
      leak_hits_count: leakHits.length,
      leak_hits: leakHits.slice(0, 5),
    }
  );

  /* ------------------------------------------------ B.1.1 Single-sourcing fixture */
  const renamedLabel = 'PĀRDĒVĒTS-KRITĒRIJS-N29: Skaitliskais aprēķins (test)';
  const scratchIslands = JSON.parse(JSON.stringify(islands));
  scratchIslands['sim-terms'].terms.forEach((t) => {
    if (t.key === 'feedback.criterion.C1_VALUE') { t.text_lv = renamedLabel; }
  });
  const scratchEnv = loadSandbox(repoRoot, scratchIslands, null);
  const scratchCov2 = scratchEnv.sb.SimCoverage.load(scratchEnv.doc, scratchEnv.sb.COVERAGE_INVARIANTS);
  const scratchCard = scratchEnv.sb.SimRevision.buildSelfAssessmentCardModel('P1-01', {
    doc: scratchEnv.doc,
    coverage: scratchCov2,
  });
  const scratchTermsMap = scratchEnv.sb.SimFeedback.loadTermsMap(scratchEnv.doc);
  const scratchGradedRec = {
    schema_version: 1,
    digest: sha256('scratch-graded'),
    totals: { auto_points: 2, auto_max_points: 2, pending_external_points: 0, pending_max_points: 0 },
    slots: [{
      slot_id: 'S1-1',
      state: 'graded',
      verdict_class: 'correct',
      slot_points: 2,
      task: { auto_points: 2, auto_max_points: 2, pending_points: 0, max_points: 2 },
      criteria: [{ criterion_id: 'C1_VALUE', engine_binding: 'N17-numeric', status: 'awarded', awarded_points: 2, max_points: 2 }],
    }],
    feedback: { items: [] },
  };
  const scratchFeedbackReport = scratchEnv.sb.SimFeedback.buildScoreReport(scratchGradedRec, scratchTermsMap);
  const cardC1Label = (scratchCard.criteria.find((c) => c.criterion_id === 'C1_VALUE') || {}).label_lv;

  check('b11_single_sourced_criterion_rename',
    cardC1Label === renamedLabel &&
    scratchFeedbackReport.html.indexOf(renamedLabel) >= 0,
    {
      renamed_label: renamedLabel,
      card_c1_label: cardC1Label,
      present_in_graded_feedback_report: scratchFeedbackReport.html.indexOf(renamedLabel) >= 0,
    }
  );

  /* ------------------------------------------------ B.1.2 Keyboard <select> & ARIA announcements */
  const kbStore = sb.SimStore.createStore({ optIn: false, doc });
  const kbCard = sb.SimRevision.openSelfAssessmentCard(doc, 'P1-01', {
    store: kbStore,
    coverage: cov,
    policy: revPolicy,
  });
  const liveEl = doc.getElementById('atskats-sa-live');
  const announcements = [];
  const selectIds = [];
  for (let i = 0; i < kbCard.criteria.length; i += 1) {
    const cid = kbCard.criteria[i].criterion_id;
    const selId = 'rev-sa-select-P1-01-' + cid;
    const sel = doc.getElementById(selId);
    if (!sel) { continue; }
    selectIds.push(selId);
    const val = i % 3 === 0 ? 'confident' : (i % 3 === 1 ? 'with_effort' : 'not_yet');
    sel.value = val;
    sel.dispatchEvent('change', { type: 'change', target: sel });
    announcements.push(liveEl.textContent);
  }
  const noteEl = doc.getElementById('atskats-sa-note');
  noteEl.value = '  Tastatūras tests bez peles klikšķiem.  ';
  noteEl.dispatchEvent('input', { type: 'input', target: noteEl });
  doc.getElementById('atskats-sa-save').click();
  const savedAfterKb = sb.SimRevision.readSelfAssessments(kbStore)['P1-01'];

  check('b12_keyboard_select_and_aria_announcements',
    selectIds.length === kbCard.criteria.length &&
    announcements.length === kbCard.criteria.length &&
    announcements.every((a) => a.indexOf('Kritērijs') >= 0 && a.indexOf('izvēlēts stāvoklis') >= 0) &&
    liveEl.getAttribute('role') === 'status' &&
    liveEl.getAttribute('aria-live') === 'polite' &&
    savedAfterKb &&
    Object.keys(savedAfterKb.ratings).length === kbCard.criteria.length &&
    savedAfterKb.note === '  Tastatūras tests bez peles klikšķiem.  ',
    {
      criteria_completed_via_select: selectIds.length,
      announcements_count: announcements.length,
      sample_announcement: announcements[0] || null,
      live_role: liveEl.getAttribute('role'),
      aria_live: liveEl.getAttribute('aria-live'),
    }
  );

  /* ------------------------------------------------ B.1.3 Persistence, boundary & erase */
  const memBacking = createStorage();
  const memEnv = loadSandbox(repoRoot, islands, memBacking.storage);
  const memStore = memEnv.sb.SimStore.createStore({ optIn: false, doc: memEnv.doc, storage: memBacking.storage });
  memEnv.sb.SimRevision.saveSelfAssessment(memStore, 'P1-01', { ratings: { C1_VALUE: 'confident' }, note: 'In-memory' });
  const memWritesCount = memBacking.writes.length;

  const rtBacking = createStorage();
  const rtEnv = loadSandbox(repoRoot, islands, rtBacking.storage);
  const rtStore = rtEnv.sb.SimStore.createStore({ optIn: true, doc: rtEnv.doc, storage: rtBacking.storage });
  const exact500 = 'A'.repeat(500);
  const over501 = 'B'.repeat(501);
  rtEnv.sb.SimRevision.saveSelfAssessment(rtStore, 'P1-01', {
    ratings: { C1_VALUE: 'with_effort' },
    note: exact500,
  });
  const boundaryErr = captureError(() => {
    rtEnv.sb.SimRevision.saveSelfAssessment(rtStore, 'P1-01', {
      ratings: { C1_VALUE: 'confident' },
      note: over501,
    });
  });

  // Reload from localStorage
  const reloadEnv = loadSandbox(repoRoot, islands, rtBacking.storage);
  const reloadStore = reloadEnv.sb.SimStore.createStore({ probeExisting: true, doc: reloadEnv.doc, storage: rtBacking.storage });
  const reloadedSa = reloadEnv.sb.SimRevision.readSelfAssessments(reloadStore)['P1-01'];
  const counterText500 = (() => {
    reloadEnv.sb.SimRevision.openSelfAssessmentCard(reloadEnv.doc, 'P1-01', { store: reloadStore });
    return reloadEnv.doc.getElementById('atskats-sa-note-counter').textContent;
  })();

  // Two-step erase
  reloadStore.requestErase();
  reloadStore.confirmErase();
  const afterEraseSa = reloadEnv.sb.SimRevision.readSelfAssessments(reloadStore);

  check('b13_persistence_boundary_and_erase',
    memWritesCount === 0 &&
    Object.keys(rtBacking.backing).length === 0 &&
    reloadedSa &&
    reloadedSa.note === exact500 &&
    reloadedSa.note.length === 500 &&
    counterText500.indexOf('500 no 500') >= 0 &&
    boundaryErr && boundaryErr.code === 'E_REVISION_NOTE_TOO_LONG' &&
    Object.keys(afterEraseSa).length === 0,
    {
      memory_mode_writes: memWritesCount,
      boundary_500_counter: counterText500,
      boundary_501_error: boundaryErr ? boundaryErr.code : null,
      keys_after_erase: Object.keys(rtBacking.backing).length,
      sa_count_after_erase: Object.keys(afterEraseSa).length,
    }
  );

  /* ------------------------------------------------ C.1.1 Determinism + Honesty Audit */
  const run1 = buildFullRevisionScenario(repoRoot, islands);
  const run2 = buildFullRevisionScenario(repoRoot, islands);
  const freshRaw = execFileSync(process.execPath, [__filename, '--replay-only', '--repo-root', repoRoot], {
    encoding: 'utf8',
    maxBuffer: 10 * 1024 * 1024,
  });
  const freshParsed = JSON.parse(freshRaw);
  const audit1 = run1.audit;

  check('c11_determinism_and_honesty_audit',
    run1.vm.digest === run2.vm.digest &&
    run1.vm.digest === freshParsed.view_model_digest &&
    run1.cardP101.digest === run2.cardP101.digest &&
    run1.cardP101.digest === freshParsed.card_digest &&
    audit1.status === 'PASS' &&
    audit1.untraceable_count === 0 &&
    audit1.merged_sources_count === 0 &&
    audit1.total_elements >= 320,
    {
      run1_vm_digest: run1.vm.digest,
      run2_vm_digest: run2.vm.digest,
      fresh_vm_digest: freshParsed.view_model_digest,
      run1_card_digest: run1.cardP101.digest,
      fresh_card_digest: freshParsed.card_digest,
      audit_status: audit1.status,
      audit_elements: audit1.total_elements,
      untraceable_count: audit1.untraceable_count,
    }
  );

  /* ------------------------------------------------ C.1.3 N30 practice handoff & built-artifact smoke */
  const handoffOk = sb.SimRevision.startPracticeFromOutcome('P1-01', { viewModel: vmMid });
  const handoffUnavailErr = captureError(() => {
    sb.SimRevision.startPracticeFromOutcome('P7-01', { viewModel: vmT7Unavail });
  });
  const handoffText = JSON.stringify(handoffOk);
  const handoffKeyFree = handoffOk.contract === 'N27-to-N30-practice-entry' &&
    handoffOk.entry_source === 'revision_panel' &&
    handoffText.indexOf('expected_value') < 0 &&
    handoffText.indexOf('correct_ids') < 0 &&
    handoffText.indexOf('rubric') < 0;

  let builtSmoke = { status: 'SKIP', reason: 'output/simulator.html not found' };
  const simPath = path.join(repoRoot, 'output/simulator.html');
  if (fs.existsSync(simPath)) {
    const html = fs.readFileSync(simPath, 'utf8');
    const islandMatches = {};
    const reIsland = /<script\s+type="application\/json"\s+id="([^"]+)">([\s\S]*?)<\/script>/g;
    let m;
    while ((m = reIsland.exec(html)) !== null) {
      islandMatches[m[1]] = m[2].replace(/<\\\//g, '</');
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
    const n29Vec = (smokeReport.vectors || []).find((v) => v.id === 'SMK-N29-REVISION-PANEL');
    builtSmoke = {
      status: smokeReport.status === 'PASS' && n29Vec && n29Vec.status === 'PASS' ? 'PASS' : 'FAIL',
      total: smokeReport.total,
      passed: smokeReport.passed,
      n29_vector: n29Vec || null,
    };
  }

  check('c13_handoff_and_built_smoke',
    handoffKeyFree &&
    handoffUnavailErr && handoffUnavailErr.code === 'E_REVISION_OUTCOME_UNAVAILABLE' &&
    builtSmoke.status === 'PASS',
    {
      handoff: handoffOk,
      unavailable_error: handoffUnavailErr ? handoffUnavailErr.code : null,
      built_smoke: builtSmoke,
    }
  );

  /* ------------------------------------------------ Write artifacts */
  if (args.profilesOut) {
    const out = path.isAbsolute(args.profilesOut) ? args.profilesOut : path.join(repoRoot, args.profilesOut);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify({
      schema_version: 1,
      owner: 'N29',
      note: 'Deterministic revision panel fixtures across 3 learner profiles plus self-rated-before-practicing and Topic-7 unavailable corner cases (N32 visual test data).',
      profiles: {
        fresh: vmFresh,
        mid_progress: vmMid,
        near_complete: vmNear,
        self_rated_before_practicing: vmSelfBeforePractice,
        unavailable_topic7: vmT7Unavail,
      },
    }, null, 2) + '\n', 'utf8');
  }

  if (args.baselineOut) {
    const out = path.isAbsolute(args.baselineOut) ? args.baselineOut : path.join(repoRoot, args.baselineOut);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify({
      schema_version: 1,
      owner: 'N29',
      note: 'Frozen full-revision regression baseline (graded history + N28 remediation queue + F07 self-assessments).',
      view_model: run1.vm,
      self_assessment_card_p101: run1.cardP101,
    }, null, 2) + '\n', 'utf8');
  }

  if (args.auditOut) {
    const out = path.isAbsolute(args.auditOut) ? args.auditOut : path.join(repoRoot, args.auditOut);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(audit1, null, 2) + '\n', 'utf8');
  }

  const record = {
    schema_version: 1,
    task: 'N29',
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    verbatim_copy: {
      self_assessment_label_lv: sb.SimRevision.VERBATIM_SELF_ASSESSMENT_LABEL_LV,
      note_never_analyzed_lv: sb.SimRevision.VERBATIM_NOTE_NEVER_ANALYZED_LV,
    },
    checks_count: Object.keys(results).length,
    failures,
    checks: results,
  };

  if (args.record) {
    const out = path.isAbsolute(args.record) ? args.record : path.join(repoRoot, args.record);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(record, null, 2) + '\n', 'utf8');
  }

  process.stdout.write(`N29 runtime: ${record.status} (${record.checks_count} checks, ${failures.length} failures)\n`);
  if (failures.length > 0) {
    failures.forEach((f) => process.stderr.write('  FAIL: ' + f + '\n'));
    process.exit(1);
  }
}

main();
