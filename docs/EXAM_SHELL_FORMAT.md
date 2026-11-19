# Exam shell format: the session contract, the timer and the mode boundary

**Owner:** N21 · **Status:** frozen interface for N22, N23, N24, N25, N28, N30 and N33
**Island:** `#sim-exam-policy` (`data/exam_policy.json`)
**Sources:** `src/session.ts`, `src/exam.ts` (strict TypeScript) → `src/compiled/session.js`,
`src/compiled/exam.js`
**Tools:** `tools/author_exam_policy.py` (authoring twin) · `tools/compile_n21_ts.py`
(compile + drift guard) · `tools/validate_n21_shell.py` (build gate 17) ·
`tools/check_n21_runtime.js` (runtime harness)

This document is the contract the downstream tasks read. It describes the exam session state
machine, the advisory timer, the answer map, the navigation and review surface, the mode registry
and the terminal record. The machine-readable declarations live in `data/exam_policy.json`; this
document explains them and states what a consumer may rely on.

**Epistemic note.** The 2025 programme fixes no point weight, no question count, no pass mark, no
allowed aid and no exact exam question type. The 21 slots, the 100 points, the three forms and the
advisory 180-minute timer are **PROPOSED training policy**. The timer is *advisory* and is labelled
as such in the interface. Nothing here is an official examination, grade, timing rule or proctoring
claim, and no session is persisted by default.

---

## 1. The session state machine

### 1.1 States and events

| States | Meaning |
|---|---|
| `not-started` | the session exists but the learner has not started it; no timer runs |
| `running` | the session is live; answers and flags are mutable |
| `review` | the review-and-submit screen is open; answers are still mutable |
| `submitted` | terminal — the work was submitted |
| `expired` | terminal — the advisory limit was reached |
| `aborted` | terminal — the session was aborted |

| Events | Effect |
|---|---|
| `start` | `not-started → running`; the timer starts and the first slot becomes current |
| `navigate` | moves the current slot; `running ↺ running`, `review ↺ review` |
| `flag` | toggles the flag of a slot (or sets it explicitly) |
| `answer` | stores the answer payload of a slot |
| `request-review` | `running → review` |
| `submit` | `review → submitted`, and only with an explicit confirmation |
| `expire` | `running/review → expired` |
| `abort` | `running/review → aborted` |

The transition table is **exhaustive**: every state × event pair has exactly one row in
`session_contract.transition_table` (6 × 8 = 48 rows). The runtime builds its table from the island
and throws `E_SESSION_CONTRACT_INVALID` if a pair is missing or ambiguous, so the island and the
runtime cannot drift.

### 1.2 The machine is the only writer

The answer map and the flag set live in private fields of `ExamSession`. There is no setter a view
can reach: `getAnswers()` and `getAnswer()` return deep JSON copies, and every change goes through
`dispatch(event, payload)`. The shell therefore cannot mutate the session except by dispatching an
event, and the build gate checks that at the source level.

### 1.3 Stable error ids

Every refusal carries a stable id. The ids are split into two disjoint sets in the island, so an id
that is declared but never raised fails the build gate.

| Id | Raised when |
|---|---|
| `E_SESSION_INVALID_EVENT` | an event that the contract does not name |
| `E_SESSION_INVALID_TRANSITION` | a state/event pair with no row (defensive; the table is exhaustive) |
| `E_SESSION_NOT_STARTED` | any event before `start` |
| `E_SESSION_ALREADY_STARTED` | `start` in `running` or `review` |
| `E_SESSION_REVIEW_REQUIRED` | `submit` before the review screen was requested |
| `E_SESSION_CONFIRMATION_REQUIRED` | `submit` without `confirmed: true` |
| `E_SESSION_LATE_WRITE` | `answer`/`flag` after `submitted` |
| `E_SESSION_EXPIRED_WRITE` | `answer`/`flag` after `expired` |
| `E_SESSION_ABORTED_WRITE` | `answer`/`flag` after `aborted` |
| `E_SESSION_TERMINAL` | any other event in a terminal state |
| `E_SESSION_UNKNOWN_SLOT` | an event that names a slot outside the form |
| `E_SESSION_FORM_INVALID` | the session was constructed without slots |
| `E_SESSION_PAYLOAD_INVALID` | a malformed or unknown payload kind |
| `E_SESSION_SERIALIZE_INVALID` | a serialised session that cannot be restored |
| `E_SESSION_MISSING_POLICY` | the session was constructed without a policy |

The last five are raised by the runtime rather than by the transition table; they are declared in
`session_contract.runtime_error_ids`.

### 1.4 The advisory timer

