# SOURCE_AUDIT — what is wrong, shaky, or inconsistent in the five source files

Prepared 2026-10-31 from a line-by-line read of every source, with arithmetic and
atom/charge checks re-run by script (`tools/check_balance.py --corpus`: 69 equations, all
bookkeeping-balanced except one known defect, A4). This file is the **evidence base** for the
"common mistakes" and "terminology" parts of the master HTML. Do not paste it into the HTML
wholesale; turn each row into the right component (see `PROMPT_master_html.md` §6).

## Citation codes

| Code | File | What it is |
| --- | --- | --- |
| **LEC** | `Oksidesanas_reducesanas procesi_2022.docx` | Lecture text (theory authority). Cite as `LEC P###` using `python3 -I tools/extract_docx.py` numbering, or `LEC table 2` etc. |
| **T13** | `13 temata apraksts.pdf` | Topic 13 outline: prerequisites, learning outcomes, theory list. Defines the **scope**. |
| **L21** | `6LW_Ox-red_LV_2021.pdf` | Lab 6 sheet: Mn colours in acid/neutral/base, blank tables, 3 conclusion questions. |
| **L20** | `Oksidesana_reducesana_reakcijas_2020.pdf` | Older lab sheet **with worked solutions** + self-test tasks 1–2. |
| **L25** | `6LW_MCh_Titration_Permanganatometrija_2025.pdf` | Permanganatometric titration of FeSO4: procedure, data table, calculation. |

## Confidence labels

* **Certain** — arithmetic, atom/charge balance, or an internal contradiction you can show on the page.
* **High** — standard textbook fact (IUPAC Gold Book, CRC Handbook, Harris, Atkins). Still cite it in the HTML.
* **Verify** — depends on edition, convention or local usage. The agent must check an external source
  (IUPAC Gold Book, CRC standard-potential table, AkadTerm / termini.lv for Latvian terms) **before** stating
  the correction as fact, and must say in the change log what it checked. If the check cannot be done, keep the
  source's wording, mark the line as "jāpārbauda" and do not silently change it.

---

## A. Chemistry and data — content that affects correctness

