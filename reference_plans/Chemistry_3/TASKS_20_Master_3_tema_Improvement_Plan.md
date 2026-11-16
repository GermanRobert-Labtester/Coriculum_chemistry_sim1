# 20-task improvement plan — `Master_3_tema_skidumi_un_koncentracijas.html`

**Workspace:** `/home/robertsrff/Chemistry_Med/Chemistry_3`
**Document under review:** `Master_3_tema_skidumi_un_koncentracijas.html`
**Inspection date:** 2026-10-31
**Plan type:** terminology correction, arithmetic/QA repair, anti-slop redesign, restyling, explanation depth, and feature backlog
**Status:** investigation complete; no source or build file has been edited by this plan.

---

## Contents

- **0.** Executive summary
- **1.** Evidence ledger (verified, line-referenced)
- **2.** Task template
- **3.** The 20 tasks: T01–T20
- **4.** Design and restyle tasks: T11–T15
- **5.** Explanation and learnability tasks: T16–T20
- **6.** Suggested feature backlog: F01–F18
- **7.** Execution sequence
- **8.** Global acceptance gate
- **9.** Open questions for the lecturer
- **10.** Change log for this plan
- **Appendix A.** File map for the implementing agent
- **Appendix B.** Exact bad strings to retire
- **Appendix C.** One-page implementation checklist

---

## 0. Executive summary

### 0.1 What the document already is

This is not a rough draft. It is a substantial, generated, single-file Latvian study document:

| Property | Measured value |
|---|---:|
| File size | 490.7 KB (after `build/build.py`) |
| Chapters | 16 (`n1`–`n16`), plus 17 `<h2>` including “Saturs” |
| Worked task blocks | 67 `<article class="task">` |
| Recall prompts | 75 rendered recall items; 142 `<details>` total |
| Tables | 25, all with `<caption>` and scoped headers |
| Figures | 9 inline-SVG figures, all with `<title>`/`<desc>` |
| Print edition | 106 A4 pages; `build/qa/master-print.pdf` |
| External requests | 0 (fonts embedded as WOFF2 base64) |
| `design-taste-frontend` lint | 0 FAIL, 1 WARN (88 em dashes) |
| Build checks | `python3 build/build.py` passes; 67 tasks; 75 recall items |

The document already does many difficult things correctly: it separates source claims from additions, recalculates numbers, marks source defects, includes a change log, uses native `<details>` for retrieval, and provides a print stylesheet. The plan below is therefore **not** a rewrite from zero. It is a precision-and-craft pass that removes the remaining contradictions, makes the design contract internally consistent, and turns the material into a more teachable object.

### 0.2 The ten most consequential findings

1. **P2 contains a false intermediate equality.**  
   `build/tasks_a.py:383` prints `m(šķīdums) = 1020 g` for `ρ = 1,03 g/mL`; `1000 · 1,03 = 1030 g`. The printed answer `7,640 %` is only correct with 1030 g. With 1020 g it would be `7,716 %`. The check line at `:385` repeats the false `78,69/1020 = 0,0764`. The source key E itself uses `1030` and `78,72`. This is the clearest correctness defect in the current document.
2. **Figures are numbered in authoring order, not document order.**  
   In document order the captions run `2, 4, 3, 9, 1, 5, 6, 7, 8`. “1. attēls” appears after “9. attēls”. A reader who follows figure references is misled. The numbering lives in `build/figures.py` (`:90`, `:129`, `:160`, `:218`, `:386`).
3. **Four anchors are duplicated.**  
   `C1.1` → `t-c11` collides with `C11`; `C1.2` → `t-c12` with `C12`; `C2.1` → `t-c21` with `C21`; `C2.2` → `t-c22` with `C22`. Cause: `build/taskbase.py:20` deletes dots before building the anchor.
4. **The quantity map contradicts itself.**  
   `build/ch05_08.html:3` says “septiņi lielumi”, line 7 says “astoņi mezgli, bet tikai septiņi neatkarīgi lielumi”, and the map itself has eight nodes: `m(viela)`, `n`, `V`, `m(šķīdums)`, `m(šķīdinātājs)`, `c`, `γ`, `w`. The phrase “neatkarīgi” is also wrong because the three masses are linked by mass balance.
5. **The terminology table has a garbled recommendation and a conceptual error.**  
   `build/ch13_14.html:125` prints “**izšķīdinātā viela**; **šķīdinātājs** — šķīdinātājs”. Line 126 says “γ, c un **w(V)** attiecas uz šķīduma tilpumu”. `w` is a mass fraction; it does not refer to volume. This is exactly the kind of denominator error the document warns against.
6. **A double negative survives in the terminology chapter.**  
   `build/ch13_14.html:207`: “Šī analīze avotā nav dota un ir **nav pārbaudīta**”. It should be “un nav pārbaudīta”.
7. **The callout taxonomy has drifted.**  
   There are 68 “Pārbaudīts”, 25 “Biežākā kļūda”, 14 “Pārbaudi sevi” inside `role-verified`, plus “Papildinājums”, “Saprāta pārbaude”, “Kā skaitīt”, “Drošība” and “Dokumenta robeža”. The contract says three semantic roles only. “Pārbaudi sevi” is not a verified result; it is retrieval practice. One block also prints “Papildinājums papildinājums” (`build/ch05_08.html` equivalent in chapter 11).
8. **The heading family changes mid-hierarchy.**  
   `h1` and `h2` use Noto Serif; `h3` and `h4` use Noto Sans (`build/head.html:108–110`). This makes the hierarchy look accidental and violates the prompt’s “headings in the same family” clause. The serif/sans split is also one of the familiar editorial shortcuts the anti-slop contract is trying to avoid.
9. **The first keyboard target does not skip anything.**  
   The skip link is placed inside `<main id="saturs">`, after the masthead and the table of contents. It points to its own parent, so it cannot skip the navigation that precedes it.
10. **The “generated” workflow is not protected by an equation-level audit.**  
    `build/build.py` checks that selected final strings exist, but it does not parse the displayed `Aprēķins` and `Pārbaude` lines. That is why the P2 `1020` error survives a passing build. The document needs an equality auditor, not only a value-presence check.

### 0.3 Secondary findings worth fixing in the same pass

- `O1`–`O5` are inside an `<ol>`, so the rendered list reads “1. O1.”, “2. O2.” (`build/ch01_04.html:6–12`). Double numbering.
- `P12` says the 3,000 g powder contains 100 mg acetylcysteine, 2.8 g sucrose and 100 mg ascorbic acid, but computes only two mass fractions. The missing 3.33 % is ascorbic acid, and the table never says so.
- Rehydron uses `C6H5Na3O7` (anhydrous citrate, M = 258.07). If a reader substitutes the common dihydrate (M = 294.10), the Na⁺ total changes. The document should state the assumption explicitly.
- The mobile tables (especially 9 and 10) are wider than 390 px and rely on horizontal scroll without an affordance; the screenshot cuts the right-hand columns.
- Inline provenance labels such as `papildinājums` are underlined like links and sit directly before a sentence, which reads as a typo rather than a label.
- The masthead’s right-hand “Saīsnes” rail duplicates five of the sixteen TOC entries and, on mobile, pushes the first chapter roughly one viewport down.
- There is no `<dfn>` or term index; definitions live in prose and in one glossary table at the end, with no first-use link.
- There are no interactive instruments despite `.instrument` CSS, and no visible “Pārbaudes gadījumi” table.
- The QA report claims Chrome at 1440/768/390 and a print PDF, but the screenshot sample covers selected chapters, not all 16. The plan treats this as a sample, not a full visual audit.

### 0.4 How to use this plan

- Each task has **one goal**, **a verified evidence base**, **an exact change list**, **acceptance criteria**, **3 substeps**, and **2–3 subtasks with 3 substeps each**.
- The tasks are ordered by dependency, not by glamour. Correctness (T06–T07), structure (T01–T05), accessibility (T09), and then design (T11–T15), explanation (T16–T19), and features (T20 + backlog).
- All edits must be made in the **build sources** (`build/ch*.html`, `build/tasks_*.py`, `build/figures.py`, `build/head.html`, `build/taskbase.py`, `build/build.py`) and then regenerated with `python3 build/build.py`. Editing the 490 KB master directly will be overwritten.
- “P0” means fix before the next study use; “P1” means fix in the next design pass; “P2” means an enhancement that should not block correctness work.
- The plan deliberately distinguishes **source defects** (`K…` in the existing register) from **defects introduced by this document** (new `I…` register, starting with `I1` for P2). Do not mislabel an internal transcription error as a source defect.

---

## 1. Evidence ledger (verified, line-referenced)

Severity: **S1** = wrong number or wrong concept; **S2** = structural/accessibility break; **S3** = craft/consistency; **S4** = enhancement.

| ID | Finding | Evidence | Severity | Task |
|---|---|---|---|---|
| E01 | P2 prints `m(šķīdums) = 1020 g` for `ρ = 1,03 g/mL`; correct is 1030 g. The printed `78,69/1020 = 7,640 %` is false; 1020 gives 7,716 %. | `build/tasks_a.py:383–385`; source E uses 1030 and 78,72 | S1 | T06, T07 |
| E02 | Figure captions are out of document order: 2, 4, 3, 9, 1, 5, 6, 7, 8. | `build/figures.py:90,129,160,218,386`; rendered captions | S2 | T08 |
| E03 | Duplicate anchors `t-c11`, `t-c12`, `t-c21`, `t-c22`. | `build/taskbase.py:20`; `C1.1`/`C11` etc. | S2 | T09 |
| E04 | Quantity map says 7 quantities, 8 nodes, 7 “independent”; mass balance is ignored. | `build/ch05_08.html:3,7` | S1 | T01 |
| E05 | Terminology row prints “šķīdinātājs — šķīdinātājs”. | `build/ch13_14.html:125` | S1 | T02 |
| E06 | Terminology row says `w(V)` refers to solution volume. `w` is mass/mass. | `build/ch13_14.html:126` | S1 | T02 |
| E07 | Double negative: “nav dota un ir nav pārbaudīta”. | `build/ch13_14.html:207` | S1 | T02 |
| E08 | “Papildinājums papildinājums” duplication in a role block. | rendered chapter 11; inline `prov p-add` inside `role-label` | S3 | T05 |
| E09 | `O1`–`O5` inside `<ol>` renders as “1. O1.” etc. | `build/ch01_04.html:6–12` | S3 | T10 |
| E10 | Skip link is inside `<main id="saturs">`, after masthead and TOC. | `Master…html` body; skip link position | S2 | T09 |
| E11 | “Pārbaudi sevi” (14×) sits inside `role-verified` blue surfaces; role taxonomy has 9 labels. | `build/taskbase.py:33`; role-label counts | S3 | T05, T13 |
| E12 | `h1`/`h2` serif, `h3`/`h4` sans; heading family changes mid-hierarchy. | `build/head.html:108–110` | S3 | T12 |
| E13 | Mobile tables 9/10 overflow 390 px; right-hand columns cut. | `build/qa/w390-ch5.png` | S2 | T14 |
| E14 | Inline `papildinājums` is underlined like a link and reads as glued to the following sentence. | `build/ch05_08.html:48`; `build/ch13_14.html:207` | S3 | T15 |
| E15 | P12 computes acetylcysteine and sucrose w, but not ascorbic acid; 3.33 % is unaccounted. | chapter 12 P12; `build/scratch` source | S1 | T10 |
| E16 | Rehydron citrate is `C6H5Na3O7` (anhydrous); hydrate assumption is unstated. | chapter 12 table; `build/calc.py:34` | S2 | T10 |
| E17 | No `<dfn>`/`class="term"`; glossary only at ch14; no term index. | grep `class="term"` = 0 | S3 | T04 |
| E18 | Masthead right rail duplicates TOC; mobile masthead consumes ~600 px. | `build/head.html:85–91`; `w390-top.png` | S3 | T11 |
| E19 | Print sample is partial (selected chapters); 106 pages; no chapter running head; `@page` margin boxes unverified in Chrome. | `build/qa/`; `build/head.html` print block | S3 | T15 |
| E20 | No interactive instruments despite `.instrument` CSS; no test-vector table. | grep `.instrument` vs body | S4 | T20 + backlog |
| E21 | `Saisnes`/`Saīsnes` is a redundant quick-link rail, not a reading aid. | masthead | S3 | T11 |
| E22 | P2 is the only displayed equality caught by a naive check, but the build never parses equations. | `build/build.py` `check()` | S1 | T07 |
| E23 | `O1`–`O5` and `K10` etc. share list markup but only O-list is double-numbered. | `build/ch01_04.html:6–12` | S3 | T10 |
| E24 | Dark-mode tone contrasts are measured above 4.5:1, but the tone ladder is not used as a legend; data figures use it inconsistently. | CSS tokens; figures | S3 | T14 |
| E25 | “Pārbaudīts” overclaims for answers that are recomputed, not source-verified; the label should distinguish “pārbaudīts ar programmu” from “avotā”. | `build/taskbase.py:33`; ch1 role legend | S3 | T05 |

---

## 2. Task template used below

Each task follows this exact shape so that it can be executed by a different agent without re-reading the whole plan:

1. **Priority / effort / dependencies.**
2. **Why this matters** — the learning or correctness consequence, not just aesthetics.
3. **What is wrong now** — exact file, line, and quoted string.
4. **What to change** — the smallest correct change, with proposed Latvian wording where it matters.
5. **Acceptance criteria** — machine-checkable where possible.
6. **The 3 substeps** — audit, change, verify.
7. **Subtasks** — 2–3, each with exactly 3 substeps.
8. **Suggested features** — what to add only after the correction is stable.
9. **Verification commands / evidence.**
10. **Risk and rollback.**

---

## 3. The 20 tasks

---

### T01 — Correct the quantity-map ontology: eight quantities, three derived, four bridges

**Priority:** P0 · **Effort:** S–M · **Depends on:** none · **Evidence:** E04

**Why this matters.** The quantity map is the document’s backbone. Every worked task is presented as a route over it (`Maršruts`), and the first sentence of chapter 5 tells the student what the whole topic is. If the map says “seven quantities” in one sentence and shows eight nodes in the figure, the student learns that the central model is arbitrary. If it says “seven independent quantities” while `m(šķīdums) = m(viela) + m(šķīdinātājs)` holds, the student learns a false independence claim. This is not cosmetic: it affects how students choose a route and whether they think they need a fourth given value.

**What is wrong now.**

- `build/ch05_08.html:3`: “Šīs tēmas kodols ir viena karte: **septiņi lielumi** un četras pārejas starp tiem.”
- `build/ch05_08.html:7`: “Kartē ir **astoņi mezgli**, bet tikai **septiņi neatkarīgi lielumi**: …”
- The list that follows names eight quantities: `m(viela)`, `n`, `V`, `m(šķīdums)`, `m(šķīdinātājs)`, `c`, `γ`, `w`.
- The figure caption at `build/figures.py:90` says “astoņiem mezgliem”.
- The map’s own alt description in the rendered SVG names eight nodes.

**What to change.**

1. Replace the lead with an exact statement:

> “Šīs tēmas kodols ir viena karte: **astoņi lielumi** un **četras pamatpārejas** starp tiem. Pieci lielumi ir pamata — `m(viela)`, `n`, `V(šķīdums)`, `m(šķīdums)`, `m(šķīdinātājs)`; trīs ir atvasināti — `c`, `γ`, `w`. Trīs masas saista masas bilance `m(šķīdums) = m(viela) + m(šķīdinātājs)`, tāpēc uzdevumā parasti doti nevis visi pieci, bet tik daudz, cik nepieciešams maršrutam.”

2. Delete the word “neatkarīgi”. Replace it with “pamata” / “atvasināti”. If the document wants a degrees-of-freedom statement, write it explicitly:
   > “Ja ir zināma molmasa `M` un blīvums `ρ`, tad ar `m(viela)` un `V` pietiek, lai aprēķinātu `n`, `c`, `γ`, `w`, `m(šķīdums)` un `m(šķīdinātājs)`.”
