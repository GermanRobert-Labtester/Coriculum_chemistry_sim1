# AGENTS.md — Chemistry_5: kinetics and catalysis

**Governance revision 2026-11-07 (R4).** This is the executive architecture contract and routing hub for the canonical offline Latvian RSU Medical Chemistry topic 5 study document. The active queue is `MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md` (present); the referenced `Master_Final_Perfected.md` and `HTML_MASTER_BUILD_PROMPT.md` are absent `[TESTED]`. Do not attribute claims to missing files. The five shards under `docs/governance/` carry details; they supplement, never weaken, this contract.

**Evidence tags:** `[TESTED]` run/count observed on the stated date · `[INSPECTED]` content read · `[INFERRED]` reasoned from evidence · `[UNVERIFIED]` not checked. **Source tags:** `[TEXT-VERIFIED]` cited passage opened · `[METADATA-VERIFIED / SCOPE-ALIGNED]` identity/scope checked, not claim proof · `[TARGET]` not yet implemented. Saved checks are historical until freshly rerun.

## 1. Goal & Architectural Philosophy

Continuously improve one canonical, self-contained, offline Latvian HTML study document for kinetics, catalysis and enzyme kinetics. Preserve course answer, source statement and correction as distinct evidence. Build and verify deterministically in Python; use HTML/CSS for content and interaction; reserve TypeScript for irreducible client logic. Never silently repair a source.  
**`[OFFLOAD-SHARD]`:** For implementation/review of document architecture and pedagogy, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup` in full before modifying workspace files.

## 2. Workspace, Offload Routing & Open Issues

**Canonical master:** `Master_5_tema_kinetika_un_katalize.html`; only live root master. `[TESTED 2026-11-07]` 1,556,007 B; 7,465 lines; mtime `2026-11-06T11:04:26.059696809+02:00`; SHA-256 `3528884dc2c1251c7c093024b5deac4f4d2eec106b524e50ee29c0c8c2629b14`. Root `.bak.html` files and `archive/` entries are historical snapshots, not sources. No usable Git repository; `git status` fails. Six course PDFs and existing tools/data/evidence files are inventoried in `STATE.md` and the roadmap.

| Canonical shard | Owns |
|---|---|
| [OPEN_ISSUES_LEDGER.md](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) | Compact issue forensics, exact known locations/counts and migration targets for active issues. |
| [ARCH_CSS_DOM_CONTRACTS.md](docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers) | CSS token/layer, DOM, content, pedagogy, accessibility and print contracts. |
| [INFRA_PYTHON_TS_JS_AUDIT.md](docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli) | Runtime audit/whitelist, Python CLI, TS compile and verification suite. |
| [TERMINOLOGY_AND_SOURCES.md](docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry) | Source hierarchy/conflicts, terminology and claim provenance. |
| [CHANGELOG_ARCHIVE.md](docs/governance/CHANGELOG_ARCHIVE.md#changelog-archive) | Older governance history and closed-issue audit trail. |

**Open Issues** — details and fix blueprints are in `OPEN_ISSUES_LEDGER.md#iss-arch`; close only on fresh evidence.

