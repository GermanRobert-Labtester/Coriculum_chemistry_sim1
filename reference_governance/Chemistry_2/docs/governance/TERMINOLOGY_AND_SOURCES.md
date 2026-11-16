# Terminology and Sources

**Parent Contract:** `../../AGENTS.md`  
**Extends:** AGENTS.md §§3, 6, 9, 10  
**Last updated:** 2026-11-07 · **Status:** [INSPECTED] workspace ledgers and B03 source adjudication read; outside authorities remain unverified unless explicitly stated.

## [CONFLICT-LOG]

**Authority order, evidence tags and conflict method.**

Authority order: (1) five local course PDFs for what the course says (preserve and label defects); (2) `PROMPT_Master_html_2_tema.md` §§7/6; (3) `AGENTS.md` and this shard; (4) an explicitly active task prompt/roadmap if present; (5) skills as advice. A verified external standard may support an addition or correction but never silently replaces the course account. If a source is silent, state `avotā nav norādīts`.

Evidence tags:

- `[TESTED]`: reproducible check actually run.
- `[INSPECTED]`: artifact directly read/observed.
- `[INFERRED]`: reasoned but not primary-source verified.
- `[UNVERIFIED]`: not established.
- `[TEXT-VERIFIED]`: wording read at a recorded text locator.
- `[METADATA-VERIFIED / SCOPE-ALIGNED]`: metadata and relevance checked; does not prove full-text support.

Never invent page numbers, quotations, editions, publishers, ISBNs, DOIs or URLs. Preserve exact source wording in quotations and log every correction with locator, original, correction, reason and confidence (C certain arithmetic/standard, H high interpretive confidence, V lecturer-policy decision).

## [VERIFIED-SOURCE-REGISTRY]

**Workspace source records.**

The current `build/sources.json` is a local hash-pinned course-source ledger, retrieved 2026-11-07. Schema fields are `id`, `kind`, `file`, `title`, `edition`, `year`, `publisher`, `pages`, `locator`, `retrieved`, `read_level`, `verification`, `supports`, `quote_ok`, `sha256`, and `notes`. Its `read_level` is `snippet` and `verification` is V2; this establishes only the recorded passages and metadata, not a full-page editorial review. The hashes below are as recorded in that ledger; `build/check_sources.py` and B03 report matching hashes on the 2026-11-07 adjudication pass.

| ID | Workspace file | Title / role | Year / pages | Publisher metadata | SHA-256 |
|---|---|---|---|---|---|
| S-TOPIC | `2_Temata apraksts 2020.docx.pdf` | Topic scope, outcomes, assessment; supports ch-1, ch-2 | 2020 / 2 | Not stated | `c7d423021bc7f661a4b1f35c4e731a9c06101d60791b54ee24c7c3aa7110ede5` |
| S-ANALIT | `Analitiskas-metodes_2024.pdf` | Theory; supports ch-2, ch-3, ch-4, ch-6, ch-7, ch-8 | 2024 / 7 | Not stated | `9d1aeafebc4f85a177119169560b31b48b2413a6e183c3fe4da4fe03ec7d896a` |
| S-2A | `2A_SEM_MCh_LV_Merijumi,grafiki_2025.pdf` | Worksheet 2A; supports ch-7 through ch-11 | 2025 / 4 | Medicīniskā ķīmija. Cilvēka fizioloģijas un bioķīmijas katedra (document header) | `319dfef6e821b934005d8fa42301580fb5747ab456ae291fe5d95a57a628a00a` |
| S-2B | `2B_SEM_MCh_LV_Trauki,skidumi_2025.pdf` | Worksheet 2B; supports ch-4, ch-5, ch-6, ch-12 | 2025 / 4 | Same header evidence | `894b5fa3db4e044a6b994b788d0ca13b8e2e3b21b163c60ac1928ebfc00f854c` |
| S-2026 | `2_SEM_MCh_LV_Trauki_Grafiki_Cipari_2026_Atbildes.pdf` | Worksheet and answer key; Q5 blank; supports ch-1, ch-4, ch-7–ch-12, ch-16 | 2026 / 7 | Same header evidence | `bfe8fdd3da40d52084aa7f4d5c72253b0427fe74a2b27f00f2cd417a69980f5b` |

