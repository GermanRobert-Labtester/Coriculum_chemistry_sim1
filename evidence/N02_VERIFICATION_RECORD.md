# N02 verification record — the coverage island, its anchors and its gate

**Task:** N02, Phase I (P0, High risk). **Recorded:** 2026-11-17 (UTC), this environment. **Workspace:** `/home/robertsrff/Chemistry_Med/Chemistry_1st_coriculum`.

**Labels.** The executions in this record are **VERIFIED (2026-11-17, this environment)**: every command and artifact is named, and the corpus runs twice with identical digests. The seven master digests are bound to the **N01 source freeze** recorded under **VERIFIED (2026-11-16)** (`evidence/SOURCE_FREEZE_INVENTORY.json`, ids `C1-MASTER` through `C7-MASTER`). The island's official topic headings, paper format and 180-minute maximum are **PROGRAMME-SOURCED**; the 64-outcome granularity, outcome statements, prerequisite edges and point/minute slots are **PROPOSED** (see `evidence/N02_LABELING_AUDIT.md`).

## 1. What exists now

| Artifact | Role |
|---|---|
| `data/coverage.json` | The authored 64-outcome island source: 7 topics, 64 outcomes, master anchors, master headings, practice bindings, N24 slots and prerequisite edges. |
| `tools/validate_coverage.py` | The schema, count, edge, planning cross-check, labeling and anchor validator. |
| `tools/resolve_coverage_anchors.py` | The anchor resolver over the frozen masters; emits `evidence/N02_ANCHOR_RESOLUTION.json`. |
| `tools/build.py` | The N02 build gate and single-file precursor assembly. The coverage check is the first registered gate (order 1, owner N02). |
| `src/shell.html`, `src/coverage-loader.js`, `src/coverage-view.js` | The minimal single-file shell, the one runtime loader and the two-view renderer. |
| `output/simulator.html` | The N02 precursor artifact: `#sim-coverage` embedded, 64 outcomes rendered from the island alone. **Not the N31 deliverable**; N06 and N31 extend it. |
| `evidence/N02_ANCHOR_RESOLUTION.json` | The 64/64 resolution record bound to the frozen master digests. |
| `evidence/N02_VALIDATION_RECORD.json` | The machine-readable validation pass and label table. |
| `evidence/N02_CORPUS_RECORD.json` | The deterministic corpus record with every fixture and both build digests. |
| `evidence/N02_LABELING_AUDIT.md` | The official-versus-proposed audit, recorded verbatim. |

## 2. The count table and the planning cross-check

Command:

```
python3 tools/validate_coverage.py --report evidence/N02_VALIDATION_RECORD.json
```

Output:

```
PASS coverage-island: 64 outcomes (9/10/11/11/10/8/5); 127 prerequisite edges (20 cross-topic); cycle=None; anchors 64/64 resolved
```

| Topic | Outcomes | Expected | Match |
|---|---|---|---|
| 1 | 9 | 9 | yes |
| 2 | 10 | 10 | yes |
| 3 | 11 | 11 | yes |
| 4 | 11 | 11 | yes |
| 5 | 10 | 10 | yes |
| 6 | 8 | 8 | yes |
| 7 | 5 | 5 | yes |
| **Total** | **64** | **64** | **yes** |

The same command cross-checks the island against `docs/PROGRAMME_COVERAGE_MATRIX.csv`: 64 planning rows, identical outcome ids, 64/64 planning statements preserved in `planning_statement_lv`, 64/64 master anchors and paths identical, 64/64 planned family sets identical. The validator also asserts the island source contains no `\uXXXX` escapes, so the Latvian text is UTF-8 as declared.

**Drift guard.** A future edit that changes the island without the planning source, or the planning source without the island, fails by named assertion. A legitimate count change must update `EXPECTED_TOTAL` / `EXPECTED_PER_TOPIC` in `tools/coverage_common.py` and the `expected` block in `data/coverage.json` in the same commit; the gate message says so explicitly (see §6).

## 3. Schema, edge and cycle fixtures

The corpus (`tools/n02_corpus.py`) mutates scratch copies only; the committed island is untouched. Exact first failures, recorded in `evidence/N02_CORPUS_RECORD.json` under `results`:

| Fixture | Result | Named failure |
|---|---|---|
| Dangling prerequisite edge (P1-01 → P9-99) | `FAIL` | `Dangling prerequisite edge: P1-01 -> P9-99 (target is not an outcome id)` |
| Scratch cycle (P1-01 → P1-02 → P1-01) | `FAIL` | `Cyclic prerequisite edge set: P1-01 -> P1-02 -> P1-01` |
| Deleted outcome (P7-05 removed) | `FAIL` | `Count assertion: expected 64 outcomes (9/10/11/11/10/8/5), found 63. …` |

