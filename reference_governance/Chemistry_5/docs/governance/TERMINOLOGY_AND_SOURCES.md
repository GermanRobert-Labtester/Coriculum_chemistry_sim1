# Terminology and Sources

> Parent Contract: `../../AGENTS.md`  
> Extends: AGENTS.md §3, §6, §9, §10  
> Last updated: 2026-11-07 · Status: `[INSPECTED]` governance/source-audit records; course PDF text was not reopened in this run.

## Source authority and conflict resolution

### [CONFLICT-LOG]

Authority order: (1) topic description defines scope; (2) blank/answered lab sheets define task and expected course answer; (3) `Kinetika.pdf` is primary lecture theory, with `Kinetika_Katalize_2020.pdf` secondary except unique content; (4) MU sheet supplies questions, not an answer key; (5) correct demonstrable errors using named evidence and show source → correction → reason. `AGENTS.md` outranks `DESIGN.md` and historical plans/prompts.

| Open item | Handling |
|---|---|
| K10 catalase value/unit | Preserve exact course entry; candidate literature values from different organisms/assays do not resolve the course value. Lecturer confirmation remains needed. |
| K17 induced-reaction example | Verify exact source passage and reaction conditions; word overlap/catalog scope is insufficient. |
| L1 MnO₂ / MnO | Separate reagent identity, oxidation state, equation and catalyst role; course-key intent remains unconfirmed. |
| Thiosulfate method | Preserve independent-tube endpoint; order fit is `ln(1/t)` vs `ln C`. Worksheet slope `0.0374 s⁻¹` is not a first-order rate constant. |
| Clinical kinetics | State one-compartment/linear/first-order assumptions; do not generalize to “most drugs” without claim-specific source text. |

### [VERIFIED-SOURCE-REGISTRY]

Six course PDFs are present. The byte sizes and SHA-256 values below are copied from the saved `CHECKS.md` source-integrity record (2026-11-06); this run did not independently hash or extract the PDFs. Page counts are from the workspace inventory. Course document text remains `[UNVERIFIED this run]`; metadata/scope is not claim-level proof.

| Workspace source file | Bytes | Pages | SHA-256 | Role / extraction evidence |
|---|---:|---:|---|---|
| `5. temata apraksts.pdf` | 144,598 | 1 | `3b7683b609a9b44d6541a8d5ab3328e9ad4046fe16379a65245618f8582ed775` | Scope/outcomes; `pdfinfo` page metadata recorded; no text extraction this run. |
| `Kinetika.pdf` | 545,564 | 18 | `e744e7c02bbcdccceb0bd5b79527d3be0881a2b60c6a14573f8ce90530753000` | Primary lecture theory/questions; `pdfinfo` page metadata recorded; no text extraction this run. |
| `Kinetika_Katalize_2020.pdf` | 595,796 | 31 | `621d3d208d9a8f60231cd0c27e4fe86303831857fdfd564161d0132d8a7cf01e` | Secondary slide deck except unique content; metadata only this run. |
| `5LW_MCh_Kinetics_2025_LV.pdf` | 441,140 | 4 | `921c1ca2efe55d2004678a543399b79f770bcb73119791246a97ca702a9fea32` | Blank laboratory sheet; metadata only this run. |
| `5LD_Kinetics_Laboratorijas_darbs_Atbildes_2026.pdf` | 370,385 | 5 | `dc8b9eaa8320864b6c6084090bb0d35a319e87a7427a0048c7f34db08530ad4e` | Laboratory answer key; metadata only this run. |
| `MU_Kin_1_2015_cAB.pdf` | 545,663 | 2 | `0316f9bd2369126f4f6b10e8026e658d1e03939b5dc269c98a88708ac270c235` | MU questions, no answer key; metadata only this run. |

Historical extraction/access method in `SOURCES_AUDIT.md`: IUPAC Gold Book entries were read from Gold Book XML mirror; open-access article material was read/checked online; books marked `[B]` were named by edition/topic but section/page not opened. No new PDF extraction method was run here. Exact course page mappings remain: topic scope (description p.1); core theory/questions (`Kinetika.pdf`, 18 pp.); slides (`Kinetika_Katalize_2020.pdf`, 31 slides/pages); blank lab (`5LW`, 4 pp.); answer key (`5LD`, 5 pp.; unresolved K10/L1 intent); MU question sheet (`MU`, 2 pp.; no key). Do not assign a page number within a PDF beyond this recorded map unless reopened.

