# Method card format and the three non-numeric verdict engines

**Owner:** N19 · **Status:** frozen interface for N20, N22, N23 and N28
**Island:** `#sim-method-cards` (`data/method_cards.json`), `#sim-method-engine`
(`data/method_engine_contract.json`)
**Twins:** `tools/method_engine.py` (authoring) · `src/method-engine.js` (runtime)

This document is the contract the downstream tasks read. It describes what a method card is, what the
three engines grade, and what a consumer may rely on. The machine-readable declarations live in
`data/method_card_schema.json` and `data/method_engine_contract.json`; this document explains them.

**Epistemic note.** The 2025 programme fixes no point weight, no question count, no pass mark, no
allowed aid and no exact exam question type. Every step order, criterion shape, free-order group and
acceptance set declared here is **PROPOSED training policy** except the rules inherited verbatim
from the frozen N05 corpus and the masters' own cited teaching. Nothing here is an official
examination, grade or proctoring claim.

---

## 1. What a method card is

A method card teaches one procedure the masters teach: the ordered critical steps, each step's
reasoning, each step's misconception link, the safety entries where the masters teach them, and the
worked chain that carries the numbers.

**A card is data, not prose.** The engine reads structure only: step ids, order positions and pair
identities. It never reads a statement, a reasoning or a note.

The card is rendered with the same collapse-and-reveal discipline as the chains: the learner sees the
step statements, and the reasoning, the misconception note, the signature and the grading rules are
revealed only on interaction.

### 1.1 The required fields

| Field | Type | Rule |
|---|---|---|
| `card_id` | string | `MC-EX01`–`MC-EX14`, unique; matches the `data/chain_references.json` declaration and exactly one `EX` chain |
| `procedure_key` | string | the procedure's name key: lowercase with underscores, no spaces; used as the UI label |
| `title_lv`, `subtitle_lv` | string | the card's name and one-line description |
| `topic` | int | the programme topic (1–7) |
| `family_id` | string | the coverage family; the join key to `#sim-coverage` and to the practice items |
| `chain_id` | string | the referenced worked chain (`EX01`–`EX14`) |
| `outcome_ids` | string[] | every id resolves in `#sim-coverage`, belongs to the card's topic and to its declared family |
| `master_citation` | object | `path` + `anchor` + `heading_lv` + `freeze_id` + `sha256`; the anchor resolves in the frozen master with case-exact matching and the sha256 matches the N01 freeze |
| `order_citation_lv` | string | one sentence saying why this is the master's sequence — the order is **cited, not invented** |
| `epistemic_label`, `banner_lv` | string | the fixed training-material labels |
| `steps` | object[] | the ordered steps |
| `free_order_groups` | object[] | the steps whose physical order the master leaves free |
| `sequence_prompts` | object[] | the sequence-completion prompts |
| `self_assessment` | object | the critical-step explanation prompt |

Optional: `secondary_citations`, `matching`, `safety_note_lv`, `print_note_lv`.

### 1.2 A step

| Field | Rule |
|---|---|
| `step_id` | unique within the card |
| `statement_lv` | what the learner does |
| `reasoning_lv` | why this step is here and why here — recomputable where numeric |
| `misconception_signature` | matches `^MC-[1-7][A-D]-[0-9]{2}$` (the N04 stub pattern) and must exist in the contract's signature registry |
| `misconception_note_lv` | the note that explains the misconception this step's mistake implies |
| `feedback_key` | resolves in `#sim-terms` to a non-empty string |
| `quantity_links` (optional) | the numeric companion |
| `safety` (optional) | a safety entry with a master citation |
| `critical` (optional) | marks a critical step for the self-assessment prompt |

### 1.3 The quantity links

A card **never invents a number**. Each numeric step links to the recomputed chain step:

| Field | Rule |
|---|---|
| `chain_id`, `chain_step_id` | resolve in `#sim-chains` |
| `value_display_lv` | **must equal** the chain step's recomputed display value |
| `unit` | **must equal** the chain step's recomputed unit |
| `quantity_lv` (optional) | what the quantity is, in Latvian |
| `dimension` (optional) | the N10 dimension, when one exists |

