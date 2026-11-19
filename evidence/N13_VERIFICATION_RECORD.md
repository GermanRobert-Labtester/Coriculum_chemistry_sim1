# N13 Verification Record — T4 energy, Hess and Maxwell-Boltzmann figures

Date: 2026-11-17. Scope: data/figure/validator/runtime verification and Falkon render checks only. Not WCAG, instructor, scientific-expert, paper-print or product acceptance.

## 1. What was built

| Item | Path | Note |
|---|---|---|
| Curve-generation extension | `data/figure_schema.json`, `src/figure-framework.js` | `curve_function_registry`: `energy_profile_single_barrier`, `maxwell_boltzmann_3d`; new type `hess_cycle`; fail-closed `E_FIG_UNKNOWN_CURVE_CLASS` / `E_FIG_BAD_CURVE_PARAMS` |
| T4 records (10) | `data/figures_t4.json` | 4 energy-path, 4 Hess, 2 Maxwell-Boltzmann |
| Terms | `data/terms.json` | 30 `fig.*` T4 entries (260 entries total) + `inverse_molar_energy` dimension |
| Frozen contract | `data/energy_conventions_contract.json` | Handed to N16 / N17 / N18; drift-checked against `conventions.json` |
| Slot closure | `data/concept_summaries.json` | `P4-01`..`P4-11` `authored-N13` (`11/11`) |
| Validator extension | `tools/validate_figures.py` | Python curve mirror, sign / barrier / Hess / MB / V-06 checks, contract drift |
| Build wiring | `tools/build.py`, `src/shell.html`, `tools/leak_scan.py`, `tools/validate_terms.py`, `tools/validate_n07_map.py` | `--figures-t4`, `sim-energy-contract-digest` meta |
| Runtime harness / corpus | `tools/check_n13_runtime.js`, `tools/n13_corpus.py` | |

C10 naming: the roadmap's "C10" catalase item is stored as `C05` / `V-08` in `conventions.json` (`N03-OBS-01`); the figure cites `V-08 / C05 (ceļvedī minēts kā C10)`.

Verbatim honesty note on `FIG-T4-ENERGY-CATALYZED` (`c10_honesty_note_lv`):

> Katalāzes aktivācijas enerģijas kursa vērtība (23 J/mol pret iespējamo 23 kJ/mol, K10) paliek zinātniski atvērta pie kursa docētājas (V-08 / C05; ceļvedī minēts kā C10, sk. N03-OBS-01). Tāpēc šis attēls māca barjeras pazemināšanas modeli ar vispārīgu piemēru (95,0 → 35,0 kJ/mol, nemainīts ΔH = −70,0 kJ/mol), nevis strīdīgos katalāzes skaitļus.

## 2. Curve generation (A.1.1)

Registered classes with parameter ranges and `point_count` declared per record (energy: `61`, MB: `193`). Python mirror and the shipped JS produce identical points; digests per series are in `N13_CORPUS_RECORD.json` → `curve_generation.table` (10 series).

Negative fixtures (scratch copies, never written to `data/`): unknown function class → `E_FIG_UNKNOWN_CURVE_CLASS` on `FIG-T4-ENERGY-EXOTHERMIC`; `E_ts <= E_r` → `E_FIG_BAD_CURVE_PARAMS` on `FIG-T4-ENERGY-EXOTHERMIC`. Runtime also rejects `Ea >= E_max` for MB.

## 3. Sign fidelity and coverage (A.1.2)

Independent recompute `ΔH = E_p − E_r` (convention `ΔH = H(produkti) − H(izejvielas)`), `Ea_fwd = E_ts − E_r`, `Ea_rev = E_ts − E_p`:

| Figure | Class | Recomputed ΔH | Declared | Ea fwd / rev (kJ/mol) | Agrees |
|---|---|---|---|---|---|
| `FIG-T4-ENERGY-EXOTHERMIC` | exothermic | −70.0 | −70.0 | 55.0 / 125.0 | yes |
| `FIG-T4-ENERGY-ENDOTHERMIC` | endothermic | 55.0 | +55.0 | 95.0 / 40.0 | yes |
| `FIG-T4-ENERGY-CATALYZED` | exothermic (catalyzed pair) | −70.0 | −70.0 | 95.0 / 165.0 (cat Ea 35.0) | yes |
| `FIG-T4-ENERGY-GRADE-READING` | gradeable readout | not labelled (targets only in `answer_targets`) | — | — | n/a |

Scratch sign flip (`declared_delta_h = +70.0` on exothermic) fails with `E_FIG_ENTHALPY_SIGN_MISMATCH` on `FIG-T4-ENERGY-EXOTHERMIC`. Case coverage: exothermic with lower forward barrier, endothermic, catalyzed pair (barrier lowered, ΔH unchanged) all authored.

## 4. Hess cycles (B.1.1)

| Figure | Step sum (kJ/mol) | Direct | Closes | Reverse trap |
|---|---|---|---|---|
| `FIG-T4-HESS-FECL3` (`#fig-hess`) | −399.5 | −399.5 | yes | no |
| `FIG-T4-HESS-CO2` (`#sec-ch5-27`) | −393.5 | −393.5 | yes | no |
| `FIG-T4-HESS-REVERSE-TRAP` | −124.0 (−2343.8 + 2219.8) | −124.0 | yes | yes |
| `FIG-T4-HESS-PRACTICE-SYNTH` | −219.0 | withheld (`null`) | n/a | no |

Scratch unbalanced cycle (`FIG-T4-HESS-FECL3` direct set to −350.0) fails with `E_FIG_HESS_UNBALANCED`.

## 5. Maxwell-Boltzmann honesty (B.1.2)

| Figure | T1 → T2 (K) | Peak x (kJ/mol) | Peak y | Normalization (trapezoid + exact tail) | Tail ≥ Ea | Ratio |
|---|---|---|---|---|---|---|
| `FIG-T4-MB-TWO-TEMP-COMPARE` (Ea 8.0) | 300 → 600 | 1.2471 → 2.4942 | 0.194027 → 0.097013 | 0.99738 / 0.99907 | 0.09308 → 0.360734 | 3.8755 |
| `FIG-T4-MB-BARRIER-SCOPE` (Ea 10.0) | 300 → 450 | 1.2471 → 1.87065 | 0.194027 → 0.129351 | 0.99738 / 0.99857 | 0.045629 → 0.148162 | 3.2471 |

Peak shifts right and flattens; rendered SVG `data-tail-start-x` equals `data-threshold-x` for both series of both figures. Scratch exaggerated claim (`tail_ratio = 12.5`) fails with `E_FIG_MB_HONESTY`. Chosen temperatures and Ea (instead of 300 → 310 K at Ea 50) keep the tail visible on a linear axis without any exaggeration of the curve.

## 6. Labels, citations, scope (A.1.3, B.1.3)

`154` label checks and `49` unit checks pass through the N10 grammar; anchors resolve case-exact (`fig-profiles`, `fig-catalysis`, `fig-hess`, `sec-ch5-27`, `fig-maxwell`). Every T4 record has a V-06 scope note; `E_FIG_SCOPE_OVERGENERALIZATION` lint passes on all 10 (scratch "universāls slieksnis visām reakcijām" fails on `FIG-T4-MB-TWO-TEMP-COMPARE`). Scratch broken anchor fails with `E_FIG_BROKEN_ANCHOR` on `FIG-T4-ENERGY-EXOTHERMIC`.

## 7. End-to-end (C.1.1)

