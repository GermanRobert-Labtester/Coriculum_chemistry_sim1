# -*- coding: utf-8 -*-
"""Self-test items. kind: mcq | multi | numeric | cloze | order | classify.

T08 feedback contract:
  why   – why the keyed answer works (must name the seed ID)
  fail  – why the most likely wrong path fails (numeric/cloze/order/classify)
  alts  – per-distractor list of {opt, tag, text} for mcq/multi
  cue   – next reasoning step the student should try on retry
  tag   – misconception | boundary | unit | reasoning

Every distractor is a mistake seed or a real lecture error; wording traps are banned.
"""

import re

Q = []
ERR_TAGS = ("misconception", "boundary", "unit", "reasoning")

# Priority concept → seed map for T08 inventory (pH, α, solubility vs concentration, stoich).
PRIORITY = {
    "pH": ("M19", "M20", "E29"),
    "alpha": ("M22", "M09"),
    "solubility_vs_concentration": ("M21", "M18"),
    "stoich_ratios": ("M25", "M04", "M24"),
}


def seed_route(seed):
    """(anchor, label) for the first learner-mistake seed in a quiz/sim seed.

    F04: distractor feedback deep-links to the inline mistake card. Compound
    seeds ("M25/M04", "E60/M24") resolve to their first M-id; a seed that is
    only an errata id (E…) is a source correction, not a learner mistake
    route, so it returns (None, None) and the caller omits the link.
    """
    m = re.search(r"M(\d{2})", seed or "")
    if not m:
        return None, None
    return f"#m{m.group(1)}", f"M{m.group(1)}"


def q(kind, prompt, options, answer, why, *, fail=None, alts=None, cue=None):
    item = dict(kind=kind, prompt=prompt, options=options, answer=answer, why=why)
    if fail is not None:
        item["fail"] = fail
    if alts is not None:
        for a in alts:
            if a.get("tag") not in ERR_TAGS:
                raise SystemExit(f"quiz distractor tag {a.get('tag')!r} not in {ERR_TAGS}")
        item["alts"] = alts
    if cue is not None:
        item["cue"] = cue
    Q.append(item)


q("mcq", "Kura rinda satur <b>tikai jonus</b>?",
  ["CO₂, H₂O, CH₄", "CO₃²⁻, HPO₄²⁻, Fe³⁺", "O₂, N₂, F₂", "glikoze, etanols, saharoze"],
  "B: CO₃²⁻, HPO₄²⁻, Fe³⁺.",
  "Jons ir uzlādēta daļiņa; B satur tikai uzlādētas daļiņas. (M02)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "CO₂, H₂O, CH₄ ir neitrālas molekulas, nevis joni."},
    {"opt": "C", "tag": "misconception", "text": "O₂, N₂, F₂ ir vienkāršas vielas (molekulas), bez lādiņa."},
    {"opt": "D", "tag": "misconception", "text": "Glikoze, etanols un saharoze šķīst, bet paliek molekulāras."},
  ],
  cue="Meklējiet lādiņa zīmi pierakstā; šķīdība nav jona pazīme.")

q("numeric", "Cik jonu kopā dod viena Al₂(SO₄)₃ formulvienība, ja disociācija ir pilnīga?",
  [], "5 joni: 2 Al³⁺ + 3 SO₄²⁻.",
  "2 Al³⁺ + 3 SO₄²⁻ = 5 joni; indeksi ārpus iekavām un iekavās jāsaskaita atsevišķi. (M03)",
  fail="Atbilde 2 vai 3 skaita tikai vienu jonu veidu un aizmirst otru.",
  cue="Uzrakstiet disociācijas vienādojumu un saskaitiet katjonus + anjonus.")

q("numeric", "Šķīdumā ir 3 mol K₃PO₄. Cik mol K⁺ jonu tajā ir?",
  [], "9 mol K⁺ (un 3 mol PO₄³⁻).",
  "Viena formulvienība dod trīs K⁺; 3 × 3 = 9. B #9 prasa tieši šo. (M03)",
  fail="Atbilde 3 mol K⁺ aizmirst, ka koeficients 3 pie K attiecas uz katru formulvienību.",
  cue="Vispirms K₃PO₄ → 3K⁺ + PO₄³⁻, tad reiziniet ar doto n.")

q("mcq", "Kas ir NaCl ūdens šķīdumā?",
  ["NaCl molekulas", "Na⁺ un Cl⁻ joni", "Na un Cl atomi", "Na₂ un Cl₂ molekulas"],
  "B: Na⁺ un Cl⁻ joni.",
  "Jonu savienojums šķīdumā sadalās jonos; atsevišķu NaCl molekulu nav. (M02)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "„NaCl molekula” sajauc formulvienību ar molekulu."},
    {"opt": "C", "tag": "misconception", "text": "Šķīdumā nav neitrālu Na un Cl atomu; ir joni."},
    {"opt": "D", "tag": "reasoning", "text": "Na₂ un Cl₂ šeit nerodas; disociācija nedod gāzes molekulas."},
  ],
  cue="Ja režģis ir jonu, šķīdumā meklējiet jonus, ne molekulu.")

q("numeric", "Cik gramu NaOH satur 48 g šķīduma ar masas daļu 22 %?",
  [], "10,56 g NaOH.",
  "w = m(vielas) / m(šķīduma), tāpēc m = 0,22 · 48 g = 10,56 g. (M05)",
  fail="Dalīt ar šķīdinātāja masu vai jaukt 48 g ar 48 mL.",
  cue="Uzrakstiet, kas dots: šķīduma masa, tad m = w·m(šķīduma).")

q("numeric", "Tā paša šķīduma (48 g, w = 22 %, ρ = 1,25 g/mL, M = 40 g/mol) molārā koncentrācija?",
  [], "6,88 mol/L.",
  "V = 48 / 1,25 = 38,4 mL = 0,0384 L; n = 10,56 / 40 = 0,264 mol; c = 0,264 / 0,0384 = 6,88 mol/L. (M26)",
  fail="Lietot 48 mL bez blīvuma vai jaukt mL ar L vienā dalījumā.",
  cue="Vispirms V = m/ρ litros, tad c = n/V.")

q("numeric", "Cik mol Ca(OH)₂ nepieciešams, lai neitralizētu 5 mol HCl?",
  [], "2,5 mol Ca(OH)₂.",
  "Ca(OH)₂ + 2HCl → CaCl₂ + 2H₂O. Uz vienu Ca(OH)₂ vajag divus HCl, tāpēc 5 / 2 = 2,5. (M25)",
  fail="Atbilde 5 mol skaita vielu molus 1:1, nevis H⁺ un OH⁻ molus.",
  cue="Sabalansējiet vienādojumu un skaitiet H⁺ pret OH⁻, ne formulas.")

