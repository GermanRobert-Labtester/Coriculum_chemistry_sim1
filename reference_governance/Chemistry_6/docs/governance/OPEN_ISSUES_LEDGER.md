# Open Issues Ledger

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §2  
Last updated: 2026-11-12  
Verification: `[INSPECTED]` current source and saved evidence; static HTML measurements marked `[TESTED]`. Browser, visual, chemistry-source and release acceptance were not run. T20 (2026-11-12) added machine-checked budget/contrast/manifest gates without changing the master (fingerprint `c40e10e3…ecd44d`, 1,669,007 B).

This ledger preserves current defects and uncertainties for a later authorized build. Historical proposal measurements are labeled as historical; fresh static measurements below refer to the master fingerprint recorded in AGENTS.md §2. No product file was changed in this audit.

## Issue index

Canonical HTML is `Master_oksidesanas_reducesanas_procesi.html`, 1,456,650 B, SHA-256 `a081c593f56b136cc1974ef2f33e283f505a483edd562a0e3c472d9bc0258e5f`, mtime 2026-11-03 10:20:40.754010335 +0200. Python stdlib `HTMLParser` and regex inspection on 2026-11-07 measured: 66,128 executable script bytes / 1,357 lines / 4.540%; one 56,636 B JSON data island; combined runtime+data 122,764 B / 8.428%; three script blocks total; 53 listeners; 3 timeouts; 27 `innerHTML`, 9 `createElement`; CSS in master 413,962 B with 0 `@layer`, 116 `!important`, 0 `@container`, 0 `subgrid`, 7 `:has()`, 1 `:target`, 0 `:checked`, 1 reduced-motion declaration; 1 inline `style`; 200 `<details>` with no `name`, 0 `<dialog>`/`popover`, 7 SVG with no `<symbol>`/`<use>`, 85 tables (46 captions, 37 `aria-label`, 1 `aria-labelledby`; direct-name union 79, six unnamed), 498 equation `aria-label`s of which 164 contain `^`, `_`, or `->`, 2 duplicate IDs and 2 broken `#ch0` links (the `#audit` hash is a mode, not an element). HTMLParser found zero inline event attributes. Static parsing does not establish runtime behavior or pixels.

## JS-01

**Executable JavaScript exceeds the registry.**

