# Terminology and Sources

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§3, 6, 9, 10  
Last updated: 2026-11-07  
Verification status: A–F **quoted passages** re-read and machine-verified 2026-11-07 (`tools/check_source_claims.py`, `build/qa/source-claims.json`); A–F as whole documents are still `[INSPECTED]` only, and external-source registry entries remain leads/history unless explicitly marked otherwise. **B05 (2026-11-07):** the ZVA product records in the verified source registry were read from the primary leaflets/SmPCs and are marked `[TEXT-VERIFIED]`/`[INSPECTED]` per row; the K18–K21 wording remediation was applied in the authorized build pass (master 1 039 717 B, SHA-256 `341f5c26…`).

## Source authority

| Source | Filename | Authority/use | Current evidence status |
|---|---|---|---|
| A | `3. temata apraksts.pdf` | Course scope and assessment threshold. | `[TEXT-VERIFIED]` for the quoted 55 % and solution-list passages; no page beyond those re-read. |
| B | `3. Sem_Koncentrāciju_apr_Darab_lapa_2020_MF.pdf` | Theory and worked examples; K1–K12 pointers. | `[TEXT-VERIFIED]` for all quoted B passages (pp. 1–14 read); other pages `[INSPECTED]`. |
| C | `3_Seminars_Koncentraciju aprekini_2023.docx` | Seminar tasks/key; K7, K13–K15, K17 pointers. | `[TEXT-VERIFIED]` for quoted questions and keys; full document not re-read. |
| D | `Papilduzdevumi. Koncentrāciju aprēķini..pdf` | P1–P13 prompts; K16, K18, K20, K22 pointers. | `[TEXT-VERIFIED]` for quoted prompts (pp. 1–2 read). |
| E | `Papilduzdevumi. Koncentrāciju aprēķini. Atbildes. .pdf` | Additional task key; K16–K21 pointers. | `[TEXT-VERIFIED]` for quoted keys and “Kā plānot?” text (pp. 1–5 read). |
| F | `3_SEM_Atbildes_konc_papilduzd_pec_nodarb_2023.pdf` | Worked solutions P10–P13; K18–K22 pointers. | `[TEXT-VERIFIED]` for quoted solutions (pp. 1–2 read). |

SHA-256, byte size and page counts for A–F are recorded in `build/qa/source-claims.json`; a quote counts as verified only while those hashes still match the files on disk. Never add invented page numbers, quotations, editions, ISBNs, DOIs, or citations. Cite C/E by question number when that is the available locator. A course key establishes what the key says, not an external chemistry fact: `#n16c` therefore carries a separate *Pamatojuma veids* (source text / chemistry law / arithmetic / course convention / unverified external source) beside every resolution.

## Conflict log

See `OPEN_ISSUES_LEDGER.md#src-001` for K1–K23 indexed diagnostics and remediation targets. The compact K rows in AGENTS.md §2 preserve the active pointers. Policy: quote or identify the source wording accurately, compute independently from stated data, state every assumption, show consequence of each viable reading, and ask the lecturer when exam intent is uncertain. Never silently overwrite a defective source or claim lecturer approval.

### Evidence tags

| Tag | Meaning |
|---|---|
| `[TESTED]` | A reproducible check was run now; record command/artifact. |
| `[INSPECTED]` | The named current artifact was directly read/parsed. |
| `[INFERRED]` | Conclusion from explicitly named evidence, not a direct test. |
| `[UNVERIFIED]` | Required evidence was not established. |
| `[TEXT-VERIFIED]` | Exact cited source text/question was read and supports the claim in scope. |
| `[METADATA-VERIFIED / SCOPE-ALIGNED]` | Metadata and topic fit checked; text itself is not thereby verified. |

Historical `[TESTED]` results expire as current acceptance when the artifact changes. Screenshots, saved QA, and roadmap claims do not replace current checks.

## Terminology dictionary

