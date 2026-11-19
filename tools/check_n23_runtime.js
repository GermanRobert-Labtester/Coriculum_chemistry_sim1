#!/usr/bin/env node
/* N23 runtime harness: the graded record, the analytics chain, the render stub
 * and the determinism proof.
 *
 * The harness loads the committed TypeScript runtime modules
 * (src/compiled/{session,exam,grading,feedback}.js and src/compiled/inputs/*.js),
 * the frozen engines from src/ (quantity, method and graph scoring — all of them
 * ship from src/) and the islands from data/. It proves the claims the roadmap
 * asks N23 to prove in Main Step C, against the frozen contract in
 * docs/GRADING_FORMAT.md:
 *
 *   1. score_matrix_grading   — the four scripted forms (FX-N23-FULL, -PARTIAL,
 *                               -ZERO, -MIXED) are built through the N21 session
 *                               machine, graded through the frozen engine
 *                               contracts, assembled and compared with the
 *                               fixture's hand-computed sums (AC1);
 *   2. analytics_chain        — terminal digest -> graded digest -> events, every
 *                               event digest-linked, remediation-state events
 *                               exactly for the incorrect/malformed slots with a
 *                               mapped remediation, and no answer text in any
 *                               event (§7);
 *   3. render_fixture         — the mixed-form score report is the DOM stub of §8:
 *                               unblended totals, pending labels, one honesty
 *                               note, feedback cards with remediation
 *                               data-attributes, the preserved raw input line;
 *   4. determinism            — the mixed form graded twice in-process and once
 *                               in a fresh Node process yields byte-identical
 *                               canonical digests, and a JSON round-trip keeps
 *                               the canonical text identical (§9);
 *   5. batch_digest           — one sha256 over the canonical concatenation of
 *                               every graded digest (the score matrix plus the
 *                               classification table when it exists) and the
 *                               grading module digests;
 *   6. smoke_vectors_in_file  — the three SMK-N23-* vectors registered in
 *                               src/smoke-subset.js run and pass.
 *
 * Pre-integration honesty: src/compiled/grading.js, src/compiled/feedback.js,
 * data/grading_policy.json and data/feedback_classification.json are authored by
 * parallel subagents. When any of them is missing the harness exits 3 (PENDING)
 * with a named list of exactly the missing files; it never reports a quiet pass
 * and never invents a grading result. Exit 1 is reserved for a real assertion
 * failure, exit 2 for a harness crash.
 *
 * The harness is not a browser render, screen-reader or instructor acceptance
 * claim. It is a machine-level proof of the grading and feedback contract.
 *
 * Usage: node tools/check_n23_runtime.js [--repo-root .] [--record PATH]
 *          [--chain PATH] [--render PATH] [--determinism PATH] [--driver-dir DIR]
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');
const { execFileSync } = require('child_process');

/* ------------------------------------------------------------------ arguments */

function parseArgs(argv) {
  const args = {
    repoRoot: path.resolve(__dirname, '..'),
    record: null,
    chain: null,
    render: null,
    determinism: null,
    driverDir: null
  };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--chain') { args.chain = argv[i + 1]; i += 1; }
    else if (argv[i] === '--render') { args.render = argv[i + 1]; i += 1; }
    else if (argv[i] === '--determinism') { args.determinism = argv[i + 1]; i += 1; }
    else if (argv[i] === '--driver-dir') { args.driverDir = argv[i + 1]; i += 1; }
  }
  return args;
}

/* -------------------------------------------------------------------- helpers */

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function exists(file) {
  return fs.existsSync(file);
}

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function sha256File(file) {
  return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
}

function fileRecord(root, relative) {
  const file = path.join(root, relative);
  if (!exists(file)) { return { path: relative, bytes: null, sha256: null, missing: true }; }
  return { path: relative, bytes: fs.statSync(file).size, sha256: sha256File(file) };
}

function makeClock(startMs) {
  let current = startMs || 0;
  return {
    now() { return current; },
    advance(ms) { current += ms; return current; }
  };
}

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

function deepEqual(a, b) {
  return canonical(a) === canonical(b);
}

