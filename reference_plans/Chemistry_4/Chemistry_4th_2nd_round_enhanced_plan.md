# Enhanced Execution Plan — Thermodynamics Course Build (F03–F10, B01–B05)

**Generated:** 2026-11-09
**Source cards:** F03–F10 (feature/adoption candidates) and B01–B05 (bug-fixing, wiring, debloating & false-claim crushing)
**Plan shape:** 15 tasks × 3 subtasks × 3 substeps = **135 substeps**
**Primary artifact:** `Master_4_temats_termodinamika.html`
**Current size:** 2,386,187 B · **Ceiling:** 2,097,152 B (2 MiB, `AGENTS.md` §4)
**Canonical build command:** `python3 -I build/build_html.py`

---

## 0. How to read this plan

| Label | Meaning |
|---|---|
| `S{n}.{m}` | Subtask *n*, substep *m*. Every task has exactly `S1.1–S1.3`, `S2.1–S2.3`, `S3.1–S3.3`. |
| **[GATE]** | A blocking check. The substask may not be marked done until the gate passes. |
| **Owner files** | The exact files an agent is permitted to touch for that substep. Anything outside this list needs a new task ID. |
| **Evidence** | The artifact that must exist after the substep (report, hash, screenshot, log, fixture). Evidence is stored under `docs/evidence/<TASK-ID>/`. |
| **Exit criterion** | The observable condition that closes the substep. |

**Global rules inherited from the cards**

1. No new `localStorage`, streak, XP, progress bar, percent score, mastery layer or ranking (`AGENTS.md` §8 ban).
2. No inline `on*=` event attributes and no data-array DOM hydration (`innerHTML` / `createElement` / `insertAdjacentHTML`) in generated output.
3. No hand-editing generated artifacts; all changes flow through `build/build_html.py`.
4. Every claim carries a source role and a verification layer; metadata alone never verifies claim text.
5. Every UI change needs falkon/falkon screenshots; every print change needs a PDF render inspected at 100 %.
6. No destructive build or legacy probe runs before its side effects have been read.

---

## 1. Triage summary

| ID | Title | Value | Effort | Priority | Verdict | Plan posture |
|---|---|---|---|---|---|---|
| F03 | Sign-convention comparison card | 5/5 | 1/5 | P1 | RECOMMEND ADOPT | Build first; unblocks F06, F10 |
| F04 | Uncertainty-budget worksheet (neutralisation calorimetry) | 4/5 | 4/5 | P2 | LOW-PRIORITY / DEFER | Duplicate-check gate before any authoring |
| F05 | No-JavaScript core study and print route | 5/5 | 3/5 | P1 | RECOMMEND ADOPT | Contract gate for all other UI work |
| F06 | Constraint-aware ΔG temperature comparison cards | 4/5 | 3/5 | P2 | RECOMMEND ADOPT | Depends on F03 notation |
| F07 | Course readiness checklist (no scoring) | 3/5 | 2/5 | P3 | REJECT IN FAVOR OF LEAN ALTERNATIVE | Build only the lean static checklist |
| F08 | Local source citation and claim-review panel | 4/5 | 3/5 | P2 | LOW-PRIORITY / DEFER | Gap analysis first; extend only if fields missing |
| F09 | Vector reading prompts on selected figures | 4/5 | 3/5 | P3 | LOW-PRIORITY / DEFER | Verify coverage/hash before authoring |
| F10 | One-page Latvian quick-reference sheet | 5/5 | 2/5 | P1 | RECOMMEND ADOPT | Depends on F03; print-evidence driven |
| B01 | Output size under 2 MiB | — | — | High | CONFIRMED DEFECT [TESTED] | Profile → reduce → gate |
| B02 | Remove inline handlers / unsafe rendering | — | — | Critical | CONFIRMED DEFECT [TESTED] | Inventory → migrate → parser gates |
| B03 | Chapter 9 numbering / recall-count drift | — | — | High | DIAGNOSTIC INVESTIGATION [INSPECTED] | Reproduce before repair |
| B04 | Verify or withdraw unsupported claims | — | — | Critical | DIAGNOSTIC INVESTIGATION [INSPECTED]/[UNVERIFIED] | Claim records → evidence → correct/withdraw |
| B05 | Trace interaction wiring & unreachable paths | — | — | High | DIAGNOSTIC INVESTIGATION [UNVERIFIED] | Static inventory → bounded probes → classify |

---

## 2. Cross-task dependencies and recommended sequencing

```
B02 (contract: no inline handlers / no DOM templating)
 └──► F05 (no-JS contract) ──► F03 (notation.json) ──► F10 (print sheet)
                                    └──► F06 (ΔG cards)
B01 (byte ceiling) constrains every addition above; run its profiler before and after each merge.
F04 ◄──── duplicate check ────► F08 (both defer on the same provenance question)
F09 depends on figure_steps.py coverage report (independent, P3).
B03 / B05 are diagnostics: they must produce evidence before any repair task is opened.
B04 is independent but blocks any "verified" label used by F08.
F07 is the lean replacement for a rejected dashboard; it must not import scoring.
```

**Recommended order:** B02 contract → B01 profiler → F05 → F03 → F10 → F06 → F04/F08 duplicate checks → F09 → F07 → B03/B05 diagnostics → B04 claim review.

---

## 3. Shared gates and evidence contract

| Gate | Command / method | Pass condition |
|---|---|---|
| Size ceiling | `wc -c < Master_4_temats_termodinamika.html` | ≤ 2,097,152 B |
| Hash binding | `sha256sum` on source fragment and generated master | Recorded in `docs/evidence/<ID>/hashes.txt` |
| Inline-handler gate | HTML parser scan for `on\w+=` attributes | 0 matches |
| Templating gate | `rg -n 'innerHTML\|createElement\|insertAdjacentHTML' build/part_*.html build/script.js` | 0 matches in output |
| No-JS gate | `tools/check_html.py` + `js=off` browser protocol | All core anchors/answers present with scripts disabled |
| Print gate | PDF render at 100 %, inspect 320 / 1440 / print | Legible, unclipped, monochrome-safe |
| A11y gate | Keyboard order, `<th scope>`, `<label for>`, screen-reader pass | Reading order == DOM order; labels associated |
| Offline gate | Load via `file://` with network disabled | Zero external requests |

---

# PART A — Feature tasks (F03–F10)

## F03 — Sign-convention comparison card

**ID, value and adoption.** Value 5/5; effort 1/5; priority P1; Adoption Verdict: **[RECOMMEND ADOPT]**.
The course and IUPAC conventions use opposing work signs; a compact card prevents students applying a remembered sign without first identifying the boundary.

**Feature type.** Conceptual scaffolding / quick reference.

**Utility and target outcome.** Support conversion between `Q = ΔU + A` and `ΔU = q + w` with a fixed system, a drawn arrow, an explicit work-by/on direction, and one reversible numeric example. Success = a student can state which convention a page uses and convert correctly in both directions.

**Architecture and interaction workflow.** Static HTML table generated from `build/notation.json`; schema fields `convention, symbol, positive_direction, equation, example, source`. No persistence, no JavaScript. Placed near the first-law chapter and repeated once in the print formula card.

### Subtask S1 — Establish the authoritative convention pair and the shared boundary

**S1.1 — Extract the course convention from the K/L pages.**
Owner files: `build/part_*.html` (read-only), `build/notation.json`.
Action: locate the first-law pages, record the exact equation form used (`Q = ΔU + A`), the work symbol (`A`), the sign rule for work done *by* the system, the page/anchor ID and the source fragment hash. Do not paraphrase — copy the equation verbatim.
Evidence: `docs/evidence/F03/course_convention.txt` with verbatim equation + anchor + hash.
Exit criterion: the course row's `equation` and `positive_direction` fields are traceable to one anchor.

**S1.2 — Extract the IUPAC convention from the cited source.**
Owner files: `build/notation.json`, bibliography source.
Action: record `ΔU = q + w`, `w > 0` for work done *on* the system, plus edition/section of the cited standard. If the edition cannot be confirmed, record `source` as "unverified" rather than inventing a page number.
Evidence: `docs/evidence/F03/iupac_convention.txt`.
Exit criterion: both rows name their source; neither claims verification it does not have.

**S1.3 — Define and publish the shared system boundary statement. [GATE]**
Owner files: `build/notation.json`.
Action: add a `boundary` field used by *both* rows: closed system, single clearly drawn boundary, only expansion/compression work unless stated otherwise, same process and same state change for both conventions. This is the sentence that makes the two rows comparable.
Evidence: boundary string in `notation.json`; rendered in the card header.
Exit criterion: removing the boundary sentence makes the two rows non-comparable — i.e. it is load-bearing.

### Subtask S2 — Author matched rows and the conversion