q("numeric", "Cik mol H₃PO₄ nepieciešams, lai neitralizētu 6 mol Mg(OH)₂?",
  [], "4 mol H₃PO₄.",
  "3Mg(OH)₂ + 2H₃PO₄ → Mg₃(PO₄)₂ + 6H₂O. Attiecība 3:2, tāpēc 6 · 2/3 = 4. (M25)",
  fail="Attiecība 1:1 vai 2:3 otrādi sajauc skābes un bāzes koeficientus.",
  cue="No sabalansētā vienādojuma ņemiet n(skābe) = n(bāze)·(2/3).")

q("mcq", "1 mol NaOH sajauc ar 2 mol HCl. Kurš reaģents ir ierobežojošais?",
  ["NaOH", "HCl", "abi vienādi", "nevar noteikt"],
  "A: NaOH.",
  "NaOH + HCl → NaCl + H₂O, attiecība 1:1. HCl ir divreiz vairāk, nekā vajag, tāpēc NaOH nosaka produkta daudzumu. (M04)",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "HCl ir pārākumā; ierobežojošais ir tas, kas beidzas pirmais."},
    {"opt": "C", "tag": "reasoning", "text": "Moli nav vienādi ar attiecību 1:1, tāpēc abi nav līdzvērtīgi."},
    {"opt": "D", "tag": "reasoning", "text": "Koeficienti un moli ir doti; ierobežojošo var noteikt."},
  ],
  cue="Daliet katru n ar koeficientu; mazākais n/k ir ierobežojošais.")

q("mcq", "9 g KOH izreaģē ar 9 g H₂SO₄. Kāda būs vide?",
  ["skāba", "bāziska", "neitrāla", "nevar noteikt bez indikatora"],
  "A: skāba.",
  "n(KOH) = 0,160 mol, n(H₂SO₄) = 0,092 mol. Vajag 0,184 mol KOH, bet ir 0,160, tāpēc KOH ir ierobežojošais un skābe paliek pāri. (M04)",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "Vienādi grami neliecina, ka bāze ir pārākumā; M(KOH) < M(H₂SO₄)."},
    {"opt": "C", "tag": "misconception", "text": "9 g = 9 g nav neitrāla punkts; vajag molu attiecību 2:1."},
    {"opt": "D", "tag": "reasoning", "text": "Moli un koeficienti pietiek, lai noteiktu atlikumu bez indikatora."},
  ],
  cue="Pārvērtiet gramus molos, tad salīdziniet ar 2KOH : 1H₂SO₄.")

q("numeric", "Kādu tilpumu (0 °C, 101,325 kPa) ieņem skābeklis, kas nepieciešams 100 g alumīnija oksidēšanai?",
  [], "62,3 L O₂.",
  "4Al + 3O₂ → 2Al₂O₃. n(Al) = 100 / 26,982 = 3,706 mol; n(O₂) = 3,706 · 3/4 = 2,780 mol; V = 2,780 · 22,414 = 62,3 L. (M24)",
  fail="Lietot 24,79 L/mol (SATP) vai nesabalansētu attiecību 1:1.",
  cue="Sabalansējiet, pārvērtiet Al molos, tad V = n·22,414 pie dotajiem apstākļiem.")

q("numeric", "Cik gramu Al₂O₃ rodas no 100 g Al?",
  [], "188,9 g Al₂O₃.",
  "n(Al₂O₃) = n(Al) / 2 = 1,853 mol; m = 1,853 · 101,961 = 188,9 g. Avotā iespiests 101,061 g/mol, bet pareizā M(Al₂O₃) ir 101,961 (E59).",
  fail="Lietot iespiesto 101,061 g/mol vai aizmirst koeficientu 2 Al → 1 Al₂O₃.",
  cue="Pārbaudiet M no atommasām un attiecību no sabalansētā vienādojuma.")

q("numeric", "10 g H₂SO₄ sajauc ar 9 g NaOH. Cik mol OH⁻ paliek pāri?",
  [], "0,021 mol OH⁻.",
  "n(H₂SO₄) = 0,102 mol, n(NaOH) = 0,225 mol. Pilnai neitralizācijai vajag 0,204 mol NaOH, tāpēc pāri paliek 0,021 mol. (M04)",
  fail="Salīdzināt gramus vai pieņemt 1:1 neitralizāciju ar H₂SO₄.",
  cue="Aprēķiniet molus, tad OH⁻ atlikums = n(NaOH) − 2·n(H₂SO₄).")

q("mcq", "Kāds ir 0,01 mol/L HCl šķīduma pH?",
  ["1", "2", "12", "13"],
  "B: pH = 2.",
  "HCl ir stipra skābe, tāpēc [H⁺] ≈ 0,01 = 10⁻² mol/L un pH = −lg(10⁻²) = 2. (M19)",
  alts=[
    {"opt": "A", "tag": "unit", "text": "pH = 1 būtu 0,1 mol/L HCl; te koncentrācija ir desmit reizes mazāka."},
    {"opt": "C", "tag": "misconception", "text": "12 ir pOH šim šķīdumam; pH un pOH nav viens un tas pats."},
    {"opt": "D", "tag": "misconception", "text": "13 būtu ļoti atšķaidīta sārma pH, ne skābes."},
  ],
  cue="Stiprai vienvērtīgai skābei [H⁺] ≈ c; pH = −lg[H⁺].")

q("numeric", "Šķīduma pH ir 3. Kāda ir [H⁺] mol/L?",
  [], "10⁻³ = 0,001 mol/L.",
  "[H⁺] = 10⁻ᵖᴴ. Ja pH = 3, tad [H⁺] = 0,001 mol/L. (E29)",
  fail="Atbilde „3 mol/L” sajauc pH skaitli ar koncentrāciju.",
  cue="Apgrieziet definīciju: [H⁺] = 10⁻ᵖᴴ, nevis pH = [H⁺].")

q("mcq", "Kāds ir neitrāls pH pie 37 °C?",
  ["7,00", "≈ 6,8", "≈ 7,4", "0"],
  "B: ≈ 6,8.",
  "K<sub>w</sub> pie 37 °C ir ≈ 2,4·10⁻¹⁴, tāpēc neitrāls pH = ½pK<sub>w</sub> ≈ 6,81. (M20) Šo 37 °C vērtību neviens kursa avots neraksta; tā nav nolasīta no primārās līdzsvara tabulas. <span class=\"tag\">[UNVERIFIED]</span> C-07.",
  alts=[
    {"opt": "A", "tag": "boundary", "text": "7,00 ir neitrāls tikai pie 25 °C, ne ķermeņa temperatūrā."},
    {"opt": "C", "tag": "misconception", "text": "7,4 ir asins pH – vāji sārmains, ne neitrāls."},
    {"opt": "D", "tag": "reasoning", "text": "pH 0 ir ļoti skābs šķīdums, ne neitrāls ūdens."},
  ],
  cue="Neitrāls = ½pK<sub>w</sub> pie dotās temperatūras.")

