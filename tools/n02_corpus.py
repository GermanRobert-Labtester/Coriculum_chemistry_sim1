#!/usr/bin/env python3
"""Run the N02 coverage corpus and record deterministic evidence.

The corpus proves the happy path and every required negative fixture:
  * schema, counts, edges and planning cross-check pass on the real island;
  * a dangling edge and a scratch cycle fail with the ids named;
  * all 64 anchors resolve against the frozen masters, and a dangling or
    case-mismatched anchor fails with the anchor and master named;
  * the build gate refuses a deleted-outcome island by count assertion;
  * two builds over unchanged sources are byte-identical;
  * the shipped runtime renders 64 outcomes, single-sources a topic-name edit,
    and degrades honestly on a truncated island.

The record contains no timestamps, so two runs produce identical bytes. The
ledger records both run digests.
"""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import COVERAGE_PATH, DEST, sha256_file, sha256_bytes  # noqa: E402
from validate_coverage import format_summary, validate  # noqa: E402
from resolve_coverage_anchors import build_record  # noqa: E402

WORK = Path('/tmp/opencode/n02-corpus')
RECORD_PATH = DEST / 'evidence/N02_CORPUS_RECORD.json'


def run_command(args: list[str]) -> dict:
    completed = subprocess.run(args, cwd=DEST, capture_output=True, text=True)
    return {
        'command': ' '.join(args),
        'returncode': completed.returncode,
        'stdout': completed.stdout.strip(),
        'stderr': completed.stderr.strip(),
    }


def write_scratch(name: str, island: dict) -> Path:
    target = WORK / name / 'coverage.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(island, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return target


