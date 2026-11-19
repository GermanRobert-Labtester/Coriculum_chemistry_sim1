#!/usr/bin/env node
/* N19 runtime harness. Loads the shipped islands from output/simulator.html and
 * the method modules from src/method-engine.js and src/method-card-view.js (both
 * are intentionally not inlined into the executable script: the Section 1.3
 * runtime-JS ceiling has 83 bytes of headroom; see
 * evidence/N19_VERIFICATION_RECORD.md).
 *
 * Proves: 10/10 N05 method-type vectors verdict for verdict, 17/17 S4-N19
 * stratum vectors, the determinism digests, the signature mapping with zero
 * dangling entries, one full feedback trace (a transposed pair producing both
 * signatures' strings), the self-assessment pending boundary, the card focus
 * traces and the in-harness smoke vector.
 * Not a browser render or accessibility acceptance claim.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');
const ISLAND_IDS = ['sim-terms', 'sim-golden-vectors', 'sim-method-cards', 'sim-method-engine'];
const MODULES = ['src/method-engine.js', 'src/method-card-view.js'];

function sha256(text) { return require('crypto').createHash('sha256').update(text, 'utf8').digest('hex'); }
function assert(cond, msg) { if (!cond) throw new Error('Assertion failed: ' + msg); }

/* Order-insensitive comparison with fixed-decimal numbers, so the JavaScript
 * and the Python twin agree byte for byte. */
function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return value.toFixed(6); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  const keys = Object.keys(value).sort();
  return '{' + keys.map(function (key) { return JSON.stringify(key) + ':' + canonical(value[key]); }).join(',') + '}';
}

/* ------------------------------------------------------------- minimal DOM */
function makeDom() {
  const registry = Object.create(null);
  function makeNode(tag) {
    const node = {
      tagName: String(tag).toUpperCase(),
      className: '',
      textContent: '',
      hidden: false,
      attributes: {},
      children: [],
      parentNode: null,
      listeners: {},
      appendChild(child) { child.parentNode = this; this.children.push(child); return child; },
      removeChild(child) {
        const index = this.children.indexOf(child);
        if (index >= 0) { this.children.splice(index, 1); child.parentNode = null; }
        return child;
      },
      get firstChild() { return this.children.length ? this.children[0] : null; },
      setAttribute(name, value) { this.attributes[name] = String(value); },
      getAttribute(name) { return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null; },
      addEventListener(type, handler) {
        if (!this.listeners[type]) { this.listeners[type] = []; }
        this.listeners[type].push(handler);
      },
      dispatch(type) {
        (this.listeners[type] || []).forEach(function (handler) { handler({ type: type }); });
      },
      focus() { this.focused = true; },
      descendants() {
        const out = [];
        const walk = (node) => {
          node.children.forEach(function (child) { out.push(child); walk(child); });
        };
        walk(this);
        return out;
      },
      querySelectorAll(selector) {
        const cls = selector.replace(/^\./, '');
        return this.descendants().filter(function (node) {
          return String(node.className).split(/\s+/).indexOf(cls) !== -1;
        });
      }
    };
    let elementId = '';
    Object.defineProperty(node, 'id', {
      get: function () { return elementId; },
      set: function (value) {
        elementId = String(value);
        if (elementId) { registry[elementId] = node; }
      }
    });
    return node;
  }
  const document = {
    createElement: makeNode,
    getElementById: function (id) { return registry[id] || null; },
    register: function (id, node) { registry[id] = node; return node; },
    registry: registry,
    activeElement: null
  };
  return document;
}

function extractIslands(html) {
  const islands = Object.create(null);
  ISLAND_IDS.forEach(function (id) {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)<\\/script>');
    const match = re.exec(html);
    if (!match) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = match[1].replace(/<\\\//g, '</');
  });
  return islands;
}