**S2.1 — Author the two matched rows.**
Owner files: `build/notation.json`.
Action: populate `convention, symbol, positive_direction, equation, example, source` for both rows. Use one matched numeric example, e.g. a process with `q = −120 J` (heat released) and `A = +120 J` (work done by the system) giving `w = −120 J` and the same `ΔU` under both conventions. Keep every quantity in joules and the same system.
Evidence: JSON diff of `notation.json`.
Exit criterion: both rows describe the *same* physical process with the same `ΔU`.

**S2.2 — Add the conversion line `w = −A` with a dimensional check. [GATE]**
Owner files: `build/notation.json`, `build/build_html.py`.
Action: emit the conversion row plus a worked arithmetic trace (`A = +120 J → w = −120 J`; `ΔU = q + w = −120 + (−120) = −240 J` vs `ΔU = Q − A`). Assert dimensional consistency: both work terms in J, same sign convention, same reference state.
Evidence: arithmetic trace in the card; unit assertion in the generator.
Exit criterion: the two equations produce identical `ΔU` for the example.

**S2.3 — Generate the static table with accessible markup.**
Owner files: `build/build_html.py`, `build/style.css`.
Action: render `<table class="sign-convention">` with `<th scope="row">` row headers, `<caption>`, no JS, no `<details>` state, monochrome-safe print rules (borders, not colour alone).
Evidence: generated fragment; parser check for `scope="row"`.
Exit criterion: table is fully interpretable with styles disabled and in greyscale print.

### Subtask S3 — Wire, link and test

**S3.1 — Place the card and add links.**
Owner files: `build/part_top.html`, `build/part_16.html`, `build/build_html.py`.
Action: place the card immediately after the first-law statement; add inbound links from the calculator/recall view and from the formula appendix; include the table exactly once in the print formula card.
Evidence: anchor list; print page map entry.
Exit criterion: every first-law calculation surface links to the card.

**S3.2 — Test equivalent arithmetic in both directions. [GATE]**
Owner files: `build/calc.py` (test only), `docs/evidence/F03/`.
Action: convert `q/w/A` for one exothermic and one endothermic example; assert equality of `ΔU` within tolerance; assert that a deliberately flipped sign produces a detectable mismatch (sign-check helper or expected-value table).
Evidence: test output showing pass/fail for both examples and the negative case.
Exit criterion: wrong sign is easy to detect, not silently plausible.

**S3.3 — Inspect responsive, print and interaction boundaries.**
Owner files: `build/style.css`.
Action: inspect at 320 px, 1440 px and print; verify keyboard order follows reading order; confirm no collision with theme tokens or with `<details>` open/closed states elsewhere on the page.
Evidence: screenshots (lite-shot) at 320/1440 + PDF page.
Exit criterion: no layout shift, no token collision, no focus trap.

**Interoperability.** Palette and search can anchor to the card; the calculator links to it; print includes the table once; no collision with theme tokens or `<details>` states.

**Failure states and accessibility.** If a source convention is unresolved, present two *named* conventions with an explicit uncertainty note rather than merging them. Row headers accessible; print monochrome; keyboard order follows reading order.

**Integration acceptance.** Compare converted `q/w/A` outputs for exothermic and endothermic examples; a wrong sign must be easy to detect; inspect at 320, 1440 and print.

**DoD and kill criterion.** **DoD:** course and IUPAC rows are independently interpretable and source-linked. **Kill** if an existing equivalent card passes the same criterion.

---

## F04 — Uncertainty-budget worksheet for neutralisation calorimetry

**ID, value and adoption.** Value 4/5; effort 4/5; priority P2; Adoption Verdict: **[LOW-PRIORITY / DEFER]**.
A saved report claims an uncertainty budget in the virtual lab, but the current output hash is unknown. Duplicating it is likely waste.

**Feature type.** Lab analysis / quantitative reasoning.

**Utility and target outcome.** Let a student identify which measured quantity dominates ΔH uncertainty and see the assumptions inside the `q/n` propagation.

**Architecture and interaction workflow.** Static worked worksheet sourced from `calc.json`; fields `input, uncertainty, sensitivity, contribution, assumption`. If interactive, native inputs only, inside the one authorized calculator. No local storage.

### Subtask S1 — Duplicate check (blocking gate)

**S1.1 — Verify whether an existing budget is present in current master. [GATE]**
Owner files: read-only scan of `build/part_*.html`, `build/instruments.html`, generated master.
Action: search for uncertainty-budget vocabulary in both Latvian and English (`nedrošums`, `kļūda`, `uncertainty`, `budget`, `dominance`); record whether a budget table exists, its row count and the master hash it was found in.
Evidence: `docs/evidence/F04/duplicate_check.md` with match counts and hash.
Exit criterion: a definite yes/no on "budget already shipped".

**S1.2 — Inventory the L/LA data that could support uncertainties.**
Owner files: `build/instruments.html`, `build/calc.json` (read-only).
Action: list every measurable quantity available to the learner (temperature resolution, solution mass/volume, concentration, calorimeter heat capacity, ΔT) and whether a defensible uncertainty exists for it.
Evidence: data inventory table.
Exit criterion: each candidate input is marked *supported* or *unsupported by L/LA data*.

**S1.3 — Record the verdict and stop or proceed. [GATE]**
Owner files: `docs/evidence/F04/`.
Action: if a duplicate budget exists, close F04 as DEFER with the evidence link and do not author anything. If absent, confirm that at least the dominant term's uncertainty is supportable, then proceed to S2.
Evidence: verdict line with hash reference.
Exit criterion: no authoring work begins while the duplicate question is open.

### Subtask S2 — Propagation model and worked example

**S2.1 — Define propagation assumptions explicitly.**
Owner files: `build/calc.py`, `build/calc.json`.
Action: write the model `q = C_cal·ΔT` (or `c·m·ΔT`), `n = c·V`, `ΔH = −q/n`; state which inputs are treated independent, which correlated, and whether uncertainties combine by root-sum-square (independent) or linear addition (worst case). Record the chosen rule and why.
Evidence: assumption block in `calc.json`.
Exit criterion: a reader can reproduce the combination rule from the text alone.

**S2.2 — Calculate the printed worked example. [GATE]**
Owner files: `build/calc.py`, `build/calc.json`.
Action: compute a full budget with fields `input, uncertainty, sensitivity, contribution, assumption`; rank contributions; identify the dominant term; round to justified significant figures — no false precision.
Evidence: worked example rows + dominance ranking.
Exit criterion: the dominant term is unambiguous and the rounding is defensible.

**S2.3 — Cross-check Python against hand propagation.**
Owner files: `build/calc.py`, `docs/evidence/F04/`.
Action: recompute the same budget by hand (or in a separate vector expression) and compare term by term; record both results and the delta.
Evidence: comparison table.
Exit criterion: agreement within stated tolerance, or a documented reason for divergence.

### Subtask S3 — Learner worksheet and reveal

**S3.1 — Add the blank learner worksheet.**
Owner files: `build/instruments.html`, `build/part_16.html`.
Action: render the same table with empty `uncertainty/sensitivity/contribution` cells, plus a `<details>` answer reveal containing the worked example. The reveal must not be open by default.
Evidence: worksheet fragment.
Exit criterion: blank state and revealed state both render without JS.

**S3.2 — Implement input validation and interaction limits.**
Owner files: `build/calc.py`, `build/instruments.html`.
Action: reject zero or invalid `ΔT` and `n` with an accessible inline message; if any interactivity is added, use native inputs only inside the one authorized calculator; no `localStorage`.
Evidence: validation test cases (0, negative, non-numeric).
Exit criterion: invalid input never produces a numeric "answer".

**S3.3 — Verify print, blank state and accessibility.**
Owner files: `build/print_map.py`, `build/style.css`.
Action: confirm the worksheet appears in the print page map, prints correctly in blank state, and ships with an accessible table plus a text description of the method.
Evidence: PDF page + a11y check.
Exit criterion: print output is usable as a paper worksheet.

**Interoperability.** Links from the lab chapter and the exam; print page map includes the worksheet; input calculator and theme unaffected.

**Failure states and accessibility.** Zero/invalid `ΔT` or `n` is rejected; uncertainty assumptions explicit; no false precision; accessible table and text description.

**Integration acceptance.** Compare hand propagation to the Python vector; verify worksheet print and blank state.

**DoD and kill criterion.** **DoD:** uncertainty model and all assumptions documented. **Kill** if F08 already provides equivalent analysis, or if uncertainties cannot be supported by L/LA data.

---

## F05 — No-JavaScript core study and print route

**ID, value and adoption.** Value 5/5; effort 3/5; priority P1; Adoption Verdict: **[RECOMMEND ADOPT]**.
A `<noscript>` exists, but OI-28 says JS-off reading/nav and instrument fallbacks are untested; adding more UI could leave core learning inaccessible.