/** The canonical projection: sorted keys, no whitespace, UTF-8-able text. */
function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return String(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.map((key) => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
}

function countOccurrences(text, needle) {
  if (!needle) { return 0; }
  return text.split(needle).length - 1;
}

function firstDefined(object, keys) {
  if (!object || typeof object !== 'object') { return undefined; }
  for (let i = 0; i < keys.length; i += 1) {
    if (Object.prototype.hasOwnProperty.call(object, keys[i]) && object[keys[i]] !== undefined) {
      return object[keys[i]];
    }
  }
  return undefined;
}

function pickString(object, keys) {
  const value = firstDefined(object, keys);
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function isNumber(value) {
  return typeof value === 'number' && isFinite(value);
}

function assertion(id, ok, detail) {
  return { id: id, ok: ok === true, detail: detail === undefined ? null : detail };
}

function pendingAssertion(id, reason) {
  return { id: id, ok: null, status: 'PENDING', detail: reason };
}

/* ------------------------------------------------------------------- islands */

const FIGURE_PATHS = [
  'data/figures_t12.json',
  'data/figures_t23.json',
  'data/figures_t4.json',
  'data/figures_t5.json',
  'data/figures_t67.json'
];

/** The two N23 islands; both are parallel-authored data, so both are optional today. */
const N23_ISLAND_FILES = {
  'sim-grading-policy': 'data/grading_policy.json',
  'sim-feedback-classification': 'data/feedback_classification.json'
};

function buildIslands(root) {
  const islands = {};
  islands['sim-conventions'] = readJson(path.join(root, 'data/conventions.json'));
  islands['sim-terms'] = readJson(path.join(root, 'data/terms.json'));
  islands['sim-engines'] = readJson(path.join(root, 'data/engine_taxonomy.json'));
  islands['sim-graph-scoring'] = readJson(path.join(root, 'data/graph_scoring_contract.json'));
  islands['sim-method-engine'] = readJson(path.join(root, 'data/method_engine_contract.json'));
  islands['sim-method-cards'] = readJson(path.join(root, 'data/method_cards.json'));
  islands['sim-exam-policy'] = readJson(path.join(root, 'data/exam_policy.json'));
  /* The feedback module resolves remediation ids against the chains island. */
  islands['sim-chains'] = readJson(path.join(root, 'data/chains.json'));
  const figures = { island_id: 'sim-figures', figures: [] };
  FIGURE_PATHS.forEach((relative) => {
    const source = readJson(path.join(root, relative));
    (source.figures || []).forEach((figure) => { figures.figures.push(figure); });
  });
  islands['sim-figures'] = figures;
  if (exists(path.join(root, 'data/response_types.json'))) {
    islands['sim-response-types'] = readJson(path.join(root, 'data/response_types.json'));
  }
  Object.keys(N23_ISLAND_FILES).forEach((id) => {
    const file = path.join(root, N23_ISLAND_FILES[id]);
    if (exists(file)) { islands[id] = readJson(file); }
  });
  return islands;
}

function makeDocument(islands) {
  const registry = Object.create(null);
  Object.keys(islands).forEach((id) => {
    registry[id] = { id: id, textContent: JSON.stringify(islands[id]) };
  });
  return {
    getElementById(id) { return registry[id] || null; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    createElement() { return {}; }
  };
}

/* ------------------------------------------------------------------- sandbox */

const ENGINE_MODULES = [
  'src/quantity-engine.js',
  'src/method-engine.js',
  'src/graph-scoring-engine.js'
];

const RUNTIME_MODULES = [
  'src/compiled/session.js',
  'src/compiled/exam.js',
  'src/compiled/inputs/registry.js',
  'src/compiled/inputs/components.js',
  'src/compiled/inputs/integration.js'
];

/** The parallel-authored grading runtime; absent until the official compile. */
const GRADING_MODULES = [
  'src/compiled/grading.js',
  'src/compiled/feedback.js'
];

const GRADING_SOURCES = [
  'src/grading.ts',
  'src/feedback.ts'
];

function missingFiles(root, relatives) {
  return relatives.filter((relative) => !exists(path.join(root, relative)));
}

function makeSandbox(root, islands, options) {
  const settings = options || {};
  const doc = makeDocument(islands);
  const globals = {
    console: console, document: doc, JSON: JSON, Error: Error, TypeError: TypeError,
    RangeError: RangeError, String: String, Object: Object, Array: Array, Math: Math,
    Number: Number, Boolean: Boolean, RegExp: RegExp, isFinite: isFinite, isNaN: isNaN,
    parseInt: parseInt, parseFloat: parseFloat, Date: Date, Map: Map, Set: Set,
    Promise: Promise, unescape: unescape, escape: escape,
    encodeURIComponent: encodeURIComponent, decodeURIComponent: decodeURIComponent
  };
  if (typeof TextEncoder !== 'undefined') { globals.TextEncoder = TextEncoder; }
  if (typeof TextDecoder !== 'undefined') { globals.TextDecoder = TextDecoder; }
  const sandbox = globals;
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  const modules = ENGINE_MODULES.concat(RUNTIME_MODULES);
  if (settings.withGrading !== false) {
    GRADING_MODULES.forEach((relative) => {
      if (exists(path.join(root, relative))) { modules.push(relative); }
    });
  }
  modules.forEach((relative) => {
    vm.runInContext(fs.readFileSync(path.join(root, relative), 'utf8'), sandbox, { filename: relative });
  });
  return sandbox;
}

/* ---------------------------------------------------------------------- bank */

function loadBank(root) {
  const bank = Object.create(null);
  const byType = Object.create(null);
  const directory = path.join(root, 'data/bank');
  fs.readdirSync(directory).sort().forEach((file) => {
    if (!file.endsWith('.json')) { return; }
    const document = readJson(path.join(directory, file));
    (document.questions || []).forEach((question) => {
      bank[question.question_id] = question;
      if (question.type_id && !byType[question.type_id]) { byType[question.type_id] = question.question_id; }
    });
  });
  return { instancesById: bank, firstByType: byType };
}

/* --------------------------------------------------- the score-matrix fixture
 *
 * The fixture is authored by the grading subagent; its exact key spelling is not
 * frozen by docs/GRADING_FORMAT.md beyond the four form ids. This adapter
 * accepts the documented shape and a few spellings of the same idea, records
 * which spelling it read (`fixture_adapter`), and fails with
 * E_N23_FIXTURE_SHAPE naming the missing key rather than guessing silently.
 */

const FORM_LIST_KEYS = ['forms', 'fixtures', 'cases', 'matrix'];
const ANSWER_KEYS = ['stored_payload', 'payload', 'answer', 'capture', 'response'];

function fixtureForms(document) {
  for (let i = 0; i < FORM_LIST_KEYS.length; i += 1) {
    const value = document[FORM_LIST_KEYS[i]];
    if (Array.isArray(value)) { return { key: FORM_LIST_KEYS[i], forms: value }; }
    if (value && typeof value === 'object') {
      return {
        key: FORM_LIST_KEYS[i],
        forms: Object.keys(value).map((id) => Object.assign({ form_id: id }, value[id]))
      };
    }
  }
  return null;
}

function normalizeExpectedTotals(raw) {
  if (!raw || typeof raw !== 'object') { return null; }
  const totals = raw.totals && typeof raw.totals === 'object' ? raw.totals : raw;
  return {
    auto: firstDefined(totals, ['auto', 'auto_points', 'auto_scored', 'machine_checked_points']),
    pending: firstDefined(totals, ['pending', 'pending_external', 'pending_external_points', 'pending_points']),
    auto_max: firstDefined(totals, ['auto_max', 'auto_max_points']),
    pending_max: firstDefined(totals, ['pending_max', 'pending_max_points']),
    accounted: firstDefined(totals, ['accounted', 'accounted_points', 'total', 'form_max_points']),
    denied: firstDefined(totals, ['denied', 'denied_points']),
    zeroed: firstDefined(totals, ['zeroed', 'zeroed_points']),
    slot_counts: firstDefined(totals, ['slots_graded']) === undefined ? null : {
      graded: firstDefined(totals, ['slots_graded']),
      incomplete: firstDefined(totals, ['slots_incomplete']),
      invalid: firstDefined(totals, ['slots_invalid']),
      unattempted: firstDefined(totals, ['slots_unattempted']),
      manual_pending: firstDefined(totals, ['slots_manual_pending'])
    },
    raw: raw
  };
}

function normalizeSlotExpectation(raw) {
  if (!raw || typeof raw !== 'object') { return null; }
  return {
    state: pickString(raw, ['state']),
    verdict_class: firstDefined(raw, ['verdict_class']),
    error_class: firstDefined(raw, ['error_class']),
    auto: firstDefined(raw, ['auto', 'auto_points']),
    auto_max: firstDefined(raw, ['auto_max', 'auto_max_points']),
    pending: firstDefined(raw, ['pending', 'pending_points']),
    pending_max: firstDefined(raw, ['pending_max', 'pending_max_points']),
    denied: firstDefined(raw, ['denied']),
    zeroed: firstDefined(raw, ['zeroed']),
    criteria: Array.isArray(raw.criteria) ? raw.criteria : null
  };
}

function normalizeSlotRow(row, index) {
  const slotId = pickString(row, ['slot_id', 'slot', 'id']) || ('SLOT?' + (index + 1));
  const state = pickString(row, ['state', 'slot_state']);
  const hasAnswerKey = ANSWER_KEYS.some((key) => Object.prototype.hasOwnProperty.call(row, key));
  const answer = firstDefined(row, ANSWER_KEYS);
  const unattempted = row.unattempted === true || state === 'unattempted'
    || (hasAnswerKey && answer === null) || answer === undefined;
  return {
    slot_id: slotId,
    type_id: pickString(row, ['type_id', 'type', 'question_type']),
    instance_id: pickString(row, ['instance_id', 'instance', 'question_id']),
    state: state,
    answer: answer,
    unattempted: unattempted,
    malformed: row.malformed === true || row.invalid === true || state === 'invalid',
    manual_pending: row.manual_pending === true || state === 'manual_pending',
    raw_input: firstDefined(row, ['raw_input', 'raw']),
    expected: normalizeSlotExpectation(firstDefined(row, ['expected', 'expect']))
  };
}

function normalizeForm(raw, index) {
  const formId = pickString(raw, ['form_id', 'id', 'case_id', 'fixture_id']) || ('FX-N23-?' + (index + 1));
  const expectedRaw = firstDefined(raw, ['expected', 'expect', 'expected_totals', 'hand_computed']);
  const slotExpected = expectedRaw && expectedRaw.slots && typeof expectedRaw.slots === 'object'
    ? expectedRaw.slots : null;
  let slots = [];
  if (Array.isArray(raw.slots) || Array.isArray(raw.rows)) {
    slots = (raw.slots || raw.rows).map(normalizeSlotRow);
  } else if (Array.isArray(raw.bindings)) {
    const answers = raw.answers && typeof raw.answers === 'object' && !Array.isArray(raw.answers)
      ? raw.answers : {};
    slots = raw.bindings.map((binding, slotIndex) => {
      const slotId = pickString(binding, ['slot_id']) || ('SLOT?' + (slotIndex + 1));
      const hasAnswer = Object.prototype.hasOwnProperty.call(answers, slotId);
      const merged = Object.assign({}, binding, { answer: hasAnswer ? answers[slotId] : null });
      return normalizeSlotRow(merged, slotIndex);
    });
  }
  if (slotExpected) {
    slots.forEach((slot) => {
      if (Object.prototype.hasOwnProperty.call(slotExpected, slot.slot_id)) {
        slot.expected = normalizeSlotExpectation(slotExpected[slot.slot_id]);
      }
    });
  }
  return {
    form_id: formId,
    slots: slots,
    expected: normalizeExpectedTotals(expectedRaw),
    declared_malformed: firstDefined(raw, ['malformed_slots', 'malformed']),
    declared_unattempted: firstDefined(raw, ['unattempted_slots', 'unattempted']),
    declared_manual_pending: firstDefined(raw, ['manual_pending_slots', 'manual_pending']),
    raw: raw
  };
}

function loadScoreMatrix(root) {
  const file = path.join(root, 'tools/fixtures/n23_score_matrix.json');
  if (!exists(file)) {
    return {
      status: 'PENDING',
      reason: 'tools/fixtures/n23_score_matrix.json does not exist yet (owner: the N23 grading subagent).',
      forms: [],
      adapter: null
    };
  }
  let document;
  try {
    document = readJson(file);
  } catch (error) {
    return { status: 'FAIL', reason: 'tools/fixtures/n23_score_matrix.json is not readable JSON: ' + error.message, forms: [], adapter: null };
  }
  const collected = fixtureForms(document);
  if (!collected) {
    return {
      status: 'FAIL',
      reason: 'E_N23_FIXTURE_SHAPE: the fixture declares no form list; expected one of '
        + FORM_LIST_KEYS.join(', ') + '.',
      forms: [],
      adapter: null
    };
  }
  return {
    status: 'READ',
    file: 'tools/fixtures/n23_score_matrix.json',
    adapter: collected.key,
    document: document,
    slot_keys: Object.keys(collected.forms[0] || {}).sort(),
    forms: collected.forms.map(normalizeForm)
  };
}

/**
 * The oracle identity of the hand-computed score matrix (GRADING_FORMAT §4
 * `grading.oracle`): the fixture document and the conventions island it is
 * computed under. This is metadata, never grading logic.
 */
function oracleFor(islands, fixtureDocument) {
  return {
    oracle_version: 'n23-score-matrix/v' + String((fixtureDocument && fixtureDocument.schema_version) || 1),
    oracle_digest: sha256(canonical(fixtureDocument)),
    conventions_digest: sha256(canonical(islands['sim-conventions']))
  };
}

/* --------------------------------------------------------------- the context */

function termsMapFrom(island) {
  const terms = Object.create(null);
  const entries = (island && island.terms) || [];
  entries.forEach((entry) => {
    if (entry && typeof entry.key === 'string') { terms[entry.key] = entry.text_lv; }
  });
  return terms;
}

/**
 * The grading context of GRADING_FORMAT §6, built by the harness and never by
 * the modules. `method` is the constructed N19 MethodEngine instance (which owns
 * grade/specFromInstance) with the module's MethodEngine constructor attached,
 * because SimMethodEngine publishes no static grade; recorded, not improvised.
 */
function buildContext(root, islands, sandbox, bank) {
  /* The registry is a pure model: it must be loaded with its island before
   * contractFor()/completion() can answer (the N22 harness does the same). */
  if (sandbox.SimInputsRegistry && typeof sandbox.SimInputsRegistry.load === 'function') {
    sandbox.SimInputsRegistry.load(islands['sim-response-types'], islands['sim-terms']);
  }
  const methodEngine = new sandbox.SimMethodEngine.MethodEngine(
    islands['sim-method-engine'],
    islands['sim-terms']
  );
  const method = Object.create(methodEngine);
  method.MethodEngine = sandbox.SimMethodEngine.MethodEngine;
  method.specForVector = sandbox.SimMethodEngine.specForVector;
  method.sha256 = sandbox.SimMethodEngine.sha256;
  sandbox.SimGraphScoring.load(sandbox.document);
  return {
    doc: sandbox.document,
    quantity: sandbox.SimEngines,
    method: method,
    graph: sandbox.SimGraphScoring,
    inputsRegistry: sandbox.SimInputsRegistry,
    inputsIntegration: sandbox.SimInputsIntegration,
    figures: sandbox.SimGraphScoring.state.figures,
    terms: termsMapFrom(islands['sim-terms']),
    examPolicy: sandbox.SimExam.loadPolicy(sandbox.document),
    bank: { instancesById: bank.instancesById }
  };
}

/* ------------------------------------------------------- one scripted session */

function payloadForSlot(context, slot) {
  const answer = slot.answer;
  if (answer && typeof answer === 'object' && !Array.isArray(answer)) {
    const direct = firstDefined(answer, ['stored_payload', 'payload']);
    if (direct && typeof direct.kind === 'string') { return JSON.parse(JSON.stringify(direct)); }
    if (typeof answer.kind === 'string') { return JSON.parse(JSON.stringify(answer)); }
    /* A component capture: build the payload through the frozen integration. */
    const capture = answer.capture !== undefined ? answer.capture : answer;
    const contract = context.inputsRegistry && context.inputsRegistry.contractFor
      ? context.inputsRegistry.contractFor(slot.type_id)
      : null;
    const instance = slot.instance_id ? context.bank.instancesById[slot.instance_id] : null;
    const built = context.inputsIntegration.buildPayload(slot.type_id, contract, instance, capture);
    return JSON.parse(JSON.stringify(built));
  }
  throw Object.assign(
    new Error('E_N23_FIXTURE_SHAPE: slot ' + slot.slot_id + ' carries no storable answer object.'),
    { code: 'E_N23_FIXTURE_SHAPE' }
  );
}

function runFormSession(context, form) {
  const S = context.session;
  const clock = makeClock(0);
  const session = new S.ExamSession({
    policy: context.examPolicy,
    form: { form_id: form.form_id, slots: context.examPolicy.slots },
    clock: clock
  });
  session.dispatch('start');
  const answered = [];
  const skipped = [];
  const payloads = Object.create(null);
  for (let i = 0; i < form.slots.length; i += 1) {
    const slot = form.slots[i];
    if (slot.unattempted) { skipped.push(slot.slot_id); continue; }
    const payload = payloadForSlot(context, slot);
    session.dispatch('navigate', { slot_id: slot.slot_id });
    session.dispatch('answer', { slot_id: slot.slot_id, payload: payload });
    const stored = session.getAnswer(slot.slot_id);
    if (!stored || canonical(stored.payload) !== canonical(payload)) {
      throw Object.assign(
        new Error('E_N23_RAW_INPUT_REWRITTEN: the session rewrote the payload of slot ' + slot.slot_id),
        { code: 'E_N23_RAW_INPUT_REWRITTEN' }
      );
    }
    payloads[slot.slot_id] = payload;
    answered.push(slot.slot_id);
  }
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });
  return {
    session: session,
    terminal: session.toTerminalRecord(),
    answers: session.getAnswers(),
    payloads: payloads,
    answered: answered,
    unattempted: skipped
  };
}

function bindingsFor(context, form) {
  const bindings = [];
  const problems = [];
  form.slots.forEach((slot) => {
    const instanceId = slot.instance_id;
    const instance = instanceId ? context.bank.instancesById[instanceId] : null;
    if (!instance) {
      problems.push({ slot_id: slot.slot_id, reason: 'instance_id ' + String(instanceId) + ' is not a frozen bank instance' });
      return;
    }
    bindings.push({
      slot_id: slot.slot_id,
      type_id: slot.type_id || instance.type_id,
      instance_id: instanceId,
      instance: instance
    });
  });
  return { bindings: bindings, problems: problems };
}

function terminalDigest(terminal, grading) {
  return grading && typeof grading.canonicalText === 'function'
    ? sha256(grading.canonicalText(terminal))
    : sha256(canonical(terminal));
}

function gradeForm(context, form, grading, feedbackModule, bank) {
  const built = runFormSession({ session: context.session, examPolicy: context.examPolicy,
    inputsRegistry: context.inputsRegistry, inputsIntegration: context.inputsIntegration,
    bank: context.bank }, form);
  const bound = bindingsFor(context, form);
  /* The binding identity of GRADING_FORMAT §4: the fixture form, or a form
   * manifest at assembly time. A shallow copy keeps the shared context intact. */
  const gradingContext = Object.assign({}, context, {
    bindingSource: 'tools/fixtures/n23_score_matrix.json#' + form.form_id
  });
  const core = grading.gradeTerminalRecord(built.terminal, bound.bindings, gradingContext);
  const feedback = feedbackModule.assemble(core, gradingContext);
  const full = grading.composeGradedRecord(core, feedback);
  return {
    terminal: built.terminal,
    terminal_digest: terminalDigest(built.terminal, grading),
    core: core,
    feedback: feedback,
    record: full,
    binding_problems: bound.problems,
    answered: built.answered,
    unattempted: built.unattempted,
    payloads: built.payloads
  };
}

/* ---------------------------------------------------------------- assertions */

function criteriaOf(slot) {
  return Array.isArray(slot.criteria) ? slot.criteria : [];
}

function slotsByState(record, state) {
  return (record.slots || []).filter((slot) => slot.state === state).map((slot) => slot.slot_id);
}

/** The unblended rule: totals carry no merged, single "score" field. */
function mergedFieldViolations(totals, auto, pending) {
  const allowed = {
    auto_points: true, auto_max_points: true, pending_external_points: true,
    pending_max_points: true, form_max_points: true, unblended: true,
    slots_total: true, slots_graded: true, slots_incomplete: true,
    slots_invalid: true, slots_unattempted: true, slots_manual_pending: true
  };
  const mergedSum = auto + pending;
  const found = [];
  const keys = totals && typeof totals === 'object' ? Object.keys(totals) : [];
  keys.forEach((key) => {
    if (allowed[key]) { return; }
    if (/merge|combined|blend|score_total|total_score|points_total|grand/i.test(key)) {
      found.push({ key: key, reason: 'merged-looking field name' });
      return;
    }
    if (isNumber(totals[key]) && totals[key] === mergedSum) {
      found.push({ key: key, reason: 'value equals auto_points + pending_external_points' });
    }
  });
  return found;
}

function sumSlotTask(record, field) {
  return (record.slots || []).reduce((total, slot) => {
    const task = slot.task || {};
    return total + (isNumber(task[field]) ? task[field] : 0);
  }, 0);
}

function commonAssertions(record, context) {
  const out = [];
  const totals = record.totals || {};
  const slotCount = (record.slots || []).length;
  const expectedSlotCount = context.examPolicy.exam.slot_count;
  out.push(assertion('slot_count', slotCount === expectedSlotCount,
    { slots: slotCount, policy_slots: expectedSlotCount }));
  out.push(assertion('form_max_points_is_100', totals.form_max_points === 100,
    { form_max_points: totals.form_max_points }));
  out.push(assertion('unblended_flag', totals.unblended === true, { unblended: totals.unblended }));
  out.push(assertion('sum_auto_matches_total',
    sumSlotTask(record, 'auto_points') === totals.auto_points,
    { summed: sumSlotTask(record, 'auto_points'), total: totals.auto_points }));
  out.push(assertion('sum_pending_matches_total',
    sumSlotTask(record, 'pending_points') === totals.pending_external_points,
    { summed: sumSlotTask(record, 'pending_points'), total: totals.pending_external_points }));
  out.push(assertion('no_merged_total_field',
    mergedFieldViolations(totals, totals.auto_points, totals.pending_external_points).length === 0,
    mergedFieldViolations(totals, totals.auto_points, totals.pending_external_points)));
  return out;
}

function expectedAssertion(out, id, field, expected, observed) {
  if (!isNumber(expected)) {
    out.push(pendingAssertion(id, 'the fixture does not declare ' + field + '; nothing is asserted'));
    return;
  }
  out.push(assertion(id, observed === expected, { expected: expected, observed: observed }));
}

function normalizeClass(value) {
  if (value === undefined || value === null || value === '' || value === 'NONE') { return null; }
  return String(value);
}

/** Compare every per-slot expectation the fixture declares with the graded record. */
function slotExpectationAssertions(record, form) {
  const mismatches = [];
  let compared = 0;
  form.slots.forEach((slot) => {
    const expected = slot.expected;
    if (!expected || !expected.state) { return; }
    compared += 1;
    const actual = (record.slots || []).filter((entry) => entry.slot_id === slot.slot_id)[0];
    if (!actual) {
      mismatches.push({ slot_id: slot.slot_id, reason: 'missing from the graded record' });
      return;
    }
    const task = actual.task || {};
    if (actual.state !== expected.state) {
      mismatches.push({ slot_id: slot.slot_id, field: 'state', expected: expected.state, observed: actual.state });
    }
    if (normalizeClass(actual.verdict_class) !== normalizeClass(expected.verdict_class)) {
      mismatches.push({ slot_id: slot.slot_id, field: 'verdict_class', expected: expected.verdict_class, observed: actual.verdict_class });
    }
    if (normalizeClass(actual.error_class) !== normalizeClass(expected.error_class)) {
      mismatches.push({ slot_id: slot.slot_id, field: 'error_class', expected: expected.error_class, observed: actual.error_class });
    }
    const fields = [['auto', 'auto_points'], ['auto_max', 'auto_max_points'],
      ['pending', 'pending_points'], ['pending_max', 'pending_max_points']];
    fields.forEach((pair) => {
      if (!isNumber(expected[pair[0]])) { return; }
      if (task[pair[1]] !== expected[pair[0]]) {
        mismatches.push({ slot_id: slot.slot_id, field: pair[1], expected: expected[pair[0]], observed: task[pair[1]] });
      }
    });
    if (expected.criteria) {
      const byId = Object.create(null);
      (actual.criteria || []).forEach((criterion) => { byId[criterion.criterion_id] = criterion; });
      expected.criteria.forEach((row) => {
        const criterion = byId[row.criterion_id];
        if (!criterion) {
          mismatches.push({ slot_id: slot.slot_id, criterion: row.criterion_id, reason: 'missing from the criterion table' });
          return;
        }
        ['status', 'awarded_points', 'pending_points', 'max_points'].forEach((field) => {
          if (row[field] === undefined) { return; }
          if (criterion[field] !== row[field]) {
            mismatches.push({ slot_id: slot.slot_id, criterion: row.criterion_id, field: field,
              expected: row[field], observed: criterion[field] });
          }
        });
      });
    }
  });
  if (compared === 0) {
    return pendingAssertion('per_slot_expectations_match_fixture',
      'the fixture declares no per-slot expectations; only the form totals are asserted');
  }
  return assertion('per_slot_expectations_match_fixture', mismatches.length === 0,
    { slots_compared: compared, mismatches: mismatches });
}

function assertFullForm(record, form, context) {
  const expected = form.expected || {};
  const totals = record.totals || {};
  const out = commonAssertions(record, context);
  out.push(slotExpectationAssertions(record, form));
  expectedAssertion(out, 'auto_equals_hand_computed', 'auto_points', expected.auto, totals.auto_points);
  expectedAssertion(out, 'auto_equals_auto_max_declared', 'auto_max_points', expected.auto_max, totals.auto_max_points);
  expectedAssertion(out, 'pending_equals_hand_computed', 'pending_external_points', expected.pending, totals.pending_external_points);
  expectedAssertion(out, 'pending_equals_pending_max', 'pending_max_points', expected.pending_max, totals.pending_max_points);
  out.push(assertion('auto_points_equal_auto_max', totals.auto_points === totals.auto_max_points,
    { auto_points: totals.auto_points, auto_max_points: totals.auto_max_points }));
  if (isNumber(expected.accounted)) {
    out.push(assertion('accounted_is_100', expected.accounted === 100, { accounted: expected.accounted }));
  } else {
    out.push(assertion('accounted_is_100',
      totals.auto_max_points + totals.pending_max_points === 100,
      { auto_max: totals.auto_max_points, pending_max: totals.pending_max_points }));
  }
  const denied = [];
  (record.slots || []).forEach((slot) => {
    (criteriaOf(slot)).forEach((criterion) => {
      if (criterion.status === 'denied') { denied.push(slot.slot_id + '/' + criterion.criterion_id); }
      if (criterion.status === 'awarded' && isNumber(criterion.awarded_points)
          && criterion.awarded_points !== criterion.max_points) {
        denied.push(slot.slot_id + '/' + criterion.criterion_id + ' awarded ' + criterion.awarded_points + ' of ' + criterion.max_points);
      }
    });
  });
  out.push(assertion('zero_denied_criteria', denied.length === 0, denied));
  if (isNumber(expected.denied)) {
    out.push(assertion('fixture_declares_zero_denied', expected.denied === 0, { denied_points: expected.denied }));
  }
  return out;
}

function assertPartialForm(record, form, context) {
  const expected = form.expected || {};
  const totals = record.totals || {};
  const out = commonAssertions(record, context);
  out.push(slotExpectationAssertions(record, form));
  expectedAssertion(out, 'auto_equals_hand_computed', 'auto_points', expected.auto, totals.auto_points);
  expectedAssertion(out, 'auto_equals_auto_max_declared', 'auto_max_points', expected.auto_max, totals.auto_max_points);
  expectedAssertion(out, 'pending_equals_hand_computed', 'pending_external_points', expected.pending, totals.pending_external_points);
  expectedAssertion(out, 'pending_equals_pending_max', 'pending_max_points', expected.pending_max, totals.pending_max_points);
  const mixedCriteria = [];
  (record.slots || []).forEach((slot) => {
    const statuses = criteriaOf(slot).map((criterion) => criterion.status);
    if (statuses.indexOf('awarded') !== -1 && statuses.indexOf('denied') !== -1) {
      mixedCriteria.push(slot.slot_id);
    }
  });
  out.push(assertion('has_mixed_awarded_and_denied_criteria', mixedCriteria.length > 0, mixedCriteria));
  if (isNumber(expected.auto) && isNumber(expected.auto_max)) {
    out.push(assertion('partial_is_strictly_between_zero_and_max',
      expected.auto > 0 && expected.auto < expected.auto_max,
      { auto: expected.auto, auto_max: expected.auto_max }));
  } else {
    out.push(pendingAssertion('partial_is_strictly_between_zero_and_max',
      'the fixture does not declare auto and auto_max; the strict-between check is not asserted'));
  }
  return out;
}

function assertZeroForm(record, form, context) {
  const expected = form.expected || {};
  const totals = record.totals || {};
  const out = commonAssertions(record, context);
  out.push(slotExpectationAssertions(record, form));
  out.push(assertion('auto_points_zero', totals.auto_points === 0, { auto_points: totals.auto_points }));
  expectedAssertion(out, 'pending_equals_hand_computed', 'pending_external_points', expected.pending, totals.pending_external_points);
  expectedAssertion(out, 'pending_max_equals_hand_computed', 'pending_max_points', expected.pending_max, totals.pending_max_points);
  const missingVerdict = [];
  let criteriaCount = 0;
  (record.slots || []).forEach((slot) => {
    (criteriaOf(slot)).forEach((criterion) => {
      criteriaCount += 1;
      const hasStatus = typeof criterion.status === 'string';
      const hasVerdict = typeof criterion.verdict_class === 'string' || typeof criterion.error_class === 'string';
      if (!hasStatus || !hasVerdict) {
        missingVerdict.push(slot.slot_id + '/' + criterion.criterion_id);
      }
      if (isNumber(criterion.awarded_points) && criterion.awarded_points !== 0) {
        missingVerdict.push(slot.slot_id + '/' + criterion.criterion_id + ' awarded ' + criterion.awarded_points);
      }
    });
  });
  out.push(assertion('every_criterion_verdict_recorded', criteriaCount > 0 && missingVerdict.length === 0,
    { criteria: criteriaCount, violations: missingVerdict }));
  return out;
}

/**
 * The MIXED form's waiver set: a slot is malformed when the fixture says the
 * completion gate or an engine's structural check stopped it (incomplete /
 * invalid), or when the engine named a structural read error. Ordinary wrong
 * answers (OUT_OF_TOLERANCE, WRONG_OPTION_SELECTION) are not malformed.
 */
function malformedSlotIds(form) {
  return form.slots.filter((slot) => {
    const expected = slot.expected || {};
    const errorClass = normalizeClass(expected.error_class);
    return slot.malformed === true || expected.state === 'invalid' || expected.state === 'incomplete'
      || errorClass === 'UNREADABLE_INPUT';
  }).map((slot) => slot.slot_id);
}

function assertMixedForm(record, form, context, graded) {
  const expected = form.expected || {};
  const totals = record.totals || {};
  const out = commonAssertions(record, context);
  out.push(slotExpectationAssertions(record, form));
  expectedAssertion(out, 'auto_equals_hand_computed', 'auto_points', expected.auto, totals.auto_points);
  expectedAssertion(out, 'pending_equals_hand_computed', 'pending_external_points', expected.pending, totals.pending_external_points);
  expectedAssertion(out, 'auto_max_equals_hand_computed', 'auto_max_points', expected.auto_max, totals.auto_max_points);
  expectedAssertion(out, 'pending_max_equals_hand_computed', 'pending_max_points', expected.pending_max, totals.pending_max_points);
  if (expected.slot_counts) {
    const counts = expected.slot_counts;
    const mismatches = [];
    [['slots_graded', 'graded'], ['slots_incomplete', 'incomplete'], ['slots_invalid', 'invalid'],
      ['slots_unattempted', 'unattempted'], ['slots_manual_pending', 'manual_pending']].forEach((pair) => {
      if (isNumber(counts[pair[1]]) && totals[pair[0]] !== counts[pair[1]]) {
        mismatches.push({ field: pair[0], expected: counts[pair[1]], observed: totals[pair[0]] });
      }
    });
    out.push(assertion('slot_state_counts_match_fixture', mismatches.length === 0, mismatches));
  } else {
    out.push(pendingAssertion('slot_state_counts_match_fixture',
      'the fixture declares no slot-state counts; only the totals are asserted'));
  }

  const malformedIds = malformedSlotIds(form);
  out.push(assertion('malformed_slots_present', malformedIds.length > 0, malformedIds));
  const malformedViolations = [];
  malformedIds.forEach((slotId) => {
    const slot = (record.slots || []).filter((entry) => entry.slot_id === slotId)[0];
    if (!slot) { malformedViolations.push({ slot_id: slotId, reason: 'missing from the graded record' }); return; }
    const task = slot.task || {};
    if (task.auto_points !== 0) {
      malformedViolations.push({ slot_id: slotId, reason: 'auto_points is ' + task.auto_points });
    }
    criteriaOf(slot).forEach((criterion) => {
      if (isNumber(criterion.awarded_points) && criterion.awarded_points !== 0) {
        malformedViolations.push({ slot_id: slotId, criterion: criterion.criterion_id, reason: 'awarded a malformed criterion' });
      }
    });
    const namedError = normalizeClass(slot.error_class) !== null;
    const criterionErrors = criteriaOf(slot).some((criterion) => Array.isArray(criterion.errors) && criterion.errors.length > 0);
    const missingNames = criteriaOf(slot).some((criterion) => Array.isArray(criterion.missing) && criterion.missing.length > 0)
      || (Array.isArray(slot.missing) && slot.missing.length > 0);
    if (!namedError && !criterionErrors && !missingNames) {
      malformedViolations.push({ slot_id: slotId, reason: 'no named structural error or missing list' });
    }
    /* The raw-input invariant: the record carries exactly the dispatched payload. */
    const dispatched = graded && graded.payloads ? graded.payloads[slotId] : undefined;
    if (dispatched !== undefined && canonical(slot.raw_input) !== canonical(dispatched)) {
      malformedViolations.push({ slot_id: slotId, reason: 'raw input is not byte-identical to the dispatched payload' });
    }
  });
  out.push(assertion('malformed_slots_are_zero_with_named_error_and_raw_preserved',
    malformedViolations.length === 0, malformedViolations));

  const unattemptedIds = (record.slots || []).filter((slot) => slot.state === 'unattempted').map((slot) => slot.slot_id);
  const unattemptedViolations = (record.slots || []).filter((slot) => slot.state === 'unattempted').filter((slot) => {
    const task = slot.task || {};
    return task.auto_points !== 0
      || criteriaOf(slot).some((criterion) => isNumber(criterion.awarded_points) && criterion.awarded_points !== 0);
  }).map((slot) => slot.slot_id);
  out.push(assertion('unattempted_slots_are_zero', unattemptedIds.length > 0 && unattemptedViolations.length === 0,
    { slots: unattemptedIds, violations: unattemptedViolations }));

  const manualSlots = (record.slots || []).filter((slot) => slot.state === 'manual_pending');
  const manualViolations = [];
  manualSlots.forEach((slot) => {
    const task = slot.task || {};
    if (task.auto_points !== 0) { manualViolations.push({ slot_id: slot.slot_id, reason: 'manual slot contributed ' + task.auto_points + ' auto points' }); }
    if (!isNumber(task.pending_points) || task.pending_points <= 0) { manualViolations.push({ slot_id: slot.slot_id, reason: 'manual slot has no pending-external points' }); }
  });
  const q03 = manualSlots.filter((slot) => slot.type_id === 'Q03');
  out.push(assertion('q03_manual_pending_outside_auto_total',
    q03.length > 0 && manualViolations.length === 0,
    { manual_pending_slots: manualSlots.map((slot) => slot.slot_id), q03_slots: q03.map((slot) => slot.slot_id), violations: manualViolations }));
  out.push(assertion('pending_points_outside_auto_total',
    totals.auto_points + totals.pending_external_points <= totals.form_max_points,
    { auto: totals.auto_points, pending: totals.pending_external_points, form_max: totals.form_max_points }));
  return out;
}

const FORM_SHAPES = {
  'FX-N23-FULL': { kind: 'FULL', check: assertFullForm },
  'FX-N23-PARTIAL': { kind: 'PARTIAL', check: assertPartialForm },
  'FX-N23-ZERO': { kind: 'ZERO', check: assertZeroForm },
  'FX-N23-MIXED': { kind: 'MIXED', check: assertMixedForm }
};

function shapeFor(formId) {
  const key = formId.toUpperCase();
  const direct = FORM_SHAPES[key];
  if (direct) { return direct; }
  const suffix = key.split('-').pop();
  if (suffix === 'FULL') { return FORM_SHAPES['FX-N23-FULL']; }
  if (suffix === 'PARTIAL') { return FORM_SHAPES['FX-N23-PARTIAL']; }
  if (suffix === 'ZERO') { return FORM_SHAPES['FX-N23-ZERO']; }
  if (suffix === 'MIXED') { return FORM_SHAPES['FX-N23-MIXED']; }
  return null;
}

/* ------------------------------------------------------------ the chain (§7) */

function rawStringsOf(record) {
  const seen = Object.create(null);
  const out = [];
  function walk(value) {
    if (typeof value === 'string') {
      if (value.length >= 2 && !seen[value]) { seen[value] = true; out.push(value); }
      return;
    }
    if (Array.isArray(value)) { value.forEach(walk); return; }
    if (value && typeof value === 'object') {
      Object.keys(value).sort().forEach((key) => walk(value[key]));
    }
  }
  (record.slots || []).forEach((slot) => walk(slot.raw_input));
  return out;
}

/** Every string VALUE of every event, in event order (keys are not values). */
function eventStringValues(events) {
  const out = [];
  function walk(value) {
    if (typeof value === 'string') { out.push(value); return; }
    if (Array.isArray(value)) { value.forEach(walk); return; }
    if (value && typeof value === 'object') {
      Object.keys(value).forEach((key) => walk(value[key]));
    }
  }
  walk(events);
  return out;
}

function mappedRemediationFor(feedbackRecord) {
  const map = Object.create(null);
  const items = (feedbackRecord && feedbackRecord.items) || [];
  items.forEach((item) => {
    const remediation = item.remediation || {};
    const concepts = Array.isArray(remediation.concept_ids) ? remediation.concept_ids : [];
    const chains = Array.isArray(remediation.chain_ids) ? remediation.chain_ids : [];
    if (concepts.length > 0 || chains.length > 0) {
      map[item.slot_id] = true;
    }
  });
  return map;
}

function checkChainForm(form, graded, grading) {
  const record = graded.record;
  const events = grading.toAnalyticsEvents(record);
  const gradedDigest = record.digest;
  const checks = {};
  const detail = {};

  const types = Object.create(null);
  events.forEach((event) => { types[event.event] = (types[event.event] || 0) + 1; });
  detail.event_types = types;
  detail.event_count = events.length;
  /* §7: task-answered is emitted per answered slot; an unattempted slot has no
   * answer to report, and the module omits it (recorded, not assumed). */
  const answeredSlots = (record.slots || []).filter((slot) => slot.state !== 'unattempted').length;
  detail.answered_slots = answeredSlots;

  checks.session_completed_once = types['session-completed'] === 1;
  checks.task_answered_per_answered_slot = types['task-answered'] === answeredSlots;
  checks.every_event_digest_linked = events.every((event) => event.graded_digest === gradedDigest);

  const rawStrings = rawStringsOf(record);
  const eventText = canonical(events);
  /* The frozen vocabulary (event names, criterion ids, statuses, verdict/error classes,
   * signature ids) is not answer text even when a learner types the same word. The scan
   * excludes exactly that vocabulary and reports how much it excluded. */
  const vocabulary = Object.create(null);
  events.forEach((event) => {
    Object.keys(event).forEach((key) => {
      if (typeof event[key] === 'string') { vocabulary[event[key]] = true; }
    });
    (event.criterion_verdicts || []).forEach((verdict) => {
      Object.keys(verdict).forEach((key) => {
        if (typeof verdict[key] === 'string') { vocabulary[verdict[key]] = true; }
      });
    });
  });
  const candidates = rawStrings.filter((text) => vocabulary[text] !== true);
  const textCandidates = candidates.filter((text) => text.length >= 6);
  const valueCandidates = candidates.filter((text) => text.length >= 2);
  const leakedInText = textCandidates.filter((text) => eventText.indexOf(text) !== -1);
  const stringValues = eventStringValues(events);
  /* A short id-like token (S1, L1) is answer content too, but substring-matching it
   * against slot ids is noise. Short tokens must match a whole event string value;
   * distinctive tokens (six characters or a decimal-separator numeral) also match
   * inside a longer value. */
  const distinctive = (text) => text.length >= 6 || /[0-9][.,][0-9]/.test(text);
  const leakedInValues = valueCandidates.filter((text) =>
    stringValues.some((value) => value === text || (distinctive(text) && value.indexOf(text) !== -1)));
  checks.no_answer_text_in_events = leakedInText.length === 0 && leakedInValues.length === 0;
  detail.raw_strings_scanned = rawStrings.length;
  detail.vocabulary_strings_excluded = rawStrings.length - candidates.length;
  detail.text_scan_candidates = textCandidates.length;
  detail.value_scan_candidates = valueCandidates.length;
  detail.leaked_in_canonical_text = leakedInText;
  detail.leaked_in_event_string_values = leakedInValues;
  detail.leaked_strings = leakedInText.concat(leakedInValues.filter((text) => leakedInText.indexOf(text) === -1));

  const mapped = mappedRemediationFor(graded.feedback);
  const expectedRemediation = (record.slots || []).filter((slot) => {
    const malformed = slot.state === 'invalid' || slot.state === 'incomplete';
    const incorrect = slot.verdict_class === 'incorrect';
    return (malformed || incorrect) && mapped[slot.slot_id] === true;
  }).map((slot) => slot.slot_id).sort();
  const actualRemediation = events
    .filter((event) => event.event === 'remediation-state')
    .map((event) => event.slot_id)
    .sort();
  checks.remediation_events_exactly_for_incorrect_or_malformed = deepEqual(expectedRemediation, actualRemediation);
  detail.expected_remediation_slots = expectedRemediation;
  detail.actual_remediation_slots = actualRemediation;

  const openStates = events.filter((event) => event.event === 'remediation-state')
    .every((event) => event.state === 'open');
  checks.remediation_state_is_open = openStates;

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The terminal record, the graded record and the analytics events are one digest-linked chain, '
      + 'and no answer text reaches an event.',
    checks: checks,
    failed: failed,
    detail: detail,
    linkage: {
      session_id: record.session ? record.session.session_id : null,
      form_id: record.session ? record.session.form_id : null,
      terminal_digest: record.session ? record.session.terminal_digest : null,
      graded_digest: gradedDigest,
      analytics_event_digest: sha256(canonical(events)),
      event_count: events.length
    },
    events: events
  };
}

