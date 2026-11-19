#!/usr/bin/env python3
"""N04 QUESTION_SCHEMA self-check and bank validator.

Validates data/question_schema.json (schema self-check and cross-island
consistency against N02 coverage, N03 conventions, blueprint, and N09 stub)
and validates a question bank directory or file at both instance level and
set level. Exits nonzero on any violation.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import jsonschema

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, load_json  # noqa: E402

SCHEMA_PATH = 'data/question_schema.json'
COVERAGE_PATH = 'data/coverage.json'
CONVENTIONS_PATH = 'data/conventions.json'
BLUEPRINT_PATH = 'docs/SIMULATION_BLUEPRINT.json'
FAMILIES_PATH = 'docs/QUESTION_FAMILIES.json'
TYPES_DOC_PATH = 'docs/QUESTION_TYPES_AND_VARIANTS.md'

EXPECTED_TYPE_IDS = [f'Q{i:02d}' for i in range(1, 19)]


def _violation(level: str, file_label: str, field: str, message: str, question_id: str | None = None) -> dict[str, Any]:
    return {
        'level': level,
        'file': file_label,
        'question_id': question_id or '<unknown>',
        'field': field,
        'message': message,
    }


def _extract_field_path(error: jsonschema.ValidationError) -> str:
    parts = [str(p) for p in error.absolute_path]
    if error.validator == 'required' and isinstance(error.message, str):
        match = re.search(r"'([^']+)' is a required property", error.message)
        if match:
            parts.append(match.group(1))
    return '.'.join(parts) if parts else '<root>'


def validate_schema(schema_path: Path, repo_root: Path) -> tuple[dict[str, Any] | None, dict[str, Any], list[dict[str, Any]]]:
    """Validate the schema artifact itself against planning contracts."""
    file_label = str(schema_path.relative_to(repo_root)) if schema_path.is_relative_to(repo_root) else str(schema_path)
    violations: list[dict[str, Any]] = []

    try:
        schema = json.loads(schema_path.read_text(encoding='utf-8'))
    except Exception as exc:
        violations.append(_violation('schema', file_label, '<root>', f'Malformed schema JSON: {exc}'))
        return None, {'status': 'FAIL'}, violations

    if not isinstance(schema, dict):
        violations.append(_violation('schema', file_label, '<root>', 'Schema root must be a JSON object'))
        return None, {'status': 'FAIL'}, violations

    for key in ('shared_core', 'payload_classes', 'types', 'required_types_per_form', 'discriminator_rule', 'cross_island_bindings', 'authoring_workflow_contract'):
        if key not in schema:
            violations.append(_violation('schema', file_label, key, f'Missing top-level schema section {key}'))

    if violations:
        return None, {'status': 'FAIL'}, violations

    # 1. Exact 18 types Q01..Q18.
    types_map = schema['types']
    if not isinstance(types_map, dict) or sorted(types_map.keys()) != EXPECTED_TYPE_IDS:
        violations.append(_violation(
            'schema', file_label, 'types',
            f'types keys must match {EXPECTED_TYPE_IDS} exactly; got {sorted(types_map.keys()) if isinstance(types_map, dict) else type(types_map).__name__}'
        ))

    # 2. Payload classes defined once and referenced by name.
    payload_classes = schema['payload_classes']
    if not isinstance(payload_classes, dict) or not payload_classes:
        violations.append(_violation('schema', file_label, 'payload_classes', 'payload_classes must be a non-empty object'))
        payload_classes = {}
    else:
        for pc_name, pc_schema in payload_classes.items():
            if not isinstance(pc_schema, dict) or 'required' not in pc_schema or 'properties' not in pc_schema:
                violations.append(_violation('schema', file_label, f'payload_classes.{pc_name}', 'Each payload class must define required and properties'))

    # 3. Check each type entry.
    declared_required_from_types: list[str] = []
    if isinstance(types_map, dict):
        for qid, tdef in types_map.items():
            if not isinstance(tdef, dict):
                violations.append(_violation('schema', file_label, f'types.{qid}', 'Type definition must be an object'))
                continue
            for req_k in ('id', 'name_lv', 'payload_class', 'required_per_form', 'engine', 'blueprint_ref'):
                if req_k not in tdef:
                    violations.append(_violation('schema', file_label, f'types.{qid}.{req_k}', f'Missing {req_k} in type {qid}'))
            pc = tdef.get('payload_class')
            if pc not in payload_classes:
                violations.append(_violation('schema', file_label, f'types.{qid}.payload_class', f'Unknown payload_class {pc!r}'))
            if tdef.get('required_per_form') is True:
                declared_required_from_types.append(qid)

    # 4. Required types match SIMULATION_BLUEPRINT.json verbatim.
    blueprint_path = repo_root / BLUEPRINT_PATH
    if blueprint_path.exists():
        blueprint = load_json(blueprint_path)
        bp_required = blueprint.get('constraints', {}).get('required_types_per_form', [])
        if schema.get('required_types_per_form') != bp_required:
            violations.append(_violation(
                'schema', file_label, 'required_types_per_form',
                f'required_types_per_form {schema.get("required_types_per_form")} != blueprint {bp_required}'
            ))
        if sorted(declared_required_from_types) != sorted(bp_required):
            violations.append(_violation(
                'schema', file_label, 'types.*.required_per_form',
                f'types marked required_per_form {sorted(declared_required_from_types)} != blueprint {sorted(bp_required)}'
            ))

    # 5. Check QUESTION_TYPES_AND_VARIANTS.md mentions all Q01..Q18.
    types_doc = repo_root / TYPES_DOC_PATH
    if types_doc.exists():
        doc_text = types_doc.read_text(encoding='utf-8')
        missing_in_doc = [qid for qid in EXPECTED_TYPE_IDS if f'| {qid} |' not in doc_text]
        if missing_in_doc:
            violations.append(_violation('schema', file_label, 'types', f'Types missing in {TYPES_DOC_PATH}: {missing_in_doc}'))

    # 6. Check shared_core has required, properties, payload_class discriminator, and extensions slot.
    shared_core = schema['shared_core']
    props = shared_core.get('properties', {}) if isinstance(shared_core, dict) else {}
    if 'payload_class' not in shared_core.get('required', []) or 'payload_class' not in props:
        violations.append(_violation('schema', file_label, 'shared_core.properties.payload_class', 'shared_core must require payload_class discriminator'))
    else:
        pc_enum = props['payload_class'].get('enum', [])
        if sorted(pc_enum) != sorted(payload_classes.keys()):
            violations.append(_violation('schema', file_label, 'shared_core.properties.payload_class.enum', f'payload_class enum {pc_enum} != payload_classes {list(payload_classes.keys())}'))
    if 'extensions' not in props:
        violations.append(_violation('schema', file_label, 'shared_core.properties.extensions', 'shared_core must declare typed extensions slot'))

    info = {
        'status': 'PASS' if not violations else 'FAIL',
        'types_count': len(types_map) if isinstance(types_map, dict) else 0,
        'payload_classes': sorted(payload_classes.keys()),
        'required_types_per_form': schema.get('required_types_per_form', []),
    }
    return schema, info, violations


def _load_cross_island_vocab(schema: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    coverage = load_json(repo_root / COVERAGE_PATH)
    outcome_topic = {o['id']: o['topic'] for o in coverage['outcomes']}

    conventions = load_json(repo_root / CONVENTIONS_PATH)
    tolerance_classes = {q['id'] for q in conventions['tolerances']['quantity_classes']}

    families_doc = load_json(repo_root / FAMILIES_PATH)
    family_ids = {f['family_id'] for f in families_doc['families']}

    mc_pattern = schema['cross_island_bindings']['misconception_signatures']['pattern']
    return {
        'outcome_topic': outcome_topic,
        'tolerance_classes': tolerance_classes,
        'family_ids': family_ids,
        'mc_regex': re.compile(mc_pattern),
    }


def _collect_bank_files(bank_path: Path) -> list[Path]:
    if bank_path.is_file():
        return [bank_path]
    if bank_path.is_dir():
        return sorted(p for p in bank_path.rglob('*.json') if p.is_file())
    return []


def validate_bank(
    schema_path: Path,
    repo_root: Path,
    bank_path: Path | None = None,
    require_all_required_types: bool = False,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    schema, schema_info, schema_violations = validate_schema(schema_path, repo_root)
    if schema_violations or schema is None:
        return {
            'status': 'FAIL',
            'schema_check': schema_info,
            'counts': {'files': 0, 'instances': 0, 'by_type': {}, 'by_family': {}, 'by_topic': {}, 'by_payload_class': {}},
            'violations': schema_violations,
            'duration_ms': round((time.perf_counter() - t0) * 1000.0, 3),
        }

    vocab = _load_cross_island_vocab(schema, repo_root)
    core_validator = jsonschema.Draft202012Validator({
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        'type': 'object',
        'required': schema['shared_core']['required'],
        'properties': schema['shared_core']['properties'],
        'additionalProperties': False,
    })
    payload_validators = {
        name: jsonschema.Draft202012Validator({
            '$schema': 'https://json-schema.org/draft/2020-12/schema',
            'type': 'object',
            'required': spec['required'],
            'properties': spec['properties'],
            'additionalProperties': False,
        })
        for name, spec in schema['payload_classes'].items()
    }

    violations: list[dict[str, Any]] = []
    by_type: dict[str, int] = {}
    by_family: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    by_payload_class: dict[str, int] = {}
    seen_ids: dict[str, str] = {}
    seen_types: set[str] = set()
    files_read = 0
    total_instances = 0

    if bank_path is not None:
        if not bank_path.exists():
            violations.append(_violation('set', str(bank_path), '<bank>', f'Bank path does not exist: {bank_path}'))
        else:
            files = _collect_bank_files(bank_path)
            if not files:
                violations.append(_violation('set', str(bank_path), '<bank>', f'No JSON files found in bank path: {bank_path}'))
            for file_path in files:
                files_read += 1
                file_label = str(file_path.relative_to(repo_root)) if file_path.is_relative_to(repo_root) else str(file_path)
                try:
                    raw = json.loads(file_path.read_text(encoding='utf-8'))
                except Exception as exc:
                    violations.append(_violation('instance', file_label, '<root>', f'Invalid JSON: {exc}'))
                    continue

                if isinstance(raw, dict) and 'questions' in raw and isinstance(raw['questions'], list):
                    instances = raw['questions']
                elif isinstance(raw, list):
                    instances = raw
                elif isinstance(raw, dict):
                    instances = [raw]
                else:
                    violations.append(_violation('instance', file_label, '<root>', 'Expected question object, list, or {questions: [...]}'))
                    continue

                for idx, inst in enumerate(instances):
                    total_instances += 1
                    if not isinstance(inst, dict):
                        violations.append(_violation('instance', file_label, f'[{idx}]', 'Question instance must be a JSON object'))
                        continue

                    qid = inst.get('question_id') if isinstance(inst.get('question_id'), str) else f'<index:{idx}>'

                    # Set-level duplicate question_id check.
                    if isinstance(inst.get('question_id'), str) and inst['question_id']:
                        if inst['question_id'] in seen_ids:
                            violations.append(_violation(
                                'set', file_label, 'question_id',
                                f'Duplicate question_id {inst["question_id"]!r} (first seen in {seen_ids[inst["question_id"]]})',
                                question_id=qid,
                            ))
                        else:
                            seen_ids[inst['question_id']] = file_label

                    # Core JSON Schema validation.
                    for err in sorted(core_validator.iter_errors(inst), key=lambda e: list(e.absolute_path)):
                        violations.append(_violation('instance', file_label, _extract_field_path(err), err.message, question_id=qid))

                    # Type & discriminator check.
                    type_id = inst.get('type_id')
                    type_ids = inst.get('type_ids')
                    payload_class = inst.get('payload_class')
                    if isinstance(type_id, str) and type_id in schema['types']:
                        by_type[type_id] = by_type.get(type_id, 0) + 1
                        seen_types.add(type_id)
                        expected_pc = schema['types'][type_id]['payload_class']
                        if payload_class != expected_pc:
                            violations.append(_violation(
                                'instance', file_label, 'payload_class',
                                f'Type {type_id} requires payload_class {expected_pc!r}, got {payload_class!r}',
                                question_id=qid,
                            ))
                        if isinstance(type_ids, list):
                            for tid in type_ids:
                                if isinstance(tid, str):
                                    seen_types.add(tid)
                            if type_id not in type_ids:
                                violations.append(_violation(
                                    'instance', file_label, 'type_ids',
                                    f'Primary type_id {type_id!r} must appear in type_ids',
                                    question_id=qid,
                                ))

                    # Payload validation.
                    if isinstance(payload_class, str) and payload_class in payload_validators:
                        by_payload_class[payload_class] = by_payload_class.get(payload_class, 0) + 1
                        payload = inst.get('payload')
                        if isinstance(payload, dict):
                            for err in sorted(payload_validators[payload_class].iter_errors(payload), key=lambda e: list(e.absolute_path)):
                                violations.append(_violation(
                                    'instance', file_label, f'payload.{_extract_field_path(err)}',
                                    err.message, question_id=qid,
                                ))
                            # Cross-island tolerance_class check (N03).
                            if payload_class == 'numeric':
                                tc = payload.get('tolerance_class')
                                if isinstance(tc, str) and tc not in vocab['tolerance_classes']:
                                    violations.append(_violation(
                                        'instance', file_label, 'payload.tolerance_class',
                                        f'tolerance_class {tc!r} not found in data/conventions.json',
                                        question_id=qid,
                                    ))
                            elif payload_class == 'graph':
                                tr = payload.get('target_readout')
                                if isinstance(tr, dict):
                                    tc = tr.get('tolerance_class')
                                    if isinstance(tc, str) and tc not in vocab['tolerance_classes']:
                                        violations.append(_violation(
                                            'instance', file_label, 'payload.target_readout.tolerance_class',
                                            f'tolerance_class {tc!r} not found in data/conventions.json',
                                            question_id=qid,
                                        ))

                    # Family & topic consistency.
                    fam = inst.get('family_id')
                    topic = inst.get('topic')
                    if isinstance(topic, int) and not isinstance(topic, bool):
                        by_topic[str(topic)] = by_topic.get(str(topic), 0) + 1
                    if isinstance(fam, str):
                        by_family[fam] = by_family.get(fam, 0) + 1
                        if fam not in vocab['family_ids']:
                            violations.append(_violation(
                                'instance', file_label, 'family_id',
                                f'family_id {fam!r} not found in docs/QUESTION_FAMILIES.json',
                                question_id=qid,
                            ))
                        elif isinstance(topic, int) and not isinstance(topic, bool):
                            fam_topic = int(fam[4])
                            if fam_topic != topic:
                                violations.append(_violation(
                                    'instance', file_label, 'family_id',
                                    f'family_id {fam!r} topic {fam_topic} != instance topic {topic}',
                                    question_id=qid,
                                ))

                    # Cross-island outcome_ids check (N02).
                    outcome_ids = inst.get('outcome_ids')
                    if isinstance(outcome_ids, list):
                        for oid in outcome_ids:
                            if not isinstance(oid, str) or oid not in vocab['outcome_topic']:
                                violations.append(_violation(
                                    'instance', file_label, 'outcome_ids',
                                    f'outcome_id {oid!r} not found in data/coverage.json',
                                    question_id=qid,
                                ))

                    # Cross-island misconception_signatures stub check (N09).
                    mcs = inst.get('misconception_signatures')
                    if isinstance(mcs, list):
                        for mc in mcs:
                            if not isinstance(mc, str) or not vocab['mc_regex'].match(mc):
                                violations.append(_violation(
                                    'instance', file_label, 'misconception_signatures',
                                    f'misconception signature {mc!r} does not match N09 stub pattern',
                                    question_id=qid,
                                ))

            if require_all_required_types:
                missing_req = [t for t in schema['required_types_per_form'] if t not in seen_types]
                if missing_req:
                    violations.append(_violation(
                        'set', str(bank_path), 'required_types_per_form',
                        f'Bank is missing required per-form types: {missing_req}',
                    ))

    return {
        'status': 'PASS' if not violations else 'FAIL',
        'schema_check': schema_info,
        'counts': {
            'files': files_read,
            'instances': total_instances,
            'by_type': dict(sorted(by_type.items())),
            'by_family': dict(sorted(by_family.items())),
            'by_topic': dict(sorted(by_topic.items())),
            'by_payload_class': dict(sorted(by_payload_class.items())),
        },
        'violations': violations,
        'duration_ms': round((time.perf_counter() - t0) * 1000.0, 3),
    }


def format_summary(report: dict[str, Any]) -> str:
    sc = report.get('schema_check', {})
    cnt = report.get('counts', {})
    return (
        f'{report["status"]} bank-schema: {sc.get("types_count", 0)} types, '
        f'{len(sc.get("payload_classes", []))} payload classes, '
        f'{cnt.get("files", 0)} files, {cnt.get("instances", 0)} instances, '
        f'{len(report.get("violations", []))} violations ({report.get("duration_ms", 0)} ms)'
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schema', default=str(DEST / SCHEMA_PATH))
    parser.add_argument('--bank', default=None, help='Bank directory or JSON file to validate')
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--require-types', action='store_true', help='Require all 7 per-form required types in the bank')
    parser.add_argument('--report', default=None, help='Write JSON report to path')
    parser.add_argument('--json', action='store_true', help='Print JSON report to stdout')
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = repo_root / schema_path
    bank_path = Path(args.bank) if args.bank else None
    if bank_path is not None and not bank_path.is_absolute():
        bank_path = repo_root / bank_path

    report = validate_bank(
        schema_path=schema_path,
        repo_root=repo_root,
        bank_path=bank_path,
        require_all_required_types=args.require_types,
    )
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = repo_root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_summary(report))
        for v in report['violations'][:20]:
            print(f'  [{v["level"]}] {v["file"]} ({v["question_id"]}) {v["field"]}: {v["message"]}', file=sys.stderr)

    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
