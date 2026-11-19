#!/usr/bin/env python3
"""N04 deterministic corpus, permanent negative fixtures, gate checks, and runtime harness."""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_bank import SCHEMA_PATH, validate_bank  # noqa: E402

FIXTURES_DIR = DEST / 'tools/fixtures/n04'
WORK = Path('/tmp/opencode/n04-corpus')
RECORD_PATH = DEST / 'evidence/N04_CORPUS_RECORD.json'

TYPE_TO_CLASS = {
    'Q01': 'numeric', 'Q02': 'numeric', 'Q03': 'method', 'Q04': 'method',
    'Q05': 'method', 'Q06': 'matching', 'Q07': 'option_select', 'Q08': 'ordering',
    'Q09': 'numeric', 'Q10': 'numeric', 'Q11': 'graph', 'Q12': 'graph',
    'Q13': 'method', 'Q14': 'option_select', 'Q15': 'method', 'Q16': 'method',
    'Q17': 'method', 'Q18': 'option_select',
}

TYPE_TO_ENGINE = {
    'Q01': 'N17-numeric', 'Q02': 'N17-numeric', 'Q03': 'N18-symbolic', 'Q04': 'N18-symbolic',
    'Q05': 'N18-symbolic', 'Q06': 'N19-method', 'Q07': 'N19-method', 'Q08': 'N19-method',
    'Q09': 'N17-numeric', 'Q10': 'N17-numeric', 'Q11': 'N17-numeric', 'Q12': 'N17-numeric',
    'Q13': 'N19-method', 'Q14': 'N19-method', 'Q15': 'self-assessed', 'Q16': 'self-assessed',
    'Q17': 'N19-method', 'Q18': 'N19-method',
}

SAMPLE_SHA = 'f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9'


def make_payload(payload_class: str) -> dict[str, Any]:
    if payload_class == 'numeric':
        return {
            'expected_value': 8.0,
            'unit': 'g',
            'tolerance_class': 'mass',
            'sig_figs': 3,
            'display_lv': '8,00 g',
            'input_fields': [{'field_id': 'ans', 'label_lv': 'Masa (g)', 'kind': 'number'}],
        }
    if payload_class == 'option_select':
        return {
            'options': [
                {'option_id': 'A', 'text_lv': 'Pareizā opcija'},
                {'option_id': 'B', 'text_lv': 'Maldinātājs'},
            ],
            'correct_ids': ['A'],
            'distractors': [{'option_id': 'B', 'rationale_lv': 'Tipiska kļūda'}],
            'requires_justification': False,
        }
    if payload_class == 'ordering':
        return {
            'items': [
                {'item_id': 'S1', 'text_lv': 'Pirmais solis'},
                {'item_id': 'S2', 'text_lv': 'Otrais solis'},
            ],
            'correct_order': ['S1', 'S2'],
            'explanation_prompt_lv': 'Izskaidro kritisko soli.',
        }
    if payload_class == 'matching':
        return {
            'left_items': [{'id': 'L1', 'text_lv': 'Birete'}, {'id': 'L2', 'text_lv': 'Mērkolba'}],
            'right_items': [{'id': 'R1', 'text_lv': 'Titrēšana'}, {'id': 'R2', 'text_lv': 'Šķīduma pagatavošana'}],
            'correct_pairs': [{'left_id': 'L1', 'right_id': 'R1'}, {'left_id': 'L2', 'right_id': 'R2'}],
        }
    if payload_class == 'graph':
        return {
            'mode': 'interpret',
            'x_axis': {'label_lv': 'Koncentrācija', 'unit': 'mol/L'},
            'y_axis': {'label_lv': 'Absorbance', 'unit': ''},
            'points': [{'x': 0.1, 'y': 0.2}, {'x': 0.2, 'y': 0.4}],
            'target_readout': {
                'quantity': 'absorbance',
                'expected_value': 0.3,
                'unit': '',
                'tolerance_class': 'absorbance',
            },
        }
    return {
        'steps': [{'step_id': 'step-1', 'prompt_lv': 'Apraksti metodi', 'expected': '2:1:2'}],
        'explanation_prompt_lv': 'Pamato atbildi.',
        'expected_summary_lv': 'Sabalansēta reakcija un skaidrojums.',
    }