q("mcq", "Kurš no šiem sāļiem dod bāzisku šķīdumu?",
  ["NaCl", "Na₂CO₃", "NH₄Cl", "KNO₃"],
  "B: Na₂CO₃.",
  "Na₂CO₃ ir stipras bāzes un vājas skābes sāls: hidrolizējas CO₃²⁻, šķīdumā paliek OH⁻. (M23)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "NaCl nehidrolizējas; vide paliek neitrāla."},
    {"opt": "C", "tag": "misconception", "text": "NH₄Cl dod skābu vidi (NH₄⁺ hidrolīze)."},
    {"opt": "D", "tag": "misconception", "text": "KNO₃ ir stipras skābes un stipras bāzes sāls bez hidrolīzes."},
  ],
  cue="Nosakiet, no kādas skābes un bāzes sāls ir veidots.")

q("mcq", "Kas notiek, ja Al₂S₃ nonāk ūdenī?",
  ["nešķīst un paliek nogulsnēs", "hidrolizējas pilnīgi", "dod neitrālu šķīdumu", "izdala tikai sērūdeņradi"],
  "B: hidrolizējas pilnīgi.",
  "Al₂S₃ ir vājas bāzes un vājas skābes sāls; abi joni hidrolizējas un sāls sadalās. (E32)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Problēma nav tikai nešķīdība; notiek pilnīga hidrolīze."},
    {"opt": "C", "tag": "boundary", "text": "„Vāja + vāja ⇒ pH 7” šeit neder; sāls sadalās."},
    {"opt": "D", "tag": "reasoning", "text": "H₂S ir viens produkts, bet hidrolīze ietver arī Al hidroksīdu."},
  ],
  cue="Vāja skābe + vāja bāze: pārbaudiet, vai sāls vispār pastāv ūdenī.")

q("mcq", "Kuram skābajam sālim šķīdums ir bāzisks?",
  ["NaHCO₃", "NaHSO₄", "NaH₂PO₄", "visiem skābajiem sāļiem"],
  "A: NaHCO₃.",
  "HCO₃⁻ ūdenī vairāk pieņem protonu, nekā atdod, tāpēc pH ≈ 8,3. „Skābais sāls” apraksta sastāvu, nevis pH (M06).",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "NaHSO₄ ir skābs šķīdumā (HSO₄⁻ atdod H⁺)."},
    {"opt": "C", "tag": "boundary", "text": "NaH₂PO₄ šķīdums ir skābs; bāzisks ir Na₂HPO₄ / Na₃PO₄."},
    {"opt": "D", "tag": "misconception", "text": "Nosaukums „skābais sāls” neparedz pH visiem sāļiem."},
  ],
  cue="Par vidi lemj hidrolīze, ne formulas nosaukums.")

q("mcq", "Kāda ir mangāna oksidēšanas pakāpe KMnO₄?",
  ["+2", "+4", "+6", "+7"],
  "D: +7.",
  "K⁺ ir +1, katrs O ir −2 (četri dod −8). Lai summa būtu 0, Mn ir +7. (M13)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "+2 ir tipisks Mn²⁺ sāļos, ne KMnO₄."},
    {"opt": "B", "tag": "misconception", "text": "+4 ir MnO₂; šeit skābekļa bilance prasa +7."},
    {"opt": "C", "tag": "reasoning", "text": "+6 būtu, ja skaitītu trīs O vai aizmirstu K⁺."},
  ],
  cue="Summa = 0 neitrālā formulā: +1 + x + 4·(−2) = 0.")

q("mcq", "Kurš ir oksidētājs reakcijā 2Fe³⁺ + 2I⁻ → 2Fe²⁺ + I₂?",
  ["Fe³⁺", "I⁻", "Fe²⁺", "I₂"],
  "A: Fe³⁺.",
  "Fe³⁺ pievieno elektronu un pārvēršas Fe²⁺, tāpēc tas reducējas un ir oksidētājs. (M14)",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "I⁻ atdod elektronus: tas ir reducētājs, ne oksidētājs."},
    {"opt": "C", "tag": "reasoning", "text": "Fe²⁺ ir produkts pēc reducēšanās, ne oksidētājs."},
    {"opt": "D", "tag": "reasoning", "text": "I₂ ir oksidēšanās produkts."},
  ],
  cue="Oksidētājs pievieno e⁻ un pats reducējas.")

q("numeric", "Kāda ir sēra oksidēšanas pakāpe H₂SO₄?",
  [], "+6.",
  "2·(+1) + x + 4·(−2) = 0, tāpēc x = +6. (M13)",
  fail="Sajaukt oksidēšanas pakāpi ar sulfāta lādiņu (−2).",
  cue="H un O parastajās pakāpēs; atrisiniet x no summas 0.")

q("mcq", "Kura ir aizvietošanas reakcija?",
  ["CaCO₃ → CaO + CO₂", "Fe + CuSO₄ → FeSO₄ + Cu", "NaOH + HCl → NaCl + H₂O", "CO₂ + CaO → CaCO₃"],
  "B: Fe + CuSO₄.",
  "Aizvietošanā vienkārša viela aizstāj elementu saliktā vielā. Šeit Fe aizstāj Cu. (M15)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "A ir sadalīšanās."},
    {"opt": "C", "tag": "misconception", "text": "C ir apmaiņa (neitralizācija)."},
    {"opt": "D", "tag": "misconception", "text": "D ir savienošanās."},
  ],
  cue="Meklējiet shēmu A + BC → AC + B.")

q("multi", "Kuras no šīm reakcijām ir redoksreakcijas? (Trīs atbildes pareizas.)",
  ["Zn + Cl₂ → ZnCl₂", "2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O", "Mg + 2HCl → MgCl₂ + H₂", "CaCO₃ → CO₂ + CaO", "Fe + CuCl₂ → Cu + FeCl₂"],
  "A, C un E.",
  "Redoks ir tur, kur mainās oksidēšanas pakāpes: Zn 0→+2, Mg 0→+2, Fe 0→+2, Cu +2→0. (M15)",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "Neitralizācijā pakāpes nemainās."},
    {"opt": "D", "tag": "misconception", "text": "CaCO₃ sadalīšanā pakāpes nemainās."},
  ],
  cue="Pārbaudiet oksidēšanas pakāpju izmaiņas; redoks nav piektais veids.")

q("mcq", "Kāds ir saīsinātais jonu vienādojums reakcijai HCl + NaOH?",
  ["H⁺ + Cl⁻ + Na⁺ + OH⁻ → NaCl + H₂O", "H⁺ + OH⁻ → H₂O", "Na⁺ + Cl⁻ → NaCl", "HCl + OH⁻ → Cl⁻ + H₂O"],
  "B: H⁺ + OH⁻ → H₂O.",
  "Na⁺ un Cl⁻ ir skatītājjoni, tie nemainās. Tāpēc tos izsvītro. (M17)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Pilnais jonu vienādojums vēl satur skatītājjomus."},
    {"opt": "C", "tag": "misconception", "text": "NaCl šķīdumā paliek kā joni; netiek veidota cieta sāls."},
    {"opt": "D", "tag": "reasoning", "text": "HCl ūdenī ir disociējis; HCl molekulāri neraksta."},
  ],
  cue="Izsvītrojiet jonus, kas abās pusēs ir vienādi.")

