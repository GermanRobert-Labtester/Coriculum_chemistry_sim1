# SOURCE_LEDGER – errata, terminology, verified numbers, mistake seeds

Topic 1 "Šķīdumi un ķīmiskās reakcijas" · compiled 2026-10-31 from the five PDFs in this folder.
Read `AGENTS.md` first. This file is the data the master HTML draws on; it is not the deliverable.

**Source IDs** (page refs are printed page numbers; `s.` = slide number)

| ID | File | Pages |
| --- | --- | --- |
| A | `1_Neorganiskā ķīmija konspekts atkārtošanai_2024.pdf` | 16 |
| B | `1_SEM_MCh_LV_Skid_un_reakcijas_2025.pdf` (footer says `…_2021`) | 4 |
| C | `1_Temata apraksts 2020.pdf` | 1 |
| D | `I_temats_TEORIJA_Final_m.pdf` | 21 |
| E | `Kimija_viss-2024 - Prezentacija.pdf` | 58 slides |

**How to read the Basis column.** `S` = provable from the sources alone (an unbalanced equation, an
arithmetic slip, two pages disagreeing). `X` = the correction relies on knowledge from outside the
PDFs. An `X` row is a strong lead, not a citation: check it against IUPAC Gold Book / CRC Handbook /
a clinical reference when you have access, otherwise print it with the label *[jāpārbauda]*.
Never present an `X` correction as if the lecturer had said it.

**Kind:** `ERR` wrong · `INC` two places disagree · `CONV` simplification or convention that misleads ·
`TYPO` print or extraction slip.

---

## 1. Errata ledger

### 1.1 Constants, units, atomic structure

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E01 | A p.2, A p.16, D | N_A = 6,023·10²³ (A p.2), 6,022·10²³ (A p.16), 6,02·10²³ (D) | One value everywhere. Exact since 2019: 6,022 140 76·10²³ mol⁻¹. Use 6,022·10²³. | INC | S+X |
| E02 | A p.16 | SI table: kg = Pt-Ir prototype; K = 1/273,16 of water triple point; A = force between wires; mol = atoms in 12 g ¹²C | All four were redefined on 20 May 2019 via fixed h, k, e, N_A. Show the table with current definitions and mark the old ones as historical. | ERR (outdated) | X |
| E03 | A p.16 | "1 mol = 1000 mmol = 1·10⁻⁶ µmol" | 1 mol = 10⁶ µmol (1 µmol = 10⁻⁶ mol). | ERR | S |
| E04 | A p.16 | Caesium written "Cz"; luminous intensity symbol "I", name "gaismas intensitāte" | Cs. Luminous intensity: I_v. Keep the lecture's Latvian name but show the symbol. | TYPO | S+X |
| E05 | A p.2 | "Atommasas mērvienība … ir g/mol. Tātad ¹²C: A = 12 g/mol" | Three different quantities share one letter: relative atomic mass A_r (dimensionless), molar mass M (g/mol), mass number A (integer count of nucleons). | ERR | S |
| E06 | A p.2, E s.4 | "Pēc relatīvās atommasas, izmantojot A = N + Z, var aprēķināt neitronu skaitu" | A here is the mass number, not A_r. Cl has A_r = 35,45 and no single N. N = A − Z holds per isotope. | ERR | S+X |
| E07 | A p.2 | "Tritijs dabā nav sastopams" | Traces occur naturally (cosmic rays); bulk is made artificially. Radioactive, t½ ≈ 12,3 gadi. | CONV | X |
| E08 | A p.1 | "16 vertikālās rindas"; groups 1.A–8.A and 1.B–8.B | That is the CAS/old-US 8A+8B scheme. IUPAC numbers 18 groups; VIIIB is three columns. Show both numberings, say which one the course uses. | CONV | X |
### 1.2 Bonding, electron shells and the periodic table

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E09 | A p.1–2, E s.9 | REN "kā elektrontieksmes un jonizācijas enerģijas pussumma" | That is Mulliken's definition. The tabulated REN scale (F = 3,98) is Pauling's. Say which, once. | CONV | X |
| E10 | A p.3, E s.22, 27 | Ionic if ΔREN ≥ 2, polar covalent if < 2 | The course's own MgCl₂ example (E s.25) has ΔREN = 1,85 < 2; Al₂S₃ = 0,97; HF = 1,78; C–H = 0,35. Common cut-offs: 0,4 / 1,7 (Pauling). Present bonding as a continuum; every answer states the criterion used. | INC | S+X |
| E11 | A p.4 | The valence-bond / MO paragraph appears twice | Print once. | TYPO | S |
| E12 | E s.30 | "π saites enerģija ≈ 10 reizes mazāka par σ" | For C–C: C–C 347, C=C 614, C≡C 839 kJ/mol → π ≈ 65–77 % of σ. Weaker, not ten times weaker. | ERR | X |
| E13 | A p.4, E s.34 | H-bond is a bond between an F/O/N atom and "ūdeņraža atoma kodolu (protonu)"; "starpmolekulārās saites" | The H is covalently bound and carries δ+; it interacts with a lone pair on another F/O/N. It is an intermolecular (or intramolecular) interaction, ≈ 5–40 kJ/mol, far weaker than a covalent bond. CH₄ has none. | ERR / CONV | X |
| E14 | A p.4, E s.32 | Metallic bond text: "neitrāli atomi un katjoni", "protonu lādiņi summējoties" | Model: lattice of cations in a delocalised electron sea. Keep the lecture's term "elektronu gāze", drop the muddled charge arithmetic. | CONV | X |
| E15 | A p.9 vs E s.36 | A: "atomāru kristālrežģi" = diamond, Si, B. E: "atomāru uzbūvi" = noble gases, "nemolekulāru" = graphite, diamond | One word, two meanings. Use "atomu (kovalentais) kristālrežģis" for diamond/Si and keep "atomārs" for monoatomic species. | INC | S |
| E16 | E s.14–15 | "Enerģijas līmenis ir aprēķināms pēc formulas 2n²"; "līmeņu skaits sakrīt ar grupas perioda numuru" | 2n² is the maximum number of electrons on level n (2, 8, 18, 32). "Grupas perioda numuru" → perioda numuru. Level 3 does not fill before 4s (E s.16 shows the order). | ERR / TYPO | S |

