# N31 Verification Record — Idempotent Single-File Build Pipeline

**Date:** 2026-11-19 | **Task:** N31 | **Phase:** Phase VII | **Status:** `PASS`

## 1. Deliverables and SHA-256 Digests

| Artifact / Touchpoint | Role | Size (bytes) | SHA-256 |
|---|---|---:|---|
| [`data/build_policy.json`](../data/build_policy.json) | Build policy artifact (`n31-single-file-build-policy-v1`, v1.0.0-n31): 22 island insertion points, 37-module topological order, stamp rules, offline URL whitelist, sub-budgets | 31,408 | `ad1c05be676675cecf0f065af28b55a6d5d623f4bc5036ef7d3cca45a69e0b0c` |
| [`docs/BUILD_PIPELINE_FORMAT.md`](../docs/BUILD_PIPELINE_FORMAT.md) | N31 build pipeline specification and N32–N40 handoff contract | 10,746 | `90dd174a173d46c1143a68872c820857dceec8caeae8f77014206172877760a2` |
| [`src/shell.html`](../src/shell.html) | HTML5 skeleton (`lang="lv"`, 9 Section 1.2 anchors + `#piemeri`, 22 island slots, 37 topological module placeholders, build stamp meta tags) | 47,427 | `e9bc172ebf7d7b201f59d1b22acabded612ba5f828834ffbc166bbcd70e03f30` |
| [`src/smoke-subset.js`](../src/smoke-subset.js) | In-file smoke harness (27 vectors including `SMK-N31-BUILD-CONTRACT` and live `SimGrading.applyRubricPolicy` slot-state wiring) | 50,275 | `4d04a6d9196a31b1a8ad65f8432a596e14847173c2fed3fab36a734a568e7add` |
| [`tools/validate_n31_build_policy.py`](../tools/validate_n31_build_policy.py) | Build Gate 27 (`build_policy`): forward module dependency order validator, circular dependency fixture, template dry-run & duplicate-insertion fixture, stamp mutation fixture | 22,554 | `852c7b58c52e964edec557c20afafcdce3a364ecadbc04c5ce3dc5e978c7af7c` |
| [`tools/check_artifact.py`](../tools/check_artifact.py) | Standalone static contract checker & Build Gate 28 (`artifact_contract`): anchors, islands, single script + Node `vm.Script` parse + boundary comments, offline URL scan + injection fixture, sub-budget accounting + oversized island fixture | 27,303 | `3f2c7b542fc2dc0922316ade8b307c5beaf2119e114dd7d697af6fe1b8091231` |
| [`tools/build.py`](../tools/build.py) | Idempotent single-file assembly pipeline (28 build gates, 22 canonical islands, 37 wrapped modules, deterministic composite stamp, atomic write) | 96,422 | `cd553703bf56789ee7fb5d9d4e26224ba3c32fbc4167abe89418f024aa002df1` |
| [`tools/byte_budget.py`](../tools/byte_budget.py) | Single byte-budget authority with N31 final inline/re-budget decision and `figures_island` sub-budget | 18,325 | `7f1a86e0b250c05fee105ebfc3b557643d49a8be2af305bdae3124bc8d4d1bba` |
| [`tools/check_n31_runtime.js`](../tools/check_n31_runtime.js) | Runtime harness executing the assembled script from `output/simulator.html`, mapping all 37 module boundary regions, and running all 27/27 in-file smoke vectors | 12,175 | `3dbc36f0a9a41f4f50160f2d26451bbf7d60e91ef6e8c8dff90e192cce35b888` |
| [`tools/n31_corpus.py`](../tools/n31_corpus.py) | Deterministic two-invocation corpus runner for Main Steps A, B, and C | 16,580 | `39b313537c210e2d6bb059e405e9bc21d0c35762f2c90e6e15e15b4f78896cd7` |
| [`output/simulator.html`](../output/simulator.html) | Single-file offline deliverable (`build_id: c05b1a8c29b52c8a`, `composite_digest: c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8`) | 2,649,417 | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` |
| [`output/build-manifest.json`](../output/build-manifest.json) | Build manifest (132 sorted source digests, 22 island digests, 37 module digests, 28 gate results, composition table) | 91,673 | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` |
| [`evidence/N31_VALIDATION_RECORD.json`](N31_VALIDATION_RECORD.json) | Gate 27 (`build_policy`) validation report | 4,767 | `b2fb4eb8bb91962727e4ffaaae90888dc8bbeb06ca08833e7f3a11a1460a630d` |
| [`evidence/N31_RUNTIME_RECORD.json`](N31_RUNTIME_RECORD.json) | N31 runtime & B.1.2 wrapper boundary mapping report | 11,483 | `f2e5b4827cf3ef9d95620c1306332f7622fd10b7650f6823217c42d371333eb2` |
| [`evidence/N31_ARTIFACT_CONTRACT.json`](N31_ARTIFACT_CONTRACT.json) | Gate 28 (`artifact_contract`) standalone checker report | 10,858 | `322481f74bc73215f75101ef77c64d89b3ec99ab4fb5bb3da0ac7be063464b5b` |
| [`evidence/N31_CORPUS_RECORD.json`](N31_CORPUS_RECORD.json) | N31 two-invocation deterministic corpus record | 16,496 | `7233544943e4c3fb018e89ab574074d61dd3b2e9c4080886066202a1d06d0710` |