q("multi", "Kuras apmaiņas reakcijas tiešām norit? (Divas atbildes pareizas.)",
  ["NaCl + KNO₃ → NaNO₃ + KCl", "Ba(NO₃)₂ + Na₂SO₄ → BaSO₄↓ + 2NaNO₃", "HCl + K₂SO₃ → 2KCl + H₂O + SO₂↑", "NaNO₃ + KCl → NaCl + KNO₃"],
  "B un C.",
  "Apmaiņa notiek, ja rodas nogulsnes, gāze vai vājš elektrolīts. (M16)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Visi joni paliek šķīdumā; ķīmiski nekas nav mainījies."},
    {"opt": "D", "tag": "misconception", "text": "Tāpat tikai jonu saraksts bez dzinējspēka."},
  ],
  cue="Meklējiet ↓, ↑ vai vāju elektrolītu (H₂O).")

q("order", "Sakārtojiet stehiometriskā aprēķina soļus pareizā secībā.",
  ["pārvērst doto lielumu molos", "sabalansēt reakcijas vienādojumu", "pēc koeficientiem atrast meklējamās vielas molus", "pārvērst molus masā, tilpumā vai citā lielumā"],
  "1) sabalansēt vienādojumu → 2) pārvērst doto lielumu molos → 3) pēc koeficientiem atrast n(B) → 4) pārvērst atbildē.",
  "Vienādojums vispirms, jo koeficienti ir attiecības avots. (M24)",
  fail="Sākt ar masas attiecību bez sabalansēta vienādojuma.",
  cue="Vispirms vienādojums, tad moli, tad masa/tilpums.")

q("order", "Sakārtojiet orbitāles to aizpildīšanās secībā.",
  ["3s", "1s", "3d", "2p", "4s", "2s", "3p"],
  "1s → 2s → 2p → 3s → 3p → 4s → 3d.",
  "4s ir zemākas enerģijas nekā 3d, tāpēc tas nāk pirmais. (M30)",
  fail="Likt 3d pirms 4s pēc galvenā kvantu skaitļa.",
  cue="Atcerieties 4s pirms 3d aizpildīšanās secībā.")

q("cloze", "Oksidētājs ______ elektronus un pats ______.",
  [], "pievieno; reducējas.",
  "Oksidētājs ņem elektronus sev, tāpēc tā oksidēšanas pakāpe samazinās un tas reducējas. (M14)",
  fail="Teikt, ka oksidētājs oksidējas – vārda līdzība maldina.",
  cue="Pusreakcijā elektroni kreisajā pusē = reducēšanās.")

q("cloze", "1 mol = ______ mmol = ______ µmol.",
  [], "1000 mmol; 1 000 000 µmol.",
  "Mikro- ir miljonā daļa, tāpēc vienā molā ir miljons mikromolu. (E03)",
  fail="Rakstīt 1·10⁻⁶ µmol – sajaukta mikro- nozīme.",
  cue="milli- = 10⁻³, mikro- = 10⁻⁶ no mola.")

q("cloze", "Gāzes molārais tilpums V₀ = 22,414 L/mol pie ______ °C un ______ kPa.",
  [], "0 °C un 101,325 kPa.",
  "Tie ir normālie apstākļi. SATP (25 °C, 100 kPa) dod 24,79 L/mol. (E60)",
  fail="Lietot 25 °C / 100 kPa kopā ar 22,414 L/mol.",
  cue="Pierakstiet apstākļus blakus katram V₀.")

q("classify", "Sadaliet vielas: Cu, NaCl, glikoze, HCl. Kuras ir elektrolīti?",
  [], "Elektrolīti: NaCl un HCl. Neelektrolīti: Cu un glikoze.",
  "Cu vada ar elektroniem, ne joniem; glikoze šķīst bez joniem. (M08)",
  fail="Saukt Cu par elektrolītu, jo tas vada strāvu.",
  cue="Jautājiet: vai šķīdumā ir brīvi joni?")

q("numeric", "0,9 % NaCl šķīdums. Cik mmol/L NaCl tas satur? (M = 58,44 g/mol)",
  [], "≈ 154 mmol/L.",
  "0,9 % nozīmē 9 g uz litru. n = 9 / 58,44 = 0,154 mol = 154 mmol. (M26)",
  fail="Aizmirst pārvērst molus mmol vai jaukt % ar mol/L tieši.",
  cue="9 g/L ÷ M, tad ·1000 → mmol/L.")

q("numeric", "5 % glikozes šķīdums. Cik mmol/L glikozes tas satur? (M = 180,16 g/mol)",
  [], "≈ 278 mmol/L.",
  "50 g/L ÷ 180,16 g/mol = 0,278 mol/L = 278 mmol/L. (M31)",
  fail="Reizināt ar 2 kā NaCl osmolaritātē – glikoze nedisociē.",
  cue="Glikoze: c mmol/L ≈ osmolaritāte; NaCl dod ~2 daļiņas.")

q("mcq", "Kurš apgalvojums par ¹²C ir pareizs?",
  ["A = 12, A_r = 12, M = 12 g/mol", "A = 12 g/mol, A_r = 12", "A_r = 12 g/mol, M = 12", "visi trīs ir viens un tas pats lielums"],
  "A: masas skaitlis 12, relatīvā atommasa 12, molmasa 12 g/mol.",
  "Trīs dažādi lielumi ar līdzīgu skaitli. (E05, M29)",
  alts=[
    {"opt": "B", "tag": "unit", "text": "Masas skaitlim nav g/mol."},
    {"opt": "C", "tag": "unit", "text": "A_r ir bez mērvienības; M ir g/mol."},
    {"opt": "D", "tag": "misconception", "text": "Vienāds skaitlis nenozīmē vienu lielumu."},
  ],
  cue="A = nukloni; A_r = attiecība; M = masa/mol.")

q("mcq", "Kura no šīm vielām ir tīra viela, nevis maisījums?",
  ["minerālūdens", "piens", "gaiss", "CO₂"],
  "D: CO₂.",
  "CO₂ ir savienojums ar noteiktu sastāvu. (E19)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Minerālūdens satur izšķīdušus sāļus – maisījums."},
    {"opt": "B", "tag": "misconception", "text": "Piens ir emulsija/koloīds – maisījums."},
    {"opt": "C", "tag": "misconception", "text": "Gaiss ir gāzu maisījums."},
  ],
  cue="Tīrai vielai ir fiksēts sastāvs; maisījumam – mainīgs.")

