#!/usr/bin/env python3
"""N08 validator: recall layers, bindings, citations, depth rule, leak scan and copy lint."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import COVERAGE_PATH, DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402
from leak_scan import (  # noqa: E402
    extract_family_answer_tokens,
    normalize_text as _normalize_text,
    scan_text_for_leaks as _unified_scan_text_for_leaks,
)
from validate_terms import TERMS_PATH  # noqa: E402

RECALL_LAYERS_PATH = 'data/recall_layers.json'
N08_TERM_STUBS_PATH = 'data/n08_term_stubs.json'
CONVENTIONS_PATH = 'data/conventions.json'
FAMILIES_SPEC_PATH = 'docs/QUESTION_FAMILIES.json'
GOLDEN_VECTORS_PATH = 'data/golden_vectors.json'
EXAMPLES_PATH = 'docs/EXAMPLE_QUESTIONS.json'

EXPECTED_LAYER_KINDS = [
    (1, 'cue'),
    (2, 'concept_link'),
    (3, 'rule_citation'),
    (4, 'first_step'),
]
ONE_STEP_FAMILIES_REQUIRING_DEPTH_RULE = {'FAM-1A', 'FAM-2A', 'FAM-2C', 'FAM-7A'}
FORBIDDEN_COPY_TOKENS = (
    'todo', 'tbd', 'fixme', 'lorem', 'ipsum', 'placeholder',
    'oficiāls eksāmens', 'garantēts eksāmens',
)


def scan_text_for_leaks(
    family_id: str,
    layer_num: int | str,
    text: str,
    answer_tokens: list[dict[str, Any]],
    surface: str = 'data',
    grammar: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Delegate N08 leak scanning to the unified N12 leak_scan engine."""
    return _unified_scan_text_for_leaks(
        family_id,
        layer_num,
        text,
        answer_tokens,
        surface=surface,
        grammar=grammar,
    )


def _check_balanced_brackets(text: str) -> bool:
    pairs = {'(': ')', '[': ']'}
    stack: list[str] = []
    for ch in text:
        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in (')', ']'):
            if not stack or stack.pop() != ch:
                return False
    return len(stack) == 0


def lint_copy(layers_data: dict[str, Any], stubs_data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    linted_count = 0

    for sem in layers_data.get('layer_semantics', []):
        for field in ('label_lv', 'purpose_lv'):
            val = str(sem.get(field, '')).strip()
            linted_count += 1
            if not val:
                errors.append(f"Empty layer_semantics.{field} on layer {sem.get('layer')}")
            elif not _check_balanced_brackets(val):
                errors.append(f"Unbalanced brackets in layer_semantics.{field} on layer {sem.get('layer')}")

    for fam in layers_data.get('families', []):
        fid = fam.get('family_id', '?')
        if fam.get('status') != 'authored':
            gap_reason = str(fam.get('gap_reason_lv', '')).strip()
            linted_count += 1
            if not gap_reason:
                errors.append(f"{fid}: gap-recorded family missing gap_reason_lv")
            continue
        for layer in fam.get('layers', []):
            txt = str(layer.get('text_lv', '')).strip()
            linted_count += 1
            if not txt:
                errors.append(f"{fid} L{layer.get('layer')}: empty text_lv")
                continue
            low = txt.lower()
            for bad in FORBIDDEN_COPY_TOKENS:
                if bad in low:
                    errors.append(f"{fid} L{layer.get('layer')}: forbidden token {bad!r}")
            if not _check_balanced_brackets(txt):
                errors.append(f"{fid} L{layer.get('layer')}: unbalanced brackets")

    for entry in stubs_data.get('keys', []):
        txt = str(entry.get('text_lv', '')).strip()
        linted_count += 1
        if not txt:
            errors.append(f"Stub {entry.get('key')}: empty text_lv")
        elif not _check_balanced_brackets(txt):
            errors.append(f"Stub {entry.get('key')}: unbalanced brackets")

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'linted_string_count': linted_count,
        'stub_dependency': 'N10 (data/n08_term_stubs.json -> stub-pending-N10)',
        'stub_key_count': len(stubs_data.get('keys', [])),
        'errors': errors,
    }


