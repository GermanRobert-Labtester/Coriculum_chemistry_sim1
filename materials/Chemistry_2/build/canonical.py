#!/usr/bin/env python3
"""T18: canonical navigation and quick-reference generation.

This module is the single place where the document's navigation and its
print quick reference are derived from canonical data. It is imported by
``build/build_doc.py`` (assembly) and by ``build/check_canonical.py`` (gate);
it has no side effects and never writes files.

Canonical sources
-----------------
* Chapters and their titles: the section sources themselves
  (``build/sections/NN_chNN.html``), never a hand-kept list.
* The five learning outcomes: ``build/outcomes.json`` (one record, with the
  course wording and its locator in the PDF).
* Computed numbers quoted by the quick reference: ``build/verified.json``,
  produced and re-checked by ``build/verify_numbers.py``.

Placeholders
------------
``{{key}}`` in a section template is replaced by the value that ``key``
denotes in the canonical record. Keys are listed in ``BINDINGS``; each entry
is a pure function of ``verified.json``, so a value can only change when the
canonical record changes. A template may not contain a hard-coded copy of a
canonical value — the gate rejects that, because it is exactly how the
quick reference drifted from the chapters (R² and the lowest standard).

Values are display strings. A value may contain the ``&nbsp;`` entity for
digit grouping; the surrounding markup stays in the template.

Run with python3 -I (isolated, standard library only).
"""
from __future__ import annotations

import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BUILD = Path(__file__).resolve().parent
SECT = BUILD / 'sections'
OUTCOMES_PATH = BUILD / 'outcomes.json'
VERIFIED_PATH = BUILD / 'verified.json'

PLACEHOLDER_RE = re.compile(r'\{\{([a-z][a-z0-9_.]*)\}\}')


# --------------------------------------------------------------------------
# number formatting (Latvian decimal comma)
# --------------------------------------------------------------------------
def lv(value) -> str:
    """Render a number with a Latvian decimal comma, no thousands grouping."""
    if isinstance(value, str):
        return value.replace('.', ',')
    return f'{value}'.replace('.', ',')


def lv_sig(value, digits: int) -> str:
    """Render a value with a given number of significant figures."""
    d = Decimal(str(value)).normalize()
    if d == 0:
        return '0'
    q = Decimal(1).scaleb(d.adjusted() - digits + 1)
    d = d.quantize(q, rounding=ROUND_HALF_UP)
    return format(d, 'f').replace('.', ',')


