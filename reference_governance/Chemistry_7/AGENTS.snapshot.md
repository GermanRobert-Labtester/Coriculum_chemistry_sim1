# AGENTS.md — Chemistry_7: absorbcijas spektrofotometrija, Lab 6B

Authoritative system architecture, infrastructure contract and governance ledger for the existing Latvian master. Maintenance workspace; do not rebuild from zero. One canonical output: `Master_spektrofotometrija_SEM7_LD6B.html`, assembled from 18 `src/*.part` files and `tools/`. Governance map: `docs/governance/`. Last reconciled: 2026-11-12. Hard size ceiling: 24,576 B; target 14,336–20,480 B. State rules once and route details by stable shard anchor.

## 1. Goal & Architectural Philosophy

Continuously improve the canonical master and deterministic offline build without rebuilding from zero. Preserve 16 chapters, corrections, evidence labels, errata, figures and print scaffolding. Teach students to explain spectrophotometry, perform Lab 6B, calculate results and avoid errors. HTML/CSS first; Python precomputes; strict TypeScript handles unavoidable residual logic; suppress raw JS. Keep source errors traceable and evidence states distinct.

**[OFFLOAD-SHARD]:** When changing architecture, component or pedagogy standards, read [`ARCH_CSS_DOM_CONTRACTS.md`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md) in full before modifying workspace files.

## 2. Workspace Topology, Offload Routing & Open Issues Index

| Role | Current workspace inventory |
|---|---|
| Canonical output | `Master_spektrofotometrija_SEM7_LD6B.html` (313,828 B at audit start; sole root master) |
| Inputs | 18 `src/*.part`; `run.sh` (mutating build runner) |
| Python | `tools/data.py`, `build.py`, `verify.py`, `behaviour.py`, `figures.py`, `lint_html.py`, `gate_css_arch.py`, `coverage.py`, `budget.py`, `numbers_trace.py` |
| TS config/source | `src/ts/*.ts` (J1–J5), `tsconfig.json`; pinned tsc 7.0.2 via `tools/compile_ts.mjs` (T15) |
| Sources | `7_SEM_Optika_analize_2025.pdf`; `LD_Spektrofotometrija_Paraugs.pdf`; `Absorbcija_LD_2022.docx` |
| Plans/evidence | `plan/`; historical evidence, not fresh acceptance |
| Governance vault | Five canonical files under `docs/governance/` (details below) |
| Reference-only | `workspace_skills/`, `PROMPT_master_html.md`, `.claude/`, `.gitignore`; `artifacts/screenshots/` (git-ignored capture area per the visual contract) |

`Chemistry_7th_2nd_round__MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` (base, 2026-11-06) and its `Tasks-`-prefixed expansion (v2.0, 2026-11-09) are proposal queues, not authorization; `plan/DEEP_INSPECTION_TASKBOOK_2026.md` and `plan/ROADMAP_T21-T40_AND_FEATURE_BACKLOG.md` are historical second-wave planning (2026-11-02; superseded by `plan/execution-log.md`). `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` are absent; `PROMPT_master_html.md` is distinct and reference-only. No Git repository detected. Do not create substitutes or edit roadmaps/prompts/taskbooks under this lock.

