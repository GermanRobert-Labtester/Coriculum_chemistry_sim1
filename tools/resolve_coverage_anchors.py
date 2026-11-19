#!/usr/bin/env python3
"""Resolve all 64 coverage master anchors against the frozen masters.

The record is bound to the N01 frozen digests. A future master edit therefore
invalidates the record visibly: the recomputed digest no longer matches the
inventory, and the resolver refuses to issue a PASS.

Matching rule: the master_anchor is compared to the master's ``id`` attribute
case-exactly. No lower-casing, trimming or Unicode normalisation is applied;
the masters use ASCII ids such as ``stehiometrija`` and ``maisijumi``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import (  # noqa: E402
    COVERAGE_PATH, DEST, TOPIC_MASTER_PATHS, anchor_heading, canonical_json_bytes,
    inventory_master_digests, load_json, parse_master, sha256_file,
)
from validate_coverage import format_summary, validate  # noqa: E402

DEFAULT_RECORD = DEST / 'evidence/N02_ANCHOR_RESOLUTION.json'


def build_record(island_path: Path, repo_root: Path, masters_root: Path) -> dict:
    island = load_json(island_path)
    inventory = inventory_master_digests(repo_root)
    masters = {}
    master_records = []
    for topic, relative in TOPIC_MASTER_PATHS.items():
        full = masters_root / relative
        entry = inventory.get(topic, {})
        digest = sha256_file(full)
        masters[topic] = parse_master(full)
        master_records.append({
            'topic': topic,
            'freeze_id': entry.get('id'),
            'path': relative,
            'bytes': full.stat().st_size,
            'sha256': digest,
            'recorded_bytes': entry.get('bytes'),
            'recorded_sha256': entry.get('sha256'),
            'digest_matches_freeze': digest == entry.get('sha256') and full.stat().st_size == entry.get('bytes'),
        })
    resolutions = []
    per_topic = {str(t): {'resolved': 0, 'total': 0} for t in range(1, 8)}
    failures = []
    for outcome in island['outcomes']:
        topic = outcome['topic']
        anchor = outcome['master_anchor']
        per_topic[str(topic)]['total'] += 1
        index = masters[topic]
        if anchor not in index.ids:
            hint = [value for value in index.ids if value.lower() == anchor.lower()]
            failures.append({
                'outcome_id': outcome['id'],
                'topic': topic,
                'master_freeze_id': outcome['master_freeze_id'],
                'master_path': outcome['master_path'],
                'anchor': anchor,
                'reason': 'anchor not found with case-exact matching',
                'case_insensitive_matches': hint[:5],
            })
            continue
        heading = anchor_heading(index, anchor)
        if heading != outcome['master_heading_lv']:
            failures.append({
                'outcome_id': outcome['id'],
                'topic': topic,
                'master_freeze_id': outcome['master_freeze_id'],
                'master_path': outcome['master_path'],
                'anchor': anchor,
                'reason': 'heading mismatch',
                'recorded_heading': outcome['master_heading_lv'],
                'master_heading': heading,
            })
            continue
        per_topic[str(topic)]['resolved'] += 1
        resolutions.append({
            'outcome_id': outcome['id'],
            'topic': topic,
            'master_freeze_id': outcome['master_freeze_id'],
            'master_path': outcome['master_path'],
            'master_sha256': inventory[topic]['sha256'],
            'anchor': anchor,
            'heading_lv': heading,
            'status': 'RESOLVED',
        })
    canonical = canonical_json_bytes(island)
    return {
        'schema_version': 1,
        'task': 'N02',
        'artifact': 'coverage-anchor-resolution',
        'island': str(island_path.relative_to(repo_root)) if island_path.is_relative_to(repo_root) else str(island_path),
        'island_sha256': sha256_file(island_path),
        'island_canonical_sha256': __import__('hashlib').sha256(canonical).hexdigest(),
        'island_canonical_bytes': len(canonical),
        'bound_to': 'N01 source freeze (evidence/SOURCE_FREEZE_INVENTORY.json, VERIFIED 2026-11-16)',
        'matching_rule': 'case-exact ASCII id attribute matching; no lower-casing, trimming or Unicode normalisation',
        'counts': {
            'total': len(island['outcomes']),
            'resolved': len(resolutions),
            'failed': len(failures),
            'per_topic': per_topic,
        },
        'masters': master_records,
        'resolutions': resolutions,
        'failures': failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--island', default=str(DEST / COVERAGE_PATH))
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--masters-root', default=None)
    parser.add_argument('--out', default=str(DEFAULT_RECORD))
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    masters_root = Path(args.masters_root) if args.masters_root else repo_root
    island_path = Path(args.island)
    if not island_path.is_absolute():
        island_path = repo_root / island_path
    validation = validate(island_path=island_path, repo_root=repo_root, masters_root=masters_root)
    if validation['status'] != 'PASS':
        print(format_summary(validation), file=sys.stderr)
        print('FAIL coverage-anchor-resolution: the island did not pass the pre-resolution validation', file=sys.stderr)
        return 1
    record = build_record(island_path, repo_root, masters_root)
    if record['failures']:
        print(f'FAIL coverage-anchor-resolution: {record["counts"]["failed"]} of {record["counts"]["total"]} anchors failed', file=sys.stderr)
        for failure in record['failures']:
            print(
                f'  - {failure["outcome_id"]} #{failure["anchor"]} in {failure["master_freeze_id"]} '
                f'({failure["master_path"]}): {failure["reason"]}',
                file=sys.stderr,
            )
        return 1
    if not all(master['digest_matches_freeze'] for master in record['masters']):
        print('FAIL coverage-anchor-resolution: one or more master digests differ from the N01 freeze', file=sys.stderr)
        return 1
    out = Path(args.out)
    if not out.is_absolute():
        out = DEST / out
    out.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    out.write_text(text, encoding='utf-8')
    if args.json:
        print(text, end='')
    else:
        per_topic = record['counts']['per_topic']
        distribution = '/'.join(f'{per_topic[str(t)]["resolved"]}/{per_topic[str(t)]["total"]}' for t in range(1, 8))
        print(f'PASS coverage-anchor-resolution: {record["counts"]["resolved"]}/{record["counts"]["total"]} anchors resolved, 0 failures')
        print(f'  per-topic resolved/total: {distribution}')
        print(f'  bound to frozen masters: {", ".join(m["freeze_id"] + "=" + m["sha256"][:16] for m in record["masters"])}')
        print(f'  record: {out} ({out.stat().st_size} bytes, sha256={sha256_file(out)})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
