#!/usr/bin/env python3
"""N06 design token validator, @layer tokens CSS emitter, and raw-value scanner.

Validates data/tokens.json for:
- Schema integrity and master-precedent metadata
- Theme completeness across light and dark (every required semantic token
  must be present in both; missing tokens fail by exact theme and token name)
- Explicit use_class ('text-classed', 'boundary-classed', 'state-classed') on
  every color_pair entry, plus WCAG AA ratio verification
- Typography floor (rem-based, >= 16px body floor) and target floor (>= 44px)
- Raw-value scan over src/styles.css (zero raw hex/rgb/hsl/oklch color
  literals and zero raw px/rem sizing values outside @layer tokens)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

TOKENS_PATH = 'data/tokens.json'
STYLES_PATH = 'src/styles.css'
VALID_USE_CLASSES = {'text-classed', 'boundary-classed', 'state-classed'}
HEX_COLOR_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b')
COLOR_FN_RE = re.compile(r'\b(?:rgba?|hsla?|oklch|oklab|lab|lch|color)\s*\(', re.IGNORECASE)
RAW_UNIT_RE = re.compile(r'(?<![\w-])\d+(?:\.\d+)?\s*(?:px|rem|em|pt|vh|vw)\b', re.IGNORECASE)


def _srgb_channel(c: int) -> float:
    x = c / 255.0
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * _srgb_channel(r) + 0.7152 * _srgb_channel(g) + 0.0722 * _srgb_channel(b)


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    la = relative_luminance(hex_a)
    lb = relative_luminance(hex_b)
    hi, lo = (la, lb) if la >= lb else (lb, la)
    return (hi + 0.05) / (lo + 0.05)


def emit_tokens_css(tokens: dict[str, Any]) -> str:
    """Emit deterministic @layer tokens CSS from data/tokens.json."""
    light = tokens['themes']['light']
    dark = tokens['themes']['dark']
    print_toks = tokens.get('print_tokens', {})
    lines = ['@layer tokens {', '  :root {', '    color-scheme: light dark;']
    for k in sorted(light.keys()):
        lines.append(f'    {k}: {light[k]};')
    for group in ('typography', 'spacing', 'layout', 'targets'):
        group_tokens = tokens.get(group, {}).get('tokens', {})
        for k in sorted(group_tokens.keys()):
            lines.append(f'    {k}: {group_tokens[k]};')
    for k in sorted(print_toks.keys()):
        lines.append(f'    {k}: {print_toks[k]};')
    lines.append('  }')

    lines.append('  @media (prefers-color-scheme: dark) {')
    lines.append('    :root:not([data-theme="light"]) {')
    for k in sorted(dark.keys()):
        lines.append(f'      {k}: {dark[k]};')
    lines.append('    }')
    lines.append('  }')

    lines.append('  :root[data-theme="dark"] {')
    for k in sorted(dark.keys()):
        lines.append(f'    {k}: {dark[k]};')
    lines.append('  }')

    print_theme = tokens.get('themes', {}).get('print')
    if isinstance(print_theme, dict) and print_theme:
        lines.append('  .theme-print, :root.theme-print {')
        lines.append('    color-scheme: light;')
        for k in sorted(print_theme.keys()):
            lines.append(f'    {k}: {print_theme[k]};')
        lines.append('  }')
        lines.append('  @media print {')
        lines.append('    :root, :root[data-theme="dark"], :root[data-theme="light"], :root:not([data-theme="light"]) {')
        lines.append('      color-scheme: light;')
        for k in sorted(print_theme.keys()):
            lines.append(f'      {k}: {print_theme[k]};')
        lines.append('    }')
        lines.append('  }')

    lines.append('}')
    return '\n'.join(lines)


def scan_raw_values(css_text: str, source_name: str = STYLES_PATH) -> list[dict[str, Any]]:
    """Scan non-token CSS for raw color literals and raw px/rem/em sizing values."""
    findings: list[dict[str, Any]] = []
    # Strip CSS comments cleanly for scanning
    stripped = re.sub(r'/\*[\s\S]*?\*/', '', css_text)
    for lineno, line in enumerate(stripped.splitlines(), start=1):
        # Allow CSS @media queries if any exist, though N06 styles.css uses fluid layout
        if line.strip().startswith('@media'):
            continue
        for m in HEX_COLOR_RE.finditer(line):
            findings.append({
                'source': source_name,
                'line': lineno,
                'kind': 'raw-hex-color',
                'value': m.group(0),
                'context': line.strip(),
            })
        for m in COLOR_FN_RE.finditer(line):
            findings.append({
                'source': source_name,
                'line': lineno,
                'kind': 'raw-color-function',
                'value': m.group(0),
                'context': line.strip(),
            })
        for m in RAW_UNIT_RE.finditer(line):
            findings.append({
                'source': source_name,
                'line': lineno,
                'kind': 'raw-dimension-unit',
                'value': m.group(0),
                'context': line.strip(),
            })
    return findings


def validate_tokens(
    tokens_path: Path | None = None,
    styles_path: Path | None = None,
    repo_root: Path = DEST,
    tokens_data: dict[str, Any] | None = None,
    styles_text: str | None = None,
) -> dict[str, Any]:
    tpath = tokens_path or (repo_root / TOKENS_PATH)
    spath = styles_path or (repo_root / STYLES_PATH)
    data = tokens_data if tokens_data is not None else load_json(tpath)
    css = styles_text if styles_text is not None else spath.read_text(encoding='utf-8')

    errors: list[str] = []
    required = list(data.get('required_semantic_tokens') or [])
    themes = data.get('themes') or {}
    if not required:
        errors.append('tokens.json missing required_semantic_tokens list')
    if 'light' not in themes or 'dark' not in themes:
        errors.append('tokens.json must define both light and dark themes')

    missing_by_theme: dict[str, list[str]] = {}
    for theme_name in ('light', 'dark'):
        theme_map = themes.get(theme_name) or {}
        missing = [tok for tok in required if tok not in theme_map]
        if missing:
            missing_by_theme[theme_name] = missing
            for tok in missing:
                errors.append(f"Missing token '{tok}' in theme '{theme_name}'")
        extra = [tok for tok in theme_map if tok not in required]
        if extra:
            errors.append(f"Undeclared extra tokens in theme '{theme_name}': {', '.join(extra)}")
        for tok, val in theme_map.items():
            if not isinstance(val, str) or not re.fullmatch(r'#[0-9a-fA-F]{6}', val):
                errors.append(f"Invalid hex value for '{tok}' in theme '{theme_name}': {val!r}")

    # Typography and target floors
    typo = data.get('typography') or {}
    if typo.get('floor_px') != 16 or typo.get('unit') != 'rem':
        errors.append(f"Typography floor must be 16px in rem, got {typo.get('floor_px')} / {typo.get('unit')}")
    fs_body = (typo.get('tokens') or {}).get('--fs-body')
    if fs_body != '1rem':
        errors.append(f"--fs-body must equal 1rem (16px floor), got {fs_body!r}")

    targets = data.get('targets') or {}
    if targets.get('floor_px') != 44 or (targets.get('tokens') or {}).get('--target-min') != '2.75rem':
        errors.append('Target floor must be 44px (--target-min: 2.75rem)')

    # Color pairs + use classes + contrast ratios
    pair_results: list[dict[str, Any]] = []
    for pair in data.get('color_pairs') or []:
        pid = pair.get('id', '<unknown>')
        uc = pair.get('use_class')
        fg_tok = pair.get('fg_token')
        bg_tok = pair.get('bg_token')
        min_ratio = float(pair.get('min_ratio', 0))
        if uc not in VALID_USE_CLASSES:
            errors.append(f"Pair '{pid}' has invalid use_class {uc!r}")
            continue
        if uc == 'text-classed' and min_ratio < 4.5:
            errors.append(f"Pair '{pid}' is text-classed but min_ratio {min_ratio} < 4.5")
        if uc in {'boundary-classed', 'state-classed'} and min_ratio < 3.0:
            errors.append(f"Pair '{pid}' is {uc} but min_ratio {min_ratio} < 3.0")

        ratios: dict[str, float] = {}
        for theme_name in ('light', 'dark'):
            theme_map = themes.get(theme_name) or {}
            if fg_tok not in theme_map or bg_tok not in theme_map:
                errors.append(f"Pair '{pid}' references missing token in theme '{theme_name}': {fg_tok} / {bg_tok}")
                continue
            r = round(contrast_ratio(theme_map[fg_tok], theme_map[bg_tok]), 2)
            ratios[theme_name] = r
            if r < min_ratio:
                errors.append(
                    f"Contrast failure in theme '{theme_name}' for '{pid}' ({uc}): {r}:1 < {min_ratio}:1"
                )
        pair_results.append({
            'id': pid,
            'use_class': uc,
            'fg_token': fg_tok,
            'bg_token': bg_tok,
            'min_ratio': min_ratio,
            'ratios': ratios,
        })

    # Raw-value scan over view styles
    raw_findings = scan_raw_values(css, str(spath.relative_to(repo_root)) if spath.is_relative_to(repo_root) else str(spath))
    for f in raw_findings:
        errors.append(f"Raw CSS value '{f['value']}' ({f['kind']}) at {f['source']}:{f['line']}")

    tokens_css = emit_tokens_css(data) if not missing_by_theme else ''
    canonical_digest = sha256_bytes(canonical_json_bytes(data))

    return {
        'schema_version': 1,
        'task': 'N06',
        'status': 'PASS' if not errors else 'FAIL',
        'tokens_digest': canonical_digest,
        'tokens_bytes': len(canonical_json_bytes(data)),
        'styles_bytes': len(css.encode('utf-8')),
        'generated_tokens_css_bytes': len(tokens_css.encode('utf-8')),
        'required_semantic_tokens_count': len(required),
        'themes': sorted(list(themes.keys())),
        'missing_by_theme': missing_by_theme,
        'color_pairs_checked': len(pair_results),
        'color_pairs': pair_results,
        'raw_value_findings_count': len(raw_findings),
        'raw_value_findings': raw_findings,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    return (
        f"tokens {report['status']}: {report['required_semantic_tokens_count']} semantic tokens x "
        f"{len(report['themes'])} themes, {report['color_pairs_checked']} pairs checked, "
        f"{report['raw_value_findings_count']} raw-value findings"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokens', default=str(DEST / TOKENS_PATH))
    parser.add_argument('--styles', default=str(DEST / STYLES_PATH))
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    report = validate_tokens(Path(args.tokens), Path(args.styles), DEST)
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(format_summary(report))
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
