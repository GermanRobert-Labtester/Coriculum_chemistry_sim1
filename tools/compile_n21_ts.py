#!/usr/bin/env python3
"""N21 TypeScript compile step and drift guard.

The N21 runtime modules are authored in strict TypeScript (``src/session.ts``
and ``src/exam.ts``) and compiled to plain local JavaScript
(``src/compiled/*.js``). The compiled files are what the build inlines and
what the runtime harness loads, so they are committed artefacts.

The N22 input modules (``src/inputs/registry.ts``, ``src/inputs/components.ts``
and ``src/inputs/integration.ts``) compile through the same pinned
configuration into ``src/compiled/inputs/*.js``; the drift guard covers them
through the same ``EXPECTED_OUTPUTS`` list, so a stale module anywhere in the
set is caught before it can ship.

The N23 grading modules (``src/grading.ts`` and ``src/feedback.ts``) join the
same pinned configuration and the same drift guard; their compiled outputs
(``src/compiled/grading.js`` and ``src/compiled/feedback.js``) ship from
``src/`` exactly like the N17–N20 engine modules and are not inlined into the
artifact — N31 owns the inline / lazy-load / re-budget decision.

This tool has two jobs:

  * ``--build`` (the default) recompiles the modules with the pinned
    ``tsc`` configuration and writes the compiled files;
  * ``--check`` recompiles into a temporary directory and compares the result
    byte-for-byte with the committed files, so a source change that was not
    recompiled is caught by the build gate instead of silently shipping a
    stale module.

The compiler is invoked through ``npx --no-install tsc`` so that the build
stays offline: if TypeScript is not installed locally the tool fails loudly
with a named message instead of reaching for the network.

Usage:
    python3 tools/compile_n21_ts.py            # compile in place
    python3 tools/compile_n21_ts.py --check    # drift guard
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, sha256_file  # noqa: E402

ROOT = DEST
SRC = ROOT / 'src'
TSCONFIG = SRC / 'tsconfig.json'
COMPILED = SRC / 'compiled'
EXPECTED_OUTPUTS = [
    'session.js',
    'exam.js',
    'inputs/registry.js',
    'inputs/components.js',
    'inputs/integration.js',
    'grading.js',
    'feedback.js',
    'assembly.js',
    'store.js',
    'analytics.js',
    'mastery.js',
    'scheduler.js',
    'remediation.js',
    'revision.js',
    'practice.js',
    'focus.js',
    'paper.js',
]


def run_tsc(project: Path) -> subprocess.CompletedProcess:
    """Compile with the pinned tsconfig. Never touches the network."""
    npx = shutil.which('npx')
    if npx is None:
        raise SystemExit(
            'FAIL n21-ts-compile: npx not found. The N21 runtime modules are '
            'authored in TypeScript; install TypeScript locally (npm i -g typescript) '
            'and re-run. The build does not download anything.'
        )
    return subprocess.run(
        [npx, '--no-install', 'tsc', '-p', str(project)],
        cwd=str(ROOT), capture_output=True, text=True,
    )


def _write_isolated_project(out_dir: Path) -> Path:
    """Write a copy of the pinned tsconfig that emits into ``out_dir``.

    The copy lives next to the original so that the relative ``files`` and
    ``rootDir`` entries resolve exactly as they do for the real build; only
    ``outDir`` is redirected. Without this the drift check would overwrite the
    committed modules it is supposed to compare against.
    """
    config = json.loads(TSCONFIG.read_text(encoding='utf-8'))
    config['compilerOptions']['outDir'] = str(out_dir)
    isolated = SRC / 'tsconfig.n21-drift-check.json'
    isolated.write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    return isolated


def compile_in_place() -> int:
    proc = run_tsc(TSCONFIG)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        print('FAIL n21-ts-compile: tsc reported errors', file=sys.stderr)
        return 1
    missing = [name for name in EXPECTED_OUTPUTS if not (COMPILED / name).exists()]
    if missing:
        print(f'FAIL n21-ts-compile: missing compiled outputs {missing}', file=sys.stderr)
        return 1
    for name in EXPECTED_OUTPUTS:
        path = COMPILED / name
        print(f'compiled src/compiled/{name} ({path.stat().st_size} bytes, sha256={sha256_file(path)[:16]}…)')
    return 0


def check_drift() -> int:
    if not COMPILED.exists():
        print('FAIL n21-ts-drift: src/compiled does not exist; run the compile step', file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        isolated = _write_isolated_project(tmp_dir)
        try:
            proc = run_tsc(isolated)
        finally:
            if isolated.exists():
                isolated.unlink()
        if proc.returncode != 0:
            sys.stderr.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            print('FAIL n21-ts-drift: the TypeScript sources do not compile', file=sys.stderr)
            return 1
        stale: list[str] = []
        for name in EXPECTED_OUTPUTS:
            committed = COMPILED / name
            fresh = tmp_dir / name
            if not committed.exists() or not fresh.exists():
                stale.append(name)
                continue
            if not filecmp.cmp(str(committed), str(fresh), shallow=False):
                stale.append(name)
        if stale:
            print(
                f'FAIL n21-ts-drift: the compiled modules differ from the TypeScript '
                f'sources: {stale}. Run "python3 tools/compile_n21_ts.py" and commit the result.',
                file=sys.stderr,
            )
            return 1
    for name in EXPECTED_OUTPUTS:
        path = COMPILED / name
        print(f'PASS src/compiled/{name} matches its TypeScript source ({path.stat().st_size} bytes)')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify the compiled output is current')
    args = parser.parse_args()
    if args.check:
        return check_drift()
    return compile_in_place()


if __name__ == '__main__':
    raise SystemExit(main())