| ID | Where | Source says | Problem and correction | Conf. |
| --- | --- | --- | --- | --- |
| A1 | LEC table 2 (rows Al → Zn) | Element column (Al, Cu, Pb, Sn, Zn) | Element labels are **shifted one row** from Cu onward: "Cu" sits beside Al³⁺/Al, "Pb" beside Cu²⁺/Cu, "Sn" beside Pb²⁺/Pb, "Zn" beside Sn²⁺/Sn; the AlO₂⁻/Al row appears **twice**. Rebuild the table with the label on the row it names; drop the duplicate. | Certain |
| A2 | LEC P078 and table 2 | Br₂/2Br⁻ E° = +0,96 V | Standard tables give **≈ +1,07 V** (1,066 V). +0,96 V is the NO₃⁻/NO value. Changes nothing qualitatively (Br₂ stays between I₂ and Cl₂) but must be flagged. | High |
| A3 | LEC P063, table 2 | PbO₂/Pb²⁺ E° = +1,80 V | CRC gives **+1,46 V** for PbO₂ + 4H⁺ + 2e⁻ → Pb²⁺ + 2H₂O (and ≈ +1,69 V for the PbSO₄ couple). The lecture's conclusion (PbO₂ oxidises Mn²⁺ to MnO₄⁻; the classic test in hot conc. HNO₃) is real, but with +1,46 V < +1,51 V it works **because of concentrations**, not because E° is larger. Good teaching case for "E° is a starting point". **Update T09:** both couples contain H⁺, so both Nernst terms apply; their slopes (−0,1184 and −0,0947 V/pH) nearly cancel and pH alone cannot flip the pair (crossing ≈ 129 mol/L). The working lever is the product ratio: at 15 mol/L HNO₃ equilibrium needs [MnO₄⁻] ≈ 1,3·10⁻²·[Mn²⁺] (CRC 1,455 V: 5,1·10⁻³). Keep +1,80 in the transcribed table with a note; do not overwrite. | Verify |
| A4 | LEC table 1 (last row) and P230 | O₂ + 2e⁻ + 2H₃O⁺ → H₂O + 2H₂O, E = +0,6945 V | **Unbalanced** (4 O left, 3 O right) and uses 2 e⁻. Reducing O₂ to water takes **4 e⁻** — the lecture itself says so in P077: O₂ + 4H₃O⁺ + 4e⁻ → 6H₂O. The value +0,6945 V matches neither E° = +1,229 V (pH 0) nor the biochemical E°′ = +0,815 V (pH 7). Present the balanced 4 e⁻ equation; flag the number. | Certain (balance) / Verify (value) |
| A5 | LEC table 1 | H⁺/H₂ = 0,00 V beside NAD⁺/NADH = −0,3391 V, FAD/FADH₂ −0,2735 V … | **Two conventions mixed.** 0,00 V is E° (all activities 1, pH 0). Biochemical tables use **E°′ (pH 7)**, where H⁺/H₂ is −0,414 V and NAD⁺/NADH ≈ −0,32 V. Direction of electron flow in the chain is judged within one convention only. Teach both and forbid mixing. (E°′ = E° − 0,0592·(m/n)·pH, m = number of H⁺ in the half-reaction.) | High |
| A6 | LEC P229 | "Šo procesu katalizē **citohromkināze**" | A *kināze* transfers phosphate. The terminal step is catalysed by **citohroma c oksidāze** (IV komplekss). Use "elektronu transporta ķēdes kompleksi I–IV". | High |
| A7 | LEC P229 | "NADH⁺ + H⁺ (reducētā NAD)" | Reduced form is **NADH** (carrier of 2 e⁻ + 1 H⁺, often written NADH + H⁺); oxidised form is NAD⁺. "NADH⁺" does not exist. | High |
| A8 | LEC P250 | Iodometry: "titrants ir I⁻ jonu saturošs šķīdums" | In **jodometrija** the sample's oxidant liberates I₂ from **excess I⁻**, and the **titrant is Na₂S₂O₃** (thiosulfate). **Jodimetrija** uses I₂ as titrant. The lecture itself describes thiosulfate in 2.4. Fix both the definition and the pairing. | High |
| A9 | LEC P249 | "Nogulsnēšanas metodes — **sedimentācijas**" | *Sedimentācija* = gravitational settling. The titration method is **nogulsnēšanas (precipitācijas) titrēšana**, e.g. argentometrija. | High |
| A10 | LEC P244, P248, P253; L25 p.1 | "ekvivalences punkts (reakcijas beigu punkts)" | **Two different things.** *Ekvivalences punkts* = theoretical point where n(titrant)·z = n(analyte)·z. *Titrēšanas beigu punkts* = what you **observe** (first persistent pale pink). Their difference is the titration (indicator) error — for KMnO₄ about one drop. L25 equates them in brackets; LEC P253 says "ekvivalences punkta" for what is observed. | High |
| A11 | LEC P253, P265; L25 p.2 | Pink must persist "**1–2 min**" / "**1 min**" / "pēc laika neizzūd" | Three different criteria for one lab. Common analytical practice is ≈ **30 s**. Do not pick silently: present the three, recommend following the lab instructor's value, record the question in the change log. | Verify |
| A12 | LEC P254 vs P097–098 and L21 | "neitrālā **vai bāziskā** vidē rodas MnO₂" | Contradicts the lecture's own half-reactions and the 2021 lab: **basic → MnO₄²⁻ (green)**, **neutral → MnO₂↓ (brown)**. (Strongly reducing/alkaline excess can carry manganate on to MnO₂, but the first product in base is manganate.) | Certain (internal) |
| A13 | LEC P071 (example 3) | "skābā vidē Cr₂O₇²⁻/2Cr³⁺ potenciāls ir lielāks … dihromāts spēj oksidēt hlorīdu" | True only when acidity is **high enough**; "skābā vidē" is not a number. With every other activity at 1 ([Cr₂O₇²⁻] = [Cr³⁺] = [Cl⁻] = 1, p(Cl₂) = 1 bar), E(Cr₂O₇²⁻) > E(Cl₂) requires **[H⁺] ≳ 1,65 M** (1,33 + (0,0592/6)·14·lg[H⁺] > 1,36). In dilute acid dichromate does *not* oxidise chloride appreciably — which is why dichromate titrations tolerate Cl⁻. Worked calculation = best "Nernst matters" example. Mark as [Ž]. | High (derived) |
| A14 | L20 p.4 (task 2); LEC self-test 2 | H₃PO₃ treated as **PO₃³⁻** | H₃PO₃ is a diprotic **molecule** (HP(O)(OH)₂); PO₃³⁻ is not the species present. Correct half-reaction: **H₃PO₃ + H₂O − 2e⁻ → H₃PO₄ + 2H⁺**. Net: 2MnO₄⁻ + 6H⁺ + 5H₃PO₃ → 2Mn²⁺ + 3H₂O + 5H₃PO₄ (balanced, verified). The source's version balances on paper — so a balance check will *not* catch this; only chemistry will. | High |
| A15 | L20/L21/LEC (sulfite in acid) | SO₃²⁻ written in H₂SO₄ solution | At pH < ~7 sulfite exists mainly as HSO₃⁻/SO₂·H₂O (H₂SO₃). Using SO₃²⁻ in acid is a **teaching simplification**; keep it (the course does) but state it once, and show E° (acid) +0,17/+0,20 V vs −0,93 V (base) as the same pH effect the course teaches for MnO₄⁻. Same logic: S²⁻ vs H₂S (LEC does this correctly). | High (nuance) |
| A16 | LEC §3.1 (task box) | M[(NH₄)₂Fe(SO₄)₂] = 284 g/mol | 284 g/mol is the **anhydrous** salt. Laboratory Mohr's salt is normally the **hexahydrate**, (NH₄)₂Fe(SO₄)₂·6H₂O, **M = 392,1 g/mol**. Whether the task means anhydrous is not stated. Make the hydrate explicit in any worked example. Same for FeSO₄ (151,9 anhydrous vs 278,0 heptahydrate) in L25. | High |
| A17 | LEC P292, P299, P303 | c = 0,13 M → m = 3,69 g | **Premature rounding.** Unrounded c = 0,024·11·5/(1·10) = 0,132 M → m = 0,132·0,1·284 = **3,75 g**. And with 2-significant-figure data the honest answer is **3,7 g**. Show: carry guard digits, round once at the end, state significant figures. | Certain |
| A18 | LEC self-test table (4 numeric tasks) | Printed answers | Recomputed: (1) 1,05 g and 0,067 mol/L ✔; (2) c(FeSO₄) = 0,0568 M ✔ but **8,63 g/L** with M = 151,91 (source 8,64); (3) 3,24 % ✔; (4) w(Fe) = **0,196 % → 0,20 %** (source 0,19 % truncates). Also task (1) asks for "**normālā** koncentrācija" but the printed answer is **molar**; normality would be 0,333 mol/L (eq). See T-set in §E. | Certain |
| A19 | LEC P294 | C_M = m / (m·V) | Second "m" must be **M** (molar mass): c = m/(M·V). L25 has it right. | Certain |
| A20 | LEC P276 | "oksidētājs V = 1,51 V" | Potential symbol is **E**; V is the unit (and volume elsewhere in the same formula). | Certain |
| A21 | LEC P039 | R = 8,314 J/mol, K | Unit is **J/(mol·K)**; a comma is not a unit separator. | Certain |
| A22 | LEC P044–045, P067–093, P224 | 0,0591 vs 0,059; "T = 25 °C" | 2,303·RT/F = **0,05916 V** at 298,15 K. Pick one constant (0,0592 or 0,059) for the whole master and say so; write T = 298 K (25 °C). | Certain |
| A23 | LEC P067, P070, P224 | E_{Cr₂/O₇²⁻ /2Cr³⁺}, E_{C₂/2Cl⁻}; "E = E⁰ + 0,059/n ∙ ⟧ log" | Typesetting slips: should read **E(Cr₂O₇²⁻/2Cr³⁺)**, **E(Cl₂/2Cl⁻)**; equation in P224 is split around "log". Retype all equations; do not copy. | Certain |
| A24 | LEC P005 | Oxidoreductase cofactors "Fe³⁺, Cu²⁺, Mn⁴⁺, Zn²⁺, Mo⁵⁺" | Zn²⁺ does **not change oxidation state** (structural / Lewis-acid role, e.g. alcohol dehydrogenase). Typical redox pairs: Fe³⁺/Fe²⁺, Cu²⁺/Cu⁺, Mn³⁺/Mn²⁺ (MnSOD), Mo(VI)/Mo(IV). Mn⁴⁺ appears in photosystem II's cluster; Mo(V) is an intermediate. Flag as simplification. | Verify |
| A25 | LEC P126 | "Ūdeņraža atomi labi šķīst **platīnā**" | H₂ **adsorbs** on (platinised) platinum — which is why Pt is the SHE electrode; bulk dissolution is the property of **palladium**. | Verify |
| A26 | LEC P029 | "ūdeņraža standartelektrods ([H⁺] = 1M)" | Defined by **activity** a(H⁺) = 1, p(H₂) = 1 bar, any temperature (E° ≡ 0 V). "1 M" is the practical approximation. | High |
| A27 | LEC P011–P012 | S⁴⁺ − 2e⁻ → S⁶⁺, O₂ + 4e⁻ → 2O²⁻ | Fine as **bookkeeping** (oxidation numbers), but SO₂/SO₃ are covalent: S⁴⁺ and O²⁻ are not real ions. State "formālais" once. | High |