3. Add a small three-column table immediately after the map:

| Slānis | Lielumi | Kā iegūst |
|---|---|---|
| Pamata | `m(viela)`, `n`, `V`, `m(šķīdums)`, `m(šķīdinātājs)` | Dots uzdevumā vai izmērīts |
| Atvasinātais | `c`, `γ`, `w` | `c=n/V`, `γ=m/V`, `w=m(viela)/m(šķīdums)` |
| Saite | `M`, `ρ` | `n=m/M`, `m(šķīdums)=Vρ` |

4. Update the figure caption and `<desc>` to say “astoņi lielumi: pieci pamata un trīs atvasināti; četras pamatpārejas M, V, ρ, w”. Do not call the derived nodes “independent”.
5. Update the chapter 1 “Apzīmējumi” table if it implies that all eight are independent; add a note that `c`, `γ`, `w` are derived.
6. Update the recall prompt in chapter 5 that asks “Kādas ir četras pamatpārejas?” — keep the four, but add a second prompt: “Kuri trīs lielumi ir atvasināti un no kā?” Answer: `c=n/V`, `γ=m/V`, `w=m(viela)/m(šķīdums)`.
7. Run the existing route checker (`build/routes.py`) after the rewrite. No route key should change; only the prose should.

**Acceptance criteria.**
- `grep -n 'septiņi lielumi' Master…html` returns no hit outside a quoted historical sentence (there should be none).
- `grep -n 'septiņi neatkarīgi'` returns nothing.
- The map’s `<desc>` names eight nodes and three derived quantities.
- Every “Maršruts” line still uses the same node names (`m(viela)`, `m(šķīdums)`, `m(šķīdinātājs)`, `n`, `V`, `c`, `γ`, `w`).
- `python3 build/routes.py` reports all routes connected.

#### The 3 substeps

1. **Audit the prose and the figure for every count word.** Search `septiņ`, `astoņ`, `neatkarīg`, `pamatpārej`, `atvasināt` in `build/ch05_08.html`, `build/figures.py`, `build/ch01_04.html`, and the recall generator. Record every hit with its current sentence.
2. **Rewrite the ontology in one place and propagate.** Make chapter 5 the canonical definition; make chapter 1 point to it; make the figure caption and `<desc>` quote it; make recall answers match it. Do not create a second competing definition.
3. **Verify with the route checker and a text search.** Run `build/build.py`, `build/routes.py`, and the `grep` checks. Read the rendered chapter 5 at 1440 and 390 px to confirm the new table does not break the reading column.

#### Subtask 1.1 — Fix the chapter 5 prose and table

1. Replace the lead sentence and the “astoņi mezgli, bet tikai septiņi…” sentence with the exact wording in “What to change”.
2. Insert the three-column “Slānis / Lielumi / Kā iegūst” table; give it the next free table number and a caption that says it is a reading aid, not a new source claim.
3. Add one sentence explaining why the three masses are not independent: “Trīs masas nav neatkarīgas: ja zināmas divas, trešo dod masas bilance.”

#### Subtask 1.2 — Fix the figure and the alt text

1. Change the caption in `build/figures.py:90` from “astoņiem mezgliem” to “astoņiem lielumiem: pieciem pamata un trim atvasinātiem”.
2. Change the SVG `<desc>` to name the base and derived quantities and the four bridges.
3. Regenerate the figure and inspect the rendered SVG at 1440 and 390 px; confirm no label overlaps and no label is cut off.

#### Subtask 1.3 — Fix the recall and the glossary cross-reference

1. Add the new recall prompt “Kuri trīs lielumi ir atvasināti?” with the formula answer.
2. Change any recall answer that says “septiņi lielumi” to “astoņi lielumi”.
3. Add a link from the chapter 1 “Apzīmējumi” section to `#n5` (“Lielumu karte”) so the reader can see the canonical map.

**Suggested features.**
- **Route explorer:** a small inline SVG version of the map where clicking a node highlights the shortest route to `c` or `w`; no storage, no animation beyond a 120 ms focus transition. This is a natural extension of the existing `route-mini` geometry.
- **“Given / find” toggle:** each task could show two extra lines: “Dotie mezgli” and “Meklējamais mezgls”, generated from the same route key. This makes the map operational rather than decorative.
- **Map legend in print:** a one-line legend under the figure: “Pamata = 5; atvasinātie = 3; bultas = 4 pārejas.”

**Verification commands.**

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_3
python3 build/build.py
python3 build/routes.py
grep -nE 'septiņi lielumi|septiņi neatkarīgi' Master_3_tema_skidumi_un_koncentracijas.html
grep -o 'class="fig-cap">[^<]*' Master_3_tema_skidumi_un_koncentracijas.html | head
```

**Risk / rollback.** Low. The only risk is changing the route vocabulary in a way that breaks the printed `Maršruts` lines; the route checker and a diff of task text will catch it. Revert `build/ch05_08.html` and `build/figures.py` if the checker fails.

---

### T02 — Repair the terminology table: one term per role, and stop calling `w` volume-based

**Priority:** P0 · **Effort:** S · **Depends on:** T01 (for consistent map vocabulary) · **Evidence:** E05, E06, E07

**Why this matters.** Chapter 14 is the document’s explicit contract with the student about language. If the contract itself contains a garbled recommendation and a false statement about `w`, the student has no stable place to resolve a terminology question. The `w(V)` error is especially dangerous because it teaches the exact denominator confusion the rest of the document is trying to prevent: `w` is mass of solute per mass of solution, not per volume.

**What is wrong now.**

- `build/ch13_14.html:125`:
  > `šķīdināmā / izšķīdusī / izšķīdinātā viela` → “**izšķīdinātā viela**; **šķīdinātājs** — šķīdinātājs”
  The recommendation repeats “šķīdinātājs” and reads like a copy/paste error.
- `build/ch13_14.html:126`:
  > “γ, c un **w(V)** attiecas uz šķīduma tilpumu (K13)”
  `w` is a mass fraction; it refers to the mass of solution. `γ` and `c` refer to volume. The parenthetical `(V)` is either a typo for “w” or a conceptual error; either way it must go.
- `build/ch13_14.html:207`:
  > “Šī analīze avotā nav dota un ir **nav pārbaudīta**”
  Double negative; it should be “un nav pārbaudīta”.

**What to change.**

1. Rewrite the first row as:
   > **Sastopams:** `šķīdināmā viela`, `izšķīdusī viela`, `izšķīdinātā viela`  
   > **Ieteicams:** `izšķīdinātā viela` (solute); `šķīdinātājs` (solvent)  
   > **Iemesls:** “Viena loma — viens termins. ‘Šķīdinātājs’ ir vide, kas šķīdina, nevis viela, kas izšķīst.”
2. Rewrite the C10 row reason:
   > “γ un c attiecas uz **šķīduma tilpumu**; w — uz **šķīduma masu**. Tāpēc ‘300 mL ūdens’ nav tas pats, kas ‘300 mL šķīduma’ (K13).”
3. Add a dedicated row for the most common confusion:
   > **Sastopams:** “masas daļa” un “masas koncentrācija” lietoti kā sinonīmi  
   > **Ieteicams:** `w = m(viela)/m(šķīdums)` (bez dimensijas); `γ = m(viela)/V(šķīdums)` (g/L = mg/mL)  
   > **Iemesls:** “Dažādi saucēji: masa pret tilpumu. Tikai `ρ ≈ 1 g/mL` gadījumā skaitļi sakrīt.”
4. Fix the morphology sentence:
   > “Šī analīze avotā nav dota un **nav pārbaudīta**; lietojiet to tikai kā atceres palīgu, nevis kā etimoloģisku avotu.”
5. Scan the rest of the 23 terminology rows for the same pattern: every row must have exactly one recommended expression per role, no semicolon-separated duplicate, and a reason that names the consequence (denominator, unit, identity, or exam policy). If a row has two recommendations, split it into two rows.
6. Add “(solute)” and “(solvent)” in parentheses in the bilingual table (chapter 14, table 20) so the English mapping is unambiguous.

**Acceptance criteria.**
- `grep -n 'šķīdinātājs</strong> — šķīdinātājs'` returns nothing.
- `grep -n 'w(V)'` returns nothing.
- `grep -n 'ir nav pārbaudīta'` returns nothing.
- Every row of table 18 has exactly one “Ieteicams” phrase per role; the table has a row for `w` vs `γ`.
- The bilingual table maps `solute` → `izšķīdinātā viela` and `solvent` → `šķīdinātājs`.

#### The 3 substeps

1. **Audit all 23 rows** for duplication, missing consequence, and denominator errors. Mark each row `OK`, `SPLIT`, or `REWRITE`.
2. **Rewrite the affected rows** and the morphology paragraph; keep the table’s three-column shape and the existing `K` references.
3. **Add a regression grep** for the three exact bad strings and a manual read of table 18 at 1440 and 390 px.

#### Subtask 2.1 — Rewrite the solute/solvent row and the C10 row

1. Replace the recommendation cell with `izšķīdinātā viela (solute); šķīdinātājs (solvent)`.
2. Replace the reason with the “one role — one term” sentence.
3. Change the C10 reason to separate `γ/c` (volume) from `w` (mass).

#### Subtask 2.2 — Add the `w` vs `γ` row and fix the double negative

1. Insert the new row immediately after the C10 row, with the formulas and the `ρ ≈ 1` caveat.
2. Fix the morphology sentence.
3. Check that the new row does not duplicate the existing “masas koncentrācija γ un blīvums ρ” row; if it does, merge them so the table still has one row per distinction.

#### Subtask 2.3 — Audit the bilingual table and add a term-consistency test

1. Add `(solute)` / `(solvent)` to table 20.
2. Add a small script or grep that checks every table-18 row has a `<strong>` recommendation and a non-empty reason.
3. Read the rendered table at 390 px; if it becomes too wide, apply the responsive table strategy from T14 rather than shrinking the font below 14 px.

**Suggested features.**
- **Term index with anchors:** link table 18 rows to the first-use `<dfn>` (T04), so a student can jump from “šķīdinātājs” to the definition and back.
- **“Say it precisely” micro-card:** a one-screen, three-line card in chapter 1: “masa / tilpums / daļa” with the three formulas. This is a retrieval aid, not a new chapter.

**Verification commands.**

```bash
grep -nE 'šķīdinātājs</strong> — šķīdinātājs|w\(V\)|ir nav pārbaudīta' Master_3_tema_skidumi_un_koncentracijas.html
python3 build/build.py
```

**Risk / rollback.** Low. The only judgment call is whether to split the `w`/`γ` row or merge it with the existing `γ`/`ρ` row; either is acceptable if the table still has one row per distinction. Keep the old row in a backup diff if the table numbering shifts.

---

### T03 — Make the symbol and unit policy enforceable, not just stated

**Priority:** P1 · **Effort:** M · **Depends on:** T02 · **Evidence:** E05, E06, E12; build warnings

**Why this matters.** The course uses `C_M`, `c_M`, `c`, `“M”` and `M` for two different quantities. The document explains this well, but the explanation is prose, not a constraint. A student who reads “M” in a formula, a table, and a sentence can still confuse mol/L with g/mol. The document needs a visible policy, a single notation in its own prose, and a build check that prevents regressions.

**What is wrong now.**

- Table 19 (`build/ch13_14.html`) lists the variants but does not state a hard rule for the document’s own prose. It says “Rakstiet mol/L, ja nav skaidrs” — a soft recommendation.
- `build/build.py` has a `transform_text` rule that replaces `digit + M` with `digit + mol/L`, but it does not catch `M` in tables, parentheticals, or formulas. The build warnings show four “M unit” hits that are actually quantity assignments (`M = 163,94`), so the check is noisy in the other direction.
- The document uses `M` as a quantity everywhere (`M(NaCl) = 58,44 g/mol`), which is correct, but the boundary between “quantity M” and “unit M” is not machine-checked.
- Decimal comma is used correctly in prose, but the build only checks `digit.digit`; it does not check missing non-breaking spaces after units in generated task text.

**What to change.**

1. Add a **“Simbolu lieta”** box in chapter 1, after “Apzīmējumi”:

> **Šajā dokumentā:** `c(B)` = vielas daudzuma koncentrācija, `mol/L`; `M(B)` = molmasa, `g/mol`; `w(B)` = masas daļa, bez dimensijas; `γ(B)` = masas koncentrācija, `g/L = mg/mL`; `ρ` = šķīduma blīvums, `g/mL`.
> **Kursa pieraksts:** `C_M`, `c_M`, `c` un `“M”` var apzīmēt to pašu koncentrāciju; `M` var apzīmēt arī molmasu. Testā atpazīstiet kursa pierakstu, bet savā risinājumā rakstiet `c(B), mol/L` un `M(B), g/mol`.

2. Replace every bare `“M”` in the document’s own prose with `mol/L`, except in the quoted course notation and in the change log. Add a `data-quote` attribute or a `«»` wrapper to quoted occurrences so the linter can distinguish them.
3. Add **number-format rules** to the same box:
   - decimal comma in Latvian prose (`12,5`, not `12.5`);
   - non-breaking space between number and unit (`12,5&nbsp;mL`);
   - unit symbols `mL`, `L`, `g`, `mg`, `mol/L`, `g/mL`, `mg/mL`, `mmol/L`;
   - no `ml`, `l`, `cc`, `ppm` in the document’s own prose;
   - `%` is written with a space in prose (`5 %`), but `%` in a formula may be tight.
4. Add a build gate in `build/build.py`:
   - scan text outside `<style>`, `<script>`, `<svg>`, and `<code>`;
   - flag bare `digit + M` unless the context contains `M =` or `M(` (quantity) or is inside a quote;
   - flag `digit.digit` followed by a unit;
   - flag `digit + space + unit` (missing `&nbsp;`);
   - flag lowercase `ml`/`l` unless inside a quoted source or the K22 row.
5. Keep a whitelist for the K table and `Piezīme avotam`, because those sections must quote bad source spelling. The existing `check()` already has a whitelist; extend it rather than replacing it.

**Acceptance criteria.**
- The document contains no bare `M` used as a unit in its own prose. The K table may quote `“M”`.
- The build gate emits 0 errors for the document and a nonzero exit only when a new violation is introduced.
- All 67 tasks use `mol/L` in their `Dots`/`Aprēķins` fields, and `M(...)` only for molar mass.
- `grep -nE '\b[0-9,]+ ?M\b'` hits are all quantity assignments or quoted source text.

#### The 3 substeps

1. **Inventory all `M` occurrences** and classify each as `quantity`, `unit`, `course quote`, or `source quote`. Write the classification into a temporary CSV under `build/scratch/`.
2. **Rewrite the prose and add the policy box.** Do not change formulas that are correct; change only the ambiguous unit usage.
3. **Add the build gate and run it against the current document.** It should pass after the rewrite and fail on a synthetic bad line (`5 M HCl`).

#### Subtask 3.1 — Build the notation inventory

1. Extract every `M` occurrence with 40 characters of context into a scratch file.
2. Classify each as `M(B)`, `M =`, `mol/L`, `“M”` quote, or `other`.
3. Identify all `ml`/`l`/`cc`/`ppm` occurrences and mark those that are inside a quoted source defect.

#### Subtask 3.2 — Add the policy box and normalize the prose

1. Insert the box in chapter 1 and link it from table 19.
2. Replace ambiguous `M` units with `mol/L`; leave `M(B)` and `M =` alone.
3. Add `&nbsp;` where the build’s `UNIT_RE` misses a unit (for example after `)` or after a number followed by `%` in a table cell).

#### Subtask 3.3 — Add the unit linter

1. Implement `check_units(doc)` in `build/build.py`, returning a list of `(line, message)`.
2. Add a `--strict-units` mode or make it part of the default `check()`; print the first 20 violations.
3. Add a synthetic test fixture in `build/scratch/` with `5 M HCl`, `12.5 ml`, and `3 g` missing `&nbsp;`; confirm each is flagged.

**Suggested features.**
- **Copy-safe answer format:** a small “Atbildes pieraksts” card that shows the expected form: `c(NaCl) = 0,154 mol/L`, `w = 0,90 %`, `γ = 9,0 mg/mL`.
- **Unit converter strip:** `1 g/L = 1 mg/mL`, `1 mL = 1 cm³`, `1 mol = 1000 mmol`, always visible in the formula appendix.

**Verification commands.**

```bash
python3 build/build.py
grep -nE '\b[0-9,]+ ?M\b' Master_3_tema_skidumi_un_koncentracijas.html | head -20
grep -nE '\b[0-9,]+ ?(ml|l|cc|ppm)\b' Master_3_tema_skidumi_un_koncentracijas.html | head -20
grep -nE '[0-9]\.[0-9]+ ?(mL|L|g|mg|mol)\b' Master_3_tema_skidumi_un_koncentracijas.html | head -20
```

**Risk / rollback.** Medium. The linter can produce false positives on formulas such as `M = 163,94` and on quoted course notation. Build the whitelist first, then tighten. Keep the rule conservative: a false negative is better than a false positive that forces bad prose edits.

---

### T04 — Add first-use definitions and a real term index

**Priority:** P1 · **Effort:** M · **Depends on:** T02 · **Evidence:** E17

**Why this matters.** The glossary currently lives in chapter 14, after the student has already met `dispersā fāze`, `šķīdība`, `α`, `ekvivalences punkts`, `ierobežojošais reaģents`, etc. A reader who forgets a term mid-chapter has to leave the page, find chapter 14, and scan a 23-row table. That is unnecessary cognitive load for a study document whose whole design is “read, retrieve, check”.

**What is wrong now.**

- `grep -c 'class="term"'` = 0; no `<dfn>`; no first-use links.
- Chapter 14 has a good table, but it is not connected to the prose.
- Some terms are defined in prose (`dispersā sistēma`, `šķīdība`), some in tables (`α`, `c`, `γ`), and some only in the glossary (`mērkolba`). There is no single retrieval path.
- The document says “term definitions marked once at first use” in the prompt, but the implementation does not mark them.

**What to change.**

1. Build a list of **25 core terms** and assign each a stable anchor:

```
šķīdums, dispersā sistēma, dispersā fāze, dispersijas vide,
šķīdība, piesātināts šķīdums, elektrolīts, disociācijas pakāpe,
mols, molmasa, masas daļa, molārā koncentrācija,
masas koncentrācija, blīvums, atšķaidīšana, sajaukšana,
neitralizācija, ierobežojošais reaģents, ekvivalences punkts,
deva, deva uz kg, suspensija, koloids, mērkolba, šķīdinātājs
```

2. At the **first prose occurrence** of each term, wrap it in `<dfn id="term-…">…</dfn>`. Do not wrap the term in tables or figure labels; tables can link to the anchor.
3. In chapter 14, add a “Terminu rādītājs” alphabetical list of links to `#term-…`. For terms whose first use is a table, link the table caption to the anchor.
4. Add `abbr` for `m/m`, `m/V`, `V/V`, `SI`, `IUPAC` on first use, with `title` text in Latvian.
5. Add a build check: for each term in the list, exactly one `<dfn id="term-…">` exists; the anchor is referenced at least once from chapter 14; no `<dfn>` occurs after the term’s first prose use.
6. Do not add a JavaScript tooltip layer. The document must remain readable with JS off and in print.

