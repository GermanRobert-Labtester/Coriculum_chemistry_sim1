# N10 Verification Record — Terminology Island & Unit-String Lint

**Status:** closed 2026-11-17 (UTC) · **Execution label:** VERIFIED (2026-11-17, this environment)

## 1. Verbatim Policy & Scope Rules

- **Masters' usage rule (`rules.masters_usage_rule`):**
  `Meistaru latviešu lietojums ir noteicošais avots; katram terminam norādīta meistara vai N06/N08 sākotnējā atsauce. Ja meistaru starpā ir atšķirības, tiek fiksēta vienotā kanoniskā forma ar nosauktu atšķirīgo formu (dissent), nevis izgudrots jauns dialekts.`
- **IUPAC pair rule (`rules.iupac_pair_rule`):**
  `Kursa meistaru latviešu forma vienmēr ir primārā. IUPAC sistemātiskais nosaukums tiek rādīts kā sekundārs pēc pieprasījuma (on-request) formātā '<primary_lv> (IUPAC: <iupac_name>)', lai saglabātu vienotu mācību valodu bez terminu sajaukšanas.`
- **Prose-exemption scope (`rules.prose_exemption_scope`):**
  `Brīvā teksta prozas lauki (piemēram, skaidrojumi, atgriezeniskās saites teikumi, piezīmes, norādes), kuros vienība var būt citēta teikuma iekšpusē, ir apzināti izslēgti no lauka līmeņa vienību sintakses pārbaudes; stingrā gramatikas pārbaude attiecas uz deklarētajiem vienību laukiem (unit, from, to, expected_unit, axis.unit, temperature_unit) un uz terminu nosaukumiem ar iekļautu vienību iekavās.`
- **Nested-unit scan rule (`rules.nested_unit_rule`):**
  `Ja termina vai grafika apzīmējuma text_lv iekļauj vienību iekavās — piemēram, 'Šķīduma blīvums ρ (g/mL)' — pilnā dokumenta skenēšana (C.1.1) izvelk iekavās esošo vienības virkni un pārbauda to ar unit_grammar parseri un dimensiju noteikumu.`

## 2. Terminology Island Validation (`data/terms.json` → `#sim-terms`)

- **Validator (`python3 tools/validate_terms.py`):** `PASS` (`canonical_bytes=64,508`, `canonical_sha256=f77bddea42b87fd098a998bfed6955b9b681fb640580acded8a704cb3a2d2d6f`).
- **Entry counts by class (`total=174`):**

| Class | Count | Scope |
|---|---:|---|
| `terms` | 65 | Seven-topic domain terms, contested-term dissent, Phase III figure axis/legend/annotation keys |
| `quantities` | 31 | Quantities with symbol/abbr, grammar-checked `unit`, and `dimension` |
| `instruments` | 13 | Lab glassware, balance, meniscus, cuvette, spectrophotometer, calorimeter |
| `interface` | 55 | N06 shell/panels, N08 hint ladder, N07 drawer, N09/N23 feedback & mode labels |
| `iupac` | 10 | Masters' primary Latvian form + on-request IUPAC name pairs |

- **Ecosystem grounding:**
  - `26` unit-grammar elements checked against `data/conventions.json`: `0` orphan elements.
  - All `concept_id` bindings resolved against `data/coverage.json` (`P1-01`–`P7-05`); all `conventions_ref` resolved against `data/conventions.json`.
  - Authored-data lint: `239` unit-bearing fields checked (`data/terms.json`, `data/conventions.json`, `data/golden_vectors.json`), `360` prose fields exempt by `rules.prose_exemption_scope`, `0` errors.

## 3. Unit Grammar Fixtures (`parse_unit` / `SimTerms.parseUnit`)

