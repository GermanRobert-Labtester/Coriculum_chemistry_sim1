# Lab 6B Guide — Integration & Execution Plan (Expanded)

**ID convention:** `T01–T18` are this plan's execution IDs; `prior-Txx` refers to tasks from the preceding 16-chapter guide plan (e.g., `prior-T07`, `prior-T11`). Source IDs (`F01–F10`, `B01–B05`) are preserved in every task title for traceability.

**Global invariants (bind every task below):** static-only delivery (no network, no storage, no new client state); print-first artifacts with sha256 evidence; accessibility (keyboard operability, screen-reader parity, never color-only encoding); 390/768/1440 px layouts; AGENTS budgets (4,096 B JS total, ≤100 lines per change, ≤2% growth); visual verification only via lite-shot Dillo/NetSurf — Chrome solely with explicit current-turn human permission, never `dillo -f`; every check carries a negative fixture; SKIP is never reported as PASS; capture failures fail closed with exit 75.

---

## Phase 0: Critical Tooling Defects & Verification Integrity

### T01: B03 — Make the Screenshot Runner Obey the Current Visual Contract
- **Type:** `Bug Fix` (tooling policy violation)
- **Priority & Dependencies:** `P0` | Depends on: `None` (first task)
- **Target Files:** `tools/shoot.mjs`, `tools/visual-verification.md`, `tools/visual-contract.json` (new), `run.sh` (invocation site)
- **Enriched Vision & Architecture Notes:**
  - Codify the written policy as a machine-readable contract (`tools/visual-contract.json`) so runner code and documentation cannot drift apart; the contract test rejects the Chrome engine unless an explicit current-turn human flag exists.
  - Fail closed with exit 75 and structured artifact metadata (engine, viewport, exit code, reason, sha256) — never a silent fallback to a prohibited engine; the observed lite-shot Dillo exit 75 (Xvfb probe) becomes a recorded blocker, not a hidden failure.
  - Add a `--dry-run` construct-only mode so contract tests verify invocation strings without launching any browser — verification stays possible under the current display restriction.
  - Zero-bloat option preserved: if lite-shot fully covers the use case, retire the wrapper entirely rather than maintaining two invocation paths.

#### ST1.1: Contract Codification
- [ ] **ST1.1.1:** Create `tools/visual-contract.json` with fields `allowed_engines: ["lite-shot:dillo", "lite-shot:netsurf"]`, `forbidden_invocations: ["dillo -f", "chrome*"]`, `fail_closed_exit: 75`, `allow_chrome: false`; each field carries a `source` citation to `tools/visual-verification.md:1-24`.
- [ ] **ST1.1.2:** Add `--dry-run` to the runner that prints the constructed command array and exits 0 without spawning a process; acceptance: `node tools/shoot.mjs --dry-run --engine netsurf` prints the lite-shot command and spawns nothing (asserted via a stubbed `child_process` in the contract test).
- [ ] **ST1.1.3:** Implement the engine gate: Chrome is constructible only when `VISUAL_ALLOW_CHROME=1` is in the current process environment AND `plan/visual-allow.token` exists (created by the human in the same turn); otherwise the Chrome branch exits 75 with stderr JSON `{"engine":"chrome","reason":"not permitted this turn"}`.

#### ST1.2: Runner Rewrite (Surgical)
- [ ] **ST1.2.1:** Replace `tools/shoot.mjs:22-74` Dillo `-f` invocation with `lite-shot --engine dillo --url <file> --out <artifact>`; delete the Chrome fallback branch entirely (not commented out) so no prohibited path remains reachable in source.
- [ ] **ST1.2.2:** On any engine failure (including the observed exit-75 Xvfb probe), write `artifacts/visual/<slug>-<engine>-<viewport>.meta.json` containing `{engine, viewport, exit_code, reason, timestamp, sha256_of_png_or_null}` and exit 75 — fail closed, never fall back.
- [ ] **ST1.2.3:** Normalize artifact naming to `artifacts/visual/<chapter>-<engine>-<390|768|1440>.png`, with `-print` suffix for print-mode captures; acceptance: two consecutive runs on unchanged input produce identical names and identical sha256.

#### ST1.3: Contract Test & Verification
- [ ] **ST1.3.1:** Add `tools/test_visual_contract.py` with negative fixtures: (a) runner source contains `dillo -f` → fail; (b) Chrome requested without token → exit 75; (c) Chrome requested with token → command constructed in dry-run only, no launch; (d) unknown/missing engine → exit 75 with reason.
- [ ] **ST1.3.2:** Execute the contract test with a PATH shim that records any browser-binary invocation; assert zero browser launches; save the log as T01 Exit evidence.
- [ ] **ST1.3.3:** Definition of Done: contract test green; runner fails closed on the previously observed Xvfb/exit-75 condition with a metadata artifact; either one real PNG inspected (if display is permitted this turn) or an RO-signed blocker recorded in `plan/blockers.md` with owner and unblock condition.

---

### T02: B04 — Stop the Harness from Passing Checks It Did Not Perform
- **Type:** `Bug Fix` (self-test side effect + architecture mismatch)
- **Priority & Dependencies:** `P0` | Depends on: `None` (parallel with T01)
- **Target Files:** `run.sh`, `tools/verify.py`, `README.md`, `tools/negative-fixtures.json` (new)
- **Enriched Vision & Architecture Notes:**
  - Split read-only verification from mutating build so `verify` can never lie about repository state; prove non-mutation with before/after sha256+mtime snapshots.
  - Move the self-test temp fixture into a temp directory — the source-hash ledger is evidence, never scratch space.
  - One negative fixture per check plus the SKIP≠PASS rule makes the harness trustworthy evidence for every later task's DoD.
  - Align README with AGENTS caps (4,096 B / 100 lines / 2%) to kill documentation drift at the source.

