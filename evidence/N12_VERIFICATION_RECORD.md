# N12 Verification Record — T2-3 Burette & Dilution Figures + Leak-Scan Engine

**Status:** Closed (`PASS`, 2026-11-17 UTC)
**Scope:** Laboratory figure authoring (`data/figures_t23.json`), burette/dilution reading-conventions contract (`data/reading_conventions_contract.json`), unified figure & hint leak-scan engine (`tools/leak_scan.py`, `src/leak-scan.js`), build gate `order 11 figure_leak_scan` (`tools/build.py`), extended runtime smoke vector (`SMK-N12-BURETTE-READ-SCAN`), and two-run deterministic corpus (`evidence/N12_CORPUS_RECORD.json`).
**Epistemic note:** All tool runs, hashes, and captures were observed in this workspace (`VERIFIED (2026-11-17)`). Design choices not specified in the programme (`RSU_MedChem_Colloq1_Prog_LV_2025.pdf`), including schematic SVG dimensions, tolerance-class labels (`burette_volume`, `volumetric_flask`), and worked/gradeable numeric example values, carry explicit `PROPOSED` or `master-grounded` labels. Falkon `lite-shot --cdp` captures are render checks only and do not substitute for full accessibility, print-press, scientific, or instructor acceptance.

---

## 1. Burette Reading-Rule Fidelity, Geometry Recompute & Edge Coverage

Every burette record adheres strictly to `N03-OBS-04` (`data/conventions.json`): `25.00 mL` nominal capacity, `0.1 mL` smallest division, `±0.05 mL` half-subdivision reading uncertainty, mandatory `2` decimal places (`reported_decimals = 2`), downward-increasing scale (`0.00 mL` at top), eye-level parallax alignment, `lower_meniscus` for `clear` solutions, and `upper_edge` for `dark` solutions (`KMnO₄`).

### 1.1 Independent Geometric Recompute Table (`6/6` Columns Pass)

| Figure ID | Column ID | Clarity / Meniscus Edge | Declared Reading (mL) | Authored `meniscus_y_px` | Expected `y` (px) | Recomputed Reading (mL) | Scale (`px/mL`) | Minor Div Print (mm) | Half-Subdiv Print (mm) | Match |
|---|---|---|---|---|---|---|---|---|---|---|
| `FIG-T2-BURETTE-CLEAR-WHOLE` | `col-whole` | `clear` / `lower_meniscus` | `1.00` | `196.0` | `196.00` | `1.00` | `120` | `2.46` | `1.23` | PASS |
| `FIG-T2-BURETTE-NEAR-ZERO` | `col-near-zero` | `clear` / `lower_meniscus` | `0.15` | `94.0` | `94.00` | `0.15` | `120` | `2.46` | `1.23` | PASS |
| `FIG-T2-BURETTE-SUBDIVIDED` | `col-subdivided` | `clear` / `lower_meniscus` | `5.85` | `238.0` | `238.00` | `5.85` | `120` | `2.46` | `1.23` | PASS |
| `FIG-T2-BURETTE-DARK-CAPACITY` | `col-dark-cap` | `dark` / `upper_edge` | `24.85` | `298.0` | `298.00` | `24.85` | `120` | `2.46` | `1.23` | PASS |
| `FIG-T2-BURETTE-DELIVERED-GRADE` | `col-start` | `clear` / `lower_meniscus` | `2.15` | `248.0` | `248.00` | `2.15` | `80` | `1.69` | `0.85` | PASS |
| `FIG-T2-BURETTE-DELIVERED-GRADE` | `col-end` | `clear` / `lower_meniscus` | `18.40` | `188.0` | `188.00` | `18.40` | `80` | `1.69` | `0.85` | PASS |

### 1.2 Pedagogical Edge Coverage & Print-Size Resolution Floor

