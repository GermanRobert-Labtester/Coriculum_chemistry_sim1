# PLAN — 20 tasks, 10 features, 5 bug fixes, wiring, debloating, false-claim removal, sources

Workspace: `/home/robertsrff/Chemistry_Med/Chemistry_5` (Medical Chemistry, RSU, topic 5: kinetics and catalysis)
Written: 2026-11-02. Author: Claude (inspection session). Language of this plan: English. Language of the product it plans to change: **Latvian** (`lang="lv"`), and it stays Latvian.

This is a **plan**, not a change. Nothing in the workspace was edited while writing it. The only file created is this one.

---------------------------------------------------------------------

## 0. How to read this file, and how far to trust it

### 0.1 What I actually did (evidence base)

| Action | Result |
|---|---|
| Listed every file, measured sizes | 311 files, 11 MB (`du -sh`). 6 source PDFs; 1 master HTML (864,806 B, 3,884 lines); 24 scripts in `tools/`, 7 verifier wrappers plus `run_all.py` in `verify/`; `workspace_skills/` is 39 entries (36 skill folders + `INDEX.md`, `COPY_MANIFEST.json`, one precedent HTML), 6.3 MB. |
| Read in full | `AGENTS.md`, `DESIGN.md`, `CHECKS.md`, `language_log.md`, `notation.md`, `workspace_skills/INDEX.md`, first 6 KB of `PROMPT_master_kinetika.md` |
| Sampled | `glossary.csv/json`, `termbase.json`, `numbers.json`, `provenance_inventory.csv` (structure only) |
| Re-ran static verifiers on the current HTML | `verify_links`, `verify_tables`, `verify_text --strict`, `verify_terms`, `verify_numbers`, `verify_provenance --strict`, `verify_design`, `verify_figures`, `verify_a11y`, `verify_selfcheck`: **all printed `RESULT: PASS`**. SHA-256 of the HTML matches `CHECKS.md` (`02e2d987…eff8`). |
| Rendered the page | headless Chrome screenshots at 1440 px and 390 px; headless console check (`--dump-dom`, 4 s virtual time): **no console messages** |
| Counted structure per chapter | script in §1.2 |
| Web research | 8 searches (standard mode): catalogue records for books, IUPAC Gold Book, Briggs–Haldane / Michaelis–Menten bibliographic data, catalase and H₂O₂ activation energies, thiosulfate-clock teaching literature |

### 0.2 What I did NOT do (so you do not over-trust this plan)

* I did **not** run `node tools/check_a11y.mjs`, `verify/verify_print.py`, `tools/check_print.py`, `lint.mjs`, `inspect.mjs` or `verify/run_all.py`. Their results below are quoted from `CHECKS.md`, not reproduced.
* I did **not** read any book. Every book entry in §9 comes from a library or retailer catalogue record returned by a search. **No chapter number, page number or quotation from a book was verified.** Where I name a chapter I say "verify". An agent that cites a book page in the HTML without opening the book breaks `AGENTS.md` §10 rule 2.
* I did **not** open the six PDFs again; I rely on `AGENTS.md` §5 and on `CHECKS.md` §6 (source hashes, one of which I recomputed: `Kinetika.pdf` matches).
* I did not read all 3,884 lines of the HTML. I read the masthead, chapter 0 head, the structure of every chapter, and targeted passages (catalase, Berzelius, √T, lab MnO/MnO₂, change log). Findings marked **[verified]** were seen in the file or a tool output in this session; **[suspected]** need a first step of confirmation, which each task includes.
* Web search quality is uneven. Some hits were spam mirrors; I used only catalogue and institutional pages and marked disagreements.

### 0.3 Rules every task below inherits (from `AGENTS.md` §10, restated because agents skip them)

1. Never modify, move or delete the six PDFs or anything in `workspace_skills/`.
2. The workspace has **no git** [verified: no `.git`]. New outputs get new file names; edits to the master HTML are made on a copy first (see W01).
3. No invented science, data, page numbers or answer keys. Unknown stays `nav zināms`.
4. Every number in the HTML comes from `numbers.json` (`data-num` spans). Recompute with `tools/build_numbers.py`, then `verify_numbers`.
5. Offline and self-contained: no CDN, no `fetch`, no storage, no web font from a URL.
6. Four separate claims in every report: static validity, visual quality, source fidelity, scientific correctness. State what was run and what was not.
7. Provenance tags (`avots`, `labojums`, `papildinājums`, `autora atbilde`) on every non-trivial statement; anything new from a book is **papildinājums**, with the book named.

### 0.4 ID scheme (new, so it does not collide with the existing `T01–T20` of the previous build)

`N01–N20` tasks · `F01–F10` features · `B01–B05` bugs · `W01–W06` wiring · `D01–D08` debloating · `C01–C11` false claims.

---------------------------------------------------------------------

## 1. Verified snapshot of the current state

### 1.1 What is solid (do not break it)

| Area | Evidence |
|---|---|
| All 10 static verifiers pass; negative fixtures prove they can fail (7 fixtures in `verify/fixtures/`) | re-run + `CHECKS.md` §2 |
| 211 computed numbers, 423 `data-num` spans, 0 unwrapped copies | `verify_numbers` |
| 36 defect rows (K1–K28, L1–L7) each anchored; provenance strict mode has 0 errors, 0 warnings | `verify_tables`, `verify_provenance` |
| 47 Q&A items, 45 four-part common-error blocks; 40 answers (22 lecture + 11 MU + 6 lab = 39, plus 1 extra) | `verify_selfcheck` |
| Accessibility groundwork: 1 `h1`, skip link, 38 formulas with text alternatives, 4 instruments with live regions, reduced-motion and forced-colours CSS | `verify_a11y`, `DESIGN.md` §11 |
| No console output in headless Chrome | my run |
| Honest reporting culture: `CHECKS.md` §4 lists what was not run; `DESIGN.md` §11 lists known limits | files |

### 1.2 Structure per chapter (measured by me)

| Ch | Title | SVG | `<figure>` | Tables | MathML | Q&A | Size kB |
|---|---|---|---|---|---|---|---|
| 0 | Lasīšanas norādes | 0 | 0 | 0 | 0 | 0 | 6 |
| 1 | Reakcijas ātrums | **0** | 0 | 0 | 1 | 0 | 9 |
| 2 | Kas nosaka ātrumu | **0** | 0 | 1 | 0 | 0 | 5 |
| 3 | Aktīvo masu likums | **0** | 0 | 0 | 1 | 0 | 5 |
| 4 | Sadursmes un barjera | 4 | 3 | 0 | 2 | 0 | 67 |
| 5 | Temperatūra | **0** | 0 | 1 | 3 | 0 | 13 |
| 6 | Pakāpe, molekularitāte, pusperiods | 6 | 6 | 3 | 2 | 0 | 131 |
| 7 | Reakciju mehānismi | 1 | 1 | 1 | 0 | 0 | 15 |
| 8 | Katalīze | **0** | 0 | 2 | 0 | 5 | 15 |
| 9 | Fermenti | 1 | 1 | 1 | 0 | 0 | 14 |
| 10 | Fermentu kinētika | 3 | 2 | 1 | 6 | 1 | 61 |
| 11 | Inhibīcija | 1 | 1 | 2 | 2 | 1 | 37 |
| 12 | Laboratorijas darbs | 3 | 1 | 4 | 5 | 0 | 48 |
| 13 | Avotu labojumu reģistrs | 0 | 0 | 2 | 0 | 0 | 43 |
| 14 | Terminoloģijas korektors | 0 | 0 | 1 | 0 | 0 | 54 |
| 15 | Pašpārbaude | 0 | 0 | 1 | 0 | 40 | 93 |
| 16 | Formulu lapa | 6 | 0 | 2 | 16 | 0 | 19 |
| 17 | Avoti un izmaiņu žurnāls | 0 | 0 | 7 | 0 | 0 | **124** |

Whole file: 25 `<svg>` tags, 29 tables, 65 `<details>` (15 open in markup), 23 `<math>`, 2 `<script>` blocks (53 KB), 39.9 KB inline CSS, 124 print pages (default), 30 (worksheet), 102 (exam).

Three readings of this table drive the plan:

1. **Five core-theory chapters have no figure at all**: reaction rate (1), what controls rate (2), mass action (3), temperature/Arrhenius (5) and catalysis (8). Chapter 5 even teaches the Arrhenius equation without a single plot of `k` against `T` or `ln k` against `1/T` [verified: 0 SVG in the chapter]. Chapter 8 teaches catalysis with no catalysed-versus-uncatalysed profile inside the chapter itself (the profile lives in chapter 4).
2. **Chapter 17 is 124 kB = 14 % of the file** and it is the developer's change log, not study material.
3. **Chapters 2, 3, 5, 8, 9 are 5–15 kB each**, while 4, 6, 10 are 61–131 kB. The depth is lopsided toward the parts that have instruments.

### 1.3 Things I saw on screen

* 1440 px: the masthead is calm and legible; the legend sits right of the standfirst, six source cards in three columns, then a two-column contents list whose right column is short, then roughly 100 px of blank before chapter 0. It reads as a monograph, not as a template. It is also **a lot of furniture before the first sentence of science**: roughly 900 px of masthead, sources and contents come before chapter 0.
* 390 px: legend, six sources and 18 contents entries stack, so **about 1.5 screens pass before any teaching**. The skip link exists but the reader of a phone sees the furniture first.
* Prose is serif, labels sans, one ink, teal and bordeaux. No gradients, shadows, pills, emoji. The anti-slop direction is already largely achieved; the remaining slop is subtler (see N15).

---------------------------------------------------------------------

## 2. Order of work and dependencies

```
W01 (snapshot/version control)  ──►  everything
N05 (leak purge) + D01 (move change log) ──► N03/N04 (language passes work on a smaller file)
N01 (terminology spine) ──► N02, N03, N10(lexicon), N17
N06 (science audit vs books) ──► N07 (lab), N08 (self-check), N17, N20
N20 (SVG program) ◄── N19 (texture system) ◄── N16 (restyle tokens)
N13 (instruments) ──► F01–F10
B01–B05, C01–C12 can run in parallel with the above
```

Suggested waves: **Wave 0** W01, C-series, D01/D02. **Wave 1** N01, N05, N06, B-series. **Wave 2** N02–N04, N07, N08, N17, N18. **Wave 3** N09–N16, N19. **Wave 4** N20 and F-series. **Wave 5** W02–W06, final audit.

---------------------------------------------------------------------

## 3. THE 20 TASKS

Each task has: what it tries to accomplish; evidence; files; **3 substeps**; **2–3 subtasks, each with 3 substeps**; features folded in; acceptance; definition of done. "Agent" means any AI coding agent given this file.

### Category A — Terminology (N01–N04)

---

### N01 · Terminology spine: one authority for every Latvian term

**Accomplishes.** The document, the glossary, the termbase, `notation.md` and `AGENTS.md` §6 currently describe the vocabulary in four places. A student sees one; a maintainer must keep four in step. N01 makes `termbase.json` the single source and generates the others, and settles the open linguistic choices with external authority rather than by internal decision.

**Evidence.**
* `termbase.json` has **71** terms [verified]; `glossary.csv` has **63** entries (64 lines incl. header) [verified]; `AGENTS.md` §6 lists 17 rows. The 8-term gap between termbase and glossary is either intentional (terms to avoid) or drift. `verify_terms.py` passes either way, so it does not check this.
* `termbase.json` meta carries a `caveat` beginning "AGENTS.md §6 has 17 r…": the previous builder already noticed the two disagree.
* Open choices recorded in `language_log.md`: `pakāpe`/`kārta`; `Mihaelisa–Mentenas` (house spelling, T01); `nekonkurentā` vs `nekonkurējošā (uncompetitive)`; `Īkšķa noteikums` ("calque, kept"); `ātruma konstante`.
* `verify_terms` reports two benign warnings (`maksvela-bolcmana`, `aktivais-komplekss`: symbol without unit).
* Language checks: no Latvian dictionary was installed during the earlier pass (`language_log.md`), so term decisions were made by judgement.

**Files.** `termbase.json`, `glossary.json`, `glossary.csv`, `notation.md`, `tools/build_glossary.py`, `tools/verify_glossary.py`, `verify/verify_terms.py`, HTML ch. 14 and 16. Read-only reference: `AGENTS.md` §6.

**Substeps.**
* **N01.1 Reconcile the three lists.** Write a script (scratchpad) that diffs the term ids and the `use` / `avoid` forms in `termbase.json` against `glossary.json` and the 17 rows of `AGENTS.md` §6. Output a three-column table: in all three / in two / in one. Decide per row: keep, merge, drop.
* **N01.2 Authority check.** For every term whose Latvian form is a judgement call, look it up in (a) the Latvian terminology database (termini.gov.lv, "Akadēmiskā terminu datubāze AkadTerm"), (b) the RTU course literature for kinetics (see §9: Čornaja, *Fizikālā ķīmija*), (c) the course's own PDFs. Record the finding, with the URL or the file+page, in the `source` field of the termbase entry. If no authority is found write `nav atrasts`, not a guess.
* **N01.3 Make the termbase the generator.** Extend `build_glossary.py` so ch. 14, ch. 16's symbol column and `notation.md` are all emitted from `termbase.json`. Add a check that fails if any of the three drifts.

**Subtasks.**
* **N01-S1 Settle `pakāpe` / `kārta`.**
  1. Count occurrences of each in the HTML text and in the six PDFs (`pdftotext -layout`, `grep -c`); tabulate by source.
  2. Look up both in AkadTerm and in the RTU material; note whether either is marked as the recommended form for "reaction order".
  3. Keep the course form (`pakāpe`) as headword, keep `kārta` as accepted synonym, and make sure ch. 6 first-use gloss, glossary and termbase agree word for word. Do **not** declare either wrong (AGENTS §6 rule).
* **N01-S2 Inhibition vocabulary.**
  1. Build a 4-row comparison: course form, other Latvian forms found, English, defining property (competitive, noncompetitive, uncompetitive, mixed).
  2. Check the current sentence "nekonkurentā vs nekonkurējošā (uncompetitive)" in ch. 11 and ch. 14: does a student reading only ch. 11 know why two near-identical Latvian words name different things? If not, add a one-sentence rail note.
  3. Add `lang="en"` wrapper to every English term in these rows (this overlaps B05; coordinate).
* **N01-S3 Symbol/unit pairing.**
  1. For each term with a symbol in the termbase, confirm a unit or `bezdimensiju` exists (clears the two W1 warnings by making them explicit decisions: Maxwell–Boltzmann and activated complex have no unit, so set `unit: "—"` and teach the verifier that `—` is allowed).
  2. Confirm every symbol in the termbase appears in `notation.md` and ch. 16 (Table 16 equals `notation.md` cell for cell today).
  3. Run `verify_units`, `verify_terms`.

**Features folded in.** A "Term of the day" is NOT proposed (decorative). Instead feature F10 (bilingual flashcards) consumes this termbase.

**Acceptance.** (a) `python3 -I verify/verify_terms.py` exit 0 with 0 warnings. (b) The three-way diff script prints "0 unexplained differences". (c) Every `use` form appears in the HTML at least once or is flagged `no occurrences` deliberately.

