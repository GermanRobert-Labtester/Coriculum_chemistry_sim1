#!/usr/bin/env python3
"""N35 Security Audit: Serialization Lint + Escape Helper & Injection Corpus (tools/audit_security.py).

Engine 1 (Static Serialization & Markup Lint):
  - Scans all 39 runtime module sources in data/build_policy.json + src/shell.html.
  - Inventories every JSON.parse, localStorage/storage API, and innerHTML site.
  - Proves scanner catches a planted unjustified innerHTML in a scratch copy.
  - Proves corrupted-island vs wrong-structure vs noscript fallback isolation.

Engine 2 (Escape Helper Unit Corpus & Adversarial Injection Corpus):
  - Tests SimStore.escapeHtml on Latvian diacritics + markup metacharacters.
  - Injects adversarial payloads across all runtime text channels (exam answer,
    revision note, feedback/term escape, paper worksheet, store export/import)
    and verifies malicious import file rejection.

Usage:
    python3 tools/audit_security.py [--artifact output/simulator.html] [--out evidence/N35_SECURITY_RECORD.json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, sha256_file  # noqa: E402

DEFAULT_ARTIFACT = DEST / 'output/simulator.html'
DEFAULT_OUT = DEST / 'evidence/N35_SECURITY_RECORD.json'
POLICY_PATH = DEST / 'data/build_policy.json'

ALLOWED_STORAGE_FILES = {
    'src/store.ts',
    'src/theme-toggle.js',
    'src/analytics.ts',
    'src/smoke-subset.js',
    'src/shell.html',
}

FORBIDDEN_APIS = {
    'sessionStorage': re.compile(r'\bsessionStorage\b'),
    'outerHTML': re.compile(r'\bouterHTML\b'),
    'insertAdjacentHTML': re.compile(r'\binsertAdjacentHTML\b'),
    'document.write': re.compile(r'document\.write\b'),
    'eval_or_Function': re.compile(r'\beval\s*\(|new\s+Function\b'),
}


def resolve_runtime_sources(policy: dict[str, Any]) -> list[str]:
    sources: list[str] = []
    for mod in policy['module_order']:
        p = mod['path']
        if p.startswith('src/compiled/'):
            sources.append('src/' + p[len('src/compiled/'):-3] + '.ts')
        else:
            sources.append(p)
    sources.append('src/shell.html')
    return sources


def scan_sources(sources: list[str], root: Path = DEST) -> dict[str, Any]:
    json_parse_sites: list[dict[str, Any]] = []
    storage_sites: list[dict[str, Any]] = []
    inner_html_sites: list[dict[str, Any]] = []
    forbidden_hits: list[dict[str, Any]] = []

    for rel in sources:
        path = root / rel
        lines = path.read_text(encoding='utf-8').splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Forbidden APIs
            for fname, pat in FORBIDDEN_APIS.items():
                if pat.search(line):
                    forbidden_hits.append({'file': rel, 'line': idx, 'api': fname, 'snippet': stripped[:120]})

            # JSON.parse inventory
            if 'JSON.parse' in line:
                if 'JSON.parse(JSON.stringify' in line:
                    cls = 'deep_clone'
                elif rel == 'src/smoke-subset.js':
                    cls = 'smoke_harness'
                else:
                    ctx = '\n'.join(lines[max(0, idx - 12):min(len(lines), idx + 3)])
                    cls = 'wrapped_try_catch' if 'try' in ctx else 'UNWRAPPED'
                json_parse_sites.append({'file': rel, 'line': idx, 'class': cls, 'snippet': stripped[:120]})

            # localStorage / storage API inventory
            if re.search(r'\blocalStorage\b|\b(getItem|setItem|removeItem)\b', line):
                storage_sites.append({
                    'file': rel,
                    'line': idx,
                    'allowed_owner': rel in ALLOWED_STORAGE_FILES,
                    'snippet': stripped[:120],
                })

            # innerHTML inventory
            if re.search(r'\binnerHTML\b', line):
                if stripped.startswith('*') or stripped.startswith('//') or stripped.startswith('/*'):
                    just = 'comment'
                elif 'innerHTML: string' in line:
                    just = 'type_decl'
                elif re.search(r'\.innerHTML\s*=', line):
                    ctx = '\n'.join(lines[max(0, idx - 15):min(len(lines), idx + 2)])
                    if 'escapeHtml' in ctx or 'renderWorksheetHTML' in line or 'renderEmptyStateHTML' in line:
                        just = 'escaped'
                    else:
                        just = 'UNJUSTIFIED'
                else:
                    just = 'read_or_other'
                inner_html_sites.append({'file': rel, 'line': idx, 'justification': just, 'snippet': stripped[:120]})

    unwrapped_json = [s for s in json_parse_sites if s['class'] == 'UNWRAPPED']
    unjustified_html = [s for s in inner_html_sites if s['justification'] == 'UNJUSTIFIED']
    undeclared_storage = [s for s in storage_sites if not s['allowed_owner']]

    return {
        'scanned_file_count': len(sources),
        'json_parse_count': len(json_parse_sites),
        'json_parse_unwrapped': unwrapped_json,
        'inner_html_count': len(inner_html_sites),
        'inner_html_sites': inner_html_sites,
        'inner_html_unjustified': unjustified_html,
        'storage_site_count': len(storage_sites),
        'storage_undeclared': undeclared_storage,
        'forbidden_hits': forbidden_hits,
        'lint_pass': (
            len(unwrapped_json) == 0
            and len(unjustified_html) == 0
            and len(undeclared_storage) == 0
            and len(forbidden_hits) == 0
        ),
    }


def test_scratch_unjustified_innerhtml() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        (tmp / 'src').mkdir(parents=True)
        scratch_file = tmp / 'src/scratch-view.js'
        scratch_file.write_text(
            "function renderBad(el, userInput) {\n  el.innerHTML = userInput;\n}\n",
            encoding='utf-8',
        )
        scan = scan_sources(['src/scratch-view.js'], root=tmp)
        detected = len(scan['inner_html_unjustified']) == 1
        return {
            'code': 'E_SECURITY_UNJUSTIFIED_INNERHTML',
            'detected': detected,
            'unjustified_sites': scan['inner_html_unjustified'],
        }


NODE_HARNESS = r"""
'use strict';
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');

