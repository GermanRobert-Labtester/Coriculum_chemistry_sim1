# Governance Changelog Archive

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §11  
Last updated: 2026-11-12  
Verification: `[INSPECTED]` existing AGENTS changelog; this archive stores entries that leave the rolling window and run-level audit trail.

## Archive rule

Keep the 10 newest run entries in `AGENTS.md` §11. Move older entries here without rewriting their meaning. Preserve closed-issue evidence here when an issue is later verified fixed; never close product issues based on this governance-only pass.

## History

## Run 2026-11-12 (F07)

The 2026-11-12 F04 row left the rolling §11 window when the F07 row was added on 2026-11-12 (AGENTS byte cap wins over retention). Moved verbatim:

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-12 | §2, §10, §11; F04 | T22→F04: pāru salīdzināšanas matrica — `Couple.comparability()` reģistra atvasinājums (E°+298,15 K+vienības aktivitātes = jā; atrunas: CRC identitāte pbo2/br2/o2h2o, pH robeža mno4h/cr2o7, vides nozīme mno4n/mno4b/alo2; trūkstoši nosacījumu lauki → «nosacījumi nav pilnībā salīdzināti»); 4.9 `#compare-matrix` ar 4.5. tabulu `#couple-matrix` (25 pāri pa vienam, E° caur `e_html` → `a.value-ref` 13.F.3), natīvie filtri (vide ×4, pH jutīgi, «ar atrunu») ar `:has()` AND kombinatoriku, druka dod pilnu tabulu neatkarīgi no filtra; vārti `check_couple_matrix.py` + 4 fiksētie, reģistrēti `check_all.py` | F04 pilots (RECOMMEND ADOPT pēc T05/T09; T09 atlikusis H-13 neatkarīgs no tabulām) — salīdzināmības verdikts ir vienīgais saturs, ko 4.4/5.1/13.A nesniedz | Master 1,784,351 B `16f51ada…4d287` → 1,818,099 B `9b3a3433…42424` (+33,748 B; JS 0 — exec 66,582 B/1,287 līn./sala 60,439 B nemainīgi); vārti 17/20 zaļi (sarkanie = JS-01/02/03 + CSS-02 + H-06 kā ierasts); fiksētie 5/5; falkon 12 PNG (1440/768/390 bez pārpildes, filtri 13/2/12/25 rindas, bez-JS, fokuss, 0 resursi, printa emulācija) + labošanas kārta (Statu/ss, −0,0592 pārlauzumi → nowrap + `.num`); Chromium (apstiprināts šajā ātrā) `qa/f04/master.pdf` 167 lpp. no frozen kopijas, matrica 25.–27. lpp., atbildes/veidnes spot-check; `qa/f04/`, `qa/design.md` Task 42, `qa/verify.md` F04, `archive/master.pre-f04.20261112-1933.html`; release PDF joprojām novecojis (H-06); mācību izmēģinājums (DoD) — gaidā, atklāti deklarēts |


The 2026-11-11 T18 row left the rolling §11 window when the T20 row was added on 2026-11-12 (AGENTS byte cap wins over retention). Moved verbatim:

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-11 | §2, §10; H-03, H-07, H-14 | T18: izrunājamas vienādojumu etiķetes + 24px mērķi — `build_master.py` `speakable()` latviešu etiķetes no strukturētiem tokeniem (`^2-`→"2 mīnus", `->`→"veido", `⇌`→"ir līdzsvarā ar"; Unicode nemainīgs); `raw_reported_block()` tabulai `aria-label`; master.css 24px minimumi px vienībās (sakne 15px): `.eq-copy` (178×), `.ref-table a`, `input[type=range]`, `.weak-filter`, `.rad-list a`, `.set-toc a`; `.audit-toggle-wrap label` inline-flex→bloks (iepriekšējs defekts: 1-zīmes kolonnas); vārti `check_a11y_names.py` + 6 fiksētie | H-03 (164/200 ar `^`), H-07 (6 nenosauktas), H-14 (178 ≡ `.eq-copy` 36.1×21.8) | Master 1,659,308 B `c258bec5…414b7cb` → 1,666,930 B `95bb5423…5b64` (+7,622 B; CSS +432 B); vārti zaļi (a11y-names, anchors, audit-banner 5/5, search/svg/claims/sources/terms/numbers/ox-state/balance/recall); 0 `^ _ ->`, 86/86 tabulas, 9/9 SVG, 0 sub-24px 390/768/1440 (inline saites = 2.5.8 izņēmums); CDP ģeometrija + 321 soļu Tab eja + 7 PNG apskatīti; `qa/b03/`, `qa/a11y_names_gate.md`, `qa/a11y_fixtures/`, `qa/verify.md` T18, `qa/design.md` Task 38; release PDF novecojis |

## Run 2026-11-11 (T19)

The 2026-11-11 T17 row left the rolling §11 window when the T19 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-11 | §2, §10; H-02 | T17: ID/fragments/ARIA integritāte — `build_master.py` `_dedupe_prov_ids()` piešķir atkārtotajiem provenance ankeriem pēc secības sufiksus (`prov-a22-2/-3`, `prov-a15-2`), `data-claim` stabils; B12 `ch_anchor` `"ch0"`→`"sakums"` ar etiķeti "0. nodaļa"; jauni vārti `check_anchors.py` (duplikātu ID, fragmenti, ARIA/`headers` IDREF, `MODE_HASHES` reģistrs `#audit`) + 5 fiksētie (valid iziet; duplikāts/fragment/ARIA/mode-hash-not-blanket neiziet) | H-02: dublēti ID (prov-a22 ×3, prov-a15 ×2) un divi bojāti `#ch0` linki no 13.E.2 rindas B12 | Master 1,659,296 B `427d90e9…df2f8` → 1,659,308 B `c258bec5…414b7cb` (+12 B); vārti zaļi (anchors PASS 553/553, audit-banner + 5/5, search, svg 9, claims 140, sources 21, terms 0, balance 69+116, ox-state 0, numbers 86, notation 0, recall 66.47 %); falkon CDP 12 scenāriji (tiešie URL fragmenti, claim-link→chlog rinda, back/forward, B12→`#sakums`, print) + 5 PNG apskatīti; no-JS fragment skrols un sintētiskā Tab fokusfiksēti kā engine warrant limiti; `qa/b02/`, `qa/anchors_gate.md`, `qa/anchor_fixtures/`, `qa/verify.md` T17, `qa/design.md` Task 37; release PDF novecojis pēc hash |

