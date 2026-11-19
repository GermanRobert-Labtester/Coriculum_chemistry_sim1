#!/usr/bin/env python3
"""N35 Performance Audit (tools/audit_perf.py).

Measures deterministic synthetic workloads in a Node VM scratch harness over
output/simulator.html (all 112 bank instances eligible, 3 N26 learner profiles,
21-slot Form A exam navigator + revision panel interactions) and verifies a
degraded per-keystroke full-view re-render scratch fixture fails the budget.

Epistemic note: all timings are Node VM scratch-harness measurements, not
browser paint timings (browser confirmation is staged for N38 smoke).

Usage:
    python3 tools/audit_perf.py [--artifact output/simulator.html] [--out evidence/N35_PERF_RECORD.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prng  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402

DEFAULT_ARTIFACT = DEST / 'output/simulator.html'
DEFAULT_OUT = DEST / 'evidence/N35_PERF_RECORD.json'
WORKLOAD_SEED = 20250901  # N05 SplitMix64 seed

BUDGET_CEILINGS_MS = {
    'island_parse': 150.0,
    'first_render_start': 50.0,
    'exam_navigator_interaction_max': 25.0,
    'revision_panel_interaction_max': 40.0,
    'keystroke_burst_30_chars': 25.0,
}

NODE_HARNESS = r"""
'use strict';
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(payload.artifact_path, 'utf8');
const budgets = payload.budgets;
const workload = payload.workload;

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
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  };
  Node.prototype.removeAttribute = function (k) { delete this.attributes[k]; };
  Node.prototype.addEventListener = function (ev, fn) {
    if (!this.listeners[ev]) this.listeners[ev] = [];
    this.listeners[ev].push(fn);
  };
  Node.prototype.dispatchEvent = function (ev) {
    const list = this.listeners[ev.type] || [];
    for (let i = 0; i < list.length; i += 1) list[i](ev);
  };
  Node.prototype.focus = function () {};
  Node.prototype.scrollIntoView = function () {};
  Node.prototype.querySelector = function (sel) {
    const m = /^#([A-Za-z0-9_:-]+)$/.exec(sel);
    if (m) return registry[m[1]] || null;
    return null;
  };
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
      const metaNode = new Node('META');
      metaNode.setAttribute('name', nameMatch[1]);
      metaNode.setAttribute('content', contentMatch[1]);
      metas[nameMatch[1]] = metaNode;
    }
  }

  const idRe = /\bid=["']([A-Za-z0-9_:-]+)["']/g;
  while ((m = idRe.exec(rawHtml)) !== null) {
    if (!registry[m[1]]) new Node('DIV', m[1]);
  }

  const bodyNode = new Node('BODY', 'sim-body');
  const docEl = new Node('HTML', 'sim-html');
  const doc = {
    body: bodyNode,
    documentElement: docEl,
    getElementById(id) { return registry[id] || null; },
    createElement(tag) { return new Node(tag); },
    createTextNode(txt) { const n = new Node('#TEXT'); n.textContent = txt; return n; },
    querySelector(sel) {
      const mm = /^meta\[name=["']([^"']+)["']\]$/.exec(sel);
      if (mm) return metas[mm[1]] || null;
      const im = /^#([A-Za-z0-9_:-]+)$/.exec(sel);
      if (im) return registry[im[1]] || null;
      return null;
    },
    querySelectorAll() { return []; },
    addEventListener() {},
  };

  return { doc, execScript, islandTexts };
}

const { doc, execScript, islandTexts } = buildDom(html);
const sandbox = {
  window: null,
  self: null,
  document: doc,
  console,
  crypto,
  TextEncoder,
  TextDecoder,
  atob: (b) => Buffer.from(b, 'base64').toString('binary'),
  btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
  setTimeout,
  clearTimeout,
  Date,
  Math,
  JSON,
  Array,
  Object,
  String,
  Number,
  Boolean,
  RegExp,
  Error,
  TypeError,
  RangeError,
  Map,
  Set,
  Uint8Array,
  Uint32Array,
  Int32Array,
  Promise,
};
sandbox.window = sandbox;
sandbox.self = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);
vm.runInContext(execScript, sandbox, { filename: 'output/simulator.html#inline-script' });

function msSince(t0) {
  return Number(process.hrtime.bigint() - t0) / 1e6;
}

// 1. Island parse measurement (all JSON islands, including full 112-instance bank)
const tParse0 = process.hrtime.bigint();
const parsedIslands = {};
const islandIds = Object.keys(islandTexts);
for (let i = 0; i < islandIds.length; i += 1) {
  const id = islandIds[i];
  parsedIslands[id] = JSON.parse(islandTexts[id]);
}
const islandParseMs = msSince(tParse0);

const bankObj = sandbox.SimBank.load(doc, { verifyIntegrity: true });
const coverageObj = sandbox.SimCoverage.load(doc, sandbox.COVERAGE_INVARIANTS);
const bankList = bankObj.questions || bankObj.instances || parsedIslands['sim-bank'].questions || [];
const eligibleCount = Array.isArray(bankList) ? bankList.length : 0;