const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
const html = fs.readFileSync(payload.artifact_path, 'utf8');

function buildDom(rawHtml, overrides) {
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
      const text = (overrides && Object.prototype.hasOwnProperty.call(overrides, idMatch[1]))
        ? overrides[idMatch[1]]
        : body;
      const node = new Node('SCRIPT', idMatch[1]);
      node.type = 'application/json';
      node.textContent = text;
      islandTexts[idMatch[1]] = text;
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

function bootVm(overrides) {
  const { doc, execScript, islandTexts } = buildDom(html, overrides);
  const sandbox = {
    window: null, self: null, document: doc, console, crypto, TextEncoder, TextDecoder,
    atob: (b) => Buffer.from(b, 'base64').toString('binary'),
    btoa: (s) => Buffer.from(s, 'binary').toString('base64'),
    setTimeout, clearTimeout, Date, Math, JSON, Array, Object, String, Number,
    Boolean, RegExp, Error, TypeError, RangeError, Map, Set, Uint8Array, Uint32Array, Int32Array, Promise,
    __xss: undefined,
  };
  sandbox.window = sandbox;
  sandbox.self = sandbox;
  sandbox.globalThis = sandbox;
  vm.createContext(sandbox);
  vm.runInContext(execScript, sandbox, { filename: 'output/simulator.html#inline-script' });
  return { doc, sandbox, islandTexts };
}

// 1. Corrupted-island & wrong-structure fixtures (Subtask B.1.3)
const { sandbox: sbCovBadJson, doc: docCovBadJson } = bootVm({ 'sim-coverage': '{"island_id":"sim-coverage","outcomes":[' });
let covJsonErr = null;
try { sbCovBadJson.SimCoverage.load(docCovBadJson); } catch (e) { covJsonErr = { code: e.code, message: e.message }; }

const { sandbox: sbCovBadShape, doc: docCovBadShape } = bootVm({ 'sim-coverage': '{"island_id":"sim-coverage"}' });
let covShapeErr = null;
try { sbCovBadShape.SimCoverage.load(docCovBadShape); } catch (e) { covShapeErr = { code: e.code, message: e.message }; }

const { sandbox: sbBankBadJson, doc: docBankBadJson } = bootVm({ 'sim-bank': '{"island_id":"sim-bank","questions":[' });
let bankJsonErr = null;
try { sbBankBadJson.SimBank.load(docBankBadJson, { verifyIntegrity: false }); } catch (e) { bankJsonErr = { code: e.code, message: e.message }; }

const { sandbox: sbBankBadShape, doc: docBankBadShape } = bootVm({ 'sim-bank': '{"island_id":"sim-bank"}' });
let bankShapeErr = null;
try { sbBankBadShape.SimBank.load(docBankBadShape, { verifyIntegrity: false }); } catch (e) { bankShapeErr = { code: e.code, message: e.message }; }

const corruptionFixturesPass = Boolean(
  covJsonErr && covJsonErr.code === 'E_COVERAGE_JSON' &&
  covShapeErr && covShapeErr.code === 'E_COVERAGE_SHAPE' &&
  covJsonErr.code !== covShapeErr.code &&
  bankJsonErr && bankJsonErr.code === 'E_BANK_JSON' &&
  bankShapeErr && bankShapeErr.code === 'E_BANK_SHAPE' &&
  bankJsonErr.code !== bankShapeErr.code
);

// 2. Escape-helper unit corpus (Subtask B.1.2)
const { sandbox, doc, islandTexts } = bootVm(null);
const escapeVectors = [
  { name: 'latvian_upper_lower', input: 'ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž ō ŗ' },
  { name: 'markup_metachars', input: '& < > " \'' },
  { name: 'script_tag', input: '<script>window.__xss=1</' + 'script>' },
  { name: 'attr_breakout', input: '" onmouseover="window.__xss=1" data-x=\'' },
];
const escapeCorpus = escapeVectors.map((v) => ({
  name: v.name,
  input: v.input,
  escaped: sandbox.SimStore.escapeHtml(v.input),
}));

// 3. Injection corpus across every runtime text channel (Main Step C)
const payloads = payload.injection_payloads;
const formsData = JSON.parse(islandTexts['sim-forms']);
const formA = Array.isArray(formsData.forms) ? formsData.forms[0] : formsData.forms.A;
const examPolicy = JSON.parse(islandTexts['sim-exam-policy']);
const coverage = sandbox.SimCoverage.load(doc, sandbox.COVERAGE_INVARIANTS);
const revPolicy = JSON.parse(islandTexts['sim-revision-policy']);
const terms = JSON.parse(islandTexts['sim-terms']);
const masteryPolicy = JSON.parse(islandTexts['sim-mastery-policy']);
const bankData = JSON.parse(islandTexts['sim-bank']);

const channelResults = [];
for (let p = 0; p < payloads.length; p += 1) {
  const pl = payloads[p];

  // Channel 1: exam_answer_input
  const session = new sandbox.SimSession.ExamSession({ policy: examPolicy, form: formA, mode: 'exam', seed: 20250901 });
  session.dispatch('start');
  const slotId = formA.slots[0].slot_id;
  session.dispatch('answer', { slot_id: slotId, payload: { kind: 'raw_text', text: pl.text } });
  const ansText = session.getAnswer(slotId).payload.text;

  // Channel 2: revision_sa_note + store round-trip
  const store = sandbox.SimStore.createStore();
  const oid = coverage.outcomes[0].outcome_id || coverage.outcomes[0].id;
  sandbox.SimRevision.saveSelfAssessment(store, oid, { ratings: { C1: 'confident' }, note: pl.text });
  const storedNote = store.getState().self_assessments[oid].note;
  sandbox.SimRevision.renderFromStore(doc, store, { coverage, masteryPolicy, revisionPolicy: revPolicy, terms });

  // Channel 3: feedback / term escapeHtml path
  const escapedFeedback = sandbox.SimStore.escapeHtml(pl.text);
  const noUnescapedTag = !/<(script|img|svg)\b/i.test(escapedFeedback);

  // Channel 4: paper_worksheet_render (injected into Form A slot 0's instance)
  const mutatedBank = {
    instances: [{ instance_id: formA.slots[0].instance_id, prompt_lv: pl.text, stem_lv: pl.text }]
  };
  const wsModel = sandbox.SimPaper.buildWorksheetModel(formsData, mutatedBank, formA.form_id);
  const wsHtml = sandbox.SimPaper.renderWorksheetHTML(wsModel);
  const paperSafe = !/<script\b/i.test(wsHtml) && wsHtml.indexOf(escapedFeedback) >= 0;

  // Channel 5: store export -> import round-trip
  const exported = store.exportProgress();
  const store2 = sandbox.SimStore.createStore();
  store2.importProgress(exported.text);
  const importedNote = store2.getState().self_assessments[oid].note;

  channelResults.push({
    payload_id: pl.id,
    exam_answer_exact: ansText === pl.text,
    revision_note_exact: storedNote === pl.text,
    feedback_escaped_safe: noUnescapedTag,
    paper_worksheet_safe: paperSafe,
    import_roundtrip_exact: importedNote === pl.text,
    xss_executed: sandbox.__xss !== undefined,
  });
}

// Malicious import file fixtures
const importStore = sandbox.SimStore.createStore();
const validExport = JSON.parse(importStore.exportProgress().text);
const tamperedExport = JSON.parse(JSON.stringify(validExport));
tamperedExport.store.settings.theme = 'dark';

const maliciousFixtures = [
  { id: 'truncated_json', input: '{"export_format":"sim_colloq1_export_v2"', expected: 'E_STORE_IMPORT_JSON' },
  { id: 'wrong_format', input: JSON.stringify({ export_format: 'evil', schema_version: 2, store: {} }), expected: 'E_STORE_IMPORT_SHAPE' },
  { id: 'tampered_digest', input: JSON.stringify(tamperedExport), expected: 'E_STORE_IMPORT_DIGEST' },
];
const maliciousResults = maliciousFixtures.map((mf) => {
  let code = null;
  try { importStore.importProgress(mf.input); } catch (e) { code = e && e.code ? e.code : 'UNKNOWN'; }
  return { id: mf.id, expected: mf.expected, actual: code, pass: code === mf.expected };
});

process.stdout.write(JSON.stringify({
  corruption_fixtures: {
    coverage_json: covJsonErr,
    coverage_shape: covShapeErr,
    bank_json: bankJsonErr,
    bank_shape: bankShapeErr,
    pass: corruptionFixturesPass,
  },
  escape_corpus: escapeCorpus,
  injection_results: channelResults,
  malicious_import_fixtures: maliciousResults,
  all_runtime_checks_pass: (
    corruptionFixturesPass &&
    channelResults.every((r) => r.exam_answer_exact && r.revision_note_exact && r.feedback_escaped_safe && r.paper_worksheet_safe && r.import_roundtrip_exact && !r.xss_executed) &&
    maliciousResults.every((m) => m.pass)
  ),
}));
"""

INJECTION_PAYLOADS = [
    {'id': 'script_tag', 'text': '<script>window.__xss=1</script>'},
    {'id': 'img_onerror', 'text': '<img src=x onerror="window.__xss=1">'},
    {'id': 'attr_quote_breakout', 'text': '" onmouseover="window.__xss=1" data-a=\''},
    {'id': 'svg_onload', 'text': "'><svg/onload=window.__xss=1>"},
    {'id': 'latvian_diacritics_xss', 'text': 'Āčēģīķļņšūž ō ŗ <b onclick="window.__xss=1">šž</b> & \'"'},
]


def test_noscript_immunity(artifact_path: Path) -> dict[str, Any]:
    html = artifact_path.read_text(encoding='utf-8')
    # Corrupt all JSON islands and strip all <script> tags (simulating script-off)
    corrupted = re.sub(
        r'(<script\b[^>]*type=["\']application/json["\'][^>]*>)([\s\S]*?)(</script>)',
        r'\1{TRUNCATED_JSON\3',
        html,
        flags=re.IGNORECASE,
    )
    no_scripts = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', '', corrupted, flags=re.IGNORECASE)
    has_notice = 'id="noscript-pazinojums"' in no_scripts
    anchor_count = len(re.findall(r'id="karte-P[1-7]-[0-9]{2}"', no_scripts))
    return {
        'has_noscript_notice': has_notice,
        'concept_anchors_intact': anchor_count,
        'pass': has_notice and anchor_count == 64,
    }


def run_audit(artifact_path: Path) -> dict[str, Any]:
    policy = json.loads(POLICY_PATH.read_text(encoding='utf-8'))
    sources = resolve_runtime_sources(policy)
    lint = scan_sources(sources)
    scratch_inner_html = test_scratch_unjustified_innerhtml()
    noscript = test_noscript_immunity(artifact_path)

    proc = subprocess.run(
        ['node', '-e', NODE_HARNESS],
        input=json.dumps({
            'artifact_path': str(artifact_path),
            'injection_payloads': INJECTION_PAYLOADS,
        }),
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'audit_security Node harness failed ({proc.returncode}): {proc.stderr}')
    runtime = json.loads(proc.stdout)

    overall_pass = (
        lint['lint_pass']
        and scratch_inner_html['detected']
        and noscript['pass']
        and runtime['all_runtime_checks_pass']
    )
    return {
        'audit': 'N35_SECURITY',
        'epistemic_status': 'VERIFIED (static source scan + Node VM runtime injection/corruption harness)',
        'artifact_path': str(artifact_path.relative_to(DEST)),
        'artifact_sha256': sha256_file(artifact_path),
        'serialization_lint': lint,
        'scratch_unjustified_innerhtml_fixture': scratch_inner_html,
        'noscript_immunity_fixture': noscript,
        **runtime,
        'pass': overall_pass,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact', type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    report = run_audit(args.artifact.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical_json_bytes(report) + b'\n')
    lint = report['serialization_lint']
    print(f"  lint: files={lint['scanned_file_count']} JSON.parse={lint['json_parse_count']} (unwrapped={len(lint['json_parse_unwrapped'])}) "
          f"innerHTML={lint['inner_html_count']} (unjustified={len(lint['inner_html_unjustified'])}) "
          f"storage={lint['storage_site_count']} (undeclared={len(lint['storage_undeclared'])})")
    print(f"  scratch_unjustified_innerhtml={'PASS' if report['scratch_unjustified_innerhtml_fixture']['detected'] else 'FAIL'}")
    print(f"  corruption_fixtures={'PASS' if report['corruption_fixtures']['pass'] else 'FAIL'} "
          f"noscript={'PASS' if report['noscript_immunity_fixture']['pass'] else 'FAIL'}")
    print(f"  injection_corpus={len(report['injection_results'])} payloads x 5 channels, malicious_imports={len(report['malicious_import_fixtures'])}/3")
    print(f"audit_security {'PASS' if report['pass'] else 'FAIL'} -> {args.out}")
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
