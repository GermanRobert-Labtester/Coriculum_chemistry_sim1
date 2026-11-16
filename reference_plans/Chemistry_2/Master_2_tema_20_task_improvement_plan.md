# Master 2. tēma — 20-Task Improvement, Restyle & Feature Plan

**Target deliverable:** `/home/robertsrff/Chemistry_Med/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html`
**Baseline inspected:** 2026-10-31 build, 458,548 bytes; 97-page A4 PDF, 549 KB
**Plan date:** 2026-11-01
**Language of deliverable:** Latvian (`lang="lv"`); this working plan is in English with Latvian strings quoted verbatim.
**Purpose:** a staged, testable backlog for terminology correction, factual/editorial repair, explanation quality, anti-slop redesign, restyling, accessibility, print, and high-value study features.

> Read this together with `AGENTS.md` and `PROMPT_Master_html_2_tema.md`. Where this plan and those files disagree, the prompt wins on content/design and `AGENTS.md` wins on workspace rules. No source PDF or `workspace_skills/` file may be edited.

---

## 0. How to use this plan

1. **Do not start with the visual restyle.** The document’s credibility rests on numbers and terminology. Waves 1–3 fix correctness and comprehension first; Waves 4–5 restyle and add features on a stable content base.
2. **Freeze a baseline before editing.** Copy the current HTML and PDF into `build/baseline/` (not the root), record hashes, and keep the original 97-page PDF for comparison.
3. **One task = one reviewable change set.** Each task below has its own acceptance checks. Do not batch unrelated terminology, arithmetic, and layout changes into one un-reviewable commit.
4. **Every content change is logged.** New corrections join the existing S1–S23/D24 register as D25+ and are shown in the change log with location, original, correction, reason, confidence.
5. **No new runtime dependency.** Search, trainers, filters, and persistence must be vanilla JS/CSS or build-time Python. No CDN, no network font, no analytics, no localStorage without explicit consent.
6. **No gamification.** Progress is a plain state, not XP, streaks, badges, confetti, or “mastery” scores. The document remains a study aid, not an app.
7. **No invented facts.** Where a source is silent, write «avotā nav norādīts»; where this plan proposes standard knowledge, label it «papildinājums»; where numbers are illustrative, label «ilustratīvs piemērs».

---

## 0.1 Executive summary — the ten moves that matter most

1. **Fix the arithmetic self-contradictions first.** The 161/161,0 hypothetical, the exact-3 rationale, the density 1,0334/1,033 conflict, and the “ceturtā zīme” count are small edits that protect the document’s credibility.
2. **Resolve the terminology contradictions, not just the glossary.** `absorbcija` as a quantity, sensitivity vs LOD, and the three “accuracy” labels are the highest-risk vocabulary issues.
3. **Make terminology and arithmetic executable.** A term checker and a Decimal-based sig-fig harness turn two good intentions into build gates.
4. **Audit every table and figure once.** 46 tables and 10 figures are the surface where unsourced claims hide; the heat-resistance and LOD/LOQ cells prove the point.
5. **Explain the four hardest concepts properly.** n−1/degrees of freedom; mixed significant-figure operations; what a calibration line cannot prove; and half-life when the data do not start at t=0.
6. **Cut the reading weight.** Split the 103 long paragraphs and 41 long sentences; reduce the 58 em dashes; turn the rhetorical heading into a declarative one.
7. **Install a type and spacing system.** Replace 15 ad-hoc sizes with a seven-step scale, normalise spacing, and add a true italic face instead of faux oblique.
8. **De-card the page and redesign the opening.** Remove the hero CTA row, open up the 44 role boxes, keep one functional panel for instruments, and make the first screen read like a reference document.
9. **Stop forcing phones to read sideways.** Stack small comparison tables, keep sticky first columns for true matrices, and give the vessel matrix a per-vessel mobile view.
10. **Add the study workspace only after the content is stable.** Search, section navigation, recall filters, exam mode, and a 4–6 page quick reference are the highest-value features; they should sit on a corrected document, not a moving one.

**Two decisions need the lecturer before T03/T06 can close:** the Latvian umbrella term for accuracy, and the expected reported precision for the calibration slope and the density example. Both are marked `V` and have ready-to-paste lecturer questions in §7.

---

## 1. Deep inspection: evidence and scorecard

### 1.1 Snapshot

| Metric | Current value | How measured |
|---|---|---:|
| HTML size | 458,548 bytes | `stat` |
| Chapters | 16 | `section.chapter` |
| Visible/plain text | ~21,850 visible words; 26,773 tokenised words | inspect report; local text extraction |
| Desktop height | ~96,300 px; ~107 screens at 1440×900 | Playwright |
| Print edition | 97 A4 pages | `pdfinfo` |
| Recall items | 113 total; 48 in ch. 15 | DOM count |
| Mistakes catalogue | 48 rows | DOM count |
| Tables | 46 | DOM count |
| Figures | 10 inline SVGs | DOM count |
| MathML blocks | 13 | DOM count |
| Details disclosures | 117 | DOM count |
| Instruments | 3 (sig figs, calibration, half-life) | DOM count |
| Defect register | S1–S23 + D24 = 24 entries; 14 C, 7 H, 2 H/V, 1 C/H | change-log parse |
| Concept inventory | 121/121 mapped to recall tags | `build/concepts.json` |
| External URLs / storage | 0 / 0 | grep |
| Lint | 0 FAIL, 1 WARN (58 em dashes) | `lint.mjs` |
| Inspect | 0 FAIL, 5 WARN with documented allowances | `inspect.mjs` |
| Contrast (light) | ink 14.96:1; ink-2 6.51:1; accent 6.64:1; rules 7.47:1; mistake 7.19:1 | computed sRGB + WCAG luminance |
| Body type | MCh Text 18 px / 1.62, measure 68 ch | computed CSS |
| Type sizes | 15 sizes at first viewport; 97 `font-size` declarations overall | inspect + CSS audit |
| Print flow observed | p96 ends after D questions with blank third; p97 is appendix E + compact footer | PDF page inspection |

### 1.2 Editorial scorecard (not a certification)

| Dimension | Score /5 | Why |
|---|---:|---|
| Factual/arithmetic reliability | 3.5 | Strong independent recomputation and a serious defect log, but several precision leaks remain (see §1.4). |
| Terminology consistency | 3.5 | A good glossary and explicit policy, undone by local contradictions (`absorbcija` as a quantity, two “accuracy” terms). |
| Prose clarity | 3.0 | Plain and often excellent, but 103 paragraphs exceed 45 words, 41 sentences exceed 35 words, and 58 em dashes accumulate. |
| Explanation depth | 4.0 | Worked examples and “why” passages are a strength; the weakest links are degrees of freedom, mixed significant-figure operations, and LOD/LOQ. |
| Study efficacy | 4.0 | 113 closed prompts, retrieval practice, annotated wrong solutions, outcome transfer tasks. Missing filters, review queue, and exam simulation. |
| Visual design | 3.5 | Calm palette, real data graphics, strong typographic voice; but 15 sizes, 44 role boxes, 5 boxed card rows, and a hero-like 75 px masthead push it toward an app landing page. |
| Accessibility | 3.5 | Good landmarks, captions, scopes, SVG titles, focus styles, and touch targets; no axe run, mobile tables require sideways reading, MathML font fallback warning. |
| Print | 3.5 | Honest running header, real page numbers, all details open; 97 pages with a forced appendix break and a compact footer create a near-empty page 96. |
| **Overall** | **3.6 / 5** | A strong reference draft that needs a precision/terminology pass, a reading-experience pass, and a deliberate anti-slop restyle. |

### 1.3 Verified strengths — do not break them

- The document is genuinely self-contained: 0 external URLs, 0 storage calls, two embedded WOFF2 faces, no runtime fetch.
- The defect log is unusually honest: S1–S23 plus D24, with confidence labels; source silence is stated, not filled with invented values.
- Every calculation in the main worked examples was independently recomputed (calibration slope 0.032165714, intercept 0.0106, R² 0.998933; Q3 mean 12.70, s 0.304, SEM 0.176, CI ±0.76; density 1.0334, w 4.86%; half-life 232.5 s).
- The three semantic roles have a label and a non-colour cue; contrast passes WCAG AA in the light theme.
- The print edition has a real running header, page numbers, open disclosures, and figures that survive print.
- The recall design is pedagogically sound: closed `<details>`, no score gimmicks, no persistence by default.
- The figures use real data geometry and avoid decorative chartjunk; the calibration and half-life plots are generated from data, not hand-drawn.

### 1.4 Findings register

The IDs below are the working register for this plan. They are not all “defects” in the source-defect sense; some are clarity, design, or editorial issues.

#### A. Correctness and precision findings

| ID | Location | Finding | Why it matters | Confidence |
|---|---|---|---|---|
| C-01 | ch8, line 38 | The hypothetical multiplication-rule example says `10,05 + 150,95` becomes `161` and that the result “should have four significant figures”. Four s.f. would be **161,0**, not 161. | The paragraph teaches the wrong hypothetical while trying to explain why the rule is wrong. | C |
| C-02 | ch8, lines 115–116 | `1,50 mol/L · 98,00 g/mol = 147,000 g/L`: the exact product is 147.0000; the guard-digit display is inconsistent. | Minor, but this is a chapter about significant figures; guard digits must be exemplary. | H |
| C-03 | ch3, line 39 | “mērīto lielumu saucam par **absorbciju vai absorbance** A” contradicts the policy that `absorbcija` is the process and `absorbance` the quantity. | Reintroduces the exact ambiguity the chapter says it removes. | C |
| C-04 | ch3, line 65 | “Jutība: jo mazāka ir nosakāmā koncentrācija, jo jutīgāka metode” defines sensitivity as detectability. | Sensitivity is the slope dA/dc; low LOD often follows high sensitivity but is not the same property. | C/H |
| C-05 | ch3, line 72 | “Noteikšanas robeža: cik mazā koncentrācijā vielu vēl var **noteikt** ar pieņemamu nenoteiktību?” describes LOQ, not LOD. | The course names LOD/LOQ; conflating them makes the criteria table unreliable. | C/H |
| C-06 | ch7, line 25 | The n−1 explanation (“vidējais tiek aprēķināts no tiem pašiem datiem; ja lieto n, iegūst novirzi uz leju”) is directionally true but too compressed to teach degrees of freedom. | The chapter’s central statistic deserves an explicit residual/degrees-of-freedom explanation. | H |
| C-07 | ch7, line 48; ch8, lines 59/149 | “3 ir precīzs skaits, tāpēc vidējais saglabā divas zīmes aiz komata” conflates the exactness of 3 with a decimal-place rule. The result 12,70 is right; the reason is incomplete. | Students memorise the wrong causal rule and misapply it to other mixed operations. | H |
| C-08 | ch10, line 85 | For the example answer `9,370 mg/100 g`, the text says “**Ceturtā** zīme aiz komata rada šķietamu precizitāti”. 9,370 has three decimal places. | A precision chapter using the wrong place count undermines trust. | C |
| C-09 | ch10, line 28 + tool | The slope is displayed as `0,03217 L/mg` in prose and `0,0321657` in the instrument; the source/verified line uses `0,0322`. No reporting policy is stated. | Different precision in three places; students cannot tell which digit is justified. | H |
| C-10 | ch12, lines 60–67, 128 | The calculation and result box report density `1,0334 g/mL`, then the next paragraph says it “should be rounded to 1,033 g/mL” because the volume has four s.f. The later correction block repeats 1,0334. | Self-contradictory final precision for a central worked example. | C |
| C-11 | ch4, line 23 | In the “Karstumizturība” column, the funnel (piltuve) row says “**Parasti jā, bet ne mērīšanai**”. Heat resistance and measurement suitability are different columns. | A matrix cell that answers two questions at once and makes the column meaningless. | C |
| C-12 | ch4, line 22 | Erlenmeyer flask heat resistance is a blanket “Jā”, while beaker/test tube rows say “Jā, ja borosilikāts”. | Overgeneralises material safety; ordinary soda-lime glass is not heat-shock safe. | H |
| C-13 | ch2, line 16 | Mass is described as “**Vielas daudzumu**, ko rāda svari”, colliding with the technical quantity `n` (amount of substance). | The chapter’s first table must distinguish mass from amount of substance. | C/H |
| C-14 | ch2, line 55 | The SI base quantity is labelled “Gaismas **intensitāte**”; the standard Latvian term for luminous intensity is “gaismas **stiprums**”. | SI terminology precision; the source may use the looser word. Mark V and confirm with the lecturer. | H/V |
| C-15 | ch14, line 135 | “Vienības simbols nāk aiz skaitļa ar **saīsinātu atstarpi** (&nbsp;).” NBSP is a non-breaking space, not a narrow space. | The document teaches typography with a false explanation. | C |
| C-16 | ch5, line 65 | “trešais **solījums** 9,00 mL” should be “trešais **solis** 9,00 mL”. | Plain language error in a caption. | C |
| C-17 | ch2, line 107 | “masas/ tilpuma” has an unwanted space after the slash. | Mechanical typo; easy to fix, easy to spot in a polished document. | C |
| C-18 | ch14 glossary | “gadījuma kļūda — Nejauša, abos virzienos.” is an incomplete sentence. | A glossary definition should be a complete, usable sentence. | C |
| C-19 | ch6 line 30; ch14 line 102; ch15 line 119 | Three labels for the same concept: “Kopējā tuvība”, “kopējā precizitāte; tuvība”, “Kopējā precizitāte”. | Students cannot tell whether these are synonyms or different quantities. | H |
| C-20 | ch4, line 107 | The source quote uses “mēraparātiem” for glassware; the document does not explicitly say that the course term is broader than the precise term `mērtrauks`. | A quoted defect can leak into student usage unless bracketed and explained. | H |

#### B. Design and editorial findings

| ID | Location | Finding | Why it matters |
|---|---|---|---|
| D-01 | `style.css` | 15 distinct screen font sizes at first viewport, 97 `font-size` declarations; half-pixel steps (13.5, 14.5, 15.5, 16.5) have no semantic role. | The scale reads as accumulated patches, not a designed system; inspect flags `size-count`. |
| D-02 | `style.css` | Spacing values are ad hoc: 26/28/30/34/38/44/55/92/118 px, plus many one-off margins. | Vertical rhythm varies without meaning; a spacing token system would make the page calmer and easier to maintain. |
| D-03 | HTML | 44 role blocks, 10 formula boxes, 3 instrument boxes; inspect flags “5 rows of identical boxed cards”. | Too many similar containers flatten hierarchy and push the page toward an app/dashboard feel. |
| D-04 | masthead | 75 px h1, 0.98 line-height, −0.035 em tracking, two CTA buttons. | Strong editorial voice, but reads like a landing-page hero; the prompt asks for a measured reference, not a marketing page. |
| D-05 | 1440/768/390 | 46 tables; 23 scroll hints visible at 390; inspect flags 9 side-scrolling rows. The vessel matrix clips after three columns at 390. | Essential study data becomes a sideways hunt on phones; clipping looks like breakage. |
| D-06 | navigation | Sidebar TOC is chapter-level only; no section navigation, search, reading progress, or visible back-to-top until the footer. | At 107 screens, finding “the bit about n−1” is slow. |
| D-07 | print | 97 pages; forced appendix E page creates a half-empty p96; compact print footer hides the full source list. | A study document should print without orphan pages; a quick-reference edition is missing. |
| D-08 | formulas | MathML is centered and unnumbered; `t_{1/2}` in one formula vs `t½` in prose; variable legends differ in format. | Formulas are the most reusable exam content; they need stable labels and notation. |
| D-09 | figures | Figure 3 (glassware) puts `<figcaption>` before the image; other figures put it after. No figure has a “view data table” alternative. | Inconsistent reading order and a missed accessibility/study feature. |
| D-10 | fonts | Only upright 400/700 WOFF2 faces are embedded; `<i>` and math variables are synthesised oblique. | Faux italics degrade typography and can distort Latvian diacritics at small sizes. |
| D-11 | prose | 103 paragraphs ≥45 words; longest 96 words; 41 sentences >35 words; 58 em dashes. Lint warns on em dashes. | The content is good but the reading rhythm is heavy; long paragraphs hide the rule→reason→example structure. |
| D-12 | headings | One rhetorical heading: “Vai 13,05 mL drīkst izslēgt?”. | The prompt bans rhetorical questions as headings; it also makes the section harder to scan. |
| D-13 | glossary | Some entries are circular or incomplete (“Nejauša, abos virzienos.”; “precizitāte — Atkārtojumu izkliede…”). | The glossary is a study surface, not a word list; entries need definition + unit/context + common confusion. |
| D-14 | accessibility | No axe run; contrast measured but not documented in the document; MathML font fallback warning. | The document claims accessibility through structure, but the evidence is incomplete. |

### 1.5 New defect candidates (D25+)

These are proposed additions to the change log after verification. Do not publish them as certain until the arithmetic/prose audit confirms each one.

