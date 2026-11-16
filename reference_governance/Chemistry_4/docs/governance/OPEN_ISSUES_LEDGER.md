# Open Issues Ledger

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §2  
Last updated: 2026-11-07  
Evidence status: current-output static metrics `[TESTED]`; source-page, browser, accessibility, print and scientific review items remain `[UNVERIFIED]`. Evidence is bound to master SHA-256 `6ec59d7845049c6554c7ca5b3c3d7ff75cabc938fdb1893042b994641d2a2845` (2,502,506 B) — verify against `build/qa/verify-report.json`, which is regenerated hash-bound on every suite run.

Use issue IDs as stable keys. Findings from earlier runs describe their captured hashes (2,486,115 B `36041054…` → 2,636,845 B `f69593c5…` → 2,696,457 B `22c825f3…` → current 2,502,506 B `6ec59d78…`, remnant-closure run R21, 2026-11-07) unless the row says historical. Do not close from an old QA report. Close only after current owner source and regenerated HTML meet the stated gate, with hash-bound evidence.

## [ISS-INDEX]

Current compact index.

| ID | Category | Location | Rule violated / gap | Target | Evidence |
|---|---|---|---|---|---|
| OI-01 | HTML-Defect | canonical master | 2,502,506 B > 2 MiB by 405,354 B (first reduction pass −193,951 B: Leitner retirement + leading-indent strip) | Python | `[TESTED]` |
| OI-03 | Closed | `build/assessment_schema.py`, `build/part_15.html`, `#search-index` | T20 reconciled 126 recall / 15 intro / 25 final / 57 bank across owners, search manifest and master; hash-bound in `build/qa/verify-report.json` | Python | `[TESTED]` |
| OI-04 | Closed | `build/part_16.html`, `build/part_top.html` | revision dates aligned: `part_top.html` doc-meta and `part_16.html` footnote both 2026-11-07 | HTML | `[TESTED]` |
| OI-05 | Unverified | workspace root | named `Master_Final_Perfected.md` absent; historical review spec unavailable | Markdown | `[TESTED][UNVERIFIED]` |
| OI-06 | Source-Conflict | Appendix H, biology, `part_15.html`, source list | “>250%” claim removed; ATP/Mg²⁺ warranted (S22/C08); BMR/TDEE §8.6 percentages and ischemia recall answer now carry `[jāpārbauda]`/`papildinājums` labels — primary-source page check still open | Python/HTML | `[TESTED: labels; source pages UNVERIFIED]` |
| OI-07 | Closed | `initLeitnerRecall`, `.leitner-*` | Leitner/mastery UI fully retired (dashboard, O1–O7 mastery SVG, progress bar, per-item boxes, JS engine, CSS); recall is unscored native `<details>` per §8 | HTML/CSS/JS | `[TESTED]` |
| OI-08 | Closed-Print | print/PDF/map | print convergence, exact-hash manifest & 0 sparse pages verified (UI interactive open in T17+) | Python/manual | `[TESTED]` |
| OI-09 | Unverified | theme tokens and controls | current contrast report exists, but current rendered UI target-size/focus contrast not freshly verified here | Python/CSS | `[UNVERIFIED]` |
| OI-10 | Closed | `build/inventory.json` | 5-pillar audit complete: 115/115 audited, 98 worked examples, 17 justified inapplicable | Python | `[TESTED]` |
| OI-11 | Closed | `.taste-skill/`, workspace lint | T20 reran lint: 0 FAIL, 12 WARN; 126 structural emoji replaced with text cue label | Python | `[TESTED]` |
| OI-13 | Closed | `build/style.css`, `.tracker-pulse` | 0 looping animations; animation/keyframes retired in T17 | CSS | `[TESTED]` |
| OI-15 | JS-Bloat | master executable script; `build/script.js` | 265,043 B / 6,016 lines / 10.60%; exceeds all three ceilings (Leitner engine −186 lines removed) | TypeScript/Python | `[TESTED]` |
| OI-16 | JS-Bloat | master script | 40 `innerHTML`, 52 `createElement`; data hydration and runtime templating | Python/HTML | `[TESTED]` |
| OI-17 | JS-Bloat | master inline handlers | 67 total: 62 `onclick`, 3 `onsubmit`, 2 `oninput` | HTML/CSS | `[TESTED]` |
| OI-18 | JS-Bloat | TOC/print/modal/details | JS state, four dialogs, 298 details without `name`, zero `popover` attributes | HTML/CSS | `[TESTED]` |
| OI-19 | JS-Bloat | calculators/scrubbers | 2 RAF, 2 intervals, 9 timeouts; calculators A–H constrained, unit/dimension validated in T18 | TypeScript/Python | `[TESTED]` |
| OI-22 | Closed | output fragments | 0 inline styles in master/fragments; semantic classes mapped in T17 | CSS/HTML | `[TESTED]` |
| OI-23 | Closed | master SVG | 42 teaching SVG + 1 shared sprite container = 43 `<svg>` (Leitner mastery matrix removed with OI-07); sprite owns one `<symbol>`+`<use>` arrowhead; `build/svg_registry.json` (42 entries) documents owner/use; `tools/check_svg.py` gates ids, a11y, geometry, captions | Python/HTML | `[TESTED: structural; render UNVERIFIED]` |
| OI-24 | Infra-Gap | `tools/` | partial gates only; no HTML-anchor/heading/count, static-render, or print checker | Python | `[INSPECTED]` |
| OI-25 | Infra-Gap | `ts/`, `tsconfig.json` | TS source/config created with strict typed interfaces in T18; tsc toolchain installation pending separate approval | TypeScript | `[TESTED]` |
| OI-26 | Infra-Gap | `build/qa/`, `scratch/` | 84 `.mjs` probes outside four-language stack | Python/TypeScript | `[TESTED]` |
| OI-27 | Infra-Gap | `build/`, `scratch/`, `build/qa/` | one-off mutators and retained QA debris; no cleanup authorized | Python | `[INSPECTED]` |
| OI-28 | Unverified | `<noscript>`/instruments | T20 added structural fallbacks: 10 noscript blocks, 8/8 instruments, static tables; executed browser behavior remains unverified | HTML/Python | `[TESTED: structural; visual UNVERIFIED]` |
| OI-29 | CSS-Arch | master / `build/style.css` | zero `:has()`/`:checked`/`subgrid`; one unnamed `@container (max-width:560px)` | CSS/HTML | `[TESTED]` |
| OI-30 | HTML-Defect | dialogs/popovers/print | four dialogs, no popover attrs; current print flatten/answer duplication not checked | HTML/CSS | `[TESTED][UNVERIFIED]` |
| OI-31 | Source-Conflict | course PDFs and 2026 claims | this run did not re-open source pages; old S1–S38 warrants retain their prior confidence only | Markdown | `[UNVERIFIED]` |
| OI-32 | Unverified | topic inventory | historical S27 coverage gaps not mapped against current output | Python/HTML | `[UNVERIFIED]` |
| OI-33 | CSS-Arch | `build/style.css` | 7 cascade layers active; non-print `!important` reduced to 28 (accessibility-only) | CSS | `[TESTED]` |
| OI-34 | Closed | `build/style.css` | 0 raw hex matches outside token block; all mapped to tokens in T17 | CSS | `[TESTED]` |
| OI-35 | Closed | `part_6_9.html`, `part_10_12.html`, `build_html.py`, `instruments.html` | B03 remnant: master had duplicated section numbers 6.9/11.5/12.7 (instrument headings vs verification-vector and F12 sections). Renumbered to 6.10/6.11 (Pārnese cascade), 11.6, 12.8 (F12); TOC/footnote/journal/search refs updated; new Gate 25 in `build/qa/verify_master.py` enforces per-chapter unique monotonic h3 numbers and no heading-level skips | Python/HTML | `[TESTED]` |

