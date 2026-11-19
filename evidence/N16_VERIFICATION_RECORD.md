# N16 Verification Record — EX01–EX14 worked example chains

Date: 2026-11-17. Scope: chain authoring data, validator and runtime checks in this workspace. This is not instructor, scientific-expert, accessibility or physical-print acceptance. The fourteen chains are authored training material, not official colloquium questions. N19 (method cards) and N20 (practice bank) are not implemented; their chain links are a validated forward contract, not authored cards or items.

## 1. What was built

| Item | Path | Note |
|---|---|---|
| Chain format | `docs/CHAIN_FORMAT.md` | Field tables, reveal contract, sealing scheme, citation rules, print rules |
| Chain schema | `data/chain_schema.json` | Format version, field registry, recompute ops, figure roles, honesty rules |
| Chain records (14) | `data/chains.json` | EX01–EX14, 69 steps, two chains per programme topic |
| Forward references | `data/chain_references.json` | 14 N19 method-card and 14 N20 practice-item declarations, `declared-pending` |
| Renderer | `src/chain-view.js` | Collapsed reveal, per-step and reveal-all controls, exact re-collapse, figure mount, named errors |
| Styles | `src/styles.css` | Chain component, print rules, revealed-step and collapsed-note behaviour |
| Shell | `src/shell.html` | `#piemeri` section, `#chain-index`, `#sim-chains` island, `#sim-chains-error` |
| Concept integration | `src/concept-drawer.js`, `data/concept_summaries.json` | 33 authored-N16 slots mount chains from the same island |
| Validator | `tools/validate_chains.py` | Schema, Decimal recompute, citation resolution, sealing, leak scans, persistence scan, planted leak |
| Build wiring | `tools/build.py` | Chain gate order 12, sealed island emission, manifest `chains_island` |
| Smoke | `src/smoke-subset.js` | `SMK-N16-CHAINS-REVEAL` with fixed EX03 pre/reveal digests |
| Runtime harness / corpus | `tools/check_n16_runtime.js`, `tools/n16_corpus.py` | Runtime proof, per-chain digests, print renders, byte accounting |

## 2. Chain records

All exact anchors, conventions refs and outcome links resolve against the frozen N02/N03 data; the validator reports zero dangling references.

| Chain | Topic | Steps | Numeric | Outcomes | Figure (step) |
|---|---|---|---|---|---|
| `EX01` | 1 | 7 | 6 | P1-01 | `FIG-T1-CHAIN-AL-OXIDATION` (S2) |
| `EX02` | 1 | 6 | 4 | P1-06, P1-05 | `FIG-T1-CHAIN-STRUCTURAL-MOLBRIDGE` (S2) |
| `EX03` | 2 | 3 | 3 | P2-07, P2-05 | `FIG-T2-BURETTE-DELIVERED-GRADE` (S1) |
| `EX04` | 2 | 4 | 3 | P2-05, P2-10, P2-03 | `FIG-T2-CHAIN-PREFIX-SCALE` (S1) |
| `EX05` | 3 | 5 | 3 | P3-04, P3-06, P3-05 | `FIG-T3-CONC-BASES-BRIDGE` (S3) |
| `EX06` | 3 | 6 | 4 | P3-10, P3-11 | `FIG-T3-DILUTION-PIPETTE-FLASK` (S5) |
| `EX07` | 4 | 5 | 4 | P4-08, P4-10, P4-11 | `FIG-T4-ENERGY-EXOTHERMIC` (S3) |
| `EX08` | 4 | 6 | 5 | P4-03, P4-02, P4-07 | `FIG-T4-HESS-CO2` (S4) |
| `EX09` | 5 | 5 | 4 | P5-08, P5-09, P5-10 | `FIG-T5-LIN-FIRST` (S5) |
| `EX10` | 5 | 6 | 3 | P5-07, P5-03, P5-06 | `FIG-T4-ENERGY-CATALYZED` (S3) |
| `EX11` | 6 | 4 | 3 | P6-08, P6-05, P6-07 | `FIG-T67-TITR-MASTER-KMNO4` (S2) |
| `EX12` | 6 | 4 | 2 | P6-03, P6-02 | — |
| `EX13` | 7 | 4 | 2 | P7-03, P7-02 | `FIG-T67-CAL-NEAR-EDGE` (S3) |
| `EX14` | 7 | 4 | 4 | P7-04, P7-03, P7-05 | `FIG-T67-CAL-MASTER` (S1) |

