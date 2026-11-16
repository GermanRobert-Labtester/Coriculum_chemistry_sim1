# OPEN_ISSUES.md — long-form open issues

Companion to `AGENTS.md` §2. The one-line index for every issue stays in
`AGENTS.md` (that file is the governance contract and must stay small); this
file carries the full description, the evidence and the required fix for the
issues that were folded out of the table to respect the §11 byte ceiling.

Rules that are folded here are **not** deleted: the issue id, the rule, the
required fix and the epistemic tag are all still stated in `AGENTS.md` §2.

Epistemic tags: `[TESTED]` a command/measurement ran; `[INSPECTED]` the named
file or page was read; `[INFERRED]` reasoned; `[UNVERIFIED]` unresolved.

## OI-03 — HTML-Defect · `header.masthead`; CSS `.masthead` · partly closed by T17

Rule violated / gap: the masthead used the dark full-width hero treatment that
§7 forbids, and the linter `focal-point` exception in `build/exceptions.json` was
tolerated, not fixed.

**Closed by T17 [TESTED 2026-11-07]:** the hero treatment is gone. `.masthead`
now sits on the page ground (`--bg`), in the reading column, with a plain
kicker, title, standfirst and note. The dark band, the `--s-display` scale
(3.4rem / 0.98 leading / -0.03em tracking) and the masthead's dark-band tokens
are removed; the title uses a new `--s-title` token. Measured: masthead height
314 → 253 px at 1440; first lesson top 745 → 618 px (83 % → 69 % of the first
screen). The `focal-point` exception's *reason* was corrected because it
described the hero that no longer exists.

**Still open [UNVERIFIED]:** the exception itself cannot be deleted. The rule
fires when the largest type is under 4.5vw and no picture holds a third of the
viewport; a reference document that leads with a title and a contents list
satisfies neither, and satisfying it means re-creating the hero T17 removed.
This is a genuine conflict between the linter's landing-page model and a study
reference, not a defect in the page. Resolving it needs a decision: either
accept the exception permanently for reference documents (the current state,
now with a true reason), or add a document/reference mode to the inspect gate.

## OI-04 — HTML-Defect · `a.skip[href="#saturs"]` · [INSPECTED]

Rule violated / gap: the skip link targets the table of contents, not `<main>`,
so keyboard users skip the chapter body on the first Tab.

Required fix next pass: add an `id` on `<main>` and retarget the skip link (HTML).

## OI-05 — HTML-Defect · `@media print`, `.mist` · closed by T16

Was: `border-left: 3.5pt dashed #111` — one `dashed` border in the print
stylesheet, against the §7 "no dashed callouts" rule.

Closed by T16: the print rule is now `border-left: 5pt solid var(--p-print-ink)`.
The three pillar treatments stay distinguishable in greyscale without a dash —
definition 3.5pt solid, mistake 5pt solid, correction 4.5pt double — and the
background ladder (`#f5f5f5` / `#e8e8e8` / `#dcdcdc`) still separates them.
Evidence: `build/check_layers.py` now fails on any `dashed` border; the print
PDF was rendered and inspected (202 pp, A4, text identical to the pre-T16
baseline).

## OI-18 — CSS-Arch · `build/assets/style.css` · partially closed by T16

Was: 0 `@layer`, 0 `@container`, 0 `subgrid`; tokens semantic-only.

Closed by T16: the sheet declares `reset, tokens, base, layout, components,
utilities, print` and every style rule lives inside one of them; the tokens
are split into a primitive palette (`--p-*`, the only place a raw hex may
appear), a semantic tier and a component tier (`--c-*`). Gate:
`build/check_layers.py`.

Still open: `@container` queries and `subgrid` are still absent.

## OI-19 — CSS-Arch · master, `build/build_master.py` · closed by T16

Was: 22 `style="text-align:left;padding-bottom:.4rem"` attributes on `<caption>`
elements, emitted from six sites in `build/build_master.py`.

Closed by T16: the declarations moved to the `.tcap` class
(`text-align: left; padding-bottom: 0.4rem`); the master and every chapter
fragment now carry 0 inline styles, 0 event-handler attributes and 0
`javascript:` URLs. Gate: `build/check_html.py`.

## OI-21 — Infra-Gap · `build/gate.py`, `build/check.sh` · partially closed by T16

Was: contrast, parser validity, `@layer`/inline-style lint and AGENTS.md size
gates were all missing.

Closed by T16: `build/check_layers.py` and `build/check_html.py` exist, each
with a self-test of positive, negative and boundary fixtures, and both are
registered in `gate.py` and `check.sh`.

