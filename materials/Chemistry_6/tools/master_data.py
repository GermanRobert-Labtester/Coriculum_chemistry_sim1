"""Single source of truth for the Topic 13 master HTML.

Every number printed in the document is derived from this module or from
study_data.py.  ASCII equations are also fed to tools/check_equations.py.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------- constants
R = 8.314462618          # J mol-1 K-1
T = 298.15               # K
F = 96485.33212          # C mol-1
NERNST = 0.0592          # V, rounded 2.303*R*T/F at 298.15 K; used throughout
NERNST_EXACT = math.log(10) * R * T / F

ATOMIC = {
    "H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990,
    "S": 32.06, "Cl": 35.45, "K": 39.0983, "Mn": 54.938044,
    "Fe": 55.845, "Cr": 51.9961, "P": 30.973762,
}
MOLAR = {
    "KMnO4": 158.034,
    "FeSO4": 151.91,
    "FeSO4.7H2O": 278.02,
    "H2O2": 34.0147,
    "Fe": 55.845,
    "Mohr_anhydrous": 284.04,
    "Mohr_hexahydrate": 392.13,
    "H2C2O4": 90.034,
    "Na2S2O3": 158.11,
    "K2Cr2O7": 294.185,
}

# ---------------------------------------------------------------- formatting
# Task 05: every printed number has a unit key, a precision, and a rounding rule.
# Prefer mol/L everywhere in teaching text. "M" (= mol/L) appears only in quoted
# source wording and in labelled mistake examples; see MOLAR_SHORTHAND_RULE_LV.

NBSP = "\u00a0"  # no-break space before units
MINUS = "\u2212"

UNITS = {
    "c": {
        "symbol": "c(X)",
        "unit": "mol/L",
        "kind": "concentration",
        "note": "Molārā koncentrācija; dokumentā raksta mol/L, ne M.",
    },
    "N": {
        "symbol": "c_N(X)",
        "unit": "ekv/L",
        "kind": "normality",
        "note": "Normālā (ekvivalenta) koncentrācija = c·z; vēsturiska, tikai ja uzdevums prasa.",
        "deprecated": True,
    },
    "V_mL": {
        "symbol": "V(X)",
        "unit": "mL",
        "kind": "volume",
        "note": "Tilpums mililitros; uz litriem: V(L) = V(mL)/1000.",
    },
    "V_L": {
        "symbol": "V(X)",
        "unit": "L",
        "kind": "volume",
        "note": "Tilpums litros.",
    },
    "n": {
        "symbol": "n(X)",
        "unit": "mol",
        "kind": "amount",
        "note": "Vielas daudzums.",
    },
    "M": {
        "symbol": "M(X)",
        "unit": "g/mol",
        "kind": "molar_mass",
        "note": "Molmasa; nav koncentrācijas saīsinājums M.",
    },
    "m": {
        "symbol": "m(X)",
        "unit": "g",
        "kind": "mass",
        "note": "Masa.",
    },
    "rho_m": {
        "symbol": "ρ_m(X)",
        "unit": "g/L",
        "kind": "mass_concentration",
        "note": "Masas koncentrācija = c·M.",
    },
    "w": {
        "symbol": "w(X)",
        "unit": "%",
        "kind": "mass_fraction",
        "note": "Masas daļa procentos.",
    },
    "rho": {
        "symbol": "ρ",
        "unit": "g/mL",
        "kind": "density",
        "note": "Blīvums.",
    },
    "z": {
        "symbol": "z",
        "unit": "",
        "kind": "equivalence",
        "note": "Ekvivalences skaitlis (elektronu skaits uz formulas vienību); bez dimensijas.",
    },
    "E": {
        "symbol": "E",
        "unit": "V",
        "kind": "potential",
        "note": "Potenciāls; E°, E°′, ΔE.",
    },
    "T": {
        "symbol": "T",
        "unit": "K",
        "kind": "temperature",
        "note": "Termodinamiskā temperatūra.",
    },
    "F": {
        "symbol": "F",
        "unit": "C/mol",
        "kind": "constant",
        "note": "Faradeja konstante.",
    },
    "R": {
        "symbol": "R",
        "unit": "J/(mol·K)",
        "kind": "constant",
        "note": "Universālā gāzu konstante.",
    },
    "dG": {
        "symbol": "ΔG°",
        "unit": "kJ/mol",
        "kind": "energy",
        "note": "Standarta Gibsa enerģijas izmaiņa.",
    },
    "lgK": {
        "symbol": "lg K",
        "unit": "",
        "kind": "equilibrium",
        "note": "Līdzsvara konstantes dekadiskais logaritms; bez dimensijas.",
    },
    "pH": {
        "symbol": "pH",
        "unit": "",
        "kind": "acidity",
        "note": "pH = −lg a(H⁺); bez dimensijas.",
    },
    "ratio": {
        "symbol": "attiecība",
        "unit": "",
        "kind": "ratio",
        "note": "Bez dimensijas attiecība (piemēram, cik reižu jāmaina Q).",
    },
}

MOLAR_SHORTHAND_RULE_LV = (
    "Šajā materiālā koncentrāciju raksta mol/L. Saīsinājums M (= mol/L) parādās tikai "
    "citētos avota tekstos un kļūdu piemēros; tur tas ir deklarēts kā mol/L saīsinājums."
)

SIGFIG_GLOBAL_RULE_LV = (
    "Nenoapaļo starplielumus; noapaļo vienreiz beigās. Ja dati doti ar n zīmīgajiem "
    "cipariem, atbilde arī ar n. Decimāldaļu atdala ar komatu; starp skaitli un vienību "
    "ir nedalāma atstarpe. Vienības: mL, L, mol/L, g, g/mol, V."
)


def lv(x: float | int | str, nd: int = 2, strip: bool = True) -> str:
    """Latvian decimal comma, fixed significant decimals, unicode minus."""
    if isinstance(x, str):
        return x.replace("-", MINUS)
    s = f"{x:.{nd}f}"
    if strip and "." in s:
        s = s.rstrip("0").rstrip(".")
    s = s.replace("-", MINUS).replace(".", ",")
    return s


def sig(x: float, n: int, *, keep_zeros: bool = False) -> str:
    """Round to n significant figures and return Latvian text.

    keep_zeros=True preserves trailing zeros that carry significance
    (0,196 → 0,20 with n=2), which is required for Task 05 reported values.
    """
    if x == 0:
        return "0"
    from math import floor, log10
    nd = n - int(floor(log10(abs(x)))) - 1
    nd = max(nd, 0)
    rounded = round(x, nd)
    s = f"{rounded:.{nd}f}"
    if not keep_zeros and "." in s:
        s = s.rstrip("0").rstrip(".")
    return s.replace("-", MINUS).replace(".", ",")


def format_value(
    value: float | int,
    unit_key: str,
    *,
    sig_figs: int | None = None,
    decimals: int | None = None,
    strip: bool = False,
    with_unit: bool = True,
    keep_zeros: bool = True,
) -> str:
    """Format a number with Latvian comma, optional unit, and a declared precision.

    Prefer sig_figs for computed answers; prefer decimals for instrument-like
    readings (titres to 0,01 mL, E to 0,01 V). Unit key must be in UNITS.
    """
    if unit_key not in UNITS:
        raise KeyError(f"unknown unit key: {unit_key!r}")
    unit = UNITS[unit_key]["unit"]
    if decimals is not None:
        s = f"{float(value):.{decimals}f}"
        if strip and "." in s:
            s = s.rstrip("0").rstrip(".")
        s = s.replace("-", MINUS).replace(".", ",")
    elif sig_figs is not None:
        s = sig(float(value), sig_figs, keep_zeros=keep_zeros)
    else:
        s = lv(value, 6, strip=True)
    if with_unit and unit:
        return f"{s}{NBSP}{unit}"
    return s


# Significant-figure / display rule for E° (Task 03).
# Working tables quote to 0.01 V (2 decimals) unless a third decimal is needed
# for the source check or for values that are conventionally three-place (O₂, Cu, Zn…).
E_SIGFIG_RULE_LV = (
    "E° vērtības darba tabulās citē līdz 0,01 V; trešo decimāldaļu rāda tikai tur, "
    "kur to prasa avots vai pārbaude (piemēram, O₂ 1,229 V, Cu 0,337 V)."
)


def format_E(
    value: float,
    decimals: int = 2,
    *,
    signed: bool = False,
    unit: bool = False,
) -> str:
    """Format a potential with a fixed number of decimals (never strip 0,60 → 0,6)."""
    s = f"{value:.{decimals}f}".replace("-", MINUS).replace(".", ",")
    if signed and value > 0:
        s = "+" + s
    if unit:
        s += f"{NBSP}V"
    return s

# ---------------------------------------------------------------- calculations
class Calcs:
    """All worked numbers; verify_numbers.py recomputes these independently."""

    # Nernst examples (Task 07: pH centrepiece)
    mn_ph0 = 1.51
    mn_ph3 = 1.51 + NERNST / 5 * math.log10(1e-3 ** 8)
    mn_drop = mn_ph0 - mn_ph3
    mn_slope = NERNST / 5 * 8          # V per pH unit at unit [MnO₄⁻]/[Mn²⁺]
    mn_ph7 = 1.51 - mn_slope * 7       # formal only; Mn²⁺ not dominant at pH 7
    mn_lg_h8_ph3 = 8 * math.log10(1e-3)  # −24
    mn_corr_ph3 = NERNST / 5 * mn_lg_h8_ph3
    # T06 (Task 26): ratio half — E depends on [Ox]/[Red] as well as on pH.
    mn_ratio10_corr = NERNST / 5          # lg(10/1) = 1 → one full 0,0592/5 step
    mn_ratio10_E = 1.51 + NERNST / 5      # worked value, rounded once on display
    # T06 4.2 counterexample: doubling E° with the coefficient is wrong (M20).
    fe_e0 = 0.77
    fe_e0_double = 2 * fe_e0
    nernst_exact = NERNST_EXACT        # 0.05916… V before document rounding

    cr_slope = NERNST * 14 / 6
    cr_ph0 = 1.33
    cr_ph1 = 1.33 - cr_slope
    cr_ph2 = 1.33 - 2 * cr_slope
    cr_ph3 = 1.33 - 3 * cr_slope
    cl2 = 1.36
    cross_ph = (1.33 - 1.36) / cr_slope          # negative pH
    cross_h = 10 ** (-cross_ph)

    # direction/equilibrium
    dE_mn_fe = 1.51 - 0.77
    lgK_mn_fe = 5 * dE_mn_fe / NERNST
    dG_mn_fe = -5 * F * dE_mn_fe / 1000           # kJ/mol
    zncu = 0.337 - (-0.763)
    # PbO₂: working E° = 1.46 V (Task 03); CRC check = 1.455 V; source = 1.80 V.
    # E = E° + (0,0592/2)·lg([H⁺]⁴) at [PbO₂]=[Pb²⁺]=1, [H⁺]=8 mol/L.
    pbo2_working = 1.46
    pbo2_crc = 1.455
    pbo2_source = 1.80
    pbo2_h = 8.0
    # Both couples contain H+, so BOTH Nernst terms must be applied. Their slopes
    # nearly cancel (-0.1184 vs -0.0947 V/pH): pH alone cannot flip this pair.
    pbo2_slope = -NERNST * 4 / 2                  # V per pH unit
    mno4_slope_pb = -NERNST * 8 / 5                # V per pH unit
    pbo2_dslope = pbo2_slope - mno4_slope_pb      # -0.02368 V per pH unit
    pbo2_dE0 = pbo2_working - 1.51
    pbo2_dE0_crc = pbo2_crc - 1.51
    pbo2_dE0_src = pbo2_source - 1.51
    # T04 (H-05): the source-vs-working difference is derived once here and
    # rendered through the DERIVED_PROSE register. 1.80 − 1.46 = 0.34 V with
    # the displayed working value; against unrounded CRC 1.455 V it is 0.345 V.
    # Never subtract rounded values to manufacture agreement.
    pbo2_ediff = pbo2_source - pbo2_working            # 0.34 V
    pbo2_ediff_crc = pbo2_source - pbo2_crc            # 0.345 V (unrounded CRC)
    pbo2_at_8m = pbo2_working + NERNST / 2 * math.log10(pbo2_h ** 4)
    pbo2_at_8m_crc = pbo2_crc + NERNST / 2 * math.log10(pbo2_h ** 4)
    pbo2_at_8m_src = pbo2_source + NERNST / 2 * math.log10(pbo2_h ** 4)
    mno4_at_8m = 1.51 + NERNST / 5 * math.log10(pbo2_h ** 8)
    pbo2_dE_at_8m = pbo2_at_8m - mno4_at_8m
    pbo2_dE_at_8m_crc = pbo2_at_8m_crc - mno4_at_8m
    pbo2_dE_at_8m_src = pbo2_at_8m_src - mno4_at_8m
    # Working medium of the preparative method: 15 mol/L HNO3.
    pbo2_at_15m = pbo2_working + NERNST / 2 * math.log10(15 ** 4)
    pbo2_at_15m_crc = pbo2_crc + NERNST / 2 * math.log10(15 ** 4)
    mno4_at_15m = 1.51 + NERNST / 5 * math.log10(15 ** 8)
    pbo2_dE_at_15m = pbo2_at_15m - mno4_at_15m
    pbo2_dE_at_15m_crc = pbo2_at_15m_crc - mno4_at_15m
    # pH at which dE = 0 with both couples at unit activities (unreachable).
    pbo2_cross_ph = -pbo2_dE0 / pbo2_dslope
    pbo2_cross_h = 10 ** (-pbo2_cross_ph)
    # [MnO4-]/[Mn2+] that makes dE = 0 at 15 mol/L HNO3, other activities 1.
    pbo2_ratio15 = 10 ** ((pbo2_dE0 + pbo2_dslope * (-math.log10(15))) / (NERNST / 5))
    pbo2_ratio15_crc = 10 ** ((pbo2_dE0_crc + pbo2_dslope * (-math.log10(15))) / (NERNST / 5))

    # MnO₂ + HCl: E(MnO₂) = 1,23 + 0,1184·lg[H⁺] (p(MnO₂) = 1, [Mn²⁺] = 1);
    # E(Cl₂) = 1,36 − 0,0592·lg[Cl⁻]² at p(Cl₂) = 1 bar. In HCl, [H⁺] = [Cl⁻] = c.
    mno2_e0 = 1.23          # D10 supplement; CRC 1,224 V
    mno2_e0_crc = 1.224
    mno2_hcl = 12.0
    mno2_at_12m = mno2_e0 + NERNST / 2 * math.log10(mno2_hcl ** 4)
    cl2_at_12m = 1.36 + NERNST / 2 * math.log10(1 / mno2_hcl ** 2)
    mno2_dE_at_12m = mno2_at_12m - cl2_at_12m
    mno2_cross_hcl = 10 ** ((1.36 - mno2_e0) / (NERNST * 4 / 2 + NERNST * 2 / 2))
    mno2_cross_hcl_crc = 10 ** ((1.36 - mno2_e0_crc) / (NERNST * 4 / 2 + NERNST * 2 / 2))

    # Close-call working rule (Task 09): |ΔE°| < 0,15 V → use Nernst.
    close_call_v = 0.15
    close_call_lgK_z1 = 1 * close_call_v / NERNST      # 2,53
    close_call_factor_z1 = 10 ** close_call_lgK_z1     # ≈ 342

    # L25 illustrative titration: three concordant titres, mean 12.35 mL
    l25_titres = [12.30, 12.35, 12.40]
    l25_v = sum(l25_titres) / len(l25_titres)
    l25_cK = 0.0200
    l25_val = 10.00
    l25_vflask = 0.1000
    l25_cFe = l25_cK * l25_v * 5 / (1 * l25_val)
    l25_nflask = l25_cFe * l25_vflask
    l25_m = l25_nflask * MOLAR["FeSO4"]
    l25_m_hepta = l25_nflask * MOLAR["FeSO4.7H2O"]

    # LEC 3.1 — M = 284 g/mol is the task-printed value (3 s.f.); do not
    # substitute MOLAR["Mohr_anhydrous"] = 284.04 here (would invent precision).
    lec_c = 0.024 * 11 * 5 / (1 * 10)          # 0.132 exactly
    lec_c_printed = 0.13
    lec_M_given = 284.0                         # as printed in LEC
    lec_M_hexa = MOLAR["Mohr_hexahydrate"]      # 392.13
    lec_m_anhydrous = lec_c * 0.1 * lec_M_given  # 3.7488
    lec_m_hexahydrate = lec_c * 0.1 * lec_M_hexa
    lec_m_printed = 0.13 * 0.1 * 284            # source premature rounding path

    # LEC self-tests
    st1_c = (0.025 * 0.025) * 2 / 5 / 0.00375
    st1_m_100 = st1_c * 0.1 * MOLAR["KMnO4"]
    st1_normality = st1_c * 5
    st2_c = 0.02 * 0.01136 * 5 / 0.020
    st2_gL = st2_c * MOLAR["FeSO4"]
    st3_nK = 0.004 * 0.020
    st3_nH2O2_10 = st3_nK * 5 / 2
    st3_nH2O2_100 = st3_nH2O2_10 * 10
    st3_m = st3_nH2O2_100 * MOLAR["H2O2"]
    st3_w = st3_m / (2.00 * 1.05) * 100
    st4_nK = 0.022 * 0.00798
    st4_nFe25 = st4_nK * 5
    st4_nFe500 = st4_nFe25 * 20
    st4_mFe = st4_nFe500 * MOLAR["Fe"]
    st4_w = st4_mFe / 500.0 * 100

    # E0' conversions (Task 08): E°′ = E° − 0.0592·(m/n)·pH at pH 7
    h2_ph7 = 0.0 - NERNST * (2 / 2) * 7          # −0,4144 V
    o2_ph7 = 1.229 - NERNST * (4 / 4) * 7         # 0,8146 V ≈ 0,815 V
    o2_eprime_reported = 0.815                    # Campbell / working E°′
    nad_eprime = -0.32                            # Campbell E°′
    destructive_mixed_dE = 0.00 - (-0.32)         # wrong: H⁺/H₂(E°) − NAD(E°′)
    destructive_correct_dE = nad_eprime - h2_ph7  # NAD − H₂ both E°′

    # pH chart sample values
    ph_points = [-0.4, -0.22, 0, 1, 2, 3, 4, 7]

    @staticmethod
    def mn_E(ph: float) -> float:
        return 1.51 - NERNST / 5 * 8 * ph

    @staticmethod
    def cr_E(ph: float) -> float:
        return 1.33 - NERNST / 6 * 14 * ph

    @staticmethod
    def e_prime(E0: float, m_H: int, n_e: int, ph: float = 7.0) -> float:
        """Biochemical standard: E°′ = E° − 0.0592·(m/n)·pH."""
        return E0 - NERNST * (m_H / n_e) * ph


C = Calcs()

# ---------------------------------------------------------------- biological chain (Task 08)
# Working column is always E°′ (pH 7). LEC 1. tabula kept as transcript (A5).
# kind: calculated = from E° via formula; campbell = external E°′; lec_as_eprime = LEC number
# treated as E°′ with caveat; protein = depends on binding environment.
BIO_CHAIN = [
    {
        "pair": "2H⁺/H₂",
        "lec": 0.00,
        "lec_flag": "E° (pH 0)",
        "eprime": C.h2_ph7,
        "kind": "calculated",
        "m": 2, "n": 2,
        "note": "E°′ = 0 − 0,0592·(2/2)·7 = −0,414 V. Avota 0,00 ir E°, nevis E°′ (A5).",
    },
    {
        "pair": "NAD⁺/NADH",
        "lec": -0.3391,
        "lec_flag": "LEC (sajaukta)",
        "eprime": C.nad_eprime,
        "kind": "campbell",
        "m": 1, "n": 2,
        "note": "Campbell E°′ ≈ −0,32 V; LEC −0,3391 V saglabāta avota kolonnā.",
    },
    {
        "pair": "FAD/FADH₂",
        "lec": -0.2735,
        "lec_flag": "LEC (sajaukta)",
        "eprime": -0.18,
        "kind": "protein",
        "m": 2, "n": 2,
        "note": "Campbell −0,18 V brīvajam FAD; saistītam proteīnā vērtība mainās.",
    },
    {
        "pair": "CoQ/CoQH₂",
        "lec": 0.0197,
        "lec_flag": "LEC (sajaukta)",
        "eprime": 0.10,
        "kind": "campbell",
        "m": 2, "n": 2,
        "note": "Campbell ≈ +0,10 V; LEC 0,0197 V atšķiras.",
    },
    {
        "pair": "citohroms b",
        "lec": 0.077,
        "lec_flag": "LEC ≈ E°′",
        "eprime": 0.075,
        "kind": "protein",
        "m": 0, "n": 1,
        "note": "Campbell 0,075 V; atkarīgs no proteīna vides.",
    },
    {
        "pair": "citohroms c₁",
        "lec": 0.220,
        "lec_flag": "LEC ≈ E°′",
        "eprime": 0.22,
        "kind": "lec_as_eprime",
        "m": 0, "n": 1,
        "note": "Avota vērtība pieņemta kā E°′; atsevišķi nav pārbaudīta.",
    },
    {
        "pair": "citohroms c",
        "lec": 0.254,
        "lec_flag": "LEC ≈ E°′",
        "eprime": 0.254,
        "kind": "campbell",
        "m": 0, "n": 1,
        "note": "Campbell 0,254 V; Fe³⁺/Fe²⁺ citohromā.",
    },
    {
        "pair": "citohroms a",
        "lec": 0.290,
        "lec_flag": "LEC ≈ E°′",
        "eprime": 0.29,
        "kind": "lec_as_eprime",
        "m": 0, "n": 1,
        "note": "Avota vērtība; proteīna vide.",
    },
    {
        "pair": "citohroms a₃",
        "lec": 0.350,
        "lec_flag": "LEC ≈ E°′",
        "eprime": 0.35,
        "kind": "lec_as_eprime",
        "m": 0, "n": 1,
        "note": "Avota vērtība; proteīna vide.",
    },
    {
        "pair": "O₂/H₂O",
        "lec": 0.6945,
        "lec_flag": "LEC (A4)",
        "eprime": C.o2_eprime_reported,
        "kind": "calculated",
        "m": 4, "n": 4,
        "note": "E° = 1,229 V → E°′ = 1,229 − 0,0592·7 ≈ 0,815 V (Campbell). Avota 0,6945 V nav šī pāra (A4).",
    },
]

# ---------------------------------------------------------------- potential comparisons (T05)
# Every side-by-side potential comparison rendered in the master is registered here.
# Gate rule R3: a comparison with different conventions on its sides may appear ONLY
# inside the destructive teaching block (id="destructive-mix", 8.2).
# convention codes: E0 | E | Eprime
def _cmp(
    id_: str, a_id: str, b_id: str, a_conv: str, b_conv: str, *,
    role: str = "working", verdict: str = "",
    activities: str = "vienības aktivitātes", ph: float | None = 0.0,
    temperature_K: float | None = 298.15, note: str = "",
) -> dict:
    return {
        "id": id_, "a_id": a_id, "b_id": b_id, "a_conv": a_conv, "b_conv": b_conv,
        "same_convention": a_conv == b_conv, "role": role, "verdict": verdict,
        "activities": activities, "ph": ph, "temperature_K": temperature_K,
        "note": note,
    }


POTENTIAL_COMPARISONS: list[dict] = [
    _cmp("cmp.mn.fe", "mno4h", "fe3", "E0", "E0",
         verdict="MnO₄⁻ oksidē Fe²⁺; ΔE° = 0,74 V — stabils secinājums",
         note="3.4/4.3 piemērs; abas vērtības E° pie pH 0, 298 K."),
    _cmp("cmp.pbo2.mn", "pbo2", "mno4h", "E0", "E0",
         verdict="Standartapstākļos nē; pie [H⁺]=8 arī nē; virzienu griež produkta attiecība, ne pH",
         activities="[Pb²⁺]=[Mn²⁺]=1; pie 8 mol/L H⁺; pie 15 mol/L HNO₃", ph=None,
         note="4.4. tabula; darba 1,46 V pret MnO₄⁻ 1,51 V; CRC un avota vērtības rādītas atsevišķi."),
    _cmp("cmp.cr.cl", "cr2o7", "cl2", "E0", "E0",
         verdict="Pie [H⁺] ≳ 1,65 mol/L dihromāts oksidē Cl⁻; atšķaidītā skābē — nē",
         activities="[Cr₂O₇²⁻]=[Cr³⁺]=[Cl⁻]=1, p(Cl₂)=1 bar; [H⁺] mainīgs", ph=None,
         note="4.3 slieksnis izraksts no deklarētām aktivitātēm; “skābā vidē” vien nav pietiekami (A13)."),
    _cmp("cmp.h2.fe3", "h2", "fe3", "E0", "E0",
         verdict="H⁺ oksidē Fe līdz Fe²⁺, bet ne Fe²⁺ līdz Fe³⁺",
         note="5. nodaļas secinājums no E°(H⁺/H₂)=0 un E°(Fe³⁺/Fe²⁺)=0,77 V."),
    _cmp("cmp.mn.media", "mno4h", "mno4n", "E0", "E0",
         verdict="Dažādas vides — dažādi produkti un z; nav savstarpējs E° salīdzinājums vienā vidē",
         note="Mn trio: katrs E° definēts savas sarakstītās pusreakcijas vienības aktivitātēm."),
    _cmp("cmp.h2.nad", "h2", "nad", "E0", "Eprime",
         role="teaching_only",
         verdict="Sajaukta konvencija apgriež šķietamo plūsmu — destruktīvais tests (8.2)",
         ph=7.0,
         note="A5: 0,00 V ir E°, −0,32 V ir E°′. Salīdzinājums drīkst pastāvēt tikai 8.2 destruktīvajā blokā."),
    _cmp("cmp.bio.chain", "nad", "o2prime", "Eprime", "Eprime",
         verdict="Elektroni NADH → … → O₂ vienā E°′ kolonnā (pH 7)",
         activities="Campbell izraksta vērtības; proteīna vide daļai pāru", ph=7.0,
         temperature_K=None,
         note="8.1. tabula; Darba kolonna tikai E°′; T izrakstā nenosaukta (H-11)."),
    _cmp("cmp.o2.eprime", "o2h2o", "o2prime", "E0", "Eprime",
         role="teaching_only",
         verdict="Viens pāris, divas konvencijas: 1,229 V (E°, pH 0) un 0,815 V (E°′, pH 7)",
         ph=7.0,
         note="8.1 darba piemērs; abi skaitļi ir viena pāra divās konvencijās, nav divi pāri."),
]

# Non-COUPLES comparison participants: biochemical E°′ carriers (Campbell transcript).
EPRIME_PARTICIPANTS: dict[str, dict] = {
    "nad": {
        "pair": "NAD⁺/NADH", "E": -0.32, "kind": "campbell",
        "conditions": "E°′ (pH 7,0); T izrakstā nenosaukta; identitāte neatrisināta (T03)",
    },
    "o2prime": {
        "pair": "O₂/H₂O", "E": C.o2_eprime_reported, "kind": "calculated",
        "conditions": "E°′ (pH 7,0) = E° − 0,0592·(4/4)·7; T nenosaukta (Campbell izraksts)",
    },
    "h2prime": {
        "pair": "2H⁺/H₂", "E": C.h2_ph7, "kind": "calculated",
        "conditions": "E°′ (pH 7,0) = E° − 0,0592·(2/2)·7",
    },
}

# ---------------------------------------------------------------- couples
# Single registry (Task 03). E_working is the only value used in tables, ladder,
# Nernst prose, I1/I2 JSON and calculators. E_source is kept for 13.A / change log.
# status: source | corrected | verified | unverified

# F04: comparability verdict labels (display + gate vocabulary) and the
# mandated string for rows whose condition metadata is missing/unaligned.
COMPARABILITY_VERDICTS_LV = {
    # En dash: the build normalizes em dashes document-wide (build_master).
    "safe": "jā – konvencijas sakrīt",
    "caveat": "ar atrunu",
    "unaligned": "nē",
}
COMPARABILITY_UNALIGNED_LV = "nosacījumi nav pilnībā salīdzināti"

@dataclass(frozen=True)
class Couple:
    id: str
    ox: str
    red: str
    half: str
    z: int
    E_working: float
    E_source: float | None = None
    medium: str = "skāba"
    role: str = "ok"          # ok = oxidant, red = reductant, amp = amphoteric
    status: str = "source"    # source | corrected | verified | unverified
    sig_figs: int = 3
    decimals: int = 2         # display decimals for working tables
    source_ref: str = ""
    E_check: float | None = None  # CRC / external check (may differ from working)
    flag: str = ""
    note: str = ""
    family: str = ""
    h: int = 0                 # H⁺ on the reactant side of the reduction
    oh: int = 0                # OH⁻ on the product side (basic form)
    gas: bool = False          # half-reaction contains a gas (p ≠ 1 bar matters)
    ph_limit: float | None = None  # above this pH the written forms are not dominant
    claim_id: str = ""
    # --- T05 condition metadata: what the stored value IS, and when it is valid ---
    potential_type: str = "E0"     # E0 | E | Eprime — convention of E_working
    temperature_K: float | None = 298.15  # temperature of the stated convention
    ph: float | None = 0.0         # pH of the stated convention (E°: 0; E°′: 7)
    activities: str = "vienības aktivitātes"  # declared activity/pressure conditions
    reaction_id: str = ""          # WORKED id or reaction anchor the couple is used in
    source_id: str = ""            # must resolve in qa/sources.csv (T05 gate)
    conditions_note: str = ""      # limitation/warrant wording shown with the value

    @property
    def E(self) -> float:
        """Alias for E_working — used by ladder, JSON, sorting."""
        return self.E_working

    @property
    def ph_slope(self) -> float:
        """dE/dpH at unit activities of every other species, V per pH unit.

        E = E° − (0,0592/z)·(h + oh)·pH for a half-reaction written with H⁺
        (acid form) or OH⁻ (basic form): both lower E when pH rises.
        Zero means the couple has no pH term in its Nernst expression.
        """
        return -NERNST * (self.h + self.oh) / self.z

    @property
    def ph_dependent(self) -> bool:
        return (self.h + self.oh) > 0

    @property
    def source_E(self) -> float | None:
        return self.E_source

    @property
    def conv_class(self) -> str:
        """CSS state class for the convention of this value (T05)."""
        return {"E0": "conv-e0", "E": "conv-e", "Eprime": "conv-eprime"}[
            self.potential_type
        ]

    def conditions_prose(self) -> str:
        """One-line validity statement for tables/captions (T05 display rule)."""
        kind = {"E0": "E°", "E": "E", "Eprime": "E°′"}[self.potential_type]
        if self.potential_type == "E":
            return f"E — faktiskais potenciāls ({self.conditions_note or 'nosacījumi jānosauc atsevišķi'})"
        # F03: surfaced in visible panel prose — Latvian decimal comma (B8).
        def _lv(x: float) -> str:
            return f"{x:g}".replace(".", ",")
        temp = f", {_lv(self.temperature_K)} K" if self.temperature_K is not None else ", T nav norādīts"
        ph = f"pH {_lv(self.ph)}" if self.ph is not None else "bez pH termiņa"
        act = self.activities
        return f"{kind} ({ph}{temp}, {act})"

    def format_working(self, *, signed: bool = False, unit: bool = False) -> str:
        return format_E(self.E_working, self.decimals, signed=signed, unit=unit)

    def provenance_title(self) -> str:
        """Hover/title text: working — check — source — changelog."""
        parts = [f"{self.format_working()} V — darba vērtība"]
        # T05: the convention sentence comes first in every tooltip.
        parts.append(self.conditions_prose())
        if self.E_check is not None and abs(self.E_check - self.E_working) > 5e-4:
            # CRC often prints three decimals (1,066; 1,455).
            parts.append(f"CRC/pārbaude {format_E(self.E_check, 3)} V")
        if self.E_source is not None and abs(self.E_source - self.E_working) > 5e-4:
            src = self.E_source
            # Match the printed source precision: 1.21865 keeps 5 dp; else 2–3.
            if abs(src - round(src, 2)) < 5e-5:
                nd = 2
            elif abs(src - round(src, 3)) < 5e-6:
                nd = 3
            else:
                nd = 5
            parts.append(f"avots {format_E(src, nd)} V")
        if self.source_ref:
            parts.append(self.source_ref)
        if self.status and self.status != "source":
            parts.append(f"statuss: {self.status}")
        return " — ".join(parts)

    # --- F04: comparability verdict, derived only from the fields above ----
    def comparability(self) -> tuple[str, str]:
        """(verdict, note) — may this E° be compared directly with other E°?

        Verdict keys: "safe" | "caveat" | "unaligned". Aligned means: E°
        convention (not E or E°′), 298,15 K, unit activities. A caveat does
        not block the comparison but must be stated. Derivation is
        attribute-driven — no couple ids are hardcoded here, so a future row
        without condition metadata degrades to "unaligned" and the matrix
        renders «nosacījumi nav pilnībā salīdzināti» for it (F04 failure rule).
        """
        if (self.potential_type != "E0"
                or self.temperature_K != 298.15
                or not self.activities
                or self.activities != "vienības aktivitātes"):
            return "unaligned", COMPARABILITY_UNALIGNED_LV
        if self.source_id == "CRC":
            return ("caveat",
                    "Darba vērtība no CRC izraksta; avota identitāte neatrisināta (T03, 13.E).")
        if self.ph_limit is not None:
            lim = f"{self.ph_limit:g}".replace(".", ",")
            return ("caveat",
                    f"Salīdzināms kā E° tikai zem pH ≈ {lim}; virs tā rakstītā forma nav dominējoša.")
        if self.medium in ("neitrāla", "bāziska"):
            return ("caveat",
                    "Vide norāda dominējošo produktu, nevis E° nosacījumus; E° definēts pie a(OH⁻)=1 rakstītajai pusreakcijai.")
        return "safe", ""


def _c(
    id: str, ox: str, red: str, half: str, z: int, E_working: float, *,
    E_source: float | None = None, medium: str = "skāba", role: str = "ok",
    status: str = "source", sig_figs: int = 3, decimals: int = 2,
    source_ref: str = "", E_check: float | None = None,
    flag: str = "", note: str = "", family: str = "",
    h: int = 0, oh: int = 0, gas: bool = False, ph_limit: float | None = None,
    claim_id: str = "",
    potential_type: str = "E0", temperature_K: float | None = 298.15,
    ph: float | None = 0.0, activities: str = "vienības aktivitātes",
    reaction_id: str = "", source_id: str = "LEC", conditions_note: str = "",
) -> Couple:
    if E_source is None:
        E_source = E_working
    return Couple(
        id, ox, red, half, z, E_working, E_source, medium, role,
        status, sig_figs, decimals, source_ref, E_check, flag, note, family,
        h, oh, gas, ph_limit, claim_id,
        potential_type, temperature_K, ph, activities, reaction_id, source_id,
        conditions_note,
    )


COUPLES: list[Couple] = [
    _c("f2", "F₂", "2F⁻", "F2 + 2e^- -> 2F^-", 2, 2.87,
       source_ref="LEC 2. tabula", family="halogēni"),
    _c("h2o2h2o", "H₂O₂", "H₂O", "H2O2 + 2H^+ + 2e^- -> 2H2O", 2, 1.78,
       source_ref="LEC 2. tabula", family="peroksīdi", h=2),
    _c("pbo2", "PbO₂", "Pb²⁺", "PbO2 + 4H^+ + 2e^- -> Pb^2+ + 2H2O", 2, 1.46,
       E_source=1.80, status="corrected", decimals=2, E_check=1.455,
       source_ref="LEC P063; A3", flag="Labots", h=4, claim_id="A3",
       note="Darba vērtība 1,46 V (CRC 1,455 V noapaļots); avotā +1,80 V — saglabāta 13.A.",
       family="metāli", source_id="CRC",
       conditions_note="Darba E° no CRC dump (identitāte neatrisināta — T03); nosacītais E aprēķins 4.4 ar deklarētām aktivitātēm."),
    _c("mno4h", "MnO₄⁻", "Mn²⁺", "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O", 5, 1.51,
       source_ref="LEC 2. tabula", note="Skābā vidē; [H⁺]⁸ Nernsta izteiksmē.", h=8, ph_limit=3,
       family="permanganāts", reaction_id="6.1",
       conditions_note="Nosacītais E (3.4) pie [MnO₄⁻]=[Mn²⁺]=1; formāls aiz pH ≈ 3."),
    _c("cl2", "Cl₂", "2Cl⁻", "Cl2 + 2e^- -> 2Cl^-", 2, 1.36,
       medium="jebkura", source_ref="LEC 2. tabula", family="halogēni", gas=True),
    _c("cr2o7", "Cr₂O₇²⁻", "2Cr³⁺", "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O", 6, 1.33,
       status="verified", source_ref="LEC 2. tabula; A13", claim_id="A13",
       note="Avota 1,33 V saglabāta kursa aprēķiniem; CRC 1,232 V ir cita konvencija (13.E).",
       family="hroms", h=14, ph_limit=3, source_id="LEC",
       conditions_note="Nosacītais E (4.4) der tikai pie deklarētām aktivitātēm; “skābā vidē” nav skaitlis (A13)."),
    _c("o2h2o", "O₂", "H₂O", "O2 + 4H^+ + 4e^- -> 2H2O", 4, 1.229,
       E_source=1.21865, status="corrected", decimals=3, E_check=1.229,
       source_ref="LEC 1. tabula; A4", flag="Labots", claim_id="A4",
       note="Avotā 1,21865 V un nepareiza 2 e⁻ shēma; darba E° = 1,229 V, E°′ = 0,815 V.",
       family="skābeklis", h=4, gas=True, source_id="CRC",
       conditions_note="E° 25 °C, a(H⁺)=1, p(O₂)=1 bar (CRC dump; identitāte neatrisināta — T03); E°′ 0,815 V — pH 7,0, T nenosaukts (Campbell izraksts)."),
    _c("br2", "Br₂", "2Br⁻", "Br2 + 2e^- -> 2Br^-", 2, 1.07,
       E_source=0.96, status="corrected", decimals=2, E_check=1.066,
       medium="jebkura", source_ref="LEC P078; A2", flag="Labots", claim_id="A2",
       note="Darba vērtība 1,07 V (CRC 1,066 V); avotā 0,96 V (NO₃⁻/NO vērtība).",
       family="halogēni", source_id="CRC",
       conditions_note="Darba vērtība no CRC dump (identitāte neatrisināta — T03)."),
    _c("no3no", "NO₃⁻", "NO", "NO3^- + 4H^+ + 3e^- -> NO + 2H2O", 3, 0.96,
       source_ref="LEC 2. tabula", family="slāpeklis", h=4, gas=True),
    _c("no3no2aq", "NO₃⁻", "NO₂", "NO3^- + 2H^+ + e^- -> NO2 + H2O", 1, 0.80,
       source_ref="LEC 2. tabula", family="slāpeklis", h=2, gas=True),
    _c("fe3", "Fe³⁺", "Fe²⁺", "Fe^3+ + e^- -> Fe^2+", 1, 0.77,
       role="amp", medium="jebkura", source_ref="LEC 2. tabula", family="dzelzs"),
    _c("o2h2o2", "O₂", "H₂O₂", "O2 + 2H^+ + 2e^- -> H2O2", 2, 0.68,
       role="amp", source_ref="LEC 2. tabula", family="skābeklis", h=2, gas=True),
    _c("mno4n", "MnO₄⁻", "MnO₂", "MnO4^- + 2H2O + 3e^- -> MnO2 + 4OH^-", 3, 0.60,
       medium="neitrāla", source_ref="LEC 2. tabula; L21",
       note="Avota vērtība 0,60 V; Nernsts mainās ar pH.", family="permanganāts", oh=4,
       reaction_id="6.2",
       conditions_note="E° definēts pie a(OH⁻)=1 sarakstītajai pusreakcijai; vide “neitrāla” norāda dominējošo produktu, nevis E° nosacījumus."),
    _c("mno4b", "MnO₄⁻", "MnO₄²⁻", "MnO4^- + e^- -> MnO4^2-", 1, 0.56,
       medium="bāziska", source_ref="LEC 2. tabula; L21", family="permanganāts",
       reaction_id="6.3",
       conditions_note="Pusreakcijā nav H⁺/OH⁻; vide “bāziska” norāda dominējošo produktu, nevis E° nosacījumus."),
    _c("i2", "I₂", "2I⁻", "I2 + 2e^- -> 2I^-", 2, 0.54,
       medium="jebkura", source_ref="LEC 2. tabula", family="halogēni"),
    _c("cu2", "Cu²⁺", "Cu", "Cu^2+ + 2e^- -> Cu", 2, 0.337,
       medium="jebkura", decimals=3, source_ref="LEC 2. tabula", family="metāli"),
    _c("so4so3", "SO₄²⁻", "SO₃²⁻", "SO4^2- + 2H^+ + 2e^- -> SO3^2- + H2O", 2, 0.20,
       role="amp", source_ref="LEC 2. tabula", family="sērs", h=2),
    _c("sh2s", "S", "H₂S", "S + 2H^+ + 2e^- -> H2S", 2, 0.17,
       role="amp", source_ref="LEC 2. tabula", family="sērs", h=2),
    _c("s4o6", "S₄O₆²⁻", "2S₂O₃²⁻", "S4O6^2- + 2e^- -> 2S2O3^2-", 2, 0.10,
       medium="jebkura", source_ref="LEC 2. tabula", family="sērs"),
    _c("h2", "2H⁺", "H₂", "2H^+ + 2e^- -> H2", 2, 0.00,
       role="amp", source_ref="LEC 2. tabula", family="ūdeņradis", h=2, gas=True),
    _c("pb2", "Pb²⁺", "Pb", "Pb^2+ + 2e^- -> Pb", 2, -0.126,
       medium="jebkura", decimals=3, source_ref="LEC 2. tabula", family="metāli"),
    _c("sn2", "Sn²⁺", "Sn", "Sn^2+ + 2e^- -> Sn", 2, -0.136,
       medium="jebkura", decimals=3, source_ref="LEC 2. tabula", family="metāli"),
    _c("zn2", "Zn²⁺", "Zn", "Zn^2+ + 2e^- -> Zn", 2, -0.763,
       medium="jebkura", decimals=3, source_ref="LEC 2. tabula", family="metāli"),
    _c("al3", "Al³⁺", "Al", "Al^3+ + 3e^- -> Al", 3, -1.66,
       medium="jebkura", source_ref="LEC 2. tabula", family="metāli"),
    _c("alo2", "AlO₂⁻", "Al", "AlO2^- + 2H2O + 3e^- -> Al + 4OH^-", 3, -2.35,
       medium="bāziska", source_ref="LEC 2. tabula", family="metāli", oh=4),
]

COUPLE_BY_ID = {c.id: c for c in COUPLES}
LADDER_IDS = ["f2", "h2o2h2o", "mno4h", "cl2", "cr2o7", "o2h2o", "br2", "fe3", "i2", "cu2", "h2", "zn2", "al3"]

# Calcs was defined before the registry; keep derived E° numbers locked to E_working.
assert abs(C.pbo2_working - COUPLE_BY_ID["pbo2"].E_working) < 1e-12
assert abs(C.mn_ph0 - COUPLE_BY_ID["mno4h"].E_working) < 1e-12
assert abs(C.cr_ph0 - COUPLE_BY_ID["cr2o7"].E_working) < 1e-12
assert abs(C.cl2 - COUPLE_BY_ID["cl2"].E_working) < 1e-12
assert abs(C.o2_ph7 - (COUPLE_BY_ID["o2h2o"].E_working - NERNST * 7)) < 1e-12


def e_html(couple_or_id: Couple | str, *, signed: bool = False, unit: bool = True) -> str:
    """Working E° as a provenance-marked HTML span for tables and prose."""
    c = couple_or_id if isinstance(couple_or_id, Couple) else COUPLE_BY_ID[couple_or_id]
    text = c.format_working(signed=signed, unit=unit)
    title = c.provenance_title().replace('"', "&quot;")
    claim_attr = f' data-claim="{c.claim_id}"' if c.claim_id else ''
    # T05: every value span carries its convention, pH, temperature and medium.
    ph_attr = f"{c.ph:g}" if c.ph is not None else ""
    temp_attr = f"{c.temperature_K:g}" if c.temperature_K is not None else ""
    conv_attr = f' data-conv="{c.potential_type}"'
    conv_attr += f' data-ph="{ph_attr}"' if ph_attr else ' data-ph=""'
    conv_attr += f' data-temp-k="{temp_attr}"' if temp_attr else ' data-temp-k=""'
    conv_attr += f' data-medium="{c.medium}"'
    # F03: every value span links to its static evidence panel (13.F.3,
    # id="ev-<couple id>"); no JS, the anchor is the whole interaction.
    return (
        f'<a class="value-ref" href="#ev-{c.id}">'
        f'<span class="e-value {c.conv_class}"{conv_attr} data-couple="{c.id}" data-e="{c.E_working}" '
        f'data-status="{c.status}"{claim_attr} title="{title}">{text}</span></a>'
    )

# Source table 2 in source order, with labels repaired (A1) and flags.
# (source element label, corrected label, ox side, z, red side, source E, master E, flag)
SOURCE_TABLE = [
    ("N", "N", "NO₃⁻ + 2H⁺", 1, "NO₂(g) + H₂O", "+0,80", "+0,80", ""),
    ("N", "N", "NO₃⁻ + H₂O", 2, "NO₂⁻ + 2OH⁻", "+0,01", "+0,01", ""),
    ("N", "N", "NO₃⁻ + 2H⁺", 2, "NO₂⁻ + H₂O", "+0,94", "+0,94", ""),
    ("N", "N", "NO₃⁻ + 4H⁺", 3, "NO(g) + 2H₂O", "+0,96", "+0,96", ""),
    ("N", "N", "NO₃⁻ + 7H₂O", 8, "NH₄OH + 9OH⁻", "−0,12", "−0,12", ""),
    ("Br", "Br", "Br₂", 2, "2Br⁻", "+0,96", "+1,07", "Labots (A2)"),
    ("Bi", "Bi", "BiO₃⁻ + 6H⁺", 2, "Bi³⁺ + 3H₂O", "+1,80", "+1,80", ""),
    ("H", "H", "2H⁺", 2, "H₂", "0,00", "0,00", ""),
    ("O", "O", "O₂(g) + 4H⁺", 4, "2H₂O", "+1,21865", "+1,229", "Labots (A4)"),
    ("O", "O", "H₂O₂ + 2H⁺", 2, "2H₂O", "+1,78", "+1,78", ""),
    ("O", "O", "O₂(g) + 2H⁺", 2, "H₂O₂", "+0,68", "+0,68", ""),
    ("Mn (H⁺)", "Mn (H⁺)", "MnO₄⁻ + 8H⁺", 5, "Mn²⁺ + 4H₂O", "+1,51", "+1,51", ""),
    ("(H₂O)", "Mn (H₂O)", "MnO₄⁻ + 2H₂O", 3, "MnO₂↓ + 4OH⁻", "+0,60", "+0,60", "Vides apzīmējums precizēts"),
    ("(OH⁻)", "Mn (OH⁻)", "MnO₄⁻", 1, "MnO₄²⁻", "+0,56", "+0,56", "Vides apzīmējums precizēts"),
    ("Pb", "Pb", "PbO₂↓ + 4H⁺", 2, "Pb²⁺ + 2H₂O", "+1,80", "+1,46", "Labots, avota vērtība paturēta (A3)"),
    ("S", "S", "SO₄²⁻ + 2H⁺", 2, "SO₃²⁻ + H₂O", "+0,20", "+0,20", ""),
    ("S", "S", "SO₄²⁻ + H₂O", 2, "SO₃²⁻ + 2OH⁻", "−0,93", "−0,93", ""),
    ("S", "S", "S↓", 2, "S²⁻", "−0,48", "−0,48", ""),
    ("S", "S", "S↓ + 2H⁺", 2, "H₂S", "+0,17", "+0,17", ""),
    ("S", "S", "S₄O₆²⁻", 2, "2S₂O₃²⁻", "+0,10", "+0,10", ""),
    ("Fe", "Fe", "Fe³⁺", 1, "Fe²⁺", "+0,77", "+0,77", ""),
    ("I", "I", "I₂", 2, "2I⁻", "+0,54", "+0,54", ""),
    ("F", "F", "F₂", 2, "2F⁻", "+2,87", "+2,87", ""),
    ("Cl", "Cl", "Cl₂", 2, "2Cl⁻", "+1,36", "+1,36", ""),
    ("Cl", "Cl", "OCl⁻ + 2H⁺", 2, "H₂O + Cl⁻", "+1,49", "+1,49", ""),
    ("Cr", "Cr", "Cr₂O₇²⁻ + 14H⁺", 6, "2Cr³⁺ + 7H₂O", "+1,33", "+1,33", "Avota vērtība paturēta"),
    ("Cr", "Cr", "CrO₄²⁻ + 4H₂O", 3, "Cr(OH)₃↓ + 5OH⁻", "−0,13", "−0,13", ""),
    ("C", "C", "2CO₂ + 2H⁺", 2, "H₂C₂O₄", "−0,49", "−0,49", ""),
    ("Al", "Al", "AlO₂⁻ + 2H₂O", 3, "Al + 4OH⁻", "−2,35", "−2,35", "Avota dublikāts noņemts (A1)"),
    ("Cu", "Al", "Al³⁺", 3, "Al↓", "−1,66", "−1,66", "Etiķete pārbīdīta (A1)"),
    ("Pb", "Cu", "Cu²⁺", 2, "Cu↓", "+0,337", "+0,337", "Etiķete pārbīdīta (A1)"),
    ("Sn", "Pb", "Pb²⁺", 2, "Pb↓", "−0,126", "−0,126", "Etiķete pārbīdīta (A1)"),
    ("Zn", "Sn", "Sn²⁺", 2, "Sn↓", "−0,136", "−0,136", "Etiķete pārbīdīta (A1)"),
    ("", "Zn", "Zn²⁺", 2, "Zn↓", "−0,763", "−0,763", "Etiķete pārbīdīta (A1)"),
]

# ---------------------------------------------------------------- equations
@dataclass
class Worked:
    id: str
    title: str
    source: str
    ox_half: str
    red_half: str
    ox_mult: int
    red_mult: int
    uncancelled: str
    ionic: str
    molecular: str
    note: str = ""
    extra: str = ""
    kind: str = "acid"
    show: bool = True
    # Task 10 — learning-ladder map (filled by CONTENT_MAP below).
    concept_introduced: str = ""
    new_feature: str = ""
    difficulty: int = 1
    prerequisite: str = ""
    path: str = "reference"          # canonical | ladder | reference | supplement
    spectators: str = ""
    variant_molecular: str = ""      # optional second molecular form (hydrate)
    variant_note: str = ""


WORKED: list[Worked] = [
    Worked(
        "6.1", "KMnO₄ + Na₂SO₃, skāba vide", "L20 p.1; LEC P089, P138",
        "SO3^2- + H2O -> SO4^2- + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 5SO3^2- + 16H^+ + 5H2O -> 2Mn^2+ + 5SO4^2- + 8H2O + 10H^+",
        "2MnO4^- + 5SO3^2- + 6H^+ -> 2Mn^2+ + 5SO4^2- + 3H2O",
        "2KMnO4 + 3H2SO4 + 5Na2SO3 -> 3H2O + 5Na2SO4 + K2SO4 + 2MnSO4",
        "Skābā vidē permanganāts pieņem 5 e⁻; sulfīts atdod 2 e⁻. Elektronu mazākais kopīgais daudzkārtnis ir 10.",
        "",
    ),
    Worked(
        "6.2", "KMnO₄ + Na₂SO₃, neitrāla vide", "L20 p.1; LEC P096",
        "SO3^2- + H2O -> SO4^2- + 2H^+ + 2e^-",
        "MnO4^- + 2H2O + 3e^- -> MnO2 + 4OH^-",
        3, 2,
        "2MnO4^- + 3SO3^2- + 4H2O + 3H2O -> 2MnO2 + 8OH^- + 3SO4^2- + 6H^+",
        "2MnO4^- + 3SO3^2- + H2O -> 2MnO2 + 2OH^- + 3SO4^2-",
        "2KMnO4 + 3Na2SO3 + H2O -> 2MnO2 + 2KOH + 3Na2SO4",
        "6H⁺ + 6OH⁻ = 6H₂O; pēc ūdens saīsināšanas paliek 2OH⁻ un 1H₂O. Brūnais MnO₂ ir nogulsnes.",
        "",
    ),
    Worked(
        "6.3", "KMnO₄ + Na₂SO₃, bāziska vide", "L20 p.1; L21 IIc; LEC P098",
        "SO3^2- + 2OH^- -> SO4^2- + H2O + 2e^-",
        "MnO4^- + e^- -> MnO4^2-",
        1, 2,
        "2MnO4^- + SO3^2- + 2OH^- -> 2MnO4^2- + SO4^2- + H2O",
        "2MnO4^- + SO3^2- + 2OH^- -> 2MnO4^2- + SO4^2- + H2O",
        "2KMnO4 + 2NaOH + Na2SO3 -> 2Na2MnO4 + K2SO4 + H2O",
        "Bāziskā vidē permanganāts pieņem tikai 1 e⁻ un pāriet zaļajā manganātjonā MnO₄²⁻. Tā nav MnO₂ nogulsne (A12).",
        "",
    ),
    Worked(
        "6.4", "KMnO₄ + FeSO₄, skāba vide", "LEC §3.1; L20 p.2; L25 p.1",
        "Fe^2+ -> Fe^3+ + e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 1,
        "MnO4^- + 8H^+ + 5Fe^2+ -> Mn^2+ + 4H2O + 5Fe^3+",
        "MnO4^- + 8H^+ + 5Fe^2+ -> Mn^2+ + 4H2O + 5Fe^3+",
        "10FeSO4 + 2KMnO4 + 8H2SO4 -> 5Fe2(SO4)3 + 2MnSO4 + K2SO4 + 8H2O",
        "Šī ir permanganatometrijas pamatreakcija: 1 mols KMnO₄ atbilst 5 moliem Fe²⁺ (z = 5 pret z = 1).",
        "",
    ),
    Worked(
        "6.5", "KMnO₄ + KI, skāba vide", "L20 p.2",
        "2I^- -> I2 + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 10I^- -> 2Mn^2+ + 8H2O + 5I2",
        "2MnO4^- + 16H^+ + 10I^- -> 2Mn^2+ + 8H2O + 5I2",
        "2KMnO4 + 8H2SO4 + 10KI -> 2MnSO4 + 6K2SO4 + 8H2O + 5I2",
        "Jodīds tiek oksidēts līdz brīvam jodam; jods ir mazšķīstošs un atzīmēts ar ↓ tikai tad, ja izdalās.",
        "",
    ),
    Worked(
        "6.6", "KMnO₄ + NaNO₂, skāba vide", "L20 p.2",
        "NO2^- + H2O -> NO3^- + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 5NO2^- + 5H2O -> 2Mn^2+ + 8H2O + 5NO3^- + 10H^+",
        "2MnO4^- + 5NO2^- + 6H^+ -> 2Mn^2+ + 3H2O + 5NO3^-",
        "2KMnO4 + 3H2SO4 + 5NaNO2 -> 2MnSO4 + 3H2O + K2SO4 + 5NaNO3",
        "Nitrīts ir reducētājs, jo slāpeklis +3 pāriet +5. Skābā vidē nitrīts ir HONO/NO₂ formā; kursa vienādojums lieto NO₂⁻ kā mācību vienkāršojumu.",
        "",
    ),
    Worked(
        "6.7", "KMnO₄ + H₂O₂, skāba vide", "L20 p.2",
        "H2O2 -> O2 + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 5H2O2 -> 2Mn^2+ + 8H2O + 5O2 + 10H^+",
        "2MnO4^- + 5H2O2 + 6H^+ -> 2Mn^2+ + 8H2O + 5O2",
        "2KMnO4 + 3H2SO4 + 5H2O2 -> 2MnSO4 + 5O2 + 8H2O + K2SO4",
        "Šeit H₂O₂ ir reducētājs: skābeklis −1 → 0. Tajā pašā reakciju kopā H₂O₂ var būt arī oksidētājs (sk. 5.4).",
        "",
    ),
    Worked(
        "6.8", "KMnO₄ + H₂S, skāba vide", "L20 p.3",
        "H2S -> S + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 5H2S -> 2Mn^2+ + 8H2O + 5S + 10H^+",
        "2MnO4^- + 6H^+ + 5H2S -> 2Mn^2+ + 8H2O + 5S",
        "2KMnO4 + 5H2S + 3H2SO4 -> 2MnSO4 + 8H2O + 5S + K2SO4",
        "Sulfīds skābā vidē praktiski ir H₂S, nevis S²⁻. Tāpēc pusreakcijā lieto H₂S (A15).",
        "",
    ),
    Worked(
        "6.9", "KMnO₄ + H₂C₂O₄, skāba vide", "L20 p.3; D1",
        "H2C2O4 -> 2CO2 + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 5H2C2O4 -> 2Mn^2+ + 8H2O + 10CO2 + 10H^+",
        "2MnO4^- + 6H^+ + 5H2C2O4 -> 2Mn^2+ + 8H2O + 10CO2",
        "2KMnO4 + 5H2C2O4 + 3H2SO4 -> 2MnSO4 + 10CO2 + 8H2O + K2SO4",
        "Šo reakciju lieto KMnO₄ standartizācijai. Sildīšana 60–70 °C un Mn²⁺ autokatalīze ir prakses piezīme (D1), nevis stehiometrijas daļa.",
        "",
    ),
    Worked(
        "6.10", "KMnO₄ + H₃PO₃, skāba vide", "LEC self-test 2; L20 p.4; A14",
        "H3PO3 + H2O -> H3PO4 + 2H^+ + 2e^-",
        "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        5, 2,
        "2MnO4^- + 16H^+ + 5H3PO3 + 5H2O -> 2Mn^2+ + 8H2O + 5H3PO4 + 10H^+",
        "2MnO4^- + 6H^+ + 5H3PO3 -> 2Mn^2+ + 3H2O + 5H3PO4",
        "2KMnO4 + 5H3PO3 + 3H2SO4 -> 2MnSO4 + 5H3PO4 + K2SO4 + 3H2O",
        "Avotā lieto PO₃³⁻, kas šķīdumā nav reālā daļiņa: H₃PO₃ ir divvērtīgā molekula. Vienādojums ar PO₃³⁻ formāli balansējas, tāpēc atomu pārbaude vien to nepieķer (A14).",
        "",
    ),
    Worked(
        "6.11", "K₂Cr₂O₇ + FeSO₄, skāba vide", "L20 p.3",
        "Fe^2+ -> Fe^3+ + e^-",
        "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O",
        6, 1,
        "Cr2O7^2- + 14H^+ + 6Fe^2+ -> 2Cr^3+ + 6Fe^3+ + 7H2O",
        "Cr2O7^2- + 14H^+ + 6Fe^2+ -> 2Cr^3+ + 6Fe^3+ + 7H2O",
        "K2Cr2O7 + 6FeSO4 + 7H2SO4 -> Cr2(SO4)3 + 3Fe2(SO4)3 + 7H2O + K2SO4",
        "Dihromāts pieņem 6 e⁻, tāpēc attiecība pret Fe²⁺ ir 1:6.",
        "",
    ),
    Worked(
        "6.12", "K₂Cr₂O₇ + KNO₂, skāba vide", "L20 p.3",
        "NO2^- + H2O -> NO3^- + 2H^+ + 2e^-",
        "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O",
        3, 1,
        "Cr2O7^2- + 14H^+ + 3NO2^- + 3H2O -> 2Cr^3+ + 7H2O + 3NO3^- + 6H^+",
        "Cr2O7^2- + 8H^+ + 3NO2^- -> 2Cr^3+ + 4H2O + 3NO3^-",
        "K2Cr2O7 + 3KNO2 + 4H2SO4 -> Cr2(SO4)3 + K2SO4 + 3KNO3 + 4H2O",
        "Nitrīts atdod 2 e⁻; 6 un 2 mazākais kopīgais daudzkārtnis ir 6, tāpēc reizinātāji ir 3 un 1.",
        "",
    ),
    Worked(
        "6.13", "K₂Cr₂O₇ + KI, skāba vide", "L20 p.4",
        "2I^- -> I2 + 2e^-",
        "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O",
        3, 1,
        "Cr2O7^2- + 14H^+ + 6I^- -> 2Cr^3+ + 7H2O + 3I2",
        "Cr2O7^2- + 14H^+ + 6I^- -> 2Cr^3+ + 7H2O + 3I2",
        "K2Cr2O7 + 6KI + 7H2SO4 -> 7H2O + Cr2(SO4)3 + 4K2SO4 + 3I2",
        "Jodīda reizinātājs ir 6, jo 6 e⁻ / 2 e⁻ = 3; hroms paliek 1.",
        "",
    ),
    Worked(
        "6.14", "K₂Cr₂O₇ + Na₂SO₃, skāba vide", "L20 p.4",
        "SO3^2- + H2O -> SO4^2- + 2H^+ + 2e^-",
        "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O",
        3, 1,
        "Cr2O7^2- + 14H^+ + 3SO3^2- + 3H2O -> 2Cr^3+ + 7H2O + 3SO4^2- + 6H^+",
        "Cr2O7^2- + 8H^+ + 3SO3^2- -> 2Cr^3+ + 4H2O + 3SO4^2-",
        "K2Cr2O7 + 4H2SO4 + 3Na2SO3 -> 4H2O + Cr2(SO4)3 + K2SO4 + 3Na2SO4",
        "Sulfīts skābā vidē ir HSO₃⁻/SO₂·H₂O; SO₃²⁻ pieraksts ir kursa vienkāršojums (A15).",
        "",
    ),
    Worked(
        "6.15", "Zn + HNO₃ → N₂O", "LEC self-test 2; L20 p.4",
        "Zn -> Zn^2+ + 2e^-",
        "2NO3^- + 10H^+ + 8e^- -> N2O + 5H2O",
        8, 2,
        "2NO3^- + 10H^+ + 4Zn -> N2O + 5H2O + 4Zn^2+",
        "2NO3^- + 10H^+ + 4Zn -> N2O + 5H2O + 4Zn^2+",
        "10HNO3 + 4Zn -> 4Zn(NO3)2 + N2O + 5H2O",
        "Cinks atdod 2 e⁻, nitrāts pieņem 8 e⁻; tāpēc Zn reizinātājs ir 4, nitrāta pusreakcijai paliek 1, bet molekulārajā vienādojumā kopā ir 10 HNO₃.",
        "",
    ),
    Worked(
        "6.16", "KMnO₄ + KOH + Na₂SO₃", "LEC self-test 1",
        "SO3^2- + 2OH^- -> SO4^2- + H2O + 2e^-",
        "MnO4^- + e^- -> MnO4^2-",
        1, 2,
        "2MnO4^- + SO3^2- + 2OH^- -> 2MnO4^2- + SO4^2- + H2O",
        "2MnO4^- + SO3^2- + 2OH^- -> 2MnO4^2- + SO4^2- + H2O",
        "2KMnO4 + 2KOH + Na2SO3 -> 2K2MnO4 + Na2SO4 + H2O",
        "Bāziskā vidē produkts ir zaļais MnO₄²⁻; KOH gadījumā molekulārajā vienādojumā sanāk K₂MnO₄.",
        "",
    ),
    Worked(
        "6.17", "PbO₂ + Mn²⁺ koncentrētā HNO₃", "LEC P063; A3; D10",
        "Mn^2+ + 4H2O -> MnO4^- + 8H^+ + 5e^-",
        "PbO2 + 4H^+ + 2e^- -> Pb^2+ + 2H2O",
        2, 5,
        "5PbO2 + 20H^+ + 2Mn^2+ + 8H2O -> 5Pb^2+ + 10H2O + 2MnO4^- + 16H^+",
        "5PbO2 + 2Mn^2+ + 4H^+ -> 5Pb^2+ + 2MnO4^- + 2H2O",
        "",
        "Šis nav avota piemērs, bet tā paskaidrojums (Papildinājums). Ar darba E° = 1,46 V (CRC 1,455 V) PbO₂ standartapstākļos nav stiprāks par MnO₄⁻ (1,51 V); koncentrētā karstā HNO₃ [H⁺] ceļ PbO₂ potenciālu uz augšu. Tāpēc reakcija notiek, lai gan E° nav lielāks.",
        "Pie [H⁺] = 8 mol/L, [PbO₂] = [Pb²⁺] = 1: E = 1,46 + (0,0592/2)·lg(8⁴) = 1,567 V; ΔE pret MnO₄⁻ = 0,057 V.",
        kind="supp", show=False,
    ),
    Worked(
        "6.19", "H₂O₂ kā oksidētājs ar I⁻", "Papildinājums; LEC P151, P079",
        "2I^- -> I2 + 2e^-",
        "H2O2 + 2H^+ + 2e^- -> 2H2O",
        1, 1,
        "H2O2 + 2H^+ + 2I^- -> I2 + 2H2O",
        "H2O2 + 2H^+ + 2I^- -> I2 + 2H2O",
        "",
        "Šeit H₂O₂ ir oksidētājs, bet I⁻ — reducētājs. Tas ir papildinājums, kas parāda H₂O₂ abas lomas kopā ar 6.7, kur H₂O₂ ir reducētājs.",
        "E°(H₂O₂/H₂O) = 1,78 V > E°(I₂/I⁻) = 0,54 V.",
        kind="supp", show=False,
    ),
    Worked(
        "6.18", "MnO₂ + koncentrēta HCl", "LEC P148; D10",
        "2Cl^- -> Cl2 + 2e^-",
        "MnO2 + 4H^+ + 2e^- -> Mn^2+ + 2H2O",
        1, 1,
        "MnO2 + 4H^+ + 2Cl^- -> Mn^2+ + Cl2 + 2H2O",
        "MnO2 + 4H^+ + 2Cl^- -> Mn^2+ + Cl2 + 2H2O",
        "MnO2 + 4HCl -> MnCl2 + Cl2 + 2H2O",
        "E°(MnO₂/Mn²⁺) ≈ 1,23 V ir mazāks par E°(Cl₂/Cl⁻) 1,36 V, tomēr karsta koncentrēta HCl strādā: [H⁺] un [Cl⁻] maina potenciālus, Cl₂ aizplūst. Tas ir tas pats princips kā A13 un A3.",
        "",
        kind="supp", show=False,
    ),
]

# ---------------------------------------------------------------- Task 10 content map
# Every example gets: the concept it introduces, the one thing that is genuinely
# new, a difficulty (1 = canonical, 2 = one new feature, 3 = two features or a trap),
# its prerequisite, and where it lives in the learning path.
# canonical = the three media; ladder = one new feature each; reference = same pattern,
# different reagent; supplement = not in the source exercise set.
CONTENT_MAP: dict[str, dict[str, object]] = {
    "6.1": dict(concept="H⁺/H₂O saīsināšana",
                new="Skāba vide: MnO₄⁻ pieņem 5 e⁻, un H⁺ ar H₂O saīsinās — paliek 6 H⁺.",
                difficulty=1, prerequisite="6.1–6.2", path="canonical",
                spectators="K⁺, Na⁺, SO₄²⁻", kind="acid"),
    "6.2": dict(concept="MnO₂ un OH⁻",
                new="Neitrāla vide: produkts ir MnO₂(s), OH⁻ paliek labajā pusē, un daļa ūdens saīsinās.",
                difficulty=1, prerequisite="6.1", path="canonical",
                spectators="K⁺, Na⁺", kind="neutral"),
    "6.3": dict(concept="1 e⁻ līdz MnO₄²⁻",
                new="Bāziskā vide: MnO₄⁻ pieņem tikai 1 e⁻ un pāriet MnO₄²⁻; OH⁻ ir reaģents.",
                difficulty=1, prerequisite="6.1", path="canonical",
                spectators="K⁺, Na⁺", kind="base"),
    "6.4": dict(concept="Otrais reducētājs",
                new="Fe²⁺ atdod 1 e⁻, tāpēc MnO₄⁻ un Fe²⁺ attiecība ir 1:5 — tā ir titrēšanas stehiometrija.",
                difficulty=2, prerequisite="6.1", path="ladder",
                spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.5": dict(concept="Divatomu produkts",
                new="Jodīds oksidējas par I₂: pusreakcijā jau ir koeficients 2, tāpēc reizinātāji ir 5 un 2.",
                difficulty=2, prerequisite="6.1", path="reference",
                spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.6": dict(concept="Oksianjons kā reducētājs",
                new="Nitrīts atdod 2 e⁻ (N +3 → +5); pusreakcijā ūdens ir reaģents, nevis produkts.",
                difficulty=2, prerequisite="6.1", path="reference",
                spectators="K⁺, Na⁺, SO₄²⁻", kind="acid"),
    "6.7": dict(concept="Neitrāla molekula",
                new="H₂O₂ ir neitrāla molekula, kas atdod 2 e⁻ un pārvēršas O₂ gāzē.",
                difficulty=2, prerequisite="6.1", path="ladder",
                spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.8": dict(concept="Gāzveida reducētājs",
                new="Skābā vidē sulfīds ir H₂S molekula, nevis S²⁻; produkts S izdalās.",
                difficulty=2, prerequisite="6.1", path="reference",
                spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.9": dict(concept="Gāzes produkts",
                new="Skābeņskābe dod divas CO₂ molekulas uz vienu H₂C₂O₄ — divi C atomi pusreakcijā.",
                difficulty=2, prerequisite="6.1", path="ladder",
                spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.10": dict(concept="Daļiņu pārbaude",
                 new="H₃PO₃ ir molekula, nevis PO₃³⁻: vienādojums ar PO₃³⁻ formāli balansējas, bet tāda daļiņa šķīdumā neeksistē.",
                 difficulty=3, prerequisite="6.9", path="ladder",
                 spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.11": dict(concept="Cits oksidētājs",
                 new="Cr₂O₇²⁻ pieņem 6 e⁻ un satur divus Cr atomus; pusreakcijā ir 14 H⁺.",
                 difficulty=2, prerequisite="6.1", path="ladder",
                 spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.12": dict(concept="LCM 6",
                 new="Dihromāts (6 e⁻) un nitrīts (2 e⁻) dod reizinātājus 1 un 3.",
                 difficulty=2, prerequisite="6.11", path="reference",
                 spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.13": dict(concept="Dihromāts ar jodīdu",
                 new="6 I⁻ dod 3 I₂; dihromāta reizinātājs paliek 1.",
                 difficulty=2, prerequisite="6.11", path="reference",
                 spectators="K⁺, SO₄²⁻", kind="acid"),
    "6.14": dict(concept="Tas pats sulfīts",
                 new="Tas pats reducētājs kā 6.1. piemērā, bet cits oksidētājs — tieša salīdzināšana.",
                 difficulty=2, prerequisite="6.11", path="reference",
                 spectators="K⁺, Na⁺, SO₄²⁻", kind="acid"),
    "6.15": dict(concept="Metāls un nitrāts",
                 new="Metāls atdod elektronus, nitrāts pieņem; N₂O satur divus N atomus, un molekulārajā vienādojumā ir skatītājoni.",
                 difficulty=3, prerequisite="6.1", path="ladder",
                 spectators="NO₃⁻ (8 no 10)", kind="acid"),
    "6.16": dict(concept="Tā pati bāze, cits katjons",
                 new="Tā pati bāziskā reakcija ar KOH: mainās tikai skatītājoni, produkts ir K₂MnO₄.",
                 difficulty=2, prerequisite="6.3", path="reference",
                 spectators="K⁺, Na⁺", kind="base"),
    "6.17": dict(concept="Apgrieztais virziens",
                 new="PbO₂ oksidē Mn²⁺ tikai ļoti koncentrētā HNO₃; piemērs paliek jonu formā.",
                 difficulty=3, prerequisite="4.4", path="supplement",
                 spectators="", kind="acid"),
    "6.18": dict(concept="Koncentrēta skābe",
                 new="Cl⁻ oksidējas par Cl₂, lai gan E°(MnO₂/Mn²⁺) ir zemāks par E°(Cl₂/Cl⁻).",
                 difficulty=3, prerequisite="4.4", path="supplement",
                 spectators="Cl⁻ (2 no 4)", kind="acid"),
    "6.19": dict(concept="H₂O₂ otrā loma",
                 new="Šeit H₂O₂ ir oksidētājs, nevis reducētājs; I⁻ ir reducētājs.",
                 difficulty=2, prerequisite="6.7", path="supplement",
                 spectators="", kind="acid"),
}

for _w in WORKED:
    _m = CONTENT_MAP[_w.id]
    _w.concept_introduced = str(_m["concept"])
    _w.new_feature = str(_m["new"])
    _w.difficulty = int(_m["difficulty"])
    _w.prerequisite = str(_m["prerequisite"])
    _w.path = str(_m["path"])
    _w.spectators = str(_m["spectators"])
    _w.kind = str(_m["kind"])
    _w.show = _w.path != "supplement"

# The heptahydrate variant of the titration equation (Task 10.A: spectator ions + hydrate).
_W64 = next(w for w in WORKED if w.id == "6.4")
_W64.variant_molecular = (
    "10FeSO4.7H2O + 2KMnO4 + 8H2SO4 -> 5Fe2(SO4)3 + 2MnSO4 + K2SO4 + 78H2O"
)
_W64.variant_note = (
    "Ja sāls ir FeSO₄·7H₂O, kristālūdens paliek vienādojumā: 70 H₂O no hidrāta "
    "+ 8 H₂O, kas rodas reakcijā, = 78 H₂O labajā pusē. Koncentrācija nemainās; "
    "mainās tikai masa, ko svēr."
)

assert sum(1 for w in WORKED if w.path == "canonical") == 3
assert sum(1 for w in WORKED if w.path == "ladder") == 6
assert sum(1 for w in WORKED if w.path == "reference") == 7
assert sum(1 for w in WORKED if w.path == "supplement") == 3
assert set(CONTENT_MAP) == {w.id for w in WORKED}

LADDER_ORDER = ["6.4", "6.7", "6.9", "6.11", "6.15", "6.10"]
CANONICAL_ORDER = ["6.1", "6.2", "6.3"]

WORKED_BY_ID = {w.id: w for w in WORKED}

# ---------------------------------------------------------------- three media (Task 11)
# Single source for chapter 7: the prediction grid, the figure, the drill, the
# protocol table and the conclusion answers all read this list. Electron counts and
# E° come from COUPLES; half-reactions come from WORKED (already balance-checked).
@dataclass(frozen=True)
class Medium:
    key: str            # acid | neutral | base
    label: str          # skāba
    added: str          # H₂SO₄
    product: str        # Mn²⁺ (display form)
    product_name: str   # mangāns(II) jons
    colour: str         # bezkrāsains
    colour_key: str     # perm | clear | green | brown
    pattern: str        # raksts, kas paliek melnbalts
    electrons: int
    couple: str         # COUPLES id → E° and z
    worked: str         # WORKED id → verified half-reaction
    what: str           # what the half-reaction does
    why: str            # why this product (short, used in the table)
    see: str            # what you observe and why
    protocol: str       # wording for the lab notebook
    observation: str    # full observation sentence
    nernst_tail: str    # right-hand side after "E = E° + "
    exponent: str       # H⁺/OH⁻ exponent shown in the table


MEDIA: list[Medium] = [
    Medium(
        key="acid", label="skābā", added="H₂SO₄",
        product="Mn²⁺", product_name="mangāns(II) jons",
        colour="bezkrāsains", colour_key="clear",
        pattern="tukšs lauks ar raustītu virsmu",
        electrons=5, couple="mno4h", worked="6.1",
        what="Permanganāts pieņem 5 elektronus un reducējas līdz Mn²⁺; skābeklis paliek ūdenī.",
        why="Cēloņu kāpa: pusreakcijā ir astoņi H⁺, tāpēc Nernsta koeficientā [H⁺] ir 8. pakāpē; pie augsta skābuma tas ceļ E, un pie [H⁺] = 1 mol/L E° = 1,51 V. Reaģents H⁺ ļauj reducēšanās iet līdz zemākajai iespējamai pakāpei Mn²⁺ (5 e⁻). Mn²⁺ ir šķīstošs un bezkrāsains, tāpēc violetā krāsa izzūd bez nogulsnēm.",
        see="Mn²⁺ ir bezkrāsains un šķīstošs, tāpēc violetā krāsa izzūd bez nogulsnēm.",
        protocol="šķīdums kļuva bezkrāsains",
        observation="violetā krāsa izzūd; šķīdums kļūst bezkrāsains, ja Na₂SO₃ ir pietiekami daudz",
        nernst_tail="(0,0592/5)·lg([MnO₄⁻][H⁺]⁸/[Mn²⁺])",
        exponent="8 (H⁺)",
    ),
    Medium(
        key="neutral", label="neitrālā", added="H₂O",
        product="MnO₂", product_name="mangāna(IV) oksīds",
        colour="brūnas nogulsnes", colour_key="brown",
        pattern="punkti, nogulsnes apakšā",
        electrons=3, couple="mno4n", worked="6.2",
        what="Permanganāts pieņem 3 elektronus; produkts ir MnO₂, kas ūdenī nešķīst.",
        why="Cēloņu kāpa: neitrālā vidē H⁺ nav pietiekami, lai reducēšanās aizietu līdz Mn²⁺, tāpēc reakcija apstājas pie Mn(IV) (3 e⁻; LEC P095–P096). Līdzsvarojot pusreakciju, rodas 4 OH⁻, tāpēc Nernsta koeficientā ir [OH⁻]⁴, nevis [H⁺]⁸. MnO₂ nešķīst, tāpēc izgulsnējas uzreiz un nogulsnes aizsedz šķīdumu.",
        see="Veidojas brūnas nogulsnes; šķīdums virs tām var palikt brūngans. Nogulsnes aizsedz beigu punktu.",
        protocol="izveidojās brūnas nogulsnes",
        observation="veidojas brūnas MnO₂ nogulsnes; šķīdums var palikt brūngans",
        nernst_tail="(0,0592/3)·lg([MnO₄⁻]/[OH⁻]⁴)",
        exponent="4 (OH⁻)",
    ),
    Medium(
        key="base", label="bāziskā", added="NaOH",
        product="MnO₄²⁻", product_name="manganāts(VI)",
        colour="zaļš", colour_key="green",
        pattern="vertikālas līnijas",
        electrons=1, couple="mno4b", worked="6.3",
        what="Permanganāts pieņem tikai vienu elektronu; produkts ir MnO₄²⁻.",
        why="Cēloņu kāpa: bāziskā vidē permanganāta spēja pieņemt elektronus ir vēl mazāka (E° = 0,56 V), un pusreakcijā nav ne H⁺, ne OH⁻, ne H₂O (LEC P097–P098). Tāpēc Nernsta koeficientā nav pH pakāpes, un MnO₄⁻ pieņem tikai vienu elektronu. Produkts ir MnO₄²⁻ — manganāts, kas atšķiras no permanganāta gan formulā, gan krāsā (zaļa, nevis violets).",
        see="MnO₄²⁻ ir šķīstošs un zaļš; šķīdums paliek dzidrs.",
        protocol="šķīdums kļuva zaļš",
        observation="šķīdums kļūst zaļš; veidojas MnO₄²⁻, nevis MnO₂",
        nernst_tail="0,0592·lg([MnO₄⁻]/[MnO₄²⁻])",
        exponent="0",
    ),
]

MEDIA_BY_KEY = {m.key: m for m in MEDIA}

for _m in MEDIA:
    _c = COUPLE_BY_ID[_m.couple]
    assert _c.z == _m.electrons, f"electron count mismatch in {_m.key}"
    assert _m.worked in WORKED_BY_ID, f"unknown worked example {_m.worked}"
    assert _m.product == _c.red, f"product mismatch in {_m.key}: {_m.product} vs {_c.red}"


EQUATIONS: list[tuple[str, str]] = []


def _add_eq(name: str, eq: str) -> None:
    if eq:
        EQUATIONS.append((name, eq))


for w in WORKED:
    _add_eq(f"{w.id} oxidation half", w.ox_half)
    _add_eq(f"{w.id} reduction half", w.red_half)
    _add_eq(f"{w.id} uncancelled", w.uncancelled)
    _add_eq(f"{w.id} ionic", w.ionic)
    _add_eq(f"{w.id} molecular", w.molecular)
    if w.variant_molecular:
        _add_eq(f"{w.id} molecular variant", w.variant_molecular)

EXTRA_EQUATIONS = [
    ("[supp] manganate disproportionation", "3MnO4^2- + 4H^+ -> 2MnO4^- + MnO2 + 2H2O"),
    ("[supp] thiosulfate with iodine", "I2 + 2S2O3^2- -> 2I^- + S4O6^2-"),
    ("[supp] SO2 comproportionation", "SO2 + 2H2S -> 3S + 2H2O"),
    ("[supp] O2 with hydronium", "O2 + 4H3O^+ + 4e^- -> 6H2O"),
    ("[supp] H2O2 oxidation half, basic", "H2O2 + 2OH^- -> 2H2O + O2 + 2e^-"),
    ("[supp] NO2- oxidation half, basic", "NO2^- + 2OH^- -> H2O + NO3^- + 2e^-"),
    ("[supp] NO2- reduction half, basic", "NO2^- + H2O + e^- -> 2OH^- + NO"),
    ("[supp] NAD+ reduction", "NAD^+ + H3O^+ + 2e^- -> NADH + H2O"),
    ("[supp] FAD reduction", "FAD + 2H3O^+ + 2e^- -> FADH2 + 2H2O"),
    ("[supp] H2S to sulfur", "H2S -> S + 2H^+ + 2e^-"),
    ("[supp] sulfide to sulfur", "S^2- -> S + 2e^-"),
    ("[supp] Fe2+ oxidation", "Fe^2+ -> Fe^3+ + e^-"),
    ("[supp] oxalate half", "H2C2O4 -> 2CO2 + 2H^+ + 2e^-"),
    ("[supp] H3PO3 half", "H3PO3 + H2O -> H3PO4 + 2H^+ + 2e^-"),
    ("[supp] Cr2O7/Cl- threshold", "Cr2O7^2- + 14H^+ + 6Cl^- -> 2Cr^3+ + 7H2O + 3Cl2"),
    ("[supp] MnO4 + Fe2+", "MnO4^- + 8H^+ + 5Fe^2+ -> Mn^2+ + 4H2O + 5Fe^3+"),
    ("[supp] KMnO4 oxalate molecular", "2KMnO4 + 5H2C2O4 + 3H2SO4 -> 2MnSO4 + 10CO2 + 8H2O + K2SO4"),
    ("[supp] FeSO4 heptahydrate dissolution", "FeSO4.7H2O -> Fe^2+ + SO4^2- + 7H2O"),
    ("[supp] Mohr hexahydrate dissolution", "(NH4)2Fe(SO4)2.6H2O -> 2NH4^+ + Fe^2+ + 2SO4^2- + 6H2O"),
    ("[supp] Ag+ + Cl- precipitation", "Ag^+ + Cl^- -> AgCl"),
    ("[supp] Cl2 reduction half", "Cl2 + 2e^- -> 2Cl^-"),
    ("[supp] Fe3+ reduction half", "Fe^3+ + e^- -> Fe^2+"),
]
EQUATIONS.extend(EXTRA_EQUATIONS)

# --- F07: static review sheet selection (lean alternative; no analytics) ---
# Deterministic, reviewable selection: six recall prompts spanning kinds
# (cloze/calc/explain/spot) and chapters 1–11, three ionic equations
# spanning skāba/neitrāla/bāziska media (6.1–6.3 share the SO₃²⁻ substrate,
# so the medium decides the product). Key equations must exist in EQUATIONS;
# the balancing skeleton is the same equation with stoichiometric
# coefficients removed, so the skeleton cannot invent species.
REVIEW_SHEET_PROMPT_PIDS: tuple[str, ...] = (
    "C01-cloze", "C37-calc", "C41-explain",
    "C81-cloze", "C131-explain", "C170-spot",
)
REVIEW_SHEET_EQUATION_IDS: tuple[str, ...] = ("6.1", "6.2", "6.3")


def strip_coeffs(equation: str) -> str:
    """Skeleton view of an ASCII equation: drop leading integer coefficients
    on species tokens only.

    Internal digits survive (Cr2O7, H2O, ^2-), so the skeleton names exactly
    the species of the balanced registry equation. Whitespace is normalized.
    """
    out: list[str] = []
    for chunk in re.split(r"(->)", equation.strip()):
        if chunk == "->":
            out.append("->")
        else:
            tokens = [re.sub(r"^\d+", "", t) for t in chunk.split()]
            out.append(" ".join(tokens))
    return " ".join(out)


# ---------------------------------------------------------------- tasks
# Results are computed; text is rendered by build_master.py.
TASK = {
    "l25": {
        "cK": C.l25_cK, "titres": C.l25_titres, "v": C.l25_v,
        "val": C.l25_val, "vflask": C.l25_vflask,
        "cFe": C.l25_cFe, "nflask": C.l25_nflask, "m": C.l25_m,
        "m_hepta": C.l25_m_hepta,
        "rule": (
            "c(KMnO₄) dota ar 4 zīmīgajiem cipariem (0,0200); titri līdz 0,01 mL; "
            "c un m ziņo ar 4 zīmīgajiem; nenoapaļoti starplielumi."
        ),
    },
    "lec31": {
        "cK": 0.024, "v": 11.0, "val": 10.0, "vflask": 0.1,
        "M_given": C.lec_M_given, "M_hexa": C.lec_M_hexa,
        "c": C.lec_c, "c_printed": C.lec_c_printed,
        "m_anhydrous": C.lec_m_anhydrous, "m_hexahydrate": C.lec_m_hexahydrate,
        "m_printed": C.lec_m_printed,
        "rule": (
            "Dati 0,024 un 11 ar 2–3 zīmīgajiem; nenoapaļota c = 0,132 mol/L; "
            "m = 3,75 g (3 zīm.); ar 2 zīmīgajiem datiem 3,7 g."
        ),
    },
    "st1": {
        "c_acid": 0.025, "v_acid": 25.0, "vK": 3.75,
        "c": C.st1_c, "m": C.st1_m_100, "normality": C.st1_normality,
        "rule": (
            "c = 0,0667 mol/L (3–4 zīm.); m = 1,05 g; normālā = 0,333 ekv/L "
            "(vēsturiska, tikai jo uzdevums to prasa)."
        ),
    },
    "st2": {
        "cK": 0.02, "vK": 11.36, "val": 20.0,
        "c": C.st2_c, "gL": C.st2_gL,
        "rule": "c = 0,0568 mol/L; ρ_m = 8,63 g/L ar M(FeSO₄) = 151,91 g/mol (3 zīm.).",
    },
    "st3": {
        "cK": 0.004, "vK": 20.0, "val": 10.0, "vflask": 100.0,
        "sample": 2.00, "rho": 1.05,
        "nK": C.st3_nK, "nH2O2_10": C.st3_nH2O2_10,
        "nH2O2_100": C.st3_nH2O2_100, "m": C.st3_m, "w": C.st3_w,
        "rule": "w = 3,24 % (3 zīmīgie cipari); M(H₂O₂) = 34,0147 g/mol.",
    },
    "st4": {
        "cK": 0.022, "vK": 7.98, "val": 25.0, "vflask": 500.0, "rho": 1.0,
        "nK": C.st4_nK, "nFe25": C.st4_nFe25, "nFe500": C.st4_nFe500,
        "mFe": C.st4_mFe, "w": C.st4_w,
        "rule": (
            "Nenoapaļots w = 0,196 %; ar 2 zīmīgajiem → 0,20 % "
            "(avota 0,19 % nogriež pēdējo ciparu — A18)."
        ),
    },
}


# ---------------------------------------------------------------- number inventory (Task 05)
# kind: measured | given | computed | source_quoted
@dataclass(frozen=True)
class NumberEntry:
    id: str
    mark: str                 # LEC1 | LEC2 | LEC3 | LEC4 | L25 | lec31 | nernst | pHcross | dGlgK | titre | other
    symbol: str
    raw: float
    reported: str             # Latvian text without unit
    unit_key: str
    kind: str                 # measured | given | computed | source_quoted
    sig_figs: int | None
    decimals: int | None
    rule: str
    source_quoted: str = ""   # if kind=source_quoted, the source string
    section: str = ""

    @property
    def unit(self) -> str:
        return UNITS[self.unit_key]["unit"]

    @property
    def reported_with_unit(self) -> str:
        u = self.unit
        return f"{self.reported}{NBSP}{u}" if u else self.reported


def _num(
    id_: str, mark: str, symbol: str, raw: float, unit_key: str, kind: str, rule: str,
    *, sig_figs: int | None = None, decimals: int | None = None,
    source_quoted: str = "", section: str = "",
    reported: str | None = None,
) -> NumberEntry:
    if reported is None:
        if decimals is not None:
            reported = format_value(raw, unit_key, decimals=decimals, with_unit=False)
        elif sig_figs is not None:
            reported = format_value(raw, unit_key, sig_figs=sig_figs, with_unit=False, keep_zeros=True)
        else:
            reported = format_value(raw, unit_key, with_unit=False)
    return NumberEntry(
        id_, mark, symbol, raw, reported, unit_key, kind, sig_figs, decimals, rule,
        source_quoted=source_quoted, section=section,
    )


NUMBERS: list[NumberEntry] = [
    # ---- L25 illustrative titration ----
    _num("l25.cK", "L25", "c(KMnO₄)", C.l25_cK, "c", "given",
         TASK["l25"]["rule"], decimals=4, section="9.4"),
    _num("l25.Vbar", "L25", "V̄", C.l25_v, "V_mL", "computed",
         TASK["l25"]["rule"], decimals=2, section="9.4"),
    _num("l25.val", "L25", "V(alikvots)", C.l25_val, "V_mL", "given",
         TASK["l25"]["rule"], decimals=2, section="9.4"),
    _num("l25.vflask", "L25", "V(mērkolba)", C.l25_vflask * 1000, "V_mL", "given",
         TASK["l25"]["rule"], decimals=1, section="9.4"),
    _num("l25.cFe", "L25", "c(Fe²⁺)", C.l25_cFe, "c", "computed",
         TASK["l25"]["rule"], decimals=4, section="9.4"),
    _num("l25.nflask", "L25", "n(FeSO₄) 100 mL", C.l25_nflask, "n", "computed",
         TASK["l25"]["rule"], sig_figs=4, section="9.4"),
    _num("l25.m", "L25", "m(FeSO₄)", C.l25_m, "m", "computed",
         TASK["l25"]["rule"], decimals=3, section="9.4"),
    _num("l25.m_hepta", "L25", "m(FeSO₄·7H₂O)", C.l25_m_hepta, "m", "computed",
         "Hidrāta izvēle maina masu, nevis koncentrāciju.", decimals=3, section="9.4"),
    # ---- LEC §3.1 ----
    _num("lec31.c", "lec31", "c(Mora sāls)", C.lec_c, "c", "computed",
         TASK["lec31"]["rule"], decimals=3, section="9.5"),
    _num("lec31.c_src", "lec31", "c(Mora sāls) avots", C.lec_c_printed, "c", "source_quoted",
         TASK["lec31"]["rule"], decimals=2, source_quoted="0,13 M", section="9.5"),
    _num("lec31.m", "lec31", "m bezūdens", C.lec_m_anhydrous, "m", "computed",
         TASK["lec31"]["rule"], sig_figs=3, section="9.5"),
    _num("lec31.m_2sf", "lec31", "m bezūdens (2 zīm.)", C.lec_m_anhydrous, "m", "computed",
         "Ar 2 zīmīgajiem datiem atbilde ir 3,7 g.", sig_figs=2, section="9.5"),
    _num("lec31.m_raw", "lec31", "m bezūdens (nenoapaļots)", C.lec_m_anhydrous, "m", "computed",
         TASK["lec31"]["rule"], decimals=4, section="9.5"),
    _num("lec31.m_hexa", "lec31", "m heksahidrāts", C.lec_m_hexahydrate, "m", "computed",
         TASK["lec31"]["rule"], sig_figs=3, section="9.5"),
    _num("lec31.m_src", "lec31", "m avots", C.lec_m_printed, "m", "source_quoted",
         "Avota 3,69 g no priekšlaicīgas noapaļošanas.", decimals=2,
         source_quoted="3,69 g", section="9.5"),
    # ---- LEC self-test 1 ----
    _num("st1.c", "LEC1", "c(KMnO₄)", C.st1_c, "c", "computed",
         TASK["st1"]["rule"], decimals=4, section="12.4.1"),
    _num("st1.c_rep", "LEC1", "c(KMnO₄) ziņots", C.st1_c, "c", "computed",
         TASK["st1"]["rule"], sig_figs=3, section="12.4.1"),
    _num("st1.m", "LEC1", "m(KMnO₄) 100 mL", C.st1_m_100, "m", "computed",
         TASK["st1"]["rule"], sig_figs=3, section="12.4.1"),
    _num("st1.N", "LEC1", "normālā c(KMnO₄)", C.st1_normality, "N", "computed",
         TASK["st1"]["rule"], decimals=3, section="12.4.1"),
    _num("st1.c_src", "LEC1", "c avots (molārā kā „normālā”)", 0.067, "c", "source_quoted",
         "Avots dod 0,067 M (= mol/L), bet uzdevums prasa normālo.", decimals=3,
         source_quoted="0,067 M", section="12.4.1"),
    # ---- LEC self-test 2 ----
    _num("st2.c", "LEC2", "c(Fe²⁺)", C.st2_c, "c", "computed",
         TASK["st2"]["rule"], decimals=4, section="12.4.2"),
    _num("st2.gL", "LEC2", "ρ_m(FeSO₄)", C.st2_gL, "rho_m", "computed",
         TASK["st2"]["rule"], sig_figs=3, section="12.4.2"),
    _num("st2.gL_raw", "LEC2", "ρ_m(FeSO₄) nenoapaļots", C.st2_gL, "rho_m", "computed",
         "Nenoapaļots 0,0568 · 151,91 = 8,628488; ziņots ar 3 zīmīgajiem cipariem "
         "(8,63 g/L). Reizināšanas blokā rādīts ar 3 decimāldaļām (8,628).",
         decimals=3, section="12.4.2"),
    _num("st2.gL_src", "LEC2", "ρ_m avots", 8.64, "rho_m", "source_quoted",
         "Avota 8,64 g/L no M = 152.", decimals=2, source_quoted="8,64 g/L", section="12.4.2"),
    # ---- LEC self-test 3 ----
    _num("st3.w", "LEC3", "w(H₂O₂)", C.st3_w, "w", "computed",
         TASK["st3"]["rule"], decimals=2, section="12.4.3"),
    _num("st3.w_raw", "LEC3", "w(H₂O₂) nenoapaļots", C.st3_w, "w", "computed",
         TASK["st3"]["rule"], decimals=3, section="12.4.3"),
    # ---- LEC self-test 4 ----
    _num("st4.w_raw", "LEC4", "w(Fe) nenoapaļots", C.st4_w, "w", "computed",
         TASK["st4"]["rule"], decimals=3, section="12.4.4"),
    _num("st4.w", "LEC4", "w(Fe)", C.st4_w, "w", "computed",
         TASK["st4"]["rule"], sig_figs=2, section="12.4.4"),
    _num("st4.w_src", "LEC4", "w avots", 0.19, "w", "source_quoted",
         "Avota 0,19 % nogriež; pareizi noapaļojot 0,20 % (A18).", decimals=2,
         source_quoted="0,19 %", section="12.4.4"),
    # ---- Nernst / pH crossing / ΔG ----
    _num("cross.h", "pHcross", "[H⁺] krustpunkts", C.cross_h, "c", "computed",
         "E(Cr₂O₇²⁻) = E(Cl₂) → [H⁺] ≈ 1,65 mol/L (2–3 zīm.).", sig_figs=3, section="4.4"),
    _num("cross.ph", "pHcross", "pH krustpunkts", C.cross_ph, "pH", "computed",
         "pH ≈ −0,22.", decimals=2, section="4.4"),
    _num("nernst.const", "nernst", "0,0592 V", NERNST, "E", "given",
         "Viena Nernsta konstante visam dokumentam pie 298 K (25 °C).", decimals=4, section="3"),
    _num("nernst.exact", "nernst", "2,303·RT/F", C.nernst_exact, "E", "computed",
         "2,303·R·T/F pie T = 298,15 K; rāda vienreiz, tad noapaļo uz 0,0592 (A22).",
         decimals=5, section="3"),
    _num("mn.ph0", "nernst", "E(Mn) pH 0", C.mn_ph0, "E", "computed",
         "E = 1,51 + (0,0592/5)·lg(1) = 1,510 V.", decimals=3, section="3.4"),
    _num("mn.ph3", "nernst", "E(Mn) pH 3", C.mn_ph3, "E", "computed",
         "lg([H⁺]⁸) = −24; korekcija (0,0592/5)·(−24) = −0,284 V → 1,226 V.",
         decimals=3, section="3.4"),
    _num("mn.ph7", "nernst", "E(Mn) pH 7 (formāli)", C.mn_ph7, "E", "computed",
         "Formāla vērtība; Mn²⁺ nav dominējošā forma bāziskā / neitrālā vidē.",
         decimals=3, section="3.4"),
    _num("mn.corr3", "nernst", "korekcija pH 3", C.mn_corr_ph3, "E", "computed",
         "(0,0592/5)·(−24).", decimals=3, section="3.4"),
    _num("mn.slope", "nernst", "slīpums V/pH", C.mn_slope, "E", "computed",
         "(0,0592/5)·8 = 0,0947 V uz pH vienību.", decimals=4, section="3.4"),
    # T12: Cr₂O₇²⁻/Cr³⁺ slope, displayed on the condition-labeled 3.1. attēls;
    # recomputed by verify_numbers.py from C.cr_slope like mn.slope.
    _num("cr.slope", "nernst", "slīpums V/pH (Cr₂O₇²⁻/Cr³⁺)", C.cr_slope, "E", "computed",
         "(0,0592/6)·14 = 0,138 V uz pH vienību.", decimals=3, section="3.4"),
    # T06 (Task 26): ratio half of the Nernst correction — worked example 3.4.
    _num("mn.ratio10.corr", "nernst", "korekcija [Ox]/[Red] = 10", C.mn_ratio10_corr, "E", "computed",
         "(0,0592/5)·lg([MnO₄⁻]/[Mn²⁺]) pie attiecības 10/1; lg 10 = 1.", decimals=4, section="3.4"),
    _num("mn.ratio10.E", "nernst", "E(Mn) pie attiecības 10", C.mn_ratio10_E, "E", "computed",
         "E = 1,510 + 0,0118 = 1,522 V pie [MnO₄⁻]/[Mn²⁺] = 10.", decimals=3, section="3.4"),
    # T06 4.2 counterexample: E° intensitāte — reizinātājs nereizina E° (M20).
    _num("fe.e0", "potentials", "E°(Fe³⁺/Fe²⁺)", C.fe_e0, "E", "given",
         "Kursa tabulas vērtība 0,77 V (LEC 2. tabula).", decimals=2, section="4.2"),
    _num("fe.e0.double", "potentials", "2·E°(Fe³⁺/Fe²⁺) — kļūda", C.fe_e0_double, "E", "computed",
         "Apgalvojuma piemērs: 2·0,77 = 1,54 V nav nekur lietojama vērtība (M20).", decimals=2, section="4.2"),
    _num("eprime.h2", "nernst", "E°′(H⁺/H₂)", C.h2_ph7, "E", "computed",
         "E°′ = 0 − 0,0592·(2/2)·7; pH 7.", decimals=3, section="2; 8.1"),
    _num("eprime.o2", "nernst", "E°′(O₂/H₂O)", C.o2_ph7, "E", "computed",
         "E°′ = 1,229 − 0,0592·(4/4)·7 ≈ 0,815 V (ziņots).", decimals=3, section="2; 8.1"),
    _num("eprime.o2_rep", "nernst", "E°′(O₂) Campbell", C.o2_eprime_reported, "E", "given",
         "Campbell tabula +0,815 V (pH 7).", decimals=3, section="8.1"),
    _num("eprime.nad", "nernst", "E°′(NAD⁺/NADH) Campbell", C.nad_eprime, "E", "given",
         "Campbell izraksta vērtība −0,32 V (pH 7,0); T izrakstā nenosaukta.",
         decimals=2, section="8.1; 8.2"),
    _num("pbo2.8m", "nernst", "E(PbO₂) pie 8 mol/L", C.pbo2_at_8m, "E", "computed",
         "E = 1,46 + (0,0592/2)·lg(8⁴); 3 decimāldaļas.", decimals=3, section="4.4"),
    _num("pbo2.8m_crc", "nernst", "E(PbO₂) pie 8 mol/L (CRC 1,455)", C.pbo2_at_8m_crc, "E", "computed",
         "E = 1,455 + (0,0592/2)·lg(8⁴); tā pati formula ar CRC vērtību.", decimals=3, section="4.4"),
    _num("pbo2.8m_src", "nernst", "E(PbO₂) pie 8 mol/L (avota 1,80 V)", C.pbo2_at_8m_src, "E", "computed",
         "1,80 + (0,0592/2)·lg(8⁴) = 1,907 V; avota vērtība tikai salīdzinājumam.", decimals=3, section="4.4"),
    _num("pbo2.dE8m", "nernst", "ΔE pie 8 mol/L", C.pbo2_dE_at_8m, "E", "computed",
         "E(PbO₂) − E(MnO₄⁻) no reģistra nenoapaļotiem lielumiem; ziņots ar 3 decimāldaļām.", decimals=3, section="4.4"),
    _num("pbo2.dE8m_crc", "nernst", "ΔE pie 8 mol/L (CRC 1,455)", C.pbo2_dE_at_8m_crc, "E", "computed",
         "Tā pati starpība ar CRC bāzes vērtību; ziņots ar 3 decimāldaļām.", decimals=3, section="4.4"),
    _num("pbo2.dE8m_src", "nernst", "ΔE pie 8 mol/L (avota 1,80 V)", C.pbo2_dE_at_8m_src, "E", "computed",
         "Starpība ar avota vērtību; virziens ir pretējs; ziņots ar 3 decimāldaļām.", decimals=3, section="4.4"),
    _num("mno4.e8m", "nernst", "E(MnO₄⁻) pie 8 mol/L", C.mno4_at_8m, "E", "computed",
         "1,51 + (0,0592/5)·lg(8⁸) = 1,595 V.", decimals=3, section="4.4"),
    _num("pbo2.slope", "nernst", "PbO₂ slīpums, V/pH", C.pbo2_slope, "E", "computed",
         "s = −0,0592·4/2 = −0,1184 V/pH.", decimals=4, section="4.4"),
    _num("pbo2.dslope", "nernst", "Slīpumu starpība, V/pH", C.pbo2_dslope, "E", "computed",
         "−0,1184 − (−0,0947) = −0,0237 V/pH; slīpumi gandrīz kompensējas.", decimals=4, section="4.4"),
    _num("pbo2.e_diff", "nernst", "E° starpība 1,46 pret 1,455 V", C.pbo2_working - C.pbo2_crc, "E", "computed",
         "1,46 − 1,455 = 0,005 V; pārāk maza, lai mainītu secinājumu.", decimals=3, section="4.4"),
    _num("pbo2.cross_ph", "nernst", "pH pie ΔE = 0 (abas korekcijas)", C.pbo2_cross_ph, "pH", "computed",
         "−(−0,05)/(−0,02368) = −2,11; ārpus reālā diapazona.", decimals=2, section="4.4"),
    _num("pbo2.dslope_abs", "nernst", "|slīpumu starpība|, V/pH", abs(C.pbo2_dslope), "E", "computed",
         "0,1184 − 0,0947 = 0,0237 V/pH; tik lēni ΔE mainās ar pH.", decimals=4, section="4.4"),
    _num("pbo2.cross_h", "nernst", "[H⁺] pie ΔE = 0 (abas korekcijas)", C.pbo2_cross_h, "c", "computed",
         "pH = −(−0,05)/(−0,02368) = −2,11 → [H⁺] = 129 mol/L; nereāli.", sig_figs=3, section="4.4"),
    _num("pbo2.e15m", "nernst", "E(PbO₂) pie 15 mol/L HNO₃", C.pbo2_at_15m, "E", "computed",
         "1,46 + (0,0592/2)·lg(15⁴) = 1,599 V.", decimals=3, section="4.4"),
    _num("mno4.e15m", "nernst", "E(MnO₄⁻) pie 15 mol/L HNO₃", C.mno4_at_15m, "E", "computed",
         "1,51 + (0,0592/5)·lg(15⁸) = 1,621 V.", decimals=3, section="4.4"),
    _num("pbo2.dE15m", "nernst", "ΔE pie 15 mol/L HNO₃", C.pbo2_dE_at_15m, "E", "computed",
         "E(PbO₂) − E(MnO₄⁻) no reģistra nenoapaļotiem lielumiem; ziņots ar 3 decimāldaļām.", decimals=3, section="4.4"),
    _num("pbo2.dE15m_crc", "nernst", "ΔE pie 15 mol/L HNO₃ (CRC 1,455)", C.pbo2_dE_at_15m_crc, "E", "computed",
         "Tā pati starpība ar CRC bāzes vērtību; ziņots ar 3 decimāldaļām.", decimals=3, section="4.4"),
    _num("pbo2.ratio15", "nernst", "[MnO₄⁻]/[Mn²⁺] pie ΔE = 0, 15 mol/L", C.pbo2_ratio15, "ratio", "computed",
         "lg r = (−0,05 + 0,0237·1,176)/(0,0592/5) = −1,87 → r = 1,3·10⁻².", sig_figs=2, section="4.4"),
    _num("pbo2.ratio15_crc", "nernst", "[MnO₄⁻]/[Mn²⁺] pie ΔE = 0, 15 mol/L (CRC)", C.pbo2_ratio15_crc, "ratio", "computed",
         "Tā pati formula ar 1,455 V: 5,1·10⁻³.", sig_figs=2, section="4.4"),
    _num("pbo2.dE0", "nernst", "ΔE° (PbO₂ pret MnO₄⁻)", C.pbo2_dE0, "E", "computed",
         "1,46 − 1,51 = −0,05 V.", decimals=2, section="4.4"),
    _num("pbo2.ediff", "nernst", "Avota un darba E° starpība", C.pbo2_ediff, "E", "computed",
         "1,80 − 1,46; no reģistra operandiem (DERIVED_PROSE); ziņo ar 2 decimāldaļām.",
         decimals=2, section="4.4"),
    _num("pbo2.ediff_crc", "nernst", "Avota un CRC E° starpība", C.pbo2_ediff_crc, "E", "computed",
         "1,80 − 1,455; nenoapaļota CRC bāze; ziņo ar 3 decimāldaļām.",
         decimals=3, section="4.4"),
    _num("pbo2.dE0_crc", "nernst", "ΔE° (CRC 1,455 pret 1,51)", C.pbo2_dE0_crc, "E", "computed",
         "1,455 − 1,51 = −0,055 V.", decimals=3, section="4.4"),
    _num("pbo2.dE0_src", "nernst", "ΔE° (avota 1,80 pret 1,51)", C.pbo2_dE0_src, "E", "computed",
         "1,80 − 1,51 = +0,29 V.", decimals=2, section="4.4"),
    _num("mno2.e0", "nernst", "E°(MnO₂/Mn²⁺)", C.mno2_e0, "E", "given",
         "D10 papildinājums; CRC 1,224 V. Kursa tabulā šī pāra nav.", decimals=2, section="4.4"),
    _num("mno2.e12", "nernst", "E(MnO₂) 12 mol/L HCl", C.mno2_at_12m, "E", "computed",
         "1,23 + (0,0592/2)·lg(12⁴) = 1,358 V.", decimals=3, section="4.4"),
    _num("cl2.e12", "nernst", "E(Cl₂) 12 mol/L HCl", C.cl2_at_12m, "E", "computed",
         "1,36 + (0,0592/2)·lg(1/12²) = 1,296 V; p(Cl₂) = 1 bar.", decimals=3, section="4.4"),
    _num("mno2.dE12", "nernst", "ΔE 12 mol/L HCl", C.mno2_dE_at_12m, "E", "computed",
         "1,358 − 1,296 = 0,062 V.", decimals=3, section="4.4"),
    _num("mno2.cross", "nernst", "c(HCl) pie ΔE = 0 (1,23 V)", C.mno2_cross_hcl, "c", "computed",
         "1,23 + 0,1184·lg c = 1,36 − 0,0592·lg c → c = 5,4 mol/L.", sig_figs=2, section="4.4"),
    _num("mno2.cross_crc", "nernst", "c(HCl) pie ΔE = 0 (CRC 1,224)", C.mno2_cross_hcl_crc, "c", "computed",
         "Tā pati formula ar 1,224 V → 5,8 mol/L.", sig_figs=2, section="4.4"),
    _num("close.v", "nernst", "tuvās robežas slieksnis", C.close_call_v, "E", "given",
         "Darba noteikums: |ΔE°| < 0,15 V → Nernsts obligāts. Nav avota skaitlis.", decimals=2, section="4.3"),
    _num("close.lgK", "nernst", "lg K pie 0,15 V (z = 1)", C.close_call_lgK_z1, "lgK", "computed",
         "lg K = 1·0,15/0,0592 = 2,5.", decimals=1, section="4.3"),
    _num("close.factor", "nernst", "Q attiecība pie 0,15 V (z = 1)", C.close_call_factor_z1, "ratio", "computed",
         "10^2,53 ≈ 342; koncentrāciju starpība, kas var pārvarēt 0,15 V pie z = 1.", decimals=0, section="4.3"),
    _num("dE.mnfe", "dGlgK", "ΔE°(Mn/Fe)", C.dE_mn_fe, "E", "computed",
         "1,51 − 0,77 = 0,74 V.", decimals=2, section="4"),
    _num("lgK.mnfe", "dGlgK", "lg K", C.lgK_mn_fe, "lgK", "computed",
         "lg K = z·ΔE°/0,0592 = 62,5.", decimals=1, section="4"),
    _num("dG.mnfe", "dGlgK", "ΔG°", C.dG_mn_fe, "dG", "computed",
         "ΔG° = −zFΔE°; ziņots kā −357 kJ/mol.", sig_figs=3, section="4"),
    # ---- titres (illustrative) ----
    _num("titre.1", "titre", "titrs 1", 12.30, "V_mL", "given",
         "Ilustratīvs titrs līdz 0,01 mL.", decimals=2, section="9.4"),
    _num("titre.2", "titre", "titrs 2", 12.35, "V_mL", "given",
         "Ilustratīvs titrs līdz 0,01 mL.", decimals=2, section="9.4"),
    _num("titre.3", "titre", "titrs 3", 12.40, "V_mL", "given",
         "Ilustratīvs titrs līdz 0,01 mL.", decimals=2, section="9.4"),
]


NUMBER_BY_ID = {n.id: n for n in NUMBERS}


# ---------------------------------------------------------------- derived prose (T04, H-05)
# Prose differences must be derived from registered operands, not written as
# literals. Each row: id (must be in NUMBERS), the expression as shown to the
# student, the operand NUMBERS ids, and the display rule in Latvian.
# tools/verify_numbers.py recomputes the result from the operands and fails
# when the displayed difference disagrees beyond half a unit in the last
# displayed digit of the result.
DERIVED_PROSE: list[dict] = [
    {
        "id": "pbo2.ediff",
        "expression": "1,80 − 1,46",
        "operand_values": [1.80, 1.46],   # avota 1,80 V; darba 1,46 V (pāris pbo2)
        "display_rule": "Starpība no reģistra operandiem; ziņo ar 2 decimāldaļām (0,34 V). Pret CRC nenoapaļoto 1,455 V — 0,345 V (pbo2.ediff_crc).",
    },
    {
        "id": "pbo2.ediff_crc",
        "expression": "1,80 − 1,455",
        "operand_values": [1.80, 1.455],  # avota 1,80 V; CRC nenoapaļota 1,455 V
        "display_rule": "Avota 1,80 V pret CRC nenoapaļoto 1,455 V; ziņo ar 3 decimāldaļām (0,345 V) un nekad neroundē operandus, lai iegūtu sakritību.",
    },
]

DERIVED_PROSE_BY_ID = {r["id"]: r for r in DERIVED_PROSE}

# ---------------------------------------------------------------- source errors (A list)
@dataclass
class SourceError:
    id: str
    where: str
    says: str
    correction: str
    evidence: str
    status: str
    action: str = "Labots"


SOURCE_ERRORS = [
    SourceError("A1", "LEC 2. tabula, Al–Zn", "Elementu etiķetes pārbīdītas par vienu rindu no Cu; AlO₂⁻/Al rinda atkārtota.",
                "Etiķetes piesaistītas pareizajām rindām; dublikāts noņemts.", "Tabulas iekšējā konsekvence", "apstiprināts"),
    SourceError("A2", "LEC P078; 2. tabula", "Br₂/2Br⁻ = +0,96 V.",
                "Lietot +1,07 V (CRC 1,066 V); avota 0,96 V norādīta 13.A.", "CRC Handbook, Br₂(l)+2e⁻ → 2Br⁻ = 1,066 V", "apstiprināts"),
    SourceError("A3", "LEC P063; 2. tabula", "PbO₂/Pb²⁺ = +1,80 V.",
                "Darba vērtība +1,46 V (CRC 1,455 V); avota +1,80 V paturēta 13.A un skaidrota.",
                "CRC Handbook: PbO₂+4H⁺+2e⁻ → Pb²⁺+2H₂O = 1,455 V", "apstiprināts"),
    SourceError("A4", "LEC 1. tabula; P230", "O₂ + 2e⁻ + 2H₃O⁺ → H₂O + 2H₂O; E = +0,6945 V.",
                "O₂ + 4H₃O⁺ + 4e⁻ → 6H₂O; E° = +1,229 V, E°′ = +0,815 V.", "CRC 1,229 V; Campbell tabula 0,815 V; atomu pārbaude", "apstiprināts"),
    SourceError("A5", "LEC 1. tabula", "H⁺/H₂ 0,00 V blakus NAD⁺/NADH −0,3391 V un citām bioloģiskām vērtībām.",
                "E° un E°′ nav jaucami; 13.8 tabulā E°′ (pH 7), avota vērtības atsevišķā kolonnā.", "Campbell tabula: NAD −0,32; O₂ 0,815 V; E°′ formula", "apstiprināts"),
    SourceError("A6", "LEC P229", "“Šo procesu katalizē citohromkināze”.",
                "Terminālo posmu katalizē citohroma c oksidāze (IV komplekss); lietots “elektronu transporta ķēdes kompleksi I–IV”.",
                "Standarta bioķīmijas terminoloģija", "apstiprināts"),
    SourceError("A7", "LEC P229", "“NADH⁺ + H⁺ (reducētā NAD)”.",
                "Reducētā forma ir NADH; NADH⁺ neeksistē.", "NAD⁺/NADH redokss; Campbell tabula", "apstiprināts"),
    SourceError("A8", "LEC P250", "Jodometrijas titrants ir “I⁻ jonu saturošs šķīdums”.",
                "Jodometrijā titrants ir Na₂S₂O₃; jodimetrijā titrants ir I₂.", "Titrimetrijas definīcijas; LEC 2.4", "apstiprināts"),
    SourceError("A9", "LEC P249", "“Nogulsnēšanas metodes – sedimentācijas”.",
                "Nogulsnēšanas (precipitācijas) titrēšana; gravitācijas nosēdēšanās nav titrēšanas metode.", "Terminoloģijas atšķirība", "apstiprināts"),
    SourceError("A10", "LEC P244, P248, P253; L25 p.1", "Ekvivalences punkts = reakcijas beigu punkts.",
                "Ekvivalences punkts ir teorētisks; titrēšanas beigu punkts ir novērots. Atšķirība ir titrēšanas kļūda.",
                "Titrimetrijas definīcijas", "apstiprināts"),
    SourceError("A11", "LEC P253, P265; L25 p.2", "Rozā krāsa saglabājas 1–2 min / 1 min / neizzūd.",
                "Trīs dažādi kritēriji; parādīti visi, ieteikts sekot laboratorijas instruktoram. Praksē bieži 30 s.",
                "Laboratorijas instrukciju atšķirības; nav viena avota", "jāpārbauda"),
    SourceError("A12", "LEC P254 pret P097–P098 un L21", "“Neitrālā vai bāziskā vidē rodas MnO₂”.",
                "Bāziskā vidē pirmais produkts ir MnO₄²⁻ (zaļš); neitrālā — MnO₂ (brūns).", "LEC paša pusreakcijas; L21 1. tabula", "apstiprināts"),
    SourceError("A13", "LEC P071, 3. piemērs", "“Skābā vidē” dihromāts oksidē hlorīdu.",
                "Tas notiek tikai, ja [H⁺] ≳ 1,65 mol/L; aprēķins 4.3.", "Nernsta aprēķins ar 0,0592 V", "apstiprināts"),
    SourceError("A14", "LEC self-test 2; L20 p.4", "H₃PO₃ kā PO₃³⁻.",
                "H₃PO₃ + H₂O → H₃PO₄ + 2H⁺ + 2e⁻; nevis PO₃³⁻.", "H₃PO₃ ir divvērtīgā molekula; sk. 6.10", "apstiprināts"),
    SourceError("A15", "L20/L21/LEC (sulfīts skābē)", "SO₃²⁻ H₂SO₄ šķīdumā.",
                "Skābā vidē dominē HSO₃⁻/SO₂·H₂O; kursa SO₃²⁻ ir vienkāršojums, atzīmēts vienreiz.", "Skābes-bāzes līdzsvars; E° atšķirība 0,20/−0,93 V", "atzīmēts"),
    SourceError("A16", "LEC §3.1", "M[(NH₄)₂Fe(SO₄)₂] = 284 g/mol.",
                "284 g/mol ir bezūdens sāls; laboratorijas Mora sāls parasti ir heksahidrāts, M = 392,1 g/mol.", "Molmasu aprēķins", "apstiprināts"),
    SourceError("A17", "LEC P292, P299, P303", "c = 0,13 M → m = 3,69 g.",
                "Nenoapaļotā c = 0,132 mol/L; m = 3,75 g (3 zīm. c.); ar 2 zīm. datiem 3,7 g.", "0,024·11·5/(1·10) = 0,132", "apstiprināts"),
    SourceError("A18", "LEC self-test tabula", "8,64 g/L; 0,19 %; “normālā” atbilde 0,067 M.",
                "8,63 g/L; 0,20 %; 0,067 M (= mol/L) ir molārā koncentrācija, normālā ir 0,333 ekv/L.", "Pārrēķins ar M = 151,91 un 55,845", "apstiprināts"),
    SourceError("A19", "LEC P294", "c = m/(m·V).",
                "c = m/(M·V); otrais m ir molmasa M.", "Dimensiju pārbaude", "apstiprināts"),
    SourceError("A20", "LEC P276", "“Oksidētājs V = 1,51 V”.",
                "Potenciāla simbols ir E; V ir vienība.", "Notācijas standarts", "apstiprināts"),
    SourceError("A21", "LEC P039", "R = 8,314 J/mol, K.",
                "R = 8,314 J/(mol·K).", "Vienību analīze", "apstiprināts"),
    SourceError("A22", "LEC P044–P045, P067–P093, P224", "0,0591 un 0,059 dažādās vietās.",
                "Viss dokuments lieto 0,0592 V pie 298 K; 0,0591/0,059 citēti tikai kā avota formas.", "2,303·RT/F = 0,05916 V", "apstiprināts"),
    SourceError("A23", "LEC P067, P070, P224", "Sarežģīti apzīmējumi E_{Cr₂/O₇²⁻/2Cr³⁺}, E_{C₂/2Cl⁻}, saplēsts log.",
                "Pārrakstīts kā E(Cr₂O₇²⁻/2Cr³⁺), E(Cl₂/2Cl⁻), lg([Ox]/[Red]).", "Ķīmiskā notācija", "apstiprināts"),
    SourceError("A24", "LEC P005", "Kofaktori Fe³⁺, Cu²⁺, Mn⁴⁺, Zn²⁺, Mo⁵⁺.",
                "Zn²⁺ parasti nemaina oksidēšanas pakāpi; tas ir strukturāls/Lūisa skābes kofaktors. Redoksā: Fe³⁺/Fe²⁺, Cu²⁺/Cu⁺, Mn³⁺/Mn²⁺, Mo(VI)/Mo(IV).",
                "Metalloenzīmu redokss; Zn²⁺ d¹⁰", "apstiprināts"),
    SourceError("A25", "LEC P126", "“Ūdeņraža atomi labi šķīst platīnā.”",
                "Uz platīna virsmas ūdeņradis adsorbējas; lielos daudzumos absorbē pallādijs.", "SHE konstrukcija; Pd hidrīds", "apstiprināts"),
    SourceError("A26", "LEC P029", "“Ūdeņraža standartelektrods ([H⁺] = 1M)”.",
                "SHE definīcija: a(H⁺) = 1, p(H₂) = 1 bar; 1 M ir praktiska tuvināšana.", "IUPAC standartelektroda definīcija", "apstiprināts"),
    SourceError("A27", "LEC P011–P012", "S⁴⁺ − 2e⁻ → S⁶⁺; O₂ + 4e⁻ → 2O²⁻.",
                "Tas ir formāls uzskaits: SO₂/SO₃ ir kovalenti; S(+4) un O(−2) nav reāli joni (avota [[w:S^4+]]/[[w:O^2-]] ir lādiņa forma).", "Kovalentā saite; oksidēšanas pakāpes formālā daba", "apstiprināts"),
]

# ---------------------------------------------------------------- change log
# Canonical 69-claim registry across 5 filterable groups (Task 20).
# id, group, source, source wording, master, reason/evidence, status, chapter_anchor
CHANGELOG = [
    # --- Labojumi (A-set errors, C-set typos) ---
    ("A1", "Labojumi", "LEC 2. tabula", "Etiķetes Cu/Pb/Sn/Zn pārbīdītas; AlO₂⁻/Al dublikāts.",
     "Etiķetes piesaistītas pareizajām rindām; dublikāts noņemts.", "Tabulas iekšējā konsekvence.", "apstiprināts", "potentials"),
    ("A2", "Labojumi", "LEC P078; 2. tabula", "Br₂/2Br⁻ +0,96 V.",
     "Darba vērtība +1,07 V; avota +0,96 V paturēta 13.A.", "CRC 1,066 V; Br₂ paliek starp I₂ un Cl₂.", "apstiprināts", "potentials"),
    ("A3", "Labojumi", "LEC P063; 2. tabula", "PbO₂/Pb²⁺ +1,80 V.",
     "Darba vērtība +1,46 V; avota vērtība paturēta 13.A.", "CRC 1,455 V; 4.4 skaidro koncentrācijas un [MnO₄⁻] lomu.", "apstiprināts", "q3"),
    ("A4", "Labojumi", "LEC 1. tabula; P230", "O₂ + 2e⁻ + 2H₃O⁺ → H₂O + 2H₂O; 0,6945 V.",
     "O₂ + 4H₃O⁺ + 4e⁻ → 6H₂O; E° 1,229 V, E°′ 0,815 V.", "Atomu un lādiņu bilance; CRC un Campbell.", "apstiprināts", "bio-table"),
    ("A5", "Labojumi", "LEC 1. tabula", "E° un E°′ vērtības vienā kolonnā.",
     "8. nodaļā E°′ atdalīts ar atsevišķu avota kolonnu.", "Campbell tabula; E°′ = E° − 0,0592(m/n)pH.", "apstiprināts", "bio-table"),
    ("A6", "Labojumi", "LEC P229", "“citohromkināze”.",
     "“citohroma c oksidāze / IV komplekss”.", "Fermenta funkcija (kināze pārnes fosfātu).", "apstiprināts", "bio-table"),
    ("A7", "Labojumi", "LEC P229", "“NADH⁺”.",
     "NADH (reducētā forma).", "NADH⁺ nepastāv; reducētais pāris ir NAD⁺/NADH.", "apstiprināts", "bio-table"),
    ("A8", "Labojumi", "LEC P250", "Jodometrijas titrants I⁻.",
     "Jodometrija: Na₂S₂O₃ titrants; jodimetrija: I₂ titrants.", "Titrimetrijas definīcijas.", "apstiprināts", "methods"),
    ("A9", "Labojumi", "LEC P249", "“sedimentācijas metodes”.",
     "“nogulsnēšanas (precipitācijas) titrēšana”.", "Termina nozīme (sedimentācija ir gravitācijas nosēšanās).", "apstiprināts", "methods"),
    ("A10", "Labojumi", "LEC P244/P253; L25 1. lpp.", "Ekvivalences punkts = beigu punkts.",
     "Nošķirti teorētiskais ekvivalences punkts un novērotais beigu punkts.", "Titrimetrijas indikatora kļūdas definīcija.", "apstiprināts", "equivalence-law"),
    ("A12", "Labojumi", "LEC P254", "“Neitrālā vai bāziskā vidē rodas MnO₂”.",
     "Bāzē MnO₄²⁻ (zaļš), neitrālā MnO₂ (brūns).", "LEC P096–P098; L21 1. tabula.", "apstiprināts", "obs"),
    ("A13", "Labojumi", "LEC P071", "“Skābā vidē” bez skaitļa.",
     "[H⁺] ≳ 1,65 mol/L; aprēķins 4.4.", "Nernsta vienādojums ar [H⁺]¹⁴ slieksni.", "apstiprināts", "q3"),
    ("A14", "Labojumi", "LEC self-test 2; L20 4. lpp.", "PO₃³⁻ treatēts kā jons.",
     "H₃PO₃ diprotiska molekula; sk. 6.10.", "Fosfītskābes pKa1 = 1,3 un disociācijas daba.", "apstiprināts", "canonical"),
    ("A16", "Labojumi", "LEC §3.1", "M = 284 g/mol.",
     "284 bezūdens; heksahidrāts 392,1 g/mol; abi parādīti.", "Mora sāls molmasu analīze.", "apstiprināts", "lec31"),
    ("A17", "Labojumi", "LEC P292/P299/P303", "0,13 M → 3,69 g.",
     "0,132 mol/L → 3,75 g; 2 zīm. → 3,7 g.", "Nenoapaļotu starplielumu saglabāšana.", "apstiprināts", "lec31"),
    ("A18", "Labojumi", "LEC self-test", "8,64 g/L; 0,19 %; normālā = 0,067 M.",
     "8,63 g/L; 0,20 %; 0,067 M ir molārā (normālā 0,333 ekv/L).", "Pārrēķins ar pareizām molmasām un z faktoru.", "apstiprināts", "lec31"),
    ("A28", "Labojumi", "12.4.2 rēķina bloks; T04", "0,0568 · 151,91 = 8,629 g.",
     "Nenoapaļots 8,628488 → 8,628 g (3 decimāldaļas); ziņotā atbilde 8,63 g/L (3 zīmīgie) nav mainīta.",
     "Rezultātu noapaļo no nenoapaļota reizinājuma vienreiz; nenoapaļotā vērtība redzama 12.4.2 rēķinā (qa/t04; H-05 līdzbraucējs).", "apstiprināts", "lec-task2"),
    ("A19", "Labojumi", "LEC P294", "C = m/(m·V).",
     "c = m/(M·V).", "Dimensiju analīze (otrais m ir molmasa M).", "apstiprināts", "lec31"),
    ("A20", "Labojumi", "LEC P276", "“V = 1,51 V”.",
     "E = 1,51 V.", "Potenciāla simbola notācija.", "apstiprināts", "potentials"),
    ("A21", "Labojumi", "LEC P039", "J/mol, K.",
     "J/(mol·K).", "SI atvasināto mērvienību pieraksts.", "apstiprināts", "nernst-derivation"),
    ("A22", "Labojumi", "LEC P044 un citur", "0,0591 / 0,059.",
     "0,0592 V visā dokumentā; avota formas tikai citātos.", "2,303·RT/F = 0,05916 V noapaļots līdz 4 zīmēm.", "apstiprināts", "fn-a22"),
    ("A23", "Labojumi", "LEC P067/P070/P224", "Salauzti E apzīmējumi.",
     "E(Cr₂O₇²⁻/2Cr³⁺), E(Cl₂/2Cl⁻), lg.", "Tipogrāfiskie labojumi formulās.", "apstiprināts", "nernst-expressions"),
    ("A24", "Labojumi", "LEC P005", "Zn²⁺ kā redoksa kofaktors.",
     "Zn²⁺ strukturāls kofaktors; redoksa pāri Fe/Cu/Mn/Mo.", "Metalloenzīmu bioķīmija.", "apstiprināts", "bio-table"),
    ("A25", "Labojumi", "LEC P126", "H šķīst platīnā.",
     "H adsorbējas uz Pt virsmas; Pd absorbē tilpumā.", "SHE elektroda darbības princips.", "apstiprināts", "ch2"),
    ("A26", "Labojumi", "LEC P029", "[H⁺] = 1 M.",
     "a(H⁺) = 1, p(H₂) = 1 bar; 1 M tuvinājums.", "IUPAC standartelektroda definīcija.", "apstiprināts", "ch2"),
    ("C1", "Labojumi", "T13", "“okdidēšanās” (divreiz).",
     "“oksidēšanās”.", "Drukas kļūda.", "apstiprināts", "outcomes"),
    ("C2", "Labojumi", "L21 atslēgvārdi", "“pusrekcijas”.",
     "“pusreakcijas”.", "Drukas kļūda.", "apstiprināts", "six-steps"),
    ("C3", "Labojumi", "L25 (divreiz)", "“elektnonu”.",
     "“elektronu”.", "Drukas kļūda.", "apstiprināts", "methods"),
    ("C4", "Labojumi", "LEC self-test virsraksts", "“vinādojumu”.",
     "“vienādojumu”.", "Drukas kļūda.", "apstiprināts", "lec-task1"),
    ("C5", "Labojumi", "LEC P005", "“reducēšanas procesi”.",
     "“reducēšanās procesi”.", "Gramatika (atgriezeniskais darbības vārds procesam).", "apstiprināts", "ch1"),
    ("C6", "Labojumi", "LEC 2. tabulas galva", "“Oksidētāforma”, “Standart-potenciālsE⁰”.",
     "“Oksidētā forma”, “Standartpotenciāls E°”.", "Drukas kļūda.", "apstiprināts", "potentials"),
    ("C7", "Labojumi", "LEC vairākās vietās", "Mīkstās defises iekšā vārdos.",
     "Vārdi savienoti.", "Ekstrakcijas artefakts.", "apstiprināts", "ch1"),
    ("C9", "Labojumi", "LEC reakciju bultiņas", "Bultiņas kā WMF attēli, tekstā nav.",
     "Bultiņas pārrakstītas no ķīmiskās jēgas, pārbaudītas ar skriptu.", "Attēlu ekstrakcija.", "apstiprināts", "six-steps"),

    # --- Vienādojumi un skaitļi (B-set notation, R-set method/calculation) ---
    ("B1", "Vienādojumi un skaitļi", "LEC/L20", "4+, +5, −3, 2− jaukti.",
     "Lādiņam skaitlis pirms zīmes (Fe³⁺); pakāpei zīme pirms skaitļa (+4).", "IUPAC Red Book notācija; sk. 11.3.", "apstiprināts", "notation-legend"),
    ("B2", "Vienādojumi un skaitļi", "L20 1.–2. lpp.", "5Na₂SO₄²⁻, K₂SO₄²⁻, 2Mn⁺²SO₄²⁻.",
     "Neitrālām formulas vienībām nav lādiņa; lādiņu raksta tikai brīviem joniem.", "Lādiņa nezūdamības likuma vizualizācija.", "apstiprināts", "six-steps"),
    ("B3", "Vienādojumi un skaitļi", "L20, LEC §3.1, L25", "1│MnO₄⁻… 5│Fe²⁺…; 1 2 un 3 6 koeficienti.",
     "Mazākie veselie reizinātāji (LCM); 2:6 saīsina uz 1:3.", "Pusreakciju metodes algoritms.", "apstiprināts", "half-recipe"),
    ("B4", "Vienādojumi un skaitļi", "LEC P280, §3.1", "2x│MnO₄⁻ + …",
     "“2x” reizinātājs molekulārās un jonu formas saskaņošanai ar Fe₂(SO₄)₃.", "Molekulārā vienādojuma stehiometrija.", "apstiprināts", "half-recipe"),
    ("B5", "Vienādojumi un skaitļi", "L20 1. lpp.", "7H₂O → 8OH⁻ + 6H⁺ → 6H₂O + 2OH⁻.",
     "Ūdens un H⁺/OH⁻ saīsināšana kā atsevišķs algebraisks solis, nevis bultiņu virkne.", "Vienādojuma skaidrība.", "apstiprināts", "half-recipe"),
    ("B6", "Vienādojumi un skaitļi", "LEC, L20", "Elektroni kreisajā pusē ar mīnusu: Fe²⁺ − e⁻ → Fe³⁺.",
     "Elektroni labajā pusē oksidēšanai (Fe²⁺ → Fe³⁺ + e⁻), kreisajā reducēšanai.", "Vienota zīmju konvencija pret zīmju kļūdām.", "apstiprināts", "half-recipe"),
    ("B7", "Vienādojumi un skaitļi", "LEC", "Jaukti H⁺ un H₃O⁺ vienā un tajā pašā vienādojumā.",
     "Viena konvencija vienādojumā: H⁺ (īsā) vai H₃O⁺ ar atbilstošu 6H₂O skaitu.", "Ūdens bilances konsekvence.", "apstiprināts", "half-recipe"),
    ("B8", "Vienādojumi un skaitļi", "L25, L21, LEC", "0.0200 M ar punktu; ml; mol/l.",
     "Decimālkomats (0,0200); nedalāma atstarpe pirms vienības; mL, L, mol/L.", "Latviešu valodas un SI standarts.", "apstiprināts", "notation-legend"),
    ("B9", "Vienādojumi un skaitļi", "LEC §3, L25", "n = elektroni (Nernsts) un n = vielas daudzums (titrēšana).",
     "Ieviests z (ekvivalences skaitlis titrēšanai); n paturēts daudzumam un Nernstam.", "Jēdzieniskā skaidrība.", "apstiprināts", "equivalence-law"),
    ("B10", "Vienādojumi un skaitļi", "L20 1. rinda", "α = 1 bez paskaidrojuma.",
     "Definēts α = disociācijas pakāpe (pieņem pilnīgu stipro elektrolītu disociāciju).", "Termina nozīme.", "apstiprināts", "six-steps"),
    ("B11", "Vienādojumi un skaitļi", "LEC P232", "ATP, ADP.",
     "Latviešu saīsinājumi ATF, ADF (ATP, ADP iekavās vienreiz).", "AkadTerm un mācību literatūras standarts.", "apstiprināts", "bio-table"),
    ("B12", "Vienādojumi un skaitļi", "Visi avoti", "“oks/red” kā virsraksts.",
     "Pilns nosaukums “oksidēšanās-reducēšanās” virsrakstos; “oks/red” kā saīsinājums.", "Akadēmiskā stila konsekvence.", "apstiprināts", "sakums"),
    ("R1", "Vienādojumi un skaitļi", "LEC P048–P071", "Noteikums un trīs piemēri bez vienotas struktūras.",
     "4.1 četru jautājumu procedūra ar skaitļošanas zaru un lēmumu koku.", "Mācību metodika; sk. 4.1.", "apstiprināts", "procedure-4"),
    ("R2", "Vienādojumi un skaitļi", "Nav avotā; A3", "PbO₂/Mn²⁺: tikai “koncentrētā HNO₃”.",
     "Nernsta pārrēķins ar [H⁺]¹⁴ un [MnO₄⁻]/[Mn²⁺] koncentrācijas attiecību.", "Slīpumu kompensācija (−0,1184 pret −0,0947 V/pH); 4.4.", "apstiprināts", "q3"),
    ("R3", "Vienādojumi un skaitļi", "Nav avotā; D10", "MnO₂ + HCl: “koncentrēta HCl”, bez skaitļa.",
     "c(HCl) ≳ 5,4 mol/L slieksnis pie p(Cl₂) = 1 bar; 12 mol/L dod ΔE ≈ +0,06 V.", "Nernsta pārrēķins ar [H⁺]⁴ un [Cl⁻]²; 4.4.", "apstiprināts", "q3"),
    ("R4", "Vienādojumi un skaitļi", "Nav avotā", "Nav tuvās robežas noteikuma.",
     "|ΔE°| < 0,15 V definēts kā “tuva robeža” (atbilst lg K ≈ 2,5 pie z = 1).", "Darba noteikums koncentrāciju pārvaramībai; sk. 4.3.", "atzīmēts", "q2"),

    # --- T06 (Task 26): mechanism/boundary rewrites; prose only, no values ---
    ("R5", "Vienādojumi un skaitļi", "LEC P018; LEC 2. tabula", "Formas un lomas, E° intensivitāte nav izvērsta.",
     "4.2 “Kāpēc E° nereizina” ar apgalvojuma piemēru 2·0,77 = 1,54 V un “Forma nav loma” ar z = 2 robežas piemēru.", "M08, M20, M01; skaitļi fe.e0 / fe.e0.double.", "apstiprināts", "q1"),
    ("R6", "Vienādojumi un skaitļi", "LEC P093", "Koeficienta Q sastāvs dotts kā tabula bez “kāpēc”.",
     "3.1 “Kāpēc” rinda: Q satur mainīgās aktivitātes; cietvielas ≈ 1; H⁺ pakāpe = koeficients.", "M06, M07; standarta Nernsta forma.", "apstiprināts", "quotient-rules"),
    ("R7", "Vienādojumi un skaitļi", "LEC P093; A22", "3.4 rāda tikai pH pusi no korekcijas.",
     "3.4 “Attiecības puse”: 0,010/0,001 mol/L → korekcija 0,0118 V, E = 1,522 V; robeža: attiecība 1 un Fe³⁺/Fe²⁺ bez H⁺.", "Skaitļi mn.ratio10.corr / mn.ratio10.E; M07.", "apstiprināts", "ph-centrepiece"),
    ("R8", "Vienādojumi un skaitļi", "LEC P093–P098", "Vides ietekme dotta kā produktu saraksts.",
     "6.1 un 7.3/7.4 cēloņu kāpa: vide → E → produkts; z nosaka, cik tālu iet, slīpums — E reakciju uz pH.", "M03, M04, M05, M11; A12.", "apstiprināts", "six-steps"),
    ("R9", "Vienādojumi un skaitļi", "LEC P006, P226–P235", "Pakāpeniskums dotts kā apgalvojums.",
     "8. intro “Kāpēc mazi soļi”: katrs sols = neliels ΔE°′; virziens vienā konvencijā; robeža 8.2 destruktīvais tests.", "M09, M25; A5.", "apstiprināts", "ch8"),
    ("R10", "Vienādojumi un skaitļi", "LEC P252–P254", "“Pirmā rozā” pamatojums tikai secinājuma līmenī.",
     "9 “Ko nozīmē pirmā rozā krāsa”: analīts reducē pārpalikumu, izsmelts → rozā paliek; robeža MnO₂ neitrālā vidē.", "M12, M13; A10/A11 paliek.", "apstiprināts", "procedure"),
    ("R11", "Vienādojumi un skaitļi", "LEC P248; P150–P154", "“5/2” un alikvota saite doti bez atvasinājuma.",
     "12.4.3 “No kurienes 5/2” (z = 5 un z = 2) un “No 2 mL uz 10 mL” (2,10 g, ×10); robeža Fe²⁺ 5/1.", "M03, M15; A18.", "apstiprināts", "numeric"),
    ("R12", "Vienādojumi un skaitļi", "LEC P292–P303", "“c un m soļi” pamatojums netiksa izvērsts.",
     "9.5 “Kāpēc c un m ir divi dažādi soļi” (alikvots ↔ šķīdums, mērkolba ↔ paraugs) un noapaļošanas robežas piemērs.", "M15, M22, M23; A16/A17.", "apstiprināts", "lec31"),

    # --- Terminoloģija (T-set terms, C8, §E) ---
    ("T1", "Terminoloģija", "LEC/T13", "“oksidēšanās pakāpe” / “oksidēšanas pakāpe”.",
     "“oksidēšanas pakāpe” visur.", "Standarta termins; kursa lietojuma vairākums.", "apstiprināts", "ch1"),
    ("T2", "Terminoloģija", "LEC P244", "“analīze” parauga nozīmē.",
     "“analīts / analizējamā viela”; analīze ir process.", "Termina nozīme.", "apstiprināts", "equivalence-law"),
    ("T3", "Terminoloģija", "LEC P248", "Ekvivalences likums ar a·n.",
     "n₁z₁ = n₂z₂; z (ekvivalences skaitlis) skaidrots.", "Stehiometrija.", "apstiprināts", "equivalence-law"),
    ("T4", "Terminoloģija", "LEC P232", "ATP, ADP.",
     "ATF, ADF (ATP, ADP iekavās vienreiz).", "Latviešu terminoloģija.", "apstiprināts", "bio-table"),
    ("T5", "Terminoloģija", "LEC", "“normālā koncentrācija”.",
     "Molārā koncentrācija c(X); normālā tikai vēsturiskajā uzdevumā.", "SI un IUPAC analītiskās ķīmijas standarts.", "apstiprināts", "lec31"),
    ("T6", "Terminoloģija", "LEC P250", "“jodometrija” kā I⁻ titrants.",
     "Jodometrija (tiosulfāts) un jodimetrija (I₂) stingri nošķirtas.", "Titrimetrijas definīcijas.", "apstiprināts", "methods"),
    ("T7", "Terminoloģija", "LEC P147–P170", "“amfotērisks pāris” matricā.",
     "“abējādas lomas” / “amfotēriska viela (redokss)”.", "Pāris = Ox/Red sistēma; viela = loma reakcijā.", "apstiprināts", "amphoteric"),
    ("C8", "Terminoloģija", "LEC", "“oksidēšanas pakāpe” un “oksidēšanās pakāpe”.",
     "“oksidēšanas pakāpe” visur.", "Standarta termins; lietojuma vairākums.", "apstiprināts", "ch1"),

    # --- Papildinājumi (D-set practice gaps) ---
    ("D1", "Papildinājumi", "LEC P270; L20 1. lpp.",
     "Precīzas KMnO₄ koncentrācijas noteikšanai lieto skābeņskābes H₂C₂O₄ šķīdumu.",
     "Standartizācija ar skābeņskābi vai nātrija oksalātu; siltā titrēšana (ap 60–70 °C); autokatalīze ar Mn²⁺.",
     "Standartizācija ar skābeņskābi: LEC P270, L20 1. lpp. “60–70 °C” un “nātrija oksalāts” kursa avotos nav — skaitlis jāpārbauda (T04/T05).",
     "jāpārbauda", "procedure"),
    ("D2", "Papildinājumi", "Nav avotā", "Biretes nolasīšana.",
     "Augšējā meniska mala KMnO₄ šķīdumam; 0,01 mL nolasīšana; gaisa izlaišana.", "Titrimetrijas laboratorijas prakse.", "atzīmēts", "procedure"),
    ("D3", "Papildinājumi", "LEC P251 (daļēji)", "Tikai H₂SO₄.",
     "Pamatojums: HCl oksidējas par Cl₂, HNO₃ pati ir spēcīgs oksidētājs.", "Redoksa īpašības un titranta selektivitāte.", "apstiprināts", "procedure"),
    ("D4", "Papildinājumi", "L25 2. lpp.", "Vismaz 3 titrēšanas.",
     "Konkordantie titri (starpība ≤ 0,10 mL); acīmredzama izlēcēja atmetšana.", "Analītiskā datu apstrādes prakse.", "apstiprināts", "procedure"),
    ("D5", "Papildinājumi", "L25 3.–4. lpp.", "Alikvots un mērkolba.",
     "c rēķina no 10,00 mL alikvota, m — no 100,0 mL mērkolbas; hidrāta M.", "Vienību un tilpumu analīze.", "apstiprināts", "l25-worked"),
    ("D7", "Papildinājumi", "L25 1. daļa",
     "…lūdziet jaunu paraugu, jo esošais vairs nebūs precīzs.",
     "Svaigs paraugs (jāprasa jauns paraugs); H₂SO₄ pievienošana (skābā vide).",
     "Svaiga parauga un H₂SO₄ pievienošanas prakse ir L25 1. daļā; gaisa skābekļa oksidēšanas paātrinājuma skaidrojums avotos un redzamajā tekstā nav.",
     "apstiprināts", "procedure"),
    ("D8", "Papildinājumi", "Nav avotā", "ΔE > 0 nav ātrums.",
     "ΔG° = −zFΔE°; lg K = zΔE°/0,0592 (termodinamika pret kinētiku).", "Termodinamiskā saikne; F un Nernsta konstante LEC P040–P044, pats apgalvojums kursa avotos nav.", "atzīmēts", "thermo-kinetics"),
    ("D9", "Papildinājumi", "Nav avotā", "Disproporcionēšanās.",
     "3MnO₄²⁻ + 4H⁺ → 2MnO₄⁻ + MnO₂ + 2H₂O (zaļā manganāta nestabilitāte).", "Mangāna(VI) ķīmija.", "apstiprināts", "disproportionation"),
    ("D10", "Papildinājumi", "LEC P148", "MnO₂ + HCl → Cl₂.",
     "E° nav vienīgais: [H⁺]⁴ un [Cl⁻]² koncentrācijas efekts un Cl₂ aizplūšana.", "Nernsta vienādojums.", "apstiprināts", "q3"),

    # --- Atstāts negrozīts (deliberately preserved source claims or pending external verification) ---
    ("A11", "Atstāts negrozīts", "LEC P253/P265; L25 2. lpp.", "1–2 min / 1 min / neizzūd.",
     "Parādīti visi trīs avotu kritēriji; ieteikts sekot pasniedzēja norādei (prakse ≈ 30 s).", "Nav vienota avota standarta; reģistrēts qa/verify.md.", "jāpārbauda", "procedure"),
    ("A15", "Atstāts negrozīts", "L20/L21/LEC", "SO₃²⁻ skābā vidē.",
     "Paturēts kursa vienkāršojums; skaidrots, ka dominē HSO₃⁻ un SO₂·H₂O.", "Kursa vienkāršojums atzīmēts 5.5 un 6.14.", "atzīmēts", "canonical"),
    ("A27", "Atstāts negrozīts", "LEC P011–P012", "S⁴⁺, O²⁻.",
     "Paturēti kā formāli oksidēšanas skaitļi; uzsvērts, ka SO₂/SO₃ ir kovalenti.", "Kovalentā saite; oksidēšanas pakāpes formālā daba.", "atzīmēts", "ch1"),
    ("D6", "Atstāts negrozīts", "L25 2. lpp.", "“10,00 mL Mora pipete”, attēlā 25 mL.",
     "Attēlots 10,00 mL vienzīmes pipetes zīmējums atbilstoši tekstam; pretruna fiksēta.", "L25 2. lpp. ilustrācija; reģistrēts qa/verify.md.", "jāpārbauda", "procedure"),
]

CHANGES_AFFECTING_EXAM_IDS = [
    "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A10",
    "A14", "A16", "A17", "A18", "A22", "D3", "D5",
]

# ---------------------------------------------------------------- claim ledger
# T01. Source-ID registry for qa/claims.csv.
#
# T03 owns the bibliographic registry (qa/sources.csv). Every ID here exists
# there with the same identifier; `tools/check_sources.py` fails when the two
# vocabularies drift apart. The IDs are immutable — a source that is retired
# stays in the registry with its limitation rather than disappearing.
SOURCE_IDS: dict[str, str] = {
    "T13": "13 temata apraksts.pdf — topic scope and learning outcomes",
    "LEC": "Oksidesanas_reducesanas procesi_2022.docx — lecture theory",
    "L25": "6LW_MCh_Titration_Permanganatometrija_2025.pdf — titration lab",
    "L21": "6LW_Ox-red_LV_2021.pdf — manganese media lab",
    "L20": "Oksidesana_reducesana_reakcijas_2020.pdf — older worked lab",
    "CRC": "CRC Handbook standard reduction potentials (local dump)",
    "CAMP": "Campbell Biology ch. 8 sample — E°′ values (local dump)",
    "LIBRE": "LibreTexts standard reduction potentials by element",
    "TERMI": "termini.gov.lv / AkadTerm — Latvian terminology",
    "IUPAC": "IUPAC Gold Book — definitions",
    "IUPAC_GB": "IUPAC Compendium of Chemical Terminology (the Gold Book) — print edition",
    "IUPAC_T06387": "IUPAC Gold Book entry T06387 — titration",
    "IUPAC_E02188": "IUPAC Gold Book entry E02188 — equivalence point",
    "IUPAC_E02096": "IUPAC Gold Book entry E02096 — end-point",
    "IUPAC_S05917": "IUPAC Gold Book entry S05917 — standard hydrogen electrode",
    "IUPAC_S05912": "IUPAC Gold Book entry S05912 — standard electrode potential",
    "IUPAC_A00113": "IUPAC Gold Book entry A00113 — activity",
    "PUBC": "PubChem — molar masses",
    "BIONUM": "BioNumbers — database dump",
    "QA": "Master QA tooling — qa/plan.md, tools/recall_matrix.py, qa/numbers.csv",
    "FONT": "Embedded WOFF2 subsets — Inter, Inter Display, Noto Sans Math",
}

# Absolute words that assert universality. Scoped absolutes ("tikai šķīdumā",
# "katrs solis") are legitimate teaching statements and are NOT listed here;
# only unqualified universals are gated. "100 %" is listed because it is a
# completeness claim; the scanner excludes the percentage *operator* (a
# multiplication by 100 in a formula), which is not a claim.
CLAIM_ABSOLUTE_PATTERNS: list[tuple[str, str]] = [
    ("vienmēr", r"\bvienmēr\b"),
    ("vienmērīgi", r"\bvienmērīgi\b"),
    ("nekad", r"\bnekad\b"),
    ("galvenī", r"\bgalvenī\b"),
    ("vienīgais", r"\bvienīgais\b"),
    ("vienīgā", r"\bvienīgā\b"),
    ("bezgalīgi", r"\bbezgalīgi\b"),
    ("garantē", r"\bgarantē"),
    ("droši", r"\bdroši\b"),
    ("noteikti", r"\bnoteikti\b"),
    ("100 %", r"\b100\s*%"),
    ("nav iespējams", r"\bnav iespējams\b"),
]

# Numeric shapes that must be registered in NUMBERS (or explicitly registered
# in qa/claims.csv) when they appear in prose.
CLAIM_NUMBER_PATTERNS: list[tuple[str, str]] = [
    ("potenciālu starpība", r"par\s+\d+[,\.]\d+\s*V"),
    ("procents", r"\d+[,\.]\d+\s*%"),
    ("tilpums", r"\d+[,\.]\d*\s*mL"),
    ("reizinājums", r"\d+\s*×"),
    ("equilibrium constant", r"\blg\s*K\b\s*[≈=]\s*\d+[,\.]\d+"),
]

# Phrases that overstate verification coverage. These must not appear in the
# generated document; check_claims.py fails if they do.
BANNED_CLAIM_PHRASES: list[tuple[str, str]] = [
    ("aizstāj piecus avotus",
     "Šis materiāls aizstāj piecus izkaisītos avotus"),
    ("katrs skaitlis pārrēķināts",
     "katrs skaitlis pārrēķināts"),
    ("visi skaitļi pārrēķināti",
     "visi skaitļi pārrēķināti"),
    ("visi vienādojumi pārbaudīti",
     "Visi vienādojumi pārbaudīti"),
]

CHANGELOG_BY_ID = {r[0]: r for r in CHANGELOG}

ANCHOR_LABELS = {
    "outcomes": "0.1",
    "notation-legend": "0. nodaļa",
    "sakums": "0. nodaļa",
    "ch1": "1. nodaļa",
    "ch2": "2. nodaļa",
    "potentials": "13.A",
    "nernst-derivation": "3.2",
    "nernst-expressions": "3.3",
    "fn-a22": "3.2",
    "ph-centrepiece": "3.4",
    "procedure-4": "4.1",
    "q1": "4.2",
    "q2": "4.3",
    "q3": "4.4",
    "thermo-kinetics": "4.7",
    "amphoteric": "5.1",
    "six-steps": "6.1",
    "half-recipe": "6.2",
    "canonical": "6.3",
    "colours": "7.1",
    "obs": "7.2",
    "disproportionation": "7.7",
    "bio-table": "8.1",
    "methods": "9.1",
    "procedure": "9.2",
    "equivalence-law": "9.3",
    "l25-worked": "9.4",
    "lec31": "9.5",
    "lec-task1": "12.1",
}

# Rendered bibliography (13.D). T03: every entry is a plain citation that
# names the identity, the imprint, the identifier, the access date, the scope
# and the limitation. The bibliographic registry `qa/sources.csv` is the
# authority for those fields; `tools/check_sources.py` fails when the two
# drift apart (same ids, same titles, same urls).
#
# Shape: (id, title, scope, url, imprint, identifier, access_date, limitation)
REFERENCES = [
    ("T13", "13. Oksidēšanās – reducēšanās procesi",
     "Kursa fails: 13. temata robežas, sasniedzamie rezultāti un teorijas saraksts. "
     "Faila nosaukums: 13 temata apraksts.pdf.",
     "", "kursa materiāls, 2020 (PDF izveidots 2020-11-22)", "vietējais fails",
     "2026-11-09",
     "Failā nav autora, izdevuma vai gada; kursa piederība nāk no projekta konteksta, "
     "nevis no faila teksta."),
    ("LEC", "Oksidēšanās-reducēšanās procesi",
     "Kursa lekciju materiāls: definīcijas, Nernsta vienādojons, standartpotenciālu "
     "tabula, pašpārbaudes uzdevumi. Faila nosaukums: "
     "Oksidesanas_reducesanas procesi_2022.docx.",
     "", "kursa materiāls, 2022", "vietējais fails", "2026-11-09",
     "DOCX nav autoru vai izdevuma metadatu; gads ņemts no faila nosaukuma; reakciju "
     "bultiņas ir attēli, un to saturu nevar atpestīt no izvērstā izņemšanas."),
    ("L25", "Titrēšana un oksidēšanās reducēšanās reakcijas",
     "Pašreizējā permanganatometrijas procedūra, titrēšanas dati un divas aprēķina "
     "versijas. Faila nosaukums: 6LW_MCh_Titration_Permanganatometrija_2025.pdf.",
     "", "kursa materiāls, 2025 (PDF izveidots 2025-10-03)", "vietējais fails",
     "2026-11-09",
     "PDF metadatos autors “AgneseBr” (kontes nosaukums, nevis publicēta autora "
     "atzīme); D6 attēla/teksta nesakritība nav atrisināta."),
    ("L21", "6. Oksidēšanās – reducēšanās procesi",
     "Mangāna savienojumu krāsas trijās vidēs; 1.–2. tabula un trīs secinājumu "
     "jautājumi. Faila nosaukums: 6LW_Ox-red_LV_2021.pdf.",
     "", "Medicīniskā ķīmija, Cilvēka fizioloģijas un bioķīmijas katedra, 2021",
     "vietējais fails", "2026-11-09",
     "Publicēta izdevuma nav; PDF metadatos autors “AgneseBr”; avota apzīmējumā ir "
     "nepareiza forma (B7)."),
    ("L20", "Oksidēšanās-reducēšanās procesi (laboratorijas darbs)",
     "Vecāks laboratorijas darbs ar izstrādātiem risinājumiem un pašpārbaudes uzdevumiem "
     "1–2. Faila nosaukums: Oksidesana_reducesana_reakcijas_2020.pdf.",
     "", "kursa materiāls, 2020 (PDF izveidots 2021-10-14)", "vietējais fails",
     "2026-11-09",
     "Faila nosaukums un PDF metadati nesakrīt par gadu; PDF metadatos autors "
     "“Irina Kazuša”."),
    ("CRC", "CRC Handbook of Chemistry and Physics — Section 8: Electrochemical Series",
     "Standartpotenciālu E° vērtības: A2, A3, A4, A9, A13, D10, R2, R3.",
     "https://chclab-chem.nsysu.edu.tw/static/file/179/1179/img/3241/TablasdepotencialesREDOX_PhysChemhandbook.pdf",
     "8. sadaļa “Electrochemical Series”, Petr Vanýsek; E° pie 298,15 K un 101,325 kPa",
     "vietējais izvērstes fails <code>qa/verify_crc.txt</code> (11 lpp.)", "2026-11-09",
     "Izdevuma numurs, gads, izdevējs un ISBN nav atgūti: vietējais PDF ir TeamLRN "
     "e-grāmata bez titullapas. Vērtības pārbaudītas, izdevuma identitāte — ne."),
    ("CAMP", "Microbial Metabolism — Chapter 8: Metabolism: Energy, Enzymes, and Regulation",
     "E°′ vērtības pie pH 7,0: A4, A5.",
     "https://glencoe.mheducation.com/sites/dl/free/0072320419/1/pre20419_ch08.pdf",
     "8.1. tabula “Selected Biologically Important Redox Couples”, lappuses 158–159",
     "vietējais izvērstes fails <code>qa/verify_bio.txt</code> (19 lpp.)", "2026-11-09",
     "19 lapu paraugs bez titullapas un autorrīks: izdevums, gads un ISBN nav "
     "apstiprināmi; ceļā minētais “0072320419” nav neviena lapā apstiprināts."),
    ("LIBRE", "P1: Standard Reduction Potentials by Element",
     "Papildu pārbaude potenciālu pāriem; kursa Cr₂O₇²⁻ vērtība 1,33 V saglabāta.",
     "https://chem.libretexts.org/Ancillary_Materials/Reference/Reference_Tables/Electrochemistry_Tables/P1%3A_Standard_Reduction_Potentials_by_Element",
     "Chemistry LibreTexts, bez rediģēšanas datuma un versijas numura",
     "vietējais izvērstes fails <code>qa/verify_libre.html</code>", "2026-11-09",
     "Lapas vērtība Cr₂O₇²⁻/Cr³⁺ ir 1,36 V — atšķiras no CRC 1,232 V un kursa 1,33 V; "
     "ārējais salīdzinājums nav atrisināts (A9)."),
    ("TERMI", "Latvijas Nacionālais terminoloģijas portāls (AkadTerm)",
     "Latviešo terminu apstiprinājumi: 13.E terminu lēmumi, T1, T4, B11.",
     "https://termini.gov.lv/",
     "Valsts valodas centrs, JSON API; 30 vaizājumi", "qa/t22/portal_checks.csv",
     "2026-11-09",
     "Portāls nav versijāts; daži termini apstiprināti tikai citā kolekcijā, un "
     "“pusreakcija”, “analīts”, “jodimetrija” attiecīgi nav apstiprināti."),
    ("IUPAC_GB", "IUPAC Compendium of Chemical Terminology (the “Gold Book”)",
     "Definīciju autoritāte: A10, A26.",
     "https://goldbook.iupac.org/",
     "2nd ed., 1997; Blackwell Scientific Publications, Oxford; tiešsaistes versija "
     "S. J. Chalk",
     "ISBN 0-9678550-9-8; DOI 10.1351/goldbook", "2026-11-09",
     "Metadati ņemti no paša avota publicētās “Cite as” rindas; tie attiecas uz 2. "
     "izdevumu, nevis uz 2025. gada 5. izdevumu."),
    ("IUPAC_T06387", "titration (Gold Book ieraksts T06387)",
     "Ekvivalences punkta un titrēšanas beigu punkta nošķiršana: A10.",
     "https://goldbook.iupac.org/terms/view/T06387",
     "IUPAC Compendium of Chemical Terminology, online version 2.3.3 (2019)",
     "DOI 10.1351/goldbook.T06387", "2026-11-09",
     "Lasīts arhīva mirklī, jo origināls aizsargāts ar Cloudflare pieprasījumu; "
     "definīcija neaptver rozā krāsas noturības laiku ne Latviešu terminoloģiju."),
    ("IUPAC_E02096", "end-point (Gold Book ieraksts E02096)",
     "Norāde uz beigu punkta definīciju: A10.",
     "https://goldbook.iupac.org/terms/view/E02096",
     "IUPAC Compendium of Chemical Terminology, online version 5.0.0 (2025)",
     "DOI 10.1351/goldbook.E02096", "2026-11-09",
     "Ieraksts nav definēts atsevišķi (“See: titration”; avots Orange Book, 2nd ed., p. 47)."),
    ("IUPAC_E02188", "equivalence point (Gold Book ieraksts E02188)",
     "Norāde uz ekvivalences punkta definīciju: A10.",
     "https://goldbook.iupac.org/terms/view/E02188",
     "IUPAC Compendium of Chemical Terminology, online version 2.3.3 (2019)",
     "DOI 10.1351/goldbook.E02188", "2026-11-09",
     "Definīcija publicēta attēla veidā — tekstuālas definīcijas nav; tāpēc šis ieraksts "
     "nav pietiekams apgalvojuma pamats."),
    ("IUPAC_S05917", "standard hydrogen electrode (Gold Book ieraksts S05917)",
     "Standarta ūdeņraža elektroda statuss: A26.",
     "https://goldbook.iupac.org/terms/view/S05917",
     "IUPAC Compendium of Chemical Terminology, online version 2.3.3 (2019)",
     "DOI 10.1351/goldbook.S05917", "2026-11-09",
     "Pārbaudītais teksts nenosaka rakstu “a(H⁺) = 1, p(H₂) = 1 bar”; tas ir kursa un "
     "vispārinātās literatūras konvencija."),
    ("IUPAC_A00113", "activity (Gold Book ieraksts A00113)",
     "Aktivitātes jēdzums: A26.",
     "https://goldbook.iupac.org/terms/view/A00113",
     "IUPAC Compendium of Chemical Terminology, online version 5.0.0 (2025)",
     "DOI 10.1351/goldbook.A00113", "2026-11-09",
     "Ieraksts ir šķērslis uz “activity (relative activity)”; vienīgās aktivitātes "
     "definīcija nav pārbaudīta."),
    ("FONT", "Inter, Inter Display, Noto Sans Math (iegultie WOFF2 apakškopas)",
     "Dokumenta tipogrāfija.",
     "https://openfontlicense.org/",
     "SIL Open Font License 1.1", "iegulti WOFF2 apakškopas", "2026-11-09",
     "Apakškopas izgatavotas no iegultiem failiem; pirms fontu maiņas jāpārbauda "
     "licences atbilstība."),
]


def write_numbers_csv(path) -> int:
    """Write qa/numbers.csv from NUMBERS. Returns row count."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "id", "mark", "symbol", "raw", "reported", "unit", "unit_key",
        "kind", "sig_figs", "decimals", "section", "source_quoted", "rule",
        # F03 per-value evidence columns (couples evidence lives in
        # VALUE_EVIDENCE/COUPLES; this CSV is the NUMBERS machine view).
        "ev_status", "ev_source_id", "ev_source_value", "ev_rounding",
        "ev_check", "ev_caveat",
    ]
    lines = [",".join(headers)]
    for n in NUMBERS:
        def cell(v: object) -> str:
            s = "" if v is None else str(v)
            if any(c in s for c in ',|"\n'):
                return '"' + s.replace('"', '""') + '"'
            return s
        ev = VALUE_EVIDENCE[n.id]
        lines.append(",".join(cell(x) for x in [
            n.id, n.mark, n.symbol, repr(n.raw), n.reported, n.unit, n.unit_key,
            n.kind, n.sig_figs, n.decimals, n.section, n.source_quoted, n.rule,
            ev.status, ev.source_id, ev.source_value, ev.rounding,
            ev.check, ev.caveat,
        ]))
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(NUMBERS)


