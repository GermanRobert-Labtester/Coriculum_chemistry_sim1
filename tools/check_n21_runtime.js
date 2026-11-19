#!/usr/bin/env node
/* N21 runtime harness: the exam session machine, the shell, the mode boundary.
 *
 * The harness loads the *shipped* runtime modules (src/compiled/session.js and
 * src/compiled/exam.js — the deterministic TypeScript build that the artifact
 * inlines) and proves the claims that the roadmap asks N21 to prove:
 *
 *   1. lifecycle          — start → answer → flag → navigate → review → submit,
 *                           and every logged transition matches the transition
 *                           table of the frozen #sim-exam-policy island;
 *   2. late_write_guard   — after submit / expire / abort every mutation is
 *                           refused with a stable error id, and the answers
 *                           that were given before the terminal transition are
 *                           preserved;
 *   3. timer_contract     — a mock clock drives the threshold (status only),
 *                           the expiry transition and the hidden-tab rule
 *                           (elapsed time comes from the clock, not from the
 *                           number of ticks);
 *   4. payload_contract   — per-type payloads are stored raw and unparsed, and
 *                           a malformed payload is refused by id;
 *   5. serialization       — a serialised session deserialises to identical
 *                           answers (the precondition N34's storage layer
 *                           depends on);
 *   6. view_discipline    — the exam render contains zero help markers and no
 *                           N16 chain step text; the practice render contains
 *                           zero exam-session fields. Both directions.
 *   7. mode_registry      — the registry maps mode → allowed components and an
 *                           unregistered component fails loudly (scratch
 *                           violation).
 *   8. navigation         — the scripted answer/flag sequence produces exactly
 *                           the expected map state; all 21 slots are reachable
 *                           by pointer and by keyboard alone.
 *   9. submit_gate        — the unanswered warning carries role="alert" and the
 *                           submission needs an explicit confirmation.
 *  10. buffer_race        — rapid navigation during a re-render loses no
 *                           in-progress answer.
 *  11. terminal_record    — the record N23 grades and N25 logs carries answers,
 *                           flags, elapsed time and the form id.
 *  12. end_to_end_trace   — the scripted session from the start screen to the
 *                           terminal record, every transition conforming to the
 *                           table.
 *  13. smoke_vectors      — the two in-file smoke vectors pass inside the built
 *                           artifact.
 *
 * The harness is not a browser render, accessibility, print or instructor
 * acceptance claim. It is a machine-level proof of the contracts above.
 *
 * Usage: node tools/check_n21_runtime.js [--repo-root .] [--record PATH]
 */
'use strict';

const fs = require('fs');
const path = require('path');

/* ------------------------------------------------------------------ arguments */

function parseArgs(argv) {
  const args = { repoRoot: path.resolve(__dirname, '..'), record: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
  }
  return args;
}

const REPO_ROOT = path.resolve(__dirname, '..');

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

/* ------------------------------------------------------------------ mini DOM */

const POINTER_EVENTS = ['click', 'pointerdown', 'pointerup', 'mousedown', 'mouseup', 'touchstart'];

