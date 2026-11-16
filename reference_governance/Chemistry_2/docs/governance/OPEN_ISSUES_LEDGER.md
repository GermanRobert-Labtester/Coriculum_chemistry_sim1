# Open Issues Ledger

**Parent Contract:** `../../AGENTS.md`  
**Extends:** AGENTS.md §2  
**Last updated:** 2026-11-07 · **Status:** [INSPECTED] static workspace audit; product runtime, accessibility and print gates are not newly verified here.

Compact active index lives in `AGENTS.md` §2. This shard holds forensic context and target-language remediation. A static observation does not establish visual or runtime behavior. Do not close an issue without the evidence class and dated changelog entry required by the parent contract.

## [CLOSURES-2026-11-07]

**Issues closed in the 2026-11-07 product/governance pass (see AGENTS.md §11 changelog).** Evidence was produced and rerun in that pass; the historical entries below are retained unaltered for the audit trail.

| ID | Disposition | Fresh evidence [TESTED unless noted] |
|---|---|---|
| JS-06 | Closed. Finite trainer data removed from the runtime. | sft trainer (8 cases) and Rīks D trainer JS deleted; ch8 static case table (8 rows) and ch9 `#ch9-gr-cases` (rows still generated from `build/graph_cases.json`) remain. All 8 sft case values independently recomputed with `Decimal`. Script 56,475 → 41,938 B, 770 lines, 4.33%. `check_graph_trainer.py --targets` passes. Runtime: Firefox/BiDi, 0 console errors. |
| HTML-01 | Closed. Counts now derived and gated. | `tools/derive_counts.py` writes `build/counts.json` (84 tables, 13 figures, 22 SVG, 178 details, 524 IDs); `tools/check_counts.py` fails on drift. Dated T08 journal row remains history; new C journal row records current counts. |
| HTML-03 | Closed. Fresh static re-scan. | Only functional scroll-edge shadows remain (`.table-scroll.is-overflowing/is-scrolled`, disabled in print); `.search-panel` uses tone step, not shadow. Roles are exactly `rule/mistake/verified` emphasized + neutral `source` + `role__label`. falkon captures inspected. |
| HTML-05 | Closed. Five-pillar matrix gate. | `tools/check_pillars.py`: 121/121 covered concepts located in their chapters; per-chapter pillar matrix printed with inapplicability reasons; 65/65 glossary rows carry English equivalents. |
| HTML-07 | Closed. Evaluated values primary-read. | LNHB/DDEP PDF (`build/source-text/LNHB_Hg-203_tables.pdf`, sha256 522880c4…) read via pdftotext: T1/2 = 46,594(12) d. NuDat/ENSDF capture (`build/source-text/NuDat_203HG_2021.txt`, sha256 350e49df…): 46.610(10) d, Kondev NDS 177, 509 (2021). Both match ch11's quoted values; course datum retained, replacement stays a lecturer decision. Sources S-LNHB/S-NUDAT added; C19 closed. |
| INFRA-02 | Closed. Budget gate implemented. | `tools/check_budget.py` (script B/lines/ratio, inline styles/handlers, banned tokens, AGENTS ceiling). Correctly FAILS on JS-01 today — the gate is live, not green-washed. |
| INFRA-03 | Closed. QA-only boundary explicit. | Every `build/*.mjs` now carries a QA-only header comment; AGENTS §10 records the boundary. |
| INFRA-04 | Closed. Missing gates implemented and run. | `tools/check_contrast.py` (WCAG 2.2 pairs, light+dark, hex/OKLCH) and `tools/check_selfcontained.py` (13 URL refs all W3C namespaces; 0 network APIs) — both pass. |
| INFRA-05 | Closed. Deterministic manifest. | `tools/make_manifest.py`: 650 files, sorted, SHA-256+size+mtime → `.cache/manifest.json`. |
| INFRA-06 | Closed. Glyph coverage gated and fixed. | `tools/check_font_glyphs.py` confirmed 11 requested glyphs (↑ → ↔ ∑ √ ≈ ≠ ≤ ≥ ⌘ □) absent from all four Noto subsets; build_doc.py now embeds an Inter symbol face (`MCh Text Sym`) subsetting exactly those glyphs; gate passes on the rebuilt master. falkon renders text; plot-geometry painting stays under HTML-10. |
| PROSE-01 | Closed. Gate rerun. | `build/check_prose_rhythm.py`: 69 long (≥45-word) paragraphs ≤ 70; teaching em dashes 31 ≤ 40; maps and ch13 refs OK. |