def numbers_json_blob() -> dict:
    """Subset of number/unit rules embedded in #master-data for the calculator."""
    return {
        "molar_shorthand_rule": MOLAR_SHORTHAND_RULE_LV,
        "sigfig_global_rule": SIGFIG_GLOBAL_RULE_LV,
        "units": {k: {"unit": v["unit"], "symbol": v["symbol"],
                      "deprecated": v.get("deprecated", False)}
                  for k, v in UNITS.items()},
        "tasks": {
            "l25": {
                "cK": C.l25_cK, "titres": C.l25_titres, "v": C.l25_v,
                "val": C.l25_val, "vflask_mL": C.l25_vflask * 1000,
                "cFe": C.l25_cFe, "nflask": C.l25_nflask,
                "m": C.l25_m, "m_hepta": C.l25_m_hepta,
                "M_anhydrous": MOLAR["FeSO4"], "M_hepta": MOLAR["FeSO4.7H2O"],
                "rule": TASK["l25"]["rule"],
                "z_K": 5, "z_Fe": 1,
            },
            "st1": {
                "c": C.st1_c, "m": C.st1_m_100, "normality": C.st1_normality,
                "z": 5, "rule": TASK["st1"]["rule"],
            },
        },
        "numbers": [
            {
                "id": n.id, "mark": n.mark, "symbol": n.symbol,
                "raw": n.raw, "reported": n.reported, "unit": n.unit,
                "unit_key": n.unit_key, "kind": n.kind,
                "sig_figs": n.sig_figs, "decimals": n.decimals,
                "rule": n.rule, "section": n.section,
            }
            for n in NUMBERS
        ],
    }


