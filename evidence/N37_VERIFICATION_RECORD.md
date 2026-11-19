# N37 Verification Record — Visual Regression Matrix (lite-shot + Falkon)

**Date:** 2026-11-19 | **Task:** N37 | **Phase:** Phase VIII | **Status:** `PASS`
**Artifact Under Test:** `output/simulator.html` (`99fd5c406950be1739b1d3480645d1698ed03eac6558f706d9f2c85b5f11745a`, `2,832,984` B)

---

## 1. Epistemic Scope Header (Verbatim)

- **Engine:** `Falkon (QtWebEngine) via lite-shot --engine falkon --cdp`
- **Authorization Citation (`AGENTS.md`):**
  > Follow the parent visual policy: lite-shot with Falkon, inspect PNGs; do not use webshot or Chrome/Chromium without explicit user authorization. Blank captures or blocked X displays are UNVERIFIED.
- **Viewports:** `320x640`, `390x844`, `768x1024`, `1280x800`
- **Themes & Modes:** `light`, `dark` (`screen` mode) + `light` (`print` stylesheet mode for `#druka` F04 worksheet)
- **Out-of-Scope / Unavailable Engines:**
  - `Chrome/Chromium (explicitly forbidden by AGENTS.md without authorization)`
  - `Firefox (UNAVAILABLE in environment)`
  - `Safari/WebKit (UNAVAILABLE in environment)`
- **Cross-Engine Delegation:** Cross-engine coverage is delegated to **N38** offline smoke rather than claimed here.

---

## 2. Deliverables and SHA-256 Digests

| Artifact | Role | Bytes | SHA-256 |
|---|---|---:|---|
| [`tools/visual_matrix.py`](../tools/visual_matrix.py) | Visual matrix generator, `lite-shot` + Falkon capture harness, perceptual comparator, fixture runner & replay prover | 32,934 | `3d8ca24dca69a885204a0da507a3db28acdfa3a289ca7bb7116afaece2ddb519` |
| [`data/visual_matrix.json`](../data/visual_matrix.json) | 219-cell matrix definition (`3` profiles × `9` views × `4` breakpoints × `2` themes + `3` print cells, mapped to `73` unique renders) | 128,864 | `b0d0a562cd4c8f01a87ae577f5c9bf0637fb468441a16648ec92211888b89374` |
| [`evidence/visual_baselines/baseline_manifest.json`](visual_baselines/baseline_manifest.json) | Versioned baseline manifest (`v1`, `73` PNGs, composite digest `447569bfd83c85301919bab44ef7c8de7e50adcb89ee4a181af13434f5662291`) | 52,385 | `0ff5754ce56615d0e4f07fcc9548c66dfec731d33c95ed6d6e2bfe8967f4293f` |
| [`evidence/N37_CALIBRATION_AND_FIXTURES.json`](N37_CALIBRATION_AND_FIXTURES.json) | Two-run smoke calibration & negative/regression/noise fixture certificate | 2,177 | `128b4237aef8612a5f84d7fa862fc2e374246da69e0524037ef7b664e0ba56ba` |
| [`evidence/N37_MATRIX_REPORT.json`](N37_MATRIX_REPORT.json) | Full 219-cell comparison report (`219/219` `MATCH`, `0` `REGRESSION`) | 91,131 | `2c514fac5a5ee6ac3b2afe3ab1156fd887ba7e267554dfe079f218bfc8eb0a6f` |
| [`evidence/N37_REPLAY_PROOF.json`](N37_REPLAY_PROOF.json) | Two-run fresh-process replay determinism proof | 644 | `dec03fd3137b9338af252ca16a1b817573804c27145fa6f65d6c40600ce970a3` |

---

## 3. Calibration, Readiness, and Negative Fixtures (`PASS`)