- `whole`: `FIG-T2-BURETTE-CLEAR-WHOLE` (`1.00 mL`, demonstrates mandatory trailing zeros `.00`).
- `near-zero`: `FIG-T2-BURETTE-NEAR-ZERO` (`0.15 mL`, near `0.00 mL` top meniscus boundary).
- `subdivided`: `FIG-T2-BURETTE-NEAR-ZERO`, `FIG-T2-BURETTE-SUBDIVIDED` (`5.85 mL`), `FIG-T2-BURETTE-DARK-CAPACITY` (`24.85 mL`), `FIG-T2-BURETTE-DELIVERED-GRADE` (`2.15 mL`, `18.40 mL`).
- `near-capacity`: `FIG-T2-BURETTE-DARK-CAPACITY` (`24.85 mL` dark `KMnO₄` upper-edge meniscus near `25.00 mL`).
- **Print resolution floor check:** All burette records exceed the declared print floors (`minor division >= 1.50 mm`, `half-subdivision >= 0.75 mm`). Even the dual-column `FIG-T2-BURETTE-DELIVERED-GRADE` (`width_mm = 165`, `viewBox` width `780`) renders `0.1 mL` subdivisions at `1.69 mm` and half-subdivision (`0.05 mL`) interpolation offsets at `0.85 mm`.
- **Negative geometry/meniscus proof:**
  - `FIG-SCRATCH-MISDRAWN-BURETTE`: fails by ID (`FIG-SCRATCH-MISDRAWN-BURETTE:col-subdivided: [E_FIG_BURETTE_GEOMETRY_MISMATCH] expected_y=238.000 != meniscus_y_px=250.0, recomputed_reading=5.9500 != declared=5.85`).
  - `FIG-SCRATCH-WRONG-EDGE`: fails by ID (`FIG-SCRATCH-WRONG-EDGE:col-whole: [E_FIG_MENISCUS_RULE] clarity='clear' requires edge='lower_meniscus', got 'upper_edge'`).

---

## 2. Dilution Arithmetic, Citations & N10 Scale-Label Validation

### 2.1 Dilution Factor Arithmetic (`4/4` Steps Pass)

| Figure ID | Step | Mode | `V1` (mL) | `V2` (mL) | `c1` (mol/L) | Stated / Recomputed `f` | Stated / Recomputed `c2` (mol/L) | Visible Label | Result |
|---|---|---|---|---|---|---|---|---|---|
| `FIG-T3-DILUTION-PIPETTE-FLASK` | `D1` | `worked_arithmetic` | `25.00` | `250.0` | `0.500` | `10.0` / `10.00` | `0.0500` / `0.0500` | Yes | PASS |
| `FIG-T3-DILUTION-SERIAL-CHAIN` | `S1` | `worked_arithmetic` | `10.00` | `100.0` | `1.00` | `10.0` / `10.00` | `0.100` / `0.1000` | Yes | PASS |
| `FIG-T3-DILUTION-SERIAL-CHAIN` | `S2` | `worked_arithmetic` | `20.00` | `100.0` | `0.100` | `5.00` / `5.00` | `0.0200` / `0.0200` | Yes | PASS |
| `FIG-T3-DILUTION-CONC-GRADE` | `G1` | `formula_only` | `15.0` | `450.0` | `3.00` | `—` / `30.00` | `—` / `0.1000` | No (gradeable `FAM-3C`) | PASS |

- Cumulative serial dilution factor on `FIG-T3-DILUTION-SERIAL-CHAIN`: `10.00 × 5.00 = 50.00` (`c_B = 0.0200 mol/L`), matching visible annotation.
- Negative dilution fixture (`FIG-SCRATCH-DILUTION-ARITH`) fails by ID with `[E_FIG_DILUTION_ARITHMETIC]`.

### 2.2 Citations & N10 Label Grammar

- **T2-3 Master Anchors & Conventions Refs (`10/10` figures resolve):**
  - `FIG-T2-BURETTE-CLEAR-WHOLE` (`C2-MASTER` / `#ch-5`, `3/3` conventions refs)
  - `FIG-T2-BURETTE-NEAR-ZERO` (`C2-MASTER` / `#ch5-biretes-protokols-2b-q2`, `3/3` conventions refs)
  - `FIG-T2-BURETTE-SUBDIVIDED` (`C2-MASTER` / `#ch5-menisks-un-paralakse`, `3/3` conventions refs)
  - `FIG-T2-BURETTE-DARK-CAPACITY` (`C6-MASTER` / `#h-ch9`, `3/3` conventions refs)
  - `FIG-T2-BURETTE-DELIVERED-GRADE` (`C2-MASTER` / `#ch-5`, `3/3` conventions refs)
  - `FIG-T3-DILUTION-PIPETTE-FLASK` (`C3-MASTER` / `#n10`, `3/3` conventions refs)
  - `FIG-T3-DILUTION-SERIAL-CHAIN` (`C3-MASTER` / `#n10`, `3/3` conventions refs)
  - `FIG-T3-DILUTION-CONC-GRADE` (`C3-MASTER` / `#n10`, `2/2` conventions refs)
  - `FIG-T3-CONC-BASES-BRIDGE` (`C3-MASTER` / `#n9`, `5/5` conventions refs)
  - `FIG-T3-MEDICAL-ION-BASES` (`C3-MASTER` / `#n5`, `4/4` conventions refs)