# ---------------------------------------------------------------- value evidence (F03)
# Per-value "kāpēc tieši šis skaitlis?" provenance. Every registered value
# (NUMBERS + COUPLES) carries exactly one evidence row; the builder renders it
# as a static <details class="value-evidence" id="ev-<id>"> panel in 13.F and
# every value span links to it (a.value-ref). No JS, no persistence, no network.
#
# Status vocabulary (label map EV_STATUS_LV):
#   source     — taken from a course source as printed
#   corrected  — source value kept for the record, working value differs (H-05)
#   verified   — text-verified against a registered external dump
#   computed   — computed from registry operands, machine-rechecked each build
#   convention — a working convention of this document, not a source number
#   unverified — honest unresolved status, must stay visible
# Rules: source_id must resolve in qa/sources.csv when set; an empty `check`
# renders the honest default "Ārējā pārbaude: nav veikta"; locators repeat
# qa/verify.md wording — no invented editions, pages, quotes or dates.
EV_STATUS_LV: dict[str, str] = {
    "source": "avota vērtība",
    "corrected": "labots",
    "verified": "verificēts",
    "computed": "aprēķināts",
    "convention": "darba konvencija",
    "unverified": "nav verificēts",
}


@dataclass(frozen=True)
class ValueEvidence:
    id: str            # number_id or couple id (must exist in NUMBERS or COUPLES)
    label: str         # what the learner sees as the value's name
    source_id: str     # resolves in qa/sources.csv; "" when not source-based
    source_locator: str
    reaction: str      # couple half-reaction in WORKED notation (builder chemifies); "" for numbers
    conditions: str
    source_value: str
    display_value: str
    rounding: str
    check: str
    status: str
    caveat: str = ""
    claim_id: str = ""


