# -*- coding: utf-8 -*-
"""T20: generated two-page A4 exam reference pack.

The pack is derived from data already owned by the document:

* quantities and route metadata from ``routes.py``;
* the formula rows of section 16.a in ``ch15_16.html``;
* two high-value rows from each mistake group in chapter 13;
* the decision tree from ``routes.validate_decision_tree()``.

Nothing is copied into a hand-maintained pack file.  Every selected formula is
checked against a ``lab.RELATIONS`` record (or a route label for dilution and
mixing), and every trap row is checked against its source table and any task
anchor it cites.

Run: ``python3 -I build/reference.py --pdf``.  ``build.py --pack`` calls
``write()`` after the normal build.
"""
from __future__ import annotations

import datetime as _dt
import html
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'out'
PACK_HTML = OUT / 'exam_pack.html'
PACK_PDF = OUT / 'exam_pack.pdf'

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import routes  # noqa: E402

# Rows of the 16.a formula table that earn a place on a two-page card.
FORMULA_NAMES = [
    'vielas daudzums',
    'molārā koncentrācija',
    'masas koncentrācija',
    'masas daļa',
    'šķīduma masa',
    'pāreja w → c',
    'pāreja c → w',
    'pāreja c → γ',
    'atšķaidīšana',
    'sajaukšana',
    'joni',
    'reakcija',
    'vienības',
]

# Exact formula fragments expected in the 16.a row (after tag/space normalisation).
PARITY = {
    'vielas daudzums': 'n=m/M',
    'molārā koncentrācija': 'c=n/V',
    'masas koncentrācija': 'γ=m/V',
    'masas daļa': 'w=m(viela)/m(šķīdums)',
    'šķīduma masa': 'm(šķīdums)=m(viela)+m(šķīdinātājs)',
    'pāreja w → c': 'c=10·w%·ρ/M',
    'pāreja c → w': 'w%=cM/(10ρ)',
    'pāreja c → γ': 'γ=cM',
    'atšķaidīšana': 'c1V1=c2V2',
    'sajaukšana': '(c1V1+c2V2)/(V1+V2)',
    'joni': 'c(jons)=koeficients·c(sāls)',
    'reakcija': 'n(B)=(b/a)·n(A)',
    'vienības': '1g/L=1mg/mL',
}

# Computational-layer evidence for each derived formula (route or lab relation).
LAB_EQUIV = {
    'vielas daudzums': ['n_m_M', 'm_n_M'],
    'molārā koncentracija': ['c_n_V', 'n_c_V', 'V_n_c'],
    'masas koncentracija': ['gamma_m_V'],
    'masas daļa': ['w_m_msol'],
    'šķīduma masa': ['msol_V_rho'],
    'pāreja w → c': ['c_w_rho_M'],
    'pāreja c → w': ['w_c_M_rho'],
    'pāreja c → γ': ['gamma_c_M'],
}
ROUTE_PARITY = {
    'atšķaidīšana': ('dil', 'c₁V₁ = c₂V₂'),
    'sajaukšana': ('mix', 'c₁V₁ + c₂V₂'),
}

PROTOCOL = [
    'Ievadi skaitļus ar pilnu precizitāti, nemaini dotos ciparus.',
    'Pārrēķini vienības pirms ievietošanas: mL → L, mg → g, % → daļa.',
    'Veic vienu dalījumu vai reizinājumu; starprezultātu nenoapaļo.',
    'Noapaļo vienreiz beigās līdz vismazāk precīzajam dotajam.',
    'Pārbaudi lielumu ar vienību ķēdi un atbildes kārtu.',
]

GROUP_TITLES = {
    'c': 'Prasa c',
    'g': 'Prasa γ',
    'w': 'Prasa w',
    'n': 'Prasa n',
    'm': 'Prasa m',
    'V': 'Prasa V',
    'dil': 'Atšķaida',
    'mix': 'Sajauc',
    'c-ions': 'Jonu c',
    'n-reaction': 'Reakcija',
}


def _text(fragment: str) -> str:
    text = re.sub(r'<[^>]+>', '', fragment)
    return re.sub(r'\s+', ' ', html.unescape(text)).strip()


def _normalise_formula(fragment: str) -> str:
    text = _text(fragment)
    text = text.replace('×', '·').replace('−', '-').replace(' ', '')
    text = text.replace('<', '').replace('>', '')
    return text


