#!/usr/bin/env python3
"""Check the N01 source-freeze inventory against the live published files.

Every FROZEN entry's byte size and SHA-256 are recomputed from the filesystem and
compared with the recorded value. Canonical masters are additionally checked
against their COPY_MANIFEST destination record. UNAVAILABLE entries must carry a
stated consequence; they are recorded, never silently dropped.

Read-only. --root allows the same checks over a scratch copy for negative fixtures.
Exit code 0 means every recorded identity matched; 1 means at least one mismatch
named the failing file.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

OFFICIAL_PROGRAMME_SHA256 = 'f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9'
HASH = re.compile(r'^[0-9a-f]{64}$')
FAILURES: list[str] = []
LINES: list[str] = []

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]),
                        help='Repository root to check (default: this workspace)')
    parser.add_argument('--inventory', default='evidence/SOURCE_FREEZE_INVENTORY.json',
                        help='Inventory path relative to --root')
    args = parser.parse_args()
    root = Path(args.root).resolve()
    inventory_path = root / args.inventory
    if not inventory_path.is_file():
        print(f'FAIL source-freeze-inventory: missing inventory {inventory_path}')
        return 1
    data = json.loads(inventory_path.read_text(encoding='utf-8'))
    sources = data.get('sources', [])

    # Structural completeness and declared counts.
    check(data.get('artifact') == 'source-freeze-inventory', 'Artifact type is not source-freeze-inventory')
    check(len(sources) == data.get('source_count'), 'source_count differs from the entry list')
    roles: dict[str, int] = {}
    ids: set[str] = set()
    frozen = unavailable = 0
    for entry in sources:
        eid = entry.get('id', '<missing id>')
        check(eid not in ids, f'Duplicate inventory id: {eid}')
        ids.add(eid)
        for field in ('path', 'role', 'status', 'consumed_by', 'citation', 'notes'):
            check(bool(entry.get(field)), f'{eid}: missing field {field}')
        roles[entry.get('role', '<missing>')] = roles.get(entry.get('role', '<missing>'), 0) + 1
        status = entry.get('status')
        check(status in {'FROZEN', 'UNAVAILABLE'}, f'{eid}: invalid status {status!r}')
        if status == 'UNAVAILABLE':
            unavailable += 1
            check(bool(entry.get('consequence')), f'{eid}: UNAVAILABLE without a stated consequence')
            LINES.append(f'UNAVAILABLE {eid}: {entry.get("path")} - recorded, not present')
            continue
        if status != 'FROZEN':
            continue
        frozen += 1
        path = root / entry['path']
        if not path.is_file():
            check(False, f'{eid}: missing file {entry["path"]}')
            LINES.append(f'FAIL {eid}: missing {entry["path"]}')
            continue
        size = path.stat().st_size
        digest = sha(path)
        if size != entry.get('bytes'):
            check(False, f'{eid}: byte size {size} differs from recorded {entry.get("bytes")} ({entry["path"]})')
            LINES.append(f'FAIL {eid}: bytes {size} != {entry.get("bytes")} ({entry["path"]})')
        if digest != entry.get('sha256'):
            check(False, f'{eid}: sha256 differs from recorded value ({entry["path"]})')
            LINES.append(f'FAIL {eid}: sha256 {digest} != {entry.get("sha256")} ({entry["path"]})')
        if size == entry.get('bytes') and digest == entry.get('sha256'):
            LINES.append(f'OK {eid}: {size} bytes sha256={digest} ({entry["path"]})')
        check(isinstance(entry.get('sha256'), str) and bool(HASH.fullmatch(entry['sha256'])),
              f'{eid}: recorded digest is not 64 lowercase hex characters')

    check(frozen == data.get('frozen_count'), 'frozen_count differs from the FROZEN entries')
    check(unavailable == data.get('unavailable_count'), 'unavailable_count differs from the UNAVAILABLE entries')
    for role, expected in data.get('required_roles', {}).items():
        check(roles.get(role, 0) == expected, f'Role {role}: {roles.get(role, 0)} entries, expected {expected}')

    masters = sorted(e.get('topic') for e in sources if e.get('role') == 'canonical-master')
    check(masters == list(range(1, 8)), f'Canonical masters do not cover topics 1-7: {masters}')

    # Canonical masters must agree with COPY_MANIFEST's destination records.
    manifest_path = root / 'COPY_MANIFEST.json'
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        by_destination = {item['destination']: item for item in manifest.get('files', [])}
        for entry in sources:
            if entry.get('role') != 'canonical-master':
                continue
            item = by_destination.get(entry.get('path'))
            if item is None:
                check(False, f'{entry.get("id")}: path is not a COPY_MANIFEST destination')
                continue
            check(item['bytes'] == entry.get('bytes'), f'{entry.get("id")}: bytes differ from COPY_MANIFEST record')
            check(item['sha256'] == entry.get('sha256'), f'{entry.get("id")}: digest differs from COPY_MANIFEST record')
    else:
        check(False, 'COPY_MANIFEST.json missing; master cross-check not possible')

    # The strongest single anchor: the official programme PDF digest, reproduced exactly.
    programme = next((e for e in sources if e.get('role') == 'official-programme'), None)
    check(programme is not None, 'No official-programme entry in the inventory')
    if programme is not None:
        check(programme.get('sha256') == OFFICIAL_PROGRAMME_SHA256,
              'Programme entry digest differs from the inspection anchor')
        check(programme.get('bytes') == 353_208, 'Programme entry byte size differs from 353,208')
        live = root / programme['path']
        if live.is_file():
            live_digest = sha(live)
            check(live_digest == OFFICIAL_PROGRAMME_SHA256, 'Live programme PDF digest differs from the inspection anchor')
            LINES.append(f'PDF {live_digest} == inspection anchor {OFFICIAL_PROGRAMME_SHA256}')
    check(data.get('official_programme_sha256') == OFFICIAL_PROGRAMME_SHA256,
          'Inventory official_programme_sha256 differs from the inspection anchor')

    status = 'PASS' if not FAILURES else 'FAIL'
    print(f'{status} source-freeze-inventory: {len(sources)} entries, {frozen} frozen, {unavailable} unavailable, root={root}')
    for line in LINES:
        print('  ' + line)
    for failure in FAILURES:
        print('  FAIL ' + failure)
    return 0 if not FAILURES else 1

if __name__ == '__main__':
    raise SystemExit(main())