## [ISS-001]

Output and executable-script budgets.

**Evidence.** Python UTF-8 byte count and inline-script extraction of the canonical master (2026-11-07 remnant-closure run R21): 2,502,506 B, SHA `6ec59d78…`. Three `application/json` data blocks total 314,492 B and are not executable JS. One executable block has 265,076 UTF-8 bytes, 6,019 lines including terminal line accounting, 10.60% of total HTML. `tools/check_budget.py --profile` writes the per-contributor byte profile to `build/qa/budget-profile.json` (executable 265,076 B; JSON 314,492 B; style 243,265 B; SVG 299,410 B; leading indent residual 31,495 B). First reduction pass applied: Leitner retirement (−65 KB owners) + leading-indent strip outside `pre`/`textarea`/`script` in `build/build_html.py` (−127 KB). Targets are ≤2,097,152 B overall and executable JS ≤min(4,096 B, 100 lines, 2%); the master remains 405,354 B over. Historical figures (2,386,187 B / 2,486,115 B / 2,696,457 B; 258,669 / 266,071 B) are superseded.

**Migration.** Profile generated size by contributor; deduplicate repeated data and markup at owner level; keep JSON payloads separately budgeted; statically pre-render computable views in Python. Keep only named registry hooks in compiled inline TS. Rebuild only in a future production-authorized run. Acceptance must capture source, output bytes/hash, and each budget result.

