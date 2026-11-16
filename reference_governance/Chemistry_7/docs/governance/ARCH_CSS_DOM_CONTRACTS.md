# Architecture, CSS and DOM Contracts

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 5, 7, 8  
Last updated: 2026-11-12 (T18; T17, T16b, T13, T12, T14, T11)  
Verification: `[INSPECTED]` contract and source inventory; accessibility/render acceptance remains open; T05 band-model prose/figure-pointer edits verified by C46/C47 harness gates; T06 derivation-chain edits verified by C48; T07 Lab 6B procedure edits verified by C49 (desktop 1280 px renders inspected `[SCREENSHOT-VERIFIED]`; mobile/print visual acceptance remains `[UNVERIFIED]`); T14 layered/tiered CSS verified by `gate_css_arch.py` G1–G8 (11 fixtures killed), rule-inventory parity diff, falkon light/dark/no-JS/320/390 captures and 65-page print inspection `[SCREENSHOT-VERIFIED]`; T17 narrow-screen reflow verified by probe + C33 (195/390/768/1440 + long-word, fixture-killed), falkon light/dark/no-JS/195/Tab-focus captures and 66-page print inspection `[SCREENSHOT-VERIFIED]`; T18 (2026-11-12) print acceptance re-confirmed on a fresh 66-page render (all pages inspected via 8 grids + margin/thin scans; G-17 page budget 100 recorded; C40 wide-rail and C35 SKIP≠PASS negative fixtures added), evidence `plan/t18-print.md`. F09/T06 (2026-11-12) route-selector re-housing verified by C25/C52, falkon light/dark/no-JS 1280+390 captures, a Chrome `.routes` element shot at 390 px, print p. 1/66 and a Chrome Tab/Enter keyboard probe `[SCREENSHOT-VERIFIED]` (Chrome owner-allowed, logged).

<a id="css-tokens-and-layers"></a>
## [CSS-TOKENS-AND-LAYERS] CSS layers, tokens and layout

### Required layer order

```css
@layer reset, tokens, base, layout, components, utilities, print;
```

Keep each concern in its named layer; print overrides live in `print`. Avoid style attributes. Target body measure is 60ch–75ch. Use intrinsic layout and fluid type where appropriate (`@container`, Grid `subgrid`, `clamp()`); selectors such as `:has()`, `:checked`, `:target`, `:focus-within`, `@starting-style` are allowed where they improve native state behavior. Do not add them for a feature checklist alone.

Since T14 (2026-11-11) this order is real and enforced: the statement opens the stylesheet, every rule in the main `<style>` and in every per-figure `<style class="fs">` block lives in a named layer (fs print boosts → `print`, mobile boosts → `utilities`), responsive overrides sit in the same layer as the rules they override (appended after them), and `tools/gate_css_arch.py` gates the statement, unlayered rules, hex placement, per-context `var()` resolution, alias cycles, duplicate declarations, print white-ground anchors and the `!important` registry (10 pinned declarations).

### Three-tier token schema

Primitive palette → semantic role → component token. Hex literals belong only in primitive definitions, not component rules or inline SVG. Calculate contrast from the actual foreground/background pair and live states.

| Family | Canonical tokens |
|---|---|
| Type | `--fs-display`, `--fs-h2`, `--fs-h3`, `--fs-body`, `--fs-sec`, `--fs-label` |
| Semantic | `--paper`, `--paper-2`, `--ink`, `--ink-2`, `--muted`, `--rule`, `--rule-2`, `--accent`, `--err`, `--ok`, `--orange`, `--serif`, `--sans`, `--gap` |
| Surface (T12, component tier) | `--surf-ex` (worked-example ground: `.formula`), `--surf-assess` (assessment-feedback ground: `.qa .a`/`.includes`, revealed `.recap` answers, `.warn.verdict`); print maps both to `--paper-p` (fills off on the white ground) |
| Figure | `--fig-ink`, `--fig-muted`, `--fig-accent`, `--fig-orange`, `--fig-paper`, `--fig-grid`, `--fig-rule`, `--fig-tint-uv`, `--fig-tint-prism`, `--fig-tint-liquid`, `--fig-tint-detector`, `--fig-tint-lamp`, `--fig-filament` |

Preserve light/dark and `prefers-contrast`; add `forced-colors`. Text contrast: ≥4.5:1; large text and meaningful UI boundaries: ≥3:1. Check focus, error, disabled, hover/active, dark, high contrast and print states. Meaning cannot rely on color alone.

### Frozen primitive naming (T14, 2026-11-11)

Since T14 the three tiers are real and machine-checked (gate G3/G4). Primitives live once in the tokens layer and are the only legal hex carriers:

- Color primitives: `--<role>-l` / `--<role>-d` for the light and dark palettes (`paper`, `paper-2`, `ink`, `ink-2`, `muted`, `rule`, `rule-2`, `accent`, `err`, `ok`, `orange`, `surf-ex`, `surf-assess`, `fig-grid`, `fig-rule`, `fig-tint-*`, `fig-filament`); print deltas `--paper-p` (#FFFFFF), `--ink-p` (#000000), `--ink-2-p` (#333333) — every other print value reuses a light primitive; high contrast `--rule-hc` (#000000) / `--rule-hc-w` (#FFFFFF).
- Scalar primitives: `--t-display/--t-h2/--t-h3/--t-body/--t-sec/--t-label`, `--f-serif`, `--f-sans`, `--sp-gap`.
- Semantic roles (the canonical names above) map to primitives per context; context blocks (OS-dark, toggle-dark, print, prefers-contrast) re-map only semantic names. Since T16b (2026-11-12) the theme checkbox inverts the system preference: OS-dark dark tokens bind on `:root:not(:has(#theme-toggle:checked))`, manual dark on the media-light-scoped `:root:has(#theme-toggle:checked)` — both blocks declare the identical dark table (C16-asserted), all four OS×checkbox states are reachable, and hc white-rule contexts follow the page state, not the OS. Component tier: `--fig-ink/--fig-muted/--fig-accent/--fig-orange/--fig-paper` alias their semantic token once on `:root` and inherit through the `var()` chain (dark blocks do not re-declare them); figure-specific `--fig-*` map to `--fig-*-l/-d` primitives.
- The print block maps every semantic token to a primitive ref and must never reference a `-d` primitive (C17 leak check); its `--paper`/`--fig-paper` → `--paper-p` mapping is the §7 white-ground anchor (gate G7).

### Current source palette snapshot (not a validated contrast report)

The token values below are unchanged since the T07 snapshot; since T14 they are expressed as primitive declarations plus `var()` aliases (values quoted here for reading, provenance in `src/00_head_masthead.part`). No OKLCH values are present in source; live WCAG ratios are computed by verify.py C29 from the resolved tables (lowest 5.14:1, dark err on paper-2). Forced colors is still absent (OI-06 open).

| Token | Light | Dark / OS-dark |
|---|---|---|
| `--paper` | `#FBFBF9` | `#14171A` |
| `--paper-2` | `#F5F4F0` | `#1E2328` |
| `--ink` | `#1A1D21` | `#E8E6E1` |
| `--ink-2` | `#3E454C` | `#C5C8CD` |
| `--muted` | `#525A62` | `#A2A8AF` |
| `--rule` | `#D8D6D0` | `#2E343B` |
| `--rule-2` | `#B9B6AE` | `#424A54` |
| `--accent` | `#19517B` | `#64A8E0` |
| `--err` | `#B3261E` | `#F26659` |
| `--ok` | `#1B6B5A` | `#42BA9E` |
| `--orange` | `#9A4A00` | `#F59E42` |
| `--fig-grid` | `#E7E5DF` | `#2A3038` |
| `--fig-rule` | `#C9C6BE` | `#3E4652` |
| `--fig-tint-uv` | `#EFF3F7` | `#1C2633` |
| `--fig-tint-prism` | `#DCE6EE` | `#283B50` |
| `--fig-tint-liquid` | `#D8E4EE` | `#233547` |
| `--fig-tint-detector` | `#E4E2DA` | `#2A2F35` |
| `--fig-tint-lamp` | `#F2E3B8` | `#383222` |
| `--fig-filament` | `#8A6A1F` | `#E5BE65` |
| `--fig-ink`, `--fig-muted`, `--fig-accent`, `--fig-orange`, `--fig-paper` | Alias semantic light values | Alias semantic dark values |
| `--rule`, `--rule-2` in `prefers-contrast: more` | `#000000` | nested OS-dark override: `#FFFFFF` |

Type/spacing tokens are scalar/font-family tokens, not colors: `--serif`, `--sans`, `--gap`, `--fs-display`, `--fs-h2`, `--fs-h3`, `--fs-body`, `--fs-sec`, `--fs-label`. Since T14 their raw values live on scalar primitives (`--t-*`, `--f-*`, `--sp-gap`) with the canonical names as `var()` aliases. Since T12 (2026-11-11) the component tier also carries two surface tokens (`--surf-ex`, `--surf-assess`; primitives `--surf-ex-l/-d` #EDF1F1/#1A232A, `--surf-assess-l/-d` #EEF2EF/#182425), applied only where role improves scanning; definition, mechanism and caution stay label/structure-carried per the recorded T13 note decision. verify.py C29 checks every text role against these surfaces in light and dark. Contrast must be computed for actual foreground/background and state pairs, including UI boundaries/focus, dark, high contrast, forced colors and print.

## [DOM-TAXONOMY] Canonical IDs, landmarks and class registry

| Contract | Required form |
|---|---|
| Chapters | `#n0`–`#n15`; headings `#h0`–`#h15`; subsections `#n{chapter}-{sub}` |
| Recall | `#r0`–`#r12`, `#r10-graph` |
| Headings | One `h1`; no skipped levels; section order must be meaningful |
| Landmarks | `main`, `nav`, `aside`; use `article` only when semantically appropriate |
| Components | `.ch`, `.lede`, `.row > .prose`, `.rail`, `.note[data-role]`, `.nlabel`, `.nbody`, `.formula`, `.legendtab`, `dl.terms`, `.mist`, `.say`, `.recap`, `.qa`, `.tablewrap`, `figure.plate`, `.fig-scroll`, `.instrument[data-instrument]`, `.tag`, `.tnote`, `.src-list`, `#theme-toggle` |
| Tables | Caption, units, and `th[scope]`; narrow tables have labelled/focusable scroll region |
| SVG | `viewBox`, accessible name via `<title>` and `<desc>` referenced by `aria-labelledby`; instance meaning and caption retained |
| Inline styling | Zero `style` attributes; use classes/tokens and `<colgroup>` |

<a id="five-pillars-markup"></a>
## [FIVE-PILLARS-MARKUP] Five content pillars

Every key concept receives all applicable evidence below; deliberate exceptions are recorded. Class presence alone is not coverage.

| Pillar | Semantic evidence pattern |
|---|---|
| Definition | `dl.terms` or labelled `.note`; term and scope |
| Mechanism | Connected explanatory `.prose`; why the relationship holds |
| Worked example | `.formula` with units, real Lab 6B value or explicit `ilustratīvi` label |
| Common mistake | `.mist`/`.say`: tempting error, why, detection and correction |
| Canonical term | Latvian form, symbol, unit, provenance; glossary `§12.7` |

Maintain 16 chapters, Planck/Einstein, `ΔE=hν=hc/λ`, `λmax`, bands vs lines, UV/VIS, `A=lg(I0/I)`, calibration curve, Fe³⁺/SCN⁻, Q1–Q9 model answers, 10-item graph exercise, six-step frame, eight-point checklist and study routes. Paragraphs ≤4 sentences; sequences numbered; comparisons tabulated; define symbols at first use.

<a id="pedagogical-patterns"></a>
## [PEDAGOGICAL-PATTERNS] Native interaction and accessible fallback

- Disclosures/reveals: `<details><summary>`; use shared `name` only for logically exclusive groups.
- Modal: native `<dialog>` only when a modal interaction is necessary; maintain keyboard/focus and close behavior.
- Footnote preview: Popover API (`popover`, `popovertarget`, `popovertargetaction`) where semantically suitable.
- Theme/filter/reveal state: CSS (`:checked`, `:has()`, `:target`, `:focus-within`) first. No persisted theme state; no `localStorage` or network.
- Reading and navigation work without JS. For any residual instrument, a static worked example/table and `<noscript>` explanation preserve the result.
- 3–5 retrieval prompts per chapter; Q1–Q9 answered. R² is never a standalone validity claim; include residuals, intercept, range and blank context.
- Band formation (T05, 2026-11-09) is taught as a three-step mechanism (sublevels → lines → merging in solution + instrument); the source's absolute-zero/thermal story is quoted and marked as a simplification, never restated as current fact — guarded by verify.py C46/C47.
- Beer–Lambert derivation (T06, 2026-11-09) defines `T = I/I₀` before `A = −lg T` in prose and MathML, anchors the integration constant to the blank (`I(0) = I₀`), states the zero-concentration check (`c = 0 → T = 1 → A = 0`) as a construction consequence, gives a worked back-conversion from a protocol value, and binds every table-23 assumption violation to a bounded failure mode; §6.2 ties the slope unit to the concentration basis — guarded by verify.py C48.
- Lab 6B procedure (T07, 2026-11-10) presents the six protocol steps as numbered actions with an observable completion criterion each, separates blank zeroing (instrument operation) from blank composition (0,00 mL stock + 10,00 mL water, table 14 row 1) and from calibration-line construction (starts at (0; 0)), keeps bench actions inside the source boundary ("Nemainiet iekārtas uzstādījumus" quoted as protocol step; reagent lists/safety regimes not invented), explains unknown numbering 2–5 and the ≥3 requirement, and states dilution with V₂ as the total volume — guarded by verify.py C49; erratum E28 records that the "taises" [sic] schema typo is in both protocol files.
- T09 plates (2026-11-10): `fig-chain` (8. attēls, §10.2) visualizes the actual protocol chain blank → standards → A readings → line through (0; 0) → unknowns 2–5 → γ = A/k in two rows (before class / in class); its textual ordered-list equivalent is the adjacent 10.2. list (no duplicate list). `fig-evidence` (9. attēls, end of §10.8) maps the four evidence tag classes (avots/aprēķins/papildinājums/nav pārbaudīts) to concrete Lab 6B values, each with its table/section source; the literature column holds no LD 6B measurements. Both carry "Shēma, nav mērogā" markers and reconcile to tables 13.–16. / `tools/data.py`.
- T11 (2026-11-11): five-pillar coverage is a plan-level trace, not new markup classes — `plan/concept-coverage.csv` (18 concepts K01–K18 × 5 pillars; literal needle inside the anchor's span as substance evidence; reasoned NA exceptions) gated by read-only `tools/coverage.py` and verify.py C51. Study routes (F09/T06, 2026-11-12) live in their own `<nav class="routes" aria-label="Mācību ceļi">` after the TOC as three static ordered anchor sequences (bench/protocol, review, data/revision; mapping and rejection rationale in a `src/00` comment): plain links, no-JS reachable, print-visible (owner hybrid ruling supersedes the T11 screen-only detail), CSS in the `layout` layer with tokens only, ≥44 px link rows on coarse pointers; the recorded rollback trigger is route UI duplicating the TOC. Q1–Q9 answer keys audited; Q2/Q6/Q9 gained explicit "why the plausible alternative fails" refutations (`plan/t11-q-audit.md`, G-15).

## [ANTI-SLOP-AND-MOTION] Visual and print constraints

Calm monograph: one text face, one label face, neutral ground, one ink accent, no more than three semantic roles. Do not use gradients, glow/shadows, backdrop blur, grain, structural emoji/icons, hero banners, drop caps, per-chapter colors, pill badges, uniform card grids, centered body prose, tiny letter-spaced caps, titles over two lines, decorative monospace, parallax or decorative animation. Meaning is carried by labels, not color alone.

Motion is limited to purposeful beam motion ≤200 ms and must honor `prefers-reduced-motion`. Visible `:focus-visible`, keyboard operation, named controls and forced colors are required. Print: white ground; all disclosure content expanded with labels; no clipped tables, unreadable figures, one-word rails or orphan captions; quick reference starts on a new page; body text ≥9 pt; target page budget 100 pages per owner ruling G-17 (2026-11-12; >100 needs a new owner decision). Inspect every rendered page before visual acceptance.

## [SVG-AND-PRINT-MARKUP] Figures and print disclosure contract

Use checked data or label diagram “shēma, nav mērogā”. Every formula has symbol/unit legend, worked number and common mistake. Keep an equivalent table when a figure carries values. Assess symbol reuse before adding `<symbol>/<use>`; do not duplicate paths unnecessarily or force abstraction that harms per-figure accessibility. Print CSS must reveal native `<details>` without JavaScript mutation and keep labels/captions visible.

## [CURRENT-STRUCTURAL-SNAPSHOT] Existing master evidence

The current master has 16 `section` elements, one `main`, two `nav`s (TOC + F09/T06 routes; recount 2026-11-12, which also refreshed aside 18 and `<details>` 101), 18 `aside`, one `h1`, 101 `<details>`, 28 tables, 13 inline SVGs, and 9 `<figure>` wrappers. Since T14 (2026-11-11) the stylesheet is fully layered (`@layer reset, tokens, base, layout, components, utilities, print`; per-figure `class="fs"` blocks included) with three-tier tokens — the 2026-11-07 "no `@layer`" observation is resolved. Since T16 (2026-11-12) `:has()` carries the native theme checkbox and the seven recall masks, and three `forced-colors` blocks exist (T14-A11Y); still absent: `<dialog>`, `popover`, named details group, `@container`, `subgrid`. Since T13 (2026-11-11) inline styling is zero: the 129 parsed style attributes were migrated to layered classes/tokens and `<colgroup>` utility classes (OI-20 closed; computed-style parity probe IDENTICAL light/dark/mobile/print). These are `[TESTED]` structural counts, not semantic, keyboard, contrast, render or print acceptance. T05 (2026-11-09) added no figures: the band mechanism reuses the existing `fig-bands` schematic; figūru ģeometrija stays owned by T08 (`plan/figures.md` T05 note). T09 (2026-11-10) added two schematic plates in n10 (`fig-chain`, `fig-evidence`; V12/V13 in `plan/figures.md`), using shared CSS primitives `.fbox/.farr/.fct/.fcm/.fcr/.fcl/.fcs` (font-size stays an attribute for the C37 probe and per-figure print boost). Full details: [`OPEN_ISSUES_LEDGER.md`](OPEN_ISSUES_LEDGER.md#iss-019).