#### ST2.1: Workflow Split (verify vs build)
- [ ] **ST2.1.1:** Rewrite `run.sh` into subcommands: `run.sh verify` (JS scan, self-test, budget check, link/anchor check, claim-lint once T03 lands) performing zero writes under `src/` and `plan/`; `run.sh build` (runs `build.py`, regenerates `plan/source-hashes.txt`); `run.sh all` = verify then build; acceptance: on a clean tree, `run.sh verify` leaves `git status --porcelain` empty.
- [ ] **ST2.1.2:** Snapshot sha256+mtime of `plan/source-hashes.txt` and all `src/**` files before and after `run.sh verify`; assert identical; store the snapshot pair as T02 evidence.

#### ST2.2: Non-Mutating Self-Test
- [ ] **ST2.2.1:** In `tools/verify.py:828-838`, relocate the temp fixture into `tempfile.TemporaryDirectory()`; the self-test reads the real ledger but never writes `plan/source-hashes.txt`; if a write is unavoidable, copy the ledger to temp and monkeypatch the path — never the original.
- [ ] **ST2.2.2:** Add an in-test assertion that the ledger sha256 after the run equals the pre-run snapshot; on mismatch, fail with a message naming the offending check.

#### ST2.3: Budget/Doc Alignment & Negative Fixtures
- [ ] **ST2.3.1:** Update the README C21 section: replace the 8 KiB cap with AGENTS values (4,096 B total JS, ≤100 lines added per change, ≤2% growth per change) and point to `AGENTS.md` as the authority; acceptance: `grep -ri "8 KiB\|8192" README.md` returns nothing.
- [ ] **ST2.3.2:** Create `tools/negative-fixtures.json` registering one negative fixture per check (missing dependency → SKIP; over-budget JS → FAIL; broken anchor → FAIL; prohibited engine → exit 75); add the harness rule that any check ending in SKIP is reported as `SKIP` and never as PASS.
- [ ] **ST2.3.3:** Definition of Done: before/after hash snapshot identical; simulated missing dependency yields SKIP (not PASS); injected over-budget JS yields FAIL; README diff merged; all negative fixtures execute inside `run.sh verify`.

---

## Phase 1: Claim Integrity, Runtime Diagnostics & Debloating

### T03: B05 — Crush Unsupported Chemistry and Regression Claims After Source Matching
- **Type:** `Bug Fix` (unsupported inference)
- **Priority & Dependencies:** `P0` | Depends on: `T09` (ledger schema for matrix storage), `prior-T01` (claim maps)
- **Target Files:** `src/04*:21-30`, `src/08*:28-38`, `src/11*:5-14`, `src/06*:65-67`, `src/10*:8-20`, `plan/claim-ledger.csv`, `plan/errata.md` (new), `tools/claim_lint.py` (new)
- **Enriched Vision & Architecture Notes:**
  - A claim/source/applicability matrix makes every student-facing statement traceable to a source whose conditions actually match this lab (wavelength, regression, speciation) — the 444 nm literature maximum establishes peak location only, never flatness at 440 nm without a matched spectrum.
  - Replace conclusions, not citations: the literature reference and the course instruction survive as distinct, correctly scoped statements.
  - Claim-lint with injection fixtures prevents regression of the same inference class; errata entries keep the guide honest and reviewable; all numeric values stay computationally reconciled (text edits only).

#### ST3.1: Claim/Source/Applicability Matrix
- [ ] **ST3.1.1:** Build matrix rows for each evidence site — `src/04*:21-30`, `src/08*:28-38`, `src/11*:5-14` (440 nm flatness inferred from the 444 nm maximum), `src/06*:65-67` (near-zero intercept used to support validity), `src/10*:8-20` (mono-complex dominance unverified) — with columns `claim_id, file:line, current wording, cited source, source conditions, lab conditions, verdict (supported|conditional|unsupported), replacement wording`.
- [ ] **ST3.1.2:** For the wavelength claims, record explicitly: a literature maximum at 444 nm establishes peak location only; flatness at 440 nm requires a measured spectrum or explicit conditional phrasing; verdict = `unsupported` as written.
- [ ] **ST3.1.3:** For `src/06*:65-67`, record: a near-zero intercept is consistent with, but does not prove, accuracy (blank offset and slope errors can compensate); the replacement states what the intercept does and does not evidence.
- [ ] **ST3.1.4:** For `src/10*:8-20`, tabulate protocol conditions (Fe(III)/SCN⁻ concentrations, acidity, timing, temperature, path length) against DOI 10.1016/j.ica.2016.02.052; verdict = `unsupported` for unique mono-complex dominance unless conditions match; otherwise retain the existing caveat verbatim.
- [ ] **ST3.1.5:** Persist the matrix as rows in `plan/claim-ledger.csv` (schema per T09) with reviewer `CR`; rows that cannot be resolved stay `unresolved` — never silently upgraded.

#### ST3.2: Surgical Text Replacement
- [ ] **ST3.2.1:** Edit only the flagged sentences in the five files; keep all numbers, citations, and course instructions intact; each replacement uses conditional language ("in this course data…", "not verified here") and links to its errata entry.
- [ ] **ST3.2.2:** Re-run all value checks (calibration arithmetic, dilution math) and confirm identical outputs — claim edits must not alter any computed value.