| ID | Proposed location | Original | Proposed correction | Confidence |
|---|---|---|---|---|
| D25 | ch8, line 38 | “10,05 + 150,95 kļūst par 161 … rezultātam vajadzētu četrus zīmīgos ciparus” | “Ja kļūdaini lietotu reizināšanas noteikumu, rezultāts būtu 161,0 (četri zīmīgie cipari), nevis 161; pareizais summēšanas rezultāts ir 161,00.” | C |
| D26 | ch3, line 65 | “jo mazāka ir nosakāmā koncentrācija, jo jutīgāka metode” | “Jutība ir kalibrēšanas taisnes slīpums: jo lielāks signāla pieaugums uz koncentrācijas vienību, jo jutīgāka metode. Zema noteikšanas robeža parasti seko augstai jutībai, bet nav tā pati īpašība.” | C |
| D27 | ch3, line 72 | LOD row defined as “noteikt ar pieņemamu nenoteiktību” | Split into LOD (detect presence) and LOQ (quantify with acceptable uncertainty); mark definitions as papildinājums, source gives no formulas. | C |
| D28 | ch3, line 39 | “mērīto lielumu saucam par absorbciju vai absorbance A” | “Mērīto lielumu sauc par absorbciju (absorbance) A” only as a historical synonym; the recommended quantity term is **absorbance A**, the process is **gaismas absorbcija**. | C |
| D29 | ch14, line 135 | “saīsinātu atstarpi (&nbsp;)” | “neplīstošu atstarpi”; NBSP prevents a line break, it is not narrower. | C |
| D30 | ch10, line 85 | “Ceturtā zīme aiz komata” for 9,370 | “Trešā zīme aiz komata” (or “ceturtais zīmīgais cipars”, depending on the sentence). | C |
| D31 | ch4, line 23 | Funnel (piltuve) heat cell “Parasti jā, bet ne mērīšanai” | “Atkarīgs no materiāla; stikla piltuve parasti ir karstumizturīga” + move “nav mērīšanai” to the use/never column. | C |
| D32 | ch4, line 22 | Erlenmeyer heat cell “Jā” | “Jā, ja borosilikāts; parastais stikls — ierobežoti” (same convention as beaker/test tube). | H |
| D33 | ch2, line 16 | Mass = “Vielas daudzumu, ko rāda svari” | “To, cik daudz matērijas ir paraugā; svari rāda masu” (avoid the technical term `vielas daudzums` for n). | H |
| D34 | ch2, line 55 | “Gaismas intensitāte” | “Gaismas stiprums (luminous intensity)”; confirm course usage before replacing the source quote. | H/V |
| D35 | ch7, lines 25/48/59; ch8 line 149 | n−1 explanation + exact-number wording | Add residual/degrees-of-freedom explanation; say exact 3 does not limit s.f., and the sum's decimal places plus the division give 4 s.f. | H |
| D36 | ch12, lines 60–67/128 | 1,0334 g/mL reported, then “should be 1,033” | Decide one policy: intermediate 1,0334 with guard digits, reported density 1,033 g/mL (4 s.f.); update every occurrence, including the correction block and caption. | C |
| D37 | ch5, line 65 | “trešais solījums” | “trešais solis” | C |
| D38 | ch2, line 107 | “masas/ tilpuma” | “masas/tilpuma” | C |
| D39 | ch14 glossary | “Nejauša, abos virzienos.” | “Nejauša, abos virzienos vienādi iespējama.” | C |
| D40 | ch6/ch14/ch15 | Three “accuracy” labels | One canonical label + explicit synonym note + V flag | H/V |

---

## 2. Task map, dependencies and execution waves

### 2.1 The 20 tasks at a glance

| ID | Task | Category | Priority | Effort | Depends on | Features |
|---|---|---|---|---|---|---|
| T01 | Canonical terminology register + executable checker | Terminology | P0 | M | — | F12 (links) |
| T02 | Absorbance/absorption + sensitivity/LOD/LOQ cluster | Terminology + precision | P0 | M | T01 | — |
| T03 | Precision/trueness/accuracy system + V marking | Terminology | P0 | M | T01 | — |
| T04 | Vessel/equipment terminology + matrix facts | Terminology + factual | P0 | M | T01, T08 | — |
| T05 | Significant-figure arithmetic corrections | Mistakes + precision | P0 | M | T01 | F10 |
| T06 | Calibration and density reporting precision | Mistakes + precision | P0 | M | T05 | — |
| T07 | Line-edit, typographic hygiene, prose rhythm | Polish | P1 | M | T01 | — |
| T08 | Table/figure factual + caption/alt audit | Mistakes + accessibility | P0 | L | T01, T04 | F06 |
| T09 | Degrees of freedom, SEM and CI explanation | Understandability | P1 | M | T05 | — |
| T10 | Mixed-operations decision tree + exact numbers | Understandability | P1 | M | T05 | F10 |
| T11 | Calibration model limits and uncertainty | Understandability | P1 | L | T02, T06 | F07 |
| T12 | Graph-reading method + trainer + data tables | Understandability + feature | P1 | L | T08 | F05, F06 |
| T13 | Half-life time-origin, units, offset simulator | Understandability + feature | P1 | M | T06 | F09 |
| T14 | Solution/density decision flow + dilution calculator | Understandability + feature | P1 | L | T06 | F08 |
| T15 | Typographic and spacing token system | Redesign | P2 | M | T07 | — |
| T16 | De-card restyle, masthead, roles and formulas | Anti-slop/restyle | P2 | L | T15 | — |
| T17 | Responsive table and mobile data strategy | Redesign | P2 | L | T08 | — |
| T18 | Section navigation, print pack, page-flow repair | Restyle + print | P2 | L | T15, T17 | F02, F11 |
| T19 | Offline search + glossary linking | Feature | P2 | XL | T01, T18 | F01, F12 |
| T20 | Recall workspace + exam mode + consent persistence | Feature | P2 | XL | T19 | F03, F04, F14 |

### 2.2 Execution waves

| Wave | Duration (single editor) | Tasks | Exit condition |
|---|---:|---|---|
| 0 — Baseline | 0.5 day | freeze, hashes, harness setup | baseline HTML/PDF archived; arithmetic and term checkers run on current build |
| 1 — Correctness | 2–3 days | T01, T02, T03, T04, T05, T06 | all P0 content findings closed; arithmetic harness green; no active banned terms |
| 2 — Comprehension | 2–3 days | T07, T08, T09, T10 | 100% tables/figures audited; long-sentence and em-dash targets met; new explanations reviewed |
| 3 — Learning features | 2–3 days | T11, T12, T13, T14 | calibration/graph/half-life/solution features pass fixed vectors; no invented data |
| 4 — Restyle | 2–3 days | T15, T16, T17, T18 | type/spacing tokens applied; inspect warnings down; mobile/print QA green |
| 5 — Study workspace | 3–4 days | T19, T20 | search/review/exam features pass keyboard/offline/no-storage tests |
| **Total** | **~10–14 days** | | P0/P1 complete; P2 features staged |

Parallelisation: T02/T03/T04 can run in parallel after T01; T05/T06 are one workstream; T09/T10 share the statistics chapter and must not be edited simultaneously; T15 must precede T16 and T18; T19 can start after T01 but its UI should follow T18’s navigation decisions.

---

## 3. The 20 tasks

Each task uses the same shape:

- **Evidence** — what in the current build justifies the task.
- **Target state** — what “done” looks like in one or two sentences.
- **Substeps (3)** — the main sequence.
- **Subtasks (2–3)** — each with exactly three sub-substeps.
- **Acceptance** — measurable checks.
- **Verification** — commands or browser checks.
- **Risk/rollback** — what can go wrong and how to reverse it.

---

### T01 — Create a canonical terminology register and make it executable

**Category:** terminology · **Priority:** P0 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** none
**Affected files:** `build/terminology.json` (new), `build/check_terms.py` (new), `build/build_doc.py`, `build/sections/*.html`, `build/app.js`, ch14, ch16
**Linked features:** F12

**Evidence**

- The HTML contains 39 occurrences of `absorbcij*` and only 10 of `absorbanc*`; 54 of `precizitāt*` and 25 of `pareizīb*`. Many are legitimate, but the counts show how easily the two vocabularies coexist.
- The glossary and prose disagree on the quantity name (`absorbcija` vs `absorbance`), on the accuracy umbrella (`kopējā tuvība` vs `kopējā precizitāte`), and on the fume-hood term (`tvaika nosūcējs` vs `velkmes skapis`).
- The document already has a strong terminology chapter (ch14), but it is a static table; nothing prevents a future edit from reintroducing a banned form.
- The prompt requires no banned spelling outside quotations (`ml`, `sec`, `ppm`, `zīmīgie skaitļi`, `Cz`, `1·10⁻⁶ µmol`, `Erlenmeiera`). A human grep is not enough at 26,773 words.

**Target state**

A single machine-readable register defines every high-risk term (canonical form, English equivalent, symbol, unit, definition, forbidden variants, allowed quote contexts, confidence). A build-time checker scans all sections and fails on active violations while allowing source quotations. Ch14 is generated from the same register, so the glossary can never drift from the prose.

**Substeps (3)**

1. **Inventory and classify.** Extract every high-risk term with context, count, and current variant; classify each hit as active use, source quotation, glossary mention, change-log mention, or code identifier. Do not “fix” quoted sources.
2. **Define the register.** For each term, record canonical LV, EN, symbol, unit, one-sentence definition, forbidden variants, allowed contexts, confidence (C/H/V), and source references. Mark unresolved items `V` and add them to the lecturer questions.
3. **Enforce and publish.** Add the checker to the build, apply the register to prose, table headers, labels, JS output, SVG `<title>/<desc>`, ch14 and ch16; regenerate the glossary table from the JSON so the canonical form is the only form a reader sees.

**Subtasks**

**T01.1 Audit the existing vocabulary**
1. Write a read-only extractor that prints file, line, 80-character context, and guessed context class for each hit of the register’s forbidden variants.
2. Review all hits by hand and mark exceptions: source quotes, change-log “original wording”, glossary “found” column, code tokens, and historical notes.
3. Record the final counts in `build/terminology_audit.csv` and summarise the active-use violations by term family.

**T01.2 Build the register and the checker**
1. Create `build/terminology.json` with the schema `{id, canonical_lv, canonical_en, symbol, unit, definition_lv, forbidden[], allowed_contexts[], confidence, source_refs[], notes}`.
2. Implement `build/check_terms.py`: strip tags, skip elements marked `data-quote="true"`, apply word-boundary matching with Latvian diacritics, and emit a non-zero exit on any active violation.
3. Add a `--report` mode that writes `build/terminology_report.md` with counts, contexts, and suggested replacements; wire the strict mode into `build/build_doc.py` after the HTML is assembled.

**T01.3 Apply the register and regenerate the glossary**
1. Replace active prose/table/JS/SVG forms with the canonical term; keep source quotations but wrap them in `<q data-quote="true">…</q>` and add “avotā” attribution.
2. Rewrite ch14’s “Avotā / Šajā dokumentā / Kāpēc” table from the register; make the same JSON produce the LV–EN glossary rows.
3. Add a dated change-log entry listing the term families changed, the number of replacements, and every preserved quotation; add D33–D40 to the defect register when verified.

**Acceptance**

- `python3 build/check_terms.py Master_2_tema_merijumi_un_grafiki.html` exits 0 on the final build and lists 0 active violations.
- Every register term appears at least once in the document or glossary; every glossary row has a definition, a unit/context, and a “don’t confuse with” field.
- Source quotations still match the PDFs character-for-character; no quotation was silently normalised.
- `grep -nE '\b(ml|sec|ppm)\b'` returns only quoted/change-log exceptions, each wrapped in `data-quote`.
- Ch14 and ch16 agree with the register on every high-risk term.

**Verification**

```bash
python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --strict
python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --report
grep -nE 'data-quote="true"' Master_2_tema_merijumi_un_grafiki.html | wc -l
```

**Risk/rollback**

The main risk is over-correction: replacing a term inside a source quote or a historical note. Mitigation: `data-quote` allowlist, a diff review of every change, and a separate commit for the mechanical replacement. Rollback: restore the baseline HTML, keep the register/checker, and reapply only the confirmed replacements.

---

### T02 — Resolve the absorbance/absorption and sensitivity/LOD/LOQ cluster

**Category:** terminology + precision · **Priority:** P0 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** T01
**Affected files:** `03_ch3.html`, `09_ch9.html`, `10_ch10.html`, `14_ch14.html`, `16_ch16.html`, `app.js` (calibration labels)
**Linked features:** —

**Evidence**

- `03_ch3.html:39` says the measured quantity can be called “absorbciju vai absorbance A”, directly contradicting the policy that `absorbcija` is the process.
- `03_ch3.html:65` defines sensitivity as “jo mazāka ir nosakāmā koncentrācija, jo jutīgāka metode”; `03_ch3.html:106` repeats “Jutība ir spēja noteikt mazas koncentrācijas”. That is detectability, not sensitivity.
- `03_ch3.html:72` defines “Noteikšanas robeža” as “cik mazā koncentrācijā vielu vēl var noteikt ar pieņemamu nenoteiktību” — that is the quantification limit, not the detection limit.
- `10_ch10.html:12, 106, 119` uses “Absorbcija A” as a table header and input label; `14_ch14.html:20` correctly says `absorbcija` is the process and `absorbance A` the quantity.
- The source names both qualitative and quantitative detection limits but gives no formulas; the document must not invent numerical LOD/LOQ values.

**Target state**

The document uses **absorbance A** for the measured quantity, **gaismas absorbcija** for the process, defines **sensitivity as the slope dA/dc**, and treats **LOD** and **LOQ** as two distinct concepts. The calibration table headers, instrument labels, glossary, recall answers and change log all agree.

**Substeps (3)**

1. **Fix the quantity/process pair.** Replace “Absorbcija A” with “Absorbance A” in headers, labels and prose; keep “gaismas absorbcija” only for the physical process; add a one-line “say this / not this” table.
2. **Fix sensitivity and the detection limits.** Rewrite the criteria table so sensitivity = slope, LOD = detect presence, LOQ = quantify with acceptable uncertainty; state that the source names but does not develop LOD/LOQ.
3. **Rehearse the distinction.** Add a diagnostic table (wrong statement → why wrong → correct statement) and two closed recall items; update the change log with D26–D28.

**Subtasks**

**T02.1 Global quantity-label migration**
1. Search every occurrence of `Absorbcija`/`absorbcija` and classify it as quantity, process, source quotation, or glossary note.
2. Replace quantity uses with `Absorbance A` in ch3/ch9/ch10/ch14/ch16 and in the calibration instrument’s labels and output strings.
3. Re-read the Beer–Lambert paragraph and the calibration threshold text to ensure no sentence still uses the process word for the number.

**T02.2 Rewrite the criteria table**
1. Replace the sensitivity row with “signāla pieaugums uz koncentrācijas vienību; slīpums dA/dc; augsta jutība var, bet ne obligāti, pazemināt LOD”.
2. Split “Noteikšanas robeža” into **LOD** (detect presence) and **LOQ** (quantify with acceptable uncertainty); add “avotā nav formulu” and “skaitliskās vērtības nav izgudrotas”.
3. Add a note that selectivity is the ability to distinguish the analyte in the matrix, and that a high slope does not prove selectivity.

**T02.3 Add diagnostics and recall**
1. Write a three-row diagnostic table: “high R² proves method” → no; “high sensitivity means low LOD” → not necessarily; “A is absorption” → A is absorbance.
2. Add closed recall items for sensitivity vs LOD, LOD vs LOQ, and absorbance vs absorption.
3. Run the term checker and re-read the ch3 source line; update the change log with the corrected definitions.

**Acceptance**

- `grep -n 'Absorbcija <i>A</i>'` returns no active table header or label.
- The criteria table has separate LOD and LOQ rows with precise one-sentence definitions.
- Sensitivity is defined as slope in ch3, ch14 and the recall answer; no remaining “small concentration = sensitive” phrasing.
- No invented numeric LOD/LOQ value appears anywhere.
- Ch3/ch10/ch14/ch16 agree; the change log includes D26–D28.

**Verification**

```bash
grep -nE 'Absorbcija|absorbciju vai absorbance|jo mazāka ir nosakāmā' build/sections/*.html
grep -n 'LOD\|LOQ\|noteikšanas robeža\|kvantificēšanas robeža' build/sections/03_ch3.html build/sections/14_ch14.html
node build/final_check.mjs
```

**Risk/rollback**

The physical/chemical distinction is subtle; over-replacing “absorbcija” in process sentences would make the text unnatural. Keep a two-column mapping and review each sentence. Rollback: restore ch3/ch10 from baseline and reapply the label migration only.

---

### T03 — Standardise precision, trueness and the “accuracy” umbrella

