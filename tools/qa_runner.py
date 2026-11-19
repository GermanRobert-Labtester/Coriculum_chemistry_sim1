#!/usr/bin/env python3
"""N39 Reproducible QA Runner & SHA-256 Evidence Chain (tools/qa_runner.py).

Single-command local offline QA orchestrator for the RSU First Colloquium
Chemistry Simulator (`output/simulator.html`).

Core guarantees:
  - Offline & read-only on repository sources (never edits sources or auto-fixes).
  - Pre-flight suite registry integrity check against ledger-sourced SHA-256
    digests (missing or stale/tampered suite fails by name before execution).
  - Pre-flight source tamper check against build-manifest.json digests (any
    tampered source refuses the run by name before any suite runs).
  - Tiered 5-tier execution loop in fresh per-suite isolated environments
    (TMPDIR / XDG_*), with per-suite timeouts (mark TIMEOUT and continue) and
    continue-on-failure visibility.
  - No partial-run green: any skipped, failed, or timed-out suite produces
    overall_verdict="FAIL" and a non-zero exit code.
  - Two-pass JSON trailer manifest write resolving self-digest reference while
    remaining valid RFC 8259 JSON and externally recomputable.
  - Versioned registry update command (`--update-suite ... --reason ...`) so
    no quiet digest edits occur anywhere.
  - Completeness cross-check against `evidence/VERIFICATION_LEDGER.md` and
    frozen release evidence pack generation for N40's ten-point release gate.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = "data/qa_registry.json"
DEFAULT_SCHEMA = "data/qa_manifest_schema.json"
DEFAULT_MANIFEST_OUT = "evidence/N39_QA_MANIFEST.json"
DEFAULT_PACK_OUT = "evidence/N39_EVIDENCE_PACK.json"
DEFAULT_LEDGER = "evidence/VERIFICATION_LEDGER.md"

TWO_PASS_RECOMPUTE_RULE = (
    "Remove the trailing 'manifest_trailer' property (from ',\\n  \"manifest_trailer\":' to EOF), "
    "restore '\\n}\\n', and compute SHA-256 of the resulting UTF-8 bytes; equivalently, parse JSON, "
    "drop top-level key 'manifest_trailer', serialize with sort_keys=True, indent=2, "
    "ensure_ascii=False + '\\n', and compute SHA-256."
)

NORMALIZATION_RULE = {
    "included_fields": ["suite_id", "tier", "verdict", "exit_code", "timed_out"],
    "excluded_fields": [
        "duration_ms",
        "started_utc",
        "finished_utc",
        "run_id",
        "sequence_number",
        "stdout_path",
        "stderr_path",
        "report_path",
    ],
    "statement": (
        "Normalized verdict vector preserves suite_id in declared registry order, tier, "
        "verdict, exit_code, and timed_out. Timing/run metadata (duration_ms, timestamps, "
        "run_id, sequence_number, per-run log file paths) are excluded by design because "
        "execution wall-times vary legitimately across identical runs."
    ),
}

# Explicit N38 honest UNVERIFIED items & workspace-level open items carried to N40
EXPLICIT_OPEN_ITEMS: list[dict[str, str]] = [
    {
        "id": "OPEN-N38-01",
        "source_task": "N38",
        "epistemic_label": "UNVERIFIED",
        "item": "NVDA (Windows) screen-reader speech/braille announcements (N33)",
        "owner": "N40 release gate / future Windows accessibility tester",
        "reason": "Offline Linux headless Xvfb environment lacks Windows/NVDA.",
    },
    {
        "id": "OPEN-N38-02",
        "source_task": "N38",
        "epistemic_label": "UNVERIFIED",
        "item": "VoiceOver (macOS) screen-reader speech/braille announcements (N33)",
        "owner": "N40 release gate / future macOS accessibility tester",
        "reason": "Offline Linux headless Xvfb environment lacks macOS/VoiceOver.",
    },
    {
        "id": "OPEN-N38-03",
        "source_task": "N38",
        "epistemic_label": "UNVERIFIED",
        "item": "Orca / AT-SPI live speech output in headless Xvfb (N33)",
        "owner": "N40 release gate / desktop Linux accessibility tester",
        "reason": "Live speech output is unavailable under headless Xvfb.",
    },
    {
        "id": "OPEN-N38-04",
        "source_task": "N38",
        "epistemic_label": "UNVERIFIED",
        "item": "Scenario 3.6 real-time timer threshold alert firing (N33)",
        "owner": "N40 release gate / manual exam timing tester",
        "reason": "Full 180-minute real-time wait not simulated in live browser smoke.",
    },
    {
        "id": "OPEN-N38-05",
        "source_task": "N38",
        "epistemic_label": "UNVERIFIED",
        "item": "Scenario 4.3 completed self-assessment toggle in fresh session (N33)",
        "owner": "N40 release gate / manual revision workflow tester",
        "reason": "Fresh in-memory session has no pre-completed self-assessment entries.",
    },
    {
        "id": "OPEN-N38-06",
        "source_task": "N38",
        "epistemic_label": "UNAVAILABLE",
        "item": "Chrome/Chromium rendering and interaction (explicitly forbidden by AGENTS.md without authorization)",
        "owner": "N40 release gate / repository governance owner",
        "reason": "AGENTS.md forbids Chrome/Chromium without explicit user authorization.",
    },
    {
        "id": "OPEN-N38-07",
        "source_task": "N38",
        "epistemic_label": "UNAVAILABLE",
        "item": "Firefox rendering and interaction (UNAVAILABLE in environment)",
        "owner": "N40 release gate / multi-browser release tester",
        "reason": "Firefox is not installed in the offline verification environment.",
    },
    {
        "id": "OPEN-N38-08",
        "source_task": "N38",
        "epistemic_label": "UNAVAILABLE",
        "item": "Safari/WebKit rendering and interaction (UNAVAILABLE in environment)",
        "owner": "N40 release gate / macOS browser tester",
        "reason": "Safari/WebKit is not present on Linux.",
    },
    {
        "id": "OPEN-N38-09",
        "source_task": "N38",
        "epistemic_label": "UNAVAILABLE",
        "item": "Physical printer paper output (UNAVAILABLE in environment)",
        "owner": "N40 release gate / instructor paper-rehearsal reviewer",
        "reason": "No physical printer hardware attached; print CSS verified engine-side in Falkon only.",
    },
    {
        "id": "OPEN-N01-V01",
        "source_task": "N01",
        "epistemic_label": "DOCUMENTED BUT NOT RERUN",
        "item": "Full-workspace sibling Chemistry_1..7 mode of verify_preparation.py (evidence/PREPARATION_VERIFICATION.json)",
        "owner": "N40 release gate / repository maintainer",
        "reason": "Published repository excludes external sibling Chemistry_1..7 directories; repository-local mode PASS is verified.",
    },
    {
        "id": "OPEN-N03-V08",
        "source_task": "N03",
        "epistemic_label": "UNDETERMINED",
        "item": "Catalase K10/K17 activation energy and induced-reaction scientific ambiguity (V-08 / C05)",
        "owner": "RSU course lecturer / N40 conflict ledger closure",
        "reason": "Inherited scientific uncertainty from course sources; carried openly without asserting a disputed single key.",
    },
    {
        "id": "OPEN-N09-GAP",
        "source_task": "N09",
        "epistemic_label": "UNAVAILABLE",
        "item": "Standalone N09 misconception registry task not implemented in workspace (recorded dependency gap in N17, N19, N23)",
        "owner": "N40 release gate / future misconception-registry authoring",
        "reason": "N17/N19/N23 use N04 stub signatures validated against frozen N05 vectors and explicitly flag N09 for future re-check.",
    },
    {
        "id": "OPEN-F08-DEFERRED",
        "source_task": "N27",
        "epistemic_label": "PROPOSED",
        "item": "Predecessor feature F08 (adaptive difficulty) DEFERRED per roadmap Section 4.3",
        "owner": "N40 conflict ledger closure",
        "reason": "Deferred until N26-N27 mastery and Leitner scheduler stabilize.",
    },
    {
        "id": "OPEN-F10-REJECTED",
        "source_task": "N25",
        "epistemic_label": "PROPOSED",
        "item": "Predecessor feature F10 (analytics dashboards / gamification) REJECTED per roadmap Section 4.3",
        "owner": "N25 / N40 release gate",
        "reason": "Rejected by privacy/honesty policy; enforced by SimAnalytics.F10_BOUNDARY and Gate 21.",
    },
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_compact_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_pretty_json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def write_manifest_two_pass(manifest_body: dict[str, Any], out_path: Path) -> dict[str, Any]:
    """Subtask A.1.3: Two-pass JSON trailer write resolving self-digest reference.

    Pass 1: Write canonical pretty JSON of manifest_body (without manifest_trailer)
            to disk and compute SHA-256 of the written UTF-8 bytes.
    Pass 2: Append the 'manifest_trailer' property directly before the final
            closing brace so the file stays valid RFC 8259 JSON and the Pass-1
            body bytes are trivially recoverable via raw byte-slicing or JSON parse.
    """
    body_clean = {k: v for k, v in manifest_body.items() if k != "manifest_trailer"}
    body_bytes = canonical_pretty_json_bytes(body_clean)
    if not body_bytes.endswith(b"\n}\n"):
        raise RuntimeError("Canonical manifest body must end with '\\n}\\n'")

    # Pass 1: write body to disk and hash the written bytes from disk
    atomic_write_bytes(out_path, body_bytes)
    disk_body_bytes = out_path.read_bytes()
    body_sha256 = sha256_bytes(disk_body_bytes)

    trailer_obj = {
        "algorithm": "sha256",
        "format": "two-pass-json-trailer-v1",
        "body_bytes": len(disk_body_bytes),
        "body_sha256": body_sha256,
        "recompute_rule": TWO_PASS_RECOMPUTE_RULE,
    }
    trailer_json = json.dumps(trailer_obj, sort_keys=True, indent=2, ensure_ascii=False)
    indented_trailer = trailer_json.replace("\n", "\n  ")
    trailer_snippet = f',\n  "manifest_trailer": {indented_trailer}\n}}\n'.encode("utf-8")

    # Pass 2: append trailer replacing the final '\n}\n' (3 bytes)
    final_bytes = disk_body_bytes[:-3] + trailer_snippet
    atomic_write_bytes(out_path, final_bytes)

    return {
        "path": str(out_path),
        "body_bytes": len(disk_body_bytes),
        "body_sha256": body_sha256,
        "final_bytes": len(final_bytes),
        "final_file_sha256": sha256_bytes(final_bytes),
        "trailer": trailer_obj,
    }


def _cmd_version(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        out = (p.stdout or p.stderr or "").strip().splitlines()
        return out[0].strip() if out else f"exit={p.returncode}"
    except Exception as exc:
        return f"UNAVAILABLE ({exc})"


def collect_environment() -> dict[str, str]:
    lite_shot = shutil.which("lite-shot") or "UNAVAILABLE"
    return {
        "python_version": platform.python_version(),
        "node_version": _cmd_version(["node", "--version"]),
        "falkon_version": _cmd_version(["falkon", "--version"]),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "lite_shot_path": lite_shot,
    }


def validate_registry(
    repo_root: Path,
    registry: dict[str, Any],
    *,
    check_ledger: bool = True,
) -> dict[str, Any]:
    """Subtask A.1 / A.1.1: Validate every registered suite resolves and matches
    its ledger-sourced SHA-256 digest. Any missing or altered file fails by name.
    """
    errors: list[str] = []
    entries: list[dict[str, Any]] = []

    ledger_text = ""
    ledger_rel = registry.get("ledger_path", DEFAULT_LEDGER)
    ledger_path = repo_root / ledger_rel
    if check_ledger:
        if not ledger_path.is_file():
            errors.append(f"E_LEDGER_MISSING: {ledger_rel}")
        else:
            ledger_text = ledger_path.read_text(encoding="utf-8")

    update_history = registry.get("update_history", [])
    versioned_paths_new_shas: dict[str, set[str]] = {}
    for ev in update_history:
        p_ev = ev.get("path")
        new_sha = ev.get("new_sha256")
        if p_ev and new_sha:
            versioned_paths_new_shas.setdefault(p_ev, set()).add(new_sha)

    suites = registry.get("suites", [])
    if not suites:
        errors.append("E_REGISTRY_EMPTY: registry contains zero suites")

    seen_ids: set[str] = set()
    prev_tier_order = 0
    for suite in suites:
        sid = suite.get("suite_id", "<missing-suite-id>")
        if sid in seen_ids:
            errors.append(f"E_DUPLICATE_SUITE_ID: {sid}")
        seen_ids.add(sid)

        t_order = int(suite.get("tier_order", 0))
        if t_order < prev_tier_order:
            errors.append(
                f"E_TIER_ORDER_VIOLATION: suite {sid} tier_order={t_order} precedes previous tier_order={prev_tier_order}"
            )
        prev_tier_order = t_order

        if not suite.get("invocation"):
            errors.append(f"E_EMPTY_INVOCATION: suite {sid} has empty invocation")
        if float(suite.get("timeout_seconds", 0)) <= 0:
            errors.append(f"E_INVALID_TIMEOUT: suite {sid} timeout_seconds must be > 0")

        sfiles = suite.get("files", [])
        if not sfiles:
            errors.append(f"E_NO_SUITE_FILES: suite {sid} declares no files for integrity checking")

        for fspec in sfiles:
            rel = fspec.get("path", "<missing-path>")
            expected = fspec.get("expected_sha256", "")
            fpath = repo_root / rel
            if not fpath.is_file():
                errors.append(f"E_SUITE_FILE_MISSING: suite={sid} path={rel}")
                entries.append({
                    "suite_id": sid,
                    "path": rel,
                    "bytes": 0,
                    "sha256": "0" * 64,
                    "expected_sha256": expected,
                    "matched": False,
                    "error": "missing",
                })
                continue

            actual_sha = sha256_file(fpath)
            actual_bytes = fpath.stat().st_size
            matched = actual_sha == expected
            if not matched:
                errors.append(
                    f"E_SUITE_DIGEST_MISMATCH: suite={sid} path={rel} "
                    f"expected={expected} actual={actual_sha}"
                )

            # Verify expected digest traces either to VERIFICATION_LEDGER.md or an
            # explicit versioned update_history event (A.1.1 no quiet edits rule)
            if check_ledger and ledger_text:
                in_ledger = (expected in ledger_text) or (expected[:16] in ledger_text)
                in_history = expected in versioned_paths_new_shas.get(rel, set())
                if not in_ledger and not in_history:
                    errors.append(
                        f"E_SUITE_UNRECORDED_IN_LEDGER: suite={sid} path={rel} "
                        f"digest={expected[:16]}... absent from {ledger_rel} and update_history"
                    )

            entries.append({
                "suite_id": sid,
                "path": rel,
                "bytes": actual_bytes,
                "sha256": actual_sha,
                "expected_sha256": expected,
                "matched": matched,
            })

    # Verify ledger-expected artifact digest is present in ledger (or update_history)
    expected_art = registry.get("artifact_expected_sha256", "")
    if check_ledger and ledger_text and expected_art:
        art_in_ledger = (expected_art in ledger_text) or (expected_art[:16] in ledger_text)
        art_in_history = expected_art in versioned_paths_new_shas.get(
            registry.get("artifact_path", "output/simulator.html"), set()
        )
        if not art_in_ledger and not art_in_history:
            errors.append(
                f"E_ARTIFACT_DIGEST_UNRECORDED: {expected_art[:16]}... absent from {ledger_rel}"
            )

    composite = sha256_bytes(
        canonical_compact_json_bytes([
            {"suite_id": e["suite_id"], "path": e["path"], "sha256": e["sha256"]}
            for e in entries
        ])
    )
    return {
        "status": "PASS" if not errors else "FAIL",
        "suite_count": len(suites),
        "file_count": len(entries),
        "errors": errors,
        "entries": entries,
        "suites_composite_sha256": composite,
    }


def check_source_integrity(repo_root: Path, registry: dict[str, Any]) -> dict[str, Any]:
    """Subtask B.1.2: Check every build source file against the recorded baseline
    digests (from output/build-manifest.json and registry) BEFORE any suite runs.
    """
    errors: list[str] = []
    manifest_rel = registry.get("build_manifest_path", "output/build-manifest.json")
    manifest_path = repo_root / manifest_rel
    if not manifest_path.is_file():
        return {
            "status": "FAIL",
            "errors": [f"E_BUILD_MANIFEST_MISSING: {manifest_rel}"],
            "sources": [],
            "sources_composite_sha256": "0" * 64,
        }

    bm_sha = sha256_file(manifest_path)
    expected_bm_sha = registry.get("build_manifest_expected_sha256")
    if expected_bm_sha and bm_sha != expected_bm_sha:
        errors.append(
            f"E_BUILD_MANIFEST_TAMPERED: path={manifest_rel} "
            f"expected={expected_bm_sha} actual={bm_sha}"
        )

    bm = load_json(manifest_path)
    recorded_sources = bm.get("sources", [])
    if not recorded_sources:
        errors.append(f"E_BUILD_MANIFEST_NO_SOURCES: {manifest_rel} lists zero sources")

    checked_sources: list[dict[str, Any]] = []
    for src in sorted(recorded_sources, key=lambda x: x["path"]):
        rel = src["path"]
        exp_sha = src["sha256"]
        fpath = repo_root / rel
        if not fpath.is_file():
            errors.append(f"E_SOURCE_MISSING: {rel}")
            checked_sources.append({"path": rel, "bytes": 0, "sha256": "0" * 64})
            continue
        actual_sha = sha256_file(fpath)
        actual_bytes = fpath.stat().st_size
        if actual_sha != exp_sha:
            errors.append(
                f"E_SOURCE_TAMPERED: path={rel} expected={exp_sha} actual={actual_sha}"
            )
        checked_sources.append({"path": rel, "bytes": actual_bytes, "sha256": actual_sha})

    # Also check pre-build artifact digest against ledger-expected digest
    art_rel = registry.get("artifact_path", "output/simulator.html")
    art_path = repo_root / art_rel
    exp_art = registry.get("artifact_expected_sha256")
    if not art_path.is_file():
        errors.append(f"E_ARTIFACT_MISSING: {art_rel}")
    elif exp_art:
        actual_art = sha256_file(art_path)
        if actual_art != exp_art:
            errors.append(
                f"E_ARTIFACT_PREFLIGHT_MISMATCH: path={art_rel} expected={exp_art} actual={actual_art}"
            )

    sources_composite = sha256_bytes(canonical_compact_json_bytes(checked_sources))
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "sources": checked_sources,
        "sources_composite_sha256": sources_composite,
        "build_manifest_sha256": bm_sha,
        "build_manifest_bytes": manifest_path.stat().st_size,
        "build_manifest_data": bm,
    }


def update_registry_suite(
    repo_root: Path,
    registry_path: Path,
    suite_id: str,
    rel_file: str,
    reason: str,
) -> dict[str, Any]:
    """Subtask A.1.1: Versioned registry update (mirroring N37 baseline rule)."""
    if not reason or not reason.strip():
        raise ValueError("E_UPDATE_REASON_REQUIRED: --reason must be a non-empty explanation")
    reg = load_json(registry_path)
    target_suite = None
    for s in reg.get("suites", []):
        if s.get("suite_id") == suite_id:
            target_suite = s
            break
    if target_suite is None:
        raise KeyError(f"E_UNKNOWN_SUITE_ID: {suite_id}")

    target_fspec = None
    for fspec in target_suite.get("files", []):
        if fspec.get("path") == rel_file:
            target_fspec = fspec
            break
    if target_fspec is None:
        raise KeyError(f"E_UNKNOWN_SUITE_FILE: suite={suite_id} path={rel_file}")

    fpath = repo_root / rel_file
    if not fpath.is_file():
        raise FileNotFoundError(f"E_FILE_NOT_FOUND: {rel_file}")

    old_sha = target_fspec["expected_sha256"]
    new_sha = sha256_file(fpath)
    new_bytes = fpath.stat().st_size
    new_ver = int(reg.get("registry_version", 1)) + 1

    event = {
        "version": new_ver,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "suite_file_digest_update",
        "suite_id": suite_id,
        "path": rel_file,
        "previous_sha256": old_sha,
        "new_sha256": new_sha,
        "bytes": new_bytes,
        "reason": reason.strip(),
    }
    reg["registry_version"] = new_ver
    target_fspec["expected_sha256"] = new_sha
    target_fspec["bytes"] = new_bytes
    reg.setdefault("update_history", []).append(event)
    atomic_write_bytes(registry_path, canonical_pretty_json_bytes(reg))
    return event


def _build_clean_suite_env(suite_tmp: Path) -> dict[str, str]:
    """Fresh per-suite environment isolating TMPDIR and XDG directories."""
    env = dict(os.environ)
    for sub, var in (
        ("tmp", "TMPDIR"),
        ("xdg_config", "XDG_CONFIG_HOME"),
        ("xdg_cache", "XDG_CACHE_HOME"),
        ("xdg_data", "XDG_DATA_HOME"),
    ):
        d = suite_tmp / sub
        d.mkdir(parents=True, exist_ok=True)
        env[var] = str(d)
    env["PYTHONNOUSERSITE"] = env.get("PYTHONNOUSERSITE", "0")
    return env


def _evaluate_suite_report(report_file: Path) -> tuple[bool, str | None]:
    """Inspect a suite's JSON report (if produced) to verify semantic pass status."""
    if not report_file.is_file():
        return False, f"expected report file missing: {report_file.name}"
    try:
        data = load_json(report_file)
    except Exception as exc:
        return False, f"invalid JSON report ({exc})"

    if isinstance(data, dict):
        if "status" in data:
            if str(data["status"]).upper() != "PASS":
                return False, f"report status={data['status']!r}"
        elif "pass" in data:
            if data["pass"] is not True:
                return False, f"report pass={data['pass']!r}"
        elif "ok" in data:
            if data["ok"] is not True:
                return False, f"report ok={data['ok']!r}"
    return True, None


