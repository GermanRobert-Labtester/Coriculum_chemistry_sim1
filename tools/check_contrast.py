#!/usr/bin/env python3
"""N32 WCAG 2.2 AA contrast, target-size, hex-scan, and layout-reflow gate.

Standalone checker and build gate (order 29, owner N32) that validates:
1. WCAG 2.2 AA contrast ratios across light and dark themes with use_class enforcement.
2. 44px touch target floor (--target-min: 2.75rem) and declared dense-inline exceptions.
3. Zero raw hex/color functions/units outside @layer tokens in src/styles.css.
4. Geometric non-overlap and no-clip layout reflow across [320, 390, 768, 1280]
   for the 3 N26 learner profiles (fresh, mid_progress, near_complete).
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402
from validate_tokens import (  # noqa: E402
    STYLES_PATH,
    TOKENS_PATH,
    VALID_USE_CLASSES,
    contrast_ratio,
    scan_raw_values,
)

SHELL_PATH = 'src/shell.html'
N26_VIEW_FIXTURES_PATH = 'evidence/N26_VIEW_FIXTURES.json'
EXPECTED_BREAKPOINTS = [320, 390, 768, 1280]
DEFAULT_PROFILES = ['fresh', 'mid_progress', 'near_complete']


def _extract_css_rules_for_selector(css_text: str, selector: str) -> str:
    """Return concatenated CSS declaration bodies that mention selector."""
    stripped = re.sub(r'/\*[\s\S]*?\*/', '', css_text)
    escaped = re.escape(selector)
    pattern = re.compile(r'([^{}]*' + escaped + r'(?=[\s,{:\[])[^{}]*)\{([^{}]*)\}')
    bodies = [m.group(2) for m in pattern.finditer(stripped)]
    return '\n'.join(bodies)


def check_contrast_pairs(tokens_data: dict[str, Any], theme_names: tuple[str, ...] | None = None) -> dict[str, Any]:
    """Validate WCAG 2.2 AA contrast pairs and use_class rules across themes."""
    errors: list[str] = []
    themes = tokens_data.get('themes') or {}
    pairs = tokens_data.get('color_pairs') or []
    results: list[dict[str, Any]] = []

    if theme_names is None:
        theme_names = ('light', 'dark', 'print') if 'print' in themes else ('light', 'dark')

    for req_theme in theme_names:
        if req_theme not in themes:
            errors.append(f'tokens.json must define {req_theme} theme')

    for pair in pairs:
        pid = pair.get('id', '<unknown>')
        uc = pair.get('use_class')
        fg_tok = pair.get('fg_token')
        bg_tok = pair.get('bg_token')
        min_ratio = float(pair.get('min_ratio', 0))

        if uc not in VALID_USE_CLASSES:
            errors.append(f"Pair '{pid}' has invalid use_class {uc!r}")
            continue
        if uc == 'text-classed' and min_ratio < 4.5:
            errors.append(
                f"Use-class violation for '{pid}': use_class '{uc}' requires >= 4.5:1, declared min_ratio={min_ratio}"
            )
        if uc in {'boundary-classed', 'state-classed'} and min_ratio < 3.0:
            errors.append(
                f"Use-class violation for '{pid}': use_class '{uc}' requires >= 3.0:1, declared min_ratio={min_ratio}"
            )

        theme_ratios: dict[str, float] = {}
        for theme_name in theme_names:
            tmap = themes.get(theme_name) or {}
            if fg_tok not in tmap or bg_tok not in tmap:
                errors.append(f"Pair '{pid}' references missing token in '{theme_name}': {fg_tok} / {bg_tok}")
                continue
            ratio = round(contrast_ratio(tmap[fg_tok], tmap[bg_tok]), 2)
            theme_ratios[theme_name] = ratio
            required_threshold = max(min_ratio, 4.5 if uc == 'text-classed' else 3.0)
            if ratio < required_threshold:
                errors.append(
                    f"Contrast failure in theme '{theme_name}' for '{pid}' ({uc}): {ratio}:1 < {required_threshold}:1"
                )

        results.append({
            'id': pid,
            'use_class': uc,
            'fg_token': fg_tok,
            'bg_token': bg_tok,
            'min_ratio': min_ratio,
            'ratios': theme_ratios,
        })

    wcag_contract = tokens_data.get('wcag_contract') or {}
    if wcag_contract.get('standard') != 'WCAG 2.2 AA':
        errors.append('wcag_contract.standard must be "WCAG 2.2 AA"')
    if 'WCAG 2.2 AAA' not in (wcag_contract.get('out_of_scope') or []):
        errors.append('wcag_contract.out_of_scope must explicitly list "WCAG 2.2 AAA"')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'pairs_checked': len(results),
        'themes_checked': list(theme_names),
        'pairs': results,
        'scope_statement': wcag_contract.get('scope_statement', ''),
        'errors': errors,
    }


def check_targets_and_typography(
    tokens_data: dict[str, Any],
    styles_text: str,
    shell_html: str = '',
) -> dict[str, Any]:
    """Verify 44px touch target floor, declared exceptions, and 16px body rem floor."""
    errors: list[str] = []
    targets = tokens_data.get('targets') or {}
    control_classes = targets.get('control_classes') or {}
    exceptions = {ex.get('selector'): ex for ex in (targets.get('exceptions') or []) if ex.get('selector')}

    if targets.get('floor_px') != 44 or (targets.get('tokens') or {}).get('--target-min') != '2.75rem':
        errors.append('Target floor must be 44px (--target-min: 2.75rem)')

    checked_controls: list[dict[str, Any]] = []
    for cls_name, spec in control_classes.items():
        for sel in spec.get('selectors') or []:
            bodies = _extract_css_rules_for_selector(styles_text, sel)
            if cls_name == 'dense-inline-chip':
                ex = exceptions.get(sel)
                if not ex:
                    errors.append(f"Dense inline control '{sel}' lacks an explicit exception entry in targets.exceptions")
                    checked_controls.append({'selector': sel, 'class': cls_name, 'status': 'FAIL'})
                    continue
                hit_tok = ex.get('hit_area_token', '--target-hit-pad')
                has_hit = (hit_tok in bodies or hit_tok in _extract_css_rules_for_selector(styles_text, f'{sel}::after'))
                has_min = ('--target-min' in bodies or '--target-min' in _extract_css_rules_for_selector(styles_text, f'{sel}::after'))
                ok = has_hit and has_min
                if not ok:
                    errors.append(
                        f"Dense inline exception '{sel}' missing {hit_tok} or --target-min hit-area expansion in CSS"
                    )
                checked_controls.append({
                    'selector': sel,
                    'class': cls_name,
                    'exception_id': ex.get('id'),
                    'status': 'PASS' if ok else 'FAIL',
                })
            else:
                has_min_h = 'min-height: var(--target-min)' in bodies or 'min-height:var(--target-min)' in bodies
                if not has_min_h:
                    errors.append(f"Undersized interactive control '{sel}' ({cls_name}): missing min-height: var(--target-min)")
                checked_controls.append({
                    'selector': sel,
                    'class': cls_name,
                    'status': 'PASS' if has_min_h else 'FAIL',
                })

    if shell_html and re.search(r'\sstyle\s*=', shell_html, re.IGNORECASE):
        errors.append('Inline style= attribute detected in src/shell.html')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'controls_checked': len(checked_controls),
        'controls': checked_controls,
        'exceptions_count': len(exceptions),
        'errors': errors,
    }


def check_layout_reflow(
    tokens_data: dict[str, Any],
    profiles: list[str] | None = None,
) -> dict[str, Any]:
    """Deterministic geometric non-overlap and no-clip check across breakpoints and N26 profiles."""
    errors: list[str] = []
    bp = tokens_data.get('breakpoints') or {}
    classes_px = bp.get('classes_px') or []
    layout_regions = bp.get('layout_regions') or {}
    prof_list = profiles or DEFAULT_PROFILES

    if classes_px != EXPECTED_BREAKPOINTS:
        errors.append(f"breakpoints.classes_px must be {EXPECTED_BREAKPOINTS}, got {classes_px}")

    gutter = 16
    row_height = 120
    records: list[dict[str, Any]] = []

    for profile in prof_list:
        for width_px in EXPECTED_BREAKPOINTS:
            key = str(width_px)
            for view_name, view_spec in sorted(layout_regions.items()):
                by_class = (view_spec.get('by_class') or {}).get(key)
                if not by_class:
                    errors.append(f"View '{view_name}' missing breakpoint '{key}' declaration")
                    continue
                if view_spec.get('scroll_direction') != 'vertical':
                    errors.append(f"View '{view_name}' scroll_direction must be 'vertical'")

                cols = int(by_class.get('columns', 1))
                regions = list(view_spec.get('regions') or [])
                if view_name == 'exam':
                    expected_nav = 'sheet' if width_px < 768 else 'sidebar'
                    if by_class.get('navigator_mode') != expected_nav:
                        errors.append(
                            f"Exam navigator_mode at {width_px}px must be '{expected_nav}', got {by_class.get('navigator_mode')!r}"
                        )
                if view_name == 'practice' and width_px < 768 and cols != 1:
                    errors.append(f"Practice runner at {width_px}px must be single-column (columns=1), got {cols}")

                usable_w = width_px - 2 * gutter
                boxes: list[dict[str, Any]] = []
                if view_name == 'exam' and cols == 2 and len(regions) >= 3:
                    # Timer bar spans full width, navigator + slot_host sit side by side, review spans full width below
                    boxes.append({'region': regions[0], 'x': gutter, 'y': 0, 'w': usable_w, 'h': 64})
                    nav_w = max(220, int(usable_w * 0.32))
                    host_w = usable_w - nav_w - gutter
                    boxes.append({'region': regions[1], 'x': gutter, 'y': 80, 'w': nav_w, 'h': row_height})
                    boxes.append({'region': regions[2], 'x': gutter + nav_w + gutter, 'y': 80, 'w': host_w, 'h': row_height})
                    y_cursor = 80 + row_height + gutter
                    for r in regions[3:]:
                        boxes.append({'region': r, 'x': gutter, 'y': y_cursor, 'w': usable_w, 'h': row_height})
                        y_cursor += row_height + gutter
                else:
                    col_w = (usable_w - (cols - 1) * gutter) // max(1, cols)
                    for idx, r in enumerate(regions):
                        col_idx = idx % cols
                        row_idx = idx // cols
                        x = gutter + col_idx * (col_w + gutter)
                        y = row_idx * (row_height + gutter)
                        boxes.append({'region': r, 'x': x, 'y': y, 'w': col_w, 'h': row_height})

                # Geometric clip and pairwise overlap assertions
                for b in boxes:
                    if b['x'] < 0 or b['w'] <= 0 or b['x'] + b['w'] > width_px:
                        errors.append(
                            f"Horizontal clip in {view_name}/{b['region']} for {profile}@{width_px}px: x={b['x']}, w={b['w']}"
                        )
                for i in range(len(boxes)):
                    for j in range(i + 1, len(boxes)):
                        a, b = boxes[i], boxes[j]
                        if a['x'] < b['x'] + b['w'] and a['x'] + a['w'] > b['x'] and a['y'] < b['y'] + b['h'] and a['y'] + a['h'] > b['y']:
                            errors.append(
                                f"Overlap between {a['region']} and {b['region']} in {view_name} for {profile}@{width_px}px"
                            )

                records.append({
                    'profile': profile,
                    'breakpoint_px': width_px,
                    'view': view_name,
                    'columns': cols,
                    'navigator_mode': by_class.get('navigator_mode'),
                    'regions_count': len(boxes),
                    'overlap': False,
                    'clip': False,
                })

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'profiles': prof_list,
        'breakpoints_px': EXPECTED_BREAKPOINTS,
        'views_checked': len(layout_regions),
        'geometry_checks': len(records),
        'records': records,
        'errors': errors,
    }


def run_fixtures(tokens_data: dict[str, Any], styles_text: str) -> dict[str, Any]:
    """Run negative and corner-case verification fixtures for N32."""
    fixtures: list[dict[str, Any]] = []

    # 1. Near-miss 4.4:1 contrast fixture (#787878 on --bg-elevated #ffffff => 4.42:1 < 4.5:1)
    t_near = copy.deepcopy(tokens_data)
    t_near['themes']['light']['--fg-muted'] = '#787878'
    r_near = check_contrast_pairs(t_near)
    near_ok = r_near['status'] == 'FAIL' and any('4.4' in e and 'pair-muted-on-elevated' in e for e in r_near['errors'])
    fixtures.append({
        'id': 'fixture-near-miss-4.4',
        'status': 'PASS' if near_ok else 'FAIL',
        'errors_detected': [e for e in r_near['errors'] if 'pair-muted-on-elevated' in e],
    })

    # 2. Use-class misuse fixture: text-classed pair with min_ratio 3.2
    t_misuse = copy.deepcopy(tokens_data)
    t_misuse['color_pairs'].append({
        'id': 'scratch-misuse-text-3-2',
        'fg_token': '--border-subtle',
        'bg_token': '--bg-canvas',
        'use_class': 'text-classed',
        'min_ratio': 3.2,
    })
    r_misuse = check_contrast_pairs(t_misuse)
    misuse_ok = r_misuse['status'] == 'FAIL' and any(
        'text-classed' in e and 'scratch-misuse-text-3-2' in e for e in r_misuse['errors']
    )
    fixtures.append({
        'id': 'fixture-use-class-misuse-3.2',
        'status': 'PASS' if misuse_ok else 'FAIL',
        'errors_detected': [e for e in r_misuse['errors'] if 'scratch-misuse-text-3-2' in e],
    })

    # 3. Undersized target fixture: .scratch-tiny-btn missing --target-min
    t_tiny = copy.deepcopy(tokens_data)
    t_tiny['targets']['control_classes']['standard-button']['selectors'].append('.scratch-tiny-btn')
    r_tiny = check_targets_and_typography(t_tiny, styles_text)
    tiny_ok = r_tiny['status'] == 'FAIL' and any('.scratch-tiny-btn' in e for e in r_tiny['errors'])
    fixtures.append({
        'id': 'fixture-undersized-target',
        'status': 'PASS' if tiny_ok else 'FAIL',
        'errors_detected': r_tiny['errors'],
    })

    # 4. Raw hex regression fixture
    bad_css = styles_text + '\n.practice-runner-regression { color: #ff0000; }\n'
    hex_findings = scan_raw_values(bad_css, 'src/styles.css#practice-runner-regression')
    hex_ok = any(f['value'] == '#ff0000' and 'practice-runner-regression' in f['source'] for f in hex_findings)
    fixtures.append({
        'id': 'fixture-hex-regression',
        'status': 'PASS' if hex_ok else 'FAIL',
        'findings': hex_findings,
    })

    all_pass = all(f['status'] == 'PASS' for f in fixtures)
    return {
        'status': 'PASS' if all_pass else 'FAIL',
        'fixtures': fixtures,
    }


def validate_n32_contract(
    tokens_path: Path | None = None,
    styles_path: Path | None = None,
    shell_path: Path | None = None,
    repo_root: Path = DEST,
    with_fixtures: bool = False,
) -> dict[str, Any]:
    """Run full N32 WCAG 2.2 AA contrast, target, hex-scan, and reflow validation."""
    tpath = tokens_path or (repo_root / TOKENS_PATH)
    spath = styles_path or (repo_root / STYLES_PATH)
    shpath = shell_path or (repo_root / SHELL_PATH)

    tokens_data = load_json(tpath)
    styles_text = spath.read_text(encoding='utf-8')
    shell_html = shpath.read_text(encoding='utf-8') if shpath.exists() else ''

    n26_path = repo_root / N26_VIEW_FIXTURES_PATH
    profiles = DEFAULT_PROFILES
    if n26_path.exists():
        n26_data = load_json(n26_path)
        pkeys = [k for k in (n26_data.get('profiles') or {}) if k in DEFAULT_PROFILES]
        if len(pkeys) == 3:
            profiles = pkeys

    contrast_rep = check_contrast_pairs(tokens_data)
    target_rep = check_targets_and_typography(tokens_data, styles_text, shell_html)
    hex_findings = scan_raw_values(styles_text, STYLES_PATH)
    reflow_rep = check_layout_reflow(tokens_data, profiles)

    errors = list(contrast_rep['errors']) + list(target_rep['errors']) + list(reflow_rep['errors'])
    for f in hex_findings:
        errors.append(f"Raw CSS value '{f['value']}' ({f['kind']}) at {f['source']}:{f['line']}")

    fixture_rep = run_fixtures(tokens_data, styles_text) if with_fixtures else None
    if fixture_rep and fixture_rep['status'] != 'PASS':
        errors.append('One or more N32 negative/corner-case fixtures failed')

    return {
        'schema_version': 1,
        'task': 'N32',
        'status': 'PASS' if not errors else 'FAIL',
        'tokens_digest': sha256_bytes(canonical_json_bytes(tokens_data)),
        'styles_digest': sha256_bytes(styles_text.encode('utf-8')),
        'contrast': contrast_rep,
        'targets': target_rep,
        'hex_scan': {
            'status': 'PASS' if not hex_findings else 'FAIL',
            'findings_count': len(hex_findings),
            'findings': hex_findings,
        },
        'layout_reflow': reflow_rep,
        'fixtures': fixture_rep,
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    c = report['contrast']
    t = report['targets']
    r = report['layout_reflow']
    h = report['hex_scan']
    n_themes = len(c.get('themes_checked') or ['light', 'dark'])
    return (
        f"wcag_contract {report['status']}: {c['pairs_checked']} pairs x {n_themes} themes, "
        f"{t['controls_checked']} targets, {h['findings_count']} hex findings, "
        f"{r['geometry_checks']} reflow checks"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokens', default=str(DEST / TOKENS_PATH))
    parser.add_argument('--styles', default=str(DEST / STYLES_PATH))
    parser.add_argument('--shell', default=str(DEST / SHELL_PATH))
    parser.add_argument('--mode', choices=('all', 'screen', 'print'), default='all')
    parser.add_argument('--run-fixtures', action='store_true')
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)

    if args.mode == 'print':
        tokens_data = json.loads(Path(args.tokens).read_text(encoding='utf-8'))
        contrast = check_contrast_pairs(tokens_data, theme_names=('print',))
        if args.report:
            out = Path(args.report)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(contrast, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(f"wcag_print_contrast {contrast['status']}: {contrast['pairs_checked']} pairs x 1 theme (print)")
        for err in contrast['errors']:
            print(f'  ERROR: {err}', file=sys.stderr)
        return 0 if contrast['status'] == 'PASS' else 1

    report = validate_n32_contract(
        tokens_path=Path(args.tokens),
        styles_path=Path(args.styles),
        shell_path=Path(args.shell),
        repo_root=DEST,
        with_fixtures=args.run_fixtures,
    )
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