## Run 2026-11-07

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-07 | §§1–12; all five shards | Rebuilt the executive contract as a 12-section routing hub; offloaded issue forensics, CSS/DOM rules, Python/TS/JS audit, terminology/source provenance, and changelog policy. Refreshed static master findings; no product or source code changed. | Correct the AGENTS byte-cap breach and install the requested two-tier governance topology without losing constraints. | `[TESTED]` AGENTS 26,008 B pre-run; master 1,456,650 B, SHA-256 `a081c593f56b136cc1974ef2f33e283f505a483edd562a0e3c472d9bc0258e5f`, mtime 2026-11-03 10:20:40.754010335 +0200 unchanged; static parser findings in `OPEN_ISSUES_LEDGER.md`; final shard telemetry recorded below. |

Verification snapshot before this archive note: `AGENTS.md` 20,210 B; shards: `ARCH_CSS_DOM_CONTRACTS.md` 7,350 B/89 lines, `CHANGELOG_ARCHIVE.md` 1,365 B/21 lines, `INFRA_PYTHON_TS_JS_AUDIT.md` 10,545 B/105 lines, `OPEN_ISSUES_LEDGER.md` 19,771 B/250 lines, `TERMINOLOGY_AND_SOURCES.md` 7,326 B/72 lines. `[TESTED]` After the note, all five shards are non-empty; 70 Markdown shard links/anchors resolve to the five canonical targets; all 12 numbered AGENTS sections contain retrieval triggers.

## Run 2026-11-09

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§3, 4, 6, 9, 11, 12; `OPEN_ISSUES_LEDGER.md` | Product pass T02: termbase schema split into `decision_lv` / `note_en` / `source_ids` / `status`; 32 Latvian term decisions; maintainer register `qa/termbase_notes.md`; live Latvian terminology portal check (`tools/check_portal_terms.py` → `qa/t22/portal_checks.csv`); language gate and schema check in `tools/check_terms.py` with four fixtures. H-08 moved to repaired. | Visible maintainer English in the term cards and statuses that claimed more authority than the evidence supported. | `[TESTED]` master 1,462,562 B, SHA-256 `58c70bb004671838b2982063cf63445836a738db509d281e4391ad557ead970b`; English hits 32 → 0 (`qa/t22/english_hits.csv`); termbase schema problems 0; portal queries 30 (12 LZA TK hits, 10 hits in other approved collections, 6 not found, 2 ambiguous); 11 gates green; print control 130 → 130 pages with one changed line on p. 71; Firefox screen shots at 390/768/1440 and print pages 71–72 inspected; `qa/design.md` Task 22, `qa/verify.md`. |

Closed-issue evidence preserved here for **H-08**: the visible `.term-decision` prose is
Latvian in all 32 cards, the English maintainer register lives in
`qa/termbase_notes.md`, and the gate blocks a regression
(`tools/check_terms.py --fixtures`, 4/4). The open status of H-09, H-11, H-13,
H-15, H-16, H-17 and H-18 is unaffected; the IUPAC Gold Book was still not
fetched, so the activity definition keeps its “not live-verified” note.

## Run 2026-11-09 (T03)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§2, 3, 4, 9, 10, 11, 12; `TERMINOLOGY_AND_SOURCES.md`, `OPEN_ISSUES_LEDGER.md` | Product pass T03: bibliographic registry `qa/sources.csv` (21 rows); claim warrant fields `system_scope`, `conditions`, `warrant_limit`, `provenance`; `tools/check_sources.py` with three fixtures; `tools/fetch_iupac_goldbook.py` writing the Gold Book evidence files; 13.D rendered as plain citations that print as text. | A source name or a matching number cannot prove the passage, the edition or the applicability of a claim. | `[TESTED]` master 1,462,562 B → 1,469,757 B, SHA-256 `58c70bb0…` → `a615c2d3…`; sources gate PASS (21 sources, 16 text-verified, 128 claims), fixtures 3/3; claims/terms/numbers/balance gates green; IUPAC entries T06387, E02188, E02096, S05917, S05912, A00113 read from archived snapshots (live origin: Cloudflare challenge); CRC and Campbell identity still `unresolved`; print 130 → 132 pages with the bibliography on pp. 101–103; `qa/verify.md` T03, `qa/sources_gate.md`. |

Closed-issue evidence preserved here for **none**: T03 closes no product issue.
H-09, H-11, H-17 and H-18 keep their open status with sharper findings — the
CRC and Campbell identities are still unrecoverable, the activity convention is
still not stated by any inspected IUPAC entry, and the rest of the claim ledger
still has no claim-to-source locator.

## Run 2026-11-09 (T04)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§2, 11; `OPEN_ISSUES_LEDGER.md` | Product pass T04: derived prose register `DERIVED_PROSE` + `Calcs.pbo2_ediff/_crc` in `tools/master_data.py`; 4.4 "Sekas" wording derived from registry operands (0,34 V / 0,345 V); 12.4.2 rounding defect 8,629 → 8,628 g with registry row `st2.gL_raw` and change-log A28; five 13.F rule strings de-literalised; 4.7 ΔG° shows the J→kJ step; `tools/verify_numbers.py` extended with `check_derived_prose`, a line-by-line visible-arithmetic scan and a fixture suite (`qa/numbers_fixtures/`); `qa/numbers.csv` 77 → 80 rows; claims ledger regenerated (P029 retired, A28 added); arithmetic inventory `qa/t04/`. H-05 moved to repaired. | Prose differences must reproduce from stated operands and round once from unrounded intermediates. | `[TESTED]` master 1,469,757 B → 1,474,083 B, SHA-256 `a615c2d3…` → `53b80712…`; all gates green (verify_numbers 80 numbers + 2 derived prose, fixtures 2/2; claims 128 rows, fixtures 3/3; sources 21, fixtures 3/3; terms 0 problems; balance 69 equations; notation/ox-state clean); inventory: 185 visible arithmetic statements, 183 exact + 1 explained unit conversion + 1 change-log quote, 0 inconsistent; visual 390 px and print pages 17/20/78 inspected via user-approved headless Chromium (`qa/t04/shots/`, `qa/t04/master-t04.pdf`), Falkon/Xvfb painted blank pages even for a probe file; `qa/design.md` Task 24, `qa/verify.md` T04. |

