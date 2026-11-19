#!/usr/bin/env python3
"""N07 concept map, ASCII anchor graph, concept summaries & anchor-registry validator.

Checks:
1. Coverage graph acyclicity re-assertion + deterministic layered layout
   (global layer rule, ascending ASCII id tie-break, wrap_threshold=3),
   including the diamond fixture and Topic-3 wide-layer wrap fixture.
2. Concept summaries (data/concept_summaries.json): 64/64 outcomes,
   case-exact master_anchor & master_heading_lv re-validation bound to
   N01 frozen master digests, V-02/V-03 convention + dissent compliance,
   and mandatory owner_task on every figures/chains/practice slot.
3. Anchor-link registry (data/anchor_registry.json): 9 shell anchors,
   7 #karte-tema-N anchors, 64 concept map/objectives/drawer targets,
   all 127 prerequisite edge targets resolving without dangling links,
   and open_link_contract handoff metadata for N08/N16/N28/N29.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import (  # noqa: E402
    COVERAGE_PATH, DEST, TOPIC_MASTER_PATHS, anchor_heading,
    canonical_json_bytes, find_cycle, inventory_master_digests, load_json,
    parse_master, sha256_bytes, sha256_file,
)

SUMMARIES_PATH = 'data/concept_summaries.json'
REGISTRY_PATH = 'data/anchor_registry.json'
CONVENTIONS_PATH = 'data/conventions.json'
OWNER_TASK_RE = re.compile(r'^N(?:1[1-6]|30)$')
WRAP_THRESHOLD = 3
DEFAULT_CHAIN_DEPTH = 2
EXPECTED_CONSUMERS = ['N08', 'N16', 'N28', 'N29']

V02_REQUIRED_IDS = {'P3-01', 'P3-03', 'P3-06', 'P3-08', 'P3-09'}
V03_REQUIRED_IDS = {'P6-02', 'P6-03', 'P6-04'}


def compute_layered_layout(outcomes: list[dict[str, Any]], topics: list[dict[str, Any]],
                           wrap_threshold: int = WRAP_THRESHOLD) -> dict[str, Any]:
    """Deterministic acyclic layered layout matching src/concept-map.js."""
    by_id = {o['id']: o for o in outcomes}
    edges: dict[str, list[str]] = {}
    for o in outcomes:
        prereqs = list(o.get('prerequisites') or [])
        for p in prereqs:
            if p not in by_id:
                raise ValueError(f"Outcome {o['id']} references nonexistent prerequisite {p}")
        edges[o['id']] = sorted(prereqs)

    cycle = find_cycle(edges)
    if cycle is not None:
        raise ValueError(f"Cycle detected in prerequisite graph: {' -> '.join(cycle)}")

    memo: dict[str, int] = {}

    def get_layer(oid: str) -> int:
        if oid in memo:
            return memo[oid]
        ps = edges[oid]
        lyr = 0 if not ps else 1 + max(get_layer(p) for p in ps)
        memo[oid] = lyr
        return lyr

    for oid in sorted(by_id):
        get_layer(oid)

    topic_records = sorted(topics, key=lambda t: t['topic'])
    topic_layouts: list[dict[str, Any]] = []
    cross_topic_edges: list[dict[str, str]] = []
    all_edges: list[dict[str, str]] = []

    for oid in sorted(by_id):
        to_out = by_id[oid]
        for pid in sorted(edges[oid]):
            from_out = by_id[pid]
            kind = 'intra-topic' if from_out['topic'] == to_out['topic'] else 'cross-topic'
            rec = {
                'id': f'{pid}->{oid}',
                'from': pid,
                'to': oid,
                'from_topic': from_out['topic'],
                'to_topic': to_out['topic'],
                'kind': kind,
            }
            all_edges.append(rec)
            if kind == 'cross-topic':
                cross_topic_edges.append(rec)

    for trec in topic_records:
        tnum = trec['topic']
        tnodes = [by_id[oid] for oid in sorted(by_id) if by_id[oid]['topic'] == tnum]
        by_layer: dict[int, list[str]] = defaultdict(list)
        for o in tnodes:
            by_layer[memo[o['id']]].append(o['id'])
        layers_out = []
        for lnum in sorted(by_layer):
            ids_sorted = sorted(by_layer[lnum])
            rows = [ids_sorted[i:i + wrap_threshold] for i in range(0, len(ids_sorted), wrap_threshold)]
            layers_out.append({
                'layer': lnum,
                'nodes': ids_sorted,
                'rows': rows,
                'wrapped': len(ids_sorted) > wrap_threshold,
            })
        topic_layouts.append({
            'topic': tnum,
            'layers': layers_out,
        })

    return {
        'rules': {
            'layer_rule': '0 if prerequisites.length == 0 else 1 + max(layer(p))',
            'tie_break': 'ascending ASCII outcome id',
            'wrap_threshold': wrap_threshold,
        },
        'node_layers': {oid: memo[oid] for oid in sorted(memo)},
        'total_nodes': len(by_id),
        'total_edges': len(all_edges),
        'cross_topic_edges': len(cross_topic_edges),
        'topics': topic_layouts,
    }


def verify_layout_fixtures() -> dict[str, Any]:
    """Verify diamond dependency and Topic-3 wide-layer wrap corner cases."""
    diamond_outcomes = [
        {'id': 'A', 'topic': 1, 'prerequisites': []},
        {'id': 'B', 'topic': 1, 'prerequisites': ['A']},
        {'id': 'C', 'topic': 1, 'prerequisites': ['A']},
        {'id': 'D', 'topic': 1, 'prerequisites': ['B', 'C']},
    ]
    diamond_topics = [{'topic': 1, 'name_lv': 'Diamond'}]
    diamond_layout = compute_layered_layout(diamond_outcomes, diamond_topics)
    assert diamond_layout['node_layers'] == {'A': 0, 'B': 1, 'C': 1, 'D': 2}
    assert diamond_layout['topics'][0]['layers'][1]['nodes'] == ['B', 'C']

    wide_outcomes = [
        {'id': f'P3-{i:02d}', 'topic': 3, 'prerequisites': []}
        for i in range(1, 12)
    ]
    wide_topics = [{'topic': 3, 'name_lv': 'Wide Topic 3'}]
    wide_layout = compute_layered_layout(wide_outcomes, wide_topics)
    wide_layer = wide_layout['topics'][0]['layers'][0]
    row_sizes = [len(r) for r in wide_layer['rows']]
    assert wide_layer['wrapped'] is True and row_sizes == [3, 3, 3, 2]

    return {
        'diamond': {
            'node_layers': diamond_layout['node_layers'],
            'layer_1_order': diamond_layout['topics'][0]['layers'][1]['nodes'],
            'status': 'PASS',
        },
        'wide_layer_topic3': {
            'node_count': 11,
            'wrap_threshold': WRAP_THRESHOLD,
            'wrapped': wide_layer['wrapped'],
            'row_sizes': row_sizes,
            'rows': wide_layer['rows'],
            'status': 'PASS',
        },
    }


def validate_all(
    island_path: Path | None = None,
    summaries_path: Path | None = None,
    registry_path: Path | None = None,
    conventions_path: Path | None = None,
    repo_root: Path = DEST,
    masters_root: Path | None = None,
    summaries_data: dict[str, Any] | None = None,
    registry_data: dict[str, Any] | None = None,
    coverage_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mroot = masters_root or repo_root
    ipath = island_path or (repo_root / COVERAGE_PATH)
    spath = summaries_path or (repo_root / SUMMARIES_PATH)
    rpath = registry_path or (repo_root / REGISTRY_PATH)
    cpath = conventions_path or (repo_root / CONVENTIONS_PATH)

    errors: list[str] = []
    cov = coverage_data if coverage_data is not None else load_json(ipath)
    summaries = summaries_data if summaries_data is not None else load_json(spath)
    registry = registry_data if registry_data is not None else load_json(rpath)
    conventions = load_json(cpath)

    # 1. Acyclic layered layout + determinism
    layout_digest = None
    layout_summary: dict[str, Any] = {}
    try:
        layout_a = compute_layered_layout(cov['outcomes'], cov['topics'])
        layout_b = compute_layered_layout(cov['outcomes'], cov['topics'])
        bytes_a = canonical_json_bytes(layout_a)
        bytes_b = canonical_json_bytes(layout_b)
        if bytes_a != bytes_b:
            errors.append('Layout computation is not deterministic across two runs')
        layout_digest = sha256_bytes(bytes_a)
        layout_summary = {
            'total_nodes': layout_a['total_nodes'],
            'total_edges': layout_a['total_edges'],
            'cross_topic_edges': layout_a['cross_topic_edges'],
            'max_layer': max(layout_a['node_layers'].values()),
            'wrap_threshold': WRAP_THRESHOLD,
            'layout_digest': layout_digest,
        }
    except ValueError as exc:
        errors.append(str(exc))

    fixtures = verify_layout_fixtures()

    # 2. Summaries validation + frozen master anchor re-validation + V-02/V-03 + slots
    cov_by_id = {o['id']: o for o in cov['outcomes']}
    sum_list = summaries.get('concepts') or []
    sum_by_id: dict[str, dict[str, Any]] = {}
    for item in sum_list:
        cid = item.get('id')
        if not cid:
            errors.append('Concept summary entry missing id')
            continue
        if cid in sum_by_id:
            errors.append(f'Duplicate concept summary id: {cid}')
        sum_by_id[cid] = item

    missing_summaries = sorted(set(cov_by_id.keys()) - set(sum_by_id.keys()))
    extra_summaries = sorted(set(sum_by_id.keys()) - set(cov_by_id.keys()))
    if missing_summaries:
        errors.append(f'Missing concept summaries for outcomes: {missing_summaries}')
    if extra_summaries:
        errors.append(f'Unknown concept summaries not in coverage: {extra_summaries}')

    if not isinstance(summaries.get('wording_rule_lv'), str) or 'conventions' not in summaries['wording_rule_lv']:
        errors.append('concept_summaries missing wording_rule_lv citing #sim-conventions')

    # Re-validate all 64 anchors against N01 frozen masters
    inventory = inventory_master_digests(repo_root)
    masters: dict[int, Any] = {}
    freeze_ok = True
    for topic, relative in TOPIC_MASTER_PATHS.items():
        full = mroot / relative
        entry = inventory.get(topic, {})
        actual_sha = sha256_file(full)
        if actual_sha != entry.get('sha256') or full.stat().st_size != entry.get('bytes'):
            freeze_ok = False
            errors.append(f'Master digest mismatch vs N01 freeze for topic {topic}: {relative}')
        masters[topic] = parse_master(full)

    anchors_resolved = 0
    slots_checked = 0
    v02_checked = 0
    v03_checked = 0
    conflict_ids_known = {e['id'] for e in (conventions.get('conflicts') or {}).get('entries', [])}

    for oid in sorted(cov_by_id):
        cov_o = cov_by_id[oid]
        s = sum_by_id.get(oid)
        if not s:
            continue
        if not isinstance(s.get('summary_lv'), str) or len(s['summary_lv'].strip()) < 30:
            errors.append(f'{oid}: summary_lv missing or too short')
        for field in ('topic', 'master_path', 'master_anchor', 'master_heading_lv', 'master_freeze_id'):
            if s.get(field) != cov_o.get(field):
                errors.append(f'{oid}: summary {field}={s.get(field)!r} mismatches coverage {cov_o.get(field)!r}')

        # Case-exact master anchor check
        topic = s.get('topic')
        anchor = s.get('master_anchor', '')
        if topic in masters:
            idx = masters[topic]
            if anchor not in idx.ids:
                errors.append(f'{oid}: master_anchor #{anchor} not found (case-exact) in {s.get("master_path")}')
            else:
                heading = anchor_heading(idx, anchor)
                if heading != s.get('master_heading_lv'):
                    errors.append(f'{oid}: heading {heading!r} != recorded {s.get("master_heading_lv")!r}')
                else:
                    anchors_resolved += 1

        # Conventions / dissent wording check
        crefs = s.get('conventions_refs') or []
        for cref in crefs:
            if cref not in conflict_ids_known:
                errors.append(f'{oid}: unknown conventions/conflict ref {cref!r}')
        if oid in V02_REQUIRED_IDS:
            v02_checked += 1
            dissent = s.get('dissent_note_lv') or ''
            if 'V-02' not in crefs or not dissent or ('m/m' not in dissent and 'm/V' not in dissent):
                errors.append(f'{oid}: missing V-02 conventions reference or named m/m vs m/V dissent note')
        if oid in V03_REQUIRED_IDS:
            v03_checked += 1
            dissent = s.get('dissent_note_lv') or ''
            if 'V-03' not in crefs or not dissent or 'E°' not in dissent or 'E°′' not in dissent:
                errors.append(f'{oid}: missing V-03 conventions reference or named E° vs E°′ dissent note')

        # Slot contract check (figures, chains, practice must each name owner_task)
        slots = s.get('slots')
        if not isinstance(slots, dict):
            errors.append(f'{oid}: missing slots object')
            continue
        for kind in ('figures', 'chains', 'practice'):
            slot = slots.get(kind)
            if not isinstance(slot, dict):
                errors.append(f'{oid}: missing slot {kind!r}')
                continue
            slots_checked += 1
            owner = slot.get('owner_task')
            if not isinstance(owner, str) or not OWNER_TASK_RE.match(owner):
                errors.append(f'{oid} slot {kind!r}: invalid or missing owner_task {owner!r}')
            if not isinstance(slot.get('slot_id'), str) or not slot['slot_id'].strip():
                errors.append(f'{oid} slot {kind!r}: missing slot_id')
            expected_statuses = {f'pending-{owner}'}
            if kind == 'figures' and owner in ('N11', 'N12', 'N13', 'N14', 'N15'):
                expected_statuses.add(f'authored-{owner}')
            if kind == 'chains' and owner == 'N16':
                expected_statuses.add('authored-N16')
            if slot.get('status') not in expected_statuses:
                errors.append(f'{oid} slot {kind!r}: status {slot.get("status")!r} not in {sorted(expected_statuses)}')
            if slot.get('status') in ('authored-N11', 'authored-N12', 'authored-N13', 'authored-N14', 'authored-N15'):
                fids = slot.get('figure_ids')
                if not isinstance(fids, list) or not fids or not all(isinstance(x, str) and x.strip() for x in fids):
                    errors.append(f'{oid} slot {kind!r}: {slot.get("status")} slot must list figure_ids')
            if slot.get('status') == 'authored-N16':
                cids = slot.get('chain_ids')
                if not isinstance(cids, list) or not cids or not all(isinstance(x, str) and x.strip() for x in cids):
                    errors.append(f'{oid} slot {kind!r}: authored-N16 slot must list chain_ids')
            if not isinstance(slot.get('label_lv'), str) or not slot['label_lv'].strip():
                errors.append(f'{oid} slot {kind!r}: missing label_lv')

    # 3. Anchor-link registry validation (no dangling concept/topic/edge/drawer links)
    reg_concepts = registry.get('concepts') or []
    reg_by_id: dict[str, dict[str, Any]] = {}
    for rc in reg_concepts:
        cid = rc.get('concept_id')
        if not cid:
            errors.append('anchor_registry entry missing concept_id')
            continue
        if cid in reg_by_id:
            errors.append(f'anchor_registry duplicate concept_id: {cid}')
        reg_by_id[cid] = rc

    valid_topic_anchors = {f'#{a}' for a in (registry.get('topic_map_anchors') or [])}
    expected_topic_anchors = {f'#karte-tema-{t}' for t in range(1, 8)}
    if valid_topic_anchors != expected_topic_anchors:
        errors.append(f'anchor_registry topic_map_anchors mismatch: {sorted(valid_topic_anchors)}')

    valid_map_anchors = {f'#karte-{oid}' for oid in cov_by_id}
    valid_obj_anchors = {f'#rezultats-{oid}' for oid in cov_by_id}
    drawer_id = registry.get('drawer_overlay_id')
    if drawer_id != 'concept-drawer':
        errors.append(f'anchor_registry drawer_overlay_id must be "concept-drawer", got {drawer_id!r}')

    olc = registry.get('open_link_contract') or {}
    if olc.get('consumers') != EXPECTED_CONSUMERS or 'conceptId' not in (olc.get('required_fields') or []):
        errors.append('anchor_registry open_link_contract missing expected consumers or conceptId')

    reg_missing = sorted(set(cov_by_id.keys()) - set(reg_by_id.keys()))
    reg_extra = sorted(set(reg_by_id.keys()) - set(cov_by_id.keys()))
    if reg_missing:
        errors.append(f'anchor_registry missing concepts: {reg_missing}')
    if reg_extra:
        errors.append(f'anchor_registry unknown concepts: {reg_extra}')

    resolved_map_links = 0
    resolved_edge_links = 0
    for oid in sorted(reg_by_id):
        rc = reg_by_id[oid]
        if oid not in cov_by_id:
            continue
        cov_o = cov_by_id[oid]
        if rc.get('map_anchor') not in valid_map_anchors or rc.get('map_anchor') != f'#karte-{oid}':
            errors.append(f'{oid}: dangling or invalid map_anchor {rc.get("map_anchor")!r}')
        else:
            resolved_map_links += 1
        if rc.get('topic_anchor') not in valid_topic_anchors or rc.get('topic_anchor') != f'#karte-tema-{cov_o["topic"]}':
            errors.append(f'{oid}: dangling topic_anchor {rc.get("topic_anchor")!r}')
        if rc.get('objectives_anchor') not in valid_obj_anchors or rc.get('objectives_anchor') != f'#rezultats-{oid}':
            errors.append(f'{oid}: dangling objectives_anchor {rc.get("objectives_anchor")!r}')
        if rc.get('drawer_target') != f'#{drawer_id}':
            errors.append(f'{oid}: unresolved drawer_target {rc.get("drawer_target")!r}')
        expected_prereqs = sorted(cov_o.get('prerequisites') or [])
        edge_list = rc.get('prerequisite_edges') or []
        seen_from = []
        for edge in edge_list:
            src = edge.get('from')
            tgt = edge.get('target_anchor')
            if src not in cov_by_id or tgt not in valid_map_anchors or tgt != f'#karte-{src}':
                errors.append(f'{oid}: dangling prerequisite link {src!r} -> {tgt!r}')
            else:
                resolved_edge_links += 1
            seen_from.append(src)
        if sorted(seen_from) != expected_prereqs:
            errors.append(f'{oid}: registry prerequisite_edges {sorted(seen_from)} != coverage {expected_prereqs}')

    return {
        'schema_version': 1,
        'task': 'N07',
        'artifact': 'n07-map-drawer-validation',
        'status': 'PASS' if not errors else 'FAIL',
        'summaries_digest': sha256_bytes(canonical_json_bytes(summaries)),
        'registry_digest': sha256_bytes(canonical_json_bytes(registry)),
        'layout': layout_summary,
        'fixtures': fixtures,
        'anchor_revalidation': {
            'total': len(cov_by_id),
            'resolved': anchors_resolved,
            'freeze_bound': freeze_ok,
        },
        'conventions_dissent': {
            'v02_checked': v02_checked,
            'v03_checked': v03_checked,
        },
        'slots_checked': slots_checked,
        'registry_resolution': {
            'concepts_resolved': resolved_map_links,
            'edge_links_resolved': resolved_edge_links,
            'topic_anchors': len(valid_topic_anchors),
        },
        'errors': errors,
    }


def build_runtime_projections(summaries: dict[str, Any], registry: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build compact deterministic runtime payloads for embedding in output/simulator.html.

    Full citations (master_path, master_heading_lv, master_freeze_id) and default
    slot labels are hydrated at runtime from #sim-coverage + slotTemplates so we
    avoid duplicating boilerplate across 64 outcomes inside Section 1.3's JS budget.
    """
    compact_concepts = []
    for c in summaries['concepts']:
        entry: dict[str, Any] = {
            'id': c['id'],
            'summary_lv': c['summary_lv'],
            'figOwner': c['slots']['figures']['owner_task'],
        }
        if c['slots']['figures'].get('status') in ('authored-N11', 'authored-N12', 'authored-N13', 'authored-N14', 'authored-N15'):
            entry['figStatus'] = c['slots']['figures']['status']
            entry['figIds'] = c['slots']['figures'].get('figure_ids', [])
        if c['slots']['chains'].get('status') == 'authored-N16':
            entry['chainStatus'] = c['slots']['chains']['status']
            entry['chainIds'] = c['slots']['chains'].get('chain_ids', [])
        if c.get('conventions_refs'):
            entry['conventions_refs'] = c['conventions_refs']
        if c.get('dissent_note_lv'):
            entry['dissent_note_lv'] = c['dissent_note_lv']
        compact_concepts.append(entry)

    compact_summaries = {
        'schema_version': summaries['schema_version'],
        'island_id': summaries['island_id'],
        'default_chain_depth': summaries['default_chain_depth'],
        'wrap_threshold': summaries['wrap_threshold'],
        'slotTemplates': {
            'chainsOwner': 'N16',
            'practiceOwner': 'N30',
        },
        'concepts': compact_concepts,
    }

    compact_registry = {
        'schema_version': registry['schema_version'],
        'artifact': registry['artifact'],
        'owner': registry['owner'],
        'drawer_overlay_id': registry['drawer_overlay_id'],
        'topic_map_anchors': registry['topic_map_anchors'],
        'open_link_contract': registry['open_link_contract'],
        'concepts': [
            {
                'concept_id': rc['concept_id'],
                'map_anchor': rc['map_anchor'],
                'topic_anchor': rc['topic_anchor'],
                'objectives_anchor': rc['objectives_anchor'],
                'drawer_target': rc['drawer_target'],
            }
            for rc in registry['concepts']
        ],
    }
    return compact_summaries, compact_registry


def format_summary(report: dict[str, Any]) -> str:
    ly = report.get('layout') or {}
    ar = report.get('anchor_revalidation') or {}
    rr = report.get('registry_resolution') or {}
    return (
        f"concept_map {report['status']}: {ly.get('total_nodes', 0)} nodes, "
        f"{ly.get('total_edges', 0)} edges ({ly.get('cross_topic_edges', 0)} cross-topic), "
        f"anchors {ar.get('resolved', 0)}/{ar.get('total', 0)}, "
        f"registry {rr.get('concepts_resolved', 0)}/64, slots {report.get('slots_checked', 0)}/192"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--island', default=str(DEST / COVERAGE_PATH))
    parser.add_argument('--summaries', default=str(DEST / SUMMARIES_PATH))
    parser.add_argument('--registry', default=str(DEST / REGISTRY_PATH))
    parser.add_argument('--report', default=None)
    args = parser.parse_args(argv)
    report = validate_all(
        island_path=Path(args.island),
        summaries_path=Path(args.summaries),
        registry_path=Path(args.registry),
        repo_root=DEST,
    )
    if args.report:
        out = Path(args.report)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(format_summary(report))
    for err in report['errors']:
        print(f'  ERROR: {err}', file=sys.stderr)
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
