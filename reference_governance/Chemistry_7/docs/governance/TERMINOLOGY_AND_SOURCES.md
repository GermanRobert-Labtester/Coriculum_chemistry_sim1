# Terminology, Sources and Provenance

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§3, 6, 9, 10  
Last updated: 2026-11-12 (T03/B05; T19; T07)  
Verification: `[INSPECTED]` governance, source inventory and saved provenance records; `[TESTED]` T04 terminology queries against Tēzaurs (MLVV/LLVV) and AkadTerm/IATE recorded in `plan/terms-source.md` (2026-11-09); T07 (2026-11-10) re-extracted both protocol files with rechecked hashes and page renders (`plan/protocol-extraction-T07.md`, `[TEXT-VERIFIED]` per page; row-by-row master reconciliation, no calculation defect found); T19 (2026-11-12) bibliographic verification of every external source against Crossref/Open Library/publisher records with the per-claim mapping in `plan/claim-ledger.csv` and the query log in `plan/terms-source.md#t19-verify-log` — Skoog year resolved to © 2018 (Cengage primary page), Gold Book definitions read directly, Sheraz introduction passage read in the CC BY full text, Harris 10th ISBN confirmed (`[TESTED]` web-record checks, no page invented).

<a id="source-authority"></a>
## [SOURCE-AUTHORITY] Authority and evidence labels

Authority order: current user instruction; this standing contract; primary course files for what the course says/procedure; recomputed `tools/data.py` for derived values; named references for external claims; dated plans as leads, not proof. Course material may contain errors. Sources and `workspace_skills/` are read-only; never edit, rename, delete or execute copied skills. Never copy university branding, student fields or PDF metadata names; never describe the guide as official university material.

| Tag | Meaning |
|---|---|
| `[TESTED]` | Command or measurement was run now; record scope/result |
| `[INSPECTED]` | Directly read/parsed artifact; state what portion |
| `[INFERRED]` | Conclusion follows from identified evidence |
| `[UNVERIFIED]` | Required evidence absent or not checked |
| `[TEXT-VERIFIED]` | Relevant source text was read |
| `[METADATA-VERIFIED / SCOPE-ALIGNED]` | Identity and claim scope checked; not a substitute for page-level text when a passage is asserted |

Document labels remain separate: `avots` (source statement), `aprēķins` (recomputed), `papildinājums` (named external reference), `nav pārbaudīts`. A page number means that page was read. Never fabricate page numbers, quotes, editions, ISBN/DOI, citations, values, hashes or approval. Keep quotes ≤25 words per source. A correction records original wording, correction, reason, location, permanent erratum ID and changelog reference.

<a id="conflict-log"></a>
## [CONFLICT-LOG] Source and warrant conflicts

| ID | Conflict | Resolution rule |
|---|---|---|
| C-01 | Course source terminology and scientific nomenclature may diverge | Attribute course wording; correct teaching claim transparently and preserve erratum |
| C-02 | Absorbance/transmittance notation and units | Use decadic `lg`; `A=lg(I₀/I)`, `T=I/I₀`, `A=−lg T`; keep dimensionless A separate from absorptance. T06 (2026-11-09): definition order `T = I/I₀` before `A = −lg T` is a contract check (verify.py C48); the integration constant is anchored to the blank (`I(0) = I₀`), slope unit follows the x-axis basis (mg·mL⁻¹ axis → mL·mg⁻¹ slope; mol/L axis → L·mol⁻¹), ε = k·M under the assumed l = 1 cm |
| C-03 | Molar coefficient symbol/unit may be wrong in course source | `ε` in L·mol⁻¹·cm⁻¹; mass absorptivity `a` in L·g⁻¹·cm⁻¹; dimensional reasoning, not unsupported “10⁶ impossible” claim |
| C-04 | 440 nm protocol setting vs 444 nm literature maximum vs “flat peak” | Keep setting and literature fact separate; local flatness is unverified without matching spectrum/conditions |
| C-05 | High R²/near-zero intercept used as proof; three fits differ | Name model, blank inclusion and point count; residuals/intercept/range/blank are diagnostics, not proof of accuracy or method validity |
| C-06 | ε converted from mass slope assumes path length | `l=1 cm` is an assumption unless protocol/sample establishes it; do not call it measured |
| C-07 | LOD/LOQ values use `3sy/k`, `10sy/k` | Label simplified regression estimates, not blank-based validated decision limits; compute from full-precision s_y (E26: displayed values must reproduce from stated inputs; blank replicates absent in Lab 6B — scope note recorded 2026-11-09) |
| C-08 | “kivete” and absorbance Latvian form | Checked 2026-11-09 (T04, `plan/terms-source.md`): `kivete` is source-supported (MLVV/LLVV entries; LLVV 2. ķīm. names the optical-apparatus vessel; AkadTerm/IATE cuvette → LV kivete IETEICAMS) — a supported house choice, not an official-norm claim; `kuvete` absent from Tēzaurs (negative result). EN absorbance maps to LV “absorbcija” (IATE), so “absorbance”/“transmitance” remain deliberate house style for disambiguation; “caurlaidība” is attested (incl. gaismas caurlaidība) but ambiguous with permeability; Drift lint: `tools/lint_html.py` / C45 |
| C-09 | Table values and source transcription | Reconcile against filled protocol pages and named fit; source hashes alone do not prove extracted values. T07 (2026-11-10): full page-by-page extraction recorded (`plan/protocol-extraction-T07.md`, `[TEXT-VERIFIED]`, render-inspected); master tables 13/14/15 reconcile row-by-row; the "taises" [sic] schema typo is present in BOTH protocol files (erratum E28); 2022 form reserves a "Paraugs 1" column absent from the filled 2020 table |
| C-10 | FeSCN²⁺/higher-complex speciation | Treat equation as simplified; dominance depends on conditions; do not assert speciation without matching solution conditions |