### 1.3 Mixtures, dispersed systems, solutions

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E17 | A p.5, E s.50 | True solutions < 1 nm; colloids 1–100 nm; coarse > 1000 nm | 100–1000 nm belongs to nothing. Usual textbook split: coarse > 100 nm. IUPAC lets colloids run to ≈ 1 µm. Show a size axis, state the boundary used. | INC | S+X |
| E18 | A p.6 | Soluble > 10 g; slightly 0,1–10 g; "practically insoluble" < 0,01 g per 100 g water | 0,01–0,1 g is undefined. Fix the class edges, mark it as a fix. | INC | S |
| E19 | D p.7 vs D p.3 | "Šķīdums: šķidrums, ko iegūst, sajaucot cietu vai gāzveida vielu ar šķīdinātāju" | D p.3 itself lists gaseous, liquid and solid solutions, and liquid–liquid solutions. Use the broad definition. | INC | S |
| E20 | D p.4 | NaCl in benzene = colloidal solution; table lists air and tissues as dispersed systems | The NaCl case is a legacy argument (von Weimarn) that colloidal is a state, not a substance class. In practice NaCl is insoluble in benzene. Keep as principle only. Air is a true gas mixture; tissues as "solidosoli" is the course's own, contested, classification. | CONV | X |
| E21 | D p.5 | Artificial kidney = electrodialysis | Haemodialysis is dialysis: diffusion down a concentration gradient plus ultrafiltration through a semipermeable membrane. Electrodialysis moves ions in an electric field (desalination, the example D gives next to it). | ERR | X |
| E22 | D p.8 | "Gāzu šķīdība, paaugstinot T, vienmēr samazinās" | "Parasti", in water. H₂, He, Ne pass through a minimum (≈ 30–60 °C); in organic solvents it often rises. | ERR (overstated) | X |
| E23 | D p.10 | "BaCl·2H₂O" | BaCl₂·2H₂O. | TYPO | S |
| E24 | D p.9–10 | "hidrāti" for both solvation shells and CuSO₄·5H₂O | Two things: hidratācija/solvatācija (shell) vs kristālhidrāts (in the lattice). | CONV | S |

