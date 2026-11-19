# FORM_ASSEMBLY_FORMAT.md — N24 Seeded, Fair A/B/C Form Assembly Contract

**Owner:** N24 · **Status:** frozen interface for N25–N30 and N40  
**Module:** `src/assembly.ts` → `src/compiled/assembly.js` (`root.SimAssembly`)  
**Build twin:** `tools/assemble_forms.py` · **Gate:** `tools/validate_n24_assembly.py` (Gate 20 `form_assembly`)  
**Island:** `#sim-forms` · **Frozen manifests:** `output/forms/form_A.json`, `output/forms/form_B.json`, `output/forms/form_C.json`

> **Epistemic note.** The 2025 programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) fixes seven
> topics, a written-on-paper examination, and a 180-minute maximum. The three forms (`A`, `B`, `C`),
> 21 slots per form, per-topic point weights (`10/12/20/15/16/15/12 = 100`), required types, and
> family structure are **PROPOSED training policy** (`docs/SIMULATION_BLUEPRINT.json` and
> `data/exam_policy.json`). Nothing here is an official RSU examination, grade, or proctoring claim.

---

## 1. Constraints

Every assembled form manifest (`A`, `B`, `C`, or `SEEDED`) satisfies all of the following invariants,
independently verified by `SimAssembly.verifyFormManifest` (JS) and
`validate_n24_assembly.verify_form_manifest_independent` (Python), sharing **zero** code with the
assembly algorithm:

1. **Slot count & order:** Exactly `21` slots matching `data/exam_policy.json#/slots` (`S1-1` through `S7-3`).
2. **Per-topic counts & points:** Exactly `3` slots per topic (`1..7`), totaling `10, 12, 20, 15, 16, 15, 12` = **100** training points.
3. **Family uniqueness:** At most one instance of any family (`FAM-1A`..`FAM-7D`) per form (21 distinct families per form).
4. **Instance uniqueness:** 21 distinct `question_id` values per form.
5. **Completed-type coverage:** Every form includes at least one instance covering each required type:
   `Q02`, `Q04`, `Q10`, `Q11`, `Q12`, `Q13`, `Q15`.
6. **Review-state eligibility (absolute gate):** Only instances with all four `review` checks (`accessibility`, `calculation`, `content`, `source`) equal to `"passed"` and (when present) `review_workflow.state === "accepted"` are eligible. Unreviewed or pending instances are never drawn.
7. **Q11 figure binding (`N23-C03`):** Every `Q11` drawing slot carries an explicit `figure_id` (`FIG-T2-PLOT-NACL-DENSITY`, `FIG-T5-LIN-FIRST`, or `FIG-T67-CAL-MASTER`).
8. **Ephemeral exclusion in exam forms:** Frozen forms (`A`, `B`, `C`) strictly forbid ephemeral variants (`ephemeral: false`). Only the seeded training option (`SEEDED`, seeds `101000..199999`) allows ephemeral variants from `SimVariantEngine.instantiateEphemeral`, and every ephemeral instance is explicitly marked `ephemeral: true` with `question_id` ending in `-EPH-{attempt}`.

---

## 2. Seed Policy & Fairness

All draws use the frozen N05 PRNG `splitmix64-u64-v1` (`tools/prng.py` / `src/prng.js`) with seeds in
the `N24_assembly` vocabulary (`data/seed_policy.json`):

| Assignment | Seed(s) | Recording rule |
|---|---|---|
| `form_A` | `"100001"` | Recorded as decimal string in `form_seed` + `policy_id` + `prng_contract_digest` |
| `form_B` | `"100002"` | Recorded as decimal string in `form_seed` + `policy_id` + `prng_contract_digest` |
| `form_C` | `"100003"` | Recorded as decimal string in `form_seed` + `policy_id` + `prng_contract_digest` |
| `fairness_sweep` | `"100101"`..`"100110"` | 10 consecutive triplets (30 forms); Python & JS bit-identical |
| `seeded_training` | `"101000"`..`"199999"` | Runtime practice draw; ephemeral variants allowed & marked |

**Build-time freeze vs runtime draw:** Forms `A`, `B`, and `C` are assembled at **build time** from
the verified frozen bank (`tools/build.py` pipeline order: bank verified first → assembly → `#sim-forms`
island & `output/forms/form_{A,B,C}.json`) so shipped forms are byte-stable artifacts rather than
per-load draws. The runtime assembly path in `SimAssembly` exists only for the learner's **seeded
training option** (`SEEDED`) and in-file self-test (`SMK-N24-ASSEMBLY-DRAW`).

---

## 3. Shortage Policy & Disabled-Form Contract

If the eligible bank cannot satisfy any constraint (for example, a family's reviews are pending):

- Assembly **never** relaxes constraints and **never** substitutes an unreviewed instance.
- Assembly emits a `ShortageReport` (`status: "SHORTAGE"`, `disabled: true`) naming:
  - `binding_constraint` (`"slot_family_eligibility" | "required_type_coverage" | "topic_slot_count"`),
  - `topic`, `slot_id`, `missing_family`, `missing_type`, `required_count`, `available_count`, `count_short`,
  - `pending_review_families`, and `disabled_reason_lv` (e.g. `"B forma pagaidām nav pieejama: gaida recenziju (...)."`).
- The start screen (`#sakums-form-picker`) and exam entry gate (`#exam-form-picker`) disable the
  affected form button (`disabled = true`, `aria-disabled="true"`, `aria-describedby` pointing to the
  reason), refuse session start (`E_EXAM_FORM_DISABLED`), and re-enable automatically when the
  underlying bank review state recovers to `"accepted"`.
- Pipeline-order assertion: assembly fails loudly with `E_ASSEMBLY_BANK_UNVERIFIED` if `bank_digest`
  is absent, stale, or the bank has not passed review/schema gates.

---

## 4. Recorded Source Conflicts

- **`N23-C01` (inherited, visible):** `FAM-7C` and `FAM-7D` carry 9-point rubrics in the frozen N20
  bank while `S7-3` declares 5 slot points in `data/exam_policy.json`. Assembly seats `FAM-7C`/`FAM-7D`
  under the authoritative 5-point slot scale (totaling 100) and records `N23-C01` visibly in every
  manifest's `conflicts[]` and in `#sim-forms` (never rescaling or hiding the mismatch). When
  `strict_rubric_points: true` is requested, assembly enforces exact rubric equality.
- **`N24-C01` (blueprint singleton slots):** `docs/SIMULATION_BLUEPRINT.json` pins 14 of 21 slots to a
  single allowed family (`allowed_family_ids` length 1). At those 14 slots, forms `A`/`B`/`C` rotate
  distinct **instances/variants** (zero instance tripling); at all 7 flexible slots (`allowed_family_ids`
  length 2), zero families triple at the same slot across `A`/`B`/`C`.

---

## 5. Downstream Interfaces

- **N21 (`SimExam` / `SimSession`):** Consumes `FormManifest` (`form_id`, `slots[{slot_id, topic, points, instance_id, family_id, type_id, figure_id, ephemeral}]`, `manifest_digest`).
- **N23 (`SimGrading`) & N25 (`analytics`):** Consume `slots` bindings (`slot_id`, `type_id`, `instance_id`, `figure_id?`) and `manifest_digest`.
- **N30 (bounded practice):** Reuses `ShortageReport` / `disabled_reason_lv` and `assembleSeededTrainingForm`.
- **N40 (release gate):** Consumes Gate 20 (`form_assembly`) and `shortages[]` as a blocking or degraded-mode decision.
