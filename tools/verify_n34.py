#!/usr/bin/env python3
"""N34 verification harness: runs all N34 fixtures, three-mode isolation,
two-run rebuild parity, and writes evidence/N34_CORPUS_RECORD.json.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

DEST = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEST / 'tools'))

import byte_budget  # noqa: E402
import check_artifact  # noqa: E402
import check_contrast  # noqa: E402
from n34_noscript import render_noscript_html  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_node_paper_fixtures(html_path: Path, form_a_path: Path) -> dict[str, Any]:
    js = r"""
const fs = require('fs');
const vm = require('vm');
const crypto = require('crypto');

const html = fs.readFileSync(process.argv[1], 'utf8');
const formA = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function extractIsland(id) {
  const re = new RegExp(`<script[^>]*id="${id}"[^>]*>([\\s\\S]*?)</script>`);
  const m = html.match(re);
  return m ? JSON.parse(m[1]) : null;
}

const formsData = extractIsland('sim-forms');
const bankData = extractIsland('sim-bank');

const paperCode = fs.readFileSync('src/compiled/paper.js', 'utf8');
const sandbox = { console, JSON, Object, Array, String, Number, Boolean, RegExp, Math, globalThis: null };
sandbox.globalThis = sandbox;
vm.runInNewContext(paperCode, sandbox);
const SimPaper = sandbox.SimPaper;

const m1 = SimPaper.buildWorksheetModel(formsData, bankData, 'A');
const m2 = SimPaper.buildWorksheetModel(formsData, bankData, 'A');
const h1 = SimPaper.renderWorksheetHTML(m1);
const h2 = SimPaper.renderWorksheetHTML(m2);
const d1 = crypto.createHash('sha256').update(h1, 'utf8').digest('hex');
const d2 = crypto.createHash('sha256').update(h2, 'utf8').digest('hex');

const slotParity = m1.slots.length === formA.slots.length && m1.slots.every((s, idx) => {
  const ref = formA.slots[idx];
  return s.slot_id === ref.slot_id && s.topic === ref.topic && s.points === ref.points && s.type_id === ref.type_id && s.instance_id === ref.instance_id;
});

const hasInteractiveInWorksheet = /<(input|textarea|select|button)\b/i.test(h1);

// Shortage & empty-state fixture
const shortageForms = {
  forms: {
    A: { form_id: 'A', status: 'AVAILABLE', slots: formA.slots },
    B: { form_id: 'B', status: 'FAILED', slots: [] },
    C: { form_id: 'C', status: 'AVAILABLE', slots: formA.slots }
  }
};
const shortageAvail = SimPaper.getAvailableForms(shortageForms).map(f => f.form_id);
const emptyAvail = SimPaper.getAvailableForms({ forms: { A: { form_id: 'A', status: 'FAILED', slots: [] } } });
const emptyHtml = SimPaper.renderEmptyStateHTML();

// Three-mode DOM mock for screen & print theme
const docClasses = new Set(['theme-dark']);
const mockElements = {
  'sim-forms': { textContent: JSON.stringify(formsData) },
  'sim-bank': { textContent: JSON.stringify(bankData) },
  'paper-form-select': { innerHTML: '', value: 'A', disabled: false, addEventListener() {} },
  'settings-paper-form-select': { innerHTML: '', value: 'A', disabled: false, addEventListener() {} },
  'paper-worksheet-output': { innerHTML: '' },
  'paper-print-btn': { innerHTML: '', addEventListener() {} }
};
const mockDoc = {
  getElementById(id) { return mockElements[id] || null; },
  documentElement: {
    classList: {
      add(c) { docClasses.add(c); },
      remove(c) { docClasses.delete(c); },
      contains(c) { return docClasses.has(c); }
    }
  }
};
const initRes = SimPaper.init(mockDoc);
SimPaper.applyPrintTheme(mockDoc, true);
const printThemeActive = docClasses.has('theme-print');

