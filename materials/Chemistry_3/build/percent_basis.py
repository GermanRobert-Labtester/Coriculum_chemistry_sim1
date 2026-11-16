# -*- coding: utf-8 -*-
"""F02 percent-basis comparison workstation.

Three basis records are the single source for the table, the exclusive
disclosure cards and the one-answer prompt.  Every denominator is explicit,
every example is marked illustrative, and the classifier refuses unit
combinations that do not define one of the three bases.

Run: python3 -I build/percent_basis.py
"""
from __future__ import annotations

from dataclasses import dataclass
import html
import re
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


@dataclass(frozen=True)
class BasisRecord:
    key: str
    basis: str
    label: str
    numerator_entity: str
    numerator_unit: str
    denominator_entity: str
    denominator_unit: str
    denominator_scale: str
    equation: str
    percent_meaning: str
    requires: str
    warning: str
    example_given: str
    example_work: str
    example_result: str
    example_value: float
    example_expected: float
    illustrative: bool = True


MASS_FRACTION = BasisRecord(
    key='mm',
    basis='m/m',
    label='masas daļa w',
    numerator_entity='izšķīdinātā viela, m(B)',
    numerator_unit='g',
    denominator_entity='šķīdums, m(šķīdums)',
    denominator_unit='g',
    denominator_scale='uz 100 g šķīduma',
    equation='w = m(B)/m(šķīdums); w % = 100 · w',
    percent_meaning='5,0 % m/m = 5,0 g vielas uz 100 g šķīduma.',
    requires='m(viela) un m(šķīdums), abas gramos; vai m(viela), V un ρ.',
    warning=('Bez šķīduma masas w neaprēķina. 0,85 g/100 mL nav w/w: '
             '100 mL nav 100 g, un tilpums viens pats šķīduma masu nedod.'),
    example_given='5,0 g vielas + 95,0 g ūdens; šķīdums sver 100,0 g.',
    example_work='w = 5,0 g / 100,0 g',
    example_result='0,050 = 5,0 % (m/m); vienības: g/g = 1.',
    example_value=5.0 / 100.0,
    example_expected=0.05,
)

MASS_CONCENTRATION = BasisRecord(
    key='mv',
    basis='m/V',
    label='masas koncentrācija γ',
    numerator_entity='izšķīdinātā viela, m(B)',
    numerator_unit='g',
    denominator_entity='šķīdums, V(šķīdums)',
    denominator_unit='mL',
    denominator_scale='uz 100 mL šķīduma',
    equation='γ = m(B)/V(šķīdums); % (m/V) = g/100 mL',
    percent_meaning=('0,85 % m/V = 0,85 g vielas uz 100 mL šķīduma '
                     '= 8,5 g/L.'),
    requires=('m(viela) gramos un V(šķīdums) mililitros; vai abus pārrēķina '
              'uz saderīgām vienībām.'),
    warning=('Saucējs ir galīgais šķīduma tilpums, nevis pievienotā '
             'šķīdinātāja tilpums. 100 mL ūdens nav 100 mL šķīduma.'),
    example_given=('0,85 g vielas izšķīdināti un uzpildīti līdz 100 mL '
                   'šķīduma.'),
    example_work='γ = 0,85 g / 100 mL',
    example_result=('0,0085 g/mL = 0,85 g/100 mL = 8,5 g/L = 8,5 mg/mL; '
                    'vienības: g/mL, nav bezdimensiju.'),
    example_value=0.85 / 100.0,
    example_expected=0.0085,
)

VOLUME_FRACTION = BasisRecord(
    key='vv',
    basis='V/V',
    label='tilpuma daļa φ',
    numerator_entity='izšķīdinātās vielas tilpums, V(B)',
    numerator_unit='mL',
    denominator_entity='šķīdums, V(šķīdums)',
    denominator_unit='mL',
    denominator_scale='uz 100 mL šķīduma',
    equation='φ = V(B)/V(šķīdums); φ % = 100 · φ',
    percent_meaning='70 % V/V = 70 mL vielas uz 100 mL šķīduma.',
    requires=('V(viela) un V(šķīdums) vienās un tajās pašās tilpuma '
              'vienībās.'),
    warning=('Tilpumi nav precīzi aditīvi: 70 mL + 30 mL var nedot 100 mL. '
             'Masas daļai vajadzīgi abu šķidrumu blīvumi.'),
    example_given=('70 mL šķidruma atšķaidīti ar šķīdinātāju līdz 100 mL '
                   'šķīduma.'),
    example_work='φ = 70 mL / 100 mL',
    example_result=('0,70 = 70 % (V/V); vienības: mL/mL = 1. Galīgais '
                    'tilpums ir 100 mL, nevis 70 + 30 mL summa.'),
    example_value=70.0 / 100.0,
    example_expected=0.70,
)

