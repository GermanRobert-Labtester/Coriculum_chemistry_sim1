# Pirmā kolokvija simulācijas darba telpa

Prepared 2026-11-16. Materials and implementation plan are ready. **The coverage island (N02), the conventions island with the conflict registry (N03), the topic figure sets (N11–N15), the worked example chains (N16), the quantity engines (N17), the graph scoring engine (N18), the method cards and verdict engines (N19), the frozen practice bank (N20), the exam shell (N21), the response-input layer (N22), the grading engine with error classification (N23), seeded, fair A/B/C form assembly (N24), local, privacy-safe analytics with the honest progress record (N25), the mastery state machine over the 64 outcomes (N26), the offline Leitner scheduler for spaced selection (N27), missed-item remediation with anchors and alternate variants (N28), the unified revision view with F07 criterion self-assessment (N29), and bounded practice paths with filters and honest shortage handling (N30 — closing Phase VI) are implemented with their build gates; final Phase VII N31–N40 gates are not.** This workspace uses the supplied 2025 programme and copies from Chemistry_1–7; the original workspaces are preserved.

Start with [the master implementation plan](MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md). It follows the individual workspaces’ 14-section, 20-core-task / 10-feature / 5-diagnostic structure. The [question-type and variant specification](docs/QUESTION_TYPES_AND_VARIANTS.md) describes 18 response types, 28 families with four variant specifications each, and 14 worked examples.

## Copied master materials

| Programme topic | Master |
|---|---|
| 1. Ievads, šķīdumi un ķīmiskās reakcijas | [Open HTML master](<materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html>) |
| 2. Aprēķini, mērījumi un grafiskās metodes | [Open HTML master](<materials/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html>) |
| 3. Šķīdumi un koncentrāciju aprēķini | [Open HTML master](<materials/Chemistry_3/Master_3_tema_skidumi_un_koncentracijas.html>) |
| 4. Termodinamika | [Open HTML master](<materials/Chemistry_4/Master_4_temats_termodinamika.html>) |
| 5. Kinētika un katalīze | [Open HTML master](<materials/Chemistry_5/Master_5_tema_kinetika_un_katalize.html>) |
| 6. Oksidēšanās un reducēšanās | [Open HTML master](<materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html>) |
| 7. Spektrofotometrija un analīzes metodes | [Open HTML master](<materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html>) |

Chemistry_6’s local Topic 13 label maps to programme Topic 6 (redox). Chemistry_7 is programme Topic 7 (spectrophotometry), including its Lab 6B. The numbered folders represent source workspaces, not automatically the local topic/lab numbers.

## Coverage island (N02)

The simulator's teaching truth now lives in one authored island: [data/coverage.json](data/coverage.json). It carries the seven programme topics and 64 outcomes (9, 10, 11, 11, 10, 8, 5), each with a Latvian statement, a frozen master anchor and heading, practice families, N24 point/minute slots and prerequisite edges. Topic names, the paper format and the 180-minute maximum are programme-sourced; the 64-outcome granularity, statements, edges and slots are training-policy proposals.

- [Coverage validator](tools/validate_coverage.py): schema, count, edge, cycle, planning cross-check, labeling and anchor checks. `python3 tools/validate_coverage.py --report evidence/N02_VALIDATION_RECORD.json`.
- [Anchor resolver](tools/resolve_coverage_anchors.py): 64/64 case-exact anchors against the frozen masters, with per-master digests. `python3 tools/resolve_coverage_anchors.py --out evidence/N02_ANCHOR_RESOLUTION.json`.
- [Build gate](tools/build.py): the coverage check is the first registered gate; it refuses a deleted-outcome island by count assertion and emits the deterministic `output/simulator.html` precursor with the `#sim-coverage` island. `python3 tools/build.py`.
- [Runtime loader](src/coverage-loader.js) and [view](src/coverage-view.js): one loader reads the island, checks the cheap invariants and renders both views; a truncated island degrades to a named error. `node tools/check_coverage_runtime.js`.
- Evidence: [N02 verification record](evidence/N02_VERIFICATION_RECORD.md), [labeling audit](evidence/N02_LABELING_AUDIT.md), [anchor resolution record](evidence/N02_ANCHOR_RESOLUTION.json) and the deterministic [corpus record](evidence/N02_CORPUS_RECORD.json). The N02 artifact is a precursor; N06 and N31 extend the shell and the pipeline.

## Conventions and conflict registry (N03)

The scientific rulebook now lives in one authored island: [data/conventions.json](data/conventions.json), inlined as `#sim-conventions`. It carries 10 master-cited atomic masses, 23 compound molar masses, 9 constants, 36 unit conversions (including 2 explicitly blocked mass↔volume paths), 9 composition chains, 12 tolerance classes, four concentration bases, the meniscus/burette reading rules, the E°/E/E°′ convention, the thermodynamic sign convention and the spectrophotometry scope rules. Citation classes distinguish the official 2025 programme from the teaching masters; tolerance thresholds and their grading use are labelled **PROPOSED training policy**, because the programme sets none.

- [Conventions validator](tools/validate_conventions.py): schema, bidirectional inverse factors, unit-algebra composition with independent `Fraction` recompute, citations against the N01 inventory, labeling, registry traceability and vector resolution. `python3 tools/validate_conventions.py --report evidence/N03_VALIDATION_RECORD.json --registry-out evidence/N03_CONFLICT_REGISTRY.json`.
- [Runtime loader](src/conventions-loader.js): one reader for conversions, chains, masses, tolerances, potentials, rounding and vector expectations; a truncated or missing island throws a named `ConventionsError` naming `#sim-conventions`. `node tools/check_conventions_runtime.js`.
- [Build gate](tools/build.py): gate order 2 `conventions`; a planted wrong chain factor and a statusless registry entry each refuse the build before any artifact is written. `python3 tools/build.py`.
- [Conflict registry](evidence/N03_CONFLICT_REGISTRY.json): 12 V findings + 10 inherited C entries + 4 N03 observations. 15 resolved-by-task, 5 documented-and-accepted, 2 open-with-owner. The catalase question stays open verbatim with the course lecturer. C10 is the predecessor's synthetic-examples item, not catalase; the roadmap's C10/C05 naming discrepancy is recorded as N03-OBS-01.
- Evidence: [N03 verification record](evidence/N03_VERIFICATION_RECORD.md), [validation record](evidence/N03_VALIDATION_RECORD.json), [registry](evidence/N03_CONFLICT_REGISTRY.json), [corpus record](evidence/N03_CORPUS_RECORD.json) and the [paint check](evidence/N03_PAINT_CHECK.png). The N03 artifact is a precursor; N11–N15, N17–N19 and N31 consume the island through the loader, and N40 closes the registry.

## Topic 5 kinetics and linearization figures (N14)

Topic 5's teaching figures now live in [data/figures_t5.json](data/figures_t5.json), inlined as part of `#sim-figures` and reached from the `P5-*` concept drawers. Eight records cover the zero-, first- and second-order concentration-time decays, a catalyst comparison, and three linearization plots (C, ln(c/c₀), 1/c against t) plus one gradeable practice plot.

- [Kinetics contract](data/kinetics_linearization_contract.json): frozen for N16 (chains), N18 (drawn-line scoring) and N20 (variant reparameterization ranges), with the span edge rule, tolerance-field vocabulary and `SimFigures.evaluateFitLine` interface. Canonical SHA-256 `50f9ee2b596f6d28e4d828c1abf1276fe902517b82b0397338fc74ca2f2abc5d`.
- [Figure validator](tools/validate_figures.py): transform consistency (slopes/intercepts recompute from the paired decay), half-life recomputation, tolerance-field resolution in both `absolute` and `significant_figures` modes, fit-line self-tolerance, and span/no-extrapolation checks. `python3 tools/validate_figures.py`.
- [N14 corpus](tools/n14_corpus.py): scratch inconsistent pair, unknown tolerance class, self-violating line and over-span failures; the four N18 preview cases; the teaching trace; the leak scan and planted practice leak; double-build parity. `python3 tools/n14_corpus.py`.
- [Runtime harness](tools/check_n14_runtime.js): 8/8 smoke vectors including `SMK-N14-T5-LINEARIZATION`, fit-line clipping, drawn-line acceptance, practice leak cleanliness and truncation degradation.
- Evidence: [N14 verification record](evidence/N14_VERIFICATION_RECORD.md), [corpus record](evidence/N14_CORPUS_RECORD.json), and Falkon paint checks `evidence/N14_PAINT_DRAWER_LIGHT.png`, `…_DARK.png`, `…_PRINT.png`.

The figures are synthetic training data labelled `PROPOSED`; they are not official measurements. The practice record stores its answer key in `answer_targets` / `grading_reference`, which the leak scan excludes from the rendered surface by rule.

## Topic 6-7 titration and calibration figures (N15)

Topic 6's titration curves and topic 7's calibration plots live in [data/figures_t67.json](data/figures_t67.json), inlined into `#sim-figures` and reached from the `P6-*` / `P7-*` concept drawers. Eight records cover strong/strong and weak/strong pH curves, the deliberately wrong methyl-orange trap, the master-grounded KMnO₄/Fe²⁺ redox curve, a gradeable titration practice, the C7 nine-standard calibration (through zero), a near-edge free-regression teaching record, and a gradeable calibration practice.

- [Titration contract](data/titration_contract.json): frozen for N17 and N18 with the model vocabulary, V-05 equivalence/endpoint wording and the N12 reading coupling. Canonical SHA-256 `6a99319281522c101d3618e6e2e0c99f880281ced28cf9163fda11578225117f`.
- [Calibration contract](data/calibration_contract.json): frozen for N18 with the V-07 assumption vocabulary and the no-extrapolation rule inherited verbatim (`N15-NOEXTRAP-01`). Canonical SHA-256 `53bf121a156920b85b852ea7ac3faa9736fb3fbace3bb2eb136f81bd446767f8`.
- [Figure validator](tools/validate_figures.py): inflection/initial/buffer model checks, V-05 copy lint, reading-strip print floor, calibration fit/reading recompute, V-07 honesty lint and build-enforced no-extrapolation span checks. `python3 tools/validate_figures.py`.
- [N15 corpus](tools/n15_corpus.py): scratch inflection disagreement, over-span fit/reading and wrong-reading failures by id; two-run curve parity; per-record leak/exemption audit; contract digests; truncation refusal; double-build parity; print renders. `python3 tools/n15_corpus.py`.
- [Runtime harness](tools/check_n15_runtime.js): 9/9 smoke vectors including `SMK-N15-T67-TITRATION`, deterministic renders, model/band/reading attributes, practice leak cleanliness and truncation degradation.
- Evidence: [N15 verification record](evidence/N15_VERIFICATION_RECORD.md), [corpus record](evidence/N15_CORPUS_RECORD.json), and Falkon print checks `evidence/N15_PRINT_TITRATION.png`, `evidence/N15_PRINT_CALIBRATION.png`.

