#!/usr/bin/env python3
"""Atom + charge balance checker for redox equations (ionic or molecular).

Usage
  python3 -I tools/check_balance.py "2MnO4^- + 16H^+ + 10I^- -> 2Mn^2+ + 8H2O + 5I2"
  python3 -I tools/check_balance.py --corpus          # re-check every equation found in the sources
  python3 -I tools/check_balance.py --data            # every equation registered in master_data
  python3 -I tools/check_balance.py --file eqs.txt     # one equation per line, '#' comments allowed

Input syntax (ASCII, so it can live in a text file)
  species separated by " + " (space-plus-space)        e.g.  Fe^2+ + MnO4^- -> ...
  charge after ^ : ^+  ^-  ^2+  ^2-  ^3+                e.g.  SO4^2-   Fe^3+   e^-
  leading integer = coefficient                         e.g.  5Fe^2+
  parentheses and hydrate dot are allowed               e.g.  (NH4)2Fe(SO4)2.6H2O
  arrow: "->" or "=" ; a half-reaction may use "e^-" as a species.
  Gas/precipitate marks (↑ ↓) and phase labels (aq)(s)(l)(g) are ignored.

Exit status: 0 if every checked equation balances, 1 otherwise.
This verifies bookkeeping only; it cannot tell you whether the chemistry is sensible
(e.g. that SO3^2- exists in strong acid) -- see SOURCE_AUDIT.md.
"""
import re
import sys
from collections import Counter

TOKEN = re.compile(r"([A-Z][a-z]?|\(|\)|\d+|\.)")


def parse_formula(f):
    """Return (Counter of atoms, charge). Handles (), hydrate dot, ^charge."""
    charge = 0
    if "^" in f:
        f, ch = f.split("^", 1)
        m = re.fullmatch(r"(\d*)([+-])", ch)
        if not m:
            raise ValueError(f"bad charge '{ch}'")
        charge = int(m.group(1) or 1) * (1 if m.group(2) == "+" else -1)
    if f == "e":
        return Counter(), charge  # electron
    # split hydrates:  X.6H2O
    total = Counter()
    for part in f.split("."):
        mult = 1
        mm = re.match(r"^(\d+)(.*)$", part)
        if mm and "." in f:
            mult, part = int(mm.group(1)), mm.group(2)
        stack = [Counter()]
        toks = TOKEN.findall(part)
        i = 0
        while i < len(toks):
            t = toks[i]
            if t == "(":
                stack.append(Counter())
            elif t == ")":
                grp = stack.pop()
                n = 1
                if i + 1 < len(toks) and toks[i + 1].isdigit():
                    n = int(toks[i + 1]); i += 1
                for k, v in grp.items():
                    stack[-1][k] += v * n
            elif t[0].isupper():
                n = 1
                if i + 1 < len(toks) and toks[i + 1].isdigit():
                    n = int(toks[i + 1]); i += 1
                stack[-1][t] += n
            else:
                raise ValueError(f"unexpected token '{t}' in '{part}'")
            i += 1
        for k, v in stack[0].items():
            total[k] += v * mult
    return total, charge


def side(text):
    atoms, charge = Counter(), 0
    for sp in re.split(r"\s\+\s", text.strip()):
        sp = re.sub(r"\((?:aq|s|l|g)\)", "", sp).replace("↑", "").replace("↓", "").strip()
        if not sp:
            continue
        m = re.match(r"^(\d+)\s*(.*)$", sp)
        coef, f = (int(m.group(1)), m.group(2)) if m else (1, sp)
        a, c = parse_formula(f)
        for k, v in a.items():
            atoms[k] += coef * v
        charge += coef * c
    return atoms, charge


def check(eq):
    lhs, rhs = re.split(r"\s*(?:->|=)\s*", eq.strip(), maxsplit=1)
    la, lc = side(lhs)
    ra, rc = side(rhs)
    diffs = {k: (la.get(k, 0), ra.get(k, 0)) for k in set(la) | set(ra) if la.get(k, 0) != ra.get(k, 0)}
    return (not diffs and lc == rc), diffs, (lc, rc)


