#!/usr/bin/env python3
"""N17 engine build gate.

Validates the frozen engine taxonomy, the no-local-constants assertion, the
conventions consumption proof, the four-class signature/feedback alignment,
the V-04 corpus, the conservation and classification vectors and the
verdict-for-verdict replay of every active N05 golden vector by the Python twin.

The JavaScript twin's parity is proven after assembly by tools/check_n17_runtime.js
and recorded in evidence/N17_CORPUS_RECORD.json by tools/n17_corpus.py.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file,
)
import quantity_engine as qe  # noqa: E402
from validate_golden_vectors import GOLDEN_VECTORS_PATH, PROTOCOL_PATH  # noqa: E402

TAXONOMY_PATH = qe.TAXONOMY_PATH
CONVENTIONS_PATH = qe.CONVENTIONS_PATH
TERMS_PATH = qe.TERMS_PATH
PYTHON_ENGINE = 'tools/quantity_engine.py'
JS_ENGINE = 'src/quantity-engine.js'
SIGNATURE_RE = re.compile(r'^MC-[1-7][A-D]-[0-9]{2}$')
NO_BLAME_RE = re.compile(r'\b(?:tu\s+esi|tu\s+ne|nepareizais|sliktais|muļķis)\b', re.IGNORECASE)


def _active_vectors(doc: dict[str, Any]) -> list[dict[str, Any]]:
    return [v for v in doc.get('vectors', []) if v.get('status') != 'retired']


def validate(repo_root: Path = DEST, taxonomy_path: Path | None = None,
             golden_path: Path | None = None, protocol_path: Path | None = None,
             conventions_path: Path | None = None, terms_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    tax_path = taxonomy_path or (repo_root / TAXONOMY_PATH)
    golden_path = golden_path or (repo_root / GOLDEN_VECTORS_PATH)
    protocol_path = protocol_path or (repo_root / PROTOCOL_PATH)

    for required in (tax_path, golden_path, protocol_path, repo_root / PYTHON_ENGINE, repo_root / JS_ENGINE):
        if not required.exists():
            errors.append(f'Missing engine artifact: {required}')
    if errors:
        return {'status': 'FAIL', 'errors': errors}

    taxonomy = load_json(tax_path)
    golden = load_json(golden_path)
    protocol = load_json(protocol_path)
    conventions = load_json(conventions_path or (repo_root / CONVENTIONS_PATH))
    terms = load_json(terms_path or (repo_root / TERMS_PATH))
    term_keys = {t['key']: t for t in terms.get('terms', [])}

    if taxonomy.get('island_id') != 'sim-engines':
        errors.append('taxonomy island_id must be sim-engines')
    if taxonomy.get('owner') != 'N17':
        errors.append('taxonomy owner must be N17')

    # -- class vocabulary, signature alignment and term resolution ----------
    classes = taxonomy.get('error_taxonomy', {}).get('classes', [])
    if len(classes) != 4:
        errors.append(f'expected four error classes, found {len(classes)}')
    if sorted(int(c.get('rank', 0)) for c in classes) != [1, 2, 3, 4]:
        errors.append('error class ranks must be exactly 1,2,3,4')
    used_signatures = set()
    golden_signatures = set()
    for vec in _active_vectors(golden):
        golden_signatures.update(vec['instance'].get('misconception_signatures', []))
    allowed_n05 = set(protocol['error_classes'])
    citation_ids = {c['id'] for c in conventions.get('citation_index', [])}
    citation_ids |= {c['id'] for c in conventions.get('conflicts', {}).get('entries', [])}
    citation_rows = []
    for entry in classes:
        cid = entry.get('id', '<unknown>')
        signature = entry.get('signature', '')
        key = entry.get('feedback_key', '')
        if not SIGNATURE_RE.match(signature):
            errors.append(f'{cid}: signature {signature!r} violates N04 stub pattern')
        if signature not in golden_signatures:
            errors.append(f'{cid}: signature {signature!r} not present in the frozen N05 corpus')
        if signature in used_signatures:
            errors.append(f'{cid}: duplicate signature {signature!r}')
        used_signatures.add(signature)
        if key not in term_keys:
            errors.append(f'{cid}: feedback key {key!r} does not resolve in #sim-terms')
        else:
            text = term_keys[key].get('text_lv', '')
            if not text.strip():
                errors.append(f'{cid}: empty feedback text')
            if NO_BLAME_RE.search(text):
                errors.append(f'{cid}: feedback text blames the learner')
        for n05 in entry.get('n05_error_classes', []):
            if n05 not in allowed_n05:
                errors.append(f'{cid}: N05 class {n05!r} not in the frozen protocol')
        cref = entry.get('conventions_ref')
        if cref not in citation_ids:
            errors.append(f'{cid}: conventions_ref {cref!r} does not resolve')
        citation_rows.append({'id': cid, 'signature': signature, 'feedback_key': key,
                              'conventions_ref': cref, 'text_lv': term_keys.get(key, {}).get('text_lv', '')})
    fallback = taxonomy.get('error_taxonomy', {}).get('fallback', {})
    if fallback.get('feedback_key') not in term_keys:
        errors.append('fallback feedback key does not resolve in #sim-terms')
    if fallback.get('signature') not in golden_signatures:
        errors.append('fallback signature not present in the frozen N05 corpus')
    for key in ('precedence_rule_verbatim', 'boundary_rule_verbatim'):
        if not taxonomy.get('error_taxonomy', {}).get(key):
            errors.append(f'missing {key}')
    for rule in taxonomy.get('plausibility_rules', []):
        if rule.get('conventions_ref') not in citation_ids:
            errors.append(f"plausibility rule {rule['id']}: bad conventions_ref")
    for rule in taxonomy.get('domain_rules', []):
        if rule.get('conventions_ref') not in citation_ids:
            errors.append(f"domain rule {rule['id']}: bad conventions_ref")
        source = repo_root / rule.get('source_contract', '')
        if not source.exists():
            errors.append(f"domain rule {rule['id']}: source contract missing")

    # -- conventions consumption and the mechanical no-drift assertion -------
    try:
        engine = qe.Engine(conventions, taxonomy, terms)
    except qe.EngineError as exc:
        errors.append(f'engine could not consume conventions: {exc}')
        engine = None
    py_source = (repo_root / PYTHON_ENGINE).read_text(encoding='utf-8')
    js_source = (repo_root / JS_ENGINE).read_text(encoding='utf-8')
    no_local = engine.no_local_constants({'python': py_source, 'js': js_source}) if engine else {
        'status': 'FAIL', 'findings': [{'source': 'engine', 'literal': '?', 'conventions_value': '?'}]}
    if no_local['status'] != 'PASS':
        errors.append(f"no-local-constants assertion failed: {no_local['findings'][:3]}")
    ast_numbers = qe.no_local_constants_ast(py_source)
    if not ast_numbers:
        errors.append('Python AST scan found no numeric literals (scan is not exercising the source)')

    # -- Python engine vs the frozen N05 corpus --------------------------------
    vector_rows: list[dict[str, Any]] = []
    vector_failures: list[str] = []
    if engine:
        for vec in _active_vectors(golden):
            exp = vec['expected']
            got = engine.grade(vec['instance'], vec['submission'], exp['oracle_version'],
                               exp['oracle_digest'], golden['conventions_digest'])
            view = engine.oracle_view(got)
            ok = view == exp
            if not ok:
                vector_failures.append(vec['vector_id'])
            vector_rows.append({
                'vector_id': vec['vector_id'], 'topic': vec['instance']['topic'],
                'payload_class': vec['instance']['payload_class'], 'expected_error': exp['error_class'],
                'engine_error': got['error_class'], 'verdict': got['verdict_class'],
                'taxonomy_class': got['taxonomy_class'], 'signature': got['signature'],
                'status': 'PASS' if ok else 'FAIL',
            })

    # -- N17 stratum vectors ---------------------------------------------------
    ev = taxonomy.get('engine_vectors', {})
    stratum_rows: list[dict[str, Any]] = []
    if engine:
        for form in ev.get('v04_forms', []):
            got = engine.classify({'raw': '1,0', 'unit': form['unit'], 'expected_unit': form['expected_unit']})
            ok = got['taxonomy_class'] == form['expected_class']
            if not ok:
                errors.append(f"V-04 form {form['id']}: expected {form['expected_class']}, got {got['taxonomy_class']}")
            stratum_rows.append({'id': form['id'], 'kind': 'v04', 'expected': form['expected_class'],
                                 'actual': got['taxonomy_class'], 'status': 'PASS' if ok else 'FAIL'})
        for vec in ev.get('conservation_vectors', []):
            got = engine.check_conservation(vec)
            ok = got['verdict'] == vec['expected_verdict']
            if not ok:
                errors.append(f"conservation vector {vec['id']}: {got['verdict']}")
            stratum_rows.append({'id': vec['id'], 'kind': 'conservation', 'expected': vec['expected_verdict'],
                                 'actual': got['verdict'], 'status': 'PASS' if ok else 'FAIL'})
        for vec in ev.get('classification_vectors', []):
            got = engine.classify(vec)
            ok = (got['taxonomy_class'] == vec['expected_class'] and
                  got['signature'] == vec['expected_signature'])
            if not ok:
                errors.append(f"classification vector {vec['id']}: {got['taxonomy_class']}/{got['signature']}")
            stratum_rows.append({'id': vec['id'], 'kind': 'classification',
                                 'expected': vec['expected_class'] + '/' + vec['expected_signature'],
                                 'actual': got['taxonomy_class'] + '/' + got['signature'],
                                 'status': 'PASS' if ok else 'FAIL'})
        scratch = ev.get('scratch', {}).get('conservation')
        if scratch:
            got = engine.check_conservation(scratch)
            if got['verdict'] != scratch['expected_verdict']:
                errors.append(f"scratch conservation vector {scratch['id']} did not fail by id")
        else:
            errors.append('missing scratch conservation vector')

    digests = {
        'taxonomy': sha256_bytes(canonical_json_bytes(taxonomy)),
        'conventions': sha256_bytes(canonical_json_bytes(conventions)),
        'python_engine': sha256_file(repo_root / PYTHON_ENGINE),
        'js_engine': sha256_file(repo_root / JS_ENGINE),
        'golden_corpus': sha256_bytes(canonical_json_bytes(golden)),
    }
    return {
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'task': 'N17',
        'summary': {
            'classes': len(classes), 'golden_vectors': len(vector_rows),
            'golden_pass': sum(1 for r in vector_rows if r['status'] == 'PASS'),
            'golden_fail': len(vector_failures),
            'stratum_vectors': len(stratum_rows),
            'stratum_pass': sum(1 for r in stratum_rows if r['status'] == 'PASS'),
            'no_local_constants': no_local['status'],
        },
        'vector_rows': vector_rows,
        'vector_failures': vector_failures,
        'stratum_rows': stratum_rows,
        'citation_rows': citation_rows,
        'no_local_constants': no_local,
        'conventions_paths': taxonomy['conventions_consumption']['paths'],
        'digests': digests,
    }


def format_summary(report: dict[str, Any]) -> str:
    s = report.get('summary', {})
    return (f"{report['status']} engines: {s.get('golden_pass', 0)}/{s.get('golden_vectors', 0)} N05 vectors, "
            f"{s.get('stratum_pass', 0)}/{s.get('stratum_vectors', 0)} N17 vectors, "
            f"{s.get('classes', 0)} error classes, no-local-constants {s.get('no_local_constants')}, "
            f"{len(report.get('errors', []))} errors")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--report', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    root = Path(args.repo_root)
    report = validate(repo_root=root)
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(__import__('json').dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
    print(json_dumps(report) if args.json else format_summary(report))
    if report['status'] != 'PASS':
        for err in report['errors'][:20]:
            print(f'  - {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


def json_dumps(value: Any) -> str:
    import json
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == '__main__':
    raise SystemExit(main())
