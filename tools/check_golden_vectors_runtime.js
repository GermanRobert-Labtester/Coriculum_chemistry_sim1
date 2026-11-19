#!/usr/bin/env node
/* N05 runtime harness: execute shipped #sim-golden-vectors & SimPRNG in a minimal DOM.
 *
 * Proves:
 *  - loading the shipped #sim-golden-vectors island from output/simulator.html;
 *  - embedded SimPRNG contract smoke check + seed-1/shuffle verification;
 *  - honest degradation on truncated (#sim-golden-vectors E_VECTORS_JSON) and
 *    missing (#sim-golden-vectors E_VECTORS_MISSING) islands;
 *  - rejection of a scratch island reusing a retired_id (E_VECTORS_RETIRED_REUSE).
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT = path.join(ROOT, 'output', 'simulator.html');

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function Node(tagName) {
  this.tagName = String(tagName).toUpperCase();
  this.childNodes = [];
  this.attributes = Object.create(null);
  this.id = '';
  this.hidden = false;
  this._text = '';
}
Object.defineProperty(Node.prototype, 'textContent', {
  get() { return this._text; },
  set(value) { this._text = String(value); }
});

function makeDocument(vectorsText) {
  const nodes = Object.create(null);
  ['sim-golden-vectors', 'sim-golden-vectors-error', 'sim-golden-vectors-status'].forEach((id) => {
    const n = new Node(id === 'sim-golden-vectors' ? 'script' : 'div');
    n.id = id;
    if (id !== 'sim-golden-vectors') n.hidden = true;
    nodes[id] = n;
  });
  if (vectorsText === null) {
    delete nodes['sim-golden-vectors'];
  } else {
    nodes['sim-golden-vectors'].textContent = vectorsText;
  }
  return {
    nodes,
    getElementById(id) {
      return Object.prototype.hasOwnProperty.call(nodes, id) ? nodes[id] : null;
    }
  };
}

function extractIsland(html, id) {
  const re = new RegExp('<script type="application/json" id="' + id + '">([\\s\\S]*?)</script>');
  const m = html.match(re);
  if (!m) throw new Error('Missing #' + id + ' in artifact');
  return m[1].replace(/<\\\//g, '</');
}

function runHarness() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const shippedText = extractIsland(html, 'sim-golden-vectors');
  const prngCode = fs.readFileSync(path.join(ROOT, 'src', 'prng.js'), 'utf8');
  const loaderCode = fs.readFileSync(path.join(ROOT, 'src', 'golden-vectors-loader.js'), 'utf8');

  const sandbox = { window: {}, globalThis: {}, console, Error, String, Object, Array, Number, BigInt, JSON };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(prngCode, sandbox, { filename: 'src/prng.js' });
  vm.runInContext(loaderCode, sandbox, { filename: 'src/golden-vectors-loader.js' });

  const SimGoldenVectors = sandbox.SimGoldenVectors;

  // 1. Shipped island
  const shippedDoc = makeDocument(shippedText);
  const loaded = SimGoldenVectors.load(shippedDoc);
  SimGoldenVectors.renderStatus(shippedDoc, loaded);

  // 2. Truncated island
  const truncDoc = makeDocument(shippedText.slice(0, 120));
  let truncErr = null;
  try {
    SimGoldenVectors.load(truncDoc);
  } catch (e) {
    truncErr = { name: e.name, code: e.code, message: e.message };
    SimGoldenVectors.renderError(truncDoc, e);
  }

  // 3. Missing island
  const missingDoc = makeDocument(null);
  let missingErr = null;
  try {
    SimGoldenVectors.load(missingDoc);
  } catch (e) {
    missingErr = { name: e.name, code: e.code, message: e.message };
  }

  // 4. Retired ID reuse rejection
  const retiredReuse = JSON.parse(shippedText);
  const firstId = retiredReuse.vectors[0].vector_id;
  retiredReuse.retired_ids = [{ retired_id: firstId, replaced_by: 'GV-S1-T1-Q02-99', reason: 'test', ledger_ref: 'N05' }];
  let retiredErr = null;
  try {
    SimGoldenVectors.load(makeDocument(JSON.stringify(retiredReuse)));
  } catch (e) {
    retiredErr = { name: e.name, code: e.code, message: e.message };
  }

  const ok = (
    loaded.island_id === 'sim-golden-vectors' &&
    loaded.counts.active === 40 &&
    loaded.counts.topics === 7 &&
    loaded.counts.types === 11 &&
    loaded.prng_smoke.illegal_zero_rejected === true &&
    !shippedDoc.nodes['sim-golden-vectors-status'].hidden &&
    truncErr && truncErr.code === 'E_VECTORS_JSON' && truncErr.message.includes('#sim-golden-vectors') &&
    !truncDoc.nodes['sim-golden-vectors-error'].hidden &&
    missingErr && missingErr.code === 'E_VECTORS_MISSING' && missingErr.message.includes('#sim-golden-vectors') &&
    retiredErr && retiredErr.code === 'E_VECTORS_RETIRED_REUSE' && retiredErr.message.includes(firstId)
  );

  return {
    schema_version: 1,
    task: 'N05',
    artifact: 'golden-vectors-runtime-harness',
    artifact_sha256: sha256(html),
    status: ok ? 'PASS' : 'FAIL',
    shipped: {
      counts: loaded.counts,
      prng_smoke: loaded.prng_smoke,
      status_text: shippedDoc.nodes['sim-golden-vectors-status'].textContent
    },
    degradation: {
      truncated: truncErr,
      missing: missingErr,
      retired_reuse: retiredErr
    }
  };
}

const report = runHarness();
if (process.argv.includes('--json')) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log(`${report.status} N05 golden-vectors runtime: ${report.shipped.counts.active} active, ${report.shipped.counts.topics} topics, ${report.shipped.counts.types} types`);
}
process.exit(report.status === 'PASS' ? 0 : 1);