Warrant rule: a source with a numeric value does not support all nearby claims. Record chemical/system conditions, solvent, pH, temperature, wavelength, concentration, model and instrument range as relevant. Nearby maxima do not prove local slope; a regression statistic does not prove trueness; assumed cell length does not make path length measured. Keep claim IDs with later corrections. Full legacy dossier includes these C-01–C-10 scope notes and tasks in the roadmap; the concise rows here preserve their decision rules.

<a id="terminology-dictionary"></a>
## [TERMINOLOGY-DICTIONARY] Canonical forms and search guidance

| Canonical | Avoid / qualify | Rule |
|---|---|---|
| absorbance `A` (gloss “absorbcija”; English at first use) | “absorbcija” as an unqualified quantity name | Dimensionless; separate from absorptance. T04 2026-11-09: IATE maps EN absorbance → LV “absorbcija”; latviskota viennozīmīga forma nav atrasta — forma “absorbance” ir deklarēts mājas stils (12.2; C45 lint), nevis valodas iestādes norma |
| transmittance `T=I/I₀`; `A=−lg T` | “caurlaidība” unless verified | `%T` is percent transmittance. T04 2026-11-09: AkadTerm apliecina “caurlaides koeficients”; “caurlaidība” attested but ambiguous (also permeability) |
| `lg` | `ln`, `Lg` | Decadic logarithm |
| Bugēra–Lamberta–Bēra likums | Bēra–Bugēra–Lamberta; “Bēra likums” | Name historical contributors without unsupported dates |
| molārais absorbcijas koeficients `ε`, L·mol⁻¹·cm⁻¹ | `a`; “1/mol·cm” | `a` is mass absorptivity, L·g⁻¹·cm⁻¹ |
| optical path length `l` (cm) | cuvette width | Mark assumption if unstated |
| `c` (mol/L); `γ` (mg/mL) | generic `C`; using `γ` as density | Keep quantities distinct |
| blank sample; zero setting | blanking = calibration curve construction | Separate operations |
| calibration line/plot; calibration solutions = standards | mixed sense of “calibration” | State local course usage |
| spectrophotometer; filter photometer/photocolorimeter | using as synonyms | Distinguish instrument selection method |
| absorption band; `λmax` | molecular “line”; bare `λmax` | Molecular sublevels/environment produce bands |
| kivete | kuvete | Source-supported form: MLVV/LLVV entries (LLVV 2. ķīm. = optical vessel); AkadTerm/IATE lists it IETEICAMS; `kuvete` is an unattested variant (2026-11-09 check) |
| dilution; `C₁V₁=C₂V₂` | dissolution | Dilution ≠ dissolving |
| quantum/photon; molecular orbital | “orbītas” for electron states | Lewis 1926 historical; Latvian name spellings per local canon |
| optical density `D`, extinction, graduation, reference solution, absorptance | unqualified use | Recognition only; define distinction and authority |

