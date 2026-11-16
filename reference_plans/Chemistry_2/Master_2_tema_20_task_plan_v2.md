# Master 2. tēma — Deep Inspection & 20-Task Plan **v2**

| Field | Value |
|---|---|
| **Deliverable under revision** | `/home/robertsrff/Chemistry_Med/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html` |
| **Build sources** | `build/sections/*.html` · `build/style.css` · `build/app.js` · `build/figures/*.svg` · `build/build_doc.py` |
| **Baseline inspected** | 2026-11-01 19:11 build — **1 296 228 bytes**, 7 043 lines, SHA-256 `2c89f6d6…c4c5790` |
| **Printed baseline** | **117 A4 pages**, 2 595 906 bytes (fresh headless render, 2026-11-01) |
| **Plan generation date** | 2026-11-01 (v2) |
| **Supersedes** | `Master_2_tema_20_task_improvement_plan.md` (v1, tasks T01–T20). v1 is **closed but not verified**; v2 begins by auditing its closure claims (§0.2, N01). |
| **Deliverable language** | Latvian (`lang="lv"`), decimal comma, NBSP before units |
| **Plan language** | English, quoting Latvian strings verbatim |
| **Authority order** | `PROMPT_Master_html_2_tema.md` §6 (design) → `AGENTS.md` (workspace rules) → individual skills → this plan |

> **Read this file with** `AGENTS.md` (§5 source-defect register S1–S23 is canonical) and `PROMPT_Master_html_2_tema.md` (§6 design contract, §7 fact base). Where this plan and prompt §6 disagree, the prompt wins on design; where this plan and `AGENTS.md` disagree, `AGENTS.md` wins on workspace rules. This plan **adds** an evidence layer measured on 2026-11-01, and it deliberately re-opens items that v1 marked done — because the artifact and the change log no longer agree with each other.

---

## 0. How to read this file

1. **§1 is the evidence.** Every finding carries an ID (`X-NN`), a location, a verbatim quote or a measured number, an impact, and a confidence (`C` certain / `H` high / `V` verify with lecturer). If a claim has no evidence line, it is not a finding — it is an opinion, and it is labelled as such in §8.
2. **§2 is the map.** Waves, dependencies, file ownership, and the ten invariants that apply to *every* task.
3. **§3 is the backlog.** 20 tasks (`N01`–`N20`). Each has a metadata table, context with evidence, a falsifiable Definition of Done, exactly **3 substeps**, and **3 subtasks with 3 substeps each** — **12 numbered steps per task, 240 in total**, plus a DoD, an acceptance command set and a rollback for each.
4. **§4–§6 are the programmes** that several tasks draw from: the feature catalogue (add-ons), the SVG programme, and the design/retexture contract v2.
5. **§7–§9 are the gates.** Commands to run, thresholds to hit, risks to avoid, and the release checklist.
6. **Appendices** hold ready-to-paste Latvian copy, lecturer questions, and the finding→task matrix.

**Non-negotiable handling rules** (from `AGENTS.md`): never edit the five source PDFs; never edit `workspace_skills/`; scratch work goes to the session scratchpad (this inspection used `~/.cache/chem2-plan/`); no git repo, no new runtime dependency, no CDN, no analytics, no persistence without consent, no gamification.

---

## 0.1 Executive verdict

The document is **not a draft anymore**. It is a 33 000-word, 117-page, offline, self-contained textbook with 75 tables, 12 data figures, 5 working instruments, 127 closed recall prompts, full-text search, a recall workspace, an exam mode, and a source-defect register with confidence labels. Most of what v1 proposed was built, and the build is **byte-for-byte reproducible** (verified: rebuilding from `build/` reproduces SHA-256 `2c89f6d6…`).

The problem is no longer *missing work*. It is **drift**: the artifact kept growing while its own audit trail, its cross-references, its responsive rules and its instruments' guard rails stopped keeping up. Measured today:

- the change log says **52 tables**; there are **75**;
- it says **10 figures**; there are **12** figures and **21** SVGs;
- it says **105 section ids**; there are **121** `<h3>`;
- it says **719 search blocks**; there are **815**;
- it says *«aktīvajā prozā vairs nav em svītru (0)»*; prose contains **96** em dashes (110 in markup, 131 raw);
- `build/concepts.json` still says **113 recall items**; there are **127**;
- the masthead says *«Pārbaudīts: 2026. gada 31. oktobrī»* while the change log has **2026-11-01** entries;
- chapter 15 opens with *«48 slēgti jautājumi»* and its own counter one screen later says *«no 127»*;
- four `<ol class="steps">` lists render **double ordinals** (`1. 1. Nosakiet mērķi.`) — visible in the rendered PDF and on screen;
- on a 390 px phone the top bar becomes a **column of three full-width buttons** with a shrunken search field;
- at ≤900 px **every figure is forced to `min-width: 820px`**, i.e. sideways scrolling for all data graphics;
- the calibration instrument accepts `A = 0` and returns **−0,330 mg/L**, and `A = 999` and returns **31 057 mg/L** — the document teaches that 0,982 is already extrapolation, but the tool does not warn;
- the printed page 62 is ~40 % empty and page 117 is ~60 % empty; the running header reads **«RSU · 2026»**, implying institutional provenance the file does not have.

**Verdict: 3.9 / 5.** Excellent content and engineering; the trust surface (self-audit, cross-references, guard rails, print pagination) has fallen behind the content. v2 is therefore weighted **60 % integrity, 25 % design/mobile/print, 15 % new capability** — not another feature wave.

**The five moves that matter most**

1. **Make the document's self-description executable** (N01): generate every count, date, cross-reference and closure claim from the artifact; fail the build on drift.
2. **Fix the visible contradictions** (N02): double ordinals, 48-vs-127, stale "Pārbaudīts" date, "0 em dashes".
3. **Give the instruments the document's own lessons** (N04, N18): range guards, unit defaults, no negative concentrations, no silent extrapolation.
4. **Repair narrow screens and print** (N14, N13): one top-bar row, figures that scale instead of scroll, no half-empty pages, a printed TOC with page numbers.
5. **Then restyle and extend** (N10–N12, N15–N17, N19–N20): de-numeralise the masthead, unify texture, and grow the SVG library with figures that carry data.

---

## 0.2 What changed since v1 (and what v1 got wrong)

v1 defined T01–T20 and a Feature catalogue F01–F14. The change log of 2026-11-01 marks all of them shipped:

| v1 task | Claimed ship evidence in the document | v2 verdict |
|---|---|---|
| T01 terminology register | `build/terminology.json`, `check_terms.py`, 0 violations | **Closed.** Harness runs clean today. |
| T02 absorbance/LOD cluster | ch3 policy block, D-entries | **Closed.** Verified in text. |
| T03 precision/trueness | ch6 table, glossary | **Closed**, one label still varies (see B-03). |
| T04 vessel terminology | ch4 matrix, honest "avotā nav" cells | **Closed**, but the matrix has an alignment defect (D-06). |
| T05 sig-fig examples | `check_sigfig_cases.py` → all ok | **Closed.** |
| T06 reporting precision | ch10/ch12, `verified.json` | **Closed.** |
| T07 line edit | claims "0 em dashes active" | **Re-opened.** 96 prose em dashes (B-01). |
| T08 table/figure audit | claims "52 tables, 10 figures" | **Re-opened.** Counts stale (A-01). |
| T09 degrees of freedom | ch7 residual explanation | **Closed**, add one worked counterfactual (C-02). |
| T10 mixed sig-fig tree | ch8 decision tree | **Closed**, double ordinals (A-02). |
| T11 calibration limits | ch10 "Ko taisne nepierāda" | **Closed**, tool contradicts it (I-01). |
| T12 graph reading | 6-step method + Tool D | **Closed**, double ordinals (A-02). |
| T13 half-life origin | ch11 offset model + Tool C | **Closed**, tool default unit wrong (I-02). |
| T14 solution flow | ch12 five-step flow + Tool E | **Closed**, but renders `1. 1.` (A-02). |
| T15 type tokens | 8 roles + print pt set | **Closed.** Verified in CSS. |
| T16 de-card + masthead | "CTA row deleted, h1 56 px" | **Partial.** CTA is gone, but the `01–05` numeral grid violates prompt §6.2 «no `01 / 02`» (D-02). |
| T17 mobile tables | 57 stacked | **Partial.** 65/75 stacked; 10 remain; figures still 820 px (F-02). |
| T18 section nav + print quickref | 105 h3 ids, TOC, quickref | **Partial.** 121 h3 now; print TOC has no page numbers (G-02). |
| T19 search + glossary links | 719 blocks, 65 terms | **Partial.** 815 blocks; index still contains answer text (I-03). |
| T20 recall workspace | 148 concepts, 127 items | **Partial.** `concepts.json` stale at 113; lead contradicts counter (A-03). |

**The methodological lesson of v1–v2**: any *human-written* count in a generated document will drift within one working session. The fix is not "be careful" — it is to remove the human number from the source and generate it (N01).

---

## 0.3 Baseline snapshot (all measured, 2026-11-01)

| Metric | Value | How measured |
|---|---:|---|
| HTML size / lines | 1 296 228 B / 7 043 | `wc` |
| Visible words | 32 796 | headless `innerText.split` |
| Words incl. UI strings & nav | 40 522 | text extraction |
| Desktop document height (1440 px) | 126 396 px ≈ **140 screens** | `scrollHeight` |
| Print pages | **117** A4 | `google-chrome --print-to-pdf` + `pdfinfo` |
| Chapters | 16 (`#ch-1` … `#ch-16`) | DOM |
| `<h2>` / `<h3>` / `<h4>` | 17 / 121 / 5 | DOM; **0 skipped heading levels** |
| `<h3>` with generated id | 107 | build-time ids; 14 widget headings skipped |
| Tables | 75, **75/75 with `<caption>`** | DOM |
| Stacked tables (`table--stack`) | 65 (1 876 `data-label`) | DOM |
| Figures / inline SVGs | 12 `<figure>` / 21 `<svg>` | DOM |
| `<details>` | 146, **0 open by default** | DOM |
| Recall items | **127** (2 + 7 + 8 + 9 + 5 + 7 + 6 + 13 + 6 + 5 + 5 + 6 + 0 + 0 + **48** + 0) | per-chapter parse |
| Glossary entries | 65 | `id="glossary-*"` |
| Search index blocks | 815 (196 item, 344 body, 129 heading, 69 table, 65 term, 12 figure) | embedded JSON parse |
| Concepts inventory | 121/121 mapped — **but file says 113 recall items (stale)** | `build/concepts.json` |
| External URLs / runtime fetch | **0 / 0** | grep |
| `localStorage` | only `mch2-t20-v1`, gated by explicit consent | code read |
| Inline `style=` attributes | **0** | DOM |
| Inputs/selects without label | **0** | DOM |
| SVGs without `<title>` | **0** | DOM |
| Duplicate ids / broken anchors | **0 / 0** | parse |
| Console errors / page errors | **0 / 0** | Playwright |
| Lint (`lint.mjs`) | **0 FAIL, 1 WARN** — 131 em dashes | run |
| Inspect (`inspect.mjs`, last run) | 0 FAIL, 5 WARN (type sizes, no video, side-scroll) | `build/inspect3.log` |
| Build reproducibility | **identical** SHA-256 after rebuild | scratch rebuild |
| Print header / footer | `Mērīšana… · Medicīniskā ķīmija, 2. tēma` / `RSU · 2026` / `Lpp. n / 117` | PDF pages |
| Fonts | `MCh Text` = Noto Sans subset, 4 faces, 8–8,7 KB each, base64 | `build_doc.py` |

**Measured at 390 px:** top bar overflows into 3 stacked buttons; 11 `.figure-scroll` regions force `min-width: 820px`; 2 table rows and 1 figure exceed the viewport; 10 tables are not stacked.

**Measured in print:** p62 ≈ 40 % blank, p117 ≈ 60 % blank (quickref checklist alone on a page); no printed page-numbered TOC; no colophon page.

---

## 0.4 Verification honesty statement

**Performed in this inspection**

- headless Chromium 156 render at 1440×1000 and 390×844 (Playwright, `/usr/bin/google-chrome`);
- full-page print render to PDF (117 pages) and page-image inspection of pp. 1, 2, 33, 62, 96, 117;
- `lint.mjs` on the deliverable;
- DOM measurement scripts (counts, overflow, labels, captions, heading order);
- runtime probes of tools A–E, search, and exam mode (input edge cases: empty, text, 0, negative, 1e9, out-of-range);
- `python3 -I build/check_terms.py … --report` → 0 violations;
- `python3 -I build/check_sigfig_cases.py --check` → all ok;
- `python3 -I build/check_calibration.py --residuals` → all ok;
- a scratch rebuild from `build/` → byte-identical output;
- `pdfinfo` page count and `pdftoppm` page rasters.

**Not performed (do not claim it)**

- axe-core / automated WCAG audit (not installed; adding it would be a new dependency);
- screen-reader pass (NVDA/JAWS/VoiceOver);
- cross-browser (Firefox, Safari) — Chromium only;
- physical printer output, ink coverage, braille;
- mobile *device* testing (emulated viewport only);
- any lecturer confirmation of the `V`-confidence items.

Every claim in §1 is one of: measured here, read from the artifact, or quoted from a source PDF. Anything else is marked *opinion* and lives in §8.

---

# 1. Deep inspection — evidence register

Each finding: **ID · location · what was observed (verbatim or measured) · impact · confidence**.
Confidence: **C** = certain (checkable here), **H** = high (strong inference), **V** = needs the lecturer or a browser/device we do not have.

## 1.1 Method

| Step | Tool | What it produced |
|---|---|---|
| Structure | Python regex parse of the built HTML | chapter/h3/table/figure/details/recall counts, id uniqueness, anchor resolution, heading order |
| Rendering | Playwright + `/usr/bin/google-chrome` 156, 1440×1000 and 390×844 | screenshots, `scrollHeight`, overflow detection, computed styles |
| Print | `--print-to-pdf`, `pdfinfo`, `pdftoppm -r 70` | 117 pages, page rasters, blank-area estimate |
| Anti-slop | `workspace_skills/design-taste-frontend/scripts/lint.mjs` | 0 FAIL / 1 WARN |
| Behaviour | runtime probes of tools A–E, search, exam | input edge cases, result strings |
| Facts | `build/check_terms.py`, `check_sigfig_cases.py`, `check_calibration.py`, `verify_numbers.py` | 0 violations, all displayed values match |
| Build | scratch copy + `python3 -I build/build_doc.py` | byte-identical output |

## 1.2 A — Self-audit, cross-reference and provenance drift *(the dominant risk)*

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **A-01** | 16. pielikums C (change log), T08 entry | *«52 tabulas, visas ar parakstu un `scope`»* — artifact has **75** tables; *«10 attēli»* — artifact has **12** figures / 21 SVGs; T18 *«105 h3 id»* — **121**; T19 *«719 bloki»* — **815**; T17 *«57 tabulas kraujamas»* — **65** | The document's core trust claim ("we audited everything") is false in its own text. A reader who counts loses confidence in every other number. | C |
| **A-02** | ch8 (decision tree, mistake ladder), ch9 (six-step reading), ch12 (five-step flow) | Four `<ol class="steps">` lists also start each `<li>` with a manual ordinal, so the browser prints **both**: rendered `1. 1. Nosakiet mērķi.`, `2. 2. Pagatavojiet šķīdumu…`, … (19 items total; visible on PDF p.* and in the 1440 px render) | The most procedural, most examinable content looks broken; it also contradicts the design contract's «Real `<ol>` for real steps». | C |
| **A-03** | ch15 lead vs workspace counter | Lead: *«48 slēgti jautājumi ar atbildēm.»* Counter one screen later: *«Atzīmēti 0 no 127»* | Two different totals in one screen; the reader cannot tell whether the workspace is the chapter or the whole document. | C |
| **A-04** | masthead; 99_footer | *«Pārbaudīts: 2026. gada 31. oktobrī»* (masthead) and *«Pārbaudīts: 2026-10-31»* (footer, p117) while the change log contains **2026-11-01** entries (T06–T20, F01–F14) | A verification date earlier than the verified changes is a credibility bug, not a typo. | C |
| **A-05** | `build/concepts.json` | `"recall_items": 113`; artifact has **127** (`inventory/covered/total: 121`) | Concept-coverage claims in the change log are computed from a stale file; any future coverage report is wrong at the source. | C |
| **A-06** | change log T07 | *«aktīvajā prozā vairs nav em svītru (0)»* — measured: **96** em dashes in visible text (110 in markup excluding `<script>`/`<style>`, 131 raw, `lint.mjs` warns) | A false "zero" claim inside the same paragraph that talks about honesty. | C |
| **A-07** | `98_quickref.html` | The print-only quick reference numbers its sections **1.–8.** inside a document whose chapters are also 1.–13.; the last section is *«8. Eksāmena kontrolsaraksts (1.–13. nodaļa)»*, which collides with chapter 8 (*Zīmīgie cipari*) in any cross-reference | Cross-references become ambiguous exactly where they must be precise. | H |
| **A-08** | ch16 B (source map) | Rows for 2B Q2 and 2B Q3 say the key has *«Nē»* (no model answer) — correct — but the same chapter's E section presents "instrument verification vectors" that look like answers to the same questions without that caveat in the table | A reader can mistake a verification vector for an official key. | H |
| **A-09** | `build/` | Stale by-products survive next to live sources: `verified_prev.json`, `inspect{,2,3}/`, `lint.log`, `_test.woff2`, `_test2.woff2`, `__pycache__/`, 41 MB total for a 1,3 MB artifact | "Which file is authoritative?" is unanswerable from the folder; every future audit re-reads the wrong one (this inspection had to check mtimes). | C |

## 1.3 B — Terminology and language

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **B-01** | whole document | 96 prose em dashes survive; many are *legitimate* (formula labels `(20,10 + 20,24) / 2 — Vidējais…`, table placeholders `—`, step titles `1. solis — …`), but a large share are rhetorical (*«kļūdai un pārbaudītajam rezultātam — tā pati josla»*, *«trešo vairs nevar brīvi izvēlēties — tā ir noteikta»*) | Em-dash habit is the single most recognisable generated-prose tell; the legitimate uses must be separated from the rhetorical ones, not blanket-removed. | C |
| **B-02** | post-T01 vocabulary | New coinages were added *after* the terminology register was frozen and are **not in it**: *lēmumu plūsma*, *atceres darba telpa*, *modeļa karte*, *signāla ceļš*, *sargcipari*, *kāpnes*, *rīks*, *saīsne*, *kontrolsaraksts* | A register that covers the sources but not the document's own metalanguage cannot prevent drift; students meet 9 undefined metaphors. | C |
| **B-03** | ch6 table vs ch14 glossary vs ch15 | Three labels for one concept still coexist in different places: *«Kopējā tuvība (accuracy)»* (ch6), *«kopējā precizitāte; tuvība»* (ch14), *«Kopējā precizitāte»* (ch15/quiz) | The reader is asked to believe these are the same quantity without being told; `AGENTS.md` S21 flags exactly this class. | H |
| **B-04** | glossary, ch3, ch6, ch10 | English equivalents appear in running text and in the glossary (`absorbance`, `accuracy`, `precision`, `trueness`, `LOD`, `LOQ`, `spike`, `recovery`) with **no `lang="en"`** anywhere except `<html lang="lv">` (measured: `langAttrs: 1`) | Screen readers pronounce English as Latvian; also a small but real WCAG 3.1.2 issue. | C |
| **B-05** | top bar | The primary study affordance is labelled **«Saīsne»** (abbreviation) with `aria-pressed`; nothing says it opens the exam quick-reference sheet | First-time users do not press it; the most useful revision artefact is hidden behind an opaque word. | H |
| **B-06** | units across text, figures, tools | Mixed micro sign usage (`µ` U+00B5 vs `μ` U+03BC), and `mg/100 g` vs `mg/100g` both appear; `build_doc.py`'s NBSP list contains both spellings | Copy-paste into reports yields inconsistent strings; the NBSP pass treats them as different units. | C |
| **B-07** | quickref, exam items | `M` appears both as the unit mol/L and as molar mass in adjacent sentences, in a document that elsewhere bans exactly this ambiguity (S21) | The reader must disambiguate from context in the one place designed for speed. | H |

## 1.4 C — Explanation, structure and study efficacy

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **C-01** | all chapters | 121 `<h3>` sections across 33 000 words with **no prerequisite signalling**: a reader landing on *«Atlikumi: vai taisne der datiem»* is not told that residuals require ch8's rounding rule and ch9's axis grammar | Skipping around (which the sidebar invites) drops the reader into undefined terms. | H |
| **C-02** | ch7 | The `n − 1` explanation is now correct and has a residual-sum demo, but there is **no numeric counterfactual shown side by side** (`s` with n vs n−1 for the same three titres) | The concept that most often fails in exams is asserted, not *shown*; a 2-row table would close it. | H |
| **C-03** | tools A–E | Five instruments share a visual shell but not an explanatory shell: each prints input → intermediate → answer, yet none offers a one-click *«kāpēc šī formula?»* that reuses the chapter's rule text | The tools can be driven mechanically, which is the opposite of the document's stated pedagogy. | H |
| **C-04** | 12 figures | `.figure-data` (data-table alternative) exists for the plots, but the vessel plate and the scheme figures have no textual equivalent beyond the caption | Figure-dependent readers lose content (WCAG 1.1.1 is satisfied by `<desc>`, but the *data* is not reachable). | H |
| **C-05** | reading experience | 140 screens with a sidebar that shows `n/16` and the active section. There is **no reading-position or "you are here in this chapter"** affordance past the section list, and no way to collapse chapters | Long-form fatigue with no recovery path except the search box. | H |
| **C-06** | `build/concepts.json` | 121 concepts / 148 tags exist as data but are **never rendered as a map**; they surface only as workspace filters | The strongest structural asset (a real dependency graph) is invisible to the student. | H |
| **C-07** | ch15 exam mode | Exam mode draws 20/30/40 stratified questions and prints an answer sheet, but finishing gives **no diagnosis** (no "your errors cluster in ch10 and ch12 → reread §10.4") | The highest-value teaching moment (post-test diagnosis) is missing from the most app-like feature. | H |
| **C-08** | ch1, O1–O5 | Five transfer tasks exist. There is **no spaced-review schedule** and no interleaved mixed set beyond chapter 15's H group | Retention is the actual exam goal; the document stops at first-pass practice. | H |
| **C-09** | prose | Metaphor drift: *ceļš*, *karte*, *plūsma*, *kāpnes*, *telpa*, *rīks* are used as structural metaphors in different chapters with different senses | Each metaphor is readable once; together they make the document feel written by five people. | H |

