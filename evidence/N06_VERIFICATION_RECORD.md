# N06 Verification Record — Start Screen, Objectives View, Design Tokens & Nine-Anchor Shell

**Status:** closed 2026-11-17 (UTC).  
**Label:** **VERIFIED (2026-11-17, this environment)**.  
**Visual inspection note:** `N06_PAINT_LIGHT.png`, `N06_PAINT_DARK.png`, and `N06_PAINT_SETTINGS.png` were captured via `lite-shot -e falkon --cdp` and visually inspected; they are render checks, not full WCAG browser/screen-reader acceptance (deferred to N32/N33/N37/N38).

---

## 1. Start Screen & Copy Lint (`#sakums`, `data/n06_term_stubs.json`)

### 1.1 Verbatim Latvian Panels & Scope Note

- **Official-facts panel (`#sakums-oficiali-fakti`, `data-epistemic="OFFICIAL"`, `PROGRAMME-SOURCED`):**
  > OFICIĀLIE PROGRAMMAS FAKTI — Kas noteikts programmā. Avots: `RSU_MedChem_Colloq1_Prog_LV_2025.pdf` (`PROGRAMME-SOURCED`): Formāts: klātienes pārbaudījums; darbs tiek rakstīts uz papīra. Maksimālais laiks: 3 stundas (180 minūtes). Septiņas programmas tēmas: (1) Ievads. Šķīdumi un ķīmiskās reakcijas; (2) Aprēķini un grafiskās metodes ķīmijā; (3) Šķīdumi un koncentrāciju aprēķini; (4) Termodinamika un tās piemēri bioloģiskajās sistēmās; (5) Kinētika un tās nozīme bioloģiskajās sistēmās; (6) Oksidēšanās – reducēšanās procesi; (7) Analīzes metodes ķīmijā. Oficiālā programma nenorāda uzdevumu skaitu, punktu svarus, sekmības slieksni, atļautos palīglīdzekļus vai precīzus jautājumu tipus.

- **Training-policy panel (`#sakums-politika`, `data-epistemic="PROPOSED"`):**
  > PROPOSED — mācību politikas priekšlikums — Simulācijas treniņmodelis. Šie parametri ir šī treniņsimulatora mācību politikas priekšlikums (PROPOSED), nevis oficiāls eksāmena nolikums: 100 treniņa punkti (PROPOSED): priekšlikums pa tēmām 1–7 ir 10 / 12 / 20 / 15 / 16 / 15 / 12 punkti. 3 treniņdarba formas — A, B un C (PROPOSED): katrā formā paredzēta 21 uzdevuma vieta (slots). Laika plānojums (PROPOSED): 170 darba minūtes + 10 pārbaudes minūtes oficiālo 180 minūšu rāmī. Struktūra (PROPOSED): 64 mācību rezultāti un 28 uzdevumu saimes ar 4 variantu specifikācijām katrā.

- **Scope note (`#sakums-tverums`, `role="note"`):**
  > Tvērums un godīguma piezīme: šis ir patstāvīgas mācīšanās palīglīdzeklis darbam bezsaistē. Tas nav oficiāls RSU kolokvija eksāmens, nepiešķir oficiālu vērtējumu vai apliecību, neveic uzraudzību un pēc noklusējuma saglabā sesijas stāvokli tikai operatīvajā atmiņā.

### 1.2 Copy Lint & N10 Stub Dependency

- **Copy lint (`tools/validate_n06_shell.py`):** `PASS` (`0` errors). Verified official panel claims match `RSU_MedChem_Colloq1_Prog_LV_2025.pdf`, training-policy claims carry `PROPOSED` labels, scope note states non-official/offline/in-memory bounds, and N25/N34 deferrals appear in `#iestatijumi`.
- **Negative fixture (`forbidden_endorsement_copy`):** Replacing `Patstāvīgas sagatavošanās` with `"Oficiāli apstiprināts eksāmens ar sertifikātu; ..."` failed copy lint by forbidden word (`sertifikātu`, `Oficiāli apstiprināts`).
- **N10 term-bank stub dependency (`data/n06_term_stubs.json`):** `21` N06 UI/panel keys recorded with `status: "stub-pending-N10"`, `target_closure_task: "N10"`.

