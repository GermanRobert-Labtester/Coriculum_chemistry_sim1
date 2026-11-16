# Open Issues Ledger

> Parent Contract: `../../AGENTS.md`  
> Extends: AGENTS.md §2, §12  
> Last updated: 2026-11-07 · Status: `[TESTED]` structural counts; content claims retain their evidence tags.

This ledger records work still open against the live master. Historical closures belong in `CHANGELOG_ARCHIVE.md`. Line numbers refer to the 2026-11-06 master snapshot (`1,556,007 B`, 7,465 lines, SHA-256 `3528884dc2c1251c7c093024b5deac4f4d2eec106b524e50ee29c0c8c2629b14`); remeasure before editing.

## Issue map

| ID | Location | Finding | Target | Evidence |
|---|---|---|---|---|
| A01 | Executable script, L5200–7463 | 121,642 B / 2,263 lines / 7.818% of master; 125 functions and 67 listeners in prior measured census; exceeds 4,096 B / 100-line / 2% ceiling. | HTML/CSS/Python/TS | `[TESTED 2026-11-07]` |
| A02 | `initNotes`, `initHashOpen`, `initCheatMode`, `initReportMode`, `initDiagnoser`, `initInstrumentA11y` L5694–5824; `initInstrumentHash`, `initMasthead`, `initDocTools`, `initSelfCheck` L6876–6987; `initChain`/`Path`/`Cycle`/`Occlude` L7253–7425 | Disclosure, mode, filter, stepper, occlusion and URL state duplicate native browser/CSS behavior (historical estimate ≈17.6 KB). | HTML/CSS | `[TESTED]` / `[INFERRED]` |
| A03 | `svgShell` L5634; `initDistribution` L5915–5921; `initOrder` L6385–6426; `initMM` L6570–6582 | 12 `innerHTML` uses perform banned string injection/markup generation. | Python/HTML | `[TESTED 2026-11-07]` |
| A04 | `initScrollHints` L7067; `initMatrix` L7120–7179 | 9 `createElement` calls generate runtime controls/answers (matrix block ≈8,352 B). | Python/HTML/CSS | `[TESTED 2026-11-07]` |
| A05 | `initDrill` L6988 | 3,063 B; `rand`/`shuffle` make drill ordering runtime-generated and nondeterministic. | Python/CSS | `[TESTED]` |
| A06 | `initDistribution`, `Unit`, `Dose`, `Arrhenius`, `Profile`, `Order`, `MM`, `Lab`; plotting library L5200–5693 | Calculators/plots ≈63,356 B; library ≈25,720 B. Plot geometry, ticks, labels and presets can be precomputed; `watchPlot` uses ResizeObserver+rAF L5655–5661. | Python/CSS; TS only for arbitrary-input arithmetic | `[TESTED]` / `[INFERRED]` |
| A07 | `initPrintState` L5765 | 1,636 B print-state hook; print expansion depends on JS and fails with JS disabled. CSS `::details-content` support remains engine-dependent. | CSS/TS | `[TESTED]` / `[UNVERIFIED]` |
| A09 | `<head><style>`, 186,820 B | No `@layer`; 60 `!important`; no `@container`, `subgrid`, `:focus-within`, `@starting-style`; 4 `clamp()` calls. | CSS | `[TESTED]` |
| A10 | Inline `style` L1113–4730 | 77 attributes: 49 `--vbw`, 26 `--minw`, shared-defs positioning and one margin. | Python/CSS | `[TESTED 2026-11-07]` |
| A11 | `tools/`, `verify/` | No architecture gate for JS budget/registry/banned APIs, inline styles, layer order, AGENTS byte ceiling, or HTML conformance. Node `.js/.mjs` checks remain outside the target stack. | Python/TS | `[TESTED]` |
| A12 | Workspace root | No `ts/`, `tsconfig.json`, or `pyproject.toml`; strict TS compiler setup absent. | TS/Python | `[TESTED]` |
| A14 | SVGs at L1113, 1438, 1572, 1733–1735, 1778, 2100, 2322, 2866, 2868, 4294–4299 | 82 `<svg>`, 75 `role="img"`, 0 `<symbol>/<use>`; inspect individual title/description/label relationships and reuse before claiming semantic or visual quality. | HTML/Python | `[TESTED]` markup counts; visual `[UNVERIFIED]` |
| A15 | ch.13/Table 12; `SOURCES_AUDIT.md` K10, K17, L1 | K10 catalase value/unit awaits lecturer; K17 example/source match open; L1 MnO₂ chemistry plausible but course-key intent unconfirmed. | HTML + source evidence | `[INSPECTED]` / `[UNVERIFIED]` |
| A16 | `CHECKS.md` §§4–6 and six course PDFs | Saved browser/print/AT outcomes are historical; source PDF text was not re-extracted in this run. | Python/HTML/CSS | `[UNVERIFIED]` |
| A18 | `#appA-clinical`, `#appA-elim` near L4660; ch.11 | Rang & Dale 9e, Goodman & Gilman 13e, Lehninger 7e are leads; the claim “most listed drugs first-order” lacks opened supporting sections. | HTML + verified sources | `[INSPECTED]` / `[UNVERIFIED]` |
| A19 | `termbase.json`; ch.6/ch.11/`#appA-*` | `farmakokinētika`, `farmakodinamika`, `eliminācijas konstante`, `stacionārais stāvoklis`, `uzkrāšanās koeficients` are used but not governed. | Python/data/HTML | `[TESTED]` / `[INSPECTED]` |
| A20 | Workspace root | `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` absent; the roadmap is present and active. Reconcile if missing authorities arrive. | Governance | `[TESTED 2026-11-07]` |
| A21 | Root snapshots and `tools/*.bak.*`; no `.git` | Manual snapshots clutter root; no VCS history; archival provenance is incomplete. Defer movement/VCS setup to an authorized production pass. | Python/governance | `[TESTED]` |
| A22 | `PROMPT_master_kinetika.md` | Historical prompt specifies system fonts and ≤1.5 MB, conflicting with five embedded fonts and current 1,556,007 B master. Current AGENTS contract takes precedence. | Governance | `[INSPECTED]` |

