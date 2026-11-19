#!/usr/bin/env python3
"""N31 Build Gate 27: validate data/build_policy.json, module dependency order,
HTML skeleton insertion points, and deterministic SHA-256 digest stamping.

Implements Subtask A.1 (A.1.1, A.1.2, A.1.3):
  - A.1.1: Module dependency order validation against declared contracts from
           N02–N30, plus the circular-dependency corner-case fixture (ModuleA
           consumes ModuleB, ModuleB consumes ModuleA -> rejected naming both).
  - A.1.2: HTML skeleton template validation (#sim-coverage, #sim-conventions,
           #sim-bank, #sim-forms, #sim-golden-vectors, #sim-terms,
           #sim-analytics and all 22 islands + 37 module placeholders), dry-run
           scratch assembly filling every point once, and duplicate-insertion
           refusal naming the offending insertion point.
  - A.1.3: Deterministic SHA-256 digest stamping over sorted sources, islands,
           and modules + composite digest; two runs over unchanged inputs emit
           identical stamps, while a 1-byte source change flips only the
           expected entries and the composite stamp.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    DEST,
    canonical_json_bytes,
    load_json,
    sha256_bytes,
    sha256_file,
)


class GateError(RuntimeError):
    """Raised when an N31 build policy or template contract check fails."""


@dataclass
class GateResult:
    gate: str
    status: str
    details: dict[str, Any]
    errors: list[str] | None = None

POLICY_PATH = DEST / "data/build_policy.json"
SHELL_PATH = DEST / "src/shell.html"

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


def validate_module_order(
    modules: list[dict[str, Any]],
    *,
    check_files_exist: bool = True,
    root: Path = DEST,
) -> dict[str, Any]:
    """Validate that module_order is contiguous and every consumed interface
    resolves strictly forward to an earlier provider module.

    Raises GateError naming both consumer and provider on any forward-reference
    or circular dependency violation.
    """
    if not isinstance(modules, list) or not modules:
        raise GateError("module_order must be a non-empty list of module contracts")

    # Map symbol -> (provider_order, provider_id, provider_path)
    provider_by_symbol: dict[str, tuple[int, str, str]] = {}
    seen_orders: set[int] = set()
    seen_ids: set[str] = set()
    seen_placeholders: set[str] = set()

    for idx, mod in enumerate(modules, start=1):
        order = mod.get("order")
        mod_id = str(mod.get("id", f"module-{idx}"))
        mod_path = str(mod.get("path", ""))
        placeholder = str(mod.get("placeholder", ""))
        provides = mod.get("provides", [])
        consumes = mod.get("consumes", [])
        citation = str(mod.get("contract_citation", "")).strip()

        if order != idx:
            raise GateError(
                f"module_order entry '{mod_id}' has order={order}, expected contiguous order={idx}"
            )
        if order in seen_orders:
            raise GateError(f"Duplicate module order {order} in module_order")
        seen_orders.add(order)

        if mod_id in seen_ids:
            raise GateError(f"Duplicate module id '{mod_id}' in module_order")
        seen_ids.add(mod_id)

        if not placeholder or placeholder in seen_placeholders:
            raise GateError(
                f"Invalid or duplicate placeholder '{placeholder}' on module '{mod_id}'"
            )
        seen_placeholders.add(placeholder)

        if not isinstance(provides, list) or not provides:
            raise GateError(f"Module '{mod_id}' must declare non-empty provides list")
        if not isinstance(consumes, list):
            raise GateError(f"Module '{mod_id}' consumes must be a list")
        if not citation:
            raise GateError(f"Module '{mod_id}' is missing contract_citation")

        if check_files_exist:
            abs_path = root / mod_path
            if not abs_path.is_file():
                raise GateError(f"Module '{mod_id}' source file does not exist: {mod_path}")

        for sym in provides:
            sym_str = str(sym)
            if sym_str in provider_by_symbol:
                prev_order, prev_id, _ = provider_by_symbol[sym_str]
                raise GateError(
                    f"Duplicate provider for '{sym_str}': provided by both '{prev_id}' (#{prev_order}) and '{mod_id}' (#{order})"
                )
            provider_by_symbol[sym_str] = (order, mod_id, mod_path)

    # Validate forward resolution of all consumed interfaces
    violations: list[dict[str, Any]] = []
    resolved_edges: list[dict[str, Any]] = []

    for mod in modules:
        consumer_order = int(mod["order"])
        consumer_id = str(mod["id"])
        consumer_path = str(mod.get("path", consumer_id))
        for sym in mod.get("consumes", []):
            sym_str = str(sym)
            if sym_str not in provider_by_symbol:
                violations.append(
                    {
                        "kind": "undeclared_provider",
                        "consumer_id": consumer_id,
                        "consumer_order": consumer_order,
                        "symbol": sym_str,
                        "provider_id": None,
                        "provider_order": None,
                    }
                )
                continue
            provider_order, provider_id, provider_path = provider_by_symbol[sym_str]
            if provider_order >= consumer_order:
                violations.append(
                    {
                        "kind": "backward_or_circular_dependency",
                        "consumer_id": consumer_id,
                        "consumer_path": consumer_path,
                        "consumer_order": consumer_order,
                        "symbol": sym_str,
                        "provider_id": provider_id,
                        "provider_path": provider_path,
                        "provider_order": provider_order,
                    }
                )
            else:
                resolved_edges.append(
                    {
                        "consumer_id": consumer_id,
                        "consumer_order": consumer_order,
                        "provider_id": provider_id,
                        "provider_order": provider_order,
                        "symbol": sym_str,
                    }
                )

    if violations:
        named_pairs = []
        for v in violations:
            if v["provider_id"] is None:
                named_pairs.append(
                    f"{v['consumer_id']} (#{v['consumer_order']}) consumes undeclared symbol {v['symbol']}"
                )
            else:
                named_pairs.append(
                    f"{v['consumer_id']} (#{v['consumer_order']}) consumes {v['symbol']} from later module {v['provider_id']} (#{v['provider_order']})"
                )
        raise GateError(
            "E_MODULE_ORDER_VIOLATION: " + "; ".join(named_pairs)
        )

    return {
        "status": "PASS",
        "module_count": len(modules),
        "provided_symbols_count": len(provider_by_symbol),
        "resolved_dependency_edges": len(resolved_edges),
    }


def run_circular_dependency_fixture() -> dict[str, Any]:
    """Subtask A.1.1 corner-case fixture: a scratch pair of modules with a
    circular dependency (ModuleA consumes ModuleB, ModuleB consumes ModuleA)
    must be rejected by validate_module_order with both module names in the
    failure message.
    """
    scratch_circular = [
        {
            "order": 1,
            "id": "ModuleA",
            "path": "scratch/module-a.js",
            "placeholder": "__SCRATCH_A_JS__",
            "owner_task": "N31",
            "provides": ["SimModuleB_TargetA"],
            "consumes": ["SimModuleA_TargetB"],
            "contract_citation": "A.1.1 circular dependency fixture: ModuleA consumes ModuleB.",
        },
        {
            "order": 2,
            "id": "ModuleB",
            "path": "scratch/module-b.js",
            "placeholder": "__SCRATCH_B_JS__",
            "owner_task": "N31",
            "provides": ["SimModuleA_TargetB"],
            "consumes": ["SimModuleB_TargetA"],
            "contract_citation": "A.1.1 circular dependency fixture: ModuleB consumes ModuleA.",
        },
    ]
    rejected = False
    error_message = ""
    try:
        validate_module_order(scratch_circular, check_files_exist=False)
    except GateError as exc:
        rejected = True
        error_message = str(exc)

    both_named = "ModuleA" in error_message and "ModuleB" in error_message
    if not rejected or not both_named:
        raise GateError(
            f"A.1.1 circular dependency fixture did not reject naming both ModuleA and ModuleB: rejected={rejected}, msg={error_message}"
        )

    return {
        "status": "PASS",
        "rejected": rejected,
        "both_modules_named": both_named,
        "named_modules": ["ModuleA", "ModuleB"],
        "error_message": error_message,
    }


def fill_template_strict(
    template_html: str,
    island_replacements: list[tuple[str, str, str]],
    token_replacements: list[tuple[str, str, str]],
) -> dict[str, Any]:
    """Fill every declared island insertion point and template placeholder
    strictly once.

    Raises GateError naming the insertion point if:
      - an insertion point is missing (count == 0),
      - an insertion point appears more than once in the template (count > 1),
      - a caller attempts to insert the same point twice, or
      - any unreplaced __PLACEHOLDER__ token survives after assembly.
    """
    html = template_html
    filled_points: list[str] = []
    seen_points: set[str] = set()

    # 1. Fill island insertion points (<script type="application/json" id="<id>">__PLACEHOLDER__</script>)
    for island_id, placeholder, payload_text in island_replacements:
        point_name = f"#{island_id}"
        if point_name in seen_points:
            raise GateError(
                f"E_TEMPLATE_DUPLICATE_INSERTION: duplicate insertion attempted for {point_name} ({placeholder})"
            )
        seen_points.add(point_name)

        tag_pattern = re.compile(
            r'<script\s+type="application/json"\s+id="' + re.escape(island_id) + r'">[\s\S]*?</script>'
        )
        tag_matches = tag_pattern.findall(html)
        if len(tag_matches) == 0:
            raise GateError(
                f"E_TEMPLATE_MISSING_POINT: island insertion point {point_name} is missing from skeleton template"
            )
        if len(tag_matches) > 1:
            raise GateError(
                f"E_TEMPLATE_DUPLICATE_POINT: island insertion point {point_name} appears {len(tag_matches)} times in skeleton template"
            )

        token_count = html.count(placeholder)
        if token_count == 0:
            raise GateError(
                f"E_TEMPLATE_MISSING_TOKEN: placeholder {placeholder} for {point_name} is missing or already filled"
            )
        if token_count > 1:
            raise GateError(
                f"E_TEMPLATE_DUPLICATE_TOKEN: placeholder {placeholder} for {point_name} appears {token_count} times"
            )

        html = html.replace(placeholder, payload_text, 1)
        filled_points.append(point_name)

    # 2. Fill module, CSS, data projection, and digest meta placeholders
    for point_label, placeholder, payload_text in token_replacements:
        if placeholder in seen_points:
            raise GateError(
                f"E_TEMPLATE_DUPLICATE_INSERTION: duplicate insertion attempted for {point_label} ({placeholder})"
            )
        seen_points.add(placeholder)

        token_count = html.count(placeholder)
        if token_count == 0:
            raise GateError(
                f"E_TEMPLATE_MISSING_TOKEN: placeholder {placeholder} for {point_label} is missing or already filled"
            )
        if token_count > 1:
            raise GateError(
                f"E_TEMPLATE_DUPLICATE_TOKEN: placeholder {placeholder} for {point_label} appears {token_count} times"
            )
        html = html.replace(placeholder, payload_text, 1)
        filled_points.append(point_label)

    leftover = sorted(set(re.findall(r"__[A-Z0-9_]+__", html)))
    if leftover:
        raise GateError(
            f"E_TEMPLATE_UNFILLED_PLACEHOLDERS: unreplaced placeholders survived assembly: {', '.join(leftover)}"
        )

    return {
        "status": "PASS",
        "html": html,
        "filled_count": len(filled_points),
        "filled_points": filled_points,
    }


def validate_skeleton_template(policy: dict[str, Any], template_html: str) -> dict[str, Any]:
    """Subtask A.1.2: validate src/shell.html insertion points, anchor order,
    island order, and run the dry-run scratch assembly + duplicate-insertion
    failure fixture.
    """
    if '<html lang="lv">' not in template_html:
        raise GateError('src/shell.html is missing <html lang="lv">')

    # Verify the 9 required Section 1.2 anchors + auxiliary anchors
    for anchor in REQUIRED_SECTION_1_2_ANCHORS:
        pattern = re.compile(rf'<section\s+id="{re.escape(anchor)}"(?=\s|>)')
        matches = pattern.findall(template_html)
        if len(matches) != 1:
            raise GateError(
                f"Blueprint anchor #{anchor} must appear exactly once as <section id=\"{anchor}\">, found {len(matches)}"
            )

    # Verify the 7 core Section 1.2 islands are declared and present in order
    declared_islands = policy["islands"]["insertion_order"]
    declared_ids = [entry["island_id"] for entry in declared_islands]
    if declared_ids[:7] != CORE_SECTION_1_2_ISLANDS:
        raise GateError(
            f"First 7 islands in build_policy.json must be {CORE_SECTION_1_2_ISLANDS}, got {declared_ids[:7]}"
        )

    found_islands = re.findall(
        r'<script\s+type="application/json"\s+id="([^"]+)">([^<]*)</script>',
        template_html,
    )
    found_ids = [item[0] for item in found_islands]
    if found_ids != declared_ids:
        raise GateError(
            f"Template island order mismatch: template has {found_ids}, policy declares {declared_ids}"
        )

    # Build a scratch dry-run replacement set covering every placeholder in src/shell.html
    scratch_islands: list[tuple[str, str, str]] = []
    scratch_tokens: list[tuple[str, str, str]] = [
        ("meta:sim-build", "__BUILD_ID__", "0000000000000000"),
        ("meta:sim-build-version", "__BUILD_VERSION__", str(policy["version"])),
        ("meta:sim-build-date", "__BUILD_ISO_DATE__", str(policy["iso_date"])),
        ("meta:sim-build-composite-digest", "__COMPOSITE_DIGEST__", "0" * 64),
        ("meta:sim-bank-digest", "__BANK_DIGEST__", "0" * 64),
        ("meta:sim-tokens-digest", "__TOKENS_DIGEST__", "0" * 64),
        ("meta:sim-concept-summaries-digest", "__CONCEPT_SUMMARIES_DIGEST__", "0" * 64),
        ("meta:sim-anchor-registry-digest", "__ANCHOR_REGISTRY_DIGEST__", "0" * 64),
        ("meta:sim-recall-layers-digest", "__RECALL_LAYERS_DIGEST__", "0" * 64),
        ("meta:sim-reading-contract-digest", "__READING_CONTRACT_DIGEST__", "0" * 64),
        ("meta:sim-energy-contract-digest", "__ENERGY_CONTRACT_DIGEST__", "0" * 64),
        ("meta:sim-kinetics-contract-digest", "__KINETICS_CONTRACT_DIGEST__", "0" * 64),
        ("css:tokens", "__TOKENS_CSS__", ":root{--sim-dry-run:1;}"),
        ("css:styles", "__STYLES_CSS__", "body{margin:0;}"),
        ("html:noscript", "__SIM_NOSCRIPT_HTML__", "<noscript></noscript>"),
    ]

    for entry in declared_islands:
        iid = entry["island_id"]
        scratch_payload = json.dumps(
            {"island_id": iid, "dry_run": True},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        scratch_islands.append((iid, entry["placeholder"], scratch_payload))
        scratch_tokens.append(
            (f"meta:{entry['digest_meta_name']}", entry["digest_placeholder"], "0" * 64)
        )

    for proj in policy["data_projection_globals"]:
        scratch_tokens.append(
            (f"data:{proj['global_name']}", proj["placeholder"], '{"dry_run":true}')
        )

    for mod in policy["module_order"]:
        sep = f"/* === MODULE: {mod['path']} === */"
        scratch_tokens.append(
            (f"module:{mod['id']}", mod["placeholder"], f"{sep}\nvoid 0;")
        )

    dry_run = fill_template_strict(template_html, scratch_islands, scratch_tokens)

    # Corner-case 1: duplicate insertion call for #sim-bank fails naming #sim-bank
    dup_call_rejected = False
    dup_call_msg = ""
    try:
        fill_template_strict(
            template_html,
            scratch_islands + [("sim-bank", "__SIM_BANK_JSON__", "{}")],
            scratch_tokens,
        )
    except GateError as exc:
        dup_call_rejected = True
        dup_call_msg = str(exc)

    if not dup_call_rejected or "#sim-bank" not in dup_call_msg:
        raise GateError(
            f"A.1.2 duplicate insertion call fixture did not fail naming #sim-bank: rejected={dup_call_rejected}, msg={dup_call_msg}"
        )

    # Corner-case 2: duplicate #sim-coverage tag in template fails naming #sim-coverage
    dup_template_rejected = False
    dup_template_msg = ""
    corrupted_template = template_html + '\n<script type="application/json" id="sim-coverage">__SIM_COVERAGE_JSON__</script>'
    try:
        fill_template_strict(corrupted_template, scratch_islands, scratch_tokens)
    except GateError as exc:
        dup_template_rejected = True
        dup_template_msg = str(exc)

    if not dup_template_rejected or "#sim-coverage" not in dup_template_msg:
        raise GateError(
            f"A.1.2 duplicate template point fixture did not fail naming #sim-coverage: rejected={dup_template_rejected}, msg={dup_template_msg}"
        )

    return {
        "status": "PASS",
        "core_islands_verified": CORE_SECTION_1_2_ISLANDS,
        "total_islands_verified": len(declared_islands),
        "total_modules_verified": len(policy["module_order"]),
        "dry_run_filled_points_count": dry_run["filled_count"],
        "duplicate_call_fixture": {
            "status": "PASS",
            "rejected": dup_call_rejected,
            "named_point": "#sim-bank",
            "error_message": dup_call_msg,
        },
        "duplicate_template_point_fixture": {
            "status": "PASS",
            "rejected": dup_template_rejected,
            "named_point": "#sim-coverage",
            "error_message": dup_template_msg,
        },
    }


def compute_build_stamp(
    *,
    version: str,
    iso_date: str,
    policy_id: str,
    sources: list[dict[str, Any]],
    islands: list[dict[str, Any]],
    modules: list[dict[str, Any]],
) -> dict[str, Any]:
    """Subtask A.1.3: compute deterministic sorted source digests and the
    composite manifest digest.
    """
    sorted_sources = sorted(
        (
            {
                "path": str(entry["path"]),
                "bytes": int(entry["bytes"]),
                "sha256": str(entry["sha256"]),
            }
            for entry in sources
        ),
        key=lambda item: item["path"],
    )
    sorted_islands = sorted(
        (
            {
                "island_id": str(entry["island_id"]),
                "bytes": int(entry["bytes"]),
                "sha256": str(entry["sha256"]),
            }
            for entry in islands
        ),
        key=lambda item: item["island_id"],
    )
    ordered_modules = sorted(
        (
            {
                "order": int(entry["order"]),
                "path": str(entry["path"]),
                "raw_sha256": str(entry["raw_sha256"]),
                "inlined_sha256": str(entry["inlined_sha256"]),
            }
            for entry in modules
        ),
        key=lambda item: item["order"],
    )
    stamp_payload = {
        "version": version,
        "iso_date": iso_date,
        "policy_id": policy_id,
        "sources": sorted_sources,
        "islands": sorted_islands,
        "modules": ordered_modules,
    }
    composite_digest = sha256_bytes(canonical_json_bytes(stamp_payload))
    build_id = composite_digest[:16]
    return {
        "version": version,
        "iso_date": iso_date,
        "policy_id": policy_id,
        "build_id": build_id,
        "composite_digest": composite_digest,
        "sources_count": len(sorted_sources),
        "islands_count": len(sorted_islands),
        "modules_count": len(ordered_modules),
        "sources": sorted_sources,
        "islands": sorted_islands,
        "modules": ordered_modules,
    }


def run_stamp_fixture(policy: dict[str, Any], root: Path = DEST) -> dict[str, Any]:
    """Subtask A.1.3 stamp fixture:
      1. Two runs over unchanged inputs emit identical manifests and an
         identical composite stamp.
      2. A one-byte source change in a module flips only that module's source
         entry, its module entry, and the composite digest.
      3. A one-byte source change in an island flips only that island's source
         entry, its island entry, and the composite digest.
    """
    sources: list[dict[str, Any]] = []
    seen_paths: set[str] = set()

    def add_source(rel_path: str) -> None:
        if rel_path in seen_paths:
            return
        p = root / rel_path
        if p.is_file():
            seen_paths.add(rel_path)
            sources.append(
                {
                    "path": rel_path,
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )

    add_source("data/build_policy.json")
    add_source("src/shell.html")
    for entry in policy["islands"]["insertion_order"]:
        for sp in entry["source_paths"]:
            p = root / sp
            if p.is_dir():
                for child in sorted(p.glob("*.json")):
                    add_source(str(child.relative_to(root)))
            else:
                add_source(sp)

    modules: list[dict[str, Any]] = []
    for mod in policy["module_order"]:
        rel = mod["path"]
        add_source(rel)
        raw_bytes = (root / rel).read_bytes()
        digest = sha256_bytes(raw_bytes)
        modules.append(
            {
                "order": mod["order"],
                "path": rel,
                "raw_sha256": digest,
                "inlined_sha256": digest,
            }
        )

    islands: list[dict[str, Any]] = []
    for entry in policy["islands"]["insertion_order"]:
        iid = entry["island_id"]
        first_src = entry["source_paths"][0]
        p = root / first_src
        raw = p.read_bytes() if p.is_file() else canonical_json_bytes({"island_id": iid})
        islands.append(
            {
                "island_id": iid,
                "bytes": len(raw),
                "sha256": sha256_bytes(raw),
            }
        )

    stamp_run_1 = compute_build_stamp(
        version=policy["version"],
        iso_date=policy["iso_date"],
        policy_id=policy["policy_id"],
        sources=sources,
        islands=islands,
        modules=modules,
    )
    # Run 2 with reversed input lists to prove order-independence
    stamp_run_2 = compute_build_stamp(
        version=policy["version"],
        iso_date=policy["iso_date"],
        policy_id=policy["policy_id"],
        sources=list(reversed(copy.deepcopy(sources))),
        islands=list(reversed(copy.deepcopy(islands))),
        modules=list(reversed(copy.deepcopy(modules))),
    )

    bytes_run_1 = canonical_json_bytes(stamp_run_1)
    bytes_run_2 = canonical_json_bytes(stamp_run_2)
    if bytes_run_1 != bytes_run_2 or stamp_run_1["composite_digest"] != stamp_run_2["composite_digest"]:
        raise GateError("A.1.3 stamp fixture failed: two runs over unchanged inputs differed")

    # One-byte mutation in a module source (src/quantity-engine.js)
    target_mod_path = "src/quantity-engine.js"
    orig_mod_bytes = (root / target_mod_path).read_bytes()
    mutated_mod_bytes = orig_mod_bytes + b"\n"
    mutated_mod_sha = sha256_bytes(mutated_mod_bytes)

    mut_sources = copy.deepcopy(sources)
    for entry in mut_sources:
        if entry["path"] == target_mod_path:
            entry["bytes"] = len(mutated_mod_bytes)
            entry["sha256"] = mutated_mod_sha

    mut_modules = copy.deepcopy(modules)
    for entry in mut_modules:
        if entry["path"] == target_mod_path:
            entry["raw_sha256"] = mutated_mod_sha
            entry["inlined_sha256"] = mutated_mod_sha

    stamp_mod_mutated = compute_build_stamp(
        version=policy["version"],
        iso_date=policy["iso_date"],
        policy_id=policy["policy_id"],
        sources=mut_sources,
        islands=islands,
        modules=mut_modules,
    )

    flipped_sources = [
        s1["path"]
        for s1, s2 in zip(stamp_run_1["sources"], stamp_mod_mutated["sources"])
        if s1["sha256"] != s2["sha256"]
    ]
    flipped_modules = [
        m1["path"]
        for m1, m2 in zip(stamp_run_1["modules"], stamp_mod_mutated["modules"])
        if m1["raw_sha256"] != m2["raw_sha256"]
    ]
    flipped_islands = [
        i1["island_id"]
        for i1, i2 in zip(stamp_run_1["islands"], stamp_mod_mutated["islands"])
        if i1["sha256"] != i2["sha256"]
    ]

    if (
        flipped_sources != [target_mod_path]
        or flipped_modules != [target_mod_path]
        or flipped_islands != []
        or stamp_mod_mutated["composite_digest"] == stamp_run_1["composite_digest"]
    ):
        raise GateError(
            f"A.1.3 one-byte module mutation flipped unexpected entries: sources={flipped_sources}, modules={flipped_modules}, islands={flipped_islands}"
        )

    # One-byte mutation in an island source (data/terms.json -> #sim-terms)
    target_island_src = "data/terms.json"
    target_island_id = "sim-terms"
    orig_island_bytes = (root / target_island_src).read_bytes()
    mutated_island_bytes = orig_island_bytes + b" "
    mutated_island_sha = sha256_bytes(mutated_island_bytes)

    mut_sources_2 = copy.deepcopy(sources)
    for entry in mut_sources_2:
        if entry["path"] == target_island_src:
            entry["bytes"] = len(mutated_island_bytes)
            entry["sha256"] = mutated_island_sha

    mut_islands_2 = copy.deepcopy(islands)
    for entry in mut_islands_2:
        if entry["island_id"] == target_island_id:
            entry["bytes"] = len(mutated_island_bytes)
            entry["sha256"] = mutated_island_sha

    stamp_island_mutated = compute_build_stamp(
        version=policy["version"],
        iso_date=policy["iso_date"],
        policy_id=policy["policy_id"],
        sources=mut_sources_2,
        islands=mut_islands_2,
        modules=modules,
    )
    flipped_sources_2 = [
        s1["path"]
        for s1, s2 in zip(stamp_run_1["sources"], stamp_island_mutated["sources"])
        if s1["sha256"] != s2["sha256"]
    ]
    flipped_islands_2 = [
        i1["island_id"]
        for i1, i2 in zip(stamp_run_1["islands"], stamp_island_mutated["islands"])
        if i1["sha256"] != i2["sha256"]
    ]
    if (
        flipped_sources_2 != [target_island_src]
        or flipped_islands_2 != [target_island_id]
        or stamp_island_mutated["composite_digest"] == stamp_run_1["composite_digest"]
    ):
        raise GateError(
            f"A.1.3 one-byte island mutation flipped unexpected entries: sources={flipped_sources_2}, islands={flipped_islands_2}"
        )

    return {
        "status": "PASS",
        "unchanged_runs_identical": True,
        "composite_digest_run_1": stamp_run_1["composite_digest"],
        "composite_digest_run_2": stamp_run_2["composite_digest"],
        "one_byte_module_mutation": {
            "mutated_path": target_mod_path,
            "flipped_sources": flipped_sources,
            "flipped_modules": flipped_modules,
            "flipped_islands": flipped_islands,
            "mutated_composite_digest": stamp_mod_mutated["composite_digest"],
        },
        "one_byte_island_mutation": {
            "mutated_path": target_island_src,
            "flipped_sources": flipped_sources_2,
            "flipped_islands": flipped_islands_2,
            "mutated_composite_digest": stamp_island_mutated["composite_digest"],
        },
    }


def validate_build_policy(
    policy_path: Path = POLICY_PATH,
    shell_path: Path = SHELL_PATH,
    root: Path = DEST,
) -> GateResult:
    """Build Gate 27 entry point."""
    if not policy_path.is_file():
        raise GateError(f"Missing build policy artifact: {policy_path}")
    if not shell_path.is_file():
        raise GateError(f"Missing HTML skeleton template: {shell_path}")

    policy = load_json(policy_path)
    if policy.get("policy_id") != "n31-single-file-build-policy-v1":
        raise GateError(f"Unexpected policy_id: {policy.get('policy_id')}")
    if policy.get("owner_task") != "N31":
        raise GateError(f"Unexpected owner_task: {policy.get('owner_task')}")

    order_check = validate_module_order(policy.get("module_order", []), check_files_exist=True, root=root)
    circular_fixture = run_circular_dependency_fixture()
    template_html = shell_path.read_text(encoding="utf-8")
    template_check = validate_skeleton_template(policy, template_html)
    stamp_fixture = run_stamp_fixture(policy, root=root)

    return GateResult(
        gate="build_policy",
        status="PASS",
        details={
            "policy_id": policy["policy_id"],
            "version": policy["version"],
            "iso_date": policy["iso_date"],
            "policy_sha256": sha256_file(policy_path),
            "module_order_validation": order_check,
            "circular_dependency_fixture": circular_fixture,
            "template_validation": template_check,
            "stamp_fixture": stamp_fixture,
        },
    )


def validate_all(repo_root: Path = DEST) -> dict[str, Any]:
    """Run all N31 build policy checks and return a structured report."""
    policy_path = repo_root / "data/build_policy.json"
    shell_path = repo_root / "src/shell.html"
    try:
        res = validate_build_policy(policy_path=policy_path, shell_path=shell_path, root=repo_root)
        return {
            "schema_version": 1,
            "task": "N31",
            "gate": res.gate,
            "status": res.status,
            "details": res.details,
            "errors": [],
        }
    except GateError as exc:
        return {
            "schema_version": 1,
            "task": "N31",
            "gate": "build_policy",
            "status": "FAIL",
            "details": {},
            "errors": [str(exc)],
        }


def format_summary(report: dict[str, Any]) -> str:
    details = report.get("details") or {}
    mod_val = details.get("module_order_validation") or {}
    tmpl_val = details.get("template_validation") or {}
    return (
        f"build_policy {report['status']}: policy={details.get('policy_id')} "
        f"modules={mod_val.get('module_count')} edges={mod_val.get('resolved_dependency_edges')} "
        f"islands={tmpl_val.get('total_islands_verified')} "
        f"filled={tmpl_val.get('dry_run_filled_points_count')}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate N31 build policy (Gate 27).")
    parser.add_argument("--repo-root", type=Path, default=DEST, help="Repository root path.")
    parser.add_argument("--report", type=Path, default=None, help="Optional path to write JSON report.")
    args = parser.parse_args()

    payload = validate_all(repo_root=args.repo_root)
    if args.report:
        out = args.report if args.report.is_absolute() else args.repo_root / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(format_summary(payload))
    for err in payload.get("errors", []):
        print(f"  ERROR: {err}", file=sys.stderr)
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
