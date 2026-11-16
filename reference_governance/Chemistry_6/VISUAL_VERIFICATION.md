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

