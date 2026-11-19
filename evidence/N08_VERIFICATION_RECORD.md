# N08 Verification Record — Recall Layers & Hint Drawer Surfaces

**Status:** closed 2026-11-17 (UTC) · **Execution label:** VERIFIED (2026-11-17, this environment)

## 1. Layer Model & Four-Layer Semantics (Verbatim)

| Layer | Kind | Label (LV) | Purpose |
|---|---|---|---|
| 1 | `cue` | Virziena norāde | Īsa virziena norāde par uzdevuma pieeju bez formulas vai skaitliskās atbildes. |
| 2 | `concept_link` | Saistītais koncepts | Saite uz koncepta atvilktni (N07) pamatojošā mācību mērķa atkārtošanai. |
| 3 | `rule_citation` | Likums vai formula ar atsauci | Vispārīgais likums, sakarība vai formula ar norādi uz kursu konvenciju vai konceptu. |
| 4 | `first_step` | Risinājuma pirmais solis | Pirmais metodiskais risinājuma solis bez konkrētā varianta gala atbildes. |

**Depth rule (`max_depth_by_variant_class`):**
`Ja viena soļa (one_step) uzdevuma 4. slānis faktiski atklātu pašu atbildi, saime deklarē maksimālā dziļuma ierobežojumu 3 šai variantu klasei.`
Applied to: `FAM-1A`, `FAM-2A`, `FAM-2C`, `FAM-7A` (`default: 4`, `one_step: 3`, `depth_rule_applied: true`).

## 2. Per-Topic Coverage Table (24 Authored, 4 Honest Gaps)

| Topic | Authored Families | Honest Gaps (`gap-recorded`) | Depth Rule (`one_step: 3`) |
|---|---|---|---|
| 1 | `FAM-1A`, `FAM-1B`, `FAM-1C` | `FAM-1D` | `FAM-1A` |
| 2 | `FAM-2A`, `FAM-2B`, `FAM-2C`, `FAM-2D` | — | `FAM-2A`, `FAM-2C` |
| 3 | `FAM-3A`, `FAM-3B`, `FAM-3C` | `FAM-3D` | — |
| 4 | `FAM-4A`, `FAM-4B`, `FAM-4C`, `FAM-4D` | — | — |
| 5 | `FAM-5A`, `FAM-5B`, `FAM-5C`, `FAM-5D` | — | — |
| 6 | `FAM-6A`, `FAM-6B`, `FAM-6C` | `FAM-6D` | — |
| 7 | `FAM-7A`, `FAM-7B`, `FAM-7C` | `FAM-7D` | `FAM-7A` |

## 3. Data & Rendered-Output Leak Scans + Copy Lint

- **Data-level leak scan (`tools/validate_n08_layers.py`):** PASS (`0` findings across 24 authored families; all `concept_ids` and `citation` entries resolved against `data/coverage.json` and `data/conventions.json`).
- **Planted data-leak fixture (`NEG-PLANTED-DATA-LEAK`):** FAIL by name (`E_LEAK_DETECTED: FAM-1C L3 leaked '8.0' (GV-S1-T1-Q02-01)`), and build gate `order 8 recall_layers` refused build (`GATE-REFUSAL-PLANTED-LEAK`, exit 1, no artifact written).
- **Rendered-output leak scan (`tools/n08_corpus.py` over `check_n08_runtime.js` output):** PASS (`24` rendered drawers scanned, `0` findings; degenerate formula-symbol edge case `c = n / V; l = 1 cm; ΔfH° = 0` produced `0` false positives; planted rendered leak `8.00 g` caught by name).
- **Copy lint:** PASS (`123` strings linted; `15` UI/layer keys recorded in `data/n08_term_stubs.json` with `status: "stub-pending-N10"` for N10 closure).

## 4. Drawer Boundary, Focus, Reopen & Grading Neutrality

- **Exam-mode refusal (`modeRefusalFixture`):** `SimHintDrawer.open({ mode: 'exam', ... })` threw `HintDrawerError` with stable error id `E_HINT_EXAM_MODE_FORBIDDEN`, `revealedLayers: 0`, `eventsRecorded: 0`; `renderHelpControl` in exam mode rendered `disabled: true` with `data-mode-boundary="E_HINT_EXAM_MODE_FORBIDDEN"`.
- **Focus & nested handoff (`focusFixture`, `nestedHandoffFixture`):** `practice-help-btn` → `hint-drawer-close` → `hint-open-concept-P1-01` → `concept-drawer-close` → `hint-open-concept-P1-01` → `practice-help-btn`.
- **Three-reveal & summary (`threeRevealFixture`):** 3 reveals produced 3 ordered events (`[1, 2, 3]`); `renderUsageSummary` rendered honest info with `data-penalty="none"`.
- **Reopen (`reopenFixture`):** closing after layers `[1, 2]` preserved `usedLayers: [1, 2]` in session; reopening emitted 0 duplicate events and resumed `#hint-reveal-next` from layer 3 (`Atklāt 3. slāni: Likums vai formula ar atsauci (3 / 4)`).
- **Grading neutrality (`neutralityFixture` on `GV-S1-T1-Q02-01`):**
  - Graded record digest without help: `dbde6d3e331cb8154dd4d88b921fe6bcd216ca4740179833712fd9f331b06632` (`0` hint events)
  - Graded record digest with 4 hints: `dbde6d3e331cb8154dd4d88b921fe6bcd216ca4740179833712fd9f331b06632` (`4` hint events)
  - `digestsMatch: true`

## 5. Build Parity, Byte Accounting, Smoke & Visual Render Check

- **Artifact:** `output/simulator.html` (`489,647` bytes, `sha256=3b0d89dabcbfbe52cd591c409b5f890a90addc69f520b7340164ac04e8ca3921`, `build_id=95a4a661a5c6e057`), byte-identical across two builds.
- **Byte contribution:** `data/recall_layers.json` canonical `28,586` B (embedded `28,517` B), `src/hint-drawer.js` `21,992` B.
- **Corpus parity:** `evidence/N08_CORPUS_RECORD.json` byte-identical across two consecutive runs (`sha256=f03559b425e219274c0a3846310c58a08019e13a0228c78a7bd2b7695bf88936`).
- **In-file smoke subset (`SimSmoke`):** `3/3` PASS (`SMK-N06-COVERAGE-COUNTS`, `SMK-N07-MAP-DRAWER-WALK`, `SMK-N08-HINT-LADDER-WALK`).
- **Prior-phase regressions:** N02, N03, N05, N06, N07 runtime harnesses all PASS.
- **Paint check (`lite-shot --cdp -e falkon --theme light --anchor prakse`):** `evidence/N08_PAINT_PRAKSE.png` (`1280x1024`, `overflow=false`, `11,418` colours; render check only, not full WCAG/accessibility acceptance).

## 6. Handoffs

- **N10:** `data/n08_term_stubs.json` (`15` keys, `stub-pending-N10`).
- **N20:** Family binding + `item_overrides` + `max_depth_by_variant_class` contract in `data/recall_layers.json`.
- **N21:** Exam-mode refusal contract (`E_HINT_EXAM_MODE_FORBIDDEN`).
- **N25:** Session `hint_layer_revealed` event schema precursor.
- **N30:** `SimHintDrawer.renderHelpControl`, `SimHintDrawer.renderUsageSummary`, and `#prakse-help-slot`.