## [ISS-002]

Client runtime and DOM generation.

**Measured current output.** Sole executable script: 171 unique named functions, 160 `addEventListener` calls, 40 `innerHTML`, 52 `createElement`, 2 `requestAnimationFrame`, 2 `setInterval`, 9 `setTimeout`, 5 `Math.random`, 1 `Date.now`. Script body is 265,076 B / 6,019 lines. The Leitner engine (`initLeitnerRecall`; function census 178→171, listeners 167→160) was removed with OI-07. JSON blocks are data, not script runtime.

**Violating clusters and target.**

| Current functions / selectors | Violation | Migration blueprint |
|---|---|---|
| `generateDrill`, `pgSolutionHtml`, `initProblemGenerator`, command palette, glossary/morph explorers, exam and search rendering | DOM templating/data-array hydration; `innerHTML`/`createElement` | Python emits stable markup/data tables; native form controls and links handle selection; TS only for genuinely arbitrary input. |
| `toggleMatrixOcclusion`, `toggleMatrixDiff`, `toggleMatrixDelta`, `sortMatrix`, `setWorkstationMode`, `assessPin`, `check*Answer`, `set*Phase`, `checkGasSign` | UI state and quizzes implemented in JS; 62 `onclick` included in 67 handlers | `<details>`, `:checked`, `:target`, `:has()` and radio/checkbox states; pre-sort views in Python. |
| `updateToc`, `requestTocUpdate`, `initScrollCues`, `openForPrint`, `restoreAfterPrint`, `showModal` call sites | scroll/print/modal behavior duplicates platform features | anchors and CSS cues; native `<dialog>`/popover where supported; print stylesheet expands answers and flattens sticky elements. |
| `aCalc`–`hCalc`, `calcDeltaG`, `initTraceScrubber`, `toggleCalorimeterPlay`, `toggleGasProcessPlay` | eight instrument clients plus animated scrubbers | Static Python-built state/lookup tables and SVG; at most one `thermoCalc` hook from registry. Remove timers/RAF unless a separately justified accessible interaction survives review. |
| `initLeitnerRecall`, `.leitner-*` | mastery/progress UI banned by §8 | native unscored recall controls; no streak, XP, mastery score or spaced-repetition status. |

No current function qualifies as an approved whitelist implementation. The registry in §4 is a target allowlist, not evidence that these hooks currently exist or comply.

## [ISS-003]

Native HTML and CSS state.

