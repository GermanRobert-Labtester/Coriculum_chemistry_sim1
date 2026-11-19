#!/usr/bin/env python3
"""Validate the N03 conventions island and the conflict registry.

Checks, in order:
  * the island schema (every section typed, required keys present);
  * every conversion pair is bidirectional or explicitly one-way, with exact
    inverse factors and offsets;
  * every declared composition chain recomputes from its component conversions
    with independent Fraction arithmetic (mass, volume, concentration, the
    V-04 density-defect chain, temperature offset);
  * every citation resolves to the N01 frozen inventory and to an anchor and/or
    literal in the cited master or the programme extract;
  * every tolerance class is complete and labelled PROPOSED training policy;
  * the conflict registry is complete (V-01..V-12, C01..C10), every entry has a
    status and real task bindings, the roadmap's claims and the registry's
    bindings agree in both directions, and the catalase question stays open
    verbatim;
  * the derivation vectors resolve through the same paths the runtime loader
    uses.

The build pipeline imports :func:`validate` and refuses to build on any error.
The N03 corpus plants a wrong factor, a statusless entry and a phantom task in
scratch copies; those fixtures must fail with the id and both factors named.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import (  # noqa: E402
    DEST, canonical_json_bytes, normalise_ws, parse_master, sha256_bytes,
    sha256_file, TOPIC_MASTER_PATHS,
)

CONVENTIONS_PATH = 'data/conventions.json'
INVENTORY_PATH = 'evidence/SOURCE_FREEZE_INVENTORY.json'
PROGRAMME_EXTRACT_PATH = 'evidence/programme_extracted.txt'
ROADMAP_PATH = 'Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md'
HANDOVER_PATH = 'evidence/V01_CONFLICT_ENTRY.json'
REGISTRY_OUT = 'evidence/N03_CONFLICT_REGISTRY.json'

ISLAND_ID = 'sim-conventions'
SCHEMA_VERSION = 1
STATUSES = ('resolved-by-task', 'documented-and-accepted', 'open-with-owner')
TASK_RE = re.compile(r'^N(?:0[1-9]|[1-3][0-9]|40)$')
V_IDS = [f'V-{i:02d}' for i in range(1, 13)]
C_IDS = [f'C{i:02d}' for i in range(1, 11)]
STATUS_VOCABULARY = set(STATUSES)

REQUIRED_TOP_KEYS = (
    'schema_version', 'island_id', 'title_lv', 'purpose_lv', 'source',
    'epistemic_contract', 'citation_index', 'atomic_masses',
    'compound_molar_masses', 'constants', 'unit_system',
    'concentration_bases', 'percentage_basis', 'density', 'titration',
    'potentials', 'thermodynamics', 'spectrophotometry', 'kinetics', 'tolerances',
    'rounding', 'open_questions', 'consumer_contract', 'derived_vectors', 'conflicts',
)

CONVENTION_SECTIONS = (
    'atomic_masses', 'compound_molar_masses', 'constants', 'unit_system',
    'concentration_bases', 'percentage_basis', 'density', 'titration',
    'potentials', 'thermodynamics', 'spectrophotometry', 'kinetics', 'tolerances',
    'rounding', 'open_questions',
)

N03_BINDING_IDS = ('V-04', 'V-05', 'V-06', 'V-07', 'V-09', 'V-10', 'V-11', 'V-12')


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data):
        self.parts.append(data)


def master_text(path: Path) -> str:
    parser = TextExtractor()
    parser.feed(path.read_text(encoding='utf-8'))
    parser.close()
    return normalise_ws(''.join(parser.parts))


def inventory_sources(repo_root: Path) -> dict[str, dict]:
    data = json.loads((repo_root / INVENTORY_PATH).read_text(encoding='utf-8'))
    return {source['id']: source for source in data.get('sources', [])}


def roadmap_task_ids(repo_root: Path) -> set[str]:
    text = (repo_root / ROADMAP_PATH).read_text(encoding='utf-8')
    return set(re.findall(r'^### (N\d\d) - ', text, flags=re.MULTILINE))


def roadmap_v_claims(repo_root: Path) -> dict[str, list[str]]:
    text = (repo_root / ROADMAP_PATH).read_text(encoding='utf-8')
    start = text.find('### 4.1')
    end = text.find('### 4.2', start)
    if start < 0 or end < 0:
        return {}
    claims: dict[str, list[str]] = {}
    for line in text[start:end].splitlines():
        if not line.startswith('| V-'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(cells) < 3:
            continue
        vid = cells[0]
        if vid not in V_IDS:
            continue
        claims[vid] = re.findall(r'N\d\d', cells[-1])
    # B.1.2 supplies bindings for several V rows; V-11's Section 4.1 row names
    # no task, so the binding sentence is the only roadmap claim for it. Use
    # the N03 block as a fallback rather than inventing a task.
    block = n03_block(repo_root)
    for vid, tasks in list(claims.items()):
        if tasks:
            continue
        for sentence in re.split(r'(?<=[.;])\s+', block):
            if vid not in sentence:
                continue
            tail = sentence[sentence.index(vid):]
            next_v = re.search(r'V-\d\d', tail[len(vid):])
            if next_v:
                tail = tail[:len(vid) + next_v.start()]
            found = re.findall(r'N\d\d', tail)
            if found:
                claims[vid] = found
                break
    return claims


def n03_block(repo_root: Path) -> str:
    text = (repo_root / ROADMAP_PATH).read_text(encoding='utf-8')
    start = text.find('### N03 -')
    end = text.find('### N04 -', start)
    return text[start:end] if start >= 0 and end >= 0 else ''


def n03_binding_sentence_has(block: str, vid: str, task: str) -> bool:
    for sentence in re.split(r'(?<=[.;])\s+', block):
        if vid in sentence and task in sentence:
            return True
    return False


def get_path(value, expression: str):
    """Resolve a dotted path with [id=...] list selectors."""
    parts: list[str] = []
    buffer = ''
    depth = 0
    for char in expression:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
        if char == '.' and depth == 0:
            parts.append(buffer)
            buffer = ''
        else:
            buffer += char
    parts.append(buffer)
    current = value
    for part in parts:
        match = re.fullmatch(r'([A-Za-z0-9_]+)(?:\[id=([^\]]+)\])?', part)
        if not match:
            raise KeyError(f'invalid path segment {part!r}')
        key, item_id = match.group(1), match.group(2)
        current = current[key]
        if item_id is not None:
            if not isinstance(current, list):
                raise KeyError(f'{key} is not a list')
            found = next((item for item in current if item.get('id') == item_id), None)
            if found is None:
                raise KeyError(f'{key}[id={item_id}] not found')
            current = found
    return current


def rational(obj, label: str, errors: list[str]) -> Fraction | None:
    if not isinstance(obj, dict) or 'num' not in obj or 'den' not in obj:
        errors.append(f'{label}: expected a rational object with num and den')
        return None
    num, den = obj.get('num'), obj.get('den')
    if not isinstance(num, int) or not isinstance(den, int) or den == 0:
        errors.append(f'{label}: num and den must be integers with den != 0')
        return None
    return Fraction(num, den)



UNIT_ATOMS = {
    'mg': {'mass': 1}, 'g': {'mass': 1}, 'kg': {'mass': 1},
    'mL': {'volume': 1}, 'L': {'volume': 1}, 'cm³': {'volume': 1},
    'dm³': {'volume': 1}, 'm³': {'volume': 1},
    'mol': {'amount': 1}, 'mmol': {'amount': 1}, 'µmol': {'amount': 1}, 'nmol': {'amount': 1},
    '°C': {'temperature': 1}, 'K': {'temperature': 1},
    '%': {}, 'fraction': {}, 'ppm': {},
    'percent_m_v': {'mass': 1, 'volume': -1},
    'fraction_m_v': {'mass': 1, 'volume': -1},
}
SPECIAL_UNITS = {'% (m/V)': 'percent_m_v', 'fraction (m/V)': 'fraction_m_v'}


def parse_unit_expr(unit: str) -> dict[str, int]:
    """Parse a small unit expression into atom -> exponent (numerator +, denominator -)."""
    if not isinstance(unit, str) or not unit.strip():
        raise ValueError('empty unit')
    if unit in SPECIAL_UNITS:
        return {SPECIAL_UNITS[unit]: 1}
    if unit.count('/') > 1:
        raise ValueError(f'only one solidus is supported in {unit!r}')
    if '/' in unit:
        numerator, denominator = unit.split('/', 1)
    else:
        numerator, denominator = unit, ''
    expression: dict[str, int] = {}
    for part, sign in ((numerator, 1), (denominator, -1)):
        for token in re.split(r'[·*]', part):
            token = token.strip()
            if not token:
                continue
            atom = SPECIAL_UNITS.get(token, token)
            expression[atom] = expression.get(atom, 0) + sign
    return {atom: exponent for atom, exponent in expression.items() if exponent}


def expr_key(expression: dict[str, int]) -> tuple:
    return tuple(sorted((atom, exponent) for atom, exponent in expression.items() if exponent))


def expr_text(expression: dict[str, int]) -> str:
    if not expression:
        return '1'
    numerator = [atom if exponent == 1 else f'{atom}^{exponent}'
                 for atom, exponent in sorted(expression.items()) if exponent > 0]
    denominator = [atom if exponent == -1 else f'{atom}^{-exponent}'
                   for atom, exponent in sorted(expression.items()) if exponent < 0]
    return '/'.join(['·'.join(numerator) or '1', '·'.join(denominator)]) if denominator else '·'.join(numerator)


def expr_dimension(expression: dict[str, int]) -> dict[str, int]:
    dimension: dict[str, int] = {}
    for atom, exponent in expression.items():
        if atom not in UNIT_ATOMS:
            raise ValueError(f'unknown unit atom {atom!r}')
        for base, power in UNIT_ATOMS[atom].items():
            dimension[base] = dimension.get(base, 0) + power * exponent
    return {base: power for base, power in dimension.items() if power}


def decimal_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    sign = '-' if value < 0 else ''
    numerator = abs(value.numerator)
    denominator = value.denominator
    # Exact decimal when the denominator is 2^a * 5^b.
    remainder = denominator
    for factor in (2, 5):
        while remainder % factor == 0:
            remainder //= factor
    if remainder != 1:
        return f'{value.numerator}/{value.denominator}'
    digits = 0
    scaled = numerator
    while scaled % denominator:
        scaled *= 10
        digits += 1
    scaled //= denominator
    text = str(scaled).rjust(digits + 1, '0')
    return f'{sign}{text[:-digits]}.{text[-digits:]}' if digits else f'{sign}{text}'


def validate_citation(citation: dict, inventory: dict[str, dict], repo_root: Path,
                      master_cache: dict[str, str], errors: list[str]) -> dict:
    cid = citation.get('id', '<missing-id>')
    source_id = citation.get('source_id')
    source_class = citation.get('source_class')
    result = {'id': cid, 'source_id': source_id, 'source_class': source_class,
              'anchor': citation.get('anchor'), 'literal': citation.get('literal'),
              'status': 'PASS', 'failures': []}

    def fail(message: str) -> None:
        errors.append(f'Citation {cid}: {message}')
        result['status'] = 'FAIL'
        result['failures'].append(message)

    if source_id not in inventory:
        fail(f'source_id {source_id!r} is not in the N01 inventory')
        return result
    source = inventory[source_id]
    if source.get('status') != 'FROZEN':
        fail(f'source {source_id} is not FROZEN (status {source.get("status")})')
    role = source.get('role')
    if role == 'canonical-master':
        if source_class != 'master':
            fail(f'canonical master {source_id} must use source_class "master", got {source_class!r}')
    elif role in ('official-programme', 'programme-transcription'):
        if source_class != 'official-programme':
            fail(f'official programme {source_id} must use source_class "official-programme", got {source_class!r}')
    elif source_class not in ('predecessor-audit', 'inspection-record', 'n01-record', 'n03-record'):
        fail(f'source role {role!r} is not allowed for a conventions citation (source_class {source_class!r})')

    anchor = citation.get('anchor')
    literals = []
    if citation.get('literal'):
        literals.append(citation['literal'])
    literals.extend(citation.get('literals') or [])

    if role == 'canonical-master':
        path = repo_root / source['path']
        if not path.is_file():
            fail(f'master file missing: {source["path"]}')
            return result
        text = master_cache.get(source_id)
        if text is None:
            text = master_text(path)
            master_cache[source_id] = text
        if anchor:
            index = parse_master(path)
            if anchor not in index.ids:
                fail(f'anchor #{anchor} does not exist in {source_id}')
        if not literals and not anchor:
            fail('citation has neither anchor nor literal; cannot machine-check it')
        for literal in literals:
            if normalise_ws(literal) not in text:
                fail(f'literal not found in {source_id}: {literal!r}')
    elif role == 'official-programme':
        if source_id in ('PROGRAMME-PDF', 'PROGRAMME-EXTRACT'):
            programme = normalise_ws((repo_root / PROGRAMME_EXTRACT_PATH).read_text(encoding='utf-8'))
            if not literals:
                fail('official-programme citation needs a literal from the extract')
            for literal in literals:
                if normalise_ws(literal) not in programme:
                    fail(f'literal not found in programme extract: {literal!r}')
        else:
            fail(f'official-programme source {source_id} has no text adapter')
    else:
        # Predecessor/inspection records are checked by their own tasks; here we
        # only require that the path exists and the literal is present.
        path = repo_root / source.get('path', '')
        if path.is_file() and literals:
            text = normalise_ws(path.read_text(encoding='utf-8', errors='replace'))
            for literal in literals:
                if normalise_ws(literal) not in text:
                    fail(f'literal not found in {source_id}: {literal!r}')
    return result


def validate(island_path: str | Path = DEST / CONVENTIONS_PATH,
             repo_root: str | Path = DEST,
             check_citations: bool = True,
             check_registry: bool = True) -> dict:
    repo_root = Path(repo_root)
    island_file = Path(island_path)
    if not island_file.is_absolute():
        island_file = repo_root / island_file
    errors: list[str] = []
    report: dict = {
        'schema_version': 1,
        'task': 'N03',
        'artifact': 'conventions-validation',
        'island': str(island_file.relative_to(repo_root)) if island_file.is_relative_to(repo_root) else str(island_file),
        'island_sha256': sha256_file(island_file) if island_file.is_file() else None,
        'island_bytes': island_file.stat().st_size if island_file.is_file() else None,
        'counts': {},
        'checks': {},
        'citation_results': [],
        'chain_results': [],
        'registry_results': {},
        'vector_results': [],
        'errors': errors,
        'status': 'FAIL',
    }
    if not island_file.is_file():
        errors.append(f'Conventions island missing: {island_file}')
        return report
    raw = island_file.read_bytes()
    try:
        island = json.loads(raw.decode('utf-8'))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f'Conventions island is not readable UTF-8 JSON: {exc}')
        return report
    if not isinstance(island, dict):
        errors.append('Conventions island root must be a JSON object')
        return report

    # ---- schema -----------------------------------------------------------
    for key in REQUIRED_TOP_KEYS:
        if key not in island:
            errors.append(f'Missing island section: {key}')
    if island.get('schema_version') != SCHEMA_VERSION:
        errors.append(f'island schema_version is {island.get("schema_version")!r}, expected {SCHEMA_VERSION}')
    if island.get('island_id') != ISLAND_ID:
        errors.append(f'island_id is {island.get("island_id")!r}, expected {ISLAND_ID!r}')
    for key in ('title_lv', 'purpose_lv'):
        if not isinstance(island.get(key), str) or not island[key].strip():
            errors.append(f'{key} must be a non-empty string')
    if b'\\u' in raw:
        errors.append('island source escapes non-ASCII text as \\uXXXX; the emission rule is UTF-8 with Latvian text intact')

    # ---- citations --------------------------------------------------------
    inventory = inventory_sources(repo_root)
    citations = island.get('citation_index') or []
    citation_map: dict[str, dict] = {}
    master_cache: dict[str, str] = {}
    if not isinstance(citations, list) or not citations:
        errors.append('citation_index must be a non-empty list')
    else:
        for citation in citations:
            cid = citation.get('id')
            if not isinstance(cid, str) or not cid:
                errors.append('citation_index contains an entry without id')
                continue
            if cid in citation_map:
                errors.append(f'duplicate citation id {cid}')
                continue
            citation_map[cid] = citation
            if check_citations:
                report['citation_results'].append(validate_citation(citation, inventory, repo_root, master_cache, errors))
            else:
                report['citation_results'].append({'id': cid, 'status': 'SKIPPED'})

    citation_use: dict[str, int] = {cid: 0 for cid in citation_map}

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            if 'citations' in node:
                ids = node['citations']
                if not isinstance(ids, list) or not ids:
                    errors.append(f'{path}.citations must be a non-empty list')
                else:
                    for cid in ids:
                        if cid not in citation_map:
                            errors.append(f'{path}.citations references unknown citation id {cid!r}')
                        else:
                            citation_use[cid] += 1
            for key, value in node.items():
                if key == 'citation_index':
                    continue
                walk(value, f'{path}.{key}' if path else key)
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(value, f'{path}[{index}]')

    walk(island, '')

    def count_citations(node) -> int:
        if isinstance(node, dict):
            total = len(node.get('citations') or []) if isinstance(node.get('citations'), list) else 0
            return total + sum(count_citations(value) for key, value in node.items() if key != 'citations')
        if isinstance(node, list):
            return sum(count_citations(value) for value in node)
        return 0

    for section in CONVENTION_SECTIONS:
        if not isinstance(island.get(section), (dict, list)):
            errors.append(f'section {section} must be an object or list')
        elif section != 'open_questions' and count_citations(island.get(section)) == 0:
            errors.append(f'section {section} has no citation; every convention needs a source')
    for cid, count in citation_use.items():
        if count == 0:
            errors.append(f'citation {cid} is defined but never used by a convention entry')

    # ---- conversions ------------------------------------------------------
    unit_system = island.get('unit_system') or {}
    conversions = unit_system.get('conversions') or []
    chains = unit_system.get('chains') or []
    conversion_map: dict[str, dict] = {}
    pair_map: dict[tuple[str, str], str] = {}
    conversion_errors: list[str] = []
    for conversion in conversions:
        cid = conversion.get('id')
        if not isinstance(cid, str) or not cid:
            conversion_errors.append('conversion without id')
            continue
        if cid in conversion_map:
            conversion_errors.append(f'duplicate conversion id {cid}')
        conversion_map[cid] = conversion
        pair = (conversion.get('from'), conversion.get('to'))
        if pair in pair_map:
            conversion_errors.append(f'duplicate conversion pair {pair[0]} -> {pair[1]} ({pair_map[pair]} and {cid})')
        pair_map[pair] = cid
        for key in ('from', 'to', 'from_dimension', 'to_dimension', 'exactness',
                    'conversion_class', 'directionality'):
            if not isinstance(conversion.get(key), str) or not conversion[key]:
                conversion_errors.append(f'conversion {cid}.{key} must be a non-empty string')
        if conversion.get('exactness') not in unit_system.get('exactness_vocabulary', {}):
            conversion_errors.append(f'conversion {cid} has unknown exactness {conversion.get("exactness")!r}')
        if conversion.get('conversion_class') not in ('multiplicative', 'offset', 'affine', 'conditional', 'blocked', 'measured'):
            conversion_errors.append(f'conversion {cid} has unknown conversion_class {conversion.get("conversion_class")!r}')
        if conversion.get('directionality') not in ('bidirectional', 'one-way'):
            conversion_errors.append(f'conversion {cid} has unknown directionality {conversion.get("directionality")!r}')
        if conversion.get('conversion_class') == 'blocked':
            if conversion.get('factor') is not None:
                conversion_errors.append(f'blocked conversion {cid} must have factor null')
            if not conversion.get('reason_lv'):
                conversion_errors.append(f'blocked conversion {cid} needs reason_lv')
        else:
            factor = rational(conversion.get('factor'), f'conversion {cid}.factor', conversion_errors)
            if factor is not None and factor <= 0:
                conversion_errors.append(f'conversion {cid}.factor must be positive')
            if conversion.get('conversion_class') == 'conditional' and not conversion.get('condition_lv'):
                conversion_errors.append(f'conditional conversion {cid} needs condition_lv')
            if conversion.get('conversion_class') == 'offset':
                offset = rational(conversion.get('offset', {'num': 0, 'den': 1}), f'conversion {cid}.offset', conversion_errors)
                if offset is not None and factor != 1:
                    conversion_errors.append(f'offset conversion {cid} must have factor 1, got {factor}')
    # inverse check
    for conversion in conversions:
        cid = conversion.get('id')
        if conversion.get('directionality') != 'bidirectional':
            if not (conversion.get('reason_lv') or conversion.get('condition_lv')):
                conversion_errors.append(f'one-way conversion {cid} must state a reason or condition')
            continue
        reverse_id = pair_map.get((conversion.get('to'), conversion.get('from')))
        if reverse_id is None:
            conversion_errors.append(f'bidirectional conversion {cid} has no inverse pair {conversion.get("to")} -> {conversion.get("from")}')
            continue
        reverse = conversion_map[reverse_id]
        fwd_factor = rational(conversion.get('factor'), f'conversion {cid}.factor', conversion_errors)
        rev_factor = rational(reverse.get('factor'), f'conversion {reverse_id}.factor', conversion_errors)
        if fwd_factor is None or rev_factor is None:
            continue
        if conversion.get('conversion_class') == 'offset':
            fwd_offset = rational(conversion.get('offset', {'num': 0, 'den': 1}), f'conversion {cid}.offset', conversion_errors)
            rev_offset = rational(reverse.get('offset', {'num': 0, 'den': 1}), f'conversion {reverse_id}.offset', conversion_errors)
            if fwd_offset is not None and rev_offset is not None and fwd_offset != -rev_offset:
                conversion_errors.append(f'offset inverse mismatch {cid} ({decimal_text(fwd_offset)}) and {reverse_id} ({decimal_text(rev_offset)})')
        else:
            if fwd_factor * rev_factor != 1:
                conversion_errors.append(f'inverse factor mismatch {cid} ({decimal_text(fwd_factor)}) and {reverse_id} ({decimal_text(rev_factor)})')
            fwd_offset = rational(conversion.get('offset', {'num': 0, 'den': 1}), f'conversion {cid}.offset', conversion_errors)
            rev_offset = rational(reverse.get('offset', {'num': 0, 'den': 1}), f'conversion {reverse_id}.offset', conversion_errors)
            if fwd_offset not in (None, 0) or rev_offset not in (None, 0):
                conversion_errors.append(f'multiplicative conversion {cid}/{reverse_id} must not carry an offset')
    # dimension sanity for every conversion (conditional and blocked are exempt)
    for conversion in conversions:
        cid = conversion.get('id')
        if conversion.get('exactness') == 'conditional' or conversion.get('conversion_class') == 'blocked':
            continue
        try:
            from_expr = parse_unit_expr(conversion.get('from'))
            to_expr = parse_unit_expr(conversion.get('to'))
            if expr_dimension(from_expr) != expr_dimension(to_expr):
                conversion_errors.append(
                    f'conversion {cid}: dimensions differ, {expr_dimension(from_expr)} -> {expr_dimension(to_expr)}'
                )
        except Exception as exc:
            conversion_errors.append(f'conversion {cid}: unit expression cannot be parsed: {exc}')
    errors.extend(conversion_errors)
    report['checks']['conversions'] = {
        'count': len(conversions),
        'bidirectional': sum(1 for c in conversions if c.get('directionality') == 'bidirectional'),
        'one_way': sum(1 for c in conversions if c.get('directionality') == 'one-way'),
        'blocked': sum(1 for c in conversions if c.get('conversion_class') == 'blocked'),
        'errors': len(conversion_errors),
    }

    # ---- composition chains ----------------------------------------------
    chain_map: dict[str, dict] = {}
    chain_results: list[dict] = []
    for chain in chains:
        cid = chain.get('id')
        result = {'id': cid, 'kind': chain.get('kind'), 'from': chain.get('from'),
                  'to': chain.get('to'), 'status': 'PASS'}
        if not isinstance(cid, str) or not cid:
            errors.append('composition chain without id')
            continue
        if cid in chain_map:
            errors.append(f'duplicate chain id {cid}')
            continue
        chain_map[cid] = chain
        kind = chain.get('kind')
        if kind not in ('multiplicative', 'affine', 'symbolic'):
            errors.append(f'chain {cid}: unknown kind {kind!r}')
            result['status'] = 'FAIL'
            chain_results.append(result)
            continue
        if kind == 'symbolic':
            if not chain.get('formula'):
                errors.append(f'symbolic chain {cid} needs formula')
                result['status'] = 'FAIL'
            if not chain.get('requires'):
                errors.append(f'symbolic chain {cid} needs requires')
                result['status'] = 'FAIL'
            chain_results.append(result)
            continue
        steps = chain.get('steps') or []
        if not steps:
            errors.append(f'chain {cid} has no steps')
            result['status'] = 'FAIL'
            chain_results.append(result)
            continue
        step_failures: list[str] = []
        try:
            current_expr = parse_unit_expr(chain.get('from'))
            target_expr = parse_unit_expr(chain.get('to'))
            start_dimension = expr_dimension(current_expr)
            target_dimension = expr_dimension(target_expr)
        except Exception as exc:
            errors.append(f'Chain {cid}: unit expression cannot be parsed: {exc}')
            result['status'] = 'FAIL'
            chain_results.append(result)
            continue
        if start_dimension != target_dimension:
            step_failures.append(
                f'dimension mismatch: from {chain.get("from")} has {start_dimension}, '
                f'to {chain.get("to")} has {target_dimension}'
            )
        scale = Fraction(1)
        shift = Fraction(0)
        for step in steps:
            conversion_id = step.get('conversion')
            power = step.get('power')
            position = step.get('position')
            if conversion_id not in conversion_map:
                step_failures.append(f'unknown conversion {conversion_id!r}')
                continue
            if power not in (-1, 1):
                step_failures.append(f'step power for {conversion_id} is {power!r}; only -1 and 1 are supported')
                continue
            if position not in ('numerator', 'denominator'):
                step_failures.append(f'step {conversion_id} needs position numerator or denominator')
                continue
            if (position == 'numerator' and power != 1) or (position == 'denominator' and power != -1):
                step_failures.append(
                    f'step {conversion_id}: position {position} and power {power} are inconsistent'
                )
                continue
            conversion = conversion_map[conversion_id]
            if conversion.get('conversion_class') == 'blocked':
                step_failures.append(f'blocked conversion {conversion_id} cannot appear in a numeric chain')
                continue
            try:
                from_expr = parse_unit_expr(conversion.get('from'))
                to_expr = parse_unit_expr(conversion.get('to'))
            except Exception as exc:
                step_failures.append(f'conversion {conversion_id} unit expression is invalid: {exc}')
                continue
            if len(from_expr) != 1 or list(from_expr.values())[0] != 1:
                step_failures.append(f'step conversion {conversion_id} must have a single atom in from')
                continue
            from_atom = next(iter(from_expr))
            sign = 1 if position == 'numerator' else -1
            if current_expr.get(from_atom, 0) * sign <= 0:
                step_failures.append(
                    f'unit {conversion.get("from")} is not present in the {position} of {expr_text(current_expr)}'
                )
                continue
            current_expr[from_atom] -= sign
            for atom, exponent in to_expr.items():
                current_expr[atom] = current_expr.get(atom, 0) + sign * exponent
            current_expr = {atom: exponent for atom, exponent in current_expr.items() if exponent}
            factor = rational(conversion.get('factor'), f'conversion {conversion_id}.factor', errors)
            offset = rational(conversion.get('offset', {'num': 0, 'den': 1}), f'conversion {conversion_id}.offset', errors)
            if factor is None or offset is None:
                step_failures.append(f'conversion {conversion_id} has no usable factor/offset')
                continue
            contribution = factor if power == 1 else Fraction(1, 1) / factor
            if offset:
                if position != 'numerator' or power != 1:
                    step_failures.append(f'offset conversion {conversion_id} cannot be used in the denominator')
                    continue
                shift = shift * contribution + offset
                scale = scale * contribution
            else:
                shift = shift * contribution
                scale = scale * contribution
        if expr_key(current_expr) != expr_key(target_expr):
            step_failures.append(
                f'unit algebra mismatch: composed {expr_text(current_expr)} != declared {expr_text(target_expr)}'
            )
        declared_factor = rational(chain.get('factor'), f'chain {cid}.factor', errors)
        declared_offset = rational(chain.get('offset', {'num': 0, 'den': 1}), f'chain {cid}.offset', errors)
        if declared_factor is None or declared_offset is None:
            step_failures.append('chain has no usable declared factor/offset')
        else:
            if declared_factor != scale:
                step_failures.append(
                    f'factor mismatch: declared {decimal_text(declared_factor)} != computed {decimal_text(scale)}'
                )
            if declared_offset != shift:
                step_failures.append(
                    f'offset mismatch: declared {decimal_text(declared_offset)} != computed {decimal_text(shift)}'
                )
        result['declared_factor'] = decimal_text(declared_factor) if declared_factor is not None else None
        result['computed_factor'] = decimal_text(scale)
        result['declared_offset'] = decimal_text(declared_offset) if declared_offset is not None else None
        result['computed_offset'] = decimal_text(shift)
        result['composed_unit'] = expr_text(current_expr)
        if step_failures:
            result['status'] = 'FAIL'
            result['failures'] = step_failures
            for failure in step_failures:
                errors.append(f'Chain {cid}: {failure}')
        chain_results.append(result)
    report['chain_results'] = chain_results
    report['checks']['chains'] = {
        'count': len(chains),
        'numeric': sum(1 for chain in chains if chain.get('kind') in ('multiplicative', 'affine')),
        'symbolic': sum(1 for chain in chains if chain.get('kind') == 'symbolic'),
        'failed': sum(1 for result in chain_results if result.get('status') != 'PASS'),
    }

    # ---- atomic masses, compounds, constants ------------------------------
    element_symbols: set[str] = set()
    for element in island.get('atomic_masses', {}).get('elements', []):
        symbol = element.get('symbol')
        if not isinstance(symbol, str) or not symbol:
            errors.append('atomic mass element without symbol')
            continue
        if symbol in element_symbols:
            errors.append(f'duplicate atomic mass symbol {symbol}')
        element_symbols.add(symbol)
        try:
            value = Decimal(str(element.get('value')))
            if value <= 0:
                raise ValueError
        except Exception:
            errors.append(f'atomic mass {symbol} has a non-positive or non-numeric value {element.get("value")!r}')
        display = element.get('display_lv')
        cited_master_text = ''
        for cid in element.get('citations', []):
            citation = citation_map.get(cid, {})
            source = inventory.get(citation.get('source_id'), {})
            if source.get('role') == 'canonical-master':
                cited_master_text += ' ' + master_cache.get(citation.get('source_id'), '')
        if display and cited_master_text and normalise_ws(display) not in cited_master_text:
            errors.append(f'atomic mass {symbol} display {display!r} does not appear in any cited master')
    compound_formulas: set[str] = set()
    for compound in island.get('compound_molar_masses', {}).get('compounds', []):
        formula = compound.get('formula')
        if not isinstance(formula, str) or not formula:
            errors.append('compound without formula')
            continue
        if formula in compound_formulas:
            errors.append(f'duplicate compound formula {formula}')
        compound_formulas.add(formula)
        for key in ('working_value', 'display_lv'):
            if not compound.get(key):
                errors.append(f'compound {formula} missing {key}')
        cited_master_text = ''
        for cid in compound.get('citations', []):
            citation = citation_map.get(cid, {})
            source = inventory.get(citation.get('source_id'), {})
            if source.get('role') == 'canonical-master':
                cited_master_text += ' ' + master_cache.get(citation.get('source_id'), '')
        if compound.get('display_lv') and cited_master_text and normalise_ws(compound['display_lv']) not in cited_master_text:
            errors.append(f'compound {formula} display {compound["display_lv"]!r} does not appear in any cited master')
    constant_ids: set[str] = set()
    for constant in island.get('constants', {}).get('values', []):
        cid = constant.get('id')
        if not cid:
            errors.append('constant without id')
            continue
        if cid in constant_ids:
            errors.append(f'duplicate constant id {cid}')
        constant_ids.add(cid)
        try:
            Decimal(str(constant.get('value')))
        except Exception:
            errors.append(f'constant {cid} has a non-numeric value {constant.get("value")!r}')
    report['checks']['atomic_masses'] = {'elements': len(element_symbols)}
    report['checks']['compounds'] = {'compounds': len(compound_formulas)}
    report['checks']['constants'] = {'constants': len(constant_ids)}

    # ---- tolerances and rounding -----------------------------------------
    tolerance_classes = island.get('tolerances', {}).get('quantity_classes', [])
    tolerance_ids: set[str] = set()
    if island.get('tolerances', {}).get('label') != 'PROPOSED training policy':
        errors.append('tolerances.label must be "PROPOSED training policy"')
    for item in tolerance_classes:
        tid = item.get('id')
        if not tid:
            errors.append('tolerance class without id')
            continue
        if tid in tolerance_ids:
            errors.append(f'duplicate tolerance class id {tid}')
        tolerance_ids.add(tid)
        absolute = item.get('absolute') or {}
        if not absolute.get('value'):
            errors.append(f'tolerance {tid} has no absolute value')
        else:
            try:
                if Decimal(str(absolute['value'])) < 0:
                    raise ValueError
            except Exception:
                errors.append(f'tolerance {tid} absolute value is not a non-negative decimal')
        if absolute.get('label') != 'PROPOSED training policy':
            errors.append(f'tolerance {tid}.absolute.label must be PROPOSED training policy')
        if not isinstance(item.get('significant_figures'), dict) or not item['significant_figures'].get('mode'):
            errors.append(f'tolerance {tid} has no significant-figure mode')
        rounding = item.get('rounding') or {}
        if rounding.get('mode') != 'half_up':
            errors.append(f'tolerance {tid}.rounding.mode must be half_up')
        if not rounding.get('decimals'):
            errors.append(f'tolerance {tid}.rounding.decimals is missing')
        if not item.get('basis_lv'):
            errors.append(f'tolerance {tid} has no basis_lv')
    rounding = island.get('rounding') or {}
    if rounding.get('rule') != 'half_up':
        errors.append('rounding.rule must be half_up')
    if rounding.get('final_only') is not True:
        errors.append('rounding.final_only must be true')
    for example in rounding.get('examples', []):
        try:
            value = Decimal(str(example['input']))
            digits = int(example['digits'])
            if example['mode'] == 'decimal_places':
                quant = Decimal(1).scaleb(-digits)
            elif example['mode'] == 'significant_figures':
                if value == 0:
                    raise ValueError('zero has no significant-figure position')
                exponent = value.adjusted()
                quant = Decimal(1).scaleb(exponent - digits + 1)
            else:
                raise ValueError(f'unknown mode {example["mode"]!r}')
            computed = value.quantize(quant, rounding=ROUND_HALF_UP)
            if computed != Decimal(str(example['output'])):
                errors.append(f'rounding example {example["input"]} -> {example["output"]} recomputes to {computed}')
        except Exception as exc:
            errors.append(f'rounding example is invalid ({example}): {exc}')
    report['checks']['tolerances'] = {'classes': len(tolerance_ids), 'rounding_examples': len(rounding.get('examples', []))}

    # ---- percentage / density / titration / potentials / spectro ---------
    bases = {basis.get('id') for basis in island.get('concentration_bases', {}).get('bases', [])}
    for required in ('m_m', 'm_v', 'v_v', 'molar'):
        if required not in bases:
            errors.append(f'concentration_bases is missing {required}')
    pct = island.get('percentage_basis') or {}
    if pct.get('label_required') is not True:
        errors.append('percentage_basis.label_required must be true')
    if pct.get('default_basis') not in bases:
        errors.append(f'percentage_basis.default_basis {pct.get("default_basis")!r} is not a defined basis')
    if not pct.get('unlabeled_percent'):
        errors.append('percentage_basis.unlabeled_percent is missing')
    density = island.get('density') or {}
    for cid in density.get('blocked_conversion_ids', []):
        if cid not in conversion_map:
            errors.append(f'density.blocked_conversion_ids references unknown conversion {cid}')
        elif conversion_map[cid].get('conversion_class') != 'blocked':
            errors.append(f'density.blocked_conversion_ids {cid} is not blocked')
    if density.get('v04_chain_id') not in chain_map:
        errors.append(f'density.v04_chain_id {density.get("v04_chain_id")!r} is not a chain')
    titration = island.get('titration') or {}
    for key in ('meniscus', 'burette', 'endpoint'):
        if not isinstance(titration.get(key), dict):
            errors.append(f'titration.{key} must be an object')
    if titration.get('endpoint', {}).get('persistence_criterion') != 'supplied_by_task':
        errors.append('titration.endpoint.persistence_criterion must be supplied_by_task')
    if titration.get('endpoint', {}).get('no_universal_time') is not True:
        errors.append('titration.endpoint.no_universal_time must be true')
    potential_symbols = {item.get('id') for item in island.get('potentials', {}).get('symbols', [])}
    for required in ('E_zero', 'E_actual', 'E_prime'):
        if required not in potential_symbols:
            errors.append(f'potentials.symbols is missing {required}')
    if not island.get('potentials', {}).get('mixing_rule_lv'):
        errors.append('potentials.mixing_rule_lv is missing')
    for value in island.get('potentials', {}).get('reference_values', []):
        if value.get('convention') not in potential_symbols:
            errors.append(f'potential reference value {value.get("id")} uses unknown convention {value.get("convention")}')
    wavelength = island.get('spectrophotometry', {}).get('wavelength', {})
    if wavelength.get('status') != 'course instrument setting':
        errors.append('spectrophotometry.wavelength.status must be "course instrument setting"')
    if wavelength.get('flatness_claim') != 'bounded inference, not a measurement':
        errors.append('spectrophotometry.wavelength.flatness_claim must be a bounded inference')
    path = island.get('spectrophotometry', {}).get('optical_path', {})
    if path.get('status') != 'declared assumption, not verified for the actual cuvette':
        errors.append('spectrophotometry.optical_path.status must be a declared assumption')
    calibration = island.get('spectrophotometry', {}).get('calibration', {})
    if calibration.get('no_extrapolation_rule_lv') is None:
        errors.append('spectrophotometry.calibration.no_extrapolation_rule_lv is missing')

    # ---- consumer contract and vectors ------------------------------------
    contract = island.get('consumer_contract') or {}
    if contract.get('island_id') != ISLAND_ID:
        errors.append('consumer_contract.island_id must be sim-conventions')
    if contract.get('no_local_copies') is not True:
        errors.append('consumer_contract.no_local_copies must be true')
    roadmap_tasks = roadmap_task_ids(repo_root)
    consumer_tasks = {consumer.get('task') for consumer in contract.get('consumers', [])}
    for required in ('N05', 'N10', 'N11', 'N12', 'N13', 'N14', 'N15', 'N17', 'N18', 'N19'):
        if required not in consumer_tasks:
            errors.append(f'consumer_contract.consumers is missing {required}')
    for task in consumer_tasks:
        if task not in roadmap_tasks:
            errors.append(f'consumer_contract.consumers names unknown task {task}')
    vector_ids: set[str] = set()
    for vector in island.get('derived_vectors', []):
        vid = vector.get('id')
        if not vid:
            errors.append('derived vector without id')
            continue
        if vid in vector_ids:
            errors.append(f'duplicate derived vector id {vid}')
        vector_ids.add(vid)
        if vector.get('consumer') not in roadmap_tasks:
            errors.append(f'derived vector {vid} names unknown consumer {vector.get("consumer")}')
        try:
            resolved = get_path(island, vector.get('source_ref', ''))
        except Exception as exc:
            errors.append(f'derived vector {vid} source_ref cannot be resolved: {exc}')
            report['vector_results'].append({'id': vid, 'status': 'FAIL', 'error': str(exc)})
            continue
        if isinstance(resolved, dict) and 'num' in resolved and 'den' in resolved:
            resolved = decimal_text(Fraction(resolved['num'], resolved['den']))
        report['vector_results'].append({
            'id': vid, 'consumer': vector.get('consumer'), 'kind': vector.get('kind'),
            'source_ref': vector.get('source_ref'), 'resolved': str(resolved), 'status': 'PASS',
        })

    # ---- conflict registry ------------------------------------------------
    registry = island.get('conflicts') or {}
    registry_results: dict = {}
    registry_digest = None
    if not isinstance(registry, dict):
        errors.append('conflicts must be an object')
    else:
        entries = registry.get('entries') or []
        entry_map = {entry.get('id'): entry for entry in entries if entry.get('id')}
        if set(registry.get('status_vocabulary') or []) != STATUS_VOCABULARY:
            errors.append('conflicts.status_vocabulary must be exactly resolved-by-task, documented-and-accepted, open-with-owner')
        if not registry.get('append_rule_lv'):
            errors.append('conflicts.append_rule_lv is missing')
        expected_ids = set(V_IDS) | set(C_IDS)
        actual_ids = set(entry_map)
        for missing in sorted(expected_ids - actual_ids):
            errors.append(f'conflict registry is missing {missing}')
        for extra in sorted(actual_ids - expected_ids):
            errors.append(f'conflict registry has unexpected id {extra}')
        claims = roadmap_v_claims(repo_root)
        block = n03_block(repo_root)
        registry_errors: list[str] = []
        for entry_id in sorted(expected_ids & actual_ids):
            entry = entry_map[entry_id]
            prefix = f'Conflict {entry_id}'
            status = entry.get('status')
            if status not in STATUS_VOCABULARY:
                registry_errors.append(f'{prefix}: status is missing or unknown ({status!r})')
            if not entry.get('status_reason'):
                registry_errors.append(f'{prefix}: status_reason is missing')
            if not entry.get('owner'):
                registry_errors.append(f'{prefix}: owner is missing')
            if not entry.get('epistemic_label'):
                registry_errors.append(f'{prefix}: epistemic_label is missing')
            history = entry.get('history') or []
            if not history:
                registry_errors.append(f'{prefix}: history is empty')
            else:
                for event in history:
                    event_task = event.get('task')
                    if event_task not in roadmap_tasks:
                        registry_errors.append(f'{prefix}: history names unknown task {event_task!r}')
                    if event.get('status') not in STATUS_VOCABULARY:
                        registry_errors.append(f'{prefix}: history event has unknown status {event.get("status")!r}')
                if history[-1].get('status') != status:
                    registry_errors.append(f'{prefix}: status {status!r} does not match last history event {history[-1].get("status")!r}')
                if any(event.get('event') == 'reopened' for event in history) and len(history) < 2:
                    registry_errors.append(f'{prefix}: a reopened entry must retain prior history')
            task_fields = []
            for key in ('resolution_task', 'mitigation_task', 'binding_task'):
                if entry.get(key):
                    task_fields.append(entry[key])
            for key in ('enforcement_tasks', 'supporting_tasks'):
                task_fields.extend(entry.get(key) or [])
            for task in task_fields:
                if task not in roadmap_tasks:
                    registry_errors.append(f'{prefix}: names unknown task {task!r}')
            if status == 'resolved-by-task':
                if not entry.get('resolution_task'):
                    registry_errors.append(f'{prefix}: resolved-by-task needs resolution_task')
                elif entry['resolution_task'] not in roadmap_tasks:
                    registry_errors.append(f'{prefix}: resolution_task {entry["resolution_task"]!r} is not a roadmap task')
                if not entry.get('resolution_text'):
                    registry_errors.append(f'{prefix}: resolved-by-task needs resolution_text')
            elif status == 'open-with-owner':
                if not entry.get('owner'):
                    registry_errors.append(f'{prefix}: open-with-owner needs owner')
                if entry_id in ('V-08', 'C05') and not entry.get('question_verbatim'):
                    registry_errors.append(f'{prefix}: the catalase question must be carried open verbatim')
            elif status == 'documented-and-accepted':
                if not entry.get('status_reason') or not entry.get('owner'):
                    registry_errors.append(f'{prefix}: documented-and-accepted needs reason and owner')
            if entry_id in V_IDS:
                if entry_id not in claims:
                    registry_errors.append(f'{prefix}: roadmap Section 4.1 has no claim row for this V id')
                else:
                    claimed = claims[entry_id]
                    if not claimed:
                        registry_errors.append(f'{prefix}: roadmap claim row names no task')
                    if entry.get('roadmap_claim_task_ids') != claimed:
                        registry_errors.append(
                            f'{prefix}: roadmap_claim_task_ids {entry.get("roadmap_claim_task_ids")} do not match the roadmap row {claimed}'
                        )
                    bound = set(task_fields) | {entry.get('resolution_task')}
                    for task in claimed:
                        if task not in bound:
                            registry_errors.append(f'{prefix}: roadmap claims {task}, but the registry binds no such task')
                    if entry_id in N03_BINDING_IDS:
                        binding_task = entry.get('binding_task')
                        if not binding_task or not n03_binding_sentence_has(block, entry_id, binding_task):
                            registry_errors.append(
                                f'{prefix}: binding_task {binding_task!r} is not present with the id in the N03 Main Step B.1.2 text'
                            )
        # B.1.2 may bind V-10 and V-11 to N31; the sentence check above covers both.
        for observation in registry.get('observations', []):
            oid = observation.get('id')
            if not oid:
                registry_errors.append('observation without id')
                continue
            if observation.get('status') not in STATUS_VOCABULARY:
                registry_errors.append(f'Observation {oid}: status is missing or unknown')
            if not observation.get('owner'):
                registry_errors.append(f'Observation {oid}: owner is missing')
            if observation.get('resolution_task') and observation['resolution_task'] not in roadmap_tasks:
                registry_errors.append(f'Observation {oid}: unknown resolution_task {observation["resolution_task"]!r}')
            for event in observation.get('history') or []:
                if event.get('task') not in roadmap_tasks:
                    registry_errors.append(f'Observation {oid}: history names unknown task {event.get("task")!r}')
        # findings and catalase text
        for entry_id in ('V-08', 'C05'):
            entry = entry_map.get(entry_id) or {}
            question = entry.get('question_verbatim') or ''
            for needle in ('23 J', 'docētāja', 'katalāz'):
                if needle.lower() not in question.lower():
                    registry_errors.append(f'{entry_id}: catalase question verbatim is missing {needle!r}')
            if entry.get('status') != 'open-with-owner':
                registry_errors.append(f'{entry_id}: catalase question must remain open-with-owner')
        c10 = entry_map.get('C10') or {}
        if 'catalase' not in json.dumps(c10, ensure_ascii=False).lower():
            registry_errors.append('C10: the C10/C05 nomenclature note is missing')
        # N01 handover fidelity: the V-01 entry must preserve the handed-over
        # finding, status, evidence and mitigation strings verbatim.
        handover_path = repo_root / HANDOVER_PATH
        if handover_path.is_file():
            handover = json.loads(handover_path.read_text(encoding='utf-8'))
            source_entry = (handover.get('entries') or [{}])[0]
            target_entry = entry_map.get('V-01') or {}
            for key in ('id', 'title', 'class', 'finding', 'status', 'status_reason',
                        'owner', 'resolution_task', 'mitigation_task', 'mitigation',
                        'evidence', 'epistemic_label', 'handoff_notes'):
                if source_entry.get(key) != target_entry.get(key):
                    registry_errors.append(f'V-01: handover field {key} was not preserved verbatim')
        else:
            registry_errors.append(f'V-01 handover record is missing: {HANDOVER_PATH}')
        errors.extend(registry_errors)
        registry_digest = sha256_bytes(canonical_json_bytes(registry))
        registry_results = {
            'entry_count': len(entries),
            'v_count': sum(1 for e in entries if e.get('id') in V_IDS),
            'c_count': sum(1 for e in entries if e.get('id') in C_IDS),
            'observation_count': len(registry.get('observations', [])),
            'status_counts': {status: sum(1 for e in entries if e.get('status') == status) for status in STATUSES},
            'roadmap_claims': claims,
            'roadmap_tasks': len(roadmap_tasks),
            'digest': registry_digest,
            'errors': registry_errors,
        }
    report['registry_results'] = registry_results
    report['checks']['registry'] = {
        'status': 'PASS' if not registry_results.get('errors') else 'FAIL',
        'entries': registry_results.get('entry_count'),
        'status_counts': registry_results.get('status_counts'),
    }

    report['counts'] = {
        'citations': len(citation_map),
        'atomic_masses': len(element_symbols),
        'compounds': len(compound_formulas),
        'constants': len(constant_ids),
        'conversions': len(conversion_map),
        'chains': len(chain_map),
        'tolerance_classes': len(tolerance_ids),
        'conflict_v': registry_results.get('v_count', 0),
        'conflict_c': registry_results.get('c_count', 0),
        'observations': registry_results.get('observation_count', 0),
        'derived_vectors': len(vector_ids),
    }
    report['checks']['citations'] = {
        'defined': len(citation_map),
        'used': sum(1 for count in citation_use.values() if count > 0),
        'failed': sum(1 for result in report['citation_results'] if result.get('status') == 'FAIL'),
    }
    if check_registry and registry_digest is None:
        errors.append('registry digest could not be computed')
    report['status'] = 'PASS' if not errors else 'FAIL'
    return report


def format_summary(report: dict) -> str:
    counts = report.get('counts', {})
    return (
        f"{report.get('status', 'FAIL')} conventions: "
        f"{counts.get('atomic_masses', 0)} elements, "
        f"{counts.get('compounds', 0)} compounds, "
        f"{counts.get('constants', 0)} constants, "
        f"{counts.get('conversions', 0)} conversions, "
        f"{counts.get('chains', 0)} chains, "
        f"{counts.get('tolerance_classes', 0)} tolerance classes, "
        f"{counts.get('conflict_v', 0)} V + {counts.get('conflict_c', 0)} C conflicts, "
        f"{counts.get('derived_vectors', 0)} vectors"
    )


def registry_export(island: dict, report: dict) -> dict:
    registry = island['conflicts']
    return {
        'schema_version': 1,
        'artifact': 'conflict-registry',
        'task': 'N03',
        'source': CONVENTIONS_PATH,
        'source_sha256': report.get('island_sha256'),
        'registry_sha256': sha256_bytes(canonical_json_bytes(registry)),
        'status_vocabulary': registry['status_vocabulary'],
        'append_rule_lv': registry['append_rule_lv'],
        'entries': registry['entries'],
        'observations': registry['observations'],
        'handoff_to_N40': registry['handoff_to_N40'],
        'validation': {
            'status': report['status'],
            'counts': report.get('counts'),
            'registry': report.get('registry_results', {}).get('status_counts'),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--island', default=str(DEST / CONVENTIONS_PATH))
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--report', default=None, help='write the machine-readable validation record')
    parser.add_argument('--registry-out', default=None, help='write the standalone conflict-registry artifact')
    parser.add_argument('--no-citations', action='store_true', help='skip citation resolution (scratch composition fixtures)')
    parser.add_argument('--no-registry', action='store_true', help='skip registry checks (scratch composition fixtures)')
    args = parser.parse_args(argv)
    root = Path(args.repo_root)
    island_path = Path(args.island)
    if not island_path.is_absolute():
        island_path = root / island_path
    report = validate(island_path=island_path, repo_root=root,
                      check_citations=not args.no_citations,
                      check_registry=not args.no_registry)
    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = root / report_path
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if args.registry_out:
        registry_path = Path(args.registry_out)
        if not registry_path.is_absolute():
            registry_path = root / registry_path
        island = json.loads(island_path.read_text(encoding='utf-8'))
        registry_path.write_text(
            json.dumps(registry_export(island, report), ensure_ascii=False, indent=2, sort_keys=True) + '\n',
            encoding='utf-8',
        )
    print(format_summary(report))
    if report['status'] != 'PASS':
        for error in report['errors'][:40]:
            print(f'  - {error}', file=sys.stderr)
        if len(report['errors']) > 40:
            print(f'  ... {len(report["errors"]) - 40} more', file=sys.stderr)
        return 1
    for chain in report.get('chain_results', []):
        if chain.get('status') == 'PASS':
            print(f'  chain {chain["id"]}: {chain["from"]} -> {chain["to"]} = {chain.get("computed_factor")}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
