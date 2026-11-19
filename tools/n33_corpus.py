#!/usr/bin/env python3
"""N33 Extended Corpus & Two-Run Parity Runner.

Executes:
  1. TypeScript drift check (compile_n21_ts.py --check)
  2. Two consecutive fresh-process rebuilds (tools/build.py, 30 gates) for byte parity
  3. N33 A11y / Keyboard / Focus checker (tools/check_a11y.py) -> evidence/N33_A11Y_REPORT.json
  4. Runtime & smoke harness (tools/check_n31_runtime.js, 29/29 vectors)
  5. Standalone artifact contract (tools/check_artifact.py)
  6. N22 ARIA parity checks (check_n22_components.js, check_n22_semantics.js)
  7. Writes evidence/N33_CORPUS_RECORD.json with digests and split epistemic status.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_cmd(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed ({' '.join(cmd)}): rc={proc.returncode}\n{proc.stderr}\n{proc.stdout}")
    return proc.stdout.strip()


def main() -> int:
    run_cmd(["python3", "tools/compile_n21_ts.py", "--check"])

    # Two consecutive fresh-process rebuilds for byte-identical parity
    run_cmd(["python3", "tools/build.py"])
    html_path = ROOT / "output" / "simulator.html"
    manifest_path = ROOT / "output" / "build-manifest.json"
    run1_html_sha = sha256_file(html_path)
    run1_html_bytes = html_path.stat().st_size
    run1_manifest_sha = sha256_file(manifest_path)

    run_cmd(["python3", "tools/build.py"])
    run2_html_sha = sha256_file(html_path)
    run2_html_bytes = html_path.stat().st_size
    run2_manifest_sha = sha256_file(manifest_path)

    if run1_html_sha != run2_html_sha or run1_manifest_sha != run2_manifest_sha:
        raise RuntimeError("Two-run rebuild parity mismatch!")

    a11y_report_path = ROOT / "evidence" / "N33_A11Y_REPORT.json"
    a11y_summary = run_cmd(["python3", "tools/check_a11y.py", "--json-out", str(a11y_report_path)])
    runtime_summary = run_cmd(["node", "tools/check_n31_runtime.js"])
    artifact_summary = run_cmd(["python3", "tools/check_artifact.py"])
    n22_comp_out = json.loads(run_cmd(["node", "tools/check_n22_components.js"]))
    n22_sem_out = json.loads(run_cmd(["node", "tools/check_n22_semantics.js"]))

    deliverables = [
        "data/keyboard_map.json",
        "src/focus.ts",
        "src/compiled/focus.js",
        "tools/check_a11y.py",
        "docs/SCREEN_READER_PROTOCOL.md",
        "src/smoke-subset.js",
        "output/simulator.html",
        "output/build-manifest.json",
        "evidence/N33_A11Y_REPORT.json",
    ]
    digests = {}
    for rel in deliverables:
        p = ROOT / rel
        digests[rel] = {
            "bytes": p.stat().st_size,
            "sha256": sha256_file(p),
        }

    corpus_record = {
        "schema_version": 1,
        "owner_task": "N33",
        "machine_status": "VERIFIED",
        "manual_protocol_status": "UNVERIFIED",
        "manual_protocol_path": "docs/SCREEN_READER_PROTOCOL.md",
        "two_run_parity": {
            "identical": True,
            "run1": {"html_bytes": run1_html_bytes, "html_sha256": run1_html_sha, "manifest_sha256": run1_manifest_sha},
            "run2": {"html_bytes": run2_html_bytes, "html_sha256": run2_html_sha, "manifest_sha256": run2_manifest_sha},
        },
        "checks": {
            "a11y_summary": a11y_summary,
            "runtime_summary": runtime_summary,
            "artifact_summary": artifact_summary,
            "n22_components_status": n22_comp_out.get("status"),
            "n22_semantics_status": n22_sem_out.get("status"),
        },
        "deliverables": digests,
    }

    out_path = ROOT / "evidence" / "N33_CORPUS_RECORD.json"
    out_path.write_text(json.dumps(corpus_record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"n33_corpus PASS: parity=True runtime=({runtime_summary}) out={out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
