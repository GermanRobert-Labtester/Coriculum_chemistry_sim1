# Open Issues Ledger

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §2, §4, §7, §9, §10, §12  
Last updated: 2026-11-07  
Verification status: `[INSPECTED]` static audit of current generated master and selected build sources. **B04 (2026-11-07):** every quoted A–F passage in `#n16c` was re-read from the current files and machine-verified (`tools/check_source_claims.py`; 63 fragments, 50 verbatim, 1 normalized, 4 elided, 8 reconstructed, 0 missing, 0 misplaced). Runtime certification is still absent. **B05 (2026-11-07):** K18–K21 product claims checked against the official ZVA register and exact Rehydron/ACC/Maalox leaflets/SmPCs (see `#b05` and the terminology registry); product facts verified or classified `[UNVERIFIED]`, and the wording remediation was applied in the user-authorized build pass (master 1 039 717 B, SHA-256 `341f5c26…`). Visual, keyboard and PDF acceptance remain absent.

This ledger is the detailed remediation source for the compact index in AGENTS.md §2. Issue status is evidence-layered. A finding from an older report remains a lead until checked against the current master. K1–K23 quotes are now byte-verified; a row stays open where its resolution needs lecturer policy or an external standard that this workspace has not opened.

## Current architecture findings

<a id="js-001"></a>
### [JS-001] Executable inline script exceeds ceiling

**Status:** `[TESTED]` 8,187 executable bytes, 196 lines, 0.7909% of the current 1,035,140-byte master. The controlling limit is 4,096 bytes / 100 lines / 2%, whichever is smallest. Inline event attributes: 0.  
**Location:** generated master `<script>`; source contributors `build/foot.html`, `build/recall_mode.js`, and search runtime emitted by `build/search.py`.  
**Violation:** total script exceeds both the byte and line ceilings; unregistered search behavior is included.  
**Emitted region split:** print state hook 692 B/10 lines (242 B over its 450 B registry cap); recall region 2,481 B/59 lines (81 B over 2,400 B cap; source file 2,394 B/55 lines); search 5,014 B/127 lines, unregistered. Regions sum to 8,187 B/196 lines.  
**Target:** strict TypeScript for residual client logic, Python for generated/static content; keep only approved micro-runtime code.  
**Blueprint:** measure the final emitted script after each isolated source change; preserve the master hash before any authorized build. Remove search/runtime code or establish a formally justified, budgeted registry entry before implementation. Keep all page reading and navigation operational with JS disabled. Do not count comments as a way to evade the ceiling.

<a id="js-002"></a>
### [JS-002] Search runtime has no registry entry

**Status:** `[INSPECTED]` current script has functions `norm`, `select`, `filter`, `jump`, `open`, and `close`; handlers listen for document click/keydown, input, list click, and dialog close. The interface uses one native `<dialog>`, but matching, result generation/selection, focus, and keyboard behavior are script-owned.  
**Location:** embedded search portion of the master script; static dialog placeholder `{{SEARCH_DIALOG}}` in `build/foot.html`; search generator `build/search.py`.  
**Violation:** search is explicitly not whitelisted in §4; client logic is raw JS and contributes to JS-001.  
**Target:** native dialog for presentation; generated index/data in Python; residual matching and keyboard behavior authored in strict TypeScript and compiled.  
**Blueprint:** first decide whether search remains a named learning task. If retained, add the smallest exact registry entry and JS-off behavior in a separately authorized implementation pass, convert source to TS, measure emitted bytes/lines, and test focus, empty query, no result, Unicode subscripts/superscripts, and keyboard selection. If it cannot fit the total ceiling, remove the enhancement while keeping chapter navigation and printable content intact.

<a id="js-003"></a>
### [JS-003] Print state hook needs one bounded implementation

**Status:** `[INSPECTED]` `build/foot.html` installs `beforeprint`/`afterprint` handlers (`openAll`, `restoreAll`); `build/head.html` also has `@media print` rules revealing details content. The exact restoration behavior in the current browser set was not established in this run.  
**Violation:** the temporary hook is eligible only as the registered ≤450-byte / ≤12-line `printExpand()` fallback after a permitted browser test demonstrates CSS alone is insufficient. The emitted script is already over budget.  
**Target:** CSS print rules first; otherwise one tiny TypeScript-authored fallback.  
**Blueprint:** use the existing `tools/check_print_state.py` state fixture and a fresh falkon/falkon permitted capture/print workflow in an implementation pass. Confirm original `open` states and `name` attributes are restored after print completion and cancellation. Keep the handler only for a reproduced renderer limitation; do not infer browser support from CSS source.

<a id="css-001"></a>
### [CSS-001] Layer declaration exists but most rules are unlayered

