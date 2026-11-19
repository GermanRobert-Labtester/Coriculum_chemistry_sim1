#!/usr/bin/env python3
"""N12 Unified Leak-Scan Engine.

Single authoritative leak scanner for both Phase III figures (T2-3+, data,
annotations, and rendered SVG) and N08 recall layers. Implements:
- N10 unit-grammar & N03 conversions unit-normalized quantity comparison
- N12-LEAK-SIG-01 significance rule (distinctive values vs common constants)
- N12-LEAK-BORDER-01 borderline range flagging rule
- N12-LEAK-EXEMPT-01 auditable exemption rule
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402
from validate_terms import TERMS_PATH, UnitGrammarError, parse_unit  # noqa: E402

CONVENTIONS_PATH = 'data/conventions.json'
GOLDEN_VECTORS_PATH = 'data/golden_vectors.json'
EXAMPLES_PATH = 'docs/EXAMPLE_QUESTIONS.json'
RECALL_LAYERS_PATH = 'data/recall_layers.json'
FIGURES_T12_PATH = 'data/figures_t12.json'
FIGURES_T23_PATH = 'data/figures_t23.json'
FIGURES_T4_PATH = 'data/figures_t4.json'
FIGURES_T5_PATH = 'data/figures_t5.json'
FIGURES_T67_PATH = 'data/figures_t67.json'

SIGNIFICANCE_RULE_ID = 'N12-LEAK-SIG-01'
SIGNIFICANCE_RULE_VERBATIM = (
    'Only values distinctive to the instance or family are scan targets. '
    'Bare un-united integers in {0..9} and common structural/scaling constants '
    '{10, 100, 1000, 0.1, 0.01, 0.001, 273.15, 298.15} are NOT scan targets when '
    'appearing without a matching unit; they ARE scan targets whenever paired with '
    'a dimensionally matching unit (e.g. "10 mL", "100 mmol/L") or written in a '
    'distinctive precision form (e.g. "10.5", "12.35") or explicitly marked distinctive.'
)

BORDERLINE_RULE_ID = 'N12-LEAK-BORDER-01'
BORDERLINE_RULE_VERBATIM = (
    'Any gradeable figure whose numeric axis range or scale window [min, max] pins '
    'a gradeable target value onto an endpoint or within the outer 2% extreme '
    '(normalized position <= 0.02 or >= 0.98) or constrains the span to <= 2 steps '
    'around the target is flagged with FLAG_BORDERLINE_RANGE for authoring review.'
)

EXEMPTION_RULE_ID = 'N12-LEAK-EXEMPT-01'
EXEMPTION_RULE_VERBATIM = (
    'Only non-gradeable teaching/reading-display figures (gradeable=false) may '
    'declare leak_scan_exemption with an explicit reason_code, non-empty Latvian '
    'reason_lv (>= 20 chars), and explicit exempted_values list; gradeable figures '
    'cannot exempt their own scored answer targets (E_LEAK_ILLEGAL_EXEMPTION), and '
    'any unlisted answer-key leak on an exempted figure is still caught. All '
    'exemptions are audited at N40 closure.'
)

ALLOWED_EXEMPTION_CODES = {
    'EXEMPT_READING_DISPLAY',
    'EXEMPT_WORKED_DERIVATION',
    'EXEMPT_GIVEN_INPUT',
}

# Common bare constants excluded when un-united (N12-LEAK-SIG-01)
COMMON_BARE_CONSTANTS = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    '10', '100', '1000', '0.1', '0.01', '0.001', '273.15', '298.15',
}

# Canonical scale factor per unit element relative to base SI-derived units in conventions.json
ELEMENT_SCALE_FACTORS: dict[str, Decimal] = {
    'kg': Decimal('1000'),
    'g': Decimal('1'),
    'mg': Decimal('0.001'),
    'm³': Decimal('1000'),
    'dm³': Decimal('1'),
    'L': Decimal('1'),
    'mL': Decimal('0.001'),
    'cm³': Decimal('0.001'),
    'mol': Decimal('1'),
    'mmol': Decimal('0.001'),
    'µmol': Decimal('0.000001'),
    'kJ': Decimal('1000'),
    'J': Decimal('1'),
    's': Decimal('1'),
    'min': Decimal('60'),
    'm': Decimal('1'),
    'cm': Decimal('0.01'),
    'mm': Decimal('0.001'),
    'nm': Decimal('0.000000001'),
    'K': Decimal('1'),
    '°C': Decimal('1'),
    'C': Decimal('1'),
    'V': Decimal('1'),
    'kPa': Decimal('1000'),
    'A': Decimal('1'),
    'pH': Decimal('1'),
}

# Regex matching numeric quantities followed by a unit expression (e.g. "500 mg", "0,5 mg/mL", "16,25 mL", "5,0 % (m/V)")
QUANTITY_TOKEN_RE = re.compile(
    r'(?<![A-Za-z0-9.])'
    r'([−\-]?\d+(?:[.,]\d+)?)'
    r'(?:\s*[×·]\s*10\^?([−\-]?\d+))?'
    r'\s*'
    r'('
    r'%\s*\([mVv]/[mVv]\)'
    r'|%'
    r'|[A-Za-zµ°][A-Za-z0-9µ°³²¹⁻¹⁻²⁻³^·/()]*'
    r')'
)


def normalize_text(text: str) -> str:
    s = str(text).lower().strip()
    s = s.replace('\u00a0', ' ').replace('−', '-')
    s = re.sub(r'(\d),(\d)', r'\1.\2', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def _to_decimal(raw: Any) -> Decimal | None:
    if isinstance(raw, bool):
        return None
    s = str(raw).strip().replace('\u00a0', '').replace('−', '-').replace(',', '.')
    try:
        d = Decimal(s)
    except InvalidOperation:
        return None
    return d if d.is_finite() else None


def _unit_basis_tag(unit_str: str) -> str:
    u = unit_str.strip()
    if '(m/m)' in u or '(M/M)' in u:
        return 'pct_mm'
    if '(m/V)' in u or '(m/v)' in u:
        return 'pct_mv'
    if '(V/V)' in u or '(v/v)' in u:
        return 'pct_vv'
    if u == '%':
        return 'pct_bare'
    return ''


def normalize_quantity(value: Any, unit_str: str | None, grammar: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize (value, unit_str) through the N10 unit grammar to canonical base scale."""
    dec = _to_decimal(value)
    if dec is None:
        return None
    u = (unit_str or '').strip()
    if not u:
        return None
    if u in ('%', '% (m/m)', '% (m/V)', '% (V/V)', '1', 'fraction', 'fraction (m/V)', 'ppm'):
        if u == 'ppm':
            canon = dec * Decimal('0.000001')
            tag = 'ppm_or_fraction'
        elif u.startswith('%'):
            canon = dec * Decimal('0.01')
            tag = _unit_basis_tag(u)
        else:
            canon = dec
            tag = 'dimensionless'
        return {
            'raw_value': str(value),
            'raw_unit': u,
            'canonical_value': canon,
            'dimension_vector': {},
            'basis_tag': tag,
        }

    try:
        parsed = parse_unit(u, grammar)
    except UnitGrammarError:
        return None

    scale = Decimal('1')
    for term in parsed['numerator']:
        el_scale = ELEMENT_SCALE_FACTORS.get(term['element'])
        if el_scale is None:
            return None
        scale *= el_scale ** int(term['exponent'])
    for term in parsed['denominator']:
        el_scale = ELEMENT_SCALE_FACTORS.get(term['element'])
        if el_scale is None:
            return None
        scale /= el_scale ** int(term['exponent'])

    return {
        'raw_value': str(value),
        'raw_unit': u,
        'canonical_value': dec * scale,
        'dimension_vector': parsed['dimension_vector'],
        'basis_tag': '',
    }


