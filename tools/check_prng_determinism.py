#!/usr/bin/env python3
"""N05 cross-language PRNG determinism harness & frozen table verifier.

Proves:
  1. Python (tools/prng.py) and JavaScript (src/prng.js) produce bit-identical
     u64 draw streams over all 11 declared contract seeds (100 draws each),
     matching the committed frozen value table in data/prng_contract_vectors.json.
  2. Unbiased bounded draws (nextInt, nextRange) and Fisher-Yates shuffles match
     across languages element-for-element and draw-count-for-draw-count.
  3. Illegal seeds (0, negative, float, > 2^64-1, string, bool, null) and
     illegal bounds are rejected identically with E_PRNG_INVALID_SEED /
     E_PRNG_INVALID_BOUND in both languages.
  4. Deliberately perturbed scratch twins (one JS constant altered, one Python
     constant altered) are caught and named with exact seed, draw index, and
     divergent values.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prng as py_prng  # noqa: E402
from coverage_common import DEST, canonical_json_bytes, sha256_bytes, sha256_file  # noqa: E402

CONTRACT_PATH = DEST / 'data/prng_contract_vectors.json'
SEED_POLICY_PATH = DEST / 'data/seed_policy.json'
JS_PRNG_PATH = DEST / 'src/prng.js'
PY_PRNG_PATH = DEST / 'tools/prng.py'
JS_HARNESS_PATH = DEST / 'tools/check_prng_runtime.js'
WORK = Path('/tmp/opencode/n05-prng-scratch')


def _sha_text(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def _parse_input(raw: Any) -> Any:
    if isinstance(raw, dict):
        if 'bigint_dec' in raw:
            return int(raw['bigint_dec'])
        if 'float' in raw:
            return float(raw['float'])
        if 'special' in raw:
            if raw['special'] == 'NaN':
                return math.nan
            if raw['special'] == 'Infinity':
                return math.inf
            if raw['special'] == 'undefined':
                return None
    return raw


def build_spec_skeleton() -> dict[str, Any]:
    policy = json.loads(SEED_POLICY_PATH.read_text(encoding='utf-8'))
    seeds = policy['seed_vocabulary']['N05_N36_verification']['contract_seeds_dec']
    return {
        'schema_version': 1,
        'artifact': 'prng-cross-language-contract-vectors',
        'policy_id': policy['policy_id'],
        'non_cryptographic_notice': policy['non_cryptographic_notice'],
        'draws_per_seed': 100,
        'contract_seeds_dec': seeds,
        'bounded_cases': [
            {'id': 'BOUND-21-S1', 'seed_dec': '1', 'op': 'nextInt', 'bound': 21, 'count': 50},
            {'id': 'BOUND-7-N24A', 'seed_dec': '100001', 'op': 'nextInt', 'bound': 7, 'count': 50},
            {'id': 'BOUND-1-EDGE', 'seed_dec': '42', 'op': 'nextInt', 'bound': 1, 'count': 5},
            {'id': 'RANGE-10-20', 'seed_dec': '2025', 'op': 'nextRange', 'min': 10, 'max': 20, 'count': 30},
            {'id': 'BOUND-BIG-U64SEED', 'seed_dec': '18446744073709551615', 'op': 'nextInt', 'bound': 1000, 'count': 25},
        ],
        'shuffle_cases': [
            {
                'id': 'SHUFFLE-21-SLOTS',
                'seed_dec': '100001',
                'items': [
                    'S1-1', 'S1-2', 'S1-3', 'S2-1', 'S2-2', 'S2-3',
                    'S3-1', 'S3-2', 'S3-3', 'S4-1', 'S4-2', 'S4-3',
                    'S5-1', 'S5-2', 'S5-3', 'S6-1', 'S6-2', 'S6-3',
                    'S7-1', 'S7-2', 'S7-3',
                ],
            },
            {
                'id': 'SHUFFLE-4-OPTIONS',
                'seed_dec': '2025',
                'items': ['A', 'B', 'C', 'D'],
            },
            {
                'id': 'SHUFFLE-1-ITEM',
                'seed_dec': '42',
                'items': ['ONLY'],
            },
            {
                'id': 'SHUFFLE-EMPTY',
                'seed_dec': '42',
                'items': [],
            },
        ],
        'illegal_seed_cases': [
            {'label': 'zero', 'input': 0},
            {'label': 'negative_one', 'input': -1},
            {'label': 'negative_forty_two', 'input': -42},
            {'label': 'above_u64_max', 'input': {'bigint_dec': '18446744073709551616'}},
            {'label': 'float_half', 'input': {'float': 1.5}},
            {'label': 'nan', 'input': {'special': 'NaN'}},
            {'label': 'infinity', 'input': {'special': 'Infinity'}},
            {'label': 'string_42', 'input': '42'},
            {'label': 'boolean_true', 'input': True},
            {'label': 'null', 'input': None},
        ],
        'illegal_bound_cases': [
            {'label': 'bound_zero', 'input': 0},
            {'label': 'bound_negative', 'input': -5},
            {'label': 'bound_float', 'input': {'float': 2.5}},
        ],
    }


def run_python_suite(mod: Any, spec: dict[str, Any]) -> dict[str, Any]:
    draws_per_seed = spec['draws_per_seed']
    streams = []
    for seed_str in spec['contract_seeds_dec']:
        stream = mod.create_stream(int(seed_str))
        draws = [str(stream.next_u64()) for _ in range(draws_per_seed)]
        streams.append({
            'seed_dec': seed_str,
            'draws': draws,
            'sha256': _sha_text(','.join(draws)),
        })

    bounded = []
    for bcase in spec['bounded_cases']:
        stream = mod.create_stream(int(bcase['seed_dec']))
        if bcase['op'] == 'nextInt':
            values = [stream.next_int(bcase['bound']) for _ in range(bcase['count'])]
        else:
            values = [stream.next_range(bcase['min'], bcase['max']) for _ in range(bcase['count'])]
        bounded.append({
            'id': bcase['id'],
            'values': values,
            'draws_consumed': stream.draws_count(),
            'sha256': _sha_text(json.dumps(values, separators=(',', ':'))),
        })

    shuffles = []
    for scase in spec['shuffle_cases']:
        stream = mod.create_stream(int(scase['seed_dec']))
        orig = list(scase['items'])
        out = stream.shuffle(orig)
        shuffles.append({
            'id': scase['id'],
            'input_preserved': orig == scase['items'],
            'output': out,
            'draws_consumed': stream.draws_count(),
            'sha256': _sha_text(json.dumps(out, ensure_ascii=False, separators=(',', ':'))),
        })

    illegal_seeds = []
    for icase in spec['illegal_seed_cases']:
        seed_val = _parse_input(icase['input'])
        rejected = False
        code = None
        try:
            mod.create_stream(seed_val)
        except Exception as exc:
            rejected = True
            code = getattr(exc, 'code', None)
        illegal_seeds.append({'label': icase['label'], 'rejected': rejected, 'code': code})

    illegal_bounds = []
    for bcase in spec['illegal_bound_cases']:
        stream = mod.create_stream(1)
        rejected = False
        code = None
        try:
            stream.next_int(_parse_input(bcase['input']))
        except Exception as exc:
            rejected = True
            code = getattr(exc, 'code', None)
        illegal_bounds.append({'label': bcase['label'], 'rejected': rejected, 'code': code})

    return {
        'language': 'python',
        'algorithm_id': mod.ALGORITHM_ID,
        'streams': streams,
        'bounded': bounded,
        'shuffles': shuffles,
        'illegal_seeds': illegal_seeds,
        'illegal_bounds': illegal_bounds,
    }


def run_js_suite(prng_path: Path, spec_path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        ['node', str(JS_HARNESS_PATH), '--prng-path', str(prng_path), '--spec', str(spec_path)],
        cwd=DEST,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f'JS PRNG harness failed ({proc.returncode}): {proc.stderr}')
    return json.loads(proc.stdout)


def compare_outputs(py_out: dict[str, Any], js_out: dict[str, Any], frozen: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    divergences: list[dict[str, Any]] = []
    for idx, (p_s, j_s) in enumerate(zip(py_out['streams'], js_out['streams'])):
        if p_s['seed_dec'] != j_s['seed_dec']:
            divergences.append({'kind': 'seed_mismatch', 'index': idx, 'py': p_s['seed_dec'], 'js': j_s['seed_dec']})
            continue
        for draw_idx, (pv, jv) in enumerate(zip(p_s['draws'], j_s['draws'])):
            if pv != jv:
                divergences.append({
                    'kind': 'stream_draw_divergence',
                    'seed_dec': p_s['seed_dec'],
                    'draw_index': draw_idx,
                    'python_value': pv,
                    'js_value': jv,
                })
                break
        if frozen is not None:
            f_s = frozen['streams'][idx]
            if p_s['sha256'] != f_s['sha256'] or p_s['draws'] != f_s['draws']:
                divergences.append({
                    'kind': 'frozen_contract_mismatch',
                    'seed_dec': p_s['seed_dec'],
                    'expected_sha256': f_s['sha256'],
                    'python_sha256': p_s['sha256'],
                })

    for idx, (p_b, j_b) in enumerate(zip(py_out['bounded'], js_out['bounded'])):
        if p_b['values'] != j_b['values'] or p_b['draws_consumed'] != j_b['draws_consumed']:
            divergences.append({'kind': 'bounded_divergence', 'id': p_b['id'], 'py': p_b, 'js': j_b})
        elif frozen is not None and p_b['values'] != frozen['bounded'][idx]['values']:
            divergences.append({'kind': 'frozen_bounded_mismatch', 'id': p_b['id']})

    for idx, (p_sh, j_sh) in enumerate(zip(py_out['shuffles'], js_out['shuffles'])):
        if p_sh['output'] != j_sh['output'] or p_sh['draws_consumed'] != j_sh['draws_consumed'] or not p_sh['input_preserved'] or not j_sh['input_preserved']:
            divergences.append({'kind': 'shuffle_divergence', 'id': p_sh['id'], 'py': p_sh, 'js': j_sh})
        elif frozen is not None and p_sh['output'] != frozen['shuffles'][idx]['output']:
            divergences.append({'kind': 'frozen_shuffle_mismatch', 'id': p_sh['id']})

    for p_i, j_i in zip(py_out['illegal_seeds'], js_out['illegal_seeds']):
        if not p_i['rejected'] or not j_i['rejected'] or p_i['code'] != 'E_PRNG_INVALID_SEED' or j_i['code'] != 'E_PRNG_INVALID_SEED':
            divergences.append({'kind': 'illegal_seed_mismatch', 'label': p_i['label'], 'py': p_i, 'js': j_i})

    for p_b, j_b in zip(py_out['illegal_bounds'], js_out['illegal_bounds']):
        if not p_b['rejected'] or not j_b['rejected'] or p_b['code'] != 'E_PRNG_INVALID_BOUND' or j_b['code'] != 'E_PRNG_INVALID_BOUND':
            divergences.append({'kind': 'illegal_bound_mismatch', 'label': p_b['label'], 'py': p_b, 'js': j_b})

    return divergences


def generate_contract() -> dict[str, Any]:
    spec = build_spec_skeleton()
    WORK.mkdir(parents=True, exist_ok=True)
    tmp_spec = WORK / 'spec.json'
    tmp_spec.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    py_out = run_python_suite(py_prng, spec)
    js_out = run_js_suite(JS_PRNG_PATH, tmp_spec)
    divs = compare_outputs(py_out, js_out, frozen=None)
    if divs:
        raise RuntimeError(f'Cannot freeze PRNG contract; Python/JS divergence detected: {divs}')

    contract = {
        **spec,
        'streams': py_out['streams'],
        'bounded': py_out['bounded'],
        'shuffles': py_out['shuffles'],
        'illegal_seeds_verified': py_out['illegal_seeds'],
        'illegal_bounds_verified': py_out['illegal_bounds'],
        'table_sha256': sha256_bytes(canonical_json_bytes({
            'streams': py_out['streams'],
            'bounded': py_out['bounded'],
            'shuffles': py_out['shuffles'],
        })),
    }
    CONTRACT_PATH.write_text(json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return contract


def verify_determinism() -> dict[str, Any]:
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)

    frozen = json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
    py_out = run_python_suite(py_prng, frozen)
    js_out = run_js_suite(JS_PRNG_PATH, CONTRACT_PATH)
    green_divs = compare_outputs(py_out, js_out, frozen=frozen)

    # Negative perturbation 1: alter JS GAMMA constant by +1n in scratch twin
    js_src = JS_PRNG_PATH.read_text(encoding='utf-8')
    perturbed_js_src = js_src.replace('0x9E3779B97F4A7C15n', '0x9E3779B97F4A7C16n', 1)
    if perturbed_js_src == js_src:
        raise RuntimeError('Failed to create perturbed JS scratch twin')
    perturbed_js_path = WORK / 'prng_perturbed_gamma.js'
    perturbed_js_path.write_text(perturbed_js_src, encoding='utf-8')
    perturbed_js_out = run_js_suite(perturbed_js_path, CONTRACT_PATH)
    perturbed_js_divs = compare_outputs(py_out, perturbed_js_out, frozen=None)

    # Negative perturbation 2: alter Python MUL1 constant in scratch twin
    py_src = PY_PRNG_PATH.read_text(encoding='utf-8')
    perturbed_py_src = py_src.replace('0xBF58476D1CE4E5B9', '0xBF58476D1CE4E5BA', 1)
    if perturbed_py_src == py_src:
        raise RuntimeError('Failed to create perturbed Python scratch twin')
    perturbed_py_path = WORK / 'prng_perturbed_mul1.py'
    perturbed_py_path.write_text(perturbed_py_src, encoding='utf-8')
    import importlib.util
    spec_mod = importlib.util.spec_from_file_location('prng_perturbed_mul1', perturbed_py_path)
    assert spec_mod and spec_mod.loader
    perturbed_py_mod = importlib.util.module_from_spec(spec_mod)
    spec_mod.loader.exec_module(perturbed_py_mod)
    perturbed_py_out = run_python_suite(perturbed_py_mod, frozen)
    perturbed_py_divs = compare_outputs(perturbed_py_out, js_out, frozen=None)

    ok = (
        len(green_divs) == 0
        and len(perturbed_js_divs) > 0
        and len(perturbed_py_divs) > 0
    )

    return {
        'schema_version': 1,
        'task': 'N05',
        'status': 'PASS' if ok else 'FAIL',
        'policy_id': frozen['policy_id'],
        'contract_sha256': sha256_file(CONTRACT_PATH),
        'table_sha256': frozen['table_sha256'],
        'py_prng_sha256': sha256_file(PY_PRNG_PATH),
        'js_prng_sha256': sha256_file(JS_PRNG_PATH),
        'seed_count': len(frozen['contract_seeds_dec']),
        'draws_per_seed': frozen['draws_per_seed'],
        'total_stream_draws_compared': len(frozen['contract_seeds_dec']) * frozen['draws_per_seed'],
        'green_comparison': {
            'divergences_count': len(green_divs),
            'divergences': green_divs,
            'stream_digests': [{'seed_dec': s['seed_dec'], 'sha256': s['sha256']} for s in py_out['streams']],
            'bounded_digests': [{'id': b['id'], 'draws_consumed': b['draws_consumed'], 'sha256': b['sha256']} for b in py_out['bounded']],
            'shuffle_digests': [{'id': s['id'], 'draws_consumed': s['draws_consumed'], 'sha256': s['sha256']} for s in py_out['shuffles']],
            'illegal_seeds_rejected': len(py_out['illegal_seeds']),
            'illegal_bounds_rejected': len(py_out['illegal_bounds']),
        },
        'negative_perturbation_js_gamma': {
            'perturbed_constant': 'GAMMA (0x9E3779B97F4A7C15n -> 0x9E3779B97F4A7C16n)',
            'caught': len(perturbed_js_divs) > 0,
            'divergences_count': len(perturbed_js_divs),
            'first_divergence': perturbed_js_divs[0] if perturbed_js_divs else None,
        },
        'negative_perturbation_py_mul1': {
            'perturbed_constant': 'MUL1 (0xBF58476D1CE4E5B9 -> 0xBF58476D1CE4E5BA)',
            'caught': len(perturbed_py_divs) > 0,
            'divergences_count': len(perturbed_py_divs),
            'first_divergence': perturbed_py_divs[0] if perturbed_py_divs else None,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generate', action='store_true', help='Generate/freeze data/prng_contract_vectors.json')
    parser.add_argument('--json', action='store_true', help='Print JSON report')
    parser.add_argument('--report', default=None, help='Write report JSON to path')
    args = parser.parse_args(argv)

    if args.generate:
        contract = generate_contract()
        print(f'Generated {CONTRACT_PATH} ({len(contract["contract_seeds_dec"])} seeds x {contract["draws_per_seed"]} draws, table_sha256={contract["table_sha256"]})')

    report = verify_determinism()
    if args.report:
        out = Path(args.report)
        if not out.is_absolute():
            out = DEST / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(
            f'{report["status"]} prng-determinism: {report["seed_count"]} seeds x '
            f'{report["draws_per_seed"]} draws ({report["total_stream_draws_compared"]} draws), '
            f'green_divs={report["green_comparison"]["divergences_count"]}, '
            f'js_perturb_caught={report["negative_perturbation_js_gamma"]["caught"]}, '
            f'py_perturb_caught={report["negative_perturbation_py_mul1"]["caught"]}'
        )
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