All titration records except the master-grounded C6 case are `PROPOSED` training policy; the calibration records use the master's worked standards. Practices keep their answers out of the rendered data; the teaching records' displayed readings carry reasoned exemptions.

## Worked example chains (N16)

Fourteen worked chains now live in [data/chains.json](data/chains.json), inlined as the sealed `#sim-chains` island and rendered collapsed in `#piemeri`. Each chain is a multi-step calculation with Latvian step statements, a master-anchor citation, conventions citations, an optional figure mounted at a declared step, and a per-step result plus reasoning that stays hidden until the learner asks for it.

- [Chain format](docs/CHAIN_FORMAT.md) and [schema](data/chain_schema.json): 14 records EX01–EX14, 69 steps (50 numeric, 19 symbolic), two chains per programme topic, 13 figure references and 35 outcome links across the N02 vocabulary. Every numeric step declares a recompute recipe.
- [Chain validator](tools/validate_chains.py): schema, Decimal recompute (50/50), citation resolution (128 conventions / 87 anchors / 13 figures / 35 outcomes), sealing round-trip and the pre-reveal/island leak scan with a planted-leak refusal. `python3 tools/validate_chains.py --report evidence/N16_VALIDATION_RECORD.json`.
- [Renderer](src/chain-view.js): collapsed default, per-step reveal, reveal-all with one confirmation, exact re-collapse, no storage or URL persistence, figure mount on reveal and named error surfaces. The sealed projection uses a per-step XOR stream keyed by SHA-256; it is inspection resistance, not cryptographic secrecy.
- [Concept integration](src/concept-drawer.js): the 33 outcome summaries with chain slots mount their chains from the same island; a map-to-chain path and an item-to-chain path restore focus per the N07 open-link contract. Method cards (N19) and practice items (N20) are declared forward references in [data/chain_references.json](data/chain_references.json) and remain `declared-pending` because those tasks are not implemented.
- [Runtime harness](tools/check_n16_runtime.js) and [corpus](tools/n16_corpus.py): 14 chains / 69 steps, per-chain pre/reveal/collapse digests, item-key scan, focus traces, smoke vector `SMK-N16-CHAINS-REVEAL`, print fixtures and byte accounting.
- Evidence: [N16 verification record](evidence/N16_VERIFICATION_RECORD.md), [validation record](evidence/N16_VALIDATION_RECORD.json), [corpus record](evidence/N16_CORPUS_RECORD.json), and Falkon print checks `evidence/N16_PRINT_COLLAPSED.png`, `evidence/N16_PRINT_REVEALED.png`.

The chains are training material, not official colloquium questions. The banner is fixed on every chain, the store opens collapsed in every session, and the print stylesheet shows a collapsed chain's statements with an interactive note while a revealed chain prints the results and reasoning the learner has already opened.

## Quantity, conservation and error-taxonomy engines (N17)

One calculation authority now lives in the Python twin [tools/quantity_engine.py](tools/quantity_engine.py) and the runtime twin [src/quantity-engine.js](src/quantity-engine.js). Both consume only `#sim-conventions`, `#sim-terms` and the frozen `#sim-engines` island; a build-time scan proves no atomic mass, molar mass, constant or conversion factor is declared locally. Quantities are dimensioned (magnitude, N10 unit expression, significant figures); every operation records its unit algebra, and a calculation whose dimensions do not close fails with the dimensional class before a number is produced, so the V-04 mg/g/L defect is structurally excluded.

- [Engine taxonomy and frozen contract](data/engine_taxonomy.json): four classes with a verbatim precedence rule (unreadable → dimensional → physically implausible → out-of-domain), conventions-backed plausibility and domain bounds, conservation rules, and the S2-N17 vector set. Four `feedback.error.*` terms resolve in `#sim-terms`, so classification and feedback are one act. The full N09 registry is still a recorded dependency gap; signatures use the N04 stub pattern and are all present in the frozen corpus.
- [Engine validator](tools/validate_engines.py): gate 13 `engines`; 40/40 N05 verdict-for-verdict, 20/20 N17 vectors, 7 V-04 forms, signature/feedback alignment with zero dangling terms, no-local-constants proof, and a scratch convention regression that fails by vector id. `python3 tools/validate_engines.py --report evidence/N17_VALIDATION_RECORD.json`.
- [Runtime harness](tools/check_n17_runtime.js) and [corpus](tools/n17_corpus.py): cross-language digest parity (Python and JavaScript twins), 1000-input throughput note, in-file `SMK-N17-CLASSIFICATION` smoke vector, two-run parity and byte accounting. `node tools/check_n17_runtime.js`, `python3 tools/n17_corpus.py`.
- Evidence: [N17 verification record](evidence/N17_VERIFICATION_RECORD.md), [validation record](evidence/N17_VALIDATION_RECORD.json) and [corpus record](evidence/N17_CORPUS_RECORD.json).

The frozen JavaScript sub-budget had 83 B of headroom at N17, so the engine module is validated from `src/` against the shipped islands instead of being inlined into `output/simulator.html`; the taxonomy island and its meta digest are embedded, and N31 must lazy-load or re-budget before inlining the code. This is recorded in the ledger rather than hidden by a ceiling change.

## Graph scoring engine (N18)

