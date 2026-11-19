# N27 Verification Record — Offline Leitner Scheduler for Spaced Selection

**Date:** 2026-11-19  
**Task:** N27 (Phase VI, P2) — Implement the offline Leitner scheduler for spaced selection  
**Status:** PASS (Gate 23, runtime & fresh-process determinism harness, clock fixtures, box round trips, property + fresh-learner + N24 availability-exclusion fixtures, term-keyed Latvian render fixture, end-to-end N30 handoff + post-session recompute, double-build & two-invocation corpus parity, upstream N06/N21–N26/repo-local regressions, and Falkon render check pass)

---

## 1. Epistemic Scope, Predecessor Citation, and Honesty Copy (Verbatim)

- **Epistemic status:** `PROPOSED` training policy (`official_counterpart_status: "UNDETERMINED"`). The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) specifies seven topics, a written-on-paper exam, and a 180-minute ceiling; it specifies no spaced-repetition schedule, intervals, or queue order.
- **Predecessor approval cited:** `Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md §4.3` (*Leitner spaced repetition (approved direction): Implemented by N27 over the mastery state machine (N26)*), `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md#F08` (adaptive difficulty deferred until N26–N27 stabilize), and `docs/MASTERY_FORMAT.md#6`. Standard 3-box day-granular Leitner scheme; no third-party algorithm (Anki, SuperMemo, SM-2) copied.
- **Honesty note (`data/scheduler_policy.json#/honesty_note_lv`):**
  > PROPOSED mācību politikas priekšlikums: 2025. gada oficiālā programma (RSU_MedChem_Colloq1_Prog_LV_2025.pdf) nenosaka atkārtošanas intervālus vai prakses rindas kārtību (oficiāls analogs: UNDETERMINED). Leitnera rinda ir patstāvīgas mācīšanās palīgs, nevis oficiāla studiju vai eksāmena prasība.
- **Box intervals (`PROPOSED`):**
  - Box 1 (`early`): `interval_days: 1` → `unseen`, `learning`, `needs_review` (forced early)
  - Box 2 (`mid`): `interval_days: 3` → `near_mastered`
  - Box 3 (`late`): `interval_days: 7` → `mastered`
  - `queue_cap`: `5` (`PROPOSED`)
