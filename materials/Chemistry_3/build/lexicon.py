# -*- coding: utf-8 -*-
"""Canonical quantity lexicon, course-notation map, and terminology lint gate.

This module is the single data-driven authority for quantities, symbols,
Latvian names, units, and course aliases in Topic 3.

It enforces:
- Canonical document symbols: c(B), M(B), w(B), γ(B), n(B), ρ, m(šķīdums).
- Machine-audited prohibition of obsolete or confusing variants (e.g. C_M, m_šķ)
  in narrative prose.
- Quotation and change-log exemptions for historically faithful citations.
- Parity between lexicon data, the chapter 14 mapping tables, and the chapter 16 formula sheet.
"""

from collections import Counter
from html.parser import HTMLParser
import re

QUANTITIES = [
    {
        'key': 'n',
        'canonical_symbol': 'n(B)',
        'canonical_latvian': 'vielas daudzums',
        'unit': 'mol',
        'aliases_seen_in_sources': ('n', 'mol'),
        'forbidden_in_document': (),
        'first_defined_chapter': 1,
    },
    {
        'key': 'M',
        'canonical_symbol': 'M(B)',
        'canonical_latvian': 'molmasa',
        'unit': 'g/mol',
        'aliases_seen_in_sources': ('M', 'molmasa', 'molārā masa'),
        'forbidden_in_document': (),
        'first_defined_chapter': 1,
    },
    {
        'key': 'c',
        'canonical_symbol': 'c(B)',
        'canonical_latvian': 'molārā koncentrācija',
        'unit': 'mol/L',
        'aliases_seen_in_sources': ('C_M', 'c_M', 'c', 'C', 'M'),
        'forbidden_in_document': (
            r'\bC_?M\b',
            r'\bc_M\b',
            r'\bC_\{M\}\b',
            r'C<sub>M</sub>',
            r'c<sub>M</sub>',
        ),
        'first_defined_chapter': 5,
    },
    {
        'key': 'w',
        'canonical_symbol': 'w(B)',
        'canonical_latvian': 'masas daļa',
        'unit': 'bez dimensijas vai %',
        'aliases_seen_in_sources': ('w', 'W', 'ω', 'W %', 'w %'),
        'forbidden_in_document': (
            r'\bW\s*%',
            r'\bW\b(?=\s*=\s*\d)',
        ),
        'first_defined_chapter': 5,
    },
    {
        'key': 'gamma',
        'canonical_symbol': 'γ(B)',
        'canonical_latvian': 'masas koncentrācija',
        'unit': 'g/L = mg/mL',
        'aliases_seen_in_sources': ('γ', 'g/L', 'mg/mL', 'm/V %'),
        'forbidden_in_document': (),
        'first_defined_chapter': 5,
    },
    {
        'key': 'rho',
        'canonical_symbol': 'ρ',
        'canonical_latvian': 'blīvums',
        'unit': 'g/mL',
        'aliases_seen_in_sources': ('ρ', 'blīvums', 'd'),
        'forbidden_in_document': (),
        'first_defined_chapter': 5,
    },
    {
        'key': 'm_solution',
        'canonical_symbol': 'm(šķīdums)',
        'canonical_latvian': 'šķīduma masa',
        'unit': 'g',
        'aliases_seen_in_sources': ('m_šķ', 'm(šķīd)', 'm(šķīdums)'),
        'forbidden_in_document': (
            r'\bm_šķ\b',
            r'\bm_sk\b',
            r'\bm\(šķīd\)',
        ),
        'first_defined_chapter': 5,
    },
    {
        'key': 'm_solute',
        'canonical_symbol': 'm(viela)',
        'canonical_latvian': 'izšķīdinātās vielas masa',
        'unit': 'g',
        'aliases_seen_in_sources': ('m(viela)', 'm_viela', 'm(B)'),
        'forbidden_in_document': (),
        'first_defined_chapter': 5,
    },
    {
        'key': 'm_solvent',
        'canonical_symbol': 'm(šķīdinātājs)',
        'canonical_latvian': 'šķīdinātāja masa',
        'unit': 'g',
        'aliases_seen_in_sources': ('m(šķīdinātājs)', 'm(ūdens)', 'm_H2O'),
        'forbidden_in_document': (),
        'first_defined_chapter': 5,
    },
    {
        'key': 'V',
        'canonical_symbol': 'V(šķīdums)',
        'canonical_latvian': 'šķīduma tilpums',
        'unit': 'mL, L',
        'aliases_seen_in_sources': ('V', 'V(šķīdums)', 'V_šķ'),
        'forbidden_in_document': (),
        'first_defined_chapter': 5,
    },
]

# Assert unique keys at module load time (Substep T01.1.1)
assert len({q['key'] for q in QUANTITIES}) == len(QUANTITIES), "Duplicate lexicon keys detected"
BY_KEY = {q['key']: q for q in QUANTITIES}
QUANTITY_KEYS = [q['key'] for q in QUANTITIES]

