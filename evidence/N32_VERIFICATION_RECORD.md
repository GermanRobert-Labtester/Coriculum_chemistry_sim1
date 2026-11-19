# N32 Verification Record — Responsive Layout and WCAG 2.2 AA Contract

**Date:** 2026-11-19 | **Task:** N32 | **Phase:** Phase VII | **Status:** `PASS`

## 1. AA Scope Statement (Verbatim)

> WCAG 2.2 AA contrast (4.5:1 body text, 3:1 large text and UI boundaries/focus), 44x44 px touch target floor with declared hit-area padding exceptions, and no color-only meaning; WCAG 2.2 AAA and external body certification are explicitly out of scope.

## 2. Deliverables and SHA-256 Digests

| Artifact / Touchpoint | Role | Size (bytes) | SHA-256 |
|---|---|---:|---|
| [`data/tokens.json`](../data/tokens.json) | Design token artifact: 26 semantic color tokens x 2 themes (`light`/`dark`), 27 classified color pairs, 16px (`1rem`) body floor, 44px (`2.75rem`) target floor + `--target-hit-pad` exception for `.exam-timer-chip`, `[320, 390, 768, 1280]` breakpoints & 10-view `layout_regions` | 18,834 | `74c1403cfb737fc58b44d19f60d22bf58a8f59148482834dec6f8959e73f5657` |
| [`src/styles.css`](../src/styles.css) | Token-only CSS layer reworked across all views with mobile-first breakpoints (`320` floor, `24.375rem` / `390`, `48rem` / `768` two-pane exam & multi-column practice, `80rem` / `1280` ceiling), 0 raw hex/unit findings, 0 undefined tokens | 58,624 | `09010cd8e1f1dd1e683d32fb828b28fdd261fdf65ffddecdd4d8000f25d63d7b` |
| [`tools/check_contrast.py`](../tools/check_contrast.py) | Standalone WCAG 2.2 AA contrast, target-size, hex-scan, and geometric layout-reflow validator + Build Gate 29 (`wcag_contract`) | 18,787 | `ed30c030fe4cf92597321c7efb5e257ced3a6ef83a11a5aedcab8b49d5322c78` |
| [`tools/build.py`](../tools/build.py) | N31/N32 single-file build pipeline with Gate 29 (`wcag_contract`) wired before assembly and atomic write | 125,094 | `6747c30d3190fafe316e18af049916293112c599d7ad7d00b4b0b95ef957cc3b` |
| [`src/smoke-subset.js`](../src/smoke-subset.js) | In-file smoke suite extended with `SMK-N32-CONTRAST-CONTRACT` (28/28 vectors PASS) | 66,207 | `e64aa6085ca3376e418ad716bc67ed63c408e5ec469e77d928780b0d4302c38d` |
| [`output/simulator.html`](../output/simulator.html) | Single-file offline deliverable (`build_id: 472de243cf3ad65f`, `composite_digest: 472de243cf3ad65fe9b4e444948d49a105b775071fcce5f8f880f15fcb5de9ba`) | 2,653,669 | `a7ce92866600777cdd71e9c320f2e6f05d7e46ede33ea68ae0d32cd90c6f7038` |
| [`output/build-manifest.json`](../output/build-manifest.json) | Build manifest (29/29 gates PASS, composition table, CSS `62,076` B = `60.6 KiB`) | 91,887 | `179ae82a880559866de7755abb0accac403f4ea522e0899ddc64f0d8f6f9b308` |
| [`evidence/N32_CONTRAST_REPORT.json`](N32_CONTRAST_REPORT.json) | Full machine-checked contrast, target, hex-scan, reflow, and negative-fixture report | 40,135 | `a15704c3740a0d3aa8934dc305eb43944470a9dab2b1cc4acd6c8c1984e943c6` |

## 3. Contrast Ratios Across Both Themes (27/27 Pairs PASS)

