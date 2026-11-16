# Architecture, CSS and DOM Contracts

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 5, 7, 8  
Last updated: 2026-11-07  
Evidence status: contract `[INSPECTED]`; current stylesheet structure `[TESTED]`; contrast and rendered acceptance `[UNVERIFIED]`.

## [CSS-TOKENS-AND-LAYERS]

CSS layers, tokens and responsive rules.

The fixed cascade order is `@layer reset, tokens, base, layout, components, utilities, print;`. Place every authored rule in one layer; limit `!important` to explicitly justified print flattening only. Raw hex values belong only in `tokens`; avoid gradients, shadows, glow/glass, decorative animation, unexplained magic numbers, duplicate palettes and inline `style=`. Default reading measure is 60–75ch; current primitive is 68ch. Use `clamp()` for type/spacing, `@container` for component reflow, grid/subgrid where its support and fallback are appropriate, and `prefers-reduced-motion: reduce` for any meaningful motion.

Current responsive topology in `build/style.css`: `.notation-sheet` is the only inline-size container; its unnamed `@container (max-width:560px)` reflows the notation table into labelled stacked rows (L5001–5035). Viewport media queries use max-width 360, 380, 420, 480, 640, 680, 900, 1199, 1239px and min-width 601, 640, 820, 1200, 1240px, including screen-scoped variants. This is an inventory, not a harmonized scale; consolidate overlapping breakpoints by owner only after component-level review. Current selectors have no `:has()`, `:checked`, `subgrid`, `@starting-style`, or CSS counter declarations. Add these only when they replace runtime state or support an actual component.

Three tiers: palette/type/geometry `--p-*` → semantic role `--t-*` → component role `--c-<component>-*`. Dark mode must override semantic mappings; components consume semantic/component tokens only. Do not introduce another `--bg*` palette. Current source declares 69 primitive, 53 scoped semantic, and 40 component-token declarations. CSS source line references are current for `build/style.css` (2026-11-07): primitive declarations start L15; semantic light mappings L108–164; component mappings L188–246; dark mappings L254–301; system dark mappings L314–361. Values below reproduce the current owner source; component values alias the semantic roles shown here.

### [CSS-PRIMITIVES] Exact current primitive palette and geometry

| Family | Token values |
|---|---|
| neutrals | `--p-white #ffffff`, `--p-black #000000`, `--p-gray-900 #111111`, `--p-gray-800 #1f2937`, `--p-gray-700 #374151`, `--p-gray-600 #4b5563`, `--p-gray-500 #6b7280`, `--p-gray-400 #9ca3af`, `--p-gray-300 #d1d5db`, `--p-gray-100 #f3f4f6`, `--p-gray-50 #f8fafc` |
| slate | `--p-slate-50 #f2f6f7`, `--p-slate-100 #edf2f4`, `--p-slate-150 #e8eef0`, `--p-slate-300 #c7d2d7`, `--p-slate-500 #758992`, `--p-slate-600 #465761`, `--p-slate-900 #12232e` |
| crimson / coral | `--p-crimson-800 #851e19`, `--p-crimson-700 #a52d27`, `--p-crimson-100 #f2e4e2`, `--p-crimson-50 #f0d3cf`; `--p-coral-400 #ff7a6e`, `--p-coral-900 #382322`, `--p-coral-950 #4c2d2a` |
| dark slate | `--p-dark-950 #0f1c24`, `--p-dark-900 #172831`, `--p-dark-850 #1d303a`, `--p-dark-700 #344a55`, `--p-dark-400 #8ba1ab`, `--p-dark-300 #a9b9c1`, `--p-dark-50 #e7eef1` |
| green | `--p-green-950 #132e1d`, `--p-green-800 #1b5e20`, `--p-green-700 #1b7340`, `--p-green-600 #15803d`, `--p-green-400 #4ade80`, `--p-green-300 #81c784`, `--p-green-200 #a5d6a7`, `--p-green-100 #e8f5e9` |
| amber | `--p-amber-950 #451a03`, `--p-amber-800 #875000`, `--p-amber-700 #b45309`, `--p-amber-600 #d97706`, `--p-amber-500 #f5a623`, `--p-amber-100 #fef3c7` |
| red | `--p-red-950 #381a1a`, `--p-red-900 #b71c1c`, `--p-red-700 #c62828`, `--p-red-400 #e57373`, `--p-red-300 #ef9a9a`, `--p-red-100 #ffebee` |
| blue / teal | `--p-blue-900 #1e3a5f`, `--p-blue-700 #235d88`, `--p-blue-400 #5ea4d4`; `--p-teal-700 #1f7a5c`, `--p-teal-400 #4ec291` |
| type / geometry | `--p-font-serif: "Source Serif 4", "Noto Sans Math", "Noto Serif", Georgia, serif`; `--p-font-math: "Noto Sans Math", "Source Serif 4", serif`; `--p-font-mono: ui-monospace, "Liberation Mono", Menlo, monospace`; `--p-max-read:68ch`; radii 3px/2px/4px; small `clamp(.78rem,.74rem+.2vw,.85rem)`, body 18px, h3 `clamp(1.12rem,1.05rem+.35vw,1.28rem)`, h2 `clamp(1.35rem,1.2rem+.75vw,1.68rem)`, display `clamp(1.75rem,1.45rem+1.5vw,2.35rem)` |