### 1.4 Electrolytes, acids, bases, pH, hydrolysis

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E25 | A p.7, E s.54 vs D p.11 | Strong α > 0,7, weak α < 0,1 vs strong α > 30 %, medium 3–30 %, weak < 3 %; D also says "α < 30 % → vājš" then "3–30 % vidēji stiprs" | Two incompatible schemes and one self-contradiction. α depends on concentration and temperature. Prefer K_a / K_b for strength. Show both schemes, flag the contradiction. | INC | S |
| E26 | A p.6 vs p.11, E s.40 | Arrhenius 1887 vs 1886 | Pick one. Thesis 1884; dissociation theory published 1887. | INC | S+X |
| E27 | B #3, A p.7, D p.11, E s.41 | "NH₄OH" and "NH₃·H₂O" used interchangeably | No discrete NH₄OH is known. Write NH₃(aq) or NH₃·H₂O; NH₃ + H₂O ⇌ NH₄⁺ + OH⁻, K_b = 1,8·10⁻⁵. | CONV | X |
| E28 | A p.7, E s.54 | "Vājo elektrolītu šķīdumi … sāļu anjoni HPO₄²⁻, HCO₃⁻" | These are amphiprotic ions, not solutions. HCO₃⁻ is more base than acid in water: NaHCO₃(aq) pH ≈ 8,3. | CONV | X |
| E29 | A p.7, E s.56 | pH = −lg[H₃O⁺] then [H⁺] = 10^−pH; [H⁺] = [OH⁻] = 10⁻⁷ stated without a temperature | H⁺ and H₃O⁺ are one species written two ways. pH is strictly −lg a(H⁺). Neutral = 7,00 only at 25 °C (K_w = 10⁻¹⁴; E s.56 gives K = 1,8·10⁻¹⁶ and [H₂O] = 55,3 mol/L). | CONV | S+X |
| E30 | D p.11 | H₃BO₃ listed as an ordinary weak acid electrolyte | B(OH)₃ + 2 H₂O ⇌ B(OH)₄⁻ + H₃O⁺: a Lewis acid, not a proton donor. Keep it as a nuance. | CONV | X |
| E31 | A p.11, E s.40 | Acids counted by "ūdeņraža atomu skaits, kas spēj aizvietoties" | Correct definition, easy to misread: CH₃COOH has four H and is monobasic; H₃PO₃ has three and is dibasic. Show the formula with the acidic H marked. | CONV | S |
| E32 | A p.8 | Weak acid + weak base salt: "hidrolizējas katjons un anjons … pH = 7" | pH ≈ 7 + ½(pK_a − pK_b). NH₄CH₃COO ≈ 7 by coincidence; NH₄F acidic; (NH₄)₂CO₃ basic. Al₂S₃ hydrolyses completely (A p.9 scheme). | ERR | S+X |
| E33 | A p.8 | Zn²⁺ + 2Cl⁻ + H₂O ⇌ Zn(OH)₂ + H⁺ + Cl⁻ and Zn²⁺ + H₂O ⇌ Zn(OH)₂ + H⁺ | Neither balances (H and O). First step: Zn²⁺ + H₂O ⇌ ZnOH⁺ + H⁺; overall Zn²⁺ + 2 H₂O ⇌ Zn(OH)₂ + 2 H⁺. | ERR | S |

