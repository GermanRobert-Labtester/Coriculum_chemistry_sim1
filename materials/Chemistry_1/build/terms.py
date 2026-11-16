# -*- coding: utf-8 -*-
"""T01: single source of truth for contested Latvian terms.

Ledger rule (SOURCE_LEDGER.md §2): where the PDFs use two spellings, the
master picks one, uses it everywhere, and records the choice. Rows marked
[apstiprināt] are unverifiable from the PDFs and are listed for the user.

When this map and the ledger disagree, the ledger wins and this file is
rewritten. Decisions the ledger does not cover go to the open-questions
list in the appendix, never silently into code.

Objects:
  CANON             stable id -> canonical record (transcribed from ledger §2)
  BANNED            (regex, reason, replacement) enforced by check()
  CONFUSABLE        the nine T04 pairs (data only; T04 places the tables)
  APPROVED_PENDING  the six open decisions with the default used
"""

import pathlib
import re

# ---------------------------------------------------------------- CANON
# Transcribed from SOURCE_LEDGER.md §2; "avoid" column feeds BANNED.
CANON = {
    "amount": {"lv": "vielas daudzums *n* (mol)", "avoid": ["molu skaits", "mols as quantity"],
               "note": "Quantity n, unit mol.", "confirm": False},
    "masses": {"lv": "relatīvā atommasa *A*r · molmasa *M* (g/mol) · masas skaitlis *A*",
               "avoid": ["one letter for all three", "atommasas mērvienība g/mol"],
               "note": "Three quantities, three names (E05, A p.2). Molmasa is M in g/mol; it is not relatīvā molekulmasa.",
               "confirm": False},
    "formula_unit": {"lv": "formulvienība (jonu savienojumiem)",
                     "avoid": ["NaCl molekula"],
                     "note": "Ionic crystals have no molecules; B #1, M02. The wrong name survives only inside a quoted correction.",
                     "confirm": False},
    "ammonia": {"lv": "NH₃·H₂O, NH₃(aq)", "avoid": ["NH₄OH", "amonija hidroksīds"],
                "note": "E27. No discrete NH₄OH is known.", "confirm": False},
    "ox_state": {"lv": "oksidēšanas pakāpe", "avoid": ["oksidēšanās pakāpe"],
                 "note": "Working spelling only. Oxidation state ≠ ion charge ≠ valence (E43, A p.14). Still [apstiprināt]; IUPAC Gold Book O04365 unread.",
                 "confirm": True},
    "agents": {"lv": "oksidētājs (reducējas) · reducētājs (oksidējas)",
               "avoid": ["oksidētājs oksidējas"],
               "note": "The agent is reduced, not oxidised.", "confirm": False},
    "stp": {"lv": "normālie apstākļi, with the numbers",
            "avoid": ["n.a. with bare 22,4"], "note": "E60.", "confirm": False},
    "rxn_kind": {"lv": "reakcijas veids / klasifikācija",
                 "avoid": ["reakcijas mehānisms for types"],
                 "note": "A mechanism is the stepwise path; savienošanās and the other four are types (E41, D p.15–16).",
                 "confirm": False},
    "saturation": {"lv": "piesātināts · nepiesātināts · pārsātināts",
                   "avoid": ["= koncentrēts / atšķaidīts"],
                   "note": "How close to solubility vs how much solute.", "confirm": False},
    "concentration": {"lv": "masas daļa *w*, molārā koncentrācija *c*(X) in mol/L, blīvums ρ",
                      "avoid": ["CM", "procentuālā koncentrācija", "normalitāte"],
                      "note": "Normality is not used in these sources.", "confirm": False},
    "hydrates": {"lv": "hidratācija / solvatācija · kristālhidrāts · hidrolīze",
                 "avoid": ["hidrāts for all"], "note": "Shell, lattice water, reaction (E24).",
                 "confirm": False},
    "dissociation": {"lv": "elektrolītiskā disociācija", "avoid": [],
                     "note": "Course term for NaCl dissociation and HCl ionisation; difference in a depth block.",
                     "confirm": False},
    "bases": {"lv": "bāze · sārms (ūdenī šķīstoša bāze) · hidroksīds (klase)",
              "avoid": ["using the three as synonyms"],
              "note": "NH₃ is a base with no OH group (A p.11). Course word for pH > 7 is sārmains (D p.20).",
              "confirm": False},
    "basic_triple": {"lv": "bāziskais oksīds / bāziskā vide / bāziskais sāls",
                     "avoid": ["assuming they share a meaning"],
                     "note": "Three uses of one adjective; course says sārmains for pH > 7 (D p.20).",
                     "confirm": False},
    "acid_salt": {"lv": "skābais sāls (contains replaceable H)",
                  "avoid": ["skābs šķīdums"], "note": "NaHCO₃(aq) is alkaline (E28).",
                  "confirm": False},
    "acid_residue": {"lv": "skābes atlikums", "avoid": [],
                     "note": "Keep (A, E). It means the anion.", "confirm": False},
    "ampho": {"lv": "amfotērs (oxide, hydroxide) · amfiprotisks jons",
              "avoid": ["one word for both", "amfolīts as a settled synonym"],
              "note": "Al₂O₃ and Zn(OH)₂ versus HCO₃⁻, H₂PO₄⁻, HPO₄²⁻. amfolīts is an unconfirmed alias, not a second species and not amfotērs. Still [apstiprināt].",
              "confirm": True},
    "hbond": {"lv": "ūdeņraža saite, described as starpmolekulāra mijiedarbība",
              "avoid": ["starpmolekulārā saite"], "note": "E13.", "confirm": False},
    "lattice": {"lv": "atomu (kovalentais) kristālrežģis", "avoid": ["atomārs for diamond"],
                "note": "Working name for diamond/Si (E15, A p.9, E s.36). atomārs stays for monoatomic species. Still [apstiprināt].",
                "confirm": True},
    "hcl": {"lv": "hlorūdeņradis (gāze) · sālsskābe (HCl šķīdums)", "avoid": [],
            "note": "D p.10 uses both correctly.", "confirm": False},
    "charges": {"lv": "jonu lādiņš Fe³⁺ (skaitlis, tad zīme) vs oksidēšanas pakāpe +3 / (III)",
                "avoid": ["Fe⁺³ for an ion"], "note": "E43.", "confirm": False},
    "typo_numbers": {"lv": "decimal comma; thin no-break space before units; L not l; − (U+2212); pH upright",
                     "avoid": [], "note": "Enforced by T03 typography.py.", "confirm": False},
    "typo_symbols": {"lv": "quantities *n*, *m*, *M*, *V*, *c*, ρ, α, *K* italic; units/symbols upright",
                     "avoid": [], "note": "Enforced by T03 typography.py.", "confirm": False},
    "gloss_en": {"lv": "English equivalents in the glossary", "avoid": ["unverified etymology"],
                 "note": "For reading international literature.", "confirm": False},
}

