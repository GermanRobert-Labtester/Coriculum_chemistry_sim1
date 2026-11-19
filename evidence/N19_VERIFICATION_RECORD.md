# N19 — Method cards and the ordering, matching and sequence verdict engines

**Status:** closed 2026-11-18 (UTC). **Phase:** IV · **Priority:** P1 · **Risk:** Medium · **Effort:** M
**Dependencies:** N05, N16 (N09 declared as **absent** in this workspace — see §2.4)

**Epistemic note.** The executions below are **VERIFIED (2026-11-18, this environment)**: the Python
twin, the JavaScript twin, the build gate, the runtime harness and the corpus all ran here and their
results are recorded. This is **not** a browser render, screen-reader, print or instructor-acceptance
claim. The 2025 programme fixes no point weight, no question count, no pass mark, no allowed aid and
no exact exam question type; every step order, criterion shape, free-order group and acceptance set
declared here is **PROPOSED training policy**, except the rules inherited verbatim from the frozen
N05 corpus and the masters' own cited teaching. The engine claims no official examination, grade or
proctoring status.

---

## 1. What was built

| Artifact | Role |
|---|---|
| `data/method_card_schema.json` | The declared method-card format: required and optional fields, the signature pattern, the honesty rules and the engine binding. |
| `data/method_cards.json` | 14 authored cards `MC-EX01`…`MC-EX14`: 74 steps, 28 sequence prompts, 3 matching exercises, 3 safety entries, 1 free-order group. |
| `data/method_engine_contract.json` | The frozen `#sim-method-engine` island: the verdict envelope, the 14-entry signature registry, the pending semantics, the declared budgets and the `S4-N19` stratum (17 vectors). |
| `tools/method_engine.py` | The Python authoring twin: ordering, matching, sequence and self-assessment grading, plus the spec builders. |
| `src/method-engine.js` | The runtime twin `SimMethodEngine`: the same contract, the same canonical projection, the same digests. |
| `src/method-card-view.js` | `SimMethodCards`: the collapse-and-reveal card renderer, the XOR unseal, the focus handling and the remediation entry point. |
| `tools/validate_method_cards.py` | Build gate 15: card structure, citation integrity, completeness, the copy lint, the signature sweep, the N05 and `S4-N19` vector passes, the no-keyword proof and the budget measurement. |
| `tools/check_n19_runtime.js` | The runtime harness: the shipped islands plus the two source modules, the verdict tables, the feedback trace, the pending boundary, the focus traces and the smoke vector. |
| `tools/n19_corpus.py` | The evidence corpus: the cross-language comparison, the determinism digests, the budget accounting and the two-run parity. |
| `docs/METHOD_CARD_FORMAT.md` | The frozen interface for N20, N22, N23 and N28. |

The cards island ships a **sealed projection**: the statements are public, the diagnostics (the
reasoning, the misconception notes, the signatures, the grading rules) are XOR-sealed and revealed
only on interaction — the same collapse-and-reveal and leak discipline the chains use.

## 2. The cards

### 2.1 The inventory — 14 cards, 74 steps

| Card | Procedure | Family | Chain | Steps | Prompts | Safety | Free-order |
|---|---|---|---|---|---|---|---|
| `MC-EX01` | Stehiometrija no masas | FAM-1C | EX01 | 5 | 2 | — | — |
| `MC-EX02` | Disociācija un joni | FAM-1B | EX02 | 5 | 2 | — | — |
| `MC-EX03` | Biretes izlietotais tilpums | FAM-2C | EX03 | 6 | 2 | S1 | — |
| `MC-EX04` | Vienību ķēde un zīmīgie cipari | FAM-2B | EX04 | 4 | 2 | — | — |
| `MC-EX05` | Koncentrācija no iesvara | FAM-3A | EX05 | 5 | 2 | — | — |
| `MC-EX06` | Atšķaidīšana līdz gala tilpumam | FAM-3C | EX06 | 7 | 2 | — | **FOG-EX06-1** |
| `MC-EX07` | Gibbsa enerģija un robežtemperatura | FAM-4C | EX07 | 5 | 2 | — | — |
| `MC-EX08` | Kalorimetrija un Hesa cikls | FAM-4B | EX08 | 7 | 2 | S2 | — |
| `MC-EX09` | Pusperioda modelis un linearizācija | FAM-5C | EX09 | 5 | 2 | — | — |
| `MC-EX10` | Aktivācijas barjera un katalizators | FAM-5A | EX10 | 6 | 2 | — | — |
| `MC-EX11` | Redoksa titrēšana (permanganatometrija) | FAM-6C | EX11 | 5 | 2 | S2 | — |
| `MC-EX12` | Nernsta vienādojums | FAM-6D | EX12 | 5 | 2 | — | — |
| `MC-EX13` | Kalibrēšana ar nenulles krustpunktu | FAM-7B | EX13 | 4 | 2 | — | — |
| `MC-EX14` | Atšķaidīts paraugs (masa un daudzums) | FAM-7C | EX14 | 5 | 2 | — | — |

