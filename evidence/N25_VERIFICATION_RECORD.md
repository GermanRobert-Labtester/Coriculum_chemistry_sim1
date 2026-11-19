# N25 Verification Record — Local, Privacy-Safe Analytics and the Honest Progress Record

**Date:** 2026-11-19  
**Task:** N25 (Phase V, P1) — Implement local, privacy-safe analytics and the honest progress record  
**Status:** PASS (all code, Gate 21, runtime & privacy audit, double-build & two-invocation corpus parity, upstream regressions, and Falkon render checks pass)

---

## 1. Epistemic Scope and Privacy Boundary

Per `AGENTS.md`, default sessions operate strictly in-memory and discard progress on close; `localStorage` persistence occurs only under explicit learner opt-in in `#iestatijumi`, touches only `["sim_colloq1_store_v2"]`, stores zero learner answer text, makes zero network attempts, and makes zero official RSU exam, grade, or competency claims (`PROPOSED` self-study tracking only).

- **F10 boundary (`rejected-by-policy`):** Predecessor feature `F10` (analytics dashboards, completionist charts, streaks, gamification, score-history visualizations) is rejected per `Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md` §4.3 and `evidence/VERIFICATION_LEDGER.md` (completionist visualization serves the tracker, not the learner). `SimAnalytics.F10_BOUNDARY` records the rejection, and Gate 21 plus `tools/check_n25_runtime.js` verify zero banned exports or `<canvas>`/streak UI.

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`data/analytics_schema.json`](../data/analytics_schema.json) | `#sim-analytics` v2 contract island, migrations, F10 boundary, verbatim Latvian copy | `6,098` canonical B, `sha256: 62f8d68d6d3fc79419bf2fbb8e47eba68fd273f692f82e3ea8be830f4da85584`, island `dc9c5daea210b1c10ba7016d497141357203ec94224743cd7925485ef772133e` |
| [`src/store.ts`](../src/store.ts) | Strict-TS versioned store (`SimStore`), in-memory default, opt-in `localStorage`, v1→v2 migration, newer-version ignore+lock, export, two-step erase | `sha256: 81304881539fb8deebc22fe3c520d9a26ffc82ceb0de2998a47a5ee7b2262947` |
| [`src/compiled/store.js`](../src/compiled/store.js) | Compiled runtime (`root.SimStore`), inlined in `output/simulator.html` | `36,642` B raw, `25,744` B compacted, `sha256: 25830414092320c2c38b0c428589fc5d23430a4f0478fb7f31b29c7e853ddf38` |
| [`src/analytics.ts`](../src/analytics.ts) | Strict-TS pure event chain (`SimAnalytics`), bounded log (`max_events=200`), 64-outcome tracking, remediation queue lifecycle, `#atskats` & `#iestatijumi` UI | `sha256: 39166736a610430f557173addf175173684c43adb448d928ea4e8b2603820239` |
| [`src/compiled/analytics.js`](../src/compiled/analytics.js) | Compiled runtime (`root.SimAnalytics`), inlined in `output/simulator.html` | `44,803` B raw, `31,951` B compacted, `sha256: 0cb7cf05d8ca4001a4b675c80d61fe05a8ff484734540545f10b81353b9c4922` |
| [`docs/ANALYTICS_STORE_FORMAT.md`](../docs/ANALYTICS_STORE_FORMAT.md) | Frozen N25 interface contract for N26–N30, N31, N35, N38, and N40 | `sha256: d84c67c82ba1dff7b1205eaf14d4a3f01474809635da360960ef257ad5000101` |
| [`tools/validate_n25_analytics.py`](../tools/validate_n25_analytics.py) | Gate 21 (`analytics`): schema, TS drift, 27 shell touchpoints, no-network/no-clock/F10 scans | `sha256: e5e23431db22a4026d1885ad131fbdabb8f2a72dc5cd7a549b3096dc15e7a839` |
| [`tools/check_n25_runtime.js`](../tools/check_n25_runtime.js) | Runtime, storage contract, event chain, bounded-log, privacy & outlier audit harness | `sha256: fcdd71f21121b87fb59affd36f3a7024c2b935eaff6be8d52591359f21048811` |
| [`output/simulator.html`](../output/simulator.html) | Built single-file artifact with `#sim-analytics`, `#atskats`, `#iestatijumi` controls, and `SMK-N25-STORE-ROUNDTRIP` | `1,756,388` B (`1,715.2` KiB), `sha256: b59cf2e20bf665d098d462d5bdb636a3db792a1b945cc2ae03412575597aeb64` |
| [`evidence/N25_CORPUS_RECORD.json`](N25_CORPUS_RECORD.json) | Master corpus & two-invocation parity record (`4bdeef0e7c064ca4...`) | `status: PASS`, `two_invocation_parity: PASS` |

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Storage Contract, Opt-In Boundary, Migration & Erase (`evidence/N25_RUNTIME_RECORD.json`)
- **A.1.1 Canonical round-trip & reload:** `SimStore` canonical SHA-256 matches Node `crypto`; reloading in a fresh VM yields identical digest `daf0ae365aa9294383d7c0edb91def0f0b08ba1069fa09ae3e2c4493f6c7ba88` (`16,178` stored bytes).
- **A.1.2 Opt-in boundary:** Default in-memory session leaves `[]` keys and `0` `localStorage` accesses; explicit opt-in persists only `["sim_colloq1_store_v2"]`; Latvian consent copy states what is stored, that nothing leaves the device, and how to erase.
- **A.1.3 Export & two-step erase:** Export (`kimija-kolokvijs1-progress-v2.json`) parses and matches `store_digest`; unconfirmed `erase(false)` / `confirmErase()` fail with `E_STORE_ERASE_CONFIRMATION_REQUIRED`; two-step confirmation empties `localStorage` (`[]` keys) and resets `#atskats`/`#iestatijumi` UI state.
- **A.1 Migration & newer-version guard:** Scratch `v1` store migrates cleanly to `v2` (`MIGRATED_V1_TO_V2`); scratch `schema_version: 99` store is ignored with visible Latvian notice (`NEWER_VERSION_IGNORED`), never overwritten (`E_STORE_WRITE_BLOCKED_NEWER_VERSION`).

