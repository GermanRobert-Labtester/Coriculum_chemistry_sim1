# AGENTS.md — Chemistry_4 (Medicīniskā ķīmija, 4. tēma)

Living architecture blueprint and governance ledger for the single generated Latvian master `Master_4_temats_termodinamika.html`. Governance root is this file plus five canonical shards in `docs/governance/`; roadmap remains the execution queue. Reconciled: 2026-11-07. Hard ceiling: 24,576 B; target: 14,336–20,480 B. Keep all medium/high-detail contracts in shards; do not duplicate deep specifications here.

## 1. Goal & Architectural Philosophy

Continuously improve one self-contained, offline study document for RSU Medicīniskā ķīmija Topic 4 «Termodinamika un tās piemēri bioloģiskajās sistēmās» (first-year medical student; assessment ≥55%; neutralisation calorimetry). The canonical HTML is generated from owners under `build/`; never hand-edit it or create a parallel master. HTML/CSS carry ≥95% of visual/interactive behavior; Python precomputes deterministic work; strict TypeScript owns only unavoidable residual browser logic; raw JS is a registered micro-runtime. Audit output, owner sources, provenance and current-hash evidence before production changes.

**[OFFLOAD-SHARD]:** When changing CSS/DOM, pedagogy or runtime, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers` and `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#four-language-stack` in full first.

## 2. Relationship to Other Files, `docs/governance/` Offload Routing Matrix & Open Issues Index

| Path | Role |
|---|---|
| `Master_4_temats_termodinamika.html` | sole generated output; protected unless implementation is authorized |
| `build/` | canonical HTML/CSS/JS fragments, data, Python generator/calculations/figures/search owners |
| `tools/` | partial Python build, budget, CSS, contrast, terminology and visual CLIs |
| `ts/` | target strict TypeScript source; currently absent |
| `build/qa/`, `scratch/` | probes/reports/output; inspect write effects before running tools |
| root PDFs, `workspace_skills/` | protected course sources and convention exemplar/skill sources |
| `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` | planning/execution queue; do not copy into this architecture contract |
| `docs/governance/OPEN_ISSUES_LEDGER.md` | complete issue forensics and remediation blueprints |
| `docs/governance/ARCH_CSS_DOM_CONTRACTS.md` | tokens, CSS/DOM, content markup, accessibility/print contracts |
| `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md` | language/CLI/JS audit, migrations and verification suite |
| `docs/governance/TERMINOLOGY_AND_SOURCES.md` | source roles, S1–S38, terminology, hashes and warrant rules |
| `docs/governance/CHANGELOG_ARCHIVE.md` | historical entries beyond rolling ten |

Topic routing: issue diagnostics→`OPEN_ISSUES_LEDGER.md#iss-index`; CSS/tokens/DOM/pillars/accessibility/pedagogy→`ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers`; JS/Python/TS/verification→`INFRA_PYTHON_TS_JS_AUDIT.md#js-suppression-registry`; source authority/terms/S1–S38/literature→`TERMINOLOGY_AND_SOURCES.md#conflict-log`; dated history→`CHANGELOG_ARCHIVE.md#archive-policy`.

Missing named input: `Master_Final_Perfected.md` is absent `[TESTED]`; historical `PROMPT_Master_html_4_tema.md` and `4lastDEEP_INSPECTION_ADDENDUM_20_TASKS_10_FEATURES.md` are present. `HTML_MASTER_BUILD_PROMPT.md` absent. Workspace is not a Git repository; use direct inventory and path/bytes/mtime/SHA-256 evidence. Do not traverse outside this workspace.

