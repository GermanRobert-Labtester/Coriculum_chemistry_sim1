# Architecture, CSS and DOM Contracts

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 5, 7, 8  
Last updated: 2026-11-07  
Verification: `[INSPECTED]` contract consolidated from current AGENTS and `tools/tokens.json`; product implementation has static gaps listed in `OPEN_ISSUES_LEDGER.md`.

## CSS tokens and layers

### Layer order

The first CSS statement is exactly:

```css
@layer reset, tokens, base, layout, components, utilities, print;
```

Place reset, generated token declarations, typography/base, page structure, component styles, small utilities, then print rules in the named layers. `!important` is prohibited except an explicitly justified print rule; the standing target is zero. No inline `style` attributes.

### Three-tier token schema

Use `tools/tokens.json` as the only value source. Preserve existing semantic names. Extend as:

| Tier | Pattern | Role | Example form |
|---|---|---|---|
| 1 primitive | `--p-<hue>-<step>` | Palette values, including light/dark values where adopted | `--p-slate-900` |
| 2 semantic | `--<existing-semantic-name>` | Roles for ink, surface, line, type, measure, spacing, radius and motion | `--ink`, `--surface`, `--space-1` |
| 3 component | `--<component>-<property>` | Local mapping to semantic tokens | `--button-border` |

**Existing semantic payload from `tools/tokens.json` (inspected 2026-11-07):** colors `ground #f4f6f3`, `surface #e8ede9`, `ink #161c18`, `ink-soft #3f4943`, `muted #59635d`, `line #75827a`, `give #185a78`, `give-tint #e2eef3`, `take #0b6456`, `take-tint #e0efe9`, `error #a02c2c`, `perm #72306c`, `mn-green #2e6b3a`, `mn-brown #6f4b2d`; type display/h2/h3/body/small/mark = 2.75/1.875/1.375/1.125/0.875/0.75 rem, mobile 2.375/1.75/1.375/1.0625/0.875/0.75 rem, print 24/16/12/10/8/7 pt; line-height 1.62; measure 68ch; rail 220px; radius 0; space 1–6 = 0.35/0.7/1.1/1.75/2.75/4.25 rem; ease `cubic-bezier(0.22, 1, 0.36, 1)`; fonts use embedded Ledger/Noto/Liberation fallbacks. These are existing token values, not a validated contrast palette.

No unverified dark palette or WCAG ratio may be invented. Calculate normal text ≥4.5:1, large text/UI ≥3:1 for every actual theme/state, and use words/shape as well as color. Semantic give/take/error colors and Mn species colors represent data; preserve that distinction.

### Layout and motion

Prose measure 60–75ch (current token 68ch); use responsive Grid/Flexbox, `clamp()`, `@container`, `subgrid` where supported, and measured breakpoints. Support 390/768/1440px with no page overflow; wide tables scroll inside a named, keyboard-focusable region. Use `:focus-visible`; no keyboard traps; `prefers-reduced-motion` must remove nonessential movement. Motion communicates state only.

## DOM class registry

| Purpose | Canonical classes / semantics |
|---|---|
| Structure and explanation | `.chapter .chapter-head .prose .lead`; headings follow ordered `h1`–`h6` hierarchy |
| Equations and state | `.eq .sp .op .arrow .what-changed`; actual `<sub>/<sup>` or MathML; accessible label is speakable Latvian |
| Worked example | `.worked .ledger-rows .lrow .lab-template .tool-purpose` |
| Mistake and term | `.mistake` with `.wrong-line`/`.right-line` and stable `SOURCE_AUDIT.md` ID; `.term-card` |
| Retrieval | `.recall-row .recall-item` using `<details>`; `.your-turn .ladder-answer .rekins` |
| Provenance | `.side .kind` with source/correction/supplement status and stable claim reference; F03 value evidence: `.value-ref` anchor on every registered value span → one static `<details class="value-evidence" id="ev-<id>">` per NUMBERS/COUPLES id in 13.F.3 (status vocabulary in `master_data.EV_STATUS_LV`) |
| Tables and figures | `.table-wrap .scroll` with named region and table caption/name; SVG `role="img"`, `<title>`, `<desc>`, `aria-labelledby`; token colors |
| Print/state | `.print-only .audit-banner .transcript-static`; print reveals all answers/details once and leaves writable templates blank |

