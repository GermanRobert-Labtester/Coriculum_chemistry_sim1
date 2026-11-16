# Architecture, CSS and DOM Contracts

> Parent Contract: `../../AGENTS.md`  
> Extends: AGENTS.md §4, §5, §7, §8  
> Last updated: 2026-11-07 · Status: `[INSPECTED]` contract consolidated from the standing blueprint; live conformance is reported separately.

## CSS tokens and layers

### [CSS-TOKENS-AND-LAYERS]

Cascade order, declared as the first stylesheet statement:

```css
@layer reset, tokens, base, layout, components, utilities, print;
```

Every selector rule belongs to one declared layer. `!important` is prohibited except where narrowly required in `reset` or `utilities`. Zero inline `style` attributes. No raw hex/rgb color literals outside `tokens`.

Token ownership is one-way and has one owner per value:

| Tier | Naming pattern | Examples / rule |
|---|---|---|
| Primitive | `--p-*` | Intended palette layer. Live master has 0 `--p-*` tokens. `[TESTED]` |
| Semantic | `--paper`, `--ground`, `--panel`, `--plot`, `--ink`, `--ink-2`, `--muted`, `--rule`, `--rule-soft`, `--grid`, `--signal`, `--signal-dark`, `--second`, `--second-dark`, `--select` | Current 15 color roles; values below. |
| Type | `--serif`, `--sans`, `--t1`…`--t5` | Five-step scale; type and space use `clamp()` where fluidity is useful. |
| Measure | `--measure`, `--measure-rail`, `--measure-solo`, `--measure-wide`, `--max` | Body prose 60–75ch. |
| Space | `--s4`…`--s64` | Named spacing scale. |
| Component | `--instr-*`, `--plate-*` | Intended component layer. Live master has 0 tokens with these prefixes. `[TESTED]` |

The live system uses semantic roles directly; the 3-tier primitive/semantic/component contract is not implemented. Color values below are inspected in the live master and `DESIGN.md`, not recomputed in this run. Values are hex; there are no OKLCH declarations in the live palette.

### [CSS-COLOR-DICTIONARY]

| Token | Light | Dark | Role |
|---|---|---|---|
| `--paper` | `#f7f8f5` | `#101513` | Page |
| `--ground` | `#e9eeeb` | `#0b100e` | Declared ground; historical/print rules |
| `--panel` | `#eef2ef` | `#171e1b` | Highlighted row |
| `--plot` | `#fbfcf9` | `#121815` | Plot ground/label halo |
| `--ink` | `#15231f` | `#e4eae6` | Main text, axes, data curve, heavy rules |
| `--ink-2` | `#2a3934` | `#c3cdc8` | Standfirst, lede, quotations |
| `--muted` | `#4d5c57` | `#8e9c97` | Captions, tags, ticks |
| `--rule` | `#b9c5bf` | `#353f3c` | Light rules |
| `--rule-soft` | `#d7dfdb` | `#242e2b` | Table row separators |
| `--grid` | `#dce3df` | `#262f2c` | Plot grid |
| `--signal` | `#006b68` | `#3fa9a2` | Teal, catalysed/modified series |
| `--signal-dark` | `#004f4d` | `#6bcfc7` | Teal text role |
| `--second` | `#8a3557` | `#e08fae` | Bordeaux, reference/error/correction |
| `--second-dark` | `#6c2742` | `#eda6bf` | Bordeaux text role |
| `--select` | `#c9dfda` | `#1e3a37` | Text selection |

High-contrast overrides in the master: light `--muted:#34423d`, `--rule:#5f6d68`, `--rule-soft:#5f6d68`, `--grid:#7d8c86`, `--signal:#004f4d`, `--second:#6c2742`; dark `--rule:#6b7874`, `--rule-soft:#5f6b68`, `--grid:#5f6b68`, `--muted:#b3c1bc`, `--signal:#5fc4bc`, `--signal-dark:#86ddd5`, `--second:#ec9fbb`, `--second-dark:#f5b3cb`. Print redefines all 15 roles to white/greys; see `DESIGN.md` §7 and master `@media print`.

Recorded A9 contrast output in `DESIGN.md` (historical verifier result, not rerun here): light worst-ground text—ink 13.8:1, muted 6.0:1, signal-dark 8.0:1, second-dark 8.9:1; plot signal/second 6.2:1 / 7.5:1; rule 1.67:1. Dark—ink 13.9:1, muted 5.9:1, signal-dark 9.2:1, second-dark 8.7:1; plot signal/second 6.3:1 / 7.5:1; rule 1.69:1. `DESIGN.md` reports other worst-ground measurements (light muted 6.0, signal-dark 8.0; dark muted 5.9, signal-dark 9.2) with rounded values; verify fresh before release. High-contrast target: rules/grid ≥3:1 and muted ≥7:1. Table-rule contrast is intentionally below 3:1 in standard themes; padding also separates rows and the rule does not convey data.

