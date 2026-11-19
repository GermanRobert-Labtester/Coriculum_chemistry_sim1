#!/usr/bin/env python3
"""N27 build gate: Leitner box-interval policy validation, non-increasing interval
negative fixtures, N10 term-key lint, TypeScript drift guard, shell touchpoints,
and offline/no-wall-clock/no-third-party-algorithm/F10 lint.

Usage:
    python3 tools/validate_n27_scheduler.py --report evidence/N27_VALIDATION_RECORD.json
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
POLICY_PATH = 'data/scheduler_policy.json'
SHELL_PATH = 'src/shell.html'
SCHEDULER_TS_PATH = 'src/scheduler.ts'
SCHEDULER_JS_PATH = 'src/compiled/scheduler.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

REQUIRED_STATES = ('unseen', 'learning', 'near_mastered', 'mastered', 'needs_review')
REQUIRED_REASONS = ('overdue', 'due_today', 'new', 'least_recently_practiced', 'unavailable')
REQUIRED_SHELL_IDS = [
    'sim-scheduler-policy',
    'sim-scheduler-error',
    'prakse-scheduler-panel',
    'prakse-scheduler-heading',
    'prakse-scheduler-honesty',
    'prakse-scheduler-status',
    'prakse-scheduler-queue',
    'prakse-scheduler-topics',
    'prakse-scheduler-handoff',
]
REQUIRED_PLACEHOLDERS = [
    '__SCHEDULER_POLICY_DIGEST__',
    '__SIM_SCHEDULER_POLICY_JSON__',
    '__SCHEDULER_JS__',
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


def _is_pos_int(val: Any) -> bool:
    return isinstance(val, int) and not isinstance(val, bool) and val > 0


def validate_policy_data(data: Any) -> dict[str, Any]:
    """Validate the Leitner box-interval artifact and selection policy."""
    errors: list[str] = []
    non_inc: list[dict[str, Any]] = []
    if not isinstance(data, dict):
        return {
            'status': 'FAIL',
            'errors': ['Scheduler policy must be a JSON object'],
            'non_increasing_pairs': [],
        }

    if data.get('island_id') != 'sim-scheduler-policy':
        errors.append(f'island_id must be "sim-scheduler-policy", got {data.get("island_id")!r}')
    if data.get('epistemic_label') != 'PROPOSED':
        errors.append('epistemic_label must be "PROPOSED"')
    if data.get('official_counterpart_status') != 'UNDETERMINED':
        errors.append('official_counterpart_status must be "UNDETERMINED"')
    if not isinstance(data.get('honesty_note_lv'), str) or not data['honesty_note_lv'].strip():
        errors.append('Missing honesty_note_lv')

    preds = data.get('predecessor_decisions')
    if not isinstance(preds, list) or len(preds) == 0:
        errors.append('Missing predecessor_decisions citations')

    qcap = data.get('queue_cap')
    qcap_val = qcap.get('value') if isinstance(qcap, dict) else None
    if not _is_pos_int(qcap_val):
        errors.append(f'queue_cap.value must be a positive integer, got {qcap_val!r}')
    elif qcap.get('epistemic_label') != 'PROPOSED':
        errors.append('queue_cap must carry epistemic_label="PROPOSED"')

    raw_boxes = data.get('boxes')
    if not isinstance(raw_boxes, list) or len(raw_boxes) < 2:
        errors.append('boxes must be a list of at least 2 Leitner boxes')
        raw_boxes = []

    by_box: dict[int, dict[str, Any]] = {}
    boxes_sorted: list[dict[str, Any]] = []
    for idx, b in enumerate(raw_boxes):
        if not isinstance(b, dict) or not _is_pos_int(b.get('box')):
            errors.append(f'Box at index {idx} missing positive integer box number')
            continue
        bnum = b['box']
        if bnum in by_box:
            errors.append(f'Duplicate box number {bnum}')
            continue
        if not _is_pos_int(b.get('interval_days')):
            errors.append(f'Box {bnum} interval_days must be a positive integer, got {b.get("interval_days")!r}')
        if b.get('epistemic_label') != 'PROPOSED':
            errors.append(f'Box {bnum} must carry epistemic_label="PROPOSED"')
        if not isinstance(b.get('label_key'), str) or not b['label_key'].strip():
            errors.append(f'Box {bnum} missing label_key')
        by_box[bnum] = b
        boxes_sorted.append(b)

    boxes_sorted.sort(key=lambda item: item['box'])
    for idx, b in enumerate(boxes_sorted):
        if b['box'] != idx + 1:
            errors.append(f'Box numbers must be contiguous starting at 1 (found box {b["box"]} at index {idx})')
        if idx > 0:
            prev = boxes_sorted[idx - 1]
            p_days = prev.get('interval_days')
            c_days = b.get('interval_days')
            if isinstance(p_days, int) and isinstance(c_days, int) and not (c_days > p_days):
                non_inc.append({
                    'lower_box': prev['box'],
                    'upper_box': b['box'],
                    'lower_days': p_days,
                    'upper_days': c_days,
                })
                errors.append(
                    f'Non-increasing interval pair between box {prev["box"]} ({p_days}d) '
                    f'and box {b["box"]} ({c_days}d); intervals must strictly increase with box number'
                )

    state_to_box = data.get('state_to_box')
    if not isinstance(state_to_box, dict):
        errors.append('state_to_box must be an object')
        state_to_box = {}
    for sid in REQUIRED_STATES:
        bnum = state_to_box.get(sid)
        if not _is_pos_int(bnum) or bnum not in by_box:
            errors.append(f'Mastery state "{sid}" missing valid mapping in state_to_box')
        else:
            mstates = by_box[bnum].get('mastery_states') or []
            if sid not in mstates:
                errors.append(f'State "{sid}" maps to box {bnum} but is absent from box {bnum}.mastery_states')

    if state_to_box.get('needs_review') != 1:
        errors.append(f'needs_review must map to early box 1, got {state_to_box.get("needs_review")!r}')

    sel_rule = data.get('selection_rule')
    if not isinstance(sel_rule, dict) or sel_rule.get('epistemic_label') != 'PROPOSED':
        errors.append('selection_rule must be an object with epistemic_label="PROPOSED"')
    elif not isinstance(sel_rule.get('tie_break'), str) or 'outcome_id' not in sel_rule['tie_break']:
        errors.append('selection_rule.tie_break must declare deterministic outcome_id ordering')

    rt = data.get('reason_templates')
    if not isinstance(rt, dict):
        errors.append('reason_templates must be an object')
        rt = {}
    for rc in REQUIRED_REASONS:
        item = rt.get(rc)
        if not isinstance(item, dict) or not isinstance(item.get('term_key'), str) or not item['term_key'].strip():
            errors.append(f'reason_templates.{rc} missing term_key')

    policy_text = json.dumps(data, ensure_ascii=False)
    for m in FORBIDDEN_ENDORSEMENT_RE.finditer(policy_text):
        errors.append(f'Forbidden endorsement/certification term in scheduler policy: {m.group(0)!r}')
    if re.search(r'https?://', policy_text, re.IGNORECASE):
        errors.append('Scheduler policy contains external URL')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'policy_id': data.get('policy_id'),
        'queue_cap': qcap_val,
        'boxes': [{'box': b['box'], 'role': b.get('role'), 'interval_days': b.get('interval_days')} for b in boxes_sorted],
        'state_to_box': state_to_box,
        'non_increasing_pairs': non_inc,
        'errors': errors,
    }


def _check_negative_fixtures(repo_root: Path, valid_policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    """Subtask A.1.1: non-increasing interval pair must fail naming both boxes (Py & JS)."""
    # Case 1: Box 2 interval == Box 1 interval (1d, 1d)
    scratch_equal = copy.deepcopy(valid_policy)
    scratch_equal['boxes'][1]['interval_days'] = 1
    rep_equal = validate_policy_data(scratch_equal)
    caught_equal = (
        rep_equal['status'] == 'FAIL'
        and len(rep_equal['non_increasing_pairs']) == 1
        and any('box 1' in e and 'box 2' in e for e in rep_equal['errors'])
    )
    if not caught_equal:
        errors.append('Scratch equal-interval fixture (box 1, box 2) did not fail naming both boxes')

    # Case 2: Box 3 interval < Box 2 interval (3d, 2d)
    scratch_inv = copy.deepcopy(valid_policy)
    scratch_inv['boxes'][2]['interval_days'] = 2
    rep_inv = validate_policy_data(scratch_inv)
    caught_inv = (
        rep_inv['status'] == 'FAIL'
        and len(rep_inv['non_increasing_pairs']) == 1
        and any('box 2' in e and 'box 3' in e for e in rep_inv['errors'])
    )
    if not caught_inv:
        errors.append('Scratch decreasing-interval fixture (box 2, box 3) did not fail naming both boxes')

    # Case 3: Missing mastery state mapping
    scratch_missing_state = copy.deepcopy(valid_policy)
    del scratch_missing_state['state_to_box']['needs_review']
    rep_missing = validate_policy_data(scratch_missing_state)
    caught_missing = rep_missing['status'] == 'FAIL' and any('needs_review' in e for e in rep_missing['errors'])
    if not caught_missing:
        errors.append('Scratch missing-state fixture (needs_review) did not fail')

    # Case 4: Non-positive queue cap
    scratch_cap = copy.deepcopy(valid_policy)
    scratch_cap['queue_cap']['value'] = 0
    rep_cap = validate_policy_data(scratch_cap)
    caught_cap = rep_cap['status'] == 'FAIL' and any('queue_cap' in e for e in rep_cap['errors'])
    if not caught_cap:
        errors.append('Scratch zero queue_cap fixture did not fail')

    # Case 5: JS validatePolicy agrees on scratch_inv
    js_probe = (
        "const S = require('./src/compiled/scheduler.js'); "
        "const p = JSON.parse(process.argv[1]); "
        "process.stdout.write(JSON.stringify(S.validatePolicy(p)));"
    )
    proc = subprocess.run(
        ['node', '-e', js_probe, json.dumps(scratch_inv)],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    js_caught = False
    js_rep: dict[str, Any] = {}
    if proc.returncode == 0:
        js_rep = json.loads(proc.stdout)
        js_caught = (
            js_rep.get('valid') is False
            and any('box 2' in e and 'box 3' in e for e in js_rep.get('errors', []))
        )
    if not js_caught:
        errors.append('JS SimScheduler.validatePolicy did not catch non-increasing box 2 / box 3 fixture')

    return {
        'status': 'PASS' if (caught_equal and caught_inv and caught_missing and caught_cap and js_caught) else 'FAIL',
        'equal_pair_box1_box2': {'caught': caught_equal, 'errors': rep_equal['errors']},
        'decreasing_pair_box2_box3': {'caught': caught_inv, 'errors': rep_inv['errors']},
        'missing_state_needs_review': {'caught': caught_missing, 'errors': rep_missing['errors']},
        'zero_queue_cap': {'caught': caught_cap, 'errors': rep_cap['errors']},
        'js_decreasing_pair': {'caught': js_caught, 'errors': js_rep.get('errors', [])},
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    for mid in missing_ids:
        errors.append(f'{SHELL_PATH} missing N27 touchpoint #{mid}')
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
    for rel in (SCHEDULER_TS_PATH, SCHEDULER_JS_PATH):
        path = repo_root / rel
        if not path.exists():
            errors.append(f'Missing N27 module {rel}')
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

    probe = "const s = require('./src/compiled/scheduler.js'); process.stdout.write(JSON.stringify(Object.keys(s)));"
    proc = subprocess.run(['node', '-e', probe], cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append(f'Node export probe for scheduler.js failed: {proc.stderr.strip()}')
    else:
        keys = json.loads(proc.stdout)
        banned = [k for k in keys if k in F10_BANNED_EXPORTS]
        if banned:
            errors.append(f'SimScheduler exports banned F10 symbols: {banned}')
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
        policy_data: dict[str, Any] = {}
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
        'task': 'N27',
        'gate': 'scheduler',
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
        f"N27 scheduler gate: {report['status']} "
        f"(boxes={len(report['policy'].get('boxes') or [])}, "
        f"cap={report['policy'].get('queue_cap')}, "
        f"terms={report['terms_lint'].get('status')}, "
        f"shell={report['shell'].get('required_ids_present')}/{report['shell'].get('required_ids_total')}, "
        f"ts_drift={report['ts_drift']})"
    )
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