#### ST3.3: Claim-Lint, Errata & Cross-Reference Review
- [ ] **ST3.3.1:** Implement `tools/claim_lint.py` with banned-pattern fixtures: "flat at 440" without a matched-spectrum qualifier, "proves accurate", "R² proves", "intercept proves", and unique/single-complex dominance claims; each fixture is an injected bad sentence that must fail lint.
- [ ] **ST3.3.2:** Add errata entries in `plan/errata.md` (`id, date, file:line, old claim, new wording, reason, source`) and link each entry from the edited chapter section.
- [ ] **ST3.3.3:** Sweep cross-references: every anchor/link pointing into edited sections still resolves after rewording (run the T02 link checker).
- [ ] **ST3.3.4:** Definition of Done: lint fails on all injected fixtures; no unsupported wording remains; errata entries present; CR sign-off recorded in the ledger; values computationally reconciled.

---

### T04: B01 — Verify and Repair Calculator Event/State Boundary Behavior
- **Type:** `Bug Fix` (diagnostic investigation)
- **Priority & Dependencies:** `P1` | Depends on: `T02` (trustworthy harness), `T01` (runtime policy)
- **Target Files:** `src/17*:30-144`, `tools/behaviour.py`, `tools/data.py`, `plan/calculator-input-contract.md` (new)
- **Enriched Vision & Architecture Notes:**
  - Contract-first: accepted separators, clamp bounds, and reset semantics are derived from `tools/data.py` before testing, so "expected" never means "whatever the code currently does".
  - Compliant DOM driver only (no Chrome without current-turn permission); if none is available, record an RO-signed blocker — no bug may be asserted without an approved runtime reproduction.
  - Stale-output rule: invalid input must never leave a plausible previous result visible; errors are announced via an ARIA live status; the static no-JS fallback is preserved untouched.

#### ST4.1: Input Contract & Fixtures (B01.0)
- [ ] **ST4.1.1:** Write `plan/calculator-input-contract.md` specifying for all three instruments (explorer, dilution, quality): accepted decimal separators (both `,` and `.`), thousands separators (space/thin-space normalized; ambiguous `1.234` rejected when a decimal comma is also present), empty input → invalid state with status message, malformed input → invalid, clamp bounds (per instrument, from `tools/data.py`), reset semantics (restores protocol defaults and clears status).
- [ ] **ST4.1.2:** Encode the contract as table-driven fixtures in `tools/behaviour.py`: cases `"1,5"`, `"1.5"`, `"1 500"`, `""`, `"abc"`, `"-1"`, `"1e3"`, `"0"`, lower/upper clamp boundaries, and reset-after-invalid; each case asserts the expected output value or the expected invalid-status string.
- [ ] **ST4.1.3:** Add the stale-output rule as an explicit assertion: after any invalid input, the output region shows the invalid-status message or a cleared state — never the previous valid value.

#### ST4.2: Compliant Reproduction
- [ ] **ST4.2.1:** Run the 31 existing assertions plus the new fixtures via a policy-compliant driver (non-Chrome engine or DOM-level harness); log the exact first failing assertion with input, expected (from `tools/data.py`), and actual.
- [ ] **ST4.2.2:** If no compliant runtime is available this turn, record an RO-signed blocker in `plan/blockers.md` and stop; if all cases pass, close the task with a trace record — no bug may be fabricated.

#### ST4.3: Surgical Patch & Guard
- [ ] **ST4.3.1:** Patch only the failing handler branch in `src/17*` (input parsing/normalization, clamp branch, or output update); keep the diff minimal and re-verify the JS budget via the T02 budget check.
- [ ] **ST4.3.2:** Add regression fixture(s) to `tools/behaviour.py` covering the reproduced failure; confirm keyboard operation and screen-reader status (aria-live) still work; confirm no storage/network calls were introduced.
- [ ] **ST4.3.3:** Definition of Done: valid input updates output; invalid input cannot leave plausible stale output; static fallback unchanged; fixtures green under the compliant runtime — or the task is closed with a trace record.

---

### T05: B02 — Remove Only Proven Dead Code or Orphaned Assets
- **Type:** `Bug Fix` / `Refactor` (diagnostic investigation)
- **Priority & Dependencies:** `P2` | Depends on: `T02` (harness), `T04` (calculator fallbacks understood first)
- **Target Files:** `src/**` (11 inline SVGs, four instruments), `tools/reference-graph.py` (new), `tools/asset-classification.md` (new)
- **Enriched Vision & Architecture Notes:**
  - Reference graph before deletion: IDs, classes, `url(#…)`, `href="#…"`, `<use>`, asset paths, JS/CSS selectors, plus build-time consumers — classification beats guessing.
  - Static no-JS fallbacks are intentionally duplicated and are protected from "duplicate" removal; print and AT consumers count as consumers.
  - Guard fixtures for every retained dependency so future deletions cannot silently break anchors.

#### ST5.1: Reference Graph
- [ ] **ST5.1.1:** Implement `tools/reference-graph.py`: parse all `src/**/*.html` for `id=`, `class=`, `url(#…)`, `href="#…"`, `<use href="#…">`, `src=`/`href=` asset paths, and all selector strings in `src/17*` JS and `src/00*` CSS; emit a JSON node→consumers graph.
- [ ] **ST5.1.2:** Include build-time consumers by scanning `build.py` templates and generation scripts for the same nodes, so build-only assets are not misclassified as dead.

#### ST5.2: Classification
- [ ] **ST5.2.1:** Classify each of the 11 SVGs and 4 instruments (plus any zero-consumer candidates) as `live / build-only / fallback / duplicate / unreachable` in `tools/asset-classification.md` with consumer evidence per row.
- [ ] **ST5.2.2:** Mark all no-JS/print/AT fallbacks as protected; duplicates serving fallback roles are excluded from removal regardless of repeated values.

#### ST5.3: Surgical Removal & Parity
- [ ] **ST5.3.1:** Remove only `unreachable` items; record the removal diff; assert total HTML size decreases and no ID/anchor breaks (T02 link checker).
- [ ] **ST5.3.2:** Add guard fixtures: one test per retained dependency class asserting each anchor target, `url(#…)` reference, and asset path resolves in built output.
- [ ] **ST5.3.3:** Definition of Done: no broken ID/anchor; offline fallback unchanged; all remaining assets resolve; HTML size decreased; build parity confirmed (build output structurally identical apart from removals).