def _eprint(x: float, nd: int) -> str:
    return format_E(x, nd)


def _src_precision(src: float) -> int:
    """Printed-precision decimals for a source E° (mirrors provenance_title)."""
    if abs(src - round(src, 2)) < 5e-5:
        return 2
    if abs(src - round(src, 3)) < 5e-6:
        return 3
    return 5


# Text-verified external checks (locators exactly as recorded in qa/verify.md;
# couples absent from this map honestly report "nav veikta").
COUPLE_CHECKS: dict[str, str] = {
    "pbo2": "CRC 1,455 V — <code>qa/verify_crc.txt</code> L232 (tekst verificēts 2026-11-09; CRC izdevums nenosakīts — T03)",
    "br2": "CRC 1,066 V — <code>qa/verify_crc.txt</code> L91 (tekst verificēts 2026-11-09; CRC izdevums nenosakīts — T03)",
    "o2h2o": "CRC 1,229 V — <code>qa/verify_crc.txt</code> L252; E°′ 0,815 V — Campbell 8.1. tabula, <code>qa/verify_bio.txt</code> (pH 7,0; abas tekst verificētas 2026-11-09, izdevumi nenosakīti — T03)",
    "cr2o7": "CRC 1,232 V — <code>qa/verify_crc.txt</code> L101; LibreTexts 1,36 V — <code>qa/verify_libre.html</code> L3056–3057; trīs dažādas vērtības, konvenciju jautājums atvērts (A9, 13.E)",
    "mno4n": "CRC 0,595 V — <code>qa/verify_crc.txt</code> L186 (tekst verificēts 2026-11-09)",
    "mno4b": "CRC 0,558 V — <code>qa/verify_crc.txt</code> L183 (tekst verificēts 2026-11-09)",
}


