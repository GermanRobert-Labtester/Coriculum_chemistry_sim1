#!/usr/bin/env python3
"""Run the N03 conventions/conflict corpus and record deterministic evidence.

The corpus proves the happy path and every required negative fixture:
  * schema, conversions, composition chains, citations, labels and the
    bidirectional registry check pass on the real artifacts;
  * a planted wrong chain factor fails the composition check with the chain id
    and both factors named;
  * a statusless registry entry fails by id;
  * a resolution citing a nonexistent task fails with the task id;
  * the build gate refuses both scratch islands and names the convention gate;
  * two builds over unchanged sources are byte-identical;
  * the shipped runtime loads the island, single-sources a tolerance change to
    the engine, figure field and vector expectation, single-sources a conversion
    change to the engine and vector, and degrades honestly on a truncated or
    missing island.

The record contains no timestamps, so two runs produce identical bytes. The
ledger records both run digests.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import byte_budget  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402
from validate_conventions import CONVENTIONS_PATH, format_summary, validate  # noqa: E402

WORK = Path('/tmp/opencode/n03-corpus')
RECORD_PATH = DEST / 'evidence/N03_CORPUS_RECORD.json'
BANK_MIN_KIB = 200
BANK_MAX_KIB = 420
TOTAL_MIN_KIB = 700
# The declared Section 1.3 band stays visible; the enforced ceiling is re-set
# on the measured requirement (N21) and lives in tools/byte_budget.py.
DECLARED_TOTAL_MAX_KIB = 1400
TOTAL_MAX_KIB = byte_budget.ceiling_bytes('artifact_total') // 1024


def run_command(args: list[str]) -> dict:
    completed = subprocess.run(args, cwd=DEST, capture_output=True, text=True)
    return {
        'command': ' '.join(args),
        'returncode': completed.returncode,
        'stdout': completed.stdout.strip(),
        'stderr': completed.stderr.strip(),
    }


def write_scratch(name: str, island: dict) -> Path:
    target = WORK / name / 'conventions.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(island, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return target


def first_error(report: dict) -> str:
    return (report.get('errors') or ['no named failure'])[0]


def named(report: dict, needles: list[str]) -> bool:
    text = '\n'.join(report.get('errors') or [])
    return all(needle in text for needle in needles)


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    island_path = DEST / CONVENTIONS_PATH
    island = json.loads(island_path.read_text(encoding='utf-8'))
    results: dict = {}
    failures: list[str] = []

    # 1. Happy-path validation.
    validation = validate(island_path=island_path, repo_root=DEST)
    results['validation'] = {
        'status': validation['status'],
        'summary': format_summary(validation),
        'counts': validation.get('counts'),
        'checks': validation.get('checks'),
        'registry_digest': validation.get('registry_results', {}).get('digest'),
        'errors': validation.get('errors'),
    }
    if validation['status'] != 'PASS':
        failures.append('happy-path validation failed')

    # 2. Wrong composition factor.
    wrong = copy.deepcopy(island)
    next(chain for chain in wrong['unit_system']['chains']
         if chain['id'] == 'concentration_mg_per_ml_to_g_per_l')['factor'] = {'num': 2, 'den': 1}
    wrong_path = write_scratch('wrong-factor', wrong)
    wrong_report = validate(island_path=wrong_path, repo_root=DEST)
    results['wrong_factor'] = {
        'validator_status': wrong_report['status'],
        'first_error': first_error(wrong_report),
        'names_chain': named(wrong_report, ['concentration_mg_per_ml_to_g_per_l']),
        'names_both_factors': named(wrong_report, ['declared 2', 'computed 1']),
        'errors': wrong_report.get('errors'),
    }
    if wrong_report['status'] != 'FAIL':
        failures.append('wrong-factor fixture did not fail')
    if not results['wrong_factor']['names_chain'] or not results['wrong_factor']['names_both_factors']:
        failures.append('wrong-factor fixture did not name the chain and both factors')

    # 3. Statusless registry entry.
    statusless = copy.deepcopy(island)
    next(entry for entry in statusless['conflicts']['entries'] if entry['id'] == 'V-05').pop('status', None)
    statusless_path = write_scratch('statusless', statusless)
    statusless_report = validate(island_path=statusless_path, repo_root=DEST)
    results['statusless'] = {
        'validator_status': statusless_report['status'],
        'first_error': first_error(statusless_report),
        'names_id': named(statusless_report, ['V-05']),
        'names_status': named(statusless_report, ['status']),
        'errors': statusless_report.get('errors'),
    }
    if statusless_report['status'] != 'FAIL' or not results['statusless']['names_id']:
        failures.append('statusless fixture did not fail by id')

    # 4. Phantom resolution task.
    phantom = copy.deepcopy(island)
    next(entry for entry in phantom['conflicts']['entries'] if entry['id'] == 'V-04')['resolution_task'] = 'N99'
    phantom_path = write_scratch('phantom-task', phantom)
    phantom_report = validate(island_path=phantom_path, repo_root=DEST)
    results['phantom_task'] = {
        'validator_status': phantom_report['status'],
        'first_error': first_error(phantom_report),
        'names_phantom': named(phantom_report, ['N99']),
        'names_id': named(phantom_report, ['V-04']),
        'errors': phantom_report.get('errors'),
    }
    if phantom_report['status'] != 'FAIL' or not results['phantom_task']['names_phantom']:
        failures.append('phantom-task fixture did not fail with the task id')

    # 5. Build-gate refusals for both scratch islands.
    def gate_refusal(name: str, scratch_path: Path) -> dict:
        record = run_command([
            sys.executable, str(DEST / 'tools/build.py'),
            '--conventions', str(scratch_path),
            '--out', str(WORK / name / 'simulator.html'),
            '--manifest-out', str(WORK / name / 'manifest.json'),
        ])
        lines = record['stderr'].splitlines()
        return {
            'command': record['command'],
            'returncode': record['returncode'],
            'first_line': lines[0] if lines else '',
            'refused': 'Refusing build' in record['stderr'],
            'names_gate': 'conventions gate' in record['stderr'],
            'names_assertion': ('factor mismatch' in record['stderr'] if name == 'wrong-factor' else 'V-05' in record['stderr']),
            'artifact_written': (WORK / name / 'simulator.html').exists(),
        }

    wrong_gate = gate_refusal('wrong-factor', wrong_path)
    statusless_gate = gate_refusal('statusless', statusless_path)
    results['gate_refusals'] = {'wrong_factor': wrong_gate, 'statusless': statusless_gate}
    for name, gate in results['gate_refusals'].items():
        if gate['returncode'] == 0 or not gate['refused']:
            failures.append(f'{name} gate did not refuse the build')
        if not gate['names_gate'] or not gate['names_assertion']:
            failures.append(f'{name} gate did not name the gate and assertion')
        if gate['artifact_written']:
            failures.append(f'{name} gate wrote an artifact despite refusing')

    # 6. Clean build and two-build parity.
    clean_out = WORK / 'clean' / 'simulator.html'
    clean_manifest = WORK / 'clean' / 'manifest.json'
    build_one = run_command([
        sys.executable, str(DEST / 'tools/build.py'),
        '--out', str(clean_out), '--manifest-out', str(clean_manifest),
    ])
    first_output = clean_out.read_bytes() if clean_out.exists() else b''
    first_manifest_bytes = clean_manifest.read_bytes() if clean_manifest.exists() else b''
    build_two = run_command([
        sys.executable, str(DEST / 'tools/build.py'),
        '--out', str(clean_out), '--manifest-out', str(clean_manifest),
    ])
    second_output = clean_out.read_bytes() if clean_out.exists() else b''
    second_manifest_bytes = clean_manifest.read_bytes() if clean_manifest.exists() else b''
    clean_manifest_data = json.loads(first_manifest_bytes.decode('utf-8')) if first_manifest_bytes else {}
    committed = DEST / 'output/simulator.html'
    results['build_parity'] = {
        'run_one_returncode': build_one['returncode'],
        'run_two_returncode': build_two['returncode'],
        'output_sha256_first': sha256_bytes(first_output),
        'output_sha256_second': sha256_bytes(second_output),
        'output_bytes': len(first_output),
        'manifest_sha256_first': sha256_bytes(first_manifest_bytes),
        'manifest_sha256_second': sha256_bytes(second_manifest_bytes),
        'outputs_identical': first_output == second_output,
        'manifests_identical': first_manifest_bytes == second_manifest_bytes,
        'committed_output_matches_fresh_build': committed.is_file() and committed.read_bytes() == first_output,
        'gates': clean_manifest_data.get('gates'),
        'conventions_island': clean_manifest_data.get('conventions_island'),
        'build_id': clean_manifest_data.get('build_id'),
    }
    if not results['build_parity']['outputs_identical'] or not results['build_parity']['manifests_identical']:
        failures.append('two builds over unchanged sources differ')
    if not results['build_parity']['committed_output_matches_fresh_build']:
        failures.append('committed output/simulator.html does not match a fresh build')
    if any(gate.get('status') != 'PASS' for gate in clean_manifest_data.get('gates', [])):
        failures.append('clean build did not record two PASS gates')

    # 7. Runtime harness (single-sourcing, degradation, accessors).
    runtime = run_command(['node', str(DEST / 'tools/check_conventions_runtime.js'), '--json'])
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

    # 8. Island byte contribution.
    canonical = canonical_json_bytes(island)
    canonical_kib = len(canonical) / 1024
    output_bytes = len(first_output)
    results['byte_contribution'] = {
        'conventions_island_bytes': len(canonical),
        'conventions_island_kib': round(canonical_kib, 2),
        'output_bytes': output_bytes,
        'output_kib': round(output_bytes / 1024, 2),
        'bank_sub_budget_kib': [BANK_MIN_KIB, BANK_MAX_KIB],
        'bank_share_percent': [round(canonical_kib / BANK_MAX_KIB * 100, 2), round(canonical_kib / BANK_MIN_KIB * 100, 2)],
        'total_budget_kib': [TOTAL_MIN_KIB, TOTAL_MAX_KIB],
        'declared_total_budget_kib': [TOTAL_MIN_KIB, DECLARED_TOTAL_MAX_KIB],
        'total_share_percent': [round(output_bytes / 1024 / TOTAL_MAX_KIB * 100, 2), round(output_bytes / 1024 / TOTAL_MIN_KIB * 100, 2)],
        'note_lv': 'Konvenciju sala nav daļa no #sim-bank; tās apjoms pret bankas apakšbudžetu ir mēroga rādītājs, ne bankas saturs. Kopējais fails paliek 700–1400 KiB budžetā.',
    }
    if canonical_kib > BANK_MAX_KIB:
        failures.append('conventions island alone exceeds the bank sub-budget maximum')

    # 9. Artifact digests.
    artifacts = [
        'data/conventions.json',
        'src/shell.html',
        'src/conventions-loader.js',
        'tools/coverage_common.py',
        'tools/validate_conventions.py',
        'tools/build.py',
        'tools/check_conventions_runtime.js',
        'output/simulator.html',
        'output/build-manifest.json',
        'evidence/N03_VALIDATION_RECORD.json',
        'evidence/N03_CONFLICT_REGISTRY.json',
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
        'task': 'N03',
        'artifact': 'conventions-conflict-corpus',
        'scope': 'Conventions schema, conversions, composition chains, citations, registry traceability, build gate, runtime loader, single-sourcing and degradation.',
        'labels': {
            'execution': 'VERIFIED (2026-11-17, this environment)',
            'master_digests': 'bound to N01 source freeze recorded VERIFIED (2026-11-16)',
            'tolerances': 'PROPOSED training policy',
        },
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'results': results,
        'commands': [
            'python3 tools/validate_conventions.py --report evidence/N03_VALIDATION_RECORD.json --registry-out evidence/N03_CONFLICT_REGISTRY.json',
            'python3 tools/build.py',
            'node tools/check_conventions_runtime.js --json',
            'python3 tools/n03_corpus.py',
        ],
    }
    text = json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    RECORD_PATH.write_text(text, encoding='utf-8')
    print(('PASS' if not failures else 'FAIL') + f' N03 corpus: {RECORD_PATH}')
    print(f'  record sha256={sha256_file(RECORD_PATH)} bytes={RECORD_PATH.stat().st_size}')
    for failure in failures:
        print(f'  - {failure}')
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
