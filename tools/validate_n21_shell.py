#!/usr/bin/env python3
"""N21 build gate: the exam session contract, the mode registry and the shell.

This gate is the build's N21 checkpoint. It refuses the build when:

- the exam-policy island does not match the authoring twin
  (``tools/author_exam_policy.py --check``);
- the compiled runtime modules differ from their TypeScript sources (the
  drift guard of ``tools/compile_n21_ts.py --check``), so a stale module can
  never be shipped;
- the session contract is not exhaustive: every (state, event) pair must have
  exactly one outcome, and every error id the runtime can raise must be
  declared in the island;
- the slot plan does not close on the blueprint (21 slots, 100 points, the
  170 + 10 minute split inside the programme's 180-minute maximum);
- the advisory timer is not labelled as advisory, or the copy claims an
  official examination;
- the mode registry does not keep the two boundaries apart: exam mode must
  forbid the four help components and practice mode must allow them;
- the shell markup is missing a touchpoint the task requires (the timer bar,
  the navigator, the question map, the review-and-submit screen), or a
  touchpoint carries an id that is not ASCII.

Usage:
    python3 tools/validate_n21_shell.py --report evidence/N21_VALIDATION_RECORD.json
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
POLICY_PATH = ROOT / 'data/exam_policy.json'
BLUEPRINT_PATH = ROOT / 'docs/SIMULATION_BLUEPRINT.json'
SHELL_PATH = ROOT / 'src/shell.html'
SESSION_TS = ROOT / 'src/session.ts'
EXAM_TS = ROOT / 'src/exam.ts'
SESSION_JS = ROOT / 'src/compiled/session.js'
EXAM_JS = ROOT / 'src/compiled/exam.js'
AUTHORING_TOOL = ROOT / 'tools/author_exam_policy.py'
COMPILE_TOOL = ROOT / 'tools/compile_n21_ts.py'

HELP_COMPONENTS = ['hint', 'chain', 'method-card', 'term-lookup']
EXAM_COMPONENTS = ['input', 'timer', 'navigator', 'map', 'review']
ASCII_ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._:-]*$')

REQUIRED_SHELL_IDS = [
    'eksamens',
    'exam-entry',
    'exam-start',
    'exam-shell',
    'exam-timer-bar',
    'exam-timer-value',
    'exam-timer-label',
    'exam-navigator',
    'exam-prev',
    'exam-next',
    'exam-flag',
    'exam-map',
    'exam-slot-host',
    'exam-review',
]

# The honesty lint: the advisory timer must say so in words, and the section
# must not claim an official examination, a grade or proctoring.
ADVISORY_REQUIRED = ['izglītojoš', 'nevis oficiāls']
FORBIDDEN_CLAIM_RE = re.compile(
    r'\b(?:proktor|proctoring|uzraudzības ierāde|oficiāl[aā]s\s+vērtējums|'
    r'oficiāl[aā]s\s+eks[aā]mens|garant[eē]\w*|sertifik[aā]t\w*)\b',
    re.IGNORECASE,
)


def _run(command: list[str], label: str) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    return {
        'label': label,
        'command': ' '.join(command),
        'returncode': proc.returncode,
        'status': 'PASS' if proc.returncode == 0 else 'FAIL',
        'stdout': proc.stdout.strip()[:4000],
        'stderr': proc.stderr.strip()[:2000],
    }


def check_island_matches_authoring(errors: list[str]) -> dict[str, Any]:
    result = _run([sys.executable, str(AUTHORING_TOOL), '--check'], 'exam_policy_island_authoring')
    if result['status'] != 'PASS':
        errors.append(f"exam-policy island does not match its authoring twin: {result['stdout']} {result['stderr']}")
    return result


def check_compiled_modules(errors: list[str]) -> dict[str, Any]:
    result = _run([sys.executable, str(COMPILE_TOOL), '--check'], 'n21_typescript_drift')
    if result['status'] != 'PASS':
        errors.append(f"the compiled N21 modules differ from their TypeScript sources: {result['stdout']} {result['stderr']}")
    return result


def check_contract(policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    contract = policy.get('session_contract') or {}
    states = contract.get('states') or []
    events = contract.get('events') or []
    terminal = contract.get('terminal_states') or []
    mutations = contract.get('mutation_events') or []
    error_ids = contract.get('error_ids') or []
    table = contract.get('transition_table') or []

    if len(states) != 6:
        errors.append(f'expected 6 session states, found {len(states)}')
    if sorted(terminal) != sorted(['submitted', 'expired', 'aborted']):
        errors.append(f'terminal states must be submitted/expired/aborted, found {terminal}')
    if sorted(mutations) != sorted(['answer', 'flag']):
        errors.append(f'mutation events must be answer/flag, found {mutations}')

    seen: dict[tuple[str, str], int] = {}
    for row in table:
        key = (str(row.get('from')), str(row.get('event')))
        seen[key] = seen.get(key, 0) + 1
        to = row.get('to')
        error = row.get('error')
        if to is None and not error:
            errors.append(f'transition {key} declares neither a next state nor an error id')
        if to is not None and error:
            errors.append(f'transition {key} declares both a next state and an error id')
        if to is not None and to not in states:
            errors.append(f'transition {key} names an unknown state {to!r}')
        if error is not None and error not in error_ids:
            errors.append(f'transition {key} names an undeclared error id {error!r}')

    for state in states:
        for event in events:
            if seen.get((state, event), 0) != 1:
                errors.append(f'transition table must cover {state}/{event} exactly once, found {seen.get((state, event), 0)}')

    declared_errors = set(error_ids)
    runtime_errors = set(contract.get('runtime_error_ids') or [])
    used_errors = {str(row.get('error')) for row in table if row.get('error')}
    for guard_errors in (contract.get('guards') or {}).values():
        for guard_error in (guard_errors or {}).values():
            used_errors.add(str(guard_error))

    # A transition error and a runtime error are disjoint sets: the table
    # answers "what happens for this pair", the runtime list covers "what the
    # machine raises outside the table".
    overlap = sorted(runtime_errors & used_errors)
    if overlap:
        errors.append(f'error ids appear both as a transition error and as a runtime error: {overlap}')

    unused = sorted(declared_errors - used_errors - runtime_errors)
    if unused:
        errors.append(f'the contract declares error ids no transition, guard or runtime path uses: {unused}')

    undeclared_runtime = sorted(runtime_errors - declared_errors)
    if undeclared_runtime:
        errors.append(f'the runtime error ids are not declared in error_ids: {undeclared_runtime}')

    return {
        'states': states,
        'events': events,
        'transition_count': len(table),
        'error_ids': error_ids,
        'runtime_error_ids': sorted(runtime_errors),
        'unused_error_ids': unused,
    }


def check_blueprint_alignment(policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    blueprint = load_json(BLUEPRINT_PATH)
    slots = policy.get('slots') or []
    blueprint_slots = blueprint['slots']

    if len(slots) != blueprint['constraints']['top_level_tasks']:
        errors.append(f"the island declares {len(slots)} slots, the blueprint declares {blueprint['constraints']['top_level_tasks']}")
    if len(slots) != policy['exam']['slot_count']:
        errors.append('the slot list does not match the declared slot count')

    total = sum(int(slot['points']) for slot in slots)
    if total != blueprint['points']:
        errors.append(f"the slot points sum to {total}, the blueprint declares {blueprint['points']}")
    if total != policy['exam']['total_points']:
        errors.append('the slot points do not match the declared total')

    for island_slot, blueprint_slot in zip(slots, blueprint_slots):
        if island_slot['slot_id'] != blueprint_slot['slot_id']:
            errors.append(f"slot order differs from the blueprint: {island_slot['slot_id']} vs {blueprint_slot['slot_id']}")
        if island_slot['topic'] != blueprint_slot['topic']:
            errors.append(f"slot {island_slot['slot_id']} topic differs from the blueprint")
        if island_slot['points'] != blueprint_slot['points']:
            errors.append(f"slot {island_slot['slot_id']} points differ from the blueprint")

    timer = policy.get('timer') or {}
    limit = timer.get('advisory_limit_seconds')
    expected_limit = blueprint['official_facts']['maximum_minutes'] * 60
    if limit != expected_limit:
        errors.append(f'the advisory limit is {limit}s, the programme maximum is {expected_limit}s')
    if timer.get('working_seconds') != blueprint['working_minutes'] * 60:
        errors.append('the working seconds do not match the blueprint')
    if timer.get('review_seconds') != blueprint['review_minutes'] * 60:
        errors.append('the review seconds do not match the blueprint')
    if timer.get('clock') != 'monotonic':
        errors.append('the timer clock must be monotonic')
    if timer.get('hidden_tab') != 'keeps_counting':
        errors.append('the hidden-tab rule must be keeps_counting')
    if not (0 < float(timer.get('threshold_ratio', 0)) < 1):
        errors.append('the threshold ratio must lie strictly between 0 and 1')

    return {
        'slot_count': len(slots),
        'points_total': total,
        'advisory_limit_seconds': limit,
        'working_seconds': timer.get('working_seconds'),
        'review_seconds': timer.get('review_seconds'),
        'threshold_ratio': timer.get('threshold_ratio'),
        'blueprint_digest': sha256_file(BLUEPRINT_PATH),
    }


def check_view_discipline(policy: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    discipline = policy.get('view_discipline') or {}
    modes = discipline.get('modes') or {}
    exam = modes.get('exam') or {}
    practice = modes.get('practice') or {}

    exam_allowed = exam.get('allowed_components') or []
    exam_forbidden = exam.get('forbidden_components') or []
    practice_allowed = practice.get('allowed_components') or []

    for component in EXAM_COMPONENTS:
        if component not in exam_allowed:
            errors.append(f'exam mode must allow the {component} component')
    for component in HELP_COMPONENTS:
        if component in exam_allowed:
            errors.append(f'exam mode must not allow the {component} component')
        if component not in exam_forbidden:
            errors.append(f'exam mode must list the {component} component as forbidden')
        if component not in practice_allowed:
            errors.append(f'practice mode must allow the {component} component')

    unknown = [c for c in exam_allowed if c not in EXAM_COMPONENTS + HELP_COMPONENTS]
    if unknown:
        errors.append(f'the exam mode registers unknown components: {unknown}')

    if discipline.get('default_mode') not in modes:
        errors.append('the default mode must be a registered mode')

    return {
        'exam_allowed': exam_allowed,
        'exam_forbidden': exam_forbidden,
        'practice_allowed': practice_allowed,
        'unregistered_component_error': discipline.get('unregistered_component_error'),
    }


def check_shell_markup(errors: list[str]) -> dict[str, Any]:
    shell = SHELL_PATH.read_text(encoding='utf-8')
    ids = re.findall(r'\sid="([^"]+)"', shell)
    found = set(ids)

    for required in REQUIRED_SHELL_IDS:
        if required not in found:
            errors.append(f'the shell is missing the exam touchpoint #{required}')
    for value in found:
        if not ASCII_ID_RE.match(value):
            errors.append(f'non-ASCII or malformed id in the shell: {value!r}')
    duplicates = [value for value in set(ids) if ids.count(value) > 1]
    if duplicates:
        errors.append(f'duplicate ids in the shell: {duplicates}')

    if '__SIM_EXAM_POLICY_JSON__' not in shell:
        errors.append('the shell does not embed the exam-policy island')
    if '__SESSION_JS__' not in shell:
        errors.append('the shell does not inline the session module')
    if '__EXAM_JS__' not in shell:
        errors.append('the shell does not inline the exam module')

    # The exam section contains nested <section> elements (the map region),
    # so the region is delimited by the next top-level section rather than by
    # the first closing tag.
    section = re.search(
        r'<section id="eksamens".*?(?=<section id="rezultati")', shell, re.DOTALL
    )
    section_text = section.group(0) if section else ''
    for needle in ADVISORY_REQUIRED:
        if needle not in section_text:
            errors.append(f'the exam section must label the timer as advisory (missing {needle!r})')
    for match in FORBIDDEN_CLAIM_RE.finditer(section_text):
        context = section_text[max(0, match.start() - 20):match.end()].lower()
        if 'nav' in context or 'nevis' in context:
            continue
        errors.append(f'the exam section makes a forbidden claim: {match.group(0)!r}')

    return {
        'shell_digest': sha256_file(SHELL_PATH),
        'touchpoints_found': [name for name in REQUIRED_SHELL_IDS if name in found],
        'touchpoints_missing': [name for name in REQUIRED_SHELL_IDS if name not in found],
    }


def check_source_guards(errors: list[str]) -> dict[str, Any]:
    """The compiled modules must not carry a write path around the machine.

    The shell may only change the session through ``dispatch``. This is a
    source-level guard: the shell module must not contain a direct write to
    an answer map, and the session module must not export the map itself.
    """
    session_js = SESSION_JS.read_text(encoding='utf-8') if SESSION_JS.exists() else ''
    exam_js = EXAM_JS.read_text(encoding='utf-8') if EXAM_JS.exists() else ''

    if not session_js or not exam_js:
        errors.append('the compiled N21 modules are missing')
        return {'status': 'FAIL'}

    forbidden_in_exam = [
        r'\.answerMap\s*\[',
        r'answerMap\s*\[.*\]\s*=',
        r'\bsetAnswer\b',
        r'\banswerMap\s*=',
    ]
    for pattern in forbidden_in_exam:
        if re.search(pattern, exam_js):
            errors.append(f'the exam shell writes to the answer map directly ({pattern})')

    if 'dispatch(' not in exam_js:
        errors.append('the exam shell never dispatches a session event')

    # The session module must not hand out the live map.
    if re.search(r'getAnswers\s*\(\)\s*\{[^}]*return\s+this\.answerMap', session_js, re.DOTALL):
        errors.append('the session module returns the live answer map instead of a copy')

    return {
        'status': 'PASS',
        'session_js_bytes': len(session_js.encode('utf-8')),
        'exam_js_bytes': len(exam_js.encode('utf-8')),
        'session_ts_digest': sha256_file(SESSION_TS),
        'exam_ts_digest': sha256_file(EXAM_TS),
        'session_js_digest': sha256_file(SESSION_JS),
        'exam_js_digest': sha256_file(EXAM_JS),
    }


def run_gate(repo_root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []

    if not POLICY_PATH.exists():
        return {
            'status': 'FAIL',
            'errors': [f'{POLICY_PATH} does not exist; run tools/author_exam_policy.py'],
        }
    policy = load_json(POLICY_PATH)

    authoring = check_island_matches_authoring(errors)
    drift = check_compiled_modules(errors)
    contract = check_contract(policy, errors)
    alignment = check_blueprint_alignment(policy, errors)
    discipline = check_view_discipline(policy, errors)
    markup = check_shell_markup(errors)
    guards = check_source_guards(errors)

    island_bytes = canonical_json_bytes(policy)

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'owner': 'N21',
        'island': {
            'id': policy.get('island_id'),
            'source': 'data/exam_policy.json',
            'digest': sha256_bytes(island_bytes),
            'bytes': len(island_bytes),
        },
        'authoring_check': authoring,
        'compile_drift_check': drift,
        'contract': contract,
        'blueprint_alignment': alignment,
        'view_discipline': discipline,
        'shell_markup': markup,
        'source_guards': guards,
        'errors': errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='write the machine-readable report to this path')
    args = parser.parse_args()

    report = run_gate()
    if args.report:
        path = Path(args.report)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if report['status'] == 'PASS':
        contract = report['contract']
        alignment = report['blueprint_alignment']
        print(
            f"PASS n21 exam_shell gate: {contract['transition_count']} transitions, "
            f"{alignment['slot_count']} slots, {alignment['points_total']} points, "
            f"advisory limit {alignment['advisory_limit_seconds']}s"
        )
        return 0
    for error in report.get('errors', []):
        print(f'  - {error}', file=sys.stderr)
    print('FAIL n21 exam_shell gate', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