- **Matrix Validation (`A.1.1`):** `python3 tools/visual_matrix.py --validate-matrix` verified `219/219` cells (`3` profiles × `9` Section 1.2 anchors × `4` breakpoints × `2` themes + `3` print cells) against `data/build_policy.json` and `data/tokens.json`.
- **Two-Run Smoke Calibration (`A.1.2`):** Consecutive `lite-shot --engine falkon --cdp` captures of `#sakums` (`1280x800`, `light`) returned `MATCH` (`diff_pct=0.0%`). Calibrated thresholds: `channel_noise_floor=4`, `max_diff_pct=0.50%`, `max_mae=0.50`. Theme-toggle check confirmed `probe.dark == False` (`light`) and `probe.dark == True` (`dark`), guarded by luminance verification (`light >= 140`, `dark <= 100`, `print >= 170`) and `--reduced-motion --anchor` deterministic scrolling.
- **Print-Class Capture (`A.1.3`):** `druka__1280__light__print.png` verified `mediaPrint == True`, `overflow == False`, black-on-white paper layout, 21-slot Form A worksheet, `N23-C01` visible source conflict box, and N34 print figure policy (`--print-fig-width: 140mm`, `--print-fig-min-width: 85mm`).
- **Negative & Calibration Fixtures:**
  - `FIX-VM-DANGLING-CELL` (`PASS`): Scratch cell `fresh__neeksistejoss_skats__1280__light__screen` rejected by `cell_id` (`E_DANGLING_ANCHOR` / `E_DANGLING_VIEW`).
  - `FIX-VM-NEVER-READY` (`PASS`): Blank scratch HTML (`<body></body>`) rejected with `Readiness/paint timeout` (`colors=1 < 16, ink=0% < 2%`).
  - `FIX-VM-PLANTED-OVERLAP` (`PASS`): Scratch `simulator.html` with injected `#sakums` overlap CSS (`margin-top: -120px`, `#ff00ff`) caught as `REGRESSION` (`diff_pct=42.0967%`, region `[[96, 0, 1184, 800]]`, `human_review=True`).
  - `FIX-VM-PLANTED-NOISE` (`PASS`): 1px AA luminance jitter (`-2` on 20px edge) classified as `NOISE` (`diff_pct=0.0%` above noise floor).
- **Versioned Baseline Rule:** Baseline updates require `--update-baseline --render-key <key> --reason <text>`, appending `{version, timestamp, render_key, previous_sha256, new_sha256, reason}` to `update_history` in `baseline_manifest.json` (refuses silent overwrites or `artifact_digest` mismatches).

---

## 4. Full Matrix Comparison & Two-Run Fresh-Process Replay Proof (`PASS`)

- **Run 1 (`evidence/N37_REPLAY_RUN1.json` / `evidence/N37_MATRIX_REPORT.json`):** `219/219` `MATCH`, `0` `NOISE`, `0` `REGRESSION` across `73/73` unique Falkon captures (`verdict_sequence_sha256 = 803e4093af99f66ffa5116cf520b502742e1461bc8dc7271c1d30deb6b989eeb`).
- **Run 2 (`evidence/N37_REPLAY_RUN2.json`):** `219/219` `MATCH`, `0` `NOISE`, `0` `REGRESSION` (`verdict_sequence_sha256 = 803e4093af99f66ffa5116cf520b502742e1461bc8dc7271c1d30deb6b989eeb`).
- **`identical_verdicts`:** `True` (`evidence/N37_REPLAY_PROOF.json`).

---

## 5. N39 QA Runner Registration

- **Suite ID:** `N37-VISUAL-MATRIX`
- **Command:** `python3 tools/visual_matrix.py --validate-matrix --compare --out evidence/N37_MATRIX_REPORT.json`
- **Expected Exit Codes:** `0` (`PASS`), `1` (`FAIL` on regression, artifact mismatch, or readiness failure)
- **Runtime Estimate:** `~480s` (sequential `lite-shot --engine falkon --cdp` across `73` unique renders)
