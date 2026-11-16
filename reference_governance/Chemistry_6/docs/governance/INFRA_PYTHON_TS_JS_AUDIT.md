# Python, TypeScript and JavaScript Audit Contract

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 10, 12  
Last updated: 2026-11-12  
Verification: `[INSPECTED]` current tool inventory; `[TESTED]` static master script accounting. No build or gate runner was executed.  
T34 amendment: the Reserve registry row is now the named `searchIndex()` runtime (same 1,396 B / 40-line budget, net-zero aggregate change); its measured block is 1,337 B / 14 lines (`tools/check_search.py` asserts it).  
T18 amendment: `check_a11y_names.py` is now implemented per the interface below (tables named; no `^ _ ->` in speech labels; SVG title/desc references; fixtures `qa/a11y_fixtures/` 6/6; report `qa/a11y_names_gate.md`). Presence checks still do not prove spoken quality.  
T20 amendment (2026-11-12): the gate set below is now implemented and machine-checked — `lint_js_budget.py` (§4 caps, function/data-island registry, banned sinks, inline handlers, external scripts; fixtures `qa/t40/fixtures/` 6/6), `lint_agents_size.py` (AGENTS byte cap + workspace-reference integrity; fixtures 5/5), `check_contrast.py` (WCAG ratios for every `tokens.json` `contrast_pairs` row, var()-coverage, raw colour literals outside the tokens layer; fixtures 5/5), aggregate `check_all.py` (task-dir-confined outputs; never builds/exports) and `tools/make_manifest.py` (artifact hash manifest; `--check` fails on drift, control drift or a stale release-PDF binding). Eight existing gates gained an optional `--report` redirect; default report paths unchanged. On the current master the JS and contrast gates are red by design (JS-01/02/03, CSS-02) and the manifest check fails on the stale PDF (H-06); see `qa/t40/evidence.md`.

T22 amendment (2026-11-12): F03 added `check_value_evidence.py` (registry row below, fixtures 7/7, registered in `check_all.py` as `value-evidence`). It adds no JS: value evidence is static `<details>` panels plus anchor links, and the `#master-data` island is byte-identical to T20 (60,439 B).

F08 amendment (2026-11-12): `statePort()` registered (row below) **before** the function shipped; gate `check_state_port.py` registered in `check_all.py` as `state-port`, fixtures 10/10. Measured block 1,719 B / 32 lines inside the ≤1,800 B / ≤40-line budget; executive JS total rises to 68,572 B (JS-01 stays red by design). The port writes only `redox-unsure-v1` and performs no network I/O (live battery: zero non-blob resource entries).

## Language stack

| Tier | Language | Contract |
|---|---|---|
| 1 | Semantic HTML5 + CSS | Primary structure, layout, rendering and state; target ≥95% of interactive/visual behavior. Native semantics and CSS selectors first. |
| 2 | Python 3 stdlib | Offline extraction, deterministic build-time rendering, SVG/data generation, precomputation and lint. Invoke `python3 -I`; final HTML has no runtime dependency. |
| 3 | TypeScript | Source for necessary client logic only; `strict: true`, zero `any`, explicit DOM null checks, compiled and stripped into minimal inline output. |
| 4 | Raw JavaScript | Suppressed micro-runtime only, within registry and aggregate caps. Unregistered function fails. |

One standalone HTML contains embedded CSS/SVG/WOFF2; no CDN, runtime request, analytics, external font or JS library. It must remain meaningful with JS off and open under `file://`.

## JS budget and whitelist

Total executable `<script>` content ≤4,096 bytes, ≤100 formatted lines and <2% of full HTML bytes (all limits apply; smallest wins). JSON data islands count toward the 2% limit and require a registry row. Banned: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `createElement` used for templating, data-array-to-HTML loops, JS UI controls where native HTML/CSS suffices, scroll-jacking, decorative `requestAnimationFrame`, external libraries. Inline event handlers are prohibited.

### Permitted JS micro-runtime registry