| ID | Category | Location | Rule violated / gap | Target | Tag | Detail |
|---|---|---|---|---|---|---|
| A01 | JS-Bloat | master script | 121,642 B / 2,263 lines / 7.818%; exceeds all JS ceilings | HTML/CSS/Python/TS | `[TESTED]` | [A01](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A02 | JS-Bloat | disclosure/mode/stepper hooks | Reimplements native HTML/CSS state | HTML/CSS | `[TESTED]` | [A02](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A03–A04 | JS-Bloat | `innerHTML` ×12; `createElement` ×9 | Runtime markup/control generation banned | Python/HTML | `[TESTED]` | [A03](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A05–A07 | JS-Bloat / HTML | drill, calculators, print state | Runtime shuffle, precomputable plots, JS-dependent print | Python/CSS/TS | `[TESTED]` / `[UNVERIFIED]` | [A05–A07](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A09–A10 | CSS-Arch | stylesheet / 77 inline styles | No layers; 60 important; zero inline styles required | CSS/Python | `[TESTED]` | [A09–A10](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A11–A12 | Infra-Gap | `tools/`, `verify/`, root | Architecture/HTML gates and strict TS setup absent | Python/TS | `[TESTED]` | [A11–A12](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A14 | Unverified | inline SVG | 82 SVG, 0 symbol/use; per-figure semantic/render audit open | HTML/Python | `[TESTED]` / `[UNVERIFIED]` | [A14](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A15–A16 | Source / Unverified | K10/K17/L1; QA evidence | Source intent open; saved PDF/browser/AT evidence is not fresh | HTML/Python | `[UNVERIFIED]` | [A15–A16](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A18–A19 | Source / HTML | clinical claims / termbase | Book passages unopened; several clinical terms ungoverned | HTML/Python | `[UNVERIFIED]` | [A18–A19](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |
| A20–A22 | Governance / Infra | root snapshots, legacy prompt | Missing spec/build prompt; no VCS; historical prompt conflicts with current contract | Governance/Python | `[TESTED]` / `[INSPECTED]` | [A20–A22](docs/governance/OPEN_ISSUES_LEDGER.md#issue-map) |

**`[OFFLOAD-SHARD]`:** When auditing architecture, open issues, workspace topology or the active roadmap, read `docs/governance/OPEN_ISSUES_LEDGER.md#issue-map` in full before modifying workspace files.

## 3. Source Authority & Conflict Resolution

Authority: (1) topic description defines scope; (2) lab sheets/key define task and expected course answer; (3) `Kinetika.pdf` primary theory, 2020 slides secondary except unique content; (4) MU sheet is questions, not key; (5) correct demonstrable errors with a named authority and source → correction → reason. Preserve literal source notation and uncertainty. Do not invent sources, quotes, pages, editions, ISBNs, DOIs or answers. K10, K17 and L1 remain open; see source shard.  
**`[OFFLOAD-SHARD]`:** For claims, terminology or source edits, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#conflict-log` in full before modifying workspace files.

## 4. Output Contract & Four-Language Architecture

| Tier | Owns | Hard rule |
|---|---|---|
| HTML5 + CSS | Content, navigation, interaction state, layout, print | Native elements and CSS state first. |
| Python 3 | Extraction, deterministic generation, precomputation, verification | Offline, repeatable CLI; final HTML has no external runtime dependency. |
| TypeScript | Irreducible residual client logic | `strict: true`, zero `any`, explicit DOM null checks; compiled, never hand-edited. |
| JavaScript | Compiled TS emit only | Suppressed micro-runtime, not primary architecture. |

**`[JS-SUPPRESSION]`** Executable inline JS ≤4,096 UTF-8 B, ≤100 formatted lines and ≤2% of master bytes (smallest ceiling governs); zero inline event handlers, DOM templating/injection, JS UI duplication, storage/network/randomness, animation loops, scroll-jacking or external scripts. Runtime may set only `textContent`, `output.value`, `details.open`, or predeclared SVG attributes.

| Hook | Budget | JS-off behavior |
|---|---:|---|
| R1 `printOpen` | 512 B / 14 lines | Print note and static print map. |
| R2 `calc` | 3,072 B / 72 lines | Python-precomputed tables/figures in `.fallback-details`. |
| R3 `hashOpen` | 512 B / 14 lines | Fragment target stays reachable; summary is keyboard-operable; remove hook if unnecessary. |

Only these hooks may ship; each needs a `<noscript>`/static fallback and justification. Current runtime conforms to none.  
**`[OFFLOAD-SHARD]`:** Before runtime, markup, style or interaction work, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#dom-components` and `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#js-whitelist` in full before modifying workspace files.

## 5. Content Standard (Five Pillars)

Teaching ch.1–12 includes: correct concepts and limits; source fidelity; equation/graph/physical meaning; worked example with assumptions/units and four-part error block; source questions with labelled model answers and tolerances. Supplemental topics remain marked as additions.  
**`[OFFLOAD-SHARD]`:** When changing chapter content or learning components, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#five-pillars-markup` in full before modifying workspace files.

## 6. Terminology & High-Priority Corrections

`termbase.json` governs terminology; glossary/cards are generated. Use Latvian, decimal comma in prose and point in data, NBSP before units, U+2212, real sub/superscripts or MathML, and no Cyrillic look-alikes. Keep `reakcijas pakāpe` distinct from `molekularitāte`; italic `k` distinct from equilibrium `K`; retain quoted source notation.  
**`[OFFLOAD-SHARD]`:** For terminology/data changes, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#terminology-dictionary` in full before modifying workspace files.

## 7. Design & CSS Engineering Standard

| Area | Contract |
|---|---|
| Cascade | First statement `@layer reset, tokens, base, layout, components, utilities, print;`; every rule layered; `!important` only in reset/utilities. |
| Tokens | Primitive `--p-*` → semantic → component; component tokens never reference primitives; one owner/value; no raw color literals outside tokens. |
| Layout/state | 60–75ch prose; intrinsic grid/flex; `clamp()`; `@container`/`subgrid`; `:has()`/`:checked`/`:target`/`:focus-within`; purposeful `@starting-style`; zero inline styles. |
| Access | WCAG 2.2 AA: text ≥4.5:1; large/UI/essential graphics ≥3:1 in each theme; visible focus, keyboard path, reduced motion and forced colors. |
| Print | CSS expands every disclosure without JS; answers marked; no clipping/stranded headings; grayscale legible. |
| Anti-slop | No decorative gradients/glow/glass/shadows, structural emoji, hero banners, prose-fragmenting card grids, stock images or decorative motion. |

**`[OFFLOAD-SHARD]`:** Before CSS, token, accessibility or print changes, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#css-tokens-and-layers` in full before modifying workspace files.

## 8. Pedagogy Standard (Native HTML)

| Need | Preferred primitive |
|---|---|
| Disclosure/answer | `<details>/<summary>`; shared `name` for exclusive groups. |
| Tabs/steppers/modes/filters/occlusion | Radio/checkbox + `:checked`/`:has()`; `:target` for deep links. |
| Term preview | Popover API. |
| True modal | `<dialog>`. |
| Numeric input | `<form>/<fieldset>/<output>` + R2 and precomputed fallback. |

Every interaction serves an outcome/error, supports keyboard, has static fallback and deterministic verification. Reading/navigation works with JS off.  
**`[OFFLOAD-SHARD]`:** Before interactive learning-component changes, read `docs/governance/ARCH_CSS_DOM_CONTRACTS.md#pedagogical-patterns` in full before modifying workspace files.

## 9. Sourcing & Provenance

Tags: `avots` = workspace file/page; `labojums` = issue ID + file/page; `papildinājums` = named authority + reason; `autora atbilde` = model answer without course key. Bibliographic metadata is not claim-level text verification. Six course PDFs are present; recorded page counts and source registry live in the source shard.  
**`[OFFLOAD-SHARD]`:** For provenance or literature changes, read `docs/governance/TERMINOLOGY_AND_SOURCES.md#verified-source-registry` in full before modifying workspace files.

## 10. Python/TS Infrastructure, Features & Literature

Existing Python builders/verifiers are in `tools/` and `verify/`; Node checks remain technical debt. Required targets: `verify/verify_architecture.py`, `verify/verify_html.py`, `tools/build_states.py`, `ts/runtime.ts`, `tsconfig.json`. CLI: `python3 <script> [--check] <explicit paths>`, UTF-8, stdlib-first, deterministic output, network off, exit 0/1; prove `--check` is read-only before use. Treat 2026 literature as unverified until primary metadata and relevant text are logged.  
**`[OFFLOAD-SHARD]`:** For tooling, runtime or verification work, read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#python-cli` and `#verification-suite`; for 2026 sources also read `docs/governance/TERMINOLOGY_AND_SOURCES.md#literature-2026` in full before modifying workspace files.

## 11. Editing, Non-Regression & Byte Budget

1. Governance-only pass: edit only `AGENTS.md` and the five canonical `docs/governance/*.md` shards; no product, source, generator or roadmap edits; no commits.
2. Production pass: never edit PDFs or `workspace_skills/`; fingerprint protected inputs before edits; never overwrite snapshots. Edit generated sources then regenerate; inspect commands first.
3. Do not weaken architecture, accessibility or provenance rules to match current defects. Close issues only on remeasured evidence.
4. `AGENTS.md` target 14,336–20,480 B; hard ceiling 24,576 B. Prefer compact tables and shard links; preserve detail in its assigned shard. Keep 10 recent compact rows here; archive older rows.
5. Visual evidence follows `VISUAL_VERIFICATION.md`: `lite-shot` with Falkon, inspect the PNG. Chrome/Chromium only when explicitly authorized by the user in the current turn. Report static, scientific, visual, accessibility and print evidence separately.

| Date | Sections/shards | Change | Evidence |
|---|---|---|---|
| 2026-11-07 | all; five shards | Created canonical offload vault; synchronized active roadmap status; compacted R4 executive contract; refreshed locked-master audit and issue index. | Master unchanged; runtime 121,642 B / 2,263 lines / 7.818%; AGENTS size/link gates measured after edit. `[TESTED]` |
| 2026-11-07 | 2, 11; issue/archive shards | Removed closed A08, A13 and A17 from the active index and retained their dated closure evidence in the archive. | Keep §2 limited to current open work. `[INSPECTED]` prior closure records |
| 2026-11-06 | all | R3 cap, registry, CSS gates, A01–A22 and budget established. | Detailed older record in `CHANGELOG_ARCHIVE.md#changelog-archive`. `[INSPECTED]` |

**`[OFFLOAD-SHARD]`:** Before changing governance history or rotating rows, read `docs/governance/CHANGELOG_ARCHIVE.md#changelog-archive` in full before modifying workspace files.

## 12. Done Definition

- [ ] Fingerprint protects the master and non-authorized files; only permitted paths changed.
- [ ] Architecture/HTML gates pass: JS budgets/registry/banned patterns; zero inline styles; correct layers; IDs/anchors/tables/SVG; AGENTS ≤24,576 B. Until gates exist, report `[NOT RUN]`.
- [ ] Existing suite and negative fixtures run only after side-effect review; saved `CHECKS.md` is not fresh proof.
- [ ] Strict TS compiles with zero `any`; JS-off reading/navigation/fallback/print and keyboard path verified.
- [ ] Theme contrast, focus, reduced motion, forced colors, print and visual screenshots reported with tool/engine/limits.
- [ ] Changed claims are source-page verified; Latvian terms, units and provenance reviewed.
- [ ] All shard files are nonempty; every `[OFFLOAD-SHARD]` path/anchor resolves; evidence tags are accurate.

**`[OFFLOAD-SHARD]`:** Before verification or release sign-off, read `docs/governance/INFRA_PYTHON_TS_JS_AUDIT.md#verification-suite` in full before modifying workspace files.
