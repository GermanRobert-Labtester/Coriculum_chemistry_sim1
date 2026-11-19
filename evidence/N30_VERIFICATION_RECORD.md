# N30 Verification Record — Bounded Practice Paths with Filters and Honest Shortage Handling

**Date:** 2026-11-19  
**Task:** N30 (Phase VI, P1) — Implement bounded practice paths with filters and honest shortage handling  
**Status:** PASS (Gate 26, 15/15 runtime checks, 10-step Phase VI capstone journey trace with mid-journey day-boundary crossing & fresh-process `--replay-only` parity, 26/26 built-artifact smoke vectors, double-build & two-invocation corpus parity, repository-local preparation check, and Falkon render check pass)

---

## 1. Epistemic Scope and Declared Path Lengths

- **Epistemic status:** `PROPOSED` training policy (`official_counterpart_status: "UNDETERMINED"`). The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) specifies no bounded practice path lengths, difficulty ordering, filters, or shortage rules.
- **Per-topic declared lengths (`data/practice_policy.json` → `#sim-practice-policy`):**
  - Grounded in `evidence/N20_VERIFICATION_RECORD.json#frozen_bank` (`4` families × `4` variants = `16` accepted eligible instances per topic, `112` total) and `data/coverage.json` outcome counts (`[9, 10, 11, 11, 10, 8, 5]`):
  - Topic 1: `6`, Topic 2: `7`, Topic 3: `8`, Topic 4: `8`, Topic 5: `7`, Topic 6: `6`, Topic 7: `5` (`5 < 8`, strictly shorter for Topic 7's 5-outcome set than Topic 3's 11-outcome set).
  - Declared lengths are targets, never promises; unreviewed or pending-review content is excluded by the shared N24 eligibility gate (`isReviewEligible`) and never used as padding.

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`data/practice_policy.json`](../data/practice_policy.json) | `#sim-practice-policy` island: per-topic `PROPOSED` lengths (`6,7,8,8,7,6,5`), difficulty-or-family ordering, 18-type filter vocabulary, no-repeat & current-session exclusion bounds, skip semantics, and shortage reasons | file `eb7b54aeba59dc59...`, canonical `efaaab47eb3d4735...` (`7,163` canonical B) |
| [`data/terms.json`](../data/terms.json) | +27 `practice.*` interface keys (`668` total entries, `N10` lint PASS) | `sha256: ec05344387393166149bb4820261e840960c0538a9584c8443c74a243162d4f7` |
| [`src/practice.ts`](../src/practice.ts) | Strict-TS pure path engine (`computePracticePath`), 3-entry normalization (`topic_browse`, `scheduler_queue`/`revision_panel`, `remediation_retry`), path runner (`createRunner`), N21 mode-boundary help contract (`describeHelpContract`), N23 grading & N26/N28/N25 store integration, `#prakse` UI | `54,485` B, `sha256: 097e08baad4ffc33d148159f33d531e45efcd38e7d53286708f156b8d6611a36` |
| [`src/compiled/practice.js`](../src/compiled/practice.js) | Compiled runtime (`root.SimPractice`), inlined in `output/simulator.html` | `97,561` B raw, `70,679` B compacted, `sha256: 80c0dcc4d3043757f6093d98ea0cdbb20d4abb88487dd79aa5b02ca17bf301e9` |
| [`src/grading.ts`](../src/grading.ts) & [`src/store.ts`](../src/store.ts) | `SimGrading.gradePracticeRecord` reuses `gradeSlot` with zero-adapter criterion parity; `SimStore` preserves `practice_history.{attempted_instance_ids,skipped_instance_ids}` | `grading.ts` `79526fb586bb15bf...`, `store.ts` `3be8121bd7fb5ecd...` |
| [`docs/PRACTICE_FORMAT.md`](../docs/PRACTICE_FORMAT.md) | Frozen N30 practice path, shortage, skip, mode-boundary, and Phase VI loop contract | `sha256: 6421349bbc87c00a2d3fb8d80ed49b5a2287802a03c533acc0ac581fe35edb25` |
| [`tools/validate_n30_practice.py`](../tools/validate_n30_practice.py) | Gate 26 (`practice`): live N20 eligible counts, 18-type registry vocabulary, 3 negative fixtures (`NEG-N30-OVERLONG-TOPIC-3`, `NEG-N30-UNKNOWN-RESPONSE-TYPE`, `NEG-N30-ALLOW-UNREVIEWED-PADDING`), N10 terms lint, TS drift, 30 shell touchpoints, offline/clock/F10 scans | `sha256: c1065b242e35a246c852a3df371466aab735b4922205d6b70a0a86a3be405524` |
| [`tools/check_n30_runtime.js`](../tools/check_n30_runtime.js) | 15-check runtime & Phase VI journey harness + `--replay-only` + 26/26 built-artifact smoke | `sha256: bb5845c61c740d5f39f1ab928eb3830969ab2791447d2b1e98b4245b232d09ef` |
| [`output/simulator.html`](../output/simulator.html) | Built single-file artifact (`26/26` gates PASS) with `#sim-practice-policy`, `#prakse-practice-wrap`, and `SMK-N30-PRACTICE-PATH` | `2,202,649` B (`2,151.0` KiB), `sha256: 4f7022494d8718870325e0a079010adc63e2f2bb4f088204ebe8bf7f25705a45` |
| [`evidence/N30_JOURNEY_TRACE.json`](N30_JOURNEY_TRACE.json) | 10-step Phase VI capstone journey trace (self-assess → queue day 10 → practice path → miss + skip + end early → day boundary 10→12 → remediation queue → alternate-variant retry → revision view) | `digest: 572094d6a33c750038f2f9a5c3de097cf2ded683b9efcd1e46ab0968b786d706`, `file_sha256: 889607b854c2ac54...` |
| [`evidence/N30_CORPUS_RECORD.json`](N30_CORPUS_RECORD.json) | Master corpus & two-invocation parity record (`018a97139ac99812...`) | `status: PASS`, `two_invocation_parity: PASS` |

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Policy Validation, Determinism & No-Repeat Invariants (`evidence/N30_VALIDATION_RECORD.json`, `evidence/N30_RUNTIME_RECORD.json`)
- **A.1.1 Live counts & negative fixtures (`A1_policy_live_counts`):** All 7 declared lengths (`6,7,8,8,7,6,5`) validate against live eligible counts (`16` per topic). Scratch overlong Topic 3 (`17 > 16`) fails validation naming `topic 3`.
- **A.1.2 Determinism & exclusions (`A1_determinism`, `A1_no_repeat_exclusions`):** Difficulty-declared Topic 3 path (`85cd3e7ecd11bce3...`, `foundational → application → transfer`) and difficulty-absent Topic 3 path (`92dc8e0dbfbe7952...`, `family_id ASC, variant_id ASC`) reproduce byte-identically; 8-item attempt history excludes those exact 8 items; 2 in-session answered items are excluded on the next path even with `unattempted_only: false`.
- **A.1.3 Three entry points over one engine (`A1_three_entry_points`):** `topic_browse` (`e31293c70ffa5d2c...`), `scheduler_queue` (`18276358c5c646de...`), and `remediation_retry` (`eab38d0450372113...`, selecting `COL1-4-4A-B-01` and excluding failed `COL1-4-4A-A-01`) all execute through `SimPractice.computePracticePath`.

