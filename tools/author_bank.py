#!/usr/bin/env python3
"""Author the frozen N20 practice bank (112 instances) into ``data/bank/``.

Every instance is produced by the N20 variant engine from the frozen family
templates in ``data/family_templates/`` and the frozen conventions island in
``data/conventions.json``. Nothing is written by hand here: the script only
decides *where* the instances go and records the seed table.

The bank is written as one JSON file per family (``data/bank/FAM-1A.json`` …
``data/bank/FAM-7D.json``), each holding ``{"questions": [...]}``. The N04
validator collects every ``*.json`` under the bank directory, so no review
record, recompute table or leak-scan report may live in ``data/bank/`` —
those belong in ``evidence/``.

Usage:
    python3 tools/author_bank.py [--repo-root .] [--check]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from variant_engine import (  # noqa: E402
    BANK_VERSION,
    VariantEngineError,
    canonical_bytes,
    instantiate,
    load_templates,
    sha256_bytes,
)

BANK_DIR = Path('data/bank')
SEED_TABLE = Path('evidence/N20_SEED_TABLE.json')


def build_instances(repo_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    templates = load_templates(repo_root / 'data/family_templates')
    conventions = json.loads((repo_root / 'data/conventions.json').read_text(encoding='utf-8'))
    by_family: dict[str, list[dict[str, Any]]] = {}
    seeds: list[dict[str, Any]] = []
    for family in templates:
        for variant in family['variants']:
            instance = instantiate(family, variant, conventions=conventions)
            by_family.setdefault(family['family_id'], []).append(instance)
            data = instance['extensions']['data']
            seeds.append({
                'question_id': instance['question_id'],
                'family_id': instance['family_id'],
                'variant_id': instance['variant_id'],
                'seed_key': data['seed_key'],
                'seed': instance['seed'],
                'seed_algorithm': data['seed_algorithm'],
                'type_id': instance['type_id'],
                'topic': instance['topic'],
                'point_weight': data['point_weight'],
            })
    instances = [q for family_id in sorted(by_family) for q in by_family[family_id]]
    meta = {
        'bank_version': BANK_VERSION,
        'instances': len(instances),
        'families': len(by_family),
        'seed_table': seeds,
    }
    return instances, meta


def _strip_review_state(instance: dict[str, Any]) -> dict[str, Any]:
    """The instance as the authoring tool produced it.

    The frozen bank files carry the review *workflow* record that the review
    pass wrote into them, so the authored bytes and the frozen bytes differ
    by exactly that record. The check therefore compares the authored
    content, not the review record, and the record itself is verified by the
    review gate.
    """
    stripped = copy.deepcopy(instance)
    data = stripped.get('extensions', {}).get('data')
    if isinstance(data, dict):
        data.pop('review_workflow', None)
    return stripped


def write_bank(repo_root: Path, check_only: bool) -> dict[str, Any]:
    instances, meta = build_instances(repo_root)
    by_family: dict[str, list[dict[str, Any]]] = {}
    for instance in instances:
        by_family.setdefault(instance['family_id'], []).append(instance)

    out_dir = repo_root / BANK_DIR
    written: list[str] = []
    mismatched: list[str] = []
    for family_id in sorted(by_family):
        payload = {'island_id': 'sim-bank', 'questions': by_family[family_id]}
        data = canonical_bytes(payload) + b'\n'
        path = out_dir / f'{family_id}.json'
        if check_only:
            if not path.exists():
                mismatched.append(str(path.relative_to(repo_root)))
                continue
            frozen = json.loads(path.read_text(encoding='utf-8'))
            frozen_questions = frozen.get('questions', []) if isinstance(frozen, dict) else frozen
            authored = canonical_bytes({
                'island_id': 'sim-bank',
                'questions': [_strip_review_state(q) for q in by_family[family_id]],
            }) + b'\n'
            frozen_bytes = canonical_bytes({
                'island_id': 'sim-bank',
                'questions': [_strip_review_state(q) for q in frozen_questions],
            }) + b'\n'
            if authored != frozen_bytes:
                mismatched.append(str(path.relative_to(repo_root)))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        written.append(str(path.relative_to(repo_root)))

    seed_payload = {
        'bank_version': BANK_VERSION,
        'policy_label': 'PROPOSED training policy (N20): 28 families x 4 variants = 112 instances.',
        'seed_algorithm': 'fnv1a64-utf8-v1',
        'instances': meta['instances'],
        'families': meta['families'],
        'seeds': meta['seed_table'],
    }
    seed_bytes = json.dumps(seed_payload, ensure_ascii=False, indent=2, sort_keys=True).encode('utf-8') + b'\n'
    seed_path = repo_root / SEED_TABLE
    if check_only:
        if not seed_path.exists() or seed_path.read_bytes() != seed_bytes:
            mismatched.append(str(SEED_TABLE))
    else:
        seed_path.parent.mkdir(parents=True, exist_ok=True)
        seed_path.write_bytes(seed_bytes)

    total = 0
    for path in sorted((repo_root / BANK_DIR).glob('*.json')):
        total += path.stat().st_size
    return {
        'instances': meta['instances'],
        'families': meta['families'],
        'files': written or sorted(
            str(p.relative_to(repo_root)) for p in (repo_root / BANK_DIR).glob('*.json')),
        'bank_bytes': total,
        'bank_digest': bank_digest(repo_root) if not check_only else None,
        'mismatched': mismatched,
    }


def bank_digest(repo_root: Path) -> str:
    """SHA-256 over the frozen bank files, in family order.

    The files are already canonical, so hashing their bytes is both the
    simplest and the most reproducible definition: re-serialising the parsed
    JSON would round-trip the numbers through the language's float printer,
    which is exactly the kind of drift the frozen contract forbids.
    """
    import hashlib
    digest = hashlib.sha256()
    for path in sorted((repo_root / BANK_DIR).glob('*.json')):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Author the N20 practice bank.')
    parser.add_argument('--repo-root', default='.')
    parser.add_argument('--check', action='store_true',
                        help='Verify the frozen bank matches a fresh instantiation.')
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    try:
        report = write_bank(repo_root, args.check)
    except VariantEngineError as error:
        print(str(error), file=sys.stderr)
        return 2
    report['mode'] = 'check' if args.check else 'write'
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.check and report['mismatched']:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