Closed-issue evidence preserved here for **H-05**: the 4.4 "Sekas" cell is
derived from `pbo2.ediff` / `pbo2.ediff_crc` (`DERIVED_PROSE`), the gate
recomputes the difference from operand literals and the fixture
`qa/numbers_fixtures/inconsistent.html` fails with the historical defect shape.
The open status of H-06, H-09, H-11, H-13, H-15, H-16, H-17 and H-18 is
unaffected; T04 touched display rounding only and adjudicated no potential
conventions (T05 boundary respected).

## Run 2026-11-09 (T05)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §11 archive move | The two 2026-11-06 rows (four-language contract/issue ledger; screenshot-first policy) left the AGENTS rolling window to make room for the T05 row. | §11 keeps the 10 newest entries; AGENTS had to stay ≤24,576 B. | `[TESTED]` AGENTS 24,130 B pre-T05 → 24,486 B post-T05 (cap respected); master fingerprint changed by the T05 product pass, recorded in §11 row T05. |

| Date | Sections/shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-06 | §§1–12 | Four-language contract, JS/CSS/HTML issue ledger | Architecture and evidence boundaries | Historical inventory; not fresh acceptance |
| 2026-11-06 | §§7, 11 | Screenshot-first evidence policy | Ground visual claims | Prior Falkon/Xvfb capture failed; no screenshot |

## Run 2026-11-09 (T06)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §11 archive move | The 2026-11-07 hub-install row and the T01 row left the AGENTS rolling window to make room for the T06 row; both are preserved in `qa/t26/agents_archived_rows.md` and below. | §11 keeps the 10 newest entries; AGENTS must stay ≤24,576 B. | `[TESTED]` AGENTS 24,486 B pre-T06 → 24,568 B post-T06 (cap respected); master fingerprint changed by the T06 product pass, recorded in the §11 row T06. |

### Archived row: 2026-11-07 hub install

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-07 | §§1–12; five shards | Installed 12-section hub; offloaded specifications; refreshed static findings | Fit cap without losing rules | Master fingerprint unchanged; see `CHANGELOG_ARCHIVE.md#run-2026-11-07` |

### Archived row: T01

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§4, 9, 11, 12 | T01: claim ledger `qa/claims.csv` (128 rows), `qa/claims_method.md`, `tools/check_claims.py` + 3 fixtures; 5 overclaim sentences narrowed, 5 change-log rows corrected, banner counters computed from registry | Unregistered absolutes implied verification beyond the evidence | Master 1,456,650 B → 1,458,468 B, SHA-256 `a081c593…` → `6ca98de7…`; 8 existing gates + claims gate green; `qa/design.md` Task 21 |

## Run 2026-11-09 (T07)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §11 archive move | The T02 and T03 rows left the AGENTS rolling window to make room for the T07 row; both are preserved below unchanged. | §11 keeps the 10 newest entries; AGENTS must stay ≤24,576 B. | `[TESTED]` AGENTS 24,568 B pre-T07 → 23,750 B post-T07 (cap respected; two rows moved out, one T07 row added); master fingerprint changed by the T07 product pass, recorded in the §11 row T07. |

### Archived row: T02

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§3, 4, 6, 9, 11, 12 | T02: termbase schema (`decision_lv`, `note_en`, `source_ids`, `status`); 32 Latvian term decisions; maintainer register `qa/termbase_notes.md`; portal check `tools/check_portal_terms.py` → `qa/t22/portal_checks.csv`; language gate + 4 fixtures → `qa/t22/english_hits.csv` | Visible maintainer English in the term cards; unsupported `apstiprināts` statuses | Master 1,458,468 B → 1,462,562 B, SHA-256 `6ca98de7…` → `58c70bb0…`; english hits 32 → 0; schema problems 0; 11 gates green; `qa/design.md` Task 22 |

### Archived row: T03

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§2, 3, 4, 9, 10, 11, 12 | T03: registry `qa/sources.csv` (21 rows: identity, imprint, identifier, scope, conditions, locator, access date, provenance, limitation); claim fields `system_scope`/`conditions`/`warrant_limit`/`provenance` (A2–A5, A10–A13, A24–A27); `tools/check_sources.py` + 3 fixtures; `tools/fetch_iupac_goldbook.py` → `qa/t03/gb_*.txt`; 13.D prints plain citations | A source name or a matching number cannot prove the passage, edition or applicability | Master 1,462,562 B → 1,469,757 B, SHA-256 `58c70bb0…` → `a615c2d3…`; sources gate PASS (21 sources, 128 claims), fixtures 3/3; IUPAC text read via archived snapshots (Cloudflare 403 confirmed); CRC/CAMP identity still unresolved; print 130 → 132 pages, 13.D on pp. 101–103 inspected; `qa/verify.md` T03 |

## Run 2026-11-10 (T10) — archived rows T04, T05