### 1.5 Oxides, bases, acids, salts, equations

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E34 | A p.10 | "MnO₃ – mangāna(VI) oksīds" among acidic oxides | Not a standard, isolable example. Use Mn₂O₇ (VII), MnO₂, MnO. | CONV | X |
| E35 | A p.10 | Fe₂O₃ among amphoteric oxides | Predominantly basic, weakly amphoteric on fusion. Mark as conditional. | CONV | X |
| E36 | A p.10–12 | (a) Na₂O + HCl → 2NaCl + H₂O. (b) SO₃ + NaOH → Na₂SO₄ + H₂O. (c) NaOH + CO₂ → Na₂CO₃ + H₂O. (d) 2Al(OH)₃ + 2HCl → Al₂(SO₄)₃ + 3H₂O. (e) Ba(OH)₂ + MgSO₄ → BaSO₄↓ + Mg(OH)₂; H₂SO₄ + BaCl₂ → BaSO₄ + 2HCl | (a) needs 2HCl. (b) 2NaOH. (c) 2NaOH. (d) 2Al(OH)₃ + 3H₂SO₄ → Al₂(SO₄)₃ + 6H₂O. (e) both Mg(OH)₂ and BaSO₄ carry ↓. | ERR | S |
| E37 | A p.13, D p.16 | "Fe + CuSO → FeSO + Cu↓" (in print, both files) | Fe + CuSO₄ → FeSO₄ + Cu↓. The copper deposits as metal on the iron. | TYPO | S |
| E38 | A p.15 | "2NaOH + H₂SO₄²⁻ → 2H₂O + Na₂SO₄" | The acid carries no charge: H₂SO₄. | TYPO | S |
| E39 | A p.12 | "2NaCl + H₂SO₄ → Na₂SO₄ + 2HCl"; "Aktīvākās skābes reaģē ar sāļiem" | Needs solid NaCl, conc. H₂SO₄, heat: a non-volatile acid displaces a volatile one. Not an aqueous exchange. Say so. | CONV | X |
| E40 | D p.15 | Zn(OH)₂↓ + NaOH → Na₂[Zn(OH)₄] | Zn(OH)₂ + 2NaOH → Na₂[Zn(OH)₄]. The ionic equation printed below it is right. | ERR | S |
| E41 | D p.15–16 | Section headings "Reakcijas mehānisms – savienošanās / aizvietošanas / sadalīšanas / apmaiņas" | Those are reaction types. A mechanism is the stepwise pathway of bond breaking and forming. | ERR (term) | S+X |
| E42 | D p.17 | Gas-forming exchange: "H₂S, HF, HCl, HI, NH₃" | Omits the most common cases, CO₂ (via H₂CO₃) and SO₂ (via H₂SO₃). B #7 uses K₂SO₃ + HCl. | CONV | S |

### 1.6 Redox, thermochemistry, potentials

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E43 | A p.13, p.14, E s.45 | "Mg⁺²O⁻²", "Mn⁺⁷", "O⁻"; "oksidēšanās pakāpe" and "oksidēšanas pakāpe" both used in A p.14 | Ion charge: Mg²⁺ (number, then sign). Oxidation state: +2 or (II). One spelling of the term. | CONV / INC | S+X |
| E44 | A p.14 | "H₂ – 2e⁻ =→ 2H⁺" | H₂ − 2e⁻ → 2H⁺. | TYPO | S |
| E45 | A p.14, E s.45 | O "parasti −2", H "parasti +1" | Say when not: peroxides O = −1, OF₂ O = +2, metal hydrides H = −1. | CONV | X |
| E46 | A p.13 | C + O₂ → CO₂ + 409 kJ/mol; C₃H₈ + 5O₂ → 3CO₂ + 4H₂O(g) + 2200; C₂H₅OH + 3O₂ → 2CO₂ + 3H₂O(g) + 1292; "+Q / −Q" | Literature: CO₂ 393,5. Propane 2043 with H₂O(g), 2220 with H₂O(l). Ethanol 1235 with H₂O(g), 1367 with H₂O(l). Methane 802 with H₂O(g) is right. State of water must match the number. +Q has the opposite sign to ΔH. | ERR / CONV | X |
| E47 | E s.48 | Standard potentials: Br₂/2Br⁻ +0,96 V; O₂/H₂O +1,21865 V; PbO₂/Pb²⁺ +1,80 V; "NH₄OH" in the NO₃⁻ row | Literature ≈ +1,07 V; +1,229 V; +1,455 V. +0,96 V is the NO₃⁻/NO value. Verify before reproducing any row; use reduction potentials. | ERR | X |

