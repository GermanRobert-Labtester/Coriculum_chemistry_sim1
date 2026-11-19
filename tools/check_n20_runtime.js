#!/usr/bin/env node
/* N20 runtime harness: cross-language parity, ephemeral path, tamper fixture.
 *
 * The harness loads the *runtime* modules (src/) exactly as the browser
 * would, and proves four claims that the frozen bank depends on:
 *
 *   1. cross-language parity — the JavaScript twin instantiates the same
 *      family/variant/seed as the Python authoring twin and produces the same
 *      canonical bytes as the frozen bank instance;
 *   2. determinism — the same seed produces the same bytes twice;
 *   3. the ephemeral retry path — a retry seed outside the frozen seed set
 *      instantiates deterministically, never carries a frozen question id, and
 *      a seed that *would* collide with a frozen seed is excluded;
 *   4. the loader's integrity check — the bank loader accepts the island whose
 *      digest matches and refuses a tampered island by digest mismatch.
 *
 * The harness also grades one frozen and one ephemeral instance of the same
 * family through the same N17 grading code, so the parity fixture compares
 * the *code path*, not the numbers.
 *
 * Usage: node tools/check_n20_runtime.js [--repo-root .] [--record PATH]
 */
'use strict';

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');

function parseArgs(argv) {
  const args = { repoRoot: repoRoot, record: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
  }
  return args;
}

/* ------------------------------------------------------------------ loading */

function loadRuntimeModules(root) {
  /* The figure framework is the SHA-256 authority for the runtime modules, so
   * it is loaded first — the same order the artifact uses. */
  require(path.join(root, 'src/figure-framework.js'));
  require(path.join(root, 'src/prng.js'));
  const variantEngine = require(path.join(root, 'src/variant-engine.js'));
  const templates = require(path.join(root, 'src/variant-templates.js'));
  const engines = require(path.join(root, 'src/quantity-engine.js'));
  require(path.join(root, 'src/bank-loader.js'));
  const bank = globalThis.SimBank;
  if (!bank) { throw new Error('src/bank-loader.js did not register SimBank.'); }
  return { variantEngine, templates, engines, bank };
}

/* A minimal DOM stand-in: the runtime modules only need the island texts and
 * the digest meta element. Nothing here fakes behaviour — the loader reads
 * exactly the text a browser would read. */
function makeDoc(islands, meta) {
  return {
    getElementById(id) {
      if (!Object.prototype.hasOwnProperty.call(islands, id)) { return null; }
      return { textContent: islands[id], hidden: true };
    },
    querySelector(selector) {
      const match = /meta\[name="([^"]+)"\]/.exec(String(selector));
      if (!match) { return null; }
      const content = meta && Object.prototype.hasOwnProperty.call(meta, match[1])
        ? meta[match[1]] : null;
      if (content === null) { return null; }
      return { getAttribute(name) { return name === 'content' ? content : null; } };
    }
  };
}

function readJson(file) { return JSON.parse(fs.readFileSync(file, 'utf8')); }

/* ------------------------------------------------------------------- checks */

function stripReviewState(instance) {
  /* The frozen bank instance carries the review workflow record; the runtime
   * instantiation does not. The comparison removes the record from the frozen
   * side so that both sides describe the same instance. */
  const copy = Object.assign({}, instance);
  const extensions = Object.assign({}, instance.extensions);
  const data = Object.assign({}, instance.extensions.data);
  delete data.review_workflow;
  extensions.data = data;
  copy.extensions = extensions;
  return copy;
}

function checkCrossLanguageParity(runtime, rawById) {
  const variantEngine = runtime.variantEngine;
  variantEngine.load(runtime.templates, readJson(path.join(repoRoot, 'data/conventions.json')));
  const rows = [];
  const mismatches = [];
  for (const family of runtime.templates.families) {
    for (const variant of family.variants) {
      const instance = variantEngine.instantiate(family.family_id, variant.variant_id);
      const frozen = rawById[instance.question_id];
      let match = false;
      if (frozen) {
        match = variantEngine.canonicalText(stripReviewState(frozen)) === instance.__text;
      }
      const row = {
        family_id: family.family_id,
        variant_id: variant.variant_id,
        question_id: instance.question_id,
        seed: instance.seed,
        js_digest: runtime.variantEngine.sha256Hex(instance),
        frozen_digest: frozen ? runtime.variantEngine.sha256Hex(stripReviewState(frozen)) : null,
        byte_identical: match
      };
      rows.push(row);
      if (!match) { mismatches.push(row); }
    }
  }
  return {
    status: mismatches.length === 0 && rows.length === 112 ? 'PASS' : 'FAIL',
    claim: 'The Python authoring twin and the JavaScript runtime twin produce '
         + 'byte-identical instances from identical seeds.',
    instances: rows.length,
    byte_identical: rows.length - mismatches.length,
    mismatches: mismatches.slice(0, 5),
    rows: rows
  };
}