The cycle detector is a colour-marking DFS over the edge map; it reports the cycle path, not just a boolean. The dangling-edge check names both the source and the target id. Acyclic and dangling-free are therefore gate properties, not authoring hopes.

## 4. Labeling audit

Recorded in full in `evidence/N02_LABELING_AUDIT.md`. The machine-checked summary:

- **PROGRAMME-SOURCED:** the seven topic headings, the paper format (`Kolokvijs notiek klātienē, darbs tiek rakstīts uz papīra.`) and the 180-minute maximum (`Maksimālais pārbaudījumam pieejamais laiks 3 stundas (180 minūtes)`). Every quote is asserted to occur in `evidence/programme_extracted.txt` after whitespace normalisation.
- **PROPOSED:** the 64-outcome granularity, the 9/10/11/11/10/8/5 split, every `statement_lv`, every prerequisite edge, the practice-family binding and the unfilled N24 point/minute slots.
- **Audit note:** the programme PDF's own text carries no outcome-level split; the island's statements are derivations from the master sections, honestly labeled. The masters are the scientific authority; where the planning wording differs, the planning wording is preserved in `planning_statement_lv` and the difference is explained in `comment` (ten entries: P1-02, P2-04, P3-01, P3-04, P4-02, P4-04, P4-08, P5-01, P7-01, P7-04).

The validator fails if any outcome statement loses its `PROPOSED` label, if a changed statement has an empty `comment`, or if the training-policy block no longer states that the programme PDF does not define the outcome-level split.

## 5. Anchor resolution bound to the frozen masters

Command:

```
python3 tools/resolve_coverage_anchors.py --out evidence/N02_ANCHOR_RESOLUTION.json
```

Output:

```
PASS coverage-anchor-resolution: 64/64 anchors resolved, 0 failures
  per-topic resolved/total: 9/9 10/10 11/11 11/11 10/10 8/8 5/5
  bound to frozen masters: C1-MASTER=037f847f78a5b30e, C2-MASTER=35819d730d74909b, C3-MASTER=d64268ce5410004f, C4-MASTER=6ec59d7845049c65, C5-MASTER=04e0efba7f27a0e6, C6-MASTER=0213a11a7c78f9aa, C7-MASTER=a4879bbd2c2519fb
  record: evidence/N02_ANCHOR_RESOLUTION.json (28,848 bytes, sha256=af4a9edafbe149947430fc5975a09267c3721caf22d8ef4991481f0d5603a7bf)
```

| Frozen id | Bytes | SHA-256 | Digest matches N01 freeze |
|---|---|---|---|
| `C1-MASTER` | 1,018,215 | `037f847f78a5b30ebcd761cf2ad3875a9809b607a809850598dedb8af20d7b39` | yes |
| `C2-MASTER` | 969,738 | `35819d730d74909b0b556aa8aee24d5babaa878cfe9a1afd732cb9dc51d8efea` | yes |
| `C3-MASTER` | 1,039,699 | `d64268ce5410004f9002d36b9815a58e25a40435c0b92e81b84d8fd95997888f` | yes |
| `C4-MASTER` | 2,502,506 | `6ec59d7845049c6554c7ca5b3c3d7ff75cabc938fdb1893042b994641d2a2845` | yes |
| `C5-MASTER` | 1,518,065 | `04e0efba7f27a0e6b4b532caa773e1d6a88f69f020e0fdbbd55437646e0fe3bb` | yes |
| `C6-MASTER` | 1,829,918 | `0213a11a7c78f9aa8f8715264f584b4c2c84a8d8f187c0f1028483d65db8bdd7` | yes |
| `C7-MASTER` | 348,993 | `a4879bbd2c2519fb705e6f39cf5c4199d27d3dafcce4a89d272df9cd31ff6b3f` | yes |

**Matching rule:** every `master_anchor` is compared to the master's `id` attribute case-exactly. No lower-casing, trimming or Unicode normalisation is applied. The resolver also asserts that the heading at the anchor equals the island's recorded `master_heading_lv`, so the outcome points at the section the statement was derived from, not merely at any element with that id.

**Negative anchor fixtures:**

| Fixture | Result | Named failure |
|---|---|---|
| Dangling anchor (`#nav-kluda` on P1-01) | `FAIL`, exit 1 | `Anchor resolution failed: P1-01 #nav-kluda not found in C1-MASTER (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html); matching is case-exact` |
| Case variant (`#Stehiometrija` on P1-01) | `FAIL` in the resolver record | `reason: anchor not found with case-exact matching`, `case_insensitive_matches: ["stehiometrija"]` |

The case fixture is deliberately isolated from the planning cross-check so the resolver's own case-exact behaviour is what fails, not the planning comparison.

## 6. Build gate, deleted outcome and refused build

