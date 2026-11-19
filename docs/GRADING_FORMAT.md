# GRADING_FORMAT.md — the N23 grading-engine and feedback-assembly contract

Owner: **N23**. Status: the frozen interface for **N24** (form assembly manifests),
**N25** (analytics events), **N28** (remediation queue), **N32** (results-view visual test
data) and **N36** (mutation-test baseline). Prepared 2026-11-19 after the inspection of the
N17/N18/N19 engine contracts, the N21 session contract, the N22 input semantics and the N20
bank. Everything here is **PROPOSED training policy** where the 2025 programme sets nothing:
the 100-point scale, the slot-point weights, the partial-credit reading and the classification
priorities are this simulator's declarations, labelled as such, never official examination
rules.

## 0. What N23 consumes (upstream, frozen)

| Source | Contract | What N23 takes |
|---|---|---|
| N21 session | `toTerminalRecord()` — 12 fields: `schema_version, session_id, form_id, state, started_at_ms, elapsed_ms, finished_at_ms, answers, flags, unanswered_slot_ids, remediation_slot_ids, transitions` | the terminal record; payloads stay raw; only terminal states grade |
| N21 policy island | `data/exam_policy.json` → `slots[]` = `{slot_id, topic, points}` × 21, sum 100 | the authoritative slot-point scale |
| N20 bank | `data/bank/FAM-*.json` instances: `rubric[] = {criterion_id, points, grading, engine_binding, depends_on, carry_forward}`, `outcome_ids[]`, `misconception_signatures[]`, `payload`, `payload_class`, `givens`, `type_id` | criteria, points, bindings; no criterion-level verdict rule exists — verdicts come from engines |
| N17 quantity engine | `SimEngines.grade(instance, submission, options)` → `{verdict_class, error_class, awarded_criteria[], machine_checked_points, pending_points, max_points, signature, feedback_key, feedback_text, taxonomy_class, tolerance_source, …}` | numeric/option-select verdicts; the four error classes with signatures `MC-2B-02, MC-3B-01, MC-3A-02, MC-7B-02`, fallback `feedback.fallback_notice` |
| N18 graph engine | `SimGraphScoring.scoreDrawing(record, payload, rubric)` / `scoreReading({kind:'n05_payload', instance}, submission, rubric)` → verdict record with `verdict_class` (adds `not_assessed`), `validity`, `cited_entries`, `assessed_geometry`, `replay` | graph verdicts; tolerances already resolved — never re-derived |
| N19 method engines | `MethodEngine.grade(specFromInstance(instance), submission)` → envelope with `awarded_criteria`, `diagnostics.{per_step,per_pair,signatures,remediation}`, pending semantics | ordering/matching/sequence/self-assessment verdicts; remediation entries `{card_id, step_id, misconception_signature, note_lv, feedback_key, feedback_text}` |
| N22 inputs | `SimInputsRegistry.completion(typeId, contract, instance, payload)` → `{status: complete\|incomplete\|invalid, missing[], errors[{id,field,message_key}]}`; `SimInputsIntegration.q03PendingPath(payload)` | the pre-grade gate and the Q03 manual-pending path; the input-preservation invariant (N22-C01) |
| Terms island | `#sim-terms` — `feedback.*` (12 pre-existing keys + 12 new `feedback.results.*` keys added by N23) | all learner-facing feedback copy; keys must resolve or the build fails |

**No N09 misconception registry exists in this workspace** (recorded dependency gap, README
and `data/method_cards.json` `n09_gap_notice_lv`). N23's classification layer therefore maps
the **frozen engine vocabularies** — the N17 error-taxonomy classes, the N19 `signature_registry`
(14 `MC-*` entries), the N18 error classes, the instance-bound `misconception_signatures[]`
and the N22 slot-state ids — through an N23-authored mapping island. The gap stays visible in
the island's epistemic note; when N09 lands, the mapping is the artifact to re-check.

## 1. Honesty rules (verbatim scope)

- **No curve adjustment, peer-norming or grade inflation** of any kind.
- **No silent forgiveness of parse errors:** a malformed response scores zero with its named
  error and its raw input preserved, never a near-miss credit.
- **No grading of self-assessed text beyond the pending state.** The only text operation is
  N19's blankness test. Manual-rubric criteria (Q03/Q05) and self-assessed criteria stay
  **pending-external**, outside the auto total, labelled.
