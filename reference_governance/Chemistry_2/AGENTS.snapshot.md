# AGENTS.md — Chemistry_2

Contract for the offline Latvian textbook **Medicīniskā ķīmija, 2. tēma**; last audit 2026-11-07. Maintain one generated master; never weaken standards to excuse defects. This is the executive routing hub; detailed shards are in `docs/governance/`. Target 14–20 KiB; hard max 24,576 B (`wc -c < AGENTS.md`).

## 1. Goal & architectural philosophy

Improve the single generated master non-destructively from `build/` sources: HTML/CSS first, Python build/verification, strict TypeScript for residual logic, compiled JavaScript last. Learner: first-year RSU medical student; topics: lab equipment, measurement, units, significant figures, errors/statistics, graphs/calibration, half-life, solutions and density. Teach reasoning; label course text/additions/examples; preserve conflicts and standards.

**[OFFLOAD-SHARD]:** For architecture/pedagogy changes, read [contracts](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup) and [issues](docs/governance/OPEN_ISSUES_LEDGER.md) first.

## 2. Workspace topology, shard routing & Open Issues Index

| Path | Role / rule |
|---|---|
| `Master_2_tema_merijumi_un_grafiki.html` | Canonical generated master; never hand-edit, move, rename or delete. Pre-run 2026-11-07 fingerprint: 985,696 B; SHA-256 `1c16f08f96cb2ceee0a6e30cb2af40c6859d7a4c2d67bd88141e96cf41fa3dc4`; mtime `2026-11-07 13:34:28.139748129 +0200`. |
| `build/sections/00_front`, `01_ch1`–`16_ch16`, `98_quickref`, `99_footer` (`.html`); `build/style.css`, `build/app.js` | Canonical inputs; generate with `python3 -I build/build_doc.py`. |
| `build/*.py`, `tools/*.py` | Build/data/verification. Use `python3 -I`; inspect side effects. |
| `build/*.mjs` | QA-only harnesses; not part of the four-language production stack or shipped runtime. |
| `build/sources.json`, `build/claims.json`, concepts/terminology/case data | Local source, claims, learning and case registers. These are not proof of all claims or gates passing. |
| Five course PDFs, prompt files, historical plans/diagnostics | Read-only inputs. Never alter PDFs, `build/baseline/`, or `workspace_skills/` without separate authorization. |
| `docs/governance/OPEN_ISSUES_LEDGER.md` | Full active issue diagnostics and remediation. |
| `docs/governance/ARCH_CSS_DOM_CONTRACTS.md` | CSS token/layer contracts, DOM patterns, five pillars, pedagogy, design/accessibility/print. |
| `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md` | Runtime inventory, JS budgets/migration, Python CLI and TS contract. |
| `docs/governance/TERMINOLOGY_AND_SOURCES.md` | Terminology, source hierarchy, provenance and source-conflict register. |
| `docs/governance/CHANGELOG_ARCHIVE.md` | Historical run rotation and closure trails. |

Environment [TESTED 2026-11-07]: Python 3.12.16, pypdf/pdftotext; Node 24.22.2; Falkon/Xvfb; no `tsc`; no Git. `Master_Final_Perfected.md`, exact `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md`, and `HTML_MASTER_BUILD_PROMPT.md` are absent. A first-round roadmap and other plans exist; do not treat/rename them as the exact active queue.

### Open Issues Index

Categories are JS-Bloat, CSS-Arch, Infra-Gap, HTML-Defect, Source-Conflict, Unverified, Gate and Governance. Close only with evidence and a dated changelog row; linked anchors hold forensics.