Still open: `check_contrast.py`, the HTML parser / unique-ID / anchor gate and
`check_agents_size.py`.

## OI-25 — HTML-Defect · `@media print`, `details` · [TESTED] — CLOSED by T12

Was: §7 requires the print layer to expand all `<details>`. It did not. The
base-layer rule `details:not([open]) > :not(summary) { display: none
!important }` had specificity (0,1,2) and carried `!important`; the print rule
`details > *:not(summary) { display: block !important }` has (0,0,1), so the
closed state won. Measured before the fix: **0 of 124** quiz answers, no
why-ladder or deep-dive body, and **8 of 11 scrubber phase bodies** were
`display: none` in the 202-page print PDF.

T16 did not change this: the migration had to preserve the printed document.
T16 did change the *mechanism*, which made the fix cheap: under CSS Cascade 5
an `!important` declaration in an earlier layer beats a later layer, so a
screen-side `!important` could never be overridden by the print layer.

Closed by T12 (2026-11-07):

1. `details:not([open]) > :not(summary)` lost its `!important` and is now a
   plain `display: none` in the base layer.
2. A second, latent defect was found at the same time: `.scrub .phase-body {
   display: block }` (specificity 0,2,0) outranked the closed rule (0,1,2).
   It was invisible only because the `!important` above masked it. The rule was
   removed; a `div` is block by default and the print layer re-asserts it.
3. `build/check_layers.py` dropped the `details:not([open])` allowlist entry
   and gained a boundary fixture that fails if `!important` returns.
4. `build/check_scrubber.py` + `check_scrubber_fixtures.py` gate the whole
   contract (pre-rendered phases, no autoplay, print unfolds, reduced motion).

Measured after the fix [TESTED 2026-11-07]: 8/8 previously hidden scrubber
phases and 107/151 quiz answers print; the 44 that stay hidden are exactly the
`#pasparbaude` self-test answers that T19.3 intends to suppress, so that rule
is now live instead of dead code. Screen behaviour is unchanged (closed phases
stay closed). Page count stays 202.

Still open: `[hidden]` keeps its `!important` by design (a hidden element must
never be revealed by the blanket print expansion). No element in the master
uses the `hidden` attribute today, so the exemption is inert but harmless.

## OI-26 — HTML-Defect · `#eksamena-simulacija`, `#sim-box` · [TESTED]

Rule violated / gap: §8 requires every study aid to work and §10 lists the
simulator questions and scoring among the native static-HTML features; the
timed practice test (20 questions, radio form, 30-minute clock, CSS-counter
scoring) is in fact unreachable. The generator emits `<div id="sim-box" hidden>`;
nothing in the runtime removes that attribute (`build/assets/app.js` contains no
`removeAttribute` call), and the CSS hook `.exam-sim.has-js #sim-static { display:
none }` expects a `has-js` class that the runtime never adds — the string occurs
only in that CSS rule.

Measured in headless Chromium on the current master: before the click, `#sim-box`
is `hidden` with `display: none`, 0 of the 20 `.sim-q` blocks are visible, and
`#sim-timer` / `#sim-reset` are hidden. After clicking "Sākt prakses testu":
`data-sim-state` becomes `active`, the clock text ticks ("Atlicis: 29:59") and
the live region announces "Atlicis 30:00.", but `#sim-box` is still
`display: none` and still 0 of 20 questions are visible. The reader therefore
only ever sees the static 20-question bank `#sim-static`, which is the
no-JavaScript fallback.

Gate gap: `build/check_js_off.py` lists `sim-box` in `ALLOWED_HIDDEN_IDS` and
`#sim-box` in `JS_ONLY_SELECTORS`, so the JS-off gate accepts the hidden box and
never notices that the JS path is unreachable as well.

Found by the T16 screenshot comparison: the `simulator` pair is pixel-identical
between the baseline and the migrated master even though `.sim-q` and
`.sim-result` consume `--canvas` — the change cannot show because the subtree
is hidden.

Required fix next pass (a separate authorized task — it changes behaviour):
decide which bank is canonical (the timed form or the static bank), unhide it in
the matching state, apply and remove `has-js` consistently, and add a wiring
gate that fails when a JS-only control stays hidden in the JS-on state. T16
deliberately left this alone: the migration had to preserve behaviour.

