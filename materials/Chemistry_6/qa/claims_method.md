# Claim ledger — method (`qa/claims_method.md`)

**Task:** T01 — *Register and falsify high-risk visible claims* (Workstream: Terminology & Sourcing).
**Artefacts:** `qa/claims.csv` (the ledger), `tools/check_claims.py` (the gate),
`tools/build_claims_ledger.py` (the ledger builder), `qa/claims_gate.md` (gate report),
`qa/claims_fixtures/` (fixture suite).

The ledger exists for one reason: an unregistered absolute ("always", "never",
"every number is recomputed") in visible teaching text implies a level of
verification the evidence does not support. Every high-risk visible claim must
therefore be **registered** — with its source, its status and its disposition —
or be **removed**. A claim that cannot be registered against a source is not a
claim this material may make.

---

## 1. Scope

**In scope.** Visible, reader-facing prose of the generated master
(`Master_oksidesanas_reducesanas_procesi.html`) that a student could read as an
assertion about chemistry, about the course material, or about the document
itself:

* numeric values stated in running text (volumes, percentages, potential
  differences, derived equilibrium constants);
* unqualified universals ("vienmēr", "nekad", "garantē", "100 %");
* the change-log statements in 13.E that document what the material claims.

**Out of scope.** Rewriting every sentence, adding chemistry, and any numeric
correction owned by another workstream (see §8, Boundaries).

---

## 2. Inclusion rules (what becomes a ledger row)

A span of visible text becomes a *candidate* when it matches one of the
registered patterns in `master_data.CLAIM_ABSOLUTE_PATTERNS` or
`master_data.CLAIM_NUMBER_PATTERNS`, and it survives the exclusions in §3.

Current pattern set:

| Kind | Pattern | Meaning |
|---|---|---|
| `absolute:vienmēr`, `absolute:nekad`, `absolute:vienīgā`, … | 12 patterns (`vienmēr`, `vienmērīgi`, `nekad`, `galvenī`, `vienīgais`, `vienīgā`, `bezgalīgi`, `garantē`, `droši`, `noteikti`, `100 %`, `nav iespējams`) | an unqualified universal |
| `number:potenciālu starpība` | `par \d+[,\.]\d+ V` | a potential difference asserted in prose |
| `number:procents` | `\d+[,\.]\d+ %` | a percentage asserted in prose |
| `number:tilpums` | `\d+[,\.]\d* mL` | a volume asserted in prose |
| `number:reizinājums` | `\d+ ×` | a scaling factor asserted in prose |
| `number:equilibrium constant` | `lg K ≈ \d+[,\.]\d+` | a derived equilibrium constant |

`100 %` is treated as a **completeness claim** only when a word follows it
("100 % pārbaudīts"). In `· 100 %` it is the multiplication operator of a mass
fraction, not a claim — that reading is not a universality and is excluded.

### 2.1 The scan is sentence-level and block-aware

`tools/check_claims.py --scan` parses the generated HTML with a small
block-aware parser (`MasterParser`):

* every open element owns a text buffer; inline elements hand their text to the
  nearest enclosing block, so a `<p>` containing `<span class="value"
  data-num>` yields one sentence that still carries the registered number;
* blocks (`p`, `li`, `td`, `h*`, `div`, `caption`, …) are emitted when they
  close, and each block is split into sentences on `.`, `!`, `?`, `;`;
* a fraction keeps its numerator and denominator apart (`num / den`);
* the anchor of a candidate is the nearest enclosing element id, so every row
  points at a place in the document that can be reached.

A number is *not* a candidate when every numeric token in the sentence is
already covered by the `NUMBERS` registry (`tools/master_data.py`), because
those values are pre-computed, unit-keyed and re-verified by
`tools/verify_numbers.py`.

**Measured baseline on the current build:** 59 candidates / 54 unique texts —
13 absolute matches and 46 number matches.

---

## 3. Exclusions (text that is not a claim of this document)

| Excluded | Why | Mechanism |
|---|---|---|
| Headings (`h1`–`h6`) | a heading names a section; it does not assert | parser skips heading blocks |
| Quoted source wording | `<span class="quote">` reproduces a source's own sentence; the source is the warrant, not the material | inline skip-class, text dropped from the block |
| Deliberately wrong forms | `<span class="wrong-line">` in mistake cards | inline skip-class |
| Rejected forms | `<span class="nelietot">`, `<span class="term-avoid">` — the "do not write" column of the glossary | inline skip-class |
| Question prompts | `<span class="recall-q">`, `<span class="prompt-id">` | inline skip-class |
| Maintainer meta | `<span class="term-decision">`, `<span class="status-tag">`, `<span class="claim-cite">` | inline skip-class |
| Source label cells | `<span class="source">` | inline skip-class |
| Change-log rows | `changelog-row` / `chlog-row` — the ledger's own source, audited in 13.E | block skip-class |
| Registered numeric values | already verified by `tools/verify_numbers.py` | numeric-token test against `NUMBERS` |
| Captions, table headers | `caption`, `figcaption`, `th` | block skip |
| Script, style, SVG, head | not visible prose | tag skip |

