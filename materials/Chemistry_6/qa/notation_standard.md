# Notation standard — charge vs oxidation state

Binding rule: `SOURCE_AUDIT.md` B1, `AGENTS.md` §5. One glyph never serves both roles.

## Rule

| Role | Form | Glyph pattern | Example |
| --- | --- | --- | --- |
| **Jonu lādiņš** (charge) | number then sign, superscript | `Fe³⁺`, `SO₄²⁻`, `MnO₄⁻`, `e⁻` | real ion or electron |
| **Oksidēšanas pakāpe** (oxidation state) | sign then number in text, or Roman numeral in a name | `+4`, `−2`, `+7`, `mangāns(VII)`, `S(+4)` | formal bookkeeping |
| **Nepareizi** (quoted) | charge-style used as if it were an oxidation state | `S⁴⁺`, `Mn⁷⁺`, `O²⁻` as “the sulphur ion” | only inside `.wrong-line` or `.quote[data-notation="wrong"]` |

Minus is U+2212 `−`, never a hyphen.

## Twelve teaching pairs

| # | Charge (correct ion / electron) | Oxidation state (correct) | Common wrong form |
| --- | --- | --- | --- |
| 1 | Fe³⁺ | Fe(+3) or +3 | Fe³⁺ used to mean “oxidation state 3” on a covalent centre |
| 2 | SO₄²⁻ | S(+6) | S⁶⁺ |
| 3 | MnO₄⁻ | Mn(+7) or mangāns(VII) | Mn⁷⁺ |
| 4 | O₂ (neutral molecule) | O(0) in O₂; O(−2) in H₂O / oxides | O²⁻ as a free ion inside O₂ |
| 5 | H₂O₂ | O(−1) | O⁻ as if peroxide were two O⁻ ions without context |
| 6 | Cr₂O₇²⁻ | Cr(+6) | Cr⁶⁺ |
| 7 | NO₃⁻ | N(+5) | N⁵⁺ |
| 8 | S₂O₃²⁻ | S(+2) average | S²⁺ |
| 9 | MnO₄²⁻ | Mn(+6) | Mn⁶⁺ |
| 10 | Cl₂ | Cl(0) | Cl⁰ written as Cl⁰⁺ / Cl |
| 11 | H⁺ | H(+1) | writing “H¹⁺” for the oxidation state of H in H₂O |
| 12 | e⁻ | — (electron is a charge carrier, not an oxidation state) | treating e⁻ as an oxidation number |

## How the master marks them

- Correct charges go through `ion(...)` / `[[Fe^3+]]` → `.notation-charge`.
- Correct oxidation states go through `os(...)` / `S(+4)` / `[[os:+4]]` → `.notation-os`.
- Deliberate wrong forms go through `wrong_form(...)` / `[[w:S^4+]]` → `.quote[data-notation="wrong"]`, usually next to a **Nepareizi** label.
- Change-log and `SOURCE_AUDIT` quotes keep the source wording; they are wrapped as `.quote` so the linter does not treat them as teaching text.

## One-line memory aid

**Lādiņš:** skaitlis, tad zīme (`Fe³⁺`). **Pakāpe:** zīme, tad skaitlis (`+3`). Ja abi izskatās vienādi, pieraksts ir nepareizs.