The exact edition is not stated for these PDFs. B03 reports extraction of all five PDFs and direct image inspection of the embedded Q8 graph; its text/page checks are prior adjudication evidence, not re-run in this governance-only turn. `build/claims.json` has C01–C20. C19 (evaluated Hg-203 data) and C20 (521 nm reagent identity) remain open. The full course source-change register S1–S23 is summarized below; consult the source PDF and `build/claims.json` before editing product content.

External authorities named in product/diagnostics but not primary-read or hash-pinned in the local ledger: VIM 2.20/2.21; ISO 5725; IUPAC Gold Book B00626; BIPM SI Brochure; NuDat/ENSDF; LNHB-DDEP. Treat their statements as `[INFERRED]` or `[UNVERIFIED]` until a local readable source copy with locator and hash is recorded.

## [TERMINOLOGY-DICTIONARY]

**Canonical wording and correction risks.**

| Risk / source form | Preferred form | Rationale / evidence boundary |
|---|---|---|
| `zīmīgie skaitļi` | `zīmīgie cipari` | S13 terminology correction. |
| `vidējā kvadrātiskā kļūda`; `σₙ₋₁` used for spread | `standartnovirze s` | Distinguish the statistic from measurement error; S8. |
| `standartkļūda` | `vidējā aritmētiskā standartkļūda sₓ̄ = s/√n` | Name the estimate and statistic. |
| `drošības intervāls` | `ticamības intervāls` / `ticamības līmenis` | V: verify lecturer/course policy before exam-facing replacement. |
| `Stjudenta`; `tαn` | `Stjūdenta t(α; n−1)` | Spelling and explicit degrees of freedom; S8. |
| `absorbcija A` for measured logarithmic quantity | `absorbance A` (dimensionless); `absorbcija` for process | Quantity/process distinction. English term needs `lang="en"`. |
| `a`, `1/mol·cm` | Discuss coefficient symbol with scope; ε may use `L·mol⁻¹·cm⁻¹` where warranted | Do not silently equate course `a` to ε; S5 and course correction record. |
| `precizitāte` means both scatter and closeness | `precision` = scatter; `pareizība` = closeness to reference | S6; VIM is named but not primary-read in B03. Lecturer policy remains separate. |
| `atkārtojamība` / `reproducējamība` swapped | Repeatability: same defined conditions; reproducibility: changed conditions/labs | S6; external standard remains unverified locally. |
| `kļūda` for uncertainty | `kļūda = result − reference`; `nenoteiktība` characterizes attributed dispersion | Distinct concepts; avoid implying the true value is known. |
| `reālā vērtība` | `atsauces vērtība` | V: course policy check. |
| `tvaika nosūcējs`; Mora/Mohr confusion | `velkmes skapis`; `Mora pipete` = one-mark, `mērpipete` = graduated | Equipment identity/markings still require source or instrument documentation; V. |
| `ω` / `w` / `C%`; `cM` / `CM` | `w`; `c(B)` in mol/L | Avoid symbol collisions; V where course convention affects assessment. |
| mass concentration / density conflated | `γ(B)` / `ρ` | Distinct quantities. |
| `ppm`; `ml`; `sec`; `diennakts` | Prefer `mg/L` only when justified; `mL`, `s`, `dienas` or `d` | SI consistency; do not assume ppm equivalence without context. |
| `tiešā/netiešā proporcija`; spelling variants of conical flask | `tieši/apgriezti proporcionāls`; choose one consistent `koniskā kolba` form | Correct meaning and consistency. |
| bare `450` / `400` | `4,5·10²` or `4,50·10²` according to precision | Trailing zeros are ambiguous; S10. |
| `1·10⁻⁶ µmol per mol` | `10⁶ µmol per mol` | Prefix arithmetic; S1. |
| `¹³³Cz` | `¹³³Cs` (cēzijs) | Element symbol; S2. |
| `divi zīmīgie cipari aiz komata` | `divi zīmīgie cipari` OR `divas zīmes aiz komata` | Distinguish significant digits and decimal places; S9. |