# ---------------------------------------------------------------- BANNED
# (regex, reason, replacement, optional window phrases). Diacritic-exact.
# A (?i) flag is used only for reakcijas mehānisms, whose source heading
# is capitalised. NH₄OH stays unbanned: E27 has to name it.
BANNED = [
    (r"oksidēšanās pakāpe",
     "state value must be 'oksidēšanas pakāpe' (E43); bare 'oksidēšanās' stays the process noun",
     "oksidēšanas pakāpe"),
    (r"molu skaits",
     "quantity is 'vielas daudzums n', unit mol (ledger §2)",
     "vielas daudzums"),
    (r"procentuālā koncentrācija",
     "use 'masas daļa w' or 'molārā koncentrācija c' (ledger §2)",
     "masas daļa w / molārā koncentrācija c"),
    (r"\bCM\b",
     "use 'c' for molārā koncentrācija (ledger §2)",
     "c"),
    (r"normalitāt\w*",
     "normality is not used in these sources; do not introduce it",
     "— (delete; use w or c)"),
    (r"starpmolekulār\w+ saite",
     "it is a 'starpmolekulāra mijiedarbība', not a bond (E13)",
     "starpmolekulāra mijiedarbība"),
    (r"<sup>\+\d",
     "ion charge is number-then-sign: Fe³⁺, not Fe⁺³ (E43)",
     "number-then-sign, e.g. Fe<sup>3+</sup>",
     # didactic refutations name the wrong form to reject it (ch12, ch15)
     ["nepareizs", "(E43)"]),
    (r"amfolīt\w*",
     "primary term is 'amfiprotisks jons'; 'amfolīts' lives only in the glossary (AGENTS §8)",
     "amfiprotisks jons",
     # the two appendix decision records name the alias to record the choice
     ["(vārdnīcā)", "vai <em>amfolītu</em>"]),
    (r"Bieži kļūdas",
     "calque of 'common mistakes'; the block name is 'Biežākās kļūdas' (plan T01, F04)",
     "Biežākās kļūdas"),
    (r"Kur kļūdīties",
     "needs the modal verb: 'Kur var kļūdīties' (plan T01, F05)",
     "Kur var kļūdīties"),
    (r"Molu karte",
     "'mols' is a unit, not a countable thing; use 'Vielas daudzuma karte' (ledger §2, F06)",
     "Vielas daudzuma karte"),
    (r"\bmolaritāt\w*",
     "canonical term is 'molārā koncentrācija c' (ledger §2); do not use the alias in prose (F07)",
     "molārā koncentrācija"),
    (r"atommasas mērvienība",
     "g/mol is the unit of molmasa M, not of relatīvā atommasa (E05, A p.2)",
     "molmasa M (g/mol), relatīvā atommasa A_r, or masas skaitlis A"),
    (r"NaCl molekul\w*",
     "an ionic solid has a formulvienība, not a NaCl molecule (B #1, M02)",
     "formulvienība",
     ["ir kļūda", "nav nevienas", "nav atsevišķu", "molekulu nav", "M02", "q-options"]),
    (r"(?i)reakcijas mehānisms",
     "savienošanās and the other course classes are reakcijas veids, not a mechanism (E41, D p.15–16)",
     "reakcijas veids",
     ["nav mehānisms", "E41", "„Reakcijas mehānisms"]),
]

# Greek letters and formula markup are notation, not Latvian vocabulary.
# check() does not skip a banned word because one of these is nearby.
# Do not copy these rows into ALLOW.
NOTATION_EXCEPTIONS = [
    {"id": "greek_quantity",
     "glyphs": "Δ δ ρ σ α β π μ",
     "ledger": "SOURCE_LEDGER.md §2 symbols row",
     "rule": "Quantity and bond symbols stay as symbols. They are not words to be respelt."},
    {"id": "formula_markup",
     "glyphs": "sub/sup formulas and number-then-sign charges",
     "ledger": "SOURCE_LEDGER.md §2 charge row; E43",
     "rule": "Formula markup is not prose. The Fe⁺³ ban stays in force; this row does not widen ALLOW."},
]

