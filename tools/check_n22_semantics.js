#!/usr/bin/env node
/* N22 runtime harness: the response-type registry, the completion model and the
 * error-surface mapping, proved against the shipped runtime module
 * (src/compiled/inputs/registry.js — the deterministic TypeScript build).
 *
 * The harness proves the claims the roadmap asks N22 to prove:
 *
 *   1. registry_load              — the island loads, all eighteen contracts are
 *                                   complete, and the island digest is recorded;
 *   2. unknown_type_rejected      — an unknown type id fails loudly with
 *                                   E_INPUTS_UNKNOWN_TYPE naming the id, and no
 *                                   fallback text field is produced (A.1.1);
 *   3. completion_complete_cases  — one happy-path payload per type yields
 *                                   "complete" (A.1.2);
 *   4. completion_q13_missing_coefficient — a coefficient vector with one empty
 *                                   cell names the species;
 *   5. completion_q17_half_drawn_structure — a half-placed structure names the
 *                                   part that is not placed;
 *   6. completion_q12_value_without_binding — a read with values but no figure
 *                                   binding names the binding;
 *   7. completion_plot_state_short — a plot-state variant short of its declared
 *                                   point count names the count;
 *   8. error_surface_mixed_separators — "1,2,3" classifies as UNREADABLE_INPUT
 *                                   through N17, maps to the frozen Latvian text,
 *                                   and the raw string is preserved byte for byte
 *                                   (the input-preservation invariant, A.1.3);
 *   9. blank_response             — blank self-assessed text yields
 *                                   BLANK_RESPONSE, non-blank text yields pending
 *                                   with no verdict (N19 pending semantics);
 *  10. invalid_verdict_case       — a malformed payload of each class yields
 *                                   "invalid" with the frozen error id named.
 *
 * The harness is not a browser render, accessibility, print or instructor
 * acceptance claim. It is a machine-level proof of the contracts above.
 *
 * Usage: node tools/check_n22_semantics.js [--repo-root .] [--record PATH]
 */
'use strict';

const crypto = require('crypto');
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

/* -------------------------------------------------------------------- helpers */

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

/* The declared canonical JSON emission rule (sorted keys, no insignificant
 * whitespace) so the island digest here agrees with the Python gate's. */
function canonicalJson(value) {
  if (value === null || typeof value !== 'object') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonicalJson).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.map((key) => JSON.stringify(key) + ':' + canonicalJson(value[key])).join(',') + '}';
}

function deepCopy(value) {
  return JSON.parse(JSON.stringify(value));
}

function deepEqual(a, b) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function deepFreeze(value) {
  if (value === null || typeof value !== 'object') { return value; }
  Object.keys(value).forEach((key) => deepFreeze(value[key]));
  return Object.freeze(value);
}

function captureError(fn) {
  try {
    const value = fn();
    return { threw: false, value: value };
  } catch (error) {
    return { threw: true, code: error && error.code, message: error && error.message, error: error };
  }
}

function loadRuntime(root) {
  return require(path.join(root, 'src/compiled/inputs/registry.js'));
}

function loadBank(root) {
  const dir = path.join(root, 'data/bank');
  const files = fs.readdirSync(dir).filter((name) => name.endsWith('.json')).sort();
  const byType = {};
  const byId = {};
  files.forEach((name) => {
    const data = readJson(path.join(dir, name));
    (data.questions || []).forEach((question) => {
      byId[question.question_id] = question;
      if (!byType[question.type_id]) { byType[question.type_id] = []; }
      byType[question.type_id].push(question);
    });
  });
  return { byType: byType, byId: byId, files: files };
}

function termText(terms, key) {
  for (let i = 0; i < terms.terms.length; i += 1) {
    if (terms.terms[i].key === key) { return terms.terms[i].text_lv; }
  }
  return null;
}

/* The permanent negative fixtures (tools/fixtures/n22/*.json) are the single
 * source of the named A.1.2 cases: the harness asserts the verdict against the
 * fixture's own expectation instead of restating it. */
function loadFixture(context, name) {
  const file = path.join(context.repoRoot, 'tools/fixtures/n22', name);
  const fixture = readJson(file);
  const instance = fixture.bank_question_id
    ? context.bank.byId[fixture.bank_question_id]
    : fixture.instance;
  return { fixture: fixture, instance: instance, payload: deepCopy(fixture.payload), file: 'tools/fixtures/n22/' + name };
}