Every card's step order is fixed by its master's teaching and cited per card through
`master_citation` (path, anchor, heading, `freeze_id`, `sha256`) and `order_citation_lv`. The
citation validation is build-gated: **36 citations resolve, 36 are checked, 0 unresolved.**

### 2.2 The completeness table — 35/35 method outcomes covered

The coverage island declares 64 outcomes; 35 of them bind a practice family that has a method card.
Every one of the 35 resolves to a card, and no outcome declares a method family without a card.

| Topic | Method outcomes | Cards |
|---|---|---|
| 1 | 5 | MC-EX01, MC-EX02 |
| 2 | 6 | MC-EX03, MC-EX04 |
| 3 | 7 | MC-EX05, MC-EX06 |
| 4 | 6 | MC-EX07, MC-EX08 |
| 5 | 6 | MC-EX09, MC-EX10 |
| 6 | 3 | MC-EX11, MC-EX12 |
| 7 | 2 | MC-EX13, MC-EX14 |

Each card's steps are non-empty, the step ids are unique within the card and the order is total,
with exactly one declared exception (§2.3).

### 2.3 The free-order group — `FOG-EX06-1`

The dilution card `MC-EX06` declares one free-order group over its steps **S1** and **S2** (the
empty volumetric-flask weighing and the substance weighing). The master's *Darba gaita* section
teaches both as preparation steps and never orders one before the other; each must precede the
transfer. The group is therefore declared orderable among themselves and graded either way, so the
grading never penalises the masters' own freedom. The group is cited to the same anchor as the
card's order (`ch12-darba-gaita`, C2-MASTER).

The scratch negative `NV-N19-SCRATCH-ORD` proves the exception is narrow: a member of a free-order
group moved **outside** the group's position in the sequence is graded wrong (`WRONG_ORDER`, wrong
positions 0 and 2), not silently accepted.

### 2.4 The N09 dependency gap — recorded, not filled

**N09 does not exist in this workspace.** The misconception registry that N19 was to consume is
absent, so the cards use the N04 stub pattern `^MC-[1-7][A-D]-[0-9]{2}$` and every signature is
required to resolve against an **existing vector in the frozen N05 corpus** (30 signatures are
present there). This binding is written into the card island's `n09_gap_notice_lv` so that whoever
implements N09 inherits the constraint instead of re-deriving it:

> *N09 misconceptions reģistrs šajā darba telpā vēl nav izpildīts. Kartīšu soļi lieto N04
> deklarēto stub-parakstu MC-[1-7][A-D]-[0-9]{2} un pievieno savu skaidrojuma tekstu; katrs
> paraksturs atbilst kādam esošam #sim-golden-vectors vektoram. N09 izpildot, jāpārbauda šī
> saiste, nevis kartīšu loģika.*

**Two of the fourteen signatures are cross-family and are marked as such** in the registry, with the
reason stated in the entry rather than left for the reader to infer:

| Card | Signature | Provenance | Why |
|---|---|---|---|
| `MC-EX10` | `MC-5D-01` | `nearest-available-cross-family` | FAM-5A has no S1-stratum vector; FAM-5D covers P5-03 and P5-06. |
| `MC-EX12` | `MC-6A-01` | `nearest-available-cross-family` | FAM-6D has no S1-stratum vector; FAM-6A covers the redox roles and the potential direction. |

The remaining twelve are `exact-family`.

### 2.5 The safety entries — 3, every one cited

A safety entry may only restate what the master teaches. The gate compares each entry against its
master anchor mechanically: the fraction of the entry's content words that appear in the cited
master section must be at least 0,9.

| Card | Step | Master anchor | Overlap |
|---|---|---|---|
| `MC-EX03` | S1 | C2 `ch4-drosiba-ar-iemeslu` | **1,00** (10/10 words) |
| `MC-EX08` | S2 | C5 `ea-slieksnis` | **1,00** (13/13 words) |
| `MC-EX11` | S2 | C6 `h-ch3` | **1,00** (13/13 words) |

