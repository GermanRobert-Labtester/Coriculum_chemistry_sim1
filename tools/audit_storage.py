#!/usr/bin/env python3
"""N35 Storage Audit (tools/audit_storage.py).

Instruments SimStore backing writes (key, byte size, schema conformance),
replays the N30 learner journey + N29 max-length note + N25 200-event cap
corner case, and verifies a scratch undeclared-key write fails by key & module.

Usage:
    python3 tools/audit_storage.py [--artifact output/simulator.html] [--out evidence/N35_STORAGE_RECORD.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, sha256_file  # noqa: E402

DEFAULT_ARTIFACT = DEST / 'output/simulator.html'
DEFAULT_OUT = DEST / 'evidence/N35_STORAGE_RECORD.json'
DECLARED_KEYS = ['sim_colloq1_store_v2']
FOOTPRINT_CAP_BYTES = 262144  # 256 KiB cap for single-key localStorage store

NODE_HARNESS = r"""
'use strict';
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(payload.artifact_path, 'utf8');
const declaredKeys = new Set(payload.declared_keys);
const footprintCap = payload.footprint_cap_bytes;

function buildDom(rawHtml) {
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
  Object.defineProperty(Node.prototype, 'textContent', {
    get() { return this.childNodes.length ? this.childNodes.map((c) => c.textContent).join('') : this._text; },
    set(v) { this.childNodes = []; this._text = String(v === null || v === undefined ? '' : v); }
  });
  Object.defineProperty(Node.prototype, 'innerHTML', {
    get() { return this.textContent; },
    set(v) { this.textContent = v; }
  });
  Node.prototype.appendChild = function (c) { if (c) { c.parentNode = this; this.childNodes.push(c); if (c.id) registry[c.id] = c; } return c; };
  Node.prototype.removeChild = function (c) { const i = this.childNodes.indexOf(c); if (i >= 0) { this.childNodes.splice(i, 1); c.parentNode = null; } return c; };
  Node.prototype.setAttribute = function (k, v) { this.attributes[k] = String(v); if (k === 'id') this.id = v; };
  Node.prototype.getAttribute = function (k) { return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null; };
  Node.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
  Node.prototype.addEventListener = function (ev, fn) { if (!this.listeners[ev]) this.listeners[ev] = []; this.listeners[ev].push(fn); };
  Node.prototype.focus = function () {};
  Node.prototype.querySelector = function () { return null; };
  Node.prototype.querySelectorAll = function () { return []; };

  const scriptRe = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let execScript = '';
  const islandTexts = Object.create(null);
  let m;
  while ((m = scriptRe.exec(rawHtml)) !== null) {
    const attrs = m[1] || '';
    const body = m[2] || '';
    const idMatch = /\bid=["']([^"']+)["']/.exec(attrs);
    const typeMatch = /\btype=["']([^"']+)["']/.exec(attrs);
    if (typeMatch && typeMatch[1] === 'application/json' && idMatch) {
      const node = new Node('SCRIPT', idMatch[1]);
      node.type = 'application/json';
      node.textContent = body;
      islandTexts[idMatch[1]] = body;
    } else if (!typeMatch) {
      execScript = body;
    }
  }
  const metaRe = /<meta\b([^>]*)>/gi;
  while ((m = metaRe.exec(rawHtml)) !== null) {
    const attrs = m[1] || '';
    const nameMatch = /\bname=["']([^"']+)["']/.exec(attrs);
    const contentMatch = /\bcontent=["']([^"']+)["']/.exec(attrs);
    if (nameMatch && contentMatch) {
      const mn = new Node('META');
      mn.setAttribute('name', nameMatch[1]);
      mn.setAttribute('content', contentMatch[1]);
      metas[nameMatch[1]] = mn;
    }
  }
  const idRe = /\bid=["']([A-Za-z0-9_:-]+)["']/g;
  while ((m = idRe.exec(rawHtml)) !== null) {
    if (!registry[m[1]]) new Node('DIV', m[1]);
  }
  const doc = {
    body: new Node('BODY', 'sim-body'),
    documentElement: new Node('HTML', 'sim-html'),
    getElementById(id) { return registry[id] || null; },
    createElement(tag) { return new Node(tag); },
    createTextNode(txt) { const n = new Node('#TEXT'); n.textContent = txt; return n; },
    querySelector(sel) {
      const mm = /^meta\[name=["']([^"']+)["']\]$/.exec(sel);
      if (mm) return metas[mm[1]] || null;
      return null;
    },
    querySelectorAll() { return []; },
    addEventListener() {},
  };
  return { doc, execScript, islandTexts };
}

const { doc, execScript, islandTexts } = buildDom(html);
const sandbox = {
  window: null, self: null, document: doc, console, crypto, TextEncoder, TextDecoder,
  atob: (b) => Buffer.from(b, 'base64').toString('binary'),
  btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
  setTimeout, clearTimeout, Date, Math, JSON, Array, Object, String, Number,
  Boolean, RegExp, Error, TypeError, RangeError, Map, Set, Uint8Array, Uint32Array, Int32Array, Promise,
};
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(execScript, sandbox, { filename: 'output/simulator.html#inline-script' });

function makeInstrumentedStorage() {
  const data = Object.create(null);
  const writeLog = [];
  const violations = [];
  let seq = 0;

  function validateWrite(key, value, moduleName) {
    const bytes = Buffer.byteLength(String(value), 'utf8');
    let schemaValid = true;
    const issues = [];
    if (!declaredKeys.has(key)) {
      schemaValid = false;
      issues.push('E_STORAGE_UNDECLARED_KEY:' + key + ':module=' + moduleName);
      violations.push({
        code: 'E_STORAGE_UNDECLARED_KEY',
        key: key,
        module: moduleName,
        bytes: bytes,
      });
    } else {
      try {
        const parsed = JSON.parse(value);
        if (!parsed || parsed.schema_version !== 2) {
          schemaValid = false;
          issues.push('E_STORAGE_SCHEMA_VERSION');
        }
        if (Array.isArray(parsed.events) && parsed.events.length > 200) {
          schemaValid = false;
          issues.push('E_STORAGE_EVENT_CAP_EXCEEDED');
        }
        if (/"answer_text"/.test(value)) {
          schemaValid = false;
          issues.push('E_STORAGE_ANSWER_TEXT_LEAK');
        }
      } catch (_e) {
        schemaValid = false;
        issues.push('E_STORAGE_INVALID_JSON');
      }
    }
    seq += 1;
    writeLog.push({ seq, key, bytes, schema_valid: schemaValid, issues, module: moduleName });
  }

  return {
    getItem(k) { return Object.prototype.hasOwnProperty.call(data, k) ? data[k] : null; },
    setItem(k, v, moduleName) {
      const mod = moduleName || 'src/store.ts';
      validateWrite(String(k), String(v), mod);
      data[String(k)] = String(v);
    },
    removeItem(k) { delete data[String(k)]; },
    keys() { return Object.keys(data); },
    getWriteLog() { return writeLog.slice(); },
    getViolations() { return violations.slice(); },
  };
}

// 1. Default memory mode: zero backing writes
const memBacking = makeInstrumentedStorage();
const memStore = sandbox.SimStore.createStore({ storage: memBacking, optIn: false });
memStore.update((draft) => {
  draft.progress.topics['1'].practiced = 3;
});
const defaultWrites = memBacking.getWriteLog().length;

// 2. Opted-in full journey + N29 max-length note + N25 200-event cap corner case
const optBacking = makeInstrumentedStorage();
const optStore = sandbox.SimStore.createStore({ storage: optBacking, optIn: true });
const coverage = JSON.parse(islandTexts['sim-coverage']);
const revPolicy = JSON.parse(islandTexts['sim-revision-policy']);
const maxNoteLen = (revPolicy && revPolicy.self_assessment && revPolicy.self_assessment.note_max_length) || 500;
const maxNoteText = ('Āčēģīķļņšūž '.repeat(55)).slice(0, maxNoteLen);

// Replay N30-style journey steps + >200 events (220 events) to prove 200-event cap
for (let i = 0; i < 220; i += 1) {
  const o = coverage.outcomes[i % coverage.outcomes.length];
  const oid = o.outcome_id || o.id;
  optStore.update((draft) => {
    draft.progress.outcomes[oid] = {
      attempted: true,
      first_pass_correct: (i % 2 === 0),
      correct_after_retry: (i % 2 === 1),
      attempts: 1,
    };
    draft.events.push({
      seq: i + 1,
      type: 'task-answered',
      outcome_id: oid,
      topic: o.topic,
      correct: (i % 2 === 0),
    });
  });
}

// Save N29 max-length self-assessment notes on 10 outcomes (composing with 200-event cap)
for (let i = 0; i < 10; i += 1) {
  const o = coverage.outcomes[i];
  const oid = o.outcome_id || o.id;
  sandbox.SimRevision.saveSelfAssessment(optStore, oid, {
    ratings: { C1: 'confident', C2: 'with_effort' },
    note: maxNoteText,
  });
}

const finalState = optStore.getState();
const writeLog = optBacking.getWriteLog();
const maxFootprintBytes = writeLog.reduce((mx, w) => Math.max(mx, w.bytes), 0);
const allSchemaValid = writeLog.every((w) => w.schema_valid);

// 3. Scratch undeclared-key violation fixture
const scratchBacking = makeInstrumentedStorage();
scratchBacking.setItem('sim_undeclared_leak_key', '{"leak":true}', 'scratch-rogue-module.js');
const scratchViolations = scratchBacking.getViolations();

process.stdout.write(JSON.stringify({
  default_mode_writes: defaultWrites,
  journey_writes_count: writeLog.length,
  max_footprint_bytes: maxFootprintBytes,
  footprint_cap_bytes: footprintCap,
  events_len_after_220: finalState.events.length,
  events_pruned_count: finalState.events_pruned_count,
  note_max_length: maxNoteLen,
  all_writes_schema_valid: allSchemaValid,
  final_keys: optBacking.keys(),
  scratch_violation_fixture: {
    detected: scratchViolations.length === 1 && scratchViolations[0].code === 'E_STORAGE_UNDECLARED_KEY',
    violation: scratchViolations[0] || null,
  },
  pass: (
    defaultWrites === 0 &&
    allSchemaValid &&
    maxFootprintBytes <= footprintCap &&
    finalState.events.length === 200 &&
    finalState.events_pruned_count === 20 &&
    optBacking.keys().length === 1 &&
    optBacking.keys()[0] === 'sim_colloq1_store_v2' &&
    scratchViolations.length === 1 &&
    scratchViolations[0].code === 'E_STORAGE_UNDECLARED_KEY'
  ),
}));
"""


def run_audit(artifact_path: Path) -> dict[str, Any]:
    payload = {
        'artifact_path': str(artifact_path),
        'declared_keys': DECLARED_KEYS,
        'footprint_cap_bytes': FOOTPRINT_CAP_BYTES,
    }
    proc = subprocess.run(
        ['node', '-e', NODE_HARNESS],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'audit_storage Node harness failed ({proc.returncode}): {proc.stderr}')
    result = json.loads(proc.stdout)
    return {
        'audit': 'N35_STORAGE',
        'epistemic_status': 'VERIFIED (instrumented Node VM backing store)',
        'artifact_path': str(artifact_path.relative_to(DEST)),
        'artifact_sha256': sha256_file(artifact_path),
        'declared_keys': DECLARED_KEYS,
        **result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    report = run_audit(args.artifact.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(report) + b'\n')
    print(f"  default_mode_writes={report['default_mode_writes']} (expected 0)")
    print(f"  journey_writes={report['journey_writes_count']} max_footprint={report['max_footprint_bytes']} B / {report['footprint_cap_bytes']} B")
    print(f"  events_cap={report['events_len_after_220']}/200 pruned={report['events_pruned_count']} note_max_len={report['note_max_length']}")
    sv = report['scratch_violation_fixture']['violation']
    print(f"  scratch_undeclared_key_fixture={'PASS' if report['scratch_violation_fixture']['detected'] else 'FAIL'} "
          f"(code={sv['code']}, key={sv['key']}, module={sv['module']})")
    print(f"audit_storage {'PASS' if report['pass'] else 'FAIL'} -> {args.out}")
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