def _numeric_forms(val: float | int, distinctive: bool = False) -> set[str]:
    """Generate normalized bare numeric string forms subject to N12-LEAK-SIG-01."""
    forms: set[str] = set()
    if isinstance(val, bool):
        return forms
    f = float(val)
    if f.is_integer():
        iv = int(f)
        s_iv = str(iv)
        if abs(iv) >= 10 and s_iv not in COMMON_BARE_CONSTANTS:
            forms.add(s_iv)
        if s_iv not in COMMON_BARE_CONSTANTS or distinctive:
            # Explicit decimal precision forms (e.g., 10.00, 30.0) are distinctive
            if s_iv not in COMMON_BARE_CONSTANTS:
                forms.add(f'{f:.1f}')
                forms.add(f'{f:.2f}')
            else:
                # For common constants like 10, only high-precision decimal forms are distinctive
                forms.add(f'{f:.2f}')
    else:
        for fmt in (f'{f:g}', f'{f:.1f}', f'{f:.2f}', f'{f:.3f}'):
            digits = fmt.lstrip('-').replace('.', '').lstrip('0')
            significant = len(digits)
            if significant < 2 and fmt != f'{f:g}':
                continue
            if fmt not in COMMON_BARE_CONSTANTS:
                forms.add(fmt)
            trimmed = fmt.rstrip('0').rstrip('.') if '.' in fmt else fmt
            if trimmed and trimmed not in COMMON_BARE_CONSTANTS:
                forms.add(trimmed)
    return forms


