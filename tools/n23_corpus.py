#!/usr/bin/env python3
"""N23 corpus runner: the evidence chain of the grading and feedback layer.

It runs the N23 gates and harnesses and collects their findings:

  1. the grading gate      — tools/validate_n23_grading.py: the
                             #sim-grading-policy island, the verdict-rule
                             totality, the classification totality, the
                             remediation-id resolution and the no-tolerance
                             source scan (``--report``);
  2. the classification    — tools/n23_classification.py (N23-B): the scripted
     sweep                   error corpus, the priority ordering and the
                             zero-unmapped/zero-unresolved sweep;
  3. the runtime harness   — tools/check_n23_runtime.js (N23-C): the score
                             matrix, the analytics chain, the render fixture,
                             the determinism proof (twice + fresh process), the
                             batch digest and the three in-file smoke vectors
                             (``--record``). The harness also writes
                             evidence/N23_CHAIN_RECORD.json,
                             evidence/N23_RENDER_FIXTURE.json and
                             evidence/N23_DETERMINISM_RECORD.json next to its
                             record.

The budget accounting reads output/build-manifest.json through
tools/byte_budget.py and adds the N23 contribution: the two inlined islands
(which the merge build embeds), the ``feedback.results.*`` terms, the appended
smoke vectors and the #rezultati copy. The compiled grading modules ship from
src/ and are NOT inlined, so they are recorded but do not enter the artifact
total.

Every child artifact of N23 is authored by a parallel subagent (the grading
core, the classification layer, the official compile). A missing child is named
and reported as PENDING — never a quiet pass and never a FAIL: FAIL is reserved
for a tool that ran and reported a violation.

The records are timestamp-free and byte-identical across runs: the whole
collection runs twice in one invocation and the two record digests are compared
(the same two-invocation parity n22_corpus.py documents).

  evidence/N23_CORPUS_RECORD.json        — the extended corpus
  evidence/N23_VALIDATION_RECORD.json    — the grading gate's report
  evidence/N23_CLASSIFICATION_TABLE.json — the classification sweep (when it writes one)
  evidence/N23_RUNTIME_RECORD.json       — the N23-C harness record
  evidence/N23_CHAIN_RECORD.json         — the digest-linked chain fixture
  evidence/N23_RENDER_FIXTURE.json       — the mixed-form score report (N32 test data)
  evidence/N23_DETERMINISM_RECORD.json   — the three-way determinism digests

Usage:
    python3 tools/n23_corpus.py [--out PATH] [--once]
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
from coverage_common import DEST, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402

ROOT = DEST
GATE = ROOT / 'tools/validate_n23_grading.py'
CLASSIFICATION = ROOT / 'tools/n23_classification.py'
RUNTIME = ROOT / 'tools/check_n23_runtime.js'
GRADING_POLICY = ROOT / 'data/grading_policy.json'
CLASSIFICATION_ISLAND = ROOT / 'data/feedback_classification.json'
SCORE_MATRIX = ROOT / 'tools/fixtures/n23_score_matrix.json'
FEEDBACK_SAMPLE = ROOT / 'tools/fixtures/n23_feedback_sample.json'
TERMS = ROOT / 'data/terms.json'
SHELL = ROOT / 'src/shell.html'
SMOKE = ROOT / 'src/smoke-subset.js'
MANIFEST = ROOT / 'output/build-manifest.json'

OUT_DEFAULT = ROOT / 'evidence/N23_CORPUS_RECORD.json'
VALIDATION_RECORD = ROOT / 'evidence/N23_VALIDATION_RECORD.json'
CLASSIFICATION_TABLE = ROOT / 'evidence/N23_CLASSIFICATION_TABLE.json'
RUNTIME_RECORD = ROOT / 'evidence/N23_RUNTIME_RECORD.json'
CHAIN_RECORD = ROOT / 'evidence/N23_CHAIN_RECORD.json'
RENDER_RECORD = ROOT / 'evidence/N23_RENDER_FIXTURE.json'
DETERMINISM_RECORD = ROOT / 'evidence/N23_DETERMINISM_RECORD.json'

# The N21/N22 ledger records src/smoke-subset.js at 31 837 B (the N22 merge).
# The three N23 vectors and the shared n23Run helper are what this task appends,
# so the delta against that measured baseline is the smoke contribution.
SMOKE_BASELINE_BYTES = 31837
SMOKE_IDS = ['SMK-N23-GRADE-FULL', 'SMK-N23-GRADE-PARTIAL', 'SMK-N23-GRADE-MALFORMED']

DIGEST_FILES = [
    'data/grading_policy.json',
    'data/feedback_classification.json',
    'src/grading.ts',
    'src/feedback.ts',
    'src/compiled/grading.js',
    'src/compiled/feedback.js',
    'tools/validate_n23_grading.py',
    'tools/n23_classification.py',
    'tools/check_n23_runtime.js',
    'tools/fixtures/n23_score_matrix.json',
    'tools/fixtures/n23_feedback_sample.json',
    'src/smoke-subset.js',
]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run_tool(command: list[str], label: str) -> dict[str, Any]:
    """Run one tool and keep its exit code and its stdout report."""
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
        'status': 'PASS' if proc.returncode == 0 else ('PENDING' if proc.returncode == 3 else 'FAIL'),
        'report': payload,
        'stdout': stdout[:2000],
        'stderr': proc.stderr.strip()[:2000],
    }


def run_optional(command: list[str], label: str, script: Path, owner: str) -> dict[str, Any]:
    """A required-for-N23 record that a sibling owns: absent means PENDING."""
    if not script.exists():
        return {
            'label': label,
            'command': ' '.join(command),
            'returncode': None,
            'status': 'PENDING',
            'reason': f'{script.relative_to(ROOT)} does not exist yet; {owner} owns it.',
            'owner': owner,
        }
    return run_tool(command, label)


def classification_command() -> list[str]:
    """Run the sweep with its own report when the script declares ``--report``."""
    command = ['python3', 'tools/n23_classification.py']
    if CLASSIFICATION.exists() and '--report' in CLASSIFICATION.read_text(encoding='utf-8'):
        command += ['--report', 'evidence/N23_CLASSIFICATION_TABLE.json']
    return command


# ------------------------------------------------------------------- budgets


def measure_budgets() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {'status': 'FAIL', 'reason': 'output/build-manifest.json is missing; run the build first.'}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    measured = byte_budget.measure_budgets(manifest)
    measured['notes'] = [
        'The measured figures are the manifest of the LAST successful build in this repository. The '
        'N23 measurement that set the two new ceilings was taken from the N23 build of 2026-11-19 '
        '(artifact 1,611,018 B, runtime JS 277,359 B); it is recorded in tools/byte_budget.py '
        'RE_BUDGET_HISTORY, so the ceilings below already account for N23.',
        'The N23 grading and feedback modules (src/compiled/grading.js, src/compiled/feedback.js) ship '
        'from src/ and are NOT inlined, so they do not enter the artifact total; only the two islands, '
        'the terms entries, the smoke vectors and the shell copy do. N31 owns the final inline / '
        'lazy-load / re-budget decision.',
        'No ceiling is changed by this runner. A ceiling moved once, on an exceeded measurement, through '
        'the visible RE_BUDGET_HISTORY entry in tools/byte_budget.py; the entries are quoted in '
        'budget_effect.re_budget_entries.',
    ]
    return measured


def canonical_island_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    document = json.loads(path.read_text(encoding='utf-8'))
    text = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(',', ':')).replace('</', '<\\/')
    return len(text.encode('utf-8'))


def feedback_results_terms_bytes() -> dict[str, Any]:
    """The ``feedback.results.*`` term entries N23 adds to data/terms.json."""
    if not TERMS.exists():
        return {'bytes': 0, 'entries': 0, 'keys': [], 'status': 'PENDING'}
    terms = json.loads(TERMS.read_text(encoding='utf-8'))
    entries = [entry for entry in terms.get('terms', [])
               if isinstance(entry.get('key'), str) and entry['key'].startswith('feedback.results.')]
    projected = canonical_json_bytes({'terms': entries})
    return {
        'bytes': len(projected),
        'entries': len(entries),
        'keys': [entry['key'] for entry in entries],
        'status': 'PASS' if entries else 'PENDING',
        'reason': None if entries else 'no feedback.results.* entries in data/terms.json yet (owner: the N23 feedback subagent)',
    }


def shell_copy_bytes() -> int:
    """The #rezultati pending-slot block, measured between its own div tags."""
    if not SHELL.exists():
        return 0
    text = SHELL.read_text(encoding='utf-8')
    start = text.find('<div class="pending-slot" data-pending-owner="N23">')
    if start < 0:
        return 0
    end = text.find('</div>', start)
    if end < 0:
        return 0
    return len(text[start:end + len('</div>')].encode('utf-8'))