function assertExpectation(context, fixture, verdict) {
  const expected = fixture.expected || {};
  const checks = {};
  checks.status = verdict.status === expected.status;
  checks.missing_field_ids = deepEqual(verdict.missing.map((item) => item.field_id),
    expected.missing_field_ids || []);
  checks.error_ids = deepEqual(verdict.errors.map((error) => error.id), expected.error_ids || []);
  const names = verdict.missing.map((item) => item.name).join(' | ');
  checks.name_contains = (expected.name_contains || []).every((token) => names.indexOf(token) !== -1);
  checks.name_terms = (expected.name_terms || []).every((key) => {
    const text = termText(context.terms, key);
    if (text === null) { return false; }
    const skeleton = text.replace(/\{[a-z_]+\}/g, '').split(':')[0].trim();
    return skeleton.length > 0 && names.indexOf(skeleton) !== -1;
  });
  checks.instance_resolved = Boolean(fixture.bank_question_id) || Boolean(fixture.instance);
  return checks;
}

/* --------------------------------------------------------------- 1. registry */

function checkRegistryLoad(context) {
  const checks = {};
  const facts = context.registry.load(context.island, context.terms);
  checks.island_id = facts.island_id === 'sim-response-types';
  checks.schema_version = facts.schema_version === 1;
  checks.type_count_18 = facts.type_count === 18;
  checks.type_ids_canonical = deepEqual(facts.type_ids, context.registry.typeIds()) &&
    facts.type_ids.length === 18;
  checks.completed_types = deepEqual(facts.completed_types,
    ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15']);
  checks.terms_loaded = context.registry.termsLoaded() === true;

  const incomplete = [];
  facts.type_ids.forEach((typeId) => {
    const entry = context.registry.contractFor(typeId);
    const complete = Boolean(entry.renderer_key) &&
      Array.isArray(entry.fields) && entry.fields.length > 0 &&
      Boolean(entry.completion_rule && entry.completion_rule.model) &&
      Array.isArray(entry.error_surfaces) && entry.error_surfaces.length > 0 &&
      Boolean(entry.keyboard && entry.keyboard.path_key) &&
      Boolean(entry.accessible_alternative && entry.accessible_alternative.label_key) &&
      Boolean(entry.name_key);
    if (!complete) { incomplete.push(typeId); }
  });
  checks.every_type_complete = incomplete.length === 0;
  checks.incomplete_types = incomplete;

  checks.completed_types_bound = context.registry.completedTypes().every((typeId) => {
    const grading = context.registry.contractFor(typeId).grading_binding;
    return grading && grading.class && grading.engine && grading.consumes.length > 0 && grading.adapter === 'none';
  });
  checks.island_frozen = Object.isFrozen(context.registry.contractFor('Q01'));
  checks.announcement_keys_resolve = context.registry.announcementKey('complete') === 'input.state.complete' &&
    context.registry.announcementKey('input_preserved') === 'input.error.preserved' &&
    context.registry.errorMessage('E_GRAPH_WRONG_DIRECTION', context.terms).length > 0;
  const badAnnouncement = captureError(() => context.registry.announcementKey('nope'));
  checks.unknown_announcement_refused = badAnnouncement.threw && badAnnouncement.code === 'E_INPUTS_REGISTRY_INVALID';

  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The #sim-response-types island loads into eighteen complete contracts (render, payload, '
         + 'completion, error and ARIA), the seven completed types carry a grading binding, and the '
         + 'registry is frozen against accidental mutation.',
    checks: checks,
    failed: failed,
    island_file: 'data/response_types.json',
    island_file_sha256: sha256(fs.readFileSync(context.islandPath, 'utf8')),
    island_canonical_digest: sha256(canonicalJson(context.island)),
    island_canonical_bytes: Buffer.byteLength(canonicalJson(context.island), 'utf8'),
    island_file_bytes: fs.statSync(context.islandPath).size
  };
}

/* --------------------------------------------------------- 2. unknown type id */

