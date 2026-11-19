# Graph scoring format (N18 frozen interface)

**Owner:** N18 · **Status:** frozen for N20, N22, N23, N33 · **Island:** `#sim-graph-scoring`
(`data/graph_scoring_contract.json`, canonical digest `938264ab…6e379`)

This document is the human-readable face of the frozen contract. The contract
is authoritative; where this page and the contract differ, the contract wins
and the difference is a defect to report, not a licence to choose.

The engine grades two families of graph work:

| Family | Learner does | Scored against |
|---|---|---|
| `reading` | marks a point on a rendered figure | the figure record's declared tolerance fields |
| `drawing` | draws a line or curve segment on declared axes | the criterion shape (declared true parameters or model) |

---

## 1. The capture payload (`sim-graph-draw-v1`)

The capture component records a drawn line or curve segment as an ordered
point list in figure coordinates.

```json
{
  "schema_id": "sim-graph-draw-v1",
  "kind": "line",
  "points": [{"x": 0.0, "y": 0.0}, {"x": 2.0, "y": -0.16}],
  "axes": {"x": {"min": 0, "max": 20}, "y": {"min": -1.7, "max": 0.1}},
  "span": {"x_min": 0, "x_max": 20, "edge_rule": "inclusive"},
  "grid": {"x_min": 0, "x_max": 20, "step": 2},
  "path_reversals": 0
}
```

| Field | Meaning |
|---|---|
| `schema_id` | always `sim-graph-draw-v1` |
| `kind` | `line` or `segment` — the criterion family the capture belongs to |
| `points` | ordered, ascending `x`, in figure coordinates, quantized to 12 decimal places |
| `axes` | the figure's declared axis window; a mark outside it is not on the figure |
| `span` | the declared assessable range; `edge_rule` is always `inclusive` |
| `grid` | the assessment grid the capture was projected onto |
| `path_reversals` | how many times the raw path reversed direction (geometric, not device) |

**Device agnosticism (`N18-CAPTURE-AGNOSTIC-01`).** The payload has no device
field. The pointer path and the keyboard path produce the same payload
structure, so the scorer cannot tell which device drew the line and cannot
grade them differently. Device provenance, if ever needed, is kept outside the
scored data.

**Grid projection (`N18-CAPTURE-GRID-01`).** Any input path is resampled onto
the declared grid: each grid point the path covers takes the path's `y` by
linear interpolation. Grid points the path does not cover are absent from the
payload. The projection is what makes pointer sampling density irrelevant to
the verdict.

**Pointer sampling (`N18-CAPTURE-POINTER-01`).** The pointer path is sampled so
that the distance between two samples is at least one tenth of the grid step.
Sampling is an input detail only, because the payload is projected onto the
grid.

**Path merge (`N18-CAPTURE-PATH-01`).** A movement that does not change the `x`
coordinate updates the current point instead of adding a vertex. The keyboard's
axis-aligned stepping would otherwise leave vertical runs in the path, and the
projection reads the path as a function of `x`: a vertical run carries no `y`
value of its own. After the merge the path is a polyline through the placed
points — exactly what a pointer drag produces.

**Keyboard increments (`N18-CAPTURE-KEY-01`).** The coarse `x` step equals the
grid step, so the keyboard can address every grid point exactly. The coarse `y`
step equals the `y` axis step. The fine `x` step is
`min(grid step / 10, half the x tolerance band)` and the fine `y` step is
`min(y axis step / 10, half the y tolerance band)`; the band of an axis that is
not assessed is `null`, and the axis step then governs alone. A fine step is
never coarser than half the tolerance band of the assessed axis, or the
keyboard path would be structurally penalized.

The diagonal step (`Alt` + arrow) moves the active point by `(fine_x, fine_y)`
in one action: right goes up, left goes down. It lets a straight line be traced
without a staircase.

Declared examples (all six capture contexts):

| Capture context | coarse x | fine x | coarse y | fine y |
|---|---|---|---|---|
| `CAP-T5-LIN-PRACTICE` | 2 s | 0.2 s | 0.5 | 0.01 |
| `CAP-T5-LIN-FIRST` | 3 s | 0.3 s | 0.4 | 0.01 |
| `CAP-T67-CAL-PRACTICE` | 0.002 mg/mL | 0.0002 mg/mL | 0.1 A | 0.0015 |
| `CAP-T67-CAL-MASTER` | 0.002 mg/mL | 0.0002 mg/mL | 0.1 A | 0.0015 |
| `CAP-T5-DECAY-FIRST` | 3 s | 0.3 s | 0.2 mol/L | 0.0025 |
| `CAP-T67-TITR-PRACTICE` | 5 mL | 0.025 mL | 2 pH | 0.2 |

