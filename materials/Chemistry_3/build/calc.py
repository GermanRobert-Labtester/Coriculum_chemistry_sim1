# -*- coding: utf-8 -*-
"""Verified arithmetic for the Topic 3 master document.
Every number used in the HTML is produced here; print_report() is pasted into the QA report.
Run: python3 -I build/calc.py
"""
import math
from math import sqrt
import json

# IUPAC 2021 standard atomic weights (abridged)
A = dict(Na=22.990, K=39.098, Cl=35.45, S=32.06, O=15.999, H=1.008,
         C=12.011, N=14.007, P=30.974, Ca=40.078, Mg=24.305, Al=26.982,
         I=126.904, F=18.998, Br=79.904)
# Course-rounded values used by the answer keys (Na 23, K 39, Cl 35.5, S 32, O 16, H 1, C 12, N 14, P 31, Ca 40, Mg 24, Al 27)
C = dict(Na=23, K=39, Cl=35.5, S=32, O=16, H=1, C=12, N=14, P=31, Ca=40, Mg=24, Al=27,
         I=127, F=19, Br=80)


def M(formula, table=A):
    """Molar mass from a very small formula parser: element + integer count, parentheses not needed here."""
    import re
    total = 0.0
    for el, num in re.findall(r'([A-Z][a-z]?)(\d*)', formula):
        if not el:
            continue
        total += table[el] * (int(num) if num else 1)
    return total


MASS = {f: M(f) for f in [
    'Na2SO4', 'NaOH', 'KOH', 'Na2CO3', 'KI', 'NaF', 'NaCl', 'Na3PO4',
    'K2SO4', 'C6H12O6', 'KBr', 'HCl', 'H2SO4', 'NH3', 'CaCl2', 'KCl',
    'K2CO3', 'HCHO', 'HCOOH', 'CH3COOH', 'H2O2', 'C6H5Na3O7', 'Al(OH)3',
    'Mg(OH)2', 'C3H7NO2S', 'C12H22O11', 'H3PO4', 'HNO3', 'Na2SO4']}
MASS.update({'acetylcysteine': 179.2, 'sucrose': 342.3, 'citrate': 258.07})
MASS_C = {
    'Na2SO4': 142, 'NaOH': 40, 'KOH': 56, 'Na2CO3': 106, 'KI': 166, 'NaF': 42,
    'NaCl': 58.5, 'Na3PO4': 164, 'K2SO4': 174, 'C6H12O6': 180, 'KBr': 119,
    'HCl': 36.5, 'H2SO4': 98, 'CaCl2': 111, 'KCl': 74.5, 'K2CO3': 138,
    'H2O2': 34, 'H3PO4': 98, 'Al(OH)3': 78, 'Mg(OH)2': 58, 'citrate': 258,
}

NA = 6.02214076e23
K_NH3 = 1.79e-5

# Hypothetical final volumes illustrate sensitivity, not measured contraction.
DILUTION_EXAMPLE = {'n': 3.0 * 0.0150}
DILUTION_EXAMPLE.update({str(v): DILUTION_EXAMPLE['n'] / (v / 1000)
                         for v in (449, 450, 451)})


def ostwald(Cc):
    """exact alpha from K = C a^2/(1-a)"""
    return (-K_NH3 + sqrt(K_NH3**2 + 4*K_NH3*Cc)) / (2*Cc)


def ostwald_approx(Cc):
    return sqrt(K_NH3 / Cc)


def threshold_5pct():
    lo, hi = 1e-5, 1.0
    for _ in range(200):
        mid = (lo*hi)**0.5
        err = (ostwald_approx(mid) - ostwald(mid)) / ostwald(mid)
        if err > 0.05:
            lo = mid
        else:
            hi = mid
    return (lo*hi)**0.5