def formula_rows():
    """Return the selected formula table rows, in document order."""
    source = (HERE / 'ch15_16.html').read_text(encoding='utf-8')
    match = re.search(
        r'<caption>22\. tabula\.[\s\S]*?</caption>[\s\S]*?<tbody>([\s\S]*?)</tbody>',
        source)
    if not match:
        raise SystemExit('reference: 16.a formula table not found')
    rows = []
    for body in re.findall(r'<tr>([\s\S]*?)</tr>', match.group(1)):
        cells = re.findall(r'<td>([\s\S]*?)</td>', body)
        if len(cells) != 4:
            continue
        rows.append({
            'name': cells[0],
            'formula': cells[1],
            'units': cells[2],
            'when': cells[3],
        })
    by_name = {_text(row['name']): row for row in rows}
    missing = [name for name in FORMULA_NAMES if name not in by_name]
    if missing:
        raise SystemExit(f'reference: formula rows missing: {missing}')
    selected = [by_name[name] for name in FORMULA_NAMES]
    if len(selected) != len(FORMULA_NAMES):
        raise SystemExit('reference: duplicate formula selection')
    return selected


def trap_rows():
    """First and last row of each chapter-13 mistake group (12 rows)."""
    source = (HERE / 'ch13_14.html').read_text(encoding='utf-8')
    matches = re.findall(
        r'<caption>(\d+)\. tabula\. Kļūdas [^<]*</caption>[\s\S]*?<tbody>([\s\S]*?)</tbody>',
        source)
    if len(matches) != 6:
        raise SystemExit(f'reference: expected 6 mistake tables, found {len(matches)}')
    tables = [body for _number, body in sorted(matches, key=lambda item: int(item[0]))]
    selected = []
    for body in tables:
        rows = []
        for row in re.findall(r'<tr>([\s\S]*?)</tr>', body):
            number = re.search(r'<th scope="row">(\d+)</th>', row)
            cells = re.findall(r'<td>([\s\S]*?)</td>', row)
            if not number or len(cells) != 4:
                continue
            rows.append({
                'number': int(number.group(1)),
                'symptom': cells[0],
                'why': cells[1],
                'fix': cells[2],
                'chapter': cells[3],
            })
        if len(rows) < 2:
            raise SystemExit('reference: mistake group with fewer than two rows')
        selected.extend([rows[0], rows[-1]])
    if len(selected) != 12:
        raise SystemExit(f'reference: expected 12 traps, got {len(selected)}')
    return selected


def _quantities():
    names = {
        'm': 'izšķīdinātās vielas masa',
        'n': 'vielas daudzums',
        'c': 'molārā koncentrācija',
        'w': 'masas daļa',
        'ms': 'šķīduma masa',
        'solvent': 'šķīdinātāja masa',
        'V': 'šķīduma tilpums',
        'g': 'masas koncentrācija',
    }
    order = ['m', 'n', 'c', 'w', 'ms', 'solvent', 'V', 'g']
    out = []
    for key in order:
        item = routes.QUANTITIES[key]
        out.append({'symbol': item['symbol'], 'name': names[key], 'unit': item['unit']})
    return out


def _decision_lines():
    tree = routes.validate_decision_tree()
    lines = []
    for group in tree['groups']:
        first = group['entries'][0]
        lines.append({
            'title': GROUP_TITLES.get(group['target'], group['title']),
            'label': first['label'],
            'start': first['start'],
            'chapter': first['chapter'],
        })
    return lines


def parity_errors(rows):
    """Every selected formula must be backed by the 16.a source and the computational layer."""
    errors = []
    try:
        import lab
    except Exception as exc:  # pragma: no cover
        return [f'lab import failed: {exc}']
    relation_ids = {r['id'] for r in lab.RELATIONS}
    for row in rows:
        name = _text(row['name'])
        evidence = PARITY.get(name)
        if evidence is None:
            errors.append(f'formula row without parity rule: {name}')
            continue
        if evidence not in _normalise_formula(row['formula']):
            errors.append(f'{name}: 16.a formula lacks {evidence!r}')
        if name in LAB_EQUIV:
            for relation in LAB_EQUIV[name]:
                if relation not in relation_ids:
                    errors.append(f'{name}: lab relation missing {relation}')
        if name in ROUTE_PARITY:
            key, needle = ROUTE_PARITY[name]
            if needle not in routes.ROUTES[key]['label_lv']:
                errors.append(f'{name}: route {key} lacks {needle}')
        if name in ('joni', 'reakcija', 'vienības') and not evidence:
            errors.append(f'{name}: no source evidence')
    return errors


