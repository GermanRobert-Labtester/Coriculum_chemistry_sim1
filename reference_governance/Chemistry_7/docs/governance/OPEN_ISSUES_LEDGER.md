# Open Issues Ledger

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §2  
Last updated: 2026-11-12 (T03/B05; T02/B04; T19, T17)  
Verification: `[INSPECTED]` current workspace/HTML source; T01 (ISS-003), T02 (ISS-001/002/005 naming and overclaims), T03 (uncertainty/LOD/LOQ precision and boundary fixtures), T04 (ISS-011 terminology authority and drift lint), T05 (band-formation model: C46/C47 gates, erratum E27; supports OI-007 pillar work), T06 (Beer–Lambert derivation chain: T-before-A order, blank boundary + zero check, worked conversion, bounded failure modes in table 23, slope-basis bridge; C48 gate + `data.py derivation_audit()` mutation detectors), T07 (Lab 6B procedure made operationally explicit: full 2020-protocol + 2022-form extraction with row-by-row reconciliation `plan/protocol-extraction-T07.md`; six-step frame with completion criteria, blank zeroing vs composition vs calibration-line distinction, bench actions incl. the protocol's don't-touch-settings rule, ≥3 unknowns on 2–5 with sample-1 absence explained, dilution V₂ = total volume explicit; erratum E28 — the "taises" [sic] typo is in BOTH protocol files (300 dpi render inspected); C49 gate + 2 negative fixtures) product fixes recorded with strict-harness and fixture evidence; T13 (2026-11-11) closed ISS-020 (zero inline style attributes, C45/T10 lint, computed-style parity probe); T14 (2026-11-11) closed ISS-019/ISS-021: cascade layers + three-tier tokens landed with a dedicated architecture gate (`tools/gate_css_arch.py` G1–G8 + 11 negative fixtures), alias-resolving C16/C17/C29, rule-inventory parity proof and fresh screenshot/print evidence; T07 visual evidence: desktop 1280 px full page and §10.2/§10.3 captures inspected `[SCREENSHOT-VERIFIED]` (falkon via lite-shot; 390/768 px falkon captures hang — mobile coverage stays programmatic via C33); visual/print evidence for T04–T06 `[UNVERIFIED]`; instructor content review remains `[UNVERIFIED]`.

## Scope and closure rule

This is the forensic companion to the compact §2 index. Issue IDs are stable; do not renumber. Close only when source, rebuilt output, a failing check turned green, and any required human/visual evidence agree. A saved plan, old check, or this documentation is not closure evidence. Product findings below remain open; this run changed governance Markdown only.

<a id="iss-001"></a>
## [ISS-001] OI-01 — Residual range overclaims linearity

- **Category / target:** HTML defect; HTML + Python.
- **Location:** `#n10-7` (historical l.2085), `#n15-c` (l.3134); erratum E18; calculation authority `tools/data.py`.
- **Observed:** text uses “±0,003 A” residuals as linearity support. Saved calculation record gives maximum absolute residual 0.00431 A for origin fit and 0.0036 A for free 9-point fit; `sy=0.002644 A`. The displayed range is not a valid proof of linearity.
- **Blueprint:** recompute each named model; state residual range and model explicitly; remove “proves linearity” framing; align plot, E18 and check fixtures. Do not merge origin, free-9, and free-8 results.
- **Evidence:** `[INSPECTED]` AGENTS snapshot and `data.py` scope; exact fresh calculation not run here.
- **Update 2026-11-09 (T02):** residual attributions bound. §10.7 now reads “atlikumi no 9 punktu taisnes caur nulli ir haotiski, lielākais 0,0043 A — saderīgi ar lineāru instrumentu, bet nenovērš iespējamu sistemātisku nobīdi, kuru ne R², ne atlikumu izkliede neredz (E18, E19)”; 16. tabula tnote and 7.1/7.2 table cells attribute every residual to its named fit; “Ko šis darbs parāda” separates the free-9 R² diagnostic from origin-fit residuals and states accuracy is not established. Fresh recomputation matched all displayed values (origin max |res| 0,00431 A; free-9 0,00360 A; s_y 0,002644/0,002618). C43 lint blocks proof verbs on R²/residual/intercept without a diagnostic marker (2 negative fixtures); print pp 34/37 and 390 px renders inspected `[SCREENSHOT-VERIFIED]`. Residual linearity overclaim removed from live text; issue remains open only pending instructor content review.

<a id="iss-002"></a>
## [ISS-002] OI-02 — R² and intercept treated as validation

- **Category / target:** HTML defect; HTML.
- **Location:** `#n5-3`, table 23 rows 1 and 4 (historical l.1146, 1149); E19.
- **Observed:** R² `0.99978` is said to “prove” even absorber distribution and near-zero intercept to “confirm” validity.
- **Blueprint:** replace proof language with bounded diagnostics; discuss residual pattern, intercept, calibration range and blank treatment; explain that neither R² nor intercept establishes accuracy, homogeneity, monochromaticity or method validity. Reconcile E19 and add a negative claim fixture.
- **Evidence:** `[INSPECTED]` recorded source locations and existing issue dossier.
- **Update 2026-11-09 (T02):** table 23 (§5.3) rows 1 and 4 rewritten — R² now “diagnostiski atbalsta, bet nepierāda vienmērīgu sadalījumu”, intercept +0,0017 A “nepierāda, ka kalibrēšana der visā diapazonā — diapazonu ierobežo standartu apgabals” with new erratum E25 logging the old wording; §8.3 “Dziļāk” note retains the bounded reading; ch11 dl and the glossary “linearitāte” row now state compatibility-not-proof and the calibration-range boundary. C43 negative fixture kills an injected “R² = 0,99978 apstiprina, ka metode ir precīza un derīga”. 390 px t23 render and print pp 16/61 inspected `[SCREENSHOT-VERIFIED]`; issue remains open only pending instructor content review.

<a id="iss-003"></a>
## [ISS-003] OI-03 — 440 nm local-peak inference mislabeled as source