/* ----------------------------------------------------------- the render (§8) */

const RENDER_TERM_FALLBACK = {
  'feedback.results.auto_total': 'Automātiski vērtētie punkti',
  'feedback.results.pending_total': 'Ārēji gaidīšanas punkti',
  'feedback.results.unblended': 'Summas netiek apvienotas',
  'feedback.results.honesty': 'Šis ir mācību politikas kopsavilkums, nevis oficiāls rezultāta dokuments.',
  'feedback.results.raw_preserved': 'Saglabātā atbilde',
  'feedback.results.criterion_disclosure': 'Kritēriju detaļas',
  'feedback.results.malformed_zero': 'Nolasīšanas kļūda: 0 punkti',
  'feedback.results.incomplete_zero': 'Nepilnīga atbilde: 0 punkti',
  'feedback.results.unattempted': 'Nav atbildēts',
  'feedback.results.task_level': 'Uzdevuma līmenis',
  'feedback.results.misconception': 'Pārpratums',
  'feedback.results.remediation': 'Atkārtošana',
  'feedback.citation_label': 'Atsauce',
  'feedback.correct': 'Pareizi',
  'feedback.partial': 'Daļēji pareizi',
  'feedback.incorrect': 'Nepareizi',
  'feedback.pending_review': 'Gaida pārbaudi',
  'feedback.self_assess': 'Pašnovērtējums'
};

