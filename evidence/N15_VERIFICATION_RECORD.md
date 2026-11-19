# N15 Verification Record — Topic 6-7 titration and calibration figures

Date: 2026-11-17. Scope: figure authoring data, validator and runtime checks in this workspace. This is not instructor, scientific-expert, physical-print or accessibility acceptance. The titration curves except the master-grounded KMnO₄ case are `PROPOSED` training policy, not official exam content.

## 1. What was built

| Item | Path | Note |
|---|---|---|
| T6-7 records (8) | `data/figures_t67.json` | 5 titration records (strong/strong, weak/strong, wrong indicator, master KMnO₄/Fe²⁺, practice) + 3 calibration records (master through-zero, near-edge free regression, practice) |
| Titration contract | `data/titration_contract.json` | Model vocabulary, V-05 wording rule, N12 reading coupling, N17/N18/N37 handoff |
| Calibration contract | `data/calibration_contract.json` | V-07 assumption vocabulary and the no-extrapolation rule verbatim for N18 |
| Schema extension | `data/figure_schema.json` | Three `titration_*` curve classes, `t67_titration_calibration_fields`, type-registry handoff |
| Renderer | `src/figure-framework.js` | Titration curve classes, indicator/buffer bands, equivalence/half/endpoint markers, reading strip, calibration reading lines, axis decimal formatting |
| Terms | `data/terms.json` | 28 N15 `fig.*` entries (315 total) |
| Slot closure | `data/concept_summaries.json` | `P6-01`–`P6-08` and `P7-01`–`P7-05` `authored-N15` (13/13) |
| Validator | `tools/validate_figures.py` | Model, V-05, reading, calibration, V-07 and no-extrapolation checks; contract drift checks |
| Build wiring | `tools/build.py` | `--figures-t67`, contract digests, merged `#sim-figures` (45 records) |
| Smoke | `src/smoke-subset.js` | `SMK-N15-T67-TITRATION` (9/9 total) |
| Runtime harness / corpus | `tools/check_n15_runtime.js`, `tools/n15_corpus.py` | |

## 2. Records

| Figure | Type | Model / dataset | Key declared values | Answer exposure |
|---|---|---|---|---|
| `FIG-T67-TITR-STRONG` | curve | HCl 0,1000 mol/L, 25,00 mL; NaOH 0,1000 mol/L | V_eq 25,00 mL, pH 7,00; phenolphthalein 8,2–10,0 | teaching; no answer target |
| `FIG-T67-TITR-WEAK` | curve | CH₃COOH 0,1000 mol/L, K_a 1,8·10⁻⁵; NaOH 0,1000 mol/L | V_eq 25,00 mL, pH 8,72; half-eq 12,50 mL/pH 4,745 | teaching; no answer target |
| `FIG-T67-TITR-WRONG-IND` | curve | same weak acid; methyl orange 3,1–4,4 | V_eq 25,00 mL; endpoint 7,77 mL; miss 17,23 mL | exempted worked teaching trace |
| `FIG-T67-TITR-MASTER-KMNO4` | curve | C6 L25: Fe²⁺ 0,1235 mol/L, 10,00 mL; KMnO₄ 0,0200 mol/L | V_eq 12,35 mL; E_eq 1,3867 V; E₀ 0,5332 V | master-grounded teaching |
| `FIG-T67-TITR-PRACTICE` | curve | weak acid 0,0900 mol/L, 25,00 mL; NaOH 0,1100 mol/L | V_eq computed 20,4545 mL; no declared answer in data | gradeable; answer target 20,45 mL only |
| `FIG-T67-CAL-MASTER` | scatter | C7 2020 protocol: 9 standards 0–0,016 mg/mL, A 0–0,482 | through-zero A = 30,39·γ; A = 0,258 → 0,00849 mg/mL | exempted reading display |
| `FIG-T67-CAL-NEAR-EDGE` | scatter | same standards; free regression | A = 30,24·γ + 0,0017; A = 0,470 → 0,01549 mg/mL (96,8 % of upper standard) | exempted reading display |
| `FIG-T67-CAL-PRACTICE` | scatter | 5 standards 0–0,016 mg/mL; through zero | A = 25,02·γ; signal 0,365; answer withheld | gradeable; answer target 0,01459 mg/mL only |

The master redox case is labelled `master-grounded` and cites `materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html#h-ch9`; the calibration records cite `materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html#fig-cal`. The C6 bench figure itself gives the 0,0200 mol/L KMnO₄ titrant, 10,00 mL Fe²⁺ aliquot and 12,35 mL reading; the Fe²⁺ concentration follows from the master's 5:1 stoichiometry.

