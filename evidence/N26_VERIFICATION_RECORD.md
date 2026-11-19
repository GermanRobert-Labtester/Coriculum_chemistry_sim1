# N26 Verification Record — Mastery State Machine over Outcomes

**Date:** 2026-11-19  
**Task:** N26 (Phase VI, P1) — Implement the mastery state machine over outcomes  
**Status:** PASS (Gate 22, runtime & fresh-process replay harness, 3-profile + unavailable view fixtures, end-to-end `FX-N23-MIXED` integration, double-build & two-invocation corpus parity, upstream N06/N21–N25/repo-local regressions, and Falkon render checks pass)

---

## 1. Epistemic Scope, Policy Honesty Note, and Labeling Copy (Verbatim)

- **Epistemic status:** `PROPOSED` training policy (`official_counterpart_status: "UNDETERMINED"`). The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) specifies seven topics, a written-on-paper exam, and a 180-minute ceiling; it specifies no mastery thresholds or competency standard.
- **Honesty note (`data/mastery_policy.json#/honesty_note_lv`):**
  > PROPOSED mācību politikas priekšlikums: 2025. gada oficiālā programma (RSU_MedChem_Colloq1_Prog_LV_2025.pdf) nenosaka apguves sliekšņus vai kompetences slēdzienus (oficiāls analogs: UNDETERMINED). Šie stāvokļi atspoguļo tikai patstāvīgās mācīšanās progresu no automātiski vērtētajiem kritērijiem un nav oficiāls RSU kolokvija vērtējums.
