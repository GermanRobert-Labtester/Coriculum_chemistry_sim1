#!/usr/bin/env python3
"""Canonical Latvian terminology for Topic 13 (Task 04, schema extended in T02).

One preferred spelling per concept. Forbidden forms are allowed only in
deliberate quote / wrong-line / change-log / nelietot contexts — enforced by
tools/check_terms.py.

Register separation (T02.1.1):
  definition  — what the student reads as the term's meaning.
  decision_lv — the student-facing Latvian decision sentence, rendered in the
                term card. It must be Latvian and must carry a reason.
  note_en     — maintainer nuance, English. It is NOT rendered on the page; it
                lives in qa/termbase_notes.md, keyed by the stable term id.
  source_ids  — stable source ids (the SOURCE_IDS vocabulary in
                tools/master_data.py) that warrant the term.
  status      — apstiprināts | jāpārbauda | avota formāts.

Do not invent Latvian terms. Unverified rows stay status="jāpārbauda".
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Letters that occur in Latvian orthography and are not ASCII. A student-facing
# decision sentence must contain at least one of them.
LATVIAN_MARKERS = frozenset("āčģēīķļņōŗšūž")
VALID_STATUSES = frozenset({"apstiprināts", "jāpārbauda", "avota formāts"})


@dataclass(frozen=True)
class Term:
    id: str
    preferred: str
    forbidden: tuple[str, ...]
    definition: str
    example: str
    source: str
    decision_lv: str
    note_en: str
    source_ids: tuple[str, ...]
    status: str  # apstiprināts | jāpārbauda | avota formāts
    kind: str = "term"  # term | process | method | symbol | species
    formula: str = ""
    chapter: str = "11"
    search_extra: str = ""  # extra tokens for the glossary filter

    @property
    def decision(self) -> str:
        """Backward-compatible alias for the maintainer note (pre-T02 name)."""
        return self.note_en



@dataclass(frozen=True)
class Species:
    id: str
    name: str
    formula: str
    ox: str
    note: str
    confusion: str  # common wrong form / look-alike
    pair_with: str = ""  # id of contrast partner


@dataclass(frozen=True)
class Contrast:
    id: str
    left: str
    left_formula: str
    right: str
    right_formula: str
    cue: str
    source: str


# ---------------------------------------------------------------- terms (§E)
TERMS: list[Term] = [
    Term(
        id="oksidēšanās",
        preferred="oksidēšanās",
        forbidden=(),  # “oksidēšanās pakāpe” is gated under oksidēšanas_pakāpe
        definition="Process, kurā viela atdod elektronus; elementa oksidēšanas pakāpe paaugstinās.",
        example="Fe²⁺ → Fe³⁺ + e⁻",
        source="LEC P013; SOURCE_AUDIT §E",
        decision_lv=(
            "„Oksidēšanās” ir process: viela atdod elektronus un tās oksidēšanas pakāpe "
            "paaugstinās. „Oksidēšana” ir oksidētāja darbība, tāpēc šos vārdus nedrīkst "
            "lietot kā sinonīmus."
        ),
        note_en="Process noun. Oksidēšana = oksidētāja darbība pret citu vielu.",
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="process",
        search_extra="oksidēšana process",
    ),
    Term(
        id="oksidēšana",
        preferred="oksidēšana",
        forbidden=(),
        definition="Oksidētāja darbība: oksidētājs oksidē citu vielu un pats reducējas.",
        example="KMnO₄ oksidē Fe²⁺",
        source="LEC P015–P017; §E",
        decision_lv=(
            "„Oksidēšana” nozīmē oksidētāja darbību pret citu vielu, nevis procesu; "
            "procesu apzīmē ar vārdu „oksidēšanās”."
        ),
        note_en="Kept as agent action; not a synonym of oksidēšanās.",
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="process",
    ),
    Term(
        id="oksidēšanas_pakāpe",
        preferred="oksidēšanas pakāpe",
        forbidden=("oksidēšanās pakāpe",),
        definition="Formāls elektronu uzskaites skaitlis; zīme pirms skaitļa (+7, −2).",
        example="Mn(+7); S(+4); O(−2)",
        source="LEC P088, P100; §E; T1",
        decision_lv=(
            "Šo formu lieto gan lekcijas tekstā, gan Latvijas Zinātņu akadēmijas ķīmijas "
            "terminu vārdnīcā; forma ar garo patskani (“oksidēšanās pakāpe”) paliek "
            "tikai avota citātos."
        ),
        note_en=(
            "Majority LEC usage + standard term. Avota otrā forma tikai citātos. "
            "Portal 2026-11-09: LZA TK Terminoloģija 7 (Ķīmijas terminu vārdnīca) approves "
            "“oksidēšanas pakāpe”; the competing form exists only in the 1979 LPE thematic "
            "list project."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        search_extra="oksidēšanās pakāpe oxidation state",
    ),
    Term(
        id="oks_red",
        preferred="oksidēšanās-reducēšanās sistēma (oks/red sistēma)",
        forbidden=(),
        definition="Oksidētās un reducētās formas pāris, kas var pāriet viena otrā (Ox/Red).",
        example="MnO₄⁻/Mn²⁺",
        source="LEC P018, P031; §E",
        decision_lv=(
            "Īsuminājumu „oks/red” drīk lietot tekstā, bet nodaļu virzienos un glosārijā "
            "termins jāraksta pilnīgi."
        ),
        note_en="Abbreviation oks/red is allowed in body; spell out in headings/glossary.",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="oks/red pāris couple",
    ),
    Term(
        id="oksidētājs",
        preferred="oksidētājs",
        forbidden=(),
        definition="Viela, kas pieņem elektronus un pati reducējas.",
        example="KMnO₄, Cl₂, O₂",
        source="LEC P015–P017",
        decision_lv=(
            "Oksidētājs ir viela, kas reakcijā pieņem elektronus un pati reducējas; tā ir "
            "loma konkrētā reakcijā, nevis pastāvīgs vielas apzīmējums."
        ),
        note_en="Role in a reaction, not a permanent label of a substance.",
        source_ids=("LEC",),
        status="apstiprināts",
    ),
    Term(
        id="reducētājs",
        preferred="reducētājs",
        forbidden=(),
        definition="Viela, kas atdod elektronus un pati oksidējas.",
        example="Fe²⁺, SO₃²⁻, H₂S",
        source="LEC P015–P017",
        decision_lv=(
            "Reducētājs ir viela, kas reakcijā atdod elektronus un pati oksidējas; tā ir "
            "loma reakcijā."
        ),
        note_en="Role in a reaction.",
        source_ids=("LEC",),
        status="apstiprināts",
    ),
    Term(
        id="pusreakcija",
        preferred="pusreakcija",
        forbidden=("pusrekcija",),
        definition="Atsevišķa oksidēšanās vai reducēšanās daļa ar elektroniem.",
        example="Fe²⁺ → Fe³⁺ + e⁻",
        source="LEC P177; C2",
        decision_lv=(
            "Vārds rakstāms ar „-reakcija” (avota drukas kļūda „pusrekcija”); jonu-elektronu "
            "metodē šo reakcijas daļu sauc par pusreakciju."
        ),
        note_en=(
            "Spelling with -reakcija. Method: jonu-elektronu (pusreakciju) metode. "
            "Portal 2026-11-09: neither “pusreakcija” nor “pusrekcija” is attested; the "
            "decision rests on the course spelling and Latvian orthography."
        ),
        source_ids=("LEC", "T13"),
        status="apstiprināts",
        search_extra="pusrekcija half-reaction",
    ),
    Term(
        id="standartpotenciāls",
        preferred="standartpotenciāls E°",
        forbidden=(),
        definition="Reducēšanas potenciāls pie pH 0, vienības aktivitātēm un 298 K.",
        example="E°(Fe³⁺/Fe²⁺) = +0,77 V",
        source="LEC P037; A26; §E",
        decision_lv=(
            "Standartpotenciāls E° ir reducēšanas potenciāls pie pH 0, vienības aktivitātēm "
            "un 298 K; to nedrīkst sajaukt ar E°′ vai ar faktisko E."
        ),
        note_en=(
            "Synonym normālpotenciāls once in 13.A caption; not E°′. Distinct from actual E. "
            "Portal 2026-11-09: “standartpotenciāls” is approved, but in a construction "
            "dictionary; the two-word “standarta potenciāls” is not attested, so the course "
            "one-word form is kept."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        search_extra="normālpotenciāls E0",
    ),
    Term(
        id="potencials_E",
        preferred="potenciāls E",
        forbidden=(),
        definition="Faktiskais elektroda vai elementa potenciāls jebkuros apstākļos; Nernsts saista E ar E°.",
        example="E(MnO₄⁻/Mn²⁺) pie pH 3 = 1,226 V",
        source="LEC P032–P045; 3. nod.",
        decision_lv=(
            "Potenciāls E ir faktiskais elektroda potenciāls jebkurā koncentrācijā un pH; "
            "to aprēķina pēc Nernsta vienādojuma, nevis ņem no E°."
        ),
        note_en="Not E° and not E°′; any concentration or pH.",
        source_ids=("LEC",),
        status="apstiprināts",
        kind="symbol",
        search_extra="faktiskais potenciāls Nernst",
    ),
    Term(
        id="e_prime",
        preferred="E°′",
        forbidden=(),
        definition="Bioloģiskais standartpotenciāls pie pH 7. E°′ = E° − 0,0592·(m/n)·7 (m = H⁺ skaits, n = e⁻ skaits).",
        example="E°′(O₂/H₂O) = +0,815 V",
        source="A5; 2. un 8. nod.",
        decision_lv=(
            "E°′ ir bioloģiskais standartpotenciāls pie pH 7; to nedrīkst lietot vienā darba "
            "kolonnā ar E°."
        ),
        note_en="Never mix with E° in one working column.",
        source_ids=("LEC", "CAMP"),
        status="apstiprināts",
        kind="symbol",
    ),
    Term(
        id="eds",
        preferred="elektrodzinējspēks (EDS)",
        forbidden=(),
        definition="Galvaniskā elementa spriegums: E(katods) − E(anods).",
        example="E = 1,100 V (Cu/Zn)",
        source="LEC P023–P027; §E",
        decision_lv=(
            "Elektrodzinējspēks ir E(katods) − E(anods), nevis divu potenciālu summa; "
            "E₁ apzīmē lielāko reducēšanas potenciālu."
        ),
        note_en="Not the sum of two potentials; E₁ is the larger reduction potential.",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="EDS EMF",
    ),
    Term(
        id="elektrods",
        preferred="elektrods",
        forbidden=(),
        definition="Vadošā fāze (piemēram, Pt stienis). Oks/red sistēma / puselements ir veselā Ox/Red sistēma.",
        example="Pt | H⁺/H₂ (SHE)",
        source="LEC P029; §E",
        decision_lv=(
            "Elektrods ir vadītājs (piemēram, Pt stienis), bet oksidēšanās-reducēšanās "
            "sistēma ir viss Ox/Red pāris kopumā."
        ),
        note_en="SHE is the standard hydrogen electrode, not a couple name.",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="SHE standartelektrods puselements",
    ),
    Term(
        id="she",
        preferred="standarta ūdeņraža elektrods (SHE)",
        forbidden=("SHE pāris", "SHE pāra"),
        definition="Atskaites elektrods: a(H⁺) = 1, p(H₂) = 1 bar; E° = 0,00 V.",
        example="2H⁺ + 2e⁻ ⇌ H₂",
        source="LEC P029; A26",
        decision_lv=(
            "SHE ir elektroda nosaukums, nevis oksidēšanās-reducēšanās pāra apzīmējums; "
            "atskaites elektrods ir ūdeņraža elektrods."
        ),
        note_en=(
            "SHE is an electrode name, not an Ox/Red couple label. Portal 2026-11-09: "
            "“ūdeņraža elektrods” is approved (LZA TK Terminoloģija 5); the compound "
            "“standarta ūdeņraža elektrods” is not attested, so the course form is kept."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        search_extra="SHE",
    ),
    Term(
        id="ekvivalences_punkts",
        preferred="ekvivalences punkts",
        forbidden=(),
        definition="Teorētiskais punkts, kurā n(titrants)·z = n(analīts)·z.",
        example="n₁z₁ = n₂z₂",
        source="LEC P248; A10",
        decision_lv=(
            "Ekvivalences punkts ir teorētiskais punkts, kurā n(titrants)·z = n(analīts)·z; "
            "to nedrīkst sajaukt ar novērojamo krāsas maiņu."
        ),
        note_en=(
            "Not the observed colour change. Portal 2026-11-09: approved (LZA TK "
            "Terminoloģija 7)."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
    ),
    Term(
        id="beigu_punkts",
        preferred="titrēšanas beigu punkts",
        forbidden=(),
        definition="Novērojamais signāls, kas norāda titrēšanas beigas.",
        example="pirmais noturīgais vāji rozā",
        source="LEC P253; A10",
        decision_lv=(
            "Titrēšanas beigu punkts ir novērojams signāls, un tas var nedaļzīgi "
            "atšķirties no ekvivalences punkta."
        ),
        note_en=(
            "Observed; may differ slightly from the equivalence point. Portal 2026-11-09: "
            "approved (LZA TK Terminoloģija 7)."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        search_extra="beigu punkts",
    ),
    Term(
        id="titrants",
        preferred="titrants",
        forbidden=(),
        definition="Šķīdums ar precīzi zināmu koncentrāciju, ko pievieno no biretes.",
        example="KMnO₄ 0,0200 mol/L",
        source="LEC P244; L25",
        decision_lv=(
            "Titrants ir precīzi zināmas koncentrācijas šķīdums, ko pievieno no biretes; "
            "to nedrīkst sajaukt ar kolbā esošo analītu."
        ),
        note_en=(
            "In the burette. Portal 2026-11-09: approved (State Language Centre chemistry "
            "term list)."
        ),
        source_ids=("LEC", "L25", "TERMI"),
        status="apstiprināts",
    ),
    Term(
        id="analīts",
        preferred="analīts",
        forbidden=(),
        definition="Nosakāmā viela analizējamajā šķīdumā (kolbā).",
        example="Fe²⁺ / FeSO₄",
        source="LEC P244; §E; T2",
        decision_lv=(
            "„Analīts” apzīmē nosakāmo vielu kolbā, atšķirībā no procesa „analīze”; "
            "terminoloģijas portālā šī forma nav apstiprināta, tāpēc tā paliek "
            "jāpārbauda."
        ),
        note_en=(
            "analīze = process; analīts = substance. Source “100 ml analīzes” is quoted "
            "only. Portal 2026-11-09: “analīts” is not attested; the academic dictionary "
            "(LZA TK Terminoloģija 7) approves “analizējamais šķīdums” for the flask "
            "content. Status therefore stays jāpārbauda."
        ),
        source_ids=("QA",),
        status="jāpārbauda",
        search_extra="analīze analizējamais",
    ),
    Term(
        id="analīze",
        preferred="analīze",
        forbidden=(),
        definition="Process (tilpuma analīze, kvalitatīvā analīze), nevis parauga viela.",
        example="tilpuma analīze (volumetrija)",
        source="§E; T2",
        decision_lv=(
            "„Analīze” ir process (tilpuma analīze, kvalitatīvā analīze); kursa avotos "
            "šo vārdu lieto arī par parauga šķīdumu, un tā nozīme tiek citēta tikai "
            "avota tekstā."
        ),
        note_en=(
            "Keep for the process sense; sample sense is forbidden outside quotes. Portal "
            "2026-11-09: “analīze” approved (State Language Centre term list)."
        ),
        source_ids=("LEC", "L25", "TERMI"),
        status="apstiprināts",
        kind="process",
    ),
    Term(
        id="z",
        preferred="ekvivalences skaitlis z",
        forbidden=(),
        definition="Elektronu skaits uz vienu formulas vienību konkrētajā reakcijā.",
        example="z(KMnO₄) = 5; z(Fe²⁺) = 1",
        source="LEC §3.1; B9",
        decision_lv=(
            "Ekvivalences skaitlis z ir elektronu skaits uz vienu formulas vienību; to nav "
            "vielas daudzums n."
        ),
        note_en=(
            "Not the same as n (amount of substance). Portal 2026-11-09: "
            "“ekvivalences skaitlis” is not attested (only “ekvivalences punkts”), so the "
            "course wording is kept and the distinction is taught from the LEC."
        ),
        source_ids=("LEC",),
        status="apstiprināts",
        kind="symbol",
    ),
    Term(
        id="c",
        preferred="molārā koncentrācija c(X)",
        forbidden=(),
        definition="Vielas daudzums tilpuma vienībā; vienība mol/L.",
        example="c(Fe²⁺) = 0,1235 mol/L",
        source="LEC §3.1; §E",
        decision_lv=(
            "Mūsdienu tekstā lieto molāro koncentrāciju c(X) ar vienību mol/L; normālā "
            "koncentrācija ir novecojusi lielums."
        ),
        note_en=(
            "Preferred over obsolete normality in modern text. Portal 2026-11-09: "
            "“molārā koncentrācija” approved (LZA TK Terminoloģija 7)."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="symbol",
        search_extra="molārā",
    ),
    Term(
        id="normalitate",
        preferred="normālā (ekvivalenta) koncentrācija",
        forbidden=(),
        definition="Vēsturisks lielums (ekv/L). Ja uzdevums to prasa, atbildi sniedz blakus molārajai.",
        example="0,333 ekv/L = 5·0,0667 mol/L",
        source="A18; §E",
        decision_lv=(
            "Normālā (ekvivalenta) koncentrācija ir vēsturisks lielums; ja uzdevums to "
            "prasa, atbildi sniedz blakus molārajai koncentrācijai."
        ),
        note_en="Obsolete; shown only when the LEC task asks for it.",
        source_ids=("LEC",),
        status="avota formāts",
        kind="symbol",
    ),
    Term(
        id="jodometrija",
        preferred="jodometrija",
        forbidden=(),
        definition="Metode, kurā analīta oksidētājs izdala I₂ no I⁻ pārākuma; titrants ir Na₂S₂O₃.",
        example="I₂ + 2S₂O₃²⁻ → 2I⁻ + S₄O₆²⁻",
        source="LEC P250; A8",
        decision_lv=(
            "Jodometrijā analīta oksidētājs izdala I₂ no I⁻ pārākuma, un titrants ir "
            "Na₂S₂O₃."
        ),
        note_en=(
            "Distinguished from jodimetrija. Both terms are kept. Portal 2026-11-09: "
            "“jodometrija” approved (State Language Centre chemistry term list); LEC P251 "
            "defines it differently (titrant with I⁻), a source conflict kept visible in "
            "13.E."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="method",
        search_extra="tiosulfāts",
    ),
    Term(
        id="jodimetrija",
        preferred="jodimetrija",
        forbidden=(),
        definition="Metode, kurā titrants ir I₂.",
        example="I₂ + reducētājs",
        source="A8",
        decision_lv=(
            "Jodimetrijā titrants ir I₂; šī forma kursa un terminoloģijas portāla "
            "avotos nav apstiprināta, tāpēc tā paliek jāpārbauda."
        ),
        note_en=(
            "Distinguished from jodometrija. Both terms are kept. Portal 2026-11-09: "
            "“jodimetrija” is not attested; the term is introduced only to contrast with "
            "jodometrija, so the status stays jāpārbauda."
        ),
        source_ids=("QA",),
        status="jāpārbauda",
        kind="method",
    ),
    Term(
        id="permanganatometrija",
        preferred="permanganatometrija",
        forbidden=(),
        definition="Titrimetrijas metode ar KMnO₄ titrantu skābā vidē.",
        example="MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O",
        source="LEC P251",
        decision_lv=(
            "Permanganatometrija ir titrimetrijas metode, kurā titrants ir KMnO₄ un "
            "vidi ir skāba."
        ),
        note_en=(
            "Keep. Portal 2026-11-09: “permanganatometrija” is not attested; the term is "
            "kept on the course wording (LEC P251)."
        ),
        source_ids=("LEC",),
        status="apstiprināts",
        kind="method",
    ),
    Term(
        id="nogulsnēšana",
        preferred="nogulsnēšanas (precipitācijas) titrēšana",
        forbidden=("sedimentācija", "sedimentācijas"),
        definition="Titrēšana, kurā veidojas nogulsnes. Gravitācijas nosēdēšanās nav titrēšanas metode.",
        example="Ag⁺ + Cl⁻ → AgCl↓",
        source="LEC P249; A9",
        decision_lv=(
            "Titrēšanas veidu nosaka pēc nogulsnes veidošanās, nevis pēc gravitācijas "
            "nosēdēšanās."
        ),
        note_en=(
            "Replace the source’s gravity-settling wording with precipitation titration. "
            "Portal 2026-11-09: “nogulsnēšana” approved (LZA TK Terminoloģija 7)."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="method",
        search_extra="sedimentācija",
    ),
    Term(
        id="atf",
        preferred="ATF",
        forbidden=("ATP",),
        definition="Adenozīntrifosfāts, šūnas enerģijas pārnesējs. Angļu saīsinājums iekavās vienreiz.",
        example="ADF + Pᵢ → ATF",
        source="LEC P232; B11; T4",
        decision_lv=(
            "Latviešu literatūrā lieto ATF; angļu saīsinājums ATP parādās tikai vienu "
            "reizi, iekavās."
        ),
        note_en="Latvian ATF / ADF; English abbreviation once in brackets (term-once).",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="ATP adenozīntrifosfāts",
    ),
    Term(
        id="adf",
        preferred="ADF",
        forbidden=("ADP",),
        definition="Adenozīndifosfāts. Angļu saīsinājums iekavās vienreiz kopā ar ATF.",
        example="ATF ⇌ ADF + Pᵢ",
        source="LEC P232; B11",
        decision_lv=(
            "ADF ir adenozīndifosfāts un to lieto kopā ar ATF; angļu saīsinājums ADP "
            "parādās tikai vienu reizi, iekavās."
        ),
        note_en="Paired with ATF.",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="ADP",
    ),
    Term(
        id="enzīms",
        preferred="enzīms",
        forbidden=(),
        definition="Bioloģiskais katalizators; ferments iekavās vienreiz.",
        example="oksidoreduktāze",
        source="LEC P005; §E",
        decision_lv=(
            "Ieteicams lietot vārdu „enzīms”; „ferments” tiek minēts vienu reizi kā "
            "sinonīms."
        ),
        note_en="Prefer enzīms; ferments once as synonym.",
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="ferments",
    ),
    Term(
        id="oksidoreduktāze",
        preferred="oksidoreduktāze",
        forbidden=(),
        definition="Enzīms, kas katalizē oksidēšanās-reducēšanās reakciju.",
        example="dehidrogenāzes, oksidāzes",
        source="LEC P005",
        decision_lv=(
            "Oksidoreduktāze ir enzīms, kas katalizē oksidēšanās-reducēšanās reakciju."
        ),
        note_en="Keep.",
        source_ids=("LEC",),
        status="apstiprināts",
    ),
    Term(
        id="amfotera",
        preferred="amfotēriska viela (redokss)",
        forbidden=("amfotērisks pāris", "amfoterisks pāris"),
        definition="Viela, kas dažādās reakcijās var būt gan oksidētājs, gan reducētājs. Nav skābes-bāzes amfotērija.",
        example="H₂O₂, SO₃²⁻, NO₂⁻, MnO₂",
        source="LEC P147–P170; §E; Task 04",
        decision_lv=(
            "Redoksa gadījumā lietojam apzīmējumus „viela” un „abējādas lomas”; "
            "oksidēšanās-reducēšanās pāri sauc par sistēmu, nevis par šo lomu."
        ),
        note_en=(
            "Use viela / abējādas lomas; an Ox/Red couple is a sistēma, not this role label."
        ),
        source_ids=("LEC",),
        status="apstiprināts",
        search_extra="abējādas amfotēra",
    ),
    Term(
        id="mora",
        preferred="Mora sāls / Mora pipete",
        forbidden=(),
        definition="Kursa latviešu nosaukumi; personas vārds Mohr minēts vienreiz.",
        example="FeSO₄·(NH₄)₂SO₄·6H₂O",
        source="L25; D6; §E",
        decision_lv=(
            "Kursa tekstā paliek „Mora sāls” (vīrišu dzimme) un „Mora pipete” (sievišu "
            "dzimme); personas vārds Mohr tiek minēts vienu reizi."
        ),
        note_en=(
            "Keep Mora in running text. Portal 2026-11-09: “Mora sāls” is approved "
            "(Pētersona 1922 dictionary); “Mora pipete” is ambiguous — D6 (volume of the "
            "course pipette) stays open, so the status is jāpārbauda."
        ),
        source_ids=("LEC", "L25", "TERMI"),
        status="jāpārbauda",
        search_extra="Mohr",
    ),
    Term(
        id="faradejs",
        preferred="Faradeja konstante F",
        forbidden=(),
        definition="F ≈ 96 485 C/mol (avots bieži noapaļo līdz 96 500).",
        example="ΔG° = −zFΔE°",
        source="LEC P041; §E",
        decision_lv=(
            "Lekcijā lietota forma „Faradeja konstante”; tā ir apstiprināta Latvijas "
            "terminoloģijā, un tajā pašā ierakstā pieļaujama arī „Faradeja skaitlis”."
        ),
        note_en=(
            "Wording Faradeja konstante; verify vs termini.lv when available. Portal "
            "2026-11-09: approved in B. Rolovs, Par fiziku un fiziķiem (1989), where "
            "“Faradeja skaitlis” is an equally approved synonym; LEC P041 writes "
            "“Faradeja skaitlis”."
        ),
        source_ids=("LEC", "TERMI"),
        status="apstiprināts",
        kind="symbol",
        search_extra="Faradeja skaitlis",
    ),
]
TERM_BY_ID = {t.id: t for t in TERMS}

# Source id owned by the workspace itself; it is internal evidence only and can
# never carry an "apstiprināts" status on its own.
INTERNAL_SOURCE_IDS = frozenset({"QA"})


def known_source_ids() -> set[str]:
    """The interim source-id vocabulary owned by tools/master_data.py (T01)."""
    try:
        import master_data  # tools/ is on sys.path for every caller
    except Exception:  # pragma: no cover - vocabulary unavailable
        return set()
    return set(master_data.SOURCE_IDS)


def validate() -> list[str]:
    """Schema check for the termbase. Returns one string per problem.

    Rules (T02.1.1):
      * every term keeps a stable id, a preferred form, a definition, a source
        line, a Latvian student-facing decision and a maintainer note;
      * the student-facing decision must actually contain Latvian letters;
      * the status must be one of the three allowed values;
      * every term names at least one source id from the SOURCE_IDS vocabulary;
      * "apstiprināts" needs at least one source id that is not internal QA.
    """
    problems: list[str] = []
    known = known_source_ids()
    seen: set[str] = set()
    for term in TERMS:
        tid = term.id or "<empty id>"
        if term.id in seen:
            problems.append(f"{tid}: duplicate term id")
        seen.add(term.id)
        if not term.preferred.strip():
            problems.append(f"{tid}: preferred form is empty")
        if not term.definition.strip():
            problems.append(f"{tid}: definition is empty")
        if not term.source.strip():
            problems.append(f"{tid}: source line is empty")
        if not term.decision_lv.strip():
            problems.append(f"{tid}: decision_lv is empty")
        elif not any(ch in LATVIAN_MARKERS for ch in term.decision_lv):
            problems.append(f"{tid}: decision_lv contains no Latvian letters")
        if not term.note_en.strip():
            problems.append(f"{tid}: note_en is empty")
        if term.status not in VALID_STATUSES:
            problems.append(f"{tid}: unknown status {term.status!r}")
        if not term.source_ids:
            problems.append(f"{tid}: source_ids is empty")
        for sid in term.source_ids:
            if known and sid not in known:
                problems.append(f"{tid}: source id {sid!r} is not in SOURCE_IDS")
        if term.status == "apstiprināts" and not (
            set(term.source_ids) - INTERNAL_SOURCE_IDS
        ):
            problems.append(f"{tid}: apstiprināts without an external source id")
    return problems


def coverage() -> dict[str, int]:
    """Counts used by the term report and by the QA notes."""
    counts: dict[str, int] = {"terms": len(TERMS)}
    for term in TERMS:
        counts[term.status] = counts.get(term.status, 0) + 1
        for sid in term.source_ids:
            counts[f"src:{sid}"] = counts.get(f"src:{sid}", 0) + 1
    counts["gate_rows"] = len(GATE_ROWS)
    counts["species"] = len(SPECIES)
    counts["contrasts"] = len(CONTRASTS)
    counts["usage_rows"] = len(USAGE)
    counts["glossary_rows"] = len(GLOSSARY)
    return counts

# Forbidden forms that the grep gate scans for (union of Term.forbidden + curated).
# Deduplicated by forbidden string; first preferred wins.
_GATE_EXTRA: list[tuple[str, str, str]] = [
    ("pusrekcija", "pusreakcija", "pusreakcija"),
    ("pusrekcijas", "pusreakcijas", "pusreakcija"),
    ("oksidēšanās pakāpes", "oksidēšanas pakāpes", "oksidēšanas_pakāpe"),
    ("amfotēriskā pāra", "amfotēriska viela", "amfotera"),
    ("sedimentācijas metode", "nogulsnēšanas titrēšana", "nogulsnēšana"),
]
_gate_seen: set[str] = set()
GATE_ROWS: list[tuple[str, str, str]] = []
for _t in TERMS:
    for _f in _t.forbidden:
        key = _f.strip()
        if key and key not in _gate_seen:
            _gate_seen.add(key)
            GATE_ROWS.append((key, _t.preferred, _t.id))
for _f, _p, _i in _GATE_EXTRA:
    if _f not in _gate_seen:
        _gate_seen.add(_f)
        GATE_ROWS.append((_f, _p, _i))

# ---------------------------------------------------------------- species rail
SPECIES: list[Species] = [
    Species("s2", "sulfīds", "S²⁻", "−2", "sērs zemākajā pakāpē; skābē H₂S", "nejaukt ar sulfītu", "so3"),
    Species("so3", "sulfīts", "SO₃²⁻", "+4", "skābē galvenokārt HSO₃⁻/SO₂·H₂O", "S⁴⁺ kā jons", "so4"),
    Species("so4", "sulfāts", "SO₄²⁻", "+6", "sēra augstākā pakāpe", "S⁶⁺ kā jons", "so3"),
    Species("no2", "nitrīts", "NO₂⁻", "+3", "skābē HONO/NO₂ forma", "N³⁺ kā jons", "no3"),
    Species("no3", "nitrāts", "NO₃⁻", "+5", "slāpekļa augstākā pakāpe", "N⁵⁺ kā jons", "no2"),
    Species("mno42", "manganāts", "MnO₄²⁻", "+6", "zaļš; bāziskā vidē", "Mn⁶⁺ kā jons", "mno4"),
    Species("mno4", "permanganāts", "MnO₄⁻", "+7", "violets; skābā → Mn²⁺", "Mn⁷⁺ kā jons", "mno42"),
    Species("cro4", "hromāts", "CrO₄²⁻", "+6", "dzeltenīgs; bāziskā vidē", "Cr⁶⁺ kā jons", "cr2o7"),
    Species("cr2o7", "dihromāts", "Cr₂O₇²⁻", "+6", "oranžs; skābā vidē", "Cr⁶⁺ kā jons", "cro4"),
    Species("s2o3", "tiosulfāts", "S₂O₃²⁻", "+2 (vidēji)", "reducētājs; produkts S₄O₆²⁻", "S²⁺ kā jons", "s4o6"),
    Species("s4o6", "tetrationāts", "S₄O₆²⁻", "+2,5 (vidēji)", "tiosulfāta oksidēšanās produkts", "—", "s2o3"),
    Species("mno2", "mangāna(IV) oksīds", "MnO₂", "+4", "brūns; neitrālā vidē", "Mn⁴⁺ kā jons", ""),
]

# ---------------------------------------------------------------- contrast pairs
CONTRASTS: list[Contrast] = [
    Contrast("mn", "manganāts", "MnO₄²⁻", "permanganāts", "MnO₄⁻",
             "Zaļš Mn(VI) pret violetu Mn(VII); bāze pret skābi.", "LEC P096–P098; L21"),
    Contrast("cr", "hromāts", "CrO₄²⁻", "dihromāts", "Cr₂O₇²⁻",
             "Abi Cr(+6); vide maina formu, nevis pakāpi.", "LEC; §E"),
    Contrast("s", "sulfīts", "SO₃²⁻", "sulfāts", "SO₄²⁻",
             "S(+4) pret S(+6); sulfīts ir tipisks reducētājs.", "LEC P147"),
    Contrast("n", "nitrīts", "NO₂⁻", "nitrāts", "NO₃⁻",
             "N(+3) pret N(+5); nitrīts var būt abējāds.", "LEC P158–P170"),
    Contrast("thio", "tiosulfāts", "S₂O₃²⁻", "tetrationāts", "S₄O₆²⁻",
             "Jodometrijā I₂ oksidē S₂O₃²⁻ līdz S₄O₆²⁻.", "LEC P250; A8"),
    Contrast("iodo", "jodometrija", "titrants Na₂S₂O₃", "jodimetrija", "titrants I₂",
             "Abi termini ir pareizi; atšķiras titrants un shēma.", "A8"),
]

# ---------------------------------------------------------------- usage (lietot / nelietot)
# Derived view for chapter 11.4 — one row per contested spelling.
USAGE: list[tuple[str, str, str, str]] = [
    ("oksidēšanās", "process, kurā viela atdod elektronus",
     "oksidēšanās pakāpe", "Pakāpei lieto “oksidēšanas pakāpe”; oksidēšanās ir process."),
    ("oksidēšanas pakāpe", "formāls elektronu uzskaites skaitlis",
     "oksidēšanās pakāpe", "Viena rakstība visā dokumentā (T1)."),
    ("oksidēšana", "oksidētāja darbība pret citu vielu",
     "—", "Nav aizliegta; nozīme atšķiras no oksidēšanās."),
    ("ekvivalences punkts", "teorētiskais n₁z₁ = n₂z₂ punkts",
     "beigu punkts (kā sinonīms)", "Beigu punkts ir novērojums (A10)."),
    ("jodometrija", "I₂ izdalīšana; titrants Na₂S₂O₃",
     "jodimetrija (kā sinonīms)", "Abi termini pastāv; tos nedrīkst jaukt (A8)."),
    ("jodimetrija", "titrants ir I₂",
     "jodometrija (kā sinonīms)", "Skat. iepriekšējo rindu."),
    ("nogulsnēšanas titrēšana", "titrēšana ar nogulsnēm",
     "sedimentācija", "Sedimentācija ir gravitācijas nosēdēšanās (A9)."),
    ("analīts", "nosakāmā viela kolbā",
     "analīze (parauga nozīmē)", "Analīze ir process (T2)."),
    ("ATF", "adenozīntrifosfāts",
     "ATP (visā tekstā)", "Latviešu ATF; angļu saīsinājums tikai iekavās vienreiz (T4)."),
    ("ADF", "adenozīndifosfāts",
     "ADP (visā tekstā)", "Latviešu ADF; angļu saīsinājums tikai iekavās vienreiz."),
    ("molārā koncentrācija", "c(X), mol/L",
     "normālā koncentrācija (kā noklusējums)", "Normālo rāda tikai, ja uzdevums to prasa (A18)."),
    ("Mora sāls / Mora pipete", "kursa nosaukumi",
     "—", "Personas vārds Mohr minēts vienreiz; tekstā paliek Mora."),
    ("enzīms (ferments)", "bioloģiskais katalizators",
     "ferments (kā vienīgā forma)", "Ferments iekavās vienreiz."),
    ("H⁺ (aq)", "ūdeņraža jons ūdenī",
     "H₃O⁺ (vienmēr)", "H₃O⁺ tikai tad, ja ūdens molekulas tiek skaitītas."),
    ("amfotēriska viela (redokss)", "var būt oksidētājs un reducētājs",
     "amfotērisks pāris", "Pāris ir Ox/Red sistēma; viela ir loma (Task 04)."),
    ("standarta ūdeņraža elektrods (SHE)", "atskaites elektrods",
     "SHE pāris", "SHE ir elektrods, nevis pāris."),
    ("pusreakcija", "pusreakcija ar -reakcija",
     "pusrekcija", "Drukas kļūda avotā (C2)."),
]

# ---------------------------------------------------------------- glossary view (ch 11.1)
# Compact teaching rows; avoid-column shows the wrong form only.
GLOSSARY: list[tuple[str, str, str, str, str]] = [
    (t.preferred, t.definition, t.example or t.formula, t.source,
     (", ".join(t.forbidden) if t.forbidden else "—"))
    for t in TERMS
    if t.kind in ("term", "process", "method", "symbol")
    and t.id not in ("oksidēšana", "analīze", "normalitate", "adf")  # covered via related rows / usage
]

# Keep a stable short glossary closer to the previous teaching set + new rows.
GLOSSARY = [
    ("Oksidēšanās", TERMS[0].definition, TERMS[0].example, TERMS[0].source,
     "nejaukt ar oksidēšanu kā oksidētāja darbību"),
    ("Reducēšanās", "Elektronu pieņemšana; elementa oksidēšanas pakāpe pazeminās.",
     "MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O", "LEC P014", "nav “reducēšana” ar vienu s"),
    ("Oksidētājs", TERM_BY_ID["oksidētājs"].definition, TERM_BY_ID["oksidētājs"].example,
     TERM_BY_ID["oksidētājs"].source, "nav tas, kas oksidējas"),
    ("Reducētājs", TERM_BY_ID["reducētājs"].definition, TERM_BY_ID["reducētājs"].example,
     TERM_BY_ID["reducētājs"].source, "nav tas, kas reducējas"),
    ("Oks/red sistēma", TERM_BY_ID["oks_red"].definition, TERM_BY_ID["oks_red"].example,
     TERM_BY_ID["oks_red"].source, "nevis “SHE pāris”"),
    ("Oksidēšanas pakāpe", TERM_BY_ID["oksidēšanas_pakāpe"].definition,
     TERM_BY_ID["oksidēšanas_pakāpe"].example, TERM_BY_ID["oksidēšanas_pakāpe"].source,
     "oksidēšanās pakāpe"),
    ("Pusreakcija", TERM_BY_ID["pusreakcija"].definition, TERM_BY_ID["pusreakcija"].example,
     TERM_BY_ID["pusreakcija"].source, "pusrekcija"),
    ("Standartpotenciāls E°", TERM_BY_ID["standartpotenciāls"].definition,
     TERM_BY_ID["standartpotenciāls"].example, TERM_BY_ID["standartpotenciāls"].source,
     "nav E°′ (pH 7); nav faktiskais E"),
    ("Potenciāls E", TERM_BY_ID["potencials_E"].definition, TERM_BY_ID["potencials_E"].example,
     TERM_BY_ID["potencials_E"].source, "nejaukt ar E° vai E°′"),
    ("E°′", TERM_BY_ID["e_prime"].definition, TERM_BY_ID["e_prime"].example,
     TERM_BY_ID["e_prime"].source, "nejaukt ar E°"),
    ("Elektrodzinējspēks (EDS)", TERM_BY_ID["eds"].definition, TERM_BY_ID["eds"].example,
     TERM_BY_ID["eds"].source, "nav potenciālu summa"),
    ("Standarta ūdeņraža elektrods (SHE)", TERM_BY_ID["she"].definition,
     TERM_BY_ID["she"].example, TERM_BY_ID["she"].source, "SHE pāris"),
    ("Ekvivalences punkts", TERM_BY_ID["ekvivalences_punkts"].definition,
     TERM_BY_ID["ekvivalences_punkts"].example, TERM_BY_ID["ekvivalences_punkts"].source,
     "nav novērojamā krāsa"),
    ("Titrēšanas beigu punkts", TERM_BY_ID["beigu_punkts"].definition,
     TERM_BY_ID["beigu_punkts"].example, TERM_BY_ID["beigu_punkts"].source,
     "nav tas pats, kas ekvivalences punkts"),
    ("Titrants", TERM_BY_ID["titrants"].definition, TERM_BY_ID["titrants"].example,
     TERM_BY_ID["titrants"].source, "nav analīts"),
    ("Analīts", TERM_BY_ID["analīts"].definition, TERM_BY_ID["analīts"].example,
     TERM_BY_ID["analīts"].source, "analīze (parauga nozīmē)"),
    ("Ekvivalences skaitlis z", TERM_BY_ID["z"].definition, TERM_BY_ID["z"].example,
     TERM_BY_ID["z"].source, "nav vielas daudzums n"),
    ("Permanganatometrija", TERM_BY_ID["permanganatometrija"].definition,
     TERM_BY_ID["permanganatometrija"].example, TERM_BY_ID["permanganatometrija"].source,
     "nevis jodometrija"),
    ("Jodometrija", TERM_BY_ID["jodometrija"].definition, TERM_BY_ID["jodometrija"].example,
     TERM_BY_ID["jodometrija"].source, "nejaukt ar jodimetriju"),
    ("Jodimetrija", TERM_BY_ID["jodimetrija"].definition, TERM_BY_ID["jodimetrija"].example,
     TERM_BY_ID["jodimetrija"].source, "nejaukt ar jodometriju"),
    ("Nogulsnēšanas titrēšana", TERM_BY_ID["nogulsnēšana"].definition,
     TERM_BY_ID["nogulsnēšana"].example, TERM_BY_ID["nogulsnēšana"].source,
     "sedimentācija"),
    ("ATF", "Adenozīntrifosfāts; angļu saīsinājums iekavās vienreiz.",
     "ADF + Pᵢ → ATF", TERM_BY_ID["atf"].source, "ATP (visā tekstā)"),
    ("Amfotēriska viela (redokss)", TERM_BY_ID["amfotera"].definition,
     TERM_BY_ID["amfotera"].example, TERM_BY_ID["amfotera"].source,
     "amfotērisks pāris"),
    ("Enzīms (ferments)", TERM_BY_ID["enzīms"].definition, TERM_BY_ID["enzīms"].example,
     TERM_BY_ID["enzīms"].source, "tikai “ferments” bez paskaidrojuma"),
    ("Oksidoreduktāze", TERM_BY_ID["oksidoreduktāze"].definition,
     TERM_BY_ID["oksidoreduktāze"].example, TERM_BY_ID["oksidoreduktāze"].source, "—"),
]


def species_as_tuples() -> list[tuple[str, str, str, str, str]]:
    """Legacy (name, formula, ox, note, wrong) shape for older call sites."""
    out = []
    for s in SPECIES:
        wrong = "—" if s.confusion in ("—", "") else s.confusion
        # Prefer charge-as-OS wrong forms where the note historically had [[w:...]]
        legacy_wrong = {
            "sulfīts": "[[w:S^4+]]",
            "sulfāts": "[[w:S^6+]]",
            "nitrīts": "[[w:N^3+]]",
            "nitrāts": "[[w:N^5+]]",
            "manganāts": "[[w:Mn^6+]]",
            "permanganāts": "[[w:Mn^7+]]",
            "hromāts": "[[w:Cr^6+]]",
            "dihromāts": "[[w:Cr^6+]]",
            "tiosulfāts": "[[w:S^2+]]",
            "mangāna(IV) oksīds": "[[w:Mn^4+]]",
        }.get(s.name, wrong if wrong != "—" else "—")
        out.append((s.name, s.formula, s.ox, s.note, legacy_wrong))
    return out


def json_blob() -> dict:
    """Data for the offline glossary search / term cards."""
    return {
        "terms": [
            {
                "id": t.id,
                "preferred": t.preferred,
                "forbidden": list(t.forbidden),
                "definition": t.definition,
                "example": t.example,
                "source": t.source,
                "status": t.status,
                "kind": t.kind,
                "search": " ".join(
                    [t.preferred, t.definition, t.example, t.formula, t.search_extra,
                     " ".join(t.forbidden)]
                ).lower(),
                "chapter": t.chapter,
            }
            for t in TERMS
        ],
        "species": [
            {
                "id": s.id,
                "name": s.name,
                "formula": s.formula,
                "ox": s.ox,
                "note": s.note,
                "confusion": s.confusion,
                "pair_with": s.pair_with,
                "search": f"{s.name} {s.formula} {s.ox} {s.confusion}".lower(),
            }
            for s in SPECIES
        ],
        "contrasts": [
            {
                "id": c.id,
                "left": c.left,
                "left_formula": c.left_formula,
                "right": c.right,
                "right_formula": c.right_formula,
                "cue": c.cue,
                "search": f"{c.left} {c.right} {c.left_formula} {c.right_formula}".lower(),
            }
            for c in CONTRASTS
        ],
    }