- **Term-keyed Latvian reason strings (`data/terms.json`, `N10` lint PASS):**
  - `scheduler.reason.overdue`: `"Nokavēts par {days} d. (kaste {box}, intervāls {interval} d.)"`
  - `scheduler.reason.due_today`: `"Atkārtojums pienācis šodien (kaste {box}, intervāls {interval} d.)"`
  - `scheduler.reason.new`: `"Jauns mērķis — vēl nav mēģināts (kaste {box})"`
  - `scheduler.reason.least_recently_practiced`: `"Agrāka atkārtošana — pēdējā prakse pirms {days} d. (kaste {box}, intervāls {interval} d.)"`
  - `scheduler.reason.unavailable`: `"Pagaidām nav pieejams praksei: nav treniņformai derīgu uzdevumu."`

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`data/scheduler_policy.json`](../data/scheduler_policy.json) | `#sim-scheduler-policy` island: 3 boxes (`1/3/7` days), `queue_cap: 5`, tier & `outcome_id` tie-break rules, term-keyed reasons | file `1f4bace5a705ca17...`, island `e97381ce5333d2e7...` (`5,161` canonical B) |
| [`data/terms.json`](../data/terms.json) | +16 `scheduler.*` interface/reason keys (`479` total entries, `248` checked keys) | `sha256: 2260bc4ade93ed48486dccfe45798a821b0c94ca06f99e7ad89666bb6cf8e647` |
| [`src/scheduler.ts`](../src/scheduler.ts) | Strict-TS day-clock contract, box mapper, N24/N26 availability consumer, pure queue selector, `#prakse` renderer, N30 handoff | `72,037` B, `sha256: 972e95c4d4b0c8566841ed71518daf515c4643dde74568e665771b14ec33b3f2` |
| [`src/compiled/scheduler.js`](../src/compiled/scheduler.js) | Compiled runtime (`root.SimScheduler`), inlined in `output/simulator.html` | `72,778` B raw, `50,950` B compacted, `sha256: d1f072d3db0d0c11d81a39b41d047b846e450be5aacee18f511f26c726607f48` |
| [`docs/SCHEDULER_FORMAT.md`](../docs/SCHEDULER_FORMAT.md) | Frozen box model, day-clock, selection, and N27 → N30 practice-entry handoff contract | `sha256: 7237117ff2f3dacb239f6babf417154a59890be3b59177b34ffe0ce8907f6bdf` |
| [`tools/validate_n27_scheduler.py`](../tools/validate_n27_scheduler.py) | Gate 23 (`scheduler`): strict monotonicity, non-increasing box-pair failures, N10 term lint, TS drift, shell & F10/wall-clock/network scans | `sha256: 2786cda731e69604339a769c73eaf96085cd603d9692e3c10b500e72c1bcd2f1` |
| [`tools/check_n27_runtime.js`](../tools/check_n27_runtime.js) | Runtime, `--determinism-only`, week-apart clock, box round trip, property set, N24 exclusion, render fixture, E2E handoff, built smoke | `sha256: ae457f57282699e6b575ece87f059d873377d6506198f87eb3273b8b39925b3b` |
| [`output/simulator.html`](../output/simulator.html) | Built single-file artifact (`23/23` gates PASS) with `#sim-scheduler-policy`, `#prakse-scheduler-panel`, and `SMK-N27-SCHEDULER-QUEUE` | `1,886,741` B (`1,842.5` KiB), `sha256: beee5d43114881fb7b561fcde0fab8b9c2f8a622d3348e7a4930fd4dd41ba190` |
| [`evidence/N27_RENDER_FIXTURE.json`](N27_RENDER_FIXTURE.json) | 5-item deterministic queue render fixture with term-keyed Latvian reasons (also serves as N32 visual test data) | `render_digest: 98aa29eab6ce15f4763cc6b8de22d1945dac52024255258028a12d91bd5aaad0` |
| [`evidence/N27_CORPUS_RECORD.json`](N27_CORPUS_RECORD.json) | Master corpus & two-invocation parity record (`9bb38a3d6ac70f4b...`) | `status: PASS`, `two_invocation_parity: PASS` |

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Box-Interval Validation & Non-Increasing Negative Fixtures (`evidence/N27_VALIDATION_RECORD.json`)
- **A.1.1 Policy validation:** Boxes `1` (`1d`, `early`), `2` (`3d`, `mid`), `3` (`7d`, `late`) are strictly increasing; all 5 N26 mastery states map to declared boxes (`needs_review` → box `1`); `queue_cap = 5` (`PROPOSED`); `terms_lint` PASS (`248` checked keys).
- **A.1.1 Negative fixtures:**
  - Equal interval (`box 1 = 1d`, `box 2 = 1d`) fails naming `box 1` and `box 2`.
  - Decreasing interval (`box 2 = 3d`, `box 3 = 2d`) fails naming `box 2` and `box 3` in both Python and JS `SimScheduler.validatePolicy`.
  - Missing `needs_review` mapping and `queue_cap = 0` both fail by name.

