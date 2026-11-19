# N31 — Idempotent Single-File Build Pipeline Format and Contract

**Owner Task:** N31 | **Phase:** Phase VII | **Policy Artifact:** [`data/build_policy.json`](../data/build_policy.json) | **Build Entry Point:** [`tools/build.py`](../tools/build.py) | **Contract Checker:** [`tools/check_artifact.py`](../tools/check_artifact.py)

## 1. Purpose and Scope

The N31 build pipeline assembles every Phase I–VI deliverable (`N01`–`N30`) into a single offline deliverable [`output/simulator.html`](../output/simulator.html) and emits its companion cryptographic fingerprint [`output/build-manifest.json`](../output/build-manifest.json):

- **Plain Python 3 assembly:** No bundler, transpiler, npm package, CDN, or network dependency is permitted at build time or runtime.
- **Deterministic idempotence:** Running `python3 tools/build.py` repeatedly in fresh processes over unchanged sources produces byte-identical [`output/simulator.html`](../output/simulator.html) and byte-identical [`output/build-manifest.json`](../output/build-manifest.json).
- **Atomic deliverable write:** Both outputs are written to unique temporary files in `output/`, flushed and `os.fsync`-synced, and atomically replaced via `os.replace`. Any validation, encoding, or budget error leaves any previous deliverable on disk untouched.

## 2. HTML Skeleton and Island Insertion Order

The HTML skeleton [`src/shell.html`](../src/shell.html) declares:

- `<html lang="lv">`, `<meta charset="utf-8">`, `<meta name="viewport" content="width=device-width, initial-scale=1">`, and `<meta name="color-scheme" content="light dark">`.
- Metadata stamp `<meta>` elements:
  - `meta[name="sim-build"]` (16-hex prefix of `composite_digest`)
  - `meta[name="sim-build-version"]` (`1.0.0-n31`)
  - `meta[name="sim-build-date"]` (`2026-11-19`)
  - `meta[name="sim-build-composite-digest"]` (64-hex SHA-256 `composite_digest`)
  - Per-island SHA-256 digest `<meta name="sim-*-digest">` tags.
- The 9 blueprint Section 1.2 top-level ASCII `<section>` landmarks (`#sakums`, `#saturs`, `#prakse`, `#eksamens`, `#rezultati`, `#atskats`, `#metodika`, `#druka`, `#iestatijumi`) plus the auxiliary worked-example section `#piemeri`, each present exactly once with `aria-labelledby`.
- **22 inline JSON islands** (`<script type="application/json" id="...">`), beginning with the 7 core Section 1.2 islands in declared order:
  1. `#sim-coverage` (`data/coverage.json`, N02)
  2. `#sim-conventions` (`data/conventions.json`, N03)
  3. `#sim-bank` (`data/question_bank_schema.json` + 28 `data/bank/*.json`, N04/N20)
  4. `#sim-forms` (`data/forms.json`, N04/N24)
  5. `#sim-golden-vectors` (`data/golden_vectors.json`, N05)
  6. `#sim-terms` (`data/terms.json`, N10)
  7. `#sim-analytics` (`data/analytics_schema.json`, N25)
  followed by the 15 extended policy, figure, chain, and engine islands (`#sim-mastery-policy`, `#sim-scheduler-policy`, `#sim-remediation-policy`, `#sim-revision-policy`, `#sim-practice-policy`, `#sim-figures`, `#sim-chains`, `#sim-engines`, `#sim-graph-scoring`, `#sim-method-cards`, `#sim-method-engine`, `#sim-exam-policy`, `#sim-response-types`, `#sim-grading-policy`, `#sim-feedback-classification`).

All JSON islands are serialized with `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)` and `</` escaped as `<\/` so Latvian diacritics remain human-readable UTF-8 while dictionary key order is invariant.

## 3. Topological Runtime Module Order (37 Inlined Modules)

Inside the single executable `<script>` element, 4 canonical data projections (`COVERAGE_INVARIANTS`, `CONCEPT_DRAWER_DATA`, `ANCHOR_REGISTRY`, `RECALL_LAYERS_DATA`) precede the 37 runtime modules. Every module is preceded by its boundary separator comment `/* === MODULE: <path> === */`, and every `consumes` contract resolves strictly forward (`provider.order < consumer.order`):

