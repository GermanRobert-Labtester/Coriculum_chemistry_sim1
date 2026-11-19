#!/usr/bin/env python3
"""N31 Standalone Static Contract Checker & Build Gate 28 (tools/check_artifact.py).

Implements Main Step C and Subtask C.1 (C.1.1, C.1.2, C.1.3):
  - Asserts lang="lv", the 9 Section 1.2 ASCII anchors (#sakums through
    #iestatijumi) + #piemeri present once each, the 7 core Section 1.2 island
    ids (#sim-coverage, #sim-conventions, #sim-bank, #sim-forms,
    #sim-golden-vectors, #sim-terms, #sim-analytics) and all 22 declared JSON
    islands in order with valid JSON and matching digest meta tags.
  - Asserts a single executable <script> element (0 external scripts), with all
    37 module boundary separator comments (/* === MODULE: <path> === */) present
    in declared order and the assembled script parsing cleanly via Node's
    vm.Script parser binding.
  - Runs the offline external-URL scan (http:// and https://) with its declared
    license-comment whitelist policy, plus the injected-URL negative fixture
    that fails naming the URL, line number, and line context.
  - Measures the assembled artifact's exact byte composition table (islands,
    bank, figures/SVG specs, runtime JS, embedded JS data, CSS, template
    overhead) against tools/byte_budget.py sub-budgets, plus the oversized
    scratch island negative fixture that fails naming the offending segment.

Can be invoked standalone by N39's QA runner:
    python3 tools/check_artifact.py [--html output/simulator.html]
        [--manifest output/build-manifest.json]
        [--policy data/build_policy.json]
        [--report evidence/N31_ARTIFACT_CONTRACT.json]
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import byte_budget  # noqa: E402
from coverage_common import (  # noqa: E402
    ANCHOR_RE,
    DEST,
    canonical_json_bytes,
    load_json,
    sha256_bytes,
    sha256_file,
)

DEFAULT_HTML = DEST / "output/simulator.html"
DEFAULT_MANIFEST = DEST / "output/build-manifest.json"
DEFAULT_POLICY = DEST / "data/build_policy.json"

CORE_SECTION_1_2_ISLANDS = [
    "sim-coverage",
    "sim-conventions",
    "sim-bank",
    "sim-forms",
    "sim-golden-vectors",
    "sim-terms",
    "sim-analytics",
]

REQUIRED_SECTION_1_2_ANCHORS = [
    "sakums",
    "saturs",
    "prakse",
    "eksamens",
    "rezultati",
    "atskats",
    "metodika",
    "druka",
    "iestatijumi",
]

URL_RE = re.compile(r"https?://[^\s\"'<>)\]]+", re.IGNORECASE)


class ArtifactContractError(RuntimeError):
    """Raised when output/simulator.html violates any Section 1 contract."""


class _ArtifactHTMLInspector(HTMLParser):
    """Single-pass HTML structural inspector for output/simulator.html."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.html_lang: str | None = None
        self.metas: dict[str, str] = {}
        self.charset: str | None = None
        self.ids: list[str] = []
        self.section_ids: list[str] = []
        self.section_labelledby: dict[str, str | None] = {}
        self.internal_hrefs: list[str] = []
        self.external_scripts: list[str] = []
        self.external_stylesheets: list[str] = []
        self.json_islands: list[tuple[str, str]] = []
        self.executable_scripts: list[str] = []
        self.styles: list[str] = []

        self._active_script_kind: str | None = None
        self._active_island_id: str | None = None
        self._script_buf: list[str] = []
        self._in_style: bool = False
        self._style_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {k: (v if v is not None else "") for k, v in attrs}
        if tag == "html" and self.html_lang is None:
            self.html_lang = attr_map.get("lang")

        if "id" in attr_map:
            self.ids.append(attr_map["id"])

        if tag == "section" and "id" in attr_map:
            sec_id = attr_map["id"]
            self.section_ids.append(sec_id)
            self.section_labelledby[sec_id] = attr_map.get("aria-labelledby")

        if tag == "a":
            href = attr_map.get("href", "")
            if href.startswith("#") and len(href) > 1:
                self.internal_hrefs.append(href[1:])

        if tag == "meta":
            if "charset" in attr_map:
                self.charset = attr_map["charset"]
            name = attr_map.get("name")
            if name:
                self.metas[name] = attr_map.get("content", "")

        if tag == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "")
            if "stylesheet" in rel and href:
                self.external_stylesheets.append(href)

        if tag == "style":
            self._in_style = True
            self._style_buf = []

        if tag == "script":
            src = attr_map.get("src", "").strip()
            if src:
                self.external_scripts.append(src)
            script_type = attr_map.get("type", "").strip().lower()
            if script_type == "application/json":
                self._active_script_kind = "json"
                self._active_island_id = attr_map.get("id", "")
            else:
                self._active_script_kind = "exec"
                self._active_island_id = None
            self._script_buf = []

    def handle_data(self, data: str) -> None:
        if self._active_script_kind is not None:
            self._script_buf.append(data)
        if self._in_style:
            self._style_buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._active_script_kind is not None:
            content = "".join(self._script_buf)
            if self._active_script_kind == "json":
                self.json_islands.append((self._active_island_id or "", content))
            else:
                self.executable_scripts.append(content)
            self._active_script_kind = None
            self._active_island_id = None
            self._script_buf = []
        elif tag == "style" and self._in_style:
            self.styles.append("".join(self._style_buf))
            self._in_style = False
            self._style_buf = []