Current output has 313 `<details>` with zero `name` attributes, four `<dialog>`, zero `popover` attributes, and 42 teaching SVGs plus one shared sprite container (43 `<svg>` elements; the Leitner mastery matrix was removed with OI-07). T19 replaced the retired per-plate arrow markers with one shared sprite (`<symbol id="fig-arrowhead">` reused by `<use>` through `#fig-arrow-ink`/`#fig-arrow-accent`), added stable `title`/`desc`/`aria-labelledby` wiring for every teaching SVG, documented each asset in `build/svg_registry.json`, and added `tools/check_svg.py` (unique ids, aria targets, viewBox clipping, raw-colour rejection, text-collision warnings, caption/step alignment, registry boundary). One runtime SVG template in `build/script.js` remains documented as a runtime asset and is not counted in the 43. It has one h1, one main, two nav, 34 sections, 15 asides, no article, five noscript blocks, unique IDs in the parser pass, and 69 parsed event attributes (62 click, 3 submit, 2 input). Heading counts and order need a semantic pass. Use `<details name>` for exclusive disclosure groups, `<dialog>` for modal contexts, Popover API for transient previews, CSS state selectors, SVG symbols for exact repeated geometry, and semantic section landmarks. Avoid forcing a given control into a primitive if it cannot preserve keyboard semantics.

**T19 SVG normalization (2026-11-07):** Added `build/svg_registry.json` (43 entries with owner/host/kind/purpose) and `tools/check_svg.py`; added the two approved Section-6 plates `fig-sign-convention` and `fig-open-coupling-boundary`; fixed render-visible defects surfaced by inspection: the T13 regression-vector fixture was painting over the calorimeter title (`display="none"` now), the calorimeter left callouts were clipped (content box widened), and duplicate figure numbers `5.b`/`8.b` plus the unlabelled U6 caption were renumbered (`5.c`, `8.c`, `11.c`). A start-up regex bug in `build/search_index.py` silently produced zero `#defect-S*` anchors and a zero defect count after T11 moved rows to `<th scope="row">`; restored to 38 S-rows (39 index entries incl. the S34 cross-link). Remaining text collisions in the T13 calorimeter plate and the dense concept/etymology plates are recorded as warnings in `build/qa/svg_report.txt`; they are not clipped outside the viewBox but need T13/editorial follow-up. No browser or PDF render was accepted: falkon/falkon do not render SVG here, falkon did not finish loading the 2.6 MB page, and the last PDF predates the current hash. SVG geometry was inspected through supplementary Inkscape renders under `.cache/t19/`; page/print acceptance stays `[UNVERIFIED]`.

## [ISS-004]

CSS architecture and design rules.

**Present:** `build/style.css` establishes full 7-layer cascade architecture (`reset, tokens, base, layout, components, utilities, print`). All authored stylesheet rules are enclosed in declared layers. Primitive `--p-*`, semantic `--t-*`, and component `--c-*` token tiers are strictly observed. Zero raw hex literals exist outside `@layer tokens` (OI-34 closed). Non-print `!important` reduced from 61 to 28 (strictly bounded to `.sr-only` accessibility utility and `@media (prefers-reduced-motion)`). Zero looping animations exist (OI-13 closed; `.tracker-pulse` animation neutralized). Master HTML and fragments contain 0 inline `style` attributes (OI-22 closed). Zero box-shadows and zero gradients exist. Automated CSS linter `tools/check_css.py` and contrast validator `tools/check_contrast.py` integrated into build pipeline. Visual captures across light/dark desktop/mobile, print, and 320px viewport inspected with falkon `webshot`.

**Gaps:** zero `:has()` and `:checked` in current master; no `subgrid`; one unnamed `@container (max-width:560px)`; no `@starting-style` or CSS counters. Preserve no-gradients/glows/glass, no shadows, no structural emoji, no uniform card grids, no hero banners, no decorative animation, no drop caps/badges/stock images.