**Feature type.** Accessibility / offline resilience.

**Utility and target outcome.** Guarantee that navigation, essential explanation, static calculations and closed-answer retrieval remain available when scripts fail or are disabled.

**Architecture and interaction workflow.** No-JS is a *testable feature contract*, implemented primarily as semantic HTML plus build-time Python output. A `<noscript>` banner links to static calculation tables and a chapter index; avoid duplicate content.

### Subtask S1 — Map script dependence

**S1.1 — Enumerate every script-dependent region.**
Owner files: read-only scan of `build/part_*.html`, `build/script.js`, generated master.
Action: list each element/ID that requires JS (nav toggles, search, calculators, instrument simulators, theme switch, any `<details>` polyfill) with the learning outcome it serves.
Evidence: `docs/evidence/F05/js_dependence_map.md`.
Exit criterion: every JS-bound region has an ID and an outcome tag.

**S1.2 — Classify core vs enhancement and record core losses. [GATE]**
Owner files: `docs/evidence/F05/`.
Action: mark each region *core* (concept explanation, equation, static calculation, closed-answer retrieval, navigation) or *enhancement*. Any core region without a static path is a **core loss** and blocks adoption.
Evidence: classification table with a core-loss count.
Exit criterion: core-loss count is either 0 or has a named remediation per item.

**S1.3 — Produce the dependence map artifact.**
Owner files: `docs/evidence/F05/js_dependence_map.md`.
Action: consolidate S1.1/S1.2 into one document with counts, per-region outcome mapping, and the proposed fallback for each core region.
Evidence: committed map.
Exit criterion: the map is the reference used by S2 and by the acceptance test.

### Subtask S2 — Generate deterministic static fallbacks

**S2.1 — Render static fallback blocks at build time.**
Owner files: `build/build_html.py`.
Action: emit static calculation tables, the chapter index, and closed-answer lists as ordinary HTML in the generated output so the content exists before any script runs.
Evidence: generated fragment containing the static blocks.
Exit criterion: content is present in the raw HTML with scripts disabled.

**S2.2 — Hide only redundant controls when JS is absent.**
Owner files: `build/build_html.py`, `build/part_top.html`, `build/style.css`.
Action: use progressive enhancement — default `no-js` class on `<html>`, swapped by a minimal inline script; CSS hides only controls that are pure duplicates of static content. The `<noscript>` banner links to the static tables and chapter index without repeating their content.
Evidence: CSS rules + banner markup.
Exit criterion: no content is hidden that has no static equivalent.

**S2.3 — Make theme and assets JS-independent.**
Owner files: `build/style.css`, `build/instruments.html`.
Action: theme falls back to `prefers-color-scheme` with no JS; confirm zero external requests (no CDN fonts, no remote scripts) so the file works offline from `file://`.
Evidence: network log showing 0 external requests.
Exit criterion: page renders correctly offline with JS blocked.

### Subtask S3 — Protocol test and gates

**S3.1 — Add the `js=off` browser protocol and Python checker. [GATE]**
Owner files: `tools/check_html.py` (new), `docs/evidence/F05/`.
Action: document a repeatable procedure (disable JS in the test browser, open the `file://` master, capture) and implement a parser that asserts required static anchors, answers and nav targets exist in the output.
Evidence: checker script + protocol doc.
Exit criterion: the checker fails loudly when a core anchor is missing.

**S3.2 — Compare outcomes and anchor counts with/without JS.**
Owner files: `tools/check_html.py`.
Action: diff the set of required learning outcomes and anchor counts between JS-on and JS-off runs; assert no core concept or calculation explanation is JS-only.
Evidence: comparison report.
Exit criterion: zero core-only items.

**S3.3 — Capture evidence and run the a11y review.**
Owner files: `docs/evidence/F05/`.
Action: capture the no-JS screenshot **only through lite-shot**; run a screen-reader label review; verify reading stays usable and focus is retained under three conditions: script blocked, malformed storage, and JS disabled.
Evidence: screenshot + SR review notes.
Exit criterion: all three failure conditions leave reading usable.

**Interoperability.** Search/nav, `<details>`, figure descriptions, exam and print routes must work or disclose the unavailable action; theme falls back to system preference.

**Failure states and accessibility.** Script blocked, malformed storage and disabled JS all leave reading usable; focus remains; no external requests.

**Integration acceptance.** Compare required learning outcomes and anchor counts with/without JS; submit the no-JS screenshot only through lite-shot; screen-reader label review.

**DoD and kill criterion.** **DoD:** no core concept/calculation explanation is JS-only. **Kill** only if all interactive scripts are removed and an independent gate proves no content loss.

---

## F06 — Constraint-aware ΔG temperature comparison cards

**ID, value and adoption.** Value 4/5; effort 3/5; priority P2; Adoption Verdict: **[RECOMMEND ADOPT]**.
Temperature-crossing values are easy to overgeneralize when ΔH and ΔS are treated constant; a bounded card communicates the model conditions.

**Feature type.** Thermodynamic derivation / comparison.

**Utility and target outcome.** Show sign cases and a computed crossover only where assumptions and the supported temperature range permit.

**Architecture and interaction workflow.** Python generates precomputed values from `ΔG(T) = ΔH − TΔS`, with dataset IDs, validity range and units; static `<details>` cards. No JavaScript slider.

### Subtask S1 — Link curves to data and uncertainty

**S1.1 — Link each case to its dataset row. [GATE]**
Owner files: `build/calc.json`, `build/calc.py`.
Action: every card references a dataset ID carrying `ΔH`, `ΔS`, units, source and uncertainty. No card may exist without a dataset row.
Evidence: dataset-to-card mapping table.
Exit criterion: 1:1 mapping, no orphan cards.

**S1.2 — Record the applicable temperature range per dataset.**
Owner files: `build/calc.json`.
Action: store `T_min`/`T_max` (or an explicit "unbounded within course scope" flag) and the reason for the bound (phase change, measurement range, assumption breakdown).
Evidence: range fields with justification.
Exit criterion: every dataset has a range or an explicit unbounded justification.

**S1.3 — Reconcile units and sign convention with F03.**
Owner files: `build/notation.json`, `build/calc.py`.
Action: assert ΔH in kJ/mol (or J/mol) consistently, ΔS in matching units, and that the work/heat sign convention matches the F03 card so `ΔG = ΔH − TΔS` is not silently mixed with the other convention.
Evidence: unit-consistency assertion.
Exit criterion: no mixed units or mixed sign conventions across cards.

### Subtask S2 — Generate sign cases and the crossover

**S2.1 — Generate the sign-case table.**
Owner files: `build/calc.py`.
Action: emit rows for all four ΔH/ΔS quadrants plus the edge cases ΔS = 0 and ΔH = 0, each with the resulting ΔG(T) behaviour (always negative, always positive, crossover, temperature-independent).
Evidence: sign-case table.
Exit criterion: every quadrant and both edge cases are represented.

**S2.2 — Compute `T* = ΔH/ΔS` only under valid conditions. [GATE]**
Owner files: `build/calc.py`.
Action: compute `T*` only when `ΔS ≠ 0` **and** `T*` lies inside the applicable range. When `ΔS = 0`, emit "no finite crossover". When `T*` is outside the range, label it **extrapolation** and do not present it as a course result.
Evidence: per-case computation log with the guard conditions.
Exit criterion: no unguarded or out-of-range crossover is emitted.

**S2.3 — Render static `<details>` cards with semantic styling.**
Owner files: `build/part_10_12.html`, `build/style.css`, `build/figures.py`, `build/figures.html`.
Action: render one `<details>` card per case; colours come from semantic tokens (not hard-coded hex); every label carries its sign; no JS slider; no custom state.
Evidence: generated cards.
Exit criterion: cards render and print correctly with styles reduced.

### Subtask S3 — Boundary text and testing

**S3.1 — Add boundary/assumption text to every card.**
Owner files: `build/part_10_12.html`, `build/calc.py`.
Action: state the model conditions explicitly — ΔH and ΔS treated constant over the range, no phase change, fixed pressure/composition — and name what breaks them.
Evidence: assumption text per card.
Exit criterion: a student can see *why* the crossover may not hold outside the card.

**S3.2 — Test values on both sides of `T*` and at the range boundary. [GATE]**
Owner files: `build/calc.py`, `docs/evidence/F06/`.
Action: evaluate ΔG just below and just above `T*` and confirm the sign flips; evaluate exactly at `T_min`/`T_max` and confirm the boundary label; compare against hand calculation.
Evidence: test table with sign-flip confirmation.
Exit criterion: sign flip and boundary behaviour both verified numerically.

