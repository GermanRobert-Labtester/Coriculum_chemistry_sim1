# Python, TypeScript and JavaScript Audit Contract

Parent Contract: `../../AGENTS.md`  
Extends: AGENTS.md §§4, 10, 12  
Last updated: 2026-11-07 · Static audit `[INSPECTED]`; one JavaScript budget check `[TESTED]`.

## FOUR-LANGUAGE-STACK

| Tier | Language | Responsibility | Enforcement |
|---|---|---|---|
| 1 | Semantic HTML + modern CSS | Primary structure, presentation, native interaction; target at least 95% of UI/visual behavior. | Native `<details name>`, `<dialog>`, popover; CSS state and layout. Zero inline style/event handlers. |
| 2 | Python 3 | Offline extraction, precomputation, generation and verification. | Deterministic CLI, offline; errors exit nonzero and identify file/selector/line. Production writes restricted to `build/` and canonical generated master. |
| 3 | TypeScript | Residual client logic that HTML/CSS and Python cannot perform. | `strict: true`, zero `any`, explicit DOM null checks, no runtime library. Compile and minify locally. |
| 4 | Raw JavaScript | Compiled TypeScript micro-runtime only; never primary architecture. | Every top-level function registered; script total capped by all three limits; no DOM templates or external loads. |

The final HTML works from `file://`, is self-contained, and makes no network requests. Python/build dependencies are not shipped as runtime dependencies. New features must exhaust HTML/CSS → Python before proposing TypeScript/JavaScript.

## JS-SUPPRESSION

Executable inline JavaScript must remain at or below 4,096 UTF-8 bytes, 100 newline-separated lines, and 2% of total master bytes; the smallest cap binds. JSON data scripts are not executable but must be Python-generated, registered, have a static fallback, and be reported. No `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `createElement` templating, data-array-to-HTML hydration, JS-driven accordions/tabs/modals/tooltips, `requestAnimationFrame` eye candy, scroll-jacking, external library, or network API. Core reading, navigation and every Tier 1 answer work with JS off.

## JS-WHITELIST

`build/js_registry.json` is the machine copy. Current verification on 2026-11-07: `python3 build/check_js_budget.py` **PASS**, shipped 2,203 B / 48 lines / 3 registered top-level functions; 0.258% of the 853,072 B master; no banned API. Historical root-AGENTS measurement 3,713 B / 75 lines / 6 functions is stale. Raw HTMLParser measured 2,205 B because it includes wrapper whitespace; the checker’s normalized shipped-script measure is authoritative.

| Function | Per-function cap | Why no HTML/CSS or Python substitute | JS-off degradation |
|---|---:|---|---|
| `persistMarks` | 700 B / 19 lines | Browser `localStorage` persistence of user marks/checklists. | Native radio/checkbox state works for visit; static score text remains. |
| `calcConc` | 1,200 B / 19 lines | Arbitrary user-entered numerical `w ↔ c` conversion with density and molar mass. | Static formula/example remains; calculator is hidden. |
| `printChapter` | 200 B / 6 lines | Browser print dialog activation. | Whole document remains printable; button hidden. |

Nested helpers are included in their owning registered function budget; only top-level functions require rows. Reserve is not permission to spend: add an explicit row, rationale, fallback, checker update and changelog before any expansion. Runtime behavior was not exercised in this audit.

## PYTHON-CLI

| CLI / module | Contract |
|---|---|
| `build/build_master.py` | Sole writer of the canonical master; deterministic from local sources; never hand-edit generated HTML. Do not invoke under a documentation-only lock. F07: it also owns the `REVIEW_DAYS` schedule literal and the `review_sequence()` renderer behind `{{REVIEW_SEQUENCE}}`; the literal is plain data so a read-only checker can parse it without importing the module. |
| `build/ledger.py`, `terms.py`, `figures.py`, `glossary.py`, `quiz.py`, `definitions.py`, `components.py`, `prereq.py`, `reaction_practice.py`, `typography.py`, `tools.py` | Python source extraction, correction pairs, terms, figures, static components, navigation and text. Make output deterministic; keep sources/locators. `reaction_practice.py` (F03) holds the 8 vetted conservation records and renders the two practice sections; its `validate()` asserts conservation and distractor semantics, and `build_master.py` refuses to build on a fault. |
| `build/check_js_budget.py` | Read-only master/source/registry audit. Default checks shipped bytes/lines/percent, registered top-level functions and ceilings, banned APIs, JSON blocks. `--self-test` is separately a fixture test. |
| `build/check_balance.py` | Read-only. Besides the E01–E61 reconciliation and the taught-equation scan, it re-derives conservation for the F03 practice records (8 answers + ionic lines + distractor semantics) and keeps the rule that a balanced equation with a phase/gas/heat/concentration mark is still not a verified reaction. `build/check_numbers.py` additionally renders the practice HTML and holds its computed `.num` span (the item-7 EMF) to the sigfig discipline. |
| `build/check_js_off.py`, `check_layers.py`, `check_html.py`, `check_contrast.py`, `check_numbers.py`, `check_terms.py`, `check_claims.py`, `check_claim_crush.py`, `check_links.py`, `check_network.py`, `check_size.py`, `check_scrubber.py`, `check_pillars.py`, `check_balance.py`, `check_wiring.py` | Read-only checks when invoked directly; inspect each command before use. All fail nonzero with actionable diagnostics. Do not assume the umbrella runner is read-only. F04: `check_links.py` and `check_wiring.py` also call `ledger.validate_mistake_route(html)`, which requires all 33 M-ids to resolve both ways (route card `#mr-MNN` → inline card `#mNN` → back-link); `terms.py` exempts the `#mistake-route` span because it names wrong forms to correct them, as `.mist` blocks do. F07: `check_links.py` also runs `audit_review_sequence(html, ids, days)` — it reads the `REVIEW_DAYS` literal out of `build_master.py` with `ast.literal_eval` (never by importing the builder, which writes the master at import time) and fails when the emitted `#review-sequence` disagrees with it: day count and numbering, one labelled fieldset per day, three labelled checkboxes each pointing at its chapter and named worked example, three resolving retrieval links, bidirectional `id`/`label[for]` pairing, and no `data-persist` hook anywhere in the component. `--self-test` fixtures (via `_review_selfcheck()`) cover one well-formed day plus five single-rule breakages. |
| `build/check_wiring.py`, `build/wiring.py`, `build/tests/` | Read-only control-contract gate. `wiring.py` is the registry of every interactive family (selectors, cardinality, trigger→handler→state→persistence→view, default/reset/failure/JS-off) and `build/WIRING.md` is generated from it — a stale document fails the gate. `check_wiring.py --runtime` runs `build/tests/run_wiring.mjs` against a JSON DOM exported from the *built* master (`dom_fixture.py`), so the suite cannot drift from the deliverable. F08: `tests/dom.mjs` learned `:has()` compound matching and exclusive radio groups (a radio group that does not clear its siblings makes every `:checked`-scoped CSS contract untraceable); the suite gained 11 occlusion-station cases (32 total) that read selectors *and* declarations out of the shipped stylesheet and evaluate them against the shipped markup; `check_dynamic()` now implements the `occlusion_labels` contract the registry had declared but nothing consumed — the master's per-figure `.lbl` list must equal what `figures.py` generates, text for text. Mutation-verified: 14/14 scratch-master mutations caught. `--self-test` covers zero/multiple cardinality, a missing optional figure, undeclared storage keys, an unguarded storage access, a missing `noscript` block and a hand-edited figure label. |
| `build/gate.py`, `build/check.sh` | `[TESTED]` B04: strictly read-only aggregate runner. `check.sh` is 21 lines of pure `exec python3 build/gate.py "$@"` delegation, so the two entry points cannot diverge; `gate.py` never names `build_master` in code or in any string literal (AST-asserted by `tests/test_gate_runner.py`). Every subprocess runs with `PYTHONDONTWRITEBYTECODE=1`. A SHA-256 manifest of the whole production tree (`__pycache__` included) is taken before and after the run; any write fails the gate, and the passing proof is recorded as a `readonly-integrity` step in every report (schema 2.1.0, 26 steps: 25 checks + `readonly-integrity`). The only production-tree write is `build/check-report.json` itself, skipped by `--no-report`; all generated diagnostics go to `$CHEM1_SCRATCH`. B04 moved `check_definitions.py`'s `def_first_use.json` out of `build/` for this reason. `--check-stale` binds a saved report to `master.sha256` and labels partial coverage; `--require-full` refuses it. |
| Required future checks | Parser validity, unique IDs, fragment targets, skip target and `AGENTS.md ≤ 24,576 B`; `check_agents_size.py` was not found. Confirm whether existing `htmltree.py`/`check_html.py` already cover parser/IDs before adding a duplicate. |
| Proposed static search | Generate index/anchors in Python; no runtime HTML hydration. A dedicated `gen_search_index.py` is absent. |