- **N10 Grammar & Scale Formatting:** `34` rendered burette scale labels across all `6` burette columns verified to match `^\d+,\d{2} mL$` (`2` decimals with Latvian comma) and pass N10 unit parsing. `data/terms.json` expands to `230` entries (`121` terms / `31` quantities / `13` instruments / `55` interface keys / `10` IUPAC pairs); `python3 tools/validate_terms.py` PASS (`units=321`, `keys=84`, `exempt_prose=360`).
- **T2-3 Concept Slots Closed:** `12/12` N12-owned slots (`P2-07`, `P3-01`–`P3-11`) closed (`authored-N12`), joining N11's `18/18` (`slots 192/192` in `validate_n07_map.py`).

---

## 3. Unified Leak-Scan Engine, Declared Rules & Planted Corpus

The leak-scan engine (`tools/leak_scan.py` + `src/leak-scan.js`) scans three surfaces (`data`, `annotations`, `rendered_svg`), normalizes quantities via the N10 unit grammar (`SI` base dimensions `{M, L, T, N}` and decimal scaling), and converges N08 hint-layer leak scanning into the same engine. Runtime execution never scans learner input.

### 3.1 Declared Rules (Verbatim)

- **`N12-LEAK-SIG-01` (Significance Rule):**
  > Only values distinctive to the instance or family are scan targets. Bare un-united integers in {0..9} and common structural/scaling constants {10, 100, 1000, 0.1, 0.01, 0.001, 273.15, 298.15} are NOT scan targets when appearing without a matching unit; they ARE scan targets whenever paired with a dimensionally matching unit (e.g. "10 mL", "100 mmol/L") or written in a distinctive precision form (e.g. "10.5", "12.35") or explicitly marked distinctive.
- **`N12-LEAK-BORDER-01` (Borderline Range Rule):**
  > Any gradeable figure whose numeric axis range or scale window [min, max] pins a gradeable target value onto an endpoint or within the outer 2% extreme (normalized position <= 0.02 or >= 0.98) or constrains the span to <= 2 steps around the target is flagged with FLAG_BORDERLINE_RANGE for authoring review.
- **`N12-LEAK-EXEMPT-01` (Exemption Discipline):**
  > Only non-gradeable teaching/reading-display figures (gradeable=false) may declare leak_scan_exemption with an explicit reason_code, non-empty Latvian reason_lv (>= 20 chars), and explicit exempted_values list; gradeable figures cannot exempt their own scored answer targets (E_LEAK_ILLEGAL_EXEMPTION), and any unlisted answer-key leak on an exempted figure is still caught. All exemptions are audited at N40 closure.

### 3.2 Planted Corpus Results (`7/7` Cases + Build Gate Refusal + N08 Convergence)

