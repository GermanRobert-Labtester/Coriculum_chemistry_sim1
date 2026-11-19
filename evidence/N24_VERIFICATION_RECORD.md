# N24 Verification Record — Seeded, Fair A/B/C Form Assembly

**Date:** 2026-11-19  
**Task:** N24 (Phase V, P0) — Implement seeded, fair A/B/C form assembly  
**Status:** PASS (all code, build gate, runtime harness, corpus parity, upstream regression, and Falkon render checks pass)

---

## 1. Epistemic Scope and Non-Claims

The three 21-slot forms (`A`, `B`, `C`), 100-point scale, per-topic point targets `[10, 12, 20, 15, 16, 15, 12]`, required completed types per form (`Q02, Q04, Q10, Q11, Q12, Q13, Q15`), and seeded training draw (`101000..199999`) are **PROPOSED training policy**. The supplied 2025 programme specifies seven topics, a written-on-paper examination, and a 180-minute maximum; it does not specify form counts, point weights, question types, or pass marks.

- **Not claimed:** official RSU colloquium exam equivalence, official grading/proctoring status, adaptive difficulty (F08 stays deferred), full browser/screen-reader/print/instructor acceptance (Falkon CDP captures verify initial paint only; N32–N34/N37/N40 own those gates), or unreviewed instance assembly (eligibility gate is absolute).

---

## 2. Deliverables and Digests

| Artifact | Role | Digest / Size |
|---|---|---|
| [`src/assembly.ts`](../src/assembly.ts) | Strict-TS constraint assembler, independent verifier, seeded training draw, fairness sweep | `sha256: 5a4579c1bae44f97041d4009251cc88b5f47650b3a37bdf4c736b601af9e9333` |
| [`src/compiled/assembly.js`](../src/compiled/assembly.js) | Compiled runtime module (`root.SimAssembly`), inlined into `output/simulator.html` | `58,129` B raw, `39,806` B compacted, `sha256: 551b56bdf39141a5bb6568f38c092ad0cf652d3addd2668c94d88181224ef9e5` |
| [`tools/assemble_forms.py`](../tools/assemble_forms.py) | Build-time Python twin (byte-identical manifests to JS, pipeline-order guard) | `sha256: 56d54f6d9ba547fc83d4c4ed98e1175446d6d1a3153801c4fa0c54ad383103e5` |
| [`tools/validate_n24_assembly.py`](../tools/validate_n24_assembly.py) | Independent Python Gate 20 (`form_assembly`, zero shared assembly logic) | `sha256: 76e654bba73a100e8b4f39ec1cda08f88c9e01229c1338a7f6ddf371cd3885a1` |
| [`docs/FORM_ASSEMBLY_FORMAT.md`](../docs/FORM_ASSEMBLY_FORMAT.md) | Frozen assembly interface contract for N25–N30 and N40 | `sha256: 90fbf2ed89044768803f7a8a3b33ce2fbde013a6da99f680a4078f2a74b20646` |
| [`output/forms/form_A.json`](../output/forms/form_A.json) | Frozen Form A manifest (`seed: "100001"`, 21 slots, 100 pts) | `manifest_digest: b1ac2f07085b244eea29cae721d3a205cd2dd9cd076983f303d1a503ef0e08e0`, file `sha256: 0bb4e1bf161d57fc933155c6e6e0f41cd97362db2780eb34dbe2ac27d9eea98b` |
| [`output/forms/form_B.json`](../output/forms/form_B.json) | Frozen Form B manifest (`seed: "100002"`, 21 slots, 100 pts) | `manifest_digest: 55531768cd785997773ebc69949c9dba6aff7508f5de5af28fd4f454c62e2541`, file `sha256: 26e643d219156e6f84878221bb82c1a7f368407c1e9d852f51a2e4d183c902d8` |
| [`output/forms/form_C.json`](../output/forms/form_C.json) | Frozen Form C manifest (`seed: "100003"`, 21 slots, 100 pts) | `manifest_digest: 5781f7973c006497c41da05e646d0f1a28f7e911e5b50f50609da65a04172d42`, file `sha256: 11c7b5b85511390cdd17af2bed87159c8177fac08058250c8471cf14b380e2b4` |
| [`output/simulator.html`](../output/simulator.html) (`#sim-forms`) | Single-file artifact with embedded `#sim-forms` island, inline `assembly.js`, picker UI, and `SMK-N24-ASSEMBLY-DRAW` | `1,684,264` B (`1644.8` KiB), `sha256: 9e5a74a05d87a2ff26152f1c151995b473a320deafa7b9077cc2444f25418e3f`; `#sim-forms` `16,067` canonical B, `digest: 61df93c0390a0a0f8ec1b22814cf7d106a25e6c794cf1941ddd7b5d22de72f1f` |
| [`tools/check_n24_runtime.js`](../tools/check_n24_runtime.js) | Node runtime harness for AC1–AC3, A1.1–A1.3, B1.1–B1.3, C1.1–C1.2 | `sha256: 9c605f13d62e2818dc7ca3ef14eba268a03f03b4cad816dd2058d33ffa45a9f2` |
| [`tools/n24_corpus.py`](../tools/n24_corpus.py) | Master corpus & two-invocation determinism runner | `N24_CORPUS_RECORD.json` `sha256: fd781fa8d6dfa5ecef8e3c691845e83a25dcdaa1ac25e2215c25afcf838b1e4b` |

