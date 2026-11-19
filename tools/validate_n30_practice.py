#!/usr/bin/env python3
"""N30 build gate: bounded practice path policy validation against live N20
eligible counts and the 18-type registry, negative scratch fixtures (overlong
topic length & unknown response type), N10 term-key & copy lint, TypeScript
drift guard, shell touchpoints, and offline/no-wall-clock/F10 source scan.

Usage:
    python3 tools/validate_n30_practice.py --report evidence/N30_VALIDATION_RECORD.json
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
POLICY_PATH = 'data/practice_policy.json'
RESPONSE_TYPES_PATH = 'data/response_types.json'
TERMS_PATH = 'data/terms.json'
COVERAGE_PATH = 'data/coverage.json'
BANK_DIR = 'data/bank'
SHELL_PATH = 'src/shell.html'
PRACTICE_TS_PATH = 'src/practice.ts'
PRACTICE_JS_PATH = 'src/compiled/practice.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

REQUIRED_SHELL_IDS = [
    'sim-practice-policy',
    'prakse-practice-wrap',
    'prakse-practice-heading',
    'prakse-practice-honesty',
    'prakse-error',
    'prakse-filters',
    'prakse-filter-type',
    'prakse-filter-unattempted',
    'prakse-topics-grid',
    'prakse-tema-1',
    'prakse-tema-2',
    'prakse-tema-3',
    'prakse-tema-4',
    'prakse-tema-5',
    'prakse-tema-6',
    'prakse-tema-7',
    'prakse-runner',
    'prakse-runner-progress',
    'prakse-shortage-banner',
    'prakse-exhausted-panel',
    'prakse-runner-item-host',
    'prakse-help-slot',
    'prakse-runner-chain-host',
    'prakse-runner-term-host',
    'prakse-runner-feedback',
    'prakse-submit-btn',
    'prakse-skip-btn',
    'prakse-next-btn',
    'prakse-end-btn',
    'prakse-summary',
]
REQUIRED_PLACEHOLDERS = [
    '__PRACTICE_POLICY_DIGEST__',
    '__SIM_PRACTICE_POLICY_JSON__',
    '__PRACTICE_JS__',
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


def _is_review_eligible(inst: dict[str, Any]) -> bool:
    if not isinstance(inst, dict):
        return False
    qid = str(inst.get('question_id') or '')
    ext_data = (inst.get('extensions') or {}).get('data') or {}
    eph = ext_data.get('ephemeral') or {}
    if (isinstance(eph, dict) and eph.get('frozen_bank_member') is False) or re.search(r'-EPH-[0-9]+$', qid):
        return False
    rev = inst.get('review')
    if not isinstance(rev, dict):
        return False
    for k in ('accessibility', 'calculation', 'content', 'source'):
        if rev.get(k) != 'passed':
            return False
    wf = ext_data.get('review_workflow')
    if isinstance(wf, dict) and wf.get('state') != 'accepted':
        return False
    return True


def _live_eligible_counts(repo_root: Path) -> dict[str, int]:
    counts: dict[str, int] = {str(t): 0 for t in range(1, 8)}
    bank_dir = repo_root / BANK_DIR
    for path in sorted(bank_dir.glob('*.json')):
        data = load_json(path)
        questions = data if isinstance(data, list) else data.get('questions', data.get('instances', []))
        for q in questions:
            if _is_review_eligible(q):
                tk = str(q.get('topic') or '')
                if tk in counts:
                    counts[tk] += 1
    return counts


def validate_policy_data(
    data: Any,
    eligible_counts: dict[str, int],
    registered_types: set[str],
    outcome_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return {'status': 'FAIL', 'errors': ['Practice policy must be a JSON object']}

    if data.get('island_id') != 'sim-practice-policy':
        errors.append(f'island_id must be "sim-practice-policy", got {data.get("island_id")!r}')
    if data.get('epistemic_label') != 'PROPOSED':
        errors.append('epistemic_label must be "PROPOSED"')
    if data.get('official_counterpart_status') != 'UNDETERMINED':
        errors.append('official_counterpart_status must be "UNDETERMINED"')
    if not isinstance(data.get('honesty_note_lv'), str) or not data['honesty_note_lv'].strip():
        errors.append('Missing honesty_note_lv')

    preds = data.get('predecessor_decisions')
    if not isinstance(preds, list) or len(preds) == 0:
        errors.append('predecessor_decisions must be non-empty')

    tl = data.get('topic_lengths')
    lengths: dict[str, int] = {}
    if not isinstance(tl, dict):
        errors.append('topic_lengths must be an object')
    else:
        for t in range(1, 8):
            tk = str(t)
            entry = tl.get(tk)
            if not isinstance(entry, dict):
                errors.append(f'topic {tk}: missing topic_lengths entry')
                continue
            dl = entry.get('declared_length')
            if not isinstance(dl, int) or isinstance(dl, bool) or dl <= 0:
                errors.append(f'topic {tk}: declared_length must be a positive integer, got {dl!r}')
                continue
            if entry.get('epistemic_label') != 'PROPOSED':
                errors.append(f'topic {tk}: epistemic_label must be "PROPOSED"')
            lengths[tk] = dl
            elig = eligible_counts.get(tk, 0)
            if dl > elig:
                errors.append(
                    f'topic {tk}: declared_length ({dl}) exceeds live eligible instance count ({elig})'
                )
            if outcome_counts and tk in outcome_counts:
                if entry.get('outcomes_count') != outcome_counts[tk]:
                    errors.append(
                        f'topic {tk}: outcomes_count ({entry.get("outcomes_count")}) != coverage ({outcome_counts[tk]})'
                    )
        if '7' in lengths and '3' in lengths and lengths['7'] >= lengths['3']:
            errors.append(
                f'topic 7 declared_length ({lengths["7"]}) must be shorter than topic 3 ({lengths["3"]})'
            )

    ord_rule = data.get('ordering_rule')
    if not isinstance(ord_rule, dict) or not isinstance(ord_rule.get('difficulty_order'), list) or not ord_rule['difficulty_order']:
        errors.append('ordering_rule.difficulty_order must be non-empty')

    fs = data.get('filter_semantics')
    vocab = fs.get('response_type_vocabulary') if isinstance(fs, dict) else None
    if not isinstance(vocab, list) or len(vocab) != 18:
        errors.append('filter_semantics.response_type_vocabulary must declare all 18 response types')
    if isinstance(vocab, list):
        for rt in vocab:
            if rt not in registered_types:
                errors.append(f'filter_semantics.response_type_vocabulary references unknown type {rt!r}')

    bounds = data.get('bounds_rules')
    if not isinstance(bounds, dict) or bounds.get('no_repeat_within_path') is not True or \
       bounds.get('exclude_current_session_answered') is not True or \
       bounds.get('never_pad_with_unreviewed') is not True or \
       bounds.get('never_pad_with_repeats') is not True:
        errors.append('bounds_rules must enforce no-repeat, current-session exclusion, and no unreviewed padding')

    skip = data.get('skip_semantics')
    if not isinstance(skip, dict) or skip.get('advances_without_grading') is not True or \
       skip.get('recorded_as') != 'skipped' or skip.get('counts_as_incorrect') is not False:
        errors.append('skip_semantics must advance without grading and record as skipped (not incorrect)')

    canonical = canonical_json_bytes(data)
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'policy_id': data.get('policy_id'),
        'epistemic_label': data.get('epistemic_label'),
        'official_counterpart_status': data.get('official_counterpart_status'),
        'topic_lengths': lengths,
        'eligible_counts': eligible_counts,
        'bytes': len(canonical),
        'digest': sha256_bytes(canonical),
        'errors': errors,
    }


def _check_negative_fixtures(
    valid_policy: dict[str, Any],
    eligible_counts: dict[str, int],
    registered_types: set[str],
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    overlong = copy.deepcopy(valid_policy)
    overlong['topic_lengths']['3']['declared_length'] = eligible_counts.get('3', 16) + 1
    r1 = validate_policy_data(overlong, eligible_counts, registered_types)
    named_topic_3 = any('topic 3' in e for e in r1['errors'])
    cases.append({
        'id': 'NEG-N30-OVERLONG-TOPIC-3',
        'expected': 'FAIL',
        'observed': r1['status'],
        'rejected': r1['status'] == 'FAIL' and named_topic_3,
        'named_topic_3': named_topic_3,
        'errors': r1['errors'],
    })

    bad_type = copy.deepcopy(valid_policy)
    bad_type['filter_semantics']['response_type_vocabulary'].append('Q99')
    r2 = validate_policy_data(bad_type, eligible_counts, registered_types)
    named_q99 = any('Q99' in e for e in r2['errors'])
    cases.append({
        'id': 'NEG-N30-UNKNOWN-RESPONSE-TYPE',
        'expected': 'FAIL',
        'observed': r2['status'],
        'rejected': r2['status'] == 'FAIL' and named_q99,
        'named_q99': named_q99,
        'errors': r2['errors'],
    })

    bad_pad = copy.deepcopy(valid_policy)
    bad_pad['bounds_rules']['never_pad_with_unreviewed'] = False
    r3 = validate_policy_data(bad_pad, eligible_counts, registered_types)
    cases.append({
        'id': 'NEG-N30-ALLOW-UNREVIEWED-PADDING',
        'expected': 'FAIL',
        'observed': r3['status'],
        'rejected': r3['status'] == 'FAIL',
        'errors': r3['errors'],
    })

    return {'status': 'PASS' if all(c['rejected'] for c in cases) else 'FAIL', 'cases': cases}


def _check_terms_lint(repo_root: Path, policy_data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    terms_doc = load_json(repo_root / TERMS_PATH)
    by_key = {t.get('key'): t for t in (terms_doc.get('terms') or []) if isinstance(t, dict) and isinstance(t.get('key'), str)}
    copy_keys = policy_data.get('copy_keys') or {}
    missing_copy: list[str] = []
    endorsement_hits: list[str] = []

    for ck, term_key in sorted(copy_keys.items()):
        entry = by_key.get(term_key)
        if not entry or not isinstance(entry.get('text_lv'), str) or not entry['text_lv'].strip():
            missing_copy.append(f'{ck}:{term_key}')
        else:
            for m in FORBIDDEN_ENDORSEMENT_RE.finditer(entry['text_lv']):
                endorsement_hits.append(f'{term_key}:{m.group(0)}')

    if missing_copy:
        errors.append(f'Missing #sim-terms keys for practice policy: {missing_copy}')
    if endorsement_hits:
        errors.append(f'Forbidden endorsement phrasing in practice terms: {endorsement_hits}')

    terms_res = validate_terms.validate_all(repo_root=repo_root)
    if terms_res.get('status') != 'PASS':
        errors.append('N10 terminology validator failed')

    return {
        'status': 'PASS' if (not missing_copy and not endorsement_hits and terms_res.get('status') == 'PASS') else 'FAIL',
        'copy_keys_checked': len(copy_keys),
        'missing_copy_keys': missing_copy,
        'endorsement_hits': endorsement_hits,
        'n10_terms_status': terms_res.get('status'),
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    missing_ph = [ph for ph in REQUIRED_PLACEHOLDERS if ph not in shell]
    for mid in missing_ids:
        errors.append(f'src/shell.html missing required N30 id #{mid}')
    for mph in missing_ph:
        errors.append(f'src/shell.html missing required N30 placeholder {mph}')
    return {
        'status': 'PASS' if (not missing_ids and not missing_ph) else 'FAIL',
        'required_ids_checked': len(REQUIRED_SHELL_IDS),
        'missing_ids': missing_ids,
        'missing_placeholders': missing_ph,
    }


def _check_source_scans(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    ts_path = repo_root / PRACTICE_TS_PATH
    js_path = repo_root / PRACTICE_JS_PATH
    if not ts_path.exists():
        errors.append(f'Missing TypeScript source {PRACTICE_TS_PATH}')
        return {'status': 'FAIL'}
    if not js_path.exists():
        errors.append(f'Missing compiled module {PRACTICE_JS_PATH}')
        return {'status': 'FAIL'}

    ts_text = ts_path.read_text(encoding='utf-8')
    net_hits = [label for pat, label in FORBIDDEN_NETWORK_PATTERNS if re.search(pat, ts_text)]
    clk_hits = [label for pat, label in FORBIDDEN_CLOCK_PATTERNS if re.search(pat, ts_text)]
    f10_hits = [
        exp for exp in F10_BANNED_EXPORTS
        if re.search(rf'\b{re.escape(exp)}\s*:', ts_text)
    ]
    for nh in net_hits:
        errors.append(f'{PRACTICE_TS_PATH} contains forbidden network primitive: {nh}')
    for ch in clk_hits:
        errors.append(f'{PRACTICE_TS_PATH} contains forbidden wall-clock primitive: {ch}')
    for fh in f10_hits:
        errors.append(f'{PRACTICE_TS_PATH} exports forbidden F10 property: {fh}')

    return {
        'status': 'PASS' if (not net_hits and not clk_hits and not f10_hits) else 'FAIL',
        'network_hits': net_hits,
        'clock_hits': clk_hits,
        'f10_hits': f10_hits,
        'ts_sha256': sha256_file(ts_path),
        'js_sha256': sha256_file(js_path),
    }


def _check_ts_drift(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(repo_root / COMPILE_TOOL), '--check'],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    ok = proc.returncode == 0
    if not ok:
        errors.append('TypeScript drift check failed: ' + (proc.stderr.strip() or proc.stdout.strip()))
    return {'status': 'PASS' if ok else 'FAIL', 'returncode': proc.returncode}


def validate_all(repo_root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    policy_path = repo_root / POLICY_PATH
    if not policy_path.exists():
        return {'status': 'FAIL', 'errors': [f'Missing {POLICY_PATH}']}
    policy_data = load_json(policy_path)
    eligible_counts = _live_eligible_counts(repo_root)
    rt_data = load_json(repo_root / RESPONSE_TYPES_PATH)
    registered_types = set((rt_data.get('types') or {}).keys())
    cov_data = load_json(repo_root / COVERAGE_PATH)
    outcome_counts: dict[str, int] = {str(t): 0 for t in range(1, 8)}
    for oc in cov_data.get('outcomes', []):
        tk = str(oc.get('topic') or '')
        if tk in outcome_counts:
            outcome_counts[tk] += 1

    policy_report = validate_policy_data(policy_data, eligible_counts, registered_types, outcome_counts)
    errors.extend(policy_report['errors'])
    neg_report = _check_negative_fixtures(policy_data, eligible_counts, registered_types)
    if neg_report['status'] != 'PASS':
        errors.append('One or more negative practice-policy fixtures were not rejected')
    terms_report = _check_terms_lint(repo_root, policy_data, errors)
    shell_report = _check_shell(repo_root, errors)
    source_report = _check_source_scans(repo_root, errors)
    drift_report = _check_ts_drift(repo_root, errors)

    return {
        'schema_version': 1,
        'task': 'N30',
        'gate': 'practice',
        'status': 'PASS' if not errors else 'FAIL',
        'policy': policy_report,
        'negative_fixtures': neg_report,
        'terms_lint': terms_report,
        'shell': shell_report,
        'source_scans': source_report,
        'ts_drift': drift_report,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    pol = report.get('policy') or {}
    neg = report.get('negative_fixtures') or {}
    return (
        f"practice {report['status']}: policy={pol.get('bytes')}B "
        f"lengths={pol.get('topic_lengths')} "
        f"neg={len(neg.get('cases') or [])}/{len(neg.get('cases') or [])}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(ROOT))
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    report = validate_all(repo_root=repo_root)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(format_summary(report))
    for err in report.get('errors', []):
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