function renderTerms(context) {
  const terms = Object.assign(Object.create(null), RENDER_TERM_FALLBACK);
  Object.keys(context.terms || {}).forEach((key) => { terms[key] = context.terms[key]; });
  return terms;
}

function checkRender(form, graded, feedbackModule, terms) {
  const report = feedbackModule.buildScoreReport(graded.record, terms);
  const html = report && typeof report.html === 'string' ? report.html : '';
  const totals = graded.record.totals || {};
  const checks = {};
  checks.has_score_report = html.indexOf('class="score-report"') !== -1;
  checks.carries_graded_digest = html.indexOf('data-graded-digest="' + graded.record.digest + '"') !== -1;
  checks.auto_total_shown = html.indexOf('class="score-auto"') !== -1
    && html.indexOf(String(totals.auto_points)) !== -1
    && html.indexOf(String(totals.auto_max_points)) !== -1;
  checks.pending_total_shown = html.indexOf('class="score-pending"') !== -1
    && html.indexOf(String(totals.pending_external_points)) !== -1;
  checks.unblended_note_shown = html.indexOf('score-unblended-note') !== -1;
  checks.honesty_note_exactly_once = countOccurrences(html, 'score-honesty-note') === 1;
  checks.no_merged_total_line = html.indexOf('score-total"') === -1;
  const pendingSlots = (graded.record.slots || []).filter((slot) => slot.state === 'manual_pending');
  checks.pending_slots_labelled = pendingSlots.every((slot) => {
    const tag = new RegExp('<li[^>]*data-slot-id="' + slot.slot_id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '"[^>]*>').exec(html);
    return Boolean(tag) && tag[0].indexOf('data-state="manual_pending"') !== -1;
  });
  checks.feedback_cards_present = html.indexOf('class="feedback-card"') !== -1;
  checks.remediation_data_attributes = html.indexOf('data-concept=') !== -1
    || html.indexOf('data-chain=') !== -1
    || html.indexOf('data-card=') !== -1;
  const malformedIds = malformedSlotIds(form);
  const malformed = malformedIds
    .map((slotId) => (graded.record.slots || []).filter((slot) => slot.slot_id === slotId)[0])
    .filter(Boolean);
  checks.malformed_rows_show_named_error = malformed.every((slot) =>
    (typeof slot.error_class === 'string' && html.indexOf(slot.error_class) !== -1)
    || criteriaOf(slot).some((criterion) =>
      (Array.isArray(criterion.errors) && criterion.errors.some((error) => html.indexOf(error.id) !== -1))
      || (Array.isArray(criterion.missing) && criterion.missing.length > 0)));
  const invalidSlots = malformed.filter((slot) => slot.state === 'invalid');
  const preserved = invalidSlots.every((slot) => {
    const leaves = [];
    (function walk(value) {
      if (typeof value === 'string') { leaves.push(value); return; }
      if (Array.isArray(value)) { value.forEach(walk); return; }
      if (value && typeof value === 'object') { Object.keys(value).forEach((key) => walk(value[key])); }
    })(slot.raw_input);
    return leaves.some((leaf) => leaf.length >= 3 && html.indexOf(leaf) !== -1);
  });
  checks.raw_input_preserved = invalidSlots.length === 0 ? true : preserved;
  checks.raw_line_present = invalidSlots.length === 0 ? true : html.indexOf('score-raw') !== -1;
  checks.graded_malformed_slots = malformed.filter((slot) => slot.state === 'graded').map((slot) => slot.slot_id);

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The mixed-form score report is the §8 DOM stub: unblended totals, pending labels, one honesty '
      + 'note, feedback cards with remediation data-attributes and the preserved raw input line.',
    checks: checks,
    failed: failed,
    html: html,
    digest: report && report.digest ? report.digest : null
  };
}