### 1.7 Organism and medical context (all in D)

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E48 | D p.2 | "pH 7,32–7,45, 7,4 – neitrāla vide" | Arterial blood 7,35–7,45 is slightly alkaline. Neutral water = 7,00 at 25 °C and ≈ 6,8 at 37 °C. (7,32 may be a venous value.) | ERR | S+X |
| E49 | D p.2 | Stabilised parameters: "asins gāzu sastāvs (skābeklis, slāpeklis)" | O₂ and CO₂ (p_O₂, p_CO₂). N₂ is not a regulated blood gas. | ERR | X |
| E50 | D p.2 | "temperatūra 36,5–38,6 °C" | The upper end is a fever. Typical core temperature ≈ 36,1–37,5 °C. | ERR | X |
| E51 | D p.1 | "Cilvēka ķermenī vairāk nekā 70 % šķidruma"; "bezšūnu šķidrā fāze … šūnu citoplazmas šķidrums"; "iekšējās vides tilpums ≈ 14,5 L" | Adult total body water ≈ 50–60 %; > 70 % is an infant figure. Cytoplasm is intracellular, so cannot sit inside a "bezšūnu" phase. 14,5 L fits extracellular fluid only, not total body water (≈ 42 L). | ERR (logic) | S+X |
| E52 | D p.2 | "Mononukleāro (mono – viens; nucleum – šūna)" | nucleus = kodols. | ERR | X |
| E53 | D p.3 | "Hiperaldosteronisms (Kušinga sindroms)"; "Diabetes inspidus"; "preperāti" | Primary hyperaldosteronism = Konna sindroms; Kušinga = hiperkortizolisms. insipidus. preparāti. | ERR / TYPO | X |
| E54 | D p.12 | Proteins, carbohydrates, fats "kopā ar nukleīnskābēm ir organisma enerģijas avots"; 55–60 / 20–25 / 15–20 % | Nucleic acids store and transmit information; they are not a fuel. The percentages are dietary guideline ranges, not constants. | ERR / CONV | X |
| E55 | D p.13 | "Hlorofils katalizēts bioķīmisks process" | Chlorophyll absorbs light; the CO₂ fixation is enzyme-catalysed (Rubisco). | CONV | X |
| E56 | D p.13 | "Visi lipīdi ir ūdenī nešķīstoši … vitamīni K, E, D, A" | Amphiphilic lipids (phospholipids) form micelles and bilayers. The fat-soluble vitamins are lipophilic, not lipids in the strict sense. | CONV | X |
| E57 | D p.15 | Krebs cycle "ķīmiskā enerģija pārnesta uz … ATP" | The cycle yields NADH, FADH₂ and one GTP/ATP; most ATP comes from oxidative phosphorylation. | CONV | X |

### 1.8 Stoichiometry text and provenance

| ID | Where | Source says | Correct / how to handle | Kind | Basis |
| --- | --- | --- | --- | --- | --- |
| E58 | D p.18 | "Aprēķinot n_B, n_A jādala ar stehiometrijas rādītāju b" | The formula printed above is n_B = n_A · b / a: divide by a, multiply by b. | ERR | S |
| E59 | D p.19–20 | "m_Al / V₀,O₂ = 4 mol·26,98154 / 4 mol·26,98154"; "101,061 g/mol"; "M_H₂SO₄ = 23+16+1 = 40"; ratio "2,20" | 4·M_Al : 3·V₀. 101,961 (Al₂O₃). That line is M_NaOH. 0,225 / 0,102 = 2,21. | TYPO | S |
| E60 | D p.19–20 | V₀ = 22,4 L/mol "normālos apstākļos" | State the conditions: 0 °C and 101,325 kPa → 22,414 L/mol. IUPAC STP (100 kPa) → 22,711; SATP (25 °C, 100 kPa) → 24,79 L/mol. 100 g Al needs 62,3 L O₂ at 0 °C / 101,325 kPa, 68,9 L at SATP. | CONV | S+X |
| E61 | B, C | B is named …2025 but its footer says …2021; C is "2020" and describes a Zoom course | Versions differ. The master cites the file name as received and does not claim a year. | INC | S |

---

## 2. Terminology (Latvian)

Rule: where the PDFs use two spellings, the master picks one, uses it everywhere, and records the
choice in the changelog. Rows marked **[apstiprināt]** are choices you cannot verify from the PDFs;
list them in the final report for the user to confirm instead of deciding silently.

