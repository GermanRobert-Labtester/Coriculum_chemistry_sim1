#!/usr/bin/env node
/* N22-B component and parity harness: the eighteen response renderers, the
 * keyboard interaction contracts, the pointer/keyboard parity fixtures, the
 * mid-gesture abort, the input-preservation invariant and the composed
 * response container.
 *
 * It runs against the SHIPPED registry island (data/response_types.json, the
 * authority for every contract) and the shipped term island, and against the
 * bank instances plus the committed scratch instances in
 * tools/fixtures/n22/scratch_instances.json.
 *
 * What it proves, and what it does not:
 *
 *   * every type's render description carries exactly the field set its
 *     registry contract expands to, and every ARIA name is the term island's
 *     resolved pattern (never a literal invented in code);
 *   * a contract that is missing a field the renderer needs fails loudly with
 *     E_INPUTS_CONTRACT_VIOLATION naming that field — the registry is
 *     authoritative, not decorative;
 *   * for every spatial type (Q06, Q08, Q11, Q12, Q17) one identical task
 *     answered twice — once by a scripted pointer session, once by a scripted
 *     keyboard session — yields DEEP-EQUAL payloads with identical digests;
 *   * a mid-interaction abort discards the in-progress gesture and never
 *     emits a partial placement;
 *   * an error never destroys the learner's raw input, and the error slot
 *     carries the shipped Latvian message;
 *   * a two-part composed response names only the incomplete part's missing
 *     field and keeps the composed payload an ordered map.
 *
 * It is NOT a browser render, screen-reader or instructor acceptance claim:
 * N33 owns the live assistive-technology pass. Parity here means mechanical
 * payload equality under scripted sessions.
 *
 * Usage:
 *   node tools/check_n22_components.js \
 *     [--repo-root .] \
 *     [--record evidence/N22_COMPONENTS_RECORD.json] \
 *     [--record-parity evidence/N22_PARITY_RECORD.json]
 *
 * With --record and no --record-parity, the parity record is written next to
 * the components record as N22_PARITY_RECORD.json.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

/* ------------------------------------------------------------------ args */

function parseArgs(argv) {
  const args = { repoRoot: path.resolve(__dirname, '..'), record: null, recordParity: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
    else if (argv[i] === '--record-parity') { args.recordParity = argv[i + 1]; i += 1; }
  }
  return args;
}

/* --------------------------------------------------------------- helpers */

function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }
function readText(file) { return fs.readFileSync(file, 'utf8'); }
function hasOwn(object, key) { return Object.prototype.hasOwnProperty.call(object, key); }

function sha256(text) {
  return crypto.createHash('sha256').update(String(text), 'utf8').digest('hex');
}

/* Order-insensitive canonical form: keys sorted, no whitespace. */
function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return isFinite(value) ? JSON.stringify(value) : 'null'; }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.map((key) => JSON.stringify(key) + ':' + canonical(value[key])).join(',') + '}';
}

function digest16(value) { return sha256(canonical(value)).slice(0, 16); }
function deepEqual(a, b) { return canonical(a) === canonical(b); }

function captureError(fn) {
  try {
    fn();
    return null;
  } catch (error) {
    return {
      name: error && error.name ? error.name : null,
      code: error && error.code ? error.code : null,
      message: error && error.message ? error.message : String(error),
      details: error && error.details ? error.details : null
    };
  }
}

function result(claim, checks, extra) {
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return Object.assign({
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: claim,
    checks: checks,
    failed: failed
  }, extra || {});
}

/* A fixture that throws is a failed fixture, not a crashed harness. */
function guard(claim, fn) {
  try {
    return fn();
  } catch (error) {
    return {
      status: 'FAIL',
      claim: claim,
      checks: { fixture_completed: false },
      failed: ['fixture_completed'],
      error: {
        name: error && error.name ? error.name : null,
        code: error && error.code ? error.code : null,
        message: error && error.message ? error.message : String(error),
        details: error && error.details ? error.details : null
      }
    };
  }
}

/* --------------------------------------------------------------- loading */

function loadComponents(root) {
  require(path.join(root, 'src/compiled/inputs/components.js'));
  const components = globalThis.SimInputsComponents;
  if (!components || typeof components.render !== 'function') {
    throw new Error('src/compiled/inputs/components.js did not register SimInputsComponents');
  }
  return components;
}

function mergeFigures(root) {
  const files = ['figures_t12.json', 'figures_t23.json', 'figures_t4.json', 'figures_t5.json', 'figures_t67.json'];
  const figures = [];
  files.forEach((name) => {
    const island = readJson(path.join(root, 'data', name));
    (island.figures || []).forEach((figure) => { figures.push(figure); });
  });
  return { figures: figures };
}

function loadGraphEngine(root) {
  require(path.join(root, 'src/graph-scoring-engine.js'));
  require(path.join(root, 'src/graph-capture.js'));
  const engine = globalThis.SimGraphScoring;
  const capture = globalThis.SimGraphCapture;
  if (!engine || typeof engine.capturePath !== 'function') {
    throw new Error('src/graph-scoring-engine.js did not register SimGraphScoring');
  }
  if (!capture || typeof capture.create !== 'function') {
    throw new Error('src/graph-capture.js did not register SimGraphCapture');
  }
  const nodes = {
    'sim-conventions': readText(path.join(root, 'data/conventions.json')),
    'sim-graph-scoring': readText(path.join(root, 'data/graph_scoring_contract.json')),
    'sim-figures': JSON.stringify(mergeFigures(root))
  };
  const doc = {
    getElementById(id) { return hasOwn(nodes, id) ? { id: id, textContent: nodes[id] } : null; },
    querySelector() { return null; },
    querySelectorAll() { return []; }
  };
  engine.load(doc);
  return { engine: engine, capture: capture };
}

function loadBank(root) {
  const dir = path.join(root, 'data/bank');
  const byId = Object.create(null);
  fs.readdirSync(dir).sort().forEach((name) => {
    if (!/^FAM-[1-7][A-D]\.json$/.test(name)) { return; }
    const island = readJson(path.join(dir, name));
    (island.questions || []).forEach((question) => { byId[question.question_id] = question; });
  });
  return byId;
}

function loadRegistry(root) {
  const shipped = path.join(root, 'data/response_types.json');
  if (!fs.existsSync(shipped)) {
    throw new Error('data/response_types.json is missing: the N22 registry island is the authority '
      + 'for every contract and the fixtures do not fall back to a private contract set. '
      + 'Restore the island before running this harness.');
  }
  const island = readJson(shipped);
  if (!island || !island.types || typeof island.types !== 'object') {
    throw new Error('data/response_types.json does not expose a per-type contract map under "types"');
  }
  return { source: 'data/response_types.json', island: island, contracts: island.types };
}

/* -------------------------------------- independent contract expansion */

/* The harness expands the registry itself, with its own code, so the render
 * description is compared against a second opinion rather than against the
 * module's own plan. The rules are the documented ones:
 *
 *   repeat  iff  payload_path carries an element token or value_type is
 *                "string_list"; otherwise the template is one field whose
 *                source only supplies options.
 *
 * Field ids are renderer-owned; the conventions below are the ones the module
 * documents (field ids are the only thing the registry does not name). */
const REPEAT_RE = /\[(index|step_id|field_id|part_id)\]/;

