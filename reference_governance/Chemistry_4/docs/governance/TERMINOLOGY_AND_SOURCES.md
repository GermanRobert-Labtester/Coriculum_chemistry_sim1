# Terminology and Sources

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§3, 6, 9, 10  
Last updated: 2026-11-07  
Evidence status: source file identities and hashes `[TESTED]`; PDF page claims and outside literature warrants retain prior status and are not newly page-verified here.

## [CONFLICT-LOG]

Source authority and conflict resolution.

| Code | Source role | Rule |
|---|---|---|
| T | topic description | scope and learning outcomes |
| K | theory notes | course exposition/data; known discrepancies remain traceable |
| U | seminar questions | preserve question wording and given values; do not silently replace data |
| L | lab procedure | procedure and measurements |
| LA | partial lab answers | source answer key; conclusions are blank and some numeric/sign errors are registered |
| E | exemplar HTML | convention exemplar only; not a scientific authority |

When authorities conflict, preserve the course-specific answer for assessed tasks, show the discrepancy beside it, and label external corrections `papildinājums`, `jāpārbauda`, or `avotā nav norādīts`. Keep the original, corrected wording, reason, confidence, page/question, and S-ID. Never fabricate a page, quote, edition, ISBN, DOI, or reference. A course-source statement and an external standard are different evidence claims.

Epistemic tags: `[TESTED]` executed/measured now; `[INSPECTED]` directly read or parsed; `[INFERRED]` reasoned implication; `[UNVERIFIED]` unresolved. Provenance: `[TEXT-VERIFIED]` belongs only beside a claim checked against the specific page text; `[METADATA-VERIFIED / SCOPE-ALIGNED]` establishes identity/declared role only. Labels A/P/I/V remain source-local and do not substitute for these statuses.

## [VERIFIED-SOURCE-REGISTRY]

Canonical sources and integrity.

The five source PDFs are workspace-local. Current SHA-256/byte counts were computed 2026-11-07; page counts/roles below were carried from the `pdfinfo` inventory dated 2026-11-06 and were not rerun in this governance task. Hash proves file identity only, not page text correctness.

| ID | Exact file | Recorded pages | Role / map | Bytes | SHA-256 |
|---|---|---:|---|---:|---|
| T | `4 temata apraksts.pdf` | 1 | topic scope | 139,068 | `fd6a32aaa9a133c75f34a333325a38df33e1f5029211a6ed1e4f183876d598e5` |
| K | `Termodinamika_pamatkonspekts_2026.pdf` | 19 | theory; S1–S27; image-only pages historically listed p.2, 6–8, 14, 18 | 684,274 | `753f7a0955c2b1ad55409eed0c2828f326d4162364846e0362fa3a57241f0c91` |
| U | `4_SEM_Termodinamika_uzdevumi.pdf` | 2 | U1–U6 wording/data | 232,085 | `f09cf14dfdaf95a2019a4f231a85b8a5d0c1f50ba14091de1173c66dff7c8360` |
| L | `LW_Thermodynamics_2020_LV (2).pdf` | 3 | lab procedure; historically image-only p.1 | 229,296 | `d1955d5d46d067474d27fdb7a9d5793bf795de9e63c81fde91adf43d9b134c08` |
| LA | `4_SEM_Labor_Thermodynamics_2026_LV _Atbildes.pdf` | 3 | partial lab key; historically image-only p.1 | 268,902 | `bb6227cdc419b1197eb7728de106ab166dc0595b866f80ad8aabe510841a993a` |
| E | `workspace_skills/Master_lekcija_7-8_sanu_dalisinas.html` | — | convention exemplar only | not measured | no hash recorded |

`PROMPT_Master_html_4_tema.md` and `4lastDEEP_INSPECTION_ADDENDUM_20_TASKS_10_FEATURES.md` are present, historical planning/spec artifacts. The user-named `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` were not found in the workspace-local inventory; do not reconstruct them from those historical files. The roadmap is `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md`; it contains 20 T packages, 10 F proposals and B diagnostics despite “35” in its filename, and remains a planning/execution queue rather than an architecture override.

## [TERMINOLOGY-DICTIONARY]

Canonical Latvian terms and correction rules.