**Category:** terminology · **Priority:** P0 · **Effort:** M (3–5 h) · **Risk:** medium · **Depends on:** T01
**Affected files:** `06_ch6.html`, `14_ch14.html`, `15_ch15.html`, `16_ch16.html`, `04_ch4.html` (vessel heading), ch1 legend if needed

**Evidence**

- `06_ch6.html:30` uses “Kopējā tuvība”; `14_ch14.html:102` uses “kopējā precizitāte; tuvība”; `15_ch15.html:119` uses “Kopējā precizitāte”.
- The document correctly separates `precizitāte` (scatter) from `pareizība` (closeness of the mean to a reference), but the umbrella term is unresolved.
- The heading “Trauku precizitātes pakāpe” (ch4) still uses the overloaded word for vessel quality; the body explains the issue, but the heading does not.
- The prompt marks the accuracy translation as `V` (verify with lecturer); the current text presents one wording as settled.

**Target state**

One canonical umbrella term is chosen and marked `V`; the glossary lists the accepted synonym but warns against ambiguity. Vessel quality is described as “pieļaujamā kļūda / mērtrauks ar mazu kļūdu”, not “precizitāte”. The target diagram and the three-term table use the same labels.

**Substeps (3)**

1. **Decide the umbrella.** Review the course PDF wording and the prompt; choose `kopējā tuvība (accuracy)` as the prose term (recommended) or `kopējā precizitāte`, and record the decision plus the `V` flag. Do not average the two.
2. **Apply consistently.** Replace the label in ch6, ch14, ch15 and the glossary; add a parenthetical synonym note only once, in ch14; rename the ch4 vessel heading and any “precīzi trauki” active uses that are not quoted.
3. **Teach the distinction.** Add a 2×2/3-case table (precise but biased; imprecise but unbiased; both; neither) tied to the target figure; add a recall item that asks for the umbrella term and its two components.

**Subtasks**

**T03.1 Resolve the term and its status**
1. Extract the exact source sentences from the course PDF and the prompt’s §7.5 row; quote them side by side.
2. Choose the canonical term and document the rationale; mark it `V` if the course uses a different umbrella.
3. Add the open question to ch16 D (Jautājumi lektoram): “Kuru terminu lietot eksāmenā — kopējā tuvība vai kopējā precizitāte?”

**T03.2 Rewrite the labels**
1. Change ch6’s `<dt>Kopējā tuvība</dt>` to the canonical label and add a one-line synonym note.
2. Change ch14’s glossary row to `canonical (accuracy); synonym: …` with a warning that `precizitāte` alone means scatter.
3. Change ch15’s answer and ch4’s heading; re-read for any remaining active “trauka precizitāte” phrase and replace with “pieļaujamā kļūda”.

**T03.3 Add the contrast exercise**
1. Write a three-row table: tight + centred; tight + offset; scattered + centred; name each with precision/trueness/umbrella.
2. Add a recall item: “A series is tight but 0.8 mL high — precise, true, accurate? Which umbrella term applies?”
3. Check the target figure labels match the table exactly; update the figure `<desc>` if needed.

**Acceptance**

- Only one umbrella term appears in active prose; the synonym is explicitly labelled once.
- The `V` flag is visible in ch14/ch16 and the lecturer question exists.
- No active “trauka precizitāte” heading or sentence remains; source quotes remain untouched.
- Target figure, legend, glossary, recall answers and ch15 agree.
- `build/check_terms.py` passes with the new canonical term.

**Verification**

```bash
grep -nE 'Kopējā tuvība|kopējā precizitāte|Kopējā precizitāte' build/sections/*.html
grep -n 'Trauku precizitātes pakāpe' build/sections/04_ch4.html
python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --strict
```

**Risk/rollback**

`accuracy` has no single settled Latvian equivalent; a wrong choice could look authoritative. Mark `V`, ask the lecturer, and keep the synonym visible. Rollback: revert the label change while keeping the `V` note and the clearer vessel heading.

---

### T04 — Correct vessel/equipment terminology and matrix facts

**Category:** terminology + factual · **Priority:** P0 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** T01, T08
**Affected files:** `04_ch4.html`, `05_ch5.html`, `14_ch14.html`, glassware SVGs/labels, ch16 Q5/D24 rows
**Linked features:** —

**Evidence**

- `04_ch4.html:23`: the funnel (piltuve) row’s “Karstumizturība” cell reads “Parasti jā, bet ne mērīšanai” — a use/never-use statement in the heat column.
- `04_ch4.html:22`: Erlenmeyer heat resistance is “Jā”, while beaker/test tube say “Jā, ja borosilikāts”; the matrix is inconsistent about material.
- `04_ch4.html:107`: the source quote uses “mēraparātiem”; the document does not explicitly distinguish the source’s broad word from the precise `mērtrauks`.
- `04_ch4.html:53` and the glossary use “tvaika nosūcējs”; the prompt notes “velkmes skapis” as a possible V term. One term must win.
- `05_ch5.html:65`: “trešais solījums” is a plain typo in the burette caption.
- Q5 contains 17 rows; several reasons are good, but the matrix and Q5 must agree on heat, material and “not a measuring vessel”.

**Target state**

The vessel matrix has clean, single-purpose columns; heat resistance is conditional on material; “mērtrauks” and “mēraparāts” are distinguished; one fume-hood term is used; Q5, the matrix and the glossary agree; the burette caption says “solis”.

**Substeps (3)**

1. **Audit the matrix.** Rebuild the columns as “Mērījuma statuss”, “Materiāls / karstums”, “Kad lietot”, “Kad nē”; replace blanket “Jā” with “Jā, ja borosilikāts” or “Atkarīgs no marķējuma”; move measurement statements out of the heat column.
2. **Reconcile Q5 and the glossary.** Check every Q5 row against the matrix; fix the pipette/funnel/Erlenmeyer/Petri reasons; add a note that Q5 is a papildinājums; unify the fume-hood term with a first-use synonym.
3. **Fix labels and figures.** Correct the burette caption typo; check glassware SVG labels (`Mora pipete`, `mērpipete`, `Erlenmeijera kolba`) and the figure caption order; update the term register.

**Subtasks**

**T04.1 Matrix column redesign**
1. Draft a 4-column schema and map every current cell to exactly one column; mark any cell that currently answers two questions.
2. Rewrite the 11 vessel rows with conditional heat wording and a clear “measuring claim” value.
3. Re-render the matrix at 1440/768/390 and verify no column becomes a paragraph; move detail into a table note if needed.

**T04.2 Q5 and glossary reconciliation**
1. Check all 17 Q5 rows against the matrix; fix the funnel heat cell and any row whose reason contradicts the matrix.
2. Add a short editorial note: “Q5 atbildes ir papildinājums; trauka izvēle var būt cita, ja pamatojums ir fizikāls.”
3. Choose the fume-hood canonical term, use it in the matrix/Q5/glossary, and add the synonym in parentheses once; mark `V` if the course is unconfirmed.

**T04.3 Labels, figures and change log**
1. Fix “trešais solījums” → “trešais solis”; scan all captions for similar noun errors.
2. Check the glassware SVG `<title>`/`<desc>` and visible labels for the canonical vessel names; ensure the figure caption comes after the drawing.
3. Add D31/D32/D37 and the terminology changes to the change log; note D24 remains the 25/50 mL cylinder mismatch.

**Acceptance**

- No matrix cell mixes heat resistance with measurement suitability.
- Every heat-resistance value is conditional or explicitly material-dependent.
- Q5, matrix, glossary and SVG labels use the same vessel names.
- The burette caption reads “trešais solis”.
- One fume-hood term is canonical; the synonym appears once.
- `build/check_terms.py` passes; the change log includes the new rows.

**Verification**

```bash
grep -n 'Parasti jā, bet ne mērīšanai\|solījums\|mēraparāt' build/sections/04_ch4.html build/sections/05_ch5.html
grep -n 'tvaika nosūcēj\|velkmes skap' build/sections/04_ch4.html build/sections/14_ch14.html
node build/final_check.mjs
```

**Risk/rollback**

Heat resistance depends on the actual glassware, not just the name; any categorical “Jā” can become unsafe. Keep the “check the manufacturer’s mark” caveat and do not turn the matrix into a safety certification. Rollback: restore the old matrix and keep the typo/label fixes separate.

---

### T05 — Recompute and correct every significant-figure worked example

**Category:** mistakes + precision · **Priority:** P0 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** T01
**Affected files:** `08_ch8.html`, `07_ch7.html`, `02_ch2.html`, `app.js` (sig-fig instrument), ch16 test vectors
**Linked features:** F10

**Evidence**

- `08_ch8.html:38`: the hypothetical multiplication-rule example says the result becomes 161 while also saying it should have four s.f.; four s.f. is 161,0.
- `08_ch8.html:115–116`: `1,50 × 98,00 = 147,000`; the exact product is 147,0000. The guard-digit display is inconsistent.
- `07_ch7.html:48` and `08_ch8.html:149`: the exact number 3 is said to “preserve two decimal places”; the correct explanation is that 3 does not limit significant figures, and the sum’s two decimal places plus the division give 12,70 (4 s.f.).
- The instrument already passes its test vectors, but its explanations are the same prose students read; the prose must match the tool.

**Target state**

Every displayed calculation follows a single written policy: keep guard digits in intermediates; apply the operation-specific rule; round once at the end; report the error before the result. The 161/161,0 example is corrected, the exact-3 rationale is precise, and the instrument’s output is consistent with the text.

**Substeps (3)**

1. **Build a test-case file.** Encode every worked sig-fig example (inputs, operation, expected unrounded value, expected reported value, rule) in `build/sigfig_cases.json`; recompute all with Python `Decimal`, not binary floats.
2. **Rewrite the chapter.** Fix the hypothetical 161→161,0; correct the Q4c guard digits; rewrite the exact-number explanation; add a mixed-operation warning and a “round once” example.
3. **Synchronise the instrument and the chapter.** Make the instrument’s wording and expected outputs match the chapter; add test vectors for exact-3 and mixed operations; update ch16’s vector table.

**Subtasks**

**T05.1 Build the arithmetic harness**
1. Encode the cases: 10,05+150,95; the wrong multiplication-rule hypothetical; 3,45×0,8; 0,25÷1,0; 12,50+13,05+12,55 then ÷3; 1,50×98,00; 1,1145±0,0127; 1,1145±0,019; 450 inspection.
2. Compute expected values with `decimal.Decimal` and record both the unrounded and reported forms; flag any case whose expected value is ambiguous.
3. Add a `--check` mode that parses the HTML for the displayed values and fails on a mismatch at the stated precision.

**T05.2 Rewrite the prose**
1. Replace the 161 sentence with: “Ja kļūdaini lietotu reizināšanas noteikumu, rezultāts būtu 161,0 (četri zīmīgie cipari), nevis 161; pareizais summēšanas rezultāts ir 161,00.”
2. Rewrite the exact-3 sentence: “3 ir precīzs skaits un neierobežo zīmīgo ciparu skaitu; summa 38,10 ir ar divām zīmēm aiz komata, un 38,10/3 = 12,70 saglabā 4 zīmīgos ciparus.”
3. Correct Q4c to show the exact guard-digit product (`147,0000`) or explicitly label the displayed value as rounded; use one policy everywhere.

**T05.3 Synchronise the tool and vectors**
1. Update the sig-fig instrument’s rule text and output for the exact-3/mixed cases; ensure it never claims a decimal-place rule for division.
2. Add the new vectors to ch16 E and to the instrument’s `Pārbaudes gadījumi` table.
3. Run the instrument in Chrome and compare its output to the JSON expectations; record the result in the QA log.

**Acceptance**

- The 161→161,0 sentence is corrected and the “four significant figures” claim is internally consistent.
- All displayed arithmetic matches the Decimal harness at the stated precision.
- The exact-3 explanation no longer claims that exactness preserves decimal places.
- Q4c uses consistent guard digits or is explicitly labelled.
- Instrument outputs match the chapter for all vectors.
- D25 and D35 are in the change log.

**Verification**

```bash
python3 -I build/check_sigfig_cases.py --check Master_2_tema_merijumi_un_grafiki.html
node - <<'JS'
// run the sf test hooks for 10,05+150,95, 3,45*0.8, 12,50/13,05/12,55, 1,50*98,00
JS
```

**Risk/rollback**

Significant-figure conventions are course-specific; the document already distinguishes the course convention from standard practice. Do not “correct” the course’s trailing-zero convention without marking it. Rollback: keep the harness, revert the prose patch, and log the remaining discrepancy.

---

### T06 — Make calibration and density reporting precision self-consistent

**Category:** mistakes + precision · **Priority:** P0 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** T05
**Affected files:** `10_ch10.html`, `12_ch12.html`, `app.js` (calibration output), ch16 test vectors, figure captions
**Linked features:** F07 (model panel)

**Evidence**

- `10_ch10.html:28` displays slope `0,03217 L/mg`; the instrument uses `0,0321657`; the source/verified line is `0,0322`. There is no statement of which digit is justified.
- `10_ch10.html:85` says “Ceturtā zīme aiz komata” for `9,370` (three decimals).
- `12_ch12.html:60–67` reports density `1,0334 g/mL`, then says it should be rounded to `1,033 g/mL`; the correction block at line 128 repeats `1,0334`.
- The calibration tool’s intermediate output and the chapter’s rounded line are different precisions; a student copying either sees a different “line”.

**Target state**

A written guard-digit/reporting policy is applied everywhere: full precision in the tool and intermediates, one reported slope (3 s.f., 0,0322), one reported density (4 s.f., 1,033 g/mL), and a clearly labelled intermediate 1,0334. The “9,370” sentence uses the correct place count.

**Substeps (3)**

1. **Define the policy.** State how many guard digits are kept, how slope/intercept are reported (slope 3 s.f.; intercept 3 s.f.), how density is reported from 100,0 mL and 103,34 g, and how w is reported (3 s.f. direct; 2 s.f. from the graph).
2. **Apply to prose and tables.** Update ch10’s line, worked steps, sample table and tool labels; update ch12’s steps, result box, caption and correction block; preserve full precision only where explicitly labelled “starpvērtība”.
3. **Test the tool and the display.** Add the reported and intermediate values to the test vectors; verify the tool says which slope it uses; ensure no page shows two different final values for the same quantity.

**Subtasks**

**T06.1 Calibration slope/intercept policy**
1. Compute the slope/intercept with full precision; write the line at 3 s.f. for the reported form and show the full precision in a parenthetical “aprēķinos lietots”.
2. Update ch10 line 28, the four calculation steps, the sample table note and the instrument intro/output.
3. Add a “guard digits” callout: keep 2–3 extra digits, round once; never round the slope before inverting it.

**T06.2 Density reporting policy**
1. Decide the reported density: 1,033 g/mL (4 s.f. from 100,0 mL) with 1,0334 labelled as the unrounded intermediate; or explicitly justify 5 s.f. if the volume is treated as exact. Recommend 1,033 with the intermediate shown.
2. Update the calculation steps, result box, figure caption, temperature paragraphs and the correction block; ensure every occurrence uses the same reported value.
3. Recompute w from the reported density and from the intermediate; state which one is used and why the final w remains 4,86%.

**T06.3 The 9,370 sentence and tool sync**
1. Replace “Ceturtā zīme aiz komata” with “Trešā zīme aiz komata” or “ceturtais zīmīgais cipars”, depending on whether the sentence counts places or significant digits.
2. Make the calibration tool display the same slope/intercept as the prose and label the full-precision value as intermediate.
3. Add regression cases: A=0,845 → 25,9; A=0,312 → 9,4; A=0,982 → 30,2 + extrapolation flag; A=0 → negative + flag; density 1,0334 → w 4,86.

**Acceptance**

- One reported slope (0,0322 L/mg) and one reported intercept (0,0106) in prose; full precision only in labelled intermediates.
- One reported density (1,033 g/mL) and one clearly labelled intermediate (1,0334); no self-contradiction.
- The “9,370” sentence uses the correct decimal-place count.
- Tool output matches the prose and test vectors.
- C-09/D30/D36 are in the change log.

**Verification**

```bash
grep -n '1,0334\|1,033\|0,03217\|0,0322\|Ceturtā zīme' build/sections/10_ch10.html build/sections/12_ch12.html
node build/final_check.mjs
```

**Risk/rollback**

Changing the reported density may change the answer students expect from the source example. Keep both values visible with an explicit “starpvērtība / atbilde” label, and log the policy; if the lecturer wants 1,0334, revert the reported value but keep the guard-digit note.

---

### T07 — Line-edit, typographic hygiene, and prose rhythm

**Category:** polish · **Priority:** P1 · **Effort:** M (4–6 h) · **Risk:** low–medium · **Depends on:** T01
**Affected files:** all sections, ch14 glossary, ch5 caption, ch7 heading, ch2 note

**Evidence**