No invented etymologies. Existing term gate is `build/check_terms.py` plus data; a pass is not editorial verification. Inspect quotations and source-conflict regions directly.

## [COURSE-CONFLICTS-S1-S23]

**Source correction register summary.**

These are source defects identified in `PROMPT_Master_html_2_tema.md` §7.3 and detailed in the master appendix/claims register. Preserve the course account as `avotā`; any correction must be labelled and justified.

| ID | Topic | Required distinction / correction summary | Locator family |
|---|---|---|---|
| S1 | mol/µmol prefix | `1 mol = 10³ mmol = 10⁶ µmol` | Analit. p.7, SI table |
| S2 | Caesium isotope / symbol | `¹³³Cs`; avoid `¹³³Cz`; distinguish luminous intensity symbol | Analit. p.7 |
| S3 | SI definitions | Separate the course's pre-2019 definitions from current defining-constant framing | Analit. p.7 |
| S4 | mass and amount equation | `n=m/M`, `m=n·M`; `v` is not amount symbol | Analit. p.1 |
| S5 | Beer–Lambert | Separate absorbance from absorption; check coefficient symbol and units | Analit. p.1 |
| S6 | metrology terms | Separate precision, trueness, repeatability and closeness to reference | Analit. p.2 |
| S7 | class-B tolerance | State course convention; do not generalize without instrument standard/capacity | Analit. p.3; V |
| S8 | statistics and terms | Use `s`, explicit `t(α;n−1)`, standard error and confidence interval terms | Analit. p.4 |
| S9 | precision wording | Do not conflate significant digits and decimal places | Analit. p.5 |
| S10 | trailing zero | Disambiguate bare integer precision with scientific notation | Analit. p.5 |
| S11 | pipette illustration/caption | Reconcile shown instrument and 10 mL aliquot; preserve literal source quote (`ml`) | Analit. p.6 |
| S12 | Q3 titre | Retain/reject readings only under a stated criterion; recompute and explain | 2026 Q3 p.1 |
| S13 | term `skaitļi` | Prefer `zīmīgie cipari` | 2026 Q3 p.1 |
| S14 | Q2 concentration notation | Write quantity, amount and final volume with explicit units/precision | 2026 Q2 p.1 |
| S15 | Q7 calibration values | Recompute fit and identify extrapolation/limits | 2026 Q7 pp.4–5 |
| S16 | solvent vs final volume | State final solution volume to mark; distinguish added solvent | 2026 Q7 p.5; 2A Q5 p.2; V |
| S17 | half-life time units | Preserve significant figures; use day/days consistently | 2026 Q8 p.6 |
| S18 | graph axes/time origin | Label time and concentration with units; intervals begin from nonzero origin when shown | 2026 Q8 p.6 image [INSPECTED] |
| S19 | blank Q5 answer key | Mark proposed answer as addition, not course key | 2026 Q5 p.2 |
| S20 | wording/unit consistency | Fix direct/inverse proportion wording, repeated noun and mL case | Topic document p.1 |
| S21 | symbols | Distinguish `w`, `γ`, `c`, `M`; avoid reusing symbols with conflicting meanings | All sources |
| S22 | burette capacity | Check cumulative delivery against instrument capacity; refill or use suitable instrument | 2B Q2 p.3 |
| S23 | double rounding | Retain guard digits and round once: the cited density result should follow single-rounding logic | Analit. p.5 |

**Open policy flags:** lecturer has not confirmed V items. B03 reports exact-page S1–S23 reconciliation, but its suggested editorial closure is not applied until qualified review and correction of the S11 literal-quotation case.

## [LITERATURE-2026]

**New external literature intake.**

No 2026 external scientific literature has been primary-read into the hash-pinned source ledger in this workspace. Do not use the date in the section name to imply new literature was reviewed. Add a source only after obtaining a local copy, hash, exact edition/version, locator, read level, and claim-to-source support; record inaccessible items as `[UNVERIFIED]` with the technical limitation.