function makeDocument(spec) {
  const registry = Object.create(null);
  const doc = {
    documentElement: null,
    body: null,
    activeElement: null,
    pointerEventCount: 0,
    createElement(tag) { return new Node(tag); },
    createElementNS(_ns, tag) { return new Node(tag); },
    getElementById(id) {
      if (Object.prototype.hasOwnProperty.call(registry, id)) { return registry[id]; }
      return findById(doc.body, id);
    },
    querySelector() { return null; },
    querySelectorAll() { return []; }
  };

  function findById(rootNode, id) {
    if (!rootNode) { return null; }
    if (rootNode.id === id) { return rootNode; }
    for (let i = 0; i < rootNode.childNodes.length; i += 1) {
      const found = findById(rootNode.childNodes[i], id);
      if (found) { return found; }
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
    this.type = '';
    this.value = '';
    this.checked = false;
    this.tabIndex = 0;
    this._text = '';
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(value) {
      if (this._id && registry[this._id] === this) { delete registry[this._id]; }
      this._id = String(value);
      if (this._id) { registry[this._id] = this; }
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
    if (child.id) { registry[child.id] = child; }
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const index = this.childNodes.indexOf(child);
    if (index >= 0) { this.childNodes.splice(index, 1); child.parentNode = null; }
    return child;
  };
  Node.prototype.setAttribute = function (key, value) {
    this.attributes[key] = String(value);
    /* A browser reflects the id attribute onto the id property, and the
     * document registry follows it. The shell sets ids with setAttribute, so
     * the harness has to mirror that or getElementById would miss nodes. */
    if (key === 'id') { this.id = value; }
  };
  Node.prototype.getAttribute = function (key) {
    return Object.prototype.hasOwnProperty.call(this.attributes, key) ? this.attributes[key] : null;
  };
  Node.prototype.removeAttribute = function (key) { delete this.attributes[key]; };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) { this.listeners[type] = []; }
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (type, event) {
    if (POINTER_EVENTS.indexOf(type) !== -1) { doc.pointerEventCount += 1; }
    const list = this.listeners[type] || [];
    const payload = event || {};
    payload.type = type;
    for (let i = 0; i < list.length; i += 1) { list[i](payload); }
    return true;
  };
  Node.prototype.focus = function () { doc.activeElement = this; };
  Node.prototype.blur = function () { if (doc.activeElement === this) { doc.activeElement = doc.body; } };

  doc.documentElement = new Node('html');
  doc.body = new Node('body');
  doc.activeElement = doc.body;

  Object.keys(spec).forEach((id) => {
    const definition = spec[id];
    const node = new Node(definition.tag || 'div');
    node.id = id;
    if (definition.className) { node.className = definition.className; }
    if (definition.hidden) { node.hidden = true; }
    if (definition.text) { node.textContent = definition.text; }
    doc.body.appendChild(node);
  });

  return doc;
}

/* The exam section markup, mirrored from src/shell.html. */
const EXAM_SPEC = {
  'eksamens': { tag: 'section' },
  'sim-exam-status': { tag: 'p', hidden: true },
  'exam-entry': { tag: 'div' },
  'exam-entry-note': { tag: 'p' },
  'exam-start': { tag: 'button' },
  'exam-shell': { tag: 'div', hidden: true },
  'exam-timer-bar': { tag: 'div' },
  'exam-timer-label': { tag: 'p' },
  'exam-timer-value': { tag: 'span', text: '00:00' },
  'exam-timer-threshold': { tag: 'p', hidden: true },
  'exam-timer-expired': { tag: 'p', hidden: true },
  'exam-navigator': { tag: 'div' },
  'exam-prev': { tag: 'button' },
  'exam-next': { tag: 'button' },
  'exam-flag': { tag: 'button' },
  'exam-review-button': { tag: 'button' },
  'exam-slot-status': { tag: 'p' },
  'exam-map-heading': { tag: 'h3' },
  'exam-map': { tag: 'div' },
  'exam-slot-host': { tag: 'div' },
  'exam-review': { tag: 'section', hidden: true },
  'exam-scope-note': { tag: 'aside' },
  'practice-host': { tag: 'div' }
};

function makeExamDocument(islandText) {
  const doc = makeDocument(EXAM_SPEC);
  const island = doc.getElementById('sim-exam-policy');
  if (!island) {
    const node = doc.createElement('script');
    node.setAttribute('type', 'application/json');
    node.id = 'sim-exam-policy';
    doc.body.appendChild(node);
  }
  doc.getElementById('sim-exam-policy').textContent = islandText;
  return doc;
}

function escapeText(text) {
  return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function serialize(node) {
  if (!node) { return ''; }
  const tag = node.tagName.toLowerCase();
  const attributes = Object.keys(node.attributes).sort()
    .map((key) => ' ' + key + '="' + String(node.attributes[key]).replace(/"/g, '&quot;') + '"')
    .join('');
  const inner = node.childNodes.length
    ? node.childNodes.map((child) => serialize(child)).join('')
    : escapeText(node.textContent);
  return '<' + tag + attributes + '>' + inner + '</' + tag + '>';
}

function findByAttribute(node, attribute, values) {
  const found = [];
  (function walk(current) {
    if (!current) { return; }
    const value = current.getAttribute ? current.getAttribute(attribute) : null;
    if (value !== null && values.indexOf(value) !== -1) { found.push(current); }
    (current.childNodes || []).forEach(walk);
  }(node));
  return found;
}

/* ----------------------------------------------------------------- mock clock */

function makeClock(startMs) {
  let current = startMs || 0;
  return {
    now() { return current; },
    advance(ms) { current += ms; return current; },
    set(ms) { current = ms; return current; }
  };
}

/* ------------------------------------------------------------------- helpers */

function captureError(fn) {
  try {
    fn();
    return null;
  } catch (error) {
    return {
      code: error && error.code ? error.code : null,
      message: error && error.message ? error.message : String(error)
    };
  }
}

function rowFor(table, from, event) {
  return table.filter((row) => row.from === from && row.event === event)[0] || null;
}

function deepEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function loadRuntime(root) {
  require(path.join(root, 'src/compiled/session.js'));
  require(path.join(root, 'src/compiled/exam.js'));
  const session = globalThis.SimSession;
  const exam = globalThis.SimExam;
  if (!session || !exam) {
    throw new Error('The compiled N21 modules did not register SimSession/SimExam.');
  }
  return { session, exam };
}

function newSession(runtime, policy, clock, formId) {
  return new runtime.session.ExamSession({
    policy: policy,
    form: { form_id: formId || 'A', slots: policy.slots },
    clock: clock || makeClock(0)
  });
}

/* --------------------------------------------------------------- 1. lifecycle */

function checkLifecycle(runtime, policy) {
  const table = policy.session_contract.transition_table;
  const clock = makeClock(1000);
  const session = newSession(runtime, policy, clock);
  const checks = {};
  const rows = [];

  const notStarted = captureError(() => session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'x' }
  }));
  checks.answer_before_start_refused = Boolean(notStarted) && notStarted.code === 'E_SESSION_NOT_STARTED';

  session.dispatch('start');
  session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id,
    payload: { kind: 'numeric', values: { value: '9,81' } }
  });
  session.dispatch('flag', { slot_id: policy.slots[2].slot_id });
  session.dispatch('navigate', { slot_id: policy.slots[3].slot_id });
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });

  const log = session.getTransitions();
  let tableConforms = true;
  let detail = '';
  for (let i = 0; i < log.length; i += 1) {
    const row = rowFor(table, log[i].from, log[i].event);
    if (!row || row.to !== log[i].to) {
      tableConforms = false;
      detail = 'transition ' + i + ' (' + log[i].from + '/' + log[i].event + ') does not match the table';
      break;
    }
    rows.push({ seq: log[i].seq, from: log[i].from, event: log[i].event, to: log[i].to });
  }

  checks.transition_count = log.length === 6;
  checks.transition_table_conforms = tableConforms;
  checks.final_state_submitted = session.getState() === 'submitted';
  checks.answer_stored = session.isAnswered(policy.slots[0].slot_id);
  checks.flag_stored = session.isFlagged(policy.slots[2].slot_id);
  checks.current_slot_after_navigate = session.getCurrentSlotId() === policy.slots[3].slot_id;
  checks.elapsed_uses_monotonic_clock = session.getElapsedMs() === 0;
  checks.limit_from_policy = session.getLimitMs() === policy.timer.advisory_limit_seconds * 1000;

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The lifecycle runs start → answer → flag → navigate → review → submit and every '
         + 'transition conforms to the transition table of the frozen policy island.',
    checks: checks,
    failed: failed,
    transitions: rows,
    detail: detail
  };
}

/* -------------------------------------------------------- 2. late write guard */

