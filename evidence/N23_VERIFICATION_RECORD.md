# N23 verification record — error classification and the partial-credit grading engine

**Status: VERIFIED (2026-11-19).** The grading engine, the error-classification layer and the
feedback-assembly contract exist with their build gate, runtime harness, corpus runner,
classification sweep, determinism proofs, chain fixture, smoke vectors and budget
measurement. Every command below ran against the final integrated state; the corpus record
is byte-identical across two separate invocations.

## What N23 built

One deterministic grading engine assembles the frozen engine verdicts into honest scores and
teaching feedback:

- **`src/grading.ts` → `src/compiled/grading.js`** (`root.SimGrading`, 73,429 B compiled).
  `gradeTerminalRecord()` grades a terminal session record through the frozen contracts
  only: N22 `completion()` gates every payload first (invalid → zero with named errors and
  the raw input preserved; incomplete → zero with the named missing list; no engine call in
  either case), Q03/Q05 take the manual-rubric pending path (`q03PendingPath`), and complete
  payloads dispatch to the exact zero-adapter engine calls of the N22 parity table
  (`SimEngines.grade`, `MethodEngine.grade(specFromInstance)`, `SimGraphScoring.scoreDrawing`
  / `scoreReading`). `applyRubricPolicy()` is the pure aggregation primitive the smoke
  vectors probe; `toAnalyticsEvents()` emits the N25-shaped digest-linked event set;
  `composeGradedRecord()` attaches the feedback record; `digestOf()` is the N04
  canonicalization (sorted keys, no insignificant whitespace, UTF-8, SHA-256).
- **`src/feedback.ts` → `src/compiled/feedback.js`** (`root.SimFeedback`, 60,692 B compiled).
  `assemble()` maps every verdict signature/error class/slot state through the
  classification island to feedback items (task-level first, then per-criterion, priority
  ascending); `buildScoreReport()` renders the §8 DOM stub that doubles as N32's visual
  test data; unmapped signatures throw `E_FEEDBACK_UNMAPPED`; unresolved remediation ids
  throw `E_FEEDBACK_REMEDIATION_UNRESOLVED`.
- **`data/grading_policy.json`** (island `#sim-grading-policy`, 12,143 B canonical): the
  rubric policy as validated data — explicit rules for every frozen verdict class, the
  loud-unknown rule, slot-state rules, the points rule (fractions are the declared
  per-criterion points; partial iff `0 < machine < auto_max`), honesty accounting, the
  slot-points-authoritative binding rule, three self-test fixtures
  (SF-N23-FULL/PARTIAL/MALFORMED) and the conflict records.
- **`data/feedback_classification.json`** (island `#sim-feedback-classification`, 63,716 B
  canonical): 88 mapping rows — 62 signatures (every `misconception_signatures[]` value
  across the 112 bank instances plus the N17 taxonomy signatures and the conservation
  `MC-1C-01`), 21 error classes (the N18 vocabulary plus the N17 taxonomy ids and the six
  extra n05 classes), 5 slot states — with the N23-authored priority ladder, the alias rule
  and the remediation bindings. **The N09 gap stays visible**: the island's epistemic note
  and provenance record that no misconception registry exists in this workspace; 44
  bank-bound signature names are declared here (`name_source_vocabulary` documents all four
  name sources).
- **Gate 19 `grading`** (`tools/validate_n23_grading.py`): policy schema and verdict-rule
  totality against the frozen enums, self-test fixture consistency, classification totality
  over the frozen vocabulary union, remediation-id resolution against the N07/N16/N19
  registries, term-key existence, fixture binding sums versus slot points (the loud
  N23-C01 guard) and the no-tolerance source scan of `grading.ts`/`feedback.ts`.
- **The frozen interface** is [docs/GRADING_FORMAT.md](../docs/GRADING_FORMAT.md), including
  the as-built amendments of section 13.

## The honesty decisions that shaped it

- **The engines award points; N23 assembles them.** The frozen contracts already emit
  `awarded_criteria[]` with per-criterion points; the grading engine never re-derives a
  verdict, a tolerance or a unit factor (gate-enforced source scan). N23's rubric policy
  maps *verdicts to counting rules* as data, and an unknown verdict class fails loudly with
  the criterion and verdict named.
- **The 100-point scale is the slot's.** `auto_max + pending_max = 100` on every fixture
  form; a binding whose rubric sum differs from the slot points is refused by id
  (`E_GRADING_BINDING_POINTS`, conflict N23-C01 for the FAM-7C/7D vs S7-3 case).
