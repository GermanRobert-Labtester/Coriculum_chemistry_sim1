# Response input format: the registry, the payloads, the completion overlays

**Owner:** N22 · **Status:** frozen interface for N23, N24, N30, N33
**Islands:** `#sim-response-types` (`data/response_types.json`), `#sim-terms`
(`data/terms.json`), `#sim-exam-policy` (`data/exam_policy.json`)
**Sources:** `src/inputs/registry.ts`, `src/inputs/components.ts`,
`src/inputs/integration.ts` (strict TypeScript) → `src/compiled/inputs/*.js`
**Tools:** `tools/validate_n22_inputs.py` (build gate 18) · `tools/check_n22_semantics.js`
(the completion model and the label bank) · `tools/check_n22_components.js` (the render
descriptions and the keyboard parity) · `tools/check_n22_runtime.js` (the capture, the parity
table and the session integration) · `tools/n22_corpus.py` (the evidence runner) ·
`tools/compile_n21_ts.py` (compile and drift guard)

This document is the contract the downstream tasks read. It describes the eighteen response
types as the simulator implements them: the registry entry each type carries, the payload the
session stores, when a response counts as complete, which errors a type can surface, how the
component describes itself, and how the integration writes an answer without becoming a second
writer of the session.

**Epistemic note.** The 2025 programme fixes no response component, no field count and no ARIA
name. Every renderer, completion rule, keyboard path and Latvian label in this layer is a
**PROPOSED training policy**, labelled `PROPOSED` in each registry entry. Nothing here is an
official examination requirement, and the accessibility evidence is a mechanical structural
check — the live screen-reader pass is N33's.

---

## 1. The registry island

`data/response_types.json` is inlined as `#sim-response-types`. It is a map, not a list:

| Field | Meaning |
|---|---|
| `island_id`, `schema_version` | `sim-response-types`, `1`; the loader refuses anything else |
| `types` | exactly `Q01` … `Q18`; a missing or extra id fails the gate |
| `types[id].payload_kind` / `payload_variant` | the frozen session vocabulary (§2) |
| `types[id].renderer_key` | one of `src/bank-loader.js` `RENDERER_REGISTRY` keys |
| `types[id].fields[]` | `role`, `control`, `value_type`, `required`, `label_key`, `payload_path` |
| `types[id].completion_rule` | the model name plus its paths (§3) |
| `types[id].error_surfaces[]` | the frozen error ids that type may render (§4) |
| `types[id].feedback_keys{}` | error id → term key for the Latvian message |
| `types[id].keyboard` | path/parity/abort term keys (§6) |
| `types[id].accessible_alternative` | the blueprint's mandated alternative, term-keyed |
| `types[id].grading_binding` | `class` (`auto`/`mixed`/`pending`/`self`), `engine`, `consumes[]`, `adapter` |
| `types[id].policy_label` | always `PROPOSED` |

`SimInputsRegistry` is the typed reader:

| Entry point | Contract |
|---|---|
| `load(islandJson, termsJson?)` | validates the island and refuses a half-broken one with `E_INPUTS_REGISTRY_INVALID` naming the defect |
| `contractFor(typeId)` | the frozen entry; an unknown id throws `E_INPUTS_UNKNOWN_TYPE` naming the id — there is **no** fallback text field, because a silent fallback changes the task's meaning |
| `completion(typeId, contract, instance, payload)` | the pure completion model (§3) |
| `errorSurfaces(typeId)`, `errorMessage(errorId, terms)` | the declared ids and their Latvian text |
| `typeIds()`, `completedTypes()`, `nameKey(typeId)` | the inventory |

The registry never reads the island or the term bank itself: both are handed in, so the same code
runs in the artifact and in the Node harness.

## 2. The per-type payload

Answers are stored **raw and unparsed** by `ExamSession` (see `docs/EXAM_SHELL_FORMAT.md` §1.5).
This table is the frozen vocabulary the integration builds and the parity table audits. `fields`
becomes `values`; everything else keeps its name.