Typography: quantities italic, `Δ`/`lg`/units upright; U+202F before units; U+2212 minus; decimal comma; `mL`. See `plan/style-canon.md` (recorded 13 rules; not freshly audited here). Errata E1–E28 are permanent; never renumber. E18 residuals and E19 R² link to ISS-001/ISS-002; E20 wavelength to ISS-003; E24 separates the 440 nm protocol setting from the 444 nm aqueous literature maximum and records that local flatness is unverified; E25 (T02, 2026-11-09) records the “krustpunkts ≈ 0 apstiprina…” overclaim — intercept/fit diagnostics never confirm method validity, and the calibration range is bounded by the standards span; E28 (T07, 2026-11-10) records that the “Kalibrēšanas taises konstruēšana” [sic] schema typo exists in both protocol files (2020 p.1 chevron render-inspected at 300 dpi; 2022 SmartArt label), not only in the 2022 form.

<a id="verified-source-registry"></a>
## [VERIFIED-SOURCE-REGISTRY] Workspace primary sources and hashes

Source hashes below are recorded in the 2026-11-06 governance snapshot. Current byte/timestamp inventory was checked 2026-11-07; files were not rehashed or re-extracted during this run, so hashes remain historical until refreshed.

| Source | Role/status | SHA-256 (recorded) | Boundary |
|---|---|---|---|
| `7_SEM_Optika_analize_2025.pdf` | Course theory; primary | `7d7bccca30c38e10312e82153f7b9f0d81a1e684c5afd974b48b9c68e2ed2951` | Full page-by-page source review outstanding |
| `LD_Spektrofotometrija_Paraugs.pdf` | Filled 2020 protocol; only absorbance source; re-extracted page-by-page 2026-11-10 (T07) | `5ee9207ef4948f4d8091572bb573903373ebbddba78cc1ec3278b486430f55cf` | Rows reconciled to master tables 13/14/15; extraction transcript + renders in `plan/protocol-extraction-T07.md` |
| `Absorbcija_LD_2022.docx` | Blank 2022 form; field/SmartArt map extracted 2026-11-10 (T07, read-only unzip) | `95c1a7d01ff7d2deccb8f7af8b58ffa52914e5b6c224c65ee1a21b056f2bdfd6` | Not a source of absorbance values; "Paraugs 1" column divergence and stale in-form table reference recorded in the T07 extraction artifact |

Current HTML baseline: `Master_spektrofotometrija_SEM7_LD6B.html`, 313,828 B, SHA-256 `f90d552db94b5da17f2b86aed16a9e55ad66080fb72f4731b5ea1e62c2ba7a22`, mtime 2026-11-02 22:03:22 (snapshot matches start/end of governance run).

<a id="literature-2026"></a>
## [LITERATURE-2026] Named external leads and scope