The build registry declares coverage as its first gate:

```
gate 1: coverage (N02) PASS
```

Command with a scratch island missing P7-05:

```
python3 tools/build.py --island /tmp/opencode/n02-corpus/deleted/coverage.json \
  --out /tmp/opencode/n02-corpus/deleted/simulator.html \
  --manifest-out /tmp/opencode/n02-corpus/deleted/manifest.json
```

Exit code `1`. Exact first line:

```
FAIL coverage gate (order 1, owner N02): Count assertion: expected 64 outcomes (9/10/11/11/10/8/5), found 63. If this is an intentional count change, update EXPECTED_TOTAL / EXPECTED_PER_TOPIC in tools/coverage_common.py and the expected block in data/coverage.json in the same commit; the island is then re-authored and re-gated.
```

The same run prints `Refusing build. The artifact was not written.` The scratch output path is absent, so the gate fails closed. The message is an instruction, not just a complaint: a legitimate future count change updates the recorded expectation in the same commit.

**Build parity.** Two fresh builds over unchanged sources produced:

- `output/simulator.html`: 62,350 bytes, SHA-256 `4b1f0ab58282681bd0823ba0d333b3bc50ce76f82ad6f1309eec0f61cc42a44a` in both runs;
- `output/build-manifest.json`: SHA-256 `a8bf077bfac3838299e5a127a39a5b22d9e2690d337dbaeb2292a080adeeee6c` in both runs;
- the committed `output/simulator.html` equals a fresh build byte for byte.

The manifest records the source digests, the build id `cb2f70aba052b1e4`, the `#sim-coverage` canonical digest `f33f61be6755f94426f623ebcfdf267a46c09538da3664df3a55956ffa3009c3` (46,502 bytes) and the gate result. There are no timestamps in content; the emission rule is sorted keys, separators `(",", ":")`, `ensure_ascii=False`, UTF-8, with `</` escaped as `<\/` before embedding.

## 7. Runtime loader, degradation and single-sourcing

Command:

```
node tools/check_coverage_runtime.js
```

Output:

```
PASS coverage-runtime
  baseline: 7 topics, 64 outcomes
  single-source: nav=true, list=true
  truncated: visible=true, names island=true, code=E_COVERAGE_JSON
  deleted outcome: rejected=true, code=E_COVERAGE_COUNT
```

- **Baseline:** the shipped loader reads `#sim-coverage` once, validates the cheap invariants (total 64, unique ids, topic range 1..7, per-topic 9/10/11/11/10/8/5), and both the topic navigation and the outcome index render from the same loaded records.
- **Single-sourcing:** replacing the first topic name in a scratch island copy with `SENTINELA TĒMA N02` changes both the navigation and the outcome index; the baseline name disappears from both. One place, one truth.
- **Truncated island:** the loader throws `E_COVERAGE_JSON`, and the view renders the honest Latvian error naming `#sim-coverage`; `#coverage-nav` and `#coverage-list` are non-blank. There is no blank view.
- **Deleted outcome:** the cheap count invariant rejects the island with `E_COVERAGE_COUNT` (`paredzēti 64 rezultāti, atrasti 63`), and the view names the island. The heavy anchor check remains build-time.

The runtime harness executes the exact shipped script from `output/simulator.html` in a minimal DOM with no external dependencies and no network. A visual check with `lite-shot -e falkon` (no Chrome) painted the page at 1280×1200 and the full page at 1259×3033; both captures are non-blank. The screenshots are review evidence, not an accessibility or print acceptance claim.

## 8. Digest ledger inputs