Moved from `AGENTS.md` §11 during T10 because the byte cap (≤24,576 B)
was breached after the T10 row was appended and the rolling window held
only six rows — retention (keep 10 newest) and the cap could not both
hold. The two oldest full rows are preserved verbatim below; the cap
takes precedence, mirroring the 2026-11-07 cap-breach precedent.

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§2, 11 | T04: derived prose register (`DERIVED_PROSE`) + `Calcs.pbo2_ediff/_crc`; 4.4 "Sekas" wording now derived (0,34 V / 0,345 V, H-05 closed); 12.4.2 8,629→8,628 (A28); five 13.F rule strings de-literalised; 4.7 ΔG° J→kJ shown; `verify_numbers.py` + derived-prose check + visible-arithmetic scan + fixtures; claims P029 retired, A28 added; numbers.csv 77→80 rows | Prose differences must reproduce from stated operands; round once from unrounded intermediates | Master 1,469,757 B → 1,474,083 B, SHA-256 `a615c2d3…` → `53b80712…`; all gates green (numbers 80/2 prose, fixtures 2/2; claims 128; sources 21; terms 0; balance 69); visual+print via user-approved Chromium (`qa/t04/`); `qa/design.md` Task 24 |
| 2026-11-09 | §§2, 4, 9, 11, 12 | T05: condition metadata on every couple (type/T/pH/activities/reaction/source); registries `POTENTIAL_COMPARISONS` (8, mixed teaching-only) + `EPRIME_PARTICIPANTS`; conv/pH/T/medium attributes on value spans; 2.2 conditions matrix; boundary captions 3.3/3.4/4.3/4.4; 8.1 E°′ footnote (pH 7,0 quoted, T unstated; 0,6945 V unresolved, O₂/H₂O₂ lead recorded); gate `check_potential_conditions.py` (R1–R4) + 4 fixtures | E° alone cannot set direction at arbitrary pH/activities; mixed conventions only as destructive test | Master 1,474,083 B `53b80712…` → 1,486,201 B `2eaf59fd…ac7ef0`; gate PASS (28-row matrix), fixtures 4/4; full suite green; visual+print via user-approved Chromium (falkon blank; 12 shots no overflow; 133-pp PDF, 7 pp. inspected); H-04 fresh repro; `qa/design.md` Task 25, `qa/verify.md` T05 |

After the move: `AGENTS.md` within the cap; rows retained in `AGENTS.md`
§11: T06, T07, T08, T10.

## Run 2026-11-10 (T11) — archived row T06

Moved from `AGENTS.md` §11 during T11 because the byte cap (≤24,576 B)
left only 364 B of headroom against a full T11 row. Precedent: the T10
cap-breach note — the cap takes precedence over the 10-row retention rule
while the window holds fewer rows than the rule protects. The T06 row is
preserved verbatim below.

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §11; `qa/trace.md` | T06: 8 paskaidrojumi pārrakstīti ap mehānismu + robežu (`qa/design.md` Task 26); 4 NUMBERS rindas (`mn.ratio10.*`, `fe.e0*`); 13.E R5–R12; karte `qa/t26/explanation_map.csv`; claims 137 | Bez mehānisma apgalvojums nemāca, kāpēc rezultāts spēkā ir; katrs jauns teikums avots (LEC) vai Papildinājums; tikai proza, avota vērtības netiktas | Master 1,486,201 B `2eaf59fd…` → 1,507,096 B `c51c368f…faa3b27`; visi vārti zaļi (numbers 85, claims 137, sources 21, terms 0, balance 69+116, fiksētie gadījumi 2/2+3/3+3/3+4/4); Chromium (atļauts šajā izpildē; falkon atkal tukšs): 27 kadri bez pārpildes, 1 defekts labots; 138-lpp PDF, 6 lpp. skatītas; `qa/design.md` Task 26, `qa/verify.md` T06 |

After the move: rows retained in `AGENTS.md` §11: T07, T08, T10, T11;
`AGENTS.md` within the cap.

## Run 2026-11-10 (T12 — rows archived under the §11 byte cap)

AGENTS.md §11 was 26,279 B after appending the T12 row, above the 24,576 B
cap; per the archive rule the byte cap wins, so the three oldest rows were
moved here verbatim (no rewriting) and the T12 row was tightened. Product
pass, not governance-only; master after the pass: 1,558,739 B, SHA-256
`9f164461b690150a0461adb3c4930da74497ec07601e0f46f629c1ef6fa5aaa0`, mtime `2026-11-10 23:47:56.374735499 +0200`.

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-09 | §§2, 4, 8, 11 | T07: 24 prompti (11 spot + 13 saistīti) saņem atgāžu skaidrojumu no kļūdu atlanta kartēm (`study_data.py`); ekrānā `<details class="recall-feedback">`, drukā `.pa.feedback` (bez JS, vienreiz); `recall_matrix.py` → `qa/t07b/` režīmi + 4 fiksētie; claims P60–P62 | Segums nepierāda atgāžu kvalitāti | Master 1,507,096 B `c51c368f…` → 1,537,476 B `d6b9c0da…16627c`; 113/170 = 66,47 %; režīmi 11/39/24/44; dublikāti 0; fiksētie 4/4; vārti zaļi (claims 140); Chromium (atļauts): 8 kadri, JS-off |
| 2026-11-09 | §§2, 11 | T08: lasāmceļa audits (ch1/3/6/9/11): 228 atklājumi (0 dekoratīvu; T07 dublikāti saglabāti); norāžu labojumi — 6.nod. sadaļas 6.1–6.6 un 9.4 kā "N.M. sadaļa.", 12 pārceļi (piemērs/sadaļa), mirušās 0.1 kartes norādes (9.7/9.8/6.6–6.8/1.1–1.5/2.2–2.5/12.8) → esoši mērķi, A15 "5.5"→"5.1. sadaļā", kājene = būvdatums; vārti `check_number_refs`+`check_ch6_number_labels`+3 fiksētie; bez ķīmijas/avota izmaiņām | Lasītājs nevar atšķirt sadaļu no piemēra; mirušās norādes novirza | Master 1,537,476 B `d6b9c0da…16627c` → 1,537,747 B `a1054ec2…eeeb13`; vārti zaļi (claims 140, fiksētie 5/5); Chromium (atļauts): pārplūde 0 px 390/768/1440; JS-off; PDF 141 lpp, 6 skatītas; `qa/t28/` |