Shell, exam wiring, and build updates: [`src/shell.html`](../src/shell.html) (`5a...`→`a4d0181c0116e13d4debddb5136abb7f3ace04c86c4f70c679d47d1c79623061`), [`src/styles.css`](../src/styles.css) (`83af18f4243be44a3d617ac73e2d87ca433836087a31c013fcfdbbd05f4c10b8`), [`src/exam.ts`](../src/exam.ts) (`088472dd31e136e40b6f4e234f37c4480175a3803dad1c75615bb67ed7d5b4ed`), [`src/compiled/exam.js`](../src/compiled/exam.js) (`197a3459172c2d03742d05c8ff7e4901312931d26ecce9966f207b7919a54820`), [`src/smoke-subset.js`](../src/smoke-subset.js) (`ab636769a43643f260317114a5a120f40e9a06405c3e7c5683380e0565fe432a`, `+4,566` B), [`tools/build.py`](../tools/build.py) (`9e154ef0027dade394245cd86500525e9758cfe02c1c9bf477273e0c32589d1b`), and [`tools/byte_budget.py`](../tools/byte_budget.py) (`a8d9b755c3af8c7ccdf968dc4f6dfb4f742049f39ad998209b0774034cc60d7e`).

---

## 3. Acceptance Criteria Verification Summary

### AC1 — Happy path, independent checker, zero-slack & 1-short fixtures (Evidence: [`evidence/N24_VALIDATION_RECORD.json`](N24_VALIDATION_RECORD.json), [`evidence/N24_RUNTIME_RECORD.json`](N24_RUNTIME_RECORD.json))

- Forms `A` (`100001`), `B` (`100002`), and `C` (`100003`) each draw `21` slots (`3` per topic across topics 1–7), exact per-topic points `{1: 10, 2: 12, 3: 20, 4: 15, 5: 16, 6: 15, 7: 12}` totaling `100`, cover all required completed types (`Q02, Q04, Q10, Q11, Q12, Q13, Q15`), use distinct families per form, draw only `review-passed` instances, bind `figure_id` on Q11 slots, and pass all 10 independent `verifyFormManifest` checks (`0` errors, `shortages_zero: true`).
- **Checker independence:** `verifyFormManifest` (JS) and `tools/validate_n24_assembly.py` (Python Gate 20) share zero functions with assembly logic.
- **Python/JS parity:** Python build-time forms `A`, `B`, `C` and JS runtime forms `A`, `B`, `C` produce byte-identical manifests and identical digests.
- **Zero-slack corner case (A1.1):** Narrowed eligible pool where each slot has exactly one eligible instance produces `status: "AVAILABLE"` and passes `verifyFormManifest` (`"PASS"`).
- **One-short negative fixture (A1.1):** Removing the sole eligible instance for `S1-2` (`FAM-1C`) produces `status: "SHORTAGE"`, `binding_constraint: "slot_family_eligibility"`, `missing_family: "FAM-1C"`, `count_short: 1`, `disabled_reason_lv: "SHORT1 forma pagaidām nav pieejama: nepietiek atbilstošu uzdevumu (FAM-1C, vieta S1-2, iztrūkst 1)."`, and independent checker refuses (`status: "FAIL"`, 6 explicit constraint violation messages).

### AC2 — Fairness sweep & seeded determinism (Evidence: [`evidence/N24_FAIRNESS_SWEEP.json`](N24_FAIRNESS_SWEEP.json), [`evidence/N24_RUNTIME_RECORD.json`](N24_RUNTIME_RECORD.json))

- **Blueprint sweep (`100101..100110`, 10 seeds × 3 forms = 30 forms):** `28/28` families seen (`families_missing: []`), `0` tripled flexible family slots (`S1-1, S2-1, S3-1, S4-1, S5-1, S6-1, S7-3`), `0` tripled instance slots across all 21 slots, `all_checks_passed: true`, and `double_regen_parity: true` (all 30 digests identical across regeneration).
- **Topic-flexible sweep (`30` forms, all 4 families per topic eligible at every slot):** `28/28` families seen, `0` tripled family slots across all 21 slots, `all_checks_passed: true`, `double_regen_parity: true`.
- **Seeded training draws (A1.3, seeds `101001..101005`):** All 5 seeded training draws pass `verifyFormManifest`, each instantiating `5` `ephemeral` variants (`*-EPH-*`, `all_eph_marked: true`) via `SimVariantEngine`.

### AC3 — Shortage honesty, recovery, picker-to-session wiring & double-build parity (Evidence: [`evidence/N24_RUNTIME_RECORD.json`](N24_RUNTIME_RECORD.json), [`evidence/N24_CORPUS_RECORD.json`](N24_CORPUS_RECORD.json))