---

## Phase 2: Lean Navigation & Model-Boundary Note

### T06: F09 — CSS-Only Route Selector for Three Study Workflows (Lean Alternative)
- **Type:** `Feature` (interactive version documented as rejected; lean alternative adopted)
- **Priority & Dependencies:** `P2` | Depends on: `T02` (anchor checker), existing chapter anchors
- **Target Files:** `src/00*` (nav markup + CSS)
- **Enriched Vision & Architecture Notes:**
  - Three static ordered link lists at document top — zero JS, zero state, zero storage; print-visible; survives no-JS by construction.
  - Rejection rationale preserved in a source comment: no tab state, no route memory, no chapter hiding, no separate interface.
  - Keyboard and document order are native (plain anchors), so accessibility costs nothing.

#### ST6.1: Route→Anchor Mapping
- [ ] **ST6.1.1:** Define the three routes (bench/protocol path, data/analysis path, questions/review path) and map each to existing chapter anchors only — no new pages; record the mapping in a comment block in `src/00*`.
- [ ] **ST6.1.2:** Validate anchor completeness with the T02 link checker; any missing target blocks the task.

#### ST6.2: Rendering & Styling
- [ ] **ST6.2.1:** Insert `<nav aria-label="Mācību ceļi">` at the top of `src/00*` containing three `<ol>` lists of `<a href="#anchor">` links with visible text labels; no icon-only links.
- [ ] **ST6.2.2:** Add CSS in `src/00*`: compact vertical lists; `display: block` under `@media print` (never hidden in print); wraps without horizontal overflow at 390 px; visible `:focus-visible` outlines; touch targets ≥44 px; no `:target` tricks that hide chapters.

#### ST6.3: Verification
- [ ] **ST6.3.1:** Keyboard test: Tab order follows document order through the nav then content; Enter activates anchors; no focus traps.
- [ ] **ST6.3.2:** Print artifact: nav renders fully; 390 px inspection shows a wrapped, non-clipped list.
- [ ] **ST6.3.3:** Kill-criterion check: diff confirms no chapter hiding, no storage, no runtime route memory; DoD = anchors resolve + print/390 px clean.

---

### T07: F05 — Fe(III)–Thiocyanate Speciation Boundary Note (Conditional)
- **Type:** `Feature` (model-boundary note; conditional adoption)
- **Priority & Dependencies:** `P2` | Depends on: `T03` (speciation claim row), protocol data
- **Target Files:** `src/10*`, `plan/speciation-conditions.md` (new)
- **Enriched Vision & Architecture Notes:**
  - A short static note — explicitly not a speciation calculator — stating where the course's stoichiometric shorthand stops and equilibrium speciation begins.
  - Conditional adoption: the source row is added only if protocol conditions align with DOI 10.1016/j.ica.2016.02.052; otherwise the existing caveat stays and the mismatch analysis is the deliverable.
  - Conditional language throughout ("under the conditions of…"), so the note can never be read as asserting unique complex dominance.

#### ST7.1: Condition Extraction & Matching
- [ ] **ST7.1.1:** Extract exact protocol values (Fe(III) and SCN⁻ concentrations, acidity/H⁺, volumes, timing, temperature, path length) from the protocol/filled PDF into `plan/speciation-conditions.md`.
- [ ] **ST7.1.2:** Tabulate the same fields from the peer-reviewed source; compute per-condition verdicts (match / partial / mismatch); decision rule: publish the note only if acidity and concentration ranges both match or partially match with explicit conditional wording.

#### ST7.2: Note Authoring
- [ ] **ST7.2.1:** If applicable: write the static note in `src/10*` with conditional language plus a one-row source table (source, DOI, conditions, applicability).
- [ ] **ST7.2.2:** If not applicable: retain the current caveat verbatim and record the mismatch analysis in `plan/speciation-conditions.md`; no new student-facing claim is added.

#### ST7.3: Verification
- [ ] **ST7.3.1:** CR sign-off on the published note or the retained caveat; run `tools/claim_lint.py` (T03) over any new text.
- [ ] **ST7.3.2:** Kill-criterion check: the note is not a calculator and asserts no unique complex dominance; print/390 px rendering clean if published.

---

## Phase 3: Source-of-Truth & Schema Stabilization (Entry-Condition Work for Phase 4)

*Note: this phase consolidates the step-1 schema/freeze work embedded in the F03/F04/F06/F07 cards so Phase 4 features consume stable artifacts instead of racing to define their own data formats.*

### T08: Canonical Term Schema & Anchor Registry
- **Type:** `Refactor/Wiring` (data schema; from F06 step 1)
- **Priority & Dependencies:** `P2` | Depends on: `None`
- **Target Files:** `plan/terms.csv`, `tools/terms_lint.py` (new), `build.py` (hook point)
- **Enriched Vision & Architecture Notes:**
  - Single source of truth for terms with stable anchors; generation-time validation prevents duplicate terms and broken anchors before any index exists.
  - Schema deliberately small so the held F06 index (T17) stays cheap to generate and review.

#### ST8.1: Schema Definition
- [ ] **ST8.1.1:** Define `plan/terms.csv` columns: `term_id` (unique slug), `term_lv`, `definition_lv`, `units`, `chapter_anchor` (`#term-<slug>`), `source_ref`, `status` (`draft|verified`); seed with terms already used verbatim in the chapters.
- [ ] **ST8.1.2:** Fix the anchor convention `#term-<slug>` in the CSV header comment; verify uniqueness against all existing site IDs.