def _couple_evidence(c: Couple) -> ValueEvidence:
    src_val = (
        f"{c.format_working()} V (avotā tā pati)"
        if c.E_source is None or abs(c.E_source - c.E_working) <= 5e-4
        else f"{_eprint(c.E_source, _src_precision(c.E_source))} V"
    )
    check = COUPLE_CHECKS.get(c.id, "")
    caveat = c.conditions_note or c.note
    return ValueEvidence(
        id=c.id,
        label=f"{c.ox}/{c.red}",
        source_id=c.source_id,
        source_locator=c.source_ref or "—",
        reaction=c.half,
        conditions=c.conditions_prose(),
        source_value=src_val,
        display_value=f"{c.format_working()} V",
        rounding=f"{c.decimals} decimāldaļas",
        check=check,
        status=c.status,
        caveat=caveat,
        claim_id=c.claim_id,
    )


# Course-source locator per NUMBERS mark (§-level only; no invented pages).
MARK_SOURCE: dict[str, tuple[str, str]] = {
    "L25": ("L25", "L25: datu tabula un aprēķins"),
    "lec31": ("LEC", "LEC §3.1 uzdevums (P292–P303)"),
    "LEC1": ("LEC", "LEC pašpārbaudes uzdevums 1"),
    "LEC2": ("LEC", "LEC pašpārbaudes uzdevums 2"),
    "LEC3": ("LEC", "LEC pašpārbaudes uzdevums 3"),
    "LEC4": ("LEC", "LEC pašpārbaudes uzdevums 4"),
    "potentials": ("LEC", "LEC 2. tabula"),
    "nernst": ("LEC", "LEC Nernsta vienādojums (P224)"),
}