q("mcq", "Kurš ir heterogēns maisījums?",
  ["sāls šķīdums", "eļļa un ūdens", "gaiss", "cukura šķīdums"],
  "B: eļļa un ūdens.",
  "Eļļa un ūdens veido divas saskatāmas fāzes. (E19)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Sāls šķīdums ir homogēns."},
    {"opt": "C", "tag": "misconception", "text": "Gaiss ir homogēns gāzu maisījums."},
    {"opt": "D", "tag": "misconception", "text": "Cukura šķīdums ir homogēns."},
  ],
  cue="Heterogēns = vairākas saskatāmas fāzes.")

q("mcq", "Kāds ir koloīdu daļiņu izmērs?",
  ["mazāk par 1 nm", "1–100 nm", "100–1000 nm", "vairāk par 1 µm"],
  "B: 1–100 nm.",
  "Zem 1 nm ir īstie šķīdumi; virs 100 nm – rupjdispersās sistēmas. (E17)",
  alts=[
    {"opt": "A", "tag": "boundary", "text": "< 1 nm ir īsts šķīdums."},
    {"opt": "C", "tag": "boundary", "text": "100–1000 nm kursā nepaliek koloīda zonā."},
    {"opt": "D", "tag": "boundary", "text": "> 1 µm ir rupja suspensija."},
  ],
  cue="Atcerieties robežas 1 nm un 100 nm.")

q("mcq", "Kā parasti mainās gāzes šķīdība ūdenī, paaugstinot temperatūru?",
  ["pieaug", "samazinās", "nemainās", "vispirms samazinās, tad pieaug visām gāzēm"],
  "B: samazinās.",
  "Siltākā ūdenī gāze parasti mazāk šķīst. Izņēmumi H₂, He, Ne ar minimumu. (E22)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "Cietām vielām bieži pieaug; gāzēm ūdenī parasti otrādi."},
    {"opt": "C", "tag": "reasoning", "text": "Temperatūra ietekmē līdzsvaru; šķīdība mainās."},
    {"opt": "D", "tag": "boundary", "text": "Minimums nav „visām” gāzēm – tikai dažām."},
  ],
  cue="Atcerieties „parasti” un izņēmumus H₂/He/Ne.")

q("mcq", "Ko nozīmē „piesātināts šķīdums”?",
  ["daudz izšķīdušas vielas", "līdzsvaru ar neizšķīdušo vielu", "šķīdumu ar augstu blīvumu", "šķīdumu bez nogulsnēm ar maksimālo iespējamo koncentrāciju"],
  "B: līdzsvaru ar neizšķīdušo vielu.",
  "Piesātināts nozīmē, ka šķīšanas un kristalizācijas ātrumi ir vienādi. Tas nav tas pats, kas koncentrēts. (M21)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "„Daudz vielas” = koncentrēts; mazšķīstošas vielas piesātināts šķīdums ir atšķaidīts."},
    {"opt": "C", "tag": "unit", "text": "Blīvums nav piesātinājuma definīcija."},
    {"opt": "D", "tag": "boundary", "text": "Bez nogulsnēm tas var būt nepiesātināts vai nestabils pārsātināts; piesātinājums prasa līdzsvaru ar cieto fāzi."},
  ],
  cue="Jautājiet: vai ir līdzsvars ar neizšķīdušo vielu?")

q("multi", "Kuras no šīm vielām ir stipri elektrolīti? (Trīs atbildes pareizas.)",
  ["HCl", "CH₃COOH", "NaOH", "NaCl", "glikoze"],
  "A, C un D.",
  "HCl, NaOH un NaCl disociē praktiski pilnīgi. Stiprs ≠ koncentrēts. (M09)",
  alts=[
    {"opt": "B", "tag": "misconception", "text": "CH₃COOH ir vāja skābe (daļēja disociācija)."},
    {"opt": "E", "tag": "misconception", "text": "Glikoze ir neelektrolīts."},
  ],
  cue="Stiprums = disociācijas pilnība, ne koncentrācija.")

q("mcq", "Kura formula apzīmē formulvienību, nevis molekulu?",
  ["H₂O", "CO₂", "NaCl", "CH₄"],
  "C: NaCl.",
  "NaCl ir jonu režģis; atsevišķas molekulas nav. (M02)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "H₂O ir molekula."},
    {"opt": "B", "tag": "misconception", "text": "CO₂ ir molekula."},
    {"opt": "D", "tag": "misconception", "text": "CH₄ ir molekula."},
  ],
  cue="Metāls + nemetāls jonu režģī → formulvienība.")

q("mcq", "Kura skābe ir divvērtīga?",
  ["HCl", "HNO₃", "CH₃COOH", "H₂SO₄"],
  "D: H₂SO₄.",
  "Divvērtīga skābe var atdot divus protonus. CH₃COOH satur četrus H, bet tikai viens ir skābs. (E31)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "HCl ir vienvērtīga."},
    {"opt": "B", "tag": "misconception", "text": "HNO₃ ir vienvērtīga."},
    {"opt": "C", "tag": "misconception", "text": "H atomu skaits formulā ≠ vērtība; etiķskābei skābs ir viens H."},
  ],
  cue="Skaitiet aizvietojamos H, ne visus H formulā.")

q("mcq", "Atšķaidot etiķskābes šķīdumu, α pieaug. Vai skābe kļūst stiprāka?",
  ["jā, jo α pieaug", "nē, K<sub>a</sub> nemainās; mainās tikai disociējusī daļa", "jā, jo [H⁺] pieaug", "nē, jo α vienmēr samazinās atšķaidot"],
  "B: nē, K<sub>a</sub> nemainās; mainās tikai disociējusī daļa.",
  "Atšķaidot α pieaug, bet jonu koncentrācija krīt; stiprumu nosaka K<sub>a</sub>, ne α. (M22)",
  alts=[
    {"opt": "A", "tag": "misconception", "text": "α↑ nav tas pats, kas stiprāks elektrolīts."},
    {"opt": "C", "tag": "unit", "text": "Atšķaidot [H⁺] parasti krīt, lai gan α pieaug."},
    {"opt": "D", "tag": "reasoning", "text": "Vājām skābēm α atšķaidot pieaug, nevis samazinās."},
  ],
  cue="Salīdziniet K<sub>a</sub> (vielas īpašība) ar α (stāvokļa lielums).")