**S3.3 — Verify integration surfaces.**
Owner files: `build/figures.html`, `build/print_map.py`.
Action: confirm the concept map and search link to the corresponding case, the exam uses distinct cases, the print figure caption states the validity range, reduced-motion is moot (no animation), and the accessible table is the source of truth.
Evidence: link list + print caption.
Exit criterion: every surface either links to a case or discloses that it does not.

**Interoperability.** Concept map and search link to the corresponding case; exam uses distinct cases; print figure caption states validity; no custom state.

**Failure states and accessibility.** `ΔS = 0` has no finite crossover; an outside-range crossing is marked extrapolation; the accessible table is the source of truth; reduced-motion moot.

**Integration acceptance.** Test signs and cases for the ΔH/ΔS quadrant, zero denominator, range boundary and print.

**DoD and kill criterion.** **DoD:** each plotted point traces to data and assumptions. **Kill** if there is no verified use case, or if the constant-property assumption misleads beyond the course scope.

---

## F07 — Course readiness checklist tied to outcomes, without scoring

**ID, value and adoption.** Value 3/5; effort 2/5; priority P3; Adoption Verdict: **[REJECT IN FAVOR OF LEAN ALTERNATIVE]**.
An exam and concept map are already claimed by historical reports; another dashboard risks a mastery layer explicitly banned in `AGENTS.md` §8.

**Feature type.** Study workflow / navigation.

**Utility and target outcome.** Offer a simple unscored checklist mapping the seven course outcomes to chapter/retrieval anchors, with no completion persistence and no percent score.

**Architecture and interaction workflow.** Static table with native checkboxes that reset on reload; no `localStorage`, streak, XP, progress bar or ranking. This is the lean alternative to analytics.

### Subtask S1 — Verify the outcome list and existing equivalents

**S1.1 — Verify the current outcome list from the prompt/T source. [GATE]**
Owner files: `build/inventory.json`, course prompt/T source.
Action: extract the seven course outcomes verbatim with their IDs; do not rely on a historical report's paraphrase.
Evidence: outcome list with source anchor.
Exit criterion: exactly seven outcomes, each traceable to the current source.

**S1.2 — Confirm what the exam and concept map already provide.**
Owner files: read-only scan of generated master.
Action: record the anchors the existing exam and concept map expose, so the checklist links to them rather than duplicating them.
Evidence: existing-anchor inventory.
Exit criterion: no planned checklist row duplicates an existing learner-facing surface.

**S1.3 — Pre-check the kill criterion against `coverage_table.html`. [GATE]**
Owner files: read-only scan.
Action: determine whether `coverage_table.html` already provides an equivalent learner-facing checklist. If yes, close F07 immediately with evidence.
Evidence: comparison note.
Exit criterion: proceed only if no equivalent exists.

### Subtask S2 — Build the outcome → anchor mapping

**S2.1 — Build the mapping from the inventory.**
Owner files: `build/inventory.json`.
Action: map each of the seven outcomes to chapter anchors and retrieval anchors; store the mapping in `inventory.json` with a stable schema.
Evidence: mapping JSON.
Exit criterion: all seven outcomes have at least one anchor.

**S2.2 — Make unmapped concepts visibly "not mapped".**
Owner files: `build/inventory.json`, `build/part_16.html`.
Action: where an outcome has no anchor, render an explicit "not mapped" / "nav kartēts" state instead of silently omitting the row.
Evidence: rendered empty state.
Exit criterion: gaps are visible to a reviewer, not hidden.

**S2.3 — Record the coverage count.**
Owner files: `build/inventory.json`.
Action: compute and store the mapped/total count for the acceptance test (used only for verification, never displayed as a score).
Evidence: count field.
Exit criterion: count is reproducible from the mapping.

### Subtask S3 — Render as a printable, non-persistent checklist

**S3.1 — Render Appendix D as a static checklist. [GATE]**
Owner files: `build/part_16.html`, `build/build_html.py`.
Action: render a printable table with native checkboxes; no JS, no `localStorage`, no streak, XP, progress bar, percent score or ranking.
Evidence: generated Appendix D.
Exit criterion: parser scan finds zero storage calls and zero score-like strings in the fragment.

**S3.2 — Style with standard form controls and print blanks.**
Owner files: `build/style.css`.
Action: use standard form controls and theme/viewport defaults; print shows *blank* boxes (never pre-ticked); associate every checkbox with a `<label for>`.
Evidence: CSS + print render.
Exit criterion: keyboard toggling works and print boxes are empty.

**S3.3 — Run the acceptance sequence.**
Owner files: `docs/evidence/F07/`.
Action: click all anchors, toggle every box by keyboard, reload to confirm no persisted state, and compare the print mapping count against the stored count. Confirm the screen reader announces optional self-reflection, not a grade.
Evidence: test log + reload screenshot.
Exit criterion: zero persistence, full anchor validity, count match.

**Interoperability.** Navigation links to existing retrieval; print shows blank boxes; theme/viewport use standard form controls.

**Failure states and accessibility.** Empty concepts remain visibly "not mapped"; keyboard label association; screen reader indicates optional self-reflection, not grade.

**Integration acceptance.** Click all anchors, keyboard-toggle boxes, reload to confirm no persisted state, compare print mapping count.

**DoD and kill criterion.** **DoD:** full outcome coverage and zero scoring/storage. **Kill** if `coverage_table.html` already gives an equivalent learner-facing checklist.

---

## F08 — Local source citation and claim-review panel

**ID, value and adoption.** Value 4/5; effort 3/5; priority P2; Adoption Verdict: **[LOW-PRIORITY / DEFER]**.
Appendix C and F04 reportedly provide provenance labels and S-ID links; the reviewer needs a claim's source role and condition beside the text.

**Feature type.** Terminology / citation tooling.

**Utility and target outcome.** Expose source role, location and confidence for flagged claims without claiming that publisher metadata proves claim text.

**Architecture and interaction workflow.** Build-time static `<details>` panel per S-ID from a manifest: `claim, source_id, location, role, verification_layer, condition, warrant, status`; no network fetch.

### Subtask S1 — Verify F04's current output and gaps

**S1.1 — Inspect Appendix C and F04 provenance output in current master. [GATE]**
Owner files: read-only scan of `build/part_16.html`, `build/part_15.html`, generated master.
Action: list which provenance fields already exist (S-ID links, labels, locations) and record the master hash inspected.
Evidence: field-presence table + hash.
Exit criterion: a definite list of present vs absent fields.

**S1.2 — Identify the real gap: UI or source access.**
Owner files: `docs/evidence/F08/`.
Action: determine whether the missing piece is a *display* gap (fields exist, not shown) or an *access* gap (the source text itself is unavailable). Only a display gap justifies UI work.
Evidence: gap classification.
Exit criterion: the gap is named, not assumed.

**S1.3 — Record the defer/proceed verdict. [GATE]**
Owner files: `docs/evidence/F08/`.
Action: if existing F04 already covers source roles and the remaining gap is source access, close F08 as DEFER. Otherwise proceed to S2.
Evidence: verdict line.
Exit criterion: no manifest is created while the verdict is open.

### Subtask S2 — Extend the manifest only if warranted

**S2.1 — Create `build/source_claims.json` only if fields are missing.**
Owner files: `build/source_claims.json` (new, conditional).
Action: use the schema `claim, source_id, location, role, verification_layer, condition, warrant, status`. If the file is not warranted, this substep is recorded as *not executed* with the reason.
Evidence: file or a "not warranted" note.
Exit criterion: the file exists if and only if a field gap was proven.

**S2.2 — Populate entries without inventing metadata.**
Owner files: `build/source_claims.json`.
Action: fill entries for flagged claims; never invent a page number or DOI; unknown or conflicting citations get `status: "unverified"`.
Evidence: populated manifest with status distribution.
Exit criterion: zero fabricated locations.

**S2.3 — Validate the manifest against sources. [GATE]**
Owner files: `build/source_claims.json`, `docs/evidence/F08/`.
Action: for each entry, confirm `location` and `role` trace to a real bibliography entry, and that `verification_layer` records whether the *text* was inspected or only metadata.
Evidence: validation table.
Exit criterion: no claim is marked verified on metadata alone.

### Subtask S3 — Generate the panel and integrate

**S3.1 — Generate the anchor-linked `<details>` panel.**
Owner files: `build/build_html.py`, `build/part_16.html`.
Action: emit one static `<details>` per S-ID with an exact source-role legend; no network fetch, no runtime filtering.
Evidence: generated panel.
Exit criterion: panel renders with JS disabled.

**S3.2 — Integrate with search, provenance lens and print.**
Owner files: `build/search_index.py`, `build/style.css`.
Action: search and provenance-lens anchors integrate with the panel; print emits status tags; theme uses semantic labels and links.
Evidence: search payload diff + print page.
Exit criterion: status tags survive print.

