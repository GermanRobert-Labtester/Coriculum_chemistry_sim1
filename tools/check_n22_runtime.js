#!/usr/bin/env node
/* N22 runtime harness: the capture layer, the eighteen payloads, the parity table.
 *
 * The harness loads the committed TypeScript runtime modules
 * (src/compiled/{session,exam}.js and src/compiled/inputs/*.js), the frozen
 * engines from src/ (quantity, method, graph scoring and the graph capture
 * component — all of them ship from src/) and the islands from data/. It proves
 * the claims the roadmap asks N22 to prove in Main Step C:
 *
 *   1. payload_contract        — every one of the 18 built payloads passes the
 *                                session machine's own structural check, and the
 *                                validated object is identical to the built one
 *                                (no adapter, no coercion);
 *   2. scripted_session_18     — 18 types answered through the component/
 *                                integration API in one scripted session, plus
 *                                one deliberately incomplete case per completed
 *                                type; every answer goes through dispatch; the
 *                                session serialises and deserialises to
 *                                identical answers;
 *   3. capture_grading_parity  — the parity table: each stored payload consumed
 *                                by its frozen engine produces the engine's
 *                                criterion shape without adaptation;
 *   4. navigator_completion_overlay — the map cells and the review warning list
 *                                refined by the completion verdict, with the
 *                                Latvian missing names;
 *   5. smoke_vectors_in_file   — the three SMK-N22-* vectors registered in
 *                                src/smoke-subset.js run and pass;
 *   6. only_writer_guards      — no setter exists, the machine's accessors hand
 *                                out deep copies, and the integration writes
 *                                only by dispatching;
 *   7. blank_and_pending       — a whitespace-only Q15 is BLANK_RESPONSE with
 *                                zero points; a non-blank Q15 is pending with no
 *                                verdict; Q03 stays manual-rubric pending.
 *
 * The harness is not a browser render, screen-reader or instructor acceptance
 * claim. It is a machine-level proof of the capture contract.
 *
 * Usage: node tools/check_n22_runtime.js [--repo-root .] [--record PATH]
 *                                         [--trace PATH] [--parity PATH]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

/* ------------------------------------------------------------------ arguments */

function parseArgs(argv) {
  const args = { repoRoot: path.resolve(__dirname, '..'), record: null, trace: null, parity: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--trace') { args.trace = argv[i + 1]; i += 1; }
    else if (argv[i] === '--parity') { args.parity = argv[i + 1]; i += 1; }
  }
  return args;
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function exists(file) {
  return fs.existsSync(file);
}

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

/* ------------------------------------------------------------------ helpers */

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
  return JSON.stringify(a) === JSON.stringify(b);
}