# --- Every equation in the five source files, transcribed in ASCII. ----------------
# EXPECT=True  -> must balance.  EXPECT=False -> known defect (see SOURCE_AUDIT.md id).
CORPUS = [
    # Lecture docx (2022)
    ("lec P010", "2SO2 + O2 -> 2SO3", True),
    ("lec P011 S", "S^4+ -> S^6+ + 2e^-", True),
    ("lec P011 O", "O2 + 4e^- -> 2O^2-", True),
    ("lec P077 O2/H3O+", "O2 + 4H3O^+ + 4e^- -> 6H2O", True),
    ("lec table1 / P231 O2 (2 e-)  [A4]", "O2 + 2e^- + 2H3O^+ -> H2O + 2H2O", False),
    ("lec table1 NAD+", "NAD^+ + H3O^+ + 2e^- -> NADH + H2O", True),
    ("lec table1 FAD", "FAD + 2H3O^+ + 2e^- -> FADH2 + 2H2O", True),
    ("lec P057 Fe/I", "2Fe^3+ + 2I^- -> 2Fe^2+ + I2", True),
    ("lec P089 MnO4 acid", "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O", True),
    ("lec P096 MnO4 neutral", "MnO4^- + 2H2O + 3e^- -> MnO2 + 4OH^-", True),
    ("lec P098 MnO4 basic", "MnO4^- + e^- -> MnO4^2-", True),
    ("lec P101 Cr2O7", "Cr2O7^2- + 6e^- + 14H^+ -> 2Cr^3+ + 7H2O", True),
    ("lec P106 H2", "2H^+ + 2e^- -> H2", True),
    ("lec P109 NO2", "NO3^- + e^- + 2H^+ -> NO2 + H2O", True),
    ("lec P110 NO", "NO3^- + 3e^- + 4H^+ -> NO + 2H2O", True),
    ("lec SO3 half", "SO3^2- + H2O -> SO4^2- + 2H^+ + 2e^-", True),
    ("lec S2O3 half", "2S2O3^2- -> S4O6^2- + 2e^-", True),
    ("lec H2O2 ox acid", "H2O2 + 2e^- + 2H^+ -> 2H2O", True),
    ("lec H2O2 ox neutral/basic", "H2O2 + 2e^- -> 2OH^-", True),
    ("lec H2O2 red acid", "H2O2 -> 2H^+ + O2 + 2e^-", True),
    ("lec H2O2 red basic", "H2O2 + 2OH^- -> 2H2O + O2 + 2e^-", True),
    ("lec NO2- ox acid", "NO2^- + e^- + 2H^+ -> H2O + NO", True),
    ("lec NO2- ox basic", "NO2^- + e^- + H2O -> 2OH^- + NO", True),
    ("lec NO2- red acid", "NO2^- + H2O -> 2H^+ + NO3^- + 2e^-", True),
    ("lec NO2- red basic", "NO2^- + 2OH^- -> H2O + NO3^- + 2e^-", True),
    ("lec self-test 2a molecular (H3PO3)", "2KMnO4 + 5H3PO3 + 3H2SO4 -> 2MnSO4 + 5H3PO4 + K2SO4 + 3H2O", True),
    ("lec self-test 2b molecular", "10HNO3 + 4Zn -> 4Zn(NO3)2 + N2O + 5H2O", True),
    ("lec self-test 2b ionic", "2NO3^- + 10H^+ + 4Zn -> N2O + 5H2O + 4Zn^2+", True),
    ("lec 3.1 ionic", "MnO4^- + 8H^+ + 5Fe^2+ -> Mn^2+ + 4H2O + 5Fe^3+", True),
    ("lec 3.1 molecular", "10(NH4)2Fe(SO4)2 + 2KMnO4 + 8H2SO4 -> 10(NH4)2SO4 + K2SO4 + 8H2O + 5Fe2(SO4)3 + 2MnSO4", True),
    # Lab 2020 (worked solutions)
    ("2020 acid molecular", "2KMnO4 + 3H2SO4 + 5Na2SO3 -> 3H2O + 5Na2SO4 + K2SO4 + 2MnSO4", True),
    ("2020 acid ionic (final)", "2MnO4^- + 6H^+ + 5SO3^2- -> 2Mn^2+ + 3H2O + 5SO4^2-", True),
    ("2020 basic molecular", "2KMnO4 + 2NaOH + Na2SO3 -> H2O + 2Na2MnO4 + K2SO4", True),
    ("2020 basic ionic", "2MnO4^- + SO3^2- + 2OH^- -> 2MnO4^2- + SO4^2- + H2O", True),
    ("2020 neutral molecular [B2: 'KOH-' typo]", "2KMnO4 + 3Na2SO3 + H2O -> 2MnO2 + 2KOH + 3Na2SO4", True),
    ("2020 neutral ionic (final)", "2MnO4^- + H2O + 3SO3^2- -> 2MnO2 + 2OH^- + 3SO4^2-", True),
    ("2020 Fe2+ molecular", "10FeSO4 + 2KMnO4 + 8H2SO4 -> K2SO4 + 8H2O + 5Fe2(SO4)3 + 2MnSO4", True),
    ("2020 KI molecular", "2KMnO4 + 8H2SO4 + 10KI -> 2MnSO4 + 6K2SO4 + 8H2O + 5I2", True),
    ("2020 KI ionic", "2MnO4^- + 16H^+ + 10I^- -> 2Mn^2+ + 8H2O + 5I2", True),
    ("2020 NaNO2 molecular", "2KMnO4 + 3H2SO4 + 5NaNO2 -> 2MnSO4 + 3H2O + K2SO4 + 5NaNO3", True),
    ("2020 NaNO2 ionic", "2MnO4^- + 6H^+ + 5NO2^- -> 2Mn^2+ + 3H2O + 5NO3^-", True),
    ("2020 H2O2 molecular", "2KMnO4 + 3H2SO4 + 5H2O2 -> 2MnSO4 + 5O2 + 8H2O + K2SO4", True),
    ("2020 H2O2 ionic", "2MnO4^- + 6H^+ + 5H2O2 -> 2Mn^2+ + 8H2O + 5O2", True),
    ("2020 H2S molecular", "2KMnO4 + 5H2S + 3H2SO4 -> 2MnSO4 + 8H2O + 5S + K2SO4", True),
    ("2020 H2S ionic", "2MnO4^- + 6H^+ + 5H2S -> 2Mn^2+ + 8H2O + 5S", True),
    ("2020 H2C2O4 molecular", "2KMnO4 + 5H2C2O4 + 3H2SO4 -> 2MnSO4 + 8H2O + 10CO2 + K2SO4", True),
    ("2020 H2C2O4 ionic", "2MnO4^- + 6H^+ + 5H2C2O4 -> 2Mn^2+ + 8H2O + 10CO2", True),
    ("2020 Cr/Fe molecular", "K2Cr2O7 + 6FeSO4 + 7H2SO4 -> Cr2(SO4)3 + 3Fe2(SO4)3 + 7H2O + K2SO4", True),
    ("2020 Cr/Fe ionic", "Cr2O7^2- + 14H^+ + 6Fe^2+ -> 2Cr^3+ + 7H2O + 6Fe^3+", True),
    ("2020 Cr/NO2 molecular", "K2Cr2O7 + 3KNO2 + 4H2SO4 -> Cr2(SO4)3 + K2SO4 + 3KNO3 + 4H2O", True),
    ("2020 Cr/NO2 ionic", "Cr2O7^2- + 8H^+ + 3NO2^- -> 2Cr^3+ + 4H2O + 3NO3^-", True),
    ("2020 Cr/I molecular", "K2Cr2O7 + 6KI + 7H2SO4 -> 7H2O + Cr2(SO4)3 + 4K2SO4 + 3I2", True),
    ("2020 Cr/I ionic", "Cr2O7^2- + 14H^+ + 6I^- -> 2Cr^3+ + 7H2O + 3I2", True),
    ("2020 KOH/SO3 molecular", "2KMnO4 + 2KOH + Na2SO3 -> H2O + 2K2MnO4 + Na2SO4", True),
    ("2020 Cr/SO3 molecular", "K2Cr2O7 + 4H2SO4 + 3Na2SO3 -> 4H2O + Cr2(SO4)3 + K2SO4 + 3Na2SO4", True),
    ("2020 Cr/SO3 ionic", "Cr2O7^2- + 8H^+ + 3SO3^2- -> 2Cr^3+ + 4H2O + 3SO4^2-", True),
    # Balances on paper, but PO3^3- is not the species present (H3PO3 is a molecule) -> see A14.
    ("2020 H3PO3 ionic as written (PO3^3-) [A14: balances, wrong species]", "2MnO4^- + 6H^+ + 5PO3^3- -> 2Mn^2+ + 3H2O + 5PO4^3-", True),
    # Lab 2021 / 2025
    ("2025 titration molecular", "10FeSO4 + 2KMnO4 + 8H2SO4 -> 5Fe2(SO4)3 + 2MnSO4 + K2SO4 + 8H2O", True),
    ("2025 titration ionic", "5Fe^2+ + MnO4^- + 8H^+ -> 5Fe^3+ + Mn^2+ + 4H2O", True),
    # Corrected / supplementary (these are what the master should print)
    ("[corr] H3PO3 ionic", "2MnO4^- + 6H^+ + 5H3PO3 -> 2Mn^2+ + 3H2O + 5H3PO4", True),
    ("[corr] H3PO3 half", "H3PO3 + H2O -> H3PO4 + 2H^+ + 2e^-", True),
    ("[corr] O2 4e- (as P077)", "O2 + 4e^- + 4H^+ -> 2H2O", True),
    ("[supp] MnO2 + conc. HCl", "MnO2 + 4H^+ + 2Cl^- -> Mn^2+ + Cl2 + 2H2O", True),
    ("[supp] manganate disproportionation", "3MnO4^2- + 4H^+ -> 2MnO4^- + MnO2 + 2H2O", True),
    ("[supp] oxalate standardisation (ionic)", "2MnO4^- + 6H^+ + 5H2C2O4 -> 2Mn^2+ + 8H2O + 10CO2", True),
    ("[supp] iodometry I2 + thiosulfate", "I2 + 2S2O3^2- -> 2I^- + S4O6^2-", True),
    ("[supp] Cr2O7 + Cl-  (conc. acid)", "Cr2O7^2- + 14H^+ + 6Cl^- -> 2Cr^3+ + 7H2O + 3Cl2", True),
    ("[supp] SO2 + 2 H2S comproportionation", "SO2 + 2H2S -> 3S + 2H2O", True),
    ("[supp] Mohr salt hexahydrate", "(NH4)2Fe(SO4)2.6H2O -> 2NH4^+ + Fe^2+ + 2SO4^2- + 6H2O", True),
]


