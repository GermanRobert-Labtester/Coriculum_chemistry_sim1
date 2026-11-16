# 20-task deep revision plan (v2) — `Master_3_tema_skidumi_un_koncentracijas.html`

**Workspace:** `/home/robertsrff/Chemistry_Med/Chemistry_3`
**Document under revision:** `Master_3_tema_skidumi_un_koncentracijas.html` (566.2 KB, 16 chapters, 109 A4 print pages)
**Inspection date:** 2026-11-01
**Supersedes:** `TASKS_20_Master_3_tema_Improvement_Plan.md` (v1, 2026-10-31). Several v1 findings are **already fixed** in the current build; this file re-verifies everything and removes finished work. See §1.2.
**Axes:** terminology · correctness polish · anti-slop redesign & restyle · explanation precision & graspability · retexturing · feature add-ons · more SVGs · correct SVG design
**Status of this file:** investigation + plan only. No source, build file, figure or style has been edited by writing it.

---

## 0. How to read this file

Visual checks in this plan must follow `workspace_skills/VISUAL_VERIFICATION.md`: falkon/falkon first, screenshot capture and direct inspection required; Chrome/Chromium references are fallback-only under that policy.

1. **§1** says what the document is *today*, measured, and what changed since v1.
2. **§2** is the evidence ledger `E01…E28`. Every task cites ledger IDs. If a claim is not in the ledger, it is not a claim — do not build a task on it.
3. **§3** is the 20-task map with axes and dependency order.
4. **§4** explains the task template.
5. **§5** is the 20 tasks. Each task has: evidence → definition of done → touch points → **three moves** → **2–3 work packets, each with three substeps** → acceptance → reject-if.
6. **§6** is the feature backlog `F01…F14`, each mapped to the task that ships it.
7. **§7** sequences the work into five waves; **§8** is the copy-paste acceptance gate; **§9** non-goals; **§10** questions for the lecturer; **§11** change log.

**Rule of precedence:** `PROMPT_Master_html_3_tema.md` §6 (design contract) > `AGENTS.md` > any skill. Where this plan and the prompt disagree, the prompt wins; where this plan and *measured reality* disagree, re-measure before believing either.

---

## 1. Executive summary

### 1.1 What the document is today (all numbers re-measured on 2026-11-01)

| Property | Measured | How |
|---|---:|---|
| Build | **passes**, 0 errors | `python3 build/build.py` |
| Size | 566.2 KB, one file, 1 `<style>`, 1 `<script>` | `wc -c` |
| External requests | 0 | grep for `https?://` in `src`/`href` |
| Chapters | 16 (`n1`–`n16`) | `<section class="chapter"` |
| Worked tasks | 67 (50 «avotā», 17 «papildinājums») | `<article class="task"` |
| Tables | 32, all captioned, numbered, in order | build gate |
| Figures | 9 inline SVG | `build/figures/*.svg` |
| `<details>` blocks | 151 | count |
| Recall items | 75 bank + 69 inline = 144 | count |
| Term definitions | 25 `<dfn id="term-…">` | build output |
| Equation audit | 264 equalities parsed, 0 failures, 12/12 fixtures | `build/equations.py` |
| Print | 109 pages A4, fonts embedded | `pdfinfo` |
| Words | 29 445 | tag-stripped count |
| Scrim/contrast | ink/ground 13.47 : 1; muted 5.81; accent 6.30; ink/mistake 8.44 | `build/qa/report.json` |
| Anti-slop lint | 0 FAIL, 2 WARN (1 outlined box, 145 em dashes) | `lint.mjs` |

This is a mature document: it separates source from addition, recomputes every printed equality, registers 23 source defects (K1–K23, all present), keeps a change log, and ships a print edition. The remaining work is **precision, craft and teaching**, not repair from zero.

### 1.2 What changed since the v1 plan (do not redo these)

| v1 finding | Current state |
|---|---|
| P2 printed the false intermediate `1020 g` | **Fixed.** `tasks_a.py` now prints `1000 · 1,03 = 1030 g`; the build has a dedicated P2 regression gate. |
| Figures numbered in authoring order (`2,4,3,9,1,…`) | **Fixed.** `assert_figure_order()` validates caption number + chapter + kind against `FIG_ORDER`; document order is now 1…9. |
| Duplicate anchors `t-c11`/`C1.1` | **Fixed.** `assert_unique_ids()` passes; 0 duplicate ids, 0 unresolved `href="#…"`. |
| Terminology regressions (`šķīdinātājs — šķīdinātājs`, `w(V)`, `ir nav pārbaudīta`) | **Fixed and gated** by explicit banned-string checks in `build/build.py`. |
| Heading family changes mid-hierarchy | **Fixed.** h1–h4 all `Noto Serif` (`head.html:122–127`). |
| Skip link inside `<main>` | **Fixed.** First element in `<body>`, targets `#saturs`, `main` has `tabindex="-1"`, build-enforced. |
| Callout taxonomy drift | **Partially fixed.** `rolecheck.py` now enforces 5 roles with exact labels. |
| O1–O5 double numbering | **Fixed** (`<ol>` items carry no manual `O1.` prefix). |

Consequence: any agent working from the v1 file will waste its first session re-discovering fixed defects. Use this file.

### 1.3 The ten findings that actually matter now

1. **The document duplicates its own answers and the copies disagree.** 12 inline recall prompts repeat a chapter-15 bank item; **11 of the 12 answers differ** in wording or content (e.g. `c(Na⁺)` for Na₂SO₄ gains/loses the sulfate line). Two sources of truth for one fact (E03).
2. **The font subset is incomplete, so the print PDF falls back to a system font.** 11 characters used in the document (`-§÷→↔⇌√≈≠≪◆`) are absent from the text/serif subsets, and `NotoMath`'s `unicode-range` omits `÷`, `≪`, `§`, `◆`. The PDF therefore embeds `NimbusSans-Regular` as **Type 3** (E06).
3. **The print PDF is untagged and bookmark-free.** `Outlines 0`, `StructTreeRoot 0` (E07). A 109-page study document with no PDF outline is hard to navigate on a laptop the night before a test.
4. **Every figure must be panned horizontally on a phone.** All 9 figures set `--figure-min-width: 947–991 px` inside a 390 px viewport (E04). The `aria-hidden` scroll hint is the only affordance.
5. **The flagship diagram, the quantity map, labels its edges wrongly.** `('n','V','c')` puts a `c` label on the n–V edge while `c` is also a node; a hand-drawn curve `M 390 165 C 470 470 …` carries the label `V` at the bottom of the canvas. A student reading `n —c→ V` will conclude `c = n·V` (E10).
6. **One figure class is invisible.** `fig-leader` is used by `figures.py:161` but has **no CSS rule**, so the four leader lines in `particle_scale` never render (E09).
7. **Figure text is effectively 7.6–11 px on screen.** Fig labels are 10–14 SVG user units in an 860–900 viewBox that is displayed at ~660 px in the reading column (E12).
8. **The reading column wastes ~390 px at 1440 px.** Layout is `218 + 58 + minmax(0,1fr)` inside 1320, but children cap at `66ch` (660 px), leaving a large dead right margin — the exact place a margin-note rail belongs (E15).
9. **Teaching depth is uneven.** 56 of 67 tasks have no «Biežākā kļūda» block, 37 have no source note, only 9 declare an assumption, 8 have a «Kāpēc šādi» block of ≤20 words, and 17 tasks share a route sentence with another task (E13).
10. **The QA harness prints a false alarm.** `report.json` reports `contrast.ink_verified = 1.445` — that is a *transparent* background composited as black, not a real contrast failure. A reader of the report will "fix" a non-problem (E08).

### 1.4 What this plan optimises for

A first-year medical student, 20 minutes before a seminar, on a laptop or a phone, with a calculator and two tests at ≥55 %. Design decisions are judged by **where the eye lands first, whether the number can be trusted, and whether the next step is obvious** — not by novelty.

---

## 2. Evidence ledger (measured, reproducible)

Every ID here was produced by a command run in this workspace on 2026-11-01. Reproduce with the command given; if a number moved, update the ledger before writing a task that depends on it.

| ID | Finding | Evidence / command |
|---|---|---|
| **E01** | Build passes; 566.2 KB; 67 tasks; 75 recall items; 25 term definitions; 264 equations, 0 failures; 12/12 fixtures; 9 figures | `python3 build/build.py` |
| **E02** | 16 chapters, 32 tables, 151 `<details>`, 144 recall items, 0 duplicate ids, 0 broken anchors | python count over the built file |
| **E03** | 12 inline recall prompts duplicate a bank item; **11 answers diverge**; e.g. `c(Na⁺) 0,20 mol/L Na₂SO₄` → inline "2·0,20 = 0,40 mol/L; c(SO₄²⁻) = 0,20 mol/L" vs bank "2 · 0,20 = 0,40 mol/L" | python parse of `<details class="recall">` pairs |
| **E04** | At 390 px viewport: **9/9 figures** overflow (947–991 px), **8 tables** overflow (449 vs 484–715 px) | injected `scrollWidth > clientWidth` probe in headless Chrome |
| **E05** | At ≤430 px the route mini-graph is `display:none` — the document's core "route" metaphor disappears exactly where comprehension is hardest | `build/head.html:342` |
| **E06** | 11 used characters missing from all text subsets; `NotoMath` range lacks `÷` `≪` `§` `◆`; PDF embeds **Type 3** `NimbusSans-Regular` and Type 3 `NotoSansMath` | `fontTools` cmap vs document char set; `pdffonts build/qa/master-print.pdf` |
| **E07** | Print PDF is untagged and has no outline | `pdfinfo` + byte scan: `Outlines 0`, `StructTreeRoot 0` |
| **E08** | `report.json` `contrast.ink_verified = 1.445` is a measurement artifact: `.role-verified` has `background:transparent`, and the probe composites it as black | `build/qa/report.json`, `build/head.html:149` |
| **E09** | `fig-leader` used 4× in `particle_scale`, no CSS rule → leader lines invisible | `figures.py:161`; `grep fig-leader build/head.html` → empty |
| **E10** | Quantity map: `('n','V','c')` labels the n–V edge `c` although `c` is a node; `('c','g','M')` labels c–γ `M`; a hand-drawn curve from m to γ is labelled `V` at `(560,466)` | `build/figures.py:98–107` |
| **E11** | Same figure states `450 mL 0,10 mol/L` (row label) and `450 mL · 0,1 mol/L` (bar note) — two sig-fig conventions, 40 px apart | `figures.py:309` + generated SVG |
| **E12** | Figure type is 10–14 user units in an 860–900 viewBox shown at ~660 px → **7.6–11 px** effective; below the 12 px floor used elsewhere | `figures.py` `font-size` values vs CSS measure |
| **E13** | 56/67 tasks have no «Biežākā kļūda»; 37/67 no source note; 9/67 an explicit assumption; 8/67 «Kāpēc šādi» ≤20 words; 17 tasks share a route string | python over `TASKS` |
| **E14** | Concept coverage 58/66 (87.9 %); missing `A2 mols, A8 mmol/µmol, D1 Arrēniuss, D2 elektrolīts, M7 noapaļošana, M8 vienību pārbaude, R1 neitralizācija, S1 dispersā sistēma` | `build/recall.py` `INVENTORY` + report |
| **E15** | ~390 px of dead right margin at 1440 px: 1264 content − (218 toc + 58 gap) − 660 measure ≈ 328 inside the column, +120 outer | `head.html:96–100`, `report.json` `pMeasure: 660` |
| **E16** | 2 tracked-uppercase micro-label rules (`ĪSIE CEĻI`, recall labels) — a named anti-slop tell | `head.html:104`, `:277` |
| **E17** | 151 `<details>` share one shape: surface fill + 6 px left bar — the most repeated visual element in the document | `head.html:158` |
| **E18** | Real contrast is sound (ink 13.47, muted 5.81, accent 6.30, text-on-mistake 8.44). The palette is **not** the problem; only E08 is | `report.json` |
| **E19** | `lint.mjs`: 0 FAIL, 2 WARN — 1 px outlined box (`head.html:288`), 145 em dashes | `node …/lint.mjs` |
| **E20** | All K1–K23 defect rows present; change log has 26 dated lines, all `2026-11-01` | table/parse |
| **E21** | Source coverage: C 1.1–4.2 + C5–C27 (31 items), B Ex1–10 + 1*–6*, self-checks 1/2 via P8/P9, self-checks 4–10, D/E P1–P13 | `TASKS` `src` field |
| **E22** | 29 445 words / 109 pages; 66ch measure: 18 px/1.6 body, 27.2 px line at 390 | `report.json` |
| **E23** | QA screenshots (`build/qa/*.png`) are from the build at 16:53; `QA_STATUS` states tables/figures were **not** browser-checked after the last layout change | `build/build.py:31`, PNG mtimes |
| **E24** | No in-document search, no per-task scratch input, no unit calculator, no numeric answer check; the only interaction is the chapter-15 recall script | `recall_mode.js` scope |
| **E25** | Print CSS unfolds all `<details>` (`printOpenedDetails: 151`) and drops feature questions — good — but `a{text-decoration:none}` hides all cross-references in print | `head.html:391` |
| **E26** | Only one `@media` breakpoint owns the figure min-width; the hint text is `aria-hidden="true"`, so screen-reader users are told nothing about horizontal panning | `figures.py:70` |
| **E27** | `.role-mistake` uses `--tone-3` (a mid tone) as a full background for 25 blocks — the heaviest surface in the document, used for the *most common* block type | `head.html:151` |
| **E28** | 145 em dashes and 67 × «Kāpēc šādi.» + 67 × «Pārbaude.» make the task blocks read as a template rather than as 67 different problems | text count |

---

## 3. The 20 tasks

Axes: **TERM** terminology · **FIX** correctness polish · **DESIGN** anti-slop/restyle · **TEX** retexturing · **EXPL** explanation depth · **SVG** figures · **FEAT** add-on features.