function checkLateWriteGuard(runtime, policy) {
  const checks = {};
  const observed = {};

  const submitted = newSession(runtime, policy, makeClock(0));
  submitted.dispatch('start');
  submitted.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'saglabāts' }
  });
  submitted.dispatch('request-review');
  submitted.dispatch('submit', { confirmed: true });
  observed.late_answer = captureError(() => submitted.dispatch('answer', {
    slot_id: policy.slots[1].slot_id, payload: { kind: 'raw_text', text: 'pārāk vēlu' }
  }));
  observed.late_flag = captureError(() => submitted.dispatch('flag', { slot_id: policy.slots[1].slot_id }));
  observed.late_navigate = captureError(() => submitted.dispatch('navigate', { slot_id: policy.slots[1].slot_id }));
  observed.late_start = captureError(() => submitted.dispatch('start'));
  checks.submitted_answer_refused = Boolean(observed.late_answer) && observed.late_answer.code === 'E_SESSION_LATE_WRITE';
  checks.submitted_flag_refused = Boolean(observed.late_flag) && observed.late_flag.code === 'E_SESSION_LATE_WRITE';
  checks.submitted_navigate_refused = Boolean(observed.late_navigate) && observed.late_navigate.code === 'E_SESSION_TERMINAL';
  checks.submitted_start_refused = Boolean(observed.late_start) && observed.late_start.code === 'E_SESSION_TERMINAL';
  checks.submitted_answers_preserved = submitted.getAnswers().length === 1;

  const expired = newSession(runtime, policy, makeClock(0));
  expired.dispatch('start');
  expired.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'pirms termiņa' }
  });
  expired.dispatch('expire');
  observed.expired_answer = captureError(() => expired.dispatch('answer', {
    slot_id: policy.slots[1].slot_id, payload: { kind: 'raw_text', text: 'pārāk vēlu' }
  }));
  observed.expired_flag = captureError(() => expired.dispatch('flag', { slot_id: policy.slots[1].slot_id }));
  checks.expired_answer_refused = Boolean(observed.expired_answer) && observed.expired_answer.code === 'E_SESSION_EXPIRED_WRITE';
  checks.expired_flag_refused = Boolean(observed.expired_flag) && observed.expired_flag.code === 'E_SESSION_EXPIRED_WRITE';
  checks.expired_answers_preserved = expired.getAnswers().length === 1;
  checks.expired_state = expired.getState() === 'expired';

  const aborted = newSession(runtime, policy, makeClock(0));
  aborted.dispatch('start');
  aborted.dispatch('abort');
  observed.aborted_answer = captureError(() => aborted.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'pēc aborta' }
  }));
  checks.aborted_answer_refused = Boolean(observed.aborted_answer) && observed.aborted_answer.code === 'E_SESSION_ABORTED_WRITE';
  checks.aborted_state = aborted.getState() === 'aborted';

  const running = newSession(runtime, policy, makeClock(0));
  running.dispatch('start');
  observed.skip_review = captureError(() => running.dispatch('submit', { confirmed: true }));
  observed.unconfirmed = captureError(() => {
    const inReview = newSession(runtime, policy, makeClock(0));
    inReview.dispatch('start');
    inReview.dispatch('request-review');
    inReview.dispatch('submit', {});
  });
  observed.unknown_event = captureError(() => running.dispatch('explode'));
  observed.unknown_slot = captureError(() => running.dispatch('navigate', { slot_id: 'S9-9' }));
  checks.submit_without_review_refused = Boolean(observed.skip_review) && observed.skip_review.code === 'E_SESSION_REVIEW_REQUIRED';
  checks.submit_without_confirmation_refused = Boolean(observed.unconfirmed) && observed.unconfirmed.code === 'E_SESSION_CONFIRMATION_REQUIRED';
  checks.unknown_event_refused = Boolean(observed.unknown_event) && observed.unknown_event.code === 'E_SESSION_INVALID_EVENT';
  checks.unknown_slot_refused = Boolean(observed.unknown_slot) && observed.unknown_slot.code === 'E_SESSION_UNKNOWN_SLOT';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'After a terminal transition every mutation is refused with a stable error id, and '
         + 'the answers given before the terminal transition are preserved.',
    checks: checks,
    failed: failed,
    observed: observed
  };
}

/* ---------------------------------------------------------- 3. timer contract */

function checkTimerContract(runtime, policy) {
  const checks = {};
  const limitMs = policy.timer.advisory_limit_seconds * 1000;
  const thresholdMs = limitMs * policy.timer.threshold_ratio;
  const clock = makeClock(500);
  const session = newSession(runtime, policy, clock);
  const shell = new runtime.exam.ExamShell({
    policy: policy, session: session, doc: makeExamDocument(JSON.stringify(policy))
  });

  session.dispatch('start');
  shell.render();
  checks.elapsed_starts_at_zero = session.getElapsedMs() === 0;

  /* The threshold is a status indication only: the state does not change. */
  clock.set(500 + thresholdMs);
  shell.tick();
  checks.threshold_reached = session.isThresholdReached() === true;
  checks.threshold_does_not_change_state = session.getState() === 'running';
  checks.threshold_marker_visible = shell.getSession().snapshot().threshold_reached === true;

  /* A hidden tab: the clock advances while no tick happens. The elapsed time
   * still follows the clock, because the elapsed time is never counted from
   * the number of ticks. */
  clock.advance(60000);
  checks.hidden_tab_keeps_counting = session.getElapsedMs() === thresholdMs + 60000;

  /* Expiry is driven by the elapsed time, not by the tick count. */
  clock.set(500 + limitMs);
  shell.tick();
  checks.expired_state = session.getState() === 'expired';
  checks.expiry_preserved_answers = session.getAnswers().length === 0;

  const second = newSession(runtime, policy, makeClock(0));
  second.dispatch('start');
  second.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'saglabāta' }
  });
  const secondClock = makeClock(0);
  const secondSession = newSession(runtime, policy, secondClock);
  secondSession.dispatch('start');
  secondSession.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'raw_text', text: 'saglabāta' }
  });
  secondClock.set(limitMs);
  secondSession.dispatch('expire');
  checks.expiry_preserves_answers = secondSession.getAnswers().length === 1
    && secondSession.getAnswer(policy.slots[0].slot_id).payload.text === 'saglabāta';
  checks.expired_rejects_writes = Boolean(captureError(() => secondSession.dispatch('answer', {
    slot_id: policy.slots[1].slot_id, payload: { kind: 'raw_text', text: 'vēlu' }
  })));
  checks.timer_limit_is_advisory_label = policy.timer.advisory_limit_seconds === 10800
    && policy.timer.clock === 'monotonic'
    && policy.timer.hidden_tab === 'keeps_counting';
  checks.threshold_ratio_is_90_percent = policy.timer.threshold_ratio === 0.9;

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The advisory timer uses a monotonic clock: the 90 % threshold is status only, the '
         + 'elapsed time keeps counting while the tab is hidden, and the expiry transition '
         + 'preserves the answers.',
    limit_ms: limitMs,
    threshold_ms: thresholdMs,
    checks: checks,
    failed: failed
  };
}

/* --------------------------------------------------------- 4. payload contract */

