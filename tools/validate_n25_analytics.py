#!/usr/bin/env python3
"""N25 build gate: local store schema, analytics contract, F10 boundary,
TypeScript compile parity, shell touchpoints, and offline/no-network source scan.

This gate is the build's N25 checkpoint (order 21, owner N25). It refuses the
build when:
- data/analytics_schema.json is missing, invalid, or lacks the F10 rejection
  boundary or required Latvian copy;
- src/compiled/store.js or src/compiled/analytics.js has drifted from TypeScript;
- src/shell.html is missing #atskats or #iestatijumi N25 touchpoints or
  __SIM_ANALYTICS_JSON__ / __STORE_JS__ / __ANALYTICS_JS__ placeholders;
- src/store.ts or src/analytics.ts references network APIs, external URLs,
  wall-clock Date.now()/performance.now(), or exports F10 chart/streak symbols.

Usage:
    python3 tools/validate_n25_analytics.py --report evidence/N25_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
SCHEMA_PATH = 'data/analytics_schema.json'
SHELL_PATH = 'src/shell.html'
STORE_TS_PATH = 'src/store.ts'
ANALYTICS_TS_PATH = 'src/analytics.ts'
STORE_JS_PATH = 'src/compiled/store.js'
ANALYTICS_JS_PATH = 'src/compiled/analytics.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

REQUIRED_SHELL_IDS = [
    'atskats',
    'atskats-honesty-note',
    'atskats-storage-notice',
    'atskats-zero-notice',
    'atskats-summary',
    'atskats-sessions-count',
    'atskats-outcomes-correct',
    'atskats-outcomes-first-pass',
    'atskats-remediation-count',
    'atskats-topics-table',
    'atskats-topics-body',
    'atskats-forms-list',
    'atskats-remediation-list',
    'atskats-outcomes-list',
    'settings-storage-slot',
    'store-consent-copy',
    'store-opt-in-toggle',
    'store-status',
    'store-notice',
    'store-export-btn',
    'store-export-status',
    'store-erase-request',
    'store-erase-confirm-box',
    'store-erase-prompt',
    'store-erase-confirm',
    'store-erase-cancel',
    'sim-analytics',
]

REQUIRED_COPY_KEYS = [
    'consent_title',
    'consent_body',
    'opt_in_enable_label',
    'opt_in_disable_label',
    'disabled_state_notice',
    'enabled_state_notice',
    'newer_version_notice',
    'migrated_v1_notice',
    'corrupt_store_notice',
    'storage_degraded_notice',
    'export_label',
    'export_ready_notice',
    'erase_request_label',
    'erase_confirm_prompt',
    'erase_confirm_label',
    'erase_cancel_label',
    'erase_done_notice',
    'honesty_banner',
    'zero_activity_notice',
]

FORBIDDEN_NETWORK_PATTERNS = [
    (r'\bfetch\s*\(', 'fetch()'),
    (r'\bXMLHttpRequest\b', 'XMLHttpRequest'),
    (r'\bWebSocket\b', 'WebSocket'),
    (r'\bsendBeacon\b', 'sendBeacon'),
    (r'https?://', 'external URL'),
]

FORBIDDEN_CLOCK_PATTERNS = [
    (r'\bDate\.now\s*\(', 'Date.now()'),
    (r'\bperformance\.now\s*\(', 'performance.now()'),
]

F10_BANNED_EXPORTS = [
    'chart', 'charts', 'streak', 'streaks', 'gamification',
    'scoreHistory', 'score_history', 'dashboard', 'leaderboard',
]


def _check_schema(schema_file: Path, errors: list[str]) -> dict[str, Any]:
    if not schema_file.exists():
        errors.append(f'Missing {SCHEMA_PATH}')
        return {'status': 'FAIL'}
    raw_text = schema_file.read_text(encoding='utf-8')
    if re.search(r'https?://', raw_text, re.IGNORECASE):
        errors.append(f'{SCHEMA_PATH} contains external URL')
    data = load_json(schema_file)
    if data.get('island_id') != 'sim-analytics':
        errors.append(f'{SCHEMA_PATH}: island_id must be "sim-analytics"')
    if data.get('schema_version') != 2:
        errors.append(f'{SCHEMA_PATH}: schema_version must be 2')
    sc = data.get('store_contract') or {}
    if sc.get('storage_keys') != ['sim_colloq1_store_v2']:
        errors.append(f'{SCHEMA_PATH}: storage_keys must be ["sim_colloq1_store_v2"]')
    if not isinstance(sc.get('max_events'), int) or sc.get('max_events') <= 0:
        errors.append(f'{SCHEMA_PATH}: max_events must be a positive integer')
    if sc.get('default_mode') != 'memory':
        errors.append(f'{SCHEMA_PATH}: default_mode must be "memory"')
    ec = data.get('event_contract') or {}
    if ec.get('event_types') != ['session-completed', 'task-answered', 'remediation-state']:
        errors.append(f'{SCHEMA_PATH}: event_types mismatch')
    f10 = data.get('f10_boundary') or {}
    if f10.get('rejected_feature') != 'F10' or f10.get('status') != 'rejected-by-policy':
        errors.append(f'{SCHEMA_PATH}: f10_boundary must record F10 rejected-by-policy')
    copy_lv = data.get('copy_lv') or {}
    missing_copy = [k for k in REQUIRED_COPY_KEYS if not isinstance(copy_lv.get(k), str) or not copy_lv[k].strip()]
    if missing_copy:
        errors.append(f'{SCHEMA_PATH}: missing copy_lv keys {missing_copy}')
    canonical = canonical_json_bytes(data)
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'schema_version': data.get('schema_version'),
        'storage_keys': sc.get('storage_keys'),
        'max_events': sc.get('max_events'),
        'bytes': len(canonical),
        'digest': sha256_bytes(canonical),
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    for mid in missing:
        errors.append(f'{SHELL_PATH} missing N25 touchpoint #{mid}')
    for ph in ('__ANALYTICS_DIGEST__', '__SIM_ANALYTICS_JSON__', '__STORE_JS__', '__ANALYTICS_JS__'):
        if ph not in shell:
            errors.append(f'{SHELL_PATH} missing placeholder {ph}')
    atskats_m = re.search(r'<section id="atskats"[\s\S]*?</section>', shell)
    if atskats_m and '<canvas' in atskats_m.group(0).lower():
        errors.append('#atskats must not contain <canvas> (F10 rejected)')
    return {
        'status': 'PASS' if not missing else 'FAIL',
        'required_ids_present': len(REQUIRED_SHELL_IDS) - len(missing),
        'required_ids_total': len(REQUIRED_SHELL_IDS),
        'missing_ids': missing,
    }


def _check_sources(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    scanned: dict[str, Any] = {}
    for rel in (STORE_TS_PATH, ANALYTICS_TS_PATH, STORE_JS_PATH, ANALYTICS_JS_PATH):
        path = repo_root / rel
        if not path.exists():
            errors.append(f'Missing N25 module {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        net_hits = [label for pat, label in FORBIDDEN_NETWORK_PATTERNS if re.search(pat, text)]
        clk_hits = [label for pat, label in FORBIDDEN_CLOCK_PATTERNS if re.search(pat, text)]
        if net_hits:
            errors.append(f'{rel} contains forbidden network references: {net_hits}')
        if clk_hits:
            errors.append(f'{rel} contains forbidden wall-clock calls: {clk_hits}')
        scanned[rel] = {
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
            'network_hits': net_hits,
            'clock_hits': clk_hits,
        }

    # Check compiled JS exports for F10 banned symbols
    js_probe = """