The `dimension` field is optional because some pairs (for example `mL`/`mg`) have no matching
dimension in the N10 ledger. The link is still enforced on value and unit.

### 1.4 The safety entries

A safety entry may only restate what the master teaches. It carries a full citation
(`path`, `anchor`, `heading_lv`, `freeze_id`, `sha256`), and the build gate compares the entry
mechanically against the cited master section: the fraction of the entry's content words that
appear in the master must be at least **0,9**. An entry that adds a precaution the master does not
state falls below the threshold and fails the build.

### 1.5 The free-order groups

A free-order group declares steps whose physical order the master leaves free. Its members may be
in any order **among themselves**; the sequence outside the group is strict.

The group is authored **deliberately into one card** — the dilution card `MC-EX06`, group
`FOG-EX06-1` over the two independent weighings — so the grading never penalises the masters' own
freedom. Moving a member **outside** the group's position is still wrong.

Each group carries a `reason_lv` and a citation to the master passage that leaves the order open.

### 1.6 The sequence prompts

| Field | Rule |
|---|---|
| `prompt_id` | unique within the card |
| `prompt_lv` | the question |
| `acceptance_step_ids` | the accepted next steps — **exact id identity**, a set |
| `distractors` | plausible but wrong next steps, each with its own `step_id`, `misconception_signature` and `note_lv`; a distractor may not also be accepted |
| `criterion_id`, `points` | the criterion and its weight |

### 1.7 The matching exercise

`left_items`, `right_items` and `correct_pairs`. Each pair carries `left_id`, `right_id`,
`misconception_signature`, `note_lv` and `feedback_key`, so a wrong pair is **diagnosed** rather
than merely counted.

### 1.8 The self-assessment

```json
"self_assessment": {
  "prompt_lv": "…",
  "grading": "self",
  "pending_semantics_lv": "…"
}
```

`grading` is always `"self"`. The engine records the learner's text and returns a pending state. It
never parses the text. See §4.

---

## 2. The three engines

### 2.1 The shared no-keyword rule

> **Verdicts are computed from structural identity only — step ids, pair identities and order
> positions. No verdict path compares learner text, a step statement or any other prose field, and
> no verdict path uses string similarity, keyword matching or case folding. A near-synonym
> submission is not a correct submission.**

This is enforced three ways, all build-gated:

1. **Static** — the gate tokenises both engine sources and fails on a similarity/keyword/case-folding
   identifier, on a domain keyword literal, and on any comparison of a prose field.
2. **Adversarial** — stratum vectors submit near-synonyms and prose in place of ids and must fail.
3. **Behavioural** — a free-text field added to a submission must leave the verdict record
   byte-identical.

### 2.2 The ordering engine

**Input:** `{ "order": ["S1", "S2", …] }` — a permutation of the step ids.
**Grading:** each position is compared to the declared order; the members of a free-order group are
compared as sets.

| Per-step status | Meaning |
|---|---|
| `correct` | the step is in its declared position |
| `misplaced` | the step is elsewhere; the step's misconception signature is returned |
| `unknown_step` | the submitted id is not a step of this card |
| `missing_step` | a declared step was not submitted |

The verdict is per-step: a wrong step position maps to the signature its note names. The
**awarded criterion stays all-or-nothing** — the per-step diagnostics carry the diagnosis, not the
score. The order is right or wrong per the declared rule; there is no almost-ordered verdict.

### 2.3 The matching engine

**Input:** `{ "pairs": [{ "left_id": "L1", "right_id": "R1" }, …] }`.
**Grading:** per pair, by exact id identity.

| Per-pair status | Meaning |
|---|---|
| `correct` | the pair is one of the declared correct pairs |
| `wrong_pair` | both ids are known but the pair is not correct |
| `repeated_left` | the left item appears more than once |
| `repeated_right` | the right item appears more than once |
| `unmatched` | an item was left without a pair |

A duplicated left item **denies all pairs that touch it**, so the verdict cannot be gamed by
repeating a correct answer. The verdict class is `correct` when every pair is correct, `partial`
when some are, and `incorrect` otherwise.

### 2.4 The sequence engine

**Input:** `{ "next_step_id": "S5" }`.
**Grading:** against the declared acceptance set by **exact id identity**.

