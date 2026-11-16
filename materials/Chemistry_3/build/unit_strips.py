# -*- coding: utf-8 -*-
"""F07: native unit-cancellation rehearsal strips.

The strips are static worked examples, not a calculator.  Each record stores the
factors as numerator/denominator pairs plus the cancellation sentence, so the
fraction notation and the numeric expectation are generated from one place.
"""
from __future__ import annotations

import html

import unitcheck

# Four high-frequency conversions used by current tasks.  The strip itself is
# an illustrative re-arrangement of the task's conversion, hence p-ill.
STRIPS = [
    {
        'key': 'mg-g',
        'chapter': 4,
        'title': '18 000 mg → g',
        'task': 'C10',
        'task_label': 'C 10',
        'kind': 'Ilustratīvs piemērs',
        'prov': 'p-ill',
        'given': 'Dotais lielums: 18 000 mg.',
        'math': '18 000 mg',
        'compose': 'multiply',
        'factors': [
            {'num': '1 g', 'den': '1000 mg', 'cancel': 'mg saīsinās ar mg; paliek g.'},
        ],
        'result': '18 g',
        'check': '18 g × 1000 = 18 000 mg. Atpakaļceļš atgriež doto skaitli.',
        'wrong': {
            'math': '18 000 mg × 1000 = 18 000 000 mg = 18 kg',
            'explain': 'Faktors 1000 ir bez vienības, tāpēc mg paliek mg. Iznākums nav 18 g; vienība neatcēlās.',
        },
        'numeric': {'value': 18000, 'frm': 'mg', 'to': 'g', 'expected': 18.0},
    },
    {
        'key': 'ml-l',
        'chapter': 4,
        'title': '125 mL → L',
        'task': 'C2.2',
        'task_label': 'C 2.2',
        'kind': 'Ilustratīvs piemērs',
        'prov': 'p-ill',
        'given': 'Dotais lielums: 125 mL.',
        'math': '125 mL',
        'compose': 'multiply',
        'factors': [
            {'num': '1 L', 'den': '1000 mL', 'cancel': 'mL saīsinās ar mL; paliek L.'},
        ],
        'result': '0,125 L',
        'check': '0,125 L × 1000 = 125 mL. Atpakaļceļš atgriež doto skaitli.',
        'numeric': {'value': 125, 'frm': 'mL', 'to': 'L', 'expected': 0.125},
    },
    {
        'key': 'gl-mgml',
        'chapter': 8,
        'title': '13,512 g/L → mg/mL',
        'task': 'C15',
        'task_label': 'C 15',
        'kind': 'Ilustratīvs piemērs',
        'prov': 'p-ill',
        'given': 'Dotais lielums: 13,512 g/L.',
        'math': '13,512 g/L',
        'compose': 'multiply',
        'factors': [
            {'num': '1000 mg', 'den': '1 g', 'cancel': 'g saīsinās ar g; paliek mg/L.',
             'intermediate': '13 512 mg/L'},
            {'num': '1 L', 'den': '1000 mL', 'cancel': 'L saīsinās ar L; paliek mg/mL.'},
        ],
        'result': '13,512 mg/mL',
        'check': '13,512 mg/mL = 13,512 g/L, jo 1 g/L = 1 mg/mL. Abos pierakstos saucējs ir litrs šķīduma.',
        'numeric': {'value': 13.512, 'frm': 'g/L', 'to': 'mg/mL', 'expected': 13.512},
    },
    {
        'key': 'm-gamma-v',
        'chapter': 8,
        'title': '40,5 mg ÷ 9,0 mg/mL = mL',
        'task': 'C11',
        'task_label': 'C 11',
        'kind': 'Ilustratīvs piemērs',
        'prov': 'p-ill',
        'given': 'Dotais: 40,5 mg vielas; γ = 9,0 mg/mL.',
        'math': '40,5 mg',
        'compose': 'fraction',
        'factors': [
            {'num': '40,5 mg', 'den': '9,0 mg/mL',
             'cancel': 'mg / (mg/mL): mg saīsinās, paliek mL.'},
        ],
        'result': '4,5 mL',
        'check': '4,5 mL × 9,0 mg/mL = 40,5 mg.',
        'wrong': {
            'math': '40,5 mg × 9,0 mg/mL = 364,5 mg²/mL',
            'explain': 'Reizinājums dod mg²/mL, nevis mL. Masu ar masas koncentrāciju dala, jo abās vienībās ir mg.',
        },
        'numeric': {'value': 40.5, 'divisor': 9.0, 'expected': 4.5},
    },
]

INTROS = {
    4: ('Vienības pārbaudi pirms skaitļa. Atver vienu ķēdi un izlasi, kā katrs '
        'faktors saīsina skaitītāju ar saucēju. Tikai pēc tam rēķini.'),
    8: ('Šīs ķēdes rāda, kā no g/L iegūst mg/mL un kā mg/(mg/mL) dod mL. '
        'Katrs solis ir atsevišķa rinda, tāpēc atver tikai to ķēdi, kuru pārbaudi.'),
}


