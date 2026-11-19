#!/usr/bin/env python3
"""N10 validator: terminology island, unit-string grammar, stub closure,
authored-data unit/key lint, and full-document rendered term scan.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import COVERAGE_PATH, DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

TERMS_PATH = 'data/terms.json'
CONVENTIONS_PATH = 'data/conventions.json'
GOLDEN_VECTORS_PATH = 'data/golden_vectors.json'
RECALL_LAYERS_PATH = 'data/recall_layers.json'
CONCEPT_SUMMARIES_PATH = 'data/concept_summaries.json'
N06_STUBS_PATH = 'data/n06_term_stubs.json'
N08_STUBS_PATH = 'data/n08_term_stubs.json'
N09_STUBS_PATH = 'data/n09_term_stubs.json'

VALID_CLASSES = ('terms', 'quantities', 'instruments', 'interface', 'iupac')
SUPERSCRIPT_MAP = {
    '¹': 1,
    '²': 2,
    '³': 3,
    '⁻¹': -1,
    '⁻²': -2,
    '⁻³': -3,
}

# Explicit documented exemptions in N03 conventions.json where a descriptive
# label or conversion-factor ratio phrase appears in a field named "unit"
# (prose/ratio descriptions rather than standalone measurement unit strings).
CONVENTIONS_DESCRIPTIVE_UNIT_EXEMPTIONS = {
    'dimensionless (relative atomic mass A_r)',
    '1 (bez dimensijas)',
    'g/L per mg/mL',
    'g/mL per mg/L',
    '% of nominal volume',
}


class UnitGrammarError(ValueError):
    def __init__(self, code: str, message: str, unit_str: str = '') -> None:
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message
        self.unit_str = unit_str


def _build_element_map(grammar: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {el['symbol']: el for el in grammar.get('elements', []) if 'symbol' in el}


def _parse_term_token(token: str, elements: dict[str, dict[str, Any]], raw: str) -> tuple[str, int]:
    if not token:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Tukšs vienības loceklis virknē {raw!r}.', raw)
    if re.search(r'\s', token):
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Atstarpe nav atļauta vienības loceklī {token!r} ({raw!r}).', raw)
    if '*' in token or ',' in token or ';' in token:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nederīgs atdalītājs loceklī {token!r} ({raw!r}).', raw)

    # Exact registered element (covers cm³, dm³, m³ with exponent 1)
    if token in elements:
        return token, 1

    if '^' in token:
        parts = token.split('^')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            raise UnitGrammarError('E_UNIT_BAD_EXPONENT', f'Nederīgs pakāpes pieraksts {token!r} ({raw!r}).', raw)
        base, exp_str = parts
        if not re.match(r'^[-+]?[1-9][0-9]*$', exp_str):
            raise UnitGrammarError('E_UNIT_BAD_EXPONENT', f'Pakāpei jābūt nenulles veselam skaitlim: {token!r} ({raw!r}).', raw)
        if base not in elements:
            raise UnitGrammarError('E_UNIT_UNKNOWN_ELEMENT', f'Nezināms vienības elements {base!r} virknē {raw!r}.', raw)
        return base, int(exp_str)

    # Check Unicode superscript suffix
    for sup, exp_val in sorted(SUPERSCRIPT_MAP.items(), key=lambda kv: -len(kv[0])):
        if token.endswith(sup):
            base = token[:-len(sup)]
            if base in elements:
                return base, exp_val
            raise UnitGrammarError('E_UNIT_UNKNOWN_ELEMENT', f'Nezināms vienības elements {base!r} virknē {raw!r}.', raw)

    raise UnitGrammarError('E_UNIT_UNKNOWN_ELEMENT', f'Nezināms vienības elements {token!r} virknē {raw!r}.', raw)


def _split_product(expr: str, elements: dict[str, dict[str, Any]], raw: str) -> list[dict[str, Any]]:
    if not expr:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Tukšs reizinājums virknē {raw!r}.', raw)
    if '*' in expr or '.' in expr:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Reizināšanai jālieto "·", nevis "*" vai ".": {raw!r}.', raw)
    if expr.startswith('·') or expr.endswith('·') or '··' in expr:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nepareizs reizināšanas atdalītājs "·" virknē {raw!r}.', raw)
    parts = expr.split('·')
    terms: list[dict[str, Any]] = []
    for part in parts:
        sym, exp = _parse_term_token(part, elements, raw)
        terms.append({'element': sym, 'exponent': exp})
    return terms


def _has_balanced_parens(text: str) -> bool:
    depth = 0
    for ch in text:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def parse_unit(unit_str: str, grammar: dict[str, Any]) -> dict[str, Any]:
    """Parse a composed unit string into structured numerator/denominator and dimension vector."""
    if not isinstance(unit_str, str) or unit_str == '' or unit_str.strip() == '':
        raise UnitGrammarError('E_UNIT_EMPTY', 'Vienības virkne ir tukša.', str(unit_str))
    if unit_str != unit_str.strip():
        raise UnitGrammarError('E_UNIT_WHITESPACE', f'Vienības virknē {unit_str!r} nav atļautas sākuma/beigu atstarpes.', unit_str)
    if not _has_balanced_parens(unit_str):
        raise UnitGrammarError('E_UNIT_UNBALANCED_PARENS', f'Nesabalansētas iekavas vienībā {unit_str!r}.', unit_str)

    dimensionless_tokens = set(grammar.get('dimensionless_tokens', []))
    if unit_str in dimensionless_tokens:
        return {
            'raw': unit_str,
            'kind': 'dimensionless',
            'numerator': [],
            'denominator': [],
            'dimension_vector': {},
            'elements': [],
        }

    elements = _build_element_map(grammar)

    # Top-level parenthesized power e.g. (mol/L)^2 or (mol/L)²
    m_pow = re.match(r'^\((.+)\)(\^[-+]?[1-9][0-9]*|[¹²³]|⁻¹|⁻²|⁻³)$', unit_str)
    if m_pow and _has_balanced_parens(m_pow.group(1)):
        inner_str = m_pow.group(1)
        exp_tok = m_pow.group(2)
        outer_exp = int(exp_tok[1:]) if exp_tok.startswith('^') else SUPERSCRIPT_MAP[exp_tok]
        inner = parse_unit(inner_str, grammar)
        scaled_dim = {k: v * outer_exp for k, v in inner['dimension_vector'].items() if v * outer_exp != 0}
        return {
            'raw': unit_str,
            'kind': 'composed',
            'numerator': [{**t, 'exponent': t['exponent'] * outer_exp} for t in inner['numerator']],
            'denominator': [{**t, 'exponent': t['exponent'] * outer_exp} for t in inner['denominator']],
            'dimension_vector': scaled_dim,
            'elements': inner['elements'],
        }

    # Find '/' at paren depth 0
    slash_positions: list[int] = []
    depth = 0
    for idx, ch in enumerate(unit_str):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == '/' and depth == 0:
            slash_positions.append(idx)

    if len(slash_positions) > 1:
        raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Atļauta ne vairāk kā viena dalīšanas zīme "/": {unit_str!r}.', unit_str)

    if len(slash_positions) == 1:
        pos = slash_positions[0]
        num_str = unit_str[:pos]
        den_str = unit_str[pos + 1:]
        if not num_str or not den_str:
            raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nepilna dalīšanas izteiksme: {unit_str!r}.', unit_str)
        if ' ' in num_str or ' ' in den_str:
            raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Atstarpes nav atļautas saliktā vienībā: {unit_str!r}.', unit_str)
        if '(' in num_str or ')' in num_str:
            raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nepareizas iekavas skaitītājā: {unit_str!r}.', unit_str)
        numerator = _split_product(num_str, elements, unit_str)

        if den_str.startswith('(') and den_str.endswith(')') and _has_balanced_parens(den_str[1:-1]):
            inner_den = den_str[1:-1]
            if '/' in inner_den or '(' in inner_den or ')' in inner_den:
                raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Ligzdots dalījums vai iekavas saucējā nav atļautas: {unit_str!r}.', unit_str)
            denominator = _split_product(inner_den, elements, unit_str)
        else:
            if '(' in den_str or ')' in den_str:
                raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nepareizas iekavas saucējā: {unit_str!r}.', unit_str)
            if '·' in den_str or '*' in den_str:
                raise UnitGrammarError(
                    'E_UNIT_AMBIGUOUS_DENOMINATOR',
                    f'Vairāklocekļu saucējs jāliek iekavās, piem., J/(mol·K), saņemts {unit_str!r}.',
                    unit_str,
                )
            denominator = _split_product(den_str, elements, unit_str)
    else:
        if ' ' in unit_str or '(' in unit_str or ')' in unit_str:
            raise UnitGrammarError('E_UNIT_MALFORMED_SEPARATOR', f'Nepareiza sintakse vienībā {unit_str!r}.', unit_str)
        numerator = _split_product(unit_str, elements, unit_str)
        denominator = []

    dim_vec: dict[str, int] = {}
    used_elements: list[str] = []
    for sign, side in ((1, numerator), (-1, denominator)):
        for term in side:
            sym = term['element']
            exp = term['exponent'] * sign
            if sym not in used_elements:
                used_elements.append(sym)
            for dim_axis, dim_pow in elements[sym]['dimension_vector'].items():
                dim_vec[dim_axis] = dim_vec.get(dim_axis, 0) + dim_pow * exp
    dim_vec = {k: v for k, v in dim_vec.items() if v != 0}

    return {
        'raw': unit_str,
        'kind': 'composed',
        'numerator': numerator,
        'denominator': denominator,
        'dimension_vector': dim_vec,
        'elements': used_elements,
    }


def check_dimension_match(unit_str: str, expected_dimension: str, grammar: dict[str, Any]) -> tuple[bool, str | None, dict[str, Any] | None]:
    dimensions = grammar.get('dimensions', {})
    if expected_dimension not in dimensions:
        return False, f'[E_UNIT_UNKNOWN_DIMENSION] Nezināma dimensija {expected_dimension!r}.', None
    try:
        parsed = parse_unit(unit_str, grammar)
    except UnitGrammarError as exc:
        return False, str(exc), None
    expected_vec = {k: v for k, v in dimensions[expected_dimension].items() if v != 0}
    if parsed['dimension_vector'] != expected_vec:
        return (
            False,
            f"[E_UNIT_DIMENSION_MISMATCH] Dimensijai {expected_dimension!r} gaidīts {expected_vec}, "
            f"bet vienībai {unit_str!r} ir {parsed['dimension_vector']}.",
            parsed,
        )
    return True, None, parsed


def _collect_conventions_tokens(conventions: dict[str, Any]) -> set[str]:
    """Collect all unit element symbols attested in data/conventions.json."""
    text = json.dumps(conventions, ensure_ascii=False)
    found: set[str] = set()
    # Scan unit-like tokens across conventions.json (plus 'min' from programme extract)
    for tok in re.findall(r'[A-Za-zµ°][A-Za-z0-9³²¹]*', text):
        found.add(tok)
    return found


def extract_nested_units(text_lv: str, entry: dict[str, Any] | None = None, grammar: dict[str, Any] | None = None) -> list[str]:
    """Extract parenthetical unit strings embedded inside a Latvian term label (C.1.1)."""
    nested: list[str] = []
    if not isinstance(text_lv, str) or '(' not in text_lv:
        return nested
    skip_exact = {
        'm/m', 'm/V', 'V/V', 'pH', 'ε', 'H₃O⁺', 'HCl(aq)', 'NH₃(aq)',
        'N06', 'N07', 'N08', 'N10', 'N25', 'N30', 'N34', 'PROPOSED',
        'kāpnes', 'Erlenmeijera kolba', 'reģistrēts iztrūkums',
        'informatīva atzīme, bez soda punktiem',
        'nav automātiski pārbaudīts',
        'kursa zīmju konvencija',
        'dimērs N₂O₄', 'C/C₀', 'c/c₀', 'C₀/C₀',
    }
    elements = set(_build_element_map(grammar or {}).keys())
    for m in re.finditer(r'\(([^()]+)\)', text_lv):
        inner = m.group(1).strip()
        if not inner or inner in skip_exact:
            continue
        if inner.startswith('IUPAC:') or inner.startswith('N25') or inner.startswith('N34'):
            continue
        # Unit-like inside parens: contains '/' or '·' or '^' (not prose) OR matches element/unit on a quantity
        looks_like_unit = (
            ('/' in inner or '·' in inner or '^' in inner or '*' in inner)
            and ' ' not in inner
        ) or (
            entry is not None
            and entry.get('class') == 'quantities'
            and (inner in elements or re.match(r'^[A-Za-zµ°][A-Za-z0-9³²¹⁻¹⁻²^·/*-]*$', inner) is not None)
        )
        if looks_like_unit:
            nested.append(inner)
    return nested


def check_stub_closure(
    terms_by_key: dict[str, dict[str, Any]],
    repo_root: Path = DEST,
    n06_stubs_path: Path | None = None,
    n08_stubs_path: Path | None = None,
    n09_stubs_path: Path | None = None,
) -> dict[str, Any]:
    """Check prior task stub files (N06, N08, N09) against data/terms.json."""
    specs = [
        ('N06', n06_stubs_path or (repo_root / N06_STUBS_PATH), True),
        ('N08', n08_stubs_path or (repo_root / N08_STUBS_PATH), True),
        ('N09', n09_stubs_path or (repo_root / N09_STUBS_PATH), False),
    ]
    closure_rows: list[dict[str, Any]] = []
    missing_entries: list[dict[str, str]] = []
    text_mismatches: list[dict[str, str]] = []

    for task_id, path, required in specs:
        if not path.exists():
            if required:
                missing_entries.append({'task': task_id, 'key': '<FILE_MISSING>', 'file': str(path)})
                closure_rows.append({
                    'task': task_id,
                    'file': str(path),
                    'status': 'FAIL-MISSING-FILE',
                    'total_keys': 0,
                    'resolved_keys': 0,
                    'missing_keys': ['<FILE_MISSING>'],
                })
            else:
                closure_rows.append({
                    'task': task_id,
                    'file': str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path),
                    'status': 'pending-N09 (N09 not yet executed in workspace; feedback interface keys pre-authored in #sim-terms)',
                    'total_keys': 0,
                    'resolved_keys': 0,
                    'missing_keys': [],
                })
            continue

        stub_data = load_json(path)
        keys = stub_data.get('keys', [])
        missing_for_task: list[str] = []
        resolved_count = 0
        for item in keys:
            k = item.get('key')
            if not k or k not in terms_by_key:
                missing_for_task.append(str(k))
                missing_entries.append({'task': task_id, 'key': str(k)})
            else:
                resolved_count += 1
                expected_lv = item.get('text_lv')
                actual_lv = terms_by_key[k].get('text_lv')
                if expected_lv is not None and expected_lv != actual_lv:
                    text_mismatches.append({
                        'task': task_id,
                        'key': k,
                        'stub_text_lv': expected_lv,
                        'island_text_lv': str(actual_lv),
                    })
        status = 'CLOSED' if not missing_for_task and not any(m['task'] == task_id for m in text_mismatches) else 'FAIL'
        closure_rows.append({
            'task': task_id,
            'file': str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path),
            'status': status,
            'total_keys': len(keys),
            'resolved_keys': resolved_count,
            'missing_keys': missing_for_task,
        })

    ok = len(missing_entries) == 0 and len(text_mismatches) == 0
    return {
        'status': 'PASS' if ok else 'FAIL',
        'rows': closure_rows,
        'missing_entries': missing_entries,
        'text_mismatches': text_mismatches,
    }


def lint_authored_data(
    terms_data: dict[str, Any],
    terms_by_key: dict[str, dict[str, Any]],
    repo_root: Path = DEST,
    conventions_path: Path | None = None,
    golden_vectors_path: Path | None = None,
    extra_data_paths: list[Path] | None = None,
) -> dict[str, Any]:
    """Lint unit-bearing fields and term keys across authored data files.

    Prose fields (feedback sentences, explanations, stems, notes) are exempt by
    design per rules.prose_exemption_scope.
    """
    grammar = terms_data['unit_grammar']
    errors: list[str] = []
    checked_unit_fields = 0
    checked_term_keys = 0
    exempt_prose_fields = 0

    def check_unit_val(val: str, ctx: str, expected_dim: str | None = None, allow_empty: bool = False, allow_conv_exempt: bool = False) -> None:
        nonlocal checked_unit_fields
        if val == '' and allow_empty:
            return
        if allow_conv_exempt and val in CONVENTIONS_DESCRIPTIVE_UNIT_EXEMPTIONS:
            return
        checked_unit_fields += 1
        if expected_dim is not None:
            ok, err, _ = check_dimension_match(val, expected_dim, grammar)
            if not ok:
                errors.append(f'{ctx}: {err}')
        else:
            try:
                parse_unit(val, grammar)
            except UnitGrammarError as exc:
                errors.append(f'{ctx}: {exc}')

    def walk_structured(obj: Any, file_label: str, path: str = '', is_conventions: bool = False, allow_empty_unit: bool = False) -> None:
        nonlocal checked_term_keys, exempt_prose_fields
        if isinstance(obj, dict):
            # If object has both dimension and unit, check dimension coupling!
            if isinstance(obj.get('unit'), str) and isinstance(obj.get('dimension'), str):
                check_unit_val(obj['unit'], f'{file_label}:{path}.unit', expected_dim=obj['dimension'], allow_empty=allow_empty_unit, allow_conv_exempt=is_conventions)

            for k, v in obj.items():
                sub_path = f'{path}.{k}' if path else k
                if k in ('term_key', 'title_key', 'label_key', 'unit_key', 'legend_key', 'annotation_key') and isinstance(v, str):
                    checked_term_keys += 1
                    if v not in terms_by_key:
                        errors.append(f'{file_label}:{sub_path}: [E_TERMS_UNKNOWN_KEY] Nezināma termina atslēga {v!r}.')
                elif k == 'term_keys' and isinstance(v, list):
                    for idx, item_key in enumerate(v):
                        checked_term_keys += 1
                        if not isinstance(item_key, str) or item_key not in terms_by_key:
                            errors.append(f'{file_label}:{sub_path}[{idx}]: [E_TERMS_UNKNOWN_KEY] Nezināma termina atslēga {item_key!r}.')
                elif k == 'unit' and isinstance(v, str):
                    if not isinstance(obj.get('dimension'), str):
                        check_unit_val(v, f'{file_label}:{sub_path}', allow_empty=allow_empty_unit, allow_conv_exempt=is_conventions)
                elif k in ('from', 'to') and isinstance(v, str) and (path.startswith('unit_system.conversions') or path.startswith('unit_system.chains')):
                    check_unit_val(v, f'{file_label}:{sub_path}', allow_conv_exempt=is_conventions)
                elif k in ('expected_unit', 'temperature_unit') and isinstance(v, str):
                    check_unit_val(v, f'{file_label}:{sub_path}', allow_empty=allow_empty_unit, allow_conv_exempt=is_conventions)
                elif k in ('text_lv', 'feedback_lv', 'stem_lv', 'summary_lv', 'note_lv', 'basis_lv', 'when_lv', 'rule_lv', 'gap_reason_lv') and isinstance(v, str):
                    exempt_prose_fields += 1
                else:
                    walk_structured(v, file_label, sub_path, is_conventions=is_conventions, allow_empty_unit=allow_empty_unit)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                walk_structured(item, file_label, f'{path}[{idx}]', is_conventions=is_conventions, allow_empty_unit=allow_empty_unit)

    # 1. Lint terms.json entries themselves
    for entry in terms_data.get('terms', []):
        key = entry.get('key', '?')
        if entry.get('unit') is not None:
            check_unit_val(
                entry['unit'],
                f'data/terms.json:{key}.unit',
                expected_dim=entry.get('dimension'),
            )
        # Nested unit check on text_lv (C.1.1)
        for nested_u in extract_nested_units(entry.get('text_lv', ''), entry, grammar):
            check_unit_val(
                nested_u,
                f'data/terms.json:{key}.text_lv(nested)',
                expected_dim=entry.get('dimension'),
            )

    # 2. Lint conventions.json
    conv_file = conventions_path or (repo_root / CONVENTIONS_PATH)
    conv_data = load_json(conv_file)
    walk_structured(conv_data, 'data/conventions.json', is_conventions=True, allow_empty_unit=False)

    # 3. Lint golden_vectors.json
    gv_file = golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH)
    gv_data = load_json(gv_file)
    walk_structured(gv_data, 'data/golden_vectors.json', is_conventions=False, allow_empty_unit=True)

    # 4. Lint recall_layers.json, concept_summaries.json & figure data (key & prose exemption)
    for rel in (RECALL_LAYERS_PATH, CONCEPT_SUMMARIES_PATH, 'data/figures_t12.json', 'data/figures_t23.json',
                'data/figures_t4.json', 'data/figures_t5.json', 'data/figures_t67.json'):
        p = repo_root / rel
        if p.exists():
            walk_structured(load_json(p), rel, is_conventions=False, allow_empty_unit=True)

    # 5. Lint any extra data files (e.g., planted-failure corpus or bank)
    for ep in extra_data_paths or []:
        walk_structured(load_json(ep), str(ep), is_conventions=False, allow_empty_unit=True)

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'checked_unit_fields': checked_unit_fields,
        'checked_term_keys': checked_term_keys,
        'exempt_prose_fields': exempt_prose_fields,
        'errors': errors,
    }


class _DocumentTermScanner(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.term_key_refs: list[dict[str, str]] = []
        self.scripts: dict[str, str] = {}
        self._cur_script_id: str | None = None
        self._cur_chunks: list[str] = []
        self._active_term_key: str | None = None
        self._active_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v if v is not None else '') for k, v in attrs}
        if 'data-term-key' in attr_map:
            self._active_term_key = attr_map['data-term-key']
            self._active_text = []
            self.term_key_refs.append({
                'tag': tag,
                'id': attr_map.get('id', ''),
                'key': attr_map['data-term-key'],
            })
        if tag == 'script':
            self._cur_script_id = attr_map.get('id', '')
            self._cur_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag == 'script' and self._cur_script_id is not None:
            self.scripts[self._cur_script_id] = ''.join(self._cur_chunks)
            self._cur_script_id = None
        if self._active_term_key is not None:
            # Attach captured inner text to last ref if empty
            if self.term_key_refs and 'text' not in self.term_key_refs[-1]:
                self.term_key_refs[-1]['text'] = ''.join(self._active_text).strip()
            self._active_term_key = None

    def handle_data(self, data: str) -> None:
        if self._cur_script_id is not None:
            self._cur_chunks.append(data)
        elif self._active_term_key is not None:
            self._active_text.append(data)


def scan_rendered_document(html_path: Path, terms_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Scan output/simulator.html for #sim-terms, data-term-key resolution, and nested units."""
    raw = html_path.read_text(encoding='utf-8')
    scanner = _DocumentTermScanner()
    scanner.feed(raw)
    scanner.close()

    errors: list[str] = []
    if 'sim-terms' not in scanner.scripts:
        errors.append('output/simulator.html missing #sim-terms script island')
        return {'status': 'FAIL', 'errors': errors}

    embedded = json.loads(scanner.scripts['sim-terms'])
    grammar = (terms_data or embedded)['unit_grammar']
    by_key = {e['key']: e for e in embedded.get('terms', [])}

    resolved_dom_keys = 0
    for ref in scanner.term_key_refs:
        k = ref['key']
        if k not in by_key:
            errors.append(f"HTML element <{ref['tag']} id={ref['id']!r}> references unknown data-term-key {k!r}")
        else:
            resolved_dom_keys += 1
            if not ref.get('text'):
                errors.append(f"HTML element <{ref['tag']} id={ref['id']!r}> with data-term-key {k!r} has empty static text")

    nested_checked = 0
    unit_strings_checked = 0
    for e in embedded.get('terms', []):
        if e.get('unit') is not None:
            unit_strings_checked += 1
            try:
                parse_unit(e['unit'], grammar)
            except UnitGrammarError as exc:
                errors.append(f"Embedded #sim-terms {e['key']}.unit: {exc}")
        for nu in extract_nested_units(e.get('text_lv', ''), e, grammar):
            nested_checked += 1
            try:
                parse_unit(nu, grammar)
            except UnitGrammarError as exc:
                errors.append(f"Embedded #sim-terms {e['key']}.text_lv nested unit {nu!r}: {exc}")

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'embedded_terms_count': len(by_key),
        'dom_term_key_refs': len(scanner.term_key_refs),
        'resolved_dom_keys': resolved_dom_keys,
        'unit_strings_checked': unit_strings_checked,
        'nested_units_checked': nested_checked,
        'errors': errors,
    }


