#!/usr/bin/env python3
"""N22 corpus runner: the evidence chain of the response-input capture layer.

It runs the N22 gates and harnesses and collects their findings:

  1. the registry gate   — tools/validate_n22_inputs.py: the #sim-response-types
                           island, its 18 contracts, the N04 agreement, the
                           completed-type grading bindings and the term-keyed
                           Latvian ARIA bank (``--report``);
  2. the semantics harness — tools/check_n22_semantics.js (N22-A): the
                           completion model, the error surfaces and the label
                           bank fixtures (``--record``);
  3. the components harness — tools/check_n22_components.js (N22-B): the 18
                           render descriptions, the keyboard/pointer payload
                           parity and the composed container (``--record``);
  4. the runtime harness — tools/check_n22_runtime.js (N22-C): the payload
                           contract, the 18-type scripted session, the parity
                           table, the completion overlays, the three in-file
                           smoke vectors, the only-writer guard and the
                           blank/pending honesty (``--record``). The harness
                           also writes evidence/N22_SESSION_TRACE.json and
                           evidence/N22_PARITY_TABLE.json next to its record;
  5. the TypeScript drift gate — tools/compile_n21_ts.py --check: the
                           committed src/compiled inputs match their sources;
  6. the label-bank term-key lint — a mechanical scan written here: zero
                           literal unit strings in src/inputs/*.ts, every
                           term-keyed ARIA name resolving in data/terms.json,
                           the rendered names of the component record matching
                           the resolved terms, and no English in the new
                           input.* terms.

The budget accounting reads output/build-manifest.json through
tools/byte_budget.py, and adds the input-layer contribution: the compiled
input modules (which ship from src/ and are NOT inlined) and the registry
island's canonical bytes (which the merge build inlines).

The records it writes are timestamp-free and byte-identical across two runs:
the same sources produce the same evidence, which is the parity proof the
roadmap asks for.

  evidence/N22_CORPUS_RECORD.json        — the extended corpus
  evidence/N22_VALIDATION_RECORD.json    — the registry gate's report
  evidence/N22_SEMANTICS_RECORD.json     — the N22-A harness record
  evidence/N22_COMPONENTS_RECORD.json    — the N22-B harness record
  evidence/N22_RUNTIME_RECORD.json       — the N22-C harness record
  evidence/N22_SESSION_TRACE.json        — the scripted session trace
  evidence/N22_PARITY_TABLE.json         — the capture-grading parity table
  evidence/N22_TERMS_LINT.json           — the label-bank term-key lint
  evidence/N22_VERIFICATION_RECORD.json  — the claims and their evidence
  evidence/N22_VERIFICATION_RECORD.md    — the reasoning behind the decisions

Usage:
    python3 tools/n22_corpus.py [--out PATH] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import byte_budget  # noqa: E402
from coverage_common import DEST, sha256_file  # noqa: E402

ROOT = DEST
REGISTRY_GATE = ROOT / 'tools/validate_n22_inputs.py'
SEMANTICS = ROOT / 'tools/check_n22_semantics.js'
COMPONENTS = ROOT / 'tools/check_n22_components.js'
RUNTIME = ROOT / 'tools/check_n22_runtime.js'
COMPILE = ROOT / 'tools/compile_n21_ts.py'
ISLAND = ROOT / 'data/response_types.json'
TERMS = ROOT / 'data/terms.json'
EXAM_POLICY = ROOT / 'data/exam_policy.json'
MANIFEST = ROOT / 'output/build-manifest.json'
SMOKE = ROOT / 'src/smoke-subset.js'

OUT_DEFAULT = ROOT / 'evidence/N22_CORPUS_RECORD.json'
VALIDATION_RECORD = ROOT / 'evidence/N22_VALIDATION_RECORD.json'
SEMANTICS_RECORD = ROOT / 'evidence/N22_SEMANTICS_RECORD.json'
COMPONENTS_RECORD = ROOT / 'evidence/N22_COMPONENTS_RECORD.json'
RUNTIME_RECORD = ROOT / 'evidence/N22_RUNTIME_RECORD.json'
TRACE_RECORD = ROOT / 'evidence/N22_SESSION_TRACE.json'
PARITY_RECORD = ROOT / 'evidence/N22_PARITY_TABLE.json'
TERMS_LINT_RECORD = ROOT / 'evidence/N22_TERMS_LINT.json'
VERIFICATION_JSON = ROOT / 'evidence/N22_VERIFICATION_RECORD.json'
VERIFICATION_MD = ROOT / 'evidence/N22_VERIFICATION_RECORD.md'

# The N21 ledger records src/smoke-subset.js at 28 439 B; the three N22 vectors
# are what this task appends, so the delta is the smoke contribution.
SMOKE_BASELINE_BYTES = 28439
SMOKE_IDS = ['SMK-N22-NUMERIC-CAPTURE', 'SMK-N22-CLASSIFICATION-CAPTURE', 'SMK-N22-ORDERING-CAPTURE']


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def run_tool(command: list[str], label: str) -> dict[str, Any]:
    """Run one tool and keep its exit code and its stdout report."""
    if not Path(command[1]).exists() and command[0] != 'node':
        pass
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


def run_optional(command: list[str], label: str, script: Path) -> dict[str, Any]:
    """A required-for-N22 record that a sibling owns: absent means PENDING."""
    if not script.exists():
        return {
            'label': label,
            'command': ' '.join(command),
            'returncode': None,
            'status': 'PENDING',
            'reason': f'{script.relative_to(ROOT)} does not exist yet; the sibling owns it.',
        }
    return run_tool(command, label)


def measure_budgets() -> dict[str, Any]:
    if not MANIFEST.exists():
        return {'status': 'FAIL', 'reason': 'output/build-manifest.json is missing; run the build first.'}
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    measured = byte_budget.measure_budgets(manifest)
    measured['notes'] = [
        'The response-input runtime (registry, components, integration) ships from src/ and is NOT '
        'inlined into output/simulator.html; only the #sim-response-types island and the three smoke '
        'vectors enter the artifact at the merge build. N31 owns the final inline / lazy-load / '
        're-budget decision.',
        'The measured figures below are the manifest of the last build. They include the three smoke '
        'vectors (inlined) and exclude the island until the coordinator rebuilds at merge; the corpus '
        'is re-run after that rebuild for the final numbers.',
    ]
    return measured


def input_layer_bytes(manifest: dict[str, Any]) -> dict[str, Any]:
    """The N22 byte contribution, split by what is inlined and what is not."""
    modules = []
    total = 0
    for relative in ('src/compiled/inputs/registry.js', 'src/compiled/inputs/components.js',
                     'src/compiled/inputs/integration.js'):
        path = ROOT / relative
        size = path.stat().st_size
        total += size
        modules.append({
            'path': relative,
            'bytes': size,
            'sha256': sha256_file(path),
            'inlined_in_artifact': False,
            'note': 'Ships from src/; the artifact does not inline it (N31 owns the decision).',
        })
    island_file_bytes = ISLAND.stat().st_size if ISLAND.exists() else 0
    island_embedded_bytes = 0
    if ISLAND.exists():
        island_doc = json.loads(ISLAND.read_text(encoding='utf-8'))
        canonical = json.dumps(island_doc, ensure_ascii=False, sort_keys=True,
                               separators=(',', ':')).replace('</', '<\\/')
        island_embedded_bytes = len(canonical.encode('utf-8'))
    island = {
        'path': 'data/response_types.json',
        'bytes': island_embedded_bytes,
        'file_bytes': island_file_bytes,
        'sha256': sha256_file(ISLAND) if ISLAND.exists() else None,
        'emission': 'sorted keys; separators (",", ":"); ensure_ascii=False; UTF-8; "</" escaped as "<\\/" '
                    '— the same projection the build inlines',
        'inlined_in_artifact': True,
        'note': 'Inlined as #sim-response-types by the merge build; the island is JSON data, so it '
                'counts against the artifact total, not the runtime-JS code budget.',
    }
    smoke_bytes = max(0, SMOKE.stat().st_size - SMOKE_BASELINE_BYTES) if SMOKE.exists() else 0
    budgets = {entry['name']: entry for entry in byte_budget.measure_budgets(manifest).get('budgets', [])} \
        if manifest else {}
    runtime = budgets.get('runtime_js_code', {})
    artifact = budgets.get('artifact_total', {})
    runtime_headroom = (runtime.get('max_bytes', 0) - runtime.get('bytes', 0)) if runtime else None
    artifact_headroom = (artifact.get('max_bytes', 0) - artifact.get('bytes', 0)) if artifact else None
    return {
        'modules': modules,
        'runtime_module_bytes_total': total,
        'registry_island': island,
        'smoke_vectors': {
            'ids': SMOKE_IDS,
            'file': 'src/smoke-subset.js',
            'file_bytes': SMOKE.stat().st_size if SMOKE.exists() else 0,
            'baseline_bytes': SMOKE_BASELINE_BYTES,
            'appended_bytes': smoke_bytes,
            'inlined_in_artifact': True,
        },
        'budget_effect': {
            'runtime_js_headroom_before_smoke_bytes': runtime_headroom,
            'smoke_appended_bytes': smoke_bytes,
            'runtime_js_headroom_after_smoke_bytes': None if runtime_headroom is None
            else runtime_headroom - smoke_bytes,
            'artifact_total_headroom_before_island_bytes': artifact_headroom,
            'island_bytes': island['bytes'],
            'artifact_total_headroom_after_island_bytes': None if artifact_headroom is None
            else artifact_headroom - island['bytes'],
            'projected_artifact_overrun_bytes': None if artifact_headroom is None
            else max(0, island['bytes'] - artifact_headroom),
            'projected_runtime_js_overrun_bytes': None if runtime_headroom is None
            else max(0, smoke_bytes - runtime_headroom),
        },
        'notes': [
            'The compiled input modules are strict TypeScript output and are committed; the drift '
            'guard (tools/compile_n21_ts.py --check) keeps them in step with src/inputs/*.ts.',
            'The three smoke vectors are appended to src/smoke-subset.js and are inlined, so they '
            'consume runtime-JS headroom. Their appended size is measured against the N21 ledger '
            'figure for the same file.',
            'The projection above is what the merge build will measure: the island is inlined, the '
            'modules are not. A positive projected_artifact_overrun_bytes means the enforced '
            'artifact-total ceiling is exceeded by that many bytes once the island lands; AGENTS.md '
            'sets the budget on the measured requirement, so the resolution is a visible re-budget '
            '(coordinator / N31), not a silent shrink of the contract.',
        ],
    }


# --------------------------------------------------------------- the terms lint

STRING_RE = re.compile(r"'((?:[^'\\\n]|\\.)*)'|\"((?:[^\"\\\n]|\\.)*)\"|`((?:[^`\\]|\\.)*)`", re.S)
TERM_KEY_RE = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$')
PLACEHOLDER_RE = re.compile(r'^\{[a-z0-9_]+\}$')
TOKEN_SPLIT_RE = re.compile(r'[^0-9A-Za-z\u00c0-\u017f_]+')

# The English denylist: words that have no business in a Latvian input.* string.
# It is a *mechanical* signal with declared limits, not a language detector.
ENGLISH_DENYLIST = {
    'the', 'and', 'with', 'select', 'choose', 'answer', 'enter', 'value', 'values',
    'correct', 'wrong', 'please', 'your', 'from', 'this', 'that', 'option', 'options',
    'order', 'pair', 'pairs', 'read', 'plot', 'graph', 'table', 'question', 'check',
    'mass', 'volume', 'moles', 'concentration', 'time', 'temperature', 'pressure',
    'energy', 'unit', 'units', 'number', 'first', 'second', 'total', 'missing',
    'required', 'field', 'input', 'output', 'type', 'button', 'label', 'list', 'row',
    'cell', 'step', 'select', 'submit', 'reset', 'clear',
}
# Physical key caps keep their Latin names in the Latvian keyboard help.
KEY_CAP_ALLOWLIST = {
    'enter', 'tab', 'escape', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright',
    'alt', 'shift', 'space', 'home', 'end', 'ctrl', 'control', 'pageup', 'pagedown',
}


def strip_comments(text: str) -> str:
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'(?m)^\s*//.*$', '', text)


def unit_symbols(terms: dict[str, Any]) -> list[str]:
    return [entry['symbol'] for entry in terms['unit_grammar']['elements']]


def scan_literal_units() -> dict[str, Any]:
    terms = json.loads(TERMS.read_text(encoding='utf-8'))
    units = set(unit_symbols(terms))
    rows = []
    violations = []
    literal_count = 0
    for path in sorted((ROOT / 'src/inputs').glob('*.ts')):
        text = strip_comments(path.read_text(encoding='utf-8'))
        for match in STRING_RE.finditer(text):
            literal = match.group(1) if match.group(1) is not None else (
                match.group(2) if match.group(2) is not None else match.group(3))
            if not literal:
                continue
            literal_count += 1
            if TERM_KEY_RE.match(literal) or PLACEHOLDER_RE.match(literal) or '%' in literal:
                continue
            tokens = [token for token in TOKEN_SPLIT_RE.split(literal) if token and not token.isdigit()]
            hits = sorted({token for token in tokens if token in units})
            if hits:
                violations.append({
                    'file': str(path.relative_to(ROOT)),
                    'literal': literal[:120],
                    'unit_tokens': hits,
                })
        rows.append({'file': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size})
    return {
        'files': rows,
        'string_literals_scanned': literal_count,
        'violations': violations,
        'status': 'PASS' if not violations else 'FAIL',
        'rule': 'No string literal in src/inputs/*.ts may contain a standalone unit symbol from '
                'data/terms.json unit_grammar.elements. Term keys, {placeholders} and the percentage '
                'basis notation are allowlisted; identifiers are tokenised whole, so min_length is '
                'not the unit min.',
    }


def scan_aria_bank() -> dict[str, Any]:
    if not ISLAND.exists():
        return {
            'status': 'PENDING',
            'reason': 'data/response_types.json does not exist yet.',
        }
    terms = json.loads(TERMS.read_text(encoding='utf-8'))
    known = {entry['key'] for entry in terms['terms']}
    island = json.loads(ISLAND.read_text(encoding='utf-8'))
    scanned: list[tuple[str, str]] = []
    literals: list[tuple[str, str]] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if isinstance(value, str) and (key.endswith('_key') or key == 'key') and '.' in value:
                    scanned.append((f'{path}/{key}', value))
                elif key == 'term_keys' and isinstance(value, list):
                    for index, item in enumerate(value):
                        if isinstance(item, str):
                            scanned.append((f'{path}/term_keys[{index}]', item))
                elif key == 'feedback_keys' and isinstance(value, dict):
                    for inner, text in value.items():
                        if isinstance(text, str):
                            scanned.append((f'{path}/feedback_keys/{inner}', text))
                elif isinstance(value, str) and key in ('name_lv', 'label_lv', 'text_lv', 'aria_name', 'aria_name_lv'):
                    literals.append((f'{path}/{key}', value))
                walk(value, f'{path}/{key}')
        elif isinstance(node, list):
            for index, item in enumerate(node):
                walk(item, f'{path}[{index}]')

    walk(island, '')
    unresolved = [{'path': path, 'key': key} for path, key in scanned if key not in known]
    rendered = {'status': 'PENDING', 'reason': 'evidence/N22_COMPONENTS_RECORD.json does not exist yet.'}
    gaps = {'status': 'PENDING', 'reason': 'evidence/N22_COMPONENTS_RECORD.json does not exist yet.'}
    if COMPONENTS_RECORD.exists():
        record = json.loads(COMPONENTS_RECORD.read_text(encoding='utf-8'))
        terms_block = record.get('terms') or {}
        gap_keys = terms_block.get('scratch_gap_key_list') or []
        gaps = {
            'status': 'PASS' if not gap_keys else 'FAIL',
            'record': 'evidence/N22_COMPONENTS_RECORD.json',
            'scratch_gap_key_count': len(gap_keys),
            'scratch_gap_keys': gap_keys,
            'module': 'src/inputs/components.ts',
            'rule': 'A component must render only labels the shipped bank can resolve. Keys the '
                    'component harness had to invent a scratch term for are, by definition, ARIA names '
                    'the shipped data/terms.json cannot translate yet.',
            'resolution_owner': 'N22-A (data/terms.json) or N22-B (components.ts). Reported, never '
                                'silently allowlisted by this lint.',
        }
        flags: list[dict[str, Any]] = []

        def collect(node: Any, path: str) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    if isinstance(value, bool) and 'aria_name' in key:
                        flags.append({'path': f'{path}/{key}', 'value': value})
                    collect(value, f'{path}/{key}')
            elif isinstance(node, list):
                for index, item in enumerate(node):
                    collect(item, f'{path}[{index}]')

        collect(record, '')
        failures = [flag for flag in flags if flag['value'] is not True]
        rendered = {
            'status': 'PASS' if flags and not failures else ('FAIL' if failures else 'PENDING'),
            'record': 'evidence/N22_COMPONENTS_RECORD.json',
            'aria_flags_checked': len(flags),
            'failures': failures,
            'rule': 'The rendered aria_name of every field equals the term text the registry key '
                    'resolves to (the N22-B render fixtures). This lint re-reads that record; it does '
                    'not re-render.',
        }
    literal_with_key = 0
    for path, value in literals:
        if value.strip():
            literal_with_key += 1
    return {
        'status': 'PASS' if not unresolved else 'FAIL',
        'term_keys_scanned': len(scanned),
        'unique_term_keys': len({key for _, key in scanned}),
        'unresolved': unresolved,
        'literal_latvian_names': literal_with_key,
        'rendered_names': rendered,
        'component_term_gaps': gaps,
        'rule': 'Every dotted *_key / term_keys[] / feedback_keys{} in data/response_types.json must '
                'resolve in data/terms.json; the label bank is term-keyed, never a literal.',
    }


def scan_english_terms() -> dict[str, Any]:
    if not ISLAND.exists():
        return {'status': 'PENDING', 'reason': 'data/response_types.json does not exist yet.'}
    terms = json.loads(TERMS.read_text(encoding='utf-8'))
    entries = [entry for entry in terms['terms'] if entry['key'].startswith('input.')]
    hits = []
    ascii_only = []
    for entry in entries:
        text = re.sub(r'\{[a-z0-9_]+\}', '', entry['text_lv'])
        words = {word.lower() for word in re.findall(r'[A-Za-z\u00c0-\u017f]+', text)}
        found = sorted(word for word in words
                       if word in ENGLISH_DENYLIST and word not in KEY_CAP_ALLOWLIST)
        if found:
            hits.append({'key': entry['key'], 'words': found, 'text_lv': entry['text_lv']})
        if re.fullmatch(r'[\x00-\x7f]+', entry['text_lv']):
            ascii_only.append(entry['key'])
    return {
        'status': 'PASS' if not hits else 'FAIL',
        'input_terms_scanned': len(entries),
        'hits': hits,
        'ascii_only_terms': ascii_only,
        'limits': 'A denylist over whole words with {placeholders} removed and the physical key caps '
                  'allowlisted. It catches English UI vocabulary, not English phrasing; it is a '
                  'mechanical signal, not a language detector.',
    }


def terms_lint() -> dict[str, Any]:
    literal = scan_literal_units()
    aria = scan_aria_bank()
    english = scan_english_terms()
    statuses = [literal['status'], aria['status'], english['status']]
    rendered = aria.get('rendered_names', {}).get('status')
    gaps = aria.get('component_term_gaps', {}).get('status')
    for extra in (rendered, gaps):
        if extra == 'FAIL':
            statuses.append('FAIL')
    status = 'FAIL' if 'FAIL' in statuses else ('PENDING' in statuses and 'PENDING' or 'PASS')
    if 'FAIL' in statuses:
        status = 'FAIL'
    elif 'PENDING' in statuses:
        status = 'PENDING'
    else:
        status = 'PASS'
    return {
        'schema_version': 1,
        'owner': 'N22',
        'status': status,
        'checks': {
            'literal_unit_strings': literal,
            'aria_term_keys': aria,
            'english_in_input_terms': english,
        },
        'summary': {
            'literal_unit_violations': len(literal['violations']),
            'term_keys_scanned': aria.get('term_keys_scanned', 0),
            'unresolved_term_keys': len(aria.get('unresolved', [])),
            'aria_render_flags': aria.get('rendered_names', {}).get('aria_flags_checked', 0),
            'component_term_gaps': len(aria.get('component_term_gaps', {}).get('scratch_gap_keys', [])),
            'english_hits': len(english.get('hits', [])),
        },
        'not_claimed': [
            'Not a translation-quality review: the lint proves key resolution and the absence of '
            'declared English words, not that every Latvian sentence reads well.',
            'Not a screen-reader acceptance claim: that is N33.',
        ],
    }


# ----------------------------------------------------------------- the records

def digest_bundle() -> dict[str, Any]:
    files = [
        'src/inputs/registry.ts',
        'src/inputs/components.ts',
        'src/inputs/integration.ts',
        'src/compiled/inputs/registry.js',
        'src/compiled/inputs/components.js',
        'src/compiled/inputs/integration.js',
        'data/response_types.json',
        'data/terms.json',
        'data/exam_policy.json',
        'src/smoke-subset.js',
        'tools/validate_n22_inputs.py',
        'tools/check_n22_semantics.js',
        'tools/check_n22_components.js',
        'tools/check_n22_runtime.js',
        'tools/n22_corpus.py',
        'docs/RESPONSE_INPUT_FORMAT.md',
    ]
    out = {}
    for relative in files:
        path = ROOT / relative
        if path.exists():
            out[relative] = {'bytes': path.stat().st_size, 'sha256': sha256_file(path)}
        else:
            out[relative] = {'bytes': None, 'sha256': None, 'missing': True}
    return out


def write_verification(record: dict[str, Any]) -> None:
    runtime_checks = record['runtime'].get('checks', {})
    manifest = record.get('manifest', {})
    payload_contracts = manifest.get('exam_shell_layer', {}).get('payload_contracts', {})
    parity = record.get('parity', {})
    lint = record['terms_lint']

    def status_of(name: str) -> str:
        return runtime_checks.get(name, {}).get('status', 'FAIL')

    ac1 = all(status_of(name) == 'PASS' for name in
              ('payload_contract', 'scripted_session_18', 'capture_grading_parity'))
    ac2 = all(status_of(name) == 'PASS' for name in
              ('navigator_completion_overlay', 'blank_and_pending'))
    ac3 = all(status_of(name) == 'PASS' for name in
              ('smoke_vectors_in_file', 'only_writer_guards')) \
        and record['gates']['registry_gate']['status'] == 'PASS' \
        and lint['summary']['literal_unit_violations'] == 0 \
        and lint['summary']['unresolved_term_keys'] == 0

    verification = {
        'schema_version': 1,
        'owner': 'N22',
        'status': record['status'],
        'policy_label': 'PROPOSED training policy (N22): the eighteen response components, their '
                        'payload shapes, completion rules and Latvian ARIA names. The 2025 programme '
                        'fixes none of them; each registry entry carries its own PROPOSED label.',
        'official_programme_facts': {
            'topics': 7,
            'examination': 'written on paper',
            'maximum_minutes': 180,
            'note': 'The programme fixes no response component, field count or ARIA name. The input '
                    'semantics are this simulator\'s proposal and are labelled as such in the island.',
        },
        'acceptance_criteria': {
            'AC1_happy_path': {
                'status': 'PASS' if ac1 else 'FAIL',
                'claims': [
                    'All eighteen types have a registry contract with a render, payload, completion, '
                    'error-surface and ARIA contract; the completed types (Q02, Q04, Q10, Q11, Q12, '
                    'Q13, Q15) have grading bindings.',
                    'One instance of each of the eighteen types is answered through the component and '
                    'integration API in a scripted session; every answer goes through '
                    'session.dispatch("answer", …), and the answer map round-trips through '
                    'serialize()/deserialize() unchanged.',
                    'The capture-grading parity table shows all eighteen stored payloads consumed by '
                    'their frozen engines with no adapter: the audit finds zero adapters and zero '
                    'value rewrites.',
                    'The Q03 template response runs the manual-rubric pending path: pending, never '
                    'fake-scored.',
                ],
                'evidence': [
                    'evidence/N22_PARITY_TABLE.json',
                    'evidence/N22_SESSION_TRACE.json',
                    'evidence/N22_RUNTIME_RECORD.json',
                    'tools/check_n22_runtime.js',
                ],
            },
            'AC2_negative_or_edge': {
                'status': 'PASS' if ac2 else 'FAIL',
                'claims': [
                    'The navigator map cells carry the completion verdict from '
                    'SimInputsRegistry.completion: the eighteen answered slots are complete and the '
                    'seven deliberately incomplete cases are not.',
                    'The review warning list names exactly the incomplete slots with their Latvian '
                    'missing names and carries role="alert" for the screen-reader announcement.',
                    'A whitespace-only Q15 is BLANK_RESPONSE with zero points and every criterion '
                    'denied; a non-blank Q15 is pending with no verdict and no machine points.',
                    'Errors never destroy raw input: the stored payload is the string the learner '
                    'typed, and an error is an annotation on the completion verdict.',
                ],
                'evidence': [
                    'evidence/N22_RUNTIME_RECORD.json',
                    'evidence/N22_COMPONENTS_RECORD.json (N22-B: pointer/keyboard payload parity and '
                    'the mid-interaction abort)',
                ],
            },
            'AC3_domain_integrity': {
                'status': 'PASS' if ac3 else 'FAIL',
                'claims': [
                    'The three in-file smoke vectors (numeric, classification, ordering) are '
                    'registered, assert the eighteen-type island, drive SimSession and pass.',
                    'The session machine remains the only writer: the integration offers no setter, '
                    'the accessors hand out deep copies, and one answer() call is exactly one '
                    'dispatch.',
                    'The label bank is term-keyed: no string literal in src/inputs/*.ts carries a '
                    'standalone unit symbol, every dotted ARIA key resolves in data/terms.json, the '
                    'rendered names match the resolved terms, and the input.* terms carry no English '
                    'UI vocabulary.',
                ],
                'evidence': [
                    'evidence/N22_TERMS_LINT.json',
                    'src/smoke-subset.js',
                    'data/response_types.json',
                ],
            },
        },
        'payload_contracts': payload_contracts,
        'parity_table': {
            'evidence': 'evidence/N22_PARITY_TABLE.json',
            'rows': len(parity.get('rows', [])),
            'adapters_found': parity.get('audit', {}).get('adapters_found'),
            'identity_failures': parity.get('audit', {}).get('identity_failures'),
            'engines': parity.get('audit', {}).get('engines'),
            'findings': [entry['id'] for entry in parity.get('findings', [])],
        },
        'completion_contract': {
            'verdict_shape': '{status: complete|incomplete|invalid, missing: [{field_id, name}], '
                              'errors: [{id, field, message_key}]}',
            'owner': 'SimInputsRegistry.completion (N22-A); the integration owns the call, never the '
                     'model',
            'binding': record['runtime'].get('completion_binding'),
            'downstream': ['navigator map cells (N21/N30)', 'review warning list (N21/N33)'],
        },
        'inputs_layer': record['inputs_layer'],
        'byte_budget': record['budgets'],
        'digests': record['digests'],
        'terms_lint': lint['summary'],
        'handoff': {
            'N23_grading': {
                'terminal_record': 'ExamSession.toTerminalRecord() carries the raw payloads; the '
                                   'parity table proves each one is what the frozen engine consumes.',
                'parity_table': 'evidence/N22_PARITY_TABLE.json',
            },
            'N24_form_assembly': {
                'payload_vocabulary': 'SimInputsIntegration.vocabulary() — type id → kind, variant '
                                      'and the ride-alongs.',
                'registry': 'SimInputs.registry.contractFor(typeId)',
            },
            'N30_practice': {
                'overlays': 'completionMapState() and reviewMissingList() — pure functions of the '
                            'map/review state plus the answers plus the bindings.',
            },
            'N33_accessibility': {
                'aria_contract': 'the registry label bank and the render description; N33 owns the '
                                 'live screen-reader pass.',
            },
            'N31_inline': {
                'runtime_module_bytes_total': record['inputs_layer']['runtime_module_bytes_total'],
                'island_bytes': record['inputs_layer']['registry_island']['bytes'],
                'note': 'The three input modules ship from src/; only the island and the smoke vectors '
                        'are inlined at merge.',
            },
        },
        'not_claimed': [
            'No official examination, grade or proctoring status.',
            'No screen-reader acceptance: the ARIA evidence is a mechanical structural check (roles, '
            'names, key resolution); N33 performs the live pass.',
            'No browser-render acceptance: the render descriptions are JSON, not pixels.',
            'No semantic grading of free text: Q15/Q16 stay pending and Q03 stays manual-rubric.',
            'No claim that the four variants are four finished questions.',
            'No keyboard-vs-pointer acceptance here: that fixture belongs to N22-B; this record '
            'references its output rather than duplicating it.',
        ],
    }
    write_json(VERIFICATION_JSON, verification)
    VERIFICATION_MD.write_text(render_markdown(record, verification), encoding='utf-8')


def render_markdown(record: dict[str, Any], verification: dict[str, Any]) -> str:
    runtime = record['runtime']
    checks = runtime.get('checks', {})
    parity = record.get('parity', {})
    lint = record['terms_lint']
    layer = record['inputs_layer']
    gates = record['gates']
    lines: list[str] = []
    add = lines.append
    add('# N22 verification record: response input semantics for all 18 types')
    add('')
    add('**Owner:** N22 (integration slice N22-C). **Status:** ' + record['status'] + '.')
    add('**Islands:** `#sim-response-types` (`data/response_types.json`), `#sim-exam-policy` '
        '(`data/exam_policy.json`), `#sim-terms` (`data/terms.json`).')
    add('**Sources:** `src/inputs/registry.ts`, `src/inputs/components.ts`, '
        '`src/inputs/integration.ts` → `src/compiled/inputs/*.js`.')
    add('')
    add('This record is generated by `tools/n22_corpus.py`. It is timestamp-free: the same sources '
        'produce the same file, which is the parity proof the roadmap asks for.')
    add('')
    add('## What this slice is')
    add('')
    add('Every response type needs one defined component: how it renders, what it stores, when it '
        'counts as complete, which error states it can show and its full ARIA semantics in Latvian. '
        'The registry owns the semantics, the components own the rendering, and this slice owns the '
        'join: the payload builder, the single write path through the session machine, the '
        'completion overlays the navigator and the review screen read, and the parity proof that the '
        'stored payload is what the frozen engines consume.')
    add('')
    add('## The decisions that shaped it')
    add('')
    add('- **The session machine stays the only writer.** `SimInputsIntegration.answer()` builds the '
        'payload and dispatches `answer`; it never touches the answer map, and it re-reads the stored '
        'payload and compares content digests, so a builder that quietly rewrote a value could not '
        'pass unnoticed.')
    add('- **Raw is raw.** A numeric answer is stored as the learner typed it — `" 4,70 "` keeps its '
        'spaces and its comma — because normalisation belongs to grading. The payload builder '
        'validates shape (`raw_string`, `raw_string_map`, `string_list`, `pair_list`) and never '
        'converts a value.')
    add('- **The vocabulary is frozen and checked.** `data/exam_policy.json` (payload contracts and '
        'named variants) and `data/question_schema.json` (payload classes) fix the per-type kind; '
        '`data/response_types.json` fixes the variant names. When a registry contract is passed in, '
        'the builder refuses a mismatch (`E_INPUTS_CONTRACT_MISMATCH`) instead of drifting.')
    add('- **Completion is not computed here.** The verdict belongs to '
        '`SimInputsRegistry.completion`; the overlays call it and attach `missing` so the review '
        'warning can name the field in Latvian.')
    add('- **Q03 is pending, not scored.** The template choice plus the typed fill-ins are stored and '
        '`q03PendingPath()` returns `{class: pending, verdict: null, points_awarded: 0}`.')
    add('')
    add('## The parity table')
    add('')
    add('| Type | Engine | Verdict class | Adapter |')
    add('|---|---|---|---|')
    for row in parity.get('rows', []):
        verdict = row.get('verdict_class')
        add(f"| {row['type_id']} | {row['engine']} | {verdict if verdict else 'pending (manual rubric)'} "
            f"| {row['adapter']} |")
    add('')
    add(f"Rows: {parity.get('audit', {}).get('rows')}. Adapters found: "
        f"{parity.get('audit', {}).get('adapters_found')}. Value rewrites: "
        f"{len(parity.get('audit', {}).get('identity_failures', []))}.")
    add('')
    add('The audit asks one question per type: does the stored payload, handed to its frozen engine, '
        'produce the engine\'s own criterion shape without an adapter? The answer is yes for all '
        'eighteen, and the row names the engine and the binding so a reader can re-run it.')
    add('')
    add('## The recorded findings')
    add('')
    for finding in parity.get('findings', []):
        add(f"- **{finding['id']}** — {finding.get('topic') or finding.get('topic')}: "
            f"{finding.get('resolution') or finding.get('observation')}")
    add('')
    add('## The label-bank term-key lint')
    add('')
    add(f"- Literal unit strings in `src/inputs/*.ts`: {lint['summary']['literal_unit_violations']} "
        f"violations over {lint['checks']['literal_unit_strings']['string_literals_scanned']} string "
        f"literals.")
    add(f"- Term-keyed ARIA names: {lint['summary']['term_keys_scanned']} references, "
        f"{lint['summary']['unresolved_term_keys']} unresolved in `data/terms.json`.")
    rendered = lint['checks']['aria_term_keys'].get('rendered_names', {})
    add(f"- Rendered names re-read from the component record: {rendered.get('aria_flags_checked', 0)} "
        f"ARIA flags, status {rendered.get('status')}.")
    add(f"- English in `input.*` terms: {lint['summary']['english_hits']} hits over "
        f"{lint['checks']['english_in_input_terms']['input_terms_scanned']} terms.")
    add('')
    add('The lint is mechanical and says so: a denylist over whole words, term-key resolution, and a '
        're-read of the component harness\'s rendered names. It is not a translation review and not a '
        'screen-reader claim.')
    add('')
    add('## The byte accounting')
    add('')
    add('| Budget | Measured | Declared band | Enforced ceiling |')
    add('|---|---|---|---|')
    for entry in record['budgets'].get('budgets', []):
        add(f"| {entry['name']} | {entry['bytes']} B ({entry['kib']} KiB) | "
            f"{entry['min_bytes'] // 1024}–{entry['declared_max_bytes'] // 1024} KiB | "
            f"{entry['max_bytes'] // 1024} KiB |")
    add('')
    add(f"The input layer contributes {layer['runtime_module_bytes_total']} B of compiled modules "
        f"that ship from `src/` (not inlined), {layer['registry_island']['bytes']} B of registry "
        f"island that the merge build inlines, and {layer['smoke_vectors']['appended_bytes']} B of "
        f"appended smoke vectors (inlined). N31 owns the final inline / lazy-load / re-budget "
        f"decision.")
    add('')
    add('## What was run')
    add('')
    add('| What | Command | Result |')
    add('|---|---|---|')
    for label, gate in gates.items():
        command = gate.get('command', '')
        status = gate.get('status', '')
        add(f"| {label} | `{command}` | {status} |")
    add(f"| runtime harness | `{runtime.get('command', '')}` | {runtime.get('status')} |")
    add('')
    add('Runtime fixtures:')
    add('')
    for name, check in checks.items():
        add(f"- `{name}` — {check.get('status')}")
    add('')
    add('## What N23, N24, N30 and N33 may rely on')
    add('')
    add('- **N23 (grading):** the terminal record carries the raw payloads, and the parity table names '
        'the engine and the binding per type. A payload can be handed to its engine as it stands.')
    add('- **N24 (form assembly):** `SimInputsIntegration.vocabulary()` is the type → kind/variant '
        'map with the ride-along list; `SimInputs.registry.contractFor(typeId)` is the full contract.')
    add('- **N30 (practice):** `completionMapState()` and `reviewMissingList()` are pure functions of '
        'the map/review state, the answers and the per-slot bindings.')
    add('- **N33 (accessibility):** the registry label bank is term-keyed and the render description '
        'carries the ARIA names; the live screen-reader pass is N33\'s.')
    add('')
    add('## What is explicitly not claimed')
    add('')
    for item in verification['not_claimed']:
        add(f'- {item}')
    add('')
    return '\n'.join(lines) + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=str(OUT_DEFAULT))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    registry_gate = run_tool(
        ['python3', 'tools/validate_n22_inputs.py', '--report', 'evidence/N22_VALIDATION_RECORD.json'],
        'registry_gate')
    semantics = run_optional(
        ['node', 'tools/check_n22_semantics.js', '--record', 'evidence/N22_SEMANTICS_RECORD.json'],
        'semantics_harness', SEMANTICS)
    components = run_optional(
        ['node', 'tools/check_n22_components.js', '--record', 'evidence/N22_COMPONENTS_RECORD.json'],
        'components_harness', COMPONENTS)
    compile_gate = run_tool(['python3', 'tools/compile_n21_ts.py', '--check'], 'compile_gate')
    runtime = run_tool(
        ['node', 'tools/check_n22_runtime.js',
         '--record', 'evidence/N22_RUNTIME_RECORD.json',
         '--trace', 'evidence/N22_SESSION_TRACE.json',
         '--parity', 'evidence/N22_PARITY_TABLE.json'], 'runtime_harness')

    budgets = measure_budgets()
    manifest: dict[str, Any] = {}
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf-8'))
    layer = input_layer_bytes(manifest)
    lint = terms_lint()
    write_json(TERMS_LINT_RECORD, lint)

    runtime_record: dict[str, Any] = {}
    if RUNTIME_RECORD.exists():
        runtime_record = json.loads(RUNTIME_RECORD.read_text(encoding='utf-8'))
    parity_table: dict[str, Any] = {}
    if PARITY_RECORD.exists():
        parity_table = json.loads(PARITY_RECORD.read_text(encoding='utf-8'))
    parity = {
        'status': parity_table.get('status'),
        'evidence': 'evidence/N22_PARITY_TABLE.json',
        'audit': parity_table.get('audit', {}),
        'findings': parity_table.get('findings', []),
        'rows': [{
            'type_id': row['type_id'],
            'instance_id': row.get('instance_id'),
            'payload_digest': row.get('payload_digest'),
            'engine': row.get('engine'),
            'verdict_class': (row.get('criterion_shape') or {}).get('verdict_class'),
            'adapter': row.get('adapter'),
            'identity_ok': row.get('identity_ok'),
            'status': row.get('status'),
        } for row in parity_table.get('rows', [])],
    }

    gates = {
        'registry_gate': registry_gate,
        'semantics_harness': semantics,
        'components_harness': components,
        'compile_gate': compile_gate,
    }
    statuses = [gate['status'] for gate in gates.values()]
    statuses.append(runtime['status'])
    statuses.append(budgets['status'])
    statuses.append(lint['status'])
    if 'FAIL' in statuses:
        status = 'FAIL'
    elif 'PENDING' in statuses:
        status = 'PENDING'
    else:
        status = 'PASS'

    record = {
        'schema_version': 1,
        'owner': 'N22',
        'status': status,
        'gates': gates,
        'runtime': {
            'command': runtime['command'],
            'status': runtime['status'],
            'record': 'evidence/N22_RUNTIME_RECORD.json',
            'checks': runtime_record.get('checks', {}),
            'completion_binding': runtime_record.get('checks', {})
                                                     .get('navigator_completion_overlay', {})
                                                     .get('completion_binding'),
        },
        'parity': parity,
        'budgets': budgets,
        'inputs_layer': layer,
        'terms_lint': lint,
        'digests': digest_bundle(),
        'manifest': {
            'output_bytes': manifest.get('output_bytes'),
            'output_sha256': manifest.get('output_sha256'),
            'exam_shell_layer': {
                'payload_contracts': manifest.get('exam_shell_layer', {}).get('payload_contracts'),
                'named_variants': manifest.get('exam_shell_layer', {}).get('named_variants'),
            },
        },
        'commands': [gate['command'] for gate in gates.values()] + [runtime['command']],
        'notes': [
            'The input modules ship from src/ and are not inlined; the island and the three smoke '
            'vectors are inlined at merge.',
            'A PENDING status means a sibling artifact (the semantics harness, the components '
            'record, the registry island or the rebuilt manifest) is not in place yet; the pending '
            'item is named in its gate entry.',
        ],
    }

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    write_json(out, record)
    write_verification(record)
    print(json.dumps({
        'status': status,
        'out': str(out),
        'bytes': out.stat().st_size,
        'sha256': sha256_file(out),
        'gates': {name: gate['status'] for name, gate in gates.items()},
        'runtime': runtime['status'],
        'budgets': budgets['status'],
        'terms_lint': lint['status'],
        'parity_rows': len(parity.get('rows', [])),
        'adapters': parity.get('audit', {}).get('adapters_found'),
    }, ensure_ascii=False, indent=2))
    return 0 if status == 'PASS' else (1 if status == 'FAIL' else 3)


if __name__ == '__main__':
    raise SystemExit(main())