def _task_anchor(tid: str) -> str:
    return 't-' + tid.lower().replace(' ', '').replace('.', '-').replace('/', '-').replace('*', 's')


def trap_errors(rows):
    errors = []
    try:
        import tasks_a  # noqa: F401  (registers task data)
        import tasks_b  # noqa: F401
        from taskbase import TASKS
    except Exception as exc:  # pragma: no cover
        return [f'task import failed: {exc}']
    anchors = {_task_anchor(tid): tid for tid in TASKS}
    for row in rows:
        if not _text(row['symptom']) or not _text(row['fix']):
            errors.append(f'trap {row["number"]}: empty symptom or fix')
        for anchor in re.findall(r'href="#(t-[a-z0-9-]+)"', row['symptom'] + row['fix']):
            if anchor not in anchors:
                errors.append(f'trap {row["number"]}: unknown task anchor {anchor}')
    numbers = [row['number'] for row in rows]
    if len(set(numbers)) != len(numbers):
        errors.append('duplicate trap numbers')
    return errors


def _pdf_markup(text: str) -> str:
    """Keep only tags ReportLab Paragraph understands; drop anchors/spans."""
    text = re.sub(r'<a\b[^>]*>([\s\S]*?)</a>', r'\1', text)
    text = re.sub(r'<span\b[^>]*>([\s\S]*?)</span>', r'\1', text)
    text = re.sub(r'<abbr\b[^>]*>([\s\S]*?)</abbr>', r'\1', text)
    text = re.sub(r'<code\b[^>]*>([\s\S]*?)</code>', r'\1', text)
    return text


def _par(text: str, style: str):
    """ReportLab paragraph markup from the document's small HTML subset."""
    from reportlab.platypus import Paragraph
    text = re.sub(r'<sub>(.*?)</sub>', r'<sub>\1</sub>', text)
    text = re.sub(r'<sup>(.*?)</sup>', r'<super>\1</super>', text)
    text = text.replace('<i>', '<i>').replace('</i>', '</i>')
    return Paragraph(text, style)


def _styles():
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    ink = colors.HexColor('#111111')
    muted = colors.HexColor('#444444')
    accent = colors.HexColor('#0B4A60')
    return {
        'title': ParagraphStyle('title', fontName='NotoSerif', fontSize=18, leading=21,
                                textColor=ink, spaceAfter=2),
        'subtitle': ParagraphStyle('subtitle', fontName='NotoSans', fontSize=9.5, leading=12,
                                   textColor=muted, spaceAfter=8),
        'h2': ParagraphStyle('h2', fontName='NotoSansBold', fontSize=11.2, leading=14,
                             textColor=accent, spaceBefore=6, spaceAfter=3),
        'body': ParagraphStyle('body', fontName='NotoSans', fontSize=9.5, leading=12,
                               textColor=ink, alignment=TA_LEFT),
        'small': ParagraphStyle('small', fontName='NotoSans', fontSize=9.5, leading=11.6,
                                textColor=muted),
        'cell': ParagraphStyle('cell', fontName='NotoSans', fontSize=9.5, leading=11.6,
                               textColor=ink),
        'cellmuted': ParagraphStyle('cellmuted', fontName='NotoSans', fontSize=9.5,
                                    leading=11.4, textColor=muted),
        'accent': accent,
        'ink': ink,
        'muted': muted,
    }


def _register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    base = Path('/usr/share/fonts/google-noto')
    faces = {
        'NotoSans': base / 'NotoSans-Regular.ttf',
        'NotoSansBold': base / 'NotoSans-SemiBold.ttf',
        'NotoSerif': base / 'NotoSerif-SemiBold.ttf',
        'NotoMath': base / 'NotoSansMath-Regular.ttf',
    }
    for name, path in faces.items():
        if not path.exists():
            raise SystemExit(f'reference: font missing {path}')
        pdfmetrics.registerFont(TTFont(name, str(path)))