const st = require('./src/compiled/store.js');
const an = require('./src/compiled/analytics.js');
process.stdout.write(JSON.stringify({
  store_keys: Object.keys(st),
  analytics_keys: Object.keys(an),
  f10: an.F10_BOUNDARY || null
}));
"""
    proc = subprocess.run(['node', '-e', js_probe], cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append(f'Node export probe failed: {proc.stderr.strip()}')
    else:
        info = json.loads(proc.stdout)
        banned_found = [k for k in info['analytics_keys'] if k in F10_BANNED_EXPORTS]
        if banned_found:
            errors.append(f'SimAnalytics exports banned F10 symbols: {banned_found}')
        if not info.get('f10') or info['f10'].get('status') != 'rejected-by-policy':
            errors.append('SimAnalytics.F10_BOUNDARY missing or not rejected-by-policy')
        scanned['exports'] = info
    return scanned


def run_gate(repo_root: Path = ROOT, schema_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    schema_file = schema_path or (repo_root / SCHEMA_PATH)

    compile_proc = subprocess.run(
        [sys.executable, str(repo_root / COMPILE_TOOL), '--check'],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    if compile_proc.returncode != 0:
        errors.append('TypeScript drift check failed: ' + (compile_proc.stderr.strip() or compile_proc.stdout.strip()))

    schema_report = _check_schema(schema_file, errors)
    shell_report = _check_shell(repo_root, errors)
    source_report = _check_sources(repo_root, errors)

    return {
        'schema_version': 1,
        'task': 'N25',
        'gate': 'analytics',
        'status': 'PASS' if not errors else 'FAIL',
        'schema': schema_report,
        'shell': shell_report,
        'sources': source_report,
        'ts_drift': 'PASS' if compile_proc.returncode == 0 else 'FAIL',
        'errors': errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(ROOT))
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    report = run_gate(repo_root=repo_root)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f"N25 analytics gate: {report['status']} (schema={report['schema'].get('bytes')}B, "
          f"shell={report['shell'].get('required_ids_present')}/{report['shell'].get('required_ids_total')}, "
          f"ts_drift={report['ts_drift']})")
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