def execute_suite(
    repo_root: Path,
    suite: dict[str, Any],
    run_dir: Path,
) -> dict[str, Any]:
    """Execute one suite in a fresh subprocess with isolated temp/XDG dirs and timeout."""
    sid = suite["suite_id"]
    timeout_s = float(suite["timeout_seconds"])
    expected_codes = [int(c) for c in suite.get("expected_exit_codes", [0])]
    report_name = suite.get("report_artifact")

    run_dir.mkdir(parents=True, exist_ok=True)
    stdout_file = run_dir / f"{sid}.stdout.txt"
    stderr_file = run_dir / f"{sid}.stderr.txt"
    report_file = (run_dir / report_name) if report_name else None

    cmd: list[str] = []
    for tok in suite["invocation"]:
        if tok == "{python}":
            cmd.append(sys.executable)
        elif tok == "{report_path}":
            if report_file is None:
                raise RuntimeError(f"Suite {sid} uses {{report_path}} without report_artifact")
            cmd.append(str(report_file))
        else:
            cmd.append(tok)

    timed_out = False
    exit_code: int | None = None
    failure_reason: str | None = None
    stdout_bytes = b""
    stderr_bytes = b""

    with tempfile.TemporaryDirectory(prefix=f"qa_suite_{sid}_") as stmp:
        env = _build_clean_suite_env(Path(stmp))
        t0 = time.monotonic()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(repo_root),
                env=env,
                capture_output=True,
                timeout=timeout_s,
            )
            duration_ms = round((time.monotonic() - t0) * 1000.0, 3)
            exit_code = int(proc.returncode)
            stdout_bytes = proc.stdout or b""
            stderr_bytes = proc.stderr or b""
        except subprocess.TimeoutExpired as exc:
            duration_ms = round((time.monotonic() - t0) * 1000.0, 3)
            timed_out = True
            exit_code = None
            stdout_bytes = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode("utf-8")
            stderr_bytes = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode("utf-8")
            failure_reason = f"E_SUITE_TIMEOUT: suite {sid} exceeded timeout of {timeout_s}s"

    stdout_file.write_bytes(stdout_bytes)
    stderr_file.write_bytes(stderr_bytes)
    stdout_sha = sha256_bytes(stdout_bytes)
    stderr_sha = sha256_bytes(stderr_bytes)

    report_sha: str | None = None
    report_rel: str | None = None
    if report_file is not None and report_file.is_file():
        report_sha = sha256_file(report_file)
        try:
            report_rel = str(report_file.relative_to(repo_root))
        except ValueError:
            report_rel = str(report_file)

    try:
        stdout_rel = str(stdout_file.relative_to(repo_root))
    except ValueError:
        stdout_rel = str(stdout_file)
    try:
        stderr_rel = str(stderr_file.relative_to(repo_root))
    except ValueError:
        stderr_rel = str(stderr_file)

    if timed_out:
        verdict = "TIMEOUT"
    elif exit_code not in expected_codes:
        verdict = "FAIL"
        failure_reason = f"E_SUITE_EXIT_CODE: suite {sid} exited with {exit_code} (expected {expected_codes})"
    else:
        if report_file is not None:
            rep_ok, rep_err = _evaluate_suite_report(report_file)
            if not rep_ok:
                verdict = "FAIL"
                failure_reason = f"E_SUITE_REPORT_FAIL: suite {sid} {rep_err}"
            else:
                verdict = "PASS"
        else:
            verdict = "PASS"

    output_digest = sha256_bytes(
        canonical_compact_json_bytes({
            "suite_id": sid,
            "exit_code": exit_code,
            "timed_out": timed_out,
            "stdout_sha256": stdout_sha,
            "stderr_sha256": stderr_sha,
            "report_sha256": report_sha,
        })
    )

    return {
        "suite_id": sid,
        "tier": suite["tier"],
        "tier_order": int(suite["tier_order"]),
        "owner_task": suite["owner_task"],
        "invocation": suite["invocation"],
        "expected_exit_codes": expected_codes,
        "timeout_seconds": timeout_s,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "verdict": verdict,
        "duration_ms": duration_ms,
        "stdout_path": stdout_rel,
        "stderr_path": stderr_rel,
        "stdout_sha256": stdout_sha,
        "stderr_sha256": stderr_sha,
        "report_path": report_rel,
        "report_sha256": report_sha,
        "output_digest": output_digest,
        "failure_reason": failure_reason,
    }


