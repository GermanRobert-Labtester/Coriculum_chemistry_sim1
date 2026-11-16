# Python, TypeScript, and JavaScript Audit

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 10, 12  
Last updated: 2026-11-07  
Verification status: current file inventory and emitted-script static metrics `[TESTED]`; browser behavior and fresh build acceptance `[UNVERIFIED]`.

## Language ownership

| Tier | Language | Responsibility | Contract |
|---|---|---|---|
| 1 | Semantic HTML5 + CSS | Structure, styling, navigation, disclosures, dialogs/popovers, responsive and print state. | Target ≥95% of visual/interaction behavior; core reading/navigation work without JS. |
| 2 | Python 3 | Source extraction, calculations, static markup/SVG/index generation, lint/gates/reports. | Offline deterministic CLI; use `python3 -I` for untrusted input; nonzero on failure; no runtime dependency enters final HTML. |
| 3 | TypeScript | Residual browser behavior that cannot be expressed in HTML/CSS or precomputed in Python. | `strict: true`, no `any`, explicit null checks; compile/minify/strip to the single inline runtime. |
| 4 | Emitted JavaScript | Last-resort micro-runtime, only compiled TS output. | Total executable inline content ≤4,096 bytes, ≤100 lines, and ≤2% of HTML bytes; use the smallest ceiling. Zero inline event attributes, DOM templating, external libraries, and unregistered functions. |

<a id="js-audit-and-migration"></a>
## JavaScript audit and migration

### Current emitted script

`Master_3_tema_skidumi_un_koncentracijas.html`: 8,187 bytes, 196 lines, 0.7909% of the current 1,035,140-byte master; one inline script; zero inline event attributes. Thus the controlling limit is 4,096 bytes and 100 lines, and the master fails both. Static scan found zero `innerHTML`, `outerHTML`, `insertAdjacent*`, `document.write`, `createElement`, `requestAnimationFrame`, `IntersectionObserver`, `localStorage`, `fetch`, or `XMLHttpRequest` occurrences in the emitted script. The master fingerprint changed from the start snapshot during this audit; cause was not established.

| Script region/function | Current role | Current disposition |
|---|---|---|
| `openAll`, `restoreAll` | `beforeprint`/`afterprint` details state restoration; saves `open` state and `name` values. | Emitted print region is 692 B/10 lines, 242 B above its ≤450 B/12-line cap; keep only if a renderer test proves CSS print expansion insufficient, then reduce. |
| `update` and recall click handler | Per-visit known/unknown, filter, exam, reveal, count state; source `build/recall_mode.js` is 2,394 B/55 lines. | Emitted recall region is 2,481 B/59 lines, 81 B above its ≤2,400 B/60-line cap. Controls hidden in source HTML until enhancement; answers remain available in ordinary disclosure mode. |
| `norm`, `select`, `filter`, `jump`, `open`, `close` | Search normalization, query matching, result navigation, dialog/focus behavior. | Emitted search region is 5,014 B/127 lines and is not in the current whitelist; `[JS-BLOAT]` issue JS-002. Native dialog does not make its matching/keyboard logic native. |
| Anonymous callbacks | Recall click; search document click/keydown, input, list click, dialog close; print event callbacks named above. | Count and review with every emitted build; no unregistered event listener may remain. |

The emitted runtime contains no DOM-creation/injection calls, but size/line limits and search whitelisting still fail. `build/qa.js` is a separate development harness: 29,556 bytes / 702 lines, not embedded. Treat its migration independently from the production script.

### Permitted JS micro-runtime registry

| Entry | Exact budget | Why HTML/CSS + Python cannot do it | JS-off behavior |
|---|---|---|---|
| `recallMode()` | ≤2,400 B and ≤60 lines. | Per-visit learner marks, filtering and answer conceal/reveal depend on interaction state not known at build time. | Controls remain hidden; ordinary prompt/answer disclosures remain readable and printable. |
| `printExpand()` (`openAll`/`restoreAll`) | ≤450 B and ≤12 lines; delete if the CSS print test passes. | Browser-specific printing may not expose closed native details content. | Details remain natively collapsible; print CSS exposes content where supported. |

Unlisted functions are violations. Search, theme persistence, calculators, external libraries, network/storage, generated DOM, JS tabs/accordions/tooltips, scroll listeners, and animation loops remain forbidden unless a future governance change registers a specific residual task and budget.

### Migration order

1. Keep native chapter links and CSS `:target`/`:has()` current-section state; no scroll state script.
2. Keep native details/dialog controls; pre-render all stable controls and indexes in Python.
3. Remove or explicitly scope search; if retained, author residual matching/keyboard logic in TS, preserve native dialog and no-JS fallback, and fit it plus recall/print within the total budget.
4. Run print-state fixture against the actual permitted renderer before retaining `printExpand()`.
5. Compile one final inline runtime; produce byte/line/function inventory; scan banned APIs and inline handlers; verify no external requests.

