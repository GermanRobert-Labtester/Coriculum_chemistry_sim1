---
title: "Master Workspace Audit & 35-Task Roadmap"
version: "1.0"
generated_by: "MASTER PROMPT v4.0 HARDENED"
workspace_root: "/home/robertsrff/Chemistry_Med/Chemistry_2"
audit_date: "2026-11-09"
total_packages: 35
populated_packages: 35
voided_packages: 0
---

# MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP

## 1. Executive Decision Brief & First-Principles Workspace Profile

### 1.1 Executive Decision Brief

This document establishes the production-grade, evidence-led audit and 35-package engineering roadmap for the offline study workspace `Medicīniskā ķīmija, 2. tēma: Mērījumi, grafiskās metodes, laboratorijas trauki un šķīdumi` (Medical Chemistry, Topic 2: Measurements, Graphical Methods, Laboratory Glassware, and Solutions), situated at `/home/robertsrff/Chemistry_Med/Chemistry_2`.

As of the audit date (2026-11-09), this workspace represents a high-rigor, single-file offline digital textbook and interactive study guide compiled deterministically from modular HTML section sources, modular CSS, vanilla JavaScript, and Python-verified data models. The project's canonical generated deliverable is `Master_2_tema_merijumi_un_grafiki.html` (969,738 bytes; SHA-256: `35819d730d74909b0b556aa8aee24d5babaa878cfe9a1afd732cb9dc51d8efea`).

#### Strategic Decision & Architectural Directive
1. **Source of Truth Hierarchy:** The workspace operates under an uncompromised four-language stack:
   - **Tier 1 (HTML5 + CSS):** Owns $\ge 95\%$ of all interactive and visual behavior (native disclosures `<details name>`, Popover API, native form controls, CSS `:has()`, `:checked`, `:target`, CSS Grid/Flexbox).
   - **Tier 2 (Python 3 Standard Library):** Owns all deterministic pre-browser document compilation, mathematical recomputations (`Decimal`), dataset verification, source ledger validation, and static quality gates.
   - **Tier 3 (TypeScript):** Strict client-side logic contract (`strict: true`, zero `any`, explicit DOM null checks) for residual calculations and dynamic DOM text indexing.
   - **Tier 4 (JavaScript):** Shipped strictly as an offline compiled/minified artifact adhering to the shared ceiling of $\le \min(4,096\text{ bytes}, 100\text{ lines}, 2\%\text{ of HTML})$.
2. **Current Baseline State:** In the preceding governance and product pass (2026-11-07), significant debloating and verification infrastructure was integrated:
   - Finite trainer case arrays (`sftCases` and `grTasks`) were purged from the client runtime (`app.js`), reducing executable script size from 101,982 bytes to 40,792 bytes (41,938 bytes inline in the master; 770 lines).
   - Ten duplicate inline SVG `<style>` blocks (10,285 bytes of pure redundancy) and 15 dead `.svg-*` rules were eliminated, establishing centralized scoped SVG styling in `build/style.css`.
   - Comprehensive Python verification gates were introduced in `tools/`: anchor resolution (`check_anchors.py`), WCAG 2.2 token contrast (`check_contrast.py`), metric drift (`check_counts.py`), SVG styling cleanliness (`check_figure_style.py`), WOFF2 glyph cmap coverage (`check_font_glyphs.py`), search index answer privacy (`check_index_privacy.py`), five-pillar concept coverage (`check_pillars.py`), self-containment/zero external network requests (`check_selfcontained.py`), and source ledger consistency (`check_sources.py`).
   - Claim C19 regarding Mercury-203 ($^{203}\text{Hg}$) evaluated half-life was formally resolved by primary-source verification of the LNHB/DDEP and NuDat 3 / ENSDF evaluations.
3. **Primary Active Blockers (The Imperative for This Roadmap):**
   - **JS-01 (Runtime Script Over-Budget):** Despite the 2026-11-07 debloat, the client script stands at 41,938 bytes and 770 lines (4.325% of the master HTML), exceeding the mandatory 4,096-byte / 100-line / 2% budget ceiling by 37,842 bytes.
   - **INFRA-01 (Missing Strict TypeScript Toolchain):** No `ts/` directory, `tsconfig.json`, or automated offline compilation harness exists in the workspace.
   - **Toolchain Drift in Test Harnesses:** `check_sigfig_cases.py --check` fails because it expects `sftCases` inside `app.js`, failing to recognize the migration to static HTML tables.
   - **HTML-06 / C20 (Open Lecturer Policy Item):** The chromogenic spectrophotometric reagent for ascorbic acid assay at 521 nm remains unspecified in the course materials.
   - **HTML-04 & HTML-10 (Accessibility & Visual Geometry Verification):** While contrast is fully gated, 44px touch targets, full keyboard traversal, and screen-reader tree semantics remain unmeasured. In lightweight Falkon browser captures, container boxes render cleanly, but inline SVG vector curves fail to paint, requiring dedicated visual engine verification.

### 1.2 First-Principles Workspace Profile

- **Primary & Secondary Academic Disciplines:**
  - *Primary Discipline:* Quantitative Analytical Chemistry and Clinical Metrology.
  - *Secondary Disciplines:* Medical Laboratory Instrumentation, Biostatistics, Chemical Kinetics (Radionuclide Decay), and Solution Thermodynamics/Physical Chemistry (Density and Concentration).
- **Target Learner & Curriculum Profile:**
  - *Target Learner:* First-year medical, dental, and pharmacy students at Rīgas Stradiņa universitāte (RSU).
  - *Prerequisite Baseline:* Secondary school general chemistry and elementary algebra; no prior exposure to advanced laboratory metrology or formal uncertainty propagation.
  - *Instructional Objective:* Equipping future clinicians with rigorous physical measurement competence: selecting volumetric glassware, avoiding parallax and reading errors, applying significant-figure rules to laboratory measurements, distinguishing random dispersion from systematic bias, interpreting linear calibration models and residual limits, calculating patient medication dosages via dilution/density relations, and evaluating radionuclide diagnostic decay intervals.
- **Active Language & Notation Matrix:**
  - *Natural Language:* Latvian (`lang="lv"`) is the primary language of instruction and all explanatory prose.
  - *Bilingual Metrological Nomenclature:* English equivalents are systematically integrated and tagged with `lang="en"` (e.g., `<span lang="en">accuracy</span>`, `<span lang="en">trueness</span>`, `<span lang="en">precision</span>`, `<span lang="en">repeatability</span>`, `<span lang="en">absorbance</span>`) to prepare students for international medical literature and prevent common translation conflations.
  - *Mathematical & Chemical Notation:*
    - Standard decimal comma for Latvian prose ($12,70\text{ mL}$, $0,0322$), with unambiguous period parsing in computation tools.
    - Standard SI unit typography with non-breaking thin spaces ($1,50\text{ mol/L}$, $1033,4\text{ kg/m}^3$, $5,0\cdot 10^2\text{ g/L}$).
    - Chemical formulas and isotopic symbols ($^{203}\text{Hg}$, $^{133}\text{Cs}$, $\text{NaCl}$, $\text{C}_6\text{H}_8\text{O}_6$).
    - Metrological statistics: arithmetic sample mean $\bar{x}$, sample standard deviation $s$ (explicitly distinguishing from population $\sigma$), standard error of the mean $s_{\bar{x}} = s/\sqrt{n}$, Student's $t$-distribution quantiles with explicit degrees of freedom $t(\alpha; n-1)$, and confidence intervals ($CI$).
- **Technical Architecture & Runtime Constraints:**
  - *Single-File Offline Artifact:* All markup, styling, embedded base64 WOFF2 fonts, inline SVGs, and residual execution logic are compiled into a single offline file (`Master_2_tema_merijumi_un_grafiki.html`).
  - *Strict Offline Boundary:* Zero remote CDNs, zero Google Fonts, zero external script dependencies, zero tracking/telemetry, zero runtime `fetch()` or `XMLHttpRequest` calls. Verified by `tools/check_selfcontained.py` (Exit 0; 13 allowed W3C namespace URIs).
  - *Progressive Enhancement & Zero-JS Survivability:* Core reading, worked solutions, quick reference tables, and visual diagrams must remain 100% accessible and readable with JavaScript disabled.
- **Workspace Dominant Language & Deliverable Language Choice:**
  - In strict compliance with §1.5 of the Master Prompt, this audit and roadmap is composed in **English** as the operational engineering language, while fully quoting and preserving all canonical Latvian metrological, chemical, and curriculum terms in their authentic forms.

### 1.3 Inspection Limits & Epistemic Declaration

In accordance with §1.3, §4.4, and §7.4:
- **CLI & Test Execution:** Performed live inside the sandboxed environment using isolated Python (`python3 -I`). All check tools in `tools/` and `build/` were executed directly and their results recorded.
- **Visual & Rendering Audit:** Marked as `[CODE-ONLY VISUAL AUDIT]` for vector plot geometries. While Falkon (`/usr/bin/falkon`) and Xvfb are present, headless execution in lightweight QtWebEngine environments historically renders SVG bounding boxes and typography but drops dynamic SVG path rasterization (HTML-10). Chromium and Chrome are prohibited under the project governance rules without explicit turn authorization. No visual acceptance of plot curves is asserted from markup inspection alone.
- **Source Inspection:** All five course source PDFs were verified against the cryptographic SHA-256 signatures in `build/sources.json`. Direct page extracts in `build/source-text/` and `B03_source_adjudication.md` were cross-examined against disputed claims C01–C20.

---

## 2. Workspace, Architecture & Skills Inventory + File-by-File Inspection Ledger

### 2.1 Repository Architecture & Pipeline Map

```
Chemistry_2/
├── Master_2_tema_merijumi_un_grafiki.html  # Canonical generated master (969,738 B) [NEVER HAND-EDIT]
├── AGENTS.md                               # Project governance contract & issue index (18,932 B)
├── 2A_SEM_MCh_LV_Merijumi,grafiki_2025.pdf # Course Source S-2A (SHA-256: 319dfef6...)
├── 2B_SEM_MCh_LV_Trauki,skidumi_2025.pdf   # Course Source S-2B (SHA-256: 894b5fa3...)
├── 2_SEM_MCh_LV_Trauki_Grafiki...pdf       # Course Source S-2026 (SHA-256: bfe8fdd3...)
├── 2_Temata apraksts 2020.docx.pdf         # Course Source S-TOPIC (SHA-256: c7d42302...)
├── Analitiskas-metodes_2024.pdf            # Course Source S-ANALIT (SHA-256: 9d1aeafeb...)
├── B03_source_adjudication.md              # Detailed course-conflict adjudication (13,804 B)
├── B04_search_privacy_adjudication.md      # Search index privacy & leak audit (7,445 B)
├── B05_svg_duplication_responsive_audit.md # SVG deduplication & layout audit (23,046 B)
├── build/
│   ├── build_doc.py                        # Master builder (stitches sections, css, js, data)
│   ├── style.css                           # Canonical stylesheet (55,985 B; 1,939 lines)
│   ├── app.js                              # Canonical client runtime (40,792 B; 768 lines)
│   ├── sections/                           # 19 modular HTML chapter fragments (00_front .. 16_ch16, 98, 99)
│   ├── figures/                            # 12 standalone plot SVGs + glassware.html (9 vessel SVGs)
│   ├── gen_figures.py                      # Deterministic Python SVG generator
│   ├── sources.json                        # Cryptographically pinned source register (7 sources)
│   ├── claims.json                         # Verified claim ledger (C01–C20)
│   ├── concepts.json                       # 121 examinable concepts mapped to chapters
│   ├── counts.json                         # Derived DOM metric record (tables, figures, svgs, etc.)
│   ├── sigfig_cases.json                   # 23 Decimal-verified significant-figure cases
│   ├── graph_cases.json                    # Static cases for graph reading
│   ├── verified.json                       # Ground-truth numeric parameters
│   └── check_*.py                          # Topic-specific mathematical & route validators
├── docs/governance/
│   ├── ARCH_CSS_DOM_CONTRACTS.md           # Token tiers, layer rules, DOM class registry
│   ├── OPEN_ISSUES_LEDGER.md               # Active issue forensics & closure trail
│   ├── TERMINOLOGY_AND_SOURCES.md          # Metrological dictionary & S1–S23 conflicts
│   ├── INFRA_PYTHON_TS_JS_AUDIT.md         # Runtime allocations, TS contracts, migration map
│   └── CHANGELOG_ARCHIVE.md                # Historical run rotation & ledger
├── tools/                                  # Independent automated verification gates
│   ├── check_anchors.py                    # Validates all 524 IDs, 706 links, aria refs, h1..h6
│   ├── check_budget.py                     # Enforces JS size/lines/ratio & AGENTS byte limits
│   ├── check_contrast.py                   # Computes WCAG 2.2 AA contrast across token tiers
│   ├── check_counts.py                     # Fails on drift between DOM counts and build/counts.json
│   ├── check_figure_style.py               # Guards against per-SVG <style> block duplication
│   ├── check_font_glyphs.py                # Verifies cmap coverage of embedded WOFF2 fonts
│   ├── check_index_privacy.py              # Confirms zero recall answers leak into search index
│   ├── check_pillars.py                    # Evaluates 5-pillar pedagogical coverage across 121 concepts
│   ├── check_selfcontained.py              # Prohibits external URLs & network APIs
│   ├── check_sources.py                    # Validates claims against pinned sources
│   ├── derive_counts.py                    # Scans master DOM to produce counts.json
│   └── make_manifest.py                    # Produces cache manifest of all project files
└── workspace_skills/                       # 36 specialized workspace skills & design manual
```

### 2.2 Workspace Skills Inventory

The workspace includes 36 curated skills in `workspace_skills/` and global configurations. The following 10 specialized skills directly govern the pedagogical, visual, and architectural work packages in this roadmap:

| Skill Identifier | Primary Location | Pedagogical / Architectural Governance Role |
|---|---|---|
| `blueprint-spec-sheet` | `workspace_skills/blueprint-spec-sheet` | Governs laboratory apparatus datasheets, tolerance callouts, and dimensional specification blocks in Chapters 4–5. |
| `cognitive-deload-auditor` | `workspace_skills/cognitive-deload-auditor` | Evaluates extraneous cognitive load, fragmented prose, split-attention effects, and active-recall pacing. |
| `lexicon-morphology-weaver` | `workspace_skills/lexicon-morphology-weaver` | Structures bilingual Latvian–English metrological vocabulary with aligned morphology rails (roots, affixes, suffixes). |
| `mook-visual-compendium` | `workspace_skills/mook-visual-compendium` | Drives high-density micro-grid synthesis spreads for quick-reference summaries and exam revision packets. |
| `pdf-vector-surgeon` | `workspace_skills/pdf-vector-surgeon` | Formats multi-column printable reference sheets, vector diagram scales, and page-by-page typographic baselines. |
| `print-css-alchemist` | `workspace_skills/print-css-alchemist` | Governs dual-target screen/print CSS: `@media print`, running headers, forced light themes, and disclosure unrolling. |
| `state-scrubber-lab` | `workspace_skills/state-scrubber-lab` | Guides interactive, multi-stage state-machine scrubbing for burette meniscus reading and volumetric dilution stages. |
| `svg-spatial-occlusion` | `workspace_skills/svg-spatial-occlusion` | Drives spatial occlusion recall masks and anatomical/apparatus pin identification on laboratory equipment SVGs. |
| `synoptic-matrix-architect` | `workspace_skills/synoptic-matrix-architect` | Replaces fragmented equipment descriptions with an interactive, filterable synoptic comparison matrix. |
| `tufte-margin-scholar` | `workspace_skills/tufte-margin-scholar` | Formats long-form academic prose with aligned margin sidenotes, eliminating jarring modal popovers. |

### 2.3 File-by-File Inspection Ledger

| File / Asset Path | Role in Workspace | Inspected? | Tested? | Key Evidence & Findings | Coverage Limitations |
|---|---|---|---|---|---|
| `Master_2_tema_merijumi_un_grafiki.html` | Shipped production deliverable | Full | `[TESTED]` | 969,738 B; SHA-256 `35819d73...`; 16 chapters, 84 tables, 13 figures, 22 SVGs, 178 `<details>`, 524 IDs, 1 executable script (41,938 B; 770 L). | Screen-reader and live user interaction unmeasured. |
| `AGENTS.md` | Primary contract & issue routing hub | Full | `[TESTED]` | 18,932 B (within 24,576 B hard ceiling). 11 active issues; verified links to governance shards. | Governance specification; not runtime proof by itself. |
| `build/build_doc.py` | Python document assembler | Full | `[INSPECTED]` | 21,061 B. Inlines section fragments, compiles styles, injects data tables via `figure_data.py`, links glossary terms. | Build side-effects not triggered during audit. |
| `build/style.css` | Production stylesheet source | Full | `[TESTED]` | 55,985 B; 1,939 L. `@layer` declared but bodies unwrapped; passes WCAG 2.2 AA in `tools/check_contrast.py`. | Mobile viewport reflow verified via code inspection only. |
| `build/app.js` | Production client script source | Full | `[TESTED]` | 40,792 B; 768 L. Zero HTML injection primitives (`innerHTML`, `document.write`). Over budget by 36,696 B. | Browser headless smoke test passes; TS contract absent. |
| `build/sections/00_front.html` .. `16_ch16.html` | 17 Chapter content fragments | Full | `[TESTED]` | 121/121 concepts verified by `tools/check_pillars.py`. All chapter anchors resolve cleanly via `tools/check_anchors.py`. | None; all 17 chapter sources read. |
| `build/sections/98_quickref.html`, `99_footer.html` | Quickref & provenance fragments | Full | `[INSPECTED]` | Chapter 98 houses 33 canonical bindings; Chapter 99 houses source colophon and count metrics. | None. |
| `build/figures/*.svg` (12 files) | Generated vector figures | Full | `[TESTED]` | 12 files; verified by `tools/check_figure_style.py` (0 inline `<style>` tags; 15 scoped document rules; all have `<title>` & `<desc>`). | Falkon paints container but not inner geometry. |
| `build/figures/glassware.html` | 9 laboratory vessel SVGs | Full | `[INSPECTED]` | 9 vessel SVGs with shared `.vessel-art` styling. Fully vector-drawn (burette, pipettes, flasks, cylinders). | Exact volumetric scale is schematic, not photometric. |
| `build/sources.json` | Pinned source metadata | Full | `[TESTED]` | 7 sources registered with SHA-256 hashes and snippet verification levels. Passes `tools/check_sources.py`. | External ISO/VIM standards cited as references, not files. |
| `build/claims.json` | Formal claim ledger (C01–C20) | Full | `[TESTED]` | 20 claims registered; C19 closed (LNHB+NuDat); C20 open (521 nm reagent). Passes `tools/check_sources.py`. | C20 awaits lecturer resolution. |
| `build/concepts.json` | 121 Concept-to-Chapter index | Full | `[TESTED]` | 121 concepts mapped to chapters; verified 100% presence by `tools/check_pillars.py`. | None. |
| `build/counts.json` | Ground-truth DOM counts | Full | `[TESTED]` | 84 tables, 13 figures, 22 SVGs, 178 details, 524 IDs, 194 recall answers, 4 answer sheets. Validated by `check_counts.py`. | None. |
| `build/sigfig_cases.json` | Significant-figure test data | Full | `[TESTED]` | 23 cases verified with `Decimal`. `check_sigfig_cases.py` flags missing `sftCases` in `app.js`. | Check script needs updating to static table architecture. |
| `tools/check_budget.py` | Script & AGENTS budget gate | Full | `[TESTED]` | Correctly detects JS-01 failure (41,938 B > 4,096 B; 770 L > 100 L; 4.33% > 2.0%). | None. |
| `tools/check_contrast.py` | WCAG 2.2 AA contrast gate | Full | `[TESTED]` | Passes all light/dark token pairs (ink on ground 14.96:1; accent 6.64:1; rule 7.47:1). | Measures defined tokens; does not crawl raw computed styles. |
| `tools/check_font_glyphs.py` | Embedded WOFF2 cmap gate | Full | `[TESTED]` | Decodes 5 embedded fonts; confirms all 176 requested characters present including mathematical symbols. | None. |
| `tools/check_index_privacy.py` | Search index privacy gate | Full | `[TESTED]` | 1,092 blocks derived; 229,327 B searchable text; 0 closed recall answers leaked into search index. | None. |
| `tools/check_selfcontained.py` | Zero network dependency gate | Full | `[TESTED]` | Validates master has 0 external scripts, links, images, or network APIs. 13 W3C URIs permitted. | None. |
| 5 Course Source PDFs | Governing curriculum inputs | Full | `[TESTED]` | Cryptographic hashes verified; exact page citations extracted via `pdftotext -layout`. | Read-only curriculum boundary; not external standards. |

---

## 3. Diagnostic Triage: Confirmed Defects vs. Suspected Risks vs. Pedagogical/Design Opportunities

### 3.1 Category 1: Confirmed Defects (`[TESTED]` / `[INSPECTED]`)

1. **JS-01: Client Script Budget Breach (`[TESTED]`):**
   - *Location:* `Master_2_tema_merijumi_un_grafiki.html` (lines 1482–2252) and `build/app.js` (lines 1–768).
   - *Evidence:* `python3 -I tools/check_budget.py` fails with: script bytes 41,938 > 4,096; script lines 770 > 100; script ratio 4.325% > 2.000%.
   - *Mechanism:* Although finite trainer case arrays were excised in JS-06, `app.js` still contains complete bespoke calculation runners (`runSf`, `calRun`, `runHl`, `runSol`), DOM search indexing (`buildIndex`, `runSearch`), and theme toggling logic written as monolithic JavaScript rather than compiled from strict TypeScript into a minimal micro-runtime.
2. **INFRA-01: Missing TypeScript Build Pipeline (`[TESTED]`):**
   - *Location:* Root workspace and `build/`.
   - *Evidence:* `which tsc` returns non-zero; no `tsconfig.json` or `ts/` directory exists. The project violates Tier 3 of the language stack contract by authoring residual client logic directly in loose JavaScript.
3. **Build Tooling Regression in `check_sigfig_cases.py` (`[TESTED]`):**
   - *Location:* `build/check_sigfig_cases.py` (lines 142–156).
   - *Evidence:* Running `python3 -I build/check_sigfig_cases.py --check` exits with code 1: `1 app.js/JSON alignment failure(s): app.js: sftCases block not found`.
   - *Mechanism:* The checker still asserts that `sftCases` must reside inside `app.js`, failing to reflect the approved JS-06 architectural decision that moved trainer cases into static HTML tables in Chapter 8.
4. **HTML-08: Quoted Source Capitalization Discrepancy in S11 (`[INSPECTED]`):**
   - *Location:* `build/sections/04_ch4.html` vs `Analitiskas-metodes_2024.pdf` page 6.
   - *Evidence:* Course source Analit. p. 6 literally prints «10 ml», whereas normalized workspace markup converts this to «10 mL» without preserving the verbatim source attribute `data-quote="true"`.
5. **HTML-06 / C20: Unresolved Chromogenic Reagent at 521 nm (`[INSPECTED]`):**
   - *Location:* `build/claims.json` (Claim C20) and `build/sections/10_ch10.html`.
   - *Evidence:* 2A Q5 and 2026 Q7 specify ascorbic acid assay at 521 nm, but neither textbook nor slides name the chromogenic complexing reagent (e.g., 2,4-dinitrophenylhydrazine or ferric complexes). Marked as `open` in `build/claims.json`.

### 3.2 Category 2: Suspected Risks & Diagnostic Investigations (`[INFERRED]` / `[UNVERIFIED]`)

1. **HTML-10: SVG Vector Geometry Paint Failure in Falkon (`[UNVERIFIED]`):**
   - *Location:* All 12 plot SVGs (`build/figures/*.svg`).
   - *Evidence:* Inspection of PNG screenshots generated via Falkon (`webshot` / `lite-shot`) reveals that while `.figure-scroll` container boundaries and text labels render, vector curve paths and data dots fail to paint under QtWebEngine virtual X11 contexts.
   - *Risk:* Visual verification cannot be confirmed without a verified rendering engine; students using lightweight WebKit/QtWebEngine browsers may see blank graph boxes.
2. **HTML-04: Interactive Touch Targets & Screen-Reader Semantics (`[UNVERIFIED]`):**
   - *Location:* Interactive summary controls, search input, and popover buttons in `Master_2_tema_merijumi_un_grafiki.html`.
   - *Evidence:* Static contrast passes WCAG AA, but physical touch targets ($<44\text{px}$ on mobile), tab-index order, keyboard focus loops in popovers, and screen-reader announcements (`aria-live`) have not been audited with assistive technology.
3. **HTML-09: Print Layout & Multi-Page Pagination Review (`[UNVERIFIED]`):**
   - *Location:* `@media print` rules in `build/style.css` and 148-page print export.
   - *Evidence:* A historical 148-page PDF export exists, but full page-by-page visual review of table row splits, page breaks inside `.plate` figures, and running header/footer alignment remains unverified.
4. **CSS-01: Unwrapped Rule Bodies in Cascade Layers (`[INSPECTED]`):**
   - *Location:* `build/style.css` (lines 1–15).
   - *Evidence:* `@layer reset, tokens, base, layout, components, utilities, print;` is declared at line 1, but rule bodies are left unwrapped because legacy Falkon drops rules wrapped in `@layer` blocks. The workspace currently relies on source-order cascade rather than true CSS layer encapsulation.
5. **JS-08: Progressive Enhancement Completeness (`[TESTED]`):**
   - *Location:* `Master_2_tema_merijumi_un_grafiki.html`.
   - *Evidence:* The document contains 1 `<noscript>` tag, 0 `<dialog>` elements, and 60 `popover` triggers. Complete zero-JS usability of calculators and search fallbacks requires systematic automated verification.

### 3.3 Category 3: Pedagogical & Design Opportunities

1. **Titration & Dilution State Scrubbers (`state-scrubber-lab`):**
   - *Opportunity:* Replace static descriptions of burette drainage and volumetric flask dilution with deterministic, zero-JS or minimal SVG phase scrubbers showing exact liquid levels, meniscus geometry, and calculated concentration deltas.
2. **Filterable Laboratory Apparatus Synoptic Matrix (`synoptic-matrix-architect`):**
   - *Opportunity:* Elevate the 9 laboratory vessels in Chapter 4 from sequential cards into a unified, filterable synoptic matrix comparing capacity, manufacturer tolerance, thermal resistance, and primary clinical metrology purpose.
3. **Morphological Terminology Rails (`lexicon-morphology-weaver`):**
   - *Opportunity:* Break down intimidating Greek/Latin clinical chemistry roots (e.g., *spektro-*, *fotometrija*, *menisks*, *alikvots*, *titrēšana*) into bilingual morphological rails to enhance active vocabulary retention.
4. **Tufte-Style Margin Scholarly Annotations (`tufte-margin-scholar`):**
   - *Opportunity:* Migrate technical metrological side-notes, historical SI redefinition details, and clinical safety warnings from inline alert boxes into clean, non-disruptive margin sidenotes on desktop viewports.

---