### [CSS-LAYOUT-ACCESS-PRINT]

Use intrinsic grid/flex sizing; `@container` and `subgrid` when a component depends on its container; `clamp()` for fluid type/space; `:has()`, `:checked`, `:target`, and `:focus-within` for native CSS state; `@starting-style` only for useful non-decorative entry transitions; visible `:focus-visible`; `prefers-reduced-motion`; `forced-colors`; and no color-only encoding. WCAG 2.2 AA gates: normal text ≥4.5:1; large text, UI and essential graphics ≥3:1 in every theme.

Print belongs in `@layer print`. Expand every disclosure without JS using supported `::details-content`; R1 `printOpen` is only a compatibility fallback. Keep answers, avoid clipping/stranded headings, and preserve grayscale distinction. Browser engine support must be tested and recorded.

Anti-slop contract: no decorative gradients, glow, glass effects, shadows, structural emoji, hero banners, uniform card grids that fragment prose, stock imagery, or decorative animation. Visual elements encode course data or structure.

## DOM contracts

### [DOM-COMPONENTS]

| Component | Required structure / invariant |
|---|---|
| Document | `main#sakums`; one primary `h1`; logical heading order; chapters `#ch0`–`#ch17`; appendix `#appA`. |
| Chapter | `.chapter`, `.chapter-head`; content rows `.row` with exactly one of `.row--rail`, `.row--solo`, `.row--full`; prose `.prose`, `.rail`, `.lead`. |
| Callouts | `.callout` with `.correction` or `.terminology` when applicable; source text and correction remain distinct. |
| Formula/table | `.formula`; `.table-wrap > table` with `<caption>` and scoped row/column `<th>`. |
| Figure | `.plate` inline SVG with `role="img"`, `<title>`/`<desc>` or equivalent labelled reference, direct labels, and non-color encoding. |
| Learning | `.qa`, `.errblock` (`Students domā / Kāpēc tas vilina / Pareizi / Ātrā pārbaude`), `.ladder`, `.flashcards`, `.report-doc`. |
| Instrument | `.instrument`, labelled `<fieldset>`, `<output>`, `role="status"`, static `.fallback-details`, and `<noscript>` guidance. |
| Provenance | `.prov` with source/correction/supplement/model-answer tag. |

IDs use `#ch*`, `#appA*`, `#instr-*`, `#fig-*`, `#t*`; IDs are unique/stable and every local `href="#…"` resolves. A content SVG has a programmatic name and a short description appropriate to its learning role. Use `<symbol>/<use>` only when shared geometry remains maintainable and accessible; reuse is not mandatory.

## Five pillars markup

### [FIVE-PILLARS-MARKUP]

| Pillar | Required evidence in a teaching chapter |
|---|---|
| Correct concepts | Variables, assumptions, meaning, units and limits; overall order is not molecularity. |
| Source fidelity | Course statement is visible as such; sourced correction remains adjacent and attributed. |
| Explanation | Equation, graph and physical meaning are connected in plain Latvian. |
| Worked examples/errors | Assumptions and units shown; four-part misconception block. |
| Retrieval | Source question and labelled model answer; read-off tolerance stated. |

Chapters 1–12 apply all five. Chapters 0 and 13–17 apply relevant pillars. Distinguish 22 lecture, 11 MU and 6 lab source questions from supplemental pharmacokinetics, methanol/fomepizole, Lineweaver–Burk, inhibition, induced fit, instruments and lab-report material.

## Pedagogical patterns

### [PEDAGOGICAL-PATTERNS]

| Need | Native pattern | Required fallback |
|---|---|---|
| Disclosure/answer | `<details>/<summary>`; shared `name` for exclusive groups. | Summary remains keyboard-operable. |
| Tabs, stepper, mode, filter, occlusion | Radio/checkbox + `:checked`/`:has()`; `:target` for deep links. | Useful static content remains reachable. |
| Term/footnote preview | Popover API (`popover`, `popovertarget`, `popovertargetaction`). | Inline term/source remains available. |
| Modal task | `<dialog>` only when modality is required. | Non-modal reading path remains. |
| Numeric calculation | `<form>/<fieldset>/<output>` + R2. | Precomputed figures/tables in `.fallback-details`. |

Each interaction has an outcome/error purpose, keyboard path, static fallback and deterministic verification. No runtime persistence, network, scoring, randomization or decorative motion. Core reading/navigation has no JS dependency.
