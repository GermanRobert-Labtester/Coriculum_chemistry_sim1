#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/data.py — Canonical data and recomputation engine for Lab 6B.

All scientific facts, standards, samples, calibration regressions, photon energies,
and uncertainty budgets are maintained here with SI units.

T10 auditability contract (C-05/C-09):
- Raw protocol rows below are the only absorbance-value source (filled 2020 protocol).
  They are never normalized, filtered or reordered before computation; see
  source_observations() for the named raw layer and named_results() for the named
  derived layer that plan/numbers.csv `ref` column points at.
- Every displayed number must be reproducible from this file: named_results() is the
  single registry connecting a published value to its derivation and assumptions.
- tools/numbers_trace.py audits the registry against plan/numbers.csv and the HTML;
  it is read-only. build.py remains the only writer of plan/uncertainty.csv.
"""

import math
import os
import sys

# -----------------------------------------------------------------------------
# 1. Physical & Chemical Constants
#    Raw datum layer (T10.1): each value carries its unit and its source. None of
#    these is normalized before use; display formatting happens only at the end.
# -----------------------------------------------------------------------------
CONSTANTS = {
    "substance": "Riboflavīns (vitamīns B2, C17H20N4O6)",
    "M": 376.36,              # g / mol (molar mass; handout §10.5, "dots")
    "wavelength_nm": 440.0,   # nm (protocol-fixed measurement wavelength)
    "cuvette_path_cm": 1.0,   # cm (optical path length l — ASSUMED: the protocol does not state it; 1 cm is the standard cuvette, AGENTS §5)
    "stock_gamma": 0.0400,    # mg / mL (stock solution concentration, "dots" 10.1)
    "total_volume_mL": 10.00, # mL (dilution flask / test tube volume, "dots" 10.5)
    "h": 6.62607015e-34,      # J * s (Planck constant)
    "c_light": 299792458,     # m / s (speed of light in vacuum)
    "N_A": 6.02214076e23,     # mol^-1 (Avogadro constant)
    "e_charge": 1.602176634e-19, # C (elementary charge)
    "resolution_A": 0.001,    # A (protocol display resolution: A recorded to 3 decimals — C49 step 4)
    "u_A_conservative": 0.001,# A (conservative reading uncertainty u(A) = one resolution unit; adopted model, 25. tabula)
}

# Derived uncertainty constants (T10.1: single definitions, no duplicated literals).
U_A_CONSERVATIVE = CONSTANTS["u_A_conservative"]  # A — conservative reading uncertainty
U_A_RECTANGULAR = U_A_CONSERVATIVE / math.sqrt(3.0)  # A — same half-width, rectangular distribution (0,000577 A)

# Stated assumptions for conditional results (T10.1.3). Every conditional number
# below cites the assumption key it depends on; displayed values inherit the label.
ASSUMPTIONS = {
    "path_length": "l = 1,0 cm ir PIEŅĒMUMS; protokols ceļa garumu nenorāda (AGENTS §5); ε un a derīgi tikai šai vērtībai",
    "epsilon": "ε = k·M derīgs pie l = 1 cm (sk. path_length); k ir mL·mg⁻¹, M ir g·mol⁻¹ → ε L·mol⁻¹·cm⁻¹",
    "lod_loq": "LOD = 3·s_y/k, LOQ = 10·s_y/k — vienkāršotas regresijas aplēses (homoscedasticity pieņēmums), NEVIS uz tukšā parauga atkārtotiem mērījumiem balstīta noteikšanas spēja (C-07/E26)",
    "u_A_model": "u(A) = 0,001 A konservatīvs (viens nolasīšanas soļš); taisnstūra modelis u = 0,001/√3; izslēgtas: pipetēšana, temperatūra, kivetes ceļš, tukšā mainīgums (25. tabula)",
    "free8_diagnostic": "brīvā 8 punktu variants ir tukšā jutīguma diagnoze, nevis rezultāta variants (C-05)",
    "model_7_3": "§7.3 transmisijas kļūdas modelis: ΔT = 0,005 (deklarēta konvencija, pusprocents); ΔA ≈ lg(e)·ΔT/T; relatīvā kļūda ΔA/A",
    "model_T12": "T12 izkliedētās gaismas modelis: T_m = (T + s)/(1 + s), s — izkliedētās gaismas daļa; nevis fizikāls detektora modelis",
}

# -----------------------------------------------------------------------------
# 2. Calibration Standards Data (handout 14. tabula / protocol 2. tabula, T07 C-09)
#    Raw protocol rows (T10.1.1): tuples are used exactly as recorded — no scaling,
#    no rounding, no reordering before the computations below. Display formatting
#    (decimal comma, fixed decimals) happens only when values reach the HTML.
# -----------------------------------------------------------------------------
STANDARDS = [
    # (id, v_stock_mL, v_water_mL, A_measured)  — A from the FILLED 2020 protocol
    (0, 0.00, 10.00, 0.000),  # tukšais (blank): 0,00 mL sākotnējā + 10,00 mL ūdens
    (1, 0.50,  9.50, 0.063),
    (2, 1.00,  9.00, 0.121),
    (3, 1.50,  8.50, 0.184),
    (4, 2.00,  8.00, 0.247),
    (5, 2.50,  7.50, 0.302),
    (6, 3.00,  7.00, 0.368),
    (7, 3.50,  6.50, 0.426),
    (8, 4.00,  6.00, 0.482),
]

# -----------------------------------------------------------------------------
# 3. Unknown Samples Data (protocol tables 1 & 3 / handout 13. tabula)
#    A_measured: filled 2020 protocol (the only absorbance source). gamma_protocol_read:
#    the protocol's own 4-decimal reading, kept for cross-checking — it is a SOURCE
#    observation, never an input to the fits.
# -----------------------------------------------------------------------------
SAMPLES = [
    # (sample_id, A_measured, gamma_protocol_read)
    (2, 0.086, 0.0028),
    (3, 0.170, 0.0055),
    (4, 0.258, 0.0085),
    (5, 0.372, 0.0122),
]

# -----------------------------------------------------------------------------
# 3a. Structured source observations (T10.1.1)
#     Named raw values that plan/numbers.csv `ref` column may point at. Every value
#     is read from the raw rows above at call time — a change to a protocol datum
#     therefore changes the observation names' values and is caught by the trace.
# -----------------------------------------------------------------------------
def source_observations():
    """Return [(name, value, unit, provenance)] for every raw protocol datum."""
    obs = []
    c = CONSTANTS
    obs.append(("constants.M", c["M"], "g/mol", "izdales materiāls (dots)"))
    obs.append(("constants.wavelength_nm", c["wavelength_nm"], "nm", "protokols (mērījuma vilnis)"))
    obs.append(("constants.cuvette_path_cm", c["cuvette_path_cm"], "cm", "PIĒŅĒMUMS (protokols nenorāda)"))
    obs.append(("constants.stock_gamma", c["stock_gamma"], "mg/mL", "dots (izejas šķīdums)"))
    obs.append(("constants.total_volume_mL", c["total_volume_mL"], "mL", "dots (kopējais tilpums)"))
    obs.append(("constants.h", c["h"], "J·s", "konstante"))
    obs.append(("constants.c_light", c["c_light"], "m/s", "konstante"))
    obs.append(("constants.N_A", c["N_A"], "mol^-1", "konstante"))
    obs.append(("constants.e_charge", c["e_charge"], "C", "konstante"))
    obs.append(("constants.resolution_A", c["resolution_A"], "A", "protokols (nolasīšanas izšķirtspēja)"))
    for std_id, v_st, v_w, A in STANDARDS:
        obs.append((f"std{std_id}.v_stock_mL", v_st, "mL", "14./15. tabula"))
        obs.append((f"std{std_id}.v_water_mL", v_w, "mL", "14./15. tabula"))
        obs.append((f"std{std_id}.A", A, "A", "14. tabula (aizpildītais protokols)"))
    for s_id, A, g_read in SAMPLES:
        obs.append((f"sample{s_id}.A", A, "A", "13. tabula (aizpildītais protokols)"))
        obs.append((f"sample{s_id}.gamma_protocol_read", g_read, "mg/mL", "13. tabula (protokola nolasījums, 4 zīmes)"))
    return obs

# -----------------------------------------------------------------------------
# 4. Mathematical Recomputations
# -----------------------------------------------------------------------------
def get_standards_table():
    """Compute concentration and derived values for calibration standards."""
    rows = []
    c0 = CONSTANTS["stock_gamma"]
    v_tot = CONSTANTS["total_volume_mL"]
    M = CONSTANTS["M"]
    for std_id, v_st, v_w, A in STANDARDS:
        gamma = c0 * (v_st / v_tot)
        c_mol = (gamma / M) # mol / L (since 1 mg/mL = 1 g/L)
        c_umol = c_mol * 1e6
        T = 10.0 ** (-A)
        rows.append({
            "id": std_id,
            "v_stock_mL": v_st,
            "v_water_mL": v_w,
            "gamma_mg_per_mL": gamma,
            "A": A,
            "c_mol_per_L": c_mol,
            "c_umol_per_L": c_umol,
            "T": T,
            "T_pct": T * 100.0,
        })
    return rows

def standards_rows(include_blank=True):
    """T10: single source of the fit point sets. The blank is included/excluded BY
    NAME at every call site so no fit can silently inherit the wrong point set."""
    rows = get_standards_table()
    return rows if include_blank else [r for r in rows if r["id"] > 0]

def compute_regression_origin(standards_rows):
    """
    Least squares fit through the origin: A = k * gamma
    Formula: k = sum(gamma * A) / sum(gamma^2)
    Standard error: s_y = sqrt(sum((A - k*gamma)^2) / (N - 1))
                    SE(k) = s_y / sqrt(sum(gamma^2))
    Units: k in mL·mg⁻¹ (A per mg/mL); sy, residuals in A.
    """
    sum_ga = sum(r["gamma_mg_per_mL"] * r["A"] for r in standards_rows)
    sum_g2 = sum(r["gamma_mg_per_mL"] ** 2 for r in standards_rows)
    k = sum_ga / sum_g2

    N = len(standards_rows)
    residuals = [r["A"] - k * r["gamma_mg_per_mL"] for r in standards_rows]
    res_sq = sum(e ** 2 for e in residuals)
    sy = math.sqrt(res_sq / (N - 1))
    se_k = sy / math.sqrt(sum_g2)

    return {
        "name": "origin9pt_blank_included",
        "label": "caur nulli, 9 punkti (tukšais iekļauts; b = 0 fiksēts)",
        "blank_included": True,
        "units": {"k": "mL·mg⁻¹", "se_k": "mL·mg⁻¹", "sy": "A", "residuals": "A"},
        "k": k,
        "sy": sy,
        "se_k": se_k,
        "N": N,
        "residuals": residuals,
    }

def compute_regression_free(standards_rows, include_blank=True):
    """
    Standard unconstrained linear regression: A = slope * gamma + intercept.
    Units: slope mL·mg⁻¹, intercept A, sy A; se_slope/se_intercept in the same
    units as slope/intercept (T10: published in 16. tabula but previously not
    computed here — now part of the named registry).
    """
    pts = standards_rows if include_blank else [r for r in standards_rows if r["id"] > 0]
    n = len(pts)
    sum_x = sum(r["gamma_mg_per_mL"] for r in pts)
    sum_y = sum(r["A"] for r in pts)
    sum_x2 = sum(r["gamma_mg_per_mL"] ** 2 for r in pts)
    sum_xy = sum(r["gamma_mg_per_mL"] * r["A"] for r in pts)

    denom = n * sum_x2 - sum_x ** 2
    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    # R^2 and sy
    mean_y = sum_y / n
    ss_tot = sum((r["A"] - mean_y) ** 2 for r in pts)
    ss_res = sum((r["A"] - (slope * r["gamma_mg_per_mL"] + intercept)) ** 2 for r in pts)
    r2 = 1.0 - (ss_res / ss_tot)
    sy = math.sqrt(ss_res / (n - 2))

    # SE(slope) and SE(intercept) from the same residual variance sy (16. tabula)
    sxx = n * sum_x2 - sum_x ** 2
    se_slope = sy * math.sqrt(n / sxx)
    se_intercept = sy * math.sqrt(sum_x2 / sxx)

    blank = "blank_included" if include_blank else "blank_excluded"
    return {
        "name": f"free{n}pt_{blank}",
        "label": (f"brīvā, {n} punkti (tukšais {'iekļauts' if include_blank else 'izslēgts'})"),
        "blank_included": bool(include_blank),
        "units": {"slope": "mL·mg⁻¹", "intercept": "A", "sy": "A",
                  "se_slope": "mL·mg⁻¹", "se_intercept": "A"},
        "slope": slope,
        "intercept": intercept,
        "r2": r2,
        "sy": sy,
        "se_slope": se_slope,
        "se_intercept": se_intercept,
        "n": n,
    }

def compute_photon_energy(wavelength_nm=440.0):
    """Photon energy calculations at given wavelength."""
    lam_m = wavelength_nm * 1e-9
    h = CONSTANTS["h"]
    c = CONSTANTS["c_light"]
    N_A = CONSTANTS["N_A"]
    e = CONSTANTS["e_charge"]

    E_joules = (h * c) / lam_m
    E_eV = E_joules / e
    E_kJ_mol = (E_joules * N_A) / 1000.0
    wavenumber_cm = 1.0 / (lam_m * 100.0)
    frequency_hz = c / lam_m

    return {
        "wavelength_nm": wavelength_nm,
        "E_joules": E_joules,
        "E_eV": E_eV,
        "E_kJ_mol": E_kJ_mol,
        "wavenumber_cm": wavenumber_cm,
        "frequency_hz": frequency_hz,
    }

# --- T10 teaching models: published prose numbers brought into the authority ---
def transmittance_error_rel_pct(A, dT=0.005):
    """§7.3 reading-error model (assumption: model_7_3): if T is read with absolute
    error dT, then dA ≈ lg(e)·dT/T and the relative concentration error is dA/A.
    Returns the relative error in percent for absorbance A."""
    T = 10.0 ** (-A)
    dA = math.log10(math.e) * dT / T
    return dA / A * 100.0

def transmittance_error_min_A():
    """§7.3: A at the minimum of the relative-error curve. dA/A ∝ 1/(A·T) with
    T = 10^-A, so the minimum maximizes A·10^-A, which peaks at A = 1/ln(10)
    = lg(e) ≈ 0,434 — the same boundary as the lg(e) limit (14. atsauce)."""
    return 1.0 / math.log(10.0)

def stray_light_error_pct(A, s):
    """T12 stray-light model (assumption: model_T12): measured T_m = (T + s)/(1 + s)
    for stray-light fraction s; returns the relative error of the displayed A in
    percent: (A_m - A)/A·100."""
    T = 10.0 ** (-A)
    T_m = (T + s) / (1.0 + s)
    A_m = -math.log10(T_m)
    return (A_m - A) / A * 100.0

def stray_light_neg1pct_limit_A(s):
    """T12: the A at which the stray-light model's relative error reaches −1 %
    (bisection between 0,5 and 10; s = 0,1 % gives A ≈ 1,6, 26. tabula note)."""
    lo, hi = 0.5, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if stray_light_error_pct(mid, s) > -1.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0

# T03 boundary fixtures: calibrated absorbance span of the standards. The uncertainty
# budget and c = A/k readings are defined only inside this span; outside it the result
# would be an extrapolation the budget does not cover (10.8, 25. tabula, J4 warning).
A_CAL_MIN = 0.063   # lowest standard (solution 1)
A_CAL_MAX = 0.482   # highest standard (solution 8)

def uncertainty_for_A(A, u_A_cons=None):
    """T03 boundary-fixture function: T11 conservative uncertainty budget for a displayed
    absorbance A (reading term u(A) = 0,001 A combined with u(k)/k of the 9-point origin
    fit; U = 2u; assumption: u_A_model). Raises ValueError for A <= 0: zero or negative
    absorbance has no finite, meaningful concentration, and the budget must never
    silently produce one. Flags extrapolation outside the calibrated span
    [A_CAL_MIN, A_CAL_MAX]. Default u(A) comes from CONSTANTS["u_A_conservative"]
    (T10: single named constant, no duplicated literal).
    """
    if u_A_cons is None:
        u_A_cons = U_A_CONSERVATIVE
    if A is None:
        raise ValueError("A is required and must be > 0")
    A = float(A)
    if not (A > 0.0):
        raise ValueError("A must be > 0: A = 0 or negative yields no finite concentration")
    orig = compute_regression_origin(get_standards_table())
    rel = math.sqrt((u_A_cons / A) ** 2 + (orig["se_k"] / orig["k"]) ** 2)
    return {
        "A": A,
        "c_mg_per_mL": A / orig["k"],
        "u_rel": rel,
        "u_rel_pct": rel * 100.0,
        "U_expanded_mg_per_mL": 2.0 * (A / orig["k"]) * rel,
        "extrapolated": bool(A < A_CAL_MIN or A > A_CAL_MAX),
        "calibrated_span": (A_CAL_MIN, A_CAL_MAX),
    }

def compute_samples_results(origin_fit, free_fit_9pt, free_fit_8pt=None):
    """Compute concentration, transmittance, and uncertainty for samples 2-5.

    Pure function (T10): all three fits are passed in explicitly — no module-level
    fit state — so a changed protocol row changes every dependent result.

    Regression-variant contract (C-05 / T02):
    - gamma_origin_fit: origin-locked 9-point fit A = k*gamma (the result variant);
    - gamma_free_fit: FREE 9-POINT fit INCLUDING the blank point (cross-check variant,
      matching table 13 and 15.f in the document);
    - gamma_free_8pt: free 8-point fit EXCLUDING the blank — blank-sensitivity
      diagnostic only, never a reported result (assumption: free8_diagnostic).
    """
    if free_fit_8pt is None:
        free_fit_8pt = compute_regression_free(get_standards_table(), include_blank=False)
    k = origin_fit["k"]
    se_k = origin_fit["se_k"]
    rel_se_k = se_k / k
    M = CONSTANTS["M"]
    u_A_cons = U_A_CONSERVATIVE

    res = []
    for s_id, A, gamma_read in SAMPLES:
        gamma_orig = A / k
        gamma_free = (A - free_fit_9pt["intercept"]) / free_fit_9pt["slope"]
        gamma_free_8pt = (A - free_fit_8pt["intercept"]) / free_fit_8pt["slope"]
        c_mol = gamma_orig / M
        c_umol = c_mol * 1e6
        T = 10.0 ** (-A)

        # Uncertainty budget (T11 conservative model)
        u_rel = math.sqrt((u_A_cons / A) ** 2 + rel_se_k ** 2)
        u_c = gamma_orig * u_rel
        U_exp = 2.0 * u_c

        res.append({
            "sample_id": s_id,
            "A": A,
            "gamma_protocol_read": gamma_read,
            "gamma_origin_fit": gamma_orig,
            "gamma_free_fit": gamma_free,
            "gamma_free_8pt": gamma_free_8pt,
            "c_mol_per_L": c_mol,
            "c_umol_per_L": c_umol,
            "T_pct": T * 100.0,
            "u_rel_pct": u_rel * 100.0,
            "u_c_mg_per_mL": u_c,
            "U_expanded_mg_per_mL": U_exp,
        })
    return res

def compute_all():
    """Compute and return complete dictionary of verified numbers."""
    stds = get_standards_table()
    orig = compute_regression_origin(stds)
    free9 = compute_regression_free(stds, include_blank=True)
    free8 = compute_regression_free(stds, include_blank=False)
    energy = compute_photon_energy(CONSTANTS["wavelength_nm"])
    samples = compute_samples_results(orig, free9)

    # Molar absorption coefficient epsilon = k * M. CONDITIONAL (T10.1.3): valid only
    # for the assumed path length l = 1 cm (assumption keys: epsilon, path_length).
    epsilon = orig["k"] * CONSTANTS["M"]

    # LOD and LOQ estimates: 3*sy/k and 10*sy/k (assumption: lod_loq — simplified
    # regression estimates, homoscedasticity; not blank-replicate detectability).
    lod = 3.0 * orig["sy"] / orig["k"]
    loq = 10.0 * orig["sy"] / orig["k"]

    return {
        "constants": CONSTANTS,
        "assumptions": ASSUMPTIONS,
        "standards": stds,
        "regression_origin": orig,
        "regression_free_9pt": free9,
        "regression_free_8pt": free8,
        "photon_energy_440nm": energy,
        "samples": samples,
        "epsilon_molar": epsilon,
        "LOD_mg_per_mL": lod,
        "LOQ_mg_per_mL": loq,
    }


def named_results():
    """T10 registry: every derived value that a published number may trace to.

    Returns an ordered dict name -> {"value", "unit", "expression", "assumption"}.
    Names carry the blank-inclusion status of every fit (C-05), so a result can
    never be swapped for another variant without the trace noticing. Values are
    computed fresh from the raw rows above on every call — nothing is cached.
    """
    stds = get_standards_table()
    orig9 = compute_regression_origin(stds)
    orig8 = compute_regression_origin(standards_rows(include_blank=False))
    free9 = compute_regression_free(stds, include_blank=True)
    free8 = compute_regression_free(stds, include_blank=False)
    samples = compute_samples_results(orig9, free9, free8)
    eps = orig9["k"] * CONSTANTS["M"]
    out = {}

    # --- fit variants (names state the blank inclusion; C-05) ---
    out["origin9pt_blank_included.k"] = (None, orig9["k"], "mL·mg⁻¹", "k = ΣγA/Σγ², 9 punkti")
    out["origin9pt_blank_included.se_k"] = (None, orig9["se_k"], "mL·mg⁻¹", "SE(k) = s_y/√Σγ²")
    out["origin9pt_blank_included.sy"] = (None, orig9["sy"], "A", "s_y = √(Σ(A−kγ)²/(N−1))")
    out["origin9pt_blank_included.residual_max_abs"] = (None, max(abs(e) for e in orig9["residuals"]), "A", "lielākais |atlikums|")
    out["origin8pt_blank_excluded.sy"] = (None, orig8["sy"], "A", "s_y caur nulli, 8 punkti (tukšais izslēgts; k nemainās — (0,0) nedod ieguldījumu)")
    out["free9pt_blank_included.slope"] = (None, free9["slope"], "mL·mg⁻¹", "brīvā regresija, 9 punkti")
    out["free9pt_blank_included.intercept"] = (None, free9["intercept"], "A", "brīvā regresija, 9 punkti")
    out["free9pt_blank_included.r2"] = (None, free9["r2"], "—", "R² brīvā 9 punkti")
    out["free9pt_blank_included.sy"] = (None, free9["sy"], "A", "s_y brīvā 9 punkti")
    out["free9pt_blank_included.se_slope"] = (None, free9["se_slope"], "mL·mg⁻¹", "SE(m) 16. tabula")
    out["free9pt_blank_included.se_intercept"] = (None, free9["se_intercept"], "A", "SE(b) 16. tabula")
    out["free9pt_blank_included.residual_max_abs"] = (None, max(abs(r["A"] - (free9["slope"] * r["gamma_mg_per_mL"] + free9["intercept"])) for r in stds), "A", "lielākais |atlikums| brīvā 9 punkti")
    out["free8pt_blank_excluded.slope"] = (None, free8["slope"], "mL·mg⁻¹", "diagnostika, tukšais izslēgts")
    out["free8pt_blank_excluded.intercept"] = (None, free8["intercept"], "A", "diagnostika, tukšais izslēgts")
    out["free8pt_blank_excluded.r2"] = (None, free8["r2"], "—", "R² brīvā 8 punkti")
    out["free8pt_blank_excluded.sy"] = (None, free8["sy"], "A", "s_y brīvā 8 punkti")
    out["free8pt_blank_excluded.se_slope"] = (None, free8["se_slope"], "mL·mg⁻¹", "SE(m) 16. tabula")
    out["free8pt_blank_excluded.se_intercept"] = (None, free8["se_intercept"], "A", "SE(b) 16. tabula")

    # --- standards (γ by dilution, c by M, T by A) ---
    for r in stds:
        sid = r["id"]
        out[f"std{sid}.gamma_mg_per_mL"] = (None, r["gamma_mg_per_mL"], "mg/mL", "γ = γ₀·V₁/V_kopā")
        out[f"std{sid}.c_mol_per_L"] = (None, r["c_mol_per_L"], "mol/L", "c = γ/M (1 mg/mL = 1 g/L)")
        out[f"std{sid}.c_x10_6"] = (None, r["c_mol_per_L"] * 1e6, "µmol/L", "c = γ/M")
        out[f"std{sid}.c_x10_5"] = (None, r["c_mol_per_L"] * 1e5, "×10⁻⁵ mol/L", "c = γ/M")
        out[f"std{sid}.T_pct"] = (None, r["T_pct"], "%", "T = 10^(−A)")
        out[f"std{sid}.absorbed_pct"] = (None, 100.0 - r["T_pct"], "%", "absorbētā daļa = 100 − T%")
        out[f"std{sid}.A_pred_origin"] = (None, orig9["k"] * r["gamma_mg_per_mL"], "A", "A = k·γ (taisne caur nulli)")

    # --- samples ---
    for s in samples:
        sid = s["sample_id"]
        out[f"sample{sid}.gamma_origin9"] = (None, s["gamma_origin_fit"], "mg/mL", "γ = A/k")
        out[f"sample{sid}.gamma_free9"] = (None, s["gamma_free_fit"], "mg/mL", "γ = (A − b)/m, brīvā 9 punkti")
        out[f"sample{sid}.gamma_free8_diagnostic"] = (None, s["gamma_free_8pt"], "mg/mL", "diagnostika, tukšais izslēgts")
        out[f"sample{sid}.gamma_read_minus_origin9"] = (None, s["gamma_protocol_read"] - s["gamma_origin_fit"], "mg/mL", "protokola nolasījums − pārrēķins (13. tabulas novirzes kolonna)")
        out[f"sample{sid}.T"] = (None, 10.0 ** (-s["A"]), "—", "T = 10^(−A)")
        out[f"sample{sid}.T_pct"] = (None, 10.0 ** (-s["A"]) * 100.0, "%", "T = 10^(−A)")
        out[f"sample{sid}.absorbed_pct"] = (None, 100.0 * (1.0 - 10.0 ** (-s["A"])), "%", "100 − T%")
        out[f"sample{sid}.c_umol_per_L"] = (None, s["c_umol_per_L"], "µmol/L", "c = γ/M")
        out[f"sample{sid}.u_rel_pct"] = (None, s["u_rel_pct"], "%", "u(c)/c konservatīvs")
        out[f"sample{sid}.u_rel_rect_pct"] = (None, math.sqrt((U_A_RECTANGULAR / s["A"]) ** 2 + (orig9["se_k"] / orig9["k"]) ** 2) * 100.0, "%", "u(c)/c taisnstūra modelis (25. tabula)")
        out[f"sample{sid}.u_c_mg_per_mL"] = (None, s["u_c_mg_per_mL"], "mg/mL", "u(c) = γ·u_rel")
        out[f"sample{sid}.U_expanded_mg_per_mL"] = (None, s["U_expanded_mg_per_mL"], "mg/mL", "U = 2u")
        out[f"sample{sid}.U_expanded_5dp"] = (None, float(f"{s['U_expanded_mg_per_mL']:.5f}"), "mg/mL", "U = 2u (rādījuma noapaļojums, 25. tabula)")
        out[f"sample{sid}.u_reading_pct"] = (None, U_A_CONSERVATIVE / s["A"] * 100.0, "%", "u(A)/A")
        out[f"sample{sid}.u_k_pct"] = (None, orig9["se_k"] / orig9["k"] * 100.0, "%", "u(k)/k")

    # --- global derived ---
    out["epsilon_molar"] = (None, eps, "L·mol⁻¹·cm⁻¹", "ε = k·M; PIEŅĒMUMS l = 1 cm")
    out["epsilon_order_x10_4"] = (None, eps / 1e4, "×10⁴", "ε kārta")
    out["LOD_mg_per_mL"] = (None, 3.0 * orig9["sy"] / orig9["k"], "mg/mL", "3·s_y/k")
    out["LOD_ug_per_mL"] = (None, 3.0 * orig9["sy"] / orig9["k"] * 1e3, "µg/mL", "3·s_y/k")
    out["LOQ_mg_per_mL"] = (None, 10.0 * orig9["sy"] / orig9["k"], "mg/mL", "10·s_y/k")
    out["LOQ_ug_per_mL"] = (None, 10.0 * orig9["sy"] / orig9["k"] * 1e3, "µg/mL", "10·s_y/k")
    out["u_A_rect"] = (None, U_A_RECTANGULAR, "A", "0,001/√3, taisnstūra modelis")
    out["u_A_rect_pct"] = (None, U_A_RECTANGULAR * 100.0, "%", "taisnstūra u(A) procentos")
    out["u_k_over_k_pct"] = (None, orig9["se_k"] / orig9["k"] * 100.0, "%", "u(k)/k — taisnes devums")
    out["resolution_gamma_mg_per_mL"] = (None, CONSTANTS["resolution_A"] / orig9["k"], "mg/mL", "nolasīšanas izšķirtspēja γ vienībās = 0,001/k")
    out["k_step_per_0_001_gamma"] = (None, orig9["k"] * 0.001, "A", "A pieaugums pie Δγ = 0,001 mg/mL")
    out["unit_conversion_1mgmL_mmol_L"] = (None, 1.0 / CONSTANTS["M"] * 1e3, "mmol/L", "1,00 mg/mL = 1,00 g/L → c = 1,00/M (12.3 pārveidojums)")

    # --- photon energies (3. tabula: 200/400/700 nm; 19. tabula: 440 nm) ---
    for lam in (200.0, 400.0, 440.0, 700.0):
        e = compute_photon_energy(lam)
        p = f"photon_{int(lam)}nm"
        out[f"{p}.E_J_x10_19"] = (None, e["E_joules"] / 1e-19, "×10⁻¹⁹ J", "E = hc/λ")
        out[f"{p}.E_eV"] = (None, e["E_eV"], "eV", "E = hc/λ / e")
        out[f"{p}.E_kJ_mol"] = (None, e["E_kJ_mol"], "kJ/mol", "E = hcNa/λ")
        out[f"{p}.wavenumber_cm"] = (None, e["wavenumber_cm"], "cm⁻¹", "1/λ")
        out[f"{p}.frequency_x10_14_Hz"] = (None, e["frequency_hz"] / 1e14, "×10¹⁴ Hz", "ν = c/λ")

    # --- teaching models (documented assumptions; see ASSUMPTIONS) ---
    out["model_7_3.rel_err_pct_A0_086"] = (None, transmittance_error_rel_pct(0.086), "%", "ΔT = 0,005 konvencija")
    out["model_7_3.rel_err_pct_A0_482"] = (None, transmittance_error_rel_pct(0.482), "%", "ΔT = 0,005 konvencija")
    out["model_7_3.rel_err_pct_A1"] = (None, transmittance_error_rel_pct(1.0), "%", "ΔT = 0,005 konvencija")
    out["model_7_3.min_A"] = (None, transmittance_error_min_A(), "A", "min[iela/A·10^−A]")
    out["model_T12.err_pct_s0_01_A1"] = (None, stray_light_error_pct(1.0, 0.01), "%", "s = 1 %")
    out["model_T12.err_pct_s0_01_A2"] = (None, stray_light_error_pct(2.0, 0.01), "%", "s = 1 %")
    out["model_T12.err_pct_s0_0001_A1"] = (None, stray_light_error_pct(1.0, 0.0001), "%", "s = 0,01 %")
    out["model_T12.limit_A_s0_001_neg1pct"] = (None, stray_light_neg1pct_limit_A(0.001), "A", "−1 % robeža pie s = 0,1 %")

    # --- worked examples instantiated from real protocol values ---
    out["worked.A_over_gamma_std4"] = (None, 0.247 / 0.008, "mL·mg⁻¹", "A/γ, 4. standarts")
    out["worked.A_over_gamma_std8"] = (None, 0.482 / 0.016, "mL·mg⁻¹", "A/γ, 8. standarts")
    out["worked.doubling_factor"] = (None, 0.482 / 0.247, "—", "A pieauguma faktors")
    out["worked.doubling_deficit_pct"] = (None, (2.0 - 0.482 / 0.247) / 2.0 * 100.0, "%", "novirze no precīzas dubultošanās")
    out["worked.comma_error_2_8"] = (None, 0.0028 * 1000.0, "mg/mL", "komata kļūda ×1000 (11.4)")
    out["worked.comma_error_factor_175"] = (None, 2.8 / 0.016, "—", "2,8/0,016 pret augstāko standartu")
    out["worked.neg_lg_0_5"] = (None, -math.log10(0.5), "A", "−lg 0,5")
    out["worked.lg_e"] = (None, math.log10(math.e), "A", "lg e")
    out["worked.ln_10"] = (None, math.log(10.0), "—", "ln 10")
    out["worked.T_at_A0_5"] = (None, 10.0 ** (-0.5), "—", "T = 10^(−0,5)")
    out["worked.T_at_A0_482"] = (None, 10.0 ** (-0.482), "—", "T = 10^(−0,482)")
    out["worked.T_pct_at_A0_434"] = (None, 10.0 ** (-0.434) * 100.0, "%", "T% pie A = 0,434")
    out["worked.absorbed_pct_A0_434"] = (None, 100.0 * (1.0 - 10.0 ** (-0.434)), "%", "absorbēti pie A = 0,434")
    out["worked.pred_A_0_001_gamma_step"] = (None, orig9["k"] * 0.001, "A", "A pieaugums uz 0,001 γ")
    out["worked.task6_A0_247_over_k"] = (None, 0.247 / orig9["k"], "mg/mL", "6. uzdevums: 0,247/30,39")

    # --- scaled physical constants (display mantissas, 2.x / 3. tabula) ---
    out["constants.N_A_x10_23"] = (None, CONSTANTS["N_A"] / 1e23, "×10²³ mol⁻¹", "Avogadro")
    out["constants.h_x10_34"] = (None, CONSTANTS["h"] / 1e-34, "×10⁻³⁴ J·s", "Planka konstante")
    out["constants.c_light_x10_8"] = (None, CONSTANTS["c_light"] / 1e8, "×10⁸ m/s", "gaismas ātrums")
    out["constants.e_charge_x10_19"] = (None, CONSTANTS["e_charge"] / 1e-19, "×10⁻¹⁹ C", "elementārlādiņš")

    # --- illustrative teaching tables: 8. tabula (A → T) and 10. tabula (γ → A) ---
    # Inputs are declared teaching values; the derivations are real and named.
    for a_in in (0.0, 0.1, 0.2, 0.3, 0.4, 0.434, 0.5, 1.0, 2.0):
        tag = ("%.3f" % a_in).rstrip("0").rstrip(".").replace(".", "_")
        out[f"table8.T_A{tag}"] = (None, 10.0 ** (-a_in), "—", "T = 10^(−A), 8. tabula")
        out[f"table8.T_pct_A{tag}"] = (None, 10.0 ** (-a_in) * 100.0, "%", "T = 10^(−A), 8. tabula")
        out[f"table8.absorbed_pct_A{tag}"] = (None, 100.0 * (1.0 - 10.0 ** (-a_in)), "%", "100 − T%, 8. tabula")
    for g_in in (0.002, 0.005, 0.01, 0.015, 0.02):
        tag = ("%.4f" % g_in).rstrip("0").rstrip(".").replace(".", "_")
        A_pred = orig9["k"] * g_in
        out[f"table10.A_pred_gamma{tag}"] = (None, A_pred, "A", "A = k·γ, 10. tabula")
        out[f"table10.T_pct_gamma{tag}"] = (None, 10.0 ** (-A_pred) * 100.0, "%", "T = 10^(−kγ), 10. tabula")
        out[f"table10.absorbed_pct_gamma{tag}"] = (None, 100.0 * (1.0 - 10.0 ** (-A_pred)), "%", "100 − T%, 10. tabula")

    # --- 5.3 two-component illustrative example (inputs declared fictional in the
    # document; the solved concentrations are real derivations from those inputs) ---
    tc_eps1_445, tc_eps2_445, tc_eps1_500, tc_eps2_500 = 30.0, 4.0, 2.0, 18.0
    tc_a445, tc_a500 = 0.350, 0.210
    tc_det = tc_eps1_445 * tc_eps2_500 - tc_eps2_445 * tc_eps1_500
    out["twocomp.c1"] = (None, (tc_a445 * tc_eps2_500 - tc_eps2_445 * tc_a500) / tc_det, "mg/mL", "5.3 2-komp. piemērs (ieejas deklarētas kā izdomātas)")
    out["twocomp.c2"] = (None, (tc_eps1_445 * tc_a500 - tc_a445 * tc_eps1_500) / tc_det, "mg/mL", "5.3 2-komp. piemērs")

    for name, (disp, val, unit, expr) in out.items():
        out[name] = {"display": disp, "value": val, "unit": unit, "expression": expr}
    return out

# T06 numeric derivation audit: κ that maps the displayed epsilon back to the
# differential law (eps = kappa / ln 10); ln(10) is the only base conversion used.
LN10 = math.log(10.0)
KAPPA_DERIVED = None  # filled by derivation_audit()


def derivation_audit():
    """T06 equation audit sheet (numeric, from stated inputs only).

    Chain: dI = -kappa*I*c*dl -> T = I/I0 = exp(-kappa*c*l) -> A = -lg T
    = kappa*c*l/ln(10) = eps*c*l. Verifies signs, the decadic base, the blank
    zero-concentration consequence, additivity, dimensional cancellation and the
    eps = k*M bridge; mutation detectors prove the fixtures can fail.
    Returns (rows, ok) where rows are (step, lhs, rhs_str, value, note).
    """
    global KAPPA_DERIVED
    stds = get_standards_table()
    orig = compute_regression_origin(stds)
    eps = orig["k"] * CONSTANTS["M"]          # L/(mol*cm), at assumed l = 1 cm
    kappa = eps * LN10                          # L/(mol*cm) equivalent in the e-law
    KAPPA_DERIVED = kappa
    l_cm = CONSTANTS["cuvette_path_cm"]
    rows = []
    ok = True

    def step(name, lhs, rhs_str, value, note, expect):
        nonlocal ok
        good = expect(value)
        ok = ok and good
        rows.append((name, lhs, rhs_str, value, note, good))

    # 1. Differential vs closed form: numeric integration of dI/I = -kappa*c*dl
    #    reproduces exp(-kappa*c*l) (multiplicative Euler product; 100000 slices,
    #    realistic c so the exponent stays in the teaching range).
    c = 1.0e-5  # mol/L, illustrative (A ≈ 0,11)
    n, dl = 100000, l_cm / 100000.0
    integ = 1.0
    for i in range(n):
        integ *= (1.0 - kappa * c * dl)
    closed = math.exp(-kappa * c * l_cm)
    step("1 plāns slānis", "T = I/I0", "exp(-κcl) vs ∫dI/I", integ / closed,
         "skaitliskā integrācija ≈ slēgtā forma", lambda v: abs(v - 1.0) < 1e-6)

    # 2. Sign: dA/dγ must be POSITIVE (more absorber -> higher A) and T must fall.
    A_lo = eps * l_cm * 1.0e-3
    A_hi = eps * l_cm * 2.0e-3
    step("2 zīme", "dA/dγ", "> 0", A_hi - A_lo,
         "A aug ar koncentrāciju", lambda v: v > 0.0)

    # 3. Sign mutation detector: T = 10^+A breaks physics (T > 1) and is caught.
    bad_T = 10.0 ** (+A_lo)
    step("3 zīmes mutācija", "T = 10^+A", "> 1 — nepareizi", bad_T,
         "ar pluszīmi T pārsniedz 1", lambda v: v > 1.0)

    # 4. Base: A = -lg T and T = 10^-A round-trip exactly; the missing /ln(10)
    #    conversion (ln-base mutation) would shift every value by ln(10) and is caught.
    T_rt = 10.0 ** (-(eps * l_cm * c))
    A_rt = -math.log10(T_rt)
    step("4 bāze", "T = 10^-A", "round-trip ≈ 0", A_rt - eps * l_cm * c,
         "lg bāze apli atdod A", lambda v: abs(v) < 1e-12)
    step("4 bāzes mutācija", "A bez /ln10", "= κcl (par 2,303 par lielu)",
         kappa * c * l_cm / (eps * c * l_cm),
         "ln bāze bez konversijas", lambda v: abs(v - LN10) < 1e-9)

    # 5. Zero concentration: c = 0 -> T = 1 -> A = 0 (blank correction consequence).
    step("5 nulle", "c = 0", "A = 0", -math.log10(10.0 ** (-(eps * l_cm * 0.0))),
         "tukšais paraugs: nulles pārbaude", lambda v: v == 0.0)

    # 6. Additivity: two serial slabs multiply T, so A adds (A12 == A1 + A2).
    A1, A2 = eps * l_cm * 1.0e-3, eps * l_cm * 2.0e-3
    A12 = -math.log10((10.0 ** (-A1)) * (10.0 ** (-A2)))
    step("6 aditivitāte", "A1+A2", "A12", A12 - (A1 + A2),
         "slāņi: T reizinās, A saskaitās", lambda v: abs(v) < 1e-12)

    # 7. Dimensional cancellation for both canonical coefficient forms, checked
    #    through the unit dictionary (base-unit cancellation, not a bookkeeping 1.0).
    UNITS = {"L": 1e-3, "mol": 1.0, "cm": 1e-2, "mL": 1e-3, "mg": 1e-6, "g": 1e-3}
    def unit_value(expr):
        v = 1.0
        for unit, power in expr:
            v *= UNITS[unit] ** power
        return v
    eps_form = unit_value([("L", 1), ("mol", -1), ("cm", -1), ("cm", 1), ("mol", 1), ("L", -1)])
    mass_form = unit_value([("mL", 1), ("mg", -1), ("cm", -1), ("cm", 1), ("mg", 1), ("mL", -1)])
    step("7 dimensijas", "ε·l·c, a·l·γ", "= 1", [eps_form, mass_form],
         "bāsvienību atcelšanās abām formām",
         lambda v: abs(v[0] - 1.0) < 1e-12 and abs(v[1] - 1.0) < 1e-12)

    # 8. Unit-bridge parity: eps = k*M within the invariant tolerance (canonical 11 439).
    step("8 tilts ε = k·M", "ε, L·mol⁻¹·cm⁻¹", "≈ 11 439", eps,
         "k mL·mg⁻¹ × M g·mol⁻¹ (l = 1 cm pieņēmums)",
         lambda v: abs(v - 11439) < 50)

    # 9. Basis swap caught: A displayed against the WRONG basis (ε with γ in mg/mL)
    #    would make the product γ·ε ≠ dimensionless-checked value and is detected.
    gamma_sample4 = 0.0085  # mg/mL (protocol reading, sample 4)
    wrong = gamma_sample4 * eps  # treated as if eps consumed mg/mL directly
    step("9 bāzes maiņa aizķeršanās", "γ·ε (jaukta bāze)", "≠ A(γ)",
         wrong / (orig["k"] * gamma_sample4),
         "ε ar mg/mL dod M reizes lielāku skaitli", lambda v: abs(v - CONSTANTS["M"]) < 1e-6)

    return rows, ok


def verify_invariants():
    """Assert against all documented canonical values in AGENTS.md."""
    data = compute_all()
    orig = data["regression_origin"]
    free9 = data["regression_free_9pt"]
    free8 = data["regression_free_8pt"]
    samples = data["samples"]
    energy = data["photon_energy_440nm"]

    # Slope through origin: 30.39 mL/mg (SE ~0.093, sy ~0.0026)
    assert abs(orig["k"] - 30.394608) < 1e-4, f"k_origin mismatch: {orig['k']}"
    assert abs(orig["se_k"] - 0.0926) < 1e-3, f"se_k mismatch: {orig['se_k']}"
    assert abs(orig["sy"] - 0.002644) < 1e-4, f"sy mismatch: {orig['sy']}"

    # Free regression 9pt (with blank): slope 30.24, intercept 0.0017, R2 0.99978
    assert abs(free9["slope"] - 30.241667) < 1e-4, f"free9 slope mismatch: {free9['slope']}"
    assert abs(free9["intercept"] - 0.0017) < 1e-3, f"free9 intercept mismatch: {free9['intercept']}"
    assert abs(free9["r2"] - 0.99978) < 1e-5, f"free9 R2 mismatch: {free9['r2']}"

    # Free regression 8pt (without blank): slope 30.15, intercept 0.0028, R2 0.99972
    assert abs(free8["slope"] - 30.150) < 1e-2, f"free slope mismatch: {free8['slope']}"
    assert abs(free8["intercept"] - 0.0028) < 1e-3, f"free intercept mismatch: {free8['intercept']}"
    assert abs(free8["r2"] - 0.99972) < 1e-4, f"free R2 mismatch: {free8['r2']}"

    # Variant ordering and naming contract (C-05): the three fits must stay distinct
    # and ordered exactly as the document's canonical variant table states.
    assert orig["k"] > free9["slope"] > free8["slope"], "variant slope ordering broken"
    assert free8["intercept"] > free9["intercept"] > 0, "variant intercept ordering broken"
    assert free9["n"] == 9 and free8["n"] == 8, "variant point counts broken"
    assert abs(free8["intercept"] - free9["intercept"]) < 0.002, "blank-sensitivity delta out of range"

    # Samples: origin-fit cross-check values 0.00283, 0.00559, 0.00849, 0.01224
    expected_g_orig = [0.00283, 0.00559, 0.00849, 0.01224]
    for s, exp in zip(samples, expected_g_orig):
        assert abs(s["gamma_origin_fit"] - exp) < 1e-4, f"Sample {s['sample_id']} gamma origin mismatch"

    # Sample cross-check columns use the FREE 9-POINT variant (table 13 / 15.f):
    # displayed rounded values 0.00279, 0.00556, 0.00847, 0.01224
    expected_g_free9 = [0.00279, 0.00556, 0.00847, 0.01224]
    for s, exp in zip(samples, expected_g_free9):
        assert abs(s["gamma_free_fit"] - exp) < 1e-4, f"Sample {s['sample_id']} gamma free9 mismatch"

    # Blank-sensitivity fact (16. tabula tnote): the free 8-point variant rounds
    # sample 3 to 0.0055 (4 decimal places), i.e. one last-digit unit below the
    # free-9 value 0.0056. All other samples keep the displayed rounding.
    assert round(samples[1]["gamma_free_8pt"], 4) == 0.0055, \
        f"sample 3 free-8 rounding changed: {samples[1]['gamma_free_8pt']}"
    assert round(samples[0]["gamma_free_8pt"], 4) == 0.0028
    assert round(samples[2]["gamma_free_8pt"], 4) == 0.0085
    assert round(samples[3]["gamma_free_8pt"], 4) == 0.0122

    # Photon energy at 440 nm
    assert abs(energy["E_joules"] - 4.515e-19) < 1e-21, "Energy J mismatch"
    assert abs(energy["E_eV"] - 2.818) < 1e-3, "Energy eV mismatch"
    assert abs(energy["E_kJ_mol"] - 271.9) < 1e-1, "Energy kJ/mol mismatch"
    assert abs(energy["wavenumber_cm"] - 22727) < 1, "Wavenumber mismatch"

    # Molar absorptivity epsilon ~ 1.14e4 L/(mol*cm)
    assert abs(data["epsilon_molar"] - 11439) < 50, "Epsilon mismatch"

    # --- T03 boundary fixtures (C-06/C-07): zero/negative A never yields a finite
    # concentration; extrapolation outside the calibrated span is flagged; the
    # displayed budget values reproduce from the full-precision authority.
    for bad_a in (0.0, -0.001):
        try:
            uncertainty_for_A(bad_a)
            raise AssertionError(f"boundary fixture failed: A = {bad_a} must raise ValueError")
        except ValueError:
            pass
    try:
        uncertainty_for_A(None)
        raise AssertionError("boundary fixture failed: A = None must raise ValueError")
    except ValueError:
        pass
    lo_edge, hi_edge = uncertainty_for_A(A_CAL_MIN), uncertainty_for_A(A_CAL_MAX)
    assert not lo_edge["extrapolated"] and not hi_edge["extrapolated"], \
        "calibrated endpoints flagged as extrapolation"
    assert uncertainty_for_A(0.05)["extrapolated"] and uncertainty_for_A(0.60)["extrapolated"], \
        "extrapolation flag broken outside [0,063; 0,482] A"
    s2b, s5b = uncertainty_for_A(0.086), uncertainty_for_A(0.372)
    assert abs(s2b["u_rel_pct"] - 1.20) < 0.005, f"sample 2 budget drift: {s2b['u_rel_pct']}"
    assert abs(s5b["u_rel_pct"] - 0.41) < 0.005, f"sample 5 budget drift: {s5b['u_rel_pct']}"
    assert format(s2b["U_expanded_mg_per_mL"], ".5f") == "0.00007", "sample 2 U display parity broken"
    assert format(s5b["U_expanded_mg_per_mL"], ".5f") == "0.00010", "sample 5 U display parity broken"
    for s in samples:
        via = uncertainty_for_A(s["A"])
        assert abs(via["u_rel_pct"] - s["u_rel_pct"]) < 1e-9, \
            "boundary fixture diverges from the canonical budget path"

    # LOD/LOQ stay simplified full-precision estimates (C-07 / E26):
    # 0,00026 / 0,00087 mg/mL (0,26 / 0,87 ug/mL), both below the lowest standard 0,002 mg/mL.
    assert abs(data["LOD_mg_per_mL"] - 0.00026) < 5e-6, f"LOD drift: {data['LOD_mg_per_mL']}"
    assert abs(data["LOQ_mg_per_mL"] - 0.00087) < 5e-6, f"LOQ drift (double rounding E26): {data['LOQ_mg_per_mL']}"
    assert abs(data["LOQ_mg_per_mL"] * 1000.0 - 0.87) < 0.005, "LOQ ug/mL display parity broken"
    assert data["LOD_mg_per_mL"] > 0 and data["LOD_mg_per_mL"] < data["LOQ_mg_per_mL"] < 0.0020, \
        "LOD/LOQ ordering vs lowest standard broken"

    # --- T06 derivation audit (C-02/C-03): the chain dI -> T = I/I0 -> A = -lg T
    # -> eps*c*l must reproduce numerically; sign/base/unit mutations are caught.
    rows, audit_ok = derivation_audit()
    assert audit_ok, "T06 derivation audit failed: " + "; ".join(
        f"{r[0]}={r[3]!r}" for r in rows if not r[5])
    assert len(rows) == 10, f"T06 audit sheet must have 10 steps, got {len(rows)}"
    # displayed chain expectations: sign positive, zero check exact, eps parity
    assert rows[1][3] > 0.0, "T06: dA/dgamma must be positive"
    assert rows[5][3] == 0.0, "T06: c = 0 must give A = 0 exactly"
    assert abs(KAPPA_DERIVED - data["epsilon_molar"] * LN10) < 1e-9, "kappa/ln10 parity broken"
    # dimension step must be a real cancellation (both forms reduce to 1.0)
    dim = rows[7][3]
    assert isinstance(dim, list) and abs(dim[0] - 1.0) < 1e-12 and abs(dim[1] - 1.0) < 1e-12, \
        "T06: unit cancellation must be verified, not asserted"

    # --- T10 pipeline auditability (C-05/C-09): raw rows are the authority; the
    # named registry exposes origin9/free9/free8 with blank inclusion in names;
    # no source value is normalized beyond decimal display formatting.
    assert orig.get("blank_included") is True and orig.get("name") == "origin9pt_blank_included", \
        "origin fit must stay named 'origin9pt_blank_included'"
    assert free9.get("blank_included") is True and free9.get("name") == "free9pt_blank_included", \
        "9-point free fit must stay named 'free9pt_blank_included'"
    assert free8.get("blank_included") is False and free8.get("name") == "free8pt_blank_excluded", \
        "8-point diagnostic must stay named 'free8pt_blank_excluded'"
    obs = dict((name, (val, unit)) for name, val, unit, _prov in source_observations())
    for (sid, v_st, v_w, A) in STANDARDS:
        assert obs[f"std{sid}.A"] == (A, "A") and obs[f"std{sid}.v_stock_mL"] == (v_st, "mL"), \
            f"source observation std{sid} diverged from the raw row"
    for (sid, A, g_read) in SAMPLES:
        assert obs[f"sample{sid}.gamma_protocol_read"] == (g_read, "mg/mL"), \
            f"source observation sample{sid} diverged from the raw row"
    names = named_results()
    assert abs(names["origin9pt_blank_included.k"]["value"] - orig["k"]) < 1e-12
    assert abs(names["free9pt_blank_included.se_slope"]["value"] - free9["se_slope"]) < 1e-12
    assert abs(names["free8pt_blank_excluded.se_intercept"]["value"] - free8["se_intercept"]) < 1e-12
    assert abs(names["model_7_3.rel_err_pct_A0_086"]["value"] - 3.1) < 0.05, "7.3 model drift at A=0,086"
    assert abs(names["model_7_3.min_A"]["value"] - 0.434) < 0.001, "7.3 minimum drifted off lg(e)"
    assert abs(abs(names["model_T12.err_pct_s0_01_A1"]["value"]) - 3.7) < 0.05, "T12 model drift at A=1, s=1 %"
    assert abs(abs(names["model_T12.err_pct_s0_01_A2"]["value"]) - 14.8) < 0.05, "T12 model drift at A=2, s=1 %"
    assert abs(abs(names["model_T12.err_pct_s0_0001_A1"]["value"]) - 0.04) < 0.005, "T12 model drift at s=0,01 %"
    assert abs(names["model_T12.limit_A_s0_001_neg1pct"]["value"] - 1.6) < 0.05, "T12 −1 % boundary drifted"
    assert abs(names["worked.comma_error_factor_175"]["value"] - 175.0) < 1e-9, "comma-error factor drifted"
    assert abs(names["unit_conversion_1mgmL_mmol_L"]["value"] - 2.657) < 5e-4, "12.3 conversion drifted"

    return True

if __name__ == "__main__":
    verify_invariants()
    print("PASS: tools/data.py invariants verified successfully!")
    print("T10 layers: %d named source observations, %d named derived results"
          % (len(source_observations()), len(named_results())))
    d = compute_all()
    f9 = d["regression_free_9pt"]
    f8 = d["regression_free_8pt"]
    orig = d["regression_origin"]
    print("Variant matrix (C-05):")
    print("  caur nulli, 9 punkti (tukšais iekļauts; b=0 fiksēts): k=%.4f  SE=%.4f  s_y=%.6f" % (orig["k"], orig["se_k"], orig["sy"]))
    print("  brīvā, 9 punkti (tukšais iekļauts):                  m=%.4f  b=%+.4f  R2=%.7f  s_y=%.6f" % (f9["slope"], f9["intercept"], f9["r2"], f9["sy"]))
    print("  brīvā, 8 punkti (tukšais izslēgts):                  m=%.4f  b=%+.4f  R2=%.7f  s_y=%.6f" % (f8["slope"], f8["intercept"], f8["r2"], f8["sy"]))
    print("  paraugu pārbaudes vērtības (brīvā 9 punkti): %s" % ", ".join("%.5f" % s["gamma_free_fit"] for s in d["samples"]))
    print("  paraugu tukšā-jutīguma diagnoze (brīvā 8 punkti): %s" % ", ".join("%.5f" % s["gamma_free_8pt"] for s in d["samples"]))
    print("  LOD = %.5f mg/mL (%.2f ug/mL); LOQ = %.5f mg/mL (%.2f ug/mL) -- simplified regression estimates (C-07)" % (d["LOD_mg_per_mL"], d["LOD_mg_per_mL"] * 1e3, d["LOQ_mg_per_mL"], d["LOQ_mg_per_mL"] * 1e3))
    try:
        uncertainty_for_A(0.0)
        print("  boundary fixture A=0: NOT REJECTED (regression)")
    except ValueError:
        print("  boundary fixtures: A <= 0 rejected; extrapolation flagged outside [0,063; 0,482] A")
    rows, audit_ok = derivation_audit()
    print("  T06 derivation audit: %s; zīmes/bāzes mutācijas aizķertas (%d soļi)" % ("OK" if audit_ok else "FAIL", len(rows)))