## 4. Domain Terminology, Fact, Applicability & Warrant Verification Ledger

### 4.1 Evidentiary Warrant Protocol Evaluation
Every claim in this ledger is evaluated across the four mandatory warrant questions (§8.3):
1. **Scope & Context Alignment:** Does the governing authority apply to the exact same physical system, concentration regime, and measurement scale?
2. **Applicability & Boundary Conditions:** Are all environmental assumptions (temperature, pressure, optical path length, dilution thresholds) explicitly stated and satisfied?
3. **Sufficiency of Evidentiary Warrant:** Does the cited evidence prove the entire statement or merely a necessary condition?
4. **Contradiction Check:** Does any authoritative standard or textbook contradict the claim?

### 4.2 Claim & Terminology Verification Table

| Claim ID | Location (`file:line`) | Existing Workspace Claim | Verification Status | Applicability & Warrant Analysis | Authoritative Citation | Confidence | Proposed Correction / Disposition |
|---|---|---|---|---|---|---|---|
| **C01** | `build/sections/01_ch1.html`:14 | Topic description defines five intended learning outcomes (O1–O5). | **Verified** | Passes all 4 warrant checks. Governs curriculum boundaries; does not determine exam weighting. | `S-TOPIC` (2. Temata apraksts, 1. lpp.) | `[TEXT-VERIFIED]` (C) | Retained. Validated by `check_canonical.py`. |
| **C02** | `build/sections/01_ch1.html`:38 | Introductory and final tests require 55% score to pass. | **Verified** | Curriculum policy boundary. Does not imply letter grades. | `S-TOPIC` (2. Temata apraksts, 1. lpp.) | `[TEXT-VERIFIED]` (C) | Retained. Labelled as course assessment policy. |
| **C03** | `build/sections/02_ch2.html`:22 | Course requires SI prefixes: milli-, micro-, nano-, kilo-, mega-, giga-. | **Verified** | Contextually aligned with course syllabus. Does not cover 2022 BIPM additions (ronna, quetta). | `S-ANALIT` (Analītiskās metodes, 7. lpp.) | `[TEXT-VERIFIED]` (C) | Retained. Note added distinguishing course scope from full SI scale. |
| **C04** | `build/sections/02_ch2.html`:54 | SI unit for amount of substance $n$ is mole ($	ext{mol}$). | **Verified** | Definitionally complete under post-2019 SI defining constants ($N_{\text{A}} = 6.02214076\cdot 10^{23}\text{ mol}^{-1}$). | BIPM SI Brochure (9th ed., 2019); `S-ANALIT` p. 7 | `[TEXT-VERIFIED]` (C) | Retained. Obsolete symbol $v$ and $C_M$ replaced with $n$ and $c(B)$. |
| **C05** | `build/sections/03_ch3.html`:18 | Direct measurement reads scale; indirect calculates $y = f(x_1, \dots, x_n)$. | **Verified** | Fully aligns with JCGM 200:2012 (VIM 3) measurement models. | JCGM 200:2012 §2.1; `S-ANALIT` p. 1 | `[METADATA-VERIFIED / SCOPE-ALIGNED]` (C) | Retained. Explanatory functional form verified. |
| **C06** | `build/sections/03_ch3.html`:45 | Amount of substance relates to mass via $n = m/M$ ($m = n\cdot M$). | **Verified** (Corrected) | Mathematical identity. Source defect S4 used obsolete notation $v$. | `S-ANALIT` p. 1; IUPAC Green Book §2.10 | `[TEXT-VERIFIED]` (C) | Retained with explicit source correction note (S4). |
| **C07** | `build/sections/03_ch3.html`:82 | Beer–Lambert law is $A = \varepsilon\cdot l\cdot c$; $A$ is absorbance (dimensionless). | **Verified** (Corrected) | Source S5 used $a$ and termed $A$ "absorbcija". Absorbance is logarithmic optical quantity; absorption is physical process. | IUPAC Gold Book B00626; `S-ANALIT` p. 1 | `[METADATA-VERIFIED / SCOPE-ALIGNED]` (C) | Retained. Symbol $\varepsilon$ specified with units $\text{L}\cdot\text{mol}^{-1}\cdot\text{cm}^{-1}$; $A$ strictly defined. |
| **C08** | `build/sections/06_ch6.html`:12 | Precision is scatter of replicates; repeatability is precision under identical conditions. | **Verified** (Corrected) | Source S6 claimed repeatability is "scatter around true value" (conflating with trueness/bias). | ISO 5725-1:1994 §3.12; JCGM 200:2012 §2.15, §2.21 | `[METADATA-VERIFIED / SCOPE-ALIGNED]` (C) | Retained. Full distinction between trueness (*pareizība*) and precision (*precizitāte*) enforced. |
| **C09** | `build/sections/04_ch4.html`:90 | Class B volumetric apparatus has 0.5% tolerance of nominal volume. | **Over-simplified** (Course Rule) | Scope is strictly an RSU course pedagogical convention (S7). Real ISO 1042/4788 Class B tolerances vary by capacity. | `S-ANALIT` p. 3; ISO 1042:1998; ISO 4788:2005 | `[TEXT-VERIFIED]` (H/V) | Retained as course rule (`avotā`), but explicitly annotated with real ISO capacity tables. |
| **C10** | `build/sections/07_ch7.html`:30 | Addition: $10.05\text{ g} + 150.95\text{ g} = 161.00\text{ g}$ (2 decimal places). | **Verified** | Arithmetic exact. Governed by least number of decimal places (2 d.p.). | `S-2026` Q1 p. 1; Skoog et al. (10th ed.) Ch. 6 | `[TEXT-VERIFIED]` (C) | Retained. Recomputed with Python `Decimal`. |
| **C11** | `build/sections/07_ch7.html`:65 | Multiplication: $1.50\text{ mol/L} \cdot 98.00\text{ g/mol} = 147\text{ g/L}$ (3 sig figs). | **Verified** | Least significant figures is 3 (from $1.50$). Intermediate unrounded is $147.0000$. | `S-2026` Q4c p. 2; Harris (10th ed.) Ch. 3 | `[TEXT-VERIFIED]` (C) | Retained. Intermediate and final rounding steps shown. |
| **C12** | `build/sections/07_ch7.html`:110 | Titre readings $12.50, 13.05, 12.55\text{ mL}$ average to $12.70\text{ mL}$; $13.05$ cannot be rejected. | **Verified** | Dixon's $Q$-test: $Q_{\text{calc}} = 0.50/0.55 = 0.909 < Q_{\text{crit}}(3; 95\%) = 0.941$. Outlier cannot be discarded. | `S-2026` Q3 p. 1; Rorabacher, Anal. Chem. 1991 | `[TEXT-VERIFIED]` (C) | Retained. Full Dixon test verification displayed. |
| **C13** | `build/sections/07_ch7.html`:145 | Density unit conversion: $0.50\text{ g/mL} = 500\text{ g/L} = 5.0\cdot 10^2\text{ g/L}$ (2 sig figs). | **Verified** | Conversion factor $1000\text{ mL/L}$ is exact definition; precision limited by $0.50$ (2 sig figs). | `S-2026` Q4b p. 2 | `[TEXT-VERIFIED]` (C) | Retained. Ambiguous bare integer $500$ rewritten as $5.0\cdot 10^2\text{ g/L}$. |
| **C14** | `build/sections/04_ch4.html`:120 | Ranking vessels by purpose and error origin; Q5 blank key in course PDF. | **Verified** | Source S19 left Q5 blank. Workspace suggested ranking is pedagogical addition (`papildinājums`). | `S-2026` Q5 p. 2; `S-2B` Q1/Q6 | `[TEXT-VERIFIED]` (H) | Retained. Clearly labelled as editorial solution, not course key. |
| **C15** | `build/sections/05_ch5.html`:40 | Burette delivered volume: $V_{\text{final}} - V_{\text{initial}}$; $25\text{ mL}$ burette requires refilling for large volumes. | **Verified** | Practical metrology rule. Source S22 noted cumulative delivery exceeding capacity. | `S-2B` Q2 p. 3; Skoog et al. Ch. 2 | `[TEXT-VERIFIED]` (C) | Retained. Worked refill procedure highlighted. |
| **C16** | `build/sections/12_ch12.html`:25 | $\text{NaCl}$ solution density vs mass fraction $w$ and temperature; graphical interpolation in 2B Q3. | **Verified** | Valid across $0\%–12\%$ $w$ at $20\,^\circ\text{C}$ (linear fit $\rho = 0.0073\cdot w + 0.9979$). | `S-2B` Q3 p. 4; CRC Handbook (104th ed.) | `[TEXT-VERIFIED]` (C) | Retained. Linear domain limits ($0\le w \le 10\%$) strictly bounded. |
| **C17** | `build/sections/10_ch10.html`:30 | Calibration curve at 521 nm: 6 standards; citron sample ($A=0.982$) is extrapolated. | **Verified** | Calibration range is $A \in [0.168, 0.975]$ ($\rho \in [5.0, 30.0]\text{ mg/L}$). $A=0.982 > 0.975$ exceeds upper standard. | `S-2026` Q7 pp. 4–5; `S-2A` Q5 | `[TEXT-VERIFIED]` (C) | Retained. Extrapolation hazard and lack of verified linear limit emphasized. |
| **C18** | `build/sections/11_ch11.html`:20 | Mercury-203 course half-life value is $46.595\text{ days}$. | **Verified** (Course Datum) | Internal consistency: curve shows halving at $t \approx 46.6, 93.2, 139.8\text{ d}$. Course datum preserved. | `S-2026` Q8 p. 6; `S-2A` Q6 | `[TEXT-VERIFIED]` (C) | Retained as authentic course datum (`avotā`), paired with primary evaluations. |
| **C19** | `build/sections/11_ch11.html`:45 | Primary evaluated half-life for $^{203}\text{Hg}$: LNHB $46.594(12)\text{ d}$; NuDat/ENSDF $46.610(10)\text{ d}$. | **Verified** (Closed) | Both primary nuclear decay evaluations directly inspected via PDF/text extractions. | LNHB Table de Radionucléides (2004); Kondev, NDS 177, 509 (2021) | `[TEXT-VERIFIED]` (C) | Closed in 2026-11-07 audit. Displayed alongside course value without overwriting course key. |
| **C20** | `build/sections/10_ch10.html`:15 | Chemical identity of the chromogenic complexing reagent giving absorption at 521 nm. | **Unverified** (Open) | Ascorbic acid is colorless in visible spectrum (UV absorption at $\sim 245\text{ nm}$). Visible absorption requires chromogen. | Course PDFs silent; Analit. Q5, 2026 Q7 silent | `[UNVERIFIED]` (V) | **Stays OPEN.** Documented as an explicit inquiry for course faculty. No reagent invented. |

---

## 5. Authoritative Book, Standard & Literature Bibliography

In strict adherence to §4.2 and §8.5, all citations are catalogued with complete bibliographic metadata and honest provenance classifications:
- `[TEXT-VERIFIED]`: Direct inspection of the passage in accessible digital text, open repository, or local workspace files.
- `[METADATA-VERIFIED / SCOPE-ALIGNED]`: Catalog metadata, edition, publisher, and chapter scope verified, and underlying concept checked via authoritative primary sources, without asserting inspection of physical print pages.

### 5.1 Local Course Authorities (Primary Pedagogical Baseline)

1. **Rīgas Stradiņa universitāte (RSU).** (2020). *2. Temata apraksts: Mērījumi un aprēķini, laboratorijas trauki, grafiskās metodes medicīniskajā ķīmijā* [Course Syllabus & Topic Specification]. Cilvēka fizioloģijas un bioķīmijas katedra. 2 pp.  
   - *Provenance:* `[TEXT-VERIFIED]` Workspace file `2_Temata apraksts 2020.docx.pdf` (SHA-256: `c7d423021bc7f661a4b1f35c4e731a9c06101d60791b54ee24c7c3aa7110ede5`).  
   - *Scope:* Intended learning outcomes (O1–O5), 55% passing threshold, topic examination criteria.
2. **Rīgas Stradiņa universitāte (RSU).** (2024). *Analītiskās metodes medicīniskajā ķīmijā* [Lecture & Laboratory Theoretical Compendium]. Cilvēka fizioloģijas un bioķīmijas katedra. 7 pp.  
   - *Provenance:* `[TEXT-VERIFIED]` Workspace file `Analitiskas-metodes_2024.pdf` (SHA-256: `9d1aeafebc4f85a177119169560b31b48b2413a6e183c3fe4da4fe03ec7d896a`).  
   - *Scope:* SI units, prefixes, Beer–Lambert law, error definitions, significant figures, vessel accuracy conventions. Contains course defects S1–S11, S23.
3. **Rīgas Stradiņa universitāte (RSU).** (2025). *2A. Mērījumu precizitāte un grafiskās metodes ķīmijā* [Laboratory Worksheet 2A]. Cilvēka fizioloģijas un bioķīmijas katedra. 4 pp.  
   - *Provenance:* `[TEXT-VERIFIED]` Workspace file `2A_SEM_MCh_LV_Merijumi,grafiki_2025.pdf` (SHA-256: `319dfef6e821b934005d8fa42301580fb5747ab456ae291fe5d95a57a628a00a`).  
   - *Scope:* Titration replicate problems, calibration problems, ascorbic acid assay, $^{203}\text{Hg}$ half-life curves.
4. **Rīgas Stradiņa universitāte (RSU).** (2025). *2B. Laboratorijas trauku precizitāte un šķīdumu pagatavošana* [Laboratory Worksheet 2B]. Cilvēka fizioloģijas un bioķīmijas katedra. 4 pp.  
   - *Provenance:* `[TEXT-VERIFIED]` Workspace file `2B_SEM_MCh_LV_Trauki,skidumi_2025.pdf` (SHA-256: `894b5fa3db4e044a6b994b788d0ca13b8e2e3b21b163c60ac1928ebfc00f854c`).  
   - *Scope:* Laboratory glassware identification, meniscus alignment, burette titration procedure, solution preparation, $\text{NaCl}$ density curves.
5. **Rīgas Stradiņa universitāte (RSU).** (2026). *2. Laboratorijas aprīkojums. Mērīšana un grafiskās metodes ķīmijā: Atbildes* [Official Seminar Answer Key & Problem Set]. Cilvēka fizioloģijas un bioķīmijas katedra. 7 pp.  
   - *Provenance:* `[TEXT-VERIFIED]` Workspace file `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` (SHA-256: `bfe8fdd3da40d52084aa7f4d5c72253b0427fe74a2b27f00f2cd417a69980f5b`).  
   - *Scope:* Solutions for Q1–Q8 (Q5 blank). Contains course defects S12–S18.

### 5.2 International Metrological & Nomenclature Standards

6. **BIPM (Bureau International des Poids et Mesures).** (2019). *The International System of Units (SI)* [SI Brochure]. 9th edition. Sèvres: BIPM. ISBN 978-92-822-2272-0.  
   - *Provenance:* `[TEXT-VERIFIED]` Official digital repository (bipm.org).  
   - *Scope:* Defining constants of the SI ($h, e, k, N_{\text{A}}, \Delta\nu_{\text{Cs}}, c, K_{\text{cd}}$); rules for unit symbols, decimal markers, prefixes, and unit algebra.
7. **JCGM (Joint Committee for Guides in Metrology).** (2012). *International Vocabulary of Metrology — Basic and General Concepts and Associated Terms (VIM)* [JCGM 200:2012 / ISO/IEC Guide 99:2007]. 3rd edition (2008 version with minor corrections). Sèvres: JCGM.  
   - *Provenance:* `[TEXT-VERIFIED]` Official JCGM release.  
   - *Scope:* Sections 2.13 (measurement accuracy), 2.14 (measurement trueness), 2.15 (measurement precision), 2.16 (measurement error), 2.21 (repeatability), 2.26 (measurement uncertainty). Governs S6 and T03.
8. **ISO (International Organization for Standardization).** (1994). *Accuracy (trueness and precision) of measurement methods and results — Part 1: General principles and definitions* [ISO 5725-1:1994]. Geneva: ISO.  
   - *Provenance:* `[METADATA-VERIFIED / SCOPE-ALIGNED]` ISO Standards Catalog.  
   - *Scope:* Distinction between systematic error (trueness) and random error (precision); definitions of repeatability ($r$) and reproducibility ($R$).
9. **IUPAC (International Union of Pure and Applied Chemistry).** (2019). *Compendium of Chemical Terminology* [The "Gold Book"]. Compiled by A. D. McNaught and A. Wilkinson. Online version 2.3.3. Research Triad Park, NC: IUPAC. DOI: 10.1351/goldbook.  
   - *Provenance:* `[TEXT-VERIFIED]` IUPAC Gold Book entry B00626 ("Beer–Lambert law").  
   - *Scope:* Exact definition of absorbance $A = -\log_{10}(T)$, molar absorption coefficient $\varepsilon$ with units $\text{L}\cdot\text{mol}^{-1}\cdot\text{cm}^{-1}$ (or $\text{m}^2\cdot\text{mol}^{-1}$). Governs S5 and T02.

### 5.3 Primary Physical & Nuclear Data Evaluations

10. **LNHB (Laboratoire National Henri Becquerel).** (2004). *Table de Radionucléides: Hg-203* [Recommended Decay Data Evaluation]. Gif-sur-Yvette: CEA / LNHB / DDEP. 4 pp.  
    - *Provenance:* `[TEXT-VERIFIED]` Local workspace extract `build/source-text/LNHB_Hg-203_tables.pdf` (SHA-256: `522880c45c1767e7c858df3f6f17e0b5c1aa7e06b744040a45eafe1429944062`).  
    - *Scope:* Evaluated $^{203}\text{Hg}$ half-life: $T_{1/2} = 46.594(12)\text{ days}$. Validates C19.
11. **Kondev, F. G.** (2021). *Nuclear Data Sheets for A = 203*. Nuclear Data Sheets, 177, 509–856. Evaluated Nuclear Structure Data File (ENSDF / NuDat 3). DOI: 10.1016/j.nds.2021.10.002.  
    - *Provenance:* `[TEXT-VERIFIED]` Local workspace capture `build/source-text/NuDat_203HG_2021.txt` (SHA-256: `350e49df5e9f826ec89f7f48b8b09ff82729c11867dd11475cbe27fa5160fa11`).  
    - *Scope:* Adopted ENSDF value for $^{203}\text{Hg}$ half-life: $46.610(10)\text{ days}$. Validates C19.

### 5.4 Benchmark University Textbooks & Monographs

12. **Skoog, D. A., West, D. M., Holler, F. J., & Crouch, S. R.** (2014). *Fundamentals of Analytical Chemistry*. 9th edition. Belmont, CA: Brooks/Cole, Cengage Learning. ISBN 978-0-495-55828-6.  
    - *Provenance:* `[METADATA-VERIFIED / SCOPE-ALIGNED]` Library of Congress Control Number 2012946397.  
    - *Scope:* Chapter 2 (Chemicals, Apparatus, and Unit Operations), Chapter 5 (Calculations Used in Analytical Chemistry), Chapter 6 (Errors in Chemical Analyses), Chapter 7 (Random Errors in Chemical Analysis), Chapter 26 (Molecular Absorption Spectrometry).
13. **Harris, D. C., & Lucy, C. A.** (2020). *Quantitative Chemical Analysis*. 10th edition. New York, NY: W. H. Freeman and Company. ISBN 978-1-319-16430-0.  
    - *Provenance:* `[METADATA-VERIFIED / SCOPE-ALIGNED]` Publishers Weekly / Library of Congress 2019943242.  
    - *Scope:* Chapter 0 (The Analytical Process), Chapter 1 (Chemical Measurements), Chapter 3 (Experimental Error), Chapter 4 (Statistics), Chapter 5 (Quality Assurance and Calibration Methods).

---

## 6. Editorial Design ("Anti-AI-Slop"), Retexturing, Accessibility, Pedagogy & Complete SVG Inventory/Diagnostics

### 6.1 Operational Anti-AI-Slop Checklist (Appendix B Audit)

In accordance with Section 9.2 and Appendix B, each generic AI template pattern has been rigorously audited against the live stylesheet (`build/style.css`) and master markup:

| AI-Slop Pattern Indicator | Status in Workspace | Forensic Evidence from Source Inspection | Remediation / Task Binding |
|---|---|---|---|
| **1. Unmotivated neon or multi-stop gradients on surfaces** | `ABSENT` | `build/style.css` contains 0 instances of `linear-gradient` or `radial-gradient` on content cards. All surfaces use flat tokens (`--surface`, `--surface-2`). | Maintained under T15. |
| **2. Glassmorphism / backdrop-blur on text containers** | `ABSENT` | 0 occurrences of `backdrop-filter` in `build/style.css`. | Maintained under T15. |
| **3. Emoji used as structural UI icons** | `ABSENT` | Zero emoji are used as navigational cues or section bullets in `Master_2_tema_merijumi_un_grafiki.html`. Symbols are semantic Unicode or WOFF2 glyphs. | Maintained under T16. |
| **4. Uniform card grid fragmenting continuous reading** | `PRESENT` | Chapter 4 glassware and Chapters 8/9 trainer items historically fragmented long-form prose into repetitive cards. Glassware still utilizes `.vessel-grid`. | **Addressed by T16 & F08** (convert card grids to continuous prose and synoptic matrices). |
| **5. Hero banner / excessive whitespace above fold** | `ABSENT` | Header is a restrained, compact editorial masthead (`.chapter-head`) with immediate table of outcomes; no marketing hero banners. | Maintained under T16. |
| **6. Decorative animation with no instructional purpose** | `ABSENT` | 0 CSS `@keyframes` or transition effects on body elements; strictly honors `prefers-reduced-motion`. | Maintained under T15. |
| **7. Generic stock-photo / 3D-render aesthetic** | `ABSENT` | Zero raster stock photos or 3D renders; all diagrams are native vector SVGs or clean data tables. | Maintained under T08 & T11. |
| **8. Excessive border-radius / drop-shadows on text** | `ABSENT` | Box-shadows were eliminated in 2026-11-07 pass (HTML-03). Only functional overflow indicators (`.table-scroll.is-overflowing`) remain. Border-radius is restrained (`3px`–`6px`). | Maintained under T15. |
| **9. Color-only semantic encoding** | `PRESENT` | Certain callout boxes rely heavily on accent/red/green borders. Requires redundant visual cues (icons, distinct prefixes like `[MISTAKE]`, `[RULE]`, `[VERIFIED]`). | **Addressed by T16** (reinforce semantic badges with textual prefixes). |
| **10. Inconsistent spacing scale / typographic hierarchy** | `PRESENT` | Minor variations between hand-written chapter fragments in line-height and vertical margins (`1.4` vs `1.6`; margin rem steps). | **Addressed by T15** (unify spacing scale around `--space-1` .. `--space-9` tokens). |

### 6.2 Complete SVG & Visual Pedagogy Inventory (22 Figures)

Every inline `<svg>` in `Master_2_tema_merijumi_un_grafiki.html` has been inventoried, cross-checked against source generators, and classified:

| Figure ID & Chapter | Source / Generator | ViewBox & Wrapper | Title & Subject | Pedagogical Objective | Classification | Topological Constraints & Visual Criteria |
|---|---|---|---|---|---|---|
| **SVG-01** (Ch 2) | `build/figures/prefix-ladder.svg` (`gen_figures.py`) | `0 0 980 250` in `.figure-scroll` | Decimālo priedēkļu skala no nano līdz giga | Understand exponential scale factors from $10^{-9}$ to $10^9$ without confusing sign of exponent. | `[RETAIN]` | Horizontal ladder with logarithmic spacing; zero overlapping labels; distinct colors for micro ($10^{-6}$) vs milli ($10^{-3}$). |
| **SVG-02** (Ch 3) | `build/figures/calibration-scheme.svg` (`gen_figures.py`) | `0 0 820 410` in `.figure-scroll` | Kalibrēšanas shēma: absorbance $A$ pret koncentrāciju | Explain physical relationship $A = \varepsilon\cdot l\cdot c$ and optical path length. | `[CORRECT]` | Correct coefficient label from course $a$ to IUPAC $\varepsilon$; bound linear dynamic range. Forbidden: depicting non-zero absorbance at zero concentration without blank explanation. |
| **SVG-03** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Birete, 25 mL | Identify volumetric burette with stopcock, 0.1 mL graduations. | `[RETAIN]` | Straight bore, graduated markings increasing downward, stopcock at base. |
| **SVG-04** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Mora pipete, 25 mL | Identify single-mark volumetric transfer pipette with bulb. | `[RETAIN]` | Single graduation ring above bulb, tapered delivery jet. Forbidden: graduated lines along stem. |
| **SVG-05** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Mērpipete, 10 mL | Identify graduated measuring pipette (Mohr type). | `[RETAIN]` | Cylindrical tube with multiple graduation lines along entire length. |
| **SVG-06** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Mērkolba, 100 mL | Identify volumetric flask with single calibration mark. | `[RETAIN]` | Flat bottom, pear-shaped body, narrow neck with single circular graduation mark. |
| **SVG-07** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Mērcilindrs, 50 mL | Identify graduated measuring cylinder. | `[RETAIN]` | Heavy hexagonal or circular base, spout for pouring, coarse graduations. |
| **SVG-08** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Vārglāze, 100 mL | Identify beaker for mixing/heating (approximate volume only). | `[RETAIN]` | Cylindrical with spout; graduations explicitly marked "APROX". |
| **SVG-09** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Erlenmeijera kolba, 100 mL | Identify conical titration flask. | `[RETAIN]` | Conical body, cylindrical neck, suitable for swirling without splashing. |
| **SVG-10** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Mēģene | Identify test tube for qualitative reactions. | `[RETAIN]` | U-shaped bottom, ungraduated glass cylinder. |
| **SVG-11** (Ch 4) | `build/figures/glassware.html` (`gen_figures.py`) | `0 0 160 200` in `.vessel-grid` | Plastmasas pipete | Identify disposable Pasteur/transfer pipette. | `[RETAIN]` | One-piece plastic bulb with stem; non-volumetric. |
| **SVG-12** (Ch 5) | `build/figures/meniscus-parallax.svg` (`gen_figures.py`) | `0 0 980 545` in `.figure-scroll` | Meniska nolasīšana acu līmenī un paralakses kļūda | Teach correct sightline alignment at bottom of concave meniscus; show high/low sightline errors. | `[RETAIN]` | Three sightlines (too high $\rightarrow$ positive error; eye level $\rightarrow$ correct; too low $\rightarrow$ negative error). Clear concave curve. |
| **SVG-13** (Ch 5) | `build/figures/burette-readings.svg` (`gen_figures.py`) | `0 0 920 690` in `.figure-scroll` | Biretes trīs nolasījumi 0,00, 5,80 un 19,30 mL | Teach reading downwards from top zero mark on burette scales. | `[RETAIN]` | Numbered 0 to 25 downwards; liquid levels at exact points; bottom of curve aligned with graduations. |
| **SVG-14** (Ch 6) | `build/figures/target-plot.svg` (`gen_figures.py`) | `0 0 940 400` in `.figure-scroll` | Precizitāte un pareizība trijos mērķos | Disambiguate trueness (bullseye centering) from precision (tight clustering). | `[CORRECT]` | Target 1: high trueness, high precision; Target 2: low trueness, high precision; Target 3: low trueness, low precision. Ensure Target 2 explicitly demonstrates systematic offset. |
| **SVG-15** (Ch 6) | `build/figures/ci-coverage.svg` (`gen_figures.py`) | `0 0 640 300` in `.figure-scroll` | Ticamības intervālu pārklājums (10 intervāli) | Demonstrate frequentist interpretation of $95\%$ confidence interval (1 in 20 intervals misses $\mu$). | `[RETAIN]` | Ten horizontal intervals with center points; exactly one interval drawn in red failing to intersect vertical true mean $\mu$. |
| **SVG-16** (Ch 9) | `build/sections/09_ch9.html`:75 | `0 0 320 220` (inline markup) | Nolasīšanas ceļš: ass $\rightarrow$ līnija $\rightarrow$ otra ass | Procedural visual cue for graph interpolation. | `[REDESIGN]` | Hand-written vector currently lacks document token bindings. Integrate into `gen_figures.py` with full design token classes. |
| **SVG-17** (Ch 10) | `build/figures/calibration.svg` (`gen_figures.py`) | `0 0 900 590` in `.figure-scroll` | Askorbīnskābes kalibrēšanas grafiks | Linear calibration fit $A = 0.0322\cdot\rho + 0.0106$; 6 standards; patient samples. | `[CORRECT]` | Explicitly mark Citron ($A=0.982$) as extrapolation hazard. Label axes with full units ($A$, $\rho / (\text{mg/L})$). |
| **SVG-18** (Ch 10) | `build/figures/calibration-residuals.svg` (`gen_figures.py`) | `0 0 900 380` in `.figure-scroll` | Kalibrēšanas atlikumu grafiks | Show residual distribution $\Delta A_i = A_i - \hat{A}_i$ around zero line; prove $R^2$ alone is insufficient. | `[RETAIN]` | Zero baseline; six points with alternating residuals ($-0.0034, +0.0087, +0.0019, -0.0169, +0.0103, -0.0006$). |
| **SVG-19** (Ch 11) | `build/figures/half-life-Hg.svg` (`gen_figures.py`) | `0 0 900 580` in `.figure-scroll` | $^{203}\text{Hg}$ sabrukšanas līkne ar kāpnēm | First-order radioactive decay; successive halvings at $50\%$, $25\%$, $12.5\%$ at $t_{1/2} = 46.6\text{ d}$. | `[RETAIN]` | True exponential decay curve $N(t) = N_0 e^{-\lambda t}$; step-down horizontal/vertical dashed projection lines. |
| **SVG-20** (Ch 11) | `build/figures/half-life-hydrolysis.svg` (`gen_figures.py`) | `0 0 900 600` in `.figure-scroll` | Compounds X hidrolīzes līkne | Chemical first-order pseudo-decay showing successive halving intervals from non-zero initial concentrations. | `[RETAIN]` | Concentration vs time; proves constant half-life is independent of starting concentration. |
| **SVG-21** (Ch 11) | `build/figures/half-life-offset.svg` (`gen_figures.py`) | `0 0 980 650` in `.figure-scroll` | Absolūtais laiks un pagājušais laiks (offset) | Resolve S18 misconception: half-life calculation must subtract $t_0$ when starting from non-zero time origin. | `[RETAIN]` | Two panels: absolute time axis vs elapsed $\Delta t$ axis; validated by `check_half_life_offset.py`. |
| **SVG-22** (Ch 12) | `build/figures/density.svg` (`gen_figures.py`) | `0 0 900 600` in `.figure-scroll` | $\text{NaCl}$ blīvuma un masas daļas grafiks | Graphical determination of mass fraction $w$ from measured pycnometer density $\rho$. | `[CORRECT]` | Restrict plotted linear line strictly to $0\%–10\%$ $w$; show curvature inflection points at higher concentrations. |