- **Category / target:** HTML defect; HTML.
- **Location:** `#n10-1` (l.1721), compare `#n3-2`, `#n15-d`, E20.
- **Observed:** “440 nm on the flat peak” is placed in an `avots` paragraph. The course setting is 440 nm; literature reports an aqueous maximum at 444 nm. Neither establishes local slope for the Lab 6B sample.
- **Blueprint:** separate protocol fact (440 nm), literature value (444 nm), and local-spectrum inference; label the inference as unverified unless matching sample spectrum, solvent/pH and instrument bandpass are established. Align E20.
- **Evidence:** `[INSPECTED]` workspace record; literature scope is carried from the source dossier, not re-extracted here.
- **Update 2026-11-09 (T01):** product fix applied. `#n10-1` now calls 440 nm the protocol/course setting; `#n3-2` and `#n7-2` attribute 444 nm to aqueous literature and label local flatness `nav pārbaudīts`; C-04 map added to `plan/terms-source.md`; E24 records the old wording. Rebuild 316,430 B, SHA-256 `b4c4c27a…`; harness 36/37 (C03 stale root allowlist: docs, roadmap, VISUAL_VERIFICATION.md, .cache). Print visual inspection and instructor review remain `[UNVERIFIED]`; issue stays open.
- **Update 2026-11-09 (T01 continuation):** harness repaired and extended, visual/print evidence attached. C03 allowlist now matches the AGENTS §2 governed inventory; new C38 claim map (n3/n7/n10/n15 carry setting+literature+`nav pārbaudīts`; E24 present) and C39 flatness lint (forbidden formulation caught in prose; 444–445 range allowed only inside the E20 erratum quote) with 2 negative fixtures. Print inspection found a real defect: the screen `.rail{width:220px}` overflowed the 56 mm print grid track and Chrome clipped trailing rail words (PDF word extraction: “bet liter”, “teiku”, “pieņē”); fixed with `width:auto;max-width:100%` in the print block. An orphaned Q9 source note produced a 66-character page 57; fixed with `.src{break-before:avoid}` + `#q9{break-inside:avoid}`. New C40 print margin-integrity check kills a reproduced defect build. Final build 316,859 B, SHA-256 `c73a9c2d…`; strict 40/40 PASS, 0 SKIP; selftest 31/31. Evidence: 390 px §3.2/§10.1 close-ups, desktop 1280 px, mobile 375 px, print pages 8/23/28/58/60 inspected as PNG (Falkon blank under Xvfb → `shoot.mjs` tiered Chrome fallback with logged reason, owner allowance this turn). Instructor content review remains `[UNVERIFIED]`; issue stays open.

<a id="iss-004"></a>
## [ISS-004] OI-04 — Claim-level evidence labels are not audited

- **Category / target:** Unverified; Python + HTML.
- **Location:** paragraphs in `#n0`–`#n15`; `tools/verify.py` C13.
- **Observed:** prior inventory counted 379 paragraphs, 140 tagged and 239 untagged; C13 checks frequency/known label spread, not whether each claim has the correct evidence class or source.
- **Blueprint:** build a claim-level inventory; distinguish claims from navigation, captions and non-claims; report missing/ambiguous tags with locations and negative fixtures. Do not “fix” by mechanically tagging every paragraph.
- **Evidence:** `[INSPECTED]` previous recorded inventory; not recounted in this run.

<a id="iss-005"></a>
## [ISS-005] OI-05 — Regression variants/counts conflict

- **Category / target:** Source conflict; Python + HTML.
- **Location:** `#n10-4` table 13 (l.1753–1765), `#n10-8`, `#n15-f` (l.3171), `tools/data.py:159–170`.
- **Observed:** free-fit table column corresponds to 9 points while `compute_samples_results` uses the 8-point fit. Blank inclusion and point count are not named consistently.
- **Blueprint:** name “origin 9-point”, “free 9-point including blank”, and “free 8-point excluding blank” wherever values appear; keep protocol readings separate from recalculated concentrations; add parity tests for count and labels.
- **Recorded values:** origin `k=30.3946 mL·mg⁻¹`, `SE=0.0926`, `sy=0.002644 A`, max `|res|=0.00431 A`; free-9 slope `30.24`, intercept `+0.0017 A`, `R²=0.99978`; free-8 slope `30.150`, intercept `+0.0028 A`, `R²=0.99972`; origin unknowns `0.00283, 0.00559, 0.00849, 0.01224 mg/mL`; protocol readings `0.0028, 0.0055, 0.0085, 0.0122 mg/mL` remain distinct.
- **Evidence:** `[INSPECTED]` recorded calculations and locations; recomputation not run this turn.
- **Update 2026-11-09 (T02) — closed for the naming conflict:** fresh recomputation confirmed the divergence and repaired it. `data.py` sample cross-check now uses the free-9 fit (matching t13/15.f); the free-8 fit is kept as a named blank-sensitivity diagnostic (`gamma_free_8pt`; sample 3 rounds to 0,0055 — fixed in invariants). 16. tabula is the canonical variant table (point count, blank inclusion, intercept rule, role row); t13 column renamed “γ (brīvā, 9 punkti)”; §8.3 names all three variants; 15.f attributes every value. C42 map + 2 negative fixtures; C43 lint; numbers.csv gained 3 needles (0,00279/0,00556/0,00847) via build reconciliation. Verified `[TESTED]` strict 42/42, 0 SKIP; `[SCREENSHOT-VERIFIED]` 390 px t13/t16 and print pp 30/35. Naming/parity conflict closed; broader claim-label audit (ISS-004) stays separate.

<a id="iss-006"></a>
## [ISS-006] OI-06 — Forced-colors and full contrast coverage missing

- **Category / target:** CSS architecture/accessibility; CSS + Python.
- **Location:** `src/00_head_masthead.part`; `plan/contrast.txt`.
- **Observed:** no `forced-colors` mode; saved `contrast.txt` does not prove WCAG 2.2 AA for every live component/state/theme/print combination.
- **Blueprint:** add forced-colors support; compute text ≥4.5:1 and large text/UI ≥3:1 from live tokens and actual component pairs in light, dark, high contrast and print; include focus, disabled and error states. Preserve non-color cues.
- **Evidence:** `[INSPECTED]` source and existing workspace record; no contrast computation performed in this run.

<a id="iss-007"></a>
## [ISS-007] OI-07 — Five-pillar concept map absent

- **Category / target:** Unverified/pedagogy; Python + HTML.
- **Location:** concepts across `#n0`–`#n15`.
- **Observed:** no per-concept mapping for Definition, Mechanism, Worked Example, Common Mistakes, Canonical Term.
- **Blueprint:** create a concept-to-evidence map with explicit exceptions; evaluate substance, not class-name presence; add missing pedagogical elements in product work and a report/fixture in Python.
- **Evidence:** `[UNVERIFIED]` coverage remains unassessed.
- **Update 2026-11-11 (T11):** map and gates delivered. `plan/concept-coverage.csv` maps 18 stable concepts (K01–K18) × five pillars = 90 rows; every EVIDENCE row is an `#anchor` + literal needle verified inside the anchor's span by the new read-only `tools/coverage.py` (pillar-appropriate structure checked per [FIVE-PILLARS-MARKUP]; 3 deliberate NA rows carry recorded reasons), and q1–q9 map 9/9. Harness gate C51 added with 2 negative fixtures (removed passage, retargeted anchor; selftest 56→58, all killed). Study routes added to the nav (three anchor sequences, screen-only, no-JS reachability captured); Q2/Q6/Q9 answer keys repaired with explicit alternative refutations (`plan/t11-q-audit.md`; G-15 audit table). Rebuild 335,714 B, SHA-256 `9c915dece3d0…`; strict 50/50 PASS, 0 SKIP; 390 px light/dark/no-JS + 1440 px inspected `[SCREENSHOT-VERIFIED]`; print 65 pp all inspected via 6 grids (Chrome fallback logged, owner allowance). Issue stays open only pending instructor content review; claim-level label audit remains ISS-004 scope.