| # | Task | Axis | Wave | Depends on | Size |
|---|---|---|---|---|---|
| T01 | Terminology lock: one name per quantity, machine-enforced | TERM | 1 | — | M |
| T02 | Number truth: sig-figs, rounding display, cross-surface consistency | FIX | 1 | T01 | M |
| T03 | Type & print integrity: complete subset, no Type 3, tagged PDF, outline | FIX | 1 | — | M |
| T04 | QA that tells the truth: fix the false contrast, refresh evidence, publish coverage | FIX | 1 | — | S |
| T05 | Real reading rail: turn the 390 px void into margin notes | DESIGN/TEX | 2 | T01, T04 | L |
| T06 | Element diet: remove the template tells, keep the structure | DESIGN | 2 | T05 | M |
| T07 | Retexture: a subject-derived surface system, not decoration | TEX | 2 | T05 | M |
| T08 | Typography & prose rhythm: scale, segmentation, hyphenation | DESIGN/EXPL | 2 | T05 | M |
| T09 | Responsive & print redesign: figures that fit, a PDF with a spine | DESIGN | 3 | T07, T16 | L |
| T10 | Explanation depth: a three-part «why», everywhere | EXPL | 3 | T06 | L |
| T11 | Concept graph & prerequisite rail; close the 8 coverage gaps | EXPL | 3 | T04 | M |
| T12 | Task-route pedagogy: the map as a thinking tool, not a badge | EXPL/SVG | 3 | T15 | L |
| T13 | Synthesis artefacts: one sentence per chapter, decision tree, matrices | EXPL | 4 | T10 | M |
| T14 | Latvian register & readability pass | TERM/EXPL | 4 | T01, T10 | M |
| T15 | SVG correctness repair: semantics, classes, collisions, sig-figs | SVG | 2 | T02 | M |
| T16 | SVG design system: type floor, palette, dark/print, guards | SVG | 3 | T15 | L |
| T17 | New figures (8) with a written spec and register update | SVG | 4 | T16 | L |
| T18 | Solve-along workspace: stepwise hints + numeric answer check | FEAT | 4 | T10, T12 | L |
| T19 | Conversion & unit lab (offline, dimension-checked) | FEAT | 4 | T02 | M |
| T20 | Exam pack export: 2-page formula card + triage sheet + search | FEAT | 5 | T09, T13 | M |

Dependency rule: **do not start Wave 2 before Wave 1 gates pass** — a layout rewrite on top of wrong numbers hides the numbers.

---

## 4. Task template (what every task below contains)

- **Evidence** — ledger IDs only, with the one number that justifies the work.
- **Definition of done** — the reader-visible change, in one sentence.
- **Touch points** — exact files.
- **Three moves** — the spine: what to do first, second, third. If an agent does only these three, the task is still a net improvement.
- **Work packets** — 2–3 sub-units, each with 3 substeps. These are the units an agent can actually commit.
- **Acceptance** — checkable by a command or a one-line manual test.
- **Reject if** — the failure mode that means "stop and re-think", not "try harder".

---

## 5. TASKS

### T01 — Terminology lock: one name per quantity, machine-enforced

**Axis:** TERM · **Wave:** 1 · **Depends on:** — · **Effort:** M (1 session) · **Risk:** low

**Evidence.** K5 in `AGENTS.md` §5 still governs the course (C_M / c_M / c / C; w / W / ω / W %; m_šķ / m(šķīdums); `M` as unit *and* as molar mass). The document has converged on `c`, `w`, `γ`, `M`, `ρ` in prose — good — but the *course* uses `C_M`, so a student meets two systems and the document never shows the mapping in one place. `M(M)` is still a live collision (E01 step: `M(NaCl) 58,440` and `mol/L` both in the same output). Terms live in `build/terms.py` (25 `<dfn>`), `build/head.html` and `build/*.html` prose. E28 shows the template risk: 67 identical labels make terminology drift invisible. `AGENTS.md` §3.6 requires `mL`, `L`, `mol/L`, decimal comma, non-breaking space.

**Definition of done.** One canonical symbol per quantity, one canonical Latvian name, one canonical unit spelling; the course's `C_M` shown once with an explicit "the course writes X, this document writes Y" mapping; a lint that fails the build on any reintroduced variant.

**Touch points.** `build/build.py` (banned-string gate, already has a list), `build/terms.py`, `build/ch05_08.html`, `build/ch13_14.html` (the «Apzīmējumu politika» section), `build/ch15_16.html` (formula sheet), `build/taskbase.py` (the `Dots`/`Meklējams` labels).

**Three moves.**

1. **Freeze the vocabulary as data, not prose.** Create `build/lexicon.py` with one row per quantity: `key, canonical_symbol, canonical_latvian, unit, aliases_seen_in_sources, forbidden_in_document, first_defined_chapter`. It becomes the single source for the glossary table, the formula sheet and the lint. Aliases are recorded because the *sources* use them — the document must be able to quote a source without breaking its own rule.
2. **Render the mapping once, visibly.** In chapter 14, above «Ko aizstāt ar ko», add a 6-row table «Kursа pieraksts → šis dokuments → kāpēc»: `C_M → c` (unit mol/L; `M` is reserved for molar mass), `W % → w %` (mass fraction, not mass concentration), `m_šķ → m(šķīdums)`, `ml → mL`, `l → L`, `m/V % → γ` (g/100 mL, the label convention). Each row one sentence of *why*, not just *what*.
3. **Make the lint adversarial.** Move the banned-string list out of `check()` into a table-driven `lexicon.audit(doc)` that returns `(pattern, count, first_context)`; fail on any hit outside a quote/change-log/source-note context (reuse the context test already written for K-defects in `build.py`). Add the *inverse* test: every term defined in `terms.py` must appear in the glossary table and in the formula sheet.

**Work packets.**

#### T01.1 — Build `build/lexicon.py` and wire the audit

1. Write the module with the schema above and 8–10 quantities (`m(viela)`, `n`, `M`, `V`, `ρ`, `w`, `c`, `γ`, `m(šķīdums)`, `m(šķīdinātājs)`), each with the source aliases from `AGENTS.md` K5 verbatim.
2. Add `lexicon.audit(doc)` to `build.py` after `check_units`, returning hard errors for forbidden spellings in prose and warnings for quote contexts. Print counts (`c: 214 uses, 0 variants`) so a silent zero is visible.
3. Add three deliberate regression fixtures to `build/equation_fixtures.py` analogue (`lexicon_fixtures.py`): `CM = 0,5` in prose → FAIL; `C_M` inside a «Piezīme avotam» quote → PASS; `m_šķ` inside the change log → PASS.

#### T01.2 — Publish the course↔document mapping table

1. Draft the six rows in `ch13_14.html`; keep the left column in the *course's* notation so the student recognises it, right column in the document's.
2. Add one sentence per row stating the consequence of confusing them ("`M` raksta arī molmasai, tāpēc `0,1 M` un `M = 58,44 g/mol` vienā rindā ir neskaidri").
3. Link the table from the formula sheet (`ch15_16.html` §16.a) and from chapter 5's opening, so it is reachable from both directions.

#### T01.3 — Unit and name consistency sweep

1. Grep both `mL`/`ml`, `L`/`l`, `mol/L`/`M`, `%`/`procenti` in the built file; produce a diff list; fix prose only (never inside «Piezīme avotam» or the change log).
2. Replace `masas procenti` with `masas daļa, izteikta procentos` on first use in each chapter, then allow the short form — a student who reads only chapter 6 must still get the definition.
3. Re-run the build; require `lexicon: 0 variants, 0 errors` in the output and attach the counts to the change log line.

**Acceptance.**
- [ ] `python3 build/build.py` prints a lexicon line with 0 variants.
- [ ] The mapping table renders 6 rows and is linked from §16.a and chapter 5.
- [ ] No `C_M`, `m_šķ`, `ml`, `l` (unit) outside quote contexts: the existing grep in `AGENTS.md` §8 returns only K-rows.
- [ ] Glossary table and formula sheet agree with `lexicon.py` row-for-row (inverse test passes).

**Reject if.** The lint is implemented as more hard-coded `if bad in doc` strings. The point is a table a lecturer can correct in one place.

---

### T02 — Number truth: sig-figs, rounding display, cross-surface consistency

**Axis:** FIX · **Wave:** 1 · **Depends on:** T01 · **Effort:** M · **Risk:** medium (touches 67 tasks)