- **No tolerance logic of its own.** The grading module imports only engine contracts; it
  never re-derives a tolerance, a unit factor or a plausibility bound. Contract test: a
  build-time source scan (see §11).
- **No silent defaults.** An unexpected verdict class fails loudly with the criterion and
  verdict named (`E_GRADING_UNKNOWN_VERDICT`), never a quiet zero.
- **Unblended totals.** Auto-scored points and pending-external points are two separate sums
  in the graded record, in the render stub and in every analytics event. `unblended: true` is
  an asserted field, not a comment.

## 2. The grading-policy island — `data/grading_policy.json` (island id `sim-grading-policy`)

Authored data, validated by gate 19 (`tools/validate_n23_grading.py`). Required structure:

```
schema_version: 1
island_id: "sim-grading-policy"
owner: "N23"
status: "authored"
title_lv, epistemic_note          # PROPOSED training policy; N09-gap visible
rubric_policy:
  verdict_rules:                  # EXPLICIT rule for EVERY verdict class that can occur
    correct:                    {count: "auto criteria at full awarded points"}
    partial:                    {count: "auto criteria mixed awarded/denied; 0 < auto < auto_max"}
    incorrect:                  {count: "auto criteria zero; pending criteria stay pending"}
    pending_self_assessment:    {count: "no auto points; pending-external"}
    auto_passed_pending_review: {count: "auto full; self criteria pending-external"}
    not_assessed:               {count: "zero auto (out-of-span); excluded geometry recorded"}
  unknown_verdict_rule: "fail E_GRADING_UNKNOWN_VERDICT naming criterion and verdict"
  criterion_status_rules: {awarded, denied, pending}      # awarded=points, denied=0, pending=external
  slot_state_rules:              # N23's own pre-verdict states (declared vocabulary)
    graded:        "completion complete -> engine contract call"
    incomplete:   "completion incomplete -> zero, named missing list, no engine call (PROPOSED)"
    invalid:      "completion invalid or engine structural error -> zero, named errors, raw preserved"
    unattempted:  "no answer -> zero, error_class UNATTEMPTED (declared here)"
    manual_pending: "Q03/Q05 grading_binding class pending -> pending-external, no engine call"
  points_rule_verbatim_lv:        # full-or-zero per criterion; fractions ARE the declared
                                  # per-criterion points (e.g. 0.75 in FAM-7A); partial iff
                                  # 0 < machine_checked_points < auto_max
  engine_bindings: ["N17-numeric","N18-symbolic","N19-method","self-assessed","human-review"]
honesty_accounting:
  form_max_points: 100
  unblended: true
  auto_total_rule, pending_external_rule, display_copy_keys: [feedback.results.* keys]
binding_rule:
  slot_points_authoritative: true          # the 100-point scale comes from exam_policy slots
  mismatch_rule: "E_GRADING_BINDING_POINTS naming slot, instance and both sums"
  conflict_ref: "N23-C01"                  # FAM-7C/FAM-7D 9-point rubrics vs 5-point S7-3
analytics_contract: {event_types: [...], no_answer_text_rule}
self_test_fixtures: [SF-N23-FULL, SF-N23-PARTIAL, SF-N23-MALFORMED]   # see §10
conflicts: [N23-C01, N22-C06-resolution]
```

**N23-C01 (new, owner N23, handoff N24).** `FAM-7C` and `FAM-7D` instances carry 9-point
rubrics while the blueprint/policy slot `S7-3` declares 5 points. The scale is the slot's: a
binding whose rubric sum ≠ slot points fails loudly by id. Assembly (N24) must not seat a
9-point family in a 5-point slot; the frozen fixtures bind only matching families.

**N22-C06 resolution (N23 decides, recorded here).** The bank's Q02/Q09/Q10/Q11/Q12
self-assessed criteria have no declared text annex in the N04 numeric/graph payload classes.
N23 **accepts them as pending-external without inventing an input field**: the engines already
mark them `pending`; the graded record carries them in `pending_external_points`, labelled.
Dropping criteria is N24's option at assembly time, not N23's at grading time.

## 3. The classification island — `data/feedback_classification.json` (island id `sim-feedback-classification`)

