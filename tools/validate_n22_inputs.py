#!/usr/bin/env python3
"""N22 build gate: the response-type registry, its semantics and its ARIA bank.

This gate is the build's N22 checkpoint. It refuses the build when:

- the ``#sim-response-types`` island is not the frozen shape (schema_version 1,
  island id ``sim-response-types``, exactly the eighteen type ids Q01-Q18);
- the island drifts from the frozen N04 contract: ``payload_kind`` must equal
  ``types[id].payload_class``, ``engine_binding`` must equal ``types[id].engine``,
  ``required_per_form`` must equal the schema's flag, and ``completed_type``
  must be true for exactly Q02, Q04, Q10, Q11, Q12, Q13, Q15 (AC1);
- a ``renderer_key`` is not one of ``src/bank-loader.js`` ``RENDERER_REGISTRY``
  keys, or a type is missing one of its render / payload / completion / error /
  ARIA contracts, or a completed type lacks a grading binding (AC1);
- a payload variant contradicts ``data/exam_policy.json``
  ``session_contract.payload_contracts``: an unknown kind, a missing declared
  field, or a ride-along field typed differently from the declared type;
- a Latvian ARIA name does not resolve in ``data/terms.json`` (the label bank is
  term-keyed, never a literal), a name pattern uses an unknown ``{slot}``, or a
  name carries a raw unit literal instead of referencing the quantity;
- an ``error_surfaces`` id is not in the frozen N17/N18/N19 vocabulary, a
  ``feedback_keys`` value does not resolve in the term bank, or the completion
  model can emit an id the type does not declare;
- the compiled registry module differs from its TypeScript source, so a stale
  module can never ship;
- ``--prove-scratch-refusal`` is given and the gate does *not* refuse a scratch
  type id Q99 by name (A.1.1: an unknown type id must fail loudly, never render
  a fallback text field).

Usage:
    python3 tools/validate_n22_inputs.py --report evidence/N22_REGISTRY_VALIDATION.json
    python3 tools/validate_n22_inputs.py --prove-scratch-refusal
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
ISLAND_PATH = ROOT / 'data/response_types.json'
SCHEMA_PATH = ROOT / 'data/question_schema.json'
TERMS_PATH = ROOT / 'data/terms.json'
POLICY_PATH = ROOT / 'data/exam_policy.json'
TAXONOMY_PATH = ROOT / 'data/engine_taxonomy.json'
METHOD_PATH = ROOT / 'data/method_engine_contract.json'
GRAPH_PATH = ROOT / 'data/graph_scoring_contract.json'
LOADER_PATH = ROOT / 'src/bank-loader.js'
REGISTRY_TS = ROOT / 'src/inputs/registry.ts'
REGISTRY_JS = ROOT / 'src/compiled/inputs/registry.js'
BUILD_PATH = ROOT / 'tools/build.py'
COMPILE_TOOL = ROOT / 'tools/compile_n21_ts.py'
TERMS_TOOL = ROOT / 'tools/validate_terms.py'

ISLAND_ID = 'sim-response-types'
OWNER = 'N22'
TYPE_IDS = [f'Q{i:02d}' for i in range(1, 19)]
COMPLETED_TYPES = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15']
PAYLOAD_KINDS = ['numeric', 'option_select', 'ordering', 'matching', 'graph', 'method']
GRADING_CLASSES = ['auto', 'self', 'pending', 'mixed']
TERM_REF_FIELDS = (
    'name_key', 'label_key', 'title_key', 'term_key', 'path_key', 'parity_key',
    'abort_rule_key', 'message_key', 'description_key',
)
TERM_REF_LISTS = ('term_keys',)
SLOTS = {
    'label', 'step', 'species', 'left', 'option', 'position', 'item', 'axis',
    'count', 'part', 'slot', 'type', 'state', 'message',
}
ENGLISH_WORDS = {
    'the', 'and', 'answer', 'value', 'missing', 'input', 'output', 'field',
    'complete', 'incomplete', 'error', 'label', 'name', 'row', 'column', 'text',
    'button', 'select', 'option', 'check', 'please', 'enter', 'type', 'graph',
}
ALLOWED_KEY_NAMES = {'tab', 'enter', 'alt', 'aria'}


def _display(command: list[str]) -> str:
    """The recorded command line: repository-relative, interpreter-neutral.

    Evidence records carry no absolute paths (house rule), so the interpreter
    is recorded as ``python3`` and the repository root is stripped.
    """
    rendered = []
    for part in command:
        text = str(part)
        if text == sys.executable:
            text = 'python3'
        if text.startswith(str(ROOT) + '/'):
            text = text[len(str(ROOT)) + 1:]
        rendered.append(text)
    return ' '.join(rendered)


def _run(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    return {
        'command': _display(command),
        'returncode': proc.returncode,
        'status': 'PASS' if proc.returncode == 0 else 'FAIL',
        'stdout': proc.stdout.strip()[-4000:],
        'stderr': proc.stderr.strip()[-2000:],
    }


def _renderers() -> dict[str, str]:
    text = LOADER_PATH.read_text(encoding='utf-8')
    block = re.search(r'RENDERER_REGISTRY\s*=\s*\{(.*?)\};', text, re.DOTALL)
    if not block:
        return {}
    return {m.group(1): m.group(2) for m in re.finditer(r"(Q\d{2})\s*:\s*'([^']+)'", block.group(1))}


def _frozen_error_ids() -> dict[str, str]:
    """Every error id the frozen islands declare, with the island it comes from."""
    found: dict[str, str] = {}
    taxonomy = load_json(TAXONOMY_PATH)
    for entry in taxonomy['error_taxonomy']['classes']:
        found[entry['id']] = 'data/engine_taxonomy.json'
    for entry in taxonomy['error_taxonomy']['classes']:
        for n05 in entry.get('n05_error_classes', []):
            found.setdefault(n05, 'data/engine_taxonomy.json#n05_error_classes')
    method = load_json(METHOD_PATH)
    for engine in method['engines'].values():
        for error_class in engine.get('error_classes', []):
            if error_class != 'NONE':
                found.setdefault(error_class, 'data/method_engine_contract.json')
    graph = load_json(GRAPH_PATH)
    for entry in graph['validity_rules']['classes']:
        found[entry['id']] = 'data/graph_scoring_contract.json'
    return found


def _term_texts() -> dict[str, dict[str, Any]]:
    terms = load_json(TERMS_PATH)
    return {entry['key']: entry for entry in terms['terms']}


def _walk_term_refs(node: Any, path: str, out: list[dict[str, Any]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            sub = f'{path}.{key}' if path else key
            if key in TERM_REF_FIELDS and isinstance(value, str):
                out.append({'path': sub, 'key': value})
            elif key in TERM_REF_LISTS and isinstance(value, list):
                for index, item in enumerate(value):
                    out.append({'path': f'{sub}[{index}]', 'key': item})
            elif key in ('feedback_keys', 'missing', 'announcement_keys') and isinstance(value, dict):
                for slot, term_key in value.items():
                    out.append({'path': f'{sub}.{slot}', 'key': term_key})
            else:
                _walk_term_refs(value, sub, out)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            _walk_term_refs(item, f'{path}[{index}]', out)


def check_island_shape(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    if island.get('schema_version') != 1:
        errors.append(f'island.schema_version must be 1, got {island.get("schema_version")!r}')
    if island.get('island_id') != ISLAND_ID:
        errors.append(f'island.island_id must be {ISLAND_ID!r}, got {island.get("island_id")!r}')
    if island.get('owner') != OWNER:
        errors.append(f'island.owner must be {OWNER!r}, got {island.get("owner")!r}')
    if not island.get('status'):
        errors.append('island.status is missing')

    types = island.get('types')
    if not isinstance(types, dict):
        errors.append('island.types is not an object')
        types = {}
    missing = [tid for tid in TYPE_IDS if tid not in types]
    unexpected = sorted(key for key in types if key not in TYPE_IDS)
    for tid in missing:
        errors.append(f'island.types is missing the frozen type id {tid}')
    for key in unexpected:
        errors.append(f'island.types carries an unknown type id {key}: the registry covers exactly Q01-Q18')

    completed = island.get('completed_types') or []
    if list(completed) != COMPLETED_TYPES:
        errors.append(f'island.completed_types must be {COMPLETED_TYPES}, got {list(completed)}')

    conflicts = island.get('conflicts') or []
    if not conflicts:
        errors.append('island.conflicts is empty: the naming resolutions must stay visible')
    conflict_ids = [entry.get('id') for entry in conflicts]
    for wanted in ('N22-C01', 'N22-C02'):
        if wanted not in conflict_ids:
            errors.append(f'island.conflicts must record {wanted}')
    for entry in conflicts:
        if not entry.get('resolution_lv'):
            errors.append(f"conflict {entry.get('id')!r} has no resolution_lv")

    return {
        'schema_version': island.get('schema_version'),
        'island_id': island.get('island_id'),
        'owner': island.get('owner'),
        'type_count': len(types),
        'missing_type_ids': missing,
        'unknown_type_ids': unexpected,
        'completed_types': list(completed),
        'conflict_ids': conflict_ids,
    }


def check_schema_consistency(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    schema = load_json(SCHEMA_PATH)
    renderers = _renderers()
    if len(renderers) != 18:
        errors.append(f'src/bank-loader.js RENDERER_REGISTRY carries {len(renderers)} renderers, not 18')

    completed_from_schema = list(schema['required_types_per_form'])
    rows = []
    for tid in TYPE_IDS:
        entry = island['types'].get(tid) or {}
        declared = schema['types'].get(tid) or {}
        problems = []
        if 'name_key' not in entry:
            problems.append('name_key')
        if 'fields' not in entry:
            problems.append('fields')
        if 'completion_rule' not in entry:
            problems.append('completion_rule')
        if 'error_surfaces' not in entry:
            problems.append('error_surfaces')
        if 'accessible_alternative' not in entry or 'keyboard' not in entry:
            problems.append('aria')
        if not entry.get('renderer_key'):
            problems.append('renderer_key')
        if problems:
            errors.append(f'{tid} is missing contracts: {sorted(set(problems))}')

        if entry.get('payload_kind') != declared.get('payload_class'):
            errors.append(
                f"{tid}.payload_kind is {entry.get('payload_kind')!r}, "
                f"N04 types[{tid}].payload_class is {declared.get('payload_class')!r}"
            )
        if entry.get('engine_binding') != declared.get('engine'):
            errors.append(
                f"{tid}.engine_binding is {entry.get('engine_binding')!r}, "
                f"N04 types[{tid}].engine is {declared.get('engine')!r}"
            )
        if bool(entry.get('required_per_form')) != bool(declared.get('required_per_form')):
            errors.append(f'{tid}.required_per_form drifts from N04')
        expected_completed = tid in completed_from_schema
        if bool(entry.get('completed_type')) != expected_completed:
            errors.append(f'{tid}.completed_type is {entry.get("completed_type")!r}, expected {expected_completed}')
        if tid not in renderers:
            errors.append(f'{tid} has no renderer in src/bank-loader.js RENDERER_REGISTRY')
        elif entry.get('renderer_key') != renderers[tid]:
            errors.append(
                f'{tid}.renderer_key is {entry.get("renderer_key")!r}, '
                f'bank-loader declares {renderers[tid]!r}'
            )

        grading = entry.get('grading_binding') or {}
        if expected_completed:
            if not grading:
                errors.append(f'{tid} is a completed type without a grading binding (AC1)')
            if grading.get('class') not in GRADING_CLASSES:
                errors.append(f'{tid}.grading_binding.class {grading.get("class")!r} is not one of {GRADING_CLASSES}')
            if not grading.get('engine'):
                errors.append(f'{tid}.grading_binding.engine is empty')
            if not grading.get('consumes'):
                errors.append(f'{tid}.grading_binding.consumes is empty')
            if grading.get('adapter') != 'none':
                errors.append(f'{tid}.grading_binding.adapter is {grading.get("adapter")!r}; the payload must need no adapter')
        rows.append({
            'type_id': tid,
            'payload_kind': entry.get('payload_kind'),
            'renderer_key': entry.get('renderer_key'),
            'completed_type': bool(entry.get('completed_type')),
            'grading_class': grading.get('class'),
            'grading_engine': grading.get('engine'),
        })
    return {
        'renderer_registry_keys': sorted(renderers.values()),
        'rows': rows,
        'completed_types_from_schema': completed_from_schema,
    }


def check_payload_variants(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    policy = load_json(POLICY_PATH)
    contract = policy['session_contract']
    contracts = contract['payload_contracts']
    named = contract.get('named_variants') or {}
    rows = []
    variants = []
    notes: list[dict[str, Any]] = []
    for tid in TYPE_IDS:
        entry = island['types'].get(tid) or {}
        kind = entry.get('payload_kind')
        variant = entry.get('payload_variant')
        variants.append({'type_id': tid, 'kind': kind, 'variant': variant, 'declared_by': 'payload_variant'})
        for extra_variant in sorted((entry.get('completion_rule') or {}).get('variant_rules') or {}):
            if extra_variant != variant:
                variants.append({
                    'type_id': tid, 'kind': kind, 'variant': extra_variant,
                    'declared_by': 'completion_rule.variant_rules',
                })
        declared = contracts.get(kind)
        if declared is None:
            errors.append(f'{tid}.payload_kind {kind!r} is not a declared session payload kind')
            continue
        declared_fields = set(declared.get('field_types') or {})
        rule = entry.get('completion_rule') or {}
        used_fields = set()
        role_types = {
            field.get('role'): field.get('value_type')
            for field in (entry.get('fields') or [])
            if isinstance(field, dict) and field.get('role')
        }
        model = rule.get('model')
        if model == 'graph':
            used_fields.add('variant')
            for variant_name, variant_rule in (rule.get('variant_rules') or {}).items():
                used_fields.add('variant')
                for name in ('record_path', 'plot_path', 'read_path', 'draw_path'):
                    if isinstance(variant_rule.get(name), str):
                        used_fields.add(variant_rule[name].split('.')[0])
        else:
            for name in ('values_path', 'vector_path', 'rows_path', 'pairs_path', 'order_path',
                         'selection_path', 'text_path', 'choice_path', 'fill_ins_path',
                         'conserved_path', 'map_path', 'structure_path', 'explanation_path',
                         'justification_path'):
                if isinstance(rule.get(name), str):
                    used_fields.add(rule[name].split('.')[0])
            if entry.get('payload_variant') is not None:
                used_fields.add('variant')
            if model == 'selection' and rule.get('justification_path'):
                used_fields.add('justification')
        for field_name in sorted(used_fields):
            if field_name in declared_fields:
                continue
            if field_name in ('kind',):
                continue
            # A ride-along field the session contract does not type is allowed.
            # One it types *differently* is a contract contradiction and fails.
            for other_kind, other in contracts.items():
                other_types = other.get('field_types') or {}
                if field_name in other_types and other_kind != kind:
                    declared_type = other_types[field_name]
                    registry_type = role_types.get(field_name)
                    if registry_type is not None and registry_type == declared_type:
                        notes.append({
                            'type_id': tid,
                            'field': field_name,
                            'typed_by': other_kind,
                            'value_type': declared_type,
                        })
                    else:
                        errors.append(
                            f'{tid}: ride-along field {field_name!r} is typed {declared_type!r} by the '
                            f'session contract under kind {other_kind!r}; the registry declares '
                            f'{registry_type!r} under kind {kind!r}'
                        )
        required = list(declared.get('required') or [])
        for field_name in required:
            if field_name not in used_fields:
                errors.append(f'{tid} does not declare the required session field {field_name!r} of kind {kind!r}')
        rows.append({
            'type_id': tid,
            'kind': kind,
            'variant': variant,
            'declared_kind': kind in contracts,
            'used_fields': sorted(used_fields),
        })

    for variant_name, declared in named.items():
        bound = [row for row in variants if row['variant'] == variant_name]
        if not bound:
            errors.append(f'exam_policy names variant {variant_name!r} that no registry entry declares')
        for row in bound:
            if row['kind'] != declared.get('kind'):
                errors.append(
                    f'{row["type_id"]} stores variant {variant_name!r} under kind {row["kind"]!r}, '
                    f'exam_policy says {declared.get("kind")!r}'
                )
    for row in variants:
        if row['variant'] is None:
            continue
        for variant_name, declared in named.items():
            if row['variant'] == variant_name and row['kind'] != declared.get('kind'):
                errors.append(
                    f'{row["type_id"]} stores variant {variant_name!r} under kind {row["kind"]!r}, '
                    f'exam_policy says {declared.get("kind")!r}'
                )
    return {
        'payload_contracts': sorted(contracts.keys()),
        'named_variants': sorted(named.keys()),
        'rows': rows,
        'ride_along_notes': notes,
    }


def check_terms(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    terms = _term_texts()
    refs: list[dict[str, Any]] = []
    _walk_term_refs(island, '', refs)
    unresolved = []
    english = []
    bad_slots = []
    unit_like = []
    grammar = load_json(TERMS_PATH)['unit_grammar']
    symbols = sorted({element['symbol'] for element in grammar['elements'] if element.get('symbol')}, key=len, reverse=True)
    unit_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(symbol) for symbol in symbols) + r')\s*/\s*(?:' + '|'.join(re.escape(symbol) for symbol in symbols) + r')\b')

    for ref in refs:
        key = ref['key']
        entry = terms.get(key)
        if entry is None:
            unresolved.append(ref)
            continue
        text = entry.get('text_lv') or ''
        if entry.get('class') != 'interface':
            errors.append(f'{ref["path"]}: term {key!r} is class {entry.get("class")!r}, expected "interface"')
        for slot in re.findall(r'\{([a-z_]+)\}', text):
            if slot not in SLOTS:
                bad_slots.append({'path': ref['path'], 'key': key, 'slot': slot})
        prose = re.sub(r'\{[a-z_]+\}', ' ', text)
        for token in re.findall(r'[A-Za-z]+', prose):
            lowered = token.lower()
            if lowered in ENGLISH_WORDS and lowered not in ALLOWED_KEY_NAMES:
                english.append({'path': ref['path'], 'key': key, 'word': token})
        if unit_pattern.search(text):
            unit_like.append({'path': ref['path'], 'key': key, 'text': text})
        citation = entry.get('master_citation') or {}
        if key.startswith('input.') and citation.get('source_id') != OWNER:
            errors.append(f'{ref["path"]}: term {key!r} cites {citation.get("source_id")!r}, expected "N22"')
        if not citation.get('anchor_or_page'):
            errors.append(f'{ref["path"]}: term {key!r} has no anchor')

    for ref in unresolved:
        errors.append(f'{ref["path"]}: [E_TERMS_UNKNOWN_KEY] unknown term key {ref["key"]!r}')
    for item in bad_slots:
        errors.append(f'{item["path"]}: term {item["key"]!r} uses unknown slot {{{item["slot"]}}}')
    for item in english:
        errors.append(f'{item["path"]}: term {item["key"]!r} carries the English word {item["word"]!r}')
    for item in unit_like:
        errors.append(f'{item["path"]}: term {item["key"]!r} carries a raw unit literal ({item["text"]!r})')

    cross_check = _run([sys.executable, str(TERMS_TOOL), '--extra-data', 'data/response_types.json'])
    if cross_check['status'] != 'PASS':
        errors.append(f'tools/validate_terms.py --extra-data data/response_types.json failed: {cross_check["stdout"]}')

    return {
        'referenced_keys': len(refs),
        'unique_keys': len({ref['key'] for ref in refs}),
        'unresolved': unresolved,
        'english_words': english,
        'bad_slots': bad_slots,
        'unit_literals': unit_like,
        'validate_terms_cross_check': cross_check,
    }


def check_error_ids(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    frozen = _frozen_error_ids()
    terms = _term_texts()
    declared_ids: dict[str, list[str]] = {}
    feedback_keys: dict[str, str] = {}
    for tid in TYPE_IDS:
        entry = island['types'].get(tid) or {}
        surfaces = entry.get('error_surfaces') or []
        declared_ids[tid] = list(surfaces)
        mapping = entry.get('feedback_keys') or {}
        for error_id in surfaces:
            if error_id not in frozen:
                errors.append(f'{tid}.error_surfaces names {error_id!r}, which no frozen engine island declares')
            if error_id not in mapping:
                errors.append(f'{tid}.feedback_keys has no entry for {error_id!r}')
                continue
            term_key = mapping[error_id]
            if term_key not in terms:
                errors.append(f'{tid}.feedback_keys[{error_id}] -> {term_key!r} does not resolve in #sim-terms')
            if error_id in feedback_keys and feedback_keys[error_id] != term_key:
                errors.append(f'{error_id!r} maps to two different term keys')
            feedback_keys[error_id] = term_key
        extra = sorted(set(mapping) - set(surfaces))
        if extra:
            errors.append(f'{tid}.feedback_keys declares ids outside error_surfaces: {extra}')
    return {
        'frozen_ids': sorted(frozen.keys()),
        'frozen_sources': frozen,
        'declared_by_type': declared_ids,
        'feedback_keys': feedback_keys,
    }


def check_completion_emits(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    rows = []
    for tid in TYPE_IDS:
        entry = island['types'].get(tid) or {}
        surfaces = set(entry.get('error_surfaces') or [])
        rule = entry.get('completion_rule') or {}
        emits: list[str] = []

        def collect(node: Any) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == 'emits' and isinstance(value, list):
                        emits.extend(value)
                    else:
                        collect(value)
            elif isinstance(node, list):
                for item in node:
                    collect(item)

        collect(rule)
        unknown = sorted(set(emits) - surfaces)
        if unknown:
            errors.append(f'{tid}.completion_rule emits {unknown} that error_surfaces does not declare')
        rows.append({'type_id': tid, 'emits': sorted(set(emits)), 'surfaces': sorted(surfaces)})
    return {'rows': rows}


def check_compile_drift(errors: list[str]) -> dict[str, Any]:
    result = _run([sys.executable, str(COMPILE_TOOL), '--check'])
    if result['status'] != 'PASS':
        errors.append(
            'the compiled input modules differ from their TypeScript sources: '
            f'{result["stdout"]} {result["stderr"]}'
        )
    # The record keeps only this module's line: the sibling modules belong to
    # N22-B/N22-C and their byte counts would make this evidence churn.
    lines = [line for line in result['stdout'].splitlines() if 'inputs/registry.js' in line]
    return {
        'command': result['command'],
        'returncode': result['returncode'],
        'status': result['status'],
        'registry_lines': lines,
        'modules_checked': len(result['stdout'].splitlines()),
        'stderr': result['stderr'],
    }


def check_byte_accounting(island: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    island_bytes = canonical_json_bytes(island)
    terms_bytes = canonical_json_bytes(load_json(TERMS_PATH))
    module_bytes = REGISTRY_JS.stat().st_size if REGISTRY_JS.exists() else 0
    if module_bytes == 0:
        errors.append('src/compiled/inputs/registry.js is missing; run tools/compile_n21_ts.py')
    if not BUILD_PATH.exists():
        errors.append('tools/build.py is missing')
    return {
        'island': {
            'source': 'data/response_types.json',
            'digest': sha256_bytes(island_bytes),
            'bytes': len(island_bytes),
            'source_bytes': ISLAND_PATH.stat().st_size,
        },
        'terms_island': {
            'source': 'data/terms.json',
            'digest': sha256_bytes(terms_bytes),
            'bytes': len(terms_bytes),
        },
        'registry_module': {
            'source': 'src/inputs/registry.ts',
            'compiled': 'src/compiled/inputs/registry.js',
            'source_digest': sha256_file(REGISTRY_TS),
            'compiled_digest': sha256_file(REGISTRY_JS) if REGISTRY_JS.exists() else None,
            'compiled_bytes': module_bytes,
        },
        'note_lv': (
            'Šie ir izmērītie N22 apjomi; griestu pārbudžetēšana pieder koordinētājam un N31, '
            'nevis šai pārbaudei.'
        ),
    }


def prove_scratch_refusal(repo_root: Path = ROOT, island_path: Path | None = None) -> dict[str, Any]:
    """Show that the gate and the runtime refuse an unknown type id by name.

    The scratch island is a copy of the frozen island with one extra type entry
    ``Q99`` (a copy of Q01 with its id rewritten). The gate must FAIL and the
    failure must name Q99; the compiled module must throw
    ``E_INPUTS_UNKNOWN_TYPE`` with Q99 in the message. Cleanup is unconditional.
    """
    source = island_path or (repo_root / 'data/response_types.json')
    scratch_dir = Path(tempfile.mkdtemp(prefix='n22-scratch-'))
    try:
        island = load_json(source)
        scratch_island = json.loads(json.dumps(island))
        clone = json.loads(json.dumps(island['types']['Q01']))
        clone['id'] = 'Q99'
        scratch_island['types']['Q99'] = clone
        scratch_path = scratch_dir / 'response_types.json'
        scratch_path.write_text(json.dumps(scratch_island, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

        report = run_gate(repo_root, island_path=scratch_path)
        named = [error for error in report['errors'] if 'Q99' in error]

        # Two runtime refusals: the registry refuses the unknown *instance* type
        # id, and the island that carries it is refused at load, by name.
        script = (
            "const fs=require('fs');"
            f"const R=require({json.dumps(str(REGISTRY_JS))});"
            "const terms=JSON.parse(fs.readFileSync(" + json.dumps(str(repo_root / 'data/terms.json')) + ",'utf8'));"
            "const frozen=JSON.parse(fs.readFileSync(" + json.dumps(str(repo_root / 'data/response_types.json')) + ",'utf8'));"
            "const scratch=JSON.parse(fs.readFileSync(" + json.dumps(str(scratch_path)) + ",'utf8'));"
            "R.load(frozen, terms);"
            "try{R.contractFor('Q99');console.log('UNKNOWN_TYPE|NO_REFUSAL');}"
            "catch(e){console.log('UNKNOWN_TYPE|'+e.code+'|'+e.message);}"
            "try{R.load(scratch, terms);console.log('SCRATCH_LOAD|NO_REFUSAL');}"
            "catch(e){console.log('SCRATCH_LOAD|'+e.code+'|'+e.message);}"
        )
        runtime = _run(['node', '-e', script])
        lines = [line for line in runtime['stdout'].splitlines() if line.strip()]
        unknown_line = next((line for line in lines if line.startswith('UNKNOWN_TYPE|')), '')
        scratch_line = next((line for line in lines if line.startswith('SCRATCH_LOAD|')), '')

        runtime_refused = 'E_INPUTS_UNKNOWN_TYPE' in unknown_line and 'Q99' in unknown_line
        load_refused = 'E_INPUTS_REGISTRY_INVALID' in scratch_line and 'Q99' in scratch_line
        gate_refused = report['status'] == 'FAIL' and bool(named)
        return {
            'status': 'PASS' if (gate_refused and runtime_refused and load_refused) else 'FAIL',
            'scratch_type_id': 'Q99',
            'gate_status': report['status'],
            'gate_refusal_named': named[:5],
            'runtime_status': runtime['status'],
            'runtime_refuses_instance_type': runtime_refused,
            'runtime_refuses_scratch_island': load_refused,
            'runtime_output': runtime['stdout'][:600],
            'runtime_stderr': runtime['stderr'][:400],
            'note_lv': (
                'Skrāpja tips Q99 tiek noraidīts ar vārdu gan instance ceļā '
                '(E_INPUTS_UNKNOWN_TYPE), gan salas ielādē (E_INPUTS_REGISTRY_INVALID); rezerves '
                'ievades lauks netiek renderēts.'
            ),
        }
    finally:
        shutil.rmtree(scratch_dir, ignore_errors=True)


def run_gate(repo_root: Path = ROOT, island_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    source = island_path or (repo_root / 'data/response_types.json')
    if not source.exists():
        return {'status': 'FAIL', 'owner': OWNER, 'errors': [f'{source} does not exist']}
    island = load_json(source)

    shape = check_island_shape(island, errors)
    if shape['missing_type_ids'] or shape['unknown_type_ids'] or not isinstance(island.get('types'), dict):
        # The remaining checks walk the eighteen entries; with a broken shape
        # they would only repeat the named defect.
        return {
            'status': 'FAIL',
            'owner': OWNER,
            'island': {
                'id': island.get('island_id'),
                'source': str(source.relative_to(repo_root)) if source.is_relative_to(repo_root) else str(source),
                'digest': sha256_bytes(canonical_json_bytes(island)),
                'bytes': len(canonical_json_bytes(island)),
            },
            'island_shape': shape,
            'errors': errors,
        }

    consistency = check_schema_consistency(island, errors)
    variants = check_payload_variants(island, errors)
    terms = check_terms(island, errors)
    error_ids = check_error_ids(island, errors)
    emits = check_completion_emits(island, errors)
    drift = check_compile_drift(errors)
    accounting = check_byte_accounting(island, errors)

    island_bytes = canonical_json_bytes(island)
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'owner': OWNER,
        'island': {
            'id': island.get('island_id'),
            'source': str(source.relative_to(repo_root)) if source.is_relative_to(repo_root) else str(source),
            'digest': sha256_bytes(island_bytes),
            'bytes': len(island_bytes),
        },
        'island_shape': shape,
        'schema_consistency': consistency,
        'payload_variants': variants,
        'terms': terms,
        'error_ids': error_ids,
        'completion_emits': emits,
        'compile_drift_check': drift,
        'byte_accounting': accounting,
        'notes_lv': [
            'Šī pārbaude nepalaiž tools/build.py: 18. vārtu savienošana ar būvi pieder koordinētājam.',
            'tools/check_n10_runtime.js lasa jau uzbūvēto artefaktu, tāpēc jaunās terminu atslēgas '
            'tajā parādās tikai pēc pārbūves; tā iepriekšējā SMK-N20 kļūda nav šīs izmaiņas sekas.',
        ],
        'errors': errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', help='write the machine-readable report to this path')
    parser.add_argument('--island', default=None, help='validate this island file instead of the repository one')
    parser.add_argument('--prove-scratch-refusal', action='store_true',
                        help='prove the gate and the runtime refuse an unknown type id Q99 by name')
    args = parser.parse_args(argv)

    island_path = Path(args.island) if args.island else None
    if args.prove_scratch_refusal:
        report = prove_scratch_refusal(ROOT, island_path)
    else:
        report = run_gate(ROOT, island_path)

    if args.report:
        path = Path(args.report)
        if not path.is_absolute():
            path = ROOT / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if report['status'] == 'PASS':
        if args.prove_scratch_refusal:
            print(
                'PASS n22 scratch refusal: unknown type Q99 refused by the gate, by '
                'E_INPUTS_UNKNOWN_TYPE and by E_INPUTS_REGISTRY_INVALID at island load'
            )
        else:
            island = report['island']
            shape = report['island_shape']
            print(
                f"PASS n22 response_types gate: {shape['type_count']} types, "
                f"completed {','.join(shape['completed_types'])}, island {island['bytes']} B, "
                f"terms {report['terms']['unique_keys']} keys, errors {len(report['error_ids']['frozen_ids'])} frozen ids"
            )
        return 0
    for error in report.get('errors', []):
        print(f'  - {error}', file=sys.stderr)
    if args.prove_scratch_refusal:
        print(f"  - gate refusal named: {report.get('gate_refusal_named')}", file=sys.stderr)
        print(f"  - runtime output: {report.get('runtime_output')!r}", file=sys.stderr)
        print(f"  - runtime stderr: {report.get('runtime_stderr')!r}", file=sys.stderr)
    print('FAIL n22 response_types gate', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
