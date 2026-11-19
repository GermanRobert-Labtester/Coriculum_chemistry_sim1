# N14 Verification Record — Topic 5 kinetics figures and linearization tolerance fields

Date: 2026-11-17. Scope: authoring-data, validator, runtime, Falkon render and evidence verification in this workspace. Not instructor, scientific-expert, physical-print or accessibility acceptance.

## 1. What was built

| Item | Path | Note |
|---|---|---|
| T5 records (8) | `data/figures_t5.json` | Zero/first/second decay, catalyst comparison, three linearizations, one gradeable practice plot |
| Kinetics conventions | `data/conventions.json` | `kinetics` section, `LN2`, six tolerance classes (`time`, `rate_constant_zero/first/second`, `inverse_concentration`, `log_concentration_ratio`) |
| Frozen interface | `data/kinetics_linearization_contract.json` | Tolerance vocabulary, span/edge rule, `evaluateFitLine`, N20 reparameterization ranges |
| Schema extension | `data/figure_schema.json` | `kinetics_decay` curve class, `kinetics_linearization_fields`, scatter fit-line/span support |
| Renderer | `src/figure-framework.js` | `kinetics_decay`, clipped fit line, tolerance band, half-life marker, `evaluateFitLine`, dataset-table companion |
| Terms | `data/terms.json` | 28 T5 `fig.*` entries; `inverse_concentration` dimension |
| Slot closure | `data/concept_summaries.json` | `P5-01`–`P5-05`, `P5-07`–`P5-10` `authored-N14` (9/10); `P5-06` handed to N16 |
| Validator | `tools/validate_figures.py` | Transform, half-life, tolerance, span, notation, slot and contract checks |
| Build wiring | `tools/build.py`, `src/shell.html` | `--figures-t5`, `sim-kinetics-contract-digest`, merged `#sim-figures` |
| Smoke | `src/smoke-subset.js` | `SMK-N14-T5-LINEARIZATION` (8/8 total) |
| Runtime harness / corpus | `tools/check_n14_runtime.js`, `tools/n14_corpus.py` | |

`P5-04` closes through the existing N13 Maxwell–Boltzmann record (`FIG-T4-MB-TWO-TEMP-COMPARE`); `P5-07` through the existing N13 catalyzed energy profile. Cross-referenced concept IDs were added to those two N13 records.

## 2. Records

| Figure | Type | Dataset | Transform | Slope (authored) | Intercept (authored) |
|---|---|---|---|---|---|
| `FIG-T5-DECAY-ZERO` | curve | C₀ 1,00 mol/L, k 0,0200 mol/(L·s), 0–40 s | C = C₀ − kt | — | — |
| `FIG-T5-DECAY-FIRST` | curve | C₀ 1,00 mol/L, k 0,0500 s⁻¹, 0–30 s | ln(C/C₀) = −kt | — | — |
| `FIG-T5-DECAY-SECOND` | curve | C₀ 1,00 mol/L, k 0,0400 L/(mol·s), 0–30 s | 1/C = 1/C₀ + kt | — | — |
| `FIG-T5-DECAY-CATALYST` | curve | k 0,0250 → 0,0750 s⁻¹ | first-order pair | — | — |
| `FIG-T5-LIN-ZERO` | scatter | paired with decay-zero | C vs t | −0,0200 mol/(L·s) | 1,00 mol/L |
| `FIG-T5-LIN-FIRST` | scatter | paired with decay-first | ln(C/C₀) vs t | −0,0500 s⁻¹ | 0,00 |
| `FIG-T5-LIN-SECOND` | scatter | paired with decay-second | 1/C vs t | +0,0400 L/(mol·s) | 1,00 L/mol |
| `FIG-T5-LIN-PRACTICE` | scatter | own synthetic first-order dataset (k withheld) | ln(C/C₀) vs t | withheld in `answer_targets` / `grading_reference` | withheld |

All datasets are synthetic training data labelled `PROPOSED`; no official measurement is claimed. The practice record renders data points only — no fit line and no tolerance band — so the answer key is not visible. Its `grading_reference` is excluded from the leak scan by the same rule as `answer_targets`.

## 3. Transform consistency (A.1.1)

`tools/validate_figures.py` recomputes slope and intercept from the paired decay record's `order`, `C0_mol_l`, `k` and span:

| Figure | Paired decay | Order | Recomputed slope | Authored slope | Recomputed intercept | Authored intercept | Agrees |
|---|---|---|---|---|---|---|---|
| `FIG-T5-LIN-ZERO` | `FIG-T5-DECAY-ZERO` | 0 | −0,0200 | −0,0200 | 1,00 | 1,00 | yes |
| `FIG-T5-LIN-FIRST` | `FIG-T5-DECAY-FIRST` | 1 | −0,0500 | −0,0500 | 0 | 0,00 | yes |
| `FIG-T5-LIN-SECOND` | `FIG-T5-DECAY-SECOND` | 2 | 0,0400 | 0,0400 | 1 | 1,00 | yes |
| `FIG-T5-LIN-PRACTICE` | none (own dataset) | 1 | −0,0800 | −0,0800 | 0 | 0,00 | yes |

Scratch fixture: setting `FIG-T5-LIN-FIRST.fit_line.slope = −0.0600` fails with `[E_FIG_TRANSFORM_INCONSISTENT]` on `FIG-T5-LIN-FIRST`.

Half-life check: `FIG-T5-DECAY-FIRST` recomputes `t½ = ln2/k = 0.693147…/0.0500 = 13.862944 s`, authored display `13,9 s`; zero and second order recompute `25,0 s`. All rows agree.

Dataset tables and transformed point lists are recomputed row-by-row under `Decimal` half-up rounding; a mismatch fails `[E_FIG_KINETICS_DATASET]` / `[E_FIG_KINETICS_POINT]`.

## 4. Tolerance coupling (A.1.2)

Every linearization record carries three coupled fields: `slope`, `intercept`, `point_acceptance`. Each names a `conventions.json` class, a `tolerance_mode` and its parameter.

| Figure | Slope class / mode / value | Intercept class / mode / value | Point class / mode / value | Rendered line inside own tolerance |
|---|---|---|---|---|
| `FIG-T5-LIN-ZERO` | `rate_constant_zero` / significant_figures / 0,0005 | `concentration_molar` / absolute / 0,01 | `concentration_molar` / absolute / 0,01 | yes |
| `FIG-T5-LIN-FIRST` | `rate_constant_first` / significant_figures / 0,0005 | `log_concentration_ratio` / absolute / 0,02 | `log_concentration_ratio` / absolute / 0,02 | yes |
| `FIG-T5-LIN-SECOND` | `rate_constant_second` / significant_figures / 0,0005 | `inverse_concentration` / absolute / 0,05 | `inverse_concentration` / absolute / 0,05 | yes |
| `FIG-T5-LIN-PRACTICE` | `rate_constant_first` / significant_figures / 0,0005 | `log_concentration_ratio` / absolute / 0,02 | `log_concentration_ratio` / absolute / 0,02 | n/a (answer line not rendered) |

The validator resolves both conventions modes. `significant_figures` uses half a unit in the last declared digit of the expected value; `absolute` uses the class value. For each teaching linearization the rendered fit line is compared with the true line over the declared span: slope difference, intercept difference and maximum point deviation are all zero, so every figure satisfies its own grading rule.

Scratch fixtures: an unknown class fails `[E_FIG_UNKNOWN_TOLERANCE_CLASS]`; a line changed to slope `−0.0600` fails `[E_FIG_TOLERANCE_SELF_VIOLATION]` on `FIG-T5-LIN-FIRST`.

## 5. Labels, notation and number format (A.1.3)

- Log axis term `fig.axis.ln_concentration_ratio` = “Logaritmiskā attiecība ln(c/c₀)”, with no fabricated unit (dimensionless ratio). The declared notation rule is cited to `CIT-C5-INTEGRATED` / `CIT-C5-KUNITS`.
- Inverse axis term `fig.axis.inverse_concentration_l_mol` uses the grammar-checked unit `L/mol` (`inverse_concentration` dimension).
- Time axis reuses `fig.axis.time_s` (`s`); concentration axes reuse `fig.axis.concentration_mol_l`.
- All T5 display copy uses decimal commas; a dot-decimal in T5 subtitle/description/annotation copy fails `[E_FIG_DECIMAL_COMMA]`.
- Report: 216 label checks, 71 unit checks, no log/inverse/decimal failures.

## 6. Span rule and render clipping (B.1.1)

Each linearization declares `span.x_min`, `span.x_max`, `span.data_x_min`, `span.data_x_max`, `edge_rule = "inclusive"` and `beyond_span = "not_assessed"`. The fit line is drawn only between `x_min` and `x_max`; the renderer clips any longer line. Validation asserts the rendered extent equals the declared span.