The two topic 5 chains are anchored in topic 5 outcomes; `EX10` deliberately reuses the topic 4 catalysed-energy figure because the chain teaches the catalyst comparison while the outcome links remain `P5-*`. `EX10/S6` also covers P5-06 (multi-step mechanism and rate-determining step), closing the mechanism-chain handoff from N14/N15; the P5-06 figure slot stays a declared placeholder because no separate mechanism figure is owed. `EX12` is the one chain without a figure reference; it teaches the half-life/decay method symbolically after `EX11`'s figure-bearing titration chain.

## 3. Recompute and citation proof (A.1.1–A.1.3)

The validator independently recomputes every numeric step from the declared inputs and the conventions entries with Python `Decimal`; it does not read the authored result as an operand. Recomputed and declared values agree for all 50 numeric steps.

| Chain | Steps | Recompute PASS | Citation refs | Multi-citation steps |
|---|---|---|---|---|
| `EX01` | 7 | 6/6 | 8 | 1 |
| `EX02` | 6 | 4/4 | 11 | 4 |
| `EX03` | 3 | 3/3 | 6 | 3 |
| `EX04` | 4 | 3/3 | 7 | 3 |
| `EX05` | 5 | 3/3 | 9 | 3 |
| `EX06` | 6 | 4/4 | 10 | 4 |
| `EX07` | 5 | 4/4 | 10 | 5 |
| `EX08` | 6 | 5/5 | 12 | 6 |
| `EX09` | 5 | 4/4 | 9 | 3 |
| `EX10` | 6 | 3/3 | 11 | 5 |
| `EX11` | 4 | 3/3 | 8 | 4 |
| `EX12` | 4 | 2/2 | 10 | 4 |
| `EX13` | 4 | 2/2 | 8 | 4 |
| `EX14` | 4 | 4/4 | 9 | 4 |
| **Total** | **69** | **50/50** | **128 conventions (122 step + 6 given) + 87 anchors** | **53** |

Citation counts also include 13 figure references and 35 outcome links. The 53 multi-citation steps are the demonstrated multi-citation form: a step may cite a unit conversion and a rounding/tolerance rule together. Example: `EX01/S1` cites `rounding.rule` and `compound_molar_masses.compounds[Mg(OH)2]` in one step; both resolve and neither is silently replaced by a paraphrase.

A copied `EX03` with `S2`'s declared value changed to `326` is run through the real validator; it fails by chain and step id with `EX03/S2: recompute mismatch: got 325, declared 326` and `EX03/S2: display '326' is not a correct rounding of 325`, proving the check bites at the step level rather than at chain granularity. The validator also records an inline comparison of the real `EX03/S2` recompute against a deliberately wrong `326`. The full 50-row recompute table, 128-row resolve table and 87 master-anchor checks are in `evidence/N16_VALIDATION_RECORD.json`; the scratch-run errors are in `evidence/N16_CORPUS_RECORD.json`.

## 4. Leak-free delivery and reveal semantics (B.1.1–B.1.3)

The runtime island is a sealed projection: each hidden step's `{value, display_lv, unit, sig_figs, reasoning_lv}` is JSON-serialised and XORed with a per-step SHA-256-derived stream key, then base64-encoded. The pre-reveal DOM contains only the banner, title, subtitle, master citation, givens, step quantity/statement, figure placeholder and controls. Results are empty `<div hidden>` elements; reasoning is not present.

| Proof | Result |
|---|---|
| Chains / steps | 14 / 69 |
| Pre-reveal DOM leaks | 0 |
| Sealed island leaks | 0 |
| Pre-reveal fixture digest | `12685d9d8cab31a71aa2810dd367dc8c2d84f3ef43ade8c1fe5f62e78fa31379` |
| Sealed island digest (`#sim-chains`) | `4b61010688da6805687f23ed2c7aa6c15949a26c966778ab4c23db0969626c27` |
| Sealed payload round trip | 69/69 |
| Planted leak | PASS — `EX03/S1` injected `16,25` into the pre-reveal fixture; detected as `result_value` by chain and step |
| Persistence scan | PASS — no `localStorage`, `sessionStorage`, cookie, IndexedDB, history or location API in `src/chain-view.js` |