**S3.3 — Sample three S-IDs across source classes. [GATE]**
Owner files: `docs/evidence/F08/`.
Action: sample three S-IDs spanning T/K/U/L/LA; confirm page mapping, scope and the text-verification label; verify keyboard disclosure and a text-only fallback.
Evidence: three-sample review sheet.
Exit criterion: all three samples are correctly scoped and labelled.

**Interoperability.** Search and provenance-lens anchors integrate; print emits status tags; theme uses semantic labels and links.

**Failure states and accessibility.** Unknown/conflicting citation remains "unverified"; no invented page or DOI; keyboard disclosure and text-only fallback.

**Integration acceptance.** Sample three S-IDs across T/K/U/L/LA and confirm page mapping, scope, and text-verification label.

**DoD and kill criterion.** **DoD:** no claim is presented as verified based only on metadata. **Kill** if existing F04 covers source roles and the remaining gap is source access, not UI.

---

## F09 — Vector reading prompts attached to selected figures

**ID, value and adoption.** Value 4/5; effort 3/5; priority P3; Adoption Verdict: **[LOW-PRIORITY / DEFER]**.
Historical F07 claims 3–5 "read the figure" prompts on every one of 28 figures; the current source count/hash is unverified.

**Feature type.** Visual active retrieval.

**Utility and target outcome.** Ask learners to identify axes, boundary, arrow or sign before revealing the interpretation.

**Architecture and interaction workflow.** Use the existing `figure_steps.py` and native `<details>` only; prompts reference figure IDs and never reproduce answers in the initial visible summary. No scoring.

### Subtask S1 — Verify figure-step coverage in the current build

**S1.1 — Run the coverage check against the current build. [GATE]**
Owner files: `build/figure_steps.py`, generated master (read-only).
Action: enumerate all figures in the current master (claimed 28) and count existing steps per figure; record the count and the master hash.
Evidence: `docs/evidence/F09/coverage_report.md`.
Exit criterion: a definite per-figure step count bound to a hash.

**S1.2 — Compare against the historical F07 claim.**
Owner files: `docs/evidence/F09/`.
Action: compare the actual counts against the claimed "3–5 prompts on every figure"; list figures that meet, undershoot or exceed the claim.
Evidence: delta table.
Exit criterion: the historical claim is either confirmed or explicitly marked stale.

**S1.3 — Produce the gap list.**
Owner files: `docs/evidence/F09/`.
Action: list figures with zero prompts, and figures whose existing prompts merely restate the caption (these are gaps too, not assets).
Evidence: gap list with rationale.
Exit criterion: every gap has a stated reason.

### Subtask S2 — Select only figures with real interpretation demand

**S2.1 — Apply the selection filter. [GATE]**
Owner files: `build/figure_steps.py`, `docs/evidence/F09/`.
Action: select only figures with genuine spatial/graph interpretation demand — axes meaning, system boundary, arrow direction, sign of a quantity. Exclude decorative and static icons.
Evidence: selected set with inclusion reason per figure.
Exit criterion: no decorative figure is selected.

**S2.2 — Define one question and one explanation per selected figure.**
Owner files: `build/figure_steps.py`.
Action: for each selected figure, write exactly one question targeting the specific interpretation demand and one explanation that carries the answer warrant (why that reading is correct).
Evidence: question/explanation pairs.
Exit criterion: each pair targets a demand, not a caption restatement.

**S2.3 — Record the comprehension-gap evidence.**
Owner files: `docs/evidence/F09/`.
Action: note, per figure, the observable reason a learner would misread it (ambiguous axis, unlabelled arrow, sign not marked).
Evidence: gap rationale per figure.
Exit criterion: selection is evidence-driven, not coverage-driven.

### Subtask S3 — Author, render and integrate

**S3.1 — Add the prompts to `figure_steps.py`.**
Owner files: `build/figure_steps.py`.
Action: add one question and one explanation per gap; prompts reference figure IDs; the initial visible summary never contains the answer.
Evidence: updated step data.
Exit criterion: no answer leaks into the closed summary.

**S3.2 — Render with native `<details>` and equivalent list text.**
Owner files: `build/figures.html`, `build/search_index.py`.
Action: render prompts as native `<details>`; provide an equivalent plain list for print and text-only use; update the search index; no extra widget and no separate SVG.
Evidence: rendered figures + search payload diff.
Exit criterion: print and text-only paths carry the same content.

**S3.3 — Verify IDs, counts, keyboard, zoom and PDF. [GATE]**
Owner files: `docs/evidence/F09/`.
Action: check unique figure IDs, step count against the selected figure set, keyboard reveal, mobile zoom, and that the PDF includes each explanation exactly once; confirm the figure description remains when labels are hidden.
Evidence: verification log + PDF.
Exit criterion: unique IDs, exact count match, explanation appears once in print.

**Interoperability.** Figure workbench (if active), search, print-open `<details>` and captions share one content source.

**Failure states and accessibility.** No prompt on decorative/static icons; answer available by keyboard; figure description remains when labels are hidden; print includes the explanation once.

**Integration acceptance.** Check unique IDs, step count against the selected figure set, keyboard reveal, mobile zoom and PDF.

**DoD and kill criterion.** **DoD:** evidence of a comprehension gap and a clear answer warrant. **Kill** if F07 already supplies equivalent prompts, or if the prompts merely restate captions.

---

## F10 — One-page Latvian thermodynamics quick-reference sheet

**ID, value and adoption.** Value 5/5; effort 2/5; priority P1; Adoption Verdict: **[RECOMMEND ADOPT]**.
The master is long; reports claim a 26-row formula appendix but not whether one-page legibility holds for the current hash. A compact handout supports review only if it is readable.

**Feature type.** Print and exam synthesis.

**Utility and target outcome.** Provide a one-page print reference for sign conventions, key equations, units, conditions and short references to the full derivations.

**Architecture and interaction workflow.** Generate from `notation.json` and verified equations; no manually duplicated values. Dedicated print target with a user-controlled print action and no persistent state.

### Subtask S1 — Verify the current formula card and its print evidence

**S1.1 — Verify present formula card contents and hash. [GATE]**
Owner files: `build/part_16.html`, generated master (read-only).
Action: count the actual rows in the current formula appendix (claimed 26), list them, and record the master hash. Confirm or refute the "26-row" claim.
Evidence: `docs/evidence/F10/formula_card_audit.md`.
Exit criterion: actual row count is known and hash-bound.

**S1.2 — Capture print evidence for the current card.**
Owner files: `build/print_map.py`, `docs/evidence/F10/`.
Action: render the current card to PDF, inspect at 100 %, and measure type size, line height and any clipped formulas.
Evidence: PDF + measurements.
Exit criterion: legibility is measured, not assumed.

**S1.3 — Decide one-page vs two-page on evidence. [GATE]**
Owner files: `docs/evidence/F10/`.
Action: if the required content cannot fit one A4 page at readable type, decide *now* to label the artifact a two-page reference rather than shrinking type below the readable floor.
Evidence: decision record with the measurement that forced it.
Exit criterion: the page-count decision precedes any layout work.

### Subtask S2 — Select equations and source them canonically

**S2.1 — Select equations required by the outcomes.**
Owner files: `build/inventory.json`, `build/notation.json`.
Action: select the equations the seven course outcomes actually require; include assumptions, units and conditions for each; add the sign-convention mini-row from F03.
Evidence: selected equation list mapped to outcomes.
Exit criterion: every selected equation maps to at least one outcome.

**S2.2 — Source all values from canonical rows. [GATE]**
Owner files: `build/notation.json`, `build/build_html.py`.
Action: generate every value from `notation.json` / verified equation rows; no manually maintained duplicates anywhere in the sheet.
Evidence: generator diff showing single-source values.
Exit criterion: changing a canonical row changes the sheet.

**S2.3 — Order rows for review flow.**
Owner files: `build/build_html.py`.
Action: order rows by outcome/chapter so the sheet reads as a revision path, and attach a short reference or link to the full derivation for each row.
Evidence: ordered row list with derivation links.
Exit criterion: each row has a derivation reference.

### Subtask S3 — Render, test and link

**S3.1 — Render the A4 print target and test minimum type. [GATE]**
Owner files: `build/print_map.py`, `build/style.css`.
Action: render a dedicated A4 print target; enforce a minimum type size (no reduction below the readable floor, e.g. ≥ 9 pt body / ≥ 12 px equivalent); confirm no formula is clipped.
Evidence: PDF + type measurements.
Exit criterion: no clipped formula and no sub-floor type.

