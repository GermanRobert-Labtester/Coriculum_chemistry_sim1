#!/usr/bin/env python3
"""N24 build gate: form assembly, independent constraint checker, and parity.

This gate is the build's N24 checkpoint (order 20, owner N24). It implements an
INDEPENDENT constraint checker (sharing zero code with tools/assemble_forms.py)
and refuses the build when:

- src/compiled/assembly.js or src/compiled/exam.js has drifted from TypeScript;
- src/shell.html is missing the form-picker touchpoints or __SIM_FORMS_JSON__ /
  __ASSEMBLY_JS__ placeholders;
- any assembled form (A, B, C) fails the independent constraint checker:
  21 slots, exact slot order, per-topic slot counts (3 each), per-topic point
  subtotals (10/12/20/15/16/15/12 = 100), family uniqueness (21 distinct
  families), instance uniqueness, required completed-type coverage
  (Q02, Q04, Q10, Q11, Q12, Q13, Q15), review-passed eligibility, and Q11
  figure_id binding (N23-C03);
- the assembled forms' bank_digest is missing or stale relative to the verified
  bank;
- Python assembly (tools/assemble_forms.py) and TypeScript/JS assembly
  (src/compiled/assembly.js) diverge on any form digest.

Usage:
    python3 tools/validate_n24_assembly.py --report evidence/N24_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
SHELL_PATH = 'src/shell.html'
ASSEMBLY_TS_PATH = 'src/assembly.ts'
ASSEMBLY_JS_PATH = 'src/compiled/assembly.js'
PRNG_JS_PATH = 'src/prng.js'
EXAM_POLICY_PATH = 'data/exam_policy.json'
BLUEPRINT_PATH = 'docs/SIMULATION_BLUEPRINT.json'
SEED_POLICY_PATH = 'data/seed_policy.json'
PRNG_CONTRACT_PATH = 'data/prng_contract_vectors.json'
BANK_DIR = 'data/bank'
FORMS_DIR = 'output/forms'

REQUIRED_SHELL_IDS = [
    'sakums-forma-izvele',
    'sakums-form-picker',
    'sakums-pick-A',
    'sakums-pick-B',
    'sakums-pick-C',
    'sakums-pick-SEEDED',
    'sakums-seed-input',
    'sakums-form-reason',
    'exam-form-picker',
    'exam-pick-A',
    'exam-pick-B',
    'exam-pick-C',
    'exam-pick-SEEDED',
    'exam-seed-input',
    'exam-form-shortage',
    'sim-forms',
]


def verify_form_manifest_independent(
    manifest: dict[str, Any],
    bank_questions: list[dict[str, Any]],
    exam_policy: dict[str, Any],
    blueprint: dict[str, Any],
    *,
    allow_ephemeral: bool = False,
    strict_rubric_points: bool = False,
) -> dict[str, Any]:
    """Independent Python constraint checker (shares ZERO logic with assemble_forms.py)."""
    errors: list[str] = []
    checks = {
        'slot_count': True,
        'slot_order': True,
        'eligibility': True,
        'topic_and_slot_constraints': True,
        'per_topic_points_and_counts': True,
        'total_points': True,
        'family_uniqueness': True,
        'instance_uniqueness': True,
        'required_types_coverage': True,
        'q11_figure_binding': True,
    }

    if not isinstance(manifest, dict) or not isinstance(manifest.get('slots'), list):
        checks['slot_count'] = False
        return {'status': 'FAIL', 'checks': checks, 'errors': ['Manifest missing slots array']}

    policy_slots = exam_policy['slots']
    bp_allowed = {s['slot_id']: list(s.get('allowed_family_ids') or []) for s in blueprint['slots']}
    req_types = list(exam_policy['exam']['required_types_per_form'])
    expected_total = int(exam_policy['exam']['total_points'])

    expected_topic_points: dict[int, int] = {}
    expected_topic_counts: dict[int, int] = {}
    plan_by_id: dict[str, dict[str, Any]] = {}
    for ps in policy_slots:
        t = int(ps['topic'])
        expected_topic_points[t] = expected_topic_points.get(t, 0) + int(ps['points'])
        expected_topic_counts[t] = expected_topic_counts.get(t, 0) + 1
        plan_by_id[ps['slot_id']] = ps

    bank_by_id = {q['question_id']: q for q in bank_questions if isinstance(q, dict) and q.get('question_id')}

    drawn_slots = manifest['slots']
    if len(drawn_slots) != len(policy_slots):
        checks['slot_count'] = False
        errors.append(f'Expected {len(policy_slots)} slots, got {len(drawn_slots)}')

    for idx, ps in enumerate(policy_slots):
        if idx >= len(drawn_slots) or drawn_slots[idx].get('slot_id') != ps['slot_id']:
            checks['slot_order'] = False
    if not checks['slot_order']:
        errors.append('Slot order or slot_id mismatch against exam_policy')

    seen_families: dict[str, str] = {}
    seen_instances: dict[str, str] = {}
    seen_types: set[str] = set()
    got_topic_counts: dict[int, int] = {}
    got_topic_points: dict[int, int] = {}
    total_pts = 0

    for slot in drawn_slots:
        sid = slot.get('slot_id', '')
        iid = slot.get('instance_id', '')
        plan = plan_by_id.get(sid)
        inst = bank_by_id.get(iid)
        if inst is None:
            checks['eligibility'] = False
            errors.append(f'Instance {iid!r} at slot {sid!r} not found in verified bank')
            continue

        rev = inst.get('review') or {}
        rev_ok = (
            rev.get('accessibility') == 'passed'
            and rev.get('calculation') == 'passed'
            and rev.get('content') == 'passed'
            and rev.get('source') == 'passed'
        )
        wf = ((inst.get('extensions') or {}).get('data') or {}).get('review_workflow')
        wf_ok = True if wf is None else (wf.get('state') == 'accepted')
        eph_meta = ((inst.get('extensions') or {}).get('data') or {}).get('ephemeral')
        is_eph = bool(
            slot.get('ephemeral')
            or re.search(r'-EPH-[0-9]+$', iid)
            or (isinstance(eph_meta, dict) and eph_meta.get('frozen_bank_member') is False)
        )
        if not rev_ok or not wf_ok:
            checks['eligibility'] = False
            errors.append(f'Instance {iid!r} at slot {sid!r} is not review-accepted')
        if is_eph and not allow_ephemeral:
            checks['eligibility'] = False
            errors.append(f'Ephemeral instance {iid!r} forbidden in frozen form at {sid!r}')

        if plan is None or int(inst['topic']) != int(plan['topic']) or int(slot.get('topic', -1)) != int(plan['topic']) or int(slot.get('points', -1)) != int(plan['points']):
            checks['topic_and_slot_constraints'] = False
            errors.append(f'Slot {sid!r} topic/points mismatch against plan')
        allowed = bp_allowed.get(sid)
        if allowed and inst.get('family_id') not in allowed:
            checks['topic_and_slot_constraints'] = False
            errors.append(f'Family {inst.get("family_id")!r} not allowed at slot {sid!r}')
        if strict_rubric_points and plan is not None:
            rsum = sum(float(c.get('points', 0)) for c in (inst.get('rubric') or []))
            if round(rsum, 6) != float(plan['points']):
                checks['topic_and_slot_constraints'] = False
                errors.append(f'Rubric sum {rsum} != slot points {plan["points"]} at {sid!r}')

        fam = str(inst.get('family_id', ''))
        if fam in seen_families:
            checks['family_uniqueness'] = False
            errors.append(f'Duplicate family {fam!r} in slots {seen_families[fam]} and {sid}')
        seen_families[fam] = sid

        if iid in seen_instances:
            checks['instance_uniqueness'] = False
            errors.append(f'Duplicate instance {iid!r} in slots {seen_instances[iid]} and {sid}')
        seen_instances[iid] = sid

        if inst.get('type_id') == 'Q11' and not str(slot.get('figure_id') or '').strip():
            checks['q11_figure_binding'] = False
            errors.append(f'Q11 slot {sid!r} missing figure_id binding (N23-C03)')

        t = int(slot.get('topic', 0))
        got_topic_counts[t] = got_topic_counts.get(t, 0) + 1
        got_topic_points[t] = got_topic_points.get(t, 0) + int(slot.get('points', 0))
        total_pts += int(slot.get('points', 0))
        if inst.get('type_id'):
            seen_types.add(str(inst['type_id']))
        for tid in (inst.get('type_ids') or []):
            seen_types.add(str(tid))

    for t, want_c in sorted(expected_topic_counts.items()):
        if got_topic_counts.get(t, 0) != want_c:
            checks['per_topic_points_and_counts'] = False
            errors.append(f'Topic {t} slot count {got_topic_counts.get(t, 0)} != {want_c}')
        if got_topic_points.get(t, 0) != expected_topic_points[t]:
            checks['per_topic_points_and_counts'] = False
            errors.append(f'Topic {t} points {got_topic_points.get(t, 0)} != {expected_topic_points[t]}')

    if total_pts != expected_total:
        checks['total_points'] = False
        errors.append(f'Total points {total_pts} != {expected_total}')

    missing_types = [rt for rt in req_types if rt not in seen_types]
    if missing_types:
        checks['required_types_coverage'] = False
        errors.append(f'Missing required completed types: {missing_types}')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'checks': checks,
        'errors': errors,
    }


def _check_shell_markup(repo_root: Path, errors: list[str]) -> dict[str, Any]:
    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    ids = set(re.findall(r'\sid="([^"]+)"', shell))
    missing_ids = [rid for rid in REQUIRED_SHELL_IDS if rid not in ids]
    for mid in missing_ids:
        errors.append(f'src/shell.html missing N24 touchpoint #{mid}')
    for placeholder in ('__SIM_FORMS_JSON__', '__ASSEMBLY_JS__', '__FORMS_DIGEST__'):
        if placeholder not in shell:
            errors.append(f'src/shell.html missing placeholder {placeholder}')
    return {
        'status': 'PASS' if not missing_ids else 'FAIL',
        'required_ids_present': len(REQUIRED_SHELL_IDS) - len(missing_ids),
        'required_ids_total': len(REQUIRED_SHELL_IDS),
        'missing_ids': missing_ids,
    }


def _check_js_parity(
    repo_root: Path,
    py_forms: list[dict[str, Any]],
    bank_questions: list[dict[str, Any]],
    bank_digest: str,
    prng_contract_digest: str,
    errors: list[str],
) -> dict[str, Any]:
    script = """