def make_question(
    qid: str,
    type_id: str,
    family_id: str = 'FAM-1A',
    variant_id: str = 'A',
    topic: int = 1,
    outcome_id: str = 'P1-01',
) -> dict[str, Any]:
    pc = TYPE_TO_CLASS[type_id]
    eng = TYPE_TO_ENGINE[type_id]
    return {
        'question_id': qid,
        'schema_version': 1,
        'bank_version': '0.1.0-scratch',
        'family_id': family_id,
        'variant_id': variant_id,
        'seed': f'{family_id}-{variant_id}',
        'topic': topic,
        'outcome_ids': [outcome_id],
        'type_id': type_id,
        'type_ids': [type_id],
        'difficulty': 'application',
        'time_minutes': 5.0,
        'stem_lv': f'Parauga uzdevums {qid} ({type_id}).',
        'feedback_lv': {
            'correct': 'Pareizi.',
            'incorrect': 'Pārbaudi nosacījumus un vienības.',
        },
        'misconception_signatures': [f'MC-{topic}A-01'],
        'source_refs': [
            {
                'path': 'RSU_MedChem_Colloq1_Prog_LV_2025.pdf',
                'sha256': SAMPLE_SHA,
                'locator': 'Topic 1',
                'claim_status': 'proposal-explicit-givens',
            }
        ],
        'givens': {'medium': 'ūdens šķīdums'},
        'payload_class': pc,
        'payload': make_payload(pc),
        'rubric': [
            {
                'criterion_id': 'C1',
                'points': 2.0,
                'grading': 'auto' if eng != 'self-assessed' else 'self',
                'engine_binding': eng,
                'depends_on': [],
                'carry_forward': False,
            }
        ],
        'review': {
            'content': 'pending',
            'source': 'pending',
            'calculation': 'pending',
            'accessibility': 'pending',
        },
    }


def write_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return path


def build_permanent_negative_corpus() -> dict[str, Path]:
    if FIXTURES_DIR.exists():
        shutil.rmtree(FIXTURES_DIR)
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Malformed schema fixture
    schema_bad = FIXTURES_DIR / 'schema_malformed.json'
    schema_bad.write_text('{"types": {"Q01": {}', encoding='utf-8')

    base = make_question('COL1-1-1A-A-01', 'Q01')

    # 2. Missing stem
    f_stem = copy.deepcopy(base)
    del f_stem['stem_lv']
    p_stem = write_json(FIXTURES_DIR / 'neg_missing_stem.json', f_stem)

    # 3. Unknown tolerance_class
    f_tol = copy.deepcopy(base)
    f_tol['payload']['tolerance_class'] = 'nonexistent_tol'
    p_tol = write_json(FIXTURES_DIR / 'neg_bad_tolerance.json', f_tol)

    # 4. Unknown outcome_id
    f_out = copy.deepcopy(base)
    f_out['outcome_ids'] = ['P9-99']
    p_out = write_json(FIXTURES_DIR / 'neg_bad_outcome.json', f_out)

    # 5. Bad family_id format
    f_fam = copy.deepcopy(base)
    f_fam['family_id'] = 'BAD-FAM'
    p_fam = write_json(FIXTURES_DIR / 'neg_bad_family.json', f_fam)

    # 6. Discriminator mismatch
    f_disc = copy.deepcopy(base)
    f_disc['payload_class'] = 'option_select'
    p_disc = write_json(FIXTURES_DIR / 'neg_discriminator_mismatch.json', f_disc)

    # 7. Bad misconception stub
    f_mc = copy.deepcopy(base)
    f_mc['misconception_signatures'] = ['BAD-MC']
    p_mc = write_json(FIXTURES_DIR / 'neg_bad_misconception.json', f_mc)

    # 8. Set-level duplicate question_id across two files
    dup_dir = FIXTURES_DIR / 'neg_duplicate_id'
    write_json(dup_dir / 'part1.json', copy.deepcopy(base))
    q2 = copy.deepcopy(base)
    q2['variant_id'] = 'B'
    write_json(dup_dir / 'part2.json', q2)

    return {
        'schema_malformed': schema_bad,
        'missing_stem': p_stem,
        'bad_tolerance': p_tol,
        'bad_outcome': p_out,
        'bad_family': p_fam,
        'discriminator_mismatch': p_disc,
        'bad_misconception': p_mc,
        'duplicate_id': dup_dir,
    }