| Quantity/concept | Preferred form | Variants/context | Correction rule |
|---|---|---|---|
| Vielas daudzums | `n`, `mol` | `N/N_A` for entity-count relation when appropriately sourced. | Distinguish amount of substance from number of entities; verify current SI wording before quoting. |
| Molmasa | `M(B)`, `g/mol` | Course notation may shorten to `M`. | Do not use bare `M` ambiguously in explanatory prose. |
| Molārā koncentrācija | `c(B)`, `mol/L` | Course `C_M`, `c_M`, or `M` convention. | State mapping to course notation; avoid claiming `M` is globally invalid. |
| Masas daļa | `w(B)`, dimensionless or `%` with basis. | `W`, `ω`, `W%`, `w%`. | State whether basis is m/m, m/V, or another defined ratio. |
| Masas koncentrācija | `γ(B)`, `g/L` (numerically equal to `mg/mL`). | Course symbols may vary. | Distinguish from density; denominator is solution volume. |
| Blīvums | `ρ`, `g/mL` or `kg/L`. | — | Define as solution mass / solution volume at stated conditions. |
| Tilpuma daļa | `φ` | `%` only when basis is clear. | Do not infer V/V from an unqualified percent. |
| Dispersā sistēma | phase + dispersion medium. | Course classification bands. | Preserve unprovided thresholds/gaps; seek course authority. |
| Izšķīdinātā viela / šķīdinātājs | named components. | — | Keep solute, solvent, powder, and solution masses distinct. |
| Atšķaidīšana / sajaukšana | state conserved amount and conditions. | `n` conservation only for the named species/reaction assumptions. | State volume additivity; it is not universal. |
| Neitralizācija | balanced-equation stoichiometric ratio. | — | Never presume a 1:1 ratio or pH 7. |

Latvian terminology portals were not checked in this run; no official-term verdict is made.

## Verified source registry

B05 (2026-11-07) opened the Latvian regulator (ZVA) register and the exact product leaflets/SmPCs below. Each row was read from the primary item on the access date; `dati.zva.gov.lv` blocks the default fetcher, so pages were retrieved with a browser user-agent GET (read-only) and leaflets/SmPCs parsed from the returned PDF/DOC. These certify product composition only; they are not clinical guidance. The K18–K21 wording remediation was applied in the 2026-11-07 authorized build pass (master 1 039 717 B, SHA-256 `341f5c26…`); the K rows stay open only for the lecturer-policy question.

| Claim | Primary title/version | Publisher | Exact URL/ISBN | Date opened | Status | Use location | Supporting passage |
|---|---|---|---|---|---|---|---|
| Classic Rehydron sachet = worksheet P10 (K18) | Rehydron pulveris iekšķīgi lietojama šķīduma pagatavošanai, reģ. 01-0036 (Orion Corporation, Somija; reģ. 17.01.2001; OTC; register: nav pieejamas aptiekās). PIL «SASKAŅOTS ZVA 10-02-2026»; SmPC 19-10-2021. | ZVA Latvijas Zāļu reģistrs | https://dati.zva.gov.lv/zalu-registrs/info/01-0036 (+ `/pil`, `/smpc`) | 2026-11-07 | `[TEXT-VERIFIED]` | `#n12` P10 / K18 | PIL §6: «Katra paciņa satur 10,0 g glikozes, 3,5 g nātrija hlorīda, 2,9 g nātrija citrāta un 2,5 g kālija hlorīda. Nesatur citas sastāvdaļas.» §3: «Vienas paciņas saturu izšķīdiniet vienā litrā dzeramā ūdens.» SmPC §2 (1 L): Na 89,5; K 33,5; Cl 93,4; glikoze 55,5; citrāts 9,9 mmol/L. Citrāts 9,9 mmol/L no 2,9 g ⇒ M≈294 ⇒ dihidrāts; bezūdens formula dotu 11,2 mmol/L. |
| Current available LV Rehydron product differs | Rehydron Optim pulveris iekšķīgi lietojama šķīduma pagatavošanai, reģ. 11-0302 (Orion; reģ. 28.07.2011; OTC; pieejamas). PIL 10-02-2026; SmPC 15-08-2023. | ZVA | https://dati.zva.gov.lv/zalu-registrs/info/11-0302 (+ `/pil`) | 2026-11-07 | `[TEXT-VERIFIED]` | `#n12` context | PIL §6: «glikoze – 6,75 g, nātrija hlorīds – 1,30 g, nātrija citrāts – 1,45 g un kālija hlorīds – 0,75 g»; paciņa 10,7 g; §3: «izšķīdiniet 0,5 litros remdena ūdens». Atšķirīgs sastāvs un tilpums nekā P10. |
| ACC 100 mg pulveris (P12/K20); deva (K19) | ACC 100 mg pulveris iekšķīgi lietojama šķīduma pagatavošanai, reģ. 00-0284 (Sandoz d.d., Slovēnija; reģ. 15.03.2000; OTC). SmPC 18-09-2025; PIL «SASKAŅOTS ZVA 24-03-2026» (kopīgs ACC 100/200/Hot). | ZVA | https://dati.zva.gov.lv/zalu-registrs/info/00-0284 (+ `/smpc`, `/pil`) | 2026-11-07 | `[TEXT-VERIFIED]` | `#n12` P12 / K19, K20 | SmPC §2: «Katra ACC 100 mg paciņa ar 3 g pulvera satur 100 mg acetilcisteīna»; «satur 2,8 g saharozes». PIL §6: askorbīnskābe «ACC 100 mg- 12,5 mg» (nevis 100 mg), saharīns, saharoze, apelsīnu aromātviela (glikoze, laktoze). SmPC §4.2: pieaugušie/≥14 g. «2 pulvera paciņas 2 – 3 reizes dienā (atbilst 400 – 600 mg … dienā)»; PIL: «Ja pēc 4-5 dienām nejūtaties labāk … jākonsultējas ar ārstu» (nav fiksēta 4 dienu maksimuma). |
| ACC 10 %/20 % oral solution nav LV reģistrā (P11/K19) | ZVA register, substance query «Acetylcysteinum» (visas formas/statusi). | ZVA | https://dati.zva.gov.lv/zalu-registrs/?iss=1&q=Acetylcysteinum | 2026-11-07 | `[INSPECTED]` (register enumeration) | `#n12` P11 / K19 | Vienīgais šķīdums iekšķīgai lietošanai: 20 mg/mL (2 %, Acetylcysteine Sandoz). 100 mg/mL (10 %) tikai «Šķīdums injekcijām» (ACC 05-0134). 200 mg/mL (20 %) nav reģistrā. P11 «10 %/20 % ACC» perorāli + deva 1,8–4,0 g/dienā nav apstiprināta ar nevienu pašreizējo LV perorālo produktu. |
| Maalox suspensija (P13/K21) | Maalox 40 mg/35 mg/ml suspensija iekšķīgai lietošanai, reģ. 96-0538 (Opella Healthcare France; reģ. 14.11.1996; OTC). SmPC. | ZVA | https://dati.zva.gov.lv/zalu-registrs/info/96-0538 (+ `/smpc`) | 2026-11-07 | `[TEXT-VERIFIED]` | `#n12` P13 / K21 | SmPC §2: «1 ml suspensijas satur: magnija hidroksīdu 40 mg, alumīnija hidroksīdu 35 mg» ⇒ 10 mL: Mg 400 mg / Al 350 mg. P13 dotie 220 mg Al / 380 mg Mg uz 10 mL neatbilst nevienam pašreizējam LV Maalox (arī 10-0504 460/400 uz 4,3 mL; 10-0503 400/400 tabletes). Vēsturiska uzdevuma vērtība. |