Use stdlib where practical. `pdftotext -layout -f P -l P` is the page-scoped extractor the `claim-crush` step uses to verify course-text provenance (B05); extraction goes to a temp dir outside the tree, and `exit 3` means a required input was absent, which the gate records as UNVERIFIED rather than PASS or FAIL. No script accesses the network or writes outside permitted build outputs. Gate additions need positive, negative and boundary fixtures. Verification mode must prove it did not mutate production files; bind reports to master SHA-256.

## TYPESCRIPT-COMPILE

No `src/ts/*.ts`, `tsconfig.json`, or `pyproject.toml` was found in the scoped inventory. `tsc` is recorded unavailable on PATH in current AGENTS (not rechecked here). Before residual code is authorized, specify a local deterministic compiler command and version, strict configuration, explicit null checks, zero `any`, minification, source-to-inline mapping, and a no-network runtime check. Never use TypeScript to move precomputable or native UI state into the browser.

## MIGRATION-PLAYBOOK

| Runtime work | Preferred target |
|---|---|
| Disclosure, exclusive accordions, dialog, tooltip/popover | Native `<details name>`, `<dialog>`, Popover API; CSS focus/state. |
| Filters, masking, column choices, navigation/current section | Labeled inputs and `:checked`, `:has()`, `:target`; accessible static fallback. |
| Tables, figure paths, scrubber phases, quiz question/answer bodies, search data | Python-rendered HTML/SVG at build time; include full no-JS and print representation. |
| Repeated runtime `innerHTML`/element creation loops | Remove templating; render deterministic static markup in Python and leave a stable `<output>` target if a true calculator requires script. |
| Numeric user input or storage that cannot be precomputed | Strict TypeScript micro-runtime; registry rationale, exact byte/line ceiling, text-only output and explicit JS-off behavior. |

Historical T15 records establish prior migration work, not the current content/behavior status. The current checker passes its script budget. The user’s requested audit forbade modifying or rebuilding the HTML, Python, TypeScript, roadmap or sources.

## VERIFICATION-SUITE

Report each result at its evidence layer: `[TESTED]` command/measurement run; `[INSPECTED]` file or captured page read; `[INFERRED]` reasoned; `[UNVERIFIED]` unresolved. Static scans do not establish browser runtime, visual output, WCAG conformance, screen-reader behavior, print pagination or scientific truth. For every test name the exact master hash, command, exit/result, and whether the command writes. Saved JSON and historical reports remain historical unless hash-bound to the current output. Current user instructions forbid adding/running tests except the requested audit verification; only the read-only JS budget checker ran.

