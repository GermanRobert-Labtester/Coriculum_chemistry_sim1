# Python, TypeScript and JavaScript Audit Contract

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 10, 12  
Last updated: 2026-11-07  
Evidence status: static source/output audit `[TESTED]`; no build, checker, browser, or runtime was executed in this governance-only run.

## [FOUR-LANGUAGE-STACK]

Language order and boundaries.

| Tier | Language | Responsibility | Gate |
|---|---|---|---|
| 1 | semantic HTML + modern CSS | ≥95% of visual and interactive state; offline reading, disclosure, forms, responsive layout, theme/state presentation | native interaction; no inline `style=` or `on*=` |
| 2 | Python 3 | deterministic offline extraction, validation, precomputation, SVG geometry, search/index/data generation, byte budgets | stdlib preferred; isolated invocation; deterministic output; nonzero on failure |
| 3 | TypeScript | only residual logic that needs arbitrary client input or browser-only state | `strict`, `noImplicitAny`, `noUncheckedIndexedAccess`; zero `any`; explicit DOM null/input checks; compiled/minified and measured |
| 4 | raw JS | suppressed output of reviewed TS micro-runtime only | no unregistered function, framework, external script, DOM templating, or UI state duplicating HTML/CSS |

No CDN, external runtime, fetch/network dependency or font dependency in the final standalone master. Build/report tools may use permitted local utilities, but must declare side effects and not silently overwrite unrelated evidence.

## [JS-SUPPRESSION-REGISTRY]

Hard ceilings and allowed hooks.

Executable inline `<script>` total ≤min(4,096 UTF-8 bytes, 100 formatted lines, 2% of HTML bytes). JSON data blocks are not executable and are counted separately against total HTML. Banned: `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, templating with `createElement`, runtime data-array hydration, inline event attributes, JS accordions/tabs/modals/tooltips/search UI when native HTML/CSS suffices, scroll-jacking, RAF/interval animation, libraries/frameworks. A function not in the registry is disallowed.

| Function | Exact max | Why HTML/CSS + Python cannot do it | JS-off behavior |
|---|---:|---|---|
| `themeInit` | 300 B / 8 lines | read an explicit saved preference before first paint | system `prefers-color-scheme` |
| `themeToggle` | 400 B / 12 lines | persist an intentional per-user theme choice | system theme, toggle absent |
| `dialogEdge` | 500 B / 15 lines | narrowly scoped focus return/Escape edge cases where native dialog behavior is incomplete | `<details>` or `:target` explanation |
| `thermoCalc` | 2,000 B / 45 lines | arbitrary numeric student input and immediate derived thermodynamic result | Python-built lookup table and `<noscript>` explanation |
| `errorLog` | 800 B / 20 lines | optional local persistence and explicit deletion/export | log hidden; reading and tasks unaffected |

Aggregate ceiling still applies; per-function ceilings do not add permission to exceed 4,096 B/100 lines/2%. Each entry requires tested null checks, finite/range validation, storage-failure handling where applicable, keyboard path, and visible fallback.

## [CURRENT-SCRIPT-AUDIT] Script blocks, inline handlers and function census

Captured master SHA: `36041054f1fb25f5eea744562aa204da3ede41923c0d827fa95dff9fbe3f2416`.

| Block order | Type / id | UTF-8 body bytes | Lines | Classification |
|---|---|---:|---:|---|
| 1 | `application/json#search-index` | 238,649 | 1 | data; not executable |
| 2 | `application/json#exam-bank` | 38,094 | 1 | data; not executable |
| 3 | `application/json#thermo-test-vectors` | 6,896 | 102 | data; not executable |
| 4 | executable, no type | 266,071 | 6,070 | JS; 10.70% of master bytes; hard failure against every budget |

Data block bytes sum to 283,639. The extracted executable block has 178 unique named function names (184 declaration matches including nested/duplicates) and 167 event-listener registration calls. Static lexical counts: `innerHTML` 40; `createElement` 52; `outerHTML` 0; `insertAdjacentHTML` 0; `document.write` 0; `requestAnimationFrame` 2; `setInterval` 2; `setTimeout` 9; `Math.random` 5; `Date.now` 1. These counts are reproducible static evidence, not a semantic reachability/runtime trace.