**S3.2 — Handle the impossible case and protect the HTML source.**
Owner files: `build/style.css`, `build/print_map.py`.
Action: if one page is impossible, label the artifact a two-page reference; ensure the accessible HTML remains the source of truth and that theme styles do not leak into print.
Evidence: label + print CSS isolation check.
Exit criterion: print output is theme-independent.

**S3.3 — Link, map and verify against source. [GATE]**
Owner files: `build/part_16.html`, `build/print_map.py`, `build/style.css`.
Action: link the sheet from course navigation and the print TOC; confirm the print map and total page count; compare every formula row against `notation.json` and record the hash binding.
Evidence: link list, page count, row-by-row comparison.
Exit criterion: all formulas accurate, legible, sourced and hash-bound.

**Interoperability.** Print TOC and search link to the sheet; the screen retains normal reading; theme styles are not leaked into print.

**Failure states and accessibility.** No reduction below readable type; one page must not force clipped formulas; if impossible, label as a two-page reference; accessible HTML remains the source.

**Integration acceptance.** Compare each formula row to source/notation; render the PDF and visually inspect at 100 %; confirm the map and total page count.

**DoD and kill criterion.** **DoD:** all formulas accurate, legible, sourced and hash-bound. **Kill** if the existing A.1 card meets the one-page visual and content criteria.

---

# PART B — Bug-fixing, wiring, debloating & false-claim tasks (B01–B05)

## B01 — Bring output size under the 2 MiB ceiling

**Category / severity / status:** Code & asset debloat; High; **[CONFIRMED DEFECT]** [TESTED].

**Evidence and reproduction.** `Master_4_temats_termodinamika.html` is 2,386,187 B, exceeding 2,097,152 B (`AGENTS.md` §4). Reproduce with `wc -c < Master_4_temats_termodinamika.html`. It is one generated artifact, so removal by hand is forbidden.

**Root-cause hypothesis / propagation.** A large inline stylesheet, executable JS, repeated SVG/markup and JSON data islands accumulate in source fragments → `build/build_html.py` embeds them → the final file exceeds budget. The root shares architecture with T18/T19; the exact contribution by component requires a byte-profile report.

### Subtask S1 — Read-only byte profiling

**S1.1 — Add byte profiling by section and tag type. [GATE]**
Owner files: `build/build_html.py` (profiling only, output unchanged).
Action: instrument the generator to emit a read-only profile: bytes per source fragment and per tag type (`<style>`, `<script>`, `<svg>`, JSON data islands, plain markup). The generated master must be byte-identical when profiling is off.
Evidence: `docs/evidence/B01/byte_profile_baseline.txt`.
Exit criterion: profile runs without altering output.

**S1.2 — Record the baseline.**
Owner files: `docs/evidence/B01/`.
Action: run `python3 -I build/build_html.py`, then record `wc -c` (2,386,187 B) and `sha256sum` of the master alongside the profile.
Evidence: baseline size + hash + profile.
Exit criterion: baseline is reproducible from a clean run.

**S1.3 — Identify duplication hotspots.**
Owner files: `docs/evidence/B01/`.
Action: from the profile, rank the top contributors and quantify duplication: repeated CSS rule blocks, identical inline SVG markup, repeated JSON keys, dead runtime code.
Evidence: ranked hotspot list with byte counts.
Exit criterion: each planned reduction in S2 maps to a measured hotspot.

### Subtask S2 — Reduce duplication in canonical owners

**S2.1 — Deduplicate the stylesheet.**
Owner files: `build/style.css`, `build/build_html.py`.
Action: extract repeated rules into shared classes; remove duplicate declarations across fragments; verify no visual regression by before/after screenshots.
Evidence: CSS diff + screenshots.
Exit criterion: byte reduction recorded with no visual change.

**S2.2 — Reuse identical SVG symbols.**
Owner files: `build/figures.py`, `build/part_*.html`, `build/build_html.py`.
Action: convert repeated inline SVG markup to a `<symbol>`/`<use>` sprite; keep accessible names and descriptions intact.
Evidence: SVG diff + a11y check.
Exit criterion: identical rendering with fewer bytes.

**S2.3 — Trim Python-generated data and runtime JS.**
Owner files: `build/build_html.py`, `build/script.js`.
Action: remove duplicated generated data (emit once, reference by ID), and restrict runtime JS to the approved whitelist; delete dead functions.
Evidence: data/JS diff.
Exit criterion: no approved behaviour is lost.

### Subtask S3 — Regenerate and gate

**S3.1 — Regenerate and compare bytes. [GATE]**
Owner files: `build/build_html.py`.
Action: run `python3 -I build/build_html.py`; compare section and total bytes against the baseline profile; confirm the total is ≤ 2,097,152 B with the same course concepts, provenance and accessible static fallback.
Evidence: before/after profile + `wc -c`.
Exit criterion: total ≤ ceiling.

**S3.2 — Add the build-time ceiling gate.**
Owner files: `build/build_html.py`, `tools/check_html.py`.
Action: fail the build above the ceiling with a useful per-section report rather than a bare number.
Evidence: gate code + failing-run output.
Exit criterion: an over-budget build cannot silently succeed.

**S3.3 — Verify boundary conditions. [GATE]**
Owner files: `docs/evidence/B01/`.
Action: confirm UTF-8 Latvian text, SVG and JSON remain valid; no generated field is silently dropped; record the generated HTML hash, offline check, source/calc counts, and viewport + print regression.
Evidence: validation report + hash.
Exit criterion: size reduction with zero content loss.

**Before / after.** Before 2.386 MB (> 2 MiB); target after ≤ 2,097,152 B with the same course concepts, provenance and accessible static fallback.

**Regression / DoD.** Positive: generated file at or below cap. Negative: a fixture that adds > budget fails with a useful report. Boundary: UTF-8 Latvian/SVG/JSON remains valid and no generated field is silently dropped. Require generated HTML hash, offline check, source/calc counts, viewport and print regression. No acceptance until the capture contract is met.

---

## B02 — Remove inline event attributes and unsafe data-to-HTML rendering

**Category / severity / status:** Broken wiring / code debloat; Critical; **[CONFIRMED DEFECT]** [TESTED].

**Evidence and reproduction.** A static parse of the current master finds 67 event attributes (the AGENTS snapshot counted 62); a string scan finds 40 `innerHTML` and 52 `createElement` calls in the executable bundle. Reproduce with an HTML parser and `rg -n 'onclick=|innerHTML|createElement' build/part_*.html build/script.js`. The agreed future contract bans inline `on*=` and DOM templating.

**Root-cause hypothesis / propagation.** Historical modules bind behaviour by inline handlers and generate UI from arrays in JS; the build output inherits these patterns, creating a large stateful runtime and duplicated UI ownership. This diagnosis does not claim every call is exploitable or broken — it is contract nonconformance.

### Subtask S1 — Inventory and classify every handler

**S1.1 — Enumerate all inline event attributes. [GATE]**
Owner files: read-only parse of generated master and `build/part_*.html`.
Action: parse with a real HTML parser (not regex) and list every `on*=` attribute with its element, ID and originating fragment; reconcile the 67 vs 62 count difference.
Evidence: `docs/evidence/B02/handler_inventory.csv`.
Exit criterion: every attribute has an owner file and element ID.

**S1.2 — Scan and map the templating calls.**
Owner files: `build/script.js`, `build/part_*.html`.
Action: locate all 40 `innerHTML` and 52 `createElement` calls; map each to a module and classify the intended ownership as CSS / native HTML / Python build-time / runtime.
Evidence: call map with ownership classification.
Exit criterion: no call is left unclassified.

**S1.3 — Produce the migration strategy per control.**
Owner files: `docs/evidence/B02/`.
Action: for each control, name the replacement: native element (`<details>`, checkbox, `:target`, `:checked`), CSS-only state, Python-rendered markup, or a whitelisted runtime function.
Evidence: strategy table.
Exit criterion: every control has exactly one target owner.

### Subtask S2 — Migrate rendering and behaviour

**S2.1 — Render data-bearing markup in Python. [GATE]**
Owner files: `build/build_html.py`, `build/part_*.html`.
Action: move all array-driven UI generation from JS into build-time Python output; remove the JS data islands that only existed to hydrate markup.
Evidence: before/after fragment diff.
Exit criterion: no data array is hydrated in the browser.

**S2.2 — Replace state toggles with native semantics.**
Owner files: `build/part_*.html`, `build/style.css`.
Action: convert show/hide and open/closed toggles to `<details>`, checkboxes, `:target` or `:checked` wherever semantics permit; keep keyboard operability.
Evidence: converted controls list + keyboard test.
Exit criterion: converted controls work without JS.

**S2.3 — Retain only whitelisted runtime code.**
Owner files: `build/script.js`, `build/build_html.py`.
Action: reduce the executable bundle to the approved whitelist; consolidate remaining behaviour into one delegated module with zero inline attributes.
Evidence: final script diff + whitelist.
Exit criterion: bundle contains only whitelisted functions.