def n23_layer_bytes() -> dict[str, Any]:
    """The N23 byte contribution, split by what is inlined and what is not."""
    modules = []
    total = 0
    for relative in ('src/compiled/grading.js', 'src/compiled/feedback.js',
                     'src/grading.ts', 'src/feedback.ts'):
        path = ROOT / relative
        if not path.exists():
            modules.append({'path': relative, 'bytes': None, 'sha256': None, 'missing': True,
                            'inlined_in_artifact': False})
            continue
        size = path.stat().st_size
        total += size
        modules.append({
            'path': relative,
            'bytes': size,
            'sha256': sha256_file(path),
            'inlined_in_artifact': False,
            'note': 'Ships from src/; the artifact does not inline it (N31 owns the decision).',
        })
    policy_bytes = canonical_island_bytes(GRADING_POLICY)
    classification_bytes = canonical_island_bytes(CLASSIFICATION_ISLAND)
    islands = [
        {
            'id': 'sim-grading-policy',
            'path': 'data/grading_policy.json',
            'bytes': policy_bytes,
            'file_bytes': GRADING_POLICY.stat().st_size if GRADING_POLICY.exists() else None,
            'sha256': sha256_file(GRADING_POLICY) if GRADING_POLICY.exists() else None,
            'inlined_in_artifact': True,
            'status': 'READ' if GRADING_POLICY.exists() else 'PENDING',
        },
        {
            'id': 'sim-feedback-classification',
            'path': 'data/feedback_classification.json',
            'bytes': classification_bytes,
            'file_bytes': CLASSIFICATION_ISLAND.stat().st_size if CLASSIFICATION_ISLAND.exists() else None,
            'sha256': sha256_file(CLASSIFICATION_ISLAND) if CLASSIFICATION_ISLAND.exists() else None,
            'inlined_in_artifact': True,
            'status': 'READ' if CLASSIFICATION_ISLAND.exists() else 'PENDING',
        },
    ]
    terms = feedback_results_terms_bytes()
    smoke_bytes = max(0, SMOKE.stat().st_size - SMOKE_BASELINE_BYTES) if SMOKE.exists() else 0
    copy_bytes = shell_copy_bytes()
    projections = {
        'grading_policy_island_bytes': policy_bytes,
        'classification_island_bytes': classification_bytes,
        'feedback_results_terms_bytes': terms['bytes'],
        'smoke_appended_bytes': smoke_bytes,
        'shell_copy_bytes': copy_bytes,
    }
    projections['projected_artifact_delta_bytes'] = sum(projections.values())
    projections['projected_terms_delta_note'] = (
        'feedback_results_terms_bytes is the canonical size of the feedback.results.* entries only; '
        'the rest of data/terms.json is not attributable to N23.')
    return {
        'modules': modules,
        'runtime_module_bytes_total': total,
        'islands': islands,
        'terms': terms,
        'smoke_vectors': {
            'ids': SMOKE_IDS,
            'file': 'src/smoke-subset.js',
            'file_bytes': SMOKE.stat().st_size if SMOKE.exists() else None,
            'baseline_bytes': SMOKE_BASELINE_BYTES,
            'appended_bytes': smoke_bytes,
            'inlined_in_artifact': True,
        },
        'shell_copy': {'file': 'src/shell.html', 'section': '#rezultati', 'bytes': copy_bytes},
        'projections': projections,
    }