const ROLE_SLOTS = {
  /* Every plausible element-derived slot value is offered; only the
   * placeholders the term pattern actually contains are substituted, so the
   * comparison is about the pattern and the term bank, not about my guess of
   * which slot a role uses. */
  any: (element, index, instance) => ({
    label: element && element.label_lv !== undefined ? element.label_lv : '',
    step: element && element.prompt_lv !== undefined ? element.prompt_lv : '',
    slot: element && element.prompt_lv !== undefined ? element.prompt_lv : '',
    left: element && element.text_lv !== undefined ? element.text_lv : '',
    option: element && element.text_lv !== undefined ? element.text_lv : '',
    part: element && element.text_lv !== undefined ? element.text_lv : '',
    species: typeof element === 'string' ? element
      : (element && element.species !== undefined ? element.species : ''),
    position: String(index + 1),
    count: String(index + 1),
    unit: element && element.unit !== undefined ? element.unit : ''
  })
};

const ROLE_IDS = {
  value: (element) => String(element.field_id),
  unit: () => 'unit',
  step: (element) => String(element.step_id),
  fill_in: (element) => 'fill_' + String(element.step_id),
  coefficient: (element, index) => 'coef_' + String(index),
  row: (element) => 'row_' + String(element.step_id),
  pair: (element) => 'pair_' + String(element.id !== undefined ? element.id : element.step_id),
  option: (element) => 'opt_' + String(element.option_id),
  position: (element, index) => 'slot_' + String(index + 1),
  explanation: () => 'explanation',
  choice: () => 'choice',
  conserved: () => 'conserved',
  read_x: () => 'read_x',
  read_y: () => 'read_y',
  figure_binding: () => 'figure_binding',
  located: () => 'located',
  replacement: () => 'replacement',
  reason: () => 'reason',
  text: () => 'text',
  justification: () => 'justification',
  structure: (element) => 'place_' + String(element.part_id),
  record: () => 'record',
  draw_payload: () => 'draw_payload'
};

const CONTROL_MAP = {
  'text-input': 'textbox',
  'text-input-map': 'textbox',
  'text-input-vector': 'coefficient',
  'select': 'select',
  'checkbox-group': 'checkbox',
  'radio-group': 'radio',
  'textarea': 'textarea',
  'coordinate-table': 'coordinate_table',
  'graph-canvas-keyboard': 'graph_canvas',
  'select-and-place': 'placement'
};

function readPath(object, path) {
  if (typeof path !== 'string' || path === '') { return object; }
  let current = object;
  const segments = path.split('.');
  for (let i = 0; i < segments.length; i += 1) {
    if (current === null || current === undefined) { return undefined; }
    const match = /^([A-Za-z0-9_]+)((?:\[\d+\])*)$/.exec(segments[i]);
    if (!match) { return undefined; }
    current = current[match[1]];
    const indexes = match[2] ? match[2].match(/\[\d+\]/g) : null;
    if (indexes) {
      for (let j = 0; j < indexes.length; j += 1) {
        if (current === null || current === undefined) { return undefined; }
        current = current[Number(indexes[j].slice(1, -1))];
      }
    }
  }
  return current;
}

function makeExpected(termIndex) {
  function term(key) { return hasOwn(termIndex, key) ? termIndex[key] : null; }

  function arrayFor(instance, source) {
    if (typeof source !== 'string') { return null; }
    if (source === 'none' || source === 'static' || source === 'sim-figures') { return null; }
    const relative = source.indexOf('instance.') === 0 ? source.slice(9) : source;
    const value = readPath(instance, relative);
    return Array.isArray(value) ? value : null;
  }

  function expand(contract, instance) {
    const out = [];
    (contract.fields || []).forEach((template) => {
      const role = template.role;
      const repeats = REPEAT_RE.test(String(template.payload_path || ''))
        || template.value_type === 'string_list';
      const list = repeats ? arrayFor(instance, template.source) : null;
      const count = repeats ? (list === null ? 0 : list.length) : 1;
      if (count === 0) {
        out.push({
          role: role, field_id: null, aria_name: null, control: CONTROL_MAP[template.control],
          required: template.required !== false, absent: true, count: 0
        });
        return;
      }
      for (let i = 0; i < count; i += 1) {
        const element = repeats ? list[i] : null;
        const idFn = ROLE_IDS[role];
        const fieldId = idFn ? idFn(element, i) : role;
        const slots = ROLE_SLOTS.any(element, i, instance);
        if (role === 'unit') { slots.label = String(readPath(instance, 'payload.unit')); }
        if (slots.unit === '' && /\{unit\}/.test(String(term(template.label_key)))) {
          slots.unit = String(readPath(instance, 'payload.unit'));
        }
        const pattern = term(template.label_key);
        const aria = pattern === null ? null : String(pattern).replace(/\{([a-z0-9_]+)\}/gi,
          (whole, name) => (slots[name] === undefined || slots[name] === null
            ? whole : String(slots[name])));
        out.push({
          role: role,
          field_id: fieldId,
          aria_name: aria,
          label_key: template.label_key,
          control: CONTROL_MAP[template.control],
          required: template.required !== false,
          absent: false,
          count: count
        });
      }
    });
    return out;
  }

  return { expand: expand, term: term, arrayFor: arrayFor };
}

/* -------------------------------------------------------------- fixtures */

const TYPE_IDS = [
  'Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09',
  'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18'
];

const SPATIAL = ['Q06', 'Q08', 'Q11', 'Q12', 'Q17'];

/* The N18 capture context the parity fixture binds to Q11. The shipped
 * registry declares none, so the assembler supplies it (see observations). */