console.log(JSON.stringify({
  available_forms: SimPaper.getAvailableForms(formsData).map(f => f.form_id),
  digest_run1: d1,
  digest_run2: d2,
  deterministic: d1 === d2,
  slot_count: m1.slots.length,
  total_points: m1.total_points,
  n24_slot_parity: slotParity,
  has_interactive_in_worksheet: hasInteractiveInWorksheet,
  shortage_available: shortageAvail,
  empty_available_count: emptyAvail.length,
  empty_state_has_marker: emptyHtml.includes('paper-empty-state'),
  screen_init: initRes,
  print_theme_class_applied: printThemeActive,
  worksheet_chars: h1.length
}));
"""
    proc = subprocess.run(
        ['node', '-e', js, str(html_path), str(form_a_path)],
        cwd=str(DEST),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout.strip())


def main() -> int:
    html_path = DEST / 'output' / 'simulator.html'
    manifest_path = DEST / 'output' / 'build-manifest.json'
    html_text = html_path.read_text(encoding='utf-8')

    # A.1.1 Single-sourcing generation fixture
    coverage = json.loads((DEST / 'data' / 'coverage.json').read_text(encoding='utf-8'))
    anchor_registry = json.loads((DEST / 'data' / 'anchor_registry.json').read_text(encoding='utf-8'))
    concept_summaries = json.loads((DEST / 'data' / 'concept_summaries.json').read_text(encoding='utf-8'))
    conventions = json.loads((DEST / 'data' / 'conventions.json').read_text(encoding='utf-8'))
    terms_data = json.loads((DEST / 'data' / 'terms.json').read_text(encoding='utf-8'))

    scratch_terms = copy.deepcopy(terms_data)
    scratch_marker = 'N34-SINGLE-SOURCE-DRIFT-PROOF-MARKER'
    scratch_terms['terms'][0]['text_lv'] = f"{scratch_terms['terms'][0]['text_lv']} [{scratch_marker}]"
    scratch_noscript = render_noscript_html(coverage, anchor_registry, concept_summaries, conventions, scratch_terms)
    single_source_pass = scratch_marker in scratch_noscript

    # A.1.2 Noscript link-integrity + scratch dangling link
    noscript_pass = check_artifact.check_noscript_fallback(html_text, expected_term_count=len(terms_data['terms']))
    dangling_html = html_text.replace('</noscript>', '<a href="#neeksistejoss-enkurs">Dangling</a></noscript>', 1)
    dangling_res = check_artifact.check_noscript_fallback(dangling_html)
    dangling_caught = (
        dangling_res['status'] == 'FAIL'
        and any('#neeksistejoss-enkurs' in e and 'E_NOSCRIPT_DANGLING_LINK' in e for e in dangling_res['errors'])
    )

    # B.1.1 Print theme contrast
    tokens_data = json.loads((DEST / 'data' / 'tokens.json').read_text(encoding='utf-8'))
    print_contrast = check_contrast.check_contrast_pairs(tokens_data, theme_names=('print',))

    # B.1.2 Paper worksheet determinism, N24 slot parity, empty state
    paper_fixtures = run_node_paper_fixtures(html_path, DEST / 'output' / 'forms' / 'form_A.json')

    # B.1.3 Print-rule static validation + scratch unmatched selector failure
    print_rules_pass = check_artifact.check_print_rules(html_text)
    bad_print_html = html_text.replace('</style>', '@media print { .nonexistent-chrome-typo { display: none; } }\n</style>', 1)
    bad_print_res = check_artifact.check_print_rules(bad_print_html)
    unmatched_caught = (
        bad_print_res['status'] == 'FAIL'
        and any('.nonexistent-chrome-typo' in e and 'E_PRINT_UNMATCHED_SELECTOR' in e for e in bad_print_res['errors'])
    )

    # C.1.2 Two-run rebuild parity
    run1_html_sha = sha256_file(html_path)
    run1_manifest_sha = sha256_file(manifest_path)
    subprocess.run([sys.executable, 'tools/build.py'], cwd=str(DEST), check=True, capture_output=True, text=True)
    run2_html_sha = sha256_file(html_path)
    run2_manifest_sha = sha256_file(manifest_path)
    parity_pass = (run1_html_sha == run2_html_sha) and (run1_manifest_sha == run2_manifest_sha)

    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    budgets = byte_budget.measure_budgets(manifest)

    # Smoke runtime check
    smoke_proc = subprocess.run(['node', 'tools/check_n31_runtime.js'], cwd=str(DEST), capture_output=True, text=True, check=True)

    record = {
        'task': 'N34',
        'status': 'PASS' if (
            single_source_pass
            and noscript_pass['status'] == 'PASS'
            and dangling_caught
            and print_contrast['status'] == 'PASS'
            and paper_fixtures['deterministic']
            and paper_fixtures['n24_slot_parity']
            and not paper_fixtures['has_interactive_in_worksheet']
            and paper_fixtures['empty_available_count'] == 0
            and paper_fixtures['empty_state_has_marker']
            and print_rules_pass['status'] == 'PASS'
            and unmatched_caught
            and parity_pass
            and budgets['status'] == 'PASS'
        ) else 'FAIL',
        'single_source_fixture': {'status': 'PASS' if single_source_pass else 'FAIL', 'marker': scratch_marker},
        'noscript_check': noscript_pass,
        'dangling_link_fixture': {'status': 'PASS' if dangling_caught else 'FAIL', 'errors': dangling_res['errors']},
        'print_contrast': {'status': print_contrast['status'], 'pairs_checked': print_contrast['pairs_checked']},
        'print_policy': tokens_data.get('print_policy'),
        'paper_fixtures': paper_fixtures,
        'print_rules_check': print_rules_pass,
        'unmatched_selector_fixture': {'status': 'PASS' if unmatched_caught else 'FAIL', 'errors': bad_print_res['errors']},
        'two_run_parity': {
            'status': 'PASS' if parity_pass else 'FAIL',
            'run1_html_sha256': run1_html_sha,
            'run2_html_sha256': run2_html_sha,
            'run1_manifest_sha256': run1_manifest_sha,
            'run2_manifest_sha256': run2_manifest_sha,
        },
        'budgets': budgets,
        'smoke_runtime': smoke_proc.stdout.strip(),
    }

    out_path = DEST / 'evidence' / 'N34_CORPUS_RECORD.json'
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N34 verification {record['status']}: html_sha256={run2_html_sha[:16]}... parity={parity_pass} smoke={record['smoke_runtime']}")
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