# T13.2: retrieval kind (r=recall, a=apply, t=transfer) + mistake seed per item.
QRK = {
    1: ("t", "M02"),
    2: ("a", "M03"),
    3: ("a", "M03"),
    4: ("t", "M02"),
    5: ("a", "M05"),
    6: ("a", "M26"),
    7: ("a", "M25"),
    8: ("a", "M25"),
    9: ("a", "M04"),
    10: ("a", "M04"),
    11: ("a", "M24"),
    12: ("a", "E59"),
    13: ("a", "M04"),
    14: ("a", "M19"),
    15: ("a", "E29"),
    16: ("t", "M20"),
    17: ("t", "M23"),
    18: ("t", "E32"),
    19: ("t", "M06"),
    20: ("a", "M13"),
    21: ("a", "M14"),
    22: ("a", "M13"),
    23: ("t", "M15"),
    24: ("t", "M15"),
    25: ("a", "M17"),
    26: ("t", "M16"),
    27: ("a", "M24"),
    28: ("r", "M30"),
    29: ("r", "M14"),
    30: ("r", "E03"),
    31: ("r", "E60"),
    32: ("t", "M08"),
    33: ("a", "M26"),
    34: ("a", "M31"),
    35: ("t", "E05"),
    36: ("r", "E19"),
    37: ("r", "E19"),
    38: ("r", "E17"),
    39: ("t", "E22"),
    40: ("t", "M21"),
    41: ("t", "M09"),
    42: ("r", "M02"),
    43: ("r", "E31"),
    44: ("t", "M22"),
}


# ---------------------------------------------------------------------------
# T10 – practice bank (Python-owned; build_master.py renders the untimed
# static bank). T16.2 retired the timed form: it was unreachable, so the
# timer, its milestones and the state machine are gone with it.
# scope: course | course-clinical | clinical-unverified
# Official exam blueprint unavailable → no "matches course tests" claim (OI-02).
# ---------------------------------------------------------------------------

SIM_PASS_PCT = 55  # course Ievadtests/Nobeiguma cut-off (MASTER_PROMPT); practice only
SIM_SCOPE = ("course", "course-clinical", "clinical-unverified")
ERR_TAGS_SIM = ERR_TAGS

SIM = []


def sim(qid, prompt, options, correct, ok, *, alts, cue, chapter, seed, scope, warrant, clinical=False):
    """Register one simulator item. correct is 0-based option index."""
    if scope not in SIM_SCOPE:
        raise SystemExit(f"sim {qid}: bad scope {scope!r}")
    if not isinstance(correct, int) or not (0 <= correct < len(options)):
        raise SystemExit(f"sim {qid}: malformed answer key correct={correct!r} n_opts={len(options)}")
    if len(options) < 2:
        raise SystemExit(f"sim {qid}: need ≥2 options")
    for a in alts:
        if a.get("tag") not in ERR_TAGS_SIM:
            raise SystemExit(f"sim {qid}: bad alt tag {a.get('tag')!r}")
        if "idx" not in a or not (0 <= a["idx"] < len(options)):
            raise SystemExit(f"sim {qid}: alt idx out of range")
        if a["idx"] == correct:
            raise SystemExit(f"sim {qid}: alt idx collides with correct")
    item = {
        "id": qid,
        "prompt": prompt,
        "options": list(options),
        "correct": correct,
        "ok": ok,
        "alts": list(alts),
        "cue": cue,
        "chapter": chapter,
        "seed": seed,
        "scope": scope,
        "warrant": warrant,
        "clinical": bool(clinical),
    }
    SIM.append(item)


sim(
    "S01",
    "Kāds ir protonu un elektronu skaits nātrija jonā ²³₁₁Na⁺?",
    ["11 protoni, 11 elektroni", "11 protoni, 10 elektroni", "10 protoni, 11 elektroni", "12 protoni, 11 elektroni"],
    1,
    "Z = 11 protoni; Na⁺ zaudē 1 e⁻ → 10 elektroni.",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Aizmirst, ka katjons zaudē elektronu."},
        {"idx": 2, "tag": "misconception", "text": "Sajauc protonu un elektronu skaitu."},
        {"idx": 3, "tag": "reasoning", "text": "Masas skaitlis 23 nav protonu skaits."},
    ],
    cue="Protonus dod Z; elektronus = Z − lādiņš.",
    chapter="atomi", seed="E05", scope="course",
    warrant="MASTER_PROMPT ch2 / A atomu uzbūve",
)

sim(
    "S02",
    "Kura saite veidojas starp elementiem ar ΔREN = 2,4?",
    ["Nepolāra kovalentā saite", "Polāra kovalentā saite", "Jonu saite", "Metāliskā saite"],
    2,
    "Pēc kursa konvencijas ΔREN ≥ 2,0 → jonu saite. (E10: continuum; atbilde nosauc kursa robežu.)",
    alts=[
        {"idx": 0, "tag": "boundary", "text": "Nepolāra: ΔREN ≈ 0."},
        {"idx": 1, "tag": "boundary", "text": "Polāra kovalentā: ΔREN < 2 kursā."},
        {"idx": 3, "tag": "misconception", "text": "Metāliskā saite ir starp metāliem, ne pēc ΔREN."},
    ],
    cue="Salīdziniet ΔREN ar kursa robežu 2.",
    chapter="saites", seed="E10", scope="course",
    warrant="E10 / A p.3, E s.22",
)

sim(
    "S03",
    "Kāpēc CO₂ molekula ir nepolāra, lai gan C=O saites ir polāras?",
    ["Oglekļa REN ir vienāda ar skābekļa REN", "Lineārā ģeometrija atceļ dipolu momentus", "Tā ir jonu viela", "Skābekļa atomi atgrūž elektronus"],
    1,
    "CO₂ ir lineāra (O=C=O); pretēji dipoli summā dod 0 (M10).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "C un O REN atšķiras; saites ir polāras."},
        {"idx": 2, "tag": "misconception", "text": "CO₂ ir molekulāra viela, ne jonu."},
        {"idx": 3, "tag": "reasoning", "text": "Atgrūšanās nepaskaidro molekulas polaritāti."},
    ],
    cue="Saites polaritāte ≠ molekulas polaritāte – pārbaudiet ģeometriju.",
    chapter="saites", seed="M10", scope="course",
    warrant="M10 / saites polaritāte",
)

sim(
    "S04",
    "Kāda veida dispersā sistēma ir asinis?",
    ["Molekulārs (īsts) šķīdums", "Koloīdā suspensija un emulsija", "Vienkārša gāze", "Aerosols"],
    1,
    "Asinis satur šūnas un olbaltumvielu koloīdus (kursa disperso sistēmu piemērs).",
    alts=[
        {"idx": 0, "tag": "boundary", "text": "Īsts šķīdums: daļiņas < 1 nm; asinis ir sarežģītākas."},
        {"idx": 2, "tag": "misconception", "text": "Asinis ir šķidrums, ne gāze."},
        {"idx": 3, "tag": "misconception", "text": "Aerosols ir cietas/šķidras daļiņas gāzē."},
    ],
    cue="Koloīds: 1–100 nm + šūnu fāzes.",
    chapter="maisijumi", seed="E19", scope="course-clinical", clinical=True,
    warrant="MASTER_PROMPT ch4 / D p.3–7 (asinis kā dispersā sistēma)",
)

