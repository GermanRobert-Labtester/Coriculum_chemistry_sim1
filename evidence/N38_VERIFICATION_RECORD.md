# N38 Verification Record — Cross-Engine Offline Smoke & Staged Manual Protocols

**Date:** 2026-11-20 | **Task:** N38 | **Phase:** Phase VIII | **Status:** `PASS`
**Artifact Under Test:** `output/simulator.html` (`12e36ae39677a090750d014eac3621b7138e8bd4831b6b64cf2a4a953f55ce80`, `2,834,200` B)

---

## 1. Honest Cross-Engine Statement (Verbatim)

> The artifact is proven alive, correct, and offline in Falkon (QtWebEngine) under the AGENTS.md policy, with the interaction path, focus behavior, verdicts, and storage degradation all evidenced; behavior in Chrome, Safari, Firefox, and on physical print remains UNVERIFIED in this environment.

---

## 2. Deliverables and SHA-256 Digests

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| [`tools/smoke_browser.py`](../tools/smoke_browser.py) | Falkon (Xvfb + CDP) offline smoke runner, calibration fixture runner, N33/N35 protocol executor & 3-run determinism prover | 60,606 | `316ae3babca1c2b35472ec9c23624089cb2b2bacec4a081846279665a9e2616d` |
| [`evidence/N38_SMOKE_REPORT.json`](N38_SMOKE_REPORT.json) | Machine-readable N38 smoke, calibration, N33/N35 protocols, and 3-run determinism report | 23,354 | `820bfc9f1933456f9203406b555da4e275ce8f8077fd8be419065ae6c93108b3` |
| [`output/simulator.html`](../output/simulator.html) | Rebuilt single-file offline artifact (`30/30` build gates PASS) | 2,834,200 | `12e36ae39677a090750d014eac3621b7138e8bd4831b6b64cf2a4a953f55ce80` |

---

## 3. Defects Discovered & Fixed During Browser Smoke

Running the real-DOM Falkon smoke and N33 keyboard protocol exposed the following real defects, all fixed in source and rebuilt (`30/30` build gates PASS):

1. **`src/practice.ts` (`#prakse-submit-btn` & `gContext.terms`):** `#prakse-submit-btn` had no click listener in `init()`, and `buildGradedSlotSummary` passed the raw `#sim-terms` island object instead of `doc` to `SimFeedback.loadTermsMap`. Wired `#prakse-submit-btn` and passed `doc || termsIsland` (`e7fa858273bdc6aa...`).
2. **`src/shell.html` (`SimInputsRegistry.load` & `#atskats-revision-heading`):** `SimInputsRegistry.load` was not invoked at boot (`E_INPUTS_REGISTRY_INVALID` on practice grading), and `#atskats-revision-heading` lacked `tabindex="-1"` (`e77cc974f84fd4b8...`).
3. **`src/exam.ts` (`#exam-review-submitted` & `stopPropagation`):** Exam submit rendered no `#exam-review-submitted` status banner or `#sim-live-verdict` update, and `bindKeyboard()` let `f` bubble to `document` (`SimFocus`), double-toggling `#exam-flag` (`9f339c6c67c59338...`).
4. **`src/smoke-subset.js` (`SMK-N16-CHAINS-REVEAL` & `smoke-n08-help-btn`):** `SMK-N16-CHAINS-REVEAL` passed string `'click'` to `dispatchEvent` (failing in real DOM), and `SMK-N08-HINT-DRAWER` left temporary `#smoke-n08-help-btn` inside `#prakse-help-slot`, shadowing `#prakse-open-hint` for key `h` (`d7456609b6c10483...`).
5. **`src/hint-drawer.js` & `src/concept-drawer.js` (N33 no-focus-trap contract):** Both drawers intercepted `Tab` to wrap focus back to the first element, violating N33 Steps `2.4` and `5.3`; removed the `Tab` trap while preserving `Escape` close + focus restore (`729ee40be3dcc2ab...`, `146bf37373b90726...`).
6. **`src/focus.ts` (`handleKeyDown`):** Focused `tabindex="-1"` targets (e.g., `#atskats-revision-heading` on key `c`) before `.click()` (`dbf658ada69bb7b9...`).

---

## 4. Calibration Fixtures (`PASS`)

- **`FIX-SMOKE-BROKEN-ISLAND` (`PASS`):** Scratch copy with corrupted `#sim-bank` JSON failed at `readiness` naming `sim-bank` (`Visible boot errors in islands: sim-bank`).
- **`FIX-SMOKE-DEAD-SUBMIT` (`PASS`):** Scratch copy with `#exam-review-submit` click handler unbound failed at `exam_submit` (`step=exam_submit submit did not render report or verdict`).

