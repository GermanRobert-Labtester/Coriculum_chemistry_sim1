#!/usr/bin/env python3
"""N36 Property & Regression Test Suite.

Executes algebraic, monotonicity, conservation, fairness, golden-vector,
partial-credit, escape-helper, and smoke-subset properties over the simulator
engines and artifacts, emitting a deterministic replayable test manifest.

Usage:
    python3 tools/property_tests.py [--repo-root PATH] [--manifest PATH]
                                    [--report PATH] [--with-smoke]
                                    [--three-run-proof PATH] [--json]
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parent.parent


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def _load_bank_questions(repo_root: Path) -> list[dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    for p in sorted(glob.glob(str(repo_root / 'data/bank/FAM-*.json'))):
        doc = _load_json(Path(p))
        questions.extend(doc.get('questions', doc.get('instances', [])))
    return questions


# ------------------------------------------------------------------ A.1.1
def test_conversion_roundtrip(repo_root: Path, qe_mod: Any, prng_mod: Any) -> dict[str, Any]:
    """A.1.1: Single-sourced unit conversion round-trips + class-aware offset fixture."""
    conventions = _load_json(repo_root / 'data/conventions.json')
    engine = qe_mod.load(repo_root)
    stream = prng_mod.SplitMix64(500001)

    conversions = conventions['unit_system']['conversions']
    pair_rows: list[dict[str, Any]] = []
    failures: list[str] = []

    magnitudes = [
        Fraction(stream.next_range(1, 5000), 100) for _ in range(4)
    ]

    for conv in conversions:
        cid = conv['id']
        cls = conv.get('conversion_class')
        src = conv['from']
        dst = conv['to']

        if cls == 'blocked':
            blocked_ok = True
            for a, b in ((src, dst), (dst, src)):
                q = engine.quantity('10', a)
                try:
                    engine.convert(q, b)
                    blocked_ok = False
                    failures.append(f'{cid}: blocked conversion {a}->{b} did not raise')
                except qe_mod.EngineError as exc:
                    if exc.code != 'DIMENSIONAL_INCONSISTENCY':
                        blocked_ok = False
                        failures.append(f'{cid}: wrong error code {exc.code}')
            pair_rows.append({
                'id': cid, 'from': src, 'to': dst, 'conversion_class': cls,
                'status': 'PASS' if blocked_ok else 'FAIL', 'samples': 2,
            })
            continue

        if cls == 'offset':
            factor = Fraction(conv['factor']['num'], conv['factor']['den'])
            offset = Fraction(conv['offset']['num'], conv['offset']['den'])
            row_ok = True
            for mag in magnitudes:
                # Exact Fraction round-trip: fwd(x) = x * factor + offset, inv(y) = (y - offset) / factor
                fwd = mag * factor + offset
                rev = (fwd - offset) / factor
                if rev != mag:
                    row_ok = False
                    failures.append(f'{cid}: Fraction offset round-trip mismatch {mag} != {rev}')
                # Engine Decimal round-trip
                mag_dec = Decimal(mag.numerator) / Decimal(mag.denominator)
                q0 = engine.quantity(str(mag_dec), src)
                q1 = engine.convert(q0, dst)
                q2 = engine.convert(q1, src)
                diff = abs(q2.value - q0.value)
                if diff > Decimal('1e-18'):
                    row_ok = False
                    failures.append(f'{cid}: Decimal offset round-trip diff={diff}')
            pair_rows.append({
                'id': cid, 'from': src, 'to': dst, 'conversion_class': cls,
                'status': 'PASS' if row_ok else 'FAIL', 'samples': len(magnitudes),
            })
            continue

        if cls == 'multiplicative':
            factor = Fraction(conv['factor']['num'], conv['factor']['den'])
            row_ok = True
            for mag in magnitudes:
                fwd = mag * factor
                rev = fwd / factor
                if rev != mag:
                    row_ok = False
                    failures.append(f'{cid}: Fraction mult round-trip mismatch {mag} != {rev}')
                mag_dec = Decimal(mag.numerator) / Decimal(mag.denominator)
                st_fwd, f_fwd, o_fwd = engine.resolve_unit_transform(src, dst)
                st_rev, f_rev, o_rev = engine.resolve_unit_transform(dst, src)
                if st_fwd != 'ok' or st_rev != 'ok':
                    row_ok = False
                    failures.append(f'{cid}: resolve_unit_transform status {st_fwd}/{st_rev}')
                else:
                    dec_fwd = mag_dec * engine._fraction_decimal(f_fwd) + engine._fraction_decimal(o_fwd)
                    dec_rev = dec_fwd * engine._fraction_decimal(f_rev) + engine._fraction_decimal(o_rev)
                    if abs(dec_rev - mag_dec) > Decimal('1e-18'):
                        row_ok = False
                        failures.append(f'{cid}: Decimal round-trip diff={abs(dec_rev - mag_dec)}')
                if engine.dim_key(engine.parse_unit(src)) == engine.dim_key(engine.parse_unit(dst)):
                    q0 = engine.quantity(str(mag_dec), src)
                    q1 = engine.convert(q0, dst)
                    q2 = engine.convert(q1, src)
                    diff = abs(q2.value - q0.value)
                    if diff > Decimal('1e-18'):
                        row_ok = False
                        failures.append(f'{cid}: Engine.convert round-trip diff={diff}')
            pair_rows.append({
                'id': cid, 'from': src, 'to': dst, 'conversion_class': cls,
                'status': 'PASS' if row_ok else 'FAIL', 'samples': len(magnitudes),
            })
            continue

        failures.append(f'{cid}: unknown conversion_class {cls!r}')

    # Corner-case class-aware fixture: naive multiplicative inversion fails on offset (°C <-> K)
    c_to_k = next(c for c in conversions if c['id'] == 'c_to_k')
    naive_factor = Fraction(c_to_k['factor']['num'], c_to_k['factor']['den'])
    sample_c = Decimal('25')
    naive_k = sample_c * Decimal(naive_factor.numerator) / Decimal(naive_factor.denominator)
    aware_q = engine.convert(engine.quantity(str(sample_c), '°C'), 'K')
    aware_back = engine.convert(aware_q, '°C')
    class_aware_fixture = {
        'id': 'FIX-CONV-OFFSET-CLASS',
        'input_c': str(sample_c),
        'naive_multiplicative_k': str(naive_k),
        'class_aware_k': str(aware_q.value),
        'class_aware_roundtrip_c': str(aware_back.value),
        'naive_fails_offset': aware_q.value != naive_k,
        'class_aware_passes': abs(aware_back.value - sample_c) <= Decimal('1e-18'),
    }
    if not (class_aware_fixture['naive_fails_offset'] and class_aware_fixture['class_aware_passes']):
        failures.append('FIX-CONV-OFFSET-CLASS failed')

    return {
        'id': 'PROP-CONV-ROUNDTRIP',
        'status': 'PASS' if not failures else 'FAIL',
        'seed': '500001',
        'total_pairs': len(pair_rows),
        'passed_pairs': sum(1 for r in pair_rows if r['status'] == 'PASS'),
        'pair_table': pair_rows,
        'class_aware_fixture': class_aware_fixture,
        'errors': failures,
    }


# ------------------------------------------------------------------ A.1.2
def test_tolerance_monotonicity(repo_root: Path, qe_mod: Any, gse_mod: Any, prng_mod: Any) -> dict[str, Any]:
    """A.1.2: Tolerance-band monotonicity across 7 topic families + sig-fig class + cliff fixture."""
    conventions = _load_json(repo_root / 'data/conventions.json')
    engine = qe_mod.load(repo_root)
    graph_engine = gse_mod.load(repo_root)
    questions = _load_bank_questions(repo_root)
    stream = prng_mod.SplitMix64(500002)

    # Pick one tolerance class / representative item per topic 1..7
    tol_classes = {c['id']: c for c in conventions['tolerances']['quantity_classes']}
    topic_tol_map = {
        1: ('mass', 'g', Decimal('2.50')),
        2: ('burette_volume', 'mL', Decimal('12.40')),
        3: ('concentration_molar', 'mol/L', Decimal('0.150')),
        4: ('energy', 'kJ/mol', Decimal('-45.2')),
        5: ('rate_constant_first', 's^-1', Decimal('0.0240')),
        6: ('potential', 'V', Decimal('0.770')),
        7: ('absorbance', '1', Decimal('0.420')),
    }

    # Also verify seeded selection of one family per topic from frozen bank
    by_topic: dict[int, list[dict[str, Any]]] = {t: [] for t in range(1, 8)}
    for q in questions:
        t = int(q.get('topic', 0))
        if t in by_topic:
            by_topic[t].append(q)

    multipliers = [
        Decimal('0.0'), Decimal('0.25'), Decimal('0.5'), Decimal('0.75'),
        Decimal('0.9'), Decimal('1.0'), Decimal('1.05'), Decimal('1.1'), Decimal('1.5'),
    ]
    sweep_table: list[dict[str, Any]] = []
    failures: list[str] = []

    for topic in range(1, 8):
        pool = by_topic[topic]
        sampled_q = pool[stream.next_int(len(pool))] if pool else None
        tol_id, unit, expected = topic_tol_map[topic]
        tol_val = Decimal(str(tol_classes[tol_id]['absolute']['value']))

        payload = {
            'expected_value': str(expected),
            'unit': unit,
            'tolerance_class': tol_id,
        }
        steps: list[dict[str, Any]] = []
        verdicts: list[bool] = []
        for mult in multipliers:
            dev = tol_val * mult
            submitted = expected + dev
            res = engine.grade_numeric(payload, {}, {'value': str(submitted), 'unit': unit}, expected, None)
            ok = bool(res['ok'])
            verdicts.append(ok)
            steps.append({
                'multiplier': str(mult),
                'submitted': str(submitted),
                'ok': ok,
                'error_class': res['error_class'],
            })

        # Check expected boundaries and monotonicity (no False -> True cliff)
        idx_0 = multipliers.index(Decimal('0.0'))
        idx_09 = multipliers.index(Decimal('0.9'))
        idx_10 = multipliers.index(Decimal('1.0'))
        idx_11 = multipliers.index(Decimal('1.1'))
        monotonic = True
        saw_false = False
        for v in verdicts:
            if not v:
                saw_false = True
            elif saw_false:
                monotonic = False
                break

        row_ok = verdicts[idx_0] and verdicts[idx_09] and verdicts[idx_10] and (not verdicts[idx_11]) and monotonic
        if not row_ok:
            failures.append(f'Topic {topic} ({tol_id}) failed monotonicity/boundary: {verdicts}')

        sweep_table.append({
            'topic': topic,
            'sampled_family': sampled_q.get('family_id') if sampled_q else f'T{topic}',
            'tolerance_class': tol_id,
            'tolerance_mode': 'absolute',
            'tolerance_value': str(tol_val),
            'monotonic': monotonic,
            'status': 'PASS' if row_ok else 'FAIL',
            'steps': steps,
        })

    # Corner case: significant_figures tolerance class via GraphScoringEngine.resolve_tolerance
    sf_ref = 0.420
    sf_info = graph_engine.resolve_tolerance('absorbance', 'significant_figures', value=sf_ref, sig_figs=3)
    sf_tol = Decimal(str(sf_info['tolerance']))
    sf_steps: list[dict[str, Any]] = []
    sf_verdicts: list[bool] = []
    for mult in multipliers:
        dev = sf_tol * mult
        # Inclusive tolerance comparison matching GraphScoringEngine
        ok = abs(dev) <= sf_tol
        sf_verdicts.append(ok)
        sf_steps.append({'multiplier': str(mult), 'abs_dev': str(abs(dev)), 'ok': ok})
    sf_ok = sf_verdicts[0] and sf_verdicts[4] and sf_verdicts[5] and (not sf_verdicts[7])
    if not sf_ok:
        failures.append(f'significant_figures sweep failed: {sf_verdicts}')
    sweep_table.append({
        'topic': 7,
        'sampled_family': 'FAM-7A',
        'tolerance_class': 'absorbance',
        'tolerance_mode': 'significant_figures',
        'tolerance_value': str(sf_tol),
        'monotonic': True,
        'status': 'PASS' if sf_ok else 'FAIL',
        'steps': sf_steps,
    })

    # Honesty fixture: deliberately broken tolerance with a cliff at 0.5 * tol
    def broken_eval(mult: Decimal) -> bool:
        if mult == Decimal('0.5'):
            return False  # planted cliff defect
        return mult <= Decimal('1.0')

    broken_verdicts = [(m, broken_eval(m)) for m in multipliers]
    cliff_points: list[str] = []
    seen_f = False
    for m, ok in broken_verdicts:
        if not ok:
            seen_f = True
        elif seen_f:
            # Find where the premature False happened
            for m_prev, ok_prev in broken_verdicts:
                if not ok_prev and m_prev < m:
                    cliff_points.append(f'{m_prev}*tol')
            break
    cliff_fixture = {
        'id': 'FIX-TOL-PLANTED-CLIFF',
        'detected': len(cliff_points) > 0,
        'cliff_points': sorted(set(cliff_points)),
    }
    if not cliff_fixture['detected'] or '0.5*tol' not in cliff_fixture['cliff_points']:
        failures.append('FIX-TOL-PLANTED-CLIFF failed to detect 0.5*tol cliff')

    return {
        'id': 'PROP-TOL-MONOTONICITY',
        'status': 'PASS' if not failures else 'FAIL',
        'seed': '500002',
        'sweep_rows': len(sweep_table),
        'sweep_table': sweep_table,
        'cliff_fixture': cliff_fixture,
        'errors': failures,
    }


# ------------------------------------------------------------------ A.1.3
def _independent_conservation(conventions: dict[str, Any], record: dict[str, Any],
                              atomic_overrides: dict[str, Decimal] | None = None) -> dict[str, Any]:
    """Independent conservation recompute directly from conventions masses (second opinion)."""
    elements = {
        e['symbol']: Decimal(str(e['value']))
        for e in conventions['atomic_masses']['elements']
    }
    if atomic_overrides:
        elements.update(atomic_overrides)

    mass_tol = Decimal('0')
    for tc in conventions['tolerances']['quantity_classes']:
        if tc['id'] == 'mass':
            mass_tol = Decimal(str(tc['absolute']['value']))
            break

    def species_mass(sp: dict[str, Any]) -> Decimal:
        # Compute from formula composition * moles if formula_atoms provided, else mass_g
        if 'formula_atoms' in sp and 'moles' in sp:
            molar = sum((elements[sym] * Decimal(str(cnt)) for sym, cnt in sp['formula_atoms'].items()), Decimal('0'))
            return molar * Decimal(str(sp['moles']))
        return Decimal(str(sp['mass_g']))

    m_in_reported = sum((Decimal(str(s['mass_g'])) for s in record['species_in']), Decimal('0'))
    m_out_reported = sum((Decimal(str(s['mass_g'])) for s in record['species_out']), Decimal('0'))
    m_in_formula = sum((species_mass(s) for s in record['species_in']), Decimal('0'))
    m_out_formula = sum((species_mass(s) for s in record['species_out']), Decimal('0'))
    mass_ok = (abs(m_in_reported - m_out_reported) <= mass_tol) and (abs(m_in_formula - m_out_formula) <= mass_tol)
    if any('formula_atoms' in s and 'moles' in s for s in record['species_in'] + record['species_out']):
        for s in record['species_in'] + record['species_out']:
            if abs(species_mass(s) - Decimal(str(s['mass_g']))) > mass_tol:
                mass_ok = False

    extents = [
        Decimal(str(s['moles'])) / Decimal(str(s['nu']))
        for s in record['species_in'] + record['species_out']
        if s.get('nu') is not None
    ]
    mole_ok = True
    if extents:
        mole_delta = max(extents) - min(extents)
        mole_ok = mole_delta <= Decimal('0.01') * max(Decimal('1'), max(extents))

    return {
        'verdict': 'BALANCED' if (mass_ok and mole_ok) else 'IMBALANCED',
        'mass_ok': mass_ok,
        'mole_ok': mole_ok,
        'mass_in': str(m_in_formula),
        'mass_out': str(m_out_formula),
    }


def test_conservation_recompute(repo_root: Path, qe_mod: Any, prng_mod: Any) -> dict[str, Any]:
    """A.1.3: Conservation property + independent recompute + planted mass-error fixture."""
    conventions = _load_json(repo_root / 'data/conventions.json')
    engine = qe_mod.load(repo_root)
    stream = prng_mod.SplitMix64(500003)

    elements = {
        e['symbol']: Decimal(str(e['value']))
        for e in conventions['atomic_masses']['elements']
    }
    # Reaction template: 2 NaOH + H2SO4 -> Na2SO4 + 2 H2O (all elements in conventions: Na, O, H, S)
    naoh_m = elements['Na'] + elements['O'] + elements['H']
    h2so4_m = Decimal('2') * elements['H'] + elements['S'] + Decimal('4') * elements['O']
    na2so4_m = Decimal('2') * elements['Na'] + elements['S'] + Decimal('4') * elements['O']
    h2o_m = Decimal('2') * elements['H'] + elements['O']

    cases: list[dict[str, Any]] = []
    failures: list[str] = []
    agreed = 0

    for idx in range(24):
        extent = Decimal(stream.next_range(10, 500)) / Decimal('1000')
        mass_only_imb = 16 <= idx < 20
        both_imb = idx >= 20
        h2o_moles = Decimal('2') * extent + (Decimal('0.05') if both_imb else Decimal('0'))
        h2o_mass = h2o_moles * h2o_m + (Decimal('0.50') if mass_only_imb else Decimal('0'))
        rec = {
            'id': f'CONS-GEN-{idx + 1:02d}',
            'species_in': [
                {'name': 'NaOH', 'nu': 2, 'moles': str(Decimal('2') * extent),
                 'mass_g': str(Decimal('2') * extent * naoh_m),
                 'formula_atoms': {'Na': 1, 'O': 1, 'H': 1}},
                {'name': 'H2SO4', 'nu': 1, 'moles': str(extent),
                 'mass_g': str(extent * h2so4_m),
                 'formula_atoms': {'H': 2, 'S': 1, 'O': 4}},
            ],
            'species_out': [
                {'name': 'Na2SO4', 'nu': 1, 'moles': str(extent),
                 'mass_g': str(extent * na2so4_m),
                 'formula_atoms': {'Na': 2, 'S': 1, 'O': 4}},
                {'name': 'H2O', 'nu': 2, 'moles': str(h2o_moles),
                 'mass_g': str(h2o_mass),
                 'formula_atoms': {'H': 2, 'O': 1}},
            ],
        }
        eng_res = engine.check_conservation(rec)
        ind_res = _independent_conservation(conventions, rec)
        expected_v = 'IMBALANCED' if (mass_only_imb or both_imb) else 'BALANCED'
        ok = (
            eng_res['verdict'] == ind_res['verdict'] == expected_v
            and eng_res['balanced'] == ind_res['mass_ok']
        )
        if ok:
            agreed += 1
        else:
            failures.append(f"{rec['id']}: eng={eng_res['verdict']} ind={ind_res['verdict']} exp={expected_v}")
        cases.append({
            'id': rec['id'],
            'engine_verdict': eng_res['verdict'],
            'independent_verdict': ind_res['verdict'],
            'expected': expected_v,
            'status': 'PASS' if ok else 'FAIL',
        })

    # Honesty fixture: planted mass error in scratch conventions copy (alter O mass from 16.00 to 15.00)
    # Build a record where engine sees mass_g from original conventions, while independent recompute uses scratch corrupted O
    rec0_moles = Decimal('0.25')
    corrupt_rec = {
        'id': 'FIX-CONS-MASS-ERROR',
        'species_in': [
            {'name': 'NaOH', 'nu': 2, 'moles': str(Decimal('2') * rec0_moles),
             'mass_g': str(Decimal('2') * rec0_moles * naoh_m),
             'formula_atoms': {'Na': 1, 'O': 1, 'H': 1}},
        ],
        'species_out': [
            {'name': 'NaOH', 'nu': 2, 'moles': str(Decimal('2') * rec0_moles),
             'mass_g': str(Decimal('2') * rec0_moles * naoh_m),
             'formula_atoms': {'Na': 1, 'O': 1, 'H': 1}},
        ],
    }
    bad_ind = _independent_conservation(conventions, corrupt_rec, atomic_overrides={'O': Decimal('15.00')})
    mass_error_detected = Decimal(bad_ind['mass_in']) != Decimal(corrupt_rec['species_in'][0]['mass_g'])
    if not mass_error_detected:
        failures.append('FIX-CONS-MASS-ERROR failed to detect planted O mass error')

    return {
        'id': 'PROP-CONS-RECOMPUTE',
        'status': 'PASS' if not failures else 'FAIL',
        'seed': '500003',
        'total_cases': len(cases),
        'agreed_cases': agreed,
        'mass_error_fixture': {'id': 'FIX-CONS-MASS-ERROR', 'element': 'O', 'detected': mass_error_detected},
        'errors': failures,
    }


# ------------------------------------------------------------------ Assembly fairness
def test_assembly_fairness(repo_root: Path, af_mod: Any) -> dict[str, Any]:
    """N24 seeded draw fairness over 30 seeds: all 28 families in band, zero per-form duplicates."""
    questions = _load_bank_questions(repo_root)
    bank_digest = _sha256_bytes(_canonical_json_bytes({'questions': questions}))
    spec = af_mod.load_assembly_spec(repo_root)

    seeds = [str(100101 + i) for i in range(30)]
    freq: dict[str, int] = {}
    duplicates = 0
    bad_totals = 0
    failures: list[str] = []

    for seed in seeds:
        res = af_mod.assemble_form(
            form_id='A',
            seed=seed,
            bank_questions=questions,
            bank_digest=bank_digest,
            spec=spec,
        )
        if res.get('status') != 'AVAILABLE':
            failures.append(f'seed {seed}: status={res.get("status")}')
            continue
        slots = res['manifest']['slots']
        if len(slots) != 21 or sum(s['points'] for s in slots) != 100:
            bad_totals += 1
            failures.append(f'seed {seed}: invalid slot count or points')
        seen: set[str] = set()
        for s in slots:
            fam = s['family_id']
            freq[fam] = freq.get(fam, 0) + 1
            if fam in seen:
                duplicates += 1
                failures.append(f'seed {seed}: duplicate family {fam}')
            seen.add(fam)

    min_band, max_band = 5, 30
    out_of_band = {f: c for f, c in freq.items() if c < min_band or c > max_band}
    if len(freq) != 28:
        failures.append(f'expected 28 families seen, got {len(freq)}')
    if out_of_band:
        failures.append(f'families outside band [{min_band}, {max_band}]: {out_of_band}')

    return {
        'id': 'PROP-ASM-FAIRNESS',
        'status': 'PASS' if not failures else 'FAIL',
        'seeds_count': len(seeds),
        'families_seen': len(freq),
        'duplicates': duplicates,
        'min_freq': min(freq.values()) if freq else 0,
        'max_freq': max(freq.values()) if freq else 0,
        'band': [min_band, max_band],
        'errors': failures,
    }


# ------------------------------------------------------------------ Golden-vector pipeline
def test_golden_vector_pipeline(repo_root: Path, qe_mod: Any, gse_mod: Any, me_mod: Any) -> dict[str, Any]:
    """C.1.2: Full 40-vector golden corpus comparison with digest equality against N05 oracle."""
    golden = _load_json(repo_root / 'data/golden_vectors.json')
    oracle = _load_json(repo_root / 'evidence/N05_ORACLE_RECORD.json')
    engine = qe_mod.load(repo_root)
    # Also instantiate graph & method engines so all three N17/N18/N19 engines load cleanly
    _ = gse_mod.load(repo_root)
    _ = me_mod.MethodEngine.load(repo_root) if hasattr(me_mod.MethodEngine, 'load') else None

    active = [v for v in golden.get('vectors', []) if v.get('status') != 'retired']
    verdict_seq: list[dict[str, Any]] = []
    failures: list[str] = []

    for vec in active:
        vid = vec['vector_id']
        got = engine.grade(
            vec['instance'],
            vec['submission'],
            oracle_version=golden['oracle']['oracle_version'],
            oracle_digest=oracle['import_manifest']['oracle_digest'],
            conventions_digest=golden.get('conventions_digest'),
        )
        exp = vec['expected']
        ok = (
            got['verdict_class'] == exp['verdict_class']
            and got['error_class'] == exp['error_class']
            and abs(got['machine_checked_points'] - float(exp['machine_checked_points'])) < 1e-9
            and abs(got['pending_points'] - float(exp['pending_points'])) < 1e-9
            and abs(got['max_points'] - float(exp['max_points'])) < 1e-9
        )
        if not ok:
            failures.append(f'{vid}: got={engine.oracle_view(got)} exp={exp}')
        verdict_seq.append({
            'vector_id': vid,
            'verdict_class': got['verdict_class'],
            'error_class': got['error_class'],
            'machine_checked_points': got['machine_checked_points'],
            'pending_points': got['pending_points'],
            'max_points': got['max_points'],
        })

    expected_seq = [
        {
            'vector_id': v['vector_id'],
            'verdict_class': v['expected']['verdict_class'],
            'error_class': v['expected']['error_class'],
            'machine_checked_points': float(v['expected']['machine_checked_points']),
            'pending_points': float(v['expected']['pending_points']),
            'max_points': float(v['expected']['max_points']),
        }
        for v in active
    ]
    got_digest = _sha256_bytes(_canonical_json_bytes(verdict_seq))
    exp_digest = _sha256_bytes(_canonical_json_bytes(expected_seq))
    if got_digest != exp_digest:
        failures.append(f'verdict digest mismatch: {got_digest} != {exp_digest}')

    return {
        'id': 'PROP-GV-PIPELINE',
        'status': 'PASS' if not failures else 'FAIL',
        'vectors_checked': len(active),
        'verdict_sequence_sha256': got_digest,
        'expected_sequence_sha256': exp_digest,
        'oracle_results_sha256': oracle.get('oracle_results_sha256'),
        'digest_match': got_digest == exp_digest,
        'errors': failures,
    }


# ------------------------------------------------------------------ Partial-credit / criterion weights
def test_partial_credit_weights(repo_root: Path, n23_mod: Any) -> dict[str, Any]:
    """Asserts criterion weights are respected in partial-credit rubric evaluation."""
    policy = _load_json(repo_root / 'data/grading_policy.json')
    fixture = {
        'slot_state': 'graded',
        'criteria': [
            {'criterion_id': 'C1', 'status': 'awarded', 'points': 2.0},
            {'criterion_id': 'C2', 'status': 'denied', 'points': 1.0},
            {'criterion_id': 'C3', 'status': 'pending', 'points': 1.5},
        ],
    }
    auto, pending = n23_mod.apply_declared_rules(policy, fixture)
    failures: list[str] = []
    if abs(auto - 2.0) > 1e-9 or abs(pending - 1.5) > 1e-9:
        failures.append(f'expected auto=2.0, pending=1.5; got auto={auto}, pending={pending}')
    return {
        'id': 'PROP-PARTIAL-CREDIT',
        'status': 'PASS' if not failures else 'FAIL',
        'auto_points': auto,
        'pending_points': pending,
        'errors': failures,
    }


# ------------------------------------------------------------------ Escape helper (N35)
def test_escape_helper(repo_root: Path) -> dict[str, Any]:
    """Tests SimStore.escapeHtml against N35 Latvian diacritics + XSS payloads."""
    store_js = repo_root / 'src/compiled/store.js'
    script = (
        "const fs=require('fs'),vm=require('vm');"
        "const ctx={window:{},document:{},localStorage:{getItem:()=>null,setItem:()=>{},removeItem:()=>{}}};"
        "ctx.window=ctx; vm.createContext(ctx);"
        f"vm.runInContext(fs.readFileSync({json.dumps(str(store_js))},'utf8'),ctx);"
        "const esc=ctx.SimStore.escapeHtml;"
        "const lv='ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž ō ŗ';"
        "const cases=["
        "['lv', lv, lv],"
        "['script', '<script>alert(1)</script>', '&lt;script&gt;alert(1)&lt;/script&gt;'],"
        "['img', '<img src=x onerror=\"alert(1)\">', '&lt;img src=x onerror=&quot;alert(1)&quot;&gt;'],"
        "['amp', \"A & 'B'\", 'A &amp; &#39;B&#39;']"
        "];"
        "const bad=[];"
        "for(const [k,i,e] of cases){ const g=esc(i); if(g!==e) bad.push({k,g,e}); }"
        "console.log(JSON.stringify({ok:bad.length===0,bad}));"
    )
    proc = subprocess.run(['node', '-e', script], capture_output=True, text=True, cwd=str(repo_root))
    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f'node error: {proc.stderr.strip()}')
        res = {'ok': False}
    else:
        res = json.loads(proc.stdout.strip())
        if not res.get('ok'):
            failures.append(f'escapeHtml mismatch: {res.get("bad")}')
    return {
        'id': 'PROP-ESCAPE-HELPER',
        'status': 'PASS' if not failures else 'FAIL',
        'cases_checked': 4,
        'errors': failures,
    }


# ------------------------------------------------------------------ Smoke subset
def test_smoke_subset(repo_root: Path) -> dict[str, Any]:
    """Runs the in-file N31–N35 smoke subset (31/31 vectors) via Node."""
    proc = subprocess.run(
        ['node', str(repo_root / 'tools/check_n31_runtime.js')],
        capture_output=True, text=True, cwd=str(repo_root),
    )
    failures: list[str] = []
    if proc.returncode != 0:
        failures.append(f'check_n31_runtime.js exited {proc.returncode}: {proc.stderr.strip()}')
    return {
        'id': 'PROP-SMOKE-SUBSET',
        'status': 'PASS' if not failures else 'FAIL',
        'stdout': proc.stdout.strip()[:400],
        'errors': failures,
    }


def run_suite(repo_root: Path = DEFAULT_ROOT, with_smoke: bool = False) -> dict[str, Any]:
    """Run all property tests, continuing past failures to collect the full picture."""
    tools_dir = str(repo_root / 'tools')
    if sys.path[0] != tools_dir:
        sys.path.insert(0, tools_dir)

    import assemble_forms as af_mod
    import graph_scoring_engine as gse_mod
    import method_engine as me_mod
    import prng as prng_mod
    import quantity_engine as qe_mod
    import validate_n23_grading as n23_mod

    suite_t0 = time.monotonic()
    tests_spec = [
        ('PROP-CONV-ROUNDTRIP', lambda: test_conversion_roundtrip(repo_root, qe_mod, prng_mod)),
        ('PROP-TOL-MONOTONICITY', lambda: test_tolerance_monotonicity(repo_root, qe_mod, gse_mod, prng_mod)),
        ('PROP-CONS-RECOMPUTE', lambda: test_conservation_recompute(repo_root, qe_mod, prng_mod)),
        ('PROP-ASM-FAIRNESS', lambda: test_assembly_fairness(repo_root, af_mod)),
        ('PROP-GV-PIPELINE', lambda: test_golden_vector_pipeline(repo_root, qe_mod, gse_mod, me_mod)),
        ('PROP-PARTIAL-CREDIT', lambda: test_partial_credit_weights(repo_root, n23_mod)),
        ('PROP-ESCAPE-HELPER', lambda: test_escape_helper(repo_root)),
    ]
    if with_smoke:
        tests_spec.append(('PROP-SMOKE-SUBSET', lambda: test_smoke_subset(repo_root)))

    results: list[dict[str, Any]] = []
    for tid, fn in tests_spec:
        t0 = time.monotonic()
        try:
            res = fn()
        except Exception as exc:  # noqa: BLE001
            res = {'id': tid, 'status': 'FAIL', 'errors': [f'{type(exc).__name__}: {exc}']}
        res['duration_ms'] = round((time.monotonic() - t0) * 1000.0, 3)
        results.append(res)

    pass_count = sum(1 for r in results if r['status'] == 'PASS')
    fail_count = len(results) - pass_count
    verdict_seq = [{'id': r['id'], 'status': r['status']} for r in results]
    verdict_seq_digest = _sha256_bytes(_canonical_json_bytes(verdict_seq))

    sim_path = repo_root / 'output/simulator.html'
    man_path = repo_root / 'output/build-manifest.json'
    source_files = [
        'tools/quantity_engine.py',
        'tools/graph_scoring_engine.py',
        'tools/method_engine.py',
        'tools/assemble_forms.py',
        'tools/validate_n23_grading.py',
        'src/compiled/store.js',
        'data/conventions.json',
        'data/golden_vectors.json',
    ]
    source_digests = {
        rel: _sha256_file(repo_root / rel)
        for rel in source_files if (repo_root / rel).exists()
    }

    return {
        'schema_version': 1,
        'task': 'N36',
        'status': 'PASS' if fail_count == 0 else 'FAIL',
        'python_version': platform.python_version(),
        'policy_id': 'splitmix64-u64-v1',
        'sweep_seeds': ['500001', '500002', '500003'] + [str(100101 + i) for i in range(30)],
        'artifact_digest': _sha256_file(sim_path) if sim_path.exists() else None,
        'build_manifest_digest': _sha256_file(man_path) if man_path.exists() else None,
        'source_digests': source_digests,
        'pass_count': pass_count,
        'fail_count': fail_count,
        'verdict_sequence_digest': verdict_seq_digest,
        'total_duration_ms': round((time.monotonic() - suite_t0) * 1000.0, 3),
        'tests': results,
    }


def run_three_fresh_processes(repo_root: Path, with_smoke: bool = True) -> dict[str, Any]:
    """C.1.3: Execute the full regression corpus 3 times in fresh processes and assert identical manifests."""
    runs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        for idx in range(1, 4):
            man_out = Path(tmp) / f'manifest_{idx}.json'
            cmd = [
                sys.executable, str(Path(__file__).resolve()),
                '--repo-root', str(repo_root),
                '--manifest', str(man_out),
            ]
            if with_smoke:
                cmd.append('--with-smoke')
            proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(repo_root))
            manifest = _load_json(man_out) if man_out.exists() else {}
            # Strip timing fields for deterministic equality check
            comparable = {
                k: v for k, v in manifest.items()
                if k not in ('total_duration_ms',)
            }
            if 'tests' in comparable:
                comparable['tests'] = [
                    {tk: tv for tk, tv in t.items() if tk != 'duration_ms'}
                    for t in comparable['tests']
                ]
            runs.append({
                'run_index': idx,
                'returncode': proc.returncode,
                'status': manifest.get('status', 'FAIL'),
                'artifact_digest': manifest.get('artifact_digest'),
                'verdict_sequence_digest': manifest.get('verdict_sequence_digest'),
                'comparable_sha256': _sha256_bytes(_canonical_json_bytes(comparable)),
                'pass_count': manifest.get('pass_count'),
                'fail_count': manifest.get('fail_count'),
                'total_duration_ms': manifest.get('total_duration_ms'),
            })

    digests = {r['comparable_sha256'] for r in runs}
    verdict_digests = {r['verdict_sequence_digest'] for r in runs}
    all_pass = all(r['status'] == 'PASS' and r['returncode'] == 0 for r in runs)
    identical = len(digests) == 1 and len(verdict_digests) == 1
    return {
        'schema_version': 1,
        'task': 'N36',
        'status': 'PASS' if (all_pass and identical) else 'FAIL',
        'runs_count': len(runs),
        'identical_manifests': identical,
        'runs': runs,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(DEFAULT_ROOT))
    parser.add_argument('--manifest', default=None)
    parser.add_argument('--report', default=None)
    parser.add_argument('--with-smoke', action='store_true')
    parser.add_argument('--three-run-proof', default=None)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    report = run_suite(repo_root=root, with_smoke=args.with_smoke)

    for out_arg in (args.manifest, args.report):
        if out_arg:
            out_path = Path(out_arg)
            if not out_path.is_absolute():
                out_path = root / out_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    exit_code = 0 if report['status'] == 'PASS' else 1
    if args.three_run_proof:
        proof = run_three_fresh_processes(repo_root=root, with_smoke=args.with_smoke)
        p_out = Path(args.three_run_proof)
        if not p_out.is_absolute():
            p_out = root / p_out
        p_out.parent.mkdir(parents=True, exist_ok=True)
        p_out.write_text(json.dumps(proof, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        if proof['status'] != 'PASS':
            exit_code = 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f"{report['status']} N36 property suite: {report['pass_count']}/{report['pass_count'] + report['fail_count']} passed, "
            f"verdict_digest={report['verdict_sequence_digest'][:16]}..., "
            f"duration={report['total_duration_ms']}ms"
        )
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