### [CSS-SEMANTIC-MAP] Current light/dark semantic colors and OKLCH metadata

| Semantic role | Light HEX | Light OKLCH (where defined) | Dark HEX |
|---|---|---|---|
| ground | `#f2f6f7` | `oklch(.968 .006 210)` | `#0f1c24` |
| surface | `#e8eef0` | `oklch(.938 .009 215)` | `#172831` |
| surface-2 | `#edf2f4` | `oklch(.952 .007 215)` | `#1d303a` |
| ink | `#12232e` | `oklch(.22 .025 240)` | `#e7eef1` |
| muted | `#465761` | `oklch(.44 .02 230)` | `#a9b9c1` |
| faint | `#758992` | `oklch(.62 .02 225)` | `#8ba1ab` |
| line | `#c7d2d7` | `oklch(.84 .015 220)` | `#344a55` |
| accent | `#a52d27` | `oklch(.50 .19 27)` | `#ff7a6e` |
| accent-soft | `#f2e4e2` | `oklch(.938 .02 27)` | `#382322` |
| selection | `#f0d3cf` | not defined | `#4c2d2a` |

Status roles: light success `#1b7340 / #e8f5e9 / #81c784 / #1b5e20`; warning `#b45309 / #fef3c7 / #d97706 / #875000`; error `#c62828 / #ffebee / #e57373 / #b71c1c`; info `#235d88 / #edf2f4 / #5ea4d4 / #1e3a5f` (foreground/background/border/text). Dark success `#4ade80 / #132e1d / #1b7340 / #a5d6a7`; warning `#f5a623 / #451a03 / #b45309 / #f5a623`; error `#e57373 / #381a1a / #c62828 / #ef9a9a`; info `#5ea4d4 / #1d303a / #5ea4d4 / #5ea4d4`. Explicit dark and system-dark mappings are equivalent. Legacy `--bg`, `--bg-surface`, `--bg-alt` aliases map to ground/surface/surface-2 and must not become a second palette.

Component dictionary (`:root`, L188–246): infocard background/border/hover-border; formula background/border/text/muted; note background/border/rule-border/mistake-border; recall background/border/known-border; legacy `--c-leitner-known` and `--c-leitner-progress` (flag for removal with OI-07); dialog background/border/text; table header/border/text; provenance background/border/text; instrument background/border/lead; button background/border/text/active background/active border/active text; positive/negative feedback background/border/text. All reference semantic tokens, except active button uses `--p-green-700` and white.

Saved `build/qa/contrast_report.json` contains 14 checks per theme and `overall_status: PASSED`; it was modified after the current master and contains no matching master hash, so values below are `[INSPECTED: saved report]`, not current-hash acceptance. Light ratios: ink 14.78/13.73/14.25; muted 6.90/6.41/6.65; accent 6.42 ground, 5.96 surface; success text 7.00; error text 5.75; active button 5.88; dialog 14.78. Dark: ink 14.77/12.93/11.65; muted 8.58/7.51/6.77; accent 6.82 ground, 5.97 surface; success text 8.90; error text 7.33; active button 5.88; dialog 14.77. All saved checks exceed their listed thresholds; current hash, all component states, and target/focus geometry remain unverified.

| Semantic role | Required usage / contrast pairs |
|---|---|
| `--t-ground`, `--t-surface`, `--t-surface-2` | page and reading surfaces; text contrast checked against all three |
| `--t-ink` | primary text; ≥4.5:1 normal, ≥3:1 large |
| `--t-muted` | secondary text; retain ≥4.5:1 while it conveys information |
| `--t-faint` | nonessential decoration only; never encode required content solely with faint text |
| `--t-line` | separators; controls/focus additionally need ≥3:1 UI contrast |
| `--t-accent`, `--t-accent-soft`, `--t-selection` | links/state/focus; text links ≥4.5:1 and UI/focus ≥3:1 |
| `--t-{success,warning,error,info}-{text,bg,border}` | status uses text plus shape/label; text ≥4.5:1 |

Component roles are a constrained API: `.infocard`, `.formula`, `.note`, `.recall`, `.dialog`, `.table`, `.prov`, `.instrument`, `.btn`, `.feedback`. A component token must be used in a component rule or removed from source. Do not rely on color alone to distinguish scientific status.

