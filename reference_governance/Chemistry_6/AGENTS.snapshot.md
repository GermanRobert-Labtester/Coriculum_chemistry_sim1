# AGENTS.md — Chemistry_6 · RSU Medicīniskā ķīmija · 13. temats

Standing contract; not a task plan. Speak to the owner in English; the student document remains Latvian. Canonical generated product: `Master_oksidesanas_reducesanas_procesi.html`. Read this file first, then the linked shard for the work at hand, `SOURCE_AUDIT.md`, relevant `qa/design.md`/`qa/verify.md`, and only then the authorized task. **Governance-only tasks may edit this file and the five `docs/governance/*.md` shards only.** Source, generator, QA evidence, and HTML are protected unless a task explicitly authorizes their edits. Never hand-edit generated HTML.

Evidence: `[TESTED]` = run with method/result; `[INSPECTED]` = directly read, not correctness proof; `[INFERRED]` = reasoned; `[UNVERIFIED]` = named check absent; `[TEXT-VERIFIED]` = source text/figure inspected for claim; `[METADATA-VERIFIED / SCOPE-ALIGNED]` = identity/topic only. A gate proves only what it measures. Never invent citations, pages, values, quotes or Latvian terms.

## 1. Goal & Architectural Philosophy

Continuously improve one canonical generated Topic 13 master for chemistry accuracy, teaching value, provenance, accessibility, print and restrained design. Keep the product self-contained and offline. Architecture priority: **HTML semantics + CSS state/layout → Python build-time work → strict TypeScript for irreducible client logic → tiny registry-approved JavaScript.** Never create a parallel master.

