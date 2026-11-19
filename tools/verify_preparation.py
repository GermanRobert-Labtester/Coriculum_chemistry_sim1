#!/usr/bin/env python3
"""Verify preparation artifacts only. Never builds or modifies imported products.

Default is read-only; --report writes only the specified destination-local report.
Checks source inventory/hashes, copies, programme identity, planning contracts,
coverage anchors, local documentation links and independent exemplar arithmetic.

Two modes, one contract:

  The PASS criterion is the **published snapshot's integrity**: every one of the
  174 COPY_MANIFEST destinations must match the manifest's own recorded size and
  SHA-256, the published set must be exactly the declared set, and the programme,
  design and exemplar checks must hold. This is what this repository can
  guarantee about itself, and it is asserted in every mode.

  The live sibling Chemistry_1 through Chemistry_7 trees are *compared* and their
  divergence is *reported* — per file, with both digests, both sizes and the
  source mtime — but a divergence is not a failure. Those workspaces are
  actively developed and keep advancing after publication; an upstream advance
  is not damage to this repository's published snapshot, and treating it as a
  failure would make the published artifact unverifiable the moment its author
  edits an upstream file. `--strict-sibling` restores the stronger contract,
  where any source divergence or preservation-baseline drift fails the run.

  Nothing here writes to a sibling workspace. AGENTS.md forbids it, and the
  published copies are this repository's own frozen snapshot.

--repo-local selects a published-repository-only mode: the 174 COPY_MANIFEST
destinations are checked against the manifest's own recorded hashes and totals
without dereferencing the unpublished sibling Chemistry_1 through Chemistry_7
trees at all. It emits its own scoped record and never overwrites the full-workspace
evidence/PREPARATION_VERIFICATION.json.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import math
import platform
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

DEST = Path(__file__).resolve().parents[1]
ROOT = DEST.parent
FAILURES: list[str] = []
CHECKS: dict[str, object] = {}

# Frozen identities recorded by the preparation inspection (2026-11-16).
EXPECTED_MANIFEST_FILES = 174
EXPECTED_MANIFEST_BYTES = 30_083_827
EXPECTED_MANIFEST_ROLES = {'canonical-master': 7, 'course-source': 35, 'supporting-reference-data': 65,
                           'planning-reference': 18, 'archived-governance-reference': 49}
# COPY_MANIFEST hashes are lowercase hex SHA-256 digests. The inspection quoted the manifest
# digest as the 16-character prefix 07d49735060796c3; comparators accept any 4-64 character
# lowercase hex prefix so a short recorded style is honored rather than silently redefined.
HASH_PREFIX = re.compile(r'^[0-9a-f]{4,64}$')

def hash_matches(recorded: str, computed: str) -> bool:
    if not HASH_PREFIX.fullmatch(recorded):
        return False
    return computed == recorded if len(recorded) == 64 else computed.startswith(recorded)

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)

def load(rel: str):
    return json.loads((DEST / rel).read_text(encoding='utf-8'))

class HTMLInventory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.local_resources: list[str] = []
        self.remote_resources: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get('id'):
            self.ids.add(values['id'])
        # Hyperlinks can be reference text; only loaded resources are audited here.
        keys = ['src', 'poster']
        if tag == 'link':
            keys.append('href')
        if tag == 'object':
            keys.append('data')
        for key in keys:
            value = values.get(key, '')
            if not value or value.startswith(('#', 'data:')):
                continue
            if value.startswith(('https:', 'http:', '//')):
                self.remote_resources.append(value)
            else:
                self.local_resources.append(value)

def verify_copies(repo_local: bool = False, strict_sibling: bool = False):
    data = load('COPY_MANIFEST.json')
    if not repo_local:
        check(data['destination'] == str(DEST), 'Manifest destination differs from actual workspace')
    roles: dict[str, int] = {}
    destinations: set[str] = set()
    masters: dict[int, HTMLInventory] = {}
    hash_matches_count = 0
    divergence: list[dict[str, object]] = []
    sibling_available = False
    for item in data['files']:
        dst_rel = item['destination']
        dst = DEST / dst_rel
        src = None if repo_local else ROOT / item['source']
        check(dst_rel not in destinations, f'Duplicate copied path: {dst_rel if repo_local else dst}')
        destinations.add(dst_rel)
        if repo_local:
            check(dst.is_file(), f'Missing published file: {dst_rel}')
            if not dst.is_file():
                continue
        else:
            check(dst.is_file(), f'Missing published file: {dst_rel}')
            if not dst.is_file():
                continue
            if src is not None and src.is_file():
                sibling_available = True
        # The published snapshot's own integrity: the copy must match the manifest.
        # This is the PASS criterion in every mode.
        published_bytes = dst.stat().st_size
        published_sha = sha(dst)
        if published_bytes != item['bytes']:
            check(False, f'Published size differs from the manifest: {dst_rel}')
        if hash_matches(item['sha256'], published_sha):
            hash_matches_count += 1
        else:
            check(False, f'Published hash differs from the manifest: {dst_rel}')
        if not repo_local and src is not None and src.is_file():
            # The upstream comparison: reported, and failed only under --strict-sibling.
            source_bytes = src.stat().st_size
            source_sha = sha(src)
            if source_sha != published_sha or source_bytes != published_bytes:
                entry = {
                    'source': item['source'],
                    'destination': dst_rel,
                    'role': item['role'],
                    'source_sha256': source_sha,
                    'source_bytes': source_bytes,
                    'source_mtime_utc': datetime.fromtimestamp(
                        src.stat().st_mtime, tz=timezone.utc).isoformat(),
                    'published_sha256': published_sha,
                    'published_bytes': published_bytes,
                    'manifest_sha256': item['sha256'],
                    'manifest_bytes': item['bytes'],
                    'published_matches_manifest': hash_matches(item['sha256'], published_sha),
                }
                divergence.append(entry)
                if strict_sibling:
                    check(False, f'Copy size mismatch: {dst}')
                    check(False, f'Copy hash mismatch: {dst}')
        roles[item['role']] = roles.get(item['role'], 0) + 1
        if item['role'] == 'canonical-master':
            topic = int(Path(item['source']).parts[0].split('_')[1])
            text = dst.read_text(encoding='utf-8')
            parser = HTMLInventory()
            parser.feed(text)
            masters[topic] = parser
            check(not parser.remote_resources, f'Master loads remote resource: {dst_rel if repo_local else dst}')
            for ref in parser.local_resources:
                where = f'{dst_rel}: {ref}' if repo_local else ref
                check((dst.parent / unquote(urlsplit(ref).path)).is_file(), f'Missing master resource: {where}')
    check(len(data['files']) == EXPECTED_MANIFEST_FILES, f'Expected {EXPECTED_MANIFEST_FILES} copied reference files')
    check(roles == EXPECTED_MANIFEST_ROLES, 'Copied role counts differ')
    check(set(masters) == set(range(1, 8)), 'Missing one or more topic masters')
    copies_check = {'files': len(data['files']), 'bytes': sum(x['bytes'] for x in data['files']), 'roles': roles,
                    'manifest_sha256': sha(DEST / 'COPY_MANIFEST.json'),
                    'master_resource_check': 'Static loaded-resource attributes only; no browser acceptance'}
    # The published set is asserted against the manifest in every mode: the declared
    # set must be exactly the published set, and the declared byte total must hold.
    check(copies_check['bytes'] == EXPECTED_MANIFEST_BYTES,
          f"Published byte total differs from {EXPECTED_MANIFEST_BYTES}")
    hash_lengths = sorted({len(item['sha256']) for item in data['files']})
    hash_format_ok = all(HASH_PREFIX.fullmatch(item['sha256']) for item in data['files'])
    check(hash_format_ok, 'COPY_MANIFEST contains a non-lowercase-hex SHA-256 value')
    archives = {rel.split('/')[0] for rel in destinations}
    published = set()
    for top in sorted(archives):
        base = DEST / top
        if base.is_dir():
            published |= {str(path.relative_to(DEST)) for path in base.rglob('*') if path.is_file()}
    undeclared = sorted(published - destinations)
    absent = sorted(destinations - published)
    check(not undeclared, f'Published files not declared in COPY_MANIFEST: {undeclared[:5]}')
    check(not absent, f'Declared files absent from the published set: {absent[:5]}')
    committed_manifest_sha = None
    committed = DEST / 'evidence/PREPARATION_VERIFICATION.json'
    if committed.is_file():
        try:
            committed_manifest_sha = json.loads(committed.read_text(encoding='utf-8'))[
                'checks']['copies']['manifest_sha256']
        except (KeyError, ValueError, TypeError):
            committed_manifest_sha = None
    copies_check.update({
        'hash_matches': hash_matches_count,
        'hash_format': {'algorithm': 'sha256', 'recorded_lengths': hash_lengths,
                        'all_lowercase_hex': hash_format_ok,
                        'inspection_prefix_example': '07d49735060796c3',
                        'rule': 'Full 64-character digests compare by equality; shorter lowercase hex values compare as prefixes'},
        'published_set': {'declared': len(destinations), 'enumerated': len(published),
                          'undeclared': undeclared, 'absent': absent,
                          'published_matches_manifest': hash_matches_count == len(destinations)},
        'manifest_destination_recorded': data['destination'],
        'manifest_matches_committed_record': (committed_manifest_sha == copies_check['manifest_sha256']
                                              if committed_manifest_sha else None),
    })
    if repo_local:
        copies_check['sibling_source_identity'] = 'NOT ASSERTED in repository-local mode'
    else:
        copies_check.update({
            'sibling_source_identity': ('Compared and reported; a divergence is not a failure '
                                        'unless --strict-sibling is given'
                                        if not strict_sibling else
                                        'Asserted as identical (--strict-sibling)'),
            'sibling_available': sibling_available,
            'upstream_divergence': {
                'files': len(divergence),
                'status': ('NONE' if not divergence else
                           ('REPORTED' if not strict_sibling else 'FAILED')),
                'meaning': 'The live sibling Chemistry_1 through Chemistry_7 trees advanced after '
                           'publication. The published copies still match COPY_MANIFEST.json; the '
                           'upstream files moved on. Re-importing them is a decision for the task '
                           'that owns the sibling workspace, because the published master digest is '
                           'cited by the coverage island, the golden vectors, the method cards, the '
                           'topic-4 family templates and the frozen bank.',
                'entries': divergence,
            },
        })
    CHECKS['copies'] = copies_check
    return masters


def verify_preservation(strict_sibling: bool = False):
    baseline = load('evidence/source_workspace_baseline.json')
    before = baseline['files']
    current: set[str] = set()
    changed = []
    for n in range(1, 8):
        tree = ROOT / f'Chemistry_{n}'
        if not tree.is_dir():
            continue
        for path in tree.rglob('*'):
            if path.is_file() and not path.is_symlink():
                rel = str(path.relative_to(ROOT))
                current.add(rel)
                if rel not in before:
                    continue
                stat = path.stat()
                old = before[rel]
                if stat.st_size != old['bytes'] or stat.st_mtime_ns != old['mtime_ns'] or sha(path) != old['sha256']:
                    changed.append(rel)
    added, missing = sorted(current - set(before)), sorted(set(before) - current)
    sibling_available = bool(current)
    if strict_sibling:
        check(not changed and not added and not missing, 'Source workspace changed: see preservation details')
    CHECKS['preservation'] = {'regular_files': len(before), 'changed': changed, 'added': added, 'missing': missing,
      'compared_fields': ['relative path', 'bytes', 'mtime_ns', 'sha256'],
      'baseline_captured_utc': baseline['captured_utc'], 'baseline_sha256': sha(DEST / 'evidence/source_workspace_baseline.json'),
      'scope': 'All regular non-symlink files under Chemistry_1 through Chemistry_7',
      'status': ('ASSERTED' if strict_sibling else
                 ('DRIFT_REPORTED' if (changed or added or missing) else 'UNCHANGED')),
      'meaning': ('The live sibling trees are compared with the inspection-time baseline. The '
                  'baseline describes the source workspaces as they were at inspection; those '
                  'workspaces keep being edited afterwards, so a difference is an upstream '
                  'advance rather than damage to this repository. It fails the run only under '
                  '--strict-sibling.'),
      'sibling_available': sibling_available,
      'changed_count': len(changed), 'added_count': len(added), 'missing_count': len(missing)}

def verify_programme():
    path = DEST / 'RSU_MedChem_Colloq1_Prog_LV_2025.pdf'
    expected = 'f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9'
    check(path.is_file() and sha(path) == expected, 'Programme PDF identity mismatch')
    text = (DEST / 'evidence/programme_extracted.txt').read_text()
    check('180 minūtes' in text and '2025' in text, 'Programme extraction misses time/year')
    CHECKS['programme'] = {'sha256': sha(path), 'bytes': path.stat().st_size, 'pages_inspected': 4,
                           'year': 2025, 'page_render_review': 'Four Poppler PNGs directly inspected during preparation'}

def verify_plan():
    text = (DEST / 'MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md').read_text()
    sections = re.findall(r'^## (\d+)\.', text, re.M)
    check(sections == [str(i) for i in range(1, 15)], 'Roadmap sections are not exactly 1 through 14')
    for prefix, count in [('T', 20), ('F', 10), ('B', 5)]:
        ids = re.findall(rf'^### ({prefix}\d{{2}}) —', text, re.M)
        check(ids == [f'{prefix}{i:02}' for i in range(1, count + 1)], f'Roadmap {prefix} cards differ')
    for i in range(1, 21):
        tid = f'T{i:02}'
        card = text.split(f'### {tid} —', 1)[1].split('\n### ', 1)[0].split('\n## ', 1)[0]
        check(len(re.findall(r'^\d\. ', card, re.M)) == 3, f'{tid}: expected 3 main steps')
        for sub in (1, 2):
            check(re.findall(rf'^- \*\*{tid}\.{sub}\.(\d):', card, re.M) == ['1', '2', '3'],
                  f'{tid}.{sub}: expected exactly 3 substeps')
        for label in ['**Affected targets:**', '**Acceptance / positive-negative boundary:**', '**Rollback:**', '**Done:**']:
            check(label in card, f'{tid}: missing execution-card field {label}')
    # No malformed tables caused by blank lines between individual rows.
    for rel in ['README.md', 'MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md', 'docs/QUESTION_TYPES_AND_VARIANTS.md']:
        doc = (DEST / rel).read_text()
        check(not re.search(r'(?m)^\|[^\n]*\n\n\|', doc), f'Malformed separated table rows in {rel}')
        for target in re.findall(r'\]\((<[^>]+>|[^)]+)\)', doc):
            target = target.strip('<>')
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            path = (DEST / rel).parent / unquote(urlsplit(target).path)
            # This report may be created by the current run.
            check(path.exists() or path == DEST / 'evidence/PREPARATION_VERIFICATION.json', f'Broken document link: {rel}: {target}')
    CHECKS['roadmap'] = {'sections': len(sections), 'core_tasks': 20, 'feature_proposals': 10,
                        'diagnostics': 5, 'core_card_shape': '3 main steps; 2 subtasks with 3 substeps each',
                        'sha256': sha(DEST / 'MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md')}

def verify_data(masters, repo_local: bool = False):
    families = load('docs/QUESTION_FAMILIES.json')['families']
    family_ids = {f['family_id'] for f in families}
    check(len(families) == len(family_ids) == 28, 'Expected 28 unique question families')
    schema = load('docs/QUESTION_SCHEMA.json')
    type_ids = set(schema['properties']['type_ids']['items']['enum'])
    check(type_ids == {f'Q{i:02}' for i in range(1, 19)}, 'Question-type enum differs')
    with (DEST / 'docs/PROGRAMME_COVERAGE_MATRIX.csv').open(newline='') as stream:
        coverage = list(csv.DictReader(stream))
    outcome_ids = {r['outcome_id'] for r in coverage}
    check(len(coverage) == len(outcome_ids) == 64, 'Expected 64 distinct coverage rows')
    check({int(r['programme_topic']) for r in coverage} == set(range(1, 8)), 'Coverage missing a topic')
    for row in coverage:
        topic = int(row['programme_topic'])
        if repo_local and topic not in masters:
            check(False, f"Missing published master for coverage topic {topic}; anchor not checked")
            continue
        check((DEST / row['master_path']).is_file(), f"Missing coverage master: {row['outcome_id']}")
        check(row['master_anchor'] in masters[topic].ids, f"Missing coverage anchor: {row['outcome_id']} #{row['master_anchor']}")
        for fid in row['planned_families'].split(';'):
            check(fid in family_ids, f'Unknown coverage family: {fid}')
    covered = set()
    for family in families:
        check([v['variant_id'] for v in family['variants']] == list('ABCD'), f"Variant labels differ: {family['family_id']}")
        check(len({v['specification_lv'] for v in family['variants']}) == 4, 'Duplicate variant specification')
        check(set(family['question_types']) <= type_ids, 'Unknown family question type')
        for rid in family['programme_outcomes']:
            check(rid in outcome_ids, f'Unknown family outcome: {rid}')
            covered.add(rid)
            row = next(r for r in coverage if r['outcome_id'] == rid)
            check(family['family_id'] in row['planned_families'].split(';'), 'Asymmetric family/outcome mapping')
    check(covered == outcome_ids, 'Unmapped programme outcomes')
    check(set(t for f in families for t in f['question_types']) == type_ids, 'Unused question types')
    bp = load('docs/SIMULATION_BLUEPRINT.json')
    check(len(bp['slots']) == 21 and len({s['slot_id'] for s in bp['slots']}) == 21, 'Expected 21 unique form slots')
    check(sum(s['points'] for s in bp['slots']) == bp['points'] == 100, 'Form points differ')
    check(sum(x['working_minutes'] for x in bp['topic_weights']) == bp['working_minutes'] == 170, 'Working duration differs')
    check(bp['working_minutes'] + bp['review_minutes'] == 180, 'Proposed duration exceeds 180 minutes')
    for row in bp['topic_weights']:
        slots = [s for s in bp['slots'] if s['topic'] == row['topic']]
        check(len(slots) == 3 and sum(s['points'] for s in slots) == row['points'], 'Per-topic form total differs')
    for slot in bp['slots']:
        check(set(slot['allowed_family_ids']) <= family_ids, 'Unknown form family')
    # Validate the proposed schema itself if the already-installed library exists.
    schema_status = 'JSON parsed; semantic instance validator is a future T04 task'
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        pass
    else:
        Draft202012Validator.check_schema(schema)
        schema_status = 'Draft 2020-12 schema structure checked with installed jsonschema; no release instances exist'
    CHECKS['design_data'] = {'coverage_rows': len(coverage), 'core_programme_paraphrase_rows': sum(r['requirement_kind'] == 'programme-paraphrase' for r in coverage),
        'supplementary_application_rows': sum(r['requirement_kind'] == 'application-detail' for r in coverage),
        'families': len(families), 'variant_specifications': sum(len(f['variants']) for f in families),
        'question_types': len(type_ids), 'slots': len(bp['slots']), 'points': bp['points'],
        'minutes': bp['working_minutes'] + bp['review_minutes'], 'schema_check': schema_status,
        'scope': 'Specifications only; no 112-item release bank or three assembled forms yet'}

def verify_examples():
    examples = load('docs/EXAMPLE_QUESTIONS.json')['examples']
    by_id = {e['example_id']: e for e in examples}
    check(len(examples) == len(by_id) == 14, 'Expected 14 distinct examples')
    check(all(sum(e['topic'] == n for e in examples) == 2 for n in range(1, 8)), 'Expected 2 examples per topic')
    # Independent reference calculations: do not import copied code or expected keys.
    calculated = {
      'EX01': {'n_Mg_mol': 4.80/24.0, 'm_MgO_g': 4.80/24.0*40.0},
      'EX03': {'delivered_mL': 18.40-2.15},
      'EX04': {'mass_mg': 0.00450*1e6, 'product': 2.50*3.42},
      'EX05': {'n_mol': 2.922/58.44, 'c_mol_L': (2.922/58.44)/(250.0/1000)},
      'EX06': {'V1_mL': 0.0500*100.0/0.500},
      'EX07': {'delta_G_kJ_mol': 40.0-298*(150/1000), 'boundary_T_K': 40000/150},
      'EX08': {'q_solution_J': 100.0*4.18*5.00, 'q_reaction_J': -100.0*4.18*5.00},
      'EX09': {'half_life_min': 30, 'k_min_inverse': math.log(2)/30, 'm90_mg': 80*2**(-90/30)},
      'EX10': {'Ea_uncatalysed_kJ_mol': 100-20, 'Ea_catalysed_kJ_mol': 60-20, 'delta_H_kJ_mol': -10-20},
      'EX11': {'n_MnO4_mol': 0.02000*18.60/1000, 'c_Fe_mol_L': 5*0.02000*18.60/25.00},
      'EX12': {'Q': 1/0.0100, 'n': 2, 'E_V': 0.340-(0.05916/2)*math.log10(1/0.0100)},
      'EX13': {'slope_mL_mg': (0.610-0.010)/(0.012-0), 'intercept': 0.010,
               'gamma_measured_mg_mL': (0.350-0.010)/50},
      'EX14': {'gamma_original_mg_mL': (0.350-0.010)/50*5,
               'mass_mg': (0.350-0.010)/50*5*25,
               'n_mol': ((0.350-0.010)/50*5*25/1000)/376.36},
    }
    for eid, values in calculated.items():
        for name, value in values.items():
            expected = by_id[eid]['expected'][name]
            check(math.isclose(value, expected, rel_tol=1e-10, abs_tol=1e-12), f'Example arithmetic mismatch: {eid}.{name}')
    # Independent atom and charge inventory for EX11's net redox equation.
    species = {
      'MnO4': ({'Mn': 1, 'O': 4}, -1), 'H': ({'H': 1}, 1), 'Fe2': ({'Fe': 1}, 2),
      'Mn2': ({'Mn': 1}, 2), 'water': ({'H': 2, 'O': 1}, 0), 'Fe3': ({'Fe': 1}, 3)}
    def counts(side):
        result = {'charge': 0}
        for species_id, coefficient in side.items():
            atoms, charge = species[species_id]
            result['charge'] += coefficient*charge
            for atom, number in atoms.items():
                result[atom] = result.get(atom, 0)+coefficient*number
        return result
    check(counts({'MnO4': 1, 'H': 8, 'Fe2': 5}) == counts({'Mn2': 1, 'water': 4, 'Fe3': 5}), 'EX11 atom/charge imbalance')
    for example in examples:
        check(bool(example['rubric']) and all(r['points'] > 0 for r in example['rubric']), 'Invalid example rubric')
    CHECKS['examples'] = {'examples': len(examples), 'independently_recomputed_numeric_examples': len(calculated),
                         'numeric_fields_checked': sum(map(len, calculated.values())), 'net_redox_atom_charge_balance': True,
                         'limit': 'Arithmetic and one structured balance; no official-key, complete scientific or learner-trial acceptance'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=str, help='Optional JSON report path within this workspace')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--repo-local', action='store_true',
                       help='Verify only the published repository: the 174 manifest destinations and their '
                            'recorded hashes, without dereferencing sibling Chemistry_1 through Chemistry_7 trees')
    mode.add_argument('--strict-sibling', action='store_true',
                       help='Restore the stronger contract: a divergence between the live sibling source and '
                            'the published copy, or a drift against the source-workspace baseline, fails the run')
    args = parser.parse_args()
    masters = verify_copies(repo_local=args.repo_local, strict_sibling=args.strict_sibling)
    if args.repo_local:
        CHECKS['preservation'] = {
            'status': 'NOT ASSERTED',
            'reason': 'Requires the unpublished sibling Chemistry_1 through Chemistry_7 trees and their baseline',
            'scope': 'All regular non-symlink files under Chemistry_1 through Chemistry_7'}
    else:
        verify_preservation(strict_sibling=args.strict_sibling)
    verify_programme()
    verify_plan()
    verify_data(masters, repo_local=args.repo_local)
    verify_examples()
    if args.repo_local:
        scope = ('Repository-local: published file set only (174 COPY_MANIFEST destinations and their recorded '
                 'hashes/totals); sibling source trees and the 15,978-file preservation baseline are not asserted')
    elif args.strict_sibling:
        scope = ('Full workspace with the strict sibling contract: the published copies must be identical to the '
                 'live Chemistry_1 through Chemistry_7 sources and to the manifest, and the source trees must '
                 'match the inspection-time baseline')
    else:
        scope = ('Published-snapshot integrity (174 COPY_MANIFEST destinations against the manifest) plus the '
                 'programme, design and exemplar checks. The live sibling trees are compared and their '
                 'divergence is reported, not failed: they are actively developed workspaces that advance '
                 'after publication, and an upstream advance is not damage to this repository. '
                 '--strict-sibling restores the stronger contract.')
    report = {'schema_version': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(),
      'scope': scope,
      'status': 'PASS' if not FAILURES else 'FAIL', 'checks': CHECKS, 'failures': FAILURES,
      'not_performed': ['Simulator runtime', 'Browser rendering of masters/application', 'Accessibility/assistive technology',
                        'Assessment paper/PDF rendering', 'Full chemistry/source verification', 'Student/instructor trial']}
    if args.repo_local:
        report['mode'] = 'repo-local'
        report['environment'] = {'python': sys.version.split()[0], 'platform': platform.platform(),
                                 'workspace': str(DEST)}
        report['not_asserted'] = [
            'Source-to-copy identity against the sibling Chemistry_1 through Chemistry_7 trees',
            'The 15,978-file source-workspace preservation baseline (evidence/source_workspace_baseline.json)',
            'Full-workspace default-mode PASS issued from a clean clone (the siblings are not published)']
        report['not_performed'] = report['not_performed'] + report['not_asserted']
    else:
        report['mode'] = 'strict-sibling' if args.strict_sibling else 'published-snapshot'
        report['environment'] = {'python': sys.version.split()[0], 'platform': platform.platform(),
                                 'workspace': str(DEST)}
        report['contract'] = {
            'pass_criterion': 'Every published copy matches COPY_MANIFEST.json (size and SHA-256); the published '
                              'set is exactly the declared set; the programme, design and exemplar checks hold.',
            'reported_not_failed': 'A divergence between a live sibling source file and its published copy, and a '
                                   'drift against the source-workspace baseline.',
            'strict_flag': '--strict-sibling turns the reported divergence into a failure.',
        }
        report['not_asserted'] = [
            'That the live sibling Chemistry_1 through Chemistry_7 trees still match the published copies '
            '(reported under checks.copies.upstream_divergence instead)',
            'That the live sibling trees still match the inspection-time source-workspace baseline '
            '(reported under checks.preservation instead)']
        report['not_performed'] = report['not_performed'] + report['not_asserted']
    if args.report:
        path = (DEST / args.report).resolve()
        if not path.is_relative_to(DEST) or path.suffix != '.json':
            raise ValueError('Report must be a JSON file inside this workspace')
        # Do not allow a report path to overwrite source or planning inputs. Each mode has its own
        # record so a repository-local PASS can never overwrite the committed full-workspace PASS.
        allowed = 'evidence/REPO_LOCAL_VERIFICATION.json' if args.repo_local else 'evidence/PREPARATION_VERIFICATION.json'
        if path != (DEST / allowed).resolve():
            raise ValueError(f'Only {allowed} is an allowed report target for this mode')
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(FAILURES)

if __name__ == '__main__':
    raise SystemExit(main())
