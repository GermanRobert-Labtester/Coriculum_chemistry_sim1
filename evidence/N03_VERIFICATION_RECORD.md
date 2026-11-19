# N03 verification record — conventions artifact, conflict registry, gate and handoff

**Task:** N03, Phase I (P0, High risk). **Recorded:** 2026-11-17 (UTC). **Workspace:** `/home/robertsrff/Chemistry_Med/Chemistry_1st_coriculum`.

**Epistemic labels.** The validator, composition, citation, registry, gate, runtime, single-sourcing, degradation and parity runs below are **VERIFIED (2026-11-17, this environment)** with the commands and artifacts named. Their citation anchors are bound to the N01 frozen masters under **VERIFIED (2026-11-16)**; a changed master digest is a visible event because the literal or anchor check fails. The tolerance thresholds and their grading use are **PROPOSED training policy**. The catalase question is **OPEN** with the course lecturer as owner. The paint check is a **render check only**, not a browser, accessibility or print acceptance.

## 1. What exists now

| Artifact | Path | Role |
|---|---|---|
| Conventions island | `data/conventions.json` | Authored scientific rulebook, embedded as `#sim-conventions` |
| Conventions validator | `tools/validate_conventions.py` | Schema, conversions, composition, citations, labels, registry, vectors |
| Runtime loader | `src/conventions-loader.js` | One reader; named `ConventionsError` degradation |
| Runtime harness | `tools/check_conventions_runtime.js` | Baseline accessors, single-sourcing, degradation |
| Build gate | `tools/build.py` | Gate order 2 `conventions`; embeds the island and loader |
| Conflict registry | `evidence/N03_CONFLICT_REGISTRY.json` | Standalone registry export (22 V/C entries + 4 observations) |
| Validation record | `evidence/N03_VALIDATION_RECORD.json` | Machine-readable counts, citation results, chain results |
| Corpus record | `evidence/N03_CORPUS_RECORD.json` | Happy path + six negative fixtures + parity |

The island is **not a second copy** of the masters. It declares rules, constants and unit relations with machine-checked citations; the masters remain the teaching authority.

## 2. Validator pass — entry count per section

Command:

```
python3 tools/validate_conventions.py --report evidence/N03_VALIDATION_RECORD.json --registry-out evidence/N03_CONFLICT_REGISTRY.json
```

Verbatim first line:

```
PASS conventions: 10 elements, 23 compounds, 9 constants, 36 conversions, 9 chains, 12 tolerance classes, 12 V + 10 C conflicts, 7 vectors
```

| Section | Count | Check |
|---|---:|---|
| Atomic masses | 10 elements | Every value is a positive decimal; display value appears in a cited master |
| Compound molar masses | 23 compounds | Working value and course-rounded value kept separately; display value appears in a cited master |
| Constants | 9 | Numeric; exact/working/conditioned declared |
| Unit conversions | 36 | 34 bidirectional, 2 explicit one-way blocked (`mass_to_volume_direct`, `volume_to_mass_direct`) |
| Composition chains | 9 | 7 numeric, 2 symbolic; independent `Fraction` recompute |
| Tolerance classes | 12 | Absolute value, significant-figure mode, rounding rule and PROPOSED label complete |
| Concentration bases | 4 | m/m, m/V, V/V, molar; Latvian names; default m/m |
| Potential symbols | 3 | E°, E, E°′; mixing rule; E°′ formula |
| Reference potentials | 7 | Each carries its convention id |
| Citations | 74 | 69 master + 5 official-programme; all resolve; all used |
| Conflict entries | 22 | 12 V + 10 C; status, owner, history and task bindings |
| Observations | 4 | New N03 findings, registered outside the fixed V/C numbering |
| Derived vectors | 7 | Every `source_ref` resolves through the runtime path |

Citation result: **74 defined, 74 used, 0 failed**. The citation split is explicit:

- **69 master citations** (`source_class: "master"`) to `C1-MASTER` through `C7-MASTER`; each has an anchor that exists case-exactly and/or a literal found in the tag-stripped master text.
- **5 official-programme citations** (`source_class: "official-programme"`) to `PROGRAMME-EXTRACT`: paper format, 180 minutes, seven topics, significant-figure expectation, and the programme's own malformed `mg <=> g` line (C02/V-04).

The official-versus-training split is therefore visible at the convention level, not only in prose: `CIT-PROG-*` versus `CIT-C*-*`.

## 3. Composition chains — independent recompute