## [ISS-JS-01]

**Executable JavaScript exceeds suppression budget.**

- **Evidence [TESTED]:** canonical `Master_2_tema_merijumi_un_grafiki.html`, 985,696 bytes; one executable inline script, 56,475 UTF-8 bytes, 1,087 content lines, 5.729% of HTML. Inline event attributes: 0. Hard cap is min(4,096 bytes, 100 lines, 2% of HTML); both script measures and the ratio fail.
- **Source:** `build/app.js`; hand-written JavaScript remains the script source. No `ts/` or `tsconfig.json` exists, and `tsc` is unavailable per workspace environment record.
- **Remediation [TS]/[HTML]/[Python]:** inventory every function and event listener; migrate UI state to HTML/CSS; precompute static cases in Python; implement residual arbitrary-input logic in strict TypeScript; compile/minify to the inline artifact; strip QA hooks; enforce bytes, lines and ratio in a Python budget gate. Do not relax the ceiling.
- **Current static scan:** `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `createElement`, `requestAnimationFrame`, `fetch`, `XMLHttpRequest`, and `sendBeacon` each occur 0 times in the shipped script. This does not close the size violation or establish runtime safety.

## [ISS-JS-06] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Calculation and trainer logic still ships in the runtime.**

- **Evidence [INSPECTED]:** script function families include calibration (`calRun`), significant figures (`runSf`), significant-figure trainer (`evaluateSft`), half-life (`runHl`), solutions/dilutions (`runSol`), graph reading (`runGr`), plus search and theme. Current script has 1,087 lines. It uses event listeners and DOM text/value updates; static audit found no prohibited HTML-string injection primitives.
- **Gap:** arbitrary learner numeric input can justify a small calculation layer, but pre-authored trainer cases, labels, answers, static tables and SVGs belong in generated HTML. The script currently exceeds the total shared budget, so no function family is budget-compliant merely because it is useful.
- **Remediation [Python]/[TS]:** pre-render finite cases and explanatory answer keys; retain only calculations that require arbitrary user input; budget the entire remaining runtime under §4's single global ceiling. Keep visible static answers when JavaScript is off. Exact function inventory and migration mapping: `INFRA_PYTHON_TS_JS_AUDIT.md#function-inventory-and-migration`.

## [ISS-JS-08]

**Native progressive enhancement remains incomplete.**

- **Evidence [TESTED]:** current master contains one `<noscript>`, zero `<dialog>` elements, and 60 `popover` plus 60 `popovertarget` attributes, alongside `<details>`, `:has()` and `:checked`. A zero-JS runtime walkthrough was not performed in this pass.
- **Remediation [HTML]/[CSS]:** use native disclosures, dialogs and popovers where they improve the task; preserve reading/navigation and static calculation guidance with JavaScript disabled; test JS-off behavior separately. Do not add a dialog/popover solely to satisfy a count.

## [ISS-CSS-01]

**CSS rule bodies are outside declared cascade layers.**

- **Evidence [INSPECTED]:** `build/style.css` declares `@layer reset, tokens, base, layout, components, utilities, print;` but documents that rule bodies remain unwrapped because falkon and falkon drop layered rules. The master includes this CSS. Static scan: 0 `@container`, 0 `:target`, 0 `subgrid`, 0 `@starting-style`; `:has()` and `:checked` are present; 2 `clamp()` uses.
- **Remediation [CSS]:** retain and test the lightweight-browser compatibility requirement; establish a tested layered implementation/fallback before wrapping rules. Record browser support and screenshot evidence. Do not claim layer compliance from the declaration alone.

## [ISS-HTML-01] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Dated appendix/footer metrics may be stale.**

- **Evidence [INSPECTED]:** the master has 16 chapter sections, 84 tables, 13 figures/figcaptions, 22 SVGs, 176 `<details>`, 541 IDs, 187 `.recall-answer` nodes and 3 `.answer-sheet` nodes (static scan, 2026-11-07). The footer's date/count text has not been reconciled in this pass.
- **Remediation [Python]:** derive dated counts reproducibly, compare appendix B/C/D and footer text with live DOM counts, and update source data only in a product pass. Keep this issue open until that pass is tested.

## [ISS-HTML-03] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Visual-role and shadow audit requires a fresh review.**

