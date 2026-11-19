#!/usr/bin/env node
/* N17 runtime harness. Loads the shipped islands from output/simulator.html and
 * the engine module from src/quantity-engine.js (the module is intentionally not
 * inlined into the executable script: the N06 Section 1.3 runtime-JS ceiling has
 * 83 bytes of headroom at N17; see evidence/N17_VERIFICATION_RECORD.md).
 *
 * Proves: 40/40 N05 verdict parity, 20/20 N17 stratum vectors, cross-language
 * comparable digests, an in-file smoke classification vector, and two-run parity.
 * Not a browser render or accessibility acceptance claim.
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');
const ISLAND_IDS = ['sim-conventions', 'sim-terms', 'sim-golden-vectors', 'sim-engines'];

function sha256(text) { return crypto.createHash('sha256').update(text, 'utf8').digest('hex'); }
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
  nodes['sim-engines-error'] = { id: 'sim-engines-error', textContent: '', hidden: true };
  nodes['sim-smoke-status'] = { id: 'sim-smoke-status', textContent: '', hidden: true };
  return { getElementById: (id) => nodes[id] || null };
}

function makeSandbox(doc) {
  const sandbox = {
    console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
    RegExp, isFinite, parseInt, parseFloat, Date
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  ['src/terms-loader.js', 'src/figure-framework.js', 'src/quantity-engine.js', 'src/smoke-subset.js']
    .forEach((relative) => vm.runInContext(fs.readFileSync(path.join(ROOT, relative), 'utf8'), sandbox,
      { filename: relative }));
  return sandbox;
}

function canonical(value) {
  if (Array.isArray(value)) return '[' + value.map(canonical).join(',') + ']';
  if (value && typeof value === 'object') {
    return '{' + Object.keys(value).sort().map((k) => JSON.stringify(k) + ':' + canonical(value[k])).join(',') + '}';
  }
  return JSON.stringify(value);
}
function verdictDigest(rows) { return sha256(JSON.stringify(rows)); }

function runOnce(html, islands, doc, registerSmoke) {
  const sandbox = makeSandbox(doc);
  const E = sandbox.SimEngines;
  assert(E && typeof E.grade === 'function', 'SimEngines did not load');
  const golden = JSON.parse(islands['sim-golden-vectors']);
  const tax = JSON.parse(islands['sim-engines']);
  const goldenRows = [];
  golden.vectors.filter((v) => v.status !== 'retired').forEach((vec) => {
    const exp = vec.expected;
    const got = E.grade(vec.instance, vec.submission, {
      oracle_version: exp.oracle_version, oracle_digest: exp.oracle_digest,
      conventions_digest: golden.conventions_digest
    });
    const keys = ['verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
      'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points',
      'oracle_version', 'oracle_digest', 'conventions_digest'];
    const view = Object.create(null);
    keys.forEach((k) => { view[k] = got[k]; });
    const ok = canonical(view) === canonical(exp);
    goldenRows.push({ id: vec.vector_id, status: ok ? 'PASS' : 'FAIL',
      error_class: got.error_class, taxonomy_class: got.taxonomy_class, signature: got.signature });
    if (!ok) throw new Error('vector mismatch ' + vec.vector_id + ': ' + got.error_class + '/' + got.verdict_class);
  });

  const ev = tax.engine_vectors;
  const stratumRows = [];
  ev.v04_forms.forEach((f) => {
    const got = E.classify({ raw: '1,0', unit: f.unit, expected_unit: f.expected_unit });
    stratumRows.push({ id: f.id, kind: 'v04', status: got.taxonomy_class === f.expected_class ? 'PASS' : 'FAIL',
      actual: got.taxonomy_class });
  });
  ev.conservation_vectors.forEach((v) => {
    const got = E.checkConservation(v);
    stratumRows.push({ id: v.id, kind: 'conservation', status: got.verdict === v.expected_verdict ? 'PASS' : 'FAIL',
      actual: got.verdict, signature: got.signature });
  });
  ev.classification_vectors.forEach((v) => {
    const got = E.classify(v);
    const ok = got.taxonomy_class === v.expected_class && got.signature === v.expected_signature;
    stratumRows.push({ id: v.id, kind: 'classification', status: ok ? 'PASS' : 'FAIL',
      actual: got.taxonomy_class, signature: got.signature, trace: got.precedence_trace });
  });
  const scratch = E.checkConservation(ev.scratch.conservation);
  if (scratch.verdict !== ev.scratch.conservation.expected_verdict) throw new Error('scratch conservation did not fail by id');
  if (stratumRows.some((r) => r.status !== 'PASS')) throw new Error('N17 stratum vector failure: ' +
    JSON.stringify(stratumRows.filter((r) => r.status !== 'PASS')));

  // Smoke vector SMK-N17-CLASSIFICATION: registered in the harness because the
  // Section 1.3 runtime-JS ceiling leaves no room in the artifact's smoke subset.
  let smoke = null;
  if (registerSmoke && sandbox.SimSmoke && typeof sandbox.SimSmoke.register === 'function') {
    const spec = tax.smoke;
    sandbox.SimSmoke.register({
      id: spec.id, owner: 'N17',
      description: 'V-04 classification by precedence with a fixed feedback digest.',
      run: function () {
        const got = E.classify(spec.case);
        if (got.taxonomy_class !== spec.expected_class || got.signature !== spec.expected_signature) {
          return { status: 'FAIL', reason: 'classification' };
        }
        if (!got.feedback_text) return { status: 'FAIL', reason: 'feedback unresolved' };
        const digest = E.sha256(JSON.stringify([got.taxonomy_class, got.signature]));
        if (digest !== 'd1c5027bf952ccf126a044dc2804e557de7245da20581388218e65749dd17127') {
          return { status: 'FAIL', reason: 'digest ' + digest };
        }
        return { status: 'PASS', details: { taxonomyClass: got.taxonomy_class, signature: got.signature,
          digest: digest, feedbackKey: got.feedback_key } };
      }
    });
    const registered = sandbox.SimSmoke.vectors[sandbox.SimSmoke.vectors.length - 1];
    const outcome = registered.run(doc);
    smoke = {
      status: outcome.status === 'PASS' ? 'PASS' : 'FAIL',
      total: 1, passed: outcome.status === 'PASS' ? 1 : 0,
      failed: outcome.status === 'PASS' ? 0 : 1,
      vectors: [{ id: registered.id, owner: registered.owner, status: outcome.status,
        details: outcome.details || null, reason: outcome.reason || null }]
    };
    if (smoke.status !== 'PASS') throw new Error('smoke vector failed: ' + JSON.stringify(smoke.vectors));
  }

  return {
    goldenRows: goldenRows,
    stratumRows: stratumRows,
    smoke: smoke,
    digests: {
      golden_verdicts: verdictDigest(goldenRows),
      stratum_verdicts: verdictDigest(stratumRows),
      taxonomy: sha256(islands['sim-engines']),
      engine_source: sha256(fs.readFileSync(path.join(ROOT, 'src/quantity-engine.js'), 'utf8'))
    },
    counts: {
      golden: goldenRows.length, v04: ev.v04_forms.length,
      conservation: ev.conservation_vectors.length,
      classification: ev.classification_vectors.length
    }
  };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const islands = extractIslands(html);
  const first = runOnce(html, islands, makeDocument(islands), true);
  const second = runOnce(html, islands, makeDocument(islands), false);
  const parity = JSON.stringify(first.digests) === JSON.stringify(second.digests);
  const report = {
    schema_version: 1, task: 'N17', status: parity ? 'PASS' : 'FAIL',
    artifact_sha256: sha256(html),
    runtime_js_note: 'Engine module verified from src/quantity-engine.js against shipped islands; runtime-JS ceiling headroom at N17 was 83 bytes.',
    counts: first.counts, digests: first.digests, parity: parity,
    smoke: first.smoke,
    smoke_summary: first.smoke ? {
      total: first.smoke.total, passed: first.smoke.passed, failed: first.smoke.failed,
      vector: first.smoke.vectors.filter((v) => v.id === 'SMK-N17-CLASSIFICATION')
    } : { status: 'not-run' },
    golden_sample: first.goldenRows.slice(0, 6),
    stratum_rows: first.stratumRows
  };
  console.log(JSON.stringify(report, null, 2));
  if (report.status !== 'PASS') process.exit(1);
}
main();