| Use | Avoid / collision | Note |
| --- | --- | --- |
| vielas daudzums *n* (mol) | "molu skaits"; "mols" as a quantity | Quantity n, unit mol. |
| relatīvā atommasa *A*ᵣ · molmasa *M* (g/mol) · masas skaitlis *A* | one letter for all three; "atommasas mērvienība g/mol" (E05) | Three quantities, three names. |
| formulvienība (ionic compounds) | "NaCl molekula" | Ionic crystals have no molecules. B #1 asks atom / ion / molecule. |
| NH₃·H₂O, NH₃(aq) | NH₄OH, "amonija hidroksīds" (E27) | |
| oksidēšanas pakāpe **[apstiprināt]** | "oksidēšanās pakāpe" mixed in (E43) | Oxidation state ≠ ion charge ≠ valence. |
| oksidētājs (reducējas) · reducētājs (oksidējas) | "oksidētājs oksidējas" | The agent is reduced, not oxidised. |
| normālie apstākļi, with the numbers (E60) | "n.a." with bare 22,4 | |
| reakcijas veids / klasifikācija | "reakcijas mehānisms" for types (E41) | |
| piesātināts · nepiesātināts · pārsātināts (vs solubility) | = koncentrēts / atšķaidīts | Different axes: how much solute vs. how close to solubility. |
| masas daļa *w*, molārā koncentrācija *c*(X) in mol/L, blīvums ρ | "CM", "procentuālā koncentrācija", normalitāte | Normality is not used in these sources; do not introduce it. |
| hidratācija / solvatācija · kristālhidrāts · hidrolīze | "hidrāts" for all (E24) | Three different things. |
| elektrolītiskā disociācija | – | Course term for both ionic dissociation (NaCl) and ionisation by water (HCl). Mention the difference in a depth block. |
| bāze · sārms (ūdenī šķīstoša bāze) · hidroksīds (savienojumu klase) | using the three as synonyms | NH₃ is a base with no OH group. |
| bāziskais oksīds / bāziskā vide / bāziskais sāls | assuming they share a meaning | Three different uses of "bāzisks". The course says "sārmains" for pH > 7 in D p.20. |
| skābais sāls (contains replaceable H) | "skābs šķīdums" | NaHCO₃(aq) is alkaline (E28). |
| skābes atlikums | – | Keep (A, E). It means the anion. |
| amfotērs (oxide, hydroxide) · amfolīts / amfiprotisks jons **[apstiprināt]** | one word for both | Al₂O₃, Zn(OH)₂ vs HCO₃⁻, H₂PO₄⁻, HPO₄²⁻. |
| ūdeņraža saite, but described as starpmolekulāra mijiedarbība (E13) | "starpmolekulārā saite" | |
| atomu (kovalentais) kristālrežģis **[apstiprināt]** | "atomārs" for diamond (E15) | |
| hlorūdeņradis (gāze) · sālsskābe (HCl šķīdums) | | D p.10 uses both correctly. |
| jonu lādiņš Fe³⁺ (skaitlis, zīme) vs oksidēšanas pakāpe +3 / (III) | "Fe⁺³" for an ion | |
| decimal comma in running text: 0,7; thin no-break space before units: 22,4 L/mol; "L" not "l"; "−" (U+2212) for minus and charges; "pH" upright | sources mix "7.32" and "7,4", "l" and "L", hyphen-minus | |
| symbols: *n*, *m*, *M*, *V*, *c*, ρ, α, *K* in italic; units, element symbols and formulas upright | | |
| English equivalents in the glossary (for reading international literature) | etymology unless you can verify it (see `MASTER_PROMPT.md` §6) | |

### T01 decision note (2026-11-06)

Recorded in `build/terms.py`. No row below was approved by a named editor. IUPAC Gold Book text was not read (HTTP 403), so an IUPAC spelling for the open rows stays [UNVERIFIED].