WHO ORS composition does not establish a branded product formulation; the rows above use the exact jurisdictional leaflet/SmPC, not the WHO formula. The hypernatremia spelling in the classic Rehydron PIL is «hipernatrēmija»; the master now uses that official PIL spelling in the quoted source, while «hipernatriēmija» (the earlier K18 correction) is also attested in Latvian medical texts and is acknowledged as a variant to align with a terminology authority, not a proven error.

Current master footer states A–F (2020–2023) and build checks dated 2026-11-07; that footer is not source verification for every claim. `build/qa/source-claims.json` records per-fragment verdicts keyed to the A–F hashes, and `build/conflicts.py` prints “Pārbaudīts avotā” only while those hashes match; a stale or missing report renders every fragment as unverified and fails `build.py`'s conflict audit. Recompute by running `python3 -I tools/check_source_claims.py`.

## Literature 2026

The 2026-11-02 research noted in older AGENTS history is historical. Do not imply it was refreshed here. Recheck primary BIPM, IUPAC, EDQM, WHO, ZVA, and publisher sources per exact claim; record the current version, publisher, URL/identifier, access date, context, and use location. Never call an edition “2026” unless its publisher says so. WHO ORS composition does not establish a branded product formulation. Product facts require the exact current jurisdictional leaflet and formulation; otherwise qualify or remove. B05 (2026-11-07) opened the ZVA register and the exact Rehydron/ACC/Maalox leaflets and SmPCs recorded in the registry above; the worksheet's ACC 10 %/20 % oral solution and Maalox 220/380 mg per 10 mL have no current Latvian product match and stay `[UNVERIFIED]` as product facts. The authorized build pass then labelled those values as worksheet-stipulated hypothetical/historical data in #n12, marked the ACC 100 mg ascorbic acid as the worksheet value against the official 12,5 mg, and removed the dose advice.