No precaution was invented: an entry that added a word the master does not use would fall below the
threshold and fail the gate.

### 2.6 The numeric companion — the quantities come from the chains

A card never invents a quantity. Each numeric step links to the recomputed chain step, and the gate
enforces that the link's `value_display_lv` and `unit` **equal** the chain step's recomputed result.
The `dimension` field is optional because the `mL`/`mg` pair has no matching dimension in the N10
ledger — the link is still checked on value and unit.

## 3. The three engines

### 3.1 The grading rules

**Ordering.** The submission is a permutation of the step ids. Each position is compared to the
declared order; the members of a free-order group are compared as sets. The verdict is per-step:
each step is `correct` or `misplaced`, and the misplaced step returns the misconception signature
that its note names. The criterion stays **all-or-nothing** for the awarded points — the per-step
diagnostics carry the diagnosis, not the score.

**Matching.** The submission is a list of pairs across two lists, graded per pair by exact id
identity. The declared verdict classes are `correct`, `wrong_pair`, `repeated_left`,
`repeated_right` and `unmatched`. A duplicated left item denies **all** pairs that touch it, so the
verdict cannot be gamed by repeating a correct answer.

**Sequence.** The submission is one next-step id, graded against the declared acceptance set by
exact id identity. A distractor drawn from the card's own plausible-but-wrong steps returns its
signature; an unknown id returns `unknown`.

**Self-assessment.** Not graded. The learner's text is recorded and never parsed.

### 3.2 The no-keyword rule — three independent proofs

**Rule (verbatim, from the contract).** *"Verdicts are computed from structural identity only —
step ids, pair identities and order positions. No verdict path compares learner text, a step
statement or any other prose field, and no verdict path uses string similarity, keyword matching or
case folding. A near-synonym submission is not a correct submission."*

1. **Static.** The gate tokenises both engine sources (Python AST and a JS tokenizer) and fails on
   any identifier containing a similarity/keyword/case-folding routine, on any **domain keyword
   literal** that also occurs in the card text, and on any comparison of a prose field. Result:
   0 findings in both files.
2. **Adversarial.** Five stratum vectors submit near-synonyms or prose in place of ids and must
   fail: `NV-N19-ORD-05` (a sentence instead of a step id), `NV-N19-ORD-06` (a step dropped),
   `NV-N19-MAT-05` (a step statement instead of a right-item id), `NV-N19-SEQ-03` (a statement
   instead of a step id). All are graded wrong with the declared verdict class.
3. **Behavioural.** The gate grades three probes twice — once clean and once with a free-text field
   added to the submission — and asserts that the verdict record is **identical** in all eight
   compared fields, diagnostics included. An added free-text field never changes a verdict.

### 3.3 The N05 vectors — 10/10, verdict for verdict

The frozen S1 corpus is untouched. Its ten method-type vectors (Q06 ×4, Q08 ×3, Q15 ×3) are re-graded
by the N19 engines and compared against the N05 oracle on all eight verdict fields.

| Vector | Type | Case | Expected | Graded | Signatures |
|---|---|---|---|---|---|
| `GV-S1-T1-Q15-01` | Q15 | pending | `pending_self_assessment` | identical | — |
| `GV-S1-T1-Q15-02` | Q15 | blank | `incorrect` / `BLANK_RESPONSE` | identical | — |
| `GV-S1-T2-Q06-01` | Q06 | correct | `correct` | identical | — |
| `GV-S1-T2-Q06-02` | Q06 | partial | `partial_matching` / `WRONG_PAIRING` | identical | `MC-2A-01` |
| `GV-S1-T2-Q06-03` | Q06 | wrong pairing | `incorrect` / `WRONG_PAIRING` | identical | `MC-2A-01` |
| `GV-S1-T2-Q08-01` | Q08 | pending review | `auto_passed_pending_review` | identical | — |
| `GV-S1-T2-Q08-02` | Q08 | wrong order | `incorrect` / `WRONG_ORDER` | identical | `MC-2A-02` |
| `GV-S1-T3-Q08-01` | Q08 | pending review | `auto_passed_pending_review` | identical | — |
| `GV-S1-T4-Q15-01` | Q15 | pending | `pending_self_assessment` | identical | — |
| `GV-S1-T6-Q06-01` | Q06 | correct | `correct` | identical | — |

The engine stays **oracle-compatible**: the N05 verdict classes and awarded criteria are unchanged,
so the N05 corpus is a genuine regression suite and not a document of a different design.