const fs = require('fs'), crypto = require('crypto');
require('./src/prng.js');
require('./src/compiled/assembly.js');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const sha = (t) => crypto.createHash('sha256').update(t, 'utf8').digest('hex');
const res = globalThis.SimAssembly.assembleFormSet({
  bank: input.bank,
  bank_digest: input.bank_digest,
  prng_contract_digest: input.prng_contract_digest,
  sha256: sha
});
process.stdout.write(JSON.stringify(res.forms));
"""
    payload = json.dumps({
        'bank': bank_questions,
        'bank_digest': bank_digest,
        'prng_contract_digest': prng_contract_digest,
    })
    proc = subprocess.run(
        ['node', '-e', script],
        cwd=str(repo_root),
        input=payload,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        errors.append(f'JS assembly parity run failed: {proc.stderr.strip()}')
        return {'status': 'FAIL', 'stderr': proc.stderr.strip()}
    js_forms = json.loads(proc.stdout)
    matches = {}
    for py_f, js_f in zip(py_forms, js_forms):
        fid = py_f.get('form_id', '?')
        same = canonical_json_bytes(py_f) == canonical_json_bytes(js_f)
        matches[fid] = {
            'byte_identical': same,
            'py_digest': py_f.get('manifest_digest'),
            'js_digest': js_f.get('manifest_digest'),
        }
        if not same:
            errors.append(f'Python vs JS assembly divergence on form {fid}')
    return {'status': 'PASS' if all(v['byte_identical'] for v in matches.values()) else 'FAIL', 'forms': matches}


def validate_assembled_island(
    *,
    forms_island: dict[str, Any],
    bank_questions: list[dict[str, Any]],
    bank_digest: str,
    repo_root: Path = ROOT,
) -> dict[str, Any]:
    """Validate an in-memory #sim-forms island during build before writing artifacts."""
    errors: list[str] = []
    exam_policy = load_json(repo_root / EXAM_POLICY_PATH)
    blueprint = load_json(repo_root / BLUEPRINT_PATH)
    prng_contract = load_json(repo_root / PRNG_CONTRACT_PATH)
    prng_contract_digest = sha256_bytes(canonical_json_bytes(prng_contract))

    drift_proc = subprocess.run(
        [sys.executable, str(repo_root / 'tools/compile_n21_ts.py'), '--check'],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    if drift_proc.returncode != 0:
        errors.append(f'TypeScript compile drift detected: {drift_proc.stdout} {drift_proc.stderr}')

    shell_check = _check_shell_markup(repo_root, errors)

    if forms_island.get('island_id') != 'sim-forms':
        errors.append('forms island_id must be "sim-forms"')
    if forms_island.get('bank_digest') != bank_digest:
        errors.append(
            f'forms_island bank_digest {forms_island.get("bank_digest")} != live bank_digest {bank_digest} (stale assembly)'
        )

    forms = forms_island.get('forms') or []
    if len(forms) != 3:
        errors.append(f'Expected 3 forms (A, B, C), got {len(forms)}')

    form_reports = {}
    for fm in forms:
        fid = fm.get('form_id', '?')
        if fm.get('status') != 'AVAILABLE':
            errors.append(f'Form {fid} is in shortage state: {fm.get("disabled_reason_lv")}')
            form_reports[fid] = {'status': 'FAIL', 'shortage': fm}
            continue
        rep = verify_form_manifest_independent(fm, bank_questions, exam_policy, blueprint)
        form_reports[fid] = {
            'status': rep['status'],
            'checks': rep['checks'],
            'errors': rep['errors'],
            'manifest_digest': fm.get('manifest_digest'),
            'form_seed': fm.get('form_seed'),
            'total_slots': fm.get('total_slots'),
            'total_points': fm.get('total_points'),
        }
        for err in rep['errors']:
            errors.append(f'Form {fid}: {err}')

    parity = _check_js_parity(repo_root, forms, bank_questions, bank_digest, prng_contract_digest, errors)

    # Pipeline-order refusal proof: unverified or stale bank must raise E_ASSEMBLY_BANK_UNVERIFIED
    from assemble_forms import AssemblyPipelineError, assemble_frozen_forms  # noqa: E402
    pipeline_guard = {'absent_digest_refused': False, 'stale_digest_refused': False, 'unverified_flag_refused': False}
    bank_island_mock = {'island_id': 'sim-bank', 'questions': bank_questions}
    for key, kwargs in (
        ('absent_digest_refused', {'bank_digest': '', 'bank_verified': True}),
        ('stale_digest_refused', {'bank_digest': '0' * 64, 'bank_verified': True}),
        ('unverified_flag_refused', {'bank_digest': bank_digest, 'bank_verified': False}),
    ):
        try:
            assemble_frozen_forms(
                bank_island=bank_island_mock,
                bank_embedded_digest=bank_digest,
                repo_root=repo_root,
                **kwargs,
            )
            errors.append(f'Pipeline-order guard failed to refuse {key}')
        except AssemblyPipelineError as exc:
            pipeline_guard[key] = exc.code == 'E_ASSEMBLY_BANK_UNVERIFIED'
            if not pipeline_guard[key]:
                errors.append(f'Unexpected error code for {key}: {exc.code}')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'owner': 'N24',
        'bank_digest': bank_digest,
        'forms_island_digest': sha256_bytes(canonical_json_bytes(forms_island)),
        'forms_island_bytes': len(canonical_json_bytes(forms_island)),
        'compile_drift': 'PASS' if drift_proc.returncode == 0 else 'FAIL',
        'shell_markup': shell_check,
        'forms': form_reports,
        'js_parity': parity,
        'pipeline_guard': pipeline_guard,
        'errors': errors,
    }


