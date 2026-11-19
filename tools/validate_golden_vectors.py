#!/usr/bin/env python3
"""N05 Golden Vectors, Seed Policy, and Growth Protocol Validator.

Validates:
  1. data/seed_policy.json (algorithm constants, non-crypto notice, seed ranges, JS BigInt rule).
  2. data/golden_vector_protocol.json (vector format, stratum registry, append-only retired-id rules).
  3. tools/prng.py against data/prng_contract_vectors.json (11 seeds x 100 u64 draws + illegal seeds).
  4. tools/golden_oracle.py AST import manifest (stdlib only; zero engine imports).
  5. data/golden_vectors.json:
     - root fields, conventions/schema/oracle digests match current files;
     - vector IDs match protocol regex, unique, and zero active vectors reuse retired_ids;
     - every vector's instance half passes tools/validate_bank.py (N04 schema);
     - replaying tools/golden_oracle.py produces identical expected verdicts for every active vector.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_oracle  # noqa: E402
import prng as py_prng  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_bank import SCHEMA_PATH, validate_bank  # noqa: E402

GOLDEN_VECTORS_PATH = 'data/golden_vectors.json'
PROTOCOL_PATH = 'data/golden_vector_protocol.json'
SEED_POLICY_PATH = 'data/seed_policy.json'
PRNG_CONTRACT_PATH = 'data/prng_contract_vectors.json'
CONVENTIONS_PATH = 'data/conventions.json'
ORACLE_PATH = 'tools/golden_oracle.py'


def validate_all(
    repo_root: Path = DEST,
    vectors_path: Path | None = None,
    conventions_path: Path | None = None,
    schema_path: Path | None = None,
    protocol_path: Path | None = None,
    seed_policy_path: Path | None = None,
    prng_contract_path: Path | None = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    errors: list[str] = []

    v_path = vectors_path or (repo_root / GOLDEN_VECTORS_PATH)
    c_path = conventions_path or (repo_root / CONVENTIONS_PATH)
    s_path = schema_path or (repo_root / SCHEMA_PATH)
    p_path = protocol_path or (repo_root / PROTOCOL_PATH)
    sp_path = seed_policy_path or (repo_root / SEED_POLICY_PATH)
    pc_path = prng_contract_path or (repo_root / PRNG_CONTRACT_PATH)

    for label, p in (
        ('golden_vectors', v_path),
        ('conventions', c_path),
        ('schema', s_path),
        ('protocol', p_path),
        ('seed_policy', sp_path),
        ('prng_contract', pc_path),
    ):
        if not p.exists():
            errors.append(f'Missing {label} file: {p}')

    if errors:
        return {'status': 'FAIL', 'errors': errors, 'counts': {}, 'duration_ms': round((time.perf_counter() - t0) * 1000.0, 3)}

    try:
        vectors_doc = load_json(v_path)
        conventions = load_json(c_path)
        schema = load_json(s_path)
        protocol = load_json(p_path)
        seed_policy = load_json(sp_path)
        prng_contract = load_json(pc_path)
    except Exception as exc:
        return {'status': 'FAIL', 'errors': [f'Malformed JSON: {exc}'], 'counts': {}, 'duration_ms': round((time.perf_counter() - t0) * 1000.0, 3)}

    # 1. Seed policy checks
    if 'NON-CRYPTOGRAPHIC' not in str(seed_policy.get('non_cryptographic_notice', '')):
        errors.append('seed_policy.json missing non_cryptographic_notice')
    for vocab_key in ('N24_assembly', 'N27_sample_selection', 'N30_workload_generation'):
        if vocab_key not in seed_policy.get('seed_vocabulary', {}):
            errors.append(f'seed_policy.json missing seed_vocabulary.{vocab_key}')

    # 2. Python PRNG check against frozen contract table
    for s_entry in prng_contract.get('streams', []):
        stream = py_prng.create_stream(int(s_entry['seed_dec']))
        draws = [str(stream.next_u64()) for _ in range(prng_contract['draws_per_seed'])]
        if draws != s_entry['draws']:
            errors.append(f'PRNG Python twin diverged from frozen contract on seed {s_entry["seed_dec"]}')
            break
    for bad in (0, -1, -42):
        try:
            py_prng.create_stream(bad)
            errors.append(f'PRNG accepted illegal seed {bad}')
        except py_prng.PrngError as exc:
            if exc.code != 'E_PRNG_INVALID_SEED':
                errors.append(f'PRNG illegal seed {bad} raised wrong code {exc.code}')

    # 3. Oracle import manifest independence check
    manifest = golden_oracle.verify_import_manifest(repo_root / ORACLE_PATH)
    if not manifest['independent_of_engines']:
        errors.append(f'Oracle imports disallowed modules: {manifest["disallowed_imports"]}')

    # 4. Root fields & digest parity
    for req_root in protocol['vector_format']['root_required']:
        if req_root not in vectors_doc:
            errors.append(f'golden_vectors.json missing root field {req_root}')
    if vectors_doc.get('island_id') != 'sim-golden-vectors':
        errors.append(f'island_id must be "sim-golden-vectors", got {vectors_doc.get("island_id")!r}')

    c_dig = sha256_bytes(canonical_json_bytes(conventions))
    s_dig = sha256_bytes(canonical_json_bytes(schema))
    o_dig = sha256_file(repo_root / ORACLE_PATH)
    if vectors_doc.get('conventions_digest') != c_dig:
        errors.append(f'conventions_digest mismatch: corpus {vectors_doc.get("conventions_digest")} != current {c_dig}')
    if vectors_doc.get('schema_digest') != s_dig:
        errors.append(f'schema_digest mismatch: corpus {vectors_doc.get("schema_digest")} != current {s_dig}')
    if vectors_doc.get('oracle', {}).get('oracle_digest') != o_dig:
        errors.append(f'oracle_digest mismatch: corpus {vectors_doc.get("oracle", {}).get("oracle_digest")} != current {o_dig}')

    # 5. Vector structure, retired IDs, and ID stability
    id_re = re.compile(protocol['vector_id_pattern'])
    retired_entries = vectors_doc.get('retired_ids', [])
    retired_set: set[str] = set()
    for r in retired_entries:
        if not isinstance(r, dict) or not all(k in r for k in ('retired_id', 'replaced_by', 'reason', 'ledger_ref')):
            errors.append(f'Malformed retired_ids entry: {r!r}')
        else:
            retired_set.add(r['retired_id'])

    seen_ids: set[str] = set()
    active_vectors: list[dict[str, Any]] = []
    for idx, vec in enumerate(vectors_doc.get('vectors', [])):
        if not isinstance(vec, dict):
            errors.append(f'Vector index {idx} is not an object')
            continue
        for req_k in protocol['vector_format']['vector_required']:
            if req_k not in vec:
                errors.append(f'Vector {vec.get("vector_id", idx)} missing field {req_k}')
        vid = vec.get('vector_id', '')
        if not id_re.match(vid):
            errors.append(f'Vector {vid!r} does not match protocol pattern {protocol["vector_id_pattern"]}')
        if vid in seen_ids:
            errors.append(f'Duplicate vector_id {vid!r}')
        seen_ids.add(vid)
        if vec.get('status') == 'active':
            if vid in retired_set:
                errors.append(f'Active vector {vid!r} reuses a retired_id')
            active_vectors.append(vec)

    # 6. Cross-check every vector's instance half through N04 validate_bank
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False, encoding='utf-8') as tf:
        json.dump({'questions': [v['instance'] for v in active_vectors]}, tf, ensure_ascii=False)
        tmp_bank_path = Path(tf.name)
    try:
        bank_rep = validate_bank(schema_path=s_path, repo_root=repo_root, bank_path=tmp_bank_path, require_all_required_types=False)
    finally:
        tmp_bank_path.unlink(missing_ok=True)
    if bank_rep['status'] != 'PASS':
        for viol in bank_rep.get('violations', [])[:10]:
            errors.append(f'N04 schema violation in {viol.get("question_id")} {viol.get("field")}: {viol.get("message")}')

    # 7. Oracle replay parity on every active vector
    oracle_report = golden_oracle.grade_corpus(vectors_doc, conventions)
    oracle_by_id = {r['vector_id']: r['verdict'] for r in oracle_report['results']}
    by_topic: dict[str, int] = {}
    by_type: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    by_error: dict[str, int] = {}

    for vec in active_vectors:
        vid = vec['vector_id']
        inst = vec['instance']
        exp = vec['expected']
        for req_e in protocol['vector_format']['expected_required']:
            if req_e not in exp:
                errors.append(f'Vector {vid} expected missing {req_e}')
        actual = oracle_by_id.get(vid)
        if actual != exp:
            errors.append(f'Oracle mismatch on {vid}: expected {exp} != oracle {actual}')

        t_key = str(inst['topic'])
        by_topic[t_key] = by_topic.get(t_key, 0) + 1
        by_type[inst['type_id']] = by_type.get(inst['type_id'], 0) + 1
        vc = exp.get('verdict_class', 'unknown')
        by_verdict[vc] = by_verdict.get(vc, 0) + 1
        ec = exp.get('error_class', 'unknown')
        by_error[ec] = by_error.get(ec, 0) + 1

    # Require all 7 topics represented in active vectors
    missing_topics = [str(t) for t in range(1, 8) if str(t) not in by_topic]
    if missing_topics:
        errors.append(f'Golden corpus missing topics: {missing_topics}')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'oracle_manifest': manifest,
        'oracle_results_sha256': oracle_report['results_sha256'],
        'corpus_sha256': sha256_bytes(canonical_json_bytes(vectors_doc)),
        'counts': {
            'active_vectors': len(active_vectors),
            'retired_ids': len(retired_set),
            'topics': len(by_topic),
            'types': len(by_type),
            'by_topic': dict(sorted(by_topic.items())),
            'by_type': dict(sorted(by_type.items())),
            'by_verdict': dict(sorted(by_verdict.items())),
            'by_error': dict(sorted(by_error.items())),
        },
        'bank_cross_check': {
            'status': bank_rep['status'],
            'instances': bank_rep['counts']['instances'],
            'violations': len(bank_rep['violations']),
        },
        'duration_ms': round((time.perf_counter() - t0) * 1000.0, 3),
    }


def format_summary(report: dict[str, Any]) -> str:
    cnt = report.get('counts', {})
    return (
        f'{report["status"]} golden-vectors: {cnt.get("active_vectors", 0)} active vectors, '
        f'{cnt.get("retired_ids", 0)} retired, {cnt.get("topics", 0)} topics, '
        f'{cnt.get("types", 0)} types, {len(report.get("errors", []))} errors '
        f'({report.get("duration_ms", 0)} ms)'
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vectors', default=str(DEST / GOLDEN_VECTORS_PATH))
    parser.add_argument('--conventions', default=str(DEST / CONVENTIONS_PATH))
    parser.add_argument('--schema', default=str(DEST / SCHEMA_PATH))
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--report', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    v_path = Path(args.vectors)
    if not v_path.is_absolute():
        v_path = repo_root / v_path
    c_path = Path(args.conventions)
    if not c_path.is_absolute():
        c_path = repo_root / c_path
    s_path = Path(args.schema)
    if not s_path.is_absolute():
        s_path = repo_root / s_path

    report = validate_all(repo_root=repo_root, vectors_path=v_path, conventions_path=c_path, schema_path=s_path)
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
        for err in report['errors'][:20]:
            print(f'  - {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