**`[OFFLOAD-SHARD]`:** For architecture/markup use [CSS tokens and layers](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers); for runtime use [language stack](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#language-stack).

## 2. Workspace Topology, Offload Routing & Open Issues

Root master selection is explicit; archived/QA HTML is noncanonical. `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` is the current proposal queue, not authorization. `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` are absent; `PROMPT_master_html.md` is historical. Do not create missing controls. Shard routing is below.

`[TESTED]` 2026-11-12 master fingerprint (F07 build): 1,826,786 B; SHA-256 `37e1877c98409c2df33cb6b48352aedd6b1723ffc99f0ca3abc68d608b0b8d2a`, mtime 2026-11-12 20:50:43. Product inventory (F07 static counts): 13 chapters plus `#print-answers`, 15 sections, 87 tables (all named; F04 added `#couple-matrix` in §4.9), 342 `<details>` (111 F03 value-evidence panels; F07 added `#review-key` in §12.8), 294 `value-ref` links, 9 inline SVG (all title+desc). Release PDF `qa/t33/master.pdf` (142 pp) is stale by hash (binds the T34 master via `qa/t33/manifest.json`); staleness is machine-reported by `make_manifest.py --check`. Generator: `tools/build_master.py`; values/equations: `tools/master_data.py`. Recheck fingerprints before relying on them.

| Workspace path | Role / lock |
|---|---|
| Five root source files (T13, LEC, L25, L21, L20) | Read-only authority set; see §3 and `TERMINOLOGY_AND_SOURCES.md#verified-source-registry` |
| `SOURCE_AUDIT.md` | Findings A–F and stable source IDs; preserve |
| `tools/*.py`, `tools/assets/*`, `tools/tokens.json` | Builder/data/styles/runtime and existing gates; implementation-only authorization |
| `tools/ts/`, configs | Not present in current inventory; target infrastructure only |
| `docs/governance/*.md` | Exactly five canonical offload shards; detailed governance specification |
| `qa/`, `archive/`, `workspace_skills/` | Evidence/snapshots/reference; preserve; inspect runner side effects before execution |

| Topic | Canonical shard |
|---|---|
| Issue forensics | [Open issues](docs/governance/OPEN_ISSUES_LEDGER.md#issue-index) |
| CSS, DOM, pedagogy, print | [Architecture](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#dom-class-registry) |
| JS, Python, TypeScript | [Infrastructure](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#language-stack) |
| Terms, claims, provenance | [Sources](docs/governance/TERMINOLOGY_AND_SOURCES.md#source-authority) |
| Changelog history | [Archive](docs/governance/CHANGELOG_ARCHIVE.md#archive-rule) |

`[TESTED]` There is no Git worktree at this root. Python 3.12.16 and Node 24.22.2 were recorded in prior governance; no TypeScript compiler/config. Current master static architecture measurements are in the issue ledger and runtime shard.

### Open Issues Index

Open unless repaired and evidenced in an authorized product pass. Static/source counts do not prove appearance or runtime behavior.

| ID | Category | Location | Rule violated / gap | Target | Details | Tag |
|---|---|---|---|---|---|---|
| JS-01 | JS-Bloat | Master scripts | 66,128 B / 1,357 lines / 4.540%; above all caps | HTML/CSS/TS | [JS-01](docs/governance/OPEN_ISSUES_LEDGER.md#js-01) | [TESTED] |
| JS-02 | JS-Bloat | `master.js` | 27 `innerHTML`, 9 templating `createElement` | Python/CSS | [JS-02](docs/governance/OPEN_ISSUES_LEDGER.md#js-02) | [TESTED] |
| JS-03 | JS-Bloat | `#master-data` | 56,636 B JSON island, itself >2% | Python | [JS-03](docs/governance/OPEN_ISSUES_LEDGER.md#js-03) | [TESTED] |
| JS-04 | JS-Bloat | I1–I6/audit/filter state | JS duplicates native state and precomputation | HTML/CSS/Python | [JS-04](docs/governance/OPEN_ISSUES_LEDGER.md#js-04) | [INSPECTED] |
| JS-05 | Infra-Gap | `tools/ts/` | No TS source/config/compiler | TypeScript | [JS-05](docs/governance/OPEN_ISSUES_LEDGER.md#js-05) | [TESTED] |
| CSS-01 | CSS-Arch | Embedded/master CSS | No layers; 116 `!important`; intrinsic-state gaps | CSS | [CSS-01](docs/governance/OPEN_ISSUES_LEDGER.md#css-01) | [TESTED] |
| CSS-02 | CSS-Arch | `tokens.json`, footer, SVG | No primitive/component/dark/OKLCH tiers or contrast ratios; one inline style | CSS/Python | [CSS-02](docs/governance/OPEN_ISSUES_LEDGER.md#css-02) | [INSPECTED] |
| HTML-01 | HTML-Defect | details/SVG | No named groups/dialog/popover/symbol reuse | HTML/Python | [HTML-01](docs/governance/OPEN_ISSUES_LEDGER.md#html-01) | [TESTED] |
| INFRA-01 | Infra-Gap | `tools/` | repaired in T20 — byte/contrast/aggregate gates + artifact manifest implemented; red on current master by design (JS-01/02/03, CSS-02, H-06) | Python | [INFRA-01](docs/governance/OPEN_ISSUES_LEDGER.md#infra-01) | [TESTED] |
| INFRA-02 | Infra-Gap | `qa/**/*.mjs` | 39 raw-JS QA tools; not all inspected | Python/TS | [INFRA-02](docs/governance/OPEN_ISSUES_LEDGER.md#infra-02) | [INSPECTED] |
| GOV-01 | Governance | Root control files | Required audit spec/build prompt absent; roadmap present | Governance | [GOV-01](docs/governance/OPEN_ISSUES_LEDGER.md#gov-01) | [TESTED] |
| GOV-02 | Governance | QA HTML copies | Legacy snapshots’ authority/content not re-audited | Governance | [GOV-02](docs/governance/OPEN_ISSUES_LEDGER.md#gov-02) | [INSPECTED] |
| GOV-03 | Evidence-Gap | `qa/design.md` | 15 task headings vs. note claiming all 20 are documented | Governance | [GOV-03](docs/governance/OPEN_ISSUES_LEDGER.md#gov-03) | [TESTED] |
| H-01 | HTML-Defect | `#sakums` | overclaim strings absent (0 matches, T08 grep); footer/§sakums text within measured claims | Python/HTML | [H-01](docs/governance/OPEN_ISSUES_LEDGER.md#h-01) | [TESTED] |
| H-02 | HTML-Defect | `prov-a22`, `prov-a15`, `#ch0` | repaired in T17 — prov ID suffixes, B12→`#sakums`; gate + 5 fixtures; 12 CDP nav scenarios | Python/HTML | [H-02](docs/governance/OPEN_ISSUES_LEDGER.md#h-02) | [TESTED] |
| H-03 | HTML-Defect | Equation aria-labels | repaired in T18 — `speakable()` Latvian labels; 0 of 200 expose `^ _ ->`; gate + 6 fixtures | Python/HTML | [H-03](docs/governance/OPEN_ISSUES_LEDGER.md#h-03) | [TESTED] |
| H-04 | HTML-Defect | `#audit-banner[hidden]` | repaired in T16 — utilities-layer `[hidden]` outranks display switch; `setAudit(false)` clears `#audit`; gate + 5 fixtures | CSS/HTML | [H-04](docs/governance/OPEN_ISSUES_LEDGER.md#h-04) | [TESTED] |
| H-05 | HTML-Defect | PbO₂ difference | repaired in T04 — prose derived from registry operands (0,34 V / 0,345 V); gate + fixtures block the defect shape | Python/HTML | [H-05](docs/governance/OPEN_ISSUES_LEDGER.md#h-05) | [TESTED] |
| H-06 | Unverified | `qa/master.pdf` | PDF timestamp precedes HTML; no current page review | Python/print | [H-06](docs/governance/OPEN_ISSUES_LEDGER.md#h-06) | [TESTED] |
| H-07 | Accessibility | 86 tables | repaired in T18 — all named (caption/aria-label); gate blocks unnamed + ancestor-named-only | Python/HTML | [H-07](docs/governance/OPEN_ISSUES_LEDGER.md#h-07) | [TESTED] |
| H-08 | HTML-Defect | `#ch11 .term-decision` | repaired in T02 — 32/32 decisions Latvian, gate blocks English | Python/HTML | [H-08](docs/governance/OPEN_ISSUES_LEDGER.md#h-08) | [TESTED] |
| H-09 | Source-Conflict | Potentials / `qa/verify.md` | CRC/Campbell identity unresolved; Cr₂O₇²⁻ has three values (1,33 / 1,232 / 1,36 V) | Sources | [H-09](docs/governance/OPEN_ISSUES_LEDGER.md#h-09) | [TESTED] |
| H-11 | Unverified | Biology / E°′ claims | O₂/Hb wording still unchecked; E°′ pH 7,0 condition now text-verified | Sources | [H-11](docs/governance/OPEN_ISSUES_LEDGER.md#h-11) | [INSPECTED] |
| H-13 | Unverified | SVG/CSS | SVG color half repaired in T10 (token classes + gate + inspected figures); contrast ratios now machine-checked (T20: 38/38 pairs pass); 65-selector mapping still open | CSS/SVG | [H-13](docs/governance/OPEN_ISSUES_LEDGER.md#h-13) | [TESTED] |
| H-14 | Accessibility | Controls at 390px | repaired in T18 — 0 sub-24px controls at 390/768/1440; inline links = documented 2.5.8 exception | CSS/HTML | [H-14](docs/governance/OPEN_ISSUES_LEDGER.md#h-14) | [TESTED] |
| H-15 | Unverified | C01–C170, trace | Five-pillar crosswalk not audited; saved recall 113/170 | Python/HTML | [H-15](docs/governance/OPEN_ISSUES_LEDGER.md#h-15) | [UNVERIFIED] |
| H-16 | Unverified | No-JS/print/keyboard/file URL | Not rerun for current master | HTML/CSS | [H-16](docs/governance/OPEN_ISSUES_LEDGER.md#h-16) | [UNVERIFIED] |
| H-17 | Source-Conflict | A11/D6/A25/A26 and terms | Lab, Pt/Pd and activity wording still open; IUPAC entries now read | Sources | [H-17](docs/governance/OPEN_ISSUES_LEDGER.md#h-17) | [TESTED] |
| H-18 | Unverified | Local source claims | T03 warrant claims reviewed against sources; the rest of the ledger still has no claim-to-source locator | Sources | [H-18](docs/governance/OPEN_ISSUES_LEDGER.md#h-18) | [TESTED] |

**`[OFFLOAD-SHARD]`:** Read the [issue index](docs/governance/OPEN_ISSUES_LEDGER.md#issue-index) and relevant issue entry in full before working on a listed defect; use the routing matrix above for all other topics.

## 3. Source Authority & Conflict Resolution

Scope order: T13 > LEC > L25 > L21 > L20. A demonstrably wrong source is logged with source wording, correction, reason and evidence; source error is not repeated as fact. Every taught claim maps to `qa/trace.md` or is a sourced `Papildinājums`. Read PDF page images when extraction flattens formula layout; inspect DOCX equation images. No made-up references. Full current source status and unresolved conflicts are in the source shard.

`qa/sources.csv` is the bibliographic registry (T03): every source id used by the ledger or the generator resolves there with scope, conditions, locator, access date, provenance tag and limitation. No scope means no warrant; a `[TEXT-VERIFIED]` row without a real inspected locator fails `tools/check_sources.py`.

**`[OFFLOAD-SHARD]`:** For a claim, source, value convention or Latvian term, read [source authority](docs/governance/TERMINOLOGY_AND_SOURCES.md#source-authority) and the [conflict](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) and [registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry) sections in full.

## 4. Output Contract & Four-Language Architecture

One standalone `.html`; CSS, SVG and licensed WOFF2 embedded; no CDN, external runtime, network, analytics or library. Works with JS disabled and `file://`.

| Tier | Language | Mandate |
|---|---|---|
| 1 | HTML5 + CSS | Semantic structure and ≥95% visual/interactive behavior; native state and modern layout |
| 2 | Python 3 stdlib | Extraction, generation, precomputation, SVG, static checks; `python3 -I` |
| 3 | TypeScript | Residual client source, strict mode, zero `any`, explicit DOM null checks, compiled/stripped |
| 4 | Raw JS | Last-resort whitelist micro-runtime only |

Executable JS ≤4,096 B, ≤100 formatted lines and <2% HTML bytes; all limits apply. JSON islands count toward percentage. Ban DOM templating/injection, JS controls replaceable by native HTML/CSS, scroll-jacking, decorative animation loops and external JS. Unregistered functions fail.

| Whitelisted function | Budget | Why CSS/Python cannot | Degradation |
|---|---|---|---|
| `markUnsure()` | ≤900 B / 30 lines | Persist marks across reload via Web Storage | `<noscript>`; marks/session state remain optional, prompts readable |
| `calcTitr()` | ≤1,800 B / 45 lines | Arbitrary user volume inputs | `<noscript>`; static example/template; print unaffected |
| `searchIndex()` | ≤1,396 B / ≤40 lines | Typed diacritic-folded filtering over a pre-rendered index cannot be precomputed per query | No-JS: static 13.H A–Z appendix; dialog hidden |
| `statePort()` | ≤1,800 B / ≤40 lines | F08: Blob export + strict File validation of the marks file (schema v1, reject-before-replace, confirm); writes only `redox-unsure-v1` | No-JS: hidden in `.js-only` `.weak-controls`; print suppressed |

CSS layer order: `reset, tokens, base, layout, components, utilities, print`; token tiers use `--p-<hue>-<step>` → existing semantic names → `--<component>-<property>`. IDs include `#sakums`, `#ch1`…`#ch13`, `#print-answers`, descriptive section IDs and unique provenance IDs. Class contract: structure `.chapter .chapter-head .prose`; equations `.eq .sp .op .arrow`; worked `.worked .ledger-rows .lrow`; mistake `.mistake .wrong-line .right-line`; recall `.recall-row .recall-item`; provenance `.side .kind`; tables `.table-wrap .scroll`; print `.print-only .transcript-static`. Full markup is offloaded.

**`[OFFLOAD-SHARD]`:** Before output/runtime edits read [native interaction patterns](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#native-interaction-patterns) and [JS budget and whitelist](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#js-budget-and-whitelist).

## 5. Content Standard — Five Pillars

Each concept carries **definition, mechanism/why, worked example with steps/units/check, common mistake (wrong → tempting cause → catching check → correct), canonical term**. Connect to stable source/concept IDs. Claim first; one idea per sentence; paragraphs ≤5 sentences; carry unrounded values and round once. Balance equations for atoms/charge and separately assess species plausibility.

**`[OFFLOAD-SHARD]`:** For markup blueprints and the complete concept contract read [five pillars markup](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup).

## 6. Terminology & High-Priority Corrections

Canonical distinctions: `oksidēšanās` process / `oksidēšana` action; `oksidēšanas pakāpe`; `oksidētājs` accepts electrons; `ekvivalences punkts` ≠ observed endpoint; `analīts` ≠ `analīze`; `jodometrija` (thiosulfate titrant) ≠ `jodimetrija` (iodine titrant); `ATF` (ATP once); `SHE` is electrode, not couple; `z` ≠ `n`. Confusable formulas require word/formula/charge/state together. Unverified portal forms remain `jāpārbauda`.

**`[OFFLOAD-SHARD]`:** Read the [terminology dictionary](docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary) for the full canonical table and [conflict log](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) for unresolved usage.

## 7. Design & CSS Engineering Standard

Design follows the electrochemical bench/electron ledger. Ban decorative gradients/glow/glass, structural emojis, uniform card grids that fragment prose, marketing hero, decorative motion, tracked-capital kickers and medallions. Body measure 60–75ch; contrast ≥4.5:1 normal text and ≥3:1 large text/UI in every state/theme; focus-visible, keyboard operation, reduced-motion, targets ≥24×24px or documented WCAG exception; no page overflow at 390/768/1440. Print opens details, hides controls, prints answers once and leaves templates blank. **Visual claim requires lite-shot Falkon PNG and direct inspection. Do not use Chrome/Chromium unless user explicitly allows it in current turn.**

**`[OFFLOAD-SHARD]`:** For layers/tokens, class contracts, accessibility and print read [CSS tokens and layers](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) and [print accessibility](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#print-accessibility).

## 8. Pedagogy & Native Interaction Patterns

Reveals use `<details>`; exclusive groups use shared `name`; filters/lenses use radio/checkbox + `:has()`; bounded steps use `:target`; previews use Popover API; dialogs use `<dialog>`. No-JS and print equivalents are mandatory. Controls need a learning purpose. Recall prompts map to `qa/plan.md` concepts; saved report is 113/170 checkable (66.47%), historical only. Do not treat count as learning acceptance.

**`[OFFLOAD-SHARD]`:** Read [native interaction patterns](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#native-interaction-patterns) before interaction changes.

## 9. Sourcing & Provenance Rules

For each claim record source identity, edition/version, exact locator, access date, result, applicability and limitation in `qa/verify.md`. Keep metadata-only distinct from text verification. Source labels: **Avots** (claim + locator), **Labots** (correction + source + check), **Papildinājums** (sourced addition). No invented pages/quotes/ISBN/DOI/URLs; inaccessible references stay unresolved. Full source registry and open conflict evidence are in the source shard.

The registry is the machine-checked form of this rule: `tools/check_sources.py` enforces mandatory metadata for resolved book citations, a resolvable locator for every `[TEXT-VERIFIED]` row, and the claim fields `system_scope`, `conditions`, `warrant_limit`, `provenance`.

| Source set | Purpose | Current evidence state |
|---|---|---|
| T13, LEC, L25, L21, L20 | Scope, theory and lab | Metadata/scope recorded; not freshly re-read |
| CRC, Campbell, LibreTexts | Potential/biology comparisons | Edition/conditions/locator open; `[UNVERIFIED]` |
| AkadTerm/termini.gov.lv, IUPAC Gold Book | Terms and definitions | Live text not rechecked; unresolved items stay `jāpārbauda` |

**`[OFFLOAD-SHARD]`:** Read the [verified source registry](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry) and [conflict log](docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log) in full for sourcing or terminology work.

## 10. Python/TS Infrastructure & New Features

Existing verifiers: balance, number, term, notation, oxidation-state, recall. Review side effects before running; some write to `qa/`. New tooling uses stdlib, `python3 -I`, non-zero failure, explicit input/output, QA-only reports and no implicit build/export. TypeScript config/compiler are absent. New feature must serve a T13 outcome, teach a state, be precomputed where possible, traced, sourced, and useful without JS/when printed. A “2026” label needs a source dated 2026. T03 added `tools/check_sources.py` (registry + claim warrants, three fixtures) and `tools/fetch_iupac_goldbook.py` (network evidence dump for Gold Book entries). T10 added `tools/check_svg.py` (plate contracts + five fixtures) and the SVG token tier; SVG colors live only in `master.css` classes because presentation attributes cannot take `var()`. T17 added `tools/check_anchors.py` (duplicate-ID, fragment and ARIA/`headers` IDREF gate with the explicit `#audit` mode-hash registry; fixtures `qa/anchor_fixtures/`, report `qa/anchors_gate.md`). T18 added `tools/check_a11y_names.py` (named tables, marker-free speech labels, SVG title/desc references; fixtures `qa/a11y_fixtures/`, report `qa/a11y_names_gate.md`) and `speakable()` equation labels in `tools/build_master.py`. T20 added `lint_js_budget.py`, `lint_agents_size.py`, `check_contrast.py`, aggregate `check_all.py` (task-dir-confined outputs; non-composable gates withheld with reasons) and `make_manifest.py` (`--check` fails on artifact drift, control drift or stale PDF); eight gates gained an optional `--report` redirect. T21 added `tools/termref.py` + `tools/check_term_refs.py` (F02 first-occurrence glossary term links, byte-exact policy; fixtures `qa/termref_fixtures/`). T22 added `tools/check_value_evidence.py` (F03 per-value evidence panels: 1:1 NUMBERS+COUPLES coverage, link graph, honest unresolved statuses; fixtures `qa/valueevidence_fixtures/`). F04 added `tools/check_couple_matrix.py` (25-couple matrix coverage exactly once, row condition state = registry derivation, mandated unaligned string; fixtures `qa/f04/couple_matrix_fixtures/`). F07 added `tools/check_review_sheet.py` (static §12.8 review sheet: slots, `#p-{pid}`-anchored prompts, `strip_coeffs()` skeletons + `#review-key`, no state hooks, one-page print; seven inline fixtures). F08 added `tools/check_state_port.py` (state-port gate; fixtures `qa/f08/fixtures/`).

**`[OFFLOAD-SHARD]`:** Read [Python CLI](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli), [TypeScript contract](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#typescript-contract), and [2026 literature rule](docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026) before infrastructure or new-feature work.

## 11. Editing, Non-Regression & Byte Budget

No source or generated output edits without explicit task authorization. For an authorized build: fingerprint, archive, edit canonical sources, rebuild, run relevant gates after side-effect review, inspect 390/768/1440 and keyboard/reduced-motion/JS-off/`file://`, regenerate and inspect every PDF page, update QA evidence and the canonical change log. Governance-only: touch only `AGENTS.md` and five shards; record pre/post master SHA-256, byte size, mtime. `AGENTS.md` ≤24,576 B (target 14,336–20,480 B). Keep the 10 newest run entries in full; archive older entries.

| Date | Sections/shards | Change | Reason | Evidence |
|---|---|---|---|---|
| 2026-11-12 | §4, §10; F08 | Task 46 F08: eksports/imports — `statePort()` ≤1,800 B/40 līn. reģistrs pirms funkcijas (1,719 B/32); shēma v1 `{version:1,unsure_ids}` (bez `preferences`), caps 8192 B/400 ID, PID_RE, reject-before-replace ar `confirm()`, imports krusto ar dokumenta pid; kontroles `.weak-controls` (js-only/printā slēptas), `#weak-dl` bez `createElement`; vārti `check_state_port.py` R1–R4 + 10 fiksētie | Pilns darbs — īpašnieks atcēla DEFER (T19/T20 pabeigti) | Master 1,826,786 `37e1877c…b8d2a` → 1,829,918 `0213a11a…bdd7` B (+3,132; exec 66,582→68,572); vārti 20/22 (sarkanā tikai JS-01/02/03 + CSS-02); fiksētie 10/10; falkon 12 scenāriji (round-trip, noraidījumi bez zaudēm, pid atzarošana, 0 pieprasījumi, klaviatūra, bez-JS, bez pārpildes); Chromium (apstiprināts) release PDF pārsiets 169 lpp., lpp. 89.–92. inspektētas (12.8 1 lapā, atbildes 1×, lite-shot PNG), H-06 aizvērts; `qa/f08/`, `qa/design.md` Task 46, `qa/verify.md` F08, `archive/master.pre-f08.20261112-f08run.html`; F07 rinda arhivēta |

**`[OFFLOAD-SHARD]`:** Read [archive rule](docs/governance/CHANGELOG_ARCHIVE.md#archive-rule) for history retention and run evidence.

## 12. Done Definition & Verification

- [ ] Source claims have correct provenance/conditions; equations balance and are chemically plausible; numbers/units/rounding reconcile; terminology gate passes.
- [ ] Every source has a registry row with scope, limitation and provenance; `[TEXT-VERIFIED]` rows point at an inspected locator; no claim outruns its sources (`tools/check_sources.py`).
- [ ] JS bytes/lines/percentage, banned patterns and registry pass; CSS layers/tokens/inline style and contrast pass; anchors, labels, tables and SVGs are named.
- [ ] Keyboard, focus, reduced motion, no-JS, `file://`, offline, 390/768/1440 reflow, current PDF pages, templates, and one-time answers are checked on current build.
- [ ] Visual claims use directly inspected lite-shot image; saved QA is not fresh proof.
- [ ] Governance-only: only permitted docs changed, shard links resolve, AGENTS ≤24,576 B, and protected master fingerprint matches.

**`[OFFLOAD-SHARD]`:** Read [verification suite](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite) for detailed gates and evidence requirements.