BASES = (MASS_FRACTION, MASS_CONCENTRATION, VOLUME_FRACTION)

PROMPT = dict(
    id='procentu-bazes-uzdevums',
    question=('0,85 g vielas ir 100 mL šķīduma. Kura procenta bāze atbilst '
              'šim pierakstam?'),
    options=(
        dict(id='a', correct=False,
             text='m/m, jo 0,85 un 100 abi ir masas.',
             feedback=('Skaitītājs ir masa gramos, bet saucējs ir '
                       'tilpums mililitros; tas nav m/m.')),
        dict(id='b', correct=True,
             text='m/V, jo skaitītājs ir masa gramos, saucējs — šķīduma tilpums mililitros.',
             feedback=('0,85 g/100 mL ir m/V: 8,5 g/L. Blīvums nav '
                       'vajadzīgs, lai noteiktu bāzi; tas vajadzīgs tikai '
                       'pārrēķinam uz m/m.')),
        dict(id='c', correct=False,
             text='V/V, jo 100 mL ir tilpums.',
             feedback=('V/V prasa tilpumu arī skaitītājā; 0,85 ir '
                       'masa gramos.')),
        dict(id='d', correct=False,
             text='Bāzi nevar noteikt, jo nav dots blīvums.',
             feedback=('Skaidri norādītās vienības nosaka m/V. '
                       'Blīvums vajadzīgs tikai pārrēķinam uz m/m, nevis '
                       'bāzes atpazīšanai.')),
    ),
)

SOURCE_LABEL = dict(
    text='0,85 %',
    basis=None,
    note=('Avotā B, 9.a uzdevumā (BSC9) ir «0,85 %» bez procenta veida. '
          'Šī darbstacija to neklasificē. Atsevišķi norādītais 0,85 g/100 mL '
          'ir m/V; tas nav tas pats, kas avota etiķete bez vienībām.'),
)

DIMENSION = {'g': 'mass', 'mg': 'mass', 'mL': 'volume', 'L': 'volume'}
MEASUREMENT_RE = re.compile(
    r'^\s*[+-]?\d+(?:[.,]\d+)?\s*(g|mg|mL|L)\s*/\s*(?:100\s*)?(g|mg|mL|L)\s*$'
)


def classify_units(numerator_unit: str, denominator_unit: str) -> str:
    """Return the basis determined by explicit units; refuse anything else."""
    try:
        numerator = DIMENSION[numerator_unit]
        denominator = DIMENSION[denominator_unit]
    except KeyError as exc:
        raise ValueError(f'unsupported unit: {exc.args[0]}') from None
    pair = (numerator, denominator)
    if pair == ('mass', 'mass'):
        return 'm/m'
    if pair == ('mass', 'volume'):
        return 'm/V'
    if pair == ('volume', 'volume'):
        return 'V/V'
    raise ValueError(f'incompatible units: {numerator_unit}/{denominator_unit}')


def classify_measurement(text: str) -> str:
    """Classify a written ratio such as '0,85 g/100 mL' from its units."""
    match = MEASUREMENT_RE.fullmatch(text or '')
    if not match:
        raise ValueError('measurement is not a supported ratio')
    return classify_units(match.group(1), match.group(2))


def mass_fraction(m_solute_g: float, solution_mass_g: float | None) -> float:
    """w = m(B)/m(solution); never guess the solution mass from a volume."""
    if solution_mass_g is None:
        raise ValueError('w/w needs the solution mass; a volume alone is not enough')
    if solution_mass_g <= 0:
        raise ValueError('solution mass must be positive')
    return m_solute_g / solution_mass_g


def _lv(value: float, decimals: int) -> str:
    return f'{value:.{decimals}f}'.replace('.', ',')


