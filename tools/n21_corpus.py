#!/usr/bin/env python3
"""N21 corpus runner: the evidence chain of the exam shell.

It runs the four gates of N21 and collects their findings:

  1. the authoring gate — data/exam_policy.json matches its authoring twin;
  2. the TypeScript drift gate — the committed modules match their sources;
  3. the build gate — tools/validate_n21_shell.py against the built artifact;
  4. the runtime harness — tools/check_n21_runtime.js, whose fixtures prove the
     lifecycle, the late-write guard, the timer contract, the payload and
     serialization contracts, the two-way view discipline, the mode registry,
     the navigation and keyboard completeness, the submit gate, the buffer
     race, the terminal record and the scripted end-to-end trace.

The records it writes are timestamp-free and byte-identical across two runs:
the same sources produce the same evidence, which is the parity proof the
roadmap asks for.

  evidence/N21_CORPUS_RECORD.json        — the extended corpus
  evidence/N21_VALIDATION_RECORD.json    — the gate-level summary
  evidence/N21_VERIFICATION_RECORD.json  — the claims and their evidence
  evidence/N21_RUNTIME_RECORD.json       — the runtime harness record
  evidence/N21_SESSION_TRACE.json        — the scripted session trace
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import byte_budget  # noqa: E402
from coverage_common import DEST, sha256_file  # noqa: E402

ROOT = DEST
AUTHORING = ROOT / 'tools/author_exam_policy.py'
COMPILE = ROOT / 'tools/compile_n21_ts.py'
GATE = ROOT / 'tools/validate_n21_shell.py'
HARNESS = ROOT / 'tools/check_n21_runtime.js'
ISLAND = ROOT / 'data/exam_policy.json'
MANIFEST = ROOT / 'output/build-manifest.json'

OUT_DEFAULT = ROOT / 'evidence/N21_CORPUS_RECORD.json'
VALIDATION_OUT = ROOT / 'evidence/N21_VALIDATION_RECORD.json'
VERIFICATION_OUT = ROOT / 'evidence/N21_VERIFICATION_RECORD.json'
RUNTIME_RECORD = ROOT / 'evidence/N21_RUNTIME_RECORD.json'
TRACE_OUT = ROOT / 'evidence/N21_SESSION_TRACE.json'


def run_tool(command: list[str], label: str) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    stdout = proc.stdout.strip()
    payload: Any = None
    if stdout.startswith('{') or stdout.startswith('['):
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            payload = None
    return {
        'label': label,
        'command': ' '.join(command),
        'returncode': proc.returncode,
        'status': 'PASS' if proc.returncode == 0 else 'FAIL',
        'report': payload,
        'stdout': stdout[:4000],
        'stderr': proc.stderr.strip()[:2000],
    }


def run_harness() -> dict[str, Any]:
    """Run the runtime harness and keep its full record as evidence."""
    RUNTIME_RECORD.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(['node', str(HARNESS), '--record', str(RUNTIME_RECORD)],
                          cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f'FAIL n21-runtime-harness: {proc.stderr.strip()[:2000]}')
    return json.loads(RUNTIME_RECORD.read_text(encoding='utf-8'))


def measure_budgets() -> dict[str, Any]:
    """The Section 1.3 byte accounting, measured against the built artifact."""
    if not MANIFEST.exists():
        return {'status': 'FAIL', 'reason': 'output/build-manifest.json is missing; run the build first.'}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    measured = byte_budget.measure_budgets(manifest)
    measured['notes'] = [
        'The exam shell has to run inside the single-file artifact, so its runtime is '
        'inlined; that is why the runtime JS and the artifact total were re-set on the '
        'measured requirement (byte_budget.RE_BUDGET_HISTORY, conflicts N21-C02 and '
        'N21-C03). The declared Section 1.3 bands stay visible next to the enforced '
        'ceilings.',
        'The final inline / lazy-load / re-budget decision belongs to N31.',
    ]
    return measured


def write_trace(harness: dict[str, Any]) -> None:
    """The scripted session trace: the integration input of N23 and N25."""
    trace_check = harness.get('checks', {}).get('end_to_end_trace', {})
    trace = {
        'schema_version': 1,
        'owner': 'N21',
        'note': 'The scripted session from the start screen to the terminal record. Every '
                'transition is one row of the transition table of #sim-exam-policy; the '
                'trace is the integration input of the grading task (N23) and of the '
                'logging task (N25).',
        'states': ['not-started', 'running', 'review', 'submitted', 'expired', 'aborted'],
        'transitions': trace_check.get('trace', []),
        'terminal_record_fields': harness.get('checks', {})
                                 .get('terminal_record', {})
                                 .get('record_fields', []),
        'expected_map': harness.get('checks', {}).get('navigation', {}).get('expected_map', []),
    }
    TRACE_OUT.parent.mkdir(parents=True, exist_ok=True)
    TRACE_OUT.write_text(json.dumps(trace, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                         encoding='utf-8')


def write_validation_record(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    """The gate-level validation record: what each gate checked and what it found."""
    gates = record['gates']
    runtime_checks = record['runtime']['checks']

    def report_of(label: str) -> dict[str, Any]:
        report = gates[label].get('report')
        return report if isinstance(report, dict) else {}

    validation = {
        'schema_version': 1,
        'owner': 'N21',
        'status': record['status'],
        'gates': {
            'authoring': {
                'status': gates['authoring_gate']['status'],
                'command': gates['authoring_gate']['command'],
                'island_bytes': report_of('authoring_gate').get('bytes'),
                'island_sha256': report_of('authoring_gate').get('sha256'),
            },
            'typescript_drift': {
                'status': gates['compile_gate']['status'],
                'command': gates['compile_gate']['command'],
                'stdout': gates['compile_gate'].get('stdout'),
            },
            'exam_shell': {
                'status': gates['exam_shell_gate']['status'],
                'command': gates['exam_shell_gate']['command'],
                'report': report_of('exam_shell_gate'),
            },
            'runtime': {
                'status': record['runtime']['status'],
                'checks': runtime_checks,
                'evidence': 'evidence/N21_RUNTIME_RECORD.json',
            },
        },
        'counts': {
            'slots': manifest.get('exam_shell_layer', {}).get('slot_count'),
            'points': manifest.get('exam_shell_layer', {}).get('points_total'),
            'transitions': manifest.get('exam_shell_layer', {}).get('transition_count'),
            'states': manifest.get('exam_shell_layer', {}).get('session_states'),
            'events': manifest.get('exam_shell_layer', {}).get('session_events'),
            'error_ids': manifest.get('exam_shell_layer', {}).get('error_ids'),
            'artifact_bytes': manifest.get('output_bytes'),
        },
        'digests': record['digests'],
        'budgets': record['budgets'],
        'violations': [],
    }
    VALIDATION_OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2,
                                         sort_keys=True) + '\n', encoding='utf-8')


def write_verification_record(record: dict[str, Any], manifest: dict[str, Any],
                              harness_checks: dict[str, Any]) -> None:
    """The machine-readable verification record: the claims and their evidence."""
    def status_of(name: str) -> str:
        return harness_checks.get(name, {}).get('status', 'FAIL')

    verification = {
        'schema_version': 1,
        'owner': 'N21',
        'status': record['status'],
        'policy_label': record['policy_label'],
        'official_programme_facts': {
            'topics': 7,
            'examination': 'written on paper',
            'maximum_minutes': 180,
            'note': 'The 2025 programme fixes no point weight, no question count, no pass '
                    'mark, no allowed aid and no exact exam question type. The 21 slots, '
                    'the 100 points and the three forms are the training policy of this '
                    'simulator (PROPOSED).',
        },
        'acceptance_criteria': {
            'AC1_happy_path': {
                'status': 'PASS' if all(status_of(name) == 'PASS' for name in (
                    'lifecycle', 'late_write_guard', 'timer_contract', 'payload_contract',
                    'serialization', 'buffer_race', 'terminal_record',
                    'end_to_end_trace')) else 'FAIL',
                'claims': [
                    'Every transition of the lifecycle matches the transition table of the '
                    'frozen #sim-exam-policy island.',
                    'A late write after submit, after expiry and after abort is refused '
                    'with a stable error id (E_SESSION_LATE_WRITE, E_SESSION_EXPIRED_WRITE, '
                    'E_SESSION_ABORTED_WRITE), and the answers given before the terminal '
                    'transition are preserved.',
                    'The advisory timer reads a monotonic clock: the 90 % threshold is a '
                    'status indication only, the elapsed time keeps counting while the tab '
                    'is hidden, and the expiry transition preserves the answers.',
                    'Answers are stored raw and unparsed; a serialised session deserialises '
                    'to identical answers, flags and state.',
                    'Rapid navigation during a re-render loses no in-progress answer.',
                    'The terminal record carries the answers, the flags, the elapsed time '
                    'and the form id.',
                    'The scripted session runs from the start screen to the terminal record '
                    'and every transition conforms to the table.',
                ],
                'evidence': ['evidence/N21_RUNTIME_RECORD.json',
                             'evidence/N21_SESSION_TRACE.json',
                             'tools/check_n21_runtime.js'],
            },
            'AC2_negative_or_edge': {
                'status': 'PASS' if all(status_of(name) == 'PASS' for name in (
                    'navigation', 'keyboard_traversal', 'submit_gate')) else 'FAIL',
                'claims': [
                    'The scripted answer/flag sequence (slots 1, 5 and 21 answered, slot 3 '
                    'flagged, the full range navigated) produces exactly the expected map '
                    'state, in the pure render state and in the rendered cells alike.',
                    'All 21 slots are reachable by pointer and by keyboard alone; the '
                    'keyboard run answers and flags across all 21 slots without a single '
                    'pointer event and the focus is never trapped.',
                    'The review screen carries the unanswered warning with role="alert", '
                    'and the submission requires an explicit confirmation that the machine '
                    'also enforces (E_SESSION_CONFIRMATION_REQUIRED).',
                ],
                'evidence': ['evidence/N21_RUNTIME_RECORD.json',
                             'evidence/N21_SESSION_TRACE.json'],
            },
            'AC3_domain_integrity': {
                'status': 'PASS' if all(status_of(name) == 'PASS' for name in (
                    'view_discipline', 'mode_registry', 'artifact_wiring',
                    'smoke_vectors')) else 'FAIL',
                'claims': [
                    'The exam render contains zero help-component markers and zero N16 '
                    'chain step text; a practice render contains zero exam-session fields '
                    'and zero exam answer content.',
                    'The mode registry maps mode to allowed components, and an '
                    'unregistered component fails the render contract loudly with '
                    'E_MODE_COMPONENT_NOT_ALLOWED.',
                    'The built artifact carries the policy island, the two runtime modules, '
                    'the shell markup and the boot call, with no external script.',
                    'The two in-file smoke vectors run against the built artifact.',
                ],
                'evidence': ['evidence/N21_RUNTIME_RECORD.json',
                             'src/smoke-subset.js',
                             'data/exam_policy.json'],
            },
        },
        'session_contract': {
            'states': manifest.get('exam_shell_layer', {}).get('session_states'),
            'events': manifest.get('exam_shell_layer', {}).get('session_events'),
            'transitions': manifest.get('exam_shell_layer', {}).get('transition_count'),
            'error_ids': manifest.get('exam_shell_layer', {}).get('error_ids'),
            'slots': manifest.get('exam_shell_layer', {}).get('slot_count'),
            'total_points': manifest.get('exam_shell_layer', {}).get('points_total'),
            'payload_contracts': manifest.get('exam_shell_layer', {}).get('payload_contracts'),
            'named_variants': manifest.get('exam_shell_layer', {}).get('named_variants'),
            'timer': manifest.get('exam_shell_layer', {}).get('timer'),
            'view_discipline': manifest.get('exam_shell_layer', {}).get('view_discipline'),
            'conflicts': manifest.get('exam_shell_layer', {}).get('conflicts'),
        },
        'byte_budget': record['budgets'],
        'digests': record['digests'],
        'sources': record['sources'],
        'handoff': record['handoff'],
        'not_claimed': [
            'No official examination, grade or proctoring status: the timer is advisory '
            'and labelled as such.',
            'No browser render, screen-reader, print or instructor acceptance: the '
            'accessibility evidence is a mechanical structural check (role="alert", '
            'aria-pressed, aria-current, focus movement); the renderer-level acceptance '
            'belongs to N22/N33/N34.',
            'No keyword matching as semantic grading: N21 stores the payload raw and '
            'never grades it.',
            'No claim that the four variants are four finished questions: they are four '
            'parameterisations of one family template.',
            'No persisted session: the state lives in memory for as long as the page '
            'does, and no localStorage write happens.',
        ],
    }
    VERIFICATION_OUT.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_OUT.write_text(json.dumps(verification, ensure_ascii=False, indent=2,
                                           sort_keys=True) + '\n', encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    authoring = run_tool([sys.executable, str(AUTHORING), '--check'], 'authoring_gate')
    compile_gate = run_tool([sys.executable, str(COMPILE), '--check'], 'compile_gate')
    exam_gate = run_tool([sys.executable, str(GATE)], 'exam_shell_gate')
    harness = run_harness()
    budgets = measure_budgets()

    gates = [authoring, compile_gate, exam_gate]
    harness_checks = harness.get('checks', {})
    harness_status = harness.get('status')
    status = 'PASS' if (all(gate['status'] == 'PASS' for gate in gates)
                        and harness_status == 'PASS'
                        and budgets['status'] == 'PASS') else 'FAIL'

    manifest: dict[str, Any] = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

    record = {
        'schema_version': 1,
        'owner': 'N21',
        'status': status,
        'policy_label': 'PROPOSED training policy (N21): 21 slots, 100 points, three forms '
                        'and an advisory 180-minute timer. Official programme facts: seven '
                        'topics, a written-on-paper examination and a maximum of 180 '
                        'minutes. The timer is advisory and never claims an official rule.',
        'gates': {
            'authoring_gate': authoring,
            'compile_gate': compile_gate,
            'exam_shell_gate': exam_gate,
        },
        'runtime': {
            'status': harness_status,
            'record': 'evidence/N21_RUNTIME_RECORD.json',
            'checks': {name: check.get('status') for name, check in harness_checks.items()},
            'transition_table_run': harness_checks.get('lifecycle', {}).get('transitions'),
            'timer_contract': harness_checks.get('timer_contract'),
            'view_discipline': harness_checks.get('view_discipline'),
            'mode_registry': harness_checks.get('mode_registry'),
            'navigation': harness_checks.get('navigation'),
            'keyboard_traversal': harness_checks.get('keyboard_traversal'),
            'submit_gate': harness_checks.get('submit_gate'),
            'buffer_race': harness_checks.get('buffer_race'),
            'terminal_record': harness_checks.get('terminal_record'),
            'end_to_end_trace': harness_checks.get('end_to_end_trace'),
        },
        'budgets': budgets,
        'digests': {
            'policy_island_digest': manifest.get('exam_shell_layer', {}).get('digest'),
            'policy_island_bytes': manifest.get('exam_shell_layer', {}).get('bytes'),
            'session_module_digest': manifest.get('exam_shell_layer', {}).get('session_module_digest'),
            'exam_module_digest': manifest.get('exam_shell_layer', {}).get('exam_module_digest'),
            'artifact_sha256': manifest.get('output_sha256'),
        },
        'sources': {
            'session_typescript': sha256_file(ROOT / 'src/session.ts'),
            'exam_typescript': sha256_file(ROOT / 'src/exam.ts'),
            'session_module': sha256_file(ROOT / 'src/compiled/session.js'),
            'exam_module': sha256_file(ROOT / 'src/compiled/exam.js'),
            'policy_author': sha256_file(AUTHORING),
            'compile_tool': sha256_file(COMPILE),
            'gate': sha256_file(GATE),
            'harness': sha256_file(HARNESS),
            'byte_budget': sha256_file(ROOT / 'tools/byte_budget.py'),
            'smoke_subset': sha256_file(ROOT / 'src/smoke-subset.js'),
            'shell_markup': sha256_file(ROOT / 'src/shell.html'),
        },
        'handoff': {
            'grading_N23': {
                'terminal_record': 'ExamSession.toTerminalRecord() — answers, flags, elapsed '
                                   'time, form id, transitions, unanswered and remediation lists.',
                'payload_kinds': ['numeric', 'option_select', 'ordering', 'matching', 'graph',
                                   'method', 'raw_text'],
                'note': 'The payloads are stored raw and unparsed; the normalisation and the '
                        'grading belong to N23.',
            },
            'logging_N25': {
                'session_trace': 'evidence/N21_SESSION_TRACE.json',
                'note': 'The trace is the integration input of the logging task; the session '
                        'state itself is never persisted without an explicit learner opt-in.',
            },
            'form_assembly_N24': {
                'slots': manifest.get('exam_shell_layer', {}).get('slot_count'),
                'note': 'The form is still the blueprint plan: the slot host shows the '
                        'pending-instance note until N24 supplies the instances.',
            },
            'remediation_N28': {
                'remediation_list': 'ExamSession.getRemediationSlotIds() — the post-exam '
                                    'list, because a remediation link cannot exist inside '
                                    'the exam before the submission.',
            },
            'inline_and_rebudget_N31': {
                'runtime_js_bytes': budgets['budgets'][1]['bytes'] if len(budgets.get('budgets', [])) > 1 else None,
                'artifact_total_bytes': budgets['budgets'][0]['bytes'] if budgets.get('budgets') else None,
                'note': 'The inline / lazy-load / re-budget decision belongs to N31; N21 '
                        're-set the interim ceilings on the measured requirement.',
            },
        },
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                   encoding='utf-8')
    write_trace(harness)
    write_verification_record(record, manifest, harness_checks)
    write_validation_record(record, manifest)
    print(json.dumps({
        'status': status,
        'out': str(out),
        'bytes': out.stat().st_size,
        'sha256': sha256_file(out),
        'gates': {gate['label']: gate['status'] for gate in gates},
        'runtime': harness_status,
        'runtime_checks': record['runtime']['checks'],
        'budgets': {entry['name']: f"{entry['kib']} KiB" for entry in budgets.get('budgets', [])},
    }, ensure_ascii=False, indent=2))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