| 2026-11-10 | §§2, 10, 11 | T10: 7 SVG plaknes uz tokenu klasēm (0 krāsu/fontu atribūtu; `svg_type` 11/12/13/14 px; tokeni `glass/membrane/sediment/pink/pink-deep/copper`, `svg-flow-e/h`; 6 kontrasta pāri); ķīmijas labojumi pēc avota — 8.1 ķēde: I→III un CoQ→IV viltus ceļi dzēsti, II nav strupceļš, cit. c/O₂ pārcelti (LEC proza); 3.1: "[H⁺]" un "E, V" atmarķēti; 9.1: mērcilindrs ārā no statīva, vienzīmes pipete ar vidusbulbu (D6), skava, piliens `--perm`; vārti `check_svg.py`+5 fiksētie; H-13 SVG daļa aizvērta; labots T09 mantojuma defekts — `token_css()` neizdeva primitives (tokeni → melni) | Zīmējuma topoloģijai jāsakrīt ar avota prozu; krāsas tikai tokenos | Master 1,537,747 B `a1054ec2…eeeb13` → 1,541,054 B `c4931720…ee113e`; vārti zaļi (numbers 85, claims 140, sources 21, terms 0, balance 116, fiksētie 5/5); falkon: 1440/768/390/320 bez pārpildes, JS-off, pelēktoņa; PDF 144 lpp (Chromium tikai print-to-pdf, atļauts), 6 skatītas; `qa/t30/` |
Post-move telemetry: `AGENTS.md` 23 643 B; shards: `ARCH_CSS_DOM_CONTRACTS.md` 7 350 B, `CHANGELOG_ARCHIVE.md` 18 170 B, `INFRA_PYTHON_TS_JS_AUDIT.md` 10 545 B, `OPEN_ISSUES_LEDGER.md` 24 009 B, `TERMINOLOGY_AND_SOURCES.md` 9 955 B. `[TESTED]` sizes measured after the move; master hash/size/mtime recorded above.

## Run 2026-11-11 (T33 archive move)

| Date | Section(s) & shards | Change | Why | Evidence |
|---|---|---|---|---|
| 2026-11-10 | §§2, 10, 11 | T11: jauns statisks sešposmu SVG `fig-balance` ("6.1. attēls") 6.2. sadaļā — 6.1. piemērs (MnO₄⁻+SO₃²⁻, skāba; L20 p.1; LEC P089, P138) cauri vide→atomi→O/H→lādiņš→reizinātāji→summa; vienādojumi no `D.WORKED_BY_ID["6.1"]` (asserts LCM↔reizinātāji); uzsvari e⁻=give, H⁺/H₂O=take, saīsināmie izsvītroti; LCM punkti; 4. posmā nepareizais e⁻-puses gadījums (M03); atrunas A14/A15; `verify_numbers.py` "attēls" atzinējs+fixtures; 5 render/print defekti laboti pirms pierādījumiem | Ierobežojumi jāredz veidojamies; bilance nepierāda ticamību | Master 1,541,054 B `c4931720…ee113e` → 1,550,816 B `45ca0fb7…caed8`; vārti zaļi (svg 8, numbers 85, fixtures 5/5, claims 140, sources 21, balance 116+69, terms 0); falkon: 320/390/768/1440 bez pārpildes, pelēktoņa, no-JS; print PDF 146 lpp (Chromium tikai print-to-pdf): figūra sākumā pārsniedza lappuvi (sagriezta 5/6) — print cap `.balance-svg` 116 mm laboja, 36. lpp. vesela skatīta; T06 rinda → arhīvs (baits); `qa/t31/`, `qa/verify.md` T11, `qa/design.md` Task 31 |

Archived verbatim from `AGENTS.md` §11 during the T33 run: the new T33 row
pushed `AGENTS.md` past the 24,576 B cap; the byte cap wins, so the oldest
rolling row moved here without rewriting. `[TESTED]` AGENTS.md 25,343 B
before the move; master fingerprint `273dc6a6…8ab7c042` unchanged.

## Run 2026-11-11 (T34 archive move)

Adding the T34 changelog row (and the `searchIndex()` registry amendment in
§4) pushed `AGENTS.md` past the 24,576 B cap; per the archive rule the byte
cap wins, so the oldest rolling row (T32) moved here verbatim without
rewriting. Rows remaining in `AGENTS.md` §11: T33, T34.

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-10 | §§2, 4, 10, 11 | T12: 3.1. attēls (fig-ph) tagad ir nosacījumu apzīmēta plaksne — plaksnē nosacījumu josla ([Ox]=[Red]=1; p(Cl₂)=1 bar; 298 K), slīpuma etiketes ar 1 px līderiem (mn.slope 0,0947; jauns reģistra ieraksts cr.slope 0,138 V/pH; Cl₂ 0 V/pH), raustīta derīguma robeža pie pH 3 un ārpus domēna punkts kā atvērtais aplis pH 7 (mn.ph7 0,847 V, "formāli"); jauns statisks shematiskais fig-titr ("9.2. attēls") 9. nod. pirmās rozā piezīmē: teorētiskais ekvivalences punkts (raustīts, bezkrāsainajā zonā) pret novēroto beigu punktu (līnija pie krāsas pārejas), brakets "titrēšanas kļūda ≈ viena pilīte" (A10) un pārtērēšanas josla; L25 nesniedz līknes datus, tāpēc bez mēroga un bez skaitļu asīm; visi attēlotie lielumi no reģistra/D.Calcs; CSS: 6 jaunas klases esošos tokenu maršrutos; defekti (skat. qa/t32/notes.md): komentāru noplūde, etikešu sadursmes, ch9 dublēšanās | Nosacījumi un robeža jāredz uz plaksnes; ekvivalences/beigu punktu atšķirība līdz šim tikai prozā | Master 1,550,816 B `45ca0fb7…caed8` → 1,558,739 B `9f164461…f6aaa0`; vārti zaļi (svg 9 plaknes, numbers 86 + fixtures 5/5, balance 116+69, claims 140, sources 21, terms 0); falkon 320/390/768/1440, pelēktoņa, print media, no-JS, in-situ; print PDF 147 lpp (Chromium tikai print-to-pdf, atļauts), lpp. 16–18/64–65 skatītas; `qa/t32/` |
Post-move telemetry: `AGENTS.md` 24,396 B; shards: `ARCH_CSS_DOM_CONTRACTS.md` 7,350 B, `CHANGELOG_ARCHIVE.md` 21,520 B, `INFRA_PYTHON_TS_JS_AUDIT.md` 10,962 B, `OPEN_ISSUES_LEDGER.md` 25,436 B, `TERMINOLOGY_AND_SOURCES.md` 9,955 B. `[TESTED]` sizes measured after the move; master 1,658,590 B, SHA-256 `71b7656f…d4f2dc`, mtime `2026-11-11 19:36:46.057010829 +0200`.

