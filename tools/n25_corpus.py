#!/usr/bin/env python3
"""N25 corpus runner: validation gate, runtime & privacy harness, double-build
parity, byte accounting, and two-invocation parity.

Writes:
  evidence/N25_VALIDATION_RECORD.json
  evidence/N25_RUNTIME_RECORD.json
  evidence/N25_PRIVACY_AUDIT.json
  evidence/N25_CORPUS_RECORD.json

Usage:
    python3 tools/n25_corpus.py [--out PATH] [--once]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import byte_budget  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
GATE = ROOT / 'tools/validate_n25_analytics.py'
RUNTIME = ROOT / 'tools/check_n25_runtime.js'
BUILD = ROOT / 'tools/build.py'
MANIFEST = ROOT / 'output/build-manifest.json'
SIMULATOR = ROOT / 'output/simulator.html'
SMOKE_BASELINE_BYTES = 43790  # N24 baseline of src/smoke-subset.js (39224 + 4566)

OUT_DEFAULT = ROOT / 'evidence/N25_CORPUS_RECORD.json'
VALIDATION_RECORD = ROOT / 'evidence/N25_VALIDATION_RECORD.json'
RUNTIME_RECORD = ROOT / 'evidence/N25_RUNTIME_RECORD.json'
PRIVACY_RECORD = ROOT / 'evidence/N25_PRIVACY_AUDIT.json'

DIGEST_FILES = [
    'data/analytics_schema.json',
    'src/store.ts',
    'src/analytics.ts',
    'src/compiled/store.js',
    'src/compiled/analytics.js',
    'src/shell.html',
    'src/styles.css',
    'src/smoke-subset.js',
    'tools/validate_n25_analytics.py',
    'tools/check_n25_runtime.js',
    'tools/build.py',
    'tools/byte_budget.py',
    'tools/compile_n21_ts.py',
    'docs/ANALYTICS_STORE_FORMAT.md',
]


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _run_tool(command: list[str], label: str) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    return {
        'label': label,
        'command': ' '.join(command),
        'returncode': proc.returncode,
        'status': 'PASS' if proc.returncode == 0 else 'FAIL',
        'stdout': proc.stdout.strip()[:2000],
        'stderr': proc.stderr.strip()[:2000],
    }


def _double_build_parity() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
        out1 = Path(tmp1) / 'simulator.html'
        man1 = Path(tmp1) / 'build-manifest.json'
        out2 = Path(tmp2) / 'simulator.html'
        man2 = Path(tmp2) / 'build-manifest.json'
        r1 = subprocess.run(
            [sys.executable, str(BUILD), '--out', str(out1), '--manifest-out', str(man1)],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        r2 = subprocess.run(
            [sys.executable, str(BUILD), '--out', str(out2), '--manifest-out', str(man2)],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if r1.returncode != 0 or r2.returncode != 0:
            return {
                'status': 'FAIL',
                'build1_rc': r1.returncode,
                'build2_rc': r2.returncode,
                'stderr1': r1.stderr[-1000:],
                'stderr2': r2.stderr[-1000:],
            }
        m1 = json.loads(man1.read_text(encoding='utf-8'))
        m2 = json.loads(man2.read_text(encoding='utf-8'))
        html_match = sha256_file(out1) == sha256_file(out2) == sha256_file(SIMULATOR)
        analytics_match = (
            (m1.get('analytics_layer') or {}).get('digest')
            == (m2.get('analytics_layer') or {}).get('digest')
        )
        return {
            'status': 'PASS' if (html_match and analytics_match) else 'FAIL',
            'html_sha256_build1': sha256_file(out1),
            'html_sha256_build2': sha256_file(out2),
            'html_sha256_committed': sha256_file(SIMULATOR),
            'analytics_digest': (m1.get('analytics_layer') or {}).get('digest'),
        }


def collect_once() -> dict[str, Any]:
    gate_run = _run_tool([sys.executable, str(GATE), '--report', str(VALIDATION_RECORD)], 'gate_21_analytics')
    runtime_run = _run_tool([
        'node', str(RUNTIME), '--repo-root', '.',
        '--record', str(RUNTIME_RECORD), '--privacy-out', str(PRIVACY_RECORD),
    ], 'runtime_and_privacy_harness')
    double_build = _double_build_parity()

    validation = json.loads(VALIDATION_RECORD.read_text(encoding='utf-8')) if VALIDATION_RECORD.exists() else {}
    runtime = json.loads(RUNTIME_RECORD.read_text(encoding='utf-8')) if RUNTIME_RECORD.exists() else {}
    privacy = json.loads(PRIVACY_RECORD.read_text(encoding='utf-8')) if PRIVACY_RECORD.exists() else {}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}

    budgets = byte_budget.measure_budgets(manifest) if manifest else {'status': 'FAIL'}
    smoke_bytes = (ROOT / 'src/smoke-subset.js').stat().st_size
    analytics_layer = manifest.get('analytics_layer') or {}

    digests = {rel: sha256_file(ROOT / rel) for rel in DIGEST_FILES if (ROOT / rel).exists()}
    all_ok = (
        gate_run['status'] == 'PASS'
        and runtime_run['status'] == 'PASS'
        and double_build['status'] == 'PASS'
        and privacy.get('status') == 'PASS'
        and budgets.get('status') == 'PASS'
    )

    return {
        'schema_version': 1,
        'task': 'N25',
        'status': 'PASS' if all_ok else 'FAIL',
        'gates': {
            'gate_21_analytics': gate_run,
            'runtime_harness': runtime_run,
            'double_build_reproduction': double_build,
        },
        'validation_summary': {
            'schema_version': (validation.get('schema') or {}).get('schema_version'),
            'schema_bytes': (validation.get('schema') or {}).get('bytes'),
            'shell_touchpoints': validation.get('shell'),
            'ts_drift': validation.get('ts_drift'),
        },
        'runtime_checks': runtime.get('checks', {}),
        'privacy_summary': {
            'status': privacy.get('status'),
            'schema_keys': privacy.get('schema_keys'),
            'writes_during_memory_phase': privacy.get('writes_during_memory_phase'),
            'outlier_keys_count': len(privacy.get('outlier_keys') or []),
            'network_attempts_count': privacy.get('network_attempts_count'),
            'keys_after_erase': privacy.get('keys_after_erase'),
            'rogue_outlier_caught': privacy.get('rogue_outlier_caught'),
            'f10_banned_exports_found': privacy.get('f10_banned_exports_found'),
            'access_log_count': privacy.get('access_log_count'),
        },
        'byte_accounting': {
            'budgets': budgets,
            'analytics_island_bytes': analytics_layer.get('bytes'),
            'store_compacted_js_bytes': analytics_layer.get('store_compacted_js_bytes'),
            'analytics_compacted_js_bytes': analytics_layer.get('analytics_compacted_js_bytes'),
            'smoke_delta_bytes': smoke_bytes - SMOKE_BASELINE_BYTES,
            're_budget_entries': [e for e in byte_budget.RE_BUDGET_HISTORY if e.get('task') == 'N25'],
        },
        'digests': digests,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--once', action='store_true')
    args = parser.parse_args(argv)

    first = collect_once()
    if not args.once:
        second = collect_once()
        d1 = sha256_bytes(canonical_json_bytes(first))
        d2 = sha256_bytes(canonical_json_bytes(second))
        first['two_invocation_parity'] = {
            'status': 'PASS' if d1 == d2 else 'FAIL',
            'run1_sha256': d1,
            'run2_sha256': d2,
        }
        if d1 != d2:
            first['status'] = 'FAIL'

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    _write_json(out_path, first)
    print(f"N25 corpus: {first['status']} (double_build={first['gates']['double_build_reproduction']['status']}, "
          f"privacy={first['privacy_summary']['status']}, "
          f"parity={first.get('two_invocation_parity', {}).get('status', 'single-run')})")
    return 0 if first['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