# ---------------------------------------------------------------- CONFUSABLE
# The nine T04 pairs. rows: one per term (term, is, is_not, example) plus
# `difference` — every cell <= 18 words (enforced by check_confusable).
# `check` + `answer` render as the hidden self-test beneath the table.
# `seed` names the mistake seed the check guards; None = pure meaning
# confusion with no M seed (rendered as such, never hidden). `where`
# is the human-readable placement. Non-breaking spaces (U+202f) are
# written as escapes wherever a digit meets a unit (T03 rule).
CONFUSABLE = [
 {"id": "skidiba_skidums", "a": "šķīdība", "b": "šķīdums",
  "difference": "Cik daudz izšķīst, pret maisījumu, kas rodas.",
  "chapter": "skidiba", "where": "5. nodaļa", "seed": "M18",
  "check": "Vai 30 g NaCl 100 g ūdenī ir šķīdība vai šķīdums?",
  "answer": "Abi: 30 g/100 g ir šķīdība (mērs), bet sāls ar ūdeni kopā ir šķīdums.",
  "rows": [
   {"term": "šķīdība",
    "is": "Cik daudz vielas izšķīst 100 g ūdens dotajā temperatūrā.",
    "is_not": "Nav maisījums un nav recepte.",
    "example": "NaCl: ap 36 g/100 g pie 20 °C."},
   {"term": "šķīdums",
    "is": "Maisījums no izšķīdušās vielas un šķīdinātāja.",
    "is_not": "Nav tas pats, kas šķīdība.",
    "example": "0,9 % NaCl infūzija."}]},
 {"id": "piesatinats_koncentrets", "a": "piesātināts", "b": "koncentrēts",
  "difference": "Pie šķīdības robežas, pret vienkārši daudz vielas.",
  "chapter": "skidiba", "where": "5. nodaļa", "seed": "M21",
  "check": "Vai atšķaidīts Ca(OH)₂ var būt piesātināts?",
  "answer": "Jā: mazšķīstoša viela sasniedz līdzsvaru jau mazā koncentrācijā.",
  "rows": [
   {"term": "piesātināts",
    "is": "Šķīdums līdzsvarā ar neizšķīdušo vielu.",
    "is_not": "Nav vienkārši daudz vielas.",
    "example": "Ca(OH)₂: atšķaidīts, bet piesātināts."},
   {"term": "koncentrēts",
    "is": "Šķīdums ar lielu vielas daudzumu.",
    "is_not": "Nav līdzsvara stāvoklis.",
    "example": "Glikoze 5 %: koncentrēta, bet nepiesātināta."}]},
 {"id": "oksidetajs_oksidesanas", "a": "oksidētājs", "b": "oksidēšanās",
  "difference": "Viela, kas reducējas, pret elektronu atdošanas procesu.",
  "chapter": "redoks", "where": "12. nodaļa", "seed": "M14",
  "check": "Kas notiek ar oksidētāju: oksidējas vai reducējas?",
  "answer": "Reducējas: tas pievieno elektronus, kamēr reducētājs tos atdod.",
  "rows": [
   {"term": "oksidētājs",
    "is": "Viela, kas pievieno elektronus un pati reducējas.",
    "is_not": "Nav tas, kas oksidējas.",
    "example": "Cl₂ + 2e⁻ → 2Cl⁻: Cl₂ ir oksidētājs."},
   {"term": "oksidēšanās",
    "is": "Elektronu atdošana; oksidēšanas pakāpe pieaug.",
    "is_not": "Nav viela, bet process.",
    "example": "Zn − 2e⁻ → Zn²⁺: cinks oksidējas."}]},
 {"id": "baziskais_triple", "a": "bāziskais oksīds", "b": "bāziskā vide / bāziskais sāls",
  "difference": "Savienojuma klase, pH apgabals un sāls veids: trīs nozīmes.",
  "chapter": "klases", "where": "10. nodaļa", "seed": None,
  "check": "Vai bāziskais sāls vienmēr dod bāzisku vidi?",
  "answer": "Nē: Al(OH)SO₄ šķīdums ir skābs, jo hidrolizējas katjons.",
  "rows": [
   {"term": "bāziskais oksīds",
    "is": "Savienojums ar skābekli; reaģē ar skābēm.",
    "is_not": "Nav vide un nav sāls.",
    "example": "Na₂O + 2HCl → 2NaCl + H₂O."},
   {"term": "bāziskā vide",
    "is": "Šķīdums ar pH virs 7 (OH⁻ pārsvars).",
    "is_not": "Nav savienojuma klase.",
    "example": "NaOH šķīdums: pH ap 13."},
   {"term": "bāziskais sāls",
    "is": "Sāls ar OH grupām anjonā.",
    "is_not": "Nav ne sāls vide, ne oksīds.",
    "example": "Al(OH)SO₄: bāziskais, bet šķīdums skābs."}]},
 {"id": "skabais_sals", "a": "skābais sāls", "b": "skābs šķīdums",
  "difference": "Satur aizvietojamu H, pret pH mazāku par 7.",
  "chapter": "klases", "where": "10. nodaļa", "seed": "M06",
  "check": "NaHCO₃ ir skābais sāls; kāds ir tā šķīduma pH?",
  "answer": "Bāzisks, ap 8,3: HCO₃⁻ vairāk darbojas kā bāze (E28).",
  "rows": [
   {"term": "skābais sāls",
    "is": "Sāls ar aizvietojamu H anjonā.",
    "is_not": "Nav skābs šķīdums.",
    "example": "NaHCO₃: skābais sāls."},
   {"term": "skābs šķīdums",
    "is": "Vide ar pH zem 7 (H⁺ pārsvars).",
    "is_not": "Nav savienojuma klase.",
    "example": "NaHCO₃(aq): pH ap 8,3, tātad bāzisks."}]},
 {"id": "atommasa_trio", "a": "atommasa A_r", "b": "molmasa M / masas skaitlis A",
  "difference": "Bezdimensiju attiecība, g/mol, pret nuklonu skaitu.",
  "chapter": "atomi", "where": "2. nodaļa", "seed": "M29",
  "check": "Ko mēra g/mol: A_r, M vai A?",
  "answer": "M: molmasa. A_r ir bez mērvienības, A ir nuklonu skaits.",
  "rows": [
   {"term": "masas skaitlis A",
    "is": "Nuklonu skaits kodolā; vesels skaitlis.",
    "is_not": "Nav masa un nav mērvienība.",
    "example": "³⁵Cl: A = 35; ³⁷Cl: A = 37."},
   {"term": "relatīvā atommasa A_r",
    "is": "Atoma masas attiecība pret 1/12 no ¹²C.",
    "is_not": "Nav viena izotopa masa.",
    "example": "Cl: A_r = 35,45 (vidējais)."},
   {"term": "molmasa M",
    "is": "Viena mola masa; g/mol.",
    "is_not": "Nav bezmērvienības attiecība.",
    "example": "NaCl: M = 58,44 g/mol."}]},
 {"id": "hidratacija_trio", "a": "hidratācija", "b": "kristālhidrāts / hidrolīze",
  "difference": "Apvalks šķīdumā, ūdens režģī, pret reakciju ar ūdeni.",
  "chapter": "skidiba", "chapter_b": "hidrolize", "where": "5. un 9. nodaļa",
  "seed": None,
  "check": "Vai CuSO₄·5H₂O karsēšana ir hidrolīze?",
  "answer": "Nē: ūdens aiziet no režģa, bet neveidojas jauni joni; tā ir dehidratācija, nevis hidrolīze.",
  "rows": [
   {"term": "hidratācija",
    "is": "Ūdens apvalks ap daļiņu šķīdumā.",
    "is_not": "Nav ūdens kristāla režģī.",
    "example": "Na⁺(aq): jonus ieskauj H₂O."},
   {"term": "kristālhidrāts",
    "is": "Ūdens kristāla režģī noteiktā attiecībā.",
    "is_not": "Nav apvalks šķīdumā.",
    "example": "CuSO₄·5H₂O ir zils, bezūdens CuSO₄ ir balts."},
   {"term": "hidrolīze",
    "is": "Sāls jona reakcija ar ūdeni; maina pH.",
    "is_not": "Nav šķīšana un nav apvalks.",
    "example": "NH₄Cl šķīdums: skābs."}]},
 {"id": "valence_trio", "a": "valence", "b": "oksidēšanas pakāpe / jona lādiņš",
  "difference": "Saišu spēja, formāls uzskaitījums, pret daļiņas lādiņu.",
  "chapter": "redoks", "where": "12. nodaļa", "seed": "M13",
  "check": "Fe³⁺: kas ir 3 – valence, pakāpe vai lādiņš?",
  "answer": "Jona lādiņš: skaitlis pirms zīmes. FeCl₃ sastāvā tā pati III ir valence, bet +3 ir pakāpe.",
  "rows": [
   {"term": "valence",
    "is": "Saišu skaits, ko atoms veido savienojumā.",
    "is_not": "Nav lādiņš un nav uzskaite.",
    "example": "FeCl₃: Fe valence ir III (3 saites)."},
   {"term": "oksidēšanas pakāpe",
    "is": "Nosacīts lādiņš, ja elektroni piešķirti elektronegatīvākajam.",
    "is_not": "Nav reāls daļiņas lādiņš.",
    "example": "FeCl₃: Fe pakāpe ir +3 (vai III)."},
   {"term": "jona lādiņš",
    "is": "Veselas daļiņas reālais lādiņš.",
    "is_not": "Nav formāla uzskaite savienojumā.",
    "example": "Šķīdumā: Fe³⁺ (skaitlis pirms zīmes)."}]},
 {"id": "elektrolits_trio", "a": "elektrolīts", "b": "vadītājs / šķīstošs",
  "difference": "Disociē ūdenī, pret vada jebkā vai šķīst.",
  "chapter": "elektroliti", "where": "7. nodaļa", "seed": "M09",
  "check": "Varš vada; vai tas ir elektrolīts? Glikoze šķīst; vai tā ir?",
  "answer": "Nē un nē: varš vada ar elektroniem, glikoze neveido jonus (M09).",
  "rows": [
   {"term": "elektrolīts",
    "is": "Viela, kas ūdenī disociē jonos.",
    "is_not": "Nav jebkurš vadītājs.",
    "example": "NaCl(aq): Na⁺ + Cl⁻ vada."},
   {"term": "vadītājs",
    "is": "Viela, kas vada strāvu jebkādā veidā.",
    "is_not": "Nav obligāti jonu vadītājs.",
    "example": "Cu: vada ar elektroniem, nav elektrolīts."},
   {"term": "šķīstošs",
    "is": "Viela, kas šķīdumā pāriet molekulās vai jonos.",
    "is_not": "Nav tas pats, kas disociē.",
    "example": "Glikoze 5 %: šķīst, bet nevada."}]},
]