**Keyboard trace fidelity (`N18-CAPTURE-TRACE-01`).** The keyboard path can
reproduce a pointer path only to the precision of the declared increments. When
`fine_y / fine_x` divides the criterion's slope without a remainder, both
devices produce byte-identical payloads. Otherwise the payloads differ, but the
verdicts do not: the placement error stays inside the tolerance band, because
the fine step is finer than the band.

---

## 2. Validity classes and their precedence

Validity rules run **before** any numeric comparison, so an unphysical
submission returns a reason class instead of a numeric score against an absurd
geometry.

| Rank | Class | Raised when |
|---|---|---|
| 1 | `E_GRAPH_PAYLOAD_MALFORMED` | the payload does not satisfy the schema (by named check) |
| 2 | `E_GRAPH_EMPTY_SUBMISSION` | fewer than two points |
| 3 | `E_GRAPH_OUT_OF_AXIS_RANGE` | a mark lies outside the figure's declared axes |
| 4 | `E_GRAPH_WRONG_DIRECTION` | the drawn direction contradicts the criterion's declared slope sign |
| 5 | `E_GRAPH_DOUBLE_BACK` | the path reverses over itself |
| 6 | `E_GRAPH_NON_MONOTONIC` | the segment is not monotone in the declared direction |

Then, and only then: `NOT_ASSESSED` (nothing to assess), then the domain class
`OUT_OF_DOMAIN_EXTRAPOLATION`, then the tolerance class `OUT_OF_TOLERANCE`.

**Precedence rule (verbatim).** *"Ja iesniegums atbilst vairākām klasēm, izvēlas mazāko kārtas numuru: 1 (neizlasāms iesniegums) pirms 2 (tukšs iesniegums) pirms 3 (ārpus ass diapazona) pirms 4 (nepareizs novirzes virziens) pirms 5 (dubultā atkāpšana) pirms 6 (monotonitātes pārkāpums); tikai tad, kad neviens derīguma pārkāpums nav atrasts, tiek lietots domēna klase OUT_OF_DOMAIN_EXTRAPOLATION, un tikai pēc tam tolerances klase OUT_OF_TOLERANCE. Pirmā atrastā klase aptur turpmāku pārbaudi; katrs gadījums iegūst tieši vienu klasi."*

The validity classes precede the domain class because geometry beyond the span
is *not assessed* rather than *rejected*; an unphysical in-span geometry must
still be reported.

---

## 3. The inherited no-extrapolation rule

`N15-NOEXTRAP-01` is inherited **verbatim** from the calibration contract and
the conventions island:

> *"Neviena taisne, nolasījums vai atzīmēta vērtība netiek renderēta ārpus datu deklarētā diapazona. Nolasījums ārpus standartu apgabala ir jāatspoguļo kā neatļauts, nevis jāpieņem klusējot."*

`N14-SPAN-01` is inherited with its edge semantics: the span boundary is
**inclusive** — a point exactly on `span.x_min` or `span.x_max` is assessed.

For drawings, only points with `span.x_min <= x <= span.x_max` enter the
assessment; points outside are recorded as `excluded_points` in the verdict and
are neither accepted nor rejected. For readings, the `x` coordinate of the
marked point must lie inside the span; a reading outside it is
`OUT_OF_DOMAIN_EXTRAPOLATION`.

---

## 4. Tolerance resolution (`N18-TOLERANCE-01`)

The tolerance **class** is named by the record or by the contract; the
tolerance **value** is resolved from `#sim-conventions` at scoring time and is
never copied into a record.

| Mode | Value |
|---|---|
| `absolute` | `conventions.tolerances.quantity_classes[id].absolute.value` |
| `significant_figures` | `0.5 · 10^(e − sf + 1)`, where `e` is the exponent of the assessed magnitude and `sf` is the tolerance field's declared `sig_figs` |

The significant-figures derivation is identical to N14's
`SimFigures.evaluateFitLine` field tolerance, so the figure layer and the
scoring layer cannot drift apart. If a record's tolerance field declares
`abs_value`, it must equal the conventions-resolved value; a difference is
`E_GRAPH_TOLERANCE_DRIFT`.

---

## 5. The verdict record

Every verdict carries the N05 oracle fields (so a verdict is comparable with
the frozen golden corpus) plus the N18 extension fields.

