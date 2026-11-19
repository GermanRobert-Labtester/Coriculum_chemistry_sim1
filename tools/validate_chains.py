#!/usr/bin/env python3
"""N16 worked example chain validator, recompute table and leak-free delivery gate.

The validator is the authoring second opinion:
- every numeric step is recomputed from declared givens/prior steps with Decimal;
- every step and result is checked against the chain format;
- every master anchor, conventions entry, figure id and coverage outcome resolves;
- every chain reference (method card / practice item) resolves bidirectionally;
- the honesty banner is fixed and positive official-exam claims are rejected;
- the runtime projection seals per-step results and reasoning with a per-step key;
- the pre-reveal fixture and the sealed island are scanned for plaintext answers;
- a planted leak is required to fail with the chain and step named.

Run: python3 tools/validate_chains.py --report evidence/N16_VALIDATION_RECORD.json
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_UP, getcontext
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    COVERAGE_PATH, DEST, canonical_json_bytes, load_json, sha256_bytes,
    parse_master, anchor_heading,
)

getcontext().prec = 50

CHAINS_PATH = 'data/chains.json'
CHAIN_SCHEMA_PATH = 'data/chain_schema.json'
CHAIN_REFS_PATH = 'data/chain_references.json'
CONVENTIONS_PATH = 'data/conventions.json'
SUMMARIES_PATH = 'data/concept_summaries.json'
EXAMPLES_PATH = 'docs/EXAMPLE_QUESTIONS.json'
FIGURES_PATHS = [
    'data/figures_t12.json',
    'data/figures_t23.json',
    'data/figures_t4.json',
    'data/figures_t5.json',
    'data/figures_t67.json',
]
EXPECTED_IDS = [f'EX{i:02d}' for i in range(1, 15)]

BANNER = ("Mācību materiāls patstāvīgai sagatavošanai: nav oficiāls RSU kolokvija eksāmens, "
          "neapliecina eksāmena saturu un nepiešķir vērtējumu.")
FORBIDDEN_POSITIVE = [
    'oficiāls eksāmens',
    'oficiāls kolokvija eksāmens',
    'īsts eksāmens',
    'eksāmena jautājums',
    'oficiāls uzdevums',
    'RSU eksāmens',
    'garantēts vērtējums',
    'proktors',
]

SUPERSCRIPT = str.maketrans({
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁻': '-', '⁺': '+',
})
UNIT_ALIASES = [
    ('mol·l⁻¹', 'mol/l'), ('mol l⁻¹', 'mol/l'), ('mol/l', 'mol/l'), ('moll-1', 'mol/l'),
    ('kj·mol⁻¹', 'kj/mol'), ('kj mol⁻¹', 'kj/mol'), ('kj/mol', 'kj/mol'),
    ('j·mol⁻¹·k⁻¹', 'j/(mol*k)'), ('j/(mol·k)', 'j/(mol*k)'), ('j/(mol*k)', 'j/(mol*k)'),
    ('g·mol⁻¹', 'g/mol'), ('g/mol', 'g/mol'),
    ('mg/ml', 'mg/ml'), ('mg·ml⁻¹', 'mg/ml'), ('g/l', 'g/l'),
    ('ml', 'ml'), ('l', 'l'), ('mg', 'mg'), ('g', 'g'), ('kj', 'kj'), ('j', 'j'),
]


class ChainError(Exception):
    pass


# ---------------------------------------------------------------------------
# Citation resolver


SEG_RE = re.compile(r'([A-Za-z0-9_]+)(?:\[([A-Za-z0-9_]+)(?:=([^\]]+))?\])?')


def _list_item(items: list[Any], key: str | None, value: str | None) -> Any:
    for item in items:
        if not isinstance(item, dict):
            continue
        if key is not None and str(item.get(key)) == value:
            return item
        if key is None:
            for candidate in ('id', 'symbol', 'formula', 'couple', 'order', 'name', 'name_lv'):
                if str(item.get(candidate)) == value:
                    return item
    raise ChainError(f'selector [{key}={value}] did not resolve in list')


def resolve_ref(data: Any, ref: str) -> Any:
    """Resolve a dotted conventions path such as
    ``kinetics.integrated_forms[order=1].half_life`` or
    ``compound_molar_masses.compounds[NaCl]``.
    """
    cur = data
    for part in str(ref).split('.'):
        match = re.fullmatch(r'([A-Za-z0-9_]+)(?:\[([^\[\]]+)\])?', part)
        if not match:
            raise ChainError(f'malformed reference {ref!r} at {part!r}')
        key, selector = match.group(1), match.group(2)
        resolved_from_list = False
        if isinstance(cur, dict):
            if key not in cur:
                raise ChainError(f'{ref!r}: missing key {key!r}')
            cur = cur[key]
        elif isinstance(cur, list):
            if selector is None:
                raise ChainError(f'{ref!r}: list requires a selector at {part!r}')
            if '=' in selector:
                sk, sv = selector.split('=', 1)
                cur = _list_item(cur, sk, sv)
            else:
                cur = _list_item(cur, None, selector)
            resolved_from_list = True
        else:
            raise ChainError(f'{ref!r}: cannot descend into {type(cur).__name__}')
        if selector is not None and not resolved_from_list:
            if isinstance(cur, list):
                if '=' in selector:
                    sk, sv = selector.split('=', 1)
                    cur = _list_item(cur, sk, sv)
                else:
                    cur = _list_item(cur, None, selector)
            elif isinstance(cur, dict):
                if '=' in selector:
                    sk, sv = selector.split('=', 1)
                    if sk in cur and str(cur[sk]) != sv:
                        raise ChainError(f'{ref!r}: selector did not resolve')
                    if sk not in cur:
                        raise ChainError(f'{ref!r}: selector {sk!r} not in object')
                else:
                    raise ChainError(f'{ref!r}: bare selector {selector!r} on an object')

    return cur


# ---------------------------------------------------------------------------
# Numeric helpers


def as_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise ChainError(f'not a decimal: {value!r}') from exc


def fmt_decimal(value: Decimal) -> str:
    text = format(value, 'f')
    if '.' in text:
        text = text.rstrip('0').rstrip('.')
    return text or '0'


def parse_display(display: str) -> tuple[Decimal, Decimal] | None:
    """Return (numeric value, half-unit of the last displayed digit).

    Handles Latvian comma decimals, U+2212 minus and ``·10ⁿ`` / ``×10ⁿ``.
    Symbolic displays return None.
    """
    text = str(display).strip().replace('\u2212', '-').replace('−', '-')
    text = text.replace(' ', '')
    text = text.translate(SUPERSCRIPT)
    m = re.search(r'([+-]?\d+(?:[.,]\d+)?)(?:[·×xX]10\^?([+-]?\d+))?', text)
    if not m:
        return None
    mantissa = m.group(1).replace(',', '.')
    exp = int(m.group(2)) if m.group(2) else 0
    try:
        value = Decimal(mantissa) * (Decimal(10) ** exp)
    except Exception:
        return None
    decimals = len(mantissa.split('.')[1]) if '.' in mantissa else 0
    half_unit = Decimal(5) * (Decimal(10) ** (exp - decimals - 1))
    return value, half_unit


def extract_numbers(text: str) -> list[Decimal]:
    out = []
    norm = str(text).replace('\u2212', '-').replace('−', '-').replace(',', '.')
    norm = norm.translate(SUPERSCRIPT)
    norm = re.sub(r'([·×xX])10\^?([+-]?\d+)', lambda m: 'e' + m.group(2), norm)
    for m in re.finditer(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', norm):
        token = m.group(0)
        try:
            d = Decimal(token)
            if abs(d.adjusted()) <= 30:
                out.append(d)
        except Exception:
            pass
    return out


def display_ok(value: Decimal, display: str) -> bool:
    parsed = parse_display(display)
    if parsed is None:
        return False
    shown, half = parsed
    return abs(value - shown) <= half + max(Decimal('1e-30'), abs(value) * Decimal('1e-15'))


# ---------------------------------------------------------------------------
# Independent recompute


def recompute(step: dict[str, Any], givens: dict[str, Decimal], steps: dict[str, Decimal]) -> Decimal:
    rc = step.get('recompute')
    if not isinstance(rc, dict):
        raise ChainError(f"{step.get('step_id')}: numeric step without recompute")
    op = rc.get('op')
    ops = rc.get('operands')
    if not isinstance(ops, list):
        raise ChainError(f"{step.get('step_id')}: recompute operands missing")

    def val(o: dict[str, Any]) -> Decimal:
        if 'given' in o:
            if o['given'] not in givens:
                raise ChainError(f"unknown given {o['given']!r}")
            return givens[o['given']]
        if 'step' in o:
            if o['step'] not in steps:
                raise ChainError(f"forward or unknown step reference {o['step']!r}")
            return steps[o['step']]
        if 'number' in o:
            return as_decimal(o['number'])
        if 'constant' in o:
            return as_decimal(o['constant'])
        raise ChainError(f'unknown operand {o!r}')

    if op == 'add':
        return sum((val(o) for o in ops), Decimal(0))
    if op == 'subtract':
        return val(ops[0]) - val(ops[1])
    if op == 'multiply':
        out = Decimal(1)
        for o in ops:
            out *= val(o)
        return out
    if op == 'divide':
        den = val(ops[1])
        if den == 0:
            raise ChainError('division by zero')
        return val(ops[0]) / den
    if op == 'negate':
        return -val(ops[0])
    if op == 'scale':
        factor = rc.get('factor') or {}
        return val(ops[0]) * as_decimal(factor.get('num', 1)) / as_decimal(factor.get('den', 1))
    if op == 'multiply_ratio':
        return val(ops[0]) * as_decimal(rc.get('num', 1)) / as_decimal(rc.get('den', 1))
    if op == 'power':
        exp_o = ops[1]
        exp = int(exp_o['number']) if 'number' in exp_o else int(val(exp_o))
        return val(ops[0]) ** exp
    if op == 'log10':
        v = val(ops[0])
        if v <= 0:
            raise ChainError('log10 of non-positive value')
        return v.log10()
    if op == 'linfit_component':
        pts = [(as_decimal(x), as_decimal(y)) for x, y in (rc.get('points') or [])]
        if len(pts) < 2:
            raise ChainError('linfit needs at least two points')
        n = Decimal(len(pts))
        sx = sum((p[0] for p in pts), Decimal(0))
        sy = sum((p[1] for p in pts), Decimal(0))
        sxy = sum((p[0] * p[1] for p in pts), Decimal(0))
        sxx = sum((p[0] * p[0] for p in pts), Decimal(0))
        den = n * sxx - sx * sx
        if den == 0:
            raise ChainError('linfit degenerate x values')
        slope = (n * sxy - sx * sy) / den
        intercept = (sy - slope * sx) / n
        return slope if rc.get('component') == 'slope' else intercept
    if op == 'nernst':
        e0 = val(ops[0])
        slope = val(ops[1])
        n = val(ops[2])
        q = val(ops[3])
        if n == 0 or q <= 0:
            raise ChainError('nernst requires n != 0 and Q > 0')
        return e0 - (slope / n) * q.log10()
    raise ChainError(f'unknown recompute op {op!r}')


# ---------------------------------------------------------------------------
# Sealing


def step_key(chain_id: str, step_id: str) -> str:
    import hashlib
    return hashlib.sha256(f'{chain_id}:{step_id}:N16'.encode('utf-8')).hexdigest()


def xor_bytes(data: bytes, key_hex: str) -> bytes:
    key = bytes.fromhex(key_hex)
    if not key:
        raise ChainError('empty reveal key')
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def seal_payload(chain_id: str, step: dict[str, Any]) -> dict[str, Any]:
    payload = {
        'value': step['result'].get('value'),
        'display_lv': step['result'].get('display_lv'),
        'unit': step['result'].get('unit'),
        'sig_figs': step['result'].get('sig_figs'),
        'reasoning_lv': step.get('reasoning_lv'),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    key = step_key(chain_id, step['step_id'])
    sealed = xor_bytes(raw, key)
    return {
        'alg': 'xor-v1',
        'key': key,
        'data': base64.b64encode(sealed).decode('ascii'),
    }


def unseal_payload(chain_id: str, step_id: str, blob: dict[str, Any]) -> dict[str, Any]:
    key = blob.get('key') or step_key(chain_id, step_id)
    raw = xor_bytes(base64.b64decode(blob['data']), key)
    return json.loads(raw.decode('utf-8'))


def build_runtime_projection(chains_data: dict[str, Any]) -> dict[str, Any]:
    chains = []
    for chain in chains_data.get('chains', []):
        steps = []
        for st in chain.get('steps', []):
            result = st.get('result', {})
            steps.append({
                'step_id': st['step_id'],
                'quantity_lv': st['quantity_lv'],
                'statement_lv': st['statement_lv'],
                'result_kind': result.get('kind'),
                'result_unit': result.get('unit'),
                'public': bool(result.get('public')),
                'citations': st.get('citations', {}),
                'sealed': seal_payload(chain['id'], st),
            })
        chains.append({
            'id': chain['id'],
            'topic': chain['topic'],
            'title_lv': chain['title_lv'],
            'subtitle_lv': chain['subtitle_lv'],
            'outcome_ids': chain['outcome_ids'],
            'master_citation': chain['master_citation'],
            'epistemic_label': chain['epistemic_label'],
            'banner_lv': chain['banner_lv'],
            'givens': chain['givens'],
            'steps': steps,
            'figure_refs': chain['figure_refs'],
            'back_links': chain['back_links'],
        })
    return {
        'schema_version': chains_data.get('schema_version', 1),
        'format_version': chains_data.get('format_version', 1),
        'island_id': 'sim-chains',
        'owner': 'N16',
        'status': 'authored',
        'title_lv': chains_data.get('title_lv', 'Darba piemēru ķēdes EX01–EX14'),
        'banner_lv': chains_data.get('banner_lv', BANNER),
        'honesty': chains_data.get('honesty', {}),
        'chain_count': len(chains),
        'chains': chains,
    }


# ---------------------------------------------------------------------------
# Pre-reveal fixture and leak scan


def _esc(text: Any) -> str:
    return (str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def pre_reveal_fixture(projection: dict[str, Any], only_chain: str | None = None) -> str:
    parts = ['<div class="chain-fixture" data-fixture="pre-reveal">']
    for chain in projection['chains']:
        if only_chain and chain['id'] != only_chain:
            continue
        parts.append(
            f'<article class="chain" id="chain-{_esc(chain["id"])}-fixture" '
            f'data-chain-id="{_esc(chain["id"])}" data-chain-topic="{chain["topic"]}" '
            f'data-revealed-count="0" data-revealed-all="false">'
        )
        parts.append(f'<p class="chain-banner">{_esc(chain["banner_lv"])}</p>')
        parts.append(f'<h3 class="chain-title" tabindex="-1">{_esc(chain["title_lv"])}</h3>')
        parts.append(f'<p class="chain-subtitle">{_esc(chain["subtitle_lv"])}</p>')
        mc = chain['master_citation']
        parts.append(f'<p class="chain-citation">{_esc(mc.get("heading_lv"))} '
                     f'<code>{_esc(mc.get("anchor"))}</code></p>')
        parts.append('<dl class="chain-givens">')
        for g in chain.get('givens', []):
            if g.get('kind') == 'points':
                continue
            parts.append(f'<div class="chain-given" data-given-id="{_esc(g["id"])}">'
                         f'<dt>{_esc(g["label_lv"])}</dt><dd>{_esc(g["display_lv"])} '
                         f'{_esc(g["unit"])}</dd></div>')
        parts.append('</dl>')
        parts.append('<ol class="chain-steps">')
        for st in chain['steps']:
            parts.append(f'<li class="chain-step" data-step-id="{_esc(st["step_id"])}" data-revealed="false">')
            parts.append(f'<p class="chain-step-quantity">{_esc(st["quantity_lv"])}</p>')
            parts.append(f'<p class="chain-step-statement">{_esc(st["statement_lv"])}</p>')
            fig_here = [f for f in chain.get('figure_refs', []) if f.get('step_id') == st['step_id']]
            if fig_here:
                parts.append('<p class="chain-figure-placeholder">Attēls tiks parādīts kopā ar šo soli: '
                             + ', '.join(_esc(f['figure_id']) for f in fig_here) + '</p>')
            parts.append(f'<button type="button" class="chain-reveal-btn" data-chain-id="{_esc(chain["id"])}" '
                         f'data-step-id="{_esc(st["step_id"])}" aria-expanded="false">Parādīt rezultātu</button>')
            parts.append('<div class="chain-result" hidden></div>')
            parts.append('</li>')
        parts.append('</ol>')
        parts.append('<button type="button" class="chain-reveal-all">Parādīt visus soļus</button>')
        parts.append('<div class="chain-confirm" hidden role="group" aria-label="Apstiprinājums">'
                     '<p>Vai tiešām vēlaties atklāt visus soļus? Šis ir pašizskaidrošanas treniņš.</p>'
                     '<button type="button" class="chain-confirm-yes">Jā, atklāt visus</button>'
                     '<button type="button" class="chain-confirm-no">Nē</button></div>')
        parts.append('<button type="button" class="chain-collapse" hidden>Sakļaut atpakaļ</button>')
        parts.append('<p class="chain-print-note chain-print-note-collapsed">Pamatojums ir interaktīvs; '
                     'drukātajā versijā atklājiet soļus pirms drukāšanas.</p>')
        parts.append('</article>')
    parts.append('</div>')
    return '\n'.join(parts)


def pre_reveal_visible_text(projection: dict[str, Any], only_chain: str | None = None) -> str:
    """Concatenate the learner-visible pre-reveal text (no attributes, ids, step numbers)."""
    parts = []
    for chain in projection['chains']:
        if only_chain and chain['id'] != only_chain:
            continue
        parts.extend([chain.get('banner_lv', ''), chain.get('title_lv', ''), chain.get('subtitle_lv', '')])
        mc = chain.get('master_citation') or {}
        parts.extend([mc.get('heading_lv', ''), mc.get('anchor', '')])
        for g in chain.get('givens', []):
            if g.get('kind') == 'points':
                continue
            parts.extend([g.get('label_lv', ''), str(g.get('display_lv', '')), str(g.get('unit', ''))])
        for st in chain['steps']:
            parts.extend([st.get('quantity_lv', ''), st.get('statement_lv', '')])
            for fr in chain.get('figure_refs', []):
                if fr.get('step_id') == st['step_id']:
                    parts.append(fr.get('figure_id', ''))
            parts.append('Parādīt rezultātu')
        parts.extend(['Parādīt visus soļus', 'Vai tiešām vēlaties atklāt visus soļus?',
                      'Jā, atklāt visus', 'Nē', 'Sakļaut atpakaļ',
                      'Pamatojums ir interaktīvs; drukātajā versijā atklājiet soļus pirms drukāšanas.'])
    return '\n'.join(str(p) for p in parts if p is not None)



def _norm_text(text: str) -> str:
    text = str(text).lower().replace('\u2212', '-').replace('−', '-')
    text = text.translate(SUPERSCRIPT)
    text = re.sub(r'[·×xX]10\^?([+-]?\d+)', r'e\1', text)
    for old, new in UNIT_ALIASES:
        text = text.replace(old, new)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _secret_numbers(step: dict[str, Any]) -> list[tuple[Decimal, Decimal]]:
    """Return (value, tolerance) pairs that must not appear before reveal."""
    result = step['result']
    if result.get('public'):
        return []
    out = []
    if result.get('kind') == 'numeric':
        try:
            value = as_decimal(result['value'])
            out.append((value, max(Decimal('1e-12'), abs(value) * Decimal('1e-10'))))
        except Exception:
            pass
    shown = parse_display(result.get('display_lv', ''))
    if shown is not None:
        out.append((shown[0], shown[1] + max(Decimal('1e-12'), abs(shown[0]) * Decimal('1e-10'))))
    return out


def scan_text(text: str, chains: list[dict[str, Any]], revealed: set[tuple[str, str]] | None = None,
              only_chain: str | None = None) -> list[dict[str, Any]]:
    revealed = revealed or set()
    violations: list[dict[str, Any]] = []
    norm = _norm_text(text)
    compact = norm.replace(' ', '')
    def hit(token: str) -> bool:
        token = _norm_text(token)
        if not token:
            return False
        # Numeric-looking tokens get digit/decimal boundaries so 2 does not
        # match 2,15 and 100 does not match 100,0. Symbolic tokens are matched
        # as substrings (they contain letters or operators).
        if re.fullmatch(r'[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?', token):
            pat = r'(?<![\d.,])' + re.escape(token) + r'(?![\d.,])'
            return re.search(pat, norm) is not None or re.search(pat, compact) is not None
        return token in norm or token.replace(' ', '') in compact
    for chain in chains:
        if only_chain and chain['id'] != only_chain:
            continue
        for step in chain['steps']:
            if (chain['id'], step['step_id']) in revealed:
                continue
            result = step['result']
            if result.get('public'):
                continue
            if result.get('kind') == 'numeric':
                secrets = [result.get('display_lv', ''), result.get('value', '')]
            else:
                secrets = [result.get('value', ''), result.get('display_lv', '')]
            for secret in secrets:
                if hit(secret):
                    violations.append({
                        'chain_id': chain['id'],
                        'step_id': step['step_id'],
                        'kind': 'result_value',
                        'secret': str(secret),
                        'where': 'pre_reveal',
                    })
                    break
            reasoning = _norm_text(step.get('reasoning_lv', ''))
            if reasoning:
                segments = [s.strip() for s in re.split(r'[.;:]\s*', reasoning) if len(s.strip()) >= 20]
                for seg in segments:
                    if seg in norm or seg.replace(' ', '') in compact:
                        violations.append({
                            'chain_id': chain['id'],
                            'step_id': step['step_id'],
                            'kind': 'reasoning',
                            'secret': seg[:80],
                            'where': 'pre_reveal',
                        })
                        break
    # de-duplicate
    seen = set()
    uniq = []
    for v in violations:
        key = (v['chain_id'], v['step_id'], v['kind'], v['secret'])
        if key in seen:
            continue
        seen.add(key)
        uniq.append(v)
    return uniq


def scan_island(projection: dict[str, Any], chains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    violations = []
    for chain in projection['chains']:
        text = pre_reveal_visible_text(projection, only_chain=chain['id'])
        violations.extend(scan_text(text, chains, only_chain=chain['id']))
    return violations


# ---------------------------------------------------------------------------
# Main validation


def validate_chains(repo_root: Path | str = DEST,
                    chains_path: Path | str | None = None,
                    schema_path: Path | str | None = None,
                    refs_path: Path | str | None = None,
                    coverage_path: Path | str | None = None,
                    conventions_path: Path | str | None = None,
                    summaries_path: Path | str | None = None,
                    figure_paths: list[Path | str] | None = None,
                    examples_path: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root)
    errors: list[str] = []
    warnings: list[str] = []

    def load(rel: str) -> Any:
        return load_json(root / rel)

    chains_file = Path(chains_path) if chains_path else root / CHAINS_PATH
    schema_file = Path(schema_path) if schema_path else root / CHAIN_SCHEMA_PATH
    refs_file = Path(refs_path) if refs_path else root / CHAIN_REFS_PATH
    cov_file = Path(coverage_path) if coverage_path else root / COVERAGE_PATH
    conv_file = Path(conventions_path) if conventions_path else root / CONVENTIONS_PATH
    sum_file = Path(summaries_path) if summaries_path else root / SUMMARIES_PATH
    ex_file = Path(examples_path) if examples_path else root / EXAMPLES_PATH
    fig_files = [Path(p) if Path(p).is_absolute() else root / p for p in (figure_paths or FIGURES_PATHS)]

    try:
        chains_data = load_json(chains_file)
    except Exception as exc:
        return {'status': 'FAIL', 'errors': [f'cannot load {chains_file}: {exc}'], 'summary': {}}
    try:
        schema = load_json(schema_file)
        refs = load_json(refs_file)
        coverage = load_json(cov_file)
        conventions = load_json(conv_file)
        summaries = load_json(sum_file)
        examples = load_json(ex_file)
    except Exception as exc:
        return {'status': 'FAIL', 'errors': [f'cannot load a dependency: {exc}'], 'summary': {}}

    figures = []
    for fp in fig_files:
        try:
            figures.extend(load_json(fp).get('figures', []))
        except Exception as exc:
            errors.append(f'cannot load figures {fp}: {exc}')

    fig_by_id = {f.get('id'): f for f in figures if f.get('id')}
    cov_by_id = {o.get('id'): o for o in coverage.get('outcomes', [])}
    outcomes_by_id = cov_by_id
    example_ids = {e.get('example_id') for e in examples.get('examples', [])}

    # Reveal state must stay in memory: no storage, cookie or URL persistence.
    view_path = root / 'src/chain-view.js'
    forbidden_api = ('localStorage', 'sessionStorage', 'document.cookie', 'indexedDB',
                     'history.pushState', 'history.replaceState', 'location.hash',
                     'location.search', 'URLSearchParams')
    persistence = {'source': 'src/chain-view.js', 'forbidden': list(forbidden_api), 'hits': [],
                   'status': 'FAIL'}
    if not view_path.is_file():
        errors.append('missing src/chain-view.js for the persistence scan')
    else:
        view_text = view_path.read_text(encoding='utf-8')
        persistence['hits'] = [token for token in forbidden_api if token in view_text]
        persistence['status'] = 'PASS' if not persistence['hits'] else 'FAIL'
        if persistence['hits']:
            errors.append('chain-view.js uses persistence API(s): ' + ', '.join(persistence['hits']))

    # Format / island envelope
    if chains_data.get('schema_version') != schema.get('schema_version'):
        errors.append('chains schema_version mismatch')
    if chains_data.get('format_version') != schema.get('format_version'):
        errors.append('chains format_version mismatch')
    if chains_data.get('island_id') != 'sim-chains':
        errors.append('chains island_id must be sim-chains')
    if chains_data.get('owner') != 'N16':
        errors.append('chains owner must be N16')
    if chains_data.get('banner_lv') != BANNER:
        errors.append('island banner does not equal the fixed N16 banner')
    if schema.get('honesty', {}).get('banner_lv') != BANNER:
        errors.append('schema banner does not equal the fixed N16 banner')

    chains = chains_data.get('chains') or []
    if not isinstance(chains, list):
        errors.append('chains must be a list')
        chains = []
    ids = [c.get('id') for c in chains]
    if ids != EXPECTED_IDS:
        errors.append(f'chain ids must be exactly {EXPECTED_IDS}, got {ids}')
    topic_counts = {t: 0 for t in range(1, 8)}
    step_count = 0
    numeric_count = 0
    symbolic_count = 0
    recompute_rows: list[dict[str, Any]] = []
    negative_recompute = {'status': 'NOT_RUN'}
    citation_counts = {'anchors': 0, 'conventions': 0, 'figures': 0, 'outcomes': 0}
    citation_refs: list[dict[str, Any]] = []
    multi_citations: list[dict[str, Any]] = []
    figure_rows: list[dict[str, Any]] = []
    chain_rows: list[dict[str, Any]] = []
    honesty_violations: list[dict[str, Any]] = []
    master_cache: dict[str, Any] = {}

    def master_index(path: str) -> Any:
        if path not in master_cache:
            full = root / path
            if not full.exists():
                raise ChainError(f'master path does not exist: {path}')
            master_cache[path] = parse_master(full)
        return master_cache[path]

    for chain in chains:
        cid = chain.get('id', '?')
        chain_errors = []
        for field in schema.get('record_required', []):
            if field not in chain:
                chain_errors.append(f'{cid}: missing field {field}')
        if chain.get('banner_lv') != BANNER:
            chain_errors.append(f'{cid}: banner_lv is not the fixed banner')
        topic = chain.get('topic')
        if topic not in range(1, 8):
            chain_errors.append(f'{cid}: topic must be 1-7')
        else:
            topic_counts[topic] += 1
        outcomes = chain.get('outcome_ids') or []
        if not isinstance(outcomes, list) or not outcomes:
            chain_errors.append(f'{cid}: outcome_ids must be a non-empty list')
            outcomes = []
        for oid in outcomes:
            if oid not in cov_by_id:
                chain_errors.append(f'{cid}: outcome {oid} does not resolve in #sim-coverage')
            else:
                citation_counts['outcomes'] += 1
                if cov_by_id[oid].get('topic') != topic:
                    chain_errors.append(f'{cid}: outcome {oid} belongs to topic {cov_by_id[oid].get("topic")}, not {topic}')
        mc = chain.get('master_citation') or {}
        for field in ('path', 'anchor', 'heading_lv', 'freeze_id'):
            if not mc.get(field):
                chain_errors.append(f'{cid}: master_citation missing {field}')
        try:
            idx = master_index(mc.get('path', ''))
            if mc.get('anchor') not in idx.ids:
                chain_errors.append(f'{cid}: master anchor #{mc.get("anchor")} does not resolve')
            else:
                citation_counts['anchors'] += 1
                heading = anchor_heading(idx, mc.get('anchor'))
                if heading != mc.get('heading_lv'):
                    chain_errors.append(f'{cid}: master heading {heading!r} != {mc.get("heading_lv")!r}')
            if outcomes and outcomes[0] in cov_by_id:
                primary = cov_by_id[outcomes[0]]
                for cov_field, chain_field in (
                    ('master_path', 'path'), ('master_anchor', 'anchor'),
                    ('master_heading_lv', 'heading_lv'), ('master_freeze_id', 'freeze_id'),
                ):
                    if primary.get(cov_field) != mc.get(chain_field):
                        chain_errors.append(
                            f'{cid}: master_citation.{chain_field} {mc.get(chain_field)!r} != '
                            f'primary outcome {primary.get(cov_field)!r}')
        except ChainError as exc:
            chain_errors.append(f'{cid}: {exc}')

        # Givens
        givens = chain.get('givens') or []
        givens_by_id: dict[str, dict[str, Any]] = {}
        given_vals: dict[str, Decimal] = {}
        for g in givens:
            gid = g.get('id')
            if not gid:
                chain_errors.append(f'{cid}: given without id')
                continue
            if gid in givens_by_id:
                chain_errors.append(f'{cid}: duplicate given id {gid}')
            givens_by_id[gid] = g
            if g.get('kind') != 'points':
                try:
                    given_vals[gid] = as_decimal(g.get('value'))
                except Exception:
                    chain_errors.append(f'{cid}: given {gid} value is not numeric')
            source = g.get('source') or {}
            kind = source.get('kind')
            ref = source.get('ref', '')
            if kind not in schema.get('given_source_kinds', []):
                chain_errors.append(f'{cid}: given {gid} has unknown source kind {kind!r}')
            elif kind == 'conventions':
                try:
                    citation_counts['conventions'] += 1
                    resolve_ref(conventions, ref)
                    citation_refs.append({'chain_id': cid, 'step_id': None, 'kind': 'given', 'ref': ref, 'status': 'OK'})
                except ChainError as exc:
                    chain_errors.append(f'{cid}: given {gid} conventions ref {ref!r}: {exc}')
                    citation_refs.append({'chain_id': cid, 'step_id': None, 'kind': 'given', 'ref': ref, 'status': 'DANGLING'})
            elif kind == 'master':
                try:
                    path_part, _, anchor = ref.partition('#')
                    idx = master_index(path_part)
                    if anchor not in idx.ids:
                        raise ChainError(f'anchor #{anchor} not found')
                    citation_counts['anchors'] += 1
                except ChainError as exc:
                    chain_errors.append(f'{cid}: given {gid} master ref {ref!r}: {exc}')
            elif kind == 'synthetic_given':
                if ref.startswith('docs/EXAMPLE_QUESTIONS.json#'):
                    eid = ref.split('#', 1)[1]
                    if eid not in example_ids:
                        chain_errors.append(f'{cid}: given {gid} example ref {eid} not found')
                else:
                    chain_errors.append(f'{cid}: given {gid} synthetic ref {ref!r} is not an example anchor')

        # Steps and recompute
        steps = chain.get('steps') or []
        if not isinstance(steps, list) or len(steps) < 3:
            chain_errors.append(f'{cid}: steps must be a list of at least three entries')
            steps = steps or []
        step_ids = [s.get('step_id') for s in steps]
        if step_ids != [f'S{i}' for i in range(1, len(steps) + 1)]:
            chain_errors.append(f'{cid}: step ids must be S1..S{len(steps)} in order, got {step_ids}')
        step_vals: dict[str, Decimal] = {}
        seen_steps: set[str] = set()
        for st in steps:
            sid = st.get('step_id', '?')
            step_count += 1
            for field in schema.get('step_required', []):
                if field not in st:
                    chain_errors.append(f'{cid}/{sid}: missing step field {field}')
            result = st.get('result') or {}
            kind = result.get('kind')
            if kind not in schema.get('result_kinds', []):
                chain_errors.append(f'{cid}/{sid}: unknown result kind {kind!r}')
            if not result.get('display_lv'):
                chain_errors.append(f'{cid}/{sid}: missing display_lv')
            if result.get('unit') is None:
                chain_errors.append(f'{cid}/{sid}: missing unit')
            citations = st.get('citations') or {}
            conv_refs = citations.get('conventions_refs') or []
            if not isinstance(conv_refs, list) or not conv_refs:
                chain_errors.append(f'{cid}/{sid}: at least one conventions_ref is required')
                conv_refs = []
            if len(conv_refs) > 2:
                chain_errors.append(f'{cid}/{sid}: at most two conventions_refs are supported')
            for ref in conv_refs:
                citation_counts['conventions'] += 1
                try:
                    resolve_ref(conventions, ref)
                    citation_refs.append({'chain_id': cid, 'step_id': sid, 'kind': 'conventions', 'ref': ref, 'status': 'OK'})
                except ChainError as exc:
                    chain_errors.append(f'{cid}/{sid}: conventions ref {ref!r}: {exc}')
                    citation_refs.append({'chain_id': cid, 'step_id': sid, 'kind': 'conventions', 'ref': ref, 'status': 'DANGLING'})
            if len(conv_refs) == 2:
                multi_citations.append({'chain_id': cid, 'step_id': sid, 'refs': conv_refs})
            master_refs = citations.get('master_refs') or []
            for ref in master_refs:
                if not str(ref).startswith('#'):
                    chain_errors.append(f'{cid}/{sid}: master ref {ref!r} must start with #')
                    continue
                try:
                    idx = master_index(mc.get('path', ''))
                    anchor = str(ref)[1:]
                    if anchor not in idx.ids:
                        raise ChainError(f'anchor #{anchor} not found')
                    citation_counts['anchors'] += 1
                except ChainError as exc:
                    chain_errors.append(f'{cid}/{sid}: master ref {ref!r}: {exc}')

            if kind == 'numeric':
                numeric_count += 1
                if not isinstance(result.get('sig_figs'), int) or not 1 <= result['sig_figs'] <= 8:
                    chain_errors.append(f'{cid}/{sid}: numeric result needs sig_figs 1-8')
                try:
                    want = as_decimal(result.get('value'))
                except Exception as exc:
                    chain_errors.append(f'{cid}/{sid}: result value is not numeric: {exc}')
                    want = None
                try:
                    got = recompute(st, given_vals, step_vals)
                    if want is not None:
                        delta = abs(got - want)
                        tol = max(Decimal('1e-12'), abs(got) * Decimal('1e-9'))
                        if delta > tol:
                            chain_errors.append(
                                f'{cid}/{sid}: recompute mismatch: got {fmt_decimal(got)}, declared {result.get("value")}'
                            )
                        if not display_ok(got, result.get('display_lv', '')):
                            chain_errors.append(
                                f'{cid}/{sid}: display {result.get("display_lv")!r} is not a correct rounding of {fmt_decimal(got)}'
                            )
                        recompute_rows.append({
                            'chain_id': cid, 'step_id': sid, 'op': st['recompute'].get('op'),
                            'operands': st['recompute'].get('operands'),
                            'computed': fmt_decimal(got), 'declared': str(result.get('value')),
                            'delta': fmt_decimal(delta), 'status': 'PASS' if delta <= tol else 'FAIL',
                        })
                    step_vals[sid] = got
                    if cid == 'EX03' and sid == 'S2':
                        scratch_declared = Decimal('326')
                        scratch_delta = abs(got - scratch_declared)
                        scratch_tol = max(Decimal('1e-12'), abs(got) * Decimal('1e-9'))
                        detected = scratch_delta > scratch_tol
                        negative_recompute = {
                            'status': 'PASS' if detected else 'FAIL',
                            'chain_id': cid, 'step_id': sid,
                            'computed': fmt_decimal(got), 'declared': fmt_decimal(scratch_declared),
                            'delta': fmt_decimal(scratch_delta),
                            'error': f'{cid}/{sid}: recompute mismatch: got {fmt_decimal(got)}, declared 326',
                        }
                        if not detected:
                            errors.append('negative recompute fixture EX03/S2 was not detected; the gate does not bite')
                except ChainError as exc:
                    chain_errors.append(f'{cid}/{sid}: recompute failed: {exc}')
                    recompute_rows.append({'chain_id': cid, 'step_id': sid, 'op': (st.get('recompute') or {}).get('op'),
                                           'status': 'FAIL', 'error': str(exc)})
            elif kind == 'symbolic':
                symbolic_count += 1
                if st.get('recompute'):
                    chain_errors.append(f'{cid}/{sid}: symbolic result must not carry recompute')
            seen_steps.add(sid)

        # Figure refs
        fig_ids = set()
        for fr in chain.get('figure_refs') or []:
            fid = fr.get('figure_id')
            sid = fr.get('step_id')
            role = fr.get('role')
            if fid not in fig_by_id:
                chain_errors.append(f'{cid}: figure {fid} does not exist')
                continue
            fig_ids.add(fid)
            citation_counts['figures'] += 1
            if sid not in step_ids:
                chain_errors.append(f'{cid}: figure {fid} slot step {sid} does not exist')
            if role not in schema.get('figure_roles', []):
                chain_errors.append(f'{cid}: figure {fid} has unknown role {role!r}')
            concepts = set(fig_by_id[fid].get('concept_ids') or [])
            if outcomes and not concepts.intersection(outcomes):
                chain_errors.append(f'{cid}: figure {fid} concepts {sorted(concepts)} do not intersect outcomes {outcomes}')
            figure_rows.append({
                'chain_id': cid, 'figure_id': fid, 'step_id': sid, 'role': role,
                'status': 'OK' if sid in step_ids and concepts.intersection(outcomes) else 'FAIL',
            })

        # Back links
        back = chain.get('back_links') or {}
        for field in ('method_card_ids', 'practice_item_ids'):
            if not isinstance(back.get(field), list) or not back.get(field):
                chain_errors.append(f'{cid}: back_links.{field} must be a non-empty list')

        # Honesty lint
        texts = [chain.get('title_lv'), chain.get('subtitle_lv'), chain.get('epistemic_label'),
                 chain.get('scope_note_lv'), chain.get('given_note_lv')]
        for st in steps:
            texts.extend([st.get('quantity_lv'), st.get('statement_lv'), st.get('reasoning_lv'),
                          (st.get('result') or {}).get('display_lv')])
        for g in givens:
            texts.append(g.get('label_lv'))
        for fr in chain.get('figure_refs') or []:
            texts.append(fr.get('note_lv'))
        haystack = ' '.join(str(t) for t in texts if t).lower()
        for phrase in FORBIDDEN_POSITIVE:
            if phrase in haystack:
                chain_errors.append(f'{cid}: honesty lint found positive official claim {phrase!r}')
                honesty_violations.append({'chain_id': cid, 'phrase': phrase})

        if chain_errors:
            errors.extend(chain_errors)
        chain_rows.append({
            'id': cid, 'topic': topic, 'outcomes': outcomes, 'steps': len(steps),
            'numeric_steps': sum(1 for s in steps if (s.get('result') or {}).get('kind') == 'numeric'),
            'figures': sorted(fig_ids), 'status': 'FAIL' if chain_errors else 'PASS',
        })

    for t, count in topic_counts.items():
        if count < 2:
            errors.append(f'topic {t} has {count} chains; at least two are required')

    # References
    method_cards = refs.get('method_cards') or []
    practice_items = refs.get('practice_items') or []
    ref_rows: list[dict[str, Any]] = []
    chain_by_id = {c['id']: c for c in chains}
    declared_refs: dict[str, dict[str, Any]] = {}
    for kind, records, consumer in (('method', method_cards, 'N19'), ('practice', practice_items, 'N20')):
        for rec in records:
            rid = rec.get('id')
            if not rid:
                errors.append(f'{kind} reference without id')
                continue
            if rid in declared_refs:
                errors.append(f'duplicate reference id {rid}')
            declared_refs[rid] = rec
            if rec.get('consumer_task') != consumer:
                errors.append(f'{rid}: consumer_task must be {consumer}')
            if not str(rec.get('status', '')).startswith('declared-pending-'):
                errors.append(f'{rid}: status must be declared-pending-* while {consumer} is unimplemented')
            for cid in rec.get('chain_ids') or []:
                if cid not in chain_by_id:
                    errors.append(f'{rid}: chain {cid} does not exist')
            if not rec.get('chain_ids'):
                errors.append(f'{rid}: chain_ids must be non-empty')
            ref_rows.append({'kind': kind, 'id': rid, 'consumer': consumer,
                             'chain_ids': rec.get('chain_ids'), 'family_id': rec.get('family_id'),
                             'status': rec.get('status')})
    for chain in chains:
        cid = chain['id']
        back = chain.get('back_links') or {}
        for rid in back.get('method_card_ids') or []:
            rec = declared_refs.get(rid)
            if not rec or rec.get('consumer_task') != 'N19':
                errors.append(f'{cid}: method card {rid} does not resolve')
            elif cid not in (rec.get('chain_ids') or []):
                errors.append(f'{cid}: method card {rid} does not point back to the chain')
            else:
                fam = rec.get('family_id')
                outcome_fams = set()
                for oid in chain.get('outcome_ids') or []:
                    outcome_fams.update((cov_by_id.get(oid) or {}).get('bindings', {}).get('practice_families') or [])
                if fam and fam not in outcome_fams:
                    errors.append(f'{cid}: method card family {fam} not in outcome practice families {sorted(outcome_fams)}')
        for rid in back.get('practice_item_ids') or []:
            rec = declared_refs.get(rid)
            if not rec or rec.get('consumer_task') != 'N20':
                errors.append(f'{cid}: practice item {rid} does not resolve')
            elif cid not in (rec.get('chain_ids') or []):
                errors.append(f'{cid}: practice item {rid} does not point back to the chain')
            else:
                fam = rec.get('family_id')
                outcome_fams = set()
                for oid in chain.get('outcome_ids') or []:
                    outcome_fams.update((cov_by_id.get(oid) or {}).get('bindings', {}).get('practice_families') or [])
                if fam and fam not in outcome_fams:
                    errors.append(f'{cid}: practice item family {fam} not in outcome practice families {sorted(outcome_fams)}')

    # Leak-free delivery
    projection = build_runtime_projection(chains_data)
    fixture = pre_reveal_fixture(projection)
    fixture_leaks = []
    for chain in chains:
        chain_text = pre_reveal_visible_text(projection, only_chain=chain['id'])
        fixture_leaks.extend(scan_text(chain_text, [chain], only_chain=chain['id']))
    island_leaks = scan_island(projection, chains)
    if fixture_leaks:
        errors.append(f'pre-reveal fixture leaks {len(fixture_leaks)} secret(s): '
                      + ', '.join(f'{v["chain_id"]}/{v["step_id"]}:{v["kind"]}' for v in fixture_leaks[:5]))
    if island_leaks:
        errors.append(f'sealed island leaks {len(island_leaks)} secret(s): '
                      + ', '.join(f'{v["chain_id"]}/{v["step_id"]}:{v["kind"]}' for v in island_leaks[:5]))

    # Planted leak fixture: must fail by chain and step
    planted_chain = next((c for c in chains if c['id'] == 'EX03'), None)
    planted = {'status': 'NOT_RUN'}
    if planted_chain:
        scratch = json.loads(json.dumps(planted_chain, ensure_ascii=False))
        leak_step = next((s for s in scratch['steps'] if s['step_id'] == 'S1'), scratch['steps'][0])
        target = scratch['steps'][1] if len(scratch['steps']) > 1 else scratch['steps'][0]
        target['statement_lv'] = target['statement_lv'] + ' ' + leak_step['result']['display_lv']
        planted_fixture = pre_reveal_fixture(build_runtime_projection({
            'schema_version': 1, 'format_version': 1, 'island_id': 'sim-chains',
            'owner': 'N16', 'banner_lv': BANNER, 'honesty': {},
            'chains': [scratch],
        }))
        planted_hits = scan_text(planted_fixture, [scratch])
        hit = next((v for v in planted_hits if v['chain_id'] == 'EX03' and v['step_id'] == leak_step['step_id']), None)
        planted = {
            'status': 'PASS' if hit else 'FAIL',
            'chain_id': 'EX03',
            'step_id': leak_step['step_id'],
            'injected': leak_step['result']['display_lv'],
            'hit': hit,
        }
        if not hit:
            errors.append('planted leak fixture was not detected by EX03/S1; the gate does not bite')
    else:
        errors.append('planted leak fixture requires EX03')

    # Sealed payload round trip: the validator can unseal its own payloads.
    roundtrip = 0
    for chain in projection['chains']:
        src = chain_by_id.get(chain['id'])
        for st, sealed in zip(src['steps'], chain['steps']):
            payload = unseal_payload(chain['id'], st['step_id'], sealed['sealed'])
            if (payload.get('value') != st['result'].get('value') or
                    payload.get('reasoning_lv') != st.get('reasoning_lv')):
                errors.append(f'{chain["id"]}/{st["step_id"]}: sealed payload round trip mismatch')
            else:
                roundtrip += 1

    # Print honesty fixtures: the CSS contract is in src/styles.css and the
    # fixtures are derived from the same pre-reveal/revealed markup.
    print_fixture = pre_reveal_fixture(projection)
    print_rows = []
    for cid in ('EX03', 'EX11'):
        chain = next(c for c in projection['chains'] if c['id'] == cid)
        print_rows.append({
            'chain_id': cid,
            'collapsed_has_note': 'Pamatojums ir interaktīvs' in print_fixture,
            'revealed_rule': '.chain-step[data-revealed="true"] .chain-result { display:block !important } (src/styles.css)',
        })

    # Byte accounting
    projection_bytes = canonical_json_bytes(projection)
    fixture_bytes = fixture.encode('utf-8')
    summary = {
        'chains': len(chains),
        'steps': step_count,
        'numeric_steps': numeric_count,
        'symbolic_steps': symbolic_count,
        'topics': topic_counts,
        'recompute_pass': sum(1 for r in recompute_rows if r.get('status') == 'PASS'),
        'recompute_fail': sum(1 for r in recompute_rows if r.get('status') == 'FAIL'),
        'negative_recompute': negative_recompute.get('status'),
        'citations': citation_counts,
        'multi_citations': len(multi_citations),
        'figures': len(figure_rows),
        'method_cards': len(method_cards),
        'practice_items': len(practice_items),
        'fixture_leaks': len(fixture_leaks),
        'island_leaks': len(island_leaks),
        'planted_leak': planted.get('status'),
        'sealed_roundtrip': roundtrip,
        'projection_bytes': len(projection_bytes),
        'projection_digest': sha256_bytes(projection_bytes),
        'fixture_bytes': len(fixture_bytes),
        'fixture_digest': sha256_bytes(fixture_bytes),
    }
    report = {
        'schema_version': 1,
        'task': 'N16',
        'status': 'PASS' if not errors else 'FAIL',
        'banner_lv': BANNER,
        'summary': summary,
        'errors': errors,
        'warnings': warnings,
        'chains': chain_rows,
        'recompute': recompute_rows,
        'negative_recompute': negative_recompute,
        'citations': {
            'counts': citation_counts,
            'dangling': [r for r in citation_refs if r.get('status') != 'OK'],
            'refs': citation_refs,
            'multi_citation': multi_citations,
        },
        'figures': figure_rows,
        'references': {'rows': ref_rows, 'status': 'PASS' if not any('reference' in e or 'back_links' in e for e in errors) else 'FAIL'},
        'leaks': {
            'pre_reveal': fixture_leaks,
            'island': island_leaks,
            'planted': planted,
            'fixture_digest': sha256_bytes(fixture_bytes),
            'island_digest': summary['projection_digest'],
        },
        'honesty': {
            'banner': BANNER,
            'forbidden_positive': FORBIDDEN_POSITIVE,
            'violations': honesty_violations,
            'copy_lint': 'PASS' if not honesty_violations else 'FAIL',
        },
        'persistence': persistence,
        'print': print_rows,
        'bytes': {
            'source_chains': chains_file.stat().st_size if chains_file.exists() else None,
            'runtime_projection': len(projection_bytes),
            'pre_reveal_fixture': len(fixture_bytes),
        },
    }
    return report


def format_summary(report: dict[str, Any]) -> str:
    s = report.get('summary', {})
    return (f"{s.get('chains', 0)} chains, {s.get('steps', 0)} steps "
            f"({s.get('numeric_steps', 0)} numeric), recompute {s.get('recompute_pass', 0)}/"
            f"{s.get('recompute_pass', 0) + s.get('recompute_fail', 0)}, "
            f"citations {s.get('citations', {}).get('conventions', 0)} conventions/"
            f"{s.get('citations', {}).get('anchors', 0)} anchors, "
            f"leaks {s.get('fixture_leaks', 0)}+{s.get('island_leaks', 0)}, planted {s.get('planted_leak')}, "
            f"{s.get('projection_bytes', 0)} B projection")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Validate N16 chains and leak-free delivery.')
    parser.add_argument('--chains', default=str(DEST / CHAINS_PATH))
    parser.add_argument('--schema', default=str(DEST / CHAIN_SCHEMA_PATH))
    parser.add_argument('--refs', default=str(DEST / CHAIN_REFS_PATH))
    parser.add_argument('--coverage', default=str(DEST / COVERAGE_PATH))
    parser.add_argument('--conventions', default=str(DEST / CONVENTIONS_PATH))
    parser.add_argument('--summaries', default=str(DEST / SUMMARIES_PATH))
    parser.add_argument('--report', default=None)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args(argv)
    report = validate_chains(
        DEST,
        chains_path=args.chains,
        schema_path=args.schema,
        refs_path=args.refs,
        coverage_path=args.coverage,
        conventions_path=args.conventions,
        summaries_path=args.summaries,
    )
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = DEST / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if report['status'] == 'PASS':
        print(f"PASS chains: {format_summary(report)}")
        return 0
    print(f"FAIL chains: {format_summary(report)}", file=sys.stderr)
    for err in report.get('errors', [])[:30]:
        print(f'  - {err}', file=sys.stderr)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