def validate_records() -> list[str]:
    errors: list[str] = []
    if len(BASES) != 3:
        errors.append(f'expected three basis records, got {len(BASES)}')
    keys = {record.basis for record in BASES}
    if keys != {'m/m', 'm/V', 'V/V'}:
        errors.append(f'basis set is {sorted(keys)}')
    for record in BASES:
        try:
            classified = classify_units(record.numerator_unit, record.denominator_unit)
        except ValueError as exc:
            errors.append(f'{record.basis}: {exc}')
            continue
        if classified != record.basis:
            errors.append(f'{record.basis}: units classify as {classified}')
        if not record.denominator_entity or not record.denominator_unit:
            errors.append(f'{record.basis}: denominator is not explicit')
        if not record.illustrative:
            errors.append(f'{record.basis}: example is not marked illustrative')
        if abs(record.example_value - record.example_expected) > 1e-12:
            errors.append(f'{record.basis}: example arithmetic differs')
    if classify_measurement('0,85 g/100 mL') != 'm/V':
        errors.append('0.85 g/100 mL is not classified as m/V')
    if classify_measurement('5,0 g/100 g') != 'm/m':
        errors.append('5.0 g/100 g is not classified as m/m')
    if classify_measurement('70 mL/100 mL') != 'V/V':
        errors.append('70 mL/100 mL is not classified as V/V')
    try:
        classify_units('g', 'mol')
        errors.append('g/mol was accepted as a percent basis')
    except ValueError:
        pass
    try:
        mass_fraction(0.85, None)
        errors.append('w/w was calculated without the solution mass')
    except ValueError:
        pass
    if SOURCE_LABEL['basis'] is not None:
        errors.append('source label with no percent kind was silently classified')
    prompt_correct = [option for option in PROMPT['options'] if option['correct']]
    if len(prompt_correct) != 1:
        errors.append(f'prompt must have exactly one correct option, got {len(prompt_correct)}')
    return errors


def _basis_row(record: BasisRecord) -> str:
    basis = html.escape(record.basis)
    return (
        f'<tr data-basis="{html.escape(record.key, quote=True)}">'
        f'<th scope="row"><strong>{basis}</strong><br><span class="basis-label">{html.escape(record.label)}</span></th>'
        f'<td>{html.escape(record.numerator_entity)}<br><span class="unit">{html.escape(record.numerator_unit)}</span></td>'
        f'<td>{html.escape(record.denominator_entity)}<br><span class="unit">{html.escape(record.denominator_unit)}</span>; {html.escape(record.denominator_scale)}</td>'
        f'<td>{html.escape(record.equation)}</td>'
        f'<td>{html.escape(record.percent_meaning)}</td>'
        f'</tr>'
    )


def _basis_card(record: BasisRecord) -> str:
    return f'''<details class="basis-card" name="procentu-baze" data-basis-card="{html.escape(record.key, quote=True)}">
  <summary>{html.escape(record.basis)} — {html.escape(record.label)}</summary>
  <div class="basis-body">
    <ul class="basis-meta">
      <li><strong>Skaitītājs:</strong> {html.escape(record.numerator_entity)} ({html.escape(record.numerator_unit)}).</li>
      <li><strong>Saucējs:</strong> {html.escape(record.denominator_entity)} ({html.escape(record.denominator_unit)}), {html.escape(record.denominator_scale)}.</li>
      <li><strong>Vienādojums:</strong> {html.escape(record.equation)}.</li>
      <li><strong>Kas jāzina:</strong> {html.escape(record.requires)}</li>
    </ul>
    <p class="basis-example"><span class="prov p-ill">Ilustratīvs piemērs.</span> {html.escape(record.example_given)} {html.escape(record.example_work)} = <strong>{html.escape(record.example_result)}</strong></p>
    <p class="basis-warning"><strong>Brīdinājums.</strong> {html.escape(record.warning)}</p>
  </div>
</details>'''


def _prompt_option(option: dict) -> str:
    verdict = 'Pareizi.' if option['correct'] else 'Nepareizi.'
    return f'''<details class="basis-option" name="procentu-bazes-atbilde" data-answer="{html.escape(option['id'], quote=True)}">
  <summary>{html.escape(option['id'].upper())}. {html.escape(option['text'])}</summary>
  <div class="basis-feedback"><p><strong>{verdict}</strong> {html.escape(option['feedback'])}</p></div>
</details>'''