def build_runtime_projection(layers_data: dict[str, Any]) -> dict[str, Any]:
    """Build compact runtime projection of recall_layers for embedding in simulator.html."""
    return {
        'schema_version': layers_data['schema_version'],
        'island_id': layers_data['island_id'],
        'owner': layers_data['owner'],
        'status': layers_data['status'],
        'layer_semantics': layers_data['layer_semantics'],
        'contracts': layers_data['contracts'],
        'families': layers_data['families'],
    }


def validate_all(
    repo_root: Path = DEST,
    layers_path: Path | None = None,
    stubs_path: Path | None = None,
    coverage_path: Path | None = None,
    conventions_path: Path | None = None,
    golden_vectors_path: Path | None = None,
) -> dict[str, Any]:
    lp = layers_path or (repo_root / RECALL_LAYERS_PATH)
    sp = stubs_path or (repo_root / N08_TERM_STUBS_PATH)
    cp = coverage_path or (repo_root / COVERAGE_PATH)
    conv_p = conventions_path or (repo_root / CONVENTIONS_PATH)
    gvp = golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH)

    layers_data = load_json(lp)
    stubs_data = load_json(sp)
    coverage = load_json(cp)
    conventions = load_json(conv_p)
    golden_vectors = load_json(gvp)
    examples_data = load_json(repo_root / EXAMPLES_PATH)
    families_spec = load_json(repo_root / FAMILIES_SPEC_PATH)
    terms_path = repo_root / TERMS_PATH
    grammar = load_json(terms_path).get('unit_grammar') if terms_path.exists() else None

    errors: list[str] = []

    # 1. Layer semantics
    semantics = layers_data.get('layer_semantics', [])
    got_sem = [(s.get('layer'), s.get('kind')) for s in semantics]
    if got_sem != EXPECTED_LAYER_KINDS:
        errors.append(f"layer_semantics mismatch: expected {EXPECTED_LAYER_KINDS}, got {got_sem}")

    # 2. Build lookup sets from N02 and N03
    outcome_ids = {o['id'] for o in coverage.get('outcomes', [])}
    conv_cit_ids = {c['id'] for c in conventions.get('citation_index', [])}
    conv_conflict_ids = {c['id'] for c in conventions.get('conflicts', {}).get('entries', [])}
    valid_conv_ids = conv_cit_ids | conv_conflict_ids

    spec_families = {f['family_id']: f for f in families_spec.get('families', [])}
    families = layers_data.get('families', [])
    seen_fams: set[str] = set()

    topic_table: dict[int, dict[str, Any]] = {
        t: {'topic': t, 'authored': [], 'gaps': [], 'depth_rule_families': []}
        for t in range(1, 8)
    }

    answer_tokens_by_family = extract_family_answer_tokens(golden_vectors, examples_data)
    leak_findings: list[dict[str, Any]] = []

    for fam in families:
        fid = fam.get('family_id')
        if not fid or fid in seen_fams:
            errors.append(f"Duplicate or missing family_id: {fid}")
            continue
        seen_fams.add(fid)
        if fid not in spec_families:
            errors.append(f"Unknown family_id {fid} not in QUESTION_FAMILIES.json")
            continue
        topic = fam.get('topic')
        if topic != spec_families[fid]['topic']:
            errors.append(f"{fid}: topic {topic} != spec {spec_families[fid]['topic']}")

        for cid in fam.get('concept_ids', []):
            if cid not in outcome_ids:
                errors.append(f"{fid}: unknown concept_id {cid!r}")

        status = fam.get('status')
        if status == 'gap-recorded':
            if fam.get('layers'):
                errors.append(f"{fid}: gap-recorded family must have empty layers")
            if topic in topic_table:
                topic_table[topic]['gaps'].append(fid)
            continue
        if status != 'authored':
            errors.append(f"{fid}: invalid status {status!r}")
            continue

        if topic in topic_table:
            topic_table[topic]['authored'].append(fid)

        pcid = fam.get('primary_concept_id')
        if pcid not in outcome_ids:
            errors.append(f"{fid}: primary_concept_id {pcid!r} not in coverage.json")

        # Depth rule check
        max_depths = fam.get('max_depth_by_variant_class', {})
        if max_depths.get('default') != 4:
            errors.append(f"{fid}: max_depth_by_variant_class.default must be 4")
        if fid in ONE_STEP_FAMILIES_REQUIRING_DEPTH_RULE:
            if not fam.get('depth_rule_applied') or max_depths.get('one_step', 4) > 3:
                errors.append(f"{fid}: depth rule violation — one_step variant requires max_depth <= 3 and depth_rule_applied=true")
        if fam.get('depth_rule_applied') and topic in topic_table:
            topic_table[topic]['depth_rule_families'].append(fid)

        # Layers check
        layers = fam.get('layers', [])
        got_kinds = [(l.get('layer'), l.get('kind')) for l in layers]
        if got_kinds != EXPECTED_LAYER_KINDS:
            errors.append(f"{fid}: layers must match {EXPECTED_LAYER_KINDS}, got {got_kinds}")

        fam_tokens = answer_tokens_by_family.get(fid, [])
        for layer in layers:
            lnum = layer.get('layer')
            cit = layer.get('citation')
            if not isinstance(cit, dict) or cit.get('kind') not in ('concept', 'convention'):
                errors.append(f"{fid} L{lnum}: invalid citation {cit!r}")
            else:
                ckind = cit['kind']
                cid = cit.get('id')
                if ckind == 'concept' and cid not in outcome_ids:
                    errors.append(f"{fid} L{lnum}: unresolved concept citation {cid!r}")
                elif ckind == 'convention' and cid not in valid_conv_ids:
                    errors.append(f"{fid} L{lnum}: unresolved convention citation {cid!r}")

            if layer.get('kind') == 'concept_link':
                lcid = layer.get('concept_id')
                if lcid not in outcome_ids:
                    errors.append(f"{fid} L{lnum}: unresolved concept_link concept_id {lcid!r}")

            leak_findings.extend(
                scan_text_for_leaks(fid, lnum, layer.get('text_lv', ''), fam_tokens, surface='data', grammar=grammar)
            )

    missing_fams = sorted(set(spec_families.keys()) - seen_fams)
    if missing_fams:
        errors.append(f"Missing families from recall_layers.json: {missing_fams}")

    if leak_findings:
        for lf in leak_findings:
            errors.append(f"{lf['error_id']}: {lf['family_id']} L{lf['layer']} leaked {lf['leaked_raw']!r} ({lf['source']})")

    copy_lint = lint_copy(layers_data, stubs_data)
    if copy_lint['status'] != 'PASS':
        errors.extend(copy_lint['errors'])

    authored_count = sum(len(v['authored']) for v in topic_table.values())
    gap_count = sum(len(v['gaps']) for v in topic_table.values())
    canonical_digest = sha256_bytes(canonical_json_bytes(layers_data))

    return {
        'schema_version': 1,
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'canonical_sha256': canonical_digest,
        'summary': {
            'total_families': len(families),
            'authored_families': authored_count,
            'gap_families': gap_count,
            'depth_rule_families': sorted(
                f['family_id'] for f in families if f.get('depth_rule_applied')
            ),
            'leak_findings_count': len(leak_findings),
            'copy_lint': copy_lint,
        },
        'topic_coverage_table': [topic_table[t] for t in range(1, 8)],
        'leak_findings': leak_findings,
    }


def format_summary(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        f"recall_layers: {report['status']} | authored={s['authored_families']}/{s['total_families']} "
        f"gaps={s['gap_families']} leaks={s['leak_findings_count']} lint={s['copy_lint']['linted_string_count']} strings",
    ]
    if report['errors']:
        for err in report['errors'][:10]:
            lines.append(f"  ERROR: {err}")
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate N08 recall layers.')
    parser.add_argument('--json', action='store_true', help='Print full JSON report.')
    parser.add_argument('--report', type=Path, help='Write JSON report to path.')
    args = parser.parse_args(argv)

    report = validate_all()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_summary(report))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