| Issue ID | Category | Location | Rule violated / gap | Target | Details shard anchor | Tag |
|---|---|---|---|---|---|---|
| JS-01 | JS-Bloat | Master/app.js | 41.9 KB; 770 lines; 4.33% vs 4,096 B/100 L/2%. | TS/HTML/Python | [ISS-JS-01](docs/governance/OPEN_ISSUES_LEDGER.md#iss-js-01) | [TESTED] |
| JS-08 | JS-Bloat | Master disclosures/glossary | 1 noscript; 0 dialogs; 60 popover triggers; JS-off untested. | HTML/CSS | [ISS-JS-08](docs/governance/OPEN_ISSUES_LEDGER.md#iss-js-08) | [TESTED] |
| CSS-01 | CSS-Arch | `style.css` | Layer order only; bodies unwrapped for Falkon. | CSS | [ISS-CSS-01](docs/governance/OPEN_ISSUES_LEDGER.md#iss-css-01) | [INSPECTED] |
| HTML-04 | Partial | Master | Contrast gate passes; keyboard, targets, AT, `lang` runs unmeasured. | Python/HTML/CSS | [ISS-HTML-04](docs/governance/OPEN_ISSUES_LEDGER.md#iss-html-04) | [UNVERIFIED] |
| HTML-06 | Source-Conflict | Source/claim ledgers | C19 closed (LNHB+NuDat primary-read); C20 lecturer item open. | Python/editorial | [ISS-HTML-06](docs/governance/OPEN_ISSUES_LEDGER.md#iss-html-06) | [INSPECTED] |
| HTML-08 | Source-Conflict | Appendix C S1–S23/D24–D51 | Editorial closure pending; S11 quote case differs. | Editorial/Python | [ISS-HTML-08](docs/governance/OPEN_ISSUES_LEDGER.md#iss-html-08) | [INSPECTED] |
| HTML-09 | Partial | Print edition | 148-pp export + 4 pages inspected; every-page review pending. | HTML/CSS | [ISS-HTML-09](docs/governance/OPEN_ISSUES_LEDGER.md#iss-html-09) | [UNVERIFIED] |
| HTML-10 | Unverified | Inline SVGs | Falkon paints no plot geometry; fresh captures show containment only. | HTML/Visual | [ISS-HTML-10](docs/governance/OPEN_ISSUES_LEDGER.md#iss-html-10) | [UNVERIFIED] |
| INFRA-01 | Infra-Gap | No `ts/`/config | No strict TS source/compiler. | TS | [ISS-INFRA-01](docs/governance/OPEN_ISSUES_LEDGER.md#iss-infra-01) | [TESTED] |
| GOV-01 | Governance | Root inputs | Three exact audit files absent; alternate roadmap not assumed active. | Governance | [ISS-GOV-01](docs/governance/OPEN_ISSUES_LEDGER.md#iss-gov-01) | [TESTED] |
| GOV-02 | Governance | Workspace root | No Git metadata. | Governance | [ISS-GOV-02](docs/governance/OPEN_ISSUES_LEDGER.md#iss-gov-02) | [TESTED] |

**[OFFLOAD-SHARD]:** Before issue work, read its [detail](docs/governance/OPEN_ISSUES_LEDGER.md#iss-js-01) and related shard.

## 3. Source authority & conflict resolution

Order: five course PDFs (`avotā`); `PROMPT_Master_html_2_tema.md`; this contract/shards; active task; skills as advice. Label corrections/additions; source silence = `avotā nav norādīts`. Never invent locators, quotes or publication metadata. Course evidence is not external-standard verification. Hashes/S1–S23: [registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry), [conflicts](docs/governance/TERMINOLOGY_AND_SOURCES.md#course-conflicts-s1-s23); C19/C20 open.

Tags: `[TESTED]` reproducible check run; `[INSPECTED]` directly read/observed; `[INFERRED]` reasoned, not primary-read; `[UNVERIFIED]` not established; `[TEXT-VERIFIED]` text read at exact locator; `[METADATA-VERIFIED / SCOPE-ALIGNED]` metadata and relevance checked, not full-text support.

**[OFFLOAD-SHARD]:** For source/claim work, read the [conflict log](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) and [registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry).

## 4. Output contract & four-language architecture

Deliver one offline, self-contained `<html lang="lv">` generated by `python3 -I build/build_doc.py`. No CDN, network fonts/requests, analytics, external links, or final-output runtime dependencies. Citations are plain text; identifiers in `<code>`.

| Tier | Language | Ownership | Hard contract |
|---|---|---|---|
| 1 | HTML5 + CSS | ≥95% of interactive/visual behavior | Native `<details name>`, `<dialog>`, `popover`; `:has()`, `:checked`, `:target`, `:focus-within`, `@container`, `subgrid`, `clamp()`, counters, `@starting-style`; zero inline style/handler attributes. |
| 2 | Python 3 | Pre-browser extraction/build/generation/verification | `python3 -I`; deterministic CLI; no output runtime dependency. |
| 3 | TypeScript | Residual client logic impossible in HTML/CSS/Python | strict mode, zero `any`, checked DOM nulls; compile offline to inline output. |
| 4 | JavaScript | Compiled artifact only | Total executable script ≤min(4,096 B, 100 lines, 2% of HTML); no DOM templating, external libraries/network, QA hooks, or JS UI duplicating native features. |

Permitted micro-runtime registry (shared ceiling ≤4,096 B/100 lines/2%; strictest wins):

| Hook | Budget | Why HTML/CSS/Python cannot | JS-off behavior |
|---|---|---|---|
| J1 `themeInit` | 300 B/10 L | Zero-flash saved theme | CSS system theme; hide toggle |
| J2 arbitrary-input calculator | 1,796 B/45 L | Learner enters values | Static cases; label unavailable |
| J3 DOM-derived search | 2,000 B/45 L | Free-text lookup | TOC/glossary remain |

Current master exceeds the shared budget; full function map/migrations: [registry](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#permitted-js-micro-runtime), [audit](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#function-inventory-and-migration).

CSS layers: `reset, tokens, base, layout, components, utilities, print`. Bodies remain unwrapped for lightweight-browser compatibility; declaration alone is not compliance. Tokens and DOM: [CSS](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers), [DOM](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#dom-class-registry). Static: one script, 41,938 B/770 lines (4.33%); 0 inline handlers; JS-06 trainer data removed. Static inspection is not runtime proof.

**[OFFLOAD-SHARD]:** For output/runtime/CSS/DOM work, read [stack](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#language-stack) and [CSS](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers).

## 5. Content standard: five pillars

Each concept covers applicable pillars: definition (term/symbol/unit), mechanism (why/assumptions), recomputed worked example, common mistake (symptom/cause/correction), canonical Latvian + sourced English term. State inapplicability. Label `avotā`, `papildinājums`, `ilustratīvs piemērs`; log changes with locator/original/correction/reason/C-H-V. Recompute displayed math; do not copy keys or assert unverified lab/clinical/policy claims.

Markup and assessment schema: [five-pillar markup](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup).

**[OFFLOAD-SHARD]:** For content/markup edits, read [five-pillar markup](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup).

## 6. Terminology check & high-priority corrections

English terms use `lang="en"`; V means lecturer/course policy must be checked first.

| Risk | Preferred form | Reason |
|---|---|---|
| Significant-digit wording / precision | `zīmīgie cipari`; distinguish `precision` / `pareizība` | S6, S9, S13; VIM not primary-read |
| Error vs. uncertainty | `kļūda` vs. `nenoteiktība` | Distinct quantities |
| Absorption / coefficient | `absorbance A`; qualify `a`/ε and units | Quantity/process; do not equate silently (S5) |
| Statistics | `s`; `Stjūdenta t(α;n−1)` | S8 |
| Ambiguous `450`; isotope/prefix | Scientific notation; `¹³³Cs`; `10⁶ µmol/mol` | S1, S2, S10 |
| SI unit spelling | `mL`, `s`, `dienas`/`d` | Consistency |
| Symbol collisions | `w`; `c(B)`; distinguish `γ(B)` and `ρ` | Avoid ambiguity; verify course policy |

Full dictionary, rationale, search risks and all S1–S23: [terminology dictionary](docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary), [course conflicts](docs/governance/TERMINOLOGY_AND_SOURCES.md#course-conflicts-s1-s23). Do not invent etymologies; a term-gate pass is not editorial verification.

**[OFFLOAD-SHARD]:** For terminology edits, read the [dictionary](docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary).

## 7. Design & CSS engineering standard

Measured scientific design: cool low-chroma ground, deep ink, restrained accent, real data graphics. Ban gradients/glow/glass, structural emoji, uniform card grids, hero banners, decorative motion, medallions, badges, gamification and tracked microtype. ≤2 callouts/screen, no nesting; emphasize only Rule, Mistake, Verified; other labels neutral; ≤2 type families; tabular numerals.

| Gate | Requirement |
|---|---|
| Contrast | WCAG 2.2 AA: text ≥4.5:1; large/UI ≥3:1; measure light/dark. |
| Focus/targets | `:focus-visible` ≥3:1; controls ≥44px. |
| Keyboard/semantics | Reading/navigation without JS; one h1, ordered headings, labelled controls, non-color cues, SVG title/desc, language tags. |
| Motion | Honor `prefers-reduced-motion`; no decorative motion. |
| Print | Force light; expand details once; flatten sticky/fixed; keep rows/figures/captions; number pages; contents/colophon; inspect every page. |
| Visual | UI/layout/SVG/style/theme/reflow claims require inspected PNG from `lite-shot` Falkon under `VISUAL_VERIFICATION.md`; source/DOM alone never pass. Chrome/Chromium prohibited unless user explicitly allows in current turn. |

Current layer, token and evidence gaps stay open in §2; full token and markup standards are in the [accessibility contract](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#anti-slop-and-accessibility).

**[OFFLOAD-SHARD]:** For style/accessibility/print edits, read [CSS tokens](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) and [gates](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#anti-slop-and-accessibility).

## 8. Pedagogy & native interaction

Teach selection, setup, reasoning, units, uncertainty, interpretation and transfer. Connect examples to rules/errors; show intermediate values/precision; label measured, calculated, graph-read and illustrative data. Explain axes, scale, fit and calibration limits; high R² alone is insufficient. From nonzero origin, half-life uses intervals between successive halvings.

Use native `<details name>`, `:target`, popover and `:checked`; keep recall answers out of search and preserve static/print alternatives. No gamification or silent storage; `localStorage` only by informed consent. Patterns: [pedagogy shard](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns).

**[OFFLOAD-SHARD]:** For study interaction edits, read [pedagogical patterns](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns).

## 9. Sourcing & provenance

Five course PDFs form the local source set; `build/sources.json`/`claims.json` record hashes/claims. C19/C20 open; no claim rests on V0/V1 alone. Paraphrase and never infer citations. Separate course text from verified standards/additions. See [registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry), [conflicts](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log), [2026 intake](docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026).

**[OFFLOAD-SHARD]:** For source edits, read the [registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry).

## 10. Python/TypeScript infrastructure and new features

Common Python checker contract: `python3 -I`, deterministic, nonzero on failure, stdout report, no network or final-output runtime dependency. Present: `tools/check_index_privacy.py`, `check_anchors.py`, `check_sources.py`, `check_figure_style.py`, `check_budget.py`, `check_contrast.py`, `check_selfcontained.py`, `check_font_glyphs.py`, `check_pillars.py`, `check_counts.py`, `make_manifest.py`; `build/check_sources.py` and domain/numeric gates. Missing: no strict TS compiler (blocks JS-01 closure). New features require source trail, accessible controls and static/print fallback. `build/*.mjs` remains QA-only and outside production matrix.

| Family | Entrypoints | Purpose |
|---|---|---|
| Budget / contrast | `check_budget.py`, `check_contrast.py` | File ceilings and WCAG token pairs (light/dark). |
| Integrity | `check_anchors.py`, `check_selfcontained.py`, `check_font_glyphs.py`, `check_counts.py` | IDs/targets/headings; self-containment; glyph cmap; derived counts. |
| Existing | `build/check_*`, privacy/source/number gates | Terminology, tables and domain cases. |

Exact CLI specs, strict TS contract, observed functions, budget allocation and verification separation: [Python CLI](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli), [TypeScript](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#typescript-contract), [verification suite](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite).

**[OFFLOAD-SHARD]:** For infrastructure/runtime work, read [Python](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli) and [TypeScript](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#typescript-contract).

## 11. Editing, non-regression & rolling changelog

Honor task locks. Product pass: edit `build/` sources, never generated HTML/SVG; hash master, run `python3 -I build/build_doc.py`, diff, then requested gates. Preserve PDFs, baseline and QA residue. Governance-only: change authorized Markdown; prove master hash/size/mtime and changed-path inventory. No commits/Git claims. Keep browser, source, runtime, access, visual and print gates distinct.

### Changelog — 9 recent entries (7 prior + 2 current)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-07 | §§2,4 | Native residual radio view | JS-05 | 973,591 B; historical [TESTED] |
| 2026-11-07 | §§2,4,7,10 | B02 recall/privacy/print fixes | JS-off answers | 26 assertions; 142/143 pp; historical [TESTED] |
| 2026-11-07 | §§2,4,10 | T19 DOM search + glossary | Runtime bloat | 941,149 B; historical [TESTED] |
| 2026-11-07 | §§2,9,10 | F10 source/claim ledger | Provenance | 5 sources/20 claims; historical [TESTED] |
| 2026-11-07 | §§2,4,10 | B01 calculator guards | Invalid inputs | 16+/28−; Firefox; historical [TESTED] |
| 2026-11-07 | §§2,4,10 | B05 closed duplicated SVG styles | Accessibility | 0 nested styles; [TESTED]/[INSPECTED] |
| 2026-11-07 | §§1–12; shards | Created vault; refreshed issues and routing | Governance/byte limit | Telemetry and links checked; [TESTED] |
| 2026-11-07 | §§2,4,7,10 | Product: JS-06 trainers static; font fallback; line-strong 3:1; six new gates; C19 closed | Budget/contrast/fonts/counts | 41,938 B script; Firefox/BiDi 0 errors; 148-pp print PDF; [TESTED] |
| 2026-11-07 | §§2,10,12 | Governance: index refreshed; 11 issues closed with fresh evidence | Governance/byte limit | Gates rerun post-edit; [TESTED] |

No archive rows older than the ten-entry rolling window were present before this pass. Rotation policy and preserved closure summaries: [archive policy](docs/governance/CHANGELOG_ARCHIVE.md#archive-policy), [closure trails](docs/governance/CHANGELOG_ARCHIVE.md#closed-issue-trails).

**[OFFLOAD-SHARD]:** For history/closure work, read the [archive policy](docs/governance/CHANGELOG_ARCHIVE.md#archive-policy).

## 12. Done definition & verification checklist

1. **Automated:** AGENTS ≤24,576 B; run §10 gates or report telemetry only; script within §4.
2. **Manual:** reread 12 sections/five shards; verify links, standards, sources and missing inputs.
3. **Issues:** match rows to evidence; retain browser, AT, source, print or lecturer gaps.
4. **Product:** content, math, sources, privacy, access, responsive, print and JS-off gates stay separate.
5. **Governance lock:** authorized files only; master hash/size/mtime unchanged; no Git claims.

**[OFFLOAD-SHARD]:** Before verification edits, read [suite](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite) and [issues](docs/governance/OPEN_ISSUES_LEDGER.md).