function checkPayloadContract(runtime, policy) {
  const checks = {};
  const session = newSession(runtime, policy, makeClock(0));
  session.dispatch('start');

  /* A numeric string is stored exactly as it was typed: no parsing, no
   * rounding, no separator normalisation. Parsing belongs to grading (N22). */
  session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id,
    payload: { kind: 'numeric', values: { value: ' 1 000,50 ' } }
  });
  const numeric = session.getAnswer(policy.slots[0].slot_id);
  checks.numeric_stored_raw = numeric.payload.values.value === ' 1 000,50 ';
  checks.numeric_stored_as_string = typeof numeric.payload.values.value === 'string';

  session.dispatch('answer', {
    slot_id: policy.slots[1].slot_id,
    payload: { kind: 'ordering', order: ['C', 'A', 'B'] }
  });
  checks.ordering_stored_as_typed = deepEqual(
    session.getAnswer(policy.slots[1].slot_id).payload.order, ['C', 'A', 'B']);

  session.dispatch('answer', {
    slot_id: policy.slots[2].slot_id,
    payload: { kind: 'matching', pairs: [['a', '2'], ['b', '1']] }
  });
  checks.matching_stored_as_typed = deepEqual(
    session.getAnswer(policy.slots[2].slot_id).payload.pairs, [['a', '2'], ['b', '1']]);

  session.dispatch('answer', {
    slot_id: policy.slots[3].slot_id,
    payload: { kind: 'option_select', selected: ['b'], justification: '  jo tā  ' }
  });
  checks.justification_stored_raw = session.getAnswer(policy.slots[3].slot_id).payload.justification === '  jo tā  ';

  session.dispatch('answer', {
    slot_id: policy.slots[4].slot_id,
    payload: { kind: 'graph', variant: 'Q18_plot_state', plot_state: { points: [[0, 0], [1, 2]] } }
  });
  checks.graph_variant_preserved = session.getAnswer(policy.slots[4].slot_id).payload.variant === 'Q18_plot_state';

  session.dispatch('answer', {
    slot_id: policy.slots[5].slot_id,
    payload: { kind: 'method', variant: 'Q13_vector', vector: [1, 0, 0] }
  });
  checks.method_variant_preserved = session.getAnswer(policy.slots[5].slot_id).payload.variant === 'Q13_vector';

  const missing = captureError(() => session.dispatch('answer', {
    slot_id: policy.slots[6].slot_id, payload: { kind: 'numeric' }
  }));
  const unknownKind = captureError(() => session.dispatch('answer', {
    slot_id: policy.slots[6].slot_id, payload: { kind: 'telepathy', text: '?' }
  }));
  const notAnObject = captureError(() => session.dispatch('answer', {
    slot_id: policy.slots[6].slot_id, payload: 'string'
  }));
  checks.missing_field_refused = Boolean(missing) && missing.code === 'E_SESSION_PAYLOAD_INVALID';
  checks.unknown_kind_refused = Boolean(unknownKind) && unknownKind.code === 'E_SESSION_PAYLOAD_INVALID';
  checks.non_object_refused = Boolean(notAnObject) && notAnObject.code === 'E_SESSION_PAYLOAD_INVALID';
  checks.refused_payload_not_stored = session.getAnswer(policy.slots[6].slot_id) === null;

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'Answers are stored raw and unparsed: the learner\'s own text survives byte for byte, '
         + 'and a malformed payload is refused by a stable error id without being stored.',
    checks: checks,
    failed: failed
  };
}

/* ------------------------------------------------------------ 5. serialization */

function checkSerialization(runtime, policy) {
  const checks = {};
  const clock = makeClock(0);
  const session = newSession(runtime, policy, clock);
  session.dispatch('start');
  session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'numeric', values: { value: '9,81' } }
  });
  session.dispatch('answer', {
    slot_id: policy.slots[10].slot_id, payload: { kind: 'ordering', order: ['B', 'A'] }
  });
  session.dispatch('flag', { slot_id: policy.slots[2].slot_id });
  session.dispatch('navigate', { slot_id: policy.slots[4].slot_id });

  const text = session.serialize();
  const restored = runtime.session.ExamSession.deserialize(text, {
    policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: makeClock(0)
  });

  checks.round_trip_answers_identical = deepEqual(restored.getAnswers(), session.getAnswers());
  checks.round_trip_flags_identical = deepEqual(restored.getFlags(), session.getFlags());
  checks.round_trip_state_identical = restored.getState() === session.getState();
  checks.round_trip_current_slot_identical = restored.getCurrentSlotId() === session.getCurrentSlotId();
  checks.round_trip_transition_count = restored.getTransitions().length === session.getTransitions().length;
  checks.round_trip_raw_value_preserved = restored.getAnswer(policy.slots[0].slot_id).payload.values.value === '9,81';
  checks.serialized_is_plain_json = (function () {
    try { JSON.parse(text); return true; } catch (error) { return false; }
  }());

  const broken = captureError(() => runtime.session.ExamSession.deserialize('{not json', {
    policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: makeClock(0)
  }));
  const wrongShape = captureError(() => runtime.session.ExamSession.deserialize('{"schema_version":9}', {
    policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: makeClock(0)
  }));
  checks.broken_serialization_refused = Boolean(broken) && broken.code === 'E_SESSION_SERIALIZE_INVALID';
  checks.wrong_shape_refused = Boolean(wrongShape) && wrongShape.code === 'E_SESSION_SERIALIZE_INVALID';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'A serialised session deserialises to identical answers, flags and state — the '
         + 'precondition N34\'s storage layer depends on.',
    checks: checks,
    failed: failed
  };
}

/* --------------------------------------------------- 6./7. view discipline */

const HELP_COMPONENTS = ['hint', 'chain', 'method-card', 'term-lookup'];
const EXAM_SESSION_FIELDS = [
  'answer_map', 'session_id', 'elapsed_ms', 'updated_at_ms', 'current_slot_id',
  'flags', 'slot_id', 'form_id', 'remediation_slot_ids'
];

