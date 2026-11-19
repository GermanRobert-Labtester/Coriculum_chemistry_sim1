# SCHEDULER_FORMAT.md — N27 Offline Leitner Scheduler & N30 Practice Handoff Contract

**Owner:** N27 · **Status:** frozen interface for N30, N31, N32, and N40  
**Module:** `src/scheduler.ts` → `src/compiled/scheduler.js` (`root.SimScheduler`)  
**Island:** `#sim-scheduler-policy` (`data/scheduler_policy.json`) · **Gate:** `tools/validate_n27_scheduler.py` (Gate 23 `scheduler`)

> **Epistemic boundary.** The 2025 RSU programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`) specifies seven topics, a written-on-paper exam, and a 180-minute ceiling; it specifies **no** spaced-repetition intervals, Leitner boxes, or practice queue order (`official_counterpart_status: "UNDETERMINED"`). All box intervals, queue caps, and selection rules below are **PROPOSED** training policy implementing the predecessor plan's approved Leitner direction without copying any third-party algorithm (no SM-2, Anki, or SuperMemo code).

---

## 1. Leitner Box Model & Intervals (`PROPOSED`)

| Box | Role | Interval (`interval_days`, `PROPOSED`) | Mapped N26 Mastery States |
|---:|---|---:|---|
| `1` | `early` | `1` | `unseen`, `learning`, `needs_review` (forced early) |
| `2` | `mid` | `3` | `near_mastered` |
| `3` | `late` | `7` | `mastered` |

- **Strict monotonicity invariant:** `box[i+1].interval_days > box[i].interval_days` for every consecutive box pair; any non-increasing pair fails validation naming both boxes.
- **Single state truth:** `SimScheduler` reads `MasteryMap.outcomes[oid]` from N26 (`SimMastery`) and maintains no duplicate mastery state.

---

## 2. Day-Clock Contract

- Coarse **day granularity only** (zero sub-day/hour/millisecond scheduling precision; zero `Date.now()` or `performance.now()`).
- `SimScheduler.toDayNumber(dateInput)` accepts integer day indices, strict `YYYY-MM-DD` strings, or `Date` objects (using local calendar year/month/day).
- `SimScheduler.createFixedDayClock(dateInput)` provides deterministic injected clocks for all tests and fixtures.
- `SimScheduler.defaultDayClock()` reads the host's local calendar date for interactive `#prakse` display only.
- Pure selection `SimScheduler.selectQueue(...)` never reads wall time; it consumes an explicit `date` or `clock`.

---

## 3. Queue Selection & Deterministic Ordering (`PROPOSED`)

1. **Availability exclusion (N24 / N26):** Outcomes with `eligible_count === 0` (from N24 form-eligible family map or `SimMastery.computeAvailability`) are excluded from `queue[]` and recorded in `excluded[]` with `reason_code: "unavailable"` and term-keyed `reason_lv`.
2. **Overdueness:**
   - Fresh/never-seen (`state === 'unseen'` or `last_practiced_day === null`): `overdue_days = 0` (floored at zero).
   - Practiced: `days_since = max(0, current_day - last_practiced_day)`, `raw_overdue = days_since - box.interval_days`, `overdue_days = max(0, raw_overdue)`.
3. **Priority Tiers & Tie-Break:**
   - **Tier 1 (`overdue_and_due`):** `raw_overdue >= 0`, ordered by `overdue_days DESC`, tie-break `outcome_id ASC`. (`raw_overdue > 0` → `reason_code: "overdue"`; `raw_overdue === 0` → `reason_code: "due_today"`.)
   - **Tier 2 (`never_seen`):** `state === 'unseen' || last_practiced_day === null`, ordered by `topic ASC, outcome_id ASC` (`reason_code: "new"`).
   - **Tier 3 (`least_recently_practiced`):** `raw_overdue < 0`, ordered by `last_practiced_day ASC`, tie-break `outcome_id ASC` (`reason_code: "least_recently_practiced"`).
4. **Queue Cap:** Bounded to `queue_cap.value = 5` (`PROPOSED`).
5. **Reasons:** Term-keyed Latvian strings resolved from `#sim-terms` (`scheduler.reason.*`), linted by N10 (`tools/validate_terms.py`).

---

## 4. N27 → N30 Practice-Entry Handoff Contract

Accepting a queue item in `#prakse` invokes `SimScheduler.startPracticeFromQueueItem(item, options)`, which builds a selection-only handoff payload and passes it to `SimPractice.startPath(handoff)` (N30) when present (or renders `#prakse-scheduler-handoff` when N30 is not yet loaded):

```ts
interface PracticeHandoff {
  schema_version: 1;
  contract: 'N27-to-N30-practice-entry';
  entry_source: 'scheduler_queue';
  outcome_id: string;
  topic: number;
  mastery_state: 'unseen' | 'learning' | 'near_mastered' | 'mastered' | 'needs_review';
  box: number;
  reason_code: 'overdue' | 'due_today' | 'new' | 'least_recently_practiced' | 'unavailable';
  reason_lv: string;
  filters: {
    topic: number;
    outcome_id: string;
    family_ids: string[];
    instance_ids: string[];
  };
}
```

**Security / leak invariant:** The handoff payload contains **selection data only** — zero grading rubrics, zero answer keys, zero `payload` / `derived` / `expected` / `correct_ids` fields.