```
schema_version: 1, island_id: "sim-feedback-classification", owner: "N23", status: "authored"
title_lv, epistemic_note       # N09 absent; this mapping is N23-authored PROPOSED policy over
                                # the frozen engine vocabularies; re-check when N09 lands
mapping: [                       # total over every family that can reach a learner
  {
    match_kind: "signature" | "error_class" | "slot_state",
    match_value: "MC-2B-02" | "UNREADABLE_INPUT" | "E_GRAPH_WRONG_DIRECTION" | "UNATTEMPTED" | …
    misconception_name: {island: "engine_taxonomy"|"method_engine_contract"|"terms",
                          field: "name_lv"|"note_lv"|"key"},
    feedback_key: "<existing #sim-terms key>",
    citations: [ {kind: "conventions_ref|engine_rule|graph_rule|contract_rule", id: "…"} ],
    remediation: {concept_ids: ["P<topic>-<nn>", …], chain_ids: ["EXnn", …]},
    priority: <int>,             # smaller = more specific = first (ties: match_value ascending)
    specificity_note_lv: "…"
  }, …
]
ordering_rule: {rule: "priority-ascending-then-match_value", proposed: true,
                n09_gap_notice_lv: "…"}     # the roadmap's "registry priority field" is
                                            # AUTHORED HERE because N09 does not exist
unmapped_rule: "E_FEEDBACK_UNMAPPED naming slot and signature/error; zero-unmapped at the
                build gate (totality sweep) and at grade time"
remediation_resolution: {
  concept_ids_must_resolve_in: ["data/anchor_registry.json", "data/concept_summaries.json"],
  chain_ids_must_resolve_in: ["data/chains.json"],
  method_card_steps_must_resolve_in: ["data/method_cards.json"],
  null_chain_allowed: true        # N28 B.1.1: families without a worked chain render anchor-only
}
render_contract: { … }           # the DOM stub spec, see §8
```

Coverage requirement (the zero-unmapped rule applied at grading time): every id in the union
of {N17 error-taxonomy classes + fallback, N17 conservation signature `MC-1C-01`, N19
`signature_registry` values, N18 `error_class_vocabulary`, every `misconception_signatures[]`
value across the 112 bank instances, the slot-state vocabulary of §2} has a mapping entry.
The build gate proves totality mechanically; the classification sweep (B.1.2) proves it
behaviourally over the scripted error corpus.

## 4. The graded record (canonical, sorted keys)

Emitted by `SimGrading.gradeTerminalRecord` (core, `feedback: null`) and completed by
`SimGrading.composeGradedRecord(core, feedbackRecord)`. Serialization is the N04 rule:
`json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))` → UTF-8 →
SHA-256. The `digest` field is computed over the record **with its own `digest` field
removed**.

```
{
  schema_version: 1, owner: "N23", record_kind: "graded-record",
  session: { session_id, form_id, state, started_at_ms, finished_at_ms, elapsed_ms,
             flags[], unanswered_slot_ids[], remediation_slot_ids[],
             transition_count, terminal_digest },
  grading: { policy_digest, classification_digest,
             binding: { source: "tools/fixtures/n23_score_matrix.json#<form>" | "form-manifest",
                        binding_digest },
             oracle: { oracle_version, oracle_digest, conventions_digest } },
  slots: [ {
    slot_id, topic, slot_points, instance_id, family_id, type_id,
    state: "graded" | "incomplete" | "invalid" | "unattempted" | "manual_pending",
    verdict_class,                 # engine verdict, or NONE for non-graded states
    error_class,                   # engine error, or UNATTEMPTED | MANUAL_PENDING (§2)
    criteria: [ {
      criterion_id, engine_binding, grading, max_points,
      status: "awarded" | "denied" | "pending",
      awarded_points, pending_points,
      verdict_class, error_class,          # engine's per-criterion view when graded
      errors: [{id, field, message_key}],  # present iff slot state invalid
      missing: [{field, name}],            # present iff slot state incomplete
      signature_ids[], feedback_keys[],
      remediation_entries[]               # N19 diagnostics.remediation passthrough, if any
    } ],
    task: { auto_points, auto_max_points, pending_points, pending_max_points, max_points },
    outcome_ids[], misconception_signatures[],   # instance bindings carried for feedback
    raw_input: <the stored payload, byte-identical; NEVER normalized>
  } ],
  totals: {
    auto_points, auto_max_points,
    pending_external_points, pending_max_points,
    form_max_points: 100, unblended: true,
    slots_total: 21, slots_graded, slots_incomplete, slots_invalid,
    slots_unattempted, slots_manual_pending
  },
  feedback: <FeedbackRecord | null>,
  digest: "<sha256 over canonical record minus digest>"
}
```