## 2. Main Step A — Build Policy, Module Order Validation, Template Dry-Run, and Stamp Fixtures

- **A.1.1 Module Order Validation & Circular Dependency Fixture (`PASS`):**
  - All **37** inlined runtime modules (`order` 1..37) and **38** published symbols (`SimCoverage`, `SimCoverage.render`, `SimConventions`, `SimTerms`, `SimPRNG`, `SimFigures`, `SimBank`, `SimGoldenVectors`, `SimLeakScan`, `SimEngines`, `SimGraphScoring`, `SimGraphCapture`, `SimMethodEngine`, `SimMethodCards`, `SimVariantEngine`, `SimChains`, `SimStartView`, `SimConceptDrawer`, `SimConceptMap`, `SimHintDrawer`, `SimTheme`, `SimSession`, `SimInputsRegistry`, `SimInputsComponents`, `SimInputsIntegration`, `SimInputs`, `SimGrading`, `SimFeedback`, `SimAssembly`, `SimExam`, `SimStore`, `SimAnalytics`, `SimMastery`, `SimScheduler`, `SimRemediation`, `SimRevision`, `SimPractice`, `SimSmoke`) resolve their **137** load/init dependency edges strictly forward (`provider.order < consumer.order`).
  - **Circular dependency corner-case fixture:** A scratch pair of modules (`ModuleA` #1 consuming `SimModuleA_TargetB` from `ModuleB` #2, and `ModuleB` #2 consuming `SimModuleB_TargetA` from `ModuleA` #1) is rejected with `E_MODULE_ORDER_VIOLATION: ModuleA (#1) consumes SimModuleA_TargetB from later module ModuleB (#2)`, naming both `ModuleA` and `ModuleB`.
- **A.1.2 Skeleton Template Dry-Run & Duplicate-Insertion Fixtures (`PASS`):**
  - Dry-run assembly over a scratch island and module set fills all **99** template insertion points in [`src/shell.html`](../src/shell.html) (including the 7 core Section 1.2 islands `#sim-coverage`, `#sim-conventions`, `#sim-bank`, `#sim-forms`, `#sim-golden-vectors`, `#sim-terms`, `#sim-analytics`, all 22 JSON islands, 4 JS data projections, 37 module slots, 2 CSS slots, and 34 metadata digest attributes) exactly once with zero leftover `__*__` tokens.
  - **Duplicate insertion call fixture:** Attempting to insert `#sim-bank` twice fails with `E_TEMPLATE_DUPLICATE_INSERTION: duplicate insertion attempted for #sim-bank (__SIM_BANK_JSON__)`.
  - **Duplicate template point fixture:** A template with a duplicated `#sim-coverage` tag fails with `E_TEMPLATE_DUPLICATE_POINT: island insertion point #sim-coverage appears 2 times in skeleton template`.
- **A.1.3 Digest Stamping & One-Byte Mutation Fixtures (`PASS`):**
  - Two stamp computations over unchanged inputs (including reversed input list ordering) emit identical canonical bytes and identical composite digest `e515c7fcb3b207b0c24f3f20070bc3d0180deed7ff23bb2b80a7101db3e48ed6`.
  - A 1-byte mutation in `src/quantity-engine.js` flips only `sources["src/quantity-engine.js"]`, `modules["src/quantity-engine.js"]`, and `composite_digest` (`6cba29b9922365102857df9ca4816c56b17a12c2012b74a8509dc65d77dc269d`).
  - A 1-byte mutation in `data/terms.json` flips only `sources["data/terms.json"]`, `islands["sim-terms"]`, and `composite_digest` (`334df6b78d7a759fcf14a0d26e283efb610b4f9cf8c03544d501bef64f92c781`).

## 3. Main Step B — Assembly, Three-Run Idempotence Table, Atomicity, and Collision Fixtures

- **B.1.1 Deterministic JSON Emission Fixture (`PASS`):**
  - Three insertion-order-varying dictionary permutations containing nested keys, Latvian diacritics (`Šķīdumu molārā koncentrācija un oksidēšanās–reducēšanās līdzsvars`), and `</script>` substrings emit byte-identical 332-byte UTF-8 payloads (`sha256: b19a55d7eeedf4ae693ffa33f90101085ac85758f205e33490cd5b71fb40dfe7`) with readable Latvian characters (`ensure_ascii=False`) and `<\/script>` escaping.
- **B.1.2 Single-Script Wrapper & Runtime Facade Exercise (`PASS`):**
  - The single inline `<script>` element (`1,225,957` bytes, `sha256: d23c6c079ee490935d5e1e6c96c2ce71679776ca1337694ef9fc54090be12722`) parses cleanly through Node's `vm.Script` parser binding.
  - All **37** module regions are bounded by their `/* === MODULE: <path> === */` separator comments in declared topological order followed by `/* === BOOTSTRAP: src/shell.html === */`.
  - Executing the assembled script against the artifact DOM initializes all 37 globals with zero error banners and passes **27/27** in-file smoke vectors (`SMK-N20-BANK-GRADE-VERDICT` grading live in-file via `SimEngines.grade`, `SMK-N22-*` exercising live `SimInputs.buildPayload`, `SMK-N23-*` exercising live `SimGrading.applyRubricPolicy`, and `SMK-N31-BUILD-CONTRACT` passing with 7 core islands and 36 runtime globals).
- **B.1.3 Three-Run Fresh-Process Idempotence Table (`PASS`):**

| Fresh Process Run | Exit Code | `output/simulator.html` Bytes | `output/simulator.html` SHA-256 | `output/build-manifest.json` Bytes | `output/build-manifest.json` SHA-256 | `composite_digest` | Diff vs. Run 1 |
|---|---:|---:|---|---:|---|---|---:|
| Run 1 | `0` | `2,649,417` | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` | `91,673` | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` | `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` | `0 B` |
| Run 2 | `0` | `2,649,417` | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` | `91,673` | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` | `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` | `0 B` |
| Run 3 | `0` | `2,649,417` | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` | `91,673` | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` | `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` | `0 B` |
| Post-Corpus Rebuild 4 | `0` | `2,649,417` | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` | `91,673` | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` | `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` | `0 B` |
| Post-Corpus Rebuild 5 | `0` | `2,649,417` | `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c` | `91,673` | `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99` | `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` | `0 B` |

- **B.1.3 Atomicity & Stale Temp-File Collision Fixtures (`PASS`):**
  - Injecting a corrupt UTF-8 source (`0xff 0xfe` in `--terms`) causes `tools/build.py` to fail with exit code `1` while leaving the existing `simulator.html` (`2,649,417` B, `sha256: d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c`) and `build-manifest.json` (`sha256: eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99`) untouched on disk and `0` stray `.tmp` files.
  - Pre-populating a stale temporary file (`direct_atomic.html.stale_collision.tmp`) from an earlier crash is survived without collision by `_atomic_write`'s unique `NamedTemporaryFile` policy, producing the exact target digest and cleaning up the active temporary file.

## 4. Main Step C — Deliverable Contract Check, Offline URL Scan, and Composition Table

- **C.1.1 Standalone Contract Check (`python3 tools/check_artifact.py`, `PASS`):**
  - `lang`: `"lv"`
  - `charset`: `"utf-8"`
  - `required_section_1_2_anchor_count`: `9/9` (`#sakums`, `#saturs`, `#prakse`, `#eksamens`, `#rezultati`, `#atskats`, `#metodika`, `#druka`, `#iestatijumi` present once each; `11` total `<section id="...">` elements including `#piemeri` and `#exam-review`)
  - `core_section_1_2_island_count`: `7/7` (`#sim-coverage`, `#sim-conventions`, `#sim-bank`, `#sim-forms`, `#sim-golden-vectors`, `#sim-terms`, `#sim-analytics`)
  - `total_island_count`: `22/22` in declared order, all valid canonical JSON matching their `<meta name="sim-*-digest">` stamps
  - `executable_script_count`: `1` (`0` external `<script src>`, `0` external stylesheets)
  - `external_url_count`: `0`
  - `unique_ascii_id_count`: `245` (`0` duplicates, `0` non-ASCII IDs, `0` unresolved internal `#anchor` links)
- **C.1.2 Offline URL Scan & Injected-URL Fixture (`PASS`):**
  - `output/simulator.html` contains `0` external `http://` or `https://` URLs.
  - Injecting `<script src="https://cdn.example.invalid/external-tracker.js"></script>` at line 11 of a scratch artifact fails `scan_offline_urls` naming the URL (`https://cdn.example.invalid/external-tracker.js`), line number (`11`), and line context.
- **C.1 Sub-Budget Composition Table & Oversized Scratch Island Fixture (`PASS`):**

| Segment | Description | Measured Bytes | Measured KiB | Share of Deliverable | Declared Section 1.3 Band | Enforced Ceiling | Status |
|---|---|---:|---:|---:|---|---|---|
| `bank_island` | Frozen `#sim-bank` JSON island (112 reviewed instances across 28 families) | `249,798` | `243.9 KiB` | `9.43%` | `200–420 KiB` (`204,800–430,080 B`) | `420 KiB` (`430,080 B`) | `PASS (58.08%)` |
| `figures_island` | Declarative SVG figure specs (`#sim-figures`, 45 T1–T7 records) | `142,579` | `139.2 KiB` | `5.38%` | `60–140 KiB` (`61,440–143,360 B`) | `140 KiB` (`143,360 B`) | `PASS (99.46%)` |
| `other_islands` | Remaining 20 JSON islands (`#sim-coverage`, `#sim-conventions`, `#sim-forms`, `#sim-golden-vectors`, `#sim-terms`, `#sim-analytics`, policies, chains, engines, method cards, grading) | `932,992` | `911.1 KiB` | `35.21%` | — | — | `PASS` |
| `runtime_js_code` | 37 inlined runtime JS modules + bootstrap + module boundary comments | `1,152,126` | `1,125.1 KiB` | `43.49%` | `120–220 KiB` (`122,880–225,280 B`) | `1,168 KiB` (`1,196,032 B`, N31 re-budget) | `PASS (96.33%)` |
| `embedded_js_data` | 4 canonical JS data projection globals (`COVERAGE_INVARIANTS`, `CONCEPT_DRAWER_DATA`, `ANCHOR_REGISTRY`, `RECALL_LAYERS_DATA`) | `73,830` | `72.1 KiB` | `2.79%` | — | — | `PASS` |
| `css` | Inline `<style>` block (`src/tokens.css` + `src/styles.css`) | `59,899` | `58.5 KiB` | `2.26%` | `40–80 KiB` (`40,960–81,920 B`) | `80 KiB` (`81,920 B`) | `PASS (73.12%)` |
| `template_overhead` | HTML5 skeleton markup, Latvian copy, meta digest tags, and `<script>`/`<style>` wrappers | `38,192` | `37.3 KiB` | `1.44%` | — | — | `PASS` |
| **`artifact_total`** | **Complete single-file deliverable [`output/simulator.html`](../output/simulator.html)** | **`2,649,417`** | **`2,587.3 KiB`** | **`100.00%`** | **`700–1,400 KiB` (`716,800–1,433,600 B`)** | **`2,624 KiB` (`2,686,976 B`, N31 re-budget)** | **`PASS (98.60%)`** |

  - **Oversized scratch island fixture:** Injecting a `462,848` B `#sim-bank` island fails `measure_budgets` naming `bank_island`; injecting a `159,744` B `#sim-figures` island fails `measure_budgets` naming `figures_island`.

## 5. Frozen Deliverable Handoff Contract for N32–N40

- **Deliverable path:** [`output/simulator.html`](../output/simulator.html) (`2,649,417` bytes / `2,587.3 KiB`, SHA-256 `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c`)
- **Build manifest path:** [`output/build-manifest.json`](../output/build-manifest.json) (`91,673` bytes, SHA-256 `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99`)
- **Composite source/island/module stamp:** `c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8` (`build_id: c05b1a8c29b52c8a`)
- **Standalone QA contract checker for N39:** `python3 tools/check_artifact.py --html output/simulator.html --manifest output/build-manifest.json --policy data/build_policy.json`