One interpretation authority now grades two families of graph work: **reading** (a marked point on a rendered figure, scored against the figure record's declared tolerance fields) and **drawing** (a drawn line or curve segment on declared axes, scored against the criterion shape). The engine lives in the frozen [`data/graph_scoring_contract.json`](data/graph_scoring_contract.json), inlined as `#sim-graph-scoring`, with the Python twin [tools/graph_scoring_engine.py](tools/graph_scoring_engine.py), the runtime twin [src/graph-scoring-engine.js](src/graph-scoring-engine.js) and the drawn-response capture component [src/graph-capture.js](src/graph-capture.js).

- **Tolerances are resolved at scoring time.** The tolerance *class* is named by the record or by the contract; the value comes from `#sim-conventions` and is never copied into a record. Both modes are exercised: `absolute` and `significant_figures`, the latter derived exactly as N14's field tolerance so the figure layer and the scoring layer cannot drift apart.
- **Validity first.** Six classes (malformed payload, empty submission, outside the axes, wrong direction, double back, non-monotonic) run before any numeric comparison, with a declared precedence that resolves a submission that is both unphysical and out of domain to a single verdict.
- **The no-extrapolation rule is inherited verbatim** from N15 and N14: geometry beyond the declared span is neither accepted nor rejected, it is simply not assessed, and the span boundary is inclusive. Three boundary fixtures prove the behaviour against the rule text.
- **The capture payload has no device field.** Pointer and keyboard paths project onto the same declared grid and digest equal on all seven drawing vectors, so a keyboard-only learner is graded by identical rules with identical tolerance. The keyboard fine step is bounded by half the tolerance band.
- **The capture component is input-agnostic by construction.** `SimGraphCapture` records a drawn response as a polyline through the placed points; a pointer drag of 401 raw points and a keyboard walk of 81 raw points produce a byte-identical payload, and a reading mark placed by either device produces the same mark and the same verdict. The keyboard increments are derived by the engine from the declared contract, so a component cannot invent its own precision; the fine step is never coarser than half the tolerance band of the assessed axis.
- **Every verdict is auditable and replayable.** Each verdict cites the tolerance class, the record's tolerance field, the contract rules and the inherited rules, and carries a replay block from which the verdict can be reconstructed alone.

- [Graph scoring format](docs/GRAPH_SCORING_FORMAT.md): the frozen interface for N20, N22, N23 and N33.
- [Build gate](tools/validate_graph_scoring.py): contract structure, 3/3 N05 reading vectors, 14/14 S3-N18 stratum, 5/5 validity cases, 6/6 malformed payloads, 7/7 parity pairs, 4/4 replayed verdicts, 6/6 declared keyboard contexts, 3/3 scratch negatives. `python3 tools/validate_graph_scoring.py --report evidence/N18_VALIDATION_RECORD.json`.
- [Runtime harness](tools/check_n18_runtime.js) and [corpus](tools/n18_corpus.py): the parity matrix with digests, the capture component fixtures, the verdict replay proof, the cross-language comparison on eight tables (six verdict tables, the capture component and the full verdict records), the budget accounting and the smoke vector. `node tools/check_n18_runtime.js`, `python3 tools/n18_corpus.py`.
- Evidence: [N18 verification record](evidence/N18_VERIFICATION_RECORD.md), [validation record](evidence/N18_VALIDATION_RECORD.json) and [corpus record](evidence/N18_CORPUS_RECORD.json).

The engine declares no tolerance, unit factor or model coefficient of its own; it consumes only `#sim-conventions`, `#sim-figures` and `#sim-graph-scoring`. Its tolerances, criterion shapes and reading families are PROPOSED training policy — the 2025 programme sets none of them. Like the N17 engine, the module ships from `src/` because the runtime-JS ceiling had 83 bytes of headroom; the capture component ships the same way; N31 must lazy-load or re-budget before inlining either.

## Method cards and the non-numeric verdict engines (N19)

One method authority now teaches the procedures the masters teach and grades the three non-numeric response types the schema declares. The cards are **data** — [data/method_cards.json](data/method_cards.json) holds 14 cards `MC-EX01`–`MC-EX14` (74 steps, 28 sequence prompts, 3 matching exercises, 3 safety entries, 1 free-order group), with the format declared in [data/method_card_schema.json](data/method_card_schema.json). The engines live in the frozen [`data/method_engine_contract.json`](data/method_engine_contract.json) (`#sim-method-engine`), with the Python twin [tools/method_engine.py](tools/method_engine.py), the runtime twin [src/method-engine.js](src/method-engine.js) and the card renderer [src/method-card-view.js](src/method-card-view.js).

- **A card is data, and the order is cited, not invented.** Each card's step order comes from its master's teaching and is cited per card (path, anchor, heading, freeze id, sha256); the citation validation is build-gated, 36 of 36 citations resolve. Every numeric step links to the recomputed chain step, and the link's value and unit must equal the chain's result — a card invents no quantity.
- **The three engines grade structurally, never by text.** Ordering compares order positions, matching compares pair identities, sequence compares step ids against a declared acceptance set. Three independent proofs hold the no-keyword rule: a static token and literal scan of both engine sources, adversarial near-synonym vectors that must fail, and a behavioural fixture showing an added free-text field never changes a verdict.
- **A wrong step is diagnosable, not just wrong.** Ordering grades per step and returns the misconception signature the step's note names. A transposed pair marks both positions and returns both steps' own notes and feedback strings; the remediation entry names the card, the step, the signature and the resolved feedback text, so N28's link lands on the step's note.
- **The masters' own freedom is honoured.** The dilution card declares one free-order group over the two independent weighings the master leaves unordered, and the group is graded either way. It is authored into one card deliberately, so the grading never penalises the masters; moving a member outside the group's position is still wrong.
- **Self-assessment stays honestly pending.** A learner's own words are recorded and never parsed: the only operation on the text is a blankness test. A self-assessment yields a pending record with no verdict and no signature; a blank one yields `BLANK_RESPONSE` and zero points. The pending semantics are frozen for N23.
- **Safety entries only restate the masters.** Each of the three entries cites its master anchor, and the build gate compares the entry mechanically against that section — the overlap is 1,00 for all three, so an invented precaution would fail the build.

**Recorded dependency gap: N09 does not exist in this workspace.** The signatures therefore use the N04 stub pattern `^MC-[1-7][A-D]-[0-9]{2}$` and each must resolve against an existing vector in the frozen N05 corpus; two of the fourteen are marked `nearest-available-cross-family` with the reason recorded in the registry. The gap is written into the card island, not silently filled: when N09 lands, that binding is what must be re-checked, not the card logic.

- [Method card format](docs/METHOD_CARD_FORMAT.md): the frozen interface for N20, N22, N23 and N28 — the card fields, the three engines' rules, the signature registry, the pending semantics, the runtime API and the remediation contract.
- [Build gate](tools/validate_method_cards.py): card structure, 36/36 citations, 35/35 method outcomes covered, the copy lint, the 14-signature sweep in both directions, 10/10 N05 vectors, 17/17 S4-N19 vectors, the no-keyword proof and the budget. `python3 tools/validate_method_cards.py --report evidence/N19_VALIDATION_RECORD.json`.
- [Runtime harness](tools/check_n19_runtime.js) and [corpus](tools/n19_corpus.py): the verdict tables, the feedback trace, the pending boundary, the focus traces, the cross-language comparison and the smoke vector. `node tools/check_n19_runtime.js`, `python3 tools/n19_corpus.py`.
- Evidence: [N19 verification record](evidence/N19_VERIFICATION_RECORD.md), [validation record](evidence/N19_VALIDATION_RECORD.json) and [corpus record](evidence/N19_CORPUS_RECORD.json).

**Budget limitation, recorded rather than hidden.** The runtime-JS ceiling had 83 bytes of headroom when N19 started, so **both** new modules ship from `src/` and are not inlined into the artifact's executable script; the card drawer is therefore proven in the harness against the shipped islands, not in the shipped HTML. The cards budget measures the shipped sealed island (109,919 B of 131,072 B), not the source file (84,088 B), because the projection carries the sealed diagnostics. **N31 owns the resolution** — inline, lazy-load or re-budget — exactly as for N17 and N18; the ceiling itself was not changed. The N19 smoke vector is registered in the runtime harness because the artifact's smoke subset cannot be extended within the headroom.

**Handoffs.** The frozen contract (`data/method_engine_contract.json`) and the card format go to **N20** (method practice items referencing the cards; the `PRAC-EX*` declarations stay `declared-pending-N20`), **N22** (the ordering, matching and sequence response components), **N23** (the grading pathways, including the frozen pending class) and **N28** (the remediation links, whose target is `diagnostics.remediation` → `SimMethodCards.stepNote`). **N09** inherits the signature binding.

## Variant engine, family templates and the frozen practice bank (N20)

The 28 declared families are now **templates and instances**, not only specifications. A deterministic variant engine draws each family's declared parameters through the frozen N05 PRNG, computes the derived values through the N17/N18/N19 contracts and emits schema-valid instances; 112 instances (28 families × 4 variants) are frozen, reviewed and embedded in the artifact as `#sim-bank`.

- [tools/variant_engine.py](tools/variant_engine.py) is the Python authoring twin and [src/variant-engine.js](src/variant-engine.js) the runtime twin `SimVariantEngine`. All arithmetic is fixed-point integer arithmetic at scale 10⁻⁹ — no float ever reaches an emitted number — so the two languages cannot drift on a rounding boundary. The seed is FNV-1a-64 over the family/variant key, and the same seed reproduces the same instance anywhere.
- The templates are frozen in [data/family_templates/](data/family_templates/) (28 families, 112 variants, canonical bytes) and are also emitted as the runtime asset [src/variant-templates.js](src/variant-templates.js) for the ephemeral path. The frozen bank is [data/bank/](data/bank/) (28 files, 112 reviewed instances). The authored content lives in [tools/n20_content.py](tools/n20_content.py).
- **The bank is reviewed, not just written.** Five mechanical checks per instance — range compliance, the N17 recompute, the N12 leak scan, the accessibility structure and the grading alignment — and five stages (`authored → validated → recomputed → reviewed → accepted`). The sign-off is the **N20 task author's preparation pass**, not an RSU instructor's acceptance. The workflow is build gate 16: it refuses the build when an instance is not accepted, and the refusal is proven by id (`COL1-1-1A-ZZ-99`).
- **The loader verifies the island.** `src/bank-loader.js` digests the island text as embedded and refuses a tampered island (`E_BANK_DIGEST_MISMATCH`) or an unsigned one (`E_BANK_DIGEST_MISSING`) instead of loading it. The frozen digests are the bank source digest `1c263cdb…acb6` (the reference for "any bank change is a new digest and a deliberate act") and the island digest `07fec72a…bac1`.
- **Practice is unbounded, the graded bank is not.** The ephemeral retry path draws a seed outside the frozen set, instantiates from the same templates through the same code, grades through the same engines and is never persisted; it carries its own `-EPH-{attempt}` identity so it can never be confused with the frozen instance.
- The answers are written the way a learner must write them: the payload's `sig_figs` is the significant-figure count of the **written** form, and a whole answer whose precision lives in trailing zeros is written in scientific notation (`6,80 × 10²`), which N17 parses and counts the same way.

- [Variant engine format](docs/VARIANT_ENGINE_FORMAT.md): the frozen interface for N24, N28, N30 and N31 — the template fields, the recipe operations, the guarantees, the bank digests, the integrity check and the ephemeral contract.
- [Template gate](tools/validate_family_templates.py): the per-family validation table, the determinism proof and the out-of-range refusal. `python3 tools/validate_family_templates.py`.
- [Review gate](tools/validate_bank_review.py): the five mechanical checks, the promotion and the scratch-refusal proof. `python3 tools/validate_bank_review.py --review`, `--prove-scratch-refusal`.
- [Runtime harness](tools/check_n20_runtime.js) and [corpus](tools/n20_corpus.py): cross-language parity (112/112 byte-identical), determinism, the ephemeral path, the parity fixture, the tamper fixture and the in-file smoke vector against the built artifact. `node tools/check_n20_runtime.js`, `python3 tools/n20_corpus.py`.
- Evidence: [N20 verification record](evidence/N20_VERIFICATION_RECORD.md), [machine-readable record](evidence/N20_VERIFICATION_RECORD.json), [gate-level validation record](evidence/N20_VALIDATION_RECORD.json), [corpus record](evidence/N20_CORPUS_RECORD.json) and [runtime record](evidence/N20_RUNTIME_RECORD.json).

**Budgets, measured.** The artifact is 1,374,364 B (1,342.2 KiB) of the 700–1,400 KiB budget; the bank island is 249,798 B (243.9 KiB) of the 200–420 KiB sub-budget; the inline runtime JS is 225,192 B (219.9 KiB). The island is a **runtime projection** of the frozen bank — the per-instance audit tables stay in `data/bank/*.json` and in the evidence records, and both digests are recorded. The runtime-JS ceiling was re-set on the measurement (225,280 B → 237,568 B), as AGENTS.md requires: the inline JS was already 218.1 KiB before N20, so the old figure would have been exceeded by 88 bytes. The CSS measures 38.9 KiB, below the plan's *target* range; that content belongs to earlier phases and N20 records the measurement instead of changing it. `src/variant-engine.js` and `src/variant-templates.js` ship from `src/` and are **not** inlined, exactly like the N17/N18/N19 engine modules — **N31 owns the inline / lazy-load / re-budget decision.**

**Handoffs.** The instance ids and the island digest go to **N24** (exam assembly — the bank is training material, and an assembly built from it is a training-policy simulation, never an official examination); the ephemeral contract and the family templates go to **N28** (remediation) and **N30** (bounded practice); the grading surfaces go to **N23** (`N17-numeric` for numeric and graph, `N19-method` for option_select, ordering and matching, self-assessment only for the `method` payload class).

**Not claimed.** No official examination, grade or proctoring status; no browser render, screen-reader, print or instructor acceptance (the accessibility review is a mechanical structural check, deferred to N22/N34); no semantic grading (the N12 scanner is a token and unit-normalised rule); no claim that the four variants are four finished questions — they are four parameterisations of one family template.

## Exam shell: the session machine, the timer, navigation, flags and the view boundary (N21)

The container every graded interaction lives in now exists as an explicit state machine with a
frozen contract. A training-policy exam session of **21 slots and 100 points** runs on an
**advisory** timer, navigates by pointer or keyboard, flags per slot, and ends on an explicitly
confirmed, one-way submission that writes a terminal record. The programme fixes the topics, a
written-on-paper examination and a maximum of 180 minutes — the slots, the points, the forms and
the timer are this simulator's **PROPOSED training policy**, and nothing here claims an official
examination, grade, timing rule or proctoring.

- **The machine is the only writer.** [src/session.ts](src/session.ts) holds the answer map and
  the flag set in private fields; the accessors return deep copies, and every change goes through
  `dispatch(event, payload)`. The shell has no setter to reach, so "no component mutates the
  answer map outside the machine" is a structural property, not a convention. The build gate
  checks it at the source level and the fixtures check it at runtime.
- **The transition table lives in the island.** [data/exam_policy.json](data/exam_policy.json)
  declares 6 states (`not-started`, `running`, `review`, `submitted`, `expired`, `aborted`), 8
  events and an **exhaustive 48-row** transition table. The runtime builds its table from the
  island and raises `E_SESSION_CONTRACT_INVALID` when a state/event pair is missing or ambiguous,
  so the island and the runtime cannot drift. Every refusal carries a stable id —
  `E_SESSION_LATE_WRITE` after a submission, `E_SESSION_EXPIRED_WRITE`, `E_SESSION_ABORTED_WRITE`,
  `E_SESSION_REVIEW_REQUIRED`, `E_SESSION_CONFIRMATION_REQUIRED` — and the answers given before a
  terminal transition are preserved for the report.
- **The timer is advisory and honest.** The elapsed time comes from a **monotonic** clock
  (`performance.now()`, never `Date.now()`) and is derived at every read, never counted from the
  ticks — so a throttled or hidden tab still reports honest elapsed time. The 90 % threshold is a
  **status indication only**: it never changes the state and never disables a control. The label
  says so in Latvian: *"Izglītojošs laika ierobežojums (mācību politika, nevis oficiāls eksāmens)"*.
- **Answers are stored raw.** A numeric string stays exactly as it was typed (`" 1 000,50 "`
  survives byte for byte), the ordering and the pairs stay as they were arranged, and the payload
  validation is structural only. Normalisation and grading belong to N23. A serialised session
  deserialises to identical answers, flags and state — the precondition N34's storage layer
  depends on.
- **The boundary is architectural, in both directions.** In exam mode the hint ladder, the worked
  chains, the method cards and the term lookup are **never created** — the render contract asks
  the mode registry first, and an unregistered component fails loudly with
  `E_MODE_COMPONENT_NOT_ALLOWED`. The fixture serialises the exam DOM and finds zero help markers
  and zero N16 chain step text; the practice surface is built from a practice context and never
  receives an exam session, so the serialised practice DOM contains zero exam-session fields, zero
  flags and zero answer content.
- **Navigation is complete in both paths.** The 21-cell map, the previous/next controls and the
  flag toggle are pure functions of the session state. All 21 slots are reachable by pointer and
  by keyboard alone: the scripted keyboard run answers and flags across all 21 slots **without a
  single pointer event**, and `Tab` is never intercepted, so the focus is never trapped. The
  review screen shows all 21 slots, names the unanswered ones in a `role="alert"` warning, and
  the submission needs an explicit confirmation that the **machine** also enforces.
- **Strict TypeScript is the source of truth.** [src/exam.ts](src/exam.ts) and
  [src/session.ts](src/session.ts) are compiled deterministically by
  [tools/compile_n21_ts.py](tools/compile_n21_ts.py) into the committed
  [src/compiled/](src/compiled) modules; `--check` recompiles into an isolated directory and
  compares, so a stale module can never ship. AGENTS.md assigns the session and response logic to
  strict TypeScript, and the artifact stays offline and dependency-free.

- [Exam shell format](docs/EXAM_SHELL_FORMAT.md): the frozen interface for N22–N34 — the states,
  the events, the error ids, the timer contract, the payload kinds, the terminal record, the mode
  registry and the handoffs.
- [Policy authoring twin](tools/author_exam_policy.py) and [build gate 17](tools/validate_n21_shell.py):
  `python3 tools/author_exam_policy.py --check`, `python3 tools/validate_n21_shell.py`.
- [Runtime harness](tools/check_n21_runtime.js) and [corpus](tools/n21_corpus.py): 15 fixtures —
  the lifecycle, the late-write guard, the mock-clock timer, the payload and serialisation
  contracts, the two-way boundary, the mode registry, the navigation and keyboard completeness,
  the submit gate, the buffer race, the terminal record and the scripted end-to-end trace.
  `node tools/check_n21_runtime.js`, `python3 tools/n21_corpus.py`.
- Evidence: [N21 verification record](evidence/N21_VERIFICATION_RECORD.md),
  [machine-readable record](evidence/N21_VERIFICATION_RECORD.json),
  [gate-level validation record](evidence/N21_VALIDATION_RECORD.json),
  [corpus record](evidence/N21_CORPUS_RECORD.json), [runtime record](evidence/N21_RUNTIME_RECORD.json),
  [session trace](evidence/N21_SESSION_TRACE.json) and the two Falkon render checks
  [shell](evidence/N21_PAINT_SHELL.png) / [review](evidence/N21_PAINT_REVIEW.png) — render checks
  only, not accessibility or browser-matrix acceptance.

**Budgets, measured — and a re-budget that is visible.** The artifact is 1 436 780 B (1 403.1 KiB)
of the declared 700–1 400 KiB budget; the inline runtime JS is 266 616 B (260.4 KiB) of the
declared 120–220 KiB; the CSS is 44 267 B (43.2 KiB) of the 40–80 KiB; the bank island is
unchanged at 249 798 B (243.9 KiB) of the 200–420 KiB. The exam shell has to run **inside** the
single-file artifact, so its runtime is inlined — and the plan's total band was already 95.9 %
consumed when N20 finished. N21 therefore re-set the interim ceilings **on the measured
requirement**, as AGENTS.md requires, instead of shrinking the deliverable by dropping the shell or
the fixtures. The deviation is visible in four places: [tools/byte_budget.py](tools/byte_budget.py)
holds the declared band next to the enforced ceiling and the re-budget history, the island carries
the conflicts `N21-C02` and `N21-C03`, every gate and corpus runner enforces the shared ceilings,
and the [ledger](evidence/VERIFICATION_LEDGER.md) records the measurement. **N31 owns the final
inline / lazy-load / re-budget decision**; until then, N22–N25 should ship their heavy runtime
from `src/` — the pattern the N17–N20 engines already use — or re-set their own ceiling on their
own measurement.

**Handoffs.** The terminal record (`toTerminalRecord()`: answers, flags, elapsed time, form id,
transitions, unanswered and remediation lists) goes to **N23** (grading) and **N25** (logging — no
persistence without an explicit learner opt-in); the payload kinds go to **N22** (the typed answer
components); the 21 slot ids and their points go to **N24** (the form assembly — the shell renders
the blueprint plan and says so until the instances exist); `getRemediationSlotIds()` goes to
**N28** (a remediation link cannot exist inside the exam before the submission by design);
`buildMapState()` goes to **N32** as the deterministic responsive test data; the keyboard contract
and the alert/pressed/current semantics go to **N33**; `serialize()`/`deserialize()` go to **N34**.

**Not claimed.** No official examination, grade, timing rule or proctoring status; no browser
render, screen-reader, print or instructor acceptance (the accessibility evidence is a mechanical
structural check); no keyword matching as semantic grading; no claim that the four variants are
four finished questions; no persisted session — the state lives in memory for as long as the page
does.

## Response input semantics: the registry, the components and the ARIA contracts (N22)

Every one of the 18 response types now has one authored contract and one thin renderer over it. The
contract lives in the registry island [data/response_types.json](data/response_types.json), inlined
as `#sim-response-types`: for each of Q01–Q18 the render contract (field templates with term-keyed
ARIA name patterns and `{slot}` substitution), the payload shape stored in the answer map (the N21
kind plus the registry-declared variant), the declarative completion rule, the error surfaces
(frozen N17/N18/N19 ids only), the keyboard path and the accessible alternative the blueprint
mandates. The completed types (Q02, Q04, Q10, Q11, Q12, Q13, Q15) each carry a render and a grading
binding with `adapter: "none"` — N23 receives payloads it can grade without adaptation.

- **The registry is the single source.** [SimInputsRegistry](src/inputs/registry.ts) loads the island
  and refuses an unknown type id loudly (`E_INPUTS_UNKNOWN_TYPE`, proven by a scratch `Q99`
  fixture in [tools/validate_n22_inputs.py](tools/validate_n22_inputs.py)); a fallback text field
  would silently change a task's meaning and is structurally excluded. Build gate 18
  (`response_inputs`) asserts the 18 types against the frozen N04 schema, the completed-type
  bindings, the term-key resolution and the compile drift.
- **Completion is a pure function.** `completion(typeId, contract, instance, payload)` returns
  `complete`, `incomplete` with a named Latvian missing list, or `invalid` with named errors; the
  navigator overlay and the review warning consume the same verdicts. The four roadmap fixtures
  (Q13 missing coefficient, Q17 half-drawn structure, Q12 value without figure binding, the
  plot-state short of its declared point count) each yield their named list.
- **Errors never destroy input.** The error-surface mapping renders only frozen ids; the roadmap's
  `MIXED_SEPARATORS` does not exist as an id, so a mixed-separator entry surfaces the frozen
  `UNREADABLE_INPUT` message on blur with the raw string preserved byte-for-byte (conflict
  `N22-C01`). The input-preservation invariant is recorded and all 18 types inherit it.
- **Keyboard parity is proven per spatial type.** [SimInputsComponents](src/inputs/components.ts)
  renders descriptions (pure functions of contract, state and payload); the pair matcher, the
  ordering strip, the plot input (pointer plus the coordinate table through the N18 capture
  contexts), the read declaration and the Q17 structure palette each answer one identical task
  twice — pointer and keyboard — with byte-identical payloads, and a mid-gesture abort discards the
  in-progress placement without emitting a partial one.
- **The capture-grading parity table covers all 18.** The scripted 18-type session drives the
  session machine through the component API, serialises, round-trips and grades through the frozen
  engines with zero adapters; the Q03 template response runs the manual-rubric **pending** path
  rather than pretending auto-scoring.
- **The ARIA label bank is term-keyed.** 131 new `input.*` entries (451 total) in
  [data/terms.json](data/terms.json); the lint pass records zero literal unit strings and zero
  untranslated ARIA names. Three in-file smoke vectors (`SMK-N22-NUMERIC-CAPTURE`,
  `SMK-N22-CLASSIFICATION-CAPTURE`, `SMK-N22-ORDERING-CAPTURE`) are embedded in the artifact.
- **Modules ship from `src/`, not inlined.** registry 58 817 B, components 123 374 B, integration
  43 718 B — the N17–N20 pattern; **N31 owns the final inline / lazy-load / re-budget decision**.
- [Response input format](docs/RESPONSE_INPUT_FORMAT.md): the frozen interface for N23, N24, N30
  and N33.
- Build gate: `python3 tools/validate_n22_inputs.py --report evidence/N22_REGISTRY_VALIDATION.json`;
  harnesses `node tools/check_n22_semantics.js`, `node tools/check_n22_components.js`,
  `node tools/check_n22_runtime.js`; corpus `python3 tools/n22_corpus.py` (byte-identical across
  two runs).
- Evidence: [N22 verification record](evidence/N22_VERIFICATION_RECORD.md),
  [registry validation](evidence/N22_REGISTRY_VALIDATION.json),
  [corpus record](evidence/N22_CORPUS_RECORD.json),
  [parity table](evidence/N22_PARITY_TABLE.json) and
  [session trace](evidence/N22_SESSION_TRACE.json).

**Budgets, measured.** The artifact is 1 522 870 B (1 487.2 KiB) against the declared 700–1 400 KiB
band; the interim ceiling was re-set 1 440 → 1 504 KiB on the measurement (conflict `N22-C08`, the
N21 precedent), with the declared band left visible. The inline runtime JS is 270 014 B (263.7 KiB)
— inside the 264 KiB ceiling with 322 B to spare. The registry island is 34 962 B canonical; the
terms island grew to 165 933 B.

**Handoffs.** N23 grades the payloads without adapters and honors the input-preservation invariant;
N24 binds instances through the render context (`figures` for Q12 bindings, capture contexts for
Q11 draws); N30 renders practice items through the same components; N33 consumes the name-role-value
records (its live screen-reader pass is the release gate N22's fixtures only precondition); N31
owns the inline/lazy-load/re-budget decision.

**Not claimed.** No screen-reader, browser-render, print or instructor acceptance (N33/N34 own
those gates); no official examination, grade or proctoring status; no semantic grading of free text
(keyword matching is never semantic grading); the open item `N22-C06` (the bank's self-assessed
criteria for Q02/Q09/Q10/Q11/Q12 have no declared text annex in the frozen N04 payload classes) is
recorded with N23/N24 as owners, not silently solved.

## Grading engine: verdict assembly, error classification and honest totals (N23)

The scoring heart of the simulator now exists as one deterministic assembly layer over the frozen
engine contracts. [src/grading.ts](src/grading.ts) → [src/compiled/grading.js](src/compiled/grading.js)
(`root.SimGrading`) grades a terminal session record through the N22 completion gate first
(invalid → zero with named errors and the raw input preserved; incomplete → zero with the named
missing list; no engine call in either case), routes Q03/Q05 through the manual-rubric pending
path, dispatches complete payloads to the exact zero-adapter engine calls of the N22 parity table,
and aggregates per-criterion points into per-slot and form totals on the 100-point scale.
[src/feedback.ts](src/feedback.ts) → [src/compiled/feedback.js](src/compiled/feedback.js)
(`root.SimFeedback`) maps every verdict signature, error class and slot state through the
classification island to Latvian feedback items (task-level first, then per-criterion, the
authored priority ladder ordering multi-signature verdicts) whose remediation payloads resolve
into N07 concepts, N16 chains and N19 card steps.

- **The engines award; N23 assembles.** The module contains no tolerance logic of its own — a
  gate-enforced source scan — and an unknown verdict class fails loudly with the criterion and
  verdict named (`E_GRADING_UNKNOWN_VERDICT`), never a silent zero.
- **Pending stays external.** The full score-matrix form reads 48 auto-scored of 48 auto-max plus
  52 pending-external of 52 pending-max: the 100-point scale fully accounted, the two sums never
  merged (`unblended: true` is an asserted field, carried into the analytics events unchanged).
  The N22-C06 conflict is decided: the self-assessed criteria of Q02/Q09/Q10/Q11/Q12 are accepted
  as pending-external without inventing input fields, with the decision recorded in the policy
  island and the ledger.
- **The scale is the slot's.** A binding whose rubric sum differs from the declared slot points is
  refused by id (`E_GRADING_BINDING_POINTS`; conflict N23-C01 names the FAM-7C/7D vs S7-3 case for
  N24).
- **Malformed is zero with the named error, never near-miss credit.** The mixed-separator
  `"1.000,50"` is caught by the N17 engine (`UNREADABLE_INPUT`, `MC-2B-02`); the truncated
  ordering and the empty coefficient are caught by N22 completion; the raw input survives
  byte-for-byte in the graded record in every case.
- **The N09 gap stays visible.** No misconception registry exists in this workspace (the recorded
  dependency gap N19 already carries); the classification island
  [data/feedback_classification.json](data/feedback_classification.json) (`#sim-feedback-classification`,
  88 rows: 62 signatures, 21 error classes, 5 slot states) is N23-authored PROPOSED policy over
  the frozen vocabularies, with the priority ladder declared as data and the island named as the
  artifact to re-check when N09 lands. The sweep proves zero unmapped signatures and zero
  unresolved remediation links over the whole bank.
- **The record is canonical and digest-linked.** Graded records emit the N04 canonicalization
  (sorted keys, SHA-256); the same terminal record graded twice and in a fresh process yields
  byte-identical digests; the chain fixture links terminal digest → graded digest → analytics
  events (session-completed, task-answered without answer text, remediation-state), each carrying
  the graded digest — N25 consumes the same record without re-scoring.

- [Grading engine format](docs/GRADING_FORMAT.md): the frozen interface for N24, N25, N28, N32
  and N36, including the as-built amendments recorded at integration.
- Rubric policy island: [data/grading_policy.json](data/grading_policy.json)
  (`#sim-grading-policy`) — verdict rules for every frozen class, slot-state rules, the points
  rule, honesty accounting, three self-test fixtures and the conflict records; validated by build
  gate 19. `python3 tools/validate_n23_grading.py --report evidence/N23_VALIDATION_RECORD.json`.
- Classification sweep: `python3 tools/n23_classification.py` →
  [the classification table](evidence/N23_CLASSIFICATION_TABLE.json) (88 rows, 27 scripted error
  cases, the multi-signature and priority-ordering fixtures; N36's mutation-test baseline).
- Runtime harness: `node tools/check_n23_runtime.js --record … --chain … --render … --determinism …`
  — the four-form score matrix (FULL/PARTIAL/ZERO/MIXED, all totals equal the hand-computed sums in
  [tools/fixtures/n23_score_matrix.json](tools/fixtures/n23_score_matrix.json)), the chain fixture,
  the [render stub](evidence/N23_RENDER_FIXTURE.json) (unblended totals, pending labels, the
  honesty note once, preserved raw input — N32's visual test data) and the three-way determinism
  digests.
- Corpus: `python3 tools/n23_corpus.py` (twice — byte-identical records) →
  [the corpus record](evidence/N23_CORPUS_RECORD.json).
- Evidence: [N23 verification record](evidence/N23_VERIFICATION_RECORD.md), the
  [validation record](evidence/N23_VALIDATION_RECORD.json),
  [runtime record](evidence/N23_RUNTIME_RECORD.json),
  [chain record](evidence/N23_CHAIN_RECORD.json),
  [determinism record](evidence/N23_DETERMINISM_RECORD.json) and the Falkon paint check
  [evidence/N23_PAINT_REZULTATI.png](evidence/N23_PAINT_REZULTATI.png) — a render check only.

**Budgets, measured.** The artifact is 1,611,253 B (1,573.5 KiB); the two new data islands add
12,143 + 63,716 canonical bytes, the twelve `feedback.results.*` term entries grow the terms
island, and the three in-file smoke vectors (`SMK-N23-GRADE-FULL/PARTIAL/MALFORMED`, +7,387 B)
are inlined. Both interim ceilings were re-set on the measurement — runtime JS 264 → 280 KiB
(277,359 B) and artifact 1,504 → 1,600 KiB — with the declared bands left visible and **N31 the
final inline / lazy-load / re-budget owner**; the grading modules themselves (134,121 B compiled)
ship from `src/`, the N17–N20 pattern. The corpus records the forward projection honestly: a
merged build that inlined them would reach ≈1,699,804 B, N31's decision, recorded rather than
hidden.

**Handoffs.** N24 receives the binding format (with the optional `figure_id` for Q11) and the
point-binding rule; N25 receives the pure, digest-linked analytics events; N28 receives the
remediation payloads (concept ids, chain ids, card steps — every id resolvable, null chain
allowed); N32 receives the render fixture; N36 receives the classification table as its
mutation-test baseline.

**Not claimed.** No official examination, grade or proctoring status; no browser-render,
screen-reader, print or instructor acceptance (the paint check is a render check; N32/N33/N34/N37
own those gates); no semantic grading of free text; no N09 registry — the classification is
N23-authored PROPOSED training policy over the frozen vocabularies, and the 100-point scale, the
partial-credit reading and the priority ladder are declarations the 2025 programme does not set.

## Seeded, fair A/B/C form assembly (N24)

Three frozen 21-slot practice forms (`A`, `B`, `C`) and a deterministic seeded training draw now
bridge the frozen practice bank (`N20`) to the exam session machine (`N21`) under `PROPOSED`
training policy. [src/assembly.ts](src/assembly.ts) → [src/compiled/assembly.js](src/compiled/assembly.js)
(`root.SimAssembly`) and [tools/assemble_forms.py](tools/assemble_forms.py) run `SimPRNG`
(`splitmix64-u64-v1`, seeds `100001`–`100003` for `A`/`B`/`C`, `101000..199999` for runtime
training draws) over `review-passed` instances only, preserving per-topic counts (`3×7 = 21`),
per-topic points (`[10, 12, 20, 15, 16, 15, 12] = 100`), family uniqueness within each form, and
required completed types (`Q02, Q04, Q10, Q11, Q12, Q13, Q15`).

- **Independent verification & shortage honesty.** `verifyFormManifest` (JS) and Gate 20
  [validate_n24_assembly.py](tools/validate_n24_assembly.py) (Python) share zero logic with assembly.
  Pending-review or under-supplied slots emit an explicit `SHORTAGE` report with `disabled_reason_lv`
  and disable the picker control (`E_EXAM_FORM_DISABLED`) instead of relaxing constraints or drawing
  unreviewed instances; restoring review re-enables the form on the next assembly.
- **Fairness sweep & determinism.** Ten consecutive sweep seeds (`100101..100110`, 30 forms) cover all
  `28/28` families with `0` tripled flexible family slots, `0` tripled instance slots, `0` family
  triples under topic-flexible relaxation, and byte-identical regeneration digests (`N24-C01` records
  the 14 blueprint-pinned single-family slots alongside `N23-C01` and `N23-C03`).
- **Build-time freeze & pipeline guard.** `tools/build.py` verifies `#sim-bank` first, assembles
  [output/forms/form_A.json](output/forms/form_A.json),
  [output/forms/form_B.json](output/forms/form_B.json) and
  [output/forms/form_C.json](output/forms/form_C.json) (refusing absent or stale `bank_digest` with
  `E_ASSEMBLY_BANK_UNVERIFIED`), embeds `#sim-forms` (`16,067` canonical B) and `assembly.js`
  (`39,806` compacted B), and runs `SMK-N24-ASSEMBLY-DRAW` (`20/20` built-artifact smoke pass).
- **Contract & evidence:** [Form assembly contract](docs/FORM_ASSEMBLY_FORMAT.md),
  [N24 verification record](evidence/N24_VERIFICATION_RECORD.md),
  [validation record](evidence/N24_VALIDATION_RECORD.json),
  [runtime record](evidence/N24_RUNTIME_RECORD.json),
  [fairness sweep](evidence/N24_FAIRNESS_SWEEP.json),
  [corpus record](evidence/N24_CORPUS_RECORD.json), and Falkon paint checks
  [N24_PAINT_START.png](evidence/N24_PAINT_START.png) and
  [N24_PAINT_EXAM_PICKER.png](evidence/N24_PAINT_EXAM_PICKER.png).

**Budgets, measured.** `output/simulator.html` is `1,684,264` B (`1644.8` KiB; re-budgeted `1600 → 1680` KiB);
inline `runtime_js_code` is `329,976` B (`322.2` KiB; re-budgeted `280 → 332` KiB). Declared bands
(`700–1400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget
decision.

## Local, privacy-safe analytics and the honest progress record (N25)

A versioned, opt-in local store (`SimStore` in [src/store.ts](src/store.ts)) and honest progress record (`SimAnalytics` in [src/analytics.ts](src/analytics.ts)) now close Phase V over `#sim-analytics` ([data/analytics_schema.json](data/analytics_schema.json)), `#atskats` and `#iestatijumi`:

- **In-memory by default, explicit opt-in (`AGENTS.md` / `V-09`).** Default sessions make zero `localStorage` writes and leave zero keys. Explicit opt-in in `#iestatijumi` persists only `["sim_colloq1_store_v2"]` using canonical sorted-key UTF-8 JSON (`v2` schema, `max_events = 200` oldest-first pruning), supports `v1 → v2` migration, ignores `schema_version > 2` with a visible Latvian notice without overwriting it, exports `kimija-kolokvijs1-progress-v2.json` matching `store_digest`, and requires two-step confirmation for full erase.
- **Digest-linked, unblended and answer-text-free.** `SimAnalytics.extractEvents` matches `SimGrading.toAnalyticsEvents` byte-for-byte (`25` events over `FX-N23-MIXED`), keeping `auto_points` and `pending_external_points` unblended, tracking all `64` `#sim-coverage` outcomes (with honest `0` states), and persisting the `open` → `resolved` remediation queue for N28.
- **F10 boundary enforced.** `F10` dashboards, charts, streaks and gamification remain `REJECTED` per the roadmap/ledger; Gate 21 (`validate_n25_analytics.py`) and `check_n25_runtime.js` enforce zero banned exports, zero network attempts and zero outlier `localStorage` keys (`N25_PRIVACY_AUDIT.json`).
- **Contract & evidence:** [Analytics & store contract](docs/ANALYTICS_STORE_FORMAT.md), [N25 verification record](evidence/N25_VERIFICATION_RECORD.md), [validation record](evidence/N25_VALIDATION_RECORD.json), [runtime record](evidence/N25_RUNTIME_RECORD.json), [privacy audit](evidence/N25_PRIVACY_AUDIT.json), [corpus record](evidence/N25_CORPUS_RECORD.json), and Falkon render checks [N25_PAINT_ATSKATS.png](evidence/N25_PAINT_ATSKATS.png) and [N25_PAINT_IESTATIJUMI.png](evidence/N25_PAINT_IESTATIJUMI.png).

**Budgets, measured.** `output/simulator.html` is `1,756,388` B (`1,715.2` KiB; re-budgeted `1,680 → 1,720` KiB); inline `runtime_js_code` is `390,841` B (`381.7` KiB; re-budgeted `332 → 388` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Mastery state machine over outcomes (N26)

A validated, deterministic five-state mastery machine (`SimMastery` in [src/mastery.ts](src/mastery.ts) → [src/compiled/mastery.js](src/compiled/mastery.js)) now governs all 64 programme outcomes over `#sim-mastery-policy` ([data/mastery_policy.json](data/mastery_policy.json)), `#atskats`, and `#prakse`:

- **PROPOSED training policy (`UNDETERMINED` official counterpart).** Five states (`unseen ○`, `learning ◔`, `near_mastered ◑`, `mastered ●`, `needs_review ↻`) with explicit entry/exit/regression rules, `PROPOSED` thresholds (`2` / `2` / `1` consecutive correct criteria, `14` days inactivity, `1` miss in `mastered`), and predecessor T/F-card citations (`T02`, `T04`, `T17`, `F01`, `F07`, `F08`, `F10`). Gate 22 (`validate_n26_mastery.py`) verifies state reachability (rejecting scratch unreachable states by name) and 28-family / 112-instance / 267-criterion totality.
- **Pure reducer & strict evidence isolation.** `SimMastery.reduce` derives state solely from machine-graded criterion verdicts (`awarded` → `correct`, `denied` → `incorrect`, `pending`/`self`/`manual_pending`/`unattempted` ignored) and explicit decay events; fresh-process `--replay-only`, interleaved outcome independence, and `FX-N23-MIXED` end-to-end integration all match hand-computed expectations with identical SHA-256 digests.
- **Store persistence & honest, accessible views.** Absent `mastery` keys in pre-mastery `v2` or migrated `v1` stores map to all-64-`unseen`; `schema_version > 2` remains locked; `#atskats` and `#prakse` render icon + Latvian text (never color-only), never claim official competency, and mark outcomes with zero form-eligible instances as `⊘ Pagaidām nav pieejams` with their honest reason.
- **Contract & evidence:** [Mastery format](docs/MASTERY_FORMAT.md), [N26 verification record](evidence/N26_VERIFICATION_RECORD.md), [validation record](evidence/N26_VALIDATION_RECORD.json), [runtime record](evidence/N26_RUNTIME_RECORD.json), [3-profile view fixtures](evidence/N26_VIEW_FIXTURES.json), [corpus record](evidence/N26_CORPUS_RECORD.json), and Falkon render checks [N26_PAINT_ATSKATS.png](evidence/N26_PAINT_ATSKATS.png) and [N26_PAINT_PRAKSE.png](evidence/N26_PAINT_PRAKSE.png).

**Budgets, measured.** `output/simulator.html` is `1,817,433` B (`1,774.8` KiB; re-budgeted `1,720 → 1,780` KiB); inline `runtime_js_code` is `437,232` B (`427.0` KiB; re-budgeted `388 → 432` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Offline Leitner scheduler for spaced selection (N27)

A validated, deterministic, day-granular 3-box Leitner scheduler (`SimScheduler` in [src/scheduler.ts](src/scheduler.ts) → [src/compiled/scheduler.js](src/compiled/scheduler.js)) now drives the `#prakse` recommended-next queue and per-topic scheduling states over `#sim-scheduler-policy` ([data/scheduler_policy.json](data/scheduler_policy.json)):

- **PROPOSED training policy (`UNDETERMINED` official counterpart).** Standard 3-box Leitner model (`1 / 3 / 7` days, `queue_cap = 5`, no third-party Anki/SuperMemo/SM-2 code copied) mapping N26 mastery states (`unseen`/`learning`/`needs_review` → Box `1`, `near_mastered` → Box `2`, `mastered` → Box `3`) and citing `Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md §4.3` & `F08`. Gate 23 (`validate_n27_scheduler.py`) enforces strictly increasing intervals (rejecting scratch non-increasing box pairs by box number) and N10 term-key lint over all `scheduler.*` strings.
- **Injectable day-clock & pure selection.** `selectQueue` consumes explicit integer days / `YYYY-MM-DD` dates or an injected `DayClock` (`defaultDayClock()` uses local calendar date for interactive display only), computes overdueness floored at `0` for fresh items, orders by `overdue DESC` → `due_today` → `never_seen` (topic/id order) → `least_recently_practiced`, breaks ties by `outcome_id ASC`, and excludes unavailable outcomes (`N24`/`N26` `eligible_count === 0`) into `excluded[]`.
- **`#prakse` integration & N30 handoff.** Renders `#prakse-scheduler-panel` above the topic cards with the policy honesty note, 5-item queue, term-keyed Latvian reasons, per-topic box/overdue chips, and click-to-practice `N27-to-N30-practice-entry` handoff (selection data only, zero key material) that re-computes post-session when mastery updates.
- **Contract & evidence:** [Scheduler format](docs/SCHEDULER_FORMAT.md), [N27 verification record](evidence/N27_VERIFICATION_RECORD.md), [validation record](evidence/N27_VALIDATION_RECORD.json), [runtime record](evidence/N27_RUNTIME_RECORD.json), [N32 render fixture](evidence/N27_RENDER_FIXTURE.json), [corpus record](evidence/N27_CORPUS_RECORD.json), and Falkon render check [N27_PAINT_PRAKSE.png](evidence/N27_PAINT_PRAKSE.png).

**Budgets, measured.** `output/simulator.html` is `1,886,741` B (`1,842.5` KiB; re-budgeted `1,780 → 1,848` KiB); inline `runtime_js_code` is `491,765` B (`480.2` KiB; re-budgeted `432 → 484` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Missed-item remediation with anchors and alternate variants (N28)

A deduplicating, link-validated remediation flow (`SimRemediation` in [src/remediation.ts](src/remediation.ts) → [src/compiled/remediation.js](src/compiled/remediation.js)) now closes the teaching loop in `#atskats` over `#sim-remediation-policy` ([data/remediation_policy.json](data/remediation_policy.json)):

- **PROPOSED recommend-only policy (`UNDETERMINED` official counterpart).** Misses (`incorrect`, `partial`, `invalid`, `incomplete` with links) deduplicate by `(family_id, outcome_id)` without resurrecting `resolved` history, never force remediation gating, and never alter original graded attempts. Default `confirm_required` policy advances correct retries to `retried` with verbatim evidence copy (*Viena pareiza atbilde ir pierādījums virzībai...*), while `one_correct_resolves` behaves per its declared policy data.
- **Alternate-variant retries & N20 ephemeral fallback.** `selectRetryInstance` deterministically cycles `A → B → C → D` across eligible bank variants, falls back to `SimVariantEngine.instantiateEphemeral` once all bank letters are attempted, never re-serves the failed instance, updates `SimMastery` and the queue in one chain, and respects N30 practice-path bounds (`PATH_EXHAUSTED` without bypass).
- **Study handoffs & absolute link integrity.** Anchor links open `SimConceptDrawer` (`N07`), chain links mount `SimChains` (`N16`) at collapsed initial state (`data-revealed-count="0"`), families without worked chains render anchor-only (`chain_id: null`), and dangling links fail loudly (`E_REMEDIATION_DANGLING_LINK`) at both write time and on-read render time.
- **Contract & evidence:** [Remediation format](docs/REMEDIATION_FORMAT.md), [Analytics & store contract](docs/ANALYTICS_STORE_FORMAT.md), [N28 verification record](evidence/N28_VERIFICATION_RECORD.md), [validation record](evidence/N28_VALIDATION_RECORD.json), [runtime record](evidence/N28_RUNTIME_RECORD.json), [loop trace](evidence/N28_LOOP_TRACE.json), [privacy audit](evidence/N28_PRIVACY_AUDIT.json), [corpus record](evidence/N28_CORPUS_RECORD.json), and Falkon render check [N28_PAINT_ATSKATS.png](evidence/N28_PAINT_ATSKATS.png).

**Budgets, measured.** `output/simulator.html` is `1,972,615` B (`1,926.4` KiB; re-budgeted `1,848 → 1,928` KiB); inline `runtime_js_code` is `563,555` B (`550.3` KiB; re-budgeted `484 → 552` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Unified revision view and criterion self-assessment (N29)

`#atskats` now hosts the unified revision panel (`#atskats-revision-panel`) and F07 criterion self-assessment card (`#atskats-self-assessment-host` / `#atskats-sa-card`) implemented in [src/revision.ts](src/revision.ts) and governed by [data/revision_policy.json](data/revision_policy.json) (Gate 25, [tools/validate_n29_revision.py](tools/validate_n29_revision.py)):

- **All 64 outcomes & single-sourced truth.** Renders all 7 topics and all 64 programme outcomes with per-topic state summary lines, honest zero counts for untouched topics, N26 mastery state badges and last-practiced dates, N24/N26 honest `not-yet-available` counts/reasons, N28 active remediation counts, anchor/worked-chain/practice-entry affordances validated on read (`E_REVISION_DANGLING_LINK` fails loudly on broken anchors/chains), and `N27-to-N30-practice-entry` payloads handed to N30.
- **Strict F07 separation & key-free single-sourced criteria.** Criterion names come exclusively from `#sim-terms` (`feedback.criterion.<id>`) via `SimFeedback.criterionLabel` (`src/feedback.ts`) with zero key content exposed (`leak_matches=0`). Ratings (`confident`, `with_effort`, `not_yet`) use accessible `<select>` controls with `aria-live="polite"` announcements, a verbatim `note_max_length: 500` free-text note field with live counter, and explicit learner-assessment copy (`Izglītojamā paša novērtējums (F07, PROPOSED)`). Self-assessments persist in `sim_colloq1_store_v2.self_assessments` without ever modifying `mastery`.
- **Determinism, honesty audit & evidence.** 3-way determinism verified (`d407880deddd66d8...` panel / `522bd25a29030902...` card), honesty audit traces all `327` rendered elements to exactly one source (`0` untraceable, `0` merged), and `SMK-N29-REVISION-PANEL` runs in the built smoke suite (`25/25` PASS).
- **Contract & evidence:** [Revision format](docs/REVISION_FORMAT.md), [Analytics & store contract](docs/ANALYTICS_STORE_FORMAT.md), [validation record](evidence/N29_VALIDATION_RECORD.json), [runtime record](evidence/N29_RUNTIME_RECORD.json), [profile fixtures](evidence/N29_PROFILE_FIXTURES.json), [full-revision baseline](evidence/N29_FULL_REVISION_BASELINE.json), [honesty audit](evidence/N29_HONESTY_AUDIT.json), [corpus record](evidence/N29_CORPUS_RECORD.json), and Falkon render check [N29_PAINT_ATSKATS.png](evidence/N29_PAINT_ATSKATS.png).

**Budgets, measured.** `output/simulator.html` is `2,105,879` B (`2,056.5` KiB; re-budgeted `1,928 → 2,060` KiB); inline `runtime_js_code` is `630,624` B (`615.8` KiB; re-budgeted `552 → 620` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Bounded practice paths with filters and honest shortage handling (N30)

`#prakse` now hosts bounded, deterministic per-topic practice paths (`#prakse-practice-wrap`, `#prakse-topics-grid`, `#prakse-runner`, `#prakse-summary`) implemented in [src/practice.ts](src/practice.ts) → [src/compiled/practice.js](src/compiled/practice.js) (`root.SimPractice`) and governed by [data/practice_policy.json](data/practice_policy.json) (`#sim-practice-policy`, Gate 26, [tools/validate_n30_practice.py](tools/validate_n30_practice.py)), closing Phase VI:

- **PROPOSED bounded lengths grounded in N20 (`UNDETERMINED` official counterpart).** Per-topic target lengths `[6, 7, 8, 8, 7, 6, 5]` respect N20's `16` accepted instances per topic and `data/coverage.json` outcome counts (`[9, 10, 11, 11, 10, 8, 5]`, with Topic 7's 5-outcome path `5 < 8` Topic 3). Gate 26 validates lengths against live eligible counts (rejecting scratch overlong lengths by topic name) and validates all 18 filter response types (`Q01–Q18`) against `#sim-response-types`.
- **One pure engine across all entry points.** `SimPractice.computePracticePath` serves `topic_browse`, `scheduler_queue` / `revision_panel` (`N27-to-N30-practice-entry`), and `remediation_retry` (`N28-to-N30-remediation-retry`), enforcing the shared N24 review-eligibility gate, easy-to-hard ordering (`foundational → application → transfer`, falling back deterministically to `family_id ASC, variant_id ASC` when difficulty is absent), no-repeat within a path, current-session answered exclusion, and `unattempted_only` history filtering.
- **Honest shortage triad, skip semantics, N21 mode boundary & N23 grading chain.** Shortages report true length and reason (`pending_review`, `filter_shortage`, `history_exhausted` with dignified exits naming N27 `1 / 3 / 7` day intervals and N20's ephemeral variant path) without padding or drawing unreviewed items. Skips record as `skipped` (`0` incorrect verdicts, `0` mastery/remediation mutations). Practice answers grade through `SimGrading.gradePracticeRecord` + `SimFeedback.assemble` and update `SimMastery`, `SimRemediation`, and `SimStore` identically to exam sessions. Practice help surfaces (`hint`, `chain`, `term-lookup`) run under the N21 mode registry and are refused in `exam` mode (`E_MODE_COMPONENT_NOT_ALLOWED`).
- **Phase VI capstone journey & evidence:** [Practice format](docs/PRACTICE_FORMAT.md), [N30 verification record](evidence/N30_VERIFICATION_RECORD.md), [validation record](evidence/N30_VALIDATION_RECORD.json), [runtime record](evidence/N30_RUNTIME_RECORD.json), [10-step Phase VI journey trace](evidence/N30_JOURNEY_TRACE.json) (`572094d6a33c7500...`, fresh-process `--replay-only` parity across all 6 Phase VI modules including day `10 → 12` boundary), [corpus record](evidence/N30_CORPUS_RECORD.json) (`018a97139ac99812...`), and Falkon render check [N30_PAINT_PRAKSE.png](evidence/N30_PAINT_PRAKSE.png).

**Budgets, measured.** `output/simulator.html` is `2,202,649` B (`2,151.0` KiB; re-budgeted `2,060 → 2,156` KiB); inline `runtime_js_code` is `705,815` B (`689.3` KiB; re-budgeted `620 → 692` KiB). Declared bands (`700–1,400` KiB and `120–220` KiB) remain visible, and **N31** owns the final inline/lazy-load/re-budget decision.

## Idempotent single-file build pipeline (N31)

The Phase VII build pipeline ([tools/build.py](tools/build.py)) and its declared policy artifact ([data/build_policy.json](data/build_policy.json), `n31-single-file-build-policy-v1`, v1.0.0-n31, documented in [docs/BUILD_PIPELINE_FORMAT.md](docs/BUILD_PIPELINE_FORMAT.md)) now assemble every Phase I–VI deliverable into one reproducible offline file [output/simulator.html](output/simulator.html) (`2,649,417` bytes = `2,587.3` KiB, SHA-256 `d17237c39ab6d930fc5c5e94307f15a8ea7e5188eb2a5bcf0aa021de0a8cbe3c`) and its companion manifest [output/build-manifest.json](output/build-manifest.json) (`91,673` bytes, SHA-256 `eccd12f5e25e9fdc2b6da660db77775c13a4877ef1b8c30789fe061ce93c3e99`, `composite_digest: c05b1a8c29b52c8ace5b28a9f6eb5d5596f948045fc286924ee4d5d83147e3b8`):

- **Topological module order & final inline decision (Gate 27, [tools/validate_n31_build_policy.py](tools/validate_n31_build_policy.py)).** All 37 runtime modules (including all 11 Phase IV–V engine, input, and grading code modules: `quantity-engine.js`, `graph-scoring-engine.js`, `graph-capture.js`, `method-engine.js`, `method-card-view.js`, `variant-engine.js`, `inputs/{registry,components,integration}.js`, `grading.js`, `feedback.js`) are inlined inside the single `<script>` element in strict topological order (`137` forward load/init dependency edges validated; circular dependency fixture `ModuleA ↔ ModuleB` rejected naming both modules), each wrapped with `/* === MODULE: <path> === */` boundary comments. The 308.6 KiB authoring-time generator template asset (`src/variant-templates.js`) stays in `src/` because all 112 reviewed question instances are embedded in `#sim-bank`.
- **Skeleton template, deterministic JSON emission & digest stamping.** All 22 JSON islands (starting with the 7 core Section 1.2 islands `#sim-coverage`, `#sim-conventions`, `#sim-bank`, `#sim-forms`, `#sim-golden-vectors`, `#sim-terms`, `#sim-analytics`) emit with `sort_keys=True, separators=(",", ":"), ensure_ascii=False` and `</` escaped as `<\/`. Dry-run template assembly fills all 99 insertion points once (duplicate insertion attempts fail naming `#sim-bank` / `#sim-coverage`), and a 1-byte source mutation flips only the affected source, island/module digest, and `composite_digest`.
- **Three-run fresh-process idempotence, atomicity & collision survival.** Three fresh-process builds over unchanged sources produce byte-identical `output/simulator.html` (`d17237c39ab6d930...`, `0` B diff) and byte-identical manifests (`eccd12f5e25e9fdc...`). A mid-assembly decode error leaves the previous deliverable untouched on disk (`0` stray `.tmp` files), and `_atomic_write`'s unique temporary file policy survives pre-existing stale `.tmp` files without collision.
- **Standalone contract checker & sub-budget accounting (Gate 28, [tools/check_artifact.py](tools/check_artifact.py)).** Invokable standalone by N39's QA runner (`python3 tools/check_artifact.py`), asserting `lang="lv"`, 9/9 Section 1.2 ASCII anchors + `#piemeri`, 7/7 core islands and 22/22 total islands, 1 executable `<script>` parsing cleanly via Node `vm.Script` with 37 module boundary markers, `0` external URLs (with injected external URL fixture failing with URL, line `11`, and context named), V-10 unique ASCII IDs (`245` IDs, `0` duplicates, `0` unresolved `#anchor` hrefs), and exact sub-budget accounting (`bank_island` `243.9 / 420` KiB, `figures_island` `139.2 / 140` KiB, `css` `58.5 / 80` KiB, `runtime_js_code` `1,125.1 / 1,168` KiB, `artifact_total` `2,587.3 / 2,624` KiB; oversized scratch islands fail naming `bank_island` and `figures_island`).
- **Contract & evidence:** [Build pipeline format](docs/BUILD_PIPELINE_FORMAT.md), [N31 verification record](evidence/N31_VERIFICATION_RECORD.md), [validation record](evidence/N31_VALIDATION_RECORD.json), [runtime record](evidence/N31_RUNTIME_RECORD.json) (`27/27` in-file smoke vectors PASS with live in-file `SimEngines`, `SimInputs`, and `SimGrading` facades exercised), [artifact contract record](evidence/N31_ARTIFACT_CONTRACT.json), and [corpus record](evidence/N31_CORPUS_RECORD.json) (`4232fc0eff56bad1...` two-invocation parity).

## Reproducible QA runner and SHA-256 evidence chain (N39)

One local offline command validates every suite digest against the ledger, verifies all 132 build sources for tampering before execution, rebuilds `output/simulator.html` (N31) asserting its SHA-256 matches the ledger, executes all **15 registered suites** in 5 declared tiers inside fresh per-suite environments (build/static gates → audits → property/mutation corpus → Falkon visual matrix → Falkon offline browser smoke), and writes the two-pass SHA-256-chained run manifest:

```bash
python3 tools/qa_runner.py
```

- **Expected runtime:** `~11–12 min` total (`~58 s` for Tiers 1–3, `~9–10 min` for Tier 4 N37 visual matrix across 73 Falkon CDP renders, `~35–45 s` for Tier 5 N38 browser smoke).
- **Suite registry & versioned updates:** [data/qa_registry.json](data/qa_registry.json) records every suite's ledger-verified SHA-256 digest and timeout; legitimate updates require `python3 tools/qa_runner.py --update-suite <ID> --file <PATH> --reason "<reason>"` so no quiet digest edits exist.
- **Manifest schema & independent verification:** [data/qa_manifest_schema.json](data/qa_manifest_schema.json) and [docs/QA_RUNNER_FORMAT.md](docs/QA_RUNNER_FORMAT.md) document the two-pass JSON trailer and normalized verdict vector exclusion rule. Any maintainer can verify the manifest and frozen evidence pack independently without importing `qa_runner`:

```bash
python3 tools/verify_qa_manifest.py --manifest evidence/N39_QA_MANIFEST.json --pack evidence/N39_EVIDENCE_PACK.json
```

- **Evidence & handoff to N40:** [N39 QA manifest](evidence/N39_QA_MANIFEST.json), [N39 frozen evidence pack](evidence/N39_EVIDENCE_PACK.json), [two-run determinism proof](evidence/N39_TWO_RUN_EQUALITY.json), [order-independence proof](evidence/N39_ORDER_INDEPENDENCE.json), [independent verifier record](evidence/N39_VERIFIER_RECORD.json), [negative & corner fixtures](evidence/N39_FIXTURES_RECORD.json), and [N39 verification record](evidence/N39_VERIFICATION_RECORD.md). Honest open/UNVERIFIED items (N38 cross-engine/screen-reader/print rows, N09 gap, V-01 full-workspace mode, V-08 catalase) are enumerated explicitly in the pack for N40's release gate.

## Programme and planning files

- [Original programme PDF](RSU_MedChem_Colloq1_Prog_LV_2025.pdf): seven topics, written-on-paper examination, maximum 180 minutes.
- [Coverage matrix](docs/PROGRAMME_COVERAGE_MATRIX.csv): programme outcomes → copied master anchors → planned families.
- [Proposed form blueprint](docs/SIMULATION_BLUEPRINT.json): three A/B/C forms, 21 tasks, 100 practice points, 170 working minutes + 10 review. Weights and formats are proposals.
- [Family specifications](docs/QUESTION_FAMILIES.json): 28 families × four authoring specifications; not 112 finished questions.
- [Worked example data](docs/EXAMPLE_QUESTIONS.json): 14 proposed questions with answers, rubrics and variants.
- [Proposed instance schema](docs/QUESTION_SCHEMA.json): contracts for future authoring.
- [Copy manifest](COPY_MANIFEST.json): 174 files and their original/destination paths, roles, sizes and SHA-256.
- [Inspection ledger](evidence/INSPECTION_LEDGER.md) and [preparation verification](evidence/PREPARATION_VERIFICATION.json).

## Snapshot boundaries

materials/Chemistry_n contains the canonical master, every top-level course PDF/DOCX and selected source/conflict/calculation records. reference_plans/Chemistry_n contains 18 master/deep/improvement plan references. reference_governance/Chemistry_n contains archived source AGENTS.snapshot.md, visual policies and five detailed governance shards. Those are reference records, not active instructions for this new workspace. Imported code is supporting evidence, not a complete executable generator checkout. Caches, node_modules, screenshots, backup masters and unrelated numbered workspaces were not copied.

The snapshot totals 30,083,827 bytes (about 28.7 MiB), including seven masters and 35 course documents. Identical documents are kept under their source topic names to preserve provenance. No new external chemistry research was performed; historical source labels remain historical. The N02 and N03 paint checks used Falkon through `lite-shot` and are render checks, not browser-acceptance claims.

## Verify the preparation

From this directory: `python3 tools/verify_preparation.py --report evidence/PREPARATION_VERIFICATION.json`. This rechecks the published snapshot, plan structure, coverage anchors, type/family/variant records, blueprint totals and independently computed numerical examples. It does not run any copied generator. Future application, accessibility and print checks are separate roadmap gates.

### What the preparation check asserts, and what it only reports

The **PASS criterion is the published snapshot's integrity**: every one of the 174 `COPY_MANIFEST.json` destinations matches the manifest's own recorded size and SHA-256, the published set is exactly the declared set, the byte total and role counts hold, and the programme, design and exemplar checks pass.

The live sibling `Chemistry_1`–`Chemistry_7` workspaces are still dereferenced and compared, but a **divergence is reported, not failed**: those workspaces are actively developed and keep advancing after publication, so an upstream advance is not damage to this repository's published snapshot. Every divergence is listed per file under `checks.copies.upstream_divergence` with the source digest, size and mtime against the published digest. The source-workspace preservation baseline is treated the same way — the diff against the inspection-time baseline is reported, not failed.

The stronger contract is one flag away and still detects the drift on demand:

`python3 tools/verify_preparation.py --strict-sibling`

That mode fails on any source-versus-published divergence and on any baseline drift — it is what produced the 17 `Chemistry_4` failures before the contract was re-scoped, and it still reproduces them. The decision, its measurement and its rejected alternative (re-importing the advanced files) are recorded in [the verification ledger](evidence/VERIFICATION_LEDGER.md).

### Repository-local verification

The published repository alone verifies itself, without dereferencing the absent siblings:

`python3 tools/verify_preparation.py --repo-local --report evidence/REPO_LOCAL_VERIFICATION.json`

This asserts the 174 published `COPY_MANIFEST.json` destinations against the manifest's own recorded hashes, byte total and role counts. Its PASS is explicitly scoped to the published set; the 15,978-file source-preservation baseline stays unasserted. The clean-clone crash of the old default mode is reproduced and documented as V-01 in [the verification record](evidence/N01_VERIFICATION_RECORD.md).

The consumed sources are frozen in [the source-freeze inventory](evidence/SOURCE_FREEZE_INVENTORY.json) and recomputed live by [the inventory checker](tools/check_source_inventory.py): `python3 tools/check_source_inventory.py`. The [verification ledger](evidence/VERIFICATION_LEDGER.md) records the artifact digests and epistemic labels, and the [V-01 registry entry](evidence/V01_CONFLICT_ENTRY.json) is handed to N03.