### Subtask S3 — Gates and regression

**S3.1 — Add parser gates for the banned patterns. [GATE]**
Owner files: `tools/check_html.py`, `build/build_html.py`.
Action: gate 1 — zero inline event attributes in output; gate 2 — zero banned output-templating APIs (`innerHTML`, `createElement`, `insertAdjacentHTML`) in output.
Evidence: gate code + clean-run output.
Exit criterion: both gates pass on the regenerated master.

**S3.2 — Add negative fixtures.**
Owner files: `tools/check_html.py`, `docs/evidence/B02/`.
Action: a fixture containing `onclick` must fail; a fixture containing `innerHTML` must fail; each failure must name the file and line.
Evidence: failing-fixture output.
Exit criterion: gates fail loudly and specifically.

**S3.3 — Verify behaviour preservation. [GATE]**
Owner files: `docs/evidence/B02/`.
Action: confirm hidden/closed answers remain closed until user action, JS-off text remains, and no IDs or listeners are missing at runtime before vs after; capture falkon/falkon screenshots for all UI changes.
Evidence: before/after runtime check + screenshots.
Exit criterion: identical behaviour, zero inline handlers.

**Before / after.** Before 67 handlers and templating calls in the bundled runtime; target zero inline event attributes and no data-array DOM hydration.

**Regression / DoD.** Positive: each supported control has one valid native or whitelisted handler. Negative: a fixture with `onclick` or `innerHTML` fails. Boundary: hidden/closed answers remain closed until user action, and JS-off text remains. Confirm no missing IDs/listeners at runtime before/after; all UI changes need falkon/falkon screenshots.

---

## B03 — Reconcile Chapter 9 numbering, order and recall-count drift

**Category / severity / status:** Runtime/layout and content structure; High; **[DIAGNOSTIC INVESTIGATION]** [INSPECTED].

**Evidence and reproduction.** `AGENTS.md` OI-02/OI-03 cites duplicate 9.10 headings, a 9.9 calculator placed before 9.5 conclusions, and recall-count drift (125 text prompts vs 126 tags; manifest 127 vs 126). A historical report later says numbering/gates changed. First reproduce against the current master and fragments: extract headings in source order, IDs, recall item labels, tagged count, `inventory.json`, the `search_index.py` manifest and the generated search payload.

**Root-cause hypothesis / trace.** A one-off insertion/renumber operation, or separate counting sources, may have shifted chapter order and count manifests. Because source files and current output may have diverged, no exact active defect is declared until source and output agree on evidence.

### Subtask S1 — Build the read-only mismatch report

**S1.1 — Extract and compare heading sequences. [GATE]**
Owner files: read-only extraction from `build/part_*.html` and the generated master.
Action: extract headings in source order from fragments and from the master; extract section IDs; diff the two sequences and flag duplicates (e.g. two 9.10 headings) and ordering violations (9.9 before 9.5).
Evidence: `docs/evidence/B03/mismatch_report.md`.
Exit criterion: the report states whether each historical finding reproduces on the current hash.

**S1.2 — Reconcile the recall counts.**
Owner files: `build/inventory.json`, `build/search_index.py`, generated master.
Action: count recall items four ways — text prompts, tags, manifest value, generated search payload — and record the deltas against the historical 125/126/127/126 figures.
Evidence: count reconciliation table.
Exit criterion: every count has a source and a number.

**S1.3 — Declare defect or closed. [GATE]**
Owner files: `docs/evidence/B03/`.
Action: state explicitly which findings reproduce on the current hash and which are already closed by later revisions. No repair is scheduled for a finding that does not reproduce.
Evidence: verdict per finding.
Exit criterion: the repair scope in S2 covers only reproduced findings.

### Subtask S2 — Designate one source of truth and fix ordering

**S2.1 — Designate a single numbering/count source. [GATE]**
Owner files: `build/build_html.py`, `build/search_index.py`, `build/inventory.json`.
Action: make one Python component the authority for section numbers and recall counts (derived from fragment order at build time); deprecate all other counters so they cannot drift.
Evidence: ownership note + code diff.
Exit criterion: exactly one component emits numbers/counts.

**S2.2 — Fix fragment ordering and renumber.**
Owner files: `build/part_*.html` (Chapter 9 fragments), `build/build_html.py`.
Action: move the 9.9 calculator after the 9.5 conclusions and renumber to unique, monotone values; keep intentional aliases and back-references explicitly marked so they are not counted as duplicate sections.
Evidence: reordered fragment diff.
Exit criterion: heading sequence is unique and monotone.

**S2.3 — Reconcile the recall manifest.**
Owner files: `build/inventory.json`, `build/search_index.py`.
Action: make text prompts, tags, manifest and generated payload agree on one number; document the counting rule (what counts as a recall item).
Evidence: reconciled counts + counting rule.
Exit criterion: all four counts are equal.

### Subtask S3 — Add gates and inspect output

**S3.1 — Add non-monotone and count-equality gates. [GATE]**
Owner files: `tools/check_html.py`, `build/build_html.py`.
Action: gate A — section numbers must be unique and monotone within each chapter; gate B — recall counts must be equal across manifest and generated payload. Both gates record source and output hashes.
Evidence: gate code + passing run.
Exit criterion: both gates pass on the regenerated master.

**S3.2 — Add negative tests.**
Owner files: `tools/check_html.py`, `docs/evidence/B03/`.
Action: a fixture with duplicated numbering fails gate A; a fixture with one missing recall item fails gate B.
Evidence: failing-fixture output.
Exit criterion: both gates fail loudly.

**S3.3 — Inspect TOC, print sequence and hash.**
Owner files: `docs/evidence/B03/`.
Action: inspect the generated TOC and the print sequence for correct order; record the current master hash; note which old findings are documented as already closed.
Evidence: TOC/print screenshots + hash.
Exit criterion: output order matches source order and the record is hash-bound.

**Before / after.** Before: reported conflicts, current applicability unknown. After: unique monotone section numbers and reconciled counts — or a report documenting which old finding is already closed.

**Regression / DoD.** Positive: each chapter heading sequence and count manifest match. Negative: duplicated numbering or one missing recall item makes the gate fail. Boundary: intentional aliases/back-references do not count as duplicate sections. Inspect generated TOC, print sequence and current hash.

---

## B04 — Verify or withdraw unsupported scientific and learning claims

**Category / severity / status:** False-claim/source investigation; Critical; **[DIAGNOSTIC INVESTIGATION]** [INSPECTED]/[UNVERIFIED].

**Evidence and reproduction.** `AGENTS.md` OI-06 flags BMR/TDEE, ischemia, ATP/Mg²⁺ additions, and a ">250 %" Roediger–Karpicke claim in Appendix H, §§8, 10–11, `part_15.html` and `part_16.html`. Search the exact phrases and trace source IDs, bibliography entries, editions, pages, and whether accessible source text supports the exact context.

**Root-cause hypothesis / propagation.** Claims may have been added from secondary summaries, or from a source whose population/regime differs; citation metadata or adjacent terminology might be mistaken for evidence of a causal or quantitative conclusion.

### Subtask S1 — Build claim records

**S1.1 — Extract exact wording and location for each flagged claim. [GATE]**
Owner files: read-only extraction from Appendix H, §§8, 10–11, `build/part_15.html`, `build/part_16.html`.
Action: copy the exact sentence for each flagged claim (BMR/TDEE, ischemia, ATP/Mg²⁺, ">250 %") with its section, anchor and source ID. No paraphrase.
Evidence: `docs/evidence/B04/claim_records.md`.
Exit criterion: every flagged claim has verbatim text and a location.

**S1.2 — Record population, system, conditions and cited passage.**
Owner files: `docs/evidence/B04/`.
Action: for each claim, record the target population/system, the conditions under which it is asserted, and the cited passage (bibliography entry, edition, page if inspected).
Evidence: per-claim condition block.
Exit criterion: scope is explicit for every claim.

**S1.3 — Classify each claim. [GATE]**
Owner files: `docs/evidence/B04/`.
Action: classify as supported / partially supported / unsupported / unverifiable, with the reason. "Partially supported" must name the condition that is *not* covered.
Evidence: classification table.
Exit criterion: no claim is left unclassified.

### Subtask S2 — Seek and assess evidence

**S2.1 — Seek primary, peer-reviewed or official evidence.**
Owner files: `docs/evidence/B04/`.
Action: for each claim, look for primary/peer-reviewed or official sources; record what was found, what was not, and the search scope.
Evidence: evidence log per claim.
Exit criterion: each claim has a documented evidence search.

