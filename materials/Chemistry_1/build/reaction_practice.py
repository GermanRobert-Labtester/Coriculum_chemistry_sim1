#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F03 — reaction-equation conservation practice set.

Eight vetted challenges for ch11 (reakcijas) and ch12 (redoks). The learner
balances an equation as a conservation problem — atom ledger plus net
charge — and then judges whether the balanced equation describes a reaction
that actually occurs. Balance is necessary but not sufficient: item 4 keeps
a paper-balanced equation whose reaction does not happen (M16), and two
distractors balance while answering a different question or direction.

Design contract (AGENTS.md §§4, 8, 12):
  * the set is fixed and Python-generated; there is no random runtime, no
    network and no third-party resource, and every answer is a native
    <details> disclosure that works with JavaScript off;
  * conservation is asserted by build/check_balance.py against this module
    during the build — a malformed equation blocks the build;
  * "balanced" is never labelled "reaction occurs": every record carries a
    feasibility verdict with its reason, and item 4 keeps a "does not
    occur" verdict although its equation balances;
  * distractors are machine-checked: a wrong-form distractor must fail
    conservation for the stated reason, and a balances-but-wrong distractor
    must pass conservation — that difference is the diagnostic.

Stdlib only. Imports check_balance (the independent T03 parser) and ledger
(M seeds named by the distractor feedback); check_balance imports this
module inside its main() so there is no import cycle.
"""
from __future__ import annotations

import html
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "build"))

import check_balance as cb  # noqa: E402  independent conservation parser
import ledger  # noqa: E402  M-seed registry referenced by the feedback

ARROW = " → "

# ---------------------------------------------------------------- records
# eq        balanced answer in course Unicode notation (the build turns
#           sub/superscripts into <sub>/<sup> markup)
# eq_ionic  optional net-ionic line shown under the molecular answer
# charge    optional note for the ionic line
# verdict   "Notiek." / "Nenotiek." — never derived from balance alone
# feas_tag  optional tag printed after the feasibility reason
# products  optional feasibility table (item 4)
# distractors: form = quoted wrong form or wrong claim; kind marks what the
#           checker must prove:
#             unbalanced      must fail atom/charge conservation
#             substance       balances, but a formula is not the substance
#             wrong-target    balances, but answers another question
#             wrong-direction balances, but the arrow runs the wrong way
#             claim           a verbal claim, no equation to parse
RECORDS = [
    dict(
        id="ep-01", chapter="ch11", kind="savienošanās", dkind="a", seed="M01",
        prompt="Sabalansējiet: Al + O₂ → Al₂O₃.",
        steps="Al: labajā pusē divas Al₂O₃ satur četrus Al, tāpēc pa kreisi "
              "4Al. O: trīs O₂ dod sešus skābekļa atomus, un 2 · 3 = 6 arī "
              "labajā pusē. Koeficienti ir 4, 3 un 2.",
        eq="4Al + 3O₂ → 2Al₂O₃",
        verdict="Notiek.",
        feas="Savienošanās: divas vielas dod vienu produktu, un sadegšana "
             "ir eksotermiska. Alumīnijs oksidējas no 0 līdz +3, skābeklis "
             "reducējas no 0 līdz −2.",
        src="[D p.19]",
        distractors=[
            dict(form="2Al + 3O → Al₂O₃", kind="substance",
                 why="Indeksa maiņa nav sabalansēšana: skābeklis kā viela ir "
                     "O₂, ne atsevišķi O atomi. Formula ar mainītu indeksu ir "
                     "cita viela, ne tā pati (M01)."),
            dict(form="2Al + 3O₂ → Al₂O₃", kind="unbalanced",
                 why="Al nav izlīdzināts: pa kreisi 2, pa labi 4. Skābeklis "
                     "jau sakrīt, tāpēc jāmaina tikai koeficients pie Al."),
        ],
    ),
    dict(
        id="ep-02", chapter="ch11", kind="neitralizācija", dkind="a", seed="M01",
        prompt="Sabalansējiet: NaOH + H₂SO₄ → Na₂SO₄ + H₂O.",
        steps="Na: Na₂SO₄ satur divus Na, tāpēc pa kreisi 2NaOH. H: tagad pa "
              "kreisi ir 2 + 2 = 4 H, bet viena H₂O satur tikai 2, tāpēc "
              "2H₂O. O pārbaudā: pa kreisi 2 + 4 = 6, pa labi 4 + 2 = 6.",
        eq="2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O",
        eq_ionic="H⁺ + OH⁻ → H₂O",
        charge="Saīsinātais jonu vienādojums: Na⁺ un SO₄²⁻ ir skatītājjoni; "
               "lādiņš +1 − 1 = 0 (M17).",
        verdict="Notiek.",
        feas="Neitralizācija: veidojas ūdens — vājš elektrolīts, tāpēc H⁺ un "
             "OH⁻ nepaliek brīvi joni (M16). Reakcija ir eksotermiska.",
        src="[D p.16–17]",
        distractors=[
            dict(form="2NaOH + H₂SO₄ → Na₂SO₄ + H₂O", kind="unbalanced",
                 why="Ūdens koeficients aizmirsts: pa kreisi H ir 4, pa labi "
                     "2. H₂O jāreizina ar 2 — tad sakrīt arī O (6 = 6)."),
            dict(form="NaOH + H₂SO₄ → NaHSO₄ + H₂O", kind="wrong-target",
                 why="Bilance sakrīt, bet tas ir atbilde citam jautājumam: "
                     "NaHSO₄ ir skābais sāls, ne pilna neitralizācija līdz "
                     "Na₂SO₄. Uzdevumā prasīti visi H⁺ no skābes."),
        ],
    ),
    dict(
        id="ep-03", chapter="ch11", kind="nogulsnēšanās", dkind="a", seed="M03",
        prompt="Sabalansējiet: BaCl₂ + Na₂SO₄ → BaSO₄ + NaCl.",
        steps="Ba un S jau ir viens pret vienu. Cl: BaCl₂ dod divus Cl⁻, "
              "tāpēc labajā pusē 2NaCl. Na: Na₂SO₄ dod divus Na⁺, kas "
              "apstiprina to pašu koeficientu 2 (M03).",
        eq="BaCl₂ + Na₂SO₄ → BaSO₄↓ + 2NaCl",
        eq_ionic="Ba²⁺ + SO₄²⁻ → BaSO₄↓",
        charge="Saīsinātais jonu vienādojums: Na⁺ un Cl⁻ ir skatītājjoni; "
               "lādiņš +2 − 2 = 0 (M17).",
        verdict="Notiek.",
        feas="BaSO₄ šķīdības tabulā apzīmēts ar N, tāpēc veidojas nogulsne — "
             "tieši tas ir apmaiņas reakcijas iemesls (M16).",
        src="[D p.6]",
        distractors=[
            dict(form="BaCl₂ + Na₂SO₄ → BaSO₄ + NaCl", kind="unbalanced",
                 why="NaCl koeficients aizmirsts: BaCl₂ dod divus Cl⁻ un "
                     "Na₂SO₄ divus Na⁺, tāpēc jābūt 2NaCl (M03)."),
            dict(form="Ba²⁺ + 2Cl⁻ + Na⁺ + SO₄²⁻ → BaSO₄↓ + 2Na⁺ + 2Cl⁻",
                 kind="unbalanced",
                 why="Na₂SO₄ dod divus Na⁺, ne vienu (M03); turklāt tas ir "
                     "pilnais jonu vienādojums — skatītājjoni jāizsvītro (M17)."),
        ],
    ),
    dict(
        id="ep-04", chapter="ch11", kind="apmaiņa, kas nenotiek", dkind="t",
        seed="M16",
        prompt="Vai šī reakcija notiek: NaCl + KNO₃ → NaNO₃ + KCl?",
        steps="Vienādojums uz papīra jau ir sabalansēts. Tomēr apmaiņas "
              "reakcija notiek tikai tad, ja veidojas nogulsne, gāze vai "
              "vājš elektrolīts. Pārbaudiet katru produktu šķīdības tabulā.",
        eq="NaCl + KNO₃ → NaNO₃ + KCl",
        verdict="Nenotiek.",
        feas="Abi produkti ir šķīstoši sāļi: nav ne nogulsnes, ne gāzes, ne "
             "vāja elektrolīta. Joni paliek šķīdumā blakus, un ķīmiskā "
             "pārvērtība nav notikusi (M16).",
        src="[D p.16–17]",
        products=dict(
            caption="Produktu pārbaude pirms koeficientiem (M16)",
            cols=("Produkts", "Šķīdības tabulā", "Novērojums"),
            rows=[("NaNO₃", "šķīsts", "nogulsnes nav"),
                  ("KCl", "šķīsts", "nogulsnes nav")]),
        distractors=[
            dict(form="Reakcija notiek, jo atomu skaits abās pusēs sakrīt.",
                 kind="claim",
                 why="Bilance ir nepieciešama, bet nav pietiekama. Tā "
                     "nepārbaudā, vai reakcija vispār notiek: šeit nekas "
                     "neizkrīt un neburbuļo (M16)."),
            dict(form="Reakcija notiek, jo joni apmainās.", kind="claim",
                 why="Apmaiņa nepieciešama, bet nepietiekama: ja neveidojas "
                     "nogulsne, gāze vai vājš elektrolīts, joni paliek "
                     "šķīdumā un nekāda pārvērtība nav notikusi (M16)."),
        ],
    ),
    dict(
        id="ep-05", chapter="ch11", kind="gāzes veidošanās", dkind="a",
        seed="M17",
        prompt="Sabalansējiet: HCl + K₂SO₃ → KCl + H₂O + SO₂.",
        steps="K: K₂SO₃ dod divus K⁺, tāpēc 2KCl un līdz ar to 2HCl. H un Cl "
              "tagad sakrīt pa divi. S paliek viens, un O: pa kreisi 3, pa "
              "labi 1 + 2 = 3.",
        eq="2HCl + K₂SO₃ → 2KCl + H₂O + SO₂↑",
        eq_ionic="2H⁺ + SO₃²⁻ → H₂O + SO₂↑",
        charge="Saīsinātais jonu vienādojums: K⁺ un Cl⁻ ir skatītājjoni; "
               "lādiņš +2 − 2 = 0 (M17).",
        verdict="Notiek.",
        feas="Veidojas SO₂ gāze, kas aiziet no šķīduma — tieši tas ir "
             "apmaiņas reakcijas iemesls (M16).",
        src="[D p.16–17]",
        distractors=[
            dict(form="HCl + K₂SO₃ → KCl + H₂O + SO₂↑", kind="unbalanced",
                 why="Koeficients pie HCl aizmirsts: K₂SO₃ dod divus K⁺, "
                     "tāpēc vajag 2HCl un 2KCl. Pa kreisi H būtu 1, pa labi 2."),
            dict(form="H⁺ + SO₃²⁻ → H₂O + SO₂↑", kind="unbalanced",
                 why="Jonu formā H nav izlīdzināts un lādiņš nesakrīt: "
                     "kreisajā pusē +1 − 2 = −1, labajā 0. Pareizi "
                     "2H⁺ + SO₃²⁻ → H₂O + SO₂↑."),
        ],
    ),
    dict(
        id="ep-06", chapter="ch11", kind="kompleksa veidošanās", dkind="a",
        seed="M01",
        prompt="Sabalansējiet: Zn(OH)₂ + NaOH → Na₂[Zn(OH)₄].",
        steps="Na: labajā pusē divi Na, tāpēc 2NaOH. Tad H: pa kreisi "
              "2 + 2 = 4, labajā 4. O: pa kreisi 2 + 2 = 4, labajā 4. Zn "
              "paliek viens.",
        eq="Zn(OH)₂ + 2NaOH → Na₂[Zn(OH)₄]",
        eq_ionic="Zn(OH)₂ + 2OH⁻ → [Zn(OH)₄]²⁻",
        charge="Jonu forma: cinks saista divas papildu OH⁻ grupas; lādiņš "
               "−2 = −2 (E40).",
        verdict="Notiek.",
        feas="Nešķīstošs amfotērais hidroksīds izšķīst sārma pārākumā un "
             "veido kompleksu — savienošanās ar kompleksa veidošanos (E40).",
        src="(E40)",
        distractors=[
            dict(form="Zn(OH)₂ + NaOH → Na₂[Zn(OH)₄]", kind="unbalanced",
                 why="Tā ir avota kļūda (E40): bez koeficienta 2 Na, H un O "
                     "nesakrīt. Jonu vienādojums zem tās ir pareizs, kļūda "
                     "ir tikai molekulārajā rindā."),
            dict(form="Zn(OH)₂ + OH⁻ → [Zn(OH)₄]²⁻", kind="unbalanced",
                 why="Jonu formā pietrūkst otra OH⁻: O būtu 3 pret 4, un "
                     "lādiņš −1 pret −2. Komplekss ir 2−, tāpēc kreisajā "
                     "pusē jābūt diviem OH⁻."),
        ],
    ),
    dict(
        id="ep-07", chapter="ch12", kind="aizvietošanās", dkind="a", seed="M14",
        prompt="Pārbaudiet atomu un lādiņu bilanci: Zn + Cu²⁺ → Zn²⁺ + Cu. "
               "Kurš ir oksidētājs?",
        steps="Atomi sakrīt viens pret vienu. Lādiņš: pa kreisi +2, pa labi "
              "+2 — arī sakrīt, tāpēc papildu koeficenti nav vajadzīgi. "
              "Cinks atdod divus elektronus, Cu²⁺ tos pievieno.",
        eq="Zn + Cu²⁺ → Zn²⁺ + Cu",
        verdict="Notiek.",
        feas="E°(Cu²⁺/Cu) = +0,337\u202fV > E°(Zn²⁺/Zn) = −0,763\u202fV, "
             "tāpēc EMS = 0,337 − (−0,763) = {n}\u202fV > 0 un reakcija "
             "notiek. Zn ir reducētājs (0 → +2), Cu²⁺ ir oksidētājs "
             "(+2 → 0) (M14). E° vērtības ņemtas no 12. nodaļas tabulas; "
             "tās nav nolasītas no primārās elektrodu tabulas.",
        feas_tag="[UNVERIFIED] C-11",
        # computed value: display rounds exact; expr recomputes exact —
        # verified by build/check_numbers.py like every other .num span
        feas_num=("1,1", "0.337-(-0.763)", "1,10"),
        src="[A p.14]",
        distractors=[
            dict(form="Zn + Cu²⁺ → Zn⁺ + Cu", kind="unbalanced",
                 why="Lādiņš nav saglabāts: cinks atdod divus elektronus, "
                     "tāpēc produkts ir Zn²⁺. Pa kreisi +2, pa labi +1 — "
                     "elektronu skaits nesakrīt."),
            dict(form="Cu + Zn²⁺ → Cu²⁺ + Zn", kind="wrong-direction",
                 why="Bilance sakrīt, bet virziens ir pretējs: metāls ar "
                     "negatīvāku potenciālu izspiež metālu ar pozitīvāku, "
                     "tāpēc Zn izspiež Cu, ne otrādi. Bilance nenozīmē, ka "
                     "reakcija notiek šajā virzienā."),
        ],
    ),
    dict(
        id="ep-08", chapter="ch12", kind="pusreakciju metode", dkind="a",
        seed="M13",
        prompt="Savienojiet pusreakcijas vienā jonu vienādojumā (skābā "
               "vide): MnO₄⁻ + H₂O₂ + H⁺ → Mn²⁺ + O₂ + H₂O.",
        steps="Reducēšanās: MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O (Mn no +7 līdz "
              "+2). Oksidēšanās: H₂O₂ − 2e⁻ → O₂ + 2H⁺ (O no −1 līdz 0; "
              "peroksīdā skābeklis ir −1, ne −2). Elektroni: 5 · 2 = 10, "
              "tāpēc pirmo pusreakciju reizina ar 2, otro ar 5. H⁺ un H₂O "
              "saīsinās.",
        eq="2MnO₄⁻ + 5H₂O₂ + 6H⁺ → 2Mn²⁺ + 8H₂O + 5O₂",
        verdict="Notiek.",
        feas="Skābā vidē permanganāts ir stiprs oksidētājs, un H₂O₂ šajā "
             "reakcijā ir reducētājs (M14). Lādiņa pārbaude: kreisajā pusē "
             "−2 + 6 = +4, labajā 2 · (+2) = +4.",
        src="[A p.14]",
        distractors=[
            dict(form="2MnO₄⁻ + 5H₂O₂ + 4H⁺ → 2Mn²⁺ + 8H₂O + 5O₂",
                 kind="unbalanced",
                 why="H⁺ skaits nolaists no lādiņa bilances, ne no "
                     "ūdeņraža: kreisajā pusē jābūt +4, tāpēc 6H⁺. Ar 4H⁺ "
                     "lādiņš būtu +2 un H nesakrītu (14 pret 16)."),
            dict(form="Neitrālā vidē produkts ir MnO₂.", kind="claim",
                 why="Uzdevums ir skābā vidē, kur produkts ir Mn²⁺. "
                     "Neitrālā vidē pusreakcija ir citādīga (MnO₂), un "
                     "H⁺ un OH⁻ loma mainās."),
        ],
    ),
]

KINDS_UNBALANCED = {"unbalanced"}
KINDS_BALANCED = {"substance", "wrong-target", "wrong-direction"}

SECTION = {
    "ch11": dict(
        sid="equation-practice",
        title="Uzdevumi: bilance, lādiņš un vai reakcija notiek",
        intro=[
            "Katrs uzdevums ir divi soļi. Pirmais: izlīdziniet atomus un "
            "lādiņu tikai ar koeficientiem — indeksa maiņa maina vielu, "
            "nevis sabalansē vienādojumu (M01). Otrais: pārbaudiet, vai "
            "reakcija vispār notiek, jo bilance ir nepieciešama, bet nav "
            "pietiekama. Atbilde ar bilances tabulu atveras pēc jūsu "
            "mēģinājuma.",
            "Šis ir treniņš, ne tests: punktu skaitītāja šeit nav, un viena "
            "kļūda nenozīmē „nepareizi visu”. Uzdevumi balstās kursa "
            "vielās un kritērijos; avots norādīts pie katra. Redoksa "
            "uzdevumi ar pusreakcijām un elektronu bilanci ir "
            "<a href=\"#equation-practice-redox\">12. nodaļā</a>; "
            "reakciju veidi paskaidroti <a href=\"#def-veidi\">iepriekš "
            "šajā nodaļā</a>.",
        ]),
    "ch12": dict(
        sid="equation-practice-redox",
        title="Uzdevumi: redoksa bilance",
        intro=[
            "Redoks vienādojumā jābilancē trīs lietas: atomi, lādiņš un "
            "elektroni. Ja lādiņš nesakrīt, elektronu skaits nav "
            "izlīdzināts — pat ja atomi izskatās kārtīgi. Šeit redzams arī "
            "otrs gadījums: sabalansēts vienādojums vēl nenozīmē, ka "
            "reakcija notiek šajā virzienā.",
            "Pamata uzdevumi par veidiem, nogulsnēm un jonu formu ir "
            "<a href=\"#equation-practice\">11. nodaļā</a>.",
        ]),
}

SEED_RE = re.compile(r"\((M\d{2})\)")


# ---------------------------------------------------------------- helpers
def _esc(s):
    return html.escape(s, quote=False)


def _seed_link(seed):
    """Distractor feedback links the placed mistake block (M01 → #m01)."""
    return "<a href=\"#m%s\">%s</a>" % (seed[1:], seed)


def _link_seeds(text):
    """(M01) in authored prose becomes a link to the placed M block."""
    return SEED_RE.sub(lambda m: "(" + _seed_link(m.group(1)) + ")"
                       if m.group(1) in ledger.M else m.group(0), text)


def _side(expr):
    return expr.split(ARROW) if ARROW in expr else expr.split("→")


def ledger_of(equation):
    """(rows, left_charge, right_charge) recomputed by the T03 parser.

    rows = [(element, left_count, right_count)] sorted by symbol. The
    displayed table can therefore never drift from the equation.
    """
    expr, _cond = cb.prepare(equation)
    left, right = _side(expr)
    lp, lc, ln, lnc = cb.side_totals(left)
    rp, rc, rn, rnc = cb.side_totals(right)
    left_el, right_el = Counter(lp), Counter(rp)
    left_el.update(rn)
    right_el.update(ln)
    left_ch, right_ch = lc + rnc, rc + lnc
    rows = [(el, left_el[el], right_el[el])
            for el in sorted(set(left_el) | set(right_el))]
    return rows, left_ch, right_ch


def _charge_text(ch):
    if ch == 0:
        return "0"
    return ("+%d" % ch) if ch > 0 else ("−%d" % (-ch))


def _analyze(equation):
    return cb.analyze(equation)


# ---------------------------------------------------------------- validate
def validate():
    """Every conservation claim this module makes, asserted. Returns faults."""
    faults = []
    here = "build/reaction_practice.py"

    if len(RECORDS) != 8:
        faults.append("%s:1 records: expected 8 challenges, found %d"
                      % (here, len(RECORDS)))
    seen = set()
    for rec in RECORDS:
        rid = rec["id"]
        sel = "[%s]" % rid
        if rid in seen:
            faults.append("%s:1 record-id: duplicate %s" % (here, rid))
        seen.add(rid)
        for field in ("chapter", "kind", "prompt", "steps", "eq", "verdict",
                      "feas", "src", "dkind", "seed"):
            if not str(rec.get(field, "")).strip():
                faults.append("%s:1 %s record-field: empty %s"
                              % (here, sel, field))
        if rec["chapter"] not in SECTION:
            faults.append("%s:1 %s record-chapter: no section for %s"
                          % (here, sel, rec["chapter"]))
        if rec["dkind"] not in ("r", "a", "t"):
            faults.append("%s:1 %s record-kind: %r not in r/a/t"
                          % (here, sel, rec["dkind"]))
        if rec["verdict"] not in ("Notiek.", "Nenotiek."):
            faults.append("%s:1 %s record-verdict: %r must be Notiek. or "
                          "Nenotiek." % (here, sel, rec["verdict"]))
        if rec["seed"] not in ledger.M:
            faults.append("%s:1 %s record-seed: %s not in ledger"
                          % (here, sel, rec["seed"]))
        if len(rec["distractors"]) < 2:
            faults.append("%s:1 %s record-distractors: fewer than two"
                          % (here, sel))

        # 1. the answer itself must conserve atoms and charge
        got = _analyze(rec["eq"])
        if got.parse_error:
            faults.append("%s:1 %s answer-parse: %s" % (here, sel, got.parse_error))
        elif not got.balanced:
            faults.append("%s:1 %s answer-balance: %s" % (here, sel, got.detail))
        rows, lch, rch = ledger_of(rec["eq"])
        if lch != rch:
            faults.append("%s:1 %s answer-charge: %s ≠ %s"
                          % (here, sel, _charge_text(lch), _charge_text(rch)))
        if any(l != r for _el, l, r in rows):
            bad = ", ".join("%s %d≠%d" % (el, l, r)
                            for el, l, r in rows if l != r)
            faults.append("%s:1 %s answer-ledger: %s" % (here, sel, bad))

        # 2. a computed value must be annotated like every other .num span
        if ("{n}" in rec["feas"]) != bool(rec.get("feas_num")):
            faults.append("%s:1 %s feas-num: placeholder and annotation "
                          "disagree" % (here, sel))
        if rec.get("feas_num"):
            exact, expr, disp = rec["feas_num"]
            if not re.fullmatch(r"[0-9+\-*/(). ]+", expr):
                faults.append("%s:1 %s feas-num: expr charset %r"
                              % (here, sel, expr))
            else:
                val = eval(expr, {"__builtins__": {}}, {})  # noqa: S307 — charset-whitelisted
                if abs(val - float(exact.replace(",", "."))) > 5e-6 * max(1.0, abs(val)):
                    faults.append("%s:1 %s feas-num: expr %s ≠ exact %s"
                                  % (here, sel, expr, exact))
                dec = len(disp.split(",")[1]) if "," in disp else 0
                if abs(float(disp.replace(",", ".")) - val) > 0.5 * 10 ** -dec + 1e-12:
                    faults.append("%s:1 %s feas-num: display %s does not "
                                  "round %s" % (here, sel, disp, exact))

        # 3. an ionic line must also conserve, and carry its charge note
        if rec.get("eq_ionic"):
            gi = _analyze(rec["eq_ionic"])
            if gi.parse_error:
                faults.append("%s:1 %s ionic-parse: %s" % (here, sel, gi.parse_error))
            elif not gi.balanced:
                faults.append("%s:1 %s ionic-balance: %s" % (here, sel, gi.detail))
            if not rec.get("charge"):
                faults.append("%s:1 %s ionic-charge: no charge note" % (here, sel))

        # 3. each distractor must fail — or balance — for the stated reason
        for d in rec["distractors"]:
            dsel = "%s/%s" % (sel, d["kind"])
            if d["kind"] not in (KINDS_UNBALANCED | KINDS_BALANCED | {"claim"}):
                faults.append("%s:1 %s distractor-kind: unknown %r"
                              % (here, dsel, d["kind"]))
            if not d.get("why", "").strip():
                faults.append("%s:1 %s distractor-why: empty reason"
                              % (here, dsel))
            if d["kind"] == "claim":
                continue
            gd = _analyze(d["form"])
            if gd.parse_error:
                faults.append("%s:1 %s distractor-parse: %s" % (here, dsel, gd.parse_error))
                continue
            if d["kind"] in KINDS_UNBALANCED and gd.balanced:
                faults.append("%s:1 %s distractor-unbalanced: %r balances — "
                              "it does not fail conservation" % (here, dsel, d["form"]))
            if d["kind"] in KINDS_BALANCED and not gd.balanced:
                faults.append("%s:1 %s distractor-balanced: %r fails (%s) — "
                              "the stated reason is not the real one"
                              % (here, dsel, d["form"], gd.detail))

        # 4. feasibility table rows carry three cells
        prod = rec.get("products")
        if prod:
            if len(prod["cols"]) != 3 or len(prod["rows"]) < 1:
                faults.append("%s:1 %s products-table: malformed" % (here, sel))
            for row in prod["rows"]:
                if len(row) != 3 or not all(str(c).strip() for c in row):
                    faults.append("%s:1 %s products-row: %r" % (here, sel, row))
    return faults


# ------------------------------------------------------------------ render
def _ledger_table(equation):
    rows, lch, rch = ledger_of(equation)
    out = ['<table class="data ep-ledger"><caption>Bilance: atomu skaits un '
           'lādiņa summa abās pusēs</caption><thead><tr><th scope="col">'
           'Elements</th><th scope="col">Kreisajā pusē</th><th scope="col">'
           'Labajā pusē</th></tr></thead><tbody>']
    for el, l, r in rows:
        out.append('<tr><th scope="row">%s</th><td>%d</td><td>%d</td></tr>'
                   % (_esc(el), l, r))
    out.append('<tr><th scope="row">lādiņa summa</th><td>%s</td><td>%s</td>'
               '</tr>' % (_charge_text(lch), _charge_text(rch)))
    out.append('</tbody></table>')
    return "".join(out)


def _products_table(prod):
    out = ['<table class="data ep-ledger"><caption>%s</caption><thead><tr>'
           % _esc(prod["caption"])]
    out += ['<th scope="col">%s</th>' % _esc(c) for c in prod["cols"]]
    out.append('</tr></thead><tbody>')
    for row in prod["rows"]:
        out.append('<tr><th scope="row">%s</th><td>%s</td><td>%s</td></tr>'
                   % tuple(_esc(c) for c in row))
    out.append('</tbody></table>')
    return "".join(out)


def _eq_box(rec, n):
    label = "Vienādojums, uzdevums %d" % n
    body = _esc(rec["eq"])
    if rec.get("eq_ionic"):
        body += "<br>" + _esc(rec["eq_ionic"])
        if rec.get("charge"):
            body += '<span class="why">%s</span>' % _link_seeds(_esc(rec["charge"]))
    return ('<div class="eq ep-eq" role="group" tabindex="0" aria-label="%s">'
            '%s</div>' % (html.escape(label), body))


def _distractors(rec):
    out = []
    for d in rec["distractors"]:
        out.append('<p class="ep-wrong"><b>„%s”</b> %s</p>'
                   % (_esc(d["form"]), _link_seeds(_esc(d["why"]))))
    return "".join(out)


def _item(rec, n):
    summary = "<b>%d · %s.</b> %s" % (n, _esc(rec["kind"]), _esc(rec["prompt"]))
    body = ['<div class="answer work">']
    lead = "Kā pārbaudīt." if rec["id"] == "ep-04" else "Kā sabalansēt."
    body.append("<p><b>%s</b> %s</p>" % (lead, _esc(rec["steps"])))
    body.append(_eq_box(rec, n))
    body.append(_ledger_table(rec["eq"]))
    if rec.get("products"):
        body.append(_products_table(rec["products"]))
    feas = "<b>%s</b> %s" % (_esc(rec["verdict"]), _esc(rec["feas"]))
    if rec.get("feas_num"):
        exact, expr, disp = rec["feas_num"]
        span = ('<span class="num" data-exact="%s" data-expr="%s">%s</span>'
                % (exact, html.escape(expr, quote=True), disp))
        feas = feas.replace("{n}", span)
    if rec.get("feas_tag"):
        feas += ' <span class="tag">%s</span>' % _esc(rec["feas_tag"])
    body.append('<p class="ep-feas">%s <span class="src">%s</span></p>'
                % (feas, _esc(rec["src"])))
    body.append(_distractors(rec))
    body.append("</div>")
    return ('<details class="q ep-item" data-kind="%s" data-seed="%s" id="%s">'
            "<summary>%s</summary>%s</details>"
            % (rec["dkind"], rec["seed"], rec["id"], summary, "".join(body)))


def render(chapter):
    sec = SECTION[chapter]
    out = ['<section class="eq-practice" id="%s">' % sec["sid"]]
    out.append("<h3>%s</h3>" % _esc(sec["title"]))
    for para in sec["intro"]:
        out.append('<p class="ep-intro">%s</p>' % para)
    for n, rec in enumerate(RECORDS, 1):
        if rec["chapter"] == chapter:
            out.append(_item(rec, n))
    out.append("</section>")
    return "".join(out)


def render_ch11():
    return render("ch11")


def render_ch12():
    return render("ch12")


# --------------------------------------------------------------- self-test
def _fixture_check():
    """Positive, negative and boundary fixtures (gate convention)."""
    faults = []

    # positive: every shipped record validates and renders
    if validate():
        faults.append("self-test: shipped records do not validate")
    if not render_ch11() or not render_ch12():
        faults.append("self-test: empty render")

    # negative: a wrong coefficient in an answer must be caught
    saved = RECORDS[0]
    RECORDS[0] = dict(saved, eq="2Al + 3O₂ → 2Al₂O₃")  # Al 2 ≠ 4
    try:
        if not any("answer-balance" in f for f in validate()):
            faults.append("self-test: unbalanced answer was accepted")
    finally:
        RECORDS[0] = saved

    # negative: a distractor marked unbalanced that balances must be caught
    saved = RECORDS[1]
    RECORDS[1] = dict(saved, distractors=[
        dict(form="NaOH + HCl → NaCl + H₂O", kind="unbalanced", why="x")])
    try:
        if not any("distractor-unbalanced" in f for f in validate()):
            faults.append("self-test: balanced distractor marked unbalanced")
    finally:
        RECORDS[1] = saved

    # boundary: a charge-only mismatch is not a balanced equation
    g = _analyze("Zn + Cu²⁺ → Zn⁺ + Cu")
    if g.parse_error or g.balanced:
        faults.append("self-test: charge-only mismatch read as balanced")
    # boundary: the item-4 paper equation balances although no reaction occurs
    g = _analyze("NaCl + KNO₃ → NaNO₃ + KCl")
    if g.parse_error or not g.balanced:
        faults.append("self-test: item-4 paper equation should balance")
    ep04 = [r for r in RECORDS if r["id"] == "ep-04"][0]
    if ep04["verdict"] != "Nenotiek.":
        faults.append("self-test: item-4 must keep the does-not-occur verdict")
    # boundary: the ledger is recomputed, never trusted from the record
    rows, lch, rch = ledger_of("2MnO₄⁻ + 5H₂O₂ + 6H⁺ → 2Mn²⁺ + 8H₂O + 5O₂")
    tally = dict((e, (l, r)) for e, l, r in rows)
    if lch != 4 or rch != 4 or tally.get("O") != (18, 18) or tally.get("Mn") != (2, 2):
        faults.append("self-test: ledger_of miscomputed the permanganate row")
    return faults


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        faults = _fixture_check()
        for f in faults:
            print("FAIL  " + f)
        print("reaction_practice self-test: %s"
              % ("PASS" if not faults else "FAIL"))
        return 1 if faults else 0
    faults = validate()
    if faults:
        print("\n".join("FAIL  " + f for f in faults))
        print("reaction_practice: %d faults" % len(faults))
        return 1
    n_bal = sum(1 for r in RECORDS if _analyze(r["eq"]).balanced)
    print("reaction_practice: %d challenges, %d answers conserve atoms and "
          "charge, %d does-not-occur verdicts not derived from balance"
          % (len(RECORDS), n_bal,
             sum(1 for r in RECORDS if r["verdict"] == "Nenotiek.")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
