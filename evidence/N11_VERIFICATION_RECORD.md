# N11 Verification Record — Inline SVG Figure Framework & T1-2 Records

**Status:** closed 2026-11-17 (UTC) · **Execution label:** VERIFIED (2026-11-17, this environment)

## 1. Figure Format Contract & Type Registry (`data/figure_schema.json`)

- **Registered types (`6`):** `bar`, `chain`, `curve`, `scatter`, `band`, `schema_plot` (N04 `payload_class: "graph"` coupled plot).
- **Mandatory shared fields:** `id`, `type`, `version`, `topic`, `concept_ids`, `title_key`, `description_lv` (mandatory Latvian screen-reader text >= 20 chars), `epistemic_label`, `has_measured_quantity`, `tolerance_coupling`, `axes`, `series`, `annotations`, `citations`, `lazy_slot: true`, `print_spec` (`viewBox[4]`, `monochrome_safe: true`).
- **Tolerance coupling & optionality rule (`N11-TOL-OPT-01`):**
  - **Mandatory** when `has_measured_quantity === true` OR `type === 'schema_plot'`: `tolerance_coupling` must resolve `tolerance_class` in `data/conventions.json` (`tolerances.quantity_classes[].id`), `conventions_ref`, `target_quantity_term_key` in `#sim-terms`, and `expected_unit` via N10 unit grammar.
  - **Optional (`null` permitted)** only when `has_measured_quantity === false && type !== 'schema_plot'` AND `structural_only_reason_lv` is declared explicitly.
- **V-02 percentage-basis rule:** Any figure using `%` or `fraction` must declare `percentage_basis` (`m_m`, `m_v`, `v_v`) and label every axis/series/bar/description explicitly; bare `%` fails validation (`E_FIG_UNLABELED_PERCENT`).

## 2. Malformed-Record Corpus & Valid Scratch Fixture (`tools/n11_corpus.py`)

- **Valid scratch record (`FIG-SCRATCH-VALID`):** `PASS`.
- **Malformed corpus (`9/9` caught by class & name) + build-gate refusal:**

| Fixture ID | Expected Error Code | Outcome |
|---|---|---|
| `NEG-UNKNOWN-TYPE` | `E_FIG_UNKNOWN_TYPE` | `PASS` (caught by type name) |
| `NEG-UNRESOLVED-TERM-KEY` | `E_TERMS_UNKNOWN_KEY` | `PASS` (caught by key name) |
| `NEG-UNIT-GRAMMAR-FAIL` | `E_UNIT_AMBIGUOUS_DENOMINATOR` | `PASS` (`J/mol·K` rejected) |
| `NEG-UNRESOLVED-TOLERANCE` | `E_FIG_UNKNOWN_TOLERANCE_CLASS` | `PASS` (caught by class name) |
| `NEG-MISSING-DESCRIPTION` | `E_FIG_MISSING_DESCRIPTION` | `PASS` (caught naming `FIG-SCRATCH-NODESC`) |
| `NEG-UNLABELED-PERCENT` | `E_FIG_UNLABELED_PERCENT` | `PASS` (bare `%` rejected) |
| `NEG-BROKEN-ANCHOR` | `E_FIG_BROKEN_ANCHOR` | `PASS` (case-exact check failed) |
| `NEG-RECOMPUTE-MISMATCH` | `E_FIG_RECOMPUTE_MISMATCH` | `PASS` (Decimal recompute caught mismatch) |
| `NEG-MISSING-MEASURED-TOLERANCE` | `E_FIG_MISSING_TOLERANCE` | `PASS` (mandatory coupling enforced) |
| `GATE-REFUSAL-UNKNOWN-TYPE` | `E_FIG_UNKNOWN_TYPE` | `PASS` (`tools/build.py` exited `1`, `artifact_written=false`) |

## 3. T1-2 Figure Set, Citations, Independent Recompute & Label Contract

- **Dataset (`data/figures_t12.json` → `#sim-figures`):** `9` records (`3` `bar`, `4` `chain`, `1` `band`, `1` `schema_plot`) covering all `18/18` N11-owned T1-2 concepts (`P1-01`–`P1-09`, `P2-01`–`P2-06`, `P2-08`–`P2-10`); `P2-07` stays `pending-N12`.
- **Anchor & conventions citations:** `9/9` master anchors resolved case-exactly against frozen `C1-MASTER` / `C2-MASTER` digests; all `conventions_refs` resolved against `data/conventions.json`.
- **N10 label & unit lint (`tools/validate_terms.py` + `tools/validate_figures.py`):** `43` figure term-key checks and `12` figure unit/dimension checks passed (`205` total `#sim-terms` entries, `0` errors).
- **Rounding-boundary corner case (`FIG-T2-COMP-ROUNDING-BOUNDARY`):** Samples `4,96 % (m/m)` and `5,04 % (m/m)` both round half-up to `5,0 % (m/m)` at 2 sig figs (`DV-RB-496`, `DV-RB-504`); bars render with guard-digit heights and display both exact and rounded values.
- **Independent `Decimal` (`ROUND_HALF_UP`) recompute (`17/17` agree):**