**Status:** `[INSPECTED]` `build/head.html` declares the required order near line 10, but only the print layer is a block; the rest of the 47,539-byte style sheet is outside layers. `@container` and `subgrid` are absent.  
**Violation:** declaration alone does not establish the mandated layer architecture; component and layout rules remain in the unlayered cascade.  
**Target:** CSS.  
**Blueprint:** migrate reset, token, base, layout, component, utility, and print rules into the declared layers in precedence order; keep browser defaults intentional; use container queries/subgrid only where the component structure benefits. Recheck light, dark, print, and narrow layouts after each source-owned change.

<a id="css-002"></a>
### [CSS-002] Custom properties remain a flat palette

**Status:** `[INSPECTED]` root and dark-theme values use names such as `--ground`, `--surface`, `--ink`, `--tone-1` and `--accent`; no `--p-*`, `--t-*`, or `--c-*` tiers were found.  
**Violation:** primitive, semantic, and component values are not separated; theme overrides are mixed with the current palette.  
**Target:** CSS.  
**Blueprint:** retain current hex values as the inspected baseline; introduce primitive tokens, map semantic tokens for light/dark/print, and define component tokens only for repeated component needs. Record calculated WCAG ratios only after a fresh resolved-background check; do not copy historical ratios or label them verified.

<a id="html-001"></a>
### [HTML-001] Native details groups and missing reuse patterns need semantic review

**Status:** `[INSPECTED]` generated master has 268 `<details>`, 37 opening tags with `name=`, one `<dialog>`, zero Popover API attributes, zero `<symbol>`/`<use>` pairs, 77 inline SVGs, and two `<noscript>` blocks. All 77 SVG opening tags carry `role="img"`.  
**Violation/gap:** no Popover-based previews or SVG symbol reuse were found; the 37 named groups have not been checked against every intended exclusive-answer group. Counts alone do not prove the other disclosures need exclusivity.  
**Target:** HTML/Python generation.  
**Blueprint:** map each disclosure to its pedagogical purpose; apply shared `name` only to mutually exclusive alternatives; preserve independent disclosures otherwise. Adopt `<symbol>/<use>` only for genuinely repeated artwork and preserve unique accessible titles/descriptions. Add popovers only for actual previews with keyboard and print fallbacks.

<a id="infra-001"></a>
### [INFRA-001] Missing deterministic HTML, budget, source, and governance gates

**Status:** `[INSPECTED]` current `tools/` contains `check_contrast.py`, `check_print_state.py`, `check_qa_report.py`, `check_recall_mode.py`, `check_source_claims.py`, `check_t20.py`, and `language_lint.py`. It does not contain `check_js_budget.py`, `check_html.py`, `check_agents_md.py`, or `extract_sources.py`. No `tsconfig.json`, `pyproject.toml`, or `.ts` source was found.  
**Target:** Python/TypeScript; detailed contract in `INFRA_PYTHON_TS_JS_AUDIT.md`.  
**Blueprint:** implement non-mutating CLIs with explicit input/output arguments, deterministic JSON reports, non-zero failure status, stdlib-only behavior unless a named build-only dependency is approved, and isolated QA outputs. Do not run a gate that rewrites the generated master as part of a documentation-only pass.

<a id="infra-002"></a>
### [INFRA-002] QA harness is raw JavaScript outside the production tiers

**Status:** `[INSPECTED]` `build/qa.js` is 29,556 bytes / 702 lines. It is a development QA harness and is not the embedded runtime.  
**Gap:** a substantial raw-JS QA system duplicates contrast resolution and browser checks; current Python report validators exist, but there is no strict TypeScript project.  
**Target:** Python for static checks and report processing; strict TypeScript only for browser-dependent QA where needed.  
**Blueprint:** inventory consumers and report schema; move static checks to Python, type any retained browser harness, separate generated evidence from source, and preserve tests/coverage. Do not delete or weaken QA checks during migration.

<a id="verify-001"></a>
### [VERIFY-001] Visual, keyboard, assistive technology, and PDF acceptance is open

**Status:** `[TESTED]` (B06, 2026-11-07, user-authorized Playwright/Chrome allowance): fresh screenshots at 390/768/1440, light and dark, were captured by `node build/qa.js` and directly inspected (task flow, dark theme, masthead, source-inventory table); zero console errors, zero external requests, contrast gates pass (ink_verified 13.47:1 resolved). Fresh full print PDF inspected (`pdffonts`, `pdfinfo`, outline parse): 259 pages, 0 PDF outline items, `Tagged: no`, and one Type 3 NotoSansMath subset on 19 pages — see `#b06`. **Still `[UNVERIFIED]`:** manual keyboard-only and assistive-technology walkthroughs, JS-off interactive walkthrough, and falkon/falkon lite-shot captures (not run this pass; Chrome was explicitly allowed by the user instead).  
**Target:** CSS/HTML/Python QA plus manual verification.  
**Blueprint:** follow `workspace_skills/VISUAL_VERIFICATION.md`; use `lite-shot` falkon then falkon, never Chrome unless explicitly allowed. Inspect the PNG; test keyboard and JS-off paths; inspect a freshly generated PDF for details, font embedding, outline, tags, and pagination. Record renderer, artifact, viewport/theme, status, and limitations. Governance-only changes require no render and must not claim visual acceptance.