| Function | Budget | Why HTML/CSS + Python cannot do it | JS-off behavior |
|---|---|---|---|
| `markUnsure()` | ≤900 B / ≤30 lines | Persistence across reload needs Web Storage | `<noscript>` note; native/session marks only; prompts readable |
| `calcTitr()` | ≤1,800 B / ≤45 lines | Arbitrary entered volumes cannot be precomputed | `<noscript>`; static L25 worked example + blank template; print unaffected |
| `searchIndex()` | ≤1,396 B / ≤40 lines | Typed diacritic-folded filtering over a pre-rendered index cannot be precomputed per query; T34/F01 amendment replaces the former Reserve row at the same budget | No-JS: static 13.H A–Z appendix (`#raditajs`); dialog hidden; print suppressed |
| `statePort()` | ≤1,800 B / ≤40 lines | F08/T46 amendment (2026-11-12, made before the function shipped): learner-initiated Blob download and strict File validation cannot be done in HTML/CSS/Python; writes only the registered `redox-unsure-v1` key, schema v1 `{version:1,unsure_ids}`; reject-before-replace with explicit confirm | No-JS: controls sit inside the `.js-only` `.weak-controls` row and stay hidden; marks remain session-local per `markUnsure()` degradation; print suppressed with `.weak-controls` |

Registry amendment must precede any new function. The present master exceeds every aggregate ceiling and the JSON island alone exceeds the percentage budget; none of its existing handlers is grandfathered as compliant.

## JS forensic audit

Static `HTMLParser`/regex scan, 2026-11-07, master hash `a081c593…0258e5f`:

| Payload | Bytes | Lines | Finding |
|---|---:|---:|---|
| Early executable flag script (line 1461) | 45 | 1 | Adds `.js`; fold into documented progressive-enhancement contract only if retained |
| Main executable block (line 4591) | 66,083 | 1,356 | ~70 named local functions; 53 listeners, 3 timeouts; exceeds cap |
| Executable total | 66,128 | 1,357 | 4.540% of HTML; cap fails |
| `application/json#master-data` (line 4590) | 56,636 | 1 | 3.889% of HTML; cap fails on its own |
| Executable + JSON data island | 122,764 | — | 8.428% of HTML under combined byte accounting |
| DOM construction patterns | 27 `innerHTML`, 9 `createElement` | — | Banned where used for content/template generation |

**Named functions/arrow-function variables found in `tools/assets/master.js` (68 unique names):** `$`, `$$`, `nf`, `nfFixed`, `sigFigs`, `formatValue`, `unit`, `esc`, `lcm`, `announce`, `asNumber`, `onConvention`, `setConvention`, `i1`, `sup`, `fmtConc`, `fmtBig`, `slopeText`, `targetLabel`, `compute`, `k`, `describe`, `render`, `i2q`, `i2`, `update`, `i3`, `stepsIn`, `stepName`, `diffText`, `setExampleOptions`, `gotoS`, `i5`, `renumberTitres`, `setMode`, `check`, `reset`, `i4`, `show`, `copyText`, `readState`, `outlier`, `row`, `set`, `showCard`, `isOk`, `updateFilter`, `matchType`, `matchCh`, `apply`, `q`, `hay`, `syncScrollHints`, `eqToPlain`, `setAudit`, `checkAuditHash`, `applyChlogFilters`, `matchGroup`, `revealTargetChlogRow`, `isAll`, `save`, `updateCount`, `addLink`, `updateReport`, `applyFilter`, `applyMarks`, `before`, `after`. Anonymous callback functions are included in the executable byte/line total and listener count.

**All 53 `addEventListener` invocations, grouped by source line(s) and behavior:** 93 (convention change); 300–304 (I1 selection/reset); 372–373 (I2 selection/reset); 485–486 (I2 slider/reset); 546–554 (I3 previous/next/example/step/reset); 579 (mode buttons); 605–606 (I6 check/reset); 833–834, 852, 862–866, 883–890 (I4 row add/remove/input, titre edits, mode, reset, copy and calculation fields); 910, 934, 939, 951, 995, 1003 (lab/chapter drills); 1042, 1075, 1080, 1091, 1118 (filter/input/resize/navigation/copy); 1154, 1157, 1160, 1168 (audit state and hash); 1199, 1212, 1246, 1323, 1330–1331 (changelog, weak-mark filters/hash); 1352–1353 (before/after print). Multiple calls share some listed lines; count is invocation count, not line count.