- `05_ch5.html:65`: “trešais solījums” → “trešais solis”.
- `02_ch2.html:107`: “masas/ tilpuma” → “masas/tilpuma”.
- `14_ch14.html:135`: NBSP described as a “saīsināta atstarpe”; it is a non-breaking space.
- ch7 heading: “Vai 13,05 mL drīkst izslēgt?” is a rhetorical question, which the prompt bans as a heading.
- 103 paragraphs ≥45 words; 41 sentences >35 words; 58 em dashes (lint warning).
- Ch14 glossary has at least one incomplete sentence (“Nejauša, abos virzienos.”).

**Target state**

Known mechanical errors are gone; prose paragraphs are shorter and more signposted; em dashes are reduced to deliberate use; units use NBSP correctly; headings are declarative; the glossary reads as finished prose.

**Substeps (3)**

1. **Mechanical sweep.** Fix the known typos and punctuation; run a script for repeated words, double spaces, spaces before punctuation, normal spaces before units, and broken slash compounds.
2. **Rhythm pass.** Split the longest paragraphs and sentences, move the rule/reason/example to the front of each section, remove filler transitions, and reduce em dashes to ≤20 purposeful uses.
3. **Read-aloud proof.** Render the changed pages, read them aloud (or use text-to-speech) and check for breathlessness, ambiguity, and repeated sentence openings; update the change log.

**Subtasks**

**T07.1 Mechanical and typographic fixes**
1. Fix `solījums`, `masas/ tilpuma`, the incomplete glossary sentence, and any spacing-before-punctuation hits.
2. Normalise NBSP before units and between number and unit; verify `12,70&nbsp;mL` is used everywhere in prose and tables.
3. Replace the rhetorical heading with a declarative one, e.g. “13,05 mL izslēgšanas pārbaude” or “Kad vērtību drīkst izslēgt”.

**T07.2 Prose rhythm and signposting**
1. Extract the 103 long paragraphs and rank by length; rewrite the top 30 so each has one controlling idea and a short first sentence.
2. Split sentences over 35 words, especially those with multiple semicolons or parentheses; keep source quotations intact.
3. Replace generic transitions (“Tāpēc”, “Tas nozīmē”, “Šajā dokumentā”) where they add no logic; keep the rule→reason→example order visible.

**T07.3 Em-dash, NBSP and read-aloud audit**
1. Count em dashes and replace most with full stops, commas or colons; keep ranges as en dashes; do not alter source quotations.
2. Re-run the unit-spacing and decimal-comma greps; verify no normal space before a unit in active prose.
3. Read the changed pages at 1440 and 390, and the print pages; log any sentence that still requires a second reading.

**Acceptance**

- Zero known typos from the mechanical list; no “solījums”, “masas/ tilpuma”, or incomplete glossary sentence.
- Em dashes ≤20 in active prose (excluding source quotations and change-log ranges).
- No sentence over 45 words in explanatory prose without a documented reason.
- NBSP and decimal comma correct in all new/changed text.
- The rhetorical heading is gone; all headings are declarative.
- Ch14 glossary definitions are complete sentences with unit/context where relevant.

**Verification**

```bash
grep -nE 'solījums|masas/ |  +| ,' build/sections/*.html | head -40
grep -o '—' Master_2_tema_merijumi_un_grafiki.html | wc -l
python3 - <<'PY'
# longest-sentence and long-paragraph report
PY
```

**Risk/rollback**

A prose rewrite can accidentally change technical meaning. Keep a diff with original/corrected side by side; never rewrite formulas, numbers or source quotations. Rollback: restore individual paragraphs from the baseline; keep mechanical fixes separate.

---

### T08 — Audit every table and figure for factual claims, captions and alternatives

**Category:** mistakes + accessibility · **Priority:** P0 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T01, T04
**Affected files:** all 46 tables, all 10 figures, ch4 glassware, ch12 density, ch3 criteria, ch16 source map
**Linked features:** F06

**Evidence**

- 46 tables and 10 figures; several contain “papildinājums” facts (heat resistance, pipette divisions, Q5 answers) that are not in the source.
- `04_ch4.html` puts the glassware `<figcaption>` before the drawing; the other nine figures put it after.
- No figure offers a data-table alternative; a screen-reader user gets the `<desc>` but cannot inspect the plotted values.
- The matrix and Q5 need the T04 corrections; the LOD/LOQ and density tables need T02/T06.
- The prompt requires every table caption and `scope`, and every SVG `<title>/<desc>`; the current build has these, but the audit must verify content, not just presence.

**Target state**

A register lists every table and figure with its claim, source/papildinājums status, units, caption, alt/long description, and verification date. Factual errors are fixed; unsupported claims are labelled; figures have data-table alternatives; caption order is consistent.

**Substeps (3)**

1. **Build the register.** Extract all 46 tables and 10 figures; record caption, columns, units, claims, source refs, status, and known issues; classify each table (matrix, numeric, procedure, glossary, test vector, change log).
2. **Audit in batches.** Review by chapter; check every number against the source/verified JSON; mark any unsourced claim as papildinājums; fix the known heat/LOD/density issues from T04/T02/T06.
3. **Fix semantics and alternatives.** Ensure captions after images, `<title>/<desc>` present and meaningful, data tables for plots, `scope` on all headers, and print behaviour for wide tables.

**Subtasks**

**T08.1 Table register and batch audit**
1. Generate a table inventory with chapter, caption, row/column count, numeric columns, and source/papildinājums status.
2. Audit the numeric tables against `verified.json` and the source PDFs; flag any value that cannot be reproduced.
3. Audit the qualitative cells (heat, use/never, safety, Q5 reasons) against T04’s decision rules.

**T08.2 Figure register and semantics**
1. Record each figure’s title, `<desc>`, caption, data source, plotted values, and whether it is model/redrawn or source data.
2. Move the ch4 `<figcaption>` after the drawing; verify reading order in the accessibility tree.
3. Add a `<details>` data table under each plot (at least calibration, both half-life graphs, density) with the exact plotted values and the model equation.

**T08.3 Accessibility and print checks**
1. Verify every table has a caption and `scope`; every numeric column is right-aligned; every unit is in the header, not repeated in each cell.
2. Verify every SVG has a `<title>` and `<desc>` that describe the data, not the decoration; check contrast of labels.
3. Print the affected pages and confirm no table splits mid-row, no caption is orphaned, and every figure keeps its caption.

**Acceptance**

- 46/46 tables have a caption, scope, units and a source/papildinājums status.
- 10/10 figures have meaningful `<title>/<desc>`, a caption after the image, and a data-table alternative where the figure encodes data.
- No numeric claim in the register is unreproducible or unlabelled.
- Heat/LOD/density corrections from T02/T04/T06 are applied.
- The accessibility tree reads figure → caption in the correct order.

**Verification**

```bash
python3 -I build/audit_tables.py --report
node - <<'JS'
// count captions, scope attributes, SVG title/desc, figcaption order
JS
```

**Risk/rollback**

A “fix” to a source-supported claim can become a new defect. Keep the source reference and status in the register; if a claim cannot be sourced, label it papildinājums rather than deleting it. Rollback: restore the table/figure from baseline and keep the register note.

---

### T09 — Explain degrees of freedom, SEM and confidence intervals properly

**Category:** understandability · **Priority:** P1 · **Effort:** M (5–7 h) · **Risk:** medium · **Depends on:** T05
**Affected files:** `07_ch7.html`, `06_ch6.html`, ch15 recall, ch16 formulas
**Linked features:** —

**Evidence**

- `07_ch7.html:25` explains n−1 in one compressed sentence; it says the mean is computed from the same data and n gives a downward bias, but does not show why one degree of freedom is lost.
- `07_ch7.html:48` says the exact number 3 preserves two decimal places; the logic is imprecise (T05 corrects it).
- The CI interpretation paragraph is good but appears after the computation; students may still read “95%” as a property of the specific interval.
- There is no visual explanation of SD vs SEM, and no numeric check that the 95% CI is wide because n = 3.

**Target state**

The chapter explains the residual constraint (squared deviations sum to zero; one degree of freedom used by the mean), shows why n−1 is the unbiased variance denominator, distinguishes SD from SEM, and teaches the frequentist CI interpretation with a small simulation or static diagram. The worked example’s 12,70 ± 0,76 mL is explained as a wide interval, not a precise truth.

**Substeps (3)**

1. **Write the missing derivation.** Add a “Kāpēc n − 1?” box: deviations from the sample mean sum to zero, so only n−1 are free; dividing by n underestimates variance; show the three-value residual example.
2. **Visualise SD vs SEM and CI coverage.** Add a static diagram or a deterministic in-page simulation (no network) showing repeated samples, their means, and intervals; state that ~95% of intervals cover the reference in the long run.
3. **Rework the example and practice.** Replace the exact-3 rationale, add a “what the interval does not mean” callout, and add recall items that require interpreting the interval and choosing SD vs SEM.

**Subtasks**

**T09.1 The n−1 explanation**
1. Write the residual-sum argument with the 12,50/13,05/12,55 data; show the three deviations and their sum.
2. Explain the unbiased variance denominator and why n−1 is not a “correction fudge”; keep the algebra at the course level.
3. Add a one-sentence exam-ready rule: “Aprēķinot s no tās pašas izlases vidējā, viena brīvības pakāpe jau izlietota; tāpēc dala ar n−1.”

**T09.2 SD, SEM and CI visual**
1. Design a small static SVG or deterministic JS panel: population, repeated samples, sample means, ±t·SEM intervals; mark coverage.
2. Define SD (scatter of individual measurements) and SEM (uncertainty of the mean) side by side with the same data.
3. Add a “95% nozīmē procedūru, nevis konkrēto intervālu” callout; ensure the language matches the existing paragraph.

**T09.3 Practice and misconceptions**
1. Add a recall item: “Kāpēc 12,70 ± 0,76 ir tik plats, ja s = 0,304?” (n=3, t=4,3).
2. Add a diagnostic item: “Vai 95% ticamības intervāls nozīmē, ka 95% mērījumu ir intervālā?” (no).
3. Add an exam-style mixed question requiring mean, s, SEM and CI in sequence; compute the answer with the harness.

**Acceptance**

- The chapter contains a correct residual/degrees-of-freedom explanation, not only the “same data” sentence.
- SD vs SEM is explicit, with units and the √n factor.
- The CI paragraph says the 95% refers to the procedure, not the realised interval.
- The worked example’s exact-3 rationale is corrected and consistent with T05.
- New recall items are closed and their answers are verified.

**Verification**

```bash
grep -n 'n − 1\|brīvības pakāp\|standartkļūd\|ticamības intervāl' build/sections/07_ch7.html
node build/final_check.mjs
```

**Risk/rollback**

A simulation can become a new source of confusion if it is not deterministic or if it implies Bayesian coverage. Keep it optional, static-first, and label it “ilustratīvs modelis”. Rollback: keep the text explanation, remove the simulation.

---

### T10 — Teach mixed significant-figure operations with a decision tree

**Category:** understandability · **Priority:** P1 · **Effort:** M (4–6 h) · **Risk:** medium · **Depends on:** T05
**Affected files:** `08_ch8.html`, `02_ch2.html`, `07_ch7.html`, `app.js`, ch16 test vectors
**Linked features:** F10

**Evidence**

- The chapter gives the ×/÷ and +/− rules, but not a procedure for mixed operations such as “sum then divide by an exact count” or “multiply then convert units”.
- The Q3 mean and Q4c examples are mixed operations; their explanations currently rely on the exact-3 shortcut rather than a general method.
- Students see a rule table but no decision path; the instrument supports single operations plus average, not a full mixed chain.

**Target state**

A decision tree and six worked mixed cases make the order explicit: mark exact numbers → apply each operation’s rule → keep guard digits → round once at the end → report the error before the result. Students can explain why 12,70 is four s.f. and why 147 is three s.f.

**Substeps (3)**

1. **Write the decision tree.** Start with “Is the number exact?”; branch into +/− (decimal places), ×/÷ (s.f.), mixed (guard digits and operation order), and reporting (error first).
2. **Work six cases.** Include the mean of three titres, Q4c, a unit-chain conversion, a two-step dilution, an error-then-result case, and a deliberately ambiguous integer; compute all with the harness.
3. **Integrate practice.** Add a printable flowchart, an in-chapter exercise set, and an extension to the sig-fig instrument that shows the operation sequence.

**Subtasks**

**T10.1 Decision-tree design**
1. Draft the tree in plain Latvian with four decision nodes and no more than three branches per node.
2. Test the tree against all existing examples; if any example needs an ad-hoc rule, revise the tree.
3. Render it as inline SVG/HTML (text, not image-only) with a text alternative and print styling.

**T10.2 Six verified cases**
1. Select the six cases and encode them in `sigfig_cases.json` with intermediate and final values.
2. Write a short “why” for each: which operation sets the limit, which digits are guard digits, where rounding happens.
3. Add the cases to ch8 and ch16 E; ensure no answer is visible in a closed recall prompt.

**T10.3 Instrument and practice**
1. Extend the instrument to display the operation sequence and the limiting operand; keep the existing single-operation outputs.
2. Add a practice set of five new cases (not answers in visible markup; closed `<details>`).
3. Run the instrument and the harness; verify every case matches.

**Acceptance**

- A reader can follow the tree to the correct result for all six cases.
- The tree names exact numbers, guard digits, and the “round once” rule.
- The instrument shows why the limiting operand sets the precision.
- New practice items are closed and their answers are verified.
- The Q3/Q4c explanations reference the tree rather than an ad-hoc shortcut.

**Verification**

```bash
python3 -I build/check_sigfig_cases.py --check Master_2_tema_merijumi_un_grafiki.html
grep -n 'precīzs skaits\|precīzs skaitlis\|noapaļo tikai' build/sections/07_ch7.html build/sections/08_ch8.html
```

**Risk/rollback**

Mixed-operation rules are a simplification; do not claim they replace a full uncertainty budget. State the scope (“course-level significant figures”), and keep the error-first method as the more rigorous alternative. Rollback: keep the tree, remove the extra practice if it overwhelms the chapter.

---

### T11 — Clarify what a calibration line can and cannot prove

**Category:** understandability · **Priority:** P1 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T02, T06
**Affected files:** `03_ch3.html`, `09_ch9.html`, `10_ch10.html`, `11_ch11.html` (model language), ch14, new figure/data table
**Linked features:** F07

**Evidence**

- The document says R² is not proof of correctness, which is good, but the model limits are scattered across ch3, ch9 and ch10.
- The calibration line is reported with four-s.f. slope and three-s.f. intercept without a slope-uncertainty discussion; the tool uses a different precision (T06).
- LOD/LOQ are named but not developed; the relationship between sensitivity, linear range, and detection limit is not shown.
- There is no residual view or “what the line does not tell you” table.

**Target state**

A single calibration-model section explains the signal chain, linear range, slope/intercept, residuals, R², sensitivity, LOD/LOQ (named, not invented), extrapolation, and the difference between calibration and validation. A residual plot and a “limits” table make the model’s boundaries visible.

**Substeps (3)**

1. **Build the model map.** Create a one-page concept map/table: concentration → signal → calibration → inverse prediction; distinguish calibration, validation, selectivity, and uncertainty.
2. **Add the residual view.** Compute residuals for the six standards; add a static residual plot or data table; state that a pattern in residuals can reveal non-linearity even with high R².
3. **Add the limits table and exercises.** List what the line does not prove (selectivity, trueness, matrix effects, extrapolation, uncertainty of a single prediction); add two calibration diagnostic questions.

**Subtasks**

**T11.1 Model map and definitions**
1. Draft the map with the exact terms from ch14; no new synonyms.
2. Define calibration (建立 signal–concentration relation), validation (does the method meet the intended use), and routine analysis; keep the scope course-level.
3. Add a short “calibration is not validation” callout with a source/papildinājums label.

**T11.2 Residual and sensitivity view**
1. Compute residuals from the six standards and the fitted line; encode them in a JSON/table.
2. Add a residual plot/figure or a compact data table; explain that random residuals support linearity, a curve/trend suggests a wrong model.
3. Link sensitivity (slope) to LOD conceptually, without inventing a numeric LOD; explain that a larger slope usually lowers the detectable concentration but selectivity and noise also matter.

**T11.3 Limits and exercises**
1. Build a “Ko taisne nepierāda” table: selectivity, trueness, matrix effects, sample preparation, extrapolation, single-sample uncertainty.
2. Add two diagnostic questions: high R² with a biased reference; a sample above the top standard; a residual pattern.
3. Update the calibration tool to show residuals or a “model limits” note; keep the main input/output simple.

**Acceptance**

- One model section covers calibration, validation, residuals, R², sensitivity, LOD/LOQ limits, and extrapolation.
- The residual values are computed and reconciled with the fitted line.
- No numeric LOD/LOQ is invented; the source silence is explicit.
- The tool and the chapter agree on slope/precision (T06).
- New diagnostic answers are verified and closed.

**Verification**

```bash
python3 -I build/check_calibration.py --residuals
grep -n 'R²\|atlikum\|LOD\|LOQ\|valid' build/sections/10_ch10.html
```