- **View labeling copy (`data/mastery_policy.json`):**
  - `unseen`: icon `○`, `Nav mēģināts`
  - `learning`: icon `◔`, `Apgūšanas procesā`
  - `near_mastered`: icon `◑`, `Gandrīz apgūts`
  - `mastered`: icon `●`, `Apgūts (pašmācībā)`
  - `needs_review`: icon `↻`, `Jāatkārto`
  - `unavailable` (rendering status when `eligible_count === 0`): icon `⊘`, `Pagaidām nav pieejams` — reason: `Pagaidām nav pieejams praksei: mērķa uzdevumi gaida recenziju (0 derīgu treniņformai).` / `Pagaidām nav pieejams praksei: šim mācību mērķim pašlaik nav treniņformai derīgu uzdevumu.`
  - `atskats_honesty_note`: `Pašmācības apguves stāvokļi (PROPOSED mācību politika; oficiāls programmas analogs: UNDETERMINED). Atvasināts tikai no automātiski vērtētajiem kritērijiem — tas ir patstāvīgas mācīšanās progress, nevis oficiāls RSU kolokvija vērtējums.`
  - `prakse_honesty_note`: `Apguves indikatori parāda patstāvīgās mācīšanās stāvokli pa tēmām un mērķiem (PROPOSED), lai palīdzētu izvēlēties, ko atkārtot nākamo. Tie nav oficiāli RSU vērtējumi.`
  - `fresh_learner_note_lv`: `Godīgs sākuma stāvoklis: visi 64 mācību mērķi pašlaik ir stāvoklī 'Nav mēģināts' (nav pieņemtu kļūdu).`

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`data/mastery_policy.json`](../data/mastery_policy.json) | `#sim-mastery-policy` island: 5 states, `PROPOSED` thresholds (`2/2/1/14d/1`), predecessor T/F-card citations, verbatim copy | file `cf102dce5dca701b...`, island `b1b5dab8a6b7335d...` (`10,378` canonical B) |
| [`src/mastery.ts`](../src/mastery.ts) | Strict-TS pure reducer, criterion-to-outcome resolver, store reader/writer, availability checker, `#atskats` & `#prakse` renderers | `sha256: 96a2c2bd08ca7b76193e3fee49791b295be990806d9eb4d2dca940d56d491484` |
| [`src/compiled/mastery.js`](../src/compiled/mastery.js) | Compiled runtime (`root.SimMastery`), inlined in `output/simulator.html` | `59,476` B raw, `43,200` B compacted, `sha256: 256207ee68c9be9de902ca91258c325d2a111a5e385e1652cbc2c6f5cd9136a1` |
| [`docs/MASTERY_FORMAT.md`](../docs/MASTERY_FORMAT.md) | Frozen state-map, event, store-migration, availability, and N27–N29 handoff contract | `sha256: 27b475455ac0c760229e0b66ed8fc00ececfd151e81cf58eb04a60bad29f76ba` |
| [`tools/validate_n26_mastery.py`](../tools/validate_n26_mastery.py) | Gate 22 (`mastery`): policy reachability, unreachable-state negative fixtures, 28-family criterion totality, TS drift, shell & lint scans | `sha256: 89dabb240181be4ece681eb0ba23292c0250ab1ea10bc6830cad21a415fe0b03` |
| [`tools/check_n26_runtime.js`](../tools/check_n26_runtime.js) | Runtime, fresh-process `--replay-only`, interleaved independence, migration/round-trip/erase, 3-profile & `FX-N23-MIXED` harness | `sha256: 98eea121590e74e98c4f10ad84b5fafcae8b6107998f55c7c3b334a8734001fd` |
| [`output/simulator.html`](../output/simulator.html) | Built single-file artifact (`22/22` gates PASS) with `#sim-mastery-policy`, `#atskats`/`#prakse` mastery UI, and `SMK-N26-MASTERY-WALK` | `1,817,433` B (`1,774.8` KiB), `sha256: 5aed45aed181f73c97f1aeebe8ddf6eeea0aa5d5c0f19509d8f10a9d41825071` |
| [`evidence/N26_VIEW_FIXTURES.json`](N26_VIEW_FIXTURES.json) | 3-profile (`fresh`, `mid_progress`, `near_complete`) + Topic-7 unavailable corner fixtures for N32 visual QA | `status: authored/generated` |
| [`evidence/N26_CORPUS_RECORD.json`](N26_CORPUS_RECORD.json) | Master corpus & two-invocation parity record (`b2d06b261cd9f220...`) | `status: PASS`, `two_invocation_parity: PASS` |

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Policy Validation & Unreachable-State Fixtures (`evidence/N26_VALIDATION_RECORD.json`)
- **A.1.1 Transition policy:** All 5 states (`unseen`, `learning`, `near_mastered`, `mastered`, `needs_review`) carry entry rules, exit paths, regression rules, distinct icons, and Latvian labels; all 5 thresholds (`2`, `2`, `1`, `14`, `1`) are positive integers labeled `PROPOSED` with `official_counterpart_status: "UNDETERMINED"`, citing `T02`, `T04`, `T17`, `F01`, `F07`, `F08`, `F10`.
- **A.1 Negative fixtures:**
  - Extra unreachable state `stranded_vault` fails validation naming `stranded_vault` (`Unreachable mastery states detected: stranded_vault`).
  - Cut incoming edge to `needs_review` fails validation naming `needs_review` (`Unreachable mastery states detected: needs_review`).
  - Zero threshold fails validation naming `learning_to_near_mastered_streak`.
- **A.1.2 Per-criterion mapping totality:** `28/28` families, `112/112` bank instances, `267/267` rubric criteria resolve to valid `#sim-coverage` outcome IDs (`0` unmapped, `0` unknown); negative unmapped scratch criterion throws `E_MASTERY_UNMAPPED_CRITERION`.

### AC2 — Pure Reducer, Determinism & Fresh-Process Replay (`evidence/N26_RUNTIME_RECORD.json`)
- **A.1.3 Scripted walk:** `unseen` → (`incorrect`) `learning` → (`correct`) `learning` → (`correct`) `near_mastered` → (`correct`) `near_mastered` → (`correct`) `mastered` → (`decay(14d)`) `needs_review`. Double-run digests match identically: `a4f28bad132f5fa1c0bee13c5569c3bc7bf1f748bce0ae1ed8331f5ebf0cb83b`. Recovery (`needs_review` → `near_mastered`), regression (`near_mastered` → `learning`), miss-from-mastered (`mastered` → `needs_review`), and partial-task split (`P3-01` `awarded` → `learning` streak 1; `P3-02` `denied` → `learning` streak 0; `P3-03` `pending` → `unseen`) all pass.
- **C.1.1 Fresh-process replay & interleaved independence:** Child `node tools/check_n26_runtime.js --replay-only` yields identical digest `a4f28bad132f5fa1c0bee13c5569c3bc7bf1f748bce0ae1ed8331f5ebf0cb83b`. Interleaving `P1-01` and `P4-02` events produces byte-identical per-outcome states (`P1-01: mastered`, `P4-02: near_mastered`) to reducing each independently.

