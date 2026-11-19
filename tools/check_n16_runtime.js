#!/usr/bin/env node
/* N16 runtime harness: executes the shipped script from output/simulator.html in
 * a minimal DOM and proves:
 *  - 14 collapsed chains, 68 sealed steps, 0 plaintext result/reasoning leaks
 *  - per-step reveal, reveal-all confirmation once, re-collapse digest equality
 *  - item-to-chain focus restore and the drawer-close-mid-confirmation edge case
 *  - map-to-chain focus restore and cross-reference island consistency
 *  - two-run parity of the whole chain walk
 *  - in-file smoke vector SMK-N16-CHAINS-REVEAL PASS
 * The harness is not a browser render, accessibility or print acceptance claim.
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
function assert(cond, msg) {
  if (!cond) throw new Error('Assertion failed: ' + msg);
}

function makeDocument(islands) {
  const registry = Object.create(null);
  const doc = {
    documentElement: null,
    activeElement: null,
    createElement(tag) { return new Node(tag); },
    createElementNS(_ns, tag) { return new Node(tag); },
    getElementById(id) { return registry[id] || findById(doc.body, id); }
  };
  function findById(rootNode, id) {
    if (!rootNode) return null;
    if (rootNode.id === id) return rootNode;
    for (let i = 0; i < rootNode.childNodes.length; i += 1) {
      const f = findById(rootNode.childNodes[i], id);
      if (f) return f;
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
    this.type = '';
    this.tabIndex = 0;
    this._text = '';
  }
  Object.defineProperty(Node.prototype, 'id', {
    get() { return this._id; },
    set(v) {
      if (this._id && registry[this._id] === this) delete registry[this._id];
      this._id = String(v);
      if (this._id) registry[this._id] = this;
    }
  });
  Object.defineProperty(Node.prototype, 'firstChild', {
    get() { return this.childNodes.length ? this.childNodes[0] : null; }
  });
  Object.defineProperty(Node.prototype, 'textContent', {
    get() {
      if (this.childNodes.length) return this.childNodes.map((c) => c.textContent).join('');
      return this._text;
    },
    set(v) {
      this.childNodes = [];
      this._text = String(v);
    }
  });
  Node.prototype.appendChild = function (child) {
    child.parentNode = this;
    this.childNodes.push(child);
    if (child.id) registry[child.id] = child;
    return child;
  };
  Node.prototype.removeChild = function (child) {
    const i = this.childNodes.indexOf(child);
    if (i >= 0) { this.childNodes.splice(i, 1); child.parentNode = null; }
    return child;
  };
  Node.prototype.setAttribute = function (k, v) { this.attributes[k] = String(v); };
  Node.prototype.getAttribute = function (k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  };
  Node.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
  Node.prototype.addEventListener = function (type, fn) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(fn);
  };
  Node.prototype.dispatchEvent = function (type, ev) {
    const list = this.listeners[type] || [];
    for (let i = 0; i < list.length; i += 1) list[i](ev || {});
  };
  Node.prototype.focus = function () { doc.activeElement = this; };
  Node.prototype.blur = function () { if (doc.activeElement === this) doc.activeElement = doc.body; };

  doc.documentElement = new Node('html');
  doc.body = new Node('body');
  doc.activeElement = doc.body;

  const spec = [
    ['sim-coverage', 'script'], ['sim-conventions', 'script'], ['sim-bank', 'script'],
    ['sim-forms', 'script'], ['sim-golden-vectors', 'script'], ['sim-terms', 'script'],
    ['sim-analytics', 'script'], ['sim-figures', 'script'], ['sim-chains', 'script'],
    ['sim-header', 'header'], ['sim-main', 'main'], ['sim-footer', 'footer'],
    ['sakums-oficialas-temas', 'ol'], ['coverage-nav', 'nav'], ['coverage-list', 'div'],
    ['coverage-total', 'strong'], ['theme-toggle', 'button'], ['theme-status', 'p'],
    ['sim-smoke-status', 'p'],
    ['sim-coverage-error', 'div'], ['sim-conventions-error', 'div'], ['sim-bank-error', 'div'],
    ['sim-golden-vectors-error', 'div'], ['sim-terms-error', 'div'], ['sim-figures-error', 'div'],
    ['sim-chains-error', 'div'],
    ['sim-conventions-status', 'p'], ['sim-bank-status', 'p'], ['sim-golden-vectors-status', 'p'],
    ['sim-terms-status', 'p'], ['sim-figures-status', 'p'], ['sim-chains-status', 'p'],
    ['chain-index', 'div'],
    ['concept-drawer-backdrop', 'div'], ['concept-drawer', 'aside'],
    ['concept-drawer-topic', 'p'], ['concept-drawer-title', 'h2'], ['concept-drawer-back', 'button'],
    ['concept-drawer-close', 'button'], ['concept-drawer-breadcrumb', 'p'],
    ['concept-drawer-summary', 'p'], ['concept-drawer-citation', 'p'],
    ['concept-drawer-dissent', 'p'], ['concept-drawer-prereqs', 'div'],
    ['concept-drawer-slots', 'div'], ['concept-drawer-status', 'p'],
    ['hint-drawer-backdrop', 'div'], ['hint-drawer', 'aside'], ['hint-drawer-body', 'div'],
    ['prakse-help-slot', 'div'], ['karte', 'div']
  ];
  spec.forEach(([id, tag]) => {
    const node = new Node(tag);
    node.id = id;
    if (id.endsWith('-error') || id.endsWith('-status') || id === 'concept-drawer-backdrop' ||
        id === 'concept-drawer' || id === 'concept-drawer-back' || id === 'concept-drawer-breadcrumb' ||
        id === 'concept-drawer-dissent' || id === 'hint-drawer-backdrop' || id === 'hint-drawer') {
      if (id !== 'theme-status' && id !== 'concept-drawer-status') node.hidden = true;
    }
    doc.body.appendChild(node);
  });
  const backdrop = registry['concept-drawer-backdrop'];
  const drawer = registry['concept-drawer'];
  backdrop.appendChild(drawer);
  ['concept-drawer-topic', 'concept-drawer-title', 'concept-drawer-back', 'concept-drawer-close',
    'concept-drawer-breadcrumb', 'concept-drawer-summary', 'concept-drawer-citation',
    'concept-drawer-dissent', 'concept-drawer-prereqs', 'concept-drawer-slots',
    'concept-drawer-status'].forEach((id) => drawer.appendChild(registry[id]));
  Object.keys(islands).forEach((id) => { if (registry[id]) registry[id].textContent = islands[id]; });
  return doc;
}

function extractArtifact(html) {
  const islandIds = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms',
    'sim-golden-vectors', 'sim-terms', 'sim-analytics', 'sim-figures', 'sim-chains'];
  const islands = {};
  islandIds.forEach((id) => {
    const re = new RegExp('<script\\s+type="application/json"\\s+id="' + id + '"[^>]*>([\\s\\S]*?)</script>');
    const m = re.exec(html);
    if (!m) throw new Error('Missing #' + id + ' in output/simulator.html');
    islands[id] = m[1].replace(/<\\\//g, '</');
  });
  const scripts = [];
  const pattern = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let m;
  while ((m = pattern.exec(html)) !== null) scripts.push(m[1]);
  if (scripts.length !== 1) throw new Error('Expected 1 executable script, found ' + scripts.length);
  return { islands, bootstrap: scripts[0] };
}

function runInVm(islands, bootstrap) {
  const document = makeDocument(islands);
  const sandbox = {
    document, console, JSON, Error, String, Object, Array, Math, Number, BigInt, Boolean, RegExp,
    atob, TextDecoder, Uint8Array, decodeURIComponent, escape
  };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document, sandbox };
}

function findAll(node, pred, out) {
  out = out || [];
  if (!node) return out;
  if (node.nodeType === undefined && pred(node)) out.push(node);
  for (let i = 0; i < (node.childNodes || []).length; i += 1) findAll(node.childNodes[i], pred, out);
  return out;
}
function byClass(root, cls) {
  return findAll(root, (n) => String(n.className || '').split(/\s+/).indexOf(cls) >= 0);
}
function firstByClass(root, cls) { return byClass(root, cls)[0] || null; }
function byAttr(root, attr, val) {
  return findAll(root, (n) => n.getAttribute && n.getAttribute(attr) === val);
}
function visibleText(node, skip) {
  if (!node) return '';
  if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return '';
  if (skip && skip(node)) return '';
  if (!node.childNodes || node.childNodes.length === 0) return node._text || '';
  let out = '';
  for (let i = 0; i < node.childNodes.length; i += 1) out += ' ' + visibleText(node.childNodes[i], skip);
  return out.replace(/\s+/g, ' ').trim();
}
function serializeChain(node) {
  if (!node) return '';
  if (!node.childNodes || node.childNodes.length === 0) {
    if (node.tagName) return '<' + node.tagName + (node.hidden ? ' hidden' : '') + '>' + (node._text || '');
    return node._text || '';
  }
  if (!node.tagName) return node._text || '';
  const attrs = [];
  if (node.id) attrs.push('id=' + node.id);
  if (node.className) attrs.push('class=' + node.className);
  ['data-chain-id', 'data-step-id', 'data-revealed', 'data-revealed-count', 'data-revealed-all'].forEach((k) => {
    const v = node.getAttribute(k);
    if (v !== null) attrs.push(k + '=' + v);
  });
  if (node.hidden) attrs.push('hidden');
  const kids = [];
  for (let i = 0; i < node.childNodes.length; i += 1) kids.push(serializeChain(node.childNodes[i]));
  return '<' + node.tagName + ' ' + attrs.join(' ') + '>' + kids.join('') + '</' + node.tagName + '>';
}
const SUPER = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁻': '-', '⁺': '+' };
function norm(text) {
  return String(text).toLowerCase().replace(/\u2212/g, '-').replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]/g, (c) => SUPER[c] || c)
    .replace(/[·×xX]10\^?([+-]?\d+)/g, 'e$1').replace(/\s+/g, ' ').trim();
}
function hasSecret(text, secret) {
  const n = norm(text);
  const s = norm(secret);
  if (!s) return false;
  if (/^[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?$/.test(s)) {
    const re = new RegExp('(?<![\\d.,])' + s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '(?![\\d.,])');
    return re.test(n);
  }
  return n.indexOf(s) >= 0;
}
function unseal(sealed) {
  const key = Buffer.from(sealed.key, 'hex');
  const data = Buffer.from(sealed.data, 'base64');
  const out = Buffer.alloc(data.length);
  for (let i = 0; i < data.length; i += 1) out[i] = data[i] ^ key[i % key.length];
  return JSON.parse(new TextDecoder('utf-8').decode(out));
}
function collectSecrets(chain) {
  const secrets = [];
  chain.steps.forEach((st) => {
    if (st.public) return;
    const p = unseal(st.sealed);
    secrets.push({ step: st.step_id, kind: 'result', text: String(p.display_lv || p.value || '') });
    secrets.push({ step: st.step_id, kind: 'reasoning', text: String(p.reasoning_lv || '') });
  });
  return secrets;
}
function scanChain(article, secrets) {
  const text = visibleText(article);
  const hits = [];
  secrets.forEach((s) => {
    if (s.kind === 'reasoning') {
      const parts = s.text.split(/[.;:]\s*/).filter((p) => p.length >= 20);
      for (const p of parts) if (hasSecret(text, p)) { hits.push({ step: s.step, kind: 'reasoning' }); break; }
    } else if (hasSecret(text, s.text)) {
      hits.push({ step: s.step, kind: 'result' });
    }
  });
  return { text, hits };
}
function chainArticle(doc, chainId, key) {
  return doc.getElementById('chain-' + chainId + '-' + key);
}

