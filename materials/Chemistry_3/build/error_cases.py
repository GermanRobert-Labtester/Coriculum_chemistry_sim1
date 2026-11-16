# -*- coding: utf-8 -*-
"""F06 — first-error diagnosis cases for verified tasks.

Each case is a short solution line sequence attached to an existing task.
`valid_until` is the 0-based index of the first invalid line: every line
before it is a correct prefix, the line at that index is the answer.
Radio feedback is native HTML/CSS (no JavaScript, no score, no history).
Every numeric line and corrected value is recomputed by `audit()`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from calc import M

ERROR_TYPES = {
    'denominator': 'saucējs — šķīduma masa',
    'density': 'blīvums — tilpums nav masa',
    'ion-coefficient': 'disociācijas koeficients',
    'mass-balance': 'masas bilance',
    'unit-conversion': 'mērvienību pārvēršana',
    'formula-inversion': 'formulas izteiksme',
    'molar-mass': 'molmasa',
    'dose-application': 'devas piemērošana',
    'final-vs-added': 'gala tilpums pret pievienoto',
    'mixing-average': 'vidējais aritmētiskais',
    'rounding': 'priekšlaicīga noapaļošana',
}

CASES = {}


def L(html, calc=None, value=None, dp=0):
    return {'html': html, 'calc': calc, 'value': value, 'dp': dp}


def C(task, error_type, lines, valid_until, corrected, corrected_calc,
      corrected_value, corrected_dp, rationale):
    assert error_type in ERROR_TYPES, error_type
    CASES[task] = dict(task=task, error_type=error_type, label=ERROR_TYPES[error_type],
                       lines=lines, valid_until=valid_until,
                       corrected=corrected, corrected_calc=corrected_calc,
                       corrected_value=corrected_value, corrected_dp=corrected_dp,
                       rationale=rationale)


# 1. C6 — denominator omits the dissolved solid.
C('C6', 'denominator',
  [L('<i>m</i>(šķīdums) = 45 + 700,0 = 745 g', lambda: 45 + 700.0, 745.0, 0),
   L('<i>w</i> = 45/700 · 100 = 6,43 %', lambda: 45 / 700 * 100, 6.43, 2),
   L('Atbilde: <i>w</i> = 6,43 %')],
  1,
  '<i>w</i> = 45/(700 + 45) · 100 = 6,04 %',
  lambda: 45 / (700 + 45) * 100, 6.04, 2,
  'Saucējā jābūt visa šķīduma masai: 45 g vielas + 700 g ūdens = 745 g. '
  'Dalījums ar 700 g skaita tikai ūdeni, tāpēc atbilde ir par lielu.')

# 2. C7 — volume used as if it were mass.
C('C7', 'density',
  [L('<i>m</i>(šķīdums) = 500,0 · 1,07 = 535,0 g', lambda: 500.0 * 1.07, 535.0, 1),
   L('<i>w</i> = 5,0/500 · 100 = 1,0 %', lambda: 5.0 / 500 * 100, 1.0, 1),
   L('Atbilde: <i>w</i> = 1,0 %')],
  1,
  '<i>m</i>(šķīdums) = 500,0 · 1,07 = 535,0 g; <i>w</i> = 5,0/535,0 · 100 = 0,93 %',
  lambda: 5.0 / (500.0 * 1.07) * 100, 0.93, 2,
  '500 mL šķīduma nav 500 g: ar ρ = 1,07 g/mL masa ir 535,0 g. '
  'Tilpumu drīkst likt masas daļas saucējā tikai pēc pārrēķina ar blīvumu.')

# 3. C19 — ion count divided by the number of ions.
C('C19', 'ion-coefficient',
  [L('<i>c</i>(NaCl) = 0,70 mol/L (dots)', lambda: 0.70, 0.70, 2),
   L('<i>c</i>(Na<sup>+</sup>) = 0,70/2 = 0,35 mol/L', lambda: 0.70 / 2, 0.35, 2),
   L('Atbilde: <i>c</i>(Na<sup>+</sup>) = 0,35 mol/L')],
  1,
  '<i>c</i>(Na<sup>+</sup>) = 1 · 0,70 = 0,70 mol/L',
  lambda: 1 * 0.70, 0.70, 2,
  'Viena NaCl formulas vienība dod vienu Na⁺ jonu, tāpēc koeficients ir 1, '
  'nevis 1/2. Dalīšana ar jonu skaitu sajauc daudzumu ar koncentrāciju.')

# 4. C9 — dilution mass balance drops the initial solution mass.
C('C9', 'mass-balance',
  [L('Vielas masa nemainās: 0,3·<i>m</i><sub>1</sub> = 0,1·<i>m</i><sub>2</sub>.'),
   L('0,3·<i>m</i><sub>1</sub> = 0,1 · 300 → <i>m</i><sub>1</sub> = 100 g', lambda: 0.1 * 300 / 0.3, 100.0, 0),
   L('Atbilde: jāņem 100 g 30 % šķīduma')],
  1,
  '0,3·<i>m</i><sub>1</sub> = 0,1(<i>m</i><sub>1</sub> + 300) → <i>m</i><sub>1</sub> = 150 g',
  lambda: 0.1 * 300 / (0.3 - 0.1), 150.0, 0,
  'Gala masa ir <i>m</i><sub>1</sub> + 300, nevis tikai 300 g. '
  'Labajā pusē pazūd pats koncentrētais šķīdums, tāpēc vienādojums dod 100 g.')

# 5. C2.2 — millilitres not converted to litres.
C('C2.2', 'unit-conversion',
  [L('<i>V</i> = 125 mL = 0,125 L', lambda: 125 / 1000, 0.125, 3),
   L('<i>n</i> = 0,400 · 125 = 50 mol', lambda: 0.400 * 125, 50.0, 0),
   L('Atbilde: <i>n</i> = 50 mol')],
  1,
  '<i>n</i> = 0,400 · 0,125 = 0,0500 mol',
  lambda: 0.400 * (125 / 1000), 0.0500, 4,
  'Koncentrācija ir mol/L, tāpēc tilpumam jābūt litros: 125 mL = 0,125 L. '
  'Reizināšana ar 125 dod skaitli, kas atbilst mol/L · mL, nevis moliem.')

# 6. C2.1 — formula inverted.
C('C2.1', 'formula-inversion',
  [L('Dots: <i>c</i> = 1,00 mol/L; <i>V</i> = 2,50 L.'),
   L('<i>n</i> = <i>c</i>/<i>V</i> = 1,00/2,50 = 0,40 mol', lambda: 1.00 / 2.50, 0.40, 2),
   L('Atbilde: <i>n</i> = 0,40 mol')],
  1,
  '<i>n</i> = <i>c</i> · <i>V</i> = 1,00 · 2,50 = 2,50 mol',
  lambda: 1.00 * 2.50, 2.50, 2,
  'No definīcijas c = n/V izriet n = c·V. Dalīšana ar tilpumu dod mol/L², '
  'kas nav molu vienība; tāpēc formula ir apgriezta.')

# 7. C3.2 — molar mass drops the formula indices.
C('C3.2', 'molar-mass',
  [L('Dots: <i>m</i>(Na<sub>2</sub>CO<sub>3</sub>) = 53,0 g; <i>V</i> = 2,50 L.'),
   L('<i>M</i>(Na<sub>2</sub>CO<sub>3</sub>) = 23 + 12 + 16 = 51 g/mol', lambda: 23 + 12 + 16, 51.0, 0),
   L('<i>c</i> = (53,0/51)/2,50 = 0,42 mol/L', lambda: (53.0 / 51) / 2.50, 0.42, 2)],
  1,
  '<i>M</i> = 2·22,99 + 12,01 + 3·16,00 = 105,99 g/mol; <i>c</i> = (53,0/105,99)/2,50 = 0,200 mol/L',
  lambda: (53.0 / M('Na2CO3')) / 2.50, 0.200, 3,
  'Formulas indeksi 2 un 3 pieder pie Na un O: M = 2·22,99 + 12,01 + 3·16,00 = 105,99 g/mol. '
  'Ar 51 g/mol molu skaits un koncentrācija tiek mākslīgi dubultoti.')

# 8. C12 — the per-10-kg dose is applied a second time.
C('C12', 'dose-application',
  [L('Deva uz kg: 450/10 = 45,0 mg/kg', lambda: 450 / 10, 45.0, 1),
   L('Kopējā deva: 45,0 · 70 = 3150 mg', lambda: (450 / 10) * 70, 3150.0, 0),
   L('<i>V</i> = 3150/150 · 10 = 210 mL', lambda: 3150 / 150 * 10, 210.0, 0)],
  2,
  '<i>V</i> = 3150/150 = 21,0 mL',
  lambda: 3150 / 150, 21.0, 1,
  '450 mg jau ir deva uz 10 kg, tāpēc vispirms iegūst 45 mg/kg un tikai tad reizina ar 70 kg. '
  'Pēdējā rindā reizināšana ar 10 notiek otrreiz; 150 mg/mL jau satur visu tilpumu.')

# 9. C16 — final volume reported as added water.
C('C16', 'final-vs-added',
  [L('<i>V</i><sub>1</sub> = 0,10 · 450,0/3,0 = 15 mL', lambda: 0.10 * 450.0 / 3.0, 15.0, 0),
   L('Jāpievieno 15 mL ūdens', lambda: 0.10 * 450.0 / 3.0, 15.0, 0)],
  1,
  '<i>V</i>(ūdens) = 450,0 − 15,0 = 435 mL',
  lambda: 450.0 - 15.0, 435.0, 0,
  '15 mL ir 3,0 mol/L šķīduma tilpums, kas jāatšķaida līdz 450 mL. '
  'Pievienojamais ūdens ir starpība 450,0 − 15,0 = 435 mL.')

# 10. C18 — arithmetic mean for unequal volumes.
C('C18', 'mixing-average',
  [L('<i>n</i>(kopā) = 0,0350 + 0,0390 = 0,0740 mol', lambda: 0.0350 + 0.0390, 0.0740, 4),
   L('<i>c</i> = 0,0740/0,100 = 0,740 mol/L', lambda: 0.0740 / 0.100, 0.740, 3),
   L('Vidējais: (1,00 + 0,600)/2 = 0,800 mol/L', lambda: (1.00 + 0.600) / 2, 0.800, 3)],
  2,
  '<i>c</i> = (0,0350 + 0,0390)/0,100 = 0,740 mol/L',
  lambda: (0.0350 + 0.0390) / 0.100, 0.740, 3,
  'Vidējais aritmētiskais der tikai vienādiem tilpumiem. Šeit 100 mL un 600 mL '
  'ir nesamērīgi, tāpēc jāsaskaita moli un jādala ar kopējo tilpumu 0,100 L.')

# 11. BEx7I — premature rounding before the density division.
C('BEx7I', 'rounding',
  [L('<i>n</i> = 0,1 · 0,500 = 0,0500 mol', lambda: 0.1 * 0.500, 0.0500, 4),
   L('<i>m</i>(H<sub>2</sub>SO<sub>4</sub>) = 0,0500 · 98,08 = 4,904 g', lambda: 0.0500 * M('H2SO4'), 4.904, 3),
   L('<i>m</i>(96 %) = 4,904/0,96 = 5,108 g', lambda: 4.904 / 0.96, 5.108, 3),
   L('<i>V</i> = 5,1/1,84 = 2,77 mL', lambda: 5.1 / 1.84, 2.77, 2)],
  3,
  '<i>V</i> = 5,108/1,84 = 2,78 mL',
  lambda: 5.108 / 1.84, 2.78, 2,
  'Ar deklarēto M = 98,08 g/mol starprezultātu 5,108 g nedrīkst noapaļot uz 5,1 g pirms '
  'dalīšanas ar blīvumu: 2,776 mL ≈ 2,78 mL, bet 5,1/1,84 = 2,77 mL. Avots B lieto citu '
  'molmasu (M = 98,00 g/mol), ar kuru arī 5,104/1,84 = 2,774 mL noapaļojas uz 2,77 mL, '
  'tāpēc avota atbilde nav kļūda — kļūda ir sajaukt abas M vērtības vienā uzdevumā (K12).')


def _safe_id(tid):
    return tid.lower().replace(' ', '').replace('.', '-').replace('/', '-').replace('*', 's')


def _tol(dp):
    return 0.5 * 10 ** (-dp) + 1e-9


def audit(tasks=None):
    """Recompute every line and reject malformed or unrecomputable cases."""
    if tasks is None:
        import tasks_a, tasks_b  # noqa: F401  (register task data)
        import taskbase
        tasks = taskbase.TASKS
    errors = []
    for tid, c in CASES.items():
        if tid not in tasks:
            errors.append(f'first-error {tid}: task not found in TASKS registry')
        lines = c['lines']
        n = len(lines)
        if not 2 <= n <= 6:
            errors.append(f'first-error {tid}: {n} lines, expected 2–6')
        vu = c['valid_until']
        if not isinstance(vu, int) or not 0 <= vu < n:
            errors.append(f'first-error {tid}: valid_until {vu} outside 0..{n - 1}')
            continue
        if vu == 0:
            errors.append(f'first-error {tid}: no correct prefix before the first error')
        for i, line in enumerate(lines):
            calc = line.get('calc')
            if calc is None:
                continue
            got = calc()
            if abs(got - line['value']) > _tol(line['dp']):
                errors.append(f'first-error {tid} line {i + 1}: recomputed {got:.6g} != stated {line["value"]}')
        if not any(line.get('calc') is not None for line in lines[vu:vu + 1]):
            errors.append(f'first-error {tid}: first invalid line has no recomputed number')
        if not any(line.get('calc') is not None for line in lines):
            errors.append(f'first-error {tid}: no recomputable numeric line')
        got = c['corrected_calc']()
        if abs(got - c['corrected_value']) > _tol(c['corrected_dp']):
            errors.append(f'first-error {tid}: corrected {got:.6g} != stated {c["corrected_value"]}')
        if not c['corrected'] or not c['rationale']:
            errors.append(f'first-error {tid}: corrected line or rationale missing')
        if c['error_type'] not in ERROR_TYPES:
            errors.append(f'first-error {tid}: unknown error type {c["error_type"]}')
    return errors


def render(tid):
    c = CASES[tid]
    sid = _safe_id(tid)
    vu = c['valid_until']
    out = [f'<details class="first-error" id="fe-{sid}">',
           f'<summary>Atrodi pirmo kļūdu <span class="fe-summary-type">· {c["label"]}</span></summary>',
           '<p class="fe-intro">Zemāk ir īss risinājums. Atzīmējiet <strong>pirmo</strong> rindu, '
           'kurā parādās kļūda, un pēc tam salīdziniet ar laboto rindu. Šis bloks ir neobligāts; '
           'uzdevuma atbilde augstāk paliek pieejama arī bez izvēles.</p>',
           '<fieldset class="fe-fieldset">',
           '<legend>Kura rinda ir pirmā kļūdainā?</legend>',
           '<ol class="fe-lines">']
    for i, line in enumerate(c['lines']):
        if i < vu:
            note = '<p class="fe-note fe-note-valid" aria-live="polite" aria-atomic="true">Šī rinda ir pareiza — pirmā kļūda ir vēlāk.</p>'
        elif i == vu:
            note = (f'<p class="fe-note fe-note-first" aria-live="polite" aria-atomic="true">Pareizi: šī ir pirmā kļūdainā rinda. '
                    f'Kļūdas tips: {c["label"]}.</p>')
        else:
            note = ('<p class="fe-note fe-note-late" aria-live="polite" aria-atomic="true">Šī rinda nav pirmā kļūdainā — '
                    'iepriekš jau ir kļūda.</p>')
        out += [f'<li class="fe-option">',
                f'<input type="radio" id="fe-{sid}-{i + 1}" name="fe-{sid}" value="{i + 1}">',
                f'<label for="fe-{sid}-{i + 1}"><span class="fe-num">{i + 1}.</span> {line["html"]}</label>',
                note,
                '</li>']
    out += ['</ol>', '</fieldset>',
            '<div class="fe-solution">',
            f'<p><strong>Labotā rinda:</strong> {c["corrected"]}</p>',
            f'<p><strong>Kāpēc:</strong> {c["rationale"]}</p>',
            f'<p class="fe-source">Avota uzdevums: <a href="#t-{sid}">{tid}</a>.</p>',
            '</div>', '</details>']
    return '\n'.join(out)


def test_states():
    """No default selection; every earlier line is explicitly rejected."""
    for tid, c in CASES.items():
        out = render(tid)
        sid = _safe_id(tid)
        if 'checked' in out:
            raise AssertionError(f'first-error {tid}: a radio is preselected')
        if f'name="fe-{sid}"' not in out:
            raise AssertionError(f'first-error {tid}: radio group name missing')
        if out.count('fe-note-first') != 1:
            raise AssertionError(f'first-error {tid}: expected exactly one first-error note')
        valid_notes = out.count('fe-note-valid')
        if valid_notes != c['valid_until']:
            raise AssertionError(f'first-error {tid}: {valid_notes} valid-line notes, expected {c["valid_until"]}')
        late = len(c['lines']) - c['valid_until'] - 1
        if out.count('fe-note-late') != late:
            raise AssertionError(f'first-error {tid}: late-line note count mismatch')
        if 'punkt' in out.lower() or 'score' in out.lower():
            raise AssertionError(f'first-error {tid}: score language must not appear')
    return True


def test_invalid_index():
    """An out-of-range valid_until must be rejected by the gate, not rendered."""
    saved = CASES['C6']
    bad = dict(saved)
    bad['valid_until'] = 99
    CASES['C6'] = bad
    try:
        errs = audit({'C6': {}})
    finally:
        CASES['C6'] = saved
    if not any('valid_until' in e for e in errs):
        raise AssertionError('Out-of-range valid_until was not rejected')
    return True


def report():
    print(f'first-error cases: {len(CASES)}; types: {len({c["error_type"] for c in CASES.values()})}')
    print('tasks:', ', '.join(sorted(CASES)))
    return {'cases': len(CASES)}


if __name__ == '__main__':
    errs = audit()
    if errs:
        raise SystemExit('\n'.join(errs))
    test_states()
    report()