sim(
    "S05",
    "Cik jonu rodas, pilnīgi disociējot vienai Al₂(SO₄)₃ formulvienībai?",
    ["2 joni", "3 joni", "5 joni", "6 joni"],
    2,
    "2 Al³⁺ + 3 SO₄²⁻ = 5 joni (M03).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Skaita tikai Al³⁺."},
        {"idx": 1, "tag": "misconception", "text": "Skaita tikai SO₄²⁻."},
        {"idx": 3, "tag": "reasoning", "text": "6 rastos, ja skaitītu atomus, ne jonus."},
    ],
    cue="Saskaitiet katjonus + anjonus no disociācijas.",
    chapter="elektroliti", seed="M03", scope="course",
    warrant="M03",
)

sim(
    "S06",
    "Aprēķiniet c, ja 0,5 mol glikozes izšķīdināti līdz 250 mL šķīduma!",
    ["0,5 mol/L", "1,0 mol/L", "2,0 mol/L", "4,0 mol/L"],
    2,
    "c = n/V = 0,5 / 0,250 = 2,0 mol/L (M26).",
    alts=[
        {"idx": 0, "tag": "unit", "text": "Aizmirst dalīt ar tilpumu litros."},
        {"idx": 1, "tag": "unit", "text": "Lieto 0,5 L vietā 0,250 L."},
        {"idx": 3, "tag": "unit", "text": "Dalījums ar 0,125 L vai dubults pārveidojums."},
    ],
    cue="250 mL = 0,250 L pirms dalīšanas.",
    chapter="koncentracija", seed="M26", scope="course",
    warrant="M26",
)

sim(
    "S07",
    "Kāda ir vides reakcija un pH vērtība 0,01 M HCl šķīdumam?",
    ["pH = 1 (skāba)", "pH = 2 (skāba)", "pH = 7 (neitrāla)", "pH = 12 (bāziska)"],
    1,
    "[H⁺] ≈ 0,01 = 10⁻² → pH = 2 (M19).",
    alts=[
        {"idx": 0, "tag": "unit", "text": "pH 1 būtu 0,1 M HCl."},
        {"idx": 2, "tag": "misconception", "text": "Stipra skābe nav neitrāla."},
        {"idx": 3, "tag": "misconception", "text": "12 ir pOH; sajauc pH ar pOH."},
    ],
    cue="Stiprai vienvērtīgai skābei pH = −lg c.",
    chapter="ph", seed="M19", scope="course",
    warrant="M19",
)

sim(
    "S08",
    "Kāda ir pH vērtība un lakmusa krāsa Na₂CO₃ ūdens šķīdumā?",
    ["pH < 7, sarkana", "pH = 7, violeta", "pH > 7, zila", "pH = 1, sarkana"],
    2,
    "CO₃²⁻ hidrolīze dod OH⁻ → pH > 7, lakmuss zils (M23).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Sāls no vājas skābes nav skābs."},
        {"idx": 1, "tag": "misconception", "text": "Na₂CO₃ nav neitrāls kā NaCl."},
        {"idx": 3, "tag": "reasoning", "text": "pH 1 ir stipras skābes zona."},
    ],
    cue="Nosakiet skābi/bāzi, no kuras sāls veidots.",
    chapter="hidrolize", seed="M23", scope="course",
    warrant="M23",
)

sim(
    "S09",
    "Kurš no šiem sāļiem ir praktiski nešķīstošs ūdenī (nogulsnes)?",
    ["NaNO₃", "BaSO₄", "CaCl₂", "K₂CO₃"],
    1,
    "BaSO₄ tabulā N – nogulsnes (M18).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "NaNO₃ ir Š."},
        {"idx": 2, "tag": "misconception", "text": "CaCl₂ ir Š."},
        {"idx": 3, "tag": "misconception", "text": "K₂CO₃ ir Š."},
    ],
    cue="Pārbaudiet pāri tabulā: Ba²⁺ + SO₄²⁻ = N.",
    chapter="skidiba", seed="M18", scope="course",
    warrant="M18",
)

sim(
    "S10",
    "Kāda ir mangāna oksidēšanas pakāpe savienojumā KMnO₄?",
    ["+2", "+4", "+6", "+7"],
    3,
    "+1 + x − 8 = 0 ⇒ x = +7 (M13).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "+2 ir Mn²⁺ sāļos."},
        {"idx": 1, "tag": "misconception", "text": "+4 ir MnO₂."},
        {"idx": 2, "tag": "reasoning", "text": "+6 – kļūdaina O vai K bilance."},
    ],
    cue="Summa 0: K(+1) + Mn(x) + 4O(−2).",
    chapter="redoks", seed="M13", scope="course",
    warrant="M13",
)

sim(
    "S11",
    "Kurš apgalvojums ir pareizs par reducētāju reakcijā?",
    ["Piesaista elektronus un samazina pakāpi", "Atdod elektronus un palielina pakāpi", "Vienmēr ir skābeklis", "Nemaina elektronu skaitu"],
    1,
    "Reducētājs atdod e⁻ un oksidējas; pakāpe pieaug (M14).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Tas ir oksidētāja apraksts."},
        {"idx": 2, "tag": "misconception", "text": "Reducētājs nav obligāti skābeklis."},
        {"idx": 3, "tag": "reasoning", "text": "Redoks maina elektronu skaitu."},
    ],
    cue="Reducētājs reducē otru un pats oksidējas.",
    chapter="redoks", seed="M14", scope="course",
    warrant="M14",
)

sim(
    "S12",
    "Cik molu H₂ radīsies, reaģējot 2 mol Al ar sērskābes pārākumu?",
    ["1 mol", "2 mol", "3 mol", "6 mol"],
    2,
    "2 Al + 3 H₂SO₄ → … + 3 H₂: 2 mol Al → 3 mol H₂ (M24).",
    alts=[
        {"idx": 0, "tag": "reasoning", "text": "Attiecība nav 2:1."},
        {"idx": 1, "tag": "misconception", "text": "1:1 pēc Al moliem bez koeficientiem."},
        {"idx": 3, "tag": "unit", "text": "6 – reizina ar 3 bez attiecības 2:3."},
    ],
    cue="No sabalansētā vienādojuma 2 Al : 3 H₂.",
    chapter="stehiometrija", seed="M24", scope="course",
    warrant="M24",
)

sim(
    "S13",
    "Ja sajauc 1 mol NaOH ar 1 mol H₂SO₄, kura viela ir pārākumā?",
    ["NaOH", "H₂SO₄", "Neviena, izreaģē pilnīgi", "Ūdens"],
    1,
    "Vajag 2 mol NaOH uz 1 mol H₂SO₄; NaOH beidzas, H₂SO₄ paliek (M25/M04).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "NaOH ir ierobežojošais, ne pārākumā."},
        {"idx": 2, "tag": "misconception", "text": "1:1 moli ≠ 2:1 H⁺/OH⁻."},
        {"idx": 3, "tag": "reasoning", "text": "Ūdens ir produkts, ne reaģents pārākumā."},
    ],
    cue="Skaitiet H⁺ pret OH⁻, ne formulas 1:1.",
    chapter="stehiometrija", seed="M25", scope="course",
    warrant="M25 / M04",
)

