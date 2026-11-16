# -*- coding: utf-8 -*-
import re
"""F09: the single registry of Topic 1 core formulas and their assumptions.

Before this file the same nine formulas lived in two unlinked places: the nine-row
list inside build_master.py::formula_card() and the six-row hand-written table in
build/content/ch17.html (#formulu-pienemumi). Nothing compared them, so a wording or
unit edit on one side silently diverged from the other. The registry is now the only
source: card_html() renders the appendix summary sheet, assumptions_html() renders the
assumptions table, and build/check_links.py proves both against the shipped master
(audit_formula_registry).

Deliberately NOT here: the printable one-page "formula-sheet" the F09 roadmap row asks
for. The appendix already carries this content (assumptions, units, worked examples and,
in #formulu-pienemumi, the failure mode when an assumption breaks), the F09 verdict is
[LOW-PRIORITY / DEFER] pending learner evidence, and the master sits 92.6 KB over its
size ceiling (ISS-14), so a third formula table is not shipped. F09_REPORT.md records
the decision, the premise corrections and the blueprint.

Fields
------
id        stable slug; the assumptions rows reference it through ASSUMPTIONS["of"]
n         printed ordinal in the appendix card (assigned from position, never typed)
title     row heading as printed
eq        the relation, semantic HTML (the builder rewrites <i> to <var>)
lielumi   every symbol with its unit — F09 requires "every symbol/unit defined"
pieņēmumi  the boundary assumption; when it does not hold the formula is wrong
piemērs   one worked example carrying its own units
simboli   the symbols the lielumi cell defines, written in plain() form (the
          sub/superscripts already folded); the gate checks each one really
          occurs in that cell, so quietly dropping a unit fails the build
saite     master anchor where the relation is taught; the gate checks it resolves
"""