def run_data():
    """Check every equation registered in master_data.EQUATIONS (Task 10 gate)."""
    import sys as _sys
    from pathlib import Path as _Path
    _here = str(_Path(__file__).resolve().parent)
    if _here not in _sys.path:
        _sys.path.insert(0, _here)
    import master_data as D
    bad = 0
    for name, eq in D.EQUATIONS:
        ok, diffs, ch = check(eq)
        if not ok:
            bad += 1
            print(f"FAIL {name}: {eq}\n     atoms(L,R)={diffs}  charge(L,R)={ch}")
    print(f"\n{len(D.EQUATIONS)} registered equations checked; failures: {bad}")
    return 1 if bad else 0


def run_corpus():
    bad_unexpected = 0
    for name, eq, expect in CORPUS:
        ok, diffs, ch = check(eq)
        status = "ok " if ok else "BAD"
        flag = ""
        if ok != expect:
            flag = "  <-- UNEXPECTED"
            bad_unexpected += 1
        elif not ok:
            flag = "  (known defect, expected)"
        detail = "" if ok else f"   atoms(L,R)={diffs} charge(L,R)={ch}"
        print(f"{status} {name}{flag}{detail}")
    print(f"\n{len(CORPUS)} equations checked; unexpected results: {bad_unexpected}")
    return 1 if bad_unexpected else 0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    if argv[1] == "--corpus":
        return run_corpus()
    if argv[1] == "--data":
        return run_data()
    eqs = []
    if argv[1] == "--file":
        eqs = [l.strip() for l in open(argv[2], encoding="utf8") if l.strip() and not l.lstrip().startswith("#")]
    else:
        eqs = argv[1:]
    worst = 0
    for eq in eqs:
        ok, diffs, ch = check(eq)
        print(("OK  " if ok else "FAIL") + "  " + eq + ("" if ok else f"\n      atoms(L,R)={diffs}  charge(L,R)={ch}"))
        worst |= 0 if ok else 1
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv))