V = {}
# ---- Seminar C ----
V['C1.1'] = dict(c=2.0/2.0)
V['C1.2'] = dict(c=0.5/5.0)
V['C2.1'] = dict(n=1.00*2.50)
V['C2.2'] = dict(n=0.400*0.125)
V['C3.1'] = dict(c=2.80/MASS['KOH']/0.500, c_course=2.80/56/0.5)
V['C3.2'] = dict(c=53.0/MASS['Na2CO3']/2.50, c_course=53.0/106/2.5)
V['C4.1'] = dict(m=0.1*0.0500*MASS['NaOH'])
V['C4.2'] = dict(m=0.10*0.500*MASS['KI'])
n_a = 21.0/MASS['NaF']; n_b = 10.5/MASS['NaF']
V['C5'] = dict(ca=n_a/0.500, cb=n_b/0.100, ma=21.0, mb=10.5)
V['C6'] = dict(w=45/(700.0+45)*100, wrong=45/700*100)
V['C7'] = dict(w=5.0/(500.0*1.07)*100, wrong=5.0/500*100, alt=5.0/(500.0*1.005)*100)
V['C8'] = dict(w=0.560/10.4*100)
V['C9'] = dict(m=150.0)
V['C10'] = dict(gamma=18000/300.0)
V['C11'] = dict(V=40.5/9.0)
V['C12'] = dict(mg=450/10*70, V=(450/10*70)/150, wrong=(450/10*70)/150*10)
V['C13'] = dict(c=10*5.0*1.07/MASS['Na3PO4'], c_course=10*5*1.07/164)
V['C14'] = dict(w=0.50*MASS['K2SO4']/(10*1.02))
V['C15'] = dict(gamma=0.075*MASS['C6H12O6'])
V['C16'] = dict(V1=0.10*450.0/3.0, water=450.0-0.10*450.0/3.0,
               V1_mL=0.10*450.0/3.0, V2_mL=450.0, c1=3.0, c2=0.10, n_mmol=0.10*450.0)
m17 = 450*1.07; ms17 = m17*0.09; n17 = ms17/MASS['Na3PO4']
V['C17'] = dict(m=m17, ms=ms17, n=n17, V2=n17/0.10, water=n17/0.10-0.450, water_course=n17/0.10-0.450, wrong=n17/0.10)
V['C18'] = dict(c=(35.0*1.00+65.0*0.600)/100.0, wrong=(1.00+0.600)/2)
V['C19'] = dict(Na=0.70, Cl=0.70)
V['C20'] = dict(Na=3*0.50, PO4=0.50)
V['C21'] = dict(n=3.0)
V['C22'] = dict(n=3.0/2)
V['C23'] = dict(n=1.18, wrong1=2.35, wrong2=2.35+1.18)
V['C24'] = dict(n=0.0100*0.100)
V['C25'] = dict(V=10.0)
V['C26'] = dict(m=0.0100*0.100*MASS['NaOH'])
V['C27'] = dict(V=20.0*0.100*2/0.100, wrong=20.0)

# ---- Worksheet B ----
V['B1'] = dict(m=10.0, water=90.0)
V['B1*'] = dict(m=100.0, water=900.0)
V['B2'] = dict(m=100*1.11, solute=100*1.11*0.10, water=100*1.11*0.90)
V['B2*'] = dict(m=100*1.14, solute=100*1.14*0.17, water=100*1.14*0.83)
V['B3'] = dict(m=880*1.005, solute=880*1.005*0.0088, water=880*1.005*0.9912)
V['B4'] = dict(m1=200*1.18, solute=200*1.18*0.36, m2=200*1.18+1000, w=(200*1.18*0.36)/(200*1.18+1000)*100)
V['B4*'] = dict(m1=200*1.12, solute=200*1.12*0.16, m2=200*1.12+600, w=(200*1.12*0.16)/(200*1.12+600)*100)
V['B5'] = dict(m=1.0*MASS['Na2CO3']*0.1)
V['B5*'] = dict(m=0.1*0.200*MASS['CaCl2'])
V['B6'] = dict(c=7.78/(MASS['NaCl']*0.88), c_course=7.78/(58.5*0.88))
V['B6*'] = dict(c=7.78/(MASS['KCl']*0.080))
m_pure = 0.1*98.0*0.5
m_pure_i = 0.1*MASS['H2SO4']*0.5
m96 = m_pure_i/0.96
c96 = 1000*1.84*0.96/MASS['H2SO4']
V79 = m96/1.84
V7_key = (0.1*0.5/c96)*1000
V['B7'] = dict(m_pure=m_pure, m_pure_i=m_pure_i, m96=m96, m96_rounded=5.1,
               V=V79, V_rounded=5.1/1.84, c96=c96, V1=V7_key)
