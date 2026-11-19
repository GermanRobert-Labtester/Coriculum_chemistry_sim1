# N17 verification record — quantity, conservation and error-taxonomy engines

**Status: VERIFIED for the declared scope (2026-11-17).** This record states exactly what was authored, which checks ran and what they proved. It is an engine/data verification, not a browser, accessibility, scientific-acceptance or instructor sign-off claim.

## 1. Artifacts

| Kind | Path | Role |
|---|---|---|
| Frozen contract + taxonomy + vectors | `data/engine_taxonomy.json` | island `#sim-engines`, 4 error classes, precedence rule, plausibility/domain rules, conservation rules, S2-N17 vectors |
| Python authoring twin | `tools/quantity_engine.py` | dimensioned value, unit algebra ledger, dimension gate, conservation checker, four-class classifier, oracle-shaped verdicts |
| JavaScript runtime twin | `src/quantity-engine.js` | same logic, `SimEngines`, consuming the shipped islands |
| Build gate | `tools/validate_engines.py` | gate 13 `engines` in `tools/build.py` |
| Runtime harness | `tools/check_n17_runtime.js` | shipped islands + source module, 40+20 verdicts, smoke vector, two-run parity |
| Corpus runner | `tools/n17_corpus.py` | recompute tables, cross-language digests, scratch negatives, throughput, budget, evidence |
| Evidence | `evidence/N17_VALIDATION_RECORD.json`, `evidence/N17_CORPUS_RECORD.json`, this record | machine + human-readable proof |
| Term-island extension | `data/terms.json` (+4 `feedback.error.*` keys) | one resolving Latvian feedback string per error class; no-blame lint passes |

Digests (canonical): taxonomy/island `503d74683f495b906c97ec99b73693aba5b65a073e0c2a52d2e676d0b8714a14`; conventions `a815d77696bfe5d6820f25dc7564035980927338b183346346f0d635cec1120e`; Python engine `c71872e1b933652784904a9705f4750bdbf1ff2be5498a7ed30504f3733c010f`; JS engine `2baa84054eafa401969e94aaf57a2ec7ff6c5bdb0a7cdf47852fcc573f95ed12`; frozen corpus `27b0a0d2e5fac091160bbf7163f05ae935052e38ba5af728f390de09213eca88`.

## 2. A.1 — value type, gate and golden alignment

**A.1.1 — no local constants, conventions consumption.** The engine declares no atomic mass, molar mass, constant or conversion factor. Every declared path (`unit_system.conversions`, `unit_system.chains`, `atomic_masses`, `compound_molar_masses`, `constants`, `tolerances.quantity_classes`, `rounding`, `concentration_bases`, `percentage_basis`, `density`) resolves at load time; the built artifact's conventions digest equals the frozen corpus digest. The build-time token/AST scan over both engine sources returns **PASS with zero findings**. The value type records every operation in an internal ledger (`operation`, `inputs`, `outputs`); addition requires equal dimension vectors, multiplication combines them, division subtracts them, and conversion applies only a conventions-declared factor/offset after a dimension-vector equality check.

**A.1.2 — V-04 corpus (7/7).** Each historical defect form fails with `DIMENSIONAL_INCONSISTENCY` and mapped feedback `MC-3B-01`; both scratch valid conversions pass.

| Form | Input → target | Result | Class |
|---|---|---|---|
| V04-01 | mg → L | blocked | DIMENSIONAL_INCONSISTENCY |
| V04-02 | L → mg | blocked | DIMENSIONAL_INCONSISTENCY |
| V04-03 | g → mL (no ρ) | dimension mismatch | DIMENSIONAL_INCONSISTENCY |
| V04-04 | kg → L (prefixed) | dimension mismatch | DIMENSIONAL_INCONSISTENCY |
| V04-05 | mg → cm³ (reordered) | dimension mismatch | DIMENSIONAL_INCONSISTENCY |
| V04-VALID-01 | mg/L → g/L | factor 1/1000 | NONE |
| V04-VALID-02 | g/mL → kg/L | factor 1 | NONE |

