#!/usr/bin/env python3
"""N37 Visual Regression Matrix Harness (lite-shot + Falkon policy).

Drives Falkon through `lite-shot --engine falkon --cdp` per AGENTS.md:
  - No Chrome/Chromium or unauthorized engines.
  - Enumerates the 219-cell matrix in `data/visual_matrix.json` (3 profiles x 9 views x
    4 breakpoints x 2 themes + 3 print-class cells), mapped to 73 unique Falkon
    renders (since `output/simulator.html` boots in-memory fresh state by default).
  - Validates matrix integrity, readiness markers, theme toggle state, and N34
    print-class geometry.
  - Freezes versioned baselines, runs perceptual differencing with bounding-box
    region reports, executes negative/calibration fixtures, and proves two-run
    fresh-process replay determinism.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

REPO_ROOT = Path(__file__).resolve().parent.parent

PROFILES = ["fresh", "mid_progress", "near_complete"]

VIEW_TO_ANCHOR = {
    "start": "sakums",
    "concept_map": "saturs",
    "practice": "prakse",
    "exam": "eksamens",
    "results": "rezultati",
    "revision": "atskats",
    "methods": "metodika",
    "print": "druka",
    "settings": "iestatijumi",
}

ANCHOR_TO_VIEW = {v: k for k, v in VIEW_TO_ANCHOR.items()}

BREAKPOINT_VIEWPORTS = {
    320: {"width": 320, "height": 640},
    390: {"width": 390, "height": 844},
    768: {"width": 768, "height": 1024},
    1280: {"width": 1280, "height": 800},
}

THEMES = ["light", "dark"]

DEFAULT_THRESHOLDS = {
    "channel_noise_floor": 4,
    "max_diff_pct": 0.50,
    "max_mae": 0.50,
}

EPISTEMIC_HEADER = {
    "engine": "Falkon (QtWebEngine) via lite-shot --engine falkon --cdp",
    "authorization_citation": (
        "AGENTS.md: 'Follow the parent visual policy: lite-shot with Falkon, "
        "inspect PNGs; do not use webshot or Chrome/Chromium without explicit "
        "user authorization. Blank captures or blocked X displays are UNVERIFIED.'"
    ),
    "viewports": ["320x640", "390x844", "768x1024", "1280x800"],
    "themes": ["light", "dark"],
    "modes": ["screen", "print"],
    "out_of_scope_engines": [
        "Chrome/Chromium (explicitly forbidden by AGENTS.md without authorization)",
        "Firefox (UNAVAILABLE in environment)",
        "Safari/WebKit (UNAVAILABLE in environment)",
    ],
    "cross_engine_delegation": (
        "Cross-engine coverage is delegated to N38 offline smoke rather than "
        "claimed here."
    ),
}

N39_REGISTRATION = {
    "suite_id": "N37-VISUAL-MATRIX",
    "task": "N37",
    "invocation_command": (
        "python3 tools/visual_matrix.py --validate-matrix --compare "
        "--out evidence/N37_MATRIX_REPORT.json"
    ),
    "expected_exit_codes": {"0": "PASS (all cells MATCH or NOISE)", "1": "FAIL (regression or readiness error)"},
    "runtime_estimate_seconds": 480,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def build_matrix_definition(repo_root: Path) -> dict[str, Any]:
    build_policy = load_json(repo_root / "data" / "build_policy.json")
    tokens = load_json(repo_root / "data" / "tokens.json")
    anchors = build_policy["blueprint_anchors"]["required_section_1_2"]
    bp_classes = tokens["breakpoints"]["classes_px"]
    layout_regions = tokens["breakpoints"]["layout_regions"]

    cells: list[dict[str, Any]] = []
    for profile in PROFILES:
        for anchor in anchors:
            view = ANCHOR_TO_VIEW[anchor]
            region_spec = layout_regions.get(view, {})
            for bp in bp_classes:
                vp = BREAKPOINT_VIEWPORTS[int(bp)]
                by_class = region_spec.get("by_class", {}).get(str(bp), {})
                for theme in THEMES:
                    render_key = f"{anchor}__{bp}__{theme}__screen"
                    cells.append({
                        "cell_id": f"{profile}__{render_key}",
                        "render_key": render_key,
                        "profile": profile,
                        "view": view,
                        "anchor": anchor,
                        "breakpoint": int(bp),
                        "viewport": vp,
                        "theme": theme,
                        "mode": "screen",
                        "readiness_marker": f"#{anchor}",
                        "expected_geometry": by_class,
                    })
        # Print-class cell for F04 worksheet (#druka)
        print_key = "druka__1280__light__print"
        cells.append({
            "cell_id": f"{profile}__{print_key}",
            "render_key": print_key,
            "profile": profile,
            "view": "print",
            "anchor": "druka",
            "breakpoint": 1280,
            "viewport": {"width": 1280, "height": 800},
            "theme": "light",
            "mode": "print",
            "readiness_marker": "#druka",
            "expected_geometry": {
                "print_fig_width": tokens["print_policy"]["figure_default_width"],
                "print_fig_min_width": tokens["print_policy"]["figure_min_width"],
                "link_url_policy": tokens["print_policy"]["link_url_policy"],
            },
        })

    unique_renders: dict[str, dict[str, Any]] = {}
    for c in cells:
        rk = c["render_key"]
        if rk not in unique_renders:
            unique_renders[rk] = {
                "render_key": rk,
                "view": c["view"],
                "anchor": c["anchor"],
                "breakpoint": c["breakpoint"],
                "viewport": c["viewport"],
                "theme": c["theme"],
                "mode": c["mode"],
                "readiness_marker": c["readiness_marker"],
            }

    return {
        "schema_version": 1,
        "task": "N37",
        "profiles": PROFILES,
        "views": [ANCHOR_TO_VIEW[a] for a in anchors],
        "anchors": anchors,
        "breakpoints": [int(x) for x in bp_classes],
        "themes": THEMES,
        "modes": ["screen", "print"],
        "thresholds": DEFAULT_THRESHOLDS,
        "cell_count": len(cells),
        "unique_render_count": len(unique_renders),
        "unique_renders": list(unique_renders.values()),
        "cells": cells,
    }


def validate_matrix_definition(matrix: dict[str, Any], repo_root: Path) -> list[str]:
    build_policy = load_json(repo_root / "data" / "build_policy.json")
    tokens = load_json(repo_root / "data" / "tokens.json")
    valid_anchors = set(build_policy["blueprint_anchors"]["required_section_1_2"])
    valid_bps = {int(x) for x in tokens["breakpoints"]["classes_px"]}
    valid_profiles = set(PROFILES)
    valid_themes = set(THEMES)
    valid_modes = {"screen", "print"}

    errors: list[str] = []
    seen_ids: set[str] = set()
    for cell in matrix.get("cells", []):
        cid = cell.get("cell_id", "<missing-id>")
        if cid in seen_ids:
            errors.append(f"E_DUPLICATE_CELL: {cid}")
        seen_ids.add(cid)

        if cell.get("profile") not in valid_profiles:
            errors.append(f"E_INVALID_PROFILE: {cid} -> {cell.get('profile')}")
        anchor = cell.get("anchor")
        view = cell.get("view")
        if anchor not in valid_anchors:
            errors.append(f"E_DANGLING_ANCHOR: {cid} -> anchor={anchor}")
        if VIEW_TO_ANCHOR.get(view) != anchor:
            errors.append(f"E_DANGLING_VIEW: {cid} -> view={view} anchor={anchor}")
        if cell.get("breakpoint") not in valid_bps:
            errors.append(f"E_INVALID_BREAKPOINT: {cid} -> {cell.get('breakpoint')}")
        if cell.get("theme") not in valid_themes:
            errors.append(f"E_INVALID_THEME: {cid} -> {cell.get('theme')}")
        if cell.get("mode") not in valid_modes:
            errors.append(f"E_INVALID_MODE: {cid} -> {cell.get('mode')}")

    return errors


def run_lite_shot(
    html_path: Path,
    out_png: Path,
    *,
    width: int,
    height: int,
    theme: str,
    anchor: str | None = None,
    mode: str = "screen",
    wait_sec: int = 20,
    min_colors: int = 16,
) -> dict[str, Any]:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    url = html_path.resolve().as_uri()

    cmd = [
        "lite-shot",
        "--engine", "falkon",
        "--cdp",
        "--reduced-motion",
        "-g", f"{width}x{height}",
        "-w", str(wait_sec),
        "-m", str(min_colors),
        "--theme", theme,
    ]
    if anchor:
        cmd.extend(["--anchor", anchor])
    if mode == "print":
        cmd.extend(["--media", "print"])
    cmd.extend([url, str(out_png)])

    max_attempts = 3
    last_err = ""
    for attempt in range(1, max_attempts + 1):
        t0 = time.monotonic()
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = round(time.monotonic() - t0, 3)

        if proc.returncode != 0:
            last_err = (
                f"lite-shot failed (rc={proc.returncode}) for {url}#{anchor or ''} "
                f"[{width}x{height} {theme} {mode}]: {proc.stderr.strip() or proc.stdout.strip()}"
            )
            continue

        telemetry: dict[str, Any] = {}
        for line in proc.stdout.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    telemetry = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        # Verify readiness & policy invariants on telemetry and paint metrics
        m_paint = re.search(r"colors=(\d+)\s+ink=(\d+)%", proc.stderr)
        colors = int(m_paint.group(1)) if m_paint else 0
        ink = int(m_paint.group(2)) if m_paint else 0
        if colors < min_colors and ink < 2:
            last_err = (
                f"Readiness/paint timeout for {out_png.name}: frame unpainted "
                f"(colors={colors} < {min_colors}, ink={ink}% < 2%)"
            )
            continue

        vp = telemetry.get("viewport") or {}
        probe = telemetry.get("probe") or {}
        if vp.get("w") != width or vp.get("h") != height:
            raise RuntimeError(f"Viewport mismatch for {out_png.name}: expected {width}x{height}, got {vp}")
        if vp.get("overflow") is True:
            raise RuntimeError(f"Horizontal overflow detected for {out_png.name}: {vp}")
        if probe.get("dark") != (theme == "dark"):
            last_err = f"Theme toggle mismatch for {out_png.name}: expected dark={theme=='dark'}, got {probe.get('dark')}"
            continue
        if mode == "print" and not probe.get("mediaPrint"):
            last_err = f"Print media mismatch for {out_png.name}: mediaPrint={probe.get('mediaPrint')}"
            continue

        # Verify rendered luminance matches requested theme/mode (guards against CDP setEmulatedMedia race)
        mean_luma = ImageStat.Stat(Image.open(out_png).convert("L")).mean[0]
        if mode == "print" and mean_luma < 170.0:
            last_err = f"Print luminance mismatch for {out_png.name}: mean_luma={mean_luma:.1f} < 170"
            continue
        if mode == "screen" and theme == "light" and mean_luma < 140.0:
            last_err = f"Light theme luminance mismatch for {out_png.name}: mean_luma={mean_luma:.1f} < 140 (CDP theme race)"
            continue
        if mode == "screen" and theme == "dark" and mean_luma > 100.0:
            last_err = f"Dark theme luminance mismatch for {out_png.name}: mean_luma={mean_luma:.1f} > 100 (CDP theme race)"
            continue

        return {
            "elapsed_s": elapsed,
            "attempts": attempt,
            "mean_luma": round(mean_luma, 2),
            "png_sha256": sha256_file(out_png),
            "bytes": out_png.stat().st_size,
            "telemetry": telemetry,
        }

    raise RuntimeError(last_err or f"lite-shot failed after {max_attempts} attempts for {out_png.name}")


def compare_images(
    baseline_png: Path,
    current_png: Path,
    thresholds: dict[str, Any],
) -> dict[str, Any]:
    im_a = Image.open(baseline_png).convert("RGB")
    im_b = Image.open(current_png).convert("RGB")

    if im_a.size != im_b.size:
        return {
            "verdict": "REGRESSION",
            "reason": f"size_mismatch: {im_a.size} vs {im_b.size}",
            "diff_pct": 100.0,
            "mae": 255.0,
            "diff_pixels": im_a.size[0] * im_a.size[1],
            "total_pixels": im_a.size[0] * im_a.size[1],
            "regions": [[0, 0, im_b.size[0], im_b.size[1]]],
            "human_review": True,
        }

    w, h = im_a.size
    total_pixels = w * h
    diff_im = ImageChops.difference(im_a, im_b)
    # Per-pixel max channel delta
    raw = diff_im.tobytes()
    floor = int(thresholds["channel_noise_floor"])
    diff_pixels = 0
    sum_abs = 0
    # Grid-based region localization (32x32 tiles) for fast bounding boxes
    tile_sz = 32
    cols = (w + tile_sz - 1) // tile_sz
    rows = (h + tile_sz - 1) // tile_sz
    dirty_tiles: set[tuple[int, int]] = set()

    for idx in range(total_pixels):
        off = idx * 3
        dr = raw[off]
        dg = raw[off + 1]
        db = raw[off + 2]
        m = dr if dr >= dg else dg
        if db > m:
            m = db
        sum_abs += (dr + dg + db)
        if m > floor:
            diff_pixels += 1
            x = idx % w
            y = idx // w
            dirty_tiles.add((x // tile_sz, y // tile_sz))

    diff_pct = round(100.0 * diff_pixels / total_pixels, 4) if total_pixels else 0.0
    mae = round(sum_abs / (total_pixels * 3.0), 4) if total_pixels else 0.0

    # Merge dirty tiles into bounding boxes via BFS
    regions: list[list[int]] = []
    visited: set[tuple[int, int]] = set()
    for tile in sorted(dirty_tiles):
        if tile in visited:
            continue
        queue = [tile]
        visited.add(tile)
        min_tx = max_tx = tile[0]
        min_ty = max_ty = tile[1]
        while queue:
            tx, ty = queue.pop()
            min_tx = min(min_tx, tx)
            max_tx = max(max_tx, tx)
            min_ty = min(min_ty, ty)
            max_ty = max(max_ty, ty)
            for nx, ny in ((tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)):
                if (nx, ny) in dirty_tiles and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        regions.append([
            min_tx * tile_sz,
            min_ty * tile_sz,
            min(w, (max_tx + 1) * tile_sz),
            min(h, (max_ty + 1) * tile_sz),
        ])

    if diff_pixels == 0 and sum_abs == 0:
        verdict = "MATCH"
        human_review = False
    elif diff_pct <= float(thresholds["max_diff_pct"]) and mae <= float(thresholds["max_mae"]):
        verdict = "NOISE"
        human_review = False
    else:
        verdict = "REGRESSION"
        human_review = True

    return {
        "verdict": verdict,
        "diff_pct": diff_pct,
        "mae": mae,
        "diff_pixels": diff_pixels,
        "total_pixels": total_pixels,
        "regions": regions[:20],
        "region_count": len(regions),
        "human_review": human_review,
    }


def run_calibration(repo_root: Path, work_dir: Path) -> dict[str, Any]:
    html_path = repo_root / "output" / "simulator.html"
    p1 = work_dir / "calib_run1.png"
    p2 = work_dir / "calib_run2.png"
    p_dark = work_dir / "calib_dark.png"

    r1 = run_lite_shot(html_path, p1, width=1280, height=800, theme="light", anchor="sakums", mode="screen")
    r2 = run_lite_shot(html_path, p2, width=1280, height=800, theme="light", anchor="sakums", mode="screen")
    r_dark = run_lite_shot(html_path, p_dark, width=1280, height=800, theme="dark", anchor="sakums", mode="screen")

    cmp_res = compare_images(p1, p2, DEFAULT_THRESHOLDS)
    return {
        "fixture_id": "FIX-VM-SMOKE-CALIBRATION",
        "status": "PASS" if cmp_res["verdict"] in ("MATCH", "NOISE") else "FAIL",
        "run1_sha256": r1["png_sha256"],
        "run2_sha256": r2["png_sha256"],
        "comparison": cmp_res,
        "calibrated_thresholds": DEFAULT_THRESHOLDS,
        "theme_toggle_check": {
            "light_dark_flag": r1["telemetry"].get("probe", {}).get("dark"),
            "dark_dark_flag": r_dark["telemetry"].get("probe", {}).get("dark"),
            "status": "PASS" if (r1["telemetry"].get("probe", {}).get("dark") is False and r_dark["telemetry"].get("probe", {}).get("dark") is True) else "FAIL",
        },
    }


def run_fixtures(repo_root: Path, matrix: dict[str, Any], baseline_dir: Path, work_dir: Path) -> dict[str, Any]:
    results: dict[str, Any] = {}

    # 1. Dangling cell fixture (A.1.1)
    bad_matrix = json.loads(json.dumps(matrix))
    bad_matrix["cells"].append({
        "cell_id": "fresh__neeksistejoss_skats__1280__light__screen",
        "render_key": "neeksistejoss_skats__1280__light__screen",
        "profile": "fresh",
        "view": "nonexistent_view",
        "anchor": "neeksistejoss_skats",
        "breakpoint": 1280,
        "viewport": {"width": 1280, "height": 800},
        "theme": "light",
        "mode": "screen",
    })
    dangling_errs = validate_matrix_definition(bad_matrix, repo_root)
    results["FIX-VM-DANGLING-CELL"] = {
        "detected": any("fresh__neeksistejoss_skats__1280__light__screen" in e for e in dangling_errs),
        "errors": dangling_errs,
        "status": "PASS" if dangling_errs else "FAIL",
    }

    # 2. Never-ready blank page timeout fixture (A.1.2)
    blank_html = work_dir / "never_ready_blank.html"
    blank_html.write_text("<!doctype html><html lang='lv'><body></body></html>", encoding="utf-8")
    blank_png = work_dir / "never_ready_blank.png"
    never_ready_detected = False
    never_ready_err = ""
    try:
        run_lite_shot(blank_html, blank_png, width=320, height=240, theme="light", wait_sec=2, min_colors=16)
    except RuntimeError as exc:
        never_ready_detected = True
        never_ready_err = str(exc)
    results["FIX-VM-NEVER-READY"] = {
        "detected": never_ready_detected,
        "error": never_ready_err,
        "status": "PASS" if never_ready_detected else "FAIL",
    }

    # 3. Planted overlap defect fixture (B.1.2)
    base_png = baseline_dir / "sakums__1280__light__screen.png"
    if not base_png.exists():
        raise FileNotFoundError(f"Baseline PNG missing for overlap fixture: {base_png}")

    sim_src = (repo_root / "output" / "simulator.html").read_text(encoding="utf-8")
    overlap_css = (
        "<style id='n37-planted-overlap'>"
        "#sakums .sim-card, #sakums .card, #sakums h1 { "
        "margin-top: -120px !important; background: #ff00ff !important; "
        "outline: 12px solid #ff0000 !important; }"
        "</style></head>"
    )
    overlap_html = work_dir / "planted_overlap.html"
    overlap_html.write_text(sim_src.replace("</head>", overlap_css, 1), encoding="utf-8")
    overlap_png = work_dir / "planted_overlap.png"
    run_lite_shot(overlap_html, overlap_png, width=1280, height=800, theme="light", anchor="sakums", mode="screen")
    overlap_cmp = compare_images(base_png, overlap_png, matrix["thresholds"])
    results["FIX-VM-PLANTED-OVERLAP"] = {
        "cell": "fresh__sakums__1280__light__screen",
        "detected": overlap_cmp["verdict"] == "REGRESSION" and len(overlap_cmp["regions"]) > 0,
        "comparison": overlap_cmp,
        "status": "PASS" if overlap_cmp["verdict"] == "REGRESSION" else "FAIL",
    }

    # 4. Planted 1px AA noise jitter fixture (B.1.2)
    noise_png = work_dir / "planted_noise.png"
    im = Image.open(base_png).convert("RGB")
    px = im.load()
    for y in range(20, 40):
        r, g, b = px[40, y]
        px[40, y] = (max(0, r - 2), max(0, g - 2), max(0, b - 2))
    im.save(noise_png)
    noise_cmp = compare_images(base_png, noise_png, matrix["thresholds"])
    results["FIX-VM-PLANTED-NOISE"] = {
        "cell": "fresh__sakums__1280__light__screen",
        "classified_as_noise": noise_cmp["verdict"] == "NOISE",
        "comparison": noise_cmp,
        "status": "PASS" if noise_cmp["verdict"] == "NOISE" else "FAIL",
    }

    return results


def freeze_baselines(repo_root: Path, matrix: dict[str, Any], baseline_dir: Path, reason: str) -> dict[str, Any]:
    html_path = repo_root / "output" / "simulator.html"
    manifest_path = repo_root / "output" / "build-manifest.json"
    artifact_digest = sha256_file(html_path)
    build_manifest_digest = sha256_file(manifest_path) if manifest_path.exists() else None

    baseline_dir.mkdir(parents=True, exist_ok=True)
    renders: dict[str, Any] = {}
    for spec in matrix["unique_renders"]:
        rk = spec["render_key"]
        out_png = baseline_dir / f"{rk}.png"
        res = run_lite_shot(
            html_path,
            out_png,
            width=spec["viewport"]["width"],
            height=spec["viewport"]["height"],
            theme=spec["theme"],
            anchor=spec["anchor"],
            mode=spec["mode"],
        )
        renders[rk] = {
            "render_key": rk,
            "png_relpath": f"evidence/visual_baselines/{rk}.png",
            "png_sha256": res["png_sha256"],
            "bytes": res["bytes"],
            "elapsed_s": res["elapsed_s"],
            "capture_params": spec,
            "overflow": res["telemetry"].get("viewport", {}).get("overflow"),
            "media_print": res["telemetry"].get("probe", {}).get("mediaPrint"),
        }

    baseline_manifest = {
        "schema_version": 1,
        "task": "N37",
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "artifact_path": "output/simulator.html",
        "artifact_digest": artifact_digest,
        "build_manifest_digest": build_manifest_digest,
        "render_count": len(renders),
        "renders": renders,
        "update_history": [],
    }
    baseline_manifest["composite_digest"] = sha256_json(
        {k: v["png_sha256"] for k, v in sorted(renders.items())}
    )
    save_json(baseline_dir / "baseline_manifest.json", baseline_manifest)
    return baseline_manifest


def update_baseline_entry(repo_root: Path, baseline_dir: Path, render_key: str, reason: str) -> dict[str, Any]:
    manifest_file = baseline_dir / "baseline_manifest.json"
    manifest = load_json(manifest_file)
    if render_key not in manifest["renders"]:
        raise KeyError(f"Unknown render_key: {render_key}")
    old_entry = manifest["renders"][render_key]
    old_sha = old_entry["png_sha256"]
    spec = old_entry["capture_params"]
    out_png = baseline_dir / f"{render_key}.png"
    res = run_lite_shot(
        repo_root / "output" / "simulator.html",
        out_png,
        width=spec["viewport"]["width"],
        height=spec["viewport"]["height"],
        theme=spec["theme"],
        anchor=spec["anchor"],
        mode=spec["mode"],
    )
    manifest["version"] = int(manifest.get("version", 1)) + 1
    manifest["update_history"].append({
        "version": manifest["version"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "render_key": render_key,
        "previous_sha256": old_sha,
        "new_sha256": res["png_sha256"],
        "reason": reason,
    })
    old_entry["png_sha256"] = res["png_sha256"]
    old_entry["bytes"] = res["bytes"]
    manifest["composite_digest"] = sha256_json(
        {k: v["png_sha256"] for k, v in sorted(manifest["renders"].items())}
    )
    save_json(manifest_file, manifest)
    return manifest


def compare_matrix(repo_root: Path, matrix: dict[str, Any], baseline_dir: Path, work_dir: Path) -> dict[str, Any]:
    html_path = repo_root / "output" / "simulator.html"
    artifact_digest = sha256_file(html_path)
    baseline_manifest = load_json(baseline_dir / "baseline_manifest.json")

    if baseline_manifest["artifact_digest"] != artifact_digest:
        raise RuntimeError(
            f"Artifact digest mismatch: baseline={baseline_manifest['artifact_digest']} "
            f"current={artifact_digest}. Refusing silent comparison."
        )

    render_results: dict[str, dict[str, Any]] = {}
    for spec in matrix["unique_renders"]:
        rk = spec["render_key"]
        base_png = baseline_dir / f"{rk}.png"
        cur_png = work_dir / f"{rk}.png"
        cap = run_lite_shot(
            html_path,
            cur_png,
            width=spec["viewport"]["width"],
            height=spec["viewport"]["height"],
            theme=spec["theme"],
            anchor=spec["anchor"],
            mode=spec["mode"],
        )
        cmp_res = compare_images(base_png, cur_png, matrix["thresholds"])
        render_results[rk] = {
            "render_key": rk,
            "current_sha256": cap["png_sha256"],
            "baseline_sha256": baseline_manifest["renders"][rk]["png_sha256"],
            "elapsed_s": cap["elapsed_s"],
            **cmp_res,
        }

    cell_verdicts: list[dict[str, Any]] = []
    counts = {"MATCH": 0, "NOISE": 0, "REGRESSION": 0}
    failing_cells: list[dict[str, Any]] = []
    for cell in matrix["cells"]:
        rr = render_results[cell["render_key"]]
        v = rr["verdict"]
        counts[v] = counts.get(v, 0) + 1
        entry = {
            "cell_id": cell["cell_id"],
            "render_key": cell["render_key"],
            "verdict": v,
            "diff_pct": rr["diff_pct"],
            "mae": rr["mae"],
            "regions": rr["regions"],
            "human_review": rr["human_review"],
        }
        cell_verdicts.append(entry)
        if v == "REGRESSION":
            failing_cells.append(entry)

    verdict_sequence = [c["verdict"] for c in cell_verdicts]
    verdict_sequence_sha256 = sha256_json(verdict_sequence)
    status = "PASS" if counts["REGRESSION"] == 0 else "FAIL"

    return {
        "schema_version": 1,
        "task": "N37",
        "epistemic_header": {
            **EPISTEMIC_HEADER,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "artifact_digest": artifact_digest,
        },
        "baseline_composite_digest": baseline_manifest["composite_digest"],
        "baseline_version": baseline_manifest["version"],
        "thresholds": matrix["thresholds"],
        "status": status,
        "summary": {
            "total_cells": len(cell_verdicts),
            "unique_renders": len(render_results),
            **counts,
        },
        "verdict_sequence_sha256": verdict_sequence_sha256,
        "failing_cells": failing_cells,
        "render_results": render_results,
        "cell_verdicts": cell_verdicts,
        "n39_registration": N39_REGISTRATION,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="N37 Visual Regression Matrix Harness (lite-shot + Falkon)")
    ap.add_argument("--repo-root", default=str(REPO_ROOT))
    ap.add_argument("--matrix", default="data/visual_matrix.json")
    ap.add_argument("--baseline-dir", default="evidence/visual_baselines")
    ap.add_argument("--generate-matrix", action="store_true")
    ap.add_argument("--validate-matrix", action="store_true")
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--freeze-baselines", action="store_true")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--render-key", default=None)
    ap.add_argument("--reason", default="N37 initial baseline freeze")
    ap.add_argument("--run-fixtures", action="store_true")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--replay-proof", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    repo_root = Path(args.repo_root).resolve()
    matrix_path = repo_root / args.matrix
    baseline_dir = repo_root / args.baseline_dir

    if args.generate_matrix:
        matrix = build_matrix_definition(repo_root)
        save_json(matrix_path, matrix)
        print(f"GENERATED {matrix_path}: cells={matrix['cell_count']} unique_renders={matrix['unique_render_count']}")

    matrix = load_json(matrix_path)

    if args.validate_matrix:
        errs = validate_matrix_definition(matrix, repo_root)
        if errs:
            print("FAIL matrix validation:", errs, file=sys.stderr)
            return 1
        print(f"PASS matrix validation: {matrix['cell_count']} cells, {matrix['unique_render_count']} unique renders")

    if args.freeze_baselines:
        bm = freeze_baselines(repo_root, matrix, baseline_dir, args.reason)
        print(f"FROZEN baselines: renders={bm['render_count']} composite_digest={bm['composite_digest']}")

    if args.update_baseline:
        if not args.render_key:
            print("FAIL --update-baseline requires --render-key", file=sys.stderr)
            return 2
        bm = update_baseline_entry(repo_root, baseline_dir, args.render_key, args.reason)
        print(f"UPDATED baseline {args.render_key}: version={bm['version']} composite_digest={bm['composite_digest']}")

    with tempfile.TemporaryDirectory(prefix="n37_vis_") as tmp:
        work_dir = Path(tmp)
        report: dict[str, Any] = {}

        if args.calibrate:
            calib = run_calibration(repo_root, work_dir)
            report["calibration"] = calib
            print(f"CALIBRATION {calib['status']}: {calib['comparison']['verdict']} (diff_pct={calib['comparison']['diff_pct']}%)")
            if calib["status"] != "PASS":
                return 1

        if args.run_fixtures:
            fix = run_fixtures(repo_root, matrix, baseline_dir, work_dir)
            report["fixtures"] = fix
            for k, v in fix.items():
                print(f"FIXTURE {k}: {v['status']}")
                if v["status"] != "PASS":
                    return 1

        if args.compare:
            cmp_rep = compare_matrix(repo_root, matrix, baseline_dir, work_dir)
            report["matrix_report"] = cmp_rep
            s = cmp_rep["summary"]
            print(
                f"{cmp_rep['status']} N37 visual matrix: total={s['total_cells']} "
                f"MATCH={s['MATCH']} NOISE={s['NOISE']} REGRESSION={s['REGRESSION']} "
                f"verdict_sha256={cmp_rep['verdict_sequence_sha256'][:16]}..."
            )
            if args.out and not args.calibrate and not args.run_fixtures:
                save_json(repo_root / args.out, cmp_rep)
            elif args.out:
                save_json(repo_root / args.out, report)
            if cmp_rep["status"] != "PASS":
                return 1
        elif args.out and report:
            save_json(repo_root / args.out, report)

    if args.replay_proof:
        r1_path = repo_root / "evidence" / "N37_REPLAY_RUN1.json"
        r2_path = repo_root / "evidence" / "N37_REPLAY_RUN2.json"
        for idx, rpath in ((1, r1_path), (2, r2_path)):
            p = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "--repo-root", str(repo_root),
                    "--compare",
                    "--out", str(rpath.relative_to(repo_root)),
                ],
                capture_output=True,
                text=True,
            )
            if p.returncode != 0:
                print(f"FAIL replay run {idx}: {p.stderr}\n{p.stdout}", file=sys.stderr)
                return 1
        d1 = load_json(r1_path)
        d2 = load_json(r2_path)
        identical = d1["verdict_sequence_sha256"] == d2["verdict_sequence_sha256"]
        proof = {
            "schema_version": 1,
            "task": "N37",
            "status": "PASS" if identical else "FAIL",
            "identical_verdicts": identical,
            "artifact_digest": d1["epistemic_header"]["artifact_digest"],
            "run1_verdict_sequence_sha256": d1["verdict_sequence_sha256"],
            "run2_verdict_sequence_sha256": d2["verdict_sequence_sha256"],
            "run1_summary": d1["summary"],
            "run2_summary": d2["summary"],
        }
        save_json(repo_root / "evidence" / "N37_REPLAY_PROOF.json", proof)
        print(f"REPLAY_PROOF {proof['status']}: identical_verdicts={identical} sha256={d1['verdict_sequence_sha256'][:16]}...")
        if not identical:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