## Five pillars markup

Each teachable concept maps to a stable concept/source ID and includes all applicable pillars:

1. **Definition:** one clear claim and canonical term.
2. **Mechanism/why:** causal account and stated conditions.
3. **Worked example:** steps, units, check, unrounded intermediates, one final rounding.
4. **Common mistake:** labeled wrong form → why tempting → catching check → correct form.
5. **Canonical term:** one spelling, source state, and relationship to confusable terms.

Sentence-first, one idea per sentence, paragraph ≤5 sentences. Every claim maps to `qa/trace.md` or is explicitly `Papildinājums` with a source. A passing balance checker does not prove species plausibility.

Generator notation forms include `[[Fe^3+]]`, `os(...)`, `[[w:S^4+]]`/`wrong_form(...)`, and `->`; these are renderer inputs only. No marker or raw ASCII arrow leaks into student output except explicitly labeled wrong forms/quotes.

Chemistry typography: charge magnitude before sign (Fe³⁺); oxidation state sign before magnitude (`S(+4)`); e⁻; U+2212; `⇌ → ↓ ↑`; states `(aq) (s) (l) (g)`; decimal comma; thin no-break space before units. Keep `E`, `E°`, `E°′`, `ΔE`, `c(X)`, `n(X)`, `V(X)`, `M(X)`, `z` distinct. `0.0592 V` (Latvian display `0,0592 V`) is fixed at 298 K. Numbers and potentials live once in `master_data.py`.

## Native interaction patterns

| Need | Preferred native pattern | Required fallback |
|---|---|---|
| Reveal answer / explanation | `<details><summary>` | Content remains in HTML; print expands all |
| Mutually exclusive disclosure | `<details name="stable-group">` only when exclusive | Independent details otherwise |
| Filters, notation lens, lab mode | `<input type="checkbox/radio">` + `:checked`/`:has()` | All content remains readable; static selection stated |
| Bounded walkthrough steps | `:target` anchor states | Ordered transcript in HTML and print |
| Modal task | `<dialog>` | Direct content/anchor fallback |
| Preview/tooltip-like content | Popover API (`popover`, `popovertarget`, `popovertargetaction`) | Ordinary linked content; never hover-only |
| Arbitrary numeric titration entry | Minimal registered TS runtime | `<noscript>` note, static L25 worked example and blank template |
| Recall-state persistence | Minimal registered TS `localStorage` hook | `<noscript>` note; current-session/native checked state; prompts stay readable |

Do not use JS for accordions/tabs/modals/tooltips, static lists, table hydration, precomputable tables, or CSS state. Core reading/navigation must work with scripts disabled and under `file://`.

## Section ID taxonomy

Required top-level IDs: `#sakums`, `#ch1`…`#ch13`, `#print-answers`. Headings use `#h-<section>`; descriptive anchors include `#l25-worked`, `#recall-bank`, `#potentials`, `#avoti`, `#templates`; provenance uses unique DOM IDs `#prov-<claim>-<occurrence>` while claim IDs remain stable. Every local `href` and ARIA ID reference resolves. `#audit` is allowed as a mode hash only when explicitly registered; it is not an element anchor.

## Print accessibility

At 390/768/1440px verify reflow, focus, controls, state and SVG readability. Targets ≥24×24 CSS px or a documented WCAG 2.2 exception. Print: expand `<details>`, show answers exactly once, hide controls/banner, retain provenance, avoid splitting formula/table/SVG groups, and leave writable templates blank. No-JS, keyboard, `file://`, reduced-motion, contrast, and all-page PDF checks require direct current-build evidence. Source/CSS/DOM counts are not visual acceptance.