The validator does not trust the declared chain factor. It parses the unit expression, applies each step's conversion in the declared numerator/denominator position, composes an affine transform with `Fraction`, and compares it to the declared factor and offset.

| Chain | From → to | Declared factor | Computed factor | Composed unit | Result |
|---|---|---:|---:|---|---|
| `mass_mg_to_g` | mg → g | 0.001 | 0.001 | g | PASS |
| `volume_ml_to_l` | mL → L | 0.001 | 0.001 | L | PASS |
| `concentration_mg_per_ml_to_g_per_l` | mg/mL → g/L | 1 | 1 | g/L | PASS |
| `concentration_mg_per_l_to_g_per_ml` | mg/L → g/mL | 0.000001 | 0.000001 | g/mL | PASS |
| `concentration_g_per_ml_to_kg_per_l` | g/mL → kg/L | 1 | 1 | kg/L | PASS |
| `percent_m_v_to_g_per_l` | % (m/V) → g/L | 10 | 10 | g/L | PASS |
| `temperature_c_to_k` | °C → K | 1 + 273.15 offset | 1 + 273.15 offset | K | PASS |
| `molarity_to_mass_concentration` | mol/L → g/L | symbolic | — | requires molar mass | PASS |
| `density_mass_to_volume` | g → mL | symbolic | — | requires density | PASS |

The **V-04 density-defect chain** is the `concentration_mg_per_ml_to_g_per_l` row: mg→g and mL→L compose to exactly 1, so `1 mg/mL = 1 g/L`. The direct `mg → L` path is not a chain at all: it is a declared **blocked** conversion. A chain cannot include it, and the runtime has no factor for it.

## 4. Wrong-factor fixture — the composition check can fail

Scratch copy: `data/conventions.json` with only
`unit_system.chains[id=concentration_mg_per_ml_to_g_per_l].factor` changed from `1/1` to `2/1`.
The scratch copy was validated with the full schema, citation and registry checks.

Verbatim first error:

```
Chain concentration_mg_per_ml_to_g_per_l: factor mismatch: declared 2 != computed 1
```

The error names the chain and both factors. The full error list contains only that composition failure — citations and registry still pass, so the fixture isolates the composition check. The build gate refuses the same scratch copy (Section 7).

## 5. Conflict registry — completeness, statuses and bindings

The registry is exported to `evidence/N03_CONFLICT_REGISTRY.json`. Its canonical digest is:

```
27cd592043e257698fa57d263c5a2a31345fe271b4104dcbe7ed539ebc86537a
```

Entry statuses: **15 resolved-by-task, 5 documented-and-accepted, 2 open-with-owner**.

| Id | Status | Resolution task | Enforcement / related | Owner |
|---|---|---|---|---|
| V-01 | documented-and-accepted | — | N01 mitigation | external source workspaces (not published) |
| V-02 | resolved-by-task | N03 | N11, N17 | N03 |
| V-03 | resolved-by-task | N03 | N10 | N03 |
| V-04 | resolved-by-task | N17 | N03 authored the rule | N17 |
| V-05 | resolved-by-task | N03 | N15 | N03 |
| V-06 | resolved-by-task | N13 | N03 authored the scope rule | N13 |
| V-07 | resolved-by-task | N15 | N03 authored the assumption rule | N15 |
| V-08 | open-with-owner | — | N13, N09 | RSU course lecturer |
| V-09 | resolved-by-task | N25 | N26 | N25 |
| V-10 | resolved-by-task | N31 | N06 | N31 |
| V-11 | resolved-by-task | N31 | N02, N03 | N31 |
| V-12 | resolved-by-task | N34 | — | N34 |
| C01 | documented-and-accepted | — | official 2025 scope | official programme |
| C02 | documented-and-accepted | — | owned by V-04 | N17 (via V-04) |
| C03 | documented-and-accepted | — | owned by V-02 | N03 (via V-02) |
| C04 | resolved-by-task | N03 | N13, N17 | N03 |
| C05 | open-with-owner | — | owned by V-08 | RSU course lecturer |
| C06 | resolved-by-task | N02 | N03, N10 | N02 + N03 |
| C07 | resolved-by-task | N03 | N15 | N03 |
| C08 | resolved-by-task | N13 | N03 | N13 |
| C09 | resolved-by-task | N15 | N03 | N15 |
| C10 | documented-and-accepted | — | N05 mitigation | N05 |

The bidirectional check is real, not a claim:

- Every V and C entry has a status from the three-value vocabulary, a status reason, an owner, an epistemic label and a non-empty append-only `history`; the last history event's status must equal the current status.
- Every task id in a `resolution_task`, `mitigation_task`, `binding_task`, `enforcement_tasks` or `supporting_tasks` must exist in the roadmap's 40 task headings.
- The roadmap's Section 4.1 claim row for each V id is parsed at validation time; the registry's `roadmap_claim_task_ids` must equal it, and every claimed task must appear in the registry's binding set.
- V-11's Section 4.1 row names no task; the validator falls back to the N03 B.1.2 sentence (`V-10 and V-11 to N31's assembly policy`) and records the claim as N31. This is recorded rather than silently invented.
- For V-04, V-05, V-06, V-07, V-09, V-10, V-11 and V-12, the `binding_task` must appear with the V id in the N03 Main Step B.1.2 text. A binding that exists only in the registry would fail.
- The V-01 entry is compared field-by-field with `evidence/V01_CONFLICT_ENTRY.json` for `finding`, `status`, `status_reason`, `owner`, `resolution_task`, `mitigation_task`, `mitigation`, `evidence`, `epistemic_label` and `handoff_notes`; all are verbatim.

Negative fixtures:

| Fixture | Result | Verbatim named failure |
|---|---|---|
| Statusless entry | FAIL | `Conflict V-05: status is missing or unknown (None)` |
| Phantom resolution task | FAIL | `Conflict V-04: names unknown task 'N99'`; `Conflict V-04: resolution_task 'N99' is not a roadmap task` |

The catalase question is carried **open verbatim** under both V-08 and C05:

> Vai kursa katalāzes aktivācijas enerģija ir 23 J·mol⁻¹ (kā iespiests), 23 kJ·mol⁻¹ (piedāvātais vienības labojums) vai cita vērtība, un kādos apstākļos (katalāzes avots, temperatūra, pH, H₂O₂ koncentrācija) tā noteikta? Avotā: "23 J·mol⁻¹, kas nav fizikāli ticami; iespējams, domāts 23 kJ·mol⁻¹, bet tas nav apstiprināts. Avota skaitlis netiek mainīts. ... Kura vērtība atbilst kursa mērījumam — jāapstiprina docētājai."

**C10/C05 nomenclature discrepancy (N03-OBS-01).** The 40-task roadmap's N03 B.1.1 and N40 B.1.2 refer to “C10's catalase question”. In the predecessor audit, catalase is **C05**; **C10** is “Current plan's 14 examples are synthetic givens”. The registry preserves the predecessor numbering: C05 and V-08 carry catalase open, C10 records the synthetic-examples item, and N03-OBS-01 records the discrepancy for N40. Do not read C10 as catalase.

**New observations (registered outside V/C).** N03-OBS-02: the roadmap's C1 id count (382) and the N03 all-`id="..."` count (957) differ by counting rule; V-10 keeps the historical 382 and N31 must apply one declared rule. N03-OBS-03: C3 prints KOH as 56,105 in the worked calculation and 56,106 in the 6. table; C3 prints H₂O₂ as 34,01 and C6 as 34,0147. The artifact keeps `working_value` and `course_rounded` separate. N03-OBS-04: the C2/C6 meniscus wording is reconciled by solution colour (clear → lower meniscus, dark → upper edge; C6 uses dark KMnO₄).

## 6. Gate refusals

Build gate registry after N03: order 1 `coverage` (N02), order 2 `conventions` (N03). Both must pass before any artifact is written.

| Scratch fixture | Exit | Verbatim first gate line | Artifact written |
|---|---:|---|---|
| Wrong chain factor | 1 | `FAIL conventions gate (order 2, owner N03): Chain concentration_mg_per_ml_to_g_per_l: factor mismatch: declared 2 != computed 1` | No |
| Statusless V-05 | 1 | `FAIL conventions gate (order 2, owner N03): Conflict V-05: status is missing or unknown (None)` | No |

Both runs also print `Refusing build. The artifact was not written.` The gate is not a post-write lint.

## 7. Embedded island and byte contribution

Clean build:

```
python3 tools/build.py
```

```
PASS build: output/simulator.html (183534 bytes, sha256=98befa6dc1cffd16b616f3df63600006fcf48928629f13ffaf2a51f0b5f284db)
  build id: 3b78e360708c8062
  island: #sim-coverage 46502 canonical bytes, sha256=f33f61be6755f94426f623ebcfdf267a46c09538da3664df3a55956ffa3009c3
  island: #sim-conventions 103589 canonical bytes, sha256=6763f5f39266460f365a7a27c141a893bf0c02ee3b75a66cf55af6750a77c7bd
  gate 1: coverage (N02) PASS
  gate 2: conventions (N03) PASS
