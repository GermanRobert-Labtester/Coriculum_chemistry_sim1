#!/usr/bin/env python3
"""N19 corpus: the method cards, the three verdict engines and their evidence.

Runs the build gate (tools/validate_method_cards.py), runs the runtime harness
(tools/check_n19_runtime.js) against the shipped artifact, compares the Python
twin and the JavaScript twin verdict record by verdict record, measures the
declared sub-budgets and writes evidence/N19_CORPUS_RECORD.json.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
import method_engine as me  # noqa: E402
from validate_method_cards import (  # noqa: E402
    CARDS_PATH, CONTRACT_PATH, build_runtime_projection,
    validate as validate_method_cards,
)

ROOT = DEST
HARNESS = ROOT / 'tools/check_n19_runtime.js'
OUT_DEFAULT = ROOT / 'evidence/N19_CORPUS_RECORD.json'
CARDS = ROOT / CARDS_PATH
CONTRACT = ROOT / CONTRACT_PATH


def canonical(value: Any) -> str:
    """The cross-language canonical form: sorted keys, fixed decimals."""
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return '%.*f' % (me.CANONICAL_DECIMALS, float(value))
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (list, tuple)):
        return '[' + ','.join(canonical(item) for item in value) + ']'
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(str(k), ensure_ascii=False) + ':' + canonical(value[k])
                              for k in sorted(value)) + '}'
    return 'null'


def run_harness() -> dict[str, Any]:
    proc = subprocess.run(['node', str(HARNESS)], cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f'FAIL n19-runtime-harness: {proc.stderr.strip()[:2000]}')
    return json.loads(proc.stdout)


def python_records(engine: me.MethodEngine, cards_by_id: dict[str, dict[str, Any]],
                   vectors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    for vector in vectors:
        spec = me.spec_for_vector(engine, cards_by_id, vector)
        records.append({'id': vector['id'], 'record': engine.grade(spec, vector['submission'])})
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    report = validate_method_cards(repo_root=ROOT)
    contract = load_json(CONTRACT)
    cards_doc = load_json(CARDS)
    terms = load_json(ROOT / 'data/terms.json')
    engine = me.MethodEngine(contract, terms)
    cards_by_id = {c['card_id']: c for c in cards_doc['cards']}

    vectors = contract['method_vectors']
    all_vectors: list[dict[str, Any]] = []
    for key in ('ordering_vectors', 'matching_vectors', 'sequence_vectors', 'self_assessment_vectors'):
        all_vectors.extend(vectors.get(key, []))
    all_vectors.append(vectors.get('scratch', {}).get('ordering'))

    py = python_records(engine, cards_by_id, [v for v in all_vectors if v])

    runtime = run_harness()
    js_by_id = {row['id']: row['record'] for row in runtime['verdict_records']}

    compared = []
    mismatches = []
    for row in py:
        js_record = js_by_id.get(row['id'])
        if js_record is None:
            mismatches.append({'id': row['id'], 'reason': 'missing in the JavaScript twin'})
            continue
        same = canonical(row['record']) == canonical(js_record)
        compared.append({
            'id': row['id'],
            'verdict_class': row['record']['verdict_class'],
            'error_class': row['record']['error_class'],
            'python_digest': sha256_bytes(canonical(row['record']).encode('utf-8')),
            'javascript_digest': sha256_bytes(canonical(js_record).encode('utf-8')),
            'status': 'EQUAL' if same else 'DIFFERENT',
        })
        if not same:
            mismatches.append({'id': row['id'], 'reason': 'verdict records differ'})

    # -- the determinism proof, in the Python twin ------------------------------
    determinism_rows = []
    for vector in [v for v in all_vectors if v]:
        spec = me.spec_for_vector(engine, cards_by_id, vector)
        first = canonical(engine.grade(spec, vector['submission']))
        second = canonical(engine.grade(spec, vector['submission']))
        determinism_rows.append({
            'id': vector['id'],
            'digest': sha256_bytes(first.encode('utf-8')),
            'status': 'PASS' if first == second else 'FAIL',
        })

    # -- the budget measurement -------------------------------------------------
    # The cards budget measures the shipped island (the sealed runtime
    # projection), not the source file: the projection carries the sealed
    # diagnostics and is what the artifact actually pays for.
    runtime_projection = build_runtime_projection(cards_doc)
    budget = {
        'method_cards_island_bytes': {
            'measured': len(canonical_json_bytes(runtime_projection)),
            'measured_basis': 'shipped #sim-method-cards island (sealed runtime projection)',
            'source_bytes': len(canonical_json_bytes(cards_doc)),
            'ceiling': contract['budgets']['method_cards_island_bytes']['ceiling'],
        },
        'method_engine_contract_bytes': {
            'measured': len(canonical_json_bytes(contract)),
            'ceiling': contract['budgets']['method_engine_contract_bytes']['ceiling'],
        },
        'method_engine_js_bytes': {
            'measured': (ROOT / 'src/method-engine.js').stat().st_size,
            'ceiling': contract['budgets']['method_engine_js_bytes']['ceiling'],
        },
        'method_card_view_js_bytes': {
            'measured': (ROOT / 'src/method-card-view.js').stat().st_size,
            'ceiling': contract['budgets'].get('method_card_view_js_bytes', {}).get('ceiling', 65536),
        },
    }
    for name, entry in budget.items():
        entry['headroom_bytes'] = entry['ceiling'] - entry['measured']
        entry['status'] = 'PASS' if entry['measured'] <= entry['ceiling'] else 'FAIL'

    # -- the second run of the harness (parity) --------------------------------
    runtime_second = run_harness()
    harness_parity = runtime['digests'] == runtime_second['digests']

    status = 'PASS' if (report['status'] == 'PASS' and not mismatches and harness_parity
                        and all(r['status'] == 'PASS' for r in determinism_rows)
                        and all(e['status'] == 'PASS' for e in budget.values())) else 'FAIL'

    record = {
        'schema_version': 1,
        'task': 'N19',
        'status': status,
        'artifact': 'method cards and the ordering, matching and sequence verdict engines',
        'validation': {
            'status': report['status'],
            'summary': report['summary'],
            'digests': report['digests'],
            'errors': report['errors'],
        },
        'cards': {
            'rows': report['card_rows'],
            'coverage_rows': report['coverage_rows'],
            'reference_rows': report['reference_rows'],
            'copy_lint': report['copy_lint'],
            'signature_rows': report['signature_rows'],
        },
        'vectors': {
            'n05_rows': report['n05_rows'],
            'stratum_rows': report['stratum_rows'],
            'determinism_rows': determinism_rows,
        },
        'no_keyword': {
            'source_findings': report['source_findings'],
            'behaviour_rows': report['no_keyword_behaviour'],
            'rule_verbatim': contract['no_keyword_rule_verbatim_lv'],
            'identity_rule_verbatim': contract['identity_rule_verbatim_lv'],
        },
        'feedback_trace': runtime['feedback_trace'],
        'pending_boundary': runtime['boundary'],
        'pending_semantics': contract['pending_semantics'],
        'focus_traces': runtime['focus_traces'],
        'cross_language': {
            'status': 'PASS' if not mismatches else 'FAIL',
            'tables': compared,
            'mismatches': mismatches,
        },
        'budget': budget,
        'runtime': {
            'status': runtime['status'],
            'parity': runtime['parity'],
            'harness_parity': harness_parity,
            'counts': runtime['counts'],
            'digests': runtime['digests'],
            'artifact_sha256': runtime['artifact_sha256'],
            'runtime_js_note': runtime['runtime_js_note'],
            'signature_mapping_rows': runtime['rows']['mapping'],
        },
        'smoke': runtime['smoke_summary'],
        'handoff': contract['handoff_contract'],
        'sources': {
            'cards': sha256_file(CARDS),
            'contract': sha256_file(CONTRACT),
            'python_engine': sha256_file(ROOT / 'tools/method_engine.py'),
            'javascript_engine': sha256_file(ROOT / 'src/method-engine.js'),
            'card_view': sha256_file(ROOT / 'src/method-card-view.js'),
            'validator': sha256_file(ROOT / 'tools/validate_method_cards.py'),
            'harness': sha256_file(HARNESS),
        },
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': status, 'out': str(out), 'bytes': out.stat().st_size,
        'sha256': sha256_file(out),
        'cards': report['summary']['cards'],
        'n05': f"{report['summary']['n05_pass']}/{report['summary']['n05_vectors']}",
        'stratum': f"{report['summary']['stratum_pass']}/{report['summary']['stratum_vectors']}",
        'cross_language': record['cross_language']['status'],
        'harness_parity': harness_parity,
        'dangling_signatures': report['summary']['dangling_signatures'],
    }, ensure_ascii=False, indent=2))
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
