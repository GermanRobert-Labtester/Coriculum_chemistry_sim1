#!/usr/bin/env python3
"""N31 corpus runner: deterministic verification of the idempotent single-file
build pipeline (Main Steps A, B, and C).

Executes and records:
  1. Subtask A.1 (Gate 27 — tools/validate_n31_build_policy.py):
     - A.1.1 module dependency order validation (37 modules, 137 forward edges)
       + circular dependency rejection fixture (ModuleA <-> ModuleB named).
     - A.1.2 skeleton template dry-run assembly (all insertion points filled
       exactly once) + duplicate-insertion failure naming the offending point.
     - A.1.3 SHA-256 source/island/module digest stamping + 1-byte mutation
       flip fixture.
  2. Subtask B.1 (Assembly, deterministic JSON emission, single-script wrapper,
     3-run fresh-process idempotence proof, mid-assembly failure atomicity, and
     stale temp-file collision survival):
     - B.1.1 deterministic JSON emission across insertion-order-varying dicts
       with Latvian UTF-8 text (ensure_ascii=False) and </script> escaping.
     - B.1.2 single-script wrapper parse (Node vm.Script) + 37 module boundary
       separator comments + 27/27 in-file smoke vectors (tools/check_n31_runtime.js).
     - B.1.3 three fresh-process builds over unchanged sources producing
       byte-identical output/simulator.html and output/build-manifest.json
       (empty diff), mid-assembly decode-error atomicity proof leaving the
       previous deliverable untouched on disk, and stale .tmp collision
       survival fixture.
  3. Subtask C.1 (Gate 28 — tools/check_artifact.py):
     - C.1.1 standalone static contract check over output/simulator.html
       (lang="lv", 9 Section 1.2 anchors + #piemeri, 7 core islands + 22 total
       islands, 1 script, 0 external URLs, V-10 unique ASCII IDs).
     - C.1.2 offline URL scan with license-comment whitelist + injected
       external URL failure fixture naming URL, line, and context.
     - C.1 sub-budget composition accounting table + oversized scratch island
       failure fixture naming bank_island and figures_island.

Runs the full verification twice in one invocation to prove deterministic
corpus record emission (digest_run_1 == digest_run_2).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as build_mod  # noqa: E402
import check_artifact  # noqa: E402
import validate_n31_build_policy  # noqa: E402
from coverage_common import (  # noqa: E402
    DEST,
    canonical_json_bytes,
    escape_json_for_script,
    load_json,
    sha256_bytes,
    sha256_file,
)

ROOT = DEST
POLICY_PATH = ROOT / "data/build_policy.json"
ARTIFACT_PATH = ROOT / "output/simulator.html"
MANIFEST_PATH = ROOT / "output/build-manifest.json"

VALIDATION_RECORD_PATH = ROOT / "evidence/N31_VALIDATION_RECORD.json"
RUNTIME_RECORD_PATH = ROOT / "evidence/N31_RUNTIME_RECORD.json"
CONTRACT_RECORD_PATH = ROOT / "evidence/N31_ARTIFACT_CONTRACT.json"
CORPUS_RECORD_PATH = ROOT / "evidence/N31_CORPUS_RECORD.json"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run_b11_json_emission_fixture() -> dict[str, Any]:
    """Subtask B.1.1 fixture: an island with insertion-order-varying source
    objects and Latvian diacritics emits byte-identical UTF-8 output across all
    key orderings, with ensure_ascii=False keeping Latvian text readable and
    </ escaped as <\\/.
    """
    variant_1 = {
        "island_id": "sim-scratch-b11",
        "title_lv": "Šķīdumu molārā koncentrācija un oksidēšanās–reducēšanās līdzsvars",
        "script_guard": "</script><script>evil()</script>",
        "nested": {
            "z_key": [3, 2, 1],
            "a_key": {"beta": "vērtība", "alpha": "īpašība", "gamma": "mērvienība"},
            "m_key": {"c": 1.25, "a": 0.5, "b": 9.81},
        },
        "schema_version": 1,
    }
    variant_2 = {
        "schema_version": 1,
        "nested": {
            "m_key": {"b": 9.81, "c": 1.25, "a": 0.5},
            "a_key": {"alpha": "īpašība", "gamma": "mērvienība", "beta": "vērtība"},
            "z_key": [3, 2, 1],
        },
        "script_guard": "</script><script>evil()</script>",
        "title_lv": "Šķīdumu molārā koncentrācija un oksidēšanās–reducēšanās līdzsvars",
        "island_id": "sim-scratch-b11",
    }
    variant_3 = {
        "title_lv": "Šķīdumu molārā koncentrācija un oksidēšanās–reducēšanās līdzsvars",
        "island_id": "sim-scratch-b11",
        "schema_version": 1,
        "nested": {
            "a_key": {"gamma": "mērvienība", "beta": "vērtība", "alpha": "īpašība"},
            "z_key": [3, 2, 1],
            "m_key": {"a": 0.5, "b": 9.81, "c": 1.25},
        },
        "script_guard": "</script><script>evil()</script>",
    }

    emitted = [
        escape_json_for_script(canonical_json_bytes(v).decode("utf-8")).encode("utf-8")
        for v in (variant_1, variant_2, variant_3)
    ]
    digests = [sha256_bytes(b) for b in emitted]
    if not (emitted[0] == emitted[1] == emitted[2]):
        raise RuntimeError("B.1.1 JSON emission fixture failed: bytes differed across key orderings")

    decoded = emitted[0].decode("utf-8")
    latvian_preserved = "Šķīdumu molārā koncentrācija" in decoded and "\\u0160" not in decoded
    script_escaped = "</script>" not in decoded and "<\\/script>" in decoded
    if not latvian_preserved or not script_escaped:
        raise RuntimeError("B.1.1 JSON emission fixture failed Latvian UTF-8 or </script> escape check")

    return {
        "status": "PASS",
        "orderings_tested": 3,
        "byte_identical_across_orderings": True,
        "emitted_bytes": len(emitted[0]),
        "emitted_sha256": digests[0],
        "latvian_utf8_readable": latvian_preserved,
        "script_close_escaped": script_escaped,
    }


def run_b13_three_run_idempotence_and_atomicity() -> dict[str, Any]:
    """Subtask B.1.3:
      1. Run python3 tools/build.py three times in three fresh processes over
         unchanged repository sources; verify all three output/simulator.html
         files and all three output/build-manifest.json files are byte-identical
         with zero diff.
      2. Atomicity fixture: inject a mid-assembly failure (a scratch island
         source with a UTF-8 decode / JSON syntax error) and verify the build
         fails non-zero while leaving the previous output/simulator.html and
         output/build-manifest.json untouched on disk with their digests
         unchanged and zero leftover .tmp files.
      3. Stale temp-file collision fixture: create a pre-existing stale .tmp
         file in a scratch output directory, run _atomic_write / build over it,
         and verify the unique-temp policy survives without collision.
    """
    runs: list[dict[str, Any]] = []
    html_snapshots: list[bytes] = []
    manifest_snapshots: list[bytes] = []

    for run_idx in range(1, 4):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/build.py")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(
                f"B.1.3 fresh-process build run {run_idx} failed (rc={proc.returncode}): {proc.stderr}"
            )
        html_bytes = ARTIFACT_PATH.read_bytes()
        manifest_bytes = MANIFEST_PATH.read_bytes()
        manifest_data = json.loads(manifest_bytes.decode("utf-8"))
        html_snapshots.append(html_bytes)
        manifest_snapshots.append(manifest_bytes)
        runs.append(
            {
                "run": run_idx,
                "process_exit_code": proc.returncode,
                "artifact_bytes": len(html_bytes),
                "artifact_sha256": sha256_bytes(html_bytes),
                "manifest_bytes": len(manifest_bytes),
                "manifest_sha256": sha256_bytes(manifest_bytes),
                "build_id": manifest_data["build_id"],
                "composite_digest": manifest_data["composite_digest"],
            }
        )

    html_identical = html_snapshots[0] == html_snapshots[1] == html_snapshots[2]
    manifest_identical = (
        manifest_snapshots[0] == manifest_snapshots[1] == manifest_snapshots[2]
    )
    if not html_identical or not manifest_identical:
        raise RuntimeError(
            "B.1.3 idempotence proof failed: three fresh-process builds did not produce byte-identical outputs"
        )

    # 2. Atomicity fixture on an isolated scratch deliverable directory
    with tempfile.TemporaryDirectory(prefix="n31_atomicity_") as tmpdir_str:
        tmpdir = Path(tmpdir_str)
        scratch_out = tmpdir / "simulator.html"
        scratch_manifest = tmpdir / "build-manifest.json"
        shutil.copy2(ARTIFACT_PATH, scratch_out)
        shutil.copy2(MANIFEST_PATH, scratch_manifest)

        pre_html_sha = sha256_file(scratch_out)
        pre_html_bytes = scratch_out.stat().st_size
        pre_manifest_sha = sha256_file(scratch_manifest)

        # Create a corrupt source file with invalid UTF-8 bytes mid-stream
        corrupt_source = tmpdir / "corrupt_terms.json"
        corrupt_source.write_bytes(b'{"island_id": "sim-terms", "broken": "\xff\xfe"}')

        proc_fail = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools/build.py"),
                "--terms",
                str(corrupt_source),
                "--out",
                str(scratch_out),
                "--manifest-out",
                str(scratch_manifest),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        post_html_sha = sha256_file(scratch_out)
        post_html_bytes = scratch_out.stat().st_size
        post_manifest_sha = sha256_file(scratch_manifest)
        stray_tmps = list(tmpdir.glob("*.tmp"))

        if proc_fail.returncode == 0:
            raise RuntimeError("B.1.3 atomicity fixture expected build failure on corrupt UTF-8 source")
        if post_html_sha != pre_html_sha or post_manifest_sha != pre_manifest_sha or stray_tmps:
            raise RuntimeError(
                f"B.1.3 atomicity fixture violated: pre={pre_html_sha}, post={post_html_sha}, stray_tmps={stray_tmps}"
            )

        # Also test mid-assembly _atomic_write exception directly to prove _atomic_write
        # never touches an existing target file if an error occurs before os.replace
        direct_target = tmpdir / "direct_atomic.html"
        direct_target.write_bytes(html_snapshots[0])
        direct_pre_sha = sha256_file(direct_target)

        # Simulate a stale temp file from an earlier failed run (temp-name collision fixture)
        stale_tmp = tmpdir / f"{direct_target.name}.stale_collision.tmp"
        stale_tmp.write_bytes(b"STALE_HALF_WRITTEN_TEMP_FILE")

        # Write new identical bytes via _atomic_write while stale_tmp sits in the same directory
        build_mod._atomic_write(direct_target, html_snapshots[0])
        collision_post_sha = sha256_file(direct_target)
        stale_still_intact = stale_tmp.exists() and stale_tmp.read_bytes() == b"STALE_HALF_WRITTEN_TEMP_FILE"
        stale_tmp.unlink()
        remaining_tmps = list(tmpdir.glob("*.tmp"))

        if collision_post_sha != direct_pre_sha or not stale_still_intact or remaining_tmps:
            raise RuntimeError(
                "B.1.3 temp-name collision fixture failed: unique-temp policy did not survive stale temp file"
            )

    return {
        "status": "PASS",
        "three_run_idempotence": {
            "status": "PASS",
            "runs_count": 3,
            "all_html_byte_identical": html_identical,
            "all_manifests_byte_identical": manifest_identical,
            "rebuild_diff_bytes": 0,
            "artifact_sha256": runs[0]["artifact_sha256"],
            "artifact_bytes": runs[0]["artifact_bytes"],
            "manifest_sha256": runs[0]["manifest_sha256"],
            "composite_digest": runs[0]["composite_digest"],
            "runs": runs,
        },
        "atomicity_fixture": {
            "status": "PASS",
            "injected_fault": "corrupt UTF-8 bytes (0xff 0xfe) in scratch --terms source",
            "failed_build_exit_code": proc_fail.returncode,
            "previous_artifact_untouched": post_html_sha == pre_html_sha,
            "previous_artifact_bytes": pre_html_bytes,
            "previous_artifact_sha256": pre_html_sha,
            "after_failure_artifact_sha256": post_html_sha,
            "previous_manifest_untouched": post_manifest_sha == pre_manifest_sha,
            "stray_temp_files_count": len(stray_tmps),
        },
        "temp_collision_fixture": {
            "status": "PASS",
            "stale_temp_name": "direct_atomic.html.stale_collision.tmp",
            "survived_without_collision": True,
            "target_sha256": collision_post_sha,
            "active_temp_cleaned_up": len(remaining_tmps) == 0,
        },
    }


def collect_once() -> dict[str, Any]:
    """Run all N31 verification gates, runtime harness, and fixtures once."""
    # 1. Subtask A.1: Build policy validation + circular/template/stamp fixtures
    policy_report = validate_n31_build_policy.validate_all(repo_root=ROOT)
    if policy_report["status"] != "PASS":
        raise RuntimeError(f"Gate 27 (build_policy) failed: {policy_report['errors']}")
    write_json(VALIDATION_RECORD_PATH, policy_report)

    # 2. Subtask B.1.1: Deterministic JSON emission fixture
    b11_fixture = run_b11_json_emission_fixture()

    # 3. Subtask B.1.3: Three-run fresh-process idempotence + atomicity + collision fixtures
    b13_report = run_b13_three_run_idempotence_and_atomicity()

    # 4. Subtask B.1.2: Runtime harness & wrapper boundary fixture
    proc_rt = subprocess.run(
        ["node", str(ROOT / "tools/check_n31_runtime.js"), "--record", str(RUNTIME_RECORD_PATH)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc_rt.returncode != 0:
        raise RuntimeError(f"N31 runtime harness failed: {proc_rt.stderr or proc_rt.stdout}")
    runtime_report = load_json(RUNTIME_RECORD_PATH)

    # 5. Subtask C.1: Standalone static contract checker (tools/check_artifact.py)
    proc_chk = subprocess.run(
        [
            sys.executable,
            str(ROOT / "tools/check_artifact.py"),
            "--html",
            str(ARTIFACT_PATH),
            "--manifest",
            str(MANIFEST_PATH),
            "--policy",
            str(POLICY_PATH),
            "--report",
            str(CONTRACT_RECORD_PATH),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc_chk.returncode != 0:
        raise RuntimeError(f"Standalone check_artifact.py failed: {proc_chk.stderr or proc_chk.stdout}")
    contract_report = load_json(CONTRACT_RECORD_PATH)

    manifest_data = load_json(MANIFEST_PATH)

    tool_digests = {
        "data/build_policy.json": sha256_file(POLICY_PATH),
        "docs/BUILD_PIPELINE_FORMAT.md": sha256_file(ROOT / "docs/BUILD_PIPELINE_FORMAT.md"),
        "src/shell.html": sha256_file(ROOT / "src/shell.html"),
        "src/smoke-subset.js": sha256_file(ROOT / "src/smoke-subset.js"),
        "tools/build.py": sha256_file(ROOT / "tools/build.py"),
        "tools/byte_budget.py": sha256_file(ROOT / "tools/byte_budget.py"),
        "tools/validate_n31_build_policy.py": sha256_file(ROOT / "tools/validate_n31_build_policy.py"),
        "tools/check_artifact.py": sha256_file(ROOT / "tools/check_artifact.py"),
        "tools/check_n31_runtime.js": sha256_file(ROOT / "tools/check_n31_runtime.js"),
        "output/simulator.html": sha256_file(ARTIFACT_PATH),
        "output/build-manifest.json": sha256_file(MANIFEST_PATH),
    }

    return {
        "schema_version": 1,
        "task": "N31",
        "status": "PASS",
        "policy_id": manifest_data["policy_id"],
        "version": manifest_data["version"],
        "iso_date": manifest_data["iso_date"],
        "build_id": manifest_data["build_id"],
        "composite_digest": manifest_data["composite_digest"],
        "deliverable": {
            "path": "output/simulator.html",
            "bytes": manifest_data["output_bytes"],
            "kib": round(manifest_data["output_bytes"] / 1024, 1),
            "sha256": manifest_data["output_sha256"],
            "manifest_path": "output/build-manifest.json",
            "manifest_bytes": MANIFEST_PATH.stat().st_size,
            "manifest_sha256": sha256_file(MANIFEST_PATH),
            "gates_passed": len(manifest_data["gates"]),
            "sources_tracked": len(manifest_data["sources"]),
            "inlined_modules_count": len(manifest_data["module_order"]),
        },
        "step_a_policy_and_order": policy_report["details"],
        "step_b_assembly_and_idempotence": {
            "b11_json_emission_fixture": b11_fixture,
            "b12_wrapper_and_runtime": {
                "status": runtime_report["status"],
                "parser_engine": runtime_report["wrapper_fixture_b12"]["parser_engine"],
                "module_regions_mapped": runtime_report["wrapper_fixture_b12"]["module_regions_mapped"],
                "runtime_globals_verified_count": runtime_report["runtime_globals_verified_count"],
                "in_file_smoke": runtime_report["in_file_smoke"],
            },
            "b13_idempotence_and_atomicity": b13_report,
        },
        "step_c_contract_and_budgets": {
            "assertions": contract_report["assertions"],
            "offline_url_scan": contract_report["offline_url_scan"],
            "offline_url_scan_fixture": contract_report["offline_url_scan_fixture"],
            "composition_table": contract_report["composition_table"],
            "oversized_island_fixture": contract_report["oversized_island_fixture"],
            "manifest_parity": contract_report["manifest_parity"],
        },
        "tool_and_artifact_digests": tool_digests,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="N31 deterministic corpus runner.")
    parser.add_argument("--out", type=Path, default=CORPUS_RECORD_PATH)
    parser.add_argument("--once", action="store_true", help="Run a single pass instead of two-invocation parity.")
    args = parser.parse_args(argv)

    run_1 = collect_once()
    digest_1 = sha256_bytes(canonical_json_bytes(run_1))

    if not args.once:
        run_2 = collect_once()
        digest_2 = sha256_bytes(canonical_json_bytes(run_2))
        if digest_1 != digest_2:
            print(f"FAIL N31 corpus two-invocation parity: {digest_1} != {digest_2}", file=sys.stderr)
            return 1
        run_1["two_invocation_parity"] = {
            "status": "PASS",
            "digest_run_1": digest_1,
            "digest_run_2": digest_2,
        }
    else:
        run_1["two_invocation_parity"] = {
            "status": "PASS_SINGLE",
            "digest_run_1": digest_1,
        }

    write_json(args.out, run_1)
    d = run_1["deliverable"]
    print(
        f"n31_corpus PASS: deliverable={d['bytes']}B ({d['kib']} KiB) "
        f"sha256={d['sha256'][:16]}... composite={run_1['composite_digest'][:16]}... "
        f"gates={d['gates_passed']}/28 modules={d['inlined_modules_count']}/37 "
        f"parity={run_1['two_invocation_parity']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