function checkUnknownType(context) {
  const checks = {};
  const lookup = captureError(() => context.registry.contractFor('Q99'));
  checks.throws = lookup.threw === true;
  checks.code_is_unknown_type = lookup.threw && lookup.code === 'E_INPUTS_UNKNOWN_TYPE';
  checks.message_names_the_id = lookup.threw && String(lookup.message).indexOf('Q99') !== -1;
  checks.no_fallback_returned = lookup.threw && lookup.value === undefined;

  const surfaces = captureError(() => context.registry.errorSurfaces('Q99'));
  checks.error_surfaces_refuses = surfaces.threw && surfaces.code === 'E_INPUTS_UNKNOWN_TYPE';
  const model = captureError(() => context.registry.completion('Q99', null, context.bank.byType.Q01[0],
    { kind: 'numeric', values: { value: '1' } }));
  checks.completion_refuses = model.threw && model.code === 'E_INPUTS_UNKNOWN_TYPE';
  checks.completion_message_names_the_id = model.threw && String(model.message).indexOf('Q99') !== -1;

  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'An unknown type id is refused by name with E_INPUTS_UNKNOWN_TYPE — the registry never '
         + 'falls back to a text field, because a silent fallback changes the task meaning.',
    checks: checks,
    failed: failed,
    scratch_type_id: 'Q99',
    observed: { code: lookup.code, message: lookup.message }
  };
}

/* ----------------------------------------------------- payload construction */

function numericValues(instance, filler) {
  const values = {};
  (instance.payload.input_fields || []).forEach((field) => { values[field.field_id] = filler; });
  if (Array.isArray(instance.payload.substeps)) {
    instance.payload.substeps.forEach((step) => { values[step.step_id] = filler; });
  }
  return values;
}

function happyPayload(context, typeId, instance) {
  const payload = instance.payload || {};
  switch (typeId) {
    case 'Q01':
    case 'Q09':
    case 'Q10':
      return { kind: 'numeric', values: numericValues(instance, '4,70') };
    case 'Q02':
      return { kind: 'numeric', values: numericValues(instance, '0,0479') };
    case 'Q03': {
      const fillIns = {};
      (payload.steps || []).forEach((step) => { fillIns[step.step_id] = 'c = γ/M'; });
      return {
        kind: 'method', variant: 'Q03_template', choice: 'T1',
        fill_ins: fillIns, conserved: 'masa saglabājas'
      };
    }
    case 'Q04': {
      const vector = (payload.species_list || []).map(() => '1');
      return { kind: 'method', variant: 'Q04_vector', vector: vector };
    }
    case 'Q05': {
      const rows = {};
      (payload.steps || []).forEach((step) => { rows[step.step_id] = 'pusreakcija'; });
      return { kind: 'method', variant: 'Q05_rows', rows: rows };
    }
    case 'Q06': {
      const pairs = (payload.left_items || []).map((left, index) => ({
        left_id: left.id,
        right_id: (payload.right_items[index] || payload.right_items[0]).id
      }));
      return { kind: 'matching', pairs: pairs };
    }
    case 'Q07':
    case 'Q14':
    case 'Q18': {
      const options = payload.options || [];
      return {
        kind: 'option_select',
        selected: options.length ? [options[0].option_id] : [],
        justification: payload.requires_justification ? 'jo tā ir pareizi' : undefined
      };
    }
    case 'Q08': {
      const items = payload.items || [];
      const order = (payload.correct_order || items.map((item) => item.item_id)).slice();
      return { kind: 'ordering', order: order, explanation: 'jo atzīmi izlīdzina pēc sajaukšanas' };
    }
    case 'Q11': {
      const points = (payload.points || []).map((point) => ({ x: Number(point.x), y: Number(point.y) }));
      const drawn = points.length >= 2 ? points : [{ x: 0, y: 0 }, { x: 1, y: 1 }];
      return {
        kind: 'graph',
        variant: 'Q11_record',
        record: { points: points, x_axis: payload.x_axis, y_axis: payload.y_axis },
        draw_payload: {
          schema_id: 'sim-graph-draw-v1',
          kind: 'line',
          points: drawn,
          axes: { x: { min: 0, max: 1 }, y: { min: 0, max: 1 } },
          span: { x_min: 0, x_max: 1, edge_rule: 'inclusive' },
          grid: { x_min: 0, x_max: 1, step: 0.1 }
        }
      };
    }
    case 'Q12':
      return {
        kind: 'graph', variant: 'Q12_read',
        read: { x: '30', y: '75', figure_binding: 'FIG-T5-LIN-PRACTICE' }
      };
    case 'Q13': {
      const vector = (payload.species_list || []).map(() => '1');
      return {
        kind: 'method', variant: 'Q13_vector', vector: vector,
        located: (payload.species_list || ['S1'])[0],
        replacement: '2', reason: 'koeficients nesaglabā atomu skaitu'
      };
    }
    case 'Q15':
    case 'Q16':
      return { kind: 'method', variant: typeId === 'Q15' ? 'Q15_text' : 'Q16_text',
        text: 'MgCl₂ šķīdumā ir kustīgi joni Mg²⁺ un Cl⁻, tāpēc šķīdums vada strāvu.' };
    case 'Q17': {
      const pairMap = {};
      (payload.steps || []).forEach((step) => { pairMap[step.step_id] = 'atbilde'; });
      return { kind: 'method', variant: 'Q17_pairs', pair_map: pairMap };
    }
    default:
      throw new Error('no payload builder for ' + typeId);
  }
}