**A.1.3 — frozen corpus alignment (40/40).** `tools/validate_engines.py` replayed all 40 active N05 vectors through the Python twin: **40 verdict-for-verdict matches, 0 failures** (12 numeric Q01/Q02/Q09/Q10, 6 graph Q12, plus the structural families needed by later consumers). A scratch convention regression (mass tolerance changed to `999` in a temporary copy) made the gate **FAIL by vector id** (`GV-S1-T1-Q02-02`), proving the alignment check bites.

## 3. B.1 — conservation and the four-class taxonomy

**B.1.1 — conservation (4/4 + scratch).** Mass-in equals mass-out against `tolerances.quantity_classes[id=mass].absolute.value = 0,01 g`; mole accounting uses stoichiometric extents `nᵢ/νᵢ` with the declared 0.001 relative bound (species with `ν = null`, e.g. solvent, are outside the reaction extent).

| Vector | Result |
|---|---|
| EV-N17-CONS-01 (Mg + ½O₂ → MgO) | BALANCED (Δm = 0, Δξ = 0) |
| EV-N17-CONS-02 (dilution) | BALANCED (Δm = 0, Δξ = 0) |
| EV-N17-CONS-03 (one mass dropped) | IMBALANCED (signature `MC-1C-01`) |
| EV-N17-CONS-04 (stoichiometry broken) | IMBALANCED (Δξ = 0,2) |
| EV-N17-CONS-SCRATCH (one wrong intermediate) | IMBALANCED by id |

**B.1.2 — completeness corpus (9/9) and precedence.** At least one member per class plus a boundary and an ambiguous member.

| Vector | Input shape | Class | Signature |
|---|---|---|---|
| CLS-01 | `1,2,3` | UNREADABLE_INPUT | MC-2B-02 |
| CLS-02 | `furlong/L` | UNREADABLE_INPUT | MC-2B-02 |
| CLS-03 | mg → L | DIMENSIONAL_INCONSISTENCY | MC-3B-01 |
| CLS-04 | −1,5 g/L | PHYSICALLY_IMPLAUSIBLE | MC-3A-02 |
| CLS-05 | pH 14,7 | PHYSICALLY_IMPLAUSIBLE | MC-3A-02 |
| CLS-06 | 0,020 outside 0–0,016 | OUT_OF_DOMAIN | MC-7B-02 |
| CLS-07 | 0,016 exactly on edge | NONE (inclusive) | NONE |
| CLS-08 | `abc` **and** mg → L | UNREADABLE_INPUT | MC-2B-02 |
| CLS-09 | 17,2 mg/L → g/L | NONE | NONE |

Verbatim precedence rule: *"Ja viens ievads atbilst vairākām klasēm, izvēlas mazāko kārtas numuru: 1 (neizlasāms) pirms 2 (dimensijas) pirms 3 (fiziskā jēga) pirms 4 (domēns). Pirmā atrastā klase aptur turpmāku pārbaudi; katrs gadījums iegūst tieši vienu klasi."* The ambiguous member CLS-08 trace is `['UNREADABLE_INPUT']` — the dimension check never runs. Plausibility bounds are data in `#sim-engines`, each with a `source` path and a conventions citation (`CIT-C3-C`, `CIT-C2-UNITS`, `CIT-C2-BURETTE-READ`, `CIT-C6-EPRIME`, `CIT-C3-PERCENT`); none is an engine constant. Boundaries are inclusive, inheriting the N14 edge rule and the N15 no-extrapolation wording from `calibration_contract.json`.

**B.1.3 — signature alignment (4/4, zero dangling).**

| Class | Signature (present in frozen corpus) | Feedback key (resolves in `#sim-terms`) |
|---|---|---|
| UNREADABLE_INPUT | MC-2B-02 | feedback.error.unreadable |
| DIMENSIONAL_INCONSISTENCY | MC-3B-01 | feedback.error.dimensional |
| PHYSICALLY_IMPLAUSIBLE | MC-3A-02 | feedback.error.implausible |
| OUT_OF_DOMAIN | MC-7B-02 | feedback.error.out_of_domain |

