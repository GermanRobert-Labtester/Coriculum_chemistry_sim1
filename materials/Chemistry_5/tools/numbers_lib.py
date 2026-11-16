"""numbers_lib.py — shared helpers for build_numbers.py and verify_numbers.py (T09).

* a restricted formula evaluator (no builtins; only the names below),
* the display policy: Latvian decimal comma, NBSP thousands from 5 integer digits, U+2212 minus,
  scientific notation with Unicode superscripts,
* parse_display(): turn a display string back into a float so that verify can tell whether the
  display drops digits (approximate, needs "≈") or reproduces the value exactly.
"""
import math, re
from decimal import Decimal

NBSP = " "
MINUS = "−"
SUP = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")
SUP_INV = {v: k for k, v in zip("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")}


# ---------- formula namespace -------------------------------------------------
def _mean(x): return sum(x) / len(x)


def slope(x, y):
    mx, my = _mean(x), _mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)


def intercept(x, y): return _mean(y) - slope(x, y) * _mean(x)


def r2(x, y):
    mx, my = _mean(x), _mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy ** 2 / (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def tail(x):
    """fraction of a 3-D Maxwell–Boltzmann energy distribution with E >= Ea, x = Ea/(RT)"""
    return math.erfc(math.sqrt(x)) + 2 * math.sqrt(x / math.pi) * math.exp(-x)


def atoms(side, element):
    """count atoms of `element` on one side of an equation; side = [(coeff, 'KMnO4'), ...]"""
    total = 0
    for coeff, formula in side:
        # parentheses are not needed for the species used here
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula):
            if el == element:
                total += coeff * (int(n) if n else 1)
    return total


NAMESPACE = {
    "log": math.log, "exp": math.exp, "sqrt": math.sqrt, "erfc": math.erfc, "pi": math.pi,
    "sum": sum, "abs": abs, "min": min, "max": max, "len": len, "range": range, "zip": zip,
    "slope": slope, "intercept": intercept, "r2": r2, "tail": tail, "atoms": atoms, "mean": _mean,
}


def evaluate(formula, inputs, consts):
    env = dict(NAMESPACE)
    env.update(consts)
    env.update(inputs)
    return eval(formula, {"__builtins__": {}}, env)  # noqa: S307 — restricted namespace, repo-local JSON


# ---------- display policy ----------------------------------------------------
def _group(intpart):
    if len(intpart) < 5:
        return intpart
    out = []
    while intpart:
        out.append(intpart[-3:]); intpart = intpart[:-3]
    return NBSP.join(reversed(out))


def fmt(value, rounding):
    """rounding: {"dec": n} | {"sci": n_sig, "sep": "·" or " × "}"""
    if "dec" in rounding:
        s = f"{abs(value):.{rounding['dec']}f}"
        ip, _, fp = s.partition(".")
        out = _group(ip) + ("," + fp if fp else "")
        neg = value < 0 and float(s) != 0
        return (MINUS if neg else "") + out
    if "sci" in rounding:
        n = rounding["sci"]
        exp = int(math.floor(math.log10(abs(value))))
        mant = value / 10 ** exp
        m = f"{abs(mant):.{n - 1}f}"
        if float(m) >= 10:  # 9.996 -> 10.0
            exp += 1; m = f"{abs(value) / 10 ** exp:.{n - 1}f}"
        sep = rounding.get("sep", "·")
        e = str(exp).translate(SUP).replace("-", "⁻")
        return (MINUS if value < 0 else "") + m.replace(".", ",") + sep + "10" + e
    raise ValueError(rounding)


def norm_display(text):
    """normalise display text found in HTML: <sup>x</sup> -> unicode superscripts, entities, spaces"""
    text = re.sub(r"<sup>([^<]*)</sup>", lambda m: m.group(1).replace("−", "-").translate(SUP), text)
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&nbsp;", NBSP).replace("&minus;", MINUS).replace("-", MINUS)  # ASCII hyphen -> minus
    text = text.replace("⁻", "⁻")
    return text.strip()


def parse_display(display):
    """display -> float (inverse of fmt, for the exactness test)"""
    d = norm_display(display).replace(NBSP, "").replace(" ", "")
    neg = d.startswith(MINUS)
    d = d.lstrip(MINUS)
    m = re.fullmatch(r"([\d,]+)(?:[·×]10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+))?", d)
    if not m:
        raise ValueError(display)
    mant = float(m.group(1).replace(",", "."))
    if m.group(2):
        mant *= 10 ** int("".join(SUP_INV[c] for c in m.group(2)).replace(MINUS, "-"))
    return -mant if neg else mant


def is_exact(value, display):
    """True if the display reproduces the value (no digits dropped)"""
    p = parse_display(display)
    # exactness within a relative 1e-12 (float noise); a displayed 0,500 for 0.5 is exact, 0,417 for 5/12 is not
    return abs(p - value) <= 1e-12 * max(1.0, abs(value))