V['B8'] = dict(V2=0.200*1/0.05, water=0.200*1/0.05-0.200)
V['B9'] = dict(n=0.25*0.052, m=0.25*0.052*MASS['NaOH'])
V['B10'] = dict(nNaOH=0.2*0.05, n=0.2*0.05/2, m=0.2*0.05/2*98.0, wrong=0.2*0.05*2*98.0)
V['BSC1'] = dict(m=40*1.35*0.32)
V['BSC2'] = dict(c=(100*0.1+400*0.05)/500)
V['BSC3'] = dict(m=1000+3.5+2.5+2.9+10,
                 w=[3.5/(1000+3.5+2.5+2.9+10)*100, 2.5/(1000+3.5+2.5+2.9+10)*100,
                    2.9/(1000+3.5+2.5+2.9+10)*100, 10/(1000+3.5+2.5+2.9+10)*100],
                 wrong_sum=1000+3.5+2.9+10)
V['BSC4'] = dict(n=2.9/342.3, V_mL=(100+3)/1.01, c=(2.9/342.3)/(((100+3)/1.01)/1000))
V['BSC5'] = dict(m=3.99*15/100, nAl=3.99*15/100/78.00, nMg=3.99*15/100/58.32,
                 n=3.99*15/100/78.00+3.99*15/100/58.32)
V['BSC6'] = dict(m=20*1.18, solute=20*1.18*0.37, m2=20*1.18*0.37/0.083, V=20*1.18*0.37/0.083/1.04)
V['BSC7'] = dict(w=3.6*98/(10*1.18))
V['BSC8'] = dict(c=(248*0.25+752*0.52)/1000)
V['BSC9'] = dict(a=100*1.01*0.0085, a_key=0.85, b=0.85*0.1*MASS['NaCl'])
V['BSC10'] = dict(m1=50*1.112, solute=50*1.112*0.30, m2=50*1.112*0.30/0.06, V=50*1.112*0.30/0.06/1.020)

# Neutralisation / conversion values used by the T18 answer-record pilot.
V['BEx7II'] = dict(c=1000*1.84*0.96/MASS['H2SO4'])
V['BEx9'] = dict(m=0.25*0.052*MASS['NaOH'])
V['BEx10'] = dict(m=0.2*0.050/2*MASS['H2SO4'])

# ---- Supplementary D/E/F ----
V['P1'] = dict(c=10*3.0*1.02/MASS['K2SO4'], c_course=10*3*1.02/174)
V['P2'] = dict(m_solution=1000*1.03, m_solute=0.48*MASS['Na3PO4'],
               w=0.48*MASS['Na3PO4']/(10*1.03), w_course=0.48*164/(10*1.03))
V['P3'] = dict(V1=0.47*1/2.11, m=0.47*MASS['Na2CO3'], w=0.47*MASS['Na2CO3']/(1000*1.01)*100,
               V1_mL=0.47*1/2.11*1000, V2_mL=1000.0, c1=2.11, c2=0.47, n_mmol=0.47*1000)
V['P4'] = dict(m=500*1.04, solute=500*1.04*0.072, c1=500*1.04*0.072/MASS['K2CO3']/0.5,
               c1_course=500*1.04*0.072/138/0.5,
               V2=(500*1.04*0.072/MASS['K2CO3']/0.5)*0.5/0.1,
               V2_course=(500*1.04*0.072/138/0.5)*0.5/0.1)
V['P4']['water'] = V['P4']['V2'] - 0.5
V['P5'] = dict(m=720*1.03, solute=720*1.03*0.08, n=720*1.03*0.08/MASS['HCOOH'],
               c1=720*1.03*0.08/MASS['HCOOH']/0.720,
               c2=720*1.03*0.08/MASS['HCOOH']/1.720,
               n_hcho=720*1.03*0.08/MASS['HCHO'],
               c1_hcho=720*1.03*0.08/MASS['HCHO']/0.720,
               c2_hcho=720*1.03*0.08/MASS['HCHO']/1.720)