## 1.5 D — Design, tells and retexture

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **D-01** | masthead | Five outcomes rendered as a 2-column grid with oversized accent numerals **`01 02 03 04 05`** | Direct violation of prompt §6.2: *«Numbering: plain numerals… no `01 / 02`, no «Solis 02», no counters styled as ornament»*. It is also the "numbered feature grid" pattern `tells.md` flags. | C |
| **D-02** | masthead | Meta row *«Avoti: 5 kursa PDF · Pārbaudīts: 2026. gada 31. oktobrī · Valoda: latviešu»* plus a quiet *«Sākt ar 1. nodaļu →»* | Decorative metadata strip (the "status badges" tell in prose form) sitting where a document title block belongs. It also carries A-04's stale date. | C |
| **D-03** | masthead | `--text-display: clamp(36px, 4vw, 56px)` with tight tracking, two-line break forced by `<span class="nowrap">` | On a 1440×1000 first screen the title consumes ~30 % of the viewport above the fold and reads as a landing hero, not a textbook title page. | H |
| **D-04** | global | Accent magenta `#A61E4D` is used for: links, glossary links, chapter numbers, role labels, primary buttons, focus ring, active TOC marker, tool result emphasis, consent checkbox | "One accent" is satisfied literally but not functionally: when everything is accented, nothing is. Needs a two-tier system (accent for interaction; accent *tint* for structure). | H |
| **D-05** | CSS | 6 `box-shadow` declarations, of which 3 are function-bearing (popover, dialog, sticky bar) and 3 are decorative panels | Prompt §6.2 bans elevation-by-shadow; the exceptions need to be explicit and few. | C |
| **D-06** | ch4 vessel matrix | Cells in the *«Kļūdas pamats»* / *«Graduācija»* columns render ragged/centred while neighbours are flush left (visible at 1440 px) | A comparison matrix whose columns do not share an alignment grid loses its scanning advantage — the whole point of the table. | C |
| **D-07** | role blocks | 4 variants (Noteikums / Biežākā kļūda / Pārbaudīts / Piezīme avotam) appear 40+ times; the legend explains them once in ch1 | On several screens two or three stack, which prompt §6.2 caps at two visible per screen height. | H |
| **D-08** | figures | 12 data figures + 9 vessel icons all use the **same** 1 px stroke, the same ink, and no scale hierarchy between "measured data" and "schematic icon" | A reader cannot tell at a glance which drawings are to be *read* (graphs) and which are to be *recognised* (glassware). | H |
| **D-09** | `98_quickref.html` | The 8-section exam sheet is a **hand-maintained duplicate** of formulas and rules from ch2/7/8/10/11/12 (print-only) | Duplicated facts diverge silently; the next edit to ch8 will not reach the quickref. | C |
| **D-10** | PDF header | Running head right side reads **«RSU · 2026»** | Implies the file is issued by RSU. It is a student study aid derived from departmental handouts (`AGENTS.md` §9). Attribution must be accurate. | C |

## 1.6 E — Interaction and motion

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **E-01** | tools | No out-of-range state: the calibration tool prints a result for `A = 0` and `A = 999` with identical confidence (see I-01) | Silence reads as approval. | C |
| **E-02** | glossary popover | Focus is moved into the popover, Esc closes, focus returns (code paths present) — but there is no visible cue on the *trigger* while the popover is open | Keyboard users can lose the relationship between trigger and panel. | H |
| **E-03** | search | 815 blocks, diacritic folding works (`skidums` → 18 results, same as `šķīdums`), but results have no **type facet** (all types mixed) and no "in this chapter" filter | In a 117-page document the search result list is a second navigation problem. | H |
| **E-04** | theme toggle | Theme choice is persisted only after consent; without consent a reload resets it — but the stored theme is **read** unconditionally on load (`app.js` line 8) | Inconsistent consent semantics: read without consent, write only with it. | C |
| **E-05** | print/quickref | `quickrefToggle` controls a section marked `print-only` | A control whose target is invisible in print but visible on screen is a category error; users cannot predict what "Saīsne" will do. | H |

## 1.7 F — Responsive, touch and accessibility

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **F-01** | `.topbar` at ≤720 px | Flex row with `.topbar__actions { flex-wrap: wrap }`; at 390 px the three buttons stack into a 3-row column (~180 px tall) while the search input collapses to ~140 px at the left edge (screenshot `j-top-390.png`) | The first screen on a phone is a broken control cluster before any content; search — the main mobile affordance — is the smallest element. | C |
| **F-02** | `.figure-scroll__inner` | `@media (max-width: 900px) { .figure-scroll__inner { min-width: 820px } }` → 11 figure regions scroll sideways at 390 px by design | Contradicts `AGENTS.md` §"Stop forcing phones to read sideways" and the design contract's "figures may widen beyond the column" (widen ≠ force horizontal scroll). Data graphics become unreadable without two-handed panning. | C |
| **F-03** | tables | 65/75 stack; the 10 that do not are 7 `table--pin` + 3 compact. At 390 px the pinned ones overflow (measured: `TR right=489/518`) | Intentional for true matrices, but the three compact ones (formula list, base units, vessel use) are exactly the tables a student reads on a phone before an exam. | H |
| **F-04** | controls | Buttons/inputs are ≥44 px (measured `min-height: 44px`), focus-visible styles exist, skip link exists | Good — record as a strength, do not regress. | C |
| **F-05** | tables | `scope="row"` on 7 cells only, across 75 tables with hundreds of row headers | Screen-reader row association is weak in the matrices that need it most. | H |
| **F-06** | navigation | Sidebar `n/16` and active section exist, but there is no "back to top of chapter" other than the global «Uz sākumu» | On a 9 000-px chapter, returning to the chapter heading costs a long scroll. | H |

## 1.8 G — Print edition

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **G-01** | p62 | ≈40 % of the page blank after *«Atlikumi: vai taisne der datiem»* (break rules push the next block) | At 117 pages, blank halves are ~3–4 wasted pages and look like a rendering fault. | C |
| **G-02** | p117 | The exam checklist occupies the top ~35 % of the last page; ~60 % blank | The final impression of a 117-page reference is an empty page. | C |
| **G-03** | whole PDF | **No printed table of contents with page numbers**; the screen TOC has no page numbers and the print TOC is absent | A 117-page print artefact without a page-numbered TOC is not usable as a reference. | C |
| **G-04** | whole PDF | No cover, no colophon (edition, date, scope, what it is *not*, how to verify numbers) | Provenance lives in the HTML `<title>` and a running head; print loses it. | C |
| **G-05** | print pipeline | `beforeprint` opens all 146 `<details>`, so every recall answer prints | Intentional for a study edition, but it inflates pagination and hides the "test yourself" affordance in print. Needs an explicit, labelled decision (study edition vs. question edition). | H |
| **G-06** | running head | `RSU · 2026` (see D-10) | Attribution risk. | C |

## 1.9 H — SVG and data graphics

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **H-01** | `figures/burette-readings.svg` | The burette is drawn with a few ticks and a stopcock; **no numbered graduations, no estimated-digit zone, no 0,00/5,80/19,30 markers on the drawing itself** | The figure that teaches the hardest practical skill (reading to ±0,05 mL) does not show the scale the text describes. | C |
| **H-02** | `figures/glassware.html` | 9 vessels, uniform 1 px stroke, no liquid, no TD/Ex marks, no tolerance text, no scale numbering; Erlenmeyer outline has a spout-like break | Prompt §6.3 fig. 4 asks for aligned baselines and proportional heights — true — but the drawings cannot teach "which mark is calibrated" without the matrix. | H |
| **H-03** | 12 `<figcaption>`s | Captions carry 2–4 lines of provenance (*«Avots: … zīmējumi veidoti šim dokumentam. … papildinājums.»*) inside the caption element | Caption = what the figure shows; provenance = source line. Mixed, it reads as defensive boilerplate on every figure. | H |
| **H-04** | all SVGs | `<title>`+`<desc>` present on 21/21 (strength), but `<desc>` is often a restatement of the title, not a description of the *data* | A screen-reader user gets "Askorbīnskābes kalibrēšanas grafiks" twice and no numbers. | H |
| **H-05** | SVG typography | SVG text is sized in user units and scales with the `viewBox`; at 390 px (with the 820 px min-width removed) labels would fall below 9 px | Any mobile fix must also re-specify SVG type scales (min 11 px rendered). | H |
| **H-06** | ch4 plate | The vessel plate has a `figcaption` + a `<details class="figure-data">` + the matrix below, i.e. **three** descriptions of the same 9 objects | Redundant reading paths; the plate, the caption and the matrix should have distinct jobs. | H |

## 1.10 I — Instruments and app behaviour (measured)