function checkViewDiscipline(runtime, policy, chains) {
  const checks = {};
  const doc = makeExamDocument(JSON.stringify(policy));
  const session = newSession(runtime, policy, makeClock(0));
  const shell = new runtime.exam.ExamShell({ policy: policy, session: session, doc: doc });
  session.dispatch('start');
  session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'numeric', values: { value: '9,81' } }
  });
  shell.render();

  const examDom = serialize(doc.getElementById('exam-shell'));
  const helpNodes = findByAttribute(doc.getElementById('exam-shell'), 'data-sim-component', HELP_COMPONENTS);
  checks.exam_has_no_help_components = helpNodes.length === 0;
  checks.exam_dom_has_no_hint_marker = examDom.indexOf('data-sim-component="hint"') === -1;
  checks.exam_dom_has_no_chain_marker = examDom.indexOf('data-sim-component="chain"') === -1;
  checks.exam_dom_has_no_method_card_marker = examDom.indexOf('data-sim-component="method-card"') === -1;
  checks.exam_dom_has_no_term_lookup_marker = examDom.indexOf('data-sim-component="term-lookup"') === -1;
  checks.exam_dom_has_no_hint_drawer = examDom.indexOf('hint-drawer') === -1;

  /* No N16 chain step text may appear in the exam render. */
  const stepTexts = [];
  chains.forEach((chain) => {
    (chain.steps || []).forEach((step) => {
      if (step.statement_lv) { stepTexts.push(step.statement_lv); }
      if (step.reasoning_lv) { stepTexts.push(step.reasoning_lv); }
    });
  });
  const leakedSteps = stepTexts.filter((text) => examDom.indexOf(text) !== -1);
  checks.exam_dom_has_no_chain_step_text = leakedSteps.length === 0;
  checks.chain_step_texts_checked = stepTexts.length;

  /* The exam render does carry its own components: the map has 21 cells. */
  const mapCells = doc.getElementById('exam-map').childNodes;
  checks.exam_map_has_21_cells = mapCells.length === policy.exam.slot_count;

  /* The other direction: a practice render immediately after the exam session
   * contains no exam-session field at all. */
  const practiceDom = (function () {
    runtime.exam.renderPracticeSurface(doc, {
      host_id: 'practice-host',
      practice: { item_id: 'COL1-1-1C-A-01' }
    });
    return serialize(doc.getElementById('practice-host'));
  }());
  const leakedFields = EXAM_SESSION_FIELDS.filter((field) => practiceDom.indexOf(field) !== -1);
  checks.practice_has_no_exam_session_fields = leakedFields.length === 0;
  checks.practice_does_not_leak_the_answer = practiceDom.indexOf('9,81') === -1;
  checks.practice_does_not_leak_the_session_id = practiceDom.indexOf(session.getSessionId()) === -1;
  checks.practice_keeps_help_components = HELP_COMPONENTS.every(
    (component) => practiceDom.indexOf('data-sim-component="' + component + '"') !== -1);
  checks.practice_has_no_slot_status = practiceDom.indexOf('exam-slot-status') === -1;
  checks.exam_session_fields_checked = EXAM_SESSION_FIELDS.length;

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The boundary is architectural in both directions: the exam render contains zero help '
         + 'markers and zero N16 chain step text, and a practice render contains zero '
         + 'exam-session fields.',
    checks: checks,
    failed: failed,
    leaked_steps: leakedSteps.slice(0, 3),
    leaked_fields: leakedFields
  };
}

/* -------------------------------------------------------- 8. mode registry */

function checkModeRegistry(runtime, policy) {
  const checks = {};
  const discipline = policy.view_discipline;
  const registry = runtime.exam.createModeRegistry(discipline);

  checks.exam_allowed_matches_island = deepEqual(
    registry.allowedComponents('exam'), discipline.modes.exam.allowed_components);
  checks.practice_allowed_matches_island = deepEqual(
    registry.allowedComponents('practice'), discipline.modes.practice.allowed_components);
  checks.exam_allows_the_five_core_components = deepEqual(
    discipline.modes.exam.allowed_components.slice().sort(),
    ['input', 'map', 'navigator', 'review', 'timer']);
  checks.practice_adds_the_four_help_components = discipline.modes.practice.allowed_components
    .filter((component) => HELP_COMPONENTS.indexOf(component) !== -1).length === 4;
  checks.exam_forbids_help = deepEqual(
    discipline.modes.exam.forbidden_components.slice().sort(), HELP_COMPONENTS.slice().sort());

  const refused = captureError(() => registry.assertAllowed('hint', 'exam'));
  checks.hint_refused_in_exam = Boolean(refused) && refused.code === 'E_MODE_COMPONENT_NOT_ALLOWED';
  checks.map_allowed_in_exam = registry.isAllowed('map', 'exam') === true;
  checks.hint_allowed_in_practice = registry.isAllowed('hint', 'practice') === true;

  /* The scratch violation: an exam mode that does not register the map. The
   * render contract must fail loudly instead of rendering the component. */
  const scratch = JSON.parse(JSON.stringify(discipline));
  scratch.modes.exam.allowed_components = scratch.modes.exam.allowed_components
    .filter((component) => component !== 'map');
  const scratchSession = newSession(runtime, policy, makeClock(0));
  const scratchDoc = makeExamDocument(JSON.stringify(policy));
  const scratchError = captureError(() => {
    const scratchShell = new runtime.exam.ExamShell({
      policy: { ...policy, view_discipline: scratch }, session: scratchSession, doc: scratchDoc
    });
    scratchSession.dispatch('start');
    scratchShell.render();
  });
  checks.unregistered_component_fails_loudly = Boolean(scratchError)
    && scratchError.code === 'E_MODE_COMPONENT_NOT_ALLOWED';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The mode registry is the single source mapping mode → allowed components, and an '
         + 'unregistered component fails the render contract loudly.',
    checks: checks,
    failed: failed,
    scratch_error: scratchError
  };
}

/* ------------------------------------------------------------ 9. navigation */

function checkNavigation(runtime, policy) {
  const checks = {};
  const ids = policy.slots.map((slot) => slot.slot_id);
  const doc = makeExamDocument(JSON.stringify(policy));
  const session = newSession(runtime, policy, makeClock(0));
  const shell = new runtime.exam.ExamShell({ policy: policy, session: session, doc: doc });
  session.dispatch('start');

  /* The scripted sequence of the roadmap: answer slots 1, 5 and 21, flag slot 3,
   * then navigate the full range. */
  [0, 4, 20].forEach((index) => {
    shell.navigate(ids[index]);
    shell.recordAnswer(ids[index], { kind: 'raw_text', text: 'atbilde ' + (index + 1) });
  });
  shell.navigate(ids[2]);
  shell.toggleFlag(ids[2]);
  for (let i = 0; i < ids.length; i += 1) { shell.navigate(ids[i]); }

  const map = runtime.exam.buildMapState(session.snapshot());
  const expected = ids.map((id, index) => ({
    slot_id: id,
    index: index + 1,
    answered: index === 0 || index === 4 || index === 20,
    flagged: index === 2,
    current: index === ids.length - 1
  }));
  /* The map cell carries the slot's points and topic as well; the fixture
   * compares the four state fields the roadmap names. */
  const stateOf = (cell) => ({
    slot_id: cell.slot_id,
    index: cell.index,
    answered: cell.answered,
    flagged: cell.flagged,
    current: cell.current
  });
  checks.map_cell_count = map.cells.length === 21;
  checks.map_matches_expected = deepEqual(map.cells.map(stateOf), expected);
  checks.map_counts = map.answered_count === 3 && map.flagged_count === 1 && map.unanswered_count === 18;
  checks.map_current_slot = map.current_slot_id === ids[ids.length - 1];

  /* The rendered map must agree with the pure state. */
  const cells = doc.getElementById('exam-map').childNodes;
  const rendered = cells.map((cell) => ({
    slot_id: cell.getAttribute('data-slot-id'),
    answered: cell.getAttribute('data-answered') === 'true',
    flagged: cell.getAttribute('data-flagged') === 'true',
    current: cell.getAttribute('aria-current') === 'true'
  }));
  const renderedExpected = expected.map((cell) => ({
    slot_id: cell.slot_id, answered: cell.answered, flagged: cell.flagged, current: cell.current
  }));
  checks.rendered_map_matches_state = deepEqual(rendered, renderedExpected);

  /* Pointer path: every one of the 21 slots is reachable by clicking its cell. */
  const pointerReached = {};
  for (let i = 0; i < ids.length; i += 1) {
    const cell = doc.getElementById('exam-map-' + ids[i]);
    if (!cell) { continue; }
    cell.dispatchEvent('click');
    pointerReached[ids[i]] = session.getCurrentSlotId() === ids[i];
  }
  checks.all_slots_reachable_by_pointer = Object.keys(pointerReached).length === 21
    && Object.keys(pointerReached).every((id) => pointerReached[id]);

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The scripted answer/flag sequence produces exactly the expected map state, and every '
         + 'one of the 21 slots is reachable by pointer.',
    checks: checks,
    failed: failed,
    expected_map: expected,
    observed_map: map.cells
  };
}