V['P6'] = dict(w=0.7*MASS['CaCl2']/(10*1.05), w_course=0.7*111/(10*1.05))
V['P7'] = dict(m=300*1.15, solute=300*1.15*0.18, n=300*1.15*0.18/MASS['H2SO4'],
               V2=(300*1.15*0.18/MASS['H2SO4'])/0.7, water=(300*1.15*0.18/MASS['H2SO4'])/0.7-0.300)
V['P8'] = dict(m=40*1.35*0.32)
V['P9'] = dict(c=(100.0*0.1+400.0*0.05)/500.0)
V['P10'] = dict(m=1000+3.5+2.5+2.9+10,
                w=[3.5/1018.9*100, 2.5/1018.9*100, 2.9/1018.9*100, 10/1018.9*100],
                wrong_sum=1000+3.5+2.9+10)
V['P11'] = dict(m30_10=30*100, mg_ml_20=200, m30_20=30*200,
                day_min=3*3*200, day_max=5*4*200)
V['P12'] = dict(w_ac=100/3000*100, w_su=2800/3000*100, w_asc=100/3000*100,
                c_ac=0.1/(179.2*0.2), c_su=2.8/(342.3*0.2),
                day=2*3*100, packets=2*3*4, total=2*3*4*100)
V['P13'] = dict(gamma_al=220/10, gamma_mg=380/10,
                n_al_ml=0.022/78.00, n_mg_ml=0.038/58.32, n_mg_ml_key=0.038/58,
                m_al=355*22/1000, m_mg=355*38/1000,
                n_al=355*0.022/78.00, n_mg=355*0.038/58.32, n_mg_key=355*0.000655,
                n_al_key=355*0.00028)

# ---- Ostwald ----
OST = []
for cc in [1.0, 0.1, 0.01, 0.001, 0.0001]:
    ex, ap = ostwald(cc), ostwald_approx(cc)
    OST.append(dict(c=cc, exact=ex, approx=ap, err=(ap-ex)/ex*100))
THRESH = threshold_5pct()

# ---- Weak-electrolyte speciation (static baseline for F03) ----
# Declared model: ideal aqueous NH3, activities replaced by concentrations,
# one acid-base equilibrium, water autoprotolysis neglected.  alpha is the
# fraction of analytical ammonia converted to NH4+; it is not a free slider.
SPECIATION_C0 = 0.100


def speciation_state(c0, alpha):
    """Ideal weak-base species for a declared total concentration and alpha."""
    if c0 <= 0:
        raise ValueError('c0 must be positive')
    if not 0.0 <= alpha <= 1.0:
        raise ValueError('alpha must lie in [0, 1]')
    nh4 = c0 * alpha
    nh3 = c0 * (1.0 - alpha)
    kb_implied = (nh4 * nh4 / nh3) if nh3 > 0 else None
    return dict(c0=c0, alpha=alpha, nh3=nh3, nh4=nh4, oh=nh4,
                mass_balance=nh3 + nh4 - c0, charge_balance=nh4 - nh4,
                kb_implied=kb_implied)


SPECIATION = speciation_state(SPECIATION_C0, ostwald(SPECIATION_C0))
SPECIATION['alpha_pct'] = SPECIATION['alpha'] * 100


def speciation_errors():
    """Boundary and mass/charge checks for the declared speciation model."""
    errors = []
    for alpha in (0.0, SPECIATION['alpha'], 1.0):
        state = speciation_state(SPECIATION_C0, alpha)
        if abs(state['mass_balance']) > 1e-12:
            errors.append(f'speciation alpha={alpha}: mass balance residual {state["mass_balance"]:.3e}')
        if abs(state['charge_balance']) > 1e-12:
            errors.append(f'speciation alpha={alpha}: charge balance residual {state["charge_balance"]:.3e}')
    exact = speciation_state(SPECIATION_C0, SPECIATION['alpha'])
    if exact['kb_implied'] is None or abs(exact['kb_implied'] - K_NH3) / K_NH3 > 1e-9:
        errors.append(f'speciation exact alpha does not reproduce Kb: {exact["kb_implied"]!r}')
    for bad in (-0.01, 1.01):
        try:
            speciation_state(SPECIATION_C0, bad)
        except ValueError:
            continue
        errors.append(f'speciation accepted out-of-model alpha={bad}')
    return errors