**Acceptance criteria.**
- 25 `<dfn>` elements, one per core term, all with unique `id`s.
- Chapter 14 has a term index with 25 links, all resolving.
- No term is defined twice; no `<dfn>` appears after the first use.
- The printed document shows the definitions inline, not as hidden popups.

#### The 3 substeps

1. **Map first uses.** For each of the 25 terms, find the earliest occurrence in document order and record the chapter and paragraph.
2. **Mark up the first uses** with `<dfn>` and add the term index in chapter 14.
3. **Verify with a build script** and read the first-use paragraphs at 1440 and 390 px to confirm the definition does not interrupt the sentence.

#### Subtask 4.1 — Build the term/first-use map

1. Extract the text of each chapter and search for the 25 terms; record the first hit.
2. Decide whether the first hit is a definition context or a passing mention; if it is a passing mention, move the `<dfn>` to the next sentence that actually defines the term.
3. Write the map to `build/scratch/terms.csv` with columns `term, anchor, chapter, paragraph, current wording`.

#### Subtask 4.2 — Add `<dfn>` and the term index

1. Wrap each first use in `<dfn id="term-…">term</dfn>`; keep the surrounding grammar intact.
2. Add the alphabetical term index to chapter 14, after table 20; each entry is a link and a one-line gloss.
3. Add `abbr` for the four abbreviations and one sentence explaining that `m/m`, `m/V`, `V/V` are *kinds of percent*, not different quantities.

#### Subtask 4.3 — Add the definition-consistency gate

1. Parse all `<dfn id="term-…">` and all chapter-14 links; fail if a term has zero or more than one definition.
2. Fail if a `<dfn>` appears after the first plain-text occurrence in document order.
3. Print a table of `term, first chapter, definition chapter` so a reviewer can see the coverage.

**Suggested features.**
- **“Termins” margin note:** on wide screens, a small static margin note next to the first use; on mobile, it collapses into the existing paragraph. This borrows the *idea* of margin notes, not the Tufte hairline/cream styling.
- **Term flashcards:** reuse the 25 definitions as recall prompts in chapter 15, with the same in-memory toggle as T20.

**Verification commands.**

```bash
grep -c '<dfn id="term-' Master_3_tema_skidumi_un_koncentracijas.html
grep -o 'id="term-[^"]*"' Master_3_tema_skidumi_un_koncentracijas.html | sort | uniq -d
```

**Risk / rollback.** Low–medium. `<dfn>` inside a sentence can disturb line height if the CSS is not set; add `dfn{font-style:normal;font-weight:600}` and test subscripts nearby. If a term’s first use is inside a table cell, use a caption link instead of a `<dfn>` inside the cell.

---

### T05 — Fix the role/provenance language: “Pārbaudīts” is not “Pārbaudi sevi”

**Priority:** P1 · **Effort:** S–M · **Depends on:** T01, T02 · **Evidence:** E08, E11, E25

**Why this matters.** The document’s credibility rests on provenance. A blue block labelled “Pārbaudīts” means “this answer has been recomputed and checked”. A blue block labelled “Pārbaudi sevi” means “stop and retrieve”. They are different speech acts. Putting both inside `role-verified` teaches the student to read the blue surface as “trust this” even when the content is a question. The same surface also contains “Papildinājums”, “Drošība”, “Dokumenta robeža”, “Kā skaitīt” and “Saprāta pārbaude”, so the visual grammar no longer maps to a stable meaning.

**What is wrong now.**

- `build/taskbase.py:33` renders every 67 task answers as:
  ```html
  <div class="role role-verified"><p class="role-label">Pārbaudīts</p>…
  ```
- 14 recall blocks use `<div class="role role-verified"><p class="role-label">Pārbaudi sevi</p>`.
- One block prints “Papildinājums papildinājums” because the role label and an inline `prov p-add` span are both present.
- Role label counts: 68 “Pārbaudīts”, 25 “Biežākā kļūda”, 14 “Pārbaudi sevi”, 9 “Noteikums”, plus five one-off labels.
- The inline provenance span is underlined (`text-decoration: underline`) and has no separator, so it reads as a broken link or a typo.

**What to change.**

1. Define a **five-item language**, with only three semantic roles plus a neutral family:
   - **Noteikums** — a rule/definition. Tone 1, accent left rule.
   - **Biežākā kļūda** — a trap. Tone 3, ink left rule.
   - **Atbilde** — a verified result. Tone 2, accent-strong left rule. Label: “Atbilde · pārbaudīta ar programmu” (not just “Pārbaudīts”).
   - **Piezīme avotam** — a source-defect note. Neutral, no role colour; use a thin neutral rule.
   - **Pārbaudi sevi** — retrieval practice. Neutral surface or the existing `.recall-block`, never `role-verified`.
2. Replace the 67 task labels with “Atbilde · pārbaudīta” (or “Atbilde” + a smaller “pārbaudīta ar programmu” line). This is more honest: the answer is recomputed, not necessarily source-verified.
3. Move the 14 “Pārbaudi sevi” blocks out of `role-verified` into `recall-block` or a new neutral `.practice` block. Do not use the verified tone.
4. Remove the duplicate inline `papildinājums` in the one “Papildinājums” role block. If the paragraph needs provenance, put it in the role label only.
5. Rename one-off labels:
   - “Saprāta pārbaude” → “Pārbaude” or fold into “Atbilde”.
   - “Kā skaitīt” → “Noteikums” or a neutral “Metode”.
   - “Drošība” → neutral “Drošība” note, not a role colour.
   - “Dokumenta robeža” → neutral note.
6. Add a **role legend** in chapter 1, with one example of each of the five items and a sentence: “Krāsa nav vienīgā norāde; katram blokam ir tekstuala etiķete.”
7. Add `data-role` attributes (`rule`, `mistake`, `answer`, `source`, `practice`) so the build can count and the CSS can target without new hues.

**Acceptance criteria.**
- Exactly three `.role-*` colour classes are used for semantic roles (`role-rule`, `role-mistake`, `role-verified`), plus neutral `.source-note` and `.recall-block`.
- No “Pārbaudi sevi” inside `.role-verified`.
- No “Papildinājums papildinājums”.
- The role legend exists and lists five items, not nine.
- The build prints counts by `data-role`; the counts match the visible blocks.

#### The 3 substeps

1. **Inventory every role label and its CSS class.** Produce a table `label, class, count, intended speech act`.
2. **Reassign the speech acts.** Move recall to neutral; rename verified answers; fold one-offs; remove the duplicate.
3. **Add the legend and a build count.** Verify the visual hierarchy at 1440/768/390 and in print.

#### Subtask 5.1 — Inventory and classify the labels

1. Extract all `<p class="role-label">…</p>` and the nearest `.role` class.
2. Classify each as `rule`, `mistake`, `answer`, `source`, `practice`, or `other`.
3. Decide the final five-item vocabulary and write it into a scratch table before touching the HTML.

#### Subtask 5.2 — Migrate the blocks

1. Change `build/taskbase.py:33` to the new label and add `data-role="answer"`.
2. Move the 14 “Pārbaudi sevi” blocks to `recall-block`; remove their role wrapper.
3. Remove the duplicate inline `papildinājums` and add `data-role` to the remaining one-offs.

#### Subtask 5.3 — Add the legend and the count

1. Add the five-item legend in chapter 1, immediately after “Kā lasīt šo dokumentu”.
2. Add a build count by `data-role` and print it in the build output.
3. Check that the legend’s examples match the actual CSS colours and that the print stylesheet keeps the labels readable in grayscale.

**Suggested features.**
- **Role filter:** a plain `<details>` “Rādīt tikai kļūdas” toggle that hides/shows blocks by `data-role`; no storage, no animation. This is useful for exam revision.
- **Provenance line in the footer:** “67 atbildes pārbaudītas ar programmu; 38 piezīmes avotam; 75 atceres jautājumi.”

**Verification commands.**

```bash
grep -o '<p class="role-label">[^<]*' Master_3_tema_skidumi_un_koncentracijas.html | sed 's/.*>//' | sort | uniq -c | sort -rn
grep -n 'Papildinājums papildinājums' Master_3_tema_skidumi_un_koncentracijas.html
grep -c 'role role-verified' Master_3_tema_skidumi_un_koncentracijas.html
```

**Risk / rollback.** Low. The change is mostly labels and wrappers. The main risk is losing the visual distinction between “answer” and “practice”; keep a neutral background and a bold label, not a new hue.

---

### T06 — Correct the P2 arithmetic and register it as an internal defect (`I1`), not a source defect

**Priority:** P0 · **Effort:** XS · **Depends on:** T07 (for regression) · **Evidence:** E01

**Why this matters.** P2 is a worked example that teaches `w = m(solute)/m(solution)` from `c` and `ρ`. The current text prints a mass of solution that is 10 g too low. The answer happens to be right because it was copied from the key, but the working does not support it. A student who follows the printed intermediate gets 7.72 %, not 7.64 %, and will not know which number to trust. This is the single most important correctness fix in the document.

**What is wrong now.**

`build/tasks_a.py:383`:

```html
<i>n</i> = 0,48 mol; <i>m</i> = 0,48 · 163,94 = 78,69 g;
<i>m</i>(šķīdums) = 1020 g;
<i>w</i> % = 78,69/1020 · 100 = 7,640 %.
```

`build/tasks_a.py:385`:

```html
<i>Pārbaude.</i> 0,48 · 163,94 = 78,69 g; 78,69/1020 = 0,0764.
```

But `V = 1 L = 1000 mL`, `ρ = 1,03 g/mL`, so `m(šķīdums) = 1000 · 1,03 = 1030 g`. The source key E prints `78,72 g · 100/1030 = 7,64 %`.

**What to change.**

1. Replace `1020` with `1030` in both the calculation and the check:
   ```html
   <i>m</i>(šķīdums) = 1000 · 1,03 = 1030 g;
   <i>w</i> % = 78,69/1030 · 100 = 7,6398 %.
   ```
   and
   ```html
   <i>Pārbaude.</i> 78,69/1030 = 0,07640.
   ```
2. Keep the answer `7,64 %`; it is correct with 1030 g. Add a parenthetical: “ar kursa M = 164 un 78,72 g iegūst to pašu 7,64 %”.
3. Add an **internal defect register** entry `I1` in chapter 16, separate from K1–K23:
   > **I1** · Šī dokumenta P2 starprezultāts · `m(šķīdums) = 1020 g` · `1030 g` · `1000 · 1,03 = 1030`; ar 1020 atbilde būtu 7,72 %, nevis 7,64 % · C.
4. Add `P2` to `build/calc.py`’s expected values and to `build/build.py`’s critical-value list. The build currently checks final values but not the intermediate; after T07 it will check both.
5. Do not label this as K24. K is the source-defect register; this is a document transcription defect.

**Acceptance criteria.**
- `grep -n '1020'` in the P2 context returns nothing.
- `grep -n '78,69/1030'` returns the corrected calculation and check.
- The rendered answer is still `7,64 %`.
- `I1` appears in the change log with the exact before/after and confidence C.
- `python3 build/build.py` passes and the new equation auditor (T07) accepts P2.

#### The 3 substeps

1. **Patch the two strings** in `build/tasks_a.py` and add the `I1` row.
2. **Add the expected values** to `build/calc.py` and `build/build.py` so the build can catch a regression.
3. **Regenerate, inspect, and diff** the P2 block at 1440 and 390 px; confirm the corrected line does not overflow the route column.

#### Subtask 6.1 — Correct the calculation and check lines

1. Replace `1020` with `1030` in the `calc` string.
2. Replace `78,69/1020 = 0,0764` with `78,69/1030 = 0,07640`.
3. Add the source comparison sentence: “Avota E rēķina ar M = 164 un 78,72 g; 78,72/1030 = 7,64 %, tāpēc atbilde nemainās.”

#### Subtask 6.2 — Add the `I1` register entry

1. Add a new subsection “Dokumenta iekšējie labojumi (I)” before or after the K table.
2. Add `I1` with the exact original, corrected, reason, confidence.
3. Add a sentence in the K-table introduction: “K1–K23 ir avotu defekti; I1 ir šī dokumenta labojums, kas radušies pārrakstot.”

#### Subtask 6.3 — Add the regression value

1. Add `P2` to `build/calc.py` with the exact `w=...` and a `m_solution` field.
2. Add the string `7,6398` (or the chosen precision) to `build/build.py`’s critical values.
3. Run the build twice; confirm deterministic output and no warning.

**Suggested features.**
- **“Show the units” line** in every task: a small `g/mL · mL = g` check under the calculation. This would have made the 1020/1030 error obvious.
- **Internal defect badge** `I1` with a link to the change log, so a reader can see that the document corrects itself, not only the source.

**Verification commands.**

```bash
grep -n '1020\|78,69/1030\|7,6398' build/tasks_a.py
python3 build/build.py
```

