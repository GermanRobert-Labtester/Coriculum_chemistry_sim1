# N33 Verification Record — Keyboard-Only Operation and Screen-Reader Semantics

**Date:** 2026-11-19 | **Task:** N33 | **Phase:** Phase VII | **Machine Status:** `VERIFIED` | **Manual Protocol Status:** `UNVERIFIED` (staged for Phase VIII `N38`)

## 1. Deliverables and SHA-256 Digests

| Artifact / Touchpoint | Role | Size (bytes) | SHA-256 |
|---|---|---:|---|
| [`data/keyboard_map.json`](../data/keyboard_map.json) | Context-scoped keyboard map (`exam`, `practice`, `revision`, `settings`, `drawer-open`), modifier/input-guard rules, focus contract, live-region contract | 6,924 | `1cee12033863d33f2c8a0f23d8dc71f3c7ef26281e5aa3f7d719115a5b033e54` |
| [`src/focus.ts`](../src/focus.ts) | Strict TypeScript focus-management module (map validation, input-guard, view-transition heading focus, drawer return-focus & tab-escape, single-announcement live regions) | 22,819 | `d3de1e97e2e58819beab79ce57f428d63d76264da6b90ea991aefea604a5d7ed` |
| [`src/compiled/focus.js`](../src/compiled/focus.js) | Compiled runtime module (`SimFocus`, module order `37` in `data/build_policy.json`) | 23,053 | `4cfc5950b2124fcc69216d1714ad19b0296d48ece3f976b48b9c0541e03273f5` |
| [`tools/check_a11y.py`](../tools/check_a11y.py) | Static & Node ARIA/keyboard/focus checker + Build Gate 30 (`a11y_contract`) | 27,148 | `bc3e42cf78d976b8ee3cee32e4edb8ee6fca42fa76d23b82ac3522abc0848f7a` |
| [`docs/SCREEN_READER_PROTOCOL.md`](../docs/SCREEN_READER_PROTOCOL.md) | Staged manual screen-reader & keyboard protocol (5 scenarios, expected announcements from Name Table, mandatory defect-filing rule, Falkon/offline scope) | 7,710 | `79f61340b679adcc9e4b4240fbfa4927361dab8c139dd49491aaab16586e3615` |
| [`src/smoke-subset.js`](../src/smoke-subset.js) | Extended with `SMK-N33-KEYBOARD-FOCUS` (`29/29` smoke vectors PASS) | 69,397 | `dad3c8fc453936ce368807ef61560c4f716c0967405abb8d7bffafc8e5ee7f40` |
| [`output/simulator.html`](../output/simulator.html) | Single-file offline deliverable (`2,674,476` B, 30/30 gates PASS) | 2,674,476 | `9b3be45e19f741792b396b1015c7e97313b4e8461e3c906531575fb555228eaf` |
| [`output/build-manifest.json`](../output/build-manifest.json) | Build manifest (30/30 gates PASS, 38 modules) | 92,636 | `77ebb57b4f8779293e64d1a64f7fa46cc8549536739fd51b57d25a798150c7d5` |
| [`evidence/N33_A11Y_REPORT.json`](N33_A11Y_REPORT.json) | Full Name Table (46 shell controls + 18 N22 response types), landmarks, live regions, and fixtures | 37,135 | `06f6a8d1bc0ca5b5368c7764e78d82b6a399ba2e1d355db039fb6b3d097ae4f5` |
| [`evidence/N33_CORPUS_RECORD.json`](N33_CORPUS_RECORD.json) | Two-run parity and full suite record | 2,265 | — |

## 2. Main Step A — Keyboard Map, Collision, Focus Escape, and Typing Fixtures (`VERIFIED`)