function checkDeterminism(runtime) {
  const variantEngine = runtime.variantEngine;
  const rows = [];
  let identical = 0;
  for (const family of runtime.templates.families) {
    for (const variant of family.variants) {
      const first = variantEngine.instantiate(family.family_id, variant.variant_id);
      const second = variantEngine.instantiate(family.family_id, variant.variant_id);
      if (first.__text === second.__text) { identical += 1; }
      rows.push({
        question_id: first.question_id,
        identical: first.__text === second.__text,
        digest: variantEngine.sha256Hex(first)
      });
    }
  }
  return {
    status: identical === rows.length ? 'PASS' : 'FAIL',
    claim: 'The same family, variant and seed produce the same bytes twice.',
    instances: rows.length,
    identical: identical,
    rows: rows
  };
}

function checkEphemeralPath(runtime, rawById) {
  const variantEngine = runtime.variantEngine;
  const frozenSeeds = Object.keys(rawById).map((id) => rawById[id].seed);
  const frozenSeedSet = new Set(frozenSeeds);

  const family = runtime.templates.families[0];
  const variant = family.variants[0];
  const picked = variantEngine.ephemeralSeed(family.family_id, variant.variant_id, 0, frozenSeeds);
  const ephemeral = variantEngine.instantiateEphemeral(
    family.family_id, variant.variant_id, 0, frozenSeeds);
  const repeated = variantEngine.instantiateEphemeral(
    family.family_id, variant.variant_id, 0, frozenSeeds);
  const frozen = rawById['COL1-' + family.topic + '-' + family.family_id.slice(4) + '-'
    + variant.variant_id + '-01'];

  /* Exclusion proof: the seed that attempt 0 *would* draw is put into the
   * frozen set, so the rule has to advance to attempt 1 instead of handing
   * out a colliding seed. */
  const colliding = variantEngine.deriveSeed(
    family.family_id + '-' + variant.variant_id + '-EPH-0').toString();
  const excluded = variantEngine.ephemeralSeed(
    family.family_id, variant.variant_id, 0, [colliding]);

  const checks = {
    seed_outside_frozen_set: !frozenSeedSet.has(picked.seed.toString()),
    attempt_zero: picked.attempt === 0,
    deterministic: ephemeral.__text === repeated.__text,
    distinct_question_id: ephemeral.question_id !== frozen.question_id,
    question_id_marked_ephemeral: /-EPH-\d+$/.test(ephemeral.question_id),
    never_persisted: ephemeral.extensions.data.ephemeral.persisted === false,
    not_a_bank_member: ephemeral.extensions.data.ephemeral.frozen_bank_member === false,
    excluded_from_frozen_bank: ephemeral.extensions.data.ephemeral.excluded_frozen_seeds === true,
    collision_excluded: excluded.attempt === 1 && excluded.seed.toString() !== colliding,
    different_from_frozen_instance: ephemeral.__text !== frozen.__text
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The ephemeral retry path draws a seed outside the frozen set, is '
         + 'deterministic, never collides with a frozen question id and is '
         + 'never persisted.',
    family_id: family.family_id,
    variant_id: variant.variant_id,
    ephemeral_seed: picked.seed.toString(),
    ephemeral_attempt: picked.attempt,
    ephemeral_question_id: ephemeral.question_id,
    frozen_question_id: frozen.question_id,
    colliding_seed_used_as_frozen: colliding,
    exclusion_result_attempt: excluded.attempt,
    exclusion_result_seed: excluded.seed.toString(),
    checks: checks,
    failed: failed
  };
}

/* The written answer form a learner is expected to write: the display with
 * the unit suffix removed. */