**Risk / rollback.** Very low. The answer is unchanged; only the intermediate and check change. If `I1` is judged too much register overhead, keep the correction and add it to “Redakcijas lēmumi” instead.

---

### T07 — Build an equation-level auditor so a false intermediate can never pass again

**Priority:** P0 · **Effort:** M–L · **Depends on:** T06 · **Evidence:** E01, E22

**Why this matters.** `build/build.py` currently checks that selected final values appear somewhere in the text. That is a string-presence test, not an arithmetic test. P2 passes because `7,640` is present, even though the line that produces it is false. A study document that claims “every number is recalculated” needs an auditor that reads the displayed equalities and checks them, not a list of expected strings.

**What is wrong now.**

- `build/build.py` `check()` contains a list of `needle` strings (`'1,00 mol/L'`, `'0,3263'`, …) and fails only if a string is absent.
- It does not parse `Aprēķins` or `Pārbaude`.
- `build/calc.py` computes correct values, but the rendered task strings are authored separately in `tasks_a.py` / `tasks_b.py`, so a transcription error can diverge from the calculation.
- The P2 error is exactly that divergence: `calc.py` uses 1.03, `tasks_a.py` prints 1020.

**What to change.**

1. Add `build/equations.py` with a small, conservative parser:
   - strip HTML tags and decode entities;
   - normalize `·`, `×` to `*`, `−` to `-`, `,` decimal to `.`;
   - extract patterns `number op number = number` and chained forms;
   - evaluate with `decimal.Decimal` or `float` and a tolerance based on the printed precision;
   - skip expressions containing variables, units, or `→` unless a numeric substitution is explicit;
   - return `(source, expression, expected, actual, status)`.
2. Add a `data-eq` attribute or a JSON sidecar for each task:
   - `build/tasks_a.py` / `tasks_b.py` can emit `data-eq="m_solution:1030"` etc.;
   - alternatively, `build/equations.py` parses the rendered `calc`/`check` text directly. Start with parsing; add `data-eq` only if parsing is too noisy.
3. Integrate into `build/build.py`:
   - run the auditor after assembly;
   - fail with a nonzero exit on any false equality;
   - print a compact table of `task, expression, printed, computed, delta`.
4. Add fixtures:
   - P2 before fix should fail;
   - P2 after fix should pass;
   - C6, C7, B7, K21, BSC3, Rehydron sum should pass;
   - a synthetic `2 + 2 = 5` should fail.
5. Add the auditor’s output to the QA report (`build/qa/report.json` or a new `build/qa/equations.json`).
6. Do not try to prove every formula symbolically. The goal is to catch **displayed numeric equalities**, not to replace `calc.py`.

**Acceptance criteria.**
- `python3 build/equations.py` prints 0 failures on the corrected document.
- The pre-fix P2 content fails with a clear message: `78,69/1020 = 7,640` → actual 7.716.
- `build/build.py` runs the auditor and exits nonzero on failure.
- The auditor ignores expressions with variables (`n = cV`, `w = m/M`) and does not produce false positives on them.
- A short “Pārbaudes gadījumi” table is visible in the appendix, listing 8–12 representative equations and their status.

#### The 3 substeps

1. **Write the parser and run it in report-only mode** against the current document; collect false positives and false negatives.
2. **Tune the whitelist and tolerance**; integrate into the build as a hard gate.
3. **Add fixtures and a visible test-vector table**; run the gate on the corrected document and on a deliberately broken copy.

#### Subtask 7.1 — Write the parser

1. Extract text from `calc` and `check` fields, not the whole document, to reduce noise.
2. Implement tokenization for numbers, operators, parentheses, and `=`; evaluate simple numeric expressions left-to-right with standard precedence.
3. Emit a JSON report with `task_id`, `expression`, `printed`, `computed`, `delta`, `status`.

#### Subtask 7.2 — Integrate and tune

1. Add the call to `build/build.py` and a `--no-equations` escape hatch for debugging.
2. Build a whitelist for display rounding: allow `abs(delta) <= 0.5 * 10^-decimals` of the printed result.
3. Run on the full document; fix any real errors and whitelist only expressions that are intentionally approximate (e.g., “≈”).

#### Subtask 7.3 — Add fixtures and the public test-vector table

1. Add `build/qa/equations.json` with 12 cases and expected statuses.
2. Render a small “Pārbaudes gadījumi” table in chapter 16 with 8 rows: `P2`, `C6`, `C7`, `B7`, `K21`, `BSC3`, `P4`, `C18`.
3. Add a one-line note: “Šie nav uzdevumu atbildes; tie ir auditora testi.”

**Suggested features.**
- **Equation audit badge:** a footer line “0 false equalities in 67 tasks”.
- **Per-task “check” link:** a small “pārbaudīts ar programmu” link that opens the auditor’s JSON entry (no network; inline `<details>`).

**Verification commands.**

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_3
python3 build/equations.py
python3 build/build.py
python3 - <<'PY'
# synthetic negative test
from build.equations import check_text
print(check_text('78,69/1020 · 100 = 7,640'))  # must be False
PY
```

**Risk / rollback.** Medium. Numeric parsing of human prose is messy; expect false positives. Start in report-only mode, keep the gate off by default until the whitelist is stable, then turn it on. The auditor should never edit content; it only reports.

---

### T08 — Renumber figures in document order and add a figure register

**Priority:** P1 · **Effort:** S · **Depends on:** T01 · **Evidence:** E02

**Why this matters.** Figure numbers are navigation. A reader who sees “skatīt 1. attēlu” expects it before “2. attēls”. The current document places the quantity map (numbered 1) in chapter 5, after the particle scale (2), the Ostwald curve (4), the ion strip (3) and the unit ladder (9). The sequence looks like an authoring artifact, not a designed document, and it makes the appendix’s figure references unreliable.

**What is wrong now.** Document order of captions:

| Document position | Current caption | File |
|---:|---|---|
| 1 | 2. attēls — particle scale | `build/figures.py:129` |
| 2 | 4. attēls — Ostwald | `build/figures.py:218` |
| 3 | 3. attēls — ion strip | `build/figures.py:160` |
| 4 | 9. attēls — unit ladder | `build/figures.py:386` |
| 5 | 1. attēls — quantity map | `build/figures.py:90` |
| 6 | 5. attēls — volumetric flask | `build/figures.py:262` |
| 7 | 6. attēls — dilution ladder | `build/figures.py:294` |
| 8 | 7. attēls — mixing | `build/figures.py:319` |
| 9 | 8. attēls — neutralisation | `build/figures.py:349` |

**What to change.**

1. Decide the canonical order. Recommended: **document order**, not conceptual importance:
   ```
   1 particle_scale
   2 ostwald
   3 ion_strip
   4 unit_ladder
   5 quantity_map
   6 volumetric
   7 dilution_ladder
   8 mixing
   9 neutralisation
   ```
   If the author prefers the quantity map first, move the map to chapter 1 or chapter 2, not just renumber it. Do not keep a “1” in chapter 5.
2. Update every caption in `build/figures.py` to the new number.
3. Add a `FIG_ORDER` list in `build/figures.py` or `build/build.py` and assert that captions are strictly increasing in the assembled HTML.
4. Add an **“Attēlu saraksts”** table in chapter 16:
   | Nr. | Nosaukums | Nodaļa | Tips |
   |---:|---|---|---|
5. Add in-text references only where they help (“skatīt 5. attēlu”), and check each reference resolves.
6. Update the `<title>`/`<desc>` if they mention a number (currently they use names, not numbers; keep it that way).

**Acceptance criteria.**
- Captions in document order are 1..9 with no gaps.
- A build assertion fails if a caption number is out of order.
- The appendix has a figure list with 9 rows and correct chapter links.
- No in-text reference points to the wrong figure.

#### The 3 substeps

1. **Decide and document the order** (document order vs conceptual order). If moving a figure, record the chapter change.
2. **Renumber captions and add the register.**
3. **Add the monotonic assertion and inspect** the figure list and captions at 1440/390 and in print.

#### Subtask 8.1 — Decide the order

1. List all 9 figures with their chapter, purpose, and dependencies.
2. Choose document order unless a figure is genuinely misplaced; if so, move it and update the chapter text.
3. Write the order into `build/FIG_ORDER.md` or a comment in `build/figures.py`.

#### Subtask 8.2 — Renumber and register

1. Edit the 9 caption strings in `build/figures.py`.
2. Add the “Attēlu saraksts” table to chapter 16.
3. Add a note in the figure captions’ `fig-kind` (“attēls veidots no datiem” / “shēma”) and keep it consistent.

#### Subtask 8.3 — Assert and inspect

1. Add `assert_figure_order(doc)` to `build/build.py`; fail if a caption number is not the previous + 1.
2. Regenerate and read the captions in order; confirm no “1. attēls” appears after “2. attēls”.
3. Check the figure list links; each should jump to the figure’s chapter, not to a task anchor.

**Suggested features.**
- **Figure zoom:** wrap each SVG in a `<details>` “Palielināt” on mobile, with the same SVG at 100% width. No JavaScript.
- **Data provenance tag:** every data figure already says “attēls veidots no datiem”; add the source or `papildinājums` in the caption.

**Verification commands.**

```bash
python3 build/build.py
python3 - <<'PY'
import re
s=open('Master_3_tema_skidumi_un_koncentracijas.html',encoding='utf-8').read()
nums=[int(x) for x in re.findall(r'(\d+)\. attēls',s)]
print(nums)
assert nums==list(range(1,10)), nums
PY
```

**Risk / rollback.** Low. Renumbering is mechanical; the only risk is a stale external reference. Since this is a single file, there are no external links to preserve.

---

### T09 — Fix duplicate anchors, the skip link, and the remaining accessibility defects

**Priority:** P0 · **Effort:** S–M · **Depends on:** none · **Evidence:** E03, E10

**Why this matters.** Duplicate IDs are invalid HTML and break in-page navigation and assistive technology. The skip link is the first keyboard affordance a user meets; if it points to its own container, it does nothing. These are small fixes with disproportionate effect on trust: a document that teaches precision should not have invalid anchors.

**What is wrong now.**

- `build/taskbase.py:20`:
  ```python
  anchor = 't-' + tid.lower().replace(' ', '').replace('.', '').replace('/', '-').replace('*', 's')
  ```
  `C1.1` → `t-c11`, which collides with `C11` → `t-c11`.
- Duplicate IDs in the rendered file: `t-c11` (2), `t-c12` (2), `t-c21` (2), `t-c22` (2).
- The skip link is inside `<main id="saturs">`:
  ```html
  <main id="saturs">
    <a class="skip" href="#saturs">Pāriet uz saturu</a>
  ```
  It cannot skip the masthead or the TOC.
- The TOC has a desktop and a mobile copy; both are fine, but the mobile copy is not a `<nav>` landmark. Add `aria-label="Saturs (mobilais)"` or wrap it in `<nav>`.
- `aria-current="true"` is valid, but the scroll handler calls `getBoundingClientRect()` for every section on every scroll; at 16 sections this is acceptable, but it is worth measuring.

**What to change.**

1. Change the anchor generator to preserve dots as dashes:
   ```python
   anchor = 't-' + tid.lower().replace(' ', '').replace('.', '-').replace('/', '-').replace('*', 's')
   ```
   `C1.1` → `t-c1-1`; `C11` → `t-c11`. Add a build assertion that all IDs are unique.
2. Move the skip link to the first element inside `<body>`, before `<header>`:
   ```html
   <a class="skip" href="#saturs">Pāriet uz saturu</a>
   <header class="masthead">…
   ```
   Keep `id="saturs"` on `<main>`.
3. Add `tabindex="-1"` to `<main id="saturs">` so focus actually moves there when the skip link is used (some browsers move focus only if the target is focusable).
4. Wrap the mobile TOC in `<nav aria-label="Saturs (mobilais)">` or add `role="navigation"` to the existing `<div class="toc-mobile">`.
5. Add `scroll-margin-top` to chapter and task anchors matching the sticky TOC/ header height. The current `.chapter{scroll-margin-top:20px}` is too small if a sticky element overlaps; measure at 1440 and 768.
6. Add a build check for duplicate IDs and broken `href="#…"` targets.
7. Run a keyboard pass: Tab from the top should reveal the skip link first; Enter should move focus to the main content; then the TOC links should be reachable.

**Acceptance criteria.**
- Zero duplicate IDs.
- The skip link is the first focusable element in the body.
- `<main>` receives focus after activating the skip link.
- Every `href="#…"` resolves to exactly one ID.
- The mobile TOC has a navigation landmark.
- No horizontal scroll at 390 px.

#### The 3 substeps

1. **Fix the anchor generator and add the uniqueness check.**
2. **Move the skip link and add focus management.**
3. **Run the keyboard and anchor audit** at 1440/768/390 and in print.

#### Subtask 9.1 — Fix anchors

1. Change the `anchor` expression in `build/taskbase.py:20`.
2. Add `assert_unique_ids(doc)` to `build/build.py`; fail with the duplicate list.
3. Regenerate and confirm the four collisions are gone.

#### Subtask 9.2 — Fix the skip link and landmarks

1. Move the skip link before `<header>`; add `tabindex="-1"` to `<main>`.
2. Wrap the mobile TOC in `<nav>`; keep the desktop TOC as `<nav>`.
3. Add `scroll-margin-top` tokens for `header` height and test anchor jumps.

#### Subtask 9.3 — Audit keyboard and anchors

1. Use Chrome with keyboard only: Tab, Enter, Shift+Tab; record the focus order.
2. Run a script that parses all `href="#…"` and checks the target count.
3. Check the visible focus ring on the skip link against the ground (≥ 3:1).

**Suggested features.**
- **“Atgriezties sākumā”** link at the end of each chapter, not only in the footer.
- **Accessible “current section”** announcement: `aria-current="location"` instead of `"true"`; test with a screen reader if available.

**Verification commands.**

```bash
python3 build/build.py
python3 - <<'PY'
import re
from collections import Counter
s=open('Master_3_tema_skidumi_un_koncentracijas.html',encoding='utf-8').read()
ids=re.findall(r'\bid="([^"]+)"',s)
print([k for k,v in Counter(ids).items() if v>1])
for m in re.finditer(r'href="#([^"]+)"',s):
    assert s.count(f'id="{m.group(1)}"')==1, m.group(1)
