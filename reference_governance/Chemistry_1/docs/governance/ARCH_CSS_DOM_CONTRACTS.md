# Architecture, CSS and DOM Contracts

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 5, 7, 8  
Last updated: 2026-11-07 · Status: `[INSPECTED]` current rules; visual acceptance remains `[UNVERIFIED]` unless noted.

## CSS-TOKENS-AND-LAYERS

The first layer statement is exactly `@layer reset, tokens, base, layout, components, utilities, print;`; every authored CSS rule belongs to one of those layers. Named layer order is invariant. The current canonical sheet has the ordered declaration and seven named layers; it has no `@container` or `subgrid` rules.

| Tier | Prefix / rule | Contract |
|---|---|---|
| Primitive | `--p-*` | Palette values, including the only allowed raw hex literals. Keep light and print values explicit; do not claim a dark theme unless implemented and checked. |
| Semantic | `--bg`, `--surface`, `--surface-2`, `--ink`, `--muted`, `--line`, `--def`, `--link`, `--def-bg`, `--err`, `--err-bg`, `--fix`, `--fix-bg`, `--focus`, `--field-*` | Meaning-based aliases to primitives; states and contrast must be checked for every supported theme. |
| Component | `--c-<component>-<property>` | Component roles only; reference semantic tokens wherever possible. |
| Supporting | `--s-*`, `--font-*`, `--measure`, `--rail`, `--gap` | Type scale, font stack, prose measure and layout rhythm. Use `clamp()` for fluid values. |

Current palette values and component mappings are source-owned in `build/assets/style.css`; this shard records the contract, not an alternate source of truth. Never copy a token value into a competing runtime stylesheet.

## DOM-COMPONENT-REGISTRY

Canonical output is one self-contained UTF-8 HTML document. Use one `<header>`, one `<nav id="saturs" class="toc">`, one `<main id="main">`, and one footer. The skip link targets `#main`. Chapter sections use `section.chapter` and the stable IDs defined by `build/build_master.py` (`sakums` through `pielikumi`; currently 17). Headings progress h1 → h2 → h3 without skipping levels. Every ID is unique and every internal fragment resolves.

| Role | Markup contract |
|---|---|
| Tier declaration | `p.tier` with a visible tier label. |
| Definition | `.defn`; definition text is visible without disclosure. |
| Mechanism | `.mech`; if a concept has no mechanism pillar, explain why in its concept map. |
| Worked example | `.work`; show units and reasoning in order. |
| Common mistake | `.mist`; give plausibility, correction and a check. |
| Canonical term | `.gdef`; one approved form and any distinction needed. |
| Supporting | `.lead`, `.pair`, `.note`, `details.deep`, `details.why`, `details.q`, `.self`, `.chapter-check`, `.scrub`, `.mx-wrap`, `.exam-sim`, `.eq-practice` (F03: `.ep-intro`, `.ep-item`, `.ep-eq`, `.ep-ledger`, `.ep-feas`, `.ep-wrong`), `.mistake-route` (F04: `.mr-group`, `.mr-list`, `.mr-card`, `.mr-head`, `.mr-id`, `.mr-wrong`, `.mr-action`, `.mr-jump`, `.mr-follow`, `.mist-route-link`, `.fb-mid`), `.review-sequence` (F07: `.rv-intro`, `.rv-days`, `.rv-day`, `.rv-n`, `.rv-date`, `input.rv-date-field`, `.rv-items`, `.rv-item`, `.rv-ex`, `.rv-recall`). Do not infer concept coverage from selector counts. |

HTML has zero `style="…"`, zero inline event handlers and zero `javascript:` URLs. Use real `<sub>`/`<sup>` and semantic controls. No data-driven HTML-string injection.

A scrollable region is keyboard-reachable: the F03 equation wrapper `.eq ep-eq` carries `role="group"`, an `aria-label` and `tabindex="0"`, `overflow-x` keeps long formulas inside the labelled box (the body clips page-level overflow), and the print layer re-opens it with `overflow: visible`. Verification tables use `scope="col"`/`scope="row"` headers; native `<details>` disclosures carry `data-kind` (r/a/t) and `data-seed`.

