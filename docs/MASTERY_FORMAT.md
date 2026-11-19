# MASTERY_FORMAT.md — N26 Mastery State Machine & Handoff Contract

**Owner:** N26 · **Status:** frozen interface for N27, N28, N29, N31, N32, and N35  
**Module:** `src/mastery.ts` → `src/compiled/mastery.js` (`root.SimMastery`)  
**Island:** `#sim-mastery-policy` (`data/mastery_policy.json`) · **Gate:** `tools/validate_n26_mastery.py` (Gate 22 `mastery`)

> **Epistemic boundary.** The 2025 RSU programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) defines seven topics, a written-on-paper exam, and a 180-minute ceiling; it defines **no** mastery thresholds or competency standard (`official_counterpart_status: "UNDETERMINED"`). Every threshold and state transition below is **PROPOSED** training policy representing self-study progress only — never official certification, accreditation, or examination grading.

---

## 1. State Enum & Transition Policy (`PROPOSED`)

`SimMastery.STATES`:

| State ID | Icon | Latvian Label | Entry Rule | Exit / Advance | Regression / Decay |
|---|---|---|---|---|---|
| `unseen` | `○` | `Nav mēģināts` | Initial state (0 attempts; absent `mastery` key; after erase) | First graded attempt (any verdict) → `learning` (`consecutive_correct = 1` if `correct`, `0` if `incorrect`) | Floor state (stays `unseen`) |
| `learning` | `◔` | `Apgūšanas procesā` | From `unseen` on 1st attempt; from `near_mastered` or `needs_review` on `incorrect` | `2` consecutive `correct` (`learning_to_near_mastered_streak`, `PROPOSED`) → `near_mastered` | `incorrect` → `learning` (`consecutive_correct = 0`) |
| `near_mastered` | `◑` | `Gandrīz apgūts` | From `learning` (`2` consecutive `correct`) or `needs_review` (`1` `correct`) | `2` further consecutive `correct` (`near_mastered_to_mastered_streak`, `PROPOSED`) → `mastered` | `incorrect` → `learning` (`consecutive_correct = 0`) |
| `mastered` | `●` | `Apgūts (pašmācībā)` | From `near_mastered` (`2` consecutive `correct`) | `decay` (`days_inactive >= 14`, `PROPOSED`) → `needs_review` | `incorrect` (`miss_in_mastered >= 1`, `PROPOSED`) → `needs_review` |
| `needs_review` | `↻` | `Jāatkārto` | From `mastered` on inactivity decay (`>= 14` days) or `incorrect` (`>= 1` miss) | `1` `correct` (`needs_review_to_near_mastered_streak`, `PROPOSED`) → `near_mastered` | `incorrect` → `learning` (`consecutive_correct = 0`) |

---

## 2. Transition Event Contract (`MasteryEvent`)

The pure reducer `SimMastery.reduce(stateMap, events, policy)` accepts **only** graded criterion verdicts and explicit decay events:

```ts
type MasteryEvent =
  | {
      kind: 'criterion_verdict';
      outcome_id: string;
      verdict: 'correct' | 'incorrect';
      day?: number | null;          // injected coarse day integer (never Date.now())
      slot_id?: string;
      criterion_id?: string;
      graded_digest?: string;
    }
  | {
      kind: 'decay';
      outcome_id: string;
      days_inactive?: number | null; // or derived from current_day - last_practiced_day
      current_day?: number | null;
    };
```

**Input isolation invariant:**
- `SimMastery.extractCriterionEvents(gradedRecord, coverage, options)` converts `awarded` → `'correct'` and `denied` → `'incorrect'`.
- `pending`, `self`-graded, `manual_pending`, and `unattempted` items are **excluded** and emit zero mastery transitions.
- N29 self-assessment ratings are structurally excluded from `MasteryEvent` and cannot alter `MasteryMap`.
- Each criterion resolves its `outcome_id`s from `criterion.outcome_ids` if non-empty, else `instanceOrSlot.outcome_ids` (from N02 coverage through N20 instances), failing loudly with `E_MASTERY_UNMAPPED_CRITERION` if empty.

---

## 3. State Map Contract (`MasteryMap`)

Frozen shape stored under `store.getState().mastery` and passed to N27, N28, and N29:

```ts
interface OutcomeMasteryEntry {
  outcome_id: string;              // "P1-01" .. "P7-05" (all 64 outcomes)
  state: 'unseen' | 'learning' | 'near_mastered' | 'mastered' | 'needs_review';
  consecutive_correct: number;
  miss_in_mastered: number;
  attempts: number;
  correct_count: number;
  incorrect_count: number;
  last_practiced_day: number | null;
  last_verdict: 'correct' | 'incorrect' | 'decay' | null;
}

interface MasteryMap {
  schema_version: 1;
  policy_id: string;               // "sim-colloq1-mastery-policy-v1"
  policy_digest: string;           // SHA-256 of canonical #sim-mastery-policy
  outcomes: Record<string, OutcomeMasteryEntry>;
}
```

Canonicalization & digest: `SimMastery.digestOfMap(map)` computes SHA-256 over N04 sorted-key UTF-8 JSON.

---

## 4. Store Integration & Migration (`N25` v2)

- `SimStore` (`schema_version: 2`) persists `mastery` only under explicit learner opt-in (`sim_colloq1_store_v2`), preserves it across `normalizeV2` updates, exports it in `kimija-kolokvijs1-progress-v2.json`, and clears it completely on two-step erase.
- **Absent-key migration:** Pre-mastery `v2` stores and `v1 → v2` migrated stores omit `mastery`; `SimMastery.readFromStore(store, coverage, policy)` maps any absent `mastery` key (or missing outcome key) to all-64-`unseen`.
- **Newer-version guard:** Stores with `schema_version > 2` remain ignored and write-locked (`NEWER_VERSION_IGNORED` / `E_STORE_WRITE_BLOCKED_NEWER_VERSION`).

---

## 5. Availability & View Contracts (`#atskats`, `#prakse`)

- `SimMastery.computeAvailability(coverage, bankQuestions, policy)` evaluates N24 review eligibility per outcome (`review.{accessibility,calculation,content,source} === 'passed'` and `review_workflow.state === 'accepted'`, non-ephemeral).
- Outcomes with `eligible_count === 0` render as `unavailable` (`⊘ Pagaidām nav pieejams`) with an honest Latvian reason instead of `unseen`-but-practicable.
- Both `#atskats` (`renderAtskats` / `buildAtskatsViewModel`) and `#prakse` (`renderPrakse` / `buildPrakseViewModel`) render **icon + text** (never color-only) and carry the `PROPOSED` / non-official honesty notice.

---

## 6. Downstream Handoffs

- **N27 (Leitner scheduler):** Consumes `MasteryMap.outcomes[oid].state`, `last_practiced_day`, and `computeAvailability(...)` as its single learner-state input; maps the 5 `STATES` to Leitner boxes and excludes `eligible_count === 0` outcomes.
- **N28 (Remediation):** Consumes `MasteryMap` and updates mastery via `SimMastery.ingestGradedRecord` / `SimAnalytics.ingestGradedRecord` when remediation retries are graded.
- **N29 (Revision view & F07 self-assessment):** Consumes `MasteryMap`, `buildAtskatsViewModel`, and `STATES` labels/icons while keeping F07 self-ratings in a separate store key structurally excluded from `SimMastery.reduce`.
- **N32 (Visual / WCAG test data):** `evidence/N26_VIEW_FIXTURES.json` provides the `fresh`, `mid_progress`, `near_complete`, and `unavailable_topic` view models.