### 3.4 The `S4-N19` stratum — 17/17

Following the N17 and N18 precedent, the N19 vectors live in the N19 contract island under the
`S4-N19` stratum. The frozen N05 corpus is append-only and is **not** modified.

| Vector | Kind | Card | Verdict | Note |
|---|---|---|---|---|
| `NV-N19-ORD-01` | ordering | MC-EX03 | `correct` | the declared order |
| `NV-N19-ORD-02` | ordering | MC-EX03 | `incorrect` / `WRONG_ORDER` | **the transposed pair**: positions 1 and 2 marked |
| `NV-N19-ORD-03` | ordering | MC-EX06 | `correct` | **the free-order group accepted either way** (S1/S2 swapped) |
| `NV-N19-ORD-04` | ordering | MC-EX06 | `incorrect` / `WRONG_ORDER` | a genuine pair transposed outside the group |
| `NV-N19-ORD-05` | ordering | MC-EX03 | `incorrect` / `WRONG_ORDER` | **adversarial**: a sentence in place of a step id |
| `NV-N19-ORD-06` | ordering | MC-EX03 | `incorrect` / `WRONG_ORDER` | **adversarial**: a step dropped |
| `NV-N19-MAT-01` | matching | MC-EX03 | `correct` | all three pairs exact |
| `NV-N19-MAT-02` | matching | MC-EX03 | `partial` / `WRONG_PAIRING` | two pairs swapped |
| `NV-N19-MAT-03` | matching | MC-EX03 | `incorrect` / `WRONG_PAIRING` | **repeated left and right** — the duplicate denies all its pairs |
| `NV-N19-MAT-04` | matching | MC-EX03 | `partial` / `WRONG_PAIRING` | one pair left unmatched |
| `NV-N19-MAT-05` | matching | MC-EX03 | `partial` / `WRONG_PAIRING` | **adversarial**: a statement in place of a right-item id |
| `NV-N19-SEQ-01` | sequence | MC-EX06 | `correct` | the accepted next step |
| `NV-N19-SEQ-02` | sequence | MC-EX06 | `incorrect` / `WRONG_ORDER` | a distractor step, with its signature |
| `NV-N19-SEQ-03` | sequence | MC-EX06 | `incorrect` / `WRONG_ORDER` | **adversarial**: a statement in place of a step id |
| `NV-N19-SELF-01` | self-assessment | MC-EX06 | `pending_self_assessment` | the text is recorded, never parsed |
| `NV-N19-SELF-02` | self-assessment | MC-EX06 | `incorrect` / `BLANK_RESPONSE` | blank is a blankness test only |
| `NV-N19-SCRATCH-ORD` | ordering | — | `incorrect` / `WRONG_ORDER` | **scratch**: a free-order member moved outside the group |

### 3.5 The determinism proof

Every stratum vector is graded twice in both twins and the canonical verdict record is digested.
All 17 digests are stable, and the two runs of the harness produce identical digests
(`parity: true`, `harness_parity: true`).

| Table | Rows | Digest |
|---|---|---|
| N05 verdicts | 10 | `c05edff7…86ad60` |
| Stratum verdicts | 17 | `ec44907f…c66f81` |
| Determinism | 17 | `8a14feee…b8535e` |
| Signature mapping | 14 | `9bc3f566…042ee9` |
| Full verdict records | 17 | `daad39a8…0ad92` |

### 3.6 The signature mapping — 14/14, zero dangling

The sweep covers the **whole registry**, not only the signatures the vectors happen to exercise, and
it runs in both directions. A signature that no card declares is an orphaned registry entry and
dangles just as hard as a card signature with no registry entry.

| Signature | Cards | Provenance | In N05 corpus | Feedback resolves | Status |
|---|---|---|---|---|---|
| `MC-1B-01` | MC-EX02 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-1C-01` | MC-EX01 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-2B-01` | MC-EX04 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-2C-01` | MC-EX03 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-3A-01` | MC-EX05 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-3C-01` | MC-EX06 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-4B-01` | MC-EX08 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-4C-01` | MC-EX07 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-5C-01` | MC-EX09 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-5D-01` | MC-EX10 | **cross-family** | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-6A-01` | MC-EX12 | **cross-family** | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-6C-01` | MC-EX11 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-7B-01` | MC-EX13 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |
| `MC-7C-01` | MC-EX14 | exact-family | yes | `feedback.concept_link_label` | RESOLVED |

**Zero dangling.** Both twins report it independently: the Python gate and the JavaScript harness
each resolve all 14 entries and each assert that no card signature lacks a registry entry and that
no registry entry lacks a card.