| Topic | Canonical detail shard |
|---|---|
| Open issue forensics | [`OPEN_ISSUES_LEDGER.md`](docs/governance/OPEN_ISSUES_LEDGER.md#scope-and-closure-rule) |
| CSS, DOM, five pillars, pedagogy | [`ARCH_CSS_DOM_CONTRACTS.md`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) |
| Python/TS/JS audit and gates | [`INFRA_PYTHON_TS_JS_AUDIT.md`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#four-language-stack) |
| Terminology, source conflicts and provenance | [`TERMINOLOGY_AND_SOURCES.md`](docs/governance/TERMINOLOGY_AND_SOURCES.md#source-authority) |
| Historical changelog | [`CHANGELOG_ARCHIVE.md`](docs/governance/CHANGELOG_ARCHIVE.md#archive-policy) |

Keep issues open until source, rebuilt output and a failing check agree; visual/accessibility/source review must also pass where relevant. Never weaken a rule to match a defect. Detailed forensic fixes live in the linked ledger.
| ID | Category | Location | Rule violated / one-line issue | Target | Detail | Tag |
|---|---|---|---|---|---|---|
| OI-01 | HTML | `#n10-7`, E18 | Residuals imply linearity | HTML+Py | [ISS-001](docs/governance/OPEN_ISSUES_LEDGER.md#iss-001) | `[INSPECTED]` |
| OI-02 | HTML | `#n5-3`, E19 | R²/intercept treated as validation | HTML | [ISS-002](docs/governance/OPEN_ISSUES_LEDGER.md#iss-002) | `[INSPECTED]` |
| OI-03 | HTML | `#n10-1`, E20 | 440 nm inference labelled source | HTML | [ISS-003](docs/governance/OPEN_ISSUES_LEDGER.md#iss-003) | `[INSPECTED]` |
| OI-04 | Unverified | `#n0`–`#n15` | Claim labels not audited | Py+HTML | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) | `[INSPECTED]` |
| OI-05 | Source conflict | `#n10-4`, `data.py` | Fit point count/blank conflicts | Py+HTML | [ISS-005](docs/governance/OPEN_ISSUES_LEDGER.md#iss-005) | `[INSPECTED]` |
| OI-06 | CSS | masthead | No forced-colors; contrast incomplete | CSS+Py | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) | `[INSPECTED]` |
| OI-07 | Unverified | `#n0`–`#n15` | No five-pillar concept map | Py+HTML | [ISS-007](docs/governance/OPEN_ISSUES_LEDGER.md#iss-007) | `[UNVERIFIED]` |
| OI-08 | Unverified | `#n15-d` | Claim-source ledger absent | Py+HTML | [ISS-008](docs/governance/OPEN_ISSUES_LEDGER.md#iss-008) | `[INSPECTED]` |
| OI-09 | Unverified | `#n15-src` | `skolo.lv` scope unchecked | HTML | [ISS-009](docs/governance/OPEN_ISSUES_LEDGER.md#iss-009) | `[UNVERIFIED]` |
| OI-10 | Unverified | SVGs/print | Closed 2026-11-12 (T17): current render verified | CSS+HTML | [ISS-010](docs/governance/OPEN_ISSUES_LEDGER.md#iss-010) | `[SCREENSHOT-VERIFIED]` |
| OI-11 | Unverified | `#n12-4` | “kivete” status: queries run 2026-11-09 (Tēzaurs, AkadTerm); drift lint live | HTML | [ISS-011](docs/governance/OPEN_ISSUES_LEDGER.md#iss-011) | `[INSPECTED]` |
| OI-12 | Governance | root | Roadmap present; named spec/prompt absent | Markdown | [ISS-012](docs/governance/OPEN_ISSUES_LEDGER.md#iss-012) | `[TESTED]` |
| OI-13 | JS-Bloat | script | 7,890 B/162 lines/2.514%; cap 4,096 B | TS+Py | [ISS-013](docs/governance/OPEN_ISSUES_LEDGER.md#iss-013) | `[TESTED]` |
| OI-14 | JS-Bloat | theme block | Theme duplicates CSS state | CSS+HTML | [ISS-014](docs/governance/OPEN_ISSUES_LEDGER.md#iss-014) | `[TESTED]` |
| OI-15 | JS-Bloat | recall block | Masks use JS DOM state | CSS+HTML | [ISS-015](docs/governance/OPEN_ISSUES_LEDGER.md#iss-015) | `[INSPECTED]` |
| OI-16 | JS-Bloat | print block | Handler mutates disclosures | CSS+HTML | [ISS-016](docs/governance/OPEN_ISSUES_LEDGER.md#iss-016) | `[INSPECTED]` |
| OI-17 | JS-Bloat | three calculators | Blocks exceed J2–J4 budgets | TS+Py | [ISS-017](docs/governance/OPEN_ISSUES_LEDGER.md#iss-017) | `[TESTED]` |
| OI-18 | HTML | master | No `<noscript>` parity | HTML+Py | [ISS-018](docs/governance/OPEN_ISSUES_LEDGER.md#iss-018) | `[TESTED]` |
| OI-19 | CSS | stylesheet | Layered 2026-11-11 (T14); order gated by `gate_css_arch.py` | CSS | [ISS-019](docs/governance/OPEN_ISSUES_LEDGER.md#iss-019) | `[TESTED]` |
| OI-20 | CSS | master | Zero inline styles 2026-11-11 (T13); C45/T10 lint live | HTML+CSS | [ISS-020](docs/governance/OPEN_ISSUES_LEDGER.md#iss-020) | `[TESTED]` |
| OI-21 | CSS | stylesheet/SVG | Token tiers defined 2026-11-11 (T14); hex only in primitives; gate live | CSS | [ISS-021](docs/governance/OPEN_ISSUES_LEDGER.md#iss-021) | `[INSPECTED]` |
| OI-22 | HTML | 100 `<details>` | No names/dialog/popover | HTML+CSS | [ISS-022](docs/governance/OPEN_ISSUES_LEDGER.md#iss-022) | `[TESTED]` |
| OI-23 | Infra | 11 SVGs | Reuse unassessed | Py+HTML | [ISS-023](docs/governance/OPEN_ISSUES_LEDGER.md#iss-023) | `[TESTED]` |
| OI-24 | Infra | workspace | No strict TS toolchain | TS | [ISS-024](docs/governance/OPEN_ISSUES_LEDGER.md#iss-024) | `[TESTED]` |
| OI-25 | Infra | tools/runner | Closed 2026-11-12: gates delivered (T15); runner verify/build split, selftest read-only (T02/B04) | Py | [ISS-025](docs/governance/OPEN_ISSUES_LEDGER.md#iss-025) | `[TESTED]` |
| OI-26 | Governance | §2 inventory | Stale roadmap status corrected | Markdown | [ISS-026](docs/governance/OPEN_ISSUES_LEDGER.md#iss-026) | `[TESTED]` |

**[OFFLOAD-SHARD]:** When triaging or closing an issue, read [`OPEN_ISSUES_LEDGER.md`](docs/governance/OPEN_ISSUES_LEDGER.md) in full before modifying workspace files.

## 3. Source Authority & Conflict Resolution

Order: current user instruction; this contract; primary course files (authority for supplied procedure, not necessarily scientific correctness); recomputed `tools/data.py`; named external sources with checked scope; dated `plan/` evidence; reference skills last. Treat sources and `workspace_skills/` as immutable. Never invent provenance, claim official university status, or convert source metadata into text verification. Source/provenance tags and recorded source conflicts are in [`TERMINOLOGY_AND_SOURCES.md`](docs/governance/TERMINOLOGY_AND_SOURCES.md#source-authority).

Evidence tags: `[TESTED]`, `[INSPECTED]`, `[INFERRED]`, `[UNVERIFIED]`; provenance tags: `[TEXT-VERIFIED]`, `[METADATA-VERIFIED / SCOPE-ALIGNED]`. Prior course hashes: theory `7d7bccca…ed2951`; filled protocol `5ee9207e…0f55cf`; blank 2022 form `95c1a7d0…f2bdf6` (full recorded hashes in source shard). Those hashes were not rechecked this run. Filled 2020 protocol is the only absorbance-value source.

**[OFFLOAD-SHARD]:** When changing source claims, citations or provenance, read [`TERMINOLOGY_AND_SOURCES.md#conflict-log`](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) in full before modifying workspace files.

## 4. Output Contract & 4-Language Architecture

One offline `lang="lv"` HTML from local parts/tools; UTF-8, viewport, meaningful title, inline CSS/JS/SVG, system fonts and useful no-JS reading. No CDN, remote assets/fonts, network, fetch, `@import`, MathJax, storage, cookies, eval or persisted theme. DOI/ISBN/URL strings are plain text.

| Tier | Language | Standing rule |
|---|---|---|
| 1 | Semantic HTML + CSS | Target ≥95% UI behavior; native `<details name>`, `<dialog>`, Popover API and CSS state/layout; no JS for UI state CSS/HTML can provide |
| 2 | Python 3 (`python3 -I -B`) | Precompute extraction, calculations, tables, SVG coordinates, contrast, anchors, lint and budgets; nothing at runtime |
| 3 | TypeScript | Only residual logic impossible in tiers 1–2; `strict: true`, zero `any`, explicit DOM null checks, compiled/minified |
| 4 | JavaScript | Compiled Tier-3 micro-runtime only, registry-listed and budgeted; never primary architecture |

`[JS-SUPPRESSION]`: executable inline script ≤min(6,096 B, 100 lines, 2% HTML); zero inline handlers; handler ≤60 lines; zero DOM templating/injection (`innerHTML`, `outerHTML`, `insertAdjacent*`, `document.write`, templating `createElement`), data-array HTML hydration, JS UI state, scroll-jacking, decorative animation loops or external libraries. Four instruments maximum, ≤3 JS-driven, no fifth widget. (Owner K6 ruling 2026-11-12: byte ceiling 4,096→6,096 B; lines and share unchanged; J3/J4 caps ratified 1,400 B, floors 1,316/1,355. Owner K7 ruling 2026-11-12 (T04/B01): J3 cap 1,500 B, floor 1,453.)

| Registry | Budget | Why CSS/HTML + Python cannot do it | JS-off fallback |
|---|---:|---|---|
| J1 `fmt` decimal comma | 150 B/4 lines | Shared residual formatter | n/a |
| J2 explorer `upd` | 1,100 B/28 | Continuous γ/l inputs → A/T/%T | Python fixed-point table |
| J3 dilution `upd` | 1,500 B/22 (K7) | User V1/Vtot → C1V1=C2V2 | Static worked example |
| J4 quality `upd` | 1,400 B/32 (K6) | User A/digits → T/uncertainty | Static table |
| J5 `init` | 200 B/8 | Binds J2–J4 | n/a |

Full CSS, DOM and pedagogy contracts: [`ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers). Full TS, Python, registry, migration and CLI contract: [`INFRA_PYTHON_TS_JS_AUDIT.md#js-suppression`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#js-suppression).

**[OFFLOAD-SHARD]:** When changing output, CSS, JS or tools, read [`ARCH_CSS_DOM_CONTRACTS.md`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md) and [`INFRA_PYTHON_TS_JS_AUDIT.md`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md) in full before modifying workspace files.

## 5. Content Standard (5 Pillars)

Every key concept needs applicable Definition, Mechanism, Worked Example, Common Mistakes, and Canonical Term evidence; log exceptions. Keep 16 chapters, Planck/Einstein, `ΔE=hν=hc/λ`, λmax and bands vs lines, UV/VIS, `A=lg(I₀/I)`, calibration curve, Fe³⁺/SCN⁻, Q1–Q9 answers, graph exercise, six-step frame and eight-point checklist. Lab 6B: 440 nm, stock γ=0.0400 mg/mL, standards to 10.00 mL, filled protocol only for absorbances, path unstated (1 cm is assumption), unknowns 2–5, no extra dilution, e-studies video absent/uninspected. See the five-pillar markup map in [`ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup).

**[OFFLOAD-SHARD]:** When editing teaching content or interactive markup, read [`ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup) in full before modifying workspace files.

## 6. Terminology Check & High-Priority Corrections

| Canonical rule | Avoid / status |
|---|---|
| absorbance A; transmittance T=I/I₀; A=−lg T; decadic `lg` | Do not use “absorbcija” as unqualified quantity, unverified “caurlaidība”, or `ln` |
| Bugēra–Lamberta–Bēra law; ε in L·mol⁻¹·cm⁻¹; mass absorptivity `a` in L·g⁻¹·cm⁻¹ | Keep course errors in errata; do not conflate coefficients |
| optical path `l`; `c` mol/L; `γ` mg/mL; dilution distinct from dissolution | State assumed path; avoid generic C or γ as density |
| kivete; absorption band; standards; blank vs zeroing | “kivete” remains house choice pending lexical check; define ambiguous terms |

Full dictionary, search guidance and conflict log: [`TERMINOLOGY_AND_SOURCES.md#terminology-dictionary`](docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary).

**[OFFLOAD-SHARD]:** When changing Latvian terminology, read [`TERMINOLOGY_AND_SOURCES.md#terminology-dictionary`](docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary) in full before modifying workspace files.

## 7. Design & CSS Engineering Standard

Require `@layer reset, tokens, base, layout, components, utilities, print`; primitive→semantic→component tokens; zero inline styles; body measure 60–75ch; WCAG 2.2 AA contrast; visible focus, keyboard operation, reduced-motion and forced-colors. Print expands disclosures without JS, white background, readable tables/figures, ≥9 pt text, page budget 100 (G-17 owner ruling 2026-11-12; >100 needs a new owner decision). CSS source presence is not visual evidence.

Current visual contract: `lite-shot` Falkon first; inspect PNG directly. Chrome/Chromium is prohibited unless user explicitly permits it in the current turn. Print requires rendered output and page-by-page inspection. Visual/render status stays `[UNVERIFIED]` in this run.

**[OFFLOAD-SHARD]:** When changing CSS, design or print, read [`ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) in full before modifying workspace files.

## 8. Pedagogy Standard (Native HTML Interactive Patterns)

Teach mechanism → rule → number → mistake. Use `<details>/<summary>` for answers and reveals, `name` only for exclusive sets, native dialog for necessary modals, Popover API for suitable footnotes, CSS state first. Reading/navigation require no JS; label fallbacks for every residual tool. R² never validates alone: discuss residuals, intercept, range and blank. Preserve study routes and 3–5 retrieval prompts/chapter. See [`ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns).

**[OFFLOAD-SHARD]:** When changing pedagogy or native interactions, read [`ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns`](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns) in full before modifying workspace files.

## 9. Sourcing & Provenance Rules

Label each claim-bearing statement; separate source fact, calculation, external addition and unverified statement. Keep source identity and scope distinct from page-level text verification. No invented references, page numbers or quotations. Source inventory, historical hashes and named literature/status are in [`TERMINOLOGY_AND_SOURCES.md#verified-source-registry`](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry); 2026 literature/source leads are in [`TERMINOLOGY_AND_SOURCES.md#literature-2026`](docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026).

**[OFFLOAD-SHARD]:** When adding or revising claims/citations, read [`TERMINOLOGY_AND_SOURCES.md#verified-source-registry`](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry) in full before modifying workspace files.

## 10. Python/TS Infrastructure, New Features & Literature

Truth repair precedes features. Sequence: (1) reduce JS to registry, (2) add budget/lint + strict TS toolchain, (3) layer CSS/remove inline styles and assess native semantics, (4) repair content/source conflicts, (5) only then consider bounded features. Python computes anything possible before open; strict TS is for residual logic. Do not add network/storage, fifth widget, unregistered JS or unsupported claims. Full Python CLI and verification requirements: [`INFRA_PYTHON_TS_JS_AUDIT.md#python-cli`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli); source status: [`TERMINOLOGY_AND_SOURCES.md#literature-2026`](docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026).

**[OFFLOAD-SHARD]:** When changing infrastructure or evaluating literature, read [`INFRA_PYTHON_TS_JS_AUDIT.md#python-cli`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli) and [`TERMINOLOGY_AND_SOURCES.md#literature-2026`](docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026) in full before modifying workspace files.

## 11. Editing, Non-Regression & Byte-Budget Rules

Governance-only task: edit only authorized governance Markdown. Product task: edit source parts/tools, then rebuild only if authorized. Inspect any runner for side effects first; `run.sh` rewrites HTML and plan outputs. Commands not run are not PASS. Reconcile calculations to `data.py` and protocol; record decisions and hashes in normal product workflow. Keep ten newest dated entries here, archive older ones to [`CHANGELOG_ARCHIVE.md`](docs/governance/CHANGELOG_ARCHIVE.md#archived-entries). Master HTML budget: target ≤400 KiB (owner ruling 2026-11-13, T11: bench card + pending freeze consumers T13/T16; raised from ≤336 KiB, T09 2026-11-10), cap 600 KiB; print budget 100 pages per owner ruling G-17 (2026-11-12; §7). This AGENTS file ≤24,576 B.

| Date | Section(s)/shards | Governance change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-12 | tools/{reference_graph.py new,asset-classification.md new,negative-fixtures.json,README}; run.sh (step v6c); plan/{t05-reference-graph.json,t05-evidence.md} new; OPEN_ISSUES (OI-23 note); CHANGELOG_ARCHIVE (T02 row archived) | Recorded T05/B02 (dead-code/orphaned-asset investigation): stdlib reference graph over 18 src parts — ids/classes/fragments/aria IDREFs/attribute+CSS url(#)/<use>/asset paths/CSS selector tokens/JS-referenced ids, build-time consumers incl. plan/*.csv generation inputs; 223 ids, 115 classes, 13 SVGs, 4 instruments, 0 asset paths; classification: all live or build-only-protected — 17 zero-consumer subsection anchors are DOM-taxonomy-mandated, fig-T/res-origin/fit-origin rendered+registered, fit-free/#res-free the hidden dormant free-regression variant (figures.md V11/V12 [REDESIGN], data-reconciled T10) → zero unreachable, removal diff empty by design (size-decrease DoD vacuous); guard gate --gate (fragments/IDREF/url/use/JS ids/assets/dup ids/src→master parity) wired read-only as run.sh v6c; --selftest 7/7, each broken class asserted to fail with its own reason; url()-in-attributes gate blindness found and fixed during ST5.3 | Classification beats guessing; contract-mandated anchors and registered teaching variants are not dead code | [TESTED] selftest 7/7; gate 0 problems on built master; run.sh build byte-identical 340,674 B `f0344a56…`; combined T04+T05 verify --strict exit 0 (51/51, 0 SKIP); no markup/content change → no new visual state; instructor review [UNVERIFIED] |
| 2026-11-12 | src/15; plan/execution-log.md; CHANGELOG_ARCHIVE (T03/B05 row archived); plan/visual-allow.token | Recorded F09 formula-sheet composer (owner card): rejected, lean alternative applied — no composer, no selection JS, no second composition state; card's `#print-answers`/`build_master.py` anchors absent here (builder = tools/build.py); audit: stable formula appendix already exists as ch. 14 `#n14` (8 formulas, constants, conversions, A/%T table, workflow, mistakes; constants reconcile to data.py; same formulas recur in ch. 2/5/6/7/9/10 — composer would duplicate); gap closed in src/15: `#n14` lede gained a procedural print instruction (find the chapter in print preview, enter its page range; footer «n / N») and "Viena lapa"→"Īsa lapa" after render showed the appendix spanning pp. 61–62; roadmap F09 IDs unrelated | Composer would create a second hand-maintained formula source (kill criterion); page-range workflow serves print personalization | `[TESTED]` owner-authorized build + Chrome print fallback (logged): `./run.sh all --strict` exit 0 (51/51, 0 SKIP); master 340,886 B `2ffd82d2…` (+212 B, payload byte-identical `96fd61b8…`); falkon light `#n14` capture + Chrome print pp 61–62 inspected `[SCREENSHOT-VERIFIED]`; instructor review `[UNVERIFIED]` |
| 2026-11-12 | src/00; ARCH shard; plan/execution-log.md; CHANGELOG_ARCHIVE (T04/B01 row archived) | Recorded T06/F09 route selector (lean: no tab state, route memory, chapter hiding or separate interface): `.routes` re-housed from a TOC-nav div into own `<nav class="routes" aria-label="Mācību ceļi">` with three ordered `<ol>` (n5→n6→n8→n10→r10; n14→n7→n11→n13; r10-graph→n10-7→n10-8→n12-7+"Pārbaudiet sevi"); mapping + rejection rationale in a src/00 comment; print-visible per ST6.2.2 (owner hybrid ruling supersedes the T11 screen-only detail; T11 route names kept, data anchors added); layout-layer CSS, coarse-pointer ≥44 px rows | Lean links are the feature; anchors must resolve and routes must survive print and no-JS | `[TESTED]` owner-authorized `./run.sh all --strict` exit 0 (51/51, 0 SKIP); master 342,007 B `2b2ebdfc…` (+1,121 B), payload `e219b622…` byte-identical (no runtime change); falkon light/dark/no-JS 1280+390, Chrome 390 `.routes` element shot, print p. 1/66 inspected `[SCREENSHOT-VERIFIED]`; Chrome keyboard probe: Tab nav→content, Enter→#n5, no trap (Chrome logged); AT/instructor review `[UNVERIFIED]` |

**[OFFLOAD-SHARD]:** When changing governance history, read [`CHANGELOG_ARCHIVE.md`](docs/governance/CHANGELOG_ARCHIVE.md) in full before modifying workspace files.

## 12. Done Definition (Automated and Manual Verification)

1. Single offline Latvian master; inputs/source files unchanged where locked; build check passes.
2. Five pillars reviewed; corrections trace to errata; fit variants named; values reconcile to calculation authority and filled protocol.
3. Claims and citations are scoped and labelled; no invented evidence.
4. Strict run has zero FAIL/SKIP; budget and HTML lint enforce JS registry/limits, banned APIs, zero style attributes, layers, fallbacks, headings, scopes, SVG names, anchors and size ceilings.
5. Keyboard, no-JS, contrast in all states, reduced motion, forced colors, responsive widths/zoom and print are verified; visual proof uses direct inspected captures, print all pages inspected.
6. Issues are either still open with evidence or closed only with required product and human/visual proof.
7. Report separates `[TESTED]`, `[INSPECTED]`, `[INFERRED]`, `[UNVERIFIED]`, `[TEXT-VERIFIED]`, and `[METADATA-VERIFIED / SCOPE-ALIGNED]`.

Verification command and fixture contract: [`INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite). Governance shard link anchors and current tool inventory are checked separately; governance-only success does not imply product acceptance.

**[OFFLOAD-SHARD]:** When changing release gates or acceptance evidence, read [`INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite`](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite) in full before modifying workspace files.