# ---------------------------------------------------------------- APPROVED_PENDING
# Every record stays status=pending until a named approver is set.
# scope ledger-s2 is one-to-one with SOURCE_LEDGER.md §2 [apstiprināt] rows.
# scope exam-convention is an open exam choice that is not one of those rows.
# iupac UNVERIFIED: the Gold Book fetch returned HTTP 403 and was not read.
_PENDING_KEYS = ("id", "canon_id", "scope", "question", "alternatives",
                 "locator", "rationale", "default", "status", "approver",
                 "confirmed", "iupac")
APPROVED_PENDING = [
    {"id": "ox_state", "canon_id": "ox_state", "scope": "ledger-s2",
     "question": "oksidēšanas vs oksidēšanās pakāpe",
     "alternatives": ["oksidēšanas pakāpe", "oksidēšanās pakāpe"],
     "locator": "E43; A p.14 uses both spellings; E s.45",
     "rationale": "The state is not the process noun, the ion charge, or the valence. The PDFs never pick one spelling. Gold Book O04365 was not read.",
     "default": "oksidēšanas pakāpe",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
    {"id": "bond_threshold", "canon_id": None, "scope": "exam-convention",
     "question": "ΔREN robeža 2 vai 1,7",
     "alternatives": ["kursa robeža 2", "robeža 1,7"],
     "locator": "E10; not a §2 [apstiprināt] row",
     "rationale": "Exam practice keeps the course cut-off and still shows both numbers. No editor has chosen one.",
     "default": "parādītas abas; eksāmenā kursa robeža 2",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
    {"id": "lattice", "canon_id": "lattice", "scope": "ledger-s2",
     "question": "atomu (kovalentais) kristālrežģis dimantam",
     "alternatives": ["atomu (kovalentais) kristālrežģis", "atomārs kristālrežģis"],
     "locator": "E15; A p.9 versus E s.36",
     "rationale": "The sources use atomārs both for diamond and for monoatomic noble gases. The working text splits them. No IUPAC lattice name was read.",
     "default": "atomu (kovalentais) kristālrežģis dimantam un silīcijam",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
    {"id": "ampho_ion", "canon_id": "ampho", "scope": "ledger-s2",
     "question": "amfiprotisks jons vai amfolīts, atšķirībā no amfotēra oksīda",
     "alternatives": ["amfiprotisks jons", "amfolīts"],
     "locator": "§2 ampho row; Al₂O₃, Zn(OH)₂ versus HCO₃⁻, H₂PO₄⁻, HPO₄²⁻",
     "rationale": "The oxide or hydroxide and the proton-exchanging ion need two names. Which ion name the course expects is not in the PDFs. Gold Book was not read.",
     "default": "amfiprotisks jons; amfolīts only as an unconfirmed alias",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
    {"id": "groups", "canon_id": None, "scope": "exam-convention",
     "question": "IUPAC 1–18, kursa A/B vai abi",
     "alternatives": ["IUPAC 1–18", "kursa A/B", "abi"],
     "locator": "not a §2 [apstiprināt] row",
     "rationale": "Both numberings stay visible until a course editor names the exam form.",
     "default": "parādīti abi",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
    {"id": "molar_volume", "canon_id": None, "scope": "exam-convention",
     "question": "22,414 vai 22,4 L/mol semināra uzdevumos",
     "alternatives": ["22,414 L/mol ar nosacījumiem", "22,4 L/mol"],
     "locator": "E60; D p.19–20",
     "rationale": "The seminar prints 22,4. The working page prints 22,414 at 0 °C and 101,325 kPa. Which figure an exam accepts is still open.",
     "default": "22,414 ar norādītiem apstākļiem",
     "status": "pending", "approver": None, "confirmed": False,
     "iupac": "UNVERIFIED"},
]

# Contexts where a BANNED hit is a legitimate record, not drift.
ALLOW = [
    "nevis oksidēšanās pakāpe",
    "gan „oksidēšanās pakāpe",
    "vai <em>oksidēšanās pakāpe",
    "Vai kursā lieto",
]


def _exempt_spans(html):
    spans = []
    for pat in (r'<aside class="note"[^>]*>.*?</aside>',
                r'<table class="data"><caption>Visi 61 labojumi.*?</table>',
                r'<table class="glossary">.*?</table>',
                # F01: the alphabetic index is a term register, not prose.
                # It lists aliases (amfolīts, molaritāte) beside their
                # canonical headwords exactly as the glossary row does, so
                # the "no alias in running text" rule does not apply here.
                r'<nav id="term-index"[^>]*>.*?</nav>',
                r'<section class="mist"[^>]*>.*?</section>',
                # F04: the mistake→repair route names the wrong form to correct
                # it (the „wrong” line and the diagnostic probes), exactly as a
                # mistake block does, so the alias/charge rules do not apply.
                r'<section class="mistake-route"[^>]*>.*?</section>'):
        for m in re.finditer(pat, html, re.S):
            spans.append(m.span())
    return spans


def _line(html, pos):
    return html.count("\n", 0, pos) + 1


def check(html, registry=True):
    """Return a list of 'line N: <match> -> <replacement> (<reason>)'.

    Hits inside correction blocks, the appendix correction table, the
    glossary, mistake blocks, or an ALLOW context are legitimate records
    of the source's wording, not drift. Notation exceptions never become
    an extra skip.
    """
    violations = check_registry() if registry else []
    exempt = _exempt_spans(html)
    for entry in BANNED:
        pattern, reason, replacement = entry[0], entry[1], entry[2]
        extra = entry[3] if len(entry) > 3 else []
        for m in re.finditer(pattern, html):
            if any(a <= m.start() < b for a, b in exempt):
                continue
            win = html[max(0, m.start() - 90):m.end() + 60]
            if any(a in win for a in ALLOW + extra):
                continue
            violations.append(
                f"line {_line(html, m.start())}: {m.group(0)!r} -> "
                f"{replacement} ({reason})")
    return violations


VS_PLACEMENT = {
 "skidiba_skidums": ["ch05"],
 "piesatinats_koncentrets": ["ch05"],
 "hidratacija_trio": ["ch05", "ch09"],
 "elektrolits_trio": ["ch07"],
 "skabais_sals": ["ch10"],
 "baziskais_triple": ["ch10"],
 "atommasa_trio": ["ch02"],
 "oksidetajs_oksidesanas": ["ch12"],
 "valence_trio": ["ch12"],
}

CELL_KEYS = ("term", "is", "is_not", "example")


def check_confusable(content, built):
    """content: {chapter_file: html with tokens}; built: final HTML."""
    v = []
    if len(CONFUSABLE) != 9:
        v.append(f"CONFUSABLE has {len(CONFUSABLE)} pairs (want 9)")
    for d in CONFUSABLE:
        pid = d["id"]
        if d.get("seed") is None and pid not in ("baziskais_triple", "hidratacija_trio"):
            v.append(f"{pid}: null seed needs a documented reason")
        texts = [d["difference"], d["check"]] + [
            r[k] for r in d["rows"] for k in CELL_KEYS]
        for t in texts:
            if len(t.split()) > 18:
                v.append(f"{pid}: cell over 18 words: {t[:60]!r}")
        for ch in VS_PLACEMENT.get(pid, []):
            if pid not in content.get(ch, ""):
                v.append(f"{pid}: token or section missing in {ch}")
        m = re.search(rf'id="vs-{re.escape(pid)}(?:-duo)?-check".{{0,600}}', built, re.S)
        if not m:
            v.append(f"{pid}: hidden check vs-{pid}-check missing in output")
        ctx = m.group(0) + built[max(0, m.start() - 2500):m.start()]
        if d["seed"]:
            if d["seed"] not in ctx:
                v.append(f"{pid}: seed {d['seed']} not named near the check")
        elif "Sēkla: nav" not in ctx:
            v.append(f"{pid}: null seed not disclosed near the table")
    if 'id="vs-pielikums"' not in built:
        v.append("appendix table vs-pielikums missing")
    return v


LEDGER_MARKERS = (
    ("oksidēšanas pakāpe", "ox_state"),
    ("amfiprotisks", "ampho"),
    ("kristālrežģis", "lattice"),
)

SCOPED_CHAPTERS = ("ch02", "ch03", "ch07", "ch08", "ch10", "ch11", "ch17")

# Settled drifts. A hit anywhere in these chapters fails. Pending source
# wording is not in this list; it stays in the correction and the open list.
SCOPED_DRIFT = (
    (r"molu attiecīb", "say 'vielas daudzumu attiecība' (quantity n, unit mol)"),
    (r"relatīvo molekulmas", "molmasa is not relatīvā molekulmasa (E05)"),
    (r"atommasas mērvienība", "g/mol belongs to molmasa M (E05)"),
)

REQUIRED_PROSE = {
    "ch02": ("molmasa", "relatīvā atommasa", "formulvienība"),
    "ch03": ("formulvienība",),
    "ch07": ("formulvienība", "amfiprotisk"),
    "ch08": ("sārms", "sārmain"),
    "ch10": ("sārmiem", "kristālrežģi", "atomāras"),
    "ch11": ("vielas daudzumu attiecība", "nav mehānisms"),
    "ch17": ("[apstiprināt]", "vielas daudzums nav rēķināms", "Apstiprinātājs: nav."),
}


def _ledger_section(text):
    start = text.split("## 2. Terminology", 1)
    if len(start) != 2:
        return ""
    return start[1].split("## 3.", 1)[0]


def check_registry():
    """One [apstiprināt] ledger row ↔ one pending record. None are approved."""
    v = []
    root = pathlib.Path(__file__).resolve().parent.parent
    ledger_path = root / "SOURCE_LEDGER.md"
    if not ledger_path.exists():
        return ["registry: SOURCE_LEDGER.md missing"]
    section = _ledger_section(ledger_path.read_text(encoding="utf-8"))
    rows = [ln for ln in section.splitlines()
            if ln.startswith("|") and "[apstiprināt]" in ln
            and not ln.startswith("| ---") and not ln.startswith("| Use")]
    mapped = []
    for ln in rows:
        hits = [cid for needle, cid in LEDGER_MARKERS if needle in ln]
        if len(hits) != 1:
            v.append(f"registry: §2 row maps to {hits}: {ln[:80]}")
            continue
        mapped.append(hits[0])
    if len(rows) != 3 or len(set(mapped)) != 3:
        v.append(f"registry: want 3 distinct [apstiprināt] rows, got {len(rows)} / {mapped}")
    pending_s2 = [d for d in APPROVED_PENDING if d.get("scope") == "ledger-s2"]
    got = [d.get("canon_id") for d in pending_s2]
    if sorted(got) != sorted(mapped):
        v.append(f"registry: ledger-s2 canon ids {got} != ledger rows {mapped}")
    confirm = sorted(k for k, rec in CANON.items() if rec.get("confirm"))
    if confirm != sorted(set(mapped)):
        v.append(f"registry: CANON confirm flags {confirm} != [apstiprināt] {sorted(set(mapped))}")
    ids = [d.get("id") for d in APPROVED_PENDING]
    if len(ids) != len(set(ids)):
        v.append("registry: duplicate pending id")
    for d in APPROVED_PENDING:
        missing = [k for k in _PENDING_KEYS if k not in d]
        if missing:
            v.append(f"registry: {d.get('id')} missing {missing}")
            continue
        if d["status"] != "pending" or d["confirmed"] is not False or d["approver"] is not None:
            v.append(f"registry: {d['id']} is not an open, unapproved decision")
        if not isinstance(d["alternatives"], list) or len(d["alternatives"]) < 2:
            v.append(f"registry: {d['id']} needs at least two alternatives")
        if not d["locator"] or not d["rationale"]:
            v.append(f"registry: {d['id']} needs a locator and a rationale")
        if d["scope"] == "ledger-s2" and d["iupac"] != "UNVERIFIED":
            v.append(f"registry: {d['id']} IUPAC status must stay UNVERIFIED")
        if d["scope"] == "ledger-s2" and d["canon_id"] not in CANON:
            v.append(f"registry: {d['id']} canon_id missing from CANON")
        if d["scope"] not in ("ledger-s2", "exam-convention"):
            v.append(f"registry: {d['id']} has unknown scope")
    if len(pending_s2) != 3:
        v.append(f"registry: {len(pending_s2)} ledger-s2 decisions (want 3)")
    extra = [d["id"] for d in APPROVED_PENDING if d.get("scope") != "ledger-s2"]
    if len(APPROVED_PENDING) - len(pending_s2) != len(extra):
        v.append("registry: scope partition failed")
    note_ids = {row["id"] for row in NOTATION_EXCEPTIONS}
    if note_ids != {"greek_quantity", "formula_markup"}:
        v.append(f"registry: notation exceptions {note_ids}")
    for token in note_ids:
        if any(token in a for a in ALLOW):
            v.append(f"registry: {token} leaked into ALLOW")
    for row in NOTATION_EXCEPTIONS:
        if not row.get("rule") or not row.get("ledger"):
            v.append(f"registry: notation row {row.get('id')} incomplete")
    v.extend(check_aliases())
    v.extend(check_scoped())
    return v


def check_aliases():
    from glossary import ALIASES, G
    terms = [row[0] for row in G]
    v = []
    if not ALIASES:
        return ["alias: ALIASES empty"]
    seen = set()
    for a in ALIASES:
        name = a.get("alias")
        target = a.get("target")
        if name in seen:
            v.append(f"alias: duplicate {name}")
        seen.add(name)
        if a.get("equivalence") is not False:
            v.append(f"alias: {name} must not claim equivalence")
        if target not in terms:
            v.append(f"alias: {name} target {target!r} is not a glossary headword")
        if name == target:
            v.append(f"alias: {name} points at itself")
        if name not in terms:
            v.append(f"alias: {name} has no glossary row")
        if not a.get("locator"):
            v.append(f"alias: {name} has no locator")
    if "molaritāte" not in seen or "amfolīts" not in seen:
        v.append("alias: molaritāte and amfolīts rows are required")
    amph = next(d for d in APPROVED_PENDING if d["id"] == "ampho_ion")
    alias = next(a for a in ALIASES if a["alias"] == "amfolīts")
    if alias["status"] != "pending" or amph["status"] != "pending":
        v.append("alias: amfolīts must stay pending with ampho_ion")
    if alias["target"] != "amfiprotisks jons":
        v.append("alias: amfolīts must point at amfiprotisks jons")
    return v


def check_scoped():
    root = pathlib.Path(__file__).resolve().parent / "content"
    v = []
    for ch in SCOPED_CHAPTERS:
        html = (root / f"{ch}.html").read_text(encoding="utf-8")
        for pattern, reason in SCOPED_DRIFT:
            m = re.search(pattern, html)
            if m:
                v.append(f"scoped {ch}: {m.group(0)!r} -> {reason}")
        for needle in REQUIRED_PROSE[ch]:
            if needle not in html:
                v.append(f"scoped {ch}: missing canonical {needle!r}")
        if "<script" in html:
            v.append(f"scoped {ch}: terminology chapter grew a script")
    # The coefficient sentence is ordinary prose, readable with JS off.
    lead = (root / "ch11.html").read_text(encoding="utf-8")
    m = re.search(r'<p class="lead">.*?</p>', lead, re.S)
    if not m or "vielas daudzumu attiecība" not in m.group(0):
        v.append("scoped ch11: canonical ratio is not in the lead paragraph")
    return v


# ------------------------------------------------- F05 language-of-parts
# WCAG 2.2 SC 3.1.2 (AGENTS §7): the master is lang="lv", so the English
# glossary column is foreign-language text and must be programmatically
# determinable.  Without the tag a screen reader reads "amount of
# substance" with Latvian phonemes; with the tag on the wrong cell it
# reads Latvian with English phonemes.  Both directions fail.
#
# This is the one part of the F05 morphology rail that does not wait on
# T01: it adds no term, no equivalent and no translation, it only marks
# the language of a cell the master already ships.
_GLOSS_TABLE = re.compile(r'<table class="glossary">.*?</table>', re.S)
_GLOSS_ROW = re.compile(r'<tr data-l="[^"]*">(?P<cells>.*?)</tr>', re.S)
# The row opens with the Latvian headword cell, so the English cell is the
# second one; the tag must sit on it and nowhere else.
_EN_CELL = re.compile(r'^<th scope="row">.*?</th><td(?P<attrs>[^>]*)>(?P<text>.*?)</td>', re.S)


def check_lang(html):
    """Every glossary English cell is tagged lang="en", non-empty, and alone.

    F05 failure states, enforced: no empty translation renders; lang="en"
    sits only on English spans; the document keeps its Latvian lang.
    """
    v = []
    m = _GLOSS_TABLE.search(html)
    if not m:
        return ["lang: the glossary table is missing from the output"]
    table = m.group(0)
    rows = _GLOSS_ROW.findall(table)
    if len(rows) != table.count('<tr data-l'):
        v.append(f"lang: parsed {len(rows)} glossary rows, "
                 f"table declares {table.count('<tr data-l')}")
    tagged = table.count('<td lang="en">')
    if tagged != len(rows):
        v.append(f"lang: {tagged} English cells tagged lang=\"en\", want {len(rows)}")
    for cells in rows:
        em = _EN_CELL.match(cells)
        if not em:
            v.append("lang: glossary row has no English second cell: " + cells[:70])
            continue
        if em.group("attrs") != ' lang="en"':
            v.append("lang: the English cell is not tagged lang=\"en\" "
                     f"(attrs={em.group('attrs')!r}): {em.group('text')[:40]}")
        if not em.group("text").strip():
            v.append("lang: an empty English equivalent renders")
    leaked = html.replace(table, "", 1).count('lang="en"')
    if leaked:
        v.append(f"lang: {leaked} lang=\"en\" outside the glossary English column")
    if 'lang="lv"' not in html:
        v.append("lang: the document lost its lang=\"lv\"")
    return v


def self_test():
    """Positive canonical prose, negative banned prose, pending boundary, Greek non-exemption."""
    v = check_registry()
    good = ("<p>Molmasa <i>M</i> ir g/mol. Formulvienība nav molekula. "
            "Bāze, sārms un hidroksīds ir trīs nosaukumi. "
            "Reakcijas veids nav solis pa solim. ρ = 1,25. α ir daļa.</p>")
    bad_hits = check(good, registry=False)
    if bad_hits:
        v.append("self-test positive fixture failed: " + "; ".join(bad_hits))
    neg = "<p>Šeit molu skaits ir 2, un NaCl molekula disociē, un reakcijas mehānisms ir savienošanās.</p>"
    neg_hits = check(neg, registry=False)
    if len(neg_hits) < 3:
        v.append(f"self-test negative fixture returned {len(neg_hits)} hits, want 3")
    boundary = "<p>Tāpēc „NaCl molekula” ir kļūda. Vai kursā lieto oksidēšanas pakāpe vai oksidēšanās pakāpe?</p>"
    if check(boundary, registry=False):
        v.append("self-test boundary: quoted correction was flagged")
    greek = "<p>molu skaits un ρ = 1,25</p>"
    if not check(greek, registry=False):
        v.append("self-test: a Greek letter exempted a Latvian ban")
    # F05 language-of-parts fixtures: a tagged row passes, an untagged row
    # fails, and a tag on a Latvian cell is the mirror defect.  The document
    # lang is part of the fixture: check_lang also asserts it is still there.
    doc = '<html lang="lv"><body>'
    row = ('<tr data-l="A"><th scope="row">atomkaitlis</th>'
           '<td lang="en">atomic number</td><td><var>Z</var></td></tr>')
    if check_lang(doc + '<table class="glossary">' + row + '</table></body></html>'):
        v.append("self-test: a tagged English cell was flagged")
    untagged = row.replace('<td lang="en">', '<td>')
    if not check_lang(doc + '<table class="glossary">' + untagged + '</table></body></html>'):
        v.append("self-test: an untagged English cell passed")
    empty = row.replace('>atomic number<', '><')
    if not any('empty' in x for x in
               check_lang(doc + '<table class="glossary">' + empty + '</table></body></html>')):
        v.append("self-test: an empty English equivalent passed")
    # The tag on the symbol cell instead of the English cell: wrong target.
    misplaced = row.replace('<td lang="en">atomic number</td><td>',
                            '<td>atomic number</td><td lang="en">')
    if not check_lang(doc + '<table class="glossary">' + misplaced + '</table></body></html>'):
        v.append("self-test: lang=\"en\" was accepted on a non-English cell")
    # A document that lost its Latvian lang must fail too.
    if not any('lang=\"lv\"' in x for x in
               check_lang('<table class="glossary">' + row + '</table>')):
        v.append("self-test: a missing document lang passed")
    if any(d["confirmed"] for d in APPROVED_PENDING):
        v.append("self-test: a pending decision is marked confirmed")
    return v


def summary():
    return (f"terms: {len(CANON)} canonical, {len(BANNED)} banned patterns, "
            f"{len(CONFUSABLE)} confusable pairs, "
            f"{len(APPROVED_PENDING)} pending approvals, "
            f"{len(NOTATION_EXCEPTIONS)} notation exceptions")


if __name__ == "__main__":
    import pathlib, sys
    ROOT = pathlib.Path(__file__).resolve().parent
    out_file = ROOT.parent / "Master_temats_1_skidumi_un_kimiskas_reakcijas.html"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        out_file = pathlib.Path(sys.argv[1])
    violations = check(out_file.read_text(encoding="utf-8"))
    if violations:
        print(f"terms: {len(violations)} FAIL")
        for v in violations:
            print("FAIL ", v)
        sys.exit(1)
    print(f"terms: PASS ({summary()}, 0 violations)")