def render() -> str:
    rows = ''.join(_basis_row(record) for record in BASES)
    cards = ''.join(_basis_card(record) for record in BASES)
    options = ''.join(_prompt_option(option) for option in PROMPT['options'])
    return f'''<section class="basis-workstation" id="procentu-bazes" aria-labelledby="procentu-bazes-title">
  <h3 id="procentu-bazes-title">Procenta bāzes darbstacija: kas ir saucējs?</h3>
  <p class="lead">Viens un tas pats skaitlis procentos var apzīmēt dažādu sastāvu. Vispirms nosakiet <strong>skaitītāju</strong> un <strong>saucēju</strong>, tad vienības. Tikai pēc tam var runāt par pārrēķinu.</p>

  <div class="table-wrap">
    <table>
      <caption>Procenta bāzes: skaitītājs, saucējs un vienības · <span class="prov p-add">papildinājums</span></caption>
      <thead><tr><th scope="col">Bāze</th><th scope="col">Skaitītājs</th><th scope="col">Saucējs</th><th scope="col">Vienādojums</th><th scope="col">Ko nozīmē procents</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>

  <p class="basis-select-hint"><strong>Izvēlieties vienu bāzi.</strong> Sākumā neviena nav atvērta; atveriet to, kuru pārbaudāt. Katrā kartē ir viens skaidri nosaukts saucējs, vienības un ilustratīvs piemērs.</p>
  <div class="basis-cards">{cards}</div>

  <div class="recall-block basis-prompt" id="{html.escape(PROMPT['id'], quote=True)}">
    <p class="basis-prompt-label">Vienizvēles pārbaude</p>
    <p><strong>{html.escape(PROMPT['question'])}</strong> Atveriet vienu atbildi; pareizā atbilde paskaidro, kāpēc vienības nosaka bāzi.</p>
    <div class="basis-options">{options}</div>
  </div>

  <div class="source-note" data-role="source">
    <p class="source-note-label">Piezīme avotam</p>
    <p><strong>Robeža.</strong> {html.escape(SOURCE_LABEL['note'])} Tāpēc <strong>0,85 %</strong> vien neļauj noteikt bāzi, bet <strong>0,85 g/100 mL</strong> ir m/V. Ja būtu jāaprēķina w/w, vajadzīga šķīduma masa: 100 mL · ρ, nevis pieņēmums, ka 100 mL sver 100 g.</p>
  </div>

  <p class="basis-refusal"><strong>Ja vienības nesader</strong> (piemēram, g pret mol), bāzi nevar noteikt un aprēķins nav veicams. Šī lapa nav kalkulators: tā neveic pārrēķinu starp bāzēm bez blīvuma vai galīgā tilpuma.</p>
  <p class="source-line"><span class="prov p-add">Papildinājums.</span> Salīdzinājums veidots no <code>build/percent_basis.py</code> datiem; skatiet arī <a href="#k-k11">K11</a> un <a href="#k-k23">K23</a>. Piemēri ir ilustratīvi, nevis avota etiķešu klasifikācija.</p>
</section>'''


def audit(doc: str) -> list[str]:
    errors: list[str] = []
    rendered = render()
    if doc.count('id="procentu-bazes"') != 1:
        errors.append('percent-basis workstation must render exactly once')
    if rendered.count('data-basis-card=') != len(BASES):
        errors.append('basis card count differs from records')
    if rendered.count('<tr data-basis=') != len(BASES):
        errors.append('basis table row count differs from records')
    if rendered.count('name="procentu-baze"') != len(BASES):
        errors.append('basis cards are not an exclusive disclosure group')
    if rendered.count('name="procentu-bazes-atbilde"') != len(PROMPT['options']):
        errors.append('prompt options are not an exclusive disclosure group')
    if '<caption>' not in rendered:
        errors.append('basis table has no caption')
    if rendered.count('scope="col"') != 5:
        errors.append('basis table does not have five column headers')
    if rendered.count('scope="row"') != len(BASES):
        errors.append('basis table does not have one row header per basis')
    for bad in ('<script', 'style=', 'onclick=', 'http://', 'https://',
                'localStorage', 'sessionStorage', 'innerHTML', '<input'):
        if bad in rendered:
            errors.append(f'percent-basis workstation contains forbidden {bad!r}')
    for record in BASES:
        if f'data-basis="{record.key}"' not in rendered:
            errors.append(f'percent-basis workstation omits {record.basis}')
    if '0,85 g/100 mL' not in rendered or 'nav w/w' not in rendered:
        errors.append('0.85 g/100 mL classification is not stated')
    if 'bez procenta veida' not in rendered or 'neklasificē' not in rendered:
        errors.append('source label without a percent kind is not left unclassified')
    for anchor in ('k-k11', 'k-k23'):
        if f'id="{anchor}"' not in doc:
            errors.append(f'percent-basis link target missing: #{anchor}')
    start = doc.find('id="n6"')
    end = doc.find('id="n7"')
    position = doc.find('id="procentu-bazes"')
    if not (0 <= start < position < end):
        errors.append('percent-basis workstation is not inside or beside chapter 6')
    if '.basis-cards{display:block}' not in doc:
        errors.append('percent-basis workstation has no print linearisation')
    section = doc[position:doc.find('</section>', position)]
    if 'role="region"' not in section or 'tabindex="0"' not in section:
        errors.append('basis table is not a keyboard-scrollable region')
    if not re.search(r'<caption id="table-[^"]+"', section):
        errors.append('basis table caption has no stable id')
    return errors


def test() -> list[str]:
    return validate_records()


def report() -> list[str]:
    errors = validate_records()
    print(f'percent basis: {len(BASES)} records, {len(PROMPT["options"])} prompt options; '
          f'0.85 g/100 mL -> {classify_measurement("0,85 g/100 mL")}; errors: {len(errors)}')
    for error in errors:
        print('  -', error)
    return errors


if __name__ == '__main__':
    raise SystemExit(1 if report() else 0)