End-to-end trace (class two): `17,2 mg → L` → blocked conversion → `DIMENSIONAL_INCONSISTENCY` / `MC-3B-01` → term key `feedback.error.dimensional` → *"Vienību algebra neslēdzas: masa un tilpums nav savstarpēji pārrēķināmi bez deklarēta blīvuma ρ."* Each mapped string names the violated rule and never addresses the learner. **Honest dependency gap:** the full N09 registry is not present in this workspace; the taxonomy uses the N04-declared stub signature pattern and signatures already present in the frozen N05 corpus. This is recorded in the artifact (`handoff.n09_gap_notice`) rather than claimed as N09 closure.

## 4. C.1 — cross-language binding, budget and closure

**C.1.1 — cross-language harness.** Python and JavaScript twins were run over the same 40 golden vectors and the same 20 stratum vectors against the shipped islands. All four compared digests are equal:

| Digest | Both twins |
|---|---|
| golden verdicts | `f33911b0990976ad0a6c17672c9545f6ec772da8008306411d6bcf65fc8b6c5f` |
| N17 stratum verdicts | `5f5055b6d0ac369e0f2d6b1d6ed19e1e72ba739eb9b6fa473b3916d84b0e96b3` |
| shipped taxonomy island | `503d74683f495b906c97ec99b73693aba5b65a073e0c2a52d2e676d0b8714a14` |
| engine source | `2baa84054eafa401969e94aaf57a2ec7ff6c5bdb0a7cdf47852fcc573f95ed12` |

Both harness runs are internally two-run identical (`parity: true`); the corpus replay is also two-run identical (`corpus_parity: true`) and the gate report is two-run identical (`validation_parity: true`).

**C.1.2 — budget, throughput and smoke.** Runtime JS code `225 197 B` against the declared `225 280 B` ceiling — **83 B headroom**. The compiled engine is `29 975 B` (source `31 619 B`) and the taxonomy island is `12 814 B`; the artifact is `952 276 B`, inside the 700–1400 KiB total budget. Because the engine cannot be inlined without breaking the frozen JavaScript sub-budget, it ships as a validated source module with its frozen island; the runtime harness loads it directly and N31 must lazy-load or re-budget before inlining. This is a recorded constraint, not a silent budget override. Parse-cost note: 1000 synthetic classifications in `35,202 ms` (~28 407/s) on the authoring host, inside the declared 2000 ms bound; explicitly **not** a reference-device acceptance claim. Smoke vector `SMK-N17-CLASSIFICATION` passes with digest `d1c5027bf952ccf126a044dc2804e557de7245da20581388218e65749dd17127`; it is registered in the runtime harness (the artifact smoke subset could not be extended within the 83 B headroom) and the deviation is recorded here.

**C.1.3 — frozen contract.** `data/engine_taxonomy.json` freezes the API (`quantity`, `convert`, `add`, `multiply`, `divide`, `dimensionGate`, `grade`, `checkConservation`, `classify`, `feedback`), the four error classes and their signatures, the verbatim dimension-gate, precedence and boundary rules, the conventions paths, and the handoff to N18/N20/N22/N23/N31. Its digest is entered above and in the ledger.

## 5. Commands actually run

```
python3 tools/validate_engines.py --report evidence/N17_VALIDATION_RECORD.json
python3 tools/build.py                         # gates 1-13, incl. engines
node tools/check_n17_runtime.js
python3 tools/n17_corpus.py                    # writes evidence/N17_CORPUS_RECORD.json
python3 tools/verify_preparation.py --report evidence/PREPARATION_VERIFICATION.json
python3 tools/n16_corpus.py --skip-print       # N16 zero-regression: 50/50, 0+0 leaks
```

## 6. Boundaries

No engine-level tolerance decisions (all from the conventions island); no free-text formula parsing (the N19 self-assessment path stays unparsed); no error text authored in the engine (all from `#sim-terms`); no persist/reveal state introduced; no official-exam, grade or proctoring claim. The golden vectors are untouched (append-only protocol honoured; S2-N17 vectors live in the engine taxonomy, not by editing S1). Rollback: the engines are additive modules; removal leaves numeric inputs without an authority and N18/N20/N22/N23 without their foundation, as the roadmap states.