- **Keyboard Map Validation (`PASS`):** `SimFocus.validateKeyboardMap` checked all 5 contexts (`exam`, `practice`, `revision`, `settings`, `drawer-open`) with zero key collisions and zero browser/AT key overrides.
- **Scratch Collision Fixture (`PASS`):** Binding `exam_note_scratch` to key `'n'` in context `'exam'` (alongside `exam_next`) fails with `E_KEYMAP_COLLISION: Key collision in context "exam" for key "n": actions [exam_next, exam_note_scratch].`
- **Focus Escape & Restore Fixture over `#concept-drawer` (`PASS`):** `SimFocus.walkTabSequence` walked in from `concept-node-T1-01`, through `["concept-drawer-close", "concept-drawer-prereq-1", "concept-drawer-practice-link"]`, and escaped outside `#concept-drawer` to `post-drawer-next-control` (`escapedOutsideDrawer: true`); `SimFocus.closeDrawer` restored focus to `concept-node-T1-01`.
- **Typing-Context Input-Guard Fixture (`PASS`):** Keying topic-jump letter `'t'` inside `<input id="q01-numeric-answer" type="number">` returned `{ handled: false, suppressed: true, reason: "typing_context", action: null }` without triggering navigation.

## 3. Main Step B — Static & Component Semantics (`VERIFIED`)

- **Interactive Controls (`PASS`, 46/46):** Every interactive control in `output/simulator.html` has a non-empty computed accessible name (`name_errors=0`).
- **Scratch Empty-Label Fixture (`PASS`):** `<button id="scratch-icon-flag" type="button" aria-label="">` fails with `E_EMPTY_ARIA_LABEL: component "scratch-icon-flag" has empty aria-label=""`.
- **18 N22 Response Types (`PASS`, 18/18):** `Q01`–`Q18` rendered via `SimInputsComponents.render` all resolve non-empty Latvian accessible names, roles, and states against `data/response_types.json`.
- **Landmarks & Headings (`PASS`):** `1` `<main>`, `3` uniquely labeled `<nav>` landmarks, `9/9` required Section 1.2 `<section aria-labelledby="...">` landmarks, `1` `<h1>`, `0` heading level skips, and documented list-item allowance for `#exam-map` / `#exam-navigator`.
- **Live Regions (`PASS`):** Single dedicated region per event (`#sim-live-timer` `assertive`/`alert`, `#sim-live-verdict` `polite`/`status`, `#sim-live-view` `polite`/`status`); `#exam-timer-bar` carries no `aria-live`; Node harness fires each event once with announcement count `1/1/1`.

## 4. Main Step C — Manual Protocol, Two-Run Parity, Smoke, and Handoffs

- **Manual Screen-Reader Protocol ([`docs/SCREEN_READER_PROTOCOL.md`](../docs/SCREEN_READER_PROTOCOL.md)):** **`UNVERIFIED`** — staged with 5 execution-ordered scenarios, expected-announcement tables, and mandatory keyboard-completion defect-filing rule; awaiting Phase VIII (`N38`) execution.
- **Two-Run Rebuild Parity (`PASS`):** Two consecutive fresh-process `python3 tools/build.py` runs produced byte-identical `output/simulator.html` (`2,674,476` B, `sha256: 9b3be45e19f741792b396b1015c7e97313b4e8461e3c906531575fb555228eaf`) and `output/build-manifest.json` (`92,636` B, `sha256: 77ebb57b4f8779293e64d1a64f7fa46cc8549536739fd51b57d25a798150c7d5`).
- **In-File Smoke (`PASS`, 29/29):** `node tools/check_n31_runtime.js` passed `modules=38/38 globals=37 islands=22/22 smoke=29/29` (`SMK-N33-KEYBOARD-FOCUS` PASS).
- **N22 ARIA Parity (`PASS`):** `node tools/check_n22_components.js` and `node tools/check_n22_semantics.js` both exit `0` (`PASS`).
- **Handoffs:**
  - **To N37:** `data/keyboard_map.json` (visible-focus expectations per context and control).
  - **To N38:** `docs/SCREEN_READER_PROTOCOL.md` and `evidence/N33_A11Y_REPORT.json` (Name Table and expected announcements).