/* --------------------------------------------------------- determinism (§9) */

/**
 * The generated driver lives under /tmp/opencode/n23-g3/ (the approved scratch
 * root), never inside the repository. If that path is not writable the OS temp
 * directory is the declared fallback; the record names whichever was used.
 */
function defaultDriverDir() {
  const preferred = '/tmp/opencode/n23-g3';
  try {
    fs.mkdirSync(preferred, { recursive: true });
    fs.accessSync(preferred, fs.constants.W_OK);
    return preferred;
  } catch (error) {
    return path.join(os.tmpdir(), 'n23-g3');
  }
}

function freshDriverSource() {  return [
    "'use strict';",
    "const fs = require('fs');",
    "const harness = require(process.argv[2]);",
    "const payload = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));",
    "const result = harness.gradeInFreshProcess(payload);",
    "process.stdout.write(JSON.stringify(result));"
  ].join('\n') + '\n';
}

function gradeInFreshProcess(payload) {
  const root = payload.repo_root;
  const islands = buildIslands(root);
  const sandbox = makeSandbox(root, islands, { withGrading: true });
  const grading = sandbox.SimGrading;
  const feedbackModule = sandbox.SimFeedback;
  if (!grading || typeof grading.gradeTerminalRecord !== 'function') {
    throw new Error('E_N23_FRESH_PROCESS: SimGrading is not loaded in the fresh process');
  }
  const bank = loadBank(root);
  const context = buildContext(root, islands, sandbox, bank);
  context.session = sandbox.SimSession;
  const fixture = loadScoreMatrix(root);
  if (fixture.status !== 'READ') {
    throw new Error('E_N23_FRESH_PROCESS: the score-matrix fixture is not readable in the fresh process');
  }
  context.oracle = oracleFor(islands, fixture.document);
  if (typeof payload.form_id !== 'string' || payload.form_id === '') {
    throw new Error('E_N23_FRESH_PROCESS: the driver payload carries no form_id');
  }
  context.bindingSource = 'tools/fixtures/n23_score_matrix.json#' + payload.form_id;
  const bindings = (payload.bindings || []).map((entry) => ({
    slot_id: entry.slot_id,
    type_id: entry.type_id,
    instance_id: entry.instance_id,
    instance: bank.instancesById[entry.instance_id]
  }));
  const core = grading.gradeTerminalRecord(payload.terminal, bindings, context);
  const feedback = feedbackModule.assemble(core, context);
  const record = grading.composeGradedRecord(core, feedback);
  return {
    digest: record.digest,
    canonical_sha256: sha256(grading.canonicalText(record)),
    canonical_text: grading.canonicalText(record)
  };
}