**Risk/rollback**

Residual/uncertainty material can exceed the course scope. Keep it clearly labelled “papildinājums” and optional; the exam-critical content remains the line, inversion and extrapolation flag. Rollback: remove the residual figure, keep the limits table.

---

### T12 — Turn graph reading into a repeatable method and a trainer

**Category:** understandability + feature · **Priority:** P1 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T08
**Affected files:** `09_ch9.html`, `10_ch10.html`, `11_ch11.html`, `12_ch12.html`, figures, `app.js`, new data tables
**Linked features:** F05, F06

**Evidence**

- The graph-reading method is a single paragraph: horizontal line → vertical line → read; it does not teach how to choose the uncertainty or how to read a scale with a minor division.
- The document says “one minor division is the limit” but does not give a repeatable estimation rule or a practice loop.
- There is no data-table alternative under the plots; the trainer does not exist.
- Q7/Q8 readings have tolerances (±0.5 mg/L, ±15 s) but no interactive check.

**Target state**

A six-step reading method with an explicit uncertainty statement, three worked reads (calibration, half-life, density), a data table under each plot, and a trainer that gives tolerance-based feedback without score gimmicks.

**Substeps (3)**

1. **Write the method.** Six steps: identify axes/units → determine the minor division → locate the known value → draw horizontal/vertical to the line/curve → read to half a division → report value ± uncertainty.
2. **Add worked reads.** Re-read Q7 A=0.845 (25.9 ± 0.5 mg/L), hydrolysis 355/580 s (225 ± 15 s), density 1.0334 → 4.86 ± 0.05 pp; show the reading path and the rejected over-precision.
3. **Build the trainer and data tables.** Add a fixed-graph trainer with keyboard controls and tolerance feedback; add `<details>` data tables under all data figures.

**Subtasks**

**T12.1 Method and worked examples**
1. Draft the six-step method with a small inline diagram of the reading path.
2. Write three worked reads, each with input, line/curve intersection, minor division, uncertainty, and final digits.
3. Add a “what not to report” line for each (e.g., 25.937 mg/L).

**T12.2 Trainer**
1. Define 5 fixed tasks (calibration, Hg-203, hydrolysis, density, a new transfer line) with target values and tolerances.
2. Implement a keyboard-accessible cursor/input: arrow keys move, Enter checks; feedback states “too high/too low/within tolerance” and shows the correct path.
3. Test the trainer at 390/768/1440 and with JS disabled (static answer table fallback).

**T12.3 Data tables and accessibility**
1. Add a `<details>` data table under each plot with the exact plotted values, model equation, and note “model/redrawn”.
2. Ensure the table is not a duplicate of a recall answer; it is a data view, not a hidden answer key.
3. Check the accessibility tree and print: table visible when details open; no layout shift; captions preserved.

**Acceptance**

- The six-step method is visible and used in all graph examples.
- The trainer has fixed data, tolerance feedback, keyboard support, and a static fallback.
- Every data figure has a data-table alternative with the plotted values.
- No trainer item reveals a closed recall answer.
- The reading uncertainty is stated consistently (±0.5 mg/L; ±15 s; ±0.05 pp).

**Verification**

```bash
node - <<'JS'
// exercise the trainer's fixed vectors and keyboard path
JS
grep -c 'data-figure-table' Master_2_tema_merijumi_un_grafiki.html
```

**Risk/rollback**

A trainer can become a game; keep it plain, no scores or timers. It should teach the reading path, not reward speed. Rollback: keep the method and data tables, remove the interactive trainer if QA is incomplete.

---

### T13 — Fix half-life time origin, unit conversion and notation

**Category:** understandability + feature · **Priority:** P1 · **Effort:** M (5–7 h) · **Risk:** medium · **Depends on:** T06
**Affected files:** `11_ch11.html`, `app.js`, half-life SVGs, ch15/16, ch14 glossary
**Linked features:** F09

**Evidence**

- The hydrolysis graph starts at ≈115 s, not t=0; the document explains this, but the tool’s halving ladder still starts at 0 and has no offset input.
- The formula uses `t_{1/2}` (a fraction subscript) while prose uses `t½`; notation is inconsistent.
- The conversion table rounds 46.595 d correctly, but the tool returns 3.6667 min for 220 s while the text advises 3.7 min; the relationship between intermediate precision and reported precision is not shown in the tool.
- S17/S18 are handled honestly, but the student still needs a repeatable procedure for data that start at t0.

**Target state**

The chapter teaches the offset model `c(t)=c0·2^−(t−t0)/t½`, successive halving as a time difference, and unit conversion with guard digits. The tool accepts a start time and shows absolute times and intervals; notation is `t½` consistently; test vectors cover 46.595 d, 220 s and a 115 s offset.

**Substeps (3)**

1. **Rewrite the model.** Add the offset form, explain why the first reading is not a half-life, and derive the interval method; keep the 220 vs 232.5 s reconciliation.
2. **Fix notation and figures.** Use `t½` in MathML/prose/SVG; ensure the hydrolysis figure shows cumulative times and intervals; label the source’s `sec`/`Conc (M)` correction.
3. **Upgrade the tool.** Add `t0` and optional `c0` inputs; display absolute halving times and intervals; label intermediate vs reported precision; add test vectors.

**Subtasks**

**T13.1 Offset model**
1. Write the general formula with `t0`; define what `t0` is (first observed time, not necessarily reaction start).
2. Work the hydrolysis example: t0=115 s, levels at 355/580 s, intervals 240/225 s, mean 232.5 s.
3. Add a “t0 = 0 trap” callout and a recall item.

**T13.2 Notation and figures**
1. Replace `t_{1/2}` with `t½` in MathML, prose, SVG labels and JS strings; ensure screen readers say “t puse”.
2. Update the hydrolysis figure to show cumulative times and Δt brackets; no collisions.
3. Check the Hg-203 conversion table’s guard digits and the 220 vs 232.5 wording.

**T13.3 Tool and tests**
1. Add `t0` (default 0) and optional `c0`; compute halving times `t0 + k·t½` and intervals.
2. Show both intermediate (more digits) and reported (2–5 s.f. per input) values; do not silently round the input.
3. Add test vectors: 46.595 d; 220 s; t0=115 s, t½=232.5 s; 1 d; invalid/zero input.

**Acceptance**

- The offset model and interval method are explained and used consistently.
- `t½` notation is consistent across MathML, prose and SVG.
- The tool accepts t0 and displays absolute times and intervals.
- Test vectors pass; invalid inputs produce a clear message.
- No “diennakts” active use; S17 wording remains accurate.

**Verification**

```bash
node - <<'JS'
// run half-life vectors including t0=115
JS
grep -n 't_{1/2}\|t½\|diennakts' build/sections/11_ch11.html
```

**Risk/rollback**

Adding `t0` can confuse users if the UI does not explain it; default to 0 and show a worked example. Rollback: keep the text model, revert the tool to the single-input version.

---

### T14 — Restructure solution preparation and density around a decision flow; add a calculator

**Category:** understandability + feature · **Priority:** P1 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T06
**Affected files:** `12_ch12.html`, `02_ch2.html` (cross-links), `app.js`, new calculator markup, ch15/16
**Linked features:** F08

**Evidence**

- The chapter is rich but sequence-heavy: protocol table, formulas, worked example, graph, density–temperature table, interpolation, mistake block. A student can lose the decision “what is known / what is asked / is V final or solvent?”.
- The final density precision is self-contradictory (T06).
- There is no calculator for the common exam tasks: mass fraction, mass concentration, molar concentration, dilution, density.
- The temperature correction is explained, but the calculator cannot help students see the effect or avoid using a 20 °C line at 25 °C.

**Target state**

The chapter follows a five-step decision flow: define the target → prepare the solution (final volume, temperature, mixing) → measure mass/volume → compute ρ, w, γ, c → report with uncertainty and temperature. A calculator handles mass fraction, concentration and dilution with unit checks and explicit final-volume assumptions.

**Substeps (3)**

1. **Restructure the chapter.** Put a one-page decision flow at the top; move the protocol details under step 2; place the calculations under step 3; keep the temperature table as a boundary condition.
2. **Build the calculator.** Add modes for `w` from mass/solution mass, `ρ` from mass/volume, `γ` and `c` from w/ρ/M, and dilution `c1V1=c2V2`; show intermediate and final values; warn when V is solvent vs final.
3. **Add error-diagnosis cases.** Five cases: mass vs solution mass, 5 g + 100 mL ≠ 100 mL, density vs concentration, 20 °C line at 25 °C, over-precise result.

**Subtasks**

**T14.1 Chapter flow**
1. Draft the five-step flow with the key question at each step and a link to the relevant section.
2. Reorder the existing content under the steps without deleting source-based material; keep the illustrative example clearly labelled.
3. Add a “before you calculate” checklist: target quantity, units, final volume, temperature, significant figures.

**T14.2 Calculator**
1. Define the input/output model and formulas; test against the worked example (5.02 g, 103.34 g, 100.0 mL, M=58.44).
2. Implement the UI with unit selectors and validation; show the formula, intermediate, result and a one-line “why”.
3. Add fixed test vectors and a static fallback table; no storage.

**T14.3 Error-diagnosis cases**
1. Write five symptom → cause → fix cases, each linked to the relevant step.
2. Add two closed recall items: final volume vs solvent volume; density vs concentration.
3. Print the calculator’s fallback table and verify the values; update the change log.

**Acceptance**

- The chapter has a visible five-step decision flow; each section maps to a step.
- The calculator’s outputs match the worked example and test vectors.
- It explicitly distinguishes final volume from solvent volume and flags missing temperature.
- The density precision policy from T06 is applied throughout.
- Error cases are sourced/labelled and do not invent lab data.

**Verification**

```bash
node - <<'JS'
// calculator vectors: w=4.86, rho=1.0334, c=1.83 for 10% example, dilution
JS
grep -n '1,0334\|100,0 mL\|gala tilpums' build/sections/12_ch12.html
```

**Risk/rollback**

A calculator can encourage button-pressing without understanding. Keep the formula and “why” visible, and make the static table usable without JS. Rollback: keep the chapter flow, remove the calculator if its validation is incomplete.

---

### T15 — Replace ad-hoc type sizes and spacing with a small token system

**Category:** redesign · **Priority:** P2 · **Effort:** M (5–7 h) · **Risk:** low–medium · **Depends on:** T07
**Affected files:** `build/style.css`, font build (`build/build_doc.py`), figure SVG label sizes
**Linked features:** —

**Evidence**

- Inspect reports 15 font sizes at the first viewport; the CSS has 97 `font-size` declarations. Sizes 13.5/14.5/15.5/16.5 are semantic noise.
- Spacing is ad hoc: 26/28/30/34/38/44/55/92/118 px, plus one-off margins.
- Body is 18 px/1.62 at 68 ch; the top of the contract range. Latvian long words and tables make 64–66 ch safer.
- Only upright 400/700 faces are embedded; `<i>`/math variables are synthesised oblique.

**Target state**

A seven-step type scale and a 4-px spacing scale, expressed as custom properties, cover all screen text. Body stays 18 px/1.55–1.65 at 64–66 ch. A true italic face (or a deliberate system-italic fallback) replaces faux oblique. Print uses its own small set of pt sizes.

**Substeps (3)**

1. **Inventory and map.** List every selector’s size/line-height/margin; assign each to a token (display, h1, h2, h3, body, table, small, micro); identify selectors that do not fit and simplify them.
2. **Define and apply tokens.** Add `--text-*`, `--space-*`, `--leading-*`; replace declarations; normalise section spacing, card padding, table paddings, and figure margins; set measure to 64–66 ch.
3. **Add real italics and verify.** Embed an OFL italic face subset (or switch variables to a system italic stack), test Latvian diacritics, compare screenshots at 1440/768/390 and print.

**Subtasks**

**T15.1 Type and spacing inventory**
1. Export a CSV of selector, size, line-height, margin/padding, and usage count; flag every off-scale value.
2. Group selectors by semantic role and propose the minimal token set; keep body 18, small 14, table 15, captions 14, labels 13–14, h3 22–24, h2 30–32, h1 48–56, display 64–75 only if justified.
3. Check the print pt sizes separately; do not force screen tokens into print.

**T15.2 Token implementation**
1. Add the custom properties and replace values in a single CSS pass; keep a visual diff.
2. Normalise vertical spacing to 4/8/12/16/24/32/48/64/96; remove one-off 26/34/38/55/118 values where they have no semantic role.
3. Set `--measure: 64ch` or `66ch`; check paragraph line length and long-word wrapping at 390.

**T15.3 Italic and diacritic verification**
1. Subset/embed an OFL italic face (or use a true italic system fallback) and map `font-style: italic`; verify `ā č ē ģ ī ķ ļ ņ š ū ž` in italics at 14–18 px.
2. Check MathML variables and `<i>` spans; ensure no faux oblique remains.
3. Screenshot body, headings, tables and formulas at 1440/768/390 and in print; compare with the baseline.

**Acceptance**

- ≤8 distinct screen sizes, all mapped to named roles; no 13.5/14.5/15.5/16.5 half-steps unless documented.
- All margins/paddings are on the 4-px scale or documented exceptions.
- Body 18 px, line-height 1.55–1.65, measure 64–66 ch.
- True italic renders; no synthesised oblique; diacritics intact.
- Visual hierarchy is preserved or improved; no clipped headings/figures.

**Verification**

```bash
python3 - <<'PY'
# count unique px font sizes and spacing values
PY
node workspace_skills/design-taste-frontend/scripts/inspect.mjs Master_2_tema_merijumi_un_grafiki.html --allow few-pictures,off-centre,still-page
```

**Risk/rollback**

A type-scale change can make tables too small or headings too weak. Do a component-by-component visual diff and keep the old CSS behind a branch/copy for rollback. Do not change print sizes in the same pass.

---

### T16 — De-card the layout, redesign the masthead, and refine the semantic roles

**Category:** anti-slop/restyle · **Priority:** P2 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T15
**Affected files:** `build/style.css`, `00_front.html`, role/formula/instrument markup, ch1 legend
**Linked features:** —

**Evidence**

- Inspect flags “5 rows of identical boxed cards”; the HTML has 44 role blocks, 10 formula boxes, 3 instrument boxes.
- Masthead: 75 px h1, 0.98 leading, −0.035 tracking, two CTA buttons. It reads like a landing hero, not a reference document.
- Role blocks all use the same surface box; the semantic difference is carried mostly by a 4 px left bar and a label. With 44 boxes, the page becomes a stack of cards.
- Formula boxes and instrument boxes add another layer of containers; the content hierarchy is flattened.

**Target state**

The opening reads as a title page/reading surface, not a marketing page: no CTA buttons, a concise title block, metadata, and a study-path list. Role blocks become open typographic bands with a label and a non-colour cue; formulas lose the decorative box; only the interactive instruments keep a functional panel. Card rows drop to ≤2.

**Substeps (3)**

1. **Redesign the masthead.** Reduce the h1 to 48–56 px, remove the primary/secondary CTA row, keep a quiet “Sākt ar 1. nodaļu” link in the metadata or study path, and make the five outcomes the visual anchor.
2. **Remove non-functional containers.** Turn Noteikums/Biežākā kļūda/Pārbaudīts into open bands with a left rule + label; remove surface backgrounds from formula boxes; keep one panel style for instruments.
3. **Re-check hierarchy and anti-slop.** Ensure roles remain distinguishable by label/texture, not colour alone; keep one accent; verify card rows and box count; screenshot and compare.

**Subtasks**

**T16.1 Masthead and opening**
1. Draft three masthead variants (title block + outcomes; title block + “how to use”; title block + study path) and choose one that reads as a document.
2. Remove the CTA buttons; keep a single text link and the theme/print controls in a quiet toolbar.
3. Re-render at 1440/768/390 and check the h1 line breaks, diacritics and first-screen information density.

**T16.2 Role and formula de-carding**
1. Define two visual levels: open band (Noteikums) and tonal band (mistake/verified); remove the common surface box.
2. Remove the formula box background; use spacing, a small label and a left rule only where needed; ensure formulas still stand out.
3. Count boxes and card rows; target ≤2 card rows and ≤1 instrument panel per screen.

**T16.3 Anti-slop verification**
1. Run lint/inspect; target 0 FAIL and fewer WARN (card-rows should disappear).
2. Check the three roles without colour (grayscale screenshot); labels and bars must still distinguish them.
3. Review at 1440/768/390 and in print; compare against the baseline for unintended hierarchy loss.

**Acceptance**

- No hero CTA row; the opening reads as a reference/title page.
- Role blocks no longer all share the same boxed card; the semantic roles remain distinguishable in grayscale.
- Formula boxes are open; only the 3 instruments keep functional panels.
- Inspect card-rows warning is gone or reduced to an intentional, documented pattern.
- Lint 0 FAIL; no new accessibility or contrast regression.

**Verification**

