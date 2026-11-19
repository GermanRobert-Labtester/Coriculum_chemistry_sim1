# N02 labeling audit — official facts versus training-policy proposals

**Task:** N02 (Phase I). **Artifact audited:** `data/coverage.json` (64 outcomes, 7 topics). **Execution:** 2026-11-17, this environment. **Machine check:** `python3 tools/validate_coverage.py --report evidence/N02_VALIDATION_RECORD.json` → PASS (see `evidence/N02_VALIDATION_RECORD.json`, `checks.labels`).

## 1. What is official

The only official facts in the island are the programme's own record. Their source is `RSU_MedChem_Colloq1_Prog_LV_2025.pdf`, SHA-256 `f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9`, 353,208 bytes, as extracted in `evidence/programme_extracted.txt`.

| Island field | Label | Official content | Programme quote (normalised) |
|---|---|---|---|
| `topics[1].official_heading` | `PROGRAMME-SOURCED` | Topic 1 name | `1. Temats. IEVADS. ŠĶĪDUMI UN ĶĪMISKĀS REAKCIJAS` |
| `topics[2].official_heading` | `PROGRAMME-SOURCED` | Topic 2 name | `2. Temats. APRĒĶINI UN GRAFISKĀS METODES ĶĪMIJĀ` |
| `topics[3].official_heading` | `PROGRAMME-SOURCED` | Topic 3 name | `3. Temats. ŠĶĪDUMI UN KONCENTRĀCIJU APRĒĶINI` |
| `topics[4].official_heading` | `PROGRAMME-SOURCED` | Topic 4 name | `4. Temats. TERMODINAMIKA UN TĀS PIEMĒRI BIOLOĢISKAJĀS SISTĒMĀS` |
| `topics[5].official_heading` | `PROGRAMME-SOURCED` | Topic 5 name | `5. Temats. KINĒTIKA UN TĀS NOZĪME BIOLOĢISKAJĀS SISTĒMĀS` |
| `topics[6].official_heading` | `PROGRAMME-SOURCED` | Topic 6 name | `6. Temats. OKSIDĒŠANĀS – REDUCĒŠANĀS PROCESI` |
| `topics[7].official_heading` | `PROGRAMME-SOURCED` | Topic 7 name | `7. Temats. ANALĪZES METODES ĶĪMIJĀ` |
| `official_facts[OF-2]` | `PROGRAMME-SOURCED` | Paper examination | `Kolokvijs notiek klātienē, darbs tiek rakstīts uz papīra.` |
| `official_facts[OF-3]` | `PROGRAMME-SOURCED` | 180-minute maximum | `Maksimālais pārbaudījumam pieejamais laiks 3 stundas (180 minūtes)` |

The validator asserts that every `official_heading` and every `evidence_quote` occurs in `evidence/programme_extracted.txt` after whitespace normalisation. The island therefore cannot silently replace an official heading with a paraphrase.

## 2. What is proposed

Everything below is training policy. The programme PDF states topics, content and skills; it does not define 64 outcome-level statements, a 9/10/11/11/10/8/5 split, prerequisite edges, points or minutes.

| Island field | Label | Why it is proposed |
|---|---|---|
| `expected.total` = 64 | `PROPOSED` | A training-policy granularity chosen by this roadmap. |
| `expected.per_topic` = 9, 10, 11, 11, 10, 8, 5 | `PROPOSED` | A training-policy distribution; the programme does not enumerate outcomes. |
| `outcomes[].statement_lv` | `PROPOSED` | A Latvian derivation aligned to the master section's heading and lead. |
| `outcomes[].prerequisites` | `PROPOSED` | The N07 concept graph authored by N02; only Topic 1's explicit master chains are direct source statements. |
| `bindings.practice_families` | `PROPOSED` | The planning source's family mapping, not an official requirement. |
| `bindings.exam_slots` | `PROPOSED` (unfilled) | Declared slot for N24's assembly policy. |
| `bindings.points`, `bindings.minutes` | `PROPOSED` (null) | Declared slots for N24's policy; N02 does not assign values. |