Parsed inline attributes total 67: `onclick` 62, `onsubmit` 3, `oninput` 2. Zero-inline-handler target is unchanged. Old OI-17’s 62 number counted only `onclick`; old report’s 67 and current parser agree when all three types are included.

Major named clusters include `systemTheme`, `paintThemeButton`, `updateToc`, `requestTocUpdate`, `openForPrint`, `restoreAfterPrint`, `printCheatSheet`; unit and numeric guards; `calcDeltaG`, `aCalc`–`hCalc`, `renderA`–`renderH`; `generateDrill`, `pgSolutionHtml`, `initProblemGenerator`; matrix/workstation/answer toggles; scrubber and playback functions; glossary/morph explorers; command palette/search; notation and Leitner recall; tests/random exam; provenance lens/concept map; lab simulation; error log; figure workbench and initializers. This is not a whitelist. Only the §JS-SUPPRESSION-REGISTRY hooks may remain.

Named function declaration inventory (178 unique names; nested names included): `systemTheme`, `paintThemeButton`, `updateToc`, `requestTocUpdate`, `openForPrint`, `restoreAfterPrint`, `printCheatSheet`, `foldNumberText`, `normalizeUnit`, `parseNumber`, `parseNum`, `convertUnit`, `readField`, `unitHint`, `fmtUnitValue`, `refreshUnitLines`, `initUnitGuards`, `validateFinite`, `validatePositive`, `validateTemperature`, `validateConcentration`, `aUnitHints`, `fmt`, `fmtSigned`, `setText`, `clearHint`, `caseInfo`, `calcDeltaG`, `aCalc`, `updateSvgA`, `mapY`, `mapX`, `requestRenderA`, `renderA`, `bCalc`, `renderB`, `generateDrill`, `checkDrill`, `cCalc`, `renderC`, `bindInputSliderC`, `setCPreset`, `dCalc`, `renderD`, `eCalc`, `renderE`, `comb`, `fCalc`, `renderF`, `almost`, `gCalc`, `gCoupleCalc`, `renderG`, `bindInputSliderG`, `hCalc`, `renderH`, `bindInputSliderH`, `setHPreset`, `selfTest`, `pgRng`, `pgRound`, `pgMake`, `pgGrade`, `pgVerdict`, `pgSolutionHtml`, `pgNumber`, `initProblemGenerator`, `writeUrl`, `render`, `updateWrapperScrollCues`, `initScrollCues`, `initScrollHints`, `toggleMatrixOcclusion`, `toggleMatrixDiff`, `sortMatrix`, `resetMatrixSort`, `toggleMatrixDelta`, `traceTempAt`, `tracePhaseNameAt`, `traceFmt`, `setTraceTime`, `toggleTraceExtrapolation`, `resetTraceScrubber`, `initTraceScrubber`, `pauseCalorimeterPlay`, `setCalorimeterPhase`, `toggleCalorimeterPlay`, `pauseGasProcessPlay`, `setGasProcessPhase`, `checkGasSign`, `toggleGasProcessPlay`, `initScrubberKeyNav`, `setWorkstationMode`, `selectPin`, `clearPartHighlight`, `assessPin`, `nextDrillPin`, `checkDrillGuess`, `resetWorkstation`, `updateWorkstationProgress`, `initOcclusionWorkstations`, `checkBoundaryAnswer`, `checkRoleAnswer`, `init`, `t`, `highlight`, `setLayout`, `initGlossarySearch`, `jumpToLetter`, `initMorphExplorer`, `show`, `hide`, `calcCalorimetry`, `calcHessCycle`, `calcNutrition`, `runThermoTestVectors`, `passed`, `foldSearchText`, `initCommandPalette`, `itemByAnchor`, `score`, `search`, `setActive`, `open`, `close`, `choose`, `openNotation`, `initNotationKey`, `initLeitnerRecall`, `saveState`, `updateStatsAndUI`, `setFilter`, `initTestSuites`, `setupSingleTest`, `mulberry32`, `shuffleWithRng`, `normalizeShortAnswer`, `initRandomExam`, `readSeed`, `selectItems`, `gradeAnswer`, `initProvLens`, `applyClasses`, `countByRole`, `initConceptMap`, `pathTo`, `walk`, `clearHighlight`, `simLinearFit`, `simModel`, `simThermogramSvg`, `X`, `Y`, `fitY`, `initLabSim`, `readInputs`, `initErrorLog`, `persist`, `addEntry`, `removeEntry`, `buildControls`, `syncLabel`, `itemMeta`, `arm`, `renderSummary`, `download`, `exportMd`, `exportJson`, `syncConsentUi`, `initFigureWorkbench`, `applyZoom`, `endDrag`, `initAllWorkstations`, `initDensityToggle`, `setFocus`, `onSchemeChange`, `onPrintChange`, `clickReveal`.