| Figure ID | Derived ID | Conventions Sources | Exact Decimal | Recomputed / Authored | Unit |
|---|---|---|---|---|---|
| `FIG-T1-COMP-NACL-BASES` | `DV-NACL-W-MM` | `percentage_basis.default_basis`, `rounding.rule` | `4.857751...` | `4.86` | `% (m/m)` |
| `FIG-T1-COMP-NACL-BASES` | `DV-NACL-W-MV` | `percentage_basis.allowed_bases`, `rounding.rule` | `5.02` | `5.02` | `% (m/V)` |
| `FIG-T1-COMP-NACL-BASES` | `DV-NAOH-W-MV` | `CIT-C1-DENSITY`, `rounding.rule` | `27.500` | `27.5` | `% (m/V)` |
| `FIG-T2-COMP-ROUNDING-BOUNDARY` | `DV-RB-496` | `rounding.rule` | `4.96` | `5.0` | `% (m/m)` |
| `FIG-T2-COMP-ROUNDING-BOUNDARY` | `DV-RB-504` | `rounding.rule` | `5.04` | `5.0` | `% (m/m)` |
| `FIG-T1-COMP-ETANOL-VV` | `DV-ETOH-WATER-VV` | `percentage_basis.allowed_bases`, `rounding.rule` | `30.0` | `30.0` | `% (V/V)` |
| `FIG-T1-CHAIN-AL-OXIDATION` | `DV-AL-N` | `atomic_masses.Al`, `rounding.rule` | `3.706174...` | `3.706` | `mol` |
| `FIG-T1-CHAIN-AL-OXIDATION` | `DV-O2-M` | `atomic_masses.Al`, `atomic_masses.O`, `rounding.rule` | `88.942628...` | `88.94` | `g` |
| `FIG-T1-CHAIN-AL-OXIDATION` | `DV-O2-V` | `atomic_masses.Al`, `constants.V_M`, `rounding.rule` | `62.302646...` | `62.30` | `L` |
| `FIG-T1-CHAIN-AL-OXIDATION` | `DV-AL2O3-M` | `atomic_masses.Al`, `compound_molar_masses.Al2O3`, `rounding.rule` | `188.942628...` | `188.9` | `g` |
| `FIG-T1-CHAIN-KOH-NEUTRALIZATION` | `DV-KOH-MASS` | `atomic_masses.{K,O,H}`, `rounding.rule` | `28.052500` | `28.05` | `g` |
| `FIG-T1-CHAIN-KOH-NEUTRALIZATION` | `DV-HCL-MASS` | `atomic_masses.{H,Cl}`, `rounding.rule` | `18.229000` | `18.23` | `g` |
| `FIG-T1-CHAIN-KOH-NEUTRALIZATION` | `DV-KCL-MASS` | `atomic_masses.{K,Cl}`, `rounding.rule` | `37.274000` | `37.27` | `g` |
| `FIG-T1-CHAIN-KOH-NEUTRALIZATION` | `DV-H2O-MASS` | `atomic_masses.{H,O}`, `rounding.rule` | `9.007500` | `9.01` | `g` |
| `FIG-T2-PLOT-NACL-DENSITY` | `DV-DEN-0` | `density.reference_relations[id=nacl_20c]` | `0.9979` | `0.9979` | `g/mL` |
| `FIG-T2-PLOT-NACL-DENSITY` | `DV-DEN-10` | `density.reference_relations[id=nacl_20c]` | `1.0709` | `1.0709` | `g/mL` |
| `FIG-T2-PLOT-NACL-DENSITY` | `DV-DEN-W-MEAS` | `density.reference_relations[id=nacl_20c]`, `rounding.rule` | `4.863013...` | `4.86` | `% (m/m)` |

## 4. Renderer Determinism, Theme Parity, Lazy Render, Degradation & Print

- **Two-run pure-renderer determinism (`tools/check_n11_runtime.js`, `9/9` byte-identical, `0` raw hex/rgb colors):**
  - `FIG-T1-COMP-NACL-BASES` (`4,430` B): `55d240dae8d597515eb8c74dff7de892d1dd42624369a7caf634f9025ac7e4fb`
  - `FIG-T2-COMP-ROUNDING-BOUNDARY` (`4,178` B): `b9db74b7accdca42c7b942a6e0c91402d2a4db0237b86a788f79e1a366a448f3`
  - `FIG-T1-COMP-ETANOL-VV` (`3,519` B): `6e2eb4174f879ab3ccfda8b19ae4f6907f980d5f8475f101a24772bf72602c2d`
  - `FIG-T1-CHAIN-AL-OXIDATION` (`3,179` B): `411fef5a16d60cee6bf8efb03b7ac42674e60a8f091a319006970966bbc8876e`
  - `FIG-T1-CHAIN-KOH-NEUTRALIZATION` (`2,591` B): `1411ba1d5a84f9739d4a9245e49346c26a2afcbb780c785fca9d1a51da6e86a9`
  - `FIG-T1-BAND-DISPERSION` (`2,846` B): `01ffd590916b8642a6d6bf6bb9eea82f83ece872f2fc548c735fc816979bdf10`
  - `FIG-T1-CHAIN-STRUCTURAL-MOLBRIDGE` (`2,612` B): `16f036e051b7cee2067b992dfe19f6f11fdac3018d2ac2cc9c46f4ac5429b769`
  - `FIG-T2-PLOT-NACL-DENSITY` (`7,178` B): `08197fbcdb580fedf3955b60aa5e688f0c86a3442620d07f7e54fa2a9e1f80e2`
  - `FIG-T2-CHAIN-PREFIX-SCALE` (`2,495` B): `66d268c64725ffcc35a09dafa35fe51729d7ea1075e624edc62097a66d699815`
