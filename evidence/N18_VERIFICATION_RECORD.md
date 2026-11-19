# N18 — Graph scoring engine with criterion shapes and the inherited no-extrapolation rule

**Status:** closed 2026-11-18 (UTC). **Phase:** IV · **Priority:** P0 · **Risk:** High · **Effort:** L
**Dependencies:** N05, N11, N14 (plus N12, N15, N17 contracts consumed verbatim)

**Epistemic note.** The executions below are **VERIFIED (2026-11-18, this environment)**: the Python
twin, the JavaScript twin, the build gate, the runtime harness and the corpus all ran here and their
results are recorded. This is **not** a browser render, screen-reader, print or instructor-acceptance
claim. The 2025 programme fixes no tolerance, no significant-figure rule, no point count and no
reading types; every threshold, criterion shape and reading family declared here is **PROPOSED training
policy**, except the rules that are inherited verbatim from the frozen N12/N14/N15 contracts. The engine
claims no official examination, grade or proctoring status.

---

## 1. What was built

| Artifact | Role |
|---|---|
| `data/graph_scoring_contract.json` | The frozen `#sim-graph-scoring` island: criterion shapes, validity classes and precedence, capture payload schema, tolerance resolution, verdict record schema, cited-entry rule, the inherited rules verbatim, the S3-N18 stratum and the capture contexts. |
| `tools/graph_scoring_engine.py` | The Python authoring twin: reading scorer, drawing scorer, validity rules, capture, payload validation, verdict replay. |
| `src/graph-scoring-engine.js` | The runtime twin `SimGraphScoring`, same contract, same digests. |
| `src/graph-capture.js` | The drawn-response capture component `SimGraphCapture`: the pointer path, the keyboard map, the declared increments and the device-free payload. |
| `tools/validate_graph_scoring.py` | Build gate 14: contract structure, conventions consumption, the N05 reading vectors, the S3-N18 stratum, the validity corpus, the payload corpus, the parity fixture, the replay proof, the inheritance fixtures, the six keyboard contexts and three scratch negatives. |
| `tools/check_n18_runtime.js` | The runtime harness: the shipped islands plus the two source modules, the capture component fixtures, the parity matrix, the replay proof and the smoke vector. |
| `tools/n18_corpus.py` | The evidence corpus: verdict tables, cross-language comparison, budget accounting and two-run parity. |
| `docs/GRAPH_SCORING_FORMAT.md` | The frozen interface for N20, N22, N23 and N33. |

The engine consumes only `#sim-conventions`, `#sim-figures` and `#sim-graph-scoring`. It declares no
tolerance value, no unit factor and no model coefficient of its own; every tolerance class is resolved
from the conventions island at scoring time.

## 2. The two families

**Reading.** A marked point (or the N05 payload readout) is scored against the figure record's declared
tolerance fields. The criterion is resolved per shape: the N05 payload's declared readout, the
calibration line evaluated at the marked `x`, the concentration read at the declared signal, or the
declared equivalence volume of a titration curve.

**Drawing.** A drawn line or curve segment is scored against the criterion shape: the N14 declared true
parameters (slope, intercept, point deviation) for the kinetics linearisation records, the declared
standards for the calibration records, and the declared decay model for the curve segments. The
no-extrapolation rule is applied at scoring: points beyond the declared span are excluded from the
assessment, the boundary inclusive.

## 3. The verdict tables (verdict for verdict)

### 3.1 The N05 reading entries — 3/3

The frozen S1-N05 corpus is untouched; its graph entries are re-graded by the N18 scorer.

| Vector | Expected | Graded | Tolerance class / mode | Deviation | Tolerance |
|---|---|---|---|---|---|
| `GV-S1-T5-Q12-01` | correct / NONE | correct / NONE | `mass` / absolute | 0 | 0,01 g |
| `GV-S1-T7-Q12-01` | correct / NONE | correct / NONE | `absorbance` / absolute | 0,002 | 0,003 A |
| `GV-S1-T7-Q12-02` | incorrect / OUT_OF_DOMAIN_EXTRAPOLATION | identical | `absorbance` / absolute | — | — |

`GV-S1-T5-Q12-01` also proves the unit path: the submission is `10 mg` against a `g` target, converted
through the conventions' `mg → g` factor before the comparison.