def first_error(report: dict) -> str:
    errors = report.get('errors') or ['no named failure']
    return errors[0]


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    island_path = DEST / COVERAGE_PATH
    island = json.loads(island_path.read_text(encoding='utf-8'))
    results: dict = {}
    failures: list[str] = []

    # 1. Happy-path validation.
    validation = validate(island_path=island_path, repo_root=DEST, masters_root=DEST)
    results['validation'] = {
        'status': validation['status'],
        'summary': format_summary(validation).splitlines()[0],
        'counts': validation.get('counts'),
        'edges': validation.get('checks', {}).get('edges'),
        'anchors': validation.get('checks', {}).get('anchors'),
        'labels': validation.get('checks', {}).get('labels'),
        'errors': validation.get('errors'),
    }
    if validation['status'] != 'PASS':
        failures.append('happy-path validation failed')

    # 2. Anchor resolution record.
    resolution = build_record(island_path, DEST, DEST)
    results['anchor_resolution'] = {
        'counts': resolution['counts'],
        'masters': [
            {'freeze_id': master['freeze_id'], 'sha256': master['sha256'], 'digest_matches_freeze': master['digest_matches_freeze']}
            for master in resolution['masters']
        ],
        'failures': resolution['failures'],
    }
    if resolution['failures'] or not all(m['digest_matches_freeze'] for m in resolution['masters']):
        failures.append('anchor resolution failed')

    # 3. Deleted outcome: validator and build gate.
    deleted = copy.deepcopy(island)
    removed = deleted['outcomes'].pop()
    deleted_path = write_scratch('deleted', deleted)
    deleted_report = validate(island_path=deleted_path, repo_root=DEST, masters_root=DEST)
    deleted_gate = run_command([
        sys.executable, str(DEST / 'tools/build.py'), '--island', str(deleted_path),
        '--out', str(WORK / 'deleted' / 'simulator.html'),
        '--manifest-out', str(WORK / 'deleted' / 'manifest.json'),
    ])
    results['deleted_outcome'] = {
        'removed_id': removed['id'],
        'validator_status': deleted_report['status'],
        'validator_first_error': first_error(deleted_report),
        'gate_returncode': deleted_gate['returncode'],
        'gate_first_line': deleted_gate['stderr'].splitlines()[0] if deleted_gate['stderr'] else '',
        'gate_refused_build': 'Refusing build' in deleted_gate['stderr'],
        'gate_names_count_assertion': 'Count assertion' in deleted_gate['stderr'],
    }
    if deleted_report['status'] != 'FAIL' or deleted_gate['returncode'] == 0:
        failures.append('deleted-outcome fixture did not fail')
    if 'Count assertion' not in deleted_gate['stderr'] or 'Refusing build' not in deleted_gate['stderr']:
        failures.append('deleted-outcome gate did not name the count assertion and refuse the build')

    # 4. Dangling edge.
    dangling = copy.deepcopy(island)
    next(outcome for outcome in dangling['outcomes'] if outcome['id'] == 'P1-01')['prerequisites'].append('P9-99')
    dangling_path = write_scratch('dangling-edge', dangling)
    dangling_report = validate(island_path=dangling_path, repo_root=DEST, masters_root=DEST)
    results['dangling_edge'] = {
        'status': dangling_report['status'],
        'first_error': first_error(dangling_report),
        'names_source_and_target': 'P1-01' in first_error(dangling_report) and 'P9-99' in first_error(dangling_report),
    }
    if dangling_report['status'] != 'FAIL' or 'P9-99' not in first_error(dangling_report):
        failures.append('dangling-edge fixture did not fail with the target named')

    # 5. Cycle.
    cycle = copy.deepcopy(island)
    next(outcome for outcome in cycle['outcomes'] if outcome['id'] == 'P1-01')['prerequisites'] = ['P1-02']
    next(outcome for outcome in cycle['outcomes'] if outcome['id'] == 'P1-02')['prerequisites'] = ['P1-01']
    cycle_path = write_scratch('cycle', cycle)
    cycle_report = validate(island_path=cycle_path, repo_root=DEST, masters_root=DEST)
    cycle_error = next((error for error in cycle_report['errors'] if error.startswith('Cyclic')), '')
    results['cycle'] = {
        'status': cycle_report['status'],
        'first_error': first_error(cycle_report),
        'cycle_error': cycle_error,
        'names_both_ids': 'P1-01' in cycle_error and 'P1-02' in cycle_error,
    }
    if cycle_report['status'] != 'FAIL' or not cycle_error:
        failures.append('cycle fixture did not fail as a cycle')

    # 6. Dangling anchor and case-exact anchor.
    anchor_scratch = copy.deepcopy(island)
    next(outcome for outcome in anchor_scratch['outcomes'] if outcome['id'] == 'P1-01')['master_anchor'] = 'nav-kluda'
    anchor_path = write_scratch('dangling-anchor', anchor_scratch)
    anchor_run = run_command([
        sys.executable, str(DEST / 'tools/resolve_coverage_anchors.py'),
        '--island', str(anchor_path), '--out', str(WORK / 'dangling-anchor' / 'record.json'),
    ])
    anchor_named = next((line.strip() for line in anchor_run['stderr'].splitlines() if '#nav-kluda' in line), '')
    results['dangling_anchor'] = {
        'returncode': anchor_run['returncode'],
        'stderr_first_line': anchor_run['stderr'].splitlines()[0] if anchor_run['stderr'] else '',
        'stderr_named_failure': anchor_named,
        'names_anchor_and_master': '#nav-kluda' in anchor_named and 'C1-MASTER' in anchor_named,
    }
    if anchor_run['returncode'] == 0 or '#nav-kluda' not in anchor_run['stderr'] or 'C1-MASTER' not in anchor_run['stderr']:
        failures.append('dangling-anchor fixture did not fail with anchor and master named')

    case_scratch = copy.deepcopy(island)
    next(outcome for outcome in case_scratch['outcomes'] if outcome['id'] == 'P1-01')['master_anchor'] = 'Stehiometrija'
    case_path = write_scratch('case-anchor', case_scratch)
    case_report = validate(island_path=case_path, repo_root=DEST, masters_root=DEST, check_planning=False)
    case_error = next((error for error in case_report['errors'] if error.startswith('Anchor resolution failed')), '')
    case_resolution = build_record(case_path, DEST, DEST)
    case_resolution_failure = case_resolution['failures'][0] if case_resolution['failures'] else {}
    results['case_exact_anchor'] = {
        'status': case_report['status'],
        'first_error': first_error(case_report),
        'anchor_error': case_error,
        'resolution_failure': case_resolution_failure,
        'rejects_case_insensitive_match': 'case-exact' in case_error and 'case-insensitive matches exist' in case_error,
    }
    if case_report['status'] != 'FAIL' or 'case-exact' not in case_error:
        failures.append('case-exact anchor fixture did not fail')
    if not case_resolution_failure:
        failures.append('case-exact anchor fixture did not produce a resolver failure record')

    # 7. Two-build parity over unchanged sources.
    build_out = WORK / 'parity' / 'simulator.html'
    build_manifest = WORK / 'parity' / 'manifest.json'
    build_out.parent.mkdir(parents=True, exist_ok=True)
    build_one = run_command([
        sys.executable, str(DEST / 'tools/build.py'), '--out', str(build_out), '--manifest-out', str(build_manifest),
    ])
    first_output = build_out.read_bytes()
    first_manifest = build_manifest.read_bytes()
    build_two = run_command([
        sys.executable, str(DEST / 'tools/build.py'), '--out', str(build_out), '--manifest-out', str(build_manifest),
    ])
    second_output = build_out.read_bytes()
    second_manifest = build_manifest.read_bytes()
    committed = DEST / 'output/simulator.html'
    results['build_parity'] = {
        'run_one_returncode': build_one['returncode'],
        'run_two_returncode': build_two['returncode'],
        'output_sha256_first': sha256_bytes(first_output),
        'output_sha256_second': sha256_bytes(second_output),
        'output_bytes': len(first_output),
        'manifest_sha256_first': sha256_bytes(first_manifest),
        'manifest_sha256_second': sha256_bytes(second_manifest),
        'outputs_identical': first_output == second_output,
        'manifests_identical': first_manifest == second_manifest,
        'committed_output_matches_fresh_build': committed.is_file() and committed.read_bytes() == first_output,
    }
    if not results['build_parity']['outputs_identical'] or not results['build_parity']['manifests_identical']:
        failures.append('two builds over unchanged sources differ')
    if not results['build_parity']['committed_output_matches_fresh_build']:
        failures.append('committed output/simulator.html does not match a fresh build')

    # 8. Runtime harness.
    runtime = run_command(['node', str(DEST / 'tools/check_coverage_runtime.js'), '--json'])
    try:
        runtime_report = json.loads(runtime['stdout'])
    except json.JSONDecodeError:
        runtime_report = {'status': 'FAIL', 'failures': ['runtime harness did not emit JSON'], 'raw': runtime['stdout']}
    results['runtime'] = {
        'returncode': runtime['returncode'],
        'status': runtime_report.get('status'),
        'checks': runtime_report.get('checks'),
        'failures': runtime_report.get('failures'),
    }
    if runtime['returncode'] != 0 or runtime_report.get('status') != 'PASS':
        failures.append('runtime harness failed')

    # 9. Artifact digests.
    artifacts = [
        'data/coverage.json',
        'src/shell.html',
        'src/coverage-loader.js',
        'src/coverage-view.js',
        'tools/coverage_common.py',
        'tools/validate_coverage.py',
        'tools/resolve_coverage_anchors.py',
        'tools/build.py',
        'tools/check_coverage_runtime.js',
        'output/simulator.html',
        'output/build-manifest.json',
        'evidence/N02_ANCHOR_RESOLUTION.json',
        'evidence/N02_VALIDATION_RECORD.json',
    ]
    artifact_records = []
    for relative in artifacts:
        path = DEST / relative
        if path.is_file():
            artifact_records.append({'path': relative, 'sha256': sha256_file(path), 'bytes': path.stat().st_size})
        else:
            artifact_records.append({'path': relative, 'status': 'MISSING'})
    results['artifacts'] = artifact_records

    record = {
        'schema_version': 1,
        'task': 'N02',
        'artifact': 'coverage-corpus',
        'scope': 'Coverage island, planning cross-check, edge fixtures, frozen-master anchor resolution, build gate, runtime loader and single-sourcing proof.',
        'labels': {
            'execution': 'VERIFIED (2026-11-17, this environment)',
            'master_digests': 'bound to N01 source freeze recorded VERIFIED (2026-11-16)',
        },
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'results': results,
        'commands': [
            'python3 tools/validate_coverage.py --report evidence/N02_VALIDATION_RECORD.json',
            'python3 tools/resolve_coverage_anchors.py --out evidence/N02_ANCHOR_RESOLUTION.json',
            'python3 tools/build.py',
            'node tools/check_coverage_runtime.js --json',
            'python3 tools/n02_corpus.py',
        ],
    }
    text = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    RECORD_PATH.write_text(text, encoding='utf-8')
    print(('PASS' if not failures else 'FAIL') + f' N02 corpus: {RECORD_PATH}')
    print(f'  record sha256={sha256_file(RECORD_PATH)} bytes={RECORD_PATH.stat().st_size}')
    for failure in failures:
        print(f'  - {failure}')
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