```

`output/build-manifest.json` records the conventions island source, canonical bytes, digest and emission rule. The document also carries `<meta name="sim-conventions-digest">` with the same digest.

Byte accounting:

| Measure | Value |
|---|---:|
| `data/conventions.json` (pretty authored file) | 138,269 bytes |
| `#sim-conventions` canonical island | 103,589 bytes = 101.16 KiB |
| Bank sub-budget (Section 1) | 200–420 KiB |
| Island as share of bank sub-budget | 24.09 % of 420 KiB; 50.58 % of 200 KiB |
| `output/simulator.html` | 183,534 bytes = 179.23 KiB |
| Total file budget | 700–1400 KiB |
| File as share of total budget | 12.8 % of 1400 KiB; 25.6 % of 700 KiB |

The conventions island is **not part of `#sim-bank`**; the bank comparison is a scale check, not a claim that the rulebook consumes bank content. The total file remains far inside the 700–1400 KiB budget.

## 8. Single-sourcing and honest degradation

The shipped loader is the only reader. The runtime harness (`node tools/check_conventions_runtime.js --json`) runs the loader extracted from `output/simulator.html`.

**Single-sourcing, one tolerance change.** Scratch island changes only
`tolerances.quantity_classes[id=burette_volume].absolute.value` from `0.05` to `0.10`. In one run:

| Consumer | Baseline | Scratch |
|---|---:|---:|
| Engine tolerance output (`model.tolerance('burette_volume').absolute`) | 0.05 | 0.1 |
| Figure tolerance field (same island path, the N11 stand-in) | 0.05 | 0.1 |
| Vector expected value (`VEC-TOL-BURETTE`) | 0.05 | 0.1 |

All three change, and all three read the same entry. There is no local tolerance copy.

**Single-sourcing, one conversion change.** Scratch island changes only
`unit_system.chains[id=concentration_mg_per_ml_to_g_per_l].factor` to `2/1`:

| Consumer | Baseline | Scratch |
|---|---:|---:|
| Engine conversion (`convert(1, 'mg/mL', 'g/L')`) | 1 | 2 |
| Vector expected value (`VEC-CONV-MGML-GL`) | 1 | 2 |

**Degradation fixtures.**

| Fixture | Result | Named error |
|---|---|---|
| Truncated island (first 120 chars) | Error state visible; status non-blank | `E_CONVENTIONS_JSON`; message names `#sim-conventions` |
| Missing island element | Error state visible | `E_CONVENTIONS_MISSING`; message names `#sim-conventions` |
| Deleted conflict entry (22 → 21) | Rejected | `E_CONVENTIONS_CONFLICT_COUNT`; message names `#sim-conventions` and `22`/`21` |

The loader never falls back to a local constant. A consumer that catches the error may degrade its own surface, but it cannot silently use a stale copy.

## 9. Corpus parity

`python3 tools/n03_corpus.py` writes a timestamp-free record. Two consecutive runs:

| Run | Record SHA-256 | Bytes |
|---|---|---:|
| 1 | `e701123b0d9fed7b15de7a3c4355a645f8c4f7a3a3920b76c95aba789afe1e8e` | 10,806 |
| 2 | `e701123b0d9fed7b15de7a3c4355a645f8c4f7a3a3920b76c95aba789afe1e8e` | 10,806 |

Byte-identical. The corpus also records a two-build parity: output SHA-256 `98befa6dc1cffd16b616f3df63600006fcf48928629f13ffaf2a51f0b5f284db` on both runs, and the committed `output/simulator.html` matching the fresh build. The fresh-build manifest written to the scratch output path has SHA-256 `3562a9b6852ed58d97abcec177d05d964e54c9e9e36d776b7a9d5efbf1d7f5cf` on both runs; the committed `output/build-manifest.json` (`974c256def38d80039815e4e51d41031628afa77d22b95b281e3f3c45ae89831`) differs only in its `output` field, which names the committed path instead of the scratch path.

## 10. Labeling — verbatim per section