### 3.2 The S3-N18 stratum — 14/14

The N05 growth protocol declares the `S3-N18` stratum for N18 (graph construction criterion shapes
Q11 and interpretation Q12 with pointer/keyboard parity). The stratum lives in the N18 contract island,
following the N17 precedent for `S2-N17`; the S1 corpus is not edited.

| Vector | Family | Expected | Graded | Evidence |
|---|---|---|---|---|
| `GV-S3-T7-Q12-01` | reading | correct | correct / NONE | A = 0,201 at γ = 0,008; deviation 0,00084 ≤ 0,003 A |
| `GV-S3-T7-Q12-02` | reading | incorrect | incorrect / OUT_OF_TOLERANCE | same reading, deviation 0,00384 > 0,003 A |
| `GV-S3-T7-Q12-03` | reading | correct | correct / NONE | **the same submission under the significant-figures rule**: tolerance 0,5·10^(−1−2+1) = 0,005 A |
| `GV-S3-T7-Q12-04` | reading | correct | correct / NONE | c = 0,0146 mg/mL against the declared 0,01459; unit converted mg/mL → g/L |
| `GV-S3-T6-Q12-01` | reading | correct | correct / NONE | V = 20,44 mL against 20,45 mL; deviation 0,01 ≤ 0,05 mL (`burette_volume`) |
| `GV-S3-T6-Q12-02` | reading | incorrect | incorrect / OUT_OF_TOLERANCE | V = 20,60 mL; deviation 0,15 > 0,05 mL; inside the axes and the span |
| `GV-S3-T7-Q12-05` | reading | incorrect | incorrect / OUT_OF_DOMAIN_EXTRAPOLATION | γ = 0,017 is outside the declared [0; 0,016] |
| `GV-S3-T5-Q11-01` | drawing | correct | correct / NONE | slope −0,08, intercept 0, point deviation 0 |
| `GV-S3-T5-Q11-02` | drawing | incorrect | incorrect / OUT_OF_TOLERANCE | **near miss**: `slope_ok = true`, `intercept_ok = false` (0,05 > 0,02) |
| `GV-S3-T5-Q11-03` | drawing | incorrect | incorrect / OUT_OF_TOLERANCE | `intercept_ok = true`, `slope_ok = false` (0,005 > 0,0005) |
| `GV-S3-T7-Q11-01` | drawing | correct | correct / NONE | calibration line deviation ≤ 0,00004 A at the declared standards |
| `GV-S3-T7-Q11-02` | drawing | correct | correct / NONE | **span exclusion**: correct inside [0; 0,016], wildly wrong at 0,018 — the excluded point is recorded, not assessed |
| `GV-S3-T7-Q11-03` | drawing | incorrect | incorrect / OUT_OF_TOLERANCE | **boundary inclusive**: the point exactly on `span.x_max = 0,016` is assessed (deviation 0,01968); every other deviation ≤ 0,00072 A |
| `GV-S3-T5-Q11-04` | drawing | correct | correct / NONE | curve segment against the declared first-order decay model |

### 3.3 Tolerance mode coverage — both classes exercised

| Mode | Vectors | Tolerance source |
|---|---|---|
| `absolute` | all reading vectors except `GV-S3-T7-Q12-03`, and `GV-S3-T7-Q11-01` | `conventions.tolerances.quantity_classes[id].absolute.value` |
| `significant_figures` | `GV-S3-T7-Q12-03`, `GV-S3-T5-Q11-01/02/03` | derived `0,5·10^(e−sf+1)`, identical to N14's field tolerance |

`GV-S3-T7-Q12-02` and `GV-S3-T7-Q12-03` submit the **identical** reading `0,204 A` and grade
differently because the declared mode differs. The tolerance is enforced, not decorative.