The audit identified function families for I1 potential pair selection (`i1`), I2 pH/Nernst (`i2`), I3 balancing path (`i3`), I4 titration (`i4`), I5/lab mode (`i5`), audit banner/filtering (`setAudit` and filter helpers), equation-copy speech (`eqToPlain`), recall marks and report. Historical source line references: `i1` ~97, `i2` ~381/494, `i3` ~494, `i5` ~562; confirm current source before edits. Function signatures/counts are diagnostic inventory, not a migration authorization.

| Function family | Target |
|---|---|
| I1/I2/I3 finite data and state | Python-precomputed values plus radio/checkbox/`:has()` or `:target`; static transcript |
| I4 arbitrary titration input | Keep only as `calcTitr()` after strict TS authoring and budget validation |
| I5/lab mode and audit view | Native state controls + CSS; preserve URL mode only with explicit fragment registry |
| Filters/report/static indexes | Python pre-render plus native checkboxes/details; remove array-to-HTML loops |
| Equation copy | Keep only if a measured learning need justifies it and a registry function is explicitly approved |
| `markUnsure()` persistence | Strict TS localStorage wrapper with schema validation and `<noscript>` behavior |

## DOM generation migration

1. Inventory each DOM sink and the exact generated node/data.
2. Move fixed content and deterministic choices into `tools/build_master.py`; emit accessible HTML once.
3. Move computed tables to Python and native controls to CSS state.
4. Preserve focus, labels, no-JS, print and error states before deleting a handler.
5. Re-run byte/function lint against generated HTML; do not claim parity based on source diff alone.

## TypeScript contract

If any function survives: add `tools/ts/` and strict `tsconfig.json`; no `any`, check queried elements for `null`, scope event types, isolate storage errors, compile deterministically, strip comments/source maps and inline only emitted runtime. Measure final executable bytes, formatted lines and file percentage, and confirm functions are a subset of the registry. If compiler/toolchain is unavailable, do not replace this contract with hand-authored large JS.

## Python CLI

Use only Python stdlib unless an existing dependency is specifically authorized. Every CLI: deterministic inputs, explicit paths/arguments, non-zero on failure, no implicit build/export/network/browser, and any report only under `qa/<task>/`. Invoke as `python3 -I tools/<name>.py ...`.

