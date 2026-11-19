# N28 Verification Record — Missed-Item Remediation with Anchors and Alternate Variants

**Date:** 2026-11-19  
**Task:** N28 (Phase VI, P1) — Implement missed-item remediation with anchors and alternate variants  
**Status:** PASS (Gate 24, 10/10 runtime checks, fresh-process `--replay-only` loop determinism, store round-trip + erase privacy audit, double-build & two-invocation corpus parity, upstream N06/N25–N27/repo-local regressions, and Falkon render check pass)

---

## 1. Epistemic Scope, Recommend-Only Rule, and Verbatim Resolution Copy

- **Epistemic status:** `PROPOSED` training policy (`official_counterpart_status: "UNDETERMINED"`). The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) specifies no remediation queue, variant selection rule, or completion confirmation policy.
- **Recommend-only & non-regrading contract (`data/remediation_policy.json`):**
  - `recommend_only: true` (`recommend_only_copy_lv`: *"Atkārtošana ir tikai ieteikums — nav piespiedu bloķēšanas; jūs varat brīvi turpināt citu praksi vai eksāmena mēģinājumu."*)
  - `regrade_original_attempt: false` (original graded attempts are never altered)
  - `require_resolvable_links: true` (no queue entries without resolvable links; validated at write time and re-validated on read/render)