Invariants asserted by the engine itself: `sum(slot.task.auto_points) == totals.auto_points`;
`sum(slot.task.pending_points) == totals.pending_external_points`;
`slot.max_points == slot_points` (else `E_GRADING_BINDING_POINTS`);
`totals.form_max_points == 100`; unblended fields never merged.

## 5. The feedback record

`SimFeedback.assemble(coreRecord, context)` → part of the graded record:

```
{
  schema_version: 1, owner: "N23", record_kind: "feedback-record",
  classification_digest,
  items: [ {
    slot_id,
    level: "task" | "criterion",          # task-level items first, then per-criterion
    criterion_id,                          # null at task level
    verdict_class, error_class,
    signature_id,                          # or null
    misconception_name,                    # resolved name/note text, or null
    feedback_key, feedback_text,
    citations: [ {kind, id} ],
    remediation: { concept_ids[], chain_ids[],
                   method_card: {card_id, step_id} | null, note },
    priority
  } ],
  ordering_rule: "priority-ascending-then-match_value",
  unmapped: [],                            # non-empty is a validation failure
  digest
}
```

Assembly order: **task-level items first, then per-criterion**, and inside each group
ascending `priority` (ties by `match_value`). A verdict carrying multiple signatures (the
sign-flipped-and-thousand-fold corner) emits one item per signature, most specific first per
the island's priority. Unmapped signature/error → `E_FEEDBACK_UNMAPPED`; unresolved
remediation id → `E_FEEDBACK_REMEDIATION_UNRESOLVED`.

## 6. Module contracts

**`src/grading.ts` → `src/compiled/grading.js`, global `root.SimGrading`** (strict TypeScript,
the N21/N22 compile discipline):

```
SimGrading.ISLAND_ID = 'sim-grading-policy'
SimGrading.loadPolicy(doc)                  -> {policy, digest}        // throws E_GRADING_POLICY_INVALID
SimGrading.gradeTerminalRecord(terminalRecord, bindings, context) -> core record (feedback: null)
SimGrading.applyRubricPolicy(policy, slotRows) -> {criteria, task}    // the pure aggregation
                                                                      // primitive; also the
                                                                      // smoke-vector facade probe
SimGrading.composeGradedRecord(core, feedbackRecord) -> full record    // digest recomputed
SimGrading.toAnalyticsEvents(fullRecord) -> events[]                    // §7, pure
SimGrading.canonicalText(record), SimGrading.digestOf(record)
SimGrading.errors = [ E_GRADING_POLICY_INVALID, E_GRADING_SCHEMA, E_GRADING_STATE,
  E_GRADING_BINDING_UNKNOWN, E_GRADING_BINDING_POINTS, E_GRADING_UNKNOWN_VERDICT,
  E_GRADING_CONTEXT, E_FEEDBACK_UNMAPPED, E_FEEDBACK_REMEDIATION_UNRESOLVED ]
```

**`src/feedback.ts` → `src/compiled/feedback.js`, global `root.SimFeedback`**:

```
SimFeedback.ISLAND_ID = 'sim-feedback-classification'
SimFeedback.loadClassification(doc)        -> {classification, digest}
SimFeedback.assemble(coreRecord, context)  -> FeedbackRecord
SimFeedback.classificationTable(context)   -> coverage table for the sweep runner
SimFeedback.buildScoreReport(fullRecord, termsMap) -> {html, digest}   // §8 DOM stub
```

**Context (built by the harness, never by the modules themselves):**

```
context = {
  doc,                      // pseudo-DOM carrying the inlined islands
  quantity: SimEngines, method: SimMethodEngine, graph: SimGraphScoring,
  inputsRegistry: SimInputsRegistry, inputsIntegration: SimInputsIntegration,
  figures,                  // SimGraphScoring.state.figures after graph.load(doc)
  terms,                    // resolved key -> text map from #sim-terms
  examPolicy,               // loaded N21 policy (slots authoritative)
  bank: {instancesById}
}
```