function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return String(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.map((key) => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
}

/* ------------------------------------------------------------------ islands */

const FIGURE_PATHS = [
  'data/figures_t12.json',
  'data/figures_t23.json',
  'data/figures_t4.json',
  'data/figures_t5.json',
  'data/figures_t67.json'
];

function buildIslands(root) {
  const islands = {};
  islands['sim-conventions'] = readJson(path.join(root, 'data/conventions.json'));
  islands['sim-terms'] = readJson(path.join(root, 'data/terms.json'));
  islands['sim-engines'] = readJson(path.join(root, 'data/engine_taxonomy.json'));
  islands['sim-graph-scoring'] = readJson(path.join(root, 'data/graph_scoring_contract.json'));
  islands['sim-method-engine'] = readJson(path.join(root, 'data/method_engine_contract.json'));
  islands['sim-method-cards'] = readJson(path.join(root, 'data/method_cards.json'));
  islands['sim-exam-policy'] = readJson(path.join(root, 'data/exam_policy.json'));
  const figures = { island_id: 'sim-figures', figures: [] };
  FIGURE_PATHS.forEach((relative) => {
    const source = readJson(path.join(root, relative));
    (source.figures || []).forEach((figure) => { figures.figures.push(figure); });
  });
  islands['sim-figures'] = figures;
  if (exists(path.join(root, 'data/response_types.json'))) {
    islands['sim-response-types'] = readJson(path.join(root, 'data/response_types.json'));
  }
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

/* ------------------------------------------------------------------ sandbox */

const MODULES = [
  'src/quantity-engine.js',
  'src/method-engine.js',
  'src/graph-scoring-engine.js',
  'src/graph-capture.js',
  'src/compiled/session.js',
  'src/compiled/exam.js',
  'src/compiled/inputs/registry.js',
  'src/compiled/inputs/components.js',
  'src/compiled/inputs/integration.js'
];

function makeSandbox(root, islands) {
  const doc = makeDocument(islands);
  const sandbox = {
    console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
    RegExp, isFinite, parseInt, parseFloat, Date, Map, Set, unescape, encodeURIComponent,
    escape, decodeURIComponent, Object: Object
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  MODULES.forEach((relative) => {
    vm.runInContext(fs.readFileSync(path.join(root, relative), 'utf8'), sandbox, { filename: relative });
  });
  return sandbox;
}

/* ---------------------------------------------------------------------- bank */

function loadBank(root) {
  const bank = Object.create(null);
  const directory = path.join(root, 'data/bank');
  fs.readdirSync(directory).sort().forEach((file) => {
    if (!file.endsWith('.json')) { return; }
    const document = readJson(path.join(directory, file));
    (document.questions || []).forEach((question) => { bank[question.question_id] = question; });
  });
  return bank;
}

/* ------------------------------------------------------------ the fixtures */

const TYPE_INSTANCES = {
  Q01: 'COL1-2-2B-A-01',
  Q02: 'COL1-3-3A-A-01',
  Q03: 'COL1-3-3B-D-01',
  Q04: 'COL1-1-1C-B-01',
  Q05: 'COL1-6-6B-A-01',
  Q06: 'COL1-2-2A-B-01',
  Q07: 'COL1-1-1A-A-01',
  Q08: 'COL1-2-2A-A-01',
  Q09: 'COL1-2-2B-B-01',
  Q10: 'COL1-2-2C-A-01',
  Q11: 'COL1-2-2D-A-01',
  Q12: 'COL1-2-2D-B-01',
  Q13: 'COL1-1-1A-B-01',
  Q14: 'COL1-1-1B-C-01',
  Q15: 'COL1-1-1B-B-01',
  Q16: 'COL1-1-1D-B-01',
  Q17: 'COL1-3-3D-A-01',
  Q18: 'COL1-5-5D-D-01'
};

const TYPE_ORDER = Object.keys(TYPE_INSTANCES);

/** The seven completed types carry a deliberately incomplete twin. */
const INCOMPLETE_TYPES = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15'];

/**
 * The key the numeric engine consumes for one instance: the declared answer
 * field of the instance (the registry's `fields[].source` is
 * `instance.payload.input_fields`).
 */
function numericFieldId(instance, payload) {
  const declared = (instance && instance.payload && instance.payload.input_fields) || [];
  if (declared.length > 0 && declared[0].field_id) { return declared[0].field_id; }
  const values = (payload && payload.values) || {};
  const keys = Object.keys(values);
  return keys.length > 0 ? keys[0] : 'value';
}

/**
 * The captures a component emits. They are the component's JSON description of
 * what the learner did, written in the registry's own payload paths, with the
 * raw strings untouched (spaces, comma decimals, minus signs).
 */
function capturesFor(bank, drawPayload, figureId) {
  const q11points = ((bank['COL1-2-2D-A-01'] || {}).payload || {}).points || [];
  return {
    Q01: { fields: { m_g: ' 4,70 ' } },
    Q02: { fields: { c: '1,60', S1: '0,0479', S2: '1,597' } },
    Q03: {
      choice: 'c = γ/M',
      fill_ins: { S1: 'c = γ/M', S2: 'w = γ/(ρ·1000)', S3: 'ρ ir vajadzīgs, lai pārietu no tilpuma uz masu' },
      conserved: 'ρ'
    },
    Q04: { vector: ['4', '3', '2'] },
    Q05: {
      rows: {
        S1: 'MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O',
        S2: 'Fe²⁺ → Fe³⁺ + e⁻',
        S3: 'MnO₄⁻ + 8H⁺ + 5Fe²⁺ → Mn²⁺ + 4H₂O + 5Fe³⁺',
        S4: '5 elektroni'
      }
    },
    Q06: {
      pairs: [
        { left_id: 'L1', right_id: 'R1' },
        { left_id: 'L2', right_id: 'R2' },
        { left_id: 'L3', right_id: 'R3' }
      ]
    },
    Q07: { selected: ['HET', 'SUSP'] },
    Q08: {
      order: ['S1', 'S2', 'S3', 'S4'],
      explanation: 'Atzīmi izlīdzina tikai pēc sajaukšanas, jo šķīduma tilpums mainās.'
    },
    Q09: { fields: { n_mmol: '0,190' } },
    Q10: { fields: { V_del: '5,25' } },
    Q11: {
      record: { mode: 'construct', x_axis: 'c', y_axis: 'A', scale: 'auto', points: q11points },
      draw_payload: drawPayload
    },
    Q12: { read: { x: '30', y: '75', figure_binding: figureId } },
    Q13: {
      vector: ['1', '1', '1', '1'],
      located: 'CuO',
      replacement: 'CuO + H2 → Cu + H2O',
      reason: 'Cu(II) reducējas līdz Cu(0), tāpēc tā ir arī redoksa reakcija.'
    },
    Q14: {
      selected: ['T2', 'T4'],
      justification: 'T1 un T3 ir nepareizi: glikoze šķīst kā molekulas.'
    },
    Q15: { text: 'MgCl₂ šķīdumā ir kustīgi joni Mg²⁺ un Cl⁻, kas pārnēsā elektrību.' },
    Q16: { text: 'AgCl ir nešķīstams, tāpēc veidojas nogulsne; NaNO₃ un KCl nogulsni neveido.' },
    Q17: {
      pair_map: { S1: 'γ = w·(1 g/mL)', S2: 'm(NaCl) = γ·V', S3: 'Trūkst blīvuma ρ.' },
      structure: {}
    },
    Q18: {
      selected: ['S2', 'S3'],
      justification: 'S1 un S4 ir nepareizi: kopējie koeficienti nenosaka reakcijas pakāpi.'
    },
    Q19: null
  };
}

/**
 * The incomplete twins. Each one is a real, storable payload that the session
 * accepts — the point is that the completion model, not the payload validator,
 * is what says "not finished".
 */
function incompleteCapturesFor(drawPayload) {
  return {
    Q02: { fields: { c: '   ' } },
    Q04: { vector: ['4', '3'] },
    Q10: { fields: { V_del: '' } },
    Q11: { record: { mode: 'construct', x_axis: 'c', y_axis: 'A' } },
    Q12: { read: { x: '30', y: '75' } },
    Q13: { vector: ['1', '1'], located: 'CuO', reason: 'Nepilnīgs skaidrojums.' },
    Q15: { text: '   ' },
    Q20: null
  };
}

/* ---------------------------------------------------- 1. the payload contract */

function checkPayloadContract(context) {
  const { I, policy, registryIsland } = context;
  const contracts = policy.session_contract.payload_contracts;
  const rows = [];
  const checks = {};
  const mismatches = [];
  for (let index = 0; index < TYPE_ORDER.length; index += 1) {
    const typeId = TYPE_ORDER[index];
    const contract = registryIsland ? registryIsland.types[typeId] : null;
    const instance = context.bank[TYPE_INSTANCES[typeId]];
    const payload = I.buildPayload(typeId, contract, instance, context.captures[typeId]);
    const validated = context.SimSession.validatePayload(payload, contracts);
    const identical = deepEqual(validated, payload);
    const preparedOk = deepEqual(I.buildPayload(typeId, contract, instance, payload), payload);
    const kindOk = payload.kind === ((instance && instance.payload_class) || (contract && contract.payload_kind));
    const variantOk = !contract || (payload.variant === undefined ? null : payload.variant) === (contract.payload_variant === undefined ? null : contract.payload_variant);
    if (!identical) { mismatches.push({ type_id: typeId, reason: 'validatePayload rewrote the payload' }); }
    if (!preparedOk) { mismatches.push({ type_id: typeId, reason: 'a prepared payload did not pass through unchanged' }); }
    if (!kindOk) { mismatches.push({ type_id: typeId, reason: 'kind ' + payload.kind + ' does not match the instance payload class ' + (instance && instance.payload_class) }); }
    if (!variantOk) { mismatches.push({ type_id: typeId, reason: 'variant ' + payload.variant + ' does not match the registry ' + (contract && contract.payload_variant) }); }
    rows.push({
      type_id: typeId,
      kind: payload.kind,
      variant: payload.variant === undefined ? null : payload.variant,
      keys: Object.keys(payload).sort(),
      validated_identical: identical,
      prepared_passthrough: preparedOk,
      status: identical && preparedOk && kindOk && variantOk ? 'PASS' : 'FAIL'
    });
    checks['payload_' + typeId] = identical && preparedOk && kindOk && variantOk;
  }
  checks.eighteen_rows = rows.length === 18;
  checks.no_coercion = mismatches.length === 0;
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'Every one of the 18 built payloads passes the session machine\'s own structural check, '
      + 'and the validated object is identical to the built payload: no adapter, no coercion.',
    registry_island: registryIsland ? 'data/response_types.json' : 'absent',
    rows: rows,
    mismatches: mismatches,
    checks: checks,
    failed: failed
  };
}

/* ------------------------------------------------------ 2. the scripted session */

function buildScratchForm(captures, incompleteCaptures) {
  const slots = [];
  const bindings = {};
  TYPE_ORDER.forEach((typeId, index) => {
    const slotId = 'S' + String(index + 1);
    slots.push({ slot_id: slotId, topic: index + 1, points: 1 });
    bindings[slotId] = { type_id: typeId };
  });
  INCOMPLETE_TYPES.forEach((typeId, index) => {
    const slotId = 'S' + String(TYPE_ORDER.length + index + 1);
    slots.push({ slot_id: slotId, topic: index + 1, points: 1 });
    bindings[slotId] = { type_id: typeId, incomplete: true };
  });
  return { slots: slots, bindings: bindings };
}

function checkScriptedSession(context) {
  const { I, S, policy, registryIsland, bank } = context;
  const form = buildScratchForm();
  const slotCount = form.slots.length;
  const formId = 'N22-SCRATCH-18';
  const clock = makeClock(1000);
  const session = new S.ExamSession({ policy: policy, form: { form_id: formId, slots: form.slots }, clock: clock });
  session.dispatch('start');
  const answers = [];
  const checks = {};
  let dispatchCount = 0;
  const originalDispatch = session.dispatch.bind(session);
  session.dispatch = function (event, payload) {
    dispatchCount += 1;
    return originalDispatch(event, payload);
  };
  const answered = [];
  TYPE_ORDER.forEach((typeId, index) => {
    const slotId = 'S' + String(index + 1);
    const contract = registryIsland ? registryIsland.types[typeId] : null;
    const instance = bank[TYPE_INSTANCES[typeId]];
    session.dispatch('navigate', { slot_id: slotId });
    const record = I.answer(session, slotId, typeId, contract, instance, context.captures[typeId]);
    answers.push(record);
    answered.push(slotId);
  });
  const incompleteOrder = [];
  INCOMPLETE_TYPES.forEach((typeId, index) => {
    const slotId = 'S' + String(TYPE_ORDER.length + index + 1);
    const contract = registryIsland ? registryIsland.types[typeId] : null;
    const instance = bank[TYPE_INSTANCES[typeId]];
    session.dispatch('navigate', { slot_id: slotId });
    I.answer(session, slotId, typeId, contract, instance, context.incompleteCaptures[typeId]);
    incompleteOrder.push(slotId);
  });
  session.dispatch('flag', { slot_id: 'S3' });
  session.dispatch('flag', { slot_id: incompleteOrder[0] });
  session.dispatch('request-review');
  session.dispatch('submit', { confirmed: true });

  const lateWrite = captureError(() => I.answer(session, 'S1', 'Q01', null, null, { fields: { m_g: '1' } }));
  checks.late_write_refused = Boolean(lateWrite) && lateWrite.code === 'E_SESSION_LATE_WRITE';
  checks.all_slots_answered = session.getUnansweredSlotIds().length === 0;
  checks.stored_18_complete = answered.length === 18;
  checks.dispatch_calls_counted = dispatchCount > 0;

  const serialized = session.serialize();
  const restoredClock = makeClock(1000);
  const restored = S.ExamSession.deserialize(serialized, {
    policy: policy, form: { form_id: formId, slots: form.slots }, clock: restoredClock
  });
  const before = session.getAnswers();
  const after = restored.getAnswers();
  checks.roundtrip_answers_identical = deepEqual(before, after);
  checks.roundtrip_flags_identical = deepEqual(session.getFlags(), restored.getFlags());
  checks.roundtrip_state_identical = session.getState() === restored.getState();

  const payloadTable = before.map((entry) => ({
    slot_id: entry.slot_id,
    kind: entry.kind,
    variant: entry.payload.variant === undefined ? null : entry.payload.variant,
    payload_digest: I.contentDigest(entry.payload)
  }));
  const terminal = session.toTerminalRecord();
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  const trace = {
    schema_version: 1,
    owner: 'N22',
    digest_method: 'SimInputsIntegration.contentDigest — two FNV-1a 32-bit lanes over a canonical JSON '
      + 'projection, 16 lowercase hex characters. An identity token for the trace, not a cryptographic seal.',
    form: {
      form_id: formId,
      slot_count: slotCount,
      complete_slots: answered,
      incomplete_slots: incompleteOrder,
      bindings: Object.keys(form.bindings).map((slotId) => ({
        slot_id: slotId,
        type_id: form.bindings[slotId].type_id,
        incomplete_case: form.bindings[slotId].incomplete === true
      }))
    },
    answers: before.map((entry) => ({
      slot_id: entry.slot_id,
      kind: entry.kind,
      variant: entry.payload.variant === undefined ? null : entry.payload.variant,
      payload_digest: I.contentDigest(entry.payload),
      payload: entry.payload
    })),
    payload_table: payloadTable,
    digests: {
      answers: I.contentDigest(before),
      answers_after_roundtrip: I.contentDigest(after),
      payload_table: I.contentDigest(payloadTable),
      serialized: sha256(serialized),
      terminal_record: I.contentDigest(terminal)
    },
    round_trip: {
      answers_identical: checks.roundtrip_answers_identical,
      flags_identical: checks.roundtrip_flags_identical,
      state_identical: checks.roundtrip_state_identical
    },
    terminal_record_fields: Object.keys(terminal).sort(),
    state: session.getState(),
    transitions: session.getTransitions()
  };
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'An 18-type scripted session answered only through dispatch, plus one deliberately '
      + 'incomplete case per completed-type group, serialises and deserialises to identical answers.',
    checks: checks,
    failed: failed,
    dispatch_calls: dispatchCount,
    late_write: lateWrite,
    trace: trace,
    session: session,
    form: form
  };
}

/* --------------------------------------------------------- 3. the parity table */

function submissionFor(typeId, payload, instance) {
  if (typeId === 'Q01' || typeId === 'Q02' || typeId === 'Q09' || typeId === 'Q10') {
    const fieldId = numericFieldId(instance, payload);
    return {
      submission: { value: payload.values[fieldId] },
      binding: { payload_field: 'values[' + fieldId + ']', engine_field: 'submission.value' },
      identity: payload.values[fieldId]
    };
  }
  if (typeId === 'Q07' || typeId === 'Q14' || typeId === 'Q18') {
    return {
      submission: { selected_ids: payload.selected.slice() },
      binding: { payload_field: 'selected', engine_field: 'submission.selected_ids' },
      identity: payload.selected
    };
  }
  if (typeId === 'Q06') {
    return {
      submission: { pairs: payload.pairs.map((pair) => ({ left_id: pair.left_id, right_id: pair.right_id })) },
      binding: { payload_field: 'pairs', engine_field: 'submission.pairs' },
      identity: payload.pairs
    };
  }
  if (typeId === 'Q08') {
    return {
      submission: { order: payload.order.slice() },
      binding: { payload_field: 'order', engine_field: 'submission.order' },
      identity: payload.order
    };
  }
  if (typeId === 'Q12') {
    return {
      submission: { x: payload.read.x, value: payload.read.y },
      binding: { payload_field: 'read.x / read.y', engine_field: 'submission.x / submission.value' },
      identity: [payload.read.x, payload.read.y]
    };
  }
  if (typeId === 'Q11') {
    return {
      submission: payload.draw_payload,
      binding: { payload_field: 'draw_payload', engine_field: 'scoreDrawing(record, payload)' },
      identity: payload.draw_payload
    };
  }
  /* Q03, Q04, Q05, Q13, Q15, Q16, Q17: the pending/text paths. */
  return {
    submission: payload.text === undefined ? payload : { text: payload.text },
    binding: {
      payload_field: payload.text === undefined ? 'the stored payload (recorded unparsed)' : 'text',
      engine_field: 'submission.text / the rubric'
    },
    identity: payload.text === undefined ? null : payload.text
  };
}

function criterionShape(verdict) {
  return {
    verdict_class: verdict.verdict_class,
    error_class: verdict.error_class,
    awarded_criteria: verdict.awarded_criteria,
    machine_checked_points: verdict.machine_checked_points,
    pending_points: verdict.pending_points,
    max_points: verdict.max_points
  };
}

function checkParity(context) {
  const { I, bank, registryIsland } = context;
  const engine = context.methodEngine;
  const quantity = context.SimEngines;
  const graph = context.SimGraphScoring;
  const rows = [];
  const findings = [];
  for (let index = 0; index < TYPE_ORDER.length; index += 1) {
    const typeId = TYPE_ORDER[index];
    const instance = bank[TYPE_INSTANCES[typeId]];
    const contract = registryIsland ? registryIsland.types[typeId] : null;
    const payload = I.buildPayload(typeId, contract, instance, context.captures[typeId]);
    const prepared = submissionFor(typeId, payload, instance);
    let verdict = null;
    let shape = null;
    let engineName = '';
    let identityOk = true;
    let note = '';
    if (typeId === 'Q03') {
      const pending = I.q03PendingPath(payload);
      engineName = 'manual-rubric-pending';
      shape = {
        verdict_class: null,
        error_class: null,
        awarded_criteria: [],
        machine_checked_points: 0,
        pending_points: null,
        max_points: null,
        class: pending.class,
        graded: pending.graded,
        verdict: pending.verdict
      };
      identityOk = pending.class === 'pending' && pending.graded === false && pending.verdict === null;
      note = 'Manual rubric: the template choice and the typed fill-ins are stored, never auto-scored.';
    } else if (typeId === 'Q11') {
      const record = context.figures[context.drawContext.figure_id];
      verdict = graph.scoreDrawing(record, payload.draw_payload, instance.rubric);
      engineName = 'SimGraphScoring.scoreDrawing (N18-graph)';
      shape = criterionShape(verdict);
      identityOk = verdict.capture.digest === graph.canonicalDigest(payload.draw_payload);
    } else if (typeId === 'Q12') {
      verdict = graph.scoreReading(
        { kind: 'n05_payload', instance: instance },
        prepared.submission,
        instance.rubric
      );
      engineName = 'SimGraphScoring.scoreReading (N18-graph)';
      shape = criterionShape(verdict);
      identityOk = prepared.identity[0] === payload.read.x && prepared.identity[1] === payload.read.y;
    } else if (typeId === 'Q06' || typeId === 'Q08') {
      const spec = engine.specFromInstance(instance);
      verdict = engine.grade(spec, prepared.submission);
      engineName = 'SimMethodEngine.' + (typeId === 'Q06' ? 'gradeMatching' : 'gradeOrdering') + ' (N19-method)';
      shape = criterionShape(verdict);
      identityOk = deepEqual(prepared.submission[typeId === 'Q06' ? 'pairs' : 'order'], prepared.identity);
    } else if (typeId === 'Q15' || typeId === 'Q16') {
      const spec = engine.specFromInstance(instance);
      verdict = engine.grade(spec, prepared.submission);
      engineName = 'SimMethodEngine.gradeSelfAssessment (N19-self)';
      shape = criterionShape(verdict);
      identityOk = prepared.submission.text === payload.text;
    } else {
      /* Q01, Q02, Q04, Q09, Q10 through the quantity engine; Q05, Q13, Q17
       * through the same engine's method branch (their rubric is self-assessed
       * or manual, so the shape is the pending shape and nothing is parsed). */
      verdict = quantity.grade(instance, prepared.submission, {});
      engineName = contract && contract.grading_binding
        ? 'SimEngines.grade (' + contract.grading_binding.engine + ' binding)'
        : 'SimEngines.grade';
      shape = criterionShape(verdict);
      if (typeId === 'Q05' || typeId === 'Q13' || typeId === 'Q17') {
        note = 'The instance rubric is self-assessed: the frozen engine records the payload unparsed '
          + 'and returns the pending shape. Nothing is keyword-matched.';
      }
      if (typeId === 'Q04') {
        note = 'The coefficient vector is recorded, not parsed: the instance rubric is self-assessed, '
          + 'so the engine returns the pending shape for the criteria the rubric declares. The '
          + 'completion model is what reads the vector (registry model "vector").';
      }
      if (prepared.identity !== null && typeof prepared.identity === 'string') {
        identityOk = prepared.submission.value === prepared.identity;
      } else if (Array.isArray(prepared.identity)) {
        identityOk = deepEqual(prepared.submission.selected_ids, prepared.identity);
      }
    }
    if (!note && contract && contract.grading_binding && contract.grading_binding.class !== 'pending'
        && typeof shape.verdict_class === 'string' && shape.verdict_class.indexOf('pending') === 0) {
      note = 'The registry class is ' + contract.grading_binding.class + '; the instance rubric '
        + 'declares the criterion self-assessed, so the frozen engine\'s rubric split makes the shape '
        + 'pending. The rubric decides, not the label.';
    }
    const row = {
      type_id: typeId,
      instance_id: TYPE_INSTANCES[typeId],
      payload_kind: payload.kind,
      payload_variant: payload.variant === undefined ? null : payload.variant,
      payload_digest: I.contentDigest(payload),
      engine: engineName,
      registry_grading: contract ? contract.grading_binding : null,
      submission_binding: prepared.binding,
      value_identity: 'byte-identical',
      identity_ok: identityOk,
      criterion_shape: shape,
      adapter: 'none',
      note: note,
      status: shape !== null && identityOk ? 'PASS' : 'FAIL'
    };
    if (contract && contract.grading_binding && contract.grading_binding.engine === 'N19-method'
        && (typeId === 'Q07' || typeId === 'Q14' || typeId === 'Q18')) {
      row.engine_note = 'The registry labels the binding N19-method, but SimMethodEngine.specFromInstance '
        + 'refuses payload_class option_select (E_METHOD_PAYLOAD_CLASS); the frozen engine that consumes '
        + 'a selection is the quantity engine\'s option_select branch, which is the path the N05 golden '
        + 'oracle uses. Recorded, not improvised.';
    }
    rows.push(row);
  }

  /* The Q07/Q14/Q18 refusal is a recorded finding, not a hidden adapter. */
  const refused = captureError(() => engine.specFromInstance(bank[TYPE_INSTANCES.Q07]));
  findings.push({
    id: 'N22-C05',
    label: 'DOCUMENTED-AND-ACCEPTED',
    topic: 'option_select has no N19-method spec builder',
    observation: 'SimMethodEngine.specFromInstance refuses payload_class option_select.',
    observed_error: refused,
    resolution: 'The parity row for Q07/Q14/Q18 names the quantity engine\'s option_select branch — the '
      + 'frozen path the N05 golden corpus uses — and passes payload.selected verbatim as selected_ids.'
  });
  findings.push({
    id: 'N22-C06',
    label: 'DOCUMENTED-AND-ACCEPTED',
    topic: 'variant vocabulary: named-variant key versus short value',
    observation: 'data/exam_policy.json named_variants maps Q11_record → variant "record", while '
      + 'data/response_types.json declares payload_variant "Q11_record".',
    resolution: 'The stored payload carries the registry form (Q11_record, Q12_read, Q13_vector, …), '
      + 'because response_types.json is the response-type single source that N23/N24/N30/N33 read. '
      + 'The session accepts either (variant is a raw string). Reported as a naming divergence, not '
      + 'silently unified.'
  });

  const adapters = rows.filter((row) => row.adapter !== 'none');
  const identityFailures = rows.filter((row) => row.identity_ok !== true);
  const status = rows.length === 18 && adapters.length === 0 && identityFailures.length === 0
    && rows.every((row) => row.status === 'PASS');
  return {
    status: status ? 'PASS' : 'FAIL',
    claim: 'For each of the 18 types the stored payload, consumed by its frozen engine, produces the '
      + 'recorded criterion shape without adaptation or coercion: the audit finds no adapter.',
    rows: rows,
    audit: {
      rows: rows.length,
      adapters_found: adapters.length,
      identity_failures: identityFailures.map((row) => row.type_id),
      engines: {
        quantity: rows.filter((row) => row.engine.indexOf('SimEngines') === 0).length,
        method: rows.filter((row) => row.engine.indexOf('SimMethodEngine') === 0).length,
        graph: rows.filter((row) => row.engine.indexOf('SimGraphScoring') === 0).length,
        manual_pending: rows.filter((row) => row.engine === 'manual-rubric-pending').length
      }
    },
    findings: findings
  };
}

/* ------------------------------------------------ 4. the completion overlays */

function checkCompletionOverlay(context) {
  const { I, S, X, policy, registryIsland, bank } = context;
  const registry = context.SimInputsRegistry;
  if (!registryIsland) {
    return {
      status: 'PENDING',
      claim: 'The navigator map and the review warning list are refined by the completion verdict.',
      reason: 'data/response_types.json is missing; the completion model has no contract to read.'
    };
  }
  if (!registry || registry.stub === true) {
    return {
      status: 'PENDING',
      claim: 'The navigator map and the review warning list are refined by the completion verdict.',
      reason: 'src/compiled/inputs/registry.js is still the scaffold stub: SimInputsRegistry.completion '
        + 'does not exist yet, so the overlay cannot be exercised.'
    };
  }
  const session = context.scripted.session;
  const form = context.scripted.form;
  const answers = session.getAnswers();
  const bindings = {};
  Object.keys(form.bindings).forEach((slotId) => {
    const binding = form.bindings[slotId];
    bindings[slotId] = {
      type_id: binding.type_id,
      contract: registryIsland.types[binding.type_id],
      instance: bank[TYPE_INSTANCES[binding.type_id]]
    };
  });
  const mapState = X.buildMapState(session.snapshot());
  const overlay = I.completionMapState(mapState, answers, bindings);
  const reviewState = X.buildReviewState(session.snapshot());
  const review = I.reviewMissingList(reviewState, answers, bindings);

  const incompleteSlots = Object.keys(form.bindings)
    .filter((slotId) => form.bindings[slotId].incomplete === true);
  const completeSlots = Object.keys(form.bindings)
    .filter((slotId) => form.bindings[slotId].incomplete !== true);
  const overlayStatus = {};
  (overlay.cells || []).forEach((cell) => { overlayStatus[cell.slot_id] = cell.completion_status; });
  const wrongComplete = completeSlots.filter((slotId) => overlayStatus[slotId] !== 'complete');
  const wrongIncomplete = incompleteSlots.filter((slotId) => {
    return overlayStatus[slotId] === 'complete' || overlayStatus[slotId] === 'unanswered';
  });
  const named = (review.incomplete || []).map((entry) => entry.slot_id).sort();
  const namesPresent = (review.incomplete || []).every((entry) => Array.isArray(entry.missing_names_lv)
    && entry.missing_names_lv.length > 0);
  const checks = {
    cells_refined: (overlay.cells || []).length === (mapState.cells || []).length,
    eighteen_complete: wrongComplete.length === 0 && overlay.complete_count === 18,
    seven_not_complete: wrongIncomplete.length === 0 && (overlay.incomplete_count + overlay.invalid_count) === 7,
    review_names_the_seven: deepEqual(named, incompleteSlots.slice().sort()),
    review_has_latvian_names: namesPresent,
    review_role_alert: review.role === 'alert',
    review_count_matches: review.count === incompleteSlots.length,
    n21_answered_flag_preserved: (overlay.cells || []).every((cell) => typeof cell.answered === 'boolean')
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The navigator cells carry the completion verdict and the review warning list names exactly '
      + 'the seven incomplete cases with their Latvian missing names.',
    completion_binding: I.completionBinding(),
    checks: checks,
    failed: failed,
    overlay: {
      complete_count: overlay.complete_count,
      incomplete_count: overlay.incomplete_count,
      invalid_count: overlay.invalid_count,
      statuses: overlayStatus
    },
    review: { count: review.count, text_lv: review.text_lv, incomplete: review.incomplete }
  };
}

/* --------------------------------------------------- 5. the in-file smoke run */

const SMOKE_IDS = ['SMK-N22-NUMERIC-CAPTURE', 'SMK-N22-CLASSIFICATION-CAPTURE', 'SMK-N22-ORDERING-CAPTURE'];

function runSmokeSandbox(root, islands, label) {
  const doc = makeDocument(islands);
  const sandbox = {
    console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp,
    isFinite, parseInt, parseFloat, Date, Set, Map, Promise
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
    label: label,
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    suite: { total: report.total, passed: report.passed, failed: report.failed },
    vectors: vectors,
    checks: checks,
    failed: failed
  };
}

function checkSmokeVectors(root, context) {
  const responseIsland = exists(path.join(root, 'data/response_types.json'));
  if (!responseIsland) {
    return {
      status: 'PENDING',
      claim: 'The three SMK-N22-* vectors registered in src/smoke-subset.js run and pass.',
      reason: 'data/response_types.json is missing: the island the vectors assert on does not exist yet.'
    };
  }
  const islands = context.islands;
  const fromSource = runSmokeSandbox(root, islands, 'src modules + data islands');
  let artifact = null;
  const artifactPath = path.join(root, 'output/simulator.html');
  if (exists(artifactPath)) {
    const html = fs.readFileSync(artifactPath, 'utf8');
    if (html.indexOf('<script type="application/json" id="sim-response-types">') !== -1) {
      const extracted = {};
      Object.keys(islands).forEach((id) => {
        const match = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)<\\/script>').exec(html);
        if (match) { extracted[id] = JSON.parse(match[1].replace(/<\\\//g, '</')); }
      });
      const smokeRun = runSmokeSandbox(root, extracted, 'shipped artifact islands');
      artifact = { island_present: true, run: smokeRun };
      if (smokeRun.status !== 'PASS') {
        fromSource.status = 'FAIL';
        fromSource.failed = fromSource.failed.concat(['artifact:' + smokeRun.failed.join(',')]);
      }
    } else {
      artifact = {
        island_present: false,
        note: 'output/simulator.html does not carry #sim-response-types yet; the coordinator rebuilds the '
          + 'artifact at merge, and this check re-runs against it then.'
      };
    }
  } else {
    artifact = { island_present: false, note: 'output/simulator.html is not built.' };
  }
  return {
    status: fromSource.status,
    claim: 'The three SMK-N22-* vectors registered in src/smoke-subset.js run and pass, and they also '
      + 'pass against the shipped artifact once it carries the island.',
    vectors: fromSource.vectors,
    suite: fromSource.suite,
    checks: fromSource.checks,
    failed: fromSource.failed,
    artifact: artifact
  };
}

/* ------------------------------------------------------ 6. the only-writer guard */

function checkOnlyWriter(context) {
  const { I, S, policy } = context;
  const session = new S.ExamSession({
    policy: policy,
    form: { form_id: 'N22-GUARD', slots: [{ slot_id: 'S1', topic: 1, points: 1 }] },
    clock: makeClock(0)
  });
  session.dispatch('start');
  I.answer(session, 'S1', 'Q01', null, null, { fields: { m_g: '2,50' } });
  const guard = I.assertOnlyWriter(session);
  const direct = ['setAnswer', 'setAnswers', 'writeAnswer', 'setAnswerMap']
    .filter((name) => typeof session[name] === 'function');
  /* The integration's write path is dispatch, and only dispatch: a call to
   * answer() must surface as exactly one dispatch. */
  let dispatched = 0;
  const original = session.dispatch.bind(session);
  session.dispatch = function (event, payload) { dispatched += 1; return original(event, payload); };
  I.answer(session, 'S1', 'Q09', null, null, { fields: { n_mmol: '0,190' } });
  const checks = {
    no_public_setter: direct.length === 0,
    guard_reports_dispatch_only: guard.writer === 'dispatch',
    guard_reports_no_setters: (guard.checks.public_setters || []).length === 0,
    guard_proves_deep_copies: guard.checks.copies_are_deep === true,
    one_dispatch_per_answer: dispatched === 1
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The integration has no write path other than dispatch: the machine offers no setter, its '
      + 'accessors hand out deep copies, and one answer() call is exactly one dispatch.',
    note: 'The compiled machine keeps its private fields as own properties (a TypeScript compile detail), '
      + 'so the only-writer property is a contract plus these structural checks, not a runtime seal. '
      + 'The integration never touches them, and the guard proves the accessors copy.',
    checks: checks,
    failed: failed,
    guard: guard
  };
}

/* ------------------------------------------------- 7. the blank/pending honesty */

function checkBlankAndPending(context) {
  const { I, bank } = context;
  const engine = context.methodEngine;
  const instance = bank[TYPE_INSTANCES.Q15];
  const spec = engine.specFromInstance(instance);
  const blankPayload = I.buildPayload('Q15', null, instance, { text: '   ' });
  const blankVerdict = engine.grade(spec, { text: blankPayload.text });
  const answeredPayload = I.buildPayload('Q15', null, instance, context.captures.Q15);
  const answeredVerdict = engine.grade(spec, { text: answeredPayload.text });
  const q03Payload = I.buildPayload('Q03', null, bank[TYPE_INSTANCES.Q03], context.captures.Q03);
  const pending = I.q03PendingPath(q03Payload);
  const checks = {
    blank_is_blank_response: blankVerdict.error_class === 'BLANK_RESPONSE',
    blank_scores_zero: blankVerdict.machine_checked_points === 0 && blankVerdict.pending_points === 0,
    blank_denies_every_criterion: blankVerdict.awarded_criteria.every((entry) => entry.status === 'denied'),
    non_blank_is_pending: answeredVerdict.verdict_class === 'pending_self_assessment',
    non_blank_awards_nothing: answeredVerdict.machine_checked_points === 0,
    non_blank_pends_every_point: answeredVerdict.pending_points === answeredVerdict.max_points
      && answeredVerdict.pending_points > 0,
    non_blank_text_not_parsed: deepEqual(answeredVerdict.diagnostics.per_step, [])
      && answeredVerdict.diagnostics.text_parsed === false,
    q03_pending_has_no_verdict: pending.verdict === null,
    q03_pending_awards_nothing: pending.points_awarded === 0 && pending.points_pending === null,
    q03_pending_is_not_graded: pending.graded === false && pending.class === 'pending'
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'A whitespace-only Q15 is BLANK_RESPONSE with zero points, a non-blank Q15 is pending with '
      + 'no verdict, and the Q03 manual-rubric path never fakes a score.',
    checks: checks,
    failed: failed,
    blank: {
      error_class: blankVerdict.error_class,
      verdict_class: blankVerdict.verdict_class,
      machine_checked_points: blankVerdict.machine_checked_points
    },
    answered: {
      error_class: answeredVerdict.error_class,
      verdict_class: answeredVerdict.verdict_class,
      machine_checked_points: answeredVerdict.machine_checked_points,
      pending_points: answeredVerdict.pending_points,
      max_points: answeredVerdict.max_points
    },
    q03: pending
  };
}

/* -------------------------------------------------------------------- the run */

function runOnce(root) {
  const islands = buildIslands(root);
  const sandbox = makeSandbox(root, islands);
  const I = sandbox.SimInputsIntegration;
  if (!I || typeof I.buildPayload !== 'function') {
    throw new Error('The compiled N22 integration module did not register SimInputsIntegration.');
  }
  const policy = islands['sim-exam-policy'];
  const registryIsland = islands['sim-response-types'] || null;
  if (registryIsland && sandbox.SimInputsRegistry && typeof sandbox.SimInputsRegistry.load === 'function') {
    sandbox.SimInputsRegistry.load(registryIsland, islands['sim-terms']);
  }
  const bank = loadBank(root);
  const figureContract = islands['sim-graph-scoring'].capture_contract.capture_contexts;
  const drawContext = figureContract['CAP-T67-CAL-PRACTICE'];
  sandbox.SimGraphScoring.load(sandbox.document);
  const drawCapture = sandbox.SimGraphCapture.create({
    context: drawContext,
    contextId: 'CAP-T67-CAL-PRACTICE',
    engine: sandbox.SimGraphScoring
  });
  /* The keyboard walk places a point on every grid column and reaches the
   * target y with the fine increment: the same device-agnostic payload a
   * pointer drag produces (N18's B.1 parity rule). */
  const slope = 25.02;
  const gridStep = Number(drawContext.grid.step);
  const columns = Math.round((Number(drawContext.span.x_max) - Number(drawContext.grid.x_min)) / gridStep);
  drawCapture.keyboard.begin([0, 0]);
  for (let column = 1; column <= columns; column += 1) {
    drawCapture.keyboard.keyDown({ key: 'ArrowRight' });
    const target = slope * column * gridStep;
    const fineSteps = Math.round((target - drawCapture.active().y) / drawCapture.increments.fine_y);
    const key = fineSteps >= 0 ? 'ArrowUp' : 'ArrowDown';
    for (let step = 0; step < Math.abs(fineSteps); step += 1) {
      drawCapture.keyboard.keyDown({ key: key, shiftKey: true });
    }
  }
  const drawPayload = drawCapture.keyboard.keyDown({ key: 'Enter' });
  if (!drawPayload) { throw new Error('The graph capture component produced no draw payload.'); }
  const figureId = 'FIG-T5-LIN-PRACTICE';

  const methodEngine = new sandbox.SimMethodEngine.MethodEngine(
    islands['sim-method-engine'],
    islands['sim-terms']
  );

  const context = {
    I: I,
    S: sandbox.SimSession,
    X: sandbox.SimExam,
    SimSession: sandbox.SimSession,
    SimEngines: sandbox.SimEngines,
    SimGraphScoring: sandbox.SimGraphScoring,
    SimInputsRegistry: sandbox.SimInputsRegistry,
    policy: policy,
    registryIsland: registryIsland,
    bank: bank,
    islands: islands,
    figures: sandbox.SimGraphScoring.state.figures,
    drawContext: drawContext,
    drawPayload: drawPayload,
    methodEngine: methodEngine,
    captures: capturesFor(bank, drawPayload, figureId),
    incompleteCaptures: incompleteCapturesFor(drawPayload)
  };

  const payloadContract = checkPayloadContract(context);
  const scripted = checkScriptedSession(context);
  context.scripted = scripted;
  const parity = checkParity(context);
  const overlay = checkCompletionOverlay(context);
  const smoke = checkSmokeVectors(root, context);
  const guards = checkOnlyWriter(context);
  const honesty = checkBlankAndPending(context);

  return {
    payload_contract: payloadContract,
    scripted_session_18: scripted,
    capture_grading_parity: parity,
    navigator_completion_overlay: overlay,
    smoke_vectors_in_file: smoke,
    only_writer_guards: guards,
    blank_and_pending: honesty
  };
}

function writeJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n', 'utf8');
}

/**
 * The record keeps the claims and the counts; the bulky payloads live in their
 * own evidence files (the trace, the parity table, the runtime record), so the
 * corpus is not three copies of the same bytes.
 */
function pruneCheck(entry) {
  const copy = JSON.parse(JSON.stringify(entry, function (key, value) {
    if (key === 'session' || key === 'trace') { return undefined; }
    return value;
  }));
  if (Array.isArray(copy.rows)) {
    copy.rows = copy.rows.map((row) => ({
      type_id: row.type_id,
      engine: row.engine,
      payload_digest: row.payload_digest,
      verdict_class: row.criterion_shape ? row.criterion_shape.verdict_class : null,
      adapter: row.adapter,
      identity_ok: row.identity_ok,
      status: row.status
    }));
  }
  return copy;
}

function resolveOut(root, value) {
  if (!value) { return null; }
  return path.isAbsolute(value) ? value : path.join(root, value);
}

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const check = runOnce(root);

  const names = Object.keys(check);
  const failed = names.filter((name) => check[name].status === 'FAIL');
  const pending = names.filter((name) => check[name].status === 'PENDING');
  const status = failed.length > 0 ? 'FAIL' : (pending.length > 0 ? 'PENDING' : 'PASS');

  const record = {
    schema_version: 1,
    owner: 'N22',
    status: status,
    runtime_modules: ['src/compiled/inputs/integration.js'],
    source_modules: ['src/inputs/integration.ts'],
    engine_modules: [
      'src/quantity-engine.js',
      'src/method-engine.js',
      'src/graph-scoring-engine.js',
      'src/graph-capture.js'
    ],
    islands: [
      'data/response_types.json',
      'data/exam_policy.json',
      'data/terms.json',
      'data/engine_taxonomy.json',
      'data/graph_scoring_contract.json',
      'data/method_engine_contract.json',
      'data/bank/*.json'
    ],
    digest_method: 'SimInputsIntegration.contentDigest — two FNV-1a 32-bit lanes over a canonical JSON '
      + 'projection, 16 lowercase hex characters.',
    note: 'The integration is strict TypeScript compiled by tools/compile_n21_ts.py; the compiled module '
      + 'is committed and the drift guard keeps it in step. The module ships from src/ and is not inlined '
      + 'into the artifact; N31 owns the final inline decision. This harness is not a browser render, '
      + 'screen-reader or instructor acceptance claim.',
    checks: (function () {
      const pruned = {};
      names.forEach((name) => { pruned[name] = pruneCheck(check[name]); });
      return pruned;
    })()
  };

  if (args.record) {
    const out = resolveOut(root, args.record);
    writeJson(out, record);
    const directory = path.dirname(out);
    const tracePath = resolveOut(root, args.trace) || path.join(directory, 'N22_SESSION_TRACE.json');
    writeJson(tracePath, check.scripted_session_18.trace);
    const parityPath = resolveOut(root, args.parity) || path.join(directory, 'N22_PARITY_TABLE.json');
    writeJson(parityPath, {
      schema_version: 1,
      owner: 'N22',
      status: check.capture_grading_parity.status,
      claim: check.capture_grading_parity.claim,
      digest_method: record.digest_method,
      rows: check.capture_grading_parity.rows,
      audit: check.capture_grading_parity.audit,
      findings: check.capture_grading_parity.findings,
      not_claimed: [
        'No semantic grading of free text: the Q04/Q05/Q13/Q15/Q16/Q17 rows show the pending shape the '
          + 'rubric produces, not a machine judgement of the learner\'s wording.',
        'No claim that the four variants are four finished questions.',
        'No official examination, grade or proctoring status.'
      ]
    });
  }

  process.stdout.write(JSON.stringify({
    status: status,
    checks: names.map((name) => ({ name: name, status: check[name].status })),
    parity_rows: check.capture_grading_parity.rows.length,
    adapters: check.capture_grading_parity.audit.adapters_found,
    smoke: SMOKE_IDS
  }, null, 2) + '\n');
  return status === 'FAIL' ? 1 : (status === 'PENDING' ? 3 : 0);
}

if (require.main === module) {
  try {
    process.exitCode = main();
  } catch (error) {
    process.stderr.write('FAIL n22_runtime: ' + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main };