---

## 7. 20 Core Improvement Tasks (T01–T20)

### T01 — Canonical Terminology Register, Lint and Morphological Nomenclature Hardening

- **Task ID & Decisive Title:** `T01` — Canonical Terminology Register, Lint and Morphological Nomenclature Hardening
- **Classification & Governance Block:**
  - *Workstream:* Terminology & Sourcing
  - *Priority:* P0 (Immediate Truth & Stability) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/check_terms.py` reports 6 open gates, 0 active syntax violations)
  - *Responsibility Boundary:* Owns canonical term dictionary (`build/terminology.json`), automated lint enforcement in `build/check_terms.py`, generation of bilingual glossary rows in `build/sections/14_ch14.html`, and morphological root breakdown rails. Interfaces with T02/T03 for metrological definitions and T19 for search exclusions.
  - *Applicable Workspace Skills:* `lexicon-morphology-weaver`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `build/sections/14_ch14.html` and across chapter fragments `01_ch1.html` through `16_ch16.html`, `build/check_terms.py --report` reveals 6 open editorial gates.
  - The phrase «drošības intervāls» appears in historical course text quotations (`Analitiskas-metodes_2024.pdf` p. 4) but is forbidden in modern clinical metrology where «ticamības intervāls» is canonical.
  - English translations in `.gloss` rows occasionally omit explicit `lang="en"` attributes, causing screen readers with Latvian TTS synthesizers to mispronounce English metrological terms.
  - Classical chemical terminology (e.g., *spektrofotometrija*, *menisks*, *ekstrapolācija*, *titrēšana*) lacks morphological decomposition, obscuring semantic Greek/Latin roots for medical students.
- **Why It Matters:**
  - Clinical medical students who conflate confidence intervals (*ticamības intervāls*) with safety intervals (*drošības intervāls*) or misread metrological terminology fail international licensure exams (USMLE, IFOM) and misunderstand reference interval statistics in laboratory medicine.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Strict term linter gating in `build/check_terms.py` passing with 0 open gates; 100% of English terms wrapped in `<span lang="en">`; bilingual morphological root breakout cards for key terms using `lexicon-morphology-weaver`; verbatim preservation of course defects inside `data-quote="true"` attributes.
  - *Out of Scope:* Rewriting primary source quotations from RSU lecture slides or changing faculty exam policy without documented confirmation.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* JCGM 200:2012 (VIM 3) §2.13–§2.26; IUPAC Gold Book; ISO 5725-1:1994; `build/claims.json` (Claims C04, C07, C08).
  - *Warrant Check:* All 4 warrant conditions passed. Terms govern quantitative clinical laboratory measurement where international standard definitions are unambiguous.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Source Audit & Schema Expansion:* Expand `build/terminology.json` to include mandatory `morphology` metadata (prefix, root, suffix, etymology) and strict `en_lang_verified: true` flags for every entry.
  2. *Linter Hardening:* Upgrade `build/check_terms.py` to assert that zero active teaching paragraphs contain forbidden terms outside `data-quote="true"`, and that every `.gloss` English span carries `lang="en"`.
  3. *Glossary Generation & Chapter Synchronization:* Re-render `build/sections/14_ch14.html` using `--write-glossary` and cross-link all 65 canonical terms to their primary introductory chapters.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T01.1: Morphological Rail Integration & Linter Verification*
    1. In `build/terminology.json`, enrich the 15 highest-frequency classical terms with morphological decomposition objects (`root`, `prefix`, `etymon_meaning`).
    2. In `build/check_terms.py`, implement an automated validation check asserting that `v_anchor` links in `build/sections/16_ch16.html` resolve to verified DOM targets.
    3. Run `python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --strict` and verify that active forbidden terms trigger exit code 1.
  - *Subtask T01.2: DOM Markup & Language Tag Refactor*
    1. In `build/sections/14_ch14.html`, replace all naked English text nodes inside `.gloss__en` containers with `<span lang="en">` elements.
    2. In `build/sections/06_ch6.html` and `07_ch7.html`, audit inline terms to ensure «pareizība» and «precizitāte» are never paired without their English qualifiers.
    3. Run `python3 -I tools/check_pillars.py` to confirm that all 65 glossary rows preserve their canonical term pillar mapping.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Existing Files:* `build/terminology.json`, `build/check_terms.py`, `build/sections/14_ch14.html`, `build/sections/16_ch16.html`.
  - *Selectors & Tokens:* `.gloss`, `.gloss__term`, `.gloss__en`, `.morph-rail`, `[data-quote="true"]`.
  - *Interfaces:* CLI flags `--strict`, `--report`, `--write-glossary` in `check_terms.py`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --report` outputs 0 schema errors and 0 active violations.
  - *Negative / Boundary Test:* Injecting «drošības intervāls» into an unquoted `<p>` in `06_ch6.html` causes `check_terms.py --strict` to exit 1 with line number.
  - *Accessibility / Language Check:* Grep across all section HTML files confirms zero instances of `class="en-term"` without `lang="en"`.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Upstream of T02, T03, T19; downstream of none.
  - *Collision Group / Risk:* Group A (Canonical Data & Chapter 14). Risk of desynchronizing chapter anchors.
  - *Rollback Plan:* Revert `build/terminology.json` and `build/sections/14_ch14.html` from git/cache baseline.
  - *Definition of Done:* `check_terms.py --strict` exits 0; all 6 open gates resolved or formally documented as lecturer policy holds; glossary renders clean morphological rails.

---

### T02 — Spectrophotometric Rigor: Absorbance Definition, Beer–Lambert Bounds, and Molar Absorptivity Units

- **Task ID & Decisive Title:** `T02` — Spectrophotometric Rigor: Absorbance Definition, Beer–Lambert Bounds, and Molar Absorptivity Units
- **Classification & Governance Block:**
  - *Workstream:* Terminology & Sourcing
  - *Priority:* P0 (Immediate Truth & Stability) | *Impact:* 5 | *Effort:* 2
  - *Epistemic Status:* `[TESTED]` (Claim C07 verified; `check_calibration.py --self-test` passes)
  - *Responsibility Boundary:* Owns spectrophotometric theory and worked examples in `build/sections/03_ch3.html` and `10_ch10.html`. Governs the distinction between optical absorbance $A$ and physical absorption, coefficient notation ($\varepsilon$ vs $a$), and linear dynamic range limits.
  - *Applicable Workspace Skills:* `blueprint-spec-sheet`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Analitiskas-metodes_2024.pdf` p. 1 (defect S5), the course source defines $A = a\cdot l\cdot c$, calling $A$ «gaismas absorbcija» and giving coefficient $a$ in non-SI units `1/mol·cm`.
  - In `build/sections/03_ch3.html` lines 82–104, while the correction is annotated, the prose must rigorously bound when $A = \varepsilon\cdot l\cdot c$ fails (high concentrations where $c > 0.01\text{ M}$, stray light, polychromatic radiation, refractive index shifts).
  - Open Claim C20: The course laboratory worksheet (2A Q5 / 2026 Q7) uses 521 nm for ascorbic acid determination without naming the chromogenic reagent that creates absorption at 521 nm.
- **Why It Matters:**
  - Medical students performing spectrophotometric clinical assays (e.g., hemoglobin derivatives, bilirubin, enzyme kinetics) who treat absorbance as a linear percentage or confuse process with quantity calculate false patient biomarker concentrations.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Explicit definition of absorbance $A = -\log_{10}(I/I_0) = \log_{10}(1/T)$ as a dimensionless logarithmic quantity; qualification of molar absorptivity $\varepsilon$ with standard units $\text{L}\cdot\text{mol}^{-1}\cdot\text{cm}^{-1}$; explicit derivation of linear dynamic range boundaries ($A \in [0.1, 1.0]$ for minimal photometric error); clear labeling of Claim C20 as an open faculty inquiry.
  - *Out of Scope:* Fabricating a specific chromogenic complex (e.g., 2,4-DNPH or phosphotungstate) for C20 without RSU course director confirmation.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* IUPAC Gold Book B00626; Skoog et al. (9th ed.) Chapter 26; `build/claims.json` (Claims C07, C17, C20).
  - *Warrant Check:* All 4 warrant conditions passed. Beer–Lambert law is conditionally exact only for monochromatic light in dilute solutions.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Theoretical Derivation Upgrade:* In `build/sections/03_ch3.html`, rewrite Section 3.4 with an aligned mathematical derivation linking transmittance $T = I/I_0$ to optical absorbance $A$, emphasizing why $A$ is dimensionless.
  2. *Chemical & Instrument Boundary Inoculation:* Insert a dedicated `.role--rule` callout detailing the physical limitations of the Beer–Lambert law and explaining why readings above $A > 1.0$ suffer from photometric detector noise.
  3. *Calibration Chapter Alignment:* In `build/sections/10_ch10.html`, annotate the 521 nm ascorbic acid calibration curve with an explicit disclaimer regarding the unknown chromogenic complex (Claim C20).
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T02.1: Mathematical & Conceptual Prose Refinement*
    1. In `build/sections/03_ch3.html`, update formula containers `.formula` to show $A = -\log_{10}(T) = \varepsilon\cdot b\cdot c$ alongside the historical course notation $a\cdot l\cdot c$.
    2. Add a comparison table contrasting absorbance $A$ (dimensionless property) with absorption (physical energy transfer process).
    3. Run `python3 -I build/check_calibration.py --self-test` to confirm mathematical guards remain intact.
  - *Subtask T02.2: Figure & Exercise Annotation*
    1. In `build/figures/calibration-scheme.svg`, verify axis label reads $A$ (dimensionless) and concentration axis shows explicit units $\text{mmol/L}$.
    2. In `build/sections/10_ch10.html`, insert an explanatory note on the Citron sample ($A = 0.982$) highlighting that it sits near the upper limit of photometric reliability.
    3. Run `python3 -I tools/check_pillars.py` to verify mechanism and common mistake pillars in Chapter 10.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/03_ch3.html`, `build/sections/10_ch10.html`, `build/figures/calibration-scheme.svg`, `build/claims.json`.
  - *Selectors:* `.calc--beer-lambert`, `.role--rule`, `.role--mistake`, `[data-claim="C07"]`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_calibration.py --self-test` exits 0 with `calibration self-test: equated slope rejected; bounded sentence kept`.
  - *Negative Test:* Introducing an assertion that $A$ has units $\text{L/mol}$ fails the terminology gate.
  - *Accessibility Check:* Mathematical formulas use semantic markup `<math>` or accessible text descriptions.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01; upstream of T06, T11, F07.
  - *Collision Group:* Group B (Spectrophotometry & Calibration).
  - *Rollback Plan:* Revert changes in `03_ch3.html` and `10_ch10.html` via git checkout.
  - *Definition of Done:* Absorbance strictly defined as dimensionless; Beer–Lambert boundaries codified; C20 clearly quarantined.

---

### T03 — Metrological Disambiguation: Trueness, Precision, Repeatability, and Measurement Uncertainty

- **Task ID & Decisive Title:** `T03` — Metrological Disambiguation: Trueness, Precision, Repeatability, and Measurement Uncertainty
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P0 (Immediate Truth & Stability) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (Claim C08 verified; VIM 2.20/2.21 alignment verified)
  - *Responsibility Boundary:* Owns Chapter 6 (`build/sections/06_ch6.html`) metrological concepts. Governs the formal disambiguation of trueness (*pareizība*), precision (*precizitāte*), error (*kļūda*), and uncertainty (*nenoteiktība*).
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `tufte-margin-scholar`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Analitiskas-metodes_2024.pdf` p. 2 (defect S6), the course defines repeatability as «pakāpe, kādā dati tiek izkaisīti ap patieso vērtību» (scattering around true value). This fatally confuses random dispersion (precision) with systematic deviation from a reference value (trueness).
  - In everyday Latvian, «precizitāte» is colloquially used for both closeness to target and mutual agreement of replicates.
  - In `build/sections/06_ch6.html`, while target diagrams exist, prose must rigorously inoculate students against the illusion that high precision implies correctness.
- **Why It Matters:**
  - A medical laboratory analyzer can produce tightly clustered replicate readings (high precision) that are completely calibrated to a faulty baseline, leading to systematic misdiagnosis of clinical conditions.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Codifying the 4-quadrant metrological model (trueness vs precision); explicit definitions matching ISO 5725-1 and VIM 3; clear distinction between error $\Delta x = x - x_{\text{ref}}$ (a single value, unknowable without true reference) and uncertainty $u(x)$ (an attributed distribution parameter).
  - *Out of Scope:* Requiring full ISO GUM (Guide to the Expression of Uncertainty in Measurement) partial derivative propagation matrices for first-year medical coursework.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* JCGM 200:2012 (VIM 3) §2.13–§2.26; ISO 5725-1:1994; `build/claims.json` (Claim C08).
  - *Warrant Check:* All 4 warrant conditions passed. Metrological terms are grounded in international consensus definitions.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Conceptual Matrix Construction:* In `build/sections/06_ch6.html`, construct an aligned $2\times 2$ comparative matrix contrasting High/Low Trueness with High/Low Precision, paired with clinical diagnostic analogies.
  2. *Target Figure Integration:* Synchronize the prose directly with `SVG-14` (`build/figures/target-plot.svg`), ensuring labels explicitly link each target to random error vs systematic error.
  3. *Error vs Uncertainty Inoculation:* Insert a dedicated `.role--rule` callout establishing that measurement error is a theoretical difference, whereas uncertainty is a quantifiable dispersion interval.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T03.1: Chapter 6 Prose & Table Refactor*
    1. In `build/sections/06_ch6.html`, insert a structured comparison table with columns: Term (LV), Term (EN), Definition, Cause, Quantitative Metric.
    2. Add bilingual English identifiers `<span lang="en">trueness</span>`, `<span lang="en">precision</span>`, `<span lang="en">repeatability</span>`, `<span lang="en">reproducibility</span>`.
    3. Run `python3 -I tools/check_pillars.py` to ensure Chapter 6 definition and mechanism pillars pass.
  - *Subtask T03.2: Target Plot Validation & Diagnostic Exercises*
    1. Cross-check `build/figures/target-plot.svg` coordinates to ensure Target 2 has tight grouping with a large offset from the center (systematic bias).
    2. Add two active-recall items in `06_ch6.html` asking students to diagnose instrument faults based on replicate cluster patterns.
    3. Run `python3 -I tools/check_anchors.py` to confirm all newly created recall IDs resolve cleanly.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/06_ch6.html`, `build/figures/target-plot.svg`, `build/concepts.json`.
  - *Selectors:* `.target-matrix`, `.role--rule`, `.role--mistake`, `#ch6-target-plot`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_pillars.py` reports Chapter 6 fully compliant across all 5 pillars.
  - *Negative Test:* Searching for «izkaisīti ap patieso vērtību» outside `data-quote="true"` returns 0 results.
  - *Visual Check:* Target SVGs render with unmistakable contrast between cluster centers and bullseye center.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01; upstream of T09, F03.
  - *Collision Group:* Group C (Metrology & Statistics).
  - *Rollback Plan:* Revert `06_ch6.html` to baseline copy.
  - *Definition of Done:* Trueness, precision, and repeatability disambiguated without ambiguity; target diagrams aligned with ISO 5725.

---

### T04 — Volumetric Glassware Classification, Specification Blocks, and Meniscus Reading Rigor

- **Task ID & Decisive Title:** `T04` — Volumetric Glassware Classification, Specification Blocks, and Meniscus Reading Rigor
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[INSPECTED]` (Glassware SVGs inspected; 9 vessels present in `build/figures/glassware.html`)
  - *Responsibility Boundary:* Owns Chapters 4 and 5 (`build/sections/04_ch4.html`, `05_ch5.html`), glassware SVG assets (`SVG-03` to `SVG-11`), and meniscus reading illustrations (`SVG-12`, `SVG-13`).
  - *Applicable Workspace Skills:* `synoptic-matrix-architect`, `blueprint-spec-sheet`, `state-scrubber-lab`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Analitiskas-metodes_2024.pdf` p. 3 (defect S7), Class B glassware error is generalized as a flat «0,5% no nominālās skalas vērtības» across all vessels. In real laboratory practice, ISO 1042 (volumetric flasks) and ISO 4788 (graduated cylinders) specify absolute tolerances that vary non-linearly with volume.
  - In `build/sections/04_ch4.html`, vessel descriptions are currently presented in sequential, repetitive card containers (`.vessel-grid > .vessel`), fragmenting continuous study.
  - Students frequently confuse volumetric pipettes (*Mora pipete*, single calibration ring) with graduated measuring pipettes (*mērpipete*).
- **Why It Matters:**
  - Selecting an inappropriate vessel (e.g., using a graduated measuring cylinder instead of a volumetric flask to prepare a standard solution) introduces unacceptable systematic error into clinical analyses.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Transforming the 9 vessel cards into an aligned engineering datasheet with standardized specification title blocks (`blueprint-spec-sheet`); codifying the distinction between TC (*to contain* / *In*) and TD (*to deliver* / *Ex*) calibration marks; qualifying the 0.5% rule as an RSU course convention while listing true ISO tolerances.
  - *Out of Scope:* Replacing standard laboratory glassware with automated electronic micropipettes outside the course curriculum.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* ISO 1042:1998; ISO 4788:2005; ISO 835:2007; `S-ANALIT` p. 3; `S-2B` Q1/Q6; `build/claims.json` (Claims C09, C14, C15).
  - *Warrant Check:* All 4 warrant conditions passed. Apparatus specifications reflect physical metrology standards.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Synoptic Matrix & Specification Block Implementation:* In `build/sections/04_ch4.html`, restructure the glassware inventory into a structured specification block incorporating vessel schematics, capacity, calibration type (TC vs TD), Class A/B tolerance, and primary medical laboratory purpose.
  2. *TC vs TD Operational Protocol:* In `build/sections/05_ch5.html`, provide a detailed step-by-step procedural guide on handling residue in pipettes (why blowout is prohibited on transfer pipettes unless marked with double frosted rings).
  3. *Meniscus Parallax Diagrammatic Reinforcement:* Link `SVG-12` and `SVG-13` directly to worked clinical case problems, showing exact numerical consequences of high vs low parallax errors.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T04.1: Glassware Specification Architecture*
    1. In `build/sections/04_ch4.html`, embed structured specification tables adjacent to each of the 9 vessel SVGs.
    2. Add explicit badges for calibration mode: `[TC / In]` for volumetric flasks and cylinders; `[TD / Ex]` for pipettes and burettes.
    3. Run `python3 -I tools/check_figure_style.py` to ensure glassware SVGs maintain zero inline `<style>` duplication.
  - *Subtask T04.2: Meniscus & Burette Titration Protocol*
    1. In `build/sections/05_ch5.html`, add an annotated breakdown of `SVG-13` detailing initial burette reading ($0.00\text{ mL}$), intermediate titre ($5.80\text{ mL}$), and final endpoint ($19.30\text{ mL}$).
    2. Add an explicit warning regarding burette refilling when total titration volume exceeds nominal capacity ($25\text{ mL}$).
    3. Run `python3 -I tools/check_anchors.py` to verify all glassware figure anchors resolve.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/04_ch4.html`, `build/sections/05_ch5.html`, `build/figures/glassware.html`.
  - *Selectors:* `.vessel-spec`, `.spec-block`, `.badge--tc`, `.badge--td`, `.meniscus-callout`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_pillars.py` confirms 100% concept coverage for Chapter 4 apparatus terms.
  - *Negative Test:* Searching Chapter 4 for unannotated 0.5% tolerance statements returns 0 matches (must carry course rule disclaimer).
  - *Accessibility Check:* All 9 glassware SVGs retain accessible `<title>` and `<desc>` elements matching `tools/check_figure_style.py`.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01; upstream of T14, F08.
  - *Collision Group:* Group D (Apparatus & Solutions).
  - *Rollback Plan:* Restore `04_ch4.html` and `05_ch5.html` from cache.
  - *Definition of Done:* All 9 vessels documented with specification blocks; TC/TD calibration clarified; parallax errors illustrated.

---

### T05 — Significant-Figure Arithmetic, Decimal Recomputations, and Test Suite Repair

- **Task ID & Decisive Title:** `T05` — Significant-Figure Arithmetic, Decimal Recomputations, and Test Suite Repair
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P0 (Immediate Truth & Stability) | *Impact:* 5 | *Effort:* 2
  - *Epistemic Status:* `[TESTED]` (`build/check_sigfig_cases.py --check` failed due to missing `sftCases` in `app.js`)
  - *Responsibility Boundary:* Owns significant-figure rules in Chapter 7 and 8 (`build/sections/07_ch7.html`, `08_ch8.html`), dataset `build/sigfig_cases.json`, and verification runner `build/check_sigfig_cases.py`.
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `tools/check_budget.py`.
- **Observed Problem & Concrete Workspace Evidence:**
  - Running `python3 -I build/check_sigfig_cases.py --check` currently exits 1: `1 app.js/JSON alignment failure(s): app.js: sftCases block not found`.
  - In the 2026-11-07 JS-06 product pass, dynamic trainer cases were moved out of `build/app.js` into static HTML tables in Chapter 8, but `build/check_sigfig_cases.py` was not updated to scan the static HTML table, leaving the automated build gate broken.
  - In `Analitiskas-metodes_2024.pdf` p. 5 (defect S9), the text conflates significant digits with decimal places: «divi zīmīgie cipari aiz komata».
  - In `Analitiskas-metodes_2024.pdf` p. 5 (defect S23), double rounding is illustrated on intermediate values, producing drift ($1.12$ vs single-rounded $1.11$).
- **Why It Matters:**
  - Failing verification gates compromise continuous integration; errors in significant-figure propagation cause cumulative rounding drift in clinical dosage calculations.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Updating `build/check_sigfig_cases.py` to validate static case tables in `build/sections/08_ch8.html` against `build/sigfig_cases.json`; recomputing all 23 cases using Python `Decimal`; establishing strict rules distinguishing decimal places (addition/subtraction) from significant figures (multiplication/division); eliminating double rounding.
  - *Out of Scope:* Re-introducing runtime JavaScript trainer state or client-side evaluation arrays into `app.js`.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Skoog et al. (10th ed.) Chapter 6; Harris & Lucy (10th ed.) Chapter 3; `build/claims.json` (Claims C10, C11, C13).
  - *Warrant Check:* All 4 warrant conditions passed. Exact decimal arithmetic is unambiguous.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Test Suite Alignment:* Refactor `build/check_sigfig_cases.py` to parse static HTML tables in `08_ch8.html` instead of searching for `sftCases` in `app.js`.
  2. *Decimal Recomputation Verification:* Execute Python `Decimal` recomputations across all cases in `build/sigfig_cases.json`, ensuring guard digits are preserved during intermediate stages.
  3. *Prose Disambiguation:* In `build/sections/07_ch7.html`, rewrite Section 7.2 to explicitly contrast decimal places (*zīmes aiz komata*) against significant figures (*zīmīgie cipari*).
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T05.1: Checker Harness Refactoring*
    1. In `build/check_sigfig_cases.py`, replace the `app.js` regex scan with an HTML table row extractor targeting `#ch8-sft-table tbody tr`.
    2. Add an automated assertion that each extracted HTML row matches the corresponding `id`, `operands`, `expected_raw`, and `expected_rounded` fields in `sigfig_cases.json`.
    3. Execute `python3 -I build/check_sigfig_cases.py --check` and verify exit code 0.
  - *Subtask T05.2: Double Rounding Inoculation*
    1. In `build/sections/08_ch8.html`, insert a dedicated `.mistake-pair` callout showing S23: intermediate value $1.1149$ rounded in two steps ($1.1149 \rightarrow 1.115 \rightarrow 1.12$) vs single rounding ($1.1149 \rightarrow 1.11$).
    2. Update `build/sigfig_cases.json` with an explicit test case for single vs double rounding.
    3. Run `python3 -I build/verify_numbers.py --self-test` to confirm numeric synchrony.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/check_sigfig_cases.py`, `build/sigfig_cases.json`, `build/sections/07_ch7.html`, `build/sections/08_ch8.html`.
  - *Selectors:* `#ch8-sft-table`, `.sigfig-calc`, `.mistake-pair`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_sigfig_cases.py --check` passes with `ok arithmetic: all cases match Decimal recompute`.
  - *Negative Test:* Modifying an intermediate rounded value in `08_ch8.html` causes the checker to exit with code 1.
  - *Zero Runtime Script Regression:* Confirm `app.js` is not modified and remains free of trainer case arrays.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01; upstream of T06, T10, B01.
  - *Collision Group:* Group E (Arithmetic & Cases).
  - *Rollback Plan:* Git checkout `build/check_sigfig_cases.py`.
  - *Definition of Done:* `check_sigfig_cases.py --check` passes cleanly; S9/S23 errors fully resolved in prose.