<a id="src-001"></a>
### [SRC-001] Current source conflict register K1–K23

**Status:** `[TESTED]` the saved 2026-11-07 source-claims report records 63 quoted fragments (50 verbatim, 1 normalized, 4 elided, 8 reconstructed), 0 missing, 0 misplaced, and 0 errors; its A–F hashes match the current source files. Excerpts in `#n16c` are `[TEXT-VERIFIED]`; the full documents are not certified as a whole. K1–K23 remain open where interpretation, external authority, arithmetic acceptance, or lecturer policy remains unresolved. Preserve source wording, calculate independently, state assumptions, and request lecturer resolution when exam intent is unclear.

### <a id="k1"></a> K1 — Mole definition conflict
**Location:** B p.3; `#n4`. **Gap:** mole definition versus fixed-constant definition. **Fix:** reopen B; distinguish historical source wording from current SI definition; cite a read primary source before revising.

### <a id="k2"></a> K2 — Particle-class bands
**Location:** B p.1; `#n2`. **Gap:** particle-class bands leave gaps. **Fix:** preserve endpoints/gaps; ask course owner before interpolation.

### <a id="k3"></a> K3 — Degree of dissociation
**Location:** B p.2; C Q19–20; `#n3`. **Gap:** α omitted; full dissociation assumed. **Fix:** mark α=1 as an exercise assumption; distinguish ideal stoichiometry from equilibrium.

### <a id="k4"></a> K4 — Ammonia and Ostwald notation
**Location:** B p.2; `#n3`. **Source text (read 2026-11-07):** «Vājie elektrolīti ir (α < 0,1) … NH3 · H2O», and the worked example prints K<sub>dis</sub> = [OH⁻][NH₄⁺]/[NH₄OH] = 1,79·10⁻⁵, then Ostwald's law as K<sub>a</sub> = C·α² and α = √(K<sub>a</sub>/C). **Gap:** the source labels a base equilibrium with an acid constant and invents the species NH₄OH; 1,79·10⁻⁵ is the ammonia K<sub>b</sub> value. **Fix:** keep the quotation; separate notation from the restricted model; the standard value is `[UNVERIFIED]` here because no primary equilibrium source was opened. Lecturer question open.

### <a id="k5"></a> K5 — M symbol collision
**Location:** B p.3, C, E; `#n5/#n7/#n14`. **Gap:** `M` collides between molar mass and molar concentration. **Fix:** state course convention; use `c(B)` and `mol/L` in new prose; retain quoted notation mapping.

### <a id="k6"></a> K6 — Density conversion
**Location:** B p.3, E p.1; `#n6`. **Gap:** L with g/mL density risks a ×1000 error. **Fix:** show unit cancellation and factor; recompute exact example.

### <a id="k7"></a> K7 — Formula labels
**Location:** C formula labels; `#n16a`. **Gap:** duplicate formula number 7 and skipped 8. **Fix:** preserve source labels; use stable guide IDs and show mapping.

### <a id="k8"></a> K8 — KOH/Na₂CO₃ example
**Location:** B Ex2 p.5, Ex5* p.8; `#n6–#n7`. **Gap:** KOH header on Na₂CO₃; starred example conflicts. **Fix:** keep source statement; solve each plausible reading; request lecturer intent.

### <a id="k9"></a> K9 — Stoichiometric ratio
**Location:** B Ex10 pp.12–13; `#n11`. **Source text (read 2026-11-07):** «n skābes = 2n sārma» twice, immediately followed by «n NaOH = n H2SO4 / 2» and the result 0,005 mol → 0,49 g. **Gap:** the sentence reverses the relation; read literally it gives 0,020 mol and 1,96 g. **Fix:** derive the ratio from H₂SO₄ + 2NaOH → Na₂SO₄ + 2H₂O; keep both readings visible.

### <a id="k10"></a> K10 — Saline percent conflict
**Location:** A; B Ex3 p.6; `#n5/#n6`. **Gap:** 0.9% versus 0.88%. **Fix:** identify percent basis and course/external context; do not conflate.

