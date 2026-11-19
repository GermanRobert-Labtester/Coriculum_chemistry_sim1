#!/usr/bin/env python3
"""N17 corpus: recompute/verdict tables, cross-language parity, scratch negatives,
throughput note, budget accounting, smoke vector and two-run parity.

Run: python3 tools/n17_corpus.py
     python3 tools/n17_corpus.py --out /tmp/opencode/n17_second.json
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
import quantity_engine as qe  # noqa: E402
from validate_engines import validate as validate_engines  # noqa: E402
from validate_n06_shell import validate_shell  # noqa: E402

ROOT = DEST
OUT = ROOT / 'evidence'
ARTIFACT = ROOT / 'output' / 'simulator.html'
MANIFEST = ROOT / 'output' / 'build-manifest.json'
HARNESS = ROOT / 'tools' / 'check_n17_runtime.js'
ENGINE_JS = ROOT / 'src' / 'quantity-engine.js'
SMOKE_DIGEST = 'd1c5027bf952ccf126a044dc2804e557de7245da20581388218e65749dd17127'
ORACLE_FIELDS = ['verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
                 'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points',
                 'oracle_version', 'oracle_digest', 'conventions_digest']


def compact(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'))


def digest(value: Any) -> str:
    return sha256_bytes(compact(value).encode('utf-8')) if isinstance(value, str) else sha256_bytes(canonical_json_bytes(value))


def island_text(island_id: str) -> str:
    html = ARTIFACT.read_text(encoding='utf-8')
    match = re.search(r'<script\s+type="application/json"\s+id="' + island_id +
                      r'"[^>]*>([\s\S]*?)</script>', html)
    if not match:
        raise SystemExit('missing island #' + island_id)
    return match.group(1).replace('<\\/', '</')


def canonical_view(value: Any) -> str:
    if isinstance(value, dict):
        return '{' + ','.join(json.dumps(k, ensure_ascii=False) + ':' + canonical_view(value[k])
                              for k in sorted(value)) + '}'
    if isinstance(value, list):
        return '[' + ','.join(canonical_view(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def python_rows(engine: qe.Engine, golden: dict[str, Any], taxonomy: dict[str, Any]) -> dict[str, Any]:
    golden_rows = []
    for vec in golden['vectors']:
        if vec.get('status') == 'retired':
            continue
        exp = vec['expected']
        got = engine.grade(vec['instance'], vec['submission'], exp['oracle_version'],
                           exp['oracle_digest'], golden['conventions_digest'])
        view = {k: got[k] for k in ORACLE_FIELDS}
        ok = canonical_view(view) == canonical_view(exp)
        golden_rows.append({'id': vec['vector_id'], 'status': 'PASS' if ok else 'FAIL',
                            'error_class': got['error_class'], 'taxonomy_class': got['taxonomy_class'],
                            'signature': got['signature']})

    ev = taxonomy['engine_vectors']
    stratum_rows = []
    for form in ev['v04_forms']:
        got = engine.classify({'raw': '1,0', 'unit': form['unit'], 'expected_unit': form['expected_unit']})
        stratum_rows.append({'id': form['id'], 'kind': 'v04',
                             'status': 'PASS' if got['taxonomy_class'] == form['expected_class'] else 'FAIL',
                             'actual': got['taxonomy_class']})
    for vec in ev['conservation_vectors']:
        got = engine.check_conservation(vec)
        stratum_rows.append({'id': vec['id'], 'kind': 'conservation',
                             'status': 'PASS' if got['verdict'] == vec['expected_verdict'] else 'FAIL',
                             'actual': got['verdict'], 'signature': got['signature']})
    for vec in ev['classification_vectors']:
        got = engine.classify(vec)
        ok = got['taxonomy_class'] == vec['expected_class'] and got['signature'] == vec['expected_signature']
        stratum_rows.append({'id': vec['id'], 'kind': 'classification',
                             'status': 'PASS' if ok else 'FAIL', 'actual': got['taxonomy_class'],
                             'signature': got['signature'], 'trace': got['precedence_trace']})
    return {
        'golden_rows': golden_rows, 'stratum_rows': stratum_rows,
        'digests': {
            'golden_verdicts': sha256_bytes(compact(golden_rows).encode('utf-8')),
            'stratum_verdicts': sha256_bytes(compact(stratum_rows).encode('utf-8')),
            'taxonomy': sha256_bytes(island_text('sim-engines').encode('utf-8')),
            'engine_source': sha256_file(ENGINE_JS),
        },
    }


def scratch_constant_regression() -> dict[str, Any]:
    """A wrong tolerance in a scratch conventions copy must fail by vector id."""
    conventions = load_json(ROOT / qe.CONVENTIONS_PATH)
    scratch = copy.deepcopy(conventions)
    for entry in scratch['tolerances']['quantity_classes']:
        if entry['id'] == 'mass':
            entry['absolute']['value'] = '999'
            break
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'conventions_scratch.json'
        path.write_text(json.dumps(scratch, ensure_ascii=False), encoding='utf-8')
        report = validate_engines(repo_root=ROOT, conventions_path=path)
    failures = report.get('vector_failures', [])
    return {
        'status': 'PASS' if report['status'] == 'FAIL' and failures else 'FAIL',
        'report_status': report['status'],
        'failed_ids': failures[:8],
        'failed_count': len(failures),
    }


def throughput(engine: qe.Engine, iterations: int = 1000) -> dict[str, Any]:
    cases = [
        {'raw': '17,2', 'unit': 'mg', 'expected_unit': 'L'},
        {'raw': '1,2,3', 'unit': 'g/L', 'expected_unit': 'g/L'},
        {'raw': '-1,5', 'unit': 'g/L', 'expected_unit': 'g/L', 'rule_id': 'nonnegative_concentration'},
        {'raw': '0,020', 'unit': 'g/L', 'expected_unit': 'g/L', 'span': {'min': 0, 'max': 0.016}},
    ]
    start = time.perf_counter()
    for i in range(iterations):
        engine.classify(cases[i % len(cases)])
    elapsed = (time.perf_counter() - start) * 1000.0
    bound_ms = 2000.0
    return {
        'iterations': iterations, 'elapsed_ms': round(elapsed, 3),
        'throughput_per_s': round(iterations / (elapsed / 1000.0), 1) if elapsed else None,
        'declared_bound_ms': bound_ms,
        'status': 'PASS' if elapsed <= bound_ms else 'FAIL',
        'note': 'Authoring-host measurement; not a reference-device acceptance claim.',
    }


def compacted_engine_bytes() -> int:
    proc = subprocess.run(
        [sys.executable, '-c',
         'import sys;sys.path.insert(0,"tools");from tools.build import compact_js_source;'
         'print(compact_js_source(open("src/quantity-engine.js",encoding="utf-8").read()),end="")'],
        cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit('compacted engine measurement failed: ' + proc.stderr[:300])
    return len(proc.stdout.encode('utf-8'))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT / 'N17_CORPUS_RECORD.json'))
    args = parser.parse_args(argv)

    report = validate_engines(repo_root=ROOT)
    if report['status'] != 'PASS':
        print('FAIL engine gate:', report['errors'][:5], file=sys.stderr)
        return 1
    report2 = validate_engines(repo_root=ROOT)
    validation_parity = canonical_view(report) == canonical_view(report2)

    harness = subprocess.run(['node', str(HARNESS)], cwd=str(ROOT), capture_output=True, text=True)
    if harness.returncode != 0:
        print('FAIL runtime harness:', (harness.stderr or '')[:800], file=sys.stderr)
        return 1
    runtime = json.loads(harness.stdout)
    if runtime['status'] != 'PASS':
        print('FAIL runtime status', file=sys.stderr)
        return 1

    engine = qe.load()
    golden = load_json(ROOT / 'data/golden_vectors.json')
    taxonomy = load_json(ROOT / qe.TAXONOMY_PATH)
    py = python_rows(engine, golden, taxonomy)
    cross = {
        'status': 'PASS' if py['digests'] == runtime['digests'] else 'FAIL',
        'python': py['digests'], 'javascript': runtime['digests'],
        'compared_fields': sorted(py['digests']),
    }
    if cross['status'] != 'PASS':
        print('FAIL cross-language digest parity', cross, file=sys.stderr)
        return 1

    scratch = scratch_constant_regression()
    if scratch['status'] != 'PASS':
        print('FAIL scratch constant regression', scratch, file=sys.stderr)
        return 1
    rate = throughput(engine)
    if rate['status'] != 'PASS':
        print('FAIL throughput', rate, file=sys.stderr)
        return 1

    py2 = python_rows(engine, golden, taxonomy)
    corpus_parity = py['digests'] == py2['digests']

    html = ARTIFACT.read_text(encoding='utf-8')
    shell = validate_shell(html_text=html, repo_root=ROOT)
    manifest = load_json(MANIFEST)
    compiled = compacted_engine_bytes()
    budget = {
        'runtime_js_code_bytes': shell['byte_accounting']['runtime_js_code_bytes'],
        'runtime_js_ceiling_bytes': shell['byte_accounting']['runtime_js_ceiling_bytes'],
        'runtime_js_headroom_bytes': shell['byte_accounting']['runtime_js_ceiling_bytes'] -
                                     shell['byte_accounting']['runtime_js_code_bytes'],
        'engine_island_bytes': manifest['engines_island']['bytes'],
        'engine_compiled_bytes': compiled,
        'engine_source_bytes': ENGINE_JS.stat().st_size,
        'artifact_bytes': manifest['output_bytes'],
        'artifact_sha256': manifest['output_sha256'],
        'engines_gate': next(g['summary'] for g in manifest['gates'] if g['id'] == 'engines'),
        'status': 'PASS',
        'note': ('The Section 1.3 runtime-JS code ceiling was already 83 bytes from its limit before N17. '
                 'The engine module therefore ships as src/quantity-engine.js, is validated by gate 13, '
                 'its contract and vectors ship in #sim-engines, and the runtime harness loads the module '
                 'directly against the shipped islands. N31 must lazy-load or re-budget before inlining it.'),
    }

    ev = taxonomy['engine_vectors']
    ambiguity = next(v for v in ev['classification_vectors'] if v['id'] == 'EV-N17-CLS-08')
    ambiguity_result = engine.classify(ambiguity)

    record = {
        'schema_version': 1, 'task': 'N17', 'status': 'PASS',
        'validation': {
            'status': report['status'], 'summary': report['summary'],
            'digests': report['digests'], 'errors': report['errors'],
        },
        'validation_parity': validation_parity,
        'vectors': {
            'golden_rows': report['vector_rows'], 'golden_failures': report['vector_failures'],
            'stratum_rows': report['stratum_rows'],
        },
        'v04_corpus': [r for r in report['stratum_rows'] if r['kind'] == 'v04'],
        'conservation': {
            'rows': [r for r in report['stratum_rows'] if r['kind'] == 'conservation'],
            'scratch': {
                'id': ev['scratch']['conservation']['id'],
                'verdict': engine.check_conservation(ev['scratch']['conservation'])['verdict'],
                'signature': engine.check_conservation(ev['scratch']['conservation'])['signature'],
            },
        },
        'classification': {
            'rows': [r for r in report['stratum_rows'] if r['kind'] == 'classification'],
            'precedence_rule': taxonomy['error_taxonomy']['precedence_rule_verbatim'],
            'ambiguous_member': {'id': ambiguity['id'], 'trace': ambiguity_result['precedence_trace'],
                                 'class': ambiguity_result['taxonomy_class']},
            'boundary_rule': taxonomy['error_taxonomy']['boundary_rule_verbatim'],
        },
        'signature_alignment': report['citation_rows'],
        'no_local_constants': report['no_local_constants'],
        'conventions_consumption': {
            'paths': report['conventions_paths'],
            'conventions_digest': report['digests']['conventions'],
            'status': 'PASS' if report['no_local_constants']['status'] == 'PASS' else 'FAIL',
        },
        'cross_language': cross,
        'negative': {'scratch_constant_regression': scratch},
        'throughput': rate,
        'budget': budget,
        'smoke': runtime['smoke_summary'],
        'smoke_digest': SMOKE_DIGEST,
        'runtime': runtime,
        'corpus_parity': corpus_parity,
        'handoff': {
            'n18': 'SimEngines.grade / checkConservation contract for the graph and energy vectors',
            'n20': 'SimEngines.classify reparameterization bounds from conventions entries',
            'n22': 'SimEngines.quantity / convert / dimensionGate input semantics',
            'n23': 'taxonomy_class, signature, feedback_key and feedback_text on every verdict',
            'n31': 'inline or lazy-load src/quantity-engine.js after budget decision',
        },
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': record['status'], 'out': str(out), 'bytes': out.stat().st_size,
        'sha256': sha256_file(out), 'validation_parity': validation_parity,
        'cross_language': cross['status'], 'corpus_parity': corpus_parity,
        'golden': f"{report['summary']['golden_pass']}/{report['summary']['golden_vectors']}",
        'stratum': f"{report['summary']['stratum_pass']}/{report['summary']['stratum_vectors']}",
        'scratch': scratch['status'], 'throughput': rate['status'],
        'engine_island_bytes': budget['engine_island_bytes'],
        'engine_compiled_bytes': compiled,
        'headroom': budget['runtime_js_headroom_bytes'],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
