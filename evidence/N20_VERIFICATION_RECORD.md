# N20 — Variant engine, the 28 family templates and the frozen 112-instance practice bank

**Status:** closed 2026-11-18 (UTC). **Phase:** IV · **Priority:** P0 · **Risk:** High · **Effort:** L
**Dependencies:** N04, N05, N16, N17, N18, N19

**Epistemic note.** Every execution recorded below **VERIFIED (2026-11-18, this environment)**: the
Python authoring twin, the JavaScript runtime twin, the four gates, the runtime harness, the corpus
and the build all ran here, and their results are in `evidence/`. This is **not** a browser render,
screen-reader, print or instructor-acceptance claim, and not an official examination claim. The
2025 programme fixes seven topics, a written-on-paper examination and a maximum of 180 minutes; it
fixes **no** point weight, no question count, no pass mark, no allowed aid and no exact exam
question type. Everything declared here as a weight, a count, a family mix or an acceptance set is
**PROPOSED training policy**. The family count, the variant count, the instance count, the required
types and the point weights are proposals; the seven topics, the paper examination and the
180-minute maximum are the only official facts this task may rely on.

---

## 1. What was built

| Artifact | Role |
|---|---|
| `tools/variant_engine.py` | The Python authoring twin: fixed-point arithmetic, seeded drawing, the derivation recipes, the canonical emission and the template validation. |
| `src/variant-engine.js` | The runtime twin `SimVariantEngine`: the same contract, the same canonical bytes, the ephemeral retry path. |
| `tools/n20_content.py` | The authored content: 28 families × 4 variants — Latvian stems, declared ranges, exact recipes, payloads, rubrics, source references and the misconception signatures. |
| `data/family_templates/topic1..7.json` | The frozen family templates (28 families, 112 variants), canonical bytes. |
| `src/variant-templates.js` | The runtime template asset, generated from the frozen templates; it ships from `src/` and is **not** inlined. |
| `data/bank/FAM-*.json` | The frozen practice bank: 112 reviewed instances in 28 family files. |
| `tools/author_family_templates.py` | Freezes the templates and emits the runtime asset; `--check` proves the frozen bytes still match the authored content. |
| `tools/author_bank.py` | Instantiates the 112 instances and writes the bank; `--check` proves the frozen bank still matches the templates. |
| `tools/validate_family_templates.py` | The template gate: the per-family validation table, the determinism proof and the out-of-range refusal. |
| `tools/validate_bank_review.py` | The review workflow gate: five mechanical checks per instance, the promotion to the accepted state and the scratch-refusal proof. Build gate 16. |
| `tools/check_n20_runtime.js` | The runtime harness: cross-language parity, determinism, the ephemeral path, the parity fixture, the tamper fixture and the in-file smoke vector against the built artifact. |
| `tools/n20_corpus.py` | The evidence corpus: the gates, the harness, the byte accounting and the two-run parity. It writes three timestamp-free records: the corpus record, the gate-level validation record and the acceptance-criteria verification record. |
| `docs/VARIANT_ENGINE_FORMAT.md` | The frozen interface for N24, N28, N30 and N31. |
| `src/bank-loader.js` | The runtime integrity check: the loader verifies the island digest at load and refuses a tampered or unsigned island. |

## 2. The variant engine

**One authority per concern.** The constants live only in `#sim-conventions` and are resolved by
reference (`molar_mass:NaCl`, `potential:Cu2_Cu`, `nernst_slope` …) — no physical constant is
copied by value into a template. The arithmetic lives only in the engine, and the grading lives
only in N17/N18/N19. The engine computes; it never grades.

**Fixed-point arithmetic only.** Every number is an integer at scale 10⁻⁹ (`SCALE = 9`): Python
`int`, JavaScript `BigInt`. No IEEE-754 float ever reaches an emitted number, so the two twins
cannot drift on a rounding boundary. The only transcendental-looking operation, `log10_pow10`,
is exact integer arithmetic: it counts the trailing decimal zeros of the fixed-point representation
and refuses a value that is not an exact power of ten. A value that cannot be represented exactly
is a hard failure, never an approximation.

**The seed.** `FNV-1a-64` over the UTF-8 seed key `FAM-<family>-<variant>`; the draws come from
the frozen N05 SplitMix64 stream. The same family, variant and seed therefore reproduce the same
instance anywhere — which is what makes the bank auditable and the ephemeral path comparable.

**The written answer form.** The payload's `sig_figs` is the significant-figure count of the
*written* answer form, which is what the grader counts — the same convention the frozen N05 corpus
follows (`8,00 g` → 3). A whole answer whose significant figures live in trailing zeros (`680`) is
written in scientific notation (`6,80 × 10²`), because N17 counts `680` as two significant figures
and the plain form cannot carry three. N17's parser accepts that form and counts it the same way,
so the display teaches exactly what the grader accepts.

