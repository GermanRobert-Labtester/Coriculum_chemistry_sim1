# -*- coding: utf-8 -*-
"""Audit displayed numeric equalities in task working.

This is deliberately conservative: it checks only expressions made of
numbers, parentheses and the four arithmetic operators.  An expression
that contains a unit, a variable or a relation is skipped, because a
string-presence test cannot prove it.  The goal is to catch transcription
errors such as ``78,69/1020 = 7,640`` before they reach the reader.

Run: python3 -I build/equations.py
"""
from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

NUM = r"-?\d+(?:\.\d+)?"
ALLOWED = set("0123456789.+-*/() ")


@dataclass
class Finding:
    source: str
    expression: str
    printed: str
    computed: str
    delta: str
    status: str


def _plain(s: str) -> str:
    s = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    return s.replace("−", "-").replace("×", "*").replace("·", "*")


def _decimal_comma(s: str) -> str:
    # In this document a comma between digits is always a decimal comma.
    # A space between a digit and a three-digit group is a thousands separator.
    s = re.sub(r"(?<=\d)[ \u00a0](?=\d{3}(?!\d))", "", s)
    return re.sub(r"(?<=\d),(?=\d)", ".", s)


def _balanced(expr: str) -> bool:
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _value(expr: str) -> float | None:
    if not _balanced(expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 - digits/operators only
    except (SyntaxError, ZeroDivisionError, ValueError, TypeError):
        return None


def check_text(text: str, source: str = "?") -> list[Finding]:
    """Return findings for every displayed numeric equality in *text*."""
    s = _decimal_comma(_plain(text))
    findings: list[Finding] = []
    for m in re.finditer(r"=", s):
        i = m.start()
        # Walk left over the numeric expression only.
        j = i
        while j > 0 and s[j - 1] in ALLOWED:
            j -= 1
        left = s[j:i].strip()
        if not left or not re.search(r"[+\-*/]", left):
            continue
        # If the expression starts inside a formula (e.g. H2SO4 · 2),
        # the preceding letter means we captured only a fragment.
        if j > 0 and (s[j - 1].isalpha() or s[j - 1] in ")]"):
            continue
        # A parenthesised factor immediately after a slash is a denominator,
        # not a complete equation (0,100 g/(179,2 · 0,200) = ...).
        if left.startswith("(") and j > 0 and s[j - 1] == "/":
            continue
        # A leading operator belongs to the preceding prose, not to this expression.
        left = re.sub(r"^[+\-*/ ]+", "", left).strip()
        if not left or not re.search(r"\d", left):
            continue
        # Require at least one operator between two numbers.
        if not re.search(rf"{NUM}\s*[+\-*/]\s*{NUM}", left):
            continue
        # Read the printed result, allowing a percent sign or a unit after it.
        tail = s[i + 1:i + 40]
        rm = re.match(r"\s*(-?\d+(?:\.\d+)?)(\s*%|\s*[A-Za-zµ]+)?", tail)
        if not rm:
            continue
        printed = rm.group(1)
        is_percent = bool(rm.group(2) and "%" in rm.group(2))
        try:
            printed_float = float(Decimal(printed))
        except InvalidOperation:
            continue
        actual = _value(left)
        if actual is None:
            continue
        decimals = len(printed.split(".")[1]) if "." in printed else 0
        tol = 0.5 * 10 ** (-decimals) + 1e-9
        delta = abs(actual - printed_float)
        delta_pct = abs(actual * 100.0 - printed_float) if is_percent else delta
        ok = delta <= tol or (is_percent and delta_pct <= tol)
        findings.append(Finding(
            source=source,
            expression=left,
            printed=printed,
            computed=f"{actual:.12g}",
            delta=f"{min(delta, delta_pct):.3g}",
            status="ok" if ok else "FAIL",
        ))
    # Adjacent bare numeric results in chains need their own comparison:
    # the left side of the second '=' has no arithmetic operator.
    for m in re.finditer(rf'=\s*({NUM})\s*=\s*({NUM})(?![\d.])(\s*%)?', s):
        left, printed = m.group(1), m.group(2)
        actual, target = Decimal(left), Decimal(printed)
        if m.group(3):
            actual *= 100
        decimals = len(printed.split('.')[1]) if '.' in printed else 0
        delta = abs(actual - target)
        tol = Decimal('0.5') * (Decimal(10) ** -decimals)
        findings.append(Finding(source, left, printed, str(actual), str(delta),
                                'ok' if delta <= tol else 'FAIL'))
    return findings


def audit_tasks() -> list[Finding]:
    # Importing the task modules registers TASKS in taskbase.
    import tasks_a  # noqa: F401
    import tasks_b  # noqa: F401
    from taskbase import TASKS

    out: list[Finding] = []
    for tid, t in TASKS.items():
        for field in ("calc", "check"):
            out.extend(check_text(t[field], f"{tid}.{field}"))
    return out


def write_report(findings, fixtures):
    from dataclasses import asdict
    from taskbase import TASKS
    bad = [f for f in findings if f.status != 'ok']
    report = {'scope': 'Parsed numeric equalities in task calc and check fields only; unparsed expressions are not verified.',
              'tasks': len(TASKS), 'parsed_equalities': len(findings), 'failures': len(bad),
              'findings': [asdict(f) for f in findings], 'fixtures': fixtures}
    (HERE / 'qa' / 'equations.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def main() -> int:
    findings = audit_tasks()
    bad = [f for f in findings if f.status != "ok"]
    from equation_fixtures import run_cases
    fixtures = run_cases()
    write_report(findings, fixtures)
    print(f"equations checked: {len(findings)}; failures: {len(bad)}")
    print(f"fixtures: {len(fixtures)}; mismatches: {sum(not x['passed'] for x in fixtures)}")
    print('scope: parsed task calc/check equalities only; skipped expressions are not verified')
    if bad:
        print("\nTask | expression | printed | computed | delta")
        for f in bad:
            print(f"{f.source} | {f.expression} | {f.printed} | {f.computed} | {f.delta}")
    else:
        print("all parsed equalities passed")
    return 1 if bad or any(not x['passed'] for x in fixtures) else 0


if __name__ == "__main__":
    raise SystemExit(main())