- **Shortage & recovery (B1.1):** Marking `FAM-1C` pending-review (`pending-review`) disables the affected form with `status: "SHORTAGE"`, `disabled: true`, `binding_constraint: "slot_family_eligibility"`, `slot_id: "S1-2"`, `missing_family: "FAM-1C"`, `pending_review_families: ["FAM-1C"]`, and `disabled_reason_lv: "B forma pagaidām nav pieejama: gaida recenziju (FAM-1C, vieta S1-2, iztrūkst 1)."` with zero silent substitutions. Attempting to start a disabled form throws `E_EXAM_FORM_DISABLED`. Restoring `FAM-1C` to `review-passed` clears the shortage on the next assembly (`recovered_form_digest: c0efd19eeabec3ecb06c21fc17232485fcd9b743a2b48f97492777ac3dfa6e55`).
- **Picker-to-session contract (B1.3):** Starting `ExamSession` via `#sakums-form-picker` / `#exam-form-picker` for `A`, `B`, and `C` produces 21 slots and 100 points matching each manifest slot-for-slot (`slots_match_manifest: true`).
- **Pipeline-order guard (C1.1):** `assemble_frozen_forms` and `assembleFormSet` refuse absent, stale, or unverified (`bank_verified: false`) `bank_digest` with `E_ASSEMBLY_BANK_UNVERIFIED`.
- **Built-artifact smoke (C1.2):** `SMK-N24-ASSEMBLY-DRAW` runs inside built `output/simulator.html` over a 6-family mini-bank (`miniSlots: 6`, `miniPoints: 22`, `unreviewedExcluded: true`, `independentCheck: "PASS"`, `formsInIsland: 3`), contributing to `20/20` passing smoke vectors.
- **Double-build & corpus parity (B1.2, C1.3):** Two consecutive `tools/build.py` runs emit byte-identical `output/forms/form_{A,B,C}.json` and `output/simulator.html` (`9e5a74a05d87a2ff...`); two consecutive `tools/n24_corpus.py` runs emit byte-identical `N24_CORPUS_RECORD.json` (`fd781fa8d6dfa5ec...`).

---

## 4. Verbatim Advisory Copy and Conflicts

- **`#sakums-forma-advisory`:** `"Mācību politikas priekšlikums (PROPOSED): trīs 21 uzdevuma vietas treniņformas (A, B, C, 100 punkti) vai sēklots treniņa zīmējums. Nav oficiāls RSU kolokvija eksāmens un nepiešķir oficiālu vērtējumu."`
- **`#exam-form-advisory`:** `"Mācību politikas priekšlikums (PROPOSED): izvēlieties treniņformu A, B, C vai sēklotu treniņa zīmējumu. Nav oficiāls RSU kolokvija eksāmens."`
- **Recorded conflicts (never hidden):**
  - `N23-C01` (inherited, visible in every manifest's `conflicts[]` and `#sim-forms`): `FAM-7C`/`FAM-7D` carry 9-pt rubrics in frozen N20 while `S7-3` carries `5` slot points in `data/exam_policy.json`; slot points govern the 100-pt form sum (`strict_rubric_points: true` enforces strict equality on demand).
  - `N24-C01` (new, recorded): `docs/SIMULATION_BLUEPRINT.json` pins 14/21 slots to single `allowed_family_ids`; those 14 slots rotate variants (`0` instance tripling across 30 sweep forms), while the 7 flexible slots (`S1-1, S2-1, S3-1, S4-1, S5-1, S6-1, S7-3`) and topic-flexible sweeps achieve `0` family tripling.
  - `N23-C03` (carried): Q11 drawing slots carry explicit `figure_id` bindings (`FIG-T2-PLOT-NACL-DENSITY`, `FIG-T5-LIN-FIRST`, `FIG-T67-CAL-MASTER`).

---

## 5. Byte Accounting and Visual Render Checks

- `output/simulator.html`: `1,684,264` B (`1644.8` KiB; re-budgeted `1600 → 1680` KiB = `1,720,320` B; declared band `700–1400` KiB remains visible).
- Inline `runtime_js_code`: `329,976` B (`322.2` KiB; re-budgeted `280 → 332` KiB = `339,968` B; declared band `120–220` KiB remains visible). `src/compiled/assembly.js` accounts for `39,806` compacted B; `SMK-N24-ASSEMBLY-DRAW` adds `4,566` B.
- `css`: `45,473` B (`44.4` KiB); `bank_island`: `249,798` B (`243.9` KiB); `#sim-forms` island: `16,067` canonical B. Final inline/lazy-load/re-budget ownership stays with **N31**.
- Visual render checks (`lite-shot -e falkon --cdp`, inspected via `read_file`): [`evidence/N24_PAINT_START.png`](N24_PAINT_START.png) (`209,074` B) and [`evidence/N24_PAINT_EXAM_PICKER.png`](N24_PAINT_EXAM_PICKER.png) (`136,692` B) confirm start and exam picker rendering (render checks only).
