#!/usr/bin/env node
/* N02 runtime harness: execute the shipped loader/view in a minimal DOM.
 *
 * Proves the baseline render, the single-sourcing rule (a topic-name edit in
 * the island changes both views), the truncated-island degradation (honest error
 * naming #sim-coverage, never a blank page) and the deleted-outcome rejection.
 *
 * No external dependencies, no network, no browser. Run:
 *   node tools/check_coverage_runtime.js --json
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

function makeDocument(islandText) {
  const nodes = Object.create(null);

  function Node(tagName) {
    this.tagName = String(tagName).toUpperCase();
    this.childNodes = [];
    this.parentNode = null;
    this.attributes = Object.create(null);
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

  ['sim-coverage', 'coverage-nav', 'coverage-list', 'coverage-total', 'sim-coverage-error'].forEach((id) => {
    const node = new Node(id === 'sim-coverage' ? 'script' : (id === 'coverage-nav' ? 'nav' : 'div'));
    node.id = id;
    nodes[id] = node;
  });
  nodes['sim-coverage'].textContent = islandText;
  nodes['sim-coverage-error'].hidden = true;

  return {
    createElement(tag) { return new Node(tag); },
    getElementById(id) { return nodes[id] || null; },
    _nodes: nodes
  };
}

function extractArtifact(html) {
  const islandMatch = /<script\s+type="application\/json"\s+id="sim-coverage">([\s\S]*?)<\/script>/.exec(html);
  if (!islandMatch) {
    throw new Error('output/simulator.html has no #sim-coverage JSON island');
  }
  const scripts = [];
  const pattern = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = pattern.exec(html)) !== null) {
    scripts.push(match[1]);
  }
  if (!scripts.length) {
    throw new Error('output/simulator.html has no executable script');
  }
  return { islandText: islandMatch[1], bootstrap: scripts[scripts.length - 1] };
}

function run(islandText, bootstrap) {
  const document = makeDocument(islandText);
  const sandbox = { document, console, JSON, Error, String, Object, Array, Math };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document, sandbox };
}

function errorCode(sandbox, document) {
  try {
    sandbox.SimCoverage.load(document, sandbox.COVERAGE_INVARIANTS);
    return null;
  } catch (error) {
    return { code: error.code, message: error.message };
  }
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { islandText, bootstrap } = extractArtifact(html);
  const checks = {};

  // Baseline render.
  const baseline = run(islandText, bootstrap);
  const navText = baseline.document.getElementById('coverage-nav').textContent;
  const listText = baseline.document.getElementById('coverage-list').textContent;
  const totalText = baseline.document.getElementById('coverage-total').textContent;
  const errorNode = baseline.document.getElementById('sim-coverage-error');
  checks.baseline = {
    nav_items: (navText.match(/\(/g) || []).length,
    list_outcome_ids: (listText.match(/P[1-7]-\d{2}/g) || []).length,
    total_label: totalText,
    error_hidden: errorNode.hidden === true,
    error_text: errorNode.textContent
  };

  // Single-sourcing: change the first topic name in a scratch island copy.
  const originalTopic = 'Ievads. Šķīdumi un ķīmiskās reakcijas';
  const sentinel = 'SENTINELA TĒMA N02';
  if (islandText.indexOf(originalTopic) < 0) {
    throw new Error('Baseline island does not contain the expected topic name');
  }
  const editedIsland = islandText.replace(originalTopic, sentinel);
  const edited = run(editedIsland, bootstrap);
  const editedNav = edited.document.getElementById('coverage-nav').textContent;
  const editedList = edited.document.getElementById('coverage-list').textContent;
  checks.single_source = {
    sentinel: sentinel,
    nav_changed: editedNav.indexOf(sentinel) >= 0 && editedNav.indexOf(originalTopic) < 0,
    list_changed: editedList.indexOf(sentinel) >= 0 && editedList.indexOf(originalTopic) < 0,
    nav_items: (editedNav.match(/\(/g) || []).length,
    list_outcome_ids: (editedList.match(/P[1-7]-\d{2}/g) || []).length
  };

  // Truncated island: the loader must name #sim-coverage and render text.
  const truncatedText = islandText.slice(0, 120);
  const truncated = run(truncatedText, bootstrap);
  const truncatedError = truncated.document.getElementById('sim-coverage-error');
  const truncatedList = truncated.document.getElementById('coverage-list').textContent;
  const truncatedNav = truncated.document.getElementById('coverage-nav').textContent;
  const truncatedCode = errorCode(truncated.sandbox, makeDocument(truncatedText));
  checks.truncated = {
    error_visible: truncatedError.hidden === false,
    error_names_island: truncatedError.textContent.indexOf('#sim-coverage') >= 0,
    error_text: truncatedError.textContent,
    list_nonblank: truncatedList.trim().length > 0,
    nav_nonblank: truncatedNav.trim().length > 0,
    code: truncatedCode && truncatedCode.code
  };

  // Deleted outcome: cheap count invariant must reject it.
  const parsed = JSON.parse(islandText);
  parsed.outcomes.pop();
  const deletedText = JSON.stringify(parsed);
  const deleted = run(deletedText, bootstrap);
  const deletedError = deleted.document.getElementById('sim-coverage-error');
  const deletedCode = errorCode(deleted.sandbox, makeDocument(deletedText));
  checks.deleted_outcome = {
    rejected: deletedError.hidden === false,
    code: deletedCode && deletedCode.code,
    error_text: deletedError.textContent,
    list_nonblank: deleted.document.getElementById('coverage-list').textContent.trim().length > 0
  };

  const failures = [];
  if (checks.baseline.nav_items !== 7) failures.push('baseline nav does not have 7 topics');
  if (checks.baseline.list_outcome_ids !== 64) failures.push('baseline list does not render 64 outcome ids');
  if (checks.baseline.total_label !== '64') failures.push('baseline total label is not 64');
  if (!checks.baseline.error_hidden) failures.push('baseline error box is visible');
  if (!checks.single_source.nav_changed) failures.push('single-sourcing: nav did not follow the island edit');
  if (!checks.single_source.list_changed) failures.push('single-sourcing: list did not follow the island edit');
  if (!checks.truncated.error_visible) failures.push('truncated island did not show the error state');
  if (!checks.truncated.error_names_island) failures.push('truncated island error does not name #sim-coverage');
  if (!checks.truncated.list_nonblank || !checks.truncated.nav_nonblank) failures.push('truncated island left a blank view');
  if (!checks.deleted_outcome.rejected) failures.push('deleted outcome was not rejected at runtime');
  if (checks.deleted_outcome.code !== 'E_COVERAGE_COUNT') failures.push('deleted outcome did not fail with E_COVERAGE_COUNT');

  const result = {
    schema_version: 1,
    task: 'N02',
    artifact: 'coverage-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    island_sha256: sha256(islandText),
    status: failures.length ? 'FAIL' : 'PASS',
    checks,
    failures
  };
  const json = JSON.stringify(result, null, 2);
  if (process.argv.indexOf('--json') >= 0) {
    process.stdout.write(json + '\n');
  } else {
    process.stdout.write((result.status === 'PASS' ? 'PASS' : 'FAIL') + ' coverage-runtime\n');
    process.stdout.write('  baseline: ' + checks.baseline.nav_items + ' topics, ' + checks.baseline.list_outcome_ids + ' outcomes\n');
    process.stdout.write('  single-source: nav=' + checks.single_source.nav_changed + ', list=' + checks.single_source.list_changed + '\n');
    process.stdout.write('  truncated: visible=' + checks.truncated.error_visible + ', names island=' + checks.truncated.error_names_island + ', code=' + checks.truncated.code + '\n');
    process.stdout.write('  deleted outcome: rejected=' + checks.deleted_outcome.rejected + ', code=' + checks.deleted_outcome.code + '\n');
    for (const failure of failures) process.stdout.write('  - ' + failure + '\n');
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