## Run 2026-11-11 (T33)

Moved verbatim from `AGENTS.md` §11 rolling log by T35 (2026-11-11): the AGENTS byte cap (24,576 B) took priority over the 10-row retention rule; T34 remains the newest full row in the parent contract.

| 2026-11-11 | §§2, 11 | T33: atbrīvošanas PDF regenerēts un visas 142 lappuses pārbaudītas. Atradums 1 (būtisks, iepriekšējs kopš T09): `#print-answers` nekad nedrukājās — `@layer reset` nebija aizvērts, trīs `@layer print` bloki bija ligzdoti `@layer components` iekšpusē, un Chromium kārto slāņa paša deklarācijas PĒC ligzdoto apslāņu, tāpēc `.print-only{display:none}` uzvarēja drukas atkārtotas ieslēgšanas noteikumus (arī `.print-only-caption`, `.eq-copy`, `.notation-lens-bar`). Labots master.css: reset aizvērts, print bloki augšējā līmeņa `@layer print` faila beigās. Atradums 2: `overflow-wrap:anywhere` saspieda šaurās drukas tabulu kolonnas zem vārda platuma (7.2 "sk/āb/ā", galvenes "Vi de") — drukas šūnās tagad `break-word`. Manifests `qa/t33/manifest.json` (HTML+PDF SHA-256, 142 lpp., komanda, laiks) + validators `qa/t33/check_manifest.py` (stale-hash atteikums pierādīts); falkon ekrānuzņēmumi nemainīgi; visi vārti zaļi | Vecais `qa/master.pdf` (2026-11-09) atstāts kā vēsturisks; atbilžu lapa neparādījās ne T03/T12 eksportos, jo pilnā lappušu pārbaude nebija jebkad veikta | Master 1,558,739 B `9f164461…f6aaa0` → 1,558,991 B `273dc6a6…8ab7c042`; PDF `qa/t33/master.pdf` 4,396,525 B, 142 lpp., `ef28e79c…473b9` hash skat. manifestā; vārti zaļi (svg 9+5/5, numbers 86+5/5, claims 140+3/3, sources 21+3/3, terms 0+4/4, balance 116+69, notation 0, recall PASS); visas 142 lpp. inspektētas: atbildes 1× (87. lpp.), veidnes tukšas, vadīklas nav, secība OK; `qa/t33/`, H-06 → labots |

## Run 2026-11-11 (T34)

Moved verbatim from `AGENTS.md` §11 rolling log by T16 (2026-11-11): the AGENTS byte cap (24,576 B) took priority over the retention rule; T15 and T16 remain full rows in the parent contract.

| 2026-11-11 | §§4, 11; INFRA | T34/F01: offline meklēšana — `<dialog id="search-dialog">` ar priekšrenderētu 248 ierakstu sarakstu (77 virsraksti, 22 piemēri, 32 termini, 116 prompti; etiķetes burtiski no lapas), anonīms IIFE 1,337 B / 14 līnijas rezervē (reģistra rinda pārsaukta `searchIndex()`, bilance pret 4,096 B nemainīga), diakritiku salocīšana `fold_lv` = NFD + U+0300–036F (gate importē no build_master), statisks 13.H. Alfabētiskais rādītājs `#raditajs` (bez JS redzams, ar JS slēpts, drukā nav), ankeri `term-*`/`p-*` pirmajā renderējumā, pogas + / un Ctrl/Cmd+K, jauni vārti `check_search.py` + 5 fiksētie; `check_claims.py` (s-l/rad-list spoguļteksti, recall-item id caurspīdīgi ankeriem) un `verify_numbers.py` (meklēšanas konteineru atbrīvojumi) papildināti; atbilžu PDF nereģenerēts (falkon nav printToPDF; Chromium nav atļauts) — qa/t33/master.pdf novecojis pēc manifestā hash | Salocīto diakritiku meklēšana pārsniedz pārlūka find; F01 [RECOMMEND ADOPT] | Master 1,558,991 B `273dc6a6…8ab7c042` → 1,658,590 B `71b7656f…4f2dc`; vārti zaļi (search PASS + 5/5, numbers 86 + 5/5, claims 140 + 3/3, sources 21 + 3/3, terms 0, balance 116 + 69, svg 9, ox-state 0, notation OK, recall PASS); falkon cdp: dialogs atvērts/filtrēts 1440/390, Enter→3. nod., bultu fokusēšana, zero-results, no-JS 13.H 1440/768/390, print media bez meklēšanas, Tab-1 fokuss; fiksētie 5/5, vaicājumi 10+1; `qa/t34/` |

## Run 2026-11-11 (T15)

Moved verbatim from `AGENTS.md` §11 rolling log by T17 (2026-11-11): the AGENTS byte cap (24,576 B) took priority over the 10-row retention rule; T16 and T17 remain the newest full rows in the parent contract.