def is_significant_bare_token(needle: str) -> bool:
    """Enforce N12-LEAK-SIG-01 significance rule for bare un-united numbers."""
    s = needle.strip().replace(',', '.')
    if s in COMMON_BARE_CONSTANTS:
        return False
    # Single-digit bare integers 0..9 are never bare targets
    if re.fullmatch(r'-?\d', s):
        return False
    return True


def extract_quantities_from_text(text: str, grammar: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract and unit-normalize all quantity expressions (<num> <unit>) from text."""
    out: list[dict[str, Any]] = []
    # Normalize XML tags away for SVG scanning without gluing adjacent text
    clean = re.sub(r'<[^>]+>', ' ', str(text))
    for m in QUANTITY_TOKEN_RE.finditer(clean):
        num_s = m.group(1).replace('−', '-').replace(',', '.')
        exp_s = m.group(2)
        unit_s = m.group(3).strip().rstrip('.,;:)')
        # Normalize '% (m/V)' spacing
        unit_s = re.sub(r'%\s*\(', '% (', unit_s)
        try:
            num_dec = Decimal(num_s)
            if exp_s:
                num_dec *= Decimal(10) ** int(exp_s.replace('−', '-'))
        except Exception:
            continue
        norm = normalize_quantity(num_dec, unit_s, grammar)
        if norm is not None:
            norm['matched_text'] = m.group(0).strip()
            out.append(norm)
    return out


def extract_family_answer_tokens(
    golden_vectors: dict[str, Any],
    examples_data: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """Collect normalized answer tokens per family_id from golden vectors and examples."""
    by_family: dict[str, list[dict[str, Any]]] = {}

    def add_token(fam: str, raw: str, norm: str, source: str, kind: str,
                  numeric_val: float | None = None, unit: str = '') -> None:
        if not norm or len(norm) < 2:
            return
        by_family.setdefault(fam, []).append({
            'raw': raw,
            'norm': norm,
            'source': source,
            'kind': kind,
            'value': numeric_val,
            'unit': unit,
        })

    for vec in golden_vectors.get('vectors', []):
        inst = vec.get('instance', {})
        fam = inst.get('family_id')
        if not fam:
            continue
        vid = vec.get('vector_id', 'vec')
        payload = inst.get('payload', {})
        if isinstance(payload.get('expected_value'), (int, float)):
            ev = payload['expected_value']
            unit = str(payload.get('unit', '')).strip()
            for nf in _numeric_forms(ev):
                add_token(fam, str(ev), nf, vid, 'numeric', numeric_val=float(ev), unit=unit)
                if unit:
                    add_token(fam, f'{ev} {unit}', f'{nf} {unit.lower()}', vid, 'numeric_unit', numeric_val=float(ev), unit=unit)
            if unit:
                # Always keep the raw quantity target for unit-normalized comparison even if bare constant
                add_token(fam, f'{ev} {unit}', f'{ev} {unit.lower()}', vid, 'quantity_target', numeric_val=float(ev), unit=unit)
        if isinstance(payload.get('display_lv'), str) and payload['display_lv'].strip():
            disp = payload['display_lv'].strip()
            add_token(fam, disp, normalize_text(disp), vid, 'display')
        if isinstance(payload.get('expected_text'), str) and payload['expected_text'].strip():
            et = payload['expected_text'].strip()
            if len(et) >= 4:
                add_token(fam, et, normalize_text(et), vid, 'text')
        for cid in payload.get('correct_ids', []) or []:
            if isinstance(cid, str) and len(cid) >= 3 and cid not in ('TRUE', 'FALSE'):
                add_token(fam, cid, cid.lower(), vid, 'choice_id')

    for ex in examples_data.get('examples', []):
        fam = ex.get('family_id')
        if not fam:
            continue
        exp = ex.get('expected', {})
        if isinstance(exp.get('display_lv'), str):
            add_token(fam, exp['display_lv'], normalize_text(exp['display_lv']), ex.get('example_id', 'ex'), 'display')

    return by_family


def scan_text_for_leaks(
    family_id: str,
    layer_num: int | str,
    text: str,
    answer_tokens: list[dict[str, Any]],
    surface: str = 'data',
    grammar: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Unified token-boundary + unit-normalized leak scanner."""
    norm_text = normalize_text(re.sub(r'<[^>]+>', ' ', str(text)))
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()

    # 1. Token-boundary string / bare-numeric checks (N12-LEAK-SIG-01 enforced)
    for tok in answer_tokens:
        needle = tok.get('norm', '')
        if not needle:
            continue
        if tok.get('kind') == 'quantity_target':
            continue
        if tok.get('kind') == 'numeric' and not is_significant_bare_token(needle):
            continue
        pattern = r'(?<![a-z0-9.])' + re.escape(needle) + r'(?![a-z0-9]|\.\d)'
        if re.search(pattern, norm_text):
            key = f'{family_id}:{layer_num}:{surface}:{needle}'
            if key not in seen:
                seen.add(key)
                findings.append({
                    'error_id': 'E_LEAK_DETECTED',
                    'match_kind': tok.get('kind', 'token'),
                    'surface': surface,
                    'family_id': family_id,
                    'layer': layer_num,
                    'leaked_raw': tok['raw'],
                    'leaked_norm': needle,
                    'source': tok.get('source', ''),
                })

    # 2. Unit-normalized quantity checks (e.g. 500 mg == 0.5 g, 0.5 mg/mL == 500 mg/L)
    if grammar:
        extracted = extract_quantities_from_text(text, grammar)
        qty_targets: list[tuple[dict[str, Any], dict[str, Any]]] = []
        for tok in answer_tokens:
            if tok.get('value') is not None and tok.get('unit'):
                tnorm = normalize_quantity(tok['value'], tok['unit'], grammar)
                if tnorm is not None:
                    qty_targets.append((tok, tnorm))
        for ext in extracted:
            for tok, tnorm in qty_targets:
                if ext['dimension_vector'] != tnorm['dimension_vector']:
                    continue
                if ext['basis_tag'] != tnorm['basis_tag']:
                    continue
                tval = tnorm['canonical_value']
                eval_d = ext['canonical_value']
                tol = max(Decimal('1e-9'), abs(tval) * Decimal('1e-6'))
                if abs(eval_d - tval) <= tol:
                    key = f"{family_id}:{layer_num}:{surface}:unit_norm:{ext['matched_text']}->{tok['raw']}"
                    if key not in seen:
                        seen.add(key)
                        findings.append({
                            'error_id': 'E_LEAK_DETECTED',
                            'match_kind': 'unit_normalized',
                            'surface': surface,
                            'family_id': family_id,
                            'layer': layer_num,
                            'leaked_raw': ext['matched_text'],
                            'leaked_norm': f"{ext['canonical_value']} (dim={ext['dimension_vector']})",
                            'target_raw': f"{tok['value']} {tok['unit']}",
                            'source': tok.get('source', ''),
                        })

    return findings


def _strip_figure_scan_metadata(rec: dict[str, Any]) -> dict[str, Any]:
    """Return copy of figure data excluding declarative scan/exemption metadata."""
    cleaned = {}
    for k, v in rec.items():
        if k in ('answer_targets', 'leak_scan_exemption', 'grading_reference'):
            continue
        cleaned[k] = v
    return cleaned


def _check_borderline_ranges(
    rec: dict[str, Any],
    targets: list[dict[str, Any]],
    grammar: dict[str, Any],
) -> list[dict[str, Any]]:
    """Enforce N12-LEAK-BORDER-01 borderline range flagging rule."""
    flags: list[dict[str, Any]] = []
    fid = rec.get('id', '?')
    if not rec.get('gradeable'):
        return flags

    ranges: list[dict[str, Any]] = []
    for ax_name, ax in (rec.get('axes') or {}).items():
        if isinstance(ax, dict) and ax.get('min') is not None and ax.get('max') is not None:
            ranges.append({
                'axis': f'axes.{ax_name}',
                'min': ax['min'],
                'max': ax['max'],
                'step': ax.get('step'),
                'unit': ax.get('unit') or '',
            })
    bg = rec.get('burette_geometry') or {}
    for col in bg.get('columns') or []:
        if col.get('view_min_ml') is not None and col.get('view_max_ml') is not None:
            ranges.append({
                'axis': f"burette.{col.get('id', 'col')}",
                'min': col['view_min_ml'],
                'max': col['view_max_ml'],
                'step': bg.get('division_ml', '0.1'),
                'unit': 'mL',
            })

    for rng in ranges:
        rmin = _to_decimal(rng['min'])
        rmax = _to_decimal(rng['max'])
        if rmin is None or rmax is None or rmax <= rmin:
            continue
        span = rmax - rmin
        rstep = _to_decimal(rng.get('step'))
        min_norm = normalize_quantity(rmin, rng['unit'], grammar) if rng['unit'] else None
        max_norm = normalize_quantity(rmax, rng['unit'], grammar) if rng['unit'] else None
        for tgt in targets:
            tval = _to_decimal(tgt.get('value'))
            tunit = (tgt.get('unit') or '').strip()
            if tval is None:
                continue
            # Convert target into axis unit if units differ
            t_in_axis: Decimal | None = None
            if not rng['unit'] and tunit in ('', '1'):
                t_in_axis = tval
            elif rng['unit'] and tunit:
                tn = normalize_quantity(tval, tunit, grammar)
                if tn and min_norm and max_norm and tn['dimension_vector'] == min_norm['dimension_vector'] and tn['basis_tag'] == min_norm['basis_tag']:
                    # Scale factor from canonical back to axis unit
                    axis_unit_scale = normalize_quantity(Decimal('1'), rng['unit'], grammar)
                    if axis_unit_scale and axis_unit_scale['canonical_value'] != 0:
                        t_in_axis = tn['canonical_value'] / axis_unit_scale['canonical_value']
            if t_in_axis is None:
                continue
            pos = (t_in_axis - rmin) / span
            near_extreme = (Decimal('-0.001') <= pos <= Decimal('0.02')) or (Decimal('0.98') <= pos <= Decimal('1.001'))
            tight_span = (rstep is not None and rstep > 0 and span <= rstep * Decimal('2') and Decimal('0') <= pos <= Decimal('1'))
            if near_extreme or tight_span:
                flags.append({
                    'flag_id': 'FLAG_BORDERLINE_RANGE',
                    'rule_id': BORDERLINE_RULE_ID,
                    'figure_id': fid,
                    'axis': rng['axis'],
                    'range': [str(rmin), str(rmax)],
                    'unit': rng['unit'],
                    'target_value': f'{tval} {tunit}'.strip(),
                    'normalized_position': f'{pos:.4f}',
                    'reason': 'Axis/scale range pins gradeable target to a readable extreme or <=2 steps.',
                })
    return flags


def _render_figures_with_node(figures: list[dict[str, Any]], repo_root: Path) -> dict[str, str]:
    """Render figures deterministically via the shipped JS renderer for leak scanning."""
    payload = json.dumps({
        'figures': figures,
        'terms': load_json(repo_root / TERMS_PATH),
        'conventions': load_json(repo_root / CONVENTIONS_PATH),
    }, ensure_ascii=False)
    js_script = (
        "const fs = require('fs');\n"
        "const path = require('path');\n"
        "const vm = require('vm');\n"
        "const inp = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sandbox = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sandbox.globalThis = sandbox;\n"
        "vm.createContext(sandbox);\n"
        "vm.runInContext(fs.readFileSync(path.join(process.cwd(), 'src/terms-loader.js'), 'utf8'), sandbox);\n"
        "vm.runInContext(fs.readFileSync(path.join(process.cwd(), 'src/figure-framework.js'), 'utf8'), sandbox);\n"
        "const termsFakeDoc = { getElementById(id){ return id==='sim-terms'?{textContent:JSON.stringify(inp.terms)}:null; } };\n"
        "const termsObj = sandbox.SimTerms.load(termsFakeDoc);\n"
        "const out = {};\n"
        "for (const rec of inp.figures) {\n"
        "  out[rec.id] = sandbox.SimFigures.renderFigureSvg(rec, { terms: termsObj, conventions: inp.conventions, theme: 'light' });\n"
        "}\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    proc = subprocess.run(
        ['node', '-e', js_script],
        input=payload,
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'Node figure render failed for leak scan: {proc.stderr}')
    return json.loads(proc.stdout)


def _is_value_exempted(
    finding: dict[str, Any],
    exempted_norms: list[dict[str, Any]],
    grammar: dict[str, Any],
) -> bool:
    if not exempted_norms:
        return False
    # Check unit-normalized match against exempted_values
    val_candidates = []
    if finding.get('target_raw'):
        parts = finding['target_raw'].split(' ', 1)
        nq = normalize_quantity(parts[0], parts[1] if len(parts) > 1 else '1', grammar)
        if nq:
            val_candidates.append(nq)
    raw = str(finding.get('leaked_raw', '')).strip()
    exts = extract_quantities_from_text(raw, grammar)
    val_candidates.extend(exts)
    if not val_candidates:
        d = _to_decimal(raw)
        if d is not None:
            for ex in exempted_norms:
                ex_d = _to_decimal(ex['raw_value'])
                if ex_d is not None and abs(d - ex_d) <= Decimal('1e-9'):
                    return True
        return False

    for vc in val_candidates:
        for ex in exempted_norms:
            if vc['dimension_vector'] == ex['dimension_vector'] and vc['basis_tag'] == ex['basis_tag']:
                tol = max(Decimal('1e-9'), abs(ex['canonical_value']) * Decimal('1e-6'))
                if abs(vc['canonical_value'] - ex['canonical_value']) <= tol:
                    return True
    return False


def scan_figure_record(
    rec: dict[str, Any],
    answer_targets: list[dict[str, Any]],
    terms_by_key: dict[str, dict[str, Any]],
    grammar: dict[str, Any],
    rendered_svg: str = '',
) -> dict[str, Any]:
    """Scan one figure record across data, annotations, rendered SVG, borderline ranges & exemptions."""
    fid = rec.get('id', '?')
    gradeable = bool(rec.get('gradeable', False))
    exemption = rec.get('leak_scan_exemption')
    errors: list[str] = []
    leaks: list[dict[str, Any]] = []
    exempted_hits: list[dict[str, Any]] = []

    # 1. Validate exemption contract (N12-LEAK-EXEMPT-01)
    is_exempt = False
    exempted_norms: list[dict[str, Any]] = []
    if isinstance(exemption, dict) and exemption.get('exempt'):
        if gradeable:
            errors.append(
                f'{fid}: [E_LEAK_ILLEGAL_EXEMPTION] Gradeable figure cannot declare leak_scan_exemption.'
            )
        else:
            rcode = exemption.get('reason_code')
            rlv = str(exemption.get('reason_lv') or '').strip()
            evals = exemption.get('exempted_values') or []
            if rcode not in ALLOWED_EXEMPTION_CODES:
                errors.append(f'{fid}: [E_LEAK_BAD_EXEMPTION] Unknown exemption reason_code {rcode!r}')
            if len(rlv) < 20:
                errors.append(f'{fid}: [E_LEAK_BAD_EXEMPTION] Exemption reason_lv too short')
            if not evals:
                errors.append(f'{fid}: [E_LEAK_BAD_EXEMPTION] Exemption must list exempted_values')
            if not errors:
                is_exempt = True
                for ev in evals:
                    nq = normalize_quantity(ev.get('value'), ev.get('unit') or '1', grammar)
                    if nq:
                        exempted_norms.append(nq)

    # 2. Build scan tokens from answer_targets
    tokens: list[dict[str, Any]] = []
    for tgt in answer_targets:
        val = tgt.get('value')
        unit = str(tgt.get('unit') or '').strip()
        src = tgt.get('vector_id') or tgt.get('family_id') or tgt.get('source') or 'target'
        distinctive = bool(tgt.get('distinctive', False))
        dec = _to_decimal(val)
        if dec is not None:
            for nf in _numeric_forms(float(dec), distinctive=distinctive):
                tokens.append({
                    'raw': str(val), 'norm': nf, 'source': src,
                    'kind': 'numeric', 'value': float(dec), 'unit': unit,
                })
                if unit:
                    tokens.append({
                        'raw': f'{val} {unit}', 'norm': f'{nf} {unit.lower()}', 'source': src,
                        'kind': 'numeric_unit', 'value': float(dec), 'unit': unit,
                    })
            if unit:
                tokens.append({
                    'raw': f'{val} {unit}', 'norm': f'{val} {unit.lower()}', 'source': src,
                    'kind': 'quantity_target', 'value': float(dec), 'unit': unit,
                })
        if isinstance(tgt.get('text'), str) and len(tgt['text'].strip()) >= 3:
            tokens.append({
                'raw': tgt['text'], 'norm': normalize_text(tgt['text']),
                'source': src, 'kind': 'text',
            })

    # 3. Scan three surfaces: data, annotations, rendered SVG
    data_payload = json.dumps(_strip_figure_scan_metadata(rec), ensure_ascii=False)
    ann_texts: list[str] = []
    for ann in rec.get('annotations') or []:
        if ann.get('text_override_lv'):
            ann_texts.append(str(ann['text_override_lv']))
        akey = ann.get('annotation_key')
        if akey and akey in terms_by_key:
            ann_texts.append(str(terms_by_key[akey].get('text_lv', '')))
    ann_payload = ' | '.join(ann_texts)

    raw_findings: list[dict[str, Any]] = []
    raw_findings.extend(scan_text_for_leaks(fid, 'data', data_payload, tokens, surface='data', grammar=grammar))
    raw_findings.extend(scan_text_for_leaks(fid, 'annotations', ann_payload, tokens, surface='annotations', grammar=grammar))
    if rendered_svg:
        raw_findings.extend(scan_text_for_leaks(fid, 'rendered', rendered_svg, tokens, surface='rendered', grammar=grammar))

    for fnd in raw_findings:
        if is_exempt and _is_value_exempted(fnd, exempted_norms, grammar):
            exempted_hits.append(fnd)
        else:
            leaks.append(fnd)
            errors.append(
                f"{fid}: [E_LEAK_DETECTED] ({fnd['surface']}/{fnd['match_kind']}) leaked {fnd['leaked_raw']!r} (target={fnd.get('target_raw', fnd['leaked_norm'])})"
            )

    # 4. Borderline range flagging (N12-LEAK-BORDER-01)
    flags = _check_borderline_ranges(rec, answer_targets, grammar)

    outcome = 'FAIL' if errors else ('EXEMPT' if is_exempt else ('FLAG' if flags else 'PASS'))
    return {
        'figure_id': fid,
        'gradeable': gradeable,
        'outcome': outcome,
        'leaks_count': len(leaks),
        'leaks': leaks,
        'flags_count': len(flags),
        'flags': flags,
        'exempt': is_exempt,
        'exemption_record': {
            'figure_id': fid,
            'reason_code': exemption.get('reason_code'),
            'reason_lv': exemption.get('reason_lv'),
            'exempted_values': exemption.get('exempted_values'),
            'matched_hits_count': len(exempted_hits),
        } if is_exempt else None,
        'errors': errors,
    }


def scan_figures_dataset(
    repo_root: Path = DEST,
    figures_paths: list[Path] | None = None,
    figures_list: list[dict[str, Any]] | None = None,
    terms_path: Path | None = None,
    golden_vectors_path: Path | None = None,
    examples_path: Path | None = None,
    extra_targets_by_figure: dict[str, list[dict[str, Any]]] | None = None,
    rendered_svgs: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Scan all figures across T1-2 and T2-3 (or supplied records) and N08 recall layers."""
    terms_data = load_json(terms_path or (repo_root / TERMS_PATH))
    grammar = terms_data.get('unit_grammar') or {}
    terms_by_key = {e['key']: e for e in terms_data.get('terms', [])}
    gv_data = load_json(golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH))
    ex_data = load_json(examples_path or (repo_root / EXAMPLES_PATH))

    if figures_list is not None:
        all_figures = list(figures_list)
    else:
        paths = figures_paths or [
            p for p in (repo_root / FIGURES_T12_PATH, repo_root / FIGURES_T23_PATH, repo_root / FIGURES_T4_PATH,
                        repo_root / FIGURES_T5_PATH, repo_root / FIGURES_T67_PATH) if p.exists()
        ]
        all_figures = []
        for p in paths:
            all_figures.extend(load_json(p).get('figures', []))

    svg_map = rendered_svgs if rendered_svgs is not None else _render_figures_with_node(all_figures, repo_root)

    # Family-level answer targets from golden vectors + examples
    fam_tokens = extract_family_answer_tokens(gv_data, ex_data)

    results: list[dict[str, Any]] = []
    exemptions_audit: list[dict[str, Any]] = []
    all_flags: list[dict[str, Any]] = []
    errors: list[str] = []

    for rec in all_figures:
        fid = rec.get('id', '?')
        targets: list[dict[str, Any]] = list(rec.get('answer_targets') or [])
        if extra_targets_by_figure and fid in extra_targets_by_figure:
            targets.extend(extra_targets_by_figure[fid])

        # For gradeable figures, also include golden-vector targets for any declared family_id
        seen_fams = {t.get('family_id') for t in targets if t.get('family_id')}
        for fam_id in sorted(seen_fams):
            if fam_id in fam_tokens:
                for ft in fam_tokens[fam_id]:
                    if ft.get('value') is not None and ft.get('unit'):
                        targets.append({'value': ft['value'], 'unit': ft['unit'], 'source': ft['source']})

        res = scan_figure_record(
            rec,
            targets,
            terms_by_key,
            grammar,
            rendered_svg=svg_map.get(fid, ''),
        )
        results.append(res)
        errors.extend(res['errors'])
        all_flags.extend(res['flags'])
        if res['exemption_record']:
            exemptions_audit.append(res['exemption_record'])

    # Also run unified engine over N08 recall layers (B.1.3 convergence check)
    n08_findings: list[dict[str, Any]] = []
    layers_p = repo_root / RECALL_LAYERS_PATH
    if layers_p.exists():
        layers_data = load_json(layers_p)
        for fam in layers_data.get('families', []):
            if fam.get('status') != 'authored':
                continue
            fid = fam['family_id']
            ftoks = fam_tokens.get(fid, [])
            for layer in fam.get('layers', []):
                lf = scan_text_for_leaks(fid, layer.get('layer'), layer.get('text_lv', ''), ftoks, surface='n08_data', grammar=grammar)
                n08_findings.extend(lf)
                for item in lf:
                    errors.append(f"N08:{fid} L{layer.get('layer')}: [E_LEAK_DETECTED] {item['leaked_raw']!r}")

    return {
        'schema_version': 1,
        'task': 'N12',
        'engine': 'unified_leak_scan_v1',
        'status': 'PASS' if not errors else 'FAIL',
        'rules': {
            'significance_rule': {'id': SIGNIFICANCE_RULE_ID, 'verbatim': SIGNIFICANCE_RULE_VERBATIM},
            'borderline_rule': {'id': BORDERLINE_RULE_ID, 'verbatim': BORDERLINE_RULE_VERBATIM},
            'exemption_rule': {'id': EXEMPTION_RULE_ID, 'verbatim': EXEMPTION_RULE_VERBATIM},
        },
        'figures_scanned': len(all_figures),
        'gradeable_figures': sum(1 for r in results if r['gradeable']),
        'exempt_figures': len(exemptions_audit),
        'flags_count': len(all_flags),
        'n08_convergence_leaks': len(n08_findings),
        'exemptions_audit': exemptions_audit,
        'flags': all_flags,
        'figure_results': results,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    return (
        f"leak_scan {report['status']}: figures={report['figures_scanned']} "
        f"(gradeable={report['gradeable_figures']}, exempt={report['exempt_figures']}), "
        f"flags={report['flags_count']}, n08_leaks={report['n08_convergence_leaks']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figures', type=Path, action='append', default=[])
    parser.add_argument('--report', type=Path, default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    paths = args.figures if args.figures else None
    report = scan_figures_dataset(figures_paths=paths)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_summary(report))
        for err in report['errors'][:15]:
            print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
