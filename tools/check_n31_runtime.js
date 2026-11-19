#!/usr/bin/env node
/* N31 runtime harness (tools/check_n31_runtime.js):
 * Executes the single assembled script from output/simulator.html against its
 * own embedded islands and <meta> digest tags in an isolated VM context,
 * proving:
 *   1. B.1.2 Single-script wrapper & boundary mapping: the inline script parses
 *      via vm.Script and every one of the 37 module regions is findable by its
 *      recorded separator comment (/* === MODULE: <path> === *\/) and maps back
 *      to its source file in data/build_policy.json.
 *   2. Topological load/bootstrap execution: all 36 Sim* runtime globals
 *      (including the 11 newly inlined Phase IV–V engine/input/grading modules)
 *      initialize cleanly from output/simulator.html with zero error banners.
 *   3. In-file smoke suite (27/27 vectors PASS):
 *      - SMK-N20-BANK-GRADE-VERDICT exercises live in-file SimBank + SimEngines
 *      - SMK-N22-* exercise live in-file SimInputs.buildPayload ('facade-exercised')
 *      - SMK-N23-* exercise live in-file SimGrading.applyRubricPolicy ('facade-exercised')
 *      - SMK-N31-BUILD-CONTRACT passes (7 core islands, 36 runtime globals)
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');
const ARTIFACT_PATH = path.join(ROOT, 'output', 'simulator.html');
const POLICY_PATH = path.join(ROOT, 'data', 'build_policy.json');

function sha256(text) {
  return crypto.createHash('sha256').update(String(text), 'utf8').digest('hex');
}

function parseArgs(argv) {
  const args = { record: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--record' && argv[i + 1]) {
      args.record = path.resolve(argv[i + 1]);
      i += 1;
    }
  }
  return args;
}

function buildArtifactDom(html) {
  const registry = Object.create(null);
  const metas = Object.create(null);

  function Node(tagName, id) {
    this.tagName = String(tagName || 'DIV').toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
    this.listeners = Object.create(null);
    this.className = '';
    this._id = '';
    this.hidden = false;
    this.disabled = false;
    this.type = '';
    this.value = '';
    this.checked = false;
    this.tabIndex = 0;
    this._text = '';
    this.dataset = Object.create(null);
    this.style = Object.create(null);
    if (id) this.id = id;
  }

  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(v) {
      if (this._id && registry[this._id] === this) delete registry[this._id];
      this._id = String(v || '');
      if (this._id) registry[this._id] = this;
    }
  });

  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });

  Object.defineProperty(Node.prototype, 'textContent', {
    get() {
      return this.childNodes.length
        ? this.childNodes.map((c) => c.textContent).join('')
        : this._text;
    },
    set(v) {
      this.childNodes = [];
      this._text = String(v === null || v === undefined ? '' : v);
    }
  });

  Object.defineProperty(Node.prototype, 'innerHTML', {
    get() { return this.textContent; },
    set(v) { this.textContent = v; }
  });

  Node.prototype.appendChild = function (child) {
    if (!child) return child;
    child.parentNode = this;
    this.childNodes.push(child);
    if (child.id) registry[child.id] = child;
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const idx = this.childNodes.indexOf(child);
    if (idx >= 0) {
      this.childNodes.splice(idx, 1);
      child.parentNode = null;
    }
    return child;
  };
  Node.prototype.setAttribute = function (k, v) {
    this.attributes[k] = String(v);
    if (k === 'id') this.id = v;
  };
  Node.prototype.getAttribute = function (k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k)
      ? this.attributes[k]
      : null;
  };
  Node.prototype.removeAttribute = function (k) {
    delete this.attributes[k];
  };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (typeOrEv, evObj) {
    const type = typeof typeOrEv === 'string' ? typeOrEv : (typeOrEv && typeOrEv.type);
    const list = this.listeners[type] || [];
    for (let i = 0; i < list.length; i += 1) {
      list[i](evObj || (typeof typeOrEv === 'object' ? typeOrEv : { type }));
    }
    return true;
  };
  Node.prototype.focus = function () { doc.activeElement = this; };
  Node.prototype.blur = function () {
    if (doc.activeElement === this) doc.activeElement = null;
  };
  Node.prototype.querySelector = function () { return null; };
  Node.prototype.querySelectorAll = function () { return []; };

  const doc = {
    documentElement: new Node('html', ''),
    body: new Node('body', ''),
    activeElement: null,
    createElement(tag) { return new Node(tag, ''); },
    createElementNS(_ns, tag) { return new Node(tag, ''); },
    createTextNode(text) {
      const n = new Node('#text', '');
      n.textContent = String(text);
      return n;
    },
    getElementById(id) { return registry[id] || null; },
    querySelector(sel) {
      const m = /^meta\[name="([^"]+)"\]$/.exec(String(sel || '').trim());
      if (m && metas[m[1]]) return metas[m[1]];
      const idMatch = /^#([A-Za-z0-9_-]+)$/.exec(String(sel || '').trim());
      if (idMatch) return registry[idMatch[1]] || null;
      return null;
    },
    querySelectorAll() { return []; },
    addEventListener() {}
  };

  // Extract all <meta name="..." content="...">
  const metaRe = /<meta\s+name="([^"]+)"\s+content="([^"]*)"\s*>/g;
  let m;
  while ((m = metaRe.exec(html)) !== null) {
    const metaNode = new Node('meta', '');
    metaNode.setAttribute('name', m[1]);
    metaNode.setAttribute('content', m[2]);
    metas[m[1]] = metaNode;
  }

  // Extract all elements with id="..." in the HTML skeleton
  const tagIdRe = /<([a-zA-Z0-9]+)\b[^>]*\bid="([^"]+)"[^>]*>/g;
  while ((m = tagIdRe.exec(html)) !== null) {
    const tag = m[1].toLowerCase();
    const id = m[2];
    if (tag === 'script') continue;
    if (!registry[id]) {
      const node = new Node(tag, id);
      if (/\bhidden\b/.test(m[0])) node.hidden = true;
      doc.body.appendChild(node);
    }
  }

  // Extract all JSON islands (<script type="application/json" id="...">...</script>)
  const islandRe = /<script\s+type="application\/json"\s+id="([^"]+)">([\s\S]*?)<\/script>/g;
  const islands = Object.create(null);
  while ((m = islandRe.exec(html)) !== null) {
    const id = m[1];
    const raw = m[2].replace(/<\\\//g, '</');
    islands[id] = raw;
    const node = new Node('script', id);
    node.setAttribute('type', 'application/json');
    node.textContent = raw;
    doc.body.appendChild(node);
  }

  return { doc, islands, metas };
}

function main() {
  const args = parseArgs(process.argv);
  const html = fs.readFileSync(ARTIFACT_PATH, 'utf8');
  const policy = JSON.parse(fs.readFileSync(POLICY_PATH, 'utf8'));

  // 1. Extract the single executable script
  const execScripts = [];
  const scriptRe = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = scriptRe.exec(html)) !== null) {
    execScripts.push(match[1]);
  }
  if (execScripts.length !== 1) {
    throw new Error(`Expected 1 executable script in output/simulator.html, found ${execScripts.length}`);
  }
  const inlineScript = execScripts[0];

  // 2. B.1.2 Wrapper fixture: parse with vm.Script and locate all 37 module boundaries
  const compiledScript = new vm.Script(inlineScript, {
    filename: 'output/simulator.html#inline-script'
  });

  const boundaryRegions = [];
  const modules = policy.module_order;
  for (let i = 0; i < modules.length; i += 1) {
    const mod = modules[i];
    const sep = `/* === MODULE: ${mod.path} === */`;
    const startIdx = inlineScript.indexOf(sep);
    if (startIdx < 0) {
      throw new Error(`Missing module separator comment in artifact: ${sep}`);
    }
    const nextSep = (i + 1 < modules.length)
      ? `/* === MODULE: ${modules[i + 1].path} === */`
      : policy.single_script_wrapper.bootstrap_separator;
    const endIdx = inlineScript.indexOf(nextSep, startIdx + sep.length);
    if (endIdx < 0 || endIdx <= startIdx) {
      throw new Error(`Module boundary out of order for ${mod.path}`);
    }
    const regionText = inlineScript.slice(startIdx, endIdx).trim();
    boundaryRegions.push({
      order: mod.order,
      id: mod.id,
      path: mod.path,
      owner_task: mod.owner_task,
      start_offset: startIdx,
      end_offset: endIdx,
      inlined_bytes: Buffer.byteLength(regionText, 'utf8'),
      inlined_sha256: sha256(regionText)
    });
  }

  // 3. Execute the assembled script in an isolated VM context against the artifact DOM
  const { doc, islands } = buildArtifactDom(html);
  const sandbox = {
    console,
    document: doc,
    JSON,
    Error,
    TypeError,
    RangeError,
    SyntaxError,
    String,
    Object,
    Array,
    Math,
    Number,
    Boolean,
    RegExp,
    Date,
    BigInt,
    Set,
    Map,
    Uint8Array,
    Int32Array,
    Float64Array,
    isFinite,
    isNaN,
    parseInt,
    parseFloat,
    encodeURIComponent,
    decodeURIComponent,
    TextDecoder,
    TextEncoder,
    atob: typeof atob === 'function' ? atob : (s) => Buffer.from(String(s), 'base64').toString('binary'),
    btoa: typeof btoa === 'function' ? btoa : (s) => Buffer.from(String(s), 'binary').toString('base64')
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  compiledScript.runInContext(sandbox, { timeout: 15000 });

  // 4. Verify all 36 runtime globals + SimSmoke are present
  const expectedGlobals = [
    'SimCoverage', 'SimConventions', 'SimTerms', 'SimPRNG', 'SimFigures',
    'SimBank', 'SimGoldenVectors', 'SimLeakScan', 'SimEngines', 'SimGraphScoring',
    'SimGraphCapture', 'SimMethodEngine', 'SimMethodCards', 'SimVariantEngine',
    'SimChains', 'SimStartView', 'SimConceptDrawer', 'SimConceptMap',
    'SimHintDrawer', 'SimTheme', 'SimSession', 'SimInputsRegistry',
    'SimInputsComponents', 'SimInputsIntegration', 'SimInputs', 'SimGrading',
    'SimFeedback', 'SimAssembly', 'SimExam', 'SimStore', 'SimAnalytics',
    'SimMastery', 'SimScheduler', 'SimRemediation', 'SimRevision', 'SimPractice',
    'SimSmoke'
  ];
  const missingGlobals = expectedGlobals.filter((g) => !sandbox[g]);
  if (missingGlobals.length > 0) {
    throw new Error(`Missing runtime globals after bootstrap: ${missingGlobals.join(', ')}`);
  }

  // 5. Verify no error banners were triggered during bootstrap
  const errorBoxIds = [
    'sim-coverage-error', 'sim-conventions-error', 'sim-bank-error',
    'sim-golden-vectors-error', 'sim-terms-error', 'sim-figures-error',
    'sim-chains-error', 'sim-engines-error', 'sim-graph-scoring-error',
    'sim-mastery-error', 'sim-scheduler-error', 'sim-remediation-error',
    'sim-revision-error', 'prakse-error'
  ];
  const visibleErrors = [];
  for (const id of errorBoxIds) {
    const el = doc.getElementById(id);
    if (el && !el.hidden && el.textContent) {
      visibleErrors.push({ id, text: el.textContent });
    }
  }
  if (visibleErrors.length > 0) {
    throw new Error(`Bootstrap error banners visible: ${JSON.stringify(visibleErrors)}`);
  }

  // 6. Verify all 27 in-file smoke vectors pass and exercise the newly inlined facades
  const smokeReport = sandbox.SimSmoke.lastReport || sandbox.SimSmoke.run(doc);
  if (!smokeReport || smokeReport.status !== 'PASS' || smokeReport.failed !== 0) {
    throw new Error(`In-file smoke suite failed: ${JSON.stringify(smokeReport)}`);
  }

  const byVectorId = Object.create(null);
  for (const v of smokeReport.vectors) {
    byVectorId[v.id] = v;
  }

  const n20Vec = byVectorId['SMK-N20-BANK-GRADE-VERDICT'];
  const n22Vec = byVectorId['SMK-N22-NUMERIC-CAPTURE'];
  const n23Vec = byVectorId['SMK-N23-GRADE-FULL'];
  const n31Vec = byVectorId['SMK-N31-BUILD-CONTRACT'];

  const facadeChecks = {
    n20_bank_and_engine_in_file: Boolean(n20Vec && n20Vec.status === 'PASS' && n20Vec.details && n20Vec.details.verdict === 'correct'),
    n22_inputs_facade_exercised: Boolean(n22Vec && n22Vec.status === 'PASS' && n22Vec.details && n22Vec.details.inputs === 'facade-exercised'),
    n23_grading_facade_exercised: Boolean(n23Vec && n23Vec.status === 'PASS' && n23Vec.details && n23Vec.details.engine === 'facade-exercised'),
    n31_build_contract_vector_pass: Boolean(n31Vec && n31Vec.status === 'PASS' && n31Vec.details && n31Vec.details.coreIslands === 7 && n31Vec.details.inlinedGlobals === 36)
  };
  const failedFacades = Object.keys(facadeChecks).filter((k) => !facadeChecks[k]);
  if (failedFacades.length > 0) {
    throw new Error(`Newly inlined runtime facades were not exercised in-file: ${failedFacades.join(', ')}`);
  }

  const record = {
    schema_version: 1,
    task: 'N31',
    status: 'PASS',
    artifact_sha256: sha256(html),
    artifact_bytes: Buffer.byteLength(html, 'utf8'),
    inline_script_sha256: sha256(inlineScript),
    inline_script_bytes: Buffer.byteLength(inlineScript, 'utf8'),
    islands_loaded_count: Object.keys(islands).length,
    runtime_globals_verified_count: expectedGlobals.length,
    visible_bootstrap_errors_count: visibleErrors.length,
    wrapper_fixture_b12: {
      status: 'PASS',
      parser_engine: 'node:vm.Script',
      module_regions_mapped: boundaryRegions.length,
      first_region: boundaryRegions[0],
      last_region: boundaryRegions[boundaryRegions.length - 1],
      regions: boundaryRegions
    },
    in_file_smoke: {
      status: smokeReport.status,
      total: smokeReport.total,
      passed: smokeReport.passed,
      failed: smokeReport.failed,
      facade_checks: facadeChecks,
      n31_vector: n31Vec
    }
  };

  if (args.record) {
    fs.mkdirSync(path.dirname(args.record), { recursive: true });
    fs.writeFileSync(args.record, JSON.stringify(record, null, 2) + '\n', 'utf8');
  }

  process.stdout.write(
    `n31_runtime PASS: modules=${boundaryRegions.length}/${modules.length} globals=${expectedGlobals.length} `
    + `islands=${Object.keys(islands).length}/22 smoke=${smokeReport.passed}/${smokeReport.total}\n`
  );
}

main();
