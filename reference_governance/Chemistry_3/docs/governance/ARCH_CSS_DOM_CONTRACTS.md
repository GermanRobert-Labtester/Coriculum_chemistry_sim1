# Architecture, CSS, and DOM Contracts

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 5, 7, 8  
Last updated: 2026-11-07  
Verification status: requirements are normative; current master structure is `[INSPECTED]`, contrast/render acceptance is `[UNVERIFIED]`.

## Five pillars markup

1. **Truth:** numbers derive from structured task records and `build/calc.py`; calculate at full precision and round once to declared input precision. Preserve disagreements with A–F.
2. **Terminology:** one canonical term, quantity, symbol, and unit; quoted course variants receive an explicit mapping.
3. **Teaching:** each worked item exposes givens, asked quantity, formula choice, assumptions, unit-bearing route, rounded answer, dimensional/reasonableness check, likely first error, and transfer/self-check.
4. **Design:** readable, restrained, responsive, keyboard-operable and print-aware; visual claims require a captured and inspected PNG.
5. **Features and sources:** offline, tied to a named learning task, source-tagged, and usable without runtime JS for core reading/navigation.

### Component contracts

| Component | Canonical structure / invariant |
|---|---|
| Task | `article.task#t-*`; `.task-head`, `.task-id`, `.task-src`, `.route`, `.route-mini`, `.why`, `.answer-check`. Keep assumptions adjacent to calculation. |
| Term | `dfn#term-*`; stable IDs, one canonical Latvian definition, optional sourced English mapping. |
| Figure | `figure#fig-*`; `.figure-scroll`, keyboard-reachable scroll hint, SVG `<title>` and `<desc>`, visible caption, responsive/print rules. |
| Table | `table.table-plate` inside `.table-wrap`; `<caption>`, scoped header cells, readable small-screen behavior. |
| Callout | `.role-rule`, `.role-mistake`, `.role-verified`, `.source-note`, `.recall-block`; labels and shape/structure carry meaning as well as color. |
| Provenance | `.prov.p-source`, `.prov.p-add`, `.prov.p-ill` visibly distinguish *Avotā*, *Papildinājums*, *Ilustratīvs piemērs*. |
| Recall | `details.recall`; static prompt/answer available without JS. Script may only enhance per-visit state and answer concealment. |

The current generated master is `[INSPECTED]` with one `<h1>`, 16 chapter IDs `#n1`–`#n16`, 268 details, 67 articles, one `<main>`, three `<nav>`, one `<dialog>`, 77 SVGs with `role="img"`, two `<noscript>` blocks, zero inline `style=` attributes, and zero inline event handlers. It currently has 37 opening details tags with `name=`; semantic exclusivity must be reviewed per group rather than inferred from this count.

### Pedagogical patterns

#### Disclosures and answer groups

Use native `<details><summary>…</summary>…</details>` for answers and explanations. Give a shared `name` only to mutually exclusive alternatives in the same group. Keep unrelated answers independent. Native state, summary keyboard operation, and the answer content must work with JS disabled. Use `<dialog>` for a true task-oriented modal and Popover API for short anchored previews only when their fallbacks and print behavior are clear.

#### Example task blueprint

```html
<article class="task" id="t-…">
  <header class="task-head"><span class="task-id">…</span><span class="task-src">Avots …</span></header>
  <p class="given">Doti lielumi ar vienībām.</p>
  <p class="asked">Jāatrod …</p>
  <p class="assumption">Pieņēmums: …</p>
  <p class="route">Formula → pārveidošana → aprēķins ar vienībām.</p>
  <details class="recall"><summary>Pārbaudi sevi</summary><div class="recall-answer">…</div></details>
</article>
```

This is a structural pattern, not a source quote. Production markup is Python-generated and must retain the component classes/IDs above.

#### SVG and landmarks

Use one `<main>`, labelled navigation landmarks, semantic `article`/`section` hierarchy, and `aside` only for genuinely complementary material. SVGs need a meaningful `<title>` and `<desc>` or an explicit accessible name; do not add `role="img"` mechanically to decorative art. Reuse `<symbol>/<use>` only when geometry is genuinely repeated and accessible labeling remains correct. Current master has 77 labelled SVGs but no `symbol`/`use`; this is a reuse opportunity, not proof that every figure is defective.

## CSS tokens and layers

### Required layer order

