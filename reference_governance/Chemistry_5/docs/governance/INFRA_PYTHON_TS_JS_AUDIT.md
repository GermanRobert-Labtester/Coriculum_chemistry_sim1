# Python, TypeScript and JavaScript Audit

> Parent Contract: `../../AGENTS.md`  
> Extends: AGENTS.md §4, §10, §12  
> Last updated: 2026-11-07 · Status: `[TESTED]` inventory and master counts; missing-tool specifications are `[TARGET]`.

## JavaScript forensic baseline

### [JS-AUDIT]

Canonical file: `Master_5_tema_kinetika_un_katalize.html`, 1,556,007 B. In the current read-only audit, executable content excludes two `application/json` data blocks:

| Metric | Current observation |
|---|---:|
| Executable script | 121,642 UTF-8 B; 2,263 lines; 7.817574% of master |
| Inline event attributes | 0 |
| `addEventListener` calls | 67 |
| Function declarations / rough function census | 125 in prior dedicated census; function shape dependent |
| `innerHTML` / `createElement` | 12 / 9 |
| `requestAnimationFrame` | 1 (`watchPlot` redraw support) |
| `outerHTML` / `document.write` / `Math.random` | 0 / 0 / 0 |
| Registered R1–R3 hooks | 0; existing runtime does not conform |

Remeasured script metrics match the stated 4,096 B / 100-line / 2% suppression rule, not the exact function-census method. Detailed migration targets are in `../governance/OPEN_ISSUES_LEDGER.md#iss-arch`.

### [JS-WHITELIST]

Only these optional hooks may ship, as compiled TypeScript emit; remove any hook that is unnecessary. Total ceiling is the smallest of 4,096 B, 100 formatted lines, and 2% of master bytes. Zero inline event attributes, DOM templating, `innerHTML`/`outerHTML`/`insertAdjacentHTML`/`document.write`, runtime `createElement` templates, JS UI state where native HTML/CSS works, animation loops/scroll-jacking, storage, network, randomness or external scripts.

| ID | Function | Maximum | Why runtime may be needed | JS-off behavior |
|---|---|---:|---|---|
| R1 | `printOpen` | 512 B / 14 lines | Compatibility only when the print engine cannot expand `details` content in CSS. | Print note “Atveriet sadaļas pirms drukas”; static print map. |
| R2 | `calc` | 3,072 B / 72 lines | Arbitrary real-valued Arrhenius two-point Eₐ, dose accumulation, or Michaelis–Menten input cannot be fully enumerated. | Python-precomputed tables/figures in `.fallback-details`. |
| R3 | `hashOpen` | 512 B / 14 lines | Keep only if a supported engine fails to auto-expand a fragment-targeted closed `details`. | Fragment target remains reachable; summary opens by keyboard. |

Runtime may set only `textContent`, `output.value`, `details.open`, or predeclared SVG attributes. `<noscript>` fallback per live instrument/hook. TypeScript emits unminified code for budget auditing; never hand-edit compiled JS.

## Python CLI

### [PYTHON-CLI]

Workspace has `tools/`, `verify/`, and `verify/run_all.py`; existing builders cover numbers, glossary/cards, self-check, figures, print map, fonts, MathML alt and instruments. Existing verifiers cover design, contrast/accessibility, tables, figures, numbers, provenance, text, terms, flashcards and other domain checks. There are six Node `.js/.mjs` checks, including `tools/test_halflife.js`, `tools/test_instruments.mjs`, `tools/check_a11y.mjs`, `tools/check_labels.mjs`, `tools/render_figure_shots.mjs`, and the audit tooling. No `ts/`, `tsconfig.json`, `pyproject.toml`, `verify/verify_architecture.py`, or `verify/verify_html.py` exists in current root inventory.

CLI contract for new/maintained Python tools: `python3 <script> [--check] <explicit paths>`; stdlib-first, UTF-8, deterministic sorted output, network off, exit 0 pass / 1 violation. `--check` must be strictly read-only; inspect each runner before invocation because `tools/build_numbers.py` has previously written under `--check`.

### [PY-ARCH-GATE]

`verify/verify_architecture.py` [TARGET] must gate executable JS bytes/lines/share, banned patterns, function registry, event attributes, inline styles, first `@layer` order, layer containment, important allowlist, noscript coverage and AGENTS byte ceiling (24,576 B). `verify/verify_html.py` [TARGET] covers IDs/anchors, heading order, landmarks, table captions/scopes and SVG names. Every gate needs a negative fixture under `verify/fixtures/` and a documented invocation.

### [PY-BUILD-CLI]

`tools/build_states.py` [TARGET] extracts governed presets and deterministically emits static SVG/HTML states, labels and `:checked` CSS. Python owns extraction, tables, precomputed plot geometry, generation, number/contrast checks, internal anchors and byte-budget checks. The final HTML has zero external runtime dependencies. Preserve source hashes/provenance and stable output ordering.

## TypeScript contract

### [TS-COMPILE]

Create `ts/runtime.ts` and `tsconfig.json` [TARGET]; `strict: true`, `noImplicitAny: true`, `noUncheckedIndexedAccess: true`, zero `any`, explicit DOM null checks. TS is the source for any residual client calculation; compile deterministically and inline the emit via a Python build step. Current workspace reports `tsc` absent as of the last environment inventory; recheck availability before planning the build.

Interfaces should use explicit input/output contracts, e.g. decimal-comma parser returns `number | null`; calculation functions return validated display values plus a status message; DOM bindings require non-null element narrowing before use. Never build HTML strings from data.

## Verification suite

### [VERIFICATION-SUITE]

| Gate | Evidence expected |
|---|---|
| Static architecture / HTML | Run architecture and conformance gates; capture exit status and measured values. Until implemented: `[NOT RUN]`. |
| Existing checks | `python3 verify/run_all.py` and its fixture suite, only after inspecting side effects; historical `CHECKS.md` is not fresh acceptance. |
| TypeScript | Strict compile; zero `any`; output and budget tied to source. |
| JS-off / keyboard | Reading, navigation, disclosures, static instrument fallbacks and print path remain usable; full keyboard path. |
| Accessibility | Contrast per theme, visible focus, reduced motion, forced colors; record assistive technology coverage. |
| Print | Engine, page count, disclosure expansion, clipping and stranded headings recorded. |
| Visual | Workspace protocol requires `lite-shot` with falkon then falkon and direct PNG inspection. Chrome/Chromium only if explicitly authorized in the current turn. |

This governance-only run did not execute the product test suite, browser, print renderer or visual capture.