# ---- Medical table ----
MED = dict(
    nacl_gL=9.0, nacl_mmol=9.0/MASS['NaCl']*1000,
    glu_gL=50.0, glu_mmol=50.0/MASS['C6H12O6']*1000,
    h2o2_gL=30.0, h2o2_mol=30.0/MASS['H2O2'],
    glu55_mgdl=5.5*MASS['C6H12O6']/10,
    ca_mmol=2.40, ca_meq=4.80, ca_mgdl=2.40*40.078/10,
    reh_nacl=3.5/58.44*1000, reh_kcl=2.5/74.551*1000,
    reh_cit=2.9/258.07*1000, reh_glu=10/180.156*1000,
    reh_na=3.5/58.44*1000 + 3*(2.9/258.07*1000),
    reh_k=2.5/74.551*1000,
    reh_cl=3.5/58.44*1000 + 2.5/74.551*1000)

# Percentage-kind examples: m/V values per litre and the conditional m/m
# mass concentration at rho = 1 g/mL. These are teaching assumptions, not labels.
PERCENT_CASES = {
    'NaCl': dict(percent=0.9, m_v_gL=0.9*10, m_m_gL_rho1=0.9*10,
                 mmol_L=0.9*10/MASS['NaCl']*1000,
                 ion_mmol_L=2*0.9*10/MASS['NaCl']*1000),
    'glucose': dict(percent=5, m_v_gL=5*10, m_m_gL_rho1=5*10,
                    mmol_L=5*10/MASS['C6H12O6']*1000),
    'H2O2': dict(percent=3, m_v_gL=3*10, m_m_gL_rho1=3*10,
                 mol_L=3*10/MASS['H2O2']),
    'iodine': dict(percent=5, m_v_gL=5*10, m_m_gL_rho1=5*10),
    'ethanol': dict(percent=70, v_v_mL_L=70*10),
}