- **Pending stays external.** 151 of the bank's 267 criteria are self-assessed; the full
  form therefore reads **48 auto of 48 auto-max plus 52 pending of 52 pending-max** — the
  100-point scale fully accounted, the two sums never merged (`unblended: true` asserted),
  exactly the honesty the roadmap's "72 of 100 auto-scored with 8 pending" example demands.
  The N22-C06 conflict is decided and recorded: the self-assessed criteria of
  Q02/Q09/Q10/Q11/Q12 are accepted as pending-external without inventing input fields.
- **Malformed is zero with the named error, never near-miss credit.** The mixed-separator
  answer `"1.000,50"` passes completion and is caught by the N17 engine
  (`UNREADABLE_INPUT`, signature `MC-2B-02`); the truncated ordering and the empty Q13
  coefficient are caught by N22 completion as incomplete with the named missing items; a
  stored-payload structural twin is caught as invalid `E_GRAPH_PAYLOAD_MALFORMED`. In every
  case the raw input is preserved byte-for-byte in the graded record.
- **The priority field is authored, honestly.** No frozen island carries a signature
  priority (N09 absent), so the classification island declares the ladder as PROPOSED
  training policy and the multi-signature fixture proves the ordering behaviourally.

## The score matrix (AC1)

| Form | auto / auto_max | pending ext. / max | denied | states |
|---|---|---|---|---|
| FX-N23-FULL | 48 / 48 | 52 / 52 | 0 | 19 graded, 2 manual-pending |
| FX-N23-PARTIAL | 44.5 / 48 | 52 / 52 | 3.5 | two transposed 0.75 criteria + one sig-fig criterion denied |
| FX-N23-ZERO | 0 / 48 | 52 / 52 | 48 | every criterion shows its verdict; self/manual stay pending |
| FX-N23-MIXED | 18 / 48 | 37 / 52 | 14 | 13 graded, 3 incomplete, 1 invalid, 2 unattempted, 2 manual-pending |

Every total equals the hand-computed sums recorded in
[tools/fixtures/n23_score_matrix.json](../tools/fixtures/n23_score_matrix.json) and
re-derived independently by the gate. Graded digests: FULL
`d7ab6baf…`, PARTIAL `f41066c6…`, ZERO `eea329d9…`, MIXED `5a01ab73…`.

## The classification sweep (AC2)

[evidence/N23_CLASSIFICATION_TABLE.json](N23_CLASSIFICATION_TABLE.json): 88/88 required
families mapped, **zero unmapped signatures, zero unresolved remediation links, zero
missing term keys**; 27 scripted wrong answers across representative instances (the
thousand-fold slip, the comma error, the density-required mass-volume error, the
implausible negative, the conservation imbalance, the transposed ordering pairs, the wrong
matching, the sequence distractor, the blank self-assessment, the wrong option selection,
the out-of-domain read, the intercept drop, the five drawing validity classes, the
malformed payload, and the slot states). The multi-signature fixture
(`NUM-THOUSAND-FOLD`) emits priority-ordered items (30 → 60 → 94) and the ordering fixture
(`ORD-CARD-TRANSPOSE-PAIR`) proves task-level-before-criterion and card-step remediation.
The table is N36's mutation-test baseline.

## Determinism, chain and smoke (AC3)

- **Determinism** ([N23_DETERMINISM_RECORD.json](N23_DETERMINISM_RECORD.json)): the MIXED
  form graded twice in-process and once in a fresh Node process yields the byte-identical
  digest `5a01ab73745c19ed157a83a96626a1fc2e0c644388c8ed0b980601d9321d9db0`; the canonical
  text survives a JSON round-trip (key-order stability proof).
- **The chain fixture** ([N23_CHAIN_RECORD.json](N23_CHAIN_RECORD.json)): terminal digest
  `6eb8b0a8…` → graded digest `5a01ab73…` → 25 analytics events (1 session-completed, 19
  task-answered, 5 remediation-state) each carrying the graded digest; a scan of 60 raw
  answer strings finds **zero leaked into any event** (no answer text ever).
- **The batch digest** over the whole corpus: `66756a271c31bbe1293a8fc4ff82289154102b20fd0e6e4d3fa7dc75cf8f25f3`.
- **Smoke**: three in-file vectors (`SMK-N23-GRADE-FULL/PARTIAL/MALFORMED`, +7,387 B in
  `src/smoke-subset.js`) pass over the shipped policy island with the honest degradation
  note `engine: 'ships-from-src-not-inlined'` (the grading runtime itself ships from
  `src/`), and report `engine: 'facade-exercised'` when the module is present.
- **Corpus parity**: `python3 tools/n23_corpus.py` twice as separate invocations produces
  the byte-identical record `6624ba46…` (status PASS).

## Byte accounting and the re-budget