| Type | Kind | Variant | Required structure | Ride-alongs |
|---|---|---|---|---|
| Q01 | `numeric` | — | `values{field_id: raw_string}` | — |
| Q02 | `numeric` | — | `values{field_id: raw_string}` (one entry per declared field **and** per declared substep) | — |
| Q03 | `method` | `Q03_template` | `choice` | `fill_ins{step_id: raw_string}`, `conserved` |
| Q04 | `method` | `Q04_vector` | `vector[]` (one cell per species) | — |
| Q05 | `method` | `Q05_rows` | `rows{step_id: raw_string}` | — |
| Q06 | `matching` | — | `pairs[{left_id, right_id}]` (the N19 shape) | — |
| Q07 | `option_select` | — | `selected[]` | `justification` |
| Q08 | `ordering` | — | `order[item_id]` | `explanation` |
| Q09 | `numeric` | — | `values{}` | — |
| Q10 | `numeric` | — | `values{}` | — |
| Q11 | `graph` | `Q11_record` | `record{…, points[]}` | `draw_payload` (`sim-graph-draw-v1`) |
| Q12 | `graph` | `Q12_read` | `read{x, y, figure_binding}` | — |
| Q13 | `method` | `Q13_vector` | `vector[]` | `located`, `replacement`, `reason` |
| Q14 | `option_select` | — | `selected[]` | `justification` |
| Q15 | `method` | `Q15_text` | `text` | — |
| Q16 | `method` | `Q16_text` | `text` | — |
| Q17 | `method` | `Q17_pairs` | `pair_map{step_id: raw_string}` | `structure{part_id: …}` |
| Q18 | `option_select` | — | `selected[]` | `justification` |

`Q18` also accepts the plot-state shape the graph class declares: a capture that carries
`plot_state` is stored as `{kind: "graph", variant: "Q18_plot_state", plot_state}` (conflict
N21-C01 / N22-C02 — the *type* stays `option_select` per the N04 schema).

**Raw strings are raw.** `" 4,70 "` keeps its leading space and its comma; the builder validates
the *shape* (`raw_string`, `raw_string_map`, `string_list`, `pair_list`, `json_list`) and never
converts a value. A number in a coefficient vector is copied as a number, not stringified — a
coercion there would be exactly the silent adapter the parity audit exists to catch.

`SimInputsIntegration.buildPayload(typeId, contract, instance, capture)` accepts either the
component's **capture** (`fields`, `selected`, `order`, `pairs`, `read`, `vector`, `text`,
`pair_map`, `structure`, `record`, `draw_payload`, `plot_state`, `choice`, `fill_ins`,
`conserved`, `located`, `replacement`, `reason`, `justification`, `explanation`) or an
**already-prepared payload** in this vocabulary (`SimInputsComponents.payloadOf()` returns one).
A prepared payload is accepted only when its `kind` and `variant` match the frozen table; a
mismatch throws `E_INPUTS_CONTRACT_MISMATCH`.

## 3. The completion verdict