def budget_effect(budgets: dict[str, Any], layer: dict[str, Any]) -> dict[str, Any]:
    entries = {entry['name']: entry for entry in budgets.get('budgets', [])}
    artifact = entries.get('artifact_total', {})
    runtime = entries.get('runtime_js_code', {})
    deltas = layer['projections']
    artifact_measured = artifact.get('bytes')
    runtime_measured = runtime.get('bytes')
    artifact_projected = None if artifact_measured is None else artifact_measured + deltas['projected_artifact_delta_bytes']
    runtime_projected = None if runtime_measured is None else runtime_measured + deltas['smoke_appended_bytes']
    artifact_ceiling = artifact.get('max_bytes')
    runtime_ceiling = runtime.get('max_bytes')
    artifact_overrun = None if artifact_projected is None else max(0, artifact_projected - artifact_ceiling)
    runtime_overrun = None if runtime_projected is None else max(0, runtime_projected - runtime_ceiling)
    re_budget_entries = [entry for entry in byte_budget.RE_BUDGET_HISTORY if entry.get('task') == 'N23']
    return {
        'measured_artifact_total_bytes': artifact_measured,
        'measured_runtime_js_code_bytes': runtime_measured,
        'artifact_total_ceiling_bytes': artifact_ceiling,
        'runtime_js_code_ceiling_bytes': runtime_ceiling,
        'n23_contributions': deltas,
        'projected_artifact_total_bytes': artifact_projected,
        'projected_runtime_js_code_bytes': runtime_projected,
        'projected_artifact_overrun_bytes': artifact_overrun,
        'projected_runtime_js_overrun_bytes': runtime_overrun,
        'ceiling_exceeded_by_measurement': bool((artifact_overrun or 0) > 0 or (runtime_overrun or 0) > 0),
        're_budget_required_after_merge_build': bool((artifact_overrun or 0) > 0 or (runtime_overrun or 0) > 0),
        're_budget_entry_added': bool(re_budget_entries),
        're_budget_entries': re_budget_entries,
        're_budget_note': (
            'The two N23 ceilings were re-set on the measured N23 build (the entries above): the artifact '
            'total 1,504 -> 1,600 KiB at 1,611,018 B and the runtime JS 264 -> 280 KiB at 277,359 B. The '
            'manifest measured below is still the pre-N23 artifact, because gate 19 and the official '
            'compile must both pass in the repository before the artifact can be rebuilt there; the '
            'projection therefore shows the ceiling already accounting for the N23 contribution.'
            if re_budget_entries else
            'No N23 ceiling has been re-set: the current measurement does not exceed an enforced ceiling.'),
        're_budget_owner': 'coordinator / N31',
        'rule': 'AGENTS.md: budgets are set on measured new requirements. A ceiling moves only on an '
                'exceeded measurement, through the visible RE_BUDGET_HISTORY entry, never on a projection.',
    }