The artifact is 1,611,253 B (1,573.5 KiB); the two new data islands add 12,143 + 63,716
canonical bytes, the twelve `feedback.results.*` term entries grow the terms island, and
the three smoke vectors add 7,387 B of inlined JS. Both interim ceilings were re-set on the
measurement in [tools/byte_budget.py](../tools/byte_budget.py) — runtime JS 264 → 280 KiB
(measured 277,359 B) and artifact total 1,504 → 1,600 KiB (measured 1,611,253 B) — with the
declared bands left visible and N31 named as the final inline/lazy-load/re-budget owner,
exactly the N21/N22 precedent. The grading and feedback modules themselves are **not
inlined** (the N17–N20 pattern); the corpus also records the honest forward projection: a
hypothetical merged build that inlined them would reach ~1,699,804 B, 61,404 B over the
current ceiling — N31's decision, recorded rather than hidden.

## Conflicts recorded

| Id | Subject | State |
|---|---|---|
| N23-C01 | Slot points authoritative; FAM-7C/7D 9-point rubrics vs the 5-point S7-3 | documented-and-accepted, handoff N24 |
| N23-C02 | The N19 registry binds 13 signatures to the link-label key; MC-1C-01 uses the conservation copy | open-reference, handoff N19/N28 |
| N23-C03 | Q11 drawing slots need an optional `binding.figure_id`; without it the engine refuses by name | open-gap, handoff N24 |
| N23-C04 | The N17 n05→`MC-7B-02` map is a class alias for wrong selection/order/pairing; suppressed as a "diagnosis" only in feedback assembly | open-reference (renumbered from a colliding first-draft N23-C03; the renumber is recorded in the island's provenance) |
| N22-C06 | Self-assessed criteria of Q02/Q09/Q10/Q11/Q12 without a declared text annex | decided-by-N23: accepted as pending-external, handoff N24 |
| N22-C05 | Q07/Q14/Q18 registry label vs the quantity-engine dispatch | followed (the frozen N22 parity routing) |
| N09-GAP | No misconception registry exists in this workspace | recorded-dependency-gap; the classification island is the artifact to re-check when N09 lands |

## The verification N23 ran

| What | Command | Result |
|---|---|---|
| Strict-TS compile + drift | `python3 tools/compile_n21_ts.py` ; `… --check` | 7/7 modules match (grading.js, feedback.js committed) |
| Grading gate | `python3 tools/validate_n23_grading.py --report evidence/N23_VALIDATION_RECORD.json` | PASS (policy 12,143 B, 3 fixtures, 4 forms, classification checked, 0 errors) |
| Classification sweep | `python3 tools/n23_classification.py --report evidence/N23_CLASSIFICATION_TABLE.json` | OK: 88 rows, 0 unmapped, 0 unresolved, parity true |
| Runtime harness | `node tools/check_n23_runtime.js --record … --chain … --render … --determinism …` | PASS: 4 forms, chain, render, determinism, batch, smoke |
| Full build | `python3 tools/build.py` | 19/19 gates PASS; artifact rebuilt |
| Corpus ×2 | `python3 tools/n23_corpus.py` | PASS; byte-identical records (`6624ba46…`) |
| Regressions | `node tools/check_n10_runtime.js` … `check_n22_runtime.js` | all exit 0 |
| Preparation integrity | `python3 tools/verify_preparation.py --repo-local` | PASS |
| Paint check | lite-shot (falkon, CDP) on the rebuilt artifact | painted (evidence/N23_PAINT_REZULTATI.png, render check only) |

## Handoffs N23 leaves

- **N24:** the binding format `{slot_id, type_id, instance_id}` (+ optional `figure_id`
  for Q11), the `E_GRADING_BINDING_POINTS` rule, the N23-C01/C03 constraints, and the
  authoring note that a transposed matching pair costs two 0.75 criteria.
- **N25:** `toAnalyticsEvents()` — pure, digest-linked, unblended, no answer text; the
  chain fixture is the input contract proof.
- **N28:** the feedback items' remediation payload (concept ids, chain ids, method-card
  steps) — every id resolvable by the loader rules; null chain allowed for non-example
  families.
- **N32:** [N23_RENDER_FIXTURE.json](N23_RENDER_FIXTURE.json) as the results-view visual
  test data; the live in-artifact renderer is pending N31's inline/lazy-load decision (the
  `#rezultati` placeholder copy says exactly this).
- **N36:** the classification table as the grading engine's mutation-test baseline.

**Not claimed:** no official examination, grade or proctoring status; no browser-render,
screen-reader, print or instructor acceptance (N32/N33/N34/N37/N40 own those gates — the
Falkon capture is a render check); no semantic grading of free text; no N09 registry. The
100-point scale, the partial-credit reading, the slot weights and the classification
priorities are PROPOSED training policy; the 2025 programme sets none of them.