def run_qa(
    repo_root: Path,
    registry_path: Path,
    manifest_out: Path,
    *,
    run_seq: int = 1,
    run_dir: Path | None = None,
    check_ledger: bool = True,
    check_sources: bool = True,
    suite_ids_override: list[str] | None = None,
    verbose: bool = True,
) -> tuple[int, dict[str, Any]]:
    """Run the full QA orchestrator and write the two-pass SHA-256 manifest."""
    started_utc = datetime.now(timezone.utc).isoformat()
    registry = load_json(registry_path)
    registry_sha = sha256_file(registry_path)

    # Step 1: Pre-flight registry & suite digest validation
    reg_check = validate_registry(repo_root, registry, check_ledger=check_ledger)
    if reg_check["status"] != "PASS":
        if verbose:
            print("REFUSED (registry validation failed):", file=sys.stderr)
            for err in reg_check["errors"]:
                print(f"  - {err}", file=sys.stderr)
        return 2, {"refused": True, "stage": "registry_validation", "errors": reg_check["errors"]}

    # Step 2: Pre-flight source & artifact tamper detection (before any suite runs)
    if check_sources:
        src_check = check_source_integrity(repo_root, registry)
        if src_check["status"] != "PASS":
            if verbose:
                print("REFUSED (source/artifact tamper detected before execution):", file=sys.stderr)
                for err in src_check["errors"]:
                    print(f"  - {err}", file=sys.stderr)
            return 2, {"refused": True, "stage": "source_tamper_check", "errors": src_check["errors"]}
    else:
        src_check = {
            "status": "PASS",
            "errors": [],
            "sources": [{"path": "scratch", "bytes": 0, "sha256": "0" * 64}],
            "sources_composite_sha256": sha256_bytes(b"scratch"),
            "build_manifest_sha256": "0" * 64,
            "build_manifest_bytes": 1,
            "build_manifest_data": {"build_id": "scratch", "composite_digest": "0" * 64},
        }

    art_rel = registry.get("artifact_path", "output/simulator.html")
    art_path = repo_root / art_rel
    pre_art_sha = sha256_file(art_path) if art_path.is_file() else ("0" * 64)
    run_id = f"qa-{pre_art_sha[:12]}-seq{run_seq:04d}"

    if run_dir is None:
        run_dir = repo_root / "evidence" / "qa_runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    suites_all = registry["suites"]
    selected_set = set(suite_ids_override) if suite_ids_override is not None else None
    if suite_ids_override is not None:
        # Execute in requested order, then mark any omitted registered suite SKIPPED (no partial-run green!)
        by_id = {s["suite_id"]: s for s in suites_all}
        ordered_to_run = [by_id[sid] for sid in suite_ids_override if sid in by_id]
        omitted = [s for s in suites_all if s["suite_id"] not in selected_set]
    else:
        ordered_to_run = list(suites_all)
        omitted = []

    results_by_id: dict[str, dict[str, Any]] = {}
    post_build_mismatch_err: str | None = None

    for suite in ordered_to_run:
        sid = suite["suite_id"]
        if verbose:
            print(f"[QA {run_id}] Running {sid} ({suite['tier']}, timeout={suite['timeout_seconds']}s)...", flush=True)
        res = execute_suite(repo_root, suite, run_dir)

        # Immediately after N31-BUILD-PIPELINE, assert rebuilt artifact matches ledger digest
        if sid == "N31-BUILD-PIPELINE" and res["verdict"] == "PASS":
            rebuilt_sha = sha256_file(art_path)
            exp_art = registry.get("artifact_expected_sha256", "")
            if exp_art and rebuilt_sha != exp_art:
                res["verdict"] = "FAIL"
                post_build_mismatch_err = (
                    f"E_POST_BUILD_ARTIFACT_MISMATCH: rebuilt={rebuilt_sha} expected_ledger={exp_art}"
                )
                res["failure_reason"] = post_build_mismatch_err

        results_by_id[sid] = res
        if verbose:
            print(
                f"  -> {sid}: {res['verdict']} (exit={res['exit_code']}, "
                f"duration={res['duration_ms']}ms, timed_out={res['timed_out']})",
                flush=True,
            )

    for suite in omitted:
        sid = suite["suite_id"]
        empty_sha = sha256_bytes(b"")
        results_by_id[sid] = {
            "suite_id": sid,
            "tier": suite["tier"],
            "tier_order": int(suite["tier_order"]),
            "owner_task": suite["owner_task"],
            "invocation": suite["invocation"],
            "expected_exit_codes": [int(c) for c in suite.get("expected_exit_codes", [0])],
            "timeout_seconds": float(suite["timeout_seconds"]),
            "exit_code": None,
            "timed_out": False,
            "verdict": "SKIPPED",
            "duration_ms": 0.0,
            "stdout_path": None,
            "stderr_path": None,
            "stdout_sha256": empty_sha,
            "stderr_sha256": empty_sha,
            "report_path": None,
            "report_sha256": None,
            "output_digest": sha256_bytes(canonical_compact_json_bytes({"suite_id": sid, "verdict": "SKIPPED"})),
            "failure_reason": "E_SUITE_SKIPPED: partial run is not allowed to pass",
        }

    # Always emit suites in declared registry order (unless order override requested for logging)
    suite_results = [results_by_id[s["suite_id"]] for s in suites_all]

    # Re-read post-run artifact & build manifest digests
    post_art_sha = sha256_file(art_path) if art_path.is_file() else ("0" * 64)
    post_art_bytes = art_path.stat().st_size if art_path.is_file() else 1
    bm_path = repo_root / registry.get("build_manifest_path", "output/build-manifest.json")
    post_bm_sha = sha256_file(bm_path) if bm_path.is_file() else src_check["build_manifest_sha256"]
    post_bm_bytes = bm_path.stat().st_size if bm_path.is_file() else src_check["build_manifest_bytes"]
    post_bm_data = load_json(bm_path) if bm_path.is_file() else src_check["build_manifest_data"]

    expected_art_sha = registry.get("artifact_expected_sha256", post_art_sha)
    digest_matches_ledger = (post_art_sha == expected_art_sha)

    normalized_vector = [
        {
            "suite_id": r["suite_id"],
            "tier": r["tier"],
            "verdict": r["verdict"],
            "exit_code": r["exit_code"],
            "timed_out": r["timed_out"],
        }
        for r in suite_results
    ]
    normalized_vector_sha = sha256_bytes(canonical_compact_json_bytes(normalized_vector))

    all_passed = (
        digest_matches_ledger
        and post_build_mismatch_err is None
        and all(r["verdict"] == "PASS" for r in suite_results)
    )
    overall_verdict = "PASS" if all_passed else "FAIL"
    finished_utc = datetime.now(timezone.utc).isoformat()

    try:
        reg_rel = str(registry_path.relative_to(repo_root))
    except ValueError:
        reg_rel = str(registry_path)

    manifest_body = {
        "schema_version": 1,
        "task": "N39",
        "run_id": run_id,
        "sequence_number": run_seq,
        "started_utc": started_utc,
        "finished_utc": finished_utc,
        "artifact": {
            "path": art_rel,
            "bytes": post_art_bytes,
            "sha256": post_art_sha,
            "build_id": str(post_bm_data.get("build_id", "")),
            "composite_digest": str(post_bm_data.get("composite_digest", "0" * 64)),
            "ledger_expected_sha256": expected_art_sha,
            "digest_matches_ledger": digest_matches_ledger,
        },
        "build_manifest": {
            "path": registry.get("build_manifest_path", "output/build-manifest.json"),
            "bytes": post_bm_bytes,
            "sha256": post_bm_sha,
        },
        "registry": {
            "path": reg_rel,
            "version": int(registry.get("registry_version", 1)),
            "sha256": registry_sha,
            "suite_count": len(suites_all),
            "update_history": registry.get("update_history", []),
        },
        "sources": src_check["sources"],
        "sources_composite_sha256": src_check["sources_composite_sha256"],
        "suites_integrity": [
            {
                "suite_id": e["suite_id"],
                "path": e["path"],
                "bytes": e["bytes"],
                "sha256": e["sha256"],
                "expected_sha256": e["expected_sha256"],
                "matched": e["matched"],
            }
            for e in reg_check["entries"]
        ],
        "suites_composite_sha256": reg_check["suites_composite_sha256"],
        "environment": collect_environment(),
        "normalization_rule": NORMALIZATION_RULE,
        "suites": suite_results,
        "normalized_verdict_vector": normalized_vector,
        "normalized_verdict_vector_sha256": normalized_vector_sha,
        "overall_verdict": overall_verdict,
    }

    write_info = write_manifest_two_pass(manifest_body, manifest_out)
    if verbose:
        print(
            f"[QA {run_id}] OVERALL={overall_verdict} "
            f"passed={sum(1 for r in suite_results if r['verdict'] == 'PASS')}/{len(suite_results)} "
            f"vector_sha256={normalized_vector_sha[:16]}... "
            f"body_sha256={write_info['body_sha256'][:16]}... "
            f"out={manifest_out}",
            flush=True,
        )

    final_manifest = load_json(manifest_out)
    return (0 if overall_verdict == "PASS" else 1), {
        "refused": False,
        "manifest": final_manifest,
        "write_info": write_info,
    }