def write_pdf(rows=None, traps=None):
    """Optional PDF export.  The HTML is canonical; this is a 2-page print proof."""
    def _P(text, style):
        return Paragraph(_pdf_markup(text), style)
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                        TableStyle, PageBreak)
    except Exception as exc:
        print(f'reference: reportlab unavailable ({exc}); PDF not written')
        return None
    rows = rows or formula_rows()
    traps = traps or trap_rows()
    _register_fonts()
    st = _styles()
    OUT.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(PACK_PDF), pagesize=A4,
                            leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=12 * mm, bottomMargin=12 * mm,
                            title='Eksāmena atsauces lapa — Šķīdumi un koncentrācijas',
                            author='Ģenerēts no build/reference.py')
    story = []
    stamp = _dt.date.today().isoformat()
    story.append(_P('Eksāmena atsauces lapa', st['title']))
    story.append(_P(
        'Šķīdumi un koncentrāciju aprēķini · Medicīniskā ķīmija, 3. tēma · '
        f'ģenerēts no dokumenta datiem {stamp} · avoti A–F; skaitļi pārbaudīti ar build/calc.py',
        st['subtitle']))

    story.append(_P('1. Lielumi un mērvienības', st['h2']))
    qrows = [[_P('Apzīmējums', st['cellmuted']), _P('Lielums', st['cellmuted']),
              _P('Mērvienība', st['cellmuted'])]]
    for q in _quantities():
        qrows.append([_P(q['symbol'], st['cell']), _P(q['name'], st['cell']),
                      _P(q['unit'], st['cell'])])
    qtable = Table(qrows, colWidths=[42 * mm, 86 * mm, 46 * mm])
    qtable.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, st['accent']),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(qtable)
    story.append(Spacer(1, 4))

    story.append(_P('2. Formulas un lietošanas nosacījumi', st['h2']))
    frows = [[_P('Lielums', st['cellmuted']), _P('Formula', st['cellmuted']),
              _P('Mērvienības / kad lieto', st['cellmuted'])]]
    for row in rows:
        frows.append([
            _P(row['name'], st['cell']),
            _P(row['formula'], st['cell']),
            _P(row['units'] + ' · ' + row['when'], st['cellmuted']),
        ])
    ftable = Table(frows, colWidths=[36 * mm, 82 * mm, 56 * mm], repeatRows=1)
    ftable.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, st['accent']),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(ftable)
    story.append(_P(
        'Procenta veids: w ir m/m; etiķetes procenti var būt m/V. Bez ρ starp w un c pāriet nevar. '
        'Tilpumu aditivitāte ir atsevišķs pieņēmums, nevis formula.', st['small']))

    story.append(PageBreak())
    story.append(_P('3. Kā sākt uzdevumu', st['h2']))
    tree_rows = []
    for line in _decision_lines():
        tree_rows.append([
            _P(line['title'], st['cell']),
            _P(line['label'], st['cell']),
            _P(line['start'], st['cellmuted']),
        ])
    ttable = Table(tree_rows, colWidths=[30 * mm, 56 * mm, 88 * mm])
    ttable.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.0),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(ttable)
    story.append(Spacer(1, 3))

    story.append(_P('4. Divpadsmit kļūdas, kas jāatpazīst', st['h2']))
    erows = [[_P('Nr.', st['cellmuted']), _P('Simptoms', st['cellmuted']),
              _P('Labojums', st['cellmuted'])]]
    for trap in traps:
        erows.append([
            _P(str(trap['number']), st['cell']),
            _P(trap['symptom'], st['cell']),
            _P(trap['fix'], st['cell']),
        ])
    etable = Table(erows, colWidths=[10 * mm, 78 * mm, 86 * mm], repeatRows=1)
    etable.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, st['accent']),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1.1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.1),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(etable)
    story.append(Spacer(1, 3))

    story.append(_P('5. Kalkulatora protokols', st['h2']))
    for index, item in enumerate(PROTOCOL, 1):
        story.append(_P(f'{index}. {item}', st['body']))
    story.append(Spacer(1, 4))
    story.append(_P(
        'Šī lapa ir mācību palīglīdzeklis, nevis klīniskā vadlīnija. '
        f'Būvēts {stamp}; pirms lietošanas pārbaudiet, vai dokumenta versija nav mainījusies.',
        st['small']))

    doc.build(story)
    pages = getattr(doc, 'page', None)
    if pages != 2:
        raise SystemExit(f'reference: PDF has {pages} pages, expected 2')
    return PACK_PDF