The first CSS statement is:

```css
@layer reset, tokens, base, layout, components, utilities, print;
```

Place reset, tokens, base, layout, component, utility and print rules in their matching layers. Unlayered rules outrank layered normal declarations, so merely declaring the layer order does not satisfy the contract. Current inspection found the declaration and a print-layer block, while most rules remain unlayered.

### Token tiers

| Tier | Prefix | Owns | Example |
|---|---|---|---|
| Primitive | `--p-*` | Raw palette, spacing, type scale, dimensions. | `--p-blue-700`, `--p-space-4`, `--p-type-0`. |
| Semantic | `--t-*` | Meaning and theme mapping; only this tier changes between light/dark/print. | `--t-ground`, `--t-surface`, `--t-ink`, `--t-ink-muted`, `--t-accent`, `--t-line`, `--t-focus`. |
| Component | `--c-<component>-*` | Repeated component-specific choices mapped to semantic/primitive values. | `--c-task-border`, `--c-table-stripe`, `--c-figure-scroll-hint`. |

Do not create token aliases without repeated use. Avoid direct palette literals in component rules. Proposed prefixes describe the target architecture; current stylesheet remains flat and has no measured contrast table.

### Inspected current palette (not a verified contrast report)

| Role | Light | Dark |
|---|---|---|
| Ground | `#F3F7F8` | `#0F171B` |
| Surface | `#FBFDFD` | `#162228` |
| Ink | `#1E2B31` | `#E4EDF0` |
| Muted ink | `#51636C` | `#A9BDC6` |
| Accent | `#17627F` | `#7CC3DC` |
| Strong accent | `#1B4E63` | `#9BD6E8` |
| Line | `#CBD9DF` | `#34505C` |
| Focus | `#A34A00` | `#F0B45A` |
| Tone ladder 1–6 | `#E6F0F4`, `#CBE1E9`, `#A8CBD8`, `#6FA6BC`, `#2F6E88`, `#1B4E63` | `#1B2B33`, `#213843`, `#2A4B59`, `#3C6676`, `#5E93A7`, `#8FC0D2` |

No contrast ratio is certified here. Require fresh resolved-background WCAG calculations in light, dark, and print contexts.

### Layout, typography, and state

| Contract | Requirement |
|---|---|
| Measure | 60–75ch for sustained text; current inspected body token is 66ch and lead is 58ch. |
| Fluid type | `clamp()` for display scale; avoid viewport-only sizing and arbitrary per-component magic breakpoints. |
| Intrinsic layout | Prefer grid/flex intrinsic sizing; use `@container` for component-local adaptation and `subgrid` for aligned child grids where supported. |
| CSS state | Prefer `:has()`, `:checked`, `:target`, `:focus-within`, native details/dialog/popover state. No scroll listener for chapter state. |
| Motion | No decorative motion; `prefers-reduced-motion: reduce` removes transitions/animation and smooth scrolling. |
| Focus/targets | Visible `:focus-visible`; interactive targets at least 44×44 CSS px unless a documented WCAG exception applies. |
| Responsive figures | No clipping at 390 CSS px; scroll containers have visible, spoken, keyboard-reachable guidance when needed. SVG labels at least 12 px at target phone scale. |

## Five-pillar content and source contracts

Use Latvian decimal commas and a nonbreaking space before units. Preferred spellings: `mL`, `L`, `g`, `mg/mL`, `mol/L`; never imply that course `M` for mol/L is the same quantity as molar mass `M(B)`. Source-backed claims carry evidence tags as described in `TERMINOLOGY_AND_SOURCES.md#source-authority`.

Avoid gradients, glow, glass effects, ornamental shadows, structural emoji, hero banners, decorative animation, uniform cards that fragment sustained prose, tracked uppercase micro-labels, invented metrics, and color-only meaning. Cross-references remain underlined in print.

## Print and accessibility

`@layer print` must expand closed details without JS where supported; retain a JS fallback only if a permitted renderer test demonstrates a gap. Repeat table headers, prevent row splitting, keep source links identifiable, suppress non-print controls, and inspect page breaks. PDF targets are zero Type 3 fonts, chapter outline, tagged output or a dated limitation. WCAG 2.2 AA targets are ≥4.5:1 normal text and ≥3:1 large text/UI; static source inspection is not a conformance result. Manual keyboard and assistive-technology evidence remains required.