## 3. Titration model checks (A.1.1)

`tools/validate_figures.py` regenerates each curve from its own parameters, finds the maximum adjacent-point slope and compares that inflection with the declared equivalence volume; it also recomputes the initial pH/potential and, for weak acids, the buffer slope.

| Figure | Model V_eq (mL) | Declared V_eq (mL) | Inflection (mL) | Initial pH / V recomputed | Buffer slope / equivalence slope (pH/mL) | Agrees |
|---|---|---|---|---|---|---|
| `FIG-T67-TITR-STRONG` | 25,0000 | 25,00 | 24,9375 | pH 1,000000 | — | yes |
| `FIG-T67-TITR-WEAK` | 25,0000 | 25,00 | 24,9375 | pH 2,875277 | 0,0762 / 60,6584 | yes |
| `FIG-T67-TITR-WRONG-IND` | 25,0000 | 25,00 | 24,9375 | pH 2,875277 | 0,0762 / 60,6584 | yes |
| `FIG-T67-TITR-MASTER-KMNO4` | 12,3500 | 12,35 | 12,3438 | E 0,533203 V | — | yes |
| `FIG-T67-TITR-PRACTICE` | 20,4545 | computed (answer withheld) | 20,4375 | pH 2,898313 | 0,0932 / 68,3225 | yes |

The inflection tolerance is 0,15 mL, i.e. about one 401-point step (50 mL / 400 = 0,125 mL) on each side. A scratch copy of `FIG-T67-TITR-STRONG` with `declared_equivalence_volume_ml = 26.00` fails by id with `E_FIG_TITRATION_EQUIVALENCE`.

## 4. V-05 copy lint and wrong-indicator trap (A.1.2)

Every record with an endpoint or indicator names “ekvivalences punkts” and “beigu punkts” distinctly, explains that the difference is the titration error (≈ one drop), and contains no equation of the two terms and no invented universal persistence time. The practice record has no endpoint, so it only carries the distinct equivalence term.

| Figure | Equivalence named | Endpoint named | Distinction explained | Synonym forbidden | No universal time | Agrees |
|---|---|---|---|---|---|---|
| `FIG-T67-TITR-STRONG` | yes | yes | yes | yes | yes | yes |
| `FIG-T67-TITR-WEAK` | yes | yes | yes | yes | yes | yes |
| `FIG-T67-TITR-WRONG-IND` | yes | yes | yes | yes | yes | yes |
| `FIG-T67-TITR-MASTER-KMNO4` | yes | yes | yes | yes | yes | yes |
| `FIG-T67-TITR-PRACTICE` | yes | no endpoint | n/a | yes | yes | yes |

The wrong-indicator record declares methyl orange 3,1–4,4 against pH(V_eq) = 8,72, draws the band at that range, marks the endpoint at 7,77 mL and states the 17,23 mL miss. This is the masters' warned-about indicator-selection failure taught visually, not an indicator recommendation.

## 5. Reading coupling and print subdivision (A.1.3)

Each titration record carries an inset burette strip with 0,1 mL graduations, two reported decimals, a declared reading and the `N12-BURETTE-GEOM-01` reference. The validator computes the rendered subdivision from the declared 160 mm width and a 480-unit viewBox.

| Figure | Strip window (mL) | Reading (mL) | 0,1 mL subdivision (mm) | N12 floor 1,50 mm | Agrees |
|---|---|---|---|---|---|
| `FIG-T67-TITR-STRONG` | 24,50–25,10 | 25,00 | 9,47 | pass | yes |
| `FIG-T67-TITR-WEAK` | 24,60–25,20 | 24,99 | 9,47 | pass | yes |
| `FIG-T67-TITR-WRONG-IND` | 7,40–8,00 | 7,77 | 9,47 | pass | yes |
| `FIG-T67-TITR-MASTER-KMNO4` | 11,85–12,45 | 12,35 | 9,47 | pass | yes |
| `FIG-T67-TITR-PRACTICE` | 0,00–0,60 | 0,00 (start) | 9,47 | pass | yes |

The 0,1 mL strip is a vertical inset because 0,1 mL graduations across a 50 mL axis would fall below the print floor. The axis itself keeps 5 mL major ticks; the strip supplies the reading discipline the N12 contract requires.

## 6. Calibration fit and reading recompute (B.1.1)

The validator recomputes the fit from the standard points, checks the declared fit and then reads the unknown signal through the fitted line back to the concentration axis.