| Case ID | Scenario | Expected | Observed Outcome / Output | Result |
|---|---|---|---|---|
| `PLANTED-LEAK-ANNOTATION` | Gradeable annotation quotes `16.25` | Catch (`FAIL`) | `FIG-SCRATCH-LEAK-ANN: [E_LEAK_DETECTED] (data/numeric) leaked '16.25' (target=16.25)` | PASS |
| `PLANTED-LEAK-UNIT-NORMALIZED` | Target `0.75 mg/mL`; annotation says `"750 mg/L"` | Catch (`FAIL`) | `unit_normalized` match: `leaked_raw='750 mg/L'`, `leaked_norm='0.750 (dim={M:1, L:-3})'`, `target_raw='0.75 mg/mL'` | PASS |
| `PLANTED-BORDERLINE-RANGE` | Axis `[0.0, 16.5]` pins target `16.25 mL` at `0.9848 >= 0.98` | Flag (`FLAG`) | `FLAG_BORDERLINE_RANGE` on `axes.y`, `rule_id=N12-LEAK-BORDER-01`, `normalized_position=0.9848` | PASS |
| `EXEMPT-READING-DISPLAY` | `FIG-T2-BURETTE-SUBDIVIDED` displays `5.85 mL` (`gradeable=false`) | Exempt (`EXEMPT`) | `EXEMPT_READING_DISPLAY`, `matched_hits_count=10`, Latvian `reason_lv` recorded | PASS |
| `SIGNIFICANCE-CONSTANT-10-IGNORED` | Bare constant `10` in structural figure with answer target `10` | Pass (`PASS`) | Common constant without unit ignored under `N12-LEAK-SIG-01` | PASS |
| `SIGNIFICANCE-UNIT-PAIRED-10ML-CAUGHT` | Target `10.0 mL`; text contains `"10,0 mL"` | Catch (`FAIL`) | `unit_normalized` match: `leaked_raw='10,0 mL'`, `leaked_norm='0.0100 (dim={L:3})'` | PASS |
| `ILLEGAL-GRADEABLE-EXEMPTION` | Gradeable figure attempts `leak_scan_exemption` | Catch (`FAIL`) | `FIG-SCRATCH-ILLEGAL-EXEMPT: [E_LEAK_ILLEGAL_EXEMPTION] Gradeable figure cannot declare leak_scan_exemption.` | PASS |
| `GATE-REFUSAL-PLANTED-LEAK` | Inject `0,01625 L` into `FIG-T2-BURETTE-DELIVERED-GRADE` build | Refuse (`rc=1`, no artifact) | `FAIL figure_leak_scan gate (order 11, owner N12): ... leaked '0,01625 L' (target=16.25 mL)`, `artifact_written=false` | PASS |
| `N08-CONVERGENCE-REGRESSION` | Run `tools/n08_corpus.py` delegated through `tools/leak_scan.py` | `PASS` | `24` authored families, `0` leaks, `n08_corpus_status=PASS`, `rendered_scan_status=PASS` | PASS |

- Production corpus scan (`19` total figures: `9` T1-2 + `10` T2-3; `2` gradeable, `7` exempted): `flags=0`, `leaks=0`, `status=PASS`.

---

## 4. End-to-End Runtime Proof, Visual Inspection & Frozen Contract Handoff

- **Pure-renderer two-run determinism (`tools/check_n12_runtime.js`, `10/10` T2-3 figures byte-identical, `0` raw colors):**
  - `FIG-T2-BURETTE-CLEAR-WHOLE` (`5,364` B): `778eff25f3903d10550e45699125474af7fedf08cf4b7fa0ea861e3fd59ca99b`
  - `FIG-T2-BURETTE-NEAR-ZERO` (`4,738` B): `01ca4e9690b68dad9edf2a5f2fde3ade3638a031696302e29157b4287c2b002a`
  - `FIG-T2-BURETTE-SUBDIVIDED` (`5,307` B): `61f503ca8fc097acefa06fe71f76942bd258f3cd395aeeb41da2597b01b13eae`
  - `FIG-T2-BURETTE-DARK-CAPACITY` (`5,056` B): `9a69f6e2ce9563d20c9db4efcc04cf4e8b165a6da5765e580492cb254e798576`
  - `FIG-T2-BURETTE-DELIVERED-GRADE` (`9,893` B): `5351fee6b52ea19a736bd4c0d9b2932fc40f7719430c90e6003bea5c372879c1`
  - `FIG-T3-DILUTION-PIPETTE-FLASK` (`2,482` B): `1ea928fd15da223735eb0956fe2b287fda211e183691119760a4be889836d65a`
  - `FIG-T3-DILUTION-SERIAL-CHAIN` (`3,722` B): `09854492a7066f9919938c86b6ed3fd321493bd8fc2af5264b34c7cc41e71117`
  - `FIG-T3-DILUTION-CONC-GRADE` (`2,381` B): `8585ea2d190970c983fd24fdce4dde3b5ea8469cd95294f4550101f4fb7732ba`
  - `FIG-T3-CONC-BASES-BRIDGE` (`3,072` B): `3d10d75d0b458a510403858abf2732259ebad1e26f81683e292d8c5a5dc6a90e`
  - `FIG-T3-MEDICAL-ION-BASES` (`4,088` B): `5951c6fb3f9ff8c20197c77f5d8eceb9d3c5b04ce02a13863ec6c44c201d9d2e`