def _font_faces():
    from fonts.base64 import B64
    return (
        '@font-face{font-family:"PackSans";src:url(data:font/woff2;base64,'
        + B64['sans-regular'] + ') format("woff2");font-weight:400;font-style:normal;font-display:swap}'
        '@font-face{font-family:"PackSans";src:url(data:font/woff2;base64,'
        + B64['sans-semibold'] + ') format("woff2");font-weight:600;font-style:normal;font-display:swap}'
        '@font-face{font-family:"PackMath";src:url(data:font/woff2;base64,'
        + B64['math'] + ') format("woff2");font-weight:400;font-style:normal;font-display:swap;'
        'unicode-range:U+2190-21FF,U+2200-22FF,U+25A0-25FF,U+00B1,U+00D7,U+00B7}'
    )


def render(rows=None, traps=None):
    rows = rows or formula_rows()
    traps = traps or trap_rows()
    stamp = _dt.date.today().isoformat()
    quantities = _quantities()
    decision = _decision_lines()
    q_html = ''.join(
        f'<tr><td>{q["symbol"]}</td><td>{q["name"]}</td><td>{q["unit"]}</td></tr>'
        for q in quantities)
    f_html = ''.join(
        f'<tr><td>{r["name"]}</td><td>{r["formula"]}</td>'
        f'<td>{r["units"]} · {r["when"]}</td></tr>'
        for r in rows)
    d_html = ''.join(
        f'<tr><td>{line["title"]}</td><td>{line["label"]}</td><td>{line["start"]}</td></tr>'
        for line in decision)
    e_html = ''.join(
        f'<tr><td>{t["number"]}</td><td>{t["symptom"]}</td><td>{t["fix"]}</td></tr>'
        for t in traps)
    p_html = ''.join(f'<li>{item}</li>' for item in PROTOCOL)
    return f'''<!DOCTYPE html>
<html lang="lv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Eksāmena atsauces lapa — 2 lappuses</title>
<style>
{_font_faces()}
@page{{size:A4 portrait;margin:12mm}}
*{{box-sizing:border-box}}
html{{font-size:9.5pt}}
body{{margin:0;background:#fff;color:#111;font-family:"PackSans","Noto Sans",sans-serif;line-height:1.28}}
.pack-page{{width:auto;max-width:680px;min-height:273mm;margin:0;padding:0 2mm;break-after:page;page-break-after:always}}
.pack-page:last-child{{break-after:auto;page-break-after:auto}}
h1{{font-size:17pt;line-height:1.1;margin:0 0 3px;font-weight:600}}
.meta{{font-size:8.2pt;color:#444;margin:0 0 9px;border-bottom:1px solid #0B4A60;padding-bottom:5px}}
h2{{font-size:10.5pt;color:#0B4A60;margin:7px 0 3px;font-weight:600}}
th,td{{overflow-wrap:anywhere;word-break:break-word}}
p{{margin:0 0 4px}}
table{{border-collapse:collapse;width:100%;table-layout:fixed;font-size:8.1pt;line-height:1.22}}
th{{text-align:left;font-weight:600;color:#444;border-bottom:1px solid #0B4A60;padding:2px 3px}}
td{{vertical-align:top;padding:1.5px 3px;border-bottom:1px solid #E2E2E2;overflow-wrap:anywhere;word-break:break-word}}
td:first-child{{white-space:normal}}
.formula{{font-family:"PackMath","PackSans",sans-serif;font-variant-numeric:tabular-nums}}
.small,.note{{font-size:7.8pt;color:#444;line-height:1.25}}
ol.protocol{{margin:0;padding-left:16px}}
ol.protocol li{{margin:0 0 2px}}
.foot{{margin-top:6px;border-top:1px solid #C8C8C8;padding-top:4px;font-size:7.6pt;color:#444}}
a{{color:#111;text-decoration:underline;text-underline-offset:1.5pt}}
@media print{{a{{color:#111}}.pack-page{{max-width:none;width:auto;margin:0;padding:0;min-height:0}}}}
</style>
</head>
<body>
<section class="pack-page" id="pack-1">
  <h1>Eksāmena atsauces lapa</h1>
  <p class="meta">Šķīdumi un koncentrāciju aprēķini · Medicīniskā ķīmija, 3. tēma · avoti A–F · ģenerēts {stamp} no <code>build/reference.py</code></p>
  <h2>1. Lielumi un mērvienības</h2>
  <table>
    <thead><tr><th>Apzīmējums</th><th>Lielums</th><th>Mērvienība</th></tr></thead>
    <tbody>{q_html}</tbody>
  </table>
  <h2>2. Formulas un lietošanas nosacījumi</h2>
  <table>
    <thead><tr><th>Lielums</th><th>Formula</th><th>Mērvienības · kad lieto</th></tr></thead>
    <tbody>{f_html}</tbody>
  </table>
  <p class="note">Procenta veids: w ir m/m; etiķetes procenti var būt m/V. Bez ρ starp w un c pāriet nevar. Tilpumu aditivitāte ir atsevišķs pieņēmums, nevis formula.</p>
  <p class="foot">Skaitļi pārbaudīti ar <code>build/calc.py</code>; formulas — <code>build/lab.py</code>; avotu kļūdas — 13. nodaļa un 16.c žurnāls.</p>
</section>
<section class="pack-page" id="pack-2">
  <h1>Kā sākt uzdevumu</h1>
  <p class="meta">Rādītājs veidots no <code>build/routes.py</code>; 12 kļūdas — no 13. nodaļas; nekas nav pārrakstīts ar roku.</p>
  <h2>3. Īsais lēmumu ceļš</h2>
  <table>
    <thead><tr><th>Jautājums prasa</th><th>Maršruts</th><th>Doti lielumi</th></tr></thead>
    <tbody>{d_html}</tbody>
  </table>
  <h2>4. Divpadsmit kļūdas, kas jāatpazīst</h2>
  <table>
    <thead><tr><th>Nr.</th><th>Simptoms</th><th>Labojums</th></tr></thead>
    <tbody>{e_html}</tbody>
  </table>
  <h2>5. Kalkulatora protokols</h2>
  <ol class="protocol">{p_html}</ol>
  <p class="foot">Mācību palīglīdzeklis, nevis klīniskā vadlīnija. Būvēts {stamp}; ja dokumenta versija mainās, pārģenerējiet šo lapu.</p>
</section>
</body>
</html>
'''