### A-set: things confirmed **correct** — do not "fix" these

* All half-reactions and E° values in LEC §2.3–2.5 and table 2 **except A1–A5** (Mn: +1,51/+0,60/+0,56; Cr₂O₇²⁻ +1,33; Cl₂ +1,36; I₂ +0,54; Fe³⁺ +0,77; F₂ +2,87; H₂O₂ +1,78/+0,68 …).
* Every molecular and net ionic equation in L20, L25 and LEC §2.3–§3.1 (the 69-equation corpus in `tools/check_balance.py`) is atom- and charge-balanced, except A4 (A14 balances on paper but names a wrong species). L21 contains no equations.
* LEC self-test numbers 1,05 g / 0,067 mol/L, 0,0568 mol/L, 3,24 % (see A18 for rounding notes).
* Reasoning in LEC §2.2 examples 1–2 (direction by comparing E°) and the 6-step method in §2.6.
* Titration logic: n(KMnO₄)·z(KMnO₄) = n(analyte)·z(analyte), z(MnO₄⁻→Mn²⁺) = 5, z(Fe²⁺→Fe³⁺) = 1.

---

## B. Notation and form — the habits that cause student errors

| ID | Where | Seen | Use instead / teach |
| --- | --- | --- | --- |
| B1 | LEC (4+, +5, −3, 2−), L20 (`Mn+2SO₄²⁻`, `Cr₂⁺³(SO₄²⁻)₃`) | Oxidation state and ionic charge written the same way | **Charge**: number then sign, superscript — Fe³⁺, SO₄²⁻. **Oxidation state**: sign then number — +4, −2 (or Roman numerals in names: mangāns(VII)). "Mn⁷⁺" is not an ion that exists in MnO₄⁻. |
| B2 | L20 pp.1–2 | `5Na₂SO₄²⁻`, `K₂SO₄²⁻`, `2Mn⁺²SO₄²⁻`, `2KOH⁻`, `2Na₂MnO₄²⁻` | **Neutral formula units carry no charge.** Charges belong on ions in the ionic equation only. (Atoms balance regardless — the error is notational, but it hides charge conservation, the very check students must do.) |
| B3 | L20, LEC §3.1, L25 | `1│MnO₄⁻…  5│Fe²⁺…`; `1 2 Cr₂O₇²⁻`, `3 6 NO₂⁻`; "2 MnO₄⁻ + 8H⁺ + 5e⁻" | The number before **│** is the **multiplier** (LCM of electrons ÷ electrons in that half-reaction). "1 2" and "3 6" are an unreduced 2:6 → 1:3. A leading "2 MnO₄⁻" with "5e⁻" mixes multiplier and coefficient in one line. Show the multiplier column explicitly and **simplify by the common factor**. |
| B4 | LEC P280, §3.1 | `2x│MnO₄⁻ + 8H⁺ + 5Fe²⁺ → …` | The "2x" means "double this ionic equation to match Fe₂(SO₄)₃ in the molecular equation". Say so. |
| B5 | L20 p.1 (neutral) | `7H₂O → 8OH⁻ + 6H⁺ → 6H₂O + 2OH⁻` | An arrow chain used as arithmetic. Write the cancellation as a step: 6H⁺ + 6OH⁻ = 6H₂O, then cancel water. |
| B6 | LEC, L20 | Electrons on the **left with a minus**: `Fe²⁺ − e⁻ → Fe³⁺` | Valid shorthand, but the usual form is `Fe²⁺ → Fe³⁺ + e⁻`. Pick one and keep it; when showing both, show the equivalence (a frequent source of sign errors when adding half-reactions). Recommended for the master: electrons on the product side for oxidation, reactant side for reduction. |
| B7 | LEC | Mixed H⁺ and H₃O⁺ | H⁺ in water **is** H₃O⁺ (shorthand). If H₃O⁺ is written, count the extra water: O₂ + 4H₃O⁺ + 4e⁻ → **6**H₂O, not 2H₂O. Keep one convention per equation. |
| B8 | L25 p.2, L21, LEC | "0.0200 M" (point), "0,0200"; `ml`, `mL`; `mol/l`, `mol/L`, `M` | Latvian text → **decimal comma**. Recommended: **mL**, **L**, **mol/L** (M = shorthand for mol/L). A thin no-break space between number and unit (`0,0200 mol/L`). |
| B9 | LEC §3, L25 | **n** = electrons (Nernst) *and* **n** = amount of substance (titration); **C_M, cM, CM, c(X)**; **V** potential/volume | Two meanings of *n* in two chapters: introduce *z* (ekvivalences skaitlis, = electrons per formula unit in this reaction) for titration. Use **c(X)**, **V(X)**, **n(X)**, **M(X)**, **E**. |
| B10 | L20 line 1 | "α = 1" | α = degree of dissociation: "assume strong electrolytes fully dissociated". Define it on first use. |
| B11 | LEC P232 | ATP, ADP | Latvian abbreviations **ATF, ADF** (the earlier master uses ATF). Choose one; use the other in parentheses once. |
| B12 | all | "oks/red" | Acceptable *abbreviation* in this course; spell out *oksidēšanās-reducēšanās* in headings and the glossary; one spelling (see §E). |