def validate_all(
    repo_root: Path = DEST,
    terms_path: Path | None = None,
    coverage_path: Path | None = None,
    conventions_path: Path | None = None,
    golden_vectors_path: Path | None = None,
    n06_stubs_path: Path | None = None,
    n08_stubs_path: Path | None = None,
    n09_stubs_path: Path | None = None,
    extra_data_paths: list[Path] | None = None,
) -> dict[str, Any]:
    tp = terms_path or (repo_root / TERMS_PATH)
    cp = coverage_path or (repo_root / COVERAGE_PATH)
    conv_p = conventions_path or (repo_root / CONVENTIONS_PATH)
    gv_p = golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH)

    terms_data = load_json(tp)
    coverage = load_json(cp)
    conventions = load_json(conv_p)

    errors: list[str] = []

    if terms_data.get('schema_version') != 1:
        errors.append(f"terms.schema_version must be 1, got {terms_data.get('schema_version')!r}")
    if terms_data.get('island_id') != 'sim-terms':
        errors.append(f"terms.island_id must be 'sim-terms', got {terms_data.get('island_id')!r}")
    if terms_data.get('language') != 'lv':
        errors.append(f"terms.language must be 'lv', got {terms_data.get('language')!r}")
    if terms_data.get('status') != 'authored':
        errors.append(f"terms.status must be 'authored', got {terms_data.get('status')!r}")

    rules = terms_data.get('rules', {})
    for req_rule in ('masters_usage_rule', 'iupac_pair_rule', 'prose_exemption_scope', 'nested_unit_rule', 'figure_label_contract'):
        if not rules.get(req_rule):
            errors.append(f"Missing rules.{req_rule}")

    grammar = terms_data.get('unit_grammar', {})
    elements = grammar.get('elements', [])
    if not elements:
        errors.append('unit_grammar.elements is empty')

    # Check every unit_grammar element exists in conventions.json (no orphan units)
    conv_tokens = _collect_conventions_tokens(conventions)
    orphan_elements: list[str] = []
    for el in elements:
        sym = el.get('symbol', '')
        if not sym:
            errors.append('Empty symbol in unit_grammar.elements')
            continue
        if sym not in conv_tokens:
            orphan_elements.append(sym)
            errors.append(f'[E_UNIT_ORPHAN_ELEMENT] Vienības elements {sym!r} nav atrodams data/conventions.json.')

    outcome_ids = {o['id'] for o in coverage.get('outcomes', [])}
    conv_cit_ids = {c['id'] for c in conventions.get('citation_index', [])}
    conv_conflict_ids = {c['id'] for c in conventions.get('conflicts', {}).get('entries', [])}
    valid_conv_refs = conv_cit_ids | conv_conflict_ids

    entries = terms_data.get('terms', [])
    by_key: dict[str, dict[str, Any]] = {}
    counts_by_class: dict[str, int] = {c: 0 for c in VALID_CLASSES}
    concept_bindings_count = 0
    unit_slots_count = 0
    nested_unit_slots_count = 0

    for idx, entry in enumerate(entries):
        key = entry.get('key')
        if not key or not isinstance(key, str):
            errors.append(f'Entry at index {idx} missing valid key')
            continue
        if key in by_key:
            errors.append(f'[E_TERMS_DUPLICATE_KEY] Atkārtota termina atslēga {key!r}.')
            continue
        by_key[key] = entry

        cls = entry.get('class')
        if cls not in VALID_CLASSES:
            errors.append(f'{key}: invalid class {cls!r}')
        else:
            counts_by_class[cls] += 1

        txt = entry.get('text_lv')
        if not isinstance(txt, str) or not txt.strip():
            errors.append(f'{key}: empty text_lv')

        if cls == 'quantities':
            if not entry.get('unit'):
                errors.append(f'{key}: quantities entry missing required unit')
            if not entry.get('dimension'):
                errors.append(f'{key}: quantities entry missing required dimension')

        if cls == 'iupac':
            if not entry.get('primary_lv') or not entry.get('iupac_name'):
                errors.append(f'{key}: iupac entry must define primary_lv and iupac_name')

        cid = entry.get('concept_id')
        if cid is not None:
            concept_bindings_count += 1
            if cid not in outcome_ids:
                errors.append(f'{key}: [E_TERMS_BAD_CONCEPT] concept_id {cid!r} not in coverage.json')

        cref = entry.get('conventions_ref')
        if cref is not None and cref not in valid_conv_refs:
            errors.append(f'{key}: [E_TERMS_BAD_CONV_REF] conventions_ref {cref!r} not in conventions.json')

        if not entry.get('master_citation'):
            errors.append(f'{key}: missing master_citation')

        if entry.get('unit') is not None:
            unit_slots_count += 1
        nested = extract_nested_units(txt or '', entry, grammar)
        nested_unit_slots_count += len(nested)

    closure = check_stub_closure(
        by_key,
        repo_root=repo_root,
        n06_stubs_path=n06_stubs_path,
        n08_stubs_path=n08_stubs_path,
        n09_stubs_path=n09_stubs_path,
    )
    if closure['status'] != 'PASS':
        for m in closure['missing_entries']:
            errors.append(f"[E_STUB_UNRESOLVED] Uzdevums {m['task']} atsaucas uz trūkstošu atslēgu {m['key']!r}.")
        for tm in closure['text_mismatches']:
            errors.append(
                f"[E_STUB_TEXT_MISMATCH] {tm['task']} {tm['key']}: stub={tm['stub_text_lv']!r} != island={tm['island_text_lv']!r}"
            )

    lint_report = lint_authored_data(
        terms_data,
        by_key,
        repo_root=repo_root,
        conventions_path=conv_p,
        golden_vectors_path=gv_p,
        extra_data_paths=extra_data_paths,
    )
    if lint_report['status'] != 'PASS':
        errors.extend(lint_report['errors'])

    canonical_bytes = canonical_json_bytes(terms_data)
    return {
        'schema_version': 1,
        'task': 'N10',
        'status': 'PASS' if not errors else 'FAIL',
        'canonical_sha256': sha256_bytes(canonical_bytes),
        'canonical_bytes': len(canonical_bytes),
        'counts_by_class': counts_by_class,
        'total_entries': len(by_key),
        'concept_bindings_count': concept_bindings_count,
        'unit_slots_count': unit_slots_count,
        'nested_unit_slots_count': nested_unit_slots_count,
        'grammar_elements_count': len(elements),
        'orphan_elements': orphan_elements,
        'stub_closure': closure,
        'lint': lint_report,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    c = report['counts_by_class']
    lint = report['lint']
    lines = [
        f"terminology: {report['status']} | entries={report['total_entries']} "
        f"(terms={c['terms']}, quantities={c['quantities']}, instruments={c['instruments']}, "
        f"interface={c['interface']}, iupac={c['iupac']}) | "
        f"units={lint['checked_unit_fields']} keys={lint['checked_term_keys']} "
        f"exempt_prose={lint['exempt_prose_fields']}",
    ]
    for err in report['errors'][:10]:
        lines.append(f'  ERROR: {err}')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--terms', type=Path, default=None)
    parser.add_argument('--extra-data', type=Path, action='append', default=[])
    parser.add_argument('--n09-stubs', type=Path, default=None)
    parser.add_argument('--html', type=Path, default=None)
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--report', type=Path, default=None)
    args = parser.parse_args(argv)

    report = validate_all(
        terms_path=args.terms,
        n09_stubs_path=args.n09_stubs,
        extra_data_paths=args.extra_data,
    )
    if args.html:
        report['html_scan'] = scan_rendered_document(args.html, load_json(args.terms or (DEST / TERMS_PATH)))
        if report['html_scan']['status'] != 'PASS':
            report['status'] = 'FAIL'
            report['errors'].extend(report['html_scan']['errors'])

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_summary(report))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