Settled from the course files, and used in teaching prose: *molmasa* *M* in g/mol is not *relatīvā atommasa* and not *masas skaitlis* (E05, A p.2); *formulvienība* for an ionic solid (B #1, M02); *bāze*, *sārms* and *hidroksīds* are three names (A p.11; NH₃ has no OH); pH > 7 is *sārmains* (D p.20); *reakcijas veids* is not *reakcijas mehānisms* (E41, D p.15–16). Quoted source wording stays inside the correction.

Still open, approver unset: the three table rows marked **[apstiprināt]**. Greek letters and formula markup are a notation exception. They do not relax the Latvian prose bans.

---

## 3. Verified numbers (recomputed 2026-10-31 in Python; recompute again in the build script)

Atomic masses used: H 1,008 · C 12,011 · O 15,999 · Na 22,990 · Mg 24,305 · Al 26,982 · S 32,06 · K 39,098.
M(NaOH) = 40,00 · M(KOH) = 56,11 · M(H₂SO₄) = 98,07 · M(Al₂O₃) = 101,96 g/mol.

| Item | Result |
| --- | --- |
| B #7 | Fe + CuCl₂ → Cu + FeCl₂ · 3Ca + N₂ → Ca₃N₂ · Ba(NO₃)₂ + Na₂SO₄ → BaSO₄ + 2NaNO₃ · Al(OH)₃ + 3HCl → AlCl₃ + 3H₂O · 2HCl + K₂SO₃ → 2KCl + H₂O + SO₂ · 2Na + 2H₂O → 2NaOH + H₂ · C₃H₈ + 5O₂ → 3CO₂ + 4H₂O |
| B #8 | Ions per formula unit: NaCl 2, Na₂SO₄ 3, Na₃PO₄ 4, AlCl₃ 4, Al₂(SO₄)₃ **5** → largest. Assumes full dissociation, no ion pairing. |
| B #9 | 3 mol K₃PO₄ → 9 mol K⁺, 3 mol PO₄³⁻ |
| B #10 | 2,5 mol Ca(OH)₂ |
| B #11 | 4 mol H₃PO₄ |
| B #12 | 1 mol NaCl; 1 mol HCl left over (NaOH is limiting) |
| B #13 | n(KOH) = 0,1604 mol, n(H₂SO₄) = 0,0918 mol; need n(KOH)/n(acid) = 2, have 1,75 → KOH limiting. K₂SO₄ = 0,0802 mol, H₂SO₄ left = 0,0116 mol → **acidic**. Comparing grams (9 g = 9 g) gives the wrong picture. |
| B #14 | 48 g of 22 % NaOH: 10,56 g NaOH = 0,264 mol; V = 48 / 1,25 = 38,4 mL → c = **6,88 mol/L** |
| B #15 | 48 mL: 60 g solution, 13,2 g NaOH = 0,330 mol → c = **6,88 mol/L** (same; c = 10·w%·ρ / M, independent of the volume taken) |
| D p.19 | 100 g Al: n = 3,706 mol; O₂ 2,78 mol = 62,3 L (0 °C, 101,325 kPa); Al₂O₃ 1,853 mol = 188,9 g |
| D p.20 | 10 g H₂SO₄ = 0,102 mol, 9 g NaOH = 0,225 mol; ratio 2,21 > 2 → NaOH in excess (0,021 mol) → alkaline |
| Neutral pH at 37 °C | 6,81 (K_w ≈ 2,4·10⁻¹⁴) |
| 0,9 % NaCl | 154 mmol/L NaCl ≈ 308 mOsm/L · 5 % glucose = 278 mmol/L |
| ΔREN (Pauling) | Li–F 3,00 · Na–Cl 2,23 · Mg–Cl 1,85 · H–F 1,78 · H–O 1,24 · Al–S 0,97 · C–O 0,89 · C–H 0,35 |

**Judgement items (no single right answer; show the reasoning, not a verdict):**
B #1 O and Cl as free atoms (reactive radicals, not stable species) · NO₂ as an odd-electron molecule ·
B #2 Al(OH)₃ and Al₂O₃ are amphoteric · NaHCO₃ and Na₂HPO₄ are acid salts with alkaline solutions ·
B #3 Cu conducts but is not an electrolyte; ZnO, CaO, NO₂, Cl₂ either do not dissolve or react with
water, so the solution conducts because of a product · B #5 Al₂S₃ and CH₄ depend on the ΔREN
criterion (E10); CO₂ has polar bonds in a nonpolar molecule · B #6 "2NaOH + CO₂" is an exchange
(neutralisation via H₂CO₃) that the four-type scheme fits awkwardly.

---

## 4. Mistake seeds

One line each. The master expands every seed into: the wrong move, why it feels right, the right move,
a mini check. Mark each `[avots]` (the sources cover it) or `[papildinājums]` (pedagogical addition).

| ID | Mistake | Hook |
| --- | --- | --- |
| M01 | Changing subscripts instead of coefficients to balance | B #7 [avots] |
| M02 | "NaCl molecule"; counting a formula unit as a molecule | B #1 [avots] |
| M03 | Forgetting how many ions one formula unit gives (Al₂(SO₄)₃ → 5) | B #8, #9 [avots] |
| M04 | Comparing grams instead of moles; picking the limiting reagent by mass | B #13 [avots] |
| M05 | Treating "48 g" and "48 mL" of a solution as the same; using volume of solvent for molarity | B #14, #15 [avots] |
| M06 | "Acid salt ⇒ acidic solution" | B #2, E28 [avots] |
| M07 | Forgetting amphoteric hydroxides dissolve in excess alkali | B #2, D p.15 [avots] |
| M08 | Calling any conductor, or any substance that reacts with water, an electrolyte | B #3 [avots] |
| M09 | Equating strong electrolyte, soluble and concentrated | A p.7, D p.11 [avots] |
| M10 | Polar bonds ⇒ polar molecule (CO₂) | B #5 [papildinājums] |
| M11 | Ionic vs covalent as a yes/no switch; applying "typical metal + nonmetal" without a criterion | E10 [avots] |
| M12 | Hydrogen bond drawn inside a molecule, or from any H (CH₄) | E13 [papildinājums] |
| M13 | Mixing oxidation state, ion charge and valence; O always −2, H always +1 | A p.14 [avots] |
| M14 | "The oxidiser gets oxidised" | A p.14 [avots] |
| M15 | Treating redox as a fifth type beside the four. Displacement is always redox, exchange never, combination and decomposition sometimes | A p.13 [papildinājums] |
| M16 | Writing a reaction for an exchange with no precipitate, gas or weak electrolyte (all ions stay) | D p.16 [avots] |
| M17 | Net ionic equations: splitting insoluble salts, weak electrolytes, gases, water; unbalanced charge | D p.16–17 [avots] |
| M18 | Reading the solubility table as "dissolves / doesn't" with no temperature or no "maz šķīst" | B #4, D p.6 [avots] |
| M19 | pH: assuming pH 7 is neutral at every temperature; a ten-fold dilution of an acid taking pH past 7 | E29 [papildinājums] |
| M20 | Blood pH 7,4 called neutral | E48 [avots] |
| M21 | Saturated = concentrated; supersaturated treated as stable | D p.9 [avots] |
| M22 | Dilution raises α but lowers [ion]; reading α up as "stronger" | A p.7, D p.10 [avots] |
| M23 | Hydrolysis: NaCl hydrolyses; "weak + weak ⇒ pH 7" | A p.8, E32 [avots] |
| M24 | Using an unbalanced equation's ratios; applying 22,4 L/mol to liquids, solids or non-standard conditions | D p.19, E60 [avots] |
| M25 | Neutralisation by equal moles of acid and base rather than equal moles of H⁺ and OH⁻ (H₂SO₄, H₃PO₄) | B #10–13 [avots] |
| M26 | mL and L, mmol and µmol, g and mg in the same line | B #15, E03 [avots] |
| M27 | Metal + acid: any metal liberates H₂; Fe gives Fe³⁺ with HCl | A p.9, p.13 [avots] |
| M28 | Salt formulas: charge balance, sulfate/sulfite, nitrate/nitrite, Fe(II)/Fe(III) | A p.12 [avots] |
| M29 | Isotopes: confusing A, A_r and M; "tritium does not exist" | E05–E07 [avots] |
| M30 | Electron configuration: filling 3d before 4s; group number = valence electrons for d-block | E s.16 [avots] |
| M31 | 5 % glucose "isotonic" taken to mean it stays isotonic in the body (glucose is metabolised) | D p.5 [papildinājums] |
| M32 | Barium: all barium salts are poisonous (BaSO₄ is safe because it is insoluble; soluble Ba²⁺ salts are toxic) | D p.6 [papildinājums] |
| M33 | Reading solubility (g/100 g solvent at a stated temperature) as a concentration (mol/L of solution) | A p.6 definition + F06 worked models [papildinājums] |