### AC2 — Bounded Log, Pure Event Chain, Unblended Honesty & Remediation (`evidence/N25_RUNTIME_RECORD.json`)
- **B.1.1 Event chain over `FX-N23-MIXED`:** `SimAnalytics.extractEvents` matches `SimGrading.toAnalyticsEvents` byte-for-byte (`25` events: `1` `session-completed`, `19` `task-answered`, `5` `remediation-state`), every event carries `graded_digest`, `0` answer strings leak.
- **B.1 Bounded log & unblended display:** Appending `215` events yields `200` retained events (`events_pruned_count: 15`, oldest `1..15` pruned, `16..215` kept). Mixed form renders `18/48` auto and `37/52` (`13 vietas`) pending separately, never `55/100`.
- **B.1.2 64-outcome tracking:** Fresh state shows honest `0` across all 7 topics (`0/9`, `0/10`, `0/11`, `0/11`, `0/10`, `0/8`, `0/5`); mixed-form ingestion updates `13` outcomes to `first_pass_correct`.
- **B.1.3 Remediation queue lifecycle:** `5` items enter `open`; resolving `2` via `SimAnalytics.resolveRemediationItem` updates `#atskats-remediation-count` to `"3"` and persists `"3"` across VM reload.

### AC3 — Privacy Audit, F10 Boundary & Built-Artifact Smoke (`evidence/N25_PRIVACY_AUDIT.json`, `evidence/N25_CORPUS_RECORD.json`)
- **C.1.1 Full-session privacy audit:** Memory phase records `0` `localStorage` writes and `0` keys; opt-in/export/erase phase records `5` accesses touching only `sim_colloq1_store_v2`, `0` outlier keys, `0` leaked answer strings, `0` network attempts, `0` keys after erase; negative test catches rogue key `sim_render_cache`.
- **C.1.2 F10 boundary:** Zero banned exports on `SimAnalytics` or `SimStore`; zero `<canvas>` or streak UI in `#atskats`.
- **C.1.3 Built-artifact smoke & parity:** `SMK-N25-STORE-ROUNDTRIP` (`roundTripDigest: f8d7ca02466584a8...`) and `21/21` smoke vectors pass in Node VM over `output/simulator.html`; double-build parity (`b59cf2e20bf665d0...`) and two-invocation corpus parity (`4bdeef0e7c064ca4...`) pass.

---

## 4. Byte Accounting and Falkon Render Checks

- `output/simulator.html`: `1,756,388` B (`1,715.2` KiB; re-budgeted `1,680 → 1,720` KiB = `1,761,280` B; declared band `700–1,400` KiB remains visible).
- Inline `runtime_js_code`: `390,841` B (`381.7` KiB; re-budgeted `332 → 388` KiB = `397,312` B; declared band `120–220` KiB remains visible). `store.js` = `25,744` B, `analytics.js` = `31,951` B, `SMK-N25-STORE-ROUNDTRIP` = `+3,011` B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- `css`: `46,521` B (`45.4` KiB); `bank_island`: `249,798` B (`243.9` KiB); `#sim-analytics`: `6,098` canonical B.
- Visual render checks (`lite-shot -e falkon --cdp --theme light`, inspected via `read_file`): [`evidence/N25_PAINT_ATSKATS.png`](N25_PAINT_ATSKATS.png) (`118,016` B, `overflow=false`) and [`evidence/N25_PAINT_IESTATIJUMI.png`](N25_PAINT_IESTATIJUMI.png) (`142,107` B, `overflow=false`) confirm `#atskats` and `#iestatijumi` layout and zero-state rendering (render checks only; note that the in-page smoke status box in Falkon reports `20/21` because pre-existing `SMK-N16-CHAINS-REVEAL` calls `dispatchEvent('click')` with a string in live DOM, whereas `SMK-N25-STORE-ROUNDTRIP` and all `21/21` vectors pass in Node VM).