/* ------------------------------------------------------ 3. happy-path verdicts */

function checkCompleteCases(context) {
  const checks = {};
  const verdicts = {};
  context.registry.typeIds().forEach((typeId) => {
    const instance = context.bank.byType[typeId][0];
    if (!instance) {
      checks['instance_' + typeId] = false;
      return;
    }
    const payload = happyPayload(context, typeId, instance);
    const verdict = context.registry.completion(typeId, context.registry.contractFor(typeId), instance, payload);
    verdicts[typeId] = { status: verdict.status, missing: verdict.missing.length, errors: verdict.errors.length };
    checks['complete_' + typeId] = verdict.status === 'complete';
    checks['no_missing_' + typeId] = verdict.missing.length === 0;
    checks['no_errors_' + typeId] = verdict.errors.length === 0;
  });
  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'One happy-path payload per type yields the "complete" verdict, so every one of the '
         + 'eighteen contracts has a reachable completion state.',
    checks: checks,
    failed: failed,
    verdicts: verdicts
  };
}

/* ---------------------------------------------- 4. Q13 missing coefficient */

function checkQ13MissingCoefficient(context) {
  const loaded = loadFixture(context, 'q13_missing_coefficient.json');
  const fixture = loaded.fixture;
  const verdict = context.registry.completion(fixture.type_id, null, loaded.instance, loaded.payload);
  const checks = assertExpectation(context, fixture, verdict);
  checks.empty_cell_only = loaded.payload.vector.filter((value) => value === '').length === 1;
  checks.species_named = verdict.missing.length > 0 &&
    verdict.missing[0].name.indexOf(loaded.instance.payload.species_list[1]) !== -1;
  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: fixture.claim,
    fixture: loaded.file,
    checks: checks,
    failed: failed,
    observed: { status: verdict.status, missing: verdict.missing }
  };
}

/* ------------------------------------------- 5. Q17 half-drawn structure */

function checkQ17HalfDrawnStructure(context) {
  const loaded = loadFixture(context, 'q17_half_drawn_structure.json');
  const fixture = loaded.fixture;
  const verdict = context.registry.completion(fixture.type_id, null, loaded.instance, loaded.payload);
  const checks = assertExpectation(context, fixture, verdict);
  checks.placed_part_not_reported = verdict.missing.every((item) => item.field_id !== 'structure.P1');
  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: fixture.claim,
    fixture: loaded.file,
    checks: checks,
    failed: failed,
    observed: { status: verdict.status, missing: verdict.missing }
  };
}

/* ------------------------------------------- 6. Q12 read without binding */

function checkQ12ValueWithoutBinding(context) {
  const loaded = loadFixture(context, 'q12_value_without_binding.json');
  const fixture = loaded.fixture;
  const verdict = context.registry.completion(fixture.type_id, null, loaded.instance, loaded.payload);
  const checks = assertExpectation(context, fixture, verdict);
  checks.values_not_reported_missing = verdict.missing.every((item) =>
    item.field_id.indexOf('read.x') === -1 && item.field_id.indexOf('read.y') === -1);
  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: fixture.claim,
    fixture: loaded.file,
    checks: checks,
    failed: failed,
    observed: { status: verdict.status, missing: verdict.missing }
  };
}

/* ------------------------------------------- 7. plot_state short of points */

