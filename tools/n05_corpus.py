#!/usr/bin/env python3
"""N05 deterministic verification corpus & evidence generator.

Executes and records:
  1. Cross-language PRNG determinism proof (11 seeds x 100 u64 draws, bounded,
     Fisher-Yates shuffle, illegal seed/bound rejections, JS+Python constant
     perturbation catches) -> evidence/N05_PRNG_CONTRACT.json.
  2. Oracle independence manifest + 3 hand-computed spot checks + Stratum 1
     oracle grading + coverage table -> evidence/N05_ORACLE_RECORD.json.
  3. Stratum 1 schema validation & N04 bank cross-check + retired-id reuse
     negative fixture.
  4. Twice-fresh-process oracle replay parity & conventions perturbation-and-revert
     proof (changing burette_volume tolerance 0.05 -> 0.01 flips ONLY the
     affected vector GV-S1-T2-Q10-01; reverting restores exact replay digest).
  5. Build gate refusal (invalid scratch golden vectors) + double-build parity +
     Node.js runtime harness -> evidence/N05_CORPUS_RECORD.json.

Produces zero timestamps so consecutive runs are byte-identical.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_prng_determinism  # noqa: E402
import golden_oracle  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_golden_vectors import validate_all as validate_golden_vectors  # noqa: E402

WORK = Path('/tmp/opencode/n05-corpus')
PRNG_RECORD_PATH = DEST / 'evidence/N05_PRNG_CONTRACT.json'
ORACLE_RECORD_PATH = DEST / 'evidence/N05_ORACLE_RECORD.json'
CORPUS_RECORD_PATH = DEST / 'evidence/N05_CORPUS_RECORD.json'


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _run_cmd(args: list[str]) -> dict[str, Any]:
    res = subprocess.run(args, cwd=DEST, capture_output=True, text=True)
    return {
        'command': ' '.join(args),
        'returncode': res.returncode,
        'stdout': res.stdout.strip(),
        'stderr': res.stderr.strip(),
    }


def run_spot_checks(conventions: dict[str, Any], corpus: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {v['vector_id']: v for v in corpus['vectors']}

    # Spot check 1: Numeric unit conversion & sig figs (GV-S1-T2-Q01-01)
    # Hand calculation: 4.50e3 mg = 4500 mg * (1/1000 g/mg) = 4.50 g; diff = 0 <= 0.01 g; 4.50e3 has 3 sig figs == 3.
    v1 = by_id['GV-S1-T2-Q01-01']
    o1 = golden_oracle.grade_vector(v1['instance'], v1['submission'], conventions)
    sc1_hand = {
        'hand_converted_g': '4.50',
        'hand_sig_figs': 3,
        'hand_verdict_class': 'correct',
        'hand_error_class': 'NONE',
        'hand_machine_points': 2.0,
    }
    sc1_match = (
        o1['verdict_class'] == sc1_hand['hand_verdict_class']
        and o1['error_class'] == sc1_hand['hand_error_class']
        and o1['machine_checked_points'] == sc1_hand['hand_machine_points']
    )

    # Spot check 2: Tolerance-edge inclusive + half_up rounding tie (GV-S1-T2-Q10-01 & GV-S1-T4-Q09-01)
    # Hand calculation A: |16.30 - 16.25| = 0.05 <= 0.05 (burette_volume) -> correct.
    # Hand calculation B: 1.125 rounded half_up to 2 dp = 1.13; |1.14 - 1.13| = 0.01 <= 0.01 (mass) -> correct.
    v2a = by_id['GV-S1-T2-Q10-01']
    o2a = golden_oracle.grade_vector(v2a['instance'], v2a['submission'], conventions)
    v2b = by_id['GV-S1-T4-Q09-01']
    o2b = golden_oracle.grade_vector(v2b['instance'], v2b['submission'], conventions)
    rounded_tie = str(golden_oracle.round_half_up_decimals(Decimal('1.125'), 2))
    sc2_match = (
        o2a['verdict_class'] == 'correct'
        and o2b['verdict_class'] == 'correct'
        and rounded_tie == '1.13'
    )

    # Spot check 3: V-04 density-defect error-class (GV-S1-T3-Q02-02)
    # Hand calculation: w=10.0% m/m, rho=1.070 g/mL -> true gamma = 107.0 g/L;
    # submitted 100.0 g/L == 107.0 / 1.070 (omitted rho!) -> incorrect, DIMENSIONAL_INCONSISTENCY.
    v3 = by_id['GV-S1-T3-Q02-02']
    o3 = golden_oracle.grade_vector(v3['instance'], v3['submission'], conventions)
    sc3_match = (
        o3['verdict_class'] == 'incorrect'
        and o3['error_class'] == 'DIMENSIONAL_INCONSISTENCY'
        and o3['machine_checked_points'] == 0.0
    )

    return [
        {
            'id': 'SPOT-1-NUMERIC-CONVERSION-SIGFIG',
            'vector_id': v1['vector_id'],
            'hand_computation': sc1_hand,
            'oracle_verdict': o1['verdict_class'],
            'oracle_error_class': o1['error_class'],
            'oracle_machine_points': o1['machine_checked_points'],
            'agreed': sc1_match,
        },
        {
            'id': 'SPOT-2-TOLERANCE-EDGE-AND-HALF-UP',
            'vector_ids': [v2a['vector_id'], v2b['vector_id']],
            'hand_computation': {
                'burette_abs_diff': '0.05 <= 0.05 (inclusive)',
                'half_up_1_125_2dp': rounded_tie,
                'mass_abs_diff': '|1.14 - 1.13| = 0.01 <= 0.01',
            },
            'oracle_verdicts': [o2a['verdict_class'], o2b['verdict_class']],
            'agreed': sc2_match,
        },
        {
            'id': 'SPOT-3-V04-DENSITY-DEFECT-ERROR-CLASS',
            'vector_id': v3['vector_id'],
            'hand_computation': {
                'true_gamma_g_per_L': '107.0',
                'submitted_omitted_rho': '100.0 (= 107.0 / 1.070)',
                'hand_verdict_class': 'incorrect',
                'hand_error_class': 'DIMENSIONAL_INCONSISTENCY',
            },
            'oracle_verdict': o3['verdict_class'],
            'oracle_error_class': o3['error_class'],
            'agreed': sc3_match,
        },
    ]


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []

    # 1. PRNG cross-language determinism & perturbation catch
    prng_report = check_prng_determinism.verify_determinism()
    _write_json(PRNG_RECORD_PATH, prng_report)
    if prng_report['status'] != 'PASS':
        failures.append('PRNG determinism check failed')

    # 2. Oracle manifest & spot checks
    conventions = load_json(DEST / 'data/conventions.json')
    corpus = load_json(DEST / 'data/golden_vectors.json')
    manifest = golden_oracle.verify_import_manifest()
    spot_checks = run_spot_checks(conventions, corpus)
    if not manifest['independent_of_engines']:
        failures.append('Oracle import manifest failed independence check')
    if not all(sc['agreed'] for sc in spot_checks):
        failures.append('One or more hand-computed oracle spot checks disagreed')

    # 3. Full golden vectors validation (includes N04 validate_bank cross-check)
    val_report = validate_golden_vectors(repo_root=DEST)
    if val_report['status'] != 'PASS':
        failures.append(f'validate_golden_vectors failed: {val_report["errors"]}')

    oracle_record = {
        'schema_version': 1,
        'task': 'N05',
        'status': 'PASS' if (manifest['independent_of_engines'] and all(sc['agreed'] for sc in spot_checks) and val_report['status'] == 'PASS') else 'FAIL',
        'import_manifest': manifest,
        'spot_checks': spot_checks,
        'coverage_table': val_report['counts'],
        'bank_cross_check': val_report['bank_cross_check'],
        'oracle_results_sha256': val_report['oracle_results_sha256'],
        'corpus_sha256': val_report['corpus_sha256'],
    }
    _write_json(ORACLE_RECORD_PATH, oracle_record)

    # 4. Twice-fresh-process oracle replay & conventions perturbation-and-revert
    replay1 = _run_cmd(['python3', 'tools/golden_oracle.py', '--json'])
    replay2 = _run_cmd(['python3', 'tools/golden_oracle.py', '--json'])
    if replay1['returncode'] != 0 or replay2['returncode'] != 0:
        failures.append('Oracle replay subprocess failed')
    replay1_json = json.loads(replay1['stdout'])
    replay2_json = json.loads(replay2['stdout'])
    replay_parity = (
        replay1['stdout'] == replay2['stdout']
        and replay1_json['results_sha256'] == replay2_json['results_sha256']
    )
    if not replay_parity:
        failures.append('Fresh-process oracle replays did not match byte-for-byte')

    # Perturb scratch copy of conventions: burette_volume 0.05 -> 0.01
    perturbed_conv = copy.deepcopy(conventions)
    for qc in perturbed_conv['tolerances']['quantity_classes']:
        if qc['id'] == 'burette_volume':
            qc['absolute']['value'] = '0.01'
    perturbed_conv_path = WORK / 'conventions_perturbed_burette.json'
    _write_json(perturbed_conv_path, perturbed_conv)

    perturbed_run = _run_cmd(['python3', 'tools/golden_oracle.py', '--conventions', str(perturbed_conv_path), '--json'])
    perturbed_json = json.loads(perturbed_run['stdout'])
    base_by_id = {r['vector_id']: r['verdict'] for r in replay1_json['results']}
    pert_by_id = {r['vector_id']: r['verdict'] for r in perturbed_json['results']}
    flipped_ids = [
        vid for vid in sorted(base_by_id)
        if base_by_id[vid]['verdict_class'] != pert_by_id[vid]['verdict_class']
        or base_by_id[vid]['error_class'] != pert_by_id[vid]['error_class']
    ]
    # Revert / re-run against real unmodified conventions
    reverted_run = _run_cmd(['python3', 'tools/golden_oracle.py', '--json'])
    reverted_json = json.loads(reverted_run['stdout'])
    revert_restored = (reverted_json['results_sha256'] == replay1_json['results_sha256'])

    if flipped_ids != ['GV-S1-T2-Q10-01']:
        failures.append(f'Conventions perturbation flipped unexpected vectors: {flipped_ids}')
    if not revert_restored:
        failures.append('Reverted conventions run did not restore replay digest')

    # 5. Retired-ID reuse negative fixture
    retired_corpus = copy.deepcopy(corpus)
    reused_id = retired_corpus['vectors'][0]['vector_id']
    retired_corpus['retired_ids'] = [{'retired_id': reused_id, 'replaced_by': 'GV-S1-T1-Q02-99', 'reason': 'fixture', 'ledger_ref': 'N05'}]
    retired_path = WORK / 'golden_vectors_retired_reuse.json'
    _write_json(retired_path, retired_corpus)
    retired_rep = validate_golden_vectors(repo_root=DEST, vectors_path=retired_path)
    if retired_rep['status'] != 'FAIL' or not any(reused_id in e for e in retired_rep['errors']):
        failures.append('Retired-id reuse fixture did not fail naming the reused id')

    # 6. Build gate refusal (scratch invalid golden vectors) and double-build parity
    gate_fail_out = WORK / 'gate_fail.html'
    gate_fail_man = WORK / 'gate_fail_manifest.json'
    gate_fail_cmd = _run_cmd([
        'python3', 'tools/build.py',
        '--golden-vectors', str(retired_path),
        '--out', str(gate_fail_out),
        '--manifest-out', str(gate_fail_man),
    ])
    if gate_fail_cmd['returncode'] == 0 or gate_fail_out.exists() or 'golden_vectors' not in gate_fail_cmd['stderr']:
        failures.append('Build gate did not refuse invalid golden vectors before writing')

    b1_out = WORK / 'sim1.html'
    b1_man = WORK / 'man1.json'
    b2_out = WORK / 'sim2.html'
    b2_man = WORK / 'man2.json'
    b1 = _run_cmd(['python3', 'tools/build.py', '--out', str(b1_out), '--manifest-out', str(b1_man)])
    b2 = _run_cmd(['python3', 'tools/build.py', '--out', str(b2_out), '--manifest-out', str(b2_man)])
    if b1['returncode'] != 0 or b2['returncode'] != 0:
        failures.append('Scratch double-build failed')
    build_parity = sha256_file(b1_out) == sha256_file(b2_out)
    if not build_parity:
        failures.append('Scratch double-build outputs were not byte-identical')

    # 7. Runtime harness (Node.js)
    rt = _run_cmd(['node', 'tools/check_golden_vectors_runtime.js', '--json'])
    if rt['returncode'] != 0:
        failures.append(f'Runtime harness failed: {rt["stderr"]}')
    rt_json = json.loads(rt['stdout'])

    corpus_record = {
        'schema_version': 1,
        'task': 'N05',
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'artifacts': {
            'data/seed_policy.json': sha256_file(DEST / 'data/seed_policy.json'),
            'data/prng_contract_vectors.json': sha256_file(DEST / 'data/prng_contract_vectors.json'),
            'data/golden_vector_protocol.json': sha256_file(DEST / 'data/golden_vector_protocol.json'),
            'data/golden_vectors.json': sha256_file(DEST / 'data/golden_vectors.json'),
            'tools/prng.py': sha256_file(DEST / 'tools/prng.py'),
            'src/prng.js': sha256_file(DEST / 'src/prng.js'),
            'tools/golden_oracle.py': sha256_file(DEST / 'tools/golden_oracle.py'),
            'tools/validate_golden_vectors.py': sha256_file(DEST / 'tools/validate_golden_vectors.py'),
            'src/golden-vectors-loader.js': sha256_file(DEST / 'src/golden-vectors-loader.js'),
            'src/shell.html': sha256_file(DEST / 'src/shell.html'),
            'tools/build.py': sha256_file(DEST / 'tools/build.py'),
            'output/simulator.html': sha256_file(DEST / 'output/simulator.html'),
            'output/build-manifest.json': sha256_file(DEST / 'output/build-manifest.json'),
        },
        'prng_determinism': {
            'status': prng_report['status'],
            'seed_count': prng_report['seed_count'],
            'draws_per_seed': prng_report['draws_per_seed'],
            'table_sha256': prng_report['table_sha256'],
            'green_divergences': prng_report['green_comparison']['divergences_count'],
            'js_gamma_perturbation_caught': prng_report['negative_perturbation_js_gamma']['caught'],
            'py_mul1_perturbation_caught': prng_report['negative_perturbation_py_mul1']['caught'],
        },
        'replay_and_perturbation': {
            'replay_run1_sha256': sha256_bytes(replay1['stdout'].encode('utf-8')),
            'replay_run2_sha256': sha256_bytes(replay2['stdout'].encode('utf-8')),
            'replay_results_sha256': replay1_json['results_sha256'],
            'replay_identical': replay_parity,
            'perturbed_conventions_change': 'burette_volume.absolute.value: 0.05 -> 0.01',
            'perturbed_results_sha256': perturbed_json['results_sha256'],
            'flipped_vector_ids': flipped_ids,
            'flipped_detail': {
                'vector_id': 'GV-S1-T2-Q10-01',
                'baseline': {'verdict_class': base_by_id['GV-S1-T2-Q10-01']['verdict_class'], 'error_class': base_by_id['GV-S1-T2-Q10-01']['error_class']},
                'perturbed': {'verdict_class': pert_by_id['GV-S1-T2-Q10-01']['verdict_class'], 'error_class': pert_by_id['GV-S1-T2-Q10-01']['error_class']},
            },
            'reverted_results_sha256': reverted_json['results_sha256'],
            'revert_restored': revert_restored,
        },
        'retired_id_negative_fixture': {
            'status': retired_rep['status'],
            'errors': retired_rep['errors'],
        },
        'build_gate': {
            'refusal_returncode': gate_fail_cmd['returncode'],
            'refusal_artifact_written': gate_fail_out.exists(),
            'refusal_stderr': gate_fail_cmd['stderr'],
            'double_build_parity': build_parity,
            'double_build_sha256': sha256_file(b1_out),
            'committed_matches_fresh_build': sha256_file(DEST / 'output/simulator.html') == sha256_file(b1_out),
        },
        'runtime_harness': rt_json,
    }
    _write_json(CORPUS_RECORD_PATH, corpus_record)

    print(
        f'{corpus_record["status"]} n05-corpus: prng={prng_report["status"]}, '
        f'oracle={oracle_record["status"]}, replay={replay_parity}, '
        f'flipped={flipped_ids}, revert={revert_restored}, build_parity={build_parity}, '
        f'runtime={rt_json["status"]}'
    )
    if failures:
        for f in failures:
            print(f'  - {f}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