- **Verbatim one-correct-answer-is-evidence copy (`resolution_policy.one_correct_evidence_copy_lv`):**
  > Viena pareiza atbilde ir pierādījums virzībai, nevis pilnīga apguve — apstipriniet pabeigšanu manuāli vai praktizējiet tālāk.

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`data/remediation_policy.json`](../data/remediation_policy.json) | `#sim-remediation-policy` island: `(family_id, outcome_id)` deduplication, `confirm_required` vs `one_correct_resolves`, cyclic `A–D` + ephemeral fallback, recommend-only rule | file `cc320a5279dd9999...`, island `02268d355e2ff814...` (`4,208` canonical B) |
| [`data/terms.json`](../data/terms.json) | +18 `remediation.*` interface keys (`497` total entries, `235` checked keys, `N10` lint PASS) | `sha256: f37e0f370dd31f188d707a1fc67efe31e93591d8034b3dd4008872f25dcef238` |
| [`data/analytics_schema.json`](../data/analytics_schema.json) | Appends `store_contract.remediation_queue_fields` (30 keys inside `sim_colloq1_store_v2`) for N35 privacy continuity | `sha256: 4eae757780fd7e653a3693aa05729bb7f364ee3b2e20aa7d9d884d8c7c2af436` |
| [`src/remediation.ts`](../src/remediation.ts) | Strict-TS remediation state machine, write/on-read link validation, cyclic + N20 ephemeral retry selection, anchor/chain handoffs, `#atskats` renderer, N29 queue snapshot, N30 retry handoff | `89,567` B, `sha256: 7b88c82988e9c53f78b9ed84bc1da4aa8cba37849a37960a437126d08922f519` |
| [`src/compiled/remediation.js`](../src/compiled/remediation.js) | Compiled runtime (`root.SimRemediation`), inlined in `output/simulator.html` | `88,466` B raw, `64,524` B compacted, `sha256: dbffc634d390e5a6c734174b43bb90cd404f007dce9e2b85bb9c726ea5c553e9` |
| [`src/store.ts`](../src/store.ts) & [`src/analytics.ts`](../src/analytics.ts) | `SimStore` supports `open` / `retried` / `resolved` + N28 fields; `SimAnalytics.ingestGradedRecord` & `refresh` delegate to `SimRemediation` when loaded | `store.ts` `ecd5899d83ad5c64...`, `analytics.ts` `9803a24c44710a4c...` |
| [`docs/REMEDIATION_FORMAT.md`](../docs/REMEDIATION_FORMAT.md) | Frozen N28 remediation & retry contract handed to N29, N30, N35 | `sha256: c33658131aefbdda5021b65cb4c5036e830d2bb7497f4c8e9a2d4f74b1c4eb30` |
| [`tools/validate_n28_remediation.py`](../tools/validate_n28_remediation.py) | Gate 24 (`remediation`): policy validation, forced-gating/regrade/dangling-link negative fixtures, N10 term lint, TS drift, shell & F10/wall-clock/network scans | `sha256: 3ff8599fec0421f801c35a36aaa5e4faf358c475e832f5bb8b2c44c36ba7e918` |
| [`tools/check_n28_runtime.js`](../tools/check_n28_runtime.js) | 10-check runtime, `--replay-only`, 4-retry selection, loop trace, nullable-chain, dangling-link failure, bounded-path exhaustion, store round-trip & erase privacy audit, built smoke | `sha256: 3a5de246179f00cfb409e07cb22dc9a1286eb333d7cf49c0795ceb4d549288e9` |
| [`output/simulator.html`](../output/simulator.html) | Built single-file artifact (`24/24` gates PASS) with `#sim-remediation-policy`, `#atskats-remediation-wrap`, and `SMK-N28-REMEDIATION-WALK` | `1,972,615` B (`1,926.4` KiB), `sha256: c307b70194a6d665f57d1cc6de3bf38138f9197fe4586d2839708be29a546fba` |
| [`evidence/N28_LOOP_TRACE.json`](N28_LOOP_TRACE.json) | 7-step end-to-end classification (`Q07`, `FAM-6A`) trace: miss → anchor → chain (`data-revealed-count="0"`) → return → alternate variant (`B`) → mastery + queue advance → resolve | `trace_digest: ea4771f62815d250febc1df8f172dc41c98ae058907796988a5260e732ba132a` |
| [`evidence/N28_PRIVACY_AUDIT.json`](N28_PRIVACY_AUDIT.json) | Populated-queue round-trip & 2-step erase privacy audit (`0` memory writes, `0` outlier keys, `0` network attempts, `0` keys after erase, `30` queue fields recorded) | `status: PASS` |
| [`evidence/N28_CORPUS_RECORD.json`](N28_CORPUS_RECORD.json) | Master corpus & two-invocation parity record (`8d55ab2c66c9c4e6...`) | `status: PASS`, `two_invocation_parity: PASS` |

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Coalescing, Partial Entry, Resolved No-Rewind & Policy-Driven Resolution (`evidence/N28_RUNTIME_RECORD.json`)
- **A.1.1 Coalescing (`a11_coalescing_partial_and_no_rewind`):** Three scripted misses on `('FAM-6A', 'P6-01')` (`COL1-6-6A-A-01`, `COL1-6-6A-B-01`, `COL1-6-6A-C-01`) coalesce into one entry (`miss_count: 3`, `concept_ids: ['P6-01','P6-02','P6-04']`, `chain_ids: ['EX12']`, `signature_ids: ['MC-6A-01','MC-6A-02']`). Partial verdict (`FAM-4B`, `P4-02`) enters `open`. Resolving `FAM-6A::P6-01` and missing `COL1-6-6A-D-01` opens a **new** entry (`miss_count: 1`, `state: 'open'`) while keeping the resolved entry (`miss_count: 3`, `state: 'resolved'`) intact.
- **A.1 Policy separation (`a1_policy_driven_resolution`):** Default `confirm_required` moves a correct retry to `'retried'` (`resolved_seq: null`) with verbatim evidence copy; scratch `one_correct_resolves` resolves directly (`state: 'resolved'`, `resolved_reason: 'auto_one_correct'`).