**Definition of done.** One termbase, three generated views, a short `decisions` table (term, chosen form, authority, date), and the change-log line that says which choices remain judgement.

---

### N02 · Notation, symbol typography and language-marking

**Accomplishes.** Variables look like variables (italic where the convention says so), indices are real markup, English terms are marked `lang="en"`, and the notation rules in `notation.md` are enforced by a checker rather than by memory.

**Evidence.**
* `DESIGN.md` §11 "Known limits": "English terms (e.g. 'uncompetitive') are not marked `lang="en"`." [verified; also line 2875 of the HTML repeats it]. Only **1** `lang="en"` occurrence exists in the file [verified].
* `language_log.md` "Seen, not changed": "`E_a`, `C_S` as ASCII underscore notation in tables" (assigned to T03). The rendered text I extracted shows `E a`, i.e. subscript markup is probably present now, but **[suspected]** SVG `<title>` and `aria-label` still use `Ea`, `vmax` on purpose (documented in `notation.md`).
* `notation.md` itself states: "Quoted source defects keep the source notation".
* The Michaelis constant is written `K<sub>M</sub>` and `K_M` in the same document: AGENTS writes `K_M`; HTML writes `K<sub>M</sub>`. Fine inside a plan; the checker must ensure no `K_M` ASCII form appears in visible HTML text.

**Files.** HTML (text nodes only), `tools/verify_text.py`, `tools/verify_units.py`, `notation.md`.

**Substeps.**
* **N02.1 Inventory.** Extract every visible token that looks like a symbol (`[A-Za-z]_[A-Za-z0-9]`, `\^`, `E a`, bare `k` / `K`, `ln`, `t½`/`τ½`) with its context; classify as correct, ASCII-leak, or quoted-source.
* **N02.2 Language-mark English.** Wrap every English word or phrase in the visible text in `<span lang="en">` (the termbase `en` column drives the list). Keep proper names unmarked (Lineweaver–Burk is a name; `induced fit` is a term).
* **N02.3 Enforce.** Add rules to `verify_text.py`: R1 no `_` or `^` in visible text outside `<code>`, `<del>`, quoted-source spans; R2 every termbase `en` string found in visible text is inside `[lang=en]`; R3 `K` and `k` are never swapped (the lab chapter must write rate constant as `k`).

**Subtasks.**
* **N02-S1 Italic variables.**
  1. Decide the policy (ISO 80000-2: quantity symbols italic, units and chemical formulas upright). Write it into `notation.md` Display policy.
  2. Apply to `<var>` or `<i>` in prose; MathML `<mi>` is italic by default for single letters, check multi-letter identifiers such as `KMnO` (currently `<mi>KMnO</mi>` in MathML at line 1719; **[verified]** it is an `mi` which renders italic in some engines: formulae should be `mtext` or `mi mathvariant="normal"`).
  3. Regression: `build_mathalt.py --check` must still produce the same text alternatives.
* **N02-S2 `t½` versus `τ½`.**
  1. Count both in the HTML; the policy says `t½` everywhere in the document and `τ½` only when quoting the lecture.
  2. Replace stray `τ½` that is not a quotation; keep it in the gloss.
  3. Add a verifier rule.
* **N02-S3 Units spacing and minus.**
  1. Confirm the NBSP/minus policy (`language_log.md`: 223 NBSP, U+2212) still holds after any later edit by adding the counts to `verify_text` output so a regression is visible.
  2. Check script-generated strings (`fmt()`, `sciText()`) in the instruments; the log says units inside script strings still use a normal space ("optional"), so fix them.
  3. Test in the rendered DOM with a headless script.

**Acceptance.** `verify_text --strict` has the new rules and passes; at least 30 English terms carry `lang="en"` (the termbase count tells you the exact number); headless DOM check shows 0 ASCII-caret exponents.

**Definition of done.** `DESIGN.md` §11 "Known limits" loses the `lang="en"` limitation (edit only when the user asks, per `AGENTS.md` rule 3; otherwise record it in the report).

---

### N03 · Latvian proofreading, pass 2 (the parts pass 1 skipped)

**Accomplishes.** Pass 1 read only prose fragments longer than 90 characters. Everything else (table cells, SVG labels, MathML text, short fragments, script strings, `aria-label`s) got a word sweep at best. N03 reads that remainder.

**Evidence.** `language_log.md`: "**Not** read sentence by sentence: table cells, SVG labels, MathML and fragments under 91 characters". No Latvian spelling dictionary was installed ("hunspell present, `lv` dictionary absent"). 362 fragments were read; 40+ errors were found in them (gender agreement, case government, missing macrons), which is a high base rate: expect a comparable rate in the unread portion.

**Files.** HTML; `language_log.md` (append a section, do not rewrite).

**Substeps.**
* **N03.1 Build the reading set.** Extract all text nodes **not** in the 362 reviewed fragments: table cells (29 tables), figure captions, `aria-label` and `title`/`desc` strings (SVG and attributes), script string literals shown to the user, short callout feet, the answer text of all 40 Q&A, ch. 13/14/17 cells. Write them to a numbered list in the scratchpad with their line numbers.
* **N03.2 Read with a defined checklist.** For each fragment: diacritics; case government (`ietekmēt` + accusative; `zāles` is plural-only); gender agreement (`pārnese`, `molekula`, `piedeva` are feminine); verb reflexivity (`denaturēties`); register (imperative 2nd singular used consistently); anglicisms (`fits`, `hand-drawn`); mixed decimal separators.
* **N03.3 Log and re-verify.** Append a table (line, old, new, reason) in the format of `language_log.md`; run `verify_text --strict`; run the full verifier suite.

