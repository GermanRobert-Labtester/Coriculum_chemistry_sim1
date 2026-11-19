#!/usr/bin/env python3
"""N06 structural contract, ARIA foundation, copy lint, and byte-budget validator.

Checks output/simulator.html (or a supplied HTML string/path) for:
- Structural contract (N31 precursor): lang="lv", 1 executable <script>,
  10 declared JSON islands in order (N02-N17), 9 unique ASCII blueprint anchors,
  ASCII-only unique id namespace (V-10), internal href="#..." resolution,
  and zero external URLs (http://, https://).
- ARIA foundations (N22/N33 precursor): 1 <main>, named <nav> landmarks,
  9 named <section> landmarks via aria-labelledby, valid heading hierarchy
  (1 <h1>, no level skips), and accessible #theme-toggle button.
- Copy lint (Section 1.5 split + AGENTS.md + N10 stub pass): official panel
  matches programme facts; training-policy panel carries PROPOSED labels;
  scope note states offline/non-official/in-memory bounds; zero endorsement
  or certification claims; N10 term-bank stub manifest checked.
- Section 1.3 byte accounting: CSS, runtime JS, JSON islands, template bytes.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import byte_budget  # noqa: E402
from coverage_common import DEST, load_json, sha256_bytes  # noqa: E402

BLUEPRINT_ANCHORS = [
    'sakums', 'saturs', 'piemeri', 'prakse', 'eksamens', 'rezultati',
    'atskats', 'metodika', 'druka', 'iestatijumi',
]
DECLARED_ISLANDS_ORDER = [
    'sim-coverage',
    'sim-conventions',
    'sim-bank',
    'sim-forms',
    'sim-golden-vectors',
    'sim-terms',
    'sim-analytics',
    'sim-mastery-policy',
    'sim-scheduler-policy',
    'sim-remediation-policy',
    'sim-revision-policy',
    'sim-practice-policy',
    'sim-figures',
    'sim-chains',
    'sim-engines',
    'sim-graph-scoring',
    'sim-method-cards',
    'sim-method-engine',
    'sim-exam-policy',
    'sim-response-types',
    'sim-grading-policy',
    'sim-feedback-classification',
]
ASCII_ID_RE = re.compile(r'^[A-Za-z][A-Za-z0-9._:-]*$')
EXTERNAL_URL_RE = re.compile(r'(?:https?:)?//[^\s"\'<>)]+', re.IGNORECASE)
FORBIDDEN_ENDORSEMENT_RE = re.compile(
    r'\b(?:sertifik[aā]t\w*|akredit[eē]t\w*|ofici[aā]li\s+apstiprin\w*|garant[eē]\w*|lab[aā]k[aā]is|ofici[aā]l[aā]\s+atz[iī]me)\b',
    re.IGNORECASE,
)


class _ShellParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.html_lang: str | None = None
        self.ids: list[str] = []
        self.duplicate_ids: list[str] = []
        self.non_ascii_ids: list[str] = []
        self.links: list[dict[str, str]] = []
        self.scripts: list[dict[str, Any]] = []
        self.styles: list[str] = []
        self.mains: int = 0
        self.headers: int = 0
        self.footers: int = 0
        self.navs: list[dict[str, Any]] = []
        self.sections: list[dict[str, Any]] = []
        self.headings: list[dict[str, Any]] = []
        self.theme_toggle: dict[str, str] | None = None
        self.region_text: dict[str, list[str]] = {}

        self._seen_ids: set[str] = set()
        self._stack: list[tuple[str, str | None]] = []
        self._in_script: dict[str, Any] | None = None
        self._in_style: list[str] | None = None
        self._in_heading: dict[str, Any] | None = None
        self._tracked_regions = {
            'sakums-oficiali-fakti',
            'sakums-politika',
            'sakums-tverums',
            'iestatijumi',
            'sakums',
            'saturs',
        }

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v if v is not None else '') for k, v in attrs}
        el_id = attr_map.get('id')
        if tag == 'html':
            self.html_lang = attr_map.get('lang')
        if el_id is not None:
            if el_id in self._seen_ids:
                self.duplicate_ids.append(el_id)
            self._seen_ids.add(el_id)
            self.ids.append(el_id)
            if not ASCII_ID_RE.match(el_id):
                self.non_ascii_ids.append(el_id)
            if el_id == 'theme-toggle':
                self.theme_toggle = {'tag': tag, **attr_map}
        if tag == 'a' and 'href' in attr_map:
            self.links.append({'href': attr_map['href'], 'id': el_id or ''})
        if tag == 'main':
            self.mains += 1
        elif tag == 'header':
            self.headers += 1
        elif tag == 'footer':
            self.footers += 1
        elif tag == 'nav':
            self.navs.append({
                'id': el_id or '',
                'aria_label': attr_map.get('aria-label', ''),
                'aria_labelledby': attr_map.get('aria-labelledby', ''),
            })
        elif tag == 'section':
            self.sections.append({
                'id': el_id or '',
                'aria_labelledby': attr_map.get('aria-labelledby', ''),
            })
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._in_heading = {'level': int(tag[1]), 'id': el_id or '', 'text': []}
        elif tag == 'script':
            self._in_script = {
                'id': el_id or '',
                'type': attr_map.get('type', ''),
                'src': attr_map.get('src', ''),
                'chunks': [],
            }
        elif tag == 'style':
            self._in_style = []

        active_region = el_id if el_id in self._tracked_regions else None
        self._stack.append((tag, active_region))

    def handle_endtag(self, tag: str) -> None:
        if tag == 'script' and self._in_script is not None:
            body = ''.join(self._in_script['chunks'])
            self.scripts.append({
                'id': self._in_script['id'],
                'type': self._in_script['type'],
                'src': self._in_script['src'],
                'bytes': len(body.encode('utf-8')),
                'text': body,
            })
            self._in_script = None
        elif tag == 'style' and self._in_style is not None:
            self.styles.append(''.join(self._in_style))
            self._in_style = None
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6') and self._in_heading is not None:
            self.headings.append({
                'level': self._in_heading['level'],
                'id': self._in_heading['id'],
                'text': ''.join(self._in_heading['text']).strip(),
            })
            self._in_heading = None

        for idx in range(len(self._stack) - 1, -1, -1):
            if self._stack[idx][0] == tag:
                del self._stack[idx:]
                break

    def handle_data(self, data: str) -> None:
        if self._in_script is not None:
            self._in_script['chunks'].append(data)
            return
        if self._in_style is not None:
            self._in_style.append(data)
            return
        if self._in_heading is not None:
            self._in_heading['text'].append(data)
        for _tag, region in self._stack:
            if region is not None:
                self.region_text.setdefault(region, []).append(data)


def scan_external_urls(html_text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for lineno, line in enumerate(html_text.splitlines(), start=1):
        for m in EXTERNAL_URL_RE.finditer(line):
            url = m.group(0)
            # Ignore JS regex literal like /.../g or CSS comments if no scheme
            if not url.lower().startswith(('http://', 'https://')):
                continue
            findings.append({'line': lineno, 'url': url, 'context': line.strip()[:160]})
    return findings


def check_copy_lint(parser: _ShellParser, stubs_data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    sakums_text = ' '.join(parser.region_text.get('sakums', []))
    official_text = ' '.join(parser.region_text.get('sakums-oficiali-fakti', []))
    proposed_text = ' '.join(parser.region_text.get('sakums-politika', []))
    scope_text = ' '.join(parser.region_text.get('sakums-tverums', []))
    settings_text = ' '.join(parser.region_text.get('iestatijumi', []))

    # Official facts checks (Section 1.5)
    for required_needle in ('RSU_MedChem_Colloq1_Prog_LV_2025.pdf', 'uz papīra', '180 minūtes', 'Septiņas programmas tēmas'):
        if required_needle not in official_text:
            errors.append(f"Official panel missing programme fact {required_needle!r}")

    # Training-policy panel checks (Section 1.5)
    for required_needle in ('PROPOSED', '100 treniņa punkti', 'A, B un C', '21 uzdevuma', '64 mācību rezultāti', '28 uzdevumu saimes'):
        if required_needle not in proposed_text:
            errors.append(f"Proposed policy panel missing required claim/label {required_needle!r}")

    # Scope note checks (AGENTS.md)
    for required_needle in ('nav oficiāls', 'bezsaist', 'operatīvajā atmiņā'):
        if required_needle not in scope_text:
            errors.append(f"Scope note missing AGENTS.md honesty statement {required_needle!r}")

    # Settings scaffold deferrals
    if 'N25' not in settings_text or 'localStorage' not in settings_text:
        errors.append('Settings scaffold missing N25 localStorage deferral notice')
    if 'N34' not in settings_text:
        errors.append('Settings scaffold missing N34 print deferral notice')

    # Forbidden endorsement / certification words anywhere in visible text
    all_visible = ' '.join([sakums_text, settings_text])
    for m in FORBIDDEN_ENDORSEMENT_RE.finditer(all_visible):
        errors.append(f"Forbidden endorsement/certification term found: {m.group(0)!r}")
    for m in re.finditer(r'\bofici[aā]ls\s+eks[aā]mens\b', all_visible, re.IGNORECASE):
        prefix = all_visible[max(0, m.start() - 15):m.start()].lower()
        if 'nav' not in prefix:
            errors.append(f"Unnegated 'oficiāls eksāmens' claim found near: {all_visible[max(0, m.start()-20):m.end()+20]!r}")

    # N10 stub closure manifest check
    stub_keys = stubs_data.get('keys') or []
    if stubs_data.get('target_closure_task') != 'N10' or len(stub_keys) == 0:
        errors.append('N06 term stub manifest missing target_closure_task=N10 or keys')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'official_panel_text_lv': ' '.join(official_text.split()),
        'proposed_panel_text_lv': ' '.join(proposed_text.split()),
        'scope_note_text_lv': ' '.join(scope_text.split()),
        'n10_stub_keys_count': len(stub_keys),
        'n10_dependency_status': stubs_data.get('status', 'stub-pending-N10'),
        'errors': errors,
    }


def check_aria(parser: _ShellParser) -> dict[str, Any]:
    errors: list[str] = []
    if parser.mains != 1:
        errors.append(f"Expected exactly 1 <main> landmark, found {parser.mains}")
    if parser.headers < 1:
        errors.append('Missing <header> banner landmark')
    if parser.footers < 1:
        errors.append('Missing <footer> contentinfo landmark')

    id_set = set(parser.ids)
    for nav in parser.navs:
        if not nav['aria_label'] and not nav['aria_labelledby']:
            errors.append(f"<nav id={nav['id']!r}> missing accessible name (aria-label / aria-labelledby)")

    section_map = {s['id']: s for s in parser.sections}
    for anchor in BLUEPRINT_ANCHORS:
        sec = section_map.get(anchor)
        if not sec:
            errors.append(f"Missing <section id={anchor!r}> landmark")
            continue
        lbl = sec['aria_labelledby']
        if not lbl or lbl not in id_set:
            errors.append(f"<section id={anchor!r}> aria-labelledby={lbl!r} does not resolve")

    h1_count = sum(1 for h in parser.headings if h['level'] == 1)
    if h1_count != 1:
        errors.append(f"Expected exactly 1 <h1>, found {h1_count}")
    prev_level = 0
    for h in parser.headings:
        lvl = h['level']
        if prev_level > 0 and lvl > prev_level + 1:
            errors.append(f"Heading level skip from h{prev_level} to h{lvl} ({h['text']!r})")
        prev_level = lvl

    if not parser.theme_toggle:
        errors.append('Missing #theme-toggle control')
    else:
        if parser.theme_toggle.get('tag') != 'button':
            errors.append(f"#theme-toggle must be <button>, got <{parser.theme_toggle.get('tag')}>")
        if 'aria-pressed' not in parser.theme_toggle:
            errors.append('#theme-toggle missing aria-pressed attribute')

    return {
        'status': 'PASS' if not errors else 'FAIL',
        'mains': parser.mains,
        'headers': parser.headers,
        'footers': parser.footers,
        'nav_count': len(parser.navs),
        'section_landmarks': len(BLUEPRINT_ANCHORS),
        'headings_count': len(parser.headings),
        'h1_count': h1_count,
        'errors': errors,
    }


def validate_shell(
    html_path: Path | None = None,
    html_text: str | None = None,
    repo_root: Path = DEST,
) -> dict[str, Any]:
    target = html_path or (repo_root / 'output/simulator.html')
    raw_html = html_text if html_text is not None else target.read_text(encoding='utf-8')
    stubs_data = load_json(repo_root / 'data/n06_term_stubs.json')

    parser = _ShellParser()
    parser.feed(raw_html)
    parser.close()

    errors: list[str] = []
    if parser.html_lang != 'lv':
        errors.append(f'<html lang> must be "lv", got {parser.html_lang!r}')

    json_islands = [s for s in parser.scripts if s['type'] == 'application/json']
    exec_scripts = [s for s in parser.scripts if s['type'] != 'application/json']
    if len(exec_scripts) != 1:
        errors.append(f"Expected exactly 1 executable <script>, found {len(exec_scripts)}")
    for s in parser.scripts:
        if s['src']:
            errors.append(f"External script src forbidden: {s['src']!r}")

    island_ids = [s['id'] for s in json_islands]
    if island_ids != DECLARED_ISLANDS_ORDER:
        errors.append(f"JSON island order mismatch: expected {DECLARED_ISLANDS_ORDER}, got {island_ids}")

    id_set = set(parser.ids)
    missing_anchors = [a for a in BLUEPRINT_ANCHORS if a not in id_set]
    if missing_anchors:
        errors.append(f"Missing blueprint anchors: {missing_anchors}")
    if parser.duplicate_ids:
        errors.append(f"Duplicate id attributes (V-10): {parser.duplicate_ids}")
    if parser.non_ascii_ids:
        errors.append(f"Non-ASCII id attributes: {parser.non_ascii_ids}")

    dangling_links = []
    for link in parser.links:
        href = link['href']
        if href.startswith('#'):
            target_id = href[1:]
            if target_id not in id_set:
                dangling_links.append(href)
        else:
            errors.append(f"Non-local href forbidden in single-file offline shell: {href!r}")
    if dangling_links:
        errors.append(f"Unresolved internal anchor links: {dangling_links}")

    external_urls = scan_external_urls(raw_html)
    for item in external_urls:
        errors.append(f"External URL forbidden at line {item['line']}: {item['url']}")

    aria_report = check_aria(parser)
    errors.extend(aria_report['errors'])

    copy_report = check_copy_lint(parser, stubs_data)
    errors.extend(copy_report['errors'])

    css_bytes = sum(len(s.encode('utf-8')) for s in parser.styles)
    js_bytes = sum(s['bytes'] for s in exec_scripts)
    embedded_js_data_bytes = 0
    for s in exec_scripts:
        for line in s['text'].splitlines():
            if re.match(r'^\s*var\s+(?:COVERAGE_INVARIANTS|CONCEPT_DRAWER_DATA|ANCHOR_REGISTRY|RECALL_LAYERS_DATA)\s*=', line):
                embedded_js_data_bytes += len((line + '\n').encode('utf-8'))
    js_code_bytes = js_bytes - embedded_js_data_bytes
    islands_bytes = sum(s['bytes'] for s in json_islands)
    figures_island_bytes = sum(s['bytes'] for s in json_islands if s['id'] == 'sim-figures')
    total_bytes = len(raw_html.encode('utf-8'))
    template_bytes = total_bytes - css_bytes - js_bytes - islands_bytes

    # Section 1.3 sub-budget ceilings: CSS 40-80 KiB (81,920 B ceiling), executable JS code 120-220 KiB (225,280 B ceiling),
    # Inline SVG figures 60-140 KiB (143,360 B ceiling). Embedded N07/N08 JSON var projections are accounted separately.
    #
    # The byte ceilings live in tools/byte_budget.py: one source for every gate,
    # with the declared Section 1.3 bands, the enforced ceilings and the
    # re-budget history (N20: 220 → 232 KiB; N21: 232 → 264 KiB). AGENTS.md
    # requires the budgets to follow the measured requirement rather than an
    # inherited cap, and the deviation from the declared band stays visible in
    # the byte accounting below.
    if css_bytes > byte_budget.ceiling_bytes('css'):
        errors.append(
            f"CSS bytes {css_bytes} exceeds Section 1.3 ceiling "
            f"({byte_budget.ceiling_bytes('css')} bytes)"
        )
    if js_code_bytes > byte_budget.ceiling_bytes('runtime_js_code'):
        errors.append(
            f"Runtime JS code bytes {js_code_bytes} exceeds the measured Section 1.3 ceiling "
            f"({byte_budget.ceiling_bytes('runtime_js_code')} bytes)"
        )
    if figures_island_bytes > 140 * 1024:
        errors.append(f"Figures island bytes {figures_island_bytes} exceeds Section 1.3 figure ceiling (143360 bytes)")

    return {
        'schema_version': 1,
        'task': 'N06',
        'status': 'PASS' if not errors else 'FAIL',
        'artifact_sha256': sha256_bytes(raw_html.encode('utf-8')),
        'structural': {
            'lang': parser.html_lang,
            'executable_scripts_count': len(exec_scripts),
            'json_islands_order': island_ids,
            'blueprint_anchors': BLUEPRINT_ANCHORS,
            'blueprint_anchors_present': len(BLUEPRINT_ANCHORS) - len(missing_anchors),
            'total_ids': len(parser.ids),
            'duplicate_ids': parser.duplicate_ids,
            'non_ascii_ids': parser.non_ascii_ids,
            'internal_links_count': len(parser.links),
            'dangling_links': dangling_links,
            'external_urls_count': len(external_urls),
            'external_urls': external_urls,
        },
        'aria': aria_report,
        'copy_lint': copy_report,
        'byte_accounting': {
            'total_bytes': total_bytes,
            'css_bytes': css_bytes,
            'css_ceiling_bytes': 80 * 1024,
            'runtime_js_bytes': js_bytes,
            'runtime_js_code_bytes': js_code_bytes,
            'embedded_js_data_bytes': embedded_js_data_bytes,
            'runtime_js_ceiling_bytes': byte_budget.ceiling_bytes('runtime_js_code'),
            'declared_runtime_js_band_bytes': list(byte_budget.DECLARED_BANDS['runtime_js_code']),
            'figures_island_bytes': figures_island_bytes,
            'figures_ceiling_bytes': 140 * 1024,
            'islands_bytes': islands_bytes,
            'template_overhead_bytes': template_bytes,
        },
        'errors': errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    st = report['structural']
    ba = report['byte_accounting']
    return (
        f"n06_shell {report['status']}: lang={st['lang']}, anchors={st['blueprint_anchors_present']}/{len(BLUEPRINT_ANCHORS)}, "
        f"islands={len(st['json_islands_order'])}/8, scripts={st['executable_scripts_count']}, "
        f"urls={st['external_urls_count']}, css={ba['css_bytes']}B, js_code={ba['runtime_js_code_bytes']}B (script={ba['runtime_js_bytes']}B), fig={ba['figures_island_bytes']}B, total={ba['total_bytes']}B"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', default=str(DEST / 'output/simulator.html'))
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    report = validate_shell(html_path=Path(args.html), repo_root=DEST)
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