---

## 2. Single-Sourced Objectives View & ARIA Foundation (`#saturs`, `src/coverage-view.js`, `src/start-view.js`)

- **Baseline rendering (`node tools/check_n06_runtime.js --json`):**
  - `#sakums-oficialas-temas`: `7` official topics populated from `#sim-coverage`.
  - `#coverage-nav`: `7` topic jump links.
  - `#coverage-list`: `64/64` outcomes rendered verbatim across 7 topics (`[9, 10, 11, 11, 10, 8, 5]`), every topic linking to `#karte-tema-N` (N07 slot) and `#prakse-tema-N` (N30 slot).
- **Single-sourcing fixture:** Editing Topic 1's `name_lv` (`SENTINELA TĒMA N06`) and `P1-01.statement_lv` (`SENTINELA REZULTĀTS N06`) in `#sim-coverage` updated `#sakums-oficialas-temas`, `#coverage-nav`, and `#coverage-list` simultaneously.
- **Markup-character escaping fixture (N35 precursor):** Injecting `"<img src=x onerror=alert(1)> & <b>skābe</b>"` into `P1-01.statement_lv` rendered verbatim as `textContent` inside `li#rezultats-P1-01` with child tags `["SPAN", "SPAN"]` (zero injected DOM elements).
- **ARIA foundation (`tools/validate_n06_shell.py`):** `PASS` — `1` `<main>`, `1` `<header>`, `1` `<footer>`, `3` uniquely named `<nav>` landmarks, `9` `<section>` landmarks via `aria-labelledby`, `1` `<h1>`, `0` heading level skips across all `h1`–`h3` headings, and `<button type="button" id="theme-toggle" aria-pressed="false">`.

---

## 3. Design Token Layer & Theme Toggle (`data/tokens.json`, `src/styles.css`, `src/theme-toggle.js`)

- **Tokens digest (`canonical_json_bytes` SHA-256):** `6b419c04be2db45a96e4eae04320bbb5799e09e4109ec132e299afe5e1b911ab` (handed to **N32**).
- **Completeness & use classes (`tools/validate_tokens.py`):** `26` required semantic tokens present in both `light` and `dark` themes (`0` missing, `0` undeclared extras); `27` declared color pairs with explicit `use_class` (`text-classed`, `boundary-classed`, `state-classed`), all clearing WCAG AA thresholds (`>= 4.5:1` text, `>= 3.0:1` boundaries/states) in both themes; `rem`-based typography with `16px` (`1rem`) body floor; `44px` (`2.75rem`) interactive target floor.
- **Negative fixture (`missing_token`):** Removing `--border-subtle` from `dark` failed `validate_tokens.py` (`Missing token '--border-subtle' in theme 'dark'`) and caused `tools/build.py` gate order `5` (`tokens`, owner `N06`) to exit `1` without writing any artifact.
- **Raw-value scan & negative fixture (`raw_css_values`):** `src/styles.css` passed with `0` raw hex colors, `0` color functions, and `0` raw `px`/`rem` sizing values. Injecting `color: #ff0000; font-size: 12px;` failed the scan (`2` findings) and caused `tools/build.py` gate `5` to refuse the build before writing.
- **Theme toggle state machine (`tools/check_n06_runtime.js`):**
  - Initial default: `data-theme="light"`, `aria-pressed="false"`, in-memory store (`AGENTS.md` compliance).
  - Click `#theme-toggle`: `data-theme="dark"`, `aria-pressed="true"`.
  - Keyboard `Space` on `#theme-toggle`: `data-theme="light"`, `aria-pressed="false"`, `preventDefault` invoked.
  - Opted-in adapter persist & restore: persisted `sim_theme_v1="dark"`, restored `data-theme="dark"` in a fresh document context.
  - No-store (`storage: null`) and throwing-store (`SecurityError`) degradation: degraded cleanly to `mode="memory"`, `degraded=true`, toggle remained operational without throwing.

---