| Section | Label in `data/conventions.json` |
|---|---|
| `atomic_masses` | `master-grounded` |
| `compound_molar_masses` | `master-grounded` |
| `constants` | `master-grounded` |
| `unit_system` | `master-grounded conversions; measured density is declared separately` |
| `concentration_bases` | `master-grounded definitions; default basis is a course convention` |
| `percentage_basis` | `master-grounded rule; default is a course convention` |
| `density` | `master-grounded measured relation; V-04 rule` |
| `titration` | `master-grounded reading rules; V-05 wording rule` |
| `potentials` | `master-grounded convention; V-03 rule` |
| `thermodynamics` | `master-grounded convention; C04 resolution` |
| `spectrophotometry` | `master-grounded scope rules; V-06 and V-07 resolutions` |
| `tolerances` | `PROPOSED training policy` |
| `rounding` | `master-grounded rule; PROPOSED as grading policy` |
| `open_questions[0]` | `open-with-owner` (catalase) |

Every tolerance class carries `absolute.label = "PROPOSED training policy"`, `significant_figures.label = "PROPOSED training policy"` and `rounding.label = "PROPOSED training policy"`. The programme sets no tolerance rule; the master's instrument uncertainty (e.g. burette ±0.05 mL) is the basis, not an official grading threshold.

## 11. Handoff to consumers

`consumer_contract` names N05, N10, N11, N12, N13, N14, N15, N17, N18 and N19. In particular:

- **N05** reads `derived_vectors`, `unit_system.chains` and `constants`; the golden vectors cite the island digest rather than copying factors.
- **N10** reads `potentials.symbols`, `concentration_bases` and `unit_system.conversions`; the E°/E°′ symbols and percent basis come from one place.
- **N11–N15** read `tolerances.quantity_classes`, `atomic_masses`, `compound_molar_masses`, `titration`, `spectrophotometry` and `thermodynamics`; figure rules cite entries, not local text.
- **N17–N19** read `unit_system`, `density`, `tolerances`, `rounding` and the potential/thermodynamic rules; the V-04 dimension gate and the V-05 wording rule are bound to them.
- **N40** receives the registry as the authoritative conflict list. The append rule is recorded in `conflicts.append_rule_lv`: re-opening appends a `reopened` history event and never rewrites prior events.

## 12. Paint check

`lite-shot -e falkon --cdp -g 1280x1100 --full-page output/simulator.html evidence/N03_PAINT_CHECK.png` painted at 1259×3094 with 5,744 colours; the status line is visible:

> Konvenciju kopa ielādēta: 36 vienību pārejas, 9 ķēdes, 12 tolerances, 22 konflikti.

No conventions error box is visible. This is a paint check, not a visual, accessibility or print acceptance.

## 13. Limits and not performed

- The citation check is a machine check of anchor existence and literal presence in the frozen master/programme text. It is not a semantic proof that the master's chemistry is correct. The N36 conservation recompute remains the scientific cross-check; a contradiction between a convention and a master worked example surfaces as a property failure, not a silent preference.
- The tolerance values and their grading use are PROPOSED training policy. The programme sets no tolerance, point-weight or pass-mark rules.
- V-04's structural gate is bound to N17 and is not implemented here; N03 authors the rule, the blocked conversion, the composition chain and the gate fixture. The registry records that state explicitly.
- V-06, V-07, V-09, V-10, V-11 and V-12 are bound to N13, N15, N25, N31 and N34; those implementations are not part of N03.
- The catalase question is not resolved. It stays open with the course lecturer; no disputed value is asserted.
- No browser acceptance, assistive-technology check, print/paper acceptance, learner trial or official-examination claim is made.
- The N02 coverage runtime harness was re-run after the conventions island was added and still passes (7 topics, 64 outcomes).

## 14. Commands run

```
python3 tools/validate_conventions.py --report evidence/N03_VALIDATION_RECORD.json --registry-out evidence/N03_CONFLICT_REGISTRY.json
python3 tools/build.py
node tools/check_conventions_runtime.js --json
python3 tools/n03_corpus.py
python3 tools/n03_corpus.py
node tools/check_coverage_runtime.js --json
python3 tools/verify_preparation.py --repo-local
python3 tools/check_source_inventory.py
lite-shot -e falkon --cdp -g 1280x1100 --full-page output/simulator.html evidence/N03_PAINT_CHECK.png
```

Scratch fixtures live under `/tmp/opencode/n03-corpus/`; they are regenerated by the corpus and never written into `data/`, `materials/` or `output/`.