## [ISS-ARCH] Architecture migration blueprints

### [ISS-JS-STATE]

Replace disclosure and mode toggles with native `<details>/<summary>`, radio/checkbox state plus `:checked`/`:has()`, and `:target` where deep links are useful. Use `<dialog>` only for true modality and Popover API for term/footnote previews. Keep stable fragment targets. Do not port the current JS state machine wholesale.

### [ISS-JS-GENERATION]

Move SVG, labels, controls, answer markup, matrix rows, and drill order generation to deterministic Python builders. Emit fixed preset states as static SVG/HTML, switched with CSS. Do not use runtime markup strings, `createElement` loops, random ordering, or resize redraws. SVG `viewBox` scaling should handle viewport changes.

### [ISS-JS-CALCULATORS]

Precompute finite cases (distribution, order, inhibition, profile, lab illustrations) in Python. Retain arbitrary-input arithmetic only when required by learning outcomes and only in R2 `calc`; type it in strict TypeScript and validate output text/numeric values. Supply static tables/figures inside `.fallback-details` and one `<noscript>` fallback per live instrument.

### [ISS-CSS]

Declare `@layer reset, tokens, base, layout, components, utilities, print;` first; put each rule in a layer; eliminate `!important` outside reset/utilities. Replace inline variables with named classes/tokens from generated markup. Measure body prose at 60–75ch; use intrinsic grid/flex, `clamp()`, and container-aware layout. Add engine-recorded print expansion and JS-off behavior.

### [ISS-SOURCES]

For K10/K17/L1 preserve the exact course statement, proposed correction, and reason in separate visible fields. Reopen the cited course page and named authority before changing a factual claim. Literature measurements from other catalase organisms/assays do not establish the course value. Do not infer textbook passages from catalog metadata.