# Explicit overrides where the derived status would be dishonest.
NUM_EV_OVERRIDES: dict[str, dict] = {
    "nernst.const": {
        "status": "convention", "source_id": "LEC",
        "caveat": "Viena Nernsta konstante visam dokumentam pie 298 K (A22); precīzā vērtība — nernst.exact.",
    },
    "close.v": {
        "status": "convention", "source_id": "", "source_locator": "",
        "caveat": "Darba noteikums, nevis avota skaitlis; pamatojums 4.3 sadaļā.",
    },
    "titre.1": {"status": "convention", "source_id": "", "source_locator": "",
                "caveat": "Ilustratīvi titri; nav izmērīti dati (9.4)."},
    "titre.2": {"status": "convention", "source_id": "", "source_locator": "",
                "caveat": "Ilustratīvi titri; nav izmērīti dati (9.4)."},
    "titre.3": {"status": "convention", "source_id": "", "source_locator": "",
                "caveat": "Ilustratīvi titri; nav izmērīti dati (9.4)."},
    "eprime.o2_rep": {
        "status": "verified", "source_id": "CAMP",
        "source_locator": "Campbell 8.1. tabula (E°′; pH 7,0 piezīme) — <code>qa/verify_bio.txt</code> L363–L394",
        "check": "Tekst verificēts 2026-11-09; parauga izdevums nenosakīts (T03); T nav nosaukta ārpus pH 7,0.",
        "caveat": "Ārējā E°′ vērtība; salīdzinājumam ar aprēķinu eprime.o2.",
    },
    "eprime.nad": {
        "status": "verified", "source_id": "CAMP",
        "source_locator": "Campbell 8.1. tabula (E°′) — <code>qa/verify_bio.txt</code> L374",
        "check": "Tekst verificēts 2026-11-09; parauga izdevums nenosakīts (T03).",
        "caveat": "Campbell izraksta vērtība pH 7,0; izrakstā T nav nosaukta.",
    },
    "fe.e0.double": {
        "caveat": "Nav ne viena pāra, ne kopsummas potenciāls — apgalvojuma piemērs (M20); E° ir intensitātes lielums.",
    },
}


