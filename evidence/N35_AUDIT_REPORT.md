# N35 Performance, Storage, and Security Audit Report

**Date:** 2026-11-19 | **Task:** N35 | **Phase:** Phase VII | **Status:** `PASS`
**Epistemic Scope:** All timing, storage-write, corruption, and injection checks are `VERIFIED` as **Node VM scratch-harness measurements and static source scans** over `output/simulator.html` (`99fd5c406950be1739b1d3480645d1698ed03eac6558f706d9f2c85b5f11745a`, `2,832,984` B). They are **not browser paint timings**; browser-side timing confirmation is staged for **N38** smoke.

---

## 1. Deliverables, Refactored Modules, and SHA-256 Digests

| Artifact / Touchpoint | Role | SHA-256 |
|---|---|---|
| [`tools/audit_perf.py`](../tools/audit_perf.py) | Deterministic SplitMix64 (`20250901`) performance harness & degraded keystroke fixture | `4c366eeb01fd0ffcd6ec161171708dc5bc8704b045eab22539049348cbbc07b0` |
| [`tools/audit_storage.py`](../tools/audit_storage.py) | Instrumented store write-log, N30+N29+N25 footprint cap & undeclared-key fixture | `f13dd1c2d4d4bb64266e54e9ed5ad33925213ebb1ac35afd7f8e024260f31bbb` |
| [`tools/audit_security.py`](../tools/audit_security.py) | Serialization/markup lint, corruption/noscript fixtures, escape & injection corpus | `07bd30baf7e17f1aa66aeb65cd0b041d5c00f4821074cf715f55046d9b920f21` |
| [`src/store.ts`](../src/store.ts) / [`src/compiled/store.js`](../src/compiled/store.js) | Added canonical `SimStore.escapeHtml` helper & schema/digest-validated `importProgress` | `e7ff78641b356e060428ed2bdf1db136dec73b65a4fa5fd7abb5d2760021bee3` |
| [`src/exam.ts`](../src/exam.ts) / [`src/compiled/exam.js`](../src/compiled/exam.js) | Fixed per-keystroke full-view re-render in `#exam-answer-input` via `{ incremental: true }` | `239cb1ee1cb13d80b6f8bce4d3a22ddd855746942913219da93aaedea868aa4b` |
| [`src/feedback.ts`](../src/feedback.ts) / [`src/paper.ts`](../src/paper.ts) | Delegated `escapeHtml` to `SimStore.escapeHtml` | `1abc6b2928a9c8c94cbcb1232a64a954bff8f53c50d87b0ac72026d92ac988ef` / `84c094fe47c48dd98b7db22c204b31194441afb41c57a99a40113f86637028d0` |
| [`src/method-card-view.js`](../src/method-card-view.js) | Wrapped `JSON.parse` inside `unseal()` with `E_METHOD_CARD_JSON` | `63cbd00f137fa5441db145b3806e1e3434b92d39ae96ca0a61c8694036ceaf9d` |
| [`src/chain-view.js`](../src/chain-view.js) | Wrapped `JSON.parse` inside `unseal()` with `E_CHAIN_JSON` | `477d08ace64a93b6de5f0678eb9f43236f2d8e40d991105c63c6f0212c8edff3` |
| [`src/smoke-subset.js`](../src/smoke-subset.js) | Added `SMK-N35-ESCAPE-HELPER` (`31/31` smoke vectors PASS) | `7cb22597d7a64040b91285842399c5119f3937a47403636d212b3a11d3325518` |
| [`output/simulator.html`](../output/simulator.html) | Rebuilt offline deliverable (`30/30` build gates PASS) | `99fd5c406950be1739b1d3480645d1698ed03eac6558f706d9f2c85b5f11745a` |
| [`output/build-manifest.json`](../output/build-manifest.json) | Rebuilt manifest (`39` modules, `30/30` gates PASS) | `4cdee3e440a41f2793d4eb5b859449ec069b0271341b0be8b3b04de744198a51` |
| [`evidence/N35_PERF_RECORD.json`](N35_PERF_RECORD.json) | Machine-readable performance audit output | `b1d3966d83e90ff81703f8d6bc3f370fdc338eb6c65a48b0a0f564b0eb39b56b` |
| [`evidence/N35_STORAGE_RECORD.json`](N35_STORAGE_RECORD.json) | Machine-readable storage audit output (2-run parity verified) | `62b3d9ee5bba44088dcb9a37157963c5cfb8f76d533d2f82c24af22068340574` |
| [`evidence/N35_SECURITY_RECORD.json`](N35_SECURITY_RECORD.json) | Machine-readable security audit output (2-run parity verified) | `db5f090fb2795b248005b59f08371836bcd724c248bbaf6b93d1d3a254ebc12a` |

---

## 2. Performance Audit (`tools/audit_perf.py`) — `VERIFIED` (Node VM Scratch Harness)

**Workload:** Deterministic SplitMix64 seed `20250901`, full bank (`112/112` instances eligible), 21-slot Form A exam navigator, 3 N26 learner profiles (`fresh`, `mid_progress`, `near_complete`), and 32-char keystroke burst.