#### ST8.2: Validation Tooling
- [ ] **ST8.2.1:** Implement `tools/terms_lint.py`: fail on duplicate `term_id`, duplicate `chapter_anchor`, malformed slug, or anchor absent from built HTML; one negative fixture per rule.
- [ ] **ST8.2.2:** Wire the lint into `run.sh verify` (read-only) so schema drift fails fast.

#### ST8.3: Verification
- [ ] **ST8.3.1:** Definition of Done: CSV parses; lint green with negative fixtures injected; anchors resolve in built output; schema version recorded in the header for T17 consumption.

---

### T09: Claim/Source Ledger Schema
- **Type:** `Refactor/Wiring` (data schema; from F07 step 1)
- **Priority & Dependencies:** `P2` | Depends on: `None` (consumed by T03 and T14)
- **Target Files:** `plan/claim-ledger.csv`, `plan/sources.csv` (new), `tools/ledger_lint.py` (new)
- **Enriched Vision & Architecture Notes:**
  - The ledger is the shared substrate for B05's matrix (T03) and the public atlas (T14); stabilizing it first prevents two divergent claim formats.
  - Status vocabulary forbids color-only semantics; `unresolved` is a first-class status, not a failure state to hide.

#### ST9.1: Schema Definition
- [ ] **ST9.1.1:** Define `plan/claim-ledger.csv` columns: `claim_id`, `claim_text_lv`, `chapter_anchor`, `source_id`, `source_scope`, `applicability` (`matched|partial|unmatched`), `status` (`supported|conditional|unsupported|unresolved`), `reviewer`, `updated`, `next_action`.
- [ ] **ST9.1.2:** Create `plan/sources.csv` (`source_id`, citation, DOI/URL, conditions summary); enforce `source_id` as a resolvable foreign key.

#### ST9.2: Validation Tooling
- [ ] **ST9.2.1:** Implement `tools/ledger_lint.py`: referential integrity (`source_id` resolves), enum validation, non-empty `claim_text_lv`, `unresolved` rows require `next_action`; one negative fixture per rule.
- [ ] **ST9.2.2:** Migrate T03's matrix rows into the ledger as the first real data; confirm round-trip parse.

#### ST9.3: Verification
- [ ] **ST9.3.1:** Definition of Done: lint green; T03 matrix fully represented; the T14 generator can consume the CSV with field selection only — no transformation.

---

### T10: Answer-Key & Canonical Data Freeze
- **Type:** `Refactor/Wiring` (content freeze; from F03/F04 step 1)
- **Priority & Dependencies:** `P2` | Depends on: `T03` (values must be claim-clean before freezing)
- **Target Files:** `plan/canonical-6b.json` (new), `tools/data.py` (authority), `src/14*` (Q1–Q9 prompts)
- **Enriched Vision & Architecture Notes:**
  - Freeze canonical values (440 nm, blank, stock concentration, final volume, unknown IDs) with a content hash so every downstream asset (bench card, fold sheet, worksheet) is provably derived from one authority.
  - Any later data change forces a re-freeze with diff review — preventing silent drift between assets.

#### ST10.1: Canonical Fixture
- [ ] **ST10.1.1:** Extract canonical values from `tools/data.py` and the filled PDF into `plan/canonical-6b.json`: `{wavelength_nm, blank_id, stock_concentration, stock_units, final_volume, final_volume_units, unknown_ids[], sha256}`, recording the protocol page/line for each value.
- [ ] **ST10.1.2:** Map Q1–Q9 prompts to the pillar map and to the canonical fields each answer depends on; store under `q_map` in the same JSON.

#### ST10.2: Answer Keys
- [ ] **ST10.2.1:** Draft answer keys for Q1–Q9 with units and boundary conditions (valid ranges, rounding, significant figures); each key references canonical field paths, not literals.
- [ ] **ST10.2.2:** Reconciliation check: recompute every numeric answer from the canonical fields and assert equality with the key; store the reconciliation log as evidence.

#### ST10.3: Freeze Gate
- [ ] **ST10.3.1:** Add a build-time assertion that assets consuming canonical data (T11, T13, T16) embed the same `sha256`; mismatch fails the build.
- [ ] **ST10.3.2:** Definition of Done: fixture hashed; reconciliation log clean; freeze-gate test (mutate one value → build fails) passes.

---

## Phase 4: Feature Integration & Polish

### T11: F01 — One-Page Lab 6B Bench Reference Card
- **Type:** `Feature`
- **Priority & Dependencies:** `P1` | Depends on: `T10` (canonical freeze), `T03` (claim-clean values), `T01` (print artifact evidence), `prior-T07`
- **Target Files:** `src/11*` (`.bench-card` markup), `src/00*` (class rules)
- **Enriched Vision & Architecture Notes:**
  - Static synthesis of protocol-verified values only; semantic table plus printable checklist; one-page budget enforced by print-artifact inspection.
  - Missing source values are omitted or tagged in text (never color-only); labels are real text; checkbox states print.
  - Zero JS: pure HTML/CSS, inheriting no-JS resilience and costing nothing against the JS budget.

#### ST11.1: Content Extraction & Markup
- [ ] **ST11.1.1:** Extract only protocol-verified values (440 nm, blank, stock concentration, final volume, unknown IDs) from `plan/canonical-6b.json` — no value enters the card without a canonical field reference; missing values are omitted or tagged with a text element (class `bench-missing`, human-readable site-language text), never color-only.
- [ ] **ST11.1.2:** Build `.bench-card` in `src/11*` as a `<table>` with `<caption>` and `<th scope="col|row">`, plus a checklist using native `<input type="checkbox">` with associated `<label>` text; no icon-only labels.
- [ ] **ST11.1.3:** Add chapter links from each card section to the procedure and data chapters; verify every target exists.