def run_gate(repo_root: Path = ROOT) -> dict[str, Any]:
    """Run Gate 20 over the committed output/forms/*.json + live bank."""
    from assemble_forms import assemble_frozen_forms  # noqa: E402
    # Reconstruct bank projection identically to build.py
    questions: list[dict[str, Any]] = []
    for path in sorted((repo_root / BANK_DIR).glob('*.json')):
        doc = load_json(path)
        for q in doc.get('questions', []):
            proj = json.loads(json.dumps(q))
            data = (proj.get('extensions') or {}).get('data')
            if isinstance(data, dict):
                for dropped in ('draws', 'derived', 'review_workflow'):
                    data.pop(dropped, None)
            questions.append(proj)
    bank_island = {
        'island_id': 'sim-bank',
        'schema_version': 1,
        'bank_version': '1.0.0-n20',
        'status': 'frozen-reviewed-bank',
        'questions': questions,
    }
    bank_digest = sha256_bytes(canonical_json_bytes(bank_island))

    forms_dir = repo_root / FORMS_DIR
    if all((forms_dir / f'form_{fid}.json').exists() for fid in ('A', 'B', 'C')):
        disk_forms = [load_json(forms_dir / f'form_{fid}.json') for fid in ('A', 'B', 'C')]
        fresh = assemble_frozen_forms(
            bank_island=bank_island,
            bank_digest=bank_digest,
            bank_embedded_digest=bank_digest,
            bank_verified=True,
            repo_root=repo_root,
        )
        fresh['forms'] = disk_forms
        report = validate_assembled_island(
            forms_island=fresh,
            bank_questions=questions,
            bank_digest=bank_digest,
            repo_root=repo_root,
        )
        # Also verify disk forms match freshly assembled forms
        fresh_rebuilt = assemble_frozen_forms(
            bank_island=bank_island,
            bank_digest=bank_digest,
            bank_embedded_digest=bank_digest,
            bank_verified=True,
            repo_root=repo_root,
        )
        for disk_f, new_f in zip(disk_forms, fresh_rebuilt['forms']):
            if canonical_json_bytes(disk_f) != canonical_json_bytes(new_f):
                report['errors'].append(
                    f'Disk manifest output/forms/form_{disk_f.get("form_id")}.json is stale vs verified bank'
                )
                report['status'] = 'FAIL'
        return report

    fresh = assemble_frozen_forms(
        bank_island=bank_island,
        bank_digest=bank_digest,
        bank_embedded_digest=bank_digest,
        bank_verified=True,
        repo_root=repo_root,
    )
    return validate_assembled_island(
        forms_island=fresh,
        bank_questions=questions,
        bank_digest=bank_digest,
        repo_root=repo_root,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='write JSON validation report to this path')
    args = parser.parse_args()
    report = run_gate(ROOT)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if report['status'] == 'PASS':
        digs = {k: v['manifest_digest'][:12] for k, v in report['forms'].items()}
        print(f"PASS n24 form_assembly gate: 3 forms (21 slots, 100 pts each), digests={digs}, parity=PASS")
        return 0
    for err in report.get('errors', []):
        print(f'  - {err}', file=sys.stderr)
    print('FAIL n24 form_assembly gate', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