### <a id="k11"></a> K11 — Mass fraction needs solution mass
**Location:** B 9a p.14; `#n6/#n13`. **Gap:** 0.85 g supports m/V but w/w needs total solution mass/density. **Fix:** give conditional m/V result; mark w/w underdetermined without density.

### <a id="k12"></a> K12 — Molar mass, not premature rounding
**Location:** B Ex7 p.10; `#n9`. **Source text (read 2026-11-07):** «MH2SO4 = (2 · 1) + 32 + (4 · 16) = 98 (g/mol)», «mšķ. = 100 · 4,9 / 96% = 5,1 (g)», «V = 5,1 / 1,84 = 2,77 (ml)». **Gap:** the earlier diagnosis was wrong. With the handout's own M = 98,00 g/mol the chain is 4,900 g → 5,104 g → 2,774 mL, and 5,1/1,84 = 2,7717 mL also rounds to 2,77 mL; so 2,77 is *not* a premature-rounding error. 2,78 mL appears only with M = 98,08 g/mol (4,904 g → 5,108 g → 2,776 mL). **Fix:** the dispute is which molar mass the exam accepts; never mix a 98,08 intermediate with a 98 answer. Both values stay visible; lecturer question open.

### <a id="k13"></a> K13 — Final volume for γ
**Location:** C Q10; `#n8`. **Gap:** 300.0 mL water treated as final volume for γ. **Fix:** distinguish solvent from final solution volume; state missing assumption.

### <a id="k14"></a> K14 — Given densities
**Location:** C Q7/Q13/Q17; `#n6/#n9`. **Gap:** given densities appear atypical. **Fix:** treat as stipulated exercise values unless exact composition, temperature, and primary data are verified.

### <a id="k15"></a> K15 — Answer-key slips
**Location:** C key Q9/Q10/Q20/Q24–26; `#n1/#n13/#n16c`. **Gap:** significant-figure and ion-label slips. **Fix:** compare literal key, balanced equation, charge, units, and unrounded value.

### <a id="k16"></a> K16 — Formalin/formic acid
**Location:** D/E P5; `#n10`. **Gap:** “Formalin (HCOOH)” confuses formaldehyde and formic acid. **Fix:** preserve quoted error; distinguish HCHO from HCOOH and verify source context.

### <a id="k17"></a> K17 — Denominators and volume additivity
**Location:** E P7; C Q17; B Ex8; `#n10`. **Gap:** solute called solution mass; volume additivity assumed. **Fix:** identify denominator and explicitly qualify additive-volume approximation.

### <a id="k18"></a> K18 — Rehydron composition/basis
**Location:** D/E/F P10; `#n12`. **Gap:** sum omits KCl; water mass unstated. **Fix:** verify exact Latvian formulation/leaflet and basis; never substitute WHO ORS; otherwise use hypothetical data.
**B05 (2026-11-07) `[TEXT-VERIFIED]`:** classic Rehydron reģ. 01-0036 (Orion; PIL ZVA 10-02-2026, SmPC 19-10-2021) matches the worksheet exactly — 10,0 g glikozes / 3,5 g NaCl / 2,9 g nātrija citrāta / 2,5 g KCl, dissolve in 1 L; «Nesatur citas sastāvdaļas». SmPC §2 ions (Na 89,5; citrāts 9,9 mmol/L) prove the 2,9 g citrate is the **dihydrate** (M≈294), so the master's anhydrous table (citrāts 11,2; Na 93,6) is the worksheet-formula reading, not the official product. Register shows 01-0036 «nav pieejamas»; the current available product is **Rehydron Optim 11-0302** (6,75/1,30/1,45/0,75 g in 0,5 L) — different. PIL spelling «hipernatrēmija» vs master correction «hipernatriēmija» (both attested; variant). **Applied (build pass):** the #n12 table is captioned as the worksheet-formula reading; the official dihydrate ions (citrāts 9,9; Na 89,5) and the Optim mismatch are stated in prose and P10's note; the spelling is aligned to the PIL («hipernatrēmija», variant noted) and appears only as quoted source. **Still open:** lecturer policy on which product an exam would mean (V). See `TERMINOLOGY_AND_SOURCES.md` registry.

