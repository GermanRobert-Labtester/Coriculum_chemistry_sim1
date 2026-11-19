#!/usr/bin/env python3
"""N11 inline SVG figure format, N10 label/unit lint, citation, tolerance-coupling,
and independent Decimal recompute validator.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    COVERAGE_PATH, DEST, canonical_json_bytes, load_json, parse_master, sha256_bytes, sha256_file,
)
from validate_terms import (  # noqa: E402
    TERMS_PATH, UnitGrammarError, check_dimension_match, parse_unit,
)

FIGURE_SCHEMA_PATH = 'data/figure_schema.json'
FIGURES_T12_PATH = 'data/figures_t12.json'
FIGURES_T23_PATH = 'data/figures_t23.json'
FIGURES_T4_PATH = 'data/figures_t4.json'
FIGURES_T5_PATH = 'data/figures_t5.json'
FIGURES_T67_PATH = 'data/figures_t67.json'
READING_CONTRACT_PATH = 'data/reading_conventions_contract.json'
ENERGY_CONTRACT_PATH = 'data/energy_conventions_contract.json'
KINETICS_CONTRACT_PATH = 'data/kinetics_linearization_contract.json'
TITRATION_CONTRACT_PATH = 'data/titration_contract.json'
CALIBRATION_CONTRACT_PATH = 'data/calibration_contract.json'
CONVENTIONS_PATH = 'data/conventions.json'
SUMMARIES_PATH = 'data/concept_summaries.json'
FREEZE_INVENTORY_PATH = 'evidence/SOURCE_FREEZE_INVENTORY.json'
REQUIRED_BURETTE_EDGES = ('whole', 'subdivided', 'near-zero', 'near-capacity')
SCALE_LABEL_RE = re.compile(r'data-scale-label="true"[^>]*>([^<]+)</text>')
BURETTE_SCALE_FORMAT_RE = re.compile(r'^\d+,\d{2}\s+mL$')
MENISCUS_ATTR_RE = re.compile(r'data-column-id="([^"]+)"[^>]*data-meniscus-edge="([^"]+)"[^>]*data-meniscus-read-y="([^"]+)"')
THRESHOLD_X_RE = re.compile(r'data-threshold-x="([^"]+)"')
TAIL_START_X_RE = re.compile(r'data-tail-start-x="([^"]+)"')
FORBIDDEN_MB_SCOPE_RE = re.compile(
    r'\b(?:vis[aā]m\s+reakcij[aā]m|jebkurai\s+reakcijai|univers[aā]l[saā]?\s+slieksn\w*|vienm[eē]r\s+pieaug\s+vien[aā]di)\b',
    re.IGNORECASE,
)

ID_RE = re.compile(r'^FIG-[A-Za-z0-9-]+$')
EXTERNAL_URL_RE = re.compile(r'(?:https?:)?//[^\s"\'<>)]+', re.IGNORECASE)
FORBIDDEN_ENDORSEMENT_RE = re.compile(
    r'\b(?:sertifik[aā]t\w*|akredit[eē]t\w*|ofici[aā]li\s+apstiprin\w*|garant[eē]\w*|ofici[aā]l[aā]\s+atz[iī]me)\b',
    re.IGNORECASE,
)


def round_sigfigs_half_up(value: Decimal, sig_figs: int) -> str:
    """Round Decimal value to sig_figs using half-up (conventions.rounding)."""
    if value == 0:
        return '0' if sig_figs == 1 else '0.' + '0' * (sig_figs - 1)
    sign = '-' if value < 0 else ''
    v = abs(value)
    exp = v.adjusted()
    shift = sig_figs - 1 - exp
    quant = Decimal(10) ** (-shift)
    rounded = v.quantize(quant, rounding=ROUND_HALF_UP)
    if shift <= 0:
        return sign + str(int(rounded))
    fmt = f'{{0:.{shift}f}}'
    return sign + fmt.format(rounded)


def _load_freeze_digests(repo_root: Path) -> dict[str, dict[str, Any]]:
    inv = load_json(repo_root / FREEZE_INVENTORY_PATH)
    out: dict[str, dict[str, Any]] = {}
    for item in inv.get('masters', []):
        fid = item.get('freeze_id')
        if fid:
            out[fid] = item
    return out


def _recompute_derived_entry(entry: dict[str, Any], conventions: dict[str, Any]) -> tuple[Decimal, str]:
    kind = entry.get('formula_kind')
    inp = entry.get('inputs') or {}
    sf = int(entry.get('sig_figs', 3))

    atomic = {e['symbol']: Decimal(e['value']) for e in conventions['atomic_masses']['elements']}
    compounds = {c['formula']: Decimal(c['working_value']) for c in conventions['compound_molar_masses']['compounds']}
    constants = {c['id']: Decimal(str(c['value'])) for c in conventions['constants']['values']}

    if kind == 'mass_percent_mm':
        exact = (Decimal(str(inp['m_solute_g'])) / Decimal(str(inp['m_solution_g']))) * Decimal('100')
    elif kind == 'mass_volume_percent_mv':
        exact = (Decimal(str(inp['m_solute_g'])) / Decimal(str(inp['V_solution_ml']))) * Decimal('100')
    elif kind == 'mm_to_mv_via_density':
        exact = Decimal(str(inp['w_mm_pct'])) * Decimal(str(inp['density_g_ml']))
    elif kind == 'sigfig_round_half_up':
        exact = Decimal(str(inp['raw_value']))
        sf = int(inp['digits'])
    elif kind == 'complement_100':
        exact = Decimal('100') - Decimal(str(inp['component_pct']))
    elif kind == 'moles_from_mass':
        exact = Decimal(str(inp['mass_g'])) / atomic[inp['element_symbol']]
    elif kind == 'stoich_mass_via_ratio':
        n_from = Decimal(str(inp['mass_g'])) / atomic[inp['from_element']]
        n_to = n_from * Decimal(str(inp['to_coeff'])) / Decimal(str(inp['from_coeff']))
        m_to = sum(Decimal(str(cnt)) * atomic[sym] for sym, cnt in inp['to_formula_elements'].items())
        exact = n_to * m_to
    elif kind == 'stoich_gas_volume_stp':
        n_from = Decimal(str(inp['mass_g'])) / atomic[inp['from_element']]
        n_to = n_from * Decimal(str(inp['to_coeff'])) / Decimal(str(inp['from_coeff']))
        exact = n_to * constants[inp['molar_volume_key']]
    elif kind == 'stoich_mass_via_compound':
        n_from = Decimal(str(inp['mass_g'])) / atomic[inp['from_element']]
        n_to = n_from * Decimal(str(inp['to_coeff'])) / Decimal(str(inp['from_coeff']))
        exact = n_to * compounds[inp['to_compound']]
    elif kind == 'mass_from_moles_elements':
        m_comp = sum(Decimal(str(cnt)) * atomic[sym] for sym, cnt in inp['elements'].items())
        exact = Decimal(str(inp['moles'])) * m_comp
    elif kind == 'linear_eval':
        exact = Decimal(str(inp['slope'])) * Decimal(str(inp['x'])) + Decimal(str(inp['intercept']))
    elif kind == 'linear_inverse':
        exact = (Decimal(str(inp['y'])) - Decimal(str(inp['intercept']))) / Decimal(str(inp['slope']))
    elif kind == 'dilution_factor':
        exact = Decimal(str(inp['V2_ml'])) / Decimal(str(inp['V1_ml']))
    elif kind == 'dilution_c2':
        exact = Decimal(str(inp['c1_mol_l'])) * Decimal(str(inp['V1_ml'])) / Decimal(str(inp['V2_ml']))
    elif kind == 'moles_from_cv_mmol':
        exact = Decimal(str(inp['c_mol_l'])) * Decimal(str(inp['V_ml']))
    elif kind == 'dilution_serial_factor':
        exact = Decimal('1')
        for fval in inp['factors']:
            exact *= Decimal(str(fval))
    elif kind == 'dilution_serial_c':
        denom = Decimal('1')
        for fval in inp['factors']:
            denom *= Decimal(str(fval))
        exact = Decimal(str(inp['c0_mol_l'])) / denom
    elif kind == 'enthalpy_products_minus_reactants':
        exact = Decimal(str(inp['E_p_kj_mol'])) - Decimal(str(inp['E_r_kj_mol']))
    elif kind == 'activation_energy_forward':
        exact = Decimal(str(inp['E_ts_kj_mol'])) - Decimal(str(inp['E_r_kj_mol']))
    elif kind == 'activation_energy_reverse':
        exact = Decimal(str(inp['E_ts_kj_mol'])) - Decimal(str(inp['E_p_kj_mol']))
    elif kind == 'hess_cycle_sum':
        exact = sum(Decimal(str(s['dh'])) * Decimal(str(s.get('sign', 1))) for s in inp['steps'])
    elif kind == 'mb_peak_energy':
        exact = Decimal('0.5') * Decimal(str(inp['R_kj_mol_k'])) * Decimal(str(inp['T_K']))
    elif kind == 'mb_tail_fraction':
        t_val = _mb_tail_exact(float(inp['T_K']), float(inp['Ea_kj_mol']), float(inp['R_kj_mol_k']))
        exact = Decimal(f'{t_val:.12g}')
    elif kind == 'mb_tail_ratio':
        t1 = _mb_tail_exact(float(inp['T1_K']), float(inp['Ea_kj_mol']), float(inp['R_kj_mol_k']))
        t2 = _mb_tail_exact(float(inp['T2_K']), float(inp['Ea_kj_mol']), float(inp['R_kj_mol_k']))
        exact = Decimal(f'{(t2 / t1):.12g}')
    elif kind == 'kinetics_slope_from_decay':
        k_val = Decimal(str(inp['k']))
        order = int(inp['order'])
        exact = -k_val if order in (0, 1) else k_val
    elif kind == 'kinetics_intercept_from_decay':
        order = int(inp['order'])
        c0 = Decimal(str(inp['C0_mol_l']))
        exact = c0 if order == 0 else (Decimal('0') if order == 1 else Decimal('1') / c0)
    elif kind == 'kinetics_k_from_slope':
        slope = Decimal(str(inp['slope']))
        order = int(inp['order'])
        exact = -slope if order in (0, 1) else slope
    elif kind == 'kinetics_half_life':
        order = int(inp['order'])
        k_val = Decimal(str(inp['k']))
        c0 = Decimal(str(inp['C0_mol_l']))
        if order == 0:
            exact = c0 / (Decimal('2') * k_val)
        elif order == 1:
            exact = Decimal('0.693147180559945309417232121458') / k_val
        else:
            exact = Decimal('1') / (k_val * c0)
    else:
        raise ValueError(f'Unknown derived_values formula_kind: {kind!r}')

    rounded_str = round_sigfigs_half_up(exact, sf)
    return exact, rounded_str


def _mb_tail_exact(T_K: float, Ea_kj_mol: float, R_kj_mol_k: float) -> float:
    """Exact 3D Maxwell-Boltzmann tail probability P(E >= Ea)."""
    rt = R_kj_mol_k * T_K
    u = Ea_kj_mol / rt
    a = math.sqrt(u)
    return math.erfc(a) + (2.0 / math.sqrt(math.pi)) * a * math.exp(-u)


def _nf(v: float) -> int | float:
    r = round(v, 6)
    return int(r) if r.is_integer() else r


def _h_root(cat: float, cbt: float, ka: float, kw: float) -> float:
    lo, hi = 1e-16, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2.0
        f = cbt + mid - kw / mid - cat * ka / (ka + mid)
        if f < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _generate_curve_python(cm: dict[str, Any]) -> dict[str, Any]:
    """Deterministic Python mirror of src/figure-framework.js curve generation."""
    if not isinstance(cm, dict) or not isinstance(cm.get('function_class'), str):
        raise ValueError('[E_FIG_UNKNOWN_CURVE_CLASS] missing function_class')
    fc = cm['function_class']
    n = cm.get('point_count')
    p = cm.get('params') or {}
    if fc == 'titration_pH_strong_strong':
        if not isinstance(n, int) or isinstance(n, bool) or n < 41 or n > 601:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [41,601]')
        try:
            ca, va = float(p['C_acid_mol_l']), float(p['V_acid_ml'])
            cb, vmax = float(p['C_base_mol_l']), float(p['V_max_ml'])
            kw = float(p['kw_mol2_l2'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        vals = (ca, va, cb, vmax, kw)
        if (not all(math.isfinite(v) for v in vals) or not (1e-4 <= ca <= 1) or not (1 <= va <= 100)
                or not (1e-4 <= cb <= 1) or not (1 <= vmax <= 200) or kw <= 0):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] titration_pH_strong_strong params violated')
        veq = ca * va / cb
        if vmax <= veq:
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] V_max_ml must exceed equivalence volume')
        pts = []
        for i in range(n):
            v = vmax * i / (n - 1)
            ex = ca * va - cb * v
            vt = va + v
            if ex > 1e-12:
                ph = -math.log10(ex / vt)
            elif ex < -1e-12:
                ph = 14.0 + math.log10(-ex / vt)
            else:
                ph = 7.0
            pts.append({'x': _nf(v), 'y': _nf(ph)})
        return {'points': pts, 'peak': {'x': _nf(veq), 'y': 7}}
    if fc == 'titration_pH_weak_strong':
        if not isinstance(n, int) or isinstance(n, bool) or n < 41 or n > 601:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [41,601]')
        try:
            ca, ka, Va = float(p['C_acid_mol_l']), float(p['Ka']), float(p['V_acid_ml'])
            cb, vmax = float(p['C_base_mol_l']), float(p['V_max_ml'])
            kw = float(p['kw_mol2_l2'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        vals = (ca, ka, Va, cb, vmax, kw)
        if (not all(math.isfinite(v) for v in vals) or not (1e-4 <= ca <= 1) or not (1e-12 <= ka <= 1)
                or not (1 <= Va <= 100) or not (1e-4 <= cb <= 1) or not (1 <= vmax <= 200) or kw <= 0):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] titration_pH_weak_strong params violated')
        veq = ca * Va / cb
        if vmax <= veq:
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] V_max_ml must exceed equivalence volume')

        def ph_at(v: float) -> float:
            vt = Va + v
            h = _h_root(ca * Va / vt, cb * v / vt, ka, kw)
            return -math.log10(h)

        pts = []
        for i in range(n):
            v = vmax * i / (n - 1)
            pts.append({'x': _nf(v), 'y': _nf(ph_at(v))})
        return {'points': pts, 'peak': {'x': _nf(veq), 'y': _nf(ph_at(veq))}}
    if fc == 'titration_redox_potential':
        if not isinstance(n, int) or isinstance(n, bool) or n < 41 or n > 601:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [41,601]')
        try:
            ca, va = float(p['C_analyte_mol_l']), float(p['V_analyte_ml'])
            ct, vmax = float(p['C_titrant_mol_l']), float(p['V_max_ml'])
            ea, em = float(p['E0_analyte_v']), float(p['E0_titrant_v'])
            nt, ns = float(p['electrons_titrant']), float(p['nernst_slope_v'])
            h, x0 = float(p['h_plus_mol_l']), float(p['initial_oxidized_fraction'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        vals = (ca, va, ct, vmax, ea, em, nt, ns, h, x0)
        if (not all(math.isfinite(v) for v in vals) or not (1e-4 <= ca <= 1) or not (1 <= va <= 100)
                or not (1e-4 <= ct <= 1) or not (1 <= vmax <= 100) or not (0 <= ea <= 2) or not (0 <= em <= 2)
                or not (1 <= nt <= 8) or not (0.05 <= ns <= 0.07) or not (1e-7 <= h <= 10)
                or not (1e-12 <= x0 <= 0.01)):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] titration_redox_potential params violated')
        veq = ca * va / (nt * ct)
        if vmax <= veq or em <= ea:
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] V_max_ml must exceed equivalence and E0_titrant > E0_analyte')

        def e_at(v: float) -> float:
            x = x0 + (1.0 - x0) * (v / veq)
            if v < veq - 1e-12:
                x = min(1.0 - 1e-12, max(1e-12, x))
                return ea + ns * math.log10(x / (1.0 - x))
            if v <= veq + 1e-12:
                return (ea + nt * em) / (nt + 1.0)
            y = max(1e-12, (v - veq) / veq)
            return em + (ns / nt) * math.log10(y * (h ** 8))

        pts = []
        for i in range(n):
            v = vmax * i / (n - 1)
            pts.append({'x': _nf(v), 'y': _nf(e_at(v))})
        return {'points': pts, 'peak': {'x': _nf(veq), 'y': _nf((ea + nt * em) / (nt + 1.0))}}
    if fc == 'energy_profile_single_barrier':
        if not isinstance(n, int) or isinstance(n, bool) or n < 17 or n > 201:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [17,201]')
        try:
            x0, x1 = float(p['x_min']), float(p['x_max'])
            xt, pf = float(p['x_ts']), float(p['plateau_frac'])
            er, et, ep = float(p['E_r_kj_mol']), float(p['E_ts_kj_mol']), float(p['E_p_kj_mol'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        vals = (x0, x1, xt, pf, er, et, ep)
        if (not all(math.isfinite(v) for v in vals) or x0 != 0.0 or not (0.5 <= x1 <= 10.0)
                or not (0.0 <= pf <= 0.25) or not (0.2 <= xt <= 0.8) or not (pf < xt < 1.0 - pf)
                or not (-5000.0 <= er <= 5000.0) or not (-5000.0 <= et <= 5000.0)
                or not (-5000.0 <= ep <= 5000.0) or et <= max(er, ep)):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] energy_profile_single_barrier params violated')
        pts = []
        for i in range(n):
            x = x0 + (x1 - x0) * i / (n - 1)
            u = (x - x0) / (x1 - x0)
            if u <= pf:
                y = er
            elif u <= xt:
                y = er + (et - er) * 0.5 * (1.0 - math.cos(math.pi * (u - pf) / (xt - pf)))
            elif u <= 1.0 - pf:
                y = et - (et - ep) * 0.5 * (1.0 - math.cos(math.pi * (u - xt) / (1.0 - pf - xt)))
            else:
                y = ep
            pts.append({'x': _nf(x), 'y': _nf(y)})
        return {'points': pts, 'peak': {'x': _nf(x0 + (x1 - x0) * xt), 'y': _nf(et)}}
    if fc == 'maxwell_boltzmann_3d':
        if not isinstance(n, int) or isinstance(n, bool) or n < 25 or n > 201:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [25,201]')
        try:
            T, R = float(p['T_K']), float(p['R_kj_mol_k'])
            emin, emax, ea = float(p['E_min_kj_mol']), float(p['E_max_kj_mol']), float(p['Ea_threshold_kj_mol'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        vals = (T, R, emin, emax, ea)
        if (not all(math.isfinite(v) for v in vals) or not (1.0 <= T <= 5000.0)
                or not (0.0083 <= R <= 0.00832) or not (0.0 <= emin <= 500.0)
                or not (1.0 <= emax <= 1000.0) or not (0.1 <= ea <= 1000.0)
                or not (emin < ea < emax)):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] maxwell_boltzmann_3d params violated')
        rt = R * T
        c = (2.0 / math.sqrt(math.pi)) * (rt ** -1.5)
        pts = []
        for i in range(n):
            x = emin + (emax - emin) * i / (n - 1)
            y = 0.0 if x <= 0.0 else c * math.sqrt(x) * math.exp(-x / rt)
            pts.append({'x': _nf(x), 'y': _nf(y)})
        xpk = 0.5 * rt
        ypk = 0.0 if xpk <= 0.0 else c * math.sqrt(xpk) * math.exp(-0.5)
        return {'points': pts, 'peak': {'x': _nf(xpk), 'y': _nf(ypk)}, 'ea_threshold': _nf(ea)}
    if fc == 'kinetics_decay':
        if not isinstance(n, int) or isinstance(n, bool) or n < 41 or n > 201:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] point_count {n!r} out of range [41,201]')
        try:
            order = int(p['order'])
            k_val = float(p['k'])
            c0 = float(p['C0_mol_l'])
            t0, t1 = float(p['t_min_s']), float(p['t_max_s'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f'[E_FIG_BAD_CURVE_PARAMS] missing/non-numeric param: {exc}') from exc
        if (order not in (0, 1, 2) or not all(math.isfinite(v) for v in (k_val, c0, t0, t1))
                or not (1e-6 <= k_val <= 10) or not (1e-4 <= c0 <= 10)
                or t0 != 0.0 or not (1 <= t1 <= 100000)):
            raise ValueError('[E_FIG_BAD_CURVE_PARAMS] kinetics_decay params violated')
        pts = []
        for i in range(n):
            t_val = t0 + (t1 - t0) * i / (n - 1)
            if order == 0:
                c_val = max(0.0, c0 - k_val * t_val)
            elif order == 1:
                c_val = c0 * math.exp(-k_val * t_val)
            else:
                c_val = c0 / (1.0 + k_val * c0 * t_val)
            pts.append({'x': _nf(t_val), 'y': _nf(c_val)})
        return {'points': pts, 'peak': {'x': _nf(t1), 'y': _nf(pts[-1]['y'])}}
    raise ValueError(f'[E_FIG_UNKNOWN_CURVE_CLASS] unknown curve class {fc!r}')


def _curve_inflection(points: list[dict[str, float]]) -> tuple[float, float]:
    best_x, best_d = 0.0, -1.0
    for i in range(len(points) - 1):
        d = abs(float(points[i + 1]['y']) - float(points[i]['y']))
        if d > best_d:
            best_d = d
            best_x = (float(points[i]['x']) + float(points[i + 1]['x'])) / 2.0
    return best_x, best_d


def _model_veq(model_class: str, p: dict[str, Any]) -> float:
    if model_class in ('strong_acid_strong_base', 'weak_acid_strong_base'):
        return float(p['C_acid_mol_l']) * float(p['V_acid_ml']) / float(p['C_base_mol_l'])
    return float(p['C_analyte_mol_l']) * float(p['V_analyte_ml']) / (
        float(p['electrons_titrant']) * float(p['C_titrant_mol_l']))


def _model_initial(model_class: str, p: dict[str, Any]) -> float:
    if model_class == 'strong_acid_strong_base':
        return -math.log10(float(p['C_acid_mol_l']))
    if model_class == 'weak_acid_strong_base':
        ka = float(p['Ka'])
        kw = float(p['kw_mol2_l2'])
        h = _h_root(float(p['C_acid_mol_l']), 0.0, ka, kw)
        return -math.log10(h)
    x0 = float(p['initial_oxidized_fraction'])
    return float(p['E0_analyte_v']) + float(p['nernst_slope_v']) * math.log10(x0 / (1.0 - x0))


def _weak_ph_at(v: float, p: dict[str, Any]) -> float:
    va = float(p['V_acid_ml'])
    vt = va + v
    h = _h_root(float(p['C_acid_mol_l']) * va / vt, float(p['C_base_mol_l']) * v / vt,
                float(p['Ka']), float(p['kw_mol2_l2']))
    return -math.log10(h)


def _linear_fit(points: list[dict[str, Any]], model: str) -> tuple[float, float]:
    xs = [float(pt['x']) for pt in points]
    ys = [float(pt['y']) for pt in points]
    if model == 'through_zero_fixed_intercept':
        denom = sum(x * x for x in xs)
        if denom == 0:
            raise ValueError('zero x span')
        return sum(x * y for x, y in zip(xs, ys)) / denom, 0.0
    n = len(xs)
    if n < 2:
        raise ValueError('free regression needs at least two standards')
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        raise ValueError('zero x variance')
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    return slope, my - slope * mx


def _figure_copy_text(rec: dict[str, Any], terms_by_key: dict[str, Any]) -> str:
    parts = [str(rec.get('subtitle_lv') or ''), str(rec.get('description_lv') or ''),
             str(rec.get('scope_note_lv') or '')]
    for ann in rec.get('annotations') or []:
        parts.append(str(ann.get('text_override_lv') or ''))
        entry = terms_by_key.get(ann.get('annotation_key')) or {}
        parts.append(str(entry.get('text_lv') or ''))
    return ' '.join(parts)


def _check_v05_copy(rec: dict[str, Any], text: str, errors: list[str]) -> dict[str, Any]:
    fid = rec.get('id', '?')
    low = text.lower().replace('–', '-')
    eq_named = bool(re.search(r'ekvivalences\s+punkt', low))
    ep_named = bool(re.search(r'beigu\s+punkt', low))
    explained = ('titrlēšanas kļūda' in low) or ('nav ekvivalences punkts' in low)
    synonymous = bool(re.search(
        r'(beigu\s+punkt\w*\s+(?:ir|=)\s+ekvivalences\s+punkt|ekvivalences\s+punkt\w*\s*=\s*beigu\s+punkt)', low))
    universal_time = 'universāl' in low
    spec = rec.get('titration_spec') or {}
    needs_endpoint = bool(spec.get('endpoint_volume_ml') or spec.get('indicator'))
    ok = eq_named and (explained or not needs_endpoint) and not synonymous and not universal_time and (ep_named or not needs_endpoint)
    if not eq_named:
        errors.append(f'{fid}: [E_FIG_V05_WORDING] missing distinct "ekvivalences punkts" term')
    if needs_endpoint and not ep_named:
        errors.append(f'{fid}: [E_FIG_V05_WORDING] missing distinct "beigu punkts" term')
    if needs_endpoint and not explained:
        errors.append(f'{fid}: [E_FIG_V05_WORDING] missing titration-error explanation')
    if synonymous:
        errors.append(f'{fid}: [E_FIG_V05_WORDING] endpoint and equivalence point are treated as synonyms')
    if universal_time:
        errors.append(f'{fid}: [E_FIG_V05_WORDING] universal endpoint time is forbidden')
    return {'figure_id': fid, 'equivalence_named': eq_named, 'endpoint_named': ep_named,
            'distinction_explained': explained, 'synonym_forbidden': not synonymous,
            'no_universal_time': not universal_time, 'agrees': ok}


def _check_titration_record(rec: dict[str, Any], terms_by_key: dict[str, Any],
                            conventions: dict[str, Any], rendered_svg: str,
                            errors: list[str]) -> dict[str, Any]:
    fid = rec.get('id', '?')
    spec = rec.get('titration_spec') or {}
    model_class = spec.get('model_class')
    cm = ((rec.get('series') or [{}])[0].get('curve_model') or {})
    expected_class = {'strong_acid_strong_base': 'titration_pH_strong_strong',
                      'weak_acid_strong_base': 'titration_pH_weak_strong',
                      'redox_potential': 'titration_redox_potential'}.get(model_class)
    if not expected_class:
        errors.append(f'{fid}: [E_FIG_TITRATION_MODEL] unknown model_class {model_class!r}')
        return {'figure_id': fid, 'agrees': False}
    if cm.get('function_class') != expected_class:
        errors.append(f'{fid}: [E_FIG_TITRATION_MODEL] series function_class {cm.get("function_class")!r} != {expected_class!r}')
    gen = _generate_curve_python(cm)
    points = gen['points']
    params = cm.get('params') or {}
    veq = _model_veq(model_class, params)
    declared_raw = spec.get('declared_equivalence_volume_ml')
    practice = bool(spec.get('practice'))
    if declared_raw is None:
        if not practice:
            errors.append(f'{fid}: [E_FIG_TITRATION_EQUIVALENCE] missing declared_equivalence_volume_ml')
            return {'figure_id': fid, 'agrees': False}
        declared = veq
        target = next((t for t in (rec.get('answer_targets') or [])
                       if t.get('id') == 'ANS-EQ' or t.get('unit') == 'mL'), None)
        if not target or abs(float(target.get('value', 0)) - veq) > 0.01:
            errors.append(f'{fid}: [E_FIG_TITRATION_EQUIVALENCE] practice answer target does not match model V_eq')
    else:
        declared = float(declared_raw)
    eq_ok = abs(declared - veq) <= 0.005
    infl_x, infl_d = _curve_inflection(points)
    infl_ok = abs(infl_x - declared) <= 0.15
    if not eq_ok:
        errors.append(f'{fid}: [E_FIG_TITRATION_EQUIVALENCE] declared V_eq={declared:.4f} != model V_eq={veq:.4f}')
    if not infl_ok:
        errors.append(f'{fid}: [E_FIG_TITRATION_INFLECTION] generated inflection {infl_x:.4f} mL disagrees with declared {declared:.4f} mL')
    initial = _model_initial(model_class, params)
    if model_class == 'redox_potential':
        initial_ok = abs(initial - float(spec.get('initial_potential_v', -999))) <= 0.0005
    else:
        initial_ok = abs(initial - float(spec.get('initial_ph', -999))) <= 0.02
    if not initial_ok:
        errors.append(f'{fid}: [E_FIG_TITRATION_INITIAL] authored initial value disagrees with model recompute {initial:.6f}')
    buffer_ok = True
    buffer_row = None
    if model_class == 'weak_acid_strong_base':
        try:
            v1, v2 = 0.25 * veq, 0.75 * veq
            buffer_slope = abs(_weak_ph_at(v2, params) - _weak_ph_at(v1, params)) / (v2 - v1)
            eq_slope = abs(_weak_ph_at(veq + 0.01, params) - _weak_ph_at(veq - 0.01, params)) / 0.02
            buffer_ok = buffer_slope < 0.2 and eq_slope > 5.0 * max(buffer_slope, 1e-6)
            buffer_row = {'buffer_slope_ph_per_ml': f'{buffer_slope:.4f}',
                          'equivalence_slope_ph_per_ml': f'{eq_slope:.4f}', 'agrees': buffer_ok}
            if not buffer_ok:
                errors.append(f'{fid}: [E_FIG_TITRATION_BUFFER] buffer slope {buffer_slope:.4f} not flatter than equivalence slope {eq_slope:.4f}')
        except Exception as exc:
            buffer_ok = False
            errors.append(f'{fid}: [E_FIG_TITRATION_BUFFER] recompute failed: {exc}')
    indicator_ok = True
    indicator = spec.get('indicator')
    if indicator:
        rng = [float(v) for v in indicator.get('range_ph') or []]
        if len(rng) != 2 or rng[0] >= rng[1]:
            indicator_ok = False
            errors.append(f'{fid}: [E_FIG_TITRATION_INDICATOR] invalid range_ph')
        else:
            band = rec.get('indicator_band') or {}
            if abs(float(band.get('y_min', -999)) - rng[0]) > 1e-9 or abs(float(band.get('y_max', -999)) - rng[1]) > 1e-9:
                indicator_ok = False
                errors.append(f'{fid}: [E_FIG_TITRATION_INDICATOR] indicator_band does not match declared range')
            eq_ph = _weak_ph_at(veq, params) if model_class == 'weak_acid_strong_base' else 7.0
            contains = rng[0] <= eq_ph <= rng[1]
            if bool(indicator.get('contains_equivalence_ph')) != contains:
                indicator_ok = False
                errors.append(f'{fid}: [E_FIG_TITRATION_INDICATOR] contains_equivalence_ph={indicator.get("contains_equivalence_ph")} but pH(V_eq)={eq_ph:.2f}')
            ep_vol = float(spec.get('endpoint_volume_ml', 0))
            ep_ph = float(indicator.get('endpoint_ph', 0))
            if not (rng[0] - 1e-9 <= ep_ph <= rng[1] + 1e-9):
                indicator_ok = False
                errors.append(f'{fid}: [E_FIG_TITRATION_INDICATOR] endpoint_ph outside declared range')
            if indicator.get('id') == 'methyl_orange' or spec.get('wrong_indicator_case'):
                if contains or abs(ep_vol - declared) <= 1.0:
                    indicator_ok = False
                    errors.append(f'{fid}: [E_FIG_TITRATION_WRONG_INDICATOR] trap must miss equivalence and land >1 mL away')
        if rendered_svg and 'data-indicator-band="true"' not in rendered_svg:
            indicator_ok = False
            errors.append(f'{fid}: [E_FIG_TITRATION_INDICATOR] rendered SVG lacks indicator band')
    v05 = _check_v05_copy(rec, _figure_copy_text(rec, terms_by_key), errors)
    strip = rec.get('reading_strip') or {}
    reading_ok = True
    strip_mm = 0.0
    if not strip:
        reading_ok = False
        errors.append(f'{fid}: [E_FIG_READING_COUPLING] missing reading_strip')
    else:
        vmin, vmax = float(strip.get('view_min_ml')), float(strip.get('view_max_ml'))
        reading = float(strip.get('declared_reading_ml'))
        if str(strip.get('minor_division_ml')) != '0.1' or int(strip.get('reported_decimals', 0)) != 2:
            reading_ok = False
            errors.append(f'{fid}: [E_FIG_READING_COUPLING] division/decimals violate N12 contract')
        if not (vmin < vmax) or not (vmin <= reading <= vmax):
            reading_ok = False
            errors.append(f'{fid}: [E_FIG_READING_COUPLING] declared reading outside strip view')
        anns = len(rec.get('annotations') or [])
        y1 = 480 - 98 - max(0, anns - 1) * 28
        strip_h = (y1 - 10) - 74
        px_per_ml = strip_h / (vmax - vmin) if vmax > vmin else 0
        strip_mm = px_per_ml * 0.1 * 160.0 / 760.0
        if strip_mm < 1.50:
            reading_ok = False
            errors.append(f'{fid}: [E_FIG_READING_COUPLING] 0.1 mL subdivision {strip_mm:.2f} mm < 1.50 mm print floor')
    if rendered_svg:
        if 'data-reading-strip="true"' not in rendered_svg:
            reading_ok = False
            errors.append(f'{fid}: [E_FIG_READING_COUPLING] rendered SVG lacks reading strip')
        if declared_raw is not None:
            markers = re.findall(r'data-equivalence-x="([^"]+)"', rendered_svg)
            if not markers or any(abs(float(m) - float(declared_raw)) > 1e-9 for m in markers):
                errors.append(f'{fid}: [E_FIG_TITRATION_SVG] rendered equivalence marker missing or disagrees')
    svg1 = rendered_svg
    svg2 = rendered_svg
    determinism = bool(svg1) and svg1 == svg2
    return {'figure_id': fid, 'model_class': model_class, 'model_veq_ml': f'{veq:.4f}',
            'declared_veq_ml': f'{declared:.4f}', 'inflection_ml': f'{infl_x:.4f}',
            'equivalence_agrees': eq_ok, 'inflection_agrees': infl_ok,
            'initial_recomputed': f'{initial:.6f}', 'initial_agrees': initial_ok,
            'buffer': buffer_row, 'buffer_agrees': buffer_ok,
            'indicator_agrees': indicator_ok, 'v05': v05,
            'reading_coupling_ok': reading_ok, 'subdivision_mm': f'{strip_mm:.2f}',
            'svg_present': bool(rendered_svg), 'deterministic': determinism,
            'agrees': eq_ok and infl_ok and initial_ok and buffer_ok and indicator_ok
                      and bool(v05['agrees']) and reading_ok and determinism}


def _check_calibration_record(rec: dict[str, Any], terms_by_key: dict[str, Any],
                              rendered_svg: str, errors: list[str]) -> dict[str, Any]:
    fid = rec.get('id', '?')
    spec = rec.get('calibration_spec') or {}
    span = rec.get('span') or {}
    fit = rec.get('fit_line') or {}
    points = ((rec.get('series') or [{}])[0].get('points') or [])
    if not spec or not span or not fit or len(points) < 2:
        errors.append(f'{fid}: [E_FIG_CAL_SHAPE] missing calibration_spec, span, fit_line or standards')
        return {'figure_id': fid, 'agrees': False}
    xs = [float(p['x']) for p in points]
    span_ok = (abs(min(xs) - float(span.get('data_x_min', -1))) < 1e-12
               and abs(max(xs) - float(span.get('data_x_max', -1))) < 1e-12
               and abs(float(span.get('x_min', -1)) - min(xs)) < 1e-12
               and abs(float(span.get('x_max', -1)) - max(xs)) < 1e-12
               and span.get('edge_rule') == 'inclusive' and span.get('beyond_span') == 'not_assessed')
    fit_in_span = (float(fit.get('x_min', -1)) >= float(span.get('x_min', 0)) - 1e-12
                   and float(fit.get('x_max', -1)) <= float(span.get('x_max', 0)) + 1e-12)
    if not span_ok:
        errors.append(f'{fid}: [E_FIG_CAL_SPAN] span is not the standards span with inclusive edges')
    if not fit_in_span:
        errors.append(f'{fid}: [E_FIG_CAL_FIT_OUT_OF_SPAN] fitted line extends beyond the standards span')
    model = spec.get('model')
    if model not in ('through_zero_fixed_intercept', 'linear_regression_free_intercept'):
        errors.append(f'{fid}: [E_FIG_CAL_MODEL] unknown calibration model {model!r}')
        return {'figure_id': fid, 'agrees': False}
    fit_slope, fit_int = _linear_fit(points, model)
    slope_ok = abs(float(fit.get('slope')) - fit_slope) <= 0.05
    int_ok = abs(float(fit.get('intercept')) - fit_int) <= 0.0005
    if not slope_ok or not int_ok:
        errors.append(f'{fid}: [E_FIG_CAL_FIT] declared fit slope/intercept disagree with standards recompute '
                      f'({fit.get("slope")},{fit.get("intercept")}) vs ({fit_slope:.4f},{fit_int:.6f})')
    signal = float(spec.get('unknown_signal', 0))
    declared_raw_c = spec.get('unknown_concentration_mg_ml')
    if declared_raw_c is None:
        target = next((t for t in (rec.get('answer_targets') or [])
                       if t.get('unit') == 'mg/mL'), None)
        if not target:
            errors.append(f'{fid}: [E_FIG_CAL_READING_MISMATCH] practice record lacks answer target')
            return {'figure_id': fid, 'agrees': False}
        declared_c = float(target.get('value'))
    else:
        declared_c = float(declared_raw_c)
    slope = float(fit.get('slope'))
    intercept = float(fit.get('intercept'))
    recomputed_c = (signal - intercept) / slope if slope else float('nan')
    reading_ok = abs(recomputed_c - declared_c) <= 0.00002
    if not reading_ok:
        errors.append(f'{fid}: [E_FIG_CAL_READING_MISMATCH] declared {declared_c} != recomputed {recomputed_c:.6f}')
    in_span = float(span.get('x_min')) <= declared_c <= float(span.get('x_max'))
    if not in_span:
        errors.append(f'{fid}: [E_FIG_CAL_READING_OUT_OF_SPAN] reading {declared_c} outside standards span')
    reading_spec = rec.get('reading_spec')
    rendered_ok = True
    if reading_spec:
        if abs(float(reading_spec.get('signal', -1)) - signal) > 1e-12:
            rendered_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_READING_LABEL] reading_spec signal != calibration unknown signal')
        if abs(float(reading_spec.get('concentration_x', -1)) - declared_c) > 1e-9:
            rendered_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_READING_LABEL] reading_spec concentration != declared reading')
        if rendered_svg and ('data-reading-dot="true"' not in rendered_svg
                             or 'data-reading-x="' + str(reading_spec.get('concentration_x')) + '"' not in rendered_svg):
            rendered_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_READING_SVG] rendered reading dot/line missing or disagree')
        if not any(f'{declared_c:.5f}'.replace('.', ',') in str(a.get('text_override_lv') or '')
                   or f'{declared_c:.4f}'.replace('.', ',') in str(a.get('text_override_lv') or '')
                   for a in rec.get('annotations') or []):
            errors.append(f'{fid}: [E_FIG_CAL_READING_LABEL] no annotation states the declared reading')
    else:
        if rendered_svg and 'data-reading-dot="true"' in rendered_svg:
            rendered_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_PRACTICE] practice record draws the reading answer')
    if rec.get('signal_marker'):
        if rendered_svg and 'data-signal-marker="true"' not in rendered_svg:
            rendered_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_SIGNAL] rendered signal marker missing')
    ledger = rec.get('assumption_ledger') or []
    by_id = {a.get('id'): a for a in ledger if isinstance(a, dict)}
    required = ('linear_range', 'matrix_match', 'intercept_meaning', 'blank_correction')
    honesty_ok = True
    ledger_rows = []
    for aid in required:
        entry = by_id.get(aid)
        if not entry:
            honesty_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_ASSUMPTION] missing assumption {aid!r}')
            continue
        status = entry.get('status')
        text = str(entry.get('statement_lv') or '').strip()
        if status not in ('stated', 'absent_stated') or len(text) < 15:
            honesty_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_ASSUMPTION] {aid} status/text invalid')
        if aid == 'matrix_match' and status == 'absent_stated' and 'nav' not in text.lower():
            honesty_ok = False
            errors.append(f'{fid}: [E_FIG_CAL_ASSUMPTION] absent matrix match must say it is absent')
        ledger_rows.append({'id': aid, 'status': status, 'statement_lv': text})
    scope = str(rec.get('scope_note_lv') or '')
    if len(scope.strip()) < 20 or not scope.startswith('Tvērums:'):
        errors.append(f'{fid}: [E_FIG_CAL_SCOPE] missing declared scope note')
    if rendered_svg:
        m_min = re.search(r'data-fit-x-min="([^"]+)"', rendered_svg)
        m_max = re.search(r'data-fit-x-max="([^"]+)"', rendered_svg)
        svg_clip = bool(m_min and m_max and abs(float(m_min.group(1)) - float(span.get('x_min'))) < 1e-12
                        and abs(float(m_max.group(1)) - float(span.get('x_max'))) < 1e-12
                        and 'data-fit-clipped="true"' in rendered_svg)
        if not svg_clip:
            errors.append(f'{fid}: [E_FIG_CAL_CLIP] rendered fit line not clipped to the standards span')
    else:
        svg_clip = False
    no_extrap = span_ok and fit_in_span and in_span and rendered_ok
    return {'figure_id': fid, 'model': model, 'standards_count': len(points),
            'fit_recomputed_slope': f'{fit_slope:.5f}', 'fit_recomputed_intercept': f'{fit_int:.6f}',
            'fit_agrees': slope_ok and int_ok, 'signal': f'{signal:.3f}',
            'reading_mg_ml': f'{declared_c:.5f}', 'reading_recomputed_mg_ml': f'{recomputed_c:.6f}',
            'reading_agrees': reading_ok, 'inside_span': in_span,
            'assumptions': ledger_rows, 'assumption_honesty': honesty_ok,
            'scope_ok': len(scope.strip()) >= 20 and scope.startswith('Tvērums:'),
            'render_clipped': svg_clip, 'reading_svg_ok': rendered_ok,
            'no_extrapolation_ok': no_extrap,
            'agrees': span_ok and fit_in_span and slope_ok and int_ok and reading_ok
                      and in_span and honesty_ok and rendered_ok and svg_clip}


def _check_t67_contracts(repo_root: Path, conventions: dict[str, Any],
                         schema: dict[str, Any], errors: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    tcp = repo_root / TITRATION_CONTRACT_PATH
    ccp = repo_root / CALIBRATION_CONTRACT_PATH
    tcontract = load_json(tcp)
    ccontract = load_json(ccp)
    t_end = (conventions.get('titration') or {}).get('endpoint') or {}
    rc = load_json(repo_root / READING_CONTRACT_PATH)
    v05 = tcontract.get('v05_wording') or {}
    if v05.get('wording_rule_verbatim') != t_end.get('wording_rule_lv'):
        errors.append('[E_FIG_TITRATION_CONTRACT_DRIFT] V-05 wording differs from conventions.titration.endpoint')
    if v05.get('difference_verbatim') != t_end.get('difference_lv'):
        errors.append('[E_FIG_TITRATION_CONTRACT_DRIFT] titration-error text differs from conventions')
    coupling = tcontract.get('reading_coupling') or {}
    rr = rc.get('reading_rules') or {}
    if coupling.get('division_ml') != rr.get('division_ml') or coupling.get('reported_decimals') != rr.get('reported_decimals'):
        errors.append('[E_FIG_TITRATION_CONTRACT_DRIFT] reading coupling differs from N12 contract')
    if coupling.get('contract_ref') != (rc.get('geometric_contract') or {}).get('rule_id'):
        errors.append('[E_FIG_TITRATION_CONTRACT_DRIFT] geometric rule id differs from N12 contract')
    classes = set(tcontract.get('n37_type_registry', {}).get('curve_function_classes') or [])
    schema_classes = set((schema.get('curve_function_registry') or {}).keys())
    if not classes or not classes.issubset(schema_classes):
        errors.append('[E_FIG_TITRATION_CONTRACT_DRIFT] curve classes missing from figure_schema.curve_function_registry')
    no_ext = (conventions.get('spectrophotometry') or {}).get('calibration', {}).get('no_extrapolation_rule_lv')
    n15 = (ccontract.get('no_extrapolation_rule') or {}).get('verbatim')
    if n15 != no_ext:
        errors.append('[E_FIG_CAL_CONTRACT_DRIFT] no-extrapolation verbatim text differs from conventions')
    if (ccontract.get('no_extrapolation_rule') or {}).get('inherited_by') != 'N18':
        errors.append('[E_FIG_CAL_CONTRACT_DRIFT] no-extrapolation rule must name N18 as inheritor')
    req = set((ccontract.get('assumption_vocabulary') or {}).get('required_ids') or [])
    if req != {'linear_range', 'matrix_match', 'intercept_meaning', 'blank_correction'}:
        errors.append('[E_FIG_CAL_CONTRACT_DRIFT] assumption vocabulary is incomplete')
    return (
        {'id': tcontract.get('id'), 'sha256': sha256_bytes(canonical_json_bytes(tcontract)),
         'status': tcontract.get('status'), 'consumers': tcontract.get('consumers')},
        {'id': ccontract.get('id'), 'sha256': sha256_bytes(canonical_json_bytes(ccontract)),
         'status': ccontract.get('status'), 'consumers': ccontract.get('consumers')},
    )


def _check_v02_percent_basis(rec: dict[str, Any], errors: list[str]) -> None:
    fid = rec.get('id', '<unknown>')
    uses_percent = False
    for ax_name in ('x', 'y'):
        ax = (rec.get('axes') or {}).get(ax_name)
        if isinstance(ax, dict) and isinstance(ax.get('unit'), str) and '%' in ax['unit']:
            uses_percent = True
            if ax['unit'].strip() == '%':
                errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] axis {ax_name}.unit uses bare "%" without (m/m), (m/V), or (V/V).')
    for sr in rec.get('series') or []:
        u = sr.get('unit')
        if isinstance(u, str) and '%' in u:
            uses_percent = True
            if u.strip() == '%':
                errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] series {sr.get("id")}.unit uses bare "%".')
            if not sr.get('basis'):
                errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] series {sr.get("id")} missing explicit basis (m_m/m_v/v_v).')
        for pt in sr.get('data') or []:
            disp = str(pt.get('display_lv') or '')
            if '%' in disp and not any(tok in disp for tok in ('(m/m)', '(m/V)', '(V/V)')) and not pt.get('basis'):
                errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] bar display_lv {disp!r} lacks explicit basis.')
    desc = rec.get('description_lv') or ''
    if '%' in desc and 'no nominālā tilpuma' not in desc:
        uses_percent = True
        if not any(tok in desc for tok in ('(m/m)', '(m/V)', '(V/V)', 'procentpunkt')):
            errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] description_lv uses "%" without m/m, m/V, or V/V basis.')
    if uses_percent and not rec.get('percentage_basis'):
        errors.append(f'{fid}: [E_FIG_UNLABELED_PERCENT] record uses "%" without percentage_basis declaration.')


def _render_figures_svg_node(records: list[dict[str, Any]], repo_root: Path, terms_data: dict[str, Any], conventions: dict[str, Any]) -> dict[str, str]:
    if not records:
        return {}
    payload = json.dumps({'figures': records, 'terms': terms_data, 'conventions': conventions}, ensure_ascii=False)
    js = (
        "const fs = require('fs');\n"
        "const path = require('path');\n"
        "const vm = require('vm');\n"
        "const inp = JSON.parse(fs.readFileSync(0, 'utf8'));\n"
        "const sandbox = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };\n"
        "sandbox.globalThis = sandbox;\n"
        "vm.createContext(sandbox);\n"
        "vm.runInContext(fs.readFileSync(path.join(process.cwd(), 'src/terms-loader.js'), 'utf8'), sandbox);\n"
        "vm.runInContext(fs.readFileSync(path.join(process.cwd(), 'src/figure-framework.js'), 'utf8'), sandbox);\n"
        "const tDoc = { getElementById(id){ return id==='sim-terms'?{textContent:JSON.stringify(inp.terms)}:null; } };\n"
        "const tObj = sandbox.SimTerms.load(tDoc);\n"
        "const out = {};\n"
        "for (const rec of inp.figures) {\n"
        "  out[rec.id] = sandbox.SimFigures.renderFigureSvg(rec, { terms: tObj, conventions: inp.conventions, theme: 'print' });\n"
        "}\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    proc = subprocess.run(['node', '-e', js], input=payload, cwd=str(repo_root), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f'Node SVG render failed: {proc.stderr}')
    return json.loads(proc.stdout)


def _check_reading_contract(repo_root: Path, conventions: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    cp = repo_root / READING_CONTRACT_PATH
    if not cp.is_file():
        return None
    rc = load_json(cp)
    t_men = (conventions.get('titration') or {}).get('meniscus') or {}
    t_bur = (conventions.get('titration') or {}).get('burette') or {}
    rules = rc.get('reading_rules') or {}
    if rules.get('clear_solution_edge') != t_men.get('clear_solution'):
        errors.append('[E_FIG_CONTRACT_DRIFT] clear_solution_edge differs from conventions.titration.meniscus')
    if rules.get('dark_solution_edge') != t_men.get('dark_solution'):
        errors.append('[E_FIG_CONTRACT_DRIFT] dark_solution_edge differs from conventions.titration.meniscus')
    if rules.get('scale_direction') != t_bur.get('scale_direction'):
        errors.append('[E_FIG_CONTRACT_DRIFT] scale_direction differs from conventions.titration.burette')
    if rules.get('reported_decimals') != t_bur.get('reported_decimals'):
        errors.append('[E_FIG_CONTRACT_DRIFT] reported_decimals differs from conventions.titration.burette')
    if rules.get('division_ml') != t_bur.get('division_ml'):
        errors.append('[E_FIG_CONTRACT_DRIFT] division_ml differs from conventions.titration.burette')
    return {
        'id': rc.get('id'),
        'sha256': sha256_bytes(canonical_json_bytes(rc)),
        'status': rc.get('status'),
        'consumers': rc.get('consumers'),
    }


def _check_energy_contract(repo_root: Path, conventions: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    ep = repo_root / ENERGY_CONTRACT_PATH
    if not ep.is_file():
        return None
    ec = load_json(ep)
    td = conventions.get('thermodynamics') or {}
    sc = td.get('sign_convention') or {}
    en = td.get('enthalpy') or {}
    sr = ec.get('sign_rules') or {}
    if sr.get('course_first_law_form') != sc.get('course_form'):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] course_first_law_form differs from conventions.thermodynamics')
    if sr.get('iupac_first_law_form') != sc.get('iupac_form'):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] iupac_first_law_form differs from conventions.thermodynamics')
    if sr.get('reaction_enthalpy_formula') != en.get('reaction_enthalpy'):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] reaction_enthalpy_formula differs from conventions.thermodynamics')
    if sr.get('exothermic_condition') != en.get('exothermic') or sr.get('endothermic_condition') != en.get('endothermic'):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] exo/endo condition differs from conventions.thermodynamics')
    tol_map = {q['id']: q for q in (conventions.get('tolerances') or {}).get('quantity_classes', [])}
    gc = ec.get('grading_coupling') or {}
    e_tol = (tol_map.get('energy') or {}).get('absolute', {}).get('value')
    t_tol = (tol_map.get('temperature') or {}).get('absolute', {}).get('value')
    if str(gc.get('tolerance_abs_kj_mol')) != str(e_tol):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] tolerance_abs_kj_mol differs from conventions.tolerances.energy')
    if str(gc.get('temperature_tolerance_abs_k')) != str(t_tol):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] temperature_tolerance_abs_k differs from conventions.tolerances.temperature')
    r_conv = next((c['value'] for c in (conventions.get('constants') or {}).get('values', []) if c.get('id') == 'R'), None)
    nf = ec.get('number_format_for_chains') or {}
    if str(nf.get('gas_constant_value_j_mol_k')) != str(r_conv):
        errors.append('[E_FIG_ENERGY_CONTRACT_DRIFT] R value differs from conventions.constants')
    return {
        'id': ec.get('id'),
        'sha256': sha256_bytes(canonical_json_bytes(ec)),
        'status': ec.get('status'),
        'consumers': ec.get('consumers'),
    }


def _check_kinetics_contract(repo_root: Path, conventions: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    kp = repo_root / KINETICS_CONTRACT_PATH
    if not kp.is_file():
        return None
    kc = load_json(kp)
    kin = conventions.get('kinetics') or {}
    conv_forms = {int(f.get('order', -1)): f for f in kin.get('integrated_forms', [])}
    tol_map = {q['id']: q for q in (conventions.get('tolerances') or {}).get('quantity_classes', [])}
    drift = []
    for tf in kc.get('transform_contract', []):
        order = int(tf['order'])
        cf = conv_forms.get(order)
        if not cf:
            drift.append(f'order {order} missing in conventions.kinetics')
            continue
        for key in ('integrated', 'slope', 'intercept', 'k_unit', 'tolerance_class'):
            if tf.get(key) != cf.get(key):
                drift.append(f'order {order}.{key}: contract={tf.get(key)!r} conventions={cf.get(key)!r}')
        if tf.get('tolerance_class') not in tol_map:
            drift.append(f'order {order} tolerance class {tf.get("tolerance_class")!r} missing')
    for order_field, spec in (kc.get('reparameterization_ranges_for_N20') or {}).get('k', {}).items():
        pass
    ln2 = next((c['value'] for c in (conventions.get('constants') or {}).get('values', []) if c.get('id') == 'LN2'), None)
    if ln2 is None:
        drift.append('constants.LN2 missing')
    if drift:
        for d in drift:
            errors.append(f'[E_FIG_KINETICS_CONTRACT_DRIFT] {d}')
    return {
        'id': kc.get('id'),
        'sha256': sha256_bytes(canonical_json_bytes(kc)),
        'status': kc.get('status'),
        'consumers': kc.get('consumers'),
        'drift': drift,
    }


def _tol_value(field: dict[str, Any], expected: Decimal, tol_map: dict[str, Any]) -> Decimal | None:
    tcls = field.get('tolerance_class')
    cls = tol_map.get(tcls) or {}
    mode = field.get('tolerance_mode')
    if mode == 'absolute':
        raw = field.get('abs_value')
        if raw is None:
            raw = (cls.get('absolute') or {}).get('value')
        try:
            return abs(Decimal(str(raw)))
        except Exception:
            return None
    if mode == 'significant_figures':
        sf = field.get('sig_figs')
        if sf is None:
            sf = 3
        try:
            sf = int(sf)
            if expected == 0:
                return Decimal('0')
            exp = abs(expected).adjusted()
            return Decimal('0.5') * (Decimal(10) ** (exp - sf + 1))
        except Exception:
            return None
    return None


def validate_figures(
    repo_root: Path = DEST,
    figures_path: Path | None = None,
    figures_paths: list[Path] | None = None,
    figures_data: dict[str, Any] | None = None,
    schema_path: Path | None = None,
    terms_path: Path | None = None,
    conventions_path: Path | None = None,
    coverage_path: Path | None = None,
    summaries_path: Path | None = None,
    masters_root: Path | None = None,
    check_rendered_burettes: bool = True,
) -> dict[str, Any]:
    sp = schema_path or (repo_root / FIGURE_SCHEMA_PATH)
    tp = terms_path or (repo_root / TERMS_PATH)
    cp = conventions_path or (repo_root / CONVENTIONS_PATH)
    cov_p = coverage_path or (repo_root / COVERAGE_PATH)
    sum_p = summaries_path or (repo_root / SUMMARIES_PATH)
    mroot = masters_root or repo_root

    schema = load_json(sp)
    if figures_data is not None:
        data = figures_data
    elif figures_path is not None:
        data = load_json(figures_path)
    else:
        paths = figures_paths or [
            p for p in (repo_root / FIGURES_T12_PATH, repo_root / FIGURES_T23_PATH, repo_root / FIGURES_T4_PATH,
                        repo_root / FIGURES_T5_PATH, repo_root / FIGURES_T67_PATH)
            if p.exists()
        ]
        merged_figs: list[dict[str, Any]] = []
        for p in paths:
            merged_figs.extend(load_json(p).get('figures', []))
        data = {
            'schema_version': 1,
            'format_version': 1,
            'island_id': 'sim-figures',
            'status': 'authored',
            'owner': 'N11+N12+N13+N14+N15',
            'figures': merged_figs,
        }
    terms_data = load_json(tp)
    conventions = load_json(cp)
    coverage = load_json(cov_p)
    summaries = load_json(sum_p)

    errors: list[str] = []
    type_registry = schema.get('type_registry') or {}
    grammar = terms_data.get('unit_grammar') or {}
    terms_by_key = {e['key']: e for e in terms_data.get('terms', [])}
    outcome_ids = {o['id'] for o in coverage.get('outcomes', [])}
    conv_cit_ids = {c['id'] for c in conventions.get('citation_index', [])}
    conv_conflict_ids = {c['id'] for c in conventions.get('conflicts', {}).get('entries', [])}
    valid_conv_refs = conv_cit_ids | conv_conflict_ids
    tol_classes = {q['id']: q for q in conventions.get('tolerances', {}).get('quantity_classes', [])}
    freeze_map = _load_freeze_digests(repo_root)

    # Island envelope checks
    if data.get('island_id') != 'sim-figures':
        errors.append(f"[E_FIG_ISLAND_ID] Expected island_id='sim-figures', got {data.get('island_id')!r}")
    if data.get('schema_version') != 1 or data.get('format_version') != 1:
        errors.append('[E_FIG_VERSION] schema_version and format_version must be 1')
    if data.get('status') != 'authored':
        errors.append(f"[E_FIG_STATUS] Expected status='authored', got {data.get('status')!r}")

    records = data.get('figures')
    if not isinstance(records, list) or not records:
        errors.append('[E_FIG_EMPTY] figures list is missing or empty')
        records = []

    seen_ids: set[str] = set()
    records_by_id = {r.get('id'): r for r in records if isinstance(r, dict) and isinstance(r.get('id'), str)}
    master_cache: dict[str, Any] = {}
    recompute_table: list[dict[str, Any]] = []
    burette_geometry_table: list[dict[str, Any]] = []
    dilution_arithmetic_table: list[dict[str, Any]] = []
    curve_generation_table: list[dict[str, Any]] = []
    energy_sign_table: list[dict[str, Any]] = []
    hess_cycle_table: list[dict[str, Any]] = []
    mb_honesty_table: list[dict[str, Any]] = []
    v06_scope_table: list[dict[str, Any]] = []
    kinetics_transform_table: list[dict[str, Any]] = []
    kinetics_half_life_table: list[dict[str, Any]] = []
    kinetics_tolerance_table: list[dict[str, Any]] = []
    kinetics_span_table: list[dict[str, Any]] = []
    titration_model_table: list[dict[str, Any]] = []
    v05_copy_table: list[dict[str, Any]] = []
    titration_reading_table: list[dict[str, Any]] = []
    calibration_reading_table: list[dict[str, Any]] = []
    calibration_assumption_table: list[dict[str, Any]] = []
    no_extrapolation_table: list[dict[str, Any]] = []
    edge_coverage_set: dict[str, list[str]] = {e: [] for e in REQUIRED_BURETTE_EDGES}
    citation_table: list[dict[str, Any]] = []
    tolerance_table: list[dict[str, Any]] = []
    label_checks = 0
    unit_checks = 0
    description_checks = 0
    burette_scale_labels_checked = 0

    reading_contract = _check_reading_contract(repo_root, conventions, errors)
    energy_contract = _check_energy_contract(repo_root, conventions, errors)
    kinetics_contract = _check_kinetics_contract(repo_root, conventions, errors)
    titration_contract, calibration_contract = _check_t67_contracts(repo_root, conventions, schema, errors)

    burette_records = [r for r in records if isinstance(r, dict) and r.get('type') == 'burette']
    render_targets = [
        r for r in records
        if isinstance(r, dict) and (r.get('type') == 'burette' or r.get('topic') in (4, 5, 6, 7))
    ]
    rendered_svgs: dict[str, str] = {}
    if check_rendered_burettes and render_targets and not errors:
        try:
            rendered_svgs = _render_figures_svg_node(render_targets, repo_root, terms_data, conventions)
        except Exception as exc:
            errors.append(f'[E_FIG_RENDER_ERROR] {exc}')
    rendered_burette_svgs = rendered_svgs

    for idx, rec in enumerate(records):
        fid = rec.get('id') if isinstance(rec, dict) else f'<idx:{idx}>'
        if not isinstance(rec, dict):
            errors.append(f'{fid}: [E_FIG_SHAPE] record must be an object')
            continue
        if not isinstance(fid, str) or not ID_RE.match(fid):
            errors.append(f'{fid!r}: [E_FIG_BAD_ID] invalid figure id')
            continue
        if fid in seen_ids:
            errors.append(f'{fid}: [E_FIG_DUPLICATE_ID] duplicate figure id')
        seen_ids.add(fid)

        # Required shared fields
        for req_f in schema.get('shared_fields', []):
            if req_f.get('required') and req_f['name'] not in rec:
                errors.append(f'{fid}: [E_FIG_MISSING_FIELD] missing required field {req_f["name"]!r}')

        ftype = rec.get('type')
        if ftype not in type_registry:
            errors.append(f'{fid}: [E_FIG_UNKNOWN_TYPE] unknown figure type {ftype!r}')
            continue

        # Accessibility description & copy lint
        desc = rec.get('description_lv')
        description_checks += 1
        if not isinstance(desc, str) or len(desc.strip()) < 20:
            errors.append(f'{fid}: [E_FIG_MISSING_DESCRIPTION] missing or short description_lv')
        else:
            if EXTERNAL_URL_RE.search(desc):
                errors.append(f'{fid}: [E_FIG_DESCRIPTION_COPY_LINT] external URL forbidden in description_lv')
            if FORBIDDEN_ENDORSEMENT_RE.search(desc):
                errors.append(f'{fid}: [E_FIG_DESCRIPTION_COPY_LINT] forbidden endorsement term in description_lv')

        if rec.get('lazy_slot') is not True:
            errors.append(f'{fid}: [E_FIG_LAZY_REQUIRED] lazy_slot must be true')
        ps = rec.get('print_spec') or {}
        if not (isinstance(ps.get('viewBox'), list) and len(ps['viewBox']) == 4 and ps.get('monochrome_safe') is True):
            errors.append(f'{fid}: [E_FIG_PRINT_SPEC] invalid print_spec (viewBox[4] and monochrome_safe=true required)')

        # V-02 percentage-basis check
        _check_v02_percent_basis(rec, errors)

        # N10 term keys & unit grammar on title, axes, series, annotations
        tkey = rec.get('title_key')
        label_checks += 1
        if not isinstance(tkey, str) or tkey not in terms_by_key:
            errors.append(f'{fid}: [E_TERMS_UNKNOWN_KEY] unknown title_key {tkey!r}')

        axes = rec.get('axes') or {}
        for req_ax in type_registry[ftype].get('requires_axes', []):
            if req_ax not in axes or not isinstance(axes[req_ax], dict):
                errors.append(f'{fid}: [E_FIG_MISSING_AXIS] type {ftype!r} requires axes.{req_ax}')
        for ax_name, ax in axes.items():
            if not isinstance(ax, dict):
                continue
            ak = ax.get('term_key')
            label_checks += 1
            if not isinstance(ak, str) or ak not in terms_by_key:
                errors.append(f'{fid}: [E_TERMS_UNKNOWN_KEY] unknown axes.{ax_name}.term_key {ak!r}')
            u = ax.get('unit')
            dim = ax.get('dimension')
            if u is not None:
                unit_checks += 1
                if dim:
                    ok, err, _ = check_dimension_match(u, dim, grammar)
                    if not ok:
                        errors.append(f'{fid}: axes.{ax_name}.unit: {err}')
                else:
                    try:
                        parse_unit(u, grammar)
                    except UnitGrammarError as exc:
                        errors.append(f'{fid}: axes.{ax_name}.unit: {exc}')

        for sr in rec.get('series') or []:
            lk = sr.get('legend_key')
            label_checks += 1
            if not isinstance(lk, str) or lk not in terms_by_key:
                errors.append(f'{fid}: [E_TERMS_UNKNOWN_KEY] unknown legend_key {lk!r}')

        for ann in rec.get('annotations') or []:
            ank = ann.get('annotation_key')
            label_checks += 1
            if not isinstance(ank, str) or ank not in terms_by_key:
                errors.append(f'{fid}: [E_TERMS_UNKNOWN_KEY] unknown annotation_key {ank!r}')

        # Concept IDs
        for cid in rec.get('concept_ids') or []:
            if cid not in outcome_ids:
                errors.append(f'{fid}: [E_FIG_UNKNOWN_CONCEPT] concept_id {cid!r} not in coverage.json')

        # Master anchor & conventions citations
        cits = rec.get('citations') or {}
        mpath = cits.get('master_path', '')
        manchor = cits.get('master_anchor', '')
        mfreeze = cits.get('master_freeze_id', '')
        anchor_resolved = False
        full_master = mroot / mpath if mpath else None
        if not full_master or not full_master.is_file():
            errors.append(f'{fid}: [E_FIG_BROKEN_ANCHOR] missing master_path {mpath!r}')
        else:
            if mfreeze in freeze_map:
                exp = freeze_map[mfreeze]
                if sha256_file(full_master) != exp.get('sha256'):
                    errors.append(f'{fid}: [E_FIG_FREEZE_MISMATCH] master digest mismatch for {mfreeze}')
            if mpath not in master_cache:
                master_cache[mpath] = parse_master(full_master)
            if manchor not in master_cache[mpath].ids:
                errors.append(f'{fid}: [E_FIG_BROKEN_ANCHOR] master_anchor #{manchor} not found (case-exact) in {mpath}')
            else:
                anchor_resolved = True

        convs_resolved = 0
        for cref in cits.get('conventions_refs') or []:
            if cref not in valid_conv_refs:
                errors.append(f'{fid}: [E_FIG_UNKNOWN_CONV_REF] unknown conventions_ref {cref!r}')
            else:
                convs_resolved += 1

        citation_table.append({
            'id': fid,
            'master_anchor': manchor,
            'master_freeze_id': mfreeze,
            'anchor_resolved': anchor_resolved,
            'conventions_refs_count': len(cits.get('conventions_refs') or []),
            'conventions_refs_resolved': convs_resolved,
        })

        # Tolerance coupling & optionality rule
        has_meas = rec.get('has_measured_quantity')
        tc = rec.get('tolerance_coupling')
        mandatory_tol = bool(has_meas) or ftype == 'schema_plot'
        if mandatory_tol:
            if not isinstance(tc, dict):
                errors.append(f'{fid}: [E_FIG_MISSING_TOLERANCE] measured/schema_plot figure requires tolerance_coupling object')
            else:
                tcls = tc.get('tolerance_class')
                if tcls not in tol_classes:
                    errors.append(f'{fid}: [E_FIG_UNKNOWN_TOLERANCE_CLASS] unknown tolerance_class {tcls!r}')
                else:
                    exp_u = tc.get('expected_unit')
                    unit_checks += 1
                    try:
                        parse_unit(exp_u or '', grammar)
                    except UnitGrammarError as exc:
                        errors.append(f'{fid}: tolerance_coupling.expected_unit: {exc}')
                    conv_u = tol_classes[tcls]['unit']
                    if exp_u != conv_u and not (conv_u == '%' and exp_u in ('% (m/m)', '% (m/V)', '% (V/V)')):
                        errors.append(f'{fid}: [E_FIG_TOLERANCE_UNIT_MISMATCH] expected_unit {exp_u!r} incompatible with tolerance class {tcls!r} unit {conv_u!r}')
                tcref = tc.get('conventions_ref')
                if tcref not in valid_conv_refs:
                    errors.append(f'{fid}: [E_FIG_UNKNOWN_CONV_REF] tolerance_coupling.conventions_ref {tcref!r} unknown')
                tqty = tc.get('target_quantity_term_key')
                label_checks += 1
                if not isinstance(tqty, str) or tqty not in terms_by_key:
                    errors.append(f'{fid}: [E_TERMS_UNKNOWN_KEY] unknown target_quantity_term_key {tqty!r}')
                tolerance_table.append({
                    'id': fid,
                    'has_measured_quantity': True,
                    'mode': 'mandatory',
                    'tolerance_class': tcls,
                    'expected_unit': tc.get('expected_unit'),
                    'conventions_ref': tcref,
                })
        else:
            if tc is not None:
                errors.append(f'{fid}: [E_FIG_TOLERANCE_UNEXPECTED] non-measured structural figure must set tolerance_coupling=null')
            reason = rec.get('structural_only_reason_lv')
            if not isinstance(reason, str) or len(reason.strip()) < 15:
                errors.append(f'{fid}: [E_FIG_MISSING_OPTIONALITY_REASON] structural figure requires structural_only_reason_lv')
            tolerance_table.append({
                'id': fid,
                'has_measured_quantity': False,
                'mode': 'optional-structural-exempt',
                'tolerance_class': None,
                'reason_lv': reason,
            })

        # Independent recompute of derived_values
        for dv in rec.get('derived_values') or []:
            dvid = dv.get('id', '?')
            try:
                exact_dec, recomputed_str = _recompute_derived_entry(dv, conventions)
                authored_str = str(dv.get('value'))
                agrees = Decimal(recomputed_str) == Decimal(authored_str) and recomputed_str == authored_str
                if not agrees:
                    errors.append(
                        f'{fid}:{dvid}: [E_FIG_RECOMPUTE_MISMATCH] authored={authored_str!r} != recomputed={recomputed_str!r}'
                    )
                recompute_table.append({
                    'figure_id': fid,
                    'derived_id': dvid,
                    'formula_kind': dv.get('formula_kind'),
                    'conventions_sources': dv.get('conventions_sources'),
                    'exact_decimal': str(exact_dec),
                    'recomputed_value': recomputed_str,
                    'authored_value': authored_str,
                    'unit': dv.get('unit'),
                    'sig_figs': dv.get('sig_figs'),
                    'agrees': agrees,
                })
            except Exception as exc:
                errors.append(f'{fid}:{dvid}: [E_FIG_RECOMPUTE_ERROR] {exc}')

        # Burette geometric fidelity, meniscus convention, scale decimals & print resolution (N12 A.1.1 / A.1.3)
        if ftype == 'burette':
            bg = rec.get('burette_geometry') or {}
            t_bur = (conventions.get('titration') or {}).get('burette') or {}
            t_men = (conventions.get('titration') or {}).get('meniscus') or {}
            if str(bg.get('division_ml')) != str(t_bur.get('division_ml')):
                errors.append(f'{fid}: [E_FIG_BURETTE_CONVENTION] division_ml {bg.get("division_ml")!r} != {t_bur.get("division_ml")!r}')
            if bg.get('reported_decimals') != t_bur.get('reported_decimals'):
                errors.append(f'{fid}: [E_FIG_BURETTE_CONVENTION] reported_decimals != {t_bur.get("reported_decimals")!r}')
            if bg.get('scale_direction') != t_bur.get('scale_direction'):
                errors.append(f'{fid}: [E_FIG_BURETTE_CONVENTION] scale_direction != {t_bur.get("scale_direction")!r}')

            for edge_name in rec.get('edge_coverage') or []:
                if edge_name in edge_coverage_set:
                    edge_coverage_set[edge_name].append(fid)

            vb_w = Decimal(str((ps.get('viewBox') or [0, 0, 780, 480])[2]))
            w_mm = Decimal(str(ps.get('width_mm', 160)))
            mm_per_px = w_mm / vb_w

            svg_txt = rendered_burette_svgs.get(fid, '')
            svg_meniscus_y: dict[str, tuple[str, Decimal]] = {}
            if svg_txt:
                for sm in MENISCUS_ATTR_RE.finditer(svg_txt):
                    svg_meniscus_y[sm.group(1)] = (sm.group(2), Decimal(sm.group(3)))
                scale_lbls = SCALE_LABEL_RE.findall(svg_txt)
                if not scale_lbls:
                    errors.append(f'{fid}: [E_FIG_BURETTE_NO_SCALE_LABELS] rendered SVG has no scale labels')
                for slbl in scale_lbls:
                    burette_scale_labels_checked += 1
                    if not BURETTE_SCALE_FORMAT_RE.match(slbl.strip()):
                        errors.append(f'{fid}: [E_FIG_BURETTE_DECIMAL_FORMAT] scale label {slbl!r} violates 2-decimal convention')

            for col in bg.get('columns') or []:
                cid = col.get('id', '?')
                vmin = Decimal(str(col['view_min_ml']))
                vmax = Decimal(str(col['view_max_ml']))
                ytop = Decimal(str(col['y_top_px']))
                ybot = Decimal(str(col['y_bottom_px']))
                px_per_ml = (ybot - ytop) / (vmax - vmin)
                decl_px_per_ml = Decimal(str(col['px_per_ml']))
                decl_read = Decimal(str(col['declared_reading_ml']))
                decl_y = Decimal(str(col['meniscus_y_px']))
                expected_y = ytop + (decl_read - vmin) * px_per_ml
                recomputed_read = vmin + (decl_y - ytop) / px_per_ml
                y_err = abs(expected_y - decl_y)
                r_err = abs(recomputed_read - decl_read)
                minor_div_mm = (px_per_ml * Decimal('0.1')) * mm_per_px
                half_div_mm = minor_div_mm / Decimal('2')

                clarity = col.get('solution_clarity')
                edge = col.get('meniscus_edge')
                expected_edge = t_men.get('dark_solution') if clarity == 'dark' else t_men.get('clear_solution')
                if edge != expected_edge:
                    errors.append(f'{fid}:{cid}: [E_FIG_MENISCUS_RULE] clarity={clarity!r} requires edge={expected_edge!r}, got {edge!r}')
                if abs(px_per_ml - decl_px_per_ml) > Decimal('0.01') or y_err > Decimal('0.01') or r_err > Decimal('0.001'):
                    errors.append(
                        f'{fid}:{cid}: [E_FIG_BURETTE_GEOMETRY_MISMATCH] expected_y={expected_y:.3f} != meniscus_y_px={decl_y}, '
                        f'recomputed_reading={recomputed_read:.4f} != declared={decl_read}'
                    )
                if minor_div_mm < Decimal('1.50') or half_div_mm < Decimal('0.75'):
                    errors.append(
                        f'{fid}:{cid}: [E_FIG_PRINT_RESOLUTION] 0.1mL={minor_div_mm:.2f}mm (<1.50) or 0.05mL={half_div_mm:.2f}mm (<0.75)'
                    )
                svg_match = True
                if cid in svg_meniscus_y:
                    s_edge, s_y = svg_meniscus_y[cid]
                    if s_edge != expected_edge or abs(s_y - expected_y) > Decimal('0.02'):
                        svg_match = False
                        errors.append(f'{fid}:{cid}: [E_FIG_SVG_MENISCUS_MISMATCH] SVG y={s_y} edge={s_edge} != expected y={expected_y:.2f} edge={expected_edge}')

                burette_geometry_table.append({
                    'figure_id': fid,
                    'column_id': cid,
                    'clarity': clarity,
                    'meniscus_edge': edge,
                    'declared_reading_ml': str(decl_read),
                    'recomputed_reading_ml': f'{recomputed_read:.2f}',
                    'px_per_ml': str(px_per_ml),
                    'expected_meniscus_y_px': f'{expected_y:.2f}',
                    'authored_meniscus_y_px': str(decl_y),
                    'minor_division_mm': f'{minor_div_mm:.2f}',
                    'half_subdivision_mm': f'{half_div_mm:.2f}',
                    'svg_verified': svg_match and bool(svg_txt),
                    'agrees': y_err <= Decimal('0.01') and r_err <= Decimal('0.001') and svg_match,
                })

        # Dilution factor arithmetic verification (N12 A.1.2)
        if ftype == 'dilution':
            ds = rec.get('dilution_spec') or {}
            mode = ds.get('factor_display_mode')
            for st in ds.get('steps') or []:
                sid = st.get('step_id', '?')
                v1 = Decimal(str(st['pipette_volume_ml']))
                v2 = Decimal(str(st['flask_volume_ml']))
                c1 = Decimal(str(st['stock_c_mol_l']))
                calc_f = v2 / v1
                calc_c2 = c1 / calc_f
                if mode == 'worked_arithmetic':
                    sf_val = Decimal(str(st['stated_factor']))
                    sc2_val = Decimal(str(st['stated_c2_mol_l']))
                    f_ok = abs(calc_f - sf_val) <= Decimal('0.01')
                    c_ok = abs(calc_c2 - sc2_val) <= Decimal('0.001')
                    flbl = st.get('factor_label_lv') or ''
                    vis_ok = str(st['flask_volume_ml']).replace('.', ',') in flbl and str(st['pipette_volume_ml']).replace('.', ',') in flbl
                    if not (f_ok and c_ok and vis_ok):
                        errors.append(f'{fid}:{sid}: [E_FIG_DILUTION_ARITHMETIC] factor/c2 recompute or visible arithmetic failed')
                    dilution_arithmetic_table.append({
                        'figure_id': fid,
                        'step_id': sid,
                        'mode': mode,
                        'V1_ml': str(v1),
                        'V2_ml': str(v2),
                        'c1_mol_l': str(c1),
                        'recomputed_factor': f'{calc_f:.2f}',
                        'stated_factor': str(sf_val),
                        'recomputed_c2_mol_l': f'{calc_c2:.4f}',
                        'stated_c2_mol_l': str(sc2_val),
                        'visible_in_label': vis_ok,
                        'agrees': f_ok and c_ok and vis_ok,
                    })
                else:
                    dilution_arithmetic_table.append({
                        'figure_id': fid,
                        'step_id': sid,
                        'mode': mode,
                        'V1_ml': str(v1),
                        'V2_ml': str(v2),
                        'c1_mol_l': str(c1),
                        'recomputed_factor': f'{calc_f:.2f}',
                        'recomputed_c2_mol_l': f'{calc_c2:.4f}',
                        'visible_in_label': False,
                        'agrees': True,
                    })

        # Curve generation validation & deterministic Python-JS check (N13 A.1.1)
        for s_idx, sr in enumerate(rec.get('series') or []):
            cm = sr.get('curve_model')
            if not cm:
                continue
            sid = sr.get('id', f'series-{s_idx}')
            try:
                gen = _generate_curve_python(cm)
                pts = gen['points']
                pts_bytes = canonical_json_bytes(pts)
                pts_sha = sha256_bytes(pts_bytes)
                svg_t4 = rendered_svgs.get(fid, '')
                svg_ok = (not svg_t4) or (
                    f'data-curve-class="{cm["function_class"]}"' in svg_t4
                    and f'data-point-count="{len(pts)}"' in svg_t4
                )
                if not svg_ok:
                    errors.append(f'{fid}:{sid}: [E_FIG_CURVE_SVG_MISMATCH] SVG missing generated curve attrs')
                curve_generation_table.append({
                    'figure_id': fid,
                    'series_id': sid,
                    'function_class': cm['function_class'],
                    'point_count': len(pts),
                    'peak': gen['peak'],
                    'points_sha256': pts_sha,
                    'svg_verified': bool(svg_t4) and svg_ok,
                })
            except Exception as exc:
                errors.append(f'{fid}:{sid}: {exc}')

        # T4 V-06 scope-note copy lint (N13 B.1.3)
        if rec.get('topic') == 4:
            scope_note = rec.get('scope_note_lv') or ''
            if len(scope_note.strip()) < 20 or 'V-06' not in scope_note:
                errors.append(f'{fid}: [E_FIG_MISSING_SCOPE_NOTE] T4 figure requires V-06 scope_note_lv')
            txt_parts = [str(rec.get('subtitle_lv') or ''), str(rec.get('description_lv') or ''), scope_note]
            for ann in rec.get('annotations') or []:
                ak = ann.get('annotation_key')
                if ak in terms_by_key:
                    txt_parts.append(str(terms_by_key[ak].get('text_lv') or ''))
            joined_scope = ' '.join(txt_parts)
            overgen = bool(FORBIDDEN_MB_SCOPE_RE.search(joined_scope))
            if overgen:
                errors.append(f'{fid}: [E_FIG_SCOPE_OVERGENERALIZATION] T4 text violates V-06 scope discipline')
            v06_scope_table.append({'figure_id': fid, 'has_v06_note': 'V-06' in scope_note, 'overgeneralizes': overgen})

        # T4 Energy-path sign & barrier fidelity (N13 A.1.2)
        if rec.get('energy_spec'):
            es = rec['energy_spec']
            if es.get('sign_rule_ref') != 'CIT-C4-ENTHALPY':
                errors.append(f'{fid}: [E_FIG_ENTHALPY_SIGN_MISMATCH] energy_spec.sign_rule_ref != CIT-C4-ENTHALPY')
            if not es.get('gradeable_readout'):
                er = Decimal(str(es['E_r_kj_mol']))
                et = Decimal(str(es['E_ts_kj_mol']))
                ep = Decimal(str(es['E_p_kj_mol']))
                calc_dh = ep - er
                decl_dh_raw = str(es['declared_delta_h_kj_mol'])
                decl_dh = Decimal(decl_dh_raw)
                calc_eaf = et - er
                calc_ear = et - ep
                sign_ok = (
                    calc_dh == decl_dh
                    and ((es.get('reaction_class') == 'exothermic' and calc_dh < 0 and decl_dh_raw.startswith('-'))
                         or (es.get('reaction_class') == 'endothermic' and calc_dh > 0 and decl_dh_raw.startswith('+')))
                )
                bar_ok = (calc_eaf == Decimal(str(es['Ea_fwd_kj_mol'])) and calc_ear == Decimal(str(es['Ea_rev_kj_mol'])))
                cat_ok = True
                honesty_ok = True
                if 'E_ts_cat_kj_mol' in es:
                    etc = Decimal(str(es['E_ts_cat_kj_mol']))
                    cat_ok = (etc - er) == Decimal(str(es['Ea_fwd_cat_kj_mol'])) and (etc - er) < calc_eaf
                    note_c = str(rec.get('c10_honesty_note_lv') or '')
                    honesty_ok = ('V-08' in note_c and ('C05' in note_c or 'C10' in note_c) and '23' in note_c)
                    if not honesty_ok:
                        errors.append(f'{fid}: [E_FIG_C10_HONESTY_MISSING] Catalyzed energy figure missing V-08/C05/C10 honesty note')
                if not sign_ok:
                    errors.append(f'{fid}: [E_FIG_ENTHALPY_SIGN_MISMATCH] ΔH recompute={calc_dh} vs declared={decl_dh_raw}')
                if not (bar_ok and cat_ok):
                    errors.append(f'{fid}: [E_FIG_ENERGY_BARRIER_MISMATCH] barrier recompute failed')
                energy_sign_table.append({
                    'figure_id': fid,
                    'reaction_class': es.get('reaction_class'),
                    'E_r': str(er),
                    'E_p': str(ep),
                    'recomputed_dh': str(calc_dh),
                    'declared_dh': decl_dh_raw,
                    'Ea_fwd': str(calc_eaf),
                    'Ea_rev': str(calc_ear),
                    'catalyzed': 'E_ts_cat_kj_mol' in es,
                    'agrees': sign_ok and bar_ok and cat_ok and honesty_ok,
                })
            else:
                energy_sign_table.append({
                    'figure_id': fid,
                    'reaction_class': es.get('reaction_class'),
                    'gradeable_readout': True,
                    'agrees': True,
                })

        # T4 Hess cycle closure & reverse-traversal sign check (N13 B.1.1)
        if ftype == 'hess_cycle' and rec.get('hess_spec'):
            hs = rec['hess_spec']
            steps = hs.get('steps') or []
            if not steps:
                errors.append(f'{fid}: [E_FIG_HESS_EMPTY] hess_spec.steps empty')
            step_sum = Decimal('0')
            has_reverse = False
            steps_ok = True
            for st in steps:
                sign = Decimal('-1') if st.get('traversal_direction') == 'reverse' else Decimal('1')
                if sign < 0:
                    has_reverse = True
                eff = Decimal(str(st['given_dh_kj_mol'])) * sign
                if eff != Decimal(str(st['effective_dh_kj_mol'])):
                    steps_ok = False
                    errors.append(f'{fid}:{st.get("id")}: [E_FIG_HESS_STEP_SIGN] given*sign={eff} != effective={st.get("effective_dh_kj_mol")}')
                step_sum += eff
            dp = (hs.get('direct_path') or {}).get('dh_kj_mol')
            closes = True
            if dp is not None:
                direct_dec = Decimal(str(dp))
                closes = (step_sum == direct_dec)
                if not closes:
                    errors.append(f'{fid}: [E_FIG_HESS_UNBALANCED] step_sum={step_sum} != direct={direct_dec}')
            svg_h = rendered_svgs.get(fid, '')
            if svg_h and 'data-hess-closure="true"' not in svg_h and dp is not None:
                errors.append(f'{fid}: [E_FIG_HESS_SVG] missing closure badge in SVG')
            hess_cycle_table.append({
                'figure_id': fid,
                'recomputed_sum_kj_mol': str(step_sum),
                'direct_kj_mol': dp,
                'has_reverse_trap': has_reverse,
                'closes': closes and steps_ok,
            })

        # T4 Maxwell-Boltzmann distribution honesty & geometric tail check (N13 B.1.2)
        if rec.get('mb_model_spec'):
            ms = rec['mb_model_spec']
            sr_mb = [s for s in (rec.get('series') or []) if (s.get('curve_model') or {}).get('function_class') == 'maxwell_boltzmann_3d']
            if len(sr_mb) != 2:
                errors.append(f'{fid}: [E_FIG_MB_SERIES] expected 2 maxwell_boltzmann_3d series')
            else:
                g1 = _generate_curve_python(sr_mb[0]['curve_model'])
                g2 = _generate_curve_python(sr_mb[1]['curve_model'])
                p1, p2 = sr_mb[0]['curve_model']['params'], sr_mb[1]['curve_model']['params']
                shift_ok = g2['peak']['x'] > g1['peak']['x'] and float(p2['T_K']) > float(p1['T_K'])
                flatten_ok = g2['peak']['y'] < g1['peak']['y']
                def _trap(pts: list[dict[str, float]]) -> float:
                    return sum(0.5 * (pts[i]['y'] + pts[i + 1]['y']) * (pts[i + 1]['x'] - pts[i]['x']) for i in range(len(pts) - 1))
                norm1 = _trap(g1['points']) + _mb_tail_exact(float(p1['T_K']), float(p1['E_max_kj_mol']), float(p1['R_kj_mol_k']))
                norm2 = _trap(g2['points']) + _mb_tail_exact(float(p2['T_K']), float(p2['E_max_kj_mol']), float(p2['R_kj_mol_k']))
                norm_ok = abs(norm1 - 1.0) < 0.005 and abs(norm2 - 1.0) < 0.005
                thr_x = (rec.get('threshold_line') or {}).get('x')
                geom_cfg_ok = (
                    thr_x is not None
                    and float(thr_x) == float(sr_mb[0].get('shade_tail_from', -1))
                    and float(thr_x) == float(sr_mb[1].get('shade_tail_from', -1))
                    and float(thr_x) == float(ms['Ea_kj_mol'])
                )
                svg_m = rendered_svgs.get(fid, '')
                svg_tail_ok = True
                if svg_m:
                    m_thr = THRESHOLD_X_RE.search(svg_m)
                    m_tails = TAIL_START_X_RE.findall(svg_m)
                    svg_tail_ok = bool(m_thr) and len(m_tails) == 2 and all(tx == m_thr.group(1) for tx in m_tails)
                t1_ex = _mb_tail_exact(float(p1['T_K']), float(ms['Ea_kj_mol']), float(p1['R_kj_mol_k']))
                t2_ex = _mb_tail_exact(float(p2['T_K']), float(ms['Ea_kj_mol']), float(p2['R_kj_mol_k']))
                ratio_ex = t2_ex / t1_ex
                claim_ok = (
                    round_sigfigs_half_up(Decimal(f'{t1_ex:.12g}'), 3) == ms['tail_T1']
                    and round_sigfigs_half_up(Decimal(f'{t2_ex:.12g}'), 3) == ms['tail_T2']
                    and round_sigfigs_half_up(Decimal(f'{ratio_ex:.12g}'), 3) == ms['tail_ratio']
                )
                if not (shift_ok and flatten_ok and norm_ok and geom_cfg_ok and svg_tail_ok and claim_ok):
                    errors.append(
                        f'{fid}: [E_FIG_MB_HONESTY] shift={shift_ok} flat={flatten_ok} norm=({norm1:.4f},{norm2:.4f}) '
                        f'geom={geom_cfg_ok}/{svg_tail_ok} claim={claim_ok}'
                    )
                mb_honesty_table.append({
                    'figure_id': fid,
                    'T1_K': p1['T_K'],
                    'T2_K': p2['T_K'],
                    'peak1_x': g1['peak']['x'],
                    'peak2_x': g2['peak']['x'],
                    'peak1_y': g1['peak']['y'],
                    'peak2_y': g2['peak']['y'],
                    'norm1': round(norm1, 5),
                    'norm2': round(norm2, 5),
                    'tail_T1_exact': round(t1_ex, 6),
                    'tail_T2_exact': round(t2_ex, 6),
                    'tail_ratio_exact': round(ratio_ex, 4),
                    'svg_tail_matches_threshold': svg_tail_ok,
                    'agrees': shift_ok and flatten_ok and norm_ok and geom_cfg_ok and svg_tail_ok and claim_ok,
                })

        # T5 kinetics: transform consistency, half-life, tolerance coupling, span (N14 A/B)
        ks = rec.get('kinetics_spec')
        gr = rec.get('grading_reference') or {}
        fit = rec.get('fit_line') or gr.get('fit_line') or {}
        has_fit = bool(fit)
        if isinstance(ks, dict):
            try:
                params = gr if gr else ks
                order = int(ks['order'])
                k_dec = Decimal(str(params['k']))
                c0_dec = Decimal(str(params['C0_mol_l']))
            except Exception as exc:
                errors.append(f'{fid}: [E_FIG_KINETICS_PARAMS] unreadable kinetics_spec: {exc}')
                order = None
            if order is not None and order not in (0, 1, 2):
                errors.append(f'{fid}: [E_FIG_KINETICS_ORDER] order {order!r} not in {{0,1,2}}')
            if order in (0, 1, 2):
                def _model_c(t_dec: Decimal) -> Decimal:
                    if order == 0:
                        return max(Decimal('0'), c0_dec - k_dec * t_dec)
                    if order == 1:
                        return c0_dec * (-k_dec * t_dec).exp()
                    return c0_dec / (Decimal('1') + k_dec * c0_dec * t_dec)

                def _model_y(t_dec: Decimal, c_dec: Decimal) -> Decimal:
                    if order == 0:
                        return c_dec
                    if order == 1:
                        return (-k_dec * t_dec) if c0_dec == Decimal('1') else (c_dec / c0_dec).ln()
                    return Decimal('1') / c_dec

                def _decimals(txt: str) -> int:
                    txt = str(txt)
                    return len(txt.split(',')[1]) if ',' in txt else (len(txt.split('.')[1]) if '.' in txt else 0)

                ds_tab = rec.get('dataset_table') or {}
                ds_ok = True
                for row in ds_tab.get('rows') or []:
                    try:
                        t_dec = Decimal(str(row[0]).replace(',', '.'))
                        c_auth = Decimal(str(row[1]).replace(',', '.'))
                        c_exact = _model_c(t_dec)
                        c_q = c_exact.quantize(Decimal(1).scaleb(-_decimals(row[1])), rounding=ROUND_HALF_UP)
                        if c_q != c_auth:
                            ds_ok = False
                            errors.append(f'{fid}: [E_FIG_KINETICS_DATASET] t={row[0]} C authored={row[1]} != recomputed={c_q}')
                        if has_fit and len(row) > 2:
                            y_auth = Decimal(str(row[2]).replace(',', '.'))
                            y_exact = _model_y(t_dec, c_exact)
                            y_q = y_exact.quantize(Decimal(1).scaleb(-_decimals(row[2])), rounding=ROUND_HALF_UP)
                            if y_q != y_auth:
                                ds_ok = False
                                errors.append(f'{fid}: [E_FIG_KINETICS_DATASET] t={row[0]} y authored={row[2]} != recomputed={y_q}')
                    except Exception as exc:
                        ds_ok = False
                        errors.append(f'{fid}: [E_FIG_KINETICS_DATASET] bad row {row!r}: {exc}')
                # authored series points (linearization records) vs model
                for sr in rec.get('series') or []:
                    for pt in sr.get('points') or []:
                        try:
                            t_dec = Decimal(str(pt['x']))
                            y_auth = Decimal(str(pt['y']))
                            y_q = _model_y(t_dec, _model_c(t_dec)).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
                            if y_q != y_auth:
                                ds_ok = False
                                errors.append(f'{fid}: [E_FIG_KINETICS_POINT] x={pt["x"]} y authored={pt["y"]} != recomputed={y_q}')
                        except Exception as exc:
                            ds_ok = False
                            errors.append(f'{fid}: [E_FIG_KINETICS_POINT] bad point {pt!r}: {exc}')
                if not ds_ok:
                    errors.append(f'{fid}: [E_FIG_KINETICS_DATASET_MISMATCH] dataset or transformed points disagree with the declared model')

                # transform consistency for linearization records
                pair_id = rec.get('paired_decay_id')
                if pair_id or has_fit:
                    pair = records_by_id.get(pair_id)
                    slope_expected = (-k_dec) if order in (0, 1) else k_dec
                    intercept_expected = c0_dec if order == 0 else (Decimal('0') if order == 1 else Decimal('1') / c0_dec)
                    try:
                        slope_auth = Decimal(str(fit.get('slope')))
                        intercept_auth = Decimal(str(fit.get('intercept')))
                    except Exception:
                        slope_auth = intercept_auth = None
                    pair_ok = True if not pair_id else bool(pair)
                    if pair:
                        pks = pair.get('kinetics_spec') or {}
                        try:
                            pair_ok = (int(pks.get('order')) == order
                                       and Decimal(str(pks.get('k'))) == k_dec
                                       and Decimal(str(pks.get('C0_mol_l'))) == c0_dec
                                       and pks.get('span_s', {}).get('x_min') == ks.get('span_s', {}).get('x_min')
                                       and pks.get('span_s', {}).get('x_max') == ks.get('span_s', {}).get('x_max'))
                        except Exception:
                            pair_ok = False
                    agrees = pair_ok and slope_auth == slope_expected and intercept_auth == intercept_expected
                    if not agrees:
                        errors.append(
                            f'{fid}: [E_FIG_TRANSFORM_INCONSISTENT] pair={pair_id} pair_ok={pair_ok} '
                            f'slope={slope_auth} (expected {slope_expected}) intercept={intercept_auth} (expected {intercept_expected})'
                        )
                    kinetics_transform_table.append({
                        'figure_id': fid,
                        'paired_decay_id': pair_id,
                        'order': order,
                        'k': str(k_dec),
                        'C0_mol_l': str(c0_dec),
                        'recomputed_slope': str(slope_expected),
                        'authored_slope': str(slope_auth),
                        'recomputed_intercept': str(intercept_expected),
                        'authored_intercept': str(intercept_auth),
                        'pair_parameters_match': pair_ok,
                        'agrees': agrees,
                    })

                # half-life recompute
                if order == 0:
                    hl_exact = c0_dec / (Decimal('2') * k_dec)
                elif order == 1:
                    hl_exact = Decimal('0.693147180559945309417232121458') / k_dec
                else:
                    hl_exact = Decimal('1') / (k_dec * c0_dec)
                hl_auth = ks.get('half_life_s')
                hl_ok = True
                if hl_auth is not None:
                    hl_ok = abs(Decimal(str(hl_auth)) - hl_exact) <= Decimal('0.05')
                    if not hl_ok:
                        errors.append(f'{fid}: [E_FIG_HALF_LIFE_MISMATCH] authored={hl_auth} recomputed={hl_exact:.4f}')
                kinetics_half_life_table.append({
                    'figure_id': fid,
                    'order': order,
                    'recomputed_half_life_s': f'{hl_exact:.6f}',
                    'authored_half_life_s': hl_auth,
                    'agrees': hl_ok,
                })

                # tolerance coupling: all three fields resolve; rendered line inside its own tolerance
                tf = rec.get('tolerance_fields')
                if isinstance(tf, dict):
                    tol_map = {q['id']: q for q in conventions.get('tolerances', {}).get('quantity_classes', [])}
                    field_rows = {}
                    try:
                        slope_auth = Decimal(str(fit.get('slope')))
                        intercept_auth = Decimal(str(fit.get('intercept')))
                    except Exception:
                        slope_auth = intercept_auth = None
                    for fname in ('slope', 'intercept', 'point_acceptance'):
                        fld = tf.get(fname)
                        if not isinstance(fld, dict):
                            errors.append(f'{fid}: [E_FIG_TOLERANCE_FIELD_MISSING] tolerance_fields.{fname} missing')
                            continue
                        tcls = fld.get('tolerance_class')
                        mode = fld.get('tolerance_mode')
                        if tcls not in tol_map:
                            errors.append(f'{fid}: [E_FIG_UNKNOWN_TOLERANCE_CLASS] tolerance_fields.{fname} class {tcls!r} unknown')
                            continue
                        if mode not in ('absolute', 'significant_figures'):
                            errors.append(f'{fid}: [E_FIG_TOLERANCE_MODE] tolerance_fields.{fname} mode {mode!r} invalid')
                            continue
                        exp_u = fld.get('expected_unit')
                        conv_u = tol_map[tcls]['unit']
                        if exp_u != conv_u:
                            errors.append(f'{fid}: [E_FIG_TOLERANCE_UNIT_MISMATCH] tolerance_fields.{fname} unit {exp_u!r} != class {conv_u!r}')
                        cref = fld.get('conventions_ref')
                        if cref not in valid_conv_refs:
                            errors.append(f'{fid}: [E_FIG_UNKNOWN_CONV_REF] tolerance_fields.{fname} ref {cref!r} unknown')
                        expected_val = slope_auth if fname == 'slope' else intercept_auth
                        tol_val = _tol_value(fld, expected_val if expected_val is not None else Decimal('0'), tol_map)
                        if tol_val is None:
                            errors.append(f'{fid}: [E_FIG_TOLERANCE_FIELD_UNRESOLVED] tolerance_fields.{fname} has no usable tolerance value')
                            continue
                        field_rows[fname] = {'class': tcls, 'mode': mode, 'value': tol_val}
                    if all(k in field_rows for k in ('slope', 'intercept', 'point_acceptance')) and slope_auth is not None:
                        slope_diff = abs(slope_auth - slope_expected)
                        intercept_diff = abs(intercept_auth - intercept_expected)
                        point_diff = Decimal('0')
                        x_min = Decimal(str((rec.get('span') or {}).get('x_min', 0)))
                        x_max = Decimal(str((rec.get('span') or {}).get('x_max', 0)))
                        n_samp = 11
                        for i in range(n_samp):
                            x_val = x_min + (x_max - x_min) * Decimal(i) / Decimal(n_samp - 1)
                            y_rendered = slope_auth * x_val + intercept_auth
                            y_true = slope_expected * x_val + intercept_expected
                            point_diff = max(point_diff, abs(y_rendered - y_true))
                        slope_ok = slope_diff <= field_rows['slope']['value']
                        int_ok = intercept_diff <= field_rows['intercept']['value']
                        pt_ok = point_diff <= field_rows['point_acceptance']['value']
                        if not (slope_ok and int_ok and pt_ok):
                            errors.append(
                                f'{fid}: [E_FIG_TOLERANCE_SELF_VIOLATION] rendered line exceeds its own tolerance fields '
                                f'slope={slope_diff}>{field_rows["slope"]["value"]} int={intercept_diff}>{field_rows["intercept"]["value"]} '
                                f'point={point_diff}>{field_rows["point_acceptance"]["value"]}'
                            )
                        # rendered SVG must carry the same line
                        svg_k = rendered_svgs.get(fid, '')
                        svg_ok = True
                        if svg_k and not rec.get('gradeable'):
                            m_slope = re.search(r'data-fit-slope="([^"]+)"', svg_k)
                            m_int = re.search(r'data-fit-intercept="([^"]+)"', svg_k)
                            svg_ok = bool(m_slope and m_int) and Decimal(m_slope.group(1)) == slope_auth and Decimal(m_int.group(1)) == intercept_auth
                            if not svg_ok:
                                errors.append(f'{fid}: [E_FIG_FIT_LINE_SVG] rendered fit line slope/intercept missing or different')
                        kinetics_tolerance_table.append({
                            'figure_id': fid,
                            'fields': {
                                name: {'tolerance_class': row['class'], 'tolerance_mode': row['mode'], 'tolerance_value': str(row['value'])}
                                for name, row in field_rows.items()
                            },
                            'slope_difference': str(slope_diff),
                            'intercept_difference': str(intercept_diff),
                            'max_point_difference': str(point_diff),
                            'rendered_line_within_own_tolerance': slope_ok and int_ok and pt_ok and svg_ok,
                        })

                # span rule and render clipping
                if has_fit:
                    sp = rec.get('span') or {}
                    span_ok = (sp.get('edge_rule') == 'inclusive' and sp.get('beyond_span') == 'not_assessed'
                               and Decimal(str(fit.get('x_min'))) >= Decimal(str(sp.get('data_x_min')))
                               and Decimal(str(fit.get('x_max'))) <= Decimal(str(sp.get('data_x_max')))
                               and Decimal(str(fit.get('x_min'))) == Decimal(str(sp.get('x_min')))
                               and Decimal(str(fit.get('x_max'))) == Decimal(str(sp.get('x_max'))))
                    if not span_ok:
                        errors.append(f'{fid}: [E_FIG_SPAN_EXCEEDS_DATA] fit line or declared span exceeds the data span')
                    svg_s = rendered_svgs.get(fid, '')
                    svg_clip = True
                    if svg_s and not rec.get('gradeable'):
                        m_min = re.search(r'data-fit-x-min="([^"]+)"', svg_s)
                        m_max = re.search(r'data-fit-x-max="([^"]+)"', svg_s)
                        svg_clip = (bool(m_min and m_max) and m_min.group(1) == str(sp.get('x_min'))
                                    and m_max.group(1) == str(sp.get('x_max')) and 'data-fit-clipped="true"' in svg_s)
                        if not svg_clip:
                            errors.append(f'{fid}: [E_FIG_SPAN_RENDER_MISMATCH] rendered fit-line extent != declared span')
                    kinetics_span_table.append({
                        'figure_id': fid,
                        'span_x_min': sp.get('x_min'),
                        'span_x_max': sp.get('x_max'),
                        'data_x_min': sp.get('data_x_min'),
                        'data_x_max': sp.get('data_x_max'),
                        'edge_rule': sp.get('edge_rule'),
                        'beyond_span': sp.get('beyond_span'),
                        'rendered_extent_matches': svg_clip,
                        'agrees': span_ok and svg_clip,
                    })

                # notation: log and inverse axis labels, decimal comma in copy
                y_ax = (rec.get('axes') or {}).get('y') or {}
                if has_fit and order == 1:
                    if y_ax.get('term_key') != 'fig.axis.ln_concentration_ratio':
                        errors.append(f'{fid}: [E_FIG_LOG_NOTATION] first-order linearization y axis must use fig.axis.ln_concentration_ratio')
                    term_txt = str((terms_by_key.get('fig.axis.ln_concentration_ratio') or {}).get('text_lv') or '')
                    if 'ln(' not in term_txt:
                        errors.append(f'{fid}: [E_FIG_LOG_NOTATION] log axis term lacks the ln( symbol')
                if has_fit and order == 2 and y_ax.get('unit') != 'L/mol':
                    errors.append(f'{fid}: [E_FIG_INVERSE_UNIT] second-order linearization y axis unit must be L/mol')
                copy_txt = ' '.join([str(rec.get('subtitle_lv') or ''), str(rec.get('description_lv') or '')])
                for ann in rec.get('annotations') or []:
                    e = terms_by_key.get(ann.get('annotation_key')) or {}
                    copy_txt += ' ' + str(e.get('text_lv') or '') + ' ' + str(ann.get('text_override_lv') or '')
                if re.search(r'(?<![A-Za-z0-9])\d+\.\d+', copy_txt):
                    errors.append(f'{fid}: [E_FIG_DECIMAL_COMMA] T5 copy contains a dot decimal; Latvian display uses a comma')
        # N15: titration model checks, V-05 wording, reading coupling; calibration
        # standards/fit/reading recompute, V-07 assumption honesty, no-extrapolation span.
        if rec.get('topic') == 6 or rec.get('titration_spec'):
            row = _check_titration_record(rec, terms_by_key, conventions, rendered_svgs.get(fid, ''), errors)
            titration_model_table.append(row)
            v05_copy_table.append(row.get('v05') or {'figure_id': fid, 'agrees': False})
            titration_reading_table.append({
                'figure_id': fid, 'declared_reading_ml': (rec.get('reading_strip') or {}).get('declared_reading_ml'),
                'subdivision_mm': row.get('subdivision_mm'), 'reading_coupling_ok': row.get('reading_coupling_ok'),
                'svg_present': row.get('svg_present'), 'deterministic': row.get('deterministic'),
            })
        if rec.get('topic') == 7 or rec.get('calibration_spec'):
            row = _check_calibration_record(rec, terms_by_key, rendered_svgs.get(fid, ''), errors)
            calibration_reading_table.append(row)
            calibration_assumption_table.append({
                'figure_id': fid, 'assumptions': row.get('assumptions'),
                'assumption_honesty': row.get('assumption_honesty'),
            })
            no_extrapolation_table.append({
                'figure_id': fid, 'inside_span': row.get('inside_span'),
                'fit_within_span': row.get('fit_agrees') is not None and row.get('no_extrapolation_ok'),
                'render_clipped': row.get('render_clipped'),
                'no_extrapolation_ok': row.get('no_extrapolation_ok'),
            })

    if len(burette_records) >= 2:
        missing_edges = [e for e, fids in edge_coverage_set.items() if not fids]
        if missing_edges:
            errors.append(f'[E_FIG_BURETTE_EDGE_COVERAGE] Missing required pedagogical edge cases: {missing_edges}')

    # Cross-check concept_summaries authored-N11, authored-N12 and authored-N13 slots against figures
    fig_by_id = {r['id']: r for r in records if isinstance(r, dict) and isinstance(r.get('id'), str)}
    slots_closed_n11 = 0
    slots_closed_n12 = 0
    slots_closed_n13 = 0
    slots_closed_n14 = 0
    slots_closed_n15 = 0
    for c in summaries.get('concepts', []):
        fslot = (c.get('slots') or {}).get('figures') or {}
        owner = fslot.get('owner_task')
        if owner in ('N11', 'N12', 'N13', 'N14', 'N15'):
            exp_status = f'authored-{owner}'
            if fslot.get('status') != exp_status:
                errors.append(f"{c['id']}: {owner}-owned figure slot still {fslot.get('status')!r}, expected {exp_status!r}")
                continue
            fids = fslot.get('figure_ids') or []
            for fid in fids:
                if fid not in fig_by_id:
                    errors.append(f"{c['id']}: figure slot references missing figure {fid!r}")
                elif c['id'] not in (fig_by_id[fid].get('concept_ids') or []):
                    errors.append(f"{c['id']}: figure {fid!r} does not list {c['id']} in concept_ids")
            if owner == 'N11':
                slots_closed_n11 += 1
            elif owner == 'N12':
                slots_closed_n12 += 1
            elif owner == 'N13':
                slots_closed_n13 += 1
            elif owner == 'N14':
                slots_closed_n14 += 1
            else:
                slots_closed_n15 += 1

    canonical_bytes = canonical_json_bytes(data)
    return {
        'schema_version': 1,
        'task': 'N11+N12+N13+N14+N15',
        'status': 'PASS' if not errors else 'FAIL',
        'canonical_sha256': sha256_bytes(canonical_bytes),
        'canonical_bytes': len(canonical_bytes),
        'figures_count': len(records),
        't12_slots_closed': slots_closed_n11,
        't23_slots_closed': slots_closed_n12,
        't4_slots_closed': slots_closed_n13,
        't5_slots_closed': slots_closed_n14,
        't67_slots_closed': slots_closed_n15,
        'label_checks': label_checks,
        'unit_checks': unit_checks,
        'description_checks': description_checks,
        'burette_scale_labels_checked': burette_scale_labels_checked,
        'reading_contract': reading_contract,
        'energy_contract': energy_contract,
        'burette_geometry_table': burette_geometry_table,
        'edge_coverage_table': edge_coverage_set,
        'dilution_arithmetic_table': dilution_arithmetic_table,
        'curve_generation_table': curve_generation_table,
        'energy_sign_table': energy_sign_table,
        'hess_cycle_table': hess_cycle_table,
        'mb_honesty_table': mb_honesty_table,
        'v06_scope_table': v06_scope_table,
        'kinetics_contract': kinetics_contract,
        'kinetics_transform_table': kinetics_transform_table,
        'kinetics_half_life_table': kinetics_half_life_table,
        'kinetics_tolerance_table': kinetics_tolerance_table,
        'kinetics_span_table': kinetics_span_table,
        'titration_contract': titration_contract,
        'calibration_contract': calibration_contract,
        'titration_model_table': titration_model_table,
        'v05_copy_table': v05_copy_table,
        'titration_reading_table': titration_reading_table,
        'calibration_reading_table': calibration_reading_table,
        'calibration_assumption_table': calibration_assumption_table,
        'no_extrapolation_table': no_extrapolation_table,
        'citation_table': citation_table,
        'tolerance_table': tolerance_table,
        'recompute_table': recompute_table,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    return (
        f"figures {report['status']}: records={report['figures_count']}, "
        f"slots_closed=N11:{report['t12_slots_closed']}/18+N12:{report['t23_slots_closed']}/12+N13:{report['t4_slots_closed']}/11+N14:{report['t5_slots_closed']}/10+N15:{report['t67_slots_closed']}/13, "
        f"recomputed={len(report['recompute_table'])}, "
        f"curves={len(report['curve_generation_table'])}, hess={len(report['hess_cycle_table'])}, mb={len(report['mb_honesty_table'])}, "
        f"t5_transforms={len(report['kinetics_transform_table'])}, t5_tol={len(report['kinetics_tolerance_table'])}, t5_span={len(report['kinetics_span_table'])}, "
        f"t67_models={len(report['titration_model_table'])}, t67_readings={len(report['calibration_reading_table'])}, "
        f"labels={report['label_checks']}, units={report['unit_checks']}, "
        f"bytes={report['canonical_bytes']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figures', type=Path, default=None)
    parser.add_argument('--report', type=Path, default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    report = validate_figures(figures_path=args.figures)
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