PY
```

**Risk / rollback.** Low. Changing IDs could break an external bookmark, but this is a single local file with no external links. The skip-link move is HTML-only.

---

### T10 — Fix list numbering and composition completeness (O1–O5, P12, Rehydron)

**Priority:** P1 · **Effort:** S–M · **Depends on:** T06 · **Evidence:** E09, E15, E16

**Why this matters.** Two different problems share a root: the document sometimes shows a list of things without accounting for all of them. The O1–O5 list is double-numbered, which looks careless; the P12 composition table computes two of three components, which is a completeness error. Both teach the student that the visible set is the whole set when it is not.

**What is wrong now.**

1. `build/ch01_04.html:6–12`:
   ```html
   <ol class="steps">
     <li><strong>O1. Atkārtot …</strong> …</li>
     …
   </ol>
   ```
   Renders as “1. O1.”, “2. O2.”, etc.
2. Chapter 12 P12: the powder is `100 mg acetylcysteine + 2.8 g sucrose + 100 mg ascorbic acid = 3.000 g`. The task computes `w(acetylcysteine)=3.33 %` and `w(sucrose)=93.33 %` but never states that the remaining `3.33 %` is ascorbic acid. The table is therefore not a complete composition.
3. Rehydron uses `C6H5Na3O7` (anhydrous citrate). The table gives `c(citrate)=11.2 mmol/L` and `Na⁺=93.6`, which are consistent with M=258.07. If a reader uses the dihydrate (M=294.10), the numbers change. The assumption is not stated.
4. The K18 sum (`1018.9 g`) is correct only with all four solutes; the document explains this, but the Rehydron table should have a Σ row so the reader can see the accounting.

**What to change.**

1. For O1–O5, choose one of:
   - **Option A (recommended):** remove the manual `O1.`–`O5.` prefixes and keep the `<ol>` numbering. Add `id="o1"` etc. to the `<li>` for cross-references.
   - **Option B:** keep the `O1.` IDs and change `<ol>` to `<ul>` with `list-style:none`. This preserves the outcome IDs but removes the double numbering.
   Do not keep both numbering systems.
2. Add an **ascorbic acid row** to P12:
   > `w(askorbīnskābe) = 100/3000 · 100 = 3.333 %`
   and a Σ line: `3.333 + 93.333 + 3.333 = 99.999 ≈ 100 %` (rounding).
3. Add a note to the Rehydron table:
   > “Avots dod nātrija citrātu kā `C6H5Na3O7` (bezūdens, M = 258,07 g/mol). Ja lieto dihidrātu `C6H5Na3O7·2H2O` (M = 294,10), citrāta moli un Na⁺ summa mainās; eksāmenā lietojiet avota formulu.”
4. Add a **Σ row** to the Rehydron table: `Σ m = 1018,9 g`, `Σ w = 1,85 %` (solutes) + `98,15 %` water.
5. Add a build check for composition tables: each table with a “Sastāvdaļa” column must have a Σ row or a sentence explaining why not.

**Acceptance criteria.**
- O1–O5 are not double-numbered; outcome IDs remain linkable.
- P12 has three component w values and a Σ line.
- Rehydron states the citrate formula and hydrate assumption.
- The Rehydron table has a Σ row.
- The build does not introduce a new table-numbering gap.

#### The 3 substeps

1. **Fix the list semantics** and add `id`s.
2. **Complete the P12 and Rehydron compositions** with the missing component, the hydrate note, and the Σ row.
3. **Add the composition check** and inspect the rendered tables at 390 px.

#### Subtask 10.1 — Fix O1–O5

1. Remove the `O1.`–`O5.` prefixes from the `<strong>` text; keep the outcome concepts.
2. Add `id="o1"` … `id="o5"` to the `<li>` elements.
3. Update any cross-reference that says “O1” to link to `#o1`.

#### Subtask 10.2 — Complete P12 and Rehydron

1. Add the ascorbic acid calculation and Σ line to the P12 task.
2. Add the citrate formula/hydrate note and the Σ row to the Rehydron table.
3. Check that the K18 note still says `1018.9 g` with all four solutes and `1016.4 g` without KCl.

#### Subtask 10.3 — Add the composition gate

1. Write a small checker that finds tables with a “Sastāvdaļa” header and requires a “Σ” row or a `data-no-sum` attribute with a reason.
2. Run it on the document; fix any table it flags.
3. Read the P12 and Rehydron tables at 390 px; use the responsive table strategy from T14 if the Σ row makes them wider.

**Suggested features.**
- **Composition calculator:** a small table where the student enters masses and sees `w` and `Σw`; no storage, no advice.
- **“Missing component” trap card:** a reusable “Biežākā kļūda” block for any composition task: “Ja summa nav 100 %, pārbaudiet, vai kāda sastāvdaļa nav izlaista.”

**Verification commands.**

```bash
grep -n 'O1\.' build/ch01_04.html
grep -n 'askorbīn' build/ch09_12.html
grep -n 'C6H5Na3O7' build/ch09_12.html
python3 build/build.py
```

**Risk / rollback.** Low. If the O-list is used elsewhere by ID, adding `id="o1"` preserves the link. The P12 addition is a content improvement; keep the original two-value answer and add the third as a separate line so a student who only needs two is not confused.

---

## 4. Design and restyle tasks (T11–T15)

The current design is already restrained: no gradients (0), no box shadows (0), one accent hue, embedded fonts, and a data-driven tone ladder. The problem is not “AI slop” in the obvious sense. The problem is **contract drift**: a few familiar editorial shortcuts (serif hero, right-hand link rail, filled blue answer cards, underlined inline labels) have crept in and now compete with the quieter system. The five tasks below remove that drift without flattening the document into a generic study guide.

---

### T11 — Replace the masthead hero + link rail with a compact document header

**Priority:** P1 · **Effort:** S–M · **Depends on:** T09 · **Evidence:** E18, E21

**Why this matters.** The masthead is the first 440 px of the reading experience on desktop and roughly 600 px on a 390 px phone. It currently uses a two-column hero: a large serif title on the left and a “Saīsnes” rail on the right with five links. Those five links duplicate five of the sixteen TOC entries, and the rail has no active state. The result is a landing-page gesture at the top of a reference document: it delays the first chapter and implies that the five links are the important ones when the TOC already exists.

**What is wrong now.**

- `build/head.html:85`:
  ```css
  .masthead-in{…display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:56px;align-items:end}
  ```
- `build/head.html:86`: `font-size:clamp(2.1rem,4.4vw,3.35rem)` and a 24ch max-width; the title is a poster headline.
- The right rail contains `Lielumu karte`, `Atšķaidīšana`, `Biežākās kļūdas`, `Paškontrole`, `Izmaiņu žurnāls` — five of sixteen chapters.
- At 390 px, the header stacks and the nav becomes a single column (`@media max-width:760`), which is why the first chapter starts near the bottom of the first screen.
- The TOC immediately below repeats all sixteen entries, so the rail is redundant.

**What to change.**

1. Remove the two-column grid; make the masthead a single reading column:
   ```css
   .masthead-in{max-width:1320px;margin:0 auto;padding:38px 28px 28px;display:block}
   .masthead h1{font-size:clamp(1.8rem,3.2vw,2.6rem);max-width:22ch}
   ```
2. Remove the `masthead-nav` from the header. Move the five shortcuts into the TOC as a top group labelled “Īsie ceļi” (not “Saīsnes”), above the numbered list. This keeps the shortcuts but stops them from competing with the title.
3. Add one primary action under the deck:
   ```html
   <p class="masthead-start"><a href="#n1">Sākt ar 1. nodaļu</a></p>
   ```
   Keep it a text link, not a pill button.
4. On mobile, reduce the header to title + deck + meta + one link; target ≤ 320 px total height at 390 px. Measure with Chrome device emulation.
5. Keep the metadata (university, department, course, “mācību materiāls, nevis klīniskā vadlīnija”) visible; it is important for provenance.
6. Keep the header background as `tone-1`; do not introduce a gradient or a decorative rule.

**Acceptance criteria.**
- The first chapter heading is visible within the first viewport at 768 and 390 px (or within 1.2 viewports at 390, if the deck is long).
- The header has no right-hand link column.
- The TOC contains the five shortcuts in a “Īsie ceļi” group and all sixteen numbered chapters.
- No duplicate `nav` landmarks with the same accessible name.
- The header still contains the title, deck, institution, course, and disclaimer.

#### The 3 substeps

1. **Measure the current header** at 1440/768/390 and record the y-position of the first chapter.
2. **Replace the layout** with the compact header and move the shortcuts into the TOC.
3. **Re-measure and inspect** at all three widths, light and dark, and in print.

#### Subtask 11.1 — Measure and wireframe

1. Take screenshots of the top at 1440/768/390; record the first chapter’s y-position and the header height.
2. Sketch two options: (a) title + deck + meta + one link; (b) title + deck + a horizontal “Īsie ceļi” row. Choose the one that keeps the first chapter visible earliest.
3. Write the chosen measurements into a short `build/design-header.md` note.

#### Subtask 11.2 — Implement the compact header

1. Change `.masthead-in` to a single column and reduce the h1 clamp.
2. Remove `.masthead-nav` from `build/head.html`; add the “Īsie ceļi” group to the TOC.
3. Add the “Sākt ar 1. nodaļu” link and keep the metadata.

#### Subtask 11.3 — Re-measure and inspect

1. Screenshot at 1440/768/390 in light and dark; check the first chapter position.
2. Check print page 1: the header should not consume a whole page.
3. Check that the TOC’s “Īsie ceļi” links still resolve and that the active-section marker does not treat them as chapters.

**Suggested features.**
- **“Kur esmu” line** under the header: “1. nodaļa no 16 · ~106 lpp. drukā” — a plain orientation aid, not a progress bar.
- **Print cover:** a compact title block on page 1 with the same metadata, no hero.

**Verification commands.** Use Chrome headless at three widths; compare the first chapter’s `getBoundingClientRect().top`.

**Risk / rollback.** Low. The header is independent of content. If the compact header feels too plain, add the shortcuts back as a single horizontal line, not a right rail.

---

### T12 — Reconcile the typography with the contract: one heading family, one measured reading column

**Priority:** P1 · **Effort:** M · **Depends on:** T11 · **Evidence:** E12

**Why this matters.** The document uses Noto Serif for `h1`/`h2` and Noto Sans for `h3`/`h4`. That is not just a style choice; it makes the hierarchy inconsistent: a chapter title and a section title look like they belong to different documents. The prompt’s type contract says at most two families, headings in the same family, body 17–19 px, measure 60–68ch. The current `--measure:66ch` is correct in principle, but the family split and the 3.35rem hero headline work against it.

**What is wrong now.**

- `build/head.html:86`: `.masthead h1{font-family:var(--serif); … font-size:clamp(2.1rem,4.4vw,3.35rem)}`
- `build/head.html:108`: `h2{font-family:var(--serif); … font-size:clamp(1.65rem,2.5vw,2.15rem)}`
- `build/head.html:110`: `h3{font-family:var(--sans); … font-size:1.14rem}`
- `build/head.html:111`: `h4{font-family:var(--sans); … font-size:.98rem}`
- The `--serif` font is only used for h1/h2, so it is not carrying a second semantic role; it is a decorative split.
- At 768 px the body remains 18 px and the measure is 66ch; that is acceptable, but the heading scale is still hero-sized.
- Tables already use `font-variant-numeric: tabular-nums lining-nums`; inline calculations do not.

**What to change.** Choose one of two coherent systems:

**Option A (recommended): one family, sans.**
- Remove `--serif` from headings; use Noto Sans 600 for h1/h2/h3/h4.
- Keep Noto Serif only if it is used for a genuinely different role (e.g., a pull quote), otherwise remove the `@font-face` and the 20 KB.
- H1: `clamp(1.8rem,3.2vw,2.6rem)`; h2: `clamp(1.5rem,2.2vw,1.9rem)`; h3: 1.12rem; h4: 0.98rem.
- This gives a calm, technical hierarchy and matches the body.

**Option B: two families, but a real role split.**
- Use Noto Serif for all headings h1–h4 and Noto Sans for body; then the serif is a heading role, not a hero gimmick. But this is heavier and less “quiet exact” than the document’s stated direction.
- If you choose B, document the exception in the CSS comment and verify that h3 serif at 1.14rem is legible with subscripts.

Whichever option:
1. Set the measure to 64–66ch and keep it for all body text; do not remove `max-width` at 1080 px.
2. Set body to 18 px at ≥ 1080, 17 px at 760–1080, 17 px at ≤ 760; line-height 1.6.
3. Add `font-variant-numeric: tabular-nums lining-nums` to `.route dd`, `.formula`, and any inline calculation, not only tables.
4. Ensure `sub`/`sup` do not increase line height: `sub,sup{line-height:0;position:relative;vertical-align:baseline}` is already present; test a paragraph with `H₂SO₄` and a fraction.
5. Remove any single italicised emphasis word in headings; check `em` usage inside headings.
6. Add a small type specimen in `build/design-type.md` with the chosen scale, measure, and diacritics test string `āčēģīķļņšūž ĀČĒĢĪĶĻŅŠŪŽ`.

**Acceptance criteria.**
- All headings use one family (or a documented two-family role split with all headings in one family).
- The body measure is 60–68ch at 1440; no line is longer than ~75ch at 768.
- Calculations use tabular figures.
- A paragraph with `H₂SO₄`, `PO₄³⁻`, and `10⁻⁵` has the same line height as plain text.
- The CSS comment explains the accent and type choices; no gradient/shadow is introduced.

#### The 3 substeps

1. **Choose the system** and write the scale/measure into a design note.
2. **Implement the tokens and heading styles**; remove the unused font if Option A.
3. **Measure and inspect** at 1440/768/390, light/dark, and print; check subscripts and diacritics.

#### Subtask 12.1 — Choose and document

1. Compare Option A and B on a one-chapter specimen at 1440 and 390.
2. Choose based on legibility, not taste; record the reason in `build/design-type.md`.
3. Define the tokens: `--h1`, `--h2`, `--h3`, `--measure`, `--body-size`.

#### Subtask 12.2 — Implement

1. Replace the `font-family` declarations for h1–h4.
2. Adjust the clamp sizes and line-heights; keep `text-wrap:balance`.
3. Add tabular figures to route/formula text; test sub/sup.

#### Subtask 12.3 — Measure and inspect

1. Use Chrome to measure the rendered line length in `ch05` and `ch06` at 1440/768/390.
2. Check the diacritics and the math glyphs in the embedded font subset.
3. Check print sizes: body 10.4pt is currently used; confirm it remains legible after the heading change.

**Suggested features.**
- **Type scale in the appendix:** a one-page “Kā lasīt formulas” specimen with the body size, table size, and formula size.
- **“Drukas versija” switch:** a print-only class that increases leading for A4, not a screen toggle.

**Verification commands.** Screenshot and measure; no grep can prove typography.

**Risk / rollback.** Medium. Removing the serif changes the document’s character; keep the serif face until the sans version is reviewed at 1440 and 390. If the sans h1 feels too plain, use weight and spacing, not a second family.

---

### T13 — Consolidate the callout system: three roles, one neutral family, fewer filled surfaces

**Priority:** P1 · **Effort:** M · **Depends on:** T05 · **Evidence:** E08, E11

**Why this matters.** The document has 68 blue “Pārbaudīts” blocks, 25 darker “Biežākā kļūda” blocks, 9 “Noteikums” blocks, and a tail of one-off labels. Each block is a filled surface with a thick left rule. At 1440 px, a chapter can show three or four of these in a row, and the page starts to read as a stack of cards rather than a continuous explanation. The contract allows at most two callouts visible per screen height and only three semantic roles. The current system exceeds both.

**What is wrong now.**

- `.role` uses `background:var(--tone-1)` and `border-left:8px` (`build/head.html:128`).
- `.role-verified` uses `tone-2`; `.role-mistake` uses `tone-3` and a 12px ink rule.
- 68 answer blocks + 25 mistake blocks = 93 filled surfaces, plus 9 rule blocks.
- “Pārbaudi sevi” is inside the verified tone (14×).
- One-off labels (“Saprāta pārbaude”, “Kā skaitīt”, “Drošība”, “Dokumenta robeža”) use the same role surface, so the visual grammar no longer means “rule / mistake / verified”.
- The “Papildinājums” block has a duplicate inline label.

**What to change.**

1. Adopt the five-item language from T05 and map it to **three visual weights**, not five new hues:
   - **Rule** — tone-1 surface + accent rule; label bold.
   - **Mistake** — tone-3 surface + ink rule; label bold.
   - **Answer** — no filled surface; a 1px top/bottom hairline or a tone-1 label strip, with the result in body text. This reduces the blue mass while keeping the answer scannable.
   - **Source note** — no fill; a neutral 2px left rule and a small label.
   - **Practice** — no fill; use `.recall` items, not a role block.
2. Reduce `.role` padding from 17/22 to 12/16 and the rule from 8px to 4–6px; the current 12px ink rule on mistakes is visually louder than the content.
3. Remove the duplicate inline `papildinājums`; the label alone is enough.
4. Add a **legend** in chapter 1 with one example of each of the five items. The legend must use the same CSS, not a separate swatch.
5. Enforce “max two callouts per screen height” by content editing, not CSS: move some answers into the task’s `Aprēķins`/`Pārbaude` flow and keep only the final answer in a compact line.
6. Check nesting: no `<details>` inside a role block except the intended recall items; no role block inside another role block.

**Acceptance criteria.**
- Three semantic surfaces, one neutral source note, one practice pattern; no one-off role colours.
- The page has fewer filled blue rectangles; answers remain findable by their label.
- The legend exists and matches the actual classes.
- No “Papildinājums papildinājums”.
- Print keeps the labels but drops the fills where they do not carry data.