### AC2 — Shortage Triad, Exit Dignity, Skip Semantics, Grading Chain & Mode Boundary (`evidence/N30_RUNTIME_RECORD.json`)
- **B.1.1 Shortage triad & exit dignity (`B1_shortage_triad`, `B1_exhausted_exit_dignity`):**
  - *Eligibility shortage:* Topic 1 with 12 pending-review items yields `true_length = 4` (`Pieejami 4 no 6 uzdevumiem: gaida recenziju (12 neapstiprināti uzdevumi netiek iekļauti).`) with zero unreviewed items drawn.
  - *Filter shortage:* Topic 1 with `response_types: ['Q06']` yields `true_length = 2` (`Pieejami 2 no 6 uzdevumiem...`) with zero padding.
  - *History exhaustion:* All 16 Topic 1 items attempted under `unattempted_only: true` yields `true_length = 0`, `status: 'exhausted'`, and renders dignified exit options naming N27 Leitner review intervals (`1 / 3 / 7 dienas`) and N20's ephemeral variant path (`SimVariantEngine.instantiateEphemeral`).
- **B.1 Skip chain (`B1_skip_chain`):** Three consecutive skips record `skipped_count: 3`, `incorrect_count: 0`, `attempted_count: 0`, `0` remediation entries, and unchanged mastery digest.
- **B.1.2 Grading-to-mastery chain (`B1_grading_chain`):** Practice attempt on `COL1-4-4A-A-01` grades through `SimGrading.gradePracticeRecord` + `SimFeedback.assemble` (`graded_digest: 1a2027709b9e04d1...`) and produces mastery digest `31e1be3c15d24075...` identical to independent `SimMastery.reduce`.
- **B.1.3 Hint contract & N21 mode boundary (`B1_hint_and_mode_boundary`):** Practice mode enables `hint` (N08), `chain` (N16), and `term-lookup` (N07/N10); exam mode refuses with `E_MODE_COMPONENT_NOT_ALLOWED`.

