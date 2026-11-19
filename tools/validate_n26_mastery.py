#!/usr/bin/env python3
"""N26 build gate: mastery policy validation, unreachable-state corner fixture,
per-criterion mapping totality across all 28 families, TypeScript drift guard,
shell touchpoints, and offline/no-clock/no-certification lint.

Usage:
    python3 tools/validate_n26_mastery.py --report evidence/N26_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_bank import _collect_bank_files  # noqa: E402

ROOT = DEST
POLICY_PATH = 'data/mastery_policy.json'
COVERAGE_PATH = 'data/coverage.json'
BANK_DIR = 'data/bank'
SHELL_PATH = 'src/shell.html'
MASTERY_TS_PATH = 'src/mastery.ts'
MASTERY_JS_PATH = 'src/compiled/mastery.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

REQUIRED_STATES = ('unseen', 'learning', 'near_mastered', 'mastered', 'needs_review')
REQUIRED_THRESHOLDS = (
    'learning_to_near_mastered_streak',
    'near_mastered_to_mastered_streak',
    'needs_review_to_near_mastered_streak',
    'decay_inactivity_days',
    'decay_miss_count',
)
REQUIRED_SHELL_IDS = [
    'sim-mastery-policy',
    'sim-mastery-error',
    'prakse-mastery-panel',
    'prakse-mastery-honesty',
    'prakse-mastery-topics',
    'atskats-mastery-wrap',
    'atskats-mastery-heading',
    'atskats-mastery-honesty',
    'atskats-mastery-fresh-note',
    'atskats-mastery-summary',
    'atskats-mastery-topics',
]
REQUIRED_PLACEHOLDERS = [
    '__MASTERY_POLICY_DIGEST__',
    '__SIM_MASTERY_POLICY_JSON__',
    '__MASTERY_JS__',
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
    """Machine-validate a mastery policy dictionary, including state reachability."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return {'status': 'FAIL', 'errors': ['Mastery policy must be a JSON object'], 'unreachable_states': []}

    if data.get('island_id') != 'sim-mastery-policy':
        errors.append(f'island_id must be "sim-mastery-policy", got {data.get("island_id")!r}')
    if data.get('epistemic_label') != 'PROPOSED':
        errors.append('epistemic_label must be "PROPOSED"')
    if data.get('official_counterpart_status') != 'UNDETERMINED':
        errors.append('official_counterpart_status must be "UNDETERMINED"')
    if not isinstance(data.get('honesty_note_lv'), str) or not data['honesty_note_lv'].strip():
        errors.append('Missing honesty_note_lv')

    preds = data.get('predecessor_decisions')
    if not isinstance(preds, list) or len(preds) == 0:
        errors.append('Missing predecessor_decisions citations')

    thresholds = data.get('thresholds') or {}
    if not isinstance(thresholds, dict):
        errors.append('thresholds must be an object')
        thresholds = {}
    for key in REQUIRED_THRESHOLDS:
        entry = thresholds.get(key)
        if not isinstance(entry, dict):
            errors.append(f'Missing threshold "{key}"')
            continue
        val = entry.get('value')
        if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
            errors.append(f'Threshold "{key}" value must be a positive integer, got {val!r}')
        if entry.get('epistemic_label') != 'PROPOSED':
            errors.append(f'Threshold "{key}" must carry epistemic_label="PROPOSED"')

    raw_states = data.get('states')
    if not isinstance(raw_states, list):
        errors.append('states must be a list')
        raw_states = []

    by_id: dict[str, dict[str, Any]] = {}
    state_ids: list[str] = []
    icons_seen: set[str] = set()
    for idx, st in enumerate(raw_states):
        if not isinstance(st, dict) or not isinstance(st.get('id'), str) or not st['id']:
            errors.append(f'State at index {idx} missing valid id')
            continue
        sid = st['id']
        if sid in by_id:
            errors.append(f'Duplicate state id "{sid}"')
            continue
        by_id[sid] = st
        state_ids.append(sid)

    for req in REQUIRED_STATES:
        if req not in by_id:
            errors.append(f'Missing required state "{req}"')

    initial_state = data.get('initial_state')
    if not isinstance(initial_state, str) or initial_state not in by_id:
        errors.append(f'initial_state {initial_state!r} is not in declared states')

    adj: dict[str, list[str]] = {}
    for sid in state_ids:
        st = by_id[sid]
        adj[sid] = []
        label_lv = st.get('label_lv')
        icon = st.get('icon')
        if not isinstance(label_lv, str) or not label_lv.strip():
            errors.append(f'State "{sid}" missing label_lv')
        if not isinstance(icon, str) or not icon.strip():
            errors.append(f'State "{sid}" missing icon')
        elif icon in icons_seen:
            errors.append(f'State "{sid}" reuses icon {icon!r}; each state must have a distinct icon')
        else:
            icons_seen.add(icon)

        entry_rule = st.get('entry_rule')
        if not isinstance(entry_rule, dict) or entry_rule.get('kind') not in ('initial', 'transition'):
            errors.append(f'State "{sid}" missing valid entry_rule')
        elif entry_rule.get('kind') == 'transition':
            from_states = entry_rule.get('from_states')
            if not isinstance(from_states, list) or len(from_states) == 0:
                errors.append(f'State "{sid}" transition entry_rule needs non-empty from_states')
            else:
                for fs in from_states:
                    if fs not in by_id:
                        errors.append(f'State "{sid}" entry_rule references unknown state "{fs}"')

        exits = st.get('exit_paths')
        if not isinstance(exits, list) or len(exits) == 0:
            errors.append(f'State "{sid}" missing exit_paths')
        else:
            for ex in exits:
                if not isinstance(ex, dict) or ex.get('to_state') not in by_id:
                    errors.append(f'State "{sid}" exit_paths has invalid target {ex!r}')
                else:
                    adj[sid].append(ex['to_state'])

        reg = st.get('regression_rule')
        if not isinstance(reg, dict) or reg.get('to_state') not in by_id:
            errors.append(f'State "{sid}" missing valid regression_rule')
        else:
            adj[sid].append(reg['to_state'])

    # BFS reachability from initial_state
    reachable: set[str] = set()
    if isinstance(initial_state, str) and initial_state in by_id:
        q = deque([initial_state])
        reachable.add(initial_state)
        while q:
            cur = q.popleft()
            for nxt in adj.get(cur, []):
                if nxt not in reachable:
                    reachable.add(nxt)
                    q.append(nxt)

    unreachable = [sid for sid in state_ids if sid not in reachable]
    if unreachable:
        errors.append(f'Unreachable mastery states detected: {", ".join(unreachable)}')

    # Copy lint: no official certification / endorsement terms
    policy_text = json.dumps(data, ensure_ascii=False)
    for m in FORBIDDEN_ENDORSEMENT_RE.finditer(policy_text):
        errors.append(f'Forbidden endorsement/certification term in policy copy: {m.group(0)!r}')
    if re.search(r'https?://', policy_text, re.IGNORECASE):
        errors.append('Mastery policy contains external URL')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'policy_id': data.get('policy_id'),
        'states': state_ids,
        'reachable_states': [sid for sid in state_ids if sid in reachable],
        'unreachable_states': unreachable,
        'thresholds': {k: (thresholds.get(k) or {}).get('value') for k in REQUIRED_THRESHOLDS},
        'errors': errors,
    }