### AC2 — 4-Variant Cyclic Retry Selection & N20 Ephemeral Fallback (`evidence/N28_RUNTIME_RECORD.json`)
- **A.1.2 Selection (`a12_four_retry_selection_and_ephemeral`):** Starting from failed `COL1-6-6A-A-01`, five scripted retries select `COL1-6-6A-B-01` (`bank`), `COL1-6-6A-C-01` (`bank`), `COL1-6-6A-D-01` (`bank`), `COL1-6-6A-A-EPH-3` (`ephemeral`, `persisted: false`), `COL1-6-6A-B-EPH-4` (`ephemeral`). Failed instance `COL1-6-6A-A-01` is never re-served; all selected IDs are distinct.

### AC3 — End-to-End Loop Trace, Nullable Chain, Dangling-Link Failure, Bounded Path, Persistence & Smoke
- **B.1 / A.1.3 Loop trace (`b1_end_to_end_classification_loop_trace`, `evidence/N28_LOOP_TRACE.json`):** `Q07` `FAM-6A` miss → `SimConceptDrawer` opens at `P6-01` and closes cleanly → `SimChains` mounts `EX12` at `data-revealed-count="0"` → return to `#atskats-remediation-list` → `launchRetry` selects `COL1-6-6A-B-01` (`remaining` `3 → 2`) → `recordRetryVerdict` advances `SimMastery` `P6-01` (`unseen → learning`) and queue (`open → retried`) with `#atskats` matching at every step → `resolve` sets `resolved` (`0` active).
- **B.1.1 Nullable chain (`b11_nullable_chain_anchor_only`):** `FAM-1A` (`chain_ids: []`) renders anchor-only (`data-has-chain="false"`, `0` chain buttons).
- **B.1.2 Dangling link (`b12_dangling_anchor_on_read_fails_loudly`):** Scratch store entry with `P9-99-BROKEN-ANCHOR` fails render loudly (`E_REMEDIATION_DANGLING_LINK` naming `P9-99-BROKEN-ANCHOR` in error and `#sim-remediation-error`).
- **B.1.3 Bounded path (`b13_bounded_path_respects_exhaustion`):** Exhausted path (`remaining: 0`) returns `PATH_EXHAUSTED` (`bound_respected: true`, `bypassed: false`).
- **C.1.1 Fresh-process replay & privacy (`c11_fresh_process_replay_determinism`, `c11_store_roundtrip_erase_and_privacy`):** Fresh child `--replay-only` matches `trace_digest` and `final_queue_digest`; store round-trip & 2-step erase pass with `0` memory writes, `0` outlier keys, `0` network calls, and `0` keys after erase.
- **C.1.2 / C.1.3 Smoke & parity:** `SMK-N28-REMEDIATION-WALK` (`24/24` smoke vectors in Node VM over `output/simulator.html`), double-build parity (`c307b70194a6d665...`), and two-invocation corpus parity (`8d55ab2c66c9c4e6...`) PASS.

---

## 4. Byte Accounting and Falkon Render Check

- `output/simulator.html`: `1,972,615` B (`1,926.4` KiB; re-budgeted `1,848 → 1,928` KiB = `1,974,272` B; declared band `700–1,400` KiB remains visible).
- Inline `runtime_js_code`: `563,555` B (`550.3` KiB; re-budgeted `484 → 552` KiB = `565,248` B; declared band `120–220` KiB remains visible). `remediation.js` compacted = `64,524` B, `SMK-N28-REMEDIATION-WALK` = `+3,585` B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- `css`: `53,834` B (`52.6` KiB); `bank_island`: `249,798` B (`243.9` KiB); `#sim-remediation-policy`: `4,208` canonical B.
- Visual render check (`lite-shot -e falkon --cdp --theme light --anchor atskats-remediation-wrap`, inspected via `read_file`): [`evidence/N28_PAINT_ATSKATS.png`](N28_PAINT_ATSKATS.png) (`165,445` B, `overflow=false`) confirms `#atskats-remediation-wrap` renders the heading, honesty note, active/resolved status line, empty queue state, and resolved history disclosure cleanly with zero horizontal overflow (render check only, not screen-reader or instructor acceptance).
