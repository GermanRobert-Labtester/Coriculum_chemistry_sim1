# REVISION_FORMAT.md — N29 Unified Revision View & F07 Criterion Self-Assessment Contract

**Owner:** N29 · **Status:** frozen interface for N30, N31, N32, N33, N35, and N40  
**Module:** `src/revision.ts` → `src/compiled/revision.js` (`root.SimRevision`)  
**Island:** `#sim-revision-policy` (`data/revision_policy.json`) · **Gate:** `tools/validate_n29_revision.py` (Gate 25 `revision`)

> **Epistemic & evidence-separation boundary.** The 2025 RSU programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) defines no revision dashboard or criterion self-assessment rubric (`official_counterpart_status: "UNDETERMINED"`). Every rule here is **`PROPOSED` training policy**. F07 self-assessment ratings are explicitly labeled as the learner's own assessment, persist separately under `sim_colloq1_store_v2.self_assessments`, and **never** feed `SimMastery.reduce` or confer graded credit.

---

## 1. Unified Revision Panel (`#atskats-revision-panel`)

`SimRevision.buildRevisionViewModel(options)` / `SimRevision.renderRevisionPanel(doc, options)` combines data from strictly isolated upstream sources across all 7 topics and 64 outcomes (none dropped, none duplicated):

| Displayed Element | Exclusive Source | Never Merged With |
|---|---|---|
| Mastery state icon, label & last-practiced day | `N26:SimMastery` (`mastery.outcomes[oid]`) | F07 self-ratings |
| Practice availability & unavailable reason | `N24/N26:Eligibility` (`computeAvailability`) | Self-ratings or queue |
| Active remediation count | `N28:SimRemediation` (`getQueueSnapshot`, on-read validated) | Mastery transitions |
| Self-assessment summary & card state | `N29:F07` (`store.self_assessments[oid]`) | Mastery or auto points |
| Concept anchor, chain & practice affordances | `N02/N07/N16/N30:Affordances` (`#sim-coverage`, `ANCHOR_REGISTRY`, `#sim-chains`) | Unvalidated links |
| F07 criterion names | `N23/N10:CriteriaLabels` (`SimFeedback.criterionLabel` / `#sim-terms`) | Rubric keys/points |

- **On-read affordance validation:** Every `master_anchor` is verified against `ANCHOR_REGISTRY` / `CONCEPT_DRAWER_DATA`, and every `chain_ids` entry against `#sim-chains`. Dangling links fail loudly with `E_REVISION_DANGLING_ANCHOR` / `E_REVISION_DANGLING_LINK` naming the broken ID.
- **Corner case (self-assessed before practicing):** An outcome with `self_assessment.rated_count > 0` and `mastery.attempts === 0` renders `○ Nav mēģināts` (`unseen`) beside the separate F07 self-rating badge, never a merged state.

---

## 2. F07 Criterion Self-Assessment Card (`#atskats-sa-card`)

- **Single-sourced key-free criterion names:** `SimRevision.resolveOutcomeCriteria` collects the outcome's unique `criterion_id`s from bank rubrics and resolves each Latvian label through `SimFeedback.criterionLabel(criterionId, termsMap)` (`#sim-terms` key `feedback.criterion.<criterion_id>`). Points, `grading`, `engine_binding`, and answer keys are never returned.
- **Three-state rating control (accessible `<select>` pattern):**
  - `""` (`revision.rating.unrated` — *Nav novērtēts*)
  - `"confident"` (`revision.rating.confident` — *Protu droši*)
  - `"with_effort"` (`revision.rating.with_effort` — *Protu ar piepūli*)
  - `"not_yet"` (`revision.rating.not_yet` — *Vēl neprotu*)
  - Every `change` event updates `#atskats-sa-live` (`role="status"`, `aria-live="polite"`) in Latvian; full card completion works through the `<select>` API alone without pointer events.
- **Verbatim copy — self-assessment label:**
  > *Izglītojamā paša novērtējums (F07, PROPOSED) — šis nav automātiskais vērtējums un neietekmē apguves stāvokli.*
- **Optional free-text note (`note_max_length: 500`):** Stored verbatim in `self_assessments[outcome_id].note` with visible counter (`{count} no 500 rakstzīmēm`); notes `> 500` chars fail loudly (`E_REVISION_NOTE_TOO_LONG`). Verbatim policy copy:
  > *Brīvā teksta piezīme tiek saglabāta burtiski bez analīzes, atslēgvārdu meklēšanas vai automātiskas vērtēšanas.*

---

## 3. Handoffs to N30, N31, N32, N33, and N35

- **To N30 (`startPracticeFromOutcome`):** Emits `N27-to-N30-practice-entry` (`entry_source: 'revision_panel'`, `outcome_id`, `topic`, `mastery_state`, `filters: { topic, outcome_id, family_ids, instance_ids }`, zero key material); throws `E_REVISION_OUTCOME_UNAVAILABLE` when `eligible_count === 0`.
- **To N31 (build):** `src/compiled/revision.js` and `#sim-revision-policy` inline into `output/simulator.html` under interim ceilings; N31 owns the final inline/lazy-load/re-budget decision.
- **To N32 (visual test data):** `evidence/N29_PROFILE_FIXTURES.json` and `evidence/N29_FULL_REVISION_BASELINE.json`.
- **To N33 (screen-reader QA):** `<select>` label/role/live-region fixture in `evidence/N29_RUNTIME_RECORD.json`.
- **To N35 (privacy audit):** `self_assessment_fields` documented in `data/analytics_schema.json`; in-memory default, opt-in `sim_colloq1_store_v2` only, and two-step erase verified.
