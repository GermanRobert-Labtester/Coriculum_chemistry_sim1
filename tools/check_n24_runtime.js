#!/usr/bin/env node
/* N24 runtime & fixture harness: seeded A/B/C assembly, independent checker,
 * fairness sweep, seeded training ephemeral draws, shortage + recovery,
 * picker-to-session contract, pipeline-order guard, and built-artifact smoke.
 *
 * Usage: node tools/check_n24_runtime.js [--repo-root .] [--record PATH]
 */
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const vm = require('vm');

function parseArgs(argv) {
  const args = { repoRoot: path.resolve(__dirname, '..'), record: null };
  for (let i = 2; i < argv.length; i += 1) {
    if (argv[i] === '--repo-root') { args.repoRoot = path.resolve(argv[i + 1]); i += 1; }
    else if (argv[i] === '--record') { args.record = argv[i + 1]; i += 1; }
  }
  return args;
}

function sha256Utf8(text) {
  return crypto.createHash('sha256').update(String(text), 'utf8').digest('hex');
}

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function loadRawBank(repoRoot) {
  const bankDir = path.join(repoRoot, 'data/bank');
  const out = [];
  for (const name of fs.readdirSync(bankDir).sort()) {
    if (!name.endsWith('.json')) { continue; }
    const doc = readJson(path.join(bankDir, name));
    for (const q of (doc.questions || [])) { out.push(q); }
  }
  return out;
}

function projectBank(questions) {
  return questions.map((q) => {
    const copy = JSON.parse(JSON.stringify(q));
    if (copy.extensions && copy.extensions.data) {
      delete copy.extensions.data.draws;
      delete copy.extensions.data.derived;
      delete copy.extensions.data.review_workflow;
    }
    return copy;
  });
}

function loadSandbox(repoRoot, withVariantEngine) {
  const sandbox = {
    console,
    Math,
    JSON,
    Date,
    Array,
    Object,
    String,
    Number,
    Boolean,
    BigInt,
    RegExp,
    Error,
    Map,
    Set,
    setTimeout,
    clearTimeout,
    setInterval,
    clearInterval,
    performance: { now: () => 0 },
  };
  sandbox.globalThis = sandbox;
  sandbox.window = sandbox;
  vm.createContext(sandbox);
  const files = [
    'src/prng.js',
    'src/figure-framework.js',
    'src/compiled/session.js',
    'src/compiled/assembly.js',
    'src/compiled/exam.js',
  ];
  if (withVariantEngine) {
    files.push('src/variant-templates.js', 'src/variant-engine.js');
  }
  for (const rel of files) {
    vm.runInContext(fs.readFileSync(path.join(repoRoot, rel), 'utf8'), sandbox, { filename: rel });
  }
  return sandbox;
}

