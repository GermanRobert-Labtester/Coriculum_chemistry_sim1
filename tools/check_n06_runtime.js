#!/usr/bin/env node
/* N06 runtime harness: executes the shipped script from output/simulator.html
 * in a minimal DOM to prove:
 *  - Start view official 7-topic list single-sourced from #sim-coverage
 *  - Objectives view renders all 64 outcomes verbatim (9,10,11,11,10,8,5)
 *    with topic links to #karte-tema-N (N07) and #prakse-tema-N (N30)
 *  - Single-sourcing: editing #sim-coverage updates start + nav + objectives
 *  - Markup-character escaping corner case (N35): <img...> & <b> renders as text
 *  - Theme toggle state machine: click, keyboard Space/Enter, persist/restore
 *    on opted-in store, and graceful no-store degradation
 *  - In-file smoke vector (SMK-N06-COVERAGE-COUNTS) PASS and mismatch catch
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

function makeDocument(islands) {
  const nodes = Object.create(null);

  function Node(tagName) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
    this.listeners = Object.create(null);
    this.className = '';
    this.id = '';
    this.hidden = false;
    this._text = '';
  }
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() {
      if (this.childNodes.length) {
        return this.childNodes.map((child) => child.textContent).join('');
      }
      return this._text;
    },
    set(value) {
      this.childNodes = [];
      this._text = String(value);
    }
  });
  Node.prototype.appendChild = function (child) {
    child.parentNode = this;
    this.childNodes.push(child);
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const index = this.childNodes.indexOf(child);
    if (index >= 0) {
      this.childNodes.splice(index, 1);
      child.parentNode = null;
    }
    return child;
  };
  Node.prototype.setAttribute = function (name, value) {
    this.attributes[name] = String(value);
  };
  Node.prototype.getAttribute = function (name) {
    return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
  };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (type, eventObj) {
    const list = this.listeners[type] || [];
    for (let i = 0; i < list.length; i += 1) {
      list[i](eventObj || {});
    }
  };

  const docElement = new Node('html');
  const spec = [
    ['sim-coverage', 'script'],
    ['sim-conventions', 'script'],
    ['sim-bank', 'script'],
    ['sim-golden-vectors', 'script'],
    ['sakums-oficialas-temas', 'ol'],
    ['coverage-nav', 'nav'],
    ['coverage-list', 'div'],
    ['coverage-total', 'strong'],
    ['theme-toggle', 'button'],
    ['theme-status', 'p'],
    ['sim-smoke-status', 'p'],
    ['sim-coverage-error', 'div'],
    ['sim-conventions-error', 'div'],
    ['sim-conventions-status', 'p'],
    ['sim-bank-error', 'div'],
    ['sim-bank-status', 'p'],
    ['sim-golden-vectors-error', 'div'],
    ['sim-golden-vectors-status', 'p']
  ];
  spec.forEach(([id, tag]) => {
    const node = new Node(tag);
    node.id = id;
    if (id.endsWith('-error') || id.endsWith('-status')) {
      if (id !== 'theme-status') node.hidden = true;
    }
    nodes[id] = node;
  });

  Object.keys(islands).forEach((id) => {
    if (nodes[id]) {
      nodes[id].textContent = islands[id];
    }
  });

  return {
    documentElement: docElement,
    createElement(tag) { return new Node(tag); },
    getElementById(id) { return nodes[id] || null; },
    _nodes: nodes
  };
}

function extractArtifact(html) {
  const islandIds = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-golden-vectors'];
  const islands = {};
  islandIds.forEach((id) => {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '">([\\s\\S]*?)</script>');
    const m = re.exec(html);
    if (!m) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = m[1].replace(/<\\\//g, '</');
  });
  const scripts = [];
  const pattern = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    scripts.push(match[1]);
  }
  if (scripts.length !== 1) {
    throw new Error('Expected 1 executable script in output/simulator.html, found ' + scripts.length);
  }
  return { islands, bootstrap: scripts[0] };
}

function runInVm(islands, bootstrap) {
  const document = makeDocument(islands);
  const sandbox = { document, console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document, sandbox };
}

function collectLinks(node) {
  const out = [];
  if (node.tagName === 'A' && node.getAttribute('href')) {
    out.push(node.getAttribute('href'));
  }
  for (let i = 0; i < node.childNodes.length; i += 1) {
    out.push(...collectLinks(node.childNodes[i]));
  }
  return out;
}

function findOutcomeLi(node, id) {
  if (node.id === id) return node;
  for (let i = 0; i < node.childNodes.length; i += 1) {
    const found = findOutcomeLi(node.childNodes[i], id);
    if (found) return found;
  }
  return null;
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, bootstrap } = extractArtifact(html);
  const coverageObj = JSON.parse(islands['sim-coverage']);
  const checks = {};
  const failures = [];

  // 1. Baseline render & verbatim check
  const base = runInVm(islands, bootstrap);
  const startTopicsText = base.document.getElementById('sakums-oficialas-temas').textContent;
  const listNode = base.document.getElementById('coverage-list');
  const navNode = base.document.getElementById('coverage-nav');
  const links = collectLinks(listNode);

  let verbatimMatches = 0;
  for (const outcome of coverageObj.outcomes) {
    const li = findOutcomeLi(listNode, 'rezultats-' + outcome.id);
    if (li && li.textContent.indexOf(outcome.statement_lv) >= 0) {
      verbatimMatches += 1;
    }
  }
  const perTopicRendered = listNode.childNodes.map((sec) => {
    const ol = sec.childNodes.find((c) => c.tagName === 'OL');
    return ol ? ol.childNodes.length : 0;
  });
  const hasMapAndPracticeLinks = [1, 2, 3, 4, 5, 6, 7].every(
    (t) => links.includes('#karte-tema-' + t) && links.includes('#prakse-tema-' + t)
  );
  checks.baseline = {
    start_topics_count: base.document.getElementById('sakums-oficialas-temas').childNodes.length,
    nav_topics_count: navNode.childNodes[0] ? navNode.childNodes[0].childNodes.length : 0,
    per_topic_counts: perTopicRendered,
    verbatim_outcomes_matched: verbatimMatches,
    has_all_map_and_practice_links: hasMapAndPracticeLinks,
    smoke_report: base.sandbox.SimSmoke.lastReport
  };
  if (checks.baseline.start_topics_count !== 7) failures.push('start screen did not render 7 topics');
  if (checks.baseline.verbatim_outcomes_matched !== 64) failures.push('expected 64 verbatim outcomes');
  if (JSON.stringify(perTopicRendered) !== JSON.stringify([9, 10, 11, 11, 10, 8, 5])) {
    failures.push('per-topic counts mismatch: ' + JSON.stringify(perTopicRendered));
  }
  if (!hasMapAndPracticeLinks) failures.push('missing topic links to #karte-tema-N or #prakse-tema-N');
  if (!base.sandbox.SimSmoke.lastReport || base.sandbox.SimSmoke.lastReport.status !== 'PASS') {
    failures.push('in-file smoke vector failed on baseline');
  }

  // 2. Single-sourcing across start, nav and objectives
  const origTopic = coverageObj.topics[0].name_lv;
  const origStmt = coverageObj.outcomes[0].statement_lv;
  const topicSentinel = 'SENTINELA TĒMA N06';
  const stmtSentinel = 'SENTINELA REZULTĀTS N06';
  const editedCoverage = JSON.parse(islands['sim-coverage']);
  editedCoverage.topics[0].name_lv = topicSentinel;
  editedCoverage.outcomes[0].statement_lv = stmtSentinel;
  const editedIslands = Object.assign({}, islands, { 'sim-coverage': JSON.stringify(editedCoverage) });
  const edited = runInVm(editedIslands, bootstrap);
  const eStart = edited.document.getElementById('sakums-oficialas-temas').textContent;
  const eNav = edited.document.getElementById('coverage-nav').textContent;
  const eList = edited.document.getElementById('coverage-list').textContent;
  checks.single_source = {
    start_changed: eStart.includes(topicSentinel) && !eStart.includes(origTopic),
    nav_changed: eNav.includes(topicSentinel) && !eNav.includes(origTopic),
    list_topic_changed: eList.includes(topicSentinel) && !eList.includes(origTopic),
    list_statement_changed: eList.includes(stmtSentinel) && !eList.includes(origStmt)
  };
  if (!checks.single_source.start_changed || !checks.single_source.nav_changed ||
      !checks.single_source.list_topic_changed || !checks.single_source.list_statement_changed) {
    failures.push('single-sourcing failed across start/nav/objectives');
  }

  // 3. Markup-significant characters corner case (N35 escaping discipline)
  const xssPayload = '<img src=x onerror=alert(1)> & <b>skābe</b>';
  const markupCoverage = JSON.parse(islands['sim-coverage']);
  markupCoverage.outcomes[0].statement_lv = xssPayload;
  const markupVm = runInVm(Object.assign({}, islands, { 'sim-coverage': JSON.stringify(markupCoverage) }), bootstrap);
  const markupLi = findOutcomeLi(markupVm.document.getElementById('coverage-list'), 'rezultats-P1-01');
  const markupChildTags = markupLi ? markupLi.childNodes.map((c) => c.tagName) : [];
  checks.markup_escaping = {
    payload: xssPayload,
    rendered_verbatim_text: Boolean(markupLi && markupLi.textContent.includes(xssPayload)),
    child_tags: markupChildTags,
    no_injected_tags: JSON.stringify(markupChildTags) === JSON.stringify(['SPAN', 'SPAN'])
  };
  if (!checks.markup_escaping.rendered_verbatim_text || !checks.markup_escaping.no_injected_tags) {
    failures.push('markup-significant statement was not safely rendered as text');
  }

  // 4. Theme toggle state machine: click, keyboard, persist, restore, no-store degradation
  const btn = base.document.getElementById('theme-toggle');
  const htmlEl = base.document.documentElement;
  const initialTheme = htmlEl.getAttribute('data-theme');
  const initialPressed = btn.getAttribute('aria-pressed');
  btn.dispatchEvent('click');
  const afterClickTheme = htmlEl.getAttribute('data-theme');
  const afterClickPressed = btn.getAttribute('aria-pressed');
  let prevented = false;
  btn.dispatchEvent('keydown', { key: ' ', preventDefault: () => { prevented = true; } });
  const afterSpaceTheme = htmlEl.getAttribute('data-theme');
  const afterSpacePressed = btn.getAttribute('aria-pressed');

  // Persist & Restore with opted-in storage adapter
  const backingData = Object.create(null);
  const mockStorage = {
    getItem: (k) => (Object.prototype.hasOwnProperty.call(backingData, k) ? backingData[k] : null),
    setItem: (k, v) => { backingData[k] = String(v); }
  };
  const docPersist = makeDocument(islands);
  const ctrlPersist = base.sandbox.SimTheme.init(docPersist, { optIn: true, storage: mockStorage });
  ctrlPersist.toggle(); // light -> dark
  const persistedVal = backingData[base.sandbox.SimTheme.STORAGE_KEY];
  const docRestore = makeDocument(islands);
  const ctrlRestore = base.sandbox.SimTheme.init(docRestore, { optIn: true, storage: mockStorage });
  const restoredTheme = ctrlRestore.getTheme();
  const restoredAttr = docRestore.documentElement.getAttribute('data-theme');

  // No-store & throwing-store degradation
  const docNoStore = makeDocument(islands);
  const ctrlNoStore = base.sandbox.SimTheme.init(docNoStore, { optIn: true, storage: null });
  const ctrlNoStoreAfterToggle = ctrlNoStore.toggle();

  const throwingStorage = {
    getItem: () => { throw new Error('SecurityError: blocked'); },
    setItem: () => { throw new Error('SecurityError: blocked'); }
  };
  const docThrow = makeDocument(islands);
  const ctrlThrow = base.sandbox.SimTheme.init(docThrow, { optIn: true, storage: throwingStorage });
  const ctrlThrowAfterToggle = ctrlThrow.toggle();

  checks.theme_toggle = {
    initial: { theme: initialTheme, pressed: initialPressed },
    after_click: { theme: afterClickTheme, pressed: afterClickPressed },
    after_space: { theme: afterSpaceTheme, pressed: afterSpacePressed, prevented },
    persist_restore: { persistedVal, restoredTheme, restoredAttr },
    no_store_degradation: {
      mode: ctrlNoStore.store.mode,
      degraded: ctrlNoStore.store.degraded,
      reason: ctrlNoStore.store.reason,
      toggled_to: ctrlNoStoreAfterToggle
    },
    throwing_store_degradation: {
      mode: ctrlThrow.store.mode,
      degraded: ctrlThrow.store.degraded,
      reason: ctrlThrow.store.reason,
      toggled_to: ctrlThrowAfterToggle
    }
  };
  if (initialTheme !== 'light' || initialPressed !== 'false') failures.push('unexpected initial theme state');
  if (afterClickTheme !== 'dark' || afterClickPressed !== 'true') failures.push('click did not switch to dark');
  if (afterSpaceTheme !== 'light' || afterSpacePressed !== 'false' || !prevented) failures.push('Space key did not toggle back to light');
  if (persistedVal !== 'dark' || restoredTheme !== 'dark' || restoredAttr !== 'dark') failures.push('persist/restore failed');
  if (!ctrlNoStore.store.degraded || ctrlNoStore.store.mode !== 'memory' || ctrlNoStoreAfterToggle !== 'dark') {
    failures.push('no-store degradation failed');
  }
  if (!ctrlThrow.store.degraded || ctrlThrow.store.mode !== 'memory' || ctrlThrowAfterToggle !== 'dark') {
    failures.push('throwing-store degradation failed');
  }

  // 5. Negative smoke vector test
  const loadedCov = base.sandbox.SimCoverage.load(base.document, base.sandbox.COVERAGE_INVARIANTS);
  const badSmoke = base.sandbox.SimSmoke.run(base.document, {
    coverage: loadedCov,
    expected: { total: 64, perTopic: { 1: 8, 2: 10, 3: 11, 4: 11, 5: 10, 6: 8, 7: 5 } }
  });
  checks.smoke_negative = badSmoke;
  if (badSmoke.status !== 'FAIL' || !badSmoke.vectors[0].reason.includes('Topic 1')) {
    failures.push('negative smoke check did not fail with Topic 1 mismatch');
  }

  const report = {
    schema_version: 1,
    task: 'N06',
    artifact: 'n06-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    status: failures.length === 0 ? 'PASS' : 'FAIL',
    checks,
    failures
  };

  if (process.argv.includes('--json')) {
    process.stdout.write(JSON.stringify(report, null, 2) + '\n');
  } else {
    process.stdout.write(report.status + ' n06-runtime\n');
    process.stdout.write('  start topics: ' + checks.baseline.start_topics_count + ', verbatim outcomes: ' + checks.baseline.verbatim_outcomes_matched + '/64\n');
    process.stdout.write('  single-source: start=' + checks.single_source.start_changed + ', nav=' + checks.single_source.nav_changed + ', list=' + checks.single_source.list_statement_changed + '\n');
    process.stdout.write('  markup escaping: ' + checks.markup_escaping.no_injected_tags + '\n');
    process.stdout.write('  theme toggle: click->' + afterClickTheme + ', space->' + afterSpaceTheme + ', restore->' + restoredTheme + ', no-store->' + ctrlNoStore.store.mode + '\n');
    process.stdout.write('  smoke vector: ' + checks.baseline.smoke_report.status + ' (' + checks.baseline.smoke_report.vectors[0].id + ')\n');
    for (const f of failures) process.stdout.write('  - ' + f + '\n');
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