### 3.7 The feedback trace — the transposed pair, end to end

A transposed pair is the classic near-miss: two adjacent steps swapped. The submission
`S1, S3, S2, S4, S5, S6` on `MC-EX03` is graded **per step**, and both positions are marked and
diagnosed:

| Position | Submitted | Expected | Status | Signature | Note |
|---|---|---|---|---|---|
| 1 | `S3` | `S2` | misplaced | `MC-2C-01` | *Sākuma nolasījumu nedrīkst pielādēt līdz nullei: izlietotais tilpums ir starpība, un izliekts sākuma līmenis to izjauc.* |
| 2 | `S2` | `S3` | misplaced | `MC-2C-01` | *Piltuves atstāšana biretē ir klasiņas klūda: tā maina sākuma līmeni nezināmo veidā.* |

Both steps carry **their own** signature assignment and **their own** note and feedback string
(*Atkārtot saistīto konceptu*), and the two notes are distinct — the harness asserts it. The
aggregate `signatures` list collapses to one entry because a card's family shares one signature
across its steps; the per-step signature assignments are what the diagnosis is made of, and both
are returned.

The remediation path resolves: each wrong step produces a remediation entry naming the card, the
step, the signature, the note and the resolved feedback string. That is the contract N28 consumes.

## 4. The self-assessment boundary

A learner's own words in a critical-step explanation are **self-assessed only**. The engine records
the text and returns a pending state. The only operation performed on the text is a **blankness
test**.

| Fixture | Input | Verdict | Pending points | Text parsed |
|---|---|---|---|---|
| `NV-N19-SELF-01` | a full Latvian explanation | `pending_self_assessment` | 2,0 | **no** |
| `NV-N19-SELF-02` | three spaces | `incorrect` / `BLANK_RESPONSE` | 0 | no |

The harness asserts `signatures.length === 0` and `text_parsed === false` on the pending path. The
behavioural proof (§3.2, part 3) shows that adding free text to any of the three graded engines
leaves the verdict record byte-identical.

**Recorded limitation.** The blankness test strips whitespace and checks emptiness — nothing else.
It does not normalise case, strip punctuation or fold any other content, so a submission of only
punctuation is not blank. This is declared, not hidden, and no semantic interpretation of the text
is claimed.

## 5. The integration fixtures

### 5.1 The map slot and the focus trace

The card drawer mounts from the map's outcome slot. The harness mounts the slot for outcome
`P2-07` from the trigger `map-btn-P2-07` and asserts that the **card heading takes focus** when the
card opens.

| Card | Heading focused | Trigger | Steps | Revealed at open |
|---|---|---|---|---|
| `MC-EX03` | yes | `map-btn-P2-07` | 6 | 0 |

Revealing a step afterwards makes its note node visible and returns the step's reasoning and its
signature; the remediation entry point resolves the same note for a step id.

### 5.2 The bidirectional reference table — 14/14

"Bidirectional" is **proven in every direction**, not asserted by one populated field:

| Direction | Requirement |
|---|---|
| card → outcomes | the card's `outcome_ids` resolve in the coverage island |
| outcomes → card | a coverage outcome declares the card's practice family |
| card → chain | the card's `chain_id` resolves in the chain registry |
| chain → card | the chain's `back_links.method_card_ids` name the card |
| card → item | a practice reference names the card's family |

All 14 rows are `BIDIRECTIONAL`. The chain direction is enforced from the chain side: a card whose
chain does not name it back fails the gate.

### 5.3 The practice items

`data/chain_references.json` declares `PRAC-EX01`…`PRAC-EX14` for **N20**. Those declarations stay
`declared-pending-N20` and are **not** consumed by N19: N20 authors the method items. The N19 side
of the contract is the reference direction — every card names a family that a practice reference
names back.

## 6. Cross-language parity

Both twins consume the same shipped islands and produce the same canonical projections.

| Table | Rows | Python | JavaScript | Status |
|---|---|---|---|---|
| Stratum verdict records | 17 | identical | identical | **EQUAL** |
| N05 verdicts | 10 | identical | identical | **EQUAL** |

The canonical projection is sorted-key with fixed decimals, so the digests are comparable across
languages rather than merely within one. The full verdict-record row is the strongest: every field,
from the oracle fields through the diagnostics and the citations, matches record for record.

## 7. Runtime budget