function makeDom(islands) {
  const registry = Object.create(null);
  function Node(tagName, id) {
    this.tagName = String(tagName).toUpperCase();
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
    if (id) { this.id = id; }
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(v) {
      if (this._id && registry[this._id] === this) { delete registry[this._id]; }
      this._id = String(v);
      if (this._id) { registry[this._id] = this; }
    }
  });
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() { return this.childNodes.length ? this.childNodes.map((c) => c.textContent).join('') : this._text; },
    set(v) { this.childNodes = []; this._text = String(v); }
  });
  Node.prototype.appendChild = function (c) { c.parentNode = this; this.childNodes.push(c); if (c.id) registry[c.id] = c; return c; };
  Node.prototype.removeChild = function (c) { const i = this.childNodes.indexOf(c); if (i >= 0) { this.childNodes.splice(i, 1); c.parentNode = null; } return c; };
  Node.prototype.setAttribute = function (k, v) { this.attributes[k] = String(v); if (k === 'id') this.id = v; };
  Node.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null; };
  Node.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
  Node.prototype.addEventListener = function (t, fn) { if (!this.listeners[t]) this.listeners[t] = []; this.listeners[t].push(fn); };
  Node.prototype.dispatchEvent = function (t, ev) {
    const list = this.listeners[t] || [];
    for (let i = 0; i < list.length; i += 1) { list[i](ev || { type: t }); }
    return true;
  };
  Node.prototype.focus = function () { doc.activeElement = this; };
  Node.prototype.blur = function () {};

  const doc = {
    documentElement: new Node('html'),
    body: new Node('body'),
    activeElement: null,
    createElement(tag) { return new Node(tag); },
    createElementNS(_ns, tag) { return new Node(tag); },
    getElementById(id) { return registry[id] || null; },
    querySelector(sel) {
      const m = /^meta\[name="([^"]+)"\]$/.exec(sel);
      if (m && islands.meta && islands.meta[m[1]] !== undefined) {
        const mn = new Node('meta');
        mn.setAttribute('content', islands.meta[m[1]]);
        return mn;
      }
      return null;
    },
    querySelectorAll() { return []; },
  };
  const ids = [
    ['eksamens', 'section'], ['sim-exam-status', 'p'], ['exam-entry', 'div'],
    ['exam-entry-note', 'p'], ['exam-start', 'button'], ['exam-shell', 'div'],
    ['exam-timer-bar', 'div'], ['exam-timer-value', 'span'], ['exam-timer-label', 'p'],
    ['exam-timer-threshold', 'p'], ['exam-timer-expired', 'p'], ['exam-navigator', 'div'],
    ['exam-prev', 'button'], ['exam-next', 'button'], ['exam-flag', 'button'],
    ['exam-slot-status', 'p'], ['exam-review-button', 'button'], ['exam-map', 'div'],
    ['exam-slot-host', 'div'], ['exam-review', 'section'],
    ['sakums-form-picker', 'div'], ['sakums-pick-A', 'button'], ['sakums-pick-B', 'button'],
    ['sakums-pick-C', 'button'], ['sakums-pick-SEEDED', 'button'],
    ['sakums-seed-wrap', 'div'], ['sakums-seed-input', 'input'], ['sakums-form-reason', 'p'],
    ['sakums-form-selected-summary', 'p'],
    ['exam-form-picker', 'div'], ['exam-pick-A', 'button'], ['exam-pick-B', 'button'],
    ['exam-pick-C', 'button'], ['exam-pick-SEEDED', 'button'],
    ['exam-seed-wrap', 'div'], ['exam-seed-input', 'input'], ['exam-form-shortage', 'p'],
  ];
  for (const [id, tag] of ids) {
    const n = new Node(tag, id);
    if (id === 'exam-shell') n.hidden = true;
    if (id === 'sakums-seed-input' || id === 'exam-seed-input') n.value = '101001';
    doc.body.appendChild(n);
  }
  for (const [id, text] of Object.entries(islands.scripts || {})) {
    const s = new Node('script', id);
    s.setAttribute('type', 'application/json');
    s.textContent = text;
    doc.body.appendChild(s);
  }
  return doc;
}

function captureError(fn) {
  try { fn(); return null; } catch (e) { return e; }
}