function checkDeterminism(root, form, rerun, graded, grading, options) {
  const second = rerun();
  const checks = {};
  checks.in_process_identical = second.record.digest === graded.record.digest
    && canonical(second.record) === canonical(graded.record);
  const text = grading.canonicalText(graded.record);
  const roundTrip = JSON.parse(text);
  checks.round_trip_identical = grading.canonicalText(roundTrip) === text;
  checks.canonical_key_order_stable = sha256(grading.canonicalText(roundTrip)) === sha256(text);

  const driverDir = options.driverDir || defaultDriverDir();
  fs.mkdirSync(driverDir, { recursive: true });
  const driverPath = path.join(driverDir, 'n23_fresh_grade_driver.js');
  const payloadPath = path.join(driverDir, 'n23_fresh_grade_payload.json');
  fs.writeFileSync(driverPath, freshDriverSource(), 'utf8');
  fs.writeFileSync(payloadPath, JSON.stringify({
    repo_root: root,
    form_id: form.form_id,
    terminal: graded.terminal,
    bindings: (form.slots || []).map((slot) => ({
      slot_id: slot.slot_id,
      type_id: slot.type_id,
      instance_id: slot.instance_id
    }))
  }), 'utf8');
  let fresh = null;
  let freshError = null;
  try {
    const stdout = execFileSync(process.execPath, [driverPath, __filename, payloadPath], {
      cwd: root, encoding: 'utf8', timeout: 300000
    });
    fresh = JSON.parse(stdout);
  } catch (error) {
    freshError = {
      message: error && error.message ? error.message : String(error),
      stderr: error && error.stderr ? String(error.stderr).slice(0, 2000) : null
    };
  }
  checks.fresh_process_available = fresh !== null;
  checks.fresh_process_identical = Boolean(fresh) && fresh.digest === graded.record.digest;
  checks.fresh_process_canonical_identical = Boolean(fresh)
    && fresh.canonical_sha256 === sha256(text);

  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The same terminal record + bindings + context yields byte-identical canonical graded '
      + 'records twice in-process and in a fresh Node process, and the canonical text survives a '
      + 'JSON round-trip.',
    checks: checks,
    failed: failed,
    in_process_1: graded.record.digest,
    in_process_2: second.record.digest,
    fresh_process: fresh ? fresh.digest : null,
    fresh_process_error: freshError,
    round_trip_identical: checks.round_trip_identical,
    canonical_sha256: sha256(text),
    driver: { path: driverPath, payload: payloadPath }
  };
}

/* ------------------------------------------------------------- batch digest */