| Measure | Value | Ceiling | Status |
|---|---|---|---|
| Runtime JS code in the artifact | 225,197 B | 225,280 B | 83 B headroom, unchanged by N19 |
| `#sim-method-cards` island (shipped, sealed projection) | **109,919 B** | 131,072 B | PASS (21,153 B headroom) |
| `data/method_cards.json` source (canonical) | 84,088 B | — | recorded for reference |
| `#sim-method-engine` island | 22,448 B | 131,072 B | PASS |
| `src/method-engine.js` | 35,170 B | 40,960 B | PASS (5,790 B headroom) |
| `src/method-card-view.js` | 12,105 B | 65,536 B | PASS |
| `output/simulator.html` | 1,124,577 B | declared 700–1400 KiB | PASS |

**The cards budget measures the shipped island, not the source file.** The sealed projection is
larger than the source because it carries the sealed diagnostics, and the shipped size is what the
artifact actually pays for. The source size is recorded alongside so the difference is visible
rather than confusing.

**Recorded limitation.** The runtime-JS ceiling had only 83 bytes of headroom when N19 started, so
both new modules ship from `src/` and are **not inlined** into the artifact's executable script.
The card drawer mounting is therefore proven in the harness against the shipped islands, not in the
shipped HTML. **N31 owns the resolution** (inline, lazy-load or re-budget), exactly as for N17 and
N18. The ceiling itself was not changed by N19.

## 8. The smoke vector

`SMK-N19-METHOD-ORDERING` asserts a fixed transposed ordering submission graded per-step:

| Field | Value |
|---|---|
| Verdict | `incorrect` / `WRONG_ORDER` |
| Wrong positions | 1, 2 |
| Per-step | `S1` correct; `S3` misplaced; `S2` misplaced |
| Signature | `MC-2C-01` |
| Digest | `b73cbb00…bf594a4` |

**Recorded limitation.** The artifact's own smoke subset (`src/smoke-subset.js`) cannot be extended
within the 83-byte headroom, so — exactly as N17 and N18 did — the smoke vector is registered in
the runtime harness with its in-file digest assertion rather than inside the artifact. The
artifact's smoke subset is unchanged.

## 9. The copy lint

The lint runs over **all** card text: 232 term keys, 541 unit fields, 435 exempt prose fields.

| Check | Result |
|---|---|
| N10 term grammar (unit strings) | PASS |
| N09 feedback lint on the misconception notes | PASS |
| Safety citation check (≥ 0,9 overlap) | PASS (3/3 at 1,00) |
| No blame language in card text | PASS |
| No forbidden positive exam claims | PASS |

## 10. Regression

* Build: `python3 tools/build.py` — gates 1–15 PASS, `output/simulator.html` 1,124,577 B,
  `build_id=2c87bec918626b84`, `runtime_js_code_bytes=225,197` ≤ `225,280`.
* Runtime harnesses: N11, N12, N13, N14, N15, N16, N17, N18, N19 — all PASS.
* The frozen inputs are untouched: `data/golden_vectors.json`, `data/coverage.json`,
  `data/terms.json` and `data/chains.json` carry the same digests as before N19
  (`27b0a0d2…eca88`, `f33f61be…009c3`, `007cce83…5cd26`, `52448ee3…12aaf34`; the shipped
  `#sim-chains` island remains `4b610106…626c27`).
* The N15, N16, N17 and N18 corpora were re-run against the N19 artifact and all PASS. Their
  evidence records embed the artifact digest, so their digests moved with the rebuild; the ledger
  records the new digests as superseding rows (N19-E20…N19-E24) rather than rewriting the earlier
  ones.

**Recorded ledger drift, not repaired by N19.** A sweep of every ledger row against the files on
disk found **14 rows** whose recorded digest was already stale before N19 started — each is a file
a later task edited after the earlier row was written, without a superseding row. None is an N19
artifact and none was touched by N19; every affected script still runs and passes. The list is
recorded in the ledger rather than papered over: re-recording another task's digest belongs to the
task that owns that file.

## 11. What is explicitly not claimed

* No browser render, screen-reader, print or instructor-acceptance claim.
* No official examination, grade or proctoring claim.
* No point weight, question count or pass mark is claimed — the 2025 programme fixes none.
* The signatures are the N04 stub pattern because **N09 is absent from this workspace**; the gap is
  recorded in the artifact, not silently filled.
* The card drawer is proven in the harness, not in the shipped HTML, because the runtime-JS ceiling
  had 83 bytes of headroom.
* The free-order group covers only the one pair the masters leave unordered; it is not a general
  tolerance for "almost ordered" sequences.
