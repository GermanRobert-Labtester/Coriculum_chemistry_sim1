# AGENTS.md — Chemistry_1 · Šķīdumi un ķīmiskās reakcijas

System architecture blueprint, infrastructure contract and living governance ledger for one Latvian Topic 1 study master. Read this file and `SOURCE_LEDGER.md` before work. `build/build_master.py` is the sole master writer; never hand-edit generated HTML.

Evidence tags: `[TESTED]` command/measurement ran; `[INSPECTED]` named file/page read; `[INFERRED]` reasoned; `[UNVERIFIED]` unresolved. Provenance: `[TEXT-VERIFIED]`, `[METADATA-VERIFIED / SCOPE-ALIGNED]`. Tags never imply broader acceptance than their evidence.

## 1. Goal & Architectural Philosophy

Continuously and non-destructively improve the single canonical master as a scientifically sound, teachable, accessible, navigable and reproducible resource for Latvian medical students. Priority: truth → comprehension → accessibility/design → study-loop features. HTML/CSS lead; Python performs precomputation; strict TypeScript owns only residual browser logic; raw JavaScript is a registered micro-runtime. Tier 1 content is visible without disclosure. Governance has two tiers: this executive contract plus five detailed shards.

**`[OFFLOAD-SHARD]`:** For CSS/DOM, pedagogy, layout or interaction work, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers` in full before modifying workspace files.

## 2. Workspace Topology, Offload Routing & Open Issues

| Path | Role / current evidence |
|---|---|
| `Master_temats_1_skidumi_un_kimiskas_reakcijas.html` | Canonical generated master; 1,018,215 B, mtime 2026-11-08 18:56:04 +0200, SHA-256 `037f847f78a5b30ebcd761cf2ad3875a9809b607a809850598dedb8af20d7b39` at this audit (B05). |
| `Master_temats_1_skidumi_un_kimiskas_reakcijas.N01.bak.html` | 2026-11-02 rollback; never deliver or replace without authorization. |
| `build/` | Python source, 17 chapter fragments, CSS/JS source, generated data, gates and reports. `build/build_master.py` writes the master; aggregate gates may write it/reports. |
| Five course PDFs | Read-only sources C/D/A/E/B; see §9. |
| `SOURCE_LEDGER.md` | Errata E01–E61, terminology and mistakes M01–M33; source authority for corrections. |
| `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` | Present active execution queue; 35 packages, 14-section historical plan. Its artifact metrics are stale until hash-reconciled. Do not edit under this contract. |
| `MASTER_PROMPT.md`, `TASK_PLAN_20_polish_restyle_svg.md`, `OPEN_ISSUES.md`, `T12/T15/T16/T17_REPORT.md`, `F06_REPORT.md`–`F10_REPORT.md` | Supporting records; the `T*` rows are historical, not fresh acceptance evidence; `F06_REPORT.md`–`F10_REPORT.md` are the F06–F10 feasibility/verification records. |
| `VISUAL_VERIFICATION.md` | Current screenshot protocol; follow its lite-shot Falkon order and browser restrictions. |
| `docs/governance/*.md` | Five canonical offload shards listed below. No other governance shard names. |
| Absent | `Master_Final_Perfected.md` (also absent under prior misspelling `Master_Final_Perfaced.md`), `HTML_MASTER_BUILD_PROMPT.md`, `src/ts/*.ts`, `tsconfig.json`, `pyproject.toml`, `build/check_agents_size.py`. |

| Shard | Deep payload |
|---|---|
| [Open Issues Ledger](docs/governance/OPEN_ISSUES_LEDGER.md#iss-01) | Current evidence, exact locations, defect diagnostics and remediation blueprints. |
| [Architecture/CSS/DOM](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) | Tokens, layers, DOM, pedagogy, interactions, visual/accessibility and print contracts. |
| [Python/TS/JS Audit](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#four-language-stack) | Language hierarchy, JS registry, Python CLI, TS build and verification evidence. |
| [Terminology & Sources](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) | Source authority, full term distinctions, source registry and literature leads. |
| [Changelog Archive](docs/governance/CHANGELOG_ARCHIVE.md#history-2026-11-07) | Historical milestones and closed-issue trail. |

Open issues (full evidence/fix plans at the linked anchor; do not delete to meet a size budget):

| Issue ID | Category | Location | Rule violated / gap | Target | Details shard anchor | Tag |
|---|---|---|---|---|---|---|
| ISS-01 | Governance | Root prompt files | Required forensic prompt absent; keep active roadmap, do not infer missing files. | Docs | [ISS-01](docs/governance/OPEN_ISSUES_LEDGER.md#iss-01) | [TESTED] |
| ISS-02 | Unverified | E25, E29–E32, E46–E57, E60 | High-risk chemistry/clinical claims lack full claim-level warrant. | Python/HTML | [ISS-02](docs/governance/OPEN_ISSUES_LEDGER.md#iss-02) | [UNVERIFIED] |
| ISS-03 | HTML-Defect | `build/exceptions.json` focal-point | Reference-page heuristic conflicts with hero prohibition. | Python | [ISS-03](docs/governance/OPEN_ISSUES_LEDGER.md#iss-03) | [UNVERIFIED] |
| ISS-04 | Unverified | All rendered states | Browser, keyboard, screen reader, print and screenshot acceptance not performed here. | HTML/CSS | [ISS-04](docs/governance/OPEN_ISSUES_LEDGER.md#iss-04) | [UNVERIFIED] |
| ISS-05 | Content | `pillar_map.json`, 8 thin mappings | Saved map covers 28 concepts; adequacy of thin entries remains open. | HTML/Python | [ISS-05](docs/governance/OPEN_ISSUES_LEDGER.md#iss-05) | [INSPECTED] |
| ISS-06 | HTML-Defect | 17 inline SVGs | Per-figure semantics, reuse and rendered legibility unverified. | HTML/Python | [ISS-06](docs/governance/OPEN_ISSUES_LEDGER.md#iss-06) | [UNVERIFIED] |
| ISS-07 | Infra-Gap | `check.sh`, `gate.py`, reports | Closed via T20: build separated from read-only gate, report hash-bound. | Python | [ISS-07](docs/governance/OPEN_ISSUES_LEDGER.md#iss-07) | [TESTED] |
| ISS-08 | Infra-Gap | Glossary/search | No whole-text static index. | Python/HTML | [ISS-08](docs/governance/OPEN_ISSUES_LEDGER.md#iss-08) | [INSPECTED] |
| ISS-09 | CSS-Arch | Inline stylesheet | 0 `@container`, 0 `subgrid`. | CSS | [ISS-09](docs/governance/OPEN_ISSUES_LEDGER.md#iss-09) | [TESTED] |
| ISS-10 | Infra-Gap | TS source/config | No strict TypeScript source/build contract. | TS/Python | [ISS-10](docs/governance/OPEN_ISSUES_LEDGER.md#iss-10) | [TESTED] |
| ISS-11 | Governance | §4 / JS registry | Root runtime metrics stale; live JS gate passes at 2,203 B/48 lines/3 functions. | Docs/Python | [ISS-11](docs/governance/OPEN_ISSUES_LEDGER.md#iss-11) | [TESTED] |
| ISS-12 | Infra-Gap | `build/check_agents_size.py` | AGENTS byte-budget CLI gate absent; parser/anchor gates exist. | Python | [ISS-12](docs/governance/OPEN_ISSUES_LEDGER.md#iss-12) | [INSPECTED] |
| ISS-13 | Governance | `__pycache__`, rollback | Legacy bytecode/artifacts need deliberate cleanup policy. | Python | [ISS-13](docs/governance/OPEN_ISSUES_LEDGER.md#iss-13) | [TESTED] |
| ISS-14 | Infra-Gap | Master size | F03 937,531 B (+15,931); F04 977,743; F06 998,512; F07 1,016,449 (+116,4 KB); B05 adds 1,766 B of withholding sentences → now 1,018,215 B (994,4 KiB, +118,3 KB over the 900 KiB cap). Every gate is green except `check_size.py`. The cap decision belongs to the workspace owner and is pending; the cap was not changed unilaterally. | Python/CSS | [ISS-14](docs/governance/OPEN_ISSUES_LEDGER.md#iss-14) | [TESTED] |
| ISS-15 | Source-Conflict | E01–E61, `#avoti` | Source/provenance is not fully claim-level verified. | Python/content | [ISS-15](docs/governance/OPEN_ISSUES_LEDGER.md#iss-15) | [UNVERIFIED] |
| ISS-16 | Governance | Roadmap/reports | Historical metrics conflict with current master; bind claims to artifact hash. | Docs | [ISS-16](docs/governance/OPEN_ISSUES_LEDGER.md#iss-16) | [INSPECTED] |
| ISS-18 | Content | `ch17.html` `#formulu-pienemumi` | Last hand-maintained formula copy; registry + parity gate cover it, token swap awaits build authorization. | Python/content | [ISS-18](docs/governance/OPEN_ISSUES_LEDGER.md#iss-18) | [TESTED] |
| ISS-17 | HTML-Defect | `style.css:699–702` | `svg .lbl:focus` half of the occlusion reveal rule is dead: no SVG label carries `tabindex`. | CSS/HTML | [ISS-17](docs/governance/OPEN_ISSUES_LEDGER.md#iss-17) | [TESTED] |
| ISS-19 | Content | `ch14.html`; `claims.py` clinical; `check_numbers.py` guard | Simulator rejected + lean vignette killed (no source states pKₐ′ ≈ 6,1 or any blood-gas range); guard gates it. | Python/content | [ISS-19](docs/governance/OPEN_ISSUES_LEDGER.md#iss-19) | [TESTED] |

`[TESTED]` No Git repository. Current HTML static census: one `<main id="main">`, skip link targets `#main`, 957 unique IDs, 398 `<details>`, 33 mistake cards, 61 E ids, 17 `<svg>`, 14 labelled `<fieldset>` revision days (42 checkboxes + 14 date fields), no duplicate IDs, inline style attributes or event handlers. Static census is not runtime/visual acceptance. OI-04 is closed by current DOM evidence; history at archive.

**`[OFFLOAD-SHARD]`:** When triaging product defects or reconciling historic reports, read `docs/governance/OPEN_ISSUES_LEDGER.md#iss-01` in full before modifying workspace files.

## 3. Source Authority & Conflict Resolution

Course scope authority: C → D → A → E → B. `SOURCE_LEDGER.md` governs recorded corrections; direct source locators and arithmetic/balance checks outrank memory. On conflict, show source wording and explain correction; never silently overwrite. Course content cites printed page/slide/problem. Verified outside content is labeled *papildinājums* and sourced to text read; unchecked content is `[jāpārbauda]`. Snippets, old plans and metadata do not prove a claim.

**`[OFFLOAD-SHARD]`:** For source conflicts, provenance or corrections, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log` in full before modifying workspace files.

## 4. Output Contract & Four-Language Architecture

One self-contained UTF-8 HTML file, works from `file://`, zero network requests or remote dependencies. HTML/CSS owns at least 95% of interactive/visual behavior; Python performs deterministic offline precomputation/generation/checking; TypeScript (`strict: true`, zero `any`, explicit DOM null checks) owns only residual client behavior; raw JS is compiled TS micro-runtime only.

| Tier | Language | Hard contract |
|---|---|---|
| 1 | HTML + CSS | Native `<details name>`, `<dialog>`, popover; CSS `:has()`, `:checked`, `:target`, `:focus-within`, Grid/subgrid, `@container`, `clamp()`, counters, ordered layers; zero inline `style`/`on*`. |
| 2 | Python 3 | Source extraction, tables/index/SVG generation, contrast, anchors and budgets; deterministic offline CLI; nonzero on failure with file/selector/line. |
| 3 | TypeScript | Only logic not possible in HTML/CSS or Python; no libraries; compile/minify locally. |
| 4 | JavaScript | Executable script ≤4,096 B, ≤100 lines, ≤2% of master (smallest cap); every top-level function registered; JSON blocks listed with static fallback. |

Ban DOM templating/injection (`innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `createElement` templates), data-to-HTML loops, JS UI that native markup covers, external libraries/network, scroll-jacking and decorative animation loops. Core reading/navigation/answers work with JS off.

| Current permitted hook | Ceiling | Why JS remains | JS-off behavior |
|---|---:|---|---|
| `persistMarks` | 700 B / 19 lines | Browser storage persistence. | Per-visit native marks; static score. |
| `calcConc` | 1,200 B / 19 lines | Arbitrary numeric user input. | Formula/example readable; tool hidden. |
| `printChapter` | 200 B / 6 lines | Invoke browser print dialog. | Whole document prints; button hidden. |

`python3 build/check_js_budget.py` passed on current HTML: 2,203 B / 48 lines / 3 functions / 0.217% / no banned API (the share falls as the master grows; the byte and line ceilings are unchanged). `build/js_registry.json` is the machine registry. Exact architecture, CLI and TypeScript contract: see shards.

Build and verify are separate invocations with separate proof: `build/build_master.py` writes the master; `python3 build/gate.py` (or `bash build/check.sh`) never calls it, runs every subprocess with `PYTHONDONTWRITEBYTECODE=1`, and compares a SHA-256 manifest of the whole production tree before and after the run — any write fails the gate, and the passing proof is recorded as the `readonly-integrity` step in `build/check-report.json` (schema 2.1.0), which also binds `master.sha256` and a `coverage` block so a `--fast` PASS is never mistaken for full verification (`--check-stale --require-full` refuses it).

**`[OFFLOAD-SHARD]`:** For CSS/DOM details read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#dom-component-registry`; for JS/Python/TS work read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#js-suppression` in full before modifying workspace files.

## 5. Content Standard (Five Pillars)

Every assessed concept maps Definition, Mechanism, Worked Example, Common Mistake and Canonical Term by stable ID. Explain non-applicability; never silently omit. Tier 1 is visible. Numerical reasoning includes units, balanced equation, mole conversion, coefficient ratio, limiting reagent where relevant and reasonableness check. Answers use native `<details>`. Maintain E01–E61/M01–M33 with wording, correction, reason, exact locator and evidence; do not invent values or citations.

**`[OFFLOAD-SHARD]`:** For markup and concept-to-pillar rules, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup` before modifying workspace files.

## 6. Terminology Check & High-Priority Corrections

Change terminology authority before prose; unresolved choices remain open. Core distinctions: *vielas daudzums* `n` vs mol unit; `Aᵣ` vs `M` vs `A`; *formulvienība*; *oksidēšanas pakāpe* vs charge/valence; *bāze* vs *sārms* vs *hidroksīds*; *hidratācija/solvatācija* vs *kristālhidrāts* vs *hidrolīze*; *hlorūdeņradis* gas vs *sālsskābe* aqueous; solubility state vs concentration. Use decimal comma, `L`, U+2212, charge magnitude before sign, italic quantities/upright units and formulas. Pending Latvian forms stay `[apstiprināt]`.

**`[OFFLOAD-SHARD]`:** For the complete term table and source rationale, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary` before modifying workspace files.

## 7. Design & CSS Engineering Standard

Anti-slop: no decorative gradients/glow/glass/grain/shadows/hairlines/dashed callouts, prose-fragmenting card grids, structural emoji, hero banner, drop caps, medallions, coordinate labels, decorative animation or raster filler. At most three semantic highlight colors.

| Metric | Rule |
|---|---|
| Cascade | First rule `@layer reset, tokens, base, layout, components, utilities, print;`; every CSS rule layered. |
| Tokens | Primitive `--p-*` → semantic → component `--c-*`; raw hex only in primitive tier; sizes/fonts/layout use named tokens. |
| Layout | Prose 60–75ch, target 62ch; ≤4 sentences/block; use Grid, `subgrid`, `@container`, `clamp()` with fallbacks. |
| State | Native HTML/CSS before JS; `@starting-style` only for meaningful reveals. |
| Contrast | WCAG 2.2 AA: ≥4.5:1 normal text, ≥3:1 large text/UI across supported themes and print. |
| Focus/motion | Keyboard operable, visible `:focus-visible`, `prefers-reduced-motion`; no color-only meaning. |
| Print | Expand disclosures/answers; preserve sources/equations; hide controls; no clipping; inspect PDF. |

Live CSS has 7 layers, tokens and 0 inline style attributes; it lacks `@container`/`subgrid`. This is source census, not visual or accessibility acceptance.

**`[OFFLOAD-SHARD]`:** For token definitions, component contracts and print/accessibility details, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers` before modifying workspace files.

## 8. Pedagogy Standard (Native HTML Interactive Patterns)

Teach cause before label. Calculations show units and checks. Mistakes explain plausibility, correction and verification. Retrieval answers stay in native disclosures; aim ≥30% of key concepts. Use `<details>`, popover, `<dialog>`, labeled input + `:has()` filters and CSS progress counters. Every aid has a static explanation usable offline/JS-off. Medical material is supplementary, never individualized guidance, and requires current primary sourcing. No retexture while a truth defect remains open.

**`[OFFLOAD-SHARD]`:** Before changing an interactive or pedagogical component, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns` in full.

## 9. Sourcing & Provenance Rules

Course sources C/D/A/E/B are scope-aligned metadata; claim text was not re-extracted in this run. B filename says 2025 while footer says 2021; cite file as received without claiming a year. Prior records mark BIPM SI Brochure and CIAAW atomic weights `[TEXT-VERIFIED]`; Gold Book entries remain `[UNVERIFIED]` after HTTP 403. Do not extend these statuses to unreviewed claims. External citations record title, author/body, edition/version, publisher/date, exact URL and supported claim.

**`[OFFLOAD-SHARD]`:** For source files, terminology conflicts and verification limits, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry` in full.

## 10. Python/TS Infrastructure, Features & Literature

Existing Python owns build, extraction, SVG, static tables, ledger and gates. `check_js_budget.py` is present and passed; `check_agents_size.py` is absent. `src/ts/`, `tsconfig.json`, `pyproject.toml` are absent. Whole-text search/static index is not present. Features follow HTML/CSS → Python → strict TS → registered JS. Outside literature only corrects, clarifies or fills a course gap; label *papildinājums* and keep research outside the output.

**`[OFFLOAD-SHARD]`:** For CLI, compiler, migration and test boundaries read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli` and `#verification-suite`; for outside sources read `docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026` before modifying workspace files.

## 11. Editing, Non-Regression & Byte Budget

Under a governance-only lock, edit only `AGENTS.md` and the five named `docs/governance/*.md` files; do not build, alter HTML/Python/TS/roadmap/sources or commit. Implementation changes edit source then regenerate only with authorization. Inspect runners before execution; preserve PDFs read-only; evidence scratch stays outside deliverables. Do not weaken standards or delete open issues to fit bytes. `AGENTS.md` ceiling 24,576 B; target 14,336–20,480 B. Changelog keeps the latest 10 run rows, older detail lives in archive.

| Date | Sections / shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-08 | §§2,4,5,7,11,12 + F03–F10 | F-series feature wave (F03–F10): each feature decided by its own kill criterion and mutation-verified gate. | Additive features adopted only on evidence; rejected/deferred stay specified. | Masters 937,531 B `1d6f2b4a…` → 1,016,449 B `55ebbd2d…`; fast gate 23/24 (only `check_size`, ISS-14). Full per-feature evidence: `docs/governance/CHANGELOG_ARCHIVE.md#history-2026-11-08`. |
| 2026-11-08 | §§4,11,12 + B01 | B01 inline-style defect verified closed: 0 `style=` attributes in the master, in `build/content/*.html` and in every literal of the 15 builder-side emitter modules; 23 captions carry `.tcap`. `check_html.py` hardened (`EMITTERS` = the builder's whole import graph, f-string literals scanned, self-test). | T16 removed the declarations, but the gate meant to catch their return had two holes. | Master unchanged; byte-identical rebuild; PASS; 5/5 mutations caught; fast gate 23/24 (only `check_size`). Detail: `CHANGELOG_ARCHIVE#history-2026-11-08-b`. |
| 2026-11-08 | §§4,11,12 + B02 | B02 runtime-HTML-templating defect verified closed and its gate rewired: `build/assets/app.js` is 2,499 B / 52 lines writing `textContent` only into 4 pre-rendered `<output>` nodes; the scrubber is 11 Python-rendered `<details class="phase">`, no JSON payload, no script. `check_js_budget.py` now scans the source too; the transform lives in `js_inventory.shipped_transform()`. | T15 removed the templating, but B02's named instrument („banned API scan”) was wired to the artifact only — the source could rot behind a passing master. | Master unchanged; self-test positive + 7 negative; 5/5 mutations; `check_wiring.py --runtime` 32/32; fast gate 23/24 (only `check_size`). Detail: `CHANGELOG_ARCHIVE#history-2026-11-08-b`. |
| 2026-11-08 | §§2,11,12 + B03 | B03 skip/title/print defects confirmed already resolved — no source edit, no rebuild, no byte moved: skip link → `#main` + `<main id="main">`; plain title masthead (T17, no dark band); print `.mist` solid, no `dashed`. Roadmap locators are a pre-T17 snapshot. | The named P0 defects no longer exist, so the action was investigation + gate proof, not a rebuild; each defect is gate-enforced. | Master unchanged 1,016,449 B / `55ebbd2d…`, byte-identical rebuild; Falkon plain-title capture inspected (Falkon blank `[UNVERIFIED]`); fast gate 23/24 (only `check_size`, ISS-14). Detail: `CHANGELOG_ARCHIVE#history-2026-11-08-b`. |
| 2026-11-08 | §§2,4,11,12 + B04 | Quality-gate write side effects isolated: the roadmap's `check.sh` locators are a pre-T20 snapshot; `def_first_use.json` was rewritten per verify, 17 `.pyc` created per run, and immutability was proven only on failure. Closed with bytecode suppression, scratch-routed diagnostics and a tree-wide manifest recorded as a PASSING `readonly-integrity` step. | The T20 fix asserted only the master hash, and only on failure, so „nothing was mutated” was never proven. | 917 files unchanged (0 written, 0 bytecode); `test_gate_runner.py` 6/6; `test_b04_readonly.py` 10/10. Detail: `B04_REPORT.md`; `CHANGELOG_ARCHIVE#history-2026-11-08-b`. |
| 2026-11-08 | §§2,11,12 + B05 | B05 high-risk claims crushed: course PDFs re-extracted page by page (37 passages, 3 sources); `claim_crush.py` lists 19 numbers with locator, verbatim passage and warrant class; `recompute()` re-derives 13; gate `check_claim_crush.py`. Fixed E46's locator (`A p.13`→`A p.13, p.14`) and five unmarked re-shipments of the unwarranted 37 °C neutral-pH figure (quiz, answer key, M19, M20, glossary, which mis-sourced it to `E s.56`). No number upgraded to verified. | The gate checked only the registry's curated `surfaces`; copies in quizzes, answer keys, mistake cards and the glossary were invisible. | 1,016,449 B `55ebbd2d…` → 1,018,215 B `037f847f…`; `claim-crush` PASS (37/37, 13 recomputations, 19 tokens, 5/5 mutations); `test_b05_claim_crush.py` 22+13; fast gate 22/26, 1 FAIL (`check_size`). Detail: `B05_REPORT.md`, `CHANGELOG_ARCHIVE#history-2026-11-08-b`. |

**`[OFFLOAD-SHARD]`:** For complete historical entries and closure evidence, read `docs/governance/CHANGELOG_ARCHIVE.md#history-2026-11-07` before modifying workspace files.

## 12. Done Definition & Verification Boundaries

Automated checks must exit 0 for their stated scope. Completion separately requires: generated master hash/size/mtime recorded; authorized file set only; source and terminology review; five-pillar mapping; script/registry and JS-off checks; WCAG contrast/focus/keyboard/reduced-motion/names/screen reader; responsive screenshots directly inspected; print PDF inspected; claim-level provenance; exact open issues. Static lint, saved reports, and this documentation update do not establish browser, visual, scientific, screen-reader or print acceptance.

Current run (B05): `[TESTED]` master rebuilt 1,016,449 B `55ebbd2d…` → 1,018,215 B `037f847f…` (+1,766 B, 18 intended block groups); an isolated rebuild reproduced `037f847f…` byte-for-byte and the pre-change sources reproduced `55ebbd2d…`, so the delta is attributable to the listed edits. `[TESTED]` page-scoped `pdftotext -layout -f P -l P` over the five course PDFs: 37/37 passages sit on their recorded pages — how E46's locator was found wrong (propane/ethanol are on A p.14). `[TESTED]` `claim-crush` PASS: 13 recomputations (½pKw=6,81; implied ΔH_ion 56,1 kJ/mol; 2043+4·44≈2220; 1235+3·44=1367; E°(Zn|Cu)=1,10 V), 19 tokens swept, 5/5 mutations. `[TESTED]` fast gate 22/26 PASS, 1 FAIL (`check_size`, ISS-14), 3 UNVERIFIED; `readonly-integrity` PASS: every production file unchanged, 0 written, 0 bytecode. `[TESTED]` B05 tests 22+13 subtests; b04 10/10. `[UNVERIFIED]` screenshot/print/SR acceptance and every primary table: no claim upgraded. Detail: `B05_REPORT.md`.

**`[OFFLOAD-SHARD]`:** For the CLI matrix and evidence limits, read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite` before modifying workspace files.