- `validate_figures`: `records=29, slots_closed=N11:18/18+N12:12/12+N13:11/11`.
- Leak scan: `figures=29 (gradeable=4, exempt=7), flags=0`. `FIG-T4-HESS-PRACTICE-SYNTH` is clean without exemption (`direct_path.dh_kj_mol` is `null`; −219.0 only in `answer_targets`); planted `−219,0 kJ/mol` label is caught. `FIG-T4-ENERGY-GRADE-READING` is clean (level coordinates in `params`, targets in `answer_targets`).
- Runtime (`tools/check_n13_runtime.js`): 0 `<svg>` before drawer open, lazy render in `P4-01` (2), `P4-03` (4), `P4-06` (3), `P5-01` stays `pending-N14` (0), two-run determinism and 0 raw colours for 10 records, truncated `#sim-figures` → `E_FIGURES_JSON` banner, smoke `7/7` incl. `SMK-N13-T4-HESS-CURVE`.
- Regression: `check_n10_runtime.js`, `check_n11_runtime.js`, `check_n12_runtime.js` pass (assertions updated for the 29-figure store, `P5-01` as the pending slot, smoke total `>= 6`).
- Build-gate refusal on an invalid T4 file does not write the artifact; fresh build is byte-identical to `output/simulator.html`.

## 8. Render checks (Falkon `lite-shot --cdp`, inspected)

Light, dark and `--media print --full-page` PNGs: `evidence/N13_PAINT_DRAWER_LIGHT.png` (`1400x1200`, 9,065 colours), `…_DARK.png` (8,431 colours), `N13_PAINT_PRINT.png` (`1179x3705`, 5,226 colours). Print page is a scratch page that places six T4 figures (both MB figures, catalyzed, exothermic, reverse-trap, FeCl₃ Hess) in the print theme; it was deleted afterwards, so the print check covers the print stylesheet and print theme on screen, not a physical sheet. Observed: two MB curves, dashed threshold line and shaded tail visible in monochrome (grey shading + dash patterns); arrows, signs and labels readable. First capture showed clipped annotation text; annotation copy was shortened and the Hess step labels wrapped, then recaptured. Not assessed: assistive technology, real printer output.

## 9. Budgets

| Quantity | Measured | Ceiling |
|---|---|---|
| `runtime_js_code_bytes` | 224,646 | 225,280 (634 B headroom) |
| `#sim-figures` canonical | 87,163 | 143,360 (60.8 %) |
| T4 records canonical | 33,431 | 23.32 % of the figure ceiling |
| `src/figure-framework.js` | 48,182 | — |

To fit the JS ceiling, indentation and line breaks in `src/figure-framework.js` and `src/smoke-subset.js` were compacted (whitespace only; N11/N12 runtime harnesses still pass). **Risk:** only 634 B of runtime JS headroom remain for N14 and N15; they will need a code-size plan.

## 10. Handoff

`data/energy_conventions_contract.json` (canonical sha256 `d499f1350c87f98fbbf64076007686469be2010c7e91fddea1111acc3710219e`) fixes the sign rule `ΔH = H(produkti) − H(izejvielas)`, barrier identity `ΔH = Ea,tiešā − Ea,pretējā`, Hess step-direction rule, Unicode-minus / decimal-comma format, energy tolerance `1.0 kJ/mol` and temperature tolerance `0.5 K` (both PROPOSED policy from `conventions.json`), and `sign_error_fatal`. It binds figure labels, N16 chain arithmetic and N17/N18 grading to the same conventions entries.

## 11. Verification runs

`python3 tools/build.py` (gates 1–11 PASS), `validate_terms.py`, `validate_n06_shell.py` (`js_code=224646B`), `validate_figures.py`, `leak_scan.py`, `check_n10/11/12/13_runtime.js`, `tools/n13_corpus.py` ×2 (byte-identical `N13_CORPUS_RECORD.json`, sha256 `661b570580e9f62e7f1fa0461f8204c7e0bce7f13ee1a7d646945f27548c1604`), `python3 tools/verify_preparation.py` (`status: PASS`).