Open Issues: tags `[TESTED]` measured; `[INSPECTED]` read/parsed; `[INFERRED]` reasoned; `[UNVERIFIED]` open. Close only with current owner/output evidence. Full diagnostics: [OPEN_ISSUES_LEDGER.md](docs/governance/OPEN_ISSUES_LEDGER.md#iss-index).

| ID | Category | Location | Rule violated / gap | Target | Tag | Details |
|---|---|---|---|---|---|---|
| OI-01 | HTML-Defect | master | 2,502,506 B >2 MiB by 405,354 B (R21 first pass −193,951 B) | Python | `[TESTED]` | [ISS-001](docs/governance/OPEN_ISSUES_LEDGER.md#iss-001) |
| OI-03 | Closed | `part_15.html`, `#search-index` | unified schema: 126 recall / 15 intro / 25 final / 57 bank reconcile across owners, search manifest and master | Python | `[TESTED]` | [ISS-007](docs/governance/OPEN_ISSUES_LEDGER.md#iss-007) |
| OI-04 | Closed | `part_16.html`, `part_top.html` | revision dates aligned to 2026-11-07 in doc-meta and C.4 footnote | HTML | `[TESTED]` | [ISS-007](docs/governance/OPEN_ISSUES_LEDGER.md#iss-007) |
| OI-05 | Unverified | root | `Master_Final_Perfected.md` absent | Markdown | `[TESTED][UNVERIFIED]` | [ISS-007](docs/governance/OPEN_ISSUES_LEDGER.md#iss-007) |
| OI-06 | Source-Conflict | Appendix H, biology, source list | ">250%" removed; ATP/Mg²⁺ warranted; BMR/TDEE §8.6 and ischemia recall values labelled `papildinājums`/`[jāpārbauda]` (R21); primary-source page check open | HTML | `[TESTED: labels; source pages UNVERIFIED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-07 | Closed | `initLeitnerRecall`, `.leitner-*` | Leitner/mastery UI fully retired (R21); recall is unscored native `<details>` per §8 | HTML/CSS | `[TESTED]` | [ISS-002](docs/governance/OPEN_ISSUES_LEDGER.md#iss-002) |
| OI-08 | Closed-Print | print/PDF/map | print convergence, exact-hash manifest & 0 sparse pages verified (UI interactive open in T17+) | Python/manual | `[TESTED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-09 | Unverified | theme, controls | contrast and target-size acceptance open | CSS/Python | `[UNVERIFIED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-10 | Closed | 115-concept inventory | 5-pillar audit complete: 115/115 audited, 98 worked examples, 17 justified inapplicable | Python | `[TESTED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-11 | Closed | skill lint reports | current lint rerun: 0 FAIL, 12 WARN; structural emoji removed from recall cues | Python | `[TESTED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-13 | Closed | `.tracker-pulse` | 0 looping animations; animation/keyframes retired in T17 | CSS | `[TESTED]` | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) |
| OI-15 | JS-Bloat | executable script | 265,043 B / 6,016 lines / 10.60% | TS/Python | `[TESTED]` | [ISS-001](docs/governance/OPEN_ISSUES_LEDGER.md#iss-001) |
| OI-16 | JS-Bloat | runtime renderers | 40 `innerHTML`, 52 `createElement` | Python/HTML | `[TESTED]` | [ISS-002](docs/governance/OPEN_ISSUES_LEDGER.md#iss-002) |
| OI-17 | JS-Bloat | inline handlers | 67 total (62 click, 3 submit, 2 input) | HTML/CSS | `[TESTED]` | [ISS-002](docs/governance/OPEN_ISSUES_LEDGER.md#iss-002) |
| OI-18 | JS-Bloat | details/dialog/print | 298 details without `name`; 4 dialogs; 0 popover attrs | HTML/CSS | `[TESTED]` | [ISS-003](docs/governance/OPEN_ISSUES_LEDGER.md#iss-003) |
| OI-19 | JS-Bloat | instruments/scrubbers | 2 RAF, 2 intervals, 9 timeouts | TS/Python | `[TESTED]` | [ISS-002](docs/governance/OPEN_ISSUES_LEDGER.md#iss-002) |
| OI-22 | Closed | output fragments | 0 inline styles in master/fragments; semantic classes mapped in T17 | CSS/HTML | `[TESTED]` | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) |
| OI-23 | Closed | inline SVGs | 42 teaching SVG + 1 shared sprite container = 43 `<svg>`; `<symbol>`+`<use>`; owner/use registry; plate/caption gate | Python/HTML | `[TESTED]` | [ISS-003](docs/governance/OPEN_ISSUES_LEDGER.md#iss-003) |
| OI-24 | Infra-Gap | `tools/` | SVG geometry/registry gate added (T19); full HTML-anchor/static/print gates still missing | Python | `[INSPECTED]` | [ISS-005](docs/governance/OPEN_ISSUES_LEDGER.md#iss-005) |
| OI-25 | Infra-Gap | `ts/` | TS source/config absent; `tsc` absent in prior inventory | TypeScript | `[TESTED]` | [ISS-005](docs/governance/OPEN_ISSUES_LEDGER.md#iss-005) |
| OI-26 | Infra-Gap | `build/qa/`, `scratch/` | 84 `.mjs` probes outside stack | Python/TS | `[TESTED]` | [ISS-005](docs/governance/OPEN_ISSUES_LEDGER.md#iss-005) |
| OI-27 | Infra-Gap | `build/`, `scratch/` | one-off mutators/debris; no cleanup authorized | Python | `[INSPECTED]` | [ISS-005](docs/governance/OPEN_ISSUES_LEDGER.md#iss-005) |
| OI-28 | Unverified | `noscript`, instruments | structural JS-off fallback complete: 10 noscript, 8/8 instruments, static tables; executed browser behavior unverified | HTML/Python | `[TESTED: structural; visual UNVERIFIED]` | [ISS-006](docs/governance/OPEN_ISSUES_LEDGER.md#iss-006) |
| OI-29 | CSS-Arch | CSS state/layout | no `:has()`/`:checked`/subgrid; one unnamed 560px container query | CSS | `[TESTED]` | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) |
| OI-30 | HTML-Defect | dialog/popover/print | native transient states and print behavior incomplete/unverified | HTML/CSS | `[UNVERIFIED]` | [ISS-003](docs/governance/OPEN_ISSUES_LEDGER.md#iss-003) |
| OI-31 | Source-Conflict | course PDFs | pages not reverified this run | Markdown | `[UNVERIFIED]` | [ISS-007](docs/governance/OPEN_ISSUES_LEDGER.md#iss-007) |
| OI-32 | Unverified | T-required concepts / inventory | Third Law, kinetic/potential energy, ΔG–K and T dependence need current coverage audit | Python/HTML | `[UNVERIFIED]` | [ISS-008](docs/governance/OPEN_ISSUES_LEDGER.md#iss-008) |
| OI-33 | CSS-Arch | `build/style.css` | 7 cascade layers active; non-print `!important` reduced to 28 (accessibility-only) | CSS | `[TESTED]` | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) |
| OI-34 | Closed | `build/style.css` | 0 raw hex matches outside token block; all mapped to tokens in T17 | CSS | `[TESTED]` | [ISS-004](docs/governance/OPEN_ISSUES_LEDGER.md#iss-004) |
| OI-35 | Closed | `part_6_9/10_12`, `build_html.py`, instruments | B03 remnant: duplicate sections 6.9/11.5/12.7 renumbered (6.10/6.11, 11.6, 12.8) with refs updated; Gate 25 enforces unique monotonic h3 numbers and heading-level order | Python/HTML | `[TESTED]` | [ISS-INDEX](docs/governance/OPEN_ISSUES_LEDGER.md#iss-index) |

**[OFFLOAD-SHARD]:** When triaging/closing an issue or changing queue/file ownership, read `docs/governance/OPEN_ISSUES_LEDGER.md#iss-index` in full first.

## 3. Source Authority & Conflict Resolution

Authority roles: T=scope, K=theory, U=question wording/data, L=lab procedure, LA=partial answers, E=convention exemplar only. Preserve course-specific answers on conflict; show discrepancies and label outside corrections `papildinājums`/`jāpārbauda`; never invent citations. PDF identity/hash is metadata evidence, not text verification. Source authority, epistemic tags, exact files/hashes, page maps and S1–S38 are in the shard.

**[OFFLOAD-SHARD]:** When using or editing source claims, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log` and `#verified-source-registry` in full first.

## 4. Output Contract & 4-Language Architecture

One `<html lang="lv">` offline file; no CDN, external fonts, fetch or network; one h1; ordered headings, landmarks, captions, accessible SVG, static fallback. **Tier 1:** semantic HTML/CSS ≥95% UI state. **Tier 2:** deterministic Python build/extraction/precompute/checking. **Tier 3:** strict TS only for unavoidable residual input. **Tier 4:** raw JS only for registered compiled hooks. JS total ≤min(4,096 B, 100 formatted lines, 2% HTML); zero DOM templating/injection, JS UI duplicating native controls, inline handlers, libraries, scroll-jacking or decorative RAF/interval loops.

| Whitelisted hook | Max | Why not HTML/CSS + Python | JS-off degradation |
|---|---:|---|---|
| `themeInit` | 300 B / 8 lines | read explicit preference before first paint | system theme |
| `themeToggle` | 400 B / 12 lines | persist user choice | system theme/no toggle |
| `dialogEdge` | 500 B / 15 lines | narrow focus-return/Esc edge case | `<details>`/`:target` |
| `thermoCalc` | 2,000 B / 45 lines | arbitrary numeric input | Python table + `<noscript>` |
| `errorLog` | 800 B / 20 lines | consented local persistence/deletion | log hidden; study unaffected |

No current function is confirmed compliant. Layer order `reset,tokens,base,layout,components,utilities,print`; tokens `--p-* → --t-* → --c-*`; DOM IDs `#ch1–#ch16`, `#sec-chN-N`, `#app-*`, `#instrument-a–h`, `#concept-map`, `#recall-item-N`, `#fig-*`, `#prov-N`. Full contracts: architecture shard and TS/JS audit shard.

**[OFFLOAD-SHARD]:** Before any UI/runtime/infrastructure edit, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#dom-and-identifier-contract` and `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#js-suppression-registry` in full.

## 5. Content Standard (5 Pillars)

Every taught concept: (1) definition/scope, (2) causal mechanism, (3) traceable worked example with units, (4) common error→reason→fix, (5) canonical Latvian term. Explain true inapplicability; do not waive missing pillars. Required areas: system/state/energy; 1st–3rd laws; H/Hess; entropy/Gibbs/T/equilibrium; calorimetry/food energy; biology/ATP/coupling; U1–U6; lab conclusions. T-required/K-missing material is `papildinājums`. Numerical rules: decimal comma, NBSP before units, U+2212, ΔH°/ΔG°/S°, J↔kJ conversion; recompute through owner calculation vectors before a production release. Course signs: `Q=ΔU+A` (Q absorbed, A by system); IUPAC `ΔU=q+w`, `w=−A`; lab `ΔH_r=−q_šķīdums/n`.

**[OFFLOAD-SHARD]:** When auditing content markup or pillar coverage, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup` in full.

## 6. Terminology Check & High-Priority Corrections Table

Use Hesa likums, Gibsa enerģija, patvaļīgs, siltumefekts; English equivalents only in glossary. High priority: `siltumsaturs`→entalpija; state variables ≠ state functions; endergonisks/eksergonisks ≠ endo/eksotermisks; `ΔG>0` means non-spontaneous alone, not forbidden; standard state ≠ temperature; W=microstate count; c≠C; Cal=kcal; ΔG°′ ≠ actual cellular ΔG. Do not silently normalize quoted source errors.

**[OFFLOAD-SHARD]:** Before terminology or scientific wording changes, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary` and `#source-defect-register` in full.

## 7. Design & CSS Engineering Standard

Calm reference layout: prose and real data graphics, one accent. Hard exclusions: decorative gradients/glow/glass, any `box-shadow`, structural emoji, uniform card grids splitting prose, hero banners, decorative/looping animation, drop caps, badge clutter, stock imagery. Thresholds: text ≥4.5:1 normal, ≥3:1 large/UI/focus; visible `:focus-visible`; controls ≥44 px and usable at 320 px; reduced-motion honored. Print: white ground/dark ink, answer disclosures expanded once, no duplicate keys, sticky/fixed flattened, rows/captions kept and monochrome-legible. Visual pass requires Falkon `webshot` PNGs captured and directly inspected for 1440/768/390 light+dark, 320, keyboard and PDF pages. No source-only visual claims.

**[OFFLOAD-SHARD]:** For token values, layers, accessibility/print patterns, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers` in full.

## 8. Pedagogy Standard (Native HTML Interactive Patterns)

Use native `<details name>`, `<dialog>`, Popover API, `:has()`, `:checked`, `:target`, `:focus-within`, `@container`, Grid/subgrid, `clamp()`, counters and `@starting-style` where semantically suitable. Retrieval answers closed on screen. Keyboard/core navigation must work with JS off. No mastery scores, Leitner boxes, streaks or XP. Error-log persistence only with explicit consent, local-only behavior and visible deletion. Figures need equivalent text and “what to notice.”

**[OFFLOAD-SHARD]:** Before adding an interaction, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns` in full.

## 9. Sourcing & Provenance Rules

For every correction/calculation record source/page or question, original, corrected wording, reason, confidence and basis S-ID. `[TEXT-VERIFIED]` is claim/page-specific; `[METADATA-VERIFIED / SCOPE-ALIGNED]` is identity/role only. No invented pages, quotes, editions, ISBNs, DOIs or citations. Current PDF file hashes are recorded but do not prove text. Historical source defect register S1–S38 remains open to page-level recheck.

| ID | File | Role | Recorded pages |
|---|---|---|---:|
| T | `4 temata apraksts.pdf` | scope | 1 |
| K | `Termodinamika_pamatkonspekts_2026.pdf` | theory | 19 |
| U | `4_SEM_Termodinamika_uzdevumi.pdf` | U1–U6 wording/data | 2 |
| L | `LW_Thermodynamics_2020_LV (2).pdf` | lab procedure | 3 |
| LA | `4_SEM_Labor_Thermodynamics_2026_LV _Atbildes.pdf` | partial answer key | 3 |

Page counts are from the recorded 2026-11-06 metadata pass; hashes from 2026-11-07; source text was not revalidated in this run.

**[OFFLOAD-SHARD]:** When evaluating claim provenance or 2026 literature, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry` and `#literature-2026` in full.

## 10. Python/TS Infrastructure, New Features & 2026 Literature Integration

Existing `tools/`: build, budget, CSS, contrast, terminology, SVG geometry/registry (`check_svg.py`), visual capture, token migration. Build/check scripts may mutate `build/qa/`, `calc.json`, or master; inspect effects before invoking. Required gates: output/executable-JS budget; CSS token/layer/inline style; HTML anchors/IDs/headings/counts; source/calculation vectors; static fallback; print/PDF; hash-bound reports. Use `python3 -I`, deterministic stdlib tools and nonzero exits. No TS source/config/compiler currently; future `ts/tsconfig.json` strict, zero `any`, explicit DOM checks, compile/minify and measured registry output. OI-06 literature/biology claims need verified identity and exact claim support before citation.

**[OFFLOAD-SHARD]:** Before Python/TS tooling or tests are changed/run, read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli` and `#verification-suite` in full.

## 11. Editing, Non-Regression & Byte-Budget Rules

Protect PDFs and skill sources. Edit canonical owners in `build/`, regenerate through inspected generator, and retain direct fingerprints. This governance run is restricted to `AGENTS.md` plus the five canonical shards. Master identity is checked by path+bytes+mtime+SHA-256; this workspace has no usable Git history. Append a dated row; retain ten recent runs here and move older rows without loss to archive. `AGENTS.md` ≤24,576 B.

| Date | §§ / shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-07 | 2,4,5,8,11,12 | R21 remnant closure: B03 duplicate sections 6.9/11.5/12.7 renumbered + Gate 25; OI-07 Leitner/mastery UI retired; B04 BMR/ischemia warrants + DISC-08 alignment; OI-04 dates; B01 budget profile + first reduction pass | user request: close 35-task roadmap remnants after four-agent integration audit (T01–T20 verified integrated) | part_top/6_9/10_12/13_14/15/16, script.js, style.css, build_html.py, search_index.py, verify_master.py, check_budget.py, svg_registry.json, pre/post fingerprints in scratch/remnant-run-20261107/ `[TESTED: 96/96 gates structural; Falkon 1280 capture inspected; dark/320/keyboard/print PDF UNVERIFIED]` |
| 2026-11-07 | 4,5,8,11,12 | F12: 12.7 phase/standard-state lab; 4 cases/18 labelled rows, native radios, no default, print-all, search rows, Gate 24 | phase-selector request; O₂/H₂O/N₂O₅/1 bar–1 atm boundaries; workspace F02 is notation, so registered F12 | calc.py, calc.json, part_10_12, part_top, part_16, build_html.py, search_index.py, style.css, verify_master.py `[TESTED: 93/93 structural; CSS visual 1440/320 light+dark captured; keyboard/print PDF UNVERIFIED]` |
| 2026-11-07 | 4,5,11,12 | F11: C.3 source-conflict atlas; JSON owner, static table, two-way S-ID/claim anchors, search index, print/screen CSS, Gate 23 | F01 atlas request; source pages verified; avoid duplicate F04 overlay | build/source_conflicts.json, part_16, build_html.py, search_index.py, style.css, verify_master.py `[TESTED: 85/85 structural; light visual inspected; dark/keyboard/print UNVERIFIED]` |
| 2026-11-07 | 4,5,8,10,11,12 | T20: generator-owned assessment schema; 126/15/25/57 count reconciliation; hash-bound 22-gate report; answer-leak/JS-off boundary; stale-report rejection | C10,C11, OI-03,OI-10,OI-11,OI-28 | assessment_schema.py, build_html.py, search_index.py, part_15, instruments, data owners, verify_master.py, qa/fixtures, verify-report.json `[TESTED: structural; keyboard/320-visual/print UNVERIFIED]` |
| 2026-11-07 | 4,7,10,12 | T19: SVG sprite reuse, stable a11y wiring, clip/caption/collision gate, two Section-6 plates | C13, OI-23 | figures.py/html, figure_steps, style.css, build_html.py, calc.py, svg_registry.json, check_svg.py `[TESTED: structural; visual UNVERIFIED]` |
| 2026-11-07 | 4,10,12 | T18: Unit-safe validated calculators, strict dimensions, -0/comma guards & TS contract | C01,C03,C12, OI-15–19, 24–25 | script.js, calc.py, calc.json, instruments.html, ts/, check_print_map.py `[TESTED]` |
| 2026-11-07 | 4,7,8,10 | T17: 7-layer CSS cascade, zero hex/inline styles/looping anim, contrast & 320/print pass | C13, OI-13–14, 20–22, 33–34 | style.css, check_css.py, figures.py, check_contrast.py, calc.py `[TESTED]` |
| 2026-11-07 | 4,7,8 | T16: Print convergence, page map & companion ordering | C13, OI-08 | style.css, print_map.py, inject_page_map.py, f10-final.pdf, check_print_map.py `[TESTED]` |
| 2026-11-07 | 4,5,8 | T15: 5-pillar audit, option reasoning cues, Roediger fix | C10,C11,OI-10,OI-06 | inventory.json, data_tests.py, data_recall.py, part_15, script.js `[TESTED]` |
| 2026-11-07 | 1–12; all five | Governance topology, current-output issue ledger, shard links and 12-section contract | Zero-loss offload; correct stale evidence; fit byte cap | master fingerprint unchanged; link audit; byte counts `[TESTED]` |

Older history: [CHANGELOG_ARCHIVE.md](docs/governance/CHANGELOG_ARCHIVE.md#archive-2026-11-07).

**[OFFLOAD-SHARD]:** Before editing this governance ledger or rotating entries, read `docs/governance/CHANGELOG_ARCHIVE.md#archive-policy` in full.

## 12. Done Definition (Automated Python + Manual Post-Pass Verification Checklist)

Release only when each is separately evidenced or marked `[UNVERIFIED]`: (1) one canonical master and unchanged/intended fingerprints; (2) ≤2 MiB and JS/CSS/HTML hard gates; (3) source-traced calculations recomputed; (4) five pillars/topic coverage; (5) contrast, keyboard, motion, 320 px and JS-off; (6) anti-slop rules; (7) dated ten-row log and AGENTS byte cap; (8) tags accurately distinguish tests, inspection, inference and open work. Visual and print acceptance requires captured/viewed artifacts for the current hash.

**[OFFLOAD-SHARD]:** Before release verification, read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite` in full.