#### The 3 substeps

1. **Map the current blocks to the five-item language** and count how many surfaces would disappear.
2. **Restyle the CSS and migrate the wrappers**; keep the labels, reduce the fills.
3. **Inspect a dense chapter (6, 7, 11, 12)** at 1440/768/390 and in print; check that the answers are still scannable.

#### Subtask 13.1 — Map and count

1. Count blocks by class and label in the rendered HTML.
2. Mark which blocks are truly “answer”, “rule”, “mistake”, “source”, or “practice”.
3. Estimate the reduction in filled surfaces per chapter; if a chapter still has > 3 visible, plan a content edit.

#### Subtask 13.2 — Restyle and migrate

1. Change `.role` padding/rule widths and `.role-verified` to the compact answer treatment.
2. Move “Pārbaudi sevi” to `.recall-block`; remove duplicate labels.
3. Add the legend in chapter 1 and a `data-role` attribute for counting.

#### Subtask 13.3 — Inspect and tune

1. Screenshot chapters 6, 7, 11, 12 at 1440/768/390.
2. Check the print PDF: the answer blocks should not create huge blank areas or split awkwardly.
3. Verify the contrast of the new answer label and the neutral source note (≥ 4.5:1 for body, ≥ 3:1 for large).

**Suggested features.**
- **Role filter** (from T05): show only “Biežākā kļūda” for exam revision.
- **“Answer only” print mode:** a print stylesheet that hides the `Kāpēc šādi` prose and keeps the answer + check; optional, not default.

**Verification commands.** Screenshot and count; use the browser inspector to measure the number of `.role` blocks in a viewport.

**Risk / rollback.** Medium. Reducing the answer fill may make answers harder to find; keep a strong label and a thin rule. If the page feels too flat, add a tone-1 label strip, not a full card.

---

### T14 — Fix the figure/table plate system and make wide tables usable at 390 px

**Priority:** P1 · **Effort:** M · **Depends on:** T08 · **Evidence:** E13, E24

**Why this matters.** The data figures and tables are where the document’s “exact” claim is tested. At 390 px, table 9 and table 10 are wider than the viewport; the right-hand “Piezīme” and “Kas aprēķināts” columns are cut off, and there is no visible scroll affordance. A student on a phone sees a truncated table and may not know it scrolls. The figures also use a tone ladder without a legend, so the colour depth is decorative rather than explained.

**What is wrong now.**

- `build/head.html:215`: `.table-wrap{overflow-x:auto}` — correct, but no affordance.
- At 390 px, `table{font-size:.87rem}` and `th,td{padding:8px 8px}`; table 9 has 5 columns, table 10 has 5; the screenshot shows the last column cut.
- `build/qa/w390-ch5.png` shows the cut; this is the evidence.
- Figure captions use `.fig-cap` + `.fig-kind`; the tone ladder is used in some figures but not explained.
- The data figures say “attēls veidots no datiem”; the schematic says “shēma”. Good, but the `fig-kind` is not consistently styled.

**What to change.**

1. **Table strategy at ≤ 600 px.** Choose one:
   - **Option A (recommended):** stacked definition rows for tables with ≥ 4 columns. Each row becomes a `<tbody>` group with a `<th scope="row">` and a list of label/value pairs; the `<thead>` is visually hidden. This is real responsive HTML, not a CSS trick.
   - **Option B:** keep the table but add a visible “← ritiniet →” affordance and a `tabindex="0"` on `.table-wrap` so keyboard users can scroll. This is cheaper but less readable.
   Use Option A for tables 9, 10, 11, 18, 19, 23; use B for the compact error tables 12–17 if stacking would be too long.
2. Add a **table caption pattern**:
   `9. tabula. Kā lasīt etiķetes procentus · papildinājums`
   The provenance is a separate `<span class="prov">`, not an underlined inline word. Keep it in the caption, not in the first body sentence.
3. Add a **tone legend** to the data figures: “Tumšāks tonis = lielāka koncentrācija; katrs solis ir 1 : 2 : 4 : 8.” Use the same five tone steps as the tables. Do not use a gradient.
4. Set a minimum SVG text size of 11 px at the rendered width; at 390 px, either scale the figure to a readable minimum and allow horizontal scroll inside the figure, or provide a `<details>` “Palielināt” with the full-width SVG.
5. Add `aria-describedby` on complex tables linking to the caption + a one-sentence summary; do not rely on the caption alone.
6. Add a **figure/table index** in the appendix (T08) with links.

**Acceptance criteria.**
- At 390 px, tables 9/10 show all values without horizontal scrolling, or have a visible, keyboard-accessible scroll affordance.
- Figure labels are ≥ 11 px at 390 px.
- Every data figure has a tone legend or a sentence explaining the tone.
- Captions use a consistent `· papildinājums` separator, not an underlined inline label.
- No table loses its header association when stacked.

#### The 3 substeps

1. **Choose the responsive table strategy per table** and prototype table 9 at 390 px.
2. **Implement the stacked rows / scroll affordance and the caption pattern.**
3. **Audit all 25 tables and 9 figures** at 390 px; check print and dark mode.

#### Subtask 14.1 — Prototype table 9

1. Build a stacked-row version of table 9 in a scratch HTML file at 390 px.
2. Compare readability with the current horizontal-scroll version.
3. Choose the strategy and document it in `build/design-tables.md`.

#### Subtask 14.2 — Implement across the table set

1. Apply the chosen pattern to tables 9, 10, 11, 18, 19, 23; use the scroll affordance for the compact error tables.
2. Add the caption separator and the `prov` span.
3. Add `tabindex="0"` and `aria-label` to any scroll container.

#### Subtask 14.3 — Audit figures and print

1. Add the tone legend to `quantity_map`, `dilution_ladder`, `mixing`, `neutralisation`.
2. Check SVG label sizes at 390 px; add `<details>` zoom if needed.
3. Check the print PDF: no table splits mid-row; captions stay with figures.

**Suggested features.**
- **Table card mode:** a `<details>` per row on mobile, so the student can open one row at a time; no JS.
- **“Copy table as text”** is not possible without JS; skip it.

**Verification commands.** Screenshot table 9/10 at 390; check `document.querySelector('.table-wrap').scrollWidth` vs `clientWidth`.

**Risk / rollback.** Medium. Stacked tables change the DOM and can break the print layout; keep the original table as a `<table>` with CSS-only stacking if possible. If the DOM change is too large, use Option B (scroll affordance) and revisit.

---

### T15 — Fix inline provenance, caption metadata, and the reading navigation

**Priority:** P1 · **Effort:** S–M · **Depends on:** T13, T14 · **Evidence:** E14, E19

**Why this matters.** The provenance system is one of the document’s best ideas: every claim is marked “avotā”, “papildinājums” or “ilustratīvs piemērs”. But the inline rendering undermines it. `papildinājums` is underlined like a link, sits directly before a sentence, and in captions appears as an afterthought in parentheses. The reader cannot tell whether it is a label, a link, or a typo. The same pass should fix the print navigation: 106 pages without a chapter running head is hard to use.

**What is wrong now.**

- `build/head.html:122`: `.prov{font-weight:600;font-size:.86em;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:3px;white-space:nowrap}`
- `build/ch05_08.html:48`: `<p><span class="prov p-add">papildinājums</span> Šie veidi …`
- `build/ch13_14.html:207`: same pattern.
- `build/ch05_08.html:36`: `<caption>… (visas rindas — <span class="prov p-add">papildinājums</span>)</caption>`
- The print stylesheet has `@top-left`, `@top-right`, `@bottom-right` margin boxes (`build/head.html:308–310`), but Chrome’s support for margin boxes is inconsistent; the PDF sample should be checked, not assumed.
- The print edition has no running chapter title, only the document title and “MCh · 3. tēma”.

**What to change.**

1. Replace the underlined inline label with a **neutral metadata tag**:
   ```css
   .prov{font-weight:600;font-size:.82em;text-decoration:none;white-space:nowrap}
   .prov::after{content:" ·";font-weight:400;color:var(--ink-muted)}
   ```
   or use a sentence label: `<span class="prov">Papildinājums.</span>` with a normal space. Do not use a pill or a badge.
2. In captions, use a middle dot separator: `9. tabula. … · papildinājums`. Do not wrap it in parentheses.
3. In body paragraphs, start with a capitalised label and a full stop/colon: “Papildinājums. Šie veidi …” or “Papildinājums: šie veidi …”. This is prose, not a tag.
4. Add a **print running head** with the current chapter. Since CSS margin boxes are unreliable in Chrome, use a print-only `position: fixed` header or a `@page` named page with `string-set` if supported; test the exported PDF. If neither works, add a static “chapter label” at the top of each printed chapter and accept no running head.
5. Add a **back-to-top** link at the end of each chapter, not only in the footer.
6. Check the TOC active marker and the mobile TOC: after the masthead change (T11), the TOC is the primary navigation. Add `aria-current="location"` and a visible “current” marker that is not colour-only.
7. In print, hide the TOC and the skip link; keep the chapter headings and the figure/table captions.

**Acceptance criteria.**
- No inline `.prov` is underlined.
- Captions use `· papildinājums`, not `— (papildinājums)`.
- Body provenance labels are grammatical sentences, not glued tags.
- The print PDF has a usable running head or a clear chapter label on each page.
- The TOC active marker is visible in grayscale.

#### The 3 substeps

1. **Fix the inline/caption typography** and add a small “provenance legend” in chapter 1.
2. **Fix the print navigation** and export a new PDF.
3. **Inspect the PDF and the mobile TOC**; check page breaks, running heads, and active markers.

#### Subtask 15.1 — Inline and caption provenance

1. Change `.prov` to no underline and add a separator.
2. Rewrite the body paragraphs that start with `papildinājums` as “Papildinājums. …”.
3. Rewrite the captions to use `· papildinājums`.

#### Subtask 15.2 — Print navigation

1. Add a print-only chapter label or running head; test Chrome’s `@page` margin boxes.
2. Add a back-to-top link at the end of each chapter.
3. Check `details` opening and `break-inside` rules after the label change.

#### Subtask 15.3 — Inspect

1. Export the PDF and inspect 6 pages: first page, a chapter start, a table-heavy page, a figure page, the change log, the last page.
2. Check the mobile TOC at 390 px: open/close, active marker, scroll.
3. Check grayscale: the active marker and the provenance tag must still be distinguishable.

**Suggested features.**
- **Provenance filter:** “Rādīt tikai avotā / papildinājums” — useful for exam revision and for the lecturer’s review.
- **Print chapter index:** a one-page “Saturs” at the front of the PDF with page numbers, if the renderer supports it.

**Verification commands.**

```bash
grep -n 'text-decoration:underline' build/head.html
pdftotext build/qa/master-print.pdf - | head -40
pdfinfo build/qa/master-print.pdf | grep Pages
```

**Risk / rollback.** Low–medium. The inline label change is CSS + a few strings. The print running head is the risky part; test before committing. If Chrome ignores margin boxes, use a static chapter label and document the limitation.

---

## 5. Explanation and learnability tasks (T16–T20)

The document’s explanations are already strong: every task has `Dots`, `Meklējams`, `Maršruts`, `Aprēķins`, `Atbilde`, `Pārbaude`, `Kāpēc šādi`. The next gains are in **decision-making under exam conditions**: when to use which percent, when additivity is safe, how to identify the limiting reagent, how many digits to print, and how to retrieve without rereading.

---

### T16 — Add a percent-kind decision tree and five label-reading drills

**Priority:** P1 · **Effort:** M · **Depends on:** T02, T03 · **Evidence:** E06, K23

**Why this matters.** “%” is the most dangerous symbol in the topic because it hides its denominator. The document says this, and table 9 lists the likely kinds, but it does not give the student a procedure for an unseen label. In an exam, the student sees “0,9 % NaCl” or “70 % etanols” and must decide: m/m, m/V, or V/V? The current table gives the answer for five known products; it does not teach the decision.

**What is wrong now.**

- Chapter 5 table 9 lists five products and their likely kinds, but the reasoning is compressed into a “Piezīme” column.
- The document correctly avoids inventing a kind for 3 % H₂O₂ and 5 % iodine, but it does not show the two possible calculations side by side.
- There is no “if the label says nothing” procedure beyond “jautājiet docentam”.
- The `w(V)` error in chapter 14 (T02) shows how easily the denominator can slip.

**What to change.**

1. Add a **three-question decision tree** before table 9:

```
1. Vai procenta pamatā ir masa vai tilpums?
   - masa / masa → w (m/m)
   - masa / tilpums → γ (m/V), expressed as g/100 mL
   - tilpums / tilpums → φ (V/V)

2. Vai ir dots blīvums ρ?
   - jā → pārrēķiniet starp m/m un m/V
   - nē → pieņemiet ρ ≈ 1 g/mL tikai tad, ja šķīdums ir atšķaidīts, un pierakstiet pieņēmumu

3. Vai etiķetē ir norādīts veids?
   - jā → lietojiet to
   - nē → pierakstiet visticamāko veidu un pajautājiet docētājam (K23)
```

2. Add five worked rows, each with “ja m/m” and “ja m/V” columns where relevant:
   - 0,9 % NaCl → m/V → 9,0 g/L → 154 mmol/L NaCl (308 mmol/L particles).
   - 5 % glikoze → m/V → 50 g/L → 277,5 mmol/L.
   - 3 % H₂O₂ → m/V → 30 g/L → 0,882 mol/L; if m/m with ρ ≈ 1,0, numerically similar but not identical.
   - 70 % etanols → V/V → 700 mL/L; convert to mass fraction requires ρ(ethanol) and ρ(solution); do not pretend it is w.
   - 5 % joda šķīdums spirtā → likely m/V; the source does not state it; mark V.
3. Add a “what to write in the exam” line:
   > “Ja veids nav norādīts: pierakstiet ‘pieņemu m/V, jo …’ un turpiniet. Nepareizs pieņēmums ar skaidru pamatojumu ir labāks par klusu pieņēmumu.”
4. Add a “common trap” block: “0,9 % NaCl nav 0,9 g/L” with the two-line calculation.
5. Keep the medical disclaimer: this is didactic arithmetic, not dosing advice.

**Acceptance criteria.**
- The decision tree has exactly three questions and no more than three outcomes per question.
- Five products have a worked row with the kind, the conversion, and the assumption.
- 3 % H₂O₂ and 5 % iodine are marked as unconfirmed (V), not asserted.
- The phrase “0,9 % NaCl nav 0,9 g/L” appears with the correct calculation.
- No reference range or dosing advice is added.

#### The 3 substeps

1. **Write the decision tree and the five rows** in a scratch table; check every number with `build/calc.py`.
2. **Insert the tree and rows into chapter 5**, before table 9; update the table to refer to the tree.
3. **Add a recall prompt and a wrong-answer example**; verify at 390 px and in print.

#### Subtask 16.1 — Draft and recompute

1. Write the three questions and the five rows in `build/scratch/percent-tree.md`.
2. Recompute 0.9 % NaCl, 5 % glucose, 3 % H₂O₂, 70 % ethanol, 5 % iodine with the correct assumptions.
3. Mark each row `avotā`, `papildinājums`, or `V`.

#### Subtask 16.2 — Insert and cross-link

1. Insert the tree before table 9; add a caption “Kā izvēlēties procenta veidu”.
2. Add a link from table 9’s “Piezīme” column to the relevant row.
3. Add a recall prompt: “Kāds ir 0,9 % NaCl γ, ja tas ir m/V?” Answer: 9.0 g/L.

#### Subtask 16.3 — Add the trap and verify

1. Add a “Biežākā kļūda” block with the 0.9 g/L error.
2. Check the worked rows at 390 px; use the stacked table strategy if needed.
3. Check that no row implies a clinical dose or a normal range.

**Suggested features.**
- **Label reader:** a small instrument with a text input “0,9 % NaCl” and radio buttons `m/m`, `m/V`, `V/V`; output the conversion and the assumption. Use the test vectors from chapter 5.
- **“What kind is this?” flashcard set:** 10 labels, answer + reason, in the recall block.

