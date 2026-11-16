# Python, TypeScript and JavaScript Audit

**Parent Contract:** `../../AGENTS.md`  
**Extends:** AGENTS.md §§4, 10, 12  
**Last updated:** 2026-11-07 · **Status:** [INSPECTED] source/static audit; no runtime or build executed for this governance-only pass.

## [LANGUAGE-STACK]

**Four-language ownership and runtime ceiling.**

| Tier | Language | Ownership | Contract |
|---|---|---|---|
| 1 | HTML5 + CSS | ≥95% of interactive/visual behavior: content structure, disclosure, state, responsive and print | Native semantics and CSS state first; zero inline `style=` and `on*=` attributes. |
| 2 | Python 3 | Deterministic extraction, build, precomputation and verification before the browser | Standard library preferred; `python3 -I`; final HTML has no runtime dependency. |
| 3 | TypeScript | Residual browser behavior that HTML/CSS/Python cannot provide | `strict: true`, no `any`, explicit DOM null checks; compile offline and inline only minimized output. |
| 4 | JavaScript | Compiled artifact only, never the primary source architecture | Entire executable content ≤ min(4,096 bytes, 100 formatted lines, 2% of HTML bytes). Every function must belong to the explicit registry below. |

Forbidden runtime behaviors: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, DOM templating, runtime data-array-to-HTML hydration, JS-driven UI where native HTML/CSS suffices, scroll-jacking, decorative `requestAnimationFrame`, third-party runtime libraries, QA hooks, network APIs, and persistent storage without informed opt-in. No `application/json` data block without an explicit byte budget and Python generation.

## [PERMITTED-JS-MICRO-RUNTIME]

**Registry and shared allocation.**

The allocations below are a **shared maximum**, not additive exceptions to the global ceiling. Total may not exceed 4,096 bytes or 100 lines or 2% of the master; the strictest limit wins.

| ID | Function family | Maximum allocation | Why not HTML/CSS or Python | JS-off behavior |
|---|---|---:|---|---|
| J1 | `themeInit` | 300 B / 10 lines | Optional persisted preference applied before first paint | `prefers-color-scheme`; reading remains available; hide persistence control if no JS. |
| J2 | `calc` for arbitrary numeric inputs (calibration, significant-figure arithmetic, half-life, solution/dilution) | 1,796 B / 45 lines | Learner-entered values cannot be exhaustively precomputed | Static worked cases and key answers stay visible; calculators are labelled unavailable without JS. |
| J3 | `search` from rendered DOM | 2,000 B / 45 lines | Free-text lookup across user-visible content is dynamic; stored duplicate index is disallowed | Search hidden/unavailable; TOC and glossary links remain. |
| — | Reserve | 0 B / 0 lines | Allocate only after a documented teaching need and source trail | No degradation beyond above. |

**Current status:** not compliant. The live master has 56,475 executable bytes / 1,087 lines (5.729% of a 985,696-byte HTML file); the computed ceiling is 4,096 bytes and 100 lines. Current implementation exceeds budget by bytes and lines. Do not treat the registry as approval for an oversized implementation. Any expansion requires a dated governance edit specifying function, exact budget, rationale and JS-off behavior.

## [FUNCTION-INVENTORY-AND-MIGRATION]

**Current master audit.**

### [MEASUREMENT]

