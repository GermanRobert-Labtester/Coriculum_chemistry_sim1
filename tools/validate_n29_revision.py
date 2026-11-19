#!/usr/bin/env python3
"""N29 build gate: revision & F07 self-assessment policy validation, single-sourced
criterion-label totality, negative policy fixtures, N10 term-key & copy lint,
TypeScript drift guard, shell touchpoints, and offline/no-wall-clock/F10 source scan.

Usage:
    python3 tools/validate_n29_revision.py --report evidence/N29_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import copy
import glob
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
POLICY_PATH = 'data/revision_policy.json'
TERMS_PATH = 'data/terms.json'
SHELL_PATH = 'src/shell.html'
REVISION_TS_PATH = 'src/revision.ts'
REVISION_JS_PATH = 'src/compiled/revision.js'
COMPILE_TOOL = 'tools/compile_n21_ts.py'

VERBATIM_SELF_ASSESSMENT_LABEL_LV = (
    'Izglītojamā paša novērtējums (F07, PROPOSED) — '
    'šis nav automātiskais vērtējums un neietekmē apguves stāvokli.'
)
VERBATIM_NOTE_NEVER_ANALYZED_LV = (
    'Brīvā teksta piezīme tiek saglabāta burtiski bez analīzes, '
    'atslēgvārdu meklēšanas vai automātiskas vērtēšanas.'
)

REQUIRED_RATINGS = ('confident', 'with_effort', 'not_yet')
REQUIRED_SHELL_IDS = [
    'sim-revision-policy',
    'sim-revision-error',
    'atskats-revision-wrap',
    'atskats-revision-heading',
    'atskats-revision-honesty',
    'atskats-revision-status',
    'atskats-revision-panel',
    'atskats-revision-chain-host',
    'atskats-revision-handoff',
    'atskats-self-assessment-host',
]
REQUIRED_PLACEHOLDERS = [
    '__REVISION_POLICY_DIGEST__',
    '__SIM_REVISION_POLICY_JSON__',
    '__REVISION_JS__',
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
        return {'status': 'FAIL', 'errors': ['Revision policy must be a JSON object']}

    if data.get('island_id') != 'sim-revision-policy':
        errors.append(f'island_id must be "sim-revision-policy", got {data.get("island_id")!r}')
    if data.get('epistemic_label') != 'PROPOSED':
        errors.append('epistemic_label must be "PROPOSED"')
    if data.get('official_counterpart_status') != 'UNDETERMINED':
        errors.append('official_counterpart_status must be "UNDETERMINED"')
    if not isinstance(data.get('honesty_note_lv'), str) or not data['honesty_note_lv'].strip():
        errors.append('Missing honesty_note_lv')

    preds = data.get('predecessor_decisions')
    if not isinstance(preds, list) or len(preds) == 0:
        errors.append('predecessor_decisions must be non-empty')

    sa = data.get('self_assessment')
    if not isinstance(sa, dict):
        errors.append('self_assessment must be an object')
    else:
        if sa.get('feature_id') != 'F07':
            errors.append('self_assessment.feature_id must be "F07"')
        if sa.get('excluded_from_mastery') is not True:
            errors.append('self_assessment.excluded_from_mastery must be true')
        if sa.get('excluded_from_scoring') is not True:
            errors.append('self_assessment.excluded_from_scoring must be true')
        if sa.get('key_free_criteria_only') is not True:
            errors.append('self_assessment.key_free_criteria_only must be true')
        max_len = sa.get('note_max_length')
        if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len <= 0:
            errors.append(f'self_assessment.note_max_length must be a positive integer, got {max_len!r}')
        if sa.get('verbatim_self_assessment_label_lv') != VERBATIM_SELF_ASSESSMENT_LABEL_LV:
            errors.append('self_assessment.verbatim_self_assessment_label_lv must match verbatim policy copy')
        if sa.get('verbatim_note_never_analyzed_lv') != VERBATIM_NOTE_NEVER_ANALYZED_LV:
            errors.append('self_assessment.verbatim_note_never_analyzed_lv must match verbatim policy copy')
        ratings = sa.get('ratings')
        if not isinstance(ratings, list) or len(ratings) != 3:
            errors.append('self_assessment.ratings must list 3 rating states')
        else:
            r_ids = [r.get('id') for r in ratings if isinstance(r, dict)]
            for req in REQUIRED_RATINGS:
                if req not in r_ids:
                    errors.append(f'self_assessment.ratings missing {req!r}')

    pe = data.get('practice_entry_contract')
    if not isinstance(pe, dict) or pe.get('contract') != 'N27-to-N30-practice-entry' or pe.get('zero_key_material') is not True:
        errors.append('practice_entry_contract must declare N27-to-N30-practice-entry with zero_key_material=true')

    canonical = canonical_json_bytes(data)
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'policy_id': data.get('policy_id'),
        'epistemic_label': data.get('epistemic_label'),
        'official_counterpart_status': data.get('official_counterpart_status'),
        'note_max_length': sa.get('note_max_length') if isinstance(sa, dict) else None,
        'bytes': len(canonical),
        'digest': sha256_bytes(canonical),
        'errors': errors,
    }


def _check_negative_fixtures(valid_policy: dict[str, Any]) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    bad_mastery = copy.deepcopy(valid_policy)
    bad_mastery['self_assessment']['excluded_from_mastery'] = False
    r1 = validate_policy_data(bad_mastery)
    cases.append({
        'id': 'NEG-N29-SA-FEEDS-MASTERY',
        'expected': 'FAIL',
        'observed': r1['status'],
        'rejected': r1['status'] == 'FAIL',
        'errors': r1['errors'],
    })

    bad_copy = copy.deepcopy(valid_policy)
    bad_copy['self_assessment']['verbatim_note_never_analyzed_lv'] = 'Modified text'
    r2 = validate_policy_data(bad_copy)
    cases.append({
        'id': 'NEG-N29-COPY-DRIFT',
        'expected': 'FAIL',
        'observed': r2['status'],
        'rejected': r2['status'] == 'FAIL',
        'errors': r2['errors'],
    })

    bad_len = copy.deepcopy(valid_policy)
    bad_len['self_assessment']['note_max_length'] = 0
    r3 = validate_policy_data(bad_len)
    cases.append({
        'id': 'NEG-N29-UNBOUNDED-NOTE',
        'expected': 'FAIL',
        'observed': r3['status'],
        'rejected': r3['status'] == 'FAIL',
        'errors': r3['errors'],
    })

    all_ok = all(c['rejected'] for c in cases)
    return {'status': 'PASS' if all_ok else 'FAIL', 'cases': cases}


def _check_terms_and_criteria_lint(repo_root: Path, policy_data: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    terms_file = repo_root / TERMS_PATH
    terms_doc = load_json(terms_file)
    terms_list = terms_doc.get('terms') or []
    by_key = {t.get('key'): t for t in terms_list if isinstance(t, dict) and isinstance(t.get('key'), str)}

    copy_keys = policy_data.get('copy_keys') or {}
    missing_copy: list[str] = []
    endorsement_hits: list[str] = []

    for ck, term_key in sorted(copy_keys.items()):
        entry = by_key.get(term_key)
        if not entry or not isinstance(entry.get('text_lv'), str) or not entry['text_lv'].strip():
            missing_copy.append(f'{ck}:{term_key}')
        else:
            txt = entry['text_lv']
            for m in FORBIDDEN_ENDORSEMENT_RE.finditer(txt):
                endorsement_hits.append(f'{term_key}:{m.group(0)}')

    # Collect all unique criterion_ids across the bank and verify single-sourced feedback.criterion.* keys
    bank_cids: set[str] = set()
    for p in sorted((repo_root / 'data/bank').glob('*.json')):
        bdoc = load_json(p)
        for q in bdoc.get('questions', []):
            for r in q.get('rubric', []):
                cid = r.get('criterion_id')
                if isinstance(cid, str) and cid:
                    bank_cids.add(cid)

    missing_criteria: list[str] = []
    for cid in sorted(bank_cids):
        tkey = f'feedback.criterion.{cid}'
        entry = by_key.get(tkey)
        if not entry or not isinstance(entry.get('text_lv'), str) or not entry['text_lv'].strip():
            missing_criteria.append(tkey)
        else:
            for m in FORBIDDEN_ENDORSEMENT_RE.finditer(entry['text_lv']):
                endorsement_hits.append(f'{tkey}:{m.group(0)}')

    if missing_copy:
        errors.append(f'Missing #sim-terms keys for revision policy: {missing_copy}')
    if missing_criteria:
        errors.append(f'Missing #sim-terms feedback.criterion.* keys ({len(missing_criteria)}): {missing_criteria[:10]}')
    if endorsement_hits:
        errors.append(f'Forbidden certification/endorsement phrasing in terms: {endorsement_hits}')

    terms_res = validate_terms.validate_all(repo_root=repo_root)
    if terms_res.get('status') != 'PASS':
        errors.append('N10 terminology validator failed')

    return {
        'status': 'PASS' if (not missing_copy and not missing_criteria and not endorsement_hits and terms_res.get('status') == 'PASS') else 'FAIL',
        'copy_keys_checked': len(copy_keys),
        'bank_criterion_ids_checked': len(bank_cids),
        'missing_copy_keys': missing_copy,
        'missing_criterion_keys': missing_criteria,
        'endorsement_hits': endorsement_hits,
        'n10_terms_status': terms_res.get('status'),
    }


def _check_shell(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    missing_ph = [ph for ph in REQUIRED_PLACEHOLDERS if ph not in shell]
    for mid in missing_ids:
        errors.append(f'{SHELL_PATH} missing N29 touchpoint #{mid}')
    for ph in missing_ph:
        errors.append(f'{SHELL_PATH} missing placeholder {ph}')
    atskats_m = re.search(r'<section id="atskats"[\s\S]*?</section>', shell)
    has_canvas = bool(atskats_m and '<canvas' in atskats_m.group(0).lower())
    if has_canvas:
        errors.append('#atskats must not contain <canvas> (F10 rejected)')
    return {
        'status': 'PASS' if (not missing_ids and not missing_ph and not has_canvas) else 'FAIL',
        'required_ids_present': len(REQUIRED_SHELL_IDS) - len(missing_ids),
        'required_ids_total': len(REQUIRED_SHELL_IDS),
        'missing_ids': missing_ids,
        'missing_placeholders': missing_ph,
    }


def _check_sources(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    scanned: dict[str, Any] = {}
    for rel in (REVISION_TS_PATH, REVISION_JS_PATH):
        path = repo_root / rel
        if not path.exists():
            errors.append(f'Missing N29 module {rel}')
            continue
        text = path.read_text(encoding='utf-8')
        net_hits = [label for pat, label in FORBIDDEN_NETWORK_PATTERNS if re.search(pat, text)]
        clk_hits = [label for pat, label in FORBIDDEN_CLOCK_PATTERNS if re.search(pat, text)]
        end_hits = [m.group(0) for m in FORBIDDEN_ENDORSEMENT_RE.finditer(text)]
        if net_hits:
            errors.append(f'{rel} contains forbidden network references: {net_hits}')
        if clk_hits:
            errors.append(f'{rel} contains forbidden wall-clock calls: {clk_hits}')
        if end_hits:
            errors.append(f'{rel} contains forbidden endorsement phrasing: {end_hits}')
        scanned[rel] = {
            'bytes': path.stat().st_size,
            'sha256': sha256_file(path),
            'network_hits': net_hits,
            'clock_hits': clk_hits,
            'endorsement_hits': end_hits,
        }

    js_probe = """