<a id="iss-008"></a>
## [ISS-008] OI-08 — Claim-to-source ledger absent

- **Category / target:** Unverified/provenance; Python + HTML.
- **Location:** `#n15-d` l.3144–3156; supplements/source block.
- **Observed:** supplements are grouped broadly; no claim-level source ledger is present in the declared workspace inventory.
- **Blueprint:** add a deterministic claim→source record in a later authorized product/evidence pass; include source scope, page only if read, extraction method, status and claim IDs; do not invent citations.
- **Evidence:** `[INSPECTED]` recorded prior location/inventory.
- **Update 2026-11-12 (T19):** claim-to-source record delivered. `plan/claim-ledger.csv` (schema: kind, id, source, status, claim, scope, conditions, reviewer, date) maps C-01–C-10 plus CL-01–CL-16 to source IDs [R1]–[R10], [S1]–[S3], NOSRC and SKOLO with provenance tiers, scope and conditions; `src/16*` n15-d bibliography entries now carry the source-ID markers and refined status language (Skoog year resolved © 2018 per Cengage primary page; Gold Book definitions read 2026-11-12; Harris 10th ISBN 978-1-319-16430-0 confirmed; errata E1–E28 untouched), `src/15*` quick-sheet gained the [R1] pointer. New read-only gate `tools/lint_claims.py` (L1–L7: dangling claims, unregistered markers, status vocabulary, page-citation ban in the external bibliography, tier-tag consistency, C-01–C-10 completeness) with `--selftest` 7/7 fixtures killed and clean baseline, wired as run.sh step 2e. Evidence: `plan/claim-ledger.csv`, `plan/terms-source.md#t19-verify-log`, TERMINOLOGY_AND_SOURCES LITERATURE-2026 refresh — `[TESTED]` lint + web-record checks. Owner authorized the rebuild the same turn: `./run.sh --strict` exit 0 (51/51, 0 SKIP), master 340,520 B `797b3ff4…`; two print orphans created by the added text were fixed in `src/00*` (`#n15 .src-list` breakable with items atomic; `#n15-src` break-before removed) and the final print render is 66 pp with 0 thin pages, references pp 63–66 inspected; falkon CDP captures of n15/n15-d inspected `[SCREENSHOT-VERIFIED]`. Evidence: `plan/t19-claims-provenance.md`. - **Update 2026-11-12 (T03/B05):** claim/source/applicability matrix recorded. Ledger rows CRB-01–CRB-05 (reviewer CR) map the five B05 evidence sites (§3.2, §7.2, §10.1, table-23 R²/intercept rows, §9.2 speciation) to registered sources with per-site verdicts — all already conditional from E7/E18/E19/E24/E25, so no further wording repair was needed; DOI 10.1016/j.ica.2016.02.052 recorded as a metadata-only lead (full text unread; E7 caveat retained verbatim); `plan/errata.md` maps each erratum to current file:line; `tools/claim_lint.py` (P1–P5, 6 fixtures) guards the inference classes at source level as run.sh step v6b; three `(E24)` cross-links added (owner-authorized rebuild `0f6df864…`, strict 51/51). ISS-004/ISS-008 claim-label scope unchanged. - **Update 2026-11-12 (T09, lab-6b plan):** ledger schema harmonized to the T09 superset to the T09 superset (owner ruling: single-file ledger — no `plan/sources.csv`; src/16 prose names `plan/claim-ledger.csv` as the single claim+source map). New 14-column header `kind,id,citation,provenance,source_id,source_scope,conditions,claim_text_lv,chapter_anchor,applicability,status,reviewer,updated,next_action` (T19 `status` tier column renamed `provenance`, vocabulary unchanged; T09 `status` = support verdict enum `supported|conditional|unsupported|unresolved`, `unresolved` first-class with mandatory `next_action` restating recorded reopen conditions; contract `plan/ledger-schema.md` with derivation rules + recorded deviation). All 55 rows migrated with verbatim cell preservation (round-trip check in the migration run); `tools/lint_claims.py` L1–L7 semantics unchanged over the renamed columns (baseline PASS, selftest 7/7); new read-only gate `tools/ledger_lint.py` (R1 schema header, R2 referential integrity, R3 enums, R4 non-empty claim text, R5 unresolved→next_action; `--selftest` 5/5 killed, clean baseline; `--atlas-fields` prints the T14 public field-selection contract) wired as run.sh step v6d and registered in `tools/negative-fixtures.json`. No product byte changed — master `2b2ebdfc…` before/after.

Issue stays OPEN only pending instructor content review.

<a id="iss-009"></a>
## [ISS-009] OI-09 — `skolo.lv` figure lead scope unchecked

- **Category / target:** Unverified source; HTML + source review.
- **Location:** `#n15-src` l.3190; figure-2 URL.
- **Observed:** identity, content and scope alignment were not confirmed.
- **Blueprint:** verify source identity and exact figure scope before using; otherwise retain only as an explicitly unverified lead or remove in authorized product work.
- **Evidence:** `[UNVERIFIED]`.

<a id="iss-010"></a>
## [ISS-010] OI-10 — Responsive, SVG and print rendering unverified — CLOSED 2026-11-12 (T17)

- **Category / target:** Unverified visual/accessibility; CSS + HTML.
- **Location:** `#fig-T`, `#fig-beam`, `#fig-calword`, `#fig-cal`, residual SVGs, `#n15`.
- **Observed:** historical 2026-11-02 record notes seven SVGs horizontal-scroll at 390 px, three-line h1, and 58 print pages. No screenshot/PDF was captured or inspected in this run.
- **Blueprint:** after product work, capture 390/768/1440 px and relevant themes/states with `lite-shot` falkon then falkon; inspect each image directly. Render print and inspect every page. Chrome/Chromium requires explicit user allowance in the current turn. Keep this open until evidence is attached.
- **Evidence:** `[UNVERIFIED]` current visual status; historical observations are not fresh acceptance.
- **Update 2026-11-12 (T17) — CLOSED:** reflow repairs landed first (probe found page overflow at 195 px = 390 @ 200% zoom from the surviving `.rail` float/width, no overflow-wrap guard, then range-input min-content and `.mist dl` squeeze; repairs in `src/00*`; C33 extended to 195/390/768/1440 + long-word probe + fixture). Fresh render verified: lite-shot falkon 390/768/1440/195 light/dark/no-JS + Tab-focus captures inspected `[SCREENSHOT-VERIFIED]`; the historical "seven SVGs horizontal-scroll at 390" is now intentional localized overflow — all 40 scrollable regions are named, `role="region"`, keyboard-focusable (Tab probe), and C33 asserts no page-level overflow plus that a long word cannot widen the page. Print re-rendered (Chrome print-PDF, owner-allowed; lite-shot --print-pdf broken per recorded quirk): 66 pages inspected via 6 grids — white ground, expanded disclosures, no clipped or near-empty pages. Evidence: `plan/t17-reflow.md`, `plan/t17-probe-{before,after}.json`, `plan/t17-artifact-hashes.txt`, `plan/visual-evidence/`. Instructor content review remains `[UNVERIFIED]` (tracked separately).

