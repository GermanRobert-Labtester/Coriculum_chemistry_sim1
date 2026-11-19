#!/usr/bin/env python3
"""N16 chain corpus: validation, recompute/citation tables, runtime digests,
leak scans, focus traces, print renders, byte accounting and parity.

Run: python3 tools/n16_corpus.py
     python3 tools/n16_corpus.py --skip-print --out /tmp/opencode/n16_second.json
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes, sha256_file  # noqa: E402
from validate_chains import (  # noqa: E402
    CHAINS_PATH, BANNER, build_runtime_projection, pre_reveal_fixture,
    unseal_payload, validate_chains,
)
from validate_n06_shell import validate_shell  # noqa: E402

ROOT = DEST
OUT = ROOT / 'evidence'
HARNESS = ROOT / 'tools' / 'check_n16_runtime.js'
BUILD_MANIFEST = ROOT / 'output' / 'build-manifest.json'
ARTIFACT = ROOT / 'output' / 'simulator.html'


def _style_block(html: str) -> str:
    m = re.search(r'<style>([\s\S]*?)</style>', html)
    if not m:
        raise SystemExit('no <style> block in artifact')
    return m.group(1)


def _esc(text) -> str:
    return (str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


FIG_SCRIPT = r"""
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('output/simulator.html', 'utf8');
function island(id) {
  const re = new RegExp('<script[^>]*id="' + id + '"[^>]*>([\\s\\S]*?)<\\/script>');
  const m = html.match(re);
  if (!m) throw new Error('missing island ' + id);
  return m[1];
}
const sb = { console, JSON, Error, String, Object, Array, Math, Number, Boolean, RegExp };
sb.globalThis = sb; vm.createContext(sb);
vm.runInContext(fs.readFileSync('src/terms-loader.js', 'utf8'), sb);
vm.runInContext(fs.readFileSync('src/figure-framework.js', 'utf8'), sb);
const termsData = JSON.parse(island('sim-terms'));
const terms = sb.SimTerms.load({ getElementById(id) {
  return id === 'sim-terms' ? { textContent: JSON.stringify(termsData) } : null;
} });
const rec = JSON.parse(island('sim-figures')).figures.find((f) => f.id === process.argv[1]);
if (!rec) throw new Error('unknown figure ' + process.argv[1]);
const cite = rec.citations || {};
process.stdout.write(JSON.stringify({
  id: rec.id, epistemic: rec.epistemic_label, anchor: cite.master_anchor || '',
  tolerance: rec.tolerance_coupling ? rec.tolerance_coupling.tolerance_class : null,
  svg: sb.SimFigures.renderFigureSvg(rec, { terms: terms, theme: 'print' })
}));
"""
_FIGURE_CACHE: dict[str, dict] = {}


def figure_info(figure_id: str) -> dict:
    if figure_id not in _FIGURE_CACHE:
        proc = subprocess.run(['node', '-e', FIG_SCRIPT, figure_id], cwd=str(ROOT),
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit('figure render failed for ' + figure_id + ': ' + (proc.stderr or '').strip()[:300])
        _FIGURE_CACHE[figure_id] = json.loads(proc.stdout)
    return _FIGURE_CACHE[figure_id]


def figure_card(figure_id: str) -> str:
    info = figure_info(figure_id)
    tol = (' · Tolerance (' + info['tolerance'] + ', PROPOSED)') if info.get('tolerance') else \
        ' · Strukturāla shēma (bez mērījuma tolerances)'
    caption = info['id'] + ' · ' + info['epistemic'] + ' · #' + info['anchor'] + tol
    return ('<figure class="fig-card" data-figure-id="' + _esc(figure_id) +
            '" data-lazy-state="rendered">' + info['svg'] + '<p class="fig-caption">' +
            _esc(caption) + '</p></figure>')


def revealed_fixture(projection: dict, chain_id: str) -> str:
    chain = next(c for c in projection['chains'] if c['id'] == chain_id)
    parts = ['<article class="chain" data-chain-id="' + _esc(chain_id) + '" data-revealed-count="' +
             str(len(chain['steps'])) + '" data-revealed-all="true">']
    parts.append('<p class="chain-banner">' + _esc(chain['banner_lv']) + '</p>')
    parts.append('<h3 class="chain-title">' + _esc(chain['title_lv']) + '</h3>')
    parts.append('<p class="chain-subtitle">' + _esc(chain['subtitle_lv']) + '</p>')
    mc = chain.get('master_citation') or {}
    parts.append('<p class="chain-citation">' + _esc(mc.get('heading_lv', '')) + ' <code>' +
                 _esc(mc.get('anchor', '')) + '</code></p>')
    parts.append('<dl class="chain-givens">')
    for g in chain.get('givens', []):
        if g.get('kind') == 'points':
            continue
        parts.append('<div class="chain-given"><dt>' + _esc(g['label_lv']) + '</dt><dd>' +
                     _esc(g['display_lv']) + ' ' + _esc(g['unit']) + '</dd></div>')
    parts.append('</dl><ol class="chain-steps">')
    for st in chain['steps']:
        payload = unseal_payload(chain_id, st['step_id'], st['sealed'])
        parts.append('<li class="chain-step" data-step-id="' + _esc(st['step_id']) + '" data-revealed="true">')
        parts.append('<p class="chain-step-quantity">' + _esc(st['quantity_lv']) + '</p>')
        parts.append('<p class="chain-step-statement">' + _esc(st['statement_lv']) + '</p>')
        for fr in chain.get('figure_refs', []):
            if fr.get('step_id') == st['step_id']:
                parts.append('<div class="chain-figure-host" data-figure-state="mounted">' +
                             figure_card(fr['figure_id']) + '</div>')
        parts.append('<div class="chain-result"><p class="chain-result-value">' +
                     _esc(str(payload.get('display_lv') or payload.get('value') or '') + ' ' +
                          str(payload.get('unit') or '')) + '</p>')
        parts.append('<p class="chain-result-reasoning">' + _esc(payload.get('reasoning_lv') or '') + '</p></div>')
        parts.append('</li>')
    parts.append('</ol>')
    parts.append('<p class="chain-print-note chain-print-note-collapsed">Pamatojums ir interaktīvs; '
                 'drukātajā versijā atklājiet soļus pirms drukāšanas.</p>')
    parts.append('</article>')
    return '\n'.join(parts)


def write_print_fixture(name: str, chain_html: str, css: str) -> Path:
    path = Path('/tmp/opencode') / name
    path.parent.mkdir(parents=True, exist_ok=True)
    html = ('<!doctype html><html lang="lv" data-theme="light"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<style>' + css + '</style></head><body><main class="sim-main">' + chain_html + '</main></body></html>')
    path.write_text(html, encoding='utf-8')
    return path


def render_print(name: str, html_path: Path, png_path: Path) -> dict:
    cmd = ['lite-shot', '--cdp', '--theme', 'light', '--media', 'print', '--full-page',
           '-g', '800x1100', str(html_path), str(png_path)]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    ok = proc.returncode == 0 and png_path.exists() and png_path.stat().st_size > 0
    return {
        'name': name,
        'command': ' '.join(cmd),
        'returncode': proc.returncode,
        'stderr': (proc.stderr or '').strip()[:400],
        'png': str(png_path.relative_to(ROOT)) if png_path.is_relative_to(ROOT) else str(png_path),
        'bytes': png_path.stat().st_size if png_path.exists() else 0,
        'sha256': sha256_file(png_path) if png_path.exists() else None,
        'status': 'PASS' if ok else 'UNVERIFIED',
    }


def scratch_recompute() -> dict:
    """Run the real validator on a copied EX03/S2 with a wrong declared value."""
    data = load_json(ROOT / CHAINS_PATH)
    scratch = copy.deepcopy(data)
    chain = next(c for c in scratch['chains'] if c['id'] == 'EX03')
    step = next(s for s in chain['steps'] if s['step_id'] == 'S2')
    step['result']['value'] = '326'
    step['result']['display_lv'] = '326'
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / 'chains_scratch.json'
        path.write_text(json.dumps(scratch, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        report = validate_chains(repo_root=ROOT, chains_path=path)
    matched = [e for e in report.get('errors', []) if 'EX03/S2: recompute mismatch' in e]
    return {
        'status': 'PASS' if report.get('status') == 'FAIL' and matched else 'FAIL',
        'report_status': report.get('status'),
        'matched_errors': matched[:2],
        'errors': report.get('errors', [])[:5],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-print', action='store_true')
    parser.add_argument('--out', default=str(OUT / 'N16_CORPUS_RECORD.json'))
    args = parser.parse_args(argv)

    chains_data = load_json(ROOT / CHAINS_PATH)
    projection = build_runtime_projection(chains_data)
    report = validate_chains(repo_root=ROOT)
    if report['status'] != 'PASS':
        print('FAIL chains validation:', report['errors'][:5], file=sys.stderr)
        return 1

    # Runtime harness
    proc = subprocess.run(['node', str(HARNESS)], cwd=str(ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        print('FAIL runtime harness:', (proc.stderr or '').strip()[:800], file=sys.stderr)
        return 1
    runtime = json.loads(proc.stdout)

    # Two-run validation parity (the runtime harness already runs the chain walk twice).
    report2 = validate_chains(repo_root=ROOT)
    validation_parity = sha256_bytes(canonical_json_bytes(report)) == sha256_bytes(canonical_json_bytes(report2))

    # Byte accounting from the built artifact
    html = ARTIFACT.read_text(encoding='utf-8')
    shell_report = validate_shell(html_text=html, repo_root=ROOT)
    manifest = load_json(BUILD_MANIFEST)
    renderer_bytes = len(subprocess.run(
        [sys.executable, '-c',
         'import sys;sys.path.insert(0,"tools");from tools.build import compact_js_source;'
         'print(compact_js_source(open("src/chain-view.js",encoding="utf-8").read()),end="")'],
        cwd=str(ROOT), capture_output=True, text=True).stdout.encode('utf-8'))

    # Print fixtures and renders
    css = _style_block(html)
    print_rows = []
    if not args.skip_print:
        collapsed = pre_reveal_fixture(projection, only_chain='EX03')
        revealed = revealed_fixture(projection, 'EX03')
        cpath = write_print_fixture('n16_print_collapsed.html', collapsed, css)
        rpath = write_print_fixture('n16_print_revealed.html', revealed, css)
        print_rows.append(render_print('collapsed', cpath, OUT / 'N16_PRINT_COLLAPSED.png'))
        print_rows.append(render_print('revealed', rpath, OUT / 'N16_PRINT_REVEALED.png'))
    else:
        for name, png in (('collapsed', OUT / 'N16_PRINT_COLLAPSED.png'),
                          ('revealed', OUT / 'N16_PRINT_REVEALED.png')):
            print_rows.append({
                'name': name, 'png': str(png.relative_to(ROOT)) if png.is_relative_to(ROOT) else str(png),
                'bytes': png.stat().st_size if png.exists() else 0,
                'sha256': sha256_file(png) if png.exists() else None,
                'status': 'PASS' if png.exists() else 'UNVERIFIED',
                'command': 'reused existing render (--skip-print)',
            })

    # Per-chain leak scan summary (from the validator report)
    leak_rows = []
    for chain in report['chains']:
        cid = chain['id']
        pre = [v for v in report['leaks']['pre_reveal'] if v['chain_id'] == cid]
        isl = [v for v in report['leaks']['island'] if v['chain_id'] == cid]
        leak_rows.append({'chain_id': cid, 'pre_reveal_leaks': len(pre), 'island_leaks': len(isl),
                          'status': 'PASS' if not pre and not isl else 'FAIL'})

    # Cross-reference table
    ref_rows = report['references']['rows']
    ref_table = [
        {
            'kind': r['kind'], 'id': r['id'], 'consumer': r['consumer'],
            'chain_ids': r['chain_ids'], 'family_id': r['family_id'], 'status': r['status'],
        }
        for r in ref_rows
    ]

    scratch = scratch_recompute()
    record = {
        'schema_version': 1,
        'task': 'N16',
        'status': 'PASS' if (report['status'] == 'PASS' and runtime['status'] == 'PASS'
                             and scratch['status'] == 'PASS'
                             and all(p['status'] == 'PASS' for p in print_rows)) else 'FAIL',
        'banner_lv': BANNER,
        'summary': report['summary'],
        'validation_parity': validation_parity,
        'runtime': runtime,
        'recompute': report['recompute'],
        'negative_recompute': report.get('negative_recompute'),
        'scratch_recompute': scratch,
        'citations': report['citations'],
        'figures': report['figures'],
        'references': ref_table,
        'leaks': {
            'per_chain': leak_rows,
            'pre_reveal': report['leaks']['pre_reveal'],
            'island': report['leaks']['island'],
            'planted': report['leaks']['planted'],
            'item_context': runtime.get('item_context'),
        },
        'persistence': report.get('persistence'),
        'print': print_rows,
        'bytes': {
            'chains_island': manifest.get('chains_island', {}).get('bytes'),
            'chains_island_digest': manifest.get('chains_island', {}).get('digest'),
            'chain_renderer_compacted': renderer_bytes,
            'runtime_js_code_bytes': shell_report['byte_accounting']['runtime_js_code_bytes'],
            'runtime_js_ceiling_bytes': shell_report['byte_accounting']['runtime_js_ceiling_bytes'],
            'runtime_js_headroom': shell_report['byte_accounting']['runtime_js_ceiling_bytes'] - shell_report['byte_accounting']['runtime_js_code_bytes'],
            'artifact_bytes': manifest['output_bytes'],
            'artifact_sha256': manifest['output_sha256'],
            'build_id': manifest['build_id'],
            'html_bytes': len(html.encode('utf-8')),
        },
        'smoke': runtime.get('smoke'),
        'smoke_summary': runtime.get('smoke_summary'),
        'handoff': {
            'n19': 'data/chain_references.json method card forward contract',
            'n20': 'data/chain_references.json practice item forward contract',
            'n29': 'SimChains.mountChain / openFromLink',
            'n34': 'print rules data-revealed-count / data-revealed-all',
        },
    }
    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({
        'status': record['status'], 'out': str(out), 'bytes': out.stat().st_size,
        'sha256': sha256_file(out), 'validation_parity': validation_parity,
        'runtime': runtime['status'], 'print': [p['status'] for p in print_rows],
        'recompute': f"{report['summary']['recompute_pass']}/{report['summary']['recompute_pass'] + report['summary']['recompute_fail']}",
        'scratch_recompute': scratch['status'],
        'leaks': f"{len(report['leaks']['pre_reveal'])}+{len(report['leaks']['island'])}",
        'planted': report['leaks']['planted']['status'],
        'runtime_js': shell_report['byte_accounting']['runtime_js_code_bytes'],
        'chains_island': manifest.get('chains_island', {}).get('bytes'),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