Parsed event attribute values (67 nodes, 29 unique literal strings): `PrintCSSAlchemist.printCheatSheet()`; `assessPin(...)`; `checkBoundaryAnswer(...)`; `checkGasSign(...)`; `checkRoleAnswer(...)`; `nextDrillPin(...)`; `resetMatrixSort()`; `resetTraceScrubber()`; `resetWorkstation(...)`; `setCalorimeterPhase(0..4)`; `setGasProcessPhase(0..3)`; `setWorkstationMode(...)`; `sortMatrix(...)`; `toggleCalorimeterPlay()`; `toggleGasProcessPlay()`; `toggleMatrixDelta(...)`; `toggleMatrixDiff(...)`; `toggleMatrixOcclusion(...)`; `toggleTraceExtrapolation()`; input handlers `setCalorimeterPhase(parseInt(this.value,10))` and `setGasProcessPhase(parseInt(this.value,10))`; three submit-handler attributes return false. Listener call count is 167; event types include DOMContentLoaded, beforeprint/afterprint, blur/focus, change/input/click, close/toggle, keydown, mouseenter/leave, pointer lifecycle, resize/scroll and visibilitychange. Trigger-target mapping needs a generated exact selector/listener manifest before implementation.

## [JS-MIGRATION-BLUEPRINTS] Replace runtime behavior at owner level

| Existing behavior | Preferred target | Constraint / acceptance |
|---|---|---|
| matrix hide/diff/phase/filter, workstation modes, reveal/self-checks | fieldset radio/checkbox + `:checked`, `<details>`, scoped `:has()` | keyboard and screen-reader names/states preserved; no inline handlers |
| table sorting, generated drills, exam questions, search index/UI, glossary lists | Python creates final order/index/HTML data before build | deterministic seed and reproducible output; answer keys stay separate/closed |
| `innerHTML`/`createElement` SVG and result generation | static HTML/SVG generated by Python; fixed DOM nodes only for a permitted calc | no user string interpolation into markup |
| TOC progress, scroll cues, print preparation | anchor links, CSS scroll/state features, `@media print` | no scroll-jack or event-driven geometry loop |
| modal/transient notes | `<dialog>`, `<details>`, Popover API | native keyboard path; only narrow `dialogEdge` remains if test proves needed |
| instruments A–H, lab/gas traces and autoplay | static Python-computed SVG/tables and explanatory state rows | preserve units/data vectors; no autoplay; any retained variable calculator must be `thermoCalc` |
| Leitner/mastery counters | unscored native recall and answer feedback | remove progress/streak/XP/mastery framing; do not persist without explicit consent |

## [PYTHON-CLI]

Existing and required deterministic command contracts.

Existing commands seen in source inventory: `tools/build.py`, `tools/check_budget.py`, `tools/check_css.py`, `tools/check_contrast.py`, `tools/check_terminology.py`, `tools/check_svg.py` (T19 SVG geometry/reuse/registry gate), `tools/capture_visuals.py`, `tools/migrate_tokens.py`; source owners under `build/` include `build_html.py`, `calc.py`, `search_index.py`, `figures.py`, `concept_map.py`, `data_*.py`, and figure/instrument sources.