**Verification commands.**

```bash
python3 build/calc.py
grep -n '0,9 % NaCl nav 0,9 g/L' Master_3_tema_skidumi_un_koncentracijas.html
```

**Risk / rollback.** Medium. The 70 % ethanol conversion requires densities the source does not give; keep it qualitative and mark it V. Do not add a numeric mass fraction for ethanol unless you state the density assumption.

---

### T17 — Explain dilution without pretending volumes are additive

**Priority:** P1 · **Effort:** M · **Depends on:** T16 · **Evidence:** K17

**Why this matters.** The document correctly says `V(ūdens) = V₂ − V₁` only under additivity, and it includes a note. But the note is easy to skip, and the worked tasks still present `435 mL` water as if it were exact. A student who later measures 448 mL in a volumetric flask may think the formula is wrong. The explanation should distinguish **the invariant** (`n` constant, `c₁V₁ = c₂V₂` when `V₂` is the final measured volume) from **the approximation** (`V₂ ≈ V₁ + V_water`).

**What is wrong now.**

- Chapter 10 has a “Piezīme avotam” about additivity, but the `Aprēķins` lines still read as exact.
- The figure “Atšķaidīšanas kāpnes” shows equal amounts in growing volumes, which is correct, but it does not show the volume-contraction caveat.
- The `V(ūdens) = V₂ − V₁` formula is presented without a “only if” next to it in the formula sheet.
- Some tasks (P3, P4, P5, P7) assume additive volumes silently; K17 flags this.

**What to change.**

1. Add a **two-level explanation** in chapter 10:
   - **Invariant:** the amount of solute does not change; `n₁ = n₂`; therefore `c₁V₁ = c₂V₂` if `V₂` is the final solution volume.
   - **Approximation:** the final volume is not exactly the sum of the volumes; `V₂ ≈ V₁ + V_water`. In a volumetric flask, you add solvent to the mark, so you measure `V₂`, not `V_water`.
2. Add a **quantitative counterexample**:
   > “15,0 mL 3,0 mol/L H₂SO₄ + 435 mL water may give 448–452 mL, not exactly 450,0 mL. The moles are still 0,0450 mol; if the final volume is 450,0 mL, c₂ = 0,100 mol/L. If it is 449,0 mL, c₂ = 0,1002 mol/L.”
3. Add a **decision line** to every dilution task: “Pieņemts, ka tilpumi saskaitās; ja gatavojat mērkolbā, lietojiet atzīmi.”
4. Add a **volumetric flask procedure** (three steps, from the existing figure): weigh/transfer, dissolve in ~2/3 volume, fill to the mark and mix. Explain that the mark defines `V₂`.
5. Update the formula sheet: `V(ūdens) = V₂ − V₁` with a superscript “tikai ar aditivitātes pieņēmumu”.
6. Add a “common trap”: using `c₁V₁ = c₂V₂` with `V₂ = V₁ + V_water` when the volumes do not add; the exam-safe method is to use the final volume.
7. Do not add a lab safety lecture; keep the existing “acid into water” note as a one-liner.

**Acceptance criteria.**
- The invariant and the approximation are stated separately.
- A numerical counterexample exists and is recomputed.
- Every dilution task that assumes additivity says so.
- The formula sheet has the caveat next to the formula, not only in prose.
- The volumetric flask figure caption explains that the mark defines `V₂`.

#### The 3 substeps

1. **Write the two-level explanation and the counterexample**; recompute the numbers.
2. **Propagate the caveat** to every dilution task and the formula sheet.
3. **Inspect the chapter and the figure** at 1440/390 and print; check that the caveat does not overwhelm the main method.

#### Subtask 17.1 — Draft and recompute

1. Write the invariant/approximation text in `build/scratch/dilution.md`.
2. Compute the 449/450/451 mL examples with `build/calc.py`.
3. Decide the exact wording for “exam-safe”: “ja nav mērkolbas, pieņemiet aditivitāti un pierakstiet to”.

#### Subtask 17.2 — Propagate the caveat

1. Add a one-line `Pieņēmums` to the `Dots` or `Maršruts` of the dilution tasks that assume additivity.
2. Update the formula sheet row.
3. Update the figure caption and the “Kāpēc šādi” paragraph.

#### Subtask 17.3 — Inspect and test

1. Check the chapter at 390 px; the caveat should be a separate short paragraph, not a footnote.
2. Check the print page; the formula and the caveat should stay together.
3. Add a recall prompt: “Kas paliek nemainīgs atšķaidīšanā?” Answer: `n` (and mass of solute), not volume.

**Suggested features.**
- **Dilution calculator** with a required checkbox “Pieņemu tilpumu aditivitāti”; output `V₂` and `V_water`, with a caveat line.
- **“Flask vs beaker” comparison:** a two-column figure showing `V₂` measured vs `V_water` added.

**Verification commands.** Recompute and inspect; no grep can prove the pedagogy.

**Risk / rollback.** Low–medium. The caveat may make the tasks feel wordier; keep it to one line per task and one full explanation in chapter 10.

---

### T18 — Turn neutralisation into a repeatable algorithm, not a set of worked examples

**Priority:** P1 · **Effort:** M · **Depends on:** T17 · **Evidence:** K9, C21–C27

**Why this matters.** Neutralisation is where the document’s source defect K9 (the reversed 1:2 ratio) is most dangerous. The worked examples are correct, but a student who memorises “acid = 2 × base” from the source will fail. The document needs a procedure that works for HCl, H₂SO₄, H₃PO₄, NaOH, KOH, and a limiting-reagent case, and it needs a before/after mole table so the student can see why the coefficient matters.

**What is wrong now.**

- The chapter explains equivalence and the 1:1/1:2 ratios, and it includes correct worked examples.
- The “Biežākā kļūda” block shows the reversed ratio, but the algorithm is distributed across prose.
- The limiting-reagent task C23 is explained, but there is no general “divide by coefficient” table.
- The pH-7 caveat is present, but it is a note, not part of the decision procedure.

**What to change.**

1. Add a **five-line algorithm** at the start of chapter 11:

```
1. Uzrakstiet izlīdzināto vienādojumu.
2. Aprēķiniet n katram reaģentam: n = cV vai n = m/M.
3. Izrēķiniet n/koeficients katram reaģentam.
4. Mazākais n/koeficients ir ierobežojošais reaģents; no tā rēķina produktu.
5. Pārbaudiet lādiņu bilanci un masu; nepieņemiet, ka pH = 7.
```

2. Add a **coefficient table**:
   | Reakcija | Attiecība | Ko tas nozīmē |
   |---|---|---|
   | HCl + NaOH | 1:1 | `n(HCl)=n(NaOH)` |
   | H₂SO₄ + 2 NaOH | 1:2 | `n(H₂SO₄)=n(NaOH)/2` |
   | H₃PO₄ + 3 NaOH | 1:3 | `n(H₃PO₄)=n(NaOH)/3` |
   | 2 HCl + Ca(OH)₂ | 2:1 | `n(Ca(OH)₂)=n(HCl)/2` |
3. Add a **before/after mole table** for C21–C27:
   | Uzdevums | n(skābe) | n(bāze) | n/koef. | Ierobežojošais | Produkts |
4. Add a “wrong route” box for the two most common errors: reversed 1:2 and ignoring the limiting reagent.
5. Keep the “pH 7 only strong acid + strong base” note, but move it next to the algorithm, not only in a footnote.
6. Add a recall prompt: “Kāpēc n(H₂SO₄) = n(NaOH)/2, nevis 2n(NaOH)?” Answer: one H₂SO₄ supplies two H⁺; the acid is consumed half as fast.

**Acceptance criteria.**
- The five-line algorithm is visible before the first worked example.
- The coefficient table covers HCl, H₂SO₄, H₃PO₄, Ca(OH)₂.
- The before/after table has all C21–C27 rows.
- The wrong-route box shows both 1.96 g and 0.49 g.
- The pH caveat is next to the algorithm.

#### The 3 substeps

1. **Write the algorithm and coefficient table**; recompute all rows.
2. **Add the before/after table and wrong-route box**; connect to the existing tasks.
3. **Audit C21–C27** for consistency and inspect at 390 px/print.

#### Subtask 18.1 — Write the algorithm

1. Draft the five lines in `build/scratch/neutralisation.md`.
2. Build the coefficient table and check each ratio against the balanced equation.
3. Add the pH caveat as a one-sentence “Piezīme” under step 5.

#### Subtask 18.2 — Add the tables and wrong routes

1. Add the before/after table with C21–C27; use the existing values.
2. Add the wrong-route box: “1,96 g” vs “0,49 g” and “20 mL” vs “40,0 mL”.
3. Link each row to its task anchor (after T09 fixes the anchors).

#### Subtask 18.3 — Audit and inspect

1. Check every C21–C27 task uses the same algorithm and the same labels.
2. Check the table at 390 px; use the stacked strategy if needed.
3. Add a recall prompt for the reversed ratio.

**Suggested features.**
- **Neutralisation calculator** with acid/base select, any two of `n`, `cV`, `m`, output the limiting reagent and salt moles; test vectors from chapter 11.
- **Mole bar figure** (already exists) with a “before/after” label for the limiting reagent.

**Verification commands.** Recompute C21–C27 with `build/calc.py`; inspect the table.

**Risk / rollback.** Low. The algorithm is a summary of existing correct content; the main risk is making the chapter longer. Keep the algorithm to five lines and the tables compact.

---

### T19 — Make significant figures a procedure, not a footnote

**Priority:** P1 · **Effort:** M · **Depends on:** T06, T07 · **Evidence:** K15

**Why this matters.** The course instruction says “norādot atbilstošu mērvienību un zīmīgos ciparus”, but the keys are not uniform: Q24 prints `0,001 mol` where 10 mL has 2 s.f. → `0,0010 mol`; Q10 prints `60 mg/mL` where the trailing zero is ambiguous; Q9 prints `150 g` from 1 s.f. data. The document notes this, but it does not teach the student how to decide. In an exam, “how many digits?” is a recurring source of lost points.

**What is wrong now.**

- Chapter 1 says “zīmīgie cipari” but no procedure.
- Chapter 13 item 19 lists the symptoms but not a decision flow.
- The worked tasks sometimes print 3 s.f. and sometimes 2, without a visible rule.
- The build’s expected values include strings at different precisions (`0,0010`, `60 mg/mL`, `150 g`), which makes it hard to see the policy.

**What to change.**

1. Add a **five-step procedure**:
   ```
   1. Nosakiet neprecīzāko doto lielumu (mazāk zīmīgo ciparu).
   2. Skaitiet zīmīgos ciparus: visi cipari, izņemot sākuma nulles; iekšējās nulles skaitās; beigu nulles aiz komata skaitās.
   3. Aprēķiniet ar pilnu precizitāti; nenoapaļojiet starprezultātus.
   4. Noapaļojiet vienreiz beigās līdz neprecīzākā ievada zīmīgajiem cipariem.
   5. Pierakstiet mērvienību un, ja nepieciešams, zinātnisko pierakstu (6,0·10¹ mg/mL).
   ```
2. Add three annotated examples:
   - `C24`: 10,0 mL (3 s.f.) × 0,100 mol/L (3 s.f.) → `0,00100 mol`? Wait, 10.0 mL has 3 s.f.; 0.100 has 3; product = 0.00100 mol (3 s.f.). The document currently says 0.0010 mol (2 s.f.) because it treats 10 mL as 2 s.f. Clarify the data: if the task says “10 mL” (1 s.f.), the answer is 0.001 mol; if “10,0 mL”, it is 0.00100 mol. The document should show the distinction, not just assert one.
   - `C10`: 18 g (2 s.f.) / 300.0 mL (4 s.f.) → 60 mg/mL = 6.0·10¹ mg/mL (2 s.f.).
   - `C9`: 0.3, 0.1, 300 g (1 s.f.) → 1.5·10² g, not “150 g” with three apparent s.f.
3. Add a **“course vs IUPAC”** note: the course sometimes uses rounded M (164, 98, 58) and prints 3 s.f.; use the course value if the task gives it, but do not mix it with a more precise value in the same calculation.
4. Add an **answer-format checklist**:
   - unit;
   - decimal comma;
   - s.f. count;
   - `mol/L` not `M`;
   - if the answer is a range, write the range, not just the maximum.
5. Audit all 67 tasks and the 75 recall answers for consistency; mark each answer with `data-sf="2"` etc. if useful for the auditor.
6. Do not silently change the source key’s value; show both and explain.

**Acceptance criteria.**
- The five-step procedure is visible in chapter 1 or 4.
- Three annotated examples show the data, the count, and the rounded answer.
- The Q24/Q10/Q9 policy is consistent and explained.
- The answer-format checklist is in the appendix.
- The build’s expected values are documented with their precision.

#### The 3 substeps

1. **Write the procedure and the three examples**; decide the data precision for each.
2. **Audit the 67 tasks** and mark the inconsistent ones; fix the labels, not the underlying answer.
3. **Add the checklist and a build note**; verify at 390 px and in print.

#### Subtask 19.1 — Procedure and examples

1. Draft the five steps and the three examples in `build/scratch/sigfig.md`.
2. Check each example with a calculator; write the unrounded intermediate.
3. Add a note on trailing zeros and scientific notation.

#### Subtask 19.2 — Audit the tasks

1. Extract every answer and its `Dots` values; count the least precise input.
2. Mark tasks where the printed answer has more or fewer s.f. than the data support.
3. Fix the labels/answers that are clearly wrong (Q24 `0,0010`; Q10 `6,0·10¹`; Q9 `1,5·10²`), and add a note where the course key differs.

#### Subtask 19.3 — Checklist and verification

1. Add the answer-format checklist to chapter 16.
2. Add a build comment listing the precision policy for the critical values.
3. Check the examples at 390 px; the scientific notation must not break the line.

**Suggested features.**
- **Sig-fig helper:** an instrument that takes a calculation string and the input precision, and returns the rounded answer with the rule; no storage.
- **“Answer format” card** in the exam appendix: a one-screen checklist.

**Verification commands.** Recompute the examples; grep for `0,0010`, `6,0·10`, `1,5·10`.

**Risk / rollback.** Medium. Significant figures are a policy question; the document already flags V items. Do not assert a single policy for the course without the lecturer’s confirmation; present the procedure and mark the course-specific choices.

---

### T20 — Add a retrieval-practice layer and a plain exam mode

**Priority:** P2 · **Effort:** M · **Depends on:** T05, T15 · **Evidence:** E20; prompt §8D

**Why this matters.** The document has 75 recall prompts, but they are passive `<details>`: open, read, close. There is no record of what the student knew, no way to filter, and no “exam mode” that hides answers. The prompt explicitly allows a plain per-item “zināju / nezināju” toggle in memory, with a summary count, and no storage. That is a small feature with a large effect on study use.

**What is wrong now.**

- 75 recall items, all `<details class="recall">`; no per-item state.
- The print stylesheet opens all details; good.
- There is no “reset”, “count”, or “filter”.
- There is no “exam mode” that hides the answer until the student commits.
- No localStorage is used, which is correct; keep it that way.

**What to change.**

1. Add a **“Atceres režīms”** control at the top of chapter 15:
   - buttons: “Sākt”, “Atiestatīt”, “Rādīt tikai nezināmos”;
   - a live count: “Zināju 12 / 75; nezināju 8; neizvēlēti 55”;
   - no persistence, no XP, no streaks.
2. For each recall item, add two small buttons **“Zināju” / “Nezināju”** with `aria-pressed`; store state in a JS `Map` in memory.
3. Add an **“Exam mode”** toggle that hides `.recall-answer` until the student clicks “Rādīt atbildi”; in exam mode, the summary buttons are disabled and the count is hidden.
4. Add a **filter** “Rādīt tikai nezināmos” that hides the items marked “Zināju”; reset restores all.
5. Add a **print state**: print always opens all details and ignores the filter; do not print the buttons.
6. Keep the static fallback: if JS is off, all details work as before; the counts are absent, not broken.
7. Add a **concept coverage summary** at the bottom: “58 no 66 jēdzieniem (87,9 %)” with links to the missing concepts A2, A8, D1, D2, M7, M8, R1, S1 (from `build/recall.py`). This makes the gap visible instead of hiding it.