### AC2 — Day-Clock, Box Round Trip, Property Fixtures & Fresh Learner (`evidence/N27_RUNTIME_RECORD.json`)
- **A.1.2 Day-clock fixture:** Same mastery map under injected `'2026-11-10'` vs `'2026-11-17'` (7 days apart) produces different queues (`week1_overdue: ['P1-01']`, `week2_overdue: ['P1-01', 'P2-01', 'P4-01', 'P3-01']`); malformed `'2026-02-30'` throws `E_SCHEDULER_INVALID_DATE`.
- **A.1.3 Box round trip:** `unseen` → `learning` → `near_mastered` → `mastered` → `needs_review` → `learning` traces `[1, 1, 1, 2, 2, 3, 1, 1]` directly from `SimMastery` state truth.
- **B.1 / B.1.1 Property fixtures & fresh corner:**
  - Determinism across 2 in-process runs + fresh child `--determinism-only`: identical digest `ddce3db7639860785d585dc2120b642af03975c9450a4d5c6d5f3e758c54f45c`.
  - Cap: 15 overdue outcomes → exactly `5` queued.
  - Exclusion: maximally overdue unavailable `P1-01` excluded from `queue` and recorded in `excluded`.
  - Tie-break: 5 equal-overdue outcomes (`P6-03, P2-05, P1-09, P4-02, P3-01`) sort deterministically to `P1-09, P2-05, P3-01, P4-02, P6-03`.
  - Fresh learner: all-64-`unseen` yields `['P1-01', 'P1-02', 'P1-03', 'P1-04', 'P1-05']` (`overdue_days: 0`, `reason_code: 'new'`, `box: 1`).
  - Least-recently-practiced tier: all-practiced non-overdue map orders by oldest `last_practiced_day` (`P2-04, P3-03, P5-04, P7-01, P7-02`).
- **B.1.2 N24 family availability:** Unreviewed Topic 7 families (`FAM-7A..7D`) exclude `P7-01..P7-05` even when overdue and record them in `excluded[]` with `scheduler.reason.unavailable`.

### AC3 — End-to-End Practice Handoff, Post-Session Recompute, Term-Keyed Reasons & Smoke (`evidence/N27_RUNTIME_RECORD.json`, `evidence/N27_CORPUS_RECORD.json`)
- **B.1.3 Render fixture (`evidence/N27_RENDER_FIXTURE.json`):** 5-item queue (`overdue`, `overdue`, `due_today`, `new`, `new`) with `#sim-terms`-resolved Latvian reasons (`render_digest: 98aa29eab6ce15f4...`).
- **C.1 / C.1.1 E2E handoff & recompute:** Stored `SimStore` mastery map + `'2026-11-19'` yields `P1-05` first; clicking its `.scheduler-accept-btn` delivers `N27-to-N30-practice-entry` handoff (`filters.instance_ids: ['COL1-1-1B-A-01', ..., 'COL1-1-1B-D-01']`, `leaked_fields: []`); completing practice via `SimMastery.ingestGradedRecord` advances `P1-05` to `near_mastered` and re-computes the `#prakse` queue with `P2-01` moving to rank 1 and `P1-05` leaving the overdue queue.
- **C.1.2 / C.1.3 Smoke & parity:** `SMK-N27-SCHEDULER-QUEUE` (`['P4-01', 'P2-01', 'P3-01', 'P1-01', 'P1-02']`, `9e7c612f1783ddb3...`) and `23/23` smoke vectors pass in Node VM over `output/simulator.html`; double-build parity (`beee5d43114881fb...`) and two-invocation corpus parity (`9bb38a3d6ac70f4b...`) pass.

---

## 4. Byte Accounting and Falkon Render Check

- `output/simulator.html`: `1,886,741` B (`1,842.5` KiB; re-budgeted `1,780 → 1,848` KiB = `1,892,352` B; declared band `700–1,400` KiB remains visible).
- Inline `runtime_js_code`: `491,765` B (`480.2` KiB; re-budgeted `432 → 484` KiB = `495,616` B; declared band `120–220` KiB remains visible). `scheduler.js` compacted = `50,950` B, `SMK-N27-SCHEDULER-QUEUE` = `+2,625` B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- `css`: `51,952` B (`50.7` KiB); `bank_island`: `249,798` B (`243.9` KiB); `#sim-scheduler-policy`: `5,161` canonical B.
- Visual render check (`lite-shot -e falkon --cdp --theme light --anchor prakse-scheduler-panel`, inspected via `read_file`): [`evidence/N27_PAINT_PRAKSE.png`](N27_PAINT_PRAKSE.png) (`132,939` B, `overflow=false`) confirms `#prakse-scheduler-panel` renders the honesty note, status summary, 5 queued items with box badges, Latvian reasons, accept buttons, and per-topic scheduling chips cleanly with zero horizontal overflow (render check only, not screen-reader or instructor acceptance).