function makeSandbox(doc) {
  const sandbox = {
    console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
    RegExp, isFinite, parseInt, parseFloat, Date, Map, Set, unescape, encodeURIComponent,
    escape, decodeURIComponent, atob: function (text) { return Buffer.from(text, 'base64').toString('binary'); }
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  MODULES.forEach(function (relative) {
    vm.runInContext(fs.readFileSync(path.join(ROOT, relative), 'utf8'), sandbox, { filename: relative });
  });
  return sandbox;
}

/* ------------------------------------------------------------------- run */
function runOnce(islands, registerSmoke) {
  const doc = makeDom();
  ISLAND_IDS.forEach(function (id) { doc.register(id, { id: id, textContent: islands[id] }); });
  const sandbox = makeSandbox(doc);
  const M = sandbox.SimMethodEngine;
  const Cards = sandbox.SimMethodCards;
  assert(M && typeof M.MethodEngine === 'function', 'SimMethodEngine did not load');
  assert(Cards && typeof Cards.mountCard === 'function', 'SimMethodCards did not load');

  const contract = JSON.parse(islands['sim-method-engine']);
  const cardsIsland = JSON.parse(islands['sim-method-cards']);
  const terms = JSON.parse(islands['sim-terms']);
  const golden = JSON.parse(islands['sim-golden-vectors']);
  const engine = new M.MethodEngine(contract, terms);
  const cardsById = {};
  cardsIsland.cards.forEach(function (card) { cardsById[card.card_id] = card; });
  /* The shipped island carries the sealed diagnostics; a runtime consumer
   * unseals the card when it needs the signature, the note or the rules. */
  const unsealedCards = Cards.unsealCards(cardsById);

  // -- the N05 method-type vectors -----------------------------------------
  const n05Rows = [];
  golden.vectors.filter(function (v) { return v.status !== 'retired' && ['ordering', 'matching', 'method'].indexOf(v.instance.payload_class) !== -1; })
    .forEach(function (vector) {
      const record = engine.gradeInstance(vector.instance, vector.submission);
      const view = engine.oracleView(record);
      const keys = ['verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
        'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points'];
      const ok = keys.every(function (key) { return canonical(view[key]) === canonical(vector.expected[key]); });
      n05Rows.push({
        id: vector.vector_id, type_id: vector.instance.type_id, case_kind: vector.case_kind,
        verdict_class: view.verdict_class, error_class: view.error_class,
        signatures: record.diagnostics.signatures || [],
        status: ok ? 'PASS' : 'FAIL'
      });
      if (!ok) throw new Error('N05 method vector mismatch ' + vector.vector_id);
    });

  // -- the S4-N19 stratum ---------------------------------------------------
  const vectors = contract.method_vectors;
  const allVectors = []
    .concat(vectors.ordering_vectors || [])
    .concat(vectors.matching_vectors || [])
    .concat(vectors.sequence_vectors || [])
    .concat(vectors.self_assessment_vectors || []);
  if (vectors.scratch && vectors.scratch.ordering) { allVectors.push(vectors.scratch.ordering); }
  const stratumRows = [];
  const determinismRows = [];
  allVectors.forEach(function (vector) {
    const spec = M.specForVector(unsealedCards, vector);
    const record = engine.grade(spec, vector.submission);
    const again = engine.grade(spec, vector.submission);
    const diagnostics = record.diagnostics;
    const got = {
      verdict_class: record.verdict_class, error_class: record.error_class,
      signatures: diagnostics.signatures || []
    };
    if (spec.kind === 'ordering') { got.wrong_positions = diagnostics.wrong_positions; }
    if (spec.kind === 'matching') { got.pair_statuses = diagnostics.pair_statuses; }
    if (spec.kind === 'sequence') { got.status = (diagnostics.per_step || [{}])[0].status; }
    if (spec.kind === 'self_assessment') { got.pending_points = record.pending_points; }
    const differences = {};
    Object.keys(vector.expected).forEach(function (key) {
      if (canonical(vector.expected[key]) !== canonical(got[key])) {
        differences[key] = { expected: vector.expected[key], actual: got[key] };
      }
    });
    stratumRows.push({
      id: vector.id, kind: spec.kind, card_id: vector.card_id,
      status: Object.keys(differences).length ? 'FAIL' : 'PASS', differences: differences
    });
    const digest = sha256(canonical(record));
    const digestAgain = sha256(canonical(again));
    determinismRows.push({
      id: vector.id, digest: digest, stable: digest === digestAgain,
      status: digest === digestAgain ? 'PASS' : 'FAIL'
    });
    if (Object.keys(differences).length) throw new Error('N19 stratum vector mismatch ' + vector.id);
    if (digest !== digestAgain) throw new Error('N19 vector is not deterministic ' + vector.id);
  });

  // -- signature mapping: the whole registry, zero dangling --------------------
  // The sweep covers every registry entry, not only the signatures that the
  // vectors happen to exercise: a registry entry that no vector reaches is
  // still a dangling reference if its feedback does not resolve.
  const registry = {};
  contract.signature_registry.forEach(function (entry) { registry[entry.signature] = entry; });
  const goldenSignatures = {};
  golden.vectors.forEach(function (vector) {
    (vector.instance.misconception_signatures || []).forEach(function (signature) {
      goldenSignatures[signature] = true;
    });
  });
  const usedSignatures = {};
  allVectors.forEach(function (vector) {
    const spec = M.specForVector(unsealedCards, vector);
    const record = engine.grade(spec, vector.submission);
    (record.diagnostics.signatures || []).forEach(function (signature) { usedSignatures[signature] = true; });
  });
  /* The signatures the cards themselves declare, over every card. The shipped
   * island carries the sealed projection, so the sweep reads the unsealed
   * cards: the signatures are the answer key and are sealed until the card
   * is opened. */
  const cardSignatures = {};
  Object.keys(unsealedCards).forEach(function (cardId) {
    const card = unsealedCards[cardId];
    (card.steps || []).forEach(function (step) {
      if (step.misconception_signature) { cardSignatures[step.misconception_signature] = true; }
    });
    (card.sequence_prompts || []).forEach(function (prompt) {
      (prompt.distractors || []).forEach(function (distractor) {
        if (distractor.misconception_signature) { cardSignatures[distractor.misconception_signature] = true; }
      });
    });
    ((card.matching || {}).correct_pairs || []).forEach(function (pair) {
      if (pair.misconception_signature) { cardSignatures[pair.misconception_signature] = true; }
    });
  });
  const allSignatures = Object.keys(registry).concat(
    Object.keys(cardSignatures), Object.keys(usedSignatures)
  ).filter(function (value, index, list) { return list.indexOf(value) === index; }).sort();
  const mappingRows = [];
  allSignatures.forEach(function (signature) {
    const entry = registry[signature];
    const feedbackKey = entry ? entry.feedback_key : null;
    const term = feedbackKey ? terms.terms.filter(function (t) { return t.key === feedbackKey; })[0] : null;
    const feedbackResolved = Boolean(term && term.text_lv && term.text_lv.trim());
    const problems = [];
    if (!entry) { problems.push('not in the signature registry'); }
    if (!goldenSignatures[signature]) { problems.push('not present in the frozen N05 corpus'); }
    if (!feedbackResolved) { problems.push('feedback key does not resolve in #sim-terms'); }
    mappingRows.push({
      signature: signature, in_registry: Boolean(entry),
      in_golden_corpus: Boolean(goldenSignatures[signature]),
      feedback_key: feedbackKey, feedback_resolved: feedbackResolved,
      feedback_text: term ? term.text_lv : '',
      provenance: entry ? entry.provenance : null,
      declared_by_card: Boolean(cardSignatures[signature]),
      used_by_vector: Boolean(usedSignatures[signature]),
      problems: problems,
      status: problems.length ? 'DANGLING' : 'RESOLVED'
    });
  });
  /* Every card signature must reach the registry and every registry entry must
   * be reachable from a card: no orphaned entry, no undeclared signature. */
  const registryWithoutCard = mappingRows.filter(function (row) {
    return row.in_registry && !row.declared_by_card;
  });
  const cardWithoutRegistry = mappingRows.filter(function (row) {
    return row.declared_by_card && !row.in_registry;
  });
  assert(registryWithoutCard.length === 0,
    'registry entries without a card: ' + registryWithoutCard.map(function (r) { return r.signature; }).join(', '));
  assert(cardWithoutRegistry.length === 0,
    'card signatures without a registry entry: ' + cardWithoutRegistry.map(function (r) { return r.signature; }).join(', '));

  // -- the feedback trace: a transposed pair produces both signatures' strings
  const cardMc03 = unsealedCards['MC-EX03'];
  const orderSpec = M.specForVector(unsealedCards, {
    id: 'TRACE', card_id: 'MC-EX03', spec_source: 'card',
    spec: {
      kind: 'ordering', item_ids: cardMc03.steps.map(function (s) { return s.step_id; }),
      correct_order: cardMc03.steps.map(function (s) { return s.step_id; }),
      free_groups: [], rubric: [{ criterion_id: 'C1_ORDER', grading: 'auto', engine_binding: 'N19-method', points: 2.0 }]
    }
  });
  const stepIds = cardMc03.steps.map(function (s) { return s.step_id; });
  const transposed = stepIds.slice();
  transposed[1] = stepIds[2];
  transposed[2] = stepIds[1];
  const traceRecord = engine.grade(orderSpec, { order: transposed });
  const diagnosed = traceRecord.diagnostics.per_step.filter(function (s) {
    return s.status === 'misplaced' || s.status === 'unknown_step' || s.status === 'missing_step';
  });
  const feedbackTrace = {
    card_id: 'MC-EX03',
    submission: transposed,
    wrong_positions: traceRecord.diagnostics.wrong_positions,
    signatures: traceRecord.diagnostics.signatures,
    /* The per-step signature assignments of the transposed pair. The card's
     * family shares one signature across its steps, so the aggregate list
     * collapses to one entry while the diagnosis still names both steps. */
    per_step_signatures: diagnosed.map(function (s) {
      return { position: s.position, step_id: s.step_id, signature: s.misconception_signature };
    }),
    steps: diagnosed.map(function (s) {
      return {
        position: s.position, step_id: s.step_id, expected_step_id: s.expected_step_id,
        status: s.status, misconception_signature: s.misconception_signature,
        misconception_note_lv: s.misconception_note_lv, feedback_key: s.feedback_key,
        feedback_text: s.feedback_text
      };
    }),
    remediation: traceRecord.diagnostics.remediation
  };
  assert(feedbackTrace.wrong_positions.length === 2, 'the transposed pair must mark both positions');
  assert(feedbackTrace.per_step_signatures.length === 2,
    'the transposed pair must return a signature for each of the two steps');
  assert(feedbackTrace.per_step_signatures.every(function (s) { return s.signature; }),
    'every transposed step must carry its signature');
  assert(feedbackTrace.signatures.length === 1 && feedbackTrace.signatures[0] === 'MC-2C-01',
    'the transposed pair must return the card signature');
  assert(feedbackTrace.steps.length === 2, 'the transposed pair must produce two diagnosed steps');
  assert(feedbackTrace.steps.every(function (s) { return s.misconception_note_lv && s.feedback_text; }),
    'every diagnosed step must carry a note and a resolved feedback string');
  assert(feedbackTrace.steps[0].misconception_note_lv !== feedbackTrace.steps[1].misconception_note_lv,
    'the two transposed steps must carry their own distinct notes');

  // -- the self-assessment boundary -------------------------------------------
  const boundarySpec = {
    kind: 'self_assessment', engine: 'N19-self',
    rubric: [{ criterion_id: 'C1_SELF', grading: 'self', engine_binding: 'self-assessed', points: 2.0 }],
    default_signature: null
  };
  const pendingRecord = engine.grade(boundarySpec, { text: 'Gala tilpumu nosaka atzīme, tāpēc ūdens porciju neizmēra.' });
  const blankRecord = engine.grade(boundarySpec, { text: '   ' });
  const boundary = {
    pending: {
      verdict_class: pendingRecord.verdict_class, error_class: pendingRecord.error_class,
      pending_points: pendingRecord.pending_points, max_points: pendingRecord.max_points,
      signatures: pendingRecord.diagnostics.signatures, text_parsed: pendingRecord.diagnostics.text_parsed,
      status: pendingRecord.verdict_class === 'pending_self_assessment' && pendingRecord.diagnostics.signatures.length === 0
        && pendingRecord.diagnostics.text_parsed === false ? 'PASS' : 'FAIL'
    },
    blank: {
      verdict_class: blankRecord.verdict_class, error_class: blankRecord.error_class,
      pending_points: blankRecord.pending_points,
      status: blankRecord.verdict_class === 'incorrect' && blankRecord.error_class === 'BLANK_RESPONSE'
        && blankRecord.pending_points === 0 ? 'PASS' : 'FAIL'
    }
  };
  assert(boundary.pending.status === 'PASS', 'the pending boundary failed');
  assert(boundary.blank.status === 'PASS', 'the blank boundary failed');

  // -- the card focus traces -------------------------------------------------
  const loaded = Cards.load(doc);
  const host = doc.createElement('div');
  doc.register('method-card-host', host);
  const trigger = doc.createElement('button');
  trigger.id = 'map-btn-P2-07';
  doc.register('map-btn-P2-07', trigger);
  const mounts = Cards.mountOutcomeSlot(doc, host, 'P2-07', trigger, loaded);
  const focusTraces = mounts.map(function (mount) {
    return {
      card_id: mount.cardId,
      heading_focused: Boolean(mount.heading && mount.heading.focused),
      trigger_id: mount.trigger ? mount.trigger.id : null,
      steps: mount.card.steps.length,
      revealed_count: Object.keys(mount.revealed).length
    };
  });
  assert(mounts.length > 0, 'the outcome slot mounted no card');
  assert(focusTraces.every(function (t) { return t.heading_focused; }),
    'the card heading must take focus when the card opens');
  const firstMount = mounts[0];
  const revealed = Cards.revealStep(doc, firstMount.id, firstMount.card.steps[0].step_id);
  assert(revealed.reasoning_lv, 'the revealed step must carry its reasoning');
  assert(revealed.misconception_signature, 'the revealed step must carry its signature');
  const noteNode = doc.getElementById(firstMount.id + '-note-' + firstMount.card.steps[0].step_id);
  assert(noteNode && noteNode.hidden === false, 'the revealed note must become visible');
  const remediationNote = Cards.stepNote('MC-EX03', firstMount.card.steps[0].step_id, loaded);
  assert(remediationNote && remediationNote.note_lv, 'the remediation path must resolve the step note');

  // -- the smoke vector -------------------------------------------------------
  let smoke = null;
  if (registerSmoke) {
    const spec = {
      kind: 'ordering', engine: 'N19-ordering',
      item_ids: ['S1', 'S2', 'S3'], correct_order: ['S1', 'S2', 'S3'], free_groups: [],
      step_meta: {
        S1: { signature: 'MC-2C-01', note_lv: 'Pārbaudi krānu.', feedback_key: 'feedback.concept_link_label' },
        S2: { signature: 'MC-2C-01', note_lv: 'Noņem piltuvi.', feedback_key: 'feedback.concept_link_label' },
        S3: { signature: 'MC-2C-01', note_lv: 'Nolasi sākuma līmeni.', feedback_key: 'feedback.concept_link_label' }
      },
      default_signature: 'MC-2C-01',
      rubric: [{ criterion_id: 'C1_ORDER', grading: 'auto', engine_binding: 'N19-method', points: 2.0 }],
      source_ref: 'SMK-N19-METHOD-ORDERING'
    };
    const record = engine.grade(spec, { order: ['S1', 'S3', 'S2'] });
    const perStep = record.diagnostics.per_step.map(function (s) {
      return { position: s.position, step_id: s.step_id, status: s.status };
    });
    const ok = record.verdict_class === 'incorrect' && record.error_class === 'WRONG_ORDER' &&
      record.diagnostics.wrong_positions.length === 2 &&
      record.diagnostics.signatures.length === 1 && record.diagnostics.signatures[0] === 'MC-2C-01';
    smoke = {
      status: ok ? 'PASS' : 'FAIL',
      id: 'SMK-N19-METHOD-ORDERING',
      owner: 'N19',
      description: 'A fixed transposed ordering submission grades per-step: both slots are marked and the card signature is returned.',
      details: {
        verdict_class: record.verdict_class, error_class: record.error_class,
        wrong_positions: record.diagnostics.wrong_positions, per_step: perStep,
        signatures: record.diagnostics.signatures,
        digest: sha256(canonical(record))
      }
    };
    if (smoke.status !== 'PASS') throw new Error('the N19 smoke vector failed');
  }

  const verdictRecords = allVectors.map(function (vector) {
    const spec = M.specForVector(unsealedCards, vector);
    return { id: vector.id, record: engine.grade(spec, vector.submission) };
  });

  return {
    counts: {
      n05: n05Rows.length, stratum: stratumRows.length,
      signatures: mappingRows.length, cards: cardsIsland.cards.length
    },
    digests: {
      n05_verdicts: sha256(JSON.stringify(n05Rows)),
      stratum_verdicts: sha256(JSON.stringify(stratumRows)),
      determinism: sha256(JSON.stringify(determinismRows)),
      signature_mapping: sha256(JSON.stringify(mappingRows)),
      feedback_trace: sha256(canonical(feedbackTrace)),
      boundary: sha256(canonical(boundary)),
      focus: sha256(JSON.stringify(focusTraces)),
      verdict_records: sha256(JSON.stringify(verdictRecords)),
      contract: sha256(islands['sim-method-engine']),
      cards_island: sha256(islands['sim-method-cards']),
      engine_source: sha256(fs.readFileSync(path.join(ROOT, 'src/method-engine.js'), 'utf8')),
      card_view_source: sha256(fs.readFileSync(path.join(ROOT, 'src/method-card-view.js'), 'utf8'))
    },
    rows: { n05: n05Rows, stratum: stratumRows, determinism: determinismRows, mapping: mappingRows },
    feedback_trace: feedbackTrace,
    boundary: boundary,
    focus_traces: focusTraces,
    smoke: smoke,
    verdict_records: verdictRecords
  };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const islands = extractIslands(html);
  const first = runOnce(islands, true);
  const second = runOnce(islands, false);
  const parity = JSON.stringify(first.digests) === JSON.stringify(second.digests);
  const dangling = first.rows.mapping.filter(function (row) { return row.status !== 'RESOLVED'; });
  const report = {
    schema_version: 1, task: 'N19', status: parity && dangling.length === 0 ? 'PASS' : 'FAIL',
    artifact_sha256: sha256(html),
    runtime_js_note: 'The method verdict engine and the method card view are verified from src/method-engine.js and src/method-card-view.js against the shipped islands; neither is inlined into the artifact, because the runtime-JS ceiling headroom is 83 bytes (N31 owns the resolution).',
    counts: first.counts, digests: first.digests, parity: parity,
    rows: first.rows, feedback_trace: first.feedback_trace, boundary: first.boundary,
    focus_traces: first.focus_traces, smoke: first.smoke,
    smoke_summary: first.smoke ? {
      total: 1, passed: first.smoke.status === 'PASS' ? 1 : 0, failed: first.smoke.status === 'PASS' ? 0 : 1,
      vector: [first.smoke]
    } : { status: 'not-run' },
    verdict_records: first.verdict_records
  };
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exit(1);
}
main();
