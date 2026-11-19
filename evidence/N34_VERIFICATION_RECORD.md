# N34 Verification Record — No-JavaScript Fallback and Print & Paper Mode

**Date:** 2026-11-19 | **Task:** N34 | **Phase:** Phase VII | **Status:** `PASS` (`VERIFIED` in machine checks, print/noscript DOM model, and two-run parity)

## 1. Deliverables and SHA-256 Digests

| Artifact / Touchpoint | Role | SHA-256 |
|---|---|---|
| [`tools/n34_noscript.py`](../tools/n34_noscript.py) | Single-sourced `<noscript>` generator (`coverage`, `anchor_registry`, `concept_summaries`, `conventions`, `terms`) | `8683201811021302d772d1c304fef9e2842a06b989d71d48b71a0f1437e8ab3c` |
| [`src/paper.ts`](../src/paper.ts) | Strict TypeScript F04 paper worksheet generator (`SimPaper`) | `fd59a8233d64fe38e8e98586c52f00e3cc9d2396dd3e9ef07e18ed91d082a541` |
| [`src/compiled/paper.js`](../src/compiled/paper.js) | Compiled runtime module (`SimPaper`, module order `38` in `data/build_policy.json`, `13,402` B) | `54e9bc1eb870a3d6216557ff4988937e349653a84c2d664e865248347ef68a59` |
| [`src/styles.css`](../src/styles.css) | Added `.noscript-*`, `.paper-*`, and comprehensive `@media print` rules | `a3953873fc59d4995b72175cf35134c3e9f10929f2182e34f0428fc92c362cc8` |
| [`src/shell.html`](../src/shell.html) | Added `__SIM_NOSCRIPT_HTML__`, `#druka` paper controls/output, `#settings-print-slot` sync, `__SIM_PAPER_JS__` | `4b72772b25d0f57c65f506e33ebc8b904b1b1ca185c1193a7eb29f736b6c3b7c` |
| [`data/tokens.json`](../data/tokens.json) | Added `themes.print` (26 black-on-white tokens), print figure/grid tokens, and `print_policy` | `eaeb66e411d10b8bbd5d5713029e543dcbbabb7fb08285a9a26ef7637977a2d8` |
| [`data/terms.json`](../data/terms.json) | Added `noscript.notice`, `noscript.limits`, `print.heading`, `print.form_select`, `print.button` (673 total entries) | `8bdd4b1379733ff0ebb63247663fdce8c81112dd733d80da571bc4171113897c` |
| [`tools/check_artifact.py`](../tools/check_artifact.py) | Extended with N34 `check_noscript_fallback` and `check_print_rules` passes | `0211172c797e102a94a09b1cda9a3b432882d521373aa8350d5071257bd2c928` |
| [`src/smoke-subset.js`](../src/smoke-subset.js) | Extended with `SMK-N34-PRINT-WORKSHEET` (`30/30` smoke vectors PASS) | `832e5f3eb976748a9340d2042605bb9df83c5505c0a5349225f4eccc865c0a74` |
| [`tools/verify_n34.py`](../tools/verify_n34.py) | N34 verification harness & three-mode / parity runner | `ee6bf420c6f3fa6ce906f5e1a1b932ccac2b63e4840d202f4bd2b67a625a8226` |
| [`output/simulator.html`](../output/simulator.html) | Single-file offline deliverable (`2,829,225` B, `30/30` build gates PASS) | `04ee192cb3551d54de6997d5dd72bfc67c59775b59b3d223b89b99e1f9079c7a` |
| [`output/build-manifest.json`](../output/build-manifest.json) | Build manifest (`30/30` gates PASS, `39` modules) | `b76248d15edee4bd1b2e6d9ce7c11951cab0d090de7ee7e09fa1e4cd2cac27ec` |
| [`evidence/N34_CORPUS_RECORD.json`](N34_CORPUS_RECORD.json) | Machine-readable N34 fixture, parity, and budget evidence | — |

## 2. Verbatim Latvian Copy (`data/terms.json`)