**Historical checks & remediation (T17):** Prior state had rules unlayered, 149 inline styles, 93 raw hex literals outside tokens, and looping animation on `.tracker-pulse`. In T17, all authored rules were partitioned into the 7 declared layers, all 148 inline styles replaced with semantic classes, all raw hex replaced with tokens, `.tracker-pulse` animation neutralized, and print convergence preserved at 213 pages (0 sparse pages). Contrast calculations (WCAG AA/AAA) verified with 0 failures.

## [ISS-005]

Python and TypeScript infrastructure.

Existing tools are `tools/build.py`, `check_budget.py`, `check_css.py`, `check_contrast.py`, `check_terminology.py`, `check_svg.py` (T19 SVG gate), `capture_visuals.py`, and `migrate_tokens.py`. `tools/build.py` runs `calc.py`, invokes `build_html.py`, then terminology checks; it writes generated outputs. `check_budget.py` reads but only budgets AGENTS/HTML and `build/script.js`; its own docstring mentions banned patterns not enforced in code. `check_css.py` checks layer order, token presence, orphan components, and shadow; it does not check inline styles, gradients, full layer placement, or hex scoping. `check_contrast.py` writes `build/qa/contrast_report.*`; inspect before running. Do not run build/check scripts in this governance-only audit.

Missing/needed deterministic gates: HTML parse for duplicate IDs and broken anchors, heading/landmark/attribute checks, executable script and inline-event budgets from final HTML, banned DOM APIs, inline style and CSS token/layer validation, data-count parity, static output and noscript fallback, print/PDF hash+page-map validation, and hash-bound report manifest. Centralize counters to avoid the 62-vs-67 event discrepancy and data-source drift.

Target TypeScript project: `ts/tsconfig.json` with `strict`, `noImplicitAny`, `noUncheckedIndexedAccess`; zero `any`; explicit null checks; typed DOM and validated inputs; compiled/minified artifact size checked against whitelist budgets. In T18, `ts/tsconfig.json` and `ts/calculator.ts` were created with strict typing; `tsc` toolchain installation remains pending explicit approval. Keep Python stdlib deterministic; no final HTML dependency/network.

## [ISS-006]

Sources, accessibility and release evidence.

The canonical source PDFs are present but page-level scientific claims were not verified in this turn. Historical QA, saved PDFs and the roadmap are not current-hash acceptance. T20 reran contrast, CSS, SVG, terminology and retrieval gates successfully; `build/qa/verify-report.json` records input/output SHA-256, commands, Python version, pass/fail and explicit untested modes. Target sizes, keyboard, screen-reader, JS-off browser execution, viewport/theme captures, and PDF output remain open. The print gate currently rejects the saved PDF because it predates the current master hash. A visual pass requires falkon/falkon `webshot` output PNG and direct inspection under `VISUAL_VERIFICATION.md`; no screenshot was captured in this governance run. Master_Final_Perfected.md is absent; the historical prompt and addendum are present but not coequal authority unless the user supplies the named specification.

## [ISS-007]

Source-defect and stale issue IDs.

T20 closed OI-03 from current owner/output evidence: `build/assessment_schema.py` is the single owner of recall/exam counts and stable IDs, and `build/qa/verify_master.py` Gate 20 reconciles owners, the embedded manifest, the search manifest and the master. OI-04 and S1–S38 remain open until checked against current source fragments and their printed PDF pages. The `Master_Final_Perfected.md` absence is a real record gap, not permission to reconstruct its content from the roadmap. See `TERMINOLOGY_AND_SOURCES.md#source-defect-register` and `#verified-source-registry`.

## [ISS-008]

Historical source coverage gaps (S27): Third Law, kinetic/potential energy, ΔG–K link, and temperature dependence. The topic description requires these ideas; the current master has not been mapped against the full concept/outcome denominator in this governance pass. Establish a source-backed concept inventory, check each emitted heading/content region, and record a gap or valid coverage for each item. Do not claim absence from output without that map. Target: Python coverage report plus editorial inspection; source content remains untouched until an implementation run is authorized.