function classificationCorpus(root) {
  const candidates = [
    'evidence/N23_CLASSIFICATION_TABLE.json',
    'evidence/N23_CLASSIFICATION_RECORD.json'
  ];
  for (let i = 0; i < candidates.length; i += 1) {
    const file = path.join(root, candidates[i]);
    if (exists(file)) {
      const raw = fs.readFileSync(file, 'utf8');
      let parsed = null;
      try { parsed = JSON.parse(raw); } catch (error) { parsed = null; }
      return {
        status: 'READ',
        file: candidates[i],
        sha256: sha256(raw),
        canonical_sha256: parsed === null ? null : sha256(canonical(parsed))
      };
    }
  }
  return {
    status: 'PENDING',
    reason: 'no classification table at ' + candidates.join(' or ')
      + ' yet (owner: the N23 classification subagent); the batch digest covers the score matrix only'
  };
}

function digestBundle(root, relatives) {
  const out = {};
  relatives.forEach((relative) => { out[relative] = fileRecord(root, relative); });
  return out;
}

/* --------------------------------------------------- the in-file smoke run */

const SMOKE_IDS = ['SMK-N23-GRADE-FULL', 'SMK-N23-GRADE-PARTIAL', 'SMK-N23-GRADE-MALFORMED'];

function runSmokeSandbox(root, islands) {
  const doc = makeDocument(islands);
  const sandbox = {
    console: console, JSON: JSON, Error: Error, String: String, Object: Object, Array: Array,
    Math: Math, Number: Number, Boolean: Boolean, RegExp: RegExp, isFinite: isFinite,
    parseInt: parseInt, parseFloat: parseFloat, Date: Date, Set: Set, Map: Map, Promise: Promise
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  ['src/compiled/session.js', 'src/compiled/exam.js', 'src/smoke-subset.js'].forEach((relative) => {
    vm.runInContext(fs.readFileSync(path.join(root, relative), 'utf8'), sandbox, { filename: relative });
  });
  const report = sandbox.SimSmoke.run(doc, {});
  const vectors = SMOKE_IDS.map((id) => (report.vectors || []).filter((entry) => entry.id === id)[0] || null);
  const checks = {};
  SMOKE_IDS.forEach((id, index) => {
    checks[id + '_present'] = Boolean(vectors[index]);
    checks[id + '_passes'] = Boolean(vectors[index]) && vectors[index].status === 'PASS';
  });
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    suite: { total: report.total, passed: report.passed, failed: report.failed },
    vectors: vectors,
    checks: checks,
    failed: failed,
    policy_island_present: Boolean(islands['sim-grading-policy'])
  };
}

/* -------------------------------------------------------------------- writing */

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

function resolveOut(root, value) {
  if (!value) { return null; }
  return path.isAbsolute(value) ? value : path.join(root, value);
}

/* -------------------------------------------------------------------- the run */

function preflight(root) {
  const missingModules = missingFiles(root, GRADING_MODULES);
  const missingSources = missingFiles(root, GRADING_SOURCES);
  const missingIslands = Object.keys(N23_ISLAND_FILES)
    .filter((id) => !exists(path.join(root, N23_ISLAND_FILES[id])))
    .map((id) => N23_ISLAND_FILES[id]);
  const missingCore = missingFiles(root, ENGINE_MODULES.concat(RUNTIME_MODULES));
  return {
    missing_modules: missingModules,
    missing_sources: missingSources,
    missing_islands: missingIslands,
    missing_core: missingCore,
    pending: missingModules.length > 0 || missingIslands.length > 0,
    blocking: missingCore.length > 0
  };
}

function runOnce(root, options) {
  const pre = preflight(root);
  const islands = buildIslands(root);
  const digests = digestBundle(root, [
    'src/grading.ts',
    'src/feedback.ts',
    'src/compiled/grading.js',
    'src/compiled/feedback.js',
    'data/grading_policy.json',
    'data/feedback_classification.json',
    'tools/fixtures/n23_score_matrix.json',
    'tools/fixtures/n23_feedback_sample.json',
    'tools/validate_n23_grading.py',
    'tools/n23_classification.py',
    'tools/check_n23_runtime.js',
    'src/smoke-subset.js',
    'src/shell.html'
  ]);

  const smoke = runSmokeSandbox(root, islands);

  if (pre.blocking) {
    throw new Error('E_N23_MODULES: the frozen engine/session modules are missing: '
      + pre.missing_core.join(', '));
  }

  const record = {
    schema_version: 1,
    owner: 'N23',
    status: pre.pending ? 'PENDING' : 'PASS',
    digest_method: 'canonical JSON (sorted keys, separators (",", ":"), ensure_ascii=False) -> UTF-8 -> '
      + 'SHA-256, the N04 emission rule; the graded record digest excludes its own digest field.',
    contract: 'docs/GRADING_FORMAT.md (frozen 2026-11-19)',
    runtime_modules: GRADING_MODULES,
    source_modules: GRADING_SOURCES,
    engine_modules: ENGINE_MODULES,
    islands: Object.keys(N23_ISLAND_FILES).map((id) => N23_ISLAND_FILES[id]),
    preflight: pre,
    context_binding: {
      method: 'the constructed N19 MethodEngine instance (grade / specFromInstance) with the module '
        + 'MethodEngine constructor attached; SimMethodEngine publishes no static grade, and '
        + 'GRADING_FORMAT §0 names the instance methods. Recorded, not improvised.',
      figures: 'SimGraphScoring.state.figures after graph.load(doc)',
      terms: 'resolved key -> text_lv map from #sim-terms',
      bank: '{instancesById} from data/bank/*.json',
      examPolicy: 'SimExam.loadPolicy(doc) (the N21 island, slots authoritative)'
    },
    smoke: smoke,
    digests: digests,
    forms: [],
    chain: { status: 'PENDING', reason: 'the grading runtime and the score-matrix fixture are not in place yet' },
    render: { status: 'PENDING', reason: 'the grading runtime and the score-matrix fixture are not in place yet' },
    determinism: { status: 'PENDING', reason: 'the grading runtime and the score-matrix fixture are not in place yet' },
    batch: { status: 'PENDING', reason: 'no graded records yet' },
    missing: {
      modules: pre.missing_modules,
      sources: pre.missing_sources,
      islands: pre.missing_islands,
      fixture: pre.pending ? 'tools/fixtures/n23_score_matrix.json' : null
    },
    not_claimed: [
      'No browser render, screen-reader, print or instructor acceptance: this harness is a machine-level '
        + 'proof of the grading and feedback contract; N32/N33/N34 own the visual and assistive gates.',
      'No official examination, grade or proctoring status: every policy value is PROPOSED training policy.',
      'No semantic grading of free text: self-assessed criteria stay pending-external.',
      'The fresh-process determinism proof runs the same harness code in a second Node process; it is a '
        + 'process-level determinism proof, not a machine reboot or a different runtime.'
    ]
  };

  if (pre.pending) {
    const missingFixture = !exists(path.join(root, 'tools/fixtures/n23_score_matrix.json'));
    record.missing.fixture = missingFixture ? 'tools/fixtures/n23_score_matrix.json' : null;
    record.chain.reason = 'missing: ' + []
      .concat(pre.missing_modules, pre.missing_islands, missingFixture ? ['tools/fixtures/n23_score_matrix.json'] : [])
      .join(', ');
    record.render.reason = record.chain.reason;
    record.determinism.reason = record.chain.reason;
    record.batch.reason = record.chain.reason;
    return { record: record, smoke: smoke, digests: digests, pre: pre };
  }

  const fixture = loadScoreMatrix(root);
  record.fixture = {
    file: fixture.file || 'tools/fixtures/n23_score_matrix.json',
    adapter: fixture.adapter,
    form_count: fixture.forms.length,
    form_ids: fixture.forms.map((form) => form.form_id),
    slot_keys: fixture.slot_keys || null,
    status: fixture.status,
    reason: fixture.reason || null
  };
  if (fixture.status === 'FAIL') {
    throw new Error(fixture.reason || 'E_N23_FIXTURE_SHAPE: the score-matrix fixture is unusable');
  }
  if (fixture.status !== 'READ') {
    record.fixture = {
      file: 'tools/fixtures/n23_score_matrix.json',
      status: fixture.status,
      reason: fixture.reason || null
    };
    record.missing.fixture = 'tools/fixtures/n23_score_matrix.json';
    record.status = 'PENDING';
    record.chain.reason = fixture.reason;
    record.render.reason = fixture.reason;
    record.determinism.reason = fixture.reason;
    record.batch.reason = fixture.reason;
    record.status_detail = { failures: [], pending: ['fixture'] };
    return { record: record, smoke: smoke, digests: digests, pre: pre };
  }

  const sandbox = makeSandbox(root, islands, { withGrading: true });
  const grading = sandbox.SimGrading;
  const feedbackModule = sandbox.SimFeedback;
  if (!grading || typeof grading.gradeTerminalRecord !== 'function') {
    throw new Error('E_N23_MODULES: src/compiled/grading.js did not register SimGrading.gradeTerminalRecord');
  }
  if (!feedbackModule || typeof feedbackModule.assemble !== 'function') {
    throw new Error('E_N23_MODULES: src/compiled/feedback.js did not register SimFeedback.assemble');
  }
  const bank = loadBank(root);
  const context = buildContext(root, islands, sandbox, bank);
  context.session = sandbox.SimSession;
  context.oracle = oracleFor(islands, fixture.document);

  const gradedByForm = Object.create(null);
  const gradedDigests = [];
  const shapeFailures = [];

  fixture.forms.forEach((form) => {
    const shape = shapeFor(form.form_id);
    if (!shape) {
      shapeFailures.push({ form_id: form.form_id, reason: 'no AC1 shape for this form id; expected FX-N23-FULL/PARTIAL/ZERO/MIXED' });
      return;
    }
    const graded = gradeForm(context, form, grading, feedbackModule, bank);
    gradedByForm[form.form_id] = { form: form, shape: shape, graded: graded };
    gradedDigests.push({ form_id: form.form_id, digest: graded.record.digest });
    const assertions = shape.check(graded.record, form, context, graded);
    if (graded.binding_problems.length > 0) {
      assertions.push(assertion('bindings_complete', false, graded.binding_problems));
    } else {
      assertions.push(assertion('bindings_complete', true, { count: form.slots.length }));
    }
    const failed = assertions.filter((entry) => entry.ok === false).map((entry) => entry.id);
    const pendings = assertions.filter((entry) => entry.ok === null).map((entry) => entry.id);
    record.forms.push({
      form_id: form.form_id,
      kind: shape.kind,
      status: failed.length > 0 ? 'FAIL' : (pendings.length > 0 ? 'PENDING' : 'PASS'),
      failed: failed,
      pending: pendings,
      totals: graded.record.totals,
      terminal_digest: graded.terminal_digest,
      graded_digest: graded.record.digest,
      answered_slots: graded.answered,
      unattempted_slots: graded.unattempted,
      assertions: assertions
    });
  });

  if (shapeFailures.length > 0) {
    record.missing.forms = shapeFailures;
  }

  /* The chain and the render fixture use the MIXED form: it carries the
   * malformed trio, the unattempted slots and the Q03 manual-pending path. */
  const mixedKey = Object.keys(gradedByForm).filter((id) => /MIXED/i.test(id))[0];
  if (!mixedKey) {
    record.chain = { status: 'PENDING', reason: 'the fixture declares no MIXED form; the chain fixture has no subject' };
    record.render = { status: 'PENDING', reason: record.chain.reason };
    record.determinism = { status: 'PENDING', reason: record.chain.reason };
  } else {
    const subject = gradedByForm[mixedKey];
    record.chain = checkChainForm(subject.form, subject.graded, grading);
    record.render = checkRender(subject.form, subject.graded, feedbackModule, renderTerms(context));
    record.render.html_bytes = Buffer.byteLength(record.render.html || '', 'utf8');
    record.render.sha256 = record.render.html ? sha256(record.render.html) : null;
    record.determinism = checkDeterminism(root, subject.form, function () {
      return gradeForm(context, subject.form, grading, feedbackModule, bank);
    }, subject.graded, grading, options);
  }

  /* The batch digest: every graded digest in form order, plus the classification
   * table when the sweep has produced it. */
  const classification = classificationCorpus(root);
  const ordered = gradedDigests.slice().sort((a, b) => (a.form_id < b.form_id ? -1 : (a.form_id > b.form_id ? 1 : 0)));
  const batchPayload = {
    contract: 'docs/GRADING_FORMAT.md',
    graded: ordered,
    classification: classification.status === 'READ' ? classification.canonical_sha256 : null,
    modules: ['src/grading.ts', 'src/feedback.ts', 'src/compiled/grading.js',
      'src/compiled/feedback.js', 'data/grading_policy.json', 'data/feedback_classification.json']
      .map((relative) => ({ path: relative, sha256: digests[relative] ? digests[relative].sha256 : null }))
  };
  record.batch = {
    status: classification.status === 'PENDING' ? 'PENDING' : 'PASS',
    batch_digest: sha256(canonical(batchPayload)),
    graded_forms: ordered.length,
    graded_digests: ordered,
    classification_corpus: classification,
    payload: batchPayload
  };
  record.classification_corpus = classification;

  const names = ['smoke'].concat(record.forms.map((form) => 'form:' + form.form_id),
    ['chain', 'render', 'determinism', 'batch']);
  const statusOf = {
    smoke: record.smoke.status,
    chain: record.chain.status,
    render: record.render.status,
    determinism: record.determinism.status,
    batch: record.batch.status
  };
  record.forms.forEach((form) => { statusOf['form:' + form.form_id] = form.status; });
  const failures = names.filter((name) => statusOf[name] === 'FAIL');
  const pendings = names.filter((name) => statusOf[name] === 'PENDING');
  if (failures.length > 0) { record.status = 'FAIL'; }
  else if (pendings.length > 0) { record.status = 'PENDING'; }
  else { record.status = 'PASS'; }
  record.status_detail = { failures: failures, pending: pendings };

  return {
    record: record,
    smoke: smoke,
    digests: digests,
    pre: pre,
    gradedByForm: gradedByForm,
    fixture: fixture
  };
}

