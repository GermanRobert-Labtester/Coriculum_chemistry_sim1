# N30 — Bounded Practice Paths, Filters, and Honest Shortage Contract (`PROPOSED`)

**Owner:** N30 (`src/practice.ts` → `src/compiled/practice.js`, `data/practice_policy.json` → `#sim-practice-policy`)  
**Epistemic Status:** `PROPOSED` training policy (`official_counterpart_status: UNDETERMINED`; the 2025 programme sets no bounded practice lengths, ordering rules, filters, or shortage behavior).

---

## 1. Per-Topic Declared Lengths (Grounded in N20)

All 7 topics have 4 families × 4 variants = **16** accepted bank instances per topic (`evidence/N20_VERIFICATION_RECORD.json#frozen_bank`, 112 total). Declared path lengths (`PROPOSED`) scale with programme outcome counts (`data/coverage.json`):

| Topic | Outcomes (`N02`) | Families (`N20`) | Eligible (`N20`) | Declared Path Length (`PROPOSED`) |
|---:|---:|---:|---:|---:|
| 1 | 9 | 4 | 16 | 6 |
| 2 | 10 | 4 | 16 | 7 |
| 3 | 11 | 4 | 16 | 8 |
| 4 | 11 | 4 | 16 | 8 |
| 5 | 10 | 4 | 16 | 7 |
| 6 | 8 | 4 | 16 | 6 |
| 7 | 5 | 4 | 16 | 5 |

Topic 7 (5 outcomes) is strictly shorter (`5`) than Topic 3 (11 outcomes, `8`). Gate 26 (`tools/validate_n30_practice.py`) validates every declared length against live eligible counts; any scratch length exceeding a topic's live eligible count fails loudly naming the topic.

---

## 2. Pure Path Engine (`SimPractice.computePracticePath`)

One pure function serves all entry points (`topic_browse`, `scheduler_queue` via `N27-to-N30-practice-entry`, `revision_panel` via `N27-to-N30-practice-entry`, and `remediation_retry` via `N28-to-N30-remediation-retry`):

1. **Scope filter:** `topic`, `outcome_id`, `family_ids`, `instance_ids`.
2. **Absolute eligibility gate (shared with N24):** `isReviewEligible(inst, allowEphemeral)` requires `review.{accessibility,calculation,content,source} === 'passed'` and `review_workflow.state === 'accepted'`. Unreviewed instances are counted in `pending_review_count` and never drawn.
3. **Response type filter:** validated against the 18-type `#sim-response-types` registry (`Q01`–`Q18`). Unknown types throw `E_PRACTICE_UNKNOWN_TYPE`.
4. **No-repeat & history exclusion:**
   - Deduplicates by `question_id` within a path.
   - Always excludes `session_answered_ids` (items answered in the current session) and `excluded_instance_ids` (e.g., failed N28 retry instances).
   - When `unattempted_only === true`, excludes `attempted_instance_ids` read from `SimStore` (`practice_history.attempted_instance_ids`, `remediation_queue`, `events`); when history is empty, `history_empty = true` and `0` items are excluded.
5. **Deterministic ordering:**
   - When difficulty is declared (`foundational` → `application` → `transfer`), sorts by `(difficulty_rank ASC, family_id ASC, variant_id ASC, question_id ASC)`.
   - When difficulty is absent, falls back deterministically to `(family_id ASC, variant_id ASC, question_id ASC)`.
6. **Bounded slice & canonical digest:** slices `0..target_length` (`declared_length` is a target, never a promise) and emits a canonical SHA-256 `digest`.

---

## 3. Honest Shortage Triad & Skip Semantics

- **Eligibility shortage (`pending_review`):** returns only eligible items (`true_length < target_length`), never pads with unreviewed items, and renders `practice.shortage.pending_review`.
- **Filter shortage (`filter_shortage`):** returns only filter-matching items (e.g., `Q06` in Topic 1 yields `2`), never pads, and renders `practice.shortage.filter`.
- **History exhaustion (`history_exhausted`):** returns `true_length = 0`, `status = 'exhausted'`, and renders dignified exit options naming both N27 Leitner review intervals (`1 / 3 / 7` days) and N20's ephemeral variant path (`SimVariantEngine.instantiateEphemeral`).
- **Skip semantics:** `skipCurrent()` advances without grading, records `status: 'skipped'` (`graded: false`, `verdict_class: null`), produces `0` incorrect verdicts, and never triggers mastery regression or remediation.

---

## 4. Mode Boundary & Grading Integration

- **Mode boundary (N21):** `describeHelpContract` consults `#sim-exam-policy` (`view_discipline`) via `SimExam.createModeRegistry`: `'practice'` enables `hint` (N08), `chain` (N16 worked chains via `#sim-method-cards`), and `term-lookup` (N07/N10); `'exam'` throws `E_MODE_COMPONENT_NOT_ALLOWED`.
- **Grading-to-mastery chain:** `submitAnswer` grades through `SimGrading.gradePracticeRecord` + `SimFeedback.assemble` + `SimGrading.composeGradedRecord` (N23), updates `SimStore` (`progress`, `practice_history`, `events`), feeds `SimMastery` (N26), and updates `SimRemediation` (N28) in one consistent transaction.
