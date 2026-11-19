# REMEDIATION_FORMAT.md — N28 Missed-Item Remediation & Alternate-Variant Retry Contract

**Owner:** N28 · **Status:** frozen interface for N29, N30, N31, N32, N33, N35, N38, and N40  
**Module:** `src/remediation.ts` → `src/compiled/remediation.js` (`root.SimRemediation`)  
**Island:** `#sim-remediation-policy` (`data/remediation_policy.json`) · **Gate:** `tools/validate_n28_remediation.py` (Gate 24 `remediation`)

> **Epistemic & non-gating note.** The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) defines no remediation queue, retry variant selection rule, or completion confirmation policy (`official_counterpart_status: "UNDETERMINED"`). Every rule here is **`PROPOSED` training policy**. Remediation is **recommend-only** (`recommend_only: true`): no learner is ever forced through remediation, and original graded attempts are never re-graded or modified (`regrade_original_attempt: false`).

---

## 1. Queue Entry Model & `(family_id, outcome_id)` Deduplication

Entries live in `SimStore` (`sim_colloq1_store_v2.remediation_queue`), governed by N25's opt-in persistence and two-step erase rules (in-memory by default; zero answer text persisted).

- **Entry triggers:** `invalid`, `incomplete` (with links), or `graded` with `verdict_class === 'incorrect' | 'partial'` from N23 `GradedRecord` slots with resolvable feedback links.
- **Deduplication key:** `(family_id, outcome_id)` (`dedup_key = "${family_id}::${outcome_id}"`) across **active** (`state === 'open' || state === 'retried'`) entries:
  - A new miss matching an active entry increments `miss_count`, unions `slot_ids`, `outcome_ids`, `signature_ids`, `concept_ids`, `chain_ids`, `graded_digests`, `attempted_instance_ids`, and `attempted_variant_ids`, and sets `state = 'open'`.
  - **No history rewind:** A new miss on a `(family_id, outcome_id)` whose previous entry is `resolved` opens a **new** entry (`id = "${family_id}::${outcome_id}::${seq}"`) instead of resurrecting the resolved entry.
- **States & resolution policy:**
  - `open` (`Atvērts`): gap needs study and/or alternate-variant retry.
  - `retried` (`Atkārtots (gaida apstiprinājumu)`): under default `resolution_policy.mode === "confirm_required"`, a correct retry advances the entry to `retried` and displays verbatim copy:
    > *Viena pareiza atbilde ir pierādījums virzībai, nevis pilnīga apguve — apstipriniet pabeigšanu manuāli vai praktizējiet tālāk.*
  - `resolved` (`Atrisināts`): reached via explicit learner confirmation (`resolveEntry`, `resolved_reason: "learner_confirmed"`) OR via declared policy `mode === "one_correct_resolves"` (`resolved_reason: "auto_one_correct"`).

---

## 2. Deterministic Alternate-Variant Selection & N20 Ephemeral Fallback

`SimRemediation.selectRetryInstance(entry, bankQuestions, options)`:

1. Collects all review-passed (`content/source/calculation/accessibility === 'passed'`, non-ephemeral) bank instances in `entry.family_id` and records all frozen `seed` values.
2. Builds `excludedSet` from `entry.instance_id`, `entry.attempted_instance_ids`, `entry.last_retry_instance_id`, and any `additionalExcludedIds`.
3. Searches `cycle_order` (`['A', 'B', 'C', 'D']`) cyclically starting strictly **after** `lastVariant`. Picks the first eligible bank instance not in `excludedSet`.
4. **Never re-serves failed instance:** When all eligible bank letters in the family have been attempted, delegates to `SimVariantEngine.instantiateEphemeral(family_id, nextLetter, attempt, frozenSeeds)` (`N20`), advancing `attempt` if needed so `question_id` (`-EPH-{attempt}`) is never in `excludedSet`.

---

## 3. Study Handoffs, Nullable Chains & Absolute Link Integrity

- **Write-time & on-read validation:** `validateLinks` checks every `concept_id` against `#sim-coverage` / `ANCHOR_REGISTRY`, every `chain_id` against `#sim-chains`, and any `method_card` against `#sim-method-cards`. Empty `concept_ids` throws `E_REMEDIATION_NO_LINKS`; any dangling anchor/chain/card throws `E_REMEDIATION_DANGLING_LINK` naming the broken ID loudly at both write time and render/read time (`validateQueueLinks`).
- **Nullable chain links:** Families without a worked chain (`chain_ids: []`, e.g. `FAM-1A`, `FAM-2D`) render anchor-only (`data-has-chain="false"`) with zero broken chain affordances; calling `openStudyChain` directly throws `E_REMEDIATION_CHAIN_UNAVAILABLE`.
- **Loop return context (`N28-study-handoff`):** `openStudyAnchor` opens `SimConceptDrawer` at `concept_id` with `returnContext` pointing back to `#atskats-remediation-list`; `openStudyChain` mounts `SimChains.mountChain` in `#atskats-remediation-chain-host` (initial collapsed state `data-revealed-count="0"`) with `#atskats-remediation-chain-return` (`Atgriezties atkārtošanas rindā`) restoring queue focus.

---

## 4. Handoffs to N29, N30, and N35

- **To N29 (`getQueueSnapshot`):** `SimRemediation.getQueueSnapshot(store, options)` re-validates all queue links on read and returns `{ schema_version: 1, contract: 'N28-queue-state-snapshot', policy_id, epistemic_label: 'PROPOSED', recommend_only: true, active_count, open_count, retried_count, resolved_count, active_entries, resolved_entries, by_outcome, digest }` for the `#atskats` unified revision view.
- **To N30 (`N28-to-N30-remediation-retry`):** `launchRetry` produces `{ contract: 'N28-to-N30-remediation-retry', remediation_entry_id, family_id, outcome_id, excluded_instance_ids, selected_instance_id, selected_variant_id, selection_source, ephemeral_spec, filters, counts_against_practice_bound: true }`. Retries respect `practicePath` bounds (`PATH_EXHAUSTED` without bypass when `remaining <= 0`). Graded retry verdicts invoke `recordRetryVerdict` to update `SimMastery`, progress stats, and the queue entry in one atomic `SimStore.update` transaction.
- **To N35 (privacy audit):** All queue entries live inside `sim_colloq1_store_v2.remediation_queue` (`remediation_queue_fields` listed in `data/analytics_schema.json`); `check_n28_runtime.js` records zero memory writes, zero outlier keys, zero leaked answer text, zero network calls, and zero erase residue (`evidence/N28_PRIVACY_AUDIT.json`).