### AC3 — Store Persistence, View Honesty, E2E Integration & Smoke (`evidence/N26_RUNTIME_RECORD.json`, `evidence/N26_CORPUS_RECORD.json`)
- **B.1.1 Store migration, round-trip & erase:** Scratch pre-mastery `v2` store loads all 64 outcomes as `unseen`; `schema_version: 99` store remains `NEWER_VERSION_IGNORED` / `E_STORE_WRITE_BLOCKED_NEWER_VERSION`; opted-in round-trip preserves identical store digest (`e2e` / `roundtrip_mastery_digest: a4f28bad132f5fa1...`) across VM reload; two-step erase leaves `0` `localStorage` keys and all-`unseen`.
- **B.1.2 View renderers & unavailable corner case:** `fresh`, `mid_progress`, and `near_complete` render models recorded in `evidence/N26_VIEW_FIXTURES.json`; Topic 7 pending-review scratch bank (`0` eligible instances for `P7-01..P7-05`) renders `"Pagaidām nav pieejams"` (`unavailable`, icon `⊘`) with honest reason instead of unseen-but-practicable; `>= 128` icon+text pairs rendered; zero certification/endorsement claims.
- **B.1.3 End-to-end `FX-N23-MIXED` chain:** Graded record flows through `SimAnalytics.ingestGradedRecord` → `SimMastery.applyGradedRecordDraft` → `SimStore` → `#atskats` + `#prakse` re-render, matching hand-computed expectation digest `b48d52188aa4845681a2c51e6626ceb1256a4b9940e03e5bb5a5ee26ba48cd25` (`P1-05`/`P5-05` `near_mastered`, `P2-01` `learning` streak 1, `P6-01`/`P4-02` `learning` streak 0, self-only `P1-02` & pending-only `P1-08` `unseen`).
- **C.1.2 / C.1.3 Built-artifact smoke & parity:** `SMK-N26-MASTERY-WALK` (`unseen>learning>near_mastered>learning`, digest `8c93721f05567444...`) and `22/22` smoke vectors pass in Node VM over `output/simulator.html`; double-build parity (`5aed45aed181f73c...`) and two-invocation corpus parity (`b2d06b261cd9f220...`) pass.

---

## 4. Byte Accounting and Falkon Render Checks

- `output/simulator.html`: `1,817,433` B (`1,774.8` KiB; re-budgeted `1,720 → 1,780` KiB = `1,822,720` B; declared band `700–1,400` KiB remains visible).
- Inline `runtime_js_code`: `437,232` B (`427.0` KiB; re-budgeted `388 → 432` KiB = `442,368` B; declared band `120–220` KiB remains visible). `mastery.js` compacted = `43,200` B, `SMK-N26-MASTERY-WALK` = `+2,391` B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- `css`: `49,258` B (`48.1` KiB); `bank_island`: `249,798` B (`243.9` KiB); `#sim-mastery-policy`: `10,378` canonical B.
- Visual render checks (`lite-shot -e falkon --cdp --theme light`, inspected via `read_file`): [`evidence/N26_PAINT_ATSKATS.png`](N26_PAINT_ATSKATS.png) (`159,233` B, `overflow=false`) and [`evidence/N26_PAINT_PRAKSE.png`](N26_PAINT_PRAKSE.png) (`221,702` B, `overflow=false`) confirm `#atskats` per-topic summaries and `#prakse` 7-topic mastery cards render cleanly with icon + Latvian text badges and zero horizontal overflow (render checks only, not screen-reader or instructor acceptance).