- **`noscript.notice`:**
  > JavaScript ir izslēgts. Interaktīvā prakse, eksāmena simulācija, automātiskā vērtēšana, figūru SVG attēlošana un dinamiskā A/B/C darba lapas salikšana bez skriptiem nav pieejama; pārlūka druka (Ctrl+P / #druka) un šajā blokā dotais statiskais saturs (jēdzienu karte, metodika, terminu saraksts) joprojām darbojas.
- **`noscript.limits`:**
  > Bez skriptiem paliek slēpti vai neaktīvi šādi moduļi: uzdevumu banka (#sim-bank), zelta pārbaudes vektori (#sim-golden-vectors), sesijas analītika un meistarības aprēķins (#sim-analytics), interaktīvie SVG grafiki un dinamiskā formas A/B/C papīra darba lapas ģenerēšana sadaļā #druka. Pārlūka druka (Ctrl+P) un statiskais pārskats paliek pieejami.

## 3. Main Step A — No-JavaScript Fallback (`PASS`)

- **A.1.1 Single-Sourced Generation Fixture (`PASS`):** Scratch edit (`N34-SINGLE-SOURCE-DRIFT-PROOF-MARKER`) in `terms_data['terms'][0]['text_lv']` propagated identically into `render_noscript_html(...)` output.
- **A.1.2 Link-Integrity & Dangling-Link Fixture (`PASS`):** `check_noscript_fallback` parsed `output/simulator.html` with `<script>` stripped: `1` `#noscript-pazinojums` notice, `64` concept anchors (`karte-P1-01`..`karte-P7-09`), `142` internal links checked (`0` dangling, `0` external URLs, `0` interactive controls), `#druka` cross-reference present. Scratch `<a href="#neeksistejoss-enkurs">` failed by name with `E_NOSCRIPT_DANGLING_LINK`.
- **A.1.3 Terminology Lint (`PASS`):** `python3 tools/validate_terms.py` passed (`entries=673`).

## 4. Main Step B — Print Stylesheet and F04 Paper Worksheet (`PASS`)

- **B.1.1 Print Theme Contrast & Figure Sizing (`PASS`):** `python3 tools/check_contrast.py --mode print` passed (`27 pairs x 1 theme (print)`). Policy in `data/tokens.json`: `link_url_policy: "hide-internal-anchors"`, SVG figures use `--print-fig-width: 140mm` and `--print-fig-min-width: 85mm`.
- **B.1.2 Paper Worksheet Determinism, N24 Slot Parity & Empty-State (`PASS`):**
  - Form A digest run 1 = run 2 = `9d6e16daf8bb551ade297110a62101241f18144cf01b5110c4b89e292c183b73` (`21` slots, `100` points, `11,375` chars, `0` interactive controls).
  - All 21 slots match `output/forms/form_A.json` (`slot_id`, `topic`, `points`, `type_id`, `instance_id`).
  - Form shortage (`B` `FAILED`) lists only `['A', 'C']`; all forms `FAILED` returns `0` options and `#paper-empty-state`.
- **B.1.3 Print-Rule Validation & Unmatched Selector Fixture (`PASS`):** `check_print_rules` verified `5` `@media print` blocks and `133` selectors (`0` unmatched). Scratch `.nonexistent-chrome-typo` failed by name with `E_PRINT_UNMATCHED_SELECTOR`.

## 5. Main Step C — Mode Isolation, Budgets, Smoke, and Handoffs (`PASS`)

### Degradation Honesty Audit
| Mode | Content Delivered | Controls Present | Isolation Verified |
|---|---|---|---|
| Script-off (`<noscript>`) | Notice, 64-concept nested list, methodology, 673-term table, honest limits, `#druka` xref | `0` interactive controls inside `<noscript>` | `PASS` (`check_noscript_fallback`) |
| Screen (`SimPaper.init`) | Interactive `#paper-form-select`, `#settings-paper-form-select`, `#paper-print-btn`, Form A worksheet | Form selector & print button (`data-print-hide="true"`) | `PASS` (`check_n31_runtime.js`) |
| Print (`.theme-print` / `@media print`) | 21-slot Form A worksheet, point table, handwriting blanks, computation grid | Chrome hidden (`display: none !important`), dark theme overridden to `#ffffff`/`#000000` | `PASS` (`check_print_rules` + `applyPrintTheme`) |

- **Two-Run Rebuild Parity (`PASS`):** Consecutive `python3 tools/build.py` runs produced identical `output/simulator.html` (`04ee192cb3551d54de6997d5dd72bfc67c59775b59b3d223b89b99e1f9079c7a`) and `output/build-manifest.json` (`b76248d15edee4bd1b2e6d9ce7c11951cab0d090de7ee7e09fa1e4cd2cac27ec`).
- **Budgets (`PASS`):** `artifact_total` = `2,829,225` B (`2,762.9` KiB / ceiling `2,780` KiB); `runtime_js_code` = `1,187,063` B (`1,159.2` KiB / ceiling `1,168` KiB); `css` = `68,000` B (`66.4` KiB / ceiling `80` KiB).
- **Smoke (`PASS`):** `node tools/check_n31_runtime.js` passed `modules=39/39 globals=37 islands=22/22 smoke=30/30` (`SMK-N34-PRINT-WORKSHEET` PASS).
- **Handoffs:**
  - **To N37:** `.theme-print` + `@media print` expectations (`--print-fig-width: 140mm`, `--print-fig-min-width: 85mm`, `.paper-sheet` 21-slot geometry, chrome hidden).
  - **To N39:** `check_noscript_fallback`, `check_print_rules`, and `tools/verify_n34.py` registered for QA runner.