def run_cmd(args: list[str]) -> dict[str, Any]:
    res = subprocess.run(args, cwd=DEST, capture_output=True, text=True)
    return {
        'command': ' '.join(args),
        'returncode': res.returncode,
        'stdout': res.stdout.strip(),
        'stderr': res.stderr.strip(),
    }


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)

    schema_path = DEST / SCHEMA_PATH
    families_doc = load_json(DEST / 'docs/QUESTION_FAMILIES.json')
    families = families_doc['families']

    # 1. Schema self-check
    schema_report = validate_bank(schema_path=schema_path, repo_root=DEST)

    # 2. Permanent negative corpus
    neg_paths = build_permanent_negative_corpus()
    neg_results: dict[str, Any] = {}
    failures: list[str] = []

    # Schema-error fixture
    bad_schema_rep = validate_bank(schema_path=neg_paths['schema_malformed'], repo_root=DEST)
    neg_results['schema_malformed'] = {
        'status': bad_schema_rep['status'],
        'violations': bad_schema_rep['violations'],
    }
    if bad_schema_rep['status'] != 'FAIL':
        failures.append('schema_malformed did not fail')

    expected_fields = {
        'missing_stem': 'stem_lv',
        'bad_tolerance': 'payload.tolerance_class',
        'bad_outcome': 'outcome_ids',
        'bad_family': 'family_id',
        'discriminator_mismatch': 'payload_class',
        'bad_misconception': 'misconception_signatures',
        'duplicate_id': 'question_id',
    }
    for key, exp_field in expected_fields.items():
        rep = validate_bank(schema_path=schema_path, repo_root=DEST, bank_path=neg_paths[key])
        fields = [v['field'] for v in rep['violations']]
        neg_results[key] = {
            'status': rep['status'],
            'fields': fields,
            'violations': rep['violations'],
        }
        if rep['status'] != 'FAIL' or exp_field not in fields:
            failures.append(f'{key} did not fail naming {exp_field}: got {fields}')

    # 3. Valid 18-type scratch bank (1 per type)
    valid18_dir = WORK / 'valid_18'
    for idx in range(1, 19):
        tid = f'Q{idx:02d}'
        q = make_question(f'COL1-1-1A-A-{idx:02d}', tid)
        write_json(valid18_dir / f'{tid}.json', q)
    valid18_rep = validate_bank(schema_path=schema_path, repo_root=DEST, bank_path=valid18_dir, require_all_required_types=True)
    if valid18_rep['status'] != 'PASS' or valid18_rep['counts']['instances'] != 18:
        failures.append('valid_18 failed')

    # 4. Full-size 112-instance scratch bank (28 families x 4 variants, cycling Q01..Q18)
    full_dir = WORK / 'full_112'
    full_questions: list[dict[str, Any]] = []
    type_cycle = [f'Q{i:02d}' for i in range(1, 19)]
    counter = 0
    for fam in families:
        fid = fam['family_id']
        topic = fam['topic']
        outcome = f'P{topic}-01'
        for var in ('A', 'B', 'C', 'D'):
            tid = type_cycle[counter % len(type_cycle)]
            counter += 1
            qid = f'COL1-{topic}-{fid[4:]}-{var}-{counter:03d}'
            q = make_question(qid, tid, family_id=fid, variant_id=var, topic=topic, outcome_id=outcome)
            full_questions.append(q)
            write_json(full_dir / f'{qid}.json', q)

    full_rep = validate_bank(schema_path=schema_path, repo_root=DEST, bank_path=full_dir, require_all_required_types=True)
    if full_rep['status'] != 'PASS' or full_rep['counts']['instances'] != 112:
        failures.append(f'full_112 failed: {full_rep["status"]} count={full_rep["counts"]["instances"]}')

    full_bundle_path = WORK / 'full_112_bundle.json'
    write_json(full_bundle_path, {'questions': full_questions})

    # 5. Build gate refusal (invalid scratch bank) and pass (clean 112 scratch bank)
    gate_fail_out = WORK / 'gate_fail.html'
    gate_fail_man = WORK / 'gate_fail_manifest.json'
    gate_fail_cmd = run_cmd([
        'python3', 'tools/build.py',
        '--bank', str(neg_paths['missing_stem']),
        '--out', str(gate_fail_out),
        '--manifest-out', str(gate_fail_man),
    ])
    if gate_fail_cmd['returncode'] == 0 or gate_fail_out.exists() or 'stem_lv' not in gate_fail_cmd['stderr']:
        failures.append('build gate did not refuse invalid scratch bank with stem_lv named')

    gate_pass_out = WORK / 'gate_pass.html'
    gate_pass_man = WORK / 'gate_pass_manifest.json'
    gate_pass_cmd = run_cmd([
        'python3', 'tools/build.py',
        '--bank', str(full_dir),
        '--out', str(gate_pass_out),
        '--manifest-out', str(gate_pass_man),
    ])
    if gate_pass_cmd['returncode'] != 0 or not gate_pass_out.exists():
        failures.append('build gate failed on clean 112 scratch bank')

    # 6. Runtime harness
    runtime_cmd = run_cmd(['node', 'tools/check_bank_runtime.js', '--full-bank', str(full_bundle_path), '--json'])
    if runtime_cmd['returncode'] != 0:
        failures.append(f'runtime harness failed: {runtime_cmd["stderr"]}')
    runtime_json = json.loads(runtime_cmd['stdout']) if runtime_cmd['stdout'] else {}

    record = {
        'schema_version': 1,
        'task': 'N04',
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'schema_self_check': {
            'status': schema_report['status'],
            'schema_check': schema_report['schema_check'],
            'schema_sha256': sha256_file(schema_path),
        },
        'negative_corpus': neg_results,
        'valid_18_scratch': {
            'status': valid18_rep['status'],
            'counts': valid18_rep['counts'],
        },
        'full_112_scratch': {
            'status': full_rep['status'],
            'counts': full_rep['counts'],
            'fast_gate_under_1000ms': full_rep['duration_ms'] < 1000.0,
        },
        'build_gate_refusal': {
            'returncode': gate_fail_cmd['returncode'],
            'artifact_written': gate_fail_out.exists(),
            'stderr': gate_fail_cmd['stderr'],
        },
        'build_gate_pass': {
            'returncode': gate_pass_cmd['returncode'],
            'artifact_written': gate_pass_out.exists(),
        },
        'runtime_harness': runtime_json,
        'artifacts': {
            'data/question_schema.json': sha256_file(DEST / 'data/question_schema.json'),
            'tools/validate_bank.py': sha256_file(DEST / 'tools/validate_bank.py'),
            'src/bank-loader.js': sha256_file(DEST / 'src/bank-loader.js'),
            'tools/build.py': sha256_file(DEST / 'tools/build.py'),
            'src/shell.html': sha256_file(DEST / 'src/shell.html'),
        },
    }

    RECORD_PATH.parent.mkdir(parents=True, exist_ok=True)
    RECORD_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'{record["status"]} N04 corpus: 112-bank={full_rep["status"]} ({full_rep["duration_ms"]} ms), runtime={runtime_json.get("status")}')
    if failures:
        for f in failures:
            print(f'  FAIL: {f}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