- The limit comes from the island: `timer.advisory_limit_seconds` = 10 800 s (180 min), which is the
  programme's *maximum*, used as a training limit. The 170 + 10 minute split is **PROPOSED**.
- The clock is **monotonic**: `performance.now()` where available, never `Date.now()`. A wall-clock
  jump cannot corrupt the elapsed time.
- The elapsed time is *derived* from the clock at every read, never counted from the number of
  ticks. A throttled or hidden tab therefore still reports honest elapsed time.
- `timer.threshold_ratio` = 0.9. The threshold is a **status indication only**: it never changes the
  state and never disables a control.
- The expiry transition is driven by the elapsed time reaching the limit. It preserves the answers:
  an expired session still carries everything the learner entered.
- `timer.hidden_tab` = `keeps_counting` — this is the declared policy, and the harness proves it
  with a mock clock.

### 1.5 The answer map

Answers are stored **raw and unparsed**: what the learner typed is what is stored. Normalisation
and grading belong to N23, not to the session. The payload contract is structural only — it checks
that the declared fields are present with the declared type.

| Kind | Required | Type | Note |
|---|---|---|---|
| `numeric` | `values` | `raw_string_map` | the map's own values are the typed strings, e.g. `{"value": " 1 000,50 "}` |
| `option_select` | `selected` | `string_list` | option identifiers; `justification` is an optional raw string |
| `ordering` | `order` | `string_list` | the order as it was arranged |
| `matching` | `pairs` | `pair_list` | the pairs as they were arranged |
| `graph` | `variant` | `raw_string` | `Q11_record` or `Q18_plot_state`; `record` / `plot_state` ride along |
| `method` | `variant` | `raw_string` | `Q13_vector` or `Q17_pairs`; `vector` / `pair_map` ride along |
| `raw_text` | `text` | `raw_string` | the free-text answer until N22's typed components exist |

`getRemediationSlotIds()` returns the unanswered plus the flagged slots. It exists because a
remediation link **cannot** exist inside the exam before the submission by design; N28 consumes the
list after the session.

### 1.6 Serialisation

`serialize()` returns plain JSON: `schema_version`, `island_id`, `session_id`, `form_id`, `state`,
`current_slot_id`, `started_at_ms`, `finished_at_ms`, `elapsed_ms`, `answers`, `flags`, `slot_ids`
and `transitions`. `ExamSession.deserialize(text, {policy, form, clock})` restores it. The harness
proves the round trip: a serialised session deserialises to identical answers, flags and state.
N34's storage layer depends on this and must not need a custom codec.

---

## 2. The shell

### 2.1 The pure render state

Three functions are pure functions of the session snapshot and touch no DOM:

| Function | Returns |
|---|---|
| `SimExam.buildMapState(snapshot)` | the 21 map cells with `answered`, `flagged`, `current`, `points`, `topic`, plus the counts |
| `SimExam.buildReviewState(snapshot)` | the 21 review rows, the unanswered list, the remediation list and the submit flags |
| `SimExam.buildTimerState(snapshot, copy)` | the elapsed/limit/remaining times, the threshold flag and the three labels |

Because they are pure, the same functions serve the screen, the fixtures and the responsive test
data of N32.

### 2.2 Navigation, flags and the keyboard

- Previous/next controls, the 21-cell question map and the flag toggle act on the session only
  through `dispatch`.
- The map cell states are exactly the session states: a cell is answered when the session holds an
  answer for that slot, flagged when the flag set holds it, current when the slot is the current one.
- The keyboard contract: `ArrowRight`/`ArrowDown` move to the next slot, `ArrowLeft`/`ArrowUp` to
  the previous one, `f`/`F` toggles the flag of the current slot. The shell moves the focus *into*
  the slot host on navigation and never intercepts `Tab` — the focus is never trapped.
- The documented shortcut is printed in the slot host from `copy_lv.keyboard_hint`.

### 2.3 The review-and-submit screen

- A summary table of all 21 slots: index, slot id, points, answered, flagged.
- The honesty line (`copy_lv.review_summary`): *this is a training-policy summary, not an official
  result document*.
- The unanswered warning, with `role="alert"`, so a screen reader announces it; it names the number
  of unanswered slots and states that the submission is final. It can be dismissed.
- The submission needs an explicit confirmation. The gate is **structural**: the machine raises
  `E_SESSION_CONFIRMATION_REQUIRED` if `submit` arrives without `confirmed: true`, so a disabled
  button is a convenience, not the guarantee.
- The submission is one-way: after `submitted`, `answer` and `flag` raise `E_SESSION_LATE_WRITE`.

### 2.4 The terminal record