- **Theme parity (`FIG-T2-BURETTE-DELIVERED-GRADE`):** `light` `5351fee6...`, `dark` `27b0b9709894795b8aff71e353f508ccfd6893bdbbc25e17c726af6586128db7`, `print` `0705e2f46c1cdcf6ed39b92c0af578d088e77890b79bc818a1a9a324a0f295eb` (`structural_parity_light_vs_dark = true`).
- **Lazy render & truncation degradation:** `0` `<svg>` elements on initial load; opening `P2-07` renders `5` figures; opening `P3-10` renders `3` figures; truncating `#sim-figures` triggers `E_FIGURES_JSON` in `#sim-figures-error` and `.fig-error-slot` inside `P2-07` with `0` `<svg>` rendered.
- **Falkon `lite-shot --cdp` visual render checks (render check only, not full WCAG/instructor/scientific acceptance):**
  - `evidence/N12_PAINT_DRAWER_LIGHT.png` (`1280x1024`, `--theme light`, `116,951` B, `5,999` colours, `overflow=false`): inspected — `P2-07` drawer open showing burette meniscus curves, `0,00`–`2,00`/`4,50`–`6,50 mL` scales, non-overlapping `skala ↓` indicator, and parallax callouts.
  - `evidence/N12_PAINT_DRAWER_DARK.png` (`1280x1024`, `--theme dark`, `117,544` B, `6,131` colours, `overflow=false`): inspected — clean dark-theme polarity and crisp legibility.
  - `evidence/N12_PAINT_PRINT.png` (`1259x2182`, `--theme light --media print --full-page`, `235,102` B, `5,215` colours, `overflow=false`): inspected — `FIG-T2-BURETTE-DELIVERED-GRADE`, `FIG-T2-BURETTE-SUBDIVIDED`, and `FIG-T3-DILUTION-PIPETTE-FLASK` render in crisp black-on-white print styling; `0,1 mL` subdivisions and half-subdivision meniscus placement (`2,15`, `5,85`, `18,40 mL`) are clearly resolvable with zero text overlap or clipping.
- **In-file smoke subset (`SimSmoke`):** `6/6` PASS (`SMK-N06-COVERAGE-COUNTS`, `SMK-N07-MAP-DRAWER-WALK`, `SMK-N08-HINT-LADDER-WALK`, `SMK-N10-TERMS-GRAMMAR-LOOKUP`, `SMK-N11-FIGURE-FRAMEWORK`, and new `SMK-N12-BURETTE-READ-SCAN`).
- **Section 1.3 sub-budget & build parity:**
  - `output/simulator.html`: `717,923` B (`sha256=462a3d03b092e3f8f627e4f81893a7a1e6b72a29cd71418e2cebe9dbcdfb4239`, `build_id=ba59c2935f7741fc`), `output/build-manifest.json` (`12,451` B, `sha256=23cd79862557c6309d42889957af4b0b8a0203031b27c96f0279653a2f1d28d0`), byte-identical across consecutive builds; gates `1`–`11` PASS.
  - Combined `#sim-figures` (`53,947` canonical B = `24,755` T1-2 + `29,588` T2-3) + `src/figure-framework.js` (`43,429` B) + `src/leak-scan.js` (`12,128` B) = `109,504` B (`~106.9 KiB`, inside the `61,440–143,360` B / `60–140 KiB` Phase III figure sub-budget).
  - Executable JS code: `219,899` B (`<= 225,280` B ceiling); CSS: `30,932` B (`<= 81,920` B ceiling, `0` raw-value findings).
  - Two-run `evidence/N12_CORPUS_RECORD.json`: `55,668` B, `sha256=5f910a98b89e6ffaa3dc6aec0a1b2cbba495505191a09de0b5646744c67f68cb` (byte-identical across two consecutive runs).
- **Frozen handoff (`data/reading_conventions_contract.json`):** Canonical digest `e12f868229f8effafdfad329b931244ff0d002fbbf814f8795e3f35fb1408075` (file `76a34160173b544dd134f2682b29426ae4ee1c36d4c2e753914c9643191c6732`, `4,803` B), shared by **N12**, **N15** (titration figures), **N17**–**N18** (reading-error and titration grading), **N31**, and **N40** (exemption audit).
- **Prior-phase zero-regression:** `N02`, `N03`, `N05`, `N06`, `N07`, `N08`, `N10`, `N11` runtime harnesses all `PASS`.