| Pair ID | Use Class | Tokens | Min | Light Ratio | Dark Ratio | Status |
|---|---|---|---:|---:|---:|---|
| `pair-primary-on-canvas` | `text-classed` | `--fg-primary` on `--bg-canvas` | 4.5:1 | 14.92:1 | 15.54:1 | PASS |
| `pair-primary-on-surface` | `text-classed` | `--fg-primary` on `--bg-surface` | 4.5:1 | 13.55:1 | 13.65:1 | PASS |
| `pair-primary-on-elevated` | `text-classed` | `--fg-primary` on `--bg-elevated` | 4.5:1 | 16.04:1 | 12.01:1 | PASS |
| `pair-primary-on-hover` | `state-classed` | `--fg-primary` on `--state-hover-bg` | 4.5:1 | 12.17:1 | 10.31:1 | PASS |
| `pair-primary-on-active` | `state-classed` | `--fg-primary` on `--state-active-bg` | 4.5:1 | 13.42:1 | 11.84:1 | PASS |
| `pair-muted-on-canvas` | `text-classed` | `--fg-muted` on `--bg-canvas` | 4.5:1 | 7.47:1 | 9.3:1 | PASS |
| `pair-muted-on-surface` | `text-classed` | `--fg-muted` on `--bg-surface` | 4.5:1 | 6.78:1 | 8.17:1 | PASS |
| `pair-muted-on-elevated` | `text-classed` | `--fg-muted` on `--bg-elevated` | 4.5:1 | 8.03:1 | 7.19:1 | PASS |
| `pair-accent-on-canvas` | `text-classed` | `--fg-accent` on `--bg-canvas` | 4.5:1 | 7.54:1 | 9.43:1 | PASS |
| `pair-accent-on-surface` | `text-classed` | `--fg-accent` on `--bg-surface` | 4.5:1 | 6.85:1 | 8.28:1 | PASS |
| `pair-accent-on-elevated` | `text-classed` | `--fg-accent` on `--bg-elevated` | 4.5:1 | 8.1:1 | 7.29:1 | PASS |
| `pair-accent-on-accent-subtle` | `text-classed` | `--fg-accent` on `--bg-accent-subtle` | 4.5:1 | 6.78:1 | 7.18:1 | PASS |
| `pair-on-accent-solid` | `text-classed` | `--fg-on-accent` on `--bg-accent-solid` | 4.5:1 | 9.23:1 | 9.12:1 | PASS |
| `pair-official-panel` | `state-classed` | `--fg-official` on `--bg-official` | 4.5:1 | 9.65:1 | 9.13:1 | PASS |
| `pair-proposed-panel` | `state-classed` | `--fg-proposed` on `--bg-proposed` | 4.5:1 | 7.89:1 | 9.24:1 | PASS |
| `pair-error-alert` | `state-classed` | `--fg-error` on `--bg-error` | 4.5:1 | 7.96:1 | 9.05:1 | PASS |
| `pair-ok-status` | `state-classed` | `--fg-ok` on `--bg-ok` | 4.5:1 | 9.74:1 | 9.13:1 | PASS |
| `pair-pending-slot` | `state-classed` | `--state-disabled-fg` on `--bg-surface` | 4.5:1 | 6.08:1 | 7.23:1 | PASS |
| `pair-border-subtle-canvas` | `boundary-classed` | `--border-subtle` on `--bg-canvas` | 3.0:1 | 4.17:1 | 5.13:1 | PASS |
| `pair-border-subtle-surface` | `boundary-classed` | `--border-subtle` on `--bg-surface` | 3.0:1 | 3.79:1 | 4.5:1 | PASS |
| `pair-border-subtle-elevated` | `boundary-classed` | `--border-subtle` on `--bg-elevated` | 3.0:1 | 4.48:1 | 3.96:1 | PASS |
| `pair-border-strong-canvas` | `boundary-classed` | `--border-strong` on `--bg-canvas` | 3.0:1 | 8.3:1 | 8.16:1 | PASS |
| `pair-border-official-canvas` | `boundary-classed` | `--border-official` on `--bg-canvas` | 3.0:1 | 7.01:1 | 8.05:1 | PASS |
| `pair-border-proposed-canvas` | `boundary-classed` | `--border-proposed` on `--bg-canvas` | 3.0:1 | 6.15:1 | 7.27:1 | PASS |
| `pair-border-error-canvas` | `boundary-classed` | `--border-error` on `--bg-canvas` | 3.0:1 | 7.81:1 | 6.73:1 | PASS |
| `pair-focus-canvas` | `state-classed` | `--state-focus` on `--bg-canvas` | 3.0:1 | 7.54:1 | 9.43:1 | PASS |
| `pair-focus-elevated` | `state-classed` | `--state-focus` on `--bg-elevated` | 3.0:1 | 8.1:1 | 7.29:1 | PASS |

