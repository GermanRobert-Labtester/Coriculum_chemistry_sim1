#!/usr/bin/env node
/* N18 runtime harness. Loads the shipped islands from output/simulator.html and
 * the graph scoring module from src/graph-scoring-engine.js (the module is
 * intentionally not inlined into the executable script: the Section 1.3
 * runtime-JS ceiling has 83 bytes of headroom; see
 * evidence/N18_VERIFICATION_RECORD.md).
 *
 * Proves: 3/3 N05 reading vectors verdict for verdict, 14/14 S3-N18 stratum
 * vectors, 5/5 validity cases, 6/6 malformed-payload cases, the pointer and
 * keyboard parity matrix over the full vector set with digests, the verdict
 * replay proof, an in-file smoke vector and two-run parity.
 * Not a browser render or accessibility acceptance claim.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');
const ISLAND_IDS = ['sim-conventions', 'sim-figures', 'sim-golden-vectors', 'sim-graph-scoring'];
const MODULES = ['src/graph-scoring-engine.js', 'src/graph-capture.js'];

function sha256(text) { return require('crypto').createHash('sha256').update(text, 'utf8').digest('hex'); }
function assert(cond, msg) { if (!cond) throw new Error('Assertion failed: ' + msg); }

function extractIslands(html) {
  const islands = Object.create(null);
  ISLAND_IDS.forEach((id) => {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)<\\/script>');
    const match = re.exec(html);
    if (!match) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = match[1].replace(/<\\\//g, '</');
  });
  return islands;
}

function makeDocument(islands) {
  const nodes = Object.create(null);
  ISLAND_IDS.forEach((id) => { nodes[id] = { id: id, textContent: islands[id] }; });
  nodes['sim-graph-scoring-error'] = { id: 'sim-graph-scoring-error', textContent: '', hidden: true };
  nodes['sim-smoke-status'] = { id: 'sim-smoke-status', textContent: '', hidden: true };
  return { getElementById: (id) => nodes[id] || null };
}

function makeSandbox(doc) {
  const sandbox = {
    console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
    RegExp, isFinite, parseInt, parseFloat, Date, Map, Set, unescape, encodeURIComponent
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  MODULES.forEach((relative) => vm.runInContext(fs.readFileSync(path.join(ROOT, relative), 'utf8'), sandbox,
    { filename: relative }));
  return sandbox;
}

/* Order-insensitive comparison: the verdict record's key order is not part of
 * the contract, so the comparison uses sorted keys. */
function canonical(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return JSON.stringify(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) { return '[' + value.map(canonical).join(',') + ']'; }
  var keys = Object.keys(value).sort();
  return '{' + keys.map(function (key) { return JSON.stringify(key) + ':' + canonical(value[key]); }).join(',') + '}';
}

function rubricOf(vector) {
  if (vector.rubric) return vector.rubric;
  return (vector.instance || {}).rubric || [];
}