`bindings = [{slot_id, type_id, instance_id, instance}]` — authored data today
(`tools/fixtures/n23_score_matrix.json`), N24's form manifests later. The engine never
mutates a terminal record, a payload or an instance; every input is treated as read-only and
the emitted `raw_input` is a deep copy.

**Pre-grade routing (frozen):** `unanswered → unattempted`; `type grading_binding class
"pending" → manual_pending` (Q03/Q05); else `completion()` → `invalid`/`incomplete` stop
before any engine call (zero with named errors/missing, raw preserved); `complete` → the
frozen engine call for the type's `grading_binding.engine` exactly as the N22 parity table
dispatches it (no adapters): Q01/Q02/Q04/Q05(graded-parts)/Q09/Q10/Q13/Q17 and
Q07/Q14/Q18 → `SimEngines.grade`; Q06/Q08/Q15/Q16 → `MethodEngine.grade(specFromInstance)` ;
Q11 → `SimGraphScoring.scoreDrawing`; Q12 → `scoreReading({kind:'n05_payload', instance})`.

## 7. The analytics event contract (N25-shaped, digest-linked)

`toAnalyticsEvents(fullRecord)` is a **pure function** — graded record in, events out, no
wall clock, no storage, no re-scoring:

```
[
  {event: "session-completed", form_id, session_id, auto_score, pending_count,
   elapsed_ms, graded_digest},
  {event: "task-answered", slot_id, topic, family_id, type_id,
   criterion_verdicts: [{criterion_id, status, verdict_class, error_class}],
   graded_digest},                          // NO answer text, ever
  {event: "remediation-state", slot_id, state: "open",
   concept_ids[], chain_ids[], signature_id, graded_digest}
]
```

`remediation-state` events exist for incorrect/malformed slots with mapped remediation — the
open entries of N28's queue. Every event carries `graded_digest`; the chain fixture links
terminal digest → graded digest → event digests.

## 8. The score-report render contract (DOM stub for `#rezultati` / N32)

`buildScoreReport` returns an HTML string (plus its digest) that N32 can restyle but not
re-structure. Structure, with term keys for every visible string:

```
<section class="score-report" data-graded-digest="…">
  <div class="score-totals">
    <p class="score-auto">feedback.results.auto_total {auto}/{auto_max}</p>
    <p class="score-pending">feedback.results.pending_total {pending}/{pending_max}</p>
    <p class="score-unblended-note">feedback.results.unblended</p>
    <p class="score-honesty-note">feedback.results.honesty</p>   <!-- once per report -->
  </div>
  <ul class="score-slots">
    <li class="score-slot" data-slot-id="…" data-state="graded|incomplete|invalid|unattempted|manual_pending">
      <div class="score-slot-row">
        <span class="score-slot-id">S4-2</span>
        <span class="score-slot-points">…/…</span>
        <span class="score-slot-state">
          graded: verdict label (feedback.correct|partial|incorrect|pending_review|self_assess)
          invalid: feedback.results.malformed_zero
          incomplete: feedback.results.incomplete_zero
          unattempted: feedback.results.unattempted
          manual_pending: feedback.pending_review
        </span>
      </div>
      <details class="score-criteria">
        <summary>feedback.results.criterion_disclosure</summary>
        <table class="criteria-table">
          <tr><th>criterion_id</th><th>engine_binding</th><th>status</th><th>awarded/max</th><th>error</th></tr>
          …one row per criterion; errors/missing rendered from the frozen ids…
        </table>
        {state invalid} <p class="score-raw">feedback.results.raw_preserved {raw}</p>
      </details>
      <div class="feedback-cards">
        <h4>feedback.results.task_level</h4>
        <article class="feedback-card" data-level="task|criterion" data-signature="MC-…">
          <p class="feedback-misconception">feedback.results.misconception {name}</p>
          <p class="feedback-text">…feedback_text…</p>
          <p class="feedback-citations">feedback.citation_label: …ids…</p>
          <p class="feedback-remediation">
            feedback.results.remediation
            <a data-concept="P4-02">…</a> | <a data-chain="EX05">…</a> | <a data-card="MC-EX05" data-step="S3">…</a>
          </p>
        </article>
      </div>
    </li>
  </ul>
</section>
```