```bash
node workspace_skills/design-taste-frontend/scripts/lint.mjs Master_2_tema_merijumi_un_grafiki.html
node workspace_skills/design-taste-frontend/scripts/inspect.mjs Master_2_tema_merijumi_un_grafiki.html --allow few-pictures,off-centre,still-page
```

**Risk/rollback**

Removing boxes can reduce scannability if the labels are not strong enough. Test with a grayscale screenshot and a quick reading test; keep the old CSS for rollback. Do not remove the instrument panel—it signals interactivity.

---

### T17 — Replace mobile side-scrolling tables with a deliberate responsive strategy

**Category:** redesign · **Priority:** P2 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T08
**Affected files:** `style.css`, table markup/wrappers, `app.js` scroll hints, vessel matrix, ch16 tables
**Linked features:** —

**Evidence**

- 46 tables; 23 scroll hints visible at 390; inspect flags 9 side-scrolling rows.
- The vessel matrix at 390 shows only three columns and clips the rest; the student must scroll sideways and loses row context.
- Some tables are true numeric matrices; others are comparisons or procedures that would read better as stacked rows.
- The current hint text (“Ritiniet tabulu horizontāli”) is accurate but does not solve the cognitive cost.

**Target state**

Tables are classified and styled by type: small comparisons stack into labelled rows on phones; true numeric matrices keep a sticky first column, a visible edge affordance, and a clear hint; the vessel matrix becomes per-vessel detail cards at ≤600 px; no content is lost or duplicated for search engines.

**Substeps (3)**

1. **Classify all 46 tables.** Mark each as numeric matrix, comparison, procedure, glossary, test vector, or change log; decide the mobile pattern per class.
2. **Implement patterns.** Add CSS for stacked rows using `data-label`/`::before`; keep semantic `<table>` markup on wide screens; add sticky first column + scroll shadows for numeric matrices; convert the vessel matrix to `<details>` per vessel on mobile.
3. **Test and simplify hints.** Verify at 320/390/768/1440; count side-scrollers; ensure the hint appears only when scrolling is real; print tables normally.

**Subtasks**

**T17.1 Classification**
1. Build a table inventory with rows/columns, cell length, numeric density, and primary reading task.
2. Assign a pattern: stack, scroll/sticky, cards, or leave as-is; document exceptions.
3. Estimate the number of side-scrollers after the change; target ≤5 intentional tables at 390.

**T17.2 Pattern implementation**
1. Add a responsive “stacked” style for short comparison/procedure tables using `data-label` attributes; preserve the table semantics in the accessibility tree.
2. Add sticky first column + edge shadow + hint for numeric matrices; ensure the first column remains readable at 390.
3. Convert the vessel matrix to a mobile-only per-vessel `<details>` presentation (or a card list) generated from the same data; keep the desktop table.

**T17.3 QA and print**
1. Test at 320/390/768/1440; check for clipped text, lost columns, double labels, and keyboard scroll.
2. Verify the scroll hints appear only when `scrollWidth > clientWidth`; no false hints.
3. Print the affected pages; tables must not split mid-row, sticky styles must be disabled, and captions must stay attached.

**Acceptance**

- ≤5 intentional horizontally scrolling tables at 390; all others stack or card.
- No clipped content; every original column remains accessible.
- The vessel matrix is usable at 390 without losing row context.
- Hints are accurate (no hint when no overflow).
- Print output is unchanged in meaning; no sticky artefacts.

**Verification**

```bash
node - <<'JS'
// count tables with scrollWidth > clientWidth at 390, list captions
JS
node build/final_check.mjs
```

**Risk/rollback**

Stacked tables can become very tall and duplicate labels. Keep them collapsible (`<details>`) for long rows and test reading speed. Rollback: revert a single table class to the scroll pattern.

---

### T18 — Add section navigation, reading aids, and a printable quick-reference pack

**Category:** restyle + print · **Priority:** P2 · **Effort:** L (8–12 h) · **Risk:** medium · **Depends on:** T15, T17
**Affected files:** TOC generation/build, `app.js`, `style.css`, print CSS, new quick-reference section
**Linked features:** F02, F11

**Evidence**

- Sidebar TOC is chapter-level only; 94 h3 sections; no section navigation or reading progress.
- 107 screens; no persistent back-to-top until the footer; mobile TOC is a single collapsed details.
- Print: 97 pages, forced appendix E page, half-empty p96, compact footer; no short exam-reference edition.
- The prompt values print and exam preparation; a 4–6 page quick-reference would serve both.

**Target state**

A section-level TOC with active tracking and a small reading-progress/back-to-top control; a print-only quick-reference pack (4–6 pages) with units, formulas, sig-fig rules, vessel matrix condensed, calibration/half-life steps, and top mistakes; a print flow without orphan pages.

**Substeps (3)**

1. **Generate section navigation.** Build a nested TOC from h2/h3 IDs; add active-state tracking and a compact mobile view; add a back-to-top control after two screens.
2. **Build the quick-reference pack.** Reuse verified content only; produce a print-only 4–6 page section with the highest-value rules; test print pagination.
3. **Repair print flow.** Inspect the 97-page PDF page by page; fix the appendix break/orphan, footer, and any widows; re-export and verify.

**Subtasks**

**T18.1 Section TOC and progress**
1. Add stable IDs to all h3 headings and generate a nested list (chapter → section) at build time.
2. Implement active tracking with `IntersectionObserver`; add a “atpakaļ uz sākumu” control; keep keyboard access and reduced motion.
3. Test at 1440/768/390; ensure the sidebar does not become a second long document; collapse on mobile.

**T18.2 Quick-reference pack**
1. Select the highest-value content: units/conversions, formulas, sig-fig flowchart, vessel matrix condensed, calibration inversion, half-life method, top 15 mistakes, exam checklist.
2. Build a print-only section with clear page breaks and a compact two-column layout; no new facts, every item links to its chapter.
3. Export and inspect the quick-reference pages; ensure 4–6 pages and readable at A4.

**T18.3 Print flow**
1. Inspect all 97 pages for orphan headings, blank pages, split tables, missing captions and footer issues.
2. Decide appendix E’s break: keep a clean page start and fill p96 with a summary/checklist, or allow a table split with repeated header; document the choice.
3. Re-export with all details open; verify page count, running header, page numbers, and no regression on the key pages.

**Acceptance**

- Section TOC lists all h3 sections, tracks the current section, and works by keyboard.
- A visible back-to-top control appears after scrolling; no motion when reduced motion is set.
- Quick-reference is 4–6 pages, self-contained, and uses only verified content.
- No blank/orphan page in the full PDF; all details open; captions and tables intact.
- Print page count is intentional and documented.

**Verification**

```bash
node build/final_check.mjs
pdfinfo build/shots/final/Master_2_tema.pdf | grep Pages
# render and inspect p96, p97, quick-reference pages
```

**Risk/rollback**

A section TOC can overwhelm the sidebar; show only the current chapter’s sections, not all 94 at once. Quick-reference duplication can drift; generate it from the same source snippets/verified JSON. Rollback: keep the chapter-level TOC and full print edition.

---

### T19 — Add offline full-text search and first-use glossary links

**Category:** feature · **Priority:** P2 · **Effort:** XL (12–18 h) · **Risk:** medium · **Depends on:** T01, T18
**Affected files:** build index script, `app.js`, topbar/sidebar markup, ch14 anchors, `style.css`
**Linked features:** F01, F12

**Evidence**

- 26,773 tokenised words and 107 screens; no search.
- The glossary exists in ch14 but no first-use links; a student reading ch3 has to remember that `absorbance` is defined later.
- Search must not reveal answers to closed recall prompts; the recall answers are in the DOM and would otherwise appear in snippets.
- The document must remain offline and self-contained; no external search library.

**Target state**

A build-time search index covers headings, body paragraphs, table captions and glossary terms, with diacritic folding and synonyms; recall answers are excluded by default. A search field (Ctrl/Cmd+K or “/”) shows grouped results with snippets, keyboard navigation, and a link to the exact section. First-use glossary terms link to their ch14 anchor with an accessible definition popover.

**Substeps (3)**

1. **Build the index.** Extract searchable blocks at build time; normalise Latvian diacritics; add synonyms; exclude `.recall-answer`; store title, chapter, section, anchor, text, and type.
2. **Build the UI.** Add a search control in the topbar/sidebar; implement combobox semantics, result grouping, keyboard navigation, empty state, and a “no results” message; no network.
3. **Link the glossary.** Add first-use links for 40–60 high-value terms; implement a focus/click popover with the definition and a link to ch14; ensure print shows plain text, not popovers.

**Subtasks**

**T19.1 Index generation**
1. Write a build-time extractor that walks the DOM, skips `.recall-answer`, script/style/svg, and change-log source rows, and emits JSON with diacritic-folded text.
2. Add synonyms for the top term families (absorbcija/absorbance; precizitāte/pareizība; mērkolba/volumetric flask; pussabrukšana/half-life).
3. Verify index size and search latency on the 26k-word document; keep the embedded JSON small enough for the single-file budget.

**T19.2 Search UI**
1. Add the search field and results panel with proper `role="combobox"`, `aria-expanded`, `aria-activedescendant`, and live result counts.
2. Implement keyboard: `/` and Ctrl/Cmd+K focus; arrows move; Enter opens; Escape closes; Tab leaves; no focus trap.
3. Style results with section breadcrumbs and snippets; highlight the match; test at 390/768/1440 and with dark mode.

**T19.3 Glossary linking**
1. Select the first occurrence of each high-value term per chapter (not every occurrence) and link it to `#glossary-<id>`; preserve the sentence.
2. Add a definition popover on focus/click with the canonical term, one-sentence definition, unit and “don’t confuse with”; no hover-only.
3. Print test: links render as plain text, popovers are hidden, and the glossary remains available in ch14.

**Acceptance**

- Search returns results in <100 ms for a 26k-word document; diacritic-insensitive; keyboard accessible; no network.
- Recall answers are not searchable by default; no answer snippets leak.
- First-use term links open a definition accessible by keyboard and screen reader.
- Print shows no popovers or broken links.
- Single-file size remains within the prompt’s 2 MB budget.

**Verification**

```bash
python3 -I build/build_search_index.py --check
node - <<'JS'
// type “absorbcija”, “n-1”, “mērkolba”; check results and no recall answers
JS
```

**Risk/rollback**

Search can leak answers or create a second navigation model. Exclude recall answers, label result types, and keep the chapter TOC as the primary navigation. Rollback: remove the UI, keep the index unused.

---

### T20 — Build a recall workspace, exam mode, and consent-based persistence

**Category:** feature · **Priority:** P2 · **Effort:** XL (12–20 h) · **Risk:** medium–high · **Depends on:** T19
**Affected files:** `app.js`, recall markup/build, `style.css`, ch15, print CSS
**Linked features:** F03, F04, F13, F14

**Evidence**

- 113 recall items, all in closed `<details>`; marks work in memory only; no filter by chapter/concept/status; no “review unknown only”; no exam simulation.
- The document explicitly avoids gamification; any new feature must keep that stance.
- AGENTS forbids localStorage writes that survive without consent; persistence must be opt-in and resettable.
- Students preparing for a 55% test need a way to rehearse a mixed set and print an answer sheet, not just browse by chapter.

**Target state**

A plain recall workspace: filter by chapter/concept/status; review unknown-only; counts update; no score gimmicks. An exam mode presents a stratified random set, reveals answers only after an attempt, and prints an answer sheet. Persistence is off by default; an explicit “Saglabāt šajā pārlūkā” consent enables localStorage with a reset button.

**Substeps (3)**

1. **Data model and filters.** Add chapter/outcome/difficulty metadata (derived, not hand-maintained); build filter controls and an unknown-only queue; keep counts and empty states clear.
2. **Exam mode.** Build a stratified sampler; present one item at a time; “Atklāt atbildi” after an attempt; no timer by default; final list of unknown items; print answer sheet.
3. **Consent persistence and QA.** Add an explicit consent toggle for localStorage, a reset/clear action, and a privacy note; test keyboard, mobile, print, no-storage default, and no answer leakage.

**Subtasks**

**T20.1 Filters and unknown-only review**
1. Derive `data-chapter` from the enclosing section and `data-outcome` from a mapping; keep `data-concepts` as the fine tag; assign difficulty only if it can be justified (otherwise omit).
2. Build filter controls (chapter, concept, status) with a clear button; update the summary; preserve `<details>` state while filtering.
3. Add an “tikai nezināmie” queue that walks the filtered items one by one; no timer, no score.

**T20.2 Exam mode**
1. Define a default 20-item stratified sample across chapters/outcomes; seed or randomise on start; no persistence.
2. Present one prompt at a time with “Atklāt atbildi” after the student has attempted it; mark known/unknown; show a final plain list.
3. Add a print answer sheet with prompts and blank lines; answers on a separate page; no hidden answers in the prompt markup.

**T20.3 Consent persistence and QA**
1. Add an off-by-default “Saglabāt atzīmes šajā pārlūkā” control with a one-sentence explanation and a “Dzēst saglabātās atzīmes” action.
2. Store only a compact map of item IDs → known/unknown and the theme preference; no personal data; no automatic writes before consent.
3. Test reload, reset, private browsing, disabled storage, mobile, keyboard and print; verify no answers are visible before reveal.

**Acceptance**

- Filters work by chapter/concept/status; unknown-only queue is usable; counts are accurate.
- Exam mode presents a mixed set, reveals answers only after an attempt, and prints a usable answer sheet.
- Persistence is off by default; consent is explicit; reset works; no personal data.
- No gamification (no XP, streaks, badges, confetti, scores presented as mastery).
- No answer leakage in closed prompts or exam prompt markup.
- Keyboard and mobile QA pass.

**Verification**

```bash
node - <<'JS'
// click filters, start exam, reveal, reload with storage disabled/enabled, check no leak
JS
grep -n 'localStorage' Master_2_tema_merijumi_un_grafiki.html
```

**Risk/rollback**

Exam mode and persistence add state complexity and privacy risk. Keep them optional, default off, and provide a static print alternative. Rollback: remove the storage layer, keep filters/exam in memory only.

---

---

## 4. Feature catalogue

The features below are not a wish list detached from the defects. Each one either removes a measured friction (107 screens, 46 tables, 113 recall items) or closes a pedagogical gap (graph reading, time origin, solution preparation, calibration limits). Features are prioritised by study value per implementation hour and by their fit with the offline, no-gamification, no-answer-leak constraints.

### 4.1 Priority tiers

| Tier | Features | Rationale |
|---|---|---|
| **Must-have** | F01 search, F02 section navigator, F03 recall filters, F06 figure data tables, F11 quick reference | These directly address navigation, accessibility and exam preparation; they are useful even if nothing else ships. |
| **High value** | F04 exam mode, F05 graph trainer, F08 dilution calculator, F09 half-life offset simulator, F12 glossary links | These close specific comprehension gaps and reuse verified data. |
| **Later / optional** | F07 residual panel, F10 sig-fig trainer v2, F13 error-diagnosis map, F14 consent persistence | Valuable, but can be delivered after the core restyle without blocking it. |
| **Considered and deferred** | spaced repetition, AI tutor, analytics, social sharing, read-aloud | See §4.4; they conflict with offline/privacy/no-gamification or add disproportionate complexity. |

### 4.2 Feature specifications

#### F01 — Offline full-text search and command palette

**Problem:** 26,773 words and 107 screens; browser Find cannot distinguish a definition from a table cell, cannot fold diacritics, and jumps into hidden recall answers.
**Behaviour:** `Ctrl/Cmd+K` or `/` opens a search panel. Results are grouped by chapter/section with type labels (“sadaļa”, “tabula”, “termins”, “attēls”). Typing is diacritic-insensitive (`absorbcija` finds `absorbcija`/`absorbance` via synonyms; `merkolba` finds `mērkolba`). Enter opens the exact anchor; Escape closes; arrows move; the query is not persisted.
**Data:** build-time JSON index of headings, body paragraphs, table captions, figure captions and glossary terms. Exclude `.recall-answer`, exam answers, change-log source quotations, and hidden print-only content.
**Offline/a11y:** no external library; combobox semantics; `aria-activedescendant`; visible focus; result count in a polite live region; 44 px touch targets; no motion beyond focus.
**Acceptance:** <100 ms search on the current document; no network requests; no recall-answer snippets; keyboard-only path; 390 px layout; dark mode.
**Effort:** XL. **Task:** T19.

#### F02 — Section navigator, active marker and back-to-top

**Problem:** the sidebar lists only 16 chapters; there are 94 h3 sections. A student who remembers “the n−1 explanation” cannot jump to it.
**Behaviour:** the sidebar shows the current chapter’s sections; the active section is marked with text weight and a rule, not a decorative dot; a small “Atpakaļ uz sākumu” control appears after two screens; a plain “3/16” reading-position text may be shown, but no progress bar animation.
**Data:** generated from h2/h3 IDs at build time; no hand-maintained duplicate list.
**Offline/a11y:** `IntersectionObserver`; keyboard links; `aria-current="location"`; mobile collapses to one `<details>`; `prefers-reduced-motion` disables smooth scrolling.
**Acceptance:** all 94 sections reachable; current section updates; no layout shift; mobile TOC does not cover content; print hides the control.
**Effort:** M. **Task:** T18.