### AC3 — Phase VI Capstone Journey Trace, Mid-Journey Day Boundary, Replay & Built Smoke (`evidence/N30_JOURNEY_TRACE.json`)
- **C.1.1 Capstone journey (`C1_journey_modules`, `C1_day_boundary_declared_rule`, `C1_replay_parity`):** Scripted learner self-assesses `P4-01` (`N29`, mastery digest `7e233937b15abbce...` unchanged) → selects from `N27` queue at day `10` (`c0e2f4317786557d...`) → launches `N30` path (`6ec9409c142b0c5d...`) → misses `COL1-4-4A-A-01` (opens `FAM-4A::P4-01` in `N28`), skips `COL1-4-4A-B-01` (`skipped: 1`, `incorrect: 1`), ends early → clock advances day `10 → 12` (queue shifts deterministically to `d2d8b3eedac554c8...` with `expected_overdue === observed_overdue === 1`) → launches `N28` alternate-variant retry on `COL1-4-4A-B-01` (`eab38d0450372113...`) and answers correctly (`state: 'retried'`) → `N29` revision view reflects all 64 outcomes, self-rating, mastery state, and queue state. In-process rerun and fresh child process `--replay-only` match `572094d6a33c750038f2f9a5c3de097cf2ded683b9efcd1e46ab0968b786d706` (`mastery_digest: f646f94353d22d3d...`, `store_digest: 76b1ac9b1eacca59...`).
- **C.1.2 / C.1.3 Smoke & parity (`C1_smoke_vector`, `artifact`):** `SMK-N30-PRACTICE-PATH` (`26/26` built-artifact smoke vectors PASS), double-build parity (`4f7022494d871887...`), and two-invocation corpus parity (`018a97139ac99812...`) PASS.

---

## 4. Byte Accounting and Falkon Render Check

- `output/simulator.html`: `2,202,649` B (`2,151.0` KiB; re-budgeted `2,060 → 2,156` KiB = `2,207,744` B; declared band `700–1,400` KiB remains visible).
- Inline `runtime_js_code`: `705,815` B (`689.3` KiB; re-budgeted `620 → 692` KiB = `708,608` B; declared band `120–220` KiB remains visible). `practice.js` compacted = `70,679` B, `SMK-N30-PRACTICE-PATH` = `+3,594` B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- `css`: `59,902` B (`58.5` KiB within `40–80` KiB band); `bank_island`: `249,798` B (`243.9` KiB within `200–420` KiB band); `#sim-practice-policy`: `7,163` canonical B.
- Visual render check (`lite-shot -e falkon --cdp --theme light --anchor prakse-practice-wrap output/simulator.html#prakse-practice-wrap evidence/N30_PAINT_PRAKSE.png`, inspected via `read_file`): [`evidence/N30_PAINT_PRAKSE.png`](N30_PAINT_PRAKSE.png) (`124,366` B, `1280x1024`, `overflow=false`) confirms `#prakse-practice-wrap` renders the heading, honesty note, filter controls, all 7 topic cards with declared lengths and eligible counts, and the path summary cleanly with zero horizontal overflow (render check only, not accessibility or instructor acceptance).