- **Prior evidence [INSPECTED]:** earlier inventory flagged `.search-panel`, `.table-scroll` shadows and role labels beyond the three semantic roles. Current master changed since those measurements; this pass did not enumerate current selectors or visually inspect a capture.
- **Remediation [CSS]/[HTML]:** re-scan current styles and role labels, remove unjustified decorative shadows, keep auxiliary labels neutral/unboxed, and capture/inspect with `lite-shot` falkon or falkon under `VISUAL_VERIFICATION.md`.

## [ISS-HTML-04]

**Accessibility: contrast now gated; keyboard, targets, AT and language runs still unmeasured.**

- **Evidence [UNVERIFIED]:** this pass did not measure WCAG contrast, keyboard traversal, assistive technology output, target size, or state announcements. Static source includes focus and reduced-motion rules; one `h1` and SVG structure were counted, but static presence is not acceptance. English-run `lang` coverage was not computed.
- **Remediation [Python]/[HTML]/[CSS]:** run token-pair contrast in light/dark themes, inspect focus visibility and 44px targets, validate heading/landmark and language metadata, then perform keyboard and AT checks. Report each gate separately.

## [ISS-HTML-05] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Five-pillar concept coverage is unaudited.**

- **Evidence [UNVERIFIED]:** `build/concepts.json` exists; no live concept-to-pillar coverage matrix was run in this governance pass.
- **Remediation [Python]:** generate a per-concept matrix for definition, mechanism, worked example, common mistake, and canonical term; record inapplicable pillars with reasons. Do not infer completeness from a concept data file existing.

## [ISS-HTML-06]

**External scientific source layer: C19 closed by primary reads; C20 and further authorities remain.**

- **Evidence [INSPECTED]:** `build/sources.json` and `build/claims.json` cover five local course PDFs and C01–C20. B03 says external VIM/ISO/IUPAC/BIPM and nuclear-data authorities are named but not primary-read; C19 and C20 remain open. No external source may be upgraded to verified from a citation name alone.
- **Remediation [Python]/[Editorial]:** read and hash-pin primary-source copies before adding them to the local ledger; record exact locators, verification level and supported claim. Preserve course wording as course evidence and label corrections/additions.

## [ISS-HTML-07] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Hg-203 evaluated half-life remains unresolved.**

- **Evidence [UNVERIFIED]:** course value 46,595 days is [TEXT-VERIFIED] in B03. The alternative evaluated values named in the claim ledger have not been checked against NuDat/ENSDF or LNHB-DDEP. Keep the course value labelled as such.
- **Remediation [Python]/[Editorial]:** obtain a readable primary evaluation; record nuclide state, value, uncertainty, evaluation/version and locator. Do not replace the course datum based on an unverified alternative.

## [ISS-HTML-08]

**Source-conflict ledger reconciliation needs editorial closure.**

- **Evidence [INSPECTED]:** B03 reports exact-page reconciliation for S1–S23 and spot checks D24, D29, D37–D39, D52, but recommends editorial review before closing HTML-08; S11 has a quoted-case capitalization discrepancy («10 ml» source vs normalized «10 mL»). The full D24–D51 row-by-row reconciliation and qualified editorial sign-off are not established by this static governance pass.
- **Remediation [Editorial]/[Python]:** preserve literal quotations, finish every D-row with locator/original/correction/reason/confidence, compare to the local PDFs, and log closure only after documented review.

## [ISS-HTML-09]

**Print edition: fresh 148-page export exists; every-page review still incomplete.**

- **Evidence [UNVERIFIED]:** no fresh PDF was exported or inspected in this pass. Earlier reports cite a prior 142/143-page print check; that is historical evidence, not current release proof.
- **Remediation [HTML]/[CSS]:** export using the permitted workflow, inspect every page, verify expanded disclosures without duplicate answers, page numbering, contents, colophon, table breaks and figure captions; record tool and artifact.

## [ISS-HTML-10]

**SVG geometry and in-plot rendering remain visually unverified.**

- **Evidence [UNVERIFIED]:** B05 reports falkon and falkon captures showed wrapper containment but did not paint SVG geometry. This pass counted 22 inline SVGs and verified 0 `<style>` blocks nested inside SVG, but did not capture/render the master. Plot colors, geometry, labels, dark mode and print appearance therefore remain unaccepted.
- **Remediation [Visual]/[HTML]:** use a permitted engine that renders the SVG content or an approved browser only if explicitly allowed; capture and inspect each relevant figure/state. Keep containment and geometry claims separate.