```json
{
  "verdict_class": "correct",
  "error_class": "NONE",
  "awarded_criteria": [{"criterion_id": "C1_READ", "status": "awarded",
                        "awarded_points": 2.0, "pending_points": 0.0, "max_points": 2.0}],
  "machine_checked_points": 2.0, "self_assessed_points": 0.0,
  "human_reviewed_points": 0.0, "pending_points": 0.0, "max_points": 2.0,
  "oracle_version": "1.0.0", "oracle_digest": "...", "conventions_digest": "...",
  "family": "reading", "criterion_id": "FIG-T67-CAL-PRACTICE",
  "criterion_shape": "calibration_line_signal_absolute",
  "cited_entries": [{"kind": "tolerance_class", "id": "absorbance", "mode": "absolute",
                     "absolute_value": "0.003", "unit": "A"}],
  "criterion": {...}, "assessed_geometry": {...}, "validity": {...},
  "capture": {...}, "replay": {...}
}
```

**Cited entries (`N18-CITED-ENTRY-01`).** Every scoring decision cites the
tolerance class entry, the record's tolerance field and its `conventions_ref`,
the contract rule identifiers and the inherited rule identifiers. A numeric
verdict without a citation is not acceptable.

**Replay.** The `replay` block holds the assessed geometry, the criterion
parameters and the citations, so the verdict can be reconstructed from the
record alone. `SimGraphScoring.replayVerdict(record)` does exactly that; the
N18 corpus reconstructs four sampled verdicts and compares them with the
originals.

---

## 6. Criterion shapes

| Shape | Criterion | Tolerance class | Mode |
|---|---|---|---|
| `n05_payload_readout` | the N05 payload's declared readout | `target_readout.tolerance_class` | `absolute` |
| `calibration_line_signal_absolute` | the calibration line at the marked `x` | `absorbance` | `absolute` |
| `calibration_line_signal_sigfigs` | the same reading, significant-figures rule | `absorbance` | `significant_figures` |
| `calibration_line_concentration` | the concentration read at the declared signal | `tolerance_coupling.tolerance_class` | `absolute` |
| `titration_equivalence_volume` | the declared equivalence volume | `burette_volume` (N12) | `absolute` |
| `kinetics_linearization_line` | the declared true line (slope, intercept, point deviation) | the record's `tolerance_fields` | per field |
| `calibration_line_draw` | the drawn line against the declared standards | `absorbance` | `absolute` |
| `kinetics_decay_segment` | the drawn segment against the declared decay model | `tolerance_coupling.tolerance_class` | `absolute` |

The two `calibration_line_signal_*` shapes are the same reading under two
declared tolerance modes. They exist to prove that the mode changes the
verdict: `GV-S3-T7-Q12-02` and `GV-S3-T7-Q12-03` submit the identical reading
`0,204 A` and grade differently because the mode differs.

---

## 7. What N22 and N33 must provide

**N22 (graph response components).** Render the figure, capture the drawn
response into the `sim-graph-draw-v1` payload, and hand the payload to
`SimGraphScoring.scoreDrawing`. The component must not pre-validate the
learner's geometry: the engine owns the validity classes.

The reference capture component is `src/graph-capture.js`
(`SimGraphCapture.create({engine, context, contextId, element, bounds})`). It
exposes:

| Member | Meaning |
|---|---|
| `pointer.begin/move/end` | the pointer path, in figure coordinates |
| `keyboard.begin/keyDown/cancel` | the keyboard path; `keyDown` takes a key event |
| `mark(point)` | the single marked point of a reading |
| `payload()` | the `sim-graph-draw-v1` payload of the current path |
| `increments` | the declared increments the component is using |

The component reads its increments from `SimGraphScoring.keyboardIncrements`,
which derives them from the contract, so a component cannot invent its own
precision. It never inspects the learner's geometry and never grades it.

**N33 (drawn-response keyboard map).** Implement the declared increments, keep
the payload device-free, and expose the grid so the keyboard can address every
grid point. The keyboard program may assume that a keyboard submission is
scored by exactly the rules and the tolerance that apply to a pointer
submission; the N18 parity matrix proves that claim on the full vector set.

N33 inherits two limits that N18 records rather than hides: the keyboard can
only place a point to the declared fine step, and the trace fidelity of a
keyboard-drawn line is bounded by `fine_y / fine_x`. Where the keyboard's
resolution is the binding constraint, N33's program must offer the learner a
way to place points exactly on the grid (`N18-CAPTURE-PATH-01` keeps the path a
polyline through the placed points, so the placement error stays visible).

**N23 (grading engine pathway).** Read `verdict_class`, `error_class`,
`cited_entries` and `assessed_geometry` from the verdict record. Do not
re-derive tolerances; the engine has already resolved them from
`#sim-conventions`.

**N20 (practice items).** Items inherit the criterion shapes, the tolerance
classes and the declared ranges verbatim. A variant may reparameterize the
numbers inside the N14 declared ranges; it may not retune a tolerance class or
a tolerance mode, and it may not widen the assessable span.