FORMULAS = [
    {
        "id": 'w',
        "title": '1. Masas daļa <i>w</i>',
        "eq": '<i>w</i> = <i>m</i><sub>v</sub> / <i>m</i><sub>šķ</sub>',
        "lielumi": '<i>m</i><sub>v</sub>: vielas masa; <i>m</i><sub>šķ</sub> = <i>m</i><sub>v</sub> + <i>m</i>(H₂O) = <i>V</i>·ρ (šķīduma masa, g).',
        "pieņēmumi": 'Homogēns šķīdums.',
        "piemērs": '10\u202fg NaCl 90\u202fg ūdens: <i>m</i><sub>šķ</sub> = 100\u202fg, <i>w</i> = 10/100 = 0,10 (10\u202f%).',
        "simboli": ["mv", "m\u0161\u0137"],
        "saite": 'def-conc',
    },
    {
        "id": 'c-nV',
        "title": '2. Molārā koncentrācija <i>c</i>',
        "eq": '<i>c</i> = <i>n</i> / <i>V</i> = <i>m</i> / (<i>M</i> · <i>V</i>)',
        "lielumi": '<i>n</i>: daudzums (mol); <i>V</i>: <b>šķīduma</b> tilpums (L); <i>M</i>: molmasa (g/mol).',
        "pieņēmumi": '<i>V</i> ir šķīduma, nevis ūdens tilpums.',
        "piemērs": '0,20\u202fmol NaOH 0,500\u202fL: <i>c</i> = 0,20/0,500 = 0,40\u202fmol/L.',
        "simboli": ['n', 'V', 'M'],
        "saite": 'def-conc',
    },
    {
        "id": 'c-w',
        "title": '3. Pāreja starp <i>w</i> un <i>c</i>',
        "eq": '<i>c</i> = 10 · <i>w</i> · ρ / <i>M</i>',
        "lielumi": '<i>w</i>: %; ρ: blīvums g/mL; <i>M</i>: molmasa g/mol.',
        "pieņēmumi": '<i>w</i> ir % un ρ ir g/mL.',
        "piemērs": '22\u202f% NaOH, ρ = 1,25\u202fg/mL, <i>M</i> = 40,0\u202fg/mol: <i>c</i> = 10·22·1,25/40,0 = 6,88\u202fmol/L.',
        "simboli": ["w", "\u03c1", "M"],
        "saite": 'koncentracija',
    },
    {
        "id": 'dilute',
        "title": '4. Atšķaidīšanas likums',
        "eq": '<i>c</i>₁ · <i>V</i>₁ = <i>c</i>₂ · <i>V</i>₂',
        "lielumi": '<i>c</i>: koncentrācija; <i>V</i>: tilpums vienādās mērvienībās.',
        "pieņēmumi": 'Tikai atšķaidīšana: pievieno šķīdinātāju (<i>n</i>₁ = <i>n</i>₂). Aizliegts lietot caur ķīmisku reakciju, kur <i>n</i> mainās.',
        "piemērs": '50\u202fmL 2,0\u202fmol/L atšķaida līdz 250\u202fmL: <i>c</i>₂ = 2,0·50/250 = 0,40\u202fmol/L.',
        "simboli": ['c', 'V'],
        "saite": 'koncentracija',
    },
    {
        "id": 'kw',
        "title": '5. Ūdens jonu reizinājums <i>K</i><sub>w</sub>',
        "eq": '<i>K</i><sub>w</sub> = [H⁺][OH⁻] = 1,0 · 10⁻¹⁴',
        "lielumi": '[H⁺], [OH⁻]: koncentrācijas (mol/L).',
        "pieņēmumi": 'Ūdens šķīdums pie 25\u202f°C.',
        "piemērs": 'Ja [H⁺] = 10⁻³\u202fmol/L: [OH⁻] = 10⁻¹⁴/10⁻³ = 10⁻¹¹\u202fmol/L.',
        "simboli": ["H+", "OH\u2212"],
        "saite": 'ph',
    },
    {
        "id": 'ph',
        "title": '6. pH un pOH',
        "eq": 'pH = −lg[H⁺]; pH + pOH = 14',
        "lielumi": 'pH ir [H⁺] negatīvais decimāllogaritms.',
        "pieņēmumi": 'Atšķaidīts šķīdums, 25\u202f°C.',
        "piemērs": 'Ja [H⁺] = 10⁻³\u202fmol/L: pH = 3,00 (skāba vide).',
        "simboli": ['pH'],
        "saite": 'ph',
    },
    {
        "id": 'alpha',
        "title": '7. Disociācijas pakāpe α',
        "eq": 'α = <i>N</i><sub>dis</sub> / <i>N</i>₀ = <i>c</i><sub>dis</sub> / <i>c</i>₀',
        "lielumi": '<i>N</i><sub>dis</sub>: disociējušo daļiņu skaits; <i>N</i>₀: kopējais daļiņu skaits.',
        "pieņēmumi": 'Stipriem α ≈ 1, vājiem α &lt;&lt; 1.',
        "piemērs": 'Ja no 200 molekulām disociē 4: α = 4/200 = 0,02 (2\u202f%).',
        "simboli": ["Ndis", "N0"],
        "saite": 'def-alpha',
    },
    {
        "id": 'n',
        "title": '8. Vielas daudzums <i>n</i>',
        "eq": '<i>n</i> = <i>m</i> / <i>M</i> = <i>V</i> / <i>V</i>₀ = <i>N</i> / <i>N</i><sub>A</sub>',
        "lielumi": '<i>M</i>: molmasa; <i>V</i>₀ = 22,414\u202fL/mol pie 0\u202f°C, 101,325\u202fkPa (ideāla gāze); <i>N</i><sub>A</sub> = 6,022·10²³\u202fmol⁻¹.',
        "pieņēmumi": '<i>V</i>/<i>V</i>₀ der tikai gāzēm ar norādītiem T un p. Aizliegts 22,414\u202fL/mol bez apstākļiem vai šķidrumiem/cietvielām.',
        "piemērs": '4,48\u202fL CO₂ pie 0\u202f°C, 101,325\u202fkPa: <i>n</i> = 4,48/22,414 ≈ 0,200\u202fmol.',
        "simboli": ["M", "V0", "NA"],
        "saite": 'def-stoich',
    },
    {
        "id": 'limit',
        "title": '9. Ierobežojošais reaģents',
        "eq": 'Salīdzina <i>n</i>₁ / <i>k</i>₁ ar <i>n</i>₂ / <i>k</i>₂',
        "lielumi": '<i>n</i>: daudzums molos; <i>k</i>: vienādojuma koeficients.',
        "pieņēmumi": 'Mazākā attiecība nosaka ierobežojošo reaģentu.',
        "piemērs": '2 Al + 3 Cl₂ → 2 AlCl₃ ar 0,50\u202fmol Al (attiecība 0,25) un 0,60\u202fmol Cl₂ (attiecība 0,20): Cl₂ ir ierobežojošais reaģents.',
        "simboli": ['n', 'k'],
        "saite": 'def-ierobezosais',
    },
]