## Python CLI

### Existing inspected tools

`tools/`: `check_contrast.py`, `check_print_state.py`, `check_qa_report.py`, `check_recall_mode.py`, `check_source_claims.py`, `check_t20.py`, and `language_lint.py`. Build modules live under `build/`, including `build/build.py`, `calc.py`, `equations.py`, `figures.py`, `terms.py`, `recall.py`, task data, routes, and content checks. No source extraction CLI or HTML/JS-budget/governance-size gate was found. Existing tools were inventoried; this pass did not execute them.

### Required CLI contracts

| CLI target | Inputs/outputs | Required checks |
|---|---|---|
| `tools/check_js_budget.py` | Master path; optional JSON report path. | Parse executable script blocks only; byte count UTF-8, logical lines, percent of HTML, registry membership, banned APIs, inline `on*=`; nonzero for any ceiling/allowlist failure. |
| `tools/check_html.py` | Master path; optional JSON report. | HTML parse; duplicate/broken IDs and fragments, one h1, semantic landmarks, `style=` attributes, noscript, required component contracts, SVG title/desc. |
| `tools/check_agents_md.py` | Root AGENTS path and shard root. | 24,576-byte hard maximum, 12 numbered sections, canonical shard existence, relative links and heading anchors. |
| `tools/extract_sources.py` | A–F manifest, destination under `build/scratch/` or explicit temp path. | Deterministic text extraction with source filename/page/question provenance; never overwrite source files; report unsupported/unreadable inputs precisely. |
| `tools/check_contrast.py` (exists) | QA report or explicit colors/contexts. | Verify light/dark/print resolved backgrounds and WCAG ratios; distinguish fixture validation from live-master measurements. |

All new CLIs should use stdlib where practical, explicit paths rather than hidden defaults for writes, stable machine-readable reports, clear stdout summaries, and nonzero exit on failed checks. Never make a verification command silently rebuild the canonical master.

## TypeScript contract

Required future files: `tsconfig.json`, `src/ts/*.ts`, and `tools/ts_build.py`. Set `strict: true`, target browser APIs explicitly, use no `any`, narrow every queried DOM node, and avoid unsafe casts. TS source is authoritative for residual logic; generated/minified code is disposable build output and must be inserted by the established builder, never hand-edited in the generated HTML. Keep package/build dependencies development-only; the final HTML stays self-contained.

Suggested interfaces:

```ts
type RecallMark = 'known' | 'unknown';
interface RecallItem extends HTMLDetailsElement {
  id: string;
  querySelector(selectors: '.recall-answer'): HTMLElement | null;
}
interface RuntimeBudget { bytes: number; lines: number; percent: number; allowedFunctions: string[]; }
```

Do not use these illustrative interfaces in production without refining them to actual DOM structure and compiler checks.

## Verification suite

### Documentation-only pass

1. Fingerprint the protected HTML before edits: path, bytes, UTC/local mtime as reported, SHA-256.
2. Read-only static audit; do not run `build/build.py` or a tool that overwrites `build/qa/`.
3. Create/update only the authorized governance Markdown files.
4. Re-read all shards and root contract; resolve every `docs/governance/*.md#anchor` link.
5. Measure `wc -c < AGENTS.md` ≤24,576 and inventory shard bytes/lines.
6. Re-fingerprint the master and confirm all three values match exactly.

### Authorized implementation pass

Before building, inspect builder and gate side effects; back up or hash the master; redirect QA outputs where possible. Run calculation/equation, terminology, unit, role, coverage, JS budget, HTML, contrast, source, recall, print, offline, keyboard, visual, and PDF gates appropriate to changed files. Label actual execution `[TESTED]`, source reading `[INSPECTED]`, inference `[INFERRED]`; old reports are historical.

Visual work: `lite-shot -e falkon` first, then falkon, and directly inspect PNG. Chrome/Chromium is forbidden without explicit user allowance. If capture is blocked or blank, keep visual status `[UNVERIFIED]`.

### Current verification commands (read-only unless stated)

```sh
wc -c < AGENTS.md
wc -c docs/governance/*.md
sha256sum Master_3_tema_skidumi_un_koncentracijas.html
stat -c '%n | %s bytes | %y' Master_3_tema_skidumi_un_koncentracijas.html
rg --files -g '*.ts' -g 'tsconfig.json' -g 'pyproject.toml' -g 'tools/*.py'
```

Do not run a builder for this governance-only objective.