#### ST11.2: Styling & Print Rules
- [ ] **ST11.2.1:** Add `.bench-card` rules in `src/00*`: `break-inside: avoid` on rows; `@media print` single-page constraints (font-size floor, margin collapse); checkbox prints as an empty box (verified in the print artifact).
- [ ] **ST11.2.2:** Responsive: at 390 px the table reflows to stacked rows (CSS grid or data-label pattern) without horizontal scroll; at 1440 px it uses full width with a comfortable measure.

#### ST11.3: Verification
- [ ] **ST11.3.1:** Numeric reconciliation: every number on the card compared against `plan/canonical-6b.json` and the protocol; store the comparison table as evidence.
- [ ] **ST11.3.2:** Visual: inspect at 390 px and in print (T01 artifact once display is allowed, else RO-signed blocker); confirm no cutoff, one printable page, all links resolve, keyboard order follows document order.
- [ ] **ST11.3.3:** Kill-criterion check: no unsupported procedural steps added; card fits one printable page; DoD met or the card is trimmed.

---

### T12: F02 — Calibration Residual Diagnosis Gallery
- **Type:** `Feature`
- **Priority & Dependencies:** `P2` | Depends on: `T03` (claim-clean residual wording), `prior-T02`/`prior-T08` (regression source, corrected residuals), `T01` (figure inspection)
- **Target Files:** `src/11*` (`#residual-gallery`), `src/00*` (figure CSS)
- **Enriched Vision & Architecture Notes:**
  - Four hand-authored SVG patterns (curvature, single outlier, changing variance, systematic offset) from explicit synthetic labelled examples — no JS, no interaction, no persistence, no network.
  - Every figure carries a text equivalent (pattern table) so meaning never depends on color or pixels alone; synthetic values are labelled illustrative; no red/green-only encoding.
  - Native `<details>` for answer explanations; links to the real Lab 6B residuals anchor the gallery to course data.

#### ST12.1: Pattern Definition & SVG Authoring
- [ ] **ST12.1.1:** With the data analyst, define the four patterns and their evidence boundaries (what each pattern does and does not imply about the fit); record in a comment block above `#residual-gallery`.
- [ ] **ST12.1.2:** Author four inline SVGs in `src/11*` with explicit synthetic data points; each SVG includes `<title>` and `<desc>`, axis labels with units, and a visible "illustrative synthetic data" caption; encoding uses shape/position/labels plus a colorblind-safe palette, never red/green alone.
- [ ] **ST12.1.3:** Add a textual pattern table adjacent to the figures restating each pattern's signature in words (text equivalent for AT and print).

#### ST12.2: Explanations & Cross-Links
- [ ] **ST12.2.1:** Add `<details><summary>` blocks with per-pattern answer explanations; keyboard-operable natively; full feedback inside the disclosure for screen readers.
- [ ] **ST12.2.2:** Link each pattern to the real Lab 6B residuals section and to the corrected-residuals material (`prior-T08`); confirm anchors resolve.

#### ST12.3: Verification
- [ ] **ST12.3.1:** Distortion review: deliberately distort one SVG axis (e.g., non-uniform scaling), confirm the review catches it, record the review, then revert the distortion.
- [ ] **ST12.3.2:** Inspect all figures at 390/768/1440 px and in print (T01 artifacts or RO blocker); confirm no clipping, legible captions, table equivalent present.
- [ ] **ST12.3.3:** Kill-criterion check: no pattern implies a unique cause; no duplication of `prior-T08` corrections; DoD met.

---

### T13: F03 — Fold-Over Retrieval Sheet for Equations and Distinctions
- **Type:** `Feature`
- **Priority & Dependencies:** `P2` | Depends on: `T10` (answer keys), `T03` (claim-clean formulas), `prior-T11` (incl. T11.3), `T01` (print artifact)
- **Target Files:** `src/14*` (`#fold-sheet`), `src/00*` (print CSS)
- **Enriched Vision & Architecture Notes:**
  - Print-first: screen uses `<details>` disclosures; print exposes answers under prompts (or a dedicated answer section) so the printed sheet is self-contained.
  - Prompts aligned strictly to Q1–Q9 and the pillar map; answer keys carry units and boundary conditions; no storage/network.
  - No hidden-only essential content: anything essential is available to AT and print.

#### ST13.1: Prompt Selection & Answer Keys
- [ ] **ST13.1.1:** Select prompts strictly from the Q1–Q9 set and pillar map in `plan/canonical-6b.json#q_map`; no new questions invented.
- [ ] **ST13.1.2:** Write answer keys with units and boundary conditions referencing canonical fields; reconcile each key numerically (reuse the T10 reconciliation log).

#### ST13.2: Markup, Disclosure & Print Wiring
- [ ] **ST13.2.1:** Build `#fold-sheet` in `src/14*` as a definition-style list where each prompt is a `<details><summary>` and the answer lives inside; summary text alone must be meaningful.
- [ ] **ST13.2.2:** Print CSS in `src/00*`: `@media print` forces disclosure contents visible (e.g., `details:not([open]) > *:not(summary) { display: block }` or a print-only answer section); page-break control keeps each answer with its prompt.
- [ ] **ST13.2.3:** Add cross-links from each prompt to its chapter section; verify anchors.

#### ST13.3: Verification
- [ ] **ST13.3.1:** Keyboard: Tab reaches each summary; Enter/Space toggles; focus visible; no JS required.
- [ ] **ST13.3.2:** Print artifact: answers visible; 390 px screen inspection shows no overflow; page budget respected; screen-reader pass reads prompt then answer.
- [ ] **ST13.3.3:** Kill-criterion check: not a duplicate 16-chapter summary; within page budget; DoD met.