def _check_unreachable_fixtures(valid_policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    """Subtask A.1 corner-case fixtures: unreachable states & non-positive thresholds must fail by name."""
    # Case 1: Extra unreachable state 'stranded_vault'
    scratch_extra = copy.deepcopy(valid_policy)
    scratch_extra['states'].append({
        'id': 'stranded_vault',
        'order': 99,
        'label_lv': 'Iestrēdzis stāvoklis',
        'short_label_lv': 'Iestrēdzis',
        'icon': '✕',
        'entry_rule': {'kind': 'transition', 'from_states': ['mastered'], 'description_lv': 'Nav faktiskas pārejas.'},
        'exit_paths': [{'event': 'criterion_verdict', 'condition': 'correct', 'to_state': 'mastered'}],
        'regression_rule': {'event': 'incorrect', 'to_state': 'learning'},
    })
    rep1 = validate_policy_data(scratch_extra)
    caught_extra = (
        rep1['status'] == 'FAIL'
        and 'stranded_vault' in rep1['unreachable_states']
        and any('stranded_vault' in e for e in rep1['errors'])
    )
    if not caught_extra:
        errors.append('Unreachable-state scratch fixture (stranded_vault) did not fail with state named')

    # Case 2: Remove transitions into 'needs_review'
    scratch_cut = copy.deepcopy(valid_policy)
    for st in scratch_cut['states']:
        if st['id'] == 'mastered':
            st['exit_paths'] = [{'event': 'criterion_verdict', 'condition': 'correct', 'to_state': 'mastered'}]
            st['regression_rule'] = {'event': 'incorrect', 'to_state': 'near_mastered'}
    rep2 = validate_policy_data(scratch_cut)
    caught_cut = (
        rep2['status'] == 'FAIL'
        and 'needs_review' in rep2['unreachable_states']
        and any('needs_review' in e for e in rep2['errors'])
    )
    if not caught_cut:
        errors.append('Cut-edge scratch fixture (needs_review) did not fail with state named')

    # Case 3: Non-positive threshold
    scratch_zero = copy.deepcopy(valid_policy)
    scratch_zero['thresholds']['learning_to_near_mastered_streak']['value'] = 0
    rep3 = validate_policy_data(scratch_zero)
    caught_zero = rep3['status'] == 'FAIL' and any('learning_to_near_mastered_streak' in e for e in rep3['errors'])
    if not caught_zero:
        errors.append('Zero-threshold scratch fixture did not fail')

    return {
        'status': 'PASS' if (caught_extra and caught_cut and caught_zero) else 'FAIL',
        'extra_state_caught': {'caught': caught_extra, 'named': rep1['unreachable_states'], 'errors': rep1['errors']},
        'cut_edge_caught': {'caught': caught_cut, 'named': rep2['unreachable_states'], 'errors': rep2['errors']},
        'zero_threshold_caught': {'caught': caught_zero, 'errors': rep3['errors']},
    }


def _check_criterion_mapping(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    """Subtask A.1.2: prove every criterion across all 28 families resolves to >= 1 valid outcome id."""
    coverage = load_json(repo_root / COVERAGE_PATH)
    valid_outcomes = {o['id'] for o in coverage.get('outcomes', []) if isinstance(o, dict) and o.get('id')}

    bank_dir = repo_root / BANK_DIR
    questions: list[dict[str, Any]] = []
    for fp in _collect_bank_files(bank_dir):
        raw = load_json(fp)
        if isinstance(raw, dict) and isinstance(raw.get('questions'), list):
            questions.extend(raw['questions'])

    families_seen: set[str] = set()
    total_criteria = 0
    unmapped: list[dict[str, Any]] = []
    unknown_outcomes: list[dict[str, Any]] = []

    for q in questions:
        families_seen.add(q.get('family_id', ''))
        q_oids = [x for x in (q.get('outcome_ids') or []) if isinstance(x, str) and x]
        for cr in q.get('rubric', []):
            total_criteria += 1
            c_oids = [x for x in (cr.get('outcome_ids') or []) if isinstance(x, str) and x]
            resolved = c_oids if c_oids else q_oids
            if not resolved:
                unmapped.append({
                    'question_id': q.get('question_id'),
                    'family_id': q.get('family_id'),
                    'criterion_id': cr.get('criterion_id'),
                })
            else:
                bad = [oid for oid in resolved if oid not in valid_outcomes]
                if bad:
                    unknown_outcomes.append({
                        'question_id': q.get('question_id'),
                        'criterion_id': cr.get('criterion_id'),
                        'unknown': bad,
                    })

    if len(families_seen) != 28:
        errors.append(f'Expected 28 families in criterion mapping sweep, found {len(families_seen)}')
    if unmapped:
        errors.append(f'Unmapped criteria found: {unmapped[:5]}')
    if unknown_outcomes:
        errors.append(f'Criteria mapped to unknown coverage outcomes: {unknown_outcomes[:5]}')

    return {
        'status': 'PASS' if (len(families_seen) == 28 and not unmapped and not unknown_outcomes) else 'FAIL',
        'families_count': len(families_seen),
        'instances_count': len(questions),
        'criteria_count': total_criteria,
        'unmapped_count': len(unmapped),
        'unknown_outcomes_count': len(unknown_outcomes),
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    for mid in missing_ids:
        errors.append(f'{SHELL_PATH} missing N26 touchpoint #{mid}')
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
    for rel in (MASTERY_TS_PATH, MASTERY_JS_PATH):
        path = repo_root / rel
        if not path.exists():
            errors.append(f'Missing N26 module {rel}')
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

    probe = "const m = require('./src/compiled/mastery.js'); process.stdout.write(JSON.stringify(Object.keys(m)));"
    proc = subprocess.run(['node', '-e', probe], cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append(f'Node export probe for mastery.js failed: {proc.stderr.strip()}')
    else:
        keys = json.loads(proc.stdout)
        banned = [k for k in keys if k in F10_BANNED_EXPORTS]
        if banned:
            errors.append(f'SimMastery exports banned F10 symbols: {banned}')
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
        policy_data = {}
        policy_report = {'status': 'FAIL', 'errors': [f'Missing {POLICY_PATH}']}
        negative_report = {'status': 'FAIL'}
        pol_bytes = 0
        pol_digest = ''
    else:
        policy_data = load_json(pol_file)
        policy_report = validate_policy_data(policy_data)
        errors.extend(policy_report['errors'])
        negative_report = _check_unreachable_fixtures(policy_data, errors)
        canonical = canonical_json_bytes(policy_data)
        pol_bytes = len(canonical)
        pol_digest = sha256_bytes(canonical)

    mapping_report = _check_criterion_mapping(repo_root, errors)
    shell_report = _check_shell(repo_root, errors)
    source_report = _check_sources(repo_root, errors)

    return {
        'schema_version': 1,
        'task': 'N26',
        'gate': 'mastery',
        'status': 'PASS' if not errors else 'FAIL',
        'policy': {
            **policy_report,
            'bytes': pol_bytes,
            'digest': pol_digest,
            'file_sha256': sha256_file(pol_file) if pol_file.exists() else None,
        },
        'negative_fixtures': negative_report,
        'criterion_mapping': mapping_report,
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
        f"N26 mastery gate: {report['status']} "
        f"(states={len(report['policy'].get('states') or [])}, "
        f"criteria={report['criterion_mapping'].get('criteria_count')}, "
        f"shell={report['shell'].get('required_ids_present')}/{report['shell'].get('required_ids_total')}, "
        f"ts_drift={report['ts_drift']})"
    )
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