| Script | Required checks / interface |
|---|---|
| `lint_js_budget.py` ✅ T20 | Read canonical HTML and registry; count executable scripts, formatted lines, JSON data islands and HTML percentage; detect banned sinks, inline handlers, and unregistered function names. Non-zero on any cap/pattern violation. Reports: `--report` JSON+MD. |
| `lint_agents_size.py` ✅ T20 | Check `AGENTS.md` ≤24,576 bytes and referenced workspace paths exist or are explicitly marked future targets. Reports: `--report` JSON+MD. |
| `check_anchors.py` ✅ T17 | Parse IDs; reject duplicates; resolve every `href="#…"`, `for`, `aria-labelledby`, `aria-describedby`; explicitly allow registered mode hashes such as `#audit`. `--report` redirect added in T20. |
| `check_contrast.py` ✅ T20 | Parse token foreground/background pairs, compute WCAG relative-luminance ratio for every theme/state and SVG semantic color use; output failing pair and ratio. Reports: `--report` JSON+MD. |
| `check_a11y_names.py` ✅ T18 | Name every table; ensure speech labels contain no source `^ _ ->`; validate SVG title/desc references and label IDs. Presence checks do not prove spoken quality. `--report` redirect added in T20. |
| `check_term_refs.py` ✅ T21 | Unwrap `a.term-ref` anchors, re-derive first-clean-occurrence placements via the shared `tools/termref.py` policy and compare byte-for-byte; check pilot completeness, one link per term, canonical link text, and exactly one glossary term-card anchor per linked id. `--fixtures` suite in `qa/termref_fixtures/`. `--report` redirect. |
| `check_value_evidence.py` ✅ T22 | Parse the master: every NUMBERS+COUPLES id has exactly one `details.value-evidence[id="ev-<id>"]`; every value span (`data-num`, `data-couple`) is wrapped in its own `a.value-ref`; required fields, summary value equals the registry display value, status vocabulary, `source_id` resolves in `qa/sources.csv`, CRC/CAMP citations keep "izdevums nenosakīts", disputed trio cites dumps + 13.E, no anchor nesting. `--fixtures` suite in `qa/valueevidence_fixtures/`. `--report` redirect. |
| `check_state_port.py` ✅ F08 | R1 port controls present (export button, JSON-limited file input, live status, hidden download anchor) and the removed staged-confirm shape absent; R2 statePort block within its registry budget with schema, byte-cap and confirm-before-write markers, no banned sinks/network; R3 localStorage keys ⊆ `redox-unsure-v1`; R4 print parity. `--fixtures` suite in `qa/f08/fixtures/` (ok-*/fail-* mirror of the import validator, same check order). `--report` redirect. |
| `terms_lint.py` ✅ T47 | Term-schema gate for the frozen CSV artifact `tools/terms.csv` (schema terms/v1; generated from `tools/termbase.py` by `terms_export.py`, which refuses an invalid registry). R1 header comments + exact column header; R2 duplicate `term_id`; R3 duplicate `chapter_anchor`; R4 id shape (termbase vocabulary incl. Latvian diacritics), anchor `=#term-<id>`, required fields, termbase status vocabulary; R5 CSV↔registry equality incl. units occurring verbatim in definition/example; R6 every anchor exists as `class="term-card" id="term-<id>"` in the master and no orphan term anchors (the `#term-cards` container is excluded). `--fixtures` suite in `qa/terms_fixtures/` (ok + fail per rule, with `.html`/`.registry.json` stubs). `--report` redirect. Registered as `terms-schema` (composable). Proves schema/anchor consistency only. |
| `check_all.py` ✅ T20 | Run registered read-only gates, capture per-gate exit/result and current master hash; write one report to a passed QA task directory; never build or export implicitly. Non-composable gates (fixed external outputs or network) are registered but withheld unless named via `--only`. |
| `make_manifest.py` ✅ T20 | Artifact hash manifest (product, generator chain, authority sources, release-PDF binding, GOV-01 control inventory); `--check` re-verifies and fails on drift or a stale PDF. |

Existing gates that may be composed after side-effect review: `check_balance.py --corpus`, `check_balance.py --data`, `verify_numbers.py`, `check_terms.py`, `audit_notation.py`, `lint_ox_state.py`, `recall_matrix.py`, and `test_notation.py`. Some write to `qa/`; inspect implementation before invocation. `extract_docx.py` writes its requested destination.

## Historical QA tools

Inventory found 39 `qa/**/*.mjs` files, including `qa/overflow*.mjs`, `qa/t07_playwright.mjs`, and task-specific browser measurements. They may depend on Node/Playwright/browser, mutate reports, or capture screenshots. Read each tool and side effects before running. Saved output is historical until matched to the current master hash. Port maintained structural/numeric checks to Python; TypeScript is for source-typed browser logic, not test runner convenience.

## Verification suite

| Gate | Evidence needed |
|---|---|
| Architecture | Script bytes/lines/percent, data-island bytes, no banned patterns, only registry names |
| Python/TS | stdlib isolated invocation; strict TS compile and deterministic output where applicable |
| Structure/a11y | Unique IDs/fragments/ARIA refs, named tables, speakable labels, SVG titles and descriptions |
| Visual/UI | lite-shot PNG from falkon or falkon at 390/768/1440, direct pixel inspection; no Chrome unless explicitly allowed in current turn |
| Behavior | Keyboard, reduced-motion, JS-off, `file://`, offline/no requests, local state/error recovery |
| Print | Fresh PDF bound to HTML SHA; every page inspected; details open, answers once, templates blank |
| Governance | Only authorized docs changed in governance-only task; AGENTS bytes ≤24,576 and master hash/size/mtime unchanged |

No saved green report, code scan, parser, or test gate implies visual, scientific, print, or accessibility acceptance outside its measured scope.