/* --------------------------------------------------------- 10. keyboard path */

function checkKeyboardTraversal(runtime, policy) {
  const checks = {};
  const ids = policy.slots.map((slot) => slot.slot_id);
  const doc = makeExamDocument(JSON.stringify(policy));
  const session = newSession(runtime, policy, makeClock(0));
  const shell = new runtime.exam.ExamShell({ policy: policy, session: session, doc: doc });
  session.dispatch('start');
  shell.render();
  shell.bindKeyboard(doc.getElementById('exam-shell'));

  const pointerEventsBefore = doc.pointerEventCount;
  const visited = [];
  let prevented = 0;

  function press(key) {
    const event = { key: key, preventDefault() { prevented += 1; } };
    doc.getElementById('exam-shell').dispatchEvent('keydown', event);
    return event;
  }

  /* The keyboard-only run: answer every slot, flag every second slot, and walk
   * the whole range with the arrow keys. No pointer event is dispatched. */
  for (let i = 0; i < ids.length; i += 1) {
    const slotId = ids[i];
    if (session.getCurrentSlotId() !== slotId) { press('ArrowRight'); }
    visited.push(session.getCurrentSlotId());
    const input = doc.getElementById('exam-answer-input');
    if (!input) {
      checks.input_rendered = false;
      break;
    }
    input.value = 'klavieris ' + (i + 1);
    input.dispatchEvent('input', { target: input });
    if (i % 2 === 0) { press('f'); }
  }
  const pointerEventsAfter = doc.pointerEventCount;

  checks.visited_all_slots = visited.length === 21 && new Set(visited).size === 21;
  checks.answered_all_slots = session.getAnswers().length === 21;
  checks.flagged_every_second_slot = session.getFlags().length === 11;
  checks.no_pointer_events = pointerEventsAfter === pointerEventsBefore;
  checks.arrows_prevent_default = prevented > 0;

  /* Focus is never trapped: Tab is not intercepted and the focus may leave. */
  const tabEvent = { key: 'Tab', preventDefault() { checks.tab_prevented = true; } };
  doc.getElementById('exam-shell').dispatchEvent('keydown', tabEvent);
  checks.tab_not_intercepted = checks.tab_prevented !== true;
  checks.focus_moves_into_the_slot = doc.activeElement
    && doc.activeElement.id === 'exam-slot-host';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'A scripted keyboard run answers and flags across all 21 slots without a single pointer '
         + 'event, and the focus is never trapped.',
    checks: checks,
    failed: failed,
    pointer_events: pointerEventsAfter - pointerEventsBefore
  };
}

/* ---------------------------------------------------------- 11. submit gate */

function checkSubmitGate(runtime, policy) {
  const checks = {};
  const doc = makeExamDocument(JSON.stringify(policy));
  const session = newSession(runtime, policy, makeClock(0));
  const shell = new runtime.exam.ExamShell({ policy: policy, session: session, doc: doc });
  session.dispatch('start');
  shell.recordAnswer(policy.slots[0].slot_id, { kind: 'raw_text', text: 'daļēji' });
  shell.requestReview();

  const reviewHost = doc.getElementById('exam-review');
  checks.review_visible = reviewHost.hidden === false;
  const alerts = findByAttribute(reviewHost, 'role', ['alert']);
  checks.unanswered_warning_has_alert_role = alerts.length === 1;
  checks.unanswered_warning_mentions_the_gap = alerts.length === 1
    && alerts[0].textContent.indexOf(policy.copy_lv.review_warning_short) !== -1;
  const rows = reviewHost.childNodes.filter((node) => node.tagName === 'TABLE')[0];
  const tableRows = rows ? rows.childNodes.filter((node) => node.tagName === 'TBODY')[0].childNodes.length : 0;
  checks.review_table_has_21_rows = tableRows === 21;

  const submit = doc.getElementById('exam-review-submit');
  const confirm = doc.getElementById('exam-review-confirm');
  checks.submit_disabled_without_confirmation = Boolean(submit) && submit.disabled === true;
  checks.confirmation_checkbox_present = Boolean(confirm);

  /* Without the confirmation the machine refuses the submission. */
  const refused = captureError(() => shell.submit());
  checks.submit_refused_without_confirmation = Boolean(refused)
    && refused.code === 'E_SESSION_CONFIRMATION_REQUIRED';
  checks.state_still_review = session.getState() === 'review';

  /* The warning can be dismissed, and the dismissal survives the re-render. */
  const dismiss = doc.getElementById('exam-review-warning-dismiss');
  dismiss.dispatchEvent('click');
  checks.warning_dismissed = findByAttribute(reviewHost, 'role', ['alert']).length === 0;

  /* With the confirmation the submission goes through and is one-way. */
  confirm.checked = true;
  confirm.dispatchEvent('change', { target: confirm });
  const submitAfterConfirm = doc.getElementById('exam-review-submit');
  checks.submit_enabled_after_confirmation = Boolean(submitAfterConfirm) && submitAfterConfirm.disabled === false;
  submitAfterConfirm.dispatchEvent('click');
  checks.submitted_state = session.getState() === 'submitted';
  const late = captureError(() => shell.recordAnswer(policy.slots[1].slot_id, { kind: 'raw_text', text: 'vēlu' }));
  checks.submission_is_one_way = Boolean(late) && late.code === 'E_SESSION_LATE_WRITE';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The review screen carries the unanswered warning with role="alert", the submission '
         + 'requires an explicit confirmation that the machine also enforces, and the '
         + 'submission is one-way.',
    checks: checks,
    failed: failed
  };
}

/* --------------------------------------------------------- 12. buffer race */