---

## 5. Authorized Manual Protocols

### 5.1 N33 Screen-Reader & Keyboard Protocol (Split Epistemic Labels)

- **Summary:** `22` `VERIFIED` (keyboard navigation, DOM/ARIA state, live regions, focus restore, no focus trap), `26` `UNVERIFIED` (screen-reader speech/braille output unavailable in headless Xvfb + Linux offline workspace; Scenario `3.6` real-time timer threshold alert; Scenario `4.3` completed self-assessment toggle in fresh session), `0` `FAILED`.
- Full row-by-row observed-versus-expected table is recorded in [`evidence/N38_SMOKE_REPORT.json`](N38_SMOKE_REPORT.json) under `protocols.n33_screen_reader_protocol.rows`.

### 5.2 N35 Browser-Side Performance Confirmation (Single-Engine: Falkon)

Pre-declared divergence threshold: `browser_ms <= max(ceiling_ms, harness_ms * 5.0)`.

| Row ID | Label | Harness (ms) | Browser (ms) | Ceiling (ms) | Status |
|---|---|---:|---:|---:|---|
| `island_parse` | All JSON islands parse (112/112 bank instances) | 4.067 | 23.9 | 150.0 | `VERIFIED` |
| `first_render_start` | First interactive start screen render | 0.266 | 4.0 | 50.0 | `VERIFIED` |
| `exam_navigator_interaction` | Exam navigator per-interaction max latency (21 slots) | 0.383 | 8.7 | 25.0 | `VERIFIED` |
| `revision_panel_interaction` | Revision panel render max latency (3 N26 profiles) | 27.026 | 96.8 | 40.0 | `VERIFIED` (within `5.0x` factor; `135.13` ms) |
| `keystroke_burst_incremental` | Exam answer 30-char typing burst (incremental fix) | 2.368 | 20.0 | 25.0 | `VERIFIED` |

---

## 6. Three-Run Determinism & Corpus Parity (`PASS`)

- **Three Fresh-Process Falkon Runs:** `3/3` `PASS` (`11/11` assertions each: readiness, 7/7 islands, 9/9 anchors, `file://` in-memory storage normalization, N05 oracle `GV-S1-T1-Q02-01` -> `correct`, practice DOM `COL1-1-1C-A-01`, hint drawer focus restore, exam end-to-end submit, `31/31` `SimSmoke`, `0` network attempts, `0` uncaught errors).
- **Comparable Verdict Sequence SHA-256:** `afe798e0e248961bc1c5cf0bd63737f4335daa4cdb5e782823785a6e88cf825a` (`identical_verdict_sequences: true`).
- **Preparation Corpus Parity (`verify_preparation.py`):** Two runs produced identical `status: PASS` across all `174` `COPY_MANIFEST.json` destinations (diffing only `checked_utc`).

---

## 7. Explicit `UNVERIFIED` Items Staged for N40 Release Gate

1. NVDA (Windows) screen-reader speech/braille announcements (N33)
2. VoiceOver (macOS) screen-reader speech/braille announcements (N33)
3. Orca / AT-SPI live speech output in headless Xvfb (N33)
4. Scenario 3.6 real-time timer threshold alert firing (N33)
5. Scenario 4.3 completed self-assessment toggle in fresh session (N33)
6. Chrome/Chromium rendering and interaction (explicitly forbidden by `AGENTS.md` without authorization)
7. Firefox rendering and interaction (`UNAVAILABLE` in environment)
8. Safari/WebKit rendering and interaction (`UNAVAILABLE` in environment)
9. Physical printer paper output (`UNAVAILABLE` in environment)

---

## 8. N39 QA Runner Registration

- **Suite ID:** `N38-BROWSER-SMOKE`
- **Command:** `python3 tools/smoke_browser.py --replay-runs 3 --include-calibration --include-protocols --out evidence/N38_SMOKE_REPORT.json`
- **Expected Exit Codes:** `0` (`PASS`), `1` (`FAIL` on smoke/calibration/protocol failure or determinism mismatch)
- **Three-Run Expectation:** `3` fresh-process Falkon runs with identical `verdict_sequence_sha256` (`normalized_state: in_memory_safe`)
- **Footprint & Runtime Estimate:** `60,606` B (`tools/smoke_browser.py`), `~35.4s` for full 3-run + calibration + N33/N35 suite
