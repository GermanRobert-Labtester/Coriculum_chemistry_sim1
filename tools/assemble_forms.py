#!/usr/bin/env python3
"""N24 build-time form assembler (Python twin of src/assembly.ts).

Assembles the three frozen exam-simulation forms (A, B, C) from the verified
frozen practice bank using the frozen N05 SplitMix64 PRNG (tools/prng.py),
and builds the #sim-forms JSON island plus output/forms/form_{A,B,C}.json.

Pipeline-order contract (C.1.1):
  Assembly refuses to proceed unless ``bank_verified`` is True AND the
  supplied ``bank_digest`` is non-empty and matches the SHA-256 of the
  canonical bank projection being assembled. It never assembles over an
  unverified or stale bank.

Notice: This module does NOT contain the independent constraint checker.
Verification lives separately in tools/validate_n24_assembly.py (and
SimAssembly.verifyFormManifest) with zero shared logic.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402
from prng import SplitMix64  # noqa: E402

POLICY_ID = 'splitmix64-u64-v1'
DEFAULT_FORM_SEEDS = {
    'A': '100001',
    'B': '100002',
    'C': '100003',
}
DEFAULT_Q11_FIGURES = {
    'COL1-2-2D-A-01': 'FIG-T2-PLOT-NACL-DENSITY',
    'COL1-2-2D-C-01': 'FIG-T2-PLOT-NACL-DENSITY',
    'COL1-5-5B-D-01': 'FIG-T5-LIN-FIRST',
    'COL1-7-7B-A-01': 'FIG-T67-CAL-MASTER',
}

EXAM_POLICY_PATH = 'data/exam_policy.json'
BLUEPRINT_PATH = 'docs/SIMULATION_BLUEPRINT.json'
SEED_POLICY_PATH = 'data/seed_policy.json'
PRNG_CONTRACT_PATH = 'data/prng_contract_vectors.json'
EPH_RE = re.compile(r'-EPH-[0-9]+$')


class AssemblyPipelineError(RuntimeError):
    """Named failure raised when assembly preconditions or constraints fail."""

    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(f'[{code}] {message}')
        self.code = code
        self.message = message
        self.details = details or {}


def _rubric_points(inst: dict[str, Any]) -> int | float:
    total = sum(float(c.get('points', 0)) for c in (inst.get('rubric') or []))
    rounded = round(total, 6)
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def _is_eligible(inst: dict[str, Any], allow_ephemeral: bool = False) -> bool:
    if not isinstance(inst, dict):
        return False
    ext_data = (inst.get('extensions') or {}).get('data') or {}
    eph_meta = ext_data.get('ephemeral') or {}
    is_eph = bool(eph_meta.get('frozen_bank_member') is False or EPH_RE.search(str(inst.get('question_id', ''))))
    if is_eph and not allow_ephemeral:
        return False
    rev = inst.get('review') or {}
    if (
        rev.get('accessibility') != 'passed'
        or rev.get('calculation') != 'passed'
        or rev.get('content') != 'passed'
        or rev.get('source') != 'passed'
    ):
        return False
    wf = ext_data.get('review_workflow')
    if isinstance(wf, dict) and wf.get('state') != 'accepted':
        return False
    return True


def _instance_types(inst: dict[str, Any]) -> list[str]:
    out: list[str] = []
    tid = inst.get('type_id')
    if isinstance(tid, str) and tid:
        out.append(tid)
    for t in (inst.get('type_ids') or []):
        if t not in out:
            out.append(t)
    return out


def _resolve_figure_id(inst: dict[str, Any], figure_map: dict[str, str]) -> str | None:
    if inst.get('type_id') != 'Q11':
        return None
    qid = str(inst.get('question_id', ''))
    if qid in figure_map:
        return figure_map[qid]
    if qid in DEFAULT_Q11_FIGURES:
        return DEFAULT_Q11_FIGURES[qid]
    topic = inst.get('topic')
    if topic == 2:
        return 'FIG-T2-PLOT-NACL-DENSITY'
    if topic == 5:
        return 'FIG-T5-LIN-FIRST'
    if topic == 7:
        return 'FIG-T67-CAL-MASTER'
    return None


def _build_shortage(
    form_id: str,
    constraint: str,
    topic: int | None,
    slot_id: str | None,
    missing_family: str | None,
    missing_type: str | None,
    required_count: int,
    available_count: int,
    pending_families: list[str],
) -> dict[str, Any]:
    sorted_pending = sorted(set(pending_families))
    target_label = missing_family or missing_type or (f'{topic}. tēma' if topic is not None else '')
    slot_note = f', vieta {slot_id}' if slot_id else ''
    count_short = max(1, required_count - available_count)
    if sorted_pending:
        reason = (
            f'{form_id} forma pagaidām nav pieejama: gaida recenziju '
            f'({", ".join(sorted_pending)}{slot_note}, iztrūkst {count_short}).'
        )
    else:
        reason = (
            f'{form_id} forma pagaidām nav pieejama: nepietiek atbilstošu uzdevumu '
            f'({target_label}{slot_note}, iztrūkst {count_short}).'
        )
    return {
        'schema_version': 1,
        'form_id': form_id,
        'status': 'SHORTAGE',
        'disabled': True,
        'binding_constraint': constraint,
        'topic': topic,
        'slot_id': slot_id,
        'missing_family': missing_family,
        'missing_type': missing_type,
        'required_count': required_count,
        'available_count': available_count,
        'count_short': count_short,
        'pending_review_families': sorted_pending,
        'disabled_reason_lv': reason,
    }


def load_assembly_spec(repo_root: Path = DEST) -> dict[str, Any]:
    exam_policy = load_json(repo_root / EXAM_POLICY_PATH)
    blueprint = load_json(repo_root / BLUEPRINT_PATH)
    bp_allowed = {s['slot_id']: list(s.get('allowed_family_ids') or []) for s in blueprint['slots']}
    slots = []
    topic_points: dict[str, int] = {}
    for s in exam_policy['slots']:
        sid = s['slot_id']
        t = int(s['topic'])
        pts = int(s['points'])
        slots.append({
            'slot_id': sid,
            'topic': t,
            'points': pts,
            'allowed_family_ids': bp_allowed.get(sid),
        })
        topic_points[str(t)] = topic_points.get(str(t), 0) + pts
    return {
        'slots': slots,
        'required_types': list(exam_policy['exam']['required_types_per_form']),
        'topic_points': topic_points,
        'total_points': int(exam_policy['exam']['total_points']),
    }


def assemble_form(
    *,
    form_id: str,
    seed: str | int,
    bank_questions: list[dict[str, Any]],
    bank_digest: str,
    bank_verified: bool = True,
    expected_bank_digest: str | None = None,
    prng_contract_digest: str = '',
    spec: dict[str, Any] | None = None,
    allow_ephemeral: bool = False,
    strict_rubric_points: bool = False,
    figure_map: dict[str, str] | None = None,
    avoid_families_by_slot: dict[str, list[str]] | None = None,
    avoid_instances_by_slot: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    """Assemble one form deterministically. Mirrors src/assembly.ts byte-for-byte."""
    if not bank_verified or not isinstance(bank_digest, str) or not bank_digest.strip():
        raise AssemblyPipelineError(
            'E_ASSEMBLY_BANK_UNVERIFIED',
            'Formu montāža apturēta: bankas integritātes zīmogs nav nodots vai banka nav verificēta.',
            {'form_id': form_id},
        )
    if expected_bank_digest is not None and bank_digest != expected_bank_digest:
        raise AssemblyPipelineError(
            'E_ASSEMBLY_BANK_UNVERIFIED',
            'Formu montāža apturēta: bankas zīmogs ir novecojis vai nesakrīt ar verificēto banku.',
            {'expected': expected_bank_digest, 'actual': bank_digest},
        )

    spec_eff = spec or load_assembly_spec(DEST)
    seed_int = int(seed)
    if seed_int < 1:
        raise AssemblyPipelineError('E_ASSEMBLY_SEED_INVALID', f'Nederīga sēkla {seed!r}.')
    stream = SplitMix64(seed_int)
    fig_map = figure_map or DEFAULT_Q11_FIGURES
    avoid_fams = avoid_families_by_slot or {}
    avoid_insts = avoid_instances_by_slot or {}

    raw_bank = sorted(bank_questions, key=lambda q: str(q.get('question_id', '')))
    eligible_by_family: dict[str, list[dict[str, Any]]] = {}
    pending_families: set[str] = set()
    all_families_in_topic: dict[int, list[str]] = {}

    for q in raw_bank:
        fam = q.get('family_id')
        if not fam:
            continue
        topic = int(q['topic'])
        all_families_in_topic.setdefault(topic, [])
        if fam not in all_families_in_topic[topic]:
            all_families_in_topic[topic].append(fam)
        if _is_eligible(q, allow_ephemeral):
            eligible_by_family.setdefault(fam, []).append(q)
        else:
            pending_families.add(fam)

    slots_by_topic: dict[int, list[dict[str, Any]]] = {}
    for s in spec_eff['slots']:
        slots_by_topic.setdefault(int(s['topic']), []).append(s)
    topics = sorted(slots_by_topic.keys())

    shuffled_instances: dict[str, list[dict[str, Any]]] = {}
    for fam in sorted(eligible_by_family.keys()):
        shuffled_instances[fam] = stream.shuffle(eligible_by_family[fam])

    topic_assignments: dict[int, list[tuple[dict[str, Any], str]]] = {}
    for topic in topics:
        topic_slots = slots_by_topic[topic]
        topic_families = sorted(all_families_in_topic.get(topic, []))
        eligible_topic_fams = [f for f in topic_families if eligible_by_family.get(f)]

        if len(eligible_topic_fams) < len(topic_slots):
            pending_in_topic = [f for f in topic_families if f in pending_families and not eligible_by_family.get(f)]
            return {
                'status': 'SHORTAGE',
                'shortage': _build_shortage(
                    form_id, 'topic_slot_count', topic, topic_slots[0]['slot_id'],
                    pending_in_topic[0] if pending_in_topic else None, None,
                    len(topic_slots), len(eligible_topic_fams), pending_in_topic,
                ),
            }

        shuffled_topic_fams = stream.shuffle(eligible_topic_fams)
        chosen: list[tuple[dict[str, Any], str] | None] = [None] * len(topic_slots)
        used_fams: set[str] = set()

        def assign_slot(idx: int) -> bool:
            if idx >= len(topic_slots):
                return True
            slot = topic_slots[idx]
            allowed = slot.get('allowed_family_ids')
            avoid_list = avoid_fams.get(slot['slot_id'], [])
            candidates = []
            for fam in shuffled_topic_fams:
                if fam in used_fams:
                    continue
                if allowed is not None and fam not in allowed:
                    continue
                if strict_rubric_points:
                    if not any(_rubric_points(inst) == slot['points'] for inst in shuffled_instances.get(fam, [])):
                        continue
                candidates.append(fam)
            preferred = [f for f in candidates if f not in avoid_list]
            fallback = [f for f in candidates if f in avoid_list]
            for fam in preferred + fallback:
                used_fams.add(fam)
                chosen[idx] = (slot, fam)
                if assign_slot(idx + 1):
                    return True
                chosen[idx] = None
                used_fams.remove(fam)
            return False

        if not assign_slot(0):
            failed_slot = topic_slots[0]
            missing_fam = None
            pending_in_slot: list[str] = []
            for slot in topic_slots:
                allowed = slot.get('allowed_family_ids') or topic_families
                valid_fams = [
                    fam for fam in allowed
                    if eligible_by_family.get(fam)
                    and (not strict_rubric_points or any(_rubric_points(i) == slot['points'] for i in eligible_by_family[fam]))
                ]
                if not valid_fams:
                    failed_slot = slot
                    missing_fam = allowed[0] if allowed else None
                    pending_in_slot = [f for f in allowed if f in pending_families]
                    break
            return {
                'status': 'SHORTAGE',
                'shortage': _build_shortage(
                    form_id, 'slot_family_eligibility', topic, failed_slot['slot_id'],
                    missing_fam, None, 1, 0, pending_in_slot,
                ),
            }
        topic_assignments[topic] = [pair for pair in chosen if pair is not None]

    by_slot_id: dict[str, tuple[dict[str, Any], str]] = {}
    for topic in topics:
        for slot, fam in topic_assignments[topic]:
            by_slot_id[slot['slot_id']] = (slot, fam)
    ordered_assignments = [by_slot_id[s['slot_id']] for s in spec_eff['slots']]

    req_types = list(spec_eff['required_types'])

    def family_has_type(fam: str, slot_pts: int, type_id: str) -> bool:
        for inst in shuffled_instances.get(fam, []):
            if strict_rubric_points and _rubric_points(inst) != slot_pts:
                continue
            if type_id in _instance_types(inst):
                return True
        return False

    def missing_in_pool(assignments: list[tuple[dict[str, Any], str]]) -> list[str]:
        return [
            rt for rt in req_types
            if not any(family_has_type(fam, int(slot['points']), rt) for slot, fam in assignments)
        ]

    pool_missing = missing_in_pool(ordered_assignments)
    swap_guard = 0
    while pool_missing and swap_guard < 14:
        swap_guard += 1
        need_type = pool_missing[0]
        used_set = {fam for _slot, fam in ordered_assignments}
        swapped = False
        for s_idx, (slot, prev_fam) in enumerate(ordered_assignments):
            allowed = slot.get('allowed_family_ids')
            candidates = [
                fam for fam in sorted(all_families_in_topic.get(int(slot['topic']), []))
                if fam not in used_set
                and eligible_by_family.get(fam)
                and (allowed is None or fam in allowed)
                and family_has_type(fam, int(slot['points']), need_type)
            ]
            for cand in candidates:
                ordered_assignments[s_idx] = (slot, cand)
                nxt_missing = missing_in_pool(ordered_assignments)
                if len(nxt_missing) < len(pool_missing):
                    pool_missing = nxt_missing
                    swapped = True
                    break
                ordered_assignments[s_idx] = (slot, prev_fam)
            if swapped:
                break
        if not swapped:
            break

    picked: list[dict[str, Any]] = []
    for slot, fam in ordered_assignments:
        candidates = [
            inst for inst in shuffled_instances[fam]
            if not strict_rubric_points or _rubric_points(inst) == slot['points']
        ]
        avoid_list = avoid_insts.get(slot['slot_id'], [])
        preferred = [i for i in candidates if i['question_id'] not in avoid_list]
        fallback = [i for i in candidates if i['question_id'] in avoid_list]
        ordered = preferred + fallback if preferred else candidates
        picked.append(ordered[0])

    def missing_types(current: list[dict[str, Any]]) -> list[str]:
        present: set[str] = set()
        for inst in current:
            present.update(_instance_types(inst))
        return [rt for rt in req_types if rt not in present]

    initial_missing = missing_types(picked)
    if initial_missing:
        def solve_missing(current: list[dict[str, Any]], missing: list[str], locked: list[bool]) -> list[dict[str, Any]] | None:
            if not missing:
                return current
            target_type = missing[0]
            fresh_moves: list[tuple[int, dict[str, Any]]] = []
            fallback_moves: list[tuple[int, dict[str, Any]]] = []
            for s_idx, (slot, fam) in enumerate(ordered_assignments):
                if locked[s_idx]:
                    continue
                avoid_list = avoid_insts.get(slot['slot_id'], [])
                for inst in shuffled_instances[fam]:
                    if strict_rubric_points and _rubric_points(inst) != slot['points']:
                        continue
                    if target_type in _instance_types(inst):
                        if inst['question_id'] not in avoid_list:
                            fresh_moves.append((s_idx, inst))
                        else:
                            fallback_moves.append((s_idx, inst))
            for s_idx, inst in fresh_moves + fallback_moves:
                nxt = list(current)
                nxt[s_idx] = inst
                nxt_locked = list(locked)
                nxt_locked[s_idx] = True
                nxt_missing = missing_types(nxt)
                solved = solve_missing(nxt, nxt_missing, nxt_locked)
                if solved is not None:
                    return solved
            return None

        repaired = solve_missing(picked, initial_missing, [False] * len(ordered_assignments))
        if repaired is None:
            still_missing = missing_types(picked)
            target_type = still_missing[0]
            pending_with_type = sorted({
                q['family_id'] for q in raw_bank
                if not _is_eligible(q, allow_ephemeral) and target_type in _instance_types(q)
            })
            return {
                'status': 'SHORTAGE',
                'shortage': _build_shortage(
                    form_id, 'required_type_coverage', None, None,
                    pending_with_type[0] if pending_with_type else None,
                    target_type, 1, 0, pending_with_type,
                ),
            }
        picked = repaired

    slots_out: list[dict[str, Any]] = []
    topic_subtotals: dict[str, dict[str, int]] = {}
    covered_types: set[str] = set()
    conflicts: list[dict[str, Any]] = []
    total_points = 0

    for (slot, _fam), inst in zip(ordered_assignments, picked):
        rub_pts = _rubric_points(inst)
        fig_id = _resolve_figure_id(inst, fig_map)
        t_key = str(slot['topic'])
        sub = topic_subtotals.setdefault(t_key, {'slots': 0, 'points': 0})
        sub['slots'] += 1
        sub['points'] += int(slot['points'])
        total_points += int(slot['points'])
        ts = _instance_types(inst)
        covered_types.update(ts)
        eph_data = ((inst.get('extensions') or {}).get('data') or {}).get('ephemeral')
        is_eph = bool(
            (isinstance(eph_data, dict) and eph_data.get('frozen_bank_member') is False)
            or EPH_RE.search(str(inst['question_id']))
        )
        entry: dict[str, Any] = {
            'slot_id': slot['slot_id'],
            'topic': int(slot['topic']),
            'points': int(slot['points']),
            'instance_id': inst['question_id'],
            'family_id': inst['family_id'],
            'variant_id': inst['variant_id'],
            'type_id': inst['type_id'],
            'type_ids': sorted(ts),
            'rubric_points': rub_pts,
            'ephemeral': is_eph,
        }
        if fig_id:
            entry['figure_id'] = fig_id
        if is_eph and isinstance(eph_data, dict):
            entry['ephemeral_meta'] = {
                'attempt': int(eph_data.get('attempt', 0)),
                'seed': str(eph_data.get('seed', '')),
                'persisted': False,
                'frozen_bank_member': False,
            }
        slots_out.append(entry)
        if rub_pts != slot['points']:
            conflicts.append({
                'id': 'N23-C01',
                'slot_id': slot['slot_id'],
                'instance_id': inst['question_id'],
                'family_id': inst['family_id'],
                'slot_points': int(slot['points']),
                'rubric_points': rub_pts,
                'note_lv': (
                    f'Slota punktu mērogs ({int(slot["points"])}) atšķiras no bankas instances '
                    f'rubrikas summas ({rub_pts}); konflikts N23-C01 saglabāts redzams bez punktu pārmērošanas.'
                ),
            })

    base_manifest = {
        'schema_version': 1,
        'form_id': form_id,
        'status': 'AVAILABLE',
        'mode': 'seeded-training' if allow_ephemeral else 'frozen-exam-form',
        'form_seed': str(seed_int),
        'policy_id': POLICY_ID,
        'prng_contract_digest': str(prng_contract_digest or ''),
        'bank_digest': bank_digest,
        'epistemic_label': 'PROPOSED',
        'total_slots': len(slots_out),
        'total_points': total_points,
        'topic_subtotals': topic_subtotals,
        'covered_types': sorted(covered_types),
        'required_types_covered': all(rt in covered_types for rt in req_types),
        'slots': slots_out,
        'conflicts': conflicts,
    }
    manifest_digest = sha256_bytes(canonical_json_bytes(base_manifest))
    manifest = dict(base_manifest)
    manifest['manifest_digest'] = manifest_digest
    return {'status': 'AVAILABLE', 'manifest': manifest}


def assemble_frozen_forms(
    *,
    bank_island: dict[str, Any],
    bank_digest: str,
    bank_embedded_digest: str,
    bank_verified: bool,
    repo_root: Path = DEST,
    seeds: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Assemble forms A, B, C and build the #sim-forms island payload."""
    questions = bank_island.get('questions') or []
    live_digest = sha256_bytes(canonical_json_bytes(bank_island))
    if not bank_verified or not bank_digest or bank_digest != live_digest:
        raise AssemblyPipelineError(
            'E_ASSEMBLY_BANK_UNVERIFIED',
            'Formu montāža atteikta: bankas integritātes zīmogs neatbilst pārbaudītajai bankai.',
            {'supplied': bank_digest, 'live': live_digest, 'bank_verified': bank_verified},
        )

    seed_policy = load_json(repo_root / SEED_POLICY_PATH)
    reserved = seed_policy['seed_vocabulary']['N24_assembly']['reserved_assignments']
    active_seeds = seeds or {
        'A': str(reserved['form_A']),
        'B': str(reserved['form_B']),
        'C': str(reserved['form_C']),
    }
    prng_contract = load_json(repo_root / PRNG_CONTRACT_PATH)
    prng_contract_digest = sha256_bytes(canonical_json_bytes(prng_contract))
    spec = load_assembly_spec(repo_root)

    used_families_by_slot: dict[str, list[str]] = {}
    used_instances_by_slot: dict[str, list[str]] = {}
    forms_out: list[dict[str, Any]] = []
    shortages_out: list[dict[str, Any]] = []

    for fid in ('A', 'B', 'C'):
        res = assemble_form(
            form_id=fid,
            seed=active_seeds[fid],
            bank_questions=questions,
            bank_digest=bank_digest,
            bank_verified=bank_verified,
            expected_bank_digest=live_digest,
            prng_contract_digest=prng_contract_digest,
            spec=spec,
            allow_ephemeral=False,
            avoid_families_by_slot=used_families_by_slot,
            avoid_instances_by_slot=used_instances_by_slot,
        )
        if res['status'] == 'AVAILABLE':
            manifest = res['manifest']
            forms_out.append(manifest)
            for sl in manifest['slots']:
                used_families_by_slot.setdefault(sl['slot_id'], [])
                if sl['family_id'] not in used_families_by_slot[sl['slot_id']]:
                    used_families_by_slot[sl['slot_id']].append(sl['family_id'])
                used_instances_by_slot.setdefault(sl['slot_id'], [])
                if sl['instance_id'] not in used_instances_by_slot[sl['slot_id']]:
                    used_instances_by_slot[sl['slot_id']].append(sl['instance_id'])
        else:
            shortages_out.append(res['shortage'])
            forms_out.append(res['shortage'])

    island = {
        'schema_version': 1,
        'island_id': 'sim-forms',
        'owner': 'N24',
        'status': 'assembled' if not shortages_out else 'shortage',
        'epistemic_label': 'PROPOSED',
        'epistemic_note_lv': (
            'PROPOSED treniņsimulatora mācību politika: formas A, B un C (21 vieta, 100 punkti). '
            'Nav oficiāls RSU kolokvija eksāmens un nepiešķir oficiālu vērtējumu.'
        ),
        'policy_id': POLICY_ID,
        'prng_contract_digest': prng_contract_digest,
        'bank_digest': bank_digest,
        'bank_embedded_digest': bank_embedded_digest,
        'required_types_per_form': spec['required_types'],
        'forms': forms_out,
        'shortages': shortages_out,
        'conflicts': [
            {
                'id': 'N23-C01',
                'status': 'documented-and-visible',
                'slot_id': 'S7-3',
                'slot_points': 5,
                'bank_rubric_points': 9,
                'note_lv': (
                    'FAM-7C un FAM-7D bankas rubrikas nes 9 punktus, kamēr S7-3 plāna vieta nosaka 5 punktus; '
                    'montāža izmanto slota punktu skalu (kopā 100) un saglabā konfliktu redzamu.'
                ),
            },
            {
                'id': 'N24-C01',
                'status': 'documented-and-visible',
                'singleton_slots_count': 14,
                'flexible_slots_count': 7,
                'note_lv': (
                    'Plāns docs/SIMULATION_BLUEPRINT.json 14 vietām atļauj tikai vienu saimi, tāpēc tajās '
                    'formas A/B/C rotē variantus (instances); 7 elastīgajās vietās neviena saime neatkārtojas visās 3 formās.'
                ),
            },
        ],
    }
    return island