// 2. First render of start screen
const tStart0 = process.hrtime.bigint();
sandbox.SimStartView.renderStartTopics(coverageObj, doc);
sandbox.SimCoverage.render(coverageObj, doc);
const firstRenderStartMs = msSince(tStart0);

// 3. Exam navigator interaction (21-slot Form A)
const formsData = parsedIslands['sim-forms'];
const formA = Array.isArray(formsData.forms)
  ? (formsData.forms.find((f) => f.form_id === 'A') || formsData.forms[0])
  : formsData.forms.A;
const policyData = parsedIslands['sim-exam-policy'];
const session = new sandbox.SimSession.ExamSession({
  policy: policyData,
  form: formA,
  mode: 'exam',
  seed: 20250901,
});
session.dispatch('start');
const instancesById = Object.create(null);
for (let i = 0; i < bankList.length; i += 1) {
  instancesById[bankList[i].instance_id] = bankList[i];
}
const examShell = new sandbox.SimExam.ExamShell({
  doc: doc,
  session: session,
  policy: policyData,
  instancesById: instancesById,
  confirm: false,
});
examShell.render();

const examLatencies = [];
for (let i = 0; i < workload.slot_indices.length; i += 1) {
  const slotId = formA.slots[workload.slot_indices[i]].slot_id;
  const t0 = process.hrtime.bigint();
  examShell.navigate(slotId);
  if (i % 5 === 0) examShell.toggleFlag(slotId);
  examLatencies.push(msSince(t0));
}
const examNavMaxMs = Math.max(...examLatencies);
const examNavMeanMs = examLatencies.reduce((a, b) => a + b, 0) / examLatencies.length;

// 3b. Fixed incremental keystroke burst (30 chars) vs Degraded full-render keystroke burst
let fullRenderCount = 0;
const origRender = examShell.render.bind(examShell);
examShell.render = function () {
  fullRenderCount += 1;
  return origRender();
};

const tFixedKeys0 = process.hrtime.bigint();
for (let k = 1; k <= workload.keystrokes.length; k += 1) {
  examShell.recordAnswer(formA.slots[0].slot_id, { kind: 'raw_text', text: workload.keystrokes.slice(0, k) }, { incremental: true });
}
const fixedKeystrokeBurstMs = msSince(tFixedKeys0);
const fixedFullRenderCount = fullRenderCount;

// Degraded scratch fixture: per-keystroke full-view re-render (no { incremental: true })
fullRenderCount = 0;
const tDegKeys0 = process.hrtime.bigint();
for (let k = 1; k <= workload.keystrokes.length; k += 1) {
  examShell.recordAnswer(formA.slots[0].slot_id, { kind: 'raw_text', text: workload.keystrokes.slice(0, k) });
}
const degradedKeystrokeBurstMs = msSince(tDegKeys0);
const degradedFullRenderCount = fullRenderCount;

// 4. Revision panel interaction across 3 N26 profiles (fresh, mid_progress, near_complete)
const revLatencies = [];
const store = sandbox.SimStore.createStore();
function makeProfileState(kind) {
  const st = sandbox.SimStore.createDefaultState();
  const limit = kind === 'fresh' ? 0 : (kind === 'mid_progress' ? 32 : 60);
  for (let i = 0; i < limit && i < coverageObj.outcomes.length; i += 1) {
    const o = coverageObj.outcomes[i];
    const oid = o.outcome_id || o.id;
    st.progress.outcomes[oid] = {
      attempted: true,
      first_pass_correct: (i % 3 !== 0),
      correct_after_retry: (i % 3 === 0),
      attempts: 1 + (i % 2),
    };
    st.events.push({
      seq: i + 1,
      type: 'task-answered',
      outcome_id: oid,
      topic: o.topic,
      correct: (i % 3 !== 0),
    });
  }
  return st;
}
const profileKinds = ['fresh', 'mid_progress', 'near_complete'];
for (let p = 0; p < profileKinds.length; p += 1) {
  store.setState(makeProfileState(profileKinds[p]));
  const t0 = process.hrtime.bigint();
  sandbox.SimRevision.renderFromStore(doc, store, {
    coverage: coverageObj,
    masteryPolicy: parsedIslands['sim-mastery-policy'],
    revisionPolicy: parsedIslands['sim-revision-policy'],
    terms: parsedIslands['sim-terms'],
  });
  revLatencies.push(msSince(t0));
}
const revMaxMs = Math.max(...revLatencies);
const revMeanMs = revLatencies.reduce((a, b) => a + b, 0) / revLatencies.length;