| Artifact | Bytes | SHA-256 |
|---|---|---|
| `data/coverage.json` | 62,361 | `3d734990d87695899238b86e92a1253c6aebfdaf61f0fc741b5b3d115ff2ce7b` |
| `src/shell.html` | 3,923 | `6c534c758233dd770237b4458abe23524e9b4856dd6bfe8bc7cf9882bbf037e5` |
| `src/coverage-loader.js` | 7,307 | `88d1bf28492a9d2281eda9b626b6421af1c0c1a3ac6bb3ffa95d73413954bd80` |
| `src/coverage-view.js` | 4,582 | `a7485d89d2bc25a638ba638960fe8c2efbedc05f6ca1dad4bd57780f3624f2d7` |
| `tools/coverage_common.py` | 7,298 | `c0b9c6e7f87d6623ebb4f04407bf2b8fba912b8f81cc1b544a4106e7efa2fd79` |
| `tools/validate_coverage.py` | 27,890 | `6aa56a79318eed687e04f06b4a03c95b11b421234402189c275db940cd249ea5` |
| `tools/resolve_coverage_anchors.py` | 7,406 | `bedb3c73d321cd034f8dca86e61c567d4a96857c3b79ff0cfee0fb5b46cb014f` |
| `tools/build.py` | 8,776 | `db9d14497ed026618b05978208e70c3cab4396c15ea072b8a793a9d48f13f8c3` |
| `tools/check_coverage_runtime.js` | 9,627 | `bd9a07c981153f7eb01caaef780cd7d681622df110d89231969e08e38a398d12` |
| `tools/n02_corpus.py` | 13,581 | `203456ec73ee69e98a8bcee3299a58d1a6c64aa846f9b048c21ff07c2b790c08` |
| `output/simulator.html` | 62,350 | `4b1f0ab58282681bd0823ba0d333b3bc50ce76f82ad6f1309eec0f61cc42a44a` |
| `output/build-manifest.json` | 1,607 | `a8bf077bfac3838299e5a127a39a5b22d9e2690d337dbaeb2292a080adeeee6c` |
| `evidence/N02_ANCHOR_RESOLUTION.json` | 28,848 | `af4a9edafbe149947430fc5975a09267c3721caf22d8ef4991481f0d5603a7bf` |
| `evidence/N02_VALIDATION_RECORD.json` | 5,859 | `f9965b009d146d82f80cd3881bef7e1f5feaa083e9f283cc7612b88860282fb7` |
| `evidence/N02_CORPUS_RECORD.json` | 11,580 | `ceee11169835a98103fc6fd005bb20042120bd1a35073c6401a10444e15b2fe0` |
| `evidence/N02_LABELING_AUDIT.md` | see ledger | recorded by the N02 ledger entry |
| `evidence/N02_VERIFICATION_RECORD.md` | see ledger | recorded by the N02 ledger entry |

The corpus ran twice, producing the same `evidence/N02_CORPUS_RECORD.json` digest both times: `ceee11169835a98103fc6fd005bb20042120bd1a35073c6401a10444e15b2fe0` (11,580 bytes). The first run and the second run are both recorded in this record; the ledger carries both.

## 9. Handoffs

The stable outcome vocabulary is `P1-01` … `P7-05` (64 ids). The island contract is handed to:

- **N07 (concept map):** `topics` and `outcomes` are the graph's nodes; `prerequisites` is the frozen edge list. The validator guarantees acyclicity and resolution before N07 re-asserts them.
- **N16 (worked chains):** each chain links to an outcome id and the master anchor, not to a copy of the statement.
- **N24 (assembly bindings):** `bindings.exam_slots`, `bindings.points` and `bindings.minutes` are declared null slots owned by N24. N24 fills them and updates the validator's slot expectations in the same commit.
- **N09 (misconceptions):** outcome ids are the binding vocabulary for signature records.
- **N26 (mastery keys):** the per-outcome state keys are the same 64 ids.
- **N30 (practice paths):** practice entries address outcomes by id; the per-topic counts are the island's, not a local copy.

## 10. Limits and not-performed work

- The 64-outcome granularity is **PROPOSED**, not official. The programme states seven topics, content and skills, a paper format and a 180-minute maximum; it does not enumerate outcomes.
- The statements are derived from the masters' section headings and leads; the masters remain the scientific authority. The validator proves the anchor and heading exist; it does not prove that every statement is the best pedagogical wording. Instructor review remains future work.
- The prerequisite graph is authored training policy. Only Topic 1's explicit `Pirms šīs nodaļas` chains are direct master statements; the rest follows the masters' chapter order.
- The N02 build is a precursor. It proves the coverage gate and the island loading path in one file. It is **not** the N31 idempotent full pipeline, not the N06 start/objectives views, not N32 accessibility, not N34 print/JS fallback and not N35 security audit. Those tasks extend the same registry and shell.
- The visual check used Falkon through `lite-shot`; no Chrome/Chromium was used. It is a paint check, not a WCAG or print acceptance.
- No official exam, grade, institution endorsement or proctoring claim is made anywhere.

## 11. Commands run

```
python3 tools/validate_coverage.py --report evidence/N02_VALIDATION_RECORD.json
python3 tools/resolve_coverage_anchors.py --out evidence/N02_ANCHOR_RESOLUTION.json
python3 tools/build.py
node tools/check_coverage_runtime.js --json
python3 tools/n02_corpus.py          # run twice; identical digest 4451bc91…
python3 tools/verify_preparation.py  # preparation regression check
python3 tools/check_source_inventory.py
lite-shot -e falkon -g 1280x1200 "file://$PWD/output/simulator.html" /tmp/opencode/n02-shots/coverage-light.png
lite-shot -e falkon --cdp --theme light --full-page -g 1280x900 "file://$PWD/output/simulator.html" /tmp/opencode/n02-shots/coverage-light-full.png
```

The preparation verifier and the source-inventory checker results are recorded in the transcript; they are unchanged by N02's additive data, source and tooling files.
