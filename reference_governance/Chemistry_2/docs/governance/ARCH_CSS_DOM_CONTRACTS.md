# Architecture, CSS and DOM Contracts

**Parent Contract:** `../../AGENTS.md`  
**Extends:** AGENTS.md §§4, 5, 7, 8  
**Last updated:** 2026-11-07 · **Status:** [INSPECTED] current sources statically scanned; no fresh visual acceptance.

This shard contains detailed implementation contracts. Current product defects remain in `OPEN_ISSUES_LEDGER.md`; a specification is not evidence that the master implements it.

## [CSS-TOKENS-AND-LAYERS]

**Token tiers, layers and measurable styles.**

### Token tiers

| Tier | Pattern / observed names | Rule |
|---|---|---|
| Primitive palette | `--p-ground`, `--p-surface`, `--p-ink`, `--p-line`, `--p-accent`, `--p-rule`, `--p-mistake`, `--p-verified`, plot/focus primitives | Literal color values only at this tier; provide hex fallback before OKLCH where used. |
| Semantic | `--ground`, `--surface`, `--surface-2`, `--ink`, `--ink-2`, `--line`, `--line-strong`, `--accent`, `--on-accent`, `--rule`, `--mistake`, `--verified`, `--plot-grid`, `--plot-axis`, `--plot-muted`, `--focus` | Theme overrides map primitives to meanings; maintain light, dark and print values. |
| Layout/type/space | `--font`, `--page`, `--rail`, `--gap`, `--measure`, `--text-*`, `--space-1`…`--space-9`, `--print-*` | Body measure 60–75ch; current design target 66ch; use tabular figures for measurements. |
| Component | `--radius`, `--control-min-size`, `--focus-ring-*`, `--step`, `--ease`, and any component-scoped `--*` | Define only when reuse or state semantics justify a component token; do not encode one-off arbitrary values as design-system tokens. |

2026-11-07 static scan found the primitive and semantic families above and 152 custom-property declarations across the embedded style. A complete tier/value/contrast inventory has not been measured. Do not invent contrast ratios.

### Cascade layers

Canonical order: `@layer reset, tokens, base, layout, components, utilities, print;`. Put rule bodies in their named layers only after verifying support and fallback behavior. **Current compatibility constraint:** `build/style.css` documents that falkon/falkon drop rules wrapped in layers; its rule bodies are intentionally outside layers. The declaration alone does not satisfy the layered architecture requirement. See `OPEN_ISSUES_LEDGER.md#iss-css-01`.

Use intrinsic responsive layout (`minmax`, flexible tracks, `clamp`, `@container` where supported), CSS grid/subgrid where tested, and native state selectors (`:has`, `:checked`, `:target`, `:focus-within`). No zero-value claims from source declarations alone. Honor `prefers-reduced-motion`; print forces a light palette and removes fixed/sticky behavior.

## [DOM-CLASS-REGISTRY]

**Stable structure and component vocabulary.**

| Contract | Required pattern |
|---|---|
| Document | One self-contained `<html lang="lv">`; landmarks `header`, `nav`, `main`, `footer`; one `h1`; ordered heading hierarchy. |
| Chapters | `section.chapter#ch-1`…`#ch-16`; subsections use stable `chN-kebab-case` IDs. |
| Chapter headings | `.chapter`, `.chapter-head`, `.chapter-lead`; avoid parallel page-shell/card systems. |
| Semantic roles | `.role.role--rule`, `.role--mistake`, `.role--verified`, `.role--source`; only three callout roles are visually emphasized; source/auxiliary labels remain neutral. |
| Equations and reasoning | `.formula`, `.calc`, `.steps`, `.mistake-pair`; label givens, units, intermediate values and rounding endpoint. |
| Figures and data | `.plate`, `.figure-scroll`, `.data-table`, `.table-scroll`; tables have caption and scoped headers. Inline SVG has `role="img"`, `<title>`, `<desc>` and shared plot tokens. |
| Recall | `.recall-block`, `.recall-item`; answer content excluded from search; native disclosure and accessible print expansion. |
| Instruments | `.instrument__form`, `.instrument__out`, `.instrument__cases`; validate units, decimal convention and input range; show static/print fallback. |
| Terms/sources | `.gloss`, `.source-line`; English terms use `lang="en"`; source notes state evidence level. |