function sideRecords(result) {
  const record = result.record;
  const graded = result.gradedByForm
    ? result.gradedByForm[Object.keys(result.gradedByForm).filter((id) => /MIXED/i.test(id))[0]]
    : null;
  const mixedFormId = graded ? graded.form.form_id : 'FX-N23-MIXED';
  const chain = {
    schema_version: 1,
    owner: 'N23',
    status: record.chain.status,
    claim: record.chain.claim || null,
    reason: record.chain.reason || null,
    form_id: mixedFormId,
    digest_method: record.digest_method,
    linkage: record.chain.linkage || null,
    checks: record.chain.checks || null,
    failed: record.chain.failed || null,
    detail: record.chain.detail || null,
    events: record.chain.events || []
  };
  const render = {
    schema_version: 1,
    owner: 'N23',
    status: record.render.status,
    claim: record.render.claim || null,
    reason: record.render.reason || null,
    form_id: mixedFormId,
    checks: record.render.checks || null,
    failed: record.render.failed || null,
    html: record.render.html || null,
    digest: record.render.digest || null,
    sha256: record.render.sha256 || null,
    html_bytes: record.render.html_bytes || 0,
    source: 'SimFeedback.buildScoreReport(fullMixedRecord, termsMap) — docs/GRADING_FORMAT.md §8; '
      + 'recorded as N32 visual test data, not a browser-render acceptance claim'
  };
  const determinism = {
    schema_version: 1,
    owner: 'N23',
    status: record.determinism.status,
    claim: record.determinism.claim || null,
    reason: record.determinism.reason || null,
    form_id: mixedFormId,
    in_process_1: record.determinism.in_process_1 || null,
    in_process_2: record.determinism.in_process_2 || null,
    fresh_process: record.determinism.fresh_process || null,
    round_trip_identical: record.determinism.round_trip_identical === true,
    canonical_sha256: record.determinism.canonical_sha256 || null,
    checks: record.determinism.checks || null,
    failed: record.determinism.failed || null,
    fresh_process_error: record.determinism.fresh_process_error || null,
    driver: record.determinism.driver || null
  };
  return { chain: chain, render: render, determinism: determinism };
}

function prune(result) {
  const record = JSON.parse(JSON.stringify(result.record));
  if (record.render && typeof record.render.html === 'string') {
    record.render.html_excerpt = record.render.html.slice(0, 400);
    delete record.render.html;
  }
  if (record.chain && Array.isArray(record.chain.events)) {
    record.chain.event_summary = record.chain.events.map((event) => ({
      event: event.event, slot_id: event.slot_id || null, graded_digest: event.graded_digest
    }));
    delete record.chain.events;
  }
  if (record.batch && record.batch.payload) {
    record.batch.payload_digest = sha256(canonical(record.batch.payload));
    delete record.batch.payload;
  }
  return record;
}

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const result = runOnce(root, { driverDir: args.driverDir });
  const record = prune(result);
  const status = record.status;

  if (args.record) {
    const out = resolveOut(root, args.record);
    writeJson(out, record);
    const directory = path.dirname(out);
    const sides = sideRecords(result);
    writeJson(resolveOut(root, args.chain) || path.join(directory, 'N23_CHAIN_RECORD.json'), sides.chain);
    writeJson(resolveOut(root, args.render) || path.join(directory, 'N23_RENDER_FIXTURE.json'), sides.render);
    writeJson(resolveOut(root, args.determinism) || path.join(directory, 'N23_DETERMINISM_RECORD.json'), sides.determinism);
  }

  process.stdout.write(JSON.stringify({
    status: status,
    missing: record.missing,
    forms: record.forms.map((form) => ({ form_id: form.form_id, status: form.status, failed: form.failed })),
    chain: statusOrReason(record.chain),
    render: statusOrReason(record.render),
    determinism: statusOrReason(record.determinism),
    batch: record.batch.batch_digest || null,
    smoke: { status: record.smoke.status, vectors: record.smoke.vectors.map((vector) => vector ? { id: vector.id, status: vector.status } : null) },
    digests: record.digests,
    fixture: record.fixture || null
  }, null, 2) + '\n');

  if (status === 'FAIL') {
    const failed = [].concat(record.status_detail ? record.status_detail.failures : []);
    process.stderr.write('FAIL n23_runtime: ' + failed.join(', ') + '\n');
    return 1;
  }
  if (status === 'PENDING') {
    const missing = []
      .concat(record.missing.modules || [])
      .concat(record.missing.islands || [])
      .concat(record.missing.fixture ? [record.missing.fixture] : [])
      .concat(record.missing.forms ? record.missing.forms.map((entry) => entry.form_id) : []);
    const pending = record.status_detail ? record.status_detail.pending : [];
    process.stderr.write('PENDING n23_runtime: '
      + (missing.length > 0 ? 'missing ' + missing.join(', ') : 'pending ' + pending.join(', '))
      + (missing.length === 0 && record.batch && record.batch.reason ? ' — ' + record.batch.reason : '')
      + ' (owner: the parallel N23 subagents / the official compile)\n');
    return 3;
  }
  return 0;
}

function statusOrReason(entry) {
  if (!entry) { return null; }
  return { status: entry.status, reason: entry.reason || null };
}

if (require.main === module) {
  try {
    process.exitCode = main();
  } catch (error) {
    process.stderr.write('FAIL n23_runtime: ' + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main, gradeInFreshProcess, buildIslands, makeSandbox, buildContext, loadBank, canonical };