def scan_offline_urls(
    html_text: str,
    whitelist_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Subtask C.1.2: scan html_text line-by-line for http:// and https://.

    Only URLs appearing inside a line beginning with the declared
    whitelisted_comment_prefix AND explicitly listed in allowed_upstream_urls
    are exempt. Every other URL fails with its URL, line number, and line
    context recorded.
    """
    whitelist_policy = whitelist_policy or {}
    comment_prefix = str(
        whitelist_policy.get("whitelisted_comment_prefix", "<!-- LICENSE-UPSTREAM:")
    )
    allowed_urls = set(whitelist_policy.get("allowed_upstream_urls", []))

    violations: list[dict[str, Any]] = []
    whitelisted_hits: list[dict[str, Any]] = []

    for line_no, raw_line in enumerate(html_text.splitlines(), start=1):
        matches = list(URL_RE.finditer(raw_line))
        if not matches:
            continue
        stripped = raw_line.strip()
        is_license_comment = stripped.startswith(comment_prefix) and stripped.endswith("-->")
        for m in matches:
            url = m.group(0)
            start_ctx = max(0, m.start() - 40)
            end_ctx = min(len(raw_line), m.end() + 40)
            context_snippet = raw_line[start_ctx:end_ctx].strip()
            if is_license_comment and url in allowed_urls:
                whitelisted_hits.append(
                    {
                        "url": url,
                        "line": line_no,
                        "line_context": context_snippet,
                    }
                )
            else:
                violations.append(
                    {
                        "url": url,
                        "line": line_no,
                        "line_context": context_snippet,
                    }
                )

    return {
        "status": "PASS" if not violations else "FAIL",
        "external_url_count": len(violations),
        "whitelisted_url_count": len(whitelisted_hits),
        "violations": violations,
        "whitelisted_hits": whitelisted_hits,
    }


def run_offline_url_scan_fixture(
    html_text: str,
    whitelist_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Subtask C.1.2 fixture:
      1. Injects one external URL into a scratch copy of the artifact and proves
         scan_offline_urls fails naming the URL, line number, and line context.
      2. Tests that an explicitly whitelisted <!-- LICENSE-UPSTREAM: ... -->
         comment is ignored when listed in allowed_upstream_urls, while an
         unlisted URL inside a comment still fails.
    """
    injected_url = "https://cdn.example.invalid/external-tracker.js"
    injected_line = f'<script src="{injected_url}"></script>'
    lines = html_text.splitlines()
    insert_idx = min(10, len(lines))
    scratch_lines = lines[:insert_idx] + [injected_line] + lines[insert_idx:]
    scratch_html = "\n".join(scratch_lines)

    res_injected = scan_offline_urls(scratch_html, whitelist_policy)
    if res_injected["status"] != "FAIL" or res_injected["external_url_count"] != 1:
        raise ArtifactContractError(
            "C.1.2 offline URL scan fixture failed to catch injected external URL"
        )
    hit = res_injected["violations"][0]
    if (
        hit["url"] != injected_url
        or hit["line"] != insert_idx + 1
        or injected_url not in hit["line_context"]
    ):
        raise ArtifactContractError(
            f"C.1.2 offline URL scan fixture did not report expected URL/line/context: {hit}"
        )

    # Whitelist exemption check
    upstream_url = "https://upstream.example.invalid/LICENSE"
    whitelist_test_policy = {
        "whitelisted_comment_prefix": "<!-- LICENSE-UPSTREAM:",
        "allowed_upstream_urls": [upstream_url],
    }
    scratch_whitelisted = (
        f"<!-- LICENSE-UPSTREAM: {upstream_url} -->\n" + html_text
    )
    res_whitelisted = scan_offline_urls(scratch_whitelisted, whitelist_test_policy)
    if res_whitelisted["status"] != "PASS" or res_whitelisted["whitelisted_url_count"] != 1:
        raise ArtifactContractError(
            f"C.1.2 whitelist exemption check failed: {res_whitelisted}"
        )

    return {
        "status": "PASS",
        "injected_url_caught": True,
        "injected_url": hit["url"],
        "injected_line": hit["line"],
        "injected_line_context": hit["line_context"],
        "whitelist_exemption_verified": True,
    }


def verify_script_syntax_and_boundaries(
    script_text: str,
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Subtask B.1.2 / C.1.1: verify that the single executable script parses
    cleanly using the JS engine's own parser bindings (node vm.Script) and that
    every declared module boundary separator comment is present in exact order.
    """
    declared_modules = policy["module_order"]
    expected_separators = [
        f"/* === MODULE: {mod['path']} === */" for mod in declared_modules
    ]
    bootstrap_sep = policy["single_script_wrapper"]["bootstrap_separator"]

    found_positions: list[int] = []
    missing_separators: list[str] = []
    for sep in expected_separators:
        pos = script_text.find(sep)
        if pos < 0:
            missing_separators.append(sep)
        else:
            found_positions.append(pos)

    if missing_separators:
        raise ArtifactContractError(
            f"E_SCRIPT_MISSING_SEPARATORS: missing module boundary comments: {missing_separators[:5]}"
        )

    if found_positions != sorted(found_positions):
        raise ArtifactContractError(
            "E_SCRIPT_SEPARATOR_ORDER: module boundary separator comments are not in declared topological order"
        )

    bootstrap_pos = script_text.find(bootstrap_sep)
    if bootstrap_pos < 0 or (found_positions and bootstrap_pos < found_positions[-1]):
        raise ArtifactContractError(
            f"E_SCRIPT_BOOTSTRAP_SEPARATOR: missing or misplaced bootstrap separator '{bootstrap_sep}'"
        )

    # Parse script using Node's vm.Script parser bindings
    node_code = (
        "const fs = require('fs'); const vm = require('vm');"
        "const src = fs.readFileSync(0, 'utf8');"
        "new vm.Script(src, { filename: 'output/simulator.html#inline-script' });"
        "process.stdout.write('PARSE_OK');"
    )
    proc = subprocess.run(
        ["node", "-e", node_code],
        input=script_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0 or proc.stdout.strip() != "PARSE_OK":
        raise ArtifactContractError(
            f"E_SCRIPT_SYNTAX_ERROR: inline script failed Node vm.Script syntax parse: {proc.stderr.strip()}"
        )

    return {
        "status": "PASS",
        "script_parses_cleanly": True,
        "parser_engine": "node:vm.Script",
        "module_boundaries_count": len(expected_separators),
        "bootstrap_boundary_present": True,
        "first_module_boundary": expected_separators[0],
        "last_module_boundary": expected_separators[-1],
    }


def compute_composition_table(
    html_text: str,
    inspector: _ArtifactHTMLInspector,
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Subtask C.1: measure the assembled file's actual byte composition directly
    from output/simulator.html and evaluate against tools/byte_budget.py
    sub-budgets.
    """
    artifact_total_bytes = len(html_text.encode("utf-8"))
    css_text = "\n".join(inspector.styles).strip()
    css_bytes = len(css_text.encode("utf-8"))

    island_bytes_by_id: dict[str, int] = {}
    for iid, raw_content in inspector.json_islands:
        island_bytes_by_id[iid] = len(raw_content.encode("utf-8"))

    bank_island_bytes = island_bytes_by_id.get("sim-bank", 0)
    figures_island_bytes = island_bytes_by_id.get("sim-figures", 0)
    islands_total_bytes = sum(island_bytes_by_id.values())
    other_islands_bytes = islands_total_bytes - bank_island_bytes - figures_island_bytes

    exec_script = inspector.executable_scripts[0] if inspector.executable_scripts else ""
    exec_script_total_bytes = len(exec_script.encode("utf-8"))

    # Separate the 4 embedded data projection lines (var COVERAGE_INVARIANTS = ...; etc.)
    # from the executable runtime JS code, matching tools/build.py accounting.
    data_projection_prefixes = tuple(
        f"var {entry['global_name']} = " for entry in policy["data_projection_globals"]
    )
    embedded_js_data_lines: list[str] = []
    runtime_js_code_lines: list[str] = []
    for line in exec_script.splitlines():
        if line.startswith(data_projection_prefixes):
            embedded_js_data_lines.append(line)
        else:
            runtime_js_code_lines.append(line)

    embedded_js_data_bytes = len("\n".join(embedded_js_data_lines).encode("utf-8"))
    runtime_js_code_bytes = len("\n".join(runtime_js_code_lines).strip().encode("utf-8"))

    template_overhead_bytes = (
        artifact_total_bytes - islands_total_bytes - exec_script_total_bytes - css_bytes
    )

    synthetic_manifest = {
        "output_bytes": artifact_total_bytes,
        "tokens_layer": {
            "runtime_js_code_bytes": runtime_js_code_bytes,
            "css_bytes": css_bytes,
        },
        "bank_island": {
            "bytes": bank_island_bytes,
        },
        "figures_layer": {
            "island_bytes": figures_island_bytes,
        },
    }
    budget_eval = byte_budget.measure_budgets(synthetic_manifest)

    segments = [
        {
            "segment": "bank_island",
            "description": "Frozen #sim-bank JSON island (112 reviewed instances across 28 families)",
            "bytes": bank_island_bytes,
            "kib": round(bank_island_bytes / 1024, 1),
            "share_percent_of_artifact": round(bank_island_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": list(byte_budget.DECLARED_BANDS["bank_island"]),
            "enforced_ceiling_bytes": byte_budget.ENFORCED_CEILINGS["bank_island"],
            "within_ceiling": bank_island_bytes <= byte_budget.ENFORCED_CEILINGS["bank_island"],
        },
        {
            "segment": "figures_island",
            "description": "Declarative SVG figure specs (#sim-figures, 45 T1–T7 records)",
            "bytes": figures_island_bytes,
            "kib": round(figures_island_bytes / 1024, 1),
            "share_percent_of_artifact": round(figures_island_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": list(byte_budget.DECLARED_BANDS["figures_island"]),
            "enforced_ceiling_bytes": byte_budget.ENFORCED_CEILINGS["figures_island"],
            "within_ceiling": figures_island_bytes <= byte_budget.ENFORCED_CEILINGS["figures_island"],
        },
        {
            "segment": "other_islands",
            "description": "Remaining 20 JSON islands (coverage, conventions, forms, golden vectors, terms, analytics, policies, chains, engines, method cards, grading)",
            "bytes": other_islands_bytes,
            "kib": round(other_islands_bytes / 1024, 1),
            "share_percent_of_artifact": round(other_islands_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": None,
            "enforced_ceiling_bytes": None,
            "within_ceiling": True,
        },
        {
            "segment": "runtime_js_code",
            "description": "37 inlined runtime JS modules + bootstrap + module boundary comments",
            "bytes": runtime_js_code_bytes,
            "kib": round(runtime_js_code_bytes / 1024, 1),
            "share_percent_of_artifact": round(runtime_js_code_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": list(byte_budget.DECLARED_BANDS["runtime_js_code"]),
            "enforced_ceiling_bytes": byte_budget.ENFORCED_CEILINGS["runtime_js_code"],
            "within_ceiling": runtime_js_code_bytes <= byte_budget.ENFORCED_CEILINGS["runtime_js_code"],
        },
        {
            "segment": "embedded_js_data",
            "description": "4 canonical JS data projection globals (COVERAGE_INVARIANTS, CONCEPT_DRAWER_DATA, ANCHOR_REGISTRY, RECALL_LAYERS_DATA)",
            "bytes": embedded_js_data_bytes,
            "kib": round(embedded_js_data_bytes / 1024, 1),
            "share_percent_of_artifact": round(embedded_js_data_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": None,
            "enforced_ceiling_bytes": None,
            "within_ceiling": True,
        },
        {
            "segment": "css",
            "description": "Inline <style> block (src/tokens.css + src/styles.css)",
            "bytes": css_bytes,
            "kib": round(css_bytes / 1024, 1),
            "share_percent_of_artifact": round(css_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": list(byte_budget.DECLARED_BANDS["css"]),
            "enforced_ceiling_bytes": byte_budget.ENFORCED_CEILINGS["css"],
            "within_ceiling": css_bytes <= byte_budget.ENFORCED_CEILINGS["css"],
        },
        {
            "segment": "template_overhead",
            "description": "HTML5 skeleton markup, Latvian copy, meta digest tags, and <script>/<style> wrappers",
            "bytes": template_overhead_bytes,
            "kib": round(template_overhead_bytes / 1024, 1),
            "share_percent_of_artifact": round(template_overhead_bytes / artifact_total_bytes * 100, 2),
            "declared_band_bytes": None,
            "enforced_ceiling_bytes": None,
            "within_ceiling": True,
        },
        {
            "segment": "artifact_total",
            "description": "Complete single-file deliverable output/simulator.html",
            "bytes": artifact_total_bytes,
            "kib": round(artifact_total_bytes / 1024, 1),
            "share_percent_of_artifact": 100.0,
            "declared_band_bytes": list(byte_budget.DECLARED_BANDS["artifact_total"]),
            "enforced_ceiling_bytes": byte_budget.ENFORCED_CEILINGS["artifact_total"],
            "within_ceiling": artifact_total_bytes <= byte_budget.ENFORCED_CEILINGS["artifact_total"],
        },
    ]

    return {
        "status": budget_eval["status"],
        "failed_segments": budget_eval["failed_segments"],
        "artifact_total_bytes": artifact_total_bytes,
        "islands_total_bytes": islands_total_bytes,
        "bank_island_bytes": bank_island_bytes,
        "figures_island_bytes": figures_island_bytes,
        "other_islands_bytes": other_islands_bytes,
        "runtime_js_code_bytes": runtime_js_code_bytes,
        "embedded_js_data_bytes": embedded_js_data_bytes,
        "executable_script_total_bytes": exec_script_total_bytes,
        "css_bytes": css_bytes,
        "template_overhead_bytes": template_overhead_bytes,
        "island_bytes_by_id": island_bytes_by_id,
        "segments": segments,
        "budgets": budget_eval["budgets"],
    }


def run_oversized_island_fixture(
    composition: dict[str, Any],
) -> dict[str, Any]:
    """Subtask C.1 negative fixture: prove that an oversized scratch island
    exceeding its sub-budget ceiling fails the budget check and explicitly names
    the offending segment (bank_island and figures_island).
    """
    oversized_bank_manifest = {
        "output_bytes": composition["artifact_total_bytes"],
        "tokens_layer": {
            "runtime_js_code_bytes": composition["runtime_js_code_bytes"],
            "css_bytes": composition["css_bytes"],
        },
        "bank_island": {
            "bytes": byte_budget.ENFORCED_CEILINGS["bank_island"] + 32768,
        },
        "figures_layer": {
            "island_bytes": composition["figures_island_bytes"],
        },
    }
    eval_bank = byte_budget.measure_budgets(oversized_bank_manifest)
    if eval_bank["status"] != "FAIL" or "bank_island" not in eval_bank["failed_segments"]:
        raise ArtifactContractError(
            f"C.1 oversized bank_island fixture did not fail naming bank_island: {eval_bank}"
        )

    oversized_figures_manifest = {
        "output_bytes": composition["artifact_total_bytes"],
        "tokens_layer": {
            "runtime_js_code_bytes": composition["runtime_js_code_bytes"],
            "css_bytes": composition["css_bytes"],
        },
        "bank_island": {
            "bytes": composition["bank_island_bytes"],
        },
        "figures_layer": {
            "island_bytes": byte_budget.ENFORCED_CEILINGS["figures_island"] + 16384,
        },
    }
    eval_figures = byte_budget.measure_budgets(oversized_figures_manifest)
    if eval_figures["status"] != "FAIL" or "figures_island" not in eval_figures["failed_segments"]:
        raise ArtifactContractError(
            f"C.1 oversized figures_island fixture did not fail naming figures_island: {eval_figures}"
        )

    return {
        "status": "PASS",
        "oversized_bank_island_case": {
            "injected_bytes": oversized_bank_manifest["bank_island"]["bytes"],
            "ceiling_bytes": byte_budget.ENFORCED_CEILINGS["bank_island"],
            "status": eval_bank["status"],
            "failed_segments": eval_bank["failed_segments"],
        },
        "oversized_figures_island_case": {
            "injected_bytes": oversized_figures_manifest["figures_layer"]["island_bytes"],
            "ceiling_bytes": byte_budget.ENFORCED_CEILINGS["figures_island"],
            "status": eval_figures["status"],
            "failed_segments": eval_figures["failed_segments"],
        },
    }


class _NoScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.classes: set[str] = set()
        self.tags: set[str] = set()
        self.hrefs: list[str] = []
        self.interactive_tags: list[str] = []
        self.notice_count: int = 0
        self.in_noscript: bool = False
        self.noscript_ids: set[str] = set()
        self.noscript_hrefs: list[str] = []
        self.noscript_interactive: list[str] = []
        self.noscript_text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        self.tags.add(t)
        amap = {k.lower(): (v or "") for k, v in attrs}
        if t == "noscript":
            self.in_noscript = True
        el_id = amap.get("id", "")
        if el_id:
            self.ids.add(el_id)
            if self.in_noscript:
                self.noscript_ids.add(el_id)
            if el_id == "noscript-pazinojums":
                self.notice_count += 1
        cls = amap.get("class", "")
        for c in cls.split():
            if c:
                self.classes.add(c)
        if t == "a" and "href" in amap:
            href = amap["href"]
            self.hrefs.append(href)
            if self.in_noscript:
                self.noscript_hrefs.append(href)
        if self.in_noscript and t in {"input", "button", "select", "textarea"}:
            self.noscript_interactive.append(t)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "noscript":
            self.in_noscript = False

    def handle_data(self, data: str) -> None:
        if self.in_noscript:
            self.noscript_text_parts.append(data)


def check_noscript_fallback(html_text: str, expected_term_count: int | None = None) -> dict[str, Any]:
    """N34 noscript pass: strip <script> elements, parse no-JS DOM, verify anchors, single notice, zero interactive controls."""
    stripped = re.sub(r"<script\b[^>]*>[\s\S]*?</script>", "", html_text, flags=re.IGNORECASE)
    parser = _NoScriptParser()
    parser.feed(stripped)
    parser.close()

    errors: list[str] = []
    if parser.notice_count != 1:
        errors.append(f"E_NOSCRIPT_NOTICE_COUNT: expected exactly 1 #noscript-pazinojums notice, found {parser.notice_count}")

    dangling_links: list[str] = []
    external_links: list[str] = []
    for href in parser.noscript_hrefs:
        if href.startswith("#"):
            target = href[1:]
            if target not in parser.ids:
                dangling_links.append(href)
        elif href.startswith("http://") or href.startswith("https://") or href.startswith("//"):
            external_links.append(href)
        else:
            dangling_links.append(href)

    if dangling_links:
        errors.append(f"E_NOSCRIPT_DANGLING_LINK: unresolved internal links in <noscript>: {dangling_links}")
    if external_links:
        errors.append(f"E_NOSCRIPT_EXTERNAL_URL: external links forbidden in <noscript>: {external_links}")
    if parser.noscript_interactive:
        errors.append(f"E_NOSCRIPT_INTERACTIVE_CONTROL: interactive controls forbidden in <noscript>: {parser.noscript_interactive}")

    concept_nodes = sorted(eid for eid in parser.noscript_ids if eid.startswith("karte-P"))
    if len(concept_nodes) < 64:
        errors.append(f"E_NOSCRIPT_CONCEPT_COUNT: expected 64 concept anchors in <noscript>, found {len(concept_nodes)}")

    noscript_blob = "".join(parser.noscript_text_parts)
    if "#druka" not in " ".join(parser.noscript_hrefs):
        errors.append("E_NOSCRIPT_PRINT_XREF: <noscript> must cross-reference #druka")

    return {
        "status": "PASS" if not errors else "FAIL",
        "notice_count": parser.notice_count,
        "concept_anchors_count": len(concept_nodes),
        "noscript_links_checked": len(parser.noscript_hrefs),
        "dangling_links": dangling_links,
        "external_links": external_links,
        "interactive_controls": parser.noscript_interactive,
        "has_terms_table": "noscript-terms-table" in parser.classes,
        "noscript_text_chars": len(noscript_blob),
        "expected_term_count": expected_term_count,
        "errors": errors,
    }


_KNOWN_RUNTIME_PRINT_CLASSES = {
    "chain", "chain-title", "chain-subtitle", "chain-citation", "chain-banner",
    "chain-given", "chain-step-quantity", "chain-step-statement", "chain-result-value",
    "chain-result-reasoning", "chain-figure-placeholder", "chain-print-note",
    "chain-step", "chain-reveal-btn", "chain-reveal-all", "chain-collapse",
    "chain-confirm", "chain-print-note-collapsed", "chain-result", "chain-givens",
    "fig-svg", "fig-theme-print", "fig-frame", "fig-bg", "fig-node-box",
    "fig-node-highlight", "fig-annot-box", "fig-band-primary", "fig-band-secondary",
    "fig-band-accent", "fig-band-tol", "fig-indicator-band", "fig-buffer-region",
    "fig-strip-box", "fig-bar-primary", "fig-bar-secondary", "fig-bar-accent",
    "fig-axis-line", "fig-grid", "fig-arrow-line", "fig-data-line", "fig-data-line-alt",
    "fig-fit-line", "fig-draw-line", "fig-threshold-line", "fig-level-line",
    "fig-hess-direct", "fig-hess-reverse", "fig-glass-wall", "fig-meniscus-curve",
    "fig-sight-line", "fig-parallax-line", "fig-tick-major", "fig-tick-minor",
    "fig-flask-mark", "fig-equivalence-line", "fig-half-line", "fig-endpoint-line",
    "fig-reading-line", "fig-strip-meniscus", "fig-tail-shade-primary",
    "fig-tail-shade-secondary", "fig-liquid-clear", "fig-liquid-dark",
    "fig-tick-text", "fig-axis-label", "fig-title-text", "fig-subtitle-text",
    "fig-value-label", "fig-legend-text", "fig-annot-text", "fig-arrow-head",
    "fig-point-dot", "fig-reading-dot", "fig-print-note", "fig-caption",
    "paper-sheet", "paper-slot", "paper-point-table", "paper-work-grid",
    "paper-controls", "paper-empty-state", "paper-conflict-note",
    "theme-print", "prakse-runner-controls", "exam-timer-bar", "store-actions",
    "coverage-topic", "map-topic", "map-layer", "map-node", "map-cross-section", "fig-card",
}


def _extract_media_print_blocks(css_text: str) -> list[str]:
    blocks: list[str] = []
    idx = 0
    pattern = re.compile(r"@media\s+print\s*\{")
    while True:
        m = pattern.search(css_text, idx)
        if not m:
            break
        start = m.end()
        depth = 1
        pos = start
        while pos < len(css_text) and depth > 0:
            ch = css_text[pos]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            pos += 1
        blocks.append(css_text[start : pos - 1])
        idx = pos
    return blocks


def check_print_rules(html_text: str) -> dict[str, Any]:
    """N34 print-rule static validation: verify every @media print selector targets a known HTML/runtime element."""
    parser = _NoScriptParser()
    parser.feed(html_text)
    parser.close()

    known_ids = parser.ids
    known_classes = parser.classes | _KNOWN_RUNTIME_PRINT_CLASSES
    known_tags = parser.tags | {"body", "html", "details", "a", "code", "dt", "dd"}

    style_blocks = re.findall(r"<style\b[^>]*>([\s\S]*?)</style>", html_text, flags=re.IGNORECASE)
    css_text = "\n".join(style_blocks)
    print_blocks = _extract_media_print_blocks(css_text)

    errors: list[str] = []
    if not print_blocks:
        errors.append("E_PRINT_NO_MEDIA_BLOCK: no @media print blocks found in stylesheet")

    selectors_checked: list[str] = []
    unmatched_selectors: list[str] = []
    for block in print_blocks:
        # Remove declarations inside { ... } to isolate selector lists
        cleaned = re.sub(r"\{[^{}]*\}", ";", block)
        for stmt in cleaned.split(";"):
            sel_group = stmt.strip()
            if not sel_group:
                continue
            for raw_sel in sel_group.split(","):
                sel = raw_sel.strip()
                if not sel:
                    continue
                selectors_checked.append(sel)
                # Strip pseudo-classes/elements and attribute selectors for token check
                core = re.sub(r":not\([^)]*\)", "", sel)
                core = re.sub(r"::[a-zA-Z0-9_-]+|:[a-zA-Z0-9_-]+(?:\([^)]*\))?", "", core)
                core_no_attr = re.sub(r"\[[^\]]*\]", "", core).strip()
                # Check #id tokens
                id_tokens = re.findall(r"#([A-Za-z0-9_-]+)", core_no_attr)
                cls_tokens = re.findall(r"\.([A-Za-z0-9_-]+)", core_no_attr)
                matched = True
                for idt in id_tokens:
                    if idt not in known_ids:
                        matched = False
                        break
                if matched:
                    for clst in cls_tokens:
                        if clst not in known_classes:
                            matched = False
                            break
                if matched and not id_tokens and not cls_tokens and core_no_attr and core_no_attr != "*":
                    tag_tokens = re.findall(r"\b([a-zA-Z][a-zA-Z0-9-]*)\b", core_no_attr)
                    for tt in tag_tokens:
                        if tt.lower() not in known_tags:
                            matched = False
                            break
                if not matched:
                    unmatched_selectors.append(sel)

    if unmatched_selectors:
        errors.append(f"E_PRINT_UNMATCHED_SELECTOR: @media print selectors match no known element/class: {unmatched_selectors}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "media_print_blocks": len(print_blocks),
        "selectors_checked": len(selectors_checked),
        "unmatched_selectors": unmatched_selectors,
        "errors": errors,
    }


def check_artifact(
    html_path: Path = DEFAULT_HTML,
    manifest_path: Path | None = DEFAULT_MANIFEST,
    policy_path: Path = DEFAULT_POLICY,
    html_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Run the full static contract check over output/simulator.html."""
    errors: list[str] = []
    if html_bytes is None:
        if not html_path.is_file():
            raise ArtifactContractError(f"Deliverable artifact does not exist: {html_path}")
        html_bytes = html_path.read_bytes()
    if not policy_path.is_file():
        raise ArtifactContractError(f"Build policy does not exist: {policy_path}")

    policy = load_json(policy_path)
    html_sha256 = sha256_bytes(html_bytes)
    html_text = html_bytes.decode("utf-8")

    inspector = _ArtifactHTMLInspector()
    inspector.feed(html_text)

    # 1. lang="lv" and meta tags
    if inspector.html_lang != "lv":
        errors.append(f'Expected <html lang="lv">, got lang={inspector.html_lang!r}')
    if (inspector.charset or "").lower() != "utf-8":
        errors.append(f'Expected <meta charset="utf-8">, got {inspector.charset!r}')
    if inspector.metas.get("viewport") != "width=device-width, initial-scale=1":
        errors.append(f"Unexpected viewport meta: {inspector.metas.get('viewport')!r}")
    if inspector.metas.get("color-scheme") != "light dark":
        errors.append(f"Unexpected color-scheme meta: {inspector.metas.get('color-scheme')!r}")

    for meta_key in policy["metadata_stamp"]["meta_tags"]:
        if not inspector.metas.get(meta_key):
            errors.append(f"Missing or empty metadata stamp <meta name={meta_key!r}>")

    # 2. Nine Section 1.2 ASCII anchors + auxiliary #piemeri
    anchor_counts = {
        anchor: inspector.section_ids.count(anchor)
        for anchor in REQUIRED_SECTION_1_2_ANCHORS
    }
    for anchor, count in anchor_counts.items():
        if count != 1:
            errors.append(f"Section 1.2 anchor #{anchor} count is {count}, expected 1")
        labelledby = inspector.section_labelledby.get(anchor)
        if not labelledby or labelledby not in inspector.ids:
            errors.append(
                f"Section 1.2 anchor #{anchor} has missing/unresolved aria-labelledby={labelledby!r}"
            )

    expected_all_landmarks = policy["blueprint_anchors"]["all_landmarks"]
    found_top_landmarks = [s for s in inspector.section_ids if s in expected_all_landmarks]
    if found_top_landmarks != expected_all_landmarks:
        errors.append(
            f"Top-level landmark order mismatch: expected {expected_all_landmarks}, found {found_top_landmarks}"
        )

    # 3. Seven core Section 1.2 islands and all 22 declared JSON islands
    declared_islands = policy["islands"]["insertion_order"]
    declared_island_ids = [entry["island_id"] for entry in declared_islands]
    found_island_ids = [iid for iid, _ in inspector.json_islands]

    for core_id in CORE_SECTION_1_2_ISLANDS:
        if found_island_ids.count(core_id) != 1:
            errors.append(
                f"Core Section 1.2 island #{core_id} count is {found_island_ids.count(core_id)}, expected 1"
            )

    if found_island_ids != declared_island_ids:
        errors.append(
            f"Island order/set mismatch: expected {declared_island_ids}, found {found_island_ids}"
        )

    island_content_map = dict(inspector.json_islands)
    verified_island_digests: dict[str, str] = {}
    for entry in declared_islands:
        iid = entry["island_id"]
        raw_content = island_content_map.get(iid, "")
        if not raw_content:
            errors.append(f"Island #{iid} is empty or missing")
            continue
        unescaped = raw_content.replace("<\\/", "</")
        try:
            parsed = json.loads(unescaped)
        except json.JSONDecodeError as exc:
            errors.append(f"Island #{iid} contains invalid JSON: {exc}")
            continue
        # Verify canonical key-sorted emission
        canonical_str = canonical_json_bytes(parsed).decode("utf-8")
        if unescaped != canonical_str:
            errors.append(f"Island #{iid} is not emitted in canonical key-sorted JSON form")
        # Verify digest meta tag
        meta_name = entry["digest_meta_name"]
        meta_digest = inspector.metas.get(meta_name, "")
        actual_raw_digest = sha256_bytes(raw_content.encode("utf-8"))
        actual_unescaped_digest = sha256_bytes(unescaped.encode("utf-8"))
        if meta_digest not in (actual_raw_digest, actual_unescaped_digest):
            errors.append(
                f"Island #{iid} digest meta {meta_name}={meta_digest} does not match content digest {actual_raw_digest}"
            )
        verified_island_digests[iid] = actual_raw_digest

    # 4. Single executable script element, 0 external scripts/stylesheets, syntax & boundary comments
    if len(inspector.executable_scripts) != 1:
        errors.append(
            f"Expected exactly 1 executable <script> element, found {len(inspector.executable_scripts)}"
        )
    if inspector.external_scripts:
        errors.append(f"External <script src> elements forbidden: {inspector.external_scripts}")
    if inspector.external_stylesheets:
        errors.append(
            f"External stylesheet <link> elements forbidden: {inspector.external_stylesheets}"
        )

    script_check: dict[str, Any] = {}
    if len(inspector.executable_scripts) == 1:
        try:
            script_check = verify_script_syntax_and_boundaries(
                inspector.executable_scripts[0], policy
            )
        except ArtifactContractError as exc:
            errors.append(str(exc))
            script_check = {"status": "FAIL", "error": str(exc)}

    # 5. Offline URL scan + injected URL negative fixture
    url_scan = scan_offline_urls(html_text, policy.get("offline_url_whitelist"))
    if url_scan["status"] != "PASS":
        for v in url_scan["violations"]:
            errors.append(
                f"E_OFFLINE_EXTERNAL_URL: external URL {v['url']} at line {v['line']} ({v['line_context']})"
            )
    url_fixture = run_offline_url_scan_fixture(html_text, policy.get("offline_url_whitelist"))

    # 6. V-10 unique ASCII IDs and internal #anchor resolution
    seen_ids: set[str] = set()
    duplicate_ids: list[str] = []
    non_ascii_ids: list[str] = []
    for elem_id in inspector.ids:
        if elem_id in seen_ids and elem_id not in duplicate_ids:
            duplicate_ids.append(elem_id)
        seen_ids.add(elem_id)
        if not elem_id.isascii() or not ANCHOR_RE.match(elem_id):
            non_ascii_ids.append(elem_id)
    if duplicate_ids:
        errors.append(f"Duplicate element IDs found: {duplicate_ids}")
    if non_ascii_ids:
        errors.append(f"Non-ASCII or malformed element IDs found: {non_ascii_ids}")

    unresolved_hrefs = [target for target in inspector.internal_hrefs if target not in seen_ids]
    if unresolved_hrefs:
        errors.append(f"Unresolved internal #anchor hrefs: {unresolved_hrefs}")

    # 7. Sub-budget accounting + oversized scratch island negative fixture
    composition = compute_composition_table(html_text, inspector, policy)
    if composition["status"] != "PASS":
        for seg in composition["failed_segments"]:
            errors.append(
                f"E_BUDGET_EXCEEDED: sub-budget segment '{seg}' exceeded its enforced ceiling"
            )
    oversized_fixture = run_oversized_island_fixture(composition)

    # 8. Cross-check against build-manifest.json if present
    manifest_parity: dict[str, Any] = {"checked": False}
    if manifest_path and manifest_path.is_file():
        manifest = load_json(manifest_path)
        manifest_sha = manifest.get("output_sha256")
        manifest_bytes = manifest.get("output_bytes")
        manifest_composite = manifest.get("composite_digest")
        meta_composite = inspector.metas.get("sim-build-composite-digest")
        parity_ok = (
            manifest_sha == html_sha256
            and manifest_bytes == len(html_bytes)
            and manifest_composite == meta_composite
        )
        if not parity_ok:
            errors.append(
                f"Manifest parity mismatch: html_sha256={html_sha256} vs manifest={manifest_sha}, composite={meta_composite} vs {manifest_composite}"
            )
        manifest_parity = {
            "checked": True,
            "status": "PASS" if parity_ok else "FAIL",
            "artifact_sha256": html_sha256,
            "manifest_output_sha256": manifest_sha,
            "composite_digest": meta_composite,
        }

    # 9. N34 noscript fallback & print-rule static validation
    noscript_check = check_noscript_fallback(html_text)
    if noscript_check["status"] != "PASS":
        errors.extend(noscript_check["errors"])
    print_check = check_print_rules(html_text)
    if print_check["status"] != "PASS":
        errors.extend(print_check["errors"])

    status = "PASS" if not errors else "FAIL"
    return {
        "schema_version": 1,
        "task": "N31",
        "gate": "artifact_contract",
        "status": status,
        "artifact_path": str(html_path.relative_to(DEST) if html_path.is_relative_to(DEST) else html_path),
        "artifact_bytes": len(html_bytes),
        "artifact_kib": round(len(html_bytes) / 1024, 1),
        "artifact_sha256": html_sha256,
        "assertions": {
            "lang": inspector.html_lang,
            "charset": inspector.charset,
            "required_section_1_2_anchor_count": sum(
                1 for a in REQUIRED_SECTION_1_2_ANCHORS if anchor_counts.get(a) == 1
            ),
            "required_section_1_2_anchors": anchor_counts,
            "landmark_sections_count": len(inspector.section_ids),
            "core_section_1_2_island_count": sum(
                1 for i in CORE_SECTION_1_2_ISLANDS if found_island_ids.count(i) == 1
            ),
            "core_section_1_2_islands": CORE_SECTION_1_2_ISLANDS,
            "total_island_count": len(found_island_ids),
            "executable_script_count": len(inspector.executable_scripts),
            "external_script_count": len(inspector.external_scripts),
            "external_stylesheet_count": len(inspector.external_stylesheets),
            "external_url_count": url_scan["external_url_count"],
            "unique_ascii_id_count": len(seen_ids),
            "duplicate_id_count": len(duplicate_ids),
            "unresolved_internal_href_count": len(unresolved_hrefs),
        },
        "script_verification": script_check,
        "offline_url_scan": url_scan,
        "offline_url_scan_fixture": url_fixture,
        "composition_table": composition,
        "oversized_island_fixture": oversized_fixture,
        "manifest_parity": manifest_parity,
        "noscript_check": noscript_check,
        "print_check": print_check,
        "errors": errors,
    }


def format_summary(report: dict[str, Any]) -> str:
    a = report.get("assertions") or {}
    return (
        f"artifact_contract {report['status']}: bytes={report.get('artifact_bytes')} "
        f"({report.get('artifact_kib')} KiB) lang={a.get('lang')} "
        f"anchors={a.get('required_section_1_2_anchor_count')}/9 "
        f"core_islands={a.get('core_section_1_2_island_count')}/7 "
        f"all_islands={a.get('total_island_count')}/22 "
        f"scripts={a.get('executable_script_count')} "
        f"ext_urls={a.get('external_url_count')}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Standalone N31 static artifact contract checker.")
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML, help="Path to output/simulator.html")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to output/build-manifest.json")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY, help="Path to data/build_policy.json")
    parser.add_argument("--report", type=Path, default=None, help="Optional JSON report output path")
    args = parser.parse_args(argv)

    try:
        report = check_artifact(
            html_path=args.html,
            manifest_path=args.manifest,
            policy_path=args.policy,
        )
    except ArtifactContractError as exc:
        report = {
            "schema_version": 1,
            "task": "N31",
            "gate": "artifact_contract",
            "status": "FAIL",
            "errors": [str(exc)],
        }

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(format_summary(report))
    for err in report.get("errors", []):
        print(f"  ERROR: {err}", file=sys.stderr)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