**Subtasks.**
* **N03-S1 Obtain a real Latvian spelling oracle.**
  1. Check whether `hunspell-lv` is installable (`dnf search hunspell-lv`, or LibreOffice's Latvian dictionary extension); if installable offline from the distro, install it into a throw-away prefix (do **not** change system state without asking the user).
  2. If none is available, state so in the report and use a frequency-based method: list every word type occurring once and review by eye (pass 1 did this for 990 types; extend to table and SVG text).
  3. Never claim "spell-checked" without the oracle's name and version in the report.
* **N03-S2 SVG and attribute language.**
  1. Pull the text of every `<text>`, `<title>`, `<desc>` and ARIA string.
  2. Read them as a screen-reader user hears them: is the sentence grammatical Latvian, not a label pasted from English?
  3. Fix and re-run `verify_links` (SVG title/desc presence) and `verify_a11y`.
* **N03-S3 Answer text.**
  1. Read all 40 model answers aloud-style for sentence rhythm; answers have a measured minimum of 35 words and median 52 (`verify_selfcheck`), so they are terse; check they are still complete sentences.
  2. Verify each answer's number against `numbers.json` (already enforced) and its units against `notation.md`.
  3. Fix, log.

**Acceptance.** Reading set 100 % covered (counts in the report: N fragments read, M changed). `verify_text --strict` PASS. The report names the oracle or says there was none.

**Definition of done.** Appended section in `language_log.md`; zero regressions in the verifier suite.

---

### N04 · Prose voice: remove machine-sounding patterns without changing science

**Accomplishes.** The document has a coherent, sober voice. What remains is the residue of generated prose: stacked em dashes, "Ko tas maina:" / "Simptoms:" templates repeated 45 times, and abstract openers. N04 humanises *only* style, never claims.

**Evidence.**
* **248 em dashes** in the file (this counts markup and SVG too; the visible-prose subset needs measuring) [verified count of the character `—`]. `lint.mjs` already warns on 1 em-dash finding; `CHECKS.md` §3 defends it as "Standard Latvian punctuation for symbol–definition legends". That defence is true for the legend (`v — reakcijas ātrums`) and false for rhetorical dashes in running prose such as the masthead standfirst ("…un katalizatoru — no sadursmēm un aktivācijas barjeras līdz fermentiem…").
* 45 identical four-part error blocks. A structure that repeats 45 times is a template; it is useful for study but monotone in print.
* Masthead standfirst: "Sešu kursa failu saturs sakārtots vienā bezsaistes dokumentā, un katram apgalvojumam ir birka, kas rāda avotu." The last clause overclaims (see C12).

**Files.** HTML prose; `workspace_skills/design-taste-frontend/references/copy.md` (read-only guidance).

**Substeps.**
* **N04.1 Measure.** Count em dashes in visible prose only, by chapter; list sentences with 2+ dashes; list sentences with the five most repeated openers.
* **N04.2 Rewrite by rule.** Legend dashes stay. Rhetorical dashes become commas, colons, full stops or parentheses. Keep sentence length variety. No new claims, no deleted claims.
* **N04.3 Diff review.** Produce a word-level diff and check that `data-num` spans, provenance tags and anchors are untouched; run all verifiers.

**Subtasks.**
* **N04-S1 Masthead and chapter ledes.**
  1. Rewrite the standfirst to state the document's job in two plain sentences, drop the overclaim (C12).
  2. Check each of the 18 chapter ledes opens with the question it answers, not with "Šajā nodaļā".
  3. Verify lengths: ledes ≤ 2 sentences.
* **N04-S2 Error-block rhythm.**
  1. Keep the four-part content but vary the labels' wording only if the four-part verifier (`verify_errors.py`) can be told the label set; otherwise leave them.
  2. Where two blocks say the same thing (same wrong answer reached from different questions) merge by cross-reference.
  3. Re-run `verify_errors`, `build_error_index.py --check`.
* **N04-S3 Passive and abstract nouns.**
  1. Find sentences of the form "Tas ir…, kas…" with an abstract subject.
  2. Rewrite with the actor named (the molecule, the enzyme, the student).
  3. Spot-check 20 sentences against the source PDFs to ensure the meaning did not move.

**Acceptance.** Visible-prose em-dash count drops by a stated fraction (target ≥ 70 %, legends excepted); no change to any `data-num` value; all verifiers pass; the `lint.mjs` `[em-dash]` finding goes away or is narrowed to legends.

**Definition of done.** Before/after counts in the report; `language_log.md` section "N04".

---

### Category B — Polishing out mistakes (N05–N08)

---

### N05 · Remove build-process leakage from student-facing text

**Accomplishes.** A medical student must not read task IDs (`T18`), script names or "AGENTS.md" in their study material.

**Evidence.** 23 occurrences of `T01…T20` task labels in visible text [verified by regex over text nodes], e.g. "(pirms T20: 122; pirms T19: 120; pirms T18: 116…)" in the print-pages paragraph; references to `verify/verify_tables.py`, `tools/build_numbers.py`, `numbers.json`, `AGENTS.md`, `design-taste inspect`, `lint.mjs` in chapter 17 (lines ≈2731–2880). `language_log.md` had already flagged "AGENTS.md reģistru" and "verify_numbers.py" in student text for T06/T20; the change log is the remaining home of these.

**Files.** HTML ch. 17 and any prose mentioning tools; new `CHANGELOG_BUILD.md` (new file).

**Substeps.**
* **N05.1 Classify.** Every sentence in ch. 17 into: (a) student-useful ("what the document changed relative to the sources"), (b) auditor-useful ("how we checked", still valuable to a lecturer), (c) developer-only.
* **N05.2 Move (c) out.** Create `CHANGELOG_BUILD.md` in the workspace root holding (c) verbatim; the HTML keeps (a) and a compact (b).
* **N05.3 Guard.** Add a banned-pattern rule to `verify_text.py`: visible text may not match `\bT\d{2}\b`, `\.py\b`, `\.mjs\b`, `AGENTS\.md`, `numbers\.json` except inside a block marked `data-audience="audit"`.

**Subtasks.**
* **N05-S1 Student-facing "Ko mēs mainījām".**
  1. Draft ≤ 1 screen: how many source defects were corrected (the register has 36), which three matter most for the exam (K2, K22, K23 per `AGENTS.md`), the lab method caveat.
  2. Tag each line `avots`/`labojums` so provenance verification passes.
  3. Link to ch. 13.
* **N05-S2 Audit appendix for the lecturer.**
  1. Keep the numbers (print pages, checks run) because `verify_print.py` P1 compares page count to the change log (`#print-pages-*`): moving it breaks the check, so update the checker target at the same time.
  2. Rename internal terms ("T18") to plain descriptions ("drukas pārbaude").
  3. Re-run `verify_print.py` (needs Chrome).
* **N05-S3 Print-map and page counts.**
  1. After the move the PDF will be about 120 pages instead of 124 (estimate; measure).
  2. Update `#print-pages-*` anchors and `verify_print.py` expectations.
  3. Regenerate `tools/build_printmap.py` output; run `--check`.

**Acceptance.** 0 matches for the banned patterns outside audit blocks; `verify_print.py` PASS with a new page count; ch. 17 ≤ 40 kB.

**Definition of done.** New file exists, HTML smaller by ≥ 80 kB, all verifiers pass.

---

### N06 · Scientific audit, round 2, checked against books

**Accomplishes.** The previous build corrected 28 lecture-text defects and 7 lab defects against general chemistry knowledge. Round 2 re-checks every correction and every open question against *named, citable textbooks and primary papers* (§9), so a lecturer can verify a correction by opening a book, and so wrong or over-confident corrections are caught.

**Evidence (open items I found).**
1. **K10, catalase Ea.** The source table says 23 J·mol⁻¹ vs 79 000 for uncatalysed H₂O₂. The document keeps "23 (kā iespiests)" and flags it for the lecturer [verified in ch. 8 table]. My research shows **published catalase values disagree**: RSC Education gives uncatalysed ≈ 75 kJ·mol⁻¹ and catalase **19** kJ·mol⁻¹ ([RSC](https://edu.rsc.org/feature/investigating-activation-energies/2020172.article)); a LibreTexts demonstration says "below **8** kJ·mol⁻¹" ([LibreTexts](https://chem.libretexts.org/Courses/BethuneCookman_University/B-CU%3A_CH-345_Quantitative_Analysis/CH345_Labs/Demonstrations_and_Techniques/Lecture_Demonstrations/Additional_Demos/The_Catalytic_Decomposition_of_Hydrogen_Peroxide)); Purdue's demo sheet gives ≈ 75 for the uncatalysed ([Purdue](https://chemed.chem.purdue.edu/genchem/demosheets/19.6.html)). `AGENTS.md` says "single-digit kJ/mol (verify before quoting)". So the working note's "single-digit" is **not supported** by all sources. The HTML must not state any catalase value as fact until a primary kinetics paper or a textbook table is found.
2. **K22, the Michaelis–Menten derivation.** `AGENTS.md` says Michaelis assumed rapid equilibrium and Briggs–Haldane (1925) introduced steady state. The bibliographic search confirms the paper ([Briggs & Haldane, *Biochem. J.* 19:338–339, 1925](https://www.beilstein-institut.de/en/symposia/archive/enzymology/escec-2013)). But **Johnson & Goody (2011)** re-translated the 1913 paper and argue the original analysis did not centre on the constant that bears the name ([PMC3381512](https://pmc.ncbi.nlm.nih.gov/articles/PMC3381512)). Therefore any sentence in the HTML that says "Michaelis assumed X" needs to be re-read against that translation before it is kept.
3. **K16, γ and Ea.** The HTML carries two sets (51.9 / 82.2 / 103.7 kJ·mol⁻¹ differential, and 54 / 85 / 107 two-point), explained in `CHECKS.md` §5. Correct, but a student sees two answers to one question. Textbook check required (Laidler; Atkins).
4. **K18/K19** (NH₄OH; d-sublevel of Pd and Au) were demoted to terminology-level notes; confirm with a general-chemistry text that the phrase "neaizpildīts d apakšlīmenis" is only a teaching simplification.
5. **K17 coupled reactions.** The source example (H₂O₂ + 2HI, Fe²⁺ as inductor) is called "dubious". The replacement example (Fe²⁺ inducing chloride oxidation by permanganate) is a classical induced-reaction example; confirm in a physical chemistry text (Laidler; Silbey–Alberty–Bawendi) and give a page.
6. **Pharmacokinetic half-life** (required by the topic description) is a *papildinājums*. Check the claim "about 4–5 half-lives to near steady state / elimination" against a pharmacology/biochemistry text before keeping any figure.
7. The `order` vs `molecularity` statements must match IUPAC: "order" is defined from the empirical rate law; molecularity is the number of reactant entities in an elementary step ([IUPAC Gold Book O04322](https://goldbook.iupac.org/terms/view/O04322); [M03989](https://dev.goldbook.iupac.org/terms/view/M03989/plain)). Good: the document already says this; add the Gold Book as the cited authority.

**Files.** HTML ch. 3–11, 13, 16; `numbers.json`; `AGENTS.md` (read only).

**Substeps.**
* **N06.1 Claim ledger.** From the HTML extract every `labojums` and `papildinājums` statement (provenance inventory `provenance_inventory.csv` has 117 KB of rows with `claim_kind`, `tag`, `status`: filter `status ≠ no-claim`). That is the checklist.
* **N06.2 Two-source rule.** For each claim write the book or paper (§9) that supports it and what it says, in a scratch table with columns claim, source, edition, chapter/section **to be verified by opening the book**, support (full/partial/contradicts). A claim with no second source is marked `viens avots` and the HTML wording gets softened.
* **N06.3 Apply.** Edit only where a claim is unsupported or contradicted; add the book name to the `papildinājums` tag text (never a page number you have not seen); regenerate numbers and run verifiers.

**Subtasks.**
* **N06-S1 Catalase and the Ea table (Table 5 of the source).**
  1. Find a primary measurement (search "catalase activation energy" with Arrhenius plot; check the Journal of Biological Chemistry and *Biochemical Journal* archives) and a general-chemistry table.
  2. Record every value with temperature range and enzyme source (bovine liver catalase ≠ erythrocyte catalase).
  3. In the HTML replace "(kā iespiests)" handling with: printed value, probable unit slip, range of published values, instruction to ask the lecturer. Keep "nav zināms" if no primary source is found.
* **N06-S2 Michaelis–Menten derivation chapter.**
  1. Read Cornish-Bowden, *Fundamentals of Enzyme Kinetics* (4th ed.), the chapter on steady-state kinetics; Segel, *Enzyme Kinetics*, unireactant chapter (§9 for editions).
  2. Compare with ch. 10 line by line: which approximation is named, which conditions (`C_S ≫ C_E`), what `K_M` equals in each limit.
  3. Add the Johnson–Goody caution as a rail note only if the translation supports it.
* **N06-S3 Collision theory numbers.**
  1. Recompute √(383/373) = 1.0133 (matches ch. 4 text), 29¹⁰/10¹⁰ = 42 070.7, and the Boltzmann ratio at 310/300 K for 50 kJ·mol⁻¹ = 1.88 (the log explains 1.91 vs 1.88).
  2. Check each against Atkins/Laidler on collision theory and the Arrhenius factor.
  3. Document disagreement if any; `numbers.json` stays the single source.

**Acceptance.** Every `labojums` row in Table 12 has at least one book/paper named; none of the books is cited with an unverified page; items 1–7 above each have a status in the report (`confirmed`, `softened`, `still open`).

**Definition of done.** A `SOURCES_AUDIT.md` (new file) with the ledger; HTML edits minimal; the lecturer-question list (MnO/MnO₂, catalase unit) updated.

---

### N07 · Laboratory chapter: correctness and honesty of the three-layer analysis

**Accomplishes.** The thiosulfate lab is the one place where the lecturer's key is scientifically wrong (AGENTS §5.2). The three-layer policy (course method, what the numbers are, valid analysis) must be airtight, quantitatively checked, and understandable to a student who just wants the grade.

**Evidence.** Chapter 12 is 48 kB with 3 interactive SVG panels, 6 lab Q&A items, an input table; `AGENTS.md` §5.2 numbers: ln(1/t) vs ln C slope n = 0.85, R² = 0.997 (set 1); n = 0.72, R² = 0.908 (set 2); `t·C` drift ±12 %; dilution 10/12; acid balance (H⁺ not in excess in tubes 1–2, **[my calculation, verify with lecturer]**). `CHECKS.md` §5 shows lab set 2 `k₁` was removed because the key does not compute it. The thiosulfate-clock teaching literature supports taking rate ∝ 1/t only as an approximation under a fixed endpoint amount ("this is an approximation… it is assumed that the amount of sulphur produced is fixed", revision-note sources found by search; **secondary, not citable in the HTML**).

**Files.** HTML ch. 12, `numbers.json`, `tools/build_numbers.py`, `AGENTS.md` §5.2 (read only).

**Substeps.**
* **N07.1 Independent recomputation.** In the scratchpad write a fresh script (not reusing `build_numbers.py`) that reads the two data sets from the key PDF (`pdftotext`) and recomputes: C values at both dilutions, ln C, 1/t, ln(1/t), slopes, intercepts, R², `t·C`, mole balance. Compare to `numbers.json`. Differences are bugs in one of the two.
* **N07.2 Endpoint and stoichiometry honesty.** Re-derive the reaction S₂O₃²⁻ + 2H⁺ → S↓ + SO₂ + H₂O; compute H⁺ and thiosulfate moles per tube; state in plain words which tubes are acid-limited. Present as "mans aprēķins; apstiprināt ar docētāju".
* **N07.3 Uncertainty.** Add a short uncertainty paragraph (burette ±0.05 mL, stopwatch ±1 s, end-point judgement ±2–3 s) and propagate to the slope with a simple Monte Carlo seeded for reproducibility (deterministic; `Math.random` is banned for reader-visible content, so precompute in Python and store in `numbers.json`).

**Subtasks.**
* **N07-S1 The "which analysis do I submit" decision aid.**
  1. A 3-row table: what the course asks / what to write as caveat / what to submit if you want full marks.
  2. State the default (follow the lecturer's method with caveat, `AGENTS.md` §10.11).
  3. Provide copy-ready caveat sentences in Latvian, tagged `autora atbilde`.
* **N07-S2 The catalyst identity (MnO vs MnO₂).**
  1. Keep both readings visible until the lecturer answers; note the density and colour clue is not available (do not invent).
  2. Add a check box in the worksheet "uzrakstīt, kuru vielu lietoja" so the student records what the label on the jar said.
  3. Re-verify L1 wording.
* **N07-S3 Autocatalysis curve.**
  1. Provide a computed S-shaped concentration–time plot for Mn²⁺ autocatalysis (logistic-type kinetics, `d[P]/dt = k[A][P]`) labelled as *model*, not data.
  2. Mark induction period; show effect of adding MnSO₄ at start.
  3. All numbers from `numbers.json`; SVG with title/desc.

**Acceptance.** Independent recomputation matches `numbers.json` to the displayed precision for all rows; any mismatch fixed at source; the three-layer block exists in one place and the worksheet print (30 pages) still fits.

**Definition of done.** Recompute script saved in `tools/` (new file `tools/recheck_lab.py`, with a negative fixture), report shows match table.

---

### N08 · Self-check set: correctness, difficulty and distractor quality

**Accomplishes.** 40 answers exist; a good set also tells the student *how likely* they are to pass the ≥ 55 % tests and exposes the thin spots.

**Evidence.** `verify_selfcheck`: 22 lecture + 11 MU + 6 lab = 39 source questions, plus 1 extra; answers are 35–85 words, median 52. 45 four-part error blocks; `AGENTS.md` notes the MU questions have **no key in the workspace**, so all MU answers are `autora atbilde`. The entry and exit tests are not in the workspace (`CHECKS.md` §4), so no item can be matched to the real test format.

**Files.** HTML ch. 15; `tools/build_selfcheck.py`; `tools/verify_selfcheck.py`; `tools/verify_errors.py`.

**Substeps.**
* **N08.1 Tag each question** with chapter, cognitive level (recall / apply / reason), and the defect ID it tests (K-number); this lives in the generator's source list.
* **N08.2 Coverage matrix.** Chapter × level matrix; list the chapters with no applied question. Chapters 2, 3, 5, 8 are thin in structure (see §1.2) and probably in questions too: **[suspected]**.
* **N08.3 Add questions only to fill gaps**, each as `papildinājums` or `autora atbilde`, with a four-part error block; never imitate the real test text (it is not available).

**Subtasks.**
* **N08-S1 Multiple-choice conversion of a subset.**
  1. Pick 12 questions where a wrong option corresponds to a catalogued misconception (K2, K3, K11, K14, K23).
  2. Build options from the *actual* wrong answers in the error blocks.
  3. Add to F01 (practice mode).
* **N08-S2 Numeric tolerance rules.**
  1. For every numeric answer write the tolerance (read-off from a figure ≈ ±0.2).
  2. Show the tolerance in the answer.
  3. Check against `numbers.json`.
* **N08-S3 Reading-order of the answers.**
  1. Check the answer starts with the answer, then the reasoning, then the error block.
  2. Print-mode: answers hidden in exam print; worksheet print has `ws-space` areas (40 of them): confirm every question has a blank area of a size proportional to the expected answer.
  3. Verify via the 30-page worksheet PDF.

**Acceptance.** Coverage matrix has no empty cell for chapters 1–11 at "apply" level or the report says why not; `verify_selfcheck` and `verify_errors` pass with the new items.

**Definition of done.** The matrix is in the report and in `CHANGELOG_BUILD.md`.

---
### Category C — Polishing with the skills of the workspace (N09–N12)

The vendored skills are read-only references (`AGENTS.md` §2.2). "Using" a skill means reading its `SKILL.md`, applying its method, and recording which of its acceptance tests were run. `AGENTS.md` §9.2 says four composition skills contradict each other (Tufte, blueprint, mook, design-taste `tells.md`); the Tufte structure is the chosen base. Do not overlay another.

---

### N09 · Quality gates: `impeccable`, `audit`, `break-ui` and the design-taste tools, run for real and resolved honestly

**Accomplishes.** Today `lint.mjs` (5 FAIL, 3 WARN) and `inspect.mjs` (5 FAIL, 6 WARN) fail, and `run_all.py` turns that into "DEFENDED", so the overall verdict is `PASS` (`verify/run_all.py` lines 166–178, 199 [verified]). Some defences are strong (booktabs rules, a 40 px h1 on a monograph); some are only convenient (the `[still-page]` and `[few-pictures]` findings). N09 separates the two kinds, fixes what is genuinely improvable, and makes the verdict wording accurate.

**Evidence.** `CHECKS.md` §3 lists 10 findings with defences. Judgement of each (mine):

| Finding | Defence quality | Action |
|---|---|---|
| `[hairline]` 1 px rules in tables and rail | strong for booktabs; the rail boundary is weaker | keep tables; reconsider rail rule (N15) |
| `[outlined-box]` on `.btn`, inputs | strong (WCAG hit target) | keep |
| `[em-dash]` | partly valid (legends), partly not (prose) | fix prose (N04) |
| `[few-pictures]` "0 raster photographs" | irrelevant by rule (no raster allowed) | keep, wording only |
| `[focal-point]` h1 40 px | defensible for a long monograph | keep, but see N15 on the masthead |
| `[lopsided]` 20 rows at 1440 px | defensible by measure; **but** empty margin on 20 rows is also a layout choice that could carry sidenotes | evaluate in N15 |
| `[still-page]` no entrance animations | defensible (`DESIGN.md` §8 bans decorative motion) | keep |
| `[card-rows]`, `[side-scroll]`, `[off-centre]`, `[edge-text]`, `[no-footage]` WARN | mixed | check `side-scroll` on phones (N14) |

**Files.** `verify/run_all.py`, `workspace_skills/design-taste-frontend/scripts/*.mjs`, `DESIGN.md` (propose edits only).

**Substeps.**
* **N09.1 Reproduce.** Run `lint.mjs` and `inspect.mjs` from the scratchpad with `--out` set (AGENTS §8: the default writes `.taste-skill/` into the cwd). Save outputs; confirm the counts match `CHECKS.md`.
* **N09.2 Run the other three gates.** `audit` (accessibility, performance, theming, responsive, anti-patterns → P0–P3 score), `break-ui` (worst-case content: very long Latvian compounds, 0 and 1 item, huge numbers), `impeccable critique` on the masthead and one chapter. Keep each gate's report in the scratchpad; summarise in `CHECKS.md` only after the user agrees to edit it.
* **N09.3 Triage.** Every P0/P1 gets a task or a written defence; defences must name a measurable reason, not "intentional".

**Subtasks.**
* **N09-S1 `break-ui` stress for this document.**
  1. Feed the instruments extreme inputs (E_a = 0 and 400 kJ·mol⁻¹, T = 200 K and 2000 K, `C₀` = 0, K_M = 0), and the lab table with empty cells, commas and points as decimal separators.
  2. Record NaN, Infinity, overflow or label collisions.
  3. File each as a bug; B03 below is the first candidate.
* **N09-S2 Verdict wording.**
  1. Change `run_all.py` output so that the overall line reads `PASS (static, 10 suites) · ADVISORY: 2 heuristic tools FAIL, 10 findings, see §3` instead of a bare `PASS`.
  2. Keep exit code behaviour unchanged for CI.
  3. Add a fixture proving the advisory line appears.
* **N09-S3 Re-score after N15/N16.**
  1. After the redesign tasks, re-run the tools.
  2. Report the deltas, not just the end state.
  3. Do not pass `taste-skill-ignore` markers to silence a finding unless the finding is on a genuinely required element.

**Acceptance.** Each gate has a dated report; `CHECKS.md` verdict wording is accurate (see C06); every FAIL has either a fix or a one-line measurable defence.

**Definition of done.** A table "finding → decision → evidence" in the report.

---

### N10 · Tables and comparison matrices with `synoptic-matrix-architect`; terminology rails with `lexicon-morphology-weaver`

**Accomplishes.** Twenty-nine tables exist; the skill says comparisons with ≥ 4 attributes should be filterable matrices with sticky axes and exact-difference highlighting. Which tables benefit, and which are better left as booktabs?

**Evidence.** `AGENTS.md` §9.1 lists candidate matrices: enzymes vs inorganic catalysts, order 0/1/2, inhibition types, catalysis types. The document has 9 "matrix" tables (class `matrix defects` seen on Table 12). Chapter 14 (terminology corrector, 54 kB) is a candidate for morphology rails (prefix/root/ending cues): Latvian kinetic terms have transparent roots (`pus-` + `periods`, `aktivācijas` + `enerģija`, `ātruma` + `konstante`).

**Files.** HTML ch. 6, 8, 9, 11, 13, 14; skills `synoptic-matrix-architect`, `lexicon-morphology-weaver`.

**Substeps.**
* **N10.1 Triage the 29 tables.** For each: attributes count, rows count, task the reader does with it (look up, compare, recall). Matrix upgrade only where rows ≥ 4 and attributes ≥ 4 and the task is *compare*.
* **N10.2 Prototype in the scratchpad** on one table (inhibition types: mechanism, binds to, effect on v_max, effect on K_M, reversible?, example) with column-recall and row-isolation controls.
* **N10.3 Integrate** respecting DESIGN.md: native controls, no cards, no colour fills, no `localStorage`; no-JS fallback must show the plain table.

**Subtasks.**
* **N10-S1 Inhibition comparison matrix.**
  1. Rows: competitive, noncompetitive (pure), mixed, uncompetitive (papildinājums), irreversible.
  2. Columns: binds to, v_max, K_M, line pattern on the double-reciprocal plot, example drug (papildinājums, source needed from a pharmacology text).
  3. "Exact difference" highlight between any two rows.
* **N10-S2 Morphology rails in ch. 14.**
  1. Pick 12 terms; split into root + affix with a one-line meaning.
  2. Fold-over recall sheet for print (hide LV, show EN and vice versa).
  3. `verify_text` and `verify_terms` must pass; never split a term differently from `termbase.json`.
* **N10-S3 Order 0/1/2 matrix.**
  1. Columns: rate law, integrated law, linear plot, slope, unit of k, t½ expression.
  2. Reuse numbers from `numbers.json` (the three half-life formulas already tested by `test_halflife.js`, 10/10).
  3. Cross-check against the LibreTexts chart on worksheet p. 4.

**Acceptance.** Three matrices live; fallback table is present without JS (`verify_a11y` no-script rules); keyboard operation proven in `check_a11y.mjs` (extend its tests).

**Definition of done.** `verify_tables.py` still passes (29 → maybe 30 tables) and the table index in the report is current.

---

### N11 · Mechanism animations without decoration: `state-scrubber-lab` and `svg-spatial-occlusion`

**Accomplishes.** Staged processes (chain reaction, catalysed vs uncatalysed pathway, enzyme cycle) become scrubbers where the student sets the phase and watches species, energy and rate change together; the energy profile and enzyme figures become recall tools by masking labels.

**Evidence.** Only 1 SVG in chapter 7 (mechanisms), 1 in chapter 9, 0 in chapter 8. The DESIGN ban list says "decorative or motion animation": a scrubber is *student-driven state*, not motion, and respects `prefers-reduced-motion` because nothing moves on its own. Instrument 1 (distribution) and 2 (orders), 3 (Q10 reading?) and 4 (lab) already follow this pattern, so N11 extends an accepted pattern.

**Files.** HTML ch. 7, 8, 9, 10; new generator `tools/build_scrubber.py` (so SVG states are computed, like `build_orderfig.py`).

**Substeps.**
* **N11.1 Pick three processes** with discrete stages: (1) chain reaction: initiation, propagation (branching/unbranched), termination; (2) catalysed reaction pathway: E + S ⇌ ES → E + P on an energy profile; (3) enzyme cycle with inhibitor binding.
* **N11.2 Define the state vector** for each (species counts or concentrations, free-energy position, rate). Compute from `numbers.json` entries, never typed by hand.
* **N11.3 Implement** with native `input[type=range]` (`aria-valuetext` = unit string), one polite status region per instrument, static fallback figure kept in `details.fallback-details`, print shows the static figure. Follow the instrument markup of `DESIGN.md` §11.

**Subtasks.**
* **N11-S1 Chain reaction scrubber (ch. 7).**
  1. Model H₂ + Br₂ or the radical chain on the lecture slide (use only what the sources show; the specific reaction is a choice, tag it).
  2. Stages as slider positions 0–5; radical count shown as a dot strip with counts; unbranched vs branched toggle (radical count grows linearly vs exponentially).
  3. Verify the fix noted in the language log (`ģeometriski` → `eksponenciāli`) stays.
* **N11-S2 Catalysed pathway scrubber (ch. 8).**
  1. Draw the energy profile of an uncatalysed step and a catalysed two-step path with an intermediate (a *minimum*) and two transition states (maxima), using the terminology `aktīvais komplekss = maksimums`, `starpprodukts = minimums` from `AGENTS.md` §6.
  2. Scrub from reactants to products; marker position, tooltip-free (labels inline).
  3. Read-outs: Ea (forward), Ea (reverse), ΔH constant; the catalyst does not change ΔH or K.
* **N11-S3 Occlusion drill on the energy profile and on lock-and-key / induced fit.**
  1. Mask any label by checkbox ("Slēpt iezīmes"); reverse pin recall (click the region named in a prompt).
  2. State is in the DOM only (no storage).
  3. Keyboard-complete (Tab, Space); test with `check_a11y.mjs`.

**Acceptance.** Three new interactive figures, each with no-script fallback; `verify_figures` (SVG language, axes, dash roles) and `verify_a11y` pass; print shows static figures; no new colour beyond teal and bordeaux.

**Definition of done.** Numbers reproducible (script); added to the figure index; change-log entry.

---

### N12 · Print and PDF: from 124 pages to a deliberate set of printables (`print-css-alchemist`, `pdf-vector-surgeon`, `pdf-claude`)

**Accomplishes.** Three print modes exist (default 124 pp., worksheet 30, exam 102). A student wants: a **short** exam-eve sheet (4–6 pp.), the worksheet, and the full text. N12 produces them and verifies greyscale legibility, which `DESIGN.md` §7 admits has no automatic check.

**Evidence.** `DESIGN.md` §7: "Signal and second colour print as the same grey (64 and 65 of 255). Series are told apart by the direct label next to the line and by dash, never by tone; the pages with both were looked at in grayscale, but **no automatic check covers this**." `CHECKS.md` §4: only 10 of 124 print pages were looked at by a human. The roles of teal (catalysed) and bordeaux (reference/error) therefore collapse to one grey in print.

**Files.** HTML print CSS, `tools/check_print.py`, `verify/verify_print.py`, `tools/build_printmap.py`; skills `print-css-alchemist`, `pdf-vector-surgeon`.

**Substeps.**
* **N12.1 Greyscale audit.** Render all 124 pages with `pdftoppm`, convert to greyscale, and run a script that flags any plot where two strokes' luminance differs by less than a set threshold *and* the dash pattern is identical. This is the missing automatic check.
* **N12.2 Define three print products.** (a) `?mode=cheat`: formula sheet (ch. 16) + the 10 most common errors (from Table 13 index) + the three plots students must sketch; (b) existing worksheet; (c) existing full text. The mode switch already exists (`?mode=exam`, `#darba-lapa`): extend the same mechanism.
* **N12.3 Page-level QA beyond sampling.** Extend `verify_print.py` with: no figure caption separated from its figure, no equation split from its legend, no table with a single row on a page.

**Subtasks.**
* **N12-S1 Greyscale-proof strokes (couples with N19).**
  1. Compute contrast between the two print greys (64 vs 65 of 255 is essentially identical) and propose a darker/lighter pair for print: teal → ~40, bordeaux → ~110, still readable in monochrome.
  2. Add dash pattern and marker shape as redundant coding where two series share a plot.
  3. Verify with the script from N12.1.
* **N12-S2 One-page "exam-eve" sheet.**
  1. Content from ch. 16 only (formulas) plus symbol/unit table 16; no new claims.
  2. Layout with a strict baseline grid (`pdf-vector-surgeon` method).
  3. Check on A4 with a real print test if the user can; otherwise `pdffonts` and `pdfimages -list` (expect 0 raster images).
* **N12-S3 PDF metadata and accessibility.**
  1. Title, language (`lv`), author, keywords through the print pipeline (Chrome's PDF has the title from `<title>`).
  2. Tagged PDF check with `pdfinfo` (Tagged: yes/no) and report.
  3. Bookmarks for 18 chapters if the pipeline allows; otherwise state the limit.

**Acceptance.** Greyscale check script exists and passes; the page count of each product stated and verified by `verify_print.py` expectations; the report says how many pages a human actually looked at (target ≥ 30, not 10).

**Definition of done.** Printable files described in ch. 0 "Drukāšana"; checks recorded; unchecked items listed honestly.

---

### Category D — Functionality (N13–N14)

---

### N13 · Instrument engine: test, harden, and unify the four interactive instruments

**Accomplishes.** The interactive plots (distribution, orders, Michaelis–Menten with inhibitors, lab) run on one 53 KB inline script. It is checked by one JS test file (`tools/test_halflife.js`, 10 tests) and a browser accessibility test. The numerical engine that produces numbers the student relies on is therefore tested only for half-lives.

**Evidence.** Script blocks: 2, 53 KB. Test coverage in the repo: `test_halflife.js` 10/10, `check_a11y.mjs` 37/37 (a11y/keyboard, not numerics). `DESIGN.md` §10 says the browser measurement "label collisions of both interactive plots in 48 states at 12 widths from 320 to 1440 px (zero overlaps…)" is **"not automated in the repo"** [verified]. That claim cannot be reproduced by anyone.

**Files.** HTML `<script>`; new `tools/test_instruments.mjs`, `tools/check_labels.mjs`.

**Substeps.**
* **N13.1 Extract the pure functions** (Maxwell–Boltzmann tail, integrated laws, Michaelis–Menten with inhibition, ln(1/t) fit) into a clearly delimited block (`/* PURE:begin … PURE:end */`) so a Node test can `eval` that block without a DOM.
* **N13.2 Numeric test suite.** Golden values from `numbers.json` (211 entries) and independent analytic checks: t½ per order; tail ratio 1.88; K_M at v_max/2; competitive K_M,app = K_M(1+[I]/Ki); noncompetitive v_max,app = v_max/(1+[I]/Ki).
* **N13.3 Layout fuzz.** Automate the "48 states × 12 widths" claim using headless Chrome (via Playwright if installable, else the CDP approach already in `check_a11y.mjs`) and fail on label overlap, clipped label, or horizontal scroll.

**Subtasks.**
* **N13-S1 Edge-case handling.**
  1. Define behaviour at the limits (T → 0 K, E_a = 0, `C₀` = 0, `[I]` = 0 with an inhibitor selected, K_i = 0).
  2. Return a visible "nav definēts" state rather than `NaN`/`Infinity`; no `console.error`.
  3. Unit-test each.
* **N13-S2 State in the URL, not in storage.**
  1. Encode instrument parameters in the hash (`#ferments?I=0.5&Ki=1`), read on load; DESIGN bans storage and external requests, not the hash.
  2. Reset button clears hash.
  3. Test: copy link → reload → same state; works with script off by simply ignoring the hash.
* **N13-S3 One status-region pattern.**
  1. Audit that the four live regions are `aria-live="polite"` and atomic (documented), and that `<output>` elements are `aria-live="off"`.
  2. Test announcements with the Chrome accessibility tree (the existing script) for all four after N11 adds three more.
  3. Document the pattern in `DESIGN.md` §11 proposal.

**Acceptance.** `node tools/test_instruments.mjs` ≥ 40 assertions pass; the label-fuzz script exists and runs; no `NaN` is reachable by any slider combination.

**Definition of done.** `CHECKS.md` gains two rows (when the user permits editing it); the DESIGN §10 sentence "not automated" becomes true.

---

### N14 · Reading navigation without floating controls

**Accomplishes.** The first 1.5 screens on a phone are furniture; a 124-page document needs findability. DESIGN bans `position:fixed` and floating controls, so improvements must be in-flow.

**Evidence.** 390 px screenshot: legend, six source blocks and 18 contents entries come before chapter 0. There is a skip link (`<main id="sakums">`) but a reader opening the file on a phone sees it only after tabbing. `DESIGN.md` §6: "The way back to the contents is the footer link". 953 internal links exist (`verify_links`), so linking infrastructure is rich.

**Files.** HTML header and chapter heads; CSS; `check_a11y.mjs`.

**Substeps.**
* **N14.1 Reorder the masthead for narrow screens** with CSS only: title and standfirst, then contents, then legend and sources collapsed in `details` ("Avoti un birkas") that print open (as all `details` do).
* **N14.2 End-of-chapter links.** Each chapter ends with "Nākamā nodaļa →" and "↑ Saturs" in flow (not fixed). Make the arrow glyphs real text, not images; give a link name that says where it goes (DESIGN §11).
* **N14.3 In-document find.** Recommend the browser's find (Ctrl+F; ch. 13 already says so) and make it work well: all collapsed `details` hide text from find on some browsers, so add a "Atvērt visu" button that opens all `details` (the print code already does it).

**Subtasks.**
* **N14-S1 Contents layout.**
  1. Fix the two-column contents on desktop so columns balance (currently 9 vs 9 items but the right column starts far from the left; measured on the 1440 px screenshot).
  2. Group chapters into 4 parts (Pamati 1–3, Temperatūra/barjera 4–6, Katalīze/fermenti 7–11, Prakse/pārbaude 12–17) with a part heading; keep numbers functional.
  3. Verify with `verify_design.py` D12 (rows) and a screenshot at three widths.
* **N14-S2 Phone check of wide plates.**
  1. `inspect.mjs` `[side-scroll]` WARN: list the plates that scroll at 390 px.
  2. For each, choose: redraw narrower (viewBox ≤ 560 → compact layout) or keep scroller with the sticky caption.
  3. Test touch scrolling in emulation; state that real devices were not used.
* **N14-S3 "Open all / close all" and deep links.**
  1. Button above the first chapter, native `<button>`, toggles `details` without altering stored state (none exists).
  2. Every Q&A item and error block already has an id; expose a "kopēt saiti" text link (plain `<a href="#id">` is enough, no JS).
  3. Verify no duplicate ids (`verify_links`).

**Acceptance.** At 390 px the first paragraph of chapter 0 is within 1 screen after the title block (measure: y-offset of `#ch0 .lede` ≤ 1.2 × viewport height); `check_a11y.mjs` has tests for the new controls.

**Definition of done.** Before/after screenshots at 1440/768/390 px in the report; no `position:fixed` introduced (`verify_design`).

---
### Category E — Anti-slop redesign, restyle, retexturing (N15–N16, N19)

What "AI slop" means for this document: not the obvious tells (gradients, pills, emoji, cards, glassmorphism: **these are already banned and absent** [verified: `position:fixed` count 0; DESIGN §8]). The remaining slop is structural and verbal: **uniform repetition** (107 callouts, 45 identical error blocks, 80 identical ladder rungs), **ceremony before content**, **symmetry for its own sake**, and **defended-away warnings**. The brief is to make it look like the work of one person who thought about *this* subject.

---

### N15 · Anti-slop redesign pass: hierarchy, rhythm and the masthead

**Accomplishes.** The first screen should say what the document is and put a figure or the first question in front of the reader; the long middle should vary its rhythm by content (a derivation is not a warning is not a quiz).

**Evidence.**
* 1440 px screenshot: nothing wrong, nothing memorable: masthead, legend, six source tiles in a 3×2 grid, contents, chapter 0 text. Chapter 0 is *all* text (6 kB, 0 figures).
* Same shape everywhere: 107 `callout` elements; 45 `errblock`s each with four labels; 80 `rung-line`/`rung-label` pairs; 220 `qa-label`s. Consistency is a virtue for study material, but sameness over 124 pages reads as generated.
* `inspect.mjs` `[lopsided]` on 20 `.row--solo` rows and `[off-centre]`: the empty right margin is a design choice defended by measure, not a choice about where marginalia could go.
* DESIGN.md §5: rail rows only when the rail has content; "do not write a note to fill the margin" (good rule, keep it).

**Files.** HTML CSS (`:root` tokens and component rules), masthead markup, `DESIGN.md` (proposal only).

**Substeps.**
* **N15.1 Critique first.** Run `impeccable` critique and `design-taste-frontend/references/critique.md` against 12 sample screens (the tool's own sampling) and against 4 hand-chosen: masthead, ch. 6 order figure, ch. 10 instrument, ch. 13 register. Produce a P0–P3 list.
* **N15.2 Redesign the opening.** Title block with one *real* figure: the energy profile with and without catalyst (the single most recalled picture of the topic) at hero size, drawn by the SVG program (N20). Contents moves below; legend and sources collapse (N14).
* **N15.3 Rhythm rules.** Write down ≤ 6 rules (e.g., "no more than two callouts in a row", "a figure at least every 2 screens in ch. 4–12", "a worked example always follows its formula") and enforce each with a small check in `verify_design.py`.

**Subtasks.**
* **N15-S1 Callout taxonomy.**
  1. List the three callout kinds (teal general, bordeaux correction, rule terminology).
  2. For the 107 callouts compute a distribution by chapter; find chapters with runs of ≥ 3 identical callouts.
  3. Merge or convert some into prose (a callout that is two sentences is a paragraph).
* **N15-S2 Error blocks in print and screen.**
  1. Keep all 45 blocks (they carry exam value), but present them as a *single index first* (Table 13 exists; promote it) and the details second.
  2. In chapters, show only a one-line "Biežākā kļūda: …" with a link to the block.
  3. Check print height: no Q&A item exceeds the 260 mm page (tallest 142 mm today).
* **N15-S3 Rail honesty.**
  1. List rail rows and their rail text length; remove rails of < 2 lines (the design rule), as the checker D12 already demands.
  2. Consider promoting 5–10 `.row--solo` rows where a margin figure (a tiny SVG) would help instead of leaving the margin empty: e.g. next to the van 't Hoff rule a mini-plot of `k` against `T`.
  3. Re-run `inspect.mjs`; `lopsided` count should fall from 20.

**Acceptance.** `impeccable` critique P0 = 0, P1 ≤ 3 with defences; screenshots at 3 widths in the report; checks D12–D14 pass; no new hue; no `position:fixed`.

**Definition of done.** `DESIGN.md` change proposal listed (not applied without the user's yes).

---

### N16 · Restyle: type, measure, colour and (maybe) a second ground, within the existing token system

**Accomplishes.** Same design language, better execution on devices that lack the Charter fonts and on dark-preferring users, while keeping offline and accessible.

**Evidence.**
* Body is "Charter stack" (system serif) and labels are `system-ui` [DESIGN §3]. Charter is present on macOS/iOS and some Linux distros; on Android and Windows the fallback differs. **[suspected]** that the Latvian diacritics ā ē ī ū ģ ķ ļ ņ and the combining-quality of `½`, `⁻¹`, `₂` look different per OS. The previous build checked diacritics on one machine (Linux) in Chrome only (`CHECKS.md` §4).
* DESIGN §9: "Dark mode: not provided". The reasoning (a second reviewed palette for every figure and tag) is true but is a cost, not a prohibition; the document is read at night before exams.
* `--select: #c9dfda` etc. exist; type scale: 13/14/17/20/40 px.

**Files.** CSS `:root`, `DESIGN.md`, `verify_design.py`, `verify_a11y.py` (contrast).

**Substeps.**
* **N16.1 Font reality test.** Render a glyph sheet (all Latvian letters, `½ ⁻¹ ₂ ² ≈ → ⇌ µ γ τ Δ`, U+2212) with the *declared stack only* on at least Linux/Chrome (available), and, if the user has other devices, ask for a screenshot from each. Report missing glyphs by name.
* **N16.2 Decide on an embedded font.** Candidates under SIL OFL (e.g. a text serif with full Latvian coverage): subset to Latin Extended-A + needed math symbols, embed as base64 woff2 (size budget ≤ 150 KB for both families; the page is offline so no CDN). **Verify the licence text of the exact font file before embedding; include the licence in ch. 17.** Alternative: keep system stack and add a visible "fonts" fallback note. The decision is the user's (it adds ~100 KB).
* **N16.3 Dark scheme as derived tokens.** If approved: add `@media (prefers-color-scheme: dark)` redefining the 15 tokens; re-measure contrast for every role with `verify_a11y.py`; add `color-scheme: light dark` (the page currently declares `light`). Plots use tokens, so SVG follows automatically; the print block is unaffected.

**Subtasks.**
* **N16-S1 Contrast table for dark.**
  1. Pick candidate dark values for paper, ink, muted, signal, second, plot, grid.
  2. Compute WCAG ratios in a script (the repo already reports ink 13.8, muted 6.0, signal-dark 8.0, second-dark 8.9 for light).
  3. Require ≥ 4.5:1 text, ≥ 3:1 for plot strokes; reject any pair that fails.
* **N16-S2 Type scale audit.**
  1. Confirm body 17 px / line-height 1.65 gives ≈ 66 ch measure; test with Latvian long compounds (`break-ui` worst-case strings).
  2. Check `hyphens: auto` with `lang="lv"` support in Chrome; if unsupported, check ragged right behaviour in narrow rails.
  3. Keep five sizes; no sixth.
* **N16-S3 Focus and target size.**
  1. DESIGN §11: "The 24 px target size of WCAG 2.2 was not measured for the inline term links." Measure all interactive elements (78 `term-link`s, buttons, details summaries).
  2. Enlarge hit areas with padding (not visible size) where < 24 × 24 CSS px, except inline text links which WCAG 2.2 exempts in a sentence (check the exact exception text before relying on it).
  3. Add to `check_a11y.mjs`.

**Acceptance.** If dark approved: all roles pass contrast in both schemes, 0 hex colours outside `:root`/print (verify_design), figures legible; if not approved: report states "not done, user decision".

**Definition of done.** Glyph sheet screenshot; `verify_design` updated tokens; a short "why" paragraph in `DESIGN.md` proposal.

---

### N19 · Retexturing: a surface vocabulary that survives greyscale and print

**Accomplishes.** "Texture" here means *information-carrying surface*, not paper grain (which the document bans and the precedent file wrongly used). The goal is a small set of hatches, dash patterns, line weights and markers that mean the same thing everywhere, so figures stay legible in black-and-white, in print, and for colour-blind readers.

**Evidence.** Two hues carry the story (teal = modified/catalysed; bordeaux = reference/error), but they print as the same grey (64 vs 65). All 12 plates and the instruments rely on stroke colour plus direct labels plus dash (`verify_figures` checks "dash roles"). Regions (e.g., the area beyond Ea in the distribution) are currently told apart by light fills; the instrument text says "regions are named in text" for gridlines (decorative, 1.2:1).

**Files.** SVG `<defs>`, CSS tokens, `tools/verify_figures.py`, `tools/build_orderfig.py`.

**Substeps.**
* **N19.1 Define the vocabulary (≤ 8 items).**
  * stroke weights: axis 1.5, data 2, guide 1, hairline grid 0.5;
  * dash roles (already defined): solid = measured/computed data, dashed = construction guide, dotted = extrapolation;
  * markers: circle = measured point, square = read from a source figure, triangle = computed;
  * hatches: `//` = fraction above Ea (reactive), `\\` = region of a different condition, cross-hatch = excluded;
  * fill for "energy beyond barrier" always the same hatch.
* **N19.2 Implement as SVG `<pattern>` in one shared `<svg>` defs block** (referenced by `url(#…)`; check `verify_links` for the ARIA and id rules; a hidden defs SVG must be `aria-hidden="true"` and have no `<title>`, but then `verify_links` content-SVG count changes: update the verifier).
* **N19.3 Greyscale and CVD verification.** Render at greyscale and with a deuteranopia simulation matrix; compute whether any two series become indistinguishable (N12.1 script).

**Subtasks.**
* **N19-S1 Hatch for the barrier area.**
  1. In the distribution plot (ch. 4 and instrument 1) replace the tinted fill beyond Ea by a hatch of the signal ink.
  2. Heating shifts the curve; the hatched area grows. Check area computed (`numbers.json` 1.88 ratio) is mirrored in the label.
  3. Test in print and greyscale.
* **N19-S2 Table texture.**
  1. Keep booktabs (it is the right design).
  2. Mark "Sev." severity A/B/C/D with a small glyph prefix (A ■ ▲ ● ○ are shapes, not emoji) so the register reads at a glance in print.
  3. `verify_text.py` whitelist must admit those four code points; check they are present in the embedded font (N16).
* **N19-S3 Marker legend per figure.**
  1. Each figure caption lists its markers in one line.
  2. Consistency check across 12 plates by regex on the SVG `<defs>`/class names.
  3. Add to `verify_figures.py`.

**Acceptance.** Greyscale script reports no indistinguishable pair; the vocabulary is stated once (a half-page "Zīmējumu valoda" in DESIGN proposal) and checked by `verify_figures`.

**Definition of done.** Before/after greyscale renderings of 3 figures in the report.

---

### Category F — Precision of explanation, understandability, and SVG (N17, N18, N20)

---

### N17 · Explanations: make the thin chapters teach, and make every formula answer "what does this number mean?"

**Accomplishes.** Chapters 1, 2, 3, 5, 8, 9 are short and unillustrated yet carry the concepts the entry test covers (rate, factors, mass action, temperature, catalysis, enzymes). A student who reads only them should still pass the entry test.

**Evidence.** §1.2 table: sizes 9, 5, 5, 13, 15, 14 kB; SVG counts 0, 0, 0, 0, 0, 1. The topic description's required concepts (`AGENTS.md` §11 DoD): rate, Ea, catalyst; factors including surface area and pressure; homogeneous/heterogeneous catalysis; half-life in pharmacy and medicine; Ea change after catalyst addition; Maxwell–Boltzmann distribution; enzyme inhibition with catalysts.

**Files.** HTML ch. 1–3, 5, 8, 9; `numbers.json`; `tools/build_numbers.py`.

**Substeps.**
* **N17.1 Concept-by-concept gap list.** Take the required-concept sentences of the topic description (quoted in ch. 0) and tick, for each, *where* it is explained, with a worked number, with a figure, with a common error. Gaps become paragraphs.
* **N17.2 One consistent explanatory movement.** Question → mechanism in words → mathematics with a legend → worked example with real numbers → common mistake → check. Most chapters follow it; the thin ones skip steps.
* **N17.3 "What the number means" lines.** After each key formula add one sentence that translates the symbols into the physical situation, and one unit sanity check ("s⁻¹ means a fraction per second of the remaining material reacts"). Every number goes through `numbers.json`.

**Subtasks.**
* **N17-S1 Chapter 5 (temperature) rebuilt around two figures.**
  1. Figure: `k` against `T` (exponential) for two Ea values; figure: `ln k` against `1/T` (straight line, slope −Ea/R) with the two-point calculation shown.
  2. Worked example: from k at 300 K and 310 K derive Ea (this is where the 54/85/107 figures live; present the **two-point** result as the main answer and the differential as the cross-check, so students do not see two answers to one question).
  3. Common error: "γ is a law"; link to K16.
* **N17-S2 Chapter 8 (catalysis) rebuilt around the profile and a classification.**
  1. Figure: catalysed vs uncatalysed profile *inside* the chapter; arrows for Ea(fwd), Ea(rev), ΔH.
  2. Classification table (homogeneous / heterogeneous / microheterogeneous / autocatalysis) with example, phase relation, how Ea changes, where in the body.
  3. Add the Berzelius correction (K21) next to the profile, and the statement "a catalyst changes the rate, not ΔG or K" with one numeric illustration (ΔG fixed, K unchanged).
* **N17-S3 Chapters 1–3 with one figure each.**
  1. Ch. 1: concentration–time curve with the secant (average rate) and tangent (instantaneous rate).
  2. Ch. 2: heterogeneous reaction with three rate-limiting steps drawn as a pipeline (delivery, surface reaction, product removal) from the deck.
  3. Ch. 3: elementary step vs overall reaction: exponents equal coefficients only for elementary steps (K2), as two side-by-side rate-law derivations.

**Acceptance.** Gap list in report shows every required concept explained with number + figure + common error or a justified `n/a`; thin chapters grew; `verify_provenance --strict`, `verify_numbers` pass.

**Definition of done.** Chapter sizes and figure counts re-measured with the §1.2 script and reported.

---

### N18 · Bridges for medical students: mathematics, units, graphs, clinical meaning

**Accomplishes.** The audience is first-year medical students, not chemists. The sources assume `ln`, exponentials and unit manipulation. N18 adds optional, tagged *papildinājums* bridges, and ties kinetics to medical examples the topic description itself names ("pussabrukšanas laiks farmācijā un medicīnā").

**Evidence.** The topic description requires half-life in pharmacy and medicine and catalyst effects (quoted in ch. 0). `AGENTS.md` §3 says the only known papildinājumi are Lineweaver–Burk and pharmacokinetic half-life. `CHECKS.md` §4: no entry or exit test is available, so no way to calibrate which maths is assumed.

**Files.** New chapter or appendix (decision: an appendix "A. Matemātika, ko vajag", after ch. 16, to avoid renumbering the 17 chapters and the cross-reference system); `numbers.json`.

**Substeps.**
* **N18.1 Diagnose maths prerequisites.** For every formula in ch. 16, list the skills required (ln/exp inverses, slope from two points, linear regression meaning, unit cancellation, significant figures).
* **N18.2 Write 5 bridges**, one page each: (1) `ln` and `e^x` as inverses with a table; (2) slope and intercept from a line; (3) unit cancellation with `k`; (4) reading a log plot; (5) significant figures and rounding in lab reports (ties to the NBSP/decimal comma policy).
* **N18.3 Clinical anchors**, all tagged `papildinājums` with a named book (§9): exponential drug elimination and `t½`, steady state after several half-lives, enzyme inhibitor drugs as competitive (e.g. methotrexate–DHFR is the standard textbook example; **verify in the pharmacology/biochemistry text before including**), irreversible inhibition (aspirin–COX is a standard example; verify), methanol/ethanol competition for alcohol dehydrogenase (already in ch. 7 as "Etanols ir konkurējošs substrāts").

**Subtasks.**
* **N18-S1 Half-life in medicine.**
  1. Worked example: a drug with `t½` = 6 h; fraction left after 1, 2, 3, 4 half-lives (computed, 50 / 25 / 12.5 / 6.25 %).
  2. State the rule "about 4–5 half-lives for near-complete elimination" only after a textbook check; otherwise compute the exact fractions and let the student judge.
  3. Link to F06 (dosing instrument).
* **N18-S2 Graph-reading drills.**
  1. Use the MU question figures (Q3–Q5, Q10, Q11) redrawn as SVG with a tolerance rule for read-offs.
  2. Provide a "how to read off K_M" 3-step protocol (already partly in ch. 10 as the "reading protocol", verified by `verify_enzyme`).
  3. Extend the drill to the lab data.
* **N18-S3 Units ladder expansion.**
  1. The units "ladder" exists (Table 16 + unit ladder, tested by `verify_units`); add a worked unit check for each of the three orders.
  2. Add `mol·L⁻¹·s⁻¹ → µmol·min⁻¹` conversion examples (the log says 1 µmol·min⁻¹ ≈ 1.67·10⁻⁸ mol·s⁻¹).
  3. Verify numerically.

**Acceptance.** Appendix A exists, every claim tagged, no unverified page citations, `verify_provenance --strict` pass.

**Definition of done.** A student can complete the five bridges in ≤ 30 minutes (state as an *estimate*, not a measured value, unless someone tests it).

---

### N20 · SVG program: more figures, and more correct figures

**Accomplishes.** (1) Fill the figure gaps found in §1.2; (2) audit every existing SVG for correctness of axes, units, curve shapes, label sizes and accessibility; (3) generate figures from `numbers.json` so they cannot drift from the numbers.

**Evidence.**
* 12 plates + 4 instruments. 0 figures in ch. 1, 2, 3, 5, 8. Ch. 16 has 6 SVGs but 0 `<figure>` (they are formula-sheet panels, check whether they have captions).
* Hand-drawn source figures (MU Q10: "hand-drawn", curve reaches v_max exactly at C ≈ 8, K28). The HTML says "zīmēts ar roku" and keeps a read-off tolerance. Good.
* Static curves are drawn as long polylines (`L85.87 245.00 L87.48 245.00 …`; ch. 4 = 67 kB for 4 SVGs; ch. 6 = 131 kB for 6): accurate but heavy; see D07.
* `DESIGN.md` §3: SVG label sizes 12/13 user units; maximum width 1.2 × viewBox so labels render 12–14.4 px. This is a clever rule; keep it.

**Files.** HTML SVG blocks; new `tools/build_figures.py` (generator for new static plates); `tools/verify_figures.py`; `numbers.json`.

**The figure plan (new SVGs, each with `<title>` and `<desc>`, caption, source tag):**

| # | Ch | Figure | Content | Source tag |
|---|---|---|---|---|
| S01 | 1 | C(t) with secant and tangent | average vs instantaneous rate; Δt label | papildinājums |
| S02 | 2 | Heterogeneous reaction pipeline | 3 steps from the deck: delivery, surface, removal | avots · deck |
| S03 | 3 | Elementary vs overall | A + B → C; mechanism with two steps; rate-limiting highlighted | avots + labojums K2 |
| S04 | 5 | k vs T and ln k vs 1/T | two Ea values; slope −Ea/R | papildinājums |
| S05 | 5 | γ ↔ Ea map | γ = 2, 3, 4 vs Ea at 300 K, both methods | avots + [my calc] |
| S06 | 8 | Catalysed vs uncatalysed profile | intermediates are minima; Ea,f and Ea,r; ΔH unchanged | avots · deck + papildinājums |
| S07 | 8 | Heterogeneous catalysis cycle | adsorption → surface reaction → desorption | avots · Kinetika p.12 |
| S08 | 9 | Lock-and-key vs induced fit | two panels; flag K24 | avots + papildinājums |
| S09 | 10 | Progress curve and initial rate | tangent at t = 0 | papildinājums |
| S10 | 11 | Double-reciprocal plots for 3 inhibition types | three lines families, intercepts labelled | papildinājums (Lineweaver–Burk) |
| S11 | 12 | Apparatus and tube schematic | tubes with volumes, hot/cold bath, white tile with cross | avots · 5LW |
| S12 | 12 | Autocatalysis S-curve | model, induction period | papildinājums (labelled model) |
| S13 | 6 | Order × t½ trend panel | t½ vs C₀ for orders 0/1/2 | avots + papildinājums |
| S14 | 4 | Collision geometry | effective vs ineffective orientation | avots · Kinetika p.3 |

**Substeps.**
* **N20.1 Audit existing SVGs.** For each of the 19 content SVGs: axis labels and units (compare with `notation.md`), tick values computed not typed, curve shape correct (e.g. the Michaelis curve approaches v_max asymptotically; the Boltzmann curve is zero at E = 0 and has a high-energy tail), label sizes 12/13, `title`/`desc` informative (not "Attēls"), source tag. Output a table with PASS/FIX.
* **N20.2 Write the generator.** One Python module `tools/build_figures.py` that emits SVG from `numbers.json` using the shared vocabulary (N19) and the viewBox/label rules; `--check` mode for idempotence like `build_orderfig.py`.
* **N20.3 Insert and verify.** Insert S01–S14 in order of benefit (S06, S04, S10, S01 first); run `verify_figures`, `verify_links`, `verify_a11y`, print check.

**Subtasks.**
* **N20-S1 Energy profile family (S06 and the ch. 4 profile).**
  1. One generator function for reactant/product levels, Ea(f), Ea(r), ΔH sign convention (ΔH = Ea(fwd) − Ea(rev)).
  2. Exothermic and endothermic variants and a two-step variant; label "aktīvais komplekss" at maxima and "starpprodukts" at minima.
  3. Test: ΔH recomputed from the plotted heights equals the number in `numbers.json`.
* **N20-S2 Correct-by-construction curves.**
  1. Maxwell–Boltzmann: compute the actual distribution `f(E) ∝ E^{1/2} e^{−E/RT}` (3D translational kinetic energy), normalise, tail fractions from integration; confirm 1.88 at 50 kJ·mol⁻¹.
  2. Michaelis–Menten: hyperbola; do not clip at v_max.
  3. Integrated laws: straight-line panels computed; the first three half-lives marked.
* **N20-S3 Accessible figure text.**
  1. `desc` ≤ 2 sentences stating what to notice, not what is drawn.
  2. Long-description in a `<details>` for complex plates (the pattern exists in `fallback-details`).
  3. Check by reading each `desc` without the picture: can you answer the figure's purpose question?

**Acceptance.** Figure count rises from 12 plates to ≥ 22; each new figure has source tag, caption, `title`, `desc`; all numbers come from `numbers.json`; `verify_figures` extended for the new classes; print page count re-measured.

**Definition of done.** A figure index table (the document has one: "figure index" in `verify_figures`) updated; the audit table in the report; byte-size impact stated (D07).

---------------------------------------------------------------------

## 4. TEN FEATURES (additions on top of the 20 tasks)

Common rules for every feature: native HTML controls; no storage, no cookies, no external request (DESIGN §8); works without JavaScript as a static explanation plus worked example; state, if any, in the URL hash only (N13-S2); announcements via the one-polite-region pattern (DESIGN §11); numbers from `numbers.json`; provenance tag on every claim; print shows the static fallback; keyboard-operable; `lang="lv"` with English terms marked.

Feature types used: *calculator*, *instrument* (live plot), *diagnostic*, *generator*, *drill*, *print product*.

---

### F01 · Practice mode for the 40 self-check answers (type: drill)

* **Why useful.** Reading an answer is not retrieval. The exam is a test; the best study aid for a test is attempting items first. The 47 Q&A blocks already hide answers in "exam print mode"; screen mode shows them.
* **What it accomplishes.** The student sees only the question, commits to an answer (types a number, picks an option), then reveals the model answer and the matching four-part error block.
* **Conflict to resolve first.** Chapter 15 contains an explicit note (line ≈ 2820) that the document keeps no storage, cookies, points or randomness and no shuffled question order. F01 is therefore **a decision for the user**: lifting "no shuffled order" is a design change. Proposal: *deterministic* shuffle from a seed in the URL hash (no `Math.random`), no score, no storage.
* **How to implement.** `details` per question already exists; add an `<input>` or radio group inside the question block (generated by `build_selfcheck.py`, so edit the generator, not the HTML), a reveal button, and a pure function comparing numeric input against `numbers.json` with tolerance. Multiple-choice items are built from the error-block wrong answers (N08-S1).
* **What an agent changes.** `tools/build_selfcheck.py` (emit controls), `tools/verify_selfcheck.py` (check controls and fallback), CSS (new component, reuse tokens), script (≈ 60 lines), `tools/check_a11y.mjs` (keyboard test).
* **Acceptance of integration.** With script off: the page looks exactly as today. With script on: 12 MC + all numeric items answerable; reveal shows the answer and links to the error block; `verify_selfcheck` and `check_a11y` pass; print and exam print unchanged (page counts equal).
* **Definition of done.** User approval of the rule change is recorded in the report; seeded shuffle reproducible by URL; no `localStorage`/`Math.random` strings in the script.

### F02 · "Kāda ir k vienība?" unit finder and converter (type: calculator)

* **Why useful.** K8 (source writes `k` in mol/L·s for everything) is the mistake students *copy*. A tiny tool that gives the unit of `k` for order *n* (`mol^(1−n)·L^(n−1)·s⁻¹`) and converts `µmol·min⁻¹ ↔ mol·L⁻¹·s⁻¹` given a volume turns a stated rule into an experience.
* **How.** Two native `number`/`select` controls and an `<output>`; derive the unit from `v = kCⁿ` by symbolic exponent arithmetic in the script (no lookup table beyond orders 0–3 plus "n" general); show the derivation line.
* **Agent changes.** Ch. 6 or 16 insert; script function `kUnit(n)`; unit tests in `test_instruments.mjs` (n = 0, 1, 2, 3, 0.5); `notation.md` stays source of truth (verify_units must still pass).
* **Acceptance.** Output matches Table 16 for 0/1/2; for 0.5 it prints `mol^0,5·L^−0,5·s⁻¹` (decimal comma, U+2212); fallback table of orders 0–3 present without JS.
* **Done.** Tests green; one worked example under the tool.

### F03 · Lab-data fit checker: "Kursa metode" next to "Derīgā analīze" for *your* numbers (type: instrument)

* **Why useful.** The lab chapter already has three panels, but the data are the lecturer's two sets. A student who measures their own times needs the same analysis with their numbers (and to see why the course method gives two different `k` values).
* **How.** Reuse ch. 12's panels: input table accepts 5–8 rows (volume, time), computes true C (with the 10/12 factor), `ln C`, `ln(1/t)`, slope, R², `t·C`; prints the verdict sentence from a fixed set (n between 0.7 and 1.3: "aptuveni pirmā pakāpe thiosulfātam", otherwise "pārbaudiet mērījumus"). Input validation accepts decimal comma and point.
* **Agent changes.** Ch. 12 script (extend, keep pure functions separate), tests for known sets (the two key sets must reproduce n = 0.85/R² 0.997 and n = 0.72/R² 0.908), `verify_numbers` unchanged.
* **Acceptance.** Key sets reproduce stored numbers to displayed precision; invalid input yields a visible message, never `NaN`; screen-reader announcement tested.
* **Done.** Tests pass; one paragraph telling the student to submit the course method with the caveat (AGENTS §10.11) stays above the tool.

### F04 · Lab-report scaffold (type: generator + print product)

* **Why useful.** The lab report is uploaded to e-studijas and graded. A scaffold that lists required sections, with empty spaces and the computed values filled from F03, reduces missed items.
* **How.** A `?mode=report` print view (same mechanism as `?mode=exam`) containing: aim, table, graph 1, graph 2, k and t½ as the course asks, the tag "kursa metode — labojums", a caveat paragraph and a checklist. Optional "Lejupielādēt .txt" via a Blob URL (no network, no storage).
* **Agent changes.** CSS print block, small script, markup in ch. 12; update `verify_print.py` for a fourth product and `check_print.py` expectations.
* **Acceptance.** PDF renders with 1–3 pages (measure); no raster; empty spaces large enough for hand-written graphs.
* **Done.** The scaffold is labelled `Nav oficiāla veidlapa`; lecturer's actual requirements remain "kursa atbildība" (as ch. 0 says).

### F05 · Misconception diagnoser (type: diagnostic, static tree)

* **Why useful.** The error index (Table 13, 55 rows) is searchable by chapter, but students do not know *which* mistake they make. A short question set ("Kāda ir tava atbilde?") routes to the right error block.
* **How.** A decision list of 10–15 "Ja tu domā, ka… → skatīt K#" entries rendered as `<details>` (works without JS); with JS, a `<select>` filters by symptom ("pusperiods ir vienmēr nemainīgs", "katalizators maina līdzsvaru", "Ea ir enerģija, ko piegādā").
* **Agent changes.** Derive entries from `provenance_inventory.csv`/Table 12/13 data; a generator `tools/build_diagnoser.py` with `--check`; new verifier rule that every entry points to an existing `#def-K…` anchor.
* **Acceptance.** All 36 defect anchors reachable from ≥ 1 symptom or marked "not an exam risk"; links verified by `verify_links`.
* **Done.** Generator idempotent; fixture with a broken anchor fails.

### F06 · Half-life and dosing instrument (type: instrument; *papildinājums*)

* **Why useful.** The topic description explicitly asks for half-life in pharmacy and medicine, but the sources teach `t½` mainly in nuclear-physics terms (K14). Medical students need accumulation and washout intuition.
* **How.** Sliders: `t½` (h), dose interval (h), dose; plot of amount versus time for first-order elimination, single dose and repeated doses; read-outs: fraction left after n half-lives, peak/trough ratio. Closed forms: `A(t) = A₀ e^(−kt)`, `k = ln2/t½`; accumulation factor `1/(1 − e^(−kτ))` for repeated equal doses with instantaneous absorption (state the assumption in the text).
* **Agent changes.** New instrument following DESIGN §11 markup, `numbers.json` entries for the fixed example, tests, tagged `papildinājums` and a named pharmacokinetics text (§9; verify before naming a chapter).
* **Acceptance.** `t½` = 6 h, τ = 6 h gives peak/trough ratio 2 and accumulation factor 2 (exact), computed and tested; text states "first-order, one-compartment, instantaneous absorption" assumption.
* **Done.** Clear label "nav klīnisks ieteikums"; no drug-specific dosing advice (rule inherited from the current text "ne konkrētu zāļu ieteikums").

### F07 · Inhibition identifier from two curves (type: drill + instrument)

* **Why useful.** MU Q10 and Q11 ask students to *recognise* inhibition type from curves. Presently ch. 11 explains types; a drill makes recognition the task.
* **How.** Show a computed pair of curves (control and inhibited) and a double-reciprocal plot; the student chooses among competitive / noncompetitive / mixed / uncompetitive; reveal explains by v_max and K_M changes. Parameters seeded by hash (deterministic).
* **Agent changes.** Ch. 11 insert; computation reuses the Michaelis–Menten functions from N13; matrix from N10-S1 linked; Lineweaver–Burk tagged `papildinājums` (already so in ch. 10).
* **Acceptance.** For every preset the apparent v_max and K_M are verified against closed forms in tests (competitive: v_max same, K_M,app = K_M(1 + I/Ki); noncompetitive pure: v_max,app = v_max/(1 + I/Ki), K_M same; uncompetitive: both divided by (1 + I/Ki)).
* **Done.** Tests green; wording for "nekonkurentā" follows N01 decision.

### F08 · Arrhenius workbench (type: calculator + plot)

* **Why useful.** Ea from two temperatures is the single most exam-likely calculation after half-life; γ ↔ Ea is a recurrent confusion (K16).
* **How.** Inputs `k₁`, `T₁`, `k₂`, `T₂` → `Ea = R ln(k₂/k₁)/(1/T₁ − 1/T₂)`; shows `ln k` vs `1/T` with the two points and the line; second tab: γ → Ea (differential and two-point) with the two columns of `CHECKS.md` §5 side by side and an explanation why they differ by ~2 kJ·mol⁻¹.
* **Agent changes.** Ch. 5 (which currently has no figure) gets the first instrument; tests with the three γ rows; units in K and J·mol⁻¹ inside the formula, kJ·mol⁻¹ displayed.
* **Acceptance.** γ = 2/3/4 return 51.9/82.2/103.7 (differential) and 54/85/107 (two-point) to the displayed precision; invalid input (T ≤ 0, k ≤ 0) gives a message.
* **Done.** Added to the figure index; tests green.

### F09 · Reaction-profile builder (type: instrument)

* **Why useful.** Energy-profile questions (MU Q3–Q4) reward manipulating Ea and ΔH. Seeing that a catalyst lowers both Ea(fwd) and Ea(rev) by the same amount and leaves ΔH unchanged is a conceptual breakthrough that static figures only assert.
* **How.** Sliders for reactant level, product level, Ea; checkbox "ar katalizatoru" adds a lower barrier and, optionally, an intermediate; labels computed; the occlusion toggle from N11-S3 hides them.
* **Agent changes.** Share the profile generator from N20-S1; DESIGN-compliant controls; test ΔH identity.
* **Acceptance.** `ΔH = Ea(f) − Ea(r)` holds in every state; catalyst changes Ea(f) and Ea(r) equally; ΔH and K unchanged (numeric test).
* **Done.** Fallback figure and caption present; print shows static.

### F10 · Bilingual flashcards, printable (type: print product + drill)

* **Why useful.** Terminology is a recorded pain point (14. nodaļa, 54 kB) and many students meet English-language textbooks and exam questions.
* **How.** From `termbase.json` generate (a) a two-column LV↔EN table that prints as cut-out cards (8 per A4), (b) on-screen "show / hide" per column using a native checkbox; the learner's check state is not stored.
* **Agent changes.** `tools/build_glossary.py` additional output block; CSS print grid; verifier that every termbase row appears exactly once.
* **Acceptance.** 71 terms (or the number N01 settles) printed with no card split across pages; English terms carry `lang="en"` (N02).
* **Done.** Page count recorded; the print product listed in ch. 0.

---------------------------------------------------------------------

## 5. FIVE BUG-FIXING TASKS

Each lists: symptom, evidence, root cause (confirmed or suspected), fix, regression guard, acceptance, done.

### B01 · Overall verdict says PASS while two tools exit non-zero

* **Symptom.** `CHECKS.md` header: "Overall verdict: `PASS`". The same file shows `lint.mjs` "5 FAIL, 3 WARN — fix the FAILs" and `inspect.mjs` "5 FAIL, 6 WARN — not done", both labelled `DEFENDED`.
* **Evidence [verified].** `verify/run_all.py` passes a `defended` flag per suite; for such suites a non-zero exit is turned into `DEFENDED (…)` and excluded from `any_unexpected_fail` (lines ≈ 166–178), and line ≈ 199 prints `FAIL` only if `any_unexpected_fail`.
* **Root cause.** By design the two heuristic tools are advisory, but the headline collapses "advisory FAIL" into "PASS".
* **Fix.** Headline becomes `PASS (10 static + 7 dynamic suites) · ADVISORY: 2 tools report 10 FAIL findings (see §3)`; the tool tokens remain defended; exit code unchanged. Add the count of advisory FAILs as a number extracted from each tool's last line.
* **Guard.** A fixture that forces a defended suite to exit 1 and expects the headline to contain `ADVISORY`.
* **Acceptance.** Re-run produces the new headline; `CHECKS.md` regenerated (only when the user agrees to overwrite; otherwise write to a new file and show a diff).
* **Done.** Report quotes before/after headline.

### B02 · Counts written inside the change log are not machine-checked, and one looks wrong

* **Symptom.** Ch. 17 says "33 saites teksta atzīmēs “labojums · K…”" (line ≈ 2792). A crude regex count of `labojums` tag spans in the file gave **40** (42 in a looser match). The legend and chapter 0 explanatory mentions may inflate this, so the number may be correct; **I could not confirm either way** within this session.
* **Evidence.** `language_log.md` itself recorded an earlier false count ("33 izstrādātas atbildes; document has 39", fixed later). Other counts in ch. 17 (29 tables, 55 index rows, 423 `data-num` spans on 200 ids, 124 pages) are covered by verifiers; this one is not.
* **Root cause.** Prose counts are typed by hand unless wrapped in `data-num`; the verifier only checks wrapped numbers.
* **Fix.** (1) Count properly: parse the HTML, count `.prov` spans whose text starts with `labojums`, outside ch. 0/ch. 17 explanatory text; (2) wrap every count in the log as a `data-num` backed by `numbers.json`; (3) add `verify_numbers` rule: any integer immediately followed by a noun from a list (`tabulas`, `saites`, `atzīmes`, `rindas`, `lappuses`, `jautājumi`) that is not wrapped fails as a warning.
* **Guard.** Fixture with a wrong count (exists in spirit: `wrong_number.html`; add a *prose count* variant).
* **Acceptance.** The count is derived and wrapped; verifier flags a deliberately altered count.
* **Done.** Report states the true number and whether the old text was right.

### B03 · Instrument inputs at the limits (suspected NaN / Infinity)

* **Status: suspected, not reproduced.** I did not drive the sliders. This is a hypothesis from the way scientific sliders usually fail, and from the fact that the repo's only numeric JS test covers half-lives.
* **Repro plan.** In headless Chrome set each control to its min and max and to out-of-range typed values; read the DOM for the strings `NaN`, `Infinity`, `−Infinity`, `undefined`, and collect console errors. Candidates: `E_a = 0`, `T` at slider end, `[I]` = 0 with an inhibitor selected, `K_i` = 0, the number field in the lab accepting `10,0`, negative volumes.
* **Fix.** Guard every division; return a visible `—` with an explanatory `aria-live` text rather than a number; clamp inputs; reject non-numeric entries with an inline message.
* **Guard.** `tools/test_instruments.mjs` (N13) with these cases.
* **Acceptance.** 0 forbidden strings across ≥ 200 randomised-but-seeded states; 0 console messages.
* **Done.** Either "bug confirmed and fixed" or "not reproducible in N states" is reported; do not claim a fix for a bug not seen.

### B04 · Defect register: English severity word and an undocumented code

* **Symptom.** Table 12 (Pilns defektu reģistrs) uses severity codes `A`, `A/B`, `B`, `C`, `D` and the English word **`note`** [verified: `<td class="sev">note</td>`, line 1739]; the column header is "Sev.". `language_log.md` had listed "`note` is English" for task T06 and the header as unlabelled; the header is now present but the English value remains.
* **Root cause.** The register was transcribed from `AGENTS.md` §5 (which uses `note`) and the Latvian conversion was not applied to the value.
* **Fix.** Replace `note` by a Latvian label (`piez.` or `ievērojams`, decide in N01), add a legend line above or below the table: "A zinātniska kļūda · B pretruna avotā · C terminoloģija/pierakstu · D izkārtojums · piez. piezīme" and the same in Table 13's index; make the severity cells `<abbr title=…>` for hover and screen readers.
* **Guard.** `verify_tables.py` rule: severity cells ∈ allowed set; `lint` for English words in Latvian table cells (a short stoplist: note, see, and, the).
* **Acceptance.** 0 occurrences of `note` as a cell value; legend present; `verify_tables` passes.
* **Done.** Diff shows only that table and its legend.

### B05 · Accessibility gaps the project already admits

* **Symptoms (all documented in `DESIGN.md` §11 "Known limits").** (a) English terms not marked `lang="en"` (only 1 occurrence in the file [verified]); (b) the WCAG 2.2 24 px target size not measured for inline term links; (c) no screen reader, Firefox or Safari were run.
* **Fix path.** (a) via N02; (b) measure all interactive elements with a script (bounding boxes via Chrome CDP): 78 `term-link`s, buttons, summaries; (c) run NVDA/Orca if the user has them, Firefox headless for layout and the keyboard walk; **state clearly that Safari/VoiceOver cannot be tested on this Linux machine**.
* **Guard.** Extend `check_a11y.mjs` with the target-size check and the `lang="en"` check (every termbase `en` string is inside `[lang=en]`).
* **Acceptance.** Targets: each non-inline interactive element ≥ 24 × 24 CSS px; `lang` check passes; report states which browsers/readers were *not* used.
* **Done.** The "Known limits" paragraph is shortened only by the user's decision; otherwise only the report is updated.

---------------------------------------------------------------------

## 6. WIRING (making the parts connect, and keeping them connected)

### W01 · A restore point before anything changes
* **Problem.** No git, and `language_log.md` says "Pristine original (pre-T01/T02) was kept in the session scratchpad; the project has no git." The session scratchpad is temporary and not in the workspace, so **there is no recoverable baseline** [verified: no `.git` directory].
* **Action.** Ask the user whether to `git init` in the workspace (a state change; do not do it unasked). If not approved, write a dated tarball `../Chemistry_5_backup_YYYYMMDD.tar.zst` with a `sha256sum` file, outside the working directory, and copy the HTML before each task to `Master_5_tema_kinetika_un_katalize.<task>.bak.html`.
* **Done.** The restore point exists and was restored once to a temp dir as a test.

### W02 · One entry point, correct order, honest outputs
* **Problem.** Two verifier trees (`tools/verify_*.py`, `verify/verify_*.py`) with wrappers; `CHECKS.md` is generated by `verify/run_all.py` (19 KB). The order in which generators must run (numbers → data-num spans → glossary → error index → selfcheck → print map → math alternatives → order figure) exists only in the author's memory and in scattered `--check` flags.
* **Action.** Write `tools/build_all.py` that runs generators in dependency order, then `--check` for each, then `verify/run_all.py`, and prints one table. Document it in a new `README.md` (3 screens). Do not move existing scripts.
* **Done.** One command reproduces `CHECKS.md` except for timestamps.

### W03 · Verifier fixtures for every verifier
* **Problem.** 7 negative fixtures exist (`verify/fixtures/`), covering the 7 `verify/` scripts. The `tools/` verifiers (a11y, design, figures, selfcheck, errors, ladders, enzyme, units, glossary) have none [verified: fixture list].
* **Action.** For each add one fixture and a runner entry; verify exit ≠ 0.
* **Done.** `CHECKS.md` §2 lists ≥ 16 fixture rows.

### W04 · Generated artifacts and their sources
* **Problem.** `numbers_report.md` (38 KB), `numbers.json` (76 KB), `provenance_inventory.csv` (117 KB), `glossary.*`, `termbase.json` sit in the root next to the six PDFs and the deliverable. Each says "generated; do not edit" but nothing prevents drift except the verifiers.
* **Action.** Introduce `build/` for generated files **only after the user agrees to moves** (scripts reference root paths); until then add a header line and a `--check` for each.
* **Done.** `build_all.py --check` fails if any generated file is stale.

### W05 · One state document
* **Problem.** `AGENTS.md`, `CHECKS.md`, `DESIGN.md`, `PROMPT_master_kinetika.md`, `language_log.md` each carry counts and statuses that drift (see C-series).
* **Action.** Generate `STATE.md` (counts: files, bytes, chapters, tables, figures, tags, tests; last run per check) from the actual files; link it from `AGENTS.md` header; mark `PROMPT_master_kinetika.md` as "historical: the build is done".
* **Done.** `STATE.md` is regenerated by `build_all.py`.

### W06 · Cross-links between docs and document
* **Problem.** The student document references `numbers.json`, scripts and AGENTS (N05); the docs reference line numbers that move (e.g. `language_log.md` "line 478").
* **Action.** Replace line numbers in logs with element ids; add a `verify_docs.py` that checks every `#id` mentioned in `*.md` exists in the HTML.
* **Done.** Zero dangling ids across all `.md` files.

---------------------------------------------------------------------

## 7. DEBLOATING

| ID | What | Size / evidence | Action | Risk |
|---|---|---|---|---|
| D01 | Developer change log inside the student document | ch. 17 = 124 kB (14 % of HTML) | Move developer-only parts to `CHANGELOG_BUILD.md`; keep a student-readable summary (N05) | `verify_print` page count and `#print-pages-*` anchors move: update together |
| D02 | Task-ID and script-name leakage | 23 `T##` labels + tool names in visible text | Remove/translate (N05) | low |
| D03 | `workspace_skills/` | 6.3 MB of 11 MB; `AGENTS.md` §9.3 lists ~20 skills as "not relevant here" | **Do not delete** (rule 1). Option for the user: move the whole folder out of the working directory into an archive and keep `COPY_MANIFEST.json` | user decision |
| D04 | Duplicate verifier entry points and bytecode | `tools/__pycache__/` (11 `.pyc`), `.qoder/settings.local.json` (a tool's local settings) | Add `.gitignore` if git is approved; otherwise leave and note | none |
| D05 | Root clutter | 20 files in root, 7 generated | `build/` folder (W04) after approval | path changes |
| D06 | Inline CSS 39.9 kB | unknown dead selectors (e.g. `.bar-compare` is hidden in print; used?) | Script: collect all class names in markup, list CSS selectors never matched, review by hand before removal; verify with the screenshot diff at 3 widths | medium (print selectors) |
| D07 | SVG path data | ch. 4 (67 kB, 4 SVG) and ch. 6 (131 kB, 6 SVG) store curves as 2-decimal polylines (e.g. `L85.87 245.00 L87.48 245.00 …`) | Replace by fewer points (Ramer–Douglas–Peucker with tolerance 0.15 user units ≈ invisible) or by cubic Béziers; measure bytes and a pixel diff of rendered figures; accept only if max pixel diff ≤ 1 px at 1.2 × scale | the figures are generated by scripts (`build_orderfig.py`), so change the generator, not the HTML |
| D08 | Repetition in prose | 45 error blocks restate the same wrong answers in the chapters, Q&A and index | Keep blocks; replace in-chapter repeats by one-line link (N15-S2) | low |

Bytes budget (estimates, to be measured): D01 −80…−100 kB, D07 −40…−100 kB, D06 −3…−8 kB. Target: HTML ≤ 700 kB without losing content.

---------------------------------------------------------------------

## 8. CRUSHING FALSE, STALE AND UNVERIFIABLE CLAIMS

Rule: a claim is **false** if I verified the opposite; **stale** if it was true and no longer is; **overclaim** if it is broader than its evidence; **unreproducible** if no script or step lets someone check it.

| ID | Where | Claim | Finding | Type | Fix |
|---|---|---|---|---|---|
| C01 | `AGENTS.md` §2.3 | "No `.html` for topic 5 exists yet. Producing it is the open task" | `Master_5_tema_kinetika_un_katalize.html` exists, 864,806 B | **false (stale)** | Rewrite §2.3 as "delivered; see CHECKS.md"; the file is read-only for me, so propose edit text and ask |
| C02 | `AGENTS.md` §2 | "247 files, 8.8 MB" | 311 files, 11 MB (du) | stale | regenerate from `STATE.md` (W05) |
| C03 | `AGENTS.md` §8 | `lint.mjs`/`inspect.mjs` "not yet run against any file here" | `CHECKS.md` reports both were run | stale | update row |
| C04 | `PROMPT_master_kinetika.md` | "answer all 33 self-check questions" | 33 = 22 lecture + 11 MU; the HTML answers 39 source questions (incl. 6 lab) plus 1 extra | incomplete | mark prompt "historical" |
| C05 | `CHECKS.md` | "Overall verdict: PASS" | 10 heuristic FAIL findings exist, labelled DEFENDED | **overclaim** | B01 |
| C06 | `CHECKS.md` §3 | "12 scientific plates and 7 instrument canvases" | `DESIGN.md` §11 says **four** instruments; I counted at least 7 interactive SVG containers in the markup (`dist`, 3 order panels, `mm`, ≥ 2 lab panels) | inconsistent | define "instrument" vs "canvas" once and use both words consistently |
| C07 | HTML masthead | "…katram apgalvojumam ir birka, kas rāda avotu" | `verify_provenance` lists 209 exceptions (6 transition, 8 instrument, 52 qa, 18 restatement, 125 ladder) | **overclaim** | "katram būtiskam apgalvojumam" and link to the exceptions rule in ch. 0 |
| C08 | HTML ch. 17 | "33 saites … labojums · K…" | my count 40–42 | unverified, possibly false | B02 |
| C09 | `DESIGN.md` §10 | "label collisions in 48 states at 12 widths … zero overlaps" | marked "not automated in the repo"; no script | **unreproducible** | N13.3 builds the script, then re-state |
| C10 | `language_log.md` | "Pristine original … kept in the session scratchpad" | scratchpad is temporary; not in workspace; no git | unreproducible, **no baseline** | W01 |
| C11 | `AGENTS.md` K10 / §5.1 | catalase literature Ea "single-digit kJ/mol" | RSC: 19 kJ·mol⁻¹; LibreTexts: < 8 kJ·mol⁻¹; no primary source seen | **overclaim (unsupported)** | N06-S1; HTML already says "verify" — keep it that way |

Two claims I checked and found **true** (to avoid false alarms): (1) the source PDF hash for `Kinetika.pdf` in `CHECKS.md` §6 equals what I computed today; (2) `INDEX.md` "36 skill packages" matches the 36 directories in `workspace_skills/`.

---------------------------------------------------------------------

## 9. SOURCES: BOOKS FIRST

### 9.1 How to use this list

* "Verified" below = *the catalogue or institutional page found in this session says so*. Nobody opened the books. **Edition, ISBN and chapter must be confirmed from the copy in hand** before the HTML cites them.
* A citation in the HTML takes the form `papildinājums · Autors, Nosaukums, izd., nodaļa/sadaļa`. No page numbers unless an agent (or the user) has looked at the page.
* Disagreement between sources is recorded, not smoothed (K10 is the standing example).

### 9.2 Textbooks (physical and enzyme kinetics)

| Book | Edition / ISBN (as listed) | Use it for | Link / note |
|---|---|---|---|
| K. J. Laidler, *Chemical Kinetics* | 3rd ed., Harper & Row, 1987, ISBN 0-06-043862-2 (a Pearson India reprint is listed as 978-81-317-0972-6) | order vs molecularity, collision theory, Arrhenius, mechanisms, catalysis (N06-S3, N17-S1) | [catalogue record](https://ci.nii.ac.jp/ncid/BA01450356) |
| J. H. Espenson, *Chemical Kinetics and Reaction Mechanisms* | 2nd ed., McGraw-Hill, 1995, ISBN 0-07-020260-5 (1st ed. 0-07-019667-2) | integrated laws, data fitting, mechanisms (N07, F03) | [catalogue record](https://theses.univ-nantes.fr/vufind/Record/PPN032369042/Details) |
| P. Atkins, J. de Paula, J. Keeler, *Atkins' Physical Chemistry* | 11th ed., Vol. 1 "Thermodynamics and Kinetics" listed as ISBN 9780198817895; kinetics is "Focus 17" in the 11th ed. (chapter 20 in the 10th) per catalogue snippets | kinetics review, Boltzmann distribution, Arrhenius (N06, N17, F08) | [bookstore listing](https://campusstore.miamioh.edu/atkins-physical-chemistry-11e-volume-1/bk/9780198817895); numbering must be checked in your edition |
| R. J. Silbey, R. A. Alberty, M. G. Bawendi, *Physical Chemistry* | 4th ed., Wiley, 2004, ISBN-13 9780471215042 (a 2005 printing is listed as 9780471658979) | complex reactions, induced reactions (K17), enzyme kinetics | [listing](https://www.booksinbelgium.be/nl/b/physical-chemistry-robert-j-silbey-9780471215042). One search summary printed "0-471-21504-7" as ISBN-10; the ISBN-13 above corresponds to 0-471-21504-X, so confirm on the copyright page |
| A. Cornish-Bowden, *Fundamentals of Enzyme Kinetics* | 4th ed., Wiley-VCH, 2012, ISBN 978-3-527-33074-4 (ebook and print numbers differ between sellers) | steady-state vs rapid-equilibrium, K_M meaning, inhibition (N06-S2, F07) | [publisher](https://www.wiley-vch.de/de/fachgebiete/naturwissenschaften/fundamentals-of-enzyme-kinetics-978-3-527-33074-4) |
| I. H. Segel, *Enzyme Kinetics: Behavior and Analysis of Rapid Equilibrium and Steady-State Enzyme Systems* | Wiley, 1975; Wiley Classics 1993, ISBN 978-0-471-30309-1 | unireactant derivations, inhibition patterns | [catalogue](https://katalog.muni.cz/Record/MUB01000351309/Description) |
| D. L. Nelson, M. M. Cox, *Lehninger Principles of Biochemistry* | 8th ed., Freeman/Macmillan 2021, ISBN 978-1-319-22800-2 (print, per retailers; other numbers on the same page are eText/paperback) | enzyme chapter for medical audience; catalysis and inhibition at textbook level | [retail listing](https://www.ecampus.com/lehninger-principles-biochemistry-8th/bk/9781319228002&pos=1) |
| S. Čornaja, *Fizikālā ķīmija* | RTU Izdevniecība, 2008, 135 pp. (kinetics part); ISBN not found | **the Latvian-language kinetics text on an RTU course list**; terminology check for N01 | [RTU course KNF303](https://stud.rtu.lv/rtu/discpub/printDisc.10930/KNF303_Kinetikas_un_katalizes_pamati.pdf) |

Books I know exist but that were **not** looked up this session (treat as leads, confirm before citing): J. Berg, J. Tymoczko, G. Gatto, L. Stryer, *Biochemistry* (enzyme kinetics and inhibition); A. Fersht, *Structure and Mechanism in Protein Science* (Freeman, 1999); R. A. Copeland, *Enzymes* (Wiley-VCH, 2nd ed.); K. A. Connors, *Chemical Kinetics: The Study of Reaction Rates in Solution* (VCH, 1990); J. I. Steinfeld, J. S. Francisco, W. L. Hase, *Chemical Kinetics and Dynamics* (Prentice Hall, 2nd ed.). For the **pharmacokinetic half-life** (F06, N18) pick one pharmacology or clinical biochemistry text the user's course already uses; none was identified.

### 9.3 Standards and primary literature

| Item | What it supports | Status |
|---|---|---|
| [IUPAC Gold Book: order of reaction (O04322)](https://goldbook.iupac.org/terms/view/O04322) | order is defined from the empirical rate law; for elementary reactions partial orders equal stoichiometric numbers | seen in search results |
| [IUPAC Gold Book: molecularity (M03989)](https://dev.goldbook.iupac.org/terms/view/M03989/plain) | molecularity = number of reactant entities in an elementary reaction (uni/bi/termolecular) | seen in search results (dev mirror; confirm on the main site) |
| Michaelis, L., Menten, M. L. (1913) *Biochem. Z.* 49:333–369 | original rapid-equilibrium analysis | bibliographic data seen |
| [Johnson, K. A., Goody, R. S. (2011) *Biochemistry* 50(39):8264–8269](https://pmc.ncbi.nlm.nih.gov/articles/PMC3381512) | English translation and reanalysis of the 1913 paper; caution on what "Michaelis constant" meant there | seen; read before writing "Michaelis assumed…" |
| Briggs, G. E., Haldane, J. B. S. (1925) *Biochem. J.* 19:338–339 | steady-state approximation | bibliographic data seen via [this symposium page](https://www.beilstein-institut.de/en/symposia/archive/enzymology/escec-2013); related: [Briggs, "A further note…", PubMed 16743595](https://pubmed.ncbi.nlm.nih.gov/16743595/) |
| Lineweaver, H., Burk, D. (1934) *J. Am. Chem. Soc.* 56:658–666 | double-reciprocal plot | from memory, **verify** |
| Koshland, D. E. (1958) *Proc. Natl. Acad. Sci. USA* 44:98–104 | induced fit (K24) | from memory, **verify** |
| Fischer, E. (1894) *Ber. Dtsch. Chem. Ges.* 27:2985–2993 | lock-and-key | from memory, **verify** |
| Arrhenius, S. (1889) *Z. Phys. Chem.* 4:226–248; van 't Hoff, J. H. (1884) *Études de dynamique chimique* | history of the rate-temperature laws (K16, K26) | from memory, **verify** |

### 9.4 Data for the catalase / H₂O₂ question (K10)

| Source | Says | Reliability |
|---|---|---|
| [RSC Education, "Investigating activation energies"](https://edu.rsc.org/feature/investigating-activation-energies/2020172.article) | uncatalysed H₂O₂ decomposition 75 kJ·mol⁻¹; catalase-catalysed 19 kJ·mol⁻¹; iodide ≈ 57; MnO₂ or Pt ≈ 49 (as summarised by the search tool) | educational, secondary |
| [Purdue demo sheet 19.6](https://chemed.chem.purdue.edu/genchem/demosheets/19.6.html) | ≈ 75 kJ·mol⁻¹ uncatalysed | educational, secondary |
| [LibreTexts demonstration page](https://chem.libretexts.org/Courses/BethuneCookman_University/B-CU%3A_CH-345_Quantitative_Analysis/CH345_Labs/Demonstrations_and_Techniques/Lecture_Demonstrations/Additional_Demos/The_Catalytic_Decomposition_of_Hydrogen_Peroxide) | catalase lowers Ea "below 8 kJ·mol⁻¹" | educational, single source |

None of these is a primary kinetics measurement. **Do not print any catalase number in the study material until a primary paper or a book table is found and its conditions are recorded** (enzyme source, pH, temperature range).

### 9.5 Teaching literature on the thiosulfate clock

Only revision notes and practical guides were found (not citable in a medical-chemistry document), for example [a UK practical guide on the initial-rates method](https://www.chemistrystudent.com/ocr-a-level/required-practicals/rates-of-reaction--initial-rates-method.html) saying that 1/time is an *approximation* for rate. A peer-reviewed treatment (e.g. in *Journal of Chemical Education*) should be sought by title search in a university library; none was confirmed this session.

### 9.6 Suggested search routes for the next agent

1. National Library of Latvia catalogue (LNB) and RSU / LU / RTU library catalogues for "ķīmiskā kinētika", "fizikālā ķīmija", "medicīniskā ķīmija": confirm the ISBN of Čornaja and look for an RSU medical chemistry textbook (the course's own list was not in the workspace).
2. AkadTerm (termini.gov.lv) for the 71 termbase entries (N01).
3. Journal of Chemical Education archive: clock reactions, Arrhenius with two points, teaching the Michaelis–Menten derivation.
4. Pharmacology textbook used by RSU for half-life and steady state.

---------------------------------------------------------------------

## Appendix A · Commands that reproduce my measurements

```bash
cd /home/robertsrff/Chemistry_Med/Chemistry_5
F=Master_5_tema_kinetika_un_katalize.html
# structure per chapter (the table in §1.2)
python3 - <<'PY'
import re
s=open('Master_5_tema_kinetika_un_katalize.html',encoding='utf-8').read()
for p in re.split(r'(?=<section class="chapter" id="ch\d+")',s)[1:]:
    cid=re.match(r'<section class="chapter" id="(ch\d+)"',p).group(1)
    print(cid,'svg',len(re.findall('<svg',p)),'table',len(re.findall('<table',p)),
          'math',len(re.findall('<math',p)),'qa',len(re.findall(r'class="qa"',p)),'kB',len(p)//1024)
PY
# static verifiers (each ends with RESULT: PASS|FAIL)
for c in "verify/verify_links.py $F" "verify/verify_tables.py $F" "verify/verify_text.py $F --strict" \
         "verify/verify_terms.py $F" "verify/verify_numbers.py $F numbers.json" \
         "verify/verify_provenance.py $F --strict" "tools/verify_design.py $F" "tools/verify_figures.py $F" \
         "tools/verify_a11y.py $F" "tools/verify_selfcheck.py $F"; do python3 -I $c | tail -1; done
sha256sum $F                       # expect 02e2d987…eff8 until the first edit
grep -c 'position:fixed' $F        # expect 0
ls -d .git                         # expect: No such file or directory
```

## Appendix B · Index of IDs

| Group | IDs |
|---|---|
| Tasks | N01 terminology spine · N02 notation and language marks · N03 Latvian proofreading pass 2 · N04 prose voice · N05 leakage purge · N06 science audit vs books · N07 lab chapter · N08 self-check set · N09 quality gates · N10 matrices and morphology · N11 scrubbers and occlusion · N12 print and greyscale · N13 instrument engine tests · N14 reading navigation · N15 anti-slop redesign · N16 restyle · N17 explanations · N18 bridges for medical students · N19 retexturing · N20 SVG program |
| Features | F01 practice mode · F02 unit finder · F03 lab fit checker · F04 lab-report scaffold · F05 misconception diagnoser · F06 half-life and dosing · F07 inhibition identifier · F08 Arrhenius workbench · F09 profile builder · F10 flashcards |
| Bugs | B01 verdict wording · B02 hand-typed counts · B03 instrument limits (suspected) · B04 English severity word · B05 admitted accessibility gaps |
| Wiring | W01 restore point · W02 one entry point · W03 fixtures for all verifiers · W04 generated artifacts · W05 state document · W06 cross-links |
| Debloating | D01–D08 (§7) |
| False claims | C01–C11 (§8) |

## Appendix C · One-paragraph summary for the user

The workspace is in better shape than most: ten static verifiers pass today, numbers are generated, the design is already free of the obvious generated-look tells. What is weak is (1) five core chapters with no figure and thin explanations, (2) 14 % of the file being a developer log with leaked task IDs, (3) a headline "PASS" that hides ten advisory failures, (4) several documents whose counts no longer match the files, (5) no restore point and no version control, and (6) a catalase activation energy that the working notes call "single-digit" but that published educational sources put at 19 and "below 8" kJ·mol⁻¹. The plan fixes these in five waves, starting with a backup and the claim corrections.