## 4. Target-Size, Hex-Scan, ARIA Parity, and Negative Fixtures

- **Target-size floor (`PASS`, 15/15 controls):** 14 standard/form controls enforce `min-height: var(--target-min)` (`2.75rem` / `44 px`); 1 declared dense-inline exception (`.exam-timer-chip`, `timer-chip-dense-inline`) uses `--target-dense-min` visually with `--target-hit-pad` + `--target-min` hit-area expansion.
- **Hex & raw-unit scan (`PASS`, 0 findings):** Zero raw hex/color functions and zero raw `px`/`rem`/`em` literals outside `@layer tokens` and `@media` queries in `src/styles.css`; zero inline `style=` attributes in `src/shell.html`; zero undefined `var(--*)` references.
- **N22 ARIA parity (`PASS`):** `node tools/check_n22_components.js` and `node tools/check_n22_semantics.js` both exit `0` (`PASS`) after the `src/styles.css` rework.
- **Negative & corner-case fixtures (`python3 tools/check_contrast.py --run-fixtures`, `PASS`):**
  - `fixture-near-miss-4.4`: `#787878` on `--bg-elevated` (`4.42:1 < 4.5:1`) fails naming `pair-muted-on-elevated` and ratio.
  - `fixture-use-class-misuse-3.2`: `text-classed` pair with `min_ratio: 3.2` fails naming `scratch-misuse-text-3-2` and `text-classed`.
  - `fixture-undersized-target`: `.scratch-tiny-btn` without `--target-min` fails naming `.scratch-tiny-btn`.
  - `fixture-hex-regression`: `.practice-runner-regression { color: #ff0000; }` fails naming `src/styles.css#practice-runner-regression` and `#ff0000`.
- **Build Gate 29 failure fixture (`PASS`):** Dropping `--fg-muted` to `#787878` in a scratch `tokens.json` causes `tools/build.py` to fail fast (exit code `1`) naming `pair-muted-on-canvas` (`4.11:1 < 4.5:1`) before any output artifact is written.

## 5. Layout-Region Reflow Geometry & N37 Handoff

- **120/120 geometric reflow checks (`PASS`):** 3 N26 learner profiles (`fresh`, `mid_progress`, `near_complete`) x 4 breakpoint classes (`320`, `390`, `768`, `1280`) x 10 views (`navigation`, `start`, `concept_map`, `practice`, `exam`, `results`, `revision`, `methods`, `print`, `settings`).
- At `320` and `390`: `exam` `navigator_mode == "sheet"`, `practice` `columns == 1`, zero horizontal clip, zero pairwise region overlap.
- At `768` and `1280`: `exam` `navigator_mode == "sidebar"` (`columns == 2` two-pane layout), zero horizontal clip, zero pairwise region overlap.
- **Handoff to N37:** `data/tokens.json` (`breakpoints.layout_regions`) and `evidence/N32_CONTRAST_REPORT.json` (`layout_reflow`) are frozen as the expected-geometry source for N37's browser-rendered visual matrix.

## 6. Two-Rebuild Idempotence & Final Composition Table

- **Fresh-process rebuilds:** Two consecutive invocations of `python3 tools/build.py` produced byte-identical `output/simulator.html` (`2,653,669` B, SHA-256 `a7ce92866600777cdd71e9c320f2e6f05d7e46ede33ea68ae0d32cd90c6f7038`) and `output/build-manifest.json` (`91,887` B, SHA-256 `179ae82a880559866de7755abb0accac403f4ea522e0899ddc64f0d8f6f9b308`).
- **In-file runtime & smoke (`node tools/check_n31_runtime.js`):** `modules=37/37 globals=37 islands=22/22 smoke=28/28` (`SMK-N32-CONTRAST-CONTRACT` PASS).
- **Standalone artifact contract (`python3 tools/check_artifact.py`):** `PASS` (`2,653,669` B, `lang=lv`, `anchors=9/9`, `core_islands=7/7`, `all_islands=22/22`, `scripts=1`, `ext_urls=0`, CSS `62,076` B = `60.6 KiB` within `40–80 KiB` sub-budget).