The leak scan is unit-normalised: numeric tokens are compared with digit/decimal boundaries and unit spellings are normalised, so `16.25`, `16,25` and `16,25 mL` cannot hide a result. A value that appears in the citation heading is scanned too; the raw canonical representation of `EX06/S4` is stored as `10.0` (display `10,0`) so the source label “Nodaļa 10.” is not misread as a bare answer. The `pre_reveal_visible_text` function includes the master heading and anchor, so citation text is not an unscanned channel.

Per-chain DOM digests from the runtime harness (14 chains, pre-reveal → fully revealed → re-collapse):

| Chain | Pre-reveal | Fully revealed | Re-collapse = pre |
|---|---|---|---|
| `EX01` | `d2b76fc9140c4415a23d65bf265d583574291ae19b6dd01d3a5eb5f478d470c9` | `3b519bf1389d11ed818eab9b25889516a58cae9878ff5f52810fe187b618359d` | yes |
| `EX02` | `540a2922a3be61296abf68fd5e10096b4d081f6d4ece405da7d7f9c224b0967a` | `0fa5ab2208d51af975bb1e07addc6ee102a99125f904998d34e4a0936b287861` | yes |
| `EX03` | `cb23f17f6c16f5c64d333ac923aa69da8d22a17095d2cf0d2788efde8f1c6ec8` | `44e190551bfefecd40628e2b415415ba550991720eeed077796909ca3bc90b50` | yes |
| `EX04` | `ffc2238a555c7ed907b522192210346c24813efdc904b13d27c8d9acd0a66aec` | `a80d436f60cf4ca4ecb9e0e147492d6f2efeb2c594c52b11f05c0c36b5de126e` | yes |
| `EX05` | `dc90c9878a10e326c9a3f62cf5d15c7189db9d771bc88ecd774906f26bbb5458` | `dc72410e360a2ced15eae3d75aa2c0a9d700361bca89a74be18d3e5254bcadc8` | yes |
| `EX06` | `a281be5e4d1eaf8d1abf9ee54a6989ea6e1b1c1e12dd0fc8818fd4fbafca90b2` | `1c18ec4756e364e4b3abcf714fd300b3fa003f96abb332787bba032bb1852e25` | yes |
| `EX07` | `633811bc3d9bfffeed0bbb88be4be0485f8939e95e7c1238ac9e0734719c3bfd` | `be920855d226e743cac90bfafbe9fd338ffdc057335a0d147898e20a9e34673f` | yes |
| `EX08` | `50afef7b5077bd4497207b1f1f8e61046185b2e12294bceac8a6074ba6a2102b` | `58c0bcb96f7b9b5b70bc0bc4c1c8b75f0d0024861687130a9f764d9185c00b60` | yes |
| `EX09` | `47835faf77bbe06bf34b7ec7a419a9ebcd7405d1ae934ac1ed9ce61608fdd798` | `c1edb057c6bf34d6a55fa80e86c8d4f28ae6daba94da2e771d32bd604fe51292` | yes |
| `EX10` | `357442b3fb608045718a2846c7db3511f76e2edffedc8f8cf66df4a35d8e09f2` | `46e00ad90c21f3fbaf2fdb71fc6a0a5f8179dc21a8665f32ce822d914b4cc401` | yes |
| `EX11` | `e04be5551205269d2dc50bd7eee7241e5e1a69ebf1719f4254bf4e1ed2c9138e` | `ebd8dc629ac7941395e4ae1e70cf4a6058e0306cb86f1dd550009554c409a7d5` | yes |
| `EX12` | `f597cb3ea1b1ebeab63ea258c757550922c5b4d870d8abc1953dbf2adf278378` | `1f9660371f50803071de33a420807bcd4aef45e9dcf2920a81914221427d1eae` | yes |
| `EX13` | `b5be900fbc92f7be0c45aa60972e8e955544e56810703f33992dd036ba3033a1` | `7ef03944880ce12666e28136438ee09653c16dc9224d443d9713ad2c373db0a8` | yes |
| `EX14` | `51417b1b7db645a8e338b78a21fb5dac74bed8a298e6483ec40ac190290a44f4` | `34f533be539942a2bd20c39b06248f360adad439fb8b9a39d0ca006683c64f97` | yes |