## 4. Nine-Anchor Shell, Smoke Subset & Byte Accounting (`src/shell.html`, `src/smoke-subset.js`)

- **Structural contract (`tools/validate_n06_shell.py`):** `PASS` — `lang="lv"`, `1` executable `<script>`, `7` JSON islands in declared Section 1.2 order (`sim-coverage`, `sim-conventions`, `sim-bank`, `sim-forms`, `sim-golden-vectors`, `sim-terms`, `sim-analytics`), `9` unique ASCII blueprint anchors (`sakums`, `saturs`, `prakse`, `eksamens`, `rezultati`, `atskats`, `metodika`, `druka`, `iestatijumi`), `105` unique ASCII `id` attributes (`0` duplicates, `0` non-ASCII), `31` internal `#` links (`0` dangling), `0` external URLs.
- **Negative fixture (`external_url_injection`):** Injecting `https://cdn.example.invalid/style.css` failed `validate_n06_shell.py` with `external_urls_count=1` and exact URL/line context.
- **In-file smoke vector (`src/smoke-subset.js`, `SMK-N06-COVERAGE-COUNTS`):** `PASS` inside the shipped script (`7` topics, `64` outcomes `[9, 10, 11, 11, 10, 8, 5]`); negative tampered-expectation test failed naming `Topic 1`.
- **Section 1.3 byte accounting (`output/simulator.html` = `334,003` bytes, `sha256=98d88ccc71fb0e3c2ae8101d385ffafdba9f4e83fa3168b67b812ceea0bb86c1`, `build_id=234ce52d7341a63b`):**
  - CSS (`<style>` tokens + view styles): `13,546` bytes (ceiling `81,920` bytes / 80 KiB)
  - Runtime JS (single executable `<script>`): `65,150` bytes (ceiling `225,280` bytes / 220 KiB)
  - Embedded JSON islands (7 slots): `242,195` bytes
  - HTML template overhead: `13,112` bytes
- **Double-build & corpus parity:** Two consecutive runs of `python3 tools/build.py` produced byte-identical `output/simulator.html` and `output/build-manifest.json`; two consecutive runs of `python3 tools/n06_corpus.py` produced byte-identical `evidence/N06_CORPUS_RECORD.json` (`sha256=0975405f181488e0f31cb1c152befe80b83dccfc6c20819c2ba96b720a859e46`).
- **Prior-phase zero-regression:** `check_coverage_runtime.js`, `check_conventions_runtime.js`, and `check_golden_vectors_runtime.js` all re-ran `PASS`.
- **Falkon `lite-shot` render checks:**
  - `evidence/N06_PAINT_LIGHT.png` (`1280x1024`, `overflow=false`, `colors=11418`, `ink=50%`)
  - `evidence/N06_PAINT_DARK.png` (`1280x1024`, `overflow=false`, `colors=11155`, `ink=50%`)
  - `evidence/N06_PAINT_SETTINGS.png` (`1280x1024`, `#iestatijumi`, `overflow=false`, `colors=7391`, `ink=38%`)

---

## 5. Handoffs

- **To N32:** `data/tokens.json` (`tokens_digest=6b419c04be2db45a96e4eae04320bbb5799e09e4109ec132e299afe5e1b911ab`), `tools/validate_tokens.py` (completeness, use-class, and raw-value scanner), and `src/styles.css`.
- **To N07 / N30 / N21 / N23 / N25 / N34:** 9-anchor shell (`src/shell.html`), declared topic anchor slots (`#karte-tema-1`..`7`, `#prakse-tema-1`..`7`), `SimTheme` / store stub (`src/theme-toggle.js`), and pending settings slots (`#settings-storage-slot`, `#settings-print-slot`).
- **To N10:** `data/n06_term_stubs.json` (`21` Latvian interface/panel keys pending term-bank closure).
- **To N31:** `tools/validate_n06_shell.py` precursor checks and `tools/build.py` deterministic gates `5` (`tokens`) and `6` (`n06_shell`).
- **To Phases III–VIII:** `src/smoke-subset.js` (`SimSmoke` registry) initialized with `SMK-N06-COVERAGE-COUNTS`.