| Order | Module Path | Owner | Provides | Consumes (Forward Load/Init) |
|---:|---|---|---|---|
| 1 | `src/coverage-loader.js` | N02 | `SimCoverage` | — |
| 2 | `src/conventions-loader.js` | N03 | `SimConventions` | — |
| 3 | `src/terms-loader.js` | N10 | `SimTerms` | — |
| 4 | `src/prng.js` | N05 | `SimPRNG` | — |
| 5 | `src/figure-framework.js` | N11 | `SimFigures` | `SimTerms` |
| 6 | `src/bank-loader.js` | N04 | `SimBank` | `SimFigures` |
| 7 | `src/golden-vectors-loader.js` | N05 | `SimGoldenVectors` | `SimPRNG`, `SimBank` |
| 8 | `src/leak-scan.js` | N12 | `SimLeakScan` | `SimTerms`, `SimFigures` |
| 9 | `src/quantity-engine.js` | N17 | `SimEngines` | `SimConventions`, `SimTerms`, `SimFigures` |
| 10 | `src/graph-scoring-engine.js` | N18 | `SimGraphScoring` | `SimConventions`, `SimFigures` |
| 11 | `src/graph-capture.js` | N18 | `SimGraphCapture` | `SimGraphScoring` |
| 12 | `src/method-engine.js` | N19 | `SimMethodEngine` | `SimTerms` |
| 13 | `src/method-card-view.js` | N19 | `SimMethodCards` | `SimTerms`, `SimMethodEngine` |
| 14 | `src/variant-engine.js` | N20 | `SimVariantEngine` | `SimPRNG`, `SimFigures`, `SimConventions` |
| 15 | `src/chain-view.js` | N16 | `SimChains` | `SimFigures` |
| 16 | `src/coverage-view.js` | N06 | `SimCoverage.render` | `SimCoverage`, `SimTerms` |
| 17 | `src/start-view.js` | N06 | `SimStartView` | `SimCoverage` |
| 18 | `src/concept-drawer.js` | N07 | `SimConceptDrawer` | `SimCoverage`, `SimFigures`, `SimChains` |
| 19 | `src/concept-map.js` | N07 | `SimConceptMap` | `SimCoverage`, `SimConceptDrawer` |
| 20 | `src/hint-drawer.js` | N08 | `SimHintDrawer` | `SimTerms`, `SimConceptDrawer` |
| 21 | `src/theme-toggle.js` | N06 | `SimTheme` | `SimTerms` |
| 22 | `src/compiled/session.js` | N21 | `SimSession` | — |
| 23 | `src/compiled/inputs/registry.js` | N22 | `SimInputsRegistry` | `SimTerms` |
| 24 | `src/compiled/inputs/components.js` | N22 | `SimInputsComponents` | `SimInputsRegistry`, `SimGraphScoring`, `SimGraphCapture`, `SimBank` |
| 25 | `src/compiled/inputs/integration.js` | N22 | `SimInputsIntegration`, `SimInputs` | `SimInputsRegistry`, `SimInputsComponents`, `SimSession` |
| 26 | `src/compiled/grading.js` | N23 | `SimGrading` | `SimEngines`, `SimGraphScoring`, `SimMethodEngine`, `SimInputsRegistry`, `SimInputsIntegration` |
| 27 | `src/compiled/feedback.js` | N23 | `SimFeedback` | `SimGrading`, `SimTerms`, `SimChains`, `SimMethodCards` |
| 28 | `src/compiled/assembly.js` | N24 | `SimAssembly` | `SimPRNG`, `SimFigures`, `SimVariantEngine` |
| 29 | `src/compiled/exam.js` | N21 | `SimExam` | `SimSession`, `SimAssembly` |
| 30 | `src/compiled/store.js` | N25 | `SimStore` | — |
| 31 | `src/compiled/analytics.js` | N25 | `SimAnalytics` | `SimStore`, `SimCoverage`, `SimGrading`, `SimTheme` |
| 32 | `src/compiled/mastery.js` | N26 | `SimMastery` | `SimStore`, `SimCoverage`, `SimBank` |
| 33 | `src/compiled/scheduler.js` | N27 | `SimScheduler` | `SimMastery`, `SimCoverage`, `SimBank`, `SimStore`, `SimTerms` |
| 34 | `src/compiled/remediation.js` | N28 | `SimRemediation` | `SimStore`, `SimCoverage`, `SimBank`, `SimTerms`, `SimConceptDrawer`, `SimChains`, `SimMastery`, `SimVariantEngine` |
| 35 | `src/compiled/revision.js` | N29 | `SimRevision` | `SimStore`, `SimCoverage`, `SimBank`, `SimTerms`, `SimFeedback`, `SimMastery`, `SimRemediation`, `SimConceptDrawer`, `SimChains` |
| 36 | `src/compiled/practice.js` | N30 | `SimPractice` | `SimCoverage`, `SimBank`, `SimTerms`, `SimStore`, `SimExam`, `SimHintDrawer`, `SimChains`, `SimConceptDrawer`, `SimInputsRegistry`, `SimInputsComponents`, `SimInputsIntegration`, `SimEngines`, `SimGraphScoring`, `SimMethodEngine`, `SimGrading`, `SimFeedback`, `SimMastery`, `SimRemediation`, `SimVariantEngine` |
| 37 | `src/smoke-subset.js` | N31 | `SimSmoke` | All 36 globals above |