<a id="iss-011"></a>
## [ISS-011] OI-11 — Latvian lexical choice “kivete” unchecked

- **Category / target:** Unverified terminology; HTML + source review.
- **Location:** `#n12-4` l.2637; `plan/terms-source.md`.
- **Observed:** “kivete” is an intentional house choice; dictionary/terminology authority check was not run.
- **Blueprint:** verify against an appropriate Latvian terminology source; until then call it house style, not official norm.
- **Evidence:** `[UNVERIFIED]`.
- **Update 2026-11-09 (T04):** queries run 2026-11-09 against Tēzaurs (MLVV/LLVV) and AkadTerm/IATE with URL+date log in `plan/terms-source.md` ([T04-QUERY-LOG](../../plan/terms-source.md)): `kivete` attested — MLVV (dsk. ģen. -šu, from fr. *cuvette*), LLVV 2. ķīm. “stikla trauks (optiskajā aparatūrā šķidrumu īpašību pētīšanai)”, AkadTerm EN cuvette → LV **kivete (IETEICAMS)** and EN cell → LV kivete (VVC ķīmijas kolekcija) — a source-supported house choice, explicitly not an official norm; `kuvete` absent from Tēzaurs (recorded negative); `absorbance`/`transmitance` absent from Latvian dictionaries (negative), IATE maps absorbance → LV “absorbcija” and transmittance → “caurlaides koeficients” — house-style status declared in product text. Product repairs: 12.2 note, 22. tabula row, 12.4 status paragraph, n15.d date + T04 note, ch5 rail; the new lint itself found two genuine “absorbcija”-as-quantity defects (§4.4 “to absorbcija var atšķirties par 0,001–0,01 A”, §10.8 “pie nulles koncentrācijas absorbcija ir nulle”) — both fixed to “absorbance”. `tools/lint_html.py` (T1–T9, quotes/errata excluded, NFC) wired as C45 with 2 negative fixtures; `[TESTED]` strict 44/44, selftest 42/42, lint baseline clean; build 322,797 B, hash `48b73ea9…`. Terminology-status part closed; visual/print evidence and instructor content review remain `[UNVERIFIED]`.

<a id="iss-012"></a>
## [ISS-012] OI-12 — Named audit specification and build prompt absent; roadmap present

- **Category / target:** Governance; Markdown only.
- **Location:** workspace root; `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md`, `Master_Final_Perfected.md`, `HTML_MASTER_BUILD_PROMPT.md`, `PROMPT_master_html.md`.
- **Observed:** current inventory finds the 35-task roadmap (138,254 B), `PROMPT_master_html.md` (22,487 B), but not the named `Master_Final_Perfected.md` or `HTML_MASTER_BUILD_PROMPT.md`. This supersedes the stale 2026-11-06 statement that the roadmap was absent. No `.git` repository is available here.
- **Blueprint:** use the existing roadmap only as the active proposal queue; do not treat it as authorization. Reconcile named absence if the artifact is later supplied. Do not create substitutes or edit the roadmap under this lock.
- **Evidence:** `[TESTED]` local `rg --files`/inventory and git response, 2026-11-07.

<a id="iss-013"></a>
## [ISS-013] OI-13 — Runtime JavaScript exceeds hard budget — CLOSED 2026-11-12 (T15+T16)

- **Category / target:** JS bloat; TypeScript + Python, with HTML/CSS migrations.
- **Location:** one inline script; source `src/17_tail_scripts.part`.
- **Observed:** 7,890 executable bytes, 162 content lines (163 if counting trailing newline convention), 2.514% of 313,828-byte HTML. Effective ceiling is `min(4,096 B, 100 lines, 6,276.56 B)=4,096 B`, exceeded by 3,794 B and 62 actual lines (63 by prior formatted-line convention).
- **Blueprint:** retain only registry J1–J5; TypeScript strict source then compile/minify; Python pre-render fixed cases; CSS/native HTML for theme/reveal/print. Enforce bytes, lines, percent and registry matching in a Python gate with negative fixtures.
- **Evidence:** `[TESTED]` read-only parser measurement 2026-11-07.
- **Update 2026-11-12 (T15+T16) — CLOSED:** fresh pre-gate measurement (`plan/t15-js-forensics.md`): 7,940 B / 162 lines / 2.357% on the 336,853 B T13 master; unregistered theme/mask/print blocks totaled 2,955 B — removal landed first (ISS-014/015/016). Registry runtime re-authored in strict TypeScript (`src/ts/j1_registry.ts`–`j5_boot.ts`, `tsconfig.json` strict:true; pinned tsc 7.0.2 + Node 24, `tools/compile_ts.mjs` compile-twice reproducibility proof) → payload **3,938 B / 5 lines / 1.173%** (`plan/t15-js-budget.json`, payload `d0d7d7f6…`). Gates: `tools/verify_js.mjs` rewritten (registry allowlist `$ fmt upd num s2` with exactly 3 `upd`, banned APIs + unregistered feature tokens raw-scanned, `--selftest` 5/5) and new read-only `tools/budget.py` B1–B12 (`--selftest` 14 negatives + positive control); wired as run.sh steps 0/2/2d. Build 336,093 B `6fad5d1b…`; strict 51/51, 0 SKIP. K6 resolved same day by owner ruling: aggregate byte ceiling raised 4,096 → 6,096 B (+2,000 B), J3/J4 per-hook caps 1,400/1,400 B ratified (measured floors 1,316/1,355 B with teaching microcopy + C36 parity intact).

<a id="iss-014"></a>
## [ISS-014] OI-14 — Theme toggle duplicates CSS state capability — CLOSED 2026-11-12 (T16)