Honesty rules for the stub: the two totals never merge; pending slots show their pending
label; malformed slots show the named error and the preserved raw input; the
`feedback.results.honesty` note appears once; remediation links carry `data-concept` /
`data-chain` / `data-card`+`data-step` attributes (resolvable ids, §3) so N28/N32 can bind
behaviour without re-parsing text. The recorded render fixture for the mixed-form session is
`evidence/N23_RENDER_FIXTURE.json` (html + digest) — N32's visual test data.

## 9. Determinism and digests

Same terminal record + bindings + context → **byte-identical** canonical graded record,
forever. The engine is clock-free (all timestamps come from the terminal record), order-stable
(slots in form order; criteria in rubric order; signatures ordered by the classification
rule), and emits canonically sorted keys. The determinism harness grades the corpus twice
in-process and once in a **fresh process**, comparing `sha256(canonical)` digests — the
three-way identity is recorded in `evidence/N23_DETERMINISM_RECORD.json`. The batch digest
over the whole scripted corpus (score matrix + classification corpus) is recorded and
appended to the ledger.

## 10. The policy island's self-test fixtures and the smoke vectors

`data/grading_policy.json` carries three self-test fixture rows — `SF-N23-FULL`,
`SF-N23-PARTIAL`, `SF-N23-MALFORMED` — each declaring slot points, criterion rows
(`{criterion_id, points, status}` plus slot-state for the malformed case) and hand-computed
expected totals `{auto, pending_external}`. They are the in-file data the smoke vectors
assert. The three in-file smoke vectors are `SMK-N23-GRADE-FULL`, `SMK-N23-GRADE-PARTIAL`,
`SMK-N23-GRADE-MALFORMED` (appended to `src/smoke-subset.js` with a shared `n23Run` helper):

1. assert the `#sim-grading-policy` island is present, readable JSON, its `verdict_rules`
   cover every frozen verdict class, and the three fixtures exist;
2. apply the **declared** rules to each fixture's rows in pure data arithmetic (sum awarded,
   exclude pending from auto, malformed → zero) and compare with the declared expectations;
3. probe `root.SimGrading`: when present, run `applyRubricPolicy` over the fixture rows and
   compare (`engine: 'facade-exercised'`); when absent — the shipped artifact, whose grading
   runtime ships from `src/` like the N17–N20 engines — degrade honestly
   (`engine: 'ships-from-src-not-inlined'`), exactly the N22 smoke pattern.

## 11. Verification inventory

| Artifact | Owner file | Evidence |
|---|---|---|
| Policy island validation, verdict-rule totality, classification totality, remediation-id resolution, no-tolerance source scan | `tools/validate_n23_grading.py` (build gate 19 `grading`) | `evidence/N23_VALIDATION_RECORD.json` |
| Score matrix (FX-N23-FULL/PARTIAL/ZERO/MIXED) + malformed twins + hand-computed sums | `tools/fixtures/n23_score_matrix.json` | graded by the harness; sums asserted |
| Classification sweep (~20 scripted errors, every signature family, priority ordering fixture) | `tools/n23_classification.py` | `evidence/N23_CLASSIFICATION_TABLE.json` |
| Runtime harness (sessions via the N21 machine, grading, assembly, chain fixture, render stub) | `tools/check_n23_runtime.js` | `evidence/N23_RUNTIME_RECORD.json`, `evidence/N23_CHAIN_RECORD.json`, `evidence/N23_RENDER_FIXTURE.json` |
| Determinism (twice + fresh process) and batch digest | `tools/n23_corpus.py` | `evidence/N23_DETERMINISM_RECORD.json`, `evidence/N23_CORPUS_RECORD.json` |
| Smoke vectors + byte contribution | `src/smoke-subset.js` | smoke pass + budget measurement |

The **contract test** (AC-level): `tools/validate_n23_grading.py` scans `src/grading.ts` and
`src/feedback.ts` for forbidden local knowledge — numeric tolerance literals, unit factors,
atomic/molar masses — and asserts the modules' engine access goes only through the frozen
globals (`SimEngines`, `SimGraphScoring`, `SimMethodEngine`, `SimInputsRegistry`,
`SimInputsIntegration`). Grading modules ship from `src/compiled/` and are **not inlined**
(the N17–N20 pattern); **N31 owns the inline / lazy-load / re-budget decision**, and any
ceiling change follows the visible `RE_BUDGET_HISTORY` mechanism.