## [FIVE-PILLARS-MARKUP]

Five independently useful content pillars.

Every taught concept gets all applicable rows. If one truly does not apply, record why in the content inventory. Keep mechanism and example next to the definition to avoid split attention.

| Pillar | Contract | Canonical class / markup |
|---|---|---|
| Definition | canonical Latvian term, scope and conditions | `.infocard` or concise opening definition |
| Mechanism | causal steps, equation-linked symbols, assumptions and limits | `.formula` plus explanatory prose; never equation alone |
| Worked example | source-traceable or explicitly illustrative; equation, substitution, conversion, units, result and plausibility | `.exercise` |
| Common mistake | symptom → reason → repair, adjacent to relevant concept | `.note--mistake` |
| Canonical term | Latvian spelling and controlled English equivalent only in glossary | glossary entry / canonical-term link |

## [PEDAGOGICAL-PATTERNS]

Native HTML interaction blueprints.

Prefer semantic HTML state over script. Do not force a UI pattern if native semantics cannot preserve its keyboard/screen-reader behavior.

```html
<details name="recall-set">
  <summary>Atbildi pats pirms risinājuma atvēršanas</summary>
  <p>Atbilde un pamatojums.</p>
</details>
<button type="button" popovertarget="notation-help">Apzīmējums</button>
<aside id="notation-help" popover>Lokāls skaidrojums ar parastu aizvēršanas ceļu.</aside>
<dialog aria-labelledby="dialog-title">
  <h2 id="dialog-title">Avota piezīme</h2>
  <p>Avota loma un konkrētais pamatojums.</p>
</dialog>
```

Use shared `details[name]` only for mutually exclusive disclosures. Keep answers closed on screen; print must deliberately expand answer content once. CSS `:checked`, `:target`, `:has()`, `:focus-within`, native disclosure and popover states should cover toggles, tabs, filters, cues, and previews. Core reading/navigation must work with JS disabled. Do not add a mastery score, Leitner box, streak, XP, or unconsented persistence.

## [DOM-AND-IDENTIFIER-CONTRACT]

IDs, classes, landmarks and SVG.

| Contract | Stable names |
|---|---|
| Chapters and sections | `#ch1`–`#ch16`; `#sec-chN-N` |
| App/appendix | `#app-*` |
| Instruments and map | `#instrument-a`–`#instrument-h`; `#concept-map` |
| Retrieval, figures, provenance | `#recall-item-N`; `#fig-*`; `#prov-N` |
| Core classes | `.chapter`, `.chapter-head`, `.infocard`, `.formula`, `.note--rule`, `.note--mistake`, `.note--source`, `.note--verified`, `.exercise`, `.chapter-check`, `.recall-item`, `.recall-details`, `.prov`, `.table-scroll`, `.fig`, `.fig-wb`, `.instrument`, `.prov-lens` |

Use one h1, ordered h2–h6 hierarchy, named `main`/`nav` and section landmarks, labels/captions/scopes, unique IDs and resolved internal anchors. Each SVG needs a title/description or equivalent accessible name and a nearby “what to notice” text. Reuse identical geometry with `<symbol>` + `<use>` where IDs and styling remain safe. Do not claim that parser counts alone validate semantics.

## [PRINT-AND-ACCESSIBILITY] Contrast, focus, motion and print

- WCAG 2.2 AA: normal text ≥4.5:1; large text and UI/focus ≥3:1 in every supported theme. Contrast tests are computed against actual token pairs and then checked in rendered UI.
- Visible `:focus-visible`; keyboard traversal, dialog focus/escape/return and horizontal table scroll tested separately.
- Instrument and primary controls target at least 44×44 CSS px; all controls remain usable at 320 px.
- Reduced motion honored. No looping decorative animation.
- Print: white page, dark ink; CSS in `@media print` exposes every `<details>`/collapsible disclosure (use `details::details-content` where supported and a compatible fallback); no `beforeprint` JS state mutation; answers appear once; sticky/fixed elements flattened; rows/captions kept; monochrome roles distinguishable. Verify real PDF pages and page map against current output hash.
- Visual pass needs PNG captures at 1440/768/390 light+dark, 320, keyboard state and representative real PDF pages, directly inspected. Follow workspace `VISUAL_VERIFICATION.md`; use `webshot -b falkon`/`falkon` first. No visual acceptance from CSS/DOM/source inspection.

## [ANTI-SLOP] Hard visual exclusions

Zero decorative gradients, glow, glassmorphism, box shadows, structural emoji, prose-fragmenting uniform card grids, hero banners, decorative animation, drop caps, badge clutter, or stock imagery. Favor readable prose, one accent, real data graphics, and a quiet reference layout. Any violation is a tracked issue; do not weaken the contract to match the master.