---

## C. Typos and extraction artefacts in the sources (fix silently **only** in the master text; list in the change log)

| Source | Typo → correct |
| --- | --- |
| T13 (twice) | okdidēšanās → **oksidēšanās** |
| L21 keywords | pusrekcijas → **pusreakcijas** |
| L25 (twice) | elektnonu → **elektronu** |
| LEC self-test heading | vinādojumu → **vienādojumu** |
| LEC P005 | oksidēšanās-reducēšan**as** → oksidēšanās-reducēšan**ās** (**procesi**) |
| LEC table 2 header | "Oksidētāforma", "Standart-potenciālsE⁰" → *Oksidētā forma*, *Standartpotenciāls E°* |
| LEC (soft-hyphen leaks) | re-ducējoties, standart-potenciāls, oksidē-šanas, mito-hondrijā, ana-lizējamās, redu-cētāju → rejoin |
| LEC | "oksidēšanas pakāpe" **and** "oksidēšanās pakāpe" both used → see §E (term decision) |
| LEC reaction arrows | rendered as WMF pictures (`media/image1.wmf`) → absent from text extraction; **never** infer direction from the extracted text alone |

---

## D. Practice gaps — true, useful, absent from the sources (add as [Ž], clearly labelled)

| ID | Point |
| --- | --- |
| D1 | **KMnO₄ is not a primary standard** (contains MnO₂; decomposes in light; reacts with organics). Its concentration is *standardised* against H₂C₂O₄ or Na₂C₂O₄ — which is exactly the LEC self-test 1 task. (Oxalate titration is done warm, ~60–70 °C; the first drops decolourise slowly until Mn²⁺ forms and catalyses the reaction — **autocatalysis**.) |
| D2 | **Read the upper edge of the meniscus** for KMnO₄ (too dark to see the bottom). Rinse the burette with the titrant; expel the air bubble from the tip; record to 0,01 mL. |
| D3 | **Why only H₂SO₄**: HCl — Cl⁻ is oxidised by MnO₄⁻ (and Fe²⁺ "induces" it); HNO₃ is itself an oxidant. LEC P251 states the rule; the master adds the reason. |
| D4 | **Titre quality.** Discard a clear outlier; use **concordant** titres (spread ≤ 0,10 mL). L25 has 5 trials and says "vismaz 3". Averaging a bad titre propagates the error. |
| D5 | **The aliquot trap.** c(Fe²⁺) comes from the **10,00 mL** aliquot, but m(FeSO₄) is for the **100,0 mL flask**: use V = 0,1000 L and the right M (hydrate!). |
| D6 | **Pipette — text, name and picture disagree.** L25 p.2 lists "10,00 mL Mora pipete", but the drawing under that name is a one-mark **bulb (volumetric) pipette labelled "25 mL"** (**Certain**: look at the page). Separately, in German-derived usage a *Mohr pipette* is a **graduated** pipette, whereas a fixed aliquot is best taken with a volumetric pipette (**Verify** the Latvian lab usage). Do not rename equipment: draw a pipette that matches the text (10,00 mL, one mark), say which type the course means, and log the discrepancy. (Mohr's salt and the Mohr pipette are named after the same person, Karl Friedrich Mohr.) |
| D7 | **Fe²⁺ air-oxidises** to Fe³⁺ slowly; H₂SO₄ in the flask slows this. Prepare samples fresh. |
| D8 | **Direction ≠ speed.** ΔE > 0 says a reaction is *possible*; it says nothing about rate (kinetics). Related: **ΔG° = −zFΔE°** and lg K = z·ΔE°/0,0592. Example for MnO₄⁻ + 5Fe²⁺ + 8H⁺ (z = 5 electrons transferred): ΔE° = 1,51 − 0,77 = 0,74 V → lg K ≈ 62. Recompute with `python3` before printing any K. |
| D9 | **Comproportionation / disproportionation** (source mentions amphoteric redox behaviour but not these names): SO₂ + 2H₂S → 3S + 2H₂O (comproportionation); 3MnO₄²⁻ + 4H⁺ → 2MnO₄⁻ + MnO₂ + 2H₂O (disproportionation — why green manganate is unstable in neutral/acid). |
| D10 | **MnO₂ + HCl → Cl₂** (LEC P148): E°(MnO₂/Mn²⁺) ≈ 1,23 V < E°(Cl₂/Cl⁻) 1,36 V, yet it works in hot **concentrated** HCl: [H⁺]⁴ and [Cl⁻]² in the Nernst expressions plus Cl₂ leaving as gas. Pairs with A13 and A3 as the "E° is not the whole story" thread. |

---

## E. Terminology — Latvian choices the master must make once and apply everywhere

Decision rule: (1) the **course's own wording** (LEC/T13) is the default; (2) where the course is inconsistent or wrong, use the standard term and log the change; (3) for "Verify" rows consult **termini.lv (AkadTerm)** and the IUPAC Gold Book; if unreachable, keep the **majority usage in LEC** (count it) and mark "jāpārbauda". Never invent a Latvian term.

| Concept | Seen in sources | Use | Notes |
| --- | --- | --- | --- |
| oxidation (process) | oksidēšanās; "oksidēšana" | **oksidēšanās** (a species is oxidised) / **oksidēšana** (an agent oxidises something) | *Oksidētājs* → *oksidē* → pats *reducējas*. |
| oxidation number/state | **oksidēšanas pakāpe** (LEC P088, 100, 147, 148 …) and **oksidēšanās pakāpe** (P012, 013, 016, 083) | One form only. Standard: **oksidēšanas pakāpe** | Verify; count occurrences, log the decision. |
| redox couple | oks/red sistēma, oks/red pāris | **oksidēšanās-reducēšanās sistēma (oks/red sistēma)** = Ox/Red pāris | "Oksidētā forma / reducētā forma" ≠ "oksidētājs / reducētājs": the *form* is a member of a couple; the *agent* is a role in a reaction. |
| oxidising / reducing agent | oksidētājs, reducētājs | keep | An oxidising agent is **reduced**; a reducing agent is **oxidised** (never "KMnO₄ oksidējas"). |
| half-reaction | pusreakcija | **pusreakcija** (spelling!) | Method: **jonu-elektronu (pusreakciju) metode**. |
| ionic vs molecular equation | jonu vienādojums; summārais/galīgais vienādojums | **jonu vienādojums** (net ionic); **molekulārais (galīgais) vienādojums** | LEC step 6: "kombinējot reakcijas rezultātā radušos jonus ar tiem izejvielu joniem, kuri reakcijā nav pārveidojušies". Use that wording for spectator ions. |
| standard potential | standartpotenciāls, normālpotenciāls | **standartpotenciāls E°** (synonym *normālpotenciāls* once) | E° = reduction potential, 25 °C, activities 1. |
| electrode vs half-cell | "Par elektrodu sauc … iegremdētu metālu" | **elektrods** = the conductor; **oks/red sistēma / pusele­ments** = the whole Ox/Red system | The lecture blurs them. |
| electromotive force | EDS, elektrodzinējspēks | **elektrodzinējspēks (EDS)**; E_elements = E(katods) − E(anods) | "E = E₁ − E₂" in LEC: E₁ is the **larger** (reduction) potential. Say it. |
| Faraday | Faradeja skaitlis | **Faradeja konstante F** (≈ 96 485 C/mol; source rounds to 96 500) | Verify wording; mention both. |
| concentration | C_M, cM, CM, normālā | **molārā koncentrācija c(X), mol/L** | *Normālā (ekvivalenta) koncentrācija* is obsolete; if a task asks for it (A18) give both. |
| equivalence number | z, "stehiometrijas rādītājs" | **ekvivalences skaitlis z** (electrons per formula unit) | Different from *n* (amount of substance). |
| titration terms | titrants, analīze, analizējamais šķīdums | **titrants** (in the burette); **analīts / analizējamais šķīdums** (in the flask) | LEC uses *analīze* for the **sample** ("100 ml analīzes") — *analīze* is the process. |
| equivalence vs end point | "ekvivalences punkts (reakcijas beigu punkts)" | **ekvivalences punkts** (theory) ≠ **titrēšanas beigu punkts** (observed) | A10. |
| titrimetry | tilpuma analīze, volumetrija, titrimetrija | **tilpuma analīze (volumetrija)**; method = **titrimetrija** | |
| oxidimetry types | permanganatometrija, jodometrija | **permanganatometrija** (KMnO₄), **jodometrija / jodimetrija** (distinguish!), **dihromatometrija** | A8. |
| ions | permanganāts / manganāts; hromāts / dihromāts; sulfīds / sulfīts / sulfāts; nitrīts / nitrāts; tiosulfāts / tetrationāts | formulas and charges: MnO₄⁻ / MnO₄²⁻; CrO₄²⁻ / Cr₂O₇²⁻; S²⁻ / SO₃²⁻ / SO₄²⁻; NO₂⁻ / NO₃⁻; S₂O₃²⁻ / S₄O₆²⁻ | These pairs are the commonest slip. Provide a **"vārds → formula → oksidēšanas pakāpe"** table. |
| hydronium | ūdeņraža jons H⁺; oksonija jons H₃O⁺ | **H⁺ (aq)** in chemistry equations; **H₃O⁺** only if water is counted | B7. |
| enzyme | enzīms / ferments | **enzīms** (with *ferments* in brackets once); **oksidoreduktāze** | |
| ATP | ATP | **ATF** (ATP in brackets once) | B11. |
| Mohr | Mora pipete, Mora sāls | keep **Mora**; add that it is Mohr | D6. |
| glassware | birete, Erlenmeijera kolba, mērkolba, mērcilindrs, pipešu uzpildāmais | keep source names | Mērcilindrs is deliberately imprecise: acid is in excess, so its exact volume does not matter. |
| "O2 is the oxidant" in biochemistry | skābeklis | oxidant only in **water** (LEC P077): in a hydrophobic haem pocket O₂ is carried, not used | A good misconception card. |

---

## F. Misconceptions to build cards for (from the above, in priority order)

1. "The substance that is oxidised is the oxidiser." (Oxidant is reduced.)
2. Oxidation state = charge = valence. (Three different things; SO₂ has S +4 but no S⁴⁺ ion.)
3. Balancing atoms but not **charge**; or balancing charge but forgetting **electrons cancel**.
4. Wrong order of balancing: (1) atoms other than O/H, (2) O with H₂O, (3) H with H⁺, (4) charge with e⁻, (5) basic medium: neutralise H⁺ with OH⁻.
5. Adding H⁺ in **basic** solution (or OH⁻ in acid) without conversion.
6. Using **E° as if it were E** (pH, concentration, p(gas) ignored) — A13, A3, D10.
7. **Inverting the Nernst ratio** (it is [Ox]/[Red], Ox on top, for the reduction written Ox + ne⁻ → Red).
8. Treating EMF as the sum of two potentials instead of **E(cathode) − E(anode)**; flipping the sign of E° when reversing a half-reaction is correct, but **multiplying** E° by the stoichiometric multiplier is **wrong** (E° is intensive; ΔG° is extensive).
9. Mixing **E°** (pH 0) and **E°′** (pH 7) — A5.
10. Thinking "ΔE > 0 ⇒ it happens quickly".
11. Mn in three media: remembering colours but not **why** (electrons accepted 5/3/1 and the Nernst [H⁺]⁸ term).
12. HCl or HNO₃ to acidify a permanganate titration. (Only dilute H₂SO₄.)
13. Equivalence point = end point (A10).
14. Reading the burette as "what is left" and subtracting from 25 mL — L25 warns about exactly this.
15. Mass from the **aliquot** volume instead of the flask volume; wrong hydrate; premature rounding (A17).
16. Writing a species that cannot exist at that pH (PO₃³⁻, SO₃²⁻, S²⁻ in acid) — A14, A15.
17. Charges on neutral formula units in molecular equations (B2).
18. Confusing manganate (MnO₄²⁻, green) with permanganate (MnO₄⁻, violet), and dichromate with chromate.