const rev = require('./src/compiled/revision.js');
process.stdout.write(JSON.stringify({ keys: Object.keys(rev) }));
"""
    proc = subprocess.run(['node', '-e', js_probe], cwd=str(repo_root), capture_output=True, text=True)
    if proc.returncode != 0:
        errors.append(f'Node export probe failed: {proc.stderr.strip()}')
    else:
        info = json.loads(proc.stdout)
        banned_found = [k for k in info['keys'] if k in F10_BANNED_EXPORTS]
        if banned_found:
            errors.append(f'SimRevision exports banned F10 symbols: {banned_found}')
        scanned['exports'] = info
    return scanned


def run_gate(repo_root: Path = ROOT, policy_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    pfile = policy_path or (repo_root / POLICY_PATH)

    compile_proc = subprocess.run(
        [sys.executable, str(repo_root / COMPILE_TOOL), '--check'],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    if compile_proc.returncode != 0:
        errors.append('TypeScript drift check failed: ' + (compile_proc.stderr.strip() or compile_proc.stdout.strip()))

    if not pfile.exists():
        errors.append(f'Missing {POLICY_PATH}')
        policy_report: dict[str, Any] = {'status': 'FAIL', 'errors': [f'Missing {POLICY_PATH}']}
        neg_report: dict[str, Any] = {'status': 'FAIL', 'cases': []}
        terms_report: dict[str, Any] = {'status': 'FAIL'}
    else:
        raw_text = pfile.read_text(encoding='utf-8')
        if re.search(r'https?://', raw_text, re.IGNORECASE):
            errors.append(f'{POLICY_PATH} contains external URL')
        pdata = load_json(pfile)
        policy_report = validate_policy_data(pdata)
        errors.extend(policy_report.get('errors', []))
        neg_report = _check_negative_fixtures(pdata)
        if neg_report['status'] != 'PASS':
            errors.append('Negative policy fixtures failed')
        terms_report = _check_terms_and_criteria_lint(repo_root, pdata, errors)

    shell_report = _check_shell(repo_root, errors)
    source_report = _check_sources(repo_root, errors)

    return {
        'schema_version': 1,
        'task': 'N29',
        'gate': 'revision',
        'status': 'PASS' if not errors else 'FAIL',
        'policy': policy_report,
        'negative_fixtures': neg_report,
        'terms_lint': terms_report,
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
    print(
        f"N29 revision gate: {report['status']} "
        f"(criteria={report['terms_lint'].get('bank_criterion_ids_checked')}, "
        f"terms={report['terms_lint'].get('status')}, "
        f"shell={report['shell'].get('required_ids_present')}/{report['shell'].get('required_ids_total')}, "
        f"ts_drift={report['ts_drift']})"
    )
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