| Fixture | Input | Result | Code / Dimension Vector |
|---|---|---|---|
| Valid molar mass | `g/mol` | PASS | `{M: 1, N: -1}` |
| Valid mass concentration | `mg/mL` | PASS | `{M: 1, L: -3}` |
| Valid gas constant | `J/(mol·K)` | PASS | `{M: 1, L: 2, T: -2, N: -1, Theta: -1}` |
| Valid molar absorptivity | `L/(mol·cm)` | PASS | `{L: 2, N: -1}` |
| Valid ion-product | `(mol/L)^2` | PASS | `{N: 2, L: -6}` |
| Valid 1st-order rate const | `s^-1` | PASS | `{T: -1}` |
| Valid qualified percent | `% (m/V)` | PASS | `{}` (`dimensionless`) |
| Unknown element | `xyz`, `ml` | FAIL (caught) | `E_UNIT_UNKNOWN_ELEMENT` |
| Malformed separator | `g//mol`, `J/(mol*K)` | FAIL (caught) | `E_UNIT_MALFORMED_SEPARATOR` |
| Unparenthesized denominator | `J/mol·K` | FAIL (caught) | `E_UNIT_AMBIGUOUS_DENOMINATOR` |
| Flipped transcription in density | `mL/mg` (`density`) | FAIL (caught) | `E_UNIT_DIMENSION_MISMATCH` |
| Wrong dimension for density | `mol/L` (`density`) | FAIL (caught) | `E_UNIT_DIMENSION_MISMATCH` |

## 4. Stub-Closure Table

| Task | Artifact | Status | Resolved / Total | Notes |
|---|---|---|---|---|
| N06 | `data/n06_term_stubs.json` | `CLOSED` | `21 / 21` | All keys and `text_lv` match `#sim-terms` |
| N08 | `data/n08_term_stubs.json` | `CLOSED` | `15 / 15` | All keys and `text_lv` match `#sim-terms` |
| N09 | `data/n09_term_stubs.json` (not yet authored) | `pending-N09` | `0 / 0` | N09 has not yet been executed in this workspace; canonical `feedback.*` keys are pre-authored in `#sim-terms`, and `NEG-STUB-MISSED-KEY` proves a missed N09 key (`feedback.missed_n09_key`) is listed by `(task, key)` |

## 5. Planted-Failure Lint Corpus & Build Gate Refusal

- **Planted failures caught by name (`tools/n10_corpus.py`):**
  - `NEG-STUB-MISSED-KEY`: `missing_entries=[{task: "N09", key: "feedback.missed_n09_key"}]`
  - `NEG-PLANTED-INVALID-UNIT`: `E_UNIT_AMBIGUOUS_DENOMINATOR` on `'J/mol·K'`
  - `NEG-PLANTED-UNKNOWN-KEY`: `E_TERMS_UNKNOWN_KEY` on `'term.does_not_exist'`
  - `NEG-PLANTED-DIMENSION-MISMATCH`: `E_UNIT_DIMENSION_MISMATCH` on `qty.density` carrying `'mol/L'`
  - `NEG-PLANTED-NESTED-UNIT`: `E_UNIT_DIMENSION_MISMATCH` on nested `'šķīduma blīvums ρ (mL/mg)'`
  - `EDGE-PROSE-EXEMPTION`: free-text `feedback_lv` quoting `'ml'`, `'J/mol*K'`, `'mL/mg'` passed (`361` exempt prose fields)
- **Build gate (`order 9 terminology`) refusals (`tools/build.py`):**
  - `GATE-REFUSAL-DIMENSION-MISMATCH`: `returncode=1`, `artifact_written=false`, stderr head: `FAIL terminology gate (order 9, owner N10): data/terms.json:qty.density.unit: [E_UNIT_DIMENSION_MISMATCH] ...`
  - `GATE-REFUSAL-EXTRA-DATA-UNIT`: `returncode=1`, `artifact_written=false`, stderr head: `FAIL terminology gate (order 9, owner N10): <tmp>/planted_bad_unit.json:items[0].unit: [E_UNIT_AMBIGUOUS_DENOMINATOR] ...`

## 6. Runtime Lookup, Single-Sourcing, Degradation & Full-Document Scan

- **Missing-key error (`tools/check_n10_runtime.js`):** `SimTerms.lookup('does.not.exist')` threw `TermsError` (`code: "E_TERMS_MISSING_KEY"`, never `""`).
- **IUPAC pair rendering:** `SimTerms.lookup('iupac.acetic_acid')` → `'etiķskābe'`; `SimTerms.lookup('iupac.acetic_acid', { mode: 'iupac' })` → `'etiķskābe (IUPAC: etānskābe)'`.
- **Truncation & empty degradation:**
  - Truncated `#sim-terms` JSON → `#sim-terms-error` visible with `E_TERMS_JSON` naming `#sim-terms`, and subsequent `SimTerms.lookup('nav.sakums')` threw `E_TERMS_NOT_LOADED`.
  - Empty `#sim-terms` → `#sim-terms-error` visible with `E_TERMS_EMPTY`.