function checkPlotStateShort(context) {
  const loaded = loadFixture(context, 'plot_state_short.json');
  const fixture = loaded.fixture;
  const verdict = context.registry.completion(fixture.type_id, null, loaded.instance, loaded.payload);
  const checks = assertExpectation(context, fixture, verdict);
  checks.declared_count_is_the_instance_points = loaded.instance.payload.points.length === 4;
  const short = context.registry.completion(fixture.type_id, null, loaded.instance,
    { kind: 'graph', variant: 'Q11_record', record: { points: [{ x: 0, y: 1 }] } });
  checks.record_short_reports_the_count = short.missing.some((item) => item.field_id === 'record.points');
  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: fixture.claim,
    fixture: loaded.file,
    checks: checks,
    failed: failed,
    observed: { status: verdict.status, missing: verdict.missing },
    naming_resolution_lv: 'Ceļa karte šo gadījumu sauc "Q18 short plot", bet Q18 kā tips paliek '
      + 'option_select (N04). Plot-state variants ir graph klases vārdnīcas vienums Q18_plot_state '
      + '(N21-C01), tāpēc fixtures iet caur grafa klases ierakstu; sk. konfliktu N22-C02 salā.'
  };
}

/* ---------------------------------------- 8. mixed separators / preservation */

function loadEngines(root) {
  const engines = require(path.join(root, 'src/quantity-engine.js'));
  const islands = {
    'sim-conventions': 'data/conventions.json',
    'sim-terms': 'data/terms.json',
    'sim-engines': 'data/engine_taxonomy.json'
  };
  const doc = {
    getElementById(id) {
      if (!islands[id]) { return null; }
      return { textContent: fs.readFileSync(path.join(root, islands[id]), 'utf8') };
    }
  };
  engines.load(doc);
  return engines;
}

function checkMixedSeparators(context) {
  const checks = {};
  const engines = loadEngines(context.repoRoot);
  const classification = engines.classify({ raw: '1,2,3', unit: 'g/L', expected_unit: 'g/L' });
  checks.n17_classifies_unreadable = classification.taxonomy_class === 'UNREADABLE_INPUT';
  checks.n17_signature = classification.signature === 'MC-2B-02';

  const surface = context.registry.errorSurfaceFor('Q01', classification.taxonomy_class);
  checks.surface_declared_by_the_type = surface.id === 'UNREADABLE_INPUT';
  checks.surface_key_is_the_frozen_one = surface.message_key === 'feedback.error.unreadable';
  const message = context.registry.errorMessage(classification.taxonomy_class, context.terms);
  checks.message_is_the_frozen_text = message === termText(context.terms, 'feedback.error.unreadable');
  checks.message_is_latvian = /[āčēģīķļņšūž]/i.test(message);

  /* The input-preservation invariant: the raw strings survive the error path. */
  const instance = context.bank.byType.Q01[0];
  const fieldId = instance.payload.input_fields[0].field_id;
  const payload = { kind: 'numeric', values: {} };
  payload.values[fieldId] = '1,2,3';
  const before = deepCopy(payload);
  const beforeJson = JSON.stringify(payload);

  const verdict = context.registry.completion('Q01', null, instance, payload);
  const message2 = context.registry.errorMessage(classification.taxonomy_class, context.terms);
  const surface2 = context.registry.errorSurfaceFor('Q01', classification.taxonomy_class);

  checks.payload_deep_equal_after_error = deepEqual(payload, before);
  checks.payload_bytes_identical = JSON.stringify(payload) === beforeJson;
  checks.raw_string_untouched = payload.values[fieldId] === '1,2,3';
  checks.verdict_did_not_neutralise_the_cell = verdict.status === 'complete';
  checks.second_call_stable = message2 === message && surface2.message_key === surface.message_key;

  /* A frozen payload cannot be written to at all: the model would throw. */
  const frozen = deepFreeze(deepCopy(before));
  const frozenRun = captureError(() => context.registry.completion('Q01', null, instance, frozen));
  checks.frozen_payload_not_mutated = frozenRun.threw === false;

  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'A mixed-separator number classifies as UNREADABLE_INPUT through N17, maps to the frozen '
         + 'Latvian feedback text declared by the type, and the raw input is preserved byte for byte '
         + '— an error is an annotation, never a rewrite.',
    checks: checks,
    failed: failed,
    observed: {
      taxonomy_class: classification.taxonomy_class,
      signature: classification.signature,
      message_key: surface.message_key,
      message: message,
      raw_before: before.values[fieldId],
      raw_after: payload.values[fieldId]
    },
    naming_resolution_lv: 'MIXED_SEPARATORS nav saldēts kļūdas id (sk. konfliktu N22-C01); '
      + 'jaukta atdalītāja ievads klasificējas kā UNREADABLE_INPUT ar feedback.error.unreadable tekstu.'
  };
}

