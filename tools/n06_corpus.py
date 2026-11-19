#!/usr/bin/env python3
"""N06 deterministic verification corpus & negative-fixture suite.

Executes and records:
  1. Design token validation & theme completeness (26 semantic tokens x 2 themes,
     27 use-classed pairs, 0 raw CSS findings).
  2. Negative fixture: scratch dark theme missing '--border-subtle' fails by name
     and refuses build before writing any artifact.
  3. Negative fixture: scratch CSS with raw '#ff0000' and '12px' fails raw-value
     scan by kind and value, and refuses build before writing any artifact.
  4. Shell contract, ARIA foundation, copy lint (+ N10 stub pass), zero-URL
     scan, and Section 1.3 byte accounting on output/simulator.html.
  5. Negative fixtures on shell contract: injected external URL fails by URL/line,
     and injected endorsement copy fails by forbidden word.
  6. Node.js runtime harness (start view, 64 verbatim objectives, single-source,
     markup escaping, theme toggle state machine + no-store degradation, and
     in-file smoke vector SMK-N06-COVERAGE-COUNTS).
  7. Double-build parity in fresh temp directories.

Produces zero timestamps so consecutive runs emit byte-identical JSON.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_n06_shell import validate_shell  # noqa: E402
from validate_tokens import STYLES_PATH, TOKENS_PATH, validate_tokens  # noqa: E402

WORK = Path('/tmp/opencode/n06-corpus')
RECORD_PATH = DEST / 'evidence/N06_CORPUS_RECORD.json'


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _run_cmd(args: list[str]) -> dict[str, Any]:
    res = subprocess.run(args, cwd=DEST, capture_output=True, text=True)
    return {
        'command': ' '.join(args),
        'returncode': res.returncode,
        'stdout': res.stdout.strip(),
        'stderr': res.stderr.strip(),
    }


def main() -> int:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []

    # 1. Clean token validation
    tokens_report = validate_tokens(repo_root=DEST)
    if tokens_report['status'] != 'PASS':
        failures.append('baseline tokens validation failed')

    # 2. Missing-token negative fixture + build gate refusal
    tokens_data = load_json(DEST / TOKENS_PATH)
    missing_tok_data = copy.deepcopy(tokens_data)
    del missing_tok_data['themes']['dark']['--border-subtle']
    missing_tok_report = validate_tokens(repo_root=DEST, tokens_data=missing_tok_data)
    missing_tok_path = WORK / 'tokens_missing.json'
    _write_json(missing_tok_path, missing_tok_data)
    refused_out = WORK / 'refused_missing_token.html'
    refused_manifest = WORK / 'refused_missing_token_manifest.json'
    missing_gate_cmd = _run_cmd([
        sys.executable, 'tools/build.py',
        '--tokens', str(missing_tok_path),
        '--out', str(refused_out),
        '--manifest-out', str(refused_manifest),
    ])
    if missing_tok_report['status'] != 'FAIL' or not any('--border-subtle' in e for e in missing_tok_report['errors']):
        failures.append('missing-token fixture did not fail naming --border-subtle')
    if missing_gate_cmd['returncode'] == 0 or refused_out.exists():
        failures.append('build gate did not refuse missing-token fixture cleanly')

    # 3. Raw CSS value negative fixture + build gate refusal
    raw_css = (DEST / STYLES_PATH).read_text(encoding='utf-8') + '\n.bad { color: #ff0000; font-size: 12px; }\n'
    raw_css_report = validate_tokens(repo_root=DEST, styles_text=raw_css)
    raw_css_path = WORK / 'styles_raw.css'
    raw_css_path.write_text(raw_css, encoding='utf-8')
    refused_raw_out = WORK / 'refused_raw_css.html'
    refused_raw_manifest = WORK / 'refused_raw_css_manifest.json'
    raw_gate_cmd = _run_cmd([
        sys.executable, 'tools/build.py',
        '--styles', str(raw_css_path),
        '--out', str(refused_raw_out),
        '--manifest-out', str(refused_raw_manifest),
    ])
    if raw_css_report['status'] != 'FAIL' or raw_css_report['raw_value_findings_count'] < 2:
        failures.append('raw-value CSS fixture did not catch #ff0000 and 12px')
    if raw_gate_cmd['returncode'] == 0 or refused_raw_out.exists():
        failures.append('build gate did not refuse raw-value CSS fixture cleanly')

    # 4. Double-build parity + main artifact check
    build_a_html = WORK / 'build_a.html'
    build_a_manifest = WORK / 'build_a_manifest.json'
    cmd_a = _run_cmd([sys.executable, 'tools/build.py', '--out', str(build_a_html), '--manifest-out', str(build_a_manifest)])
    cmd_main_1 = _run_cmd([sys.executable, 'tools/build.py'])
    html_sha_1 = sha256_file(DEST / 'output/simulator.html')
    manifest_sha_1 = sha256_file(DEST / 'output/build-manifest.json')
    cmd_main_2 = _run_cmd([sys.executable, 'tools/build.py'])
    html_sha_2 = sha256_file(DEST / 'output/simulator.html')
    manifest_sha_2 = sha256_file(DEST / 'output/build-manifest.json')
    if cmd_a['returncode'] != 0 or cmd_main_1['returncode'] != 0 or cmd_main_2['returncode'] != 0:
        failures.append('clean build failed')
    html_parity = sha256_file(build_a_html) == html_sha_1 == html_sha_2
    manifest_parity = manifest_sha_1 == manifest_sha_2
    if not html_parity or not manifest_parity:
        failures.append('double-build parity mismatch')

    # 5. Shell contract, ARIA, copy lint, URL scan, byte accounting
    shipped_html = (DEST / 'output/simulator.html').read_text(encoding='utf-8')
    shell_report = validate_shell(html_text=shipped_html, repo_root=DEST)
    if shell_report['status'] != 'PASS':
        failures.append('shipped shell contract validation failed')

    # 6. External URL & forbidden endorsement negative fixtures
    url_injected_html = shipped_html.replace('</body>', '<!-- bad --><link href="https://cdn.example.invalid/style.css"></body>')
    url_injected_report = validate_shell(html_text=url_injected_html, repo_root=DEST)
    if url_injected_report['status'] != 'FAIL' or url_injected_report['structural']['external_urls_count'] != 1:
        failures.append('external URL negative fixture did not fail with count 1')

    copy_injected_html = shipped_html.replace('Patstāvīgas sagatavošanās', 'Oficiāli apstiprināts eksāmens ar sertifikātu; patstāvīgas sagatavošanās')
    copy_injected_report = validate_shell(html_text=copy_injected_html, repo_root=DEST)
    if copy_injected_report['status'] != 'FAIL' or copy_injected_report['copy_lint']['status'] != 'FAIL':
        failures.append('forbidden endorsement copy fixture did not fail copy lint')

    # 7. Runtime harness (Node VM)
    runtime_cmd = _run_cmd(['node', 'tools/check_n06_runtime.js', '--json'])
    if runtime_cmd['returncode'] != 0:
        failures.append('n06 runtime harness failed')
    runtime_report = json.loads(runtime_cmd['stdout'])

    # 8. Re-run N02, N03, N05 runtime harnesses for zero-regression
    n02_cmd = _run_cmd(['node', 'tools/check_coverage_runtime.js', '--json'])
    n03_cmd = _run_cmd(['node', 'tools/check_conventions_runtime.js', '--json'])
    n05_cmd = _run_cmd(['node', 'tools/check_golden_vectors_runtime.js', '--json'])
    if n02_cmd['returncode'] != 0 or n03_cmd['returncode'] != 0 or n05_cmd['returncode'] != 0:
        failures.append('prior phase runtime regression check failed')

    record = {
        'schema_version': 1,
        'task': 'N06',
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'tokens': tokens_report,
        'negative_fixtures': {
            'missing_token': {
                'validator_status': missing_tok_report['status'],
                'errors': missing_tok_report['errors'],
                'build_returncode': missing_gate_cmd['returncode'],
                'artifact_written': refused_out.exists(),
                'stderr': missing_gate_cmd['stderr'],
            },
            'raw_css_values': {
                'validator_status': raw_css_report['status'],
                'findings': raw_css_report['raw_value_findings'],
                'build_returncode': raw_gate_cmd['returncode'],
                'artifact_written': refused_raw_out.exists(),
                'stderr': raw_gate_cmd['stderr'],
            },
            'external_url_injection': {
                'status': url_injected_report['status'],
                'external_urls': url_injected_report['structural']['external_urls'],
            },
            'forbidden_endorsement_copy': {
                'status': copy_injected_report['copy_lint']['status'],
                'errors': copy_injected_report['copy_lint']['errors'],
            },
        },
        'shell_contract': shell_report,
        'runtime_harness': runtime_report,
        'prior_runtime_regression': {
            'n02_coverage': json.loads(n02_cmd['stdout'])['status'],
            'n03_conventions': json.loads(n03_cmd['stdout'])['status'],
            'n05_golden_vectors': json.loads(n05_cmd['stdout'])['status'],
        },
        'build_parity': {
            'html_identical': html_parity,
            'manifest_identical': manifest_parity,
            'output_sha256': sha256_file(DEST / 'output/simulator.html'),
            'output_bytes': (DEST / 'output/simulator.html').stat().st_size,
            'manifest_sha256': sha256_file(DEST / 'output/build-manifest.json'),
        },
        'source_digests': {
            rel: {
                'sha256': sha256_file(DEST / rel),
                'bytes': (DEST / rel).stat().st_size,
            }
            for rel in [
                'data/tokens.json',
                'data/n06_term_stubs.json',
                'src/styles.css',
                'src/shell.html',
                'src/start-view.js',
                'src/coverage-view.js',
                'src/theme-toggle.js',
                'src/smoke-subset.js',
                'tools/validate_tokens.py',
                'tools/validate_n06_shell.py',
                'tools/build.py',
                'tools/check_n06_runtime.js',
            ]
        },
    }
    _write_json(RECORD_PATH, record)
    print(f"{record['status']} n06_corpus: wrote {RECORD_PATH} ({RECORD_PATH.stat().st_size} bytes, sha256={sha256_file(RECORD_PATH)})")
    for err in failures:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