| Reference | Recorded status and use boundary |
|---|---|
| Sheraz et al., “Photo, thermal and chemical degradation of riboflavin,” *Beilstein J. Org. Chem.* 10 (2014), 1999–2012, DOI `10.3762/bjoc.10.208` | `[TEXT-VERIFIED]` (T19, 2026-11-12): CC BY open access; full text read via Europe PMC PMC4168737; introduction passage states absorption at 223, 267, 373 and 444 nm *in aqueous solution*; not Lab 6B spectrum or proof of local slope at 440 nm |
| Currie 1995, *Pure Appl. Chem.* 67, 1699–1723, DOI `10.1351/pac199567101699` | `[METADATA-VERIFIED / SCOPE-ALIGNED]` re-confirmed 2026-11-12 via Crossref (publisher record now Walter de Gruyter); full-text re-attempt blocked (HTTP 202 empty); simplified LOD/LOQ stay estimates; terminology/nomenclature use only |
| IUPAC Gold Book A00028/A00035/M03972 | `[TEXT-VERIFIED]` (T19, 2026-11-12): all three definition texts read directly on goldbook.iupac.org (previously 403-unreachable); definitions support the A/T/ε notation rows; citations visible on the entry pages (Green Book 2nd ed., p. 32; PAC 2007, 79, 293) are entry metadata, not read editions |
| IUPAC calibration guidelines, 2002, DOI `10.1351/pac200274050835` | Metadata/scope lead; full PDF was blocked in prior record; no page-specific quote |
| BIPM SI Brochure, 9th ed.; DOI `10.59161/AUEZ1291` | Record metadata checked previously; relevant chapter/page not inspected |
| Beer 1852 DOI `10.1002/andp.18521620505`; Planck 1901 DOI `10.1002/andp.19013090310`; Einstein 1905 DOI `10.1002/andp.19053220607`; Lewis 1926 DOI `10.1038/118874a0` | Metadata/history leads only; all four Crossref-confirmed 2026-11-12 (T19); texts not read in local record |
| Skoog–Holler–Crouch, 7th ed., ISBN `978-1-305-57721-3` | **Year conflict RESOLVED 2026-11-12 (T19):** Cengage product page states “7th Edition © 2018” (primary publisher); Open Library community record (2016) is divergent; LC classification QD79.I5S58 2018 corroborates; exact pages unverified |
| Atkins et al., 12th ed., ISBN `978-0-19-884781-6`; IUPAC Green Book 3rd, ISBN `978-0-85404-433-7` | Bibliographic leads; Open Library records confirmed 2026-11-12 (OUP 2022; RSC 3rd ed. 2007-09-30); OUP primary page unreachable this run; exact chapter/page not read |
| Harris, D. C.; Lucy, C. A., 10th ed., ISBN `978-1-319-16430-0` | `[METADATA-VERIFIED / SCOPE-ALIGNED]` (T19, 2026-11-12): print ISBN confirmed via Open Library (W. H. Freeman, print date 2019-12-13); edition/authorship from publisher-offering records; publisher product page unreachable (now promotes 11th ed.); book pages never seen |
| Riboflavin photolysis general support | `[UNVERIFIED]` (no named source; ledger row CL-08); do not rely without inspection |
| de Berg, K.; Maeder, M.; Clifford, S., "A new approach to the equilibrium study of iron(III) thiocyanates…", *Inorg. Chim. Acta* 445 (2016) 155–159, DOI `10.1016/j.ica.2016.02.052` | `[METADATA-VERIFIED / SCOPE-ALIGNED]` identity only (Crossref 2026-11-12, T03/B05); full text unread — experimental conditions (Fe/SCN concentrations, acidity) NOT tabulated, so unique mono-complex dominance stays unsupported; existing E7 caveat retained verbatim (ledger row CRB-05). Access re-attempted 2026-11-12 (F05/ST7): Semantic Scholar API — abstract elided by publisher, `openAccessPdf.status CLOSED`; Unpaywall — `is_oa: false`, 0 OA locations; ScienceDirect landing paywalled. Search-engine condition hints (stop-flow, ionic-strength control, varied HNO₃) are `[UNVERIFIED]` leads only, not tabulated. Additional scope finding: the filled protocol's analyte is riboflavin, so no protocol-side Fe(III)/SCN⁻ condition set exists at all; note withheld, analysis in `plan/speciation-conditions.md` |
| `skolo.lv` figure-2 URL | `[UNVERIFIED]` identity/scope; lead only (ISS-009; not re-checked in T19) |

Claim-to-source mapping: `plan/claim-ledger.csv` (T19, 2026-11-12) records each claim ID (C-01–C-10 plus CL-01–CL-16) with source ID, provenance tier, scope, conditions and reviewer/date; the T03/B05 round (2026-11-12) added the per-site claim/source/applicability matrix rows CRB-01–CRB-05 (reviewer CR; verdicts unsupported-as-written → conditional replacements, see `plan/errata.md`); `tools/lint_claims.py` (L1–L7, `--selftest` 7 fixtures) gates the ledger against `src/15*`/`src/16*` markers, status vocabulary, page-citation and tier-consistency rules; wired read-only as `run.sh` step 2e; `tools/claim_lint.py` (P1–P5 banned-inference lint over all src parts, `--selftest` 6 fixtures) wired read-only as `run.sh` step v6b. The T09 round (2026-11-12, lab-6b plan; owner ruling: single-file ledger) harmonized the ledger to the 14-column superset schema documented in `plan/ledger-schema.md` — tier column `status` renamed `provenance` (vocabulary unchanged), new T09 columns `chapter_anchor`, `applicability` (`matched|partial|unmatched`), support-verdict `status` (`supported|conditional|unsupported|unresolved`; `unresolved` rows must carry a `next_action` restating a recorded reopen condition) and `updated`; all 55 rows migrated with verbatim cell preservation; `tools/lint_claims.py` L1–L7 semantics unchanged (selftest 7/7) and new read-only `tools/ledger_lint.py` (R1–R5 schema/integrity/enum/text/next-action gate, `--selftest` 5/5, `--atlas-fields` = the T14 public field-selection contract) wired as `run.sh` step v6d. Recorded deviation: no separate `plan/sources.csv` — src/16 prose names this file as the single claim+source map and the FK is machine-enforced by R2 + L1/L2.

Named governance artifacts: `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` exists (2026-11-06); it is a proposal queue, not authorization. `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` are absent as of the local inventory; `PROMPT_master_html.md` exists and is reference-only/locked. No external network source was consulted in this run.
