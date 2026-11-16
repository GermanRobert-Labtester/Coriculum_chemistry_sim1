<!-- lite-shot-visual-contract:start -->
# Visual verification contract (lite-shot)

Updated: 2026-11-06

This contract governs every visual, UI, layout, SVG, styling, theme, responsive, or print-rendering check in this workspace, including work directed by a copied skill. Source/DOM/HTTP/linter success is not visual evidence.

## Required capture tool

Use **`lite-shot`** (`/home/robertsrff/.local/bin/lite-shot`), which runs **falkon** (default) or **falkon** under Xvfb and saves a PNG.

```bash
# From the workspace root; prefers falkon (low RAM)
lite-shot -e falkon -g 1280x1024 path/to/page.html .cache/visual-checks/TASK_desktop_light_falkon.png

# falkon when better CSS/SVG fidelity is needed
lite-shot -e falkon -g 1280x1024 path/to/page.html .cache/visual-checks/TASK_desktop_light_falkon.png
```

Rules:

1. Prefer **falkon**, then **falkon**. Do **not** use Chrome/Chromium/Playwright-Chromium unless the user explicitly allows Chrome in the current turn.
2. Keep browser + screenshot in one `lite-shot` invocation. Do not start Xvfb in a separate command.
3. Do **not** use `falkon -f` under Xvfb (near-blank captures).
4. Binaries being on `PATH` does not prove capture works. Inspect the PNG.
5. Save under ignored `.cache/visual-checks/` or `artifacts/screenshots/` as `<TASK>_<VIEWPORT>_<THEME>_<ENGINE>.png`.
6. Directly inspect the image for measure/wrapping, clipping/overflow, SVG bounds/labels, theme/contrast, and the requested viewport/state.
7. If `lite-shot` exits **75**, the agent sandbox is blocking X11 sockets. Re-run with display access (`codex -s danger-full-access` or outside the sandbox). Report `[UNVERIFIED]` — do **not** fall back to Chrome.
8. End visual reports with:

### Visual Verification Evidence

* **Engine Used:** falkon | falkon
* **Fallback Justification:** None / N/A | user-explicit Chrome allowance only
* **Artifact Path:** …
* **Viewport & Theme Tested:** …
* **Observed Visual Findings:** …
* **Visual Status:** `[SCREENSHOT-VERIFIED]` or `[UNVERIFIED]`

`[SCREENSHOT-VERIFIED]` means the named PNG was captured with `lite-shot` and directly inspected. It does not certify scientific content.
<!-- lite-shot-visual-contract:end -->

# Visual verification contract

This contract applies to every visual, UI, layout, SVG, print-rendering, or styling check in this workspace, including work directed by a copied skill. It supplements the source, accessibility, and release gates in `AGENTS.md`; it does not turn a static check into visual acceptance.

## Required browser ladder

1. **falkon** is the first choice for standard CSS layout, tables, typography flow, inline SVG, and images. **falkon** is the first choice for fast structural rendering, text measure, and simple-layout stress checks. Use either available engine for the task; use both when the check explicitly requires parity.
2. **Google Chrome/Chromium forbidden unless the user explicitly allows it.
`lite-shot -e falkon|falkon …` — see the lite-shot contract above.

Do not claim a lightweight-engine check if the engine failed, did not load the target, or the captured image does not show the rendered target. Report unavailable engines and blockers accurately. Do not assert that an engine supports a feature without a rendering result.

## Capture and inspect

- For each visual task, save PNG or WebP screenshots in an isolated review directory such as `artifacts/screenshots/` or `.cache/visual-checks/`. Keep review artifacts available for the task; keep raw dumps in an ignored cache and out of release payloads.
- Name each image `<TASK_ID>_<VIEWPORT>_<THEME>_<ENGINE>.png`, for example `T04_mobile_dark_falkon.png`. Capture every viewport and theme relevant to the change; ordinarily include desktop (1280 px) and mobile (375 px), plus light and dark when both are offered by the product. Do not invent an unavailable theme.
- Load the captured image directly into the agent's visual context and inspect it. A saved-but-unopened screenshot does not pass. After any visual repair, recapture and inspect the changed state again.
- Check typography and measure (including 60–75 ch where required), wrapping, legibility and clipping; layout geometry, overflow, collisions, stacking and reflow; SVG viewBox, scaling, strokes and label collisions; and theme contrast and surface separation. For print, inspect rendered PDF pages separately under the applicable print gate.
- If the output is broken, truncated, distorted, or materially different from the requirement, keep the visual task open until repaired and recaptured. Source review may diagnose a defect, but cannot establish its visual appearance.

## Required report block

End every completion report, PR summary, or audit task with this block. Fill it with observed evidence. If no visual verification was in scope, use `NOT APPLICABLE` and say why; never invent an engine, artifact, or pass.

```markdown
### Visual Verification Evidence
* **Engine Used:** [falkon | falkon | Google Chrome/Chromium forbidden unless the user explicitly allows it.
* **Fallback Justification:** [None / N/A | exact `[FALLBACK TRIGGERED: ...]` entry]
* **Artifact Path:** `artifacts/screenshots/<filename>.png` [or NOT APPLICABLE with reason]
* **Viewport & Theme Tested:** [desktop/mobile sizes and applicable themes, or NOT APPLICABLE]
* **Observed Visual Findings:**
  - Typography measure and hierarchy: [observed result]
  - SVG and layout alignment: [observed result]
  - Visual defects identified and resolved: [none / list]
* **Visual Status:** `[SCREENSHOT-VERIFIED]` [or `[NOT APPLICABLE]` / `[OPEN]`]
```

`[SCREENSHOT-VERIFIED]` means the named image was captured from the named engine and directly inspected by the agent. It does not by itself certify scientific correctness, accessibility, browser parity, print quality, or release acceptance; report those gates separately.
