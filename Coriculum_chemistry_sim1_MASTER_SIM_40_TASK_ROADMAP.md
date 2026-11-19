# Coriculum_chemistry_sim1 Master Simulator: Evidence-Based 40-Task Roadmap

**Document class:** Engineering roadmap (a plan, not a finished product).
**Workspace:** https://github.com/GermanRobert-Labtester/Coriculum_chemistry_sim1 (inspected 2026-11-16).
**Deliverable of the planned work:** a single offline HTML file, `output/simulator.html`, in Latvian (`lang="lv"`), for Riga Stradins University (RSU) first-colloquium medical chemistry preparation.
**Structure:** 8 phases, 40 tasks (N01-N40), 120 main steps, 120 subtasks, 360 substeps, 120 acceptance criteria, a twelve-entry conflict ledger (V-01 to V-12) inheriting ten predecessor conflicts (C01-C10), and a ten-point release gate.
**How to read this document:** every factual claim about the repository carries an epistemic label defined in Section 5. Every task names its evidence, its verification and its rollback. The roadmap is executable in dependency order by the task index in Section 6.
## 1. Mission, Scope and the Deliverable Contract

### 1.1 Mission

The workspace exists to prepare RSU medical chemistry students for the first colloquium. The seven canonical master files carry the teaching content; this roadmap plans the construction of the one artifact the workspace does not yet have: a self-contained practice simulator that runs offline, entirely in Latvian, on a student laptop, with no network dependency, no installation and no account.

### 1.2 The deliverable contract

The simulator is a single HTML file, `output/simulator.html`, produced by an idempotent build (`tools/build.py`, planned in N31) from authoring data files. The contract terms, each enforced by a later task:

- **Single file and offline:** all CSS, JavaScript, figures (inline SVG) and data (embedded JSON islands) live inside the one file. Zero external URLs, no CDN, no fetched fonts, per the workspace governance (AGENTS.md, VERIFIED 2026-11-16). N11 asserts the figure layer and N35 audits the whole artifact.
- **Language:** the document language is Latvian (`lang="lv"`), matching the masters' own convention (VERIFIED). Runtime strings resolve through a terminology island (#sim-terms, N10).
- **Embedded JSON islands:** `#sim-coverage` (the 64-outcome coverage island, N02), `#sim-conventions` (constants, units, rules and the conflict registry, N03), `#sim-bank` (the frozen 112-instance practice bank, N20), `#sim-forms` (the seeded A/B/C assemblies, N24), `#sim-golden-vectors` (the frozen regression corpus, N05), `#sim-terms` (N10) and `#sim-analytics` (the local analytics schema, N25).
- **ASCII anchors:** `#sakums`, `#saturs`, `#prakse`, `#eksamens`, `#rezultati`, `#atskats`, `#metodika`, `#druka`, `#iestatijumi` (nine top-level anchors, matching the masters' ASCII anchor convention, VERIFIED).
- **Sessions:** in-memory by default; persistence is opt-in, versioned and local only (N25, N26), per the AGENTS.md session rule.
- **Print:** the file must survive paper: a print stylesheet and a no-JavaScript fallback (N34), because the real colloquium is a paper examination.

### 1.3 Size budget for the simulator file

The artifact must stay small enough to open instantly on an ordinary laptop and large enough to carry its bank and figures. The declared budget for `output/simulator.html` is **700-1400 KiB total**, composed of:

| Component | Budget |
| --- | --- |
| Practice bank island (#sim-bank) | 200-420 KiB |
| Runtime JavaScript | 120-220 KiB |
| CSS (both themes, print rules) | 40-80 KiB |
| Inline SVG figures | 60-140 KiB |

Each phase records its measured byte contribution against this budget (the ledger accounting in N15, N16, N17, N20 and N35), and the release gate (Section 18, G8) refuses an over-budget artifact.

### 1.4 The ten-point release gate

No release of the simulator exists until ten gates pass in N40: content fidelity to the masters, golden-vector regression, grading integrity, seeded assembly fairness, accessibility conformance, print and no-JavaScript honesty, performance and storage budgets, security audit, visual matrix pass, and evidence-chain completeness with human sign-off. The gate table is Section 18.

### 1.5 Official facts versus training-policy proposals

The roadmap separates what the official programme states from what this simulator proposes as training policy. **Official facts** (VERIFIED from the programme PDF, SHA-256 `f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9`, 353,208 bytes): seven topics, a paper examination, a maximum of 180 minutes. Nothing else in the simulator's scoring model is official. **Training-policy proposals** (all labeled PROPOSED in the tasks that use them): a 100-point scale, A/B/C forms, 21 slots per form, per-topic point weights 10/12/20/15/16/15/12, per-topic minute budgets 16/20/32/25/27/28/22, 28 item families (FAM-1A through FAM-7D) with 4 variants each (112 target instances), 18 response types (Q01-Q18), and the per-form required types Q02, Q04, Q10, Q11, Q12, Q13, Q15. Every user-visible surface that reflects a proposal carries the training-material banner (N06, N16, N21); no surface claims official examination status.
## 2. Approach and Execution Model

The roadmap follows an evidence-first execution model. Facts were established by direct inspection on 2026-11-16 (Section 3) before any task was written, and every task carries its own verification plan, so progress is provable rather than asserted. The model has five commitments:

1. **Dependency order.** Tasks execute in the order of Section 6. No task starts before its dependencies close; the dependency table is the contract.
2. **One authority per concern.** Constants live only in the conventions island (N03); arithmetic only in the quantity engine (N17); scoring only in the declared engines (N17-N19); item generation only in the variant engine (N20). No local drift copies. Where two artifacts must agree, a contract is frozen and handed over by digest (for example the figure-to-scoring tolerance coupling in N11 and N14).
3. **Frozen regression.** The golden vector corpus (N05) is oracle-independent, append-only and cross-language deterministic. Every engine and every build is proven verdict-for-verdict against it (N17, N18, N19, N36), so later phases cannot silently break earlier ones.
4. **Honest failure.** Every layer fails by name: malformed data, tampered islands, invalid templates and unreviewed bank instances are build-gated failures, never runtime surprises and never silent padding.
5. **Governance compliance.** No subagents (AGENTS.md); the frozen `materials/reference_plans/reference_governance` tree is read-only; offline execution with no network; visual checks through the lite-shot pipeline with Falkon (never an unapproved browser); in-memory sessions by default; no official examination claims anywhere.

Naming conventions throughout: authoring data lives in `data/` files (chains, figures, method cards, bank, terms); the build lives in `tools/`; the deliverable lives in `output/`. Evidence accumulates in the verification ledger referenced by every task; the ledger's digests make every claimed pass replayable.
## 3. Verified Repository Inspection (2026-11-16)

All facts in this section were established by direct inspection of the repository on 2026-11-16 and are labeled `VERIFIED (2026-11-16)` unless another label is stated. They are the evidentiary basis of every task's Current State and Evidence block.

### 3.1 The workspace and its programme

The repository is a Latvian-language RSU medical chemistry first-colloquium preparation workspace. The official programme PDF is present at 353,208 bytes with SHA-256 `f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9` (VERIFIED). Its official facts are: seven topics, a paper examination, a maximum of 180 minutes (VERIFIED). The simulator itself is not implemented anywhere in the repository (VERIFIED).

### 3.2 The seven canonical masters

| Master | Bytes | Notes from inspection |
| --- | --- | --- |
| C1 | 1,018,215 | 382 id attributes; 2 localStorage references |
| C2 | 969,738 | single inline script |
| C3 | 1,039,699 | single inline script |
| C4 | 2,502,506 | 16 localStorage references; search-index, exam-bank and thermo-test-vectors JSON islands |
| C5 | 1,518,065 | inhib-data island; zero localStorage references |
| C6 | 1,829,918 | master-data island |
| C7 | 348,993 | smallest master |

All seven masters use `lang="lv"`, a single inline script, `@media print` rules, the ids `theme-toggle` and `saturs`, and ASCII anchor ids such as `#stehiometrija` and `#maisijumi` (VERIFIED). These conventions are inherited by the deliverable contract in Section 1.2.

### 3.3 Coverage and integrity facts

The teaching coverage decomposes into **64 outcomes** (per-topic counts 9/10/11/11/10/8/5), and every one of the 64 `master_anchor` values resolves against its master (zero failures, verified programmatically in the inspection; formalized by N02). `COPY_MANIFEST.json` records 174 files, 30,083,827 bytes, SHA-256 `07d49735060796c3...`, with roles: canonical-master 7, course-source 35, supporting-reference-data 65, planning-reference 18, archived-governance-reference 49 (VERIFIED).

### 3.4 The preparation-verification finding (V-01)

A clean clone of the repository **cannot** run `tools/verify_preparation.py` to success: the script crashes with `KeyError: 1` inside `verify_data`, because the COPY_MANIFEST sources point to sibling `Chemistry_1`-`Chemistry_7` directories that are not published in the repository (VERIFIED, reproduced on 2026-11-16 with the exact traceback recorded). A committed artifact `evidence/PREPARATION_VERIFICATION.json` (timestamp 2026-11-16T21:12:03Z, status PASS, 174 files, 15,978 preserved files, 13 of 14 examples recomputed) therefore carries the label **DOCUMENTED BUT NOT RERUN**: it is evidence that the full workspace passed on the original machine, but no clean clone can currently reproduce it. N01 resolves this with a mode-flagged, repository-local verification mode, and the finding is tracked as V-01 in Section 4.

### 3.5 The predecessor roadmap and its conflicts

The workspace contains a predecessor audit and roadmap, `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` (76,047 bytes), with 20 T-cards, 10 F-cards and 5 B-cards, all in NOT STARTED state (VERIFIED). It registers conflicts C01-C10, including the percentage-basis ambiguity, the mg/g/L density conversion defect, the standard-potential notation mixing, endpoint persistence, the 440 nm flatness question, calibration and path-length assumptions, and the unresolved K10/K17 catalase items. Section 4 inherits these conflicts and maps every predecessor card onto this roadmap's tasks.

### 3.6 Governance rules in force

AGENTS.md (VERIFIED) requires: no subagents; `materials/reference_plans/reference_governance` frozen read-only; offline operation with no CDN or network fetches; visual checks through the lite-shot pipeline with Falkon, never an unapproved browser; in-memory sessions by default; no claims of official examination status. Every task in this roadmap operates inside these rules, and N33, N37 and N38 stage their browser-dependent verifications accordingly.
## 4. Governance, Conflict Ledger and Predecessor Mapping

### 4.1 The conflict ledger (V-01 to V-12)

Twelve findings from the inspection carry conflict status. Each is registered in the conventions artifact (N03) with its evidence citation, and each is either resolved by a named task or explicitly deferred with its reason recorded.

| Id | Finding | Status and owning task |
| --- | --- | --- |
| V-01 | `verify_preparation.py` crashes with `KeyError: 1` on a clean clone; committed PASS evidence is not reproducible (DOCUMENTED BUT NOT RERUN) | Resolved by N01 (repository-local verify mode) |
| V-02 | Percentage-basis ambiguity (mass versus volume percent) in masters and predecessor | Resolved by N03 rule, enforced in figures (N11) and engines (N17) |
| V-03 | Standard-potential notation mixing (E degrees versus E zero-prime) | Resolved by N03 notation entry; term island renders it (N10) |
| V-04 | mg/g/L density conversion defect (the classic dimensional slip) | Resolved by the dimension gate in N17, structurally excluded |
| V-05 | Endpoint versus equivalence-point wording | Resolved by N03 wording rule, enforced in titration figures (N15) |
| V-06 | 440 nm flatness claim scope | Resolved by the scope-note rule in N13 |
| V-07 | Calibration and path-length assumptions unstated | Resolved by the assumption-annotation discipline in N15 |
| V-08 | Catalase K10/K17 values scientifically unresolved | Honesty note enforced in N13 and N09; no disputed values asserted |
| V-09 | localStorage persistence divergence across masters (2/16/0 references) | Resolved by the versioned opt-in store in N25 and N26 |
| V-10 | id attribute density (382 in C1) collision risk | Resolved by the namespace registry in N06 and N31 |
| V-11 | JSON island shape divergence across masters | Resolved by the single island schema set of Section 1.2 |
| V-12 | Print convention divergence | Resolved by the unified print contract in N34 |

### 4.2 Inherited predecessor conflicts (C01-C10)

The predecessor roadmap's conflicts C01 through C10 (Section 3.5) are inherited. Where a C-conflict coincides with a V-finding (percentage basis, density defect, potential notation, endpoint persistence, 440 nm, calibration assumptions, catalase), the V-row above owns it. The remaining predecessor conflicts (including endpoint persistence mechanics and residual governance ambiguities) are carried into the owning tasks' Risks and Guardrails blocks, and N40's ledger closure requires each inherited conflict to be closed or explicitly deferred with a recorded reason.

### 4.3 Predecessor card mapping (T/F/B to N-tasks)

Every predecessor card lands on this roadmap. Nothing is dropped silently; deferrals and rejections are named:

| Predecessor item | Disposition in this roadmap |
| --- | --- |
| T-cards (20 audit-and-fix cards) | Distributed into the implementing N-tasks: source and verification work into N01-N05, figure work into N11-N15, engine work into N16-N20, exam work into N21-N25 |
| F03 bounded practice paths | Implemented by N30 with honest shortage warnings |
| F04 print and paper mode | Implemented by N34, including the paper worksheet |
| F07 criterion self-assessment | Implemented by N29 with pending semantics (never parsed, never keyword-matched) |
| F08 adaptive difficulty | **DEFERRED** with reason: the mastery machinery (N26-N27) must stabilize first; deferral recorded in N40's ledger closure |
| F10 analytics dashboards | **REJECTED** with reason: the analytics stay local and privacy-safe (N25); no dashboard surface is planned, and the rejection boundary is recorded in N25 |
| Leitner spaced repetition (approved direction) | Implemented by N27 over the mastery state machine (N26) |
| B-cards (5 governance cards) | Absorbed into the governance rules of Section 2 and the release gate (Section 18) |
## 5. Epistemic Labels

Every factual claim in this roadmap carries one of six labels. The rules of use follow the definitions; a claim without a label is a plan statement, not a fact.

| Label | Meaning |
| --- | --- |
| `VERIFIED (2026-11-16)` | Established by direct inspection or execution on 2026-11-16, with the command, artifact or computation recorded |
| `DOCUMENTED BUT NOT RERUN` | A committed artifact records a pass, but it cannot be reproduced from a clean clone (the V-01 class) |
| `UNVERIFIED` | Asserted by a source but not independently reproduced in this inspection |
| `UNDETERMINED` | Inspected and found to have no single correct answer yet (the V-08 catalase class) |
| `UNAVAILABLE` | Cannot be verified in this environment at all (for example, proprietary browser runs) |
| `PROPOSED` | A training-policy choice of this roadmap, not an official fact (Section 1.5) |

Rules of use: (1) VERIFIED claims name their evidence in the owning task; (2) a DOCUMENTED BUT NOT RERUN claim must name the artifact and the reason it cannot be rerun; (3) UNVERIFIED claims must become VERIFIED or be removed before the owning task closes; (4) UNDETERMINED claims are handled by honesty notes, never by silently choosing a value; (5) PROPOSED values are never presented to the learner as official. The end matter's truthful self-audit (Section 20) reviews the whole document against these rules.
## 6. Task Index and Dependency Map

Forty tasks in eight phases. The dependency column is the execution contract: a task starts only when every dependency has closed its Definition of Done. Phase boundaries are review points, not barriers; the dependency graph is the authority.

| Task | Title (short) | Phase | Priority | Risk | Effort | Depends on |
| --- | --- | --- | --- | --- | --- | --- |
| N01 | Freeze the consumed sources | 1 | P0 | High | M | None |
| N02 | Build the coverage island: 64 outcomes with verified master anchors | 1 | P0 | High | M | N01 |
| N03 | Author the conventions artifact and the conflict registry | 1 | P0 | High | L | N01 |
| N04 | Author the QUESTION_SCHEMA validator | 1 | P0 | High | L | N01 |
| N05 | Build the golden vectors and the cross-language seed policy | 1 | P0 | High | L | N04 |
| N06 | Build the start screen, objectives view | 2 | P1 | Medium | M | N02 |
| N07 | Build the concept map, the ASCII anchor graph and the concept drawer | 2 | P1 | Medium | M | N02, N06 |
| N08 | Build the recall layers and the hint drawer surfaces | 2 | P2 | Medium | M | N07 |
| N09 | Build the misconception registry and the distractor signature taxonomy | 2 | P1 | Medium | L | N02, N03 |
| N10 | Build the terminology island and the unit-string lint | 2 | P2 | Medium | M | N03, N02 |
| N11 | Build the inline SVG figure framework and the T1-2 records | 3 | P1 | Medium | L | N04, N10 |
| N12 | Author the T2-3 burette and dilution figures | 3 | P1 | Medium | M | N11 |
| N13 | Author the T4 energy, Hess and Maxwell-Boltzmann figures | 3 | P1 | Medium | M | N11 |
| N14 | Author the T5 kinetics figures with linearization tolerance fields | 3 | P1 | Medium | M | N11 |
| N15 | Author the T6-7 titration curves and calibration figures | 3 | P1 | Medium | M | N11, N12 |
| N16 | Author the EX01-EX14 worked example chains | 4 | P0 | Medium | L | N07, N11, N15 |
| N17 | Implement the quantity and conservation engines | 4 | P0 | High | L | N03, N05, N09 |
| N18 | Implement the graph scoring engine | 4 | P0 | High | L | N05, N11, N14 |
| N19 | Author the method cards | 4 | P1 | Medium | M | N05, N09, N16 |
| N20 | Implement the variant engine and author the 112-instance practice bank | 4 | P0 | High | L | N04, N16, N17, N18, N19 |
| N21 | Build the exam shell: timer, navigation, flags and view discipline | 5 | P0 | High | L | N06, N16, N20 |
| N22 | Define response input semantics for all 18 types | 5 | P0 | High | L | N17, N19, N21 |
| N23 | Implement error classification and the partial-credit grading engine | 5 | P0 | High | XL | N17, N18, N19, N21, N22 |
| N24 | Implement seeded, fair A/B/C form assembly | 5 | P0 | High | L | N05, N20, N21 |
| N25 | Implement local, privacy-safe analytics and the honest progress record | 5 | P1 | Medium | M | N21, N23 |
| N26 | Implement the mastery state machine over outcomes | 6 | P1 | Medium | M | N23, N25 |
| N27 | Implement the offline Leitner scheduler for spaced selection | 6 | P2 | Medium | M | N26 |
| N28 | Implement missed-item remediation with anchors and alternate variants | 6 | P1 | Medium | M | N07, N20, N26 |
| N29 | Build the unified revision view and criterion self-assessment | 6 | P2 | Medium | M | N16, N23, N26 |
| N30 | Implement bounded practice paths | 6 | P1 | Medium | M | N08, N20, N26 |
| N31 | Implement the idempotent single-file build pipeline | 7 | P0 | High | L | N05, N16, N20, N25, N30 |
| N32 | Implement the responsive layout and WCAG 2.2 AA contract | 7 | P1 | High | L | N31 |
| N33 | Implement keyboard-only operation and screen-reader semantics | 7 | P1 | High | L | N31, N32 |
| N34 | Implement the no-JavaScript fallback and the print and paper mode | 7 | P2 | Medium | M | N31 |
| N35 | Run the performance, storage and security audit | 7 | P1 | High | M | N31, N32, N34 |
| N36 | Build the property and mutation test suites against the golden corpus | 8 | P0 | High | L | N17, N20, N23, N31 |
| N37 | Run the visual regression matrix with the lite-shot and Falkon policy | 8 | P1 | High | L | N32, N34 |
| N38 | Run the cross-engine offline smoke and the staged manual protocols | 8 | P1 | High | M | N37 |
| N39 | Build the reproducible QA runner and the SHA-256 evidence chain | 8 | P1 | Medium | M | N36, N37, N38 |
| N40 | Execute the release gate, close the conflict ledger | 8 | P0 | High | M | N39 |

### 6.1 Critical path

The critical path runs N01 to N05 (the baseline: sources, coverage, conventions, schema, vectors), through N16-N20 (the engines and the bank), into N21-N23 (exam, inputs, grading) and N31 (the build), and ends at N40 (the release gate). The figure phase (N11-N15) and the learning-science phase (N26-N30) branch from the baseline and rejoin before N31 and N36 respectively. The heaviest concentration of risk sits on N17, N20, N23 and N31, which carry the High risk rating and gate the most dependents.


## 7. Phase I (N01-N05) - Scientific Baseline, Source Traceability, Contract, Keys and Frozen Regression

Phase I establishes the ground truth every later task stands on. The sources are frozen by digest (N01), the verification finding V-01 is resolved with a repository-local mode so a clean clone can verify the workspace, the 64-outcome coverage island is built with every master anchor resolvable (N02), the conventions artifact and the twelve-entry conflict registry are authored (N03), the QUESTION_SCHEMA validator and its single loader are built for all eighteen response types (N04), and the golden vector corpus with its cross-language seed policy is frozen as the roadmap's regression authority (N05). When this phase closes, nothing unverified can enter the simulator, and every later engine has its oracle.

### N01 - Freeze the consumed sources and make repository-local verification runnable

**Phase:** Phase I | **Priority:** P0 | **Risk:** High | **Effort:** M | **Dependencies:** None

**Domain:** Source freeze and verification

**Current State and Evidence:** `VERIFIED (2026-11-16)`: tools/verify_preparation.py exists in the published repository but crashes on a clean clone with KeyError: 1 inside verify_data, because COPY_MANIFEST.json's source entries point at sibling Chemistry_1 through Chemistry_7 directories that are not published; the committed evidence/PREPARATION_VERIFICATION.json (2026-11-16T21:12:03Z, PASS, 174 files, 15,978 preserved files, 13 of 14 examples recomputed) was therefore produced in the author's full workspace and is DOCUMENTED BUT NOT RERUN here. No mode flag, no local-clone verification path, and no frozen digest inventory of the sources this roadmap consumes exist.

**Purpose and Rationale:** Every later task must be able to cite sources that cannot silently change underneath it, and must be able to verify data integrity inside the published repository alone. This task freezes the consumed sources (the seven masters C1-C7, COPY_MANIFEST.json, the programme PDF with its recorded digest, the blueprint, AGENTS.md and the predecessor roadmap) into a digest inventory, and adds a mode flag to verify_preparation.py so it can run in repository-local mode: asserting the published 174-file set against COPY_MANIFEST with the manifest's own hashes, without dereferencing the absent sibling directories, so a clean clone can produce its own PASS for the files it actually ships.

**Target Artifacts and Touchpoints:** tools/verify_preparation.py (mode-flagged, repository-local path); the source digest inventory artifact; the verification record. Evidence touchpoints: COPY_MANIFEST.json (30,083,827 bytes across 174 files, SHA-256 recorded in the inspection), the seven masters (C1 1,018,215; C2 969,738; C3 1,039,699; C4 2,502,506; C5 1,518,065; C6 1,829,918; C7 348,993 bytes), the programme PDF (353,208 bytes, SHA-256 f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9).

**Out of Scope:** No attempt to publish or reconstruct the absent Chemistry_1 through Chemistry_7 siblings (out of this roadmap's control and outside the repository's scope); no modification of the frozen materials/ tree (AGENTS.md forbids it); no claim that the committed PASS record was reproduced (it stays DOCUMENTED BUT NOT RERUN in the ledger).

**Main Step A - Reproduce and document the V-01 crash precisely.** Reproduce the clean-clone crash of tools/verify_preparation.py exactly as a reviewer would: run it on the published repository alone, capture the KeyError: 1 with its full traceback, identify the failing dereference in verify_data (a COPY_MANIFEST source entry whose key is absent because the sibling directories are not published), and record the finding as V-01 in the conflict registry with the command, the traceback and the environment; the reproduction is the prerequisite for every later credibility claim, since it establishes that this roadmap verifies rather than assumes.

**Subtask A.1 - Characterize the failure boundary exactly.** Determine precisely which assertions of verify_preparation.py can run repository-locally (the published-file set, the manifest's own recorded hashes, the file count and byte total) and which cannot (the sibling-source comparisons, the 15,978-file preserved-tree assertion, the 13-of-14 example recomputation that depends on sources), so the mode flag's repository-local PASS is defined as an honest subset of the original verification, explicitly named, never a silent redefinition of what PASS means.

- **A.1.1 -** Run the reproduction on the clean clone, capture the traceback verbatim, and record V-01 with the exact failing line and manifest entry type; the corner case is a reviewer with the sibling directories present (the author's workspace), where the script runs as designed, and the finding text must state explicitly that the crash is a property of the published repository alone, so the two environments are never conflated.

- **A.1.2 -** Inventory the script's assertions into the two classes (runnable-locally versus sibling-dependent) by reading verify_data against COPY_MANIFEST's structure (174 files, 30,083,827 bytes, the recorded SHA-256 07d49735060796c3 with the roles distribution: 7 canonical-master, 35 course-source, 65 supporting-reference-data, 18 planning-reference, 49 archived-governance-reference), and record the classification table with each assertion's class and its evidence.

- **A.1.3 -** Write the V-01 registry entry with the status documented (not resolved by this roadmap: the siblings are external) and the mitigation (the mode flag this task builds), and record the entry's digest; the registry itself belongs to N03, which will consolidate it, so this task hands the entry over in the recorded format N03 defines.

**Main Step B - Implement the mode flag and the repository-local path.** Implement the mode flag in tools/verify_preparation.py: a declared argument (for example --repo-local) that selects the repository-local verification path, asserting the 174 published files against COPY_MANIFEST's hashes and totals without dereferencing absent siblings, emitting a PASS record that names its scope explicitly (repository-local: published set only) so the record can never be mistaken for the full-workspace PASS; the default mode remains the original behavior, untouched, since the author's full workspace must keep its workflow.

**Subtask B.1 - Prove the mode flag honestly on both environments.** Prove the new path in the repository: a clean clone with --repo-local produces a PASS naming the 174-file scope; the negative fixtures are a tampered scratch copy (one file's content altered) failing with the file named, and a deleted scratch file failing the count, since a verifier that cannot fail is not a verifier; the untouched default mode is re-run in the full workspace if available, or its non-availability is recorded honestly (UNAVAILABLE in this environment), so neither mode's claim exceeds its evidence.

- **B.1.1 -** Implement the --repo-local path with its scoped PASS record (file count, byte total, hash-match count, the explicit scope line, the run's date and environment) and record the clean-clone PASS output verbatim; the corner case is hash-format drift between COPY_MANIFEST's recorded hash style and the verifier's computation (the inspection recorded the manifest SHA as 07d49735060796c3, a prefix convention), and the path must honor the manifest's own format rather than assume full digests, with the format reading recorded.

- **B.1.2 -** Implement the negative fixtures over scratch copies (tamper, delete, truncate) and record each failure with the file named and the exit code; the corner case is the manifest's own byte total assertion (30,083,827 bytes) interacting with line-ending normalization if a copy tool rewrites files, so the fixtures copy byte-exactly and the record states the byte-exact discipline.

- **B.1.3 -** Record the default-mode status honestly: in this environment the full-workspace mode cannot be exercised (the siblings are UNAVAILABLE), the committed PREPARATION_VERIFICATION.json remains DOCUMENTED BUT NOT RERUN, and the ledger entry states exactly this, so the roadmap never borrows the author's PASS as its own.

**Main Step C - Freeze the consumed-source digest inventory.** Build the source digest inventory artifact: for every source this roadmap consumes (the seven masters with their recorded byte sizes, COPY_MANIFEST.json, the programme PDF with its recorded SHA-256, the blueprint, AGENTS.md, the predecessor roadmap MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md at 76,047 bytes), record the SHA-256 digest, byte size and role, forming the frozen baseline that every later task's evidence citations point into; the inventory is the roadmap's own anchor, and its digest enters the ledger first.

**Subtask C.1 - Prove the inventory is complete and checkable.** Prove the inventory: a checker script recomputes every digest from the live files and compares against the artifact (a green pass recorded), and the negative fixture is a scratch-altered master copy failing the check with the file named, proving the inventory watches rather than decorates; the corner case is the programme PDF's already-recorded digest (f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9), which the inventory must reproduce exactly, closing the loop between the inspection's claim and the artifact's record.

- **C.1.1 -** Author the inventory artifact with per-source entries (digest, size, role, the consuming tasks) and record the checker's green pass; the corner case is a source later found to be missing from the published repository (a planning reference held only in the author's workspace): such an entry is recorded UNAVAILABLE with its consequence for downstream tasks stated, never silently dropped, and the inventory's completeness rule (every consumed source has an entry of some status) is recorded.

- **C.1.2 -** Run the tamper fixture over a scratch copy and record the named failure; then run the PDF digest reproduction and record the match against the inspection's value verbatim, so the strongest single anchor of the scientific baseline is verified twice by two records.

- **C.1.3 -** Append the inventory artifact's digest, the mode-flagged script's digest and both verification records to the ledger with their epistemic labels (repository-local PASS as VERIFIED in this environment; the committed workspace PASS as DOCUMENTED BUT NOT RERUN), and hand the frozen inventory to N02, N03, N04 and N05 as their citation baseline, closing the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given a clean clone, when verify_preparation.py runs with the mode flag, then the repository-local path PASSes over the 174 published files with its scope named, and the default mode is untouched.

- **AC2 (negative or edge case):** Given the reproduction record, when a reviewer reads V-01, then the KeyError: 1 traceback, the failing manifest entry class and the two-environment boundary are all stated verbatim, with the committed PASS kept DOCUMENTED BUT NOT RERUN.

- **AC3 (domain integrity and zero-regression):** Given the source inventory and its checker, when digests are recomputed live, then every consumed source matches (a scratch tamper fails by name) and the programme PDF digest reproduces the inspection value exactly.

**Verification and Evidence:** Record the reproduction command and traceback, the assertion classification table, the repository-local PASS output, the three negative fixture failures, the inventory checker pass and the PDF digest match. Epistemic labels: reproduction and repository-local PASS are VERIFIED (2026-11-16) in the recorded environment; the workspace-mode PASS stays DOCUMENTED BUT NOT RERUN.

**Risks, Guardrails, and Rollback Plan:** Risk: the mode flag drifting from upstream script changes if the author reworks verify_preparation.py. Guard: the script's digest is ledger-recorded, so a change is a visible event, and the flag is additive (default mode untouched). Rollback: remove the flag; the original script and the committed PASS record stand as they stood, and this roadmap's claims revert to citing the committed record with its honest label.

**Definition of Done:** The published repository verifies itself locally, the V-01 crash is reproduced and documented with its exact boundary, and every consumed source is frozen under a checker-verified digest inventory, giving all later tasks an unchanging, honest citation baseline.

### N02 - Build the coverage island: 64 outcomes with verified master anchors

**Phase:** Phase I | **Priority:** P0 | **Risk:** High | **Effort:** M | **Dependencies:** N01

**Domain:** Coverage model

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the workspace defines 64 coverage outcomes distributed per topic as 9, 10, 11, 11, 10, 8 and 5 across the seven topics, each carrying a master_anchor field; an inspection pass with an HTML parser confirmed that all 64 master_anchor values resolve to real targets inside the seven masters (zero failures). No machine-validated coverage artifact, no embedded island and no drift guard exist; the outcomes currently live only in planning documents.

**Purpose and Rationale:** The coverage island is the single source of truth for what the simulator teaches: every outcome gets an id, its topic, its official wording source (the programme's seven topics are official; the outcome granularity is this roadmap's training-policy proposal, labeled as such), its master_anchor (the verified in-master target), its practice and exam bindings (filled by later tasks), and its prerequisite edges (the concept graph of N07); embedding it as a JSON island in the simulator means every view, engine and report reads one copy, and the drift guard proves the island matches the planning source until the island supersedes it as the recorded authority.

**Target Artifacts and Touchpoints:** data/coverage.json (the authored island source, inlined by the build as #sim-coverage); the coverage validator; the anchor resolution record. Touchpoint in output/simulator.html: the #sim-coverage island and every view that lists topics or outcomes.

**Out of Scope:** No rewriting of the masters' own content (the anchors point into them read-only); no claim that the 64-outcome granularity is official (the programme states topics, not outcomes; the split is PROPOSED); no learning-objective invention beyond what the planning source and masters support.

**Main Step A - Author the coverage island from the planning source.** Author data/coverage.json: for each of the 64 outcomes, the fields (id in a stable ASCII scheme, topic 1 through 7, the outcome's Latvian statement aligned with its master's wording, master_anchor with the verified target, the point and minute bindings left as declared slots for N24's policy, the prerequisite edge list), with the file generated or at least cross-checked against the planning source so the 64 outcomes and their per-topic distribution (9, 10, 11, 11, 10, 8, 5) match exactly, since any transcription slip here propagates into every later module.

**Subtask A.1 - Validate structure and the two-level labeling.** Validate the island: the schema check (every field present, ids unique and stable, topics in range, edge targets resolving to outcome ids), the count assertions (64 outcomes, the seven per-topic counts), and the labeling audit (topic names and the paper format are official facts; the outcome statements' granularity is training policy), recorded so a later reader knows exactly which parts of the island carry which epistemic weight.

- **A.1.1 -** Author the island with a generation or verification step against the planning source, and record the count table (per-topic 9, 10, 11, 11, 10, 8, 5, total 64) with the match assertion; the corner case is an outcome whose planning wording differs subtly from its master's section wording (the masters are the scientific authority), and the rule is recorded: master wording wins, the planning wording is noted in the entry's comment field, never silently edited.

- **A.1.2 -** Implement the schema validator with the edge-resolution check (a prerequisite edge to a nonexistent outcome fails with both ids named), and record the pass; a scratch cycle in the edge set (A requires B, B requires A at the topic root level) must be detected and rejected, since a cyclic prerequisite graph would make N07's concept map and any later sequencing incoherent.

- **A.1.3 -** Run the labeling audit and record it: the official facts (seven topics, paper colloquium, 180 minutes) marked as programme-sourced, the outcome granularity marked PROPOSED, and the audit note stating that the programme PDF's own text carries no outcome-level split, so the island's statements are derivations, honestly labeled.

**Main Step B - Verify anchor resolution and embed the island.** Re-verify all 64 master_anchor values against the frozen masters from N01: the anchor resolution script parses each master's HTML and asserts every anchor target exists (the inspection's zero-failure result must be reproduced as this task's own recorded evidence, not borrowed), then the island is embedded as the #sim-coverage script island with the build's JSON emission rules, ready for the runtime's single loader.

**Subtask B.1 - Prove resolution survives the frozen state.** Prove resolution against the frozen digests: the resolution record names each master's digest (so the proof is bound to the exact frozen bytes), and the negative fixture is a scratch anchor pointing at a removed target, which must fail with the anchor and master named, since the resolution check is the learners' guarantee that every outcome link lands somewhere real.

- **B.1.1 -** Implement the anchor resolution script over the frozen masters (the same HTML-parser approach the inspection used, recorded with its digest inputs) and run it: 64 of 64 resolved, zero failures, with the per-topic resolution counts recorded; the corner case is anchor case sensitivity (the masters use ASCII ids like #stehiometrija and #maisijumi, verified in the inspection), and the script asserts case-exact matching rather than normalizing, with the rule recorded.

- **B.1.2 -** Implement the negative fixture (a scratch island entry with a dangling anchor) and record the named failure; then embed the island through the build's emission rules (sorted keys, declared separators, UTF-8 with Latvian text intact, matching the masters' own island style) and record the embedded island's digest.

- **B.1.3 -** Record the resolution record's own digest in the ledger with the VERIFIED (2026-11-16) label bound to the frozen master digests, so any future master change invalidates the record visibly rather than silently, and hand the island contract to N07 (the graph), N16 (the chains) and N24 (the assembly bindings).

**Main Step C - Implement the drift guard and the runtime loader.** Implement the drift guard: the validator's full check (schema, counts, edges, labeling audit, anchor resolution) runs as a build gate, so a future edit that breaks any property fails the build before an artifact ships; and implement the runtime loader contract: one function reads #sim-coverage, validates the invariants cheaply (counts and id uniqueness, the heavy anchor check stays build-time), and hands typed records to consumers, with corrupted-island behavior defined per the N35 error contract (honest, named degradation).

**Subtask C.1 - Prove the guard fails closed and the loader is single-sourced.** Prove the guard: a scratch island edit (one outcome deleted) fails the build gate with the count assertion named; prove the loader: a scratch truncated island degrades to the declared error state in the harness, never a blank view; and record the single-sourcing proof: the runtime's topic and outcome lists in a scratch render come from the island alone (changing a topic name in the island changes every view's rendering, one place, one truth).

- **C.1.1 -** Wire the validator into the build gate (the N31 pipeline's gate list gains the coverage check, recorded as its first registered gate) and run the deleted-outcome scratch fixture through the gate, recording the named failure and the refused build; the corner case is a legitimate count change (a future outcome addition), which must update the recorded expected counts in the same commit, and the gate's error message says so explicitly, turning a failure into an instruction.

- **C.1.2 -** Implement the loader with the cheap runtime invariants (total count, id uniqueness, topic range) and record the truncated-island degradation fixture (the honest error naming #sim-coverage) so N35's serialization audit inherits a proven behavior rather than a promise.

- **C.1.3 -** Append the island, validator, resolution record and loader digests to the ledger, run the extended corpus twice for parity with both digests recorded, and hand the outcome ids as the stable vocabulary to N09 (misconception binding), N26 (mastery keys) and N30 (practice paths), closing the task with the coverage truth frozen and loaded.

**Acceptance Criteria:**

- **AC1 (happy path):** Given data/coverage.json, when the validator runs, then 64 outcomes match the per-topic distribution 9, 10, 11, 11, 10, 8, 5, ids are unique, edges resolve, and a scratch cycle or dangling edge fails with ids named.

- **AC2 (negative or edge case):** Given the anchor resolution script over the frozen masters, when it runs, then all 64 master_anchor values resolve with zero failures bound to the recorded master digests, and a scratch dangling anchor fails by name.

- **AC3 (domain integrity and zero-regression):** Given the build gate and the loader, when a scratch edit deletes an outcome or truncates the island, then the gate refuses the build by assertion name and the runtime degrades to the honest named error, with single-sourcing proven across views.

**Verification and Evidence:** Record the count table, the schema and cycle fixtures, the labeling audit, the 64-of-64 resolution record bound to frozen digests, the dangling-anchor failure, the gate refusal and the degradation fixture. The official-versus-proposed split of the island's content is recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: the island and the planning source drifting apart during authoring. Guard: the generation or cross-check step and the count assertions make drift a gate failure. Rollback: the island is new data; removing it leaves the planning source untouched, but N07, N16, N24, N26 and N30 lose their outcome vocabulary and must re-plan.

**Definition of Done:** A validated, anchor-resolved, honestly labeled 64-outcome coverage island exists as the simulator's single source of teaching truth, embedded under build-time gates with a single-sourced loader, and its stable outcome vocabulary is handed to the consuming tasks.

### N03 - Author the conventions artifact and the conflict registry

**Phase:** Phase I | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N01

**Domain:** Scientific conventions and conflicts

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the predecessor plan's audit (76,047 bytes, 20 T, 10 F and 5 B cards, all NOT STARTED) recorded conflicts C01 through C10 (percentage-basis ambiguity, the milligram, gram and liter density defect, standard versus formal potential mixing, endpoint persistence, the 440 nm flatness, calibration and path assumptions, the unresolved catalase values, and related items); the masters' conventions are real but implicit (lang="lv", inline scripts, JSON islands, @media print, the theme-toggle id, ASCII anchors, localStorage usage varying from zero to sixteen references across masters). No explicit conventions artifact and no unified conflict registry exist.

**Purpose and Rationale:** The conventions artifact makes the scientific rules explicit and machine-checkable: atomic masses and their source, unit conversion tables with conversion classes (offset versus affine where relevant), tolerance classes (absolute versus significant-figure), rounding rules, solution-concentration basis definitions (mass per mass, mass per volume, molar), the meniscus and burette reading conventions, and the redox potential convention (E° versus E°′ with the rule for when each applies); the conflict registry consolidates the twelve verified findings of this roadmap's inspection (V-01 through V-12) with the inherited C01 through C10, each entry carrying its status (resolved by a named task, documented-and-accepted with a reason, or open with an owner), so no scientific ambiguity survives unregistered and every engine, figure and vector cites the same rules.

**Target Artifacts and Touchpoints:** data/conventions.json (the authored artifact, inlined as #sim-conventions); the conflict registry artifact; the conventions validator. Touchpoint in output/simulator.html: the #sim-conventions island consumed by engines (N17, N18), figures (N11-N15) and vectors (N05).

**Out of Scope:** No inventing physics or chemistry beyond the frozen masters (every convention cites its master or a named reference in the masters' own bibliography); no resolving the catalase question by decree (it stays open with its owner); no tolerance values presented as official (they are training policy, PROPOSED, since the programme sets no tolerance rules).

**Main Step A - Author the conventions artifact from the masters.** Author data/conventions.json: the atomic mass table with per-element values cited to the masters' own data, the unit conversion table with conversion classes and exactness declarations (exact conversions like milliliter to liter versus measured quantities like density usage), the tolerance classes (absolute tolerances per quantity type and significant-figure tolerances with their rounding rule, both labeled training policy), the concentration basis definitions with their Latvian names, the titration reading conventions (meniscus, burette, the endpoint versus equivalence point wording rule resolving V-05's ambiguity), and the potential convention resolving V-03, each entry citing the master section or inspection record that grounds it.

**Subtask A.1 - Validate conventions the way the engines will consume them.** Validate the artifact: the schema check (every entry typed, every conversion pair resolvable in both directions or declared one-way, every tolerance class complete with its rounding rule), the citation check (every entry's source resolves into the N01 inventory), and the consistency check that the quantity engines of N17 will need (a conversion chain like milligram per milliliter to gram per liter composes to the declared factor, so composition bugs are impossible later), with the checker's own fixtures proving it fails on a scratch wrong factor.

- **A.1.1 -** Author the artifact with the two-level labeling throughout (master-grounded facts cited; tolerance thresholds and rounding choices marked PROPOSED training policy), and record the validator pass with the entry count per section; the corner case is a convention the masters state differently in different files (exactly the V-class findings), which the artifact resolves by declaring one rule with the dissent recorded in the entry's note field, so the choice is visible and reversible rather than silent.

- **A.1.2 -** Implement the composition check (declared chains compose to declared factors, computed independently in the validator) and record the pass over the chains the engines will traverse (mass, volume, concentration, the density-defect chain of V-04); a scratch wrong factor planted in a scratch copy must fail the check with the chain and both factors named, since this check is the V-04 dimension gate's foundation.

- **A.1.3 -** Implement the citation check against the N01 inventory and record the pass; the corner case is a convention grounded in the programme PDF itself (the official facts: paper format, 180 minutes) versus the masters (the teaching material), and the entry's citation field distinguishes the two source classes explicitly, keeping the official-versus-training split visible at the convention level too.

**Main Step B - Consolidate the conflict registry.** Author the conflict registry: the twelve verified findings (V-01 the verification crash, V-02 the percentage-basis ambiguity, V-03 the potential mixing, V-04 the milligram, gram and liter density defect, V-05 the endpoint persistence, V-06 the 440 nm flatness, V-07 the calibration and path assumptions, V-08 the inherited catalase question, V-09 the divergent localStorage usage across masters, V-10 the id-attribute density of the masters, V-11 the divergent island shapes, V-12 the print-convention differences) plus the inherited C01 through C10, each with evidence (the inspection record or the predecessor audit's citation), status (resolved-by-task, documented-and-accepted, or open with owner) and the resolution text where it applies.

**Subtask B.1 - Validate the registry's completeness and traceability.** Validate the registry: every V and C entry has a status, every resolved entry names a real task id from this roadmap, and every task that claims to resolve a conflict has its registry entry (the bidirectional check that keeps the registry and the roadmap from claiming different histories); the scratch fixtures are a statusless entry (fails by id) and a resolution citing a nonexistent task (fails with the id), since a registry that outlives its evidence chain is just prose.

- **B.1.1 -** Author the registry with the V-01 entry handed over by N01 in N03's recorded format, the inherited C entries restated with their predecessor citations (including C10's catalase question carried open, verbatim), and the new V-09 through V-12 entries documenting the masters' engineering divergences that the single-file build must resolve; record the bidirectional validation pass.

- **B.1.2 -** Implement the resolution bindings (V-04 to N17's dimension gate, V-05 to N15's figure rules, V-06 to N13's figure context, V-07 to N15's calibration labeling, V-09 to N25's store, V-10 and V-11 to N31's assembly policy, V-12 to N34's print mode), and record each binding's entry text; the corner case is a conflict that later tasks re-open (a defect found in Phase VIII): the registry's append rule keeps the full loop, and the append semantics are recorded here so N40's closure inherits a disciplined ledger.

- **B.1.3 -** Record the registry's digest in the ledger with every entry's epistemic label (VERIFIED findings, the inherited C entries labeled as the predecessor plan's audit records), and hand the registry to N40's closure as the authoritative conflict list this roadmap must account for.

**Main Step C - Embed, gate and hand off the conventions.** Embed the conventions island (#sim-conventions) through the build with the same emission rules as N02, wire the validator into the build gate (the composition and citation checks run at every build), and define the consumer contract: the engines (N17, N18), figures (N11 through N15), vectors (N05) and the terminology lint (N10) read conventions only through the island, never a local copy, so the drift class of defect is structurally impossible.

**Subtask C.1 - Prove single-sourcing and honest degradation.** Prove single-sourcing: a scratch change to one convention value changes every consumer's behavior in the recorded fixture set (one change, one truth, everywhere); prove degradation: a truncated scratch island degrades to the honest named error per the loader rules; and record the handoff: the conventions contract goes to N05 (the vectors cite conventions digests), N10 (the unit lint), N11-N15 (figure rules) and N17-N19 (engine rules), each consumer named in the recorded handoff.

- **C.1.1 -** Embed the island and wire the gate, then run the scratch wrong-factor and statusless-entry fixtures through the build pipeline, recording both refusals with their named assertions, and the clean build's island digest.

- **C.1.2 -** Implement the single-sourcing fixture (the scratch value change observed in the engine's conversion output, the figure's tolerance field and the vector's expected value all in one recorded run), and the degradation fixture over a truncated island, recording the honest error naming #sim-conventions.

- **C.1.3 -** Append the artifact, registry, validator and gate digests to the ledger, run the extended corpus twice for parity, and record the byte contribution of the conventions island against the bank sub-budget from Section 1, closing the task with the scientific rulebook explicit, gated and consumed through one door.

**Acceptance Criteria:**

- **AC1 (happy path):** Given data/conventions.json, when the validator runs, then the schema, bidirectional conversions, composition chains and citations all pass, and a planted wrong factor fails the composition check with the chain and factors named.

- **AC2 (negative or edge case):** Given the conflict registry, when the bidirectional check runs, then every V and C entry carries a status with real task bindings (a statusless entry or a phantom-task citation fails by id), and the catalase question stays open verbatim.

- **AC3 (domain integrity and zero-regression):** Given the embedded island under the gate, when conventions change once, then every consumer record changes in the single-sourcing fixture, truncated islands degrade honestly by name, and the corpus parity run passes twice.

**Verification and Evidence:** Record the validator tables, the composition fixture, the citation pass, the registry validation with all statuses and bindings, the gate refusals, the single-sourcing and degradation fixtures, and the corpus parity digests. The PROPOSED versus master-grounded labeling of every convention section is recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: a convention value chosen here later contradicting a master's worked example (the masters are the authority). Guard: the citation check and the N36 conservation recompute; a contradiction surfaces as a property failure with the example named. Rollback: the artifact and registry are new data; removal leaves the masters untouched, but N05, N10 through N19 lose their rulebook and must re-plan.

**Definition of Done:** An explicit, cited, machine-validated conventions artifact and a bidirectionally consistent conflict registry exist, embedded under build gates and consumed through one loader, with every ambiguity from the inspection and the predecessor audit registered, bounded and handed to its resolving tasks.

### N04 - Author the QUESTION_SCHEMA validator and the single loader for eighteen types

**Phase:** Phase I | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N01

**Domain:** Question schema and loading

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the planning layer defines eighteen response types (Q01 through Q18) with a required per-form type set (Q02, Q04, Q10, Q11, Q12, Q13 and Q15); the masters carry question content in divergent island shapes (search-index, exam-bank, thermo-test-vectors, inhib-data, master-data, per the inspection), so no unified schema exists; the blueprint declares the single-file island plan (#sim-bank) but no schema, no validator and no loader exist.

**Purpose and Rationale:** The QUESTION_SCHEMA defines, for each of the eighteen types, the fields (the question's Latvian stem, the response payload shape the N22 input components will capture, the correct-value fields, the tolerance or matching rules, the criterion bindings for grading, the misconception signature slots feeding N09, the outcome binding feeding N02, the difficulty and family metadata feeding N24 and N30), and the validator enforces them at authoring time so the bank of N20 can only ever contain well-formed instances; the loader is the one runtime reader, so the question path is authored once, validated once and read once.

**Target Artifacts and Touchpoints:** data/question_schema.json (the schema artifact); tools/validate_bank.py (the validator); the runtime loader contract for #sim-bank. Touchpoint in output/simulator.html: the #sim-bank island's shape is exactly this schema's output shape.

**Out of Scope:** No authoring of question content in this task (the content is N20's bank); no grading logic here (the engines of N17 through N19 own it, and the schema only names their bindings); no tolerance values in the schema (they come from the conventions island, cited, not duplicated).

**Main Step A - Author the schema for all eighteen types.** Author data/question_schema.json: the shared core (id scheme, family id, variant letter, outcome binding, difficulty band, stem text, feedback text slots, misconception signature list), the per-type payloads (numeric with unit and tolerance class, option-select with the option and distractor slots, ordering with the sequence contract, matching with the pair set, graph with the plot payload shape, method with the step and explanation slots), and the required-type registry (the seven per-form required types recorded as the planning layer's declared constraint), with each type's contract citing the blueprint's declared type list.

**Subtask A.1 - Validate the schema against itself and the plan.** Validate the schema artifact: the self-check (every type's fields typed and non-optional where declared, every payload class defined once and referenced by name, the eighteen types exactly matching the planning list Q01 through Q18 with the required set consistent), and the negative corpus (hand-written scratch instances, one valid per type and a deliberate violation per class: a missing stem, a tolerance class not present in the conventions island, an outcome id not in N02's vocabulary, a family format error), each of which the validator must reject with the field named, since a validator proven only on valid data certifies nothing.

- **A.1.1 -** Author the schema with the eighteen type contracts and record the self-check pass, including the assertion that the type list matches the planning layer's Q01 through Q18 exactly and the required set (Q02, Q04, Q10, Q11, Q12, Q13, Q15) matches verbatim; the corner case is a type whose payload could overlap another's (numeric versus option-select both carrying a string field), resolved by the declared payload-class discriminator field, and the discriminator rule is recorded.

- **A.1.2 -** Author the negative corpus (one violation per error class, hand-written and kept as the validator's permanent regression set) and record the validator's rejections with each field named; the corner case is a violation that is also a schema file error (a malformed schema would make every instance invalid), so the validator checks the schema artifact first and its own schema-error fixture is recorded separately from instance errors.

- **A.1.3 -** Implement the cross-island checks (every outcome binding in N02's vocabulary, every tolerance class in N03's conventions, every misconception signature in N09's registry format once it exists, with a temporary stub binding recorded until N09 lands), and record the pass, so the schema is not self-contained but ecosystem-consistent from its first day.

**Main Step B - Implement the validator and the authoring workflow contract.** Implement tools/validate_bank.py: it reads a bank directory (the N20 authoring format), validates every instance against the schema, emits a structured report (counts per type and family, every violation with file, field and message), and exits nonzero on any violation, so the bank's review workflow (N20) and the build gate can both consume it; the authoring workflow contract is recorded: instances are authored as source files, validated, then frozen into the island by the build, never edited inside the island.

**Subtask B.1 - Prove the validator is the only gate the bank needs.** Prove the validator's completeness with the negative corpus (every class rejected, named) and its honesty with a valid multi-instance scratch bank (passes with its counts recorded); the corner-case fixture is a bank that validates instance-by-instance but violates a global constraint (a duplicate instance id across files), which the validator must reject at the set level, since per-file validation alone would let the classic duplicate-id collision through, and the masters' own id density (V-10) makes collision realism part of the plan.

- **B.1.1 -** Implement the validator with the two-level report (instance level and set level) and record the duplicate-id fixture's named rejection alongside the per-class corpus results, with exit codes recorded; the corner case is a very large bank approaching the real 112 instances, so the validator's runtime is recorded over a scratch full-size set, proving it stays a fast gate rather than a slow ceremony.

- **B.1.2 -** Record the authoring workflow contract (source files, validation, build-time freezing, the island never hand-edited) with the validator as its only gate, and record the contract's digest in the ledger; the corner case is an emergency fix needed in a shipped island, which the contract routes back through source and revalidation rather than island surgery, and the rule is recorded so N20 inherits it.

- **B.1.3 -** Wire the validator into the build gate list (the N31 pipeline's gate set gains the bank validation, recorded) and run a scratch invalid bank through the pipeline, recording the refused build with the first violation named, then the clean scratch bank passing, proving the gate's fail-closed behavior end to end.

**Main Step C - Implement the runtime loader and freeze the contract.** Implement the runtime loader for #sim-bank: it reads the island, asserts the cheap invariants (type count, id uniqueness, family structure), maps instances to their typed payload classes, and hands records to the runtime consumers (the N22 renderers by type, the N17-N19 engines by binding), with corrupted-island degradation defined per the loader rules; the loader and schema digests enter the ledger, and the contract is frozen for N20's authoring.

**Subtask C.1 - Prove the loader and freeze the handoff.** Prove the loader over the scratch full-size bank: every instance loads, types resolve, the required-type registry is asserted present in the eligible subset per the declared rule, and the degradation fixture (a truncated island) fails honestly by name; the handoff record names N20 as the authoring consumer, N22 as the rendering consumer and N24 as the assembly consumer of the same loaded records, one shape for all three.

- **C.1.1 -** Implement the loader with the cheap invariants and the typed mapping, and record the full-size scratch load with its counts; the corner case is an instance type the loader's renderer registry does not know (a type added to the schema without a renderer), which must fail loudly at load with the type named, since a silently unrenderable question discovered mid-exam is the worst-case failure this check exists to prevent.

- **C.1.2 -** Run the degradation fixture and record the honest error naming #sim-bank; then run the required-type assertion over a scratch bank missing one required type, recording the named failure, so the loader enforces the planning layer's declared constraint at runtime rather than trusting the assembly.

- **C.1.3 -** Append the schema, validator and loader digests to the ledger, run the extended corpus twice for parity, and hand the frozen schema contract to N20 (authoring), N22 (rendering), N24 (assembly) and N05 (the vector format shares the payload classes), closing the task with the question pipeline's shape decided once.

**Acceptance Criteria:**

- **AC1 (happy path):** Given data/question_schema.json, when the self-check and negative corpus run, then all eighteen types match the planning list exactly (required set verbatim), and every violation class is rejected with field, file and message named.

- **AC2 (negative or edge case):** Given tools/validate_bank.py, when the duplicate-id and full-size scratch fixtures run, then set-level collisions fail by id, runtime stays recorded and fast, the invalid bank refuses the build, and the clean bank passes with counts.

- **AC3 (domain integrity and zero-regression):** Given the runtime loader, when the full-size bank loads, then types resolve, the required-type assertion holds, unknown types fail loudly at load, and truncated islands degrade honestly by name.

**Verification and Evidence:** Record the self-check, the per-class rejection corpus, the cross-island consistency pass, the duplicate-id and gate fixtures, the full-size load counts and the degradation record. The authoring workflow contract and the frozen schema handoff are recorded verbatim with their digests.

**Risks, Guardrails, and Rollback Plan:** Risk: schema rigidity forcing content authors into wrong shapes (a question that genuinely needs an extra field). Guard: the schema declares an extension slot with its own validation rule, so extensions are typed, not smuggled. Rollback: the schema, validator and loader are additive; removal leaves the masters untouched, but N20 has no authoring gate and N22 and N24 lose their shared shape, so the pipeline re-plans.

**Definition of Done:** A self-checked, ecosystem-consistent QUESTION_SCHEMA for all eighteen types exists with a proven validator as the bank's only authoring gate, a fail-loud runtime loader, and the frozen contract handed to authoring, rendering, assembly and vector tasks.

### N05 - Build the golden vectors and the cross-language seed policy

**Phase:** Phase I | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N04

**Domain:** Test vectors and determinism

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters carry test-vector precedents (C4's thermo-test-vectors island, verified in the inspection) but no unified vector corpus exists; the planning layer requires seeded assembly (N24), reproducible sampling and fair forms; no PRNG policy, no seed vocabulary and no oracle-independent vector corpus exist anywhere in the workspace.

**Purpose and Rationale:** The golden vectors are the grading truth this roadmap can actually verify: for a spread of instances across all eighteen types and all seven topics, the vector records the question's frozen inputs and the expected grading outcome (the verdict class, the awarded criteria, the error class) computed by an oracle independent of the engines that will be tested against it (the oracle uses the conventions island's rules implemented directly, not through the N17-N19 engine code, so agreement between oracle and engine is evidence and not tautology); the seed policy defines the PRNG (a declared integer algorithm with its constants recorded, implemented identically in Python and in the simulator's JavaScript with cross-language test vectors proving bit-identical streams), the seed vocabulary (which decisions take seeds: assembly draws, sample selection, workload generation), and the replay rule (a recorded seed plus a recorded policy equals a reproducible fact).

**Target Artifacts and Touchpoints:** data/golden_vectors.json (the corpus, inlined as #sim-golden-vectors); the oracle script; the PRNG module (Python and JavaScript twins); the seed policy artifact.

**Out of Scope:** No vectors for unimplemented engines written before the engines exist as fixtures of engine bugs (the corpus grows per phase, each addition cited); no crypto-strength claims (the PRNG is for reproducible sampling, not security, stated honestly); no third-party randomness libraries (offline rule, and the twin implementation must be auditable line by line).

**Main Step A - Implement the PRNG twins and prove cross-language determinism.** Implement the PRNG module twice (a declared integer algorithm, for example SplitMix64 with its constants recorded, in Python for the tooling and in JavaScript for the runtime): each exposes the same declared operations (seeded stream, integer draws, bounded draws, shuffle), and the cross-language proof is a recorded set of seed values (at least ten declared seeds) whose first hundred draw values each implementation must reproduce identically, with the values table itself committed as the frozen contract any future refactor must honor.

**Subtask A.1 - Prove the twins agree and fail when they should.** The proof harness runs both implementations over the seed set and compares value-for-value (recorded); the negative fixture is a deliberately perturbed scratch twin (one constant altered) whose divergence the harness must detect and name, since a determinism harness that cannot see a planted divergence is a rubber stamp; the corner case is JavaScript's number handling (floats versus integers, overflow behavior), which the integer-only design avoids by construction, and the avoidance rule is recorded so future contributors do not reintroduce floating-point draws.

- **A.1.1 -** Implement both twins from the recorded constants with the shared operation set, and record the value table for the ten declared seeds (one hundred draws each, digest-compared across languages); the corner case is a negative seed or a zero seed (if the algorithm has degenerate states), which the policy declares illegal and both twins must reject identically, with the rejection recorded as part of the table.

- **A.1.2 -** Implement the determinism harness with the perturbation fixture and record both the green comparison and the named divergence; the corner case is shuffle determinism (the Fisher-Yates order must consume draws in the declared pattern, or the two languages could shuffle differently with the same stream), and the shuffle rule is recorded as part of the operation contract with its own cross-language fixture.

- **A.1.3 -** Author the seed policy artifact (the algorithm id and constants, the seed vocabulary: N24's assembly seeds, N27's sample seeds, N30's workload seeds, all declared with their ranges and their recording rules), and record its digest in the ledger with the value table, making the PRNG a frozen public contract of the whole roadmap.

**Main Step B - Build the oracle and the first vector stratum.** Implement the oracle: a Python script that grades a declared instance against the conventions island's rules directly (its own arithmetic, its own tolerance application, its own error classification implemented from the conventions text, sharing no code with the future engines), and author the first vector stratum: for the types whose semantics are already fixed by the schema (N04) and the conventions (N03), a spread of instances (every topic, every fixed type, at least two instances each, correct, near-tolerance, and wrong cases) with the oracle's verdicts recorded as the expected values.

**Subtask B.1 - Prove the oracle's independence and coverage.** Prove independence structurally (the oracle imports the conventions data but no engine module, recorded in its import manifest) and behaviorally (for one tolerance case, a hand-computed expected value is recorded beside the oracle's output, agreeing, so the oracle itself is spot-checked against human arithmetic); the coverage table records the stratum's spread (types, topics, verdict classes), and the corner cases are the tolerance edges (the exact boundary: the conventions' rounding rule decides the verdict at the edge, and the oracle's edge-case vectors record the rule's application verbatim).

- **B.1.1 -** Implement the oracle with its import manifest recorded (conventions data only, no engine imports possible by construction), and record the hand-computed spot checks (at least three, spanning a numeric, a tolerance-edge and an error-class case) agreeing with the oracle's outputs, so the oracle has its own evidence layer beneath the vectors.

- **B.1.2 -** Author the first stratum with the coverage table (topic by type), ensuring the near-tolerance and boundary cases the inspection's conflict classes demand (the V-04 density-defect chain gets explicit vectors: a value off by the density factor must grade wrong with the dimensional error class named), and record the stratum's digest.

- **B.1.3 -** Run the stratum through the schema validator (N04: every vector's instance half must be a valid instance) and the loader's type resolution, proving the vector corpus and the bank share one shape from the start, and record the pass with the cross-check note.

**Main Step C - Freeze the vector format and the growth protocol.** Freeze the vector format (instance half in N04's schema shape, expected half with verdict class, criteria awarded, error class, the oracle's version and digest, the vector id scheme) and the growth protocol: each later phase (the engines of N17-N19, the assembly of N24) extends the corpus with its stratum, cites this task's oracle rules, and never edits an existing vector (a changed expectation is a new vector with the old one's id retired and the reason recorded), so the corpus is append-only evidence; the corpus inlines as #sim-golden-vectors for the runtime's own smoke subset.

**Subtask C.1 - Prove replayability and close the phase.** Prove replayability: the oracle reruns the frozen stratum twice in fresh processes with identical outputs (digests recorded), and a scratch perturbed convention value must flip exactly the affected vectors' oracle outputs (proving the vectors are alive to the conventions, not frozen guesses), with the perturbation run recorded and then reverted; the phase closes with the ledger holding the PRNG contract, the oracle manifest, the stratum digest and the growth protocol.

- **C.1.1 -** Author the vector format and growth protocol as recorded artifacts, and run the format validation over the stratum (every vector structurally sound, ids stable, no retired ids present), recording the pass; the corner case is a vector whose expected half becomes obsolete (a conventions change altering the true verdict), handled by the append-only rule: a new vector, a retired id, a ledger note, never an edit, and the rule's first application (if any) is recorded as the protocol's precedent.

- **C.1.2 -** Run the twice-fresh-process replay and the perturbation-and-revert proof, recording the three digests (two replays identical, the perturbed run divergent then restored identical), which closes the determinism question for the whole corpus.

- **C.1.3 -** Append the format, protocol, PRNG, oracle and stratum digests to the ledger, run the extended corpus twice for parity, and hand the seed vocabulary to N24, N27 and N30, the vector format to N17-N19 and N36, and the corpus to the smoke subset plan, closing Phase I with the scientific baseline, the rulebook, the shape and the truth all frozen and evidenced.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the PRNG twins, when the ten-seed, hundred-draw table runs in both languages, then values are identical (digest-equal), shuffles match by rule, and a perturbed-constant scratch twin is caught and named.

- **AC2 (negative or edge case):** Given the oracle with its import manifest, when the spot checks and first stratum run, then hand computations agree, coverage spans topics and types with V-04 chain vectors present, and the stratum passes schema validation.

- **AC3 (domain integrity and zero-regression):** Given the append-only corpus, when the replay and perturbation proofs run, then fresh-process digests are identical, a conventions perturbation flips exactly the affected vectors, and the growth protocol hands the frozen contracts to N17-N19, N24, N27, N30 and N36.

**Verification and Evidence:** Record the cross-language value table, the perturbation catch, the shuffle fixtures, the seed policy, the oracle import manifest with spot checks, the coverage table, the replay digests and the perturbation-and-revert run. Epistemic labels: all VERIFIED (2026-11-16) in the recorded environment; the PRNG's non-cryptographic scope is stated verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: a later engine disagreeing with the oracle being resolved by editing the vector (the corruption of evidence). Guard: the append-only protocol and the ledger's retired-id rule make any such edit a visible event; a disagreement is a defect in one of the two implementations, investigated, never painted over. Rollback: the corpus and PRNG are additive; removal leaves the schema and conventions intact, but every seeded task (N24, N27, N30, N36) loses its determinism foundation and must re-plan.

**Definition of Done:** A cross-language-deterministic PRNG contract, an independent oracle with hand-checked evidence, and an append-only golden-vector corpus with a frozen growth protocol exist, giving the roadmap's grading, sampling and test claims a replayable, oracle-independent truth foundation for all later phases.


## 8. Phase II (N06-N10) - Objectives, Concept Maps, Recall Layers, Misconceptions and Terminology

Phase II builds the learner-facing knowledge layer. The start screen, objectives view and design tokens open the artifact honestly with the training-material banner (N06); the concept map and its ASCII anchor graph connect the 64 outcomes with a drawer and focus contract (N07); the recall layers give practice items progressive hints with the exam-mode refusal rule (N08); the misconception registry and its signature taxonomy bind every distractor to a diagnosable error (N09); and the terminology island freezes the Latvian vocabulary and the unit-string grammar (N10). When this phase closes, the simulator can speak, teach and diagnose in the masters' own terms.

### N06 - Build the start screen, objectives view and the design token foundation

**Phase:** Phase II | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N02

**Domain:** Shell, objectives and design system

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters establish the conventions this artifact inherits (lang="lv", a theme toggle with id="theme-toggle", a contents section with id="saturs", responsive patterns and @media print), all recorded in the inspection; the coverage island (N02) holds the seven topics and 64 outcomes with their official-versus-proposed labeling; the blueprint declares the single-file, offline, mobile-first contract. No start screen, no objectives view, no token system and no settings view exist for this simulator.

**Purpose and Rationale:** The start screen is the learner's first honest contact with the simulator: it states what the tool is (a self-study training simulator for the first colloquium's topics), what is official (the seven topics, the paper format, the 180-minute maximum) and what is training policy (the points, forms and timing proposals, labeled as such per the Section 1 split), and it opens the objectives view (the seven topics with their outcomes, read from the coverage island) and the settings view (the theme toggle, the storage opt-in that N25 will wire, and the print entry that N34 will build); the design tokens (the two themes, the type scale, the spacing and the target sizes) are founded here as data so that every later view and the N32 accessibility gates build on one system rather than retrofitting one.

**Target Artifacts and Touchpoints:** The start view, the objectives view, the settings view scaffold, and the token layer's data (fully consumed by N32). Touchpoints in output/simulator.html: the #sakums section (start), the objectives list inside #saturs, the theme toggle (honoring the masters' id="theme-toggle" convention), the settings panel inside #iestatijumi.

**Out of Scope:** No marketing copy or engagement claims; no reproducing any official institution's branding or implying endorsement; no interactive question content here (that begins with the practice paths of N30); no theme implementation beyond the token layer (N32 owns the full responsive and contrast contract).

**Main Step A - Author the honest start and objectives views.** Author the start view: the simulator's name and one-paragraph purpose in Latvian, the official-facts panel (seven topics listed, paper colloquium, 180 minutes, all cited to the programme), the training-policy panel (the 100-point, three-form, 21-slot proposals with their PROPOSED labels per the Section 1 split), the primary navigation into practice, exam and revision, and the honest scope note (a self-study aid, not the official exam, per the AGENTS.md rule); author the objectives view over the coverage island: the seven topics with their outcome counts, each outcome statement rendered from the island's single source, each topic linking to its concept map region (N07) and its practice entry (N30).

**Subtask A.1 - Prove the views read one truth and one labeling.** Prove single-sourcing: the objectives view's counts and statements come from the coverage island alone (a scratch island edit changes the rendering, recorded as N02's rule applied at the view level); prove the labeling: the official and proposed panels' claims are checked against the Section 1 split and the copy lint (no word implying official endorsement or certification anywhere), with the lint pass recorded, since the start screen's honesty is the simulator's first impression of the whole roadmap's discipline.

- **A.1.1 -** Author the start view with its panels and navigation, and record the copy lint pass (the official facts match the programme record; the policy facts carry their labels; the scope note states the AGENTS.md rule in learner-appropriate Latvian), and record the Latvian text's lint through the N10 term bank once it lands, with a stub pass recorded now and the dependency noted.

- **A.1.2 -** Author the objectives view over the island, and record the rendering fixture: 64 outcomes across the seven topics (9, 10, 11, 11, 10, 8, 5), each statement matching the island verbatim, each anchor resolving; the corner case is an outcome whose statement contains markup-significant characters (the escaping discipline of N35 applies from the first view), and the render fixture asserts the statements render as text, not markup.

- **A.1.3 -** Record the two views' ARIA foundations (landmarks, headings, the navigation's names) per the N22 contracts' precursor rules, so the Phase V component work inherits semantic views rather than repairing broken ones, with the semantic check pass recorded.

**Main Step B - Found the design token layer and the theme system.** Author the token layer's data: the two themes (light and dark, honoring the masters' theme-toggle convention), the semantic color pairs (text, surface, boundary, state colors) with their intended use classes (the classes N32's contrast checker will certify), the type scale (rem-based, the 16 px floor declared), the spacing scale, and the interactive target floor (44 px, the mobile-first rule); implement the theme toggle (id="theme-toggle" per the masters' convention, keyboard-operable, persisting its state through the store stub that N25 will finalize, with an in-memory default per the AGENTS.md session rule) and the settings scaffold (the theme control live, the storage opt-in and print entries rendered as declared-but-pending slots for N25 and N34).

**Subtask B.1 - Prove the tokens are data and the themes are complete.** Prove the token discipline: the views authored so far reference only tokens (a raw-value scan over the styles passes, the same scan N32 will gate with), and the theme completeness fixture: both themes carry every semantic token (a scratch theme missing one token must fail the completeness check by name), since a dark theme missing its boundary color is exactly the kind of gap that ships unnoticed and hurts learners at 2 a.m. before the colloquium.

- **B.1.1 -** Author the token data with the use classes declared per pair (text-classed, boundary-classed, state-classed), and record the completeness check over both themes with every token present; the scratch missing-token fixture's named failure is recorded, establishing the check's bite before N32 inherits it as a build gate.

- **B.1.2 -** Implement the theme toggle with its id convention, keyboard operation (the N33 map's precursor) and state persistence through the store stub (the recorded contract: default in-memory per AGENTS.md, the opt-in wiring deferred to N25 and the deferral recorded in the settings scaffold's own copy), and record the toggle's state-machine fixture (toggle, persist, restore, and the no-store degradation path).

- **B.1.3 -** Run the raw-value scan over the styles written so far and record the pass, and record the token layer's digest for N32 to consume as its foundation, so the Phase VII accessibility work builds on this layer instead of replacing it.

**Main Step C - Assemble the shell and prove the structural contract.** Assemble the runtime shell: the nine ASCII anchors (#sakums, #saturs, #prakse, #eksamens, #rezultati, #atskats, #metodika, #druka and #iestatijumi, the declared list from the blueprint) with their sections, the navigation among them, the island script tags in their declared order (the #sim-coverage and #sim-conventions islands from Phase I, with the later islands' slots declared), and the start and objectives views rendered inside; the structural contract (one file, one script, offline, lang="lv") is asserted by the N31 checker's precursor run here, before any grading or practice exists.

**Subtask C.1 - Prove the shell's honesty end to end at this stage.** The Phase II closing proof runs early: the shell loads in the scratch harness, the anchor scan passes (nine anchors, ASCII, unique), the zero-URL scan passes (offline from the first assembly, not retrofitted), the objectives render from the island, and the smoke subset's first vector (the coverage island's counts asserted in-file) passes; recording this proof now establishes the build-then-prove rhythm every later task follows.

- **C.1.1 -** Implement the nine-anchor shell with the navigation's semantic structure, and record the anchor scan (nine, ASCII, unique, matching the blueprint's declared list) plus the zero-URL pass, with the two scans' outputs recorded verbatim as the artifact contract's first green run.

- **C.1.2 -** Implement the first smoke vector (the coverage island's per-topic counts asserted from the loaded runtime island), and record its pass, founding the in-file smoke subset that Phases III through VIII extend vector by vector.

- **C.1.3 -** Append the shell, views, token layer and smoke vector digests to the ledger, run the extended corpus twice for parity, and record the byte accounting against the CSS and template sub-budgets from Section 1 (the shell's own weight matters from the start), closing the task with the simulator's skeleton standing, honest and token-founded.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the start and objectives views, when they render from the coverage island, then all 64 outcomes appear verbatim across the seven topics with correct counts, the official and proposed panels match the Section 1 split, and the copy lint passes.

- **AC2 (negative or edge case):** Given the token layer and both themes, when completeness and raw-value scans run, then every semantic token exists in both themes (a scratch omission fails by name), the toggle works and degrades without a store, and no raw values appear.

- **AC3 (domain integrity and zero-regression):** Given the assembled shell, when the anchor, URL and smoke checks run, then nine ASCII anchors are unique, zero external URLs exist, the first smoke vector passes in-file, and corpus parity holds twice.

**Verification and Evidence:** Record the copy lint, the single-sourcing and rendering fixtures, the ARIA foundation pass, the theme completeness and toggle fixtures, the raw-value scan, the anchor and URL scans, and the first smoke vector pass. The official-versus-proposed panel text and the scope note are recorded verbatim in Latvian.

**Risks, Guardrails, and Rollback Plan:** Risk: the token layer diverging from the masters' own visual language (learners know the masters' look). Guard: the toggle and contents conventions are inherited by design, and the tokens are recorded beside their master precedents. Rollback: the shell and views are additive over the islands; removal leaves Phases I intact, but every later view task loses its skeleton and token foundation and must re-plan.

**Definition of Done:** An honest start screen, a single-sourced objectives view, a complete two-theme token foundation with a working conventional theme toggle, and a nine-anchor structural shell exist, proven offline and smoke-checked from the first assembly, with the design system handed to N32 and the shell handed to every later view task.

### N07 - Build the concept map, the ASCII anchor graph and the concept drawer

**Phase:** Phase II | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N02, N06

**Domain:** Concept structure and navigation

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the coverage island (N02) carries the prerequisite edges among the 64 outcomes; the masters organize content under ASCII anchors (the inspection recorded #stehiometrija, #maisijumi and the saturs convention); the shell with its nine anchors exists (N06). No concept map, no anchor graph and no concept drawer exist for this simulator.

**Purpose and Rationale:** The concept map makes the course's structure visible and navigable: the 64 outcomes and their prerequisite edges render as a browsable graph (a layered layout per topic, prerequisites crossing topics drawn and named), every node links to its concept drawer entry, and the drawer is the study surface: opening a concept from the map (or from any remediation or feedback link, per the N28 contract) shows the concept's summary text (authored from the masters, cited by anchor), its prerequisite chain (clickable), its related figures (N11-N15 slots), its worked chains (N16 slots) and its practice entry (N30 slot); the drawer implements the return-focus rule: closing it restores focus to the invoking control, the accessibility contract that N33 formalizes and every modal in the simulator inherits.

**Target Artifacts and Touchpoints:** The concept map view (inside #saturs), the concept drawer component, and the anchor-link registry. Touchpoints in output/simulator.html: the map region, the drawer overlay, the anchor-link validation in the build.

**Out of Scope:** No force-directed or animated graph layouts (a deterministic, layered, screen-reader-traversable structure is the goal, not a physics demo); no authoring of new scientific summaries beyond what the masters and their anchors support (every summary cites its master anchor); no interactive questions inside the drawer (it is a study surface; practice opens separately).

**Main Step A - Design the map model and the layered layout.** Design the map model: the graph is the coverage island's nodes and edges (nothing new is invented structurally: the map is a rendering of N02's frozen vocabulary), and the layout is deterministic: a layered arrangement computed from the prerequisite edges (outcomes without prerequisites in the first layer, each node's layer one past its deepest prerequisite), with the seven topics as the primary grouping and the cross-topic edges drawn as named connections, so the same graph always renders identically (a property N37's visual matrix will inherit as its baseline).

**Subtask A.1 - Prove the layout is acyclic, layered and deterministic.** Prove the layout's inputs: the island's edge set is acyclic (N02's validator guarantees it; the map re-asserts it at build and fails loudly on a cycle, since the layering algorithm's assumption is exactly acyclicity); prove determinism: the layout function is pure over the island (two runs produce identical geometry, digests recorded), and the corner-case fixture is a diamond dependency (B and C both requiring A, D requiring both), which the layer rule must place correctly, since diamonds are the most common real structure in a chemistry prerequisite graph.

- **A.1.1 -** Implement the layout function with the layer rule and the tie-break (stable id order within a layer, recorded as the rule), and record the determinism digests plus the diamond fixture's placement; the corner case is a wide layer (topic 3's eleven outcomes if they shared a layer) overflowing the viewport, handled by the declared wrap rule per layer with the wrap threshold recorded, so the map stays legible at the 320 px class rather than trusting the desktop render.

- **A.1.2 -** Implement the node and edge rendering with the N06 token layer (no raw values) and the semantic structure (the graph as lists per layer with named node links, traversable without any pointer, per the N33 precursor rules), and record the semantic check: every node reachable by keyboard, every edge's name announced, since a concept map a keyboard user cannot traverse is decoration.

- **A.1.3 -** Validate every map link against the anchor registry (the build-time check that all 64 concepts and their drawer targets resolve), and record the 64-of-64 pass with the negative fixture (a scratch dangling concept link failing by name), inheriting N02's anchor discipline at the navigation layer.

**Main Step B - Build the concept drawer and the return-focus contract.** Build the concept drawer: an overlay panel (the N06 token styling, the N22 precursor semantics: role dialog, labelled by the concept's name), opening from map nodes and from any registered link source, showing the concept's summary (Latvian text authored from the masters, its master_anchor cited and re-validated against the frozen inventory), the prerequisite chain (each entry a link to that concept's drawer, the chain capped at the declared depth with the full chain available on request), the slots for figures, chains and practice (rendered as named pending entries until their phases land, never as dead controls), and the close affordance implementing the return-focus contract.

**Subtask B.1 - Prove the drawer's focus loop and its content honesty.** Prove the focus contract with the fixture: invoke from a map node, focus moves into the drawer, tab cycles the drawer's content, close restores focus to the exact invoking node (the recorded sequence is the N33 smoke vector's foundation); prove content honesty: every drawer summary's master_anchor is re-validated against the frozen masters (the N02 resolution script reused), and the summaries' scientific claims are bound to their anchors, so the drawer never drifts from the masters it cites.

- **B.1.1 -** Implement the drawer's open, focus and close mechanics with the return-focus contract, and record the focus-sequence fixture (invoke, traverse, close, restore, with the exact element ids recorded); the corner case is a drawer opened from a link inside another drawer (a prerequisite chain walk), where closing the inner drawer must restore focus to the chain link in the outer drawer, not to the map, and the nested-restore fixture is recorded, since nested drawers are exactly where naive implementations lose the trail.

- **B.1.2 -** Author the concept summaries from the masters (each summary a short Latvian text with its citation), and record the anchor re-validation over all 64 (the same 64-of-64 resolution as N02, now bound to the summaries' citations), with the wording rule recorded: where two masters word a concept differently (the V-02 and V-03 classes), the summary follows the conventions island's declared rule and names the dissent.

- **B.1.3 -** Implement the slot contract (figures, chains, practice entries as declared pending slots with their owning tasks named), and record the slot validation: a slot without an owning task id fails the authoring check, since a dead slot is a promise the roadmap forgot it made, and the check makes the forgetting impossible.

**Main Step C - Prove the map-drawer loop and record evidence.** Prove the complete loop: a scripted walk (open the map, enter a mid-graph concept, open its deepest prerequisite, walk back, jump to a cross-topic edge's target, close everything) executes with every focus transition, drawer state and link resolution recorded as one trace; the trace is replayed in a fresh process with identical state sequences (digests), founding the deterministic-navigation property that N33 and N37 both build upon.

**Subtask C.1 - Prove the loop's honesty and hand off.** The closing proof is the honesty audit: every link in the map and drawer resolves (build-gated), every summary cites a re-validated anchor, every slot names its owner, and the walk trace proves the whole surface deterministic; the handoff records the drawer's open-link contract (the payload any module may use: concept id plus return context) for N08 (hints link into the drawer), N16 (chains link from it), N28 (remediation) and N29 (revision), one contract for every consumer.

- **C.1.1 -** Implement the walk harness with the recorded trace, run it twice plus a fresh process, and record the identical digests; the corner case is the direct-link entry (a learner arriving at a concept from remediation, not from the map), which the drawer contract supports by design, and the fixture proves the drawer opens correctly with no map state present, since the drawer must never depend on the map having been visited.

- **C.1.2 -** Append the map, drawer and registry digests to the ledger, run the extended corpus twice for parity, and record the map and drawer's byte contributions against the template and figure sub-budgets from Section 1, keeping the structural layer's weight visible.

- **C.1.3 -** Extend the smoke subset with one map-drawer vector (a fixed walk subset asserted in-file), record the pass, and hand the open-link contract to N08, N16, N28 and N29, closing the task with the course's structure navigable, cited and deterministic.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the coverage island's graph, when the map renders, then layers are acyclic and deterministic (diamond placed correctly, wide layers wrapping), every link resolves (64 of 64, scratch dangles fail by name), and keyboard traversal reaches every node and edge.

- **AC2 (negative or edge case):** Given the concept drawer, when the focus fixtures run, then open, traverse, close and restore hold (including the nested-drawer case), summaries re-validate against frozen master anchors, and every slot names its owning task.

- **AC3 (domain integrity and zero-regression):** Given the walk trace, when replayed fresh, then state sequences are digest-identical, the direct-link entry works with no map state, the smoke vector passes, and the open-link contract is handed to all four consumers.

**Verification and Evidence:** Record the layout digests and fixtures, the semantic check, the anchor validations, the focus sequences including nesting, the walk trace with replays, and the smoke pass. The summary wording rule (conventions over dissenting masters, dissent named) is recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: summaries drifting from masters as content evolves. Guard: anchor re-validation is build-gated against frozen digests, so drift is a failed build. Rollback: the map and drawer are additive views over the island; removal leaves N02 intact, but N08, N16, N28 and N29 lose their link target and must re-plan.

**Definition of Done:** A deterministic, acyclic, keyboard-traversable concept map with a fully cited concept drawer exists, its focus loop and nested-restore contract proven, its links build-validated, its trace replayed identically, and its open-link contract handed to every consuming task.

### N08 - Build the recall layers and the hint drawer surfaces

**Phase:** Phase II | **Priority:** P2 | **Risk:** Medium | **Effort:** M | **Dependencies:** N07

**Domain:** Scaffolded recall

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters teach with worked steps and progressive detail (the inspection's chain and layer structures); the predecessor plan approved progressive help as training policy; the concept drawer (N07) provides the link target for conceptual help; the practice-mode help boundary (hints never in exams) is declared by the N21 mode registry contract. No recall layers, no hint drawer and no reveal discipline exist.

**Purpose and Rationale:** Recall layers give practice its teaching structure: every practice item can expose a ladder of help (the first layer a direction cue, the second the relevant concept's drawer link, the third the formula or rule with its conventions citation, the fourth the first step of the solution), each layer opening on explicit learner action (never auto-revealed), each layer's use recorded in the session (not graded, not punished, honestly visible in the practice summary as used-help information); the layers are authored as data bound to concepts and conventions, so the same ladder serves an item regardless of its variant (N20's variant engine inherits the binding rather than duplicating text per instance).

**Target Artifacts and Touchpoints:** data authored per concept family (the layer texts with their citations), the hint drawer component (a drawer sibling of N07's), and the layer contract in the runtime. Touchpoints in output/simulator.html: the practice runner's per-item help control (consumed by N30) and the hint drawer.

**Out of Scope:** No hints in exam mode (the N21 boundary is absolute and re-asserted here); no answer values in any layer (the ladder teaches the path, never the specific instance's answer); no layer text without a citation (every layer cites its concept anchor or convention entry).

**Main Step A - Author the layer model and its data.** Author the layer model: the four declared layers with their semantics (cue, concept link, rule with citation, first step), the binding rule (layers bind to concept families, with item-specific override slots for cases where a family's items genuinely need different cues), the citation requirement (each layer's text carries its concept id from N02 or its conventions entry from N03), and the reveal discipline (one layer at a time, explicit action per layer, the ladder's used-layers recorded in the session event stream); author the layer texts for the concept families the Phase III figures and Phase IV chains will serve, with the first stratum covering the seven topics' core families.

**Subtask A.1 - Validate the layer data against its ecosystem.** Validate the layer data: every binding's concept id resolves in N02's vocabulary, every citation resolves (concept or convention), no layer text contains its family's answer values (the leak check: a scratch layer containing a value present in the family's instances fails by name, reusing the N12 leak-scan approach at the data level), and the per-topic coverage table records which families carry ladders, so a family without a ladder is a visible authoring gap rather than a silent empty control.

- **A.1.1 -** Author the model and the first stratum's texts (Latvian, cited, leak-checked), and record the validation pass with the coverage table (families with ladders per topic); the corner case is a family whose fourth layer would effectively give the answer for its simplest variant (the first step of a one-step task is the answer), handled by the depth rule: the layer ladder for a family declares its honest maximum depth per variant class, and the rule's application is recorded for the offending family.

- **A.1.2 -** Implement the leak check over the authored layers (family answer values sought in layer texts, normalized for units and formatting), and record the clean pass plus the scratch planted-leak failure named, since a hint ladder that leaks answers trains dependence, not recall.

- **A.1.3 -** Run the copy lint (term-keyed vocabulary per N10's precursor rules) over every layer text and record the pass with the linted string count, with the terminology dependency noted for N10's island to finalize the keys, so the hint layers cannot drift from the frozen vocabulary once the term island lands.

**Main Step B - Build the hint drawer and wire the practice help control.** Build the hint drawer: a drawer component (N07's return-focus contract inherited, so closing restores the practice control), rendering the ladder one layer at a time (each layer's reveal an explicit button, the revealed layers staying open for study), linking to the concept drawer where the layer's citation points, and recording the used-layers in the session events; wire the practice help control (the per-item button in the practice surface, disabled in exam mode by the mode registry check, re-asserting the N21 boundary at the component level: the drawer's open function refuses an exam-mode context with a stable error id, recorded).

**Subtask B.1 - Prove the boundary and the recording semantics.** Prove the boundary: the fixture set opens the drawer in practice mode (opens, ladders reveal, events record) and attempts the same in a scratch exam-mode context (refused, stable error id, zero layers revealed, zero events recorded), since the practice-versus-exam help boundary is one of the roadmap's declared integrity rules and this component is its enforcement point; prove the recording: three reveals produce three ordered events with layer numbers, and the practice summary fixture shows used-help as information, never as a penalty.

- **B.1.1 -** Implement the drawer with the inherited focus contract and the one-at-a-time ladder, and record the focus fixture (control to drawer, ladder, close, restore) plus the mode-refusal fixture with the stable error id, both recorded verbatim, since N21's later mode registry will re-consume this exact contract.

- **B.1.2 -** Implement the event recording (used-layer events in the session stream, per N25's event schema precursor) and record the three-reveal fixture and the summary fixture (used-help rendered as honest information); the corner case is a drawer reopened after layers were used: the used record persists in the session while the drawer re-renders from the first unrevealed layer, and the reopen fixture is recorded.

- **B.1.3 -** Implement the concept-link handoff (the layer's citation opening the N07 drawer with the return context pointing back to the hint drawer), and record the nested-handoff fixture (hint drawer, concept drawer, back to hint drawer, focus intact at every step), the deepest focus chain the drawer system must hold.

**Main Step C - Prove the ladder's teaching integrity and record evidence.** Prove the ladder's integrity end to end: for the authored stratum, the fixture walk (a practice item with all four layers revealed) shows a monotonically increasing specificity (cue, concept, rule, first step) with zero answer leakage (the leak scan re-run over the rendered drawer output, not just the data), zero grading effect (the verdict path unchanged by layer use, recorded as the grading-neutrality fixture), and the honest summary (the used-layers visible); the smoke subset gains one ladder vector.

**Subtask C.1 - Prove grading neutrality and close the task.** The capstone property is grading neutrality: help use never touches the verdict (the same answer grades identically with and without layers used, the fixture's two runs digest-compared on the graded record, which differs only in the event stream), so learners trust the help enough to use it and the assessment stays honest enough to mean something; the handoff records the layer contract for N20 (variant binding), N30 (the practice help control) and N21 (the mode refusal contract).

- **C.1.1 -** Implement the rendered-output leak scan (the drawer's rendered text re-checked against the family's answer values) and record the clean pass; the corner case is a layer whose formula text, rendered with units, could format-match an instance's answer for degenerate parameter choices (a formula's symbols coinciding with a specific numeric answer), handled by the normalization rules recorded in the scan's implementation and the edge case fixture.

- **C.1.2 -** Run the grading-neutrality fixture (two runs, identical graded records, event streams differing exactly by the used-layer events) and record the digest comparison, closing the help-does-not-corrupt-assessment question with evidence rather than assurance.

- **C.1.3 -** Append the layer data, drawer and scan digests to the ledger, run the extended corpus twice for parity, record the byte contributions against the bank sub-budget (the layer texts are content weight), and extend the smoke subset with the ladder vector, closing the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the authored layer data, when validation runs, then bindings and citations resolve, the leak scan passes on data and rendered output (a planted leak fails by name), and the per-topic coverage table is recorded with honest gaps.

- **AC2 (negative or edge case):** Given the hint drawer fixtures, when practice and exam contexts run, then layers reveal and record in practice while exam contexts refuse with a stable error id, focus restores at every step including nested handoffs, and summaries show used-help honestly.

- **AC3 (domain integrity and zero-regression):** Given the grading-neutrality fixture, when identical answers grade with and without help, then graded records are digest-identical (events differ exactly by layer use), and the smoke ladder vector passes in-file.

**Verification and Evidence:** Record the validation tables, the leak scans at both levels, the boundary refusal, the focus sequences, the reopen fixture, the neutrality digests and the smoke pass. The four-layer semantics and the depth rule's application are recorded verbatim with the honest-gap coverage table.

**Risks, Guardrails, and Rollback Plan:** Risk: layers aging into answer-adjacent text as the bank grows. Guard: the leak scan is a permanent build-time check over data and rendered output, so each bank extension re-proves the ladder. Rollback: the layers and drawer are additive; removal leaves practice functional but help-less, and N30's runner and N21's registry lose the help contract and must re-plan.

**Definition of Done:** A cited, leak-checked, grading-neutral recall ladder with a focus-disciplined hint drawer exists, its exam-mode refusal contractual, its event recording honest, and its variant-binding contract handed to the variant engine, practice runner and mode registry.

### N09 - Build the misconception registry and the distractor signature taxonomy

**Phase:** Phase II | **Priority:** P1 | **Risk:** Medium | **Effort:** L | **Dependencies:** N02, N03

**Domain:** Misconceptions and feedback

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the predecessor plan's audit recorded misconception classes among its conflicts (the percentage-basis, unit-chain and potential-confusion classes, C01 through C10 with V-02, V-03, V-04 as this roadmap's consolidations); the conventions island (N03) declares the rules those misconceptions violate; the schema (N04) reserves misconception signature slots on every instance. No registry, no signature taxonomy and no feedback text system exist.

**Purpose and Rationale:** The registry turns wrong answers into teaching: every distractor (an option-select choice, a numeric trap, an ordering error) maps to a misconception signature (a stable id for the specific wrong model of the world, like percentage-basis confusion or the milligram-gram-liter chain error), and every signature carries its Latvian feedback text (why the answer is wrong, which rule it violates with the conventions citation, and the concept drawer link for re-study), so grading (N23) can classify an error to its signature and feedback (N23's records) can name the learner's actual confusion rather than saying the answer is simply incorrect; the taxonomy is authored from the masters' own error discussions and the conflict classes, with the seven topics' canonical misconceptions enumerated and their incidence honestly labeled as training observations.

**Target Artifacts and Touchpoints:** data/misconceptions.json (the registry: signatures, feedback texts, citations); the signature taxonomy document; the validator. Touchpoints in output/simulator.html: the #sim-bank instances' signature slots, the grading feedback of N23, the remediation queue of N28.

**Out of Scope:** No psychoanalytic labels or learner-facing diagnosis beyond the specific misconception (the feedback names the error model, never the learner); no incidence claims beyond PROPOSED training observations (no official statistics exist); no feedback text without a conventions or concept citation.

**Main Step A - Author the signature taxonomy from the conflict classes.** Author the signature taxonomy: the classes (unit-chain errors including the V-04 density defect, basis errors including the V-02 percentage confusion, convention violations including the V-03 potential mixing, ordering and logic errors, tolerance and rounding errors, and the topic-specific models like the V-05 endpoint confusion and V-06 wavelength flatness), each class's signatures with stable ids, and the per-topic enumeration (the canonical misconceptions the masters themselves discuss, cited per signature); the taxonomy document records the mapping from the inherited C-class conflicts to signatures, so the predecessor plan's findings live on as teachable structure.

**Subtask A.1 - Validate the taxonomy's coverage and bindings.** Validate the taxonomy: every signature's class exists, every signature carries a feedback text and citation (conventions entry or concept id), the feedback texts pass the copy lint, and the coverage table records signatures per topic; the corner-case fixture is a signature without feedback (fails by id), and the honest-gap rule applies: a topic area without authored signatures is a recorded gap, never a silent pass, since a blank registry would make error classification a no-op exactly where it matters most.

- **A.1.1 -** Author the taxonomy with the class structure and per-topic signatures (each signature's wrong-model statement in one Latvian sentence, the correct model's citation, the master or conflict citation), and record the validation pass with the coverage table; the corner case is a wrong answer that could stem from two signatures (a value wrong both by basis and by rounding), handled by the multi-signature rule: an instance's distractor may bind multiple signatures and the feedback presents them in the declared order, and the rule is recorded for N23's classifier.

- **A.1.2 -** Implement the registry validator with the citation check (conventions entry ids and concept ids resolve against N03 and N02) and record the pass; a scratch signature citing a nonexistent convention entry fails by name, keeping the registry ecosystem-consistent like every other island.

- **A.1.3 -** Run the copy lint over all feedback texts (the term-keyed vocabulary, the no-blame rule: no text addresses the learner as wrong-headed, every text addresses the error model), and record the pass with the rule text verbatim.

**Main Step B - Bind signatures to distractors and validate the bank path.** Bind the signatures to the schema's slots: the option-select distractors, the numeric trap values and the ordering error patterns each carry their signature ids (authored as part of the bank's later instances, with the binding contract frozen here), and the validator's bank-side check (extending N04) asserts every distractor carries at least one signature and every signature exists in the registry; the numeric trap bindings follow the declared trap rules (the classic wrong-unit multiple, the basis-swapped value, the off-by-ten chain error), each rule cited to its conflict class.

**Subtask B.1 - Prove the binding is total where it matters.** Prove totality on the contract that matters: a practice or exam distractor without a signature is a build failure (the bank validator rejects it by field), since an unclassified wrong answer teaches nothing and the roadmap's whole feedback chain (N23, N28) depends on classification; the scratch unbound-distractor fixture's named rejection is recorded, and the exception rule is declared honestly: free-response numeric errors outside the authored trap set classify to the generic signatures (the declared fallback class with honest feedback that names the violated rule when determinable and the study path always), never to a silent default.

- **B.1.1 -** Freeze the binding contract (distractor fields, signature slots, the multi-signature order rule, the trap-value rules with their conflict citations), and record its digest for N20's authoring; the corner case is a variant family whose distractors differ per variant (the trap values scale with the parameters), handled by the binding being per-variant in authored data, and the scaling rule is recorded so the variant engine authors signatures per variant, not once per family.

- **B.1.2 -** Extend the N04 validator with the signature checks (registry existence, at-least-one per distractor, the fallback class reserved), and record the corpus of scratch fixtures (unbound distractor, unknown signature, fallback misuse) each failing by name, plus the valid scratch instance passing.

- **B.1.3 -** Run the coverage cross-check (every class and conflict from the taxonomy has at least one authored signature somewhere in the registry, and the V-02, V-03, V-04, V-05 and V-06 findings each have their signatures), and record the cross-check table binding the conflict registry's entries to their teachable signatures, closing the loop between N03's registry and this task's taxonomy.

**Main Step C - Prove the feedback chain and record evidence.** Prove the feedback chain end to end at the data level: for a scratch set of bound distractors across the classes, the chain (distractor chosen, signature resolved, feedback text rendered with its citation and concept link, the link resolving into N07's drawer contract) executes with every step recorded, and the replay run produces identical chains (digests), so N23's later grading and N28's remediation inherit a proven, deterministic classification pipeline rather than a promise.

**Subtask C.1 - Prove the chain is honest and close the task.** The honesty audit: every rendered feedback names the violated rule with its citation (the fixture asserts the citation's presence in the rendered text), no feedback blames the learner (the copy lint re-run over rendered output), and the fallback class's behavior is demonstrated (an unbound numeric error classifying to the generic signature with its honest study path, recorded as the designed degradation); the handoff records the signature vocabulary for N17 (the error taxonomy's classes), N23 (the classifier) and N28 (the queue's signature slots).

- **C.1.1 -** Implement the chain harness (bind, resolve, render, link-check) over the scratch distractor set and record the chain trace with the replay digests; the corner case is the multi-signature distractor (two confusions presented), where the rendered feedback presents both signatures in the declared order with both citations, and the fixture records the ordered output verbatim.

- **C.1.2 -** Run the honesty audit over the rendered outputs (citation presence, no-blame lint, the fallback demonstration) and record the audit table; the corner case is a feedback text whose citation refers to a convention whose wording changed (a live consistency question), handled by the build-time citation re-validation N03 established, and the audit notes the mechanism rather than duplicating text.

- **C.1.3 -** Append the registry, taxonomy, validator extension and harness digests to the ledger, run the extended corpus twice for parity, record the registry's byte contribution against the bank sub-budget, and extend the smoke subset with one signature vector, closing the task with wrong answers made teachable and the vocabulary handed to the engines.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the signature taxonomy, when validation runs, then classes, citations and feedback texts all resolve (a signatureless or uncited entry fails by id), the coverage table records per-topic signatures with honest gaps, and the copy lint passes.

- **AC2 (negative or edge case):** Given the binding contract and validator extension, when scratch fixtures run, then unbound distractors, unknown signatures and fallback misuse fail by name, the V-02 through V-06 findings each map to signatures, and variants bind per variant.

- **AC3 (domain integrity and zero-regression):** Given the chain harness, when the scratch set runs and replays, then chains are digest-identical, multi-signature feedback presents in declared order with citations, the fallback degrades honestly, and the smoke vector passes.

**Verification and Evidence:** Record the taxonomy validation, the binding contract digest, the validator corpus, the conflict-to-signature cross-check, the chain traces with replays and the honesty audit. The multi-signature rule, the no-blame rule and the fallback semantics are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: signature proliferation as the bank grows (hundreds of near-duplicate signatures diluting the taxonomy). Guard: the class structure and the validator's class existence check force consolidation, and a near-duplicate review is part of N20's authoring workflow. Rollback: the registry is additive data; removal leaves grading functional but feedback generic, and N23 and N28 lose their classification vocabulary and must re-plan.

**Definition of Done:** A validated, cited, no-blame misconception registry with a class taxonomy bound to the inherited conflicts, a total distractor binding contract, deterministic feedback chains and honest fallback semantics exists, with its vocabulary handed to the engines, the grader and the remediation queue.

### N10 - Build the terminology island and the unit-string lint

**Phase:** Phase II | **Priority:** P2 | **Risk:** Medium | **Effort:** M | **Dependencies:** N03, N02

**Domain:** Terminology and units

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters are written in Latvian with discipline in unit usage (the inspection's unit and term conventions), but terminology lives implicitly in prose; the conventions island (N03) declares unit rules; no term island, no Latvian-IUPAC name table and no unit-string lint exist; every task so far has recorded a stub dependency on this task's lint (N06, N08, N09 all cited it).

**Purpose and Rationale:** The terminology island (#sim-terms) is the simulator's vocabulary: the Latvian term table (each term its key, its Latvian text, its abbreviation, its unit string where applicable, its concept binding), the IUPAC-versus-traditional name pairs the chemistry requires (with the display rule: the masters' Latvian usage wins, the IUPAC name available on request), the unit-string grammar (the declared format for composed units like g/mol and mg/mL, with the multiplication and division conventions), and the term-key discipline: every runtime string that names a thing comes from the island, so a term change is one edit, and the unit-string lint checks every authored unit string against the grammar (catching the classic mg/mL versus mL/mg transcription flips that unit-chain errors feed on).

**Target Artifacts and Touchpoints:** data/terms.json (inlined as #sim-terms); the unit-string grammar and lint; the runtime term lookup. Touchpoints in output/simulator.html: every view's labels, the figures' axis labels (N11-N15), the feedback texts (N09, N23), the settings and navigation copy.

**Out of Scope:** No dialect invention (the masters' own Latvian usage is the authority, cited per term); no runtime language switching (the artifact is Latvian, lang="lv", per the deliverable contract); no etymological content (the island is a working vocabulary, not a dictionary).

**Main Step A - Author the term island and the unit grammar.** Author data/terms.json: the core vocabulary (the seven topics' key terms, the quantity names, the instrument names like burette and meniscus with their Latvian forms, the interface vocabulary for navigation, states and feedback), each entry with its key, Latvian text, abbreviation slot, unit slot where the term is a quantity, and concept binding where applicable; author the unit grammar: the declared composed-unit format (numerator and denominator element lists, the element vocabulary from the conventions island's units, the separator conventions), so both authored text and rendered labels share one checkable grammar.

**Subtask A.1 - Validate the island against its ecosystem.** Validate: every concept binding resolves in N02, every unit string in the island parses under the grammar, every unit element exists in the conventions island's unit table (no orphan units), and the coverage check confirms the interface vocabulary the prior tasks stubbed (N06's panels, N08's layer texts, N09's feedback) is now fully resolvable, converting the recorded stub dependencies into a measured closure.

- **A.1.1 -** Author the island with the masters' usage cited per contested term (where the masters vary, the conventions-style rule is declared with the dissent named, mirroring N03's discipline), and record the validation pass with the entry counts per class (terms, quantities, instruments, interface).

- **A.1.2 -** Author the unit grammar with its parser (unit strings in, structured composition out) and record the grammar fixtures: valid compositions parse, and the scratch invalid forms (unknown element, malformed separator, the flipped mg/mL transcription written as mL/mg in a wrong context) fail by string, since the lint's whole value is catching exactly these slips in authored data.

- **A.1.3 -** Run the stub-closure check (the three recorded stub dependencies from N06, N08 and N09 now resolve their term keys against the island), and record the closure table; the corner case is a term key used by a prior task but absent here (a missed authoring entry), which the closure check lists by key and task, so the gap is fixed here rather than surviving into the runtime as an unresolved-key error.

**Main Step B - Implement the lint and the runtime lookup.** Implement the unit-string lint as a build gate: every authored data file's unit-bearing fields are checked against the grammar (and, for quantity terms, against the conventions island's dimension rules, so a density term cannot carry a mol/L unit string), and every runtime term-keyed string source (the views' labels, the feedback texts, the layer texts) is checked for key existence; implement the runtime lookup: one function resolving keys to the island's texts, with the missing-key behavior defined per the honest-degradation rules (a named error, never a silently empty label, since an empty label is an accessibility failure too).

**Subtask B.1 - Prove the lint bites and the lookup is single-sourced.** Prove the lint with the planted-failure corpus (a scratch data file with one invalid unit string, one unknown term key, one dimension-mismatched quantity unit: each fails the gate by name), and prove the lookup's single-sourcing: a scratch term edit changes every consuming view's rendered text in one recorded pass (the N02 rule applied to vocabulary), with the degradation fixture (a truncated island) producing the named error rather than empty labels.

- **B.1.1 -** Implement the lint over the authored data set and run the planted corpus, recording each named failure and then the clean pass; the corner case is a unit string inside free-text prose (a feedback sentence quoting a unit), which the lint's field-level scoping exempts by design, and the exemption rule is recorded so the lint's silence on prose is a declared scope, not a hole.

- **B.1.2 -** Implement the runtime lookup with the missing-key named error and the truncation degradation fixture, and record both; the corner case is the IUPAC alternate name path (the on-request display), which resolves through its own key class and its rendering rule (the masters' form primary, the IUPAC form secondary), and the fixture records the pair rendering.

- **B.1.3 -** Wire the lint into the build gate list (the N31 pipeline's gates gain the terminology check, recorded) and run a scratch failing data set through the pipeline, recording the refused build with the first failure named, then the clean build passing with the island's digest.

**Main Step C - Prove the vocabulary's consistency and record evidence.** Prove consistency across the whole authored surface so far: the full-document term scan (every rendered string in the scratch harness's render set resolves its keys; every unit-bearing rendered label parses under the grammar) passes, and the consistency table records the counts (terms, unit strings, resolved keys) with the stub-closure results, so the vocabulary the simulator speaks is measured, complete and latched; the smoke subset gains one term vector (a fixed lookup set asserted in-file).

**Subtask C.1 - Prove the figures' label path and close the phase.** The capstone handoff is the figure-label contract: the Phase III figures (N11 through N15) consume the island for every axis label, legend entry and annotation, so the island's grammar and lookup are proven against a scratch figure label set here (parse, resolve, render, degrade), and the recorded contract means the figure tasks inherit vocabulary discipline for free; the ledger records the island, grammar, lint and lookup digests, and Phase II closes with the learner-facing layer (views, structure, help, feedback, vocabulary) complete and evidenced.

- **C.1.1 -** Run the full-document term scan over the render set and record the counts with the clean pass; the corner case is a term key whose Latvian text itself contains a unit string (a quantity term like density whose name mentions units), which the scan must check through the grammar too, and the nested-check rule is recorded.

- **C.1.2 -** Run the scratch figure-label proof (parse, resolve, render, degrade over a representative label set: an axis, a legend entry, an annotation) and record the pass, freezing the label contract for N11-N15.

- **C.1.3 -** Append the island, grammar, lint and lookup digests to the ledger, run the extended corpus twice for parity, record the island's byte contribution against the bank sub-budget, extend the smoke subset with the term vector, and record the phase-closure note handing the complete learner-facing foundation to Phase III's figures and Phase IV's engines.

**Acceptance Criteria:**

- **AC1 (happy path):** Given data/terms.json and the unit grammar, when validation runs, then bindings and unit elements resolve, compositions parse with invalid forms failing by string, and the three stub dependencies close with any missing keys listed by task.

- **AC2 (negative or edge case):** Given the lint and lookup under the build gate, when the planted corpus and scratch pipeline run, then invalid units, unknown keys and dimension mismatches fail by name, single-sourcing is proven, and truncated islands degrade with named errors.

- **AC3 (domain integrity and zero-regression):** Given the full-document scan and figure-label proof, when they run over the render set, then every key resolves and every unit string parses (including nested cases), the smoke vector passes, and the label contract is frozen for Phase III.

**Verification and Evidence:** Record the validation tables, the grammar fixtures, the stub-closure table, the planted-corpus failures, the gate refusal, the single-sourcing pass, the degradation record, the full-document scan counts and the figure-label proof. The masters'-usage rule, the prose-exemption scope and the IUPAC pair rule are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: vocabulary drift between the island and the masters' own newest wording. Guard: the island cites per term and the N01 freeze makes master changes visible digest events. Rollback: the island and lint are additive; removal leaves the prior tasks' stubbed passes unbacked and the runtime's strings unlatched, so N11-N15, N23 and the views re-plan their vocabulary sources.

**Definition of Done:** A complete, cited, grammar-checked terminology island with a build-gated unit-string lint, a single-sourced runtime lookup with honest degradation, closed stub dependencies and a frozen figure-label contract exists, completing Phase II's learner-facing foundation.


## 9. Phase III (N11-N15) - Inline SVG Figure Tasks for the Master Simulator File

Phase III builds every teaching figure the colloquium's topics require, entirely as inline SVG generated from data records: the framework and the topic 1-2 records with tolerance coupling (N11), the burette and dilution figures with the general leak-scan engine (N12), the energy, Hess and Maxwell-Boltzmann figures (N13), the kinetics linearization figures with the tolerance fields the graph scoring will consume (N14), and the titration curves and calibration plots with the formal no-extrapolation rule (N15). Every figure is generated, not hand-drawn; every value derives from the conventions island or recomputes; every conflict the figures touch (V-04, V-05, V-06, V-07, V-08) is enforced in the figure copy. When this phase closes, the visual language of the simulator is complete and evidence-bearing.

### N11 - Build the inline SVG figure framework and the T1-2 records with tolerance coupling

**Phase:** Phase III | **Priority:** P1 | **Risk:** Medium | **Effort:** L | **Dependencies:** N04, N10

**Domain:** Figure framework and topic 1-2 figures

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters render their own inline SVG (the inspection's figure conventions), the deliverable contract forbids external assets (the zero-URL rule, verified against the masters' offline pattern), the schema (N04) declares the graph-type payload class, the conventions island (N03) declares tolerance classes, and the term island (N10) freezes the figure-label contract with its proven lookup and grammar. No figure framework, no figure data format and no topic figures exist for this simulator.

**Purpose and Rationale:** The figure framework is the one machinery every figure task builds on: a data-driven SVG generator (figures are authored as data records and rendered as inline SVG, never hand-drawn markup, so a figure is diffable, testable and reproducible), the figure contract (each record declares its type, its data series, its axes with term-keyed labels through the N10 contract, its annotations, its tolerance coupling fields where the figure teaches a measured quantity, and its lazy-render slot so dozens of figures do not all parse at load), and the first figures: the topic 1-2 records (stoichiometry and mixture-composition diagrams: composition bars and mass-chain diagrams for stoichiometric proportion), each carrying the tolerance fields that N18's graph scoring will consume for figures that represent gradeable plots.

**Target Artifacts and Touchpoints:** The figure framework module; data/figures_t12.json; the figure renderer contract. Touchpoints in output/simulator.html: the concept drawer's figure slots (N07), the worked chains' figures (N16), and the practice items' figure payloads.

**Out of Scope:** No raster images or external assets (inline SVG only, offline by construction); no animation (static, printable, screen-reader-describable figures are the goal); no figure data computed at runtime beyond declared transforms (values are authored or derived from the conventions island deterministically).

**Main Step A - Define the figure record format and the renderer.** Define the figure record format: the type registry (bar, chain, curve, scatter, band and schema-coupled plot types), the shared fields (id, type, title key, axis records with term keys and unit strings under the N10 grammar, series data, annotation records with their citation slots), the tolerance coupling fields (where a figure's plotted quantity carries a tolerance class, the record names the conventions entry so N18's scoring and the figure's own rendering can never disagree about what near the line means), and the accessibility fields (a description text per figure, authored Latvian, since an SVG a screen reader cannot describe is a picture, not a teaching figure); implement the renderer as a pure function over records (record in, SVG text out, deterministic).

**Subtask A.1 - Validate the format and prove renderer determinism.** Validate the format: every record type exists in the registry, every term key resolves, every unit string parses (the N10 lint extended to figure data), every tolerance coupling resolves to a conventions entry; prove the renderer: two runs over the same record produce identical SVG bytes (digests recorded), and the malformed-record corpus (an unknown type, an unresolved term key, a unit grammar failure) fails validation by name, so the framework fails closed before any figure task ships content.

- **A.1.1 -** Author the format specification with the type registry and field tables, and record the validation fixtures: the malformed corpus (one failure per class, each named) and a valid scratch record passing, establishing the framework's gate before any real figure depends on it.

- **A.1.2 -** Implement the renderer as a pure function with the token-layer styling (no raw colors: figures consume the N06 token classes so themes and print mode recolor figures automatically), and record the determinism digests plus the theme-parity fixture (the same record rendering under both theme classes with both outputs recorded, since a figure that ignores the theme would break the dark mode the masters' own toggle promises).

- **A.1.3 -** Implement the accessibility description fields and record the description presence check (every type requires a description, a scratch record without one fails by id), with the descriptions' copy lint pass recorded, so the figure framework carries screen-reader support from its first record rather than as a retrofit.

**Main Step B - Author the T1-2 records and prove their scientific grounding.** Author the topic 1-2 figure records: the mixture-composition figures (composition bars showing mass and volume fraction relationships, with the percentage-basis discipline of V-02 applied: each figure's basis labeled explicitly, never an unlabeled percent), and the stoichiometry mass-chain figures (the conservation visual the masters teach, with values derived from the conventions island's atomic masses and the derivation recorded per record); every record cites its master anchor (the N02 discipline) and its conventions entries, so the figures are as traceable as every other artifact in the roadmap.

**Subtask B.1 - Prove the values derive from the conventions island.** Prove the grounding: for each derived value in the records, an independent recompute (the N36-style second opinion, applied here at authoring time) reproduces the value from the conventions island, and the recompute table is recorded; the corner case is a rounding boundary in a bar figure (a fraction that rounds to a visually misleading equality, like two bars that look identical after rounding), handled by the declared significant-figure rule with the display note, and the boundary record is authored deliberately so the figure teaches honestly at the edge.

- **B.1.1 -** Author the T1-2 records (the composition set and the mass-chain set), and record the anchor and conventions citation validation (every record resolves both), plus the recompute table over every derived value with its agreement recorded.

- **B.1.2 -** Run the N10 label contract over the records' rendered labels (axis labels, legends, annotations: parse, resolve, render) and record the pass, converting N10's frozen contract into the figure framework's first real consumers.

- **B.1.3 -** Implement the tolerance coupling for the records that teach measured quantities (the records name their conventions tolerance entries), and record the coupling validation; the corner case is a record with no measured quantity (a purely structural diagram), where the coupling field is optional by declared rule, and the optionality rule is recorded so N14 and N15's gradeable figures know when the coupling is mandatory.

**Main Step C - Prove the render pipeline and record evidence.** Prove the full pipeline: the records validate, render deterministically (two-run digests), load lazily (the lazy-render fixture: an off-screen figure's SVG is not parsed until its drawer or item opens it, with the load event recorded, keeping the artifact's parse budget inside the N31 size and performance plans), degrade honestly (a truncated figure island produces the named error, never a half-drawn SVG), and appear in the concept drawer's slots (the N07 slot contract fulfilled for the topic 1-2 concepts, recorded as the first slot closure).

**Subtask C.1 - Prove print readiness and close the task.** The capstone proof is print readiness: the figures render under the print theme class (the N34 contract's precursor: black on white, no clipped geometry, the declared figure print sizes honored), with the print render recorded for one representative record, since the masters' own @media print convention is part of the deliverable's inheritance and the figures must survive it; the handoff records the framework contract for N12 through N15 and the slot closure for N07 and N16.

- **C.1.1 -** Implement the lazy-render mechanism (figures render on first viewport or drawer entry, with the render events recorded) and run the fixture proving the parse-time cost stays inside the declared budget with the off-screen record's SVG absent until opened, since the figure library's whole weight must not land on load.

- **C.1.2 -** Run the truncation degradation fixture (the named error for the figure island) and the two-run determinism proof over the full T1-2 set, recording all digests; the corner case is a figure opened while the island is corrupt (the drawer must show the honest error inside the slot, not a broken drawer), and the fixture records the slot-level degradation.

- **C.1.3 -** Run the print-theme render for a representative record and record it; then append the framework, records, recompute table and lint digests to the ledger, run the extended corpus twice for parity, record the figures' byte contribution against the figure sub-budget (60-140 KiB declared in Section 1, the T1-2 set's share measured), and extend the smoke subset with one figure vector (a fixed record's rendered digest asserted in-file).

**Acceptance Criteria:**

- **AC1 (happy path):** Given the figure record format, when validation runs, then the malformed corpus fails per class by name, valid records pass, rendered labels resolve through the N10 contract, and descriptions are mandatory.

- **AC2 (negative or edge case):** Given the T1-2 records, when grounding checks run, then every anchor and conventions citation resolves, derived values recompute exactly (the rounding boundary handled by the declared rule), and tolerance couplings resolve with the optionality rule recorded.

- **AC3 (domain integrity and zero-regression):** Given the render pipeline, when laziness, degradation, determinism and print proofs run, then off-screen figures stay unparsed, truncated islands fail by name, two-run digests match, print renders honor the theme class, and the smoke vector passes.

**Verification and Evidence:** Record the format fixtures, the renderer digests and theme parity, the citation and recompute tables, the label contract pass, the lazy and degradation fixtures, the print render and the smoke pass. The figure sub-budget accounting for the T1-2 set is recorded against the Section 1 declaration.

**Risks, Guardrails, and Rollback Plan:** Risk: the framework's contract drifting as four more figure tasks extend it. Guard: the type registry and validation are build-gated, so every new record type is a versioned extension. Rollback: the framework and records are additive; removal empties the figure slots back to their pending states (the N07 slot contract degrades honestly), and N12-N15 lose their foundation and must re-plan.

**Definition of Done:** A deterministic, token-styled, screen-reader-described, lazily loaded, print-ready SVG figure framework exists with the T1-2 records grounded in recompute-verified conventions values, tolerance couplings frozen for N18, and the framework contract handed to the remaining figure tasks.

### N12 - Author the T2-3 burette and dilution figures and the figure leak-scan engine

**Phase:** Phase III | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N11

**Domain:** Laboratory figure accuracy

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters teach burette reading and dilution with meniscus conventions (the inspection's laboratory figure precedents); the conventions island (N03) declares the meniscus and reading rules resolving the reading ambiguities; the figure framework (N11) exists with its validated format, renderer and label contract. No burette or dilution figures exist, and no leak-scan engine exists anywhere (the N08 data-level scan was a precursor specific to hint texts).

**Purpose and Rationale:** The laboratory figures must be instrument-accurate: the burette figures (the meniscus at declared readings, the graduation marks at the declared spacing, the read-at-the-bottom rule the conventions island declares, with the parallax note the masters teach), and the dilution figures (the pipette-to-flask chain with the volume marks and the dilution-factor labels), each figure teaching the reading conventions the titration tasks of topic 6 will grade against (a learner who misreads the meniscus in the figure is exercising exactly the error the grading engines must classify); and this task builds the general leak-scan engine: the scan that proves no figure's data or markup contains answer-key values (a figure that displays the answer it asks about is the subtlest form of leak, and every gradeable figure from here on passes through the engine).

**Target Artifacts and Touchpoints:** data/figures_t23.json; the leak-scan engine (tools and runtime-side checker). Touchpoints in output/simulator.html: the titration concept drawers' figures, the N15 titration figures' shared conventions, and the leak-scan gate in the build.

**Out of Scope:** No photorealistic rendering (the schematic clarity the masters use is the model); no figure data violating the conventions (the reading rules are the conventions island's, not a per-figure choice); no leak scan of learner input (the scan is authoring-time and build-time over figures and data, never a runtime surveillance of the learner).

**Main Step A - Author the burette and dilution records.** Author the T2-3 records: the burette set (records with declared reading values, the meniscus drawn at the value, the graduation grid at the declared spacing, the reading rule's annotation citing the conventions entry, and the parallax note as an authored annotation), and the dilution set (the transfer chain, the volumetric flask marks, the dilution-factor labels with their arithmetic shown in the annotation so the factor is derived visibly, never asserted mysteriously); every record cites its master anchor and conventions entries, and the reading values are authored to cover the pedagogically important cases (whole numbers, the between-marks readings that force the subdivision rule, and the near-zero and near-capacity edges).

**Subtask A.1 - Prove reading-rule fidelity and edge coverage.** Prove fidelity: for each burette record, the meniscus's rendered position matches the declared reading under the conventions island's rule (a geometric recompute: the reading value, the mark spacing and the meniscus y-position must agree, recorded per record), since a figure teaching readings with a misdrawn meniscus is worse than no figure; and the edge table records the coverage (whole, subdivided, near-zero, near-capacity) so the case that forces the subdivision rule is provably present rather than assumed.

- **A.1.1 -** Author the burette records with the declared readings and the geometric contract (mark spacing, meniscus offset per the conventions rule), and record the geometric recompute table: every record's meniscus position matches its declared reading, with a scratch misdrawn record (the meniscus one subdivision off) failing the recompute by id, proving the check bites.

- **A.1.2 -** Author the dilution records with the factor arithmetic in the annotations and the flask marks under the declared conventions, and record the citation validation (anchors and conventions entries resolve) plus the arithmetic check: each annotation's stated factor recomputes from the figure's own volumes, the derivation visible and verified.

- **A.1.3 -** Run the label contract over the new records (the graduated-scale labels are the densest label set yet: numbers plus unit strings) and record the N10 grammar pass, with the number-formatting rule (the declared decimal convention from N03) asserted over the rendered scale labels, since inconsistent decimals across a burette scale are exactly the transcription defect the conventions exist to prevent.

**Main Step B - Build the leak-scan engine and gate the figures.** Build the leak-scan engine: the general scanner takes a figure record (or any data record with declared key fields) and an answer-value set (the instance or family's key values, normalized through the unit grammar so mg, mg/mL and the composed forms compare correctly), and asserts none of the key values appear in the figure's rendered output, its data fields or its annotations, with a declared exemption mechanism (a figure that legitimately displays a value, like a labeled reading the learner must use rather than derive, declares the exemption explicitly with its reason, so the exemptions are auditable rather than holes); wire the scan into the build gate over every gradeable figure.

**Subtask B.1 - Prove the scan catches real leaks.** Prove the engine with the planted corpus: a scratch figure whose annotation quotes the answer (caught, named), a scratch figure whose axis range telegraphs the answer through an unlabeled endpoint (the borderline case, handled by the declared borderline rule: ranges that pin a gradeable value to a readable extreme are flagged for authoring review, the rule recorded), and a legitimately exempted figure (passes with its exemption recorded), so the scan's three behaviors (catch, flag, exempt) are all demonstrated rather than asserted.

- **B.1.1 -** Implement the engine with the unit-normalized comparison (values compared under the N10 grammar's normalization, so a leak written in different units is still a leak), and record the planted corpus's three behaviors with the named outputs; the corner case is a value that coincides with a common constant (a factor of 10 leaking trivially because the answer is 10), handled by the significance rule: only values distinctive to the instance or family are scan targets, and the significance rule is recorded.

- **B.1.2 -** Wire the scan into the build gate (the N31 pipeline's gate list gains the figure scan, recorded) and run the T2-3 records through it: the gradeable ones pass, the reading-display figures carry their recorded exemptions, and a scratch planted leak refuses the build with the figure named.

- **B.1.3 -** Extend the scan to the N08 hint data as a regression (the earlier data-level scan's logic converges here into one engine, with the N08 fixtures re-run through the new engine and passing), and record the convergence, so the roadmap has one leak engine, not two half-engines drifting apart.

**Main Step C - Prove the set end to end and record evidence.** Prove the T2-3 set end to end: all records validate (format, citations, geometry, arithmetic, labels), render deterministically (two-run digests), pass the leak scan (with exemptions recorded), degrade honestly on truncation, and print legibly (the print-theme render of the densest burette record recorded, the scale labels checked at the print size, since a burette scale that blurs at print defeats the paper mode's worksheet use); the smoke subset gains one burette vector.

**Subtask C.1 - Close with the handoff to the titration tasks.** The handoff is the reading-conventions contract: the titration figures of N15 and the grading engines of N17-N18 consume the same meniscus and reading rules these figures teach (the conventions entries are shared by design), and the recorded contract means a learner who studies these figures is studying exactly the rules the grading will apply, closing the teaching-assessment loop at the figure level; the ledger records the records, engine and gate digests with the sub-budget accounting.

- **C.1.1 -** Run the end-to-end proof over the full T2-3 set (validation, determinism, scan, degradation, print) and record the outputs; the corner case is the between-marks reading at the print size (the subdivision the learner must interpolate must remain visually resolvable), and the print render's resolution check is recorded against the declared print-size floor.

- **C.1.2 -** Author the reading-conventions contract (the shared entries, the grading coupling, the exemption discipline) and record its digest, handing it to N15, N17 and N18 as the frozen interface between the laboratory figures and the titration assessment.

- **C.1.3 -** Append the records, engine, contract and gate digests to the ledger, run the extended corpus twice for parity, record the set's byte contribution against the figure sub-budget, extend the smoke subset with the burette vector, and close the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the T2-3 records, when the geometric recompute and arithmetic checks run, then meniscus positions match declared readings (a scratch misdraw fails by id), dilution factors recompute from the figures' own volumes, and scale labels pass the unit and decimal conventions.

- **AC2 (negative or edge case):** Given the leak-scan engine, when the planted corpus runs, then leaks are caught and named, borderline ranges are flagged by rule, legitimate exemptions pass recorded, unit-normalized comparison holds, and a planted leak refuses the build.

- **AC3 (domain integrity and zero-regression):** Given the end-to-end proof, when the set runs, then validation, determinism, scan, degradation and print all pass with the between-marks case resolvable at print size, and the smoke vector passes in-file.

**Verification and Evidence:** Record the geometric recompute table, the arithmetic checks, the label passes, the planted corpus's three behaviors, the gate refusal, the N08 convergence regression, the print render and the smoke pass. The exemption and significance rules are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: exemptions accreting into holes over time. Guard: every exemption is authored data with its reason, and N40's ledger closure audits the exemption list. Rollback: the records and engine are additive; removal empties the T2-3 slots honestly, but N15's titration figures lose the reading contract and the build loses its leak gate, so both must re-plan.

**Definition of Done:** Instrument-accurate, geometrically verified, leak-scanned burette and dilution figures exist under a general leak-scan engine with auditable exemptions, print-legible at the subdivision level, with the reading-conventions contract frozen for the titration figures and grading engines.

### N13 - Author the T4 energy, Hess and Maxwell-Boltzmann figures

**Phase:** Phase III | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N11

**Domain:** Thermodynamics and kinetics figures

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters carry thermo-test-vectors (the C4 island verified in the inspection) and teach energy diagrams and reaction-rate distributions; the figure framework (N11) exists with its validated format; the conventions island declares the energy and rate conventions. No energy-path, Hess-cycle or distribution figures exist for this simulator.

**Purpose and Rationale:** Topic 4's figures teach the three visual models the colloquium's thermochemistry and kinetics questions assume: the energy-path diagrams (reactants, transition state, products, the activation energies forward and backward, the reaction enthalpy as the labeled difference, with the sign convention the conventions island declares applied consistently, since enthalpy sign errors are a canonical exam failure), the Hess-cycle figures (the cycle drawn with its arrows, each step's enthalpy labeled, the cycle's sum shown equal to the direct path, the arithmetic visible in the annotation), and the Maxwell-Boltzmann distribution figures (the curves at declared temperatures, the activation-energy threshold line, the shaded tail beyond it, and the labeled area meaning, with the V-06 wavelength-context discipline applied analogously: a distribution figure never implies its threshold generalizes beyond the declared reaction); every value derives from the conventions island or is authored with its derivation recorded, and every curve is generated, not hand-drawn, so its shape is mathematically honest.

**Target Artifacts and Touchpoints:** data/figures_t4.json; the curve-generation extension of the figure framework. Touchpoints in output/simulator.html: the topic 4 concept drawers, the worked chains' figures, the practice items' figure payloads.

**Out of Scope:** No calculated dynamics beyond the declared models (the distribution curves are the declared Maxwell-Boltzmann form at authored temperatures, not simulated molecules); no threshold claims beyond the declared reaction (the figure's scope note is part of the record); no axis without a term-keyed, unit-parsed label (the N10 contract, non-negotiable now and for every later figure).

**Main Step A - Extend the framework for curve generation and author the energy-path records.** Extend the figure framework with the curve-generation type (a record declares a curve function class and parameters, and the renderer generates the path points, so curve shapes are computed, consistent and diffable), then author the energy-path records: the exothermic and endothermic pairs (each path labeled with its activation energies and enthalpy under the sign convention, the sign rule cited to the conventions entry, and the annotation showing the enthalpy as the products-minus-reactants difference the convention defines), covering the pedagogical cases (the exothermic with the lower backward barrier, the endothermic, and the catalyzed-path pair showing the barrier lowered with the enthalpy unchanged, the case the catalase discussion C10 makes pedagogically central).

**Subtask A.1 - Prove sign-convention fidelity and case coverage.** Prove the sign fidelity: for every energy-path record, an independent recompute of the labeled enthalpy from the record's own energy levels matches the label with the declared sign, recorded per record (a scratch sign-flipped record fails by id), since a single sign error here would teach the exact failure the grading engines will penalize; and the coverage table records the case pairs (exothermic, endothermic, catalyzed) as authored, with the catalyzed pair carrying the C10 honesty note (the catalase values remain scientifically open, so the figure teaches the barrier-lowering model with the generic example, not the disputed values).

- **A.1.1 -** Implement the curve-generation type with its parameter validation (function class exists, parameters in range, the generated point count declared for determinism), and record the generation fixtures: identical parameters produce identical paths (digests), and the scratch invalid parameter set fails by name, keeping the extension inside the framework's fail-closed discipline.

- **A.1.2 -** Author the energy-path records with the case pairs, and record the sign recompute table with the scratch sign-flip failure, plus the coverage table with the C10 honesty note verbatim (the figure's example values chosen to avoid asserting the open catalase numbers).

- **A.1.3 -** Run the label contract over the records (axis labels, level labels, annotation text) and record the N10 pass, with the enthalpy and activation-energy unit strings checked under the grammar and the sign notation rendered per the conventions' declared notation rule.

**Main Step B - Author the Hess-cycle and Maxwell-Boltzmann records.** Author the Hess-cycle records: the cycles as step-arrow figures (each arrow labeled with its step enthalpy and direction, the direct path drawn beside the cycle, the annotation summing the cycle steps and showing the equality, the arithmetic rendered in the declared number format), covering the masters' own cycle examples (each cited to its master anchor) plus one scratch-free synthetic case for practice; author the Maxwell-Boltzmann records: the distribution curves at two declared temperatures (the shift and the flattening the model predicts, generated by the curve type), the activation-energy threshold line, and the shaded tail with its labeled meaning, with the scope note (the threshold belongs to the declared reaction) in the record's annotation.

**Subtask B.1 - Prove the cycle arithmetic and the distribution honesty.** Prove the Hess arithmetic: each cycle record's step sum recomputes to the direct path's value (the annotation's equality verified numerically, recorded per record; a scratch unbalanced cycle fails by id), since a Hess figure that does not close is not a Hess figure; prove the distribution honesty: the generated curves match the declared model's shape properties (the peak shift direction with temperature, the area normalization under the declared scale, recorded as the generation checks), and the tail shading's boundary matches the declared threshold value geometrically, so the visual and the number agree.

- **B.1.1 -** Author the Hess records with the sum-check fields (the cycle steps and the direct value as data, the equality asserted at validation), and record the recompute table with the scratch unbalanced cycle failing by id; the corner case is the cycle drawn in the reverse direction (steps traversed against their arrows, the classic sign trap), covered by an authored record with its reversed-step arithmetic shown, teaching the trap explicitly rather than avoiding it.

- **B.1.2 -** Author the Maxwell-Boltzmann records with the two-temperature comparison and the threshold geometry, and record the generation checks (peak shift, normalization, the tail boundary's geometric match to the threshold value); the corner case is the shaded area's visual claim (the area looks larger at the higher temperature, and the annotation's claim must match the model's actual prediction for the declared temperatures), verified by the recompute and recorded, since a visually exaggerated tail would teach a false rate intuition.

- **B.1.3 -** Run the label and citation validation over both sets (anchors, conventions entries, term keys, unit strings, the number format) and record the full pass, with the scope-note copy linted (the V-06 discipline: no figure implies its numbers generalize).

**Main Step C - Prove the set end to end and record evidence.** Run the end-to-end proof over the T4 set: validation (format, citations, arithmetic, generation checks), determinism (two-run digests over every generated curve), the leak scan (the Hess practice case's direct value must not appear in the record's non-exempt fields, or the exemption is declared), truncation degradation, and the print render of the densest record (the two-temperature distribution with its shading, legible at the print size, since the paper worksheet will carry these figures); the smoke subset gains one Hess vector.

**Subtask C.1 - Close with the thermodynamics handoff.** The handoff is the energy-conventions contract: the worked chains (N16) will chain Hess calculations through these figures, the graph scoring (N18) will grade the energy-path reading tasks against the same labeled conventions, and the recorded contract binds the figure labels, the chain arithmetic and the grading tolerances to the same conventions entries, so the topic 4 teaching-assessment loop is closed at the data level; the ledger records the set, the extension and the contract digests with the sub-budget accounting.

- **C.1.1 -** Run the end-to-end proof over the full T4 set and record the outputs, including the leak scan's result on the Hess practice case (exempt or clean, with the reasoning), and the print render's legibility check for the shaded distribution.

- **C.1.2 -** Author the energy-conventions contract (the shared sign rule, the tolerance coupling for the gradeable readings, the chain arithmetic's number format) and record its digest, handing it to N16 and N18 as the frozen topic 4 interface.

- **C.1.3 -** Append the records, extension, contract and gate digests to the ledger, run the extended corpus twice for parity, record the set's byte contribution against the figure sub-budget, extend the smoke subset with the Hess vector, and close the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the T4 records, when the sign, sum and generation checks run, then enthalpy labels recompute with the declared signs (a scratch flip fails by id), every Hess cycle closes numerically (an unbalanced cycle fails), and curves match the model's shape properties with tail boundaries geometric to the threshold.

- **AC2 (negative or edge case):** Given the label and citation validation, when it runs over both sets, then anchors, conventions entries, term keys, unit strings and number formats all pass, the reversed-step trap is taught explicitly, and no figure's scope note overgeneralizes.

- **AC3 (domain integrity and zero-regression):** Given the end-to-end proof, when the set runs, then validation, determinism, leak scan, degradation and print all pass with the shaded distribution legible, the energy-conventions contract is frozen for N16 and N18, and the smoke vector passes.

**Verification and Evidence:** Record the generation fixtures, the sign and sum recompute tables, the distribution honesty checks, the coverage table with the C10 note, the label passes, the leak result with reasoning, the print render and the smoke pass. The curve-generation determinism digests are recorded per record.

**Risks, Guardrails, and Rollback Plan:** Risk: the distribution figures drifting into rate-law claims the model does not license. Guard: the scope-note rule is copy-linted and the generation checks bind the visuals to the declared model. Rollback: the records and the curve extension are additive; removal empties the topic 4 slots, but N16's chains and N18's readings lose their figure sources and must re-plan.

**Definition of Done:** Mathematically generated, sign-verified, cycle-closing energy-path, Hess and Maxwell-Boltzmann figures exist with honest scope notes and the catalase honesty discipline, print-legible with shading intact, and the energy-conventions contract frozen for the chains and the graph scoring.

### N14 - Author the T5 kinetics figures with linearization tolerance fields

**Phase:** Phase III | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N11

**Domain:** Kinetics figures and linearization

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters teach reaction-rate linearization (the concentration-time and linearized plots, per the inspection's topic 5 material); the figure framework (N11) and its curve extension (N13) exist; the conventions island declares the rate and tolerance classes; the graph-scoring engine (N18) will consume tolerance fields per its declared contract. No kinetics figures and no linearization plot records exist.

**Purpose and Rationale:** Topic 5's figures teach the linearization method the kinetics questions grade: the concentration-time records (the decay curves for the declared orders, generated with the model's exact form, the half-life annotation for the first-order case), and the linearization records (the transformed plots: the natural-log or inverse concentration against time, with the best-fit line drawn, its slope and intercept labeled, and the tolerance fields the N18 scoring will apply to learner-drawn lines on the same axes), each record carrying the coupled tolerance fields (the slope tolerance class, the intercept tolerance class, the point-acceptance tolerance, all naming conventions entries, so the figure's visual line and the grader's acceptance region are the same numbers by construction), and the extrapolation rule declared: the drawn fit line is rendered only across the data's span (the no-extrapolation discipline N18 enforces and N15 formalizes for curves).

**Target Artifacts and Touchpoints:** data/figures_t5.json with the coupled tolerance fields. Touchpoints in output/simulator.html: the topic 5 concept drawers, the practice graph tasks' axes (consumed by N18 through the declared coupling), the worked chains' figures.

**Out of Scope:** No fitted-line values presented as official (the synthetic datasets are training data, labeled as such); no extrapolated renderings beyond the data span; no regression performed at runtime beyond the declared transform (the slopes and intercepts are authored or derived from the conventions island, recorded per record).

**Main Step A - Author the concentration-time and linearization records.** Author the concentration-time records: the zero-, first- and second-order decays (generated curves at declared rate constants and initial concentrations, the half-life annotation on the first-order case with its derivation shown, the axes labeled through the N10 contract), and the linearization records: the transformed plots (the natural-log form for first order, the inverse form for second order, the linear form's points, the best-fit line, the slope and intercept labels with their meanings annotated, and the dataset table rendered in the figure's companion for the worked chains); every record's parameters are authored with the derivation recorded (the linear parameters recompute from the decay parameters), so the two record families teach one consistent dataset.

**Subtask A.1 - Prove the transform consistency and the tolerance coupling.** Prove transform consistency: for each linearization record, the line's parameters recompute from the paired decay record's parameters exactly (the recompute table recorded; a scratch inconsistent pair fails by id), since a figure pair whose linear plot contradicts its own decay curve would teach method distrust; and prove the coupling: every tolerance field names an existing conventions entry, and the coupling validation asserts the figure's rendered line lies within its own tolerance fields of the true line (the figure is honest against its own grading rule), recorded per record.

- **A.1.1 -** Author the record pairs (three orders, each with its decay and linearization record, the parameters consistent), and record the recompute table with the scratch inconsistent pair's named failure, plus the half-life derivation check on the first-order annotation (the stated half-life recomputes from the rate constant).

- **A.1.2 -** Implement the tolerance coupling validation (the fields resolve, and the rendered line satisfies its own tolerances against the true parameters), and record the per-record pass; the corner case is a tolerance class expressed in significant figures rather than absolute units (the two conventions classes from N03), and the coupling validation handles both classes, with the class recorded per field.

- **A.1.3 -** Run the label contract and the number-format rules over the records (the log and inverse axis labels are the most notationally delicate: the log symbol, the inverse unit strings under the grammar), and record the pass, with the declared notation rule for the log axis cited to the conventions entry.

**Main Step B - Prove the linearization teaching sequence and the no-extrapolation rule.** Prove the sequence the figures teach: the worked-pair fixture walks a learner's path (open the decay figure, open the linear figure, read the slope, the annotations' stated rate constant recomputes from the slope), recorded as the teaching trace; and implement the no-extrapolation rule in the renderer: the fit line renders only across the data's declared span (the span stored in the record, the render clipped to it), with the scratch over-span record (a line whose declared span exceeds its data) failing validation by id, since the rule must be data-enforced, not renderer goodwill.

**Subtask B.1 - Prove the span rule and the grading preview.** Prove the span rule's grading relevance: the N18 preview fixture (a scratch learner-drawn line rendered on the same axes, accepted within the tolerance fields inside the span and the identical line's extension beyond the span simply not assessed, per the declared rule) is recorded here as the coupling's first consumer proof, so N18 inherits a demonstrated interface rather than a promise; the corner case is the near-span boundary (a learner's point at the span's edge), where the declared edge rule (inclusive at the boundary, recorded) applies, and the fixture records it.

- **B.1.1 -** Implement the span clipping in the renderer and the span validation in the format, and record the scratch over-span failure plus the clipped render of every linearization record (the line's rendered extent matching the declared span, recorded per record).

- **B.1.2 -** Run the N18 preview fixture (the drawn-line acceptance inside and outside the span) and record the three cases (inside accepted, edge inclusive, beyond not assessed) with the drawn-line geometry, freezing the coupling's runtime behavior before the scoring engine exists.

- **B.1.3 -** Author the teaching trace (the decay-to-linear walk with the rate-constant recompute from the slope) and record it, with the trace's arithmetic shown in the recorded table, teaching the method the chains (N16) will exercise and the scoring (N18) will grade.

**Main Step C - Prove the set end to end and record evidence.** Run the end-to-end proof over the T5 set: validation (format, citations, transforms, couplings, spans), determinism (two-run digests over the generated curves and lines), the leak scan (the rate constants and parameters of practice datasets must not appear in the annotations the practice tasks will grade against, or the exemption is declared with its reason), truncation degradation, and the print render (the log-axis record, the densest, legible at the print size); the smoke subset gains one linearization vector.

**Subtask C.1 - Close with the kinetics handoff.** The handoff is the linearization contract: the tolerance fields' vocabulary, the span rule's edge semantics and the coupling's field names are frozen for N18 (the scoring consumes them by name), N16 (the chains reference the datasets) and N20 (the variant engine's practice instances may reparameterize the curves within the declared parameter ranges, the reparameterization rule recorded); the ledger records the set and contract digests with the sub-budget accounting, closing the task.

- **C.1.1 -** Run the end-to-end proof over the full T5 set and record the outputs, including the leak scan's per-record results with any exemptions reasoned, and the print render's legibility check for the log axis.

- **C.1.2 -** Author the linearization contract (the field vocabulary, the span and edge rules, the reparameterization ranges for N20) and record its digest, handing it to N16, N18 and N20 as the frozen topic 5 interface.

- **C.1.3 -** Append the records and contract digests to the ledger, run the extended corpus twice for parity, record the set's byte contribution against the figure sub-budget, extend the smoke subset with the linearization vector, and close the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the T5 record pairs, when transforms recompute, then linear parameters match decay parameters exactly (a scratch inconsistency fails by id), half-life annotations recompute, and every tolerance field resolves with its class recorded.

- **AC2 (negative or edge case):** Given the span rule and N18 preview, when lines render and are drawn, then fit lines never exceed their data spans (an over-span record fails), inside-span draws are accepted, the edge is inclusive by rule, and beyond-span geometry is not assessed.

- **AC3 (domain integrity and zero-regression):** Given the end-to-end proof, when the set runs, then validation, determinism, leak scan with reasoned exemptions, degradation and print all pass, the linearization contract is frozen for N16, N18 and N20, and the smoke vector passes.

**Verification and Evidence:** Record the recompute tables, the coupling validations with both tolerance classes, the label and notation passes, the span fixtures with edge semantics, the teaching trace, the leak results and the print render. The reparameterization ranges for the variant engine are recorded verbatim in the handoff contract.

**Risks, Guardrails, and Rollback Plan:** Risk: tolerance fields tuned to the authored datasets and failing on N20's reparameterized variants. Guard: the coupling validation runs per record at build, and the reparameterization ranges are declared so variant parameters stay inside the tolerance classes' honest reach. Rollback: the records are additive; removal empties the topic 5 slots, but N18 loses its tolerance-field source and N16 its datasets, so both must re-plan.

**Definition of Done:** Transform-consistent, span-limited, tolerance-coupled kinetics figures for all three orders exist with the drawn-line acceptance interface proven in preview, the linearization contract frozen for the scoring engine, the chains and the variant engine, and the full evidence set recorded.

### N15 - Author the T6-7 titration curves and calibration figures with the no-extrapolation rule

**Phase:** Phase III | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N11, N12

**Domain:** Titration and calibration figures

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters teach titration curves and calibration plots (the inspection's topic 6-7 material); the reading conventions contract (N12) freezes the meniscus and reading rules; the curve generation (N13) and the span discipline (N14) exist; the conflict registry carries V-05 (the endpoint versus equivalence wording) and V-07 (the calibration assumptions). No titration or calibration figures exist for this simulator.

**Purpose and Rationale:** Topic 6's titration figures teach the curve the burette readings produce: the pH-volume curves for the declared cases (strong acid with strong base at a minimum, plus the masters' own cases, each cited), with the equivalence point marked, the endpoint region annotated with the indicator's transition range (the V-05 discipline: the figure and its annotation distinguish the equivalence point from the indicator endpoint explicitly, teaching the difference the wording conflicts obscured), and the half-equivalence and buffer regions labeled where the masters teach them; topic 7's calibration figures teach the plot the analytical method rests on: the calibration curve with its data points, the fitted line, the unknown's signal marked on the axis and read through the line, with the V-07 discipline (the assumptions labeled: the linear range declared, the matrix match stated or honestly absent, the intercept's meaning annotated), and both figure families enforce the no-extrapolation rule formally: no fitted line, reading or annotated value is rendered beyond the data's declared span, and the rule is declared in the figure contract for N18's scoring to inherit.

**Target Artifacts and Touchpoints:** data/figures_t67.json; the no-extrapolation rule in the figure contract. Touchpoints in output/simulator.html: the topic 6-7 concept drawers, the titration practice tasks' figures, the worked chains' calibration examples.

**Out of Scope:** No real analytical data claims (the datasets are synthetic training data or the masters' own worked numbers, labeled per record); no indicator recommendation claims beyond the masters' own teaching; no extrapolated readings anywhere (the rule is absolute and build-enforced).

**Main Step A - Author the titration curve records.** Author the titration records: the pH-volume curves generated point-wise from the declared chemistry (the acid-base model the conventions island licenses, the parameters per record, the generated curve's inflection at the equivalence volume verified numerically), with the annotations (the equivalence point, the indicator transition range band, the endpoint region's wording per the V-05 rule, the half-equivalence point where the case teaches it), each record citing its master anchor and conventions entries, and the reading-coupling (the burette volumes on the axis follow the N12 reading contract's spacing and subdivision rules, so the figure's axis and the burette figures teach one reading discipline).

**Subtask A.1 - Prove the curve chemistry and the V-05 wording.** Prove the chemistry: each record's generated curve passes the declared model checks (the equivalence-point inflection at the declared volume, the initial pH recomputing from the declared concentration, the buffer region's slope behavior recorded), since a titration curve whose inflection is misplaced would teach exactly the misreading the grading penalizes; and prove the V-05 wording: the annotation copy lint asserts the equivalence point and the endpoint are named distinctly wherever both appear, with the distinction's explanation present, recorded per record, converting the conflict's resolution into enforced figure copy.

- **A.1.1 -** Implement the titration curve generation (the declared model, the parameters, the point count for determinism) and record the model checks per record: the inflection verification, the initial pH recompute, and the two-run determinism digests; a scratch record whose declared equivalence volume disagrees with its generated inflection fails by id.

- **A.1.2 -** Author the annotations with the V-05 rule and record the copy lint per record (distinct naming, the explanation present, the indicator band drawn at its declared range), with the corner case taught explicitly: a record where the indicator's range misses the equivalence inflection (the wrong-indicator case the masters warn about), authored deliberately with its annotation naming the failure, since teaching the wrong-indicator trap visually is worth more than hiding it.

- **A.1.3 -** Run the reading-coupling validation (the axis volumes under the N12 spacing and subdivision rules, the meniscus-relevant graduations rendered per the contract) and record the pass, binding the laboratory figures and the titration curves into one reading discipline.

**Main Step B - Author the calibration records and formalize the no-extrapolation rule.** Author the calibration records: the signal-concentration plots (the standards' points, the fitted line across the standards' span, the unknown's signal marked on the signal axis with its reading through the line to the concentration axis, the reading rendered inside the span by construction), the assumption annotations (the V-07 discipline: the linear range declared, the matrix-match statement honest, the intercept annotated with its meaning, blank correction mentioned where the masters teach it), and the declared scope note per record; formalize the no-extrapolation rule in the figure contract: the span is data, the renderer clips lines and readings to it, validation rejects any record whose declared reading or fitted span exceeds its data, and the rule's text enters the contract N18 inherits verbatim.

**Subtask B.1 - Prove the rule holds and the readings recompute.** Prove the rule: the scratch over-span reading record fails validation by id, every authored reading recomputes through the fitted line's parameters (the reading table recorded per record: signal in, concentration out, matching the annotation), and the assumption annotations pass the honesty lint (every assumption stated or its absence stated, per the V-07 resolution); the corner case is the unknown near the span's edge (the reading inside but close, where the tolerance discussion belongs), authored deliberately with its edge annotation, teaching the honest-limit case the analytical material itself teaches.

- **B.1.1 -** Author the calibration records with the standards, fits and readings, and record the reading recompute table (each unknown's concentration recomputing from the line's parameters, the annotation matching), with a scratch wrong reading failing by id.

- **B.1.2 -** Formalize the no-extrapolation rule in the contract (the span as data, the renderer's clipping, the validation's rejection, the inherited text for N18), and record the scratch rejection plus the clipped renders of every record (lines and readings within their spans, recorded per record).

- **B.1.3 -** Run the V-07 honesty lint over the assumption annotations and record the per-record results with every assumption either stated or its absence stated, with the near-edge record's annotation recorded verbatim as the discipline's demonstrated case, so the calibration teaching never implies an unexamined linear range.

**Main Step C - Prove the set end to end and close Phase III.** Run the end-to-end proof over the T6-7 set: validation (format, citations, model checks, couplings, spans), determinism (two-run digests over the generated curves), the leak scan (the practice cases' equivalence volumes and unknown concentrations must not leak into non-exempt annotations; the wrong-indicator and near-edge teaching records carry their declared, reasoned exemptions), truncation degradation, and the print render (the titration curve with its band, and the calibration plot with its reading, legible at the print size, since the paper worksheet carries the colloquium's actual curve-reading work); the smoke subset gains one titration vector.

**Subtask C.1 - Close Phase III with the analytical handoff.** The handoff closes the figure phase: the titration contract (the model vocabulary, the V-05 wording rule, the reading coupling) goes to N17 and N18 (the quantity engines and graph scoring grade against these figures' declared models and tolerances), the calibration contract (the assumption vocabulary, the no-extrapolation rule verbatim) goes to N18 as the scoring's inherited rule, and the figure framework's completed type registry goes to N37's visual matrix as the expected-geometry source; the ledger records the set, contracts and rule digests with the phase's full sub-budget accounting, and Phase III ends with every topic's teaching figures generated, verified and contract-bound.

- **C.1.1 -** Run the end-to-end proof over the full T6-7 set and record the outputs, including the leak results with the teaching records' reasoned exemptions and the two print renders' legibility checks (the titration band and the calibration reading both resolvable at the declared print size), so the set's evidence is complete in one pass.

- **C.1.2 -** Author the titration and calibration contracts and record their digests, handing the model vocabulary, the assumption discipline and the no-extrapolation rule verbatim to N17, N18 and (for the completed type registry) N37, so the analytical grading inherits the figures' declared rules without reinterpretation.

- **C.1.3 -** Append the records, contracts and gate digests to the ledger, run the extended corpus twice for parity, record the T6-7 set's and Phase III's total byte contribution against the figure sub-budget (60-140 KiB from Section 1, the phase's measured share recorded), extend the smoke subset with the titration vector, and close the task and the phase.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the titration records, when model checks run, then inflections match declared equivalence volumes (a scratch disagreement fails by id), initial pH values recompute, the V-05 wording is enforced per record, and the wrong-indicator trap is taught explicitly.

- **AC2 (negative or edge case):** Given the calibration records and the formal rule, when validation runs, then over-span readings fail by id, every reading recomputes through its fitted line, assumption annotations pass the honesty lint, and the near-edge case is taught with its annotation.

- **AC3 (domain integrity and zero-regression):** Given the end-to-end proof, when the T6-7 set runs, then validation, determinism, leak scan with reasoned exemptions, degradation and print all pass, the contracts and the no-extrapolation rule are handed to N17, N18 and N37 verbatim, and the smoke vector passes.

**Verification and Evidence:** Record the model check tables, the V-05 copy lint results, the reading couplings, the reading recompute table, the rule rejection and clipped renders, the honesty lint, the leak results with exemptions, and the print renders. Phase III's figure sub-budget accounting is recorded against Section 1's declaration.

**Risks, Guardrails, and Rollback Plan:** Risk: the titration model's simplifications diverging from the masters' own drawn curves (the masters are the teaching authority). Guard: each record cites its master anchor and the model checks run per record, so divergence is a named build failure. Rollback: the records and the contract rule are additive; removal empties the topic 6-7 slots, but N17 and N18 lose their model and rule sources and must re-plan.

**Definition of Done:** Model-verified titration curves with enforced equivalence-endpoint wording and honest calibration plots with labeled assumptions exist under the formal, build-enforced no-extrapolation rule, print-legible for the paper worksheet, with the analytical contracts frozen and Phase III's figure program complete and evidenced.


## 10. Phase IV (N16-N20) - Worked Examples, Input Engines, Plot Scoring, Method Cards and Variants

Phase IV builds the simulator's doing layer: the fourteen worked example chains with collapsed, leak-free reveal (N16); the quantity and conservation engines with the dimension gate that structurally excludes the V-04 defect class and the four-class error taxonomy mapped to misconception signatures (N17); the graph scoring engine with criterion shapes, validity rules, the inherited no-extrapolation rule and keyboard-pointer parity (N18); the method cards with the ordering, matching and sequence verdict engines, all structural, never keyword-matching, with self-assessment kept honestly pending (N19); and the variant engine with the 28 family templates, the review-gated 112-instance bank frozen by digest, and the ephemeral retry path (N20). When this phase closes, the simulator can pose, grade and diagnose real work.

### N16 - Author the EX01-EX14 worked example chains with collapsed reveal and leak-free delivery

**Phase:** Phase IV | **Priority:** P0 | **Risk:** Medium | **Effort:** L | **Dependencies:** N07, N11, N15

**Domain:** Worked example chains

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters teach worked calculations across all seven topics (the inspection's chain precedents, each master cited by anchor in the N02 coverage island); the concept map and its drawer contract (N07) exist; the figure framework and all topic figure sets (N11-N15) exist with their contracts; the predecessor governance forbids official exam claims (AGENTS.md, verified). No worked example chains, no chain data format and no reveal mechanism exist for this simulator.

**Purpose and Rationale:** The EX01-EX14 chains are the bridge between reading and doing: fourteen multi-step worked calculations (two or more per topic, spanning stoichiometry, concentration and dilution, energy and Hess cycles, kinetics linearization, titration and calibration arithmetic, and the remaining coverage outcomes the 64-outcome island assigns them), each authored as a chain data record (steps with their quantities, transformations, intermediate results and reasoning text in Latvian, every numeric value derived from the conventions island or recomputed independently), rendered collapsed by default with the reasoning hidden and each step's result revealed one at a time on learner interaction, so the chains function as self-explanation practice rather than passive reading; the chains carry the honesty banner (training material, not an official exam artifact) and the leak-free discipline (no chain step's answer value appears in the DOM before its reveal, so a learner cannot extract answers by inspecting the markup, and the same data feeds practice items without exposing their keys).

**Target Artifacts and Touchpoints:** The chain data format; data/chains.json (EX01-EX14); the chain renderer with reveal-on-interaction. Touchpoints in output/simulator.html: the concept drawers' example slots (N07), the topic 4-7 figures embedded in their chains (N13-N15), the method cards' example references (N19), the practice items' chain links (N20).

**Out of Scope:** No official colloquium question claims (the chains teach the masters' own worked methods, labeled as training material per the honesty banner); no runtime recomputation of chain steps beyond the declared transforms (values are authored and verified, with the verification recorded); no reveal state persisted across sessions (chains always open collapsed, keeping storage honest and sessions clean).

**Main Step A - Define the chain format and author the EX01-EX14 records.** Define the chain data format: each chain record declares its id (EX01-EX14), its topic and coverage outcome link (resolving into the N02 island), its master anchor citation, its figure references (the N11-N15 record ids, rendered inside the chain at declared step positions), its step list (each step: the quantity statement, the transformation rule cited to a conventions entry, the result value, the reasoning text), and its reveal keys (per-step keys ensuring the rendered DOM before any interaction contains no future step result); author the fourteen records across the seven topics, each numeric value either taken from the conventions island with its entry named or recomputed independently with the recompute recorded in the authoring evidence.

**Subtask A.1 - Prove every chain value and citation.** Prove the records: for each chain, an independent recompute (the second-opinion discipline applied at authoring time) reproduces every step result from the stated inputs and transformations, recorded per chain (a scratch chain with one wrong intermediate fails the recompute by chain and step id), and the citation validation asserts every anchor, conventions entry, figure id and outcome link resolves (zero dangling references across all fourteen, recorded), since a chain that teaches a value no one can recompute is exactly the unverifiable teaching the governance forbids.

- **A.1.1 -** Define the format with the field tables and author the first seven records (EX01-EX07, topics 1-4), and record the recompute table: every step value reproduced from stated inputs with the transformation cited, plus the scratch wrong-intermediate failure proving the check bites at the step level.

- **A.1.2 -** Author the remaining seven records (EX08-EX14, topics 4-7, including the titration chain that embeds the N15 curve and the calibration chain that embeds the N15 plot), and record their recompute table and the figure embedding validation (each referenced figure id exists and its slot position is declared, so a chain never renders a figure it does not cite).

- **A.1.3 -** Run the citation validation across all fourteen records (anchors, conventions entries, figure ids, outcome links) and record the zero-dangling pass; the corner case is a chain whose step cites two conventions entries (a unit conversion and a tolerance rule together), covered by the declared multi-citation form and recorded as the format's demonstrated case.

**Main Step B - Implement the collapsed reveal renderer with leak-free delivery.** Implement the chain renderer: chains render collapsed (step statements visible, results and reasoning hidden), each step reveals on learner interaction (a button per step and a reveal-all control that confirms the self-explanation intent first), the reveal is client-side state only (no storage, no URL leakage), and the leak-free delivery is enforced at build: the pre-interaction DOM fixture asserts that no step result value, no reasoning text and no future-step quantity appears in the rendered markup or the JSON islands until its reveal is triggered, since the chains' data lives in the artifact and an answer visible in the island defeats the reveal's entire purpose.

**Subtask B.1 - Prove leak-freedom and reveal semantics.** Prove the leak scan: for each chain, the pre-reveal DOM snapshot and the island content are scanned for every result value (normalized through the unit grammar so different unit spellings cannot hide a leak), and only the currently revealed steps' values appear, recorded per chain; prove the reveal semantics: the reveal-all confirmation fixture (the control asks once, then reveals), the re-collapse fixture (a chain can be collapsed again, restoring the pre-reveal DOM state exactly, digest-compared), and the corner case of a chain embedded in a practice item (the item's own key values must never ride along in the chain's reveal data, asserted by the same scan extended to the item context).

- **B.1.1 -** Implement the renderer with the per-step and reveal-all controls, and record the two render states' digests per chain (pre-reveal and fully revealed), plus the re-collapse round-trip digest equality, so the collapse is provably reversible rather than merely visually hidden.

- **B.1.2 -** Implement the build-time leak scan over the rendered fixture and the islands, and record the per-chain results with the unit-normalized comparison; a scratch chain with one result value placed in the pre-reveal markup fails the build with the chain and step named, proving the gate enforces rather than suggests.

- **B.1.3 -** Run the item-context fixture (a chain linked from a practice item, scanned for the item's key values in the chain's data) and record the pass, with the honesty banner's copy lint recorded (the banner text fixed per the training-material label, no official exam wording anywhere in the chains).

**Main Step C - Integrate with the map, items and method cards, then prove end to end.** Integrate the chains: the concept map's outcome nodes link their chains (the N07 drawer opens at the chain with return-focus honored), the method cards (N19's contract) reference chains as their worked examples, and the practice items (N20's contract) link their teaching chains; prove the integration with the navigation fixtures (a drawer opened from the map, a chain revealed, the drawer closed, focus restored to the invoking control, recorded as the focus trace) and the cross-reference validation (every method card and practice item that declares a chain reference resolves to an existing chain id, and vice versa for the chains' back-links, recorded as the reference table).

**Subtask C.1 - Prove print honesty and close the task.** The print honesty proof: under the print stylesheet (the N34 contract's precursor applied here), a fully revealed chain prints with its steps and reasoning (the learner has earned the full text by revealing it), while a collapsed chain prints only the step statements with a note that the reasoning is interactive, recorded as the print render, since silently printing hidden answers would be a leak and printing nothing would waste the paper mode's teaching value; the smoke subset gains one chain vector (a fixed chain's pre-reveal and revealed digests asserted in-file), and the ledger records the format, records, recompute tables, scans and integration digests.

- **C.1.1 -** Run the navigation and focus fixtures over the map-to-chain and item-to-chain paths and record the focus traces; the corner case is the reveal-all control inside a drawer (the confirmation must not trap focus when the drawer closes mid-reveal), covered by the declared focus-restore rule and recorded as the fixture's edge case.

- **C.1.2 -** Run the cross-reference validation and record the reference table; then run the print render for one revealed and one collapsed chain and record both, freezing the print honesty rule for N34 to inherit.

- **C.1.3 -** Append the format, records, recompute tables, leak scans, focus traces and print renders to the ledger, run the extended corpus twice for parity, record the chains' byte contribution against the runtime sub-budget, extend the smoke subset with the chain vector, and close the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the EX01-EX14 records, when recomputes and citation validation run, then every step value reproduces from stated inputs (a scratch wrong intermediate fails by id), every anchor, entry, figure id and outcome link resolves, and the chains cover all seven topics.

- **AC2 (negative or edge case):** Given the reveal renderer, when the leak scan runs, then pre-reveal markup and islands contain no future result values under unit-normalized comparison (a planted leak fails the build by chain and step), reveal-all confirms once, and re-collapse restores the pre-reveal digest exactly.

- **AC3 (domain integrity and zero-regression):** Given the integration, when navigation, cross-reference and print proofs run, then the map and item paths restore focus per trace, every method card and item chain reference resolves bidirectionally, revealed chains print fully while collapsed chains print statements with the interactive note, and the smoke vector passes.

**Verification and Evidence:** Record the recompute tables per chain, the citation and cross-reference passes, the two-state render digests, the re-collapse round-trip, the per-chain leak scan results with the planted-leak refusal, the item-context pass, the focus traces, and the print renders. The chains' byte contribution is recorded against the runtime sub-budget from Section 1.

**Risks, Guardrails, and Rollback Plan:** Risk: chain values drifting from the conventions island during later edits. Guard: the recompute table is a build-gated artifact, so a drifted value is a named build failure. Rollback: the chains are additive; removal empties the example slots and the method card references, but N19 and N20 depend on the chains for their examples and links, so both must re-plan if the format is withdrawn.

**Definition of Done:** Fourteen recompute-verified, citation-complete worked chains exist with leak-free collapsed reveal, reversible state, honest print behavior and the training-material banner, integrated into the map, items and method cards with focus honored, and evidenced in the ledger.

### N17 - Implement the quantity and conservation engines with the four-class error taxonomy

**Phase:** Phase IV | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N03, N05, N09

**Domain:** Calculation engines and error classification

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the golden vector corpus and cross-language PRNG twins (N05) exist with the oracle-independent contract; the misconception signature taxonomy (N09) exists with its error-class vocabulary; the conventions island (N03) exists with the V-04 dimension defect (the mg to g to L density conversion failure) registered; the masters teach the quantity arithmetic these engines must reproduce (the inspection's calculation precedents). No quantity engine, no conservation checker and no parse-error classification exist for this simulator.

**Purpose and Rationale:** The quantity engine is the single calculation authority: all stoichiometric, concentration, dilution, energy and titration arithmetic flows through one engine that consumes only the conventions island's constants, units and rules (no local copies of atomic masses or conversion factors, so a constant is corrected once and everywhere), with quantities as dimensioned values (magnitude, unit, significant figures) rather than bare numbers, so the V-04 defect class (a density conversion that mixes mg with g and L inconsistently) is impossible to express: the dimension gate rejects a calculation whose unit algebra does not close, by rule, before any numeric result exists; the conservation engine checks the mass and mole accounting the stoichiometry teaching requires (what enters must appear, transformed, at the exit); and the four-class parse-error taxonomy (unreadable input, dimensionally inconsistent input, physically implausible input within dimensions, and syntactically valid but out-of-domain input) classifies every failure the engines return, with each class mapped onto the N09 misconception signatures so a learner's error produces feedback that names the misconception, not just the wrong answer.

**Target Artifacts and Touchpoints:** The quantity engine module; the conservation checker; the parse-error classifier with the four classes; the engine's vector harness binding to the N05 corpus. Touchpoints in output/simulator.html: every numeric response component (N22's inputs), the grading engine (N23), the variant engine's checks (N20), the practice feedback paths (N28).

**Out of Scope:** No engine-level tolerance decisions (tolerances come from the conventions entries the response declares, never hard-coded); no natural-language parsing of formulas beyond the declared input grammar (free-text chemistry is the N19 self-assessment path, never parsed as arithmetic); no error text authored in the engine (feedback strings come from the N09 taxonomy and the term island, so one misconception has one string).

**Main Step A - Implement the dimensioned quantity engine and the dimension gate.** Implement the quantity engine: the value type (magnitude, unit expression parsed through the N10 grammar, significant figures), the arithmetic operations (addition requiring compatible dimensions, multiplication combining them, conversion applied only through declared conventions entries), and the dimension gate (every operation records its unit algebra, and a computation whose input and output dimensions do not close fails with the dimension class before any number is produced), so the V-04 defect is structurally excluded: a learner who enters a density conversion with mixed mass units gets the dimensional inconsistency class with the misconception-linked feedback, not a numerically confident wrong answer; the engine consumes the conventions island exclusively, with an import-time assertion that no constant is defined locally (the no-drift rule made mechanical).

**Subtask A.1 - Prove the gate against the V-04 corpus and the vectors.** Prove the dimension gate: the V-04 corpus (the density defect's historical forms: mg with L against g with mL, the unit-prefixed variants, the reordered expressions) all fail with the dimension class, recorded per form; and the engine's happy paths are proven verdict-for-verdict against the N05 golden vectors (the oracle-independent contract: the engine's output for each vector matches the recorded verdict exactly, with mismatches failing the build by vector id), so the engine is not merely plausible but aligned with the frozen corpus the whole roadmap trusts.

- **A.1.1 -** Implement the value type and operations with the unit algebra ledger (every operation's dimension accounting recorded internally), and record the no-local-constants assertion plus the conventions consumption proof (the engine's constant table digests equal the island's entries, compared at build).

- **A.1.2 -** Implement the dimension gate and run the V-04 corpus (each historical defect form failing with the dimension class and the mapped misconception feedback, recorded per form), plus a scratch valid conversion passing, proving the gate rejects the defect class without rejecting honest unit conversion.

- **A.1.3 -** Run the N05 vector harness over the engine's arithmetic surface (the stoichiometry, concentration, dilution and energy vectors), and record the verdict-for-verdict table; a scratch engine regression (one altered constant) fails the harness by vector id, proving the alignment check detects drift.

**Main Step B - Implement the conservation checker and the four-class error taxonomy.** Implement the conservation checker: for the stoichiometry and reaction contexts, the checker takes the declared species and quantities and asserts the accounting (mass in equals mass out across the transformed forms, moles conserved through the declared stoichiometry), returning either the conservation verdict or the specific imbalance with its signature; implement the four-class parse-error taxonomy (class one: unreadable, the input grammar fails; class two: dimensionally inconsistent, the gate rejects; class three: physically implausible within dimensions, the declared plausibility rules reject, like a negative concentration or a yield above the declared bound; class four: out-of-domain, syntactically and dimensionally valid but outside the response's declared domain, like a pH of 14.7 entered into a question whose system declares the 0-14 range), with each class mapped to the N09 signatures and each mapped feedback string drawn from the taxonomy's registry, so classification and feedback are one act.

**Subtask B.1 - Prove the taxonomy's completeness and signature alignment.** Prove the taxonomy: the completeness fixture (a corpus of malformed and adversarial inputs, at least one per class plus boundary cases, like an input that is simultaneously unreadable and dimensionally broken, where the declared precedence rule orders the classes and the rule is recorded) classifies every member into exactly one class per the precedence, recorded per input; and the signature alignment validation asserts every taxonomy class maps to an existing N09 signature and every mapped string resolves in the term island (zero dangling feedback, recorded), since a classified error with no feedback string is a dead end for the learner.

- **B.1.1 -** Implement the conservation checker with the declared accounting rules and record the vector pass (the conservation vectors from the N05 corpus, verdict-for-verdict), plus the imbalance case: a scratch unbalanced record returns the imbalance verdict with its signature, proving the checker does not merely pass or crash.

- **B.1.2 -** Implement the four classes with the precedence rule and run the completeness corpus, recording per-input classifications and the precedence demonstration for the ambiguous member; the corner case is class three's plausibility bounds themselves (which come from conventions entries, never engine constants), and the bound consumption is recorded per rule used.

- **B.1.3 -** Run the signature alignment validation and record the zero-dangling pass, with one full feedback path traced end to end (a class-two input producing its mapped signature's string, rendered and recorded), demonstrating the taxonomy-to-feedback contract in one recorded example.

**Main Step C - Bind the engines to the golden contract and close the task.** Bind the engines to the frozen contract: the full vector harness (arithmetic, conservation, classification vectors) runs in both languages (the Python authoring twin and the JavaScript runtime, per the N05 cross-language policy), with verdicts compared across languages and recorded, so the runtime engine and the authoring engine are provably the same logic; the digests of both harness runs enter the ledger, and the engine's public contract (its function signatures, its error classes, its conventions consumption) is frozen as the interface N22, N23 and N20 consume, since three later tasks build on this engine and its contract must not shift under them.

**Subtask C.1 - Close with the engine evidence and the runtime budget proof.** The closure proof is the runtime budget: the engines' compiled contribution is measured against the runtime sub-budget (120-220 KiB declared in Section 1, the engines' share recorded), the parse-cost fixture (a thousand synthetic inputs classified in the declared time bound on the reference device class, recorded as the throughput note), and the smoke subset gains the classification vector (a fixed input's class and feedback digest asserted in-file); the ledger records the engines, the taxonomy, the cross-language tables and the budget accounting, and the task closes with the calculation authority of the whole simulator in place.

- **C.1.1 -** Run the full cross-language harness (both engines over the full vector set, verdicts compared) and record the table with the digests; any cross-language divergence fails by vector id and is fixed before closure, since the two engines drifting is the roadmap's most expensive silent failure.

- **C.1.2 -** Run the runtime budget measurement (compiled size share, parse throughput note on the reference device class) and record both against the Section 1 declarations; then extend the smoke subset with the classification vector and record its in-file assertion.

- **C.1.3 -** Author the frozen engine contract (function signatures, error classes, conventions consumption, the precedence rule verbatim) and record its digest, appending the engines, taxonomy and harness evidence to the ledger, running the extended corpus twice for parity, and closing the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the quantity engine, when the V-04 corpus and N05 vectors run, then every historical defect form fails the dimension class with mapped feedback, a valid conversion passes, the no-local-constants assertion holds, and verdicts match the frozen corpus verdict-for-verdict.

- **AC2 (negative or edge case):** Given the taxonomy, when the completeness corpus runs, then every input classifies into exactly one class per the precedence rule, class bounds come from conventions entries, and every class maps to an existing signature with a resolving feedback string.

- **AC3 (domain integrity and zero-regression):** Given the cross-language harness and closure proofs, when both engines run the full vector set, then verdicts match across languages, the compiled size and parse throughput stay inside the declared budgets, the classification smoke vector passes, and the engine contract is frozen for N22, N23 and N20.

**Verification and Evidence:** Record the V-04 corpus results per form, the verdict-for-verdict tables for arithmetic and conservation, the classification corpus with the precedence demonstration, the signature alignment pass, the cross-language comparison table with digests, the budget measurements, and the smoke vector assertion. The frozen engine contract digest enters the ledger.

**Risks, Guardrails, and Rollback Plan:** Risk: the dimension gate rejecting honest pedagogical cases (unit conversions the masters teach). Guard: the V-04 corpus includes a scratch valid conversion, and the class boundaries are conventions data, reviewable without engine edits. Rollback: the engines are additive modules; removal leaves the numeric inputs without an authority and N22, N23 and N20 without their foundation, so those tasks must re-plan.

**Definition of Done:** A single conventions-consuming, dimension-gated quantity authority with a conservation checker and a complete four-class error taxonomy exists, proven verdict-for-verdict against the frozen vector corpus in both languages, with mapped feedback strings, measured budgets, a frozen contract, and full ledger evidence.

### N18 - Implement the graph scoring engine with criterion shapes and inherited no-extrapolation rule

**Phase:** Phase IV | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N05, N11, N14

**Domain:** Graph interpretation and drawn-response scoring

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the figure framework and its tolerance-coupled records (N11, N14) exist with the tolerance fields naming conventions entries; the no-extrapolation rule is formalized in the figure contract (N15) with its span and edge semantics; the N14 preview fixture demonstrated the drawn-line acceptance interface; the golden corpus (N05) declares the graph vector class. No graph scoring engine and no drawn-response capture exist for this simulator.

**Purpose and Rationale:** The graph scoring engine grades two families of graph work the colloquium's method demands: reading tasks (a learner marks a value on a rendered figure, like the pH at a declared volume on a titration curve or the concentration read through a calibration line, scored against the figure's tolerance fields), and drawing tasks (a learner draws a fit line or a curve segment on declared axes, scored against the criterion shapes: the N15 declared models and the N14 tolerance classes), with the validity rules rejecting unphysical submissions before scoring (a drawn line with a positive slope where the criterion shape demands negative, a reading outside the axis range, a curve segment that doubles back where the model is monotonic), and the no-extrapolation rule inherited verbatim: geometry beyond the data's declared span is not assessed (the N14 edge semantics, inclusive at the boundary), so a learner is never graded on a region the figure itself declares unassessed; the engine is pointer-and-keyboard equal (a drawn line via keyboard stepping is scored identically to a pointer drag, by contract, since N33's keyboard program depends on the scoring being input-agnostic).

**Target Artifacts and Touchpoints:** The graph scoring engine module; the drawn-response capture component; the scoring harness binding to the N05 graph vectors. Touchpoints in output/simulator.html: the graph response components (N22), the grading engine's graph pathway (N23), the practice graph items (N20), the drawn-response keyboard map (N33).

**Out of Scope:** No aesthetic scoring (position and shape only, never penmanship or smoothness); no scoring beyond declared assessable regions (the no-extrapolation rule is absolute); no hidden tolerance overrides (every scoring decision cites the tolerance fields' conventions entries in its verdict record, so grading is auditable per item).

**Main Step A - Implement the reading scorer and the drawn-response capture.** Implement the reading scorer: a reading submission (a marked point on a rendered figure) is scored against the figure record's tolerance fields (the conventions entry named by the record, resolved at scoring time, never copied), returning a verdict with its cited entry and the marked point's geometric record; implement the drawn-response capture: the component records a drawn line or curve segment as a geometric payload (an ordered point list in figure coordinates), with pointer and keyboard input producing the identical payload format (the keyboard map steps the active point by declared increments, and the payload is input-agnostic by construction), so the scorer never knows which device drew the line.

**Subtask A.1 - Prove reading fidelity and payload parity.** Prove the reading scorer: the N05 graph vectors' reading entries grade verdict-for-verdict (each vector's expected verdict reproduced, recorded), and the tolerance class handling covers both classes from N03 (absolute and significant-figure), recorded per class; prove the payload parity: the parity fixture draws the same line twice (pointer path and keyboard path, scripted), and the two payloads digest equal, recorded, since the keyboard learner must be scored by exactly the rules the pointer learner is scored by.

- **A.1.1 -** Implement the reading scorer with the conventions-resolved tolerances and run the vector pass (verdict-for-verdict on the reading entries) with both tolerance classes exercised, recording per-entry results; a scratch reading one tolerance outside the boundary grades as outside, proving the tolerance is enforced, not decorative.

- **A.1.2 -** Implement the drawn-response capture with the shared payload format and run the pointer-keyboard parity fixture, recording the digest equality; the corner case is the keyboard fine-step (the declared increment smaller than the tolerance class for precision work), and the increment rule is recorded so the keyboard path is never structurally penalized.

- **A.1.3 -** Record the capture component's input-agnostic contract (payload schema, keyboard increments, pointer sampling) as the frozen interface for N22 and N33, with the schema's validation fixtures (a malformed payload failing by name) recorded.

**Main Step B - Implement the drawing scorer with criterion shapes and validity rules.** Implement the drawing scorer: a drawn line is scored against the criterion shape (the record's declared true parameters, per the N14 coupling: slope and intercept within their tolerance classes across the assessed span), a drawn curve segment against the declared model's shape properties (the monotonicity and curvature the record declares), with the no-extrapolation rule applied at scoring (points beyond the span are excluded from assessment, the boundary inclusive per the N14 rule), and the validity rules applied first: the pre-scoring checks (the submission within the axis range, the shape's direction and monotonicity plausibly matching the criterion's declared properties, the segment not empty), so unphysical submissions return the validity verdict with its reason class rather than a numeric score against an absurd submission; every verdict records its cited conventions entries and the assessed geometry, so any grading decision can be replayed from the verdict record alone.

**Subtask B.1 - Prove shape scoring and the no-extrapolation inheritance.** Prove the drawing scorer: the N05 graph vectors' drawing entries grade verdict-for-verdict (including the deliberate near-miss vectors: a line within slope tolerance but outside intercept tolerance, a segment correct inside the span but wildly wrong beyond it, which must grade on the inside only, recorded), and the validity corpus (the unphysical submissions: wrong-direction slope, doubling-back segment, out-of-range reading, empty submission) returns the validity class per member, recorded; the corner case is the boundary-inclusive edge (a point exactly at the span edge), graded per the N14 rule and recorded as the demonstrated edge case.

- **B.1.1 -** Implement the drawing scorer with the criterion-shape comparison and run the vector pass on the drawing entries, recording verdict-for-verdict results with the near-miss vectors' verdicts (the span-excluded geometry provably not assessed); a scratch criterion mismatch fails by vector id.

- **B.1.2 -** Implement the validity rules and run the unphysical corpus, recording per-member validity classes; the corner case is a submission that is both unphysical and out-of-domain (the declared precedence between validity and domain classes, recorded verbatim from the rule), so no submission lands in an undefined verdict state.

- **B.1.3 -** Run the no-extrapolation inheritance check: the figure contract's rule text (N15) and the scorer's exclusion behavior are compared (the behavior implements the text, asserted by the boundary fixtures), and the inheritance proof is recorded, binding the figure layer and the scoring layer into one rule.

**Main Step C - Prove keyboard parity end to end and close the task.** Prove input parity end to end: the parity matrix runs the full vector set twice (once with pointer-produced payloads, once with keyboard-produced payloads, both scripted through the capture component), and every pair of verdicts matches, recorded as the parity table with digests, since the roadmap's accessibility commitments (N33's program, the WCAG-aligned input semantics of N22) rest on this proof: a keyboard-only learner is graded by identical rules with identical tolerance; the engine's verdict records are replayed from the ledger (three sampled verdicts reconstructed from their records alone, matching the original verdicts, recorded), demonstrating auditability.

**Subtask C.1 - Close with the harness binding and budget accounting.** The closure binds the engine to the frozen contract: the full graph vector set (reading and drawing) passes in both languages where the Python twin exists (the scorer's twin reuses the N05 policy), the digests enter the ledger, the engine's public contract (payload schema, verdict record schema, cited-entry rule, the inherited rule verbatim) is frozen for N23 and N20, and the runtime budget measurement (the engine's compiled share against the 120-220 KiB runtime sub-budget from Section 1) is recorded; the smoke subset gains one graph vector, and the task closes with the simulator's interpretation layer complete.

- **C.1.1 -** Run the parity matrix (pointer and keyboard produced payloads over the full vector set, verdict pairs compared) and record the table and digests; any pair divergence fails by vector id and blocks closure, since input parity is this task's signature commitment.

- **C.1.2 -** Run the verdict replay proof (three sampled verdict records reconstructed from their stored geometry and citations alone, matching the original verdicts) and record it, demonstrating the audit trail; then run the cross-language comparison where the twin exists and record the digests.

- **C.1.3 -** Author the frozen scoring contract and record its digest, run the budget measurement, append the engine, tables and parity digests to the ledger, run the extended corpus twice for parity, extend the smoke subset with the graph vector, and close the task.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the reading scorer, when the graph vectors run, then reading entries grade verdict-for-verdict with both tolerance classes enforced (a scratch out-of-tolerance reading grades outside), and pointer and keyboard payloads digest equal for identical lines.

- **AC2 (negative or edge case):** Given the drawing scorer, when the drawing vectors and unphysical corpus run, then near-miss and span-exclusion vectors grade per the inherited rule (beyond-span geometry unassessed, the boundary inclusive), validity classes cover every unphysical member with the precedence recorded, and the rule text matches the behavior.

- **AC3 (domain integrity and zero-regression):** Given the parity matrix and closure, when both input paths run the full set, then all verdict pairs match, sampled verdict records replay from stored data alone, the contract freezes for N23 and N20, the budget stays inside the declaration, and the smoke vector passes.

**Verification and Evidence:** Record the reading and drawing verdict-for-verdict tables with per-class tolerance coverage, the payload parity digests, the validity corpus with the precedence rule, the boundary fixtures with the inheritance proof, the parity matrix with digests, the replay proof, the cross-language digests, and the budget measurement. The frozen scoring contract digest enters the ledger.

**Risks, Guardrails, and Rollback Plan:** Risk: tolerance fields drifting from the figures as N20 reparameterizes variants. Guard: the scorer resolves conventions entries at scoring time and the vector set includes reparameterized-range vectors per the N14 declared ranges. Rollback: the engine is additive; removal leaves graph responses unscored and N23's graph pathway, N20's graph items and N33's keyboard program without their foundation, so those tasks must re-plan.

**Definition of Done:** A validity-first, tolerance-audited, input-agnostic graph scoring engine exists for reading and drawing against criterion shapes, inheriting the no-extrapolation rule verbatim, proven verdict-for-verdict with keyboard-pointer parity, replayable verdicts, a frozen contract and full ledger evidence.

### N19 - Author the method cards and implement the ordering, matching and sequence verdict engines

**Phase:** Phase IV | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N05, N09, N16

**Domain:** Method cards and non-numeric verdict engines

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the misconception taxonomy and its feedback strings (N09) exist; the worked chains (N16) exist with their citation discipline; the schema (N04) declares the ordering, matching and sequence response types; the golden corpus (N05) includes verdict vectors for these types; the masters teach procedural sequences (the inspection's method material: the titration procedure, the dilution sequence, the safety order). No method cards and no ordering, matching or sequence verdict engines exist for this simulator.

**Purpose and Rationale:** The method cards teach the procedures the colloquium's method questions probe: one card per taught procedure (the titration method, the dilution preparation, the solution preparation order, the calorimetric procedure and the others the coverage island assigns), each card authored as data (the ordered critical steps, each step's reasoning and its misconception-linked note, the safety entries where the masters teach them, the referenced worked chain from EX01-EX14 as the card's numeric companion), rendered with the same collapse-and-reveal discipline as the chains; the verdict engines grade the three non-numeric response types the schema declares: ordering (a learner sequences the steps, graded by the declared order with per-step verdicts, since a method's wrong step is diagnosable, not just wrong overall), matching (a learner pairs items across two lists, graded per pair), and sequence completion (a learner fills the next step with the declared acceptance set), all deterministic, all mapped to the N09 signatures, and none using keyword matching: the grading consumes structural comparisons (order positions, pair identities, step ids), never string similarity, so the verdicts are exact and the feedback names the misconception behind the wrong order or pair, not a spelling complaint.

**Target Artifacts and Touchpoints:** The method card data format; data/method_cards.json; the ordering, matching and sequence verdict engines. Touchpoints in output/simulator.html: the concept drawers' method slots, the method-type response components (N22), the grading pathways (N23), the remediation links (N28), the practice method items (N20).

**Out of Scope:** No free-text grading (a learner's own words in a critical-step explanation are self-assessed, never parsed: the pending semantics from the schema apply, the engine returns no verdict on them); no safety claims beyond the masters' own teaching (the safety entries cite their anchors, no invented precautions); no partial-order tolerance (an order is per-step right or wrong, per the declared rule, with no almost-ordered verdicts).

**Main Step A - Author the method cards and their data format.** Define the method card format (id, procedure name key, the ordered step records with each step's id, reasoning text, misconception note link and optional safety entry, the referenced chain id, the anchor citations) and author the cards for the procedures the coverage island assigns, each card's step order fixed by the masters' teaching (cited per card), each step's reasoning recomputable where it is numeric (the card's quantities flow through the N17 engine's contract or cite the chains), and each card linked to its EX chain; the copy lint runs over all card text (the N10 term grammar for any unit strings, the N09 feedback lint for the misconception notes).

**Subtask A.1 - Prove card completeness and citation integrity.** Prove the cards: the completeness validation (every coverage outcome that declares a method skill has its card, every card's steps are non-empty and totally ordered with unique step ids, every chain and anchor reference resolves, recorded per card), and the corner case of a procedure with a deliberately reorderable pair (two steps whose physical order the masters leave free, like two independent preparation steps), handled by the declared free-order group (the steps declared orderable among themselves, graded either way), authored into one card deliberately so the grading never penalizes the masters' own freedom.

- **A.1.1 -** Define the format and author the titration and dilution cards (the two procedures with the deepest step lists), and record the citation validation and the chain-link resolution, plus the free-order group's demonstration on the dilution card.

- **A.1.2 -** Author the remaining cards (solution preparation, calorimetry, and the others the island assigns), and record the completeness validation (outcome-to-card coverage, unique step ids, total order with the free-order exception), with the anchor table per card.

- **A.1.3 -** Run the copy lint over all card text (term grammar, feedback lint, the safety entries' citation check) and record the pass, with the safety discipline noted: no invented precautions, every safety entry citing its master anchor.

**Main Step B - Implement the three verdict engines with structural grading.** Implement the ordering engine: a submission (a permutation of step ids) grades per-step (each position compared to the declared order, the free-order groups compared as sets), returning per-step verdicts with the wrong steps' misconception signatures (a wrong step position maps to the signature its note names, like the rinse-with-solution misconception behind a wrong burette preparation step); implement the matching engine: a submission (pairs across two lists) grades per pair (identity comparison, exact), with unmatched or repeated pairs returning their declared verdict classes; implement the sequence engine: a next-step submission grades against the declared acceptance set (step ids, exact identity), with distractor steps (plausible but wrong next steps drawn from the N09 registry) returning their signatures; all three engines consume the N05 verdict vectors verdict-for-verdict, and none contains a string comparison beyond id equality (the no-keyword rule enforced by the engines' code review and the vector set's adversarial members: near-synonym submissions that must not pass).

**Subtask B.1 - Prove determinism, signature mapping and the no-keyword rule.** Prove the engines: the N05 vectors for all three types grade verdict-for-verdict (recorded, including the adversarial near-synonym members, which must fail: a submission using a synonym of the correct step name must not pass, proving id-based grading), the determinism proof (the same submission graded twice produces identical verdict records, digested), and the signature mapping validation (every wrong-verdict class maps to an existing signature with a resolving feedback string, zero dangling, recorded), since the engines' value is not the binary verdict but the diagnosis.

- **B.1.1 -** Implement the ordering engine with per-step and free-order grading, and run its vector pass (verdict-for-verdict with the near-synonym adversarial member failing), recording the table; the corner case is the transposed pair (two adjacent steps swapped, the classic near-miss), graded per-step with both steps marked and their signatures returned, recorded as the demonstrated diagnosis case.

- **B.1.2 -** Implement the matching and sequence engines, and run their vector passes with the same adversarial discipline (synonym pairs failing, distractor signatures resolving), recording the tables and the determinism digests.

- **B.1.3 -** Run the signature mapping validation across all three engines and record the zero-dangling pass, plus one full feedback trace (a transposed-pair submission producing both signatures' strings, rendered and recorded), demonstrating the diagnosis contract end to end.

**Main Step C - Integrate self-assessment semantics and close the task.** Integrate the self-assessment semantics: the method cards' critical-step explanations (a learner marks a step as critical and writes why) are self-assessed only: the response records the learner's text and a pending state (the schema's declared semantics, verified in N04), the engines never parse it, and the grading surfaces it as pending in the N23 classes; the fixture proves the boundary (a self-assessment submission produces a pending record, no verdict, no string comparison anywhere, recorded), since the roadmap's honesty about what can be graded depends on this boundary holding; the integration continues with the map slots (the method cards open from their outcomes, focus honored), the remediation links (N28's contract: a wrong ordering verdict links to the card's step note), and the practice items (N20's method items referencing the cards).

**Subtask C.1 - Close with cross-reference validation and budget accounting.** The closure runs the cross-reference validation (every method-type practice instance references an existing card, every card is referenced by at least one outcome and one item, recorded as the bidirectional reference table), the budget measurement (the cards' data and the engines' compiled share against the declared sub-budgets), and the smoke subset gains one ordering vector (a fixed transposed submission's per-step verdict record asserted in-file); the ledger records the format, cards, engines, vector tables and digests, and the frozen interface (the verdict record schemas, the signature mapping, the pending semantics) is handed to N22, N23, N28 and N20.

- **C.1.1 -** Run the self-assessment boundary fixture (a critical-step explanation submission producing a pending record with no verdict and no string comparison, recorded) and freeze the pending semantics in the interface contract for N23's grading classes.

- **C.1.2 -** Run the map-slot and remediation integration fixtures (focus traces for the card drawers, the wrong-verdict link path to the step note) and record them, plus the bidirectional cross-reference table over cards, outcomes and items.

- **C.1.3 -** Run the budget measurement, append the cards, engines, tables and traces to the ledger, run the extended corpus twice for parity, extend the smoke subset with the ordering vector, and close the task with the interface contract digest recorded.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the method cards, when completeness and citation validation run, then every method-skill outcome has its card, step ids are unique with total order (the free-order group demonstrated), all chain and anchor references resolve, and the copy lint passes.

- **AC2 (negative or edge case):** Given the three verdict engines, when the N05 vectors run, then all three types grade verdict-for-verdict (near-synonym adversarial members fail, the transposed pair yields both signatures), grading is deterministic by digest, and zero signature mappings dangle.

- **AC3 (domain integrity and zero-regression):** Given the closure proofs, when the boundary, integration and cross-reference fixtures run, then self-assessment submissions stay pending with no parsing, card drawers honor focus, remediation links resolve, references are bidirectional, budgets hold, and the smoke vector passes.

**Verification and Evidence:** Record the card validation tables, the per-engine verdict-for-verdict tables with adversarial members, the determinism digests, the signature mapping pass with the feedback trace, the pending-semantics boundary fixture, the focus traces, the bidirectional reference table, and the budget measurements. The frozen interface contract digest enters the ledger.

**Risks, Guardrails, and Rollback Plan:** Risk: method card step orders drifting from the masters' teaching. Guard: every card's order cites its anchor, and the citation validation is build-gated. Rollback: the cards and engines are additive; removal empties the method slots and the method-type grading pathways, but N23, N28 and N20 depend on the verdict record schemas, so those tasks must re-plan if the interface is withdrawn.

**Definition of Done:** Citation-complete method cards with free-order honesty and structurally graded ordering, matching and sequence verdict engines exist, deterministic and signature-mapped with no keyword matching anywhere, self-assessment kept honestly pending, integrated with the map, remediation and items, and evidenced in the ledger.

### N20 - Implement the variant engine and author the 112-instance practice bank

**Phase:** Phase IV | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N04, N16, N17, N18, N19

**Domain:** Variant generation and the frozen practice bank

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the schema and loader (N04) declare the instance format; the engines (N17, N18, N19) exist with frozen contracts; the chains (N16) exist as teaching links; the PRNG policy (N05) exists for deterministic reparameterization; the inspection's training-policy proposal declares 28 families (FAM-1A through 7D) with 4 variants each, 112 target instances, and per-topic point and minute budgets. No variant engine, no practice bank and no review workflow exist for this simulator.

**Purpose and Rationale:** The variant engine generates practice instances: a family declares its template (the response types from the schema, the conventions entries it consumes, the reparameterization ranges declared by the figure contracts in N14 and N15 and the engine contracts in N17-N19), and the engine instantiates a variant by drawing parameters from the declared ranges through the seeded PRNG (the N05 policy, deterministic per seed, so any variant is reproducible from its family and seed alone); the 112-instance bank is then authored to completion (28 families times 4 variants), each instance validated against the schema, recomputed where numeric (every numeric instance's key values flow through the N17 engine or the N18 vectors' criterion discipline, with the recompute recorded per instance), reviewed through the workflow (authored, validated, reviewed, accepted: no instance enters the bank without the review state, and the review checks are mechanical where possible and human-signed where not), and frozen as the #sim-bank island with its digest in the ledger; the engine additionally produces ephemeral runtime variants for practice retries (a learner retrying a family gets a fresh seed's instance, generated at runtime from the same templates, never persisted, never entering the frozen bank), so practice is unbounded while the graded bank stays frozen and auditable.

**Target Artifacts and Touchpoints:** The variant engine module; the 28 family templates; data/bank.json (112 instances); the review workflow records; the frozen #sim-bank island with digest. Touchpoints in output/simulator.html: the practice paths (N30), the remediation retries (N28), the exam assembly (N24, consuming the frozen bank's forms), the analytics (N25, consuming the instance and family ids).

**Out of Scope:** No runtime mutation of the frozen bank (the island is build-time authored; retries use the ephemeral path exclusively); no family template without engine-validated ranges (a range outside the declared tolerance reach of N17-N19 is a template validation failure, not a runtime surprise); no official exam claim (the bank is training material, the honesty banner applies, and the exam mode's assemblies are training-policy simulations per the Section 1 split).

**Main Step A - Implement the variant engine and the 28 family templates.** Implement the variant engine: a family template declares its id (FAM-1A through 7D, the inspection's naming verified), its topic and point weight (the training-policy proposal's per-topic budgets, labeled as proposal), its response type mix (the schema's eighteen types, with the required types Q02, Q04, Q10, Q11, Q12, Q13, Q15 present per the proposal), its parameter declarations (each parameter: its range, its conventions entry where it is a constant-bound value, its engine path where it is computed), and its instance seed policy (the N05 PRNG, the seed recorded per instance); the engine instantiates a variant by drawing the parameters, computing the derived values through the engine contracts (N17 for numeric, N18's criterion discipline for graph families, N19's structural templates for method families), and emitting a schema-valid instance.

**Subtask A.1 - Prove template validity and deterministic instantiation.** Prove the templates: the template validation (every family's parameters within the declared ranges of the engine contracts, every consumed conventions entry resolving, every response type existing in the schema, the required types present across the proposal's distribution, recorded per family), and the determinism proof: instantiating the same family with the same seed twice produces byte-identical instances (digested, recorded), and the cross-language proof where the twin exists (the Python authoring twin and the runtime engine producing identical instances from identical seeds, recorded), since the bank's auditability rests on this reproducibility.

- **A.1.1 -** Implement the engine core (parameter drawing, derived-value computation through the contracts, schema emission) and run the determinism and cross-language proofs with digests recorded; a scratch template with an out-of-range parameter fails validation by family and parameter name, proving the range gate.

- **A.1.2 -** Author the 28 family templates (FAM-1A through 7D, spanning the seven topics with the proposal's type distribution), and record the per-family validation table (ranges, entries, types, required-type coverage), with the proposal labeling carried (the training-policy split from Section 1, verified in the template metadata).

- **A.1.3 -** Run the required-type coverage check across the full template set (the proposal's required types present, their families named) and record it; the corner case is a family whose graph component needs a reparameterized figure (the N14 declared ranges), and the template's figure parameter block is validated against those ranges, recorded as the demonstrated coupling.

**Main Step B - Author and review the 112-instance bank.** Author the bank: instantiate the four variants per family (the seeds drawn and recorded per instance), validate every instance against the schema (the N04 loader, zero failures, recorded), and recompute the numeric instances (every key value flowing through the N17 engine or the N18 criterion discipline, the recompute table recorded per instance), so no instance enters the bank whose answer was not independently produced by the same authority that will grade it; run the review workflow: each instance's review record (authored, validated, recomputed, reviewed, accepted, with the reviewer's mechanical checks named and the human sign-off line present), and the workflow gate refuses the build if any of the 112 lacks the accepted state (the review completeness is a build gate, not a convention).

**Subtask B.1 - Prove bank completeness and grading alignment.** Prove the bank: the completeness check (112 instances, 28 families, four per family, per-topic distribution matching the proposal's budgets, recorded), the grading alignment spot-check (a sample of instances across all response types graded by their engines with the expected verdicts, verdict-for-verdict where vectors exist, recorded), and the leak scan (the N12 engine over the practice instances: no instance's key values appear in its own non-key fields or its figure records without a declared exemption, recorded per instance), since a practice bank that leaks its own answers trains recognition, not chemistry.

- **B.1.1 -** Instantiate the 112 instances and run the schema validation and the recompute table (per instance, zero failures, the engine path named per value), and record the per-family instance counts and the seed table.

- **B.1.2 -** Run the review workflow over all 112 (the mechanical checks: schema, recompute, leak scan, range compliance; the human sign-off line per instance) and record the workflow gate's pass; a scratch unreviewed instance refuses the build by id, proving the gate.

- **B.1.3 -** Run the grading alignment spot-check (sampled across all types and engines) and the leak scan with reasoned exemptions, recording both; the corner case is a graph instance whose criterion values are visually near a figure's labeled values (the borderline significance rule from N12 applies), recorded as the demonstrated exemption case.

**Main Step C - Freeze the bank island and prove the ephemeral retry path.** Freeze the bank: the instances serialize into the #sim-bank island (the build-time artifact), the island's digest is computed and recorded in the ledger (the frozen-bank contract: any bank change is a new digest and a deliberate act), and the runtime loader's integrity check (the loader verifies the island's digest at load, failing honestly on mismatch) is implemented and fixture-proven; implement the ephemeral retry path: a practice retry draws a fresh seed (excluding the seeds of the frozen variants, per the declared exclusion rule), instantiates at runtime through the same templates and contracts, grades through the same engines, and never persists (the in-memory session default from AGENTS.md honored), so the retry path is unbounded practice while the graded artifact stays frozen.

**Subtask C.1 - Close Phase IV with the handoff contracts.** The closure proves the two paths' equality: the parity fixture (an ephemeral instance and a frozen instance of the same family, graded by identical engine code, the code path compared and the contract identity recorded), the ephemeral determinism (the same retry seed reproducing the same ephemeral instance, digested), and the exclusion rule's proof (a retry seed colliding with a frozen seed being excluded, recorded); the smoke subset gains one bank vector (a fixed instance's grading verdict asserted in-file), and the task closes Phase IV with the handoffs frozen: the bank digest and instance ids to N24 (exam assembly), the ephemeral path and family templates to N28 and N30 (remediation and bounded practice), the grading surfaces to N23.

- **C.1.1 -** Freeze the island, record the digest, and prove the loader's integrity check (a scratch tampered island failing honestly by digest mismatch), so the frozen bank is tamper-evident at runtime, not merely at build.

- **C.1.2 -** Implement the ephemeral retry path with the seed exclusion rule and prove its determinism and exclusion fixtures (the retry-seed reproduction digest, the collision exclusion), plus the parity fixture (identical engine code for both paths, recorded), so practice equality between frozen and ephemeral instances is demonstrated.

- **C.1.3 -** Run the smoke vector, append the bank, templates, workflow records, digests and fixtures to the ledger, run the extended corpus twice for parity, record the bank's byte contribution against the bank sub-budget (200-420 KiB from Section 1, the measured share recorded), and close the task and Phase IV.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the 28 family templates and the engine, when validation and determinism proofs run, then every template's ranges, entries and types validate (an out-of-range scratch template fails by name), required types cover the proposal, and identical seeds yield byte-identical instances across languages where the twin exists.

- **AC2 (negative or edge case):** Given the 112-instance bank, when schema, recompute, review and leak checks run, then all instances validate with recomputed key values, the workflow gate passes (an unreviewed scratch instance refuses the build), grading aligns on the sample, and no key leaks without reasoned exemption.

- **AC3 (domain integrity and zero-regression):** Given the frozen island and ephemeral path, when integrity, parity and exclusion fixtures run, then the loader rejects a tampered island by digest, retries are deterministic with frozen-seed exclusion, both paths grade through identical engine code, the smoke vector passes, and Phase IV's handoff contracts are frozen.

**Verification and Evidence:** Record the per-family template validation table, the determinism and cross-language digests, the per-instance schema and recompute results, the seed table, the workflow gate pass with the scratch refusal, the grading alignment sample, the leak scan with exemptions, the island digest with the tamper fixture, the retry fixtures, the parity record, and the bank sub-budget accounting.

**Risks, Guardrails, and Rollback Plan:** Risk: the frozen bank drifting from the family templates during later edits. Guard: the island digest is the ledger's frozen reference, and any regeneration is a deliberate, recorded act. Rollback: the engine and bank are additive; removal leaves practice and assembly without items, and N24, N28 and N30 depend on the bank digest and ephemeral contract, so those tasks must re-plan.

**Definition of Done:** A deterministic, contract-validated variant engine over 28 reviewed family templates and a frozen, tamper-evident 112-instance practice bank exist, recomputed and leak-scanned with workflow-gated acceptance, an unbounded ephemeral retry path through identical engine code, and the bank digest, instance ids and ephemeral contract frozen for exam assembly, remediation and bounded practice.


## 11. Phase V (N21-N25) - Exam Flow, Input Semantics, Grading, Fair Sampling and Local Analytics

Phase V builds the examination experience as an honest training simulation: the exam shell with its advisory timer, navigation, flags and strict help refusal (N21); the response input semantics for all eighteen types with full ARIA contracts (N22); the error-classification and partial-credit grading engine with the confirmed, self and pending classes (N23); the seeded, fair A/B/C assembly that reproduces from seed keys and fails loudly on shortage (N24); and the local, privacy-safe analytics with the versioned opt-in store and the recorded F10 rejection boundary (N25). When this phase closes, a learner can sit a full training examination and receive a graded, diagnosed, reproducible result with no data leaving the machine.

### N21 - Build the exam shell: timer, navigation, flags and view discipline

**Phase:** Phase V | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N06, N16, N20

**Domain:** Exam mode runtime

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the blueprint declares a 100-point, 21-slot, three-form training policy and the programme's 180-minute official maximum; AGENTS.md demands in-memory sessions by default and forbids official-exam claims; the bank (N20) and worked chains (N16) exist as prior deliverables. No timer, slot navigation, flagging or view-discipline component exists in any runtime form.

**Purpose and Rationale:** The exam shell is the container every graded interaction lives in: a training-policy exam session of 21 slots with an advisory timer (explicitly labeled izglītojošs, never claiming official timing rules), slot navigation with jump and question map, per-slot flags, answer mutability before submission, and the boundary discipline that leaks nothing (hints, method cards and worked chains never render inside exam mode, while practice keeps them).

**Target Artifacts and Touchpoints:** src/exam.ts and src/session.ts modules; the session lifetime contract. Touchpoint in output/simulator.html: the `#eksamens` section, the timer bar, the slot navigator and question map, the review-and-submit screen.

**Out of Scope:** No server, account or telemetry of any kind; no attempt to reproduce official exam software; no persisting of answer content to localStorage without an explicit learner opt-in recorded per the settings view (N06).

**Main Step A - Implement the session state machine.** Implement the exam session as an explicit state machine: not-started, running, review, submitted, expired, aborted; events are start, navigate, flag, answer, request-review, submit and the timer expiry; the machine holds the assembled form (from N24), the answer map, the flag set and the elapsed time, and its transition table is fixture-tested like every other machine in this roadmap; answers are mutable only before submit, and the machine rejects any mutation after submitted (a structural guard against late writes, not a UI convention).

**Subtask A.1 - Prove the lifecycle and late-write guard.** Fixture the complete lifecycle (start to submit, the flag toggles, a late-write attempt rejected with a stable error id, an expiry mid-session transitioning to expired with answers preserved for the report), record the transition table run, and prove the machine is the only writer: the DOM contract tests that no component mutates the answer map directly, only through session events.

- **A.1.1 -** Implement the timer contract: elapsed time from a monotonic clock, the advisory limit from the training-policy island, a threshold indicator (for example at 90 percent elapsed) rendered as status only, expiry triggering the expired transition, and tab-hidden behavior defined (the timer keeps counting, matching the policy that the limit is advisory and honest elapsed time is honest elapsed time); fixture the threshold and expiry transitions with a mock clock.

- **A.1.2 -** Implement the answer map with per-type payloads (the Q11 record, Q13 vector, Q17 pairs, Q18 plot state, numeric strings raw and unparsed), each stored as the learner typed or constructed it, never normalized in storage (normalization belongs to grading), and fixture round-trip serialization: a session serialized and deserialized yields identical answers, which N34's storage layer will depend on.

- **A.1.3 -** Implement the view discipline as a machine-level rule: while state is running or review, the render contract excludes hint, method-card and worked-chain components entirely (not merely hides them), and the fixture serializes the exam DOM and asserts the absence of those component markers plus the absence of any N16 chain step text; the corner case is a remediation link inside exam feedback, which cannot exist pre-submit by design and is instead recorded as a post-exam remediation list (consumed by N28).

**Main Step B - Implement navigation, flags and the review screen.** Implement slot navigation: previous/next controls, the question map (21 cells with answered, flagged and current states), keyboard navigation (arrow keys between slots, per the accessibility contract), a per-slot flag toggle with its stable state, and the review-and-submit screen: a summary table of all 21 slots (answered or not, flagged or not), an unanswered warning before submit, and a final submit requiring explicit confirmation; submission is one-way by design and labeled as such.

**Subtask B.1 - Prove navigation completeness and the submission gate.** Fixture the navigation contract: every one of the 21 slots is reachable by both pointer and keyboard-only paths, the map states match the session exactly after a scripted answer/flag sequence, and the submit gate blocks when the confirmation is absent; the corner case is rapid navigation during a re-render, which must never lose an in-progress answer (the machine buffers by slot id), and that race fixture is recorded.

- **B.1.1 -** Implement the map and controls as pure functions of session state (the rendering contract), and record the scripted-sequence fixture: answer slots 1, 5 and 21, flag 3, navigate the full range, then verify the serialized map equals the expected state array; the deterministic fixture doubles as N32's responsive test data.

- **B.1.2 -** Implement the keyboard contract (focus management per slot, arrows for slot movement, the documented shortcut for flag, focus never trapped in a widget), and fixture the keyboard-only traversal: a scripted keyboard run answers and flags across all 21 slots without a single pointer event, giving N33 its precondition evidence.

- **B.1.3 -** Implement the review screen's honesty copy (this is a training-policy summary, not an official result document) and the unanswered warning with its accessible alert role, fixture the warning's appearance and dismissal, and record that the final submission writes the terminal session record (answers, flags, elapsed time, form id) that N23 grades and N25 logs.

**Main Step C - Integrate the shell and prove mode boundaries.** Integrate the shell with the assembled form loader (N24), the practice-mode contrast (practice sessions reuse the same components with hints and chains enabled), and the entry gate from the start screen; then prove the two mode boundaries end to end: exam contains no help surfaces, and practice help surfaces never read exam session data, fixture-verified in both directions.

**Subtask C.1 - Prove boundary isolation both ways.** The two-way boundary fixture is this substep's completion proof: an exam render contains zero help-component markers (recorded), and a practice render immediately after an exam session contains zero exam-session fields (the practice view cannot see the exam answer map), demonstrating that the isolation is architectural, not cosmetic.

- **C.1.1 -** Implement the mode registry (a single source mapping mode to allowed component sets, machine-checked by the render contract), and record the registry fixture: exam allows the input, timer, navigator, map and review components; practice additionally allows hints, chains, method cards and term lookups; any unregistered component in a mode fails the contract test loudly, which is how mode creep gets caught.

- **C.1.2 -** Run the end-to-end scripted session: start screen entry, full navigation, answers of several types (numeric, classification, ordering), flags, review, confirmed submit, and terminal record emission, all with the mock clock; record the session trace as N23 and N25's integration input, with every transition conforming to the fixture table.

- **C.1.3 -** Append the shell module digests and session trace to the ledger, record the in-file smoke extension (one state-machine transition vector and one navigation vector), and record the runtime byte contribution against the budget, closing the container with the same evidence chain as its contents.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the state machine fixtures, when the lifecycle runs (including late write, expiry and the buffer-race corner), then every transition matches the table, late writes are rejected with stable error ids, and no in-progress answer is lost.

- **AC2 (negative or edge case):** Given the scripted answer/flag sequence, when the map and review render, then map states match the session exactly, all 21 slots are keyboard-reachable, and submission requires explicit confirmation with the unanswered warning present.

- **AC3 (domain integrity and zero-regression):** Given the two-way boundary fixture, when exam and practice render, then exam output contains zero help markers, practice output contains zero exam-session fields, and the unregistered-component check fails loudly on a scratch violation.

**Verification and Evidence:** Record the transition table run, mock-clock timer fixtures, serialization round-trips, navigation and keyboard fixtures, the two-way boundary outputs and the scripted session trace. The advisory-timer label copy is recorded verbatim; no component mutates session state outside the machine (contract test recorded).

**Risks, Guardrails, and Rollback Plan:** Risk: timer drift against wall-clock changes. Guard: monotonic elapsed time with the mock-clock fixture; the timer is advisory by policy, so no exam outcome hangs on seconds. Rollback: remove the shell modules; N20-N24 artifacts are unaffected, but N23-N25 and N30 depend on the session contract and re-plan if it reverts.

**Definition of Done:** The exam shell runs the full lifecycle with a fixture-proven state machine, keyboard-complete navigation, flags and an explicit submission gate; mode boundaries are architectural and two-way proven; the terminal record contract feeds N23 and N25; digests, smoke vectors and session traces are in the ledger.

### N22 - Define response input semantics for all 18 types with full ARIA contracts

**Phase:** Phase V | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N17, N19, N21

**Domain:** Response capture and accessibility

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the 18 response types (Q01-Q18) are frozen in the blueprint with their completion rules and accessibility alternatives; the completed-types contract (Q02, Q04, Q10, Q11, Q12, Q13, Q15 per form) is defined; the engines emit the error taxonomy and criterion shapes. No response component, ARIA contract or completion-state model exists.

**Purpose and Rationale:** Every response type needs one defined component: how it renders, what it stores, when it counts as complete, what error states it can show (the four parse-error classes and structural errors from the engines), and its full ARIA semantics (roles, names, states, descriptions in Latvian). The types span one-line numeric input, multi-field entries, Q13 coefficient vectors, Q11 classifications, Q06 pairs, Q08 orderings, Q17 structures, Q18 plot interactions and the self-assessed critical-step explanation, and each must be operable by keyboard alone and readable by a screen reader, with the accessible alternatives the blueprint mandates.

**Target Artifacts and Touchpoints:** src/inputs/*.ts (the 18 response component contracts); the completion-state model. Touchpoint in output/simulator.html: every rendered response widget in exam and practice views, and the Latvian ARIA label bank.

**Out of Scope:** No custom free-text interpretation (the Q11 explanation stays self-assessed per N19); no drag-only interactions (select-based alternatives are mandatory); no visual-only state communication (every state has text or ARIA equivalence).

**Main Step A - Specify per-type semantics and completion rules.** Write the per-type specification as a data artifact (the response-type registry): for each of Q01-Q18, the render contract (fields, controls, option sources), the payload shape stored in the answer map (N21), the completion rule (exact field list: a Q13 vector completes only when all coefficients are non-empty, a Q18 plot completes at the declared point count, a Q06 set completes when every pair is assigned), the error states it can surface (mapped to the N17 taxonomy ids and structural ids), and its accessible alternative (the blueprint's mandate made concrete per type).

**Subtask A.1 - Make the registry the single source for renderers.** Every renderer in this task reads its contract from the registry, the validator asserts the registry covers all 18 types and that each completed-type (Q02, Q04, Q10, Q11, Q12, Q13, Q15) has both a render and grading binding, and the corner case of an unknown type id in an instance fails loudly at load, never renders a fallback text field (a fallback that silently changes the task's meaning is the worst-case bug class here).

- **A.1.1 -** Author the 18 registry entries with field-level ARIA names in Latvian (from the terminology island, term-keyed), each name recorded verbatim in the registry (for example a coefficient cell is named Koeficients priekš [species] with the species name substituted), and record the registry validation pass plus a scratch unknown-type rejection fixture with the type id named.

- **A.1.2 -** Implement the completion-state model as a pure function from payload to a completion verdict (complete, incomplete-with-missing-list, or invalid-with-error-list), and fixture it per type: the Q13 missing-coefficient case, the Q17 half-drawn structure, the Q12 read with value but no figure binding, and the Q18 short plot each yield their named missing list, which the navigator (N21) and the review warning consume.

- **A.1.3 -** Implement the error-surface mapping (registry entries declare which engine error ids they render, with the Latvian message templates keyed to the same ids N09 froze), and fixture a sample: entering a mixed-separator number shows the MIXED_SEPARATORS message on blur without clearing the learner's raw input (never destroy learner input on an error), recorded as the input-preservation invariant that all 18 types inherit.

**Main Step B - Implement the 18 components against the registry.** Implement each component as a thin renderer over its registry contract: numeric inputs (one-line and multi-field) storing raw strings, the classification grid, the pair matcher (select-based), the ordering strip (select-based per N19), the coefficient vector editor, the structure palettes (Q17, palette-and-place with an explicit keyboard placement path), the plot input (pointer plus the coordinate table from N18), the read declaration widget (Q12), the option-choice groups, the multi-part composed responses (any type can sit inside a composed instance per the blueprint), and the self-assessed explanation field (text area with its minimum-length and pending semantics).

**Subtask B.1 - Prove parity between keyboard and pointer paths.** For every component with a spatial or pointer-natural interaction (plot, structures, pairs, ordering), the fixture pair proves the keyboard path produces the exact same payload as the pointer path for the same intent: a scripted pointer session and a scripted keyboard session over identical tasks yield identical answer maps, which is the strongest operability guarantee available short of a live screen-reader run (N33 performs that).

- **B.1.1 -** Implement the components as pure functions of (contract, state, payload) returning a render description (the DOM stub pattern from N08), and record the render fixture for each of the 18: its field set matches the registry, its ARIA names match the term bank, and a scratch contract violation (a missing field) fails the fixture with the field named, keeping the registry authoritative rather than decorative.

- **B.1.2 -** Implement the keyboard interaction contracts per spatial component (the plot's table path, the structure palette's select-and-place keys, the ordering's select controls) and run the parity fixtures: for each spatial type, one scripted task answered twice (pointer and keyboard) with the two payloads asserted equal, recorded per type; the corner case is mid-interaction abort (a learner starts placing a bond and navigates away), where the component must discard the in-progress gesture and never emit a partial placement.

- **B.1.3 -** Implement the composed-response container (per-part labels, per-part completion states, the composed payload as an ordered map) and fixture a two-part instance (a calculation plus a read) with mixed completion: part one complete, part two incomplete yields the named missing list for part two only, which N23's per-criterion grading will consume.

**Main Step C - Integrate with the session and prove end-to-end capture.** Integrate every component with the session machine (the only writer), the navigator completion states and the review summary, and run the end-to-end capture fixture: one instance of each of the 18 types is answered through the component API in a scripted session, the payloads serialize, round-trip and grade through the criterion-shape inputs, proving the capture layer and the engines agree on payload semantics.

**Subtask C.1 - Prove the capture-grading contract.** The end-to-end proof is the payload-contract audit: for each of the 18, the stored payload, consumed by its engine, produces the recorded criterion shape without adaptation or coercion (any adapter needed would reveal a contract mismatch, and the audit must find none), recorded as the capture-grading parity table over all 18 types.

- **C.1.1 -** Run the 18-type scripted session (each type answered once, plus one deliberately incomplete case per completed-type group) and record the payload round-trip digests plus the grading shapes, forming the parity table; the corner case is the Q03 template response (restricted templates with manual rubric per the type contract), where the payload is the template choice plus the typed fill-ins, and grading runs the manual-rubric pending path rather than pretending auto-scoring.

- **C.1.2 -** Append the registry and component digests to the ledger, extend the in-file smoke subset with three input vectors (a numeric, a classification and an ordering), and record the label bank's term-key lint pass (zero literal unit strings, zero untranslated ARIA names), closing the task's integration evidence.

- **C.1.3 -** Record the input-layer byte contribution against the runtime budget and run the extended corpus twice for ledger parity, completing the capture layer that N23 grades, N24 assembles for and N33 tests with a live screen reader.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the response-type registry, when validation runs, then all 18 types have render, payload, completion, error and ARIA contracts; completed-types have grading bindings; and a scratch unknown type fails loudly at load.

- **AC2 (negative or edge case):** Given the pointer-keyboard parity fixtures for every spatial type, when both paths answer identical tasks, then payloads are asserted equal, in-progress gestures discard cleanly, and errors never destroy raw input.

- **AC3 (domain integrity and zero-regression):** Given the 18-type scripted session, when payloads round-trip and grade, then the capture-grading parity table shows all 18 types consuming payloads without adapters, and the smoke vectors pass in-file.

**Verification and Evidence:** Record the registry validation, per-type render fixtures, parity outputs, the 18-type session trace and the parity table. ARIA names come from the term bank (term-keyed, lint-recorded); the Q03 manual-rubric path is proven pending, not fake-scored.

**Risks, Guardrails, and Rollback Plan:** Risk: ARIA contracts drifting from implementation as widgets get polished. Guard: the registry is machine-checked against renders, and N33's live screen-reader pass is a release gate. Rollback: remove the input layer; the engines, session machine and bank are unaffected; N23-N25 and N33 re-plan against a reverted capture contract.

**Definition of Done:** All 18 response types have registry-driven components with keyboard parity, completion semantics, error preservation and Latvian ARIA contracts; the capture-grading parity table covers all 18; smoke, lint and ledger evidence is recorded; and N23 receives payloads it can grade without adaptation.

### N23 - Implement error classification and the partial-credit grading engine

**Phase:** Phase V | **Priority:** P0 | **Risk:** High | **Effort:** XL | **Dependencies:** N17, N18, N19, N21, N22

**Domain:** Grading engines: assembly of verdicts

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the three content engines (N17 quantity and balance, N18 graph, N19 sequence and matching) emit criterion shapes with signature channels; the misconception registry (N09) maps signatures to teaching feedback; the rubric structure (criterion-based points with partial credit) is defined in the blueprint's training policy. No grading engine, score aggregation or feedback assembly exists.

**Purpose and Rationale:** The grading engine assembles engine verdicts into per-criterion and per-task scores: each criterion carries its declared points, verdicts map to point fractions per the rubric policy (correct full, partial where the rubric declares it, incorrect zero, pending for self-assessed items), classification errors route to N09 feedback through signature ids, and the total honors the 100-point training-policy scale. The engine must be deterministic (same answers, same score, forever), must grade only through the frozen engine contracts (no ad-hoc tolerance logic, the rule from N17), and must never award points for unattempted or malformed responses.

**Target Artifacts and Touchpoints:** src/grading.ts (new engine); the feedback assembly contract. Touchpoint in output/simulator.html: the `#rezultati` results view, the per-task feedback cards and the remediation payload that N28 consumes.

**Out of Scope:** No curve adjustment, peer-norming or grade inflation of any kind; no silent forgiveness of parse errors (a malformed response scores zero with its error message, never a near-miss credit); no grading of self-assessed text beyond the pending state.

**Main Step A - Implement criterion aggregation and scoring.** Implement the grading engine over a terminal session record: for each slot, collect its instance's rubric (criteria with points and verdict rules from the bank), run the engine contracts for each criterion (quantity, balance, graph, sequence, matching verdicts with their shapes), map verdicts to awarded points per the declared rule (full, the documented partial fractions, zero), aggregate to the task score, then to the form total on the 100-point scale, and emit the graded record: per-slot criterion table, per-slot score, total, and the elapsed time and flag metadata carried from the session.

**Subtask A.1 - Prove aggregation with the score fixtures.** Fixture the aggregation across the score matrix: a fully correct form (100 points exactly, per-criterion all full), a partially correct form (selected partial-verdict slots with the declared fractions, summed by hand and compared), an all-incorrect form (zero with every criterion showing its verdict), and a mixed form with pending items (the Q03 manual-rubric slot shows pending and its points sit outside the auto-total, labeled as such, since pretending to auto-score a manual rubric is the honesty failure this design forbids).

- **A.1.1 -** Implement verdict-to-points as data (the rubric policy table, validated like every artifact: every verdict enum value that can occur has an explicit rule; the corner case is an unexpected verdict class arriving from an engine contract change, which must fail loudly with the criterion and verdict named, never default to zero silently, since a silent default would both mis-score and hide the contract break).

- **A.1.2 -** Implement the malformed-response rule (a payload that fails its own completion check or parse scores the criterion zero with the structural error surfaced, and the fixture proves the raw input is preserved in the record even while unscored, honoring the input-preservation invariant from N22), and run the fixtures: the mixed-separator answer, the truncated ordering and the empty coefficient each yield zero-with-named-error, never a partial credit.

- **A.1.3 -** Implement the total's honesty accounting: auto-scored points plus pending-external points (the manual-rubric and self-assessed criteria) shown separately in the graded record, so a learner seeing 72 of 100 auto-scored with 8 pending understands the true state, and the fixture asserts the two sums never blend; the same record drives N25's analytics with unblended fields.

**Main Step B - Implement error classification and feedback assembly.** Implement the classification layer: each engine verdict's signature list maps through the misconception registry (N09) to feedback items (the Latvian teaching text, the misconception name, the remediation links to N07 anchors and N16 chains), the feedback assembly orders items (task-level first, then per-criterion), and the assembled feedback record is part of the graded record; unmapped signatures are a validation failure (the zero-unmapped rule from N20 applied at grading time as well, since a signature that reaches a learner with no teaching text is a content bug).

**Subtask B.1 - Prove classification coverage over the whole bank.** Run the classification sweep: scripted wrong answers per error class (the thousand-fold slip, the comma error, the intercept drop, the swapped axes, the density-required mass-volume error, the wrong-medium balance) across representative instances, each producing its registry-mapped feedback with the correct Latvian text id, recorded as the classification table; the corner case is a verdict with multiple signatures (a value that is both sign-flipped and thousand-fold), where the assembly emits the most specific signature first per the registry's priority field, and the ordering fixture is recorded.

- **B.1.1 -** Implement the feedback assembly with the remediation payload contract (concept anchor ids from N07, chain ids from N16, all validated to exist by the same loader rules), and fixture the full pipeline: one graded mixed-form session emits feedback records whose every remediation link resolves, which N28 will consume directly as its input queue.

- **B.1.2 -** Implement the classification sweep runner and record the classification table over the scripted error corpus (roughly twenty scripted wrong answers covering every signature family), asserting zero unmapped signatures and zero unresolved remediation links; this table becomes N36's mutation-test baseline for the grading engine.

- **B.1.3 -** Implement the score-report render contract (per-slot rows, criterion details behind a disclosure, feedback cards with their honesty note that classification is training-policy feedback, not an official diagnosis), and record the render fixture for the mixed-form session: the DOM stub output shows the unblended totals, the pending labels and the feedback cards, which doubles as N32's visual test data for the results view.

**Main Step C - Prove determinism and integrate with analytics.** Prove grading determinism: the same terminal record graded twice, and in a fresh process, yields byte-identical graded records; grade the scripted corpus (the score-matrix fixtures plus the classification corpus) as one batch with a recorded digest; and integrate the graded record with N25's analytics (the same record, no re-scoring), closing the loop from answers to scores to feedback to log in one deterministic chain.

**Subtask C.1 - Prove the chain end to end.** The end-to-end proof is the chain fixture: session terminal record, graded record and analytics event log are all recorded for one scripted mixed-form session, with digests linking them (the analytics events reference the graded record's digest), so the three artifacts are provably about the same answers, and any later discrepancy investigation has an unbroken evidence trail.

- **C.1.1 -** Implement the determinism harness (grade twice, compare digests, fresh process, compare again) and record the three-way identical digests; the corner case is object-key-order instability in the graded record, which the engine eliminates by emitting canonically sorted records (the same canonicalization N04's loader uses), and the sorted-digest fixture proves it.

- **C.1.2 -** Run the batch digest over the scripted corpus and append the grading engine's module digests, the classification table and the batch digest to the ledger, extending the frozen chain from engines to scores.

- **C.1.3 -** Extend the in-file smoke subset with three grading vectors (full-credit, partial-credit and malformed-zero) and record the smoke pass plus the grading runtime's byte contribution against the budget, completing the scoring heart of the simulator with every verdict traceable to an engine, every point to a rubric rule, and every feedback item to a registry entry.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the score-matrix fixtures, when the engine grades them, then the totals equal the hand-computed sums (100, partial, zero), pending items stay external to the auto-total, and malformed responses score zero with named errors and preserved raw input.

- **AC2 (negative or edge case):** Given the scripted error corpus, when classification runs, then every signature maps to registry feedback with zero unmapped entries, multi-signature verdicts order by the registry priority, and every remediation link resolves.

- **AC3 (domain integrity and zero-regression):** Given the determinism harness, when grading runs twice plus a fresh process, then graded-record digests are identical, the batch digest covers the corpus, and the chain fixture links session, graded record and analytics by digest.

**Verification and Evidence:** Record the rubric policy validation, score-matrix runs, classification table, determinism digests, the chain fixture and smoke counts. Every awarded point traces to a criterion rule; the engine contains no tolerance logic of its own (contract test: the grading module imports only engine contracts).

**Risks, Guardrails, and Rollback Plan:** Risk: partial-credit rules drifting into leniency under authoring pressure. Guard: fractions are declared data validated against the blueprint's rubric, and changes are visible version events; the zero-silent-default rule catches contract drift loudly. Rollback: remove the grading engine; engine contracts, session records and feedback registry remain; N25-N30 re-plan against a reverted scoring contract.

**Definition of Done:** Grading is deterministic, rubric-driven and honest (pending external, malformed zero with preserved input); classification covers every signature with resolvable remediation; the chain from session to analytics is digest-linked; smoke and ledger evidence is complete.

### N24 - Implement seeded, fair A/B/C form assembly

**Phase:** Phase V | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N05, N20, N21

**Domain:** Form assembly

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the blueprint's training policy declares three forms (A, B, C), 21 slots each, with the per-topic slot counts, per-topic points and the required completed-types (Q02, Q04, Q10, Q11, Q12, Q13, Q15) per form; the bank (N20) exposes review-state eligibility and the family structure; the PRNG policy (N05) is frozen with cross-language parity. No assembly algorithm exists.

**Purpose and Rationale:** Form assembly converts the frozen bank into three comparable forms: each form draws its 21 slots from distinct families (a family appears at most once per form, so a learner who sat form A never re-met the same family's variant in that form), honors the per-topic slot and point totals (the 100-point scale lands exactly on every form), satisfies the completed-type requirements, and uses the frozen PRNG so the assembly is deterministic and reproducible while remaining fair across families (every family cycles into forms across seeds, no family permanently exiled to one form).

**Target Artifacts and Touchpoints:** src/assembly.ts (new module); the three form manifests. Touchpoint in output/simulator.html: the form picker on the start screen (A, B, C and a seeded training option) and the assembly island data.

**Out of Scope:** No adaptive difficulty engine (F08 stays deferred by policy); no claiming the three forms mirror official form construction; no assembly from unreviewed instances (the eligibility gate is absolute).

**Main Step A - Implement the assembly algorithm.** Implement assembly as a constraint-driven draw: inputs are the bank's eligible set (review-passed instances only), the slot map (21 slots with their topic and type constraints), the point map, the family-uniqueness constraint and the form's target seed; the draw runs the frozen PRNG over family-order permutations within topics, assigns instances to slots, verifies the completed-type coverage (each required type appears in each form), and emits the form manifest: slot list with instance ids, topic and type labels, per-topic point subtotals and the form seed, all canonically sorted for the digest.

**Subtask A.1 - Prove the three forms satisfy every constraint.** Assemble A, B and C and run the verifier: 21 slots each, exact per-topic slot counts, exact per-topic point subtotals (the three forms' totals all equal 100), family uniqueness within each form, completed-type coverage in each, and eligibility (every drawn instance review-passed); the negative fixtures are a scratch assembly over an artificially shrunken eligible set (the shortage path), which must fail with the binding constraint named, never silently relax a constraint to succeed.

- **A.1.1 -** Implement the constraint checker as an independent function (assembly code and verification code share no logic, the same independence discipline as N05's oracle), and record its verdicts over the three forms; the corner case is a topic whose eligible instances exactly equal its slot count (no slack), where the draw is deterministic and the checker still passes, plus a one-instance-short scratch set that fails with topic and slot count named, proving the checker would catch a real shortage.

- **A.1.2 -** Implement family fairness across forms: over the recorded seed cycle (for example ten consecutive assembly seeds), every family appears in at least one form and none appears in all three forms at the same slot, recorded as the fairness sweep; the PRNG determinism proof regenerates all thirty forms (three times ten seeds) with identical digests, reusing N05's parity harness pattern.

- **A.1.3 -** Implement the seeded training option (the learner-facing pick: a specific form, or a seeded draw for practice with the same constraints but ephemeral variants allowed from N20's runtime path), and fixture it: five seeded draws each validate against the same checker, with ephemeral instances clearly marked, so practice assembly inherits exam-grade constraint discipline.

**Main Step B - Handle shortages honestly and record manifests.** Implement the shortage policy: if the eligible set cannot satisfy a form (a family's reviews still pending at release time, which N20's honest review states make possible), assembly does not relax constraints; it emits a shortage report naming the binding constraint (topic, type or family), the start screen disables the affected form with the honest reason (for example B forma pagaidām nav pieejama: gaida recenziju), and the release gate (N40) receives the shortage as a blocking or degraded-mode decision, never a silent substitution.

**Subtask B.1 - Prove shortage honesty with the fixture.** Fixture the shortage end to end: a scratch bank state with one family's reviews pending produces the disabled-form path with the recorded reason string and zero silent substitutions (the manifest diff proves only eligible instances were drawn), and the fixture's report is what N30's practice-path shortage warnings reuse for the practice-mode variant of the same honesty.

- **B.1.1 -** Implement the shortage report (binding constraint, missing family or type, count short) and the disabled-form contract (the start screen renders the disabled state with its accessible reason), and record the fixture over the scratch state plus the recovery: clearing the pending reviews (marking the scratch family reviewed) re-enables the form on the next assembly, proving the path is state-driven, not hardcoded.

- **B.1.2 -** Freeze the three form manifests as build artifacts (assembled at build time from the frozen bank, with digests in the ledger), so shipped forms are byte-stable rather than per-load draws, and record the double-build digest parity; the runtime assembly path exists only for the seeded training option, and that distinction is documented in the assembly contract.

- **B.1.3 -** Wire the form picker to the session start (N21's entry gate): choosing a form passes the manifest to the session machine, and the fixture run starts three sessions (A, B, C) with the manifests, asserting each session's slot count, topic distribution and point map match its manifest exactly, completing the picker-to-session contract.

**Main Step C - Integrate and prove assembly determinism end to end.** Integrate assembly into the build (form manifests generated and embedded in the island) and the smoke subset (one assembly vector: a mini-bank draw verifying constraint satisfaction in-file), and prove the end-to-end chain: a fresh checkout, bank build, assembly, and session start produce the recorded form digests and slot maps, closing the loop that makes forms reproducible artifacts rather than runtime accidents.

**Subtask C.1 - Prove reproducibility across the full chain.** The completion proof is the chain reproduction: the full pipeline runs twice from identical inputs and emits identical bank and form digests (extending N20's determinism chain through assembly), and the assembly contract (constraint list, shortage policy, seed policy) is documented as the interface N30's practice paths and N40's release gate consume.

- **C.1.1 -** Implement the build-time assembly step in tools/build.py's pipeline order (bank first, then assembly, then island generation), and record the pipeline run: the three manifests' digests, their byte contribution to the island, and the pipeline-order assertion (assembly fails loudly if the bank digest is absent or stale, never assembles over an unverified bank).

- **C.1.2 -** Extend the smoke subset with the assembly vector (a fixture mini-bank of six families embedded in-file, drawn under a fixed seed, with the constraint check running in the shipped file) and record the smoke pass, keeping shipped self-tests covering every major subsystem including assembly.

- **C.1.3 -** Append the manifests, fairness sweep and chain-reproduction digests to the ledger, run the extended corpus twice for parity, and record the assembly module's byte contribution against the runtime budget, completing Phase V's content-to-container bridge with determinism proven at every link.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the assembled forms A, B and C, when the independent checker runs, then slot counts, per-topic points, family uniqueness, completed-type coverage and eligibility all hold, with each form totaling exactly 100 points.

- **AC2 (negative or edge case):** Given the fairness sweep over ten seeds, when forms regenerate, then every family appears, none triples at the same slot, all digests reproduce identically, and a one-instance-short scratch set fails with the binding constraint named.

- **AC3 (domain integrity and zero-regression):** Given the shortage fixture, when a family's reviews are pending, then the form disables with its honest accessible reason, zero silent substitutions occur, recovery follows state, and double-build manifests are byte-identical.

**Verification and Evidence:** Record checker verdicts, fairness sweep, determinism digests, shortage and recovery fixtures, pipeline-order assertion, smoke pass and byte accounting. The checker is independent of assembly logic (no shared functions, structurally asserted); the advisory-label copy for form selection is recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: a late content fix after form freeze invalidating manifests. Guard: manifests are build artifacts regenerated from the bank, and any bank change re-triggers assembly plus checker runs; stale assembly fails loudly. Rollback: remove assembly and manifests; the bank and session machine are unaffected; N21, N25, N30 and N40 depend on the assembly contract and re-plan if it reverts.

**Definition of Done:** Three deterministic, constraint-verified forms exist with fairness across seeds, honest shortage handling, build-time freezing and a wired picker; smoke, ledger and chain-reproduction evidence is complete; N25-N30 and N40 receive the assembly contract.

### N25 - Implement local, privacy-safe analytics and the honest progress record

**Phase:** Phase V | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N21, N23

**Domain:** Local analytics

**Current State and Evidence:** `VERIFIED (2026-11-16)`: AGENTS.md mandates offline operation and in-memory sessions by default; the predecessor plan's F10 (a completionist analytics-and-visualization feature) is recorded as rejected in the conflict ledger; the mastery and revision features are planned for Phase VI. No analytics module, storage schema or progress view exists.

**Purpose and Rationale:** The simulator needs a modest, honest progress record: which topics have been practiced, which outcomes have been answered correctly at least once, per-form auto-scored results, and the remediation queue state, all stored locally under the learner's explicit opt-in (localStorage only, with the default in-memory session discarding progress on close, per AGENTS.md), with no telemetry, no accounts and no visualization dashboards (the F10 rejection is honored and its reasoning recorded rather than quietly re-implemented).

**Target Artifacts and Touchpoints:** src/analytics.ts and src/store.ts modules; the storage schema with version header. Touchpoint in output/simulator.html: the `#atskats` progress section and the `#iestatijumi` storage controls (opt-in toggle, export as a local file, erase all).

**Out of Scope:** No F10 dashboards, streaks or gamification (rejected by policy, recorded); no cross-device sync; no storing of answer text content beyond what the export includes by explicit choice; no collection or transmission of anything.

**Main Step A - Implement the versioned local store.** Implement the storage layer: an in-memory store as the default (AGENTS.md compliance), an explicit opt-in that switches the same interface to localStorage, a versioned schema (schema_version, progress records, remediation queue, settings) with a migration rule (a newer file ignores an older store with a visible notice rather than guessing at its format, and an older file never writes over a newer store), and the export and erase operations; the interface is consumed by analytics, mastery (N26) and settings only.

**Subtask A.1 - Prove the storage contract including the legacy hazard.** Fixture the storage contract: round-trip (write, read, identical), the opt-in boundary (an in-memory session's data never appears in localStorage, verified by reading the store after a full interaction sequence), migration (a scratch v1 store loads under the v2 schema with the documented mapping, and a scratch newer-version store is ignored with its notice shown), and erase (the store, the export and the erase leave zero residue, the same privacy bar N35 audits).

- **A.1.1 -** Implement the schema with canonical serialization (sorted keys, the same canonicalization discipline as the graded record), and record the round-trip and cross-process fixtures: two page loads in a scratch harness read identical stores, proving localStorage writes are stable rather than incidental.

- **A.1.2 -** Implement the opt-in with its explicit consent copy (Latvian text recording what is stored, that nothing leaves the device, and how to erase), and fixture the boundary both ways: default sessions leave zero localStorage keys (the guard N35 audits), and opted-in sessions persist exactly the schema keys (no stray keys from other modules), with the key set recorded.

- **A.1.3 -** Implement export (a JSON file the learner saves locally, with its filename convention) and erase (a two-step confirmation, since erasing progress is destructive), and fixture both: the exported file parses, matches the store digest, and erase empties the store and the UI state, recorded as the `#iestatijumi` contract.

**Main Step B - Implement analytics events and the progress view.** Implement the analytics module over the graded record chain (N23's digest-linked records): event types are session-completed (form id, auto-score, pending count, elapsed time), task-answered (topic, family, criterion verdicts, no answer text), and remediation-state changes; the log is bounded (a recorded maximum, pruned oldest-first, so localStorage cannot grow unbounded across months of use); and the `#atskats` view renders the honest summary: per-topic practiced counts, per-outcome first-pass correctness, form history and the current remediation queue, all from the same store.

**Subtask B.1 - Prove the log honors its bounds and its honesty.** Fixture the bounded log: generating more events than the cap yields exactly the cap with the oldest pruned (the cap and the prune are recorded), and the honesty fixture proves the view shows pending items as pending (a form with manual-rubric slots shows its auto-score with the pending count, never a total that pretends those points were scored), inheriting N23's unblended discipline into every display.

- **B.1.1 -** Implement the event emitter as a pure function chain (graded record in, events out, no wall-clock dependence beyond the recorded timestamp), and fixture the mapping over the chain fixture from N23: one mixed-form session produces its event set with the graded-record digest referenced in each, keeping the evidence chain intact into the log.

- **B.1.2 -** Implement the per-outcome tracking over the coverage island (N02's 64 outcomes with their anchors), and fixture it: a scripted sequence of graded tasks moves specific outcomes from unattempted to first-pass-correct, the view reflects exactly those outcomes, and a topic with zero activity shows an honest zero state, never a plausible-looking placeholder number.

- **B.1.3 -** Implement the remediation queue (the persisted list N28 consumes: missed items with their task ids, concepts and remediation links from N23's feedback records), and fixture its lifecycle: items enter on incorrect verdicts, are marked resolved through the N28 flow, and the view's queue count matches the store exactly across a round-trip.

**Main Step C - Audit privacy and record the F10 boundary.** Run the privacy audit as this task's capstone: a scripted full-session sweep of all runtime modules records every localStorage access (key, operation, module), asserting zero keys outside the opt-in schema, zero network attempts (the offline contract, reusing N34's no-fetch instrumentation), and zero answer-text storage outside the explicit export; and record the F10 boundary note in the analytics contract: dashboards and streaks are rejected per the ledger, and this module is the scope the workspace actually approved.

**Subtask C.1 - Prove the privacy invariants hold under the full session.** The completion proof is the audit fixture over a complete session (practice, exam, grading, analytics, opt-in, export, erase): the recorded access log shows the exact schema key set, the network instrumentation shows zero attempts, and the erase leaves zero residue; this fixture becomes the regression baseline N35 and N38 re-run at every gate.

- **C.1.1 -** Implement the access-logging instrumentation (a scratch wrapper around the storage interface recording every call), run it over the full-session fixture, and record the access log with the zero-outlier assertion; the corner case is a module writing a cache key outside the schema (for example a render cache), which the audit catches by name and which must be moved into the schema or removed, never whitelisted silently.

- **C.1.2 -** Record the F10 boundary note (the rejected feature, the ledger reference, the reasoning: completionist visualization serves the tracker, not the learner) in the analytics contract, and assert the module exports no chart, streak or score-history components beyond the honest summary, keeping the rejection an enforced fact rather than a memo.

- **C.1.3 -** Append the store and analytics digests to the ledger, extend the smoke subset with one storage vector (round-trip in-file), record the byte contribution against the runtime budget, and run the extended corpus twice for parity, closing Phase V with the simulator's full graded loop (assembly to session to grading to honest local record) implemented and evidence-complete.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the storage contract fixtures, when round-trip, opt-in boundary, migration and erase run, then data is identical on reload, default sessions leave zero localStorage keys, newer stores are ignored with a notice, and erase leaves zero residue.

- **AC2 (negative or edge case):** Given the bounded log and the full-session fixture, when events flow from the graded record, then the cap prunes oldest-first, pending stays unblended in every view, and remediation queue counts match the store across round-trips.

- **AC3 (domain integrity and zero-regression):** Given the privacy audit over a full session, when the access log and network instrumentation are recorded, then only schema keys are touched, zero network attempts occur, zero answer text persists outside export, and the F10 boundary is contractually enforced.

**Verification and Evidence:** Record the storage fixtures, event mapping over the chain fixture, bounded-log run, privacy access log, network zero-attempt assertion and smoke pass. Consent copy, notice copy and disabled-state copy are recorded verbatim in Latvian; the F10 rejection reference is the conflict ledger entry.

**Risks, Guardrails, and Rollback Plan:** Risk: storage schema changes breaking learner data after release. Guard: versioned schema with the ignore-newer rule and a migration map; N40's release gate re-runs the migration fixtures. Rollback: remove analytics and store; the graded record and remediation payloads exist independently, so N26-N30 re-plan against a missing persistence layer (mastery would degrade to session-only state).

**Definition of Done:** A versioned, opt-in, privacy-audited local store and honest progress record exist with bounded logs, digest-linked events, a resolved-boundary F10 note, and complete smoke, audit and ledger evidence; N26-N30 receive the store interface and queue contract.


## 12. Phase VI (N26-N30) - Mastery, Spaced Repetition, Remediation, Revision and Bounded Paths

Phase VI builds the learning loop around the mastery machinery: the mastery state machine over the 64 outcomes with versioned storage and migration (N26); the offline Leitner scheduler for spaced selection (N27); the missed-item remediation queue with anchor links and alternate-variant retries through the ephemeral path (N28); the unified revision view with criterion self-assessment carrying pending semantics (N29); and the bounded practice paths with filters and honest shortage warnings (N30). When this phase closes, practice is adaptive to the learner's demonstrated state, spaced by policy, and honest about its own limits.

### N26 - Implement the mastery state machine over outcomes

**Phase:** Phase VI | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N23, N25

**Domain:** Mastery and learner state

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the coverage island (N02) defines the 64 per-topic outcomes with anchors; the store (N25) provides the versioned persistence with per-outcome tracking already mapped; the graded record (N23) provides per-criterion verdicts. No mastery model, state thresholds or outcome-level state persistence exists.

**Purpose and Rationale:** Mastery turns graded verdicts into per-outcome state: each of the 64 outcomes holds a state (unseen, learning, near-mastered, mastered, and a needs-review state for decayed items), transitions are policy data (a declared rule per state: how many first-pass criterion successes advance, what regresses an item), and the state is the single input that the scheduler (N27), remediation (N28) and revision view (N29) consume, so every module agrees on what the learner knows. The policy is training policy (the roadmap's own proposal, clearly labeled, since no official mastery standard exists in the programme, `UNDETERMINED` for any official counterpart).

**Target Artifacts and Touchpoints:** src/mastery.ts (new module); the mastery policy artifact. Touchpoint in output/simulator.html: the `#atskats` per-outcome states and the `#prakse` topic view's mastery indicators.

**Out of Scope:** No adaptive difficulty engine (F08 stays deferred); no official-competency claims; no mastery state derived from anything except graded criterion verdicts (self-assessment from N29 stays a separate, labeled input).

**Main Step A - Define the mastery policy as data.** Author the mastery policy artifact: per-state transition rules (unseen to learning on first attempt regardless of verdict, since attempting is engaging; learning to near-mastered on a declared consecutive-success count; near-mastered to mastered on a further declared count; any incorrect verdict regresses one state; mastered decays to needs-review after a declared span of inactivity or a declared miss count), the criterion semantics (a task's mastery contribution is per its outcome-mapped criteria, so a partially correct task advances the criteria it satisfied and regresses the ones it failed), and the labeling copy (Latvian state names for the views).

**Subtask A.1 - Validate the policy like every other artifact.** The policy is machine-validated (every state has an entry rule, an exit path and a regression rule; no unreachable states; the declared counts are positive integers), and the validator's corner-case fixture is a scratch policy with an unreachable state, which must fail with the state named, since an unreachable mastery state would silently strand learner progress in it.

- **A.1.1 -** Author the transition table with its parameters (the consecutive-success counts, the decay span, the regression rule) as the labeled training policy, citing the predecessor plan's T-card decisions where they exist and marking the exact thresholds `PROPOSED` (they are pedagogical choices, not programme facts), and record the validator pass over the table.

- **A.1.2 -** Implement the per-criterion mapping: each bank instance's criteria carry outcome ids (from the N02 coverage binding through N20's authored instances), and the fixture proves the mapping is total: every criterion in a scratch sample of every family's instances resolves to at least one outcome id, since a criterion mapping to nothing would drop evidence on the floor.

- **A.1.3 -** Implement the state model as a pure reducer (graded events in, state map out), and record the reducer's transition fixtures: a scripted sequence (first attempt wrong, then two correct, then a streak to mastered, then a decay event) walks the declared path exactly, with each intermediate state recorded; the reducer is stateless, so determinism is by construction and the double-run fixture proves it.

**Main Step B - Integrate mastery with the store and views.** Integrate the reducer with the store (N25's schema gains the mastery map under the versioned schema; the opt-in and erase semantics apply unchanged), and render mastery in the two views: the `#atskats` per-topic outcome list with state icons and text (never color-only, the N22 accessibility discipline), and the `#prakse` topic cards showing per-outcome states so a learner sees what to practice next.

**Subtask B.1 - Prove persistence and view honesty.** Fixture the persistence: a mastery map round-trips through the store, survives a page reload in the scratch harness, and erases cleanly with the store; and the view honesty fixture proves a fresh learner sees honest unseen states (not zero-filled placeholders that look like failed attempts), and a mastered outcome shows its state without implying official certification (the labeling copy records this is self-study progress, not a grade).

- **B.1.1 -** Implement the store extension under the schema's migration rule (N25's v2 gains the mastery key with the documented mapping from an absent key to all-unseen), and record the migration fixture: a scratch pre-mastery store loads with all outcomes unseen, and the newer-store ignore rule still protects learner data from version confusion.

- **B.1.2 -** Implement the two view renderers as functions of (coverage island, mastery map), and record the render fixtures for three learner profiles (fresh, mid-progress, near-complete), which double as N32's visual test data for the mastery views; the corner case is an outcome with zero instances in the form-eligible set (a topic area awaiting reviews), which must render as not yet available with its honest reason rather than as unseen-but-practicable, since practicing it would fail shortage.

- **B.1.3 -** Run the integration fixture end to end: a graded session (N23's chain fixture) flows through the reducer into the store, the views re-render, and the recorded state map matches the hand-computed expectation for the scripted verdicts, closing the chain from answers to visible mastery.

**Main Step C - Prove determinism and record the evidence.** Prove the mastery chain's determinism: replaying the same graded-event sequence in a fresh process yields an identical state map (digest compared), the policy artifact's digest enters the ledger, and the smoke subset gains one mastery vector (a three-event reducer walk asserted in-file), keeping the shipped self-test coverage over the Phase VI chain.

**Subtask C.1 - Prove the policy boundary is honest.** The completion proof includes the policy honesty note recorded with the artifact: the thresholds are `PROPOSED` training policy with no official RSU mastery standard to verify against (`UNDETERMINED`), and the view copy never claims competency certification, so the roadmap's epistemic discipline survives into the learner-facing text.

- **C.1.1 -** Implement the replay harness (event sequence, fresh-process reduce, digest compare) and record the identical digests; then run the reverse-direction fixture: a deliberately interleaved event sequence (two outcomes progressing simultaneously) produces both outcomes' correct independent states, proving the reducer has no cross-outcome coupling, which a naive accumulator implementation would silently introduce.

- **C.1.2 -** Append the policy artifact and module digests to the ledger, run the extended corpus twice for parity (recording both digests), and record the byte contribution of the mastery module against the runtime budget from Section 1, so the mastery layer's weight stays a tracked fact rather than an afterthought.

- **C.1.3 -** Extend the smoke subset with the mastery vector, record the pass, and hand the state-map contract (state enum, transition events, map shape) to N27 and N28 as their frozen input, completing the task with mastery as the agreed learner-state truth for the rest of Phase VI.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the mastery policy artifact, when validation runs, then every state is reachable with entry, exit and regression rules, the scratch unreachable-state fixture fails with the state named, and thresholds are labeled PROPOSED.

- **AC2 (negative or edge case):** Given the scripted verdict sequence, when the reducer runs (twice plus a fresh process), then the state map walks the declared path with identical digests, and interleaved outcomes progress independently.

- **AC3 (domain integrity and zero-regression):** Given the store integration and view fixtures, when mastery persists and renders, then round-trip and erase hold, unseen renders honestly, unavailable outcomes show their reason, and no view copy claims official certification.

**Verification and Evidence:** Record the policy validation, reducer transition fixtures, replay digests, migration fixture, view renders and smoke pass. Every criterion-to-outcome mapping in the family sample resolves; the honesty note and labeling copy are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: thresholds feeling arbitrary to future maintainers and being quietly re-tuned. Guard: they are validated data with PROPOSED labels and ledger digests, so re-tuning is a visible version event. Rollback: remove the mastery module and store key; the migration map documents the absent-key path, so N25's store is unharmed; N27-N29 degrade to session-only scheduling and re-plan.

**Definition of Done:** A validated, deterministic, honestly labeled mastery state machine exists over all 64 outcomes, persisted under the versioned store, rendered honestly in both views, with smoke, ledger and handoff contracts complete for N27-N29.

### N27 - Implement the offline Leitner scheduler for spaced selection

**Phase:** Phase VI | **Priority:** P2 | **Risk:** Medium | **Effort:** M | **Dependencies:** N26

**Domain:** Spaced repetition scheduling

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the predecessor plan approved a Leitner-style approach as training policy; the mastery state machine (N26) provides the outcome state map; the store (N25) provides persistence and time handling needs only coarse day-level spans. No scheduler, box model or selection algorithm exists.

**Purpose and Rationale:** The scheduler decides what to offer next in the `#prakse` practice view: a Leitner box model (outcomes move between boxes on mastery transitions, N26's states mapping to boxes), an offline day-based schedule (each box has a re-offer interval computed from a last-practiced date, with no server and no precise-time dependence), and a selection function that, given the current state map and the current date, offers a bounded queue (a small set, for example five outcomes) ordered by overdueness and mastery need, so practice is focused rather than an undifferentiated flood.

**Target Artifacts and Touchpoints:** src/scheduler.ts (new module); the box-interval artifact. Touchpoint in output/simulator.html: the `#prakse` recommended-next queue and the per-topic scheduling states.

**Out of Scope:** No third-party spaced-repetition algorithms (Anki's, SuperMemo's, or SM-2 variants) copied in; no sub-day precision (day granularity only, honestly coarse); no claiming the schedule mirrors any official study requirement.

**Main Step A - Define the box model and intervals.** Author the box-interval artifact: boxes map to mastery states (unseen and learning to the early box, near-mastered mid, mastered late, needs-review forced early), each box declares a re-offer interval in days (the Leitner property: longer intervals for longer-mastered items), and the selection rule (overdue first, then never-seen, then least-recently-practiced) with its tie-break declared as a deterministic rule (outcome id order, so the queue is reproducible), all labeled training policy.

**Subtask A.1 - Validate intervals and the day-clock contract.** Validate the artifact (intervals strictly increasing with box number, every mastery state has a box, the queue cap is a positive integer) and define the day-clock contract: the scheduler consumes a date (the test harness injects it; the runtime reads the local date only for display-relevant decisions), so all fixtures are time-deterministic regardless of when they run, and the injected-clock discipline from N21 is reused.

- **A.1.1 -** Author the artifact with the interval table and the queue rule, citing the predecessor plan's approval and labeling the exact intervals `PROPOSED`, and record the validator pass plus the scratch fixture: a table with a non-increasing interval pair fails with the box pair named, since a non-increasing Leitner interval would invert the spacing property silently.

- **A.1.2 -** Implement the day-clock contract (an injectable clock with a default local-date implementation, all scheduler logic pure over (state map, date, artifact)), and record the clock fixture: the same state map under two injected dates a week apart yields the expected different queues (the second date has more overdue items), proving time actually enters the decision.

- **A.1.3 -** Implement the box mapping from N26's states and fixture the round trip: a mastery transition sequence moves an outcome through boxes and back (regression returns it to the early box), with the box history recorded, proving the scheduler and mastery share one state truth rather than two drifting copies.

**Main Step B - Implement selection and prove its properties.** Implement the selection function: compute overdueness (days since last practice minus the box interval, floored at zero for fresh items), order the eligible outcomes (overdue descending, then never-seen, then least-recently-practiced, tie-break by outcome id), cap the queue at the declared size, and exclude unavailable outcomes (those with no form-eligible instances, the N26 not-yet-available rule); the output queue carries reasons (overdue by N days, new, due today) that the view renders, so the learner sees why each item is offered.

**Subtask B.1 - Prove the queue's determinism and bounds.** Fixture the selection properties: determinism (same inputs, same queue, digest compared across two runs and a fresh process), the cap (a state map with fifteen overdue outcomes yields exactly the declared queue size), the exclusion rule (an unavailable outcome never appears, with the fixture using a scratch availability map), and the monotonicity corner case: two outcomes with equal overdueness order by id, and a scratch map crafted with exact ties proves the tie-break, so the queue never depends on object iteration order.

- **B.1.1 -** Implement the property fixture set (determinism, cap, exclusion, tie-break) and record all four outputs; the corner case is an entirely fresh learner (all unseen, nothing overdue), where the queue must offer the never-seen outcomes in a sensible order (topic order first, per the declared rule) rather than an empty queue, since a fresh learner told there is nothing to practice is a broken first impression, and the fresh-map fixture is recorded.

- **B.1.2 -** Implement the availability input (the form-eligible family map from N24, the same source the shortage logic uses), and record the integration fixture: a scratch bank state with one topic's families unreviewed produces a queue that excludes that topic's outcomes and includes the reason in the excluded set (not shown to the learner as a broken link, but recorded for the honest not-yet-available rendering).

- **B.1.3 -** Implement the reason strings as term-keyed Latvian text (N10's lint applies), and record the render fixture for the queue: five items with their reasons, which doubles as N32's test data for the practice queue view.

**Main Step C - Integrate with the practice view and record evidence.** Integrate the queue into the `#prakse` view (the recommended-next section above the topic cards, its honesty note that selection is a training-policy study aid), wire accepting a queue item to the bounded practice path (N30's flow), and append the artifact and module digests to the ledger with a smoke vector (a fixed-date queue computation asserted in-file).

**Subtask C.1 - Prove the practice entry end to end.** The end-to-end fixture: a stored state map plus an injected date produce a queue, accepting an item opens the bounded practice path with that outcome's eligible instances, completing the practice-selection loop; the fixture also proves the queue re-computes after the practice session (the just-practiced outcome moves or stays per its new mastery state), so the learner sees their practice reflected.

- **C.1.1 -** Implement the practice-entry handoff (queue item to N30's path starter with the outcome id and its instance filter), and record the fixture run; the contract between N27 and N30 is documented in both tasks, and the handoff payload contains no grading or key material, only selection data.

- **C.1.2 -** Append the scheduler and interval-artifact digests to the ledger, run the extended corpus twice for parity with both digests recorded, and record the scheduler module's byte contribution against the runtime budget, so the selection layer's cost is as visible as its policy.

- **C.1.3 -** Extend the smoke subset with the queue vector (a fixed state map and date embedded in-file, the queue asserted), record the pass, and close the task with the scheduler as the reproducible, time-deterministic selection truth for the practice view.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the box-interval artifact, when validation runs, then intervals strictly increase with box number, every mastery state maps to a box, and a scratch non-increasing pair fails with the box pair named.

- **AC2 (negative or edge case):** Given the property fixture set, when selection runs (twice plus a fresh process), then queues are digest-identical, caps hold, unavailable outcomes never appear, ties break by id, and the fresh-learner queue is non-empty and sensible.

- **AC3 (domain integrity and zero-regression):** Given the end-to-end practice fixture, when a queue item is accepted, then the bounded path opens with the outcome's instances, the queue re-computes post-session, and reasons render with term-keyed Latvian text.

**Verification and Evidence:** Record the artifact validation, clock fixtures, box round trips, the four property outputs, the fresh-map and exclusion fixtures, the end-to-end run and smoke pass. All intervals and rules are labeled PROPOSED training policy; no third-party algorithm is copied (the box model is the standard Leitner scheme approved by the predecessor plan, cited).

**Risks, Guardrails, and Rollback Plan:** Risk: time-dependence sneaking in beyond day granularity (for example hour-level edge tests flapping at midnight). Guard: the injectable clock isolates all logic from wall time, and fixtures run under injected dates exclusively. Rollback: remove the scheduler module; mastery (N26) and the store are unharmed; the practice view falls back to topic browsing, and N30 re-plans the queue entry.

**Definition of Done:** A validated, deterministic, day-based Leitner scheduler offers bounded, reasoned, reproducible practice queues over the mastery map, integrated with the practice view and N30's paths, with property fixtures, smoke coverage and ledger digests complete.

### N28 - Implement missed-item remediation with anchors and alternate variants

**Phase:** Phase VI | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N07, N20, N26

**Domain:** Remediation flow

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the graded record (N23) emits feedback with remediation links (concept anchors from N07, chains from N16); the store (N25) persists a remediation queue; the bank (N20) provides alternate variants within families (the variant letters) plus the runtime ephemeral variant path for practice retries. No remediation flow, retry assembly or resolution tracking exists.

**Purpose and Rationale:** Remediation closes the teaching loop: a missed task enters the queue with its outcome, misconception signatures and remediation links; the learner can jump to the concept anchor (the drawer from N07), study the worked chain (N16), and then retry with an alternate variant (a different variant letter of the same family at build time, or an ephemeral runtime variant for unlimited practice retries), never the exact same instance they failed (a retry that re-serves the failed question trains answer memory, not the skill); resolution is explicit and honest.

**Target Artifacts and Touchpoints:** src/remediation.ts (new module); the queue-state contract. Touchpoint in output/simulator.html: the remediation queue in `#atskats`, the per-item flow (study links, retry action, resolve action) and the practice retry path.

**Out of Scope:** No forced remediation gating (the learner chooses; the simulator recommends); no re-grading of the original attempt (it stays as graded); no queue entries without resolvable links (validation is absolute).

**Main Step A - Implement the queue lifecycle.** Implement the remediation queue state machine: entries enter on incorrect or partial verdicts in graded sessions (from N23's feedback records, through N25's queue persistence), each entry holds the task reference, outcome ids, signature ids, remediation links (anchor and chain ids) and its state (open, retried, resolved); transitions are add (deduplicated by family and outcome, since three missed tasks on the same outcome are one learning gap), retry (links the retry instance), and resolve (explicit learner action or a declared auto-resolve rule: a correct retry advances toward resolution, but the final mark is the learner's or the declared policy's, honestly labeled).

**Subtask A.1 - Prove deduplication and the honest-resolve rule.** Fixture the lifecycle: three misses across one outcome coalesce into one entry (the entry's miss count is three, its links one set), a correct retry advances the entry but does not silently resolve it if the declared policy requires confirmation (the copy explains why: one correct answer is evidence, not mastery), and the scratch auto-resolve variant (a policy with one-correct-resolves) behaves per its own declared rule, proving the behavior is policy data, not hardcoded sentiment.

- **A.1.1 -** Implement the entry model with deduplication keyed by (family, outcome) and record the coalescing fixture: three scripted misses produce one entry with miss count three and the union of links; the corner case is a miss on a task whose family already has a resolved entry, which must open a new entry rather than resurrecting the resolved one (progress history is not rewound), and that fixture is recorded.

- **A.1.2 -** Implement the retry instance selection: prefer a different variant letter from the same family's bank instances (deterministic: the next letter cyclically, recorded), fall back to the runtime ephemeral path (N20) when all letters have been attempted by this learner (the unlimited practice case), and never serve the exact failed instance id; the selection fixture proves the never-reserve rule across a scripted sequence of four retries through a four-variant family.

- **A.1.3 -** Implement the resolution states with their Latvian copy (open, retried, resolved with the reason), and fixture the full path: miss, study, retry, resolve, with the queue count and the `#atskats` rendering matching at every step; the graded retry itself flows through the normal practice path (N30) and its verdict updates mastery (N26) and the queue in one consistent chain.

**Main Step B - Implement the study handoff and link integrity.** Implement the study handoff: a queue entry's anchor link opens the N07 concept drawer at the exact anchor, its chain link opens the N16 worked chain, and both record a return-to-queue affordance (the flow is a loop, not a one-way jump); link integrity is validated at queue-write time (N23's records already guarantee resolvable links, and the queue re-validates on read, so a content change that broke an anchor fails loudly at render rather than rendering a dead link).

**Subtask B.1 - Prove the loop's integrity end to end.** The loop fixture: a scripted miss on a classification task, anchor open (drawer state recorded at the anchor), chain open (the reveal component's first state recorded), return to queue, retry with the alternate variant, correct verdict, mastery advance (N26), queue entry advance, all recorded as one trace; the trace is the acceptance artifact for the entire remediation design.

- **B.1.1 -** Implement the handoff payload (target anchor id, chain id, return context) and record the trace fixture; the corner case is an entry whose chain link is null (a family without a worked-chain counterpart, since chains exist only for the 14 examples' families), where the entry renders anchor-only with no broken chain affordance, and the nullable-link fixture is recorded.

- **B.1.2 -** Implement the on-read re-validation (entry links checked against the loaded islands at render time) and fixture the break: a scratch store entry with a deliberately dangling anchor fails the render contract loudly with the anchor named, proving the integrity guarantee is runtime-real, not just authoring-time.

- **B.1.3 -** Implement the retry session's integration with bounded paths (the retry counts against N30's practice bounds like any practice, no special bypass), and record the bound fixture: a retry inside an exhausted path offers the honest path state rather than exceeding the bound, keeping the practice discipline uniform.

**Main Step C - Prove the full remediation chain and record evidence.** Prove the complete chain deterministically: the scripted miss-to-resolution trace replays in a fresh process with identical queue states (digests), the queue's persistence round-trips through the store (N25's schema and erase semantics apply, so erasing progress clears the queue honestly), and the smoke subset gains one remediation vector (an add-deduplicate-retry walk asserted in-file).

**Subtask C.1 - Prove the chain's persistence honesty.** The persistence fixture proves the queue is honest about its own weight: it is stored progress (the opt-in from N25 governs it; a default in-memory session loses the queue on close, which the settings copy states plainly), and the erase operation removes it completely with the rest of the store, so the privacy audit from N25 still holds with the queue included (its keys are in the recorded schema set).

- **C.1.1 -** Implement the replay harness for the remediation trace (fresh process, digest compare) and record the identical digests; then run the store round-trip and erase fixtures with the queue populated, appending the queue keys to the recorded schema set so N35's privacy audit picks them up without re-auditing.

- **C.1.2 -** Append the remediation module digests and the loop trace to the ledger, run the extended corpus twice for parity with the digests recorded, and record the remediation module's byte contribution against the runtime budget, keeping the teaching loop's cost inside the tracked accounting.

- **C.1.3 -** Extend the smoke subset with the remediation vector, record the pass, and hand the queue-state contract to N29 (the revision view consumes the queue as part of its unified review surface), completing Phase VI's middle link with the teaching loop fully wired and evidence-complete.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the coalescing fixture, when three scripted misses land on one outcome, then one queue entry holds miss count three and the union of links, and a miss on a resolved family opens a new entry without rewinding history.

- **AC2 (negative or edge case):** Given the four-retry selection fixture, when retries draw from a four-variant family, then the exact failed instance is never re-served, letters cycle deterministically, and the ephemeral fallback engages after all letters are attempted.

- **AC3 (domain integrity and zero-regression):** Given the full loop trace (replayed fresh), when it runs, then anchor and chain open at their targets, dangling links fail loudly by name, retry verdicts advance mastery and queue in one chain, persistence and erase honor the store contract, and smoke passes in-file.

**Verification and Evidence:** Record the lifecycle fixtures, selection traces, loop trace with digests, dangling-link failure, store round-trips, smoke pass and byte accounting. Resolution copy states the one-correct-answer-is-evidence policy verbatim; no flow forces remediation (the recommend-only rule is in the recorded contract).

**Risks, Guardrails, and Rollback Plan:** Risk: remediation becoming a punitive wall learners avoid. Guard: the flow is recommend-only with plain copy, and the retry uses fresh variants so retrying feels like learning rather than repetition. Rollback: remove the remediation module and store key; grading feedback and anchors stand alone; N29's queue surface and N30's retry entry re-plan.

**Definition of Done:** A deduplicating, link-validated remediation queue exists with deterministic alternate-variant retries, an end-to-end study loop, honest resolution policy, persistence under the store contract, and complete trace, smoke and ledger evidence, with the queue contract handed to N29.

### N29 - Build the unified revision view and criterion self-assessment

**Phase:** Phase VI | **Priority:** P2 | **Risk:** Medium | **Effort:** M | **Dependencies:** N16, N23, N26

**Domain:** Revision and self-assessment

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the predecessor plan's F07 (criterion self-assessment card) is an approved feature awaiting implementation; the rubric criteria, concept anchors, worked chains and mastery map all exist as prior deliverables; the self-assessed critical-step explanation already has its pending semantics (N19, N22). No revision view, self-assessment card or checklist-of-mastery surface exists.

**Purpose and Rationale:** Revision needs one honest surface: the `#atskats` revision panel that lists per-topic outcomes with their mastery states, links to re-study each outcome's anchors and chains, and offers the F07 criterion self-assessment card: for a chosen outcome, the learner sees the outcome's criteria (the same ones grading uses, names only, no key content) and self-rates each (can do confidently, can do with effort, cannot do yet), with the self-ratings stored as a separate, clearly labeled input (they never masquerade as graded evidence; the mastery machine consumes graded verdicts only, and self-ratings appear beside them, visually and semantically distinct).

**Target Artifacts and Touchpoints:** src/revision.ts (new module); the self-assessment artifact contract. Touchpoint in output/simulator.html: the `#atskats` revision panel, the per-outcome study links and the F07 self-assessment card flow.

**Out of Scope:** No self-ratings feeding mastery transitions (the separation is the design); no revealing criterion keys or rubric internals in the card (criterion names only); no gamified confidence scores.

**Main Step A - Build the revision panel.** Implement the revision panel renderer: per topic, the outcome list (state icons and text from N26), each outcome's study affordances (the concept anchor jump, the worked chain where one exists, the practice entry through N30), and the self-assessment entry point; the panel consumes only the coverage island, the mastery map and the queue (N28), rendering honest empty states for untouched topics and the not-yet-available reason for outcomes without eligible instances.

**Subtask A.1 - Prove the panel renders the full truth.** Fixture the panel across the three learner profiles from N26 (fresh, mid-progress, near-complete): every one of the 64 outcomes renders (none dropped, none duplicated), every affordance resolves (anchors, chains, practice entries validated at render time, the N28 on-read discipline), and the empty and unavailable states render their honest copy; the three fixture renders are the panel's acceptance record and N32's visual test data.

- **A.1.1 -** Implement the outcome row contract (state, last-practiced display from the store, affordances, self-rating summary where present), and record the render fixtures for the three profiles; the corner case is an outcome with a self-rating but no graded attempt (a learner who self-assessed before practicing), where the row shows the self-rating distinctly beside an honest not-yet-attempted graded state, never a merged impression.

- **A.1.2 -** Implement the affordance resolution (the same target validation the remediation queue uses, reused through the islands' loader rules), and fixture the dangling case: a scratch coverage island with a broken anchor reference fails the render loudly with the anchor named, keeping the panel's links as guaranteed as the queue's.

- **A.1.3 -** Implement the per-topic summary line (counts by state, the honest zero for untouched topics), and record the copy lint (term-keyed Latvian, no official-certification phrasing anywhere in the panel, per the N26 honesty rule).

**Main Step B - Implement the F07 self-assessment card.** Implement the self-assessment card: for a chosen outcome, render its criteria names (from the rubric data via the coverage binding: names only, the exact Latvian criterion labels grading displays post-grade, never values or keys), the three-state rating control per criterion (the same accessible select pattern as N22's components), an optional free-text note field (stored verbatim, never analyzed), and the save action persisting ratings under the store's schema; the card explicitly labels the ratings as the learner's own assessment (the copy recorded verbatim).

**Subtask B.1 - Prove the separation invariants hold.** Fixture the separation: a session with self-ratings and graded verdicts on the same outcome shows both, distinctly labeled (the fixture asserts the two displays never share a component or a state source); the mastery map is asserted unchanged by rating activity (the reducer's input contract from N26 excludes self-ratings structurally, and the fixture proves it by digest comparison); and the card's criterion names are asserted key-free (the leak scan from N12 applied to the card's render output finds zero key values).

- **B.1.1 -** Implement the card's criterion sourcing (rubric criteria names through the same loader the grading views use, so a rubric rename propagates everywhere at once), and record the sourcing fixture: a scratch rubric rename appears identically in the graded feedback fixture and the card render, proving single sourcing rather than a copied label list that would drift.

- **B.1.2 -** Implement the rating control with N22's ARIA patterns (Latvian names from the term bank, keyboard-complete, state announced), and record the keyboard fixture: a full card is completable through the select API alone, with each rating's state change announced (the recorded ARIA assertion), giving N33 the live screen-reader precondition for this component.

- **B.1.3 -** Implement the persistence under the store (schema key, opt-in and erase semantics inherited, the free-text note stored verbatim with its never-analyzed copy), and fixture the round-trip plus the erase; the corner case is a very long note (the field's declared maximum, with a visible counter), since unbounded text in localStorage is the N25-bounded-store discipline applied to this field, and the boundary fixture is recorded.

**Main Step C - Integrate, prove determinism and hand off.** Integrate the panel and card into `#atskats`, prove the pair's determinism (same store state, same renders, digest compared across two runs and a fresh process), and run the full-revision fixture: a learner profile with graded history, queue entries and self-ratings renders the complete panel with every element in its recorded place, which becomes the revision view's frozen regression baseline.

**Subtask C.1 - Prove the honest-surface property end to end.** The capstone proof is the honesty audit: over the full-revision fixture, every displayed state traces to exactly one source (mastery from N26, queue from N28, ratings from the card schema, availability from N24's eligibility), no display merges sources, and the audit table recording each element's source is this task's final evidence, so the revision surface cannot gradually blur graded truth and self-reported truth the way unchecked study tools do.

- **C.1.1 -** Implement the determinism harness (two renders plus a fresh-process render, digest compare over the canonical render description) and record identical digests; then run the honesty audit table generation and record the table with zero untraceable elements.

- **C.1.2 -** Append the revision module digests and the three profile fixtures to the ledger, run the extended corpus twice for parity with the digests recorded, and record the revision module's byte contribution against the runtime budget, so the honest-surface work carries its visible cost.

- **C.1.3 -** Extend the smoke subset with one revision vector (a fixed profile rendering a subset assertion in-file), record the pass, and hand the panel's practice-entry contract to N30 (the bounded paths consume the same entry payload the queue uses), completing the revision surface with its evidence chain closed.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the three learner profiles, when the revision panel renders, then all 64 outcomes appear with resolvable affordances, honest empty and unavailable states, and self-ratings display distinctly from graded states.

- **AC2 (negative or edge case):** Given the self-assessment card fixtures, when ratings save and render, then criteria names are single-sourced and key-free, controls are keyboard-complete with announced states, notes round-trip verbatim with the declared maximum, and the mastery map is digest-unchanged by rating activity.

- **AC3 (domain integrity and zero-regression):** Given the determinism and honesty audit, when the full-revision fixture runs (twice plus fresh), then render digests are identical, every element traces to exactly one source in the audit table, and smoke passes in-file.

**Verification and Evidence:** Record the profile fixtures, the dangling-anchor failure, the separation digest comparison, the card sourcing and keyboard fixtures, the round-trip and boundary fixtures, the honesty audit table and smoke pass. The self-assessment label copy and the never-analyzed note copy are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: self-ratings subtly influencing recommendations in ways learners do not expect. Guard: any future scheduler consumption of ratings is a new declared policy artifact, not a quiet coupling; the structural exclusion in N26's input contract is fixture-proven. Rollback: remove the revision module and its store key; mastery, the queue and the anchors stand alone; N30's practice entry has an alternative topic-card path and re-plans.

**Definition of Done:** A unified, deterministic, honestly sourced revision panel and the F07 criterion self-assessment card exist with proven separation from graded mastery, key-free criterion names, accessible controls and complete profile, audit, smoke and ledger evidence, with the practice-entry contract handed to N30.

### N30 - Implement bounded practice paths with filters and honest shortage handling

**Phase:** Phase VI | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N08, N20, N26

**Domain:** Practice mode runtime

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the predecessor plan's F03 (per-topic bounded practice: a short, ordered path rather than an endless question stream) is an approved feature; practice components (N22's inputs, the hint surfaces from N08's drawers), the scheduler queue (N27), the remediation retry flow (N28) and the runtime ephemeral variant path (N20) all exist as prior deliverables. No practice path state machine, filter set or session flow exists.

**Purpose and Rationale:** Practice becomes a structured, bounded experience: per topic, a short declared path (a fixed small set of items, for example six to eight, ordered easy-to-hard where the family authoring data declares difficulty, otherwise family order), offered through three entry points (topic browse, scheduler queue, remediation retry, all sharing one path engine), with filters (type, and unattempted-only where honest), hints enabled (the full practice-mode help surface from N21's mode registry), and honest shortage handling: when a filter or path cannot be filled from eligible instances, the path states its real length and reason, never pads with unreviewed content or repeats items a learner just answered.

**Target Artifacts and Touchpoints:** src/practice.ts (new module); the path policy artifact. Touchpoint in output/simulator.html: the `#prakse` topic cards, the path runner view (current item, progress, hint drawers, skip and end controls) and the path summary.

**Out of Scope:** No endless random streams (the bounded path is the design, per F03); no adaptive difficulty (F08 deferred); no drawing unreviewed instances into paths (the eligibility gate is absolute, shared with N24).

**Main Step A - Define the path policy and implement the engine.** Author the path policy artifact: the per-topic declared lengths (a small fixed set per topic, the exact numbers `PROPOSED` and labeled), the ordering rule (declared difficulty where the family authoring carries it, else family id order, deterministic either way), the filter semantics (by response type; unattempted-only reads the store's attempt history and is honest when history is empty), and the bounds rules (no item repeats within a path; a path never includes an item the learner answered in the current session; the declared length is a target, not a promise).

**Subtask A.1 - Validate and fixture the policy.** Validate the artifact (lengths positive and sane against the per-topic instance counts from N20; every response type in the filter vocabulary exists in the 18-type registry), and fixture the ordering determinism: the same (topic, filters, learner history) yields the identical path, digest compared, with the difficulty-declared and difficulty-absent cases both covered.

- **A.1.1 -** Author the artifact with per-topic lengths that respect the real counts (topic 7's five outcomes and smaller family set get a shorter declared path than topic 3's eleven-outcome set, the numbers grounded in N20's bank report and cited to it), and record the validator pass; a scratch length exceeding a topic's eligible instance count fails validation with the topic named, since such a policy would guarantee permanent shortage.

- **A.1.2 -** Implement the path engine as a pure function (topic, filters, history, eligible set in; ordered instance list out), and record the determinism fixtures plus the no-repeat invariants: a scratch history containing half a topic's instances produces a path excluding exactly those, and the exclusion fixture proves the current-session exclusion too (the runner marks items answered in-session).

- **A.1.3 -** Implement the three entry points over one engine (topic browse passes topic plus default filters; the scheduler queue passes an outcome-focused filter set; remediation retry passes the specific family and alternate-variant requirement from N28), and record the three fixture paths, proving one engine serves all entries with no entry-specific quirks.

**Main Step B - Implement the runner and the honest shortage path.** Implement the path runner: current item rendered through N22's components with practice-mode help enabled (hints, the concept drawer, the term lookup, per the mode registry), progress indicator (item n of the true length), skip (advances without grading; a skipped item is recorded as skipped, not incorrect, since a skip is not evidence of failure), end-early with a summary, and the path summary at completion (attempted, correct, skipped, mastery effects through the normal grading-to-mastery chain); and the shortage path: when the engine cannot fill the declared length, the runner shows the real length with its reason (for example pieejami 4 no 6: gaida recenziju) and proceeds with the honest set.

**Subtask B.1 - Prove shortage honesty and the skip semantics.** Fixture the shortage triad: eligibility shortage (a topic with pending reviews yields the shortened path with its reason), filter shortage (a type filter that leaves two instances yields a two-item path, not a padded one), and history exhaustion (a learner who has attempted everything eligible gets the honest empty state with pointers to the scheduler's review intervals and the ephemeral variant path for unlimited retries, both named in the copy); and fixture the skip chain: three skips produce three skipped records, zero incorrect verdicts, and the summary reflects the distinction.

- **B.1.1 -** Implement the shortage reason rendering with its term-keyed copy and record all three fixtures; the corner case is the fully-exhausted returning learner (all eligible attempted, no ephemeral interest), where the path must not dead-end: it names the review intervals (items become due over days per N27) and the ephemeral option, and the copy fixture records this exit dignity.

- **B.1.2 -** Implement the runner's grading integration (practice attempts grade through N23's engines with the same criterion shapes, feed mastery (N26) and the queue (N28) normally), and record the chain fixture: one practice path session's verdicts move mastery states and queue entries exactly as an exam session's would, since a practice answer is real evidence and the modules treat it so.

- **B.1.3 -** Implement the hint contract inside the runner (hint drawer per item, the reveal of a worked chain for the same family's chain-linked instances, both never present in exam mode per the N21 boundary), and record the mode assertion: the runner's render contract, running under the practice mode registry, contains the help markers an exam render would exclude, with the boundary re-proven in this new context.

**Main Step C - Prove the practice loop end to end and record evidence.** Prove the full practice loop: profile with a scheduler queue entry, a remediation retry and a topic browse, three paths run (one per entry point), all grading, mastery, queue and store effects recorded in one trace, and the trace replayed in a fresh process with identical digests; append the policy and module digests to the ledger with a smoke vector (a fixed path computation asserted in-file).

**Subtask C.1 - Prove the loop closes Phase VI coherently.** The capstone proof is the Phase VI chain fixture: mastery (N26) feeds the scheduler (N27), the scheduler feeds the path (N30), practice verdicts feed grading and mastery again, misses feed remediation (N28) whose retries re-enter the path, and the revision view (N29) reflects it all; one scripted learner journey traverses every Phase VI module in order, and its recorded trace proves the phase's modules form one coherent learning loop rather than six disconnected features.

- **C.1.1 -** Implement the journey harness (a scripted learner: self-assesses, practices from the queue, misses, remediates, retries, revises; every step's state changes recorded) and record the journey trace as Phase VI's capstone artifact; the corner case is the journey crossing the day boundary (the injected clock advances a day mid-journey), where the scheduler's queue legitimately changes, and the trace proves the change is the declared rule, not a flake.

- **C.1.2 -** Append the practice policy and module digests to the ledger, run the extended corpus twice for parity with the digests recorded, and record the practice module's byte contribution against the runtime budget, completing the accounting for every Phase VI runtime module.

- **C.1.3 -** Extend the smoke subset with the path vector, record the pass, and close Phase VI with the practice surface, the loop's every link fixture-proven, and the runtime feature set complete for Phase VII's build, accessibility and robustness hardening.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the path policy artifact, when validation runs, then lengths are sane against the per-topic eligible counts (a scratch overlong path fails with the topic named), and path computation is digest-deterministic with no-repeat invariants.

- **AC2 (negative or edge case):** Given the shortage triad fixtures, when eligibility, filter and history shortages occur, then paths show their true lengths with reasons, no padding or unreviewed content appears, skips record as skipped (never incorrect), and the exhausted state offers dignified exits.

- **AC3 (domain integrity and zero-regression):** Given the Phase VI journey trace (replayed fresh), when the scripted learner traverses all six modules, then every state change matches the declared rules including the mid-journey day change, grading feeds mastery and queue normally, and smoke passes in-file.

**Verification and Evidence:** Record the policy validation, determinism digests, entry-point fixtures, shortage triad, skip chain, the journey trace with its replay digests and smoke pass. Practice verdicts flow through the identical grading chain (the trace shows it); the mode-boundary assertion is re-run in the runner context.

**Risks, Guardrails, and Rollback Plan:** Risk: declared lengths aging badly as the bank's review states change. Guard: the policy validator runs against live eligible counts at every build, so a bank change that invalidates a length fails loudly. Rollback: remove the practice module; the scheduler, remediation and inputs stand alone; Phase VI's loop loses its action surface and re-plans.

**Definition of Done:** Bounded, deterministic practice paths run from three entry points with hints, honest shortages, skip semantics and full grading integration; the Phase VI journey trace proves the coherent loop; smoke, ledger and byte-accounting evidence is complete.


## 13. Phase VII (N31-N35) - Single-File Build, Responsive Layout, Keyboard, Print and Security Audits

Phase VII turns the accumulated modules into the single deliverable: the idempotent build pipeline that assembles output/simulator.html with a digest manifest and a static contract checker (N31); the responsive layout and the WCAG 2.2 AA contract across the 320 to 1280 range (N32); the keyboard-only operation and screen-reader semantics with a staged manual protocol (N33); the no-JavaScript fallback and the print and paper mode (N34); and the performance, storage and security audit with the injection corpus (N35). When this phase closes, the artifact exists in its final form and survives its own audits.

### N31 - Implement the idempotent single-file build pipeline

**Phase:** Phase VII | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N05, N16, N20, N25, N30

**Domain:** Build pipeline

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the blueprint and AGENTS.md require a single offline output/simulator.html with no CDN or network dependencies; the source module set is complete through Phase VI (islands, banks, engines, runtime views); the repository already carries tools/ conventions (verify_preparation.py) and the frozen materials layout. No build tool exists for the simulator and no digest manifest exists for the artifact.

**Purpose and Rationale:** The build pipeline assembles every prior deliverable into output/simulator.html deterministically: it inlines the islands (coverage, conventions, bank, forms, golden vectors, terms, analytics data), concatenates the runtime modules in a declared dependency order, embeds the CSS and SVG assets, stamps the build metadata (version, source digests, build policy), and writes exactly one file; running the build twice over unchanged sources must produce a bit-identical file (idempotence), which is the property that makes every later verification task trustworthy, since a non-reproducible artifact cannot be regression-tested at all.

**Target Artifacts and Touchpoints:** tools/build.py (new); output/simulator.html (the deliverable); the build manifest artifact (source digests, module order, version stamp).

**Out of Scope:** No bundler, transpiler or npm dependency (plain Python 3 assembly, per the offline rule); no minification beyond whitespace normalization declared in the policy (readability is a stated goal for student-facing code review); no network fetching of any kind.

**Main Step A - Define the build policy and module order.** Author the build policy artifact: the declared module dependency order (islands first, then engines, then runtime views, then the bootstrap), the inline assembly template (the HTML skeleton with lang="lv", the viewport and theme meta, the anchors #sakums through #iestatijumi from the blueprint, the island script tags in their declared order), the metadata stamp format (version, ISO date, source digest set), and the idempotence rules (stable key ordering in all JSON islands, no timestamps inside content except the declared stamp, UTF-8 end to end).

**Subtask A.1 - Validate the order against the module contracts.** Validate the policy by loading every module's declared imports (each Phase IV-VI module records what it consumes) and proving the order satisfies them all (an import that resolves to a later module fails validation with both modules named), since a wrong order is a silent undefined-behavior class that only appears at runtime in one browser and not another.

- **A.1.1 -** Author the policy artifact with the module order derived from the recorded contracts of N16-N30 (each module's consumed interfaces cited from its task's handoff notes), and record the validation pass; the corner-case fixture is a scratch pair of modules with a circular dependency (A consumes B, B consumes A), which the validator must reject with both names, since circular inlining would be legal JavaScript but a non-deterministic assembly trap.

- **A.1.2 -** Implement the skeleton template as a Python template with the island insertion points marked by stable ids (#sim-coverage, #sim-conventions, #sim-bank, #sim-forms, #sim-golden-vectors, #sim-terms, #sim-analytics), and record the template's own fixture: a dry-run assembly over a scratch island set produces a document whose every insertion point is filled exactly once, with a duplicate-insertion attempt failing loudly with the point named.

- **A.1.3 -** Implement the digest stamping (SHA-256 over each source module and island, sorted by path, then a composite digest over the manifest), and record the stamp fixture: two runs over unchanged inputs emit identical manifests and an identical stamp, while a one-byte source change flips exactly the expected entries, proving the stamp is a real fingerprint rather than decoration.

**Main Step B - Implement the assembly and idempotence proof.** Implement the assembly: read the sources in the declared order, inline the islands with sorted keys and stable separators, concatenate the runtime with the declared wrapper (one inline script element, matching the masters' single-script convention verified in the inspection), embed the CSS and the SVG library, write output/simulator.html atomically (write to a temporary name then replace, so a failed build never leaves a half-written deliverable), and emit the manifest alongside.

**Subtask B.1 - Prove bit-identical rebuilds and the atomic write.** The idempotence proof: run the build three times over unchanged sources in three fresh processes; the three output/simulator.html files must be byte-identical (digests recorded), the manifests identical, and the rebuild-diff empty; then the atomicity fixture: an injected failure mid-assembly (a scratch source with a decode error) leaves the previous output file untouched on disk with its digest unchanged, since a corrupt half-file masquerading as the deliverable is the worst failure mode a build can have.

- **B.1.1 -** Implement the assembly with deterministic JSON emission (sort_keys, declared separators, ensure_ascii policy fixed at False to keep Latvian text readable, matching the masters' own island style verified in the inspection), and record the emission fixture: an island with insertion-order-varying source objects emits identical bytes across orderings, since key order leaks Python dict accidents into the artifact.

- **B.1.2 -** Implement the single-script wrapper with the declared newlines between modules (a policy choice recorded for diff readability), and record the wrapper fixture: the assembled script parses (the scratch harness uses the engine's own parser bindings) with module boundaries findable by their recorded separator comments, so a future maintainer can still map artifact regions to sources.

- **B.1.3 -** Implement the atomic write and the rebuild harness, then run the three-run idempotence proof and the atomicity fixture, recording all output digests; the corner case is a source tree with a stale temporary file from an earlier failed run (the temp-name collision case), which the writer's unique-temp policy must survive, and the collision fixture is recorded.

**Main Step C - Prove the artifact contract and record the ledger.** Prove the assembled artifact satisfies the deliverable contract from Section 1: a static contract check over output/simulator.html asserts lang="lv", the nine ASCII anchors present exactly once each, the seven island ids present, zero external URLs (a scan for http:// and https:// outside declared comment contexts, honoring the offline rule), a single script element, and the size within the declared budget (700-1400 KiB per Section 1, with the bank/runtime/CSS/figure sub-budgets measured and recorded); the check result is the artifact's birth certificate and N36-N40's common precondition.

**Subtask C.1 - Prove the budget accounting is real.** The budget fixture measures the assembled file's actual composition (island bytes, runtime bytes, CSS bytes, SVG bytes, template overhead) against the Section 1 sub-budgets and records the table; if any sub-budget is exceeded the build fails with the offending segment named (a soft warning would let a 3 MiB bank creep in silently), and the fixture proves the failure with a scratch oversized island.

- **C.1.1 -** Implement the static contract checker as a standalone script tools/check_artifact.py so N39's QA runner can invoke it independently, and record the check pass over the freshly built artifact with every assertion's value (anchor count, island count, external URL count of zero, script count of one, byte size).

- **C.1.2 -** Implement the offline scan with its whitelist policy (the scan ignores the declared license comment that names the upstream project, if any, but no other URL-bearing context is exempt), and record the scan fixture: a scratch artifact with one injected external URL fails with the URL and its line context named, since one CDN reference would break the offline promise the whole design rests on.

- **C.1.3 -** Append the build policy, manifest and checker digests to the ledger, record the composition table, and hand the artifact contract (digest, size, composition) to N36-N40 as their frozen input, closing the task with the deliverable existing, reproducible and contract-proven.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the build policy artifact, when module order validation runs, then every recorded import resolves forward (a scratch circular pair fails with both modules named) and every island insertion point fills exactly once.

- **AC2 (negative or edge case):** Given three fresh-process builds over unchanged sources, when their outputs are compared, then output/simulator.html files are byte-identical with identical manifests, and an injected mid-assembly failure leaves the previous artifact untouched.

- **AC3 (domain integrity and zero-regression):** Given the static contract check, when the artifact is scanned, then lang, anchors, islands, single script, zero external URLs and all sub-budgets pass, with an oversized scratch island failing by segment name.

**Verification and Evidence:** Record the policy validation, template and stamp fixtures, the three-run digest table, the atomicity and collision fixtures, the composition table and the contract check pass. The manifest lists every source digest; the build is rerun twice more on the final sources with identical output recorded in the ledger.

**Risks, Guardrails, and Rollback Plan:** Risk: source drift between the policy and the real module set (a new module added in Phase VIII work but never added to the order). Guard: the order validator derives from the recorded contracts and N39's runner re-checks; a missing module fails the contract check because its island or view is absent. Rollback: the build is additive tooling; removing it leaves all sources intact, but N36-N40 lose their input and must re-plan.

**Definition of Done:** A deterministic, atomic, policy-validated build pipeline produces a byte-identical output/simulator.html over unchanged sources, with manifest, composition accounting and static contract check all recorded, and the artifact contract handed to Phase VIII.

### N32 - Implement the responsive layout and WCAG 2.2 AA contract

**Phase:** Phase VII | **Priority:** P1 | **Risk:** High | **Effort:** L | **Dependencies:** N31

**Domain:** Responsive layout and accessibility

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the blueprint requires a mobile-first, touch-friendly simulator usable on small screens; the masters themselves use responsive patterns and @media print (verified in the inspection); the runtime views and components exist (N06-N30) but were authored against logic contracts, not layout breakpoints; no breakpoint system, WCAG contract or contrast token set exists.

**Purpose and Rationale:** The simulator must work on the phones students actually own: a mobile-first layout with declared breakpoints (320 as the floor, 390 and 768 as the practical classes, 1280 as the desktop ceiling, matching the blueprint's device matrix), a design-token system (spacing, type scale, and the contrast-safe color pairs the theme toggle switches between) defined once and consumed by every view, and a WCAG 2.2 AA contract (contrast 4.5:1 text, 3:1 large text and UI boundaries, target size, no color-only meaning) that is machine-checked at build time over the token set so accessibility is a compile-time property rather than a late audit surprise.

**Target Artifacts and Touchpoints:** The design token artifact; the CSS layer of the build (styles.css assembled by N31); the token contrast checker tools/check_contrast.py. Touchpoints in output/simulator.html: every view section, the theme toggle, the navigation.

**Out of Scope:** No framework CSS; no pixel-perfect design mimicry of any specific site; no AAA claims (the contract is AA, stated honestly); no claims of certification by any external body.

**Main Step A - Define the tokens and breakpoints as data.** Author the design token artifact: the color pairs (each semantic color in both themes with its computed contrast ratios), the type scale (declared rem sizes with a 16 px floor, honoring the no-zoom-punishment principle), the spacing scale, the target-size floor (44 px per the touch-friendly requirement), and the breakpoint table (the declared classes and what changes at each, for example single-column practice paths at 320, two-pane exam layout only above 768); every view's CSS consumes only tokens, never raw hex values, so the contrast guarantee has exactly one place to hold.

**Subtask A.1 - Validate the token set mathematically.** Implement the contrast checker: compute WCAG relative luminance and contrast ratios for every text-token pair and every UI-boundary pair in both themes, and fail the build if any pair misses its threshold (4.5:1 for body text, 3:1 for large text and boundaries, per the AA contract); the checker's own fixture is a scratch token pair at 4.4:1 failing with the pair and ratio named, since a near-miss contrast is exactly the failure a lazy audit waves through.

- **A.1.1 -** Author the token artifact with the two themes (light and dark, matching the masters' theme-toggle convention id="theme-toggle" verified in the inspection) and record the checker pass over both themes with every ratio listed; the corner case is a semantic token used both as text color and as a boundary color in different contexts (a single ratio cannot certify both uses), which the token schema handles by declaring the use class per pairing, and the misuse fixture (a text-classed pair at 3.2:1) fails by class, not just by number.

- **A.1.2 -** Implement the breakpoint contract as layout-region declarations (each view declares its regions and how they reflow per class), and record the reflow fixture for the three learner profiles from N26 rendered at each class in the scratch harness: at 320 the exam navigator collapses to a sheet, the practice runner stays single-column, and no region overlaps or clips (the overlap assertion is geometric, computed from the scratch layout model, so it is testable without a browser).

- **A.1.3 -** Implement the target-size floor as a build-time check over the declared interactive controls (every button, input and custom control carries a declared size class), and record the check with the scratch undersized control failing by name; the corner case is a dense inline control (the timer chip) whose visual size is smaller than 44 px, resolved by a declared hit-area padding token rather than shrinking the floor, and the exception is recorded in the token artifact, not silently granted.

**Main Step B - Rework the views onto the token system.** Rework every view's styles (the N06 start screen, the N07 concept map, the practice runner, the exam shell, the revision panel, the settings) onto the tokens and the breakpoint classes: no raw hex values, no absolute font sizes below the floor, no fixed pixel widths that clip at 320, and every interactive element at or above the target floor; the rework is mechanical per view but must preserve the N22 ARIA semantics exactly, since a styling pass is the classic place where role attributes get dropped.

**Subtask B.1 - Prove the rework with the contract checks.** Run the full static contract over the reworked styles: the hex-value scan (only the token layer may name colors), the size scan, the target scan and the contrast checker all pass, and the ARIA parity fixture re-runs N22's component assertions over the reworked markup (every component's role, name and state unchanged from the Phase V record), so the styling pass provably broke nothing.

- **B.1.1 -** Execute the per-view rework with the recorded before-and-after for one representative view (the practice runner, the densest), showing the token substitution and the breakpoint declarations, and run the hex scan over all views with the result recorded; a scratch regression (one view reintroducing a raw hex) fails the scan with the view named.

- **B.1.2 -** Re-run the N22 component parity fixtures over the reworked components and record the pass; the corner case is a component whose styling moved an attribute into a different element (for example the label span restructured for layout), which the parity fixture detects because the accessible name computation changed, and the fixture's failure output names the component and the changed name, preventing the silent degradation screen readers feel but audits miss.

- **B.1.3 -** Run the layout-region reflow fixtures across the three profiles at every breakpoint class and record the geometric results (no overlap, no clip, scroll directions declared), forming the deterministic half of the responsive proof; the browser-rendered half belongs to N37's visual matrix, and this task records the handoff of the region declarations to N37 as its expected-geometry source.

**Main Step C - Integrate with the build and record the ledger.** Integrate the token checks into the N31 pipeline (the build runs the contrast checker and the target scan as gate steps, so an inaccessible token change fails the build rather than reaching the artifact), assemble the reworked CSS through the pipeline, and rebuild: the artifact contract check (N31) re-passes with the new composition table recorded (the CSS sub-budget from Section 1 is watched: 40-80 KiB declared, and the token layer's cost is measured against it).

**Subtask C.1 - Prove the end state with a full rebuild.** The closing proof: two fresh-process rebuilds with the token gates active produce byte-identical artifacts (idempotence survives the new gates), the contract check passes over the final artifact, and the composition table shows the CSS within budget; the ledger records the token artifact, checker and styles digests, and the smoke subset gains one contrast-vector assertion (the token pair table asserted in-file).

- **C.1.1 -** Implement the gate wiring (the N31 build calls the contrast and target checks before assembly and fails fast), and record the gate fixture: a scratch token edit dropping one pair below threshold fails the build with the pair named before any artifact is written, honoring the atomic-write guarantee.

- **C.1.2 -** Run the two-rebuild idempotence proof over the final token set and record identical digests; the corner case is a theme toggle's runtime class swap (the DOM gains a class at toggle time), which must not change any computed static artifact byte (the themes are both fully present in the artifact), and the toggle-parity fixture proves both themes ship complete.

- **C.1.3 -** Append the token, checker and styles digests to the ledger, extend the smoke subset with the contrast vector, record the pass, and hand the expected-geometry region declarations to N37, closing the task with accessibility as a build-time property and the responsive contract ready for browser verification.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the token artifact, when the contrast checker runs over both themes, then every text pair reaches 4.5:1, every boundary pair 3:1, and a scratch 4.4:1 pair fails by pair and ratio, with use-class misuse failing by class.

- **AC2 (negative or edge case):** Given the reworked views, when the static contract runs, then zero raw hex values appear outside the token layer, all targets meet the 44 px floor with declared exceptions, and the N22 ARIA parity fixtures pass unchanged over the reworked markup.

- **AC3 (domain integrity and zero-regression):** Given the gated rebuild, when two fresh-process builds run, then the artifacts are byte-identical, both themes ship complete, the CSS stays within its Section 1 sub-budget, and the smoke contrast vector passes in-file.

**Verification and Evidence:** Record the token ratios for both themes, the reflow geometry tables, the hex, target and ARIA parity scans, the gate failure fixture and the two-rebuild digests with the final composition table. The AA scope statement (contrast, targets, no color-only meaning, with AAA explicitly out of scope) is recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: the token system decaying as later tasks hand-patch styles. Guard: the build-time hex scan makes any bypass a build failure. Rollback: the token layer and checks are additive; reverting styles leaves the Phase V markup semantics intact, but N33 and N37 lose their layout precondition and must re-plan.

**Definition of Done:** A token-driven, build-gated WCAG 2.2 AA contract exists with proven contrast, target sizes and breakpoints across both themes, all views reworked without ARIA regressions, idempotent rebuilds preserved, and the geometry handoff to N37 complete.

### N33 - Implement keyboard-only operation and screen-reader semantics

**Phase:** Phase VII | **Priority:** P1 | **Risk:** High | **Effort:** L | **Dependencies:** N31, N32

**Domain:** Keyboard and assistive technology

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the component contracts (N22) already declare roles, names and states per component; the revision and self-assessment controls carry ARIA patterns (N29's keyboard fixture); AGENTS.md's lite-shot and Falkon rules cover visual checks but no keyboard or screen-reader protocol exists anywhere in the workspace. No focus management, keyboard map or screen-reader test protocol exists.

**Purpose and Rationale:** Keyboard operation must be complete and coherent: every function reachable and operable by keyboard alone, a declared focus model (logical order, visible focus, no traps, focus moved intentionally by every view transition, restored on return per the concept drawer's return-focus rule from N07), a declared keyboard map (the shortcuts, collision-checked), and honest screen-reader semantics (name-role-value correct on every component, landmark structure for the nine sections, live regions for the events that matter: timer thresholds, verdicts, navigation changes); machine-checkable parts are fixtures, and the parts only a human with a screen reader can judge are a documented manual protocol, honestly labeled UNVERIFIED until executed rather than claimed by inference.

**Target Artifacts and Touchpoints:** The keyboard map artifact; the focus-management module (part of the runtime); the a11y checker tools/check_a11y.py; the manual screen-reader protocol document.

**Out of Scope:** No claiming screen-reader success without the manual runs (the protocol stays UNVERIFIED until Phase VIII executes it under N38's environment); no exotic shortcut frameworks; no shortcuts that trap or override browser or assistive-technology keys.

**Main Step A - Define the keyboard map and focus model.** Author the keyboard map artifact: the global shortcuts (few and declared: topic jump, theme toggle, and the section jumps to the nine anchors), the per-view keys (the exam navigator, the practice runner's hint and skip, the drawer close), the modifier rules (no bare-key shortcuts while a text input or select holds focus, the classic typing-trap defect), and the focus contract (visible focus always, focus follows view transitions, focus restores to the invoking control on drawer close, the tab order documented per view); the map is collision-checked (no key doing two things in one context).

**Subtask A.1 - Validate the map and implement the focus module.** Validate the map (every shortcut resolves to exactly one action per context, every interactive element reachable by tab, no element both a tab stop and a shortcut swallow), and implement the focus module (transition, restore, trap-guard: a fixture that walks tab past the end of a drawer and proves focus escapes rather than cycling inside it, since a focus trap inside a modal drawer is the single most common keyboard defect in component UIs).

- **A.1.1 -** Author the map artifact with the context table (exam, practice, revision, settings, drawer-open as contexts; each key's action per context), and record the collision validation including the scratch collision fixture (two actions bound to one key in one context) failing with the key and both actions named.

- **A.1.2 -** Implement the focus module with the transition rule (every view change moves focus to the new view's declared heading, announced) and the restore rule (drawer close returns focus to the invoking control, extending the N07 return-focus rule to every modal surface), and record the escape fixture over the densest drawer (the concept map drawer): tab walks in, through, and out, with the recorded focus sequence proving both entry and escape.

- **A.1.3 -** Implement the modifier rule with the input-guard (shortcuts suppress while typing contexts hold focus), and record the typing fixture: keying the topic-jump letter inside a numeric answer input produces the character in the input, not a navigation jump, since a shortcut firing mid-typing is a data-loss event for a student mid-calculation.

**Main Step B - Implement the a11y checker and fix the semantics.** Implement tools/check_a11y.py: a static semantic checker over the assembled artifact's markup plus the component contracts (every interactive element has an explicit or computed accessible name, every custom control's role matches its N22 contract, landmarks present and unique for the nine sections, headings hierarchical per view, live regions declared only for the event set), and run it: every finding is fixed at the component level (never patched in the assembled artifact, which the build would overwrite).

**Subtask B.1 - Prove name-role-value over every component.** The name-rule proof: for every one of the 18 response types plus every navigation and control component, the checker records the computed name, role and state from the contract (the same computation the browser performs, implemented against the recorded ARIA tree), and the fixture set asserts each against its N22 record; the corner case is the icon-only control (the flag toggle, the drawer close), where the name comes only from the aria-label term, and the fixture proves the label is present, non-empty and term-keyed, since icon-only controls are the canonical name-failure site.

- **B.1.1 -** Implement the checker's name computation over the ARIA tree (explicit labels first, then content, then described fallback) and run it across all components, recording the name table; the scratch fixture is a component with an empty aria-label (the label present but blank, the sneakiest variant), which fails with the component named and the empty label quoted.

- **B.1.2 -** Implement the landmark and heading checks (nine landmarks, one main, headings in order without level skips per view), and record the pass; the corner case is the exam navigator's repeated question summaries (similar elements in a list), resolved by the declared list semantics with named items, and the checker's duplicate-name allowance for list items is documented as an intentional rule rather than a missed deduplication.

- **B.1.3 -** Implement the live-region audit (the declared event set: timer threshold, verdict posted, view changed; each with exactly one live region, polite except the timer threshold at assertive per the exam-context rule), and record the fixture: each event fires once in the harness and the region announces exactly once, since double announcements are as damaging to a screen-reader user as silence.

**Main Step C - Author the manual protocol and record the ledger.** Author the manual screen-reader protocol document: the declared environment (Falkon and the available assistive tooling per the AGENTS.md policy, with the honest statement that full NVDA or VoiceOver verification is UNAVAILABLE in this offline environment unless the executor supplies it), the scripted scenarios (start screen, one practice path with hints, one full graded exam, one revision session with self-assessment, drawer round trips), the expected announcements per scenario (derived from the name table), and the recording format (observed versus expected, with discrepancies filed as defects, not notes).

**Subtask C.1 - Prove the machine-provable half and hand off the rest.** The closing proof is the split evidence: the machine half (keyboard map validated, focus fixtures, name table, landmark and live-region checks) is recorded as VERIFIED through the checker, while the manual half is recorded in the ledger as UNVERIFIED pending the protocol's execution in Phase VIII (N38's environment runs it if tooling permits), so the roadmap never lets inferred accessibility stand in for tested accessibility.

- **C.1.1 -** Author the protocol document with the scenario scripts in execution order and the per-scenario expected-announcement tables, and record its digest in the ledger with the honest UNVERIFIED status; the corner case is a scenario that cannot be completed by keyboard alone (if any is found during the fixture pass), which must be filed as a blocking defect and fixed here, not documented around, and the protocol states this rule explicitly.

- **C.1.2 -** Append the keyboard map, focus module and checker digests to the ledger, run the extended corpus twice for parity, and extend the smoke subset with one keyboard vector (the focus escape sequence asserted in-file over the recorded sequence), recording the pass.

- **C.1.3 -** Hand the protocol and the name table to N38 as its screen-reader execution input, and hand the keyboard map to N37 (visual checks must show the visible-focus indicator, so the map is part of the visual expectations), closing the task with the machine half proven and the human half honestly staged.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the keyboard map artifact, when collision validation runs, then every key resolves to one action per context (a scratch collision fails by key and both actions), typing contexts suppress shortcuts, and tab escapes every drawer.

- **AC2 (negative or edge case):** Given the a11y checker, when it runs over all components, then every interactive element has a non-empty computed name (an empty-label scratch component fails by name), roles match the N22 contracts, landmarks and headings are sound, and live regions fire exactly once per event.

- **AC3 (domain integrity and zero-regression):** Given the split evidence record, when the ledger is written, then the machine half is VERIFIED with fixtures and tables while the manual protocol is recorded UNVERIFIED pending Phase VIII execution, with the smoke keyboard vector passing in-file.

**Verification and Evidence:** Record the collision validation, focus escape and typing fixtures, the full name table across all components, the landmark and live-region results, the gate failure fixture and the smoke pass. The protocol document's scenarios, expected announcements and defect-filing rule are recorded verbatim with its digest.

**Risks, Guardrails, and Rollback Plan:** Risk: fixing component semantics late rippling into the assembled views. Guard: fixes happen at component level with the N32 ARIA parity fixture re-run after each fix, so nothing regresses silently. Rollback: the checker, map and focus module are additive; reverting them restores the Phase V markup, but N37-N38 lose their keyboard precondition and must re-plan.

**Definition of Done:** Complete keyboard operation with a validated map, trap-guarded focus management, machine-proven name-role-value semantics over every component, and an honestly staged manual screen-reader protocol, with fixtures, tables, smoke and ledger evidence complete.

### N34 - Implement the no-JavaScript fallback and the print and paper mode

**Phase:** Phase VII | **Priority:** P2 | **Risk:** Medium | **Effort:** M | **Dependencies:** N31

**Domain:** Progressive enhancement and print

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the masters use @media print conventions (verified in the inspection) and the predecessor plan approved F04 (a printable paper-mode variant: a blank answer sheet and a paper worksheet path); the artifact is fully script-driven at this point, so a no-JS reader sees an empty shell. No static fallback content, no print stylesheet, and no paper-mode artifact exist.

**Purpose and Rationale:** The simulator must degrade honestly rather than break: with JavaScript disabled, the document still shows its identity (title, language, a plain-language explanation that interactive features need scripts, the full concept map as static HTML, the methodology page, and the full reference content that does not need interactivity), because the inspection's own workflow (reading masters without running them) shows that a large part of the value is readable text; and the print mode (F04) delivers a paper worksheet: a blank answer sheet for a chosen form (A, B or C) with the 21 slots, the declared point table, a computation-work grid, and a printable variant of the question set without interactive controls, matching the programme's paper-exam reality.

**Target Artifacts and Touchpoints:** The noscript content block; the print stylesheet layer (assembled by N31); the paper-mode module; the printable form artifact. Touchpoint in output/simulator.html: noscript block, the #druka section, @media print rules.

**Out of Scope:** No claiming full interactivity without scripts (the fallback states its limits plainly); no auto-printing or print spying of any kind; no OCR or answer-scanning feature (the paper sheet is filled by hand and graded by hand against the rubric).

**Main Step A - Implement the static fallback content.** Implement the noscript block: a visible notice (Latvian, term-keyed) explaining that scripts are disabled and interactive practice, exams and grading are unavailable, followed by the static content that still works: the full concept map (the N07 graph rendered as nested lists with anchor links, since a graph without scripts is an outline), the methodology page, the terminology reference (the full sim-terms island rendered as a static table), and the honest statement of what remains hidden (the bank, the vectors, the analytics, all script-only).

**Subtask A.1 - Prove the fallback is honest and complete.** The fixture proof: with the script element removed in the scratch harness, the document still parses, every static section anchor resolves, every link in the static content is internal (the offline rule holds trivially, but the scan re-runs), and the notice appears exactly once; the corner case is a learner with scripts partially enabled (a blocker extension), which cannot be detected reliably, and the fallback copy is written to be true in the scripts-off case without asserting anything about partial states, so it never lies.

- **A.1.1 -** Author the noscript block with its static renderings derived from the same islands the runtime consumes (single sourcing: the static concept list and term table are generated from the islands by the N31 build, so a content change propagates to both), and record the generation fixture: a scratch island edit appears identically in the runtime island and the static table, proving no drift.

- **A.1.2 -** Implement the static concept-map rendering as nested lists with the anchor links preserved (the ASCII anchors from N07), and record the link-integrity check over the static output: every internal link resolves in the noscript document, run by the N31 checker extended with a noscript pass, with a scratch dangling link failing by name.

- **A.1.3 -** Implement the honest-limits copy with the term bank and record its lint pass; the corner case is the print section itself (a learner might print from the no-JS state), which the noscript copy must mention as still available, and the cross-reference between the two features is recorded so neither copy strands the other.

**Main Step B - Implement the print stylesheet and the paper worksheet.** Implement the print stylesheet: @media print rules that hide interactive chrome (navigation, buttons, the timer), keep the content flowing in black-on-white with the print-safe tokens (the N32 token system gains a print theme class), avoid page breaks inside questions and figures (break-inside rules declared per block), and expand the drawers (their content prints in reading order); and implement the paper worksheet (F04): a form-selection control (in the settings and the #druka section) that generates the printable sheet for form A, B or C from the frozen forms island, with the 21 slots in exam order, the point table, the answer blanks sized for handwriting, and a computation grid.

**Subtask B.1 - Prove the print output is paper-true.** The fixture proof: the printable form generation is deterministic (form A always yields the same sheet, digest compared, since a teacher must be able to print the same form twice), the sheet's 21 slots match the N24 assembly record exactly (slot order, point values, types), and the print stylesheet's rule set is validated (every hidden selector matches an existing element class, every break rule targets a declared block, checked by the static checker extended with a print pass, since a print stylesheet that hides nothing because of a selector typo is invisible until a teacher wastes paper on it).

- **B.1.1 -** Implement the print theme tokens (black-on-white, the link URLs hidden or shown per the declared policy, decided for the paper use case and recorded) and record the print-token pass through the N32 contrast checker in its print mode; the corner case is the SVG figures at print size (the energy and titration diagrams), whose print rendering must not scale into illegibility, and the declared figure print sizes are recorded with their rationale.

- **B.1.2 -** Implement the paper worksheet generator from the forms island, and record the determinism digest plus the slot-parity fixture against N24's record; the corner case is form shortage (a form whose assembly failed review, leaving it absent): the #druka selector lists only forms actually present in the frozen island, never a dead option, and the empty-state fixture is recorded.

- **B.1.3 -** Implement the print-rule static validation in the checker and record the pass with a scratch unmatched selector failing by name; then record the print fixture for the worksheet: the scratch print render (the checker's DOM model, since no physical printer exists here) shows the sheet's content in order with interactive chrome absent, and this geometric record is handed to N37's visual matrix as the print-class expectation.

**Main Step C - Prove the modes do not contaminate each other and record evidence.** Prove mode isolation: the noscript state, the screen runtime, and the print mode share content but never state (the worksheet is generated, never answered; the no-JS reader's view shows zero interactive controls that would dead-end), and the full-mode fixture runs all three render paths over the same frozen data (a script-off parse, a screen render, a print render) with their three outputs recorded and none containing another mode's controls; the smoke subset gains one print vector (the worksheet's slot list asserted in-file).

**Subtask C.1 - Prove the fallback serves the offline promise.** The capstone proof is the degradation honesty audit: with scripts disabled the document still delivers the concept map, the methodology, and the terminology (the three highest-value static contents, named in the audit), states its limits truthfully, and links to nothing that requires scripts; the audit table is recorded, and it closes F04's implementation with the paper path and the fallback both real rather than decorative.

- **C.1.1 -** Implement the three-mode render harness in the scratch harness and record the three outputs' key properties (parse pass, link resolution, absence of cross-mode controls), with the corner case of the theme toggle in print (printing should not carry the dark theme), covered by the print theme class and asserted in the fixture.

- **C.1.2 -** Append the noscript generator, print stylesheet and worksheet module digests to the ledger, run the extended corpus twice for parity, and record the fallback and print layers' byte contributions against the CSS and template budgets from Section 1, keeping the paper path's cost visible.

- **C.1.3 -** Extend the smoke subset with the print vector, record the pass, and hand the print-class expectations to N37's visual matrix and the noscript pass to N39's QA runner, closing the task with both degradation paths honest and evidence-complete.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the noscript document, when scripts are disabled, then the notice, static concept map, methodology and terminology render with every link resolving, the content is single-sourced from the islands, and the copy states limits truthfully.

- **AC2 (negative or edge case):** Given the paper worksheet generator, when form A is generated twice, then the sheets are digest-identical, the 21 slots and point table match the N24 record, absent forms never appear as options, and print rules all match existing selectors.

- **AC3 (domain integrity and zero-regression):** Given the three-mode fixture, when script-off, screen and print renders run over one frozen data set, then no mode carries another's controls, print carries the print theme, the degradation audit passes, and the smoke print vector passes in-file.

**Verification and Evidence:** Record the generation and link-integrity fixtures, the worksheet determinism digests and slot parity, the print-rule validation with its failure fixture, the three-mode outputs, the degradation audit table and the smoke pass. The noscript notice copy and the honest-limits copy are recorded verbatim in Latvian.

**Risks, Guardrails, and Rollback Plan:** Risk: the static fallback drifting from the islands as content evolves. Guard: single-sourced generation through the build, with the drift fixture re-run at every build. Rollback: the noscript, print and worksheet layers are additive; removing them restores the script-only artifact, but F04 re-opens and N37's print-class expectations lose their source and must re-plan.

**Definition of Done:** An honest no-JavaScript fallback with single-sourced static content, a validated print stylesheet, and the F04 paper worksheet with deterministic, slot-parity-proven forms exist, with mode-isolation fixtures, the degradation audit, smoke and ledger evidence complete, and expectations handed to N37 and N39.

### N35 - Run the performance, storage and security audit

**Phase:** Phase VII | **Priority:** P1 | **Risk:** High | **Effort:** M | **Dependencies:** N31, N32, N34

**Domain:** Performance, storage and security

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the artifact exists and is reproducible (N31); AGENTS.md mandates in-memory sessions by default and offline operation; the store (N25) is opt-in, versioned and privacy-audited; the runtime renders everything from islands. No performance budget, storage budget enforcement or security audit (serialization, injection, DOM XSS) has been performed on the assembled artifact.

**Purpose and Rationale:** The artifact must be proven fast enough, storage-honest and injection-safe before Phase VIII blesses it: a performance budget (declared targets for parse time, first interactive render and per-interaction latency, measured in the scratch harness with a deterministic workload, since no browser timing is trustworthy enough to gate on here), a storage budget (the store's declared key set and size caps from N25 re-audited against the finished runtime's actual writes), and a security audit with two engines: a serialization lint (every JSON.parse wrapped, every storage write schema-checked, every innerHTML usage inventoried and justified or replaced) and an injection corpus (a bank of adversarial strings in Latvian text fields, term fields and answer inputs, proving the renderers treat all runtime text as data).

**Target Artifacts and Touchpoints:** tools/audit_perf.py, tools/audit_storage.py, tools/audit_security.py (new); the audit report artifact. Touchpoints: the runtime's render paths, the store, the serialization helpers.

**Out of Scope:** No penetration-testing claims beyond the declared scope (client-side XSS and storage hygiene only; there is no server to audit); no CDN or third-party script to audit (none exist, by design); no tracking of real learners (the perf workload is synthetic).

**Main Step A - Implement the performance and storage audits.** Implement the performance audit: a declared budget table (island parse under a declared ceiling given the bank's real size, first render of the start screen under a declared ceiling, per-interaction render latency under a declared ceiling for the densest views: the exam navigator and the revision panel), measured over a synthetic workload (the full real bank loaded, the three learner profiles from N26, scripted interactions) in the scratch harness with results recorded; and the storage audit: instrument the store's every write (key, schema conformance, byte size), run the full learner journey from N30's trace, and record the store's maximum footprint against the declared caps.

**Subtask A.1 - Prove budgets hold and catch the corners.** The fixture proof: the budget table's every row passes with the measured values recorded beside the ceilings, and the failure path is proven with a scratch degradation (a view re-rendered per keystroke, the classic defect) which the audit must flag as exceeding the per-interaction ceiling, since a perf audit that cannot detect a known-bad pattern cannot be trusted to detect unknown ones; the storage corner case is the free-text note's declared maximum (N29) interacting with the event log cap (N25), and the journey's recorded footprint proves the caps compose rather than multiply.

- **A.1.1 -** Implement the perf harness with the synthetic workload generator (deterministic: seeded from the N05 policy, so the workload itself is reproducible) and record the three budget rows with their measured values; the corner case is the largest bank state (all 112 instances eligible), which the workload includes explicitly, since average-case budgets hide worst cases exactly when a real exam is on the line.

- **A.1.2 -** Implement the storage instrumentation (a write log capturing key, bytes and schema verdict per write) and record the journey footprint table; a scratch schema-violating write (a module writing an undeclared key) must fail the audit with the key and the writing module named, since undeclared keys are both a privacy question and a migration hazard.

- **A.1.3 -** Run the degraded scratch fixture (the per-keystroke re-render) and record the audit's detection, then fix the pattern's cause in the real runtime (if present) and re-run: the recorded before-and-after proves the audit and the runtime co-evolved rather than the audit being theater.

**Main Step B - Implement the serialization lint and run it.** Implement the serialization lint: inventory every JSON.parse call (each must be wrapped with the declared error handler, since a corrupted island must degrade to a visible error, never a silent blank), every storage read and write (schema-checked through the N25 store, no direct access), and every innerHTML or markup-building site in the runtime (each inventoried with its justification: the site renders either trusted build-time markup or runtime text through the escaping helper; any site that cannot justify itself is refactored to textContent or the escape helper before the audit passes).

**Subtask B.1 - Prove the inventory is exhaustive and the handlers work.** The proof of exhaustiveness: the lint's site list is generated by scanning the sources (not hand-maintained), and its count is asserted against the module map so a new render site added later fails loudly; the corrupted-island fixture proves the wrap: a scratch island with truncated JSON fails into the declared error state (a visible, Latvian, honest message naming the island) rather than an exception or a blank page; the corner case is an island that parses but is structurally wrong (a missing key), which the schema validator (N04's loader rules) catches downstream, and the fixture proves the two failure modes produce distinct, correct errors.

- **B.1.1 -** Implement the innerHTML inventory scanner over the runtime sources and record the site table with each site's justification class (static, escaped, or refactored); the scratch fixture is a new unjustified site planted in a scratch copy, which the scanner must find and fail, proving the inventory is a scan and not a stale list.

- **B.1.2 -** Implement the escape helper as the single runtime text path (term lookups, feedback text, learner notes, self-assessment notes: all runtime-origin strings pass through it) and record the helper's unit corpus: the Latvian alphabet plus markup metacharacters through the helper, with byte-exact escaped outputs recorded, so the helper is itself regression-frozen.

- **B.1.3 -** Run the corrupted-island and wrong-structure fixtures and record both error states (distinct, named, honest); the corner case is the noscript path (N34) where no parse occurs at all, and the fixture asserts the static content renders regardless of island corruption, since the fallback must not inherit the runtime's failure modes.

**Main Step C - Run the injection corpus and record the audit report.** Run the injection corpus: a declared adversarial string bank (markup metacharacters, angle-bracket payloads, quote payloads, and Latvian-text edge cases like the long o with the macron, s and z with the cedilla, which are exactly the characters naive byte-level handling mangles) injected through every runtime text channel (answer inputs, free-text notes, term lookups, file names in the import path), with the rendered outputs asserted to contain the payloads as visible text only: zero script execution, zero markup interpretation, zero storage corruption, and the corpus results recorded per channel.

**Subtask C.1 - Compile the audit report and close Phase VII.** Compile the audit report artifact: the budget tables, the footprint table, the site inventory, the helper corpus, the corruption fixtures and the injection results, each with its epistemic status (the scratch-harness measurements are VERIFIED as harness measurements, honestly labeled as not browser timings, with browser-side confirmation staged for N38's smoke); the report's digest enters the ledger, the smoke subset gains one escape-helper vector, and Phase VII closes with the artifact proven to budget, storage-honest and injection-safe in every machine-checkable dimension.

- **C.1.1 -** Author the injection corpus artifact with its channel matrix (every runtime text channel crossed with every payload class) and record the full run: per channel, the payload rendered as text, the storage round-trip byte-identical, and zero execution markers in the harness's instrumentation; the corner case is the import path (N25's export and import), where a malicious file is untrusted input by definition, and the corpus proves import validates and escapes before any render, with the malicious-file fixture recorded.

- **C.1.2 -** Compile the audit report with the epistemic labels per section and append its digest, the audit tool digests and the refactored module digests to the ledger, running the extended corpus twice for parity; the corner case is an audit finding that requires a runtime change (a refactored site), which re-triggers the N31 rebuild and the N32 gates, and the recorded chain proves the audit's findings flowed back through the pipeline rather than being patched in the artifact.

- **C.1.3 -** Extend the smoke subset with the escape-helper vector, record the pass, and hand the audit report and the budget table to N38 and N39 as their baseline (the smoke run re-asserts the budgets in its own environment), closing Phase VII with all machine-checkable robustness dimensions proven and recorded.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the perf and storage audits, when the synthetic workload and journey run, then every budget row passes with values recorded (a planted per-keystroke defect is detected), undeclared keys fail by name, and the footprint respects the caps.

- **AC2 (negative or edge case):** Given the serialization lint, when the source scan runs, then every parse, storage and markup site is inventoried with justification (a planted unjustified site fails), corrupted islands degrade to distinct honest errors, and the noscript path is immune.

- **AC3 (domain integrity and zero-regression):** Given the injection corpus, when all channels run all payloads, then everything renders as visible text with zero execution or corruption, imports validate untrusted files, the audit report carries honest epistemic labels, and the smoke vector passes.

**Verification and Evidence:** Record the budget and footprint tables, the site inventory, the escape-helper corpus, the corruption and injection results per channel, the refactoring chain through the rebuild, and the smoke pass. The report's epistemic labels distinguish harness measurements from browser measurements verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: audit scripts aging as the runtime grows in Phase VIII fixes. Guard: the inventories are scans, and N39's runner re-executes all three audits; a new site or key fails the gates. Rollback: the audit tools are read-only over sources; any runtime refactor they trigger is individually revertible, with the pre-audit artifact rebuildable from the ledger's recorded source digests.

**Definition of Done:** A complete performance, storage and security audit exists with budget tables held, storage writes fully declared and schema-checked, serialization sites exhaustively inventoried with corruption-proof degradation, and an injection corpus passed across every runtime text channel, with the report, smoke and ledger evidence closing Phase VII.


## 14. Phase VIII (N36-N40) - Property Tests, Visual Matrix, Offline Smoke, QA Runner and Release Gate

Phase VIII proves the artifact: the property and mutation test suites against the golden corpus (N36); the visual regression matrix across the viewport and theme grid under the lite-shot and Falkon policy (N37); the cross-engine offline smoke with staged manual protocols (N38); the reproducible QA runner with its SHA-256 evidence chain and independent verifier (N39); and the ten-point release gate execution with conflict-ledger closure and human sign-off (N40). When this phase closes, the roadmap is done: the simulator is released with a complete, replayable evidence chain and an honestly closed ledger.

### N36 - Build the property and mutation test suites against the golden corpus

**Phase:** Phase VIII | **Priority:** P0 | **Risk:** High | **Effort:** L | **Dependencies:** N17, N20, N23, N31

**Domain:** Automated testing

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the golden vectors (N05) exist with the oracle-independent, cross-language-deterministic policy; the engines (N17, N18, N19) are pure and fixture-tested; the bank (N20) is frozen with its digest in the ledger; the artifact is reproducible (N31). No property-based test suite, no mutation testing, and no automated regression corpus exist.

**Purpose and Rationale:** Property tests assert invariants rather than examples: for the quantity and conservation engines, algebraic properties (identity inputs, round-trip unit conversions, tolerance monotonicity: a tolerated answer at the tolerance edge remains correct at any smaller deviation, and drops out beyond it, with no cliff zones); for the grading engines, verdict properties (any golden vector grades correct under the full pipeline exactly as the oracle record states, digest-compared); for the assembly, fairness properties (a seeded form draw over many seeds touches every family with the expected frequency band, and no family appears twice in one form); mutation testing then proves the suites bite: a corpus of hand-crafted mutants (a tolerance sign flipped, a rounding step removed, a family filter inverted) is injected one at a time, and every mutant must be killed by at least one test, since a suite that survives a planted bug certifies nothing.

**Target Artifacts and Touchpoints:** tools/property_tests.py and tools/mutation_tests.py (new); the mutant corpus artifact; the test manifest.

**Out of Scope:** No coverage-percent vanity metric as a gate (the gate is mutants killed and properties held, not line counts); no random fuzzing without oracles (every property must state its expected relation before it runs); no browser tests here (those are N37 and N38).

**Main Step A - Author the property suite over the engines.** Author the property suite: unit-conversion round trips (every conversion pair in the conventions artifact in both directions, exactly reversible in exact arithmetic and within declared tolerance in the engines' decimal handling), tolerance-band monotonicity (for a sample of every family: the verdict is correct at zero deviation, correct at 0.9 times tolerance, incorrect at 1.1 times tolerance, and the sweep between is recorded as the declared behavior, cliff-free), conservation properties (the conservation engine's balancing relation holds for generated stoichiometry cases: the mass balance the engine asserts is independently recomputable from the conventions' atomic masses), and assembly fairness (the N24 draw over a declared seed set produces family frequencies inside the declared band with no per-form duplicates, asserting the seeding policy end to end).

**Subtask A.1 - Prove properties hold and are honest.** Run the suite and record every property's result with its sample size; the honesty fixture is the deliberately broken property (a scratch tolerance set with a cliff at 0.5 times tolerance, a planted defect), which the monotonicity sweep must detect and report with the deviation point named, since a monotonicity test that cannot find a planted cliff is decorative.

- **A.1.1 -** Implement the round-trip property with the conventions artifact as its only source of conversion facts (single-sourced: the property reads the artifact, so a convention change re-tests automatically) and record the full pair table pass; the corner case is the temperature-style affine conversions if any exist in the conventions (offset conversions do not round-trip through naive inversion), handled by the artifact's declared conversion class per pair, and the class-aware fixture is recorded.

- **A.1.2 -** Implement the tolerance sweep over a per-family sample (seeded per the N05 policy so the sample is reproducible) with the verdict recorded at each step, and record the sweep table for the seven topic families; the corner case is a family whose tolerance is expressed in significant figures rather than absolute units (the conventions' two tolerance classes), and the sweep handles both classes through the same engine path the graders use.

- **A.1.3 -** Implement the conservation recompute (an independent balance calculation written directly from the conventions' masses, not calling the engine's own code, so the property is a genuine second opinion) and record the agreement across the generated stoichiometry sample; a planted mass error in a scratch conventions copy must be detected and named, proving the second opinion has teeth.

**Main Step B - Author the mutation corpus and the kill proof.** Author the mutant corpus: a declared set of source mutations, each a single semantic change with its expected killer class (a tolerance sign flip must die at the sweep property; a removed rounding step at the golden-vector comparison; an inverted family filter at the fairness property; a swapped criterion weight at the partial-credit property; a broken escape-helper path at the helper's own corpus from N35), and implement the mutation runner: apply one mutant to a scratch copy of the sources, run the full test suite, record killed or survived, restore, repeat; the gate is every mutant killed with at least one test identified by name.

**Subtask B.1 - Prove the suite bites and measure it honestly.** Run the corpus and record the kill table (mutant, killer test, expected class, verdict); a surviving mutant is a blocking defect: either the suite gains the test that kills it or the mutant's premise was wrong and the corpus entry is corrected with the reasoning recorded, since a quiet corpus shrink is how mutation regimes rot; the corner case is an equivalent mutant (a change with no observable behavior difference, for example a refactored-but-identical expression), which is recorded in the table as equivalent with its analysis rather than pretending it was killed, keeping the metric honest.

- **B.1.1 -** Author the corpus artifact with each mutant's location (module, function, the exact semantic change) and its expected killer class, and record the artifact validation: every mutant's location resolves in the real sources, since a mutant against a renamed function is a silent skip; the scratch fixture is a mutant pointing at a nonexistent function, which the validator must reject by name.

- **B.1.2 -** Implement the mutation runner with strict hygiene (scratch copy, run, restore, and a digest assertion that the restored tree matches the original, since a mutation harness that leaks a mutant into the real sources is itself a catastrophic defect) and record the digest assertions across the full run; the leak fixture is a deliberately unrestored run which the harness's exit check must flag.

- **B.1.3 -** Run the full corpus and record the kill table; for every surviving or equivalent mutant, record the resolution (new test or reasoned correction) and re-run until the table is fully resolved, with the final table as the suite's bite certificate and the kill count recorded in the ledger.

**Main Step C - Run the full regression corpus and record evidence.** Run the full regression corpus end to end: the property suite plus the golden-vector pipeline comparison (every vector through N17, N18 and N19's engines, verdict-for-verdict against the oracle records, digest-compared, cross-checked against the N05 cross-language determinism records), plus the smoke subset, in one command with one exit code, and record the manifest (test ids, results, durations, source digests of everything under test) so the run is a replayable fact rather than a console scroll.

**Subtask C.1 - Prove determinism of the tests themselves.** The closing proof: the entire corpus runs three times in fresh processes over the same artifact digest, and every result is identical (no flaky properties, no seed drift, no time dependence, since the N05 seeded-sample policy and the injected clocks make the whole suite time-deterministic by construction); the three run manifests are recorded, and the corpus is handed to N39 as the first registered suite.

- **C.1.1 -** Implement the manifest writer (a structured record per run: artifact digest, test ids in order, pass and fail counts, per-test verdicts, wall duration) and record the first full run; the corner case is a failing test mid-run: the corpus continues (collecting the full failure picture) rather than aborting at the first red, since one failure hiding five more is a diagnosis tax Phase VIII should not pay.

- **C.1.2 -** Implement the golden-vector pipeline comparison with digest equality over the verdict sequence (the vectors' oracle records are fixed by N05, so any engine change that alters any verdict flips the digest and dies here), and record the digest match plus its cross-language note (the N05 oracle records stand as the independent reference, and the comparison re-proves the contract on the final engines).

- **C.1.3 -** Run the three-run determinism proof, record the three manifests, append the suite, corpus and manifest digests to the ledger, and hand the suite contract to N39, closing the task with the automated half of Phase VIII's verification standing on evidence.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the property suite, when it runs over the conventions, families and seeds, then round trips, tolerance sweeps, conservation recomputes and fairness bands all pass, and a planted tolerance cliff is detected and named.

- **AC2 (negative or edge case):** Given the mutant corpus, when the mutation runner executes it, then every mutant is killed by a named test (or recorded as equivalent with analysis), scratch hygiene digests hold with the leak fixture detected, and no mutant escapes into the real sources.

- **AC3 (domain integrity and zero-regression):** Given the three fresh-process runs, when the full corpus executes, then manifests are identical (verdict sequences digest-equal), the golden vectors match their oracles verdict-for-verdict, and the manifest and suite digests enter the ledger.

**Verification and Evidence:** Record the property result tables with sample sizes, the sweep tables per family, the conservation agreement record, the kill table with resolutions, the three run manifests and the golden-vector digest match. Epistemic status: the suite is VERIFIED as executed on 2026-11-16's toolchain; the ledger records the Python version alongside the digests.

**Risks, Guardrails, and Rollback Plan:** Risk: property tests passing while the assembled artifact diverges from the sources under test. Guard: every manifest records the artifact digest, and N39's runner asserts it before testing. Rollback: the suites are additive tooling; removing them leaves the artifact intact, but N39 loses its primary suite and N40's gate loses its evidence base, so the phase must re-plan rather than regress.

**Definition of Done:** A property suite over conversion, tolerance, conservation and fairness invariants plus a mutation corpus with a full kill table and a three-run deterministic manifest exist, with the golden vectors re-proven verdict-for-verdict, closing the automated-testing half of Phase VIII with evidence.

### N37 - Run the visual regression matrix with the lite-shot and Falkon policy

**Phase:** Phase VIII | **Priority:** P1 | **Risk:** High | **Effort:** L | **Dependencies:** N32, N34

**Domain:** Visual regression

**Current State and Evidence:** `VERIFIED (2026-11-16)`: AGENTS.md permits visual checks via lite-shot with Falkon and forbids Chrome use without explicit authorization; the responsive contracts (N32) provide region geometry expectations; the print mode (N34) provides print-class expectations; the master workspace has no visual regression tooling, matrix or baseline set. `UNAVAILABLE`: full multi-browser visual coverage (Falkon is the one authorized engine here, recorded honestly).

**Purpose and Rationale:** Visual regression proves the layout contract in the one authorized rendering engine and stages the rest honestly: a screenshot matrix over the declared states (the three learner profiles), views (all nine anchors), breakpoints (320, 390, 768, 1280), themes (light and dark) and modes (screen and print-class render of the F04 worksheet), captured with lite-shot driving Falkon per the AGENTS.md rule; each capture is compared against a frozen baseline with a declared pixel-difference threshold, differences classified (expected, regression, or environment noise), and the matrix result recorded; because only Falkon is authorized, the coverage claim is scoped to Falkon honestly, and the cross-engine question is delegated to N38's smoke with its own epistemic label rather than smuggled in here.

**Target Artifacts and Touchpoints:** tools/visual_matrix.py (new); the baseline artifact set; the matrix report. Environment: lite-shot plus Falkon per AGENTS.md.

**Out of Scope:** No Chrome, Chromium or unauthorized engine use (the AGENTS.md rule is absolute and the roadmap states the limitation plainly); no pixel-perfect cross-browser claims; no screenshot storage of learner data (the profiles are synthetic fixtures).

**Main Step A - Build the capture harness under the authorized policy.** Implement the capture harness: drive Falkon through lite-shot per the AGENTS.md rule (headless capture at each matrix cell's declared viewport, a deterministic wait condition on the view's readiness marker rather than a fixed sleep, the theme set through the runtime's toggle before capture, and the print-class capture taken through the print stylesheet's declared path), with every cell's parameters declared in a matrix definition artifact (state, view, breakpoint, theme, mode) so the matrix itself is data, not a script's implicit loops.

**Subtask A.1 - Validate the harness before trusting its output.** The harness validation: a smoke capture (the start screen at 1280, light theme) must produce a stable image across two consecutive runs (a perceptual digest compared within the declared threshold, since rendering noise exists even in one engine, and the threshold must be calibrated on a same-state pair, not guessed); the readiness-marker fixture proves the wait condition (a scratch view that never signals readiness fails the capture with a timeout error rather than capturing a half-drawn frame, since a half-drawn baseline poisons every future comparison).

- **A.1.1 -** Implement the matrix definition artifact (every cell enumerated: 3 profiles, 9 views, 4 breakpoints, 2 themes, plus the print-class cells, with the declared capture parameters per cell) and record its validation: every view id resolves to an anchor, every profile resolves to a store fixture, since a matrix cell pointing at a missing view is a silent skip; the scratch dangling-cell fixture fails by cell name.

- **A.1.2 -** Implement the capture driver with the readiness contract (each view exposes a render-complete marker per the N22 and N32 contracts, and the driver waits on it), and record the smoke capture's two-run stability digest with the calibrated threshold; the corner case is the theme toggle's transition (a mid-transition capture catching mixed themes), which the driver's wait-on-toggle rule prevents, and the fixture records the toggle completion signal.

- **A.1.3 -** Implement the print-class capture path (the worksheet rendered through the print stylesheet's rules as Falkon applies them) and record the first print capture against the N34 geometric expectations, with the declared figure sizes (the SVG diagrams) asserted present and legible at the print scale, since the print mode's whole value collapses if the figures print at postage-stamp size.

**Main Step B - Freeze the baselines and run the comparison.** Capture the full matrix and freeze the baseline set: each cell's image enters the baseline artifact with its digest, its capture parameters and its date; then the comparison pass: re-capture the matrix over the same artifact digest and compare every cell against its baseline (perceptual difference computed, threshold applied, differences classified with a human-review flag for anything above threshold), and record the matrix report (per-cell verdict, the failing cells' regions, the classification).

**Subtask B.1 - Prove the comparison catches real regressions.** The regression proof: a planted visual defect (a scratch build with one view's region overlap reintroduced, the N32 defect class) must be caught by the comparison with the cell and the differing region named; and a planted noise case (a one-pixel antialiasing jitter in a text block) must classify as noise within the threshold rather than a regression, proving the threshold separates defects from rendering jitter rather than crying wolf.

- **B.1.1 -** Freeze the baselines over the artifact digest from N31 (recorded per image) and record the baseline manifest with its composite digest in the ledger; the corner case is a baseline that must be legitimately updated (a deliberate design change in Phase VIII's own fixes): the update is a versioned event with the old and new images' digests recorded and the reason stated, never a quiet overwrite, since silent baseline drift is how visual suites become yes-machines.

- **B.1.2 -** Implement the comparison with perceptual differencing and the region report (the bounding areas of difference, so a human review sees where, not just that) and record the full matrix report; the scratch planted-overlap run is recorded with its failing cell and region, and the noise fixture with its pass, both as the comparison's calibration certificate.

- **B.1.3 -** Run the full matrix over the final artifact and record the pass (or the defect list with resolutions, each defect fixed at source and the matrix re-run until green), with the final matrix report and the baseline composite digest as the visual half of Phase VIII's evidence.

**Main Step C - Record the honest coverage claim and hand off.** Record the coverage claim honestly: the matrix proves the layout contract in Falkon under lite-shot per the AGENTS.md authorization, on the declared viewports and themes, as of the recorded date; it does not prove Chrome, Safari or Firefox behavior (Chrome is explicitly forbidden without authorization, and the others are UNAVAILABLE in this environment), so the cross-engine question is handed to N38's smoke as an explicitly scoped follow-up; the matrix report's epistemic header states the engine and the authorization rule verbatim.

**Subtask C.1 - Prove the matrix is replayable and close.** The replay proof: the matrix runs twice over the same artifact digest in fresh processes and every cell's comparison verdict is identical (the harness is deterministic given the engine), with both runs' composite results recorded; the matrix report, baseline manifest and harness digests enter the ledger, and the matrix is registered with N39's runner as the visual suite.

- **C.1.1 -** Author the epistemic header for the matrix report (engine, authorization citation from AGENTS.md, viewports, themes, date, artifact digest, and the explicit out-of-scope engines named) and record it verbatim, since an honest scope statement is the difference between evidence and overclaim in visual testing.

- **C.1.2 -** Run the two-run replay proof, record the identical composite verdicts, and append the matrix report, baseline manifest and harness digests to the ledger, running the extended corpus twice for parity as usual.

- **C.1.3 -** Register the matrix with the N39 runner (suite id, invocation command, expected exit codes, runtime estimate) and record the registration, closing the task with the authorized-engine visual contract proven, baselined and honestly scoped.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the matrix definition artifact, when the harness runs, then every cell resolves (a dangling cell fails by name), readiness waits hold (a never-ready view times out loudly), and the smoke capture is stable across two runs at the calibrated threshold.

- **AC2 (negative or edge case):** Given the frozen baselines, when the comparison runs over the planted overlap and noise fixtures, then the overlap is caught with cell and region named while the jitter classifies as noise, and the final matrix is green over the final artifact.

- **AC3 (domain integrity and zero-regression):** Given the two-run replay over one artifact digest, when composite verdicts are compared, then they are identical, the epistemic header names Falkon and the out-of-scope engines verbatim, and the suite registers with the N39 runner.

**Verification and Evidence:** Record the matrix definition validation, the calibration certificates, the baseline manifest with its versioned update rule, the regression and noise fixtures, the final matrix report and both replay runs. The epistemic header and the AGENTS.md authorization citation are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: baseline rot as legitimate changes land. Guard: versioned baseline events with recorded reasons and digests; the matrix fails closed on an unexplained digest change. Rollback: the matrix and baselines are additive; removal leaves the artifact intact, but N39 loses the visual suite and N40's gate loses its visual evidence, so the phase re-plans instead.

**Definition of Done:** A deterministic, policy-authorized visual regression matrix over profiles, views, breakpoints, themes and print cells exists with calibrated comparison, frozen versioned baselines, planted-defect and noise certificates, an honest scoped coverage claim, and registration with the QA runner complete.

### N38 - Run the cross-engine offline smoke and the staged manual protocols

**Phase:** Phase VIII | **Priority:** P1 | **Risk:** High | **Effort:** M | **Dependencies:** N37

**Domain:** Offline smoke and manual verification

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the artifact is offline by construction (N31's zero-URL contract); Falkon is the one authorized engine (AGENTS.md, restated in N37); the smoke subset (in-file assertions over vectors, mastery, remediation, revision, print and escape helpers) exists from Phases IV-VII; the manual screen-reader protocol (N33) and the browser-side perf confirmation (N35) are staged unexecuted. `UNAVAILABLE`: Chrome without authorization; other engines and assistive tooling in this offline environment.

**Purpose and Rationale:** The smoke run proves the artifact alive and correct outside the scratch harness: Falkon loads output/simulator.html from the local filesystem, the nine sections render, a scripted interaction pass (a practice item answered, a hint opened, an exam started, navigated, submitted, the report rendered) executes against the real DOM, the offline contract is asserted live (the network instrumentation from N25 records zero attempts during the whole run), and the runtime's own smoke subset executes in the browser and passes; where the environment cannot verify something (other engines, full screen-reader passes, real printer output), the task runs what is authorized, records the results with their true labels, and stages the remainder as an explicit, honestly-labeled manual checklist for the release gate rather than claiming it.

**Target Artifacts and Touchpoints:** tools/smoke_browser.py (new); the smoke report artifact; the staged manual checklist. Environment: Falkon per AGENTS.md.

**Out of Scope:** No Chrome or unauthorized engine; no network access at any point (the smoke asserts its absence); no claiming manual protocol completion without a recorded execution trace; no synthetic pass invented for an unavailable engine.

**Main Step A - Build the browser smoke runner.** Implement the browser smoke runner: launch Falkon per the AGENTS.md rule against the local file (no server, no network, honoring the offline rule absolutely), wait on the document's readiness marker, then execute the scripted pass: assert the nine anchors reachable and the seven islands loaded, execute the interaction script (answer a practice item with a known vector input, open the hint drawer, close it with focus restored, start an exam form, flag a slot, navigate, submit, receive the report), and collect the runtime's own smoke subset results from the browser context, plus the network instrumentation log (which must be empty).

**Subtask A.1 - Prove the runner fails loudly on real defects.** The runner's calibration: a scratch artifact with one broken island (the corruption case from N35) must fail the smoke with the island named; a scratch artifact with the submit handler unbound must fail at the interaction step with the step named, since a smoke runner that passes a dead submit button is worse than no runner at all; both failure fixtures are recorded with their exact outputs.

- **A.1.1 -** Implement the runner's readiness and island assertions over the real DOM (the same seven island ids and nine anchors from the artifact contract) and record the first clean pass; the corner case is the file:// context's storage quirks (some engines restrict localStorage under file://, the exact case the in-memory default policy from AGENTS.md anticipates), and the runner asserts the store degrades to in-memory with the honest settings notice, never an unhandled exception, and the degradation record is the fixture's expected outcome.

- **A.1.2 -** Implement the scripted interaction pass with one known-vector practice item (its expected verdict precomputed from the N05 records, so the browser run checks real engine output against the frozen oracle) and record the verdict match; the corner case is the focus-restore assertion mid-script (the hint drawer close from N33), asserted in the browser rather than only in the harness, closing the loop between the two environments.

- **A.1.3 -** Implement the network-log collection (the N25 instrumentation read out at run end, asserted empty) and the failure fixtures (the broken island and the dead submit) with their outputs recorded, calibrating the runner before its results are trusted.

**Main Step B - Execute the authorized manual protocols.** Execute the manual protocols the environment permits: the N33 screen-reader protocol to the extent the offline tooling allows (the scripted scenarios run with the available assistive features of the authorized stack; every step's observed-versus-expected table is recorded, and any scenario step that cannot be meaningfully verified is recorded UNVERIFIED with its reason, never marked pass by inference), and the N35 perf confirmation in the browser (the budget table's three rows re-measured in the Falkon run with the harness and browser values recorded side by side, honestly labeled as one-engine measurements).

**Subtask B.1 - Record only what actually happened.** The execution discipline: every protocol row carries one of three labels (VERIFIED with a recorded observation, UNVERIFIED with the missing capability named, or FAILED as a defect that blocks release), and no row is left ambiguous; the corner case is a scenario that partially verifies (the keyboard half passes while the announcement half cannot be observed without a full screen reader): the row splits into its two parts with separate labels, since a blended half-pass is exactly the overclaim the epistemic rules exist to prevent.

- **B.1.1 -** Execute the N33 protocol scenarios in the authorized environment with the observed-versus-expected tables recorded row by row, and file any FAILED row as a blocking defect with the N33 contract as its reference; the UNVERIFIED rows (full NVDA or VoiceOver observation) are recorded with their named capability gaps and handed to the release gate as explicit open items, not silently closed.

- **B.1.2 -** Re-measure the N35 budget rows in the browser (parse, first render, interaction latency over the same synthetic profiles) and record the side-by-side table (harness value, browser value, ceiling), noting that a browser value within a declared factor of the harness value confirms the model and a wild divergence is a defect to investigate, with the divergence threshold declared before the measurement rather than after.

- **B.1.3 -** Compile the manual execution records (protocol tables, the perf side-by-side, the defect list) into the smoke report artifact with per-row epistemic labels, and record its digest with the honest UNVERIFIED items enumerated explicitly for N40's gate to weigh rather than bury.

**Main Step C - Prove determinism and register the suite.** Prove the smoke's determinism: the full browser smoke runs three times in fresh processes over the same artifact digest, and every assertion sequence is identical (the scripted pass is seeded and time-independent by construction, so flakiness here means a real defect, and the three-run record is the proof); the smoke report, runner and protocol records enter the ledger, and the suite registers with N39's runner as the browser tier.

**Subtask C.1 - Close with the honest cross-engine statement.** The closing statement is deliberately narrow: the artifact is proven alive, correct and offline in Falkon under the AGENTS.md policy, with the interaction path, focus behavior, verdicts and degradation all evidenced; behavior in Chrome, Safari, Firefox and on physical print remains UNVERIFIED in this environment, and that statement is recorded verbatim in the smoke report so the release gate (N40) can weigh an honest limitation rather than discover an unstated one.

- **C.1.1 -** Run the three-run determinism proof and record the identical assertion sequences with their digests; the corner case is the file:// storage degradation appearing in some runs and not others (the engine's own nondeterminism), which the runner's explicit degradation assertion normalizes: the run records the degradation state and asserts the behavior appropriate to it, so the sequence stays comparable.

- **C.1.2 -** Append the smoke report, runner and protocol digests to the ledger, run the extended corpus twice for parity, and record the smoke runner's byte cost and runtime estimate against the tooling budget, so the smoke layer's own footprint stays accounted rather than quietly growing past its declaration.

- **C.1.3 -** Register the browser suite with the N39 runner (id, command, exit codes, the three-run expectation) and record the registration, closing the task with the authorized-engine smoke green, the manual protocols executed to the environment's true limit, and every unverified item named and staged for the gate.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the browser smoke runner, when it executes the scripted pass in Falkon from the local filesystem, then islands, anchors, the interaction chain, focus restore and the vector verdict all pass, the network log is empty, and the calibration fixtures (broken island, dead submit) fail loudly by name.

- **AC2 (negative or edge case):** Given the manual protocol executions, when the observed-versus-expected tables are recorded, then every row carries VERIFIED, UNVERIFIED or FAILED with reasons, partial rows split cleanly, and the perf side-by-side confirms within the pre-declared factor.

- **AC3 (domain integrity and zero-regression):** Given the three-run smoke proof, when assertion sequences are compared, then they are digest-identical with degradation states normalized, the cross-engine statement is recorded verbatim with UNVERIFIED items enumerated, and the suite registers with the runner.

**Verification and Evidence:** Record the smoke pass, the calibration fixtures, the protocol tables with per-row labels, the perf side-by-side, the three-run digests and the registration. The honest cross-engine statement and the enumerated UNVERIFIED items are recorded verbatim in the smoke report.

**Risks, Guardrails, and Rollback Plan:** Risk: pressure to convert UNVERIFIED rows into passes as the release approaches. Guard: the epistemic rules from Section 5 are absolute, and N40's gate explicitly weighs open items rather than assuming them closed. Rollback: the smoke runner is additive tooling; its removal does not touch the artifact, but the release gate loses its browser evidence and must re-run the tier before any release claim.

**Definition of Done:** A calibrated, deterministic, policy-authorized browser smoke exists with the interaction path proven live, offline asserted by empty network logs, manual protocols executed to the environment's true limit with honest per-row labels, and every unverified item named, recorded and staged for the release gate.

### N39 - Build the reproducible QA runner and the SHA-256 evidence chain

**Phase:** Phase VIII | **Priority:** P1 | **Risk:** Medium | **Effort:** M | **Dependencies:** N36, N37, N38

**Domain:** QA orchestration

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the suites now exist as registered artifacts (the property and mutation corpus from N36, the visual matrix from N37, the browser smoke from N38) plus the build gates from N31-N35 (contrast, targets, contract checks, audits) and the smoke subset; each records digests into the ledger. No single orchestrator, no run manifest chain, and no one-command reproducibility exist.

**Purpose and Rationale:** The QA runner is the one command that proves everything at once: it rebuilds the artifact from sources (N31), asserts the artifact digest matches the ledger's recorded digest (proving the sources under test are the shipped file), then executes every registered suite in declared order (build gates, static contract, audits, property and mutation corpus, visual matrix, browser smoke), collects every suite's structured results into one run manifest, emits one exit code, and writes the manifest with SHA-256 digests of the artifact, every source module, every suite and the manifest itself, so any past or future run is checkable against its recorded chain; the runner's own determinism (two runs over unchanged sources, identical verdicts) is proven, making QA a replayable fact instead of a ceremony.

**Target Artifacts and Touchpoints:** tools/qa_runner.py (new); the run manifest schema; the QA entry in the repository's tooling documentation.

**Out of Scope:** No CI service or cloud runner (offline rule: everything is local); no auto-fixing (the runner reports, it never edits sources); no partial-run green (a skipped suite is a failed run, recorded as such).

**Main Step A - Implement the runner and the manifest schema.** Implement the QA runner: the suite registry (each suite's id, invocation, expected exit codes, timeout, and the tier order: build and static gates first since they are fastest and their failures explain downstream ones; then the audits; then the property corpus; then the visual matrix; then the browser smoke), the execution loop (run each suite, capture stdout, exit code and duration, continue-on-failure to collect the full picture as N36 established), and the manifest schema (run id from the artifact digest and a sequence number, the artifact and source digests, per-suite results, the overall verdict, and the manifest's own digest appended after writing).

**Subtask A.1 - Validate the registry against the real suites.** The registry validation: every registered invocation resolves (the suite files exist with their recorded digests, checked against the ledger so a stale or tampered suite is caught before it certifies anything), and the scratch fixture is a registry entry pointing at a missing suite file, which must fail validation with the suite named, since a silently skipped suite is exactly the hole the runner exists to close.

- **A.1.1 -** Implement the registry with the ledger's recorded digests as the suite integrity source and record the validation pass; the corner case is a suite updated during Phase VIII's own defect fixes (a legitimate change): the registry update is a versioned event with the old and new digests and the reason recorded, mirroring the baseline rule from N37, so the integrity chain has no quiet edits anywhere.

- **A.1.2 -** Implement the execution loop with per-suite timeouts (declared per suite from the recorded runtimes, so a hung capture or a stuck browser cannot wedge the whole run) and record the timeout fixture: a scratch suite that sleeps past its declared timeout is marked timeout-failed with the suite named and the run continues, since one hang must not cost the visibility of every other suite's result.

- **A.1.3 -** Implement the manifest schema with the digest chain (artifact, sources, suites, manifest self-digest) and record the first full run's manifest; the corner case is the manifest's own self-reference (the digest of a file that contains its own digest), resolved by the declared two-pass write (manifest written, digest computed, digest appended in the trailer), and the format is documented so external verification can recompute it.

**Main Step B - Prove reproducibility and chain integrity.** Prove the runner's reproducibility: two full runs over unchanged sources in fresh processes produce identical verdict sequences (the manifest digests differ only in run metadata, so the comparison is over the normalized verdict vector, recorded explicitly), and the chain integrity proof: any tampering fixture (a scratch source edit made between the ledger record and the run) must be caught by the digest assertion at run start, with the tampered file named, since a runner that tests the wrong sources certifies the wrong artifact.

**Subtask B.1 - Prove the chain answers a real audit question.** The audit-question proof: for one recorded run, an independent recomputation (a scratch verifier that re-hashes the sources and artifact from the manifest's paths and re-derives the verdict vector from the suite outputs) reproduces the manifest's claims end to end, demonstrating that a future maintainer can verify a past release's evidence without trusting the runner's own summary, which is the entire point of the evidence chain.

- **B.1.1 -** Implement the normalized verdict vector (suite ids in registry order with their verdicts, the deterministic comparison key) and record the two-run equality; the corner case is suites with legitimately variable metadata (the visual matrix's image digests are stable, but durations vary): the normalization excludes duration by design, and the exclusion rule is documented so the vector's equality claim is precise about what it proves.

- **B.1.2 -** Implement the tamper detection (source and suite digests checked against the ledger before any suite runs) and record the tampered-source fixture with the named file and the refused run, plus the restored rerun passing, proving detection is not a deadlock.

- **B.1.3 -** Implement the independent verifier (a separate script that recomputes every digest and re-derives verdicts from raw suite outputs without importing the runner's verdict logic, so it is a second opinion in the N36 sense) and record its agreement with the manifest, closing the integrity question with two independent computations.

**Main Step C - Run the full QA pass and freeze the release evidence.** Run the complete QA pass over the final artifact and freeze the release evidence: the full manifest (every suite green, or the defect list if not, iterated to green as in N37 and N38), the normalized verdict vector, the chain of digests, the run's environment record (tool versions alongside the digests, as N36 established), and the runner's own documentation (the one command, the expected runtime, the manifest verification procedure for a maintainer); the evidence pack is the input N40's gate weighs.

**Subtask C.1 - Prove the pack is complete and register the runner.** The completeness check: every task in this roadmap that declared verification evidence has its evidence represented in the pack (a cross-check against the ledger's entries, listing any evidence type present in the ledger but absent from the pack, which must be empty or explained), so the release gate reviews a complete record rather than a curated one; the runner's digest, documentation and the pack enter the ledger, and the runner stands as the repository's permanent QA entry point.

- **C.1.1 -** Run the final full pass and record the manifest with every suite's verdict, duration and output digest; the corner case is a suite whose result depends on run order (a hidden state leak between suites, for example the browser smoke leaving a profile file), which the runner's fresh-context-per-suite rule (each suite runs from a clean working state) prevents, and the order-independence fixture (the two suites most likely to interact, run in both orders with identical results) is recorded.

- **C.1.2 -** Implement the completeness cross-check over the ledger and record the empty-explained result; the corner case is evidence types the ledger records but the pack cannot contain (the UNVERIFIED manual items from N38): these are listed as explicit open items in the pack with their epistemic labels, so the completeness check distinguishes absent evidence from honestly missing evidence, and both kinds surface at the gate.

- **C.1.3 -** Append the runner, verifier and pack digests to the ledger, record the runner documentation (the command, the runtime, the verification procedure) and close the task, handing the frozen evidence pack to N40's release gate as the complete, chain-verified record of everything this roadmap built and proved.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the suite registry, when validation runs, then every suite resolves against its ledger digest (a missing or stale suite fails by name), timeouts mark and continue, and the two-pass manifest write is documented and recomputable.

- **AC2 (negative or edge case):** Given the two full runs over unchanged sources, when normalized verdict vectors are compared, then they are identical, tampered sources are refused by name and pass after restore, and the independent verifier reproduces the manifest end to end.

- **AC3 (domain integrity and zero-regression):** Given the final QA pass, when the evidence pack freezes, then every suite is green with a complete manifest, order-independence holds, the completeness cross-check leaves nothing unexplained, and open items carry honest labels into the gate.

**Verification and Evidence:** Record the registry validation, the timeout and tamper fixtures, the two-run verdict equality, the independent verifier agreement, the final manifest and the completeness cross-check. The runner documentation and the manifest verification procedure are recorded verbatim for maintainers.

**Risks, Guardrails, and Rollback Plan:** Risk: the runner accreting suites without the ledger's discipline, becoming a pile of invocations. Guard: the registry's digest-integrity rule makes every suite addition a versioned ledger event. Rollback: the runner is additive; removal leaves all suites individually runnable from their own tasks, but N40's gate loses its single-command evidence source and must orchestrate suites manually.

**Definition of Done:** A reproducible one-command QA runner with a digest-chained manifest, proven two-run determinism, tamper detection, an independent verifier and a complete frozen evidence pack exists, with honest open items enumerated and the pack handed to the release gate.

### N40 - Execute the release gate, close the conflict ledger and record the sign-off

**Phase:** Phase VIII | **Priority:** P0 | **Risk:** High | **Effort:** M | **Dependencies:** N39

**Domain:** Release governance

**Current State and Evidence:** `VERIFIED (2026-11-16)`: the evidence pack (N39) is frozen with its digest chain; the conflict ledger holds the twelve verified findings and the inherited C01-C10 conflicts with their resolutions recorded across Phases I-VII; the official-versus-training-policy split (Section 1 and the policy artifacts) is declared in every relevant module. No release gate execution, no ledger closure record, and no sign-off document exist.

**Purpose and Rationale:** The release gate is the final honesty check: the ten-point gate from Section 1 is executed against the evidence pack (each point's evidence cited by manifest digest, each point marked passed, failed or blocked with its reason), the conflict ledger is closed (every V-finding and inherited conflict carries its final status: resolved with the resolving task, documented-and-accepted with the acceptance reason, or open with its owner and its risk stated), the open items from N38 (the honestly UNVERIFIED rows) are weighed and recorded as accepted limitations with their epistemic labels intact, and the sign-off document states plainly what the artifact is proven to do, what it is not proven to do, and under which environment facts, so the release claim itself is as evidence-grounded as every intermediate claim in this roadmap has been.

**Target Artifacts and Touchpoints:** The release gate record; the closed conflict ledger; the sign-off document; the final ledger digest. Touchpoint: the repository's release documentation entry.

**Out of Scope:** No bypassing a failed gate point (a failed point blocks release; it is fixed and re-gated, never argued past); no retroactive epistemic upgrades (an UNVERIFIED item stays UNVERIFIED in the sign-off regardless of release pressure); no official certification claims of any kind.

**Main Step A - Execute the ten-point gate.** Execute the ten-point gate from Section 1 against the frozen evidence pack: each point (the artifact contract and reproducibility, the scientific baseline and conventions, the bank and forms integrity, the grading and fairness evidence, the accessibility contract, the offline and fallback guarantees, the security audit, the test suites' determinism, the visual and smoke evidence, and the documentation completeness) is evaluated by citing its evidence in the pack (manifest digest, suite verdict, report section), and the point is marked passed (evidence complete and green), failed (a blocking defect, named, with its fix path) or blocked (evidence honestly missing, the item cited from the open-items list), with no fourth state available.

**Subtask A.1 - Prove the gate cannot pass on missing evidence.** The gate's calibration: a scratch pack with one suite's result removed (the evidence sabotage case) must make the corresponding gate point blocked, proving the gate reads evidence rather than defaults to pass; and a scratch pack with one failed suite verdict must fail the corresponding point, proving a red suite cannot slide through; both calibration runs are recorded with the exact gate outputs.

- **A.1.1 -** Implement the gate evaluation script (it reads the pack and the gate definition from Section 1, emits the per-point record with citations) and record the execution over the real pack; the corner case is a gate point whose evidence spans multiple suites (the accessibility point cites N32's checker, N33's tables and N38's protocol rows), and the point's record lists every citation so a reviewer can trace the whole chain, not just the headline verdict.

- **A.1.2 -** Implement the evidence-sabotage and red-suite calibrations with their outputs recorded, then restore and record the clean evaluation; the corner case is a blocked point with a legitimate acceptance path (N38's UNVERIFIED screen-reader rows): the gate offers blocked-with-acceptance only when the sign-off decision explicitly records the limitation, the reason and the follow-up owner, never a silent pass.

- **A.1.3 -** Compile the per-point gate record into the release gate artifact with its digest, and record any failed points as blocking defects with their fix-and-regate path (the loop back through N36-N39), honestly counting iterations if they occur.

**Main Step B - Close the conflict ledger.** Close the conflict ledger: every V-finding (V-01 through V-12) and every inherited conflict (C01-C10 from the predecessor plan) receives its final status, resolved (citing the resolving task and its evidence), documented-and-accepted (citing the acceptance reason and its owner) or open (citing the owner and the stated risk), with the official-versus-training-policy split restated per item where it applies (the percentage-basis, density-defect and potential-confusion classes from the inspection are the canonical cases), and the closed ledger's digest is recorded.

**Subtask B.1 - Prove closure is complete and honest.** The closure completeness check: the ledger's final state is cross-checked against the roadmap's own task records (every task that claimed to resolve a conflict has its resolution entry, and no conflict resolves to a task that does not mention it), so the ledger cannot claim more than the tasks prove; the corner case is a conflict that Phase VIII's own work re-opens (a defect found in the final suites touching an earlier resolution): the re-opened entry records the full loop (resolution, regression, re-resolution) rather than overwriting the history, since the ledger is an audit trail, not a whiteboard.

- **B.1.1 -** Compile the per-conflict closure records from the tasks' own verify sections (each resolution's citation is the task id plus its recorded evidence digest, not a restatement from memory) and record the closed ledger with its digest; a scratch conflict lacking any status must fail the completeness check by id.

- **B.1.2 -** Implement the task-record cross-check (every resolved conflict's cited task actually declares that resolution in its recorded output) and record the check pass; the corner case is C10's catalase question (unresolved in the predecessor plan): if it remains scientifically undetermined, it closes as documented-and-open with the owner and the exact open question restated verbatim, since an inherited scientific uncertainty is not a defect to hide but a fact to carry forward.

- **B.1.3 -** Record the official-versus-training-policy split summary (which facts are programme-official and which are the roadmap's proposals, restating the Section 1 split with any late additions), so the closure record is self-contained for a reader who starts at the sign-off and works backward.

**Main Step C - Author the sign-off and freeze the final evidence.** Author the sign-off document: the release statement (the artifact's name, digest, size, composition and the one command that rebuilds it), the proven-capabilities list (each with its gate point and evidence citation), the accepted limitations list (each UNVERIFIED or blocked item with its label, reason and follow-up owner, verbatim from the honest records), the environment facts (the toolchain, the authorized-engine scoping, the offline constraints, restated from the smoke and matrix reports), and the inheritance note (what this roadmap received from the predecessor plan and what it hands forward); the document's digest, the gate's digest and the closed ledger's digest form the final evidence triangle.

**Subtask C.1 - Freeze the triangle and state the roadmap's end honestly.** The final freeze: the sign-off, gate record and closed ledger are appended to the evidence pack as its terminal records, the pack's manifest is regenerated with the three digests, and the closing statement records the roadmap's own epistemic summary: a plan is not a product, and the artifact's claims are exactly as strong as the recorded evidence, no stronger, which has been the discipline from N01's source freeze to this final record; the roadmap ends by handing the repository a simulator, an evidence chain and an honest statement of both.

- **C.1.1 -** Author the sign-off with the proven-capabilities and accepted-limitations lists built strictly from the gate and pack records (no capability appears without a citation, no limitation without a label), and record the document with its digest; the corner case is the release-under-limitations decision: the sign-off states the criterion explicitly (release permitted with limitations recorded, or blocked pending the named follow-ups), so the decision is a recorded rule, not a mood.

- **C.1.2 -** Regenerate the pack manifest with the terminal digests and run the N39 independent verifier one final time over the complete pack, recording its end-to-end agreement, so the frozen triangle is verified by the same second-opinion machinery that validated the pack.

- **C.1.3 -** Record the final ledger state (every roadmap task's evidence digests, the gate, the sign-off and the pack in one final digest), and close the task with the repository holding the simulator, the QA command, the evidence chain and the sign-off as its permanent, verifiable record of what was built, what was proved and what remains honestly open.

**Acceptance Criteria:**

- **AC1 (happy path):** Given the gate definition and the frozen pack, when the gate executes, then every point carries passed, failed or blocked with evidence citations (multi-suite points list every citation), and the sabotage and red-suite calibrations prove the gate cannot pass on missing evidence.

- **AC2 (negative or edge case):** Given the closure cross-check, when the ledger closes, then every V and C entry carries its final status with task-cited resolutions (a statusless scratch conflict fails by id), re-opened entries keep their full history, and C10's undetermined science closes as documented-and-open verbatim.

- **AC3 (domain integrity and zero-regression):** Given the sign-off, when the final triangle freezes, then capabilities and limitations are strictly citation-built, the limitation criterion is a recorded rule, the independent verifier agrees end to end, and the final ledger digest records the complete state.

**Verification and Evidence:** Record the gate execution with per-point citations, both calibrations, the closed ledger with its cross-check, the sign-off with its digest, the regenerated manifest and the final verifier agreement. The accepted limitations, the environment facts and the official-versus-training split are recorded verbatim.

**Risks, Guardrails, and Rollback Plan:** Risk: release pressure eroding the gate (a failed point argued into a pass). Guard: the gate's three-state rule is absolute, the calibration fixtures prove it reads evidence, and the sign-off's limitation criterion is a recorded rule. Rollback: the gate, ledger closure and sign-off are records, not runtime code; a retracted release is a new sign-off version with the retraction reason recorded, and the artifact itself is untouched.

**Definition of Done:** A ten-point release gate executed against chain-verified evidence with calibration proofs, a completely closed and cross-checked conflict ledger, and a citation-built sign-off document recording proven capabilities, accepted limitations and environment facts, with the final evidence triangle frozen and the repository holding its permanent verifiable record.


## 15. Acceptance Matrix (120 criteria)

The matrix lists the three acceptance criteria of every task in short form. Each row is the traceability contract for one task: the full criterion text, its verification record and its evidence digests live in the task body above, and the row here is the index a reviewer scans first. A row is satisfied only by the recorded evidence in the task, never by an assertion in this matrix.

| Task | Happy-path criterion | Negative or edge criterion | Domain-integrity criterion |
|---|---|---|---|
| N01 | Mode-flagged verify_preparation.py runs to PASS on the repository alone | V-01 KeyError crash reproduced with exact traceback recorded | Frozen source digests recorded for every consumed dependency |
| N02 | All 64 coverage outcomes render with resolvable master_anchor targets | Zero anchor resolution failures across all seven masters | Per-topic counts match the inspection record exactly |
| N03 | Conventions artifact validates with every conflict registered | All twelve V-findings carry evidence citations and statuses | Engines consume conventions without local drift copies |
| N04 | QUESTION_SCHEMA validator passes all eighteen response types | Malformed scratch instances fail with the field named | One loader serves runtime and authoring identically |
| N05 | Golden vectors grade verdict-for-verdict against oracle records | Seeded PRNG streams are cross-language deterministic | Vector corpus is oracle-independent and replayable |
| N06 | Start screen renders objectives with honest policy labels | Theme toggle and tokens hold in both themes | No official exam claim appears in any copy |
| N07 | Concept map renders with every ASCII anchor resolvable | Drawer close restores focus to the invoking control | Map structure matches the 64-outcome coverage graph |
| N08 | Recall layers render progressive hints per practice item | Full reveals never render inside exam mode | Every layer cites its source anchor |
| N09 | Every distractor carries a misconception signature id | Latvian feedback strings pass the term lint | Signature taxonomy matches engine classification |
| N10 | sim-terms island passes the unit-string lint | Latvian and IUPAC names render consistently | Every runtime term key resolves in lookup |
| N11 | SVG framework renders T1-2 records fully inline | Tolerance coupling matches the conventions artifact | Figures contain zero external URLs |
| N12 | Burette and dilution figures follow meniscus conventions | Leak scan finds zero key values in figure output | Figures stay legible at the 320 px class |
| N13 | Energy, Hess and Maxwell-Boltzmann figures render correctly | Figure data derives from the conventions artifact | Axis labels are term-keyed and unit-linted |
| N14 | Kinetics figures match the N18 tolerance fields | Linearization math is independently recomputable | No extrapolation beyond data appears |
| N15 | Titration and calibration figures obey no extrapolation | Curve shapes match the declared criterion shapes | Calibration assumptions are labeled explicitly |
| N16 | EX01-EX14 chains render collapsed and leak-free | Reveal exposes values only on interaction | Every chain cites its master anchor |
| N17 | Quantity and conservation engines match oracles verdict-for-verdict | Error taxonomy classifies all four parse classes | The V-04 density defect is gated by rule |
| N18 | Graph scoring accepts within-tolerance points | Validity rules reject unphysical graphs | Keyboard parity with pointer input proven |
| N19 | Ordering and matching verdicts are deterministic | Self-assessed explanations stay pending | No keyword matching in any verdict |
| N20 | 112-instance bank validates across 28 families | Frozen bank island digest recorded in ledger | Review workflow gates every instance |
| N21 | Session machine passes all lifecycle fixtures | Late writes rejected with stable error ids | Exam mode contains zero help markers |
| N22 | All eighteen response types operable per contract | ARIA name-role-value proven per component | Keyboard parity holds for spatial types |
| N23 | Partial credit matches rubric weights exactly | Error classes ordered confirmed, self, pending | Grading digests identical across replays |
| N24 | Seeded A, B, C assemblies reproduce from seed keys | Slot and family uniqueness hold per form | Shortage fails loudly, never pads |
| N25 | Store round-trips with migrations passing | Privacy audit records zero undeclared keys | F10 rejection recorded with boundary copy |
| N26 | Mastery policy validates with no unreachable states | Reducer replay digests identical fresh | Views never claim official certification |
| N27 | Leitner intervals strictly increase per box | Queues digest-deterministic under injected clock | Fresh learner queue non-empty and sensible |
| N28 | Remediation coalesces by family and outcome | Retries never re-serve the failed instance | Dangling links fail loudly by name |
| N29 | Self-ratings display distinct from graded states | Criterion names single-sourced and key-free | Mastery map unchanged by rating activity |
| N30 | Path lengths sane against eligible counts | Shortages render true lengths with reasons | Journey trace replays identically fresh |
| N31 | Three fresh-process builds byte-identical | Atomic write survives injected failure | Static contract check passes all assertions |
| N32 | Contrast thresholds hold in both themes | Zero raw hex outside the token layer | ARIA parity holds after the rework |
| N33 | Keyboard map collision-free with typing guard | Focus escapes every drawer trap | Manual protocol staged honestly UNVERIFIED |
| N34 | Noscript content single-sourced and link-complete | Worksheet regeneration is digest-identical | Three-mode isolation fixtures pass |
| N35 | Perf and storage budgets hold with detection proofs | Serialization sites exhaustively inventoried | Injection corpus renders as text everywhere |
| N36 | Property suite catches the planted tolerance cliff | Every mutant killed or recorded equivalent | Three-run manifests digest-identical |
| N37 | Matrix cells resolve with readiness waits | Planted overlap caught, jitter passes | Coverage scoped to Falkon verbatim |
| N38 | Scripted pass green in Falkon from filesystem | Network log empty through entire run | Unverified items enumerated, never inferred |
| N39 | Registry validated against ledger digests | Two-run verdict vectors identical | Independent verifier reproduces the manifest |
| N40 | Gate three-state rule holds under calibrations | Ledger closed with task-cited resolutions | Sign-off citation-built, limitations labeled |

## 16. Scientific Content Checklist

The checklist restates the scientific honesty obligations that span all forty tasks, so a reviewer can audit them in one place rather than across eight phases. Every item cites the task that owns its evidence.

1. Official facts are limited to the programme's own record: seven topics, a paper colloquium format, and the 180-minute maximum. Everything else (points, forms, slots, per-topic minutes, family counts) is training policy, labeled as proposals throughout (N02, N24; Section 1's split).
2. Every numerical convention (atomic masses, unit conversions, tolerance classes, rounding rules) is single-sourced in the conventions artifact and consumed by engines, figures and vectors alike, with drift impossible by construction (N03, N11-N15, N17).
3. Every worked chain, hint layer, feedback string and misconception explanation cites its source anchor, so no scientific claim floats free of the masters (N07, N08, N09, N16).
4. The four inherited calculation dangers (percentage-basis confusion, the milligram, gram and liter density defect, the standard versus formal potential mixing, and the endpoint persistence question) carry explicit gates in the conventions, engines and figure captions (N03, N17, N15; conflict registry).
5. Graph work obeys the declared validity rules: physical constraints, no extrapolation beyond data, and tolerance fields coupled between figures and scoring (N14, N15, N18).
6. Grading never grades what the learner did not write: self-assessed explanations stay pending, skips are recorded as skipped and never as incorrect, and one correct retry is evidence rather than mastery (N19, N23, N28, N26).
7. Figures and texts avoid the flatness and assumption traps named in the inspection: the 440 nm absorption context is carried explicitly where relevant, and calibration assumptions are labeled rather than implied (N13, N15).
8. No claim of official certification, official exam equivalence or official grading appears anywhere in the artifact's copy, views or reports (N06, N26, N29; Section 1).
9. The catalase question inherited unresolved from the predecessor plan (C10) remains documented-and-open with its owner and question text verbatim, rather than being silently decided (N40's ledger closure).
10. Every scientific epistemic label in the artifact (VERIFIED, DOCUMENTED BUT NOT RERUN, PROPOSED, UNDETERMINED) follows the same rules as this roadmap's labels (Section 5), so learners see the same honesty the roadmap practices.

## 17. Browser, Device and Print QA Matrix

The QA matrix consolidates the environment-scoped verification claims of Phases VII and VIII into one honest table. The epistemic rules of Section 5 apply to every cell: a cell is claimed only where the evidence exists.

| Dimension | Coverage | Evidence owner | Epistemic status |
|---|---|---|---|
| Rendering engine | Falkon via lite-shot, per AGENTS.md authorization | N37, N38 | VERIFIED (2026-11-16 environment) |
| Chrome, Chromium | Not run; forbidden without explicit authorization | N37, N38 | UNAVAILABLE |
| Other engines (Safari, Firefox, Edge) | Not run; not present in the offline environment | N38 | UNAVAILABLE |
| Viewport classes | 320, 390, 768, 1280 px, both themes | N32, N37 | VERIFIED (Falkon-scoped) |
| Keyboard-only operation | Full map validated; scripted pass in browser | N33, N38 | VERIFIED |
| Screen-reader observation | Protocol executed to the environment's tooling limit | N33, N38 | Partially VERIFIED, remainder UNVERIFIED (named rows) |
| Offline loading | Local filesystem load, zero network attempts recorded | N31, N38 | VERIFIED |
| No-JavaScript fallback | Static content, link integrity, honest notice | N34 | VERIFIED |
| Print and paper mode | Print stylesheet validation, F04 worksheet determinism | N34, N37 | VERIFIED (engine-rendered; physical print UNVERIFIED) |
| Physical devices (phones, printers) | Not present in the environment | N37 | UNAVAILABLE |

The matrix's honest gaps are release-blocking only if the sign-off's limitation criterion (N40) says so; the default posture is release with recorded limitations and named follow-up owners.

## 18. Ten-Point Release Gate

The gate is executed by N40 against the frozen evidence pack from N39. Each point passes only on cited, digest-chained evidence; a failed point blocks release until fixed and re-gated; a blocked point (honestly missing evidence) can pass only through the sign-off's explicit limitation rule. There is no fourth state.

| Point | Gate area | Evidence required |
|---|---|---|
| G1 | Artifact contract and reproducibility | N31's three-run byte-identical builds, the manifest, and the static contract check (lang, anchors, islands, single script, zero external URLs, size and sub-budgets) all recorded in the evidence pack. |
| G2 | Scientific baseline and conventions | N01's mode-flagged verification PASS, N02's 64 resolved outcomes, and N03's validated conventions with the closed conflict registry, cited by digest. |
| G3 | Bank and forms integrity | N20's 112-instance bank validation with its frozen island digest, and N24's three-form assembly check with family uniqueness and eligibility, all green. |
| G4 | Grading and fairness evidence | N17's verdict-for-verdict oracle match, N18 and N19's deterministic engines, N23's rubric-exact partial credit, and N36's golden-vector re-proof, all digest-chained. |
| G5 | Accessibility contract | N32's build-gated contrast and target checks, N33's machine-proven name-role-value tables, and N38's protocol rows with their honest per-row labels, weighed together. |
| G6 | Offline and fallback guarantees | N31's zero-URL scan, N34's honest noscript content, and N38's empty network log across the full scripted browser run. |
| G7 | Security audit | N35's serialization inventory, corrupted-island degradation fixtures, and the injection corpus across every runtime text channel, with the refactoring chain recorded. |
| G8 | Test suite determinism | N36's three-run identical manifests, the mutation kill table, and N39's two-run normalized verdict vectors, proving the suites are replayable facts. |
| G9 | Visual and smoke evidence | N37's Falkon matrix report with its calibration certificates and honest scope header, and N38's smoke run, both registered suites green in the pack. |
| G10 | Documentation and evidence completeness | N39's completeness cross-check (every ledger evidence type present or explicitly open) and N40's citation-built sign-off with accepted limitations enumerated. |

The gate's calibration fixtures (evidence sabotage and planted red suite, N40) prove it cannot pass on missing or failed evidence, which is what distinguishes a gate from a checklist.

## 19. Risk Register and Rollback Procedure

The register consolidates the highest-level risks that cross task boundaries, with the rollback discipline stated once for the whole plan. Every task additionally carries its own risk, guardrail and rollback note in its body.

1. The single largest technical risk is bank size creep: 112 instances with rich Latvian feedback can exceed the bank sub-budget silently. Guard: N31's build fails on any sub-budget breach with the segment named; N20's frozen island digest makes any growth a visible version event. Rollback: trim feedback strings at source and rebuild; the digest change is a ledger event.
2. The single largest process risk is evidence drift: suites, baselines and manifests aging away from the artifact they certify. Guard: every suite is digest-registered against the ledger (N39), every manifest asserts the artifact digest, and the independent verifier recomputes the chain. Rollback: re-run the QA command; any digest mismatch is named before any suite executes.
3. The single largest scientific risk is an undetected convention drift between figures, vectors and engines. Guard: single-sourced conventions consumed everywhere (N03), the independent recompute properties (N36), and the golden vectors' verdict-for-verdict re-proof. Rollback: the conventions artifact's version event restores the previous digest and the suites re-gate.
4. The largest honesty risk is late-stage epistemic erosion: pressure to mark UNVERIFIED items as passed. Guard: the epistemic rules of Section 5 are absolute; N38's per-row labels and N40's limitation rule make every unverified item visible at the gate. Rollback: a retracted claim is a new sign-off version with the retraction recorded.
5. The generic rollback procedure, stated once: all work is additive over the frozen sources of N01; any task can be reverted by removing its modules and rebuilding, with the dependency tasks named in each body; the evidence ledger records every state, so a rollback is a traversal to a recorded digest, never a guess.

## 20. Truthful Self-Audit

This roadmap is a plan, not a product, and its final section states exactly what is true about itself.

1. Everything this document claims about the repository was inspected on 2026-11-16 in the recorded environment: the programme PDF's size and digest, the master file sizes and conventions, the COPY_MANIFEST counts, the 64 resolved outcome anchors, the predecessor plan's not-started cards and C01-C10 conflicts, and the AGENTS.md rules. These carry the VERIFIED (2026-11-16) label.
2. The committed PREPARATION_VERIFICATION.json (PASS, 2026-11-16T21:12:03Z, 174 files, 15,978 preserved files) is DOCUMENTED BUT NOT RERUN in the published repository: the clean clone cannot execute tools/verify_preparation.py (the KeyError finding, V-01), which is why N01's first deliverable is the mode-flagged, repository-local verification path. This roadmap does not inherit that PASS as if it were reproduced.
3. The training-policy numbers (100 points, three forms, 21 slots, per-topic distributions, 28 families, 112 instances) are proposals of this roadmap's design, derived from the predecessor plan's approved structure and the blueprint's constraints. They are labeled PROPOSED wherever they appear, and no official source supports them.
4. The browser-scoped claims (visual matrix, smoke, print rendering) are true for Falkon under the AGENTS.md lite-shot policy and for nothing else; Chrome is forbidden without authorization, and other engines are absent from the environment. Cells in Section 17's matrix say so plainly.
5. The full screen-reader verification, physical-device rendering and physical print output remain UNVERIFIED, and are recorded as accepted limitations with named follow-up owners rather than converted into claims. A future executor with the missing environments closes these rows by running the staged protocols of N33 and N38, not by editing the labels.
6. Every task's evidence chain ends in a digest recorded in the ledger, and the independent verifier of N39 recomputes the chain, so the document's final claim is narrow and checkable: the plan is internally consistent, its facts are sourced, its gaps are named, and its execution is one command away from beginning.