| ID | Location | Probe | Observed | Impact | Conf. |
|---|---|---|---|---|---|
| **I-01** | Rīks B (calibration) | `A = 0` → `A = 999` | `A = 0` ⇒ **−0,330 mg/L**; `A = 999` ⇒ **31 057 mg/L**; no range warning, though ch10 states that A = 0,982 is already above the top standard (0,975) | The tool contradicts the chapter's central lesson (extrapolation is not measurement) and prints a negative concentration as if it were an answer. | C |
| **I-02** | Rīks C (half-life) | default unit; `1e9` | Default unit = **dienas**; the chapter's worked case is **220 s**. `1e9` is rejected as "not a positive half-life" (scientific notation unsupported) | The tool's default fights the source question; rejecting `1e9` is defensible but undocumented. | C |
| **I-03** | search index | inspect embedded JSON | 13 blocks contain the literal string `Atbilde`; the index is built from the article before `<details>` state is considered | Searching can surface the text of a closed answer without the user opening it — a partial leak of the "closed recall" discipline. | H |
| **I-04** | Rīks A (sig-fig) | `1e3` | "Pirmais skaitlis nav derīgs… bez mērvienības." Scientific notation is a course concept (ch8 uses `4,5·10²`), so the input grammar should accept it or say why not. | Users type what the chapter teaches and are told they are wrong. | C |
| **I-05** | Rīks D (graph trainer) | `9999` | Prints *«Par augstu par 9977,6 mg/L»* — arithmetically right, pedagogically wrong (no clamp at the plot's axis range) | The trainer rewards nonsense with a precise-looking number. | H |
| **I-06** | all tools | reset | No explicit "clear/reset" control; clearing means selecting text and deleting | Small, repeated friction in a study loop. | C |
| **I-07** | exam mode | finish | Works (20 stratified questions, answer sheet, print). No post-exam diagnosis (see C-07). | The feature stops one step short of teaching. | C |
| **I-08** | workspace consent | inspect | Persistence is opt-in (checkbox) and `persistMarks()` returns early without consent — correct. But `localStorage.getItem` runs on load unconditionally | Consent semantics are asymmetric (read vs write). | C |

## 1.11 J — Build, process and repository hygiene

| ID | Location | Observed | Impact | Conf. |
|---|---|---|---|---|
| **J-01** | `build_doc.py` | Rebuild is **byte-identical** (SHA-256 match) and assembles sections → article → post-process (h3 ids → figures → index → table wrap → NBSP → fonts) | A genuine strength: the deliverable is a build artefact, so tasks can be specified against sources. | C |
| **J-02** | `build_doc.py` | Post-processing is regex over HTML: h3 id injection, `<table>` wrapping, NBSP insertion, `{{FIG:}}` replacement. Ordering matters and one bad regex can silently mangle a table | The pipeline has no assertion layer; a malformed section ships. | H |
| **J-03** | NBSP pass | `unit_re` rewrites `12.5 mL`-style text nodes document-wide; the unit list contains both `mg/100 g` and `mg/100g`, and the regex is applied to text nodes only (good) | Correct today (verified by `check_sigfig_cases`), but fragile: one new unit string and spacing breaks silently. | H |
| **J-04** | artifact | 1 296 228 B single file, 117-page print, 815-entry index inlined | Fine for offline, but there is **no size budget** and no perf budget; a 2 MB file would ship unnoticed. | H |
| **J-05** | `build/` | 41 MB of sources and stale artefacts; no manifest of "authoritative vs generated" | See A-09. | C |
| **J-06** | checks | Five checkers exist (`check_terms`, `check_sigfig_cases`, `check_calibration`, `check_graph_trainer`, `verify_numbers`) but each needs its own flag, and none runs automatically | "Green" depends on remembering five commands. | C |

## 1.12 Scorecard (not a certification)

| Dimension | v1 (2026-10-31) | v2 (2026-11-01) | Why |
|---|---:|---:|---|
| Factual / arithmetic reliability | 3.5 | **4.0** | All checkers green, build reproducible; still undermined by A-01/A-06 self-audit drift and I-01/I-02 guard rails. |
| Terminology consistency | 3.5 | **4.0** | Register works (0 violations) for source terms; the document's *own* new metalanguage is unregistered (B-02), and labels still vary (B-03). |
| Prose clarity | 3.0 | **3.5** | Long-paragraph problem largely solved (10 paragraphs > 60 words); em dashes (B-01) and metaphor drift (C-09) remain. |
| Explanation depth | 4.0 | **4.0** | Strong worked examples; missing prerequisites (C-01), counterfactual (C-02), tool rationale (C-03). |
| Study efficacy | 4.0 | **4.5** | 127 prompts, filters, exam mode, answer sheet — genuinely excellent; missing diagnosis (C-07) and spacing (C-08). |
| Visual design | 3.5 | **3.5** | Calm and credible, but hero-scale title (D-03), numeral grid (D-01), metadata strip (D-02), single-accent overload (D-04). |
| Accessibility | 3.5 | **4.0** | 0 unlabelled inputs, 21/21 SVG titles, focus management, 44 px targets; weak row scopes (F-05), no `lang` on English (B-04), no axe run. |
| Responsive | 3.0 | **2.5** | Worse than v1's assessment: measured broken top bar (F-01) and forced 820 px figures (F-02). |
| Print | 3.5 | **3.0** | 117 pages with two mostly-blank pages (G-01/G-02), no page-numbered TOC (G-03), no colophon (G-04). |
| Integrity of the audit trail | 3.5 | **2.5** | The change log now disagrees with the artifact in six places (A-01…A-06). |
| **Overall** | **3.6** | **3.9** | A stronger document with a weaker trust surface. |

## 1.13 Tell audit against `tells.md`

| Tell | Status in this document | Where | Verdict |
|---|---|---|---|
| Violet/indigo gradient, gradient text | absent | — | pass |
| Glass panels / backdrop blur | absent | — | pass |
| Soft grey shadow under cards | 3 decorative shadows remain | panels, figure-data | **warn** (D-05) |
| Three identical feature cards / icon-over-title tiles | absent as cards, **present as a numbered outcomes grid** | masthead | **fail vs §6.2** (D-01) |
| Eyebrow / kicker / pill badge | absent | — | pass |
| Cream ground + terracotta | absent (cool ground + magenta) | — | pass |
| Oversized italic serif headline | absent (one sans family) | — | pass |
| Em-dash habit | 96 prose occurrences | global | **warn** (B-01) |
| Decorative status dot / "updated" badge | **metadata strip** *«Pārbaudīts: …»* | masthead | **warn** (D-02) |
| Fade-and-rise on every section | absent (motion is 140 ms state transitions only) | — | pass |
| Rainbow nav dots / per-chapter motif icons | absent | — | pass |
| Fake dashboard hero | absent | — | pass |
| Mono micro-labels / all-caps tracked labels | absent | — | pass |

**Reading of the table:** the page has avoided the obvious AI-slop vocabulary and kept a real editorial voice. What remains is the *third-wave* tell — "editorialise the hero" — plus a handful of honesty tells (stale metadata, duplicated claims). That is exactly what N10–N12 target.

## 1.14 Skills ledger — which workspace skill applies, and where it conflicts

| Skill (path under `workspace_skills/`) | Use it for | Tasks | Known conflict |
|---|---|---|---|
| `design-taste-frontend` (`tells.md`, `lint.mjs`, `inspect.mjs`) | Tell registry, automated gate, screenshot loop | N10, N11, N14 | Its "one honest video" advice is inapplicable to an offline textbook — record as an accepted warning. |
| `impeccable` (`reference/mode-read.md`) | Reading-mode hierarchy, line length, density | N10, N12 | Recommends more ornament than §6 allows; §6 wins. |
| `cognitive-deload-auditor` | Extraneous load, signalling, recall gaps | N05, N09, N19 | Wants fewer callouts — agrees with §6's max-two rule. |
| `print-css-alchemist` | `beforeprint` unfolding, pagination, running heads | N13 | Its "unfold all details" recipe is already used; N13 adds a *choice*, not a default. |
| `svg-spatial-occlusion` | Label masking / reverse-pin recall on diagrams | N16, N17 | Its occlusion UI is a feature, not a default; use only where a figure is memorised (glassware, meniscus). |
| `state-scrubber-lab` | Phase scrubbers (titration, halving ladder) | N17, N19 | Must stay static-first: no autoplay, keyboard-operable, printable fallback. |
| `synoptic-matrix-architect` | ≥4-attribute comparison with sticky axes | N11, N14 | Sticky axes fight `table--stack`; resolve per table, not globally. |
| `lexicon-morphology-weaver` | Term decomposition rails (*pus-sabrukšanas*, *mēr-kolba*) | N03 | Only for verified decompositions; never invent etymology. |
| `tufte-margin-scholar` | Sidenote vocabulary for long prose | N12 (optional) | Its hairline/serif/cream rules lose to §6 on conflict. |
| `blueprint-spec-sheet` | Title-block / spec-table *idea* only | N10 | Coordinate-frame chrome is banned as ornament — do not import the frame. |
| `mook-visual-compendium` | Numbered diagram plates | N16 | Its magazine micro-grid conflicts with the measured reading column; take the numbering discipline only. |
| `pdf-vector-surgeon` | Print-grade vector QA | N13, N16 | Useful for page-by-page raster checks (already the method used here). |
| `break-ui` | Worst-case data (long Latvian compounds, 320 px) | N14 | Directly applicable: Latvian has 25+ character compounds. |
| `polish` | Language-level pass | N08 | Language-agnostic prompt; needs Latvian examples injected. |
| `learn-then-test`, `interactive-study-guide` | Retrieval design patterns | N19 | Both trend toward gamification; §"no gamification" wins. |
| `impeccable`, `audit`, `design-taste-frontend/lint` | Final gates | N20 | Note: `audit` assumes a running app; here it is a static file. |

**Skills explicitly not used:** `animate`, `review-animations`, `animation-performance`, `find-animation-opportunities` (the document should stay still); `pick-ui-library`, `prototype`, `playground` (no new stack); `pdf-claude`/`pdf-codex`/`pdf-beautify` (PDF is an export target, not a source of truth).

---

# 2. Task map

## 2.1 Waves and dependencies

```
WAVE 0 — FREEZE (0.5 day, not a task)
  baseline copy → build/baseline/v2/  (html + pdf + hashes)
  record the six measured numbers in a machine-readable file
        │
        ▼
WAVE A — INTEGRITY (N01 → N04)          P0  ·  must close before any content edit
  N01 truth ledger ──┬──> N04 number provenance
  N02 contradictions ┤
  N03 terminology v2 ┘
        │
        ▼
WAVE B — EXPLANATION (N05 → N09)        P0/P1  ·  content may now change safely
  N05 hard ideas ──> N06 prerequisites ──> N07 calc component
  N08 language polish (parallel)  N09 retrieval & spacing (depends on N05)
        │
        ▼
WAVE C — DESIGN (N10 → N14)             P1  ·  after prose is stable
  N10 restyle ──> N11 retexture ──> N12 typography
  N13 print (depends on N10/N11/N12)   N14 responsive (parallel with N13)
        │
        ▼
WAVE D — SVG (N15 → N17)                P1  ·  after N11 tokens exist
  N15 library ──> N16 redraw existing ──> N17 new figures
        │
        ▼
WAVE E — CAPABILITY (N18 → N20)         P2  ·  last, on stable content
  N18 instruments ──> N19 workspace ──> N20 release engineering
```

**Why this order.** N01/N02 protect the document's credibility and are cheap. N03/N04 make later prose edits safe (a term or number changed in ch8 must not silently break ch12 or a tool). Waves B–D change large amounts of markup; without a drift gate they would reproduce exactly the problem they are fixing. N18/N19 touch behaviour and would otherwise be re-tested three times.

## 2.2 Priority and effort matrix

| ID | Task | Wave | Priority | Effort | Risk | Blocks |
|---|---|---|---|---|---|---|
| N01 | Truth ledger | A | **P0** | M | low | everything |
| N02 | Visible contradiction sweep | A | **P0** | S | low | — |
| N03 | Terminology register v2 | A | **P0** | M | low | N05, N08 |
| N04 | Number provenance | A | **P0** | L | med | N07, N18 |
| N05 | Twelve hard ideas | B | **P0** | L | med | N06, N19 |
| N06 | Prerequisite signalling + concept map | B | P1 | M | low | — |
| N07 | Worked-example component | B | P1 | M | low | N18 |
| N08 | Language polish | B | P1 | M | low | N12 |
| N09 | Retrieval, interleaving, spacing | B | P1 | M | low | N19 |
| N10 | Anti-slop restyle | C | **P1** | L | med | N11, N13 |
| N11 | Retexture / material system | C | P1 | M | low | N13, N15 |
| N12 | Typography v2 | C | P1 | M | low | N13 |
| N13 | Print edition v2 | C | P1 | L | med | N20 |
| N14 | Narrow screens & input | C | **P0** | M | med | N20 |
| N15 | SVG component library | D | P1 | M | low | N16, N17 |
| N16 | Redraw 21 existing SVGs | D | P1 | L | med | — |
| N17 | 10 new explanatory figures | D | P2 | L | med | — |
| N18 | Instruments hardening | E | P2 | L | med | — |
| N19 | Workspace v2 | E | P2 | L | med | — |
| N20 | Release engineering | E | P2 | M | low | — |

Effort scale: **S** ≤ 0,5 day · **M** 0,5–1,5 day · **L** 1,5–3 days · **XL** > 3 days (no task here is XL).

## 2.3 File ownership map

Nothing is edited in the root HTML. Every task edits sources below and runs the build.

| Path | Role | Owner tasks |
|---|---|---|
| `build/sections/00_front.html` | masthead, TOC, outcomes | N10, N02 |
| `build/sections/01…16_ch*.html` | chapter bodies | N02, N03, N05–N09, N14, N17 |
| `build/sections/98_quickref.html` | print exam sheet | N02, N13 |
| `build/sections/99_footer.html` | source line, colophon | N01, N13 |
| `build/style.css` | tokens, layout, print CSS | N10–N14 |
| `build/app.js` | search, tools, workspace | N18, N19, N14 |
| `build/figures/*.svg` | 12 figures | N16, N17 |
| `build/figures/glassware.html` | 9 vessel icons | N16 |
| `build/build_doc.py` | assembly + post-process | N01, N04, N13, N20 |
| `build/check_*.py`, `verify_numbers.py` | verification | N01, N04, N18, N20 |
| `build/concepts.json`, `terminology.json` | registers | N01, N03, N09 |
| `build/terminology_audit.csv`, `type_inventory.csv`, `table_register.md` | audit artefacts | N03, N11, N12 |

## 2.4 Ten invariants that apply to every task

1. **Sources first.** Edit `build/…`; never hand-edit `Master_2_tema_merijumi_un_grafiki.html`. A task is not done until `python3 -I build/build_doc.py` regenerates it.
2. **No invented facts.** Silence is written as «avotā nav norādīts»; standard knowledge is marked «papildinājums»; made-up numbers are «ilustratīvs piemērs» (`AGENTS.md` §3.3).
3. **Every divergence is logged.** A new correction becomes a new row in the change log *and* in the defect register with location, original, correction, reason, confidence.
4. **Numbers are recomputed, never copied.** Any number a task touches must be re-derived by a checker in `build/` before it ships (`AGENTS.md` §3.7).
5. **Self-contained.** 0 external URLs, 0 runtime fetch, 0 analytics, 0 storage without consent, 0 new top-level dependency.
6. **One task = one reviewable change set.** Do not mix terminology, arithmetic, layout and SVG in one pass; it makes review impossible and hides regressions.
7. **Latvian typography is mandatory**: decimal comma, NBSP between number and unit, `−` (U+2212) for negative values in maths, `–` for ranges, `„ “` for quotes inside Latvian, `ML`, `mL`, `L`, `s`, `min`, `h`, `d`, `°C`, `mol/L`, `mg/L`.
8. **Print is a first-class target.** Every visual change is checked in the 117-page PDF, not only on screen.
9. **No gamification, no mastery score, no streak, no badge, no confetti.** Progress is a plain state (`AGENTS.md` §9).
10. **Honest reporting.** At the end of a task, state what was *not* verified (browser, device, axe, lecturer).

## 2.5 Task document conventions

- **Findings** listed in the metadata table are the evidence anchors from §1.
- **DoD** is a checklist of *falsifiable* statements, each with a command or a screenshot check.
- **Substeps** (3) are the main line of work, in order.
- **Subtasks** (2–3) are parallel or follow-on workstreams; each has exactly 3 substeps.
- **Acceptance** gives copy-paste commands; a task may not be closed if any command has a non-zero exit or an unexpected line.
- **Rollback** names the reversible unit (usually `git`-less: keep `build/baseline/v2/` and restore the touched files).

---

# 3. The 20 tasks

---

## N01 — Make the document's self-description executable (truth ledger)

| | |
|---|---|
| **Wave** | A — Integrity |
| **Priority** | **P0** |
| **Effort** | M (≈1,5 days) |
| **Risk** | Low — additive tooling + copy edits |
| **Axis** | self-audit, correctness, trust |
| **Skills** | `impeccable` (documentation clarity), `polish` (Latvian log wording) |
| **Files** | `build/build_doc.py`, `build/sections/16_ch16.html`, `build/sections/99_footer.html`, `build/sections/00_front.html`, `build/concepts.json`, new `build/audit_claims.py`, new `build/claims.json` |
| **Findings** | A-01, A-04, A-05, A-06, A-08, A-09, J-05 |

### Context

The change log is the document's honesty apparatus. It currently makes six verifiable claims that are false in the built artefact:

- *«52 tabulas»* → 75 tables;
- *«10 attēli»* → 12 figures / 21 SVGs;
- *«105 h3 id»* → 121 `<h3>`;
- *«719 bloki»* → 815 search blocks;
- *«aktīvajā prozā vairs nav em svītru (0)»* → 96 prose em dashes;
- `build/concepts.json` → `"recall_items": 113` while the document has 127.

Plus two dates disagree (masthead/footer "2026-10-31" vs change-log "2026-11-01"), and the `build/` folder contains stale by-products that an auditor will mistake for sources (`verified_prev.json`, three `inspect*/` dumps, `_test*.woff2`, `__pycache__`).

This is not cosmetic. The document's rhetorical stance is *“nothing is hidden, every number is recomputed”*. One countable contradiction costs more trust than ten missing features.

### Why this is P0 and first

Every later task (N03 terminology, N05 explanations, N16 SVGs) changes counts. If the counts are typed by hand, they will be wrong again the same day. The only durable fix is to **remove the number from the prose and generate it**, then fail the build when prose and artefact disagree.

### Definition of Done

- [ ] `build/claims.json` exists and is generated by `build/audit_claims.py` from the *built* HTML, containing at minimum: `tables_total`, `tables_stacked`, `figures`, `svgs`, `h3_total`, `h3_with_id`, `details`, `recall_items`, `glossary_terms`, `search_blocks`, `em_dashes_prose`, `chapters`, `print_pages`, `build_sha256`, `built_at`.
- [ ] Every count in the change log and in chapter 15's lead is a `{{CLAIM:key}}` placeholder resolved at build time, or is phrased without a number.
- [ ] One `Pārbaudīts` date exists in the document, generated from the build, and the masthead, footer and change log all read it from the same token.
- [ ] `build/concepts.json` is regenerated by the build (or deleted and replaced by the generated claim), never hand-edited.
- [ ] `audit_claims.py --check` exits non-zero if any `{{CLAIM:}}` in the source has no value, or if a literal number next to a known noun (tabulas, attēli, jautājumi, bloki, sadaļas) disagrees with the generated value.
- [ ] `build/` contains a `MANIFEST.md` that marks each file as **source**, **generated**, or **stale/removable**; the stale ones are moved to `build/_archive/` (not deleted) in one pass.
- [ ] The change log gains a row `D52 — self-audit drift` describing the six wrong counts and the mechanism that now prevents them.

### Substeps

1. **Measure, then freeze the measurement.** Write `build/audit_claims.py` so that it parses the *built* HTML with no third-party libraries (regex + `json`), emits `claims.json`, and prints a one-screen table. Run it once and store the result as `build/claims.baseline.json`. This becomes the ground truth for every later task.
   - Count definitions must be explicit in code comments: a “table” is `<table class="data-table…">`; a “figure” is `<figure>`; “prose em dashes” is `—` in text nodes after removing `<script>`, `<style>` and `data-quote` spans; “recall item” is `id="recall-*"`.
   - Add a `--json` and `--check` mode so the same script serves humans and the gate.
2. **Replace typed numbers with placeholders.** Introduce a single `{{CLAIM:key}}` syntax handled in `build_doc.py` immediately after the article is assembled (before the search index, so the index sees the final text). Migrate the change-log entries, the ch15 lead, the “48 slēgti jautājumi” sentence and the footer source line. Where a sentence would read badly with a generated number, rewrite the sentence to avoid the number entirely (e.g. *«visas tabulas ir ar parakstu»* instead of *«52 tabulas»*).
3. **Install the gate and the date token.** Add `{{BUILT_AT}}` (ISO date) and `{{BUILD_SHA}}` resolved by `build_doc.py`; use them in the masthead metadata, the footer and the change log's newest entry. Then wire `audit_claims.py --check` into a single `build/check_all.sh` (N20 will own the wrapper, but N01 creates it) so a drifted count fails loudly.

### Subtasks

#### N01.1 — Count definitions and the claims file (≈4 h)

1. Enumerate every countable noun in the change log and ch15 lead by grepping the sections for `tabul|attēl|jautājum|blok|sadaļ|vārdnīc|defekt`. Write the list into `build/claims_spec.md` with the exact definition of each count and the reason it matters to a reader.
2. Implement `audit_claims.py` with three functions (`parse_html`, `count_all`, `compare_literals`), a `--json` output, and unit-testable pure functions. Run it against the built HTML and store `claims.baseline.json`.
3. Sanity-check each number by hand against an independent method (e.g. `grep -c '<table'` for tables, a DOM count via Playwright for recall items) and record the cross-check in `claims_spec.md`. Any count that cannot be reproduced two ways is either defined wrongly or not worth publishing.

#### N01.2 — Placeholder migration (≈6 h)

1. Add the placeholder pass to `build_doc.py` right after `article = wrap_tables(article)` and before `build_search_index.build_index(article)`, with a hard error on unknown keys.
2. Rewrite the six wrong change-log entries **without deleting history**: keep the original claim, append *«(mērīts 2026-11-01: 75)»*, and add `D52` explaining the drift and the mechanism. Historical honesty beats retroactive tidiness.
3. Rewrite the ch15 lead so it distinguishes the chapter's 48 items from the workspace's 127 (`«Šajā nodaļā ir {{CLAIM:recall_ch15}} slēgti jautājumi; darba telpa rāda visus {{CLAIM:recall_items}} dokumenta jautājumus.»`).

#### N01.3 — Date, hash, manifest (≈4 h)

1. Replace every hard-coded verification date with `{{BUILT_AT}}`; delete duplicates so exactly one date string exists in the output (verify with `grep -c 'Pārbaudīts'`).
2. Add `{{BUILD_SHA}}` (first 12 hex chars of the built file's SHA-256) to the footer/colophon and to the change log's newest line, so any printed copy can be matched to a build.
3. Write `build/MANIFEST.md` (source / generated / archive) and move the stale artefacts into `build/_archive/2026-11-01/`. Keep `verified_prev.json` only if a script still reads it — check with `grep -rn verified_prev build/*.py`.

### Acceptance

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_2
python3 -I build/build_doc.py                      # exit 0
python3 -I build/audit_claims.py --check           # exit 0
grep -c 'Pārbaudīts' Master_2_tema_merijumi_un_grafiki.html   # 1 (or 2 incl. footer, same value)
grep -o '{{CLAIM:[a-z_]*}}' Master_2_tema_merijumi_un_grafiki.html | head   # empty
python3 -I build/audit_claims.py --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['tables_total'], d['recall_items'], d['em_dashes_prose'])"
```

Expected: `75 127 <number ≤ 96>`; no unresolved placeholders; no contradictory date.

### Rollback

Restore `build/sections/16_ch16.html`, `00_front.html`, `99_footer.html`, `build/concepts.json` and `build/build_doc.py` from `build/baseline/v2/`; the new files (`audit_claims.py`, `claims.json`, `MANIFEST.md`) are additive and can stay.

---

## N02 — Sweep the visible contradictions (ordinals, totals, dates, numbering collisions)

| | |
|---|---|
| **Wave** | A — Integrity |
| **Priority** | **P0** |
| **Effort** | S (≈0,5 day) |
| **Risk** | Low |
| **Axis** | editorial correctness, first-impression quality |
| **Skills** | `polish`, `impeccable` (reading-mode detail) |
| **Files** | `build/sections/08_ch8.html`, `09_ch9.html`, `12_ch12.html`, `15_ch15.html`, `98_quickref.html`, `build/style.css` |
| **Findings** | A-02, A-03, A-04, A-07 |

### Context

Four `<ol class="steps">` lists carry a manual ordinal inside the `<li>` while the list itself is `list-style: decimal`, so the rendered output is `1. 1. …`, `2. 2. …`. Nineteen items are affected across the sig-fig decision tree, the mistake ladder, the six-step graph reading method and the five-step solution flow. The screenshot of ch12 at 1440 px shows `1. 1. Nosakiet mērķi.` plainly; the same defect is in the 117-page PDF.

This is the cheapest, most visible quality defect in the document: it appears in the *procedures students memorise*, and it makes a carefully written document look machine-assembled.

### Definition of Done

- [ ] No rendered `<ol>` shows a doubled ordinal; the fix is structural (remove the manual ordinal from the text, or convert the list to a non-numbered `<ul>`/definition list where a number is part of the label).
- [ ] Step labels read naturally *after* the marker: `1. Nosakiet mērķi.`, not `1. 1. Nosakiet mērķi.` and not `1. Solis 1 — …`.
- [ ] Chapter 15's lead and counter agree (delegated to N01's `{{CLAIM:}}`; N02 only removes the contradictory literal if N01 has not landed).
- [ ] The quick-reference sections are numbered `A–H` or `Q1–Q8`, not `1.–8.` (so they cannot be confused with chapters).
- [ ] The masthead/footer date is single-sourced (N01) or, if N02 lands first, manually equal in both places.

### Substeps

1. **Audit every list.** Run a parser over the built HTML that prints, for each `<ol>`/`<ul>`: its class, item count, and whether the first 12 characters of each item are a manual ordinal (`\d+[.)]`, `Solis \d`, `\d+\. solis`). Produce `build/list_audit.txt`. This catches the four known cases plus any `«Solis 02»`-style remnant.
2. **Choose per list.** For a true sequence, keep `<ol>` and delete the manual ordinal, moving the number's semantic role into the bold label (*«Nosakiet mērķi.»*). For a ladder where the number *is* the content (mistake #1…#6 for cross-reference), switch to a definition list or a table with an explicit `Nr.` column — cross-references then point at a stable label instead of a position.
3. **Re-render and verify.** Screenshot the four regions at 1440 px and extract the four PDF pages; confirm no doubled marker and no orphaned punctuation (`1. . Nosakiet`). Add a one-line regression note to the change log.

### Subtasks

#### N02.1 — Ordinal audit and structural fix (≈2 h)

1. Extend the audit to headings and table cells for the patterns `^\d+\.\s*\d`, `Solis \d{2}`, `\d+\.\s*solis`, `Nr\.\s*\d` and report every hit with file and chapter.
2. Edit the four step lists: remove manual ordinals, keep the bold verb phrase, and ensure the `<li>` text starts with a capital letter and a full stop at the end.
3. Check the ch8 "mistake ladder" cross-references (they may point to "1. solis"): if a reference exists elsewhere, update it to the new label and log the change.

#### N02.2 — Numbers and dates that must agree (≈1 h)

1. Grep all chapter leads for totals (`\b\d{2,3}\b` followed by `jautājum`, `tabul`, `attēl`, `lpp`) and list them in `build/number_claims.txt`; hand-check each against the artifact.
2. Fix ch15's lead/numerator mismatch (or defer explicitly to N01 and record the dependency in the task note).
3. Unify the two `Pārbaudīts` dates to one value; if N01 has not landed, add a TODO marker in `16_ch16.html` naming N01 as the owner.

#### N02.3 — Quick-reference numbering (≈1 h)

1. Renumber `98_quickref.html` sections from `1.–8.` to `A–H` and update any in-document reference that says «8. pielikums» / «8. sadaļa».
2. Check the running head still fits with the new labels (print render of the last 4 pages).
3. Add a change-log line describing the renumbering and why (collision with chapter numbers).

### Acceptance

```bash
python3 -I build/build_doc.py
python3 - <<'PY'
import re
h=open('Master_2_tema_merijumi_un_grafiki.html',encoding='utf-8').read()
bad=[m.group(0) for m in re.finditer(r'<li>\s*<strong>\d+\.', h)]
print('manual-ordinal li:', len(bad))
print('double marker risk:', len(re.findall(r'<ol class="steps">(?:(?!</ol>).)*?<li>\s*<strong>\d+\.', h, re.S)))
PY
```
Expected: `0` and `0`.

### Rollback

Single-file restores of the four sections; no build-system change.

---

## N03 — Terminology register v2: the document's own metalanguage

| | |
|---|---|
| **Wave** | A — Integrity |
| **Priority** | **P0** |
| **Effort** | M (≈1,5 days) |
| **Risk** | Low–medium (touches prose broadly) |
| **Axis** | terminology, consistency, accessibility (language tagging) |
| **Skills** | `lexicon-morphology-weaver` (verified decompositions only), `polish`, `cognitive-deload-auditor` (metaphor load) |
| **Files** | `build/terminology.json`, `build/check_terms.py`, all `build/sections/0*.html`, `1?_ch*.html`, `98_quickref.html`, `build/style.css` (if a term class is needed) |
| **Findings** | B-02, B-03, B-04, B-06, B-07, C-09 |

### Context

The v1 register (T01) covers **source** terms — the defects S1–S23 and the corrections published in ch14. `check_terms.py` reports 0 violations, and that is true. But the document has since invented its own teaching metalanguage, and none of it is registered:

| New term | Where | Problem |
|---|---|---|
| `lēmumu plūsma` | ch12 | Not a chemistry term; means "decision flow". Undefined; used once as a heading. |
| `atceres darba telpa` | ch15 | "recall workspace" — a UI metaphor competing with `Paškontrole` (chapter title). |
| `modeļa karte` | ch10 | "model card" — borrowed from ML documentation, unexplained. |
| `signāla ceļš` | ch3, ch10 | Used both for the analytical chain (sample → signal) and for the figure's arrow path. |
| `sargcipari` | ch8 | Good, precise, but never defined in the glossary. |
| `kāpnes` | ch11 | "ladder" for successive halvings; competes with `pussabrukšanas kāpnes` in the figure title. |
| `saīsne` | top bar | Abbreviation used as a button label; not in the glossary. |
| `kontrolsaraksts` | quickref | Fine, but the print sheet and ch12 use `pārbaudes saraksts` for the same idea. |
| `rīks` | tools | `Rīks A…E` — fine, but the tools are also called `instrumenti` in ch16 E. |

On top of that, three labels still name the same statistical concept differently (B-03), English terms are untagged for screen readers (B-04), and two spellings of the micro sign plus two spellings of `mg/100 g` coexist (B-06).

### Definition of Done

- [ ] `build/terminology.json` gains a second namespace, `document_terms`, with the same fields as the source terms (`term`, `en`, `def`, `confuse`, `first_use_anchor`, `status: preferred|avoid|deprecated`).
- [ ] Every term in the table above has exactly one preferred form, one English equivalent, one one-sentence definition, and (if it survives) one glossary entry with an `id`.
- [ ] No document term is used before its first definition; `check_terms.py --report` extended to flag "used before defined" for `document_terms`.
- [ ] `precision / trueness / accuracy` resolve to a single published triple used identically in ch6, ch14 and ch15 (one label per concept, with the other two listed as "avoid" in the register).
- [ ] Every English term in running text is wrapped `<span lang="en">…</span>`; `grep -c 'lang="en"'` ≥ number of glossary English fields + inline uses, and a checker asserts no bare English word from a whitelist appears untagged.
- [ ] Micro sign is `µ` (U+00B5) everywhere; `mg/100 g` (with NBSP) everywhere; both enforced by a check.
- [ ] `M` used as a unit is replaced by `mol/L` in prose and table headers, with `M` allowed only where explicitly defined ("\(M\) = mol/L, šajā dokumentā nelietots").

### Substeps

1. **Inventory the metalanguage.** Script over the built HTML: collect all `<h3>`/`<h4>` phrases and all italicised terms, then diff against `terminology.json`. Every term that is neither a source term nor a chemical quantity goes into a candidate list. Review the list by hand against the table above; add what is missing (there will be more).
2. **Decide, define, rename.** For each candidate: keep (define + glossary entry), rename (choose a plainer Latvian word), or delete (rewrite the sentence without the metaphor). Renaming is a project-wide find/replace with a before/after table in the change log; deletion is preferred where the metaphor carries no information.
3. **Encode and enforce.** Extend `check_terms.py` with (a) the `document_terms` rules, (b) the used-before-defined check, (c) the `lang="en"` check, (d) the micro-sign and `mg/100 g` checks. Then run it against the build and fix every hit. The checker becomes part of `check_all.sh`.

### Subtasks

#### N03.1 — Build the document-term inventory (≈4 h)

1. Extract headings, bold lead-ins, italic terms, and the labels of all `<div class="instrument">`, `<div class="role">` and workspace controls; write `build/document_terms_raw.csv` with term, count, first anchor.
2. Classify each row: *chemical quantity* (skip), *source term* (already covered), *document coinage* (new), *English loan* (needs `lang="en"` and a definition).
3. Cross-check the coinages against the ch14 glossary; list every coinage that has no glossary entry.

#### N03.2 — Resolve the accuracy cluster and the metaphor set (≈6 h)

1. Publish one triple in ch6's table and ch14's glossary: e.g. **precizitāte** (scatter), **pareizība** (trueness / closeness to reference), **kopējā tuvība** (accuracy as the umbrella). Mark the two rejected synonyms in the register as `avoid`. Update ch15's quiz wording to the same triple.
2. Rewrite sentences that use *plūsma*, *karte*, *ceļš*, *telpa*, *kāpnes* as structural metaphors so that each is used at most once, in a place where it is defined (or remove them). Keep *kāpnes* only as the figure's label and define it in the caption.
3. Add `sargcipari` and any other surviving coinage to the glossary with `id`, English equivalent and "confuse" note; link the first use in prose.

#### N03.3 — Encode the rules in the checker (≈4 h)

1. Add `document_terms` to `terminology.json` and extend `check_terms.py` with a "used before defined" pass that walks the article in document order and tracks the first occurrence of each `id="glossary-*"` anchor.
2. Add the `lang="en"` pass with a whitelist derived from the glossary's `en` fields; report bare occurrences.
3. Add the unit-spelling pass (`μ` → `µ`, `mg/100g` → `mg/100 g`, bare `M` as a unit) with a `data-quote="true"` exemption so source quotations stay verbatim.

### Acceptance

```bash
python3 -I build/build_doc.py
python3 -I build/check_terms.py Master_2_tema_merijumi_un_grafiki.html --report   # 0 violations, and prints document-term stats
grep -c 'lang="en"' Master_2_tema_merijumi_un_grafiki.html                          # > 0
grep -c 'μ' Master_2_tema_merijumi_un_grafiki.html                                  # 0
```

### Rollback

`terminology.json` and `check_terms.py` are versioned copies; section edits are the only irreversible part — keep a `build/baseline/v2/sections/` snapshot before starting.

---

## N04 — Number provenance: every figure traceable, every constant shared

| | |
|---|---|
| **Wave** | A — Integrity |
| **Priority** | **P0** |
| **Effort** | L (≈2,5 days) |
| **Risk** | Medium — touches instruments and figures |
| **Axis** | correctness, reproducibility |
| **Skills** | `pdf-vector-surgeon` (numeric QA discipline), `impeccable` (labelling clarity) |
| **Files** | `build/verified.json`, `build/verify_numbers.py`, `build/check_calibration.py`, `build/gen_figures.py`, `build/app.js`, `build/sections/10_ch10.html`, `11_ch11.html`, `12_ch12.html`, `16_ch16.html` |
| **Findings** | I-01, I-02, A-05, J-02, J-03 |

### Context

The document publishes a `verified.json` and three checkers that pass. But provenance is **not uniform**:

- the least-squares slope appears as `0,0321657` (tool, `verified.json`), `0,0322` (equation line), `0,03217` (prose) — three precisions with no stated policy (this was C-09 in v1, partially fixed);
- the calibration tool hard-codes `0,0321657` and `0,0106` in `app.js` instead of reading them from a single generated constant block;
- the half-life tool's default unit is `dienas` while the source question is 220 s, and `1e9` is rejected;
- the density table's inversion (`w = (ρ − 0,9979)/0,0073`) exists in prose, in the tool (option `sft_interp`) and in `gen_figures.py` — three implementations of the same arithmetic;
- `build/concepts.json` is stale (A-05), which means any coverage claim computed from it is wrong.

Duplication of constants across JS, Python and prose is how a document ends up teaching two different slopes.

### Definition of Done

- [ ] A single generated constants block (`build/constants.json` → emitted as `<script type="application/json" id="constants">` and as a Python `dict` import) holds every shared number: calibration slope/intercept/R²/range, density coefficients, half-life values, tolerance table, π-free exact factors.
- [ ] `app.js` reads the constants at runtime; no numeric literal for these values remains in JS (`grep` proves it).
- [ ] `gen_figures.py` renders every plot from `constants.json` + the data tables, not from literals.
- [ ] Every published number in prose carries a provenance class: **avotā** (source PDF), **aprēķināts** (recomputed here), **ilustratīvs** (invented), **papildinājums** (standard knowledge). A script lists every number in the main worked examples with its class; unclassified numbers fail the check.
- [ ] A reporting-precision policy paragraph exists in ch16 and is enforced by `check_calibration.py --policy` (each displayed value is either the full-precision value labelled "starpvērtība" or the rounded value at the stated precision).
- [ ] `concepts.json` is either regenerated by the build or removed in favour of `claims.json` (N01); in no case does a stale count remain.
- [ ] The half-life tool's default unit matches the chapter's worked case (seconds) and the tool accepts scientific notation or explains why it does not.

### Substeps

1. **Find every duplicated constant.** Script: extract all decimal literals with ≥4 significant digits from `build/sections/`, `build/app.js`, `build/figures/`, `build/*.py`; group by value; report any value appearing in ≥2 places with different rounding. This produces the real duplication map (expect ~25 constants).
2. **Centralise and inject.** Create `constants.json`, make `build_doc.py` embed it, make `app.js` parse it once at startup, make `gen_figures.py` and the checkers import it. Delete the literals. Rebuild and diff the rendered plots and tool outputs against the baseline — they must be identical to the last displayed digit.
3. **Label and enforce provenance.** Add the provenance class to every number in the main examples (a `<span class="num" data-prov="…">` or a table column), write the policy paragraph, and extend the checkers to fail on unclassified numbers and on precision drift.

### Subtasks

#### N04.1 — Duplication map (≈6 h)

1. Write `build/find_constants.py` (regex for `-?\d+[.,]\d{3,}` plus exponent forms), output `build/constants_map.csv` with value, occurrences, files, and rounded variants.
2. Review the map by hand: which numbers are *definitions* (tolerances, molar masses), which are *derived* (slope, R², density), which are *illustrative*.
3. Decide the canonical precision for each derived value (reporting policy) and write it into `claims_spec.md`.

#### N04.2 — Single source of truth (≈10 h)

1. Author `build/constants.json` with named keys, units and a `provenance` field per key; add a JSON-schema-ish validator in `verify_numbers.py`.
2. Replace literals in `app.js`, `gen_figures.py`, `check_*.py` with reads from the constants; rebuild and compare every tool output string and every SVG path coordinate against the baseline (byte-diff the SVGs; string-diff the tool outputs).
3. Update the prose equations that quote a rounded constant so they render the same string the tool uses, or explicitly label the prose version as the rounded form.

#### N04.3 — Provenance labels and the half-life default (≈6 h)

1. Add `data-prov` to the ~120 numbers in the worked examples (ch7, ch8, ch10, ch11, ch12), and a legend in ch1 explaining the four classes.
2. Extend `check_*` to fail when a `<span class="num">` has no `data-prov`, and when a "starpvērtība" value has fewer digits than the policy requires.
3. Change the half-life tool default to `s`, keep `dienas` as an option, accept `2.2e2`/`2,2·10²`, and update the tool's helper text.

### Acceptance

```bash
python3 -I build/find_constants.py --check      # 0 duplicated-with-drift
python3 -I build/verify_numbers.py --check      # exit 0
python3 -I build/check_calibration.py --residuals
grep -n '0,0321657\|0.0321657' build/app.js     # only inside the constants loader
```

### Rollback

`constants.json` is additive; keep the old literals in a `build/_archive/v2-literals.txt` diff so the change can be reversed file by file.

---

## N05 — Twelve hard ideas: from "stated" to "shown"

| | |
|---|---|
| **Wave** | B — Explanation |
| **Priority** | **P0** |
| **Effort** | L (≈3 days) |
| **Risk** | Medium — prose changes are the least reversible |
| **Axis** | explanation depth, understandability |
| **Skills** | `cognitive-deload-auditor`, `impeccable` (`mode-read.md`), `polish` |
| **Files** | `build/sections/06_ch6.html`, `07_ch7.html`, `08_ch8.html`, `10_ch10.html`, `11_ch11.html`, `12_ch12.html`, `03_ch3.html` |
| **Findings** | C-01, C-02, C-03, C-09 |

### Context

The document is strong at *worked* explanation and weaker at *causal* explanation. Twelve ideas are asserted correctly but not made inevitable. Each is a known exam failure point:

1. **Why n − 1** (ch7) — the residual-sum argument exists; there is no numeric side-by-side of `s(n)` vs `s(n−1)` for the same titres.
2. **Mixed significant-figure operations** (ch8) — the decision tree exists; the *reason* the two rules differ (absolute vs relative uncertainty) is one sentence.
3. **Calibration is not validation** (ch10) — the table exists; the failure mode ("the line is beautiful and the method is wrong") is not shown with a counter-example.
4. **Extrapolation** (ch10) — stated, and then contradicted by the tool (I-01).
5. **Offset half-life** (ch11) — the offset model is correct; the *trap* (reading an absolute time instead of a difference) is described, not demonstrated with a wrong-vs-right pair on the same axis.
6. **Density → mass fraction inversion** (ch12) — the algebra is shown; the *meaning* of the slope (0,0073 per %) is not interpreted.
7. **Tolerance vs error** (ch4, ch6) — the matrix says "pieļaujamā kļūda"; nowhere is it stated that tolerance is a *limit*, not an observed error.
8. **Precision vs trueness vs accuracy** (ch6) — the three-target figure exists; the vocabulary conflict is N03.
9. **The uncertainty budget** (ch6) — the table adds contributions; the *reason* independent contributions add in quadrature is absent.
10. **Exact numbers** (ch8) — "3 is exact" is stated; why counting numbers and definitions are exact is not.
11. **SD vs SEM** (ch7) — both are defined; the sentence "SEM shrinks with √n, SD does not" is the one students need.
12. **LOD vs LOQ** (ch3) — distinguished in a table; the signal-to-noise picture is missing.

### Definition of Done

- [ ] Each of the twelve has a **four-part block** with fixed headings: *Apgalvojums* (the claim, one sentence) → *Kāpēc* (mechanism, 2–4 sentences) → *Kā tas sabojājas* (a concrete wrong answer or wrong practice) → *Pārbaudi sevi* (one closed recall prompt with a numeric check).
- [ ] Three of the twelve (n−1, extrapolation, offset half-life) also carry a **numeric counterfactual table** with both the wrong and the right computation, side by side.
- [ ] No block exceeds 120 words of prose; each is at most one screen at 1440×900.
- [ ] Each block is registered in `concepts.json` with the same id as its recall prompt, so N19's filters can find it.
- [ ] Every new claim is either sourced («avotā»), marked «papildinājums», or recomputed; `check_terms.py` and the provenance check (N04) stay green.

### Substeps

1. **Audit the current state of each idea.** For each of the twelve, locate the existing passage, and record (a) whether the mechanism is present, (b) whether a failure mode is present, (c) whether a self-check exists. Produce `build/hard_ideas_audit.md` with a 12-row table. Expect ~5/12 to have all three.
2. **Write the missing mechanism + failure mode.** Use a consistent micro-structure and a consistent Latvian register. Keep the "why" physical/geometric (residuals, ratios, limits) rather than algebraic. Where a figure would carry it better, leave a marker `<!-- FIG NEEDED: id -->` for N17 rather than inventing an ASCII sketch.
3. **Attach the self-check and wire the concept ids.** Add one closed recall prompt per block (`id="recall-2xx"`, `data-concepts`), verify that the answer is not visible in markup (only inside `<details>`), and that the prompt's answer is recomputed by a checker where numeric.

### Subtasks

#### N05.1 — n−1, exact numbers, SD/SEM (statistics trio) (≈8 h)

1. Build the counterfactual table for the three titres (12,50; 13,05; 12,55): show `Σ(x−x̄)² = 0,185`, `s(n−1) = 0,304`, `s(n) = 0,248`, with the percentage difference and the sentence "the sample we hold is one of many; n−1 is the honest count of independent deviations".
2. Write the "exact numbers" block: counting, definitions (1 L = 1 dm³), and conversion factors are exact; explain that an exact number has infinite significant figures and therefore never limits a result.
3. Write the SD/SEM block with the √n statement and a 2-row numeric table (n = 3 → SEM = s/1,73; n = 12 → s/3,46) and the one-sentence interpretation ("SD describes the measurements; SEM describes the mean").

#### N05.2 — Calibration quartet: validation, extrapolation, residuals, sensitivity (≈10 h)

1. Write the "beautiful line, wrong method" counter-example: a calibration with R² = 0,999 that is still invalid because the blank is contaminated — show the intercept, not the R², as the tell.
2. Write the extrapolation block with the lemon value (0,982 vs top standard 0,975) and a mini-table of "inside range / outside range / what to report".
3. Write the residuals block: three residual patterns (random, curve, fan) and what each means, tied to the existing figure and its data table. Add the sensitivity sentence (`dA/dc` is the slope; LOD is a decision limit, not a sensitivity).

#### N05.3 — Offset half-life, density inversion, tolerance, budget, LOD/LOQ (≈12 h)

1. Offset half-life: wrong-vs-right pair on the same axes (absolute t vs Δt), with the hydrolysis numbers (t₀ = 115 s; halvings at 115 → 347,5 → 580 s) and a note that the source graph starts off zero (S18).
2. Density inversion: interpret slope 0,0073 g·mL⁻¹ per % as "each mass-% moves density by 7,3 mg/mL"; show that inverting it gives the same answer only inside the calibrated range.
3. Tolerance vs error, budget quadrature, and LOD/LOQ: one block each, each ≤120 words, each with its "how it breaks" sentence; keep the existing tables and link them rather than duplicating.

### Acceptance

- Rendered check: each block fits within one 1440×900 screen (screenshot);
- `grep -c 'class="hard-idea"'` = 12; each contains the four headings in order;
- `python3 -I build/check_terms.py … --report` → 0 violations;
- no new number without provenance (N04 check).

### Rollback

Restore the touched sections from `build/baseline/v2/sections/`; the new blocks are additive and can be removed by class.

---

## N06 — Prerequisite signalling and a real concept map

| | |
|---|---|
| **Wave** | B — Explanation |
| **Priority** | P1 |
| **Effort** | M (≈1,5 days) |
| **Risk** | Low |
| **Axis** | navigation, comprehension, structure |
| **Skills** | `cognitive-deload-auditor` (signalling), `state-scrubber-lab` (graph interaction, optional), `synoptic-matrix-architect` (coverage matrix) |
| **Files** | `build/sections/0*.html`, `build/sections/1*.html`, `build/concepts.json`, new `build/figures/concept-map.svg`, `build/style.css` |
| **Findings** | C-01, C-05, C-06 |

### Context

121 sections, 140 screens, a sidebar that lists sections, and no statement of what a section assumes. A reader who jumps to *«Atlikumi: vai taisne der datiem»* (ch10) is not told that residuals require the rounding rule (ch8) and the axis grammar (ch9). The concept inventory (`concepts.json`, 121 concepts) exists but is invisible.

Two cheap structural additions would fix most of it: a **"Pirms šīs sadaļas"** line under each chapter lead, and a **concept map** rendered from `concepts.json` as one SVG.

### Definition of Done

- [ ] Every chapter lead gains one line: *«Pirms šīs nodaļas: …»* with 1–3 links to the exact sections a reader needs, or *«Pirms šīs nodaļas: nekas — sākuma nodaļa»*.
- [ ] A new figure `concept-map.svg` renders the 121 concepts and their prerequisite edges as a layered graph: 16 chapter bands, edges left→right, no crossing labels, a `<title>`/`<desc>` and a data-table alternative (`<details>` with an edge list).
- [ ] The map is reachable from the masthead and from ch16 A, and is **static** (no JS required to read it); hovering/focus highlights a node's edges only as an enhancement.
- [ ] The map's node count, edge count and max depth are asserted by `audit_claims.py` against `concepts.json`.
- [ ] On a 390 px screen the map degrades to a chapter-level list (no sideways scroll — see F-02).

### Substeps

1. **Derive the prerequisite edges.** Start from `concepts.json` (concept → chapter/section) and add a hand-reviewed edge list (concept A must precede B). Keep it small: 80–140 edges is enough; a fully connected graph is unreadable. Store as `build/concept_edges.csv` with a `reason` column.
2. **Write the prerequisite lines.** For each chapter, take the incoming edges from the previous chapters and phrase them as reader actions (*«jāprot nolasīt grafiku (9.3)»*), not as topic names. Keep to one line; link, don't explain.
3. **Render the map and the fallback.** Generate the SVG with a Python layout (layered/Sugiyama-lite: chapter bands, longest-path layering, no library), emit it via `{{FIG:concept-map.svg}}`, and add the `<details>` edge list. Test at 1440, 768, 390 and in print.

### Subtasks

#### N06.1 — Edge model (≈5 h)

1. Extract concept ids, labels, chapters and current anchors from `concepts.json` + the built TOC.
2. Write the edge list by walking the document: for each concept, ask "which earlier concept does a student need to understand this?" Record only edges that are *teaching* prerequisites, not mere mentions.
3. Validate: no cycles, every node reachable from ch1, every edge's endpoints exist; assert in `audit_claims.py`.

#### N06.2 — Prerequisite lines in 16 chapters (≈5 h)

1. Add the line to the chapter header in the section sources (one HTML pattern, styled minimally — no new box, no icon).
2. Review each for action language and for correct anchors; check that no line points forward (a prerequisite cannot be later in the document).
3. Cross-check against the concept map: every incoming edge must appear in the line or be consciously omitted (record omissions in `concepts.json` as `edge_omitted: true`).

#### N06.3 — Map rendering (≈7 h)

1. Write `build/gen_concept_map.py` (layered layout, fixed canvas 1000×1400, chapter bands as thin rules, node labels at 11 px minimum, edges as 0,6 px curves with arrowheads only on hover).
2. Emit the SVG + the `<details>` table; add a print variant (single page, A4 landscape) so the map is usable on paper.
3. Add the mobile fallback (chapter list with counts) and verify no horizontal overflow at 390 px.

### Acceptance

- `grep -c 'Pirms šīs nodaļas' …` = 16;
- SVG has `<title>`, `<desc>`, and a sibling `<details>` edge table;
- no overflow at 390 px; map prints on one page;
- `audit_claims.py --check` asserts node/edge counts.

---

## N07 — One calculation component, used everywhere

| | |
|---|---|
| **Wave** | B — Explanation |
| **Priority** | P1 |
| **Effort** | M (≈2 days) |
| **Risk** | Low–medium (mechanical, many edits) |
| **Axis** | clarity, consistency, exam technique |
| **Skills** | `impeccable`, `cognitive-deload-auditor` |
| **Files** | `build/sections/07_ch7.html`, `08_ch8.html`, `10_ch10.html`, `11_ch11.html`, `12_ch12.html`, `16_ch16.html`, `build/style.css` |
| **Findings** | C-03, C-09, A-01 (guard-digit claims) |

### Context

There are ~40 worked calculations. They are individually good and structurally *similar but not identical*: some show `Ievade → Starpvērtība → Atbilde`, some show `Formula → Aprēķins → Rezultāts`, some inline the intermediate in prose, and the guard-digit display is inconsistent (`1,0334` in one place, `1,033` as the answer, `147,0000` vs `147` in another). Students copy the format they see first; when the format varies, they infer that the rules vary.

### Definition of Done

- [ ] A single component `<div class="calc">` with three labelled rows: **Dots** (inputs + units + significant figures), **Starpvērtība** (guard digits, labelled as such), **Atbilde** (rounded, with the rounding rule named) — plus an optional **Pārbaude** row (dimensional or order-of-magnitude check).
- [ ] All ~40 calculations use it; no calculation remains in prose-only form.
- [ ] Each `calc` declares `data-rule="add|mul|mixed|mean"` and `data-limiter="…"` (the operand that limits precision); a checker asserts the declared rule matches the displayed rounding.
- [ ] The component is print-safe (three rows, no background fill beyond one tone step, no icons) and collapses to a single column at 390 px.
- [ ] Recalling a calculation in ch15's answer uses the same component, so a student sees the identical format in study and in test review.

### Substeps

1. **Inventory.** Script: find every `<table>` or `<p>` that contains `=` plus a unit, plus every `class="instrument"` output; classify as full-worked, abbreviated, or inline. Output `build/calc_inventory.csv`.
2. **Design the component once.** Write the HTML pattern, CSS (three-row grid, tabular numerals, labels in `--ink-2`, answer in `--ink` with the accent used only for the rule name), and the print rules. Prototype on one calculation (12.4, the NaCl density) and review it at 1440/390/print.
3. **Migrate and enforce.** Convert the inventory in chapter order, one chapter per pass, checking that the numbers are unchanged and that the declared rule matches. Add the checker; the task is not done until the checker reports 0 mismatches.

### Subtasks

#### N07.1 — Component design and prototype (≈6 h)

1. Define the four rows and the typographic hierarchy; ensure the "Starpvērtība" row is visually subordinate but never hidden (it is the pedagogical point).
2. Prototype on one additive case (ch7 mean) and one multiplicative case (ch10 concentration), plus one mixed case (ch8), to prove the component survives all three rule types.
3. Write the CSS with tokens only (no new sizes outside `--text-*`, no new spacing outside `--space-*`), and screenshot at 1440, 768, 390 and in print.

#### N07.2 — Migration in chapter order (≈8 h)

1. Convert ch7–ch8 first (statistics and sig figs), because they define the vocabulary the rest uses.
2. Convert ch10–ch12 (calibration, half-life, solution), watching for guard-digit drift; recompute each answer with the existing checkers and diff.
3. Convert the ch15 answer blocks and the quickref formulas that show a worked number, so the two surfaces agree.

#### N07.3 — The rule/limiter check (≈4 h)

1. Parse every `.calc`, extract the displayed numbers, and recompute with Python `Decimal` at the declared precision; compare the rounded strings.
2. Assert `data-rule` vs the operation symbols present (`+`/`−` ⇒ add; `×`/`/` ⇒ mul; both ⇒ mixed) and `data-limiter` is one of the declared inputs.
3. Add the check to `check_all.sh` and to the change log as a new defence (D-number).

### Acceptance

- `grep -c 'class="calc"'` equals the inventory count ± 0;
- `python3 -I build/check_calc.py --check` → 0;
- screenshots show identical structure across ch7/8/10/11/12;
- print pages containing calcs show no split rows (`break-inside: avoid`).

---

## N08 — Language polish: em dashes, metaphors, sentence rhythm

| | |
|---|---|
| **Wave** | B — Explanation |
| **Priority** | P1 |
| **Effort** | M (≈1,5 days) |
| **Risk** | Low (reviewable line edits) |
| **Axis** | prose quality, Latvian style |
| **Skills** | `polish`, `impeccable` (reading), `cognitive-deload-auditor` |
| **Files** | all `build/sections/*.html`, `build/sections/98_quickref.html` |
| **Findings** | B-01, C-09, A-06 |

### Context

Measured: **96 prose em dashes** (110 in markup, 131 raw with JS/index). The change log claims zero. Of the 96, roughly half are legitimate (`—` as a table placeholder, formula labels `(20,10 + 20,24) / 2 — Vidējais…`, step titles `1. solis — …`). The other half are rhetorical and are the strongest "generated prose" signal in the document. Alongside them: metaphor drift (`ceļš`, `karte`, `plūsma`, `kāpnes`, `telpa`), and a handful of long sentences that survived v1's line edit.

This task is deliberately *not* "delete all em dashes". It is: classify, keep the functional ones, rewrite the rhetorical ones, and make the rule explicit so future edits do not reintroduce them.

### Definition of Done

- [ ] `build/emdash_audit.csv` classifies every `—` as `placeholder` (table cell), `label` (formula name or step title), `quote` (inside `data-quote`), or `rhetorical`.
- [ ] All `rhetorical` occurrences are rewritten (target: 0); placeholders and labels are kept and are visually distinct (placeholders centred, labels after a bold phrase).
- [ ] `lint.mjs` em-dash warning count drops to ≤ 2× the number of functional uses, and the change log states the real number with its classification counts.
- [ ] Metaphor set reduced to at most one defined use each (see N03); the survivor is defined at first use.
- [ ] Sentences > 40 words: 0 in prose (table cells exempt); paragraphs > 90 words: ≤ 3, each justified in `build/long_paras.md`.
- [ ] A 10-line style sheet (`build/style_guide_lv.md`) records the rules so the next editor does not undo them.

### Substeps

1. **Classify.** Script the extraction with context (±80 chars) into CSV; review all 96 by hand (it takes ~45 minutes and is the whole task's value). Anything ambiguous is `rhetorical` by default.
2. **Rewrite.** For each rhetorical dash, choose a full stop, a comma, a colon, or a restructure. Prefer two sentences over one clause chain. Do not replace `—` with `–` or `...`; that is a tell in a different costume.
3. **Style sheet + gate.** Write the rules, add a lightweight checker (regex for `\s—\s` outside placeholders/labels/quotes) and wire it into `check_all.sh`.

### Subtasks

#### N08.1 — Classification (≈3 h)

1. Extract and classify; store the CSV with `id`, `chapter`, `context`, `class`, `decision`.
2. Check the borderline families: ranges (`5–10`), minus signs, table placeholders, formula labels. Any range written with `—` becomes `–`; any minus becomes `−`.
3. Count per chapter and identify the three chapters with the highest density (they are the ones written fastest).

#### N08.2 — Rewrite pass (≈6 h)

1. Rewrite the top-density chapters first; after each chapter, re-read the section aloud (or via TTS) to catch rhythm damage.
2. Remove the "not X, but Y" construction where it repeats more than twice per chapter (a strong tell); replace with a direct claim.
3. Re-check every rewritten sentence for factual drift against the source lines — a rewritten sentence must not add a claim.

#### N08.3 — Style sheet and gate (≈3 h)

1. Write `style_guide_lv.md`: dash policy, quote policy („ “ outer, ‘ ’ inner), number/unit spacing, term capitalisation, sentence-length ceiling, metaphor budget.
2. Implement `build/check_style.py` with the three mechanical rules (rhetorical dash, double space, space before unit) and document the two judgement rules (sentence length, metaphor budget) as review items.
3. Update the change log with the real counts (before/after) and add the style sheet to `build/MANIFEST.md`.

### Acceptance

```bash
python3 -I build/build_doc.py
python3 -I build/check_style.py --check     # 0 rhetorical dashes
node workspace_skills/design-taste-frontend/scripts/lint.mjs Master_2_tema_merijumi_un_grafiki.html | tail -5
```
Expected lint: no em-dash warning, or a warning count equal to documented functional uses with a `taste-skill-ignore` justification.

---

## N09 — Retrieval, interleaving and a spaced-review schedule

| | |
|---|---|
| **Wave** | B — Explanation |
| **Priority** | P1 |
| **Effort** | M (≈2 days) |
| **Risk** | Low |
| **Axis** | study efficacy |
| **Skills** | `cognitive-deload-auditor`, `learn-then-test`, `interactive-study-guide` (patterns only) |
| **Files** | `build/sections/01_ch1.html`, `15_ch15.html`, `build/concepts.json`, `build/build_recall.py`, new `build/spacing.json` |
| **Findings** | C-08, C-06, A-05 |

### Context

127 closed prompts, an exam mode, filters by chapter/concept/mark — and no answer to *"what should I review today?"*. Two gaps:

1. **Spacing** — everything is first-pass practice. A 1/3/7-day schedule, expressed as a static plan plus a "due" view in the workspace, converts the existing prompts into a retention system without gamification.
2. **Interleaving** — chapter 15 has an H group of "mixed" questions, but the exam mode already draws stratified sets. A small explicit interleaved set (12 questions spanning ch4/5/8/10/12) with a stated rationale would teach *switching*, which is what the test actually demands.

Also `concepts.json` is stale (113 vs 127), so any schedule keyed to concepts is currently keyed to a wrong inventory (fixed by N01, consumed here).

### Definition of Done

- [ ] `build/spacing.json` maps each recall id to a concept id and a chapter, generated (not typed) by `build_recall.py`.
- [ ] The workspace gains a **"Šodien jāatkārto"** filter (due queue) computed from mark history *in memory* by default, and from storage only with consent. No points, no streak, no badge.
- [ ] A **static** one-page schedule exists in ch1 or ch15 (`<details>` closed): day 0 / day 1 / day 3 / day 7 with explicit *which* sets to run, printable, no JS.
- [ ] A 12-item interleaved set exists (`id="set-interleaved"`) with a one-sentence rationale and a note that it is not a chapter test.
- [ ] Concept coverage per chapter is printed in ch15 (counts generated), so a student can see which chapter has the thinnest retrieval coverage.
- [ ] `learn-then-test` patterns are used only where they do not add scoring; the design contract's no-gamification rule is restated in the task's change-log entry.

### Substeps

1. **Rebuild the map.** After N01/N03, regenerate the concept↔recall map; verify 127/127 items have a concept and a chapter; list uncovered concepts (those with no prompt) and either add prompts or record them as "explained only".
2. **Design the schedule.** Choose the intervals (1/3/7 plus a pre-test pass), define what "done" means per session (attempt → open answer → re-mark), and express it as a printable plan that references existing sets rather than creating new content.
3. **Implement the due queue + interleaved set.** Extend `applyFilters` with a `due` mode computed from `data-mark` and a per-item `data-last` (memory only unless consent); add the interleaved set as a filtered view with a fixed id list in `spacing.json`.

### Subtasks

#### N09.1 — Concept↔recall coverage (≈5 h)

1. Regenerate `concepts.json` from the built HTML (ids, chapters, concepts, marks) and diff against the old file; record the 14-item delta.
2. Identify concepts with zero prompts; add at most 6 new prompts where the concept is exam-critical (mixed sig figs, tolerance, extrapolation, offset half-life, density inversion, unit chain), and log them.
3. Add a coverage table to ch15 (chapter × concept count) generated by the build, not typed.

#### N09.2 — Spaced schedule (≈4 h)

1. Write the one-page plan with four sessions and explicit sets (e.g. *«1. diena: 8. nodaļas D grupa + 12. nodaļas G grupa»*), each ≤20 minutes.
2. Add a "why spacing works" three-sentence note (retrieval strength vs storage strength) marked «papildinājums», with no invented statistics.
3. Print-check the one-pager: it must fit one A4 page with the existing type tokens.

#### N09.3 — Due queue and interleaved set (≈5 h)

1. Add `data-last` (ISO date, memory only) updated when a mark changes; compute due = last + interval according to the recalled count.
2. Add the `due` filter option and the count; ensure the queue is empty on first load and explains itself («Vēl nav atzīmju — sāc ar 8. nodaļu»).
3. Author the 12-item interleaved set, verify every answer is closed and correct, and add it to the exam-mode pool as an option (*«Jaukts komplekts»*) — not as the default.

### Acceptance

- coverage table generated (0 typed numbers);
- due queue empty on fresh load, non-empty after marking with a past date (test by injecting `data-last` in devtools);
- interleaved set: 12 items, 6 chapters, answers closed;
- print one-pager fits one page.

---

## N10 — Anti-slop restyle: the first screen and the accent system

| | |
|---|---|
| **Wave** | C — Design |
| **Priority** | **P1** |
| **Effort** | L (≈3 days) |
| **Risk** | Medium (visible change, subjective review) |
| **Axis** | redesign, anti-slop, hierarchy |
| **Skills** | `design-taste-frontend` (`tells.md`, `lint.mjs`, `inspect.mjs`), `impeccable`, `blueprint-spec-sheet` (title-block idea only) |
| **Files** | `build/sections/00_front.html`, `build/style.css`, `build/sections/01_ch1.html` |
| **Findings** | D-01, D-02, D-03, D-04, D-07, D-08 |

### Context

The design is close to the §6 contract and far from generic slop — but three patterns remain from the "editorial hero" family:

1. **The `01–05` numeral grid.** §6.2 explicitly bans `01 / 02` numbering and "counters styled as ornament". The five outcomes are the most important orientation device in the document, and they are currently presented as a feature grid with decorative numerals.
2. **The metadata strip.** *«Avoti: 5 kursa PDF · Pārbaudīts: … · Valoda: latviešu»* is a status-badge row in prose clothing; it also carries a stale date (A-04).
3. **The 56 px title.** `clamp(36px, 4vw, 56px)` with forced two-line break consumes ~30 % of a 1440×1000 first screen and reads as a landing hero.

Plus: one accent (`#A61E4D`) doing nine jobs (links, glossary links, chapter numerals, role labels, buttons, focus, active TOC, tool emphasis, checkbox), and role blocks stacking three deep.

### Definition of Done

- [ ] The outcomes become a **plain linked list or a two-column table** with the code `O1…O5` in `--ink-2` at body size; no oversized numerals, no `01`/`02`, no per-item accent.
- [ ] The metadata strip becomes a **colophon block** placed once (footer/appendix), not in the masthead; the masthead keeps only title, subtitle and one sentence of scope.
- [ ] Title scale: `--text-display` ≤ 40 px at 1440, ≤ 32 px at 768, single logical line if it fits, no forced `nowrap` breaks that fight the text.
- [ ] Accent is split into two tokens with distinct jobs: `--accent` (interaction: links, focus, buttons, active state) and `--accent-quiet` (structure: chapter numerals, role labels at ≥ 4,5:1 on ground). Visual audit shows at most **one** accent-bearing element per 400 px of reading column.
- [ ] Role blocks: at most two visible per 900 px screen height; a third is merged into prose or moved into `<details>`.
- [ ] Figures and schematics are visually distinguishable from icons: data figures get axes + gridlines, schematics get a 1,5 px stroke and no grid (see N11/N15).
- [ ] `lint.mjs` → 0 FAIL; `inspect.mjs` warnings do not increase; screenshots at 1440/768/390 reviewed side by side with the previous build.

### Substeps

1. **Re-read the first screen as a stranger.** Take a 1440×1000 screenshot and annotate what a reader learns in 5 seconds. Then write the intended reading order (title → scope → outcomes → chapter 1). Everything on the screen that does not serve that order is removed or moved.
2. **Rebuild the masthead.** Implement the new structure (title block + scope sentence + outcomes list + a single plain link into ch1). Remove the metadata strip; move provenance to the colophon. Adjust type tokens.
3. **Split the accent and audit its uses.** Introduce `--accent-quiet`, migrate structural uses, then run a visual audit: count accent elements per screen, remove the ones that are decorative rather than functional. Review role-block stacking and merge where needed.

### Subtasks

#### N10.1 — Masthead rebuild (≈8 h)

1. Write three static variants (list, table, and a "syllabus index" with left rule) and screenshot each at 1440 and 390. Choose on reading speed, not taste.
2. Implement the winner in `00_front.html` + CSS; ensure the outcomes still link to their chapters and still carry the "where in this document" mapping.
3. Remove the metadata strip; add the colophon placeholder (content landed in N13) and verify the first screen now reaches chapter 1's heading within one viewport.

#### N10.2 — Type and accent system (≈8 h)

1. Set `--text-display` to 40/32/28 px across breakpoints, re-check the title's line breaks at 320/390/768/1024/1440, and remove `nowrap` spans that cause hyphenless overflow.
2. Add `--accent-quiet` (a desaturated tint of the accent or a neutral with a hue nudge) and migrate chapter numerals, role labels and TOC markers; keep `--accent` for interaction only.
3. Audit focus, hover, active, and selected states so interaction remains unambiguous; verify contrast for both tokens in light and dark.

#### N10.3 — Density and role-block budget (≈6 h)

1. Count role blocks per chapter and per viewport height (script: `getBoundingClientRect` over each `.role`), list the screens with ≥3.
2. Merge the weakest third into prose (keep label + one sentence), and move the rest into `<details>`; preserve all factual content.
3. Re-screenshot and compare against the baseline on a 3-up contact sheet; record what changed in the change log with the contract clause cited.

### Acceptance

- 0 occurrences of `class="o"`-style oversized numerals in the masthead (or a replaced pattern);
- `--text-display` max ≤ 40 px (grep the CSS);
- accent audit table in the task notes: element → token → job → kept/removed;
- lint 0 FAIL; screenshot pair archived under `build/shots/v2/`.

---

## N11 — Retexture: one material system, no decorative elevation

| | |
|---|---|
| **Wave** | C — Design |
| **Priority** | P1 |
| **Effort** | M (≈2 days) |
| **Risk** | Low |
| **Axis** | retexture, consistency |
| **Skills** | `impeccable`, `design-taste-frontend` (`tells.md` §soft shadow), `synoptic-matrix-architect` (table texture) |
| **Files** | `build/style.css`, `build/sections/*.html` (class usage only), `build/figures/glassware.html` |
| **Findings** | D-05, D-06, D-08, H-06 |

### Context

"Texture" here means the *material vocabulary*: surfaces, rules, fills, strokes, and how they combine. Today it is inconsistent in four ways:

- 6 `box-shadow` declarations, of which 3 are functional (popover, dialog, sticky bar) and 3 are decorative panels that should use a tone step instead;
- role blocks come in four variants with different fills, borders and left bars, so the eye cannot learn one rule;
- table zebra/hover/selection are defined per table class rather than globally;
- the vessel plate, the figure plates and the role blocks use three different border/fill combinations for what is conceptually the same "inset card".

The design contract says: elevation by tone step only; hairlines only where they are data. The retexture makes that literal.

### Definition of Done

- [ ] A documented material scale with exactly four surfaces (`--ground`, `--surface`, `--surface-2`, `--surface-3` if needed) and one rule weight (`--line`; `--line-strong` for data only), used consistently.
- [ ] `box-shadow` appears only on: popover, dialog/panel, sticky controls. Each has a `taste-skill-ignore` comment naming the function. Count ≤ 3 + any print-specific needs.
- [ ] Role blocks share one geometry (left bar width, padding, label position) and differ only in the bar colour/label — one rule the eye learns once.
- [ ] Table texture is global: header rule, row hairline, no zebra, hover only on interactive rows (workspace lists), focus ring on the scroll container.
- [ ] All "inset" containers (`.figure-data`, `.workspace__panel`, `.calc`, `.quickref-section`) use the same surface/rule pair.
- [ ] Print texture: surfaces collapse to white with a 0,5 pt rule or a 5 % grey fill that survives laser printing; verified on 3 sample pages.
- [ ] A texture spec sheet (`build/texture_spec.md`) with a screenshot of each primitive, so future components cannot invent a fifth.

### Substeps

1. **Inventory the primitives.** List every rule/fill/shadow in `style.css` with its selector, value and purpose; classify as data, structure, or decoration. This is ~60 declarations and is the heart of the task.
2. **Define and apply the scale.** Write the four surfaces and two rule weights, then migrate components class by class, deleting the local overrides. Rebuild after each class so a regression is attributable.
3. **Print and dark verification.** Render the three modes (light, dark, print) for a page that contains every primitive; compare tone separation; adjust the print greys so nothing disappears.

### Subtasks

#### N11.1 — Primitive inventory (≈4 h)

1. Extract all `border`, `background`, `box-shadow`, `outline` declarations with selectors into `build/texture_inventory.csv`.
2. Classify each; flag the decorative shadows and the local table overrides.
3. Photograph the current state (3 screenshots: role blocks, a table, the vessel plate) for the before/after record.

#### N11.2 — Migration (≈8 h)

1. Introduce the tokens and delete the decorative shadows; replace with tone steps. Verify no component loses its boundary.
2. Unify role-block geometry and inset containers; reduce the variants from 4+3 to 4+1.
3. Normalise table texture globally; remove per-table zebra/hover; ensure `.table-scroll` focus is visible.

#### N11.3 — Print and dark (≈5 h)

1. Render a "primitive sampler" page in light, dark and print; check 5 %/8 % grey separation on paper (use the PDF raster, not the screen).
2. Fix any primitive that disappears in print (e.g. `--surface-2` on ground) by switching to a rule or a darker grey.
3. Update the changelog and the texture spec.

### Acceptance

- `grep -c 'box-shadow' build/style.css` ≤ 3 (+ documented exceptions);
- `grep -c 'background: var(--surface' build/style.css` consistent with the four-surface scale;
- sampler page prints with all primitives visible.

---

## N12 — Typography v2: Latvian micro-typography and numeric alignment

| | |
|---|---|
| **Wave** | C — Design |
| **Priority** | P1 |
| **Effort** | M (≈2 days) |
| **Risk** | Low |
| **Axis** | restyle, legibility, correctness |
| **Skills** | `impeccable`, `polish` (LV typography), `print-css-alchemist` |
| **Files** | `build/style.css`, `build/build_doc.py` (NBSP pass), all sections (character fixes), `build/figures/*.svg` (text sizes) |
| **Findings** | B-06, B-07, H-05, J-03 |

### Context

The type system is already tokenised (8 roles, print pt set) — a real strength. What remains is *micro*-typography, where Latvian and chemistry both have rules:

- decimal comma is correct everywhere (checked), but the minus sign is sometimes `-` and sometimes `−`, and ranges use `-` where `–` belongs;
- NBSP insertion is a regex in `build_doc.py` (J-03) that is correct today but fragile; it should be replaced by an asserted pass with a report;
- tabular figures: `font-variant-numeric: tabular-nums` is applied to `.num, table, math, input, output` — but the tools' output strings and the SVG axis labels are not covered;
- quotes: `„ … “` is used in prose; check the nested and the inch/arcminute cases;
- variables in prose are italic (`<i>`) but some quantities are upright (e.g. units, `pH`, `R²`), and the rule is not stated;
- SVG text sizes are in user units (H-05) and will break any mobile scaling fix;
- hyphenation: Latvian long compounds (25+ characters) at 390 px can overflow; `hyphens: auto` with `lang="lv"` needs verification in Chromium (hyphenation dictionaries may be absent).

### Definition of Done

- [ ] A written micro-typography rule set exists (`build/type_rules.md`): minus, ranges, quotes, NBSP, italics for variables, upright for units and function names, tabular figures, decimal comma, thousands separator (NBSP), unit case.
- [ ] `check_style.py` enforces the mechanical subset: `-` used as minus, `-` used as a range, space before unit, double space, `μ` vs `µ`, `x` used as multiplication.
- [ ] `tabular-nums` covers tables, `.calc`, tool outputs, SVG tick labels and the workspace counters (verified by computed style, not by reading CSS).
- [ ] The NBSP pass becomes an **asserted** pass: it reports how many insertions it made, and `--check` fails if a number/unit pair in a text node lacks NBSP after the pass.
- [ ] No horizontal overflow at 320 px caused by an unbreakable compound; the five longest compounds are listed with their break opportunities.
- [ ] SVG text has a declared minimum rendered size (11 px at 390 px) and the figures' `<text>` uses a class referencing `--fig-text` tokens instead of inline font sizes.

### Substeps

1. **Rule set first.** Write the rules with examples from the document (one positive, one negative each). This prevents 200 ad-hoc edits turning into 200 inconsistencies.
2. **Mechanical fixes.** Apply the enforceable rules via script where possible (minus, ranges, μ, NBSP), verify with the checker, and hand-fix the remainder (italics, quotes).
3. **Numbers and SVG.** Apply tabular numerals globally, then re-specify SVG text sizes against the new mobile scaling so labels stay legible.

### Subtasks

#### N12.1 — Minus, ranges, quotes, units (≈5 h)

1. Scan for `\d-\d`, `\d - \d`, `\d,\d-`, and `-` before a digit in prose; convert to `−` (U+2212) for negatives and `–` (U+2013) for ranges. Exempt `data-quote` spans.
2. Audit quotes: outer `„ “`, inner `« »` (or the reverse, but pick one and apply), and confirm the glossary's English terms are not double-quoted.
3. Verify units: case (`mL`, `L`, `s`, `min`, `h`, `d`, `°C`, `K`), NBSP before unit, no plural `s` on symbols, `mg/100 g` spacing.

#### N12.2 — Tabular figures and math (≈5 h)

1. Apply `font-variant-numeric: tabular-nums lining-nums` to `.num`, `table`, `.calc`, `.instrument output`, `.workspace__count`, and SVG tick labels via a class.
2. Define the italic/upright rule and apply it: variables italic, units upright, `pH`/`R²`/`LOD` upright, chemical formulas upright with subscripts.
3. Check the MathML blocks' font fallback (14 blocks) renders consistently in Chromium; note any fallback in the README.

#### N12.3 — Break opportunities and SVG type (≈5 h)

1. List the 20 longest words/compounds used in prose; test each at 320 px inside its container; add `hyphens: auto` where it helps and `overflow-wrap` only as a last resort.
2. Re-specify SVG type: `--fig-text: 12` (user units) with a scale that keeps ≥11 px rendered at 390; update all figure generators.
3. Render the print edition; check that SVG labels are ≥7 pt and that axis numbers are tabular.

### Acceptance

```bash
python3 -I build/check_style.py --check            # 0
grep -c 'tabular-nums' build/style.css             # ≥ 4 (base + components)
# computed check
node -e "..."   # tabular-nums on table, .calc, output
```
Plus a 320 px screenshot with no overflow.

---

## N13 — Print edition v2: pagination, a page-numbered TOC, a colophon, an honest head

| | |
|---|---|
| **Wave** | C — Design |
| **Priority** | P1 |
| **Effort** | L (≈3 days) |
| **Risk** | Medium |
| **Axis** | print, provenance |
| **Skills** | `print-css-alchemist`, `pdf-vector-surgeon` |
| **Files** | `build/style.css` (`@media print`, `@page`), `build/build_doc.py` (print TOC), `build/sections/99_footer.html`, `16_ch16.html` |
| **Findings** | G-01…G-06, D-09, D-10 |

### Context

117 A4 pages. Measured defects: page 62 ~40 % blank, page 117 ~60 % blank, no printed page-numbered TOC, no colophon, running head says **«RSU · 2026»**. The print-only quick reference duplicates formulas from the chapters (D-09) and is maintained by hand.

A printed reference must be navigable without a browser. That means: a TOC with page numbers, a colophon, consistent page furniture, and pagination that does not waste paper.

### Definition of Done

- [ ] A printed TOC with **real page numbers** exists (generated at build time by rendering the PDF and mapping anchors to pages, then injecting the numbers into a print-only TOC).
- [ ] Blank-space pages ≤ 5 % of the edition; no page is more than 25 % empty except intentional section-end pages (max 3, each labelled in the source).
- [ ] A colophon page (last or first): what the document is, what it is not, edition/date/build SHA, how numbers were verified, source list pointer, licence/provenance, and the correct attribution (no institutional implication).
- [ ] Running head/foot: left = document title; right = **«2. tēma · <edition date>»** (not `RSU`); footer = «Lpp. n / N» and the build SHA on the colophon only.
- [ ] The quick reference is **generated** from chapter sources (single source of truth) or explicitly marked as a frozen extract with its own version and a "verify against ch. X" note. It must not silently diverge.
- [ ] Print modes are explicit: **Study edition** (answers open) and **Question edition** (answers closed), selectable by a build flag; both paginate cleanly. The default stays Study.
- [ ] PDF size ≤ 3,2 MB for 117±5 pages (currently 2,6 MB; the guard prevents a runaway).

### Substeps

1. **Measure pagination.** Write `build/print_report.py`: for each page, compute ink coverage / last-y position from `pdftotext -bbox` and report pages with >25 % trailing blank. This gives an objective list to fix.
2. **Fix breaks and flow.** Apply `break-inside: avoid` surgically (not globally), `break-before` only for the 3 intentional section starts, `orphans/widows: 3`, and move figures/tables to avoid half-empty pages. Re-measure iteratively (each pass is 2 minutes).
3. **Generate the TOC, the colophon and the honest head.** Add the two-pass build (render → map anchors → inject page numbers → re-render), write the colophon, change the running head, and add the print-mode flag.

### Subtasks

#### N13.1 — Pagination measurement and repair (≈10 h)

1. Build `print_report.py` (uses `pdftotext -bbox-layout`; no new dependency) and record the baseline: pages with blank area, widows, orphan headings.
2. Fix the top 10 offenders by reordering content within the chapter (figure before paragraph), not by shrinking type.
3. Re-measure until ≤5 % waste; archive the before/after tables.

#### N13.2 — TOC with page numbers and colophon (≈8 h)

1. Implement the two-pass print: first render collects `id → page` via `pdftotext` anchors or a JS `pageNumber` probe; second render writes the numbers into a print-only TOC.
2. Author the colophon (scope, non-scope, verification method, sources, build SHA, attribution caveat, no RSU implication).
3. Verify the TOC numbers against 20 random anchors by opening those pages.

#### N13.3 — Edition modes and quickref provenance (≈6 h)

1. Add `PRINT_MODE=study|questions` to `build_doc.py`; in `questions` mode, `<details>` stay closed in print and the answer sheet is not generated.
2. Replace the hand-maintained quickref with generated extracts (or add a version + "verify against" line and a checker that diffs key strings against the chapters).
3. Verify both modes' page counts and that no page is blank in either.

### Acceptance

```bash
python3 -I build/build_doc.py --print-mode study
google-chrome --headless --print-to-pdf=... Master_2_tema_merijumi_un_grafiki.html
pdfinfo out.pdf | grep Pages
python3 -I build/print_report.py out.pdf     # waste ≤ 5 %, TOC anchors resolve
```

---

## N14 — Narrow screens and input modalities (the measured breakage)

| | |
|---|---|
| **Wave** | C — Design |
| **Priority** | **P0** |
| **Effort** | M (≈2 days) |
| **Risk** | Medium |
| **Axis** | responsive, accessibility, usability |
| **Skills** | `break-ui` (worst-case data), `impeccable`, `design-taste-frontend` (`inspect.mjs` side-scroll check) |
| **Files** | `build/style.css`, `build/sections/*.html` (table classes), `build/app.js` (search panel), `build/figures/*.svg` |
| **Findings** | F-01, F-02, F-03, F-05, F-06, H-05 |

### Context

Measured at 390×844 with Chromium 156:

- the top bar becomes **three stacked full-width buttons** plus a ~140 px search field clipped at the left edge — the first thing a phone user sees is a broken control cluster;
- **11 figure regions** are forced to `min-width: 820px`, so every data figure must be panned sideways;
- **10 tables** do not stack (7 pinned matrices, 3 compact reference tables) — the pinned ones are arguably fine, the three compact ones are not;
- `scope="row"` exists on 7 cells in 75 tables;
- there is no "back to chapter top" affordance.

This is the only *P0* design task, because it is a functional failure, not a taste question.

### Definition of Done

- [ ] Top bar at ≤720 px: one row, brand left, search expands to fill, actions collapse into a single labelled **menu** (or icon+label) that opens a small panel; total height ≤ 72 px.
- [ ] Every figure scales to the container width (no `min-width`); labels remain ≥11 px rendered; if a figure genuinely cannot scale, it gets a deliberate "open full size" link instead of silent scrolling.
- [ ] The three compact tables stack; the 7 pinned matrices keep horizontal scroll **with a visible affordance** (edge fade + "ritiniet" hint with `aria-hidden`) and a sticky first column.
- [ ] `scope="row"` added wherever the first cell is a row header (matrix tables), and a checker reports the count.
- [ ] A "↑ Nodaļas sākums" link appears at the end of each chapter (and in the sticky bar on mobile).
- [ ] Tested at 320, 360, 390, 414, 768, 1024, 1440; no horizontal document overflow (measured `scrollWidth === clientWidth`); screenshots archived.
- [ ] Worst-case Latvian compounds do not overflow (see N12.3).

### Substeps

1. **Reproduce and record.** Script the seven viewports, capture `scrollWidth`, list every overflowing element and every figure's computed width. Store as `build/responsive_report.json` — this becomes the regression baseline.
2. **Fix the top bar and the figures.** Rebuild the bar for ≤720 px; remove `min-width: 820px` and give SVG a fluid `width: 100%; height: auto` with a `viewBox` that already exists. Re-check label sizes; bump SVG type where needed.
3. **Tables, row scopes, and the chapter-top link.** Classify the 10 non-stacking tables, stack the three compact ones, add sticky first columns + affordance to the pinned ones, add `scope="row"`, and add the chapter-top link.

### Subtasks

#### N14.1 — Top bar (≈5 h)

1. Design the ≤720 px bar: 48 px height, search as the primary control (full width on a second line only if needed), actions behind a single "Izvēlne" disclosure that is keyboard-operable and closes on Esc/outside click.
2. Implement with `<details>`-based menu (no JS dependency) or a small JS enhancement; verify focus order and that the search still opens its panel at the right position.
3. Test at 320/360/390 with long Latvian labels («Tumšais režīms» is the longest).

#### N14.2 — Figures and tables (≈8 h)

1. Remove the `min-width` rule; set fluid SVG sizing; verify each of the 12 figures at 390 and 320; raise SVG type where a label falls below 11 px.
2. Stack the 3 compact tables (`Pamatvienības…`, `Aprēķinu formulas…`, `Trauku lietojums…`) with `data-label`; keep the pinned matrices but add a sticky first column and an edge-fade affordance.
3. Add `scope="row"` to matrix row headers and a checker that reports the remaining tables without it.

#### N14.3 — Navigation and worst case (≈5 h)

1. Add the chapter-top link (after the last section, before the next chapter) and a mobile-only sticky "Sadaļas" button opening the TOC details.
2. Run the `break-ui` worst-case set: 25-character compounds, `mg/100 g` cells, a 4-digit number in a 3-column table, an empty cell.
3. Archive 7 screenshots + the JSON report; add the report to the release checklist.

### Acceptance

```bash
node build/responsive_check.mjs   # asserts scrollWidth == clientWidth at 7 widths, figure widths ≤ container
```

---

## N15 — SVG component library and figure contract

| | |
|---|---|
| **Wave** | D — SVG |
| **Priority** | P1 |
| **Effort** | M (≈2 days) |
| **Risk** | Low |
| **Axis** | figures, consistency, accessibility |
| **Skills** | `svg-spatial-occlusion` (structure), `mook-visual-compendium` (numbering discipline), `pdf-vector-surgeon` (print QA) |
| **Files** | new `build/figures/_scaffold.svg`, new `build/figures/_tokens.css` (SVG-side), `build/gen_figures.py`, `build/style.css` |
| **Findings** | H-03, H-04, H-05, D-08 |

### Context

21 SVGs, all with `<title>`+`<desc>` (good), all 1 px strokes (bad for hierarchy), captions carrying provenance (H-03), `<desc>` restating the title (H-04), and type in user units (H-05). Builders (`gen_figures.py`) emit path coordinates with 17 decimal places (`158.92000000000002` seen in the markup) — harmless but noisy, and a sign there is no numeric formatting step.

A library fixes this once: one scaffold, one type scale, one stroke scale, one label-placement rule, one caption/provenance split, one data-table alternative convention.

### Definition of Done

- [ ] `_scaffold.svg` defines: `viewBox` grid (8 px minor), margins (24/24/48/64), plot area ≥70 %, title/axis/label/tick classes, stroke classes (`--fig-axis`, `--fig-data`, `--fig-muted`), 2 figure themes (light/dark via `currentColor` + CSS vars).
- [ ] Every figure uses the scaffold; **no inline `font-size`, `stroke-width`, or colour literal** remains in any SVG (`grep` proves it); all styling comes from classes defined in `style.css` under a `figure` block.
- [ ] A figure contract in `build/figure_contract.md`: `<figure>` → `<svg role="img" aria-labelledby>` → `<title>` (what) → `<desc>` (the data and the takeaway, ≥1 sentence with numbers) → `<figcaption>` (caption only: what is plotted, units, n) → `<p class="source-line">` (provenance) → optional `<details class="figure-data">` (the numbers).
- [ ] `<desc>` quality rule: it must let a reader reconstruct the main reading without seeing the image; a checker enforces ≥ 12 words and ≥ 1 numeral for data figures.
- [ ] Path coordinates are rounded to 2 decimals at generation; a checker fails on > 3 decimals.
- [ ] Print: stroke weights map to ≥0,5 pt at 100 %; gridlines lighten; no colour-only encoding (verify greyscale raster).

### Substeps

1. **Write the scaffold and the contract.** Define the tokens, the classes and the document pattern; prototype by rebuilding one simple figure (the prefix ladder) end to end.
2. **Refactor the generator.** Make `gen_figures.py` emit classes + rounded coordinates + a `<desc>` from a per-figure data structure, so the numbers in the description come from the same data as the paths.
3. **Apply and verify.** Convert the remaining 20 SVGs (N16 does the visual redesign; N15 does the structural conversion), then run the checkers: no literals, desc quality, decimal rounding, print raster.

### Subtasks

#### N15.1 — Scaffold (≈6 h)

1. Author `_scaffold.svg` with a commented example: margins, plot rect, axis lines, tick generator notes, label anchors, a legend slot.
2. Add the CSS block (`figure svg .axis { stroke: var(--fig-axis); stroke-width: 1 }` etc.) and a dark-mode override.
3. Prototype on `prefix-ladder.svg`; screenshot light/dark/print and check label sizes.

#### N15.2 — Generator refactor (≈6 h)

1. Define a Python data model per figure (`title`, `desc`, `series`, `annotations`, `labels`) and a renderer that computes both the geometry and the `<desc>` text.
2. Round all coordinates to 2 decimals; remove the 17-decimal artefacts; assert with a regex.
3. Regenerate all 12 figures with unchanged visual output (pixel-diff against the baseline; accept only sub-pixel differences).

#### N15.3 — Contract enforcement (≈5 h)

1. Write `build/check_figures.py`: requires `role="img"`, `aria-labelledby`, `<title>`, `<desc>` ≥12 words with a numeral for data figures, no inline style attributes, no font-size literals, no >3-decimal coordinates.
2. Add the `<p class="source-line">` split: move provenance out of `<figcaption>` for all 12 figures.
3. Add the figure checklist to the changelog and the release gate.

### Acceptance

```bash
python3 -I build/check_figures.py --check    # 0
grep -c 'font-size=' build/figures/*.svg     # 0
```

---

## N16 — Redraw the 21 existing SVGs so they teach

| | |
|---|---|
| **Wave** | D — SVG |
| **Priority** | P1 |
| **Effort** | L (≈3 days) |
| **Risk** | Medium (visual judgement) |
| **Axis** | figures, explanation |
| **Skills** | `svg-spatial-occlusion`, `artifact-diagramming` (host), `pdf-vector-surgeon` |
| **Files** | `build/figures/*.svg`, `build/figures/glassware.html`, `build/gen_figures.py` |
| **Findings** | H-01, H-02, H-06, D-08 |

### Context

Per-figure problems, measured by looking at the rendered plated and the markup:

| Figure | Problem |
|---|---|
| `burette-readings.svg` | No numbered graduations; no ±0,05 estimate zone; the three readings (0,00 / 5,80 / 19,30) are not marked on the drawing |
| `glassware.html` (9 vessels) | Uniform stroke, no liquid, no TD/Ex, no tolerance, no scale numbers; Erlenmeyer outline has a spout artefact; heights not consistently proportional |
| `meniscus-parallax.svg` | Eye positions exist; the *resulting reading error* is not quantified per position |
| `target-plot.svg` | Three cases exist; the "systematic vs random" mapping to the four quadrants is not labelled |
| `calibration.svg` | Six standards exist; the lemon point at 0,982 is not visibly outside the shaded calibrated range |
| `calibration-residuals.svg` | Residuals plotted; the "random vs curve vs fan" reading is not labelled |
| `half-life-hg.svg` | Ladder exists; the t½ value is not annotated at both halvings |
| `half-life-hydrolysis.svg` | Starts at 115 s (correct); the Δt reading is shown but the "absolute time" trap is not drawn |
| `density.svg` | Line + inversion arrows; the slope's meaning (7,3 mg/mL per %) is not annotated |
| `ci-coverage.svg` | 10 intervals; the one that misses is not labelled with the 95 % interpretation |
| `prefix-ladder.svg` | Good; missing the `µ` vs `m` collision warning |
| `calibration-scheme.svg` | Three steps; arrows are uniform in weight, so the "signal path" hierarchy is flat |
| `read-path.svg` | Six steps; the "back to the other axis" move is ambiguous |

### Definition of Done

- [ ] Every figure is redrawn against the N15 contract and passes `check_figures.py`.
- [ ] Each data figure has: title, axis titles with units, ≥3 numbered ticks per axis, a shaded/annotated calibrated range where relevant, a direct label for the key reading (no legend-only), and a `<desc>` containing the key number.
- [ ] The vessel plate: numbered graduation on the burette and cylinder, a meniscus in the flask and cylinder, `TD`/`Ex` where applicable, tolerance text in the drawing OR an explicit "skatīt matricu" pointer (not both).
- [ ] Stroke hierarchy: axes 1 px, data 1,5 px, annotations 1 px dashed; no figure uses more than 3 stroke styles.
- [ ] Colour: every encoded value also has a shape/line-style redundancy; greyscale raster is readable.
- [ ] Print: all labels ≥7 pt at 100 %; no label collides with geometry (checked on the raster at 150 dpi).
- [ ] Before/after contact sheet for all 12 figures archived under `build/shots/v2/figures/`.

### Substeps

1. **Per-figure spec.** Write a one-page spec per figure (12 pages, or one table with 12 rows): what the reader must be able to *do* after looking, which numbers must be readable, which trap must be visible. This prevents "prettier but no more teachable".
2. **Redraw the data figures.** Regenerate plots from `constants.json` + data tables (N04), add annotations and the calibrated range, and write `<desc>` from the data.
3. **Redraw the glassware + schematics.** Rebuild the 9 vessels on a shared baseline grid (proportional heights, one stroke), add graduations and marks; rebuild the meniscus, burette, target and read-path schematics with the 3-stroke hierarchy.

### Subtasks

#### N16.1 — Data figures (calibration, residuals, half-life ×2, density, CI, prefix) (≈12 h)

1. Spec each figure in one line ("reader must see that 0,982 lies outside 0–30 mg/L"), then implement annotations and the calibrated-range band.
2. Regenerate from data; verify every plotted value against `constants.json`/tables (a checker can dump the coordinates).
3. Add `<desc>` sentences with the key numbers and the takeaway; add/extend the data-table alternative.

#### N16.2 — Glassware plate (≈10 h)

1. Draw on a shared baseline: cylinder, burette, pipettes, flask, beaker, Erlenmeyer, tube, plastic pipette; proportional heights; meniscus in the volumetric flask and cylinder.
2. Add numbered graduations to the burette (0, 5, 10 … with 0,1 minor ticks) and the cylinder; add one calibrated mark (red) where the text says "viena atzīme"; add `TD`/`Ex` text where the matrix mentions it.
3. Remove the Erlenmeyer artefact; check print at 4 mm height for legibility; write the `<desc>` for the plate as a group.

#### N16.3 — Schematics (meniscus, burette, target, scheme, read-path) (≈10 h)

1. Meniscus: add the three eye positions with the resulting offset (Δ reading) quantified in mL.
2. Burette: three readings drawn on the same scale with the estimated digit marked and a zoom inset for ±0,05.
3. Target/scheme/read-path: label the quadrants, give the scheme arrows a hierarchy, and disambiguate the read-path return move.

### Acceptance

- `check_figures.py` 0;
- raster review at 150 dpi: no collisions;
- greyscale readable;
- data-table alternative present for 12/12 data figures.

---

## N17 — Ten new figures that carry ideas the prose cannot

| | |
|---|---|
| **Wave** | D — SVG |
| **Priority** | P2 |
| **Effort** | L (≈3 days) |
| **Risk** | Medium |
| **Axis** | explanation, visual learning |
| **Skills** | `state-scrubber-lab` (static-first), `svg-spatial-occlusion` (label masking where memorisation matters), `mook-visual-compendium` (numbering) |
| **Files** | new `build/figures/*.svg`, `build/gen_figures.py`, sections 02, 04, 06, 07, 08, 09, 10, 12 |
| **Findings** | C-01, C-03, C-06, H-05 |

### Context

Ten ideas are currently prose-only and would be materially clearer as a diagram. Each is listed with the chapter and the job it does. **Rule: a new figure must replace prose, not decorate it** — the paragraph it displaces is deleted or shortened.

| # | Figure | Ch | Job |
|---|---|---|---|
| 1 | Uncertainty budget waterfall | 6 | Show how three ± contributions combine to a total, and why the largest dominates |
| 2 | Error propagation tree | 6/8 | Show how one ± in an input travels to the result (additive vs multiplicative) |
| 3 | Titration curve with equivalence region | 5 | Show what the burette reading is *for*; connect to the 2B Q2 practical |
| 4 | Meniscus zoom inset (± half-division) | 5 | The estimated last digit, at 4× zoom, with "too precise / too coarse" labels |
| 5 | Solution-preparation flow (weigh → dissolve → fill → homogenise → measure) | 12 | Replace the numbered prose flow with a spatial flow that shows the *order constraint* |
| 6 | Significant-figure decision flow | 8 | Replace the textual decision tree with a real flowchart (3 decisions, 4 exits) |
| 7 | SD vs SEM sampling picture | 7 | Two distributions: many measurements vs many means, with √n shrinking |
| 8 | Interpolation vs extrapolation zoom | 10 | The calibrated band, the lemon outside it, and what the line "would say" |
| 9 | Unit-prefix number line (log scale) | 2 | Replace the ladder table with a positioned number line 10⁻⁹…10⁹ |
| 10 | Concept map | 1/16 | (Delivered by N06; registered here for numbering) |

### Definition of Done

- [ ] Each figure exists, passes `check_figures.py`, has a `<desc>` with numbers, a data/edge-table alternative where meaningful, and is referenced from the sentence it supports.
- [ ] The prose it replaces is **removed**, not duplicated (net word count in the chapter does not increase).
- [ ] Numbering is continuous with the existing 12 (`13. attēls` … `21. attēls`) and the list of figures in ch16 is updated automatically (N01 claims).
- [ ] Each figure prints at ≤ 1/2 page and is legible at 7 pt.
- [ ] No new JS; any occlusion/scrubber is an enhancement over a fully readable static state.

### Substeps

1. **Triage and spec.** For each of the nine new figures, write the job sentence and the numbers that must be readable; drop any figure that cannot state a number (that would be decoration).
2. **Build in dependency order.** Start with the two that unblock prose clarity most (sig-fig decision flow, solution-prep flow), then the statistical pair (SD/SEM, uncertainty waterfall), then the rest.
3. **Replace, don't add.** For each, delete the displaced prose, add the figure reference, update the figure list and the change log, and re-measure chapter length (it should shrink or stay flat).

### Subtasks

#### N17.1 — Procedural figures (3, 5, 6) (≈10 h)

1. Titration curve: generate a monoprotic strong-acid/strong-base curve in Python, mark the equivalence region, annotate "the reading you record is the volume at the steepest point".
2. Solution-prep flow: five nodes with an explicit order constraint and a failure branch ("ja neatšķīdināsi pirms uzpildes, tilpums būs nepareizs").
3. Sig-fig decision flow: three decision diamonds, four exits, each exit naming the rule; replaces the textual tree (keep the text as the `<desc>`).

#### N17.2 — Statistical figures (1, 2, 7) (≈10 h)

1. Uncertainty waterfall: four bars (±0,125; ±0,05; ±0,02; ±0,01) combining to the total, with the dominant term highlighted.
2. Error propagation tree: one example each for additive (absolute errors add) and multiplicative (relative errors add).
3. SD/SEM: two panels, same axis, showing the narrowing of the mean's distribution with n = 3 vs n = 12.

#### N17.3 — Reading figures (4, 8, 9) (≈8 h)

1. Meniscus zoom: 4× inset with the half-division band and three labels (pārāk precīzi / pareizi / pārāk rupji).
2. Interpolation/extrapolation: calibrated band 5–30 mg/L, the 0,982 reading outside, the "line would say 30,2" annotation.
3. Prefix number line: log axis, decade ticks, the `µ`/`m` collision highlighted.

### Acceptance

- 9 new SVGs (10 with the concept map), numbered 13–21;
- `check_figures.py` 0;
- net word count per touched chapter ≤ baseline;
- print page count does not grow by more than +3.

---

## N18 — Instruments: guards, defaults, wording, and a test suite

| | |
|---|---|
| **Wave** | E — Capability |
| **Priority** | P2 |
| **Effort** | L (≈3 days) |
| **Risk** | Medium |
| **Axis** | functionality, correctness, UX |
| **Skills** | `impeccable` (form states), `break-ui` (edge inputs) |
| **Files** | `build/app.js`, sections 08, 09, 10, 11, 12 |
| **Findings** | I-01…I-06, C-03 |

### Context

Measured behaviour today:

| Tool | Probe | Result | Verdict |
|---|---|---|---|
| B calibration | `A = 0` | `−0,330 mg/L` | must warn/clamp |
| B calibration | `A = 999` | `31 057 mg/L` | must warn (extrapolation) |
| B calibration | `0,982` | `30,200 mg/L` | correct value, but should *flag* "above top standard" |
| C half-life | default unit | `dienas` | wrong for the chapter's 220 s case |
| C half-life | `1e9` | rejected | undocumented grammar |
| A sig-fig | `1e3` | "not a valid number" | contradicts ch8's own `4,5·10²` |
| D graph trainer | `9999` | `Par augstu par 9977,6 mg/L` | no sanity clamp |

All tools share a shell but not an explanatory layer, and there is no test suite that runs them headless.

### Definition of Done

- [ ] Every tool has an explicit **valid range** derived from `constants.json`, and three states: *valid*, *outside calibrated range* (warning + still computes, labelled "ārpus kalibrētā diapazona — nav mērījums"), *invalid* (refuses: empty, non-numeric, physically impossible).
- [ ] Tool B warns for `A ≤ 0`, `A < intercept`, and `A > A_top` (0,975), with the sentence from ch10 reused verbatim.
- [ ] Tool C default unit = `s`; accepts `2,2e2`, `2,2·10²`, `220`; rejects non-positive with the current message.
- [ ] Tool A accepts `1e3`, `1·10³`, `1,0×10³` and explains the exponent in its output.
- [ ] Tool D clamps suggestions to the plotted range and says "ārpus grafika" instead of computing nonsense.
- [ ] Every tool has: a **Notīrīt** (reset) control, an `aria-live="polite"` output region, a keyboard path (Enter runs), and a copy-to-clipboard on the answer (with a text fallback).
- [ ] Every tool has a **«Kāpēc šī formula?»** disclosure that quotes the chapter's rule (single source: extracted by anchor at build time, not retyped).
- [ ] A headless test suite (`build/test_tools.mjs`) runs 60+ cases and fails on `NaN`, `Infinity`, `undefined`, negative concentrations without a warning, and any unlabelled output.
- [ ] No tool output is lost when JS is off: each instrument has a static "example + answer" fallback (already partly true — verify all five).

### Substeps

1. **Define the contract per tool.** A table: inputs, units, valid range, out-of-range behaviour, invalid behaviour, output rows (Dots / Starpvērtība / Atbilde), and the chapter anchor for "why".
2. **Implement guards and states.** Add a shared `validate(input, spec)` helper, a `renderState()` that shows one of three states, and route all five tools through it. Keep the arithmetic untouched (it is verified).
3. **Test and document.** Write the headless suite, add the reset/copy/a11y affordances, and add a "tool contract" table to ch16 E so a reader can see the promised behaviour.

### Subtasks

#### N18.1 — Shared validation and range states (≈10 h)

1. Write `toolSpec` objects in `app.js` fed from `constants.json`: min, max, calibratedMin/Max, unit, decimals.
2. Implement `validate()` + `renderState()` with the three-state UI (neutral text, warning tone `--mistake`, refusal), and rewire B and D (the two with real ranges).
3. Verify with the probe set (`0`, negative, `999`, text, empty) that no negative concentration is ever printed as an answer.

#### N18.2 — Input grammar and defaults (≈8 h)

1. Add a tolerant number parser (`1 234,5`, `1.234,5`? — decide and document; at minimum `1e3`, `1,5e-2`, `4,5·10²`, NBSP groups).
2. Set C's default unit to `s`; add unit options with conversion shown in the intermediate row.
3. Document the grammar in each tool's hint line, and test all accepted/rejected forms.

#### N18.3 — Affordances, rationale, and tests (≈10 h)

1. Add Notīrīt, copy-answer (with `navigator.clipboard` and a fallback select), `aria-live`, and visible focus on the output.
2. Extract the "why" paragraph by anchor from the chapter at build time and inject it into a `<details>` per tool (no retyping).
3. Write `test_tools.mjs` (Playwright, 60+ cases) and wire it into `check_all.sh`; record the run in the changelog.

### Acceptance

```bash
node build/test_tools.mjs        # 0 failures, ≥60 cases
```
Manual: `A = 0` shows a warning, not a negative answer; `A = 999` shows "ārpus diapazona"; C defaults to seconds.

---

## N19 — Study workspace v2: diagnosis, due queue, search facets, no leaks

| | |
|---|---|
| **Wave** | E — Capability |
| **Priority** | P2 |
| **Effort** | L (≈3 days) |
| **Risk** | Medium |
| **Axis** | functionality, study efficacy |
| **Skills** | `cognitive-deload-auditor`, `learn-then-test` (patterns), `impeccable` (controls) |
| **Files** | `build/app.js`, `build/sections/15_ch15.html`, `build/build_search_index.py`, `build/sections/00_front.html` |
| **Findings** | C-05, C-07, E-03, I-03, I-07, I-08, A-03, A-05 |

### Context

The workspace is the most app-like part of the document and the closest to genuinely useful. It has filters (chapter / concept / mark), a result list, an exam mode (20/30/40, stratified), and an answer sheet. What it lacks:

1. **Post-exam diagnosis** — after finishing, the user learns a score-like count and nothing else. The teaching moment is *"your errors cluster in ch10 and ch12"*.
2. **A due queue** (N09) — no answer to "what today?".
3. **Search facets** — 815 blocks mixed together; no type filter, no "in this chapter".
4. **Answer leakage in search** — 13 index blocks contain `Atbilde` text from closed prompts (I-03).
5. **Progress orientation** — the sidebar shows `n/16` but there is no per-chapter "you have marked 4/13" anywhere except the global counter.

### Definition of Done

- [ ] After an exam, a **diagnosis panel** shows: per-chapter correct/attempted, the two weakest concepts, and 3 deep links to the exact sections to reread. No score is stored; the panel is session-only and printable.
- [ ] The `due` filter exists (N09) and is the first option in the mark filter.
- [ ] Search results carry a **type** (sadaļa / tabula / attēls / termins / jautājums) and a **chapter** facet; both are keyboard-operable and combinable with the free-text query.
- [ ] The search index **excludes** recall answer bodies; a search for a distinctive answer phrase returns no closed-answer block. Verified by a test that greps the index for the first 40 characters of 10 answers.
- [ ] Chapter headers show a per-chapter recall counter (`4/13 atzīmēti`) generated from the DOM on load and after each mark.
- [ ] The consent semantics are symmetric: if nothing is stored, nothing is read (`localStorage.getItem` gated by the same consent flag); if consent is given, theme + marks + `data-last` persist, with a visible "Dzēst saglabātos datus" control.
- [ ] No gamification added: no points, no streaks, no badges. The diagnosis panel says "jāatkārto", not "līmenis".

### Substeps

1. **Diagnosis first.** Implement the post-exam panel from the in-memory answer state (chapter mapping already exists in `data-chapter`), with deep links and a print sheet. Test with a deliberately wrong run.
2. **Search: facets and leak fix.** Extend the index builder to skip `.recall-answer` content and to tag blocks by type; add the facet UI. Test the leak explicitly.
3. **Orientation and consent.** Add per-chapter counters, gate reads on consent, add the clear-data control, and verify the theme behaviour in both consent states.

### Subtasks

#### N19.1 — Post-exam diagnosis (≈10 h)

1. Define the output: chapter table (attempted/correct), concept table (top 2 weak), and 3 links chosen by lowest correct-rate.
2. Implement from the existing session state; add a printable diagnosis page (one A4) and a "sākt no jauna" action.
3. Test with 3 runs: all correct, all wrong, mixed; verify the links land on the right sections.

#### N19.2 — Search facets and the leak (≈8 h)

1. Change `build_search_index.py` to drop answer text and to emit `type`/`chapter` facets; rebuild and diff the index size and the result quality for 10 queries.
2. Implement the facet controls and the combined filter; keep the combobox pattern intact (aria-expanded, listbox, arrow keys).
3. Write the leak test: 10 answer prefixes, assert 0 index hits.

#### N19.3 — Orientation and consent symmetry (≈6 h)

1. Add per-chapter counters next to each chapter heading (or in the TOC), computed on load and on mark change.
2. Gate `getItem` behind consent; add "Dzēst saglabātos datus" with a confirmation; verify theme persistence in both states.
3. Check that the «Atzīmes netiek saglabātas» note matches the actual behaviour after the change.

### Acceptance

```bash
node build/test_workspace.mjs    # diagnosis, facets, leak, consent
```

---

## N20 — Release engineering: budgets, one gate, honest docs

| | |
|---|---|
| **Wave** | E — Capability |
| **Priority** | P2 |
| **Effort** | M (≈2 days) |
| **Risk** | Low |
| **Axis** | process, performance, reproducibility |
| **Skills** | `audit` (checklist thinking), `print-css-alchemist` (export checklist) |
| **Files** | `build/check_all.sh`, `build/build_doc.py`, `build/MANIFEST.md`, new `build/release_checklist.md`, `README` note |
| **Findings** | J-01…J-06, A-09, G-04 |

### Context

The build is reproducible and the checkers exist, but running them is a memory exercise, there are no size/perf/pagination budgets, and the folder mixes sources with stale artefacts. A release that cannot be reproduced and gated is a release that will regress.

### Definition of Done

- [ ] `build/check_all.sh` runs every gate in order and exits non-zero on the first failure: build → claims → terms → style → sig-fig → calibration → calc → figures → tools (headless) → print (pages, waste, TOC) → responsive (7 widths) → lint.
- [ ] Budgets are asserted: HTML ≤ 1,45 MB; fonts ≤ 40 KB total; search index ≤ 220 KB; print pages ≤ 122; print waste ≤ 5 %; desktop height ≤ 135 000 px; no external URL; no `NaN`/`undefined` in rendered output.
- [ ] `build/MANIFEST.md` marks every file source/generated/archive; `build/_archive/` holds the stale artefacts; a `build/.gitignore`-equivalent note explains what must never be committed.
- [ ] A `release_checklist.md` covers: version/date, build SHA, gate output, print render, screenshots, unverified items, and the "what this document is not" statement.
- [ ] A `README_build.md` lets a second person rebuild from scratch in ≤ 5 commands, including the font-subset fallback.
- [ ] The colophon (N13) is generated from the same metadata (version, SHA, date), so print and screen cannot disagree.

### Substeps

1. **Collect the gates.** Wrap the existing checkers, fix their flags, and make each print one line. Order matters (build first, then claims, then content, then rendering).
2. **Set the budgets.** Measure the current values, set the ceilings just above them, and make the script print `metric: value / limit` so drift is visible before it fails.
3. **Write the docs and the manifest.** One page each; no duplication of the plan; link to `AGENTS.md` and the prompt.

### Subtasks

#### N20.1 — The single gate (≈6 h)

1. Write `check_all.sh` with `set -e`, a section header per gate, and a final summary table.
2. Make every checker support `--check` (non-zero on failure) and a one-line pass message; fix any that only prints a report.
3. Run it against the baseline and record the first green run's output in the changelog.

#### N20.2 — Budgets and perf (≈6 h)

1. Implement `budget.mjs` (file size, font bytes, index bytes, external URL count, `NaN` scan) and `print_budget.py` (pages, waste, TOC resolution).
2. Set limits, add the numbers to the release checklist, and prove the gate fails by temporarily lowering a limit.
3. Check the first-paint cost qualitatively (no blocking third-party anything; fonts are inline base64 — verify no layout shift by measuring CLS in Playwright).

#### N20.3 — Docs, manifest, archive (≈4 h)

1. Write `MANIFEST.md`, `release_checklist.md`, `README_build.md`; move stale artefacts to `_archive/2026-11-01/`.
2. Record the exact commands and their expected output; a second reader must be able to reproduce the build without asking.
3. Add the "what this document is not" statement (student study aid, not RSU-issued, not a substitute for the practical) to the colophon and the README.

### Acceptance

```bash
bash build/check_all.sh    # exit 0, all gates green
```

---

# 4. Feature catalogue — 35 add-ons, each with an owner task

**Rules for every feature in this catalogue**

1. **Vanilla only.** No library, no CDN, no build step beyond `build/*.py`. If a feature cannot be done without a dependency, it is not done.
2. **Static-first.** The document must remain fully readable with JS disabled: a feature may add convenience, never content.
3. **No persistence without consent** (except in-memory state for the current session).
4. **No gamification.** No points, streaks, badges, levels, leaderboards, confetti, "mastery %".
5. **Print parity.** If a feature produces content, that content must either print or be explicitly marked screen-only.
6. **Each feature names its acceptance test** — a command or a manual check.

Legend: **Value** (learner benefit) H/M/L · **Cost** S/M/L · **Risk** (of harming the document) L/M/H.

## 4.1 Study and retrieval (7)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-01** | **Due queue** ("Šodien jāatkārto") | Computes which marked items are due under a 1/3/7-day schedule; empty-state explains itself | Converts 127 prompts into a retention system | M | L | N09 |
| **F2-02** | **Post-exam diagnosis** | Per-chapter correct/attempted, two weak concepts, three deep links, printable | Turns a test into a reading plan | M | L | N19 |
| **F2-03** | **Interleaved set** (12 items, 6 chapters) | A fixed mixed set that forces switching | The real exam switches topics; chapter drills do not | S | L | N09 |
| **F2-04** | **Error journal** (session-only) | A list of the items marked "nezināju" with the rule each one tests, printable | The highest-value 10 minutes before a test | M | L | N09/N19 |
| **F2-05** | **"Paskaidro atpakaļ" prompts** | 8 prompts that ask the learner to *write* an explanation, with a model answer in `<details>` | Generation effect; currently all prompts are recognition/short answer | S | L | N09 |
| **F2-06** | **Per-chapter recall counters** | `4/13 atzīmēti` beside each chapter heading and in the TOC | Orientation without a dashboard | S | L | N19 |
| **F2-07** | **Printable answer sheet variants** | 20/30/40-question sheets with a header (date, time, set id) | Makes exam practice paper-realistic | S | L | N19 |

## 4.2 Reading, navigation and accessibility (7)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-08** | **Reading position** (session-only) | A thin chapter progress rule + "turpināt" link on return within the session | 140 screens need a bookmark that is not a dashboard | S | L | N19 |
| **F2-09** | **Chapter collapse** | Each chapter heading collapses its body (details-friendly, print opens all) | Turns the document into a study skeleton | M | M | N19 |
| **F2-10** | **Text-size control** (S/M/L, 100/112/125 %) | Root font-size switch, remembered only with consent | Real accessibility need for a 117-page text | S | L | N14 |
| **F2-11** | **High-contrast theme** (beyond dark) | A third theme: pure white ground, near-black ink, no tints | Low-vision readers; also useful for projectors | S | L | N14 |
| **F2-12** | **Anchor copy** | A small "kopēt saiti" on section headings (focusable, no layout shift) | Sharing a precise reference with a classmate/tutor | S | L | N19 |
| **F2-13** | **Deep-link resolver** | `?q=…` / `#…` opens the matching section/search on load | Useful when a lecturer links to a section | S | L | N19 |
| **F2-14** | **Screen-reader landmarks audit + fixes** | Named regions, `aria-labelledby` on chapters, row scopes | WCAG 1.3.1/2.4.1 gaps | M | L | N14 |

## 4.3 Content instruments (8)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-15** | **Unit converter** (mass, volume, amount, concentration, density, temperature) | One input + unit pair → all equivalent forms, with the conversion chain shown | The most common exam error class (O5) | M | L | N18 |
| **F2-16** | **Calibration-fit playground** | Paste ≤12 (x, y) pairs → slope, intercept, R², residuals, and a "outside range" warning | Teaches that the line is computed, not drawn | L | M | N18 |
| **F2-17** | **Meniscus reading trainer** | 6 SVGs at different scales; click the reading; tolerance ±half division | The practical skill no table can teach | M | L | N16/N18 |
| **F2-18** | **Burette reading trainer** | 5 readings with a zoom; type the value; feedback on the last digit | Directly mirrors 2B Q2 | M | L | N16/N18 |
| **F2-19** | **Rounding trainer** | 20 values → round to N sig figs; shows the rule used | Fast, high-frequency drill | S | L | N18 |
| **F2-20** | **Graph "spot the error"** | 6 small charts, each with one defect (no units, wrong scale, points joined, no line) | Teaches graph critique, not just construction | M | L | N16 |
| **F2-21** | **Dilution planner** | c₁V₁ = c₂V₂ plus "how to make it" steps and the volumetric-flask warning | Ties ch12 arithmetic to practice | M | L | N18 |
| **F2-22** | **Half-life ladder explorer** | t₀, t½, unit → ladder table + absolute vs Δt toggle | Makes the offset trap visible | S | L | N18 |

## 4.4 Figures and visual learning (5)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-23** | **Glassware labelling drill** | The 9 vessels with hidden labels; "show all / hide all / quiz one" | Memorisation of the plate (image-occlusion pattern) | M | M | N16 |
| **F2-24** | **Concept map** | 121 concepts, prerequisite edges, chapter bands | The single best structural aid (N06) | L | M | N06 |
| **F2-25** | **Figure data tables everywhere** | Every data figure gets a `<details>` table | Accessibility + the numbers behind the picture | S | L | N15/N16 |
| **F2-26** | **Titration curve explorer** | Volume → pH curve; mark equivalence; connect to the burette reading | Explains *why* the reading matters | M | M | N17 |
| **F2-27** | **Uncertainty budget interactive** | Toggle contributions on/off; total recomputes with the quadrature rule | Makes the budget a model, not a table | M | M | N17/N18 |

## 4.5 Print and distribution (5)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-28** | **Printed TOC with page numbers** | Two-pass build injects real page numbers | A reference must be navigable on paper | M | L | N13 |
| **F2-29** | **Colophon page** | What it is / is not, edition, SHA, verification method, attribution | Provenance and honesty | S | L | N13 |
| **F2-30** | **Question edition** | Print without answers (`PRINT_MODE=questions`) | Lets a study partner quiz you | S | L | N13 |
| **F2-31** | **A4 formula sheet** (separate, generated) | The ch16 A page as a standalone one-pager, generated from the same source | The thing students actually print | S | L | N13 |
| **F2-32** | **A6 pocket card** | 8 rules + 4 unit conversions, print-imposed 4-up | Last-minute revision | S | L | N13 |

## 4.6 Integrity tooling (3)

| ID | Feature | What it does | Why it helps | Cost | Risk | Owner |
|---|---|---|---|---|---|---|
| **F2-33** | **Claims ledger page** | A screen-and-print page listing every generated count with its definition | Makes the audit trail inspectable by the reader | S | L | N01 |
| **F2-34** | **Defect register browser** | Filter S/D rows by chapter, confidence, status | Students and the lecturer can see what was corrected and why | S | L | N01 |
| **F2-35** | **"Verify this number" links** | Each worked answer links to the checker name and case id | A reader can re-run the claim | M | L | N04 |

## 4.7 Features deliberately **not** proposed

| Rejected | Why |
|---|---|
| Spaced-repetition algorithm with per-item ease factors (SM-2/FSRS) | Overkill for 127 items; a fixed 1/3/7 schedule is transparent and printable. |
| Analytics / telemetry / "time on task" upload | Violates offline + privacy rules. |
| AI tutor / chat panel | Not self-contained, introduces a network dependency and unverifiable content. |
| Leaderboards, streaks, XP, "mastery %" | Explicitly banned by the design contract and `AGENTS.md` §9. |
| Speech synthesis / audio narration | Not verifiable offline across voices; adds a large surface. |
| Animated plots, scroll-driven figure reveals | Motion is capped by §6.2; the document must stay still. |
| Dark-pattern "streak" reminders | Same as above; also manipulative. |
| A second colour system for "chapters" | One accent; chapter identity comes from numbering, not hue. |

---

# 5. SVG programme — from decoration to instruments

The document has 21 SVGs: 12 data figures, 9 vessel icons. They are already better than typical: real geometry, `<title>`/`<desc>`, no clip-art. The programme below makes them *instruments* — each one teaches a specific reading.

## 5.1 Principles

1. **A figure earns its space only if it lets the reader do something**: read a value, see a failure, compare two states, recognise an object. If the same words work better, delete the figure.
2. **One scaffold.** Same margins, same axis grammar, same type scale, same stroke hierarchy across all figures.
3. **Data ink first.** Gridlines are the lightest thing on the figure; data is the heaviest. Annotation is between.
4. **No colour-only encoding.** Every series also differs by marker shape or dash pattern; a greyscale raster must remain readable.
5. **Label by leader, not by legend**, wherever the label fits: the reader should not travel to a key and back.
6. **The `<desc>` is data, not a title echo.** It must contain the numbers and the takeaway.
7. **Print is a target.** Minimum 7 pt labels, 0,5 pt hairlines, no fills lighter than 5 %.
8. **Motion optional, never required.** Any scrubber/occlusion has a fully static, printable state.

## 5.2 Scaffold specification

| Element | Value | Notes |
|---|---|---|
| Canvas | `viewBox="0 0 W H"`, W ∈ {640, 900, 980}, H per figure | Fluid `width:100%`; no fixed px |
| Margins | 24 / 24 / 48 / 64 (top / right / bottom / left) | Left margin sized for the longest tick label |
| Plot area | ≥ 70 % of the canvas | If not, the figure is a diagram, not a plot |
| Grid | 8 px minor, 64 px major (design grid) | Gridlines only if they aid reading |
| Type | `--fig-title` 14, `--fig-label` 12, `--fig-tick` 11, `--fig-note` 10 (user units at W=900) | Must render ≥ 11 px at 390 px |
| Stroke | axis 1, grid 0,5, data 1,5, annotation 1 dashed | Max 3 styles per figure |
| Colour | `var(--fig-ink)`, `var(--fig-muted)`, `var(--fig-accent)`, `var(--fig-band)` | Tokens only; no literals |
| Markers | circle 4 px, square 3,5, triangle 4 | Shape encodes series identity |
| Numbers | tabular, decimal comma, unit in the axis title | Ticks: 3–6 per axis, regular |
| Annotation | direct label + leader line; no arrowheads unless direction matters | Leader 1 px, 45° or horizontal |
| Accessibility | `role="img"`, `aria-labelledby="t d"`, `<title>`, `<desc>` ≥12 words with a numeral | Checker-enforced |
| Rounding | coordinates to 2 decimals | Checker-enforced |

## 5.3 Per-figure specification (12 existing + 9 new)

### 5.3.1 Existing (redrawn in N16)

| # | File | Reader must be able to | Mandatory annotations |
|---|---|---|---|
| 1 | `prefix-ladder.svg` | Convert 10⁻⁹…10⁹ quickly | Decade ticks, `µ`/`m` collision flagged |
| 2 | `calibration-scheme.svg` | Follow sample → signal → line → result | 3 steps, distinct arrow weights, "atpakaļceļš" dashed |
| 3 | `meniscus-parallax.svg` | See that eye height changes the reading | Eye above/level/below, Δ in mL for each |
| 4 | `burette-readings.svg` | Read to ±0,05 mL | Numbered graduations, 3 readings marked, zoom inset |
| 5 | `target-plot.svg` | Name the 4 precision/trueness cases | Quadrant labels, "systematic"/"random" mapping |
| 6 | `ci-coverage.svg` | Interpret 95 % | 10 intervals, the one miss labelled, "9/10" stated |
| 7 | `read-path.svg` | Read a graph in 6 moves | Each move numbered, the return move unambiguous |
| 8 | `calibration.svg` | Read ρ from A and see the range limit | Shaded calibrated band 5–30, lemon at 0,982 outside, equation + R² |
| 9 | `calibration-residuals.svg` | Judge the fit | Zero line, ± band, "random / curve / fan" labels |
| 10 | `half-life-hg.svg` | Halve twice, read t½ | Ladder 50 → 25 → 12,5 %, t½ at both steps |
| 11 | `half-life-hydrolysis.svg` | Take Δt, not absolute t | t₀ = 115 s marked, two Δt brackets, "nepareizi" absolute-time arrow |
| 12 | `density.svg` | Invert ρ → w | Slope meaning ("7,3 mg/mL per %"), arrows both ways |
| 13 | `glassware.html` (9 icons) | Recognise + know which mark is calibrated | Baseline grid, meniscus, one red mark, `TD`/`Ex`, tolerance pointer |

### 5.3.2 New (N17)

| # | Figure | Reader must be able to | Data source |
|---|---|---|---|
| 14 | Uncertainty budget waterfall | See which contribution dominates | ch6 budget table |
| 15 | Error propagation tree | Predict whether ± adds absolutely or relatively | ch8 rules |
| 16 | Titration curve | Locate the equivalence volume | Generated curve (strong acid/base) |
| 17 | Meniscus zoom (±½ division) | Estimate the last digit correctly | ch5 rules |
| 18 | Solution-preparation flow | Recall the order constraint | ch12 five steps |
| 19 | Sig-fig decision flow | Choose the rule in 3 decisions | ch8 tree |
| 20 | SD vs SEM | Explain √n | ch7 formulas |
| 21 | Interpolation vs extrapolation | See why 0,982 is outside | ch10 data |
| 22 | Prefix number line | Place a unit on a log axis | ch2 table |

*(The concept map from N06 is numbered 23 in the figure sequence.)*

## 5.4 Figure accessibility and print rules

- `<title>` = what it is; `<desc>` = the data + takeaway (≥1 numeral for data figures); `<figcaption>` = what is plotted, units, n; `<p class="source-line">` = provenance.
- Every data figure gets `<details class="figure-data">` with the numbers in a table.
- Greyscale test: raster at 150 dpi, desaturate, verify every distinction survives.
- Print: no figure taller than 120 mm; two figures never share a page with a page-break inside them.
- Screen: `max-width: 100%`, `height: auto`, no `min-width`.
- Interactive add-ons (occlusion, scrubber) must announce state changes with `aria-live` and be keyboard-operable.

## 5.5 Figures we will not draw

Bunsen burners, fume hoods, balances, "a scientist at a bench", laboratory scenes, molecule ball-and-stick for NaCl in water (decorative), anything that cannot state a number or a recognition task. A study document does not need illustrations; it needs instruments.

---

# 6. Design contract v2 — restyle and retexture rules

This section refines prompt §6 with the measured state of the document. **Prompt §6 wins on conflict.** Nothing here overrides the ban list.

## 6.1 What the document is

A **measured readout**: a reading surface, data ink, one indicator colour, structure from space and scale. Not a landing page, not a course platform, not a slide deck, not a "premium editorial" magazine.

## 6.2 Token spec (target state after N10–N12)

| Token | Light | Dark | Job |
|---|---|---|---|
| `--ground` | `oklch(0.971 0.0035 219)` | `oklch(0.207 0.014 230)` | Page |
| `--surface` | +1 tone step | +1 step | Inset panels (calc, figure-data, workspace) |
| `--surface-2` | +2 steps | +2 steps | Header rows, subdued fills |
| `--ink` | 14,9:1 on ground | ≥12:1 | Body |
| `--ink-2` | 6,5:1 | ≥6:1 | Secondary text, captions |
| `--line` | structural hairlines | — | Non-data rules |
| `--line-strong` | data tables | — | Table header rule, axis (via `--fig-*`) |
| `--accent` | 6,6:1 | ≥5:1 | **Interaction only**: links, focus, buttons, active |
| `--accent-quiet` | ≥4,5:1 | ≥4,5:1 | **Structure only**: chapter numerals, role labels, TOC marker |
| `--mistake` | 7,2:1 | — | Mistake role |
| `--verified` | = accent | — | Verified role (label + bar, never colour alone) |
| `--fig-*` | 4 plot tokens | — | Figures (axis, muted, data, band) |

**Type** (8 screen roles, unchanged count): display ≤40 px · h2 clamp(28–36) · h3 24 · lead 20 · body 18/1,62/66ch · table 15 · small 14 · micro 13. Tabular figures everywhere numbers align. One family (subset), weights 400/700, true italics.

**Space**: 4–96 px scale; section separation ≥48 px; no borders where space will do.

**Rules**: hairline = data or table separation only. No full-width decorative rules. No ruled "broadsheet" look.

## 6.3 Permitted / forbidden (v2 additions to §6)

| Permitted | Forbidden |
|---|---|
| A plain outcomes list or 2-column table with `O1…O5` | Oversized `01/02` numerals, medals, chapter-colour dots |
| One quiet link into chapter 1 | A button row / CTA pair in the masthead |
| A colophon block at the end | A metadata strip under the title ("Pārbaudīts: …") |
| Two accent tokens with distinct jobs | Accent used for decoration (numbers, bullets, rules) |
| Tone-step panels with 1 px rules | Drop shadows on content panels |
| A 3-stroke figure hierarchy | Nine identical line weights for every drawing |
| `<details>` for depth | Accordions for navigation |
| Static charts with annotations | Animated charts, scroll reveals |
| One sticky bar (mobile) | Floating pill nav, glass header |
| Text-size and contrast controls | Theme "presets" with names like "Focus", "Calm" |

## 6.4 Component inventory (the complete set; nothing else may be invented)

| Component | Where | Variants |
|---|---|---|
| `topbar` | every screen | desktop / mobile (menu) |
| `sidebar` + `toc` | ≥1024 px | expanded / collapsed / current-section |
| `masthead` | ch0 | one variant only |
| `chapter-head` | 16× | number + title + lead + prerequisites |
| `role` | Noteikums / Kļūda / Pārbaudīts / Piezīme avotam | one geometry, four labels |
| `calc` | all worked maths | add / mul / mixed / mean |
| `table` | 75× | data / stacked / pinned / compact |
| `figure` | 23× | data / schematic / plate |
| `instrument` | 5× | tool shell + 3 states |
| `recall` | 127× | closed / opened / marked / exam |
| `workspace` | ch15 | filters / results / exam / diagnosis |
| `quickref` | print | A4 sheet |
| `colophon` | end | screen + print |

## 6.5 Motion policy

- Allowed: `<details>` open/close, 120–160 ms colour/opacity on focus/hover, instrument state change, the search panel's appearance.
- Forbidden: scroll-driven animation, parallax, bounce, autoplay, skeleton shimmer, "fade-and-rise" on sections.
- `prefers-reduced-motion` already honoured — keep it, and test with the media emulated.

## 6.6 How to review a design change

1. Screenshot at 1440, 768, 390, plus one print page — before and after.
2. Run `lint.mjs` and `inspect.mjs`; diff the warning lists.
3. Answer three questions in the change note: *What did the reader gain? What did the reader lose? Which contract clause governs?*
4. If the change cannot answer (1), the change is not ready.

---

# 7. Verification and gates

## 7.1 The one command

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_2 && bash build/check_all.sh
```

It must run, in this order, and stop at the first failure:

| # | Gate | Command | Pass criterion |
|---|---|---|---|
| 1 | Rebuild | `python3 -I build/build_doc.py` | exit 0, prints search block count |
| 2 | Self-audit | `python3 -I build/audit_claims.py --check` | 0 unresolved placeholders, 0 drifted literals |
| 3 | Terms | `python3 -I build/check_terms.py Master_…html --report` | 0 violations, document-term stats printed |
| 4 | Style | `python3 -I build/check_style.py --check` | 0 rhetorical dashes, 0 unit-spacing errors |
| 5 | Sig figs | `python3 -I build/check_sigfig_cases.py --check` | all ok |
| 6 | Calibration | `python3 -I build/check_calibration.py --residuals` | all ok |
| 7 | Calc component | `python3 -I build/check_calc.py --check` | 0 rule/limiter mismatches |
| 8 | Figures | `python3 -I build/check_figures.py --check` | 0 |
| 9 | Tools | `node build/test_tools.mjs` | 0 failures, ≥60 cases |
| 10 | Workspace | `node build/test_workspace.mjs` | 0 failures |
| 11 | Responsive | `node build/responsive_check.mjs` | no overflow at 7 widths |
| 12 | Print | `python3 -I build/print_report.py out.pdf` | pages ≤122, waste ≤5 %, TOC resolves |
| 13 | Budgets | `node build/budget.mjs` | all metrics ≤ limits |
| 14 | Lint | `node workspace_skills/design-taste-frontend/scripts/lint.mjs Master_…html` | 0 FAIL |
| 15 | Inspect | `node workspace_skills/design-taste-frontend/scripts/inspect.mjs Master_…html` | 0 FAIL |

## 7.2 Thresholds (measured today → target)

| Metric | Today | Target | Owner |
|---|---:|---:|---|
| Contradictory counts in the change log | 6 | 0 | N01 |
| Double ordinals in rendered lists | 19 items | 0 | N02 |
| Unregistered document coinages | ≥9 | 0 | N03 |
| Duplicated constants with drift | unknown (≥3 confirmed) | 0 | N04 |
| Hard ideas without mechanism + failure mode + check | ~7/12 | 0/12 | N05 |
| Chapters without prerequisite line | 16 | 0 | N06 |
| Calculations not using `.calc` | ~40 | 0 | N07 |
| Rhetorical em dashes | ~48 | 0 | N08 |
| Prose sentences >40 words | few | 0 | N08 |
| Accent elements per 400 px of column | >3 in places | ≤1 | N10 |
| Decorative box-shadows | 3 | 0 | N11 |
| Inline SVG style literals | many | 0 | N15 |
| Figures without data-table alternative | 0 (12/12 have) | 12/12 | N15 |
| Figure `<desc>` with a numeral | few | 12/12 | N15/N16 |
| Tools without range guard | 2 | 0 | N18 |
| Tools without reset/aria-live | 5 | 0 | N18 |
| Search blocks containing answer text | 13 | 0 | N19 |
| Document overflow at 390 px | topbar + 11 figures | 0 | N14 |
| Print pages | 117 | ≤122 | N13 |
| Print waste | ~8 % | ≤5 % | N13 |
| HTML size | 1 296 228 B | ≤1,45 MB | N20 |
| Console errors | 0 | 0 | all |
| External URLs | 0 | 0 | all |

## 7.3 Manual QA protocol (must be stated as performed or not)

**Screen** (Chromium, emulated): 320 / 360 / 390 / 414 / 768 / 1024 / 1440. For each: no horizontal document scroll, top bar usable, figures legible, tables stack or scroll with an affordance, focus visible on Tab from the skip link to the first 15 targets.

**Keyboard**: Tab order through top bar → sidebar → chapter; Esc closes search/popover/menu; Enter runs each tool; arrow keys in the search listbox.

**Dark mode**: every role block, table header, figure, tool output, focus ring, and the print preview (which must stay light).

**Print** (headless PDF + raster): first page, a figure page, a table page, a page break inside a `.calc` (must not happen), the TOC page numbers (spot-check 20), the colophon, the last page.

**No-JS**: disable JavaScript; verify the document is readable, all recalls are `<details>`-operable, all tools show their static fallback/example, the TOC still works (details), and nothing says "not available".

**Not claimed unless actually done**: axe, NVDA/VoiceOver, Firefox/Safari, physical print, mobile hardware.

## 7.4 Reporting template (use at the end of every task)

```
Task: N__ — <name>
Changed: <files>  Build SHA: <12 hex>
Gates run: <list>  Result: pass/fail (paste the failing line)
Measured deltas: <before → after> for the metric this task owns
Not verified: <list>
Source defects touched: <S/D ids>
New defect rows: <D ids>, if any
```

---

# 8. Risks, anti-goals and open questions

## 8.1 Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Restyle erases the document's credibility signals (defect log, source lines) | Medium | High | N10's review questions; the "spine" list below is untouchable. |
| Prose edits introduce factual drift | Medium | High | N04 provenance + recompute every number touched; diff against source quotes. |
| Print TOC two-pass build breaks reproducibility | Medium | Medium | Keep the single-pass build as fallback; the TOC numbers are a derived layer only. |
| Mobile fix shrinks SVG labels below legibility | High | Medium | N15 type floor (11 px rendered) + N14 screenshots. |
| New figures duplicate prose instead of replacing it | High | Medium | N17 "replace, don't add" rule + net word count check. |
| Instrument guards annoy users (over-blocking) | Medium | Low | Three states, never silent refusal; "ārpus diapazona" still computes and explains. |
| Terminology rename breaks anchors/ids | Medium | Medium | Rename text, never ids; checker asserts 0 broken internal links. |
| Budget gate blocks a legitimate large figure | Low | Low | Budgets are printed as value/limit; raising one requires a one-line justification in the changelog. |
| Scope creep into a "course platform" | Medium | High | §4.7 rejected list + no-gamification invariant. |

## 8.2 The spine — never remove, even in a redesign

1. The source-defect register (S1–S23 + D-rows) with confidence labels.
2. The «avotā / papildinājums / ilustratīvs piemērs» provenance marks.
3. The three semantic roles with text labels + non-colour cues.
4. Closed recall prompts with answers inside `<details>`.
5. The source lines and the change log.
6. Offline self-containment and the no-network rule.
7. The honest "avotā nav norādīts" statements.

## 8.3 Anti-goals

- No "mastery", XP, streaks, badges, leaderboards, confetti, celebration animations.
- No AI/chat/network feature.
- No new font family, icon pack, chart library or CSS framework.
- No "premium editorial" restyle (cream + serif + terracotta, oversized italic, grain overlay).
- No cards-in-grids navigation, no bento.
- No content marketing voice («Ievads», «Ko jūs iemācīsities», «Sāksim!»).
- No removal of content to make a page "cleaner".

## 8.4 Open questions (V register — ask the lecturer before asserting)

| # | Question | Why it matters | Affects |
|---|---|---|---|
| V1 | Which Latvian term is the official umbrella for *accuracy* in this course: `kopējā tuvība`, `kopējā precizitāte`, or `pareizība`? | Three labels coexist; the glossary must pick one. | N03 |
| V2 | For the calibration slope, what precision should a student report (0,0322 / 0,03217 / 0,0321657)? | Three precisions appear; the reporting policy needs an authority. | N04 |
| V3 | Is the 0,5 % class-B volumetric convention examinable as stated, or is it "read the marking on the glass"? | `AGENTS.md` S7 marks it H/V. | N03, N05 |
| V4 | In 2B Q2, is a 50 mL burette available, or must students refill? | The total delivered (28,30 mL) exceeds a 25 mL burette. | N17 (titration figure) |
| V5 | Should the print edition open all answers (study) or keep them closed (question edition) as the default? | Affects pagination and the honesty of "test yourself". | N13 |
| V6 | Is the density–temperature table examinable beyond 20 °C? | Determines whether the temperature figure is core or enrichment. | N05, N17 |

---

# 9. Definition of Done and release

## 9.1 A task is done when

1. Its DoD checklist is fully ticked, each item with evidence (command output or screenshot path).
2. `bash build/check_all.sh` is green.
3. The change log has one new dated line and, if a source was contradicted, a new D-row.
4. The task's measured metric moved in the right direction (numbers pasted in the report).
5. Nothing on the spine (§8.2) was removed.
6. Unverified items are listed honestly.

## 9.2 A release is done when

- [ ] All P0 tasks closed (N01–N05, N14).
- [ ] All P1 tasks closed or explicitly deferred with a reason.
- [ ] `check_all.sh` green on a clean rebuild from `build/`.
- [ ] Print render ≤122 pages, waste ≤5 %, TOC page numbers spot-checked (20/20).
- [ ] Screenshots archived: 1440 / 768 / 390 full-page + 12 figure close-ups + 3 print pages.
- [ ] Colophon present with edition, date, build SHA, verification method, attribution.
- [ ] `MANIFEST.md` current; `_archive/` holds the stale artefacts.
- [ ] The final report states: what passed, what is unverified, which source defects were corrected, and which remain open (`V` items).

## 9.3 Suggested sequence and calendar (a single focused week per wave)

| Wave | Tasks | Working days | Exit criterion |
|---|---|---:|---|
| 0 | freeze + baseline | 0,5 | `build/baseline/v2/` + hashes |
| A | N01, N02, N03, N04 | 5,5 | change log and artifact agree; terms/numbers centralised |
| B | N05, N06, N07, N08, N09 | 10 | 12 hard ideas shown; calc component everywhere; 0 rhetorical dashes |
| C | N10, N11, N12, N13, N14 | 12 | first screen is a title block; no decorative shadows; no mobile overflow; print ≤122 pp |
| D | N15, N16, N17 | 8 | 21 SVGs on one scaffold; 9 new figures; 12/12 desc with numbers |
| E | N18, N19, N20 | 8 | tools guarded and tested; diagnosis + due queue; one gate |

Total ≈ 44 working days for one person; ~3 weeks with two people splitting content (N05–N09) from design/SVG (N10–N17) after Wave A.

## 9.4 Success metrics (post-release)

| Metric | Baseline | Target |
|---|---:|---:|
| Countable claims contradicted by the artifact | 6 | 0 |
| Visible rendering defects (double ordinals, broken bar, blank pages) | 19 + 1 + 2 | 0 |
| Instruments contradicting the text | 2 | 0 |
| Figures whose `<desc>` carries data | ~0/12 | 12/12 |
| Time for a student to find "what to review today" | not possible | ≤ 10 s |
| Print pages | 117 | ≤122 |
| External URLs / analytics / storage-without-consent | 0 / 0 / 0 | 0 / 0 / 0 |

---

# Appendix A — Ready-to-paste Latvian corrections

**A.1 Double ordinals (remove the bold numeral, keep the verb):**

```html
<!-- before -->
<li><strong>1. Nosakiet mērķi.</strong> Ko tieši prasa: …</li>
<!-- after -->
<li><strong>Nosakiet mērķi.</strong> Ko tieši prasa: …</li>
```

Apply the same to ch8 (*1. solis — vai skaitlis ir precīzs?* → *Vai skaitlis ir precīzs?*), ch9 (*1. solis — asis un vienības* → *Asis un vienības*), and ch8's second ladder.

**A.2 Chapter 15 lead (depends on N01 placeholders):**

> Šajā nodaļā ir {{CLAIM:recall_ch15}} slēgti jautājumi ar atbildēm un aprēķiniem. Darba telpa rāda visus {{CLAIM:recall_items}} dokumenta jautājumus. Vispirms atbildiet, neatverot atbildi; tikai pēc tam atveriet to un atzīmējiet «Zināju» vai «Nezināju».

**A.3 Outcomes block (replacing the `01–05` grid):**

> **Pieci sasniedzamie rezultāti**
> - **O1** — Atpazīt laboratorijas traukus un piederumus · 4. nodaļa, Q5–Q6
> - **O2** — Nolasīt skalas un bireti · 5. nodaļa, 2B Q2
> - **O3** — Lietot zīmīgos ciparus · 8. nodaļa, Q1–Q4
> - **O4** — Zīmēt un lasīt grafikus · 9.–11. nodaļa, Q7–Q8
> - **O5** — Pārveidot mērvienības · 2. nodaļa, Q4

**A.4 Calibration tool out-of-range message (verbatim reuse from ch10):**

> Signāls A = {v} ir ārpus kalibrētā diapazona (A = 0,0106…0,975, kas atbilst 5–30 mg/L). Aprēķinātā vērtība ir ekstrapolācija, nevis mērījums — to nedrīkst ziņot kā rezultātu bez atšķaidīšanas vai jaunas kalibrācijas.

**A.5 Half-life default unit hint:**

> Pussabrukšanas periodu ievadiet tādā pašā mērvienībā, kāda dota uzdevumā (parasti sekundes). Ja ievadāt dienās, pārrēķins uz sekundēm notiek automātiski un tiek parādīts starpvērtību rindā.

**A.6 Colophon (draft):**

> **Par šo dokumentu.** Šis ir patstāvīgs mācību palīglīdzeklis Medicīniskās ķīmijas 2. tēmai, veidots no kursa izdalītajiem PDF un pārbaudīts ar aprēķinu skriptiem. Tas nav RSU izdots materiāls un neaizstāj ne lekciju, ne praktisko darbu, ne docētāja norādes. Skaitļi, kas iegūti no avotiem, ir atzīmēti «avotā»; standarta zināšanas — «papildinājums»; izdomāti piemēri — «ilustratīvs piemērs». Avota kļūdas nav labotas klusējot: tās ir 16. pielikuma izmaiņu žurnālā. Izdevums: {edition} · {date} · būves SHA {sha}.

---

# Appendix B — Lecturer questions (copy-paste, Latvian)

1. *«Kāds ir kursa oficiālais jumta termins angļu “accuracy” nozīmē — “kopējā tuvība”, “kopējā precizitāte” vai “pareizība”? Dokumentā lietoti visi trīs; gribu vienoties par vienu.»*
2. *«Ar cik zīmīgajiem cipariem jāziņo kalibrēšanas taisnes slīpums (0,0322 vai 0,03217) un krustpunkts?»*
3. *«Vai B klases mērtraukiem kursā lietotā 0,5 % pieļaujamā kļūda ir kursa vienošanās, vai tā jālasa no trauka marķējuma?»*
4. *«2B Q2 uzdevumā kopā izlietoti 28,30 mL. Vai laboratorijā ir 50 mL birete, vai arī students drīkst papildināt 25 mL bireti?»*
5. *«Vai ieskaites eksemplāram atbildes jābūt atvērtas (mācību izdevums) vai aizvērtas (jautājumu izdevums)?»*
6. *«Vai blīvuma–temperatūras tabula ir eksaminējama arī ārpus 20 °C?»*
7. *«Vai 220 s pussabrukšanas perioda piemērā pareizā atbilde ir 3,7 min (2 zīmīgie cipari), nevis 3,67 min?»*
8. *«Kāda ir kursa prasība pret mērvienību pierakstu: “mg/100 g” ar atstarpi vai “mg/100g”?»*

---

# Appendix C — Measurement snippets used in this inspection

**C.1 Counts**

```bash
python3 - <<'PY'
import re, collections
h = open('Master_2_tema_merijumi_un_grafiki.html', encoding='utf-8').read()
print('tables', len(re.findall(r'<table\b', h)))
print('figures', len(re.findall(r'<figure\b', h)))
print('svgs', len(re.findall(r'<svg\b', h)))
print('details', len(re.findall(r'<details\b', h)))
print('recall', len(re.findall(r'id="recall-\d+"', h)))
print('h3', len(re.findall(r'<h3\b', h)))
ids = re.findall(r'\sid="([^"]+)"', h)
print('dup ids', [k for k,v in collections.Counter(ids).items() if v>1])
links = set(re.findall(r'href="#([^"]+)"', h))
print('broken anchors', [l for l in links if l not in set(ids)])
PY
```

**C.2 Prose em dashes (excluding quotes, script, style)**

```bash
python3 - <<'PY'
import re
h=open('Master_2_tema_merijumi_un_grafiki.html',encoding='utf-8').read()
b=re.sub(r'<script.*?</script>','',h,flags=re.S)
b=re.sub(r'<style.*?</style>','',b,flags=re.S)
b=re.sub(r'<span data-quote="true">.*?</span>','',b,flags=re.S)
t=re.sub(r'<[^>]+>',' ',b)
print(t.count('—'))
PY
```

**C.3 Mobile overflow (Playwright)**

```js
const vw = document.documentElement.clientWidth;
const out = [...document.querySelectorAll('body *')].filter(e => {
  const r = e.getBoundingClientRect();
  return r.width > 0 && r.right > vw + 1 && getComputedStyle(e).position !== 'fixed';
}).map(e => e.tagName + '.' + e.className);
console.log(vw, out.length, out.slice(0, 10));
```

**C.4 Print page count and waste**

```bash
google-chrome --headless --no-sandbox --no-pdf-header-footer \
  --print-to-pdf=/tmp/m2.pdf "file://$PWD/Master_2_tema_merijumi_un_grafiki.html"
pdfinfo /tmp/m2.pdf | grep Pages
pdftotext -bbox-layout /tmp/m2.pdf - | grep -c '<page'
```

**C.5 Tool edge cases**

```js
const i = document.getElementById('calA'), o = document.getElementById('calOut');
for (const v of ['', 'abc', '0', '0,982', '999', '-5']) {
  i.value = v; i.dispatchEvent(new Event('input', { bubbles: true }));
  console.log(v, '→', o.innerText.replace(/\s+/g, ' ').slice(0, 120));
}
```

**C.6 Reproducible build**

```bash
mkdir -p /tmp/repro && cd /tmp/repro
cp -r "$OLDPWD/build" . && cp "$OLDPWD/Master_2_tema_merijumi_un_grafiki.html" before.html
python3 -I build/build_doc.py && sha256sum before.html Master_2_tema_merijumi_un_grafiki.html
```

---

# Appendix D — Finding → task matrix

| Finding | Task(s) | Finding | Task(s) |
|---|---|---|---|
| A-01 | N01 | C-01 | N06 |
| A-02 | N02 | C-02 | N05 |
| A-03 | N01, N02 | C-03 | N07, N18 |
| A-04 | N01 | C-04 | N15, N16 |
| A-05 | N01, N09 | C-05 | N06, N19 |
| A-06 | N01, N08 | C-06 | N06 |
| A-07 | N02 | C-07 | N19 |
| A-08 | N01 | C-08 | N09 |
| A-09 | N01, N20 | C-09 | N03, N08 |
| B-01 | N08 | D-01 | N10 |
| B-02 | N03 | D-02 | N10, N13 |
| B-03 | N03 | D-03 | N10 |
| B-04 | N03, N14 | D-04 | N10 |
| B-05 | N19 | D-05 | N11 |
| B-06 | N03, N12 | D-06 | N11 |
| B-07 | N03 | D-07 | N10 |
| E-01 | N18 | D-08 | N11, N15 |
| E-02 | N14 | D-09 | N13 |
| E-03 | N19 | D-10 | N13 |
| E-04 | N19 | F-01 | N14 |
| E-05 | N19 | F-02 | N14, N15 |
| G-01 | N13 | F-03 | N14 |
| G-02 | N13 | F-04 | (strength) |
| G-03 | N13 | F-05 | N14 |
| G-04 | N13, N20 | F-06 | N14 |
| G-05 | N13 | H-01 | N16 |
| G-06 | N13 | H-02 | N16 |
| I-01 | N18, N04 | H-03 | N15 |
| I-02 | N18, N04 | H-04 | N15 |
| I-03 | N19 | H-05 | N12, N14 |
| I-04 | N18 | H-06 | N16 |
| I-05 | N18 | J-01 | (strength) |
| I-06 | N18 | J-02 | N20 |
| I-07 | N19 | J-03 | N12, N20 |
| I-08 | N19 | J-04 | N20 |
| | | J-05 | N20 |

---

# Appendix E — What not to do (hard stops)

1. Do not hand-edit `Master_2_tema_merijumi_un_grafiki.html`. It is a build artefact.
2. Do not "fix" a source quotation. Keep it in `<span data-quote="true">` and correct it in the D-register.
3. Do not remove the confidence labels (`C/H/V`) from the defect register.
4. Do not allow a number into prose that is not generated or checked.
5. Do not add a dependency to save 20 lines of code.
6. Do not turn a figure into decoration; delete it instead.
7. Do not introduce a second accent colour, a second font family, or a card grid.
8. Do not gamify. No points, no streaks, no badges.
9. Do not "improve" pagination by shrinking type below the print scale.
10. Do not claim axe, screen-reader, cross-browser, device or physical-print QA that was not run.
11. Do not delete `build/_archive/` history to make the folder tidy.
12. Do not let a redesign touch the spine (§8.2).

---

# Appendix F — One-page kickoff brief (paste to the next agent)

> **Job:** execute Wave A of `Master_2_tema_20_task_plan_v2.md` against `/home/robertsrff/Chemistry_Med/Chemistry_2`.
> **Start with:** freeze `build/baseline/v2/` (html + pdf + sha256), then N01.
> **Never:** edit the five source PDFs or `workspace_skills/`; never hand-edit the root HTML; never invent a fact; never add a dependency; never gamify.
> **Always:** edit `build/…`, run `python3 -I build/build_doc.py`, then `bash build/check_all.sh` (N20 creates it; until then run the individual checkers).
> **Definition of done for the wave:** the change log and the artifact agree on every count and date; the four double-ordinal lists render correctly; every document coinage is defined or removed; every shared constant has one source.
> **Report:** files changed, build SHA, gates run, measured deltas, what was not verified.

---

*End of plan v2. The first executable step is Wave 0: freeze the baseline. The first task is N01, because a document that cannot count itself cannot be trusted about anything else.*