| Authority / exact locator | Scope | Evidence and limit |
|---|---|---|
| IUPAC Gold Book O04322 (order), M03989 (molecularity), E02035 (elementary reaction), R05156 (rate), C00876 (catalyst), H02716 (half-life), A00092 (activated complex), A00446 (Arrhenius), O04365 (oxidation state); online entries, DOI prefix `10.1351/goldbook.` + code | Kinetics terms and definitions | `SOURCES_AUDIT.md` records literal entry review `[TEXT-VERIFIED]`; no new re-open this run. No page numbers. |
| Briggs, G. E.; Haldane, J. B. S. “A Note on the Kinetics of Enzyme Action.” *Biochemical Journal* 19(2), 338–339 (1925), DOI `10.1042/bj0190338`, PMCID PMC1259181 | E+S/ES scheme and steady-state approximation | Open text/citation checked in prior audit `[TEXT-VERIFIED]`; applicability still claim-specific. |
| Johnson, K. A.; Goody, R. S. “The Original Michaelis Constant: Translation of the 1913 Michaelis–Menten Paper.” *Biochemistry* 50(39), 8264–8269 (2011), PMC3381512 | Historical rapid equilibrium vs Briggs–Haldane steady state | Prior audit records article read `[TEXT-VERIFIED]`; exact application must remain bounded. |
| Miłek 2018, *Brazilian Journal of Chemical Engineering* 35(3), DOI 10.1590/0104-6632.20180353s20160617 | Catalase activation energy | Prior text verification `[TEXT-VERIFIED]`: *Aspergillus niger*, EC 1.11.1.6, 20–50 °C, pH 6.9, 0.015 M H₂O₂; Ea 12.9 ± 0.7 kJ·mol⁻¹. Does not establish the course sample. |
| Koshland, D. E. Jr. “Application of a Theory of Enzyme Specificity to Protein Synthesis.” *PNAS* 44(2), 98–104 (1958), PMC335371 | Induced fit | Citation/fragment checked; open body text unavailable in saved audit, so no literal text claim `[TEXT-VERIFIED]` beyond cited fragment. |
| Atkins, *Physical Chemistry*; Laidler, *Chemical Kinetics*; Cornish-Bowden, *Fundamentals of Enzyme Kinetics*, 4th ed.; Segel, *Enzyme Kinetics*; Silbey–Alberty–Bawendi, *Physical Chemistry* | Reaction order, Maxwell–Boltzmann, inhibition, K17 | Topic/edition leads only; specific sections/pages unopened `[METADATA-VERIFIED / SCOPE-ALIGNED]` or `[UNVERIFIED]`. |
| Nelson & Cox, *Lehninger Principles of Biochemistry*, 7th ed. (2017), ISBN 9781319108243 (also format ISBN 9781464126116) | Enzyme kinetics, inhibition, methanol | NLM catalog metadata/scope; no relevant passage opened. |
| Rang et al., *Rang & Dale’s Pharmacology*, 9th ed. (2019), ISBN 9780702074462 (print; 9780702074486 another format) | Pharmacokinetics, drug enzyme inhibition | Elsevier metadata/scope; exact supporting sections unopened (A18). |
| Brunton et al., eds., *Goodman & Gilman’s The Pharmacological Basis of Therapeutics*, 13th ed. (2018), ISBN 9781259584732 | Pharmacokinetics and inhibition | NLM metadata/scope; exact supporting sections unopened (A18). |
| Six course PDFs above | Scope, expected course answer, lab method | File identity/page counts only this run. Existing source audit contains older claim-level entries; reopen exact pages before content change. |

No fabricated pages, quotations, editions, ISBNs, DOIs or answer keys. Bibliographic metadata does not prove claim text. Exact source file fingerprints are in `CHECKS.md`; this governance run did not independently hash/extract all six PDFs.

## Terminology dictionary

### [TERMINOLOGY-DICTIONARY]

`termbase.json` governs; glossary, notation and cards are generated. Latvian instructional copy; decimal comma in prose and point in data; NBSP before units; U+2212 minus; real sub/superscripts or MathML; no Cyrillic look-alikes; preserve quoted source notation.

| Concept | Canonical form / rule | Rationale |
|---|---|---|
| Reaction order / molecularity | `reakcijas pakāpe` (`kārta` glossed once) / `molekularitāte` | Empirical overall order differs from elementary-step molecularity. |
| Constants | italic `k`; uppercase `K` for equilibrium | `k` units depend on reaction order. |
| Half-life | `pusperiods` / `pussabrukšanas periods`; `t½` | Lecture `τ½` retained as source notation. |
| Activation energy | `aktivācijas enerģija`, `Eₐ`, kJ·mol⁻¹ | Energy barrier, not supplied dose. |
| Arrhenius | `Arrēniusa vienādojums` | Reject `Arēniusa`. |
| Enzyme kinetics | `Mihaelisa–Mentenas`, `K_M`, `v_max`, `k_cat` | `k_cat` per active site. |
| Oxidation state | `oksidēšanas pakāpe`, Mn(+VII) | Do not write free Mn⁷⁺ for oxidation state. |
| Inhibition | `konkurentā`, `nekonkurentā`, `jauktā`, `nekonkurējošā (uncompetitive)` | Keep idealized models distinct. |
| Clinical (A19 open) | `farmakokinētika`, `farmakodinamika`, `eliminācijas konstante` (`kₑ`), `stacionārais stāvoklis`, `uzkrāšanās koeficients` | Add reviewed entries; state the model assumptions. |

Terminology normalization never decides a source-content dispute.

## 2026 literature

### [LITERATURE-2026]

Treat every 2026 publication or claim as a lead until primary metadata and relevant text are opened and recorded in `SOURCES_AUDIT.md`. No 2026 literature was verified in the 2026-11-06/07 governance evidence. Keep new literature supplemental and distinct from course answers; record author, title, venue, year, DOI/URL only after verification, exact section/pages actually read, model/system applicability, and limitations.