**Closed by T16.2 (2026-11-07), by user decision:** the timed form was dropped
rather than repaired. `#sim-box`, the `#sim-data` JSON block, the `.sim-controls`
row, the `data-sim-state` machine and the three runtime rows (`setSimState`,
`quizClock`, `quizState`) are gone; the untimed native bank is now the only
practice bank. The heading no longer promises a timer ("Prakses tests (20
uzdevumi · bez taimera)") and the section states that there is no automatic
scoring. The retired markup is now a regression guard: `build/check_sim.py`
fails if any of it reappears, and `build/check_js_budget.py` fails if an
unregistered function or an unregistered JSON block returns. Cost: −34.4 KB of
master, the runtime down to 2,203 B / 48 lines / 3 registered functions, and
the Node runtime suite down to 18 cases (the eight simulator cases were
retired, and the simulator keyboard case now checks the native `<details>`
practice bank).

## Folded changelog detail

The 2026-11-06 structure milestone and the T15 sub-cap history were folded out
of `AGENTS.md` §11 to respect its byte ceiling; the governing summary stays in
the §11 table.

- 2026-11-06: the 15-section memo became the 12-section structure (inventory,
  DOM/CSS conventions, source registry, issue schema); the 4-language stack,
  the JS-suppression limits and registry, the Python verification contract,
  the `@layer`/token/inline-style schema and the byte budget were added; Open
  Issues moved to the 6-category schema (OI-14–22); the screenshot-grounded
  visual policy was linked from the visual skills; the file was cut from
  25,144 B to ≤ 24,576 B. Master SHA-256 `18c8581a…5115` unchanged.
- `quizClock` was budgeted at 600 B in the 2026-11-06 draft; the measurement
  showed 850 B with the JSON-driven duration, its corruption fallback and the
  live-region announcement in scope, so the sub-cap was re-measured to 900 B
  and logged. The binding cap is the script total (4,096 B / 100 lines / 2 %),
  met with 383 B and 25 lines to spare.

## OI-06 — Unverified · CSS `:root`, `:focus-visible`, print, controls · [UNVERIFIED]

Rule violated / gap: contrast in every theme, keyboard use, screen reader,
reduced motion (2 rules present) and print expansion are unmeasured. Only one
`:root` block was found, so whether several themes exist is unverified.

Required fix next pass: `check_contrast.py` over all token pairs (36 distinct
hex literals); manual keyboard, screen-reader and print runs in named browsers.

## OI-07 — Unverified · `#atomi`–`#pielikumi` · [TESTED]

Rule violated / gap: the five pillars are not mapped per Tier 1 concept.
Measured counts: 21 `.defn`, 22 `.work`, 32 `.mist`, 149 `details.q`, and no
`.mechanism` class.

Required fix next pass: a Python pillar map by section id; record absent
pillars; add the `.mech` contract (§4) before any further content work.

## OI-08 — HTML-Defect · `#elektroliti`, `#hidrolize`, `#redoks`, `#organisms` · [TESTED]

Rule violated / gap: no inline SVG in these chapters; 16 SVGs exist in the
file, none of them `<symbol>`/`<use>`.

Required fix next pass: Python-generated accessible figures through
`build/figures.py`.

## OI-09 — Infra-Gap · `build/check.sh` (14,818 B shell), `gate.py` · [INSPECTED]

Rule violated / gap: gate logic is duplicated in bash and Python; the
2026-11-02 report is historical; there is no HTML parser gate.

Required fix next pass: make `check.sh` a thin wrapper over Python and add the
parser gate (Python).

## OI-10 — Unverified · `#pielikumi #avoti`; §9 · [UNVERIFIED]

Rule violated / gap: citations are not verified claim-level; there is no
`Papildlasīšana` list.

Required fix next pass: verify each citation against a source actually read and
add the list (build).

## OI-11 — Unverified · CSS `svg text`, `svg .lbl` · [UNVERIFIED]

Rule violated / gap: rendered SVG legibility and contrast at phone, tablet and
print widths were not inspected.

Required fix next pass: render the 16 SVGs at 4 widths and measure.

## OI-12 — Unverified · `build/exceptions.json`, `check-baseline.json` · [UNVERIFIED]

Rule violated / gap: tolerated linter exceptions (`few-pictures`, `focal-point`,
`no-footage`, `still-page`) and a stale baseline; the gate was not re-run.

Required fix next pass: run the gate when authorized and update the baseline
only from measurements.

## OI-13 — HTML-Defect · `nav#saturs`; `#gloss-filter` · [TESTED]

Rule violated / gap: search is glossary-only; there is no whole-text search and
no reading progress.

Required fix next pass: a Python-built static index plus CSS `:target`/`:has()`
navigation; JS only if a registry row justifies it.

## OI-14 — JS-Bloat · `<script>` (untyped), 1 block · closed by T15