def _fraction(num, den):
    """Visual fraction plus a spoken linear equivalent for screen readers."""
    return (
        '<span class="ufrac">'
        f'<span class="ufrac-num">{html.escape(num)}</span>'
        '<span class="sr-only"> dalīts ar </span>'
        '<span class="ufrac-sep" aria-hidden="true"> / </span>'
        f'<span class="ufrac-den">{html.escape(den)}</span>'
        '</span>'
    )


def _steps(strip):
    lines = []
    current = strip['math']
    for factor in strip['factors']:
        if strip['compose'] == 'fraction':
            expression = _fraction(factor['num'], factor['den'])
        else:
            expression = f'{current} × {_fraction(factor["num"], factor["den"])}'
        extra = ''
        if factor.get('intermediate'):
            current = factor['intermediate']
            extra = f'<span class="unit-strip-intermediate">→ {html.escape(factor["intermediate"])}</span>'
        lines.append(
            '<li>'
            f'<span class="unit-strip-math">{expression}</span>'
            f'<span class="unit-strip-cancel">{html.escape(factor["cancel"])}</span>'
            f'{extra}'
            '</li>'
        )
    return '\n'.join(lines)


def _strip(strip):
    wrong = ''
    if strip.get('wrong'):
        wrong = (
            '<div class="unit-strip-wrong">'
            '<p class="unit-strip-wrong-label">Nepareizs faktors vai darbība</p>'
            f'<p class="unit-strip-math">{html.escape(strip["wrong"]["math"])}</p>'
            f'<p class="unit-strip-cancel">{html.escape(strip["wrong"]["explain"])}</p>'
            '</div>'
        )
    return (
        f'<details class="unit-strip" id="unit-strip-{strip["key"]}">'
        '<summary>'
        f'<span class="unit-strip-title">{html.escape(strip["title"])}</span> '
        f'<span class="unit-strip-kind prov {strip["prov"]}">{html.escape(strip["kind"])}</span>'
        '</summary>'
        '<div class="unit-strip-body">'
        f'<p class="unit-strip-given">{html.escape(strip["given"])} '
        f'<span class="unit-strip-source">Saistītais uzdevums: '
        f'<a href="#t-{strip["task"].lower().replace(".", "-")}">{html.escape(strip["task_label"])}</a>.</span></p>'
        f'<ol class="unit-strip-steps">\n{_steps(strip)}\n</ol>'
        f'<p class="unit-strip-result"><strong>Rezultāts.</strong> = {html.escape(strip["result"])}</p>'
        f'<p class="unit-strip-check"><strong>Pārbaude.</strong> {html.escape(strip["check"])}</p>'
        f'{wrong}'
        '</div>'
        '</details>'
    )


def render(chapter):
    strips = [s for s in STRIPS if s['chapter'] == chapter]
    if not strips:
        return ''
    heading = f'unit-strips-{chapter}'
    body = '\n'.join(_strip(s) for s in strips)
    return (
        f'<div class="unit-strips" aria-labelledby="{heading}">'
        f'<h3 id="{heading}">Mērvienību atcelšanas treniņš</h3>'
        f'<p>{html.escape(INTROS[chapter])}</p>\n'
        f'{body}\n'
        '</div>'
    )


def _result(strip):
    numeric = strip['numeric']
    if 'divisor' in numeric:
        return numeric['value'] / numeric['divisor']
    return unitcheck.convert(numeric['value'], numeric['frm'], numeric['to'])


def test():
    """Validate every strip and both kinds of deliberately wrong operation."""
    errors = []
    for strip in STRIPS:
        expected = strip['numeric']['expected']
        actual = _result(strip)
        if abs(actual - expected) > 1e-9:
            errors.append(f'unit strip {strip["key"]}: {actual} != {expected}')
        if not strip['factors']:
            errors.append(f'unit strip {strip["key"]}: no factors')
        for factor in strip['factors']:
            if not factor.get('num') or not factor.get('den') or not factor.get('cancel'):
                errors.append(f'unit strip {strip["key"]}: incomplete factor record')

    if abs(unitcheck.convert(18000, 'mg', 'g') - 18.0) > 1e-9:
        errors.append('unit strip mg-g: forward factor')
    if abs(unitcheck.convert(18.0, 'g', 'mg') - 18000.0) > 1e-9:
        errors.append('unit strip mg-g: round trip')
    if abs(unitcheck.convert(125, 'mL', 'L') - 0.125) > 1e-9:
        errors.append('unit strip ml-l: forward factor')
    if abs(unitcheck.convert(0.125, 'L', 'mL') - 125.0) > 1e-9:
        errors.append('unit strip ml-l: round trip')

    if abs(unitcheck.convert(18000, 'mg', 'g', factor=1000) - 18.0) <= 1e-9:
        errors.append('unit strip negative fixture: wrong mg factor was accepted')
    if abs(40.5 * 9.0 - 4.5) <= 1e-9:
        errors.append('unit strip negative fixture: multiplication was accepted')

    rendered = render(4) + render(8)
    if rendered.count('<details class="unit-strip"') != len(STRIPS):
        errors.append('unit strip render: wrong number of disclosure blocks')
    for needle in ('class="ufrac"', 'dalīts ar', 'ufrac-sep', 'href="#t-c10"'):
        if needle not in rendered:
            errors.append(f'unit strip render: missing {needle}')
    if 'style="' in rendered:
        errors.append('unit strip render: inline style attribute')
    return errors
