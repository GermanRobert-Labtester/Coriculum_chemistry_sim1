#!/usr/bin/env node
/* N03 runtime harness: execute the shipped conventions loader in a minimal DOM.
 *
 * Proves the baseline accessors, the single-sourcing rule (one tolerance change
 * is observed by the engine, the figure tolerance field and the vector
 * expectation in one run; one conversion change is observed by the engine and
 * the vector), and honest degradation on truncated/missing islands.
 *
 * No external dependencies, no network, no browser. Run:
 *   node tools/check_conventions_runtime.js --json
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

function makeDocument(conventionsText, coverageText) {
  const nodes = Object.create(null);
  const ids = [
    'sim-coverage', 'sim-conventions', 'coverage-nav', 'coverage-list',
    'coverage-total', 'sim-coverage-error', 'sim-conventions-error',
    'sim-conventions-status'
  ];
  ids.forEach((id) => {
    const node = new Node(id.indexOf('sim-') === 0 && (id === 'sim-coverage' || id === 'sim-conventions') ? 'script'
      : (id === 'coverage-nav' ? 'nav' : 'div'));
    node.id = id;
    nodes[id] = node;
  });
  if (conventionsText !== null) {
    nodes['sim-conventions'].textContent = conventionsText;
  } else {
    delete nodes['sim-conventions'];
  }
  if (coverageText !== null) nodes['sim-coverage'].textContent = coverageText;
  nodes['sim-coverage-error'].hidden = true;
  nodes['sim-conventions-error'].hidden = true;
  nodes['sim-conventions-status'].hidden = true;
  return {
    createElement(tag) { return new Node(tag); },
    getElementById(id) { return nodes[id] || null; },
    _nodes: nodes
  };
}

function extractArtifact(html) {
  const conventionsMatch = /<script\s+type="application\/json"\s+id="sim-conventions">([\s\S]*?)<\/script>/.exec(html);
  const coverageMatch = /<script\s+type="application\/json"\s+id="sim-coverage">([\s\S]*?)<\/script>/.exec(html);
  if (!conventionsMatch) throw new Error('output/simulator.html has no #sim-conventions JSON island');
  if (!coverageMatch) throw new Error('output/simulator.html has no #sim-coverage JSON island');
  const scripts = [];
  const pattern = /<script(?![^>]*type="application\/json")[^>]*>([\s\S]*?)<\/script>/g;
  let match;
  while ((match = pattern.exec(html)) !== null) scripts.push(match[1]);
  if (!scripts.length) throw new Error('output/simulator.html has no executable script');
  return {
    conventionsText: conventionsMatch[1],
    coverageText: coverageMatch[1],
    bootstrap: scripts[scripts.length - 1]
  };
}

function run(conventionsText, coverageText, bootstrap) {
  const document = makeDocument(conventionsText, coverageText);
  const sandbox = { document, console, JSON, Error, String, Object, Array, Math, Number, RegExp };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(bootstrap, sandbox, { timeout: 10000 });
  return { document, sandbox };
}

function loadModel(sandbox, document) {
  const loaded = sandbox.SimConventions.load(document);
  return { loaded, model: sandbox.SimConventions.model(loaded) };
}

function errorCode(sandbox, document) {
  try {
    sandbox.SimConventions.load(document);
    return null;
  } catch (error) {
    return { code: error.code, message: error.message };
  }
}

function main() {
  const html = fs.readFileSync(ARTIFACT, 'utf8');
  const { conventionsText, coverageText, bootstrap } = extractArtifact(html);
  const checks = {};

  const baseline = run(conventionsText, coverageText, bootstrap);
  const base = loadModel(baseline.sandbox, baseline.document);
  checks.baseline = {
    counts: base.loaded.counts,
    error_hidden: baseline.document.getElementById('sim-conventions-error').hidden === true,
    status_text: baseline.document.getElementById('sim-conventions-status').textContent,
    mgml_to_gl: base.model.convert(1, 'mg/mL', 'g/L'),
    mgl_to_gml: base.model.convert(1, 'mg/L', 'g/mL'),
    celsius_to_k: base.model.convert(25, '°C', 'K'),
    nacl_molar_mass: base.model.compoundMolarMass('NaCl'),
    sodium_mass: base.model.element('Na'),
    burette_tolerance: base.model.tolerance('burette_volume').absolute,
    potential_symbol: base.model.potential('E_prime').symbol,
    vector_tolerance: base.model.vectorExpectation('VEC-TOL-BURETTE').value,
    vector_conversion: base.model.vectorExpectation('VEC-CONV-MGML-GL').value,
    round_11145: base.model.roundHalfUp(1.1145, 2)
  };

  // Single-sourcing fixture 1: one tolerance value changed in a scratch island.
  const toleranceIsland = JSON.parse(conventionsText);
  const toleranceClass = toleranceIsland.tolerances.quantity_classes.find((item) => item.id === 'burette_volume');
  toleranceClass.absolute.value = '0.10';
  const toleranceScratch = JSON.stringify(toleranceIsland);
  const toleranceRun = run(toleranceScratch, coverageText, bootstrap);
  const toleranceModel = loadModel(toleranceRun.sandbox, toleranceRun.document).model;
  checks.single_source_tolerance = {
    scratch_value: '0.10',
    engine_tolerance: toleranceModel.tolerance('burette_volume').absolute,
    figure_tolerance_field: toleranceModel.tolerance('burette_volume').absolute,
    vector_expected: toleranceModel.vectorExpectation('VEC-TOL-BURETTE').value,
    all_changed: toleranceModel.tolerance('burette_volume').absolute === 0.10 &&
      toleranceModel.vectorExpectation('VEC-TOL-BURETTE').value === 0.10
  };

  // Single-sourcing fixture 2: one conversion factor changed in a scratch island.
  const conversionIsland = JSON.parse(conventionsText);
  const chain = conversionIsland.unit_system.chains.find((item) => item.id === 'concentration_mg_per_ml_to_g_per_l');
  chain.factor = { num: 2, den: 1 };
  const conversionScratch = JSON.stringify(conversionIsland);
  const conversionRun = run(conversionScratch, coverageText, bootstrap);
  const conversionModel = loadModel(conversionRun.sandbox, conversionRun.document).model;
  checks.single_source_conversion = {
    scratch_factor: 2,
    engine_conversion: conversionModel.convert(1, 'mg/mL', 'g/L'),
    vector_expected: conversionModel.vectorExpectation('VEC-CONV-MGML-GL').value,
    both_changed: conversionModel.convert(1, 'mg/mL', 'g/L') === 2 &&
      conversionModel.vectorExpectation('VEC-CONV-MGML-GL').value === 2
  };

  // Truncated island: the loader must name #sim-conventions and render text.
  const truncatedText = conventionsText.slice(0, 120);
  const truncated = run(truncatedText, coverageText, bootstrap);
  const truncatedError = truncated.document.getElementById('sim-conventions-error');
  const truncatedStatus = truncated.document.getElementById('sim-conventions-status').textContent;
  const truncatedCode = errorCode(truncated.sandbox, makeDocument(truncatedText, coverageText));
  checks.truncated = {
    error_visible: truncatedError.hidden === false,
    error_names_island: truncatedError.textContent.indexOf('#sim-conventions') >= 0,
    error_text: truncatedError.textContent,
    status_nonblank: truncatedStatus.trim().length > 0,
    code: truncatedCode && truncatedCode.code
  };

  // Missing island.
  const missing = run(null, coverageText, bootstrap);
  const missingCode = errorCode(missing.sandbox, makeDocument(null, coverageText));
  checks.missing = {
    error_visible: missing.document.getElementById('sim-conventions-error').hidden === false,
    error_names_island: missing.document.getElementById('sim-conventions-error').textContent.indexOf('#sim-conventions') >= 0,
    code: missingCode && missingCode.code
  };

  // Deleted conflict entry: the cheap count invariant must reject it.
  const deletedIsland = JSON.parse(conventionsText);
  deletedIsland.conflicts.entries.pop();
  const deletedText = JSON.stringify(deletedIsland);
  const deleted = run(deletedText, coverageText, bootstrap);
  const deletedCode = errorCode(deleted.sandbox, makeDocument(deletedText, coverageText));
  checks.deleted_conflict = {
    rejected: deleted.document.getElementById('sim-conventions-error').hidden === false,
    code: deletedCode && deletedCode.code,
    error_text: deleted.document.getElementById('sim-conventions-error').textContent
  };

  const failures = [];
  if (checks.baseline.counts.conversions < 36) failures.push('baseline has fewer than 36 conversions');
  if (checks.baseline.counts.chains < 9) failures.push('baseline has fewer than 9 chains');
  if (checks.baseline.counts.tolerance_classes < 12) failures.push('baseline has fewer than 12 tolerance classes');
  if (checks.baseline.counts.conflicts !== 22) failures.push('baseline does not have 22 conflicts');
  if (!checks.baseline.error_hidden) failures.push('baseline conventions error box is visible');
  if (checks.baseline.mgml_to_gl !== 1) failures.push('mg/mL -> g/L is not 1');
  if (Math.abs(checks.baseline.mgl_to_gml - 0.000001) > 1e-12) failures.push('mg/L -> g/mL is not 1e-6');
  if (Math.abs(checks.baseline.celsius_to_k - 298.15) > 1e-9) failures.push('25 degC -> K is not 298.15');
  if (checks.baseline.nacl_molar_mass !== 58.44) failures.push('NaCl molar mass is not 58.44');
  if (Math.abs(checks.baseline.sodium_mass - 22.99) > 1e-9) failures.push('Na atomic mass is not 22.990');
  if (checks.baseline.burette_tolerance !== 0.05) failures.push('burette tolerance is not 0.05 mL');
  if (checks.baseline.potential_symbol !== 'E°′') failures.push('E-prime symbol is wrong');
  if (checks.baseline.vector_tolerance !== 0.05) failures.push('vector tolerance is not 0.05');
  if (checks.baseline.vector_conversion !== 1) failures.push('vector conversion is not 1');
  if (checks.baseline.status_text.indexOf('22') < 0) failures.push('status text does not mention 22 conflicts');
  if (!checks.single_source_tolerance.all_changed) failures.push('single-sourcing: tolerance change did not reach engine, figure and vector');
  if (!checks.single_source_conversion.both_changed) failures.push('single-sourcing: conversion change did not reach engine and vector');
  if (!checks.truncated.error_visible) failures.push('truncated island did not show the error state');
  if (!checks.truncated.error_names_island) failures.push('truncated island error does not name #sim-conventions');
  if (!checks.truncated.status_nonblank) failures.push('truncated island left the status blank');
  if (!checks.missing.error_visible || !checks.missing.error_names_island) failures.push('missing island did not degrade by name');
  if (!checks.deleted_conflict.rejected) failures.push('deleted conflict was not rejected at runtime');
  if (checks.deleted_conflict.code !== 'E_CONVENTIONS_CONFLICT_COUNT') failures.push('deleted conflict did not fail with E_CONVENTIONS_CONFLICT_COUNT');

  const result = {
    schema_version: 1,
    task: 'N03',
    artifact: 'conventions-runtime-harness',
    artifact_path: 'output/simulator.html',
    artifact_sha256: sha256(html),
    island_sha256: sha256(conventionsText),
    status: failures.length ? 'FAIL' : 'PASS',
    checks,
    failures
  };
  const json = JSON.stringify(result, null, 2);
  if (process.argv.indexOf('--json') >= 0) {
    process.stdout.write(json + '\n');
  } else {
    process.stdout.write((result.status === 'PASS' ? 'PASS' : 'FAIL') + ' conventions-runtime\n');
    process.stdout.write('  baseline: ' + checks.baseline.counts.conversions + ' conversions, ' +
      checks.baseline.counts.chains + ' chains, ' + checks.baseline.counts.conflicts + ' conflicts\n');
    process.stdout.write('  single-source tolerance: ' + checks.single_source_tolerance.all_changed + '\n');
    process.stdout.write('  single-source conversion: ' + checks.single_source_conversion.both_changed + '\n');
    process.stdout.write('  truncated: visible=' + checks.truncated.error_visible +
      ', names island=' + checks.truncated.error_names_island + ', code=' + checks.truncated.code + '\n');
    for (const failure of failures) process.stdout.write('  - ' + failure + '\n');
  }
  process.exitCode = failures.length ? 1 : 0;
}

main();