### N31 Inline vs. Authoring Asset Decision

- **Inlined in `output/simulator.html` (all 11 Phase IV–V engine/input/grading runtime modules):** `src/quantity-engine.js`, `src/graph-scoring-engine.js`, `src/graph-capture.js`, `src/method-engine.js`, `src/method-card-view.js`, `src/variant-engine.js`, `src/compiled/inputs/registry.js`, `src/compiled/inputs/components.js`, `src/compiled/inputs/integration.js`, `src/compiled/grading.js`, and `src/compiled/feedback.js` are all inlined so the single-file deliverable is 100% self-contained for practice, exam capture, grading, feedback, and in-file smoke verification.
- **Kept in `src/` as an authoring-only asset (`inlined_in_artifact: false`):** `src/variant-templates.js` (`SimFamilyTemplates`, 308.6 KiB raw generator templates used to generate the 112 frozen instances in `data/bank/*.json`) remains in `src/` because all 112 reviewed question instances are already embedded in `#sim-bank`.

## 4. Digest Stamping and Manifest Contract

`tools/build.py` computes SHA-256 over every source file (sorted lexicographically by `path`), every emitted JSON island, and every raw/inlined JS module, then computes a deterministic `composite_digest`:

```json
{
  "version": "1.0.0-n31",
  "iso_date": "2026-11-19",
  "policy_id": "n31-single-file-build-policy-v1",
  "sources": [{"path": "...", "bytes": 123, "sha256": "..."}],
  "islands": [{"island_id": "...", "bytes": 123, "sha256": "..."}],
  "modules": [{"order": 1, "path": "...", "raw_sha256": "...", "inlined_sha256": "..."}]
}
```

Any 1-byte mutation in any source file flips its entry in `sources`, the affected island or module digest, `composite_digest`, `build_id`, and `output.sha256`.

## 5. Static Contract Checker (`tools/check_artifact.py`) and Budget Accounting

[`tools/check_artifact.py`](../tools/check_artifact.py) can be run standalone (`python3 tools/check_artifact.py`) or via Build Gate 28 (`artifact_contract`) and N39's QA runner. It asserts:

1. `lang="lv"` on `<html>`.
2. All 9 Section 1.2 ASCII landmarks (`#sakums`..`#iestatijumi`) + `#piemeri` present once each.
3. All 7 core Section 1.2 islands (`#sim-coverage`, `#sim-conventions`, `#sim-bank`, `#sim-forms`, `#sim-golden-vectors`, `#sim-terms`, `#sim-analytics`) and all 22 declared JSON islands present in exact order with valid JSON matching their `<meta name="sim-*-digest">` stamps.
4. Exactly 1 executable `<script>` element (`0` external `<script src>`), containing all 37 `/* === MODULE: <path> === */` boundary comments in declared order and `/* === BOOTSTRAP: src/shell.html === */`, and parsing cleanly through Node's `vm.Script` parser binding.
5. Zero external URLs (`http://` or `https://`) outside the declared `<!-- LICENSE-UPSTREAM: ... -->` comment whitelist (`0` total URLs in the deliverable).
6. V-10 unique ASCII-only IDs and 100% internal `#anchor` link resolution.
7. Sub-budget accounting against [`tools/byte_budget.py`](../tools/byte_budget.py) (`artifact_total`, `runtime_js_code`, `css`, `bank_island`, `figures_island`), failing loudly by segment name if any sub-budget ceiling is exceeded.
