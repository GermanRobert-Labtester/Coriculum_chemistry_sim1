#!/usr/bin/env python3
"""Shared helpers for the N02 coverage island: parsing, digests and constants.

This module is deliberately dependency-free (Python standard library only) so the
coverage gate, the anchor resolver and the build pipeline all run offline.
"""
from __future__ import annotations

import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable

DEST = Path(__file__).resolve().parents[1]

COVERAGE_PATH = 'data/coverage.json'
ISLAND_ID = 'sim-coverage'
SCHEMA_VERSION = 1

# The recorded expectation. A legitimate later count change updates this table
# and data/coverage.json's expected block in the same commit; the build gate's
# message says so explicitly.
EXPECTED_TOTAL = 64
EXPECTED_PER_TOPIC = {1: 9, 2: 10, 3: 11, 4: 11, 5: 10, 6: 8, 7: 5}

TOPIC_MASTER_PATHS = {
    1: 'materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html',
    2: 'materials/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html',
    3: 'materials/Chemistry_3/Master_3_tema_skidumi_un_koncentracijas.html',
    4: 'materials/Chemistry_4/Master_4_temats_termodinamika.html',
    5: 'materials/Chemistry_5/Master_5_tema_kinetika_un_katalize.html',
    6: 'materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html',
    7: 'materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html',
}

PLANNING_PATH = 'docs/PROGRAMME_COVERAGE_MATRIX.csv'
PROGRAMME_EXTRACT_PATH = 'evidence/programme_extracted.txt'
INVENTORY_PATH = 'evidence/SOURCE_FREEZE_INVENTORY.json'
FAMILIES_PATH = 'docs/QUESTION_FAMILIES.json'

OUTCOME_ID_RE = re.compile(r'^P([1-7])-([0-9]{2})$')
ANCHOR_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9-]*$')


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path | str) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_bytes(value) -> bytes:
    """The declared JSON emission rule for every simulator island.

    Sorted keys, no insignificant whitespace, UTF-8, Latvian text left readable.
    The build replaces ``</`` with ``<\\/`` before embedding, which is a JSON
    string escape and therefore preserves the parsed value byte for byte.
    """
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    return text.encode('utf-8')


def canonical_json_text(value) -> str:
    return canonical_json_bytes(value).decode('utf-8')


def escape_json_for_script(text: str) -> str:
    """Keep an embedded island from terminating its script element."""
    return text.replace('</', '<\\/')


def normalise_ws(text: str) -> str:
    return ' '.join(text.split())


def load_json(path: Path | str):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def load_island(path: Path | str = DEST / COVERAGE_PATH):
    return load_json(DEST / path if not Path(path).is_absolute() else path)


class MasterHTMLIndex(HTMLParser):
    """Collect ids, heading text and the first heading of each section.

    The resolver compares ids case-exactly; no lower-casing or Unicode
    normalisation is applied to an anchor.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.headings: dict[str, str] = {}
        self.section_headings: dict[str, str] = {}
        self._section_stack: list[str] = []
        self._heading_tag: str | None = None
        self._heading_id: str | None = None
        self._heading_section: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        element_id = values.get('id')
        if element_id:
            self.ids.append(element_id)
            if tag == 'section':
                self._section_stack.append(element_id)
        if tag in ('h1', 'h2', 'h3', 'h4'):
            self._heading_tag = tag
            self._heading_id = element_id
            self._heading_section = self._section_stack[-1] if self._section_stack else None
            self._heading_parts = []

    def handle_data(self, data):
        if self._heading_tag is not None:
            self._heading_parts.append(data)

    def handle_endtag(self, tag):
        if self._heading_tag is not None and tag == self._heading_tag:
            text = normalise_ws(''.join(self._heading_parts))
            if self._heading_id:
                self.headings[self._heading_id] = text
            if self._heading_section and self._heading_section not in self.section_headings:
                self.section_headings[self._heading_section] = text
            self._heading_tag = None
            self._heading_id = None
            self._heading_section = None
            self._heading_parts = []
        if tag == 'section' and self._section_stack:
            self._section_stack.pop()


def parse_master(path: Path | str) -> MasterHTMLIndex:
    parser = MasterHTMLIndex()
    parser.feed(Path(path).read_text(encoding='utf-8'))
    parser.close()
    return parser


def anchor_heading(index: MasterHTMLIndex, anchor: str) -> str | None:
    """Return the heading that owns ``anchor``, or None when it does not exist."""
    if anchor in index.headings:
        return index.headings[anchor]
    if anchor in index.section_headings:
        return index.section_headings[anchor]
    return None


def inventory_master_digests(repo_root: Path | str = DEST) -> dict[int, dict]:
    inventory = load_json(Path(repo_root) / INVENTORY_PATH)
    result: dict[int, dict] = {}
    for source in inventory.get('sources', []):
        if source.get('role') == 'canonical-master' and source.get('status') == 'FROZEN':
            result[int(source['topic'])] = source
    return result


def family_ids(repo_root: Path | str = DEST) -> set[str]:
    data = load_json(Path(repo_root) / FAMILIES_PATH)
    return {family['family_id'] for family in data['families']}


def find_cycle(edges: dict[str, list[str]]) -> list[str] | None:
    """Return one cycle as a node path (first node repeated), or None."""
    WHITE, GRAY, BLACK = 0, 1, 2
    colour = {node: WHITE for node in edges}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        colour[node] = GRAY
        stack.append(node)
        for target in edges.get(node, []):
            if target not in colour:
                continue
            if colour[target] == GRAY:
                start = stack.index(target)
                return stack[start:] + [target]
            if colour[target] == WHITE:
                found = visit(target)
                if found:
                    return found
        stack.pop()
        colour[node] = BLACK
        return None

    for node in sorted(edges):
        if colour[node] == WHITE:
            found = visit(node)
            if found:
                return found
    return None


def json_contains_unicode_escape(raw: bytes) -> bool:
    """True when a JSON source escaped non-ASCII text instead of writing UTF-8."""
    return b'\\u' in raw


def iter_outcomes(island: dict) -> Iterable[dict]:
    return island.get('outcomes', [])