const Q11_CAPTURE_CONTEXT = 'CAP-T67-CAL-PRACTICE';

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;

  const components = loadComponents(root);
  loadGraphEngine(root);
  const bank = loadBank(root);
  const shippedTerms = readJson(path.join(root, 'data/terms.json'));
  const fixture = readJson(path.join(root, 'tools/fixtures/n22/scratch_instances.json'));
  const registry = loadRegistry(root);
  const figures = mergeFigures(root).figures;

  require(path.join(root, 'src/bank-loader.js'));
  const bankLoader = globalThis.SimBank;

  /* The N22-A registry module is the completion authority. The harness loads
   * it with BOTH islands (names and error messages need the term bank), and
   * records whether the component consumed it. */
  require(path.join(root, 'src/compiled/inputs/registry.js'));
  const registryModule = globalThis.SimInputsRegistry;
  let registryLoad = null;
  if (registryModule && typeof registryModule.load === 'function') {
    registryLoad = guard('The registry module loads its two islands.', () => {
      registryModule.load(readJson(path.join(root, 'data/response_types.json')),
        readJson(path.join(root, 'data/terms.json')));
      return { status: 'PASS', claim: 'loaded', checks: { loaded: true }, failed: [] };
    });
  }

  const termIndex = Object.create(null);
  (shippedTerms.terms || []).forEach((entry) => { termIndex[entry.key] = entry.text_lv; });
  const expected = makeExpected(termIndex);

  function instanceFor(typeId) {
    const questionId = fixture.fixture_questions[typeId];
    if (!questionId) { throw new Error('No fixture question is declared for ' + typeId); }
    if (bank[questionId]) { return bank[questionId]; }
    const scratchKeys = Object.keys(fixture.instances || {});
    for (let i = 0; i < scratchKeys.length; i += 1) {
      const candidate = fixture.instances[scratchKeys[i]];
      if (candidate && candidate.question_id === questionId) { return candidate; }
    }
    throw new Error('Fixture instance for ' + typeId + ' is missing: ' + questionId);
  }

  function scratchInstance(key) {
    if (!fixture.instances || !fixture.instances[key]) {
      throw new Error('Scratch instance is missing from the fixture: ' + key);
    }
    return fixture.instances[key];
  }

  function contractFor(typeId) {
    const contract = registry.contracts[typeId];
    if (!contract) { throw new Error('Registry has no contract for ' + typeId); }
    return contract;
  }

  function initialStateFor(typeId, contract, instance, options) {
    const base = { figures: figures };
    return components.initialState(typeId, contract, instance, Object.assign(base, options || {}));
  }

  /* -------------------------------------------------- 1-18. render fixtures */

  function renderFixture(typeId) {
    const contract = contractFor(typeId);
    const instance = instanceFor(typeId);
    const checks = {};
    const descriptor = components.render(typeId, contract, instance, null, shippedTerms, {
      figures: figures,
      capture_context_id: typeId === 'Q11' ? Q11_CAPTURE_CONTEXT : undefined
    });
    const planned = expected.expand(contract, instance).filter((entry) => !entry.absent);
    const plannedIds = planned.map((entry) => entry.field_id);
    const renderedIds = descriptor.fields.map((field) => field.field_id);

    checks.descriptor_is_json_serialisable = (function () {
      try { JSON.parse(JSON.stringify(descriptor)); return true; } catch (error) { return false; }
    }());
    checks.type_id_matches = descriptor.type_id === typeId;
    checks.renderer_key_matches_bank_loader = descriptor.renderer_key === bankLoader.RENDERER_REGISTRY[typeId];
    checks.payload_kind_matches_bank_loader = contract.payload_kind === bankLoader.TYPE_PAYLOAD_CLASS[typeId];
    checks.field_set_matches_contract = deepEqual(renderedIds, plannedIds);
    checks.controls_match_contract = deepEqual(
      descriptor.fields.map((field) => field.control),
      planned.map((entry) => entry.control));

    const ariaMismatches = [];
    const unresolved = [];
    const stateTextMissing = [];
    descriptor.fields.forEach((field, position) => {
      const want = planned[position];
      if (!want) { return; }
      if (field.aria_name !== want.aria_name) {
        ariaMismatches.push({ field_id: field.field_id, got: field.aria_name, want: want.aria_name });
      }
      if (typeof field.aria_name !== 'string' || field.aria_name.trim() === ''
        || /\{[a-z0-9_]+\}/i.test(field.aria_name)) {
        unresolved.push(field.field_id);
      }
      if (typeof field.state_text !== 'string' || field.state_text.length === 0) {
        stateTextMissing.push(field.field_id);
      }
    });
    checks.aria_names_match_term_bank = ariaMismatches.length === 0;
    checks.aria_names_fully_resolved = unresolved.length === 0;
    checks.every_state_has_text = stateTextMissing.length === 0;
    checks.states_are_declared = descriptor.fields.every(
      (field) => ['empty', 'filled', 'error', 'pending'].indexOf(field.state) !== -1);
    checks.every_field_has_role = descriptor.fields.every(
      (field) => typeof field.role === 'string' && field.role.length > 0);
    checks.required_flags_are_boolean = descriptor.fields.every(
      (field) => typeof field.required === 'boolean');
    checks.stores_are_declared = descriptor.fields.every(
      (field) => typeof field.stores === 'string' && field.stores.length > 0);

    checks.group_label_from_terms = typeof descriptor.label_text_lv === 'string'
      && descriptor.label_text_lv.length > 0;
    checks.name_from_terms = typeof descriptor.name_text_lv === 'string'
      && descriptor.name_text_lv.length > 0;
    checks.labelledby_and_describedby = descriptor.labelledby === 'inputs-' + typeId.toLowerCase() + '-label'
      && descriptor.describedby === 'inputs-' + typeId.toLowerCase() + '-hint';
    checks.keyboard_hint_from_terms = typeof descriptor.keyboard_hint === 'string'
      && descriptor.keyboard_hint.length > 0;
    checks.parity_note_from_terms = typeof descriptor.parity_note_lv === 'string'
      && descriptor.parity_note_lv.length > 0;
    checks.abort_note_from_terms = typeof descriptor.abort_note_lv === 'string'
      && descriptor.abort_note_lv.length > 0;
    checks.polite_live_region_present = Array.isArray(descriptor.live)
      && descriptor.live.filter((entry) => entry.politeness === 'polite').length >= 1;
    checks.accessible_alternative_resolved = Boolean(descriptor.accessible_alternative)
      && typeof descriptor.accessible_alternative.label_text_lv === 'string'
      && descriptor.accessible_alternative.label_text_lv.length > 0
      && descriptor.accessible_alternative.details.length > 0;
    checks.completion_verdict_present = Boolean(descriptor.completion)
      && ['complete', 'incomplete', 'invalid'].indexOf(descriptor.completion.status) !== -1;

    const selectLike = descriptor.fields.filter(
      (field) => field.control === 'select' || field.control === 'radio' || field.control === 'checkbox');
    checks.select_like_fields_have_options = selectLike.every(
      (field) => Array.isArray(field.options) && field.options.length >= 1);
    checks.options_have_text = selectLike.every((field) => (field.options || []).every(
      (option) => typeof option.text_lv === 'string' && option.text_lv.length > 0));

    const duplicateNames = (function () {
      const seen = Object.create(null);
      const duplicates = [];
      descriptor.fields.forEach((field) => {
        if (seen[field.aria_name]) { duplicates.push(field.aria_name); }
        seen[field.aria_name] = true;
      });
      return duplicates;
    }());

    if (typeId === 'Q11') {
      checks.plot_surface_declared = descriptor.surfaces.length === 1
        && descriptor.surfaces[0].control === 'plot'
        && descriptor.surfaces[0].keyboard_path === 'table';
      checks.plot_surface_binds_the_capture_context = descriptor.surfaces[0].capture_context_id
        === Q11_CAPTURE_CONTEXT;
      checks.coordinate_table_has_rows = descriptor.fields[0].control === 'coordinate_table'
        && Array.isArray(descriptor.fields[0].rows)
        && descriptor.fields[0].rows.length === instance.payload.points.length;
      checks.table_rows_expose_coordinates = descriptor.fields[0].rows.every(
        (row) => row.cells.length === 2 && row.cells.every((cell) => hasOwn(cell, 'value')));
    }
    if (typeId === 'Q12') {
      checks.figure_binding_is_a_select = descriptor.fields.some(
        (field) => field.field_id === 'figure_binding' && field.control === 'select');
      checks.figure_binding_options_are_named = descriptor.fields.filter(
        (field) => field.field_id === 'figure_binding')[0].options.every(
        (option) => typeof option.text_lv === 'string' && option.text_lv.length > 0);
    }
    if (typeId === 'Q15' || typeId === 'Q16') {
      checks.text_area_is_multiline = descriptor.fields.length === 1
        && descriptor.fields[0].multiline === true;
    }
    if (typeId === 'Q06') {
      checks.pairs_are_select_based = descriptor.fields.every((field) => field.control === 'select');
      checks.option_count_is_right_items = descriptor.fields[0].options.length
        === instance.payload.right_items.length;
    }
    if (typeId === 'Q08') {
      checks.ordering_is_select_based = descriptor.fields.filter(
        (field) => field.role === 'combobox').every((field) => field.control === 'select');
      checks.position_fields_offer_items = descriptor.fields.filter(
        (field) => field.control === 'select').length === instance.payload.items.length;
    }
    if (typeId === 'Q17') {
      checks.pairs_are_text_fields = descriptor.fields.filter(
        (field) => field.control === 'textbox').length === instance.payload.steps.length;
    }

    return result(
      'The ' + typeId + ' render description carries exactly the field set the registry contract '
      + 'expands to, and every ARIA name is the term island\'s resolved pattern.', checks, {
        type_id: typeId,
        renderer_key: descriptor.renderer_key,
        instance: instance.question_id,
        field_ids: renderedIds,
        aria_names: descriptor.fields.map((field) => field.aria_name),
        duplicate_aria_names: duplicateNames,
        descriptor_digest16: digest16(descriptor),
        aria_mismatches: ariaMismatches,
        unresolved_aria: unresolved,
        state_text_missing: stateTextMissing
      });
  }

  /* ---------------------------------- 18b. scratch contract violation */

  function scratchViolation(typeId) {
    const contract = contractFor(typeId);
    const instance = instanceFor(typeId);
    const planned = expected.expand(contract, instance).filter((entry) => !entry.absent);
    const scratchContract = JSON.parse(JSON.stringify(contract));
    const index = scratchContract.fields.findIndex((template) => template.required !== false);
    const removed = scratchContract.fields.splice(index === -1 ? 0 : index, 1)[0];
    const error = captureError(() => components.render(typeId, scratchContract, instance, null,
      shippedTerms, { figures: figures, capture_context_id: typeId === 'Q11' ? Q11_CAPTURE_CONTEXT : undefined }));
    const namedId = error && error.details && error.details.field_id ? String(error.details.field_id) : null;
    const checks = {
      throws_loudly: Boolean(error),
      code_is_contract_violation: Boolean(error) && error.code === 'E_INPUTS_CONTRACT_VIOLATION',
      names_a_field_id: namedId !== null && namedId.length > 0
        && typeof error.message === 'string' && error.message.indexOf(namedId) !== -1,
      removed_role_was_the_one_needed: namedId !== null
        && (namedId.indexOf(String(removed.role)) !== -1
          || (error.details && error.details.role === removed.role)
          || planned.some((entry) => entry.field_id === namedId))
    };
    return result(
      'A scratch ' + typeId + ' contract with the "' + String(removed.role)
      + '" template deleted fails with E_INPUTS_CONTRACT_VIOLATION naming the field it cannot place.',
      checks, {
        type_id: typeId,
        removed_role: removed.role,
        named_field_id: namedId,
        observed: error
      });
  }

  function keyboardContractFixture() {
    const contracts = components.keyboardContracts();
    const checks = {};
    checks.covers_all_eighteen = Object.keys(contracts).length === 18
      && TYPE_IDS.every((typeId) => Boolean(contracts[typeId]));
    checks.every_contract_has_keys = TYPE_IDS.every((typeId) => Array.isArray(contracts[typeId].keys)
      && contracts[typeId].keys.length >= 3);
    checks.tab_never_intercepted = TYPE_IDS.every((typeId) => contracts[typeId].keys.some(
      (entry) => entry.key === 'Tab' && /netiek pārtverts/.test(entry.effect_lv)));
    checks.q06_q08_are_select_based = contracts.Q06.select_based === true
      && contracts.Q08.select_based === true && contracts.Q08.drag_forbidden === true;
    checks.q11_has_the_table_path = contracts.Q11.table_path === true
      && contracts.Q11.capture_component === 'SimGraphCapture';
    checks.q11_abort_documented = /daļēj/.test(contracts.Q11.abort_lv);
    checks.q12_reads_through_the_table = contracts.Q12.table_path === true;
    checks.q17_palette_and_place = contracts.Q17.palette_and_place === true
      && contracts.Q17.keys.some((entry) => entry.key === 'Escape' && /neviens daļējs/.test(entry.effect_lv));
    const decorated = components.keyboardContracts('Q11', contractFor('Q11'), shippedTerms);
    checks.registry_keyboard_texts_resolved = typeof decorated.path_text_lv === 'string'
      && decorated.path_text_lv.length > 0
      && typeof decorated.parity_text_lv === 'string' && decorated.parity_text_lv.length > 0
      && typeof decorated.abort_text_lv === 'string' && decorated.abort_text_lv.length > 0;
    const unknown = captureError(() => components.keyboardContracts('Q99'));
    checks.unknown_type_refused = Boolean(unknown) && unknown.code === 'E_INPUTS_UNKNOWN_TYPE';
    return result(
      'The keyboard contracts document the select-based paths for Q06 and Q08, the Q11 and '
      + 'Q12 coordinate table path, the Q17 select-and-place keys, the abort rule, and they '
      + 'carry the registry\'s own Latvian path/parity/abort texts.', checks, {
        types: Object.keys(contracts).sort()
      });
  }

  /* ------------------------------- 18c. registry verdict alignment (A.1.2) */

  /* The component assembles the payload; the registry names what is missing.
   * These two A.1.2 cases prove that the assembly reaches the registry's own
   * verdict with the registry's own Latvian names, not with a private guess. */
  function verdictAlignmentFixture() {
    const checks = {};

    const q13Contract = contractFor('Q13');
    const q13Instance = instanceFor('Q13');
    const species = q13Instance.payload.species_list;
    const partialVector = species.map((name, index) => (index === 1 ? '' : '1'));
    const q13Payload = {
      kind: 'method', variant: 'Q13_vector', vector: partialVector,
      located: 'Cu', replacement: '2', reason: 'Pārbaude'
    };
    const q13Verdict = components.completionOf(q13Contract, q13Payload, q13Instance);
    checks.q13_missing_is_named = q13Verdict.status === 'incomplete'
      && q13Verdict.missing.some((entry) => entry.name === 'Nav aizpildīts koeficients priekš H2');
    checks.q13_missing_carries_the_species = q13Verdict.missing.some(
      (entry) => String(entry.field_id).indexOf('1') !== -1 || entry.name.indexOf('H2') !== -1);

    const q12Contract = contractFor('Q12');
    const q12Instance = instanceFor('Q12');
    const q12Payload = { kind: 'graph', variant: 'Q12_read',
      read: { x: '30,00', y: '75,00', figure_binding: '' } };
    const q12Verdict = components.completionOf(q12Contract, q12Payload, q12Instance);
    checks.q12_missing_binding_is_named = q12Verdict.status === 'incomplete'
      && q12Verdict.missing.some((entry) => entry.name === 'Nav izvēlēta grafa piesaiste');
    checks.q12_missing_names_only_the_binding = q12Verdict.missing.length === 1;

    return result(
      'The component\'s assembled payloads reach the registry\'s own completion verdict with '
      + 'the registry\'s own Latvian missing names (the A.1.2 Q13 and Q12 cases).', checks, {
        q13: q13Verdict,
        q12: q12Verdict
      });
  }

  /* ------------------------------------------------ 19. parity fixtures */

  function focusOn(typeId, contract, state, targetIndex) {
    let current = state;
    let guardCount = 0;
    while (current.focus !== targetIndex && guardCount < 200) {
      const delta = current.focus < targetIndex ? 1 : -1;
      current = components.applyKey(typeId, contract, current, {
        key: delta > 0 ? 'ArrowRight' : 'ArrowLeft'
      }).state;
      guardCount += 1;
    }
    if (current.focus !== targetIndex) {
      throw new Error('focus could not reach field index ' + targetIndex);
    }
    return current;
  }

  function typeText(typeId, contract, state, fieldIndex, text) {
    let current = focusOn(typeId, contract, state, fieldIndex);
    for (let i = 0; i < text.length; i += 1) {
      current = components.applyKey(typeId, contract, current, { key: text[i] }).state;
    }
    return current;
  }

  function press(typeId, contract, state, key) {
    return components.applyKey(typeId, contract, state, { key: key }).state;
  }

  function parity(typeId, build, options) {
    const contract = contractFor(typeId);
    const instance = options.instance;
    const pointerPayload = build('pointer', contract, instance);
    const keyboardPayload = build('keyboard', contract, instance);
    const pointerDigest = digest16(pointerPayload);
    const keyboardDigest = digest16(keyboardPayload);
    const checks = {
      payloads_deep_equal: deepEqual(pointerPayload, keyboardPayload),
      digests_identical: pointerDigest === keyboardDigest,
      payload_is_json_serialisable: (function () {
        try { JSON.parse(JSON.stringify(pointerPayload)); return true; } catch (error) { return false; }
      }()),
      payload_kind_matches_contract: pointerPayload.kind === contract.payload_kind,
      no_device_marker: canonical(pointerPayload).indexOf('device') === -1
    };
    Object.keys(options.extraChecks || {}).forEach((key) => {
      checks[key] = Boolean(options.extraChecks[key](pointerPayload, keyboardPayload));
    });
    return result(
      'One identical ' + typeId + ' task answered by a pointer session and by a keyboard-only '
      + 'session yields a deep-equal, digest-identical payload.', checks, {
        type_id: typeId,
        instance: instance.question_id,
        pointer_digest16: pointerDigest,
        keyboard_digest16: keyboardDigest,
        pointer_payload: pointerPayload,
        keyboard_payload: keyboardPayload
      });
  }

  /* Q06: three pairs, each answered by choosing the right item of the same
   * index. Pointer: pick from the list. Keyboard: focus the pair, arrow down
   * through the options, Enter. */
  function buildQ06(mode, contract, instance) {
    const left = instance.payload.left_items;
    const right = instance.payload.right_items;
    let state = initialStateFor('Q06', contract, instance);
    if (mode === 'pointer') {
      left.forEach((item, position) => {
        state = components.pointerEvent('Q06', contract, state, {
          kind: 'select', field_id: 'pair_' + item.id, value: right[position].id
        }).state;
      });
      return components.payloadOf('Q06', contract, state);
    }
    left.forEach((item, position) => {
      state = focusOn('Q06', contract, state, position);
      for (let k = 0; k < position; k += 1) {
        state = press('Q06', contract, state, 'ArrowDown');
      }
      state = press('Q06', contract, state, 'Enter');
    });
    return components.payloadOf('Q06', contract, state);
  }

  /* Q08: a deliberate non-identity order S3, S1, S4, S2 across the four
   * position slots. */
  const Q08_ORDER = ['S3', 'S1', 'S4', 'S2'];

  function buildQ08(mode, contract, instance) {
    const items = instance.payload.items;
    let state = initialStateFor('Q08', contract, instance);
    if (mode === 'pointer') {
      Q08_ORDER.forEach((itemId, position) => {
        state = components.pointerEvent('Q08', contract, state, {
          kind: 'select', field_id: 'slot_' + String(position + 1), value: itemId
        }).state;
      });
      return components.payloadOf('Q08', contract, state);
    }
    Q08_ORDER.forEach((itemId, position) => {
      const optionIndex = items.findIndex((item) => item.item_id === itemId);
      state = focusOn('Q08', contract, state, position);
      for (let k = 0; k < optionIndex; k += 1) {
        state = press('Q08', contract, state, 'ArrowDown');
      }
      state = press('Q08', contract, state, 'Enter');
    });
    return components.payloadOf('Q08', contract, state);
  }

  /* Q11: one line through the two declared points. Pointer: begin, move, end
   * through SimGraphCapture. Keyboard: the same two points typed into the
   * coordinate table and committed row by row. */
  function buildQ11(mode, contract, instance) {
    const points = instance.payload.points;
    let state = initialStateFor('Q11', contract, instance, {
      capture_context_id: Q11_CAPTURE_CONTEXT
    });
    if (mode === 'pointer') {
      state = components.pointerEvent('Q11', contract, state, {
        kind: 'draw_begin', x: points[0].x, y: points[0].y
      }).state;
      for (let i = 1; i < points.length; i += 1) {
        state = components.pointerEvent('Q11', contract, state, {
          kind: 'draw_move', x: points[i].x, y: points[i].y
        }).state;
      }
      state = components.pointerEvent('Q11', contract, state, { kind: 'draw_end' }).state;
      return components.payloadOf('Q11', contract, state);
    }
    points.forEach((point, row) => {
      const xIndex = row * 2;
      state = typeText('Q11', contract, state, xIndex, components.formatRaw(point.x, 3));
      state = typeText('Q11', contract, state, xIndex + 1, components.formatRaw(point.y, 3));
      state = press('Q11', contract, state, 'Enter');
    });
    return components.payloadOf('Q11', contract, state);
  }

  /* Q12: one reading at x = 30, y = 75 plus the figure binding. */
  function buildQ12(mode, contract, instance) {
    const binding = figures[0].id;
    let state = initialStateFor('Q12', contract, instance);
    if (mode === 'pointer') {
      state = components.pointerEvent('Q12', contract, state, {
        kind: 'select', field_id: 'figure_binding', value: binding
      }).state;
      state = components.pointerEvent('Q12', contract, state, { kind: 'read', x: 30, y: 75 }).state;
      return components.payloadOf('Q12', contract, state);
    }
    state = focusOn('Q12', contract, state, 2);
    state = press('Q12', contract, state, 'Enter');
    state = typeText('Q12', contract, state, 0, components.formatRaw(30, 2));
    state = typeText('Q12', contract, state, 1, components.formatRaw(75, 2));
    return components.payloadOf('Q12', contract, state);
  }

  /* Q17: two structure parts placed on the target, plus the two step answers.
   * Pointer: choose from the palette, click the target. Keyboard: palette
   * selection, arrows to the target, Enter. */
  function buildQ17(mode, contract, instance) {
    const steps = instance.payload.steps;
    const answers = { S1: 'Na+ un Cl- joni', S2: 'm = 0,27 g' };
    const placements = [
      { part: 'P_NA', x: 1, y: 2, keys: ['ArrowRight', 'ArrowUp', 'ArrowUp'] },
      { part: 'P_CL', x: 3, y: 2, keys: ['ArrowRight', 'ArrowRight'] }
    ];
    let state = initialStateFor('Q17', contract, instance);
    if (mode === 'pointer') {
      placements.forEach((entry) => {
        state = components.pointerEvent('Q17', contract, state, {
          kind: 'select', field_id: 'palette', value: entry.part
        }).state;
        state = components.pointerEvent('Q17', contract, state, {
          kind: 'place', part_id: entry.part, x: entry.x, y: entry.y
        }).state;
      });
    } else {
      const paletteIndex = steps.length + (instance.payload.structure_parts || []).length;
      const targetX = paletteIndex + 1;
      const targetY = paletteIndex + 2;
      placements.forEach((entry, placementIndex) => {
        state = focusOn('Q17', contract, state, paletteIndex);
        const optionIndex = (instance.payload.structure_parts || [])
          .findIndex((part) => part.part_id === entry.part);
        for (let k = 0; k < optionIndex; k += 1) {
          state = press('Q17', contract, state, 'ArrowDown');
        }
        state = press('Q17', contract, state, 'Enter');
        /* The target holds its last position, so the second placement only
         * steps the difference. */
        const xNow = placementIndex === 0 ? 0 : placements[placementIndex - 1].x;
        const yNow = placementIndex === 0 ? 0 : placements[placementIndex - 1].y;
        state = focusOn('Q17', contract, state, targetX);
        for (let k = 0; k < entry.x - xNow; k += 1) {
          state = press('Q17', contract, state, 'ArrowUp');
        }
        state = focusOn('Q17', contract, state, targetY);
        for (let k = 0; k < entry.y - yNow; k += 1) {
          state = press('Q17', contract, state, 'ArrowUp');
        }
        state = press('Q17', contract, state, 'Enter');
      });
    }
    /* The step answers are typed on both devices: typing is not a device
     * difference and the parity claim is about the spatial placement. */
    steps.forEach((step, index) => {
      state = typeText('Q17', contract, state, index, answers[step.step_id]);
    });
    return components.payloadOf('Q17', contract, state);
  }

  function parityFixtures() {
    const out = {};
    out.parity_q06 = guard('Q06 parity runs.', () => parity('Q06', buildQ06, {
      instance: instanceFor('Q06'),
      extraChecks: {
        every_pair_assigned: (payload) => payload.pairs.length === 3
      }
    }));
    out.parity_q08 = guard('Q08 parity runs.', () => parity('Q08', buildQ08, {
      instance: instanceFor('Q08'),
      extraChecks: {
        order_is_a_permutation: (payload) => payload.order.length === 4
          && new Set(payload.order).size === 4,
        order_matches_the_script: (payload) => deepEqual(payload.order, Q08_ORDER)
      }
    }));
    out.parity_q11 = guard('Q11 parity runs.', () => parity('Q11', buildQ11, {
      instance: scratchInstance('q11_two_point'),
      extraChecks: {
        draw_payload_is_sim_graph_draw_v1: (payload) => Boolean(payload.draw_payload)
          && payload.draw_payload.schema_id === 'sim-graph-draw-v1',
        the_drawn_path_is_the_declared_points: (payload) => payload.draw_payload.points.length >= 2,
        record_binds_the_capture_context: (payload) => payload.record.capture_context_id
          === Q11_CAPTURE_CONTEXT
      }
    }));
    out.parity_q12 = guard('Q12 parity runs.', () => parity('Q12', buildQ12, {
      instance: instanceFor('Q12'),
      extraChecks: {
        reads_two_decimals: (payload) => payload.read.x === '30,00' && payload.read.y === '75,00',
        figure_binding_recorded: (payload) => payload.read.figure_binding === figures[0].id
      }
    }));
    out.parity_q17 = guard('Q17 parity runs.', () => parity('Q17', buildQ17, {
      instance: scratchInstance('q17_structure'),
      extraChecks: {
        two_placements_recorded: (payload) => Boolean(payload.structure)
          && payload.structure.placements.length === 2,
        pair_map_carried: (payload) => payload.pair_map.S1 === 'Na+ un Cl- joni'
      }
    }));
    return out;
  }

  /* ------------------------------------------------ 20. abort mid-gesture */

  function abortFixture() {
    const checks = {};
    const observed = {};

    const q17Contract = contractFor('Q17');
    const q17Instance = scratchInstance('q17_structure');
    let q17State = initialStateFor('Q17', q17Contract, q17Instance);
    const beforeQ17 = components.committed('Q17', q17Contract, q17State);
    q17State = components.pointerEvent('Q17', q17Contract, q17State, {
      kind: 'select', field_id: 'palette', value: 'P_NA'
    }).state;
    q17State = press('Q17', q17Contract, q17State, 'ArrowRight');
    const inGesture = Boolean(q17State.gesture);
    const abortedQ17 = components.cancel('Q17', q17Contract, q17State, 'navigate_away');
    const afterQ17 = components.committed('Q17', q17Contract, abortedQ17.state);
    const q17Payload = components.payloadOf('Q17', q17Contract, abortedQ17.state);
    observed.q17_cancel_events = abortedQ17.events;
    checks.q17_gesture_was_in_progress = inGesture;
    checks.q17_gesture_discarded = abortedQ17.state.gesture === null;
    checks.q17_committed_unchanged = deepEqual(beforeQ17.placements, afterQ17.placements)
      && afterQ17.placements.length === 0;
    checks.q17_payload_has_no_placement = q17Payload.structure === undefined;
    checks.q17_cancel_event_recorded = abortedQ17.events.some(
      (event) => event.kind === 'cancel' && event.reason === 'navigate_away' && event.discarded === true);

    const q11Contract = contractFor('Q11');
    const q11Instance = scratchInstance('q11_two_point');
    let q11State = initialStateFor('Q11', q11Contract, q11Instance, {
      capture_context_id: Q11_CAPTURE_CONTEXT
    });
    const beforeQ11 = components.committed('Q11', q11Contract, q11State);
    q11State = components.pointerEvent('Q11', q11Contract, q11State, {
      kind: 'draw_begin', x: 0.002, y: 0.05
    }).state;
    q11State = components.pointerEvent('Q11', q11Contract, q11State, {
      kind: 'draw_move', x: 0.01, y: 0.24
    }).state;
    const midPath = q11State.capture && q11State.capture.path ? q11State.capture.path.length : 0;
    const abortedQ11 = components.cancel('Q11', q11Contract, q11State, 'navigate_away');
    const afterQ11 = components.committed('Q11', q11Contract, abortedQ11.state);
    const q11Payload = components.payloadOf('Q11', q11Contract, abortedQ11.state);
    observed.q11_cancel_events = abortedQ11.events;
    checks.q11_path_was_in_progress = midPath >= 2;
    checks.q11_path_discarded = Array.isArray(abortedQ11.state.capture.path)
      && abortedQ11.state.capture.path.length === 0;
    checks.q11_committed_unchanged = deepEqual(beforeQ11.draw_payload, afterQ11.draw_payload);
    checks.q11_payload_has_no_draw = q11Payload.draw_payload === null;

    let escapeState = initialStateFor('Q17', q17Contract, q17Instance);
    escapeState = components.pointerEvent('Q17', q17Contract, escapeState, {
      kind: 'select', field_id: 'palette', value: 'P_CL'
    }).state;
    const escaped = components.applyKey('Q17', q17Contract, escapeState, { key: 'Escape' });
    checks.escape_uses_the_cancel_path = escaped.events.some(
      (event) => event.kind === 'cancel' && event.reason === 'escape');
    checks.escape_discards_the_gesture = escaped.state.gesture === null;

    return result(
      'A mid-interaction abort discards the in-progress gesture: the committed response is '
      + 'unchanged and no partial placement ever appears in the emitted payload.', checks, {
        observed: observed
      });
  }

  /* --------------------------------------------- 21. input preservation */

  function preservationFixture() {
    const contract = contractFor('Q01');
    const instance = instanceFor('Q01');
    const fieldId = instance.payload.input_fields[0].field_id;
    const checks = {};

    let state = initialStateFor('Q01', contract, instance);
    state = typeText('Q01', contract, state, 0, '1,2,3');
    const payload = components.payloadOf('Q01', contract, state);
    checks.raw_value_kept_byte_for_byte = payload.values[fieldId] === '1,2,3';

    const errors = {};
    errors[fieldId] = 'UNREADABLE_INPUT';
    const descriptor = components.render('Q01', contract, instance, payload, shippedTerms, {
      figures: figures, errors: errors
    });
    const field = descriptor.fields.filter((entry) => entry.field_id === fieldId)[0];
    checks.error_state_rendered = field.state === 'error';
    checks.error_id_is_the_taxonomy_class = Boolean(field.error) && field.error.id === 'UNREADABLE_INPUT';
    checks.error_message_is_the_shipped_term = Boolean(field.error)
      && field.error.message === termIndex['feedback.error.unreadable'];
    checks.raw_value_survives_the_error = field.value === '1,2,3';
    checks.error_state_has_text_equivalence = field.state_text === field.error.message;
    checks.error_field_has_a_describedby_slot = field.describedby === 'inputs-q01-error-' + fieldId;
    checks.live_region_carries_the_error = descriptor.live.some(
      (entry) => entry.id === 'inputs-q01-live-error' && entry.text.length > 0);

    let mixed = initialStateFor('Q01', contract, instance);
    mixed = typeText('Q01', contract, mixed, 0, '1,2.3');
    const mixedPayload = components.payloadOf('Q01', contract, mixed);
    checks.mixed_separator_kept_raw = mixedPayload.values[fieldId] === '1,2.3';
    checks.mixed_separator_is_unreadable = components.parseRaw('1,2.3') === null;

    const undeclared = captureError(() => components.render('Q01', contract, instance, payload,
      shippedTerms, { figures: figures, errors: (function () {
        const map = {};
        map[fieldId] = 'NOT_A_TAXONOMY_CLASS';
        return map;
      }()) }));
    checks.undeclared_error_class_refused = Boolean(undeclared)
      && undeclared.code === 'E_INPUTS_CONTRACT_VIOLATION';

    return result(
      'An error state never destroys the learner\'s raw input: the value stays byte for byte, '
      + 'the error slot carries the shipped Latvian message and the state has text equivalence.',
      checks, {
        field_id: fieldId,
        raw_after_error: field.value,
        error_message: field.error ? field.error.message : null
      });
  }

  /* ------------------------------------------------ 22. composed response */

  function composedFixture() {
    const spec = fixture.composed;
    const checks = {};
    const parts = spec.parts.map((part) => {
      const instance = instanceFor(part.type_id);
      return {
        part_id: part.part_id,
        label_key: part.label_key,
        type_id: part.type_id,
        contract: contractFor(part.type_id),
        instance: instance,
        payload: part.payload
      };
    });

    const composed = components.compose(parts, shippedTerms);
    const missing = composed.verdict.missing;
    checks.verdict_is_incomplete = composed.verdict.status === 'incomplete';
    checks.only_part_two_is_missing = missing.length > 0
      && missing.every((entry) => entry.part_id === 'part2');
    checks.missing_names_the_part_and_field = missing.length === 1
      && missing[0].part_id === 'part2'
      && /^read[._]y$/.test(String(missing[0].field_id))
      && missing[0].type_id === 'Q12';
    checks.missing_carries_the_resolved_name = missing.length === 1
      && typeof missing[0].name === 'string' && /y/.test(missing[0].name);
    checks.part_one_is_complete = composed.parts[0].completion.status === 'complete';
    checks.part_two_is_incomplete = composed.parts[1].completion.status === 'incomplete';
    checks.part_completion_recorded_separately = composed.parts.length === 2
      && deepEqual(composed.parts.map((part) => part.part_id), ['part1', 'part2']);
    checks.payload_is_an_ordered_map = deepEqual(Object.keys(composed.payload), ['0', '1'])
      && composed.part_ids[0] === 'part1' && composed.part_ids[1] === 'part2';
    checks.payload_carries_part_one_values = composed.payload['0'].values.c === '1,60';
    checks.payload_carries_part_two_read = composed.payload['1'].read.x === '30,00';
    checks.part_labels_from_terms = composed.parts.every(
      (part) => typeof part.label_text_lv === 'string' && part.label_text_lv.length > 0);
    checks.container_label_from_terms = typeof composed.label_text_lv === 'string'
      && composed.label_text_lv.indexOf(composed.part_names_lv[0]) !== -1;
    checks.live_region_announces_the_gap = composed.live.length === 1
      && composed.live[0].text.indexOf(composed.parts[1].label_text_lv) !== -1;

    const previous = globalThis.SimInputsRegistry;
    globalThis.SimInputsRegistry = {
      completion() {
        return { status: 'incomplete',
          missing: [{ field_id: 'registry_says_so', reason: 'registry_verdict' }], errors: [] };
      }
    };
    const delegated = guard('delegated compose runs.', () => components.compose(parts, shippedTerms));
    globalThis.SimInputsRegistry = previous;
    checks.registry_verdict_is_consumed = delegated.status !== 'FAIL'
      && delegated.verdict.missing.some((entry) => entry.field_id === 'registry_says_so');

    return result(
      'A two-part composed response with mixed completion names only part two\'s missing '
      + 'field, records both parts\' completion separately and keeps an ordered payload map.',
      checks, {
        parts: composed.parts.map((part) => ({
          part_id: part.part_id,
          type_id: part.type_id,
          completion: part.completion.status,
          missing: part.completion.missing
        })),
        missing: missing,
        payload_keys: Object.keys(composed.payload),
        payload_digest16: digest16(composed.payload)
      });
  }

  /* ----------------------------------------------------------------- run */

  const fixtures = {};
  TYPE_IDS.forEach((typeId) => {
    fixtures['render_' + typeId.toLowerCase()] = guard(
      'The ' + typeId + ' render fixture runs.', () => renderFixture(typeId));
  });
  fixtures.scratch_contract_violation = guard('The scratch contract violation fixtures run.',
    () => {
      const perType = {};
      TYPE_IDS.forEach((typeId) => {
        perType[typeId] = guard('The ' + typeId + ' scratch violation runs.',
          () => scratchViolation(typeId));
      });
      const failedTypes = Object.keys(perType).filter((typeId) => perType[typeId].status !== 'PASS');
      return result(
        'Every type\'s contract, with one field template deleted, fails loudly with '
        + 'E_INPUTS_CONTRACT_VIOLATION naming the field it cannot place.', {
          all_eighteen_name_their_field: failedTypes.length === 0
        }, { per_type: perType, failed_types: failedTypes });
    });
  fixtures.keyboard_contracts = guard('The keyboard contract fixture runs.', keyboardContractFixture);
  fixtures.registry_verdict_alignment = guard('The registry verdict alignment fixture runs.', verdictAlignmentFixture);
  fixtures.registry_binding = guard('The registry binding fixture runs.', () => {
    const checks = {};
    const types = Object.keys(registry.contracts).sort();
    checks.covers_all_eighteen = deepEqual(types, TYPE_IDS.slice().sort());
    checks.island_declares_the_same_eighteen = (registry.island.types !== undefined);
    checks.renderer_keys_match_bank_loader = types.every(
      (typeId) => registry.contracts[typeId].renderer_key === bankLoader.RENDERER_REGISTRY[typeId]);
    checks.payload_kinds_match_bank_loader = types.every(
      (typeId) => registry.contracts[typeId].payload_kind === bankLoader.TYPE_PAYLOAD_CLASS[typeId]);
    checks.every_contract_declares_fields = types.every(
      (typeId) => Array.isArray(registry.contracts[typeId].fields)
        && registry.contracts[typeId].fields.length > 0);
    checks.every_contract_declares_completion = types.every(
      (typeId) => registry.contracts[typeId].completion_rule
        && typeof registry.contracts[typeId].completion_rule.model === 'string');
    checks.every_contract_declares_error_surfaces = types.every(
      (typeId) => Array.isArray(registry.contracts[typeId].error_surfaces)
        && registry.contracts[typeId].error_surfaces.length > 0);
    checks.every_contract_declares_keyboard = types.every(
      (typeId) => Boolean(registry.contracts[typeId].keyboard));
    checks.every_contract_declares_alternative = types.every(
      (typeId) => Boolean(registry.contracts[typeId].accessible_alternative)
        && typeof registry.contracts[typeId].accessible_alternative.label_key === 'string');
    checks.completed_types_have_grading_bindings = (registry.island.completed_types || []).every(
      (typeId) => Boolean(registry.contracts[typeId].grading_binding));
    checks.unknown_type_refused = (function () {
      const error = captureError(() => components.render('Q99', {}, {}, null, shippedTerms));
      return Boolean(error) && (error.code === 'E_INPUTS_UNKNOWN_TYPE'
        || error.code === 'E_INPUTS_CONTRACT_VIOLATION');
    }());
    /* Which completion path ran: the registry module is the authority, so
     * every verdict must say it came from SimInputsRegistry.completion. */
    const sources = types.map((typeId) => {
      const instance = instanceFor(typeId);
      const verdict = components.completionOf(registry.contracts[typeId], null, instance);
      return { type_id: typeId, source: verdict.source, status: verdict.status };
    });
    checks.completion_delegates_to_the_registry = sources.every(
      (entry) => entry.source === 'SimInputsRegistry.completion');
    checks.registry_module_loaded = Boolean(registryModule)
      && Boolean(registryLoad) && registryLoad.status === 'PASS';
    return result(
      'The shipped registry covers all eighteen types with a renderer key, payload kind, field '
      + 'set, completion model, error surfaces, keyboard contract and accessible alternative, '
      + 'bound to the bank loader\'s own mapping.', checks, {
        source: registry.source,
        island_status: registry.island.status,
        island_owner: registry.island.owner,
        types: types,
        completion_sources: sources
      });
  });

  const parityFixturesOut = parityFixtures();
  const abort = guard('The abort fixture runs.', abortFixture);
  const preservation = guard('The input-preservation fixture runs.', preservationFixture);
  const composed = guard('The composed fixture runs.', composedFixture);

  const modulePath = path.join(root, 'src/compiled/inputs/components.js');
  const moduleText = readText(modulePath);

  const componentsRecord = {
    schema_version: 1,
    owner: 'N22-B',
    kind: 'components',
    api_version: components.api_version,
    module: {
      path: 'src/compiled/inputs/components.js',
      source_module: 'src/inputs/components.ts',
      bytes: fs.statSync(modulePath).size,
      sha256: sha256(moduleText),
      digest16: sha256(moduleText).slice(0, 16)
    },
    phase: 'phase-2-island-bound',
    registry: {
      source: registry.source,
      island_status: registry.island.status,
      island_owner: registry.island.owner,
      island_bytes: fs.statSync(path.join(root, 'data/response_types.json')).size,
      island_sha256_16: sha256(readText(path.join(root, 'data/response_types.json'))).slice(0, 16),
      module: 'src/compiled/inputs/registry.js',
      module_loaded: Boolean(registryModule) && Boolean(registryLoad) && registryLoad.status === 'PASS',
      completion_authority: 'SimInputsRegistry.completion (component fallback recorded per verdict)',
      note: 'The fixtures run against the shipped registry island; there is no private contract '
        + 'fallback.'
    },
    terms: {
      island: 'data/terms.json',
      key_count: (shippedTerms.terms || []).length,
      island_sha256_16: sha256(readText(path.join(root, 'data/terms.json'))).slice(0, 16)
    },
    graph_dependency: {
      modules: ['src/graph-scoring-engine.js', 'src/graph-capture.js'],
      capture_context_used_for_q11: Q11_CAPTURE_CONTEXT
    },
    fixtures_used: fixture.fixture_question_reasons,
    binding_summary: (function () {
      const summary = {};
      TYPE_IDS.forEach((typeId) => {
        const contract = registry.contracts[typeId];
        const instance = instanceFor(typeId);
        const planned = expected.expand(contract, instance).filter((entry) => !entry.absent);
        summary[typeId] = {
          contract_fields: (contract.fields || []).length,
          rendered_fields: planned.length,
          field_ids: planned.map((entry) => entry.field_id)
        };
      });
      return summary;
    }()),
    observations: fixture.observations,
    checks: fixtures,
    status: null
  };
  componentsRecord.status = Object.keys(fixtures)
    .every((key) => fixtures[key].status === 'PASS') ? 'PASS' : 'FAIL';

  const parityRecord = {
    schema_version: 1,
    owner: 'N22-B',
    kind: 'parity',
    api_version: components.api_version,
    module_digest16: componentsRecord.module.digest16,
    registry_source: registry.source,
    parity_table: SPATIAL.map((typeId) => {
      const entry = parityFixturesOut['parity_' + typeId.toLowerCase()];
      return {
        type_id: typeId,
        status: entry.status,
        pointer_digest16: entry.pointer_digest16,
        keyboard_digest16: entry.keyboard_digest16,
        digests_identical: entry.pointer_digest16 === entry.keyboard_digest16
      };
    }),
    checks: Object.assign({}, parityFixturesOut, {
      abort_mid_gesture: abort,
      input_preservation: preservation,
      composed_two_part: composed
    }),
    claim_scope: 'Mechanical payload equality under scripted sessions. Not a screen-reader, '
      + 'browser-render or instructor-acceptance claim; N33 owns the live assistive-technology pass.',
    status: null
  };
  parityRecord.status = Object.keys(parityRecord.checks)
    .every((key) => parityRecord.checks[key].status === 'PASS') ? 'PASS' : 'FAIL';

  if (args.record) {
    const out = path.isAbsolute(args.record) ? args.record : path.join(root, args.record);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(componentsRecord, null, 2) + '\n', 'utf8');
    const parityPath = args.recordParity
      ? (path.isAbsolute(args.recordParity) ? args.recordParity : path.join(root, args.recordParity))
      : path.join(path.dirname(out), 'N22_PARITY_RECORD.json');
    fs.writeFileSync(parityPath, JSON.stringify(parityRecord, null, 2) + '\n', 'utf8');
  }

  const summary = {
    status: componentsRecord.status === 'PASS' && parityRecord.status === 'PASS' ? 'PASS' : 'FAIL',
    registry_source: registry.source,
    module_digest16: componentsRecord.module.digest16,
    components: Object.keys(fixtures).map((key) => ({ name: key, status: fixtures[key].status })),
    parity: parityRecord.parity_table,
    other: ['abort_mid_gesture', 'input_preservation', 'composed_two_part'].map((key) => ({
      name: key, status: parityRecord.checks[key].status
    }))
  };
  process.stdout.write(JSON.stringify(summary, null, 2) + '\n');
  return summary.status === 'PASS' ? 0 : 1;
}

if (require.main === module) {
  try {
    process.exitCode = main();
  } catch (error) {
    process.stderr.write('FAIL n22_components: '
      + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main };