- **Category / target:** JS bloat; CSS + HTML.
- **Location:** tail script block 1, 775 B / 23 lines; `#theme-toggle`.
- **Observed:** JS changes root `data-theme`, button text and `aria-pressed`; persisted state is prohibited.
- **Blueprint:** use labelled checkbox and CSS `:checked`/`:has()` theme rules; no persistence. Ensure keyboard and no-JS usability.
- **Evidence:** `[INSPECTED]` script source and live HTML.
- **Update 2026-11-12 (T16) — CLOSED:** control is now `<label class="theme-btn"><input type="checkbox" id="theme-toggle" class="visually-hidden">` with visible state text `.toff/.ton` swapped by CSS; dark tokens bound via `:root:has(#theme-toggle:checked)` (replaces the `data-theme` attr block in tokens/OS-dark/print contexts; gate G4 + verify C16/C17 regexes updated); forced-colors edge on `.theme-btn:has(:checked)`. No persistence, no script (verify C18 fails on any `theme-toggle` token in the script). Behavioural parity proven: behaviour.py asserts computed body ink flips `#1A1D21 ↔ #E8E6E1` and label display flips on click (40/40 hold, Chrome fallback logged); keyboard/focus = native checkbox + authored `:focus-visible` rules. 768 px light masthead + dark captures inspected `[SCREENSHOT-VERIFIED]`.
- **Update 2026-11-12 (T16b, same day, repair within the closed scope):** fresh T16 re-verification exposed an unrecorded hole in the acceptance "light/dark states remain reversible": under a dark system preference BOTH checkbox states resolved dark (OS-dark media block matched unchecked; the `:has(:checked)` block matched checked), so light was unreachable and the unchecked label offered an action already in effect. Probe captured pre-fix (`.cache/t16-probe/osdark_checked_falkon.png`, Falkon `--theme dark`, candidate copy). Repair (owner-authorized rebuild): the checkbox now **inverts the system preference** — OS-dark block re-scoped to `:root:not(:has(#theme-toggle:checked))` (residual never-set `data-theme` attr selector eliminated), manual dark re-scoped under `@media (prefers-color-scheme: light)` + `:has(:checked)`; prefers-contrast white-rule context split to the two page-dark states; `.toff/.ton` label inversion added under OS-dark. All four OS×checkbox states now reachable with coherent labels. Scanner coupling updated: verify.py C16 dmedia/dattr regexes + hc `#FFF` check now covers both dark-page contrast contexts; gate_css_arch G4 os-dark/toggle-dark regexes + G6 `contrast-toggle` context. Full matrix, edge note (spec `no-preference` OS would offer light-only) and evidence: `plan/t16b-osdark-theme.md`. Rebuild 336,947 B `cd36a5a6…`; strict 51/51, 0 SKIP; 4-state capture matrix + no-JS 390 px inspected `[SCREENSHOT-VERIFIED]` (Falkon); fresh print re-render not run (Chrome-only; print layer untouched, C32/C40/C35/C17 green). Issue remains CLOSED with the repair recorded.

<a id="iss-015"></a>
## [ISS-015] OI-15 — Recall masks use JS DOM state — CLOSED 2026-11-12 (T16)

- **Category / target:** JS bloat; HTML + CSS.
- **Location:** tail block 3, 1,075 B / 26 lines; `.mapinner`, `.mask`, `#recall-status`, `#recall-all`, `#recall-hide`.
- **Observed:** listeners reveal/hide masks, set inline visibility and update status text.
- **Blueprint:** use labelled static schematic, `<details>` or CSS `:checked` state; retain meaningful labels with JS disabled; remove JS-only masks/status controls.
- **Evidence:** `[INSPECTED]`.
- **Update 2026-11-12 (T16) — CLOSED:** each of the 7 masks is a `<label class="mask" data-for=…><input type="checkbox" id="mk-…" aria-label="Atzīme N: atklāt nosaukumu">?</label>`; the matching schematic label is revealed by `.mapinner:has(#mk-X:checked) [data-lbl=X]{visibility:visible}`; the single master control is `<label class="mask-all">` + `#recall-all` with `.instrument:has(#recall-all:checked) .mapinner .lbl`. The JS-only "Noslēpt no jauna" button and `#recall-status` live region were removed (CSS state discloses itself; the status text carried no unique information). Works without JS by construction (no `html.js` gate on masks); print shows all labels via the print layer. behaviour.py asserts computed `visibility` flips for a per-mask checkbox and the master (Chrome, logged); 390/1440 px + no-JS captures inspected `[SCREENSHOT-VERIFIED]`.

<a id="iss-016"></a>
## [ISS-016] OI-16 — Print handler mutates disclosure state — CLOSED 2026-11-12 (T16)

- **Category / target:** JS bloat; CSS + HTML.
- **Location:** tail block 6, 1,125 B / 23 lines; `beforeprint`/`afterprint` handlers.
- **Observed:** script opens all `<details>` before print and restores afterward.
- **Blueprint:** use print CSS that exposes disclosure content and labels without runtime mutation; verify support in the authorized print engine and inspect every page.
- **Evidence:** `[INSPECTED]`; product print output not rendered in this run.
- **Update 2026-11-12 (T16) — CLOSED:** print layer now expands disclosure content without script: `details::details-content{content-visibility:visible;display:block}` (new engines) plus `details > *:not(summary){display:block}` (older engines expose the child boxes) — the previous `data-was-closed` mutation attributes are gone. Verified in the authorized engine: Chrome print-PDF (fallback logged, owner allowance) renders **66 pages**, all inspected via 6 grids — Q&A answers, recap answers and terminology tables are visible on the white ground with no dark leak (C17 green). `beforeprint`/`afterprint` are banned tokens in the runtime scanners (verify_js + budget B5), so a reintroduction fails the build.

<a id="iss-017"></a>
## [ISS-017] OI-17 — Calculator behaviors exceed individual registry budgets — CLOSED 2026-11-12 (T15, with recorded K6 exception)