function main() {
  const args = parseArgs(process.argv);
  const root = args.repoRoot;
  const sb = loadSandbox(root, true);
  const A = sb.SimAssembly;
  const X = sb.SimExam;
  const VE = sb.SimVariantEngine;

  const rawBank = loadRawBank(root);
  const projBank = projectBank(rawBank);
  const policy = readJson(path.join(root, 'data/exam_policy.json'));
  const conventions = readJson(path.join(root, 'data/conventions.json'));
  const prngContract = readJson(path.join(root, 'data/prng_contract_vectors.json'));
  const prngDigest = sha256Utf8(A.canonicalText(prngContract));
  const buildManifest = readJson(path.join(root, 'output/build-manifest.json'));
  const bankDigest = buildManifest.bank_island.digest;

  VE.load(sb.SimFamilyTemplates, conventions);

  const results = {};

  /* 1. AC1: happy path A, B, C + independent checker + frozen disk match */
  const abc = A.assembleFormSet({
    bank: projBank,
    bank_digest: bankDigest,
    prng_contract_digest: prngDigest,
    sha256: sha256Utf8,
  });
  const ac1Checks = { shortages_zero: abc.shortages.length === 0, forms: {} };
  for (const fid of ['A', 'B', 'C']) {
    const fm = abc.manifests_by_id[fid];
    const disk = readJson(path.join(root, 'output/forms/form_' + fid + '.json'));
    const chk = A.verifyFormManifest(fm, projBank);
    const topicCounts = {};
    const topicPts = {};
    for (const s of fm.slots) {
      topicCounts[s.topic] = (topicCounts[s.topic] || 0) + 1;
      topicPts[s.topic] = (topicPts[s.topic] || 0) + s.points;
    }
    ac1Checks.forms[fid] = {
      checker_pass: chk.status === 'PASS',
      slots: fm.total_slots === 21,
      points: fm.total_points === 100,
      required_types_covered: fm.required_types_covered === true,
      matches_disk_digest: fm.manifest_digest === disk.manifest_digest,
      topic_counts: topicCounts,
      topic_points: topicPts,
      conflicts: fm.conflicts.map((c) => c.id),
    };
  }
  ac1Checks.status = ac1Checks.shortages_zero &&
    ['A', 'B', 'C'].every((f) => ac1Checks.forms[f].checker_pass && ac1Checks.forms[f].matches_disk_digest)
    ? 'PASS' : 'FAIL';
  results.ac1_happy_path = ac1Checks;

  /* 2. A.1.1: Zero-slack corner case + 1-short negative fixture */
  const t1ZeroSlack = projBank.filter((q) =>
    q.topic !== 1 || ['COL1-1-1A-A-01', 'COL1-1-1C-B-01', 'COL1-1-1D-A-01'].includes(q.question_id)
  );
  // Ensure required types (Q15 from FAM-1B replaced by FAM-3D-D/5D/6A/7A, Q04 in 1C/1D) still coverable:
  const zeroSlackRes = A.assembleForm({
    form_id: 'ZSLACK', seed: '100001', bank: t1ZeroSlack, bank_digest: bankDigest, sha256: sha256Utf8,
  });
  const zeroSlackCheck = zeroSlackRes.status === 'AVAILABLE'
    ? A.verifyFormManifest(zeroSlackRes.manifest, t1ZeroSlack) : { status: 'FAIL' };

  const oneShortBank = projBank.filter((q) => q.family_id !== 'FAM-1C');
  const oneShortRes = A.assembleForm({
    form_id: 'SHORT1', seed: '100001', bank: oneShortBank, bank_digest: bankDigest, sha256: sha256Utf8,
  });
  const truncatedManifest = JSON.parse(JSON.stringify(abc.manifests_by_id.A));
  truncatedManifest.slots = truncatedManifest.slots.slice(1); // remove S1-1 (topic 1)
  const checkerShort = A.verifyFormManifest(truncatedManifest, projBank);
  results.a11_corner_and_negative = {
    status: (zeroSlackRes.status === 'AVAILABLE' && zeroSlackCheck.status === 'PASS' &&
      oneShortRes.status === 'SHORTAGE' && oneShortRes.shortage.topic === 1 &&
      oneShortRes.shortage.slot_id === 'S1-2' && oneShortRes.shortage.count_short === 1 &&
      checkerShort.status === 'FAIL' && checkerShort.failure_reasons.some((r) => r.topic === 1))
      ? 'PASS' : 'FAIL',
    zero_slack: { status: zeroSlackRes.status, checker: zeroSlackCheck.status },
    one_short_assembly: oneShortRes.status === 'SHORTAGE' ? oneShortRes.shortage : null,
    one_short_checker: { status: checkerShort.status, errors: checkerShort.errors },
  };

  /* 3. A.1.2: 10-seed fairness sweep (30 forms) + regeneration determinism + flexible-slot sweep */
  const sweep1 = A.runFairnessSweep({ bank: projBank, bank_digest: bankDigest, prng_contract_digest: prngDigest, sha256: sha256Utf8 });
  const sweep2 = A.runFairnessSweep({ bank: projBank, bank_digest: bankDigest, prng_contract_digest: prngDigest, sha256: sha256Utf8 });
  const sweepParity = JSON.stringify(sweep1.digests_by_seed) === JSON.stringify(sweep2.digests_by_seed);

  const flexSpec = {
    slots: A.DEFAULT_SLOTS.map((s) => ({ slot_id: s.slot_id, topic: s.topic, points: s.points })),
    required_types: A.DEFAULT_REQUIRED_TYPES,
    topic_points: A.DEFAULT_TOPIC_POINTS,
    total_points: 100,
  };
  const flexSweep1 = A.runFairnessSweep({
    bank: projBank, bank_digest: bankDigest, prng_contract_digest: prngDigest, spec: flexSpec, sha256: sha256Utf8,
  });
  const flexSweep2 = A.runFairnessSweep({
    bank: projBank, bank_digest: bankDigest, prng_contract_digest: prngDigest, spec: flexSpec, sha256: sha256Utf8,
  });
  const flexParity = JSON.stringify(flexSweep1.digests_by_seed) === JSON.stringify(flexSweep2.digests_by_seed);

  results.a12_fairness_and_determinism = {
    status: (
      sweep1.forms_generated === 30 && sweep1.families_seen.length === 28 &&
      sweep1.families_missing.length === 0 && sweep1.tripled_family_slots_flexible.length === 0 &&
      sweep1.tripled_instance_slots.length === 0 && sweep1.all_checks_passed && sweepParity &&
      flexSweep1.forms_generated === 30 && flexSweep1.families_seen.length === 28 &&
      flexSweep1.tripled_family_slots_all.length === 0 && flexSweep1.all_checks_passed && flexParity
    ) ? 'PASS' : 'FAIL',
    blueprint_sweep: {
      forms_generated: sweep1.forms_generated,
      families_seen: sweep1.families_seen.length,
      families_missing: sweep1.families_missing,
      tripled_flexible_family_slots: sweep1.tripled_family_slots_flexible.length,
      tripled_instance_slots: sweep1.tripled_instance_slots.length,
      all_checks_passed: sweep1.all_checks_passed,
      double_regen_parity: sweepParity,
      digests_by_seed: sweep1.digests_by_seed,
    },
    flexible_topic_sweep: {
      forms_generated: flexSweep1.forms_generated,
      families_seen: flexSweep1.families_seen.length,
      tripled_family_slots_all: flexSweep1.tripled_family_slots_all.length,
      all_checks_passed: flexSweep1.all_checks_passed,
      double_regen_parity: flexParity,
    },
  };

  /* 4. A.1.3: 5 seeded training draws with ephemeral variants */
  const frozenSeeds = new Set(rawBank.map((q) => String(q.seed)));
  const trainingSeeds = ['101001', '101002', '101003', '101004', '101005'];
  const trainingResults = [];
  for (const tSeed of trainingSeeds) {
    const tr = A.assembleSeededTrainingForm({
      seed: tSeed,
      bank: projBank,
      bank_digest: bankDigest,
      prng_contract_digest: prngDigest,
      variant_engine: VE,
      frozen_seeds: frozenSeeds,
      ephemeral_slot_limit: 5,
      sha256: sha256Utf8,
    });
    const chk = A.verifyFormManifest(tr.manifest, Object.values(tr.instances_by_id), undefined, { allow_ephemeral: true });
    const ephSlots = tr.manifest.slots.filter((s) => s.ephemeral === true);
    trainingResults.push({
      seed: tSeed,
      status: tr.status,
      checker: chk.status,
      ephemeral_count: ephSlots.length,
      ephemeral_ids: ephSlots.map((s) => s.instance_id),
      all_eph_marked: ephSlots.every((s) => /-EPH-[0-9]+$/.test(s.instance_id) && s.ephemeral_meta && s.ephemeral_meta.persisted === false),
      manifest_digest: tr.manifest.manifest_digest,
    });
  }
  results.a13_seeded_training = {
    status: trainingResults.every((r) => r.status === 'AVAILABLE' && r.checker === 'PASS' && r.ephemeral_count === 5 && r.all_eph_marked) ? 'PASS' : 'FAIL',
    draws: trainingResults,
  };

  /* 5. B.1 / B.1.1: Shortage honesty + disabled-form UI + state-driven recovery */
  const scratchBankPending = JSON.parse(JSON.stringify(rawBank));
  for (const q of scratchBankPending) {
    if (q.family_id === 'FAM-1C') {
      q.review.content = 'pending';
      q.extensions.data.review_workflow.state = 'reviewed';
    }
  }
  const bShortage = A.assembleForm({
    form_id: 'B', seed: '100002', bank: scratchBankPending, bank_digest: bankDigest, sha256: sha256Utf8,
  });
  // Build an island where A & C are AVAILABLE and B has the pending-review shortage
  const shortageIsland = {
    schema_version: 1,
    island_id: 'sim-forms',
    owner: 'N24',
    status: 'shortage',
    bank_digest: bankDigest,
    forms: [abc.manifests_by_id.A, bShortage.shortage, abc.manifests_by_id.C],
    shortages: [bShortage.shortage],
  };
  const docShort = makeDom({
    scripts: {
      'sim-exam-policy': JSON.stringify(policy),
      'sim-forms': JSON.stringify(shortageIsland),
      'sim-bank': JSON.stringify({ island_id: 'sim-bank', questions: projBank }),
    },
  });
  const appShort = X.init(docShort, { formId: 'B' });
  const bBtnSakums = docShort.getElementById('sakums-pick-B');
  const bBtnExam = docShort.getElementById('exam-pick-B');
  const bReasonEl = docShort.getElementById('exam-form-shortage');
  const startBlocked = captureError(() => appShort.start());

  // Recovery: mark FAM-1C reviewed/accepted again
  for (const q of scratchBankPending) {
    if (q.family_id === 'FAM-1C') {
      q.review.content = 'passed';
      q.extensions.data.review_workflow.state = 'accepted';
    }
  }
  const bRecovered = A.assembleForm({
    form_id: 'B', seed: '100002', bank: scratchBankPending, bank_digest: bankDigest, sha256: sha256Utf8,
  });
  const recoveredIsland = {
    schema_version: 1,
    island_id: 'sim-forms',
    owner: 'N24',
    status: 'assembled',
    bank_digest: bankDigest,
    forms: [abc.manifests_by_id.A, bRecovered.manifest, abc.manifests_by_id.C],
    shortages: [],
  };
  const docRecov = makeDom({
    scripts: {
      'sim-exam-policy': JSON.stringify(policy),
      'sim-forms': JSON.stringify(recoveredIsland),
      'sim-bank': JSON.stringify({ island_id: 'sim-bank', questions: projBank }),
    },
  });
  const appRecov = X.init(docRecov, { formId: 'B' });
  const bBtnRecov = docRecov.getElementById('exam-pick-B');
  appRecov.start();

  results.b11_shortage_and_recovery = {
    status: (
      bShortage.status === 'SHORTAGE' &&
      bShortage.shortage.missing_family === 'FAM-1C' &&
      bShortage.shortage.slot_id === 'S1-2' &&
      bShortage.shortage.count_short === 1 &&
      bShortage.shortage.disabled_reason_lv.includes('gaida recenziju') &&
      bBtnSakums.disabled === true && bBtnSakums.getAttribute('aria-disabled') === 'true' &&
      bBtnExam.disabled === true && bBtnExam.getAttribute('aria-disabled') === 'true' &&
      bReasonEl.textContent.includes('FAM-1C') &&
      startBlocked && startBlocked.code === 'E_EXAM_FORM_DISABLED' &&
      bRecovered.status === 'AVAILABLE' &&
      bBtnRecov.disabled === false &&
      appRecov.session.getState() === 'running' &&
      appRecov.session.getFormId() === 'B'
    ) ? 'PASS' : 'FAIL',
    shortage_report: bShortage.shortage,
    disabled_start_error: startBlocked ? startBlocked.code : null,
    recovered_form_digest: bRecovered.status === 'AVAILABLE' ? bRecovered.manifest.manifest_digest : null,
  };

  /* 6. B.1.3: Picker-to-session contract for A, B, C */
  const fullIsland = {
    schema_version: 1,
    island_id: 'sim-forms',
    owner: 'N24',
    status: 'assembled',
    bank_digest: bankDigest,
    forms: [abc.manifests_by_id.A, abc.manifests_by_id.B, abc.manifests_by_id.C],
    shortages: [],
  };
  const pickerSessions = {};
  for (const fid of ['A', 'B', 'C']) {
    const d = makeDom({
      scripts: {
        'sim-exam-policy': JSON.stringify(policy),
        'sim-forms': JSON.stringify(fullIsland),
        'sim-bank': JSON.stringify({ island_id: 'sim-bank', questions: projBank }),
      },
    });
    const app = X.init(d);
    d.getElementById('sakums-pick-' + fid).dispatchEvent('click');
    d.getElementById('exam-start').dispatchEvent('click');
    const snap = app.session.snapshot();
    const want = abc.manifests_by_id[fid];
    const slotsMatch = snap.slots.length === 21 && snap.slots.every((s, idx) =>
      s.slot_id === want.slots[idx].slot_id && s.topic === want.slots[idx].topic && s.points === want.slots[idx].points
    );
    pickerSessions[fid] = {
      form_id: snap.form_id,
      slots_count: snap.slots.length,
      total_points: snap.total_points,
      slots_match_manifest: slotsMatch,
    };
  }
  results.b13_picker_to_session = {
    status: ['A', 'B', 'C'].every((f) => pickerSessions[f].form_id === f && pickerSessions[f].slots_match_manifest) ? 'PASS' : 'FAIL',
    sessions: pickerSessions,
  };

  /* 7. C.1.1: Pipeline-order refusal when bank_digest absent or stale */
  const absentDigestErr = captureError(() => A.assembleForm({
    form_id: 'A', seed: '100001', bank: projBank, bank_digest: '', sha256: sha256Utf8,
  }));
  const staleDigestErr = captureError(() => A.assembleForm({
    form_id: 'A', seed: '100001', bank: projBank, bank_digest: 'stale', expected_bank_digest: bankDigest, sha256: sha256Utf8,
  }));
  results.c11_pipeline_order_refusal = {
    status: (absentDigestErr && absentDigestErr.code === 'E_ASSEMBLY_BANK_UNVERIFIED' &&
      staleDigestErr && staleDigestErr.code === 'E_ASSEMBLY_BANK_UNVERIFIED') ? 'PASS' : 'FAIL',
    absent_error: absentDigestErr ? absentDigestErr.code : null,
    stale_error: staleDigestErr ? staleDigestErr.code : null,
  };

  /* 8. C.1.2: Built artifact smoke vector SMK-N24-ASSEMBLY-DRAW */
  const html = fs.readFileSync(path.join(root, 'output/simulator.html'), 'utf8');
  const scriptMatches = [];
  const reScript = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = reScript.exec(html)) !== null) {
    const attrs = m[1];
    const idMatch = /\bid="([^"]+)"/.exec(attrs);
    const typeMatch = /\btype="([^"]+)"/.exec(attrs);
    scriptMatches.push({ id: idMatch ? idMatch[1] : null, type: typeMatch ? typeMatch[1] : '', text: m[2] });
  }
  const islandScripts = Object.create(null);
  let execText = '';
  for (const sm of scriptMatches) {
    if (sm.type === 'application/json' && sm.id) { islandScripts[sm.id] = sm.text; }
    else if (!sm.type) { execText = sm.text; }
  }
  const metaTags = Object.create(null);
  const reMeta = /<meta\s+name="([^"]+)"\s+content="([^"]*)"/gi;
  while ((m = reMeta.exec(html)) !== null) { metaTags[m[1]] = m[2]; }

  const artDoc = makeDom({ scripts: islandScripts, meta: metaTags });
  // Ensure every node referenced by shell on-load init exists
  ['sakums-oficialas-temas', 'coverage-nav', 'coverage-list', 'coverage-total', 'chain-index',
   'sim-coverage-error', 'sim-conventions-error', 'sim-bank-error', 'sim-golden-vectors-error',
   'sim-terms-error', 'sim-figures-error', 'sim-chains-error', 'sim-engines-error',
   'sim-graph-scoring-error', 'sim-conventions-status', 'sim-bank-status', 'sim-golden-vectors-status',
   'sim-terms-status', 'sim-figures-status', 'sim-chains-status', 'sim-smoke-status',
   'theme-toggle', 'theme-status', 'karte'].forEach((id) => {
    if (!artDoc.getElementById(id)) {
      const el = artDoc.createElement('div');
      el.id = id;
      artDoc.body.appendChild(el);
    }
  });
  const artSb = {
    document: artDoc,
    console, Math, JSON, Date, Array, Object, String, Number, Boolean, BigInt, RegExp, Error, Map, Set,
    atob, btoa, TextDecoder, TextEncoder,
    setTimeout, clearTimeout, setInterval, clearInterval,
    performance: { now: () => 0 },
  };
  artSb.globalThis = artSb;
  artSb.window = artSb;
  vm.createContext(artSb);
  vm.runInContext(execText, artSb, { filename: 'output/simulator.html#script' });
  const smokeReport = artSb.SimSmoke ? artSb.SimSmoke.lastReport : null;
  const n24Vec = smokeReport && Array.isArray(smokeReport.vectors)
    ? smokeReport.vectors.find((v) => v.id === 'SMK-N24-ASSEMBLY-DRAW') : null;

  results.c12_built_artifact_smoke = {
    status: (smokeReport && smokeReport.status === 'PASS' && n24Vec && n24Vec.status === 'PASS' &&
      n24Vec.details && n24Vec.details.miniBankFamilies === 6 && n24Vec.details.independentCheck === 'PASS')
      ? 'PASS' : 'FAIL',
    smoke_total: smokeReport ? smokeReport.total : 0,
    smoke_passed: smokeReport ? smokeReport.passed : 0,
    n24_vector: n24Vec,
  };

  const overall = Object.values(results).every((r) => r.status === 'PASS') ? 'PASS' : 'FAIL';
  const out = {
    schema_version: 1,
    owner: 'N24',
    status: overall,
    checks: results,
  };

  if (args.record) {
    const recPath = path.isAbsolute(args.record) ? args.record : path.join(root, args.record);
    fs.mkdirSync(path.dirname(recPath), { recursive: true });
    fs.writeFileSync(recPath, JSON.stringify(out, null, 2) + '\n', 'utf8');
  }
  process.stdout.write(JSON.stringify(out, null, 2) + '\n');
  process.exit(overall === 'PASS' ? 0 : 1);
}

main();