| Budget Row | Measured (ms) | Ceiling (ms) | Status |
|---|---|---|---|
| All JSON islands parse (`12` islands, `112/112` bank instances) | `4.067` | `150.0` | `PASS` |
| First interactive start screen render | `0.266` | `50.0` | `PASS` |
| Exam navigator per-interaction max (`21` slots) | `0.383` (mean `0.253`) | `25.0` | `PASS` |
| Revision panel render max (`3` N26 profiles) | `27.026` | `40.0` | `PASS` |
| Exam answer 32-char typing burst (incremental fix) | `2.368` (`0` full renders) | `25.0` | `PASS` |

- **Co-evolution Fix (Subtask A.1.3):** `src/exam.ts` previously called `this.render()` on every `input` event in `#exam-answer-input`, causing `32` full-view re-renders per 32-char burst (and destroying input focus). Refactored to `recordAnswer(slotId, payload, { incremental: true })` updating only `renderNavigator` + `renderMap` (`0` full renders per keystroke). The degraded fixture (`E_PERF_KEYSTROKE_RERENDER_BUDGET`) triggers `32` full renders and is flagged `FAIL` by the audit.

---

## 3. Storage Audit (`tools/audit_storage.py`) — `VERIFIED` (Instrumented Store)

| Check | Measured | Cap / Policy | Status |
|---|---|---|---|
| Default `memory` mode backing writes | `0` writes | `0` writes | `PASS` |
| Opted-in journey writes (`220` events + `10` N29 `500`-char notes) | `230` writes, `100%` schema-valid | `sim_colloq1_store_v2` only | `PASS` |
| Maximum store footprint | `32,521` B | `262,144` B (`256` KiB) | `PASS` |
| Event log cap composition (`max_events = 200` + `note_max_length = 500`) | `200` retained, `20` pruned | Oldest-first pruning | `PASS` |
| Scratch undeclared-key fixture (`scratch-rogue-module.js` → `sim_undeclared_leak_key`) | Flagged `E_STORAGE_UNDECLARED_KEY` | Names key & module | `PASS` |

---

## 4. Security Audit (`tools/audit_security.py`) — `VERIFIED` (Static Scan + Node VM)

### 4.1 Serialization & Markup Inventory (`40` files: `39` modules + `src/shell.html`)
- **`JSON.parse`:** `64` sites total — `0` unwrapped runtime sites (wrapped `unseal()` in `src/method-card-view.js` and `src/chain-view.js`; remaining sites are `try/catch` island/store parsers, `JSON.parse(JSON.stringify(...))` deep clones, or `src/smoke-subset.js` test vectors).
- **`innerHTML`:** `7` occurrences total — `0` unjustified sites (`3` comment-only lines, `1` TypeScript interface property `innerHTML: string`, `3` assignments in `src/paper.ts` all escaping dynamic data via `escapeHtml` → `SimStore.escapeHtml`).
- **Storage APIs:** `45` references across `5` declared owner/test files — `0` undeclared storage accesses, `0` `sessionStorage`, `0` `eval`/`new Function`, `0` `outerHTML`/`insertAdjacentHTML`/`document.write`.
- **Scratch Unjustified `innerHTML` Fixture:** Planted `el.innerHTML = userInput;` in scratch copy → detected and failed with `E_SECURITY_UNJUSTIFIED_INNERHTML`.

### 4.2 Corruption, Structure & `<noscript>` Immunity Fixtures
- `#sim-coverage` truncated JSON → `E_COVERAGE_JSON` vs missing `outcomes` → `E_COVERAGE_SHAPE` (distinct, named, honest).
- `#sim-bank` truncated JSON → `E_BANK_JSON` vs missing `questions` → `E_BANK_SHAPE` (distinct, named, honest).
- `<noscript>` path with all JSON islands corrupted and `<script>` stripped → `#noscript-pazinojums` + all `64` concept anchors (`karte-P1-01`..`karte-P7-09`) intact.

### 4.3 Escape Helper & Injection Corpus (`5` payloads × `5` channels)
- `SimStore.escapeHtml` preserves `ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž ō ŗ` verbatim while escaping `& < > " '`.
- All `5` adversarial payloads (`script_tag`, `img_onerror`, `attr_quote_breakout`, `svg_onload`, `latvian_diacritics_xss`) across `exam_answer_input`, `revision_sa_note`, `feedback_escape_render`, `paper_worksheet_render`, and `store_import_path` rendered as text only with `0` XSS executions and byte-identical storage round-trips.
- Malicious import fixtures rejected `3/3`: `truncated_json` (`E_STORE_IMPORT_JSON`), `wrong_format` (`E_STORE_IMPORT_SHAPE`), `tampered_digest` (`E_STORE_IMPORT_DIGEST`).

---

## 5. Rebuild, Smoke, and Handoffs

- **Runtime Smoke:** `node tools/check_n31_runtime.js` → `PASS` (`modules=39/39 globals=37 islands=22/22 smoke=31/31`, including `SMK-N35-ESCAPE-HELPER`).
- **Two-Run Parity:** Consecutive runs of `tools/audit_storage.py` (`62b3d9ee5bba4408...`) and `tools/audit_security.py` (`db5f090fb2795b24...`) produced byte-identical records.
- **Handoffs:**
  - **To N38 (E2E Smoke):** Confirm browser-side timings against `BUDGET_CEILINGS_MS` (`island_parse <= 150ms`, `first_render_start <= 50ms`, `exam_navigator <= 25ms`, `revision_panel <= 40ms`).
  - **To N39 (QA Runner):** Register `tools/audit_perf.py`, `tools/audit_storage.py`, and `tools/audit_security.py` in the release gate runner.
