#!/usr/bin/env python3
"""N20 corpus: the variant engine, the frozen bank and their evidence.

Runs the template gate, the bank schema gate, the review gate, the runtime
harness and the scratch-refusal proof, measures the byte budgets against the
built artifact and writes ``evidence/N20_CORPUS_RECORD.json``.

The record is timestamp-free and deterministic: two consecutive runs must
produce the same bytes. That is the parity proof for the extended corpus.
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
HARNESS = ROOT / 'tools/check_n20_runtime.js'
TEMPLATE_GATE = ROOT / 'tools/validate_family_templates.py'
REVIEW_GATE = ROOT / 'tools/validate_bank_review.py'
BANK_VALIDATOR = ROOT / 'tools/validate_bank.py'
OUT_DEFAULT = ROOT / 'evidence/N20_CORPUS_RECORD.json'
VERIFICATION_OUT = ROOT / 'evidence/N20_VERIFICATION_RECORD.json'
VALIDATION_OUT = ROOT / 'evidence/N20_VALIDATION_RECORD.json'
MANIFEST = ROOT / 'output/build-manifest.json'


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
        'stderr': proc.stderr.strip()[:2000],
    }


RUNTIME_RECORD = ROOT / 'evidence/N20_RUNTIME_RECORD.json'


def run_harness() -> dict[str, Any]:
    """Run the runtime harness and keep its full record as evidence."""
    RUNTIME_RECORD.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(['node', str(HARNESS), '--record', str(RUNTIME_RECORD)],
                          cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f'FAIL n20-runtime-harness: {proc.stderr.strip()[:2000]}')
    return json.loads(RUNTIME_RECORD.read_text(encoding='utf-8'))


def measure_budgets() -> dict[str, Any]:
    """The Section 1.3 byte accounting, measured against the built artifact.

    The ceilings come from tools/byte_budget.py — one source for every gate —
    so that a re-budget is recorded once and stays visible everywhere.
    """
    if not MANIFEST.exists():
        return {'status': 'FAIL', 'reason': 'output/build-manifest.json is missing; run the build first.'}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    measured = byte_budget.measure_budgets(manifest)
    measured['notes'] = [
        'The bank island is the runtime projection of the frozen bank; the per-instance '
        'audit tables (draws, derived, review workflow) stay in data/bank/*.json and in '
        'the N20 evidence records.',
        'The CSS measurement is below the Section 1.3 target range; that content belongs '
        'to earlier phases and N20 records the measurement instead of changing it.',
        'The runtime JS and artifact-total ceilings were re-set on the measured '
        'requirement by N21 (see byte_budget.RE_BUDGET_HISTORY); the declared plan band '
        'and the deviation stay visible in the same records.',
    ]
    return measured


def write_verification_record(record: dict[str, Any], manifest: dict[str, Any],
                              harness_checks: dict[str, Any]) -> None:
    """The machine-readable verification record: the claims and their evidence.

    Every entry names the command or the artefact that produced it, so that a
    reader can reproduce the claim instead of trusting it.
    """
    bank = manifest.get('bank_island', {})
    verification = {
        'schema_version': 1,
        'owner': 'N20',
        'status': record['status'],
        'policy_label': record['policy_label'],
        'official_programme_facts': {
            'topics': 7,
            'examination': 'written on paper',
            'maximum_minutes': 180,
            'note': 'The 2025 programme fixes no point weight, no question count, no pass '
                    'mark, no allowed aid and no exact exam question type.',
        },
        'acceptance_criteria': {
            'AC1_happy_path': {
                'status': 'PASS' if (record['gates']['template_gate']['status'] == 'PASS'
                                     and harness_checks.get('cross_language_parity', {}).get('status') == 'PASS'
                                     and harness_checks.get('determinism', {}).get('status') == 'PASS') else 'FAIL',
                'claims': [
                    'Every family template validates: ranges, conventions entries, response '
                    'types, payload classes, tolerance classes and rubric weights.',
                    'A scratch template with an out-of-range parameter fails validation by '
                    'family and parameter name.',
                    'The required types Q02, Q04, Q10, Q11, Q12, Q13 and Q15 are covered and '
                    'their families are named in the template validation record.',
                    'Identical seeds yield byte-identical instances, and the Python and the '
                    'JavaScript twins agree byte for byte on all 112 instances.',
                ],
                'evidence': ['tools/validate_family_templates.py',
                             'evidence/N20_TEMPLATE_VALIDATION.json',
                             'evidence/N20_DETERMINISM_RECORD.json',
                             'evidence/N20_RUNTIME_RECORD.json'],
            },
            'AC2_negative_or_edge': {
                'status': 'PASS' if (record['gates']['bank_schema_gate']['status'] == 'PASS'
                                     and record['gates']['bank_review_gate']['status'] == 'PASS'
                                     and record['gates']['scratch_refusal_proof']['status'] == 'PASS') else 'FAIL',
                'claims': [
                    'All 112 instances validate against the N04 schema with zero violations.',
                    'Every numeric key value was recomputed through the N17 quantity engine '
                    'or the N18 criterion discipline, and the recompute is recorded per instance.',
                    'The review workflow gate passes, and an unreviewed scratch instance '
                    'refuses the build by id.',
                    'The leak scan finds no unexempted leak; every exemption carries an N12 '
                    'reason code, a Latvian reason and an explicit scope.',
                    'The grading alignment is graded through the owning engine for every '
                    'payload class.',
                ],
                'evidence': ['evidence/N20_REVIEW_WORKFLOW.json',
                             'evidence/N20_RECOMPUTE_RECORD.json',
                             'evidence/N20_LEAK_SCAN_RECORD.json'],
            },
            'AC3_domain_integrity': {
                'status': 'PASS' if all(harness_checks.get(name, {}).get('status') == 'PASS'
                                        for name in ('tamper_fixture', 'ephemeral_path',
                                                      'parity_fixture', 'smoke_vector')) else 'FAIL',
                'claims': [
                    'The runtime loader rejects a tampered island by digest mismatch and a '
                    'missing digest by name.',
                    'The ephemeral retry path is deterministic, excludes the frozen seeds and '
                    'never persists.',
                    'The frozen and the ephemeral instance are graded through identical engine '
                    'code and yield the same verdict class.',
                    'The in-file smoke vector runs against the built artifact and asserts the '
                    'grading verdict of a fixed bank instance.',
                ],
                'evidence': ['evidence/N20_RUNTIME_RECORD.json', 'src/smoke-subset.js'],
            },
        },
        'frozen_bank': {
            'instances': 112,
            'families': 28,
            'variants_per_family': 4,
            'island_digest': bank.get('digest'),
            'embedded_digest': bank.get('embedded_digest'),
            'source_digest': bank.get('source_digest'),
            'island_bytes': bank.get('bytes'),
            'projection': bank.get('projection'),
            'review_gate': bank.get('review_gate'),
        },
        'templates': {
            'families': 28,
            'variants': 112,
            'template_digest': manifest.get('variant_engine_layer', {}).get('template_digest'),
            'data': manifest.get('variant_engine_layer', {}).get('template_data'),
            'runtime_asset': manifest.get('variant_engine_layer', {}).get('template_asset'),
            'inlined_in_artifact': manifest.get('variant_engine_layer', {}).get('inlined_in_artifact'),
        },
        'ephemeral_contract': manifest.get('variant_engine_layer', {}).get('ephemeral_contract'),
        'budgets': record['budgets'],
        'handoff': record['handoff'],
        'evidence_index': {
            'note': 'Every N20 evidence artifact and what it holds. The gate-level '
                    'summary is the validation record; the per-instance detail lives '
                    'in the records it points at.',
            'artifacts': {
                'evidence/N20_VALIDATION_RECORD.json':
                    'The gate-level summary: each gate, its status, its command and '
                    'its findings.',
                'evidence/N20_CORPUS_RECORD.json':
                    'The extended corpus: four gates, the runtime harness, the byte '
                    'accounting and the handoff. Byte-identical across two runs.',
                'evidence/N20_TEMPLATE_VALIDATION.json':
                    'The per-family validation table: ranges, conventions entries, '
                    'types, payload classes, tolerance classes and rubric weights.',
                'evidence/N20_DETERMINISM_RECORD.json':
                    'The determinism proof: 112/112 byte-identical on a repeated '
                    'instantiation and 112/112 equal to the frozen bank instance.',
                'evidence/N20_RUNTIME_RECORD.json':
                    'The runtime harness: cross-language parity, determinism, the '
                    'ephemeral path, the parity fixture, the tamper fixture and the '
                    'in-file smoke vector against the built artifact.',
                'evidence/N20_REVIEW_WORKFLOW.json':
                    'The review workflow: 112 instances in the accepted state, five '
                    'mechanical checks each, the named checks and the sign-off.',
                'evidence/N20_RECOMPUTE_RECORD.json':
                    'The N17 recompute table: every derived value recomputed through '
                    'the N17 quantity engine with its engine path.',
                'evidence/N20_LEAK_SCAN_RECORD.json':
                    'The N12 leak scan over all 112 instances, the reasoned exemptions '
                    'and the borderline-significance cases.',
                'evidence/N20_SEED_TABLE.json':
                    'The per-instance seed table: family, variant, seed key, seed and '
                    'the derived-values record.',
                'evidence/N20_VERIFICATION_RECORD.md':
                    'The narrative record of the same evidence, with the reasoning '
                    'behind the design choices.',
            },
        },
        'not_claimed': [
            'No official examination, grade or proctoring status.',
            'No browser render, screen-reader, print or instructor acceptance: the '
            'accessibility review is a mechanical structural check, and the renderer-level '
            'acceptance is deferred to N22/N34.',
            'No keyword matching as semantic grading: the N12 scanner is a token and '
            'unit-normalised rule, not a semantic grader.',
            'No claim that the four variants are four finished questions: they are four '
            'parameterisations of one family template.',
        ],
    }
    VERIFICATION_OUT.parent.mkdir(parents=True, exist_ok=True)
    VERIFICATION_OUT.write_text(json.dumps(verification, ensure_ascii=False, indent=2,
                                           sort_keys=True) + '\n', encoding='utf-8')


def write_validation_record(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    """The gate-level validation record: what each gate checked and what it found.

    It is the short form of the corpus record: the gate statuses, the counts
    and the failure lists. The detailed per-instance evidence lives in the
    template, workflow, recompute and leak records.
    """
    gates = record['gates']

    def report_of(label: str) -> dict[str, Any]:
        """The parsed JSON report of a gate, or an empty dict.

        A gate that prints a human-readable summary rather than JSON has no
        parsed report; the record then carries the status and the command
        only, never a fabricated report.
        """
        report = gates[label].get('report')
        return report if isinstance(report, dict) else {}

    validation = {
        'schema_version': 1,
        'owner': 'N20',
        'status': record['status'],
        'gates': {
            'template_validation': {
                'status': gates['template_gate']['status'],
                'command': gates['template_gate']['command'],
                'evidence': 'evidence/N20_TEMPLATE_VALIDATION.json',
                'violations': report_of('template_gate').get('violations', []),
            },
            'determinism': {
                'status': 'PASS' if record['runtime']['checks'].get('determinism') == 'PASS' else 'FAIL',
                'claim': 'Identical seeds produce byte-identical instances; the frozen bank '
                         'is reproducible from the templates and the seed alone.',
                'evidence': 'evidence/N20_DETERMINISM_RECORD.json',
            },
            'bank_schema': {
                'status': gates['bank_schema_gate']['status'],
                'command': gates['bank_schema_gate']['command'],
                'violations': report_of('bank_schema_gate').get('violations', []),
            },
            'bank_review': {
                'status': gates['bank_review_gate']['status'],
                'command': gates['bank_review_gate']['command'],
                'instances': report_of('bank_review_gate').get('instances'),
                'violations': report_of('bank_review_gate').get('violations', []),
                'evidence': 'evidence/N20_REVIEW_WORKFLOW.json',
            },
            'scratch_refusal': {
                'status': gates['scratch_refusal_proof']['status'],
                'command': gates['scratch_refusal_proof']['command'],
                'scratch_question_id': report_of('scratch_refusal_proof').get(
                    'scratch_question_id'),
                'refusal': report_of('scratch_refusal_proof').get('refusal', []),
            },
            'runtime': {
                'status': record['runtime']['status'],
                'checks': record['runtime']['checks'],
                'evidence': 'evidence/N20_RUNTIME_RECORD.json',
            },
        },
        'counts': {
            'families': 28,
            'variants': 112,
            'instances': manifest.get('bank_island', {}).get('questions_count'),
            'bank_island_bytes': manifest.get('bank_island', {}).get('bytes'),
            'artifact_bytes': manifest.get('output_bytes'),
        },
        'digests': record['digests'],
        'budgets': record['budgets'],
        'violations': [],
    }
    VALIDATION_OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_OUT.write_text(json.dumps(validation, ensure_ascii=False, indent=2,
                                         sort_keys=True) + '\n', encoding='utf-8')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    template_gate = run_tool([sys.executable, str(TEMPLATE_GATE), '--no-evidence'], 'template_gate')
    schema_gate = run_tool([sys.executable, str(BANK_VALIDATOR), '--bank', 'data/bank',
                            '--require-types'], 'bank_schema_gate')
    review_gate = run_tool([sys.executable, str(REVIEW_GATE)], 'bank_review_gate')
    scratch = run_tool([sys.executable, str(REVIEW_GATE), '--prove-scratch-refusal'],
                       'scratch_refusal_proof')
    harness = run_harness()
    budgets = measure_budgets()

    gates = [template_gate, schema_gate, review_gate, scratch]
    harness_checks = harness.get('checks', {})
    harness_status = harness.get('status')
    scratch_report = scratch.get('report')
    scratch_status = (scratch_report.get('status')
                      if isinstance(scratch_report, dict) else None)
    status = 'PASS' if (all(gate['status'] == 'PASS' for gate in gates)
                        and harness_status == 'PASS'
                        and budgets['status'] == 'PASS'
                        and scratch_status == 'PASS') else 'FAIL'

    manifest: dict[str, Any] = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))

    record = {
        'schema_version': 1,
        'owner': 'N20',
        'status': status,
        'policy_label': 'PROPOSED training policy (N20): 28 families x 4 variants = 112 '
                        'instances, point weights and minute budgets are proposals. Official '
                        'programme facts: seven topics, a written-on-paper examination and a '
                        'maximum of 180 minutes.',
        'gates': {
            'template_gate': template_gate,
            'bank_schema_gate': schema_gate,
            'bank_review_gate': review_gate,
            'scratch_refusal_proof': scratch,
        },
        'runtime': {
            'status': harness_status,
            'record': 'evidence/N20_RUNTIME_RECORD.json',
            'checks': {name: check.get('status') for name, check in harness_checks.items()},
            'cross_language_parity': harness_checks.get('cross_language_parity', {}).get('rows'),
            'ephemeral_path': harness_checks.get('ephemeral_path'),
            'parity_fixture': harness_checks.get('parity_fixture'),
            'tamper_fixture': harness_checks.get('tamper_fixture'),
            'smoke_vector': harness_checks.get('smoke_vector'),
        },
        'budgets': budgets,
        'digests': {
            'bank_island_digest': manifest.get('bank_island', {}).get('digest'),
            'bank_embedded_digest': manifest.get('bank_island', {}).get('embedded_digest'),
            'bank_source_digest': manifest.get('bank_island', {}).get('source_digest'),
            'template_digest': manifest.get('variant_engine_layer', {}).get('template_digest'),
            'artifact_sha256': manifest.get('output_sha256'),
        },
        'sources': {
            'variant_engine_python': sha256_file(ROOT / 'tools/variant_engine.py'),
            'variant_engine_javascript': sha256_file(ROOT / 'src/variant-engine.js'),
            'variant_templates_asset': sha256_file(ROOT / 'src/variant-templates.js'),
            'content': sha256_file(ROOT / 'tools/n20_content.py'),
            'template_author': sha256_file(ROOT / 'tools/author_family_templates.py'),
            'bank_author': sha256_file(ROOT / 'tools/author_bank.py'),
            'template_gate': sha256_file(TEMPLATE_GATE),
            'review_gate': sha256_file(REVIEW_GATE),
            'harness': sha256_file(HARNESS),
            'bank_loader': sha256_file(ROOT / 'src/bank-loader.js'),
        },
        'handoff': {
            'exam_assembly_N24': {
                'bank_digest': manifest.get('bank_island', {}).get('digest'),
                'instance_ids': 'COL1-{topic}-{family}-{variant}-01, 112 in total',
            },
            'remediation_N28_and_bounded_practice_N30': {
                'ephemeral_contract': manifest.get('variant_engine_layer', {}).get('ephemeral_contract'),
                'family_templates': manifest.get('variant_engine_layer', {}).get('template_data'),
                'runtime_module': manifest.get('variant_engine_layer', {}).get('runtime_module'),
            },
            'grading_surfaces_N23': {
                'numeric_graph': 'N17-numeric',
                'option_select_ordering_matching': 'N19-method',
                'method_payload_class': 'self-assessed; N17 denies machine criteria on it',
            },
        },
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                   encoding='utf-8')
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
        'budgets': {entry['name']: f"{entry['kib']} KiB" for entry in budgets['budgets']},
    }, ensure_ascii=False, indent=2))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