# ----------------------------------------------------------------- the records


def digest_bundle() -> dict[str, Any]:
    out: dict[str, Any] = {}
    missing: list[str] = []
    for relative in DIGEST_FILES:
        path = ROOT / relative
        if path.exists():
            out[relative] = {'bytes': path.stat().st_size, 'sha256': sha256_file(path)}
        else:
            out[relative] = {'bytes': None, 'sha256': None, 'missing': True, 'status': 'PENDING',
                             'owner': 'a parallel N23 subagent'}
            missing.append(relative)
    out['_status'] = 'PENDING' if missing else 'PASS'
    out['_missing'] = missing
    return out


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def collect_once() -> dict[str, Any]:
    gate = run_optional(
        ['python3', 'tools/validate_n23_grading.py', '--report', 'evidence/N23_VALIDATION_RECORD.json'],
        'grading_gate', GATE, 'the N23 grading subagent')
    classification = run_optional(
        classification_command(), 'classification_sweep', CLASSIFICATION, 'the N23 classification subagent')
    runtime = run_tool(
        ['node', 'tools/check_n23_runtime.js',
         '--record', 'evidence/N23_RUNTIME_RECORD.json',
         '--chain', 'evidence/N23_CHAIN_RECORD.json',
         '--render', 'evidence/N23_RENDER_FIXTURE.json',
         '--determinism', 'evidence/N23_DETERMINISM_RECORD.json'],
        'runtime_harness')

    runtime_record = read_json_if_exists(RUNTIME_RECORD)
    chain_record = read_json_if_exists(CHAIN_RECORD)
    render_record = read_json_if_exists(RENDER_RECORD)
    determinism_record = read_json_if_exists(DETERMINISM_RECORD)
    classification_table = read_json_if_exists(CLASSIFICATION_TABLE)

    budgets = measure_budgets()
    manifest: dict[str, Any] = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    layer = n23_layer_bytes()
    effect = budget_effect(budgets, layer)

    def row(record: dict[str, Any] | None, path: str, owner: str) -> dict[str, Any]:
        if record is None:
            return {'status': 'PENDING', 'record': path, 'reason': f'{path} does not exist yet', 'owner': owner}
        return {
            'status': record.get('status', 'PENDING'),
            'record': path,
            'claim': record.get('claim'),
            'checks': record.get('checks'),
            'failed': record.get('failed'),
            'reason': record.get('reason'),
        }

    runtime_checks = (runtime_record or {}).get('checks') or {}
    forms = (runtime_record or {}).get('forms') or []
    determinism = row(determinism_record, 'evidence/N23_DETERMINISM_RECORD.json',
                      'the N23 grading subagent / this runner')
    if determinism_record is not None:
        determinism['in_process_1'] = determinism_record.get('in_process_1')
        determinism['in_process_2'] = determinism_record.get('in_process_2')
        determinism['fresh_process'] = determinism_record.get('fresh_process')
        determinism['round_trip_identical'] = determinism_record.get('round_trip_identical')

    return {
        'gate': gate,
        'classification': classification,
        'runtime': runtime,
        'runtime_record': runtime_record,
        'runtime_forms': forms,
        'runtime_checks': runtime_checks,
        'runtime_smoke': (runtime_record or {}).get('smoke'),
        'runtime_batch': (runtime_record or {}).get('batch'),
        'classification_table': {
            'status': 'PASS' if classification_table is not None else 'PENDING',
            'record': 'evidence/N23_CLASSIFICATION_TABLE.json',
            'sha256': sha256_file(CLASSIFICATION_TABLE) if classification_table is not None else None,
            'reason': None if classification_table is not None
            else 'the classification sweep has not written evidence/N23_CLASSIFICATION_TABLE.json yet',
            'owner': 'the N23 classification subagent',
        },
        'chain': row(chain_record, 'evidence/N23_CHAIN_RECORD.json', 'this runner (via the runtime harness)'),
        'render': row(render_record, 'evidence/N23_RENDER_FIXTURE.json', 'this runner (via the runtime harness)'),
        'determinism': determinism,
        'budgets': budgets,
        'layer': layer,
        'budget_effect': effect,
        'digests': digest_bundle(),
        'manifest': {
            'output_bytes': manifest.get('output_bytes'),
            'output_sha256': manifest.get('output_sha256'),
            'build_id': manifest.get('build_id'),
            'grading_layer': manifest.get('grading_layer'),
        },
        'commands': [gate['command'], classification['command'], runtime['command']],
    }