### <a id="k19"></a> K19 — ACC and percent basis
**Location:** E/F P11(4); `#n12`. **Gap:** only maximum ACC given; percent kind implicit. **Fix:** verify exact product strength/formulation and denominator; avoid medical advice.
**B05 (2026-11-07) `[INSPECTED]`/`[UNVERIFIED]`:** the ZVA register (substance «Acetylcysteinum», all forms) has **no oral 10 %/20 % ACC solution**: the only oral solution is 20 mg/mL (2 %); 100 mg/mL (10 %) is injection-only (ACC 05-0134); 200 mg/mL (20 %) is not registered. The worksheet's «10 %/20 % ACC» oral product and its 1,8–4,0 g/dienā dose therefore have **no current official oral-product basis** and stay `[UNVERIFIED]` as product facts. The 100/200 mg/mL arithmetic itself is correct (B04 recompute). **Applied (build pass):** P11 and the #n12 ACC prose/recall now carry «Hipotētisks piemērs — tikai aritmētika, nevis zāļu lietošanas ieteikums»; the «drošības robeža», «ārsta nozīmēto» and «klīniskā atbilde» framing and the «dienas devas intervāls» recall prompt are removed; m/V and ρ assumptions are explicit; 1,8–4,0 g remains only as arithmetic. **Still open:** lecturer policy (V) on whether such a product is examinable. See registry.

### <a id="k20"></a> K20 — Powder/solution denominator
**Location:** D/E/F P12; `#n12`. **Gap:** powder and solution denominators may be mixed. **Fix:** reopen task/key; distinguish active solute, powder mass, and final solution mass.
**B05 (2026-11-07) `[TEXT-VERIFIED]`/contradiction:** ACC 100 mg reģ. 00-0284 (Sandoz; SmPC 18-09-2025, PIL ZVA 24-03-2026) confirms «3 g pulvera satur 100 mg acetilcisteīna» and «2,8 g saharozes» — the powder denominator (3 g) and active/sucrose masses match. **But** the official ascorbic-acid content is **12,5 mg** (ACC 100 mg), not the worksheet's 100 mg; the worksheet's 100+2800+100=3000 mg balance is also internally inconsistent (no room for saccharin/flavour). Current dosing: adults/≥14 y «2 paciņas 2–3 reizes dienā (400–600 mg/dienā)»; the leaflet says consult a doctor after **4–5 days**, not a fixed «max 4 days». **Applied (build pass):** P12 and #n12 label the 100 mg ascorbic acid as the worksheet value and state the official 12,5 mg; the 600 mg and 24-sachet arithmetic is labelled a worksheet stipulation, not usage advice. Denominator separation was already correct and is unchanged. See registry.

### <a id="k21"></a> K21 — 13.4 g versus 13.5 g
**Location:** E/F P13; `#n12/#n13`. **Gap:** truncation versus rounding. **Fix:** recompute full precision and apply the stated precision rule once.
**B05 (2026-11-07) `[TEXT-VERIFIED]`/`[UNVERIFIED]` product fact:** the current LV Maalox suspension reģ. 96-0538 (Opella) is **35 mg Al(OH)₃ + 40 mg Mg(OH)₂ per 1 mL** (SmPC §2; = 350/400 mg per 10 mL); other LV Maalox are 460/400 mg per 4,3 mL (10-0504) and 400/400 mg tablets (10-0503). **None matches** the worksheet's 220 mg Al / 380 mg Mg per 10 mL, so that composition is a historical worksheet value, `[UNVERIFIED]` against any current official leaflet. The 13,49→13,5 g rounding and 0,0994-vs-0,100 mol arithmetic are independently correct (B04). **Applied (build pass):** P13 and #n12 label 220/380 mg per 10 mL as worksheet-stipulated historical data, state the 96-0538 values (35/40 mg per mL) and keep the rounding correction; no dose advice is present. See registry.

### <a id="k22"></a> K22 — Typos and mixed language
**Location:** D/E/F; `#n12/#n14`. **Gap:** source typos and mixed-language text. **Fix:** quote source faithfully; edit guide explanation only with traceable correction.

### <a id="k23"></a> K23 — Percent kind
**Location:** A; `#n5/#n12`. **Gap:** percent kind/basis unspecified. **Fix:** label m/m, m/V, or V/V explicitly; ask course owner if intended basis is absent.

<a id="b05"></a>
## B05 — Product-claim primary-source verification (2026-11-07)

**Status:** `[DIAGNOSTIC INVESTIGATION]` complete (governance-only, master unchanged), then the **user-authorized build pass** applied the K18–K21 wording remediation on 2026-11-07. The K rows stay open only for the remaining lecturer-policy question (V). Master before: 1 035 140 B, SHA-256 `f0c0d76c9263d5594516b032aadebe416484b5e808c953005bff6da9d3780c3c` (backup: `build/backup/master-pre-b05-f0c0d76c.html`). Master after: 1 039 717 B, SHA-256 `341f5c2697c5c07b1fe7b9a05d75d4f8025763ca0c5b56d795fe9091f30e7935`, mtime 2026-11-07 19:24:48 +0200.