/* ------------------------------------------------------- 9. blank response */

function checkBlankResponse(context) {
  const checks = {};
  const instance = context.bank.byType.Q15[0];
  const blank = context.registry.completion('Q15', null, instance,
    { kind: 'method', variant: 'Q15_text', text: '   ' });
  checks.blank_not_complete = blank.status !== 'complete';
  checks.blank_reports_blank_response = blank.errors.some((error) => error.id === 'BLANK_RESPONSE');
  checks.blank_names_the_text = blank.missing.some((item) => item.field_id === 'text');
  checks.blank_message_key = blank.errors.length > 0 && blank.errors[0].message_key === 'input.error.blank';
  const blankMessage = context.registry.errorMessage('BLANK_RESPONSE', context.terms);
  checks.blank_message_resolves = typeof blankMessage === 'string' && blankMessage.length > 0 && /[āčēģīķļņšūž]/i.test(blankMessage);

  const filled = context.registry.completion('Q15', null, instance,
    { kind: 'method', variant: 'Q15_text', text: 'MgCl₂ šķīdumā ir kustīgi joni.' });
  checks.filled_complete = filled.status === 'complete';
  checks.filled_has_no_verdict = filled.errors.length === 0;
  checks.pending_grading_class = context.registry.contractFor('Q15').grading_binding.class === 'pending';
  checks.pending_engine = context.registry.contractFor('Q15').grading_binding.engine === 'manual-rubric-pending';

  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'Blank self-assessed text yields BLANK_RESPONSE with the Latvian announcement; any content '
         + 'is complete but stays pending — the component never pretends to have graded the text.',
    checks: checks,
    failed: failed,
    observed: { blank: blank, filled: filled.status, announced: blankMessage }
  };
}

/* -------------------------------------------------- 10. invalid verdict cases */