## 12. Handoffs

- **N24:** the binding format (`[{slot_id, type_id, instance_id}]` + manifest digest) and the
  `E_GRADING_BINDING_POINTS` rule (never seat a family whose rubric sum ≠ slot points;
  N23-C01 names the FAM-7C/7D case).
- **N25:** the analytics events (§7) — pure, digest-linked, unblended; no re-scoring, no
  answer text.
- **N28:** the feedback items' `remediation` payload (concept ids, chain ids, method card
  step) — every id resolvable by the loader rules; queue entries deduplicate by
  `(family, outcome)` per the N28 roadmap.
- **N32:** the render fixture (§8) as visual test data for `#rezultati`.
- **N36:** the classification table (§11) as the grading engine's mutation-test baseline.

**Not claimed:** no official examination, grade or proctoring; no browser-render,
screen-reader, print or instructor acceptance (N32/N33/N34/N37/N40 own those gates); no
semantic grading of free text; no N09 registry — the classification is N23-authored policy
over the frozen vocabularies, labelled PROPOSED.

## 13. As-built amendments (recorded at integration, 2026-11-19)

The three implementation passes recorded the following deviations from the sketch above.
They are amendments of detail, not of contract; every one is visible in the shipped artifacts:

1. **Name sources gained a fourth value.** 44 bank-bound signatures have no name source
   anywhere frozen (N09 absent), so `misconception_name.island` also accepts `"declared"` —
   the classification island declares their Latvian names itself, and its
   `name_source_vocabulary` documents all four values
   (`engine_taxonomy` / `method_engine_contract` / `terms` / `declared`).
2. **Context additions required by §4's own fields.** `context.oracle`
   (`{oracle_version, oracle_digest, conventions_digest}`) and `context.bindingSource` are
   required by `gradeTerminalRecord` (missing → `E_GRADING_CONTEXT` naming the slot);
   `context.gradingPolicy`, `context.responseTypes` and `context.figures` are optional with
   doc-island fallbacks. The harness supplies `bindingSource =
   tools/fixtures/n23_score_matrix.json#<form>` today; N24's manifests replace it.
3. **Slot states carry JSON `null` verdicts.** A non-graded slot's `verdict_class` is `null`
   (§4 sketched "NONE"); criterion `errors[]`/`missing[]` are always present and empty when
   not applicable. `raw_input` is exempted from structural key sorting to keep byte
   identity with what N22 stored, while the digest still canonically sorts it.
4. **`not_assessed` label.** No dedicated term key exists for it; the island's
   `render_contract.verdict_labels.not_assessed` maps it to `feedback.error.out_of_domain`
   (out-of-span geometry is taught with the same no-extrapolation copy as N14/N15).
5. **Render contract registration.** `buildScoreReport(fullRecord, termsMap)` keeps the
   frozen two-argument signature; the full §8 structure is registered by
   `loadClassification(doc)` with identical defaults available before any load.
6. **Conflicts, final numbering.** `data/grading_policy.json` carries `N23-C01` (slot points
   authoritative; FAM-7C/7D vs S7-3), `N23-C03` (Q11 drawing slots need an optional
   `binding.figure_id`; without it the engine refuses with `E_GRADING_CONTEXT`, never a
   guessed figure — handoff N24), `N22-C05-followed` and the `N22-C06-resolution`
   (self-assessed criteria accepted as pending-external, no invented input field).
   `data/feedback_classification.json` carries `N23-C02` (the N19 registry's link-label
   feedback key), `N23-C04` (the N17 n05→`MC-7B-02` alias rule; renumbered from the first
   draft's colliding `N23-C03`, with the renumber recorded in the island's provenance) and
   `N09-GAP`. A transposed matching pair denies **two** 0.75 criteria (`repeated_right`
   marks both sides) — recorded for N24's authoring budget.
7. **Shipped artefacts.** `src/compiled/grading.js` (73,429 B) and
   `src/compiled/feedback.js` (60,692 B) are committed compiled artefacts covered by the
   `compile_n21_ts.py --check` drift guard; both ship from `src/` and are not inlined.