def _num_evidence(n: NumberEntry) -> ValueEvidence:
    rounding = (
        f"{n.decimals} decimāldaļas" if n.decimals is not None
        else (f"{n.sig_figs} zīmīgie cipari" if n.sig_figs is not None else "—")
    )
    if n.kind == "computed":
        status, src_id, src_loc = "computed", "QA", "tools/verify_numbers.py; qa/numbers.csv"
        check = "verify_numbers.py neatkarīgi pārrēķina no reģistra operandiem katrā būvē"
    elif n.kind == "given":
        src_id, src_loc = MARK_SOURCE.get(n.mark, ("", ""))
        status, check = "source", ""
    else:  # source_quoted — printed source answer kept as a citation
        src_id, src_loc = MARK_SOURCE.get(n.mark, ("", ""))
        status, check = "source", ""
    ov = NUM_EV_OVERRIDES.get(n.id, {})
    conditions = f"§{n.section}" if n.section else "—"
    return ValueEvidence(
        id=n.id,
        label=n.symbol,
        source_id=ov.get("source_id", src_id),
        source_locator=ov.get("source_locator", src_loc),
        reaction="",
        conditions=conditions,
        source_value=ov.get("source_value", n.source_quoted or "—"),
        display_value=n.reported_with_unit,
        rounding=rounding,
        check=ov.get("check", check),
        status=ov.get("status", status),
        caveat=ov.get("caveat", ""),
        claim_id=ov.get("claim_id", ""),
    )


VALUE_EVIDENCE: dict[str, ValueEvidence] = {}
for _c in COUPLES:
    VALUE_EVIDENCE[_c.id] = _couple_evidence(_c)
for _n in NUMBERS:
    VALUE_EVIDENCE[_n.id] = _num_evidence(_n)

# Completeness + vocabulary invariants: a malformed id anywhere above fails
# the import and therefore the build (F03 failure rule).
assert len(VALUE_EVIDENCE) == len(NUMBERS) + len(COUPLES), "value evidence not 1:1"
for _ev in VALUE_EVIDENCE.values():
    assert _ev.status in EV_STATUS_LV, f"unknown evidence status {_ev.status}"
    assert _ev.id in NUMBER_BY_ID or _ev.id in COUPLE_BY_ID, f"orphan evidence {_ev.id}"