## [ISS-INFRA-01]

**Strict TypeScript source/build contract is absent.**

- **Evidence [TESTED]:** no `ts/`, `tsconfig.json`, `pyproject.toml`, or `tsc` installation is recorded; `build/app.js` is hand-written JavaScript.
- **Remediation [TS]:** add strict source (`strict: true`, no `any`, explicit DOM null checks), compile in a reproducible offline step, inline only the budget-compliant output, and avoid runtime dependencies. Document how the compiler is provisioned.

## [ISS-INFRA-02] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Script and governance byte-budget gate is absent.**

- **Evidence [INSPECTED]:** no `tools/check_budget.py` was found in the inspected inventory. Current inline script demonstrably exceeds its prescribed budget.
- **Remediation [Python]:** implement `python3 -I tools/check_budget.py` with non-zero failure and a concise stdout report; check executable-script bytes/lines/HTML ratio, JSON blocks, banned tokens/handlers, inline styles and AGENTS.md byte ceiling.

## [ISS-INFRA-03] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Node QA harnesses sit outside the four-language production matrix.**

- **Evidence [INSPECTED]:** `build/qa.mjs`, `shots.mjs`, `final_check.mjs`, and `final_behaviour.mjs` are present. They are QA harnesses, not shipped runtime dependencies.
- **Remediation [Python]/[TS]:** explicitly exempt them as QA-only with isolation and output guarantees, or port only the maintained checks. Do not imply they belong to the production four-language stack.

## [ISS-INFRA-04] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Verification suite still lacks measured gates.**

- **Evidence [INSPECTED]:** present: `tools/check_index_privacy.py`, `tools/check_anchors.py`, `tools/check_sources.py`, `tools/check_figure_style.py`; absent from the inventory: contrast and self-contained/no-network gates. `check_anchors.py` is a present implementation, not proof every required condition passes.
- **Remediation [Python]:** add contrast and self-contained checks; use anchor gate for IDs, local references and heading order; add schema/coverage tests where needed. Run each gate in the product pass and retain output.

## [ISS-INFRA-05] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**No reproducible workspace hash/mtime manifest; Git unavailable.**

- **Evidence [TESTED]:** `git status` and `git log` report “not a git repository.” No root inventory/hash manifest was found in the inspected file list.
- **Remediation [Python]:** add an optional deterministic manifest in a future authorized product/governance pass; for locked work, use exact file inventory, SHA-256, size and mtime before/after. Never claim Git validation.

## [ISS-INFRA-06] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Embedded font subset omits declared and used glyphs.**

- **Evidence [INSPECTED]:** B05 reports ten declared characters (`↑ → ↔ ∑ √ ≈ ≠ ≤ ≥ □`) are absent from embedded subsets despite presence in `build/_font_chars.txt`; six figure text runs use affected glyphs, with fallback-font metrics. Current source scan confirms the characters are declared and used, but this governance pass did not inspect font cmap tables.
- **Remediation [Python]:** validate requested glyph coverage against every embedded font's cmap after subsetting; fail the build on missing characters; regenerate and inspect affected labels in the permitted rendering pipeline.

## [ISS-PROSE-01] — CLOSED 2026-11-07 (see [CLOSURES-2026-11-07])

**Prose rhythm gate previously exceeded threshold.**

- **Evidence [TESTED in prior ledger, not rerun]:** `build/check_prose_rhythm.py` previously reported 73 paragraphs at least 45 words, over the 70 threshold; three splits were assigned to T07. Current result was not rerun.
- **Remediation [Python]/[Editorial]:** run the current gate and inspect the flagged paragraphs; preserve scientific nuance. Do not close from the historical task assignment alone.

## [ISS-GOV-01]

**Requested audit specification and exact queue files are absent.**

- **Evidence [TESTED]:** workspace root has no `Master_Final_Perfected.md`, no exact `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md`, and no `HTML_MASTER_BUILD_PROMPT.md`. It contains `1st_round_MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` plus other historical plans; these are not silently renamed or treated as the exact requested active queue.
- **Remediation [Governance]:** keep this absence explicit. The first-round roadmap is historical context only unless separately designated by the user.

## [ISS-GOV-02]

**No Git metadata.**

- **Evidence [TESTED]:** root is not inside a Git repository; Git checks stop at the filesystem boundary.
- **Remediation [Governance]:** use file inventories, hashes, sizes and mtimes; do not claim Git status, history, or diff validation.