`toTerminalRecord()` is what N23 grades and what N25 logs:

| Field | Content |
|---|---|
| `session_id`, `form_id`, `state` | the identity and the terminal state |
| `started_at_ms`, `finished_at_ms`, `elapsed_ms` | the timing |
| `answers` | the raw stored answers |
| `flags` | the flagged slot ids |
| `unanswered_slot_ids` | the slots without an answer |
| `remediation_slot_ids` | the unanswered plus the flagged slots, sorted and unique |
| `transitions` | the transition log: `seq`, `from`, `event`, `to`, `at_ms` |

The record contains no answer *content* beyond the raw payloads and no personal data.

---

## 3. The mode boundary

### 3.1 The registry

`SimExam.createModeRegistry(viewDiscipline)` is the single source mapping a mode to the components
that mode may render. It is also published as `SimModeRegistry` for the N08 hint drawer, which
already asks the registry for the current mode.

| Mode | Allowed components |
|---|---|
| `exam` | `input`, `timer`, `navigator`, `map`, `review` |
| `practice` | the five above plus `hint`, `chain`, `method-card`, `term-lookup` |

`assertAllowed(component, mode)` throws `E_MODE_COMPONENT_NOT_ALLOWED` — the id the island
declares as `view_discipline.unregistered_component_error` — when the component is not registered
for that mode. The render contract consults the registry before it creates anything, so a component
that a mode does not register is **never created**, not merely hidden. An unregistered component
fails loudly; that is how mode creep is caught.

### 3.2 The two-way proof

- **Exam → no help.** The serialised exam DOM contains no `data-sim-component` of `hint`, `chain`,
  `method-card` or `term-lookup`, no `hint-drawer`, and no N16 chain step text (the statement and
  the reasoning of every step of every chain are searched for).
- **Practice → no exam data.** The practice surface is built from a *practice* context and never
  receives an exam session, so it structurally cannot read the answer map. The serialised practice
  DOM contains none of the exam-session field names (`answer_map`, `session_id`, `elapsed_ms`,
  `flags`, `slot_id`, `form_id`, …), none of the flags and none of the answer content.

Both directions are fixture-verified in `tools/check_n21_runtime.js`.

---

## 4. What the downstream tasks may rely on

| Task | What it may rely on |
|---|---|
| **N22** (typed answer components) | the payload kinds and their structural contracts; the payloads are stored raw, so N22 may normalise at grading time |
| **N23** (grading) | `toTerminalRecord()` — the answers, the flags, the elapsed time, the form id; the machine never grades |
| **N24** (form assembly) | the 21 slot ids and their points of `data/exam_policy.json`; the shell renders the form it is given |
| **N25** (logging) | `evidence/N21_SESSION_TRACE.json` and the transition log; **no persistence without an explicit learner opt-in** |
| **N28** (remediation) | `getRemediationSlotIds()` — the post-exam list |
| **N30** (bounded practice) | the practice surface and the mode registry |
| **N32** (responsive) | `buildMapState()` — the deterministic fixture doubles as the responsive test data |
| **N33** (accessibility) | the keyboard contract, `role="alert"`, `aria-pressed`, `aria-current`, the focus movement; the harness proves the keyboard traversal without a pointer event |
| **N34** (storage, print) | `serialize()` / `deserialize()` — plain JSON, no custom codec |

## 5. What is explicitly not claimed

- No official examination, grade, timing rule or proctoring status. The timer is advisory.
- No browser render, screen-reader, print or instructor acceptance: the accessibility evidence is a
  mechanical structural check. The renderer-level acceptance belongs to N22/N33/N34.
- No keyword matching as semantic grading: N21 stores the payload and never grades it.
- No persistence: the session lives in memory for as long as the page does, and nothing is written
  to `localStorage`.
- No claim that the four variants are four finished questions: they are four parameterisations of
  one family template.

## 6. The recorded conflicts

| Id | Subject | State |
|---|---|---|
| `N21-C01` | the roadmap calls Q18 a "plot state" while the N04 schema binds Q18 to `option_select` | documented and accepted: the graph class carries both the record and the plot-state variants, and the type binding follows the N04 schema |
| `N21-C02` | the runtime JS band (120–220 KiB) is exceeded: 266,616 B (260.4 KiB) measured | re-budgeted on the measured requirement; the ceiling is 264 KiB, the declared band stays visible |
| `N21-C03` | the artifact total band (700–1400 KiB) is exceeded: 1,436,787 B (1,403.1 KiB) measured | re-budgeted on the measured requirement; the ceiling is 1,440 KiB, and the final inline/lazy-load/re-budget decision belongs to N31 |