2026-11-07 static scan (product pass, after JS-06 trainer removal): 1 executable inline script, 41,938 UTF-8 bytes, 769 script-content lines; total HTML 969,738 bytes; 4.33%; 0 inline event attributes. `build/app.js` is 40,792 bytes / 768 lines. No external script tag was observed. There are 30 `addEventListener` call sites and 0 `localStorage`/`sessionStorage` references. Static token counts were zero for `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `createElement`, `requestAnimationFrame`, `fetch`, `XMLHttpRequest`, `sendBeacon`. Runtime smoke (Firefox 159 headless over WebDriver BiDi): 0 console errors; calibration, significant-figure, half-life and solution calculators plus search drive and render correctly. These token counts do not waive size, functionality, or runtime review.

### [FUNCTION-VALUED-CONSTANTS]

`effectiveDark`, `syncTheme`, `foldQ`, `tokQ`, `skipped`, `blocked`, `textOf`, `ensureIndex`, `buildIndex`, `push`, `runSearch`, `tokenRx`, `snippetFor`, `closeSearch`, `renderSearch`, `supExp`, `fmtFixed`, `fmtGrouped`, `parseDecimal`, `roundTo`, `formatSig`, `fmtTrim`, `makeLine`, `setOutput`, `unitSuffix`, `calRun`, `updateSfFields`, `sfFail`, `runSf`, `normAns`, `checkSftMatch`, `updateSftDisplay`, `evaluateSft`, `convNumber`, `repS`, `runHl`, `solField`, `showSolLabels`, `updateSolFields`, `solInvalid`, `runSol`, `runGr`; plus one wrapping IIFE. Event-listener call sites: 38; types/counts: `click` 10, `change` 9, `input` 8, `keydown` 10, `blur` 1.

Finite object data removed 2026-11-07 (JS-06): `sftCases` and `grTasks` no longer ship; the ch8/ch9 static case tables are the single surface. `solDefaults`, `TYPE_LABEL`, `LVFOLD`/`DIA`/`supMap` remain and count toward the shared ceiling. Case and label data that can be represented in static markup or generated by Python belongs in build-time output; this is part of the over-budget migration issue.

### [MIGRATION-MAP]

| Current family | Destination | Rationale / retained behavior |
|---|---|---|
| `effectiveDark`, `syncTheme` | J1 TypeScript output | Only early persisted preference can justify script; CSS system preference is fallback. Avoid conflating theme button state with persistence. |
| `foldQ`…`renderSearch` | J3 TypeScript output after reduction | Search can derive visible content; never materialize recall answers or ship a duplicate prose index. Python owns policy validation and byte checks. |
| `supExp`…`runSf`, `convNumber`/`repS`, `runHl`, solution helpers/`runSol` | Split: Python pre-renders finite cases/data; TypeScript retains only arbitrary-input calculations | Do not ship finite trainer case arrays/answers in JS if static markup suffices. Preserve validation, units, significant figures, error states and explanatory output. |
| Any UI toggle, disclosure, modal, tooltip, tab, recall queue or exam assembly | HTML/CSS or Python-generated markup | Native `<details>`, `:has()`, `:checked`, `:target`, `<dialog>`, Popover API; static exam packets. |
| QA-only hooks or test instrumentation | QA harness only; never master | Strip from deliverable and assert absence in build gate. |

No refactor is authorized by this shard itself. Product work must follow the current lock and preserve the canonical master fingerprint for governance-only tasks.

## [PYTHON-CLI]

**Build and checker contract.**

Common CLI contract: run from workspace root using `python3 -I`; deterministic output; exit 0 only on success, nonzero on violations; concise machine-readable or tabular stdout; no network, external runtime dependency or destructive cleanup. Read-only checkers do not rewrite the master.

| Entry point | Inputs / behavior | Pass conditions |
|---|---|---|
| `tools/check_budget.py` (missing) | master path optional; parse executable scripts and inline handlers; compute bytes, formatted lines and percent; inspect JSON blocks, banned runtime tokens, `style=`/`on*=` and AGENTS byte ceiling | Every configured ceiling met; report measured values and exact offenders. |
| `tools/check_contrast.py` (missing) | token pair registry and CSS light/dark values | Report actual WCAG ratios per pair; normal text ≥4.5:1; large/UI ≥3:1; fail missing/low-contrast pairs. |
| `tools/check_anchors.py` (present) | canonical HTML | Unique IDs, all local hash links resolve, heading hierarchy/order valid; current pass did not execute it. |
| `tools/check_selfcontained.py` (missing) | canonical HTML and embedded style/script | No external links/assets, remote fonts, network API use or runtime dependency. |
| `tools/check_index_privacy.py` (present) | master and search policy | No stored prose index; skip policy excludes recall answers/answer sheet; self-test must prove mutation failure. |
| `tools/check_sources.py` and `build/check_sources.py` (present) | `build/sources.json`, `claims.json`, source files and live needles | Schema, unique IDs, V2/hash/locator/needle consistency, C01–C20; `--strict-open` fails on intentional open claims. |
| Existing `build/check_*.py`, `verify_numbers.py`, `audit_tables.py` | Canonical source data and output | Execute only within a product-pass authorization; a pass is not source, editorial, visual or accessibility acceptance. |

Checker implementation is absent unless marked present above. Proposed behavior is not evidence of a gate passing.

## [TYPESCRIPT-CONTRACT]

**Source and compilation.**

- Source files under `ts/`; `tsconfig.json` sets `strict: true`, `noImplicitAny`, DOM libraries and no runtime module dependency.
- Use typed interfaces for DOM contracts and calculator inputs/results; guard every queried element (`HTMLElement | null`) before use; no `any`, unsafe casts, generated HTML strings or global QA hooks.
- Compile/minify reproducibly offline; emit only whitelisted functions; embed compiled output in the single inline script. Record compiler version and command; strip source maps and test-only code.
- Current gap: no `ts/`, no `tsconfig.json`, no `tsc` recorded. Do not claim TypeScript compliance from JavaScript source.

## [VERIFICATION-SUITE]

**Separate evidence gates.**

1. Static: hashes/sizes/mtimes; budget script; self-contained and anchor checks; source/schema and numeric checks.
2. Runtime: calculator boundaries and invalid input, search/privacy, theme/storage denial and reload, keyboard and JS-off behavior. Use supported browser only under the visual policy.
3. Visual: `lite-shot` falkon/falkon screenshots, directly inspected at relevant desktop/mobile/theme states.
4. Print: export and inspect every page for disclosures, pagination, tables, figures and colophon.
5. Source/editorial/AT: primary-source locators, course-conflict adjudication, keyboard, screen reader and lecturer policy remain distinct gates.

Never combine these into a single “passed” claim. Governance-only work runs integrity and shard checks; it does not imply product acceptance.