def run_negative_and_corner_fixtures(repo_root: Path, registry_path: Path) -> dict[str, Any]:
    """Execute and record all N39 negative & corner-case fixtures in isolated temp dirs:
      - FIX-QA-MISSING-SUITE (A.1)
      - FIX-QA-STALE-SUITE-DIGEST (A.1 / AC1)
      - FIX-QA-VERSIONED-REGISTRY-UPDATE (A.1.1)
      - FIX-QA-SUITE-TIMEOUT-CONTINUE (A.1.2)
      - FIX-QA-SOURCE-TAMPER-AND-RESTORE (B.1.2)
    """
    real_registry = load_json(registry_path)
    fixtures: dict[str, Any] = {}

    # 1. FIX-QA-MISSING-SUITE (A.1)
    bad_missing = copy.deepcopy(real_registry)
    bad_missing["suites"].append({
        "suite_id": "SCRATCH-MISSING-SUITE",
        "tier": "build_and_static_gates",
        "tier_order": 5,
        "owner_task": "N39",
        "description": "Scratch missing suite file fixture",
        "files": [
            {
                "path": "tools/nonexistent_scratch_suite.py",
                "expected_sha256": "a" * 64,
                "bytes": 1,
            }
        ],
        "invocation": ["{python}", "tools/nonexistent_scratch_suite.py"],
        "expected_exit_codes": [0],
        "timeout_seconds": 10,
    })
    res_missing = validate_registry(repo_root, bad_missing, check_ledger=False)
    missing_ok = (
        res_missing["status"] == "FAIL"
        and any("SCRATCH-MISSING-SUITE" in e and "tools/nonexistent_scratch_suite.py" in e for e in res_missing["errors"])
    )
    fixtures["FIX-QA-MISSING-SUITE"] = {
        "status": "PASS" if missing_ok else "FAIL",
        "suite_named": "SCRATCH-MISSING-SUITE",
        "errors": res_missing["errors"],
    }

    # 2. FIX-QA-STALE-SUITE-DIGEST (A.1 / AC1)
    bad_stale = copy.deepcopy(real_registry)
    first_suite = bad_stale["suites"][0]
    first_suite_id = first_suite["suite_id"]
    first_file = first_suite["files"][0]["path"]
    first_suite["files"][0]["expected_sha256"] = "f" * 64
    res_stale = validate_registry(repo_root, bad_stale, check_ledger=False)
    stale_ok = (
        res_stale["status"] == "FAIL"
        and any(first_suite_id in e and first_file in e and "E_SUITE_DIGEST_MISMATCH" in e for e in res_stale["errors"])
    )
    fixtures["FIX-QA-STALE-SUITE-DIGEST"] = {
        "status": "PASS" if stale_ok else "FAIL",
        "suite_named": first_suite_id,
        "file_named": first_file,
        "errors": res_stale["errors"],
    }

    # 3. FIX-QA-VERSIONED-REGISTRY-UPDATE (A.1.1)
    with tempfile.TemporaryDirectory(prefix="qa_fix_update_") as tmp:
        tdir = Path(tmp)
        scratch_suite = tdir / "tools" / "scratch_updatable.py"
        scratch_suite.parent.mkdir(parents=True, exist_ok=True)
        scratch_suite.write_text("print('v1')\n", encoding="utf-8")
        v1_sha = sha256_file(scratch_suite)
        scratch_reg = {
            "schema_version": 1,
            "registry_version": 1,
            "suites": [
                {
                    "suite_id": "SCRATCH-UPDATABLE",
                    "tier": "build_and_static_gates",
                    "tier_order": 1,
                    "owner_task": "N39",
                    "files": [{"path": "tools/scratch_updatable.py", "expected_sha256": v1_sha, "bytes": scratch_suite.stat().st_size}],
                    "invocation": ["{python}", "tools/scratch_updatable.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 10,
                }
            ],
            "update_history": [],
        }
        reg_file = tdir / "qa_registry.json"
        atomic_write_bytes(reg_file, canonical_pretty_json_bytes(scratch_reg))

        # Edit suite legitimately (simulating Phase VIII defect fix)
        scratch_suite.write_text("print('v2 - fixed defect')\n", encoding="utf-8")
        v2_sha = sha256_file(scratch_suite)

        # Updating without reason must fail
        empty_reason_refused = False
        try:
            update_registry_suite(tdir, reg_file, "SCRATCH-UPDATABLE", "tools/scratch_updatable.py", "   ")
        except ValueError as exc:
            empty_reason_refused = "E_UPDATE_REASON_REQUIRED" in str(exc)

        ev = update_registry_suite(
            tdir,
            reg_file,
            "SCRATCH-UPDATABLE",
            "tools/scratch_updatable.py",
            "Legitimate Phase VIII defect fix update",
        )
        updated_reg = load_json(reg_file)
        post_val = validate_registry(tdir, updated_reg, check_ledger=False)
        upd_ok = (
            empty_reason_refused
            and ev["version"] == 2
            and ev["previous_sha256"] == v1_sha
            and ev["new_sha256"] == v2_sha
            and post_val["status"] == "PASS"
        )
        fixtures["FIX-QA-VERSIONED-REGISTRY-UPDATE"] = {
            "status": "PASS" if upd_ok else "FAIL",
            "empty_reason_refused": empty_reason_refused,
            "update_event": ev,
            "post_update_validation": post_val["status"],
        }

    # 4. FIX-QA-SUITE-TIMEOUT-CONTINUE (A.1.2)
    with tempfile.TemporaryDirectory(prefix="qa_fix_timeout_") as tmp:
        tdir = Path(tmp)
        (tdir / "tools").mkdir()
        (tdir / "output").mkdir()
        (tdir / "output" / "simulator.html").write_text("<!doctype html><html></html>\n", encoding="utf-8")
        art_sha = sha256_file(tdir / "output" / "simulator.html")

        sleeper = tdir / "tools" / "scratch_sleeper.py"
        sleeper.write_text("import time; time.sleep(5)\n", encoding="utf-8")
        after = tdir / "tools" / "scratch_after.py"
        after.write_text("print('SCRATCH_AFTER_TIMEOUT_OK')\n", encoding="utf-8")

        t_reg = {
            "schema_version": 1,
            "registry_version": 1,
            "artifact_path": "output/simulator.html",
            "artifact_expected_sha256": art_sha,
            "suites": [
                {
                    "suite_id": "SCRATCH-SLEEP-TIMEOUT",
                    "tier": "build_and_static_gates",
                    "tier_order": 1,
                    "owner_task": "N39",
                    "files": [{"path": "tools/scratch_sleeper.py", "expected_sha256": sha256_file(sleeper), "bytes": sleeper.stat().st_size}],
                    "invocation": ["{python}", "tools/scratch_sleeper.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 0.4,
                },
                {
                    "suite_id": "SCRATCH-AFTER-TIMEOUT",
                    "tier": "audits",
                    "tier_order": 2,
                    "owner_task": "N39",
                    "files": [{"path": "tools/scratch_after.py", "expected_sha256": sha256_file(after), "bytes": after.stat().st_size}],
                    "invocation": ["{python}", "tools/scratch_after.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 5.0,
                },
            ],
            "update_history": [],
        }
        reg_file = tdir / "qa_registry.json"
        atomic_write_bytes(reg_file, canonical_pretty_json_bytes(t_reg))
        man_file = tdir / "timeout_manifest.json"

        rc_t, info_t = run_qa(
            tdir,
            reg_file,
            man_file,
            run_seq=1,
            run_dir=tdir / "runs",
            check_ledger=False,
            check_sources=False,
            verbose=False,
        )
        suites_t = info_t["manifest"]["suites"]
        s0, s1 = suites_t[0], suites_t[1]
        timeout_ok = (
            rc_t == 1
            and s0["suite_id"] == "SCRATCH-SLEEP-TIMEOUT"
            and s0["verdict"] == "TIMEOUT"
            and s0["timed_out"] is True
            and "SCRATCH-SLEEP-TIMEOUT" in (s0.get("failure_reason") or "")
            and s1["suite_id"] == "SCRATCH-AFTER-TIMEOUT"
            and s1["verdict"] == "PASS"
            and info_t["manifest"]["overall_verdict"] == "FAIL"
        )
        fixtures["FIX-QA-SUITE-TIMEOUT-CONTINUE"] = {
            "status": "PASS" if timeout_ok else "FAIL",
            "exit_code": rc_t,
            "overall_verdict": info_t["manifest"]["overall_verdict"],
            "timed_out_suite": {
                "suite_id": s0["suite_id"],
                "verdict": s0["verdict"],
                "timed_out": s0["timed_out"],
                "duration_ms": s0["duration_ms"],
                "failure_reason": s0["failure_reason"],
            },
            "continued_suite": {
                "suite_id": s1["suite_id"],
                "verdict": s1["verdict"],
                "exit_code": s1["exit_code"],
            },
        }

    # 5. FIX-QA-SOURCE-TAMPER-AND-RESTORE (B.1.2)
    # Build an isolated scratch copy of the build sources + manifest + minimal fast registry
    # to prove tampered source is refused by name BEFORE any suite runs, and restored rerun passes!
    with tempfile.TemporaryDirectory(prefix="qa_fix_tamper_") as tmp:
        tdir = Path(tmp)
        bm_real = load_json(repo_root / "output" / "build-manifest.json")
        # Copy all 132 build sources + output/build-manifest.json + output/simulator.html + ledger
        for src in bm_real["sources"]:
            src_rel = src["path"]
            dst = tdir / src_rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo_root / src_rel, dst)
        for extra in ("output/build-manifest.json", "output/simulator.html", "evidence/VERIFICATION_LEDGER.md", "tools/check_a11y.py"):
            dst = tdir / extra
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo_root / extra, dst)

        # Scratch suite that creates a marker file if executed (proves 0 suites ran during tamper refusal!)
        marker = tdir / "suite_executed.marker"
        probe_suite = tdir / "tools" / "scratch_probe.py"
        probe_suite.write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran')\nprint('PROBE_PASS')\n",
            encoding="utf-8",
        )
        t_reg = {
            "schema_version": 1,
            "registry_version": 1,
            "artifact_path": "output/simulator.html",
            "artifact_expected_sha256": real_registry["artifact_expected_sha256"],
            "build_manifest_path": "output/build-manifest.json",
            "build_manifest_expected_sha256": real_registry["build_manifest_expected_sha256"],
            "ledger_path": "evidence/VERIFICATION_LEDGER.md",
            "suites": [
                {
                    "suite_id": "SCRATCH-TAMPER-PROBE",
                    "tier": "build_and_static_gates",
                    "tier_order": 1,
                    "owner_task": "N39",
                    "files": [{"path": "tools/scratch_probe.py", "expected_sha256": sha256_file(probe_suite), "bytes": probe_suite.stat().st_size}],
                    "invocation": ["{python}", "tools/scratch_probe.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 10,
                }
            ],
            "update_history": [],
        }
        reg_file = tdir / "qa_registry.json"
        atomic_write_bytes(reg_file, canonical_pretty_json_bytes(t_reg))

        # Tamper 1 byte in src/shell.html
        target_rel = "src/shell.html"
        target_path = tdir / target_rel
        orig_bytes = target_path.read_bytes()
        target_path.write_bytes(orig_bytes + b" ")

        rc_tamper, info_tamper = run_qa(
            tdir,
            reg_file,
            tdir / "tamper_manifest.json",
            run_seq=1,
            run_dir=tdir / "run_tamper",
            check_ledger=False,
            check_sources=True,
            verbose=False,
        )
        ran_during_tamper = marker.exists()

        # Restore exact original bytes and rerun
        target_path.write_bytes(orig_bytes)
        rc_restored, info_restored = run_qa(
            tdir,
            reg_file,
            tdir / "restored_manifest.json",
            run_seq=2,
            run_dir=tdir / "run_restored",
            check_ledger=False,
            check_sources=True,
            verbose=False,
        )
        ran_after_restore = marker.exists()

        tamper_ok = (
            rc_tamper == 2
            and info_tamper.get("refused") is True
            and not ran_during_tamper
            and any(target_rel in e and "E_SOURCE_TAMPERED" in e for e in info_tamper.get("errors", []))
            and rc_restored == 0
            and ran_after_restore
            and info_restored["manifest"]["overall_verdict"] == "PASS"
        )
        fixtures["FIX-QA-SOURCE-TAMPER-AND-RESTORE"] = {
            "status": "PASS" if tamper_ok else "FAIL",
            "tampered_file": target_rel,
            "tampered_run_exit_code": rc_tamper,
            "tampered_run_refused": info_tamper.get("refused"),
            "suites_executed_during_tamper": 1 if ran_during_tamper else 0,
            "tamper_errors": info_tamper.get("errors", []),
            "restored_run_exit_code": rc_restored,
            "restored_overall_verdict": info_restored.get("manifest", {}).get("overall_verdict"),
        }

    # 6. FIX-QA-PARTIAL-SKIP-FAILS (No partial-run green: skipped suite = FAIL)
    with tempfile.TemporaryDirectory(prefix="qa_fix_skip_") as tmp:
        tdir = Path(tmp)
        (tdir / "tools").mkdir()
        (tdir / "output").mkdir()
        (tdir / "output" / "simulator.html").write_text("<!doctype html><html></html>\n", encoding="utf-8")
        art_sha = sha256_file(tdir / "output" / "simulator.html")
        s1 = tdir / "tools" / "s1.py"
        s2 = tdir / "tools" / "s2.py"
        s1.write_text("print('S1_OK')\n", encoding="utf-8")
        s2.write_text("print('S2_OK')\n", encoding="utf-8")
        s_reg = {
            "schema_version": 1,
            "registry_version": 1,
            "artifact_path": "output/simulator.html",
            "artifact_expected_sha256": art_sha,
            "suites": [
                {
                    "suite_id": "SCRATCH-RUN-ONE",
                    "tier": "build_and_static_gates",
                    "tier_order": 1,
                    "owner_task": "N39",
                    "files": [{"path": "tools/s1.py", "expected_sha256": sha256_file(s1), "bytes": s1.stat().st_size}],
                    "invocation": ["{python}", "tools/s1.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 5,
                },
                {
                    "suite_id": "SCRATCH-OMITTED-TWO",
                    "tier": "audits",
                    "tier_order": 2,
                    "owner_task": "N39",
                    "files": [{"path": "tools/s2.py", "expected_sha256": sha256_file(s2), "bytes": s2.stat().st_size}],
                    "invocation": ["{python}", "tools/s2.py"],
                    "expected_exit_codes": [0],
                    "timeout_seconds": 5,
                },
            ],
            "update_history": [],
        }
        reg_file = tdir / "qa_registry.json"
        atomic_write_bytes(reg_file, canonical_pretty_json_bytes(s_reg))
        rc_skip, info_skip = run_qa(
            tdir,
            reg_file,
            tdir / "skip_manifest.json",
            run_seq=1,
            run_dir=tdir / "run_skip",
            check_ledger=False,
            check_sources=False,
            suite_ids_override=["SCRATCH-RUN-ONE"],
            verbose=False,
        )
        msuites = info_skip["manifest"]["suites"]
        skip_ok = (
            rc_skip == 1
            and info_skip["manifest"]["overall_verdict"] == "FAIL"
            and msuites[0]["verdict"] == "PASS"
            and msuites[1]["suite_id"] == "SCRATCH-OMITTED-TWO"
            and msuites[1]["verdict"] == "SKIPPED"
        )
        fixtures["FIX-QA-PARTIAL-SKIP-FAILS"] = {
            "status": "PASS" if skip_ok else "FAIL",
            "exit_code": rc_skip,
            "overall_verdict": info_skip["manifest"]["overall_verdict"],
            "suite_verdicts": {m["suite_id"]: m["verdict"] for m in msuites},
        }

    all_ok = all(f["status"] == "PASS" for f in fixtures.values())
    return {
        "schema_version": 1,
        "task": "N39",
        "status": "PASS" if all_ok else "FAIL",
        "fixtures": fixtures,
    }


def run_order_independence_fixture(
    repo_root: Path,
    registry_path: Path,
    pair: tuple[str, str],
) -> dict[str, Any]:
    """Subtask C.1.1: Run two interacting suites in both orders (A->B and B->A)
    inside isolated per-suite contexts and assert identical verdicts & output digests.
    """
    reg = load_json(registry_path)
    by_id = {s["suite_id"]: s for s in reg["suites"]}
    s_a, s_b = by_id[pair[0]], by_id[pair[1]]

    with tempfile.TemporaryDirectory(prefix="qa_order_indep_") as tmp:
        tdir = Path(tmp)
        ab_dir = tdir / "order_AB"
        ba_dir = tdir / "order_BA"

        ab_a = execute_suite(repo_root, s_a, ab_dir)
        ab_b = execute_suite(repo_root, s_b, ab_dir)

        ba_b = execute_suite(repo_root, s_b, ba_dir)
        ba_a = execute_suite(repo_root, s_a, ba_dir)

        verdict_a_match = (ab_a["verdict"] == ba_a["verdict"] == "PASS") and (ab_a["exit_code"] == ba_a["exit_code"])
        verdict_b_match = (ab_b["verdict"] == ba_b["verdict"] == "PASS") and (ab_b["exit_code"] == ba_b["exit_code"])

        # Compare normalized suite semantic results (report verdict digest if present)
        def _semantic_key(res: dict[str, Any], rdir: Path) -> dict[str, Any]:
            key: dict[str, Any] = {
                "suite_id": res["suite_id"],
                "verdict": res["verdict"],
                "exit_code": res["exit_code"],
                "timed_out": res["timed_out"],
            }
            if res["report_path"]:
                rp = Path(res["report_path"])
                if not rp.is_absolute():
                    rp = repo_root / rp
                if rp.is_file():
                    rep = load_json(rp)
                    if "determinism" in rep and isinstance(rep["determinism"], dict):
                        key["verdict_sequence_sha256"] = rep["determinism"].get("verdict_sequence_sha256")
                    elif "verdict_sequence_sha256" in rep:
                        key["verdict_sequence_sha256"] = rep["verdict_sequence_sha256"]
                    elif "verdict_sequence_digest" in rep:
                        key["verdict_sequence_digest"] = rep["verdict_sequence_digest"]
                    elif "pass" in rep:
                        key["pass"] = rep["pass"]
                    elif "status" in rep:
                        key["status"] = rep["status"]
            return key

        key_ab_a = _semantic_key(ab_a, ab_dir)
        key_ba_a = _semantic_key(ba_a, ba_dir)
        key_ab_b = _semantic_key(ab_b, ab_dir)
        key_ba_b = _semantic_key(ba_b, ba_dir)

        identical = (
            verdict_a_match
            and verdict_b_match
            and key_ab_a == key_ba_a
            and key_ab_b == key_ba_b
        )
        return {
            "schema_version": 1,
            "task": "N39",
            "status": "PASS" if identical else "FAIL",
            "pair": list(pair),
            "identical_results": identical,
            "order_AB": {
                "sequence": [pair[0], pair[1]],
                pair[0]: {"semantic": key_ab_a, "duration_ms": ab_a["duration_ms"]},
                pair[1]: {"semantic": key_ab_b, "duration_ms": ab_b["duration_ms"]},
            },
            "order_BA": {
                "sequence": [pair[1], pair[0]],
                pair[1]: {"semantic": key_ba_b, "duration_ms": ba_b["duration_ms"]},
                pair[0]: {"semantic": key_ba_a, "duration_ms": ba_a["duration_ms"]},
            },
        }


def build_completeness_and_evidence_pack(
    repo_root: Path,
    manifest_path: Path,
    pack_out: Path,
    *,
    two_run_path: Path | None = None,
    fixtures_path: Path | None = None,
    order_path: Path | None = None,
    verifier_path: Path | None = None,
) -> dict[str, Any]:
    """Subtask C.1.2: Cross-check every task in VERIFICATION_LEDGER.md and the
    40-task roadmap against the evidence pack, enumerating represented tasks,
    honest open/UNVERIFIED items, and asserting unexplained_absent == [].
    """
    ledger_path = repo_root / DEFAULT_LEDGER
    ledger_text = ledger_path.read_text(encoding="utf-8")
    manifest = load_json(manifest_path)

    # Extract all Nxx headings present in VERIFICATION_LEDGER.md
    ledger_tasks = sorted(set(re.findall(r"^##\s+(N\d{2})\b", ledger_text, flags=re.MULTILINE)))

    # Map every roadmap task N01..N39 to its on-disk evidence files
    ev_dir = repo_root / "evidence"
    all_ev_files = sorted(p for p in ev_dir.iterdir() if p.is_file())

    task_records: list[dict[str, Any]] = []
    unexplained_absent: list[dict[str, str]] = []
    open_gap_tasks = {"N09"}  # Recorded dependency gap in N17/N19/N23

    # Map live QA suites to the tasks they verify
    suites_by_task: dict[str, list[str]] = {}
    for s in manifest.get("suites", []):
        suites_by_task.setdefault(s["owner_task"], []).append(s["suite_id"])

    for num in range(1, 40):
        tid = f"N{num:02d}"
        in_ledger = tid in ledger_tasks
        matched_files = [
            p for p in all_ev_files
            if p.name.startswith(f"{tid}_")
            and p.resolve() != pack_out.resolve()
            and p.name != "N39_PACK_VERIFIER_RECORD.json"
        ]
        # N01 also owns REPO_LOCAL_VERIFICATION.json, SOURCE_FREEZE_INVENTORY.json, V01_CONFLICT_ENTRY.json
        if tid == "N01":
            for extra_name in ("REPO_LOCAL_VERIFICATION.json", "SOURCE_FREEZE_INVENTORY.json", "V01_CONFLICT_ENTRY.json"):
                ep = ev_dir / extra_name
                if ep.is_file() and ep not in matched_files:
                    matched_files.append(ep)
        # N37 also owns visual_baselines/baseline_manifest.json
        if tid == "N37":
            bm_f = ev_dir / "visual_baselines" / "baseline_manifest.json"
            if bm_f.is_file():
                matched_files.append(bm_f)

        file_digests = [
            {
                "path": str(p.relative_to(repo_root)),
                "bytes": p.stat().st_size,
                "sha256": sha256_file(p),
            }
            for p in sorted(matched_files)
        ]

        if tid in open_gap_tasks:
            status = "HONESTLY_OPEN"
            note = "Recorded dependency gap (OPEN-N09-GAP); tracked openly across N17, N19, N23 for N40."
        elif file_digests or suites_by_task.get(tid) or tid == "N39":
            status = "REPRESENTED"
            note = "Evidence files and/or live QA suite results represented in pack."
        else:
            status = "UNEXPLAINED_ABSENT"
            note = f"Task {tid} has no represented evidence in pack and is not in explicit open items."
            unexplained_absent.append({"task": tid, "reason": note})

        task_records.append({
            "task": tid,
            "in_ledger": in_ledger,
            "status": status,
            "qa_suites": suites_by_task.get(tid, []),
            "evidence_files": file_digests,
            "note": note,
        })

    # Verify every ledger evidence category (build gates, static contract, contrast,
    # a11y, noscript/print, perf/storage/security audits, property/mutation, visual matrix,
    # browser smoke, source freeze, conflict registry, manual protocols) is mapped
    ledger_evidence_types = [
        {"type": "source_freeze_and_repo_local_prep", "owner": "N01", "covered_by": ["N01-PREP-LOCAL", "N01-SOURCE-INVENTORY"], "status": "REPRESENTED"},
        {"type": "coverage_and_conventions_build_gates", "owner": "N02-N03", "covered_by": ["N31-BUILD-PIPELINE"], "status": "REPRESENTED"},
        {"type": "schema_bank_golden_vectors_engines_forms", "owner": "N04-N24", "covered_by": ["N31-BUILD-PIPELINE", "N36-PROPERTY-SUITE"], "status": "REPRESENTED"},
        {"type": "analytics_mastery_scheduler_remediation_revision_practice", "owner": "N25-N30", "covered_by": ["N31-BUILD-PIPELINE", "N31-RUNTIME-SMOKE"], "status": "REPRESENTED"},
        {"type": "single_file_build_and_static_contract", "owner": "N31", "covered_by": ["N31-BUILD-PIPELINE", "N31-ARTIFACT-CONTRACT", "N31-RUNTIME-SMOKE"], "status": "REPRESENTED"},
        {"type": "wcag_aa_contrast_targets_reflow", "owner": "N32", "covered_by": ["N32-WCAG-CONTRACT"], "status": "REPRESENTED"},
        {"type": "keyboard_focus_aria_machine_checks", "owner": "N33", "covered_by": ["N33-A11Y-CONTRACT"], "status": "REPRESENTED"},
        {"type": "noscript_fallback_and_print_paper_mode", "owner": "N34", "covered_by": ["N34-NOSCRIPT-PRINT"], "status": "REPRESENTED"},
        {"type": "perf_storage_security_audits", "owner": "N35", "covered_by": ["N35-AUDIT-PERF", "N35-AUDIT-STORAGE", "N35-AUDIT-SECURITY"], "status": "REPRESENTED"},
        {"type": "property_and_mutation_suites", "owner": "N36", "covered_by": ["N36-PROPERTY-SUITE", "N36-MUTATION-SUITE"], "status": "REPRESENTED"},
        {"type": "visual_regression_matrix_falkon", "owner": "N37", "covered_by": ["N37-VISUAL-MATRIX"], "status": "REPRESENTED"},
        {"type": "offline_browser_smoke_and_falkon_protocols", "owner": "N38", "covered_by": ["N38-BROWSER-SMOKE"], "status": "REPRESENTED"},
        {"type": "manual_screen_reader_cross_browser_physical_print", "owner": "N33/N38", "covered_by": [o["id"] for o in EXPLICIT_OPEN_ITEMS if o["source_task"] == "N38"], "status": "HONESTLY_OPEN"},
        {"type": "n09_misconception_registry_gap", "owner": "N09", "covered_by": ["OPEN-N09-GAP"], "status": "HONESTLY_OPEN"},
        {"type": "v01_full_workspace_sibling_mode", "owner": "N01", "covered_by": ["OPEN-N01-V01"], "status": "HONESTLY_OPEN"},
        {"type": "v08_catalase_scientific_uncertainty", "owner": "N03", "covered_by": ["OPEN-N03-V08"], "status": "HONESTLY_OPEN"},
    ]

    # Section 18 Ten-Point Release Gate index for N40
    gate_index = {
        "G1_artifact_contract_and_reproducibility": {
            "suites": ["N31-BUILD-PIPELINE", "N31-ARTIFACT-CONTRACT", "N31-RUNTIME-SMOKE"],
            "evidence": ["evidence/N31_CORPUS_RECORD.json", "evidence/N31_ARTIFACT_CONTRACT.json", "output/build-manifest.json"],
        },
        "G2_scientific_baseline_and_conventions": {
            "suites": ["N01-PREP-LOCAL", "N01-SOURCE-INVENTORY", "N31-BUILD-PIPELINE"],
            "evidence": ["evidence/REPO_LOCAL_VERIFICATION.json", "evidence/SOURCE_FREEZE_INVENTORY.json", "evidence/N02_ANCHOR_RESOLUTION.json", "evidence/N03_CONFLICT_REGISTRY.json"],
        },
        "G3_bank_and_forms_integrity": {
            "suites": ["N31-BUILD-PIPELINE", "N36-PROPERTY-SUITE"],
            "evidence": ["evidence/N20_VERIFICATION_RECORD.json", "evidence/N24_CORPUS_RECORD.json", "output/forms/form_A.json", "output/forms/form_B.json", "output/forms/form_C.json"],
        },
        "G4_grading_and_fairness_evidence": {
            "suites": ["N36-PROPERTY-SUITE", "N36-MUTATION-SUITE"],
            "evidence": ["evidence/N05_ORACLE_RECORD.json", "evidence/N17_CORPUS_RECORD.json", "evidence/N18_CORPUS_RECORD.json", "evidence/N19_CORPUS_RECORD.json", "evidence/N23_CORPUS_RECORD.json", "evidence/N36_TEST_MANIFEST.json"],
        },
        "G5_accessibility_contract": {
            "suites": ["N32-WCAG-CONTRACT", "N33-A11Y-CONTRACT", "N38-BROWSER-SMOKE"],
            "evidence": ["evidence/N32_CONTRAST_REPORT.json", "evidence/N33_A11Y_REPORT.json", "docs/SCREEN_READER_PROTOCOL.md", "evidence/N38_SMOKE_REPORT.json"],
            "open_items": ["OPEN-N38-01", "OPEN-N38-02", "OPEN-N38-03", "OPEN-N38-04", "OPEN-N38-05"],
        },
        "G6_offline_and_fallback_guarantees": {
            "suites": ["N31-ARTIFACT-CONTRACT", "N34-NOSCRIPT-PRINT", "N38-BROWSER-SMOKE"],
            "evidence": ["evidence/N31_ARTIFACT_CONTRACT.json", "evidence/N34_CORPUS_RECORD.json", "evidence/N38_SMOKE_REPORT.json"],
        },
        "G7_security_audit": {
            "suites": ["N35-AUDIT-PERF", "N35-AUDIT-STORAGE", "N35-AUDIT-SECURITY"],
            "evidence": ["evidence/N35_PERF_RECORD.json", "evidence/N35_STORAGE_RECORD.json", "evidence/N35_SECURITY_RECORD.json"],
        },
        "G8_test_suite_determinism": {
            "suites": ["N36-PROPERTY-SUITE", "N36-MUTATION-SUITE"],
            "evidence": ["evidence/N36_DETERMINISM_RUNS.json", "evidence/N36_MUTATION_REPORT.json", "evidence/N39_TWO_RUN_EQUALITY.json"],
        },
        "G9_visual_and_smoke_evidence": {
            "suites": ["N37-VISUAL-MATRIX", "N38-BROWSER-SMOKE"],
            "evidence": ["evidence/N37_CALIBRATION_AND_FIXTURES.json", "evidence/visual_baselines/baseline_manifest.json", "evidence/N37_MATRIX_REPORT.json", "evidence/N38_SMOKE_REPORT.json"],
            "open_items": ["OPEN-N38-06", "OPEN-N38-07", "OPEN-N38-08", "OPEN-N38-09"],
        },
        "G10_documentation_and_evidence_completeness": {
            "suites": ["N39-INDEPENDENT-VERIFIER"],
            "evidence": ["evidence/N39_QA_MANIFEST.json", "evidence/N39_EVIDENCE_PACK.json", "docs/QA_RUNNER_FORMAT.md", "evidence/VERIFICATION_LEDGER.md"],
        },
    }

    def _ref(p: Path | None) -> dict[str, Any] | None:
        if p is None or not p.is_file():
            return None
        return {
            "path": str(p.relative_to(repo_root)),
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }

    tools_chain = {}
    for rel in (
        "tools/qa_runner.py",
        "tools/verify_qa_manifest.py",
        "data/qa_registry.json",
        "data/qa_manifest_schema.json",
        "docs/QA_RUNNER_FORMAT.md",
    ):
        fp = repo_root / rel
        if fp.is_file():
            tools_chain[rel] = {"bytes": fp.stat().st_size, "sha256": sha256_file(fp)}

    pack = {
        "schema_version": 1,
        "task": "N39",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "handoff_target": "N40 ten-point release gate",
        "artifact": manifest["artifact"],
        "build_manifest": manifest["build_manifest"],
        "qa_manifest": {
            "path": str(manifest_path.relative_to(repo_root)),
            "run_id": manifest["run_id"],
            "overall_verdict": manifest["overall_verdict"],
            "normalized_verdict_vector": manifest["normalized_verdict_vector"],
            "normalized_verdict_vector_sha256": manifest["normalized_verdict_vector_sha256"],
            "body_sha256": manifest["manifest_trailer"]["body_sha256"],
            "file_sha256": sha256_file(manifest_path),
            "bytes": manifest_path.stat().st_size,
        },
        "environment": manifest["environment"],
        "tools_and_docs": tools_chain,
        "proof_artifacts": {
            "two_run_equality": _ref(two_run_path),
            "fixtures": _ref(fixtures_path),
            "order_independence": _ref(order_path),
            "independent_verifier": _ref(verifier_path),
        },
        "completeness_crosscheck": {
            "status": "PASS" if (not unexplained_absent and manifest["overall_verdict"] == "PASS") else "FAIL",
            "ledger_path": DEFAULT_LEDGER,
            "ledger_tasks_found": ledger_tasks,
            "roadmap_tasks_checked": len(task_records),
            "represented_count": sum(1 for t in task_records if t["status"] == "REPRESENTED"),
            "honestly_open_count": sum(1 for t in task_records if t["status"] == "HONESTLY_OPEN"),
            "unexplained_absent": unexplained_absent,
            "ledger_evidence_types": ledger_evidence_types,
            "task_records": task_records,
        },
        "open_items": EXPLICIT_OPEN_ITEMS,
        "ten_point_gate_index": gate_index,
        "runner_documentation": {
            "one_command": "python3 tools/qa_runner.py",
            "expected_runtime": "~11-12 minutes (Tier 1-3 ~58s, Tier 4 N37 visual matrix ~9-10m, Tier 5 N38 browser smoke ~35-45s)",
            "verification_command": "python3 tools/verify_qa_manifest.py --manifest evidence/N39_QA_MANIFEST.json --pack evidence/N39_EVIDENCE_PACK.json",
            "doc_path": "docs/QA_RUNNER_FORMAT.md",
        },
    }
    atomic_write_bytes(pack_out, canonical_pretty_json_bytes(pack))
    return pack


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="N39 Reproducible QA Runner & SHA-256 Evidence Chain")
    ap.add_argument("--repo-root", default=str(REPO_ROOT))
    ap.add_argument("--registry", default=DEFAULT_REGISTRY)
    ap.add_argument("--out", default=DEFAULT_MANIFEST_OUT)
    ap.add_argument("--run-seq", type=int, default=1)
    ap.add_argument("--run-dir", default=None)
    ap.add_argument("--validate-registry-only", action="store_true")
    ap.add_argument("--skip-ledger-check", action="store_true", help="For isolated scratch tests only")
    ap.add_argument("--update-suite", default=None, help="Suite ID for versioned registry digest update")
    ap.add_argument("--file", dest="update_file", default=None, help="Relative file path to update in registry")
    ap.add_argument("--reason", default=None, help="Mandatory reason for versioned registry update")
    ap.add_argument("--run-fixtures", action="store_true", help="Run all negative/corner-case fixtures")
    ap.add_argument("--fixtures-out", default="evidence/N39_FIXTURES_RECORD.json")
    ap.add_argument("--order-fixture", default=None, help="Comma-separated pair of suite IDs for order-independence proof")
    ap.add_argument("--order-out", default="evidence/N39_ORDER_INDEPENDENCE.json")
    ap.add_argument("--build-pack", action="store_true", help="Build frozen N39 evidence pack & completeness cross-check")
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST_OUT, help="Manifest path for --build-pack")
    ap.add_argument("--pack-out", default=DEFAULT_PACK_OUT)
    ap.add_argument("--two-run-ref", default="evidence/N39_TWO_RUN_EQUALITY.json")
    ap.add_argument("--verifier-ref", default="evidence/N39_VERIFIER_RECORD.json")
    ap.add_argument("--compare-runs", nargs=2, metavar=("MANIFEST1", "MANIFEST2"), default=None)
    ap.add_argument("--compare-out", default="evidence/N39_TWO_RUN_EQUALITY.json")
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()

    if args.compare_runs:
        m1_p = Path(args.compare_runs[0])
        m2_p = Path(args.compare_runs[1])
        if not m1_p.is_absolute():
            m1_p = repo_root / m1_p
        if not m2_p.is_absolute():
            m2_p = repo_root / m2_p
        m1 = load_json(m1_p)
        m2 = load_json(m2_p)
        v1 = m1["normalized_verdict_vector"]
        v2 = m2["normalized_verdict_vector"]
        s1 = m1["normalized_verdict_vector_sha256"]
        s2 = m2["normalized_verdict_vector_sha256"]
        equal = (
            v1 == v2
            and s1 == s2
            and m1["artifact"]["sha256"] == m2["artifact"]["sha256"]
            and m1["sources_composite_sha256"] == m2["sources_composite_sha256"]
            and m1["suites_composite_sha256"] == m2["suites_composite_sha256"]
            and m1["overall_verdict"] == m2["overall_verdict"] == "PASS"
        )
        cmp_rec = {
            "schema_version": 1,
            "task": "N39",
            "status": "PASS" if equal else "FAIL",
            "identical_normalized_verdict_vectors": equal,
            "normalization_rule": NORMALIZATION_RULE,
            "artifact_sha256": m1["artifact"]["sha256"],
            "sources_composite_sha256": m1["sources_composite_sha256"],
            "suites_composite_sha256": m1["suites_composite_sha256"],
            "run1": {
                "run_id": m1["run_id"],
                "manifest_path": str(m1_p.relative_to(repo_root)),
                "manifest_body_sha256": m1["manifest_trailer"]["body_sha256"],
                "manifest_file_sha256": sha256_file(m1_p),
                "overall_verdict": m1["overall_verdict"],
                "normalized_verdict_vector_sha256": s1,
                "total_duration_ms": round(sum(x["duration_ms"] for x in m1["suites"]), 3),
            },
            "run2": {
                "run_id": m2["run_id"],
                "manifest_path": str(m2_p.relative_to(repo_root)),
                "manifest_body_sha256": m2["manifest_trailer"]["body_sha256"],
                "manifest_file_sha256": sha256_file(m2_p),
                "overall_verdict": m2["overall_verdict"],
                "normalized_verdict_vector_sha256": s2,
                "total_duration_ms": round(sum(x["duration_ms"] for x in m2["suites"]), 3),
            },
            "normalized_verdict_vector": v2,
        }
        cout = Path(args.compare_out)
        if not cout.is_absolute():
            cout = repo_root / cout
        atomic_write_bytes(cout, canonical_pretty_json_bytes(cmp_rec))
        print(f"N39_TWO_RUN_EQUALITY {cmp_rec['status']}: identical={equal} vector_sha256={s1[:16]}... out={cout}")
        return 0 if equal else 1
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path

    if args.update_suite:
        if not args.update_file:
            print("FAIL --update-suite requires --file", file=sys.stderr)
            return 2
        try:
            ev = update_registry_suite(repo_root, registry_path, args.update_suite, args.update_file, args.reason or "")
        except Exception as exc:
            print(f"FAIL registry update: {exc}", file=sys.stderr)
            return 2
        print(f"UPDATED registry v{ev['version']}: {ev['suite_id']} {ev['path']} {ev['previous_sha256'][:16]} -> {ev['new_sha256'][:16]}")
        return 0

    if args.validate_registry_only:
        reg = load_json(registry_path)
        res = validate_registry(repo_root, reg, check_ledger=not args.skip_ledger_check)
        print(f"REGISTRY_VALIDATION {res['status']}: suites={res['suite_count']} files={res['file_count']} errors={len(res['errors'])}")
        for e in res["errors"]:
            print(f"  - {e}", file=sys.stderr)
        return 0 if res["status"] == "PASS" else 1

    if args.run_fixtures:
        fix = run_negative_and_corner_fixtures(repo_root, registry_path)
        fout = Path(args.fixtures_out)
        if not fout.is_absolute():
            fout = repo_root / fout
        atomic_write_bytes(fout, canonical_pretty_json_bytes(fix))
        print(f"N39_FIXTURES {fix['status']}: " + ", ".join(f"{k}={v['status']}" for k, v in fix["fixtures"].items()))
        return 0 if fix["status"] == "PASS" else 1

    if args.order_fixture:
        parts = [p.strip() for p in args.order_fixture.split(",") if p.strip()]
        if len(parts) != 2:
            print("FAIL --order-fixture requires exactly two comma-separated suite IDs", file=sys.stderr)
            return 2
        ores = run_order_independence_fixture(repo_root, registry_path, (parts[0], parts[1]))
        oout = Path(args.order_out)
        if not oout.is_absolute():
            oout = repo_root / oout
        atomic_write_bytes(oout, canonical_pretty_json_bytes(ores))
        print(f"N39_ORDER_INDEPENDENCE {ores['status']}: pair={ores['pair']} identical={ores['identical_results']} out={oout}")
        return 0 if ores["status"] == "PASS" else 1

    if args.build_pack:
        mpath = Path(args.manifest)
        if not mpath.is_absolute():
            mpath = repo_root / mpath
        pout = Path(args.pack_out)
        if not pout.is_absolute():
            pout = repo_root / pout
        pack = build_completeness_and_evidence_pack(
            repo_root,
            mpath,
            pout,
            two_run_path=(repo_root / args.two_run_ref),
            fixtures_path=(repo_root / args.fixtures_out),
            order_path=(repo_root / args.order_out),
            verifier_path=(repo_root / args.verifier_ref),
        )
        cc = pack["completeness_crosscheck"]
        print(
            f"N39_EVIDENCE_PACK {cc['status']}: represented={cc['represented_count']} "
            f"honestly_open={cc['honestly_open_count']} unexplained_absent={len(cc['unexplained_absent'])} "
            f"open_items={len(pack['open_items'])} out={pout}"
        )
        return 0 if cc["status"] == "PASS" else 1

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = repo_root / out_path
    rdir = Path(args.run_dir) if args.run_dir else None
    if rdir is not None and not rdir.is_absolute():
        rdir = repo_root / rdir

    rc, _ = run_qa(
        repo_root,
        registry_path,
        out_path,
        run_seq=args.run_seq,
        run_dir=rdir,
        check_ledger=not args.skip_ledger_check,
        check_sources=True,
        verbose=True,
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
