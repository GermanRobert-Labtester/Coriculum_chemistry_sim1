#!/usr/bin/env node
/* N05 PRNG cross-language runtime runner.
 *
 * Executes src/prng.js (or a scratch override via --prng-path) in a clean VM
 * over the declared contract seeds, bounded draws, shuffle fixtures, and
 * illegal-seed cases, emitting exact decimal strings for every 64-bit value
 * so JSON serialization never loses precision to IEEE-754 float64.
 */
'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const crypto = require('crypto');

const ROOT = path.resolve(__dirname, '..');

function sha256(text) {
  return crypto.createHash('sha256').update(text, 'utf8').digest('hex');
}

function parseSeedValue(raw) {
  if (raw && typeof raw === 'object' && Object.prototype.hasOwnProperty.call(raw, 'bigint_dec')) {
    return BigInt(raw.bigint_dec);
  }
  if (raw && typeof raw === 'object' && Object.prototype.hasOwnProperty.call(raw, 'float')) {
    return Number(raw.float);
  }
  if (raw && typeof raw === 'object' && Object.prototype.hasOwnProperty.call(raw, 'special')) {
    if (raw.special === 'NaN') return NaN;
    if (raw.special === 'Infinity') return Infinity;
    if (raw.special === 'undefined') return undefined;
  }
  return raw;
}

function loadPrng(prngPath) {
  const code = fs.readFileSync(prngPath, 'utf8');
  const sandbox = { console, Error, String, Object, Array, Number, BigInt };
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(code, sandbox, { filename: prngPath });
  return sandbox.SimPRNG;
}

function runSuite(SimPRNG, spec) {
  const drawsPerSeed = spec.draws_per_seed || 100;
  const streams = [];

  for (const seedStr of spec.contract_seeds_dec) {
    const stream = SimPRNG.createStream(BigInt(seedStr));
    const draws = [];
    for (let i = 0; i < drawsPerSeed; i += 1) {
      draws.push(stream.nextU64().toString());
    }
    streams.push({
      seed_dec: seedStr,
      draws: draws,
      sha256: sha256(draws.join(','))
    });
  }

  const bounded = [];
  for (const bcase of spec.bounded_cases) {
    const stream = SimPRNG.createStream(BigInt(bcase.seed_dec));
    const values = [];
    if (bcase.op === 'nextInt') {
      for (let i = 0; i < bcase.count; i += 1) {
        values.push(stream.nextInt(bcase.bound));
      }
    } else if (bcase.op === 'nextRange') {
      for (let i = 0; i < bcase.count; i += 1) {
        values.push(stream.nextRange(bcase.min, bcase.max));
      }
    }
    bounded.push({
      id: bcase.id,
      values: values,
      draws_consumed: stream.drawsCount(),
      sha256: sha256(JSON.stringify(values))
    });
  }

  const shuffles = [];
  for (const scase of spec.shuffle_cases) {
    const stream = SimPRNG.createStream(BigInt(scase.seed_dec));
    const inputCopy = scase.items.slice();
    const out = stream.shuffle(inputCopy);
    shuffles.push({
      id: scase.id,
      input_preserved: JSON.stringify(inputCopy) === JSON.stringify(scase.items),
      output: out,
      draws_consumed: stream.drawsCount(),
      sha256: sha256(JSON.stringify(out))
    });
  }

  const illegalSeeds = [];
  for (const icase of spec.illegal_seed_cases) {
    const seedVal = parseSeedValue(icase.input);
    let rejected = false;
    let code = null;
    let errName = null;
    try {
      SimPRNG.createStream(seedVal);
    } catch (err) {
      rejected = true;
      code = err && err.code ? err.code : null;
      errName = err && err.name ? err.name : null;
    }
    illegalSeeds.push({
      label: icase.label,
      rejected: rejected,
      code: code,
      error_name: errName
    });
  }

  const illegalBounds = [];
  for (const b of spec.illegal_bound_cases) {
    const stream = SimPRNG.createStream(1n);
    let rejected = false;
    let code = null;
    try {
      stream.nextInt(parseSeedValue(b.input));
    } catch (err) {
      rejected = true;
      code = err && err.code ? err.code : null;
    }
    illegalBounds.push({ label: b.label, rejected: rejected, code: code });
  }

  return {
    language: 'javascript',
    algorithm_id: SimPRNG.ALGORITHM_ID,
    constants: SimPRNG.CONSTANTS,
    streams: streams,
    bounded: bounded,
    shuffles: shuffles,
    illegal_seeds: illegalSeeds,
    illegal_bounds: illegalBounds
  };
}

function main() {
  const args = process.argv.slice(2);
  let prngPath = path.join(ROOT, 'src', 'prng.js');
  let specPath = path.join(ROOT, 'data', 'prng_contract_vectors.json');

  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === '--prng-path' && args[i + 1]) {
      prngPath = path.resolve(args[i + 1]);
      i += 1;
    } else if (args[i] === '--spec' && args[i + 1]) {
      specPath = path.resolve(args[i + 1]);
      i += 1;
    }
  }

  const SimPRNG = loadPrng(prngPath);
  const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
  const output = runSuite(SimPRNG, spec);
  process.stdout.write(JSON.stringify(output, null, 2) + '\n');
}

main();