function checkInvalidVerdicts(context) {
  const checks = {};
  const q11 = context.bank.byType.Q11[0];
  const q01 = context.bank.byType.Q01[0];
  const q06 = context.bank.byType.Q06[0];
  const q12 = context.bank.byType.Q12[0];
  const cases = [];

  const malformedFixture = loadFixture(context, 'graph_payload_malformed.json');
  const badSchemaVerdict = context.registry.completion(malformedFixture.fixture.type_id, null,
    malformedFixture.instance, malformedFixture.payload);
  const malformedChecks = assertExpectation(context, malformedFixture.fixture, badSchemaVerdict);
  Object.keys(malformedChecks).forEach((key) => { checks['graph_malformed_' + key] = malformedChecks[key]; });
  cases.push({
    case: 'graph_payload_malformed',
    fixture: malformedFixture.file,
    status: badSchemaVerdict.status,
    error_ids: badSchemaVerdict.errors.map((error) => error.id)
  });

  const onePoint = happyPayload(context, 'Q11', q11);
  onePoint.draw_payload.points = [{ x: 0, y: 0 }];
  const onePointVerdict = context.registry.completion('Q11', null, q11, onePoint);
  cases.push({
    case: 'graph_empty_submission',
    status: onePointVerdict.status,
    error_ids: onePointVerdict.errors.map((error) => error.id)
  });
  checks.graph_empty_invalid = onePointVerdict.status === 'invalid';
  checks.graph_empty_id = onePointVerdict.errors.some((error) => error.id === 'E_GRAPH_EMPTY_SUBMISSION');

  const fieldId = q01.payload.input_fields[0].field_id;
  const numericPayload = { kind: 'numeric', values: {} };
  numericPayload.values[fieldId] = 470;
  const numericVerdict = context.registry.completion('Q01', null, q01, numericPayload);
  cases.push({
    case: 'numeric_value_not_raw_string',
    status: numericVerdict.status,
    error_ids: numericVerdict.errors.map((error) => error.id)
  });
  checks.numeric_coercion_invalid = numericVerdict.status === 'invalid';
  checks.numeric_coercion_id = numericVerdict.errors.some((error) => error.id === 'UNREADABLE_INPUT');

  const pairVerdict = context.registry.completion('Q06', null, q06,
    { kind: 'matching', pairs: ['L1-R1'] });
  cases.push({
    case: 'matching_pair_not_an_object',
    status: pairVerdict.status,
    error_ids: pairVerdict.errors.map((error) => error.id)
  });
  checks.pair_shape_invalid = pairVerdict.status === 'invalid';
  checks.pair_shape_id = pairVerdict.errors.some((error) => error.id === 'UNREADABLE_INPUT');

  const readVerdict = context.registry.completion('Q12', null, q12,
    { kind: 'graph', variant: 'Q12_read', read: { x: 30, y: '75', figure_binding: 'FIG-T5-LIN-PRACTICE' } });
  cases.push({
    case: 'read_value_not_raw_string',
    status: readVerdict.status,
    error_ids: readVerdict.errors.map((error) => error.id)
  });
  checks.read_coercion_invalid = readVerdict.status === 'invalid';
  checks.read_coercion_id = readVerdict.errors.some((error) => error.id === 'E_GRAPH_PAYLOAD_MALFORMED');

  const kindVerdict = context.registry.completion('Q01', null, q01,
    { kind: 'matching', pairs: [] });
  cases.push({
    case: 'payload_kind_mismatch',
    status: kindVerdict.status,
    error_ids: kindVerdict.errors.map((error) => error.id)
  });
  checks.kind_mismatch_invalid = kindVerdict.status === 'invalid';
  checks.kind_mismatch_field = kindVerdict.errors.length === 1 && kindVerdict.errors[0].field === 'kind';

  const declared = context.registry.errorSurfaces('Q11');
  checks.graph_ids_are_declared = ['E_GRAPH_PAYLOAD_MALFORMED', 'E_GRAPH_EMPTY_SUBMISSION']
    .every((id) => declared.indexOf(id) !== -1);

  const failed = Object.keys(checks).filter((key) => checks[key] === false);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'A structurally malformed payload yields the "invalid" verdict with the frozen error id '
         + 'named, per class: graph body, graph emptiness, numeric coercion, pair shape, read value '
         + 'and payload-kind mismatch.',
    checks: checks,
    failed: failed,
    cases: cases
  };
}

/* --------------------------------------------------------------------- main */

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const registry = loadRuntime(root);
  const islandPath = path.join(root, 'data/response_types.json');
  const context = {
    repoRoot: root,
    registry: registry,
    island: readJson(islandPath),
    islandPath: islandPath,
    terms: readJson(path.join(root, 'data/terms.json')),
    bank: loadBank(root)
  };

  const checks = {};
  checks.registry_load = checkRegistryLoad(context);
  checks.unknown_type_rejected = checkUnknownType(context);
  checks.completion_complete_cases = checkCompleteCases(context);
  checks.completion_q13_missing_coefficient = checkQ13MissingCoefficient(context);
  checks.completion_q17_half_drawn_structure = checkQ17HalfDrawnStructure(context);
  checks.completion_q12_value_without_binding = checkQ12ValueWithoutBinding(context);
  checks.completion_plot_state_short = checkPlotStateShort(context);
  checks.error_surface_mixed_separators = checkMixedSeparators(context);
  checks.blank_response = checkBlankResponse(context);
  checks.invalid_verdict_case = checkInvalidVerdicts(context);

  const failed = Object.keys(checks).filter((key) => checks[key].status !== 'PASS');
  const record = {
    schema_version: 1,
    owner: 'N22',
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    runtime_modules: ['src/compiled/inputs/registry.js'],
    source_modules: ['src/inputs/registry.ts'],
    island: 'data/response_types.json',
    terms_island: 'data/terms.json',
    note: 'The TypeScript source is the source of truth; the compiled module is committed and is '
        + 'checked for drift by tools/compile_n21_ts.py --check. Errors are annotations: no fixture '
        + 'writes to a payload, and the preservation fixture asserts byte equality.',
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
    process.stderr.write('FAIL n22_semantics: ' + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main };