| Avoid / source form | Canonical use | Rationale / source |
|---|---|---|
| `siltumsaturs` | entalpija H | obsolete label; explain source wording only when needed (S3) |
| V,n,T,p,c called “state functions” | stāvokļa lielumi; U,H,S,G are stāvokļa funkcijas | distinguish variables from path-dependent Q/A (S26) |
| `enderģisks`, `ekserģisks` | endergonisks (ΔG>0), eksergonisks (ΔG<0) | not the same classification as endo/eksotermisks (S29) |
| ΔG>0 called `aizliegta` | nepatvaļīga kā atsevišķa reakcija | coupling may make a net process feasible (S17) |
| `standartapstākļi` as synonym for standard state | standartstāvoklis; specify T separately from p° | 1 bar standard pressure; state does not set temperature (S6) |
| `rašanās siltums` | Δ_fH°, Δ_rH°, Δ_cH° | identify the thermodynamic quantity and reaction basis (S7–8) |
| entropy defined as `haoss`/`nesakārtotība`; W called probability | energy dispersal; W = mikrostāvokļu skaits | analogy is limited; Boltzmann state count is not probability (S12–13) |
| `siltumkapacitāte` in J/(g·K) | īpatnējā siltumietilpība c; heat capacity C in J/K | distinguish specific from total capacity (S37) |
| food `kalorija` ambiguous | cal=4.184 J; Cal=kcal | label unit case and conversion (S23) |
| ΔG° at biochemical pH 7 | ΔG°′; actual cellular ΔG separately | transformed standard state vs cell conditions (S22) |
| `hemotrofs` | ķīmiotrofs (hemotrofs) only as source quotation/gloss | canonical course terminology (S22, verify spelling warrant) |
| `Lei` | Leu; Leu–Gly (leicilglicīns) | amino-acid abbreviation (S30) |
| homeostāze described as Latin | Greek origin | etymology correction (S21; outside-source warrant required) |
| N₂O₄ `dislāpekļa dioksīds` | tetraoksīds (N₂O₄) | distinguish stoichiometric name (S25) |
| `hlora jons`; `hidroksonija` | Cl⁻ hlorīda jons; H₃O⁺ hidroksonija/oksonija | verify Latvian authority choice before promoting (V) |
| states `(c),(c.v.),(g.),(šķ.)` | `(s),(l),(g),(aq)` | consistent phase notation (S25) |
| `nesakātots`; `250 C`; `2980 K`; `6,03×10²³` | `nesakārtots`; `25 °C`; `298 K`; `6,022×10²³` | spelling, spacing/degree, and constants (S6,S32) |

Keep Hesa likums, Gibsa enerģija, patvaļīgs, siltumefekts. English equivalents belong in the glossary only; do not invent etymologies. Use decimal comma, NBSP before units, U+2212, ΔH°/ΔG°/S°, and convert J↔kJ before combining ΔH and TΔS.

## [SOURCE-DEFECT-REGISTER]

S1–S38, preserved from prior AGENTS.md.

Confidence: C=certain, H=high, V=verify. Basis: S=course sources, X=outside knowledge; X claims remain marked `papildinājums`/`jāpārbauda` until claim-level reference is verified.

