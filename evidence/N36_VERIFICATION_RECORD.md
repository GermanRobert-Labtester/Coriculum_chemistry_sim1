# N36 Verification Record — Property & Mutation Test Suites

**Date:** 2026-11-19 | **Task:** N36 | **Phase:** Phase VIII | **Status:** `PASS`
**Toolchain:** Python `3.12.16` | **Policy:** `splitmix64-u64-v1` (`N05_N36_verification` seeds `500001`–`500003`, `N24_assembly` seeds `100101`–`100130`)
**Artifact Under Test:** `output/simulator.html` (`99fd5c406950be1739b1d3480645d1698ed03eac6558f706d9f2c85b5f11745a`), `output/build-manifest.json` (`4cdee3e440a41f2793d4eb5b859449ec069b0271341b0be8b3b04de744198a51`)

---

## 1. Deliverables and SHA-256 Digests

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| [`tools/property_tests.py`](../tools/property_tests.py) | Property, golden-vector, smoke & 3-run determinism suite | 37,409 | `eec8d1be96d237391b77fff4a9bae39a1e26347e76d5556cd4e6cd9cffe4af0d` |
| [`tools/mutation_tests.py`](../tools/mutation_tests.py) | Scratch-isolated mutation runner & hygiene validator | 11,057 | `8ec3ced79520660c88210df499b1c5b90c030acf056ee0f9424ebcefafbdc67b` |
| [`data/mutant_corpus.json`](../data/mutant_corpus.json) | Declared 8-mutant corpus (7 killable + 1 equivalent) | 4,163 | `c4180248dde4fae6c36230c1ad2d835aa7d39e500274a8e65fe917e10a8aa3af` |
| [`evidence/N36_TEST_MANIFEST.json`](N36_TEST_MANIFEST.json) | Replayable regression run manifest (`8/8` PASS) | 25,695 | `dc8f78472b3bb8576f29ea4b1c041863bf52fc492b015fe4f7f3e2a392de550f` |
| [`evidence/N36_MUTATION_REPORT.json`](N36_MUTATION_REPORT.json) | Mutation kill table & hygiene fixture report | 3,838 | `6ae9942be2a95b22cb29fb01a432dbf86a51faec9eac9de09b02a1ef0a2db10b` |
| [`evidence/N36_DETERMINISM_RUNS.json`](N36_DETERMINISM_RUNS.json) | Three-run fresh-process determinism proof | 1,485 | `6648c438502ed5ec12f417f27d1294eb432ba34a6050ad12851279d441b51985` |

---

## 2. Property & Regression Suite (`tools/property_tests.py`)

Command: `python3 tools/property_tests.py --with-smoke --manifest evidence/N36_TEST_MANIFEST.json --three-run-proof evidence/N36_DETERMINISM_RUNS.json`

| Test ID | Scope / Sample Size | Status | Key Evidence |
|---|---|---|---|
| `PROP-CONV-ROUNDTRIP` | `36/36` conversion entries (`data/conventions.json`), seed `500001` | `PASS` | Exact `Fraction` & `Decimal` round-trips (`<=1e-18`), `2` blocked paths raise `DIMENSIONAL_INCONSISTENCY`; `FIX-CONV-OFFSET-CLASS` proves naive multiplicative inversion fails on `°C <-> K` while class-aware affine transform round-trips |
| `PROP-TOL-MONOTONICITY` | `8` sweeps (`7` topic families `absolute` + `significant_figures` class), seed `500002` | `PASS` | `0.0x`, `0.9x`, `1.0x` tol PASS; `1.1x` tol FAIL (`OUT_OF_TOLERANCE`); cliff-free monotonicity; `FIX-TOL-PLANTED-CLIFF` detects planted `0.5*tol` cliff |
| `PROP-CONS-RECOMPUTE` | `24/24` generated stoichiometry cases (`16` balanced, `4` mass-only imbalanced, `4` mass+mole imbalanced), seed `500003` | `PASS` | 100% agreement between `Engine.check_conservation` and independent `conventions.json` atomic-mass recompute; `FIX-CONS-MASS-ERROR` detects planted `O` mass error |
| `PROP-ASM-FAIRNESS` | `30` seeded N24 draws (`100101`–`100130`) | `PASS` | `28/28` families seen (`min=10`, `max=30` in band `[5, 30]`), `0` per-form duplicates, `21` slots / `100` pts each |
| `PROP-GV-PIPELINE` | `40/40` active N05 golden vectors | `PASS` | Verdict-for-verdict match; `verdict_sequence_sha256` = `891832425d347af95d09938b2924c33de541c37ffa117525e96b0c9140190fdd` (matches expected `N05_ORACLE_RECORD.json` `oracle_results_sha256`: `7b705dbf8edd0efd20af6208ac374988d4980020173c86ee55bb12062e94e214`) |
| `PROP-PARTIAL-CREDIT` | Multi-criterion rubric (`2.0` awarded, `1.0` denied, `1.5` pending) | `PASS` | `auto=2.0`, `pending=1.5` |
| `PROP-ESCAPE-HELPER` | `SimStore.escapeHtml` (`4` cases: Latvian diacritics + XSS payloads) | `PASS` | Diacritics `ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž ō ŗ` preserved; `< > & " '` escaped |
| `PROP-SMOKE-SUBSET` | `node tools/check_n31_runtime.js` (`31/31` smoke vectors) | `PASS` | Full in-file smoke suite green |