# The six assumption rows shipped in #formulu-pienemumi. "of" names the registry
# formula each row belongs to, which is what keeps the two appendix tables from
# drifting: rename or drop a formula and the gate fails on the orphan reference.
ASSUMPTIONS = [
    {
        "of": "n",
        "formula": 'n = m / M',
        "pieņem": 'vielas masa ir tīra un molmasa ir zināma',
        "neizpildās": 'maisījumam vai nezināmam savienojumam vielas daudzums nav rēķināms',
    },
    {
        "id": 'c-nV',
        "of": 'c-nV',
        "formula": 'c = n / V',
        "pieņem": 'tilpums ir šķīduma tilpums un viela ir pilnīgi izšķīdusi',
        "neizpildās": 'nogulsnes vai neizšķīdusi daļa dod par lielu c',
    },
    {
        "of": "c-w",
        "formula": 'c = 10·w·ρ / M',
        "pieņem": 'w ir procentos, ρ ir g/mL un šķīdums ir viendabīgs',
        "neizpildās": 'citu mērvienību gadījumā koeficients 10 ir nepareizs',
    },
    {
        "of": "dilute",
        "formula": 'c₁V₁ = c₂V₂',
        "pieņem": 'vielas daudzums nemainās un tilpumi saskaitās',
        "neizpildās": 'reakcijā n mainās; dažu šķidrumu tilpumi nesaskaitās',
    },
    {
        "of": "n",
        "formula": 'V₀ = 22,414\u202fL/mol',
        "pieņem": 'gāze pie 0\u202f°C un 101,325\u202fkPa',
        "neizpildās": 'citos apstākļos tilpums ir cits',
    },
    {
        "of": "ph",
        "formula": 'pH = −lg a(H⁺)',
        "pieņem": 'atšķaidīts ūdens šķīdums pie 25\u202f°C, kur a ≈ c',
        "neizpildās": 'koncentrētā šķīdumā un citā T jārēķina ar aktivitātēm',
    },
]

# ------------------------------------------------------------------ notation
# The builder rewrites the registry's markup after it has been rendered: <i>
# becomes <var>, unicode sub/superscripts become real <sub>/<sup>, and N_A
# becomes N<sub>A</sub>. A parity check therefore cannot compare raw strings;
# plain() puts both the registry and the shipped master into one normal form.
# The two tables mirror build_master.py's _SUB/_SUP, including the Latin-1
# superscripts U+00B9/B2/B3, which have no U+207x partner for 1/2/3.
_SUB = {chr(0x2080 + i): str(i) for i in range(10)}
_SUP = {chr(0x2070 + i): str(i) for i in range(10)}
_SUP.update({"\u00b9": "1", "\u00b2": "2", "\u00b3": "3"})
_SUB.update({"\u208a": "+", "\u208b": "\u2212", "\u208c": "=",
             "\u208d": "(", "\u208e": ")"})
_SUB.update({"\u2090": "a", "\u2091": "e", "\u2092": "o", "\u2093": "x",
             "\u2094": "\u0259", "\u2095": "h", "\u2096": "k", "\u2097": "l",
             "\u2098": "m", "\u2099": "n", "\u209a": "p", "\u209b": "s",
             "\u209c": "t"})
_SUP.update({"\u207a": "+", "\u207b": "\u2212", "\u207c": "=",
             "\u207d": "(", "\u207e": ")", "\u207f": "n"})


def plain(markup):
    """Registry or shipped HTML -> the text a reader (or a screen reader) sees."""
    text = re.sub(r"<[^>]+>", "", markup)
    for table in (_SUB, _SUP):
        for char, repl in table.items():
            text = text.replace(char, repl)
    return re.sub(r"\s+", " ", text).strip()


# F09 interoperability: the sheet is exam reference, never clinical instruction.
DOSING = ("mg/kg", "deva", "doz\u0113", "pacientam")


def card_html():
    """The appendix summary sheet — byte-identical to what formula_card() used to inline."""
    rows = []
    for f in FORMULAS:
        rows.append(
            '<tr><th scope="row"><b>%s</b><br><span class="eq-highlight">%s</span></th>'
            '<td>%s</td><td>%s</td><td>%s</td></tr>'
            % (f["title"], f["eq"], f["lielumi"], f["pieņēmumi"], f["piemērs"]))
    caption = ('<caption>%d pamatformulas: sakarība, lielumi, pieņēmumi un aprēķina '
               'piemērs vienā pārskatā.</caption>' % len(FORMULAS))
    return (
        '<div class="mx-wrap"><table class="data" id="formulu-lapa-table">'
        + caption +
        '<thead><tr><th scope="col">Formula</th><th scope="col">Lielumi</th>'
        '<th scope="col">Pieņēmumi</th><th scope="col">Piemērs</th></tr></thead>'
        '<tbody>' + "".join(rows) + '</tbody></table></div>')


def assumptions_html():
    """The #formulu-pienemumi table.

    ch17.html still carries these six rows as hand-written HTML. This renderer is what
    a future {{FORMULA_ASSUMPTIONS}} token would emit; audit_formula_registry()
    compares it against the shipped rows, so the moment they agree exactly the swap is
    provably byte-identical and the last manual formula copy can be deleted.
    """
    rows = []
    for a in ASSUMPTIONS:
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
                     % (a["formula"], a["pieņem"], a["neizpildās"]))
    return ('<table class="data">\n'
            '<caption>Formulas, to pieņēmumi un kas notiek, ja pieņēmums neizpildās</caption>\n'
            '<tr><th scope="col">Formula</th><th scope="col">Ko tā pieņem</th>'
            '<th scope="col">Ja neizpildās</th></tr>\n'
            + "\n".join(rows) + "\n</table>")