- **Finding:** `[TESTED]` Master script blocks at lines 1461 (45 B, 1 line) and 4591 (66,083 B, 1,356 lines); executable total 66,128 B, 1,357 lines, 4.540% of 1,456,650 B. Cap is 4,096 B, 100 lines, and <2% (smallest limit governs). The 56,636 B `application/json` block at line 4590 also counts toward the 2% ceiling; combined total is 122,764 B / 8.428%. The source `tools/assets/master.js` is 66,081 B. None of its 68 named functions exactly matches the registry names `markUnsure()` / `calcTitr()`; no present function is demonstrated compliant with the registry.
- **T20 re-measure (2026-11-12, fingerprint `c40e10e3…ecd44d`):** `[TESTED]` `tools/lint_js_budget.py` — executable 66,582 B / 1,287 non-empty lines, executable+islands 7.611% of 1,669,007 B; island `master-data` 60,439 B unregistered; 72 named functions, 0 registered. Cap violation stands; the numbers are now machine-checked on every gate run.
- **Why it matters:** the residual browser layer exceeds the stated micro-runtime by 16× in bytes and 13× in lines; a large part handles state/data that can be native or precomputed.
- **Remediation:** migrate simple state to HTML/CSS, pre-render calculable content with Python, retain only registry-approved residual functions compiled from strict TypeScript. Preserve static/no-JS and print paths; do not delete interactions before parity is evidenced.
- **Target:** HTML/CSS/Python/TypeScript. See [JS forensic audit](INFRA_PYTHON_TS_JS_AUDIT.md#js-forensic-audit).

## JS-02

**Runtime DOM construction and injection patterns.**

- **Finding:** `[TESTED]` `master.js` has 27 `innerHTML` and 9 `createElement` occurrences; the generated source spans at least lines 110–1286 per the recorded source scan. `outerHTML`, `insertAdjacentHTML`, and `document.write` were not observed in the current inline scan.
- **T20 re-measure (2026-11-12, fingerprint `c40e10e3…ecd44d`):** `[TESTED]` `tools/lint_js_budget.py` confirms `innerHTML` ×27 and `createElement` ×9 in the shipped runtime (with per-occurrence line numbers in `qa/t40/js_budget.json`); no `outerHTML`/`insertAdjacentHTML`/`document.write`/`requestAnimationFrame`/`eval`/inline-handler/external-script findings. Counts unchanged since T19.
- **Remediation:** static tables, labels and option content belong in the Python generator; reveal existing markup with CSS/native controls. Any remaining node creation needs a registry exception and evidence that it is not templating.
- **Target:** Python/CSS/HTML. See [DOM generation migration](INFRA_PYTHON_TS_JS_AUDIT.md#dom-generation-migration).

## JS-03

**JSON data hydration island.**

- **Finding:** `[TESTED]` `<script type="application/json" id="master-data">` at line 4590 is 56,636 B (3.89% of HTML); this alone exceeds the 2% aggregate ceiling.
- **Remediation:** render deterministic tables/state choices during build; remove the data island only after consumers have static equivalents.
- **Target:** Python/HTML. See [Python CLI](INFRA_PYTHON_TS_JS_AUDIT.md#python-cli).

## JS-04

**Runtime UI state duplicates native capabilities.**

- **Finding:** `[INSPECTED]` Runtime includes `i1`, `i2`, `i3`, `i5`, `setAudit`, filters, `eqToPlain`, recall/report and related event flows; 53 `addEventListener` and 3 `setTimeout` calls. The old audit counted 36 `.js-only`/JS-only interactions and no `<noscript>`; current parser confirms no `<noscript>`. The task roadmap treats `#audit` as a mode hash.
- **Remediation:** use named `<details>` groups for exclusive disclosures, checkbox/radio state plus `:has()` for filters and modes, `:target` for bounded steps, Popover API for transient previews, and Python-built Nernst tables. Keep only arbitrary-input titration calculation and approved local recall persistence in runtime.
- **Target:** HTML/CSS/Python/TS. See [JS forensic audit](INFRA_PYTHON_TS_JS_AUDIT.md#js-forensic-audit) and [native interaction patterns](ARCH_CSS_DOM_CONTRACTS.md#native-interaction-patterns).

## JS-05

**No TypeScript source contract/toolchain.**

- **Finding:** `[TESTED]` workspace inventory finds no `tools/ts/*.ts`, `tsconfig.json`, or `pyproject.toml`; no TypeScript compiler is registered in the workspace. Target strict TS files/config do not exist.
- **Remediation:** introduce only in an authorized build pass if residual registry logic survives; strict mode, zero `any`, explicit DOM null checks, compile/strip/minify and measure emitted script.
- **Target:** TypeScript/Python. See [TypeScript contract](INFRA_PYTHON_TS_JS_AUDIT.md#typescript-contract).

## CSS-01

**Missing CSS layer and intrinsic-state architecture.**

- **Finding:** `[TESTED]` emitted CSS: 0 `@layer`, 116 `!important`, 0 `@container`, 0 `subgrid`, 0 `:checked`, 7 `:has()`, 1 `:target`, 0 `@starting-style`, 5 `clamp()`, 3 counters, 5 `:focus-visible`, 1 reduced-motion rule and 5 print media blocks. `!important` is present in print rules too; required exception is print-only.
- **Remediation:** first declaration must be `@layer reset, tokens, base, layout, components, utilities, print;`; assign rules by purpose; remove important overrides except if a documented print necessity is unavoidable; use native state selectors and measured containers.
- **Target:** CSS. See [CSS tokens and layers](ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers).

## CSS-02

**Token hierarchy and inline style violation.**

- **Finding:** `[INSPECTED]` `tools/tokens.json` contains 14 semantic colors plus type, spacing and layout tokens but no primitive/component tiers, dark theme, OKLCH values, or recorded contrast ratios; `master.css` redeclares raw color values (31 hex literals in the saved scan). Emitted HTML has one inline `style` attribute at footer (historically line 4587); SVGs contain recorded 133 hex color occurrences. Selector/color counts are inventory, not proof every occurrence is defective. Current root HTML declares `color-scheme: light` only; no contrast calculator exists.
- **Remediation:** preserve current semantic names; add primitive → semantic → component tiers with colors only sourced from `tokens.json`; convert footer inline style to class; audit SVG colors against token semantics.
- **Target:** CSS/Python/HTML. See [CSS tokens and layers](ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers).

## HTML-01

**Native disclosure and SVG reuse gaps.**

- **Finding:** `[TESTED]` 200 `<details>` and 0 `name` attributes, 0 `<dialog>`, 0 `popover`, 7 inline SVGs, 0 `<symbol>`/`<use>`. These counts do not establish that every disclosure group should be exclusive or every SVG path reusable.
- **Remediation:** assign `name` only to genuinely exclusive groups; use native dialog/popover only for task-relevant interactions; deduplicate repeated SVG structures only where geometry and semantics remain correct.
- **Target:** HTML/Python/CSS. See [native interaction patterns](ARCH_CSS_DOM_CONTRACTS.md#native-interaction-patterns).

## INFRA-01

**Missing deterministic QA and budget tools.** — **repaired in T20 (2026-11-12).**

- **Original finding:** `[TESTED]` absent in `tools/`: `lint_js_budget.py`, `lint_agents_size.py`, `check_anchors.py`, `check_contrast.py`, `check_a11y_names.py`, `check_all.py`. Build remains monolithic (`tools/build_master.py`, 251,679 B); no `pyproject.toml`.
- **Repair:** `[TESTED]` T20 implemented `lint_js_budget.py` (§4 caps, function registry, data-island registry, banned sinks, inline handlers, external scripts; fixtures 6/6), `lint_agents_size.py` (AGENTS byte cap + workspace-reference integrity with an explicit absent-controls registry; fixtures 5/5), `check_contrast.py` (WCAG ratios for every `tokens.json` `contrast_pairs` row, var()-coverage, raw colour literals outside the tokens layer; fixtures 5/5) and aggregate `check_all.py` (task-dir-confined outputs; never builds/exports; non-composable gates withheld with reasons). `check_anchors.py`/`check_a11y_names.py` already existed (T17/T18). T20 also added `tools/make_manifest.py` (artifact hash manifest; `--check` fails on drift, control drift or the stale release-PDF binding). Eight existing gates gained an optional `--report` redirect; default report paths unchanged. Negative fixtures fail with exit 1 while the master hash stays unchanged (`qa/t40/evidence.md`).
- **Residual:** the byte/contrast gates are red on the current master **by design** — they machine-check open issues JS-01/JS-02/JS-03 and CSS-02 and the stale PDF (H-06). A gate pass proves only its measured scope; splitting the monolithic builder remains a separate authorized decision.
- **Target:** Python. See [Python CLI](INFRA_PYTHON_TS_JS_AUDIT.md#python-cli).

## INFRA-02

**Raw JavaScript QA helpers.**

- **Finding:** `[INSPECTED]` `qa/overflow*.mjs`, `qa/t07_playwright.mjs`, and additional `qa/**/*.mjs` files exist; the inventory found 39 `.mjs` files. These historical QA tools were not all read or executed. Their contents/side effects remain unverified.
- **Remediation:** inspect per tool before execution; port maintained checks to Python/TS only when authorized. Existing saved reports are historical, not current acceptance.
- **Target:** Python/TS. See [historical QA tools](INFRA_PYTHON_TS_JS_AUDIT.md#historical-qa-tools).

## GOV-01

**Required control documents absent; roadmap is present.**

- **Finding:** `[TESTED]` current root has `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` (136,061 B; mtime 2026-11-06) and `PROMPT_master_html.md` (historical v1); it does not have `Master_Final_Perfected.md` or exact `HTML_MASTER_BUILD_PROMPT.md`. Earlier governance and roadmap text say the roadmap was absent; that statement is stale. Do not create missing documents or treat the historical prompt as current authority.
- **Remediation:** owner supplies/reconciles missing authoritative documents; meanwhile preserve present roadmap as a non-authorizing queue and follow current AGENTS standing rules.
- **Target:** governance/source. See [verified source registry](TERMINOLOGY_AND_SOURCES.md#verified-source-registry).

## GOV-02

**Noncanonical HTML copies and archive inventory.**

- **Finding:** `[TESTED]` canonical root master is explicitly named in AGENTS. Workspace also has 24 archived master snapshots and QA HTML `qa/t02_notation_snap.html`, `qa/t04_ch11_slim.html`, `qa/verify_bionumbers.html`, `qa/verify_libre.html`; skill template/demo HTML files are not product copies. QA snapshots’ content/authority was not re-audited.
- **Remediation:** keep root master canonical; retain archive/QA evidence; label two preexisting task snapshots as noncanonical in governance if future task updates local QA docs. Do not modify them in this run.
- **Target:** governance. This status is `[INSPECTED]` by inventory only.

## GOV-03

**Historical QA task index conflicts with completion summary.**

- **Finding:** `[TESTED]` `rg '^## Task '` in `qa/design.md` returns 15 headings: 01, 04–08, 10, 13–20. It has no headings for 02, 03, 09, 11 or 12, while its Task 20 note says all 20 tasks are fully executed and documented. This is a report completeness/evidence trace gap, not proof those tasks were unperformed.
- **Remediation:** preserve the old log; a future authorized QA documentation pass should reconcile missing task evidence without inventing results or changing product files.
- **Target:** QA/governance. Saved task reports remain historical until tied to current product hash.

## H-01

**Product-level claims exceed evidence scope.**

- **Finding:** `[INSPECTED]` current text at lines 1582 and 1586 says the material “aizstāj piecus izkaisītos avotus” and “katrs skaitlis pārrēķināts.” These claims exceed the registered-source and numeric-gate evidence described in saved QA.
- **Remediation:** narrow to measured source synthesis and registered number checks; never imply whole-source replacement or universal recomputation without a current inventory.
- **Target:** HTML/Python. Claim remains open pending current text inspection.
- **Fresh inspection (T08, 2026-11-09):** `[TESTED]` both strings are absent from the current master (grep "aizstāj piecus" / "katrs skaitlis" = 0 matches on `a1054ec2…eeeb13`); the §sakums/§footer wording now states registered checks ("Reģistrētie vienādojumi pārbaudīti ar atomu un lādiņu skriptu; reģistrētie skaitļi pārrēķināti no nenoapaļotiem starplielumiem"), which matches the gates' measured scope. The overclaim wording was repaired in an earlier authorized pass; recorded here with fresh evidence. Status: closed as repaired, evidence `qa/t28/audit.csv` row A16.

## H-02

**Duplicate IDs and missing fragments.** — repaired 2026-11-11 (T17)

- **Finding:** `[TESTED]` current parser finds `id="prov-a22"` three times, `id="prov-a15"` twice, plus two `<a href="#ch0">` links with no matching ID. `#audit` is an intentional mode hash, not a fragment target. Historic lines: A22 1778/1837/1868; A15 2196/2601; stale `#ch0` links near 4304.
- **Remediation:** unique per-occurrence IDs while preserving stable claim IDs; map obsolete `#ch0` to correct destination; anchor checker must explicitly classify `#audit`.
- **Target:** Python/HTML.
- **Repair evidence (T17, 2026-11-11):** `[TESTED]` on rebuilt master `c258bec5…414b7cb` (1,659,308 B) — (1) `tools/build_master.py` `_dedupe_prov_ids()` suffixes repeated provenance anchors in document order (`prov-a22`/`-2`/`-3`, `prov-a15`/`-2`); `data-claim` and the one-claim-link-per-note navigation unchanged; (2) changelog row B12 `ch_anchor` `"ch0"` → `"sakums"` in `tools/master_data.py` with the "0. nodaļa" label preserved, so both B12 links resolve; (3) new gate `tools/check_anchors.py` (duplicate ids, fragment resolution, ARIA/`headers` IDREFs, explicit `MODE_HASHES` registry for `#audit`) PASS on the rebuilt master (553/553 unique ids, 943 fragments, 54 IDREF tokens) and exit 1 on the pre-repair snapshot with exactly the three ledgered problems; fixtures `qa/anchor_fixtures/` 5/5 (valid passes; duplicate-id, missing-fragment, missing-ARIA, mode-hash-not-blanket fail). Navigation verified with 12 falkon CDP scenarios (`qa/b02/verify-results.json`: direct URL jumps, claim-link → chlog row, back/forward, B12 → `#sakums`, print links). No-JS fragment scroll and synthetic-Tab focus are recorded engine warrant limits, not document defects. Details: `qa/verify.md` T17, `qa/design.md` Task 37.

## H-03

**Equation aria-labels expose source syntax.** — repaired 2026-11-11 (T18)

- **Finding:** `[TESTED]` current stdlib parse: 498 equation `aria-label`s; 164 contain `^`, `_`, or `->`. Current rule remains zero such tokens in speech labels.
- **Remediation:** generate speakable Latvian descriptions from structured formula tokens and check label tree; do not treat the automated string gate as pronunciation proof.
- **Target:** Python/HTML.
- **Baseline re-measure (T18, 2026-11-11):** `[TESTED]` on `c258bec5…414b7cb`: 240 `role="math"` divs, 200 labelled, 164 contain `^`, 0 contain `_`, 0 contain `->` (the helper had already substituted `->` → `→` before embedding); 40 label-less mathblocks speak from DOM text.
- **Repair evidence (T18, 2026-11-11):** `[TESTED]` on `95bb5423…5b64` — `tools/build_master.py` `speakable()`/`_speak_species()` render structured tokens as Latvian speech (`^2-` → "2 mīnus", `->` → "veido", `⇌` → "ir līdzsvarā ar", states → "šķīdumā" etc.); `eq()` labels by default with it; visible/copyable Unicode unchanged (`eqToPlain` copies `textContent`). Gate `tools/check_a11y_names.py` + fixtures `qa/a11y_fixtures/` 6/6 (bad-label fixture fails); report `qa/a11y_names_gate.md`; label samples and limits in `qa/b03/notes.md`. Spoken-quality acceptance remains a warrant limit (no SR runtime).

## H-04

**Hidden audit banner may override `[hidden]`.** — repaired 2026-11-11 (T16)

- **Finding:** `[INSPECTED]` source has `<aside id="audit-banner" ... hidden>` at line 1465 and selector `.js .js-only{display:block}` in the dated evidence. Historical 390px collision and first-paint visibility are not reproduced this run.
- **Remediation:** preserve `[hidden]` semantics in cascade; reveal only on explicit audit state; test first paint, delayed JS, `#audit`, close, no-JS and 390px in visual-capable run.
- **Target:** CSS/HTML.
- **Fresh reproduction (T05, 2026-11-09):** `[TESTED]` on master `2eaf59fd…ac7ef0`, the banner is visible on first paint at 390/768/1440 px without `#audit` (`qa/t05/shots/t05-ch2-{390,768,1440}.png`; Playwright headless, user-approved). Cause confirmed in source: `.js .js-only{display:block}` outranks the UA `[hidden]{display:none}` rule; the JS `setAudit` only toggles after load. Print is unaffected (`display:none !important` in the print block). Not repaired in T05 (Task 20 scope).
- **Cascade state on the T34 master (T16 baseline, 2026-11-11):** `[TESTED]` the utilities-layer `[hidden] { display: none; }` rule (entered between the T05 master `2eaf59fd…` and the T33 frozen copy) already outranks the components-layer display switch by cascade-layer order. Default/no-JS/delayed-JS/`#audit`/print states measured on `71b7656f…4f2dc`: banner `display:none`, box 0×0 outside explicit audit state; `#audit` fresh load opens 50/83/136 px at 1440/768/390 with clean wrap at 390 (rows y 11–86 / 96–123). Two state gaps remained: close kept the `#audit` hash (reload reopened) and anchor jumps landed under the sticky open banner.
- **Repair evidence (T16, 2026-11-11):** `[TESTED]` on rebuilt master `427d90e9…df2f8` — (1) `setAudit(false)` clears the `#audit` mode hash via `history.replaceState` (guarded, no history entry), so reload after close does not reopen and `#audit` navigation still reopens; (2) `html.audit-on` gains `scroll-padding-top` 3.5/5.5/8.75 rem by breakpoint, matching the measured open-banner heights — jumped `#h-ch3` heading lands 71 px below viewport top at 1440 (banner 50 px) and 150 px at 390 (banner 136 px); (3) delayed-JS probe (runtime stripped, `.js` class set): banner `display:none`, box 0×0, also with `#audit` in the URL. No banner markup change; no new `!important`; print suppression unchanged. New gate `tools/check_audit_banner.py` (markup hidden attr, utilities-after-components cascade, `setAudit` wiring, print suppression) + 5 fixtures in `qa/audit_fixtures/` reproduce and block the defect shapes, including the injected visible-by-default banner; `qa/audit_gate.md`. Visual/CDP evidence: `qa/b01/verify-results.json` (15 scenarios, 1440/768/390), `qa/b01/shots/t16-*.png` (directly inspected), `qa/b01/notes.md`, `qa/verify.md` T16.

## H-05

**PbO₂ difference rounding is inconsistent.** — repaired 2026-11-09 (T04)

- **Finding:** `[TESTED]` recorded arithmetic: displayed 1.80−1.46 = 0.34 V, source precision 1.800−1.455 = 0.345 V; a prose “0.35 V” needs explicit unrounded precision and rounded operand caveat. Exact current product text was not rechecked.
- **Remediation:** retain precision provenance and align prose/data; one final rounding only.
- **Target:** Python/HTML.
- **Repair evidence (T04, 2026-11-09):** `[TESTED]` the “Sekas” cell is now derived from registered operand literals (`master_data.Calcs` `pbo2_ediff`/`pbo2_ediff_crc`, rendered via `DERIVED_PROSE` + `num_ref`): “par 0,34 V augstāka; pret CRC nenoapaļoto 1,455 V — 0,345 V (nenoapaļota)”; no 0,35 V prose remains (`rg 'par 0,35 V'` on the master returns nothing). The new gate checks (`check_derived_prose`, visible-arithmetic scan) and fixtures (`qa/numbers_fixtures/`, 2/2) reproduce and block the defect shape; the same scan found and repaired the companion rounding defect 8,629→8,628 g (12.4.2, change-log A28) and five 13.F rule strings. Visual/print evidence: `qa/t04/shots/t04-q3-390.png` (Chromium, user-approved), `qa/t04/master-t04.pdf` p. 17/20/78 inspected. Details: `qa/design.md` Task 24, `qa/verify.md` T04.

## H-06

**Current PDF predates current HTML.** — repaired 2026-11-11 (T33/T13)

- **Finding:** `[TESTED]` `qa/master.pdf` 3,696,817 B, mtime 2026-11-03 09:24:21.899833824 +0200; HTML mtime 10:20:40.754010335 +0200. Therefore saved PDF is older than current HTML; no PDF was produced or inspected in this audit. Later stale state: `qa/master.pdf` 1,278,697 B, 2026-11-09 11:56, still predating the T11/T12 builds (1,550,816 / 1,558,739 B).
- **Remediation:** in an authorized build pass bind a fresh export to exact HTML hash, inspect every page, preserve old artifact as historical evidence.
- **Target:** Python/print CSS.
- **Repair evidence (T33, 2026-11-11):** `[TESTED]` release PDF `qa/t33/master.pdf` (142 pp, A4) exported from frozen copy `qa/t33/master.frozen.html` (SHA-256 `273dc6a6…8ab7c042`, byte-identical to the canonical master at export time) with user-approved Chromium headless `--print-to-pdf` only; `qa/t33/manifest.json` records HTML hash, PDF hash, byte sizes, page count, timestamp and command, and `qa/t33/check_manifest.py` validates the binding (exit 0 on the current pair; exit 1 demonstrated on a stale hash / wrong page count). All 142 pages rendered and directly inspected: chapter order, answers once (p. 87), controls absent, templates blank, 9 SVG plates whole, no clipped/split tables. The inspection itself caught a deeper pre-existing defect — the answer appendix never printed because nested `@layer print` blocks lost to `@layer components` own declarations in Chromium — repaired in `tools/assets/master.css` (plus `overflow-wrap: break-word` on print table cells for squeezed columns); pre-fix evidence `qa/t33/master.pre-fix.defect.pdf` and `qa/t33/master.pre-fix.frozen.html`. The old `qa/master.pdf` is retained as historical evidence; the canonical release PDF is `qa/t33/master.pdf`. Details: `qa/verify.md` T33, `qa/design.md` Task 33.

## H-07

**Table names are incomplete.** — repaired 2026-11-11 (T18)

- **Finding:** `[TESTED]` current master has 85 `<table>`, 46 captions, 37 `aria-label`, and 1 `aria-labelledby`; simple per-table union finds 79 named and 6 without any of those direct names. The six table IDs and broader accessible-name computation were not isolated; a tree-aware checker is still required.
- **Remediation:** name every table with caption or accessible name; avoid duplicate adjacent label/caption; check relationships and table headers.
- **Target:** Python/HTML.
- **Repair evidence (T18, 2026-11-11):** `[TESTED]` baseline re-measure on `c258bec5…414b7cb` isolated the six unnamed tables — all from `raw_reported_block` (L25/LEC rēķins tables; the wrapping `role="region"` was named, the `<table>` element was not). Repair: `raw_reported_block()` gives the `<table>` the same `aria-label` as its region; SVG plates were verified already fully named (9/9 title+desc). Gate `tools/check_a11y_names.py` (caption / aria-label / resolving aria-labelledby on the table itself; a named ancestor region does not count) + `unnamed_table` fixture fails; final run: 86/86 tables named, 0 marker labels, 9/9 SVGs (`qa/a11y_names_gate.md`).

## H-08

**Term decision cards contain English-dominant prose.** — repaired 2026-11-09 (T02)

- **Finding:** `[INSPECTED]` historical proposal reported 23 of 32 English-dominant `.term-decision` strings; current visible text was not re-read.
- **Remediation:** student-facing decisions in Latvian, maintainer notes separate; do not invent or promote contested terminology.
- **Target:** Python/HTML.
- **Repair evidence (T02, 2026-11-09):** `[TESTED]` all 32 visible decisions are Latvian; the maintainer register moved to `qa/termbase_notes.md`; `tools/check_terms.py` fails on an English decision, on an English sentence in the visible body and on a malformed termbase row (`qa/t22/english_hits.csv`, 4 fixtures). Print control: the pre-T02 and post-T02 masters print to 130 pages with the same renderer and differ only in the computed status line on p. 71. Statuses: three terms downgraded to *jāpārbauda*, `Faradeja konstante` upgraded after the live portal check. Details: `qa/design.md` Task 22, `qa/verify.md`.

## H-09

**Bibliographic identity and convention conflicts remain unresolved.**

- **Finding:** `[TESTED]` 2026-11-09 (T03): the CRC dump was identified as Section 8 “Electrochemical Series” by Petr Vanýsek of the *CRC Handbook of Chemistry and Physics* (page footer 8-23, PDF title metadata, TeamLRN e-book, no title page), and the Campbell file as a 19-page sample of Part III “Microbial Metabolism”, Chapter 8 — in both cases **edition, year, publisher and ISBN remain unrecoverable**, so the bibliographic identity stays `unresolved` in `qa/sources.csv` while the values are `[TEXT-VERIFIED]`. The Cr₂O₇²⁻ conflict now has three recorded values (course 1,33 V, CRC 1,232 V, LibreTexts 1,36 V) and stays open.
- **Remediation:** claim-specific reaction, medium, temperature, activities, edition, locator, access date and result; preserve unresolved status until text is read.
- **Target:** Python/HTML/source ledger. See [conflict log](TERMINOLOGY_AND_SOURCES.md#conflict-log).

## H-11

**Biological wording and E°′ conditions need source review.**

- **Finding:** `[INSPECTED]` 2026-11-09 (T03): the E°′ *condition* is now text-verified — the sample’s table 8.1 carries the footnote “E′0 is the standard reduction potential at pH 7.0” (`qa/verify_bio.txt` L394) and the values at L374/L380/L391 — but the sample’s identity is unresolved and the O₂/haemoglobin phrasing still has no inspected passage.
- **Remediation:** inspect exact authoritative passage and state pH, temperature, reaction and convention; keep unresolved claims qualified.
- **Target:** Python/HTML.

## H-13

**SVG colors and selector use are unaudited.**

- **Finding:** `[INSPECTED]` prior scan counted 133 SVG hex occurrences and 65 CSS selectors absent from static markup. Counts do not prove defect; dynamic-state selectors may be valid. No SVG pixels were captured or inspected this run.
- **Remediation:** map SVG colors to semantic tokens and each selector to static/runtime markup; retain documented data colors. Visual status remains `[UNVERIFIED]` until inspected PNG evidence.
- **Target:** CSS/Python/SVG.
- **T10 partial repair (2026-11-10):** `[TESTED]` all seven inline SVG plates now carry zero color and zero font presentation attributes; every fill/stroke routes through `master.css` classes referencing `tools/tokens.json` (new SVG semantic tokens incl. `glass/membrane/sediment/pink/pink-deep/copper`, tier-3 `svg-flow-e/h`). `tools/check_svg.py` + 5 fixtures enforce the contract (`qa/svg_gate.md`, PASS on `c4931720…ee113e`). All seven figures inspected as rendered PNG/PDF pages (`qa/t30/`), so the SVG color half of this issue is closed with `[SCREENSHOT-VERIFIED]` evidence. Remaining open: the 65-selector-to-markup mapping for non-SVG CSS and ratio checking via `check_contrast.py` (T09 scope; interrupted session disclosed in `qa/t30/notes.md`).

## H-14

**Touch target measurements are historical.** — repaired 2026-11-11 (T18)

- **Finding:** `[INSPECTED]` historical CDP scan reports 178 buttons below 24×24px at 390px (295 small inline links treated as exceptions, three inputs also below size). No browser or geometry measurement was run this audit.
- **Remediation:** measure current controls at 390px; meet 24×24 CSS px or document WCAG 2.2 exception and spacing.
- **Target:** CSS/HTML.
- **Repair evidence (T18, 2026-11-11):** `[TESTED]` fresh falkon CDP geometry on `c258bec5…414b7cb` and `95bb5423…5b64` (`qa/b03/targets-pre.json`/`targets-final.json`): the historical 178 ≡ the `.eq-copy` copy control (36.1×21.8 px); remaining pre-fix smalls: 20 ref-table links (23.1 px), 1 range input (16 px), 2 label-wrapped checkboxes (13×13 / 5×13). Fix: `master.css` minimums in `px` (test root = 15 px, `rem` undershoots) — `.eq-copy`, `.ref-table a`, `input[type=range]`, `.weak-filter`, `.rad-list a`, `.set-toc a`, plus `.audit-toggle-wrap label` block-flow repair (pre-existing vertical-column collapse at 390 px, found during T18 inspection). Final: **0 sub-24 px buttons/controls at 390/768/1440**; remaining smalls documented as WCAG 2.5.8 exceptions (~300 inline-in-text links; two 18×18 checkbox boxes inside ≥24 px label targets). Keyboard: real CDP Tab walk 321 steps (`qa/b03/tab-walk-320.json`); reflow `scrollWidth ≤ innerWidth` at all widths.

## H-15

**Five-pillar coverage crosswalk is not verified.**

- **Finding:** `[UNVERIFIED]` task roadmap calls for definitions, mechanism, worked example, common mistake and term mapped per concept; `qa/trace.md` maps 75 source units, while saved recall history says 113/170 (66.47%). No concept-by-concept five-pillar crosswalk was freshly audited.
- **Remediation:** audit claims to trace and concept IDs, add only source-backed coverage; avoid treating recall percentage as pedagogy acceptance.
- **Target:** Python/HTML.

## H-16

**No-JS, print, keyboard, and file URL parity not rerun.**

- **Finding:** `[UNVERIFIED]` old `qa/design.md` records historical successful checks; the present task did not run browser, keyboard, print, no-JS or `file://` verification. `::details-content` print support remains unverified.
- **Remediation:** test on current master hash using workspace lite-shot and relevant behavior checks; inspect all PDF pages.
- **Target:** HTML/CSS/Python/TS.

## H-17

**Source and term claims remain open.**

- **Finding:** `[TESTED]` 2026-11-09 (T03): six IUPAC Gold Book entries were read from archived snapshots (`qa/t03/gb_*.txt`) — the “titration” entry supports the equivalence-point/endpoint distinction (A10) and S05917 the status of the SHE as universal reference electrode (A26) — but **no inspected entry gives the activity convention “a(H⁺)=1, p(H₂)=1 bar”**, and none mentions the pink persistence time (A11) or Latvian terminology. Pink time, “Mora pipete” usage and the Pt/Pd distinction therefore stay open.
- **Remediation:** retain `jāpārbauda` until exact source text and date are logged; do not silently adopt alternate conventions.
- **Target:** Python/HTML/source ledger. See [conflict log](TERMINOLOGY_AND_SOURCES.md#conflict-log).

## H-18

**Local source claims need fresh evidence-state reconciliation.**

- **Finding:** `[TESTED]` 2026-11-09 (T03): the claims named by the task (A2–A5, A10–A13, A24–A27) were reconciled against the local dumps and archived source pages, and each now carries a system scope, conditions, warrant limit and provenance in `qa/claims.csv`. The rest of the ledger still has no claim-to-source locator, and the five course binaries were not re-read against the original PDFs/DOCX in this pass.
- **Remediation:** future content pass must reconcile claims against page images/text and recorded evidence; keep the existing source logs unchanged until authorized.
- **Target:** Python/source ledger. See [verified source registry](TERMINOLOGY_AND_SOURCES.md#verified-source-registry).

## Audit limits

This audit ran filesystem inventory, file hashes/stat, stdlib HTML parsing and static source reads. It did not build, execute QA gates, access external sources, render screenshots, run assistive technology, test browser behavior, or inspect PDF pages. No issue above is closed by this governance update.