def group(value) -> str:
    """Group thousands with a non-breaking space entity: 4025808 -> 4 025 808."""
    n = int(Decimal(str(value)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    text = f'{n:,}'.replace(',', '&nbsp;')
    return text


# --------------------------------------------------------------------------
# canonical values used by the quick reference
# --------------------------------------------------------------------------
def _cal(v):
    return v['calibration']


def _hl(v):
    return v['half_life']


def _sig(v):
    return v['sigfig']


BINDINGS = {
    # -- calibration (ch. 10) --
    'cal.slope': lambda v: lv(_cal(v)['full_slope']),
    'cal.intercept': lambda v: lv(_cal(v)['reported_intercept']),
    'cal.r2': lambda v: lv(_cal(v)['reported_r2']),
    'cal.rho_min': lambda v: lv(int(_cal(v)['range_rho_min'])),
    'cal.rho_max': lambda v: lv(int(_cal(v)['range_rho_max'])),
    'cal.a_min': lambda v: lv(_cal(v)['range_A_min']),
    'cal.a_max': lambda v: lv(_cal(v)['range_A_max']),
    'cal.citron_a': lambda v: lv(_sample(v, 'Citroni')['A']),
    'cal.citron_c': lambda v: lv(_sample(v, 'Citroni')['c1']),
    # -- statistics (ch. 7) --
    'q3.mean': lambda v: lv(v['q3']['reported_mean']),
    'q3.n': lambda v: lv(v['q3']['n']),
    'q3.t': lambda v: lv(v['q3']['t']),
    'q3.dixon_q': lambda v: lv_sig(v['q3']['dixon_q'], 3),
    'q3.dixon_crit': lambda v: lv(v['q3']['dixon_crit']),
    # -- significant figures (ch. 8) --
    'sig.s23_once': lambda v: lv(_sig(v)['S23_once']),
    'sig.s23_double': lambda v: lv(_sig(v)['S23_double']),
    'sig.q1_add': lambda v: lv(_sig(v)['Q1_add']),
    'sig.q4c_3sf': lambda v: lv_sig(_sig(v)['Q4c_product'], 3),
    # -- half life (ch. 11) --
    'hl.t0': lambda v: lv(_hl(v)['hyd_t0']),
    'hl.h1': lambda v: lv(_hl(v)['hyd_halvings'][1]),
    'hl.h2': lambda v: lv(_hl(v)['hyd_halvings'][2]),
    'hl.d1': lambda v: lv(_hl(v)['hyd_deltas'][0]),
    'hl.d2': lambda v: lv(_hl(v)['hyd_deltas'][1]),
    'hl.mean_dt': lambda v: lv(_hl(v)['hyd_mean_dt']),
    'hl.mean_dt_min': lambda v: lv_sig(_hl(v)['hyd_mean_dt'] / 60, 4),
    'hl.key_s': lambda v: lv(_hl(v)['hyd_key_reading_s']),
    'hl.key_min': lambda v: lv_sig(_hl(v)['hyd_key_reading_s'] / 60, 2),
    'hl.hg_d': lambda v: lv(_hl(v)['hg_d']),
    'hl.hg_h': lambda v: lv_sig(_hl(v)['hg_h'], 5),
    'hl.hg_min': lambda v: group(_hl(v)['hg_min']),
    'hl.hg_s': lambda v: group(_hl(v)['hg_s']),
    # -- density and mass fraction (ch. 12) --
    'dens.solution_mass': lambda v: lv(v['density']['solution_mass']),
    'dens.temp': lambda v: lv(v['density']['line_temperature_C']),
}


def _sample(verified, name):
    for s in verified['calibration']['samples']:
        if s['name'] == name:
            return s
    raise KeyError(f'sample {name!r} not in the canonical record')


def load_verified(path=None) -> dict:
    return json.loads(Path(path or VERIFIED_PATH).read_text(encoding='utf-8'))


def binding_values(verified=None) -> dict:
    """Resolve every binding against the canonical record."""
    verified = verified if verified is not None else load_verified()
    return {key: fn(verified) for key, fn in BINDINGS.items()}


def used_bindings(text: str) -> set:
    """Binding keys referenced by a template."""
    return set(PLACEHOLDER_RE.findall(text))


def substitute(text: str, values: dict) -> str:
    """Replace {{key}} placeholders. An unknown key is an error, not a blank."""
    missing = sorted(used_bindings(text) - set(values))
    if missing:
        raise KeyError(f'unknown canonical binding(s): {", ".join(missing)}')
    return PLACEHOLDER_RE.sub(lambda m: values[m.group(1)], text)


# --------------------------------------------------------------------------
# chapters — derived from the section sources
# --------------------------------------------------------------------------
CH_FILE_RE = re.compile(r'^(\d+)_ch(\d+)\.html$')
H2_RE = re.compile(r'<h2[^>]*>(.*?)</h2>', re.S)
CHAPTER_NO_RE = re.compile(r'<span class="chapter-no">.*?</span>', re.S)
TAG_RE = re.compile(r'<[^>]+>')

# Inline markup kept in a table-of-contents label.
TOC_INLINE_TAGS = {'i', 'b', 'em', 'strong', 'sub', 'sup', 'code', 'span'}
# Labels that carry no meaning in a list of links.
TOC_DROP_CLASSES = {'tag'}


def plain(fragment: str) -> str:
    text = TAG_RE.sub('', fragment)
    text = (text.replace('&nbsp;', ' ').replace('&amp;', '&')
            .replace('&lt;', '<').replace('&gt;', '>').replace('&#8211;', '–'))
    return re.sub(r'\s+', ' ', text).strip()


def toc_label(inner: str) -> str:
    """Plain, link-free label for a navigation entry.

    Anchors are unwrapped (a nested <a> inside <a> is invalid), badge spans
    (for example the «papildinājums» marker) are dropped with their text —
    they are meaningful in the heading, not in a list of links — and the
    remaining inline markup (<i>, <sub>, …) is kept.
    """
    text = re.sub(r'<a\b[^>]*>(.*?)</a>', r'\1', inner, flags=re.S)
    text = re.sub(r'<span class="tag[^"]*">.*?</span>', '', text, flags=re.S)

    def keep(m):
        tag = re.match(r'</?([a-z0-9]+)', m.group(0)).group(1).lower()
        return m.group(0) if tag in TOC_INLINE_TAGS else ''

    text = re.sub(r'</?[a-z0-9]+\b[^>]*>', keep, text, flags=re.I)
    return re.sub(r'\s+', ' ', text).strip()


def chapter_catalogue(sect_dir=None) -> list:
    """Chapter number, title and file — read from the section sources.

    The title is the one in the chapter's own <h2>; a separate copy of the
    chapter list is what let the navigation drift from the headings.
    """
    sect_dir = Path(sect_dir or SECT)
    chapters = []
    for path in sorted(sect_dir.glob('*.html')):
        m = CH_FILE_RE.match(path.name)
        if not m:
            continue
        number = int(m.group(2))
        text = path.read_text(encoding='utf-8')
        h2 = H2_RE.search(text)
        if not h2:
            raise ValueError(f'{path.name}: no <h2> chapter heading')
        inner = CHAPTER_NO_RE.sub('', h2.group(1))
        title = plain(inner)
        if not title:
            raise ValueError(f'{path.name}: empty chapter title')
        chapters.append({'n': number, 'title': title, 'file': path.name})
    numbers = [c['n'] for c in chapters]
    if not numbers:
        raise ValueError(f'no chapter sections found in {sect_dir}')
    if len(set(numbers)) != len(numbers):
        raise ValueError(f'duplicate chapter numbers: {numbers}')
    return sorted(chapters, key=lambda c: c['n'])


# --------------------------------------------------------------------------
# outcomes — the canonical learning-outcome record
# --------------------------------------------------------------------------
def load_outcomes(path=None) -> dict:
    data = json.loads(Path(path or OUTCOMES_PATH).read_text(encoding='utf-8'))
    outcomes = data.get('outcomes')
    if not isinstance(outcomes, list) or not outcomes:
        raise ValueError('outcomes.json: outcomes must be a non-empty list')
    seen = set()
    for o in outcomes:
        for field in ('id', 'course_statement', 'learner_action', 'ch1_where',
                      'nav_label', 'nav_note', 'nav_chapters',
                      'developed_chapters', 'review_chapters'):
            if field not in o:
                raise ValueError(f'outcomes.json: {o.get("id", "?")} lacks {field}')
        if o['id'] in seen:
            raise ValueError(f'outcomes.json: duplicate id {o["id"]}')
        seen.add(o['id'])
        for field in ('nav_chapters', 'developed_chapters', 'review_chapters'):
            if not isinstance(o[field], list):
                raise ValueError(f'outcomes.json: {o["id"]}.{field} must be a list')
    return data


def outcome_chapter_map(outcomes: dict) -> dict:
    """chapter number -> outcome id, derived from the canonical record.

    A chapter may belong to only one outcome; a conflict is an error, not a
    silent last-writer-wins.
    """
    mapping = {}
    for o in outcomes['outcomes']:
        for chapter in list(o['developed_chapters']) + list(o['review_chapters']):
            if chapter in mapping and mapping[chapter] != o['id']:
                raise ValueError(
                    f'chapter {chapter} claimed by {mapping[chapter]} and {o["id"]}')
            mapping[chapter] = o['id']
    return mapping


def format_chapters(numbers) -> str:
    """Chapter reference as the document writes it: 4. nodaļa / 7. un 8. / 9.–11."""
    nums = sorted(set(numbers))
    if not nums:
        return ''
    if len(nums) == 1:
        return f'{nums[0]}. nodaļa'
    if len(nums) == 2:
        return f'{nums[0]}. un {nums[1]}. nodaļa'
    return f'{nums[0]}.–{nums[-1]}. nodaļa'


def render_outcomes_map(outcomes: dict) -> str:
    """The front-matter outcome card, generated from the canonical record."""
    items = []
    for o in outcomes['outcomes']:
        where = format_chapters(o['nav_chapters'])
        anchor = f'#ch-{o["nav_chapters"][0]}'
        items.append(
            f'    <li><a href="{anchor}">{o["nav_label"]}'
            f'<span class="s">{where} · {o["nav_note"]}</span></a></li>'
        )
    body = '\n'.join(items)
    return ('<ol class="outcomes-map" aria-label="Pieci sasniedzamie rezultāti">\n'
            f'{body}\n  </ol>')