---

### T14: F07 — Claim Provenance Atlas for Student-Facing Evidence Literacy
- **Type:** `Feature`
- **Priority & Dependencies:** `P2` | Depends on: `T09` (ledger schema), `T03` (matrix migrated), `prior-T19` (claim ledger), `T01` (print artifact)
- **Target Files:** `plan/claim-ledger.csv`, `build.py` (generator), `src/15*` (`<table id="claim-atlas">`), `src/00*` (table CSS)
- **Enriched Vision & Architecture Notes:**
  - Generated static table (build-time Python) from the ledger — public subset only; no client state, storage, or network.
  - Scope summaries validated by a subject reviewer; unresolved claims remain visibly unresolved in text, never status color alone.
  - Accessible by construction: caption, `th scope`, and a named responsive region only if the table scrolls horizontally.

#### ST14.1: Generator & Public Subset
- [ ] **ST14.1.1:** Extend `build.py` with a generator that reads `plan/claim-ledger.csv`, selects the public subset (claim text, chapter anchor, source citation, scope summary, status), and emits `<table id="claim-atlas">` near `src/15*`; deterministic row order by `claim_id`.
- [ ] **ST14.1.2:** Emit `<caption>` and `<th scope="col">`; wrap in `role="region"` + `aria-label` only if the table scrolls at narrow widths; render status as a text label, never a color chip.

#### ST14.2: Scope Summaries & Review
- [ ] **ST14.2.1:** Draft one-sentence scope summaries per source; CR validates each against the source; sign-off recorded in the ledger row.
- [ ] **ST14.2.2:** Confirm unresolved claims appear with status `unresolved` plus a next-action note — the atlas must not imply false certainty.

#### ST14.3: Verification
- [ ] **ST14.3.1:** Ledger-to-HTML trace: assert every emitted row maps to exactly one CSV row (count + ID-set equality); store the trace log.
- [ ] **ST14.3.2:** Anchor fixture: every `chapter_anchor` in the public subset resolves in built output; print artifact inspected (T01 or RO blocker); 390 px no overflow.
- [ ] **ST14.3.3:** Kill-criterion check: ledger currency process documented (owner + update cadence); no status-color-only encoding; DoD met.

---

### T15: F10 — High-Risk Misconception Check on Fit Interpretation
- **Type:** `Feature`
- **Priority & Dependencies:** `P2` | Depends on: `T03` (claim-clean regression wording), `prior-T02`/`prior-T11`, `T12` (pattern vocabulary), `T13` (disclosure/print CSS reuse)
- **Target Files:** `src/14*` (Q6/Q9 integration), `src/00*` (reused disclosure CSS)
- **Enriched Vision & Architecture Notes:**
  - One static `<details>` scenario using real Lab 6B diagnostics and an explicitly named fit; plausible incorrect reasoning plus corrective feedback describing the evidence and its insufficiency.
  - No quiz engine, no scoring, no storage; a negative fixture bans "R² proves"-style wording.
  - Reuses the gallery's pattern vocabulary (T12) so students connect residual patterns to fit claims.

#### ST15.1: Scenario & Feedback Authoring
- [ ] **ST15.1.1:** Write one scenario: a student claims the fit is valid solely because R² is high, using real Lab 6B diagnostic numbers from `plan/canonical-6b.json`; name the fit explicitly in the prompt.
- [ ] **ST15.1.2:** Draft the incorrect reasoning (plausible, sympathetic) and corrective feedback explaining what the evidence shows and what it cannot show (R²/intercept/residuals alone do not prove validity; cross-reference T12 patterns).

#### ST15.2: Integration & Wiring
- [ ] **ST15.2.1:** Embed the `<details>` block into the Q6 and Q9 sections in `src/14*` with cross-links to the regression source (`prior-T02`) and the gallery (T12); reuse the T13 disclosure styles — no new CSS.
- [ ] **ST15.2.2:** Keep the full feedback inside the disclosure so screen readers receive prompt + incorrect reasoning + correction; keyboard toggles natively.

#### ST15.3: Verification
- [ ] **ST15.3.1:** Negative fixture: grep-style test asserting "R² proves"/"proves accurate"-style wording is absent from the new block; the test fails on injection.
- [ ] **ST15.3.2:** Print/no-JS pass: disclosure content renders in print (reuse T13 print rules); 390 px no overflow.
- [ ] **ST15.3.3:** Kill-criterion check: does not duplicate an existing item; does not claim residuals alone prove validity; DoD met.

---

## Phase 5: Held Backlog (Deferred — Trigger-Gated)

### T16: F04 — Two-Page Student Calculation Worksheet (HELD)
- **Type:** `Feature` (deferred)
- **Priority & Dependencies:** `P2` | Gate: `T02` + `T03` stable; `T10` freeze complete
- **Target Files:** `src/11*` (`#worksheet-6b`)
- **Enriched Vision & Architecture Notes:**
  - Print-first tables with explicit units and blank handwriting areas; no form submission, local storage, or network.
  - Two-page limit enforced by print artifact; every blank field aligned to a T10 answer-key field.

#### ST16.1: Gate Check & Data Freeze
- [ ] **ST16.1.1:** Confirm the entry gate: T02 verification green and T03 claim-lint green; record gate evidence before any authoring.
- [ ] **ST16.1.2:** Freeze canonical data and model labels from `plan/canonical-6b.json`; any drift re-triggers the gate.

#### ST16.2: Worksheet Authoring
- [ ] **ST16.2.1:** Build `#worksheet-6b` in `src/11*`: print-first tables with unit-labelled columns and bordered blank cells for handwriting; no `<input>`/`<textarea>` (nothing to submit or store).
- [ ] **ST16.2.2:** Enforce the two-page limit via print artifact; align every blank field with an answer-key field from T10.