function runOnce(islands, doc, registerSmoke) {
  const sandbox = makeSandbox(doc);
  const E = sandbox.SimGraphScoring;
  assert(E && typeof E.scoreReading === 'function', 'SimGraphScoring did not load');
  const C = sandbox.SimGraphCapture;
  assert(C && typeof C.create === 'function', 'SimGraphCapture did not load');
  const loaded = E.load(doc);
  const contract = loaded.contract;
  const golden = JSON.parse(islands['sim-golden-vectors']);
  const figures = loaded.figures;

  // -- the N05 reading vectors -------------------------------------------
  const n05Rows = [];
  golden.vectors.filter((v) => v.status !== 'retired' && v.instance.payload_class === 'graph')
    .forEach((vector) => {
      const verdict = E.scoreReading({ kind: 'n05_payload', instance: vector.instance },
        vector.submission, rubricOf(vector));
      const expected = vector.expected;
      const keys = ['verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
        'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points'];
      const ok = keys.every((key) => canonical(verdict[key]) === canonical(expected[key]));
      n05Rows.push({
        id: vector.vector_id, status: ok ? 'PASS' : 'FAIL',
        verdict_class: verdict.verdict_class, error_class: verdict.error_class,
        tolerance_class: vector.instance.payload.target_readout.tolerance_class,
        tolerance_mode: 'absolute',
        deviation: verdict.assessed_geometry.deviation, tolerance: verdict.assessed_geometry.tolerance
      });
      if (!ok) throw new Error('N05 reading vector mismatch ' + vector.vector_id);
    });

  // -- the S3-N18 stratum -------------------------------------------------
  const stratumRows = [];
  const parityRows = [];
  const vectors = contract.graph_vectors;
  vectors.reading_vectors.forEach((vector) => {
    const verdict = E.scoreReading(
      { kind: 'figure', figure_id: vector.figure_id, criterion_shape: vector.criterion_shape },
      vector.submission, vector.rubric);
    const expected = vector.expected;
    const ok = verdict.verdict_class === expected.verdict_class &&
      verdict.error_class === expected.error_class &&
      verdict.machine_checked_points === expected.awarded_points;
    stratumRows.push({
      id: vector.id, kind: 'reading', status: ok ? 'PASS' : 'FAIL',
      verdict_class: verdict.verdict_class, error_class: verdict.error_class,
      criterion_shape: vector.criterion_shape,
      deviation: verdict.assessed_geometry.deviation, tolerance: verdict.assessed_geometry.tolerance
    });
    if (!ok) throw new Error('reading vector mismatch ' + vector.id);
  });

  vectors.drawing_vectors.forEach((vector) => {
    const context = contract.capture_contract.capture_contexts[vector.capture_context];
    const record = figures[context.figure_id];
    const pointerPayload = E.capture(vector.capture_context, vector.target_geometry, 'pointer');
    const keyboardPayload = E.capture(vector.capture_context, vector.target_geometry, 'keyboard');
    const pointerDigest = E.canonicalDigest(pointerPayload);
    const keyboardDigest = E.canonicalDigest(keyboardPayload);
    const equal = pointerDigest === keyboardDigest;
    const pointerVerdict = E.scoreDrawing(record, pointerPayload, vector.rubric);
    const keyboardVerdict = E.scoreDrawing(record, keyboardPayload, vector.rubric);
    const expected = vector.expected;
    const ok = pointerVerdict.verdict_class === expected.verdict_class &&
      pointerVerdict.error_class === expected.error_class &&
      pointerVerdict.machine_checked_points === expected.awarded_points;
    const parityOk = equal &&
      pointerVerdict.verdict_class === keyboardVerdict.verdict_class &&
      pointerVerdict.error_class === keyboardVerdict.error_class;
    stratumRows.push({
      id: vector.id, kind: 'drawing', status: ok && parityOk ? 'PASS' : 'FAIL',
      verdict_class: pointerVerdict.verdict_class, error_class: pointerVerdict.error_class,
      criterion_shape: context.criterion_shape,
      checks: pointerVerdict.assessed_geometry.checks,
      max_deviation: pointerVerdict.assessed_geometry.max_deviation,
      excluded_points: (pointerVerdict.assessed_geometry.excluded_points || []).length
    });
    parityRows.push({
      id: vector.id, status: parityOk ? 'PASS' : 'FAIL',
      pointer_digest: pointerDigest, keyboard_digest: keyboardDigest,
      point_count: pointerPayload.points.length,
      verdict: pointerVerdict.verdict_class + '/' + pointerVerdict.error_class
    });
    if (!ok) throw new Error('drawing vector mismatch ' + vector.id);
    if (!parityOk) throw new Error('pointer/keyboard divergence on ' + vector.id);
  });

  // -- the capture component ------------------------------------------------
  // The drawn-response capture component is the only place where a device can
  // be observed, so it is exercised here: the declared keyboard increments,
  // the pointer/keyboard payload parity and the reading-mark parity.
  const captureRows = [];
  /* The cross-language subset: the rows the Python twin can reproduce, so the
   * capture parity is not a JavaScript-only artefact. */
  const captureCrossRows = [];
  const captureContexts = contract.capture_contract.capture_contexts;
  const incrementExamples = {};
  contract.capture_contract.keyboard_increments.keyboard_increment_examples.forEach((row) => {
    incrementExamples[row.capture_context] = row;
  });

  function makeCapture(contextId) {
    return C.create({ engine: E, context: captureContexts[contextId], contextId: contextId });
  }

  /* The declared increments must be the ones the component uses: the
   * component reads them from the engine, the engine from the contract. */
  Object.keys(captureContexts).forEach((contextId) => {
    const capture = makeCapture(contextId);
    const declared = incrementExamples[contextId];
    assert(declared, 'no declared increment example for ' + contextId);
    const actual = capture.increments;
    const ok = Math.abs(actual.coarse_x - declared.coarse_x_value) < 1e-12 &&
      Math.abs(actual.fine_x - declared.fine_x_value) < 1e-12 &&
      Math.abs(actual.coarse_y - declared.coarse_y_value) < 1e-12 &&
      Math.abs(actual.fine_y - declared.fine_y_value) < 1e-12;
    captureRows.push({
      id: 'CAP-INC-' + contextId, kind: 'increments', status: ok ? 'PASS' : 'FAIL',
      coarse_x: actual.coarse_x, fine_x: actual.fine_x,
      coarse_y: actual.coarse_y, fine_y: actual.fine_y
    });
    captureCrossRows.push({
      id: 'CAP-INC-' + contextId, kind: 'increments',
      coarse_x: actual.coarse_x, fine_x: actual.fine_x,
      coarse_y: actual.coarse_y, fine_y: actual.fine_y
    });
    if (!ok) throw new Error('keyboard increment mismatch ' + contextId);
  });

  /* A pointer drag along a straight line. */
  function pointerDrag(contextId, slope, x0, x1, samples) {
    const capture = makeCapture(contextId);
    capture.pointer.begin([x0, slope * x0]);
    for (let i = 1; i <= samples; i += 1) {
      const x = x0 + ((x1 - x0) * i) / samples;
      capture.pointer.move([x, slope * x]);
    }
    return capture.pointer.end();
  }

  /* A keyboard walk that traces the same straight line with the declared
   * diagonal increment. */
  function keyboardDiagonal(contextId, slope, x0, x1) {
    const capture = makeCapture(contextId);
    const steps = Math.round((x1 - x0) / capture.increments.fine_x);
    capture.keyboard.begin([x0, slope * x0]);
    for (let i = 0; i < steps; i += 1) {
      capture.keyboard.keyDown({ key: 'ArrowRight', altKey: true });
    }
    return capture.keyboard.keyDown({ key: 'Enter' });
  }

  /* A keyboard walk that places a point on every grid x, with the y placed at
   * the finest declared increment: the finest geometry the keyboard path can
   * express. */
  function keyboardPlaced(contextId, slope, x0, x1) {
    const capture = makeCapture(contextId);
    const increments = capture.increments;
    const gridStep = Number(captureContexts[contextId].grid.step);
    const cells = Math.round((x1 - x0) / gridStep);
    capture.keyboard.begin([x0, slope * x0]);
    for (let i = 1; i <= cells; i += 1) {
      capture.keyboard.keyDown({ key: 'ArrowRight' });
      const target = slope * (x0 + gridStep * i);
      const steps = Math.round((target - capture.active().y) / increments.fine_y);
      const key = steps >= 0 ? 'ArrowUp' : 'ArrowDown';
      for (let k = 0; k < Math.abs(steps); k += 1) {
        capture.keyboard.keyDown({ key: key, shiftKey: true });
      }
    }
    return capture.keyboard.keyDown({ key: 'Enter' });
  }

  // CP-01: the same line, once drawn with the pointer and once walked with
  // the keyboard. The two payloads must digest equal.
  {
    const contextId = 'CAP-T67-CAL-PRACTICE';
    const capture = makeCapture(contextId);
    const slope = capture.increments.fine_y / capture.increments.fine_x;
    const pointerPayload = pointerDrag(contextId, slope, 0, 0.016, 400);
    const keyboardPayload = keyboardDiagonal(contextId, slope, 0, 0.016);
    const pointerDigest = E.canonicalDigest(pointerPayload);
    const keyboardDigest = E.canonicalDigest(keyboardPayload);
    const record = figures[captureContexts[contextId].figure_id];
    const rubric = [{ criterion_id: 'C1_DRAW', grading: 'auto', points: 3.0 }];
    const pointerVerdict = E.scoreDrawing(record, pointerPayload, rubric);
    const keyboardVerdict = E.scoreDrawing(record, keyboardPayload, rubric);
    const ok = pointerDigest === keyboardDigest &&
      pointerVerdict.verdict_class === keyboardVerdict.verdict_class &&
      pointerVerdict.error_class === keyboardVerdict.error_class;
    captureRows.push({
      id: 'CAP-PARITY-01', kind: 'payload_parity', status: ok ? 'PASS' : 'FAIL',
      slope: slope, pointer_digest: pointerDigest, keyboard_digest: keyboardDigest,
      pointer_points: pointerPayload.points.length, keyboard_points: keyboardPayload.points.length,
      verdict: pointerVerdict.verdict_class + '/' + pointerVerdict.error_class
    });
    if (!ok) throw new Error('pointer/keyboard payload parity failed on CP-01');
    captureCrossRows.push({ id: 'CAP-PARITY-01', kind: 'payload_parity', keyboard_digest: keyboardDigest });
  }

  // CP-02: the true calibration line, which the keyboard cannot place to the
  // last digit because the declared fine step is finite. The verdicts must
  // still match: the placement error stays inside the tolerance band.
  {
    const contextId = 'CAP-T67-CAL-PRACTICE';
    const record = figures[captureContexts[contextId].figure_id];
    const slope = 25.02;
    const pointerPayload = pointerDrag(contextId, slope, 0, 0.016, 800);
    const keyboardPayload = keyboardPlaced(contextId, slope, 0, 0.016);
    const rubric = [{ criterion_id: 'C1_DRAW', grading: 'auto', points: 3.0 }];
    const pointerVerdict = E.scoreDrawing(record, pointerPayload, rubric);
    const keyboardVerdict = E.scoreDrawing(record, keyboardPayload, rubric);
    const band = 0.003;
    const ok = pointerVerdict.verdict_class === keyboardVerdict.verdict_class &&
      pointerVerdict.error_class === keyboardVerdict.error_class &&
      keyboardVerdict.assessed_geometry.max_deviation <= band;
    captureRows.push({
      id: 'CAP-PARITY-02', kind: 'verdict_parity', status: ok ? 'PASS' : 'FAIL',
      pointer_digest: E.canonicalDigest(pointerPayload),
      keyboard_digest: E.canonicalDigest(keyboardPayload),
      pointer_deviation: pointerVerdict.assessed_geometry.max_deviation,
      keyboard_deviation: keyboardVerdict.assessed_geometry.max_deviation,
      tolerance_band: band,
      pointer_verdict: pointerVerdict.verdict_class + '/' + pointerVerdict.error_class,
      keyboard_verdict: keyboardVerdict.verdict_class + '/' + keyboardVerdict.error_class
    });
    if (!ok) throw new Error('pointer/keyboard verdict parity failed on CP-02');
    captureCrossRows.push({
      id: 'CAP-PARITY-02', kind: 'verdict_parity', keyboard_digest: E.canonicalDigest(keyboardPayload),
      keyboard_deviation: keyboardVerdict.assessed_geometry.max_deviation,
      keyboard_verdict: keyboardVerdict.verdict_class + '/' + keyboardVerdict.error_class
    });
  }

  // CP-03: a reading mark placed by pointer and by keyboard must be the same
  // mark and must produce the same verdict.
  {
    const contextId = 'CAP-T67-CAL-PRACTICE';
    const vector = vectors.reading_vectors[0];
    const pointerCapture = makeCapture(contextId);
    const pointerMark = pointerCapture.mark([0.008, 0.201]);
    const keyboardCapture = makeCapture(contextId);
    keyboardCapture.keyboard.begin([0, 0]);
    for (let i = 0; i < 4; i += 1) { keyboardCapture.keyboard.keyDown({ key: 'ArrowRight' }); }
    for (let i = 0; i < 134; i += 1) { keyboardCapture.keyboard.keyDown({ key: 'ArrowUp', shiftKey: true }); }
    const keyboardMark = keyboardCapture.mark();
    const pointerDigest = E.canonicalDigest(pointerMark);
    const keyboardDigest = E.canonicalDigest(keyboardMark);
    const source = { kind: 'figure', figure_id: vector.figure_id, criterion_shape: vector.criterion_shape };
    const rubric = [{ criterion_id: 'C1_READ', grading: 'auto', points: 2.0 }];
    const pointerVerdict = E.scoreReading(source, pointerMark.points[0], rubric);
    const keyboardVerdict = E.scoreReading(source, keyboardMark.points[0], rubric);
    const pointerVerdictDigest = E.canonicalDigest(E.canonicalProjection(pointerVerdict));
    const keyboardVerdictDigest = E.canonicalDigest(E.canonicalProjection(keyboardVerdict));
    const ok = pointerDigest === keyboardDigest && pointerVerdictDigest === keyboardVerdictDigest;
    captureRows.push({
      id: 'CAP-PARITY-03', kind: 'mark_parity', status: ok ? 'PASS' : 'FAIL',
      pointer_digest: pointerDigest, keyboard_digest: keyboardDigest,
      pointer_verdict_digest: pointerVerdictDigest, keyboard_verdict_digest: keyboardVerdictDigest,
      verdict: pointerVerdict.verdict_class + '/' + pointerVerdict.error_class
    });
    if (!ok) throw new Error('reading mark parity failed on CP-03');
    captureCrossRows.push({ id: 'CAP-PARITY-03', kind: 'mark_parity', keyboard_digest: keyboardDigest });
  }

  // -- the validity corpus -------------------------------------------------
  const validityRows = [];
  vectors.validity_corpus.forEach((caseRow) => {
    let verdict;
    if (caseRow.family === 'drawing') {
      const context = contract.capture_contract.capture_contexts[caseRow.capture_context];
      const record = figures[context.figure_id];
      const payload = E.capture(caseRow.capture_context, caseRow.target_geometry, 'pointer');
      verdict = E.scoreDrawing(record, payload, [{ criterion_id: 'C1_DRAW', grading: 'auto', points: 3.0 }]);
    } else {
      verdict = E.scoreReading(
        { kind: 'figure', figure_id: caseRow.figure_id, criterion_shape: caseRow.criterion_shape },
        caseRow.submission, [{ criterion_id: 'C1_READ', grading: 'auto', points: 2.0 }]);
    }
    const ok = verdict.error_class === caseRow.expected_class;
    validityRows.push({
      id: caseRow.id, case: caseRow.case, status: ok ? 'PASS' : 'FAIL',
      expected_class: caseRow.expected_class, actual_class: verdict.error_class,
      verdict_class: verdict.verdict_class, awarded_points: verdict.machine_checked_points
    });
    if (!ok) throw new Error('validity case mismatch ' + caseRow.id);
  });

  // -- the capture payload validation corpus -------------------------------
  const payloadRows = [];
  vectors.payload_validation_corpus.forEach((caseRow) => {
    let actual = null;
    try {
      E.validatePayload(caseRow.payload);
    } catch (error) {
      actual = error.code;
    }
    const ok = actual === caseRow.expected_class;
    payloadRows.push({
      id: caseRow.id, case: caseRow.case, status: ok ? 'PASS' : 'FAIL',
      expected_class: caseRow.expected_class, actual_class: actual
    });
    if (!ok) throw new Error('payload case mismatch ' + caseRow.id);
  });

  // -- the verdict replay proof -------------------------------------------
  const replayRows = [];
  [vectors.reading_vectors[0], vectors.reading_vectors[1], vectors.drawing_vectors[1],
    vectors.drawing_vectors[4]].forEach((vector) => {
    let verdict;
    if (vector.family === 'reading') {
      verdict = E.scoreReading(
        { kind: 'figure', figure_id: vector.figure_id, criterion_shape: vector.criterion_shape },
        vector.submission, vector.rubric);
    } else {
      const context = contract.capture_contract.capture_contexts[vector.capture_context];
      const record = figures[context.figure_id];
      const payload = E.capture(vector.capture_context, vector.target_geometry, 'pointer');
      verdict = E.scoreDrawing(record, payload, vector.rubric);
    }
    const replayed = E.replayVerdict(verdict);
    const ok = replayed.verdict_class === verdict.verdict_class &&
      replayed.error_class === verdict.error_class;
    replayRows.push({
      id: vector.id, status: ok ? 'PASS' : 'FAIL',
      original: verdict.verdict_class + '/' + verdict.error_class,
      replayed: String(replayed.verdict_class) + '/' + String(replayed.error_class)
    });
    if (!ok) throw new Error('verdict replay mismatch ' + vector.id);
  });

  // -- the smoke vector ----------------------------------------------------
  // The Section 1.3 runtime-JS ceiling leaves no room in the artifact's smoke
  // subset, so the graph smoke vector is registered here (the N17 precedent).
  let smoke = null;
  if (registerSmoke) {
    const spec = contract.smoke;
    const reading = E.scoreReading(
      { kind: 'figure', figure_id: spec.case.reading.figure_id, criterion_shape: spec.case.reading.criterion_shape },
      spec.case.reading.submission, [{ criterion_id: 'C1_READ', grading: 'auto', points: 2.0 }]);
    const context = contract.capture_contract.capture_contexts[spec.case.drawing.capture_context];
    const record = figures[context.figure_id];
    const payload = E.capture(spec.case.drawing.capture_context, spec.case.drawing.target_geometry, 'pointer');
    const drawing = E.scoreDrawing(record, payload, [{ criterion_id: 'C1_DRAW', grading: 'auto', points: 3.0 }]);
    const digest = E.canonicalDigest({
      reading: [reading.verdict_class, reading.error_class, reading.assessed_geometry.deviation,
        reading.assessed_geometry.tolerance],
      drawing: [drawing.verdict_class, drawing.error_class, drawing.assessed_geometry.max_deviation,
        drawing.assessed_geometry.checks]
    });
    const outcome = reading.verdict_class === spec.expected.reading_verdict &&
      drawing.verdict_class === spec.expected.drawing_verdict
      ? { status: 'PASS', details: { digest: digest, reading: reading.verdict_class, drawing: drawing.verdict_class } }
      : { status: 'FAIL', reason: 'verdict mismatch' };
    smoke = {
      status: outcome.status, total: 1, passed: outcome.status === 'PASS' ? 1 : 0,
      failed: outcome.status === 'PASS' ? 0 : 1,
      vectors: [{ id: spec.id, owner: spec.owner, status: outcome.status,
        details: outcome.details || null, reason: outcome.reason || null }]
    };
    if (smoke.status !== 'PASS') throw new Error('smoke vector failed');
  }

  // The full verdict records, canonically projected: the Python twin must
  // reproduce them record for record, not merely the summary rows.
  const verdictRecords = Object.create(null);
  golden.vectors.filter((v) => v.status !== 'retired' && v.instance.payload_class === 'graph')
    .forEach((vector) => {
      verdictRecords[vector.vector_id] = E.canonicalProjection(
        E.scoreReading({ kind: 'n05_payload', instance: vector.instance },
          vector.submission, rubricOf(vector)));
    });
  vectors.reading_vectors.forEach((vector) => {
    verdictRecords[vector.id] = E.canonicalProjection(
      E.scoreReading({ kind: 'figure', figure_id: vector.figure_id, criterion_shape: vector.criterion_shape },
        vector.submission, vector.rubric));
  });
  vectors.drawing_vectors.forEach((vector) => {
    const context = contract.capture_contract.capture_contexts[vector.capture_context];
    const record = figures[context.figure_id];
    const payload = E.capture(vector.capture_context, vector.target_geometry, 'pointer');
    verdictRecords[vector.id] = E.canonicalProjection(E.scoreDrawing(record, payload, vector.rubric));
  });

  const rows = { n05: n05Rows, stratum: stratumRows, capture: captureRows,
    capture_cross: captureCrossRows, validity: validityRows,
    payload: payloadRows, parity: parityRows, replay: replayRows };
  return {
    rows: rows,
    verdictRecords: verdictRecords,
    smoke: smoke,
    digests: {
      n05_verdicts: sha256(JSON.stringify(n05Rows)),
      stratum_verdicts: sha256(JSON.stringify(stratumRows)),
      capture_parity: sha256(JSON.stringify(captureRows)),
      capture_cross: sha256(JSON.stringify(captureCrossRows)),
      validity_verdicts: sha256(JSON.stringify(validityRows)),
      payload_verdicts: sha256(JSON.stringify(payloadRows)),
      parity_digests: sha256(JSON.stringify(parityRows)),
      replay_verdicts: sha256(JSON.stringify(replayRows)),
      contract: sha256(islands['sim-graph-scoring']),
      engine_source: sha256(fs.readFileSync(path.join(ROOT, 'src/graph-scoring-engine.js'), 'utf8')),
      capture_source: sha256(fs.readFileSync(path.join(ROOT, 'src/graph-capture.js'), 'utf8'))
    },
    counts: {
      n05: n05Rows.length, stratum: stratumRows.length, capture: captureRows.length,
      capture_cross: captureCrossRows.length,
      validity: validityRows.length, payload: payloadRows.length, parity: parityRows.length,
      replay: replayRows.length
    }
  };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const islands = extractIslands(html);
  const first = runOnce(islands, makeDocument(islands), true);
  const second = runOnce(islands, makeDocument(islands), false);
  const parity = JSON.stringify(first.digests) === JSON.stringify(second.digests);
  const report = {
    schema_version: 1, task: 'N18', status: parity ? 'PASS' : 'FAIL',
    artifact_sha256: sha256(html),
    runtime_js_note: 'The graph scoring engine and the drawn-response capture component are verified from src/graph-scoring-engine.js and src/graph-capture.js against the shipped islands; neither is inlined into the artifact, because the runtime-JS ceiling headroom is 83 bytes (N31 owns the resolution).',
    counts: first.counts, digests: first.digests, parity: parity,
    verdict_records: first.verdictRecords,
    smoke: first.smoke,
    smoke_summary: first.smoke ? {
      total: first.smoke.total, passed: first.smoke.passed, failed: first.smoke.failed,
      vector: first.smoke.vectors.filter((v) => v.id === 'SMK-N18-GRAPH-SCORING')
    } : { status: 'not-run' },
    rows: first.rows
  };
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exit(1);
}
main();
