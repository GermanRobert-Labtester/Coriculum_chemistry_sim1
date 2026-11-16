# Terminology and Source Provenance

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§3, 6, 9, 10  
Last updated: 2026-11-09  
Verification: `[INSPECTED]` `SOURCE_AUDIT.md`, `qa/verify.md`, `qa/trace.md`, `qa/e_registry.md`, `qa/terms_gate.md`; `[TESTED]` the Latvian terminology portal was queried live on 2026-11-09 (`qa/t22/portal_checks.csv`) and the bibliographic registry was gated on 2026-11-09 (`qa/sources_gate.md`, `qa/sources.csv`). The IUPAC Gold Book entries were read from archived snapshots (live origin returns a Cloudflare challenge); the course binaries were **not** rechecked.

## Source authority

Scope hierarchy: T13 defines outcomes; LEC provides theory; L25 is current titration procedure; L21 and L20 are supporting/older lab sources. An erroneous source statement is evidence of course wording, not authority for a false claim. External hierarchy: IUPAC standards/definitions, CRC Handbook, established textbooks, standards/peer-reviewed methods, Latvian terminology portal/AkadTerm. Snippets, Wikipedia, forums are leads only.

`[TESTED]` = command/measurement run with method and result; `[INSPECTED]` = read directly, not correctness; `[INFERRED]` = reasoned from evidence; `[UNVERIFIED]` = named check absent; `[TEXT-VERIFIED]` = source text/figure directly inspected for the claim; `[METADATA-VERIFIED / SCOPE-ALIGNED]` = identity/topic only. Never upgrade metadata, a search hit, a number match, or a green gate beyond its scope. No invented page, quote, edition, ISBN, DOI, URL, value, or Latvian term.

Source reading limitations: PDF extraction may flatten sub/superscripts; DOCX equations may be images. Inspect page images and reconstruct formulas before interpreting. Map each claim to `qa/trace.md` or label it `Papildinājums` with source. A Verify item remains `jāpārbauda`/`nav avotā` until evidence is in `qa/verify.md`.

## Terminology dictionary

`tools/termbase.py` is the live term authority (saved Task 04 counts: TERMS 31, SPECIES 12, CONTRASTS 6, USAGE 17, GATE_ROWS 14; current counts not rerun). Add a canonical term and gate row together.

| Concept | Canonical Latvian | Constraint / avoid form |
|---|---|---|
| Oxidation process/action | `oksidēšanās` / `oksidēšana` | Distinct meanings, not synonyms |
| Oxidation state | `oksidēšanas pakāpe` | `oksidēšanās pakāpe` is flagged; portal 2026-11-09: approved in LZA TK Terminoloģija 7, the competing form only in the 1979 LPE thematic-list project |
| Redox system / half-reaction | `oksidēšanās-reducēšanās sistēma`; `pusreakcija` | Couple members are not roles |
| Agents | `oksidētājs`; `reducētājs` | Oxidant accepts electrons and is reduced |
| Potential/electrode | `standartpotenciāls E°`, `E°′`; `standarta ūdeņraža elektrods (SHE)` | Keep E°, E and E°′ distinct; electrode ≠ couple |
| Method/amount | `jonu-elektronu (pusreakciju) metode`; `molārā koncentrācija c(X), mol/L`; `ekvivalences skaitlis z` | Oxidation-number method is a supplement; z ≠ n |
| Titration | `titrants`; `analīts`; `ekvivalences punkts`; `titrēšanas beigu punkts` | Equivalence ≠ observed endpoint; analīts ≠ analīze |
| Volumetric methods | `tilpuma analīze (volumetrija)`; `titrimetrija`; `permanganatometrija`; `jodometrija`/`jodimetrija`; `dihromatometrija` | Iodometry uses thiosulfate titrant; iodimetry uses iodine titrant |
| Confusable species | `MnO₄⁻`/`MnO₄²⁻`; `CrO₄²⁻`/`Cr₂O₇²⁻`; `S²⁻`/`SO₃²⁻`/`SO₄²⁻`; `NO₂⁻`/`NO₃⁻`; `S₂O₃²⁻`/`S₄O₆²⁻` | Pair Latvian word, formula, charge and state |
| Hydrogen/biochemistry | `H⁺ (aq)`; `H₃O⁺` only when water is explicit; `enzīms`, `ATF` (`ATP` once), `ADF` | Expand abbreviations once |
| Labware/salt/Faraday | `birete`, `Erlenmeijera kolba`, `mērkolba`, `Mora pipete`, `Mora sāls`, `Faradeja konstante` | portal 2026-11-09: `Mora sāls` approved, `Mora pipete` ambiguous (D6 open); `Faradeja konstante` approved (Rolovs 1989, with `Faradeja skaitlis` as an approved synonym) |
| Amphoteric redox | `amfotēriska viela`, `abējādas lomas` | Avoid “amfotērisks pāris” |

## Conflict log