| Required CLI | Interface and behavior | Output / failure |
|---|---|---|
| `python3 -I tools/build.py` | calculate and validate vectors, assemble master, run terminology gate; it mutates `calc.json` and HTML | report exact changed outputs; fail nonzero on any step |
| `python3 -I tools/check_budget.py [--html PATH] [--agents PATH]` | count bytes from final HTML; extract executable scripts excluding JSON; count formatted lines and events; scan forbidden runtime APIs; check file/JS/AGENTS ceilings | machine-readable `build/qa/budget.json`; nonzero for hard violations; separate warnings from failures |
| `python3 -I tools/check_css.py [--css PATH] [--html PATH]` | verify layer order, layer placement, token tiers and theme maps, orphan usage, hex scope, shadows/gradients/important, inline style count and reduced-motion/print presence | `build/qa/css-report.json`; source-level checks do not claim visual success |
| `python3 -I tools/check_contrast.py` | resolve actual computed token pairs in light/dark and calculate WCAG contrast | current script writes `build/qa/contrast_report.*`; inspect effects first; include token pair/ratio/threshold/hash |
| `python3 -I tools/check_svg.py [--self-test] [--write-registry]` | static SVG inventory from the built master (scripts stripped); unique ids and aria targets, title/desc/role, viewBox clipping with transform stack, raw-colour rejection, text-collision warnings, caption/figure-step alignment and the 43-entry owner/use registry; `--self-test` runs positive/negative/boundary fixtures | `build/qa/svg_inventory.json` + `build/qa/svg_report.txt`; nonzero for clipping/accessibility/reuse/registry failures; collisions are warnings for T13/editorial follow-up |
| `python3 -I tools/check_html.py [--html PATH]` | parse HTML; unique IDs, resolved local anchors, heading hierarchy, one h1, lang, landmarks, closed details, handlers, noscript and count parity | `build/qa/html-report.json`; nonzero on structural failure |
| `python3 -I tools/render_static.py` | render deterministic precomputed tables, search data, SVG symbol reuse and static fallback blocks | generated source fragments only; never edit final master by hand |
| `python3 -I tools/check_print.py [--html PATH]` | compare current HTML hash, PDF metadata/page count, page map and expanded answer state; must inspect any runner before use | `build/qa/print-report.json`; no screenshot claim without viewed PNG |
| `python3 -I build/calc.py` | run deterministic positive, negative and boundary calculation vectors without network | current `calc.json` is an output owner; write effects must be reviewed before invoking |

Current limitations: the tools directory exists. `check_budget.py` measures source `build/script.js`, not executable script content extracted from output, and its banned-pattern statement is stronger than its implementation. `check_css.py` covers fewer rules than its docstring contract. No `check_html.py`, `render_static.py` or `check_print.py` exists in inventory. Never run `tools/build.py` for a locked documentation-only task.

## [VERIFICATION-SUITE]

Required release gates and evidence labels.

Run each gate only when the task authorizes it and the runner’s writes are understood. Record command, exit status, exact artifact hash and generated report paths. Passing one gate does not pass another.

1. Identity/build: protected inputs and output path, bytes, mtime, SHA-256; deterministic double-build only when authorized.
2. Budget/CSS/HTML: ≤2 MiB output; executable JS limits; no inline handlers/styles or prohibited DOM APIs; CSS token/layer rules; anchors/IDs/headings/data counts.
3. Calculation/source: independent vectors and matched reaction phase, state, T, p, equation and source-page warrant; retain course convention separately from added standard values.
4. Content: five pillars per concept and topic coverage; editor review remains distinct from machine counts.
5. Behavior/accessibility: JS-on/off, keyboard, focus, storage consent/delete, 320 px targets and controls, screen-reader semantics, reduced motion.
6. Visual: falkon/falkon screenshot via workspace `webshot` instruction, capture PNG and inspect directly at specified viewport/theme states; unviewed conditions remain `[UNVERIFIED]`.
7. Print: current-hash generated PDF, page map, representative pages and expanded-answer/duplicate checks, direct visual inspection.
8. Handoff: open issues remain linked to exact current hash; `AGENTS.md` ≤24,576 B; 10-entry rolling changelog; no production change outside authorized owners.

Historical reports and saved PDFs do not satisfy these current-hash gates. `[TESTED]` means the named check actually ran; `[INSPECTED]` is a direct read/parse; `[INFERRED]` is reasoned consequence; `[UNVERIFIED]` remains open.