- **Category / target:** JS bloat; TypeScript + Python.
- **Location:** explorer block 2: 1,494 B / 29 lines; dilution block 4: 1,516 B / 26 lines; quality block 5: 1,629 B / 35 lines.
- **Observed:** values exceed J2 1,100 B/28 lines, J3 800 B/22 lines, J4 1,200 B/32 lines respectively. Existing explorer beam/dot DOM opacity updates are extra behavior needing explicit justification. Fallback parity is not proven.
- **Blueprint:** establish tested static tables from `data.py` as no-JS baseline; simplify residual controls to allowed calculations, implement in strict TS, minify, and keep per-hook budgets; update registry only with evidence that native/Python cannot serve the behavior.
- **Evidence:** `[TESTED]` block metrics; fallback parity `[UNVERIFIED]`.
- **Update 2026-11-12 (T15) — CLOSED with recorded exception:** strict-TS re-authoring + string-aware squeeze landed. Measured payload: J1 149 B (registry 150 ✓), J2 1,073 B (1,100 ✓), J3 1,316 B, J4 1,355 B, J5 45 B (200 ✓) — total 3,938 B / 5 lines / 1.173%. J3/J4 exceed their pre-implementation registry estimates (800/1,200) because the estimates were written before the clamping microcopy and the C36-asserted behaviors were costed; the floor with all user-visible strings and behaviors intact is 1,316/1,355 B. Provisional per-hook caps 1,400 B recorded in `tools/compile_ts.mjs` + `tools/budget.py` + INFRA; **K6 resolved by owner ruling 2026-11-12: aggregate byte ceiling raised 4,096 → 6,096 B (+2,000 B); the 1,400 B provisional caps stand as ratified** (alternatives on record, rejected: dropping warning strings loses C36 parity; trimming verdict text loses teaching content). Beam/dot opacity updates retained as justified J2 behavior (the figure's `desc` documents the dynamic state; static no-JS/print state is the 4-of-8-lit fallback, unchanged). Fallback parity now proven: static tables 10./15. render Python values (no-JS captures inspected), behaviour.py 40/40 asserts the JS values match.
- **Update 2026-11-12 (T04/B01) — K7 owner ruling:** the B01 input-contract fixtures (125 behaviour assertions; `plan/calculator-input-contract.md`) reproduced that J3 silently substituted protocol defaults for empty/malformed input with no status (18 contract violations; first failing assertion `j3 '1,5': invalid status is announced`). The surgical invalid-state branch (cleared outputs + pinned status `Nederīga ievade: ievadiet tilpumu.`, silent-default `num(e,d)` fallback removed) measured **1,453 B > the 1,400 B cap** with honest squeezing exhausted and all user-visible content intact → **K7: J3 per-hook cap 1,400 → 1,500 B** (recorded in `tools/compile_ts.mjs`, `tools/budget.py`, INFRA, AGENTS §4). Payload 4,075 B / 5 lines (J3 1,453, J4 1,355) — under the 6,096 B K6 aggregate; behaviour.py 125/125; strict verify 51/51, 0 SKIP; master 340,674 B `f0344a56…`.

<a id="iss-018"></a>
## [ISS-018] OI-18 — No-JS parity missing — CLOSED 2026-11-12 (T15+T16)

- **Category / target:** HTML defect; HTML + Python.
- **Location:** master; all three instruments/calculators.
- **Observed:** zero `<noscript>`; core reading remains static, but each JS instrument's useful fallback is not documented/proven.
- **Blueprint:** provide per-instrument static fallback (not merely generic text), use `<noscript>` where needed, add JS-disabled parity checks; no runtime network dependency.
- **Evidence:** `[TESTED]` zero `<noscript>` in current parser; parity `[UNVERIFIED]`.
- **Update 2026-11-12 (T15+T16) — CLOSED:** every instrument keeps its substantive static fallback (C20/B8 gate it): explorer → 10. tabula fixed-point table + static beam figure (4-of-8 lit); dilution → 15. tabula + worked formula note; quality → static readout defaults + uncertainty budget text; recall → schematic with masked labels that reveal by CSS checkbox (works without JS by construction). Instrument controls (`.controls`) stay hidden without the `js` flag; the theme control and masks are CSS-native and work with JS disabled. The "Bez JavaScript" fallback notes now state the mechanism (`fig-note` updated for recall). Evidence: falkon `--no-js` captures at 390/768 px inspected `[SCREENSHOT-VERIFIED]`; no `<noscript>` element was needed because every instrument region is fully static without the `js` flag (the registry payload only adds the continuous-input behavior).

<a id="iss-019"></a>
## [ISS-019] OI-19 — CSS is not layered — CLOSED 2026-11-11 (T14)

- **Category / target:** CSS architecture; CSS.
- **Location:** inline stylesheet(s), `src/00_head_masthead.part`.
- **Observed:** no `@layer`; required order absent: `reset, tokens, base, layout, components, utilities, print`.
- **Blueprint:** migrate rules without cascade changes; gate exact layer order and exceptions.
- **Evidence:** `[TESTED]` source marker scan; historical recorded stylesheet size 22,614 B must be freshly remeasured before implementation.
- **Update 2026-11-11 (T14) — CLOSED:** main stylesheet (fresh measure 21,606 B pre-migration) and all 12 per-figure `<style class="fs">` blocks migrated into `@layer reset, tokens, base, layout, components, utilities, print` (statement first in the stylesheet; fs print boosts → `print`, mobile boosts → `utilities`). Rule-inventory parity diff old↔new: 277 rules, 266 byte-identical, 11 designed swaps (token tiers + print hex→var, all value-preserving). One recorded cascade delta, contract-aligned: print token re-declarations moved from unlayered position 15 into the `print` layer, so layer priority now beats the OS-dark `:root:not([data-theme="light"])` specificity (0,2,0 > 0,1,0) — OS-dark + print previously resolved dark custom properties (e.g. `--ink-2` #C5C8CD captions on white); it now resolves the print token set (white ground, §7) in every theme state. Gate: `tools/gate_css_arch.py` G1 (exact statement + layer-name registry), G2 (zero unlayered rules, all blocks), G8 (`!important` registry parity, 10 declarations pinned) with 11 negative fixtures, all killed; wired read-only as `run.sh` step 2c. Rebuilt master 333,263 B SHA-256 `daf57d97…`; strict 49/49, 0 SKIP; falkon light/dark/no-JS/320/390 px + dark figures inspected `[SCREENSHOT-VERIFIED]`; print 65 pp inspected page-by-page via 6 montage grids. Design freeze + parity matrix: `plan/t14-css-architecture.md`; gate evidence `plan/t14-gates-evidence.txt`.

<a id="iss-020"></a>
## [ISS-020] OI-20 — Inline style attributes remain — CLOSED 2026-11-11 (T13)

- **Category / target:** CSS architecture; HTML + CSS.
- **Location:** master; historical examples l.513, 536, 716; table widths and footer padding.
- **Observed:** current parser finds 130 `style` attributes (prior report counted 130 across 49 lines; literal `style=` substring count can differ due CSS/SVG selectors).
- **Blueprint:** move declarations to semantic classes, `<colgroup>` and component tokens; zero inline style attributes. Re-audit exact attribute count with HTML parsing, not raw substring search.
- **Evidence:** `[TESTED]` current HTMLParser count.
- **Update 2026-11-11 (T13) — CLOSED:** all 129 parsed inline `style` attributes eliminated at source. 107 colgroup col widths → 32 `.cw-*` utilities-layer classes (kept `<colgroup>` markup; the ≤999 px `.tablewrap col{width:auto !important}` reset beats inline and class equally, so parity holds); 7 recall-mask coordinate triples → `.mask[data-for=…]` component rules; A–Ž index → `.idxcols` + scoped `.note .nbody .idxcols p`; two note-list `<ol>`s → `ol.tight-ol` scoped override; quality `<select>` → `.instrument select` (only select in the document); footer → `footer.wrap{padding-bottom:3rem}` with a print-layer companion — required because the print `.page,.wrap{padding:0}` reset previously lost to the inline style and layer order would otherwise flip the print winner. Same-layer specificity engineering covers the families where `.note .nbody p` (0,2,1) used to lose to inline. Gate: lint_html.py T10 (zero-style; lookbehind excludes SVG presentation attributes such as font-style=) inherited by C45; dedicated negative fixtures on both CLIs (lint selftest 9/9, verify fixtures 60/60 killed); the stale master failed T10 with exactly 129 violations before rebuild, green after. Rebuild 336,853 B SHA-256 `d0b4f9f7…`; strict 50/50, 0 SKIP; gate_css_arch G1–G8 PASS. Computed-style parity old↔new IDENTICAL across desktop-light, desktop-dark, mobile-light and print-emulated states for all 107 col widths, 7 mask left/top/width triples, the select box/font pair, footer padding-bottom, both tight ols, idxcols columns/font and letter-head margins (`plan/t13-parity-probe.json`; Chrome CDP, owner allowance this turn). falkon 390/768/1440 light/dark/no-JS + masks/index anchored probes inspected `[SCREENSHOT-VERIFIED]`; print 66 pp inspected via 6 montage grids (Chrome print-PDF fallback logged, owner-allowed). Instructor content review `[UNVERIFIED]`.

<a id="iss-021"></a>
## [ISS-021] OI-21 — Modern CSS and token topology incomplete — CLOSED 2026-11-11 (T14)

- **Category / target:** CSS architecture; CSS.
- **Location:** `src/00_head_masthead.part` and SVG styles.
- **Observed:** `@container`, `subgrid`, `:has()` absent; recorded audit found 85 hex literals and token tiers unadjudicated. Current direct marker scan finds no `:has()`/`@container`/`subgrid`.
- **Blueprint:** define primitive → semantic → component tokens; hex only in primitive palette; add intrinsic layout/state rules where useful; do not add features mechanically. Recompute token/contrast inventory.
- **Evidence:** `[INSPECTED]` current sources; 85 count is historical and not freshly recounted.
- **Update 2026-11-11 (T14) — CLOSED:** three-tier schema landed and frozen in `plan/t14-css-architecture.md` — primitives carry every raw value (`--<role>-l/-d` light/dark, `--paper-p/--ink-p/--ink-2-p` print deltas, `--rule-hc/-w` high contrast, `--t-*` type, `--f-serif/--f-sans`, `--sp-gap`), semantic roles keep the canonical ARCH names unchanged for every consumer, component tier = `--fig-*` (five aliases declared once on `:root` and inherited through `var()` chains; redundant dark-block re-declarations removed). Hex audit: zero hex literals outside primitive declarations anywhere in the stylesheet (fresh count, supersedes the historical 85; print component/@page hexes converted to `var(--ink)`, `var(--ink-2)`, `var(--paper)` at identical resolved values). Intrinsic layout/state rules were NOT added mechanically — existing intrinsic measures (ch/grid/minmax) suffice; `:has()`/`@container`/`subgrid` stay out per the blueprint's own clause. Contrast recomputed live from resolved tokens by C29 (lowest 5.14:1, unchanged); token resolution machine-checked per context by gate G4/G5. Enforced by `gate_css_arch.py` G3/G4 (11 fixtures killed); dark-print resolution repaired (see ISS-019 update). A20 "seven undefined vars" adjudicated as a lens artifact: the scalar tier (`--fs-*`×6 + families) was declared only in the light `:root` and inherited — all values resolved in every context; the explicit primitive homes make any context-scoped audit find the lineage.

<a id="iss-022"></a>
## [ISS-022] OI-22 — Native disclosure groups and popovers unused

- **Category / target:** HTML defect; HTML + CSS.
- **Location:** 100 `<details>` in master.
- **Observed:** zero `name=` groups, zero `<dialog>`, zero `popover` attributes. Native choices have not been classified by interaction purpose.
- **Blueprint:** classify disclosure groups; apply shared `name` where exclusivity is pedagogically correct; use Popover API for footnote previews only where semantics fit; preserve keyboard/no-JS behavior.
- **Evidence:** `[TESTED]` parser count.

<a id="iss-023"></a>
## [ISS-023] OI-23 — SVG reuse unassessed

- **Category / target:** Infrastructure/HTML; Python + HTML.
- **Location:** 11 inline SVGs across 7 figure wrappers.
- **Observed:** current parser finds no `<symbol>`/`<use>` and each inspected wrapper has role `img`; previous inventory reports title/desc and viewBox for each. Reuse could increase complexity, so it is an assessment task, not a blanket rewrite.
- **Blueprint:** assess repeated definitions; only if meaningful, generate shared symbols deterministically in Python; retain per-figure accessible title/description and instance-specific labels.
- **Evidence:** `[TESTED]` structural counts; conceptual geometry/render remains `[UNVERIFIED]`.
- **Update 2026-11-12 (T05/B02):** full node→consumers reference graph built (`tools/reference_graph.py`, graph at `plan/t05-reference-graph.json`): 13 inline SVGs across 9 figure wrappers, 223 unique ids, 115 classes, **no `<symbol>`/`<use>` element reuse** — the only repeated SVG machinery is four single-path `<marker>` defs (`ar-ch`, `ar1`, `arc`, `arp`) consumed by `marker-end="url(#…)"` within their own figures; per-figure accessible title/desc and instance labels are retained. Shared-symbol abstraction is **not meaningful** at this shape (each figure is distinct content; styling already shares `.fbox/.farr/.fct/…` classes and fig tokens), so the blueprint's conditional does not fire; OI-23 assessment satisfied, per-figure verdicts with consumer evidence in `tools/asset-classification.md`. Related: the graph also classified every zero-consumer id (17 subsection anchors DOM-taxonomy-mandated; `fit-free`/`#res-free` the registered dormant free-regression variant — protected, removal is an owner decision) and added a read-only reference-integrity guard (`reference_graph.py --gate`, run.sh step v6c).

<a id="iss-024"></a>
## [ISS-024] OI-24 — Strict TypeScript toolchain absent — CLOSED 2026-11-12 (T15)

- **Category / target:** Infrastructure gap; TypeScript.
- **Location:** workspace root and `src/`.
- **Observed:** no `.ts`, `tsconfig.json`, `pyproject.toml`; `tsc` absent per existing environment inventory.
- **Blueprint:** only when residual JS is justified, add `src/ts/`, strict configuration (`strict: true`, no `any`, explicit DOM null checks), a pinned compiler/build command and reproducible output; do not add runtime dependencies to HTML.
- **Evidence:** `[INSPECTED]` file inventory; compiler PATH finding carried from recorded environment inventory.
- **Update 2026-11-12 (T15) — CLOSED:** fresh PATH inventory found TypeScript **7.0.2** (`tsc`) + Node v24.22.2 (supersedes the stale "tsc absent" finding; recorded in `plan/t15-js-forensics.md`). `tsconfig.json`: `strict:true`, ES2020, DOM lib, `noEmitOnError`, `noUnusedLocals`. `src/ts/` holds J1–J5 with explicit null guards (`$` throws on a missing id), zero `any`, DOM-typed elements. Pinned pipeline `tools/compile_ts.mjs`: version pin check, compile-twice byte equality (reproducibility proof), string/regex-aware squeeze, per-hook budget report to `plan/t15-js-budget.json`. No runtime dependency added to the HTML (payload is the only executable script; no imports).

<a id="iss-025"></a>
## [ISS-025] OI-25 — Required budget/lint gates not implemented — CLOSED 2026-11-12 (T15)

- **Category / target:** Infrastructure gap; Python.
- **Location:** `tools/verify.py` C02/C25/C29; `tools/verify_js.mjs`; `run.sh`.
- **Observed:** no `tools/budget.py` or `tools/lint_html.py`; current harness does not enforce all §4 JS registry/bytes/lines/%, banned APIs, `noscript`, zero style attributes, CSS layers or AGENTS byte ceiling. A generic 8 KiB tool threshold is unverified. Existing `run.sh` builds and rewrites output/plan artifacts; do not run it in a governance-only task.
- **Blueprint:** add stdlib-only Python CLIs with nonzero failure, no SKIP counted as PASS, one negative fixture per rule; gate heading order, one h1, table scopes, SVG title/desc, anchors/IDs, WCAG ratios, JS caps/registry/API allowlist, HTML and AGENTS sizes; wire only in authorized implementation pass after reviewing side effects.
- **Evidence:** `[INSPECTED]` current tools inventory and `run.sh` read; no gates executed.
- **Update 2026-11-12 (T15) — CLOSED (JS/size scope; lint scope was already delivered by T04/T13 `lint_html.py`, CSS scope by T14 `gate_css_arch.py`):** new stdlib-only `tools/budget.py` (B1–B12: script bytes/lines/%, registry function allowlist, banned APIs + inline handlers, unregistered feature tokens, compile-manifest coherence, per-instrument fallbacks, HTML/AGENTS ceilings, zero style attrs, `@layer` statement; `--selftest` 14 negative fixtures + positive control; read-only, nonzero exit, no SKIP class). Stale 8 KiB threshold eliminated at all three sites (`verify_js.mjs` rewritten to the 4,096 B/100 lines/2% ceilings + registry allowlist + raw-scan of banned tokens, `--selftest` 5/5; verify.py C21 updated; README C21 row + new registry table). Wired read-only as `run.sh` step 2d after the mutating steps (build/compile) complete.
- **Update 2026-11-12 (T02/B04) — runner-mutation residue closed:** `run.sh` split into subcommands — `verify` is read-only (build `--check`, JS/trace/CSS/budget/claim/visual-contract gates, selftest, harness; zero writes under `src/`/`plan/` proven by an identical before/after sha256+mtime snapshot, `plan/t02-verify-nonmutation.*`), `build` holds the mutation, `all` = build then verify. The selftest no longer writes the evidence ledger: the C04 fixture monkeypatches `SOURCE_HASHES` to a temp ledger copy and the ledger's sha256 is re-checked against the pre-run snapshot. New `tools/negative-fixtures.json` registry (one fixture per check, tool-suite selftests, SKIP≠PASS rule) machine-checked by the selftest; 10 previously unfixtured checks (C01–C03, C08, C09, C12, C14, C22, C26, C31, C38) gained fixtures (selftest 78/78 killed). Evidence: `plan/t02-evidence.md`.

<a id="iss-026"></a>
## [ISS-026] Stale audit status in §2 needs reconciliation

- **Category / target:** Governance; Markdown.
- **Location:** former §2 sentence saying roadmap was absent and “not read”.
- **Observed:** roadmap is present and its heading inventory was inspected; `Master_Final_Perfected.md` remains absent. Existing prior status is stale.
- **Blueprint:** §2 now records current presence/absence and `[TESTED]` inventory date; keep roadmap proposals distinct from authorization. Full roadmap source remains the 2026-11-06 artifact; no roadmap edits permitted.
- **Evidence:** `[TESTED]` workspace inventory; roadmap headings/task matrix inspected.

<a id="iss-027"></a>
## [ISS-027] T03 — displayed LOD/LOQ and significant-figure boundaries

- **Category / target:** HTML/Python precision defect; HTML + Python + residual JS.
- **Location:** §10.8 LOD/LOQ paragraph (historical `src/11*` l.458–465), ch11 dl, 15.f, 15.d, J4 quality instrument (`src/17*`), `tools/data.py`.
- **Observed:** displayed LOQ 0,00086 mg/mL (0,86 µg/mL) was computed from the rounded s_y = 0,0026 A; full-precision authority s_y = 0,002644 A gives 0,00087 mg/mL (0,87 µg/mL) — double rounding (E26). LOD/LOQ lacked the fixed simplified-estimate label (C-07) and the missing-blank-evidence statement; 15.d Currie scope was broad; J4 verdict advised “0,0122” as 2 significant digits for sample 5 (magnitude-blind `fmt(c,4)`).
- **Blueprint:** reconcile every displayed limit to `data.py` rounding; show the arithmetic from stated inputs (0,00264 A); label estimates as simplified regression results, state absent blank replicates; scope Currie to terminology; make J4 sig-fig advice magnitude-correct; add A ≤ 0 / extrapolation boundary fixtures and a C44 map+lint with negative fixtures; log E26.
- **Update 2026-11-09 (T03):** applied. LOD/LOQ now 0,00026 / 0,00087 mg/mL (0,26 / 0,87 µg/mL) with full-precision s_y = 0,002644 A shown; simplified-estimate + blank-evidence labels present in §10.8; 15.d Currie note scoped to terminology/nomenclature with page-level status (no page citation invented); E26 logged; C14 → E1–E26; `data.py` `uncertainty_for_A` rejects A ≤ 0 and flags extrapolation outside 0,063–0,482 A, with U/LOD/LOQ display-parity invariants; J4 uses magnitude-correct 2-sig advice (sample 5 → 0,012), A = 0 clears outputs like an empty input (C36 35 assertions); C44 map+lint keeps 0,00086 / 0,86 µg/mL only inside the E26 before-quote. Verified `[TESTED]` strict 43/43 PASS, 0 SKIP; selftest 34/34 killed; build 321,547 B, SHA-256 `2eec8a2e…`, print 65 pp. Visual/print evidence `[UNVERIFIED]` this turn (both falkon tiers blank under Xvfb; no Chrome allowance given); instructor content review remains `[UNVERIFIED]` — issue stays open on those two points.