The harness also asserts that a revealed first step leaves every later step's result hidden and empty, that reveal-all asks once through `chain-confirm` and only `Jā, atklāt visus` performs the reveal, that `Nē` cancels, and that re-collapse rebuilds the article to the exact pre-reveal serialization. Where the first step carries a figure (`EX03`, `EX04`, `EX14`), the harness asserts that the figure host is mounted and contains no `.chain-figure-error`. The in-file smoke vector `SMK-N16-CHAINS-REVEAL` fixes `EX03`'s pre-reveal digest `b5273a658c4b6f3d52167c96c7bb49c2c852b6bd0c1e0d25e46353a7238fd797` and revealed digest `88609f5b1d246234e6a39664f519ecb05b1d9fd8fe8ea9654a7f6dcfb6910923`; it passes in the runtime harness.

## 5. Integration and focus (C.1.1)

The concept drawer mounts an `authored-N16` chain slot for 33 of the 64 outcomes. The map-to-chain path (`P2-07` → `EX03`) closes the drawer and restores focus to `karte-btn-P2-07`. The item-to-chain path (`EX11` from a synthetic practice item) restores focus to `n16-item-trigger` on a normal close and also when the drawer is closed while the reveal-all confirmation is open; the confirmation does not trap focus after the drawer is gone.

The item-context scan uses the synthetic item keys `0.03125 mol/L` and `4.20 g`; neither appears in the chain island, the chain DOM or the EX11 reveal data. This is a forward-compatible fixture, not an authored N20 item.

`data/chain_references.json` declares 14 method-card references (`MC-EX01`…`MC-EX14`, consumer N19) and 14 practice-item references (`PI-EX01`…`PI-EX14`, consumer N20), plus chain back-links. All 28 rows are schema-valid and resolve to existing chain ids. Their status is `declared-pending-N19` / `declared-pending-N20`; no method card or practice item has been authored yet, so the reference table is a contract for those tasks rather than proof of implemented cards.

## 6. Print honesty (C.1.2)

The print fixtures use the artifact's token and stylesheet blocks with `data-theme="light"`, then Falkon through `lite-shot --cdp --theme light --media print --full-page`. They are browser print-media emulations, not physical printer proofs.

| Render | Path | PNG bytes | SHA-256 | Colours | Inspection |
|---|---|---|---|---|---|
| Collapsed `EX03` | `evidence/N16_PRINT_COLLAPSED.png` | 55,424 | `5c3169e3c1f2799dc9bfbd69f297d943f0d777b0ecd0ba3c86964b70b0fe1425` | 1,951 | Statements and givens visible; no result values or reasoning; figure placeholder only; the interactive note “Pamatojums ir interaktīvs…” is printed; 800×1100 |
| Fully revealed `EX03` | `evidence/N16_PRINT_REVEALED.png` | 118,125 | `5903a96cb97091adb9eb9d3dcc32bc9244bf016bfba35ad293c8700fcd172fe7` | 4,089 | All three results and reasoning printed; the N15 burette figure is mounted with its caption; no collapsed note; 779×1407 full page |

The collapsed render deliberately keeps the figure placeholder `FIG-T2-BURETTE-DELIVERED-GRADE` rather than the answer-bearing figure, and keeps the note that the reasoning is interactive. The revealed render prints the already-revealed results and reasoning; the print rule is `.chain-step[data-revealed="true"] .chain-result { display:block !important }`, with results hidden for unrevealed steps. A chain that has never been opened therefore cannot silently print its answers.

## 7. Build gates, parity and byte accounting (C.1.3)

- `python3 tools/build.py`: PASS. All 12 gates pass, including chains at order 12. The artifact is `output/simulator.html`, 937,559 B, SHA-256 `87cbd6d82739f659c89d8cbd4beec246b27dcc030e2a01fa2e7bbe15deee3593`, build id `71042b46f5e17967`.
- `tools/n16_corpus.py`: PASS. Two full runs (the second to `/tmp/opencode/n16_second.json`) produce byte-identical records, SHA-256 `01efc1def1b63529add1ee6e9aa613c464d7e9ddea643feeefacf0a396e350f1`; validation parity is true and the scratch recompute fails by `EX03/S2`.
- Runtime harness: `node tools/check_n16_runtime.js` PASS, 14 chains / 69 steps, 14 index mounts, parity true, all ten checks true, smoke 10/10 including `SMK-N16-CHAINS-REVEAL`.
- Prior runtime harnesses: `check_coverage_runtime`, `check_conventions_runtime`, `check_golden_vectors_runtime`, `check_n06_runtime`, `check_n07_runtime`, `check_n08_runtime`, `check_n10_runtime`, `check_n11_runtime`, `check_n12_runtime`, `check_n13_runtime`, `check_n14_runtime` and `check_n15_runtime` all pass. `check_bank_runtime.js` requires a 112-instance N20 bank and is not available yet.
- `python3 tools/verify_preparation.py --repo-local --report evidence/REPO_LOCAL_VERIFICATION.json`: PASS, 174 published files / 30,083,827 B, 174 hash matches, zero failures; the sibling source identity remains NOT ASSERTED in repository-local mode.

