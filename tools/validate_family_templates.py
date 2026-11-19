#!/usr/bin/env python3
"""N20 family-template gate: validation table, determinism proof, range refusal.

The gate is the build-time authority for the 28 family templates:

* **validation** — every family's parameters, conventions references, response
  types, payload classes, tolerance classes and rubric weights are checked
  against the N04 schema and the ``#sim-conventions`` island;
* **determinism** — every family/variant pair is instantiated twice from the
  same seed and the two canonical byte streams are compared, and the digest of
  the second instantiation is compared with the frozen bank instance, so the
  claim "the bank is reproducible from the templates and the seed alone" is
  checked against the shipped bytes rather than asserted;
* **range refusal** — a scratch template whose parameter is outside the
  declared range fails validation *by family and parameter name*, which is
  what the range gate is supposed to catch.

Nothing here writes to the templates or the bank. The evidence records are
written under ``evidence/`` so that the frozen artefacts stay byte-stable.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import variant_engine as ve  # noqa: E402

TEMPLATE_DIR = 'data/family_templates'
BANK_DIR = 'data/bank'
EVIDENCE_DIR = 'evidence'
REQUIRED_TYPES = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15']


def _canonical_digest(value: Any) -> str:
    return ve.sha256_bytes(ve.canonical_bytes(value))


def _bank_instances(repo_root: Path, bank_dir: Path) -> dict[str, dict[str, Any]]:
    instances: dict[str, dict[str, Any]] = {}
    for path in sorted((repo_root / bank_dir).rglob('*.json')):
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding='utf-8'))
        for question in raw.get('questions', []):
            instances[question['question_id']] = question
    return instances


def run_validation(repo_root: Path) -> dict[str, Any]:
    """The per-family validation table."""
    templates = ve.load_templates(repo_root / TEMPLATE_DIR)
    report = ve.validate_templates(templates, repo_root)
    report['template_digest'] = ve.template_digest(templates)
    report['template_files'] = sorted(
        str(p.relative_to(repo_root)) for p in (repo_root / TEMPLATE_DIR).rglob('*.json'))
    report['required_types_expected'] = list(REQUIRED_TYPES)
    report['policy_label'] = ('PROPOSED training policy (N20): 28 families x 4 variants = 112 '
                              'instances, point weights and minute budgets are proposals, '
                              'not official examination facts.')
    return report


def run_determinism(repo_root: Path) -> dict[str, Any]:
    """Instantiate every family/variant twice and compare the canonical bytes.

    The frozen bank instance is the instantiation *plus* the review workflow
    state, so the comparison applies the same promotion to the fresh
    instantiation before it is compared with the shipped bytes. Otherwise the
    check would compare two different things and could only ever fail.
    """
    import validate_bank_review as review

    templates = ve.load_templates(repo_root / TEMPLATE_DIR)
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    frozen = _bank_instances(repo_root, Path(BANK_DIR))
    rows: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    for family in templates:
        for variant in family.get('variants') or []:
            first = ve.instantiate(family, variant, conventions=conventions)
            second = ve.instantiate(family, variant, conventions=conventions)
            digest_first = _canonical_digest(first)
            digest_second = _canonical_digest(second)
            promoted = review.accepted_state(first)
            promoted_digest = _canonical_digest(promoted)
            frozen_instance = frozen.get(first['question_id'])
            frozen_digest = _canonical_digest(frozen_instance) if frozen_instance else None
            row = {
                'family_id': family['family_id'],
                'variant_id': variant['variant_id'],
                'question_id': first['question_id'],
                'seed_key': variant.get('seed_key'),
                'seed': first['seed'],
                'digest_first': digest_first,
                'digest_second': digest_second,
                'byte_identical': digest_first == digest_second,
                'promoted_digest': promoted_digest,
                'frozen_digest': frozen_digest,
                'matches_frozen_bank': frozen_digest == promoted_digest,
            }
            rows.append(row)
            if not row['byte_identical'] or not row['matches_frozen_bank']:
                mismatches.append(row)
    return {
        'status': 'PASS' if not mismatches else 'FAIL',
        'instances': len(rows),
        'byte_identical_pairs': sum(1 for row in rows if row['byte_identical']),
        'matching_frozen_bank': sum(1 for row in rows if row['matches_frozen_bank']),
        'mismatches': mismatches,
        'rows': rows,
    }


def run_range_refusal(repo_root: Path) -> dict[str, Any]:
    """A scratch template with an out-of-range parameter must fail by name.

    The scratch template is a copy of the first family with one drawn
    parameter's maximum moved below its minimum, so the failure is produced by
    the *range* rule and names the family and the parameter.
    """
    templates = ve.load_templates(repo_root / TEMPLATE_DIR)
    scratch = copy.deepcopy(templates)
    family = scratch[0]
    target = None
    for variant in family.get('variants') or []:
        for param in variant.get('parameters') or []:
            if param.get('kind') == 'int':
                target = param
                break
        if target is not None:
            break
    if target is None:
        return {'status': 'FAIL', 'message': 'nav atrasta zīmējamais parametrs scratch ģimenē.'}
    original = {'param_id': target['param_id'], 'min': target['min'], 'max': target['max'],
                'step': target['step'], 'decimals': target['decimals']}
    target['min'] = target['max'] + target['step']
    report = ve.validate_templates(scratch, repo_root)
    named = [v for v in report['violations']
             if v.get('family_id') == family['family_id']
             and target['param_id'] in str(v.get('field', '')) + str(v.get('message', ''))]
    return {
        'status': 'PASS' if report['status'] == 'FAIL' and named else 'FAIL',
        'scratch_family_id': family['family_id'],
        'scratch_parameter': target['param_id'],
        'original_range': original,
        'scratch_range': {'min': target['min'], 'max': target['max'], 'step': target['step'],
                          'decimals': target['decimals']},
        'gate_status': report['status'],
        'named_violations': named,
        'all_violations': report['violations'][:6],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--report', default=None)
    parser.add_argument('--no-evidence', action='store_true',
                        help='Do not write the evidence records.')
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()

    validation = run_validation(repo_root)
    determinism = run_determinism(repo_root)
    refusal = run_range_refusal(repo_root)
    status = 'PASS' if (validation['status'] == 'PASS' and determinism['status'] == 'PASS'
                        and refusal['status'] == 'PASS') else 'FAIL'
    report = {
        'schema_version': 1,
        'owner': 'N20',
        'status': status,
        'validation': validation,
        'determinism': determinism,
        'range_refusal': refusal,
    }

    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
    if not args.no_evidence:
        evidence = repo_root / EVIDENCE_DIR
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'N20_TEMPLATE_VALIDATION.json').write_text(
            json.dumps({'schema_version': 1, 'owner': 'N20', 'status': validation['status'],
                        'families': validation['families'],
                        'rows': validation['rows'],
                        'required_types_covered': validation['required_types_covered'],
                        'required_types_missing': validation['required_types_missing'],
                        'violations': validation['violations'],
                        'template_digest': validation['template_digest'],
                        'policy_label': validation['policy_label']},
                       ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        (evidence / 'N20_DETERMINISM_RECORD.json').write_text(
            json.dumps({'schema_version': 1, 'owner': 'N20',
                        'claim': 'Identical seeds produce byte-identical instances, and the '
                                 'frozen bank is reproducible from the templates and the seed alone.',
                        'authority': 'tools/variant_engine.py (Python authoring twin)',
                        'status': determinism['status'],
                        'instances': determinism['instances'],
                        'byte_identical_pairs': determinism['byte_identical_pairs'],
                        'matching_frozen_bank': determinism['matching_frozen_bank'],
                        'mismatches': determinism['mismatches'],
                        'rows': determinism['rows']},
                       ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    print(f"{status} n20_family_templates: {validation['families']} families, "
          f"{determinism['instances']} variants, "
          f"determinism {determinism['byte_identical_pairs']}/{determinism['instances']} identical, "
          f"frozen-bank match {determinism['matching_frozen_bank']}/{determinism['instances']}, "
          f"range refusal {refusal['status']}")
    if status != 'PASS':
        print(json.dumps({'validation': validation.get('violations', [])[:6],
                          'determinism': determinism.get('mismatches', [])[:3],
                          'range_refusal': refusal}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