| ID | Conflict / evidence | Status and rule |
|---|---|---|
| A3/A9 | Cr₂O₇²⁻ potential: course 1.33 V, CRC dump 1.232 V, LibreTexts page 1.36 V — three values, different conventions/reactions | Keep course value with qualification; do not call external comparison settled (T03 recorded all three in `qa/sources.csv`) |
| A11 | Pink persistence: LEC 1–2 min, LEC 1 min, L25 “does not disappear” | Show source criteria; follow instructor; no universal time. The IUPAC “titration” entry (T06387) says nothing about persistence time |
| A24 | Zn²⁺ listed among redox cofactors | Distinguish structural/Lewis role from redox-active cofactors; source warrant incomplete (no inspected source proves the structural role) |
| A25 | H₂ on Pt described as dissolving; Pd absorption distinction | Correction is present in historical evidence, but CRC/LibreTexts dumps do not prove claim; still unre-checked in 2026-11-09 |
| A26 | SHE stated as `[H⁺]=1 M`; activity convention | **Partially closed 2026-11-09**: Gold Book S05917/S05912/A00113 read (archived snapshots) — S05917 defines the SHE as the universal reference electrode whose H⁺/H₂ potential is zero at all temperatures, but **no inspected entry states “a(H⁺)=1, p(H₂)=1 bar”**; the activity wording keeps its course/general-literature attribution |
| A27 | S(+4), O(−2) in covalent compounds | Label as formal oxidation-number bookkeeping, not real ions |
| D6 | L25 prose says 10.00 mL “Mora pipete”; drawing shows 25 mL bulb pipette | Drawing mismatch recorded; Latvian local instrument naming unresolved |
| H-11/H-12 | O₂/haemoglobin wording and E°′ pH/temperature conditions | E°′ pH 7.0 condition is now text-verified (sample 8.1 table footnote, `qa/verify_bio.txt` L394); the O₂/haemoglobin wording still has no inspected passage |
| H-17 | AkadTerm wording for `oksidēšanas pakāpe`, `Faradeja konstante`; activity definition | **Portal part closed 2026-11-09**; the Gold Book text was read on 2026-11-09, but it does not supply the activity convention — the SHE note keeps its limitation |

Other source findings A1–A27, notation B1–B12, typo list C, practice additions D, term decisions E, and misconceptions F remain in full in `SOURCE_AUDIT.md`, which this shard does not replace.

## Verified source registry

The machine-checked registry is `qa/sources.csv` (21 rows; gate
`tools/check_sources.py`, report `qa/sources_gate.md`). Each row carries the
identity, imprint, identifier, scope, conditions, inspected locator, access
date, provenance tag and limitation. The table below is the narrative view;
the registry is authoritative.

| Source | Intended use | Evidence state recorded in workspace |
|---|---|---|
| `13 temata apraksts.pdf` (T13) | Topic scope/outcomes | `[TEXT-VERIFIED]` for the outline text (`qa/t13.txt`); `[METADATA-VERIFIED / SCOPE-ALIGNED]` for the identity — no author, publisher or year in the file |
| `Oksidesanas_reducesanas procesi_2022.docx` (LEC) | Course theory | `[TEXT-VERIFIED]` for the extracted text (`qa/lec.txt`); identity `partial` — no author or publisher metadata; equation images evade extraction |
| `6LW_MCh_Titration_Permanganatometrija_2025.pdf` (L25) | Current titration lab | `[TEXT-VERIFIED]` (`qa/l25.txt`); PDF author field is the account name “AgneseBr”; D6 open |
| `6LW_Ox-red_LV_2021.pdf` (L21) | Manganese media lab | `[TEXT-VERIFIED]` (`qa/l21.txt`); department line printed, no publisher; the “pusrekcijas” typo is recorded as a source form |
| `Oksidesana_reducesana_reakcijas_2020.pdf` (L20) | Older lab/worked reactions | `[TEXT-VERIFIED]` (`qa/l20.txt`); filename says 2020, PDF metadata says created 2021-10-14 |
| `qa/verify_crc.txt` / `.pdf` | Standard potentials | `[TEXT-VERIFIED]` for the values (Section 8 “Electrochemical Series”, Petr Vanýsek, p. 8-23 ff.); **identity `unresolved`** — the local copy is a TeamLRN e-book without a title page, so edition, year, publisher and ISBN stay blank |
| `qa/verify_bio.txt` / `.pdf` | E°′ biology values | `[TEXT-VERIFIED]` for Table 8.1 and its pH 7.0 footnote; **identity `unresolved`** — 19-page sample without title or copyright page; the download path’s “0072320419” is ISBN-shaped but unconfirmed |
| LibreTexts “Standard Reduction Potentials by Element” dump | Comparison only | `[TEXT-VERIFIED]`; the page gives Cr₂O₇²⁻ = 1,36 V — a third value next to course 1,33 V and CRC 1,232 V; the convention question (A9) stays open |
| `termini.gov.lv` / AkadTerm | Latvian terms | `[TESTED]` 2026-11-09, live JSON API: 30 queries, 12 hits in LZA TK collections, 10 hits in other approved collections, 6 not found, 2 ambiguous (`qa/t22/portal_checks.csv`) |
| IUPAC Gold Book (compendium) | Definitions/activity | `[TEXT-VERIFIED]` — the live origin answers a Cloudflare challenge, so six entries (T06387, E02188, E02096, S05917, S05912, A00113) were read from archived snapshots saved under `qa/t03/`; the print identity comes from the source’s own “Cite as” line (2nd ed., 1997, ISBN 0-9678550-9-8). **No inspected entry states the activity convention “a(H⁺)=1, p(H₂)=1 bar”.** |
| SIL OFL/font subsets | Embedded font licensing | OFL 1.1 is recorded; subset provenance must be checked before font changes |

For each external claim log claim, exact source identity/edition, locator, access date, result and limitation in `qa/verify.md`. Do not infer the edition of a dump from its filename.

## Literature 2026

A “2026” feature or source label requires a source actually dated 2026 and a text-level locator. Metadata-only records do not establish claim content. If a source cannot be fetched or inspected, retain `[UNVERIFIED]` / `jāpārbauda`; never invent a current citation.