sim(
    "S14",
    "Kāds šķīdums ir 0,9 % NaCl salīdzinājumā ar asins plazmu?",
    ["Hipotonisks", "Izotonisks", "Hipertonisks", "Koloidāls"],
    1,
    "Kursa piemērs: 0,9 % NaCl ≈ plazmas osmolaritāte (izotonisks). Klīniskais diapazons ārpus kursa – *[jāpārbauda]* (OI-02).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Hipotonisks būtu zemāka osmolaritāte."},
        {"idx": 2, "tag": "misconception", "text": "Hipertonisks – augstāka osmolaritāte."},
        {"idx": 3, "tag": "misconception", "text": "NaCl šķīdums ir īsts šķīdums, ne koloīds."},
    ],
    cue="Salīdziniet osmolaritāti, ne tikai %.",
    chapter="organisms", seed="E22", scope="clinical-unverified", clinical=True,
    warrant="SOURCE_LEDGER 0,9 % NaCl row; plasma range [UNVERIFIED] OI-02",
)

sim(
    "S15",
    "Kā mainās elementu elektronegativitāte periodā no kreisās uz labo pusi?",
    ["Samazinās", "Palielinās", "Nemainās", "Vispirms samazinās"],
    1,
    "Periodā pa labi pieaug kodola lādiņš un REN.",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Samazinās grupā uz leju, ne periodā pa labi."},
        {"idx": 2, "tag": "reasoning", "text": "REN periodā sistemātiski mainās."},
        {"idx": 3, "tag": "boundary", "text": "Nav vispārīga „vispirms samazinās” periodā."},
    ],
    cue="Periodā pa labi REN ↑; grupā uz leju REN ↓.",
    chapter="saites", seed="E10", scope="course",
    warrant="MASTER_PROMPT / REN periods",
)

sim(
    "S16",
    "Kurš savienojums satur jonu saiti?",
    ["H₂O", "CH₄", "NaCl", "CO₂"],
    2,
    "NaCl – tipisks jonu savienojums (M02/M11).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "H₂O – polāra kovalentā."},
        {"idx": 1, "tag": "misconception", "text": "CH₄ – nepolāra kovalentā."},
        {"idx": 3, "tag": "misconception", "text": "CO₂ – kovalentās saites."},
    ],
    cue="Sārmu metāls + halogēns → jonu.",
    chapter="saites", seed="M02", scope="course",
    warrant="M02 / M11",
)

sim(
    "S17",
    "Kāds ir ūdens jonu reizinājums Kw pie 25 °C?",
    ["1,0 · 10⁻⁷", "1,0 · 10⁻¹⁴", "14", "1,0 · 10⁷"],
    1,
    "K_w = [H⁺][OH⁻] = 1,0·10⁻¹⁴ pie 25 °C (E29). Sākuma tabula nav nolasīta. <span class=\"tag\">[UNVERIFIED]</span> C-07.",
    alts=[
        {"idx": 0, "tag": "unit", "text": "10⁻⁷ ir [H⁺] neitrālā ūdenī, ne K_w."},
        {"idx": 2, "tag": "unit", "text": "14 ir pK_w, ne K_w."},
        {"idx": 3, "tag": "reasoning", "text": "Pakāpe ar plusu nav K_w."},
    ],
    cue="K_w = 10⁻¹⁴; pK_w = 14 pie 25 °C.",
    chapter="ph", seed="E29", scope="course",
    warrant="E29",
)

sim(
    "S18",
    "Kura viela reakcijā Zn + CuSO₄ → ZnSO₄ + Cu ir oksidētājs?",
    ["Zn", "Cu²⁺ (CuSO₄)", "SO₄²⁻", "Cu"],
    1,
    "Cu²⁺ pieņem e⁻ un reducējas → oksidētājs (M14).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Zn ir reducētājs (oksidējas)."},
        {"idx": 2, "tag": "reasoning", "text": "SO₄²⁻ ir skatītājjons."},
        {"idx": 3, "tag": "reasoning", "text": "Cu⁰ ir produkts."},
    ],
    cue="Oksidētājs pievieno e⁻.",
    chapter="redoks", seed="M14", scope="course",
    warrant="M14",
)

sim(
    "S19",
    "Cik litru aizņem 1 mol ideālas gāzes normālos apstākļos?",
    ["11,2 L", "22,4 L", "24,4 L", "100 L"],
    1,
    "0 °C, 101,325 kPa: V₀ ≈ 22,4 L/mol (E60/M24).",
    alts=[
        {"idx": 0, "tag": "unit", "text": "11,2 L – puse mola."},
        {"idx": 2, "tag": "boundary", "text": "≈24,8 L ir SATP, ne NTP."},
        {"idx": 3, "tag": "reasoning", "text": "100 L nav molārais tilpums."},
    ],
    cue="Pierakstiet apstākļus blakus 22,4 L/mol.",
    chapter="stehiometrija", seed="E60", scope="course",
    warrant="E60 / M24",
)

sim(
    "S20",
    "Kā sauc procesu, kurā attīra asinis caur puscaurlaidīgu membrānu?",
    ["Koagulācija", "Dialīze (hemodialīze)", "Sedimentācija", "Emulģēšana"],
    1,
    "Dialīzē mazās molekulas difundē caur membrānu (E21: hemodialīze, ne elektrodialīze).",
    alts=[
        {"idx": 0, "tag": "misconception", "text": "Koagulācija – koloīdu sarecēšana."},
        {"idx": 2, "tag": "misconception", "text": "Sedimentācija – nogulsnēšanās gravitācijā."},
        {"idx": 3, "tag": "misconception", "text": "Emulģēšana – divu šķidrumu izkliede."},
    ],
    cue="Membrāna + koncentrācijas gradients = dialīze.",
    chapter="maisijumi", seed="E21", scope="course-clinical", clinical=True,
    warrant="E21 / D p.5 (hemodialīze ≠ elektrodialīze)",
)


def sim_validate_bank():
    """Build-time / check-time integrity. Raises SystemExit on malformed keys."""
    if len(SIM) != 20:
        raise SystemExit(f"SIM bank must have 20 items, got {len(SIM)}")
    ids = [s["id"] for s in SIM]
    if len(set(ids)) != len(ids):
        raise SystemExit(f"duplicate SIM ids: {ids}")
    for s in SIM:
        if not (0 <= s["correct"] < len(s["options"])):
            raise SystemExit(f"malformed answer key for {s['id']}")
        if s["clinical"] and s["scope"] == "course":
            raise SystemExit(f"{s['id']}: clinical=True requires non-course scope")
        if s["scope"] == "clinical-unverified" and not s["clinical"]:
            raise SystemExit(f"{s['id']}: clinical-unverified needs clinical=True")


sim_validate_bank()