**Method.** Read D/E/F P10–P13 fresh with `pdftotext -layout`; re-ran the B04 gate in memory (`check_source_claims.run(write=False)`: 63 quotes, 0 missing/misplaced, 34/34 recomputes agree; stored report still matches disk). Retrieved the official ZVA register and the exact product PIL/SmPC with a browser user-agent GET (the default fetcher is 403-blocked), parsing the returned PDF/DOC. Access date 2026-11-07. Full registry fields and exact passages: `TERMINOLOGY_AND_SOURCES.md#verified-source-registry`. WHO ORS was not used to establish any branded composition.

**Verdict matrix (worksheet claim → official Latvian evidence):**

| Task | Worksheet value | Official LV result | Verdict |
|---|---|---|---|
| P10 / K18 | Rehydron 3,5 NaCl / 2,5 KCl / 2,9 citrāts / 10 glikoze, 1 L | Rehydron 01-0036 PIL 10-02-2026: exact match; registered but «nav pieejamas». Current available = Optim 11-0302 (6,75/1,30/1,45/0,75 g, 0,5 L). | Composition `[TEXT-VERIFIED]` (classic product); current-product mismatch noted. |
| P10 citrate form | bezūdens C₆H₅Na₃O₇ (table 11,2; Na 93,6 mmol/L) | 01-0036 SmPC §2: citrāts 9,9; Na 89,5 mmol/L ⇒ 2,9 g = dihidrāts (M≈294). | Master anhydrous table = worksheet reading, not official product. |
| P11 / K19 | «10 %/20 % ACC» oral; 1,8–4,0 g/dienā | Register: oral solution only 20 mg/mL (2 %); 100 mg/mL injection-only (05-0134); no 200 mg/mL. | Product + oral dose `[UNVERIFIED]`; arithmetic correct. **High risk.** |
| P12 / K20 | ACC 100: 3 g, 100 mg acetylcisteīns, 2,8 g saharoze, 100 mg askorbīnskābe; «max 4 dienas» | 00-0284 SmPC/PIL: 3 g + 100 mg + 2,8 g ✓; askorbīnskābe **12,5 mg** (not 100); adults 400–600 mg/dienā; consult after 4–5 days (no fixed 4-day max). | Active/sucrose `[TEXT-VERIFIED]`; ascorbic acid contradicted; dose/max-duration not leaflet guidance. |
| P13 / K21 | Maalox 220 mg Al / 380 mg Mg per 10 mL | 96-0538 SmPC: 35 mg Al + 40 mg Mg per 1 mL (350/400 per 10 mL); no LV match for 220/380. | Product `[UNVERIFIED]` (historical); rounding arithmetic correct. |

**Applied remediation (build pass, 2026-11-07; edit build sources, not generated HTML):**

1. **P11 (highest priority):** the clinical dose recommendation and the «maksimums … drošības robeža» / «ārsta nozīmēto intervālu» / «klīniskā atbilde» framing were removed from `build/tasks_b.py` P11 (`dots`, `why`, `assumption`, `wrong`) and `build/ch09_12.html` (ACC paragraph + recall question). The task is now an explicitly labelled hypothetical, arithmetic-only example («Hipotētisks piemērs — tikai aritmētika, nevis zāļu lietošanas ieteikums»), with the percent basis (m/V) and ρ assumption stated; the ZVA registry fact (no LV-approved oral 10 %/20 % product) is quoted; no real-product oral dosing advice remains.
2. **P10:** the composition is labelled as the classic Rehydron formulation per worksheet + official 01-0036 leaflet (dated), with the current available Optim product (11-0302, different composition) noted; the mmol/L table is captioned as the worksheet-formula reading, with the official SmPC dihydrate values (citrāts 9,9; Na⁺ 89,5; SmPC 19-10-2021) stated in prose; the hypernatremia sentence remains only as quoted source; spelling aligned to the official PIL («hipernatrēmija», variant acknowledged).
3. **P12:** the 100 mg ascorbic acid is labelled the worksheet value against the official 12,5 mg (B05); the «max 4 dienas» dose advice was removed; the 600 mg/24-sachet arithmetic is labelled a worksheet stipulation, not guidance.
4. **P13:** 220/380 mg per 10 mL is labelled worksheet-stipulated historical data with no current LV product match (96-0538 is 35/40 mg per mL); the arithmetic and rounding correction are kept; no dose advice.
5. The chapter lead disclaimer is kept; every unit denominator is explicit; no clinical recommendation or maximum was added; calculation/source/terminology gates were re-run and the QA is bound to the new master hash.