| ID | Page / issue / correction to preserve |
|---|---|
| S1 | K pp.2–3 eqs.(2),(4) vs (6), LA p.1: Q absorbed vs released (−ΔH); lab q=c·m·ΔT absorbed; U Q5/Q6 wording is unspecified. C·S |
| S2 | K p.3: isothermal Q=A is valid for ideal gas; “increase U by work” is wrong because ΔU=0. C·S |
| S3 | K p.3: H=U+pV and ΔH=q_p; `siltumsaturs` is obsolete. C/H·S/X |
| S4 | K pp.3–5: Hess law misnamed and const p/V unstated; basis is state-function property. H·X |
| S5 | K pp.4/11, U Q5: photosynthesis ΔH 1273 is wrong; ≈+2808 kJ/mol, U data +2805.3. C·S |
| S6 | K pp.4,19: standard pressure 1 bar, not 1 atm; state ≠ T; typos `2980 K`, `6,03×10²³`. C/H·S/X |
| S7 | K p.4: Eq.(8) duplicated, ν omitted, “entalpija nulle” should be formation enthalpy. C·S |
| S8 | K p.5: combustion values are standard Δ_cH°; Eq.(9) correct. H·X |
| S9 | K p.6: no thermodynamic “force”; direction by ΔS_kop>0. H·X |
| S10 | K p.6: exo/endo defined by sign of ΔH, not E_a. H·X |
| S11 | K p.7: Kelvin statement concerns cyclic process and its sole result. C·X |
| S12 | K pp.8–10,12: entropy ≠ disorder; synthesis ΔS<0 heuristic fails (U Q3 +22 J/(mol·K)). H·S |
| S13 | K p.9: W is microstate count; N_A prints 6.023; δq_apgr is reversible path. H·X |
| S14 | K p.10: exothermic reaction raises surroundings entropy; spontaneity ≠ rate. C/H·S/X |
| S15 | K p.11: garbled statement intended as T·dS > dH. C·S |
| S16 | K p.11: Δ_rS° 182.4→≈+259; Δ_rG(310 K) ≈−2888 (−2865 follows 182.4); “standard at 37 °C” contradictory. H·X |
| S17 | K pp.12–13: use |TΔS|<|ΔH| for the stated case; ΔG>0 is not “forbidden” when coupled. H·S/X |
| S18 | K p.13: Lavoisier–Laplace years 1782–1873 should be 1782–1783. C·X |
| S19 | K p.14: purported isolated examples are open; Earth is closed; numbering 23→27. C·S |
| S20 | K pp.14–15: S_i/ΔS_i collide; use ΔS_org, ΔS_env, ΔS_vis; universe ΔS>0. C·S |
| S21 | K p.15: homeostāze is Greek; Prigogine minimum principle only near equilibrium. H·X |
| S22 | K p.16: metabolism≠digestion; hemotrofs; ΔG°′; ATP→AMP+PP_i ≈−45.6. H/V·X |
| S23 | K p.17: thermochemical 4.184 J exact; 14.5→15.5 °C=4.1855; Cal=kcal. H·X |
| S24 | K pp.17–18: 9/4/4 kcal/g are Atwater, not bomb values; bomb measures ΔU; figure/table numbering; 2680 kcal unsourced. H/V·X |
| S25 | K p.19: ΔG°(CO₂) −394.3; ΔG°(H₂O,g) −228.5; N₂O₅ row is solid; N₂O₄=tetraoksīds; state notation. C/H·S |
| S26 | K p.1: distinguish parameters from state functions; typos. H·X |
| S27 | K coverage gaps: Third Law, kinetic/potential energy, ΔG–K, temperature dependence. C·S |
| S28 | U Q5: O₂ −11.715/110.876 are O₂(aq); O₂(g)=0 yields 2875.6 vs 2805.3; phases missing. H·X |
| S29 | U Q5: use endergonisks/eksergonisks. C·S |
| S30 | U Q3/Q4: Lei→Leu; `(c)`/`(s)` mixed. H/V·X |
| S31 | U/L topic numbering 3/4 and `Termo-1-2015` inconsistent; this course is topic 4. C·S |
| S32 | T typo `nesakātots`; assessment lists tests only. C·S |
| S33 | LA p.2: 2·(−273.19) should be −237.19; −104.10 is right. C·S |
| S34 | LA p.2: ΔG° −104.10 vs −102.196; H₃O⁺ data inconsistent; accepted ΔS°≈+80, ΔG°≈−79.9 (=RT ln K_w); show discrepancy [V]. C/H·S/X |
| S35 | LA p.2: reverse reaction +102.196 (≈+79.9); `250 C`→25 °C; ΔS 0.154305. C·S |
| S36 | LA p.2: ΔH_r=−52.3, not +52.3; ΔT=2 has one significant digit; ±0.1 K=5%; theoretical ΔT 2.15 K. C·S |
| S37 | L/LA p.1: c=īpatnējā siltumietilpība; assumptions ρ=1.00, no calorimeter C/no heat loss; base limiting. H·X |
| S38 | LA p.3: conclusions blank; expected ΔG°<0, ΔH°<0, error 6.9%, heat loss. C·S |

## [LITERATURE-2026]

External literature and claim warrant gate.

No complete verified bibliographic identity registry for 2026 literature was established in this workspace-only pass. OI-06 claims include BMR/TDEE, ischemia, ATP/Mg²⁺ additions and a “>250%” Roediger–Karpicke learning claim. Require authors, title, edition/year, publisher/journal, DOI/ISBN when verifiable, exact page/section or stable location, claim wording, population/conditions, and inspected text. Do not cite a search snippet or metadata as text evidence. Until then mark the claim `papildinājums`/`jāpārbauda` or `avotā nav norādīts`.