def build_record(collected: dict[str, Any]) -> dict[str, Any]:
    gate = collected['gate']
    classification = collected['classification']
    runtime = collected['runtime']
    digests = collected['digests']
    statuses = [gate['status'], classification['status'], runtime['status'], digests['_status']]
    if 'FAIL' in statuses:
        status = 'FAIL'
    elif 'PENDING' in statuses:
        status = 'PENDING'
    else:
        status = 'PASS'
    pending_reasons = []
    for label, entry in (('grading_gate', gate), ('classification_sweep', classification),
                         ('runtime_harness', runtime)):
        if entry['status'] == 'PENDING':
            pending_reasons.append({
                'row': label,
                'owner': entry.get('owner', 'a parallel N23 subagent'),
                'reason': entry.get('reason') or (entry.get('stderr') or entry.get('stdout') or '')[:400],
            })
    if digests['_status'] == 'PENDING':
        pending_reasons.append({
            'row': 'digests',
            'owner': 'parallel N23 subagents / the official compile',
            'reason': 'missing: ' + ', '.join(digests['_missing']),
        })
    return {
        'schema_version': 1,
        'owner': 'N23',
        'status': status,
        'contract': 'docs/GRADING_FORMAT.md (frozen 2026-11-19)',
        'policy_label': 'PROPOSED training policy (N23): the 100-point scale, the slot-point weights, '
                        'the partial-credit reading and the classification priorities are this '
                        'simulator\'s declarations. The 2025 programme fixes none of them.',
        'gates': {'grading_gate': gate, 'classification_sweep': classification},
        'classification': {
            'status': classification['status'],
            'command': classification['command'],
            'table': collected['classification_table'],
        },
        'runtime': {
            'command': runtime['command'],
            'status': runtime['status'],
            'record': 'evidence/N23_RUNTIME_RECORD.json',
            'forms': collected['runtime_forms'],
            'checks': collected['runtime_checks'],
            'smoke': collected['runtime_smoke'],
        },
        'determinism': collected['determinism'],
        'chain': collected['chain'],
        'render': collected['render'],
        'batch': collected['runtime_batch'],
        'digests': digests,
        'budgets': collected['budgets'],
        'grading_layer': collected['layer'],
        'budget_effect': collected['budget_effect'],
        'manifest': collected['manifest'],
        'commands': collected['commands'],
        'pending': pending_reasons,
        'notes': [
            'A PENDING status means a parallel-authored child artifact (the grading core, the '
            'classification layer, the score-matrix fixture, the official compile or the rebuilt '
            'manifest) is not in place yet; every pending row names its owner and its reason.',
            'FAIL is reserved for a tool that ran and reported a violation. A missing child is never '
            'a FAIL and never a quiet pass.',
            'The records are timestamp-free: the collection ran twice and the two record digests are '
            'recorded under "parity".',
            'No ceiling is changed here; a ceiling moves only on an exceeded measurement through the '
            'visible RE_BUDGET_HISTORY entry in tools/byte_budget.py.',
        ],
        'not_claimed': [
            'No official examination, grade or proctoring status.',
            'No browser-render, screen-reader, print or instructor acceptance: the render fixture is a '
            'DOM stub for N32, not pixels.',
            'No semantic grading of free text: self-assessed criteria stay pending-external.',
            'No N09 misconception registry: the classification is N23-authored PROPOSED policy over '
            'the frozen engine vocabularies.',
        ],
    }