BLOCK = {'p', 'li', 'td', 'th', 'caption', 'summary', 'h1', 'h2', 'h3', 'h4', 'figcaption', 'div', 'article', 'section', 'br'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

EXEMPT_IDS = {'n16c', 'n16g', 'simbolu-lieta', 'table-kursa-pieraksts', 'kursa-pieraksts', 'table-zimigie-cipari'}
EXEMPT_CLASSES = {'role-source', 'source-note', 'source-line', 'prov p-source', 'p-source'}
EXEMPT_TABLE_KEYWORDS = (
    'lielumu apzīmējumi',
    'koncentrāciju veidi',
    'sastopamais termins',
    'apzīmējums, kursa variants',
    'kursa pieraksts',
    'avotu defekti k1–k23',
    'šī dokumenta apzinātie lēmumi',
    'zīmīgie cipari un noapaļošanas līgums',
)


class LexiconParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.parts = []
        self.startline = 1
        self.errors = []
        self.warnings = []
        self.in_exempt_table = False

    def flush(self):
        if not self.parts:
            return
        text = ''.join(self.parts)
        self.parts = []
        # Replace quotes «...» and “...” with whitespace of identical length
        unquoted = re.sub(r'«[^»]*»|“[^”]*”', lambda m: ' ' * len(m.group()), text)
        for q in QUANTITIES:
            for pat in q['forbidden_in_document']:
                for m in re.finditer(pat, unquoted):
                    line = self.startline + text.count('\n', 0, m.start())
                    ctx = text[max(0, m.start() - 40):min(len(text), m.end() + 40)].replace('\n', ' ')
                    self.errors.append(
                        f"lexicon error: forbidden alias {m.group()!r} for quantity '{q['canonical_symbol']}' at line {line}: ...{ctx}..."
                    )

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag in BLOCK:
            self.flush()
        classes = set((attr_dict.get('class') or '').split())
        elem_id = attr_dict.get('id', '')
        parent_skip = any(skip for _, skip, _, _ in self.stack)

        is_exempt_container = (
            parent_skip or
            tag in {'style', 'script', 'svg', 'code'} or
            'data-quote' in attr_dict or
            'data-unit-exempt' in attr_dict or
            'data-legacy-alias' in attr_dict or
            attr_dict.get('data-role') == 'source' or
            elem_id in EXEMPT_IDS or
            any(c in EXEMPT_CLASSES for c in classes) or
            self.in_exempt_table
        )

        if tag not in VOID:
            self.stack.append((tag, is_exempt_container, elem_id, classes))

    def handle_endtag(self, tag):
        if tag in BLOCK:
            self.flush()
        if tag == 'table':
            self.in_exempt_table = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        # Check if table caption identifies an exempt mapping table
        if self.stack and self.stack[-1][0] == 'caption':
            cap_lower = data.lower()
            if any(kw in cap_lower for kw in EXEMPT_TABLE_KEYWORDS):
                self.in_exempt_table = True
        if any(skip for _, skip, _, _ in self.stack):
            return
        if not self.parts:
            self.startline = self.getpos()[0]
        self.parts.append(data)

    def close(self):
        super().close()
        self.flush()


def count_usages(doc):
    counts = {}
    for q in QUANTITIES:
        key = q['key']
        sym = q['canonical_symbol']
        canonical_count = doc.count(sym) + doc.count(q['canonical_latvian'])
        counts[key] = {
            'symbol': sym,
            'canonical_count': canonical_count,
            'variant_count': 0,
        }
    return counts


def check_parity(doc):
    errors = []
    # 1. Formula sheet check (Table 22 / #n16a)
    n16a_match = re.search(r'<h3 id="n16a">[\s\S]*?</table>', doc)
    if not n16a_match:
        errors.append("lexicon parity error: formula sheet (#n16a) not found in document")
    else:
        sheet_text = n16a_match.group(0)
        core_formula_terms = [
            ('n', 'vielas daudzums'),
            ('M', 'g/mol'),
            ('c', 'molārā koncentrācija'),
            ('gamma', 'masas koncentrācija'),
            ('w', 'masas daļa'),
            ('m_solution', 'šķīduma masa'),
            ('rho', 'ρ'),
        ]
        for key, needle in core_formula_terms:
            if needle not in sheet_text:
                errors.append(f"lexicon parity error: core quantity '{key}' ({needle}) missing from formula sheet")

    # 2. Six-row mapping table check (#table-kursa-pieraksts)
    map_match = re.search(r'<table[^>]*id="table-kursa-pieraksts"[^>]*>([\s\S]*?)</table>', doc)
    if not map_match:
        errors.append("lexicon parity error: six-row mapping table (#table-kursa-pieraksts) missing")
    else:
        tbody = re.search(r'<tbody>([\s\S]*?)</tbody>', map_match.group(1))
        rows = re.findall(r'<tr>([\s\S]*?)</tr>', tbody.group(1)) if tbody else []
        if len(rows) != 6:
            errors.append(f"lexicon parity error: mapping table has {len(rows)} rows, expected exactly 6")
        for expected_alias in ['C<sub>M</sub>', 'W %', 'm_šķ', 'ml', 'l', 'm/V %']:
            if expected_alias not in map_match.group(1):
                errors.append(f"lexicon parity error: mapping table missing alias row for '{expected_alias}'")

    # 3. Latvian diacritics check
    if '\ufffd' in doc:
        errors.append("lexicon parity error: Unicode replacement character (U+FFFD) detected in document")

    return errors


def audit(doc):
    parser = LexiconParser()
    parser.feed(doc)
    parser.close()
    errors = list(parser.errors)
    warnings = list(parser.warnings)

    parity_errors = check_parity(doc)
    errors.extend(parity_errors)

    counts = count_usages(doc)
    for err in errors:
        for q in QUANTITIES:
            if q['canonical_symbol'] in err:
                counts[q['key']]['variant_count'] += 1

    return errors, warnings, counts


def summary_string(counts):
    parts = []
    for key in ['c', 'w', 'gamma', 'M', 'n', 'rho', 'm_solution']:
        if key in counts:
            sym = counts[key]['symbol']
            vc = counts[key]['variant_count']
            parts.append(f"{sym}: {vc} variants")
    total_variants = sum(v['variant_count'] for v in counts.values())
    return f"{', '.join(parts)}; total variants: {total_variants}"
