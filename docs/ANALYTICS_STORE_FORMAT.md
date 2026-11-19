# ANALYTICS_STORE_FORMAT.md — N25 Versioned Local Store & Privacy-Safe Progress Contract

**Owner:** N25 · **Status:** frozen interface for N26–N30, N31, N35, N38, and N40  
**Modules:** `src/store.ts` → `src/compiled/store.js` (`root.SimStore`), `src/analytics.ts` → `src/compiled/analytics.js` (`root.SimAnalytics`)  
**Island:** `#sim-analytics` (`data/analytics_schema.json`) · **Gate:** `tools/validate_n25_analytics.py` (Gate 21 `analytics`)

> **Epistemic & privacy note.** Per `AGENTS.md`, default sessions are **in-memory only** and discard progress on close. Persistence to `localStorage` happens **only** after explicit learner opt-in in `#iestatijumi`, touches only the schema key `sim_colloq1_store_v2`, stores **zero answer text**, makes **zero network attempts**, and claims **no official RSU examination, grade, or competency status** (`PROPOSED` self-study tracking only).

---

## 1. Storage Schema (`schema_version: 2`)

- **Default mode:** `memory` (`opt_in: false`), zero `localStorage` reads/writes/keys.
- **Opted-in key set:** `["sim_colloq1_store_v2"]` (exact key set; zero outlier keys).
- **Canonicalization & digest:** N04 sorted-key UTF-8 JSON (`canonicalText`) + SHA-256 (`digestValue` / `digestOf`), matching `SimGrading`.
- **Bounded event log:** `max_events = 200`, pruned **oldest-first**; `events_pruned_count` records total pruned events.
- **Migration & newer-version guard:**
  - `schema_version === 1` → migrated to `v2` via `SimStore.migrateV1ToV2` (`opt_in`/`theme` → `settings`, `practiced_topics`/`correct_outcomes` → `progress`, `forms` → `progress.form_history`, `remediation` → `remediation_queue`, `events` bounded to `200`).
  - `schema_version > 2` → **ignored** with visible Latvian notice (`NEWER_VERSION_IGNORED`) and write-locked (`E_STORE_WRITE_BLOCKED_NEWER_VERSION`) so an older runtime never overwrites a newer store.
  - Pre-mastery `v2` stores omit `mastery`; when N26 adds `mastery`, an absent key maps to all-unseen and `SimStore` preserves any existing `mastery` object across updates.
- **Export & two-step erase:**
  - `exportProgress()` emits canonical JSON (`kimija-kolokvijs1-progress-v2.json`) with `store_digest === SimStore.digestOf(store)`.
  - `requestErase()` → `confirmErase()` (or `erase(true)`) removes schema keys and resets UI state; unconfirmed erase throws `E_STORE_ERASE_CONFIRMATION_REQUIRED`.

---

## 2. Analytics Event Chain & Honest Progress Summary

- `SimAnalytics.extractEvents(fullRecord)` is a pure, clock-free function over N23's digest-sealed `GradedRecord`:
  - `session-completed` (`form_id`, `session_id`, `auto_score`, `pending_count`, `elapsed_ms`, `graded_digest`)
  - `task-answered` (`slot_id`, `topic`, `family_id`, `type_id`, `criterion_verdicts[]`, `graded_digest`; **no answer text**)
  - `remediation-state` (`slot_id`, `state: "open" | "resolved"`, `concept_ids[]`, `chain_ids[]`, `signature_id`, `graded_digest`)
- **Unblended totals:** `auto_points`/`auto_max_points` and `pending_external_points`/`pending_max_points` are stored and rendered separately (`unblended: true`) in `#atskats`.
- **64-outcome tracking:** Tracks `unattempted`, `attempted`, `first_pass_correct`, and `correct_after_retry` over `#sim-coverage`; topics with zero activity display `0` honestly.
- **Remediation queue (`N25` → `N28`):** Missed items enter `remediation_queue` (`state: "open" | "retried" | "resolved"`) inside `sim_colloq1_store_v2` (zero extra `localStorage` keys). N25 records `slot_id`, `topic`, `family_id`, `instance_id`, `signature_id`, `concept_ids[]`, `chain_ids[]`, `method_card`, and `graded_digest`; N28 extends items with `dedup_key`, `slot_ids[]`, `outcome_id`, `outcome_ids[]`, `signature_ids[]`, `graded_digests[]`, `miss_count`, `retry_count`, `attempted_instance_ids[]`, `attempted_variant_ids[]`, `last_retry_instance_id`, `last_retry_variant_id`, `last_retry_verdict`, `last_retry_digest`, `resolved_reason`, `resolved_reason_lv`, and `retried_seq` (all recorded in `data/analytics_schema.json#/store_contract/remediation_queue_fields` for N35 privacy audit continuity).
- **N28 (remediation):** `SimRemediation` manages `(family_id, outcome_id)` deduplication, alternate-variant retries, study handoffs, on-read link validation, and honest resolution under `#sim-remediation-policy`; `SimAnalytics.ingestGradedRecord` delegates to `SimRemediation.applyGradedRecordDraft` when `SimRemediation` is loaded.

---

## 3. Rejected Feature Boundary (`F10`)

- **Rejected feature:** `F10` analytics dashboards (charts, streaks, gamification, score-history visualizations), per `Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md` §4.3 & `evidence/VERIFICATION_LEDGER.md`.
- **Reasoning:** Completionist visualization serves the tracker, not the learner.
- **Enforcement:** `SimAnalytics.F10_BOUNDARY` records the rejection; Gate 21 and `check_n25_runtime.js` assert zero exported chart/streak/gamification/scoreHistory symbols and zero `<canvas>` or streak UI in `#atskats`.

---

## 4. Downstream Interfaces

- **N26 (mastery):** Consumes `SimStore.createStore` / `update` / `setState` and `SimAnalytics.extractEvents`; extends `v2` with optional `mastery` map (absent → all-unseen).
- **N28 (remediation):** Consumes `store.getState().remediation_queue` (`state === 'open'`) and resolves items via `SimAnalytics.resolveRemediationItem(store, itemId)`.
- **N31 (build):** Decides final inline vs lazy-load packaging for `store.js` and `analytics.js`.
- **N35 / N38 / N40 (security, E2E, release):** Re-run `tools/check_n25_runtime.js` (`N25_PRIVACY_AUDIT.json` baseline: zero outlier `localStorage` keys, zero network attempts, zero answer-text persistence, migration & erase residue checks).