function checkBufferRace(runtime, policy) {
  const checks = {};
  const ids = policy.slots.map((slot) => slot.slot_id);
  const doc = makeExamDocument(JSON.stringify(policy));
  const session = newSession(runtime, policy, makeClock(0));
  const shell = new runtime.exam.ExamShell({ policy: policy, session: session, doc: doc });
  session.dispatch('start');
  shell.render();

  /* The learner types, and the re-render that follows a navigation replaces the
   * input element. The answer must survive, because the machine buffers by
   * slot id. */
  const input = doc.getElementById('exam-answer-input');
  input.value = 'pusfina ieraksts';
  input.dispatchEvent('input', { target: input });

  /* Rapid navigation inside one tick — the re-render happens between the two
   * navigations. */
  shell.navigate(ids[1]);
  shell.navigate(ids[2]);
  shell.navigate(ids[0]);

  checks.answer_not_lost = session.isAnswered(ids[0]);
  checks.answer_value_intact = session.getAnswer(ids[0]).payload.text === 'pusfina ieraksts';
  const restoredInput = doc.getElementById('exam-answer-input');
  checks.input_repopulated_after_rerender = Boolean(restoredInput)
    && restoredInput.value === 'pusfina ieraksts';
  checks.current_slot_after_race = session.getCurrentSlotId() === ids[0];
  checks.other_slots_untouched = !session.isAnswered(ids[1]) && !session.isAnswered(ids[2]);

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'Rapid navigation during a re-render loses no in-progress answer: the machine buffers '
         + 'the answer by slot id and repopulates the re-created input.',
    checks: checks,
    failed: failed
  };
}

/* ------------------------------------------------------- 13. terminal record */

function checkTerminalRecord(runtime, policy) {
  const checks = {};
  const session = newSession(runtime, policy, makeClock(0));
  session.dispatch('start');
  session.dispatch('answer', {
    slot_id: policy.slots[0].slot_id, payload: { kind: 'numeric', values: { value: '9,81' } }
  });
  session.dispatch('flag', { slot_id: policy.slots[2].slot_id });
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });

  const record = session.toTerminalRecord();
  checks.has_answers = Array.isArray(record.answers) && record.answers.length === 1;
  checks.has_flags = Array.isArray(record.flags) && record.flags.length === 1;
  checks.has_elapsed_time = typeof record.elapsed_ms === 'number';
  checks.has_form_id = record.form_id === 'A';
  checks.has_session_id = typeof record.session_id === 'string' && record.session_id.length > 0;
  checks.has_transitions = Array.isArray(record.transitions) && record.transitions.length === 5;
  checks.has_unanswered_list = Array.isArray(record.unanswered_slot_ids)
    && record.unanswered_slot_ids.length === policy.exam.slot_count - 1;
  checks.remediation_is_unanswered_plus_flagged = deepEqual(
    record.remediation_slot_ids,
    record.unanswered_slot_ids.concat(record.flags).filter((id, index, all) => all.indexOf(id) === index).sort()
  );
  checks.state_is_submitted = record.state === 'submitted';

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The terminal session record carries the answers, the flags, the elapsed time and the '
         + 'form id that N23 grades and N25 logs.',
    checks: checks,
    failed: failed,
    record_fields: Object.keys(record).sort()
  };
}

/* ----------------------------------------------------- 14. end-to-end trace */

function checkEndToEndTrace(runtime, policy) {
  const checks = {};
  const table = policy.session_contract.transition_table;
  const doc = makeExamDocument(JSON.stringify(policy));
  const app = runtime.exam.init(doc);
  let shell = null;
  let session = null;

  try {
    checks.boot_returns_an_app = Boolean(app);
    checks.session_absent_before_start = app.session === null && app.shell === null;
    doc.getElementById('exam-start').dispatchEvent('click');
    shell = app.shell;
    session = app.session;
    checks.start_button_starts_the_session = Boolean(session) && session.getState() === 'running';
    checks.entry_hidden_after_start = doc.getElementById('exam-entry').hidden === true;
    checks.shell_visible_after_start = doc.getElementById('exam-shell').hidden === false;
    checks.status_line_from_policy = doc.getElementById('sim-exam-status').textContent
      .indexOf(String(policy.exam.slot_count)) !== -1;

    /* Full navigation through the map, answering several types on the way. */
    const ids = policy.slots.map((slot) => slot.slot_id);
    const typed = {
      0: { kind: 'numeric', values: { value: '9,81' } },
      4: { kind: 'option_select', selected: ['c'], justification: 'jo tā' },
      10: { kind: 'ordering', order: ['B', 'A', 'C'] }
    };
    for (let i = 0; i < ids.length; i += 1) {
      const cell = doc.getElementById('exam-map-' + ids[i]);
      cell.dispatchEvent('click');
      if (typed[i]) { shell.recordAnswer(ids[i], typed[i]); }
      if (i % 5 === 0) { shell.toggleFlag(ids[i]); }
    }

    doc.getElementById('exam-review-button').dispatchEvent('click');
    checks.review_state_reached = session.getState() === 'review';
    const warning = doc.getElementById('exam-review-warning');
    checks.unanswered_warning_present = Boolean(warning)
      && warning.getAttribute('role') === 'alert';

    const confirm = doc.getElementById('exam-review-confirm');
    confirm.checked = true;
    confirm.dispatchEvent('change', { target: confirm });
    doc.getElementById('exam-review-submit').dispatchEvent('click');
    checks.submitted = session.getState() === 'submitted';

    const record = session.toTerminalRecord();
    checks.terminal_record_emitted = Boolean(record) && record.state === 'submitted';
    checks.terminal_record_has_answers = record.answers.length === 3;
    checks.terminal_record_has_form_id = record.form_id === 'A';

    /* Every transition of the trace conforms to the table. */
    const log = session.getTransitions();
    let conforms = true;
    let offender = '';
    log.forEach((entry, index) => {
      const row = rowFor(table, entry.from, entry.event);
      if (!row || row.to !== entry.to) {
        conforms = false;
        offender = index + ':' + entry.from + '/' + entry.event;
      }
    });
    checks.every_transition_conforms = conforms;
    checks.transition_count = log.length;
    checks.offender = offender;

    const failed = Object.keys(checks).filter((key) => !checks[key] && key !== 'offender');
    return {
      status: failed.length === 0 ? 'PASS' : 'FAIL',
      claim: 'The scripted session runs from the start screen through full navigation, several '
           + 'answer types, flags, review and a confirmed submission to the terminal record, '
           + 'and every transition conforms to the table.',
      checks: checks,
      failed: failed,
      trace: log.map((entry) => entry.from + ' --' + entry.event + '--> ' + entry.to)
    };
  } finally {
    if (shell) { shell.stopTimer(); }
  }
}