- **Single-sourcing in one pass:** mutating `nav.prakse`, `objectives.map_link_short`, `settings.theme.to_dark`, `hint.drawer.close`, and `hint.practice.help_button` in `#sim-terms` updated `#sim-nav`, `#coverage-list`, `#theme-toggle`, `#hint-drawer-close`, and `SimHintDrawer.renderHelpControl` in one pass (`5/5` true).
- **Full-document scan (`scan_rendered_document` + JS harness):**
  - Embedded terms in `#sim-terms`: `174`
  - `data-term-key` DOM bindings in `src/shell.html`: `18/18` resolved (`0` empty labels)
  - Unit strings checked in embedded `#sim-terms`: `42`
  - Nested parenthetical unit checked (`qty.density_with_unit_label`: `'šķīduma blīvums ρ (g/mL)'`): `1` clean pass; planted `'šķīduma blīvums ρ (mL/mg)'` rejected with `E_UNIT_DIMENSION_MISMATCH`.

## 7. Frozen Phase III Figure-Label Contract (`N11`–`N15`)

- Entry point: `SimTerms.resolveFigureLabel(spec, island)` for `kind` in `['axis', 'legend', 'annotation']`.
- Representative scratch proof (`tools/check_n10_runtime.js`):
  - `axis` (`fig.axis.concentration_mol_l`) → `'Molārā koncentrācija c (mol/L)'`
  - `axis` with nested unit (`qty.density_with_unit_label`) → `'šķīduma blīvums ρ (g/mL)'` (no duplicate unit suffix)
  - `axis` (`fig.axis.absorbance_a`) → `'Absorbance A (A)'`
  - `legend` (`fig.legend.catalyzed`) → `'Katalizēta reakcija'`
  - `annotation` (`fig.annot.no_extrapolation`) → `'Ārpus standartu lineārā diapazona ekstrapolācija nav pieļaujama'`
  - Degradation: `missing_key` → `E_TERMS_MISSING_KEY`; `bad_unit` (`'J/mol·K'`) → `E_UNIT_AMBIGUOUS_DENOMINATOR`; `dim_mismatch` (`qty.density` with `'mol/L'`) → `E_UNIT_DIMENSION_MISMATCH`.

## 8. Parity, Byte Accounting, Smoke Vector & Phase II Closure

- **Artifact:** `output/simulator.html` (`571,821` bytes, `sha256=821f74ae107f3cdcfad99680fe8ee62051f0b69a82d5f7fc37fd246ac4188167`, `build_id=40fd657aa16c5080`), byte-identical across two builds.
- **Byte contribution against Section 1.3:** `#sim-terms` `64,508` canonical bytes (`src/terms-loader.js` `13,611` B); total `runtime_js_bytes` `225,097` B (`<= 225,280` B ceiling; note `~67 KiB` of that `runtime_js_bytes` comes from N07/N08 inline `var` data projections inside the executable `<script>`), `css_bytes` `23,653` B, `template_overhead_bytes` `16,441` B.
- **Corpus parity (`evidence/N10_CORPUS_RECORD.json`):** byte-identical across two consecutive runs (`sha256=2ace7c1ab0cef3fafb39909b9a3a86447805ed0bfeb99e9d0a339a9ca343664d`).
- **In-file smoke subset (`SimSmoke`):** `4/4` PASS (`SMK-N06-COVERAGE-COUNTS`, `SMK-N07-MAP-DRAWER-WALK`, `SMK-N08-HINT-LADDER-WALK`, `SMK-N10-TERMS-GRAMMAR-LOOKUP`).
- **Prior-phase regressions:** N02, N03, N05, N06, N07, N08 runtime harnesses all PASS.
- **Paint check (`lite-shot --cdp -e falkon --theme light --anchor metodika`):** `evidence/N10_PAINT_CHECK.png` (`1280x1024`, `overflow=false`, `11,418` colours; render check only, not full WCAG/accessibility acceptance).
- **Phase II closure handoff:** The learner-facing vocabulary, unit grammar, build-gated unit/key lint, single-sourced runtime lookup, and frozen figure-label contract are complete and handed to Phase III (`N11`–`N15` inline SVG figures) and Phase IV (`N17`–`N19` engines). Note that sibling Phase II task **N09** (misconception registry) has not yet been executed in this workspace; its feedback interface keys are pre-authored in `#sim-terms` and `tools/validate_terms.py` accepts `data/n09_term_stubs.json` when N09 lands.