---

## 3. Mutation Corpus & Kill Table (`tools/mutation_tests.py`)

Command: `python3 tools/mutation_tests.py --report evidence/N36_MUTATION_REPORT.json`

- **Corpus Validation & Hygiene Fixtures:**
  - `FIX-MUT-NONEXISTENT-FUNC`: `nonexistent_function_n36` rejected by name (`detected: true`).
  - `FIX-MUT-LEAK`: unrestored scratch file `tools/quantity_engine.py` flagged by exit digest check (`detected: true`).
  - **Real Source Tree:** `real_sources_untouched: true`, `hygiene_failures: []`.

| Mutant ID | File / Function | Expected Killer Class | Actual Killers | Verdict |
|---|---|---|---|---|
| `MUT-01-TOL-SIGN-FLIP` | `tools/quantity_engine.py` / `grade_numeric` | `PROP-TOL-MONOTONICITY` | `PROP-TOL-MONOTONICITY`, `PROP-GV-PIPELINE` | `KILLED` |
| `MUT-02-REMOVED-ROUNDING` | `tools/quantity_engine.py` / `_expected_decimal` | `PROP-GV-PIPELINE` | `PROP-GV-PIPELINE` | `KILLED` |
| `MUT-03-INVERTED-FAMILY-FILTER` | `tools/assemble_forms.py` / `assemble_form` | `PROP-ASM-FAIRNESS` | `PROP-ASM-FAIRNESS` | `KILLED` |
| `MUT-04-SWAPPED-CRITERION-WEIGHT` | `tools/validate_n23_grading.py` / `apply_declared_rules` | `PROP-PARTIAL-CREDIT` | `PROP-PARTIAL-CREDIT` | `KILLED` |
| `MUT-05-BROKEN-ESCAPE-HELPER` | `src/compiled/store.js` / `escapeHtml` | `PROP-ESCAPE-HELPER` | `PROP-ESCAPE-HELPER` | `KILLED` |
| `MUT-06-CONSERVATION-TOLERANCE-BYPASS` | `tools/quantity_engine.py` / `check_conservation` | `PROP-CONS-RECOMPUTE` | `PROP-CONS-RECOMPUTE` | `KILLED` |
| `MUT-07-OFFSET-CONVERSION-DROP` | `tools/quantity_engine.py` / `convert` | `PROP-CONV-ROUNDTRIP` | `PROP-CONV-ROUNDTRIP` | `KILLED` |
| `MUT-08-EQUIVALENT-ABS-DIFF` | `tools/quantity_engine.py` / `grade_numeric` | `EQUIVALENT` | `—` | `EQUIVALENT` |

---

## 4. Three-Run Fresh-Process Determinism Proof

| Run | Status | Comparable Manifest SHA-256 | Verdict Sequence SHA-256 | Duration (ms) |
|---:|---|---|---|---:|
| 1 | `PASS` | `8f293b78ae6171d16d9490f24e6a1666e6ead89a309e4fdb2f775e8c50a1712c` | `842230727b2b41711aef68b2aab91bd93f6bbb52898c718cfc28aa69e8fd1cc2` | `717.931` |
| 2 | `PASS` | `8f293b78ae6171d16d9490f24e6a1666e6ead89a309e4fdb2f775e8c50a1712c` | `842230727b2b41711aef68b2aab91bd93f6bbb52898c718cfc28aa69e8fd1cc2` | `687.126` |
| 3 | `PASS` | `8f293b78ae6171d16d9490f24e6a1666e6ead89a309e4fdb2f775e8c50a1712c` | `842230727b2b41711aef68b2aab91bd93f6bbb52898c718cfc28aa69e8fd1cc2` | `693.836` |

**Handoff (N36 → N39):** `tools/property_tests.py`, `tools/mutation_tests.py`, `data/mutant_corpus.json`, and `evidence/N36_TEST_MANIFEST.json` are handed to **N39** as the first registered automated verification suite.