| 2026-11-11 | §11; qa/t35 | T15: ierobežota mācību paligu izvērtējums — KILL, produkts nav mainīts. Kandidāti: (1) biretes vizualizācija — dublē I4 iznākumu + `#l25-print` protokolu, nav warranta vizuālai simulācijai (A10/A11 risināmi tekstā), risks izdomātiem mērījumiem; (2) vājo vietu lapa — jau eksistē (18.C `#weak-panel`/`#weak-report`, atslēga `redox-unsure-v1` — vienīgais persistētais mācību stāvoklis); (3) koeficientu validācija — 6.4 kāpņu kartītes (`LADDER_PROMPTS`) jau dod produkciju + native `<details>` pašpārbaudi pār kanoniskajiem `WORKED` ID; mašīnvalidācija prasa jaunu reģistra funkciju pie JS-01 pārsnieguma (66,128 B / 1,357 līnijas). Atkārtotas atvēršanas nosacījums: JS-01/JS-03 laboti + reģistra amends TS `checkCoeff()` | Propozīcijas piezīmes ("nav vizuālas biretes / vājo vietu lapas") bija novecojušas pret pašreizējo būvējumu; savienots dashboard agregētu tikai vienu persistētu plūsmu, ko jau agregē vājo vietu panelis | Master pirms un pēc: 1,658,590 B `71b7656f…4f2dc`, mtime 2026-11-11 19:36 (nemainīgs); kartējums `qa/t35/workflow_map.md`, spriedums `qa/t35/evaluation.md`, evidence `qa/verify.md` (T15 sadaļa); §2 pirksta nospiedums atjaunināts uz T34 vērtībām; T33 rinda pārcelta verbatim uz `CHANGELOG_ARCHIVE.md` (baitu limits prioritārs) |

## Run 2026-11-11 (T16)

Moved verbatim from `AGENTS.md` §11 rolling log by T18 (2026-11-11): the AGENTS byte cap (24,576 B) took priority over the 10-row retention rule; T17 and T18 remain the newest full rows in the parent contract.

| 2026-11-11 | §2; H-04 | T16: audita joslas hidden semantika — bāzē uz T34 meistra utilities-slāņa `[hidden]{display:none}` jau uzvar `.js .js-only{display:block}` pēc slāņu kārtības; T05 defekta forma nav reproducējama. Laboti 2 stāvokļu trūkumi: `setAudit(false)` tīra `#audit` (`history.replaceState`; reload pēc aizvēršanas neatver, `#audit` atver), `html.audit-on` `scroll-padding-top` 3.5/5.5/8.75 rem; runtime 67,420→67,683 B (+263 B; JS-01 atvērts), CSS +443 B, bez `!important`/markup izmaiņām; vārti `check_audit_banner.py` + 5 fiksētie (injected visible-by-default neiziet) | H-04 vajag svaigu repro + akceptansa injected-tests nosacījums | Master 1,658,590 B `71b7656f…4f2dc` → 1,659,296 B `427d90e9…df2f8`; vārti zaļi (audit-banner PASS + 5/5, search/svg/numbers 5/5, claims/sources 3/3, terms 0, balance 116+69, ox-state 0, notation OK, recall PASS); falkon cdp 15 scenāriji 1440/768/390 + delayed-JS probe + 6 PNG apskatīti; `qa/b01/`, `qa/audit_gate.md`, `qa/verify.md` T16; release PDF novecojis pēc hash |

## Run 2026-11-11 (T19, moved 2026-11-12)

The 2026-11-11 T19 row left the rolling §11 window when the T21 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-11 | §2, §10; JS-04 refresh | T19: mijiedarbības stāvokļu ceļu uzmērīšana un sacietēšana — `qa/t39/interaction_map.csv` (26 virsmas, pilns izsaukums→DOM ceļš); 0 trūkstošu selektoru (77/77 id, 36/36 klases); noņemts miris dublētais `renumberTitres`; lēca un lab režīms → natīvs checkbox+`:has()` (bez `js-only`, strādā bez JS); I6 diagnoze → radio grupas ar ģeneratora `.is-key` un CSS ok/flag/details (karuselis paliek JS); labots vecs defekts: `.btn` padarīja izvēles stāvokli neredzamu; `redox-unsure-v1` sacietēšana (simbolu pārbaude, 400 caps, bojāts JSON→tukšs, novecojušu pid apciršana); vārti `tools/check_interactions.py` + 5 fiksētie | JS-04: "runtime was not traced live"; krātuve bez validācijas | Master 1,666,930 B `95bb5423…5b64` → 1,669,007 B `c40e10e3…ecd44d` (+1,482 B; JS −1,089 B; 27 innerHTML/9 createElement paliek T20) [T20: aste labota no `7020a`]; vārti zaļi (interactions + 13 exit 0; recall 66,47 %); falkon CDP S1–S4 (stāvokļi, pārlāde, korupta krātuve 4/4, pid apciršana, 0 tīkla pieprasījumi, bez-JS I6) + 4 PNG apskatīti; `qa/t39/`, `archive/master.pre-t19.20261111-2310.html`; release PDF novecojis |


## Run 2026-11-12 (T20, moved 2026-11-12)

The 2026-11-12 T20 row left the rolling §11 window when the T22 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| 2026-11-12 | §2, §10; INFRA-01 | T20 (tikai QA infrastruktūra + pārvaldība, meistars neskurts): vārti `lint_js_budget.py` (66,582 B / 1,287 r. / 7,611 % ar salu; sala 60,439 B nereģ.; innerHTML ×27, createElement ×9; 72 nereģ. fn), `lint_agents_size.py` (kaudze + ceļu integritāte), `check_contrast.py` (38/38 `contrast_pairs` apmierina grīdas; visi var() atrisināti; 1 raw literāls — backdrop skrimslis = CSS-02), agregāts `check_all.py` (izvadi tikai `qa/<task>/`) un `make_manifest.py` (artefaktu hash + PDF saistes novecojums + GOV-01 inventārs; `--check` neiziet); 8 vārtiem neobligāta `--report` pāradresācija; fiksētie 16/16 | INFRA-01: vārtu trūkums; AGENTS kaudzes limits (T18 arhivēta) | Master nemainīgs 1,669,007 B `c40e10e3…ecd44d` (mtime 23:08:22); AGENTS 24,549 B `b3de60d8…45b8ce` → 24,554 B; hash `qa/t40/evidence.md`; 14/17 vārti zaļi (sarkanie = JS-01/02/03 + CSS-02 + H-06); `qa/t40/` (evidence.md, manifest.json, vārtu JSON/MD); T19 aste labota `7020a`→`ecd44d` |


