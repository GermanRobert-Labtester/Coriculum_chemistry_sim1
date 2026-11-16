# -*- coding: utf-8 -*-
"""Claim-level warrant ledger for high-risk numbers (T02) and claim-source
ID / bibliography interface (T09).

Offline and deterministic. URLs live on support records and in
claims_notes.md. appendix_html() and bibliography_html() never print a
scheme, and the builder does not read the notes file. Arithmetic already
recomputed by check_numbers.py is not registered here.

A claim is accepted only when its status is verified, its single support
is TEXT-VERIFIED, the compare value matches, and every constrained regime
axis matches. Anything else renders as [UNVERIFIED]. revise_value() does
not change a number until a domain editor is named.

Locator grammar (exact forms; see LOCATOR_RE / parse_locator):
  [A p.N] [A p.N–M]  notes page
  [D p.N]            theory page
  [C] / [C p.N]      descriptor (usually whole file)
  [E s.N] [E s.N–M]  slide number
  [B #N]             seminar problem
  C-NN / C-NN-X      claim registry id (bare or [C-NN])
  S-TOKEN            external support id (e.g. S-BIPM)
Combined course locators may list several with commas inside one span.src.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = pathlib.Path(__file__).resolve().parent / "claims_notes.md"
MASTER = ROOT / "Master_temats_1_skidumi_un_kimiskas_reakcijas.html"

# T09: machine-checkable course locator atoms.
LOCATOR_ATOM = (
    r"(?:[AD]\s*p\.\s*\d+(?:–\d+)?"
    r"|C(?:\s*p\.\s*\d+(?:–\d+)?)?"
    r"|E\s*s\.\s*\d+(?:–\d+)?"
    r"|B\s*#\s*\d+)"
)
LOCATOR_RE = re.compile(
    r"\[" + LOCATOR_ATOM + r"(?:\s*,\s*" + LOCATOR_ATOM + r")*" + r"\]"
)
CLAIM_ID_RE = re.compile(r"\bC-\d+(?:-[A-Za-z0-9]+)?\b")
SUPPORT_ID_RE = re.compile(r"\bS-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
ERRATA_PAREN_RE = re.compile(r"\(E\d{2}\)")

REGIME_KEYS = (
    "phase", "temperature", "pressure", "ionic_strength", "specimen", "population",
)
NB = "\u202f"
DEFINED = "definēta konstante"

# Consequence of misuse, and which regime axes make the same digits a
# different claim. standard-constant stays bounded only when every axis is
# the defining-constant token.
DOMAIN_RISK = {
    "clinical": ("high", "a patient limit can be read from the wrong specimen or population"),
    "thermodynamic": ("high", "the energy changes when the water phase or standard state changes"),
    "electrochemical": ("high", "the potential changes with temperature, phase and the standard state"),
    "equilibrium": ("high", "neutrality and Kw change with temperature and the medium"),
    "standard-constant": ("bounded", "a defining constant is not a measured sample"),
}


def classify_risk(domain, regime):
    level, _why = DOMAIN_RISK[domain]
    if domain == "standard-constant":
        if all(regime.get(k) == DEFINED for k in REGIME_KEYS):
            return "bounded"
        return "high"
    return level


def regimes_match(claim_regime, support_regime):
    """A constrained axis fails when the support is missing or different.
    An empty axis does not fail."""
    for key in REGIME_KEYS:
        wanted = claim_regime.get(key)
        if wanted in (None, ""):
            continue
        if support_regime.get(key) != wanted:
            return False
    return True


def _regime(**kw):
    row = {k: None for k in REGIME_KEYS}
    row.update(kw)
    return row


SUPPORTS = {}


def _support(sid, title, version, url, status, regime, compare_value, note):
    SUPPORTS[sid] = {
        "id": sid,
        "title": title,
        "version": version,
        "url": url,
        "status": status,
        "regime": regime,
        "compare_value": compare_value,
        "note": note,
    }


_support(
    "S-BIPM",
    "BIPM SI Brochure",
    "9. izdevums, 2026. gada atjauninājums; statuss pārnests no AGENTS.md §9, šajā piegājienā brošūra nav lejupielādēta no jauna",
    "https://www.bipm.org/en/si-brochure-9",
    "TEXT-VERIFIED",
    _regime(**{k: DEFINED for k in REGIME_KEYS}),
    "6.02214076e23",
    "Warrants only the exact defining constant of the mole.",
)
_support(
    "S-CIAAW",
    "IUPAC/CIAAW Standard Atomic Weights 2024",
    "2024 tabula; statuss pārnests no AGENTS.md §9, šajā piegājienā lapa nav lejupielādēta no jauna",
    "https://www.ciaaw.org/atomic-weights.htm",
    "TEXT-VERIFIED",
    _regime(**{k: DEFINED for k in REGIME_KEYS}),
    "atomic-weights-2024",
    "Warrants current standard atomic weights for normal materials; not a course page locator.",
)
_support(
    "S-IUPAC-GB",
    "IUPAC Gold Book",
    "v5.0.0 (2025) kandidāts; tiešais fetch HTTP 403 – šajā piegājienā ieraksti nav nolasīti",
    "https://goldbook.iupac.org/",
    "UNVERIFIED",
    _regime(**{k: DEFINED for k in REGIME_KEYS}),
    "goldbook-unverified",
    "Candidate definitions only; do not cite as TEXT-VERIFIED.",
)

# Course PDF metadata for the generated bibliography. Pages/slides come from
# SOURCE_LEDGER.md header; never invent edition, ISBN or DOI here.
COURSE_SOURCES = (
    {
        "id": "C",
        "file": "1_Temata apraksts 2020.pdf",
        "kind": "temata apraksts",
        "extent": "1 lpp.",
        "role": "nosaka, ko pārbauda",
        "status": "METADATA-VERIFIED / SCOPE-ALIGNED",
        "note": "Teksts šajā piegājienā nav pārlasīts no jauna.",
    },
    {
        "id": "D",
        "file": "I_temats_TEORIJA_Final_m.pdf",
        "kind": "teorija",
        "extent": "21 lpp.",
        "role": "pilnākais teksts, medicīnas konteksts",
        "status": "METADATA-VERIFIED / SCOPE-ALIGNED",
        "note": "Lapas citē kā [D p.N].",
    },
    {
        "id": "A",
        "file": "1_Neorganiskā ķīmija konspekts atkārtošanai_2024.pdf",
        "kind": "konspekts",
        "extent": "16 lpp.",
        "role": "blīvākais kopsavilkums, lielākā daļa formulu",
        "status": "METADATA-VERIFIED / SCOPE-ALIGNED",
        "note": "Lapas citē kā [A p.N].",
    },
    {
        "id": "E",
        "file": "Kimija_viss-2024 - Prezentacija.pdf",
        "kind": "prezentācija",
        "extent": "58 slaidi",
        "role": "attēli, periodiskā tabula, potenciāli",
        "status": "METADATA-VERIFIED / SCOPE-ALIGNED",
        "note": "Slaidus citē kā [E s.N].",
    },
    {
        "id": "B",
        "file": "1_SEM_MCh_LV_Skid_un_reakcijas_2025.pdf",
        "kind": "seminārs",
        "extent": "15 uzdevumi",
        "role": "praktiskās prasmes",
        "status": "METADATA-VERIFIED / SCOPE-ALIGNED",
        "note": "Faila vārds 2025; kājenē …_2021 (E61). Uzdevumus citē kā [B #N].",
    },
)

# External reading list: only rows with known AGENTS §9 provenance.
# URL is stored for notes/support; bibliography_html prints it as plain text
# without a scheme so check_network stays zero.
EXTERNAL_SOURCES = (
    {
        "support_id": "S-BIPM",
        "supports": "Mola definīcija un SI vienību fiksētās konstantes (C-01).",
    },
    {
        "support_id": "S-CIAAW",
        "supports": "Standarta atommasas; Gd, Lu, Zr 2024 pārskatījumi.",
    },
    {
        "support_id": "S-IUPAC-GB",
        "supports": "Kandidātu definīcijas (elektrolīts, oksidēšanas pakāpe, hidrolīze, REN) – [UNVERIFIED].",
    },
)

_UNREAD = "Primārais avots šajā piegājienā nav nolasīts."

_support(
    "S-EQ-25", "līdzsvara tabula nav nolasīta", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="H₂O(l)", temperature="25" + NB + "°C", pressure="100" + NB + "kPa",
            ionic_strength="idealizēts atšķaidījums", specimen="tīrs ūdens",
            population="nav attiecināms"),
    "1.0e-14", _UNREAD,
)
_support(
    "S-EQ-37", "līdzsvara tabula nav nolasīta", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="H₂O(l)", temperature="37" + NB + "°C", pressure="100" + NB + "kPa",
            ionic_strength="idealizēts atšķaidījums", specimen="tīrs ūdens",
            population="nav attiecināms"),
    "2.4e-14", _UNREAD,
)
_support(
    "S-TH-L", "termokīmijas tabula nav nolasīta", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="H₂O(l)", temperature="25" + NB + "°C", pressure="100" + NB + "kPa",
            ionic_strength="nav attiecināms", specimen="tīra viela",
            population="nav attiecināms"),
    "2220", _UNREAD,
)
_support(
    "S-TH-G", "termokīmijas tabula nav nolasīta", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="H₂O(g)", temperature="25" + NB + "°C", pressure="100" + NB + "kPa",
            ionic_strength="nav attiecināms", specimen="tīra viela",
            population="nav attiecināms"),
    "2043", _UNREAD,
)
_support(
    "S-EL", "elektrodu tabula nav nolasīta", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="ūdens šķīdums", temperature="25" + NB + "°C", pressure="100" + NB + "kPa",
            ionic_strength="standartstāvoklis", specimen="elektrods",
            population="nav attiecināms"),
    "1.229", _UNREAD,
)
_support(
    "S-ART", "klīnisks asins gāzu avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="asinis", temperature="ķermeņa temperatūra", pressure="ķermeņa apstākļi",
            ionic_strength="fizioloģisks", specimen="arteriālās asinis",
            population="nav noteikta"),
    "7.35-7.45", _UNREAD,
)
_support(
    "S-VEN", "klīnisks asins gāzu avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="asinis", temperature="ķermeņa temperatūra", pressure="ķermeņa apstākļi",
            ionic_strength="fizioloģisks", specimen="venozās asinis",
            population="nav noteikta"),
    "7.32-7.45", _UNREAD,
)
_support(
    "S-GAS", "klīnisks asins gāzu avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="asinis", temperature="ķermeņa temperatūra", pressure="ķermeņa apstākļi",
            ionic_strength="fizioloģisks", specimen="arteriālās asinis",
            population="nav noteikta"),
    "O2-CO2", _UNREAD,
)
_support(
    "S-TEMP", "klīnisks temperatūras avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="ķermenis", temperature="36,1–37,5" + NB + "°C", pressure="ķermeņa apstākļi",
            ionic_strength="nav attiecināms", specimen="kodols",
            population="nav noteikta"),
    "36.1-37.5", _UNREAD,
)
_support(
    "S-NA", "klīnisks seruma avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="serums", temperature="nav noteikta", pressure="nav noteikts",
            ionic_strength="nav noteikts", specimen="serums",
            population="pieaugušie"),
    "135-150", _UNREAD,
)
_support(
    "S-URINE", "klīnisks urīna avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="urīns", temperature="nav noteikta", pressure="nav noteikts",
            ionic_strength="nav noteikts", specimen="diennakts urīns",
            population="nav noteikta"),
    "54-150", _UNREAD,
)
_support(
    "S-TBW", "fizioloģijas avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="ķermenis", temperature="nav attiecināms", pressure="nav attiecināms",
            ionic_strength="nav attiecināms", specimen="ķermenis",
            population="pieaugušie"),
    "50-60", _UNREAD,
)
_support(
    "S-FUEL", "uztura avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="uzturs", temperature="nav attiecināms", pressure="nav attiecināms",
            ionic_strength="nav attiecināms", specimen="uzturs",
            population="vadlīniju diapazons"),
    "55-60", _UNREAD,
)
_support(
    "S-KREBS", "bioķīmijas avots nav nolasīts", "nav versijas", "",
    "UNVERIFIED",
    _regime(phase="šūna", temperature="ķermeņa temperatūra", pressure="ķermeņa apstākļi",
            ionic_strength="fizioloģisks", specimen="mitohondrijs",
            population="nav attiecināms"),
    "NADH-FADH2-GTP", _UNREAD,
)

CLAIMS = {}


def _claim(**kw):
    row = {
        "editor": None,
        "may_replace_value": False,
        "ledger_ids": (),
        "surfaces": (),
    }
    row.update(kw)
    row["risk"] = classify_risk(row["domain"], row["regime"])
    CLAIMS[row["id"]] = row


_claim(
    id="C-01",
    domain="standard-constant",
    source_file="AGENTS.md",
    anchor="§9 BIPM",
    exact_wording="Mola definīcijā Avogadro konstante ir tieši 6,02214076·10²³ mol⁻¹.",
    value_display="6,02214076·10²³" + NB + "mol⁻¹",
    compare_value="6.02214076e23",
    unit="mol⁻¹",
    conditions="Definējoša SI konstante, nevis mērījums paraugā.",
    regime=_regime(**{k: DEFINED for k in REGIME_KEYS}),
    support_id="S-BIPM",
    status="verified",
    confidence="high",
    accepted_phrasing="Avogadro konstante ir tieši 6,02214076·10²³ mol⁻¹ (BIPM SI brošūra, 9. izdevums).",
    ledger_ids=(),
    surfaces=(),
)
_claim(
    id="C-07-25",
    domain="equilibrium",
    source_file="build/content/ch08.html",
    anchor="#ph Kw 25 °C",
    exact_wording="Pie 25 °C Kw ir 1,0·10⁻¹⁴, tāpēc [H⁺] = [OH⁻] = 10⁻⁷ mol/L.",
    value_display="1,0·10⁻¹⁴",
    compare_value="1.0e-14",
    unit="(mol/L)²",
    conditions="Tīrs ūdens, 25 °C, idealizēts atšķaidījums. Nav arteriālās asinis un nav 37 °C.",
    regime=SUPPORTS["S-EQ-25"]["regime"],
    support_id="S-EQ-25",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemērs: Kw pie 25 °C rakstīts 1,0·10⁻¹⁴. Primārā līdzsvara tabula nav nolasīta.",
    ledger_ids=("E29",),
    surfaces=(("build/content/ch08.html", "1,0·10⁻¹⁴"),),
)
_claim(
    id="C-07-37",
    domain="equilibrium",
    source_file="build/content/ch08.html",
    anchor="#ph Kw 37 °C",
    exact_wording="Pie 37 °C Kw ≈ 2,4·10⁻¹⁴, tāpēc neitrāls pH ir ≈ 6,81.",
    value_display="2,4·10⁻¹⁴; pH ≈ 6,81",
    compare_value="2.4e-14",
    unit="(mol/L)²",
    conditions="Tīrs ūdens, 37 °C. 6,81 nav asins pH un nav 25 °C neitralitāte.",
    regime=SUPPORTS["S-EQ-37"]["regime"],
    support_id="S-EQ-37",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemērs: pie 37 °C neitrāls pH rakstīts ≈ 6,81. Primārā līdzsvara tabula nav nolasīta.",
    ledger_ids=("E29",),
    surfaces=(("build/content/ch08.html", "≈ 6,81"),),
)
_claim(
    id="C-11-L",
    domain="thermodynamic",
    source_file="build/content/ch11.html",
    anchor="#reakcijas siltums H2O(l)",
    exact_wording="Aizstājums 2220 ar H₂O(l) un 1367 ar H₂O(l) nav nolasīts no primārās tabulas.",
    value_display="2220" + NB + "kJ/mol (propāns); 1367" + NB + "kJ/mol (etanols)",
    compare_value="2220",
    unit="kJ/mol",
    conditions="Sadegšana, ūdens produkts šķidrs, 25 °C. Tas pats skaitlis gāzes fāzei neder.",
    regime=SUPPORTS["S-TH-L"]["regime"],
    support_id="S-TH-L",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa aizstājums šķidram ūdenim: propāns 2220 un etanols 1367. Primārā termokīmijas tabula nav nolasīta.",
    ledger_ids=("E46",),
    surfaces=(("build/content/ch11.html", "2220 ar H₂O(l)"),),
)
_claim(
    id="C-11-G",
    domain="thermodynamic",
    source_file="build/content/ch11.html",
    anchor="#reakcijas siltums H2O(g)",
    exact_wording="Aizstājums 2043 ar H₂O(g), 1235 ar H₂O(g) un 802 ar H₂O(g) nav nolasīts no primārās tabulas.",
    value_display="2043" + NB + "kJ/mol (propāns); 1235" + NB + "kJ/mol (etanols); 802" + NB + "kJ/mol (metāns)",
    compare_value="2043",
    unit="kJ/mol",
    conditions="Sadegšana, ūdens produkts gāze, 25 °C. 2043 nav šķidrā ūdens rezultāts.",
    regime=SUPPORTS["S-TH-G"]["regime"],
    support_id="S-TH-G",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa aizstājums gāzveida ūdenim: propāns 2043, etanols 1235, metāns 802. Primārā termokīmijas tabula nav nolasīta.",
    ledger_ids=("E46",),
    surfaces=(("build/content/ch11.html", "2043 ar H₂O(g)"),),
)
_claim(
    id="C-11-E",
    domain="electrochemical",
    source_file="build/content/ch12.html",
    anchor="#redoks standartpotenciāls",
    exact_wording="Tabulā rādītie reducēšanās potenciāli, ieskaitot O₂/H₂O +1,229 V, nav nolasīti no primārās elektrodu tabulas.",
    value_display="+1,229" + NB + "V (O₂/H₂O); +1,07" + NB + "V (Br₂); −0,763" + NB + "V (Zn²⁺)",
    compare_value="1.229",
    unit="V",
    conditions="Ūdens šķīdums, 25 °C, standartstāvoklis. Cita fāze vai cita temperatūra ir cits apgalvojums.",
    regime=SUPPORTS["S-EL"]["regime"],
    support_id="S-EL",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemēri voltos paliek tabulā. Tie nav apstiprināti elektrodu potenciāli.",
    ledger_ids=("E47",),
    surfaces=(("build/content/ch12.html", "primārās elektrodu tabulas"),),
)
_claim(
    id="C-12-A",
    domain="clinical",
    source_file="build/content/ch08.html",
    anchor="#ph asins pH",
    exact_wording="Kursā paturētais arteriālo asiņu piemērs ir 7,35–7,45.",
    value_display="7,35–7,45",
    compare_value="7.35-7.45",
    unit="pH",
    conditions="Piemērs arteriālajām asinīm. Nav venozais intervāls un nav apstiprināts klīniskais slieksnis.",
    regime=SUPPORTS["S-ART"]["regime"],
    support_id="S-ART",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemērs arteriālajām asinīm: 7,35–7,45. Tas nav apstiprināts klīniskais intervāls, un avots [D p.2] šo intervālu neraksta.",
    ledger_ids=("E48",),
    surfaces=(
        ("build/content/ch08.html", "7,35–7,45"),
        ("build/content/ch01.html", "asins pH 7,4 nav"),
    ),
)
_claim(
    id="C-12-V",
    domain="clinical",
    source_file="build/content/ch08.html",
    anchor="#ph avota pH",
    exact_wording="Avots raksta pH 7,32–7,45 un sauc 7,4 par neitrālu vidi.",
    value_display="7,32–7,45",
    compare_value="7.32-7.45",
    unit="pH",
    conditions="Avota rindkopa. Nedrīkst pārcelt uz arteriālo asiņu režīmu.",
    regime=SUPPORTS["S-VEN"]["regime"],
    support_id="S-VEN",
    status="unverified",
    confidence="low",
    accepted_phrasing="Avots saka 7,32–7,45. Šis skaitlis nav pieņemts kā arteriālais intervāls.",
    ledger_ids=("E48",),
    surfaces=(("build/content/ch08.html", "7,32–7,45"),),
)
_claim(
    id="C-12-G",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms regulējamās gāzes",
    exact_wording="Stabilizējamie parametri ir O₂ un CO₂; slāpeklis nav regulējama asins gāze.",
    value_display="O₂ un CO₂, nevis N₂",
    compare_value="O2-CO2",
    unit="",
    conditions="Kvalitatīvs kursa labojums. Gāzu spriegumi skaitļos nav reģistrēti.",
    regime=SUPPORTS["S-GAS"]["regime"],
    support_id="S-GAS",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa labojums: regulē O₂ un CO₂. Primārs klīnisks avots nav nolasīts.",
    ledger_ids=("E49",),
    surfaces=(("build/content/ch14.html", "Slāpeklis asinīs ir izšķīdis"),),
)
_claim(
    id="C-12-T",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms kodola temperatūra",
    exact_wording="Kodola temperatūras kursa piemērs ir ap 36,1–37,5 °C.",
    value_display="36,1–37,5" + NB + "°C",
    compare_value="36.1-37.5",
    unit="°C",
    conditions="Kodols, nevis avota 36,5–38,6 °C. 38,6 °C kursā aprakstīts kā drudzis.",
    regime=SUPPORTS["S-TEMP"]["regime"],
    support_id="S-TEMP",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemērs: kodola temperatūra ap 36,1–37,5 °C. Tas nav apstiprināts klīniskais intervāls.",
    ledger_ids=("E50",),
    surfaces=(("build/content/ch14.html", "36,1–37,5"),),
)
_claim(
    id="C-12-NA",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms nātrija piemērs",
    exact_wording="Na serums 135–150 mmol/L ir laboratorijas piemērs lapā.",
    value_display="135–150" + NB + "mmol/L",
    compare_value="135-150",
    unit="mmol/L",
    conditions="Serums, pieaugušo piemērs. Metode, temperatūra un populācija nav norādīta avotā.",
    regime=SUPPORTS["S-NA"]["regime"],
    support_id="S-NA",
    status="unverified",
    confidence="low",
    accepted_phrasing="Lapas piemērs: Na serums 135–150 mmol/L. Tas nav apstiprināts klīniskais intervāls.",
    ledger_ids=(),
    surfaces=(("build/content/ch14.html", "135–150"),),
)
_claim(
    id="C-12-U",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms urīna nātrijs",
    exact_wording="Avotā urīna nātrijs rakstīts 54–150" + NB + "mmol/L.",
    value_display="54–150" + NB + "mmol/L",
    compare_value="54-150",
    unit="mmol/L",
    conditions="Diennakts urīns. Nav seruma intervāls un nav apstiprināts klīniskais slieksnis.",
    regime=SUPPORTS["S-URINE"]["regime"],
    support_id="S-URINE",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa lapā paturēts avota piemērs 54–150" + NB + "mmol/L urīnam. Tas nav apstiprināts klīniskais intervāls.",
    ledger_ids=(),
    surfaces=(("build/content/ch14.html", "54–150"),),
)
_claim(
    id="C-13-W",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms ūdens daudzums",
    exact_wording="Pieaugušam cilvēkam kopējais ūdens ir ap 50–60 % no ķermeņa masas; ārpusšūnu šķidrums ap 14,5 L.",
    value_display="50–60" + NB + "%; 14,5" + NB + "L",
    compare_value="50-60",
    unit="% masas",
    conditions="Pieaugušie. Vairāk nekā 70 % kursā ir zīdaiņa rādītājs, nevis šī rinda.",
    regime=SUPPORTS["S-TBW"]["regime"],
    support_id="S-TBW",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa piemērs pieaugušajiem: kopējais ūdens ap 50–60 %. Primārs fizioloģijas avots nav nolasīts.",
    ledger_ids=("E51",),
    surfaces=(("build/content/ch14.html", "kopējais ūdens ir ap 50–60"),),
)
_claim(
    id="C-13-F",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms uztura daļas",
    exact_wording="Avotā dotie 55–60 / 20–25 / 15–20 % ir uztura vadlīniju diapazoni, nevis konstantes.",
    value_display="55–60 / 20–25 / 15–20" + NB + "%",
    compare_value="55-60",
    unit="%",
    conditions="Uztura vadlīniju diapazons, nevis organisma konstante. Nukleīnskābes nav kurināmais.",
    regime=SUPPORTS["S-FUEL"]["regime"],
    support_id="S-FUEL",
    status="unverified",
    confidence="low",
    accepted_phrasing="Procenti paliek kā avota diapazons, nevis konstante. Primārs uztura avots nav nolasīts.",
    ledger_ids=("E54",),
    surfaces=(("build/content/ch14.html", "55–60 / 20–25 / 15–20"),),
)
_claim(
    id="C-13-K",
    domain="clinical",
    source_file="build/content/ch14.html",
    anchor="#organisms Krebs",
    exact_wording="Krebsa ciklā rodas NADH, FADH₂ un viens GTP/ATP; lielākā daļa ATP rodas oksidatīvajā fosforilēšanā.",
    value_display="NADH, FADH₂, viens GTP/ATP",
    compare_value="NADH-FADH2-GTP",
    unit="",
    conditions="Tiešie cikla produkti. Lejupējā ATP bilance nav šis apgalvojums.",
    regime=SUPPORTS["S-KREBS"]["regime"],
    support_id="S-KREBS",
    status="unverified",
    confidence="low",
    accepted_phrasing="Kursa formulējums: cikls dod NADH, FADH₂ un vienu GTP/ATP. Primārs bioķīmijas avots nav nolasīts.",
    ledger_ids=("E57",),
    surfaces=(("build/content/ch14.html", "Krebsa ciklā rodas NADH"),),
)

# Phrases that would ship an unqualified correction. Absence is the pass.
FORBIDDEN = (
    ("build/content/ch11.html", "pareizi ir 2043"),
    ("build/content/ch12.html", "Pārbaudītas reducēšanās"),
    ("build/content/ch12.html", "pārbaudītās rindas"),
    ("build/content/ch17.html", "pārbaudītām rindām"),
    ("build/ledger.py", "tikai pārbaudītās"),
)

CLEARED_VERIFIED = ("E29", "E46", "E47", "E48")
SCHEMA = (
    "id", "domain", "risk", "source_file", "anchor", "exact_wording",
    "value_display", "compare_value", "unit", "conditions", "regime",
    "support_id", "status", "confidence", "accepted_phrasing", "ledger_ids",
    "editor", "may_replace_value", "surfaces",
)
NOTES_MARK = "PRIMĀRĀS TABULAS ŠAJĀ PIEGĀJIENĀ NAV ATVĒRTAS"


def accept(claim, supports=None):
    supports = SUPPORTS if supports is None else supports
    if claim.get("status") != "verified":
        return False
    sup = supports.get(claim.get("support_id"))
    if not sup or sup.get("status") != "TEXT-VERIFIED":
        return False
    if claim.get("compare_value") != sup.get("compare_value"):
        return False
    if not regimes_match(claim.get("regime") or {}, sup.get("regime") or {}):
        return False
    return True


def public_status(claim, supports=None):
    if accept(claim, supports):
        return "TEXT-VERIFIED"
    return "[UNVERIFIED]"


def revise_value(claim, new_value):
    """Unsupported numbers stay. A domain editor is not named."""
    if claim.get("editor") and claim.get("may_replace_value") and accept(claim):
        return new_value
    return claim.get("compare_value")


def claims_for_ledger(eid):
    return [c for c in CLAIMS.values() if eid in c.get("ledger_ids", ())]


def citation_label(claim):
    sup = SUPPORTS.get(claim["support_id"])
    if public_status(claim) == "TEXT-VERIFIED" and sup:
        # Version text only. The support URL is not a citation label.
        version = sup["version"].split(";")[0]
        return f'{claim["id"]} · {sup["title"]}, {version}'
    return f'{claim["id"]} · [UNVERIFIED]'


def _cell(text):
    return html.escape(text or "", quote=True)


def _regime_text(regime):
    labels = {
        "phase": "fāze", "temperature": "T", "pressure": "p",
        "ionic_strength": "I", "specimen": "paraugs", "population": "populācija",
    }
    parts = []
    for key in REGIME_KEYS:
        val = regime.get(key)
        if val:
            parts.append(f"{labels[key]} {val}")
    return "; ".join(parts)


def row_html(claim):
    status = public_status(claim)
    sup = SUPPORTS[claim["support_id"]]
    cols = (
        claim["id"],
        claim["domain"],
        claim["risk"],
        claim["exact_wording"],
        claim["value_display"],
        _regime_text(claim["regime"]),
        status,
        claim["confidence"],
        citation_label(claim),
        claim["accepted_phrasing"],
        sup["version"].split(";")[0],
    )
    body = "".join(f"<td>{_cell(c)}</td>" for c in cols[1:])
    return f'<tr><th scope="row">{_cell(cols[0])}</th>{body}</tr>'


def appendix_html():
    rows = [row_html(CLAIMS[cid]) for cid in sorted(CLAIMS)]
    head = (
        "<th scope=\"col\">ID</th><th scope=\"col\">Joma</th><th scope=\"col\">Risks</th>"
        "<th scope=\"col\">Avota vārdi</th><th scope=\"col\">Vērtība</th>"
        "<th scope=\"col\">Režīms</th><th scope=\"col\">Statuss</th>"
        "<th scope=\"col\">Pārliecība</th><th scope=\"col\">Citāts</th>"
        "<th scope=\"col\">Pieņemtais formulējums</th><th scope=\"col\">Avota versija</th>"
    )
    return (
        '<div class="mx-wrap"><table class="data" id="warrant-table">'
        "<caption>Augsta riska skaitļi. [UNVERIFIED] nozīmē, ka primārais avots nav nolasīts "
        "un rinda nav apstiprināta vērtība. Tabula ir statiska un lasāma bez skripta.</caption>"
        f"<thead><tr>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    )


def parse_locator(token):
    """Return ('course'|'claim'|'support'|'errata'|None, normalised) for one token."""
    t = (token or "").strip()
    if not t:
        return None, ""
    if LOCATOR_RE.fullmatch(t) or re.fullmatch(r"\[" + LOCATOR_ATOM + r"\]", t):
        return "course", re.sub(r"\s+", " ", t)
    if CLAIM_ID_RE.fullmatch(t) or (t.startswith("[") and CLAIM_ID_RE.fullmatch(t[1:-1] or "")):
        return "claim", t.strip("[]")
    if SUPPORT_ID_RE.fullmatch(t) or (t.startswith("[") and SUPPORT_ID_RE.fullmatch(t[1:-1] or "")):
        return "support", t.strip("[]")
    if ERRATA_PAREN_RE.fullmatch(t) or re.fullmatch(r"E\d{2}", t):
        return "errata", t.strip("()")
    return None, t


def print_url(url):
    """Printed reference only: host/path without a URI scheme (offline contract)."""
    if not url:
        return "–"
    return re.sub(r"^https?://", "", url.strip())


def passage_warrants(claim, passage):
    """True only when the passage carries claim identity plus surface/status.

    A bare reuse of the same digits in an unrelated paragraph does not warrant
    the claim (T09.1.2 negative warrant).
    """
    if not passage or not claim:
        return False
    cid = claim["id"]
    has_id = cid in passage or cid.split("-")[0] + "-" + cid.split("-")[1] in passage
    # Allow family prefix only when the full id or the two-part stem matches
    # (C-07 matches C-07-25 family surfaces that print "C-07").
    stem = "-".join(cid.split("-")[:2])
    has_id = cid in passage or stem in passage
    has_surface = any(snippet in passage for _path, snippet in claim.get("surfaces") or ())
    has_status = "[UNVERIFIED]" in passage or "TEXT-VERIFIED" in passage
    if has_id and has_status:
        return True
    if has_id and has_surface:
        return True
    if has_surface and has_status and stem in passage:
        return True
    return False


def bibliography_html():
    """Compact course + external bibliography from metadata schema only."""
    course_rows = []
    for src in COURSE_SOURCES:
        cols = (
            src["id"],
            src["file"],
            src["kind"],
            src["extent"],
            src["role"],
            src["status"],
            src["note"],
        )
        body = "".join(f"<td>{_cell(c)}</td>" for c in cols[1:])
        course_rows.append(f'<tr><th scope="row">{_cell(cols[0])}</th>{body}</tr>')
    course_head = (
        "<th scope=\"col\">ID</th><th scope=\"col\">Fails</th>"
        "<th scope=\"col\">Kas tas ir</th><th scope=\"col\">Apjoms</th>"
        "<th scope=\"col\">Loma</th><th scope=\"col\">Statuss</th>"
        "<th scope=\"col\">Piezīme</th>"
    )
    course_table = (
        '<table class="data" id="course-sources">'
        "<caption>Kursa avoti. Lapas/slaidi no SOURCE_LEDGER; izdevumu/DOI/ISBN "
        "šeit nav izdomāti.</caption>"
        f"<thead><tr>{course_head}</tr></thead>"
        f"<tbody>{''.join(course_rows)}</tbody></table>"
    )

    ext_rows = []
    for row in EXTERNAL_SOURCES:
        sid = row["support_id"]
        sup = SUPPORTS[sid]
        status = sup["status"]
        if status == "TEXT-VERIFIED":
            mark = "[TEXT-VERIFIED]"
        else:
            mark = "[UNVERIFIED]"
        cols = (
            sid,
            sup["title"],
            (sup["version"] or "").split(";")[0],
            mark,
            row["supports"],
            print_url(sup.get("url") or ""),
        )
        body = "".join(f"<td>{_cell(c)}</td>" for c in cols[1:])
        ext_rows.append(f'<tr><th scope="row">{_cell(cols[0])}</th>{body}</tr>')
    ext_head = (
        "<th scope=\"col\">ID</th><th scope=\"col\">Avots</th>"
        "<th scope=\"col\">Versija</th><th scope=\"col\">Statuss</th>"
        "<th scope=\"col\">Ko atbalsta</th><th scope=\"col\">Drukāta adrese</th>"
    )
    ext_table = (
        '<table class="data" id="papildlasisana">'
        "<caption>Papildlasīšana. Tikai AGENTS §9 rindas; URL ir drukāts teksts bez "
        "shēmas un bez ielādes. Netiek uzskatīts par eksāmena autoritāti.</caption>"
        f"<thead><tr>{ext_head}</tr></thead>"
        f"<tbody>{''.join(ext_rows)}</tbody></table>"
    )

    locator_note = (
        '<p class="small muted" id="locator-grammar">Atsauces tekstā: '
        "<code>[A p.n]</code> / <code>[D p.n]</code> iespiesta lappuse; "
        "<code>[E s.n]</code> slaids; <code>[B #n]</code> semināra uzdevums; "
        "<code>[C]</code> temata apraksts; <code>C-NN</code> augsta riska "
        "reģistra ID (skatiet <a href=\"#warrant-table\">warrant tabulu</a>); "
        "<code>S-…</code> ārējais atbalsta ID.</p>"
    )
    return (
        '<div class="mx-wrap" id="bibliography">'
        f"{locator_note}{course_table}"
        "<h4 id=\"papildlasisana-h\">Papildlasīšana</h4>"
        f"{ext_table}</div>"
    )


def _line_of(text, snippet):
    at = text.find(snippet)
    if at < 0:
        return None, -1
    return text.count("\n", 0, at) + 1, at


def warrant_files():
    """Surface, gap and ledger checks. Prints nothing. Returns error strings
    with file, line and a selector."""
    errs = []
    for cid, claim in sorted(CLAIMS.items()):
        for key in SCHEMA:
            if key not in claim:
                errs.append(f"build/claims.py:1: #{cid} missing {key}")
        if claim["domain"] not in DOMAIN_RISK:
            errs.append(f"build/claims.py:1: #{cid} unknown domain")
        if claim["risk"] != classify_risk(claim["domain"], claim["regime"]):
            errs.append(f"build/claims.py:1: #{cid} risk mismatch")
        if claim["support_id"] not in SUPPORTS:
            errs.append(f"build/claims.py:1: #{cid} support gap")
            continue
        sup = SUPPORTS[claim["support_id"]]
        owners = [c["id"] for c in CLAIMS.values() if c["support_id"] == claim["support_id"]]
        if owners != [cid]:
            errs.append(f"build/claims.py:1: #{cid} support not one-to-one")
        if claim["status"] != "verified" and public_status(claim) != "[UNVERIFIED]":
            errs.append(f"build/claims.py:1: #{cid} rendered as verified")
        if claim["editor"] is not None or claim["may_replace_value"]:
            errs.append(f"build/claims.py:1: #{cid} editor set without approval")
        if revise_value(claim, "CHANGED") != claim["compare_value"]:
            errs.append(f"build/claims.py:1: #{cid} value replaced")
        if claim["status"] != "verified":
            for rel, snippet in claim["surfaces"]:
                path = ROOT / rel
                if not path.exists():
                    errs.append(f"{rel}:1: #{cid} missing file")
                    continue
                text = path.read_text(encoding="utf-8")
                line, at = _line_of(text, snippet)
                if line is None:
                    errs.append(f"{rel}:1: #{cid} anchor missing: {snippet}")
                    continue
                window = text[max(0, at - 500):at + 500]
                if "[UNVERIFIED]" not in window:
                    errs.append(f"{rel}:{line}: #{cid} unmarked high-risk value")
        if "http://" in row_html(claim) or "https://" in row_html(claim):
            errs.append(f"build/claims.py:1: #{cid} URL in row")
    for rel, phrase in FORBIDDEN:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        line, _at = _line_of(text, phrase)
        if line is not None:
            errs.append(f"{rel}:{line}: forbidden unqualified phrase")
    try:
        from ledger import E
    except ImportError as exc:
        errs.append(f"build/ledger.py:1: import failed {exc}")
        E = {}
    for eid in CLEARED_VERIFIED:
        if E.get(eid, {}).get("verified"):
            errs.append(f"build/ledger.py:1: #{eid} verified= still set")
    page = appendix_html()
    if page != appendix_html():
        errs.append("build/claims.py:1: #warrant-table not deterministic")
    lowered = page.lower()
    if "http://" in lowered or "https://" in lowered or "fetch(" in lowered:
        errs.append("build/claims.py:1: #warrant-table network text")
    bib = bibliography_html()
    if bib != bibliography_html():
        errs.append("build/claims.py:1: #bibliography not deterministic")
    blow = bib.lower()
    if "http://" in blow or "https://" in blow or "fetch(" in blow:
        errs.append("build/claims.py:1: #bibliography network text")
    if NOTES.exists():
        note = NOTES.read_text(encoding="utf-8")
        if NOTES_MARK not in note:
            errs.append("build/claims_notes.md:1: provenance mark missing")
        if NOTES_MARK in page or NOTES_MARK in bib:
            errs.append("build/claims.py:1: generated HTML includes notes mark")
    else:
        errs.append("build/claims_notes.md:1: missing provenance notes")
    builder = (ROOT / "build" / "build_master.py").read_text(encoding="utf-8")
    if "claims_notes" in builder:
        errs.append("build/build_master.py:1: builder reads provenance notes")
    return errs


def warrant_master():
    errs = []
    if not MASTER.exists():
        errs.append(f"{MASTER.name}:1: #warrant-table master missing")
        return errs
    text = MASTER.read_text(encoding="utf-8")
    line, _at = _line_of(text, 'id="warrant-table"')
    if line is None:
        errs.append(f"{MASTER.name}:1: #warrant-table not generated")
        return errs
    if "http://" in text or "https://" in text or "fetch(" in text:
        errs.append(f"{MASTER.name}:{line}: #warrant-table network text")
    if 'id="bibliography"' not in text or 'id="papildlasisana"' not in text:
        errs.append(f"{MASTER.name}:1: #bibliography / #papildlasisana not generated")
    for cid, claim in sorted(CLAIMS.items()):
        if claim["status"] == "verified":
            continue
        # The generated row must show the unverified mark, not a pass.
        needle = f"<th scope=\"row\">{cid}</th>"
        at = text.find(needle)
        if at < 0:
            errs.append(f"{MASTER.name}:{line}: #{cid} row missing")
            continue
        row = text[at:at + 2500]
        if "[UNVERIFIED]" not in row:
            errs.append(f"{MASTER.name}:{_line_of(text, needle)[0]}: #{cid} rendered as verified")
    for eid in CLEARED_VERIFIED:
        marker = f'id="e{eid[1:]}"'
        at = text.find(marker)
        if at < 0:
            errs.append(f"{MASTER.name}:1: #{eid} block missing")
            continue
        blk = text[at:at + 1800]
        if "pārbaudīts" in blk:
            errs.append(f"{MASTER.name}:{text.count(chr(10), 0, at) + 1}: #{eid} still pārbaudīts")
    return errs


def self_test():
    """Positive, negative and boundary fixtures. No network."""
    errs = []
    good = CLAIMS["C-01"]
    if not accept(good) or public_status(good) != "TEXT-VERIFIED":
        errs.append("build/claims.py:1: #C-01 matching regime did not pass")
    shifted = dict(good)
    shifted["regime"] = dict(good["regime"], temperature="37" + NB + "°C")
    if accept(shifted) or public_status(shifted) != "[UNVERIFIED]":
        errs.append("build/claims.py:1: #C-01 shifted temperature was accepted")
    # Same Kw digits, arterial specimen versus the pure-water support.
    kw = {
        "status": "verified",
        "support_id": "S-FIX",
        "compare_value": "1.0e-14",
        "editor": None,
        "may_replace_value": False,
        "regime": dict(SUPPORTS["S-EQ-25"]["regime"], specimen="arteriālās asinis"),
    }
    fake = {
        "S-FIX": {
            "status": "TEXT-VERIFIED",
            "compare_value": "1.0e-14",
            "regime": dict(SUPPORTS["S-EQ-25"]["regime"]),
        }
    }
    if accept(kw, fake) or regimes_match(kw["regime"], fake["S-FIX"]["regime"]):
        errs.append("build/claims.py:1: #Kw arterial specimen was accepted")
    gas = dict(CLAIMS["C-11-L"])
    gas["status"] = "verified"
    gas["support_id"] = "S-TH-G"
    if accept(gas):
        errs.append("build/claims.py:1: #C-11-L accepted on the gas-phase support")
    forced = dict(CLAIMS["C-07-25"])
    forced["status"] = "verified"
    if accept(forced) or public_status(forced) != "[UNVERIFIED]":
        errs.append("build/claims.py:1: #C-07-25 missing primary rendered as verified")
    if "http" in appendix_html().lower():
        errs.append("build/claims.py:1: #warrant-table contains a URL")

    # T09.1.2 negative: same digits in an unrelated stoich passage do not warrant Kw.
    unrelated = (
        "Stehiometrijas piemērs: koeficients 1,0·10⁻¹⁴ nav Kw; "
        "aprēķins lieto tikai molu attiecību 2:1."
    )
    if passage_warrants(CLAIMS["C-07-25"], unrelated):
        errs.append("build/claims.py:1: #C-07-25 warranted by unrelated digit reuse")
    # Positive: claim id + status at the real surface.
    aligned = (
        "Pie 25 °C tā ir 1,0·10⁻¹⁴ … nav nolasīti no primārās līdzsvara tabulas. "
        "[UNVERIFIED] C-07."
    )
    if not passage_warrants(CLAIMS["C-07-25"], aligned):
        errs.append("build/claims.py:1: #C-07-25 aligned passage did not warrant")
    # Boundary: inaccessible Gold Book stays UNVERIFIED in bibliography.
    bib = bibliography_html()
    if "http://" in bib.lower() or "https://" in bib.lower():
        errs.append("build/claims.py:1: #bibliography contains a URL scheme")
    if 'id="papildlasisana"' not in bib or "[UNVERIFIED]" not in bib:
        errs.append("build/claims.py:1: #papildlasisana missing UNVERIFIED Gold Book row")
    if 'id="course-sources"' not in bib:
        errs.append("build/claims.py:1: #course-sources table missing")
    # Locator grammar fixtures.
    for token, kind in (
        ("[D p.11]", "course"),
        ("[E s.54]", "course"),
        ("[B #13]", "course"),
        ("[A p.1–3]", "course"),
        ("C-07-25", "claim"),
        ("S-BIPM", "support"),
        ("(E29)", "errata"),
    ):
        got, _norm = parse_locator(token)
        if got != kind:
            errs.append(f"build/claims.py:1: locator {token!r} got {got!r} want {kind!r}")
    junk_kind, _ = parse_locator("[Al(OH)₄]")
    if junk_kind is not None:
        errs.append("build/claims.py:1: formula bracket accepted as locator")

    errs.extend(warrant_files())
    return errs
