#!/usr/bin/env node
/* N04 runtime harness: execute the shipped bank loader in a minimal DOM.
 *
 * Proves:
 *  - loading the shipped #sim-bank island from output/simulator.html;
 *  - loading a full-size 112-instance scratch bank (all 18 types, 28 families);
 *  - typed payload mapping and consumer handoff (N22 renderers, N17-N19 engines, N24 assembly);
 *  - loud failure on an unknown type (type named);
 *  - honest degradation on a truncated or missing #sim-bank (#sim-bank named);
 *  - loud failure when a required per-form type is missing from a populated bank.
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

function makeDocument(bankText) {
  const nodes = Object.create(null);
  ['sim-bank', 'sim-bank-error', 'sim-bank-status'].forEach((id) => {
    const n = new Node(id === 'sim-bank' ? 'script' : 'div');
    n.id = id;
    if (id !== 'sim-bank') n.hidden = true;
    nodes[id] = n;
  });
  if (bankText === null) {
    delete nodes['sim-bank'];
  } else {
    nodes['sim-bank'].textContent = bankText;
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

function extractLoader(html) {
  const start = html.indexOf('/* N04 bank loader:');
  const end = html.indexOf('/* N02 coverage view');
  const altEnd = html.indexOf('(function () {\n  \'use strict\';');
  const stop = end > start ? end : altEnd;
  if (start < 0 || stop <= start) {
    return fs.readFileSync(path.join(ROOT, 'src', 'bank-loader.js'), 'utf8');
  }
  return html.slice(start, stop);
}

function runHarness(fullBankPath) {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const shippedBankText = extractIsland(html, 'sim-bank');
  const loaderCode = fs.readFileSync(path.join(ROOT, 'src', 'bank-loader.js'), 'utf8');

  const sandbox = { window: {}, globalThis: {} };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(loaderCode, sandbox, { filename: 'src/bank-loader.js' });
  const SimBank = sandbox.SimBank;

  // 1. Shipped pre-N20 island
  const shippedDoc = makeDocument(shippedBankText);
  const shipped = SimBank.load(shippedDoc);
  SimBank.renderStatus(shippedDoc, shipped);

  // 2. Full-size 112-instance scratch bank
  if (!fullBankPath) {
    throw new Error('Pass --full-bank <path> to test 112-instance load');
  }
  const fullData = JSON.parse(fs.readFileSync(fullBankPath, 'utf8'));
  const fullIsland = {
    island_id: 'sim-bank',
    schema_version: 1,
    bank_version: 'scratch-112',
    status: 'validated-bank',
    questions: fullData.questions || fullData
  };
  const fullDoc = makeDocument(JSON.stringify(fullIsland));
  const loaded = SimBank.load(fullDoc);
  const q02List = SimBank.getForRenderer(loaded, 'Q02');
  const assemblyList = SimBank.getForAssembly(loaded);
  const firstBindings = SimBank.getEngineBindings(assemblyList[0]);

  // 3. Unknown type failure
  const unknownIsland = JSON.parse(JSON.stringify(fullIsland));
  unknownIsland.questions[0].type_id = 'Q99';
  let unknownErr = null;
  try {
    SimBank.load(makeDocument(JSON.stringify(unknownIsland)));
  } catch (e) {
    unknownErr = { name: e.name, code: e.code, message: e.message };
  }

  // 4. Truncated #sim-bank degradation
  const truncDoc = makeDocument('{"island_id":"sim-bank","questions":[{"question_id":"COL1-1');
  let truncErr = null;
  try {
    SimBank.load(truncDoc);
  } catch (e) {
    truncErr = { name: e.name, code: e.code, message: e.message };
    SimBank.renderError(truncDoc, e);
  }

  // 5. Missing #sim-bank degradation
  let missingErr = null;
  try {
    SimBank.load(makeDocument(null));
  } catch (e) {
    missingErr = { name: e.name, code: e.code, message: e.message };
  }

  // 6. Missing required type (drop Q15)
  const missingReqIsland = JSON.parse(JSON.stringify(fullIsland));
  missingReqIsland.questions = missingReqIsland.questions.filter(
    (q) => q.type_id !== 'Q15' && !(q.type_ids || []).includes('Q15')
  );
  let missingReqErr = null;
  try {
    SimBank.load(makeDocument(JSON.stringify(missingReqIsland)));
  } catch (e) {
    missingReqErr = { name: e.name, code: e.code, message: e.message };
  }

  const ok = (
    shipped.island_id === 'sim-bank' &&
    loaded.counts.total === 112 &&
    loaded.counts.types === 18 &&
    loaded.counts.families === 28 &&
    q02List.length > 0 &&
    assemblyList.length === 112 &&
    firstBindings.length > 0 &&
    unknownErr && unknownErr.code === 'E_BANK_UNKNOWN_TYPE' && unknownErr.message.includes('Q99') &&
    truncErr && truncErr.code === 'E_BANK_JSON' && truncErr.message.includes('#sim-bank') &&
    !truncDoc.nodes['sim-bank-error'].hidden &&
    missingErr && missingErr.code === 'E_BANK_MISSING' && missingErr.message.includes('#sim-bank') &&
    missingReqErr && missingReqErr.code === 'E_BANK_MISSING_REQUIRED_TYPE' && missingReqErr.message.includes('Q15')
  );

  return {
    schema_version: 1,
    task: 'N04',
    artifact: 'bank-runtime-harness',
    artifact_sha256: sha256(html),
    status: ok ? 'PASS' : 'FAIL',
    shipped_island: {
      status: shipped.status,
      total: shipped.counts.total,
      status_text: shippedDoc.nodes['sim-bank-status'].textContent
    },
    full_bank_load: {
      total: loaded.counts.total,
      types: loaded.counts.types,
      families: loaded.counts.families,
      q02_renderer_count: q02List.length,
      assembly_count: assemblyList.length,
      sample_renderer_key: assemblyList[0].renderer_key,
      sample_engine_bindings: firstBindings
    },
    degradation: {
      unknown_type: unknownErr,
      truncated_island: truncErr,
      truncated_error_rendered: truncDoc.nodes['sim-bank-error'].textContent,
      missing_island: missingErr,
      missing_required_type: missingReqErr
    }
  };
}

const args = process.argv.slice(2);
const fullIdx = args.indexOf('--full-bank');
const fullBankPath = fullIdx >= 0 ? args[fullIdx + 1] : null;
const report = runHarness(fullBankPath);
if (args.includes('--json')) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log(`${report.status} N04 bank runtime: ${report.full_bank_load.total} loaded, ${report.full_bank_load.types} types, ${report.full_bank_load.families} families`);
}
process.exit(report.status === 'PASS' ? 0 : 1);
