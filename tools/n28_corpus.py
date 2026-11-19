#!/usr/bin/env python3
"""N28 corpus runner: Gate 24 remediation validation, runtime & loop-trace
determinism harness, privacy audit, double-build parity, byte accounting, and
two-invocation parity.

Writes:
  evidence/N28_VALIDATION_RECORD.json
  evidence/N28_RUNTIME_RECORD.json
  evidence/N28_LOOP_TRACE.json
  evidence/N28_PRIVACY_AUDIT.json
  evidence/N28_CORPUS_RECORD.json

Usage:
    python3 tools/n28_corpus.py [--out PATH] [--once]
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
GATE = ROOT / 'tools/validate_n28_remediation.py'
RUNTIME = ROOT / 'tools/check_n28_runtime.js'
BUILD = ROOT / 'tools/build.py'
MANIFEST = ROOT / 'output/build-manifest.json'
SIMULATOR = ROOT / 'output/simulator.html'
SMOKE_BASELINE_BYTES = 51817  # N27 baseline of src/smoke-subset.js

OUT_DEFAULT = ROOT / 'evidence/N28_CORPUS_RECORD.json'
VALIDATION_RECORD = ROOT / 'evidence/N28_VALIDATION_RECORD.json'
RUNTIME_RECORD = ROOT / 'evidence/N28_RUNTIME_RECORD.json'
LOOP_TRACE = ROOT / 'evidence/N28_LOOP_TRACE.json'
PRIVACY_AUDIT = ROOT / 'evidence/N28_PRIVACY_AUDIT.json'

DIGEST_FILES = [
    'data/remediation_policy.json',
    'data/analytics_schema.json',
    'data/terms.json',
    'src/remediation.ts',
    'src/compiled/remediation.js',
    'src/store.ts',
    'src/compiled/store.js',
    'src/analytics.ts',
    'src/compiled/analytics.js',
    'src/shell.html',
    'src/styles.css',
    'src/smoke-subset.js',
    'tools/validate_n28_remediation.py',
    'tools/check_n28_runtime.js',
    'tools/build.py',
    'tools/byte_budget.py',
    'tools/compile_n21_ts.py',
    'docs/REMEDIATION_FORMAT.md',
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
        rem_match = (
            (m1.get('remediation_layer') or {}).get('digest')
            == (m2.get('remediation_layer') or {}).get('digest')
        )
        return {
            'status': 'PASS' if (html_match and rem_match) else 'FAIL',
            'html_sha256_build1': sha256_file(out1),
            'html_sha256_build2': sha256_file(out2),
            'html_sha256_committed': sha256_file(SIMULATOR),
            'remediation_policy_digest': (m1.get('remediation_layer') or {}).get('digest'),
        }


def collect_once() -> dict[str, Any]:
    gate_run = _run_tool([sys.executable, str(GATE), '--report', str(VALIDATION_RECORD)], 'gate_24_remediation')
    runtime_run = _run_tool([
        'node', str(RUNTIME), '--repo-root', '.',
        '--record', str(RUNTIME_RECORD),
        '--trace-out', str(LOOP_TRACE),
        '--privacy-out', str(PRIVACY_AUDIT),
    ], 'runtime_and_loop_trace_harness')
    double_build = _double_build_parity()

    validation = json.loads(VALIDATION_RECORD.read_text(encoding='utf-8')) if VALIDATION_RECORD.exists() else {}
    runtime = json.loads(RUNTIME_RECORD.read_text(encoding='utf-8')) if RUNTIME_RECORD.exists() else {}
    trace = json.loads(LOOP_TRACE.read_text(encoding='utf-8')) if LOOP_TRACE.exists() else {}
    privacy = json.loads(PRIVACY_AUDIT.read_text(encoding='utf-8')) if PRIVACY_AUDIT.exists() else {}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}

    budgets = byte_budget.measure_budgets(manifest) if manifest else {'status': 'FAIL'}
    smoke_bytes = (ROOT / 'src/smoke-subset.js').stat().st_size
    remediation_layer = manifest.get('remediation_layer') or {}

    digests = {rel: sha256_file(ROOT / rel) for rel in DIGEST_FILES if (ROOT / rel).exists()}
    all_ok = (
        gate_run['status'] == 'PASS'
        and runtime_run['status'] == 'PASS'
        and double_build['status'] == 'PASS'
        and budgets.get('status') == 'PASS'
        and privacy.get('status') == 'PASS'
    )

    return {
        'schema_version': 1,
        'task': 'N28',
        'status': 'PASS' if all_ok else 'FAIL',
        'gates': {
            'gate_24_remediation': gate_run,
            'runtime_harness': runtime_run,
            'double_build_reproduction': double_build,
        },
        'validation_summary': {
            'policy_id': (validation.get('policy') or {}).get('policy_id'),
            'recommend_only': (validation.get('policy') or {}).get('recommend_only'),
            'resolution_mode': (validation.get('policy') or {}).get('resolution_mode'),
            'negative_fixtures': validation.get('negative_fixtures'),
            'terms_lint': validation.get('terms_lint'),
            'shell_touchpoints': validation.get('shell'),
            'ts_drift': validation.get('ts_drift'),
        },
        'runtime_checks': runtime.get('checks', {}),
        'loop_trace_summary': {
            'trace_id': trace.get('trace_id'),
            'steps_count': trace.get('steps_count'),
            'trace_digest': trace.get('trace_digest'),
            'final_queue_digest': trace.get('final_queue_digest'),
        },
        'privacy_audit_summary': {
            'status': privacy.get('status'),
            'storage_keys': privacy.get('storage_keys'),
            'remediation_queue_fields_count': len(privacy.get('remediation_queue_fields') or []),
            'memory_phase_writes': privacy.get('memory_phase_writes'),
            'keys_after_erase': privacy.get('keys_after_erase'),
        },
        'byte_accounting': {
            'budgets': budgets,
            'remediation_policy_island_bytes': remediation_layer.get('bytes'),
            'remediation_compacted_js_bytes': remediation_layer.get('remediation_compacted_js_bytes'),
            'smoke_delta_bytes': smoke_bytes - SMOKE_BASELINE_BYTES,
            're_budget_entries': [e for e in byte_budget.RE_BUDGET_HISTORY if e.get('task') == 'N28'],
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
    print(
        f"N28 corpus: {first['status']} "
        f"(double_build={first['gates']['double_build_reproduction']['status']}, "
        f"parity={first.get('two_invocation_parity', {}).get('status', 'single-run')})"
    )
    return 0 if first['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