**Recorded divergence.** For `FIG-T5-LIN-SECOND` the derived significant-figures slope tolerance is
0,0005 L/(mol·s) while the conventions class `rate_constant_second` carries an absolute alternative of
0,005 L/(mol·s). The engine uses the derived value (identical to N14's `evaluateFitLine`) and cites the
class's absolute alternative in the verdict record, so the difference is visible per item rather than
hidden. The N14 records that use `rate_constant_first` and `rate_constant_zero` agree exactly.

## 4. The validity corpus — 5/5

| Case | Expected | Graded | Note |
|---|---|---|---|
| `VAL-N18-01` | E_GRAPH_WRONG_DIRECTION | identical | the drawn slope is positive where the criterion demands negative; the drawing stays inside the axes |
| `VAL-N18-02` | E_GRAPH_NON_MONOTONIC | identical | the segment rises again where the decay model is monotone decreasing |
| `VAL-N18-03` | E_GRAPH_OUT_OF_AXIS_RANGE | identical | the mark at x = 0,020 mg/mL is outside the axis window [0; 0,018] |
| `VAL-N18-04` | E_GRAPH_EMPTY_SUBMISSION | identical | no points |
| `VAL-N18-05` | E_GRAPH_OUT_OF_AXIS_RANGE | identical | **the precedence corner case** |

`VAL-N18-05` is simultaneously unphysical (y = 0,9 A is outside the y-axis window [0; 0,45]) and out
of domain (x = 0,017 mg/mL is outside the declared span [0; 0,016]). The declared precedence rule
resolves it: the validity class (rank 3) precedes the domain class, so the verdict is
`E_GRAPH_OUT_OF_AXIS_RANGE` and the domain condition is recorded in the trace. No submission lands in
an undefined verdict state.

**Precedence rule (verbatim).** *"Ja iesniegums atbilst vairākām klasēm, izvēlas mazāko kārtas numuru:
1 (neizlasāms iesniegums) pirms 2 (tukšs iesniegums) pirms 3 (ārpus ass diapazona) pirms 4 (nepareizs
novirzes virziens) pirms 5 (dubultā atkāpšana) pirms 6 (monotonitātes pārkāpums); tikai tad, kad neviens
derīguma pārkāpums nav atrasts, tiek lietots domēna klase OUT_OF_DOMAIN_EXPRAPOLATION, un tikai pēc tam
tolerances klase OUT_OF_TOLERANCE. Pirmā atrastā klase aptur turpmāku pārbaudi; katrs gadījums iegūst
tieši vienu klasi."*

## 5. The capture payload validation corpus — 6/6

Every malformed payload fails **by name**, with the failing check recorded:

| Case | Failure | Named check |
|---|---|---|
| `PAY-N18-01` | E_GRAPH_PAYLOAD_MALFORMED | `payload_schema` (missing `schema_id`) |
| `PAY-N18-02` | E_GRAPH_PAYLOAD_MALFORMED | `payload_points` (`points` is not an array) |
| `PAY-N18-03` | E_GRAPH_PAYLOAD_MALFORMED | `payload_points` (a point lacks a coordinate) |
| `PAY-N18-04` | E_GRAPH_PAYLOAD_MALFORMED | `payload_axes` (inverted axis bounds) |
| `PAY-N18-05` | E_GRAPH_PAYLOAD_MALFORMED | `payload_span` (inverted span) |
| `PAY-N18-06` | E_GRAPH_PAYLOAD_MALFORMED | `payload_span` (an edge rule other than `inclusive`) |

## 6. The pointer/keyboard parity matrix — 7/7

The capture payload has **no device field** (`N18-CAPTURE-AGNOSTIC-01`). The pointer path and the
keyboard path are projected onto the same declared grid, so the two payloads are byte-identical.

| Vector | Pointer digest | Keyboard digest | Points | Verdict |
|---|---|---|---|---|
| `GV-S3-T5-Q11-01` | `e6745a70…` | `e6745a70…` | 11 | correct / NONE |
| `GV-S3-T5-Q11-02` | `548b0cd7…` | `548b0cd7…` | 11 | incorrect / OUT_OF_TOLERANCE |
| `GV-S3-T5-Q11-03` | `8ec33cdd…` | `8ec33cdd…` | 11 | incorrect / OUT_OF_TOLERANCE |
| `GV-S3-T7-Q11-01` | `4f5362fd…` | `4f5362fd…` | 9 | correct / NONE |
| `GV-S3-T7-Q11-02` | `66039805…` | `66039805…` | 10 | correct / NONE |
| `GV-S3-T7-Q11-03` | `909afe33…` | `909afe33…` | 9 | incorrect / OUT_OF_TOLERANCE |
| `GV-S3-T5-Q11-04` | `dd3ec10f…` | `dd3ec10f…` | 11 | correct / NONE |

Every pointer verdict equals its keyboard verdict; any divergence would fail by vector id and block
closure.

### 6.1 The capture component — 9/9

`src/graph-capture.js` is the component that records the drawn response. It owns the input handling
only: it never inspects the learner's geometry and never grades it. The increments it uses are read
from `SimGraphScoring.keyboardIncrements`, which derives them from the contract, so a component cannot
invent its own precision.

**The declared increments — 6/6.** The engine derives them; the gate checks the derivation against the
declared examples, so the examples are expectations rather than copies.

| Capture context | coarse x | fine x | coarse y | fine y | Band that bounds the fine step |
|---|---|---|---|---|---|
| `CAP-T5-LIN-PRACTICE` | 2 s | 0,2 s | 0,5 | 0,01 | 0,02 (`log_concentration_ratio`) |
| `CAP-T5-LIN-FIRST` | 3 s | 0,3 s | 0,4 | 0,01 | 0,02 (`log_concentration_ratio`) |
| `CAP-T67-CAL-PRACTICE` | 0,002 mg/mL | 0,0002 mg/mL | 0,1 A | 0,0015 | 0,003 A (`absorbance`) |
| `CAP-T67-CAL-MASTER` | 0,002 mg/mL | 0,0002 mg/mL | 0,1 A | 0,0015 | 0,003 A (`absorbance`) |
| `CAP-T5-DECAY-FIRST` | 3 s | 0,3 s | 0,2 mol/L | 0,0025 | 0,005 mol/L (`concentration_molar`) |
| `CAP-T67-TITR-PRACTICE` | 5 mL | 0,025 mL | 2 pH | 0,2 | 0,05 mL (`burette_volume`, x axis) |

The titration context is the one case where the assessed axis is `x`: the equivalence volume is a
volume, so the band bounds the fine `x` step (0,025 mL) and the `y` axis is not assessed.

**The keyboard increment rule (`N18-CAPTURE-KEY-01`).** *"Tastatūras smalkā solis nedrīkst būt
rupjāks par pusi no vērtējamās lieluma tolerances joslas, lai tastatūras ceļš netiktu strukturāli
sodīts. Smalkā x soļa lielums ir min(māriņa soļa desmitdaļa, x tolerances joslas_half), smalkā y soļa
lielums ir min(y ass soļa desmitdaļa, y tolerances joslas_half)."* The keyboard path can therefore
address every grid point and land inside the tolerance band.

**The path merge rule (`N18-CAPTURE-PATH-01`).** A movement that does not change `x` updates the
current point instead of adding a vertex. Without it, the keyboard's axis-aligned stepping leaves
vertical runs in the path, and the projection reads the path as a function of `x`: a vertical run
carries no `y` value of its own, and a staircase drawn with the coarse step would be read as a line
one cell out of place — a deviation of `slope × grid step` (0,05004 A on the calibration record, more
than sixteen times the 0,003 A band). After the merge the path is a polyline through the placed points, exactly
what a pointer drag produces. This rule was found by the parity fixture, not assumed.

**The three parity fixtures.**

| Fixture | What it does | Pointer | Keyboard | Result |
|---|---|---|---|---|
| `CAP-PARITY-01` | the same line drawn once with the pointer and once walked with the diagonal step | 401 raw points → payload digest `9a8d7bb9…` | 81 raw points → payload digest `9a8d7bb9…` | **byte-identical payloads**; both verdicts identical |
| `CAP-PARITY-02` | the **true** calibration line (slope 25,02), which the keyboard cannot place to the last digit | deviation 0,00000 A | deviation 0,00066 A | **identical verdicts** (`correct / NONE`); the placement error is inside the 0,003 A band |
| `CAP-PARITY-03` | a reading mark placed by pointer and by keyboard | mark digest `1e0bddee…` | mark digest `1e0bddee…` | **identical marks and identical verdicts** (`correct / NONE`, same verdict digest) |

`CAP-PARITY-01` draws a line whose slope is a multiple of `fine_y / fine_x`, so both devices can
express it exactly; the verdict is `OUT_OF_TOLERANCE` for both, because the fixture proves *payload
identity*, not correctness. `CAP-PARITY-02` carries the correctness claim: the line the keyboard
learner can place is not the pointer learner's line byte for byte, but it is graded by the same rules
and lands inside the same tolerance.

**Keyboard trace fidelity (`N18-CAPTURE-TRACE-01`).** The keyboard path can reproduce a pointer path
only to the precision of the declared increments. This limit is recorded rather than hidden: N33's
keyboard program owns the live acceptance.

## 7. The verdict replay proof — 4/4

Each sampled verdict was reconstructed from its own record — the assessed geometry, the criterion
parameters and the citations — and matched the original.

| Vector | Original | Replayed |
|---|---|---|
| `GV-S3-T7-Q12-01` | correct / NONE | correct / NONE |
| `GV-S3-T7-Q12-02` | incorrect / OUT_OF_TOLERANCE | incorrect / OUT_OF_TOLERANCE |
| `GV-S3-T5-Q11-02` | incorrect / OUT_OF_TOLERANCE | incorrect / OUT_OF_TOLERANCE |
| `GV-S3-T7-Q11-02` | correct / NONE | correct / NONE |

The replay block also covers the invalid path: an out-of-domain reading replays as
`OUT_OF_DOMAIN_EXTRAPOLATION` from the stored geometry alone.

## 8. The inherited no-extrapolation rule

The rule text is compared, not assumed:

* `data/calibration_contract.json#/no_extrapolation_rule/verbatim` and
  `data/conventions.json#/spectrophotometry/calibration/no_extrapolation_rule_lv` are asserted to be
  identical by the gate;
* the N18 contract's copy is asserted to be **byte-identical** to that text;
* the N14 edge rule and its edge semantics are asserted to be inherited verbatim;
* the behaviour is asserted by three boundary fixtures:

| Fixture | Assertion | Result |
|---|---|---|
| `GV-S3-T7-Q11-02` | geometry strictly beyond the span is **not assessed** (the excluded point is recorded with its deviation and the verdict is accepted) | PASS |
| `GV-S3-T7-Q11-03` | a point **exactly on** `span.x_max` **is** assessed (deviation 0,01968 A) | PASS |
| `GV-S3-T7-Q12-05` | a reading outside the span is refused, not silently accepted | PASS |

The behaviour implements the text: the learner is never graded on a region the figure itself declares
unassessed, and the boundary point is graded.

## 9. Cross-language parity

Both twins consume the same shipped islands and produce the same canonical projections.

| Table | Rows | Python digest | JavaScript digest | Status |
|---|---|---|---|---|
| N05 reading | 3 | `1fcd559f…` | `1fcd559f…` | PASS |
| S3-N18 stratum | 14 | `5ab6f6b2…` | `5ab6f6b2…` | PASS |
| capture component | 9 | `9956a8fe…` | `9956a8fe…` | PASS |
| validity | 5 | `e965257f…` | `e965257f…` | PASS |
| payload validation | 6 | `faa93922…` | `faa93922…` | PASS |
| parity matrix | 7 | `1978137b…` | `1978137b…` | PASS |
| replay | 4 | `9ce227ab…` | `9ce227ab…` | PASS |
| **full verdict records** | 17 | `50f8390c…` | `50f8390c…` | PASS |

The canonical projection (sorted keys, every number rendered with 12 decimal places) is the declared
comparison rule, so the digests are comparable across languages rather than merely within one.

The capture row compares the keyboard-side capture rows — the six declared increment sets and the
three keyboard payload digests. The Python twin simulates the same walks from the same declared
increments and reaches the same payload digests, so the capture parity is not a JavaScript-only
artefact.

The verdict-record row is the strongest of the eight: the **complete verdict records** — every field, from the
oracle fields through the citations, the validity trace and the assessed geometry — are canonically
projected and compared record for record. All 17 are identical. This required one fix during the work:
the citation order must not depend on the JSON key order (the shipped island stores its keys sorted,
the source figure files do not), so both twins sort the tolerance field names explicitly.

## 10. The scratch negatives — 3/3

| Scratch | Mutation | Fails by | Class / message |
|---|---|---|---|
| `SCR-N18-01` | `log_concentration_ratio.absolute` → `999` | vector id `GV-S3-T5-Q11-01` | E_GRAPH_TOLERANCE_DRIFT |
| `SCR-N18-02` | `absorbance.absolute` → `0,001` | vector id `GV-S1-T7-Q12-01` | OUT_OF_TOLERANCE |
| `SCR-N18-KEY-01` | `CAP-T67-CAL-PRACTICE.y_tolerance_band` → `0,0002` | capture context id `CAP-T67-CAL-PRACTICE` | keyboard increments disagree with the declared example |

The first two fail by vector id: the tolerance is resolved from the conventions island at scoring
time, so changing the conventions changes the grading, and the drift check catches a record that
disagrees with the conventions entry. The third shows that the tolerance band is not decorative: the
fine step is *derived* from it, so shrinking the band changes the derived increment and the gate
notices the disagreement with the declared example.

## 11. Runtime budget

| Measure | Value |
|---|---|
| Runtime JS code in the artifact | 225,197 B of the 225,280 B ceiling (83 B headroom, unchanged by N18) |
| Section 1.3 declared runtime band | 120–220 KiB |
| `#sim-graph-scoring` island | 39,318 B, digest `938264ab…6e379` |
| Engine module, compacted | 55,346 B (61,766 B source) — **24,6 %** of the 220 KiB ceiling |
| Capture component, source | 7,897 B (`src/graph-capture.js`, not inlined) |
| `output/simulator.html` | 991,854 B, digest `64d5e0b1…18a052` (within the declared 700–1400 KiB) |

The runtime-JS ceiling was already 83 bytes from its limit before N18, so **both** new modules ship
from `src/`: the graph scoring engine as `src/graph-scoring-engine.js` and the drawn-response capture
as `src/graph-capture.js`. They are validated by gate 14 and exercised by the runtime harness against
the shipped islands; neither is inlined into the artifact's executable script. The island grew from
34,435 B to 39,318 B because the keyboard declarations and the path rules live in the contract, not in
the artifact's script budget. **N31 owns the resolution**: lazy-loading or re-budgeting before the
55,346 B are inlined.

## 12. The smoke vector

`SMK-N18-GRAPH-SCORING` asserts one calibrated reading and one drawn calibration line, with a fixed
digest `842d5af6…c89ad9`.

**Recorded limitation.** The artifact's own smoke subset (`src/smoke-subset.js`) cannot be extended
within the 83-byte headroom, so — exactly as N17 did — the graph smoke vector is registered in the
runtime harness with its in-file digest assertion rather than inside the artifact. The artifact's
smoke subset is unchanged: all ten existing vectors still pass (10/10 in the N16 harness).

## 13. Regression

* Build: `python3 tools/build.py` — gates 1–14 PASS, `output/simulator.html` 991,854 B,
  `build_id=3837e9d70034ba0f`.
* Runtime harnesses: N11, N12, N13, N14, N15, N16, N17, N18 — all PASS.
* Corpus: `python3 tools/n18_corpus.py` — validation parity true, cross-language PASS on all eight
  tables (six verdict tables plus the capture component and the full verdict records), two-run corpus
  parity true on all of them.
* The frozen S1 golden corpus is byte-unchanged: its digest is the same as before N18
  (`27b0a0d2…eca88`), so N04/N05 evidence is not disturbed.

## 14. Limits of this record

* The engine's verdicts are **training policy**, not official examination results.
* The tolerances, the criterion shapes, the reading families and the assessment grids are N18's
  PROPOSED declarations, auditable per item through the cited entries.
* No browser render, screen-reader run, print render or instructor review was performed here; the
  visual policy (lite-shot with Falkon) was not exercised because N18 adds no rendered surface.
* The accessibility consequence of the parity matrix is a **contract** claim (the two input paths are
  scored identically), not a screen-reader result. N33 and N31 own the live acceptance.
* The keyboard trace fidelity is bounded by the declared increments: a keyboard learner cannot place a
  point more finely than `fine_y`, and the trace of a sloped line is quantised by `fine_y / fine_x`.
  The verdict parity survives that limit because the fine step is finer than the tolerance band, but a
  keyboard program that needs more resolution than the band must ask N18 to change the declared
  increments rather than the learner to accept a worse grade.
* The N09 misconception registry is still absent in this workspace; the N18 signatures reuse the N04
  stub pattern, as N17 did, and that dependency gap is recorded in the artifact rather than filled.
