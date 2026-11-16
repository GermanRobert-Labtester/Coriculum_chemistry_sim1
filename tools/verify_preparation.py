#!/usr/bin/env python3
"""Verify preparation artifacts only. Never builds or modifies imported products.

Default is read-only; --report writes only the specified destination-local report.
Checks source inventory/hashes, copies, programme identity, planning contracts,
coverage anchors, local documentation links and independent exemplar arithmetic.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

DEST = Path(__file__).resolve().parents[1]
ROOT = DEST.parent
FAILURES: list[str] = []
CHECKS: dict[str, object] = {}

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

def verify_copies():
    data = load('COPY_MANIFEST.json')
    check(data['destination'] == str(DEST), 'Manifest destination differs from actual workspace')
    roles: dict[str, int] = {}
    destinations: set[str] = set()
    masters: dict[int, HTMLInventory] = {}
    for item in data['files']:
        src, dst = ROOT / item['source'], DEST / item['destination']
        check(item['destination'] not in destinations, f'Duplicate copied path: {dst}')
        destinations.add(item['destination'])
        check(src.is_file() and dst.is_file(), f'Missing copied/source file: {dst}')
        if not src.is_file() or not dst.is_file():
            continue
        check(src.stat().st_size == dst.stat().st_size == item['bytes'], f'Copy size mismatch: {dst}')
        check(sha(src) == sha(dst) == item['sha256'], f'Copy hash mismatch: {dst}')
        roles[item['role']] = roles.get(item['role'], 0) + 1
        if item['role'] == 'canonical-master':
            topic = int(Path(item['source']).parts[0].split('_')[1])
            text = dst.read_text(encoding='utf-8')
            parser = HTMLInventory()
            parser.feed(text)
            masters[topic] = parser
            check(not parser.remote_resources, f'Master loads remote resource: {dst}')
            for ref in parser.local_resources:
                check((dst.parent / unquote(urlsplit(ref).path)).is_file(), f'Missing master resource: {ref}')
    check(len(data['files']) == 174, 'Expected 174 copied reference files')
    check(roles == {'canonical-master': 7, 'course-source': 35, 'supporting-reference-data': 65,
                    'planning-reference': 18, 'archived-governance-reference': 49}, 'Copied role counts differ')
    check(set(masters) == set(range(1, 8)), 'Missing one or more topic masters')
    CHECKS['copies'] = {'files': len(data['files']), 'bytes': sum(x['bytes'] for x in data['files']), 'roles': roles,
                        'manifest_sha256': sha(DEST / 'COPY_MANIFEST.json'),
                        'master_resource_check': 'Static loaded-resource attributes only; no browser acceptance'}
    return masters

def verify_preservation():
    baseline = load('evidence/source_workspace_baseline.json')
    before = baseline['files']
    current: set[str] = set()
    changed = []
    for n in range(1, 8):
        for path in (ROOT / f'Chemistry_{n}').rglob('*'):
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
    check(not changed and not added and not missing, 'Source workspace changed: see preservation details')
    CHECKS['preservation'] = {'regular_files': len(before), 'changed': changed, 'added': added, 'missing': missing,
      'compared_fields': ['relative path', 'bytes', 'mtime_ns', 'sha256'],
      'baseline_captured_utc': baseline['captured_utc'], 'baseline_sha256': sha(DEST / 'evidence/source_workspace_baseline.json'),
      'scope': 'All regular non-symlink files under Chemistry_1 through Chemistry_7'}

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

def verify_data(masters):
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
    args = parser.parse_args()
    masters = verify_copies()
    verify_preservation()
    verify_programme()
    verify_plan()
    verify_data(masters)
    verify_examples()
    report = {'schema_version': 1, 'checked_utc': datetime.now(timezone.utc).isoformat(),
      'scope': 'Workspace preparation only; not simulator implementation or product acceptance',
      'status': 'PASS' if not FAILURES else 'FAIL', 'checks': CHECKS, 'failures': FAILURES,
      'not_performed': ['Simulator runtime', 'Browser rendering of masters/application', 'Accessibility/assistive technology',
                        'Assessment paper/PDF rendering', 'Full chemistry/source verification', 'Student/instructor trial']}
    if args.report:
        path = (DEST / args.report).resolve()
        if not path.is_relative_to(DEST) or path.suffix != '.json':
            raise ValueError('Report must be a JSON file inside this workspace')
        # Do not allow a report path to overwrite source or planning inputs.
        if path.parent != DEST / 'evidence' or path.name != 'PREPARATION_VERIFICATION.json':
            raise ValueError('Only evidence/PREPARATION_VERIFICATION.json is an allowed report target')
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return bool(FAILURES)

if __name__ == '__main__':
    raise SystemExit(main())