**Applied outcome.** Files edited: `build/tasks_b.py` (P10–P13), `build/ch09_12.html` (#n12 prose, table caption, role-mistake clause, recall), `build/recall.py` (chapter-12 recall prompt), `build/conflicts.py` (K18 `analysis` only; quotes untouched). Gates: build exit 0; source claims 63 quotes / 34 recomputes, 0 errors; equations 261 parsed, 0 failures, 12 fixtures; pedagogy 67/0; coverage 0; print-state, recall-mode, T20 and contrast checks PASS. Structure unchanged: 67 tasks, 268 details, 77 SVG, emitted script 8 204 B. The rendered master diff is limited to #n12 tasks/prose/recall, the table caption/index, the K18 conflict card and the search index.

**Acceptance/DoD mapping:** composition values now trace to official exact formulations where they exist (P10 classic, P12 active/sucrose), are labelled with the official value where the worksheet differs (P12 ascorbic acid), or are classified `[UNVERIFIED]` and visibly treated as worksheet-stipulated historical/hypothetical data (P11 oral dose, P13 Maalox); no dose advice remains; denominators explicit; K issues retained. **Limits:** register enumeration reflects current Latvian registrations only (historical/cancelled products may not be exhaustively searchable); leaflet facts are not clinical advice; `build/qa/report.json` is a stale Playwright artifact bound to an older master (SHA `1f39e56a…`) and was deliberately not regenerated; visual, keyboard, AT and PDF acceptance remain `[UNVERIFIED]`; the exam-pack HTML was regenerated (55.6 KB) but `exam_pack.pdf` was not rebuilt.

<a id="b06"></a>
## B06 — Roadmap-remnant verification and authorized build pass (2026-11-07)

**Status:** complete. User-authorized verification pass (fresh Playwright QA against the then-current B05 master `341f5c26…`) followed by a user-authorized build pass (scope: the open 35-task-roadmap remnants; T05/T06 plus required gate repair). Master before: 1 039 717 B, SHA-256 `341f5c2697c5c07b1fe7b9a05d75d4f8025763ca0c5b56d795fe9091f30e7935` (backup: `build/backup/master-pre-b06-341f5c26.html`). Master after: 1 039 690 B, SHA-256 `cfdfc265cbb1449fae79b02d92d5bce68e983dae2df905bbb3cfc6c5594695a7`, mtime 2026-11-07 20:14:57 +0200.

**Verification phase (no product sources touched):** the stale QA report (bound to pre-B05 `1f39e56a…`) was regenerated by `node build/qa.js` under an explicit user Chrome/Playwright allowance; the fresh run exposed a real layout regression — table 25 «Avotu inventārs» (generated by `build/conflicts.py`) overflowed its wrap at 768 CSS px (791 px scroll vs 724 px client; `narrowTables=1`, QA layout gate FAIL). Fresh T03 evidence: full print PDF 259 pages, **0 PDF outline items, `Tagged: no`, no StructTreeRoot, and one Type 3 `NotoSansMath-Regular` subset on 19 pages**; per-page character-inventory diffing isolated math/superscript glyphs (² ¹ ⁴ ⁵ ⇌ √ ≈ ≠ ≡ ≪ − × ÷ α ν ω) as the Skia-emitted Type 3 content while the T20 two-page pack remains Type-3-free. T06 census `[TESTED]`: 166 role callouts (81 `role-mistake`, 69 `role-verified`, 16 `role-rule` — all semantic, counts unchanged), 44 `.source-note`, 67 `.why`, 0 `<aside>`; 508 CSS rules, 16 media blocks; of 54 repeated selectors only 2 are true same-context shadowed duplicates (`.fig-unit.tone-2/.tone-3`); the rest are `@media`/`@supports` progressive enhancement.

**T05 disposition — evaluated and rejected with evidence.** All three roadmap-permitted note sources (K5, K13, K17) fail the task's own rejection rule T05.1.3 («reject any note that repeats adjacent prose»): the fragments already carry these caveats inline from earlier remediation passes — K5 via the quantity-map transition list, table 9's «Apzīmējuma slazds» column, and the chapter-14 mapping table (with live `#k-k5` link); K13 via the explicit «ūdens vs šķīdums» warning at the γ section (`#n8`); K17 via the additivity caveats and the Rehydron/KCl denominator explanation in `#n10`/`#n12`. Shipping a rail with zero non-redundant notes would be dead markup against the restraint pillar; T05 is closed as *evaluated, no viable note candidates*, not implemented.

**Build-pass edits (build sources only; generated HTML rewritten by the builder):**

1. `build/head.html`: `.table-wrap.compact td{overflow-wrap:anywhere}` — fixes the 768 px overflow by allowing long filename/SHA tokens to wrap; deliberately scoped to `td` after an initial `th,td` version was captured breaking header labels mid-word («I D», «Atvēr ts») and rejected by direct PNG inspection.
2. `build/head.html`: removed the two shadowed duplicate rules `.fig-unit.tone-2{fill:var(--tone-2)}` / `.fig-unit.tone-3{fill:var(--tone-3)}` (identical to the earlier occurrences at lines 307–308); the base `.fig-unit` rule and first occurrences remain.

**Applied outcome.** Gates after rebuild: build exit 0 (67 tasks, 97 recall items, 66/66 concepts, 0 pedagogy errors, 23 routes/14 fixtures, 13/13 sig-fig vectors, 31 figure numbers 0 drift); source claims 63 quotes / 34 recomputes PASS; recall-mode, print-state, contrast, T20 PASS; fresh QA report bound to `cfdfc265…` with overall PASS (narrowTables 768: 1 → 0; 1440: 0; table 25 re-measured scroll=client=724 and visually inspected). The only pre-existing non-fatal warning is the 231-item language-lint report.

**Acceptance/DoD mapping:** stale-report gate repaired without weakening the validator; the layout regression is fixed at source, not by masking the gate; role semantics unchanged; no content, terminology, or source-claim changes. **Limits:** T03 outline/tags and the Type 3 export remain open (now with fresh evidence); keyboard/AT/manual walkthroughs remain `[UNVERIFIED]`; falkon/falkon lite-shot captures were not run (Chrome explicitly allowed for this pass only); the exam-pack PDF was not rebuilt beyond the existing T20 pack.

<a id="src-002"></a>
### [SRC-002] Implementation source delta needs full content review

**Status:** `[UNVERIFIED]` inventory was compared with the prior `AGENTS.md` mtime (2026-11-07 14:01:38 +0200), but not every changed implementation source was read line-by-line. Directly inspected in this pass: `build/head.html`, `build/foot.html`, `build/recall_mode.js`, `build/qa.js`, `tools/check_contrast.py`, `tools/check_source_claims.py`, `build/qa/source-claims.json`, the generated master structure, and the visual verification protocols. The active roadmap identifies source dependencies and historical findings but is not a substitute for reading live code.  
**Remaining source delta inventory:** `build/answers.py`, `build/build.py`, `build/calc.py`, `build/ch01_04.html`, `build/ch05_08.html`, `build/ch13_14.html`, `build/ch15_16.html`, `build/conflicts.py`, `build/coverage.py`, `build/error_cases.py`, `build/figures.py`, `build/mistake_index.py`, `build/percent_basis.py`, `build/recall.py`, `build/taskbase.py`, `build/tasks_a.py`, `build/tasks_b.py`, `build/unit_strips.py`, `build/unitcheck.py`, `build/volumetric_steps.py`, `tools/check_print_state.py`, `tools/check_recall_mode.py`, and changed QA fixtures/reports/generated outputs. Some are generated; inspect their role before treating them as source. No TS files or `tsconfig.json` were found.  
**Target:** Python/content audit. Read current source records and trace build output before closing this inventory issue; do not alter product files under the documentation lock.

## Historical findings requiring current recheck

<a id="gov-002"></a>
### [GOV-002] Protected master changed during the audit window

**Status:** `[TESTED]` by pre/post fingerprint comparison; cause `[UNVERIFIED]`. Start observation at 2026-11-07 16:04:41 +0200: 1,011,445 bytes, SHA-256 `2d20f634f325b198e22a4b1ef2d263905561473e99348f6a856f72f904d2bedf`. Reobserved at 16:25:41 +0200: 1,035,140 bytes, SHA-256 `f0c0d76c9263d5594516b032aadebe416484b5e808c953005bff6da9d3780c3c`. During the same interval, build sources, generated fragments/figures, and QA JSON showed clustered mtimes around 16:19–16:25. This agent did not run the builder or write those product files.  
**Disposition:** integrity gate did not pass. Do not restore or overwrite the current master under this documentation-only scope. Establish the cause and source/master pairing in a separately authorized audit; record a new fingerprint before product work.

### [LEGACY-001] Prior E-series and QA measurements

The 2026-11-06 rulebook listed E03–E28 and older K/J/I counts from a 579,768-byte master. The live master reached 1,035,140 bytes during this run and has a different SHA-256. Do not carry old counts forward as current defects. Recheck each item against current build sources and generated output before closing or reopening it. The old report remains useful as a diagnostic checklist, not release evidence.

<a id="legacy-002"></a>
### [LEGACY-002] Roadmap/source specification files

`MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` exists and is the active queue by user instruction. It is a read-only planning document and states that its evidence is historical. `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` were not found in the root; do not fabricate or recreate them. `PROMPT_Master_html_3_tema_v2.md` and prior plans remain read-only. The workspace is not a Git repository, so no Git history/status can substantiate changes.

## Closure rule

Close an issue only with dated `[TESTED]` or sufficiently direct `[INSPECTED]` evidence against the current master/source, an exact file/selector/ID, and a row in AGENTS.md §11. For source conflicts, require the exact source passage plus calculation/authority warrant; a stale QA report or roadmap row cannot close an issue.