The island records this split in `epistemic_contract`, `training_policy` (all `PROPOSED`) and each outcome's `statement_label` / `granularity_label` (both `PROPOSED`). The validator fails if any outcome statement claims a non-`PROPOSED` label or if the `training_policy` block loses its `PROPOSED` entries.

## 3. Master wording versus planning wording

The masters are the scientific authority. Where the planning source's wording differs from the anchored master section, the island keeps:

- `planning_statement_lv`: the planning source's exact wording, never silently edited;
- `statement_lv`: the master-aligned wording;
- `comment`: a note that states why the wording changed and where the displaced concepts are covered.

Ten entries carry a non-null `comment`; the other 54 use the planning wording unchanged and carry `comment: null`.

| Outcome | Anchored master section | Planning wording | Island statement | Comment recorded |
|---|---|---|---|---|
| P1-02 | `#maisijumi` — Maisījumi un dispersijas | Homogēni un heterogēni maisījumi | Maisījumi un dispersijas, tostarp homogēni un heterogēni maisījumi | Yes |
| P2-04 | `#ch-3` — Mērīšana un analītiskais signāls | Kvalitatīvi un kvantitatīvi dati | Mērīšana un analītiskais signāls: kvalitatīvi un kvantitatīvi dati | Yes |
| P3-01 | `#n5` — Koncentrāciju veidi un to lietojums medicīnā | c, w, γ un šķīduma, šķīdinātāja, izšķīdušās vielas jēdzieni | Koncentrāciju veidi (c, w, γ) un šķīduma, šķīdinātāja un izšķīdušās vielas jēdzieni | Yes |
| P3-04 | `#n4` — Vielas daudzums, molmasa un mērvienības | M, m, V, n, w, c, ρ un γ saistības un vienības | Vielas daudzums, molmasa un mērvienības (M, m, V, n, w, c, ρ, γ) | Yes |
| P4-02 | `#ch4` — Entalpija un siltumefekti | Entalpija, entropija un Gibsa enerģija | Entalpija un siltumefekti | Yes |
| P4-04 | `#ch3` — Pirmais likums | Pirmais un Otrais termodinamikas likums | Pirmais termodinamikas likums un enerģijas bilance | Yes |
| P4-08 | `#ch7` — Gibsa enerģija un patvaļības kritērijs | Temperatūras ietekme uz entropiju un patvaļīgumu | Gibsa enerģija, patvaļības kritērijs un temperatūras ietekme | Yes |
| P5-01 | `#ch1` — Reakcijas ātrums | Reakcijas ātrums, ātruma vienības, aktivācijas enerģija un katalizators | Reakcijas ātrums un ātruma vienības | Yes |
| P7-01 | `#h1` — Kāpēc gaismu var izmantot daudzuma mērīšanai | Spektrofotometrijas izmantošanas iespējas | Gaismas izmantošana daudzuma mērīšanai: spektrofotometrijas iespējas | Yes |
| P7-04 | `#h10` — Laboratorijas darbs 6B soli pa solim | Koncentrācija, masa un vielas daudzums no kalibrēšanas grafika | Laboratorijas darbs 6B: koncentrācija, masa un vielas daudzums no kalibrēšanas grafika | Yes |

## 4. The audit note

> The programme PDF's own text carries no outcome-level split. It names seven topics and states the content and skills within them. The 64-outcome granularity, the 9/10/11/11/10/8/5 distribution, the prerequisite edges and the point/minute slots are this roadmap's training-policy derivations, honestly labeled `PROPOSED`. The topic names, the paper format and the 180-minute maximum are the programme's facts, labeled `PROGRAMME-SOURCED`. The master sections are the scientific authority for the statements; the planning source's wording is preserved beside every changed statement and explained in the entry's `comment`.

This note is repeated in the island's `training_policy[TP-1]`, which the validator requires to state that the programme PDF does not define the outcome-level split; `training_policy[TP-2]` records the derivation rule for the outcome statements.