| Figure | Span (s) | Data span (s) | Rendered extent matches | Edge rule |
|---|---|---|---|---|
| `FIG-T5-LIN-ZERO` | 0–40 | 0–40 | yes | inclusive |
| `FIG-T5-LIN-FIRST` | 0–30 | 0–30 | yes | inclusive |
| `FIG-T5-LIN-SECOND` | 0–30 | 0–30 | yes | inclusive |
| `FIG-T5-LIN-PRACTICE` | 0–20 | 0–20 | yes | inclusive |

Scratch fixture: `FIG-T5-LIN-FIRST` with `span.x_max = 45` and `fit_line.x_max = 45` fails `[E_FIG_SPAN_EXCEEDS_DATA]` by id.

## 7. N18 drawn-line preview (B.1.2)

`SimFigures.evaluateFitLine(record, {slope, intercept, x_min, x_max})` was run against `FIG-T5-LIN-FIRST` (true slope −0,05 s⁻¹, intercept 0, span 0–30 s):

| Case | Drawn line | Assessed range | Result |
|---|---|---|---|
| Inside | slope −0,0502, intercept 0,005, x 0–30 | 0–30 | `ACCEPTED`; slope/intercept/point all true |
| Edge inclusive | slope −0,0500, intercept 0, x 0–30 | 0–30 | `ACCEPTED`; both edges included |
| Beyond | slope −0,0502, intercept 0,005, x 0–95 | 0–30 | `ACCEPTED`; `beyond_span = not_assessed` |
| Far line | slope −0,08, intercept 0,2, x 0–30 | 0–30 | `REJECTED`; slope, intercept and point checks false |

A scratch copy of the record with a learner line extending to 95 s was rendered on the same axes: the drawn line is clipped at 30 s and carries `data-drawn-beyond="not_assessed"`. The beyond-span geometry is neither accepted nor rejected; it is excluded from assessment. This is the frozen runtime behaviour N18 inherits.

## 8. Teaching trace (B.1.3)

| Step | Action | Arithmetic | Result |
|---|---|---|---|
| 1 | Open `FIG-T5-DECAY-FIRST` | C₀ = 1,00 mol/L, k = 0,0500 s⁻¹, t½ = 13,9 s | first-order decay and half-life |
| 2 | Open `FIG-T5-LIN-FIRST` | slope = −0,0500 s⁻¹, intercept = 0,00 | the same dataset linearized |
| 3 | Recompute k | k = −slope = −(−0,0500) = 0,0500 s⁻¹ | matches the decay annotation |
| 4 | Recompute t½ | t½ = ln2/k = 0,6931/0,0500 = 13,8629 s → display 13,9 s | matches the decay annotation |

The trace teaches exactly the arithmetic N16's chains will show and N18 will grade.

## 9. End-to-end proof (C.1.1)

- `validate_figures`: PASS, `records=37`, `t5_transforms=4`, `t5_tol=4`, `t5_span=4`, `N14:9/10` slots (P5-06 handed to N16).
- Curve determinism: Python twice and Python/JS parity for all three decay classes; points digests in `N14_CORPUS_RECORD.json` → `curve_determinism`.
- Leak scan: 37 figures scanned, 0 flags. T5 per-record outcomes all PASS. The practice record is clean; a planted annotation “Slīpums = −0,0800 s⁻¹; k = 0,0800 s⁻¹; t½ = 8,66 s” is caught. The seven exemptions are inherited N11/N12 reading-display/worked-derivation figures, not T5.
- Truncation: damaged `#sim-figures` still yields `E_FIGURES_JSON` and the visible error banner.
- Build gate: an inconsistent scratch T5 file refuses the build and writes no artifact.
- Two builds are byte-identical (`build_id = 05f89f37553bc723`, output SHA-256 `d3e5fe0cf0147f69d91004ddf42b8dd39cc838aaa10f1fe79a982f64f30324d8`).
- `check_n14_runtime`: 37 figures, 8 T5, fit clipping, drawn-line cases, practice leak, truncation, smoke `8/8`.

## 10. Print and render checks (Falkon `lite-shot --cdp`, inspected)

| Capture | Geometry | Colours | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| `N14_PAINT_DRAWER_LIGHT.png` | 1400×1600 | 10,111 | 216,238 | `cdaeb3d5ec3fe8b59ed32cae2083db5b781692bd797d1d09cf2b204411040de1` |
| `N14_PAINT_DRAWER_DARK.png` | 1400×1600 | 10,099 | 216,991 | `8becc5490e414887b68a9240237f5d1d9b0fe913a3f48205f6c1592af61d50cd` |
| `N14_PAINT_PRINT.png` | 1000×1400 | 4,983 | 114,277 | `780088f7a7451c407dafd86f46e20630e83d89023501b788ff9bb2c4da36da0c` |