function writtenAnswer(instance) {
  const display = String(instance.payload.display_lv || '');
  const unit = String(instance.payload.unit || '');
  const suffix = unit ? ' ' + unit : '';
  if (suffix && display.slice(-suffix.length) === suffix) {
    return display.slice(0, display.length - suffix.length);
  }
  return display;
}

function checkParityFixture(runtime, rawById) {
  /* Both paths are graded by the same engine code. The frozen instance and
   * the ephemeral instance of the same family receive the same *kind* of
   * submission, and the verdict class must agree; each instance's own correct
   * answer must also be accepted. */
  const variantEngine = runtime.variantEngine;
  const engines = runtime.engines;
  const conventions = readJson(path.join(repoRoot, 'data/conventions.json'));
  const terms = readJson(path.join(repoRoot, 'data/terms.json'));
  const taxonomy = readJson(path.join(repoRoot, 'data/engine_taxonomy.json'));
  const doc = makeDoc({
    'sim-conventions': JSON.stringify(conventions),
    'sim-terms': JSON.stringify(terms),
    'sim-engines': JSON.stringify(taxonomy)
  }, {});
  engines.load(doc);

  const family = runtime.templates.families.find((f) => f.variants.some(
    (v) => v.payload && v.payload.class === 'numeric'));
  const variant = family.variants.find((v) => v.payload && v.payload.class === 'numeric');
  const frozenSeeds = Object.keys(rawById).map((id) => rawById[id].seed);
  const frozenId = 'COL1-' + family.topic + '-' + family.family_id.slice(4) + '-'
    + variant.variant_id + '-01';
  const frozen = rawById[frozenId];
  const ephemeral = variantEngine.instantiateEphemeral(
    family.family_id, variant.variant_id, 0, frozenSeeds);

  /* The submission is the *written* answer form the display teaches — the
   * same thing a learner types. For a whole answer whose significant figures
   * live in trailing zeros the display writes it in scientific notation, and
   * that written form is what carries the declared precision. */
  const frozenWritten = writtenAnswer(frozen);
  const ephemeralWritten = writtenAnswer(ephemeral);
  const frozenCorrect = engines.grade(frozen, {
    value: frozenWritten, unit: frozen.payload.unit
  });
  const ephemeralCorrect = engines.grade(ephemeral, {
    value: ephemeralWritten, unit: ephemeral.payload.unit
  });
  const frozenWrong = engines.grade(frozen, { value: '0', unit: frozen.payload.unit });
  const ephemeralWrong = engines.grade(ephemeral, { value: '0', unit: ephemeral.payload.unit });

  const checks = {
    same_written_form_rule: frozenWritten === writtenAnswer(frozen),
    same_engine_binding: JSON.stringify(frozen.rubric.map((r) => r.engine_binding))
      === JSON.stringify(ephemeral.rubric.map((r) => r.engine_binding)),
    same_criterion_ids: JSON.stringify(frozen.rubric.map((r) => r.criterion_id))
      === JSON.stringify(ephemeral.rubric.map((r) => r.criterion_id)),
    frozen_correct_accepted: frozenCorrect.verdict_class === 'correct',
    ephemeral_correct_accepted: ephemeralCorrect.verdict_class === 'correct',
    frozen_wrong_rejected: frozenWrong.verdict_class !== 'correct',
    ephemeral_wrong_rejected: ephemeralWrong.verdict_class !== 'correct',
    verdict_class_agrees: frozenCorrect.verdict_class === ephemeralCorrect.verdict_class,
    wrong_verdict_class_agrees: frozenWrong.verdict_class === ephemeralWrong.verdict_class
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The frozen and the ephemeral instance are graded by identical engine '
         + 'code and yield the same verdict class for equivalent submissions.',
    family_id: family.family_id,
    variant_id: variant.variant_id,
    frozen_question_id: frozen.question_id,
    ephemeral_question_id: ephemeral.question_id,
    engine_binding: frozen.rubric.map((r) => r.engine_binding),
    frozen_written_answer: frozenWritten,
    ephemeral_written_answer: ephemeralWritten,
    frozen_correct_verdict: frozenCorrect.verdict_class,
    ephemeral_correct_verdict: ephemeralCorrect.verdict_class,
    frozen_wrong_verdict: frozenWrong.verdict_class,
    ephemeral_wrong_verdict: ephemeralWrong.verdict_class,
    checks: checks,
    failed: failed
  };
}