def source_fingerprint(digests: dict[str, Any]) -> str:
    """One digest over the measured child artifacts (the parity input identity)."""
    rows = sorted(
        ({'path': path, 'sha256': entry.get('sha256'), 'bytes': entry.get('bytes')}
         for path, entry in digests.items() if not path.startswith('_')),
        key=lambda row: row['path'])
    return sha256_bytes(canonical_json_bytes(rows))


def changed_inputs(first: dict[str, Any], second: dict[str, Any]) -> list[str]:
    changed = []
    for path in sorted(set(first) | set(second)):
        if path.startswith('_'):
            continue
        if (first.get(path) or {}).get('sha256') != (second.get(path) or {}).get('sha256'):
            changed.append(path)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--once', action='store_true', help='skip the second collection run (parity is not proven)')
    args = parser.parse_args(argv)

    first = collect_once()
    core = build_record(first)
    core_bytes = canonical_json_bytes(core)
    first_digest = sha256_bytes(core_bytes)
    first_fingerprint = source_fingerprint(first['digests'])

    parity: dict[str, Any]
    if args.once:
        parity = {
            'mode': 'single-run',
            'identical': None,
            'status': 'PENDING',
            'record_digests': [first_digest],
            'reason': '--once skips the second collection; the two-run parity is not proven in this run',
        }
    else:
        second = collect_once()
        second_core = build_record(second)
        second_bytes = canonical_json_bytes(second_core)
        second_digest = sha256_bytes(second_bytes)
        second_fingerprint = source_fingerprint(second['digests'])
        identical = first_digest == second_digest and core_bytes == second_bytes
        tree_changed = first_fingerprint != second_fingerprint
        changed = changed_inputs(first['digests'], second['digests']) if tree_changed else []
        if identical:
            parity_status = 'PASS'
            reason = None
        elif tree_changed:
            # A sibling subagent was writing an artifact between the two runs: parity is
            # not proven, but the cause is named. Never a quiet pass, never a false FAIL.
            parity_status = 'PENDING'
            reason = ('the measured tree changed between the two runs (a parallel N23 artifact was '
                      'being written): ' + ', '.join(changed) + '; re-run on a stable tree')
        else:
            parity_status = 'FAIL'
            reason = 'the two collection runs produced different records from identical inputs'
        parity = {
            'mode': 'two-run-same-invocation',
            'identical': identical,
            'status': parity_status,
            'record_digests': [first_digest, second_digest],
            'input_fingerprints': [first_fingerprint, second_fingerprint],
            'changed_inputs': changed,
            'reason': reason,
            'note': 'The same two-invocation discipline n22_corpus.py documents; running the runner '
                    'twice as separate invocations must produce the same file, which is why no '
                    'timestamp is written anywhere.',
        }
        if parity_status == 'FAIL':
            core['status'] = 'FAIL'
        elif parity_status == 'PENDING' and core['status'] != 'FAIL':
            core['status'] = 'PENDING'

    record = dict(core)
    record['parity'] = parity
    if parity['status'] == 'FAIL':
        record['status'] = 'FAIL'
    elif parity['status'] == 'PENDING' and record['status'] != 'FAIL':
        record['status'] = 'PENDING'

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    write_json(out, record)

    print(json.dumps({
        'status': record['status'],
        'out': str(out),
        'bytes': out.stat().st_size,
        'sha256': sha256_file(out),
        'gates': {name: entry['status'] for name, entry in record['gates'].items()},
        'runtime': record['runtime']['status'],
        'digests': record['digests']['_status'],
        'parity': parity['status'],
        'pending': record['pending'],
        'budget_projection': {
            'artifact_bytes': record['budget_effect']['measured_artifact_total_bytes'],
            'projected_artifact_bytes': record['budget_effect']['projected_artifact_total_bytes'],
            'projected_overrun_bytes': record['budget_effect']['projected_artifact_overrun_bytes'],
            're_budget_required_after_merge_build': record['budget_effect']['re_budget_required_after_merge_build'],
        },
    }, ensure_ascii=False, indent=2))
    return 0 if record['status'] == 'PASS' else (1 if record['status'] == 'FAIL' else 3)


if __name__ == '__main__':
    raise SystemExit(main())
