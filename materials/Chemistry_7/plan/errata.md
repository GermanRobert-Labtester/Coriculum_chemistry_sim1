# Errata registry — B05 claim-repair subset

Machine-usable companion to the permanent errata journal (master ch. 15.c, entries
E1–E28; `src/16_ch15_labojumu_zurnals.part`). The journal is the canonical home of
the old wording (preserved verbatim inside `<span class="before">` quotes); this file
maps each claim-repair erratum to its **current** replacement sites with
file:line coordinates, so review can find what ships today. Errata ids are permanent
and never renumbered; historical wording is quoted only in the journal, never here.

Round created: B05/T03 (2026-11-12). Reviewer: CR (claim review).
Columns: `id | date | file:line (current site) | old claim (summary) | new wording (summary) | reason | source`.

| id | date | file:line (current site) | old claim | new wording | reason | source |
|---|---|---|---|---|---|---|
| E7 | 2026-11-02 | src/10_ch09_kompleksu_veidosanas.part:16 | Unique red particle asserted as [Fe(SCN)6]3− | Simplification declared; dominant red particle stated conditionally as [Fe(SCN)(H2O)5]2+; higher complexes form stepwise; speciation detail withheld (nav pārbaudīts) | Course equation is charge-balanced but speciation depends on conditions; conditions were not matched against literature (DOI 10.1016/j.ica.2016.02.052 metadata lead, full text unread) | S1 (course attribution) + NOSRC (CRB-05) |
| E18 | 2026-11-09 | src/08_ch07_novirzes_no_likuma.part:33; src/11_ch10_laboratorijas_darbs_6b.part:432 | Residual range used to imply linearity | Residuals attributed to the named fit (origin 9-point, max 0,0043 A); "saderīgi ar lineāru instrumentu, bet neizslēdz sistemātisku nobīdi, kuru ne R², ne atlikumi neredz" | Residual scatter cannot exclude a small systematic offset; R² is blind to it | S4 (data.py named fits; ISS-001) |
| E19 | 2026-11-09 | src/08_ch07_novirzes_no_likuma.part:13; src/06_ch05_transmitance_un_absorbance.part:75 | "R² = 0,99978 to izslēdz" / "linearitāte pati pierāda" | R² does not see a systematic offset; bandpass unknown; R² "diagnostiski atbalsta, bet nepierāda" | High R² is a diagnostic, never proof of homogeneity or validity | S4 (C-05; ISS-002) |
| E24 | 2026-11-09 | src/04_ch03_absorbcijas_spektrs.part:27; src/08_ch07_novirzes_no_likuma.part:29; src/11_ch10_laboratorijas_darbs_6b.part:7 | "Mērījumi veikti pie 440 nm — uz joslas plakanās virsotnes, tāpēc precīzs maksimums nav vajadzīgs" | 440 nm is the protocol setting; literature aqueous maximum 444 nm; whether 440 nm is on the flat part is not verified in this lab (ierobežots secinājums) | A literature maximum at 444 nm establishes peak location only; flatness at 440 nm requires a measured spectrum under matched conditions | R1 (Sheraz 2014) + S2 (setting); B05 added the explicit (E24) cross-links at the three sites 2026-11-12 |
| E25 | 2026-11-09 | src/06_ch05_transmitance_un_absorbance.part:78 | "krustpunkts ≈ 0 apstiprina, ka kalibrēšana der visā diapazonā" | Intercept +0,0017 A (free, 9 points) is a diagnostic, not a confirmation; calibration range bounded by the standards span | Near-zero intercept is consistent with, but does not prove, accuracy — blank offset and slope errors can compensate | S4 (C-05; ISS-002) |

## B05 round notes (2026-11-12)

- ST3.2.1 surgical edits: only three `(E24)` cross-link insertions
  (src/04:27, src/08:29, src/11:7). No numbers, citations or course instructions
  changed; all computed values untouched (verified by `build.py --check` +
  `numbers_trace.py` after rebuild).
- ST3.1 matrix rows: `plan/claim-ledger.csv` CRB-01…CRB-05 (reviewer CR) record the
  claim/source/applicability verdict per flagged site (unsupported as written →
  conditional replacement; CRB-05 keeps the E7 caveat verbatim because protocol
  conditions cannot be matched to the un-read DOI).
- Guard: `tools/claim_lint.py` (run.sh verify step) fails on regressions of these
  inference classes (flat-at-440 without qualifier, accuracy/validity proof claims,
  R²/intercept proof claims, unique mono-complex dominance, unqualified 444–445 nm
  range) at the source-part level.