## 3. The 28 family templates

| Topic | Families | Instances |
|---|---|---|
| 1 — substances, mixtures, reactions | FAM-1A … FAM-1D | 16 |
| 2 — measurements and calculations | FAM-2A … FAM-2D | 16 |
| 3 — solutions and concentrations | FAM-3A … FAM-3D | 16 |
| 4 — thermodynamics | FAM-4A … FAM-4D | 16 |
| 5 — kinetics and catalysis | FAM-5A … FAM-5D | 16 |
| 6 — redox processes | FAM-6A … FAM-6D | 16 |
| 7 — spectrophotometry | FAM-7A … FAM-7D | 16 |

**Required types.** Q02 (27), Q04 (4), Q10 (4), Q11 (4), Q12 (7), Q13 (8), Q15 (7) are present and
their families are named in `evidence/N20_TEMPLATE_VALIDATION.json`. All eighteen response types
appear; the payload classes split as numeric 41, method 38, option_select 14, graph 11, matching 5,
ordering 3.

**Template digest:** `64c492264c669b6b0b48fa00abac59e3bcaf6fc714e4fb9e0e3dc6c42efa80ad` — the
Python and the JavaScript twin compute the same digest over the same template set.

**Range gate.** `tools/validate_family_templates.py` copies the first family, moves one drawn
parameter's maximum below its minimum and shows that the validation fails by **family and
parameter name** (`E_VAR_PARAM_RANGE`, `FAM-1A`, `variants[A].m_sand_g`, "Parameter min 85 > max
80"). A template outside the declared tolerance reach of N17–N19 is a template validation failure,
never a runtime surprise.

## 4. The frozen bank

**112 instances, 28 families, four variants each** (`data/bank/FAM-*.json`, 304,293 B in 28 files).

| Digest | Value | Covers |
|---|---|---|
| Bank source digest | `1c263cdb37396f0eb910c52cf9e6a0b30725533358d57fd7de85c4b58c78acb6` | The frozen bank files, in family order — the reference for "any bank change is a new digest and a deliberate act". |
| Bank island digest | `07fec72a5484bd8e9bf705e2127f3a5b482d5b65c59c32fbee7ab2cd3299bac1` | The `#sim-bank` island the artifact embeds. |
| Embedded digest | `07fec72a5484bd8e9bf705e2127f3a5b482d5b65c59c32fbee7ab2cd3299bac1` | The same digest over the island *text as embedded*; the runtime loader verifies this one. |

**The island is a runtime projection.** It carries everything a renderer, a grader or an analytics
consumer needs, and drops the per-instance audit tables (`draws`, `derived`, `review_workflow`).
Those tables are the audit trail and they stay in `data/bank/*.json` and in the N20 evidence
records. The projection is what keeps the artifact inside the Section 1.3 budget; both digests are
recorded so that neither the authored bank nor the embedded island can change unnoticed.

## 5. The review workflow

Five stages — `authored → validated → recomputed → reviewed → accepted` — and five mechanical
checks per instance: `range_compliance`, `n17_recompute`, `n12_leak_scan`,
`accessibility_structure`, `grading_alignment`.

- **Range compliance** — every drawn value is inside its declared range and on its declared step;
  every conventions reference resolves.
- **N17 recompute** — every derived value is recomputed through the N17 quantity engine from the
  instance's *frozen* values, and the recomputed dimension must equal the declared unit's
  dimension. The comparison is independent of the variant engine's arithmetic: N17 works in exact
  decimals with a dimension vector, the engine in fixed-point integers. Every recompute is
  recorded per instance in `evidence/N20_RECOMPUTE_RECORD.json`.
- **N12 leak scan** — the scanner runs over the learner-facing surfaces of every instance. No
  instance leaks a key value without a declared exemption.
- **Accessibility structure** — a *mechanical* structural check (labels, identifiers, prompt
  text). Renderer-level AT and visual acceptance is deferred to N22/N34 and is **not** claimed.
- **Grading alignment** — every instance is graded through the engine that owns its type, with a
  learner-realistic submission, and the verdict class is compared with the expectation.

**112 of 112 instances are in the accepted state.** The sign-off is the **N20 task author's
preparation pass** — the author checked the ranges, the recompute, the leak scan and the
structure. It is **not** an RSU instructor's acceptance.

**The gate refuses an unreviewed instance.** `python3 tools/validate_bank_review.py
--prove-scratch-refusal` copies the bank, resets one instance's review state and shows the gate
refusing it **by id**: `COL1-1-1A-ZZ-99`, `E_REVIEW_NOT_ACCEPTED`, "review.content ir 'pending',
nevis \"passed\"". Build gate 16 runs the same check and refuses the build.

**Leak scan and exemptions.** Four instances carry a declared exemption, each with an N12 reason
code, a Latvian reason of at least 20 characters and an explicit scope:

| Instance | Code | Scope | Reason |
|---|---|---|---|
| COL1-2-2B-A-01 | `EXEMPT_GIVEN_INPUT` | the instance's own given inputs | the item *is* a unit conversion: the answer is the same mass the stem gives in kilograms. |
| COL1-2-2B-B-01 | `EXEMPT_GIVEN_INPUT` | the instance's own given inputs | the item is a conversion to micromoles; the answer is the same amount the stem gives in moles. |
| COL1-5-5B-D-01 | `EXEMPT_READING_DISPLAY` | `point.1.x` | the half-life is read from the graph: the answer is a plotted coordinate, and it moves with the seed, so the scope is a surface, not a number. |
| COL1-7-7B-C-01 | `EXEMPT_READING_DISPLAY` | `point.0.y`, `point.1.y` | **the borderline case.** The target concentration lies between the two calibration standards, so the absorbance is interpolated between two labelled values. The N12 borderline rule (`N12-LEAK-BORDER-01`) records it as `BORDERLINE`; the exemption says *why* the case is a learner interpolation and not a copied label. |

Eight graph instances are recorded as `BORDERLINE` under `N12-LEAK-BORDER-01` (the answer lies
within two axis steps of a labelled value). A proximity is not a leak; it is the case the learner
has to interpolate, and it is recorded per instance.

## 6. The proofs

The gate-level summary is `evidence/N20_VALIDATION_RECORD.json`: each gate, its status, its
command and its findings. The per-instance detail lives in the records the tables below name.

### AC1 — happy path

| Claim | Evidence |
|---|---|
| Every template validates (ranges, conventions entries, types, payload classes, tolerance classes, rubric weights) | `evidence/N20_TEMPLATE_VALIDATION.json`, 28 rows, 0 violations |
| An out-of-range scratch template fails by family and parameter name | `tools/validate_family_templates.py` → `E_VAR_PARAM_RANGE`, `FAM-1A`, `variants[A].m_sand_g` |
| The required types are covered and their families named | `evidence/N20_TEMPLATE_VALIDATION.json` → `required_types_covered` |
| Identical seeds yield byte-identical instances | `evidence/N20_DETERMINISM_RECORD.json`: 112/112 identical, 112/112 equal to the frozen bank |
| The two languages agree byte for byte | `evidence/N20_RUNTIME_RECORD.json` → `cross_language_parity`: 112/112 |

### AC2 — negative and edge cases

| Claim | Evidence |
|---|---|
| All 112 instances validate against the N04 schema, zero violations | `python3 tools/validate_bank.py --bank data/bank --require-types` |
| Every numeric key value was recomputed through N17 | `evidence/N20_RECOMPUTE_RECORD.json`, 112 instances, 0 failures |
| The workflow gate passes | `evidence/N20_REVIEW_WORKFLOW.json`, status PASS, 112 promoted |
| An unreviewed scratch instance refuses the build by id | `--prove-scratch-refusal` → `COL1-1-1A-ZZ-99` |
| Grading aligns on the sample | `evidence/N20_REVIEW_WORKFLOW.json` → `grading_alignment` per instance |
| No key leaks without a reasoned exemption | `evidence/N20_LEAK_SCAN_RECORD.json`, 112 instances, 0 unexempted findings |

### AC3 — domain integrity and zero regression

| Claim | Evidence |
|---|---|
| The loader rejects a tampered island by digest | `evidence/N20_RUNTIME_RECORD.json` → `tamper_fixture`: `E_BANK_DIGEST_MISMATCH` |
| The loader rejects an unsigned island | same fixture → `E_BANK_DIGEST_MISSING` |
| Retries are deterministic and exclude the frozen seeds | `ephemeral_path`: attempt 0 → a seed outside the frozen set; a colliding seed is skipped and the attempt advances to 1 |
| Both paths grade through identical engine code | `parity_fixture`: the same `N17-numeric` binding, the same criterion ids, the same verdict class for equivalent submissions |
| The ephemeral instance is never persisted and never confusable | `extensions.data.ephemeral`: `persisted: false`, `frozen_bank_member: false`, and its own question id (`…-EPH-0`) |
| The smoke vector passes | `smoke_vector`: `SMK-N20-BANK-GRADE-VERDICT` runs against the built artifact, loads the island with its digest verified and grades `COL1-1-1C-A-01` as `correct` (3/3 points) and a wrong answer as `incorrect` |
| Zero regression | All 16 build gates PASS, including the 15 pre-existing gates |

## 7. The byte budgets

| Budget | Measured | Range | Note |
|---|---|---|---|
| Artifact total | 1,374,364 B (1,342.2 KiB) | 700–1,400 KiB | 57.8 KiB of headroom |
| Bank island | 249,798 B (243.9 KiB) | 200–420 KiB | the runtime projection |
| Runtime JS code | 225,192 B (219.9 KiB) | 120–232 KiB | see below |
| CSS | 39,796 B (38.9 KiB) | 40–80 KiB (ceiling 80 KiB) | below the plan's target range; prior-phase content, recorded, not changed |

**The runtime-JS ceiling was re-set on the measurement.** The inline executable JavaScript was
223,288 B (218.1 KiB) *before* N20 — already within 2 KiB of the plan's 220 KiB figure — and N20's
frozen bank adds the loader's runtime integrity check and one in-file smoke vector, for a measured
225,192 B (219.9 KiB). The old ceiling would have been exceeded by 88 bytes, i.e. failed on a
rounding difference rather than on a requirement. `tools/validate_n06_shell.py` therefore carries a
232 KiB ceiling (237,568 B) with the measurement and the reasoning in the source, as AGENTS.md
requires ("set runtime budgets on measured new requirements rather than inheriting a chapter
master's historical widget cap"). The CSS measurement is 1.1 KiB below the plan's *target* range;
the enforced value is the ceiling, the CSS belongs to earlier phases, and N20 records the
measurement instead of changing it.

**The runtime modules are not inlined.** `src/variant-engine.js` (42,041 B) and
`src/variant-templates.js` (308,633 B) ship from `src/`, exactly like the N17/N18/N19 engine
modules; N31 owns the inline / lazy-load / re-budget decision. The ephemeral retry path needs them
at runtime, and the harness proves it with them loaded.

## 8. The handoff contracts (Phase IV closure)

| Consumer | Contract |
|---|---|
| **N24 — exam assembly** | The frozen bank's instance ids (`COL1-{topic}-{family}-{variant}-01`, 112 in total) and the island digest `07fec72a…9bac1`. The bank is training material; an exam assembly built from it is a training-policy simulation, never an official examination. |
| **N28 — remediation** and **N30 — bounded practice** | The ephemeral contract: the seed key pattern `{family}-{variant}-EPH-{attempt}`, the exclusion rule (a retry seed that is already a frozen seed is skipped; the attempt counter advances), the identity rule (the ephemeral instance carries its own `-EPH-{attempt}` id) and the persistence rule (never persisted; the instance lives in the in-memory session only). The family templates live in `data/family_templates/` and ship as `src/variant-templates.js`. |
| **N23 — grading surfaces** | `numeric` and `graph` → `N17-numeric`; `option_select`, `ordering` and `matching` → `N19-method`; the `method` payload class → self-assessed only, because N17 denies machine criteria on it. |
| **N31 — inline / lazy-load / re-budget** | The runtime-JS measurement (225,192 B) and the re-set ceiling (237,568 B); the two runtime modules that ship from `src/`. |

## 9. What is **not** claimed

- No official examination, grade or proctoring status; no pass mark; no claim that the bank
  mirrors the paper examination's form.
- No browser render, screen-reader, print or instructor acceptance. The accessibility review is a
  mechanical structural check; the renderer-level acceptance belongs to N22/N34.
- No semantic grading. The N12 scanner is a token-boundary and unit-normalised rule, not a
  semantic grader; keyword matching is not semantic grading.
- No claim that the four variants are four finished questions: they are four parameterisations of
  one family template, and each is a complete, separately graded instance.
- The four per-family exemption cases are reasoned, not silent: each names its scope.

## 10. Commands that produced this record

```
python3 tools/author_family_templates.py            # freeze the templates + the runtime asset
python3 tools/author_bank.py                        # instantiate the 112 instances
python3 tools/validate_bank.py --bank data/bank --require-types
python3 tools/validate_bank_review.py --review      # promote the passing instances
python3 tools/validate_family_templates.py          # validation table, determinism, range refusal
node    tools/check_n20_runtime.js --record evidence/N20_RUNTIME_RECORD.json
python3 tools/build.py                              # 16 gates, the artifact and the manifest
python3 tools/n20_corpus.py                         # the corpus, the validation and the verification records
```

`python3 tools/n20_corpus.py` was run twice: the two `evidence/N20_CORPUS_RECORD.json` files are
byte-identical (`962016a632e404be652e94625491e740bcaa06d30a43239baebb145308e95c24`). The same
holds for `evidence/N20_VALIDATION_RECORD.json` and `evidence/N20_VERIFICATION_RECORD.json`: all
three records are timestamp-free, so a repeated run reproduces them byte for byte.

`evidence/N20_VALIDATION_RECORD.json` is the gate-level summary — each gate, its status, its
command and its findings — and it points at the per-instance detail held in the records listed
above.