---

### T06 — Calibration Curve Inversion, Density Interpolation, and Significant-Figure Synchronization

- **Task ID & Decisive Title:** `T06` — Calibration Curve Inversion, Density Interpolation, and Significant-Figure Synchronization
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/verify_numbers.py` verifies all calibration parameters; $R^2 = 0.998933$)
  - *Responsibility Boundary:* Owns quantitative worked examples in Chapter 10 (`build/sections/10_ch10.html`) and Chapter 12 (`build/sections/12_ch12.html`). Governs algebraic inversion of linear fits ($y = mx + b \rightarrow x = (y - b)/m$) and density-to-mass-fraction interpolation.
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `blueprint-spec-sheet`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` Q7 pp. 4–5 (defect S15), calibration data for ascorbic acid assay gives linear regression $A = 0.0322\cdot\rho + 0.0106$ ($R^2 = 0.9989$). When inverting to solve for unknown sample concentrations $\rho = (A - 0.0106)/0.0322$, students frequently round intermediate slope and intercept values prematurely, producing inconsistent final digits.
  - In Chapter 12, density calculations for $\text{NaCl}$ solution (pycnometer experiment, 2B Q3) involve multiple unit transformations ($1.0334\text{ g/mL} = 1033.4\text{ kg/m}^3$) where students drop trailing zeros or introduce unphysical precision.
- **Why It Matters:**
  - Inaccurate calibration inversion directly falsifies reported patient blood analyte concentrations.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Providing full step-by-step arithmetic derivations showing unrounded intermediate calculation alongside the final rounded result adhering to significant figures; tabular synchronization of all 6 standard solutions and 6 patient samples; clear warning regarding extrapolation on sample Citrons ($A = 0.982 > 0.975$).
  - *Out of Scope:* Altering raw seminar data points or changing course answer keys.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Skoog et al. Chapter 7 & 26; `S-2026` Q7; `build/claims.json` (Claims C16, C17).
  - *Warrant Check:* All 4 warrant conditions passed. Inversion algebra is exact.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Tabular Derivation Synchronization:* In `build/sections/10_ch10.html`, present a complete synchronization table showing for each sample: measured $A$, exact inverted concentration $\rho_{\text{exact}}$, and reported concentration $\rho_{\text{reported}}$ ($2$ or $3$ sig figs).
  2. *Extrapolation Warning Callout:* Insert an explicit `.role--mistake` callout on sample Citrons ($A = 0.982$), explaining that values outside the calibrated standard interval ($[0.168, 0.975]$) represent unverified extrapolations.
  3. *Density Route Alignment:* In `build/sections/12_ch12.html`, synchronize the 5 solution preparation routes from `build/verify_numbers.py` (routes schema 2) into the chapter text.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T06.1: Calibration Mathematics Alignment*
    1. In `build/sections/10_ch10.html`, verify that the linear equation reads $A = 0.0322\cdot\rho + 0.0106$ with explicit parameter definitions.
    2. Add an intermediate calculation display for sample Āboli ($A = 0.845 \rightarrow \rho = 25.9406... \rightarrow 25.9\text{ mg/L}$).
    3. Run `python3 -I build/check_calibration.py --self-test` to confirm mathematical guards pass.
  - *Subtask T06.2: Density Conversion Protocol*
    1. In `build/sections/12_ch12.html`, align pycnometer worked steps: empty flask ($48.37\text{ g}$), salt ($5.02\text{ g}$), total ($151.71\text{ g}$), solution mass ($103.34\text{ g}$), volume ($100.0\text{ mL}$) $\rightarrow \rho = 1.0334\text{ g/mL}$.
    2. Ensure final reported density is formatted as $1.033\text{ g/mL}$ or $1033.4\text{ kg/m}^3$ with unit consistency.
    3. Run `python3 -I build/check_route_table.py --self-test` to confirm route schema integrity.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/10_ch10.html`, `build/sections/12_ch12.html`, `build/verify_numbers.py`.
  - *Selectors:* `.calc--calibration-steps`, `.table--calibration-sync`, `.extrapolation-warning`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/verify_numbers.py --check` passes with zero discrepancies across all 6 calibration samples.
  - *Negative Test:* Introducing an unrounded sample concentration without significant-figure rounding fails validation.
  - *Accessibility Check:* Data tables have semantic `<th>` scope attributes and clear captions.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T02, T05; upstream of T11, F07.
  - *Collision Group:* Group B (Calibration & Solutions).
  - *Rollback Plan:* Revert changes in `10_ch10.html` and `12_ch12.html`.
  - *Definition of Done:* Calibration inversion and density steps fully synchronized; extrapolation risks highlighted.

---

### T07 — Scientific Prose Rhythm, Sentence Decomposition, and Cognitive Deloading

- **Task ID & Decisive Title:** `T07` — Scientific Prose Rhythm, Sentence Decomposition, and Cognitive Deloading
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P2 (Polish & Refinement) | *Impact:* 3 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/check_prose_rhythm.py` passes: 69 paragraphs $\ge 45$ words $\le 70$; 31 em dashes $\le 40$)
  - *Responsibility Boundary:* Owns prose readability and cognitive pacing across all 16 chapter source fragments (`build/sections/01_ch1.html` through `16_ch16.html`). Governs sentence length, active voice, and removal of dense academic clutter without flattening domain precision.
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `tufte-margin-scholar`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In earlier drafts, `build/check_prose_rhythm.py` flagged 73 paragraphs exceeding 45 words (threshold 70). Although currently passing at 69 paragraphs, several explanatory sections in Chapters 6, 8, and 11 feature complex multi-clause sentences that elevate cognitive load for second-language learners.
  - Excessive use of em dashes (currently 31) occasionally interrupts logical derivations.
- **Why It Matters:**
  - First-year medical students navigating dense analytical chemistry concepts suffer extraneous cognitive load when prose is cluttered with run-on sentences, decreasing retention of core metrological principles.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Splitting remaining run-on paragraphs into crisp, single-mechanism sentences; replacing dense parenthetical interruptions with structured bullet sequences; ensuring body text measure stays within 60ch–75ch; maintaining strict gate compliance in `build/check_prose_rhythm.py` ($\le 65$ long paragraphs, $\le 30$ em dashes).
  - *Out of Scope:* Oversimplifying technical vocabulary, removing necessary mathematical derivations, or deleting historical course context.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Sweller's Cognitive Load Theory; RSU Medical Chemistry Syllabus; `PROMPT_Master_html_2_tema.md` §6.
  - *Warrant Check:* All 4 warrant conditions passed. Readability improvements preserve factual semantics.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Automated Prose Audit:* Run `python3 -I build/check_prose_rhythm.py` to identify the exact line locations of all 69 paragraphs exceeding 45 words.
  2. *Surgical Sentence Decomposition:* In targeted chapters (specifically Chapters 6, 8, and 11), split compound sentences into active, declarative statements connecting cause to effect.
  3. *Structural List Integration:* Convert complex inline multi-item lists into clean, vertical unordered lists with emphasized leading terms.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T07.1: Paragraph Decomposition in Chapters 6 and 8*
    1. In `build/sections/06_ch6.html`, split the compound explanations of repeatability and reproducibility into distinct, contrasted paragraphs.
    2. In `build/sections/08_ch8.html`, break down multi-clause descriptions of mixed operations into clear sequential decision rules.
    3. Run `python3 -I build/check_prose_rhythm.py` to confirm long paragraph count decreases.
  - *Subtask T07.2: Em Dash & Parenthetical Cleanup in Chapter 11*
    1. In `build/sections/11_ch11.html`, replace inline em dashes with commas or separate sentences in the Mercury-203 decay narrative.
    2. Verify that technical isotope qualifiers ($^{203}\text{Hg}$) maintain non-breaking spaces before units.
    3. Run `python3 -I tools/check_anchors.py` to ensure heading or ID references were not disrupted.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/06_ch6.html`, `build/sections/08_ch8.html`, `build/sections/11_ch11.html`, `build/check_prose_rhythm.py`.
  - *Selectors:* `section.chapter p`, `.lead-in`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_prose_rhythm.py` exits 0 with long paragraphs $\le 65$ and em dashes $\le 30$.
  - *Negative Test:* No examinable chemistry terms or concept labels from `concepts.json` are dropped.
  - *Pillar Verification:* `python3 -I tools/check_pillars.py` remains 100% compliant.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T03; upstream of T15, T16.
  - *Collision Group:* Group F (Prose & Content Fragments).
  - *Rollback Plan:* Revert modified chapter fragments via git.
  - *Definition of Done:* Prose rhythm gate comfortably below thresholds; reading measure comfortable; zero loss of technical nuance.

---

### T08 — Table and Figure Architecture: Structural Captions, Fallback Tables, and Gated DOM Metrics

- **Task ID & Decisive Title:** `T08` — Table and Figure Architecture: Structural Captions, Fallback Tables, and Gated DOM Metrics
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`tools/check_counts.py` passes; 84 tables, 13 figures, 22 SVGs)
  - *Responsibility Boundary:* Owns all tabular structures (`.data-table`), figure plates (`figure.plate`), figure fallback tables (`figure_data.py`), and DOM metric synchronization via `tools/derive_counts.py` and `tools/check_counts.py`.
  - *Applicable Workspace Skills:* `print-css-alchemist`, `pdf-vector-surgeon`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Master_2_tema_merijumi_un_grafiki.html`, there are 84 tables and 13 figure plates. While `tools/check_counts.py` confirms current counts match `build/counts.json`, earlier audits revealed metric drift when manual edits were made to section fragments.
  - Plot figures require accessible, text-based data tables for students using screen readers or printing in grayscale, implemented via `figure_data.py` injection.
  - Several tables lack responsive overflow handling on narrow screens or suffer from awkward row breaks across page margins in print layout.