Inline styles and event-handler attributes are prohibited. Avoid duplicate IDs and unnamed/ambiguous controls. Native HTML semantics precede script behavior.

## [FIVE-PILLARS-MARKUP]

**Five-pillar content record.**

Every examinable concept covers each applicable pillar. Mark inapplicability and why; absence is not inferred from a missing field.

| Pillar | Minimum content | Typical structure |
|---|---|---|
| Definition | Canonical term, symbol, unit, scope | heading + concise definition/table row |
| Mechanism | Why/how, assumptions and limits | prose or labelled mechanism figure |
| Worked example | Recomputed values, units, precision and interpretation | `.formula`/`.calc` + `.steps` |
| Common mistake | Symptom → cause → correction | `.role--mistake` or `.mistake-pair` |
| Canonical term | Latvian term and sourced English equivalent | `.gloss`; English span with `lang="en"` |

Label course statements `avotā`, supported additions `papildinājums`, and invented numbers `ilustratīvs piemērs`. Preserve course wording where quoted; put departures in the source-change log with locator, original, correction, reason and C/H/V confidence. Recompute displayed calculations in code, but a numerical gate does not establish source correctness.

## [PEDAGOGICAL-PATTERNS]

**Native interaction, zero-JS and print.**

| Need | Preferred primitive | Fallback / invariant |
|---|---|---|
| Exclusive disclosure | `<details name="group">` where exclusive behavior is useful | Each answer remains readable and keyboard reachable. |
| Dialog | `<dialog>` with labelled title and native close behavior | Core reading content is not trapped behind script-only modal state. |
| Glossary preview | `popover` / `popovertarget` | Term link or adjacent definition remains available. |
| Tab-like view | radio inputs with labels and `:checked`, or `:target` navigation | No-JS state change; clear focus and selected-state cues. |
| Recall answers | native `<details>` | Closed answers excluded from search; print opens answer once, with no duplicated sheet. |
| Theme | CSS `prefers-color-scheme`; optional tiny persisted preference | Core page remains legible if JavaScript or storage is unavailable. |
| Calculations | static worked cases plus optional arbitrary-input calculator | `<noscript>`/static explanation visible; no silent persistence. |

Print contract: force light colors; expand disclosures with engine-appropriate rules (including Firefox `::details-content { content-visibility: visible; }` where required); flatten sticky/fixed elements; keep rows and captions with figures; provide page numbering, contents and colophon; inspect every exported page. Browser differences require evidence, not assumptions.

## [ANTI-SLOP-AND-ACCESSIBILITY]

**Visual and interaction gates.**

- Palette: low-chroma cool ground, deep ink, restrained accent. Hierarchy by spacing, scale and weight; use real data graphics.
- Prohibited: gradients, glow, glassmorphism, structural emoji, uniform prose-fragmenting card grids, hero banners, decorative motion, number medallions, pill badges, gamified progress, tracked microtype.
- At most two callouts per screen height; no nested callouts. At most two type families.
- WCAG 2.2 AA: normal text ≥4.5:1; large text and UI ≥3:1; visible focus ≥3:1; targets ≥44px; report actual measured ratios for every semantic pair in light/dark states.
- Keyboard reading/navigation must work with zero JS. Label controls; preserve non-color cues, SVG titles/descriptions and language tags. Honor reduced-motion preferences.
- Visual/UI/layout/SVG/style/theme/reflow acceptance requires a `lite-shot` PNG captured with falkon or falkon and direct image inspection, under the root `VISUAL_VERIFICATION.md` procedure. Source and DOM inspection alone are not visual evidence.