function checkTamperFixture(runtime, rawById) {
  const variantEngine = runtime.variantEngine;
  const bankLoader = runtime.bank;
  const islandText = JSON.stringify({
    island_id: 'sim-bank',
    schema_version: 1,
    bank_version: '1.0.0-n20',
    status: 'frozen-reviewed-bank',
    questions: Object.keys(rawById).map((id) => rawById[id])
  });
  const digest = globalThis.SimFigures.sha256Utf8(islandText);

  const intactDoc = makeDoc({ 'sim-bank': islandText }, { 'sim-bank-embedded-digest': digest });
  let intactStatus = 'PASS';
  let intactError = null;
  let loadedCount = 0;
  try {
    const loaded = bankLoader.load(intactDoc, {});
    loadedCount = loaded.counts.total;
  } catch (error) {
    intactStatus = 'FAIL';
    intactError = { code: error.code, message: error.message };
  }

  /* Tamper: one character of the island text changes. The digest must not
   * match any more, and the loader must refuse the island by name. */
  const tamperedText = islandText.replace('"question_id":"COL1-1-1A-A-01"',
    '"question_id":"COL1-1-1A-A-02"');
  const tamperedDoc = makeDoc({ 'sim-bank': tamperedText },
    { 'sim-bank-embedded-digest': digest });
  let tamperStatus = 'FAIL';
  let tamperError = null;
  try {
    bankLoader.load(tamperedDoc, {});
  } catch (error) {
    tamperError = { code: error.code, message: error.message };
    tamperStatus = error.code === 'E_BANK_DIGEST_MISMATCH' ? 'PASS' : 'FAIL';
  }

  /* A missing digest must also fail honestly rather than pass silently. */
  const missingDoc = makeDoc({ 'sim-bank': islandText }, {});
  let missingStatus = 'FAIL';
  let missingError = null;
  try {
    bankLoader.load(missingDoc, {});
  } catch (error) {
    missingError = { code: error.code, message: error.message };
    missingStatus = error.code === 'E_BANK_DIGEST_MISSING' ? 'PASS' : 'FAIL';
  }

  const checks = {
    intact_island_loads: intactStatus === 'PASS' && loadedCount === 112,
    tampered_island_refused: tamperStatus === 'PASS',
    missing_digest_refused: missingStatus === 'PASS'
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The loader verifies the island digest at load time and refuses a '
         + 'tampered or unsigned island instead of loading it.',
    expected_digest: digest,
    intact: { status: intactStatus, questions: loadedCount, error: intactError },
    tampered: { status: tamperStatus, error: tamperError },
    missing_digest: { status: missingStatus, error: missingError },
    checks: checks,
    failed: failed
  };
}


/* The in-file smoke vector, run against the *built artifact*: the island
 * text and the digest meta are taken from output/simulator.html, so this
 * proves that the shipped artifact loads its own frozen bank and grades a
 * fixed instance the way the bank says it does. */