## Run 2026-11-12 (T21, moved 2026-11-12)

The 2026-11-12 T21 row left the rolling §11 window when the T22 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| 2026-11-12 | §10; F02 | T21: konteksta terminu saites — `tools/termref.py` kopīga politika: 10 pilotterminu pirmā tīrā vieta → glosārija enkurs `#term-*`; `analīts`/`jodimetrija` ar redzamu `(jāpārbauda)`; popover atmests (F02 kill), `analīze` izmesta (nav tīras agrīnas vietas); `.term-ref` master.css (printā melns teksts); bez JS; vārti `tools/check_term_refs.py` (byte-exakta) + 7 fiksētie + `check_all` `term-refs` | F02: termini parādās agrāk par glosāriju ch11; pirmās vietas bez JS | Master 1,669,007 B `c40e10e3…ecd44d` → 1,670,051 B `20b85439…f4a169` (+1,044 B; JS 0); vārti 15/18 exit 0 (sarkanie = JS-01/02/03 + CSS-02 + manifest drift/H-06; term-refs/anchors/search/terms zaļi); fiksētie 7/7; falkon CDP: klik→`#term-analīts`, atpakaļ→`#ch9`, fokuss redzams 768, bez-JS lietojams, print emulācija melns teksts, 390/1440 bez pārpildes + 8 PNG apskatīti; `qa/t21/` (evidence.md, manifest.json, PNG), `qa/termref_fixtures/`, `archive/master.pre-t21.20261112-1824.html`; release PDF novecojis (H-06) |


## Run 2026-11-12 (T22, moved 2026-11-12)

The 2026-11-12 T22 row left the rolling §11 window when the F04 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| 2026-11-12 | §2, §10; F03 | T22: vērtību pierādījumu paneļi — `ValueEvidence` reģistrs `master_data.py` (111 rindas = 25 COUPLES + 86 NUMBERS; reakcija, nosacījumi, avota/darba vērtība, noapaļošana, pārbaude, statuss), statiski `<details class="value-evidence" id="ev-*">` paneļi 13.F.3; katra reģistra vērtība korī (`e_html`/`num_ref`) ir saite `a.value-ref`; statusi source/corrected/verified/computed/convention/unverified; CRC/CAMP izdevumi vienmēr «nenosakīts», tukša pārbaude rāda «nav veikta»; `conditions_prose` pārēja uz decimālkomatu (B8); bez JS, sala nemainīga | F03: «kāpēc tieši šis skaitlis?» — avota vērtība, nosacījumi, noapaļošana un pārbaude vienā panelī; neatrisināta provenance paliek redzama | Master 1,670,051 B `20b85439…f4a169` → 1,784,351 B `16f51ada…4d287` (+114,300 B; JS 0; sala 60,439 B nemainīga); vārti 16/19 zaļi (sarkanie = JS-01/02/03 + CSS-02 + H-06 kā ierasts; terms/numbers sākumā sarkani → laboti ar `cite` klasi un decimālkomatu); jaunie vārti `value-evidence` zaļi + fiksētie 7/7; falkon CDP 8 scenāriji (klik uz 1,46 V → `#ev-pbo2`, paneļa lauki, Br₂/Cr₂O₇²⁻ apstrīdētie, 390/768 bez pārpildes, fokuss, printa emulācija atver paneļus melnā tekstā, bez-JS fragmens) + 9 PNG apskatīti; `qa/t22/` (evidence.md, manifest.json, scenāriji, PNG), `qa/valueevidence_fixtures/`, `archive/master.pre-t22.20261112-1902.html`; T20 rinda pārcelta verbatim uz `CHANGELOG_ARCHIVE.md` (baitu limits prioritārs); release PDF joprojām novecojis (H-06) |

The 2026-11-12 F07 row left the rolling §11 window when the F08 row was added (AGENTS byte cap wins over retention). Moved verbatim:

| 2026-11-12 | §2, §10, §11; F07 | Task 45 F07: 12.8 `#review-sheet` «izvēlies sešus jēdzienus» (A: 6 manuālas rindas; B: 6 jautājumi C01/C37/C41/C81/C131/C170 ar `#p-{pid}` saitēm; atbildes 12.7 / `#print-answers` vienreiz; C: 3 skeleti `strip_coeffs()` no 6.1–6.3 (skāba/neitrāla/bāziska vide), atslēga `details#review-key` drukā nākamā lapā; `data-eq-*` atvasinājuma pārbaudei; bez JS/krātuves); printa saspiešana — viena A4 lapa (9pt, 6 mm rindas); vārti `check_review_sheet.py` R1–R6 + 7 fiksētie, reģistrēti `check_all.py`; markUnsure audits: navigācija tikai nodaļas līmenī, `#p-{pid}` neizmantoti; bez izmaiņām | F07 pilots (REJECT IN FAVOR OF LEAN ALTERNATIVE) — analītika nav būvēta (kill saglabāti) | Master 1,818,099 B `9b3a3433…42424` → 1,826,786 B `37e1877c…b8d2a` (+8,687 B; JS 0 — exec 66,582 B/1,287 līn./sala 60,439 B nemainīgi); vārti 18/21 zaļi (sarkanie = JS-01/02/03 + CSS-02 + H-06); fiksētie 7/7; verify_numbers labošana (`.where` bez kailiem 6.x); falkon 7 scenāriji + labošana (bez pārpildes 1440/768/390, 6/6/3, bez-JS, fokuss, printa emulācija; C pārlauzās → saspiešana); Chromium (apstiprināts) `qa/f07/master.pdf` 170 lpp., lapa 89., atslēga 90., atbildes 91.; `qa/f07/`, `qa/design.md` Task 45, `qa/verify.md` F07, `archive/master.pre-f07.20261112-f07run.html`; release PDF novecojis (H-06); mācību izmēģinājums gaidā |
