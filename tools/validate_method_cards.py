#!/usr/bin/env python3
"""N19 method-card build gate.

Validates the fourteen authored method cards (structure, citation integrity,
completeness against the coverage island, the copy lint over every card text
and the safety citations), the frozen signature mapping, and the three
non-numeric verdict engines against the N05 golden corpus and the N19 stratum.

The JavaScript twin's parity is proven after assembly by tools/check_n19_runtime.js
and recorded in evidence/N19_CORPUS_RECORD.json by tools/n19_corpus.py.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    DEST, canonical_json_bytes, load_json, parse_master, sha256_bytes, sha256_file,
)
import method_engine as me  # noqa: E402
from validate_terms import lint_authored_data  # noqa: E402
from validate_golden_vectors import GOLDEN_VECTORS_PATH, PROTOCOL_PATH  # noqa: E402

CARDS_PATH = 'data/method_cards.json'
CARD_SCHEMA_PATH = 'data/method_card_schema.json'
CONTRACT_PATH = 'data/method_engine_contract.json'
CHAIN_REFS_PATH = 'data/chain_references.json'
CHAINS_PATH = 'data/chains.json'
COVERAGE_PATH = 'data/coverage.json'
TERMS_PATH = 'data/terms.json'
PYTHON_ENGINE = 'tools/method_engine.py'
JS_ENGINE = 'src/method-engine.js'

SIGNATURE_RE = re.compile(r'^MC-[1-7][A-D]-[0-9]{2}$')
PROCEDURE_KEY_RE = re.compile(r'^[a-z0-9_]+$')
NO_BLAME_RE = re.compile(r'\b(?:tu\s+esi|tu\s+ne|nepareizais|sliktais|muļķis)\b', re.IGNORECASE)

FORBIDDEN_CLAIMS = (
    'oficiāls eksāmens',
    'oficiāls kolokvija eksāmens',
    'īsts eksāmens',
    'eksāmena jautājums',
    'oficiāls uzdevums',
    'RSU eksāmens',
    'garantēts vērtējums',
    'proktors',
)

# The engines must not contain any similarity, keyword or case-folding routine.
FORBIDDEN_SOURCE_TOKENS = (
    'difflib', 'sequencematcher', 'levenshtein', 'rapidfuzz', 'fuzz', 'similarity',
    'similarities', 'tokenize', 'tokenizer', 'casefold', 'startswith', 'endswith',
    'localeCompare', 'normalize', 'stemmer', 'keyword', 'keywords', 'newregexp',
    'textmatch', 'fuzzy',
)

# The interface vocabulary of the three engines. These words are part of the
# contract's own language and are therefore not domain keywords.
ENGINE_VOCABULARY = {
    'ordering', 'matching', 'sequence', 'assessment', 'correct', 'incorrect', 'partial',
    'pending', 'awarded', 'denied', 'points', 'criterion', 'criteria', 'text', 'order',
    'pairs', 'signature', 'feedback', 'remediation', 'diagnostics', 'replay', 'digest',
    'source', 'ref', 'card', 'step', 'item', 'left', 'right', 'engine', 'kind',
    'verdict', 'error', 'class', 'status', 'position', 'expected', 'submitted', 'note',
    'key', 'blank', 'response', 'unknown', 'missing', 'misplaced', 'repeated',
    'unmatched', 'accepted', 'distractor', 'misconception', 'quantity', 'links',
    'chain', 'steps', 'spec', 'source_ref', 'contract', 'terms', 'cards', 'module',
    'runtime', 'twin', 'verdicts', 'graded', 'grading', 'rubric', 'auto', 'self',
    'assessed', 'human', 'review', 'machine', 'checked', 'instance', 'payload',
    'question', 'family', 'variant', 'seed', 'topic', 'procedure', 'lab', 'master',
    'latvian', 'english', 'level', 'notation', 'island', 'digits', 'sub', 'step',
}

# No engine comparison may touch a prose field.
PROSE_FIELDS = (
    'text_lv', 'note_lv', 'reasoning_lv', 'statement_lv', 'prompt_lv', 'title_lv',
    'subtitle_lv', 'misconception_note_lv', 'expected_summary_lv', 'order_citation_lv',
    'entry_lv', 'quantity_lv',
)

# Stop words are excluded from the safety-overlap ratio: they carry no claim.
SAFETY_STOPWORDS = {
    'un', 'ar', 'ir', 'ka', 'tas', 'tā', 'tās', 'to', 'kur', 'kad', 'jo', 'ne',
    'bet', 'tik', 'vai', 'par', 'uz', 'no', 'pa', 'priekš', 'šis', 'šī', 'šo',
    'šīs', 'darbā', 'darbu', 'aiz', 'pie', 'bez', 'pēc', 'pirms', 'šim', 'šos',
    'savu', 'savas', 'savu', 'iekšējā', 'uztvertu', 'nejaušu', 'noplūdi', 'darbs',
    'sācies', 'izšķīstu', 'izšķīstu', 'skābi', 'skābes', 'kodīgu', 'skābi',
}

CARD_TEXT_FIELDS = (
    'title_lv', 'subtitle_lv', 'order_citation_lv', 'epistemic_label', 'banner_lv',
    'safety_note_lv', 'print_note_lv', 'procedure_key',
)


def card_step_key(card_id: str, step_id: str) -> str:
    """The reveal key of one card step. Inspection resistance, not secrecy."""
    import hashlib
    return hashlib.sha256(f'{card_id}:{step_id}:N19'.encode('utf-8')).hexdigest()


def card_rules_key(card_id: str) -> str:
    import hashlib
    return hashlib.sha256(f'{card_id}:rules:N19'.encode('utf-8')).hexdigest()


def xor_bytes(data: bytes, key_hex: str) -> bytes:
    key = bytes.fromhex(key_hex)
    if not key:
        raise ValueError('empty reveal key')
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def seal_card_step(card_id: str, step: dict[str, Any]) -> dict[str, Any]:
    """Seal the diagnostic half of a step: the note, the signature and the links.

    The step statement stays public — it is the teaching content. The note and
    the signature are the answer key and are revealed only on interaction.
    """
    import base64
    payload = {
        'misconception_signature': step.get('misconception_signature'),
        'misconception_note_lv': step.get('misconception_note_lv'),
        'feedback_key': step.get('feedback_key'),
        'reasoning_lv': step.get('reasoning_lv'),
        'safety': step.get('safety'),
        'quantity_links': step.get('quantity_links'),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    key = card_step_key(card_id, step['step_id'])
    return {'alg': 'xor-v1', 'key': key,
            'data': base64.b64encode(xor_bytes(raw, key)).decode('ascii')}


def seal_card_rules(card: dict[str, Any]) -> dict[str, Any]:
    """Seal the grading rules: the free-order groups, the prompts and the pairs."""
    import base64
    payload = {
        'free_order_groups': card.get('free_order_groups', []),
        'sequence_prompts': card.get('sequence_prompts', []),
        'matching': card.get('matching'),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    key = card_rules_key(card['card_id'])
    return {'alg': 'xor-v1', 'key': key,
            'data': base64.b64encode(xor_bytes(raw, key)).decode('ascii')}


def build_runtime_projection(cards_data: dict[str, Any]) -> dict[str, Any]:
    """The island the artifact carries: public statements, sealed diagnostics."""
    cards = []
    for card in cards_data.get('cards', []):
        steps = []
        for step in card.get('steps', []):
            steps.append({
                'step_id': step['step_id'],
                'statement_lv': step['statement_lv'],
                'critical': bool(step.get('critical')),
                'sealed': seal_card_step(card['card_id'], step),
            })
        cards.append({
            'card_id': card['card_id'],
            'procedure_key': card['procedure_key'],
            'title_lv': card['title_lv'],
            'subtitle_lv': card['subtitle_lv'],
            'topic': card['topic'],
            'family_id': card['family_id'],
            'chain_id': card['chain_id'],
            'outcome_ids': card['outcome_ids'],
            'master_citation': card['master_citation'],
            'secondary_citations': card.get('secondary_citations', []),
            'order_citation_lv': card['order_citation_lv'],
            'epistemic_label': card['epistemic_label'],
            'banner_lv': card['banner_lv'],
            'safety_note_lv': card.get('safety_note_lv'),
            'self_assessment_prompt_lv': (card.get('self_assessment') or {}).get('prompt_lv'),
            'steps': steps,
            'sealed_rules': seal_card_rules(card),
        })
    return {
        'schema_version': cards_data.get('schema_version', 1),
        'format_version': cards_data.get('format_version', 1),
        'island_id': 'sim-method-cards',
        'owner': 'N19',
        'status': 'authored',
        'title_lv': cards_data.get('title_lv', 'Metodiskās kartītes'),
        'purpose_lv': cards_data.get('purpose_lv', ''),
        'scope_note_lv': cards_data.get('scope_note_lv', ''),
        'banner_lv': cards_data.get('banner_lv', ''),
        'epistemic_note': cards_data.get('n09_gap_notice_lv', ''),
        'card_count': len(cards),
        'step_count': sum(len(c['steps']) for c in cards),
        'cards': cards,
    }


def _section_text(path: Path, anchor: str) -> str:
    """Extract the visible text of the master section that owns an anchor."""
    raw = path.read_text(encoding='utf-8')
    match = re.search(r'<(section|h[1-6]|div)[^>]*\bid="%s"[^>]*>' % re.escape(anchor), raw)
    if not match:
        return ''
    tag = match.group(1)
    start = match.start()
    end = len(raw)
    if tag in ('section', 'div'):
        depth = 0
        pattern = re.compile(r'<(/?)%s\b[^>]*>' % tag)
        for hit in pattern.finditer(raw, start):
            if hit.group(1) == '':
                depth += 1
            else:
                depth -= 1
                if depth == 0:
                    end = hit.end()
                    break
        else:
            end = start + 6000
    else:
        end = match.end()
        level = int(tag[1])
        for hit in re.finditer(r'<h([1-6])\b[^>]*>', raw[end:]):
            if int(hit.group(1)) <= level:
                end += hit.start()
                break
        else:
            end = min(len(raw), end + 6000)
    fragment = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', raw[start:end], flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', fragment)
    text = html.unescape(text)
    return ' '.join(text.split())


def _words(text: str) -> list[str]:
    return re.findall(r'[A-Za-zĀ-ž][A-Za-zĀ-ž0-9īķļņēģ-]*', text.lower())


def _content_words(text: str) -> list[str]:
    return [w for w in _words(text) if len(w) >= 4 and w not in SAFETY_STOPWORDS]


def _collect_text(node: Any, out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and (key.endswith('_lv') or key in CARD_TEXT_FIELDS):
                out.append(value)
            else:
                _collect_text(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_text(item, out)


# The Latvian teaching fields. The keyword scan reads only these: the
# epistemic label and the banner are metadata, not subject matter.
TEACHING_FIELDS = (
    'title_lv', 'subtitle_lv', 'statement_lv', 'reasoning_lv', 'misconception_note_lv',
    'prompt_lv', 'note_lv', 'entry_lv', 'order_citation_lv', 'expected_summary_lv',
)


def _collect_teaching_text(node: Any, out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and key in TEACHING_FIELDS:
                out.append(value)
            else:
                _collect_teaching_text(value, out)
    elif isinstance(node, list):
        for item in node:
            _collect_teaching_text(item, out)


def _python_code_tokens(source: str) -> tuple[set[str], set[str]]:
    """Identifiers and string literals of a Python source, without comments or docstrings."""
    import ast

    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, 'body', [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                docstrings.add(id(body[0].value))
    names: set[str] = set()
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.alias):
            names.add(node.name or '')
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docstrings:
            literals.add(node.value)
    return names, literals


def _js_code_tokens(source: str) -> tuple[set[str], set[str]]:
    """Identifiers and string literals of a JavaScript source, without comments."""
    stripped = re.sub(r'/\*[\s\S]*?\*/', ' ', source)
    stripped = re.sub(r'(^|[^:"\'\\])//[^\n]*', r'\1', stripped)
    names = set(re.findall(r'[A-Za-z_$][A-Za-z0-9_$]*', stripped))
    literals = set(re.findall(r"'((?:[^'\\]|\\.)*)'", stripped)) | \
        set(re.findall(r'"((?:[^"\\]|\\.)*)"', stripped))
    return names, literals


def validate(repo_root: Path = DEST) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    cards_path = repo_root / CARDS_PATH
    schema_path = repo_root / CARD_SCHEMA_PATH
    contract_path = repo_root / CONTRACT_PATH
    refs_path = repo_root / CHAIN_REFS_PATH
    chains_path = repo_root / CHAINS_PATH
    coverage_path = repo_root / COVERAGE_PATH
    terms_path = repo_root / TERMS_PATH
    golden_path = repo_root / GOLDEN_VECTORS_PATH

    for required in (cards_path, schema_path, contract_path, refs_path, chains_path,
                     coverage_path, terms_path, golden_path,
                     repo_root / PYTHON_ENGINE, repo_root / JS_ENGINE):
        if not required.exists():
            errors.append(f'Missing N19 artifact: {required}')
    if errors:
        return {'status': 'FAIL', 'errors': errors}

    cards_doc = load_json(cards_path)
    schema = load_json(schema_path)
    contract = load_json(contract_path)
    refs = load_json(refs_path)
    chains_doc = load_json(chains_path)
    coverage = load_json(coverage_path)
    terms = load_json(terms_path)
    golden = load_json(golden_path)

    if cards_doc.get('island_id') != 'sim-method-cards':
        errors.append('cards island_id must be sim-method-cards')
    if cards_doc.get('owner') != 'N19':
        errors.append('cards owner must be N19')
    if contract.get('island_id') != 'sim-method-engine':
        errors.append('contract island_id must be sim-method-engine')

    cards = cards_doc.get('cards', [])
    chains_by_id = {c['id']: c for c in chains_doc.get('chains', [])}
    outcomes_by_id = {o['id']: o for o in coverage.get('outcomes', [])}
    terms_by_key = {t['key']: t for t in terms.get('terms', [])}
    master_cache: dict[str, Any] = {}

    # -- 1. card structure ---------------------------------------------------
    card_rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    declared_refs = {entry['id']: entry for entry in refs.get('method_cards', [])}
    practice_refs = refs.get('practice_items', [])

    # The schema declares the reference file's status for the card
    # declarations. The declaration must match the file: a card format that
    # claims a status the reference file does not carry is a drift, and the
    # N16 gate requires the declared-pending- prefix while the consumer is
    # unimplemented, so the status is not changed quietly here.
    declared_reference_status = schema.get('reference_status')
    actual_reference_statuses = sorted({str(entry.get('status', ''))
                                        for entry in refs.get('method_cards', [])})
    if declared_reference_status not in actual_reference_statuses:
        errors.append(f'reference status drift: the schema declares {declared_reference_status!r}, '
                      f'the reference file carries {actual_reference_statuses}')

    for card in cards:
        card_id = card.get('card_id', '<unknown>')
        row: dict[str, Any] = {'card_id': card_id, 'steps': 0, 'free_order_groups': 0,
                               'sequence_prompts': 0, 'safety_entries': 0, 'errors': []}
        if card_id in seen_ids:
            row['errors'].append('duplicate card_id')
            errors.append(f'{card_id}: duplicate card_id')
        seen_ids.add(card_id)
        if card_id not in declared_refs:
            row['errors'].append('not declared in data/chain_references.json')
            errors.append(f'{card_id}: not declared in data/chain_references.json')
        else:
            declared = declared_refs[card_id]
            if declared.get('chain_ids') != [card.get('chain_id')]:
                row['errors'].append('chain id differs from the declared reference')
                errors.append(f'{card_id}: chain id differs from data/chain_references.json')
            if declared.get('family_id') != card.get('family_id'):
                row['errors'].append('family id differs from the declared reference')
                errors.append(f'{card_id}: family id differs from data/chain_references.json')

        if not PROCEDURE_KEY_RE.match(card.get('procedure_key', '')):
            row['errors'].append('procedure_key is not a lower snake_case key')
            errors.append(f'{card_id}: procedure_key is not a lower snake_case key')
        topic = card.get('topic')
        if topic not in range(1, 8):
            row['errors'].append('topic out of range')
            errors.append(f'{card_id}: topic out of range')
        chain_id = card.get('chain_id')
        chain = chains_by_id.get(chain_id)
        if chain is None:
            row['errors'].append('chain id does not resolve')
            errors.append(f'{card_id}: chain id {chain_id!r} does not resolve in #sim-chains')
        else:
            if chain.get('topic') != topic:
                row['errors'].append('chain topic differs from the card topic')
                errors.append(f'{card_id}: chain topic differs from the card topic')
            card_outcomes = card.get('outcome_ids') or []
            chain_outcomes = chain.get('outcome_ids') or []
            if not set(card_outcomes).issubset(set(chain_outcomes)):
                row['errors'].append('outcome ids are not a subset of the chain outcome ids')
                errors.append(f'{card_id}: outcome ids are not a subset of the chain outcome ids')
            for outcome_id in card_outcomes:
                outcome = outcomes_by_id.get(outcome_id)
                if outcome is None:
                    row['errors'].append(f'outcome {outcome_id} does not resolve')
                    errors.append(f'{card_id}: outcome {outcome_id} does not resolve in #sim-coverage')
                elif outcome.get('topic') != topic:
                    row['errors'].append(f'outcome {outcome_id} belongs to another topic')
                    errors.append(f'{card_id}: outcome {outcome_id} belongs to another topic')
            if not card_outcomes:
                row['errors'].append('no outcome ids')
                errors.append(f'{card_id}: no outcome ids')

        # -- citations -------------------------------------------------------
        citation_fields = [('master_citation', card.get('master_citation'))]
        for extra in card.get('secondary_citations') or []:
            citation_fields.append(('secondary_citation', extra))
        resolved_citations = 0
        for label, citation in citation_fields:
            if not citation:
                row['errors'].append(f'{label} missing')
                errors.append(f'{card_id}: {label} missing')
                continue
            path = repo_root / citation.get('path', '')
            if not path.exists():
                row['errors'].append(f'{label} path does not exist')
                errors.append(f'{card_id}: {label} path does not exist')
                continue
            digest = sha256_file(path)
            if digest != citation.get('sha256'):
                row['errors'].append(f'{label} sha256 does not match the frozen master')
                errors.append(f'{card_id}: {label} sha256 does not match the frozen master')
            key = str(path)
            if key not in master_cache:
                master_cache[key] = parse_master(path)
            index = master_cache[key]
            anchor = citation.get('anchor')
            if anchor not in index.ids:
                row['errors'].append(f'{label} anchor {anchor!r} does not resolve case-exactly')
                errors.append(f'{card_id}: {label} anchor {anchor!r} does not resolve case-exactly')
                continue
            heading = index.headings.get(anchor) or index.section_headings.get(anchor)
            if heading != citation.get('heading_lv'):
                row['errors'].append(f'{label} heading differs from the master')
                errors.append(f'{card_id}: {label} heading differs from the master')
                continue
            resolved_citations += 1
        row['citations_resolved'] = resolved_citations
        row['citations_total'] = len(citation_fields)

        # -- steps ------------------------------------------------------------
        steps = card.get('steps') or []
        row['steps'] = len(steps)
        step_ids = [s.get('step_id') for s in steps]
        if not steps:
            row['errors'].append('no steps')
            errors.append(f'{card_id}: no steps')
        if len(set(step_ids)) != len(step_ids):
            row['errors'].append('step ids are not unique')
            errors.append(f'{card_id}: step ids are not unique')
        chain_steps = {s['step_id']: s for s in (chain.get('steps') if chain else [])}
        for step in steps:
            sid = step.get('step_id', '<unknown>')
            for required in schema.get('step_required', []):
                if required not in step or step.get(required) in (None, ''):
                    row['errors'].append(f'step {sid}: missing {required}')
                    errors.append(f'{card_id}: step {sid}: missing {required}')
            signature = step.get('misconception_signature', '')
            if not SIGNATURE_RE.match(signature):
                row['errors'].append(f'step {sid}: signature violates the N04 stub pattern')
                errors.append(f'{card_id}: step {sid}: signature {signature!r} violates the N04 stub pattern')
            if step.get('feedback_key') not in terms_by_key:
                row['errors'].append(f'step {sid}: feedback key does not resolve in #sim-terms')
                errors.append(f'{card_id}: step {sid}: feedback key does not resolve in #sim-terms')
            for link in step.get('quantity_links') or []:
                target_chain = chains_by_id.get(link.get('chain_id'))
                if target_chain is None:
                    row['errors'].append(f'step {sid}: quantity link chain does not resolve')
                    errors.append(f'{card_id}: step {sid}: quantity link chain does not resolve')
                    continue
                target = next((s for s in target_chain.get('steps', [])
                               if s.get('step_id') == link.get('chain_step_id')), None)
                if target is None:
                    row['errors'].append(f'step {sid}: quantity link chain step does not resolve')
                    errors.append(f'{card_id}: step {sid}: quantity link chain step does not resolve')
                    continue
                result = target.get('result') or {}
                if result.get('display_lv') != link.get('value_display_lv'):
                    row['errors'].append(f'step {sid}: quantity link value differs from the chain result')
                    errors.append(f'{card_id}: step {sid}: quantity link value differs from the chain result')
                if result.get('unit') != link.get('unit'):
                    row['errors'].append(f'step {sid}: quantity link unit differs from the chain result')
                    errors.append(f'{card_id}: step {sid}: quantity link unit differs from the chain result')
            safety = step.get('safety')
            if safety:
                row['safety_entries'] += 1
                citation = safety.get('citation') or {}
                path = repo_root / citation.get('path', '')
                if not path.exists():
                    row['errors'].append(f'step {sid}: safety citation path does not exist')
                    errors.append(f'{card_id}: step {sid}: safety citation path does not exist')
                else:
                    section = _section_text(path, citation.get('anchor', ''))
                    if not section:
                        row['errors'].append(f'step {sid}: safety citation anchor has no section text')
                        errors.append(f'{card_id}: step {sid}: safety citation anchor has no section text')
                    else:
                        section_words = set(_words(section))
                        content = _content_words(safety.get('entry_lv', ''))
                        present = [w for w in content if w in section_words]
                        ratio = (len(present) / len(content)) if content else 0.0
                        row.setdefault('safety_overlap', []).append(
                            {'step_id': sid, 'content_words': len(content), 'covered': len(present),
                             'ratio': round(ratio, 4)})
                        if ratio < 0.9:
                            row['errors'].append(f'step {sid}: safety entry is not covered by its master section')
                            errors.append(f'{card_id}: step {sid}: safety entry is not covered by its master section')

        # -- free order groups -------------------------------------------------
        groups = card.get('free_order_groups') or []
        row['free_order_groups'] = len(groups)
        for group in groups:
            for sid in group.get('step_ids', []):
                if sid not in step_ids:
                    row['errors'].append(f'free order group {group.get("group_id")} names an unknown step')
                    errors.append(f'{card_id}: free order group names an unknown step')
            citation = group.get('citation') or {}
            path = repo_root / citation.get('path', '')
            if not path.exists():
                row['errors'].append(f'free order group {group.get("group_id")}: citation path does not exist')
                errors.append(f'{card_id}: free order group citation path does not exist')

        # -- sequence prompts ---------------------------------------------------
        prompts = card.get('sequence_prompts') or []
        row['sequence_prompts'] = len(prompts)
        prompt_ids = [p.get('prompt_id') for p in prompts]
        if len(set(prompt_ids)) != len(prompt_ids):
            row['errors'].append('sequence prompt ids are not unique')
            errors.append(f'{card_id}: sequence prompt ids are not unique')
        for prompt in prompts:
            acceptance = prompt.get('acceptance_step_ids') or []
            if not acceptance:
                row['errors'].append(f'prompt {prompt.get("prompt_id")}: empty acceptance set')
                errors.append(f'{card_id}: prompt {prompt.get("prompt_id")}: empty acceptance set')
            for sid in acceptance:
                if sid not in step_ids:
                    row['errors'].append(f'prompt {prompt.get("prompt_id")}: acceptance names an unknown step')
                    errors.append(f'{card_id}: prompt acceptance names an unknown step')
            for distractor in prompt.get('distractors') or []:
                if distractor.get('step_id') not in step_ids:
                    row['errors'].append(f'prompt {prompt.get("prompt_id")}: distractor names an unknown step')
                    errors.append(f'{card_id}: prompt distractor names an unknown step')
                if distractor.get('step_id') in acceptance:
                    row['errors'].append(f'prompt {prompt.get("prompt_id")}: distractor is also accepted')
                    errors.append(f'{card_id}: prompt distractor is also accepted')
                if not SIGNATURE_RE.match(distractor.get('misconception_signature', '')):
                    row['errors'].append(f'prompt {prompt.get("prompt_id")}: distractor signature invalid')
                    errors.append(f'{card_id}: prompt distractor signature invalid')

        # -- matching ------------------------------------------------------------
        matching = card.get('matching')
        if matching:
            left_ids = {i['id'] for i in matching.get('left_items', [])}
            right_ids = {i['id'] for i in matching.get('right_items', [])}
            for pair in matching.get('correct_pairs', []):
                if pair.get('left_id') not in left_ids or pair.get('right_id') not in right_ids:
                    row['errors'].append('matching pair names an unknown item')
                    errors.append(f'{card_id}: matching pair names an unknown item')
                if pair.get('feedback_key') not in terms_by_key:
                    row['errors'].append('matching pair feedback key does not resolve')
                    errors.append(f'{card_id}: matching pair feedback key does not resolve')

        # -- self assessment ------------------------------------------------------
        self_assessment = card.get('self_assessment') or {}
        if self_assessment.get('grading') != 'self':
            row['errors'].append('self assessment grading must be "self"')
            errors.append(f'{card_id}: self assessment grading must be "self"')
        if not self_assessment.get('pending_semantics_lv'):
            row['errors'].append('self assessment has no pending semantics')
            errors.append(f'{card_id}: self assessment has no pending semantics')

        card_rows.append(row)

    # -- 2. completeness against the coverage island ---------------------------
    card_families = {card.get('family_id'): card.get('card_id') for card in cards}
    declared_card_families = {entry['family_id']: entry['id'] for entry in refs.get('method_cards', [])}
    coverage_rows: list[dict[str, Any]] = []
    method_outcomes = 0
    for outcome in coverage.get('outcomes', []):
        families = outcome.get('bindings', {}).get('practice_families', []) or []
        method_families = [f for f in families if f in declared_card_families]
        if not method_families:
            continue
        method_outcomes += 1
        cards_for_outcome = sorted({declared_card_families[f] for f in method_families})
        coverage_rows.append({
            'outcome_id': outcome['id'],
            'topic': outcome['topic'],
            'families': method_families,
            'cards': cards_for_outcome,
            'declared_by_card': sorted({c.get('card_id') for c in cards
                                        if outcome['id'] in (c.get('outcome_ids') or [])}),
            'status': 'COVERED' if cards_for_outcome else 'MISSING',
        })
        if not cards_for_outcome:
            errors.append(f'{outcome["id"]}: declares a method family without a card')

    # -- 3. bidirectional reference table ---------------------------------------
    reference_rows: list[dict[str, Any]] = []
    for card in cards:
        card_id = card.get('card_id')
        outcome_refs = sorted({c.get('card_id') for c in cards
                               if set(c.get('outcome_ids') or []) & set(card.get('outcome_ids') or [])})
        declared_outcomes = sorted({o['id'] for o in coverage.get('outcomes', [])
                                    if card_id in [declared_card_families.get(f) for f in o.get('bindings', {}).get('practice_families', [])]})
        practice_refs_for_card = sorted({p['id'] for p in practice_refs
                                         if p.get('family_id') == card.get('family_id')})
        chain_back = sorted({c['id'] for c in chains_doc.get('chains', [])
                             if card_id in ((c.get('back_links') or {}).get('method_card_ids') or [])})
        reference_rows.append({
            'card_id': card_id,
            'chain_id': card.get('chain_id'),
            'outcome_ids': card.get('outcome_ids'),
            'outcomes_declarating_the_family': declared_outcomes,
            'cards_declaring_the_same_outcomes': outcome_refs,
            'practice_refs': practice_refs_for_card,
            'chains_naming_the_card': chain_back,
            'status': 'BIDIRECTIONAL' if (declared_outcomes and practice_refs_for_card
                                          and chain_back == [card.get('chain_id')]) else 'INCOMPLETE',
        })
        if not declared_outcomes:
            errors.append(f'{card_id}: no coverage outcome declares its family')
        if not practice_refs_for_card:
            errors.append(f'{card_id}: no practice reference names its family')
        if chain_back != [card.get('chain_id')]:
            errors.append(f'{card_id}: the chain back-link names {chain_back}, the card names '
                          f'{card.get("chain_id")!r}')

    # -- 4. copy lint over every card text ---------------------------------------
    lint = lint_authored_data(terms, terms_by_key, repo_root=repo_root,
                               extra_data_paths=[cards_path])
    if lint['status'] != 'PASS':
        for message in lint['errors']:
            errors.append(f'copy lint: {message}')

    card_texts: list[str] = []
    _collect_text(cards_doc, card_texts)
    blame_hits = [t for t in card_texts if NO_BLAME_RE.search(t)]
    if blame_hits:
        errors.append(f'copy lint: {len(blame_hits)} card texts blame the learner')
    claim_hits = []
    for text in card_texts:
        for claim in FORBIDDEN_CLAIMS:
            if claim.lower() in text.lower():
                claim_hits.append(claim)
    if claim_hits:
        errors.append(f'copy lint: forbidden positive exam claims {sorted(set(claim_hits))}')

    # -- 5. signature mapping ----------------------------------------------------
    golden_signatures: set[str] = set()
    for vector in golden.get('vectors', []):
        golden_signatures.update(vector['instance'].get('misconception_signatures', []))
    registry = {entry['signature']: entry for entry in contract.get('signature_registry', [])}
    card_signatures: set[str] = set()
    for card in cards:
        for step in card.get('steps') or []:
            card_signatures.add(step.get('misconception_signature'))
        for prompt in card.get('sequence_prompts') or []:
            for distractor in prompt.get('distractors') or []:
                card_signatures.add(distractor.get('misconception_signature'))
        for pair in (card.get('matching') or {}).get('correct_pairs', []) or []:
            card_signatures.add(pair.get('misconception_signature'))

    # The sweep covers the whole registry and every signature the cards
    # declare, in both directions: a signature that no card declares is an
    # orphaned registry entry and dangles just as hard as a card signature
    # with no registry entry.
    signature_rows: list[dict[str, Any]] = []
    all_signatures = sorted(set(card_signatures) | set(registry))
    for signature in all_signatures:
        entry = registry.get(signature)
        problems: list[str] = []
        if entry is None:
            problems.append('not in the signature registry')
        else:
            if not SIGNATURE_RE.match(signature):
                problems.append('violates the N04 stub pattern')
            if signature not in golden_signatures:
                problems.append('not present in the frozen N05 corpus')
            key = entry.get('feedback_key')
            if key not in terms_by_key:
                problems.append('feedback key does not resolve in #sim-terms')
            elif not (terms_by_key[key].get('text_lv') or '').strip():
                problems.append('feedback text is empty')
            if entry.get('provenance') not in ('exact-family', 'nearest-available-cross-family'):
                problems.append('unknown provenance')
            if signature not in card_signatures:
                problems.append('no card declares this signature')
        if problems:
            errors.append(f'signature {signature}: {"; ".join(problems)}')
        signature_rows.append({
            'signature': signature,
            'in_registry': entry is not None,
            'in_golden_corpus': signature in golden_signatures,
            'feedback_key': (entry or {}).get('feedback_key'),
            'cards': sorted({c.get('card_id') for c in cards
                             if signature in {s.get('misconception_signature') for s in c.get('steps') or []}
                             or signature in {d.get('misconception_signature')
                                              for p in c.get('sequence_prompts') or [] for d in p.get('distractors') or []}
                             or signature in {p.get('misconception_signature')
                                              for p in (c.get('matching') or {}).get('correct_pairs', []) or []}}),
            'provenance': (entry or {}).get('provenance'),
            'declared_by_card': signature in card_signatures,
            'status': 'RESOLVED' if not problems else 'DANGLING',
        })

    # -- 6. the three engines against the frozen corpus ----------------------------
    engine = me.MethodEngine(contract, terms)
    cards_by_id = {c['card_id']: c for c in cards}

    n05_rows: list[dict[str, Any]] = []
    for vector in golden.get('vectors', []):
        if vector.get('status') == 'retired':
            continue
        payload_class = vector['instance'].get('payload_class')
        if payload_class not in ('ordering', 'matching', 'method'):
            continue
        record = engine.grade_instance(vector['instance'], vector['submission'])
        view = engine.oracle_view(record)
        expected = vector['expected']
        ok = all(view[key] == expected[key] for key in (
            'verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
            'self_assessed_points', 'human_reviewed_points', 'pending_points', 'max_points'))
        n05_rows.append({
            'vector_id': vector['vector_id'], 'type_id': vector['instance']['type_id'],
            'case_kind': vector['case_kind'], 'verdict_class': view['verdict_class'],
            'error_class': view['error_class'],
            'signatures': record['diagnostics'].get('signatures', []),
            'status': 'PASS' if ok else 'FAIL',
        })
        if not ok:
            errors.append(f'{vector["vector_id"]}: verdict-for-verdict mismatch against the N05 oracle')

    stratum_rows: list[dict[str, Any]] = []
    vectors = contract.get('method_vectors', {})
    all_vectors: list[dict[str, Any]] = []
    for key in ('ordering_vectors', 'matching_vectors', 'sequence_vectors', 'self_assessment_vectors'):
        all_vectors.extend(vectors.get(key, []))
    all_vectors.append(vectors.get('scratch', {}).get('ordering'))
    for vector in all_vectors:
        if not vector:
            continue
        spec = me.spec_for_vector(engine, cards_by_id, vector)
        record = engine.grade(spec, vector['submission'])
        expected = vector['expected']
        diagnostics = record['diagnostics']
        got: dict[str, Any] = {
            'verdict_class': record['verdict_class'],
            'error_class': record['error_class'],
            'signatures': diagnostics.get('signatures', []),
        }
        kind = spec.get('kind')
        if kind == me.ORDERING:
            got['wrong_positions'] = diagnostics.get('wrong_positions', [])
        elif kind == me.MATCHING:
            got['pair_statuses'] = diagnostics.get('pair_statuses', {})
        elif kind == me.SEQUENCE:
            got['status'] = (diagnostics.get('per_step') or [{}])[0].get('status')
        elif kind == me.SELF_ASSESSMENT:
            got['pending_points'] = record['pending_points']
        differences = {k: {'expected': expected.get(k), 'actual': got.get(k)}
                       for k in expected if expected.get(k) != got.get(k)}
        stratum_rows.append({
            'id': vector['id'], 'kind': kind, 'card_id': vector.get('card_id'),
            'expected': expected, 'actual': got,
            'status': 'PASS' if not differences else 'FAIL',
        })
        if differences:
            errors.append(f'{vector["id"]}: N19 stratum vector mismatch {differences}')

    # -- 7. the no-keyword rule, mechanically ---------------------------------------
    source_findings: list[dict[str, Any]] = []
    teaching_texts: list[str] = []
    _collect_teaching_text(cards_doc, teaching_texts)
    card_content_words = set()
    for text in teaching_texts:
        card_content_words.update(w for w in _words(text) if len(w) >= 5)
    for relative, tokenizer in ((PYTHON_ENGINE, _python_code_tokens), (JS_ENGINE, _js_code_tokens)):
        source = (repo_root / relative).read_text(encoding='utf-8')
        names, literals = tokenizer(source)
        hits = sorted({token for token in FORBIDDEN_SOURCE_TOKENS
                       if any(token in name.lower() for name in names)})
        domain_literals = sorted({
            word for literal in literals for word in _words(literal)
            if len(word) >= 5 and word in card_content_words and word not in ENGINE_VOCABULARY
        })
        code_only = source
        if relative == PYTHON_ENGINE:
            code_only = re.sub(r'#.*$', '', source, flags=re.M)
        comparisons = []
        for field in PROSE_FIELDS:
            for match in re.finditer(r'\b' + re.escape(field) + r'\s*(==|!=)', code_only):
                comparisons.append(f'{field}{match.group(1)}')
        source_findings.append({
            'source': relative,
            'forbidden_identifiers': hits,
            'domain_keyword_literals': domain_literals,
            'prose_comparisons': comparisons,
            'status': 'PASS' if not hits and not domain_literals and not comparisons else 'FAIL',
        })
        if hits:
            errors.append(f'{relative}: the engine contains a forbidden text routine {hits}')
        if domain_literals:
            errors.append(f'{relative}: the engine embeds domain keyword literals {domain_literals}')
        if comparisons:
            errors.append(f'{relative}: the engine compares a prose field {comparisons}')

    # -- 7b. the no-keyword rule, behaviourally -------------------------------------
    # A submission that carries free text alongside correct ids must not change
    # the verdict: the three engines read ids only.
    behaviour_rows: list[dict[str, Any]] = []
    card_mc03 = cards_by_id.get('MC-EX03')
    card_mc06 = cards_by_id.get('MC-EX06')
    if card_mc03 and card_mc06:
        probes = [
            ('ordering', card_mc03, {'order': [s['step_id'] for s in card_mc03['steps']]}),
            ('matching', card_mc03, {'pairs': [{'left_id': p['left_id'], 'right_id': p['right_id']}
                                               for p in card_mc03['matching']['correct_pairs']]}),
            ('sequence', card_mc06, {'next_step_id': card_mc06['sequence_prompts'][0]['acceptance_step_ids'][0]}),
        ]
        for kind, card, submission in probes:
            spec = engine.spec_from_card(card, kind, None, [
                {'criterion_id': 'C1_PROBE', 'grading': 'auto', 'engine_binding': 'N19-method', 'points': 1.0}])
            plain = engine.grade(spec, submission)
            noisy = engine.grade(spec, dict(submission, text='Ielej noteikto tilpumu un nolasi beigu līmeni'))
            same = all(plain[key] == noisy[key] for key in (
                'verdict_class', 'error_class', 'awarded_criteria', 'machine_checked_points',
                'pending_points', 'max_points', 'diagnostics'))
            behaviour_rows.append({
                'kind': kind, 'card_id': card['card_id'],
                'verdict_without_text': plain['verdict_class'],
                'verdict_with_text': noisy['verdict_class'],
                'verdict_unchanged': same,
                'status': 'PASS' if same else 'FAIL',
            })
            if not same:
                errors.append(f'{kind}: a free-text field changed the verdict')

    # -- 8. budget measurement -------------------------------------------------------
    # The cards budget measures the island that actually ships (the sealed
    # runtime projection), not the source file: the projection is larger than
    # the source because it carries the sealed diagnostics, and the shipped
    # size is what the artifact actually pays for.
    budgets = contract.get('budgets', {})
    runtime_projection = build_runtime_projection(cards_doc)
    measured = {
        'method_cards_island_bytes': len(canonical_json_bytes(runtime_projection)),
        'method_engine_contract_bytes': len(canonical_json_bytes(contract)),
        'method_engine_js_bytes': (repo_root / JS_ENGINE).stat().st_size,
    }
    budget_rows = []
    for name, ceiling in ((k, v.get('ceiling')) for k, v in budgets.items() if isinstance(v, dict)):
        actual = measured.get(name)
        if actual is None:
            continue
        ok = actual <= ceiling
        budget_rows.append({'budget': name, 'measured_bytes': actual, 'ceiling_bytes': ceiling,
                            'headroom_bytes': ceiling - actual, 'status': 'PASS' if ok else 'FAIL'})
        if not ok:
            errors.append(f'budget {name}: {actual} B exceeds the declared ceiling {ceiling} B')

    digests = {
        'cards': sha256_bytes(canonical_json_bytes(cards_doc)),
        'card_schema': sha256_bytes(canonical_json_bytes(schema)),
        'contract': sha256_bytes(canonical_json_bytes(contract)),
        'python_engine': sha256_file(repo_root / PYTHON_ENGINE),
        'js_engine': sha256_file(repo_root / JS_ENGINE),
        'golden_corpus': sha256_bytes(canonical_json_bytes(golden)),
        'chains': sha256_bytes(canonical_json_bytes(chains_doc)),
    }

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'errors': errors,
        'warnings': warnings,
        'task': 'N19',
        'summary': {
            'cards': len(cards),
            'steps': sum(len(c.get('steps') or []) for c in cards),
            'free_order_groups': sum(len(c.get('free_order_groups') or []) for c in cards),
            'sequence_prompts': sum(len(c.get('sequence_prompts') or []) for c in cards),
            'matching_exercises': len([c for c in cards if c.get('matching')]),
            'safety_entries': sum(len([s for s in c.get('steps') or [] if s.get('safety')]) for c in cards),
            'method_outcomes': method_outcomes,
            'n05_vectors': len(n05_rows),
            'n05_pass': sum(1 for r in n05_rows if r['status'] == 'PASS'),
            'stratum_vectors': len(stratum_rows),
            'stratum_pass': sum(1 for r in stratum_rows if r['status'] == 'PASS'),
            'signatures': len(signature_rows),
            'dangling_signatures': sum(1 for r in signature_rows if r['status'] != 'RESOLVED'),
            'copy_lint': lint['status'],
            'no_keyword_scan': 'PASS' if all(f['status'] == 'PASS' for f in source_findings) else 'FAIL',
            'no_keyword_behaviour': 'PASS' if all(r['status'] == 'PASS' for r in behaviour_rows) else 'FAIL',
        },
        'card_rows': card_rows,
        'coverage_rows': coverage_rows,
        'reference_rows': reference_rows,
        'copy_lint': lint,
        'signature_rows': signature_rows,
        'n05_rows': n05_rows,
        'stratum_rows': stratum_rows,
        'source_findings': source_findings,
        'no_keyword_behaviour': behaviour_rows,
        'budget_rows': budget_rows,
        'digests': digests,
    }


def format_summary(report: dict[str, Any]) -> str:
    s = report.get('summary', {})
    return (f"{report['status']} method-cards: {s.get('cards', 0)} cards / {s.get('steps', 0)} steps, "
            f"{s.get('method_outcomes', 0)} method outcomes covered, "
            f"{s.get('n05_pass', 0)}/{s.get('n05_vectors', 0)} N05 vectors, "
            f"{s.get('stratum_pass', 0)}/{s.get('stratum_vectors', 0)} N19 vectors, "
            f"{s.get('dangling_signatures', 0)} dangling signatures, "
            f"copy lint {s.get('copy_lint')}, no-keyword {s.get('no_keyword_scan')}, "
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
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n',
                       encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) if args.json else format_summary(report))
    if report['status'] != 'PASS':
        for error in report.get('errors', [])[:25]:
            print(f'  - {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