Budget against the 225,280-byte runtime JS ceiling:

| Measure | Bytes | Ceiling | Headroom |
|---|---|---|---|
| Sealed `#sim-chains` island | 71,253 | — | — |
| Chain renderer, compacted | 11,743 | — | — |
| Runtime JS code | 225,197 | 225,280 | 83 |
| Artifact | 937,559 | — | — |

The chain contribution is 71,253 B for the sealed data plus 11,743 B for the compacted renderer. The renderer was kept deliberately small (no serialization helper; the drawer reuses `mountChain` and control ids) because the runtime budget has only 83 B of headroom after N16. Adding any runtime chain feature requires cutting bytes elsewhere first.

Record digests:

| Evidence | SHA-256 |
|---|---|
| `evidence/N16_VALIDATION_RECORD.json` | `ddc55b76e6243735aa31472541ccd78a90f4713e1c7088b658cab893d1ea0c00` |
| `evidence/N16_CORPUS_RECORD.json` | `01efc1def1b63529add1ee6e9aa613c464d7e9ddea643feeefacf0a396e350f1` |
| `evidence/N16_PRINT_COLLAPSED.png` | `5c3169e3c1f2799dc9bfbd69f297d943f0d777b0ecd0ba3c86964b70b0fe1425` |
| `evidence/N16_PRINT_REVEALED.png` | `5903a96cb97091adb9eb9d3dcc32bc9244bf016bfba35ad293c8700fcd172fe7` |

## 8. Commands actually run

```
python3 tools/validate_chains.py --report evidence/N16_VALIDATION_RECORD.json
python3 tools/build.py
node tools/check_n16_runtime.js
python3 tools/n16_corpus.py
python3 tools/n16_corpus.py --out /tmp/opencode/n16_second.json
node tools/check_coverage_runtime.js
node tools/check_conventions_runtime.js
node tools/check_golden_vectors_runtime.js
node tools/check_n06_runtime.js
node tools/check_n07_runtime.js
node tools/check_n08_runtime.js
node tools/check_n10_runtime.js
node tools/check_n11_runtime.js
node tools/check_n12_runtime.js
node tools/check_n13_runtime.js
node tools/check_n14_runtime.js
node tools/check_n15_runtime.js
lite-shot --cdp --theme light --media print --full-page -g 800x1100 /tmp/opencode/n16_print_collapsed.html evidence/N16_PRINT_COLLAPSED.png
lite-shot --cdp --theme light --media print --full-page -g 800x1100 /tmp/opencode/n16_print_revealed.html evidence/N16_PRINT_REVEALED.png
python3 tools/verify_preparation.py --repo-local --report evidence/REPO_LOCAL_VERIFICATION.json
```

## 9. Limits and open verification

- The XOR stream seal is inspection resistance, not cryptographic secrecy. The key material is in the artifact; a determined reader can unseal a step. The leak-free claim is about the pre-reveal DOM and island scan, not about resisting reverse engineering.
- N19 and N20 are not implemented. `data/chain_references.json` is a validated forward contract with `declared-pending` status; the item-context fixture is synthetic and does not prove an authored practice item exists.
- The 14 chains are authored training material derived from the masters and conventions. The official programme specifies seven topics, a paper examination and a maximum of 180 minutes; it does not prescribe these chain examples, their values or their point weights.
- Recompute proves internal arithmetic from the declared inputs and conventions. It is not an external scientific measurement, an instructor's marking, or a claim that the master would print the same example.
- Print renders are Falkon print-media emulations at 800×1100 CSS px. Physical-printer, colour-blind, screen-reader and instructor acceptance remain unverified.
- Focus traces run in the harness's synthetic DOM. They prove the declared focus-restore behaviour of the code, not real-browser keyboard, screen-reader or assistive-technology acceptance.
- The 33 authored-N16 drawer slots and the 28 forward references are link integrity, not proof that every outcome has a chain: 33 of 64 outcomes have a chain slot, and the remaining 31 are still served by their summaries and figures. The P5-06 figure slot remains a declared placeholder; its mechanism teaching is the EX10 chain.
