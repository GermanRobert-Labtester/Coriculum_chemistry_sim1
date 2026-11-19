#!/usr/bin/env python3
"""N28 build gate: remediation policy validation, negative policy & dangling-link
fixtures, N10 term-key lint, TypeScript drift guard, shell touchpoints, and
offline/no-wall-clock/no-endorsement/F10 source scan.

Usage:
    python3 tools/validate_n28_remediation.py --report evidence/N28_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_terms  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
POLICY_PATH = 'data/remediation_policy.json'
SHELL_PATH = 'src/shell.html'
REMEDIATION_TS_PATH = 'src/remediation.ts'
REMEDIATION_JS_PATH = 'src/compiled/remediation.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

ONE_CORRECT_EVIDENCE_VERBATIM = (
    'Viena pareiza atbilde ir pierādījums virzībai, nevis pilnīga apguve — '
    'apstipriniet pabeigšanu manuāli vai praktizējiet tālāk.'
)

REQUIRED_SHELL_IDS = [
    'sim-remediation-policy',
    'sim-remediation-error',
    'atskats-remediation-wrap',
    'atskats-remediation-heading',
    'atskats-remediation-honesty',
    'atskats-remediation-status',
    'atskats-remediation-list',
    'atskats-remediation-chain-host',
    'atskats-remediation-retry-host',
    'atskats-remediation-resolved-details',
    'atskats-remediation-resolved-summary',
    'atskats-remediation-resolved-list',
]
REQUIRED_PLACEHOLDERS = [
    '__REMEDIATION_POLICY_DIGEST__',
    '__SIM_REMEDIATION_POLICY_JSON__',
    '__REMEDIATION_JS__',
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
FORBIDDEN_ENDORSEMENT_RE = re.compile(
    r'\b(?:sertifik[aā]t\w*|akredit[eē]t\w*|ofici[aā]li\s+apstiprin\w*|garant[eē]\w*|lab[aā]k[aā]is|ofici[aā]l[aā]\s+atz[iī]me)\b',
    re.IGNORECASE,
)
F10_BANNED_EXPORTS = [
    'chart', 'charts', 'streak', 'streaks', 'gamification',
    'scoreHistory', 'score_history', 'dashboard', 'leaderboard',
]


def validate_policy_data(data: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {'status': 'FAIL', 'errors': ['Remediation policy must be a JSON object']}

    if data.get('island_id') != 'sim-remediation-policy':
        errors.append(f'island_id must be "sim-remediation-policy", got {data.get("island_id")!r}')
    if data.get('epistemic_label') != 'PROPOSED':
        errors.append('epistemic_label must be "PROPOSED"')
    if data.get('official_counterpart_status') != 'UNDETERMINED':
        errors.append('official_counterpart_status must be "UNDETERMINED"')
    if data.get('recommend_only') is not True:
        errors.append('recommend_only must be true (no forced remediation gating)')
    if data.get('regrade_original_attempt') is not False:
        errors.append('regrade_original_attempt must be false')
    if data.get('require_resolvable_links') is not True:
        errors.append('require_resolvable_links must be true')
    if not isinstance(data.get('honesty_note_lv'), str) or not data['honesty_note_lv'].strip():
        errors.append('Missing honesty_note_lv')

    dedup = data.get('deduplication')
    if not isinstance(dedup, dict) or dedup.get('key') != ['family_id', 'outcome_id']:
        errors.append('deduplication.key must be ["family_id", "outcome_id"]')
    elif dedup.get('resolved_resurrection') != 'open-new-entry':
        errors.append('deduplication.resolved_resurrection must be "open-new-entry"')

    rp = data.get('resolution_policy')
    if not isinstance(rp, dict):
        errors.append('resolution_policy must be an object')
    else:
        supported = rp.get('supported_modes')
        if not isinstance(supported, list) or 'confirm_required' not in supported or 'one_correct_resolves' not in supported:
            errors.append('resolution_policy.supported_modes must include confirm_required and one_correct_resolves')
        if rp.get('mode') not in (supported if isinstance(supported, list) else []):
            errors.append(f'resolution_policy.mode {rp.get("mode")!r} not in supported_modes')
        if rp.get('one_correct_evidence_copy_lv') != ONE_CORRECT_EVIDENCE_VERBATIM:
            errors.append('resolution_policy.one_correct_evidence_copy_lv must match verbatim policy copy')

    vs = data.get('variant_selection')
    if not isinstance(vs, dict) or not isinstance(vs.get('cycle_order'), list) or not vs['cycle_order']:
        errors.append('variant_selection.cycle_order must be non-empty')
    elif vs.get('never_reserve_failed_instance') is not True:
        errors.append('variant_selection.never_reserve_failed_instance must be true')

    states = data.get('states')
    if not isinstance(states, dict) or set(states.keys()) != {'open', 'retried', 'resolved'}:
        errors.append('states must declare exact keys open, retried, resolved')

    policy_text = json.dumps(data, ensure_ascii=False)
    for m in FORBIDDEN_ENDORSEMENT_RE.finditer(policy_text):
        errors.append(f'Forbidden endorsement/certification term in remediation policy: {m.group(0)!r}')
    if re.search(r'https?://', policy_text, re.IGNORECASE):
        errors.append('Remediation policy contains external URL')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'policy_id': data.get('policy_id'),
        'recommend_only': data.get('recommend_only'),
        'resolution_mode': (rp or {}).get('mode') if isinstance(rp, dict) else None,
        'deduplication_key': (dedup or {}).get('key') if isinstance(dedup, dict) else None,
        'errors': errors,
    }


def _check_negative_fixtures(repo_root: Path, valid_policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    scratch_forced = copy.deepcopy(valid_policy)
    scratch_forced['recommend_only'] = False
    rep_forced = validate_policy_data(scratch_forced)
    caught_forced = rep_forced['status'] == 'FAIL' and any('recommend_only' in e for e in rep_forced['errors'])
    if not caught_forced:
        errors.append('Scratch recommend_only=false fixture did not fail')

    scratch_regrade = copy.deepcopy(valid_policy)
    scratch_regrade['regrade_original_attempt'] = True
    rep_regrade = validate_policy_data(scratch_regrade)
    caught_regrade = rep_regrade['status'] == 'FAIL' and any('regrade_original_attempt' in e for e in rep_regrade['errors'])
    if not caught_regrade:
        errors.append('Scratch regrade_original_attempt=true fixture did not fail')

    scratch_mode = copy.deepcopy(valid_policy)
    scratch_mode['resolution_policy']['mode'] = 'unknown_mode'
    rep_mode = validate_policy_data(scratch_mode)
    caught_mode = rep_mode['status'] == 'FAIL' and any('unknown_mode' in e for e in rep_mode['errors'])
    if not caught_mode:
        errors.append('Scratch unsupported resolution mode fixture did not fail')

    js_probe = (
        "const R = require('./src/compiled/remediation.js'); "
        "const p = JSON.parse(process.argv[1]); "
        "const polRes = R.validatePolicy(p); "
        "let linkErr = null; "
        "try { R.validateLinks({ concept_ids: ['P9-99-DANGLING'], chain_ids: [] }, { concept_ids: { 'P1-01': true }, anchors_by_concept: {}, chain_ids: {}, method_cards: {} }, 'neg'); } "
        "catch (e) { linkErr = { code: e.code, message: e.message }; } "
        "process.stdout.write(JSON.stringify({ polRes, linkErr }));"
    )
    proc = subprocess.run(
        ['node', '-e', js_probe, json.dumps(scratch_forced)],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    js_ok = False
    js_out: dict[str, Any] = {}
    if proc.returncode == 0:
        js_out = json.loads(proc.stdout)
        js_pol = js_out.get('polRes') or {}
        js_link = js_out.get('linkErr') or {}
        js_ok = (
            js_pol.get('valid') is False
            and any('recommend_only' in e for e in js_pol.get('errors', []))
            and js_link.get('code') == 'E_REMEDIATION_DANGLING_LINK'
            and 'P9-99-DANGLING' in str(js_link.get('message', ''))
        )
    if not js_ok:
        errors.append('JS SimRemediation negative policy / dangling-link probe failed')

    return {
        'status': 'PASS' if (caught_forced and caught_regrade and caught_mode and js_ok) else 'FAIL',
        'forced_gating_rejected': caught_forced,
        'regrade_rejected': caught_regrade,
        'unsupported_mode_rejected': caught_mode,
        'js_negative_probe': js_out,
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    for mid in missing_ids:
        errors.append(f'{SHELL_PATH} missing N28 touchpoint #{mid}')
    missing_ph = [ph for ph in REQUIRED_PLACEHOLDERS if ph not in shell]
    for ph in missing_ph:
        errors.append(f'{SHELL_PATH} missing placeholder {ph}')
    return {
        'status': 'PASS' if (not missing_ids and not missing_ph) else 'FAIL',
        'required_ids_present': len(REQUIRED_SHELL_IDS) - len(missing_ids),
        'required_ids_total': len(REQUIRED_SHELL_IDS),
        'missing_ids': missing_ids,
        'missing_placeholders': missing_ph,
    }


def _check_sources(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    scanned: dict[str, Any] = {}
    for rel in (REMEDIATION_TS_PATH, REMEDIATION_JS_PATH):
        path = repo_root / rel
        if not path.exists():
            errors.append(f'Missing N28 module {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        net_hits = [label for pat, label in FORBIDDEN_NETWORK_PATTERNS if re.search(pat, text)]
        clk_hits = [label for pat, label in FORBIDDEN_CLOCK_PATTERNS if re.search(pat, text)]
        cert_hits = [m.group(0) for m in FORBIDDEN_ENDORSEMENT_RE.finditer(text)]
        if net_hits:
            errors.append(f'{rel} contains forbidden network references: {net_hits}')
        if clk_hits:
            errors.append(f'{rel} contains forbidden wall-clock calls: {clk_hits}')
        if cert_hits:
            errors.append(f'{rel} contains forbidden certification terms: {cert_hits}')
        scanned[rel] = {
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
            'network_hits': net_hits,
            'clock_hits': clk_hits,
            'certification_hits': cert_hits,
        }

    probe = "const r = require('./src/compiled/remediation.js'); process.stdout.write(JSON.stringify(Object.keys(r)));"
    proc = subprocess.run(['node', '-e', probe], cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append(f'Node export probe for remediation.js failed: {proc.stderr.strip()}')
    else:
        keys = json.loads(proc.stdout)
        banned = [k for k in keys if k in F10_BANNED_EXPORTS]
        if banned:
            errors.append(f'SimRemediation exports banned F10 symbols: {banned}')
        scanned['exports'] = keys
    return scanned


def run_gate(repo_root: Path = ROOT, policy_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    pol_file = policy_path or (repo_root / POLICY_PATH)

    compile_proc = subprocess.run(
        [sys.executable, str(repo_root / COMPILE_TOOL), '--check'],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    if compile_proc.returncode != 0:
        errors.append('TypeScript drift check failed: ' + (compile_proc.stderr.strip() or compile_proc.stdout.strip()))

    if not pol_file.exists():
        errors.append(f'Missing {POLICY_PATH}')
        policy_report: dict[str, Any] = {'status': 'FAIL', 'errors': [f'Missing {POLICY_PATH}']}
        negative_report: dict[str, Any] = {'status': 'FAIL'}
        pol_bytes = 0
        pol_digest = ''
        terms_lint: dict[str, Any] = {'status': 'FAIL'}
    else:
        policy_data = load_json(pol_file)
        policy_report = validate_policy_data(policy_data)
        errors.extend(policy_report['errors'])
        negative_report = _check_negative_fixtures(repo_root, policy_data, errors)
        canonical = canonical_json_bytes(policy_data)
        pol_bytes = len(canonical)
        pol_digest = sha256_bytes(canonical)
        terms_res = validate_terms.validate_all(repo_root=repo_root, extra_data_paths=[pol_file])
        terms_lint = {
            'status': terms_res['status'],
            'checked_term_keys': terms_res['lint']['checked_term_keys'],
            'errors': terms_res['errors'],
        }
        if terms_res['status'] != 'PASS':
            errors.extend(terms_res['errors'])

    shell_report = _check_shell(repo_root, errors)
    source_report = _check_sources(repo_root, errors)

    return {
        'schema_version': 1,
        'task': 'N28',
        'gate': 'remediation',
        'status': 'PASS' if not errors else 'FAIL',
        'policy': {
            **policy_report,
            'bytes': pol_bytes,
            'digest': pol_digest,
            'file_sha256': sha256_file(pol_file) if pol_file.exists() else None,
        },
        'negative_fixtures': negative_report,
        'terms_lint': terms_lint,
        'shell': shell_report,
        'sources': source_report,
        'ts_drift': 'PASS' if compile_proc.returncode == 0 else 'FAIL',
        'errors': errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(ROOT))
    parser.add_argument('--policy', default=None)
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    pol_path = Path(args.policy) if args.policy else None
    if pol_path and not pol_path.is_absolute():
        pol_path = repo_root / pol_path

    report = run_gate(repo_root=repo_root, policy_path=pol_path)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    print(
        f"N28 remediation gate: {report['status']} "
        f"(recommend_only={report['policy'].get('recommend_only')}, "
        f"terms={report['terms_lint'].get('status')}, "
        f"shell={report['shell'].get('required_ids_present')}/{report['shell'].get('required_ids_total')}, "
        f"ts_drift={report['ts_drift']})"
    )
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