const rows = [
  {
    id: 'island_parse',
    label: 'All JSON islands parse (112/112 bank instances)',
    measured_ms: Number(islandParseMs.toFixed(3)),
    ceiling_ms: budgets.island_parse,
    pass: islandParseMs <= budgets.island_parse,
  },
  {
    id: 'first_render_start',
    label: 'First interactive start screen render',
    measured_ms: Number(firstRenderStartMs.toFixed(3)),
    ceiling_ms: budgets.first_render_start,
    pass: firstRenderStartMs <= budgets.first_render_start,
  },
  {
    id: 'exam_navigator_interaction',
    label: 'Exam navigator per-interaction max latency (21 slots)',
    measured_ms: Number(examNavMaxMs.toFixed(3)),
    mean_ms: Number(examNavMeanMs.toFixed(3)),
    ceiling_ms: budgets.exam_navigator_interaction_max,
    pass: examNavMaxMs <= budgets.exam_navigator_interaction_max,
  },
  {
    id: 'revision_panel_interaction',
    label: 'Revision panel render max latency (3 N26 profiles)',
    measured_ms: Number(revMaxMs.toFixed(3)),
    mean_ms: Number(revMeanMs.toFixed(3)),
    ceiling_ms: budgets.revision_panel_interaction_max,
    pass: revMaxMs <= budgets.revision_panel_interaction_max,
  },
  {
    id: 'keystroke_burst_incremental',
    label: 'Exam answer 30-char typing burst (incremental fix)',
    measured_ms: Number(fixedKeystrokeBurstMs.toFixed(3)),
    full_renders: fixedFullRenderCount,
    ceiling_ms: budgets.keystroke_burst_30_chars,
    pass: fixedKeystrokeBurstMs <= budgets.keystroke_burst_30_chars && fixedFullRenderCount === 0,
  },
];

// Degraded fixture must be flagged as FAIL (either exceeding burst ceiling or >0 full renders per keystroke)
const degradedFlagged = (degradedFullRenderCount === workload.keystrokes.length) && (
  degradedKeystrokeBurstMs > budgets.keystroke_burst_30_chars || degradedFullRenderCount > 0
);

process.stdout.write(JSON.stringify({
  eligible_instances: eligibleCount,
  island_count: islandIds.length,
  rows,
  degraded_fixture: {
    defect_id: 'E_PERF_KEYSTROKE_RERENDER_BUDGET',
    keystrokes: workload.keystrokes.length,
    full_renders_triggered: degradedFullRenderCount,
    measured_ms: Number(degradedKeystrokeBurstMs.toFixed(3)),
    fixed_measured_ms: Number(fixedKeystrokeBurstMs.toFixed(3)),
    fixed_full_renders: fixedFullRenderCount,
    detected: degradedFlagged,
  },
  all_passed: rows.every((r) => r.pass) && eligibleCount === 112 && degradedFlagged,
}));
"""


def build_workload() -> dict[str, Any]:
    stream = prng.create_stream(WORKLOAD_SEED)
    slot_indices = stream.shuffle(list(range(21)))

    return {
        'seed': WORKLOAD_SEED,
        'slot_indices': slot_indices,
        'keystrokes': 'CH3COOH + NaOH -> CH3COONa + H2O',
        'profiles': ['fresh', 'mid_progress', 'near_complete'],
    }


def run_audit(artifact_path: Path) -> dict[str, Any]:
    workload = build_workload()
    payload = {
        'artifact_path': str(artifact_path),
        'budgets': BUDGET_CEILINGS_MS,
        'workload': workload,
    }
    proc = subprocess.run(
        ['node', '-e', NODE_HARNESS],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'audit_perf Node harness failed ({proc.returncode}): {proc.stderr}')
    result = json.loads(proc.stdout)
    return {
        'audit': 'N35_PERF',
        'epistemic_status': 'VERIFIED (Node VM scratch-harness measurement; browser timing staged for N38 smoke)',
        'artifact_path': str(artifact_path.relative_to(DEST)),
        'artifact_sha256': sha256_file(artifact_path),
        'workload_seed': WORKLOAD_SEED,
        'eligible_instances': result['eligible_instances'],
        'island_count': result['island_count'],
        'budget_rows': result['rows'],
        'degraded_fixture': result['degraded_fixture'],
        'pass': bool(result['all_passed']),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    report = run_audit(args.artifact.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(report) + b'\n')
    for row in report['budget_rows']:
        status = 'PASS' if row['pass'] else 'FAIL'
        print(f"  [{status}] {row['id']}: {row['measured_ms']} ms (ceiling {row['ceiling_ms']} ms)")
    deg = report['degraded_fixture']
    print(f"  [{'PASS' if deg['detected'] else 'FAIL'}] degraded_fixture ({deg['defect_id']}): "
          f"{deg['measured_ms']} ms / {deg['full_renders_triggered']} full renders vs "
          f"fixed {deg['fixed_measured_ms']} ms / {deg['fixed_full_renders']} full renders")
    print(f"audit_perf {'PASS' if report['pass'] else 'FAIL'}: eligible={report['eligible_instances']}/112 -> {args.out}")
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