**Acceptance criteria.**
- JS off: all 75 details work; no layout shift.
- JS on: each item has a state; the count updates; reset works; no storage writes.
- Exam mode hides answers until “Rādīt atbildi”; print opens all.
- The coverage summary matches `build/recall.py` (58/66, 87.9 %).
- No gamification, no localStorage, no network.

#### The 3 substeps

1. **Design the state model and the DOM** (buttons, `aria-pressed`, `Map`, no storage).
2. **Implement the JS and CSS**; add the static fallback.
3. **Test with JS on/off, keyboard, print, and 390 px**; verify no storage writes.

#### Subtask 20.1 — Design the state model

1. Define `state = new Map()` keyed by recall item ID; values `known`, `unknown`, or absent.
2. Define the four controls and the count text.
3. Write the no-JS fallback: the controls are hidden with `<noscript>` CSS or `hidden` until JS loads.

#### Subtask 20.2 — Implement

1. Add the controls and buttons to chapter 15; use event delegation.
2. Add the exam-mode toggle and the filter; update the count.
3. Add print CSS: hide controls, open all details, ignore the filter.

#### Subtask 20.3 — Test

1. Keyboard: Tab to each button, Space/Enter toggles; `aria-pressed` updates.
2. JS off: reload with JS disabled; all details open/close; no console errors.
3. Print and integrity: export a page with a mix of states (all answers print once) and grep the file for `localStorage`, `sessionStorage`, `indexedDB`, `fetch`, or `XMLHttpRequest` (all absent).

**Suggested features.**
- **Concept coverage panel:** the 8 missing concepts with a one-line “why not covered” and a link to the chapter.
- **“Random 10”**: a button that opens 10 random recall items; no storage, no score. Use a seeded shuffle for reproducibility in QA? A simple `Math.random` is fine for study, but the workflow tool forbids `Math.random` only in workflow scripts, not in the document. Keep it simple.
- **“Answer format” mode:** hide the answer and show only the unit/s.f. prompt; useful for exam practice.

**Verification commands.**

```bash
grep -nE 'localStorage|sessionStorage|indexedDB|fetch\(|XMLHttpRequest' Master_3_tema_skidumi_un_koncentracijas.html
node workspace_skills/design-taste-frontend/scripts/inspect.mjs Master_3_tema_skidumi_un_koncentracijas.html --widths 1440,768,390
```

**Risk / rollback.** Medium. JS adds a failure mode; keep the static document fully usable. Do not use `localStorage` even if a user asks; the prompt forbids persistence without consent. If the state layer feels like gamification, remove the counts and keep only the filter.

---

## 6. Suggested feature backlog (prioritized)

These are additions, not corrections. Do them only after the P0/P1 tasks pass. Each feature must keep the document self-contained, offline, and readable with JS off.

| ID | Feature | Why it helps | Effort | Depends on | Notes |
|---|---|---|---|---|---|
| F01 | **w ↔ c ↔ γ converter** | The three-way conversion is the core skill; a converter with a visible route teaches the map. | M | T01, T03 | Inputs: M, ρ, one of w/c/γ; output the other two + route + units. Test vectors from prompt §8A. |
| F02 | **Dilution / mixing calculator** | Students reverse `c₁V₁=c₂V₂` and forget `V_water = V₂−V₁`. | M | T17 | Require an additivity checkbox; show the caveat. |
| F03 | **Neutralisation / limiting reagent calculator** | The 1:2 direction and the limiting reagent are the two hardest steps. | M | T18 | Output the limiting reagent, product moles, and a charge check. |
| F04 | **Label reader / percent decision** | “%” without a kind is the most common exam trap. | S–M | T16 | Radio buttons m/m, m/V, V/V; show the assumption and the conversion. |
| F05 | **Route explorer** | Makes the quantity map operational, not decorative. | S | T01 | Click a node; highlight the shortest path; no storage. |
| F06 | **Recall mode** | Turns 75 passive details into active retrieval. | M | T20 | In-memory only; no XP. |
| F07 | **Equation auditor** | Prevents another P2-type false equality. | M | T07 | Build-time, not browser. |
| F08 | **Figure/table index** | Navigation for a 106-page print edition. | S | T08, T14 | Links + page numbers if available. |
| F09 | **Term index** | Resolves terminology without leaving the chapter. | S | T04 | 25 anchors; alphabetical. |
| F10 | **Print edition pass** | 106 pages need running heads, page numbers, and no split rows. | M | T15 | Export and inspect every page category. |
| F11 | **Accessibility report** | Duplicate IDs and skip-link bugs are easy to regress. | S | T09 | Duplicate IDs, broken anchors, heading order, focus. |
| F12 | **Responsive tables** | 390 px is a real study context. | M | T14 | Stacked rows or scroll affordance. |
| F13 | **Composition checker** | P12/Rehydron show how easy it is to omit a component. | S | T10 | Σ row + missing-component warning. |
| F14 | **Unit linter** | `M` vs `mol/L`, `ml` vs `mL`, decimal points. | S | T03 | Build-time; whitelist quotes. |
| F15 | **“Answer format” card** | Students lose points on units and s.f., not chemistry. | XS | T19 | One screen, printable. |
| F16 | **Source-defect filter** | 23 K rows are hard to scan; filter by chapter/confidence. | S | T05 | Plain `<details>` or checkboxes; no storage. |
| F17 | **“What to ask the lecturer” card** | The V items are scattered across 16 chapters. | XS | T02 | One page, 10 questions. |
| F18 | **Print cover** | A 106-page PDF needs a title page and a contents page. | S | T11, T15 | No hero; just title, course, date, disclaimer. |

**Feature design rules (non-negotiable):**

- No external requests, no CDN, no analytics.
- No `localStorage`/`sessionStorage`/IndexedDB writes; state is in memory only.
- No gamification: no XP, streaks, confetti, badges, or “mastery” language.
- No dosing advice beyond the source arithmetic; no reference ranges.
- Every instrument has a visible route, intermediate values, unit, and a static fallback table.
- Every instrument has test vectors in the appendix; the build should run them.

---

## 7. Execution sequence

### Sprint 1 — correctness and trust (P0)

1. T06 (P2 fix) + T07 (equation auditor) — do these together; the auditor should fail on the old P2 and pass on the new one.
2. T09 (duplicate IDs, skip link) — small, high-confidence.
3. T01 (quantity map) + T02 (terminology rows) — the two conceptual contradictions.
4. Rebuild, run `build/build.py`, `build/routes.py`, `build/equations.py`, and the `grep` gates in `AGENTS.md` §8.

### Sprint 2 — structure and accessibility (P1)

5. T08 (figure order) + T10 (lists/compositions).
6. T03 (unit policy) + T04 (term index).
7. T05 (role language) + T13 (callout surfaces).
8. T14 (tables/figures) + T15 (inline provenance/print).
9. Full keyboard, 390 px, dark, print pass.

### Sprint 3 — design and explanation (P1)

10. T11 (header) + T12 (type system).
11. T16 (percent tree) + T17 (dilution) + T18 (neutralisation) + T19 (sig figs).
12. Read chapters 5–12 end to end; remove duplication introduced by the new cards.

### Sprint 4 — features (P2)

13. T20 (recall mode) first; it is the highest study value per line of code.
14. F01/F02/F03 converters if the static document is stable.
15. F10 print edition + F18 cover.
16. Final acceptance gate.

---

## 8. Global acceptance gate (run before calling the plan done)

1. **Build:** `python3 build/build.py` exits 0; task count 67; recall count 75; figures 9; tables 25.
2. **Arithmetic:** `python3 build/equations.py` reports 0 failures; the P2 line reads `1030` and `7,6398`.
3. **IDs:** no duplicate `id`; every `href="#…"` resolves exactly once.
4. **Skip link:** first focusable element; moves focus to `#saturs`.
5. **Figures:** captions in document order 1..9; appendix figure list complete.
6. **Terminology:** no `w(V)`, no `šķīdinātājs — šķīdinātājs`, no `ir nav pārbaudīta`, no `Papildinājums papildinājums`.
7. **Units:** no bare `M` as a unit in own prose; no `ml`/`l`/`cc`/`ppm` outside quotes; no decimal points in prose units.
8. **Roles:** three semantic surfaces + neutral source/practice; no “Pārbaudi sevi” in `role-verified`; legend present.
9. **Typography:** one heading family (or documented two-family role split); measure 60–68ch; sub/sup line-height stable; diacritics render.
10. **Responsive:** no horizontal page scroll at 1440/768/390; tables 9/10 readable at 390; figure labels ≥ 11 px.
11. **Print:** PDF exports; details open; no split table rows; running head or chapter label; page numbers if supported; 106 pages is acceptable only if navigation is usable.
12. **Self-contained:** no external `src`/`href`/`@import`/`url(http…)`; fonts embedded; no network fetch.
13. **Honesty:** every V item is still marked V; no reference ranges; no dosing advice; the “didactic arithmetic” disclaimer is present.
14. **Anti-slop:** `lint.mjs` 0 FAIL; `inspect.mjs` 0 FAIL at 1440/768/390; no gradient/shadow/emoji/pill badges; the palette is not Chemistry_2 pink.
15. **Diff review:** every change has a source (chapter, task, K/I row); no silent substitution of a remembered value.

---

## 9. Open questions for the lecturer (do not resolve by guessing)

1. **K10:** 0.88 % or 0.9 % NaCl in the exam? Which number if the task does not say?
2. **K14:** Are the textbook densities (1.07, 1.02, 1.03, 1.05 g/mL) to be used as given, or may a student substitute a “more real” density?
3. **K15:** How strict are significant figures? Is `0,001 mol` accepted where the data support `0,0010 mol`? Is `60 mg/mL` accepted instead of `6,0·10¹ mg/mL`?
4. **K16:** In P5, use the printed HCOOH (0.75 mol/L) or formaldehyde HCHO (1.15 mol/L)?
5. **K23:** What percent kinds should be assumed for 0.9 % NaCl, 5 % glucose, 3 % H₂O₂, 70 % ethanol, 5 % iodine? Is m/V → m/m conversion required?
6. **K4:** Is the exact Ostwald root required, or is α ≈ √(K/C) accepted in all courses? Will NH₄OH be corrected to NH₃ (aq)?
7. **K17:** Is volume additivity acceptable without a caveat, or must the answer use the final volumetric volume?
8. **K13:** In C10, is “300.0 mL water” intended as the final solution volume, or must the dissolved glucose volume be considered?
9. **K12:** Is the 96 % H₂SO₄ answer 2.77 mL (premature rounding) or 2.78 mL (round once)?
10. **K21:** Is Maalox 13.4 g (key) or 13.5 g (from 13,490 mg)? Are 0.0994 and 0.100 mol both acceptable?
11. **Citrate hydrate:** Does the course use anhydrous `C6H5Na3O7` (M 258.07) or the dihydrate (M 294.10) for Rehydron?
12. **Percent convention:** Is 70 % ethanol V/V and 0.9 % NaCl m/V in this course? The document marks them V; confirm.

---

## 10. Change log for this plan

| Date | Change | Reason |
|---|---|---|
| 2026-10-31 | Initial 20-task plan created after full workspace inspection. | Requested by the user. |
| 2026-10-31 | Added evidence ledger E01–E25, including the P2 arithmetic defect and the figure-order defect. | Findings must be traceable to a file/line, not remembered. |
| 2026-10-31 | Added feature backlog F01–F18 and a global acceptance gate. | The user asked for suggested features and detailed tasks. |

---

## Appendix A — Quick file map for the implementing agent

| Path | What to edit | Used by |
|---|---|---|
| `build/head.html` | CSS, masthead, skip link, print styles | T03, T09, T11–T15 |
| `build/ch01_04.html` | Chapter 1 outcomes, notation, roles | T01, T05, T09, T19 |
| `build/ch05_08.html` | Quantity map, percent table, concentration chapters | T01, T03, T08, T14, T16 |
| `build/ch09_12.html` | Conversion, dilution, neutralisation, medical tasks | T17, T18 |
| `build/ch13_14.html` | Error catalogue, terminology, symbol policy | T02, T03, T05, T19 |
| `build/ch15_16.html` | Recall, appendix, change log, figure/term indexes | T04, T06, T08, T20 |
| `build/tasks_a.py` | Tasks C1.1–C9, P1–P7, B tasks; P2 defect | T06, T07 |
| `build/tasks_b.py` | Tasks C10–C27, P8–P13, BSC tasks | T10, T18 |
| `build/taskbase.py` | Task renderer, anchors, answer block | T05, T09 |
| `build/figures.py` | 9 SVG figures and captions | T01, T08, T14 |
| `build/build.py` | Assembly and textual gates | T03, T07, T09 |
| `build/calc.py` | Expected values and recomputation | T06, T07, T16–T19 |
| `build/recall.py` | 75 recall items and coverage | T20 |
| `build/routes.py` | Route connectivity | T01 |
| `build/qa/` | Screenshots, PDF, report | T10, T14, T15 |

## Appendix B — Exact bad strings to retire (and where they may still appear)

| Bad string | Must not appear in | Allowed only in |
|---|---|---|
| `septiņi lielumi` | chapter 5 lead and prose | a quoted historical note, if any (currently none) |
| `septiņi neatkarīgi` | anywhere | nowhere |
| `šķīdinātājs</strong> — šķīdinātājs` | table 18 | nowhere |
| `w(V)` | table 18 and prose | nowhere |
| `ir nav pārbaudīta` | chapter 14 | nowhere |
| `Papildinājums papildinājums` | chapter 11 | nowhere |
| `m(šķīdums) = 1020 g` | P2 | nowhere (P2 must use 1030) |
| `78,69/1020` | P2 | nowhere |
| `t-c11`, `t-c12`, `t-c21`, `t-c22` as duplicates | anchors | the new `t-c1-1` etc. are unique |
| `1. O1.` | chapter 1 | nowhere |
| `0,001 mol` for C24 without a note | C24 | a K15 quote with the correction |
| `13,4 g` | P13 answer | a K21 quote with the correction |
| `(HCOOH)` as formalin | P5 answer | a K16 quote with the correction |
| `n skābes = 2n sārma` | chapter 11 | a K9 quote with the correction |

## Appendix C — One-page implementation checklist

- [ ] Edit `build/tasks_a.py` P2: `1020` → `1030`; check line.
- [ ] Add `I1` to chapter 16; do not call it K24.
- [ ] Add `build/equations.py`; integrate into `build/build.py`.
- [ ] Fix `build/taskbase.py` anchor: keep dots as dashes.
- [ ] Move skip link before `<header>`; add `tabindex="-1"` to `<main>`.
- [ ] Fix chapter 5 lead and “independent” sentence; update figure caption.
- [ ] Fix table 18 rows 1 and C10; fix double negative.
- [ ] Renumber figures 1–9 in document order; add figure index.
- [ ] Fix O1–O5 double numbering; add `id="o1"` etc.
- [ ] Add P12 ascorbic acid row and Σ line; add Rehydron hydrate note/Σ.
- [ ] Add the role legend; move “Pārbaudi sevi” out of verified.
- [ ] Add the unit policy box and linter.
- [ ] Add the term index and `<dfn>` first uses.
- [ ] Replace the masthead right rail; measure mobile.
- [ ] Unify heading family/scale; measure 60–68ch.
- [ ] Fix inline `.prov` underline and caption separator.
- [ ] Add stacked/scroll tables; test 390 px.
- [ ] Add percent decision tree, dilution caveat, neutralisation algorithm, sig-fig procedure.
- [ ] Add recall mode; no storage.
- [ ] Run the global acceptance gate.

---

*End of plan. This file is a plan, not a claim that the document is finished. The P2 correction and the equation auditor are the first two actions; everything else is downstream of trust in the numbers.*