`SimInputsRegistry.completion(typeId, contract, instance, payload)` is a pure function of the
payload (plus the instance's declared fields and steps). It returns:

```
{ status: "complete" | "incomplete" | "invalid",
  missing: [{ field_id, name }],      // Latvian, term-resolved: "Nav aizpildīta vērtība: c (mol/L)"
  errors:  [{ id, field, message_key }] }
```

- **complete** — every required field carries a non-blank raw string.
- **incomplete** — the payload is readable but something the task declares is still empty; the
  `missing` list names every one of them, in declaration order.
- **invalid** — the payload contradicts its own contract (unknown variant, unreadable read map,
  wrong structure). An error is an annotation: the raw strings are never rewritten.

The completed types are `Q02, Q04, Q10, Q11, Q12, Q13, Q15`; the registry declares
`completed_type: true` for exactly those, and the gate refuses a set that differs.

`SimInputsIntegration.completionForSlot(answer, typeId, contract, instance)` unwraps the stored
answer and delegates. The integration owns the **call**, never the model; the call shape is
negotiated once and cached (`completionBinding()`), and a registry that returns no verdict in any
declared shape throws `E_INPUTS_COMPLETION_BINDING` rather than guessing.

## 4. The error surfaces

A type may render only the ids its `error_surfaces[]` lists. The four engine classes come from
`data/engine_taxonomy.json`; `BLANK_RESPONSE` and the `E_GRAPH_*` ids come from the N17/N18
contracts. No new id is invented in this layer.

| Id | Raised when | Latvian text |
|---|---|---|
| `UNREADABLE_INPUT` | the number grammar fails before any dimensional check (this is where a mixed `1,2.3` separator lands) | `feedback.error.unreadable` |
| `DIMENSIONAL_INCONSISTENCY` | readable, but the unit algebra does not close | `feedback.error.dimensional` |
| `PHYSICALLY_IMPLAUSIBLE` | units are right, the magnitude breaks the declared bound | `feedback.error.implausible` |
| `OUT_OF_DOMAIN` | readable, dimensionally correct, physically possible — outside the task's declared span | `feedback.error.out_of_domain` |
| `BLANK_RESPONSE` | the required field is empty or whitespace-only | `input.error.blank` |
| `E_GRAPH_PAYLOAD_MALFORMED` | the draw payload or the read map is not the declared shape | graph contract feedback |
| `E_GRAPH_EMPTY_SUBMISSION` | fewer than two drawn points | graph contract feedback |

**N22-C01 — `MIXED_SEPARATORS`.** The roadmap's A.1.3 names a `MIXED_SEPARATORS` message. No such
id exists in the N17 taxonomy or the N18/N19 contracts, and this layer does not invent one: a
mixed-separator input classifies as `UNREADABLE_INPUT` (class 1, signature `MC-2B-02`), and the
interface shows the `feedback.error.unreadable` text on blur **without clearing the field**. The
input-preservation invariant holds for all eighteen types.

**N21-C01 / N22-C02 — the Q18 plot state.** Q18 is `option_select` per the N04 schema; the
`plot_state` variant belongs to the graph class. The registry keeps both visible instead of
silently re-binding the type.

## 5. The render description

`SimInputsComponents.render(typeId, contract, instance, payload, terms, context?)` is a pure
function returning a JSON-serialisable description — no DOM, no island read, no session write.

```
{ api_version, type_id, renderer_key, payload_kind, payload_variant,
  role, labelledby, describedby,
  label_text_lv, name_text_lv, help_text_lv, parity_note_lv, abort_note_lv,
  accessible_alternative,
  fields: [{ field_id, role, control, visible_label, aria_name, required, stores,
             error, state, state_text, value, multiline, min_length, describedby,
             transient, options, checked, rows }],
  surfaces: [...],        // plot canvas, structure palette, ordering strip
  parts: [...],           // the composed container's per-part descriptors
  static, live,           // the regions that never change / the polite live regions
  keyboard_hint, completion, error_count }
```

`label_text_lv`, `name_text_lv`, `aria_name`, `keyboard_hint`, `parity_note_lv` and
`abort_note_lv` are **substituted** term text, ready to render; `labelledby` and `describedby`
name the elements the field points at. `completion` carries the verdict (§3) and `error_count` the
number of annotations currently attached.

Rules the gate and the component harness enforce:

- The description carries **exactly** the registry field set for that type — a missing field
  fails the fixture with the field named, so the registry stays authoritative and not decorative.
- Every `aria_name` equals the term text its `label_key` resolves to. Names are term-keyed; a
  literal Latvian name in the registry or the components is a lint failure (`N22_TERMS_LINT`).
- A name pattern may use a declared `{slot}` (for example `{species}`); an undeclared slot, or a
  name still containing `{…}` after substitution, fails the fixture.
- No name carries a raw unit literal: the unit comes from the quantity, never from a string.

## 6. The keyboard and parity contract

Every spatial type has a keyboard path that produces the **same payload** as the pointer path:

| Type | Keyboard path | Parity rule |
|---|---|---|
| Q11 draw | arrows step the active point (coarse = grid step, Shift = fine), Alt = diagonal, Enter commits | the two devices produce the same ordered point list; the payload carries no device marker |
| Q12 read | text fields for `x`, `y` and a select for the figure binding | the read map is the same whether typed or clicked |
| Q17 structure | palette select-and-place with explicit part destinations | the placements are an ordered map, not a drag trace |
| Q06 pairs | a select per left item (no drag-only interaction) | pair identity, not gesture |
| Q08 ordering | a select per position | the order as arranged |

A mid-interaction abort (Escape, navigate-away) discards the in-progress gesture and never emits
a partial placement. The pointer/keyboard parity fixtures, the abort fixture and the per-type
keyboard maps are recorded by `tools/check_n22_components.js` (N22-B); this slice references that
record rather than duplicating it.

## 7. The composed container

Any type can sit inside a composed instance. `SimInputsComponents.compose(parts, terms)` renders
per-part labels and per-part completion, and `SimInputsIntegration.composedDriver(session, slotId,
parts)` stores the response as **one** answer:

```
{ kind: "method", variant: "composed",
  part_order: [part_id…],
  parts: [{ part_id, type_id, kind, variant, payload }],
  completion: { status: "complete"|"incomplete"|"invalid", incomplete_part_ids: [part_id…] } }
```

A half-complete composed response is therefore one answer with a named missing part, which is what
N23's per-criterion grading needs.

## 8. The session integration

| Function | Contract |
|---|---|
| `buildPayload(typeId, contract, instance, capture)` | the payload builder (§2) |
| `answer(session, slotId, typeId, contract, instance, capture)` | builds, dispatches `answer`, re-reads the stored payload and compares content digests (`E_INPUTS_STORE_MISMATCH` if the machine kept something else) |
| `completionForSlot(answer, typeId, contract, instance)` | delegates to the registry (§3) |
| `completionMapState(mapState, answers, bindings)` | the navigator overlay: `buildMapState()` cells plus `complete`, `completion_status`, `missing`, `errors` |
| `reviewMissingList(reviewState, answers, bindings)` | the review overlay: `{role: "alert", count, unanswered_slot_ids, incomplete[{slot_id, type_id, missing_names_lv}], text_lv}` |
| `composedDriver(...)` | §7 |
| `q03PendingPath(payload)` | `{class: "pending", engine: "manual-rubric-pending", graded: false, verdict: null, points_awarded: 0, points_pending: null, payload_digest}` |
| `assertOnlyWriter(session)` | the structural guard: no public setter, deep-copy accessors, one dispatch per answer |

**The machine is the only writer.** The integration has no setter and never reaches the answer
map; `answer()` and `composedDriver()` are the only two paths that write, and both dispatch. The
N21 `answered` flag keeps its frozen meaning (an answer exists); `complete` is the refinement this
layer adds, so the review table and the map cannot disagree about what "answered" means.

**`SimInputs`** is the aggregate: `{registry, components, buildPayload, answer,
completionForSlot, completionMapState, reviewMissingList, composedDriver, q03PendingPath,
assertOnlyWriter, contentDigest, canonical}`. It is built on first access; if a sibling is missing
it throws `E_INPUTS_INCOMPLETE` naming it, because an input layer without its registry or its
components is incomplete, not empty.

## 9. The smoke vectors

Three vectors are registered at the end of `src/smoke-subset.js` and run in the shipped artifact:

| Id | What it asserts |
|---|---|
| `SMK-N22-NUMERIC-CAPTURE` | the island covers the eighteen types; `" 4,70 "` is stored raw |
| `SMK-N22-CLASSIFICATION-CAPTURE` | the island covers the eighteen types; two option ids plus the justification are stored raw |
| `SMK-N22-ORDERING-CAPTURE` | the island covers the eighteen types; the order is stored as arranged, never re-sorted |

They degrade honestly: without the island they report `{island: "not-yet-inlined"}`, and without
the input modules they report `{inputs: "ships-from-src-not-inlined"}` — the runtime modules ship
from `src/`, so the artifact does not carry them.

## 10. What the downstream tasks may rely on

| Task | What it may rely on |
|---|---|
| **N23** (grading) | the payload vocabulary (§2) and the parity table: each stored payload, handed to its frozen engine, produces the engine's criterion shape with no adapter |
| **N24** (form assembly) | `SimInputsIntegration.vocabulary()` — type id → kind, variant, ride-alongs; `SimInputs.registry.contractFor(typeId)` |
| **N30** (practice) | `completionMapState()` and `reviewMissingList()` — pure functions of state, answers and bindings; the mode registry still forbids help surfaces in exam mode |
| **N33** (accessibility) | the ARIA names, roles, live regions, keyboard maps and the abort rule; the live screen-reader pass is N33's |

## 11. What is explicitly not claimed

- No official examination, grade, proctoring or timing status. The semantics are a proposed
  training policy and each registry entry says so.
- No screen-reader, browser-render or instructor acceptance. The evidence is structural: roles,
  names, key resolution, keyboard maps and payload equality.
- No semantic grading of free text. Q15/Q16 stay pending; Q03 stays manual-rubric pending.
- No keyboard-vs-pointer acceptance in this document: that fixture is N22-B's and is referenced,
  not restated.
- No claim that the four variants are four finished questions.

## 12. The recorded conflicts

| Id | Subject | State |
|---|---|---|
| `N22-C01` | `MIXED_SEPARATORS` as a separate id | documented and accepted: it is `UNREADABLE_INPUT`, the raw input is preserved |
| `N22-C02` | Q18 `option_select` vs the `Q18_plot_state` variant | documented and accepted: the type follows N04, the plot state is a graph-class variant |
| `N22-C03` | Q11/Q12 engine label (`N17-numeric` in N04, `N18-graph` in the graph contract) | documented: `engine_binding` keeps the N04 label, `grading_binding.engine` names the frozen scorer |
| `N22-C04` | Latvian message templates keyed to engine ids | documented: the four N17 classes and `BLANK_RESPONSE` use existing term keys; no new id is invented |
| `N22-C05` | `option_select` has no `SimMethodEngine.specFromInstance` builder | documented: the parity row for Q07/Q14/Q18 names the quantity engine's `option_select` branch — the path the N05 golden corpus uses — and passes `selected` verbatim |
| `N22-C06` | variant naming: `exam_policy.named_variants` short values vs the registry's `Q11_record` | documented: the stored payload carries the registry form; the session accepts either (variant is a raw string) |