Was: 27,638 B / 624 lines = 3.79 % of the file against a cap of 4,096 B /
100 lines (6.7× over bytes, 6.2× over lines), plus 3 `application/json` blocks
(2,977 B), 25 named functions, 39 `addEventListener` calls and 109 function or
arrow sites.

Closed: the shipped script is 3,713 B / 75 lines / 0.42 % of the master, with
6 registered functions, no banned API and 1 Python-generated JSON block.
Evidence: `build/check_js_budget.py` (+ self-test).

## OI-15 — JS-Bloat · runtime templating · closed by T15

Was: `render` (scrubber stage), `calc`, `calc2`, `calcPfx`, `updatePfxUnits`,
`updateSol`, `renderSimQuestions`, `finishSim` used 12 `innerHTML` and 6
`createElement` calls — runtime DOM templating and data-to-HTML hydration.

Closed: 0 `innerHTML`, 0 `createElement`. The scrubber phases, the simulator
options and the prefix and solubility tables are pre-rendered by Python
(`build/tools.py`, `build/build_master.py`); the residual writes are
`textContent` only.

## OI-16 — JS-Bloat · UI state kept in JS · closed by T15

Was: `setMasked`/`scrubDead`/occlusion, `setTwoPass`, `syncNotes`,
`apply`/`save`/`paint` (marks), `startSim`/`updateTimerDisplay` and 2
`setInterval` calls held UI state that CSS can hold; 357 `<button>` and 215
`<input>` elements were largely JS-wired.

Closed: matrix cells are checkbox labels, the figures one radio group, the
glossary a letter index, the marks radio pairs and the simulator score a CSS
counter; 1 `setInterval` remains (the clock).

## OI-17 — JS-Bloat · 312 `<details>` / `<summary>` · closed by T15

Was: no `name=` on exclusive groups, no `<dialog>`, no `popover` and no
`<noscript>` although JS-dependent tools existed.

Closed: 3 `<noscript>` blocks — the JS-only controls are hidden and the static
fallbacks are named; the simulator is untimed without script.

## OI-23 — Unverified · master, quiz feedback prose · closed by T16.2

Was: the typography deliverable ceiling was already breached before T15 — 160
em-dashes in the built file against a ceiling of 30 (14 in
`build/content/*.html`, the rest in `build/quiz.py` misconception text). T15
added 14 by pre-rendering the simulator feedback, and T16 measured 174.

Closed by T16.2: every em dash in the master-feeding sources was rewritten as
an en dash (U+2013) — the separator in the concept-pair ARIA labels, the
misconception prose, the figure captions, the solubility legend, the glossary
and ledger cells. Measured: **0 em-dashes in the master** (ceiling 30) and
`em-dash-density = 0` across `build/content/*.html`. The four `"symbol": "—"`
placeholders in `build/definitions.py` keep the em dash because the generator
turns them into "nav" — they never reach the master.

Two further typography faults surfaced in the same pass and were fixed with it:
the deliverable's repertoire rule rejected three `«…»` pairs (U+00AB/U+00BB,
pre-existing since before T15) — they are now Latvian `„…"` quotes — and the
quote-pair rule now sees 119 balanced pairs.

## OI-24 — Infra-Gap · master file · [TESTED]

Rule violated / gap: the size ceiling was already breached before T15 — 861.2 KB
against 725 KB (pre-T15 851.4 KB). The script shrank by 26 KB but the
pre-rendered static content grew by 36 KB.

T16 measurement: 865.8 KB (886,615 B) — the layer statement, the three token
tiers and the `.tcap` class add 4.7 KB over the T15 build (861.1 KB).

Resolved on 2026-11-07 by decision, not by silent weakening: the user chose to
**raise the ceiling to 900 KB** rather than delete study material. `MAX_TOTAL_KB`
in `build/check_size.py` is now 900.0; the check itself is unchanged and still
fails the build if the master exceeds it. T16.2 brought the master to
**825.5 KB (845,314 B)** — the retired timed practice form (−34.4 KB) and the
punctuation rewrite account for the drop — which leaves ~74 KB of headroom
under the new ceiling.

Two lossless trims stay open and were deliberately not taken (the user chose
"change nothing else" for the size work): subsetting the two embedded Inter
faces to the glyphs the master actually uses (measured **−43.1 KB**) and
minifying the inlined stylesheet (measured **−18.6 KB**). Both would need a
re-run of the cascade regression, the screenshot comparison and the print
inspection before they could be accepted.

Required fix next pass: nothing for the gate. If the master approaches 900 KB
again, take the two lossless trims first and only then re-decide the ceiling.