def audit(doc=None, rows=None, traps=None):
    errors = []
    rows = rows or formula_rows()
    traps = traps or trap_rows()
    if len(traps) != 12:
        errors.append(f'pack traps {len(traps)} != 12')
    errors.extend(parity_errors(rows))
    errors.extend(trap_errors(traps))
    page_html = render(rows, traps)
    if page_html.count('class="pack-page"') != 2:
        errors.append('pack does not have exactly two page sections')
    if '@page{size:A4' not in page_html:
        errors.append('pack lacks A4 page rule')
    if '<script' in page_html or 'http://' in page_html or 'https://' in page_html:
        errors.append('pack is not self-contained')
    if not all(name in page_html for name in ('1. Lielumi', '2. Formulas', '3. Īsais lēmumu ceļš',
                                               '4. Divpadsmit kļūdas', '5. Kalkulatora protokols')):
        errors.append('pack section missing')
    if doc is not None:
        for line in _decision_lines():
            if f'href="{line["chapter"]}"' not in doc:
                errors.append(f'decision chapter anchor missing in document: {line["chapter"]}')
    return errors


def write(pdf=False, doc=None):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = formula_rows()
    traps = trap_rows()
    errors = audit(doc=doc, rows=rows, traps=traps)
    if errors:
        for error in errors:
            print(f'reference: {error}')
        raise SystemExit('reference: audit failed')
    PACK_HTML.write_text(render(rows, traps), encoding='utf-8')
    print(f'reference: wrote {PACK_HTML} ({PACK_HTML.stat().st_size/1024:.1f} KB); 2 pages; 12 traps')
    if pdf:
        path = write_pdf(rows, traps)
        if path:
            print(f'reference: wrote {path} ({path.stat().st_size/1024:.1f} KB); pdf pages 2')
    return PACK_HTML


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', action='store_true', help='also write a 2-page PDF proof')
    args = parser.parse_args()
    write(pdf=args.pdf)


if __name__ == '__main__':
    main()