SUP = str.maketrans('0123456789-', '⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def fmt_sig(val, sig, exp=False):
    """Format number with explicit significant figures and decimal comma."""
    if sig < 1:
        raise ValueError('sig must be >= 1')
    if val == 0 or val == 0.0:
        if exp:
            return '0'
        return '0,' + '0' * (sig - 1) if sig > 1 else '0'
    neg = val < 0
    val = abs(val)
    exp_val = int(math.floor(math.log10(val)))
    if exp:
        mantissa = val / (10 ** exp_val)
        m_scaled = round(mantissa, sig - 1)
        if m_scaled >= 10.0:
            mantissa /= 10.0
            exp_val += 1
            m_scaled = round(mantissa, sig - 1)
        m_str = f'{m_scaled:.{sig-1}f}'.replace('.', ',')
        exp_str = str(exp_val).translate(SUP)
        res = f'{m_str}·10{exp_str}'
        return ('-' if neg else '') + res
    else:
        decimals = max(0, sig - 1 - exp_val)
        rounded = round(val, decimals)
        if rounded > 0:
            new_exp = int(math.floor(math.log10(rounded)))
            if new_exp != exp_val:
                decimals = max(0, sig - 1 - new_exp)
                rounded = round(val, decimals)
        if decimals == 0:
            res = f'{int(round(rounded))}'
        else:
            res = f'{rounded:.{decimals}f}'.replace('.', ',')
        return ('-' if neg else '') + res


def test_sig_vectors():
    """Verify precision contract against exact values, trailing zeros, exp, and rounding."""
    cases = [
        (0.1, 2, False, '0,10'),
        (0.1, 3, False, '0,100'),
        (1.0, 3, False, '1,00'),
        (150.0, 3, False, '150'),
        (150.0, 4, False, '150,0'),
        (0.0010, 2, False, '0,0010'),
        (13.49, 3, False, '13,5'),
        (2.776, 3, False, '2,78'),
        (0.8585, 3, False, '0,859'),
        (0.8585, 2, False, '0,86'),
        (0.0019, 2, True, '1,9·10⁻³'),
        (1.79e-5, 3, True, '1,79·10⁻⁵'),
        (6.022e23, 4, True, '6,022·10²³'),
    ]
    results = []
    for val, sig, exp, expected in cases:
        actual = fmt_sig(val, sig, exp=exp)
        results.append({
            'label': f'{val} (sig={sig}, exp={exp})',
            'val': val, 'sig': sig, 'exp': exp,
            'expected': expected, 'actual': actual,
            'passed': actual == expected,
        })
    return results


def fmt(x, nd):
    s = f'{x:.{nd}f}'.replace('.', ',')
    return s


def report():
    lines = []
    def add(k, txt): lines.append(f'{k:10} {txt}')
    add('M(NaCl)', fmt(MASS['NaCl'], 3)); add('M(Na3PO4)', fmt(MASS['Na3PO4'], 3))
    add('C1.1', fmt(V['C1.1']['c'], 2)); add('C1.2', fmt(V['C1.2']['c'], 2))
    add('C2.1', fmt(V['C2.1']['n'], 2)); add('C2.2', fmt(V['C2.2']['n'], 3))
    add('C3.1', fmt(V['C3.1']['c'], 4)); add('C3.2', fmt(V['C3.2']['c'], 4))
    add('C4.1', fmt(V['C4.1']['m'], 4)); add('C4.2', fmt(V['C4.2']['m'], 4))
    add('C5', f"a={fmt(V['C5']['ca'],3)} b={fmt(V['C5']['cb'],3)}")
    add('C6', f"w={fmt(V['C6']['w'],4)} wrong={fmt(V['C6']['wrong'],3)}")
    add('C7', f"w={fmt(V['C7']['w'],4)} wrong={fmt(V['C7']['wrong'],2)} alt={fmt(V['C7']['alt'],3)}")
    add('C8', fmt(V['C8']['w'], 4)); add('C9', fmt(V['C9']['m'], 1))
    add('C10', fmt(V['C10']['gamma'], 1)); add('C11', fmt(V['C11']['V'], 1))
    add('C12', f"mg={fmt(V['C12']['mg'],0)} V={fmt(V['C12']['V'],1)} wrong={fmt(V['C12']['wrong'],0)}")
    add('C13', f"c={fmt(V['C13']['c'],4)} course={fmt(V['C13']['c_course'],4)}")
    add('C14', f"w={fmt(V['C14']['w'],3)}"); add('C15', f"g={fmt(V['C15']['gamma'],3)}")
    add('C16', f"V1={fmt(V['C16']['V1'],2)} water={fmt(V['C16']['water'],0)}")
    add('C17', f"n={fmt(V['C17']['n'],4)} V2={fmt(V['C17']['V2'],4)} water={fmt(V['C17']['water'],3)}")
    add('C18', f"c={fmt(V['C18']['c'],3)} wrong={fmt(V['C18']['wrong'],3)}")
    add('C20', f"{fmt(V['C20']['Na'],1)} / {fmt(V['C20']['PO4'],2)}")
    add('C23', f"{fmt(V['C23']['n'],2)} wrong {fmt(V['C23']['wrong1'],2)} / {fmt(V['C23']['wrong2'],2)}")
    add('C24', fmt(V['C24']['n'], 4)); add('C26', fmt(V['C26']['m'], 4)); add('C27', fmt(V['C27']['V'], 1))
    add('B1*', f"{fmt(V['B1*']['m'],1)} + {fmt(V['B1*']['water'],1)}")
    add('B2*', f"{fmt(V['B2*']['m'],2)} m={fmt(V['B2*']['solute'],3)} water={fmt(V['B2*']['water'],2)}")
    add('B3', f"m={fmt(V['B3']['m'],2)} solute={fmt(V['B3']['solute'],4)} water={fmt(V['B3']['water'],2)}")
    add('B4*', f"w={fmt(V['B4*']['w'],4)}")
    add('B5*', f"m={fmt(V['B5*']['m'],4)}")
    add('B6*', f"c={fmt(V['B6*']['c'],4)}")
    add('B7', f"m96={fmt(V['B7']['m96'],4)} V={fmt(V['B7']['V'],4)} Vrounded={fmt(V['B7']['V_rounded'],4)} c96={fmt(V['B7']['c96'],3)} V1={fmt(V['B7']['V1'],4)}")
    add('B8', f"V2={fmt(V['B8']['V2'],2)} water={fmt(V['B8']['water'],2)}")
    add('BSC3', f"{fmt(V['BSC3']['m'],1)} " + ' / '.join(fmt(x,2) for x in V['BSC3']['w']) + f" wrongsum={fmt(V['BSC3']['wrong_sum'],1)}")
    add('BSC4', f"n={fmt(V['BSC4']['n'],6)} V={fmt(V['BSC4']['V_mL'],2)} c={fmt(V['BSC4']['c'],5)}")
    add('BSC5', f"n={fmt(V['BSC5']['n'],5)}")
    add('BSC6', f"V={fmt(V['BSC6']['V'],3)}")
    add('BSC9', f"a={fmt(V['BSC9']['a'],4)} b={fmt(V['BSC9']['b'],3)}")
    add('BSC10', f"V={fmt(V['BSC10']['V'],3)}")
    add('P1', f"{fmt(V['P1']['c'],4)} course={fmt(V['P1']['c_course'],4)}")
    add('P2', f"m_solution={fmt(V['P2']['m_solution'],0)} m_solute={fmt(V['P2']['m_solute'],4)} w={fmt(V['P2']['w'],7)} course={fmt(V['P2']['w_course'],7)}")
    add('P3', f"V1={fmt(V['P3']['V1'],5)} w={fmt(V['P3']['w'],3)}")
    add('P4', f"c1={fmt(V['P4']['c1'],4)} c1c={fmt(V['P4']['c1_course'],4)} V2={fmt(V['P4']['V2'],4)} water={fmt(V['P4']['water'],4)}")
    add('P5', f"c1={fmt(V['P5']['c1'],4)} c2={fmt(V['P5']['c2'],4)} HCHO={fmt(V['P5']['c2_hcho'],4)}")
    add('P6', f"{fmt(V['P6']['w'],3)}")
    add('P7', f"n={fmt(V['P7']['n'],4)} V2={fmt(V['P7']['V2'],4)} water={fmt(V['P7']['water'],4)}")
    add('P10', ' / '.join(fmt(x, 2) for x in V['P10']['w']))
    add('P11', f"day {fmt(V['P11']['day_min'],0)}–{fmt(V['P11']['day_max'],0)} mg")
    add('P12', f"w {fmt(V['P12']['w_ac'],3)} / {fmt(V['P12']['w_su'],3)} c {fmt(V['P12']['c_ac'],5)} / {fmt(V['P12']['c_su'],5)}")
    add('P13', f"m {fmt(V['P13']['m_al'],3)} / {fmt(V['P13']['m_mg'],3)} n {fmt(V['P13']['n_al'],4)} / {fmt(V['P13']['n_mg'],4)} keyn {fmt(V['P13']['n_al_key'],4)}")
    for o in OST:
        add('Ostwald', f"c={o['c']:g} exact={o['exact']:.4f} approx={o['approx']:.4f} err={o['err']:.1f}%")
    add('threshold', f"{THRESH:.6g}")
    add('speciation', f"c0={SPECIATION['c0']:.4f} alpha={SPECIATION['alpha']:.6f} "
                      f"NH3={SPECIATION['nh3']:.6f} NH4={SPECIATION['nh4']:.7f} "
                      f"OH={SPECIATION['oh']:.7f} mass={SPECIATION['mass_balance']:.2e} "
                      f"charge={SPECIATION['charge_balance']:.2e} "
                      f"Kb={SPECIATION['kb_implied']:.3e}")
    add('MED', f"NaCl {MED['nacl_mmol']:.1f} mmol/L; glucose {MED['glu_mmol']:.1f}; H2O2 {MED['h2o2_mol']:.4f}; glu5.5 {MED['glu55_mgdl']:.1f} mg/dL; Ca {MED['ca_mgdl']:.2f} mg/dL")
    add('Rehydron', f"Na {MED['reh_na']:.1f} K {MED['reh_k']:.1f} Cl {MED['reh_cl']:.1f} citrate {MED['reh_cit']:.1f} glu {MED['reh_glu']:.1f}")
    return '\n'.join(lines)


if __name__ == '__main__':
    print(report())