| Status | Meaning |
|---|---|
| `accepted` | the id is in the acceptance set |
| `distractor` | the id is a declared distractor; its signature is returned |
| `unknown` | the id is neither accepted nor a declared distractor |
| `blank` | no id was submitted |

### 2.5 The verdict record

The envelope is fixed by `data/method_engine_contract.json#/verdict_record`:

```
engine, kind, verdict_class, error_class, awarded_criteria,
machine_checked_points, self_assessed_points, human_reviewed_points,
pending_points, max_points, diagnostics, replay
```

**Verdict classes:** `correct`, `partial`, `incorrect`, `pending_self_assessment`,
`auto_passed_pending_review`.
**Criterion statuses:** `awarded`, `denied`, `pending`.
**Diagnostics:** always `signatures` and `remediation`.
**Replay:** always `spec_digest` and `submission_digest`, so a verdict is reconstructible from its
own record plus the spec and the submission.

The error classes in use: `NONE`, `WRONG_ORDER`, `WRONG_PAIRING`, `BLANK_RESPONSE`.

### 2.6 The point decomposition

The four point columns keep the machine-checked, self-assessed, human-reviewed and pending points
apart. A machine-checked criterion contributes to `machine_checked_points`; a self-assessed
criterion contributes to `self_assessed_points` **and** to `pending_points` — never to the awarded
total, because the learner has not been graded on it.

---

## 3. The signature registry

`data/method_engine_contract.json#/signature_registry` holds one entry per signature:

```json
{
  "signature": "MC-2C-01",
  "feedback_key": "feedback.concept_link_label",
  "cards": ["MC-EX03"],
  "corpus_vectors": ["GV-S1-T2-Q10-01", "GV-S1-T2-Q10-02"],
  "provenance": "exact-family",
  "note_lv": "…"
}
```

`provenance` is either `exact-family` or `nearest-available-cross-family`. The second value marks a
card whose family has no vector in the frozen S1 stratum and therefore borrows the nearest
available family's signature; the reason is stated in the entry's `note_lv` and is never left to be
inferred.

**The N09 gap.** N09 does not exist in this workspace. The signatures therefore use the N04 stub
pattern `^MC-[1-7][A-D]-[0-9]{2}$` and every one of them must resolve against an **existing vector
in the frozen N05 corpus**. The binding is written into the card island's `n09_gap_notice_lv`, so
whoever implements N09 inherits the constraint instead of re-deriving it. **When N09 lands, this
binding is what must be re-checked — not the card logic.**

The gate sweeps the registry in both directions: a signature no card declares is an orphaned entry
and dangles just as hard as a card signature with no registry entry. Zero dangling is asserted
independently by the Python gate and the JavaScript harness.

---

## 4. The pending semantics (frozen for N23)

> **Brīvā teksta paskaidrojums ir pašnovērtējums. Dzinējs to pieraksta un atzīmē kā pending; tas
> nedod ne punktu, ne verdiktu, ne paraksturu. Tukša atbilde (tikai atstarpes) dod 0 punktus un
> BLANK_RESPONSE; tas ir vienīgais teksta pārbaudes veids.**
>
> **Tukšums ir teksts, kas pēc atstarpju noņemšanas ir tukšs. Saturācija netiek pārbaudīta.**
>
> **Šajā ceļā nav neviena salīdzinājuma ar teksta saturu. Fiksētais N05 orakuls šim ceļam
> atbilst, un N19 vectora komplekts to pārbauda.**

| Case | Verdict | Error class | Pending points | Signatures |
|---|---|---|---|---|
| a self-assessment with text | `pending_self_assessment` | `NONE` | the criterion's points | none |
| a self-assessment that is blank | `incorrect` | `BLANK_RESPONSE` | 0 | none |

**N23's obligation:** surface the pending class for this criterion and award no points for it.
N19 allocates no points and returns no verdict on the text.

**Recorded limitation.** The blankness test strips whitespace and checks emptiness — nothing else.
It does not normalise case, strip punctuation or fold any other content, so a submission of only
punctuation is not blank.

---

## 5. The runtime API

`src/method-engine.js` exposes `SimMethodEngine`:

| Member | Purpose |
|---|---|
| `new SimMethodEngine(contract, terms)` | bind the contract and the terms island |
| `engine.grade(spec, submission)` | grade a submission, returning the verdict record |
| `engine.gradeInstance(instance, submission)` | grade an N05-shaped instance directly |
| `engine.oracleView(record)` | the N05-compatible projection (the eight oracle fields) |
| `engine.specFromCard(card, kind, promptId, rubric)` | build a spec from a card |
| `engine.specFromInstance(instance)` | build a spec from an N05 instance |
| `SimMethodEngine.specForVector(cardsById, vector)` | build a spec from a stratum vector (static) |

`src/method-card-view.js` exposes `SimMethodCards`:

| Member | Purpose |
|---|---|
| `SimMethodCards.load(document)` | read the shipped cards island |
| `SimMethodCards.mountCard(document, host, cardId, …)` | mount one card |
| `SimMethodCards.mountOutcomeSlot(document, host, outcomeId, trigger, cards)` | mount the card(s) an outcome maps to, and move focus to the heading |
| `SimMethodCards.revealStep(document, mountId, stepId)` | reveal one step's reasoning, note and signature |
| `SimMethodCards.stepNote(cardId, stepId, cards)` | the **remediation entry point**: resolve a step's note by card and step id |
| `SimMethodCards.unsealCard / unsealCards` | unseal the shipped island's diagnostics |

**Focus contract.** When a card opens, the card's heading takes focus. A consumer that mounts a card
must not steal it back.

**Remediation contract (N28).** A wrong ordering, matching or sequence verdict produces a
`diagnostics.remediation` entry per wrong step or pair, each naming the `card_id`, the `step_id`,
the `misconception_signature`, the `note_lv`, the `feedback_key` and the resolved `feedback_text`.
That entry is the link target for the remediation link — a verdict links to **the step's note**, not
to a generic concept page.

---

## 6. What a consumer may rely on

* The verdict record's envelope, the verdict classes, the error classes and the diagnostics shape.
* The signature registry and the `feedback_key` → `#sim-terms` resolution.
* The pending semantics and the `pending_self_assessment` / `BLANK_RESPONSE` behaviour.
* The `diagnostics.remediation` shape and the `SimMethodCards.stepNote` entry point.
* The card id, family and chain mapping, and the `procedure_key` UI label.

## 7. What a consumer may not rely on

* Any point weight, question count, pass mark or allowed aid — the programme fixes none.
* Any official examination, grade or proctoring status.
* Any semantic evaluation of the learner's free text — it is never parsed.
* The specific signature a family maps to, if the family had to borrow a cross-family signature:
  re-check the registry's `provenance` and `note_lv` rather than hard-coding the signature.
* The N05 corpus as a place to append N19 vectors — it is frozen and append-only. The N19 stratum
  lives in the contract island (`S4-N19`), following the N17 and N18 precedent.

---

## 8. The shipped island is sealed

The artifact carries the **sealed runtime projection** of the cards, not the source file: the
statements are public, and the diagnostics (reasoning, notes, signatures, grading rules) are
XOR-sealed and revealed only on interaction. A consumer that needs the diagnostics unseals through
`SimMethodCards.unsealCards`.

Do not describe the seal as cryptographic secrecy: the stream key is embedded in the artifact. The
verified property is the **absence of plaintext diagnostics in the pre-reveal DOM and island**.

## 9. The budget

| Measure | Ceiling |
|---|---|
| `#sim-method-cards` island (shipped, sealed projection) | 131,072 B |
| `#sim-method-engine` island | 131,072 B |
| `src/method-engine.js` | 40,960 B |
| `src/method-card-view.js` | 65,536 B |

The cards budget measures the **shipped** island, not the source file: the projection is larger
because it carries the sealed diagnostics, and the shipped size is what the artifact pays for.

**Recorded limitation.** The artifact's runtime-JS ceiling had 83 bytes of headroom when N19
started, so both N19 modules ship from `src/` and are **not inlined** into the artifact's
executable script. The card drawer is therefore proven in the runtime harness against the shipped
islands, not in the shipped HTML. **N31 owns the resolution** (inline, lazy-load or re-budget),
exactly as for N17 and N18.