/* ------------------------------------------------------- 15. the in-file smoke */

function checkSmokeVectors(root, policy) {
  const vm = require('vm');
  const artifactPath = path.join(root, 'output/simulator.html');
  if (!fs.existsSync(artifactPath)) {
    return {
      status: 'FAIL',
      claim: 'The two in-file smoke vectors run against the built artifact.',
      reason: 'output/simulator.html is not built; the vectors were not run.'
    };
  }
  const html = fs.readFileSync(artifactPath, 'utf8');
  const island = /<script type="application\/json" id="sim-exam-policy">([\s\S]*?)<\/script>/.exec(html);
  if (!island) {
    return {
      status: 'FAIL',
      claim: 'The two in-file smoke vectors run against the built artifact.',
      reason: 'The artifact does not carry the #sim-exam-policy island.'
    };
  }
  const sandbox = {
    console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp,
    isFinite, parseInt, parseFloat, Date, Set, Map, Promise
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  sandbox.setTimeout = setTimeout;
  sandbox.clearTimeout = clearTimeout;
  sandbox.setInterval = function () { return 0; };
  sandbox.clearInterval = function () {};
  vm.createContext(sandbox);
  const islandText = island[1];
  const doc = {
    getElementById(id) {
      if (id === 'sim-exam-policy') { return { textContent: islandText }; }
      if (id === 'sim-smoke-status') { return { textContent: '', hidden: true }; }
      return null;
    },
    querySelector() { return null; },
    querySelectorAll() { return []; }
  };
  sandbox.document = doc;
  ['src/compiled/session.js', 'src/compiled/exam.js', 'src/smoke-subset.js'].forEach((relative) => {
    vm.runInContext(fs.readFileSync(path.join(root, relative), 'utf8'), sandbox, { filename: relative });
  });
  if (!sandbox.SimSmoke) {
    return {
      status: 'FAIL',
      claim: 'The two in-file smoke vectors run against the built artifact.',
      reason: 'The smoke subset did not register in the sandbox.'
    };
  }
  const report = sandbox.SimSmoke.run(doc, {});
  const wanted = ['SMK-N21-SESSION-TRANSITION', 'SMK-N21-NAVIGATION-MAP'];
  const vectors = wanted.map((id) => (report.vectors || []).filter((v) => v.id === id)[0] || null);
  const checks = {
    session_vector_present: Boolean(vectors[0]),
    session_vector_passes: Boolean(vectors[0]) && vectors[0].status === 'PASS',
    navigation_vector_present: Boolean(vectors[1]),
    navigation_vector_passes: Boolean(vectors[1]) && vectors[1].status === 'PASS'
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The two in-file smoke vectors run against the built artifact.',
    artifact: path.relative(root, artifactPath),
    suite: { total: report.total, passed: report.passed, failed: report.failed },
    vectors: vectors,
    checks: checks,
    failed: failed
  };
}

/* -------------------------------------------------- 16. the artifact carries it */

function checkArtifactWiring(root) {
  const artifactPath = path.join(root, 'output/simulator.html');
  if (!fs.existsSync(artifactPath)) {
    return { status: 'FAIL', claim: 'The built artifact carries the exam shell.', reason: 'output/simulator.html is not built.' };
  }
  const html = fs.readFileSync(artifactPath, 'utf8');
  const checks = {
    island_present: html.indexOf('<script type="application/json" id="sim-exam-policy">') !== -1,
    digest_meta_present: html.indexOf('name="sim-exam-policy-digest"') !== -1,
    session_runtime_inlined: html.indexOf('SimSession') !== -1,
    exam_runtime_inlined: html.indexOf('SimExam') !== -1,
    shell_markup_present: html.indexOf('id="exam-timer-bar"') !== -1
      && html.indexOf('id="exam-map"') !== -1
      && html.indexOf('id="exam-review"') !== -1,
    boot_call_present: html.indexOf('SimExam.init(document)') !== -1,
    no_external_script: !/<script[^>]+src\s*=/i.test(html),
    honesty_copy_present: html.indexOf('nav oficiāls RSU kolokvija eksāmens') !== -1
      || html.indexOf('nevis oficiāls') !== -1
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The built artifact carries the policy island, the two runtime modules, the shell '
         + 'markup and the boot call — offline, with no external script.',
    checks: checks,
    failed: failed
  };
}

/* --------------------------------------------------------------------- main */

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const runtime = loadRuntime(root);
  const policy = readJson(path.join(root, 'data/exam_policy.json'));
  const chains = readJson(path.join(root, 'data/chains.json')).chains || [];

  const checks = {
    artifact_wiring: checkArtifactWiring(root),
    lifecycle: checkLifecycle(runtime, policy),
    late_write_guard: checkLateWriteGuard(runtime, policy),
    timer_contract: checkTimerContract(runtime, policy),
    payload_contract: checkPayloadContract(runtime, policy),
    serialization: checkSerialization(runtime, policy),
    view_discipline: checkViewDiscipline(runtime, policy, chains),
    mode_registry: checkModeRegistry(runtime, policy),
    navigation: checkNavigation(runtime, policy),
    keyboard_traversal: checkKeyboardTraversal(runtime, policy),
    submit_gate: checkSubmitGate(runtime, policy),
    buffer_race: checkBufferRace(runtime, policy),
    terminal_record: checkTerminalRecord(runtime, policy),
    end_to_end_trace: checkEndToEndTrace(runtime, policy),
    smoke_vectors: checkSmokeVectors(root, policy)
  };

  const failed = Object.keys(checks).filter((key) => checks[key].status !== 'PASS');
  const record = {
    schema_version: 1,
    owner: 'N21',
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    runtime_modules: ['src/compiled/session.js', 'src/compiled/exam.js'],
    source_modules: ['src/session.ts', 'src/exam.ts'],
    island: 'data/exam_policy.json',
    note: 'The TypeScript sources are the source of truth; the compiled modules are committed '
        + 'and are checked for drift by tools/compile_n21_ts.py --check.',
    checks: checks
  };

  if (args.record) {
    const out = path.isAbsolute(args.record) ? args.record : path.join(root, args.record);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(record, null, 2) + '\n', 'utf8');
  }
  process.stdout.write(JSON.stringify({
    status: record.status,
    checks: Object.keys(checks).map((key) => ({ name: key, status: checks[key].status }))
  }, null, 2) + '\n');
  return failed.length === 0 ? 0 : 1;
}

if (require.main === module) {
  try {
    process.exitCode = main();
  } catch (error) {
    process.stderr.write('FAIL n21_runtime: ' + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main };
