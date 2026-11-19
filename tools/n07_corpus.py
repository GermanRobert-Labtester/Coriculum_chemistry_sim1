#!/usr/bin/env python3
"""N07 deterministic verification corpus & negative-fixture suite.

Executes and records:
  1. Clean N07 validation (64/64 master anchors bound to N01 freeze,
     64/64 registry entries, 127/127 edge links, 192/192 owned slots,
     deterministic layout digest, diamond & Topic-3 wide-layer fixtures).
  2. Negative fixture: cycle injected in coverage prerequisite graph fails
     loudly naming the cycle and refuses build before writing.
  3. Negative fixture: scratch dangling concept link ('#karte-P9-99') in
     anchor registry fails by exact link name and refuses build.
  4. Negative fixture: slot without owner_task fails authoring check by
     concept and slot kind and refuses build.
  5. Negative fixture: broken master_anchor in concept summary fails case-exact
     re-validation against frozen masters and refuses build.
  6. Negative fixture: missing V-02 / V-03 dissent notes fail conventions wording check.
  7. Runtime harness (Node VM): layout determinism, semantic keyboard/edge
     checks, focus-sequence fixture, nested-drawer restore fixture, direct-link
     no-map entry, and smoke vector SMK-N07-MAP-DRAWER-WALK.
  8. Fresh-process walk replay parity (in-process runs A/B vs fresh subprocess).
  9. Double-build parity & prior-phase zero-regression (N02, N03, N05, N06).

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
from coverage_common import COVERAGE_PATH, DEST, load_json, sha256_file  # noqa: E402
from validate_n07_map import REGISTRY_PATH, SUMMARIES_PATH, validate_all  # noqa: E402

WORK = Path('/tmp/opencode/n07-corpus')
RECORD_PATH = DEST / 'evidence/N07_CORPUS_RECORD.json'


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

    # 1. Clean N07 validation
    clean_report = validate_all(repo_root=DEST)
    if clean_report['status'] != 'PASS':
        failures.append('clean N07 map/drawer validation failed')

    cov_data = load_json(DEST / COVERAGE_PATH)
    sum_data = load_json(DEST / SUMMARIES_PATH)
    reg_data = load_json(DEST / REGISTRY_PATH)

    # 2. Cycle negative fixture
    cycle_cov = copy.deepcopy(cov_data)
    for o in cycle_cov['outcomes']:
        if o['id'] == 'P1-05':
            o['prerequisites'] = ['P1-01']
            break
    cycle_report = validate_all(repo_root=DEST, coverage_data=cycle_cov)
    cycle_path = WORK / 'coverage_cycle.json'
    _write_json(cycle_path, cycle_cov)
    refused_cycle_out = WORK / 'refused_cycle.html'
    refused_cycle_manifest = WORK / 'refused_cycle_manifest.json'
    cycle_gate = _run_cmd([
        sys.executable, 'tools/build.py',
        '--island', str(cycle_path),
        '--out', str(refused_cycle_out),
        '--manifest-out', str(refused_cycle_manifest),
    ])
    if cycle_report['status'] != 'FAIL' or not any('Cycle' in e or 'cycle' in e.lower() for e in cycle_report['errors']):
        failures.append('cycle fixture did not fail naming cycle')
    if cycle_gate['returncode'] == 0 or refused_cycle_out.exists():
        failures.append('build gate did not refuse cycle fixture')

    # 3. Dangling concept link negative fixture
    dangling_reg = copy.deepcopy(reg_data)
    dangling_reg['concepts'][0]['prerequisite_edges'].append({
        'from': 'P9-99',
        'to': 'P1-01',
        'target_anchor': '#karte-P9-99',
        'kind': 'cross-topic',
    })
    dangling_report = validate_all(repo_root=DEST, registry_data=dangling_reg)
    dangling_path = WORK / 'registry_dangling.json'
    _write_json(dangling_path, dangling_reg)
    refused_dangling_out = WORK / 'refused_dangling.html'
    refused_dangling_manifest = WORK / 'refused_dangling_manifest.json'
    dangling_gate = _run_cmd([
        sys.executable, 'tools/build.py',
        '--anchor-registry', str(dangling_path),
        '--out', str(refused_dangling_out),
        '--manifest-out', str(refused_dangling_manifest),
    ])
    if dangling_report['status'] != 'FAIL' or not any('#karte-P9-99' in e for e in dangling_report['errors']):
        failures.append('dangling link fixture did not fail naming #karte-P9-99')
    if dangling_gate['returncode'] == 0 or refused_dangling_out.exists():
        failures.append('build gate did not refuse dangling link fixture')

    # 4. Missing slot owner_task negative fixture
    missing_owner_sum = copy.deepcopy(sum_data)
    del missing_owner_sum['concepts'][0]['slots']['figures']['owner_task']
    missing_owner_report = validate_all(repo_root=DEST, summaries_data=missing_owner_sum)
    missing_owner_path = WORK / 'summaries_no_owner.json'
    _write_json(missing_owner_path, missing_owner_sum)
    refused_owner_out = WORK / 'refused_owner.html'
    refused_owner_manifest = WORK / 'refused_owner_manifest.json'
    owner_gate = _run_cmd([
        sys.executable, 'tools/build.py',
        '--concept-summaries', str(missing_owner_path),
        '--out', str(refused_owner_out),
        '--manifest-out', str(refused_owner_manifest),
    ])
    if missing_owner_report['status'] != 'FAIL' or not any('owner_task' in e for e in missing_owner_report['errors']):
        failures.append('missing slot owner fixture did not fail naming owner_task')
    if owner_gate['returncode'] == 0 or refused_owner_out.exists():
        failures.append('build gate did not refuse missing slot owner fixture')

    # 5. Broken master anchor negative fixture
    broken_anchor_sum = copy.deepcopy(sum_data)
    broken_anchor_sum['concepts'][0]['master_anchor'] = 'neeksistejoss-enkurs'
    broken_anchor_report = validate_all(repo_root=DEST, summaries_data=broken_anchor_sum)
    broken_anchor_path = WORK / 'summaries_bad_anchor.json'
    _write_json(broken_anchor_path, broken_anchor_sum)
    refused_anchor_out = WORK / 'refused_anchor.html'
    refused_anchor_manifest = WORK / 'refused_anchor_manifest.json'
    anchor_gate = _run_cmd([
        sys.executable, 'tools/build.py',
        '--concept-summaries', str(broken_anchor_path),
        '--out', str(refused_anchor_out),
        '--manifest-out', str(refused_anchor_manifest),
    ])
    if broken_anchor_report['status'] != 'FAIL' or not any('#neeksistejoss-enkurs' in e for e in broken_anchor_report['errors']):
        failures.append('broken master_anchor fixture did not fail naming #neeksistejoss-enkurs')
    if anchor_gate['returncode'] == 0 or refused_anchor_out.exists():
        failures.append('build gate did not refuse broken master_anchor fixture')

    # 6. Missing V-02 / V-03 dissent negative fixture
    no_dissent_sum = copy.deepcopy(sum_data)
    for c in no_dissent_sum['concepts']:
        if c['id'] in ('P3-01', 'P6-02'):
            c['dissent_note_lv'] = None
    no_dissent_report = validate_all(repo_root=DEST, summaries_data=no_dissent_sum)
    if no_dissent_report['status'] != 'FAIL' or not (
        any('P3-01' in e and 'V-02' in e for e in no_dissent_report['errors']) and
        any('P6-02' in e and 'V-03' in e for e in no_dissent_report['errors'])
    ):
        failures.append('missing V-02/V-03 dissent fixture did not fail naming P3-01 and P6-02')

    # 7. Double-build parity
    build_a_html = WORK / 'build_a.html'
    build_a_manifest = WORK / 'build_a_manifest.json'
    cmd_a = _run_cmd([sys.executable, 'tools/build.py', '--out', str(build_a_html), '--manifest-out', str(build_a_manifest)])
    cmd_1 = _run_cmd([sys.executable, 'tools/build.py'])
    sha_1 = sha256_file(DEST / 'output/simulator.html')
    man_sha_1 = sha256_file(DEST / 'output/build-manifest.json')
    cmd_2 = _run_cmd([sys.executable, 'tools/build.py'])
    sha_2 = sha256_file(DEST / 'output/simulator.html')
    man_sha_2 = sha256_file(DEST / 'output/build-manifest.json')
    if cmd_a['returncode'] != 0 or cmd_1['returncode'] != 0 or cmd_2['returncode'] != 0:
        failures.append('clean build failed')
    html_parity = sha256_file(build_a_html) == sha_1 == sha_2
    manifest_parity = man_sha_1 == man_sha_2
    if not html_parity or not manifest_parity:
        failures.append('double-build parity mismatch')

    # 8. Runtime harness + fresh-process walk replay
    rt_cmd = _run_cmd(['node', 'tools/check_n07_runtime.js', '--json'])
    if rt_cmd['returncode'] != 0:
        failures.append('n07 runtime harness failed')
    rt_report = json.loads(rt_cmd['stdout'])

    walk_fresh_cmd = _run_cmd(['node', 'tools/check_n07_runtime.js', '--walk-only'])
    if walk_fresh_cmd['returncode'] != 0:
        failures.append('n07 fresh-process walk replay failed')
    walk_fresh = json.loads(walk_fresh_cmd['stdout'])
    walk_in_proc_digest = rt_report['checks']['walk_trace']['run_a_digest']
    walk_fresh_digest = walk_fresh['digest']
    if walk_in_proc_digest != walk_fresh_digest:
        failures.append(f'walk trace fresh-process digest mismatch: {walk_in_proc_digest} != {walk_fresh_digest}')

    # 9. Prior-phase runtime regression
    n02_cmd = _run_cmd(['node', 'tools/check_coverage_runtime.js', '--json'])
    n03_cmd = _run_cmd(['node', 'tools/check_conventions_runtime.js', '--json'])
    n05_cmd = _run_cmd(['node', 'tools/check_golden_vectors_runtime.js', '--json'])
    n06_cmd = _run_cmd(['node', 'tools/check_n06_runtime.js', '--json'])
    for label, cmd in (('N02', n02_cmd), ('N03', n03_cmd), ('N05', n05_cmd), ('N06', n06_cmd)):
        if cmd['returncode'] != 0:
            failures.append(f'{label} runtime regression failed')

    manifest = load_json(DEST / 'output/build-manifest.json')
    record = {
        'schema_version': 1,
        'task': 'N07',
        'status': 'PASS' if not failures else 'FAIL',
        'failures': failures,
        'validation': clean_report,
        'negative_fixtures': {
            'cycle_in_coverage': {
                'validator_status': cycle_report['status'],
                'errors': cycle_report['errors'],
                'build_returncode': cycle_gate['returncode'],
                'artifact_written': refused_cycle_out.exists(),
                'stderr': cycle_gate['stderr'],
            },
            'dangling_concept_link': {
                'validator_status': dangling_report['status'],
                'errors': dangling_report['errors'],
                'build_returncode': dangling_gate['returncode'],
                'artifact_written': refused_dangling_out.exists(),
                'stderr': dangling_gate['stderr'],
            },
            'missing_slot_owner': {
                'validator_status': missing_owner_report['status'],
                'errors': missing_owner_report['errors'],
                'build_returncode': owner_gate['returncode'],
                'artifact_written': refused_owner_out.exists(),
                'stderr': owner_gate['stderr'],
            },
            'broken_master_anchor': {
                'validator_status': broken_anchor_report['status'],
                'errors': broken_anchor_report['errors'],
                'build_returncode': anchor_gate['returncode'],
                'artifact_written': refused_anchor_out.exists(),
                'stderr': anchor_gate['stderr'],
            },
            'missing_v02_v03_dissent': {
                'validator_status': no_dissent_report['status'],
                'errors': no_dissent_report['errors'],
            },
        },
        'runtime_harness': rt_report,
        'walk_replay_parity': {
            'in_process_run_a': walk_in_proc_digest,
            'in_process_run_b': rt_report['checks']['walk_trace']['run_b_digest'],
            'fresh_process_digest': walk_fresh_digest,
            'all_identical': (
                walk_in_proc_digest == rt_report['checks']['walk_trace']['run_b_digest'] == walk_fresh_digest
            ),
        },
        'prior_runtime_regression': {
            'n02_coverage': json.loads(n02_cmd['stdout'])['status'],
            'n03_conventions': json.loads(n03_cmd['stdout'])['status'],
            'n05_golden_vectors': json.loads(n05_cmd['stdout'])['status'],
            'n06_shell': json.loads(n06_cmd['stdout'])['status'],
        },
        'build_parity': {
            'html_identical': html_parity,
            'manifest_identical': manifest_parity,
            'output_sha256': sha_2,
            'output_bytes': (DEST / 'output/simulator.html').stat().st_size,
            'manifest_sha256': man_sha_2,
            'byte_accounting': {
                'css_bytes': manifest['tokens_layer']['css_bytes'],
                'runtime_js_bytes': manifest['tokens_layer']['runtime_js_bytes'],
                'template_overhead_bytes': manifest['tokens_layer']['template_overhead_bytes'],
                'embedded_summaries_bytes': manifest['concept_map_layer']['embedded_summaries_bytes'],
                'embedded_registry_bytes': manifest['concept_map_layer']['embedded_registry_bytes'],
                'concept_map_js_bytes': manifest['concept_map_layer']['concept_map_js_bytes'],
                'concept_drawer_js_bytes': manifest['concept_map_layer']['concept_drawer_js_bytes'],
            },
        },
        'source_digests': {
            rel: {
                'sha256': sha256_file(DEST / rel),
                'bytes': (DEST / rel).stat().st_size,
            }
            for rel in [
                'data/concept_summaries.json',
                'data/anchor_registry.json',
                'src/concept-map.js',
                'src/concept-drawer.js',
                'src/coverage-view.js',
                'src/smoke-subset.js',
                'src/styles.css',
                'src/shell.html',
                'tools/validate_n07_map.py',
                'tools/build.py',
                'tools/check_n07_runtime.js',
            ]
        },
    }
    _write_json(RECORD_PATH, record)
    print(f"{record['status']} n07_corpus: wrote {RECORD_PATH} ({RECORD_PATH.stat().st_size} bytes, sha256={sha256_file(RECORD_PATH)})")
    for err in failures:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