#### ST16.3: Verification
- [ ] **ST16.3.1:** Print artifact: exactly two pages, no cutoff, hand-writable blank areas; 390 px screen inspection clean.
- [ ] **ST16.3.2:** Kill-criterion check: does not compete with the official protocol and is not a third redundant worksheet; if either holds, close as deferred with a trace record.

---

### T17: F06 — Searchable Term Index Generated from Canonical Term Data (HELD)
- **Type:** `Feature` (deferred)
- **Priority & Dependencies:** `P2` | Gate: `T08` schema green + reliable source data
- **Target Files:** `plan/terms.csv`, `build.py` (generator), generated index page
- **Enriched Vision & Architecture Notes:**
  - Static alphabetized index generated at build time; no client-side search or persistence.
  - Duplicate-term and broken-anchor tests are part of generation, not an afterthought.

#### ST17.1: Gate & Generation
- [ ] **ST17.1.1:** Confirm the gate: T08 lint green and term coverage judged reliable by the content owner; record the decision.
- [ ] **ST17.1.2:** Extend `build.py` to render an alphabetized static index from `plan/terms.csv` (term, definition, units, chapter anchor); deterministic ordering; no JS.

#### ST17.2: Tests
- [ ] **ST17.2.1:** Add tests: duplicate `term_id` fails generation; every `chapter_anchor` resolves; index row count equals verified-term count.
- [ ] **ST17.2.2:** Kill-criterion check: the index adds value beyond existing chapter content and source data is reliable; otherwise close as deferred with a trace record.

---

### T18: F08 — Dilution Ladder Schematic with Unit-Preserving Examples (HELD)
- **Type:** `Feature` (deferred)
- **Priority & Dependencies:** `P2` | Gate: protocol dilution scheme confirmed direct (not serial); `prior-T09`
- **Target Files:** `src/11*` (ladder SVG + table)
- **Enriched Vision & Architecture Notes:**
  - Static SVG plus a table equivalent sourced from protocol values; every row carries stock/aliquot/final-volume units.
  - Accessible description included; each row verified against `tools/data.py` before publication.

#### ST18.1: Gate & Scheme Confirmation
- [ ] **ST18.1.1:** Confirm from the protocol that preparation uses direct dilution; if serial, close as not applicable with a trace record.
- [ ] **ST18.1.2:** Extract the standard preparation scheme rows (stock, aliquot, final volume with units) from the protocol and `tools/data.py`.

#### ST18.2: Schematic & Table
- [ ] **ST18.2.1:** Author the ladder SVG in `src/11*` with `<title>`/`<desc>`, unit-labelled stages, and a companion `<table>` carrying identical values (text equivalent).
- [ ] **ST18.2.2:** Verify each row against the data authority; any mismatch blocks publication.

#### ST18.3: Verification
- [ ] **ST18.3.1:** Inspect at 390/768/1440 px and in print; accessible description present; anchors/links resolve.
- [ ] **ST18.3.2:** Kill-criterion check: no serial-dilution implication; no duplication of `prior-T09`; otherwise close as deferred with a trace record.

---

**Execution order:** Wave 1 (parallel): `T01, T02, T08, T09` → Wave 2: `T03, T04` → Wave 3: `T05, T06, T07, T10` → Wave 4: `T11–T15` → Wave 5: `T16–T18` on gate triggers.

## Final Dependency & Execution Matrix

| Task ID | Type | Target Files | Dependencies | Risk Level |
|---|---|---|---|---|
| T01 | Bug Fix | `tools/shoot.mjs`, `tools/visual-verification.md`, `tools/visual-contract.json` | None | Medium |
| T02 | Bug Fix | `run.sh`, `tools/verify.py`, `README.md`, `tools/negative-fixtures.json` | None | High |
| T03 | Bug Fix | `src/04*`, `src/06*`, `src/08*`, `src/10*`, `src/11*`, `plan/claim-ledger.csv`, `tools/claim_lint.py` | T09, prior-T01 | High |
| T04 | Bug Fix | `src/17*`, `tools/behaviour.py`, `plan/calculator-input-contract.md` | T02, T01 | Medium |
| T05 | Bug Fix / Refactor | `src/**`, `tools/reference-graph.py`, `tools/asset-classification.md` | T02, T04 | Medium |
| T06 | Feature | `src/00*` | T02 | Low |
| T07 | Feature | `src/10*`, `plan/speciation-conditions.md` | T03 | Medium |
| T08 | Refactor / Wiring | `plan/terms.csv`, `tools/terms_lint.py` | None | Low |
| T09 | Refactor / Wiring | `plan/claim-ledger.csv`, `plan/sources.csv`, `tools/ledger_lint.py` | None | Low |
| T10 | Refactor / Wiring | `plan/canonical-6b.json`, `tools/data.py` | T03 | Medium |
| T11 | Feature | `src/11*`, `src/00*` | T10, T03, T01, prior-T07 | Low |
| T12 | Feature | `src/11*`, `src/00*` | T03, prior-T02/T08, T01 | Low |
| T13 | Feature | `src/14*`, `src/00*` | T10, T03, prior-T11, T01 | Low |
| T14 | Feature | `plan/claim-ledger.csv`, `build.py`, `src/15*`, `src/00*` | T09, T03, prior-T19, T01 | Medium |
| T15 | Feature | `src/14*`, `src/00*` | T03, T12, T13, prior-T02/T11 | Low |
| T16 | Feature (HELD) | `src/11*` | Gate: T02+T03 stable, T10 | Low |
| T17 | Feature (HELD) | `plan/terms.csv`, `build.py` | Gate: T08 | Low |
| T18 | Feature (HELD) | `src/11*` | Gate: protocol scheme, prior-T09 | Low |