- **Theme parity (`FIG-T1-COMP-NACL-BASES`):**
  - `light` (`fig-theme-light`): `55d240dae8d597515eb8c74dff7de892d1dd42624369a7caf634f9025ac7e4fb`
  - `dark` (`fig-theme-dark`): `350a13cac90b661d33454d758e3e1f9bc543b051075b5136768f08b0da207b25` (structural parity `true`)
  - `print` (`fig-theme-print`): `59229a5bcfa20e90aa684a3f3e2d4980d6ddd19a65d81f556f31261b9ae78855`
- **Lazy render (`tools/check_n11_runtime.js`):** `0` `<svg>` elements parsed on initial document load (`0` `renderEvents`); off-screen deferred slots stay `data-lazy-state="pending"` until `viewport-enter` activation; opening `P1-01` drawer renders only `P1-01`'s `3` figures (`authored-N11`); `P2-07` remains `pending-N12`.
- **Truncation & drawer-slot degradation:** Truncated `#sim-figures` displays `#sim-figures-error` (`E_FIGURES_JSON`), and opening `P1-01` while `#sim-figures` is corrupt keeps `#concept-drawer` open and renders `.fig-error-slot` (`data-error-code="E_FIGURES_JSON"`, `0` `<svg>`) inside `#drawer-slot-figures-P1-01`.
- **Falkon `lite-shot --cdp` renders (render check only, not full accessibility/instructor acceptance):**
  - `evidence/N11_PAINT_DRAWER_LIGHT.png` (`1280x1024`, `--theme light`, `overflow=false`, `8,291` colours)
  - `evidence/N11_PAINT_DRAWER_DARK.png` (`1280x1024`, `--theme dark`, `overflow=false`, `8,280` colours)
  - `evidence/N11_PAINT_PRINT.png` (`1280x1024`, `--media print`, `overflow=false`, `4,240` colours; black-on-white, solid vs dashed bars, zero clipped labels)

## 5. Parity, Sub-Budget Accounting, Smoke Vector & Handoffs

- **Build parity:** `output/simulator.html` (`651,176` bytes, `sha256=491de4d3890897a91b57c60b5d7fe8415946c91227bfe7d464945ac2cdadeaf7`, `build_id=05891e689216162f`) and `output/build-manifest.json` (`11,315` bytes) are byte-identical across consecutive builds; gates `1`–`10` `PASS`.
- **Section 1.3 byte accounting:** `#sim-figures` `24,755` canonical bytes + `src/figure-framework.js` `33,325` bytes = `58,080` bytes combined T1-2 figure share (`~56.7 KiB` against the `60–140 KiB` total Phase III figure sub-budget); executable JS code `195,159` B (`<= 225,280` B ceiling; `67,903` B inline N07/N08 JSON `var` projections accounted separately), CSS `29,150` B (`<= 81,920` B ceiling, `0` raw-value findings).
- **Corpus parity (`evidence/N11_CORPUS_RECORD.json`):** `23,371` bytes, `sha256=0bc104dc58bf529e96df66b04118188079dd2a5f01b1a447e56b836594025aa9`, byte-identical across two consecutive runs.
- **In-file smoke subset (`SimSmoke`):** `5/5` PASS (`SMK-N06-COVERAGE-COUNTS`, `SMK-N07-MAP-DRAWER-WALK`, `SMK-N08-HINT-LADDER-WALK`, `SMK-N10-TERMS-GRAMMAR-LOOKUP`, `SMK-N11-FIGURE-FRAMEWORK`).
- **Prior-phase zero-regression:** N02, N03, N05, N06, N07, N08, N10 runtime harnesses all `PASS`.
- **Handoffs:** Figure format (`data/figure_schema.json`) and `SimFigures` pure renderer + lazy-slot contract handed to **N12–N15**; `tolerance_coupling` + `N11-TOL-OPT-01` optionality rule handed to **N14**, **N15**, **N18**; `18/18` N11-owned T1-2 drawer figure slots closed for **N07** and handed to **N16**.