function walkChain(doc, chainId) {
  const island = JSON.parse(doc.getElementById('sim-chains').textContent);
  const chain = island.chains.find((c) => c.id === chainId);
  assert(chain, 'missing chain ' + chainId);
  let article = chainArticle(doc, chainId, 'index');
  assert(article, 'missing index article for ' + chainId);
  assert(firstByClass(article, 'chain-citation'), chainId + ' master citation missing');
  assert(article.getAttribute('data-revealed-count') === '0', chainId + ' must open collapsed');
  const pre = serializeChain(article);
  const preText = visibleText(article);
  const preTextDigest = sha256(article.getAttribute('data-revealed-count') + '|' + article.getAttribute('data-revealed-all') + '|' + article.textContent);
  const secrets = collectSecrets(chain);
  const preScan = scanChain(article, secrets);
  assert(preScan.hits.length === 0, chainId + ' pre-reveal leak: ' + JSON.stringify(preScan.hits.slice(0, 3)));
  const stepButtons = byClass(article, 'chain-reveal-btn');
  assert(stepButtons.length === chain.steps.length, chainId + ' step button count');
  const results = byClass(article, 'chain-result');
  assert(results.length === chain.steps.length, chainId + ' result count');
  results.forEach((r) => assert(r.hidden && r.textContent.trim() === '', chainId + ' pre-reveal result must be empty'));
  // Reveal the first step only; future results must stay empty.
  stepButtons[0].dispatchEvent('click');
  assert(!results[0].hidden && results[0].textContent.length > 0, chainId + ' first step reveal failed');
  for (let i = 1; i < results.length; i += 1) assert(results[i].hidden && results[i].textContent.trim() === '', chainId + ' future step leaked');
  const firstFigRefs = (chain.figure_refs || []).filter((f) => f.step_id === chain.steps[0].step_id);
  if (firstFigRefs.length) {
    const figHost = firstByClass(article, 'chain-figure-host');
    assert(figHost && figHost.getAttribute('data-figure-state') === 'mounted', chainId + ' first-step figure not mounted');
    assert(!firstByClass(figHost, 'chain-figure-error'), chainId + ' first-step figure error');
  }
  // Reveal-all must ask once, then reveal all.
  const allBtn = firstByClass(article, 'chain-reveal-all');
  const confirm = firstByClass(article, 'chain-confirm');
  const yes = firstByClass(article, 'chain-confirm-yes');
  assert(allBtn && confirm && yes, chainId + ' reveal-all controls missing');
  allBtn.dispatchEvent('click');
  assert(!confirm.hidden, chainId + ' reveal-all did not ask for confirmation');
  yes.dispatchEvent('click');
  assert(confirm.hidden, chainId + ' confirmation did not close');
  assert(article.getAttribute('data-revealed-all') === 'true', chainId + ' not fully revealed');
  assert(article.getAttribute('data-revealed-count') === String(chain.steps.length), chainId + ' revealed count');
  results.forEach((r) => assert(!r.hidden && r.textContent.length > 0, chainId + ' revealed result empty'));
  const revealed = serializeChain(article);
  const revealedTextDigest = sha256(article.getAttribute('data-revealed-count') + '|' + article.getAttribute('data-revealed-all') + '|' + article.textContent);
  // Re-collapse restores the exact pre-reveal serialization.
  const collapse = firstByClass(article, 'chain-collapse');
  assert(collapse, chainId + ' collapse control missing');
  collapse.dispatchEvent('click');
  article = chainArticle(doc, chainId, 'index');
  const after = serializeChain(article);
  assert(after === pre, chainId + ' re-collapse digest mismatch');
  return {
    chainId, steps: chain.steps.length,
    preDigest: sha256(pre), revealedDigest: sha256(revealed), collapseDigest: sha256(after), preTextDigest: preTextDigest, revealedTextDigest: revealedTextDigest,
    preLeaks: preScan.hits.length, preTextLength: preText.length
  };
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islands, bootstrap } = extractArtifact(html);
  const base = runInVm(islands, bootstrap);
  const doc = base.document;
  const C = base.sandbox.SimChains;
  assert(C, 'SimChains module not loaded');
  const island = JSON.parse(islands['sim-chains']);
  assert(island.island_id === 'sim-chains' && island.chain_count === 14, 'expected 14 chains');
  const state0 = C.getState().filter((s) => String(s.mountKey).indexOf('index') === 0);
  assert(state0.length === 14, 'expected 14 index mounts, got ' + state0.length);
  assert(state0.every((s) => s.revealedCount === 0), 'chains must start collapsed');

  // First run
  const first = island.chains.map((c) => walkChain(doc, c.id));
  // Second fresh VM for parity
  const base2 = runInVm(islands, bootstrap);
  const second = island.chains.map((c) => walkChain(base2.document, c.id));
  const parity = JSON.stringify(first) === JSON.stringify(second);
  assert(parity, 'two-run chain walk parity failed');

  // Item-to-chain path + item-context key scan + normal and mid-confirmation focus.
  const item = doc.createElement('button');
  item.id = 'n16-item-trigger';
  item.textContent = 'Prakses vienums ar EX11 mācību saiti';
  doc.body.appendChild(item);
  item.focus();
  C.openFromLink({ chainId: 'EX11', source: 'practice-item', returnContext: { elementId: 'n16-item-trigger', triggerEl: item } }, doc);
  const drawer = doc.getElementById('concept-drawer');
  assert(!drawer.hidden, 'item-to-chain did not open the drawer');
  const drawerChain = chainArticle(doc, 'EX11', 'drawer-P6-08');
  assert(drawerChain, 'EX11 chain not mounted in the drawer');
  const drawerChainText = visibleText(drawerChain);
  const itemKeys = ['0.03125 mol/L', '4.20 g'];
  const itemLeaks = itemKeys.filter((k) => hasSecret(drawerChainText, k) || hasSecret(JSON.stringify(island), k));
  assert(itemLeaks.length === 0, 'item key leaked into chain context: ' + itemLeaks.join(', '));
  byClass(drawerChain, 'chain-reveal-btn')[0].dispatchEvent('click');
  base.sandbox.SimConceptDrawer.close(doc);
  const itemNormalFocus = doc.activeElement && doc.activeElement.id;
  assert(itemNormalFocus === 'n16-item-trigger',
    'item-to-chain close did not restore item focus, got ' + itemNormalFocus);

  // Reopen and close while the reveal-all confirmation is open.
  C.openFromLink({ chainId: 'EX11', source: 'practice-item', returnContext: { elementId: 'n16-item-trigger', triggerEl: item } }, doc);
  const drawerChain2 = chainArticle(doc, 'EX11', 'drawer-P6-08');
  const drawerAll = firstByClass(drawerChain2, 'chain-reveal-all');
  drawerAll.dispatchEvent('click');
  const drawerConfirm = firstByClass(drawerChain2, 'chain-confirm');
  assert(!drawerConfirm.hidden, 'drawer reveal-all confirmation missing');
  base.sandbox.SimConceptDrawer.close(doc);
  const itemEdgeFocus = doc.activeElement && doc.activeElement.id;
  assert(itemEdgeFocus === 'n16-item-trigger',
    'drawer close mid-confirmation did not restore item focus, got ' + itemEdgeFocus);

  // Map-to-chain path: P2-07 -> EX03, reveal, close, focus restored.
  const mapBtn = doc.getElementById('karte-btn-P2-07');
  assert(mapBtn, 'map button karte-btn-P2-07 missing');
  mapBtn.focus();
  C.openFromLink({ chainId: 'EX03', source: 'map', returnContext: { elementId: 'karte-btn-P2-07', triggerEl: mapBtn } }, doc);
  const mapChain = chainArticle(doc, 'EX03', 'drawer-P2-07');
  assert(mapChain, 'EX03 chain not mounted from map');
  byClass(mapChain, 'chain-reveal-btn')[0].dispatchEvent('click');
  base.sandbox.SimConceptDrawer.close(doc);
  const mapFocus = doc.activeElement && doc.activeElement.id;
  assert(mapFocus === 'karte-btn-P2-07',
    'map-to-chain close did not restore map focus, got ' + mapFocus);

  const report = {
    schema_version: 1,
    task: 'N16',
    artifact: 'n16-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    status: 'PASS',
    chains: first.length,
    steps: first.reduce((n, c) => n + c.steps, 0),
    parity,
    index_mounts: state0.length,
    item_context: { chain: 'EX11', item_keys: itemKeys, leaks: itemLeaks, focus_after_close: itemNormalFocus,
      focus_after_mid_confirmation_close: itemEdgeFocus },
    map_context: { chain: 'EX03', focus_after_close: mapFocus },
    chain_digests: first,
    checks: {
      collapsed_default: true,
      per_step_reveal: true,
      future_steps_hidden: true,
      reveal_all_confirms_once: true,
      collapse_roundtrip: true,
      item_key_scan: itemLeaks.length === 0,
      item_focus_restore: itemNormalFocus === 'n16-item-trigger',
      drawer_mid_confirmation_focus: itemEdgeFocus === 'n16-item-trigger',
      map_focus_restore: mapFocus === 'karte-btn-P2-07',
      smoke: true
    }
  };
  const smoke = base.sandbox.SimSmoke && typeof base.sandbox.SimSmoke.run === 'function'
    ? base.sandbox.SimSmoke.run(doc, { coverage: base.sandbox.SimCoverage.load(doc, base.sandbox.COVERAGE_INVARIANTS), onLoad: false })
    : null;
  const n16 = smoke && smoke.vectors ? smoke.vectors.find((v) => v.id === 'SMK-N16-CHAINS-REVEAL') : null;
  assert(n16 && n16.status === 'PASS', 'SMK-N16-CHAINS-REVEAL did not pass: ' + JSON.stringify(n16));
  report.smoke = n16;
  report.smoke_summary = { total: smoke.total, passed: smoke.passed, failed: smoke.failed, status: smoke.status };
  console.log(JSON.stringify(report));
}
try {
  main();
} catch (error) {
  console.error('FAIL check_n16_runtime:', error.message);
  process.exit(1);
}