**Scope-limited universals are not claims and are not gated.** "Tikai šķīdumā",
"katrs solis", "viss vienāds" — teaching statements that are true inside the
scope they name — are legitimate. Only *unqualified* universals are matched.
Including the scoped ones would have produced 196+ rows, almost all false
positives; the decision and its measurement are recorded here so the boundary
can be re-examined rather than rediscovered.

---

## 4. Ledger schema

`qa/claims.csv`, header exactly:

```text
claim_id,anchor,text,type,source_ids,status,action,reason
```

* **`claim_id`** — unique. Two families:
  * change-log seeds use the change-log id (`A1`…`A27`, `B1`…`B12`, `C1`…`C9`,
    `T1`…`T7`, `R1`…`R4`, `D1`…`D10`), so a ledger row and
    a 13.E row are the same object and can never drift apart;
  * prose rows use `P001 … P059` in scan order, assigned by
    `tools/build_claims_ledger.py`.
* **`anchor`** — an element id that exists in the generated master. For seeds
  this is the section anchor where the change is visible (one mapping: the
  change log's `ch0` → the real opening-section id `sakums`). For prose rows
  it is the candidate's own anchor.
* **`text`** — the claim as it is visible. For seeds: the change-log row's
  *master wording*. For prose rows: the extracted sentence, verbatim.
* **`type`** — the kind of claim: `fact`, `number`, `absolute`, `derived`,
  `pedagogical`, `meta`.
* **`source_ids`** — `;`-separated source ids, every one of which must exist
  in `master_data.SOURCE_IDS`.
* **`status`** — the epistemic state: `verified`, `corrected`, `noted`,
  `scoped`, `unverified`.
* **`action`** — the disposition: `keep`, `narrow`, `rewrite`, `defer`,
  `remove`.
* **`reason`** — the warrant: what was checked, against what, and why the
  status and action follow.

### 4.1 Source-id vocabulary (interim)

`SOURCE_IDS` lives in `tools/master_data.py` because T03's `qa/sources.csv`
does not exist yet. **T03 must reconcile these ids into the bibliographic
registry; the ids themselves are immutable** — the ledger already depends on
them.

| Id | Warrant |
|---|---|
| `T13` | `13 temata apraksts.pdf` — topic scope and learning outcomes |
| `LEC` | `Oksidesanas_reducesanas procesi_2022.docx` — lecture theory |
| `L25` | `6LW_MCh_Titration_Permanganatometrija_2025.pdf` — titration lab |
| `L21` | `6LW_Ox-red_LV_2021.pdf` — manganese media lab |
| `L20` | `Oksidesana_reducesana_reakcijas_2020.pdf` — older worked lab |
| `CRC` | CRC standard reduction potentials (local dump `qa/verify_crc.txt`) |
| `CAMP` | Campbell Biology ch. 8 sample (local dump) |
| `LIBRE` | LibreTexts standard reduction potentials by element |
| `TERMI` | termini.gov.lv / AkadTerm — Latvian terminology |
| `IUPAC` | IUPAC Gold Book — definitions (access attempted; not re-checked) |
| `PUBC` | PubChem — molar masses |
| `BIONUM` | BioNumbers — database dump |
| `QA` | the material's own QA tooling — `qa/plan.md`, `tools/recall_matrix.py`, `qa/numbers.csv` |

`QA` warrants a claim about *the document itself* (e.g. "118 questions …
66,5 % of 170"). It is not a substitute for a course source and may not be
used to warrant a chemistry fact.

> **Open item for T03.** The molar-mass table `master_data.MOLAR` /
> `ATOMIC` has no registered external source; rows that depend on it are
> warranted by `QA` (the internal registry) plus the course data. T03 must add
> an atomic-weights source or the values stay internally warranted.

---

## 5. Statuses, actions and their transitions

| Status | Meaning | Allowed actions |
|---|---|---|
| `verified` | the claim as stated is warranted by a registered source | `keep`, `narrow`, `rewrite` |
| `corrected` | the claim was wrong and has been corrected in the material | `rewrite`, `remove` |
| `scoped` | the claim is true only inside a stated scope; the scope is written down | `keep`, `narrow` |
| `noted` | the claim is a documented addition or simplification *without* a source; the material says so | `keep`, `narrow` |
| `unverified` | the claim contains a value or statement that the registered sources cannot confirm | `defer`, `rewrite`, `remove` |

| Action | Meaning |
|---|---|
| `keep` | the wording stands |
| `narrow` | the scope is reduced to what the source supports |
| `rewrite` | the wording changes (the new wording must itself be registered) |
| `defer` | the claim is referred to the workstream that owns it (T04/T05 numeric derivations, T03 source registry) |
| `remove` | the claim leaves the material |

### 5.1 Transitions

```text
                evidence found
   unverified ─────────────────► verified ──► corrected (only if the value was wrong)
        │  ▲                        │
        │  │  new source or         │ scope limit found
        │  │  derivation            ▼
        └──┴──── defer ────────── scoped
                │  ▲                  │
                │  │ workstream       │ scope limit found
                ▼  │ answered         ▼
             remove                noted
```

Rules:

1. **A claim may not move to `verified` without a registered source id.** The
   gate enforces this: an unknown id fails the ledger.
2. **`unverified` never silently becomes `verified`.** It may only leave that
   state through `defer` (another workstream answers) or `rewrite` (the claim
   is removed or replaced by a warranted one).
3. **`scoped` is the default for a true-but-limited statement.** A universal
   that is true only inside a scope is rewritten to name the scope, or it is
   `noted` when the scope is inherent (a definition, a lab procedure).
4. **Retirement.** A row is retired (removed from the ledger) only when the
   claim is no longer visible in the document — the gate's stale-row check
   enforces the reverse direction and fails the build if a prose row's text
   can no longer be found among the extracted candidates. Retired rows are
   not deleted silently: the change is recorded in `qa/design.md` with the
   before/after text.
5. **Adding prose creates an obligation.** If a sentence introduces a number or
   a universal, it must be registered in the same change. The gate fails the
   build when an extracted candidate has no ledger row, so the obligation is
   machine-enforced, not editorial.

---

## 6. Status of the current ledger

| | Rows |
|---|---:|
| Change-log seeds | 69 |
| Prose candidates | 59 |
| **Total** | **128** |

Within the 120–160 band the task allows, and **not padded**: every row is
either one of the 69 change-log statements or one of the 59 measured
candidates. No row was invented to reach a number.

---

## 7. Ten manually reconciled rows

Each row was checked by hand against the course text dumps in `qa/` and the
CRC dump `qa/verify_crc.txt`, not against the master's own claims.

| Row | Claim | Checked against | Verdict |
|---|---|---|---|
| `A3` (number, verified, keep) | "Darba vērtība 1,46 V; avota vērtība paturēta 13.A." | CRC dump line 232: PbO₂ + 4H⁺ + 2e⁻ → Pb²⁺ + 2H₂O = **1.455 V** | CRC 1,455 V matches the working value 1,46 V. Source value kept and labelled. **Verified.** |
| `A2` (number, verified, keep) | "Darba vērtība +1,07 V; avota +0,96 V paturēta 13.A." | CRC dump line 91: Br₂(l) + 2e⁻ → 2Br⁻ = **1.066 V** | 1,07 V is the rounded CRC value; Br₂ stays between I₂ and Cl₂. **Verified.** |
| `D1` (derived, unverified, defer) | "Standartizācija ar skābeņskābi vai nātrija oksalātu; siltā titrēšana (ap 60–70 °C); autokatalīze ar Mn²⁺." | `qa/lec.txt` P270 ("Precīzas KMnO₄ koncentrācijas noteikšanai lieto skābeņskābes H₂C₂O₄ šķīdumu"); `qa/l20.txt` line 117 `2KMnO₄ + 5H₂C₂O₄ + …` | Standardisation **is** sourced. "60–70 °C" and "nātrija oksalāts" appear in **no** course source. Row marked `jāpārbauda`; the number is deferred to T04/T05. **Unverified.** |
| `D7` (pedagogical, verified, narrow) | "Svaigs paraugs; H₂SO₄ pievienošana palēnina gaisa skābekļa oksidēšanu." | `qa/l25.txt` 1. daļa: "lūdziet jaunu paraugu"; "H2SO4 izmanto, lai iegūtu skābu vidi" | Fresh sample and acid addition are sourced; the **air-oxidation acceleration** clause is sourced nowhere and was not visible in the prose either (the string "palēnina" occurred only in the change log). The 13.E wording was narrowed to what L25 supports. **Narrowed.** |
| `P001` / `P010` (derived, unverified, defer) | "Cr₂O₇²⁻ satur 14 H⁺, tāpēc pie pH 3 potenciāls krīt par 0,28 V (E = 1,05 V pret Cl₂ 1,36 V)." | LEC P067 gives the expression with n = 6 and [H⁺]¹⁴ → slope 0,0592·14/6 = 0,1381 V/pH; at pH 3 the drop is **0,4144 V** and E = 1,33 − 0,4144 ≈ **0,92 V** | 0,28 V and 1,05 V correspond to **pH 2**. The label and the numbers disagree. Numeric convention belongs to T04/T05. **Unverified.** |
| `P029` (number, unverified, defer) | "Avota vērtība ir par 0,35 V augstāka;" | 1,80 − 1,46 = **0,34 V** | The prose rounds before subtracting. Unrounded-then-round-once is T04/T05's call (H-05). **Unverified.** |
| `P030` (derived, verified, keep) | "Darba vērtība ir 1,46 V (CRC 1,455 V) … ΔE° = −0,05 V" | 1,46 − 1,51 = −0,05 V; CRC basis 1,455 − 1,51 = −0,055 V, and both appear in the 4.4 table | The difference is computed from the working values, and the CRC basis is disclosed next to it. **Verified.** |
| `P015` (meta, verified, keep) | "118 jautājumi par 113 unikāliem jēdzieniem – 66,5 % no 170, virs 30 % sliekšņa un virs 50 % mērķa." | `tools/recall_matrix.py`: 118 prompts / 113 unique concepts / 170 concepts = **66,47 %**; `qa/plan.md` line 231: "gate is ≥ 30 %, target ≥ 50 %" | The document's self-description is accurate and re-computable. **Verified** (warrant `QA`). |
| `P007` (absolute, verified, keep) | "Šīs divas lomas vienmēr ir kopā: elektroni nepazūd un nerodas no jauna." | LEC ch. 2 — electron balance; oxidation and reduction are simultaneous halves of one reaction | A universal that is true by conservation, not an empirical over-claim. **Verified.** |
| `P055` (derived, unverified, defer) | "Tāpēc ΔE° = +0,05 V un lg K ≈ 4,2 – iespējams, bet tuva robeža;" | lg K = z·ΔE°/0,0592 with z = 5 → 4,2; but the integer-balanced reaction 2 MnO₄⁻ + 5 Pb²⁺ + 8H⁺ → 2 Mn²⁺ + 5 PbO₂ + 10H₂O has **z = 10** → lg K = **8,4** | The material itself teaches (B9, D8) that z is the electron count of the balanced reaction, so the two are inconsistent. Deferred to T04/T05. **Unverified.** |

---

## 8. Boundaries

* **T03 owns the source registry.** T01 supplies the interim id vocabulary and
  the ledger rows; T03 reconciles it into `qa/sources.csv`. No id is invented
  here — `SOURCE_IDS` describes documents that exist in this workspace.
* **T04/T05 own numeric derivations and potential conventions.** T01 does not
  change a potential, a concentration, a temperature or an equilibrium
  constant. It registers the claim and defers it. The one exception is a
  *wording* whose warrant fails outright (the LIBRE reference no longer says
  the Cr₂O₇ comparison is "audit-confirmed", but "the external comparison is
  still unresolved").
* **A claim may be narrowed even when its number is not T04/T05's.** Coverage
  overstatement is T01's own subject: a change-log row that describes more
  than the document says is corrected here (D7).
* **The master is never hand-edited.** All copy changes go through
  `tools/build_master.py` / `tools/master_data.py` and a rebuild.

---

## 9. Reproducing the ledger

```bash
python3 -I tools/check_claims.py --scan      # the measured candidate baseline
python3 -I tools/build_claims_ledger.py      # regenerate qa/claims.csv
python3 -I tools/check_claims.py             # validate; writes qa/claims_gate.md
python3 -I tools/check_claims.py --fixtures  # valid / missing-source / unsupported-universal
```

The gate fails the build when:

* a `claim_id` repeats, an `anchor` does not exist, a `source_id` is unknown,
  or a `type` / `status` / `action` is outside the vocabulary;
* an extracted candidate has no ledger row (an unregistered claim);
* a ledger row's text can no longer be found in the prose (a stale row);
* a banned overclaim phrase is present in the generated text.

The gate writes **only** `qa/claims_gate.md`. It never edits the master, the
generator or the sources.