| Figure | Model | Standards | Recomputed slope / intercept | Reading (mg/mL) | Recomputed (mg/mL) | Inside 0–0,016 | Agrees |
|---|---|---|---|---|---|---|---|
| `FIG-T67-CAL-MASTER` | through zero | 9 | 30,39461 / 0 | 0,00849 | 0,008490 | yes | yes |
| `FIG-T67-CAL-NEAR-EDGE` | free intercept | 9 | 30,24167 / 0,001733 | 0,01549 | 0,015486 | yes (96,8 % of upper standard) | yes |
| `FIG-T67-CAL-PRACTICE` | through zero | 5 | 25,01917 / 0 | 0,01459 | 0,014588 | yes | yes |

Negative fixtures fail by id: `FIG-T67-CAL-MASTER` with reading 0,02000 fails `E_FIG_CAL_READING_OUT_OF_SPAN`; the same record with `fit_line.x_max = 0.020` fails `E_FIG_CAL_FIT_OUT_OF_SPAN`; a declared reading of 0,01000 fails `E_FIG_CAL_READING_MISMATCH`.

The rendered calibration practice draws the standards and fitted line and marks A = 0,365 on the signal axis, but draws no reading line or dot, so the 0,01459 mg/mL answer is not visible. The teaching records do draw the reading and carry `EXEMPT_READING_DISPLAY` with the reasoned value list.

## 7. V-07 assumption honesty and no-extrapolation (B.1.2, B.1.3)

Every calibration record has a four-entry `assumption_ledger`:

| Assumption | Master | Near-edge | Practice |
|---|---|---|---|
| `linear_range` | stated: 0–0,016 mg/mL, 9 standards | stated: 0–0,016 mg/mL, reading at 96,8 % | stated: 0–0,016 mg/mL, 5 standards |
| `matrix_match` | absent stated: solvent/pH not verified in the protocol | absent stated | absent stated |
| `intercept_meaning` | stated: fixed 0, blank subtracted | stated: +0,0017 is system/blank offset | stated: fixed 0 |
| `blank_correction` | stated: blank contains solvent/reagents, instrument zeroed | stated: blank subtracted before fitting | stated: blank subtracted |

The near-edge annotation is the discipline's demonstrated case: `Robeža: A = 0,470 → γ = 0,01549 mg/mL (0,968 no 0,016). Diapazonā, bet tuvu malai; ekstrapolācija nav atļauta.` It is deliberately inside the standards span and explicitly refuses extrapolation.

`data/calibration_contract.json` carries the no-extrapolation rule verbatim from `conventions.spectrophotometry.calibration.no_extrapolation_rule_lv` (`N15-NOEXTRAP-01`, text SHA-256 `ef438e4361746745c362dc6f41d9996a4824156d385c0af078f72947735d5632`), names N18 as the inheritor, and states that the span is data, the renderer clips lines/readings and validation rejects outside values. The renderer clips every fit line to 0–0,016 mg/mL and every reading is inside; the scratch over-span and wrong-reading fixtures prove the build gate bites by id.

## 8. End-to-end proof (C.1.1)

- `validate_figures`: PASS, 45 records, 13/13 T6-7 slots, 272 label checks, 95 unit checks, canonical `142,579` B, digest `b641fd113a3acac618a04da60f17d1f9c56aa5aa12b703e9b98e9bd6ac2655fe`.
- `tools/n15_corpus.py`: PASS. Model tables, V-05 table, reading coupling, calibration readings, assumption ledger, negative fixtures, leak audit, contract digests, truncation refusal and double-build parity all recorded in `evidence/N15_CORPUS_RECORD.json`.
- Determinism: Python generation twice and Python/JS parity for all three curve classes (401 points each); digests are in the corpus record. The runtime harness renders each of the 8 T67 records twice and records SVG SHA-256 values.
- Leak scan: PASS, 0 flags. Per-record outcomes: strong/weak/master/practice titration PASS; wrong-indicator EXEMPT (`EXEMPT_WORKED_DERIVATION`); calibration master and near-edge EXEMPT (`EXEMPT_READING_DISPLAY`); calibration practice PASS. A planted “20,45 mL” on the titration practice and “0,01459 mg/mL” on the calibration practice are both caught by the runtime scanner.
- Truncation: a half-truncated `data/figures_t67.json` is refused by `tools/build.py` with no artifact written; a truncated embedded `#sim-figures` island degrades with `E_FIGURES_JSON`.
- Two builds: HTML and manifest are byte-identical except the output path. `output/simulator.html` is `859,170` B, SHA-256 `e0fe9dfbcaee58360fa9730a8ac59d0e5804600d2bedebf9454b6c989a2a2550`, build id `091bd144581c0241`.
- Runtime harness: `node tools/check_n15_runtime.js` PASS, 45 figures / 8 T67, 9/9 smoke vectors including `SMK-N15-T67-TITRATION`.