**Evidence.** Arithmetic is currently clean (E01: 264 equalities, 0 failures). The problem is **presentation of precision**, which no gate checks. E11: the dilution figure prints `0,10 mol/L` in the row label and `0,1 mol/L` in the bar note, 40 px apart. K15/K12/K21 in the register are exactly this class of defect (the key's own rounding). `AGENTS.md` §3.8 mandates: carry full precision, round once at the end to the least-precise input, print the unrounded intermediate. The document does this per task but never states the **rule** in one place the student can apply under exam pressure, and the build's presence-check of critical strings does not certify significant figures (the build says so itself in a comment).

**Definition of done.** A single visible "precision contract" (one box, one worked micro-example, one table of the course's own offenders), every figure/prose pair agreeing on the number of digits, and a build check that catches digit-count drift between a task's `answer` and its figure.

**Touch points.** `build/ch15_16.html` (add §16.g «Zīmīgie cipari — līgums»), `build/figures.py` (labels), `build/tasks_a.py`, `build/tasks_b.py` (`answer` strings), `build/equations.py`, `build/calc.py`.

**Three moves.**

1. **Write the contract once.** Three rules, one micro-example each: (a) count from the least precise input; (b) round once, at the end; (c) if the answer feeds another step, print the unrounded value in brackets. Then a 6-row table of the course's own cases (C9 `150 g`, C10 `60 mg/mL`, C24 `0,0010 mol`, K21 `13,49 g`, K12 `2,78 mL`, K11 `0,8585 g`) with «avotā → pareizi → kāpēc».
2. **Unify figure labels with the task answers.** Make figures read their numbers from `calc.V` and format through one helper `sig(x, n)` so `0,10` cannot become `0,1`. Every label that repeats a task answer must be generated from the same dict.
3. **Add a digit-consistency gate.** For each figure label of the form `<number> <unit>`, find the matching task answer and compare significant-figure count; mismatch = error. Start with the 9 figures and their ~40 numeric labels; whitelist deliberate counter-examples (K-rows).

**Work packets.**

#### T02.1 — The precision contract page

1. Draft §16.g with the three rules and the six-row offender table; each row links to the task that demonstrates it.
2. Add a 4-line «Kā pārbaudīt savu atbildi 10 sekundēs» checklist (unit cancels → magnitude plausible → digit count ≤ least precise input → reverse-substitute).
3. Link §16.g from every task's `Pārbaude.` line by a single footnote-style marker (`<sup>` with a link to `#n16g`), not by repeating the rule 67 times.

#### T02.2 — Generate figure numbers from `calc.py`

1. Inventory every numeric label in `figures.py` and map it to a `calc.V` key or `MASS`/`MED`/`OST` value; list the unmapped ones (expected: illustrative axis ticks).
2. Add `fmt_sig(value, sig)` to `calc.py` and route all task-derived labels through it; keep axis ticks on their own formatter.
3. Regenerate and diff the 9 SVGs; the only text changes must be the intended ones (currently at least `0,1 → 0,10` in `dilution_ladder`).

#### T02.3 — Digit-consistency gate

1. Write `build/digitcheck.py`: parse figure label numbers + units, parse task `answer` numbers + units, match by unit and proximity of value (±0.5 %), compare sig-fig counts.
2. Wire it into `build.py` with a whitelist keyed by `(figure, label)` for the K-row counter-examples; print `figure numbers: 38 checked, 0 drift`.
3. Add two fixtures: a label with one digit too few must fail; the same label inside a «Piezīme avotam» quote must pass.

**Acceptance.**
- [ ] §16.g exists, is linked from the formula sheet, and contains exactly three rules + six offender rows.
- [ ] `grep -o '0,1 mol/L' build/figures/dilution_ladder.svg` returns nothing; `0,10 mol/L` appears twice.
- [ ] Build prints `figure numbers: N checked, 0 drift`.
- [ ] No task answer gains a digit it cannot support (spot-check C9, C10, C24, P13).

**Reject if.** The gate is satisfied by loosening the tolerance until it passes. Fix the label, not the checker.

---

### T03 — Type & print integrity: complete subset, no Type 3, tagged PDF, outline

**Axis:** FIX · **Wave:** 1 · **Depends on:** — · **Effort:** M · **Risk:** low-medium

**Evidence.** E06: 11 characters used in the document are absent from every text subset and `NotoMath`'s `unicode-range` omits four of them; the PDF therefore embeds `NimbusSans-Regular` (a **system** font) as **Type 3**, contradicting the "no system fonts" claim in `AGENTS.md` §3.9 and `head.html`'s own comment. E07: the PDF is untagged with no outline. Type 3 glyphs are the classic cause of fuzzy text at high zoom and failed copy-paste.

**Definition of done.** Every character in the document is covered by an embedded Noto face; `pdffonts` shows only CID TrueType Noto faces; the PDF has a navigable outline (16 chapters + §16.a–f) and a tagged structure tree.

**Touch points.** `build/fonts.py`, `build/fonts/*.woff2`, `build/head.html` (`@font-face` + `unicode-range`), `build/build.py` (add a pre-write glyph gate), `build/qa.js` / print pipeline (`--print-to-pdf` flags).

**Three moves.**

1. **Derive the subset from the text, not from a remembered alphabet.** Before subsetting, collect the exact code-point set of the *assembled* document (after task/figure/term substitution) and union it with the diacritics list. Subset `Noto Sans` (regular/medium/semibold) and `Noto Serif SemiBold` from that set.
2. **Kill the fallback class.** Either fold the 11 symbols into the text subset (preferred: one face, no `unicode-range` gymnastics) or expand `NotoMath`'s subset *and* its `unicode-range` to the measured set. Then move the `unicode-range` declaration out of a hand-written string into a generated one.
3. **Fix the print artefact.** Emit the PDF with `--export-tagged-pdf` (Chrome ≥ 132 supports it) and verify the outline survives; if the bundled Chrome cannot tag, document the limitation in `QA_STATUS` instead of claiming accessibility.

**Work packets.**

#### T03.1 — Glyph coverage gate

1. Add `build/glyphcheck.py`: reads the assembled doc (before font injection), strips tags, builds the code-point set, and diffs it against each `build/fonts/*.woff2` cmap via `fontTools`.
2. Make it a hard build error listing `codepoint, character, samples of context` so the fix is one line, not an investigation.
3. Add the inverse assertion: the `unicode-range` string in `head.html` must be generated from the NotoMath subset's cmap, not hand-edited.

#### T03.2 — Re-subset and regenerate

1. Re-run the subset command from `build/fonts.py` with the union set; record the input char list in the module docstring so the next agent can reproduce it.
2. Rebuild, then verify in the browser that `≪`, `÷`, `↔`, `⇌`, `≈`, `≠`, `√`, `§`, `◆` render in the document's own face (compare glyph shapes at 400 % zoom against a reference string).
3. Re-export the PDF and require `pdffonts` to list **only** `NotoSans-*` and `NotoSerif-SemiBold`, **zero** Type 3, zero `Nimbus*`.

#### T03.3 — Outline and tagging

1. Test `--export-tagged-pdf` in the current headless Chrome; if it works, check that `h1`–`h4` become tagged headings and the document has a `StructTreeRoot`.
2. Ensure the PDF outline exists (Chrome derives bookmarks from headings; if absent, generate them by inserting named destinations or accept and document).
3. Record the exact print command and its verified flags in `QA_STATUS` and in §16.e «Pārbaudes statuss», with the date.

**Acceptance.**
- [ ] `python3 build/build.py` fails if any used character is missing from any declared face.
- [ ] `pdffonts build/qa/master-print.pdf` → 0 Type 3, 0 non-Noto families.
- [ ] `pdfinfo` → `Tagged: yes` **or** a dated, explicit note in §16.e saying it is not, with the reason.
- [ ] A 400 % zoom spot check of `α ≪ 1` and `1 g/L = 1 mg/mL` shows one consistent face.

**Reject if.** The fix is "add a system-font fallback for those glyphs". That is the defect.

---

### T04 — QA that tells the truth: fix the false alarm, refresh evidence, publish coverage

**Axis:** FIX · **Wave:** 1 · **Depends on:** — · **Effort:** S (half session) · **Risk:** low

**Evidence.** E08: `report.json` reports `contrast.ink_verified = 1.445`. `.role-verified` is deliberately unfilled (`head.html:149`), so the probe measured ink against transparent-black. Anyone reading the report will either distrust the whole QA file or "fix" a correct design. E23: the QA screenshots predate the current build and `QA_STATUS` says tables/figures were not browser-checked — honest, but it means the visual gate is currently *unrun*, not *passed*. E14: coverage is 87.9 % and the 8 gaps are invisible to the student.

**Definition of done.** `report.json` contains no meaningless metric; every metric states what surface it was measured against; the QA screenshots and the HTML are from the same build hash; the document itself shows concept coverage and what is unverified.

**Touch points.** `build/qa.js`, `build/qa/report.json`, `build/build.py` (`QA_STATUS`), `build/ch15_16.html` §16.e, `build/recall.py`.

**Three moves.**

1. **Fix the measurement, not the number.** In `qa.js`, resolve the effective background by walking up the DOM until a non-transparent `background-color` is found; composite alpha; only then compute contrast. Report the resolved colour next to the ratio (`ink on #FBFDFD, 13.47`). Delete `ink_verified` if the block is intentionally unfilled and instead assert "verified blocks have no fill" as a *layout* test.
2. **Make evidence attributable.** Stamp the build with a short content hash (SHA-256 of the HTML, first 8 hex) into a `<meta name="build-id">` and into `report.json`; write the hash into every QA screenshot filename. A screenshot that does not match the current hash is not evidence.
3. **Publish coverage in the document.** Turn `recall.report()` into a small table in §16.e: concept, chapter, covered by which recall item (link), or «nav pārklāts — skatīt T11». 66 rows is too many for prose; a 3-column table with a filter-free, print-safe layout is fine.

**Work packets.**

#### T04.1 — Contrast probe repair

1. Patch `contrast()` usage to composite against the resolved ancestor background; return `{ratio, fg, bg, resolved_from}`.
2. Replace the `ink_verified` metric with two assertions: `verified_bg == transparent` and `ink on ground ≥ 7`.
3. Re-run and diff `report.json`; the only change should be the corrected/removed metric. Commit the diff message as the change-log line.

#### T04.2 — Build ID and evidence freshness

1. Add `build_id = sha256(doc)[:8]` in `assemble()`, inject as meta, pass to `qa.js` via URL or env.
2. Rename QA artefacts to `w1440-ch6-<build_id>.png`; delete or clearly mark stale ones; add a `qa/index.json` listing build id → files.
3. Add a `--check-stale` mode that fails if the newest screenshot build id ≠ current build id.

#### T04.3 — Coverage table in §16.e

1. Extend `recall.report()` to emit structured rows (`concept, chapter, item_id|None`), not a sentence.
2. Render as table «Koncepts · Nodaļa · Kur pārbaudīts»; uncovered rows printed as a short list with a link to T11, not hidden.
3. Print the number in the caption («58 no 66 konceptiem pārklāti, 2026-11-01»), and regenerate the caption on every build.

**Acceptance.**
- [ ] `grep ink_verified build/qa/report.json` → no unqualified ratio; every ratio carries its resolved background.
- [ ] A screenshot from an older build cannot be mistaken for current: name and index both carry the hash.
- [ ] §16.e shows 66 concept rows with 8 explicitly uncovered.
- [ ] No prose claim in §16.e contradicts the numbers.

**Reject if.** The coverage table is generated but the 8 gaps are silently omitted "because they are few".

---

### T05 — Real reading rail: turn the 390 px void into margin notes

**Axis:** DESIGN/TEX · **Wave:** 2 · **Depends on:** T01, T04 · **Effort:** L (2–3 sessions) · **Risk:** medium — this is a layout rewrite

**Evidence.** E15: at 1440 px the text column is 660 px inside a 1264 px content box, leaving ~328 px unused beside it plus 120 px of page margin. The document then puts provenance, source defects and unit notes *inline* (`Piezīme avotam`, 39 blocks; `fig-note`; `prov` labels), which breaks the reading line and is why the prose feels interrupted. The prompt §6 explicitly allows margin-note layout vocabulary. This is the single largest available improvement to reading comfort and to "understandableness" at once.

**Definition of done.** At ≥1180 px the document is a two-track page: a 620–660 px measure plus a 200–260 px annotation rail, with source notes, unit reminders and defect tags living in the rail at the anchor where they belong. Below 1180 px those notes collapse back inline, unchanged in content.

**Touch points.** `build/head.html` (grid, `.layout`, `.chapter > *` max-widths, print rules), `build/ch*.html` (`source-note`, `neutral-note`, `fig-note`), `build/taskbase.py` (note emission), `build/figures.py` (figure captions).

**Three moves.**

1. **Introduce a note primitive, then move one class of content into it.** Add `<aside class="note" data-ref="…">` and a CSS `grid` that places it in the rail at the vertical position of its reference. Start with the **39 `source-note` blocks** — the least ambiguous case, since they are already labelled and short.
2. **Keep one source of truth for the note text.** Render notes from the existing task data (`t['note']`) into the rail; do not duplicate the sentence in two places. If the rail collapses on narrow screens, CSS moves the same node — no second copy, no drift.
3. **Guard the reading measure.** Add a build assertion: at ≥1180 px the `<p>` measure must stay within 60–70 ch and the rail must be 200–260 px; below 1180 px the rail must be hidden **and** the notes must be visible inline (test at 1024/768/390). A note that vanishes at a breakpoint is worse than no note.

**Work packets.**

#### T05.1 — Grid and note primitive

1. Change `.layout` to `grid-template-columns: 218px minmax(0,660px) minmax(200px,1fr)` with `gap: 40px 48px` at ≥1180 px; keep a single-column fallback below.
2. Define `.note` (rail variant): no fill, 2 px left rule in `--line`, `.82rem`, `--ink-muted`; `grid-column: 3`, with `align-self: start` and a small negative top offset so the first line aligns with the reference line.
3. Implement the inline variant as the default (mobile-first), then enable the rail in a `@media (min-width:1180px)` block — this guarantees the content survives without CSS.

#### T05.2 — Migrate provenance and source notes

1. Convert `source-note` to the note primitive for the 39 task notes; keep the label word «Piezīme avotam» as the note's first line (it is load-bearing for the K-defect audit).
2. Move per-chapter «Dokumenta robeža» / «Drošība» notes into the rail where they annotate a specific paragraph; leave the ones that govern a whole chapter as inline blocks.
3. Verify the defect-quote context test still passes (`build.py` warns when a K-string escapes a quote): rail text is still inside a `source-note`-marked node.

#### T05.3 — Measure, collapse and print behaviour

1. Add a headless probe that reports, per breakpoint, `p` measure in ch, rail width, and the count of visible notes; fail if any note is invisible at any width.
2. Fix the `.chapter > * { max-width: var(--measure) }` rule to apply only to prose children, so figures/plates can use the full 860 px including the rail.
3. Extend print: notes print as a right-column aside on A4 with 16 mm margins, or — if the 660+200 split does not fit — as numbered endnotes. Choose one, state it in `QA_STATUS`, and check 6 sample pages.

**Acceptance.**
- [ ] At 1440 px the right rail is occupied on ≥60 % of chapter screens (no large voids next to prose).
- [ ] At 1024/768/390 px every migrated note is visible inline, with identical text (compare text content, not markup).
- [ ] No note is rendered twice in the DOM.
- [ ] Print: 109 ± 8 pages, no note clipped at a page edge, no orphaned note header.

**Reject if.** The rail becomes a decorative sidebar with repeated boilerplate ("Pārbaudīts avotā") — that is a tell, not an annotation.

---

### T06 — Element diet: remove the template tells, keep the structure

**Axis:** DESIGN · **Wave:** 2 · **Depends on:** T05 · **Effort:** M · **Risk:** medium

**Evidence.** E16: two tracked-uppercase micro-labels (`ĪSIE CEĻI`, recall labels) — a named tell in `tells.md` §4 ("tiny uppercase letter-spaced captions"). E17: **151** `<details>` share one visual shape (surface fill + 6 px left bar), making the deepen-blocks read as cards rather than as optional depth. E27: `.role-mistake` uses a mid tone as a full background — the heaviest surface for the most common semantic block, which flattens hierarchy (if everything is tinted, nothing is emphasised). E19: one 1 px outlined box at `head.html:288`. E28: 145 em dashes and 67 identical «Kāpēc šādi.» openers. The lint passes, which shows the lint is not the whole gate.

**Definition of done.** Hierarchy comes from **space, weight and one tone step**, not from repeated bordered surfaces. Every remaining box is justified by a semantic reason a reader could state. The document looks like a considered study text, not like a component library applied to prose.

**Touch points.** `build/head.html` (role/`details`/transfer/toc styles), `build/*.html` labels, `build/taskbase.py` (`<strong>Kāpēc šādi.</strong>`), `build/recall.py` labels.

**Three moves.**

1. **Audit every surface, then delete two thirds.** Table of every element with a background or a border (`role-rule`, `role-mistake`, `role-verified`, `source-note`, `neutral-note`, `details`, `transfer`, `figure`, `chapter-top`, `toc-mobile details`). For each: what does the surface mean? Keep a fill only where meaning is "this is a different *kind* of text" (rule, mistake); keep a rule only where meaning is "this is an annotation" (notes). `details` gets no fill at all — indentation plus a disclosure marker is enough for 151 instances.
2. **Replace the uppercase tell with typographic hierarchy.** `ĪSIE CEĻI` becomes a bold sentence-case line; recall labels stop being uppercase. Where a label must be small, use size + weight + muted ink, never tracking.
3. **Break the 67-fold template.** Vary the `Kāpēc šādi.` opener by *function*: «Kāpēc šis ceļš», «Kāpēc ne savādāk», «Kur šis lūzt», «Ko tas nozīmē praksē» — chosen per task from a small set, and make the build assert each task has at least one of the *negative* kinds (why-not / where-it-breaks) so explanations cannot all be confirmations.

**Work packets.**

#### T06.1 — Surface inventory and decision table

1. Produce the inventory (element, count, fill, border, semantic job) as a table in this plan's appendix or in `build/design-tokens.md` — one row per element, with a keep/remove verdict.
2. Remove `details` background and left bar; replace with a top alignment offset and a marker glyph; verify 151 blocks still read as separable at 390 and in print.
3. Re-tone `.role-mistake`: fill `--tone-1` (same as rule) but with a 3 px ink left rule + bold label, so rule and mistake differ by *label and rule weight*, not by a dark panel.

#### T06.2 — Labels without tracking

1. Rewrite `toc-shortcuts p` and `.recall-block-label` in sentence case at `.86rem`, weight 600, `--ink-muted`; remove `letter-spacing` and `text-transform` from the stylesheet entirely.
2. Rename visible strings where the words were carrying the label's job (`ĪSIE CEĻI` → «Īsie ceļi», «Pārbaudi sevi» stays as is).
3. Grep the built file for `text-transform` and `letter-spacing` and require zero occurrences outside `code`/`kbd`.

#### T06.3 — De-templating the task blocks

1. Define the four `why` openers and their contract in `taskbase.py`; assign per task in `tasks_a.py`/`tasks_b.py` by what the explanation actually does.
2. Add build assertions: every task has a non-empty `why`; ≥30 tasks use a negative-kind opener; no opener repeats more than 20 times.
3. Read 10 tasks end-to-end and remove the second-person filler («Šeit tu vari redzēt…») — keep the arithmetic voice.

**Acceptance.**
- [ ] Zero `text-transform:uppercase` / `letter-spacing` in the stylesheet.
- [ ] ≤2 distinct filled surfaces for text blocks, both semantically justified in `design-tokens.md`.
- [ ] `details` blocks have no fill and remain distinguishable at 390 px and in print.
- [ ] Opener distribution printed by the build; no opener > 20 occurrences.
- [ ] `lint.mjs` still 0 FAIL; the em-dash count is not *increased*.

**Reject if.** The "diet" is implemented as a palette swap. The problem is repetition of shape, not hue.

---

### T07 — Retexture: a subject-derived surface system, not decoration

**Axis:** TEX · **Wave:** 2 · **Depends on:** T05 · **Effort:** M · **Risk:** low-medium

**Evidence.** The palette is already subject-derived and documented: accent = aqueous Cu²⁺ blue-cyan, 6-step tone ladder, measured contrast (E18). What is missing is a **texture logic** — how surfaces differ. Today: `--ground` for the page, `--surface` for figures/details, `--tone-1` for masthead/rule, `--tone-3` for mistakes. That is a mosaic of decisions rather than a system, and the result reads flat: the masthead is one full-bleed tinted band, figures are white cards, tables are grey headers. `AGENTS.md` §6 asks for a **dilution series**: concentration encoded by *tone depth of one hue*, never a gradient. That idea currently exists in the data figures and nowhere in the page.

**Definition of done.** One hue, one documented ladder, and an explicit rule for every surface: what it means, which step it uses, and why. The page gains *tactile* differentiation (paper-free, subtle) without grain, noise, gradients or blobs.

**Touch points.** `build/head.html` (`:root`, masthead, `.figure`, `.table-plate`, `thead`, `blockquote`-like blocks), `build/figures.py` (tone classes), `build/design-tokens.md` (create).

**Three moves.**

1. **Write the texture law.** Three surface families only: *page* (ground), *data* (surface + tone ladder, used by figures and tables), *annotation* (no fill, rule only). Every element maps to exactly one family. Publish it as a 10-line table in `build/design-tokens.md` with the hex/OKLCH of each step and where it is allowed.
2. **Give the data family real structure.** Tables get a `--tone-1` header band and hairline-free row separation via 1 px `--line` only at row boundaries where needed; figures keep `--surface` but lose the extra 18 px card padding where the plate already has a caption. The point: data surfaces look like *measured matter*, prose looks like *page*.
3. **Retexture the masthead without a band.** Replace the full-bleed `--tone-1` block with: ground + one thick rule at the top, the title at display size, and a *small measured ladder strip* (six swatches at 1:2:4:8 spacing) as the only graphic — it is the topic's own visual argument, not decoration. It must be labelled (`w`, `c`, `γ` not shown as decoration) or removed.

**Work packets.**

#### T07.1 — `design-tokens.md` and the surface law

1. Document the 6 tone steps with OKLCH values, the contrast of ink on each, and the single allowed use per step.
2. Add a build assertion that the stylesheet references **no** tone outside the documented set (grep `--tone-` usages, compare to the allow-list).
3. Add the dark-mode mapping table (same 6 steps, re-derived, contrast re-checked).

#### T07.2 — Data surfaces

1. Restyle `thead` to a `--tone-1` band with `--ink` text; remove per-cell borders except a single `--line` under the header and at the table foot.
2. Reduce figure card padding; move the caption into the same surface so a figure reads as one plate, with the `fig-kind` tag aligned to the caption baseline rather than floating.
3. Check 8 tables and 4 figures at 1440/768/390 and in print for "does this read as data or as a card?" — record the verdict per element.

#### T07.3 — Masthead retexture

1. Prototype two masthead variants (rule + ladder strip; rule + nothing) and compare at 1440 and 390 with the deck text; choose by "can a student say what this page is in 2 seconds".
2. If the ladder strip stays, label it honestly (six steps, the caption says what the depth means) and make it non-interactive; if it cannot be labelled in one line, delete it.
3. Update the print masthead to match (no band, rule only) and re-export; check page 1.

**Acceptance.**
- [ ] `design-tokens.md` exists, lists every surface, and is internally consistent with the CSS.
- [ ] No gradient, no image texture, no noise filter, no shadow anywhere (`grep -E 'gradient|filter:|box-shadow'` → only focus rings if any).
- [ ] Dark mode passes the same surface-law table; contrast re-measured and recorded.
- [ ] The masthead change is visible in the 1440 and 390 screenshots and does not push the first chapter below the fold by more than ~40 px.

**Reject if.** "Texture" turns into decorative SVG noise, paper grain, or a gradient. The subject's texture is *concentration*, not paper.

---

### T08 — Typography & prose rhythm: scale, segmentation, hyphenation

**Axis:** DESIGN/EXPL · **Wave:** 2 · **Depends on:** T05 · **Effort:** M · **Risk:** low

**Evidence.** E22: 18 px body, 1.6 leading, 66 ch — sound. But headings are `clamp()`-based with three different ratios (`h1` max 2.6rem, `h2` 1.9, `h3` 1.12 rem — a jump from 1.9 to 1.12 at one level), h1 `line-height:1.1` with `text-wrap:balance` produces the tight two-line masthead seen in the screenshot, and `h3` uses `margin:2.4em` while `h4` uses `1.6em`. Latvian compounds (`koncentrāciju`, `atšķaidīšana`, `šķīdinātājs`) hyphenate badly or not at all: no `hyphens` rule exists, and `text-wrap:pretty` is not used on paragraphs. E22 also shows 354 px measure at 390 — with no hyphenation, that produces the ragged, hard-to-track column visible in `w390-ch1.png`.

**Definition of done.** A documented type scale with consistent ratios, Latvian hyphenation via `lang="lv"` + `hyphens:auto` with `hyphenate-limit-chars`, paragraph-level widow/orphan control, and a heading rhythm that makes the hierarchy obvious without size jumps.

**Touch points.** `build/head.html` (type block, `:root` size tokens), print block, `build/*.html` (only if heading levels are misused).

**Three moves.**

1. **Derive the scale once.** A 1.25 ratio from 1rem: `--step-0: 1rem; --step-1: 1.12; --step-2: 1.4; --step-3: 1.75; --step-4: 2.2`; assign h4→step-1, h3→step-2, h2→step-3, h1→step-4 with fluid clamps *derived from* the steps, not hand-tuned per heading.
2. **Fix Latvian line-breaking.** `html{hyphens:auto}` with `hyphenate-limit-chars: 6 3 3`, `p{text-wrap:pretty}`, and a check that the `lang` attribute is on `html` (already true) so the browser uses Latvian patterns. Verify no hyphenation inside `<code>`, formulas, units or chemical names (`hyphens:none` on those).
3. **Rhythm.** Space above a heading ≈ 2× space below; unify h3/h4 margins on the same scale; set `h2` `line-height:1.22`; reduce the h1 tracking trick; ensure a chapter's first paragraph is visually a *lead* (larger, `--measure` shorter by ~8 ch) rather than an ordinary paragraph.

**Work packets.**

#### T08.1 — Scale tokens and headings

1. Define the five steps and express all headings through them (including the masthead h1).
2. Set `line-height` per step (display 1.15, h2 1.22, h3/h4 1.35, body 1.6) and verify no heading wraps to three lines at 390/768/1440.
3. Add a rule: no heading below h2 may be smaller than body size × 1.1; check `.task h3` (1.1rem) at 18 px body → 19.8 px, passes narrowly.

#### T08.2 — Hyphenation and paragraph shape

1. Add `hyphens:auto` + limits to `html`, `hyphens:none` to `code`, `sub`, `sup`, `.task-id`, table cells with units; test 10 Latvian compounds at 390 px.
2. Add `text-wrap:pretty` to `p` and `li`; check the 6 paragraphs over 60 words (E22) for manual splitting — the goal is ≤3 sentences per paragraph in the reading chapters.
3. Verify no hyphen appears in `0,9 % NaCl`, `mol/L`, `H₂SO₄`, or a task ID at any width.

#### T08.3 — Lead paragraphs and section openings

1. Style chapter leads: `1.04rem`, `--measure - 8ch`, `--ink` (already `.lead` exists — verify it is applied to *every* chapter and only to chapter openings).
2. Rewrite the 4 chapter openings that currently start with a definition list or a table so they start with one sentence saying what question the chapter answers.
3. Check the first screen of all 16 chapters at 1440: the reader must see a heading + a lead + the beginning of substance, not a nav or a table.

**Acceptance.**
- [ ] Heading sizes come from 5 named tokens; no hard-coded `rem` sizes in heading rules.
- [ ] `hyphens:auto` active on prose, disabled on formulas/units/IDs (verified by computed style at 390).
- [ ] No paragraph in chapters 1–12 exceeds 3 sentences *or* 60 words (list the exceptions deliberately kept).
- [ ] 390 px screenshots show no mid-word break inside a unit or a chemical formula.

**Reject if.** Hyphenation is disabled globally "because Latvian looked odd" — that is a font/locale problem to fix, not a reason to keep a ragged measure.

---

### T09 — Responsive & print redesign: figures that fit, a PDF with a spine

**Axis:** DESIGN · **Wave:** 3 · **Depends on:** T07, T16 · **Effort:** L · **Risk:** medium

**Evidence.** E04: **all 9 figures** require horizontal panning at 390 px (947–991 px min-width inside a 390 px viewport), and 8 tables overflow (449 vs 484–715). E26: the pan hint is `aria-hidden="true"` — screen-reader users get no warning. E05: the route mini-graph is hidden below 430 px. E25: print removes all link decoration, so 109 pages of cross-references become invisible. E07: no PDF outline. Together: the two places students actually read (phone, print) are the two places the document is weakest.

**Definition of done.** On a phone every figure is readable **without horizontal panning** (either a responsive alternate layout or a genuine zoom/scroll affordance with a visible, accessible label); tables fit or declare their scroll visually; the route metaphor survives on mobile; the print edition has a navigable outline and visible cross-reference markers.

**Touch points.** `build/figures.py` (viewBox strategy), `build/head.html` (media queries, print block), `build/build.py` (`prepare_tables`), `build/routes.py` (mini graph).

**Three moves.**

1. **Decide the mobile figure strategy per figure, not globally.** Three options: (a) **re-layout** — a second portrait-oriented SVG variant for tall/wide figures, generated from the same data with a different geometry; (b) **reduce data-ink** — fewer ticks/labels so the 900-unit canvas fits 360 px at a 12 px type floor; (c) **zoom plate** — keep the canvas, but add a visible "Palielināt" button that swaps in a full-bleed scrollable version, with an accessible label. Choose per figure and record the choice in the figure register.
2. **Make overflow honest.** Any scrollable region gets a *visible* affordance (gradient-free edge fade is banned; use a static rule + short text "↔ ritini" that is NOT `aria-hidden`), and the container gets `role="group"` + label. Buttons/affordances must be keyboard reachable.
3. **Rebuild the print spine.** Add a generated outline (§T03.3), keep cross-reference numbers visible in print (`a::after{content:" (…)"}` for internal refs, or print the section number), and set `@page` with running heads that carry the chapter, not just the document title.

**Work packets.**

#### T09.1 — Figure-by-figure mobile decision

1. Build a contact sheet of the 9 figures at 390 px width and classify: legible-as-is / needs fewer labels / needs portrait variant / needs zoom.
2. Implement the cheapest class first (label reduction) and re-measure; for the 3 worst (`quantity_map`, `ion_strip`, `neutralisation`), design portrait variants with a vertical reading axis.
3. Add a build check: every figure must declare `data-mobile="fit|zoom|variant"` and the register must show it.

#### T09.2 — Tables and affordances

1. Replace `min-width` table sizing with `table-layout:auto` + a per-table column priority list: which columns may collapse into a second line at 390 (`font-size:.9rem` already) and which must stay.
2. For tables that genuinely cannot fit (8 today), add a visible caption suffix «šī tabula šaurā ekrānā ritināma» and a non-`aria-hidden` hint; keep the `sr-only` description.
3. Restore the route mini on mobile as a 48 px inline glyph **plus** the textual route line (already present), so the idea is not lost when the diagram is hidden.

#### T09.3 — Print spine

1. Regenerate the PDF with tags/outline (from T03.3) and confirm 16 chapter bookmarks + appendix sub-entries.
2. Add chapter running head (left: chapter title, right: page x / y) by using `string-set` if available in the renderer, else accept the current header and document the limitation.
3. Check 8 sample pages: first page of a chapter, a page starting with a table, a page ending with a figure, a page with a long formula, the index page, the change log, the last page.

**Acceptance.**
- [ ] At 390 px, 0 figures require panning **or** every panning figure has a visible, non-`aria-hidden`, keyboard-reachable affordance.
- [ ] The route metaphor is present at 390 px in some form.
- [ ] Print PDF has an outline with ≥16 entries and cross-references are locatable.
- [ ] No table clips a column without a visible cue.

**Reject if.** "Responsive" is achieved by shrinking the SVG (`font-size` in the 5 px range). A figure that is complete but illegible is not responsive.

---

### T10 — Explanation depth: a three-part "why", everywhere

**Axis:** EXPL · **Wave:** 3 · **Depends on:** T06 · **Effort:** L · **Risk:** medium

**Evidence.** E13: 8 tasks have a «Kāpēc šādi» block of ≤20 words (C7, C8, BEx2, C1.1, C2.1, C4.2, BEx5, C18); 56 of 67 tasks have **no** «Biežākā kļūda» block; only 9 state an assumption. The median explanation is 25 words — enough to name the route, not enough to prevent the error the task exists to prevent. The document's own K-register shows that the *interesting* content is the failure mode (K9's reversed ratio, K11's ignored ρ), yet that content sits in a table at the back rather than next to the task that trips on it.

**Definition of done.** Every task explains three things in this order: **why this route** (the choice), **why not the tempting alternative** (the trap), **where it breaks** (the boundary). Every task that can be got wrong in a known way carries the specific wrong answer and its diagnosis.

**Touch points.** `build/tasks_a.py`, `build/tasks_b.py` (67 entries), `build/taskbase.py` (renderer), `build/ch13_14.html` (mistake summary stays as an index, not the only home).

**Three moves.**

1. **Define the three-part contract and the length floor.** `why` must contain: a route justification, a contrast with the tempting wrong route, and a boundary/assumption. Floor ~45 words, ceiling ~90; the build asserts presence of the three functional parts by keyword class (this, not-alternative, boundary), not by word count alone.
2. **Write the trap, not the moral.** For the 25 tasks with a known trap, state the exact wrong number (`n = 2n(NaOH) → 0,02 mol → 1,96 g`) and the one-line diagnosis (`koeficients 2 pieder pie sārma, nevis skābes`). For tasks with no trap, say so explicitly («Šeit tipiskas kļūdas nav; uzdevums ir maršruta treniņš») — silence reads as "nothing to know".
3. **Move the mistake register next to the work.** Chapter 13 stays as a summary, but every K-row links to the task anchor, and every task with a K-row shows the trap inline. A student reading task C14 must not need chapter 13 to learn the failure mode.

**Work packets.**

#### T10.1 — Contract + linter

1. Add `why_parts` metadata to `T(...)` (`route`, `trap`, `boundary`) and render them as three sentences in a fixed order, so the reader learns the pattern.
2. Write `build/whycheck.py`: per task, require the three parts (keyword-class heuristic + manual allowlist), floor/ceiling words, and a non-empty `wrong` for tasks whose `rkey`+source imply a known trap (list them explicitly).
3. Print a table of the 67 tasks × 3 parts in the build output so gaps are visible at a glance.

#### T10.2 — Content pass: the 8 short blocks and the 56 missing traps

1. Rewrite the 8 short explanations first (they are the cheapest visible win) and read them aloud for register.
2. Add a trap block to every task where the source register (K1–K23) or the equation fixtures record a known wrong answer; where none exists, add the explicit "no typical trap" line.
3. Add an assumption line to every task that uses ρ, additive volumes, α = 1, or a rounded M — that is more than the current 9.

#### T10.3 — Cross-linking the register

1. Add `data-k="K9"` to the task article where relevant and render a small inline «Skatīt K9» link to the register row.
2. Make the register row link back to the task (`#t-c21`), so navigation works in both directions.
3. Check 10 links in the built file; require 0 broken, 0 pointing to a non-existent anchor.

**Acceptance.**
- [ ] 67/67 tasks have three-part `why` blocks with distinct openers.
- [ ] 67/67 have an explicit trap statement (real or "none"), and the assumption count rises from 9 to every ρ/α/additivity task.
- [ ] Chapter 13 rows link to tasks and tasks link back (0 broken).
- [ ] Build prints a 67-row completeness table with 0 blanks.

**Reject if.** The three parts become three boilerplate sentences recycled across tasks. If two tasks' `why` blocks differ only in numbers, the task is not done.

---

### T11 — Concept graph & prerequisite rail; close the 8 coverage gaps

**Axis:** EXPL · **Wave:** 3 · **Depends on:** T04 · **Effort:** M · **Risk:** low

**Evidence.** E14: 58/66 concepts covered; 8 uncovered (`A2 mols`, `A8 mmol/µmol`, `D1 Arrēniuss`, `D2 elektrolīts`, `M7 noapaļošana`, `M8 vienību pārbaude`, `R1 neitralizācija`, `S1 dispersā sistēma`). Some are covered *in prose* (mols is defined) but not *retrievable* — which is what the recall bank measures. The document has no prerequisite structure at all: a student who does not understand `n` meets `c = n/V` in chapter 7 with no "you need chapter 4 first" signal. The routes module encodes transitions but only for tasks.

**Definition of done.** A small concept graph (12–16 nodes, the four conversions + five fundamentals) rendered as an SVG or a table, wired so each chapter shows "before this, you need…" and the recall bank covers all 66 concepts.

**Touch points.** `build/recall.py` (`INVENTORY`, `ITEMS`), `build/routes.py`, `build/ch01_04.html`…`ch13_14.html` chapter openings, `build/ch15_16.html` §16.e.

**Three moves.**

1. **Promote the graph to data.** `build/graph.py`: nodes = concepts, edges = "is needed for", with a chapter for each. This is a *teaching* graph, distinct from the task route map (which stays a quantity graph) — do not merge them.
2. **Render it twice, differently.** Once as a compact prerequisite strip at each chapter opening (3–5 chips: "Pirms šīs nodaļas: mols · molmasa · mērvienības", each linked), and once as a full-page plate in the appendix for orientation.
3. **Close the 8 gaps by writing items, not by renaming.** Each uncovered concept gets 1–2 recall items with an answer that is *checkable* (a number or a one-sentence rule), then the coverage table regenerates to 66/66.

**Work packets.**

#### T11.1 — `build/graph.py`

1. Encode 66 concepts with `id, label, chapter, needs[]`; validate no cycles and no dangling ids.
2. Derive the prerequisite strip for each chapter as the transitive closure limited to depth 1–2, ordered by teaching sequence.
3. Add a build assertion that every concept is reachable from chapter 1 by following `needs` — an orphan concept is a design smell.

#### T11.2 — Render the strips and the plate

1. Chapter strips: inline chips, no fill, `--line` rule, `aria-label` = "Priekšnosacījumi"; must not repeat concepts already defined in that chapter.
2. Appendix plate: a left-to-right layered graph (fundamentals → quantities → conversions → applied), generated from `graph.py`, with the same tone ladder as other figures.
3. Check the plate at 390 px: if it needs panning, fall back to a 3-column nested list (and say so in the figure register).

#### T11.3 — Close coverage

1. Draft the 8 missing items with answers traceable to a chapter sentence; add `data-concepts` ids.
2. Add 4 extra items for concepts that are covered by only one item (fragile coverage) — report `concepts covered by ≥2 items` as a second metric.
3. Regenerate §16.e and require 66/66 with ≥40 concepts having ≥2 items.

**Acceptance.**
- [ ] `graph.py` validates: 66 nodes, 0 cycles, 0 orphans.
- [ ] Every chapter shows a prerequisite strip that is correct (spot-check 5: chapter 7 needs molmasa; chapter 10 needs c and n; chapter 11 needs c and the 1:1/1:2 ratios).
- [ ] Coverage 66/66; §16.e regenerated and consistent.
- [ ] The graph plate is one of the registered figures with a caption and a source note («shēma, veidota no dokumenta struktūras»).

**Reject if.** The prerequisite strips are added but the missing concepts are "covered" by renaming an existing item's concept tag.

---

### T12 — Task-route pedagogy: the map as a thinking tool, not a badge

**Axis:** EXPL/SVG · **Wave:** 3 · **Depends on:** T15 · **Effort:** L · **Risk:** medium

**Evidence.** E05 + the 1440 screenshot: the `route-mini` graph is 112×70 px, 8 tiny nodes, `rm-edge` at 1.2 px in `--tone-3` — it reads as a decorative squiggle, not as information. It is the *signature* of the document (the prompt §6 calls the route-over-a-map the core device), yet it is too small to read, disappears on mobile, and its only encoded state is "which nodes are on" (`rm-on`). E13: 17 tasks share a route string, so the mini graph repeats identically for a fifth of the tasks — repetition without variation turns a teaching device into wallpaper.

**Definition of done.** For every task, the route is legible at a glance (≥14 px labels, ≥2 px strokes), shows **direction** and **which quantity was given vs found**, and the same information is available in text for screen readers and mobile. Where two tasks share a route, the diagram highlights the *different* input rather than looking identical.

**Touch points.** `build/routes.py` (mini renderer), `build/head.html` (`.route-mini`, `.rm-*`), `build/taskbase.py` (route heading), `build/calc.py` (given/found per task).

**Three moves.**

1. **Re-specify the mini graph.** 5×3 grid instead of 8 free nodes; each node 18×18 with a 10–11 px label *outside* the box; given node = filled accent, found node = ring, traversed nodes = mid tone, untraversed = outline only. Add a direction arrowhead on the traversed path (one arrow, not eight).
2. **Make it informative, not decorative.** Derive `given`/`found` from task data (`dots`/`find` fields already exist structurally — add explicit `from`/`to` keys). If two tasks share a route, the mini must differ by which node is filled.
3. **Guarantee the text fallback.** The `Maršruts` line stays (it is the accessible version) and is rewritten as an arrow chain with the given→found endpoints bolded, so mobile and screen-reader users get the same information at full fidelity.

**Work packets.**

#### T12.1 — Route data model

1. Add `path: ['c','n','m']`, `from: 'c'`, `to: 'w'` to each task; validate that `path` is a connected walk on the quantity graph in `routes.py`.
2. Derive `rkey` from `path` where possible; keep `rkey` for the 4 canonical conversions and mark the composed ones.
3. Build assertion: every task's `from`/`to` appears in its `dots`/`find` text (catches copy-paste drift).

#### T12.2 — Redraw the mini

1. New geometry: fixed grid coordinates per quantity, orthogonal edges with 4 px radius, one arrowhead at the final edge, 10 px labels with `dominant-baseline` set, all in `currentColor`-safe classes.
2. Encode state via `rm-given` / `rm-found` / `rm-pass` classes with tone steps 5/6/3 and a 2 px stroke; verify at 112×70 and at 2× zoom.
3. Regenerate all 67 and visually diff 6 tasks that share a route — they must be distinguishable.

#### T12.3 — Text mirror

1. Rewrite the `Maršruts` line format: `c → n → m → w`, with `from`/`to` wrapped in `<strong>`; keep the explanatory sentence after a dash.
2. Restore a small route glyph for mobile (48 px) or, if T09.2 chose otherwise, ensure the bolded text chain is enough — test with the 390 screenshot.
3. Add `aria-label` on the mini SVG: "Maršruts: dots sākas ar c, beidzas ar w, starpā n un m" — generated, not hand-written.

**Acceptance.**
- [ ] 67 minis, 0 identical pairs that have different from/to.
- [ ] Labels ≥10 px in the SVG's own units and legible in the 1440 screenshot.
- [ ] The route text alone conveys the same start/end.
- [ ] Mobile shows the route in some form.
- [ ] `aria-label` present and accurate on all 67.

**Reject if.** The mini is enlarged but still only says "these nodes are on" — that is a progress badge, not an explanation.

---

### T13 — Synthesis artefacts: one sentence per chapter, decision tree, matrices

**Axis:** EXPL · **Wave:** 4 · **Depends on:** T10 · **Effort:** M · **Risk:** low

**Evidence.** The document is 29 445 words and 109 pages. There is no chapter-level summary, no "which concentration do I need?" decision aid, and no single comparison matrix for the three concentration types across all six attributes the student must distinguish (symbol, formula, unit, what is measured, what it is used for, what it is confused with). A student revising at speed has to re-read to reconstruct the shape. `AGENTS.md` §2.1 maps tasks; nothing maps *decisions*.

**Definition of done.** Every chapter opens or closes with one bold sentence stating its single takeaway; a one-page decision tree answers "what is being asked, therefore which formula"; the concentration matrix exists once and is linked from chapters 5–9.

**Touch points.** `build/ch*.html` (chapter ends), `build/ch05_08.html` (matrix), `build/ch15_16.html` (§16.a formula card), `build/figures.py` (decision-tree SVG, if drawn).

**Three moves.**

1. **Write the 16 takeaway sentences.** One sentence each, present tense, second person, no hedging, ≤22 words: "Ja dota masa un šķīduma masa, lieto w; ja dots tilpums, vispirms vajag ρ." These go at the chapter head as a distinct `p.takeaway` (not another callout box).
2. **Draw the decision tree once.** Root: "Ko uzdevums prasa?" → w / c / γ / n / m → each branch lists the *given* combination and the formula. Six leaves, one page, printable. It is a genuine tree, not a mind map.
3. **Build the 3×6 matrix.** Rows w, c, γ; columns symbol, formula, unit, denominator, typical use, the confusion it causes. Must survive print at A4 portrait; if it does not, split into 3 rows.

**Work packets.**

#### T13.1 — Takeaways

1. Draft 16 sentences; run each through the test "could a student act on this without the chapter?".
2. Place them consistently (chapter head, after the lead, one line, `--ink`, weight 600, no icon, no colour).
3. Build check: 16 chapters, 16 takeaways, each ≤22 words and containing a verb.

#### T13.2 — Decision tree

1. Enumerate every task's given→asked pair (67 tasks) and cluster into ≤8 input patterns.
2. Draw the tree as an SVG (or a nested `<ol>` if the tree exceeds 7 branches) with the same node/edge conventions as T16.
3. Test it: give a student 5 tasks and the tree; they must find the branch in <20 s. If not, the tree is wrong.

#### T13.3 — Concentration matrix

1. Write the 18 cells with the *confusion* column being the sharpest one (w vs γ under ρ ≈ 1; c vs `M`; γ vs m/V label percent).
2. Verify every cell against `lexicon.py` and the K-rows (K5, K6, K23).
3. Link it from chapters 5, 6, 7, 8, 9 and from the formula sheet; add a "matrix" entry to the table index.

**Acceptance.**
- [ ] 16/16 takeaways, ≤22 words, build-checked.
- [ ] Decision tree answers 5 random tasks in <20 s (manual test, recorded).
- [ ] Matrix has 18 cells, all consistent with `lexicon.py`; usable in print.
- [ ] Number of "how do I start?" prose paragraphs decreases (count before/after).

**Reject if.** The takeaway lines are restatements of the chapter title ("Šajā nodaļā aplūkosim masas daļu").

---

### T14 — Latvian register & readability pass

**Axis:** TERM/EXPL · **Wave:** 4 · **Depends on:** T01, T10 · **Effort:** M · **Risk:** low

**Evidence.** The prose is competent but institutional in places: heavy nominalisation («aprēķinu veikšana», «pielietošana»), long pre-noun genitive chains («šķīduma masas daļas aprēķināšanas piemērs»), and mixed register between the source-flavoured task text and the modern explanatory text. `AGENTS.md` §3.5 requires the course's Latvian forms; §3.4 forbids silent correction of source wording. There is no style sheet for the *document's own* voice, so each of ~30k words is editorial judgement.

**Definition of done.** A short, explicit house style (voice, person, tense, how to name the reader, how to quote a source, allowed anglicisms), applied consistently; sentence length and nominalisation measured; the glossary carries English equivalents.

**Touch points.** `build/*.html` prose, `build/terms.py` (glossary), create `build/style-lv.md`, `build/ch13_14.html` (glossary section).

**Three moves.**

1. **Write the house style in 12 rules.** Person («tu» for the student, «mēs» only for the document's own decisions), tense (present for rules, past for what the source says), quoting (guillemets + «avotā»), numbers (decimal comma, NBSP, no «apm.» except in illustrative cases), anglicisms (keep `pH`, `mol`, drop `тренд`-class words), and the three words that must never be synonyms (`šķīdums`, `šķīdinātājs`, `izšķīdinātā viela`).
2. **Measure, then fix the worst 10 %.** Compute sentence length distribution and a nominalisation heuristic (`-šana`, `-ums` nouns per 100 words) per chapter; rewrite the top-decile sentences, not the whole corpus.
3. **Glossary EN column.** The bilingual table exists (build asserts `šķīdinātājs/solvent`, `izšķīdinātā viela/solute`); extend it to all 25 defined terms and put it next to the term index.

**Work packets.**

#### T14.1 — House style + measurement

1. Write `build/style-lv.md` (12 rules, each with a good/bad pair from the actual document).
2. Add `build/stylecheck.py`: sentence length histogram, nominalisation rate, banned filler list («Šeit var redzēt», «Ir svarīgi atzīmēt», «Kā zināms»), and a per-chapter table.
3. Set thresholds (median ≤18 words, ≤3 % sentences >40 words, filler ≤1 per chapter) and fail the build on regression *relative to the recorded baseline*, not absolutely.

#### T14.2 — Rewrite the top decile

1. Extract the 30 longest sentences with context; rewrite each to ≤25 words without losing a condition (numbers and qualifiers are load-bearing).
2. Remove filler openers and nominalisations in the 6 worst chapters; keep source-quoted wording untouched.
3. Re-run the measurement and record before/after in the change log.

#### T14.3 — Glossary and register consistency

1. Extend the EN column to all 25 terms; check the Latvian term in the glossary equals the `<dfn>` text (inverse test).
2. Add a one-line note on *why* the course's term is kept where it differs from standard usage (e.g. «masas procenti»).
3. Read 3 tasks aloud end-to-end; if a sentence cannot be read once without backtracking, rewrite it.

**Acceptance.**
- [ ] `style-lv.md` exists and every rule cites a real example from the document.
- [ ] Metrics improve against the recorded baseline; the baseline itself is committed.
- [ ] 25/25 glossary terms have EN equivalents and match `terms.py`.
- [ ] No source quotation was altered (diff the «Piezīme avotam» blocks before/after).

**Reject if.** The rewrite touches quoted source wording, task `dots`/`find` strings that mirror the seminar sheet, or numbers.

---

### T15 — SVG correctness repair: semantics, classes, collisions, sig-figs

**Axis:** SVG · **Wave:** 2 · **Depends on:** T02 · **Effort:** M · **Risk:** low-medium

**Evidence.** E09: `fig-leader` has no CSS rule → 4 invisible leader lines. E10: the quantity map labels the n–V edge `c` (while `c` is a node), labels c–γ `M`, and carries a hand-drawn curve from m to γ labelled `V` at the bottom of the canvas — three semantics in one diagram, one of them wrong. E11: `0,10` vs `0,1` in one figure. E12: type 10–14 user units. Reading the source also shows edges drawn **centre-to-centre** and then covered by node rectangles, so a line visually enters a box at an arbitrary point and can pass *through* an unrelated node (`ms → solvent` passes through `w`).

**Definition of done.** Every figure is semantically true (a label names exactly what the edge means), every class used is defined, no line passes through an unrelated node, no label collides with another, and every number agrees with `calc.py` and the sig-fig policy.

**Touch points.** `build/figures.py`, `build/figures/*.svg`, `build/head.html` (`.fig-*` rules), `build/build.py` (new figure gates).

**Three moves.**

1. **Repair the quantity map first — it is the document's argument.** Replace the free-form node/edge generator with an explicit spec: nodes on a fixed grid, edges as `(from, to, operator_symbol, direction)` where the operator is drawn as a small pill **on** the edge and nodes stay pure quantities. Delete the hand-drawn curve and the duplicate labels; if m→γ is needed, route it around the outside with one orthogonal path and label it `γ = m/V` in words, not a bare `V`.
2. **Make geometry honest.** Clip each edge at the node boundary (compute the intersection with the node rectangle), add 6 px of clearance, and assert in code that no edge segment intersects a non-endpoint node's rectangle.
3. **Add a CSS contract test.** Extract every `class="…"` used in `figures/*.svg`, diff against the selectors in `head.html`, and fail on any class with no rule (this immediately catches `fig-leader` and any future orphan).

**Work packets.**

#### T15.1 — Quantity map rewrite

1. Write the new spec table (8 nodes × grid coords, 7 edges × operator + direction) *in the module as data*, replacing the ad-hoc `EDGES` list and the stray `<path>`.
2. Render the operator pills (`M`, `V`, `ρ`, `w` and, for the secondary links, `c = n/V`, `γ = m/V` written out), and place them by mid-point of the *clipped* edge with a minimum 14 px clearance from node rectangles.
3. Verify against the four canonical conversions in `AGENTS.md` §6 (m↔n via M; n↔c via V; m↔m_šķ via w; m_šķ↔V via ρ) and against chapter 5's prose; correct whichever is wrong, and log it as a document-level fix (not a source defect).

#### T15.2 — Geometry + class guards

1. Add `clip_to_rect(a, b, rect)` to `figures.py` and use it for every edge; assert zero edge-through-node violations at generation time.
2. Add `figclass.audit()` in the build: used classes ⊆ defined selectors; also assert every `.fig-*` selector is used by ≥1 figure (dead CSS is a maintenance smell, not an error — warn).
3. Regenerate, then inspect all 9 at 2× and list every remaining collision manually (automation cannot see everything).

#### T15.3 — Label collision + numbers

1. Add a crude but effective collision check: for every pair of `<text>` elements, compare bounding boxes estimated from `font-size` × char count; fail on overlap > 2 px in x and y.
2. Route all numeric labels through `fmt_sig` (from T02.2) and re-diff.
3. Fix the three worst offenders found by the checks (expected: `ostwald` axis, `neutralisation` panels, `particle_scale` leaders).

**Acceptance.**
- [ ] 0 undefined SVG classes in the build.
- [ ] 0 edge-through-node intersections, asserted at generation.
- [ ] Quantity map passes the read-aloud test: a student can state each edge's meaning without the caption.
- [ ] 0 overlapping text boxes by the estimator; manual review confirms.
- [ ] All figure numbers match `calc.py` at the documented sig-figs.

**Reject if.** The map is "fixed" by removing labels until nothing is wrong. An unlabelled map is not correct, it is blank.

---

### T16 — SVG design system: type floor, palette, dark/print, guards

**Axis:** SVG · **Wave:** 3 · **Depends on:** T15 · **Effort:** L · **Risk:** medium

**Evidence.** E12: effective type 7.6–11 px. Figures mix `font-size` attributes (69 occurrences) with CSS classes — two ways to set type, no single control. Tone meaning changes per figure (documented honestly in `FIG_LEGEND`, which is the right instinct but leaves no *system*): in `dilution_ladder` depth = concentration category, in `ion_strip` tone = ion species, in `neutralisation` tone = reagent. Dark mode re-maps tokens, but figure-specific fills (`.fig-band.tone-4`, `.fig-amt-*`) were never checked against the dark ground. Print converts `--tone-*` to greys, so a 4-step tone ladder may collapse to indistinguishable greys.

**Definition of done.** One type scale in figure user units derived from the rendered size; one palette per figure *role* (species / magnitude / state), each verified in light, dark and print; a figure spec template that every new figure must fill; automated guards for type size, contrast and dark/print parity.

**Touch points.** `build/figures.py` (all generators), `build/head.html` (`.fig-*`, dark block, print block), new `build/figure-spec.md`, `build/qa.js`.

**Three moves.**

1. **Compute type from the display size.** Pick the display width per figure class (full-bleed plate ≈ 860 px, column plate ≈ 620 px), then set `font-size` in user units so the *rendered* size is ≥13 px for notes and ≥15 px for labels. Since the viewBox is displayed at ~660 px, that means ~18 and ~20 user units for a 900 viewBox. Enforce with a build calculation, not a convention.
2. **Separate the three encodings.** Define `--fig-species-1..3`, `--fig-magnitude-1..4`, `--fig-state-given/found/pass`, and forbid a figure from mixing two encodings without a legend. Each figure declares `encoding: species|magnitude|state|none` in its spec; the build checks the legend text mentions it.
3. **Verify all three modes.** A QA pass that renders each figure on light, dark and print backgrounds and measures (a) text contrast, (b) adjacent-tone ΔL ≥ 0.06 in OKLCH, (c) identical information in greyscale (print the figure in greyscale and ask "can the categories still be told apart?" — if not, add pattern/label redundancy).

**Work packets.**

#### T16.1 — Type floor

1. Add `fig_type(px_rendered, viewbox_width, display_width)` helper and replace all 69 `font-size` attributes with computed values.
2. Raise the axis/tick/note floors: notes ≥13 px rendered, labels ≥15, titles ≥17; re-check the 3 densest figures and delete labels rather than shrink below the floor.
3. Assert in the build that no `<text>` has a rendered size below the floor.

#### T16.2 — Encoding tokens

1. Define the token families in `head.html` + the dark and print remaps; document each family's meaning in `figure-spec.md`.
2. Convert the 9 figures to declare an encoding and use only that family; where a figure needs two (e.g. `ostwald`: magnitude + state), the legend must say so in one sentence.
3. Greyscale test: print each figure in pure greyscale at 100 % and record whether the categories are distinguishable; add direct labels where they are not.

#### T16.3 — Figure spec + guards

1. Write `figure-spec.md`: purpose (one sentence), data source (calc key), encoding, type sizes, viewBox, mobile strategy, alt text, legend sentence, owner. Every new figure must fill it before code.
2. Add `figurecheck.py`: type floor, undefined classes, missing `<title>/<desc>`, colour-only encoding (a figure whose legend says "tone distinguishes X" must also label X directly), and register consistency.
3. Wire into `build.py` and print `figures: 9 specs, 0 violations`.

**Acceptance.**
- [ ] No rendered text below 13 px; all 9 figures pass.
- [ ] Each figure declares one encoding family; legends match.
- [ ] Dark and print renders measured; adjacent tones ΔL ≥ 0.06 or direct labels.
- [ ] `figure-spec.md` filled for all 9 existing + 8 new figures.
- [ ] `figurecheck` runs in the build with 0 violations.

**Reject if.** The type floor is met by making the viewBox smaller while the display size stays the same (i.e. the figure simply gets denser).

---

### T17 — New figures (8) with a written spec and register update

**Axis:** SVG · **Wave:** 4 · **Depends on:** T16 · **Effort:** L · **Risk:** low

**Evidence.** 9 figures for 16 chapters and 67 tasks. Chapter gaps: no figure shows the *ion speciation of a weak electrolyte* (α, the Ostwald limit is a curve but not a particle picture); no figure shows *what a weak acid solution actually contains*; no figure shows *the three percent kinds on one object* (the single most common confusion, K23/P1); no figure shows *a dose ladder* (mg/kg → per dose → per day → per course, chapter 12); no figure shows *the anatomy of a lab result line* (chapter 5, P4); no figure shows *the mass balance in dilution* (m₁w₁ = m₂w₂) as distinct from mole balance; no figure shows *where the volume goes* when you add water (meniscus vs solvent volume, K13); there is no *decision tree* (T13) or *prerequisite graph* (T11) yet.

**Definition of done.** Eight new figures, each justified by a specific misconception, each with a filled spec, each passing T16's guards, each registered in the figure list and referenced from the text that needs it.

**Touch points.** `build/figures.py`, `build/figures/index.json`, `build/figures.py` `FIG_ORDER`, `build/ch*.html` insertion points, `build/ch15_16.html` figure register.

**Three moves.**

1. **Choose by misconception, not by aesthetics.** For each candidate, write the sentence a student gets wrong today and the figure that makes it impossible: "70 % etanols nozīmē 70 g etanola" → the three-percent figure; "šķīduma tilpums ir ūdens tilpums" → the volume-accounting figure; "α = 1 visiem" → the speciation figure.
2. **Draw the hard ones first.** Volume accounting and weak-electrolyte speciation carry the most conceptual load; dose ladder and result-line anatomy are the most practically useful. Do these four, review, then the next four.
3. **Wire them into the prose.** Each figure must be referenced from the paragraph it corrects (not only listed in the register), and each caption must state the misconception it prevents.

**Work packets.**

#### T17.1 — First four figures

1. **Three percent kinds** (`percent_kinds`): one beaker, three annotations — m/m (100 g solution), m/V (100 mL solution), V/V (100 mL solution, ethanol + water); the same 70 % label on three different objects with the actual amounts.
2. **Volume accounting** (`volume_accounting`): 300,0 mL water + 18 g glucose → solution volume ≠ 300,0 mL; meniscus above the solvent mark; a callout for K13 with the assumption stated.
3. **Weak electrolyte speciation** (`weak_speciation`): 0,1 mol/L NH₃, α ≈ 1,3 %, showing ~99 % NH₃·H₂O molecules vs NH₄⁺/OH⁻; scale-inset for the ions.
4. **Dose ladder** (`dose_ladder`): mg/kg → mg per dose → mg/day → mg per course, for one worked example from chapter 12, with the multiplication at each step.

#### T17.2 — Second four

1. **Mass balance in dilution** (`mass_balance`): m₁w₁ = m₂w₂ as two rectangles whose areas are equal, next to the mole-balance picture — the point is that they are *different* invariants.
2. **Result-line anatomy** (`result_line`): analyte · number · unit · reference interval, with the reference interval marked «laboratorijas veidlapā» (no invented ranges — `AGENTS.md` §3.3).
3. **Prerequisite graph** (from T11) and **decision tree** (from T13) — registered as figures 17–18 if drawn as SVG.
4. Register all 8: number, chapter, kind, encoding, mobile strategy, alt text; update `FIG_ORDER` and the register table; run the order gate.

#### T17.3 — Integration and review

1. Insert each figure next to its misconception; add one sentence of prose that *uses* the figure ("skatīt 12. attēlu: 70 % etanola ir 70 mL uz 100 mL šķīduma, nevis 70 g").
2. Check the figure register shows 17 entries in document order with correct chapters and kinds.
3. Review all new figures at 390 px (mobile strategy per spec) and in print greyscale.

**Acceptance.**
- [ ] 8 new figures, 8 filled specs, 0 guard violations.
- [ ] Every new figure is referenced from prose (grep the anchor) and from the register.
- [ ] Each caption names the misconception in one clause.
- [ ] No new figure invents a fact: every number traces to `calc.py`, the sources, or is labelled «ilustratīvs piemērs».
- [ ] Register order gate passes with 17 figures.

**Reject if.** A figure is added because it looks good in the register. If it does not prevent a named error, it is decoration.

---

### T18 — Solve-along workspace: stepwise hints + numeric answer check

**Axis:** FEAT · **Wave:** 4 · **Depends on:** T10, T12 · **Effort:** L · **Risk:** medium (scope creep)

**Evidence.** E24: the only interaction is chapter 15's recall mode (`recall_mode.js`, scoped to `#n15`). The 67 worked tasks are fully solved on arrival — a student cannot attempt them. The document's own pedagogy (route over a map, check by reverse substitution) is exactly the thing that should be *practised*, and there is no input anywhere. `AGENTS.md` §9 forbids gamification, XP/streaks/confetti, and persistent `localStorage` without consent.

**Definition of done.** Each worked task gains an optional "try it first" mode: the source data stays visible, the calc/answer/check are hidden behind a disclosure, and the student can type a number for the final answer and get a non-judgemental, unit-aware response (correct / off by a factor of 1000 / right value wrong precision / wrong). No scores, no streaks, no storage after reload.

**Touch points.** `build/taskbase.py` (renderer), `build/*.html` (task includes), new `build/solve.js`, `build/calc.py` (expected values), `build/head.html` (form styling).

**Three moves.**

1. **Separate "statement" from "solution" in the data.** The renderer already has the pieces (`dots`, `find`, `route`, `calc`, `answer`, `check`). Add a `solution` wrapper so the whole working can be collapsed while the statement stays open — and make the *interesting* step (`Maršruts`) the first optional hint rather than part of the statement.
2. **Check numbers, not strings.** Parse the student's input as a number + optional unit; compare to `calc.py`'s value with a relative tolerance (0.5 %), and separately compare significant figures to the documented expectation. Diagnose the four common failure classes: order of magnitude (×1000), inverted ratio, unit mismatch, precision.
3. **Keep it honest and private.** No server, no storage, no score. State in the UI in one line: «Šī pārbaude darbojas tikai šajā lapā un nekur neko nesaglabā.» Reset on reload. If the answer is not derivable from `calc.py`, do not offer input for that task.

**Work packets.**

#### T18.1 — Statement/solution split

1. Add `solution` grouping in `render()` (one `<div class="solution">` around `Maršruts`–`Kāpēc`) with `<details>` for screen and `open`-by-default in print.
2. Provide three hint levels: route only → route + given values → full working; each is a separate open, never auto-revealed.
3. Verify the print edition still prints everything (E25 behaviour must not regress): `printOpenedDetails` stays ≥151.

#### T18.2 — Numeric answer check

1. Build `answers.json` from `calc.V` at build time (task id → value, unit, sig-figs); fail the build if a task with an answer stub has no entry.
2. Implement `solve.js`: input parsing (`12,5` comma, `12.5` dot, optional unit), tolerance check, sig-fig check, four diagnostics, `aria-live="polite"` output, no `localStorage`.
3. Style the input as a single-line underline field (no box, no shadow), with a visible label; test keyboard-only use.

#### T18.3 — Coverage and restraint

1. Enable the mode only for tasks whose answer is a single number with a unit (expect ~50 of 67); list the excluded ones (multi-part answers) explicitly in the change log.
2. Add a short paragraph in chapter 15 explaining the mode and its limits («pārbauda skaitli, nevis risinājuma gaitu»).
3. Review against `AGENTS.md` §9: no XP, no streak, no confetti, no persistence, no timing pressure.

**Acceptance.**
- [ ] Statement visible, solution collapsed by default; print still complete.
- [ ] Typing `7,64` and `76,4` and `7.64` for P2 produce correct/order-of-magnitude/format feedback respectively.
- [ ] No `localStorage`/`sessionStorage`/cookie writes (`grep`).
- [ ] Works with keyboard only; `aria-live` announces the verdict.
- [ ] No score, no count of "correct answers" displayed.

**Reject if.** The feature becomes a quiz with points. The document is a study aid, not an assessment platform.

---

### T19 — Conversion & unit lab (offline, dimension-checked)

**Axis:** FEAT · **Wave:** 4 · **Depends on:** T02 · **Effort:** M · **Risk:** low

**Evidence.** E24: the student's four conversions (w↔c, c↔γ, m↔n, m_šķ↔V) are taught 67 times but can only be practised by hand. Chapter 9 shows the closed formulas `c = 10wρ/M` and `w = cM/(10ρ)` — exactly the kind of two-step expression where a factor of 10 or 1000 goes missing. `calc.py` already has the truth for every task; a small unit-aware helper would let a student check their own arithmetic on *their* numbers, not just the document's.

**Definition of done.** A single small panel (in chapter 9 and linked from the formula sheet) that takes w, ρ, M, c, γ, m, V — any two or three — and returns the consistent set, showing the formula used and the unit cancellation. No network, no `eval`, no chart, no saved state.

**Touch points.** new `build/lab.js`, `build/ch05_08.html` (chapter 9), `build/ch15_16.html` (§16.a), `build/head.html` (form styles), `build/calc.py` (shared constants).

**Three moves.**

1. **Model the quantities, not the fields.** Define the seven quantities with units and the four relations; solve for the unknown symbolically (closed-form, 7 cases), so the panel cannot produce a number without a stated formula. Show the formula string next to the result.
2. **Make units part of the answer.** Every output carries a unit; a mismatch (w in % vs fraction, ρ in g/mL vs g/L) is reported as a *specific* correction, not a generic error. Add the `1 g/L = 1 mg/mL`, `1 mL = 1 cm³` reminders inline.
3. **Refuse to guess.** If the inputs are underdetermined (e.g. only w given), say what is missing (`vajag ρ, lai iegūtu c`) instead of defaulting to ρ = 1. If ρ = 1 is used, it must be an explicit checkbox with the assumption spelled out.

**Work packets.**

#### T19.1 — Solver core

1. Implement the 7 solve cases in pure JS with no `eval`; each returns `{value, unit, formula, assumptions[]}`.
2. Add dimensional checks (unit string algebra for the 7 units) so `c` cannot be returned in g/L.
3. Unit-test 12 cases in Node against `calc.py` values (P1, P2, P6, C13, C14, C15, C3.1, C9, C10, BSC9, BSC10, P4) with 1e-6 agreement.

#### T19.2 — Interface

1. Build the form: 7 labelled inputs, unit selectors only where ambiguity exists (w as % or fraction; ρ as g/mL or g/L), a single "Aprēķināt" button, results in a definition list.
2. Show the formula and the unit cancellation line, plus one sentence «kāpēc šis lielums nav zināms» when underdetermined.
3. Add the ρ = 1 assumption as an explicit checkbox with the sentence «Pieņemts ρ = 1,00 g/mL; tas ir tuvinājums.»

#### T19.3 — Placement and restraint

1. Place it in chapter 9 after the closed formulas, and link it from §16.a; do not put it in a sticky bar or a floating widget.
2. Add a 3-line usage note: what it does, what it does not do (no significant-figure rounding of your data), and that nothing is saved.
3. Test with 6 real seminar numbers; a student should reproduce the document's own answers.

**Acceptance.**
- [ ] 12 unit tests pass against `calc.py`.
- [ ] Every result states its formula and unit.
- [ ] Underdetermined input produces a specific missing-quantity message, never a default.
- [ ] No `eval`, no network, no storage; `grep` clean.
- [ ] Keyboard operable; labels associated; errors announced.

**Reject if.** The panel silently assumes ρ = 1 or additive volumes. Both are assumptions the document spends chapters qualifying.

---

### T20 — Exam pack export: 2-page formula card, triage sheet, offline search

**Axis:** FEAT · **Wave:** 5 · **Depends on:** T09, T13 · **Effort:** M · **Risk:** low

**Evidence.** E22: 109 print pages for two tests at ≥55 %. §16.a is a formula sheet but it lives inside the 109-page document. There is no way to find a specific task quickly (E24: no search), and the TOC is chapter-level only, while there are 67 tasks and 32 tables. A student revising needs (a) two pages they can print and carry, (b) a way to jump to "the Na₃PO₄ one", (c) an index of the mistakes they personally make.

**Definition of done.** A generated 2-page A4 "exam pack" (formula card + decision tree + the 12 traps) that reuses the document's own data, a one-page "triage sheet" mapping test-question phrasing to the route to take, and an offline, in-memory search over tasks/tables/terms with a keyboard shortcut.

**Touch points.** `build/build.py` (second output target), `build/ch15_16.html` (§16.a source), `build/tasks_a.py`/`tasks_b.py` (traps), `build/terms.py`, new `build/pack.html` template, `build/search.js`.

**Three moves.**

1. **Generate the pack from the same data, not by hand.** A `--pack` build target that renders a 2-page document from `lexicon.py`, the formula sheet source, the decision tree (T13) and the 12 trap sentences (T10). Any change to a formula or trap updates the pack automatically; a hand-copied card would drift within a week.
2. **Make the pack *test-shaped*.** Page 1: symbols, units, the four conversions, the three percent kinds. Page 2: the decision tree + the 12 traps in the student's own words + a 5-line calculator protocol. Max 2 pages, A4, 9.5 pt floor, no decoration.
3. **Offline search over structure, not full text.** Index task ids/titles, table captions, term names and section headings; `Ctrl/⌘+K` opens a plain list; results jump to the anchor. No fuzzy library, no network, no index file — built into the HTML at assembly time.

**Work packets.**

#### T20.1 — Pack generator

1. Add a `--pack` mode writing `build/out/exam_pack.html` with a strict 2-page print CSS (`@page` A4, 12 mm margins, 9.5 pt floor).
2. Pull content from the single sources: `lexicon.py`, §16.a, the decision tree, the trap list; assert every symbol on the card exists in `lexicon.py`.
3. Print to PDF, verify exactly 2 pages, check that all 7 quantities and 4 conversions are present and that no formula is clipped.

#### T20.2 — Triage sheet

1. Enumerate the phrasing patterns found in the sources ("Cik gramu …", "Kāda ir … koncentrācija", "Cik mL … jāpievieno", "Cik molu …") and map each to a route.
2. Write 12 rows: «Ja jautājums skan … → vispirms atrodi … → tad …». One line each, no prose.
3. Cross-check against the 67 tasks: every task's wording must match at least one row, else add a row (cap at 14).

#### T20.3 — Offline search

1. Emit a JSON index at build time (`{title, anchor, kind}` for 67 tasks + 32 tables + 25 terms + 16 sections), embedded in the page.
2. Implement `search.js`: `Ctrl/⌘+K`, filter as you type over title/kind, arrow keys + Enter, `Escape` closes, focus returns; results capped at 20 with a count.
3. Add `aria` roles (`combobox`/`listbox`/`option`) and test with a screen reader if available; at minimum verify keyboard-only operation and that the dialog traps no focus.

**Acceptance.**
- [ ] `exam_pack.pdf` is exactly 2 pages, 0 clipped formulas, all 4 conversions + 7 quantities.
- [ ] Triage sheet: ≤14 rows, covers all 67 tasks' phrasing.
- [ ] Search: 140 entries indexed, keyboard-only, `Esc` restores focus, no network requests.
- [ ] Pack and search both regenerate from the main build (no second source of truth).

**Reject if.** The pack is produced by copying text into a new file. It will be wrong by the next revision, and nobody will notice.

---

## 6. Feature backlog (each ships inside a task)

| ID | Feature | Ships in | Notes / guardrail |
|---|---|---|---|
| F01 | Margin-note rail for provenance and defects | T05 | No duplication of note text; inline fallback is the default |
| F02 | Prerequisite strips + full concept graph | T11 | Teaching graph ≠ task route graph |
| F03 | One-sentence chapter takeaways | T13 | Must contain an action, not a topic name |
| F04 | Decision tree «Ko prasa uzdevums?» | T13 | 6–8 leaves; must be tested with 5 tasks |
| F05 | Precision contract + 10-second self-check | T02 | Three rules only |
| F06 | Concept-coverage table in the appendix | T04 | 66 rows, uncovered shown, not hidden |
| F07 | Source↔task two-way links (K-rows) | T10 | No broken anchors |
| F08 | Route mini with given/found state | T12 | Text mirror mandatory |
| F09 | Solve-along hints (3 levels) + numeric check | T18 | No scoring, no storage |
| F10 | Conversion & unit lab | T19 | Explicit ρ = 1 checkbox; refuses to guess |
| F11 | Offline `Ctrl/⌘+K` search | T20 | Structure index only; 140 entries |
| F12 | 2-page exam pack (formula + tree + traps) | T20 | Generated, never hand-copied |
| F13 | Triage sheet (phrasing → route) | T20 | ≤14 rows |
| F14 | Build-ID stamped QA evidence | T04 | A stale screenshot cannot masquerade as current |

**Explicitly not features:** myoglobin-style gamification, XP, streaks, emoji medals, confetti, a "mastery %" score, an account, a cloud sync, an AI chat panel inside the document, a dark-mode toggle that overrides `prefers-color-scheme` (a light/dark toggle is acceptable only if it is a plain two-state control and remembers nothing).

---

## 7. Execution waves

| Wave | Tasks | Exit criterion |
|---|---|---|
| **1 — Truth** | T01–T04 | Build passes with the new lexicon, glyph and digit gates; PDF has no Type 3 and has an outline; QA report has no meaningless metric and carries a build ID. |
| **2 — Design foundation** | T05, T06, T07, T08, T15 | Rails, surfaces and type are in place; figures are semantically correct and every class is defined. Do not start T10 before this lands, or the explanation rewrite will be styled twice. |
| **3 — Teaching** | T09, T10, T11, T12, T16 | 67 tasks have three-part explanations and traps; coverage 66/66; routes legible; figure system enforced. |
| **4 — Depth & features** | T13, T14, T17, T18, T19 | Synthesis artefacts exist; language pass measured; 8 new figures; solve-along and lab shipped without storage. |
| **5 — Output** | T20 | Exam pack (2 pages) + triage sheet + search, generated from the build. |

Parallelisable without conflict: T03 ∥ T04 ∥ T01; T15 ∥ T06; T13 ∥ T17. Not parallelisable: T05 and T09 (same layout), T10 and T14 (same prose).

---

## 8. Global acceptance gate (copy-paste)

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_3
F=Master_3_tema_skidumi_un_koncentracijas.html

# 1 build + all internal gates (equations, roles, units, figures, terms, ids)
python3 build/build.py

# 2 self-contained
grep -nE '(src|href)="https?://|@import|url\(https?://|<link[^>]+stylesheet' "$F"   # empty

# 3 language / title
grep -c '<html lang="lv"' "$F"                        # 1
grep -o '<title>[^<]*</title>' "$F"

# 4 no unit-spelling leaks in prose
grep -nE '\b[0-9,]+ ?(ml|l|ppm)\b' "$F" | head -20    # only K-rows / change log

# 5 no decimal-point numbers in prose
grep -nE '[0-9]\.[0-9]+ ?(mL|L|g|mg|mol|nm)\b' "$F" | head -40

# 6 corrected source defects never leak outside quotes
grep -nE 'n skābes ?= ?2 ?n sārma|NH4OH|NH₄OH|0,0994|13,4 ?g|\(HCOOH\)' "$F"

# 7 figure classes all defined (T15)
python3 - <<'PY'
import re,glob
used=set()
for f in glob.glob('build/figures/*.svg'):
    used|={c for s in re.findall(r'class="([^"]+)"',open(f,encoding='utf-8').read()) for c in s.split()}
css=open('build/head.html',encoding='utf-8').read()
defined={m for m in re.findall(r'\.([A-Za-z][\w-]*)',css)}
print('undefined in figures:',sorted(c for c in used if c not in defined))
PY

# 8 print artefacts (T03)
pdffonts build/qa/master-print.pdf | grep -Ei 'type 3|nimbus'   # empty
pdfinfo build/qa/master-print.pdf | grep -E 'Pages|Tagged'

# 9 anti-slop
node workspace_skills/design-taste-frontend/scripts/lint.mjs "$F"
node workspace_skills/design-taste-frontend/scripts/inspect.mjs "$F" --widths 1440,768,390

# 10 no persistence, no scoring, no network in shipped scripts
grep -nE 'localStorage|sessionStorage|XMLHttpRequest|fetch\(' "$F"        # empty
grep -niE 'xp|streak|confetti|mastery|score' "$F" | head               # review hits
```

Manual gate (cannot be automated, must be recorded in §16.e with a date):

- Open at 1440, 768, 390 in light and dark; read chapter 5 and task C14 end-to-end.
- Print preview: first page, a table page, a formula page, the last page.
- Keyboard-only pass: skip link → TOC → first task → its answer disclosure → search (after T20).
- Read 5 task explanations aloud; if any sentence needs a second pass, it fails T10.

---

## 9. Non-goals and risks

**Non-goals.** Rewriting from scratch; changing the source files or `workspace_skills/`; adding a build tool beyond Python + the existing Node scripts; adding frameworks; adding a server; adding accounts or telemetry; replacing the current palette wholesale; turning the document into a web app.

**Top risks.**

| Risk | Mitigation |
|---|---|
| Layout rewrite (T05) breaks the print edition | Print CSS is owned by the same task; page-count and clip checks in §8 |
| Explanation rewrite (T10) turns into 67 identical paragraphs | `why_parts` + opener-distribution assertion |
| Figure rewrite (T15/T16) changes numbers | All numbers route through `calc.py` + the digit gate (T02.3) |
| Feature work (T18/T19) drifts into a quiz app | §6 guardrails + explicit acceptance on "no storage, no score" |
| The K-register gets "cleaned up" by a well-meaning agent | K-rows may only change with a lecturer's answer (§10); quote contexts are build-protected |
| Screenshots/diff claims without a browser run | `QA_STATUS` must state what was not checked (E23 pattern) |

---

## 10. Open questions for the lecturer (do not resolve by guessing)

1. **K16** — is the formalin task (`HCOOH` in D/E P5) to be answered with 46,03 (formic acid) or 30,03 (formaldehyde)? The document currently shows both and flags it.
2. **K23** — are the percentage kinds in A to be read as m/m, m/V or V/V for each of 70 % ethanol, 3 % H₂O₂, 5 % iodine? The document states the conventions and marks them `V`.
3. **K10** — 0,88 % or 0,9 % NaCl for physiological saline; both appear in the course materials.
4. **K14** — are the illustrative densities (1,07 for 5 %/9 % Na₃PO₄) to be used as given, or replaced by measured values?
5. **K2/K3** — the unclassified bands (0,01–0,1 g solubility; 100–1000 nm particle size) and the α gap (0,1–0,7): examinable, or "know that the source is incomplete"?
6. **C_M vs c** — may the document standardise on `c` while teaching `C_M`, or must the tasks keep `C_M` verbatim?

Answers belong in §16.d of the document, dated, with the person asked.

---

## 11. Change log for this plan

| Date | Change |
|---|---|
| 2026-10-31 | v1 plan written (`TASKS_20_Master_3_tema_Improvement_Plan.md`), 127 KB. |
| 2026-11-01 | v2 written after re-inspection of the current build: v1's top defects (P2 `1020`, figure order, duplicate anchors, terminology regressions, heading families, skip link) verified **fixed** and removed from scope. New evidence added: duplicate recall answers (E03), incomplete font subset + Type 3 PDF (E06/E07), false contrast metric (E08), undefined `fig-leader` (E09), quantity-map semantics (E10), figure min-width at 390 (E04), figure type size (E12), teaching-depth distribution (E13), coverage gaps (E14), dead right margin (E15). Tasks restructured into 3 moves + 2–3 work packets × 3 substeps. |

**Plan built from measurements, not memory.** If a number in §2 disagrees with the workspace, the workspace wins; update the ledger first, then the task.

---

## Appendix A — Feature specifications (screen-level detail)

The tasks say *what* to build. This appendix says exactly what the student sees, what happens on each interaction, and what happens at the edges. It exists so that two different agents implement the same feature the same way, and so a reviewer can reject a build without arguing about taste.

### A.1 F09 — Solve-along workspace (T18)

**Placement.** Inside every `<article class="task">`, directly under the `h3`. The statement (`Dots`, `Meklējams`) stays open. Everything from `Maršruts` to `Kāpēc šādi` moves into `<div class="solution">`.

**Visual states.**

| State | What is visible | What is hidden |
|---|---|---|
| Default | `Dots`, `Meklējams`, one line: «Vispirms pamēģini pats; risinājums atveras zemāk.» | route, assumption, calc, answer, check, why, note, wrong |
| Hint 1 | + `Maršruts` (one line, no numbers) | everything else |
| Hint 2 | + `Pieņēmums` and the given values repeated as a bullet list | calc, answer, check |
| Full | everything, same order as today | — |

**Controls.** Three text buttons in one row: «Maršruts», «Doti lielumi», «Viss risinājums». Each is a toggle; opening a later level opens the earlier ones. `aria-expanded` on each. No icons.

**Answer input.** One underlined field labelled «Atbilde» + a unit shown as static text after the field (`mol/L`), because the unit is part of the question. Placeholder: none (a placeholder is a label that disappears). Helper line under the field: «Skaitli raksti ar komatu: 0,74.»

**Verdicts (in `aria-live="polite"`).**

| Student input | Verdict text |
|---|---|
| within 0.5 % and sig-figs match | «Pareizi. 0,74 mol/L.» |
| within 0.5 %, one digit too many | «Skaitlis pareizs, bet dotie lielumi dod 2 zīmīgos ciparus: 0,74.» |
| factor 10 / 100 / 1000 off | «Skaitlis atšķiras 100 reizes. Pārbaudi, vai dalīji ar litriem, nevis mililitriem.» |
| reciprocal | «Šķiet, ka dalīšana un reizināšana ir samainītas vietām.» |
| unit mismatch (typed `740 mmol/L`) | «740 mmol/L = 0,740 mol/L — tas ir pareizi; mērvienību pārrēķins ir daļa no atbildes.» |
| unparseable | «Nesapratu skaitli. Raksti tikai skaitli, piemēram, 0,74.» |

**Edges.** Empty input → no message, button disabled. Multi-part answers → no input offered; instead the disclosure only. A task whose answer is a range → input disabled, text «Šim uzdevumam atbilde ir intervāls; pārbaudi abus galus.»

**Privacy line.** One sentence, once per chapter: «Pārbaude darbojas tikai šajā lapā; nekas netiek saglabāts.» No `localStorage`, no `sessionStorage`, no cookies, no `fetch`.

**Print.** All levels print open; the input field prints as an empty underline with «Atbilde: ______» so the printed page is still usable as a worksheet.

### A.2 F10 — Conversion & unit lab (T19)

**Placement.** Chapter 9, after the two closed formulas, before the first worked task of that section. One panel, not a sticky widget.

**Inputs.** Six fields in a 2×3 grid: `w` (with a `%` / fraction toggle), `ρ` (with `g/mL` / `g/L` toggle), `M` (`g/mol`), `c` (`mol/L`), `γ` (`g/L`), `m` (`g`). One checkbox: «Pieņemts ρ = 1,00 g/mL (tuvinājums)», unchecked by default.

**Result block.** A `<dl>` of the quantities it could determine, each with the value and the unit, followed by:

- **Formula used**, typeset as text: `c = 10 · w% · ρ / M`.
- **Unit line**: `% · g/mL ÷ g/mol = mol/L` (the cancellation spelled out).
- **Assumption line**, only if used: «ρ = 1,00 g/mL pieņemts; bez tā c nevar aprēķināt.»
- **Missing line**, when underdetermined: «Lai aprēķinātu c, vajag w, ρ un M. Trūkst: ρ.»

**Behaviour.** Recompute on input (debounced 150 ms) — no submit button, because a submit button implies a server. Never round the student's own data; print as typed. If a value is impossible (`ρ = 0`, `M = 0`, negative), refuse with a specific sentence, not a red border.

**Keyboard.** Tab order follows the visual grid; `Enter` moves to the next field; no focus traps; the result block is `aria-live="polite"` but only announces the changed quantity, not the whole list.

### A.3 F11 — Offline search (T20)

**Trigger.** `Ctrl+K` / `⌘K`; also a plain text link «Meklēt» in the TOC (no icon, no floating button).

**Panel.** A native `<dialog>` centred, max-width 560 px, no backdrop blur, no rounded card. One input, one list.

**Index.** 140 entries: 67 tasks (`P2 · Na₃PO₄ masas daļa no molārās koncentrācijas`), 32 tables (`9. tabula · Koncentrāciju veidi…`), 25 terms (`γ · masas koncentrācija`), 16 sections. Entry shape: `{label, kind, anchor, keywords}`.

**Matching.** Case- and diacritic-insensitive substring over `label + keywords`; rank exact-prefix > word-start > substring; cap 20 results; show «Rāda 20 no 34» when capped. No fuzzy library.

**Keys.** `↑`/`↓` move, `Enter` opens (closes panel, jumps, moves focus to the target heading), `Escape` closes and returns focus to the trigger. Screen reader: `role="combobox"` on input, `aria-activedescendant`, `role="listbox"` on the list.

**Empty and no-result states.** Before typing: «Raksti uzdevuma numuru, tabulas numuru vai terminu.» No results: «Nekas neatrasts. Pamēģini “Na₃PO₄” vai “C14”.» — no illustration, no mascot.

### A.4 F12 — 2-page exam pack (T20)

**Page 1 — «Kas jāzina no galvas».**
Symbols row (7 quantities, symbol + unit), the four conversions with one-line conditions, the three percent kinds with one example each, the mol/L ↔ M note, and the sig-fig rules (3 lines). Type 9.5 pt floor, 12 mm margins, no colour except one accent rule.

**Page 2 — «Kā sākt uzdevumu».**
The decision tree (6–8 leaves), the 12 traps in one line each, and the 5-line calculator protocol (enter numbers with full precision → one division → round at the end → check magnitude → write the unit).

**Rules.** Exactly 2 pages; if content overflows, cut a trap, never shrink below 9.5 pt; generated from `lexicon.py`, §16.a, the tree and the trap list; footer carries the build ID and date so a stale printout is identifiable.

### A.5 F01 — Margin note (T05)

**Anatomy.** `<aside class="note"><p class="note-label">Piezīme avotam</p><p>…</p></aside>`, placed as a sibling *after* the paragraph it annotates.

**Rail geometry (≥1180 px).** Column 3, width 200–260 px, top offset −0.35 em so the first line sits on the reference line's baseline. 2 px left rule in `--line`; label `.78rem` 600 `--ink-muted`; body `.82rem/1.45`.

**Inline geometry (<1180 px).** Same node, `grid-column: 1 / -1`, left rule 3 px, 12 px padding-left, body `.9rem`.

**Never.** Never a tooltip, never a popover, never a hover-only reveal (touch and print lose it), never a footnote digit without a target, never duplicated text.

### A.6 F06 — Concept coverage table (T04)

**Shape.** 66 rows, 3 columns: `Koncepts` · `Nodaļa` · `Kur pārbaudīts`. The third cell is either a link to the recall item (`#recall-14`) or the text «nav pārklāts — sk. T11» in `--ink-muted`.

**Ordering.** By concept group (S → D → A → Q → P → C → L → R → M), not alphabetically, because the group order is the teaching order.

**Print.** Repeats the header on each page; 66 rows fit in ~1.5 pages at 9 pt; no zebra striping (a 66-row zebra is a tell and hurts print).

---

## Appendix B — Before/after, one line per task

Use this as the demo script for a reviewer. If the "after" column cannot be photographed, the task is not done.

| Task | Before (today) | After |
|---|---|---|
| T01 | `c`, `C_M`, `M` and `m_šķ` coexist; the mapping is scattered | One symbol table, one course-mapping table, build-fails on any variant |
| T02 | `0,10` and `0,1` in one figure; the precision rule is implied | One precision contract; every figure number emitted from `calc.py`; digit gate green |
| T03 | 11 glyphs fall back to a system font; PDF has Type 3 and no outline | One face for everything; `pdffonts` clean; PDF outline with 16 entries |
| T04 | `report.json` claims 1.445 : 1 contrast on a transparent block | Ratios carry their resolved background; screenshots carry the build ID |
| T05 | 390 px of empty margin; source notes break the reading line | A 200–260 px note rail; notes collapse inline below 1180 px |
| T06 | 151 identical bordered disclosure cards; two uppercase micro-labels | Space and weight do the work; no tracking; no filled cards |
| T07 | Tone ladder exists in data figures only | A documented surface law; masthead without a full-bleed band |
| T08 | Heading sizes hand-tuned; no Latvian hyphenation | Five scale tokens; `hyphens:auto` with limits; ≤3 sentences per paragraph |
| T09 | Every figure pans on a phone; print has no spine | Figures fit or offer a labelled zoom; print has an outline and running heads |
| T10 | 8 tasks explain in ≤20 words; 56 have no trap | 67/67 have route + trap + boundary; assumptions declared |
| T11 | 58/66 concepts covered; no prerequisites | 66/66 covered; prerequisite strips at every chapter head |
| T12 | A 112×70 squiggle that vanishes on mobile | A legible route with given/found state and a text mirror |
| T13 | 109 pages, no takeaway, no decision aid | One sentence per chapter; a decision tree; a 3×6 matrix |
| T14 | Institutional nominalisations; no house style | 12-rule style sheet; measured sentence length; EN glossary |
| T15 | One undefined class; a mislabelled flagship diagram | Every class defined; every edge labelled with what it means |
| T16 | 7.6–11 px figure text; tone means a different thing per figure | 13 px floor; three named encodings; greyscale-safe |
| T17 | 9 figures, gaps at the exact misconceptions | 17 figures, each tied to a named wrong answer |
| T18 | 67 fully solved tasks, no practice | Statement first, three hint levels, numeric check, no storage |
| T19 | Conversions only by hand | A 6-field lab that shows the formula and refuses to guess |
| T20 | 109 pages to revise from | 2-page pack + triage sheet + `Ctrl/⌘+K` search |

---

## Appendix C — Figure specification template (copy for every new figure)

Fill this **before** writing generator code. An empty field is a reason not to draw the figure.

| Field | Answer |
|---|---|
| `id` | snake_case, stable, used in the anchor `fig-<id>` |
| Purpose (one sentence) | What misconception does it make impossible? |
| Data source | `calc.V['…']`, `MASS`, `MED`, `OST`, or «shēma (no data)» |
| Encoding | `species` / `magnitude` / `state` / `none` — one only |
| Legend sentence | Exactly what the reader must know to decode it |
| Type sizes | title / label / note, in user units **and** rendered px at the declared display width |
| ViewBox | `0 0 W H` and the display width(s) it is designed for |
| Mobile strategy | `fit` / `zoom` / `variant` (see T09.1) |
| Greyscale check | Are categories distinguishable without colour? If not, what label redundancy was added? |
| Alt text (`<desc>`) | 1–2 sentences, includes the numbers that matter, no «attēls ar…» |
| Register | number, chapter, kind (`attēls veidots no datiem` / `shēma`) |
| Print note | Any part that must not be relied on in greyscale? |
| Owner + date | Who last verified it against `calc.py` |

---

## Appendix D — Definition of "done" for the whole programme

The revision is finished when all of the following are simultaneously true and recorded in §16.e with a date:

1. `python3 build/build.py` passes with the five new gates (lexicon, glyphs, digits, figure classes, figure specs) and prints 0 violations.
2. The built file is self-contained, `lang="lv"`, and has 0 external requests.
3. The print PDF is 105–115 pages, has no Type 3 fonts, and has ≥16 outline entries (or a dated note explaining why not).
4. 67/67 tasks have a three-part explanation, a trap statement and, where relevant, an assumption.
5. 66/66 concepts are covered, ≥40 by two or more items.
6. 17 figures, all with a filled spec, all passing the type floor and the collision check, all referenced from prose.
7. 0 duplicate facts: each recall question appears once; each formula appears once as the source and elsewhere only as a reference.
8. The four manual checks in §8 are recorded, with screenshots at 1440/768/390, light and dark, and print previews.
9. `lint.mjs` reports 0 FAIL; the em-dash count does not exceed 60.
10. Nothing in §9's non-goals has appeared.

If any of these cannot be met, say which and why in §16.e — an honest gap is worth more than a green build that measures the wrong thing.