#### F03 — Recall filters and “unknown-only” review queue

**Problem:** 113 recall items are browsable only in document order; marks reset on reload; there is no way to review just the items marked unknown.
**Behaviour:** filters for chapter, concept tag and status (`zināju`, `nezināju`, `bez atzīmes`); a “Rādīt tikai nezināmos” queue; counts update live; a clear-filters action; no score, XP, streak or percentage-as-mastery.
**Data:** existing `.recall-item` elements, `data-concepts`, derived chapter and outcome; no new content.
**Offline/a11y:** filter controls are native form elements; state updates in memory by default; optional persistence in F14; keyboard and screen-reader labels; 44 px targets.
**Acceptance:** filter counts match the visible items; unknown-only queue works; no answer is revealed by filtering; reset returns to all items.
**Effort:** L. **Task:** T20.

#### F04 — Exam mode with printable answer sheet

**Problem:** chapter-by-chapter recall does not simulate the mixed test; the pass mark is 55%, but the document offers no timed/untimed mixed rehearsal.
**Behaviour:** choose 20/30/40 items, stratified across chapters/outcomes; one prompt at a time; “Atklāt atbildi” only after an attempt; mark known/unknown; final plain list of items to revisit; optional timer off by default; “Drukāt atbildes lapu” produces prompts + blank lines, answers on a separate page.
**Data:** existing recall items only; no new questions unless they pass the same verification harness.
**Offline/a11y:** no storage by default; keyboard controls; visible focus; no autoplay; print CSS; no answer in the prompt markup before reveal.
**Acceptance:** stratified set contains the requested number; answers hidden before reveal; final list accurate; printed sheet usable; no gamification; reload starts a fresh set.
**Effort:** L. **Task:** T20.

#### F05 — Graph-reading trainer

**Problem:** the document explains the reading path but gives no practice loop; students cannot tell whether their read is within the graph’s precision.
**Behaviour:** five fixed graphs (calibration, Hg-203, hydrolysis, density, a transfer line); a keyboard-movable crosshair or numeric input; the student reads a target; feedback says “within tolerance”, “0.3 mg/L high”, and shows the correct path; tolerance derives from the minor division, not an arbitrary percentage.
**Data:** the same plotted values used in the figures; no new data.
**Offline/a11y:** vanilla SVG/JS; arrow keys; visible focus; static answer table when JS is off; no timer, no score.
**Acceptance:** all five vectors pass; tolerance matches the stated precision; keyboard-only path; mobile layout; static fallback.
**Effort:** M. **Task:** T12.

#### F06 — Data-table alternative under every data figure

**Problem:** a screen-reader user gets the SVG `<desc>` but cannot inspect the values; a student cannot check a plotted point against the table.
**Behaviour:** a `<details>` “Dati un modelis” under each plot with the exact plotted values, the model equation, and a “model/redrawn” label; the table is a data view, not the recall answer.
**Data:** `build/verified.json` and figure-generation data; no retyped numbers.
**Offline/a11y:** semantic table with caption and scopes; details is keyboard-native; print expands or keeps a note; no duplicate hidden answers.
**Acceptance:** all 10 figures have an appropriate alternative (data table for plots, long description for schematics); values match the figure; print works.
**Effort:** S. **Task:** T08/T12.

#### F07 — Calibration residual and model-limits panel

**Problem:** R² is explained as “not proof”, but students cannot see what a residual pattern looks like or where the model stops.
**Behaviour:** a compact residual table/plot for the six standards; a “Ko taisne nepierāda” list (selectivity, trueness, matrix, extrapolation, single-sample uncertainty); no invented LOD/LOQ numbers.
**Data:** residuals computed from the six standards and the fitted line.
**Offline/a11y:** static SVG/table; optional toggle; data table; no external stats library.
**Acceptance:** residuals reconcile with the fitted line; the model-limits list is source/papildinājums-labelled; no numeric LOD/LOQ invented.
**Effort:** M. **Task:** T11.

#### F08 — Solution preparation and dilution calculator

**Problem:** students confuse final volume with solvent volume, mass fraction with concentration, and density with concentration; the chapter has many steps but no self-check.
**Behaviour:** modes for `w` (mass/solution mass), `ρ` (mass/volume), `γ`/`c` (from w/ρ/M), and dilution (`c1V1 = c2V2`); inputs with units; outputs show the formula, intermediate, result and a “why”; warns when the user enters solvent volume instead of final volume and when temperature is missing.
**Data:** the verified worked example (5.02 g, 103.34 g, 100.0 mL, M=58.44) and standard formulas; no invented lab data.
**Offline/a11y:** vanilla JS; static table fallback; labels; 44 px; no storage.
**Acceptance:** test vectors match; the final-volume warning triggers; no unit ambiguity; print fallback works.
**Effort:** M. **Task:** T14.

#### F09 — Half-life offset simulator

**Problem:** the hydrolysis data start at 115 s; the existing tool assumes a start at zero and cannot show the difference between cumulative time and interval.
**Behaviour:** inputs `t½`, `t0` (default 0), optional `c0`; outputs four time units, absolute halving times (`t0 + k·t½`), intervals, and a ladder; the plot marks the offset.
**Data:** fixed vectors (46.595 d; 220 s; t0=115 s, t½=232.5 s).
**Offline/a11y:** vanilla JS; static table; unit selectors; keyboard; no storage.
**Acceptance:** offset and interval values correct; 220 vs 232.5 handled; invalid inputs explained; no silent rounding.
**Effort:** M. **Task:** T13.

#### F10 — Significant-figure mixed-operation trainer

**Problem:** the existing checker handles single operations and average; mixed operations and exact numbers remain a memorisation trap.
**Behaviour:** generated cases with a visible operation sequence; the student enters the answer; feedback names the limiting operand, the exact numbers, the guard digits and the rounding step; no score.
**Data:** deterministic case generator + verified vectors; exact numbers marked.
**Offline/a11y:** vanilla JS; keyboard; static case table; no storage.
**Acceptance:** all generated cases pass the Decimal harness; feedback matches the chapter’s decision tree; no “mastery” score.
**Effort:** M. **Task:** T10/T05.

#### F11 — Printable quick-reference pack

**Problem:** the full document is 97 pages; a student needs a 4–6 page exam sheet with the highest-value rules and traps.
**Behaviour:** print-only pages: units/conversions; formulas; sig-fig decision tree; vessel matrix condensed; calibration inversion; half-life method; top 15 mistakes; exam checklist. Each item links to its chapter in the screen edition.
**Data:** reuse verified content only; generate from the same snippets/JSON to avoid drift.
**Offline/a11y:** print CSS; no external; readable at A4; table headers repeat; page numbers.
**Acceptance:** 4–6 pages; no new fact; all formulas/numbers match the main document; print preview checked.
**Effort:** M. **Task:** T18.

#### F12 — First-use glossary links and definition popovers

**Problem:** the glossary is at the end; a student meeting `absorbance` in ch3 must remember to look it up later.
**Behaviour:** the first occurrence of 40–60 high-value terms per chapter links to the ch14 anchor; focus/click opens a small definition with canonical term, one-sentence definition, unit, and “don’t confuse with”; no hover-only.
**Data:** the T01 register; no duplicate definitions.
**Offline/a11y:** native links + small JS popover; `aria-describedby`; Escape closes; print shows plain text.
**Acceptance:** links resolve; popovers keyboard/screen-reader accessible; no broken anchor; print clean.
**Effort:** M. **Task:** T19.

#### F13 — “Why is my answer wrong?” diagnosis map

**Problem:** students see the correct answer but not which step broke; the mistake catalogue is organised by theme, not by symptom.
**Behaviour:** a static triage table: symptom (units wrong, result too precise, CI too narrow, sample outside range, half-life too short) → likely cause → fix → chapter anchor. It complements, not replaces, the 48-row mistake catalogue.
**Data:** existing mistake rows and defect log; no new claims.
**Offline/a11y:** static HTML table; print; no JS needed.
**Acceptance:** every row links to an existing mistake/section; no duplicate contradictory advice; usable at 390.
**Effort:** S. **Task:** T07/T20.

#### F14 — Consent-based persistence and theme memory

**Problem:** marks and theme reset on reload; automatic localStorage would violate the workspace’s consent rule.
**Behaviour:** an off-by-default “Saglabāt šajā pārlūkā” toggle; when enabled, store only the mark map and theme choice; a clear “Dzēst saglabātās atzīmes” action; a one-sentence privacy note; no personal data, no analytics.
**Data:** item IDs and known/unknown; theme string.
**Offline/a11y:** localStorage only after consent; graceful failure in private mode; no write before toggle; reset verified.
**Acceptance:** default reload loses marks; consent reload preserves them; reset clears; no storage when disabled; no personal data.
**Effort:** S. **Task:** T20.

### 4.3 Feature-to-defect traceability

| Feature | Primary defect(s) closed | Secondary benefit |
|---|---|---|
| F01 search | D-06 navigation | terminology lookup, faster revision |
| F02 section navigator | D-06 | reading orientation |
| F03 recall filters | no direct defect; study gap | targeted revision |
| F04 exam mode | study gap | exam confidence, 55% threshold |
| F05 graph trainer | C-04/C-05, D-05 | O4 practice |
| F06 data tables | D-09, accessibility | figure verification |
| F07 residual panel | C-09, calibration limits | R² nuance |
| F08 dilution calculator | C-10, final-volume trap | O5 practice |
| F09 offset simulator | C-18/S18, tool gap | time-origin understanding |
| F10 sig-fig trainer | C-01, C-07 | mixed-operation fluency |
| F11 quick reference | D-07 | exam preparation |
| F12 glossary links | C-19, terminology drift | vocabulary retention |
| F13 diagnosis map | D-11/D-13 | error recovery |
| F14 consent persistence | no direct defect | continuity without privacy loss |

### 4.4 Considered and deferred

| Idea | Why deferred / rejected |
|---|---|
| Spaced repetition scheduler with intervals | High value but requires persistent per-item scheduling, date arithmetic, and privacy consent; it also risks becoming a gamified “streak”. Revisit after F03/F14, as a plain “review unknown” queue first. |
| AI tutor / chat | Conflicts with offline/self-contained, introduces unverifiable answers and cost; not appropriate for a source-critical study document. |
| Analytics / heatmaps / “time on task” | No consent basis, no need, and violates the no-gamification/no-tracking stance. |
| Social sharing / leaderboards | Contradicts the private study-aid purpose and the no-gamification rule. |
| Read-aloud (Web Speech API) | Attractive for accessibility, but voice availability and quality vary offline and by OS; if added, it must be opt-in, labelled “pēc pieejamības”, and never the only path. |
| Full English translation | Out of scope; the glossary already provides English terms. A full translation would double the maintenance and source-defect surface. |

---

## 5. Cross-cutting QA and release gates

### 5.1 Pre-flight (baseline)

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_2
mkdir -p build/baseline
cp Master_2_tema_merijumi_un_grafiki.html build/baseline/master-baseline.html
cp build/shots/final/Master_2_tema.pdf build/baseline/master-baseline.pdf
sha256sum build/baseline/master-baseline.html build/baseline/master-baseline.pdf
```

Record the baseline counts: 16 chapters, 113 recall items, 48 mistakes, 46 tables, 10 figures, 3 instruments, 97 PDF pages, 458,548 bytes. Any later count change must be intentional and reported.

### 5.2 Content correctness gate

- `build/check_terms.py --strict` exits 0.
- `build/check_sigfig_cases.py --check` exits 0.
- `build/verify_numbers.py` output matches `verified.json` and the HTML at the stated precision.
- Every new/changed number has a source or an `ilustratīvs piemērs` label.
- Every new correction is in the change log with location, original, correction, reason, confidence.
- No source PDF or `workspace_skills/` file has changed (`sha256sum` against the frozen manifest).

### 5.3 Explanation-quality gate

- Each P1 chapter has: lead → rule → reason → worked example → typical mistake → retrieval prompt.
- No new paragraph >45 words without a documented exception.
- Every formula has a variable legend with units and a link to the formula sheet/quick reference.
- Every “why” claim is either sourced, labelled `papildinājums`, or explicitly marked `V`.
- The six new explanation snippets in Appendix E have been reviewed by a second reader (or read aloud and diffed).

### 5.4 Design gate

```bash
node workspace_skills/design-taste-frontend/scripts/lint.mjs Master_2_tema_merijumi_un_grafiki.html
node workspace_skills/design-taste-frontend/scripts/inspect.mjs Master_2_tema_merijumi_un_grafiki.html \
  --allow few-pictures,off-centre,still-page
```

Targets after T15–T18:

- 0 FAIL.
- `size-count` warning resolved (≤8 screen sizes).
- `card-rows` warning resolved or reduced to an intentional pattern with a written defence.
- `side-scroll` reduced to ≤5 intentional numeric tables at 390.
- No new “marketing page” tells: no hero CTA, no gradient, no shadow, no decorative icons, no card grid.
- Screenshots at 1440/768/390, light/dark, plus print preview; compare with baseline and record differences.

### 5.5 Accessibility gate

No axe-core is installed and the workspace rules forbid adding a new top-level dependency. Use:

- Chrome/Playwright accessibility tree snapshot for landmarks, headings, names, roles and table semantics.
- Keyboard-only walkthrough: skip link → topbar → TOC → search → first instrument → recall → footer; visible focus at every stop.
- Screen-reader spot check if available (Orca/NVDA/VoiceOver); if not available, say so explicitly.
- Contrast check for every changed token and role colour, both schemes; keep the measured values in the QA log.
- Touch targets ≥44 px for search, filters, instrument buttons and recall controls.
- `prefers-reduced-motion` test; no motion beyond 120–160 ms focus/hover.
- Print: all details open, links not coloured as web-only, page numbers present.

### 5.6 Print gate

- Export the full PDF with all `<details>` open.
- Check page count and inspect: masthead, all 10 figures, formula pages, calibration/half-life/density, mistakes table, change log, appendix E, final page.
- No blank page, no orphan heading, no table header without rows, no caption separated from its figure.
- Running header and page numbers on every page; footer sources present or compact with a pointer to Appendix B.
- Quick-reference pack: 4–6 pages, no clipped table, readable at A4.

### 5.7 Performance and self-containment gate

- Single HTML ≤2 MB with fonts; no external requests; no `@import`; no CDN.
- Search index adds no more than ~300 KB uncompressed; measured search latency <100 ms.
- No layout shift on load; fonts `font-display: swap` or equivalent; no invisible text flash.
- No `localStorage`/`sessionStorage` access before explicit consent; grep and runtime test.
- No runtime dependency on Python/Node; the HTML works from `file://`.

### 5.8 Regression suite (must remain true after every wave)

| Check | Expected |
|---|---|
| Calibration slope/intercept/R² | 0.032165714 / 0.0106 / 0.998933 (reported as 0.0322 / 0.0106) |
| Sample results | 25,9; 9,4; 25,4; 23,5; 30,2*; 24,4 mg/L |
| Q3 mean/s/SEM/CI | 12,70 mL; 0,304; 0,176; ±0,76 mL |
| Dixon Q | 0,909 < 0,941; do not reject at n=3 |
| Half-life Hg-203 | 46,595 d = 1118,3 h = 67 097 min = 4,0258·10⁶ s |
| Hydrolysis | 240/225 s; mean 232,5 s; 220 s key reading reconciled |
| Density | ρ=1,0334 intermediate; reported 1,033 g/mL; w=4,86% |
| Table interpolation | 4,91% |
| Recall | 113 items; 48 in ch15; no visible answers when closed |
| Structural | 1 h1, 16 h2, 16 chapters, 46 tables, 10 figures, 3 instruments |
| External/storage | 0 external URLs; 0 storage before consent |

---

## 6. Definition of Done

### 6.1 P0 release (correctness)

- T01–T06, T08 complete; all D25–D40 verified, logged, and either corrected or marked V.
- Term checker and arithmetic harness green.
- All 48 mistake rows and 113 recall answers still present; no answer leaks.
- Print/PDF re-exported; no regression in the 97-page structure.
- A dated change-log entry names every correction and every preserved source quotation.

### 6.2 P1 release (comprehension)

- T07, T09–T14 complete; long-paragraph and em-dash targets met.
- New n−1, mixed-operation, calibration-model, graph-reading, half-life-offset and solution-flow explanations reviewed.
- Every new recall item closed and verified; every new figure has `<title>/<desc>` and a data alternative where relevant.
- A second reader can follow the six Appendix E passages without the original chapter.

### 6.3 P2 release (design and features)