## 9. Print renders (C.1.1)

Both renders use `lite-shot --cdp --media print --full-page -g 800x1100` with Falkon (no Chrome/Chromium). They are browser print-media emulations, not physical printer proofs.

| Render | Path | PNG bytes | SHA-256 | Colours | Inspection |
|---|---|---|---|---|---|
| Titration band | `evidence/N15_PRINT_TITRATION.png` | 57,118 | `db2481600264d208b704fd6fedc81ecb585cf669db6fabf295a03b66ca270555` | 1,940 | pH axis 0–14, 25,00 mL equivalence marker, dashed burette strip 24,50–25,10 with 25,00 mL meniscus, phenolphthalein label/band, both annotation lines fully inside their boxes |
| Calibration reading | `evidence/N15_PRINT_CALIBRATION.png` | 58,835 | `a901515bf2f56789266dd06992ec40e5b7b2b042db11f7bdfae780089c66e0d9` | 2,259 | x axis labels 0,000–0,018 mg/mL, 9 points, fitted line ending at 0,016, horizontal reading at A = 0,258 and vertical drop at 0,00849, V-07 and reading annotations fully inside their boxes |

The visual checks found and prompted two fixes before the recorded renders: axis labels for small x steps were rounded to one decimal (“0,0”) and long annotations overflowed the SVG width. The fixed renderer uses step-derived decimals and the annotations were shortened; the PNGs above are the post-fix artefacts.

## 10. Contracts, handoffs and budget (C.1.2, C.1.3)

| Contract | SHA-256 | Consumers | Contents |
|---|---|---|---|
| `data/titration_contract.json` | `6a99319281522c101d3618e6e2e0c99f880281ced28cf9163fda11578225117f` | N17, N18, N37 | Three model classes, V-05 wording verbatim, reading coupling, N18 field names |
| `data/calibration_contract.json` | `53bf121a156920b85b852ea7ac3faa9736fb3fbace3bb2eb136f81bd446767f8` | N18, N37 | V-07 assumption ids/states, two models, no-extrapolation rule verbatim, N18 field names |

The type registry handoff (`curve`, `scatter` + the three `titration_*` curve classes) is in the titration contract's `n37_type_registry` and in `data/figure_schema.json`'s `curve_function_registry` / `type_registry`.

Budget against Section 1's 60–140 KiB figure sub-budget and 225,280-byte runtime ceiling:

| Measure | Bytes | Ceiling | Headroom |
|---|---|---|---|
| T6-7 records, canonical | 25,858 | — | — |
| Merged figure island | 142,579 | 143,360 | 781 |
| Runtime JS code | 225,184 | 225,280 | 96 |

Phase III therefore closes at 142,579 B of the 143,360 B figure ceiling. The T6-7 figure records alone are 25,531 canonical bytes; the standalone T67 island (with its scope/records note) is 25,858 B. The merged island adds the records to the 117,045-byte N11–N14 island plus the shared envelope/owner string.

## 11. Commands actually run

```
python3 tools/validate_figures.py
python3 tools/build.py
node tools/check_n15_runtime.js
python3 tools/n15_corpus.py
node tools/check_n10_runtime.js
node tools/check_n11_runtime.js
node tools/check_n12_runtime.js
node tools/check_n13_runtime.js
node tools/check_n14_runtime.js
lite-shot --cdp --media print --full-page -g 800x1100 /tmp/opencode/n15_print_titration.html evidence/N15_PRINT_TITRATION.png
lite-shot --cdp --media print --full-page -g 800x1100 /tmp/opencode/n15_print_calibration.html evidence/N15_PRINT_CALIBRATION.png
```

## 12. Limits and open verification

- The acid–base curves are `PROPOSED` training policy; only the C6 KMnO₄/Fe²⁺ case is master-grounded. The programme does not prescribe these exact titration examples.
- V-05 wording is enforced as figure copy; it is not an official exam ruling and does not claim a universal endpoint persistence time.
- The calibration records use the master's C7 worked standards and a reparameterized practice set; they are teaching data, not new analytical measurements.
- Print renders are Falkon print-media emulations at 800×1100 CSS px with a 160 mm figure width; physical-printer, colour-blind, screen-reader and instructor acceptance remain unverified.
- The model checks prove internal consistency with the declared models, not that a real titration/spectrophotometer would reproduce these values.