F07 adds one native form family: `#review-sequence` is a `<section>` of fourteen `<fieldset class="rv-day" role="group">` elements, each named by its `<legend>` (`<n>. diena <tēma>`). Every control is a native `<input>` with an explicit `id` plus a sibling `<label for>` — never a wrapping label that also carries a link, because then a click on the chapter name would toggle the checkbox instead of opening the chapter. The date field is a text input styled as a ruled line; it has no value, no `data-persist` hook and is never read back. The schedule itself is the `REVIEW_DAYS` literal in `build/build_master.py`; `build/check_links.py` parses that literal with `ast.literal_eval` (never by importing the builder, which writes the master) and fails the build when the emitted page disagrees with it.

## FIVE-PILLARS-MARKUP

Each assessed concept maps by stable concept/chapter ID to Definition, Mechanism, Worked Example, Common Mistake and Canonical Term. A non-applicable pillar must be explained and tracked as an issue; no silent omission. All answers use native disclosures and remain available with JavaScript disabled.

```html
<section class="chapter" id="stable-topic-id">
  <h2>Concept</h2>
  <p class="defn"><strong>Definīcija.</strong> ...</p>
  <p class="mech"><strong>Kāpēc.</strong> ...</p>
  <div class="work"><h3>Piemērs</h3>...</div>
  <aside class="mist"><strong>Biežākā kļūda.</strong> ...</aside>
  <p class="gdef"><strong>Termins.</strong> ...</p>
  <details class="q"><summary>Pārbaudi sevi</summary><div class="answer">...</div></details>
</section>
```

Numbered calculation values use `span.num[data-exact][data-expr]` and are checked by `build/check_numbers.py`. Course corrections retain ID, original wording, corrected wording, reason, exact locator and evidence status. Do not fabricate assessed topics to fill a visual grid.

## PEDAGOGICAL-PATTERNS

Use `<details>/<summary>` for disclosures, shared `name="…"` for exclusive disclosures where supported, `<dialog>` for modal tasks, and the Popover API for anchored nonmodal overlays. Prefer labeled radio/checkbox state with `:checked`, `:has()`, `:target`, and `:focus-within`; use CSS counters for static progress. Every interaction has keyboard-visible focus and meaningful labels. Avoid scripted UI state when a native primitive or pre-rendered Python output suffices.

Inline SVG generated by Python uses `role="img"`, `<title>`, `<desc>`, `aria-labelledby`, and a nearby caption; IDs are unique. Reuse repeated symbols with `<symbol>/<use>` where this improves maintainability. Keep each diagram beside its legend and source. A screenshot of the actual rendered SVG is required before visual acceptance.

Print rules live in `@layer print`; expand `<details>` and other answer bodies, preserve source labels/equations, hide controls, avoid clipping and split-critical figures, and use ink-safe contrast. Keep a deliberate `[hidden]` exclusion if needed. Inspect the generated PDF; source inspection is not print acceptance.

The hide list is scoped to controls that *cannot* work without a script. A native control that works without scripting must never be added to it: F07's checkboxes and date field stay visible on paper because the printed page is the component's whole purpose, and the print layer draws their boxes explicitly (`appearance: none` plus a token border) so the tick and the date line exist as ink.

## RESPONSIVE-ACCESSIBILITY

| Area | Invariant |
|---|---|
| Prose | 60–75ch, target `62ch`; at most four sentences per block. |
| Layout | CSS Grid, `subgrid` and `@container` where they solve intrinsic alignment/reflow; fluid values use `clamp()`. Provide fallback behavior. |
| Contrast | WCAG 2.2 AA: at least 4.5:1 normal text, 3:1 large text and UI. Check all supported theme and print token pairs. |
| Focus | Every action keyboard operable; visible `:focus-visible`; no information conveyed by color alone. |
| Motion | `prefers-reduced-motion: reduce` disables nonessential motion. No decorative animation or scroll-jacking. |
| Inline styling | Zero style attributes; no raw hex outside primitive token tier. |
| Anti-slop | No decorative gradients, glow, glass, grain, shadows, hairlines, dashed callouts, uniform card grids that fragment prose, structural emoji, hero banners, drop caps, medallions, coordinate labels, or raster photos added for a lint score. Use at most three semantic highlight colors. |

Static CSS or a passing lint is not visual/accessibility acceptance. Use the current workspace `VISUAL_VERIFICATION.md` tool/engine order and inspect captured pixels. At this audit, runtime contrast/keyboard/screen-reader/print behavior was not retested.

