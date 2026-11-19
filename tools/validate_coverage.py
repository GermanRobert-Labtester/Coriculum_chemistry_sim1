#!/usr/bin/env python3
"""Validate the N02 coverage island as the simulator's single teaching truth.

Checks, in order:
  * the island schema (required fields, ids, topics, bindings, labels);
  * the recorded count table (64 outcomes; 9/10/11/11/10/8/5 per topic);
  * the planning-source cross-check (ids, statements, anchors, paths, families);
  * prerequisite edge resolution and acyclicity;
  * the anchoring audit (every master_anchor exists case-exactly, its heading
    matches the recorded master heading, and the master digest is the frozen
    N01 digest);
  * the two-level labeling audit (official programme facts versus PROPOSED
    outcome granularity).

The build pipeline imports :func:`validate` and refuses to build on any error.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import (  # noqa: E402
    ANCHOR_RE, COVERAGE_PATH, DEST, EXPECTED_PER_TOPIC, EXPECTED_TOTAL,
    FAMILIES_PATH, INVENTORY_PATH, OUTCOME_ID_RE, PLANNING_PATH,
    PROGRAMME_EXTRACT_PATH, SCHEMA_VERSION, TOPIC_MASTER_PATHS,
    anchor_heading, canonical_json_bytes, family_ids, find_cycle,
    inventory_master_digests, json_contains_unicode_escape, load_json,
    normalise_ws, parse_master, sha256_file,
)

COUNT_HINT = (
    'If this is an intentional count change, update EXPECTED_TOTAL / '
    'EXPECTED_PER_TOPIC in tools/coverage_common.py and the expected block in '
    'data/coverage.json in the same commit; the island is then re-authored and '
    're-gated.'
)

REQUIRED_ISLAND_KEYS = (
    'schema_version', 'island_id', 'title_lv', 'purpose_lv', 'source',
    'epistemic_contract', 'official_facts', 'training_policy', 'expected',
    'topics', 'outcomes',
)
REQUIRED_OUTCOME_KEYS = (
    'id', 'topic', 'statement_lv', 'planning_statement_lv', 'comment',
    'statement_label', 'granularity_label', 'master_path', 'master_anchor',
    'master_heading_lv', 'master_freeze_id', 'bindings', 'prerequisites',
)


def _error(errors: list[str], message: str) -> None:
    errors.append(message)


def _load_planning(repo_root: Path) -> list[dict]:
    with (repo_root / PLANNING_PATH).open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def _programme_text(repo_root: Path) -> str:
    return normalise_ws((repo_root / PROGRAMME_EXTRACT_PATH).read_text(encoding='utf-8'))


def validate(island_path: str | Path = DEST / COVERAGE_PATH,
             repo_root: str | Path = DEST,
             masters_root: str | Path | None = None,
             check_anchors: bool = True,
             check_planning: bool = True) -> dict:
    repo_root = Path(repo_root)
    masters_root = Path(masters_root) if masters_root is not None else repo_root
    island_file = Path(island_path)
    if not island_file.is_absolute():
        island_file = repo_root / island_file
    errors: list[str] = []
    report: dict = {
        'schema_version': 1,
        'task': 'N02',
        'artifact': 'coverage-validation',
        'island': str(island_file.relative_to(repo_root)) if island_file.is_relative_to(repo_root) else str(island_file),
        'island_sha256': sha256_file(island_file) if island_file.is_file() else None,
        'island_bytes': island_file.stat().st_size if island_file.is_file() else None,
        'expected': {'total': EXPECTED_TOTAL, 'per_topic': {str(t): EXPECTED_PER_TOPIC[t] for t in range(1, 8)}},
        'checks': {},
        'errors': errors,
        'status': 'FAIL',
    }
    if not island_file.is_file():
        _error(errors, f'Island file missing: {island_file}')
        return report
    try:
        raw = island_file.read_bytes()
        island = json.loads(raw.decode('utf-8'))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        _error(errors, f'Island is not readable UTF-8 JSON: {island_file}: {exc}')
        return report

    # ---- schema: top level -------------------------------------------------
    if not isinstance(island, dict):
        _error(errors, 'Island root must be a JSON object')
        return report
    for key in REQUIRED_ISLAND_KEYS:
        if key not in island:
            _error(errors, f'Missing island field: {key}')
    if island.get('schema_version') != SCHEMA_VERSION:
        _error(errors, f'Island schema_version is {island.get("schema_version")!r}, expected {SCHEMA_VERSION}')
    if island.get('island_id') != 'sim-coverage':
        _error(errors, f'Island id is {island.get("island_id")!r}, expected "sim-coverage"')
    if json_contains_unicode_escape(raw):
        _error(errors, 'Island source escapes non-ASCII text as \\uXXXX; the declared emission rule is UTF-8 with Latvian text intact')
    for key in ('title_lv', 'purpose_lv'):
        if not isinstance(island.get(key), str) or not island.get(key).strip():
            _error(errors, f'Island {key} must be a non-empty string')

    # ---- recorded expectation ---------------------------------------------
    expected = island.get('expected', {})
    if not isinstance(expected, dict):
        _error(errors, 'Island expected must be an object')
        expected = {}
    if expected.get('total') != EXPECTED_TOTAL:
        _error(errors, f'Count assertion: expected.total is {expected.get("total")!r}, recorded expectation is {EXPECTED_TOTAL}. {COUNT_HINT}')
    per_topic_expected = expected.get('per_topic', {})
    if not isinstance(per_topic_expected, dict):
        _error(errors, 'Island expected.per_topic must be an object')
        per_topic_expected = {}
    for topic, count in EXPECTED_PER_TOPIC.items():
        if per_topic_expected.get(str(topic)) != count:
            _error(errors, f'Count assertion: expected.per_topic["{topic}"] is {per_topic_expected.get(str(topic))!r}, recorded expectation is {count}. {COUNT_HINT}')

    # ---- official facts and training policy -------------------------------
    extract = _programme_text(repo_root) if (repo_root / PROGRAMME_EXTRACT_PATH).is_file() else ''
    facts = island.get('official_facts', [])
    if not isinstance(facts, list) or len(facts) < 3:
        _error(errors, 'At least three official_facts entries are required')
        facts = facts if isinstance(facts, list) else []
    for fact in facts:
        if fact.get('label') != 'PROGRAMME-SOURCED':
            _error(errors, f'Official fact {fact.get("id")!r} must carry label PROGRAMME-SOURCED')
        quote = fact.get('evidence_quote')
        if not isinstance(quote, str) or not quote.strip():
            _error(errors, f'Official fact {fact.get("id")!r} must carry evidence_quote')
        elif extract and normalise_ws(quote) not in extract:
            _error(errors, f'Official fact {fact.get("id")!r} quote is not in {PROGRAMME_EXTRACT_PATH}: {quote!r}')
    fact_text = ' '.join(str(f.get('statement_lv', '')) for f in facts)
    if extract:
        if '180' not in fact_text:
            _error(errors, 'Official facts must state the 180-minute maximum')
        if 'papīra' not in fact_text:
            _error(errors, 'Official facts must state that the colloquium is written on paper')

    policy = island.get('training_policy', [])
    if not isinstance(policy, list) or not policy:
        _error(errors, 'training_policy must be a non-empty list')
        policy = policy if isinstance(policy, list) else []
    if not any(item.get('label') == 'PROPOSED' for item in policy):
        _error(errors, 'training_policy must contain at least one PROPOSED entry')
    for item in policy:
        if item.get('label') != 'PROPOSED':
            _error(errors, f'Training-policy entry {item.get("id")!r} must carry label PROPOSED, found {item.get("label")!r}')
    policy_text = ' '.join(str(item.get('statement_lv', '')) for item in policy)
    if '64' not in policy_text:
        _error(errors, 'training_policy must record the 64-outcome granularity as PROPOSED')
    if not any('niska' in str(item.get('note', '')) or 'nenosaka' in str(item.get('note', '')) for item in policy):
        _error(errors, 'training_policy must state that the programme PDF does not define the outcome-level split')

    # ---- topics ------------------------------------------------------------
    topics = island.get('topics', [])
    if not isinstance(topics, list) or len(topics) != 7:
        _error(errors, f'Expected exactly 7 topics, found {len(topics) if isinstance(topics, list) else "not-a-list"}')
        topics = topics if isinstance(topics, list) else []
    topic_numbers: list[int] = []
    official_names: dict[int, str] = {}
    for topic in topics:
        number = topic.get('topic')
        if not isinstance(number, int) or number not in range(1, 8):
            _error(errors, f'Topic number out of range: {number!r}')
            continue
        if number in topic_numbers:
            _error(errors, f'Duplicate topic number: {number}')
        topic_numbers.append(number)
        if topic.get('label') != 'PROGRAMME-SOURCED':
            _error(errors, f'Topic {number} label must be PROGRAMME-SOURCED')
        if topic.get('source') != 'programme-pdf':
            _error(errors, f'Topic {number} source must be programme-pdf')
        name = topic.get('name_lv')
        if not isinstance(name, str) or not name.strip():
            _error(errors, f'Topic {number} name_lv must be a non-empty string')
        else:
            official_names[number] = name
        heading = topic.get('official_heading')
        if not isinstance(heading, str) or not heading.strip():
            _error(errors, f'Topic {number} official_heading must be a non-empty string')
        elif extract and normalise_ws(heading) not in extract:
            _error(errors, f'Topic {number} official_heading is not in {PROGRAMME_EXTRACT_PATH}: {heading!r}')
    if sorted(topic_numbers) != list(range(1, 8)):
        _error(errors, f'Topic numbers must be exactly 1..7, found {sorted(topic_numbers)}')

    # ---- outcomes: schema, ids, labels, bindings --------------------------
    outcomes = island.get('outcomes', [])
    if not isinstance(outcomes, list):
        _error(errors, 'outcomes must be a list')
        outcomes = []
    if len(outcomes) != EXPECTED_TOTAL:
        _error(errors, f'Count assertion: expected {EXPECTED_TOTAL} outcomes (9/10/11/11/10/8/5), found {len(outcomes)}. {COUNT_HINT}')
    known_families = family_ids(repo_root)
    ids: list[str] = []
    by_id: dict[str, dict] = {}
    by_topic: dict[int, list[str]] = defaultdict(list)
    edges: dict[str, list[str]] = {}
    proposed_outcomes = 0
    for outcome in outcomes:
        if not isinstance(outcome, dict):
            _error(errors, 'Every outcome must be an object')
            continue
        oid = outcome.get('id')
        if not isinstance(oid, str) or not OUTCOME_ID_RE.fullmatch(oid):
            _error(errors, f'Invalid outcome id: {oid!r}')
            continue
        if oid in by_id:
            _error(errors, f'Duplicate outcome id: {oid}')
            continue
        ids.append(oid)
        by_id[oid] = outcome
        for key in REQUIRED_OUTCOME_KEYS:
            if key not in outcome:
                _error(errors, f'{oid}: missing field {key}')
        topic = outcome.get('topic')
        if not isinstance(topic, int) or topic not in range(1, 8):
            _error(errors, f'{oid}: topic out of range: {topic!r}')
            continue
        prefix_topic = int(OUTCOME_ID_RE.fullmatch(oid).group(1))
        if prefix_topic != topic:
            _error(errors, f'{oid}: id prefix names topic {prefix_topic}, topic field says {topic}')
        by_topic[topic].append(oid)
        statement = outcome.get('statement_lv')
        planning = outcome.get('planning_statement_lv')
        if not isinstance(statement, str) or not statement.strip():
            _error(errors, f'{oid}: statement_lv must be a non-empty string')
        if not isinstance(planning, str) or not planning.strip():
            _error(errors, f'{oid}: planning_statement_lv must be a non-empty string')
        if statement != planning:
            comment = outcome.get('comment')
            if not isinstance(comment, str) or not comment.strip():
                _error(errors, f'{oid}: statement differs from the planning wording but comment is empty; master wording wins and the planning wording must be noted, never silently edited')
        if outcome.get('statement_label') != 'PROPOSED':
            _error(errors, f'{oid}: statement_label must be PROPOSED (outcome granularity is training policy)')
        else:
            proposed_outcomes += 1
        if outcome.get('granularity_label') != 'PROPOSED':
            _error(errors, f'{oid}: granularity_label must be PROPOSED')
        path = outcome.get('master_path')
        if path != TOPIC_MASTER_PATHS[topic]:
            _error(errors, f'{oid}: master_path {path!r} does not match topic {topic} master {TOPIC_MASTER_PATHS[topic]!r}')
        anchor = outcome.get('master_anchor')
        if not isinstance(anchor, str) or not ANCHOR_RE.fullmatch(anchor):
            _error(errors, f"{oid}: invalid master_anchor {anchor!r} (ASCII letters/digits/hyphens only; the resolver then enforces the master's exact case)")
        if not isinstance(outcome.get('master_heading_lv'), str) or not outcome['master_heading_lv'].strip():
            _error(errors, f'{oid}: master_heading_lv must be a non-empty string')
        if outcome.get('master_freeze_id') != f'C{topic}-MASTER':
            _error(errors, f'{oid}: master_freeze_id must be C{topic}-MASTER, found {outcome.get("master_freeze_id")!r}')
        bindings = outcome.get('bindings')
        if not isinstance(bindings, dict):
            _error(errors, f'{oid}: bindings must be an object')
            bindings = {}
        practice = bindings.get('practice_families')
        if not isinstance(practice, list) or not practice:
            _error(errors, f'{oid}: bindings.practice_families must be a non-empty list')
        else:
            for family in practice:
                if family not in known_families:
                    _error(errors, f'{oid}: unknown practice family {family!r}')
            if len(set(practice)) != len(practice):
                _error(errors, f'{oid}: duplicate practice family in bindings')
        exam = bindings.get('exam_slots')
        if not isinstance(exam, list):
            _error(errors, f'{oid}: bindings.exam_slots must be a list')
        elif exam:
            _error(errors, f'{oid}: bindings.exam_slots must stay an unfilled declared slot for N24, found {exam!r}')
        if bindings.get('points') is not None:
            _error(errors, f'{oid}: bindings.points must stay null for N24, found {bindings.get("points")!r}')
        if bindings.get('minutes') is not None:
            _error(errors, f'{oid}: bindings.minutes must stay null for N24, found {bindings.get("minutes")!r}')
        if bindings.get('policy_owner') != 'N24':
            _error(errors, f'{oid}: bindings.policy_owner must be N24')
        prerequisites = outcome.get('prerequisites')
        if not isinstance(prerequisites, list) or not all(isinstance(p, str) for p in prerequisites):
            _error(errors, f'{oid}: prerequisites must be a list of outcome ids')
        else:
            if len(set(prerequisites)) != len(prerequisites):
                _error(errors, f'{oid}: duplicate prerequisite edge')
            edges[oid] = prerequisites

    # ---- topic counts and topic outcome lists ------------------------------
    counts = {t: len(by_topic.get(t, [])) for t in range(1, 8)}
    for topic, count in EXPECTED_PER_TOPIC.items():
        if counts[topic] != count:
            _error(errors, f'Count assertion: topic {topic} has {counts[topic]} outcomes, recorded expectation is {count}. {COUNT_HINT}')
    for topic in topics:
        number = topic.get('topic')
        if not isinstance(number, int) or number not in range(1, 8):
            continue
        declared = topic.get('outcome_ids')
        if not isinstance(declared, list) or not all(isinstance(x, str) for x in declared):
            _error(errors, f'Topic {number}: outcome_ids must be a list of strings')
            continue
        actual = by_topic.get(number, [])
        if declared != actual:
            _error(errors, f'Topic {number}: outcome_ids do not match the outcomes in order; declared {declared}, actual {actual}')

    # ---- edges: resolution and acyclicity ----------------------------------
    dangling = 0
    edge_total = sum(len(v) for v in edges.values())
    for oid, prerequisites in edges.items():
        for target in prerequisites:
            if target not in by_id:
                dangling += 1
                _error(errors, f'Dangling prerequisite edge: {oid} -> {target} (target is not an outcome id)')
            elif target == oid:
                _error(errors, f'Self prerequisite edge: {oid} -> {oid}')
    cycle = find_cycle({oid: [p for p in prereqs if p in by_id] for oid, prereqs in edges.items()})
    if cycle:
        _error(errors, 'Cyclic prerequisite edge set: ' + ' -> '.join(cycle))
    cross_topic = sum(
        1 for oid, prereqs in edges.items() for p in prereqs
        if p in by_id and by_id[p]['topic'] != by_id[oid]['topic']
    )
    report['checks']['edges'] = {
        'edges': edge_total,
        'cross_topic': cross_topic,
        'dangling': dangling,
        'cycle': cycle,
    }

    # ---- planning-source cross-check --------------------------------------
    planning_report: dict = {'checked': False}
    if check_planning:
        rows = _load_planning(repo_root)
        planning_report['checked'] = True
        planning_report['rows'] = len(rows)
        planning_ids = [row['outcome_id'] for row in rows]
        if len(planning_ids) != len(set(planning_ids)):
            _error(errors, 'Planning source contains duplicate outcome ids')
        planning_by_id = {row['outcome_id']: row for row in rows}
        missing = sorted(set(planning_by_id) - set(by_id))
        extra = sorted(set(by_id) - set(planning_by_id))
        if missing:
            _error(errors, f'Planning outcomes missing from the island: {missing}')
        if extra:
            _error(errors, f'Island outcomes absent from the planning source: {extra}')
        planning_counts = Counter(int(row['programme_topic']) for row in rows)
        for topic, count in EXPECTED_PER_TOPIC.items():
            if planning_counts.get(topic, 0) != count:
                _error(errors, f'Planning source topic {topic} has {planning_counts.get(topic, 0)} rows, recorded expectation is {count}. {COUNT_HINT}')
        statements_match = 0
        families_match = 0
        for oid in sorted(set(by_id) & set(planning_by_id)):
            row = planning_by_id[oid]
            outcome = by_id[oid]
            if outcome.get('planning_statement_lv') != row['requirement_lv']:
                _error(errors, f'{oid}: planning_statement_lv differs from {PLANNING_PATH}: {outcome.get("planning_statement_lv")!r} != {row["requirement_lv"]!r}')
            else:
                statements_match += 1
            if outcome.get('master_anchor') != row['master_anchor']:
                _error(errors, f'{oid}: master_anchor differs from {PLANNING_PATH}: {outcome.get("master_anchor")!r} != {row["master_anchor"]!r}')
            if outcome.get('master_path') != row['master_path']:
                _error(errors, f'{oid}: master_path differs from {PLANNING_PATH}: {outcome.get("master_path")!r} != {row["master_path"]!r}')
            if int(row['programme_topic']) != outcome.get('topic'):
                _error(errors, f'{oid}: topic differs from {PLANNING_PATH}: {outcome.get("topic")!r} != {row["programme_topic"]!r}')
            planned = [x for x in row['planned_families'].split(';') if x]
            bound = (outcome.get('bindings') or {}).get('practice_families') or []
            if set(planned) != set(bound):
                _error(errors, f'{oid}: practice families differ from {PLANNING_PATH}: {bound} != {planned}')
            else:
                families_match += 1
        planning_report.update({
            'ids_match': not missing and not extra,
            'statements_match': statements_match,
            'families_match': families_match,
            'per_topic': {str(t): planning_counts.get(t, 0) for t in range(1, 8)},
        })
    report['checks']['planning'] = planning_report

    # ---- anchor resolution and frozen-master binding ----------------------
    anchors_report: dict = {'checked': check_anchors, 'resolved': 0, 'failed': 0, 'per_topic': {}}
    if check_anchors:
        inventory = inventory_master_digests(repo_root)
        masters: dict[int, object] = {}
        master_report: list[dict] = []
        for topic, relative in TOPIC_MASTER_PATHS.items():
            full = masters_root / relative
            entry = inventory.get(topic, {})
            record = {
                'topic': topic,
                'freeze_id': entry.get('id'),
                'path': relative,
                'recorded_sha256': entry.get('sha256'),
                'recorded_bytes': entry.get('bytes'),
            }
            if not full.is_file():
                _error(errors, f'Frozen master missing: {entry.get("id", f"C{topic}-MASTER")}: {full}')
                master_report.append({**record, 'status': 'MISSING'})
                continue
            digest = sha256_file(full)
            record.update({'sha256': digest, 'bytes': full.stat().st_size})
            if entry.get('sha256') != digest:
                _error(errors, f'Frozen master digest mismatch: {entry.get("id", f"C{topic}-MASTER")}: {digest} != recorded {entry.get("sha256")} ({relative})')
                record['status'] = 'DIGEST-MISMATCH'
            else:
                record['status'] = 'FROZEN'
            masters[topic] = parse_master(full)
            master_report.append(record)
        report['checks']['masters'] = master_report
        for outcome in outcomes:
            if not isinstance(outcome, dict) or not outcome.get('id'):
                continue
            oid = outcome['id']
            topic = outcome.get('topic')
            if topic not in masters:
                anchors_report['failed'] += 1
                continue
            index = masters[topic]
            anchor = outcome.get('master_anchor')
            topic_counts = anchors_report['per_topic'].setdefault(str(topic), {'resolved': 0, 'total': 0})
            topic_counts['total'] += 1
            if anchor not in index.ids:
                anchors_report['failed'] += 1
                hint = [value for value in index.ids if isinstance(anchor, str) and value.lower() == anchor.lower()]
                suffix = f'; case-insensitive matches exist but are not accepted: {hint[:3]}' if hint else ''
                _error(errors, f'Anchor resolution failed: {oid} #{anchor} not found in {outcome.get("master_freeze_id")} ({outcome.get("master_path")}); matching is case-exact{suffix}')
                continue
            heading = anchor_heading(index, anchor)
            if heading != outcome.get('master_heading_lv'):
                _error(errors, f'Master heading mismatch: {oid} #{anchor} records {outcome.get("master_heading_lv")!r}, the master heading is {heading!r}')
            anchors_report['resolved'] += 1
            topic_counts['resolved'] += 1
        anchors_report['total'] = len([o for o in outcomes if isinstance(o, dict) and o.get('id')])
    report['checks']['anchors'] = anchors_report

    # ---- counts, labels and status ----------------------------------------
    report['checks']['schema'] = {
        'island_keys': 'present',
        'outcomes_checked': len(outcomes),
        'unique_ids': len(set(ids)),
        'duplicate_ids': [oid for oid, count in Counter(ids).items() if count > 1],
        'invalid_ids': [oid for oid in ids if not OUTCOME_ID_RE.fullmatch(oid)],
    }
    report['counts'] = {
        'total': len(outcomes),
        'expected_total': EXPECTED_TOTAL,
        'per_topic': {str(t): counts[t] for t in range(1, 8)},
        'expected_per_topic': {str(t): EXPECTED_PER_TOPIC[t] for t in range(1, 8)},
        'match': len(outcomes) == EXPECTED_TOTAL and all(counts[t] == EXPECTED_PER_TOPIC[t] for t in range(1, 8)),
    }
    report['checks']['labels'] = {
        'topics': {'label': 'PROGRAMME-SOURCED', 'count': len(official_names)},
        'official_facts': {'label': 'PROGRAMME-SOURCED', 'count': len(facts)},
        'training_policy': {'label': 'PROPOSED', 'count': len(policy)},
        'outcome_statements': {'label': 'PROPOSED', 'count': proposed_outcomes},
        'outcome_granularity': {'label': 'PROPOSED', 'count': len(outcomes)},
    }
    report['checks']['source'] = {
        'planning': PLANNING_PATH,
        'planning_sha256': sha256_file(repo_root / PLANNING_PATH) if (repo_root / PLANNING_PATH).is_file() else None,
        'programme_extract': PROGRAMME_EXTRACT_PATH,
        'inventory': INVENTORY_PATH,
        'emission_rule': 'sorted keys; separators (",",":"); ensure_ascii=False; UTF-8',
        'canonical_island_bytes': len(canonical_json_bytes(island)),
    }
    report['status'] = 'PASS' if not errors else 'FAIL'
    return report


def format_summary(report: dict) -> str:
    counts = report.get('counts', {})
    per_topic = counts.get('per_topic', {})
    distribution = '/'.join(str(per_topic.get(str(t), '?')) for t in range(1, 8))
    edges = report.get('checks', {}).get('edges', {})
    anchors = report.get('checks', {}).get('anchors', {})
    label = 'PASS' if report.get('status') == 'PASS' else 'FAIL'
    line = (f'{label} coverage-island: {counts.get("total")} outcomes ({distribution}); '
            f'{edges.get("edges", 0)} prerequisite edges ({edges.get("cross_topic", 0)} cross-topic); '
            f'cycle={edges.get("cycle")}')
    if anchors.get('checked'):
        line += f'; anchors {anchors.get("resolved")}/{anchors.get("total", anchors.get("resolved"))} resolved'
    lines = [line]
    for error in report.get('errors', []):
        lines.append(f'  - {error}')
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--island', default=str(DEST / COVERAGE_PATH), help='Island JSON path')
    parser.add_argument('--repo-root', default=str(DEST), help='Repository root')
    parser.add_argument('--masters-root', default=None, help='Root containing materials/ (defaults to repo root)')
    parser.add_argument('--skip-anchors', action='store_true', help='Skip the heavy master-anchor check (not for the gate)')
    parser.add_argument('--skip-planning', action='store_true', help='Skip the planning-source cross-check')
    parser.add_argument('--report', default=None, help='Write the machine-readable report to this path')
    parser.add_argument('--json', action='store_true', help='Print the report JSON instead of the summary')
    args = parser.parse_args(argv)
    report = validate(
        island_path=args.island,
        repo_root=args.repo_root,
        masters_root=args.masters_root,
        check_anchors=not args.skip_anchors,
        check_planning=not args.skip_planning,
    )
    if args.report:
        target = Path(args.report)
        if not target.is_absolute():
            target = DEST / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_summary(report))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