**S2.2 — Test whether the accessible source text supports the exact context. [GATE]**
Owner files: `docs/evidence/B04/`.
Action: confirm that the source's population, regime and quantitative value match the claim's. A source supporting only a partial condition cannot verify the full claim.
Evidence: context-match assessment.
Exit criterion: full-context support is proven or explicitly absent.

**S2.3 — Record the verification layer.**
Owner files: `docs/evidence/B04/`.
Action: label each claim's verification layer: *text-level* (source text inspected) or *metadata-only* (citation exists, text not inspected). Metadata-only never counts as verified.
Evidence: verification-layer column.
Exit criterion: no claim is verified on metadata alone.

### Subtask S3 — Correct, scope, label or remove

**S3.1 — Apply the correct disposition per claim. [GATE]**
Owner files: `build/part_15.html`, `build/part_16.html`, Appendix H.
Action: for each claim, either correct it, scope it to the supported condition, label it "papildinājums/jāpārbauda", or remove it. Update the claim links accordingly.
Evidence: before/after text diff per claim.
Exit criterion: no unsupported statement remains unlabelled.

**S3.2 — Strip unsupported precision.**
Owner files: `build/part_15.html`, `build/part_16.html`.
Action: remove any page number or exact numeric percentage (e.g. ">250 %") that is not backed by inspected source text.
Evidence: precision audit.
Exit criterion: zero unbacked numbers or page references.

**S3.3 — Reviewer sign-off and QA update. [GATE]**
Owner files: `docs/evidence/B04/`, QA record.
Action: require reviewer sign-off and a bibliography metadata review; update the QA record, claim links and hashes.
Evidence: signed review sheet + updated hashes.
Exit criterion: every claim has text-level support and stated applicability, or is clearly unresolved/removed.

**Before / after.** Before: material claims are flagged without warrant. After: each has text-level support and applicability, or is clearly unresolved/removed.

**Regression / DoD.** Positive: a supported claim retains a matching scoped citation. Negative: a source that supports only a partial condition cannot verify the full claim. Boundary: no page numbers or exact numeric percentage without inspected source text. Require reviewer and bibliography metadata review.

---

## B05 — Trace current interaction wiring and unreachable paths before repair

**Category / severity / status:** Diagnostic risk investigation; High; **[DIAGNOSTIC INVESTIGATION]** [UNVERIFIED].

**Evidence and reproduction.** The current output has 535 `<button>` tags, 67 inline event attributes, 4 dialogs, 73 popover matches, 16 `localStorage` string matches and one executable script; none of these counts proves behaviour. Instrument one control per class: trigger → handler → state → storage → DOM; check console errors, missing selectors, failed anchors and the disabled-script fallback. Avoid executing a destructive build or an old probe before its effects are read.

**Root-cause hypothesis / propagation.** Concurrent revisions and one central script may leave selectors or listeners stale; separate report evidence can concern older HTML. An actual failure is not asserted until it is reproducible on the current hash.

### Subtask S1 — Generate the static inventory

**S1.1 — Build the selector/event/storage inventory. [GATE]**
Owner files: read-only scan of generated master, `build/script.js`, `build/part_*.html`.
Action: enumerate 535 buttons, 67 inline handlers, 4 dialogs, 73 popover matches, 16 `localStorage` matches and the single script; bind each count to the current master hash.
Evidence: `docs/evidence/B05/inventory.csv` + hash.
Exit criterion: every count is hash-bound.

**S1.2 — Map control classes to their full path.**
Owner files: `docs/evidence/B05/`.
Action: for each control class, trace trigger → handler → state → storage → DOM; flag controls with no handler, handlers with no control, and dead selectors.
Evidence: path map with orphan flags.
Exit criterion: no control class is untraced.

**S1.3 — Identify static failure candidates.**
Owner files: `docs/evidence/B05/`.
Action: from the map, list failed-anchor candidates, missing selectors and likely console errors, plus the expected disabled-script fallback for each.
Evidence: candidate defect list.
Exit criterion: candidates are ranked by risk before any probe runs.

### Subtask S2 — Run bounded probes

**S2.1 — Verify runner side effects and visual policy first. [GATE]**
Owner files: `docs/evidence/B05/`.
Action: before executing any probe, confirm what the runner writes, whether it can trigger a build, and whether screenshots are permitted; read the effects of any legacy probe before reusing it.
Evidence: runner safety note.
Exit criterion: no probe runs without a known side-effect profile.

**S2.2 — Instrument one control per class.**
Owner files: `docs/evidence/B05/`.
Action: for each class, trigger the control and record the full chain (trigger → handler → state → storage → DOM), console errors, missing selectors, failed anchors and the disabled-script fallback behaviour.
Evidence: per-class trace logs.
Exit criterion: one complete trace per control class.

**S2.3 — Capture evidence per path.**
Owner files: `docs/evidence/B05/`.
Action: store a trace log and, where visual policy allows, a screenshot for each probed path; record the master hash for every probe run.
Evidence: trace + screenshot set with hashes.
Exit criterion: every probed path is reproducible on a stated hash.

### Subtask S3 — Classify and open follow-ups

**S3.1 — Classify every path. [GATE]**
Owner files: `docs/evidence/B05/`.
Action: label each path working, broken, duplicate, dead or inaccessible, with the trace evidence that justifies the label.
Evidence: classification table.
Exit criterion: every high-risk workflow has a current-hash trace and either a reproducible defect or explicit pass evidence.

**S3.2 — Open follow-up defect IDs.**
Owner files: `docs/evidence/B05/`, defect register.
Action: for each non-working path, open a new defect ID with the trace evidence attached; do not repair inside B05.
Evidence: new defect IDs.
Exit criterion: no repair is attempted without its own task ID.

**S3.3 — Verify boundary conditions and keep gates separate. [GATE]**
Owner files: `docs/evidence/B05/`.
Action: confirm that with no storage consent the in-memory use still works, and that JS-off remains readable; keep keyboard, theme, 320 px, print and screen-reader checks as separate gates rather than folding them into this trace.
Evidence: boundary check notes.
Exit criterion: no storage consent still yields usable in-memory behaviour; JS-off reading intact.

**Before / after.** Before: known architecture inventory but no current end-to-end state trace. After: every high-risk workflow has a current-hash trace and a reproducible defect or explicit pass evidence.

**Regression / DoD.** Positive: one trigger mutates the expected state and DOM. Negative: a missing selector or blocked storage is handled without an uncaught error. Boundary: no storage consent preserves in-memory use; JS-off remains readable. Keyboard, theme, 320 px, print and screen-reader checks remain separate gates.

---

## 5. Consolidated evidence register

| Task | Required evidence artifacts |
|---|---|
| F03 | `course_convention.txt`, `iupac_convention.txt`, `notation.json` diff, arithmetic test, 320/1440/print screenshots |
| F04 | `duplicate_check.md`, data inventory, assumption block, worked example, hand-vs-Python comparison, worksheet PDF |
| F05 | `js_dependence_map.md`, static fallback fragment, network log (0 external), `tools/check_html.py`, lite-shot no-JS screenshot, SR review |
| F06 | dataset-to-card map, range fields, sign-case table, computation log with guards, sign-flip test, print caption |
| F07 | outcome list, existing-anchor inventory, `coverage_table.html` comparison, mapping JSON, reload screenshot |
| F08 | field-presence table, gap classification, verdict, `source_claims.json` (conditional), validation table, three-sample review |
| F09 | `coverage_report.md`, delta table, gap list, selection rationale, verification log, PDF |
| F10 | `formula_card_audit.md`, print measurements, page-count decision, row-by-row source comparison, hash binding |
| B01 | `byte_profile_baseline.txt`, before/after profile, `wc -c`, gate output, validation report |
| B02 | `handler_inventory.csv`, call map, strategy table, gate output, failing fixtures, falkon/falkon screenshots |
| B03 | `mismatch_report.md`, count reconciliation, verdict per finding, gate output, TOC/print screenshots |
| B04 | `claim_records.md`, classification table, evidence log, context-match assessment, before/after diffs, signed review |
| B05 | `inventory.csv`, path map, candidate list, runner safety note, per-class traces, classification table, new defect IDs |

## 6. Rollback and safety

1. Every task regenerates through `python3 -I build/build_html.py`; the previous master and its `sha256sum` are archived before any regeneration.
2. No task edits a generated artifact directly; a hand-edit found in review invalidates the task's DoD.
3. B01's profiler and B02's parser gates run on every merge, so a regression in size or contract fails the build rather than reaching review.
4. Diagnostic tasks (B03, B05) and deferred features (F04, F08, F09) may close without code changes; a documented "already closed / duplicate / not warranted" verdict with evidence is a valid completion.
5. Any task whose kill criterion triggers is closed with the evidence link, and the finding is recorded so a later task does not re-open it blindly.