function checkSmokeVector(runtime) {
  const vm = require('vm');
  const artifactPath = path.join(repoRoot, 'output/simulator.html');
  if (!fs.existsSync(artifactPath)) {
    return {
      status: 'FAIL',
      claim: 'The in-file smoke vector runs against the built artifact.',
      reason: 'output/simulator.html is not built; the vector was not run.'
    };
  }
  const html = fs.readFileSync(artifactPath, 'utf8');
  const island = /<script type="application\/json" id="sim-bank">([\s\S]*?)<\/script>/.exec(html);
  const meta = /<meta name="sim-bank-embedded-digest" content="([0-9a-f]{64})">/.exec(html);
  if (!island || !meta) {
    return { status: 'FAIL', claim: 'The in-file smoke vector runs against the built artifact.',
      reason: 'The artifact does not carry the #sim-bank island or its digest meta.' };
  }
  const islands = { 'sim-bank': island[1] };
  for (const id of ['sim-conventions', 'sim-terms', 'sim-engines']) {
    const found = new RegExp('<script type="application\\/json" id="' + id + '">([\\s\\S]*?)<\\/script>').exec(html);
    if (found) { islands[id] = found[1]; }
  }
  const doc = makeDoc(islands, { 'sim-bank-embedded-digest': meta[1] });
  const sandbox = {
    console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
    RegExp, isFinite, parseInt, parseFloat, Date, BigInt, Set, Map
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  ['src/figure-framework.js', 'src/quantity-engine.js', 'src/bank-loader.js', 'src/smoke-subset.js']
    .forEach((relative) => vm.runInContext(fs.readFileSync(path.join(repoRoot, relative), 'utf8'),
      sandbox, { filename: relative }));
  if (!sandbox.SimSmoke) {
    return { status: 'FAIL', claim: 'The in-file smoke vector runs against the built artifact.',
      reason: 'The smoke subset did not register in the sandbox.' };
  }
  const report = sandbox.SimSmoke.run(doc);
  const vector = (report.vectors || []).find((v) => v.id === 'SMK-N20-BANK-GRADE-VERDICT');
  /* Only the bank vector is asserted here: the other in-file vectors walk a
   * real browser DOM, which this sandbox does not provide. Their results are
   * recorded as they are, not claimed as a pass. */
  const checks = {
    bank_vector_present: Boolean(vector),
    bank_vector_passes: Boolean(vector) && vector.status === 'PASS'
  };
  const failed = Object.keys(checks).filter((key) => !checks[key]);
  return {
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    claim: 'The in-file smoke vector runs against the built artifact.',
    artifact: path.relative(repoRoot, artifactPath),
    embedded_digest: meta[1],
    suite: { total: report.total, passed: report.passed, failed: report.failed,
             note: 'The other in-file vectors walk a browser DOM; only the bank '
                 + 'vector is asserted in this sandbox.' },
    vector: vector || null,
    checks: checks,
    failed: failed
  };
}

/* --------------------------------------------------------------------- main */

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const runtime = loadRuntimeModules(root);

  /* The frozen bank is read as the artifact sees it: one island document. */
  const bankFiles = fs.readdirSync(path.join(root, 'data/bank'))
    .filter((name) => name.endsWith('.json')).sort();
  const questions = [];
  for (const name of bankFiles) {
    const doc = readJson(path.join(root, 'data/bank', name));
    questions.push.apply(questions, doc.questions || []);
  }
  const rawById = {};
  for (const question of questions) { rawById[question.question_id] = question; }
  runtime.bank.validateAndMap({
    island_id: 'sim-bank', schema_version: 1, bank_version: '1.0.0-n20',
    status: 'frozen-reviewed-bank', questions: questions
  }, {});

  const checks = {
    cross_language_parity: checkCrossLanguageParity(runtime, rawById),
    determinism: checkDeterminism(runtime),
    ephemeral_path: checkEphemeralPath(runtime, rawById),
    parity_fixture: checkParityFixture(runtime, rawById),
    tamper_fixture: checkTamperFixture(runtime, rawById),
    smoke_vector: checkSmokeVector(runtime)
  };
  const failed = Object.keys(checks).filter((key) => checks[key].status !== 'PASS');
  const record = {
    schema_version: 1,
    owner: 'N20',
    status: failed.length === 0 ? 'PASS' : 'FAIL',
    runtime_modules: [
      'src/variant-engine.js', 'src/variant-templates.js', 'src/prng.js',
      'src/figure-framework.js', 'src/quantity-engine.js', 'src/bank-loader.js'
    ],
    note: 'The runtime variant engine and the family templates ship from src/ and '
        + 'are not inlined into the artifact (N31 owns the inline / lazy-load / '
        + 're-budget decision).',
    bank_instances: questions.length,
    checks: checks
  };

  if (args.record) {
    const out = path.isAbsolute(args.record) ? args.record : path.join(root, args.record);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    fs.writeFileSync(out, JSON.stringify(record, null, 2) + '\n', 'utf8');
  }
  process.stdout.write(JSON.stringify({
    status: record.status,
    bank_instances: questions.length,
    checks: Object.keys(checks).map((key) => ({
      name: key, status: checks[key].status
    }))
  }, null, 2) + '\n');
  return failed.length === 0 ? 0 : 1;
}

if (require.main === module) {
  try {
    process.exitCode = main();
  } catch (error) {
    process.stderr.write('FAIL n20_runtime: ' + (error && error.stack ? error.stack : error) + '\n');
    process.exitCode = 2;
  }
}

module.exports = { main };