- T15–T20 complete or explicitly deferred with a written reason.
- Lint 0 FAIL; inspect 0 FAIL with only the documented content allowances; size-count and card-rows addressed.
- ≤5 intentional side-scrolling tables at 390; vessel matrix usable.
- Search and recall workspace pass keyboard, offline, no-answer-leak and no-storage-before-consent tests.
- Quick-reference pack printed and inspected; no blank/orphan page.
- Final report lists verified vs unverified work; no claim of axe/screen-reader/physical-printer QA that was not performed.

---

## 7. Open questions for the lecturer (V register)

These should be added to ch16 D and, where relevant, to a `role--source` note in the chapter.

1. **Accuracy umbrella:** is the course term `kopējā tuvība` or `kopējā precizitāte`? Is `accuracy` accepted as a synonym in exam answers? (T03)
2. **Luminous intensity:** does the course use `gaismas stiprums` or `gaismas intensitāte` for the SI base quantity? (T01/C-14)
3. **Fume hood:** is `tvaika nosūcējs` or `velkmes skapis` the expected term? (T04)
4. **LOD/LOQ:** are LOD and LOQ examinable definitions, or only named criteria? Should the document give formulas? (T02/C-05)
5. **Density reporting:** does the course expect 1,0334 g/mL or 1,033 g/mL for the 103,34 g / 100,0 mL example? (T06/C-10)
6. **Calibration slope:** is the expected reported slope 0,0322 L/mg or 0,03217 L/mg? (T06/C-09)
7. **Q3 outlier:** confirm the expected answer is the three-value mean 12,70 mL with a repeat recommendation, not the two-value 12,53 mL. (S12)
8. **Q5 answers:** confirm the suggested vessel choices are acceptable as `papildinājums`, especially 38 mL with a burette and the 3 mL syringe. (S19)
9. **B-class 0.5%:** confirm this is a course convention, not a manufacturer tolerance, and whether exam answers should ignore the marking on the glass. (S7)
10. **Mora pipette naming:** confirm the course wants `Mora pipete` for the single-mark bulb pipette and `mērpipete` for the graduated type. (S21)
11. **Half-life units:** confirm the exam accepts 2,3·10² s and 220 s as consistent with the graph; clarify whether “diennakts” is ever accepted. (S17/S18)
12. **Absorption/absorbance:** confirm that `absorbance A` is the expected quantity term and `absorbcija` only the process. (S5/T02)

---

## Appendix A — Starter terminology register

This is a seed, not the final 100+ entry register. Every entry needs a source/definition reference before it is enforced.

| Canonical | Forbidden / risky variants | Symbol / unit | Definition (one line) | Contexts where the variant is allowed | Confidence |
|---|---|---|---|---|---|
| absorbance | absorbcija (as quantity) | A, dimensionless | Negative logarithm of transmittance; the measured optical quantity. | “gaismas absorbcija” for the process; source quotes | C |
| gaismas absorbcija | absorbance (as process) | — | Physical process of light attenuation in the sample. | Source quotes | C |
| masa | vielas daudzums (for m) | m, g/kg | Amount of matter in a sample; the balance reads mass. | Source quotes | C |
| vielas daudzums | masa (for n) | n, mol | Amount of substance; proportional to the number of entities. | Source quotes | C |
| molārā koncentrācija | M, CM, cM (as unit) | c, mol/L | Amount of substance per final solution volume. | Source quotes / defect log | C |
| masas koncentrācija | “koncentrācija” when γ is meant | γ, g/L or mg/L | Mass of solute per solution volume. | Generic prose where the type is obvious | H |
| masas daļa | C%, ω (as primary) | w, 1 or % | Mass of solute per mass of solution. | Source quotes | C |
| blīvums | “koncentrācija” | ρ, g/mL or kg/m³ | Mass of solution per volume. | — | C |
| precizitāte | “precīzi trauki” as a quantity | — | Scatter of repeated measurements. | Quoted course phrase once, defined | C |
| pareizība | “ticamība” for trueness | — | Closeness of the mean to the reference value. | Source quotes | H |
| kopējā tuvība | kopējā precizitāte (unmarked) | — | Precision + trueness together (accuracy). | One synonym note in ch14 | H/V |
| atkārtojamība | reproducējamība | — | Same lab, same instrument, short interval. | — | C |
| reproducējamība | atkārtojamība | — | Different lab/instrument/operator. | — | C |
| mērtrauks | mēraparāts (for glassware) | — | Vessel with a calibrated mark/scale and a stated tolerance. | Source quote “mēraparātiem” | C |
| Mora pipete | “Mohr pipette” as the single-mark type | — | Single-mark bulb pipette; not the graduated type. | English glossary note | H |
| mērpipete | Mora pipete (for graduated) | — | Graduated pipette with a scale. | — | C |
| Erlenmeijera kolba | Erlenmeijera / Erlenmeijera (koniskā) mixed | — | Conical flask for mixing/titration. | Source quotes | C |
| tvaika nosūcējs | velkmes skapis (unmarked) | — | Local exhaust enclosure for vapours. | One synonym note | H/V |
| zīmīgie cipari | zīmīgie skaitļi | — | Digits that carry measurement precision. | Source quotes | C |
| zīmes aiz komata | zīmīgie cipari (when places are meant) | — | Digits after the decimal separator. | — | C |
| diena | diennakts (active prose) | d | 24 h. | Source quote | C |
| LOD | LOQ (when detection is meant) | — | Lowest concentration detectable with stated risk. | Source names only | C/H |
| LOQ | LOD (when quantification is meant) | — | Lowest concentration quantifiable with acceptable uncertainty. | Source names only | C/H |
| jutība | “maza koncentrācija” as definition | dA/dc | Slope of the calibration function. | — | C/H |
| selektivitāte | jutība | — | Ability to distinguish analyte from matrix components. | — | C |
| gaismas stiprums | gaismas intensitāte (as SI base quantity) | I_v, cd | Luminous intensity, SI base quantity. | Source quote; confirm V | H/V |

---

## Appendix B — Arithmetic verification cases

Use `decimal.Decimal` for all cases; never binary floats for the reported digits.

| Case | Input | Operation | Expected intermediate | Expected reported | Note |
|---|---|---|---|---|---|
| B01 | 10,05; 150,95 | add | 161,00 | 161,00 g | 2 decimal places |
| B02 | 10,05; 150,95 | wrong ×/÷ hypothetical | 161,0 | 161,0 (4 s.f.) | D25 correction |
| B03 | 3,45; 0,8 | multiply | 2,76 | 3 | 1 s.f. |
| B04 | 0,25; 1,0 | divide | 0,25 | 0,25 mol/L | 2 s.f. |
| B05 | 12,50; 13,05; 12,55 | sum, then ÷3 | 38,10; 12,70 | 12,70 mL | exact 3 |
| B06 | 1,50; 98,00 | multiply | 147,0000 | 147 g/L | 3 s.f. |
| B07 | 1,1145; 0,0127 | error/result | 1,1145; 0,0127 | (1,115 ± 0,013) | 2 s.f. error |
| B08 | 1,1145; 0,019 | error/result | 1,1145; 0,019 | (1,11 ± 0,02) | 1 s.f. error, single rounding |
| B09 | 450 | inspect | ambiguous | 2 s.f. course / 4,5·10² | S10 |
| B10 | 0,845 | calibration inversion | 25,9407 | 25,9 mg/L | 3 s.f. |
| B11 | 0,982 | calibration inversion | 30,1999 | 30,2 mg/L + extrapolation | above 0,975 |
| B12 | 103,34; 100,0 | density | 1,0334 | 1,033 g/mL | 4 s.f.; T06 |
| B13 | 5,02; 103,34 | mass fraction | 0,048578… | 4,86% | 3 s.f. |
| B14 | (1,0334−0,9979)/0,0073 | w from line | 4,8630… | 4,86% / 4,9% | slope 2 s.f. |
| B15 | 46,595 d | unit conversion | 1118,28 h | 1118,3 h | 5 s.f. |
| B16 | 220 s | unit conversion | 3,6667 min | 3,7 min | 2 s.f. |
| B17 | 115; 355; 580 s | Δ halving | 240; 225 | 232,5 → 2,3·10² s | offset model |
| B18 | t0=115; t½=232,5 | halving times | 347,5; 580 | intervals 232,5 | F09 |

---

## Appendix C — QA command sheet

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_2
F=Master_2_tema_merijumi_un_grafiki.html

# Build
python3 build/build_doc.py

# Self-containment and unit hygiene
grep -nE '(src|href)="https?://|@import|url\(https?://|<link[^>]+stylesheet' "$F"   # expect none
grep -nE '\b[0-9,]+ ?(ml|sec|ppm)\b' "$F"                                          # expect none (except quoted)
grep -nE '[0-9]\.[0-9]+ ?(mL|g|mg|mol|L|s)\b' "$F"                                 # review hits

# Structure
grep -c '<html lang="lv"' "$F"
grep -o '<title>[^<]*</title>' "$F"

# Term and arithmetic checkers (to be added by T01/T05)
python3 -I build/check_terms.py "$F" --strict
python3 -I build/check_sigfig_cases.py --check "$F"

# Browser QA
node build/final_check.mjs
node workspace_skills/design-taste-frontend/scripts/lint.mjs "$F"
node workspace_skills/design-taste-frontend/scripts/inspect.mjs "$F" \
  --allow few-pictures,off-centre,still-page

# PDF
pdfinfo build/shots/final/Master_2_tema.pdf | grep Pages
# render/inspect key pages
```

---

## Appendix D — Finding-to-file map

| Finding | File:line | Task |
|---|---|---|
| 161 vs 161.0 | `08_ch8.html:38` | T05 |
| Q4c guard digits | `08_ch8.html:115–116` | T05 |
| absorbcija as quantity | `03_ch3.html:39` | T02 |
| sensitivity definition | `03_ch3.html:65, 106` | T02 |
| LOD/LOQ conflation | `03_ch3.html:72` | T02 |
| n−1 explanation | `07_ch7.html:25` | T09 |
| exact-3 wording | `07_ch7.html:48, 59` | T05/T09 |
| “ceturtā zīme” | `10_ch10.html:85` | T06 |
| slope precision | `10_ch10.html:28` | T06 |
| density 1,0334 vs 1,033 | `12_ch12.html:60–67, 128` | T06 |
| pipette heat cell | `04_ch4.html:23` | T04 |
| Erlenmeyer heat cell | `04_ch4.html:22` | T04 |
| mass definition | `02_ch2.html:16` | T01/T04 |
| luminous intensity | `02_ch2.html:55` | T01/T04 |
| NBSP explanation | `14_ch14.html:135` | T07 |
| “solījums” | `05_ch5.html:65` | T07 |
| “masas/ tilpuma” | `02_ch2.html:107` | T07 |
| accuracy labels | `06_ch6.html:30`, `14_ch14.html:102`, `15_ch15.html:119` | T03 |
| figure caption order | `04_ch4.html` (glassware figure) | T08 |
| type scale / spacing | `style.css` | T15 |
| card rows / masthead | `style.css`, `00_front.html` | T16 |
| table side-scroll | `style.css`, table wrappers | T17 |
| navigation/print | `app.js`, print CSS | T18 |

---

## Appendix E — Ready-to-paste correction copy (Latvian)

Use these as starting points; verify against the source and the current line before pasting.

### E1. Significant figures — replace the 161 sentence

> Ja summai kļūdaini piemērotu reizināšanas noteikumu, rezultāts būtu **161,0** (četri zīmīgie cipari), nevis 161. Pareizais summēšanas rezultāts ir **161,00**, jo abi saskaitāmie doti līdz 0,01 g: saskaitīšanā skaita zīmes aiz komata, nevis kopējo zīmīgo ciparu skaitu.

### E2. Exact number 3 — replace the decimal-place rationale

> **3 ir precīzs skaits**, tāpēc tas neierobežo zīmīgo ciparu skaitu. Summa 38,10 mL ir ar divām zīmēm aiz komata; dalot ar precīzo 3, iegūst 12,70 mL, t.i., četrus zīmīgos ciparus. Precizitāti šeit nosaka summas decimālzīmes un dalīšanas zīmīgo ciparu noteikums, nevis tas, ka 3 ir “precīzs”.

### E3. Why n − 1 — new box

> **Kāpēc dala ar n − 1?** Novirzes no izlases vidējā vienmēr summējas uz nulli: ja zināt n − 1 novirzes, pēdējā ir noteikta. Tāpēc brīvo noviržu skaits ir n − 1, nevis n. Dalījums ar n sistemātiski novērtē dispersiju par zemu, jo īpaši mazām sērijām; dalījums ar n − 1 ir **nenobīdīts** dispersijas novērtētājs. Ar trim mērījumiem tas ir īpaši svarīgi.

### E4. Sensitivity and LOD — criteria table copy

> **Jutība** ir kalibrēšanas taisnes slīpums: jo lielāks signāla pieaugums uz koncentrācijas vienību, jo jutīgāka metode. **LOD** ir mazākā koncentrācija, kurā vielas klātbūtni var noteikt ar norādītu risku; **LOQ** ir mazākā koncentrācija, kurā to var kvantificēt ar pieņemamu nenoteiktību. Avots abus kritērijus nosauc, bet nedod formulas; šajā dokumentā skaitliskās LOD/LOQ vērtības nav izgudrotas.

### E5. Density reporting — replace the contradiction

> Starpposmos blīvums ir **1,0334 g/mL**. Tā kā tilpums 100,0 mL ir dots ar četriem zīmīgajiem cipariem, atbildē blīvumu raksta **1,033 g/mL**; 1,0334 paliek starpvērtība, nevis gala atbilde. Masas daļa no tiešā aprēķina ir 4,86 %.

### E6. Absorbance — replace the contradictory sentence

> **Absorbance A** ir bezdimensiju mērītais lielums. Vārds **absorbcija** paliek procesa nosaukumam (“gaismas absorbcija”), nevis skaitlim. Tāpēc tabulu virsrakstos un instrumenta laukos lietojam “Absorbance A”, nevis “Absorbcija A”.

### E7. Calibration slope — reporting note

> Pilnajā aprēķinā lietotā taisne ir *A* = 0,0321657·ρ + 0,0106. Atbildē un grafikā slīpumu raksta ar trim zīmīgajiem cipariem: **0,0322 L/mg**; krustpunkts paliek 0,0106. Starpposmos ar pilnu precizitāti aprēķina, bet gala atbildē noapaļo vienu reizi.

### E8. NBSP — replace the typographic explanation

> Mērvienību simbolu no skaitļa atdala ar **neplīstošu atstarpi** (`&nbsp;`), lai skaitlis un mērvienība nekad netiktu atdalīti rindas beigās. Tā nav “saīsināta” atstarpe; tās platums ir parasta atstarpe, bet rinda tajā neplīst.

---

## Appendix F — Success metrics after the plan

| Metric | Baseline | Target |
|---|---:|---:|
| Active banned terminology forms | unknown (17 raw hits incl. quotes) | 0 |
| Arithmetic/term checker failures | none yet (checkers to be built) | 0 |
| Long paragraphs ≥45 words | 103 | ≤40 (or documented exceptions) |
| Sentences >35 words | 41 | ≤20 |
| Em dashes | 58 | ≤20 active |
| Screen font sizes | 15 | ≤8 |
| Side-scrolling tables at 390 | 23 hinted / 9 flagged | ≤5 intentional |
| Inspect FAIL/WARN | 0/5 | 0/≤3 (content allowances only) |
| Lint FAIL | 0 | 0 |
| PDF pages | 97 | ≤97, no blank/orphan page |
| Quick-reference pages | 0 | 4–6 |
| Search latency | n/a | <100 ms |
| Recall items | 113 | ≥113, no leaks |
| Tables audited | not yet | 46/46 |
| Figures with data alternative | 0 | 10/10 where applicable |
| Accessibility audit | manual only | manual + accessibility tree; axe only if available without new dependency |

---

## Appendix G — What not to do

- Do not use a source PDF as a canvas for “fixing” a quote; keep the original wording in the change log and in `<q data-quote>`.
- Do not turn the quick-reference into a new, unreviewed fact source; generate it from verified content.
- Do not add a “mastery” score, XP, streaks, confetti, badges, or a leaderboard. Progress is a plain state.
- Do not store marks, search queries, or theme choices without explicit consent; do not add analytics.
- Do not add a CDN, external font, icon pack, chart library, or runtime fetch to solve a design problem.
- Do not claim axe, screen-reader, physical-printer, or cross-browser QA that was not actually performed.
- Do not “average” conflicting skill advice; the prompt’s design contract wins on design, `AGENTS.md` wins on workspace rules.
- Do not let a redesign remove the semantic roles, the defect log, the source lines, or the closed-answer discipline. Those are the document’s spine.

---

*End of plan. The first executable step is Wave 0: freeze the baseline, then T01 (terminology register) and T05 (arithmetic harness) in parallel; nothing else should change until those two gates are green.*