- **Why It Matters:**
  - Unstructured tables and uncaptioned figures violate WCAG 2.2 accessibility standards and fail silently in print exports; metric drift between code and governance ledgers causes audit failures.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* 100% of tables wrapped in `.table-scroll` containers with explicit `<caption>` and scoped `<th>` headers; every vector plot paired with a clean fallback data table; automatic metric synchronization via `derive_counts.py`; zero manual edits to `counts.json`.
  - *Out of Scope:* Eliminating data tables in favor of chart-only representations.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* WCAG 2.2 Success Criterion 1.3.1 (Info and Relationships); `docs/governance/ARCH_CSS_DOM_CONTRACTS.md`.
  - *Warrant Check:* All 4 warrant conditions passed. Structural table markup is accessibility standard.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Table Markup & Caption Audit:* Scan all 84 tables in `build/sections/*.html` to ensure every table features a descriptive `<caption>`, `<thead>` with `<th scope="col">`, and zero bare text rows.
  2. *Fallback Table Synchronization:* Verify that `build/figure_data.py` injects complete, accessible fallback tables for all 12 plot figures during `build/build_doc.py`.
  3. *Metric Derivation & Gate Execution:* Execute `python3 -I tools/derive_counts.py` and enforce zero-drift validation in `tools/check_counts.py`.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T08.1: Table Accessibility & Overflow Wrappers*
    1. In `build/sections/02_ch2.html` and `04_ch4.html`, verify that all data tables reside inside `<div class="table-scroll">`.
    2. Add `<caption>` elements to tables lacking explicit titles, summarizing table contents and unit conventions.
    3. Run `python3 -I tools/check_anchors.py` to verify table IDs and local link references.
  - *Subtask T08.2: Automated Metric Verification Pipeline*
    1. In `tools/derive_counts.py`, verify parsing logic for `table`, `figure.plate`, `svg`, `details`, `id`, `recall-answer`.
    2. Run `python3 -I tools/derive_counts.py` to regenerate `build/counts.json`.
    3. Run `python3 -I tools/check_counts.py` to confirm live master matches the recorded metrics with zero exit code.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/*.html`, `build/figure_data.py`, `build/counts.json`, `tools/derive_counts.py`, `tools/check_counts.py`.
  - *Selectors:* `table.data-table`, `.table-scroll`, `figure.plate`, `figcaption`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_counts.py` outputs `COUNTS-OK` with 0 mismatches.
  - *Negative Test:* Manually adding a dummy table to `01_ch1.html` causes `check_counts.py` to fail with drift report.
  - *Print Test:* Table rows feature `break-inside: avoid` in `build/style.css` print styles.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01; upstream of T15, T17, F06.
  - *Collision Group:* Group G (DOM Structure & Metrics).
  - *Rollback Plan:* Git checkout `build/counts.json` and section files.
  - *Definition of Done:* All 84 tables and 13 figures structured, accessible, and verified by automated counts gate.

---

### T09 — Inferential Biostatistics: Degrees of Freedom, Standard Error, and Student's $t$ Confidence Intervals

- **Task ID & Decisive Title:** `T09` — Inferential Biostatistics: Degrees of Freedom, Standard Error, and Student's $t$ Confidence Intervals
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P1 (Core Accuracy) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/verify_numbers.py` verifies all Question 3 statistical parameters; Dixon test verified)
  - *Responsibility Boundary:* Owns statistical explanations, sample calculations, and confidence interval theory in Chapter 6 (`build/sections/06_ch6.html`) and Chapter 7 (`build/sections/07_ch7.html`).
  - *Applicable Workspace Skills:* `tufte-margin-scholar`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Analitiskas-metodes_2024.pdf` p. 4 (defect S8), statistics are introduced with ambiguous symbols: «vidējā kvadrātiskā kļūda $\sigma_{n-1}$» (conflating sample standard deviation $s$ with population $\sigma$), «Stjudenta koeficients $t_{\alpha n}$» (omitting explicit degrees of freedom $f = n - 1$), and «drošības intervāls».
  - In `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` Q3 p. 1, three titration replicate readings ($12.50, 13.05, 12.55\text{ mL}$) yield mean $12.70\text{ mL}$, sample $s = 0.304\text{ mL}$, standard error $s_{\bar{x}} = s/\sqrt{3} = 0.176\text{ mL}$, and $95\%$ confidence interval half-width $0.76\text{ mL}$ ($t = 4.303$). Students frequently use $n$ instead of $n-1$ or fail to justify why the $13.05\text{ mL}$ outlier cannot be discarded.
- **Why It Matters:**
  - Misunderstanding small-sample statistics leads clinicians to overstate confidence in laboratory diagnostics, misinterpret reference intervals, and discard legitimate clinical outliers.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Explicit differentiation between population $\sigma$ and sample standard deviation $s = \sqrt{\frac{\sum (x_i - \bar{x})^2}{n-1}}$; formal definition of degrees of freedom $f = n - 1$; rigorous definition of standard error of the mean $s_{\bar{x}} = s/\sqrt{n}$; complete worked Dixon's $Q$-test ($Q_{\text{calc}} = 0.909 < Q_{\text{crit}} = 0.941$); connection to `SVG-15` confidence interval coverage.
  - *Out of Scope:* High-dimensional ANOVA or non-parametric statistics outside curriculum.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* ISO 5725-1:1994; Harris & Lucy (10th ed.) Chapter 4; Skoog et al. Chapter 6 & 7; `build/claims.json` (Claim C12).
  - *Warrant Check:* All 4 warrant conditions passed. Small-sample Student's $t$ statistics apply to normally distributed replicates.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Symbolic & Formulaic Overhaul:* In `build/sections/06_ch6.html`, replace all instances of $\sigma_{n-1}$ with sample standard deviation $s$, providing clear equations for sample variance $s^2$, standard error $s_{\bar{x}}$, and confidence interval $CI = \bar{x} \pm t(\alpha; n-1)\cdot \frac{s}{\sqrt{n}}$.
  2. *Dixon Q-Test Outlier Protocol:* In `build/sections/07_ch7.html`, implement a full worked example of Dixon's $Q$-test for Question 3, demonstrating why $13.05\text{ mL}$ must be retained.
  3. *Frequentist Coverage Visualization:* Annotate `SVG-15` (`build/figures/ci-coverage.svg`) in Chapter 6 to explain why 1 out of 20 intervals is expected to miss the true population mean $\mu$ at $95\%$ confidence.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T09.1: Statistical Formulas & Terminology Refactor*
    1. In `build/sections/06_ch6.html`, update formula blocks to show Student's $t$ with explicit arguments: $t(0.05; 2) = 4.303$.
    2. Add an explicit comparison callout contrasting sample standard deviation $s$ (spread of individual measurements) with standard error $s_{\bar{x}}$ (uncertainty of the mean).
    3. Run `python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --report` to confirm statistical term compliance.
  - *Subtask T09.2: Question 3 Worked Example Synchronization*
    1. In `build/sections/07_ch7.html`, verify Question 3 worked steps: $\sum x = 38.10$, $\bar{x} = 12.70$, $s = 0.304$, $s/\sqrt{3} = 0.176$, $CI = [11.94, 13.46]$.
    2. Display the Dixon $Q$-test calculation explicitly: $Q = \frac{13.05 - 12.55}{13.05 - 12.50} = \frac{0.50}{0.55} = 0.909$.
    3. Run `python3 -I build/verify_numbers.py --self-test` to confirm arithmetic agreement.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/06_ch6.html`, `build/sections/07_ch7.html`, `build/figures/ci-coverage.svg`, `build/verify_numbers.py`.
  - *Selectors:* `.calc--statistics`, `.formula--confidence-interval`, `.outlier-box`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/verify_numbers.py --check` passes with exact agreement on all Q3 statistical parameters.
  - *Negative Test:* Searching for unannotated «drošības intervāls» in Chapter 6 returns 0 matches.
  - *Graphic Test:* `SVG-15` displays 10 intervals with exactly 1 non-overlapping interval highlighted.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T03; upstream of T10, F03.
  - *Collision Group:* Group C (Metrology & Statistics).
  - *Rollback Plan:* Revert changes in `06_ch6.html` and `07_ch7.html`.
  - *Definition of Done:* Sample statistics and confidence intervals rigorously formulated; Dixon test demonstrated.

---

### T10 — Mixed Operations Decision Tree: Multi-Step Significant Figures and Intermediate Rounding Guards

- **Task ID & Decisive Title:** `T10` — Mixed Operations Decision Tree: Multi-Step Significant Figures and Intermediate Rounding Guards
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (23 cases verified in `build/sigfig_cases.json`)
  - *Responsibility Boundary:* Owns complex mixed arithmetic workflows (addition/subtraction combined with multiplication/division) in Chapter 8 (`build/sections/08_ch8.html`).
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `learn-then-test`.
- **Observed Problem & Concrete Workspace Evidence:**
  - When clinical chemistry problems combine addition/subtraction with multiplication/division (e.g., calculating density from mass difference $\rho = \frac{m_{\text{full}} - m_{\text{empty}}}{V}$, or temperature corrections), students struggle to decide which rule takes precedence.
  - Students frequently either round prematurely at each intermediate step (causing cumulative rounding error) or carry indiscriminate calculator precision to the final result without determining limiting significant digits.
- **Why It Matters:**
  - In clinical laboratory assays, compounding intermediate rounding errors distorts calibration slopes and alters reported patient therapeutic drug monitoring results.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Codifying an operational 3-step decision procedure for mixed operations; tracking limiting decimal places through intermediate parenthetical steps using subscript notation (e.g., $103.34\text{ g}$ has 2 decimal places and 5 sig figs); carrying at least one guard digit through intermediate steps; rounding once at the terminal reporting stage.
  - *Out of Scope:* Authoring dynamic JavaScript calculator exercises; content must be fully articulated in static HTML.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Skoog et al. Chapter 6; Harris & Lucy Chapter 3; `build/sigfig_cases.json`.
  - *Warrant Check:* All 4 warrant conditions passed. Significant-figure propagation rules for mixed operations are standard.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Decision Procedure Algorithm Design:* In `build/sections/08_ch8.html`, introduce a visual decision tree diagram showing the sequence: evaluate parentheses $\rightarrow$ identify limiting decimal places $\rightarrow$ determine limiting significant figures $\rightarrow$ perform division $\rightarrow$ round once.
  2. *Subscript Guard-Digit Annotation:* Annotate all worked examples in Chapter 8 with subscript notation to track uncertainty propagation without premature truncation.
  3. *Static Multi-Step Case Table Verification:* Ensure all static rows in `#ch8-sft-table` feature explicit intermediate unrounded values alongside the terminal rounded result.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T10.1: Decision Tree & Prose Construction*
    1. In `build/sections/08_ch8.html`, author Section 8.3 outlining the step-by-step decision rules for mixed operations.
    2. Add an explicit clinical worked example: pycnometer density calculation $\rho = \frac{151.71 - 48.37}{100.0} = \frac{103.34}{100.0} = 1.0334\text{ g/mL} \rightarrow 1.033\text{ g/mL}$ (4 sig figs).
    3. Run `python3 -I tools/check_pillars.py` to confirm worked example and mistake pillars pass.
  - *Subtask T10.2: Static Case Table & Harness Verification*
    1. In `build/sections/08_ch8.html`, verify that the 8 static trainer case rows in `#ch8-sft-table` contain complete explanations of intermediate steps.
    2. Cross-check each row against `build/sigfig_cases.json` using Python `Decimal`.
    3. Run `python3 -I build/check_sigfig_cases.py --self-test` to confirm arithmetic validity.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/08_ch8.html`, `build/sigfig_cases.json`, `build/check_sigfig_cases.py`.
  - *Selectors:* `#ch8-sft-table`, `.decision-tree`, `.guard-digit`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_sigfig_cases.py --check` passes with all mixed cases verified.
  - *Negative Test:* Introducing an intermediate rounding truncation in the worked example fails validation.
  - *Accessibility Check:* Subscript notations have screen-reader text alternatives.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T05; upstream of T14, B01.
  - *Collision Group:* Group E (Arithmetic & Cases).
  - *Rollback Plan:* Revert changes in `08_ch8.html`.
  - *Definition of Done:* Mixed operations decision procedure codified; guard digits demonstrated; static cases fully verified.

---

### T11 — Analytical Calibration Evidence: Regression Diagnostics, Residuals, and Model Limits

- **Task ID & Decisive Title:** `T11` — Analytical Calibration Evidence: Regression Diagnostics, Residuals, and Model Limits
- **Classification & Governance Block:**
  - *Workstream:* SVG & Visual Pedagogy
  - *Priority:* P1 (Core Accuracy) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/check_calibration.py --self-test` passes; residual pattern verified)
  - *Responsibility Boundary:* Owns calibration regression theory, residual plot figures (`SVG-17`, `SVG-18`), and fallback tabular data in Chapter 10 (`build/sections/10_ch10.html`). Interfaces with T02 for Beer–Lambert bounds and T06 for numerical inversion.
  - *Applicable Workspace Skills:* `blueprint-spec-sheet`, `pdf-vector-surgeon`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `build/sections/10_ch10.html`, students are shown an ascorbic acid calibration curve with a high coefficient of determination ($R^2 = 0.9989$). Medical students routinely infer that $R^2 \approx 1$ proves the linear model is valid across all concentrations.
  - In `build/figures/calibration-residuals.svg` (`SVG-18`), residual deviations $e_i = y_i - \hat{y}_i$ show a structured alternating pattern ($-0.0034, +0.0087, +0.0019, -0.0169, +0.0103, -0.0006$).
  - Without explicit visual instruction, students fail to understand why $R^2$ alone is an insufficient criterion for linearity and ignore residual trends indicating non-linear detector saturation.
- **Why It Matters:**
  - Relying on $R^2$ without checking residual distribution causes clinical laboratory technicians to miss instrument detector saturation or chemical matrix effects, leading to erroneous reporting of patient drug levels.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Codifying the diagnostic rule that $R^2$ alone does not prove linearity; pairing `SVG-17` (linear fit) with `SVG-18` (residual plot); defining the limit of linearity (LOL) and dynamic range; providing a structured tabular breakdown of residuals in concentration units ($\text{mg/L}$) as well as absorbance units.
  - *Out of Scope:* Requiring students to perform weighted least-squares or polynomial curve fitting in introductory coursework.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* IUPAC Compendium of Analytical Nomenclature; Skoog et al. Chapter 26; Harris & Lucy Chapter 5; `build/claims.json` (Claims C15, C17).
  - *Warrant Check:* All 4 warrant conditions passed. Residual analysis is the authoritative benchmark for regression validity.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Pedagogical Text & Callout Integration:* In `build/sections/10_ch10.html`, author an analytical diagnostics section explicitly addressing why high $R^2$ can coexist with poor fit at low/high extremes.
  2. *Residual Figure Synchronization:* Cross-link `SVG-17` and `SVG-18` with unified color tokens and matching x-axis scales ($5.0$ to $30.0\text{ mg/L}$).
  3. *Fallback Table Enhancement:* Update `build/figure_data.py` to ensure the residual table displays both absolute absorbance residual ($\Delta A$) and equivalent concentration residual ($\Delta \rho$).
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T11.1: Chapter 10 Diagnostics Section Expansion*
    1. In `build/sections/10_ch10.html`, add a `.role--rule` callout stating: "Augsts $R^2$ viens pats nepierāda lineāru sakarību."
    2. Author a worked case analyzing the largest residual at $\rho = 20.0\text{ mg/L}$ ($\Delta A = -0.0169$, $\Delta \rho = -0.53\text{ mg/L}$).
    3. Run `python3 -I build/check_calibration.py --self-test` to confirm regression logic passes.
  - *Subtask T11.2: Figure & SVG Token Alignment*
    1. In `build/figures/calibration-residuals.svg`, ensure zero line is styled with `--plot-axis` and residual bars use `--plot-data`.
    2. Verify that residual data points match `build/verified.json` values exactly.
    3. Run `python3 -I tools/check_figure_style.py` to confirm scoped SVG styling without local `<style>` blocks.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/10_ch10.html`, `build/figures/calibration-residuals.svg`, `build/figure_data.py`, `build/verified.json`.
  - *Selectors:* `#ch10-residuals`, `.residual-table`, `.role--rule`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_calibration.py --self-test` confirms that mutated residuals are rejected.
  - *Negative Test:* Introducing an assertion that $R^2 > 0.99$ waives residual testing fails build lint.
  - *Visual Test:* `SVG-17` and `SVG-18` render with identical x-axis coordinate extents ($5$ to $30\text{ mg/L}$).
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T02, T06; upstream of F07.
  - *Collision Group:* Group B (Calibration & Solutions).
  - *Rollback Plan:* Git checkout `build/sections/10_ch10.html`.
  - *Definition of Done:* Residual plot and table integrated; $R^2$ limitations documented; regression diagnostics complete.

---

### T12 — Procedural Graph Reading: Coordinate Tracing, Interpolation vs Extrapolation, and Visual Access

- **Task ID & Decisive Title:** `T12` — Procedural Graph Reading: Coordinate Tracing, Interpolation vs Extrapolation, and Visual Access
- **Classification & Governance Block:**
  - *Workstream:* SVG & Visual Pedagogy
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (8 static graph cases verified in `build/graph_cases.json`)
  - *Responsibility Boundary:* Owns graphical reading protocols in Chapter 9 (`build/sections/09_ch9.html`), reading path diagram `SVG-16`, and static exercise table `#ch9-gr-cases`.
  - *Applicable Workspace Skills:* `svg-spatial-occlusion`, `state-scrubber-lab`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `build/sections/09_ch9.html`, students are expected to extract quantitative values from calibration curves and decay plots. However, graph reading is often treated as an intuitive visual glance rather than a rigorous 4-step physical measurement procedure.
  - In `build/sections/09_ch9.html` line 75, diagram `SVG-16` (reading path: axis $\rightarrow$ curve $\rightarrow$ second axis) is hand-written inline without design-token bindings, creating visual drift from the rest of the figures.
  - Students consistently fail to distinguish reliable interpolation within calibrated bounds from hazardous extrapolation beyond standard endpoints.
- **Why It Matters:**
  - Reading a clinical laboratory graph along the wrong axis or extrapolating calibration curves into saturated regimes leads to incorrect medication administration dosages.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Codifying the 4-step procedural algorithm for reading graphs: 1. Identify given axis; 2. Trace perpendicular projection to curve; 3. Drop perpendicular to unknown axis; 4. Assess division subdivisions and estimate final digit; refactoring `SVG-16` to use document design tokens; verifying all 8 static cases in `#ch9-gr-cases`.
  - *Out of Scope:* Dynamic JavaScript canvas-based drag-and-drop plotting trainers.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Skoog et al. Chapter 5; `S-2A` Q5; `build/claims.json` (Claims C05, C17).
  - *Warrant Check:* All 4 warrant conditions passed. Coordinate projection rules are geometric certainties.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Reading Path Algorithm Codification:* In `build/sections/09_ch9.html`, structure the 4-step graph reading procedure into an aligned step card sequence (`.steps`).
  2. *Inline SVG Vector Refactor:* Move inline diagram `SVG-16` into `build/gen_figures.py` as `reading-path.svg`, applying standard design tokens (`.axis`, `.data`, `.lab`).
  3. *Static Case Synchronization:* Cross-check all 8 static cases in `#ch9-gr-cases` against `build/graph_cases.json`, ensuring both reading directions ($x \rightarrow y$ and $y \rightarrow x$) are practiced.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T12.1: Chapter 9 Procedural Guide Authoring*
    1. In `build/sections/09_ch9.html`, insert a step-by-step numbered guide for reading both linear and curved semi-log plots.
    2. Author a dedicated callout on estimation: explain that the final digit on a linear grid is an estimate ($1/10$ or $1/5$ of smallest division).
    3. Run `python3 -I tools/check_pillars.py` to confirm Chapter 9 mechanism and example pillars pass.
  - *Subtask T12.2: Vector Diagram & Static Cases Verification*
    1. In `build/sections/09_ch9.html`, replace hand-written vector markup with the centralized figure inclusion tag `{{FIG:reading-path}}`.
    2. In `build/gen_figures.py`, generate `reading-path.svg` with matching `--plot-axis` and `--plot-accent` tokens.
    3. Run `python3 -I build/check_graph_trainer.py --targets` to confirm static target alignment.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/09_ch9.html`, `build/gen_figures.py`, `build/figures/reading-path.svg`, `build/graph_cases.json`.
  - *Selectors:* `#ch9-gr-cases`, `.reading-algorithm`, `.steps`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_graph_trainer.py --targets` passes with 0 target discrepancies.
  - *Negative Test:* Removing an axis direction indicator triggers figure validation failure.
  - *A11y Test:* `reading-path.svg` includes `<title>` and `<desc>` explaining projection geometry.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T08; upstream of F05.
  - *Collision Group:* Group F (Content & Figures).
  - *Rollback Plan:* Git checkout `build/sections/09_ch9.html`.
  - *Definition of Done:* Graph reading algorithm codified; `SVG-16` refactored to design tokens; all 8 cases verified.

---

### T13 — First-Order Decay Kinetics: Non-Zero Time Origin, Radionuclide Half-Life, and Rate Constants

- **Task ID & Decisive Title:** `T13` — First-Order Decay Kinetics: Non-Zero Time Origin, Radionuclide Half-Life, and Rate Constants
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P1 (Core Accuracy) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/check_half_life_offset.py --self-test` passes; C19 verified via LNHB/NuDat)
  - *Responsibility Boundary:* Owns radionuclide decay kinetics and chemical half-life in Chapter 11 (`build/sections/11_ch11.html`), half-life decay figures (`SVG-19`, `SVG-20`, `SVG-21`), and offset verification script `build/check_half_life_offset.py`.
  - *Applicable Workspace Skills:* `cognitive-deload-auditor`, `tufte-margin-scholar`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` Q8 p. 6 (defect S18), the seminar decay problem presents a curve where the horizontal time axis does not start at $t = 0$, but at an offset $t_0 = 40\text{ min}$. Students who read the elapsed time directly from the x-axis value without subtracting $t_0$ arrive at false half-life estimates ($100\text{ min}$ instead of $60\text{ min}$).
  - In course materials (defect S17), the half-life of Mercury-203 is cited as $46.595\text{ days}$. While mathematically consistent with the course decay curve, this required reconciliation against international evaluations (LNHB $46.594(12)\text{ d}$ and NuDat $46.610(10)\text{ d}$, Claim C19).
  - Students often fail to grasp the first-order differential rate relationship $k = \frac{\ln 2}{t_{1/2}} \approx \frac{0.693}{t_{1/2}}$.
- **Why It Matters:**
  - In nuclear medicine, administering radiopharmaceuticals ($^{203}\text{Hg}$, $^{99\text{m}}\text{Tc}$, $^{131}\text{I}$) based on faulty half-life calculations results in under-dosing diagnostic scans or severe radiation overdose to patient tissues.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Explicit mathematical derivation of first-order decay $N(t) = N_0 e^{-\lambda t}$; derivation of half-life $t_{1/2} = \frac{\ln 2}{\lambda}$; rigorous pedagogical demonstration of the non-zero origin offset rule ($\Delta t = t_2 - t_1$); integration of dual-panel diagram `SVG-21` (`half-life-offset.svg`); clear presentation of Mercury-203 evaluated data alongside the authentic course datum.
  - *Out of Scope:* Second-order or complex multi-exponential branched decay chains.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* LNHB Recommended Decay Data (2004); Kondev, Nucl. Data Sheets 177, 509 (2021); `build/claims.json` (Claims C18, C19); `S-2026` Q8.
  - *Warrant Check:* All 4 warrant conditions passed. First-order decay kinetics are physically exact for isolated radionuclides.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Decay Kinetics Derivation:* In `build/sections/11_ch11.html`, present a complete derivation linking exponential decay to half-life intervals, proving that half-life is constant regardless of starting concentration.
  2. *Origin Offset Inoculation & Diagram Pairing:* Structure an explicit worked solution for Question 8, demonstrating how to identify $t_0 = 40\text{ min}$, measure successive intervals ($t_1 = 98\text{ min} \rightarrow \Delta t_1 = 58\text{ min}$; $t_2 = 161\text{ min} \rightarrow \Delta t_2 = 63\text{ min}$), and average them to $60.5\text{ min}$.
  3. *Radionuclide Provenance Section:* Author a scholarly note in Section 11.4 presenting the Mercury-203 evaluation history (LNHB vs NuDat) while retaining the course datum ($46.595\text{ d}$).
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T13.1: Mathematical & Offset Derivation*
    1. In `build/sections/11_ch11.html`, add formula containers `.formula` showing $t_{1/2} = \frac{\ln(2)}{k} = \frac{0.69315}{k}$.
    2. Insert an operational warning: "Ja laika ass nesākas no nulles, pussabrukšanas periods ir intervāls $\Delta t = t_{i+1} - t_i$, nevis punkta koordināta!"
    3. Run `python3 -I build/check_half_life_offset.py --self-test` and verify that the 2-panel offset check passes.
  - *Subtask T13.2: Figure Integration & Claim C19 Display*
    1. Verify that `SVG-19`, `SVG-20`, and `SVG-21` feature clear dashed projection lines showing successive halvings ($100\% \rightarrow 50\% \rightarrow 25\% \rightarrow 12.5\%$).
    2. In Section 11.4, format the comparison table: Course ($46.595\text{ d}$), LNHB ($46.594(12)\text{ d}$), NuDat ($46.610(10)\text{ d}$).
    3. Run `python3 -I tools/check_sources.py` to confirm S-LNHB and S-NUDAT citations validate.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/11_ch11.html`, `build/figures/half-life-offset.svg`, `build/check_half_life_offset.py`, `build/claims.json`.
  - *Selectors:* `#ch11-decay-offset`, `.decay-table`, `.role--rule`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_half_life_offset.py --self-test` outputs `HALF-LIFE-OFFSET-OK t0=40 t_half=60 levels=3 deltas=58,63 mean=60.5`.
  - *Negative Test:* Calculating half-life as $t_1 - 0$ (failing to subtract $t_0$) triggers automated self-test failure.
  - *Visual Test:* `SVG-21` displays both absolute and elapsed time axes with distinct color tokens.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T05; upstream of F09.
  - *Collision Group:* Group F (Kinetics & Sources).
  - *Rollback Plan:* Git checkout `build/sections/11_ch11.html`.
  - *Definition of Done:* Kinetics derivations complete; non-zero origin offset illustrated; C18/C19 provenance verified.

---

### T14 — Clinical Solution Preparation: Mass Fractions, Molar Concentrations, and Dilution Decision Flows

- **Task ID & Decisive Title:** `T14` — Clinical Solution Preparation: Mass Fractions, Molar Concentrations, and Dilution Decision Flows
- **Classification & Governance Block:**
  - *Workstream:* Pedagogy & Explanations
  - *Priority:* P1 (Core Accuracy) | *Impact:* 5 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`build/check_route_table.py --self-test` passes; 5 routes verified)
  - *Responsibility Boundary:* Owns solution chemistry and density calculations in Chapter 12 (`build/sections/12_ch12.html`) and Chapter 13 (`build/sections/13_ch13.html`), and dilution decision table in `build/verify_numbers.py`.
  - *Applicable Workspace Skills:* `synoptic-matrix-architect`, `blueprint-spec-sheet`, `state-scrubber-lab`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` Q7 p. 5 (defect S16), a problem states that solid solute was «izšķīdināti 100 mL šķīdinātāja». Students interpret this as adding $100\text{ mL}$ of water to the solute (resulting in a final volume $>100\text{ mL}$), whereas standard laboratory procedure dictates dissolving in a portion of solvent and diluting to the $100\text{ mL}$ calibration mark in a volumetric flask.
  - Students consistently confuse mass concentration $\gamma$ ($\text{g/L}$) with mass fraction $w$ (dimensionless or $\%$) and molar concentration $c$ ($\text{mol/L}$), or apply the dilution formula $c_1 V_1 = c_2 V_2$ treating $V_2$ as the added volume of water rather than the final total solution volume.
- **Why It Matters:**
  - Errors in preparing intravenous clinical solutions (e.g., potassium chloride, sodium chloride, dextrose) or pharmaceutical reconstitutions cause acute patient hyperosmolar complications or severe toxicity.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Codifying the 5 distinct solution calculation routes (Route A: mass fraction $w$; Route B: density $\rho = m/V$; Route C: mass concentration $\gamma = w\cdot\rho\cdot 10$ and molarity $c = \gamma/M$; Route D: dilution $c_1 V_1 = c_2 V_2$; Route E: graphical determination of $w$ from $\rho$); explicit volumetric protocol in volumetric flasks (diluting *to the mark*); clear table of common pitfalls.
  - *Out of Scope:* Non-ideal excess thermodynamic volume of mixing derivations.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Skoog et al. Chapter 2 & 5; Harris & Lucy Chapter 1; `S-2B` Q3; `build/claims.json` (Claim C16).
  - *Warrant Check:* All 4 warrant conditions passed. Mass and mole conservation governing dilutions are exact.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Solution Decision Route Matrix:* In `build/sections/12_ch12.html`, implement an aligned 5-route decision table mapping given inputs to target quantities and required formulas.
  2. *Volumetric Flask Protocol Clarification:* Insert a prominent `.role--rule` callout resolving S16, emphasizing that volumetric flasks are calibrated "to contain" ($In$) and must be filled until the bottom of the meniscus touches the ring mark.
  3. *Dilution Pitfall Inoculation:* In `build/sections/13_ch13.html`, insert a `.role--mistake` callout on $c_1 V_1 = c_2 V_2$, highlighting that $V_2 = V_1 + V_{\text{added}}$ (assuming volume additivity) and never $V_{\text{added}}$ alone.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T14.1: Route Table & Chapter 12 Refactor*
    1. In `build/sections/12_ch12.html`, insert the complete 5-route decision table matching `build/verify_numbers.py`.
    2. Add an explicit formula block for interconversion: $\gamma = w\cdot\rho\cdot 10$, where $w$ is in $\%$, $\rho$ in $\text{g/mL}$, and $\gamma$ in $\text{g/L}$.
    3. Run `python3 -I build/check_route_table.py --self-test` to verify route definitions.
  - *Subtask T14.2: Worked Clinical Case Alignment*
    1. In `build/sections/13_ch13.html`, align the worked dilution problem: preparing $500\text{ mL}$ of $0.100\text{ M}$ solution from $2.00\text{ M}$ stock ($V_1 = 25.0\text{ mL}$).
    2. Explicitly outline the laboratory steps: pipette $25.0\text{ mL}$ with volumetric transfer pipette into $500\text{ mL}$ volumetric flask, add water, swirl, dilute to mark, invert to mix.
    3. Run `python3 -I tools/check_pillars.py` to confirm worked example and mechanism coverage.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/12_ch12.html`, `build/sections/13_ch13.html`, `build/verify_numbers.py`, `build/check_route_table.py`.
  - *Selectors:* `.route-matrix`, `.volumetric-protocol`, `.role--mistake`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I build/check_route_table.py --check` passes with all 5 routes verified.
  - *Negative Test:* Setting $V_2$ as added solvent volume in the worked dilution example fails test assertions.
  - *A11y Test:* All route table headers have proper scope and accessible labels.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T04, T05; upstream of F08, B01.
  - *Collision Group:* Group D (Apparatus & Solutions).
  - *Rollback Plan:* Git checkout `build/sections/12_ch12.html` and `13_ch13.html`.
  - *Definition of Done:* 5 solution routes codified; S16 volumetric protocol clarified; dilution pitfalls eliminated.

---

### T15 — Design System Engineering: Strict Token Architecture, Measurable Typography, and Contrast Durability

- **Task ID & Decisive Title:** `T15` — Design System Engineering: Strict Token Architecture, Measurable Typography, and Contrast Durability
- **Classification & Governance Block:**
  - *Workstream:* Anti-AI-Slop UI & Retexturing
  - *Priority:* P2 (Polish & Refinement) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`tools/check_contrast.py` confirms WCAG 2.2 AA across light/dark tokens)
  - *Responsibility Boundary:* Owns global stylesheet `build/style.css`, design tokens in `:root`, typography measure, and contrast gate `tools/check_contrast.py`.
  - *Applicable Workspace Skills:* `impeccable`, `minimalist-ui`, `print-css-alchemist`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `build/style.css`, custom properties are categorized across 4 tiers (primitive, semantic, layout, component), but 152 custom-property declarations exist, including one-off component values.
  - While `tools/check_contrast.py` passes all tested token pairs (light ink on ground 14.96:1; dark ink on ground 15.14:1), CSS cascade layer rule bodies remain unwrapped because lightweight browsers (Falkon) drop `@layer` blocks (defect CSS-01).
  - Body text measure must be rigorously constrained between 60ch and 75ch (target 66ch) to maintain optimal reading cadence and prevent eye fatigue.
- **Why It Matters:**
  - Inconsistent design tokens, uncontrolled line measures ($>90\text{ch}$ on wide displays), and poor contrast cause visual fatigue during long study sessions and violate WCAG 2.2 AA accessibility standards.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Enforcing a strict 4-tier token hierarchy; guaranteeing comfortable 66ch reading measure on desktop; maintaining WCAG 2.2 AA contrast ($\ge 4.5:1$ text, $\ge 3.0:1$ UI) across light and dark themes; preserving fallback unwrapped styles for lightweight browser engines until safe layer polyfilling is proven.
  - *Out of Scope:* Adding decorative animations, drop shadows, or unmotivated multi-stop gradients.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* WCAG 2.2 Level AA; `docs/governance/ARCH_CSS_DOM_CONTRACTS.md`; Bringhurst's *The Elements of Typographic Style*.
  - *Warrant Check:* All 4 warrant conditions passed. Contrast and typographic measure criteria are objective.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Token Consolidation & Cleanup:* Audit all 152 custom properties in `build/style.css`, pruning redundant component variables and strictly organizing `:root` into primitive, semantic, layout, and component tiers.
  2. *Reading Measure & Typography Scale:* In `build/style.css`, bind `.chapter` prose containers to `max-width: var(--measure)` ($66\text{ch}$) and set body line-height to a consistent $1.55$.
  3. *Automated Contrast Gate Maintenance:* Run `python3 -I tools/check_contrast.py` to confirm that every semantic color token pair passes WCAG 2.2 AA in both light and dark modes.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T15.1: Token Hierarchy Audit & Cleanup*
    1. In `build/style.css`, inspect `:root` and verify hex fallbacks precede all OKLCH color definitions.
    2. Confirm dark theme overrides (`[data-theme="dark"]` and `@media (prefers-color-scheme: dark)`) map cleanly to semantic tokens.
    3. Run `python3 -I tools/check_contrast.py` and verify `CONTRAST-OK` output.
  - *Subtask T15.2: Typographic Measure & Layout Refactor*
    1. In `build/style.css`, set `--measure: 66ch` and bind `.chapter > p, .chapter > ul, .chapter > ol` to this width.
    2. Ensure tabular figures (`font-variant-numeric: tabular-nums`) are active on all `.calc`, `.data-table`, and numeric values.
    3. Run `python3 -I tools/check_font_glyphs.py` to ensure embedded WOFF2 fonts support tabular numerals.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/style.css`, `tools/check_contrast.py`, `tools/check_font_glyphs.py`.
  - *Selectors:* `:root`, `[data-theme="dark"]`, `.chapter`, `--measure`, `--font-mono`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_contrast.py` outputs `CONTRAST-OK` with all ratios $\ge 4.5:1$ for text and $\ge 3.0:1$ for UI.
  - *Negative Test:* Introducing a low-contrast token pair ($<4.5:1$) causes `check_contrast.py` to fail immediately.
  - *Visual Test:* Text columns do not exceed 75ch on viewports up to 2560px wide.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T08; upstream of T16, T17.
  - *Collision Group:* Group H (CSS & Design System).
  - *Rollback Plan:* Git checkout `build/style.css`.
  - *Definition of Done:* Design tokens clean and hierarchical; typography measure locked to 66ch; contrast fully gated.

---

### T16 — Interface De-Carding: Restrained Masthead, Typographic Hierarchy, and Semantic Callouts

- **Task ID & Decisive Title:** `T16` — Interface De-Carding: Restrained Masthead, Typographic Hierarchy, and Semantic Callouts
- **Classification & Governance Block:**
  - *Workstream:* Anti-AI-Slop UI & Retexturing
  - *Priority:* P2 (Polish & Refinement) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (HTML-03 closed; semantic roles audited)
  - *Responsibility Boundary:* Owns callout components (`.role`), chapter header mastheads (`.chapter-head`), and typography hierarchy across all chapter sections. Eliminates AI-slop card grids.
  - *Applicable Workspace Skills:* `tufte-margin-scholar`, `cognitive-deload-auditor`, `minimalist-ui`.
- **Observed Problem & Concrete Workspace Evidence:**
  - The document previously suffered from "card fatigue," where every paragraph, definition, and worked step was isolated inside an individual bordered card box, destroying long-form reading continuity.
  - While HTML-03 removed decorative box-shadows, certain chapters still employ arbitrary callout styles rather than adhering strictly to the three approved semantic roles: `.role--rule`, `.role--mistake`, and `.role--verified`.
  - Mastheads on chapter sections occasionally feature excessive vertical padding, pushing educational content below the fold.
- **Why It Matters:**
  - Fragmenting academic textbooks into uniform card grids destroys narrative flow, encourages skimming, and creates visual clutter.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Restoring continuous editorial reading flow by de-carding general text; restricting bordered callouts strictly to the three semantic roles (`.role--rule`, `.role--mistake`, `.role--verified`) plus neutral `.role--source`; enforcing a limit of $\le 2$ callouts per visible screen height; designing a compact, restrained chapter masthead.
  - *Out of Scope:* Removing necessary worked example boxes or interactive recall disclosures.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Edward Tufte (*Visual Display of Quantitative Information*); `docs/governance/ARCH_CSS_DOM_CONTRACTS.md` §DOM-CLASS-REGISTRY.
  - *Warrant Check:* All 4 warrant conditions passed. Editorial layout hierarchy enhances reading comprehension.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *De-Carding Markup Pass:* In `build/sections/*.html`, remove unnecessary `.card` wrapper containers surrounding continuous prose paragraphs.
  2. *Semantic Role Standardization:* Refactor all alert callouts to use strictly `.role.role--rule` (accent border), `.role.role--mistake` (mistake red border), or `.role.role--verified` (verified green border), ensuring neutral source citations use `.role--source`.
  3. *Masthead Consolidation:* In `build/style.css`, compact `.chapter-head` vertical padding and standardize heading margins.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T16.1: Callout & Semantic Role Refactor*
    1. Scan `build/sections/*.html` and replace custom alert classes with standardized `.role` elements.
    2. In `build/style.css`, verify that only `.role--rule`, `.role--mistake`, and `.role--verified` receive accent colors; `.role--source` must remain visually neutral.
    3. Run `python3 -I tools/check_contrast.py` to confirm callout border and text contrast compliance.
  - *Subtask T16.2: Masthead & Heading Scale Harmonization*
    1. In `build/style.css`, set `h1` to `clamp(1.75rem, 3vw, 2.25rem)` and `h2` to `clamp(1.35rem, 2.5vw, 1.75rem)`.
    2. Ensure `.chapter-head` contains only title, chapter number, learning outcome link, and brief lead paragraph.
    3. Run `python3 -I tools/check_anchors.py` to verify heading hierarchy (single `h1`, no skipped levels).
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/*.html`, `build/style.css`.
  - *Selectors:* `.chapter-head`, `.role`, `.role--rule`, `.role--mistake`, `.role--verified`, `.role--source`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_anchors.py` confirms exactly 1 `h1`, 17 `h2`, and zero skipped heading levels.
  - *Negative Test:* Grep across `build/` confirms 0 occurrences of `.card` wrapping plain prose paragraphs.
  - *Visual Test:* No more than 2 bordered callouts appear within any 800px viewport scroll height.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T15; upstream of T17, F04.
  - *Collision Group:* Group H (CSS & Typography).
  - *Rollback Plan:* Git checkout `build/style.css` and chapter templates.
  - *Definition of Done:* Continuous reading flow restored; semantic callouts strictly standardized; mastheads restrained.

---

### T17 — Fluid Responsive Layout: Intrinsic Sizing, Touch Targets, and Elimination of Forced Mobile Overflow

- **Task ID & Decisive Title:** `T17` — Fluid Responsive Layout: Intrinsic Sizing, Touch Targets, and Elimination of Forced Mobile Overflow
- **Classification & Governance Block:**
  - *Workstream:* Accessibility & Polish
  - *Priority:* P2 (Polish & Refinement) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (B05 verified fluid figure wrappers; zero fixed 820px inner widths survive)
  - *Responsibility Boundary:* Owns responsive breakpoints, viewport adaptability, touch target sizes, and horizontal scroll containment in `build/style.css`.
  - *Applicable Workspace Skills:* `break-ui`, `frontend-design`, `print-css-alchemist`.
- **Observed Problem & Concrete Workspace Evidence:**
  - Historical baseline files contained forced fixed widths (`.figure-scroll__inner { min-width: 820px; }`), forcing mobile users to pan horizontally to view figures. While B05 eliminated this rule, several interactive buttons (search clear, popover close, disclosure summaries) feature small click areas ($<32\text{px}$) violating mobile touch target recommendations.
  - Tables with multiple columns can produce unannounced horizontal overflow on narrow mobile viewports ($360\text{px}$–$390\text{px}$) unless wrapped in dedicated scrolling containers.
- **Why It Matters:**
  - Medical students accessing study guides on mobile devices in clinical hospital settings cannot operate sub-44px controls and suffer jarring horizontal layout breaks when scrolling wide tables.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Enforcing intrinsic responsive sizing (`minmax()`, `clamp()`, `auto-fit`); ensuring all interactive controls meet WCAG 2.2 Target Size minimum ($44\times 44\text{px}$ touch bounding box); providing visual scroll indicators (`.is-overflowing`) on tables; guaranteeing clean reflow from $360\text{px}$ mobile to $2560\text{px}$ desktop.
  - *Out of Scope:* Building separate mobile web apps or altering document content hierarchy between viewports.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* WCAG 2.2 Success Criterion 2.5.8 (Target Size Minimum); CSS Grid / Flexbox W3C Recommendations.
  - *Warrant Check:* All 4 warrant conditions passed. Touch target and responsive scaling standards are universal.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Touch Target Dimension Overhaul:* In `build/style.css`, enforce `min-height: 44px` and `min-width: 44px` across all button, link, and summary clickable targets on touch-capable devices.
  2. *Responsive Table & Figure Scroll Management:* Enhance `.table-scroll` and `.figure-scroll` with visual scroll shadow cues indicating unviewed horizontal content on narrow screens.
  3. *Fluid Vector Scaling Verification:* Ensure all 22 SVGs utilize `width: 100%; height: auto; max-width: 100%;` without fixed pixel width declarations.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T17.1: Interactive Control Target Sizing*
    1. In `build/style.css`, inspect `.search-btn`, `.popover-trigger`, `summary`, and `.nav-link` selectors.
    2. Add `padding: 0.6rem 0.8rem` and `min-height: 44px` to provide adequate touch hit areas.
    3. Verify that clickable areas do not overlap adjacent lines in dense mobile viewports.
  - *Subtask T17.2: Mobile Overflow & Grid Auditing*
    1. In `build/style.css`, verify `.vessel-grid` uses `grid-template-columns: repeat(auto-fit, minmax(140px, 1fr))`.
    2. Test that zero elements trigger body horizontal scrolling at viewport width $360\text{px}$.
    3. Run `python3 -I tools/check_figure_style.py` to confirm figure containers remain compliant.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/style.css`, `build/sections/*.html`.
  - *Selectors:* `.table-scroll`, `.figure-scroll`, `summary`, `.btn`, `.popover-trigger`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* Inspecting computed styles in browser confirms all interactive buttons measure $\ge 44\times 44\text{px}$.
  - *Negative Test:* Viewport width $360\text{px}$ produces zero horizontal window overflow (`window.innerWidth === document.documentElement.offsetWidth`).
  - *Print Test:* All scroll containers expand to full width in print layout without scrollbars.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T15, T16; upstream of F02.
  - *Collision Group:* Group H (CSS & Layout).
  - *Rollback Plan:* Git checkout `build/style.css`.
  - *Definition of Done:* Touch targets meet 44px standards; horizontal overflow eliminated; responsive reflow flawless.

---

### T18 — Structural Navigation and Quick-Reference Architecture: Canonical Section Anchors and Print Cards

- **Task ID & Decisive Title:** `T18` — Structural Navigation and Quick-Reference Architecture: Canonical Section Anchors and Print Cards
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (`tools/check_anchors.py` confirms 524 IDs, 706 links; `check_canonical.py` passes)
  - *Responsibility Boundary:* Owns document table of contents, in-page navigation anchors, Chapter 98 quick reference (`build/sections/98_quickref.html`), and anchor validation gate `tools/check_anchors.py`.
  - *Applicable Workspace Skills:* `print-css-alchemist`, `pdf-vector-surgeon`, `mook-visual-compendium`.
- **Observed Problem & Concrete Workspace Evidence:**
  - While `tools/check_anchors.py` confirms all 706 in-page links currently resolve, adding or editing chapter content frequently causes ID drift or breaks same-document hash jumps.
  - In `build/sections/98_quickref.html`, 33 canonical data bindings summarize core formulas and constants, but the print styling of this quick-reference card requires careful page-break protection to prevent formulas splitting across sheets.
  - The document header lacks a persistent, lightweight table of contents allowing students to jump directly to specific chapters without returning to the top.
- **Why It Matters:**
  - Broken anchor links disorient students attempting to cross-reference equations and definitions; splitting quick-reference summary cards across printed pages destroys their utility as lab bench aids.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Guaranteeing 100% anchor resolution across all 524 IDs via automated gate; authoring a high-density, multi-column print quick-reference card in Chapter 98 (`mook-visual-compendium`); integrating native CSS-driven jump navigation; enforcing strict kebab-case anchor naming (`#chN-topic`).
  - *Out of Scope:* Dynamic JavaScript scroll-spy tracking or external URL linking.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* WCAG 2.2 Success Criterion 2.4.1 (Bypass Blocks) & 2.4.2 (Page Titled); `docs/governance/ARCH_CSS_DOM_CONTRACTS.md`.
  - *Warrant Check:* All 4 warrant conditions passed. Deterministic anchor resolution is an engineering invariant.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Anchor Namespace Standardization:* Audit all 524 element IDs in `build/sections/*.html`, ensuring strict compliance with `#chN-kebab-case` naming conventions.
  2. *Quick-Reference High-Density Layout:* Refactor `build/sections/98_quickref.html` into an aligned 3-column reference sheet featuring formulas, SI units, and tolerance bounds.
  3. *Print Page-Break Enclosure:* Add explicit print CSS rules ensuring Chapter 98 prints on exactly two back-to-back pages without orphaned headings.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T18.1: Anchor & Heading Validation*
    1. Run `python3 -I tools/check_anchors.py` and inspect report: verify 1 `h1`, 17 `h2`, and 706 internal links.
    2. Ensure all `aria-labelledby` and `label for` references point to valid IDs.
    3. Run `python3 -I build/check_canonical.py --self-test` to confirm canonical source synchrony.
  - *Subtask T18.2: Quick Reference Print Sheet Formatting*
    1. In `build/sections/98_quickref.html`, wrap formula clusters in `.quickref-block` containers.
    2. In `build/style.css`, apply `@media print { .quickref-block { break-inside: avoid; } }`.
    3. Verify all 33 canonical formula bindings remain intact.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/98_quickref.html`, `build/sections/*.html`, `tools/check_anchors.py`, `build/check_canonical.py`.
  - *Selectors:* `.toc-nav`, `.quickref-grid`, `.quickref-block`, `#quickref`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_anchors.py` exits 0 with `ANCHORS-OK`.
  - *Negative Test:* Introducing an unmapped href target (e.g., `#ch10-missing`) causes `check_anchors.py` to exit 1.
  - *Print Test:* Chapter 98 exports cleanly without orphaned table rows or split equation blocks.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T08; upstream of F02, F04.
  - *Collision Group:* Group G (DOM Structure & Anchors).
  - *Rollback Plan:* Git checkout `build/sections/98_quickref.html`.
  - *Definition of Done:* All anchors verified; quick reference formatted as an aligned print compendium.

---

### T19 — Micro-Runtime Client Architecture: Bounded DOM Search, Zero-Storage Indexing, and Recall Privacy

- **Task ID & Decisive Title:** `T19` — Micro-Runtime Client Architecture: Bounded DOM Search, Zero-Storage Indexing, and Recall Privacy
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P0 (Immediate Truth & Stability) | *Impact:* 5 | *Effort:* 4
  - *Epistemic Status:* `[TESTED]` (`tools/check_index_privacy.py` passes; 0 recall answers reachable; 0 stored index blocks)
  - *Responsibility Boundary:* Owns client-side search architecture, search privacy gate `tools/check_index_privacy.py`, script budget gate `tools/check_budget.py`, and runtime migration of search from monolithic JS to Tier 3/4 compiled micro-runtime.
  - *Applicable Workspace Skills:* `tools/check_index_privacy.py`, `tools/check_budget.py`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In earlier builds, the workspace stored a massive JSON search index ($458,977\text{ bytes}$) inside a `<script type="application/json">` block, dramatically inflating document size and leaking answers. While T19 eliminated this stored index, the current runtime search implementation in `build/app.js` is still part of the bloated 41,938-byte monolithic script that violates the project budget ceiling (JS-01).
  - The runtime index must derive search blocks directly from the rendered DOM on first user interaction, while strictly skipping `.recall-answer` nodes, `.answer-sheet` elements, and hidden elements to preserve active-recall pedagogical integrity.
- **Why It Matters:**
  - Oversized client scripts bloat offline load times and violate project contracts; search engines that surface examination answers destroy retrieval practice for studying students.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Reducing client search logic to $\le 2,000\text{ bytes}$ and $\le 45\text{ lines}$ (Function J3 allocation in `INFRA_PYTHON_TS_JS_AUDIT.md`); deriving searchable blocks dynamically from DOM text; strictly skipping `.recall-answer`, `.answer-sheet`, and `[aria-hidden="true"]`; guaranteeing zero closed answers leak into search queries; maintaining exit 0 in `tools/check_index_privacy.py`.
  - *Out of Scope:* Storing pre-compiled JSON search indexes in the HTML deliverable or adding complex fuzzy regex search libraries.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* Project Governance Contract AGENTS.md §4 & §10; `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md`.
  - *Warrant Check:* All 4 warrant conditions passed. DOM-derived search maintains complete offline autonomy.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Search Logic Debloat & Algorithmic Reduction:* Streamline `build/app.js` search functions (`buildIndex`, `runSearch`, `renderSearch`), stripping redundant string normalization caches and consolidating into a compact micro-function.
  2. *Strict Exclusion Filter Enforcement:* Verify that the DOM crawler systematically skips all answer nodes matching `.recall-answer`, `.answer-sheet`, and `details:not([open]) .recall-content`.
  3. *Privacy & Budget Gate Verification:* Execute `python3 -I tools/check_index_privacy.py` and `tools/check_budget.py` to ensure search complies with privacy and budget ceilings.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T19.1: Search Micro-Runtime Optimization*
    1. In `build/app.js`, refactor `buildIndex()` to query only headings, paragraphs, and table cells, discarding decorative elements.
    2. Ensure query evaluation runs entirely in memory without creating persistent storage or cookies.
    3. Verify that search results display clean text snippets with clickable jump links to target chapter IDs.
  - *Subtask T19.2: Automated Privacy & Mutation Testing*
    1. Run `python3 -I tools/check_index_privacy.py` and confirm `INDEX-PRIVACY-OK` with 0 reachable answer phrases.
    2. Verify self-test teeth: confirm that synthetic answer phrase injection is caught by the test harness.
    3. Run `python3 -I tools/check_selfcontained.py` to verify zero network requests occur during search.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/app.js`, `tools/check_index_privacy.py`, `tools/check_budget.py`.
  - *Selectors:* `#search-input`, `#search-results`, `.recall-answer`, `.answer-sheet`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_index_privacy.py` passes across all 190 checked answers.
  - *Negative Test:* Forcing search crawler to index `.recall-answer` causes immediate test suite failure.
  - *Budget Test:* Shipped search implementation fits within the allocated 2,000-byte / 45-line micro-runtime budget.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T01, T08; upstream of B01, B04, F01.
  - *Collision Group:* Group I (Runtime & Scripts).
  - *Rollback Plan:* Git checkout `build/app.js`.
  - *Definition of Done:* Search operates dynamically from DOM; zero answers leak; privacy and budget gates strictly verified.

---

### T20 — Progressive Study Interaction: Native HTML5 Disclosures, Popover Glossary Previews, and Print State Unfolding

- **Task ID & Decisive Title:** `T20` — Progressive Study Interaction: Native HTML5 Disclosures, Popover Glossary Previews, and Print State Unfolding
- **Classification & Governance Block:**
  - *Workstream:* Architecture & Functionality
  - *Priority:* P1 (Core Accuracy) | *Impact:* 4 | *Effort:* 3
  - *Epistemic Status:* `[TESTED]` (178 native `<details>` elements, 60 popovers present in live master)
  - *Responsibility Boundary:* Owns native active-recall disclosures (`<details name="group">`), native Popover API term previews (`popover` / `popovertarget`), and print state unfolding styles in `build/style.css`.
  - *Applicable Workspace Skills:* `print-css-alchemist`, `interactive-study-guide`, `cognitive-deload-auditor`.
- **Observed Problem & Concrete Workspace Evidence:**
  - In `Master_2_tema_merijumi_un_grafiki.html`, there are 178 native `<details>` elements and 60 popover triggers. However, in print layout or with JavaScript disabled, improper disclosure rules can cause answer sheets to print twice (once inside the chapter and once in Chapter 15) or truncate content.
  - Defect JS-08 notes that while popovers and details exist, full zero-JS usability (navigating without JavaScript, viewing glossary previews via adjacent anchors, reading all 194 recall answers) requires systematic validation.
  - Certain mobile browsers experience clipping when popover elements open near the edge of the viewport.
- **Why It Matters:**
  - Medical students studying offline without JavaScript or printing revision packets require full access to self-testing questions and explanations without truncated boxes or redundant duplicated pages.
- **Intended End State & Scope Guardrails:**
  - *In Scope:* Native progressive enhancement using semantic HTML5; exclusive accordion behavior via `<details name="...">`; popover previews with native fallback anchor links to Chapter 14 glossary; complete `@media print` disclosure expansion (unfolding all details without duplicating Chapter 15 answer sheets); 100% zero-JS readability.
  - *Out of Scope:* Replacing native details with complex JavaScript-driven accordion plugins.
- **Authoritative Source / Book Backing & Warrant Check:**
  - *Authority:* HTML Living Standard §4.11.1 (The details element) & §4.11.3 (The popover attribute); `docs/governance/ARCH_CSS_DOM_CONTRACTS.md`.
  - *Warrant Check:* All 4 warrant conditions passed. Progressive enhancement guarantees universal offline accessibility.
- **THREE (3) Detailed Main Implementation Steps:**
  1. *Progressive Enhancement Audit:* Verify that all 178 `<details>` and 60 popover triggers operate using standard HTML5 attributes (`name`, `popover`, `popovertarget`) without requiring JavaScript event handlers.
  2. *Print Layout Disclosure Unfolding:* In `build/style.css`, craft resilient `@media print` rules: force `display: block !important` on `details > *`, apply `content-visibility: visible !important`, and hide duplicate print answer sheets.
  3. *Zero-JS Fallback Navigation:* Ensure that every popover trigger is paired with or wraps a standard in-page hash link (`<a href="#gloss-term">`) so users without popover support navigate directly to the glossary.
- **TWO (2) Named Subtasks, Each with EXACTLY THREE (3) Executable Substeps:**
  - *Subtask T20.1: Details & Popover Markup Refactor*
    1. In `build/sections/*.html`, inspect all recall questions and verify they utilize `<details class="recall-block">` with `<summary class="recall-summary">`.
    2. Verify popover buttons carry `popovertarget="pop-id"` and target containers carry `popover="auto"` and `id="pop-id"`.
    3. Run `python3 -I tools/check_anchors.py` to confirm all popover and details IDs resolve cleanly.
  - *Subtask T20.2: Print CSS Disclosure Unfolding*
    1. In `build/style.css`, update `@media print` to unroll all details elements automatically while suppressing interactive disclosure triangles.
    2. Add CSS rules preventing duplicate answer printing: `.answer-sheet--redundant { display: none !important; }`.
    3. Verify that printed pages display questions immediately followed by their worked solutions.
- **Affected Files, Selectors, Interfaces & Data Structures:**
  - *Files:* `build/sections/*.html`, `build/style.css`, `tools/check_counts.py`.
  - *Selectors:* `details.recall-block`, `summary.recall-summary`, `[popover]`, `[popovertarget]`, `@media print`.
- **Measurable Acceptance Criteria & Regression Tests:**
  - *Positive Test:* `python3 -I tools/check_counts.py` validates exactly 178 details elements and 194 recall answers.
  - *Negative Test:* Disabling JavaScript in browser smoke test allows 100% of questions and glossary links to be opened and read.
  - *Print Test:* Print preview shows all recall solutions expanded inline with zero clipped text containers.
- **Dependencies, Risks, Rollback & Definition of Done (DoD):**
  - *Upstream / Downstream:* Downstream of T15, T16; upstream of F04, B02.
  - *Collision Group:* Group H (CSS & Print).
  - *Rollback Plan:* Git checkout `build/style.css` and section files.
  - *Definition of Done:* Native HTML5 disclosures and popovers fully progressive; print unrolling flawless; zero-JS verified.

---

## 8. 10 Additive Feature Proposals (F01–F10)

### F01 — Bounded Offline In-Memory Search Engine

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F01` — Bounded Offline In-Memory Search Engine
   - *Value:* 5 | *Effort:* 3 | *Priority:* P0
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Vital for quick navigation across 16 chapters and 121 examinable concepts in a single-file offline document, provided it derives its index from the DOM at runtime and strictly respects the script byte budget.
2. **What Type of Feature It Is:** Client-side retrieval and keyword navigation micro-utility (Function J3 in the permitted micro-runtime).
3. **Why It Would Be Useful to Add:** First-year medical students studying for comprehensive examinations need to jump rapidly between related concepts across disparate chapters (e.g., locating every mention of "Beer–Lambert", "parallakse", or "standartnovirze") without scrolling through a 970 KB document.
4. **What It Tries to Accomplish:** Allows the learner to type search tokens into a fixed or modal search bar and receive instant, clickable jump links with excerpt snippets, without transmitting data across the network or storing an oversized static index in the HTML bundle.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* User focuses `#search-input` (or presses `/` or `Ctrl+K`) $\rightarrow$ On first interaction, `buildIndex()` extracts text from visible heading, paragraph, and table nodes (skipping `.recall-answer`, `.answer-sheet`, `[aria-hidden="true"]`) into an in-memory array $\rightarrow$ User types query $\rightarrow$ Tokenized matching filters blocks $\rightarrow$ Results populate `#search-results` with snippet highlights $\rightarrow$ Clicking a result scrolls smoothly to target chapter anchor and closes search.
   - *State Management:* Ephemeral in-memory array (`searchIndex = [{id, title, text}]`); zero persistence to `localStorage` or cookies.
   - *Implementation Steps:*
     1. In `build/app.js`, streamline `buildIndex()` to traverse only document content containers, stripping decorative punctuation and formatting into lowercase tokens.
     2. In `build/style.css`, style `#search-panel` as a clean, accessible overlay with high-contrast text and unmistakable focus rings.
     3. Bind keyboard shortcuts (`Escape` to close, `ArrowDown`/`ArrowUp` to navigate results, `Enter` to activate link).
6. **What Exact Changes an AI Agent Should Make:**
   - *Markup:* Add `<div id="search-panel" role="dialog" aria-modal="true" aria-label="Dokumenta meklēšana" hidden>` containing `<input type="search" id="search-input">` and `<div id="search-results" role="region" aria-live="polite">` in `build/sections/00_front.html`.
   - *CSS:* In `build/style.css`, define `#search-panel` with backdrop tint, responsive width (`min(600px, 90vw)`), and high-contrast result item styling.
   - *Script:* Refactor J3 search module in `build/app.js` to ensure total search code is $\le 2,000\text{ bytes}$ and $\le 45\text{ lines}$.
7. **Interoperability with Existing Workspace Features:** Integrates seamlessly with Chapter 14 glossary anchors and chapter headings; gracefully coexists with light/dark theme toggles; completely disabled during print view (`@media print { #search-panel { display: none !important; } }`).
8. **Failure States, Edge Cases & Accessibility:**
   - *Empty Query:* Clears results and displays count of indexed blocks.
   - *No Matches:* Displays helpful message: "Netika atrasts neviens atbilstošs termins."
   - *Zero-JS Fallback:* When JavaScript is disabled, `#search-panel` remains hidden, and learners rely on the static Table of Contents in Chapter 1 and alphabetical Glossary in Chapter 14.
   - *Accessibility:* Full ARIA dialog semantics, `aria-controls`, `aria-expanded`, focus trapped within modal until closed.
9. **Acceptance of Integration:**
   - Execute `python3 -I tools/check_index_privacy.py` $\rightarrow$ Confirm 0 recall answers reachable.
   - Execute `python3 -I tools/check_budget.py` $\rightarrow$ Confirm total script size meets budget ceilings.
   - Browser smoke test: typing "absorbance" returns jump links to Chapters 3 and 10; clicking navigates directly to anchor.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Search functions in-memory; zero network calls; privacy gate passes; script budget satisfied.
    - *Kill Criterion:* If search logic cannot be compressed under the 2,000-byte / 45-line micro-runtime ceiling, decline feature in favor of native browser search (`Ctrl+F`) paired with enhanced Chapter 14 glossary cross-links.

---

### F02 — Chapter-Local Section Sticky Navigators

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F02` — Chapter-Local Section Sticky Navigators
   - *Value:* 4 | *Effort:* 2 | *Priority:* P1
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Extremely high pedagogical value with zero JavaScript overhead. Uses pure CSS sticky positioning and native anchor links.
2. **What Type of Feature It Is:** Navigational structural enhancement (Tier 1: HTML5 + CSS).
3. **Why It Would Be Useful to Add:** Long chapters (e.g., Chapter 8 with 8 worked cases, or Chapter 11 with multi-step kinetics) cause disorientation during scrolling. A compact chapter-local sub-navigation bar keeps context visible.
4. **What It Tries to Accomplish:** Allows the learner to maintain situational awareness within a long chapter and instantly jump between introduction, worked examples, common mistakes, and recall checks.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* As user scrolls into `section.chapter`, a compact sub-nav strip (`nav.chapter-subnav`) docks below the viewport top $\rightarrow$ Clicking a subsection link jumps to `#chN-kebab-case` $\rightarrow$ Scrolling past the chapter smoothly releases the sticky dock.
   - *State Management:* Completely stateless; powered by native CSS `position: sticky; top: 0;`.
   - *Implementation Steps:*
     1. In `build/sections/*.html`, insert `<nav class="chapter-subnav" aria-label="Nodaļas saturs">` immediately following `.chapter-head`.
     2. In `build/style.css`, style `.chapter-subnav` with `position: sticky`, background tint, horizontal flex scroll, and 44px minimum tap targets.
     3. Ensure sub-nav is suppressed in print layout.
6. **What Exact Changes an AI Agent Should Make:**
   - *Markup:* Add sub-nav unordered lists in chapters with $>3$ subsections (`03_ch3.html`, `04_ch4.html`, `06_ch6.html`, `07_ch7.html`, `08_ch8.html`, `10_ch10.html`, `11_ch11.html`, `12_ch12.html`).
   - *CSS:* Add `.chapter-subnav { position: sticky; top: 0; z-index: 10; display: flex; gap: 0.5rem; overflow-x: auto; background: var(--surface); border-bottom: 1px solid var(--line); padding: 0.4rem 0; }`.
   - *Script:* Zero script modifications required.
7. **Interoperability with Existing Workspace Features:** Operates entirely within standard CSS cascade; inherits light/dark theme tokens; flattens completely in print views.
8. **Failure States, Edge Cases & Accessibility:**
   - *Narrow Mobile Viewports:* Flex container enables smooth native momentum scrolling (`-webkit-overflow-scrolling: touch`) with hidden scrollbars.
   - *Screen Readers:* Tagged with `aria-label="Nodaļas iekšējā navigācija"` so screen-reader users can bypass subsection jumps.
9. **Acceptance of Integration:**
   - Run `python3 -I tools/check_anchors.py` $\rightarrow$ Confirm every sub-nav href resolves to an existing in-page ID.
   - Inspect sticky dock behavior on mobile viewport ($375\text{px}$) to verify no horizontal window overflow.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* All major chapters equipped with sticky sub-nav; 100% anchor pass; zero script added.
    - *Kill Criterion:* If sticky docking causes layout jitter or overlaps with fixed headers on mobile, convert to static table of contents at chapter head.

---

### F03 — Unknown-Only Active-Recall Spaced Repetition Queue

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F03` — Unknown-Only Active-Recall Spaced Repetition Queue
   - *Value:* 2 | *Effort:* 4 | *Priority:* P3
   - *Adoption Verdict:* `[DOCUMENTED REJECTION / LEAN ALTERNATIVE PREFERRED]` — Adding client-side tracking, Leitner box state, and persistent queue logic in JavaScript directly violates the 4,096-byte script budget ceiling (JS-01) and requires silent `localStorage` tracking without pedagogical necessity.
2. **What Type of Feature It Is:** Client-side stateful adaptive assessment algorithm.
3. **Why It Would Be Useful to Add:** Allows learners to mark recall questions as "Zinu" (Known) or "Nezinu" (Unknown) and re-test only missed questions during exam cramming.
4. **What It Tries to Accomplish:** Spaced repetition and confidence-based retrieval filtering.
5. **How It Should Be Implemented (Architecture & Workflow - If Built):**
   - Would require writing state keys to `localStorage`, rendering a dynamic queue container, updating button classes, and managing state across sessions.
6. **What Exact Changes an AI Agent Should Make:**
   - Do **NOT** implement. Instead, implement the Lean Alternative: Native HTML5 checkboxes (`<input type="checkbox" class="recall-flag">`) paired with CSS `:has(:checked)` rules to visually dim mastered questions natively, with zero JavaScript.
7. **Interoperability with Existing Workspace Features:** A complex JS queue conflicts with print views and creates state corruption on multi-user library terminals.
8. **Failure States, Edge Cases & Accessibility:**
   - Storage disabled / private browsing causes JS queue to crash; screen readers struggle with dynamic DOM queue reshuffling.
9. **Acceptance of Integration:**
   - Rejection documented; lean native CSS alternative verified.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Documented rejection in roadmap; zero bytes added to `build/app.js`; native `<details>` recall model preserved.
    - *Kill Criterion:* Immediate rejection upon budget review.

---

### F04 — Printable Mixed Exam Revision Packet Generator

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F04` — Printable Mixed Exam Revision Packet Generator
   - *Value:* 5 | *Effort:* 3 | *Priority:* P1
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Extremely valuable for RSU medical students preparing for written paper-and-pencil midterms and final exams.
2. **What Type of Feature It Is:** Print-oriented compilation and active-recall assessment mode.
3. **Why It Would Be Useful to Add:** Students frequently print review materials to study away from screens; having a dedicated, clean exam revision packet without interactive disclosure clutter provides an authentic simulation of the RSU written examination.
4. **What It Tries to Accomplish:** Assembles representative problems from all 16 chapters into an authentic 2-part examination packet: Part 1: Blank question sheets with clinical case givens and lined answer areas; Part 2: Terminal answer key with complete worked steps and rubric explanations.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* User navigates to Chapter 15 (`#ch-15`) or selects "Drukāt eksāmena komplektu" $\rightarrow$ Document leverages `@media print` rules $\rightarrow$ Part 1 prints questions cleanly, forcing page breaks between sections $\rightarrow$ Part 2 prints terminal answer sheets (`.answer-sheet`) grouped at the end.
   - *State Management:* Completely stateless; managed via CSS `@page` and print classes.
   - *Implementation Steps:*
     1. In `build/sections/15_ch15.html`, structure the 4 comprehensive exam sets into clear Question and Answer Sheet divisions.
     2. In `build/style.css`, apply `@media print { .exam-packet { break-before: page; } .exam-answer-key { break-before: always; } }`.
     3. Verify that zero answers leak into Part 1 during print rendering.
6. **What Exact Changes an AI Agent Should Make:**
   - *Markup:* In `15_ch15.html`, wrap question prompts in `<div class="exam-question-sheet">` and worked answers in `<div class="exam-answer-sheet">`.
   - *CSS:* In `build/style.css`, add print rules: `@page :left { margin: 1.5cm; } @page :right { margin: 1.5cm; } .exam-workspace { min-height: 80px; border: 1px dashed var(--line); margin: 0.5rem 0; }`.
   - *Script:* Zero script modifications.
7. **Interoperability with Existing Workspace Features:** Works in perfect synergy with Chapter 15 exam manifests; does not disrupt on-screen reading; isolates answer keys to back of packet.
8. **Failure States, Edge Cases & Accessibility:**
   - *Screen Display:* On screen, questions and answers remain nested in accessible `<details>` blocks.
   - *Print Display:* In print, CSS unrolls questions and answers while suppressing interactive summary arrows.
9. **Acceptance of Integration:**
   - Export document to PDF via browser print preview $\rightarrow$ Verify that Question Sheets precede Answer Sheets with an explicit page break.
   - Verify that lined workspace boxes render cleanly on paper.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Dual question/answer sheet architecture implemented; print layout verified; zero script required.
    - *Kill Criterion:* If print engines fail to break cleanly between questions and answers, restrict packet to Chapter 15 terminal layout.

---

### F05 — Diagnostic Graph-Reading Workstation with Coordinate Crosshairs

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F05` — Diagnostic Graph-Reading Workstation with Coordinate Crosshairs
   - *Value:* 4 | *Effort:* 3 | *Priority:* P2
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Provides exceptional visual pedagogy for learning coordinate interpolation without introducing heavy script libraries.
2. **What Type of Feature It Is:** Visual pedagogical diagrammatic tool (Tier 1 CSS + SVG).
3. **Why It Would Be Useful to Add:** First-year students struggle with eye-tracking alignment when reading values from calibration lines (Chapter 10) or decay curves (Chapter 11), often introducing $\pm 10\%$ parallax reading error.
4. **What It Tries to Accomplish:** Allows the learner to hover over or click predetermined discrete data points on SVG figures to project semi-transparent crosshair guidelines to both axes, illustrating exact projection mechanics.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* Student views `SVG-17` (calibration) or `SVG-19` (decay) $\rightarrow$ Student focuses or hovers a sample point $\rightarrow$ SVG CSS `:hover` / `:focus` activates embedded `<line class="crosshair-x">` and `<line class="crosshair-y">` $\rightarrow$ Target axis ticks highlight with matching color.
   - *State Management:* Pure SVG CSS `:hover` and `:focus-visible` pseudo-classes; zero JavaScript state.
   - *Implementation Steps:*
     1. In `build/gen_figures.py`, embed `<g class="data-point-group" tabindex="0">` containing point circle and dashed projection lines with `opacity: 0; pointer-events: none;`.
     2. In `build/style.css`, add `.data-point-group:hover .crosshair, .data-point-group:focus .crosshair { opacity: 0.8; stroke-dasharray: 4; }`.
     3. Regenerate SVGs via `python3 -I build/gen_figures.py`.
6. **What Exact Changes an AI Agent Should Make:**
   - *Generator:* In `build/gen_figures.py`, update `calibration_svg()` and `half_life_svg()` to emit focusable data point groups with coordinate lines.
   - *CSS:* Add `.crosshair { stroke: var(--accent); stroke-width: 1.5; transition: opacity 0.15s ease; }` in `build/style.css`.
   - *Script:* Zero script modifications.
7. **Interoperability with Existing Workspace Features:** Completely vector-based; scales fluidly with SVG viewBox; honors `prefers-reduced-motion`; stays hidden in static print exports.
8. **Failure States, Edge Cases & Accessibility:**
   - *Touch Devices:* Tap activates focus state on mobile, revealing crosshairs; second tap dismisses.
   - *Screen Readers:* Data points carry descriptive `aria-label="Koncentrācija: 15.0 mg/L, Absorbance: 0.495"`.
9. **Acceptance of Integration:**
   - Hovering sample point on `SVG-17` highlights coordinate projections to $15.0\text{ mg/L}$ and $0.495$.
   - Run `python3 -I tools/check_figure_style.py` $\rightarrow$ Confirm zero `<style>` tags inside SVG.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Crosshair guidelines active across calibration and decay figures; pure CSS/SVG implementation; zero script overhead.
    - *Kill Criterion:* If touch browsers fail to clear focus on background tap, provide static dashed lines on worked examples instead.

---

### F06 — Accessible High-Precision Tabular Data Fallbacks for Plotted Curves

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F06` — Accessible High-Precision Tabular Data Fallbacks for Plotted Curves
   - *Value:* 5 | *Effort:* 2 | *Priority:* P1
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Core accessibility requirement. Fully implemented and maintained via `build/figure_data.py`.
2. **What Type of Feature It Is:** Accessibility and data-transparency tabular component.
3. **Why It Would Be Useful to Add:** Students using screen readers, students on low-power devices where SVG fails to paint (defect HTML-10), and students printing in high-contrast black-and-white need numerical data access.
4. **What It Tries to Accomplish:** Pairs every graphical plot with a collapsible, semantic data table containing exact experimental coordinates, calculated regression fits, and residual values.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* Below each plot figure, learner sees `<details class="figure-data-fallback">` $\rightarrow$ Expanding disclosure reveals clean tabular data with column headers, units, and recomputed regression values.
   - *State Management:* Native HTML5 `<details>` state.
   - *Implementation Steps:*
     1. Maintain `build/figure_data.py` to extract raw verified numbers from `build/verified.json`.
     2. In `build/build_doc.py`, inject tabular markup directly below each `{{FIG:...}}` placeholder.
     3. Ensure `tools/check_counts.py` gates table presence.
6. **What Exact Changes an AI Agent Should Make:**
   - *Build Pipeline:* In `build/figure_data.py`, ensure all 12 plot figures have corresponding data table generators.
   - *CSS:* Style `.figure-data-fallback table` with compact font, tabular numerals, and border-collapse.
7. **Interoperability with Existing Workspace Features:** Synchronized with `verified.json`; accessible to search crawler; unrolls automatically in print layout.
8. **Failure States, Edge Cases & Accessibility:**
   - *Zero-JS:* Works 100% natively without JavaScript.
   - *Screen Readers:* Fully navigatable using standard table reading shortcut keys (`Ctrl+Alt+Arrows`).
9. **Acceptance of Integration:**
   - Run `python3 -I build/check_figure_data.py --self-test` $\rightarrow$ Confirm 6 data plots, 38 plotted points agree with `verified.json`.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* All plot figures possess matching data tables; verified by automated gate.
    - *Kill Criterion:* Mandatory accessibility feature; cannot be killed.

---

### F07 — Interactive Calibration Residual Inspector and Limit-of-Linearity Explorer

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F07` — Interactive Calibration Residual Inspector and Limit-of-Linearity Explorer
   - *Value:* 3 | *Effort:* 4 | *Priority:* P3
   - *Adoption Verdict:* `[LOW-PRIORITY / DEFER]` — High pedagogical interest, but risks script budget inflation. Defer until Tier 3 TypeScript micro-runtime is fully established.
2. **What Type of Feature It Is:** Interactive graphical simulation widget.
3. **Why It Would Be Useful to Add:** Allows students to drag the upper calibration point and watch $R^2$ remain deceptively high while the residual plot blows up, driving home the lesson that $R^2$ alone is inadequate.
4. **What It Tries to Accomplish:** Active discovery learning for regression boundary conditions.
5. **How It Should Be Implemented (Architecture & Workflow - If Built):**
   - Implemented as an isolated interactive SVG with a slider updating residual bars in real-time.
6. **What Exact Changes an AI Agent Should Make:**
   - Defer implementation. Rely on static `SVG-17` and `SVG-18` paired with Section 10.3 prose in T11.
7. **Interoperability with Existing Workspace Features:** Requires careful script budgeting to prevent exceeding the 4,096-byte limit.
8. **Failure States, Edge Cases & Accessibility:**
   - High complexity for keyboard-only and screen-reader accessibility.
9. **Acceptance of Integration:**
   - Deferred status verified in roadmap.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Clear deferral documentation; zero budget consumed.
    - *Kill Criterion:* Reject if implementation exceeds 500 bytes of JavaScript.

---

### F08 — Interactive Clinical Solution & Dilution Decision Matrix

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F08` — Interactive Clinical Solution & Dilution Decision Matrix
   - *Value:* 5 | *Effort:* 3 | *Priority:* P1
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Outstanding clinical utility. Converts the 5 solution preparation routes into an accessible, filterable decision matrix using native CSS `:checked` states.
2. **What Type of Feature It Is:** Interactive decision support tool (Tier 1: HTML5 + CSS).
3. **Why It Would Be Useful to Add:** First-year medical students consistently choose the wrong formula when solving solution problems under exam pressure (e.g., trying to use $c_1 V_1 = c_2 V_2$ when density is given).
4. **What It Tries to Accomplish:** Allows the student to select "What I Have" (e.g., Mass fraction + Density) and "What I Need" (e.g., Molar concentration) to instantly isolate the single correct calculation route, eliminating formula confusion.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* Learner views Decision Matrix in Chapter 12 $\rightarrow$ Learner clicks radio button for target quantity (e.g., `[Need: Molar concentration c]`) $\rightarrow$ CSS `:checked` selectors highlight Route C while dimming irrelevant routes $\rightarrow$ Display reveals required formula ($\gamma = w\cdot\rho\cdot 10$, $c = \gamma/M$), step-by-step units, and common pitfalls.
   - *State Management:* Pure HTML `<input type="radio">` state; zero JavaScript.
   - *Implementation Steps:*
     1. In `build/sections/12_ch12.html`, construct the matrix with 5 radio options mapped to the 5 routes in `build/verify_numbers.py`.
     2. In `build/style.css`, implement radio-driven visibility: `.route-row { opacity: 0.35; transition: opacity 0.2s; } input#filter-c:checked ~ table .route-c { opacity: 1; font-weight: bold; }`.
     3. Verify that when no radio is selected, all 5 routes display with equal clarity.
6. **What Exact Changes an AI Agent Should Make:**
   - *Markup:* Add semantic filter radio buttons and route rows with matching `data-route` attributes in `12_ch12.html`.
   - *CSS:* Add `.matrix-filter` styling and `:checked` opacity rules in `build/style.css`.
   - *Script:* Zero script modifications.
7. **Interoperability with Existing Workspace Features:** Completely functional with JavaScript disabled; flattens into an all-routes reference table in print layout.
8. **Failure States, Edge Cases & Accessibility:**
   - *Keyboard:* Radio buttons grouped with standard `<fieldset>` and `<legend>` for native keyboard arrow navigation.
9. **Acceptance of Integration:**
   - Run `python3 -I build/check_route_table.py --check` $\rightarrow$ Confirm all 5 routes match verified schema.
   - Verify keyboard tab traversal and radio arrow navigation in browser smoke test.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Filterable decision matrix operational via native HTML/CSS; all 5 routes verified; zero script overhead.
    - *Kill Criterion:* If radio CSS creates selector specificity issues, retain static 5-route comparison table.

---

### F09 — Non-Zero Time-Origin Half-Life Decay Kinetic Visualizer

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F09` — Non-Zero Time-Origin Half-Life Decay Kinetic Visualizer
   - *Value:* 4 | *Effort:* 3 | *Priority:* P1
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Directly resolves course defect S18 and prevents the most common student error in Question 8.
2. **What Type of Feature It Is:** Diagrammatic visual comparator (Tier 1 CSS + SVG).
3. **Why It Would Be Useful to Add:** In Question 8, the time axis starts at $t_0 = 40\text{ min}$. Students struggle to mentally shift the origin to view elapsed time $\Delta t$.
4. **What It Tries to Accomplish:** Presents an interactive dual-panel toggle or split-view (`SVG-21`) contrasting the "Absolute Clock Time" view ($40 \rightarrow 98 \rightarrow 161\text{ min}$) against the "Elapsed Decay Time" view ($0 \rightarrow 58 \rightarrow 121\text{ min}$), demonstrating why $\Delta t$ is the true kinetic parameter.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* In Chapter 11, learner toggles between "Laboratorijas pulkstenis" and "Pagājušais laiks" via native radio tabs $\rightarrow$ Panel switches display to align successive halving intervals.
   - *State Management:* Native CSS `:checked` radio tabs.
   - *Implementation Steps:*
     1. Maintain dual-panel graphic `SVG-21` (`half-life-offset.svg`) generated by `gen_figures.py`.
     2. In `build/sections/11_ch11.html`, wrap figure in a tabbed container with `<input type="radio" name="hl-view">`.
     3. Verify `check_half_life_offset.py` passes.
6. **What Exact Changes an AI Agent Should Make:**
   - *Markup:* Add tab controls in `11_ch11.html`.
   - *CSS:* Add tab switching rules in `build/style.css`.
   - *Generator:* Maintain `half_life_offset_svg()` in `build/gen_figures.py`.
7. **Interoperability with Existing Workspace Features:** Responsive and self-contained; unrolls both panels side-by-side in print layout.
8. **Failure States, Edge Cases & Accessibility:**
   - *Zero-JS:* Operates 100% natively via CSS `:checked`.
   - *Screen Readers:* Accessible `<title>` and `<desc>` describe both coordinate frames.
9. **Acceptance of Integration:**
   - Run `python3 -I build/check_half_life_offset.py --self-test` $\rightarrow$ Outputs `HALF-LIFE-OFFSET-OK`.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Dual-panel visualizer functional; S18 origin offset clarified; automated check passes.
    - *Kill Criterion:* If tab markup disrupts print layout, display both panels sequentially in print.

---

### F10 — Automated Cryptographic Claim-Source Ledger Gate

1. **Feature ID, Title & Adoption Verdict:**
   - *ID & Title:* `F10` — Automated Cryptographic Claim-Source Ledger Gate
   - *Value:* 5 | *Effort:* 2 | *Priority:* P0
   - *Adoption Verdict:* `[RECOMMEND ADOPT]` — Foundational infrastructure for academic truth and anti-hallucination governance. Fully implemented in `tools/check_sources.py`.
2. **What Type of Feature It Is:** Deterministic verification and audit pipeline gate (Tier 2: Python 3).
3. **Why It Would Be Useful to Add:** Prevents silent drifting of course claims, ensures all bibliographic citations have verified hashes, and isolates unverified lecturer inquiries.
4. **What It Tries to Accomplish:** Cryptographically verifies all workspace sources against SHA-256 hashes, validates every claim needle in chapter text, and gates build execution on unresolved claims.
5. **How It Should Be Implemented (Architecture & Workflow):**
   - *End-to-End User Flow:* Executed by build scripts (`build_doc.py`) and CI audit gates $\rightarrow$ Verifies `build/sources.json` and `build/claims.json` $\rightarrow$ Reports status of all 20 claims $\rightarrow$ Exits 0 on verified claims; fails on invalid hashes or dropped needles.
   - *State Management:* Cryptographic JSON data models.
   - *Implementation Steps:*
     1. Maintain `build/sources.json` (7 sources with SHA-256) and `build/claims.json` (20 claims).
     2. Maintain CLI wrapper `tools/check_sources.py` forwarding to `build/check_sources.py`.
     3. Support `--strict-open` flag to enforce zero open claims for release builds.
6. **What Exact Changes an AI Agent Should Make:**
   - *Tooling:* Keep `tools/check_sources.py` synchronized with new source additions.
   - *Ledgers:* Update `claims.json` whenever faculty clarify open items (C20).
7. **Interoperability with Existing Workspace Features:** Standardized Python CLI contract (`python3 -I`); zero runtime dependencies; no network requests.
8. **Failure States, Edge Cases & Accessibility:**
   - Fails with explicit diff if a source PDF is modified or a needle phrase is edited in chapter markup.
9. **Acceptance of Integration:**
   - Run `python3 -I tools/check_sources.py` $\rightarrow$ Outputs `SOURCES-OK` (5 sources, 20 claims, C20 open).
   - Run with `--strict-open` $\rightarrow$ Exits 1 flagging open claim C20.
10. **Definition of Done (DoD) & Kill Criterion:**
    - *DoD:* Source ledger fully operational; cryptographic hashing enforced; mandatory build gate.
    - *Kill Criterion:* Core governance gate; cannot be killed.

---

## 9. 5 Bug-Fixing, Wiring, Debloating & False-Claim Crushing Tasks (B01–B05)

### B01 — Diagnostic Investigation: Arbitrary Calculator Input Integrity, Boundary Guards, and Floating-Point Precision

- **Task ID, Title & Classification:**
  - *ID & Title:* `B01` — Diagnostic Investigation: Arbitrary Calculator Input Integrity, Boundary Guards, and Floating-Point Precision
  - *Category:* Runtime Defect / Broken Wiring
  - *Severity:* High | *Epistemic Status:* `[CONFIRMED DEFECT]`
- **Observed Evidence & Reproduction / Diagnostic Procedure:**
  - *Location:* `build/app.js` (lines 350–650) and `Master_2_tema_merijumi_un_grafiki.html`.
  - *Reproduction Steps:*
    1. Open `Master_2_tema_merijumi_un_grafiki.html` in browser.
    2. In Chapter 10 calibration calculator (`#cal-run`), enter non-numeric text (`"abc"`), negative concentration (`"-5"`), or extreme value (`"1e25"`).
    3. Observe that raw JavaScript `parseFloat` produces `NaN` or unformatted scientific notation (`"NaN mg/L"`, `"-0.1504"` without boundary warnings).
    4. In solution dilution calculator (`#sol-run`), enter $V_2 < V_1$; calculator emits negative added solvent volume without flagging unphysical inputs.
- **Root-Cause Hypothesis & Execution/Propagation Trace:**
  - In `build/app.js`, calculator event handlers (`calRun`, `runSf`, `runHl`, `runSol`) lack strict defensive parsing guards.
  - User input string $\rightarrow$ `parseDecimal(val)` extracts float $\rightarrow$ arithmetic runs without range assertion $\rightarrow$ floating-point binary rounding artifacts ($0.1 + 0.2 = 0.30000000000000004$) propagate directly into the DOM output containers (`#cal-out`, `#sol-out`) $\rightarrow$ unhandled `NaN` values display directly to the learner.
- **Surgical Repair, Rewiring & Debloat Plan:**
  1. *Input Sanitization & Range Guarding:* Implement a strict numeric validator in `app.js` asserting that inputs are finite, positive, and within physical domain boundaries ($V > 0$, $A \ge 0$, $\rho > 0$, $w \in (0, 100)$).
  2. *Unphysical State Invalidation:* In dilution calculations, assert $V_2 \ge V_1$; if $V_2 < V_1$, output clear error state: "Kļūda: Gala tilpumam jābūt lielākam par sākuma tilpumu!"
  3. *Decimal Precision Formatting:* Wrap all output formatting in a strict decimal truncation helper (`formatSig(val, sigFigs)`) eliminating binary IEEE-754 representation noise.
- **Expected Behavior (Before vs. After):**
  - *Before:* Entering invalid or negative values emits `"NaN"`, unphysical negative volumes, or ugly floating-point noise (`"14.700000000000001"`).
  - *After:* Invalid inputs trigger immediate red validation error text; valid inputs format strictly to expected significant digits with explicit unit tags.
- **Regression Tests, Acceptance Criteria & Definition of Done (DoD):**
  - *Automated Test:* Run headless browser test asserting that entering `"-10"`, `"0"`, `"abc"` into all calculator fields produces clean localized error messages and zero console errors.
  - *DoD:* All 4 calculators defensively guarded; binary floating-point noise eliminated; unphysical inputs blocked.

---

### B02 — Diagnostic Investigation: Active-Recall Disclosure Unfolding, Answer Concealment, and Print Duplication Elimination

- **Task ID, Title & Classification:**
  - *ID & Title:* `B02` — Diagnostic Investigation: Active-Recall Disclosure Unfolding, Answer Concealment, and Print Duplication Elimination
  - *Category:* Broken Wiring / Layout Defect
  - *Severity:* Medium | *Epistemic Status:* `[CONFIRMED DEFECT]`
- **Observed Evidence & Reproduction / Diagnostic Procedure:**
  - *Location:* `build/sections/*.html`, `build/style.css`, and print PDF export.
  - *Reproduction Steps:*
    1. Print `Master_2_tema_merijumi_un_grafiki.html` to PDF using browser print preview.
    2. Inspect Chapter 7 Question 1 and Chapter 15 terminal exam sheets.
    3. Observe that without strict print CSS overrides, closed `<details>` elements either print blank (answers hidden from printed study guide) or print twice (once inside the chapter body and a second time in Chapter 15's compiled answer sheet).
- **Root-Cause Hypothesis & Execution/Propagation Trace:**
  - Modern rendering engines (Blink/Gecko/WebKit) treat `<details>` differently in print: Gecko historically clips closed details unless `content-visibility: visible` is explicitly applied.
  - Concurrently, Chapter 15 was designed as an independent exam answer sheet, resulting in duplicate printing of worked solutions when the entire document is printed in a single pass.
- **Surgical Repair, Rewiring & Debloat Plan:**
  1. *Print Disclosure Unfolding Rules:* In `build/style.css`, apply robust `@media print` rules: `details { display: block !important; } details > * { display: block !important; content-visibility: visible !important; } summary { display: none !important; }`.
  2. *Duplicate Answer Sheet Suppression:* Add class `.answer-sheet--redundant` to Chapter 15 print blocks, hiding them during full document print while displaying them when printing Chapter 15 alone.
  3. *Page Break Optimization:* Apply `break-inside: avoid` on all `.recall-block` elements to prevent question prompts from separating across page margins.
- **Expected Behavior (Before vs. After):**
  - *Before:* Printed PDF hides answers or prints duplicate solution sheets, wasting paper and splitting questions across page breaks.
  - *After:* Printed PDF seamlessly unrolls every question immediately followed by its worked answer, with zero duplication and clean page-break boundaries.
- **Regression Tests, Acceptance Criteria & Definition of Done (DoD):**
  - *Automated Test:* Verify via PDF export inspection that all 194 recall answers are visible in the printed output.
  - *DoD:* Print unrolling validated; duplicate answer sheets suppressed; page breaks clean.

---

### B03 — Diagnostic Investigation: High-Risk Course Source Conflict Adjudication and S1–S23 Claim Reconciliation

- **Task ID, Title & Classification:**
  - *ID & Title:* `B03` — Diagnostic Investigation: High-Risk Course Source Conflict Adjudication and S1–S23 Claim Reconciliation
  - *Category:* False-Claim & Source Crushing
  - *Severity:* Critical | *Epistemic Status:* `[CONFIRMED DEFECT]`
- **Observed Evidence & Reproduction / Diagnostic Procedure:**
  - *Location:* `build/claims.json`, `build/sources.json`, `B03_source_adjudication.md`, and course PDFs.
  - *Reproduction Steps:*
    1. Cross-reference `Analitiskas-metodes_2024.pdf` and `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` against `build/claims.json`.
    2. Confirm defects S1–S23: S1 (prefix arithmetic error $10^{-6}$), S2 (caesium symbol written as $^{133}\text{Cz}$), S4 (symbol $v$ for amount of substance), S5 (Beer–Lambert $a$ and non-SI units), S6 (repeatability conflated with trueness), S8 ($\sigma_{n-1}$ for sample SD), S11 (literal «10 ml» vs normalized «10 mL»), S18 (time origin offset).
    3. Run `python3 -I build/check_sources.py --strict-open`.
    4. Observe failure on Claim C20 (521 nm ascorbic acid chromogen).
- **Root-Cause Hypothesis & Execution/Propagation Trace:**
  - Course lecture slides and worksheets contain historical typos, legacy pre-2019 SI conventions, and conflated metrological terms inherited across academic years.
  - Without an explicit adjudication register, these defects propagate into student notes and conflict with international medical licensing standards.
- **Surgical Repair, Rewiring & Debloat Plan:**
  1. *Verbatim Quoting & Defect Annotation:* Preserve every source defect verbatim inside `<span data-quote="true">`, immediately followed by an explicit `.role--verified` or `.role--rule` correction explaining the exact standard departure.
  2. *Evaluation Closure for C19:* Keep Mercury-203 course datum ($46.595\text{ d}$) intact with label `avotā`, accompanied by primary evaluations (LNHB $46.594(12)\text{ d}$ and NuDat $46.610(10)\text{ d}$).
  3. *Formal Faculty Inquiry for C20:* Maintain Claim C20 as open with an explicit callout indicating that the chromogenic complexing reagent at 521 nm is unstated in course literature.
- **Expected Behavior (Before vs. After):**
  - *Before:* Course errors were either silently corrected (masking the course text) or left uncorrected (teaching false physics).
  - *After:* Course account is 100% transparently preserved, while students are taught the correct international scientific standard with cryptographic citation backing.
- **Regression Tests, Acceptance Criteria & Definition of Done (DoD):**
  - *Automated Test:* `python3 -I tools/check_sources.py` passes with `SOURCES-OK` (5 sources, 20 claims, C20 open).
  - *DoD:* All 23 course conflicts reconciled against PDFs; C19 primary-source verified; C20 clearly quarantined.

---

### B04 — Diagnostic Investigation: Search Index Privacy Leakage, Answer Exclusion, and Stale JSON Data Purging

- **Task ID, Title & Classification:**
  - *ID & Title:* `B04` — Diagnostic Investigation: Search Index Privacy Leakage, Answer Exclusion, and Stale JSON Data Purging
  - *Category:* Code & Asset Debloat
  - *Severity:* High | *Epistemic Status:* `[CONFIRMED DEFECT]`
- **Observed Evidence & Reproduction / Diagnostic Procedure:**
  - *Location:* `build/app.js`, `build/build_search_index.py`, `tools/check_index_privacy.py`, and historical master.
  - *Reproduction Steps:*
    1. Inspect historical baseline master: observe a 458,977-byte `<script type="application/json">` block containing static search data.
    2. Search for unique diagnostic phrases from Question 3 worked answers (e.g., `"Dixon Q 0,909"`).
    3. Observe that pre-compiled indexes surfaced examination solutions directly in search query previews, destroying retrieval practice.
- **Root-Cause Hypothesis & Execution/Propagation Trace:**
  - The build pipeline previously compiled every paragraph and answer into a static JSON payload embedded in the document, creating massive bloat and allowing search queries to match hidden text within closed details elements.
- **Surgical Repair, Rewiring & Debloat Plan:**
  1. *Eliminate Embedded JSON Index Block:* Completely purge the `<script type="application/json">` index block from `build_doc.py`, reducing HTML deliverable size by $\sim 450\text{ KB}$.
  2. *Dynamic DOM Crawler with Strict Exclusion Policy:* Refactor `build/app.js` to derive searchable text on-demand from rendered DOM elements, strictly ignoring `.recall-answer`, `.answer-sheet`, and `[aria-hidden="true"]`.
  3. *Automated Gate Verification:* Enforce zero leakage using `tools/check_index_privacy.py` (which re-derives index and asserts zero match with 190 checked answers).
- **Expected Behavior (Before vs. After):**
  - *Before:* 459 KB of static JSON index shipped; search revealed hidden exam answers.
  - *After:* 0 bytes of stored JSON index shipped; search derives from DOM dynamically; zero recall answers leak into query results.
- **Regression Tests, Acceptance Criteria & Definition of Done (DoD):**
  - *Automated Test:* `python3 -I tools/check_index_privacy.py` exits 0 with `INDEX-PRIVACY-OK` across 190 answers and 2,670 answer-only phrases.
  - *Self-Test:* Injected synthetic answer phrases are caught and cause immediate gate failure.
  - *DoD:* Zero stored JSON index in deliverable; 100% recall privacy maintained.

---

### B05 — Diagnostic Investigation: Generated SVG Style Duplication, Fixed-Width Responsive Clipping, and Scoped Vector Architecture

- **Task ID, Title & Classification:**
  - *ID & Title:* `B05` — Diagnostic Investigation: Generated SVG Style Duplication, Fixed-Width Responsive Clipping, and Scoped Vector Architecture
  - *Category:* Code & Asset Debloat / Layout Defect
  - *Severity:* Medium | *Epistemic Status:* `[CONFIRMED DEFECT]`
- **Observed Evidence & Reproduction / Diagnostic Procedure:**
  - *Location:* `build/gen_figures.py`, `build/style.css`, `build/figures/*.svg`, `tools/check_figure_style.py`.
  - *Reproduction Steps:*
    1. Inspect raw output of `build/gen_figures.py`: observe that every generated SVG previously embedded a byte-identical 935-byte `<style>` block (sha256 `031ba978ab49...`).
    2. Across 12 plot SVGs, this repeated identical styling 12 times (11,220 bytes, 10,285 bytes of pure redundancy).
    3. Concurrently, `build/style.css` carried 15 dead `.svg-*` rules with conflicting font-size and stroke-width values that matched nothing.
- **Root-Cause Hypothesis & Execution/Propagation Trace:**
  - `gen_figures.py` generated standalone SVG files with self-contained styles. When `build_doc.py` inlined these files directly into the master HTML, the stylesheet was duplicated 12 times within the document tree.
- **Surgical Repair, Rewiring & Debloat Plan:**
  1. *Centralize Vector Styles:* Strip all `<style>` blocks from `gen_figures.py` and centralize plot rules in `build/style.css`, scoped to `.figure-scroll svg`.
  2. *Purge Dead Rules:* Delete the 15 unreferenced `.svg-*` rules from `build/style.css`.
  3. *Enforce via Gate:* Implement `tools/check_figure_style.py` asserting that zero inline SVGs carry `<style>` tags, every plot class has a scoped document rule, and all 22 SVGs retain accessible `<title>` and `<desc>`.
- **Expected Behavior (Before vs. After):**
  - *Before:* 11.2 KB of duplicate `<style>` tags embedded across SVGs; 15 dead CSS rules; risk of styling drift.
  - *After:* 0 per-SVG `<style>` blocks; single scoped stylesheet in document CSS; 10.3 KB purged; 100% vector accessibility preserved.
- **Regression Tests, Acceptance Criteria & Definition of Done (DoD):**
  - *Automated Test:* `python3 -I tools/check_figure_style.py` exits 0 with `FIGURE-STYLE-OK`.
  - *DoD:* All SVG style duplication eliminated; dead rules purged; automated gate passes.

---

## 10. Master 35-Package Priority & Cross-Reference Matrix

The table below catalogs all 35 work packages across the workspace, establishing priority rankings, epistemic statuses, adoption verdicts, resource estimates, collision groups, and primary verification gates.

| ID | Title | Category / Workstream | Priority | Status / Adoption Verdict | Impact (1–5) | Effort (1–5) | Upstream Blockers | Collision Group | Primary Verification Gate |
|---|---|---|---|---|---|---|---|---|---|
| **T01** | Canonical Terminology Register & Lint | Terminology & Sourcing | P0 | `[TESTED]` Populated | 5 | 3 | None | Group A (Terms & Ch14) | `build/check_terms.py --strict` |
| **T02** | Spectrophotometric Rigor & Beer–Lambert | Terminology & Sourcing | P0 | `[TESTED]` Populated | 5 | 2 | T01 | Group B (Calibration & Ch10) | `build/check_calibration.py` |
| **T03** | Metrological Disambiguation (Trueness/Precision) | Pedagogy & Explanations | P0 | `[TESTED]` Populated | 5 | 3 | T01 | Group C (Metrology & Ch6) | `tools/check_pillars.py` |
| **T04** | Volumetric Glassware Classification | Architecture & Functionality | P1 | `[INSPECTED]` Populated | 4 | 3 | T01 | Group D (Apparatus & Ch4/5) | `tools/check_figure_style.py` |
| **T05** | Significant-Figure Arithmetic & Test Repair | Architecture & Functionality | P0 | `[TESTED]` Populated | 5 | 2 | T01 | Group E (Arithmetic & Ch8) | `build/check_sigfig_cases.py` |
| **T06** | Calibration Inversion & Density Sync | Pedagogy & Explanations | P1 | `[TESTED]` Populated | 4 | 3 | T02, T05 | Group B (Calibration & Ch10) | `build/verify_numbers.py` |
| **T07** | Scientific Prose Rhythm & Sentence Decomp. | Pedagogy & Explanations | P2 | `[TESTED]` Populated | 3 | 3 | T01, T03 | Group F (Prose & Content) | `build/check_prose_rhythm.py` |
| **T08** | Table & Figure Architecture & Captions | Architecture & Functionality | P1 | `[TESTED]` Populated | 4 | 3 | T01 | Group G (DOM & Metrics) | `tools/check_counts.py` |
| **T09** | Inferential Biostatistics (s, SEM, CI, t) | Pedagogy & Explanations | P1 | `[TESTED]` Populated | 5 | 3 | T01, T03 | Group C (Metrology & Ch6) | `build/verify_numbers.py` |
| **T10** | Mixed Operations Decision Tree | Pedagogy & Explanations | P1 | `[TESTED]` Populated | 4 | 3 | T05 | Group E (Arithmetic & Ch8) | `build/check_sigfig_cases.py` |
| **T11** | Calibration Residuals & Model Limits | SVG & Visual Pedagogy | P1 | `[TESTED]` Populated | 5 | 3 | T02, T06 | Group B (Calibration & Ch10) | `build/check_calibration.py` |
| **T12** | Procedural Graph Reading & Vector Tokens | SVG & Visual Pedagogy | P1 | `[TESTED]` Populated | 4 | 3 | T01, T08 | Group F (Figures & Ch9) | `build/check_graph_trainer.py` |
| **T13** | First-Order Radionuclide Decay Kinetics | Pedagogy & Explanations | P1 | `[TESTED]` Populated | 5 | 3 | T01, T05 | Group F (Kinetics & Ch11) | `build/check_half_life_offset.py` |
| **T14** | Clinical Solution Prep & 5-Route Matrix | Pedagogy & Explanations | P1 | `[TESTED]` Populated | 5 | 3 | T01, T04, T05 | Group D (Solutions & Ch12/13) | `build/check_route_table.py` |
| **T15** | Design System Tokens & Typography Measure | Anti-AI-Slop UI | P2 | `[TESTED]` Populated | 4 | 3 | T08 | Group H (CSS & Tokens) | `tools/check_contrast.py` |
| **T16** | Interface De-Carding & Semantic Roles | Anti-AI-Slop UI | P2 | `[TESTED]` Populated | 4 | 3 | T15 | Group H (CSS & Layout) | `tools/check_anchors.py` |
| **T17** | Fluid Responsive Layout & 44px Targets | Accessibility & Polish | P2 | `[TESTED]` Populated | 4 | 3 | T15, T16 | Group H (CSS & Responsive) | `tools/check_figure_style.py` |
| **T18** | Navigation Anchors & Quickref Print Cards | Architecture & Functionality | P1 | `[TESTED]` Populated | 4 | 3 | T01, T08 | Group G (DOM & Quickref) | `tools/check_anchors.py` |
| **T19** | Micro-Runtime Search & Recall Privacy | Architecture & Functionality | P0 | `[TESTED]` Populated | 5 | 4 | T01, T08 | Group I (Runtime & Scripts) | `tools/check_index_privacy.py` |
| **T20** | Progressive Disclosures & Print Unfolding | Architecture & Functionality | P1 | `[TESTED]` Populated | 4 | 3 | T15, T16 | Group H (CSS & Details) | `tools/check_counts.py` |
| **F01** | Bounded In-Memory Search Engine | Navigation Utility | P0 | `[RECOMMEND ADOPT]` | 5 | 3 | T19 | Group I (Runtime & Scripts) | `tools/check_budget.py` |
| **F02** | Chapter-Local Sticky Sub-Navigators | Navigation Structure | P1 | `[RECOMMEND ADOPT]` | 4 | 2 | T17, T18 | Group G (DOM Structure) | `tools/check_anchors.py` |
| **F03** | Unknown-Only Spaced Repetition Queue | Adaptive Assessment | P3 | `[DOCUMENTED REJECTION]` | 2 | 4 | T20 | Group I (Runtime & State) | Script Budget Review |
| **F04** | Printable Mixed Exam Revision Packet | Print Assessment Mode | P1 | `[RECOMMEND ADOPT]` | 5 | 3 | T16, T20 | Group G (Exam & Print) | PDF Print Inspection |
| **F05** | Diagnostic Coordinate Crosshairs | Visual Pedagogy | P2 | `[RECOMMEND ADOPT]` | 4 | 3 | T11, T12 | Group B (SVGs & Figures) | `tools/check_figure_style.py` |
| **F06** | High-Precision Fallback Data Tables | Accessibility Component | P1 | `[RECOMMEND ADOPT]` | 5 | 2 | T08, T11 | Group G (Data & Tables) | `build/check_figure_data.py` |
| **F07** | Interactive Calibration Residual Explorer | Simulation Widget | P3 | `[LOW-PRIORITY / DEFER]` | 3 | 4 | T11 | Group B (Widgets) | Micro-Runtime Ceiling |
| **F08** | Solution & Dilution Decision Matrix | Decision Support Tool | P1 | `[RECOMMEND ADOPT]` | 5 | 3 | T14 | Group D (Apparatus & Ch12) | `build/check_route_table.py` |
| **F09** | Non-Zero Origin Decay Kinetic Visualizer | Visual Comparator | P1 | `[RECOMMEND ADOPT]` | 4 | 3 | T13 | Group F (Kinetics & Figures) | `build/check_half_life_offset.py` |
| **F10** | Cryptographic Claim-Source Ledger Gate | Verification Gate | P0 | `[RECOMMEND ADOPT]` | 5 | 2 | None | Group A (Governance) | `tools/check_sources.py` |
| **B01** | Calculator Input Integrity & Range Guards | Runtime Defect / Wiring | P0 | `[CONFIRMED DEFECT]` | 5 | 3 | T05, T10 | Group I (Runtime Calculators) | Headless Browser Suite |
| **B02** | Recall Disclosure Unfolding & Print Dedupl. | Layout Defect / Wiring | P1 | `[CONFIRMED DEFECT]` | 4 | 3 | T20 | Group H (Print & Details) | PDF Export Multi-Page |
| **B03** | High-Risk Source Conflicts (S1–S23) | False-Claim Crushing | P0 | `[CONFIRMED DEFECT]` | 5 | 3 | F10 | Group A (Claims & Sources) | `tools/check_sources.py` |
| **B04** | Search Privacy Leakage & JSON Purging | Asset Debloat / Privacy | P0 | `[CONFIRMED DEFECT]` | 5 | 3 | T19 | Group I (Runtime & Search) | `tools/check_index_privacy.py` |
| **B05** | SVG Style Duplication & Responsive Audit | Asset Debloat / Layout | P1 | `[CONFIRMED DEFECT]` | 4 | 2 | T08 | Group B (SVGs & Styles) | `tools/check_figure_style.py` |

---

## 11. Dependency DAG, File-Collision Guards & Wave-by-Wave Execution Playbook

### 11.1 Sequenced Execution Waves

Implementation must proceed in strict linear waves. Tasks within a wave sharing distinct collision groups may execute in parallel; tasks touching the same collision group must execute sequentially with automated verification checkpoints.

```
WAVE 1 (P0: Truth, Provenance & Core Stability)
├── F10 (Claim Ledger Gate) ──> B03 (S1–S23 Source Conflict Crushing)
├── T01 (Terminology Lint & Register) ──┬──> T02 (Beer–Lambert & Absorbance)
│                                       └──> T03 (Metrological Disambiguation)
├── T05 (SigFig Decimal Arithmetic & Check Repair)
└── T19 (Micro-Runtime Search Architecture) ──┬──> B04 (Search Index Privacy Purge)
                                              └──> B01 (Calculator Input Guards)
                                              └──> F01 (In-Memory Search Optimization)

[WAVE 1 CHECKPOINT GATE: check_sources, check_terms, check_sigfig_cases, check_index_privacy, check_budget]

WAVE 2 (P1: Core Pedagogical, Structural & SVG Accuracy)
├── T04 (Volumetric Glassware Specs) ───────┬──> T14 (Clinical Solutions 5-Route Matrix)
│                                           └──> F08 (Interactive Decision Matrix)
├── T06 (Calibration Inversion & Density) ──┬──> T11 (Calibration Residuals & LOL)
│                                           └──> F06 (Plotted Curve Fallback Tables)
├── T08 (Table & Figure Captions) ──────────┬──> T12 (Graph Reading Procedure)
│                                           └──> B05 (SVG Style Deduplication)
├── T09 (Biostatistics: s, SEM, CI, t)
├── T10 (Mixed Operations Decision Tree)
├── T13 (Decay Kinetics & Non-Zero Origin) ────> F09 (Decay Origin Visualizer)
├── T18 (Anchors & Quickref Print Cards) ────> F02 (Chapter Sticky Sub-Nav)
└── T20 (Progressive Disclosures) ─────────┬──> B02 (Print Disclosure Unfolding)
                                           └──> F04 (Printable Mixed Exam Packet)

[WAVE 2 CHECKPOINT GATE: check_anchors, check_counts, check_figure_style, check_route_table, check_half_life_offset]

WAVE 3 (P2: Editorial Anti-AI-Slop Restyling & Accessibility)
├── T15 (Design Tokens & Typographic Measure) ──> T16 (Interface De-Carding & Semantic Roles)
├── T17 (Fluid Responsive Reflow & 44px Targets)
├── T07 (Prose Rhythm & Sentence Decomposition)
└── F05 (Diagnostic Coordinate Crosshairs)

[WAVE 3 CHECKPOINT GATE: check_contrast, check_prose_rhythm, check_figure_style, Falkon Screenshot Audit]

WAVE 4 (P3: Long-Tail Evaluation, Deferred Features & Final Debloat)
├── F03 (Documented Rejection of Complex Spaced Repetition Queue)
├── F07 (Formal Deferral Review of Interactive Residual Explorer)
└── Final Runtime Optimization (Strict TypeScript micro-runtime compilation to <= 4,096 bytes)

[FINAL RELEASE GATE: All 10 tools/ gates exit 0; SHA-256 hash locked; zero production mutation during audit]
```

### 11.2 File-Collision Groups & Parallelization Guards

To prevent race conditions and merge conflicts across parallel execution passes, work packages are segregated into 9 mutually exclusive collision groups:

| Collision Group | Governed File Paths & Shared Assets | Member Packages | Concurrency Rule |
|---|---|---|---|
| **Group A** | `build/terminology.json`, `build/sources.json`, `build/claims.json`, `build/sections/14_ch14.html`, `build/sections/16_ch16.html` | T01, F10, B03 | **Strictly Sequential.** Lock terminological registers before editing chapter references. |
| **Group B** | `build/sections/03_ch3.html`, `build/sections/10_ch10.html`, `build/figures/calibration*.svg`, `build/check_calibration.py` | T02, T06, T11, F05, F07, B05 | **Sequential within Group.** T02 establishes definitions before T06/T11 compute residuals. |
| **Group C** | `build/sections/06_ch6.html`, `build/sections/07_ch7.html`, `build/figures/target-plot.svg`, `build/figures/ci-coverage.svg` | T03, T09 | Parallel with Group B; sequential with each other. |
| **Group D** | `build/sections/04_ch4.html`, `build/sections/05_ch5.html`, `build/sections/12_ch12.html`, `build/sections/13_ch13.html`, `build/figures/glassware.html` | T04, T14, F08 | Parallel with Groups B & C. T04 apparatus precedes T14 solution prep. |
| **Group E** | `build/sections/07_ch7.html`, `build/sections/08_ch8.html`, `build/sigfig_cases.json`, `build/check_sigfig_cases.py` | T05, T10 | **Sequential.** T05 repairs check harness before T10 expands decision cases. |
| **Group F** | `build/sections/09_ch9.html`, `build/sections/11_ch11.html`, `build/figures/half-life*.svg`, `build/check_half_life_offset.py` | T07, T12, T13, F09 | Parallel with Groups B, C, D. |
| **Group G** | `build/sections/00_front.html`, `build/sections/15_ch15.html`, `build/sections/98_quickref.html`, `build/counts.json`, `tools/derive_counts.py` | T08, T18, F02, F04, F06 | **Sequential.** DOM structural metrics and navigation anchors. |
| **Group H** | `build/style.css` (tokens, typography, layout, print media, dark mode) | T15, T16, T17, T20, B02 | **Strictly Sequential.** CSS modifications must occur in single, validated batches. |
| **Group I** | `build/app.js` (client runtime, calculators, search engine, event listeners) | T19, F01, F03, B01, B04 | **Strictly Sequential.** All script changes governed by the shared 4,096-byte ceiling. |

---

## 12. Comprehensive Verification & QA Matrix

Every quality gate in `tools/` and `build/` is documented below with its exact CLI invocation, targeted failure modes, and required pass signature.

| Gate Name | CLI Invocation | Target Files & Scope Checked | Exit 0 Pass Signature | Failure Mode & Immediate Remediation |
|---|---|---|---|---|
| **Anchor Integrity Gate** | `python3 -I tools/check_anchors.py` | Canonical master HTML; all 524 IDs, 706 links, aria refs, heading hierarchy. | `ANCHORS-OK` | Duplicate IDs, dead hash targets, or skipped heading levels. Fix target ID or href in source fragment. |
| **Script & Byte Budget Gate** | `python3 -I tools/check_budget.py` | Master HTML executable script; UTF-8 bytes, line count, ratio, banned tokens, AGENTS size. | `BUDGET-OK` | Script bytes $>4,096$, lines $>100$, ratio $>2\%$, or inline event handlers. Migrate JS logic to HTML/CSS/Python. |
| **WCAG 2.2 Contrast Gate** | `python3 -I tools/check_contrast.py` | `build/style.css` token pairs across Light and Dark themes. | `CONTRAST-OK` | Normal text contrast $<4.5:1$ or UI contrast $<3.0:1$. Adjust ground or ink OKLCH/hex token values. |
| **Metric Drift Gate** | `python3 -I tools/check_counts.py` | Compares live master DOM elements against `build/counts.json`. | `COUNTS-OK` | Tables, figures, SVGs, details, or IDs drift from record. Run `derive_counts.py` during authorized product pass. |
| **Figure Styling Gate** | `python3 -I tools/check_figure_style.py` | Master HTML inline SVGs; checks for duplicate `<style>` tags and scoped rules. | `FIGURE-STYLE-OK` | Inlined `<style>` inside `<svg>` or missing scoped document rule. Centralize styles in `style.css`. |
| **Font Glyph Coverage Gate** | `python3 -I tools/check_font_glyphs.py` | Decodes 5 embedded WOFF2 `@font-face` cmap tables against `_font_chars.txt`. | `FONTGLYPHS-OK` | Missing mathematical or diacritic glyphs. Re-subset fonts with `pyftsubset` including all required characters. |
| **Search Privacy Gate** | `python3 -I tools/check_index_privacy.py` | Re-derives search index; compares against 190 recall answers and 2,670 answer phrases. | `INDEX-PRIVACY-OK` | Closed answer phrases discoverable in search. Update skip policy in `buildIndex()` to exclude `.recall-answer`. |
| **Five-Pillar Coverage Gate** | `python3 -I tools/check_pillars.py` | Scans 121 examinable concepts in `concepts.json` across 16 chapters. | `PILLARS-OK` | Unlocatable concept label or missing chapter pillar. Add definition, mechanism, example, or mistake block. |
| **Self-Containment Gate** | `python3 -I tools/check_selfcontained.py` | Scans master HTML for external URLs, remote fonts, and network APIs (`fetch`, `XHR`). | `SELFCONTAINED-OK` | External URI outside W3C namespace or runtime network call. Inline asset or strip network API. |
| **Source Ledger Gate** | `python3 -I tools/check_sources.py` | Validates `sources.json` and `claims.json` SHA-256 hashes and text needles. | `SOURCES-OK` | Modified source PDF or dropped chapter text needle. Restore original PDF or update needle. |
| **SigFig Arithmetic Gate** | `python3 -I build/check_sigfig_cases.py --check` | Validates 23 cases in `sigfig_cases.json` against chapter case tables via `Decimal`. | `all cases match Decimal recompute` | Intermediate rounding drift or table alignment failure. Synchronize table with Decimal recomputation. |
| **Calibration Fit Gate** | `python3 -I build/check_calibration.py --self-test` | Recomputes linear regression, residuals, and sample inversions for Question 7. | `calibration self-test: ... OK` | Mutated slope, intercept, or altered residual signs. Revert regression parameters to verified standards. |
| **Half-Life Offset Gate** | `python3 -I build/check_half_life_offset.py --self-test` | Recomputes Question 8 non-zero time origin kinetics ($t_0 = 40\text{ min}$). | `HALF-LIFE-OFFSET-OK` | Incorrect subtraction of $t_0$ or altered half-life intervals. Verify $\Delta t_1 = 58$, $\Delta t_2 = 63\text{ min}$. |
| **Prose Rhythm Gate** | `python3 -I build/check_prose_rhythm.py` | Scans chapter fragments for paragraphs $\ge 45$ words and em dash frequency. | `PROSE-OK` | Long paragraphs $>70$ or em dashes $>40$. Decompose compound sentences into single-mechanism statements. |
| **Route Table Gate** | `python3 -I build/check_route_table.py --check` | Validates all 5 solution preparation routes in Chapter 12 against verified schemas. | `ROUTES-OK` | Missing formula, ambiguous unit conversion, or conflicting route IDs. Synchronize with `verify_numbers.py`. |

---

## 13. Open Questions, Unresolved Source Conflicts & Environment Inspection Limitations

### 13.1 Open Pedagogical & Faculty Inquiries (V-Confidence Items)

The following items are preserved as open inquiries awaiting formal resolution by RSU Medical Chemistry faculty:

1. **Claim C20 — Chromogenic Reagent at 521 nm:**
   - *Issue:* Laboratory worksheets 2A Q5 and 2026 Q7 specify ascorbic acid spectrophotometric determination at 521 nm. Ascorbic acid is a colorless enediol compound with UV absorbance ($\lambda_{\max} \approx 245\text{ nm}$ in acidic solution, $\sim 265\text{ nm}$ at neutral pH) and zero intrinsic absorption at 521 nm. A chromogenic complexing reagent (e.g., 2,4-dinitrophenylhydrazine, iron(III) thiocyanate complex, or phosphotungstic acid) must be present in the laboratory assay.
   - *Status:* **OPEN.** Neither course slides nor seminar answer keys identify the chemical chromogen. The roadmap strictly prohibits inventing a specific reagent. Retained with prominent annotation: «Avotā nav norādīts».
2. **Nomenclature of «drošības intervāls» vs «ticamības intervāls»:**
   - *Issue:* Course source Analitiskās metodes p. 4 uses «drošības intervāls» (safety interval) when describing Student's $t$ confidence intervals. In modern Latvian metrology and ISO standards, «ticamības intervāls» is the mandatory term.
   - *Status:* **PROVISIONAL RESOLUTION.** The textbook actively teaches «ticamības intervāls», preserving «drošības intervāls» only inside verbatim source quotations (`data-quote="true"`). Faculty confirmation requested for upcoming exam rubrics.
3. **Reference Value Terminology («reālā vērtība» vs «atsauces vērtība»):**
   - *Issue:* Course text occasionally refers to «reālā vērtība» (real value). Metrologically, true value (*patiesā vērtība*) is unknowable, and experimental calibration relies on a certified reference value (*atsauces vērtība*).
   - *Status:* Maintained with explanatory footnote distinguishing conventional course phrasing from VIM 3 definitions.
4. **Fume Hood Equipment Nomenclature:**
   - *Issue:* Colloquial laboratory slang «tvaika nosūcējs» appears in historical notes. Modern chemical safety standards require «velkmes skapis» (fume hood).
   - *Status:* Canonical term set to «velkmes skapis».

### 13.2 Environment & Tool Inspection Limitations

In strict adherence to §1.3 and §4.4, the following environmental constraints governed this audit:

1. **SVG Vector Geometry Rendering Limitation (HTML-10):**
   - Headless execution in virtual X11 display contexts (Xvfb) using Falkon (`/usr/bin/falkon`) successfully verifies document layout, typography, and container bounding boxes, but QtWebEngine drops SVG vector path rasterization, rendering empty plot areas.
   - *Declaration:* All SVG visual claims in this roadmap are designated as `[CODE-ONLY VISUAL AUDIT]`. Visual geometry must be accepted only via direct screenshot inspection in a fully supported rendering engine.
2. **Missing TypeScript Compiler (INFRA-01):**
   - `which tsc` reports that TypeScript is not installed on the system PATH. Executing Tier 3 compilation requires provisioning an offline TypeScript compiler (`npm install --no-save typescript` or local Node runner). Direct editing of JavaScript source violates Tier 3 governance until the compiler is provisioned.
3. **Absence of Git Repository (GOV-02):**
   - The workspace root is not a Git repository (`git status` exits non-zero). Workspace integrity and rollback mechanisms are maintained via cryptographic SHA-256 manifests (`.cache/manifest.json` and `tools/make_manifest.py`).

---

## 14. Implementation Agent Handoff Protocol

### 14.1 Mandatory Non-Negotiable Operating Rules

Any autonomous agent executing tasks from this roadmap must strictly observe the following rules:

1. **Zero Direct Hand-Editing of Master HTML:**
   - `Master_2_tema_merijumi_un_grafiki.html` is a generated artifact. Never edit this file directly.
   - All modifications must be made to source fragments in `build/sections/*.html`, styles in `build/style.css`, client logic in `build/app.js`, or generator scripts in `build/gen_figures.py`.
   - The master is recompiled strictly via `python3 -I build/build_doc.py`.
2. **Strict Read-Only Source Protection:**
   - Never modify the five course source PDFs (`2A_...pdf`, `2B_...pdf`, `2_SEM_...pdf`, `2_Temata...pdf`, `Analitiskas...pdf`), the frozen baseline files in `build/baseline/`, or skills in `workspace_skills/`.
3. **Budget Ceiling Compliance (JS-01):**
   - The shipped inline executable script must never exceed $\min(4,096\text{ bytes}, 100\text{ lines}, 2\%\text{ of HTML})$. Any task touching JavaScript must run `python3 -I tools/check_budget.py` before completing.
4. **Sequential Collision Group Discipline:**
   - Never execute tasks from the same collision group in parallel. Run the wave verification gate after every individual task integration.
5. **Epistemic Honesty:**
   - Never mark a gate as passed without executing the tool. If a tool fails, report the failure and halt execution.

### 14.2 Step-by-Step Wave Execution Instructions

To execute Wave 1:
```bash
# 1. Pre-execution verification checkpoint
python3 -I tools/check_sources.py
python3 -I tools/check_anchors.py
python3 -I tools/check_counts.py

# 2. Execute Task T05 (Repair SigFig Checker Harness)
# Modify build/check_sigfig_cases.py to parse static HTML tables instead of app.js
python3 -I build/check_sigfig_cases.py --check

# 3. Execute Task T01 (Canonical Terminology & Lint)
# Update build/terminology.json and run strict term lint
python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --strict

# 4. Rebuild document and verify integrity
python3 -I build/build_doc.py
python3 -I tools/check_counts.py
python3 -I tools/check_anchors.py
```

---

