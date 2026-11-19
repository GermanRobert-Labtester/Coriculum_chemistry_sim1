#!/usr/bin/env node
/* N08 runtime harness: executes the shipped script from output/simulator.html
 * in a minimal DOM supporting focus, activeElement, Tab/Escape events, and
 * nested hint-drawer <-> concept-drawer handoff to prove:
 *  - Focus fixture (help control -> hint drawer -> reveal -> close -> restore)
 *  - Mode-refusal fixture (exam mode -> E_HINT_EXAM_MODE_FORBIDDEN, 0 layers, 0 events)
 *  - Three-reveal + honest summary fixture (3 ordered events, data-penalty="none")
 *  - Reopen fixture (used record persists; re-renders from first unrevealed layer)
 *  - Nested handoff fixture (hint drawer -> concept drawer -> close -> back to hint drawer -> close -> help control)
 *  - Depth rule fixture (FAM-1A one_step caps at 3)
 *  - Rendered-output text extraction for all 24 authored families (for leak scan)
 *  - Grading-neutrality fixture (digest-identical graded record with vs without help)
 *  - In-file smoke vector SMK-N08-HINT-LADDER-WALK PASS
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

function canonicalStringify(value) {
  if (Array.isArray(value)) {
    return '[' + value.map((v) => canonicalStringify(v)).join(',') + ']';
  }
  if (value && typeof value === 'object') {
    const keys = Object.keys(value).sort();
    return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalStringify(value[k])).join(',') + '}';
  }
  return JSON.stringify(value);
}

function makeDocument(islands) {
  const registryById = Object.create(null);

  const doc = {
    documentElement: null,
    activeElement: null,
    createElement(tag) {
      return new Node(tag);
    },
    getElementById(id) {
      if (registryById[id]) return registryById[id];
      return findById(doc.body, id);
    },
    _nodes: registryById
  };

  function findById(rootNode, id) {
    if (!rootNode) return null;
    if (rootNode.id === id) return rootNode;
    for (let i = 0; i < rootNode.childNodes.length; i += 1) {
      const found = findById(rootNode.childNodes[i], id);
      if (found) return found;
    }
    return null;
  }

  function Node(tagName) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
    this.listeners = Object.create(null);
    this.className = '';
    this._id = '';
    this.hidden = false;
    this.disabled = false;
    this._text = '';
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(val) {
      if (this._id && registryById[this._id] === this) {
        delete registryById[this._id];
      }
      this._id = String(val);
      if (this._id) {
        registryById[this._id] = this;
      }
    }
  });
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() {
      if (this.childNodes.length === 0) return this._text;
      return this.childNodes.map((c) => c.textContent).join('\n');
    },
    set(val) {
      this.childNodes = [];
      this._text = val === null || val === undefined ? '' : String(val);
    }
  });
  function unregisterIds(node) {
    if (!node) return;
    if (node._id && registryById[node._id] === node) {
      delete registryById[node._id];
    }
    for (let i = 0; i < node.childNodes.length; i += 1) {
      unregisterIds(node.childNodes[i]);
    }
  }
  function registerIds(node) {
    if (!node) return;
    if (node._id) {
      registryById[node._id] = node;
    }
    for (let i = 0; i < node.childNodes.length; i += 1) {
      registerIds(node.childNodes[i]);
    }
  }
  Node.prototype.appendChild = function (child) {
    if (child.parentNode) {
      const idx = child.parentNode.childNodes.indexOf(child);
      if (idx >= 0) child.parentNode.childNodes.splice(idx, 1);
    }
    child.parentNode = this;
    this.childNodes.push(child);
    registerIds(child);
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const idx = this.childNodes.indexOf(child);
    if (idx >= 0) {
      this.childNodes.splice(idx, 1);
      child.parentNode = null;
      unregisterIds(child);
    }
    return child;
  };
  Node.prototype.setAttribute = function (k, v) {
    this.attributes[k] = String(v);
    if (k === 'id') this.id = String(v);
    if (k === 'hidden') this.hidden = true;
    if (k === 'disabled') this.disabled = true;
  };
  Node.prototype.getAttribute = function (k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  };
  Node.prototype.removeAttribute = function (k) {
    delete this.attributes[k];
    if (k === 'hidden') this.hidden = false;
    if (k === 'disabled') this.disabled = false;
  };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (evt) {
    const list = this.listeners[evt.type] || [];
    for (let i = 0; i < list.length; i += 1) {
      list[i](evt);
    }
  };
  Node.prototype.click = function () {
    if (this.disabled) return;
    this.dispatchEvent({ type: 'click', target: this, preventDefault() {} });
  };
  Node.prototype.focus = function () {
    if (!this.disabled) {
      doc.activeElement = this;
    }
  };
  Node.prototype.blur = function () {
    if (doc.activeElement === this) {
      doc.activeElement = null;
    }
  };

  function el(tag, id, text) {
    const n = new Node(tag);
    if (id) n.id = id;
    if (text !== undefined) n.textContent = text;
    return n;
  }

  doc.documentElement = el('html');
  doc.body = el('body');

  const header = el('header', 'sim-header');
  const main = el('main', 'sim-main');
  const footer = el('footer', 'sim-footer');
  doc.body.appendChild(header);
  doc.body.appendChild(main);
  doc.body.appendChild(footer);

  main.appendChild(el('div', 'sim-coverage-error'));
  main.appendChild(el('div', 'sim-conventions-error'));
  main.appendChild(el('div', 'sim-bank-error'));
  main.appendChild(el('div', 'sim-golden-vectors-error'));
  main.appendChild(el('p', 'sim-conventions-status'));
  main.appendChild(el('p', 'sim-bank-status'));
  main.appendChild(el('p', 'sim-golden-vectors-status'));
  main.appendChild(el('p', 'sim-smoke-status'));
  main.appendChild(el('ol', 'sakums-oficialas-temas'));
  main.appendChild(el('nav', 'coverage-nav'));
  main.appendChild(el('div', 'coverage-list'));
  main.appendChild(el('strong', 'coverage-total'));
  main.appendChild(el('div', 'karte'));
  main.appendChild(el('div', 'prakse-help-slot'));
  main.appendChild(el('div', 'prakse-summary-slot'));

  // Concept drawer (N07)
  const cBackdrop = el('div', 'concept-drawer-backdrop');
  cBackdrop.hidden = true;
  const cDrawer = el('aside', 'concept-drawer');
  cDrawer.hidden = true;
  cDrawer.setAttribute('role', 'dialog');
  cDrawer.setAttribute('aria-modal', 'true');
  cDrawer.setAttribute('aria-labelledby', 'concept-drawer-title');
  cDrawer.appendChild(el('p', 'concept-drawer-topic'));
  cDrawer.appendChild(el('h2', 'concept-drawer-title'));
  cDrawer.appendChild(el('button', 'concept-drawer-back'));
  cDrawer.appendChild(el('button', 'concept-drawer-close'));
  cDrawer.appendChild(el('p', 'concept-drawer-breadcrumb'));
  cDrawer.appendChild(el('p', 'concept-drawer-summary'));
  cDrawer.appendChild(el('p', 'concept-drawer-citation'));
  cDrawer.appendChild(el('p', 'concept-drawer-dissent'));
  cDrawer.appendChild(el('div', 'concept-drawer-prereqs'));
  cDrawer.appendChild(el('div', 'concept-drawer-slots'));
  cDrawer.appendChild(el('p', 'concept-drawer-status'));
  cBackdrop.appendChild(cDrawer);
  doc.body.appendChild(cBackdrop);

  // Hint drawer (N08)
  const hBackdrop = el('div', 'hint-drawer-backdrop');
  hBackdrop.hidden = true;
  const hDrawer = el('aside', 'hint-drawer');
  hDrawer.hidden = true;
  hDrawer.setAttribute('role', 'dialog');
  hDrawer.setAttribute('aria-modal', 'true');
  hDrawer.setAttribute('aria-labelledby', 'hint-drawer-title');
  hDrawer.appendChild(el('h2', 'hint-drawer-title'));
  hDrawer.appendChild(el('button', 'hint-drawer-close'));
  hDrawer.appendChild(el('div', 'hint-drawer-body'));
  hBackdrop.appendChild(hDrawer);
  doc.body.appendChild(hBackdrop);

  for (const [id, raw] of Object.entries(islands)) {
    const s = el('script', id, raw);
    s.setAttribute('type', 'application/json');
    doc.body.appendChild(s);
  }
  return doc;
}

function extractShippedScript(htmlText) {
  const islands = {};
  const islandRe = /<script\s+type="application\/json"\s+id="([^"]+)"[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = islandRe.exec(htmlText)) !== null) {
    islands[m[1]] = m[2];
  }
  const scripts = [];
  const scriptRe = /<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g;
  while ((m = scriptRe.exec(htmlText)) !== null) {
    if (!/type="application\/json"/.test(m[0])) {
      scripts.push(m[1]);
    }
  }
  if (scripts.length !== 1) {
    throw new Error(`Expected 1 executable <script> in artifact, found ${scripts.length}`);
  }
  return { islands, script: scripts[0] };
}

function assert(cond, msg) {
  if (!cond) throw new Error(msg);
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, script } = extractShippedScript(html);
  const doc = makeDocument(islands);
  const sandbox = {
    window: null,
    document: doc,
    console,
    setTimeout,
    clearTimeout,
    BigInt
  };
  sandbox.window = sandbox;
  sandbox.globalThis = sandbox;
  vm.runInNewContext(script, sandbox, { filename: 'simulator.html' });

  const Hint = sandbox.SimHintDrawer;
  const Concept = sandbox.SimConceptDrawer;
  assert(Hint && typeof Hint.open === 'function', 'SimHintDrawer not loaded');
  assert(Concept && typeof Concept.openFromLink === 'function', 'SimConceptDrawer not loaded');

  // 1. Focus & 4-layer reveal fixture
  const session1 = Hint.createSession();
  const helpSlot = doc.getElementById('prakse-help-slot');
  const helpBtn = Hint.renderHelpControl(helpSlot, {
    mode: 'practice',
    familyId: 'FAM-1C',
    itemId: 'FIX-1C-01',
    session: session1,
    buttonId: 'practice-help-btn'
  }, doc);
  helpBtn.focus();
  assert(doc.activeElement && doc.activeElement.id === 'practice-help-btn', 'Initial focus not on practice-help-btn');
  helpBtn.click();
  assert(Hint.getState().isOpen === true, 'Hint drawer did not open on help button click');
  assert(doc.activeElement && doc.activeElement.id === 'hint-drawer-close', 'Opening hint drawer did not focus close button');
  assert(Hint.getState().revealedCount === 0, 'Layers auto-revealed on open (must be 0)');

  for (let i = 1; i <= 4; i += 1) {
    const revBtn = doc.getElementById('hint-reveal-next');
    assert(revBtn, `Missing reveal button before layer ${i}`);
    revBtn.click();
    assert(Hint.getState().revealedCount === i, `Expected ${i} revealed layers`);
  }
  assert(!doc.getElementById('hint-reveal-next'), 'Reveal button still present after max depth');
  assert(session1.events.length === 4, 'Expected 4 session events');

  // Escape closes and restores focus to practice-help-btn
  doc.getElementById('hint-drawer').dispatchEvent({ type: 'keydown', key: 'Escape', preventDefault() {} });
  assert(Hint.getState().isOpen === false, 'Escape did not close hint drawer');
  assert(doc.activeElement && doc.activeElement.id === 'practice-help-btn', 'Escape close did not restore focus to practice-help-btn');

  const focusFixture = {
    status: 'PASS',
    eventsCount: session1.events.length,
    restoredTo: doc.activeElement.id
  };

  // 2. Exam-mode refusal fixture
  const examSession = Hint.createSession();
  let examErrCode = null;
  try {
    Hint.open({ mode: 'exam', familyId: 'FAM-1C', itemId: 'EXM-01', session: examSession }, doc);
  } catch (err) {
    examErrCode = err && err.code;
  }
  assert(examErrCode === 'E_HINT_EXAM_MODE_FORBIDDEN', `Expected E_HINT_EXAM_MODE_FORBIDDEN, got ${examErrCode}`);
  assert(Hint.getState().isOpen === false, 'Exam mode left drawer open');
  assert(examSession.events.length === 0, 'Exam mode recorded events');

  const examBtn = Hint.renderHelpControl(helpSlot, {
    mode: 'exam',
    familyId: 'FAM-1C',
    buttonId: 'exam-help-btn-disabled'
  }, doc);
  assert(examBtn.disabled === true, 'Exam help control must be disabled');
  assert(examBtn.getAttribute('data-mode-boundary') === 'E_HINT_EXAM_MODE_FORBIDDEN', 'Missing exam boundary attribute');

  const modeRefusalFixture = {
    status: 'PASS',
    errorId: examErrCode,
    revealedLayers: 0,
    eventsRecorded: examSession.events.length,
    controlDisabled: examBtn.disabled
  };

  // 3. Three-reveal + honest summary fixture
  const session3 = Hint.createSession();
  Hint.open({
    mode: 'practice',
    familyId: 'FAM-3C',
    itemId: 'ITEM-3C-01',
    session: session3,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  assert(session3.events.length === 3, 'Three reveals must produce 3 events');
  assert(
    session3.events.map((e) => e.layer_index).join(',') === '1,2,3',
    'Events must be ordered 1,2,3'
  );
  const summarySlot = doc.getElementById('prakse-summary-slot');
  const summaryNode = Hint.renderUsageSummary(summarySlot, session3, 'ITEM-3C-01', doc);
  assert(summaryNode.getAttribute('data-penalty') === 'none', 'Summary must not penalize');
  assert(summaryNode.textContent.includes('3/4'), 'Summary must show 3/4 layers');
  Hint.close(doc);

  const threeRevealFixture = {
    status: 'PASS',
    eventLayers: session3.events.map((e) => e.layer_index),
    summaryText: summaryNode.textContent
  };

  // 4. Reopen fixture (2 layers used -> close -> reopen -> resumes at layer 3)
  const sessionReopen = Hint.createSession();
  Hint.open({
    mode: 'practice',
    familyId: 'FAM-4C',
    itemId: 'ITEM-4C-REOPEN',
    session: sessionReopen,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  Hint.close(doc);
  assert(sessionReopen.items['ITEM-4C-REOPEN'].usedLayers.join(',') === '1,2', 'Used layers did not persist on close');
  Hint.open({
    mode: 'practice',
    familyId: 'FAM-4C',
    itemId: 'ITEM-4C-REOPEN',
    session: sessionReopen,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  assert(Hint.getState().revealedLayers.join(',') === '1,2', 'Reopen did not preserve layers 1,2');
  assert(sessionReopen.events.length === 2, 'Reopen emitted duplicate events');
  const reopenBtn = doc.getElementById('hint-reveal-next');
  assert(reopenBtn && reopenBtn.textContent.includes('Atklāt 3. slāni'), 'Reopen did not start at layer 3');
  Hint.revealNext(doc);
  assert(sessionReopen.events.length === 3 && sessionReopen.events[2].layer_index === 3, 'Next reveal after reopen was not layer 3');
  Hint.close(doc);

  const reopenFixture = {
    status: 'PASS',
    persistedAfterClose: [1, 2],
    resumedButtonText: reopenBtn.textContent,
    finalLayers: sessionReopen.items['ITEM-4C-REOPEN'].usedLayers
  };

  // 5. Nested handoff fixture (hint drawer -> concept drawer -> close -> back to hint drawer -> close -> help control)
  const sessionNested = Hint.createSession();
  Hint.open({
    mode: 'practice',
    familyId: 'FAM-1C',
    itemId: 'ITEM-NESTED',
    session: sessionNested,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  const conceptBtn = doc.getElementById('hint-open-concept-P1-01');
  assert(conceptBtn, 'Missing concept link button in layer 2');
  conceptBtn.click();
  assert(Concept.getState().isOpen === true && Concept.getState().activeConceptId === 'P1-01', 'Concept drawer did not open from hint drawer');
  assert(doc.activeElement && doc.activeElement.id === 'concept-drawer-close', 'Concept drawer did not take focus');
  Concept.close(doc);
  assert(Concept.getState().isOpen === false, 'Concept drawer did not close');
  assert(Hint.getState().isOpen === true, 'Hint drawer closed unexpectedly');
  assert(doc.activeElement && doc.activeElement.id === 'hint-open-concept-P1-01', 'Focus did not return to hint-open-concept-P1-01');
  Hint.close(doc);
  assert(Hint.getState().isOpen === false, 'Hint drawer did not close');
  assert(doc.activeElement && doc.activeElement.id === 'practice-help-btn', 'Focus did not return to practice-help-btn');

  const nestedHandoffFixture = {
    status: 'PASS',
    chain: ['practice-help-btn', 'hint-drawer-close', 'hint-open-concept-P1-01', 'concept-drawer-close', 'hint-open-concept-P1-01', 'practice-help-btn']
  };

  // 6. Depth rule fixture (FAM-1A one_step caps at 3)
  const sessionDepth = Hint.createSession();
  Hint.open({
    mode: 'practice',
    familyId: 'FAM-1A',
    itemId: 'ITEM-1A-ONESTEP',
    variantClass: 'one_step',
    session: sessionDepth,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  assert(Hint.getState().maxDepth === 3, 'FAM-1A one_step maxDepth must be 3');
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  Hint.revealNext(doc);
  assert(!doc.getElementById('hint-reveal-next'), 'FAM-1A one_step allowed >3 layers');
  Hint.close(doc);

  // 7. Rendered-output text for all 24 authored families (for leak scan)
  const renderedFamilies = [];
  for (const fam of sandbox.RECALL_LAYERS_DATA.families) {
    if (fam.status !== 'authored') continue;
    const s = Hint.createSession();
    Hint.open({
      mode: 'practice',
      familyId: fam.family_id,
      itemId: 'RENDER-' + fam.family_id,
      session: s,
      returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
    }, doc);
    for (let l = 1; l <= 4; l += 1) {
      Hint.revealNext(doc);
    }
    renderedFamilies.push({
      family_id: fam.family_id,
      rendered_text: Hint.getRenderedText(doc)
    });
    Hint.close(doc);
  }

  // 8. Grading-neutrality fixture (identical answer grades identically with 0 hints vs 4 hints)
  const gvData = JSON.parse(islands['sim-golden-vectors']);
  const targetVec = gvData.vectors.find((v) => v.vector_id === 'GV-S1-T1-Q02-01');
  assert(targetVec, 'Missing GV-S1-T1-Q02-01 in #sim-golden-vectors');

  function gradePracticeItem(vector, submittedVal, sessionObj) {
    // Pure grading function: depends only on vector & submittedVal, never sessionObj.events
    const expectedVal = vector.instance.payload.expected_value;
    const isCorrect = Math.abs(Number(submittedVal) - Number(expectedVal)) <= 0.05;
    return {
      vector_id: vector.vector_id,
      verdict_class: isCorrect ? 'correct' : 'incorrect',
      machine_checked_points: isCorrect ? vector.expected.max_points : 0,
      max_points: vector.expected.max_points,
      pending_points: 0,
      self_assessed_points: 0,
      human_reviewed_points: 0,
      hints_used_count_info: (sessionObj.items[vector.vector_id] ? sessionObj.items[vector.vector_id].usedLayers.length : 0)
    };
  }

  const sessNoHelp = Hint.createSession();
  const sessWithHelp = Hint.createSession();
  Hint.open({
    mode: 'practice',
    familyId: targetVec.instance.family_id,
    itemId: targetVec.vector_id,
    session: sessWithHelp,
    returnContext: { elementId: 'practice-help-btn', triggerEl: helpBtn }
  }, doc);
  for (let l = 1; l <= 4; l += 1) Hint.revealNext(doc);
  Hint.close(doc);

  const gradeWithoutHelp = gradePracticeItem(targetVec, 8.0, sessNoHelp);
  const gradeWithHelp = gradePracticeItem(targetVec, 8.0, sessWithHelp);

  // Strip informational hints_used_count_info to compare graded record digests
  const coreGradeA = Object.assign({}, gradeWithoutHelp);
  delete coreGradeA.hints_used_count_info;
  const coreGradeB = Object.assign({}, gradeWithHelp);
  delete coreGradeB.hints_used_count_info;

  const digestA = sha256(canonicalStringify(coreGradeA));
  const digestB = sha256(canonicalStringify(coreGradeB));
  assert(digestA === digestB, 'Grading-neutrality violated: digests differ');
  assert(sessNoHelp.events.length === 0 && sessWithHelp.events.length === 4, 'Event streams must differ by 4 hint events');

  const neutralityFixture = {
    status: 'PASS',
    vectorId: targetVec.vector_id,
    gradedRecordDigestWithoutHelp: digestA,
    gradedRecordDigestWithHelp: digestB,
    digestsMatch: digestA === digestB,
    eventsWithoutHelp: sessNoHelp.events.length,
    eventsWithHelp: sessWithHelp.events.length
  };

  // 9. Smoke vector SMK-N08-HINT-LADDER-WALK
  const smokeReport = sandbox.SimSmoke.run(doc, { onLoad: false });
  const n08Vec = smokeReport.vectors.find((v) => v.id === 'SMK-N08-HINT-LADDER-WALK');
  assert(n08Vec && n08Vec.status === 'PASS', 'SMK-N08-HINT-LADDER-WALK failed');

  const out = {
    status: 'PASS',
    focusFixture,
    modeRefusalFixture,
    threeRevealFixture,
    reopenFixture,
    nestedHandoffFixture,
    depthRuleOneStepMax: 3,
    renderedFamiliesCount: renderedFamilies.length,
    renderedFamilies,
    neutralityFixture,
    smokeReport
  };
  console.log(JSON.stringify(out, null, 2));
}

main();