The drawer captures show `P5-09` with four linearization figures: axis labels, fit line, data points and all three annotation rows are visible in light and dark themes. The print capture is a scratch page containing `FIG-T5-LIN-FIRST`, its caption and its dataset table under `--media print`: the log axis, `ln(c/c₀)` label, ticks, slope/intercept annotation, span note and synthetic-data note are legible at the print size. This is screen emulation of print CSS, not a physical sheet.

Observed defects corrected during verification: the log-axis term was shortened because the long wording clipped on the vertical axis; annotation boxes were shifted upward and the plot height reduced so three annotation rows no longer overlap the x-axis label; the practice axis step was changed so a tick label could not coincidentally round to the withheld slope.

## 11. Budgets

| Quantity | Measured | Ceiling |
|---|---:|---:|
| `runtime_js_code_bytes` | 217,384 | 225,280 (7,896 B headroom) |
| `#sim-figures` canonical | 117,045 | 143,360 (81.64 %) |
| T5 records canonical | 30,294 | 21.13 % of the figure ceiling |
| `output/simulator.html` | 811,910 | 700–1400 KiB declared |
| `src/figure-framework.js` | 48,899 | — |

The N14 additions fitted after whitespace/comment compaction of `figure-framework.js`, `smoke-subset.js`, `concept-drawer.js` and `hint-drawer.js`; no behaviour changed and all prior harnesses pass.

## 12. Handoff (C.1.2)

`data/kinetics_linearization_contract.json` (canonical SHA-256 `50f9ee2b596f6d28e4d828c1abf1276fe902517b82b0397338fc74ca2f2abc5d`; file SHA-256 `2c264aa8a4e2ef204a268b459aeac601a410a44de02c4739b94039435ec55ddc`) freezes:

- the tolerance-field vocabulary (`slope`, `intercept`, `point_acceptance`; class, mode, value, conventions ref, unit, meaning);
- the span rule `N14-SPAN-01` (inclusive edges, beyond-span not assessed, fit line never exceeds data span);
- the `SimFigures.evaluateFitLine` input/output names — consumed by name by N18;
- the N20 reparameterization ranges (C₀ 0,10–2,00 mol/L; k order 0: 0,0050–0,0500 mol/(L·s); order 1: 0,0100–0,1500 s⁻¹; order 2: 0,0100–0,1000 L/(mol·s); span 10–60 s; 6–15 dataset points; tolerance fields inherited verbatim).

N16 consumes the datasets and derives its chains from them; N18 consumes the tolerance fields and `evaluateFitLine`; N20 may reparameterize only inside the declared ranges.

## 13. Golden-vector re-freeze note

Adding `kinetics`, `LN2` and six tolerance classes to `data/conventions.json` changed the conventions digest. The N05 corpus was re-frozen from `corpus_version 1.0.0` to `1.1.0`: every expected verdict was recomputed with `tools/golden_oracle.py` and all 40 active vectors were verified to have **zero semantic changes** (same verdict, error class, criteria and points); only the `conventions_digest` field changed from `6763f5f3…a77c7bd` to `a815d776…c1120e`. This is recorded in `N14_CORPUS_RECORD.json` → `golden_vectors_refreeze`.

## 14. Verification runs

`python3 tools/build.py` (gates 1–11 PASS, `build_id=05f89f37553bc723`), `python3 tools/validate_figures.py` (PASS), `python3 tools/validate_conventions.py` (PASS), `python3 tools/validate_terms.py` (PASS), `python3 tools/validate_golden_vectors.py` (PASS), `node tools/check_n10_runtime.js`, `check_n11_runtime.js`, `check_n12_runtime.js`, `check_n13_runtime.js`, `check_n14_runtime.js` (PASS), `python3 tools/n14_corpus.py` ×2 (byte-identical `N14_CORPUS_RECORD.json`, SHA-256 `7413ba30336d7fc16c358afb97659f7ebfc7abdce3b4d33c208fea59b5c7bdcd`), `python3 tools/verify_preparation.py` (PASS), `python3 tools/verify_preparation.py --repo-local` (PASS).

## 15. Limitations

- Synthetic datasets are teaching data; the slopes/intercepts are not official measurements and carry `PROPOSED`.
- Player/learner drawing input is not implemented here; the preview freezes the acceptance interface, not the N18 UI.
- `P5-06` (multi-step mechanism / rate-determining step) is intentionally left to N16 because it is not a linearization figure.
- Print verification is CSS media emulation on screen; no physical printer, colour-blind, WCAG or instructor acceptance is claimed.
- The 4,983-colour print capture is a greyscale-legible token render, not a proof of physical print quality.
