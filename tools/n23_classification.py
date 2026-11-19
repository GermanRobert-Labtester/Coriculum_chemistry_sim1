#!/usr/bin/env python3
"""N23 classification sweep: the behavioural proof of the mapping's totality.

This is roadmap Main Step B.1.2. The build gate (tools/validate_n23_grading.py)
proves the classification island is *structurally* total over the frozen
vocabularies; this runner proves it *behaviourally* over a scripted error corpus.

What it does
------------
1. Enumerates the required coverage set from the frozen sources:
   N17 error-taxonomy classes, the N17 fallback, the N17 conservation signature,
   the N19 14-entry signature_registry, the N18 error_class_vocabulary, every
   `misconception_signatures[]` value across the 112 bank instances, the N22
   error surfaces and the five N23 slot states. Every family must have a
   mapping entry — zero unmapped.
2. Compiles `src/feedback.ts` into a throw-away directory with the pinned
   strict compiler options (offline, `npx --no-install tsc`) and loads it with
   the frozen engines in a Node `vm` sandbox, copying the mechanics of
   `tools/check_n22_runtime.js` (`makeSandbox` + island pseudo-DOM).
3. Runs the scripted error corpus through the frozen engines directly — the
   N17 quantity engine, the N19 method engines, the N18 graph scorer and the
   N17 conservation balance — builds the minimal GRADING_FORMAT §4 core record
   for each scripted slot, and drives `SimFeedback.assemble`.
4. Asserts zero unmapped signatures, unresolved concept/chain/card ids and
   missing term keys across the whole corpus, and records the priority-ordered
   multi-signature and ordering fixtures verbatim.
5. Writes evidence/N23_CLASSIFICATION_TABLE.json with the coverage table, the
   sweep rows, the fixtures, the module/island digests and a two-run
   byte-identical parity flag (records are timestamp-free).

The runner does not grade a session, does not claim an official examination and
does not replace the build gate: it is the behavioural half of the same totality
claim, with the N09 gap kept visible in the island it reads.

Usage:
    python3 tools/n23_classification.py [--report PATH] [--work-dir PATH]
                                        [--tsc PATH]

Exit code is non-zero on any unmapped family, unresolved link, missing term
key, island/module digest disagreement or non-identical second run.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

ROOT = DEST
ISLAND_PATH = 'data/feedback_classification.json'
MODULE_PATH = 'src/feedback.ts'
DEFAULT_REPORT = 'evidence/N23_CLASSIFICATION_TABLE.json'
DEFAULT_WORK = Path('/tmp/opencode/n23-g2')
FIGURE_PATHS = [
    'data/figures_t12.json',
    'data/figures_t23.json',
    'data/figures_t4.json',
    'data/figures_t5.json',
    'data/figures_t67.json',
]
STATE_FAMILIES = ['UNATTEMPTED', 'MANUAL_PENDING', 'GRADED', 'INCOMPLETE', 'INVALID']


# --------------------------------------------------------------------------- #
# Corpus                                                                       #
# --------------------------------------------------------------------------- #

CASES = [
    {
        'id': 'NUM-THOUSAND-FOLD',
        'mechanism': 'quantity_numeric',
        'instance_id': 'COL1-5-5B-A-01',
        'submission': {'value': '250', 'unit': 'L/(mol·s)'},
        'note_lv': 'Tūkstoškārtīga kļūda: 0,250 vietā 250. Dziness atgriež OT (OUT_OF_TOLERANCE), '
                   'kas N17 taksonomijā pieder 3. klasei un nes paraksturu MC-3A-02.',
    },
    {
        'id': 'NUM-COMMA-MIXED-SEPARATOR',
        'mechanism': 'quantity_numeric',
        'instance_id': 'COL1-5-5B-A-01',
        'submission': {'value': '1,234.5', 'unit': 'L/(mol·s)'},
        'note_lv': 'Jaukts komats/punkts: latviešu decimālkomats kopā ar tūkstošu punktu nav '
                   'viena skaitļa gramatika, tāpēc 1. klase (MC-2B-02).',
    },
    {
        'id': 'NUM-MASS-VOLUME-NO-RHO',
        'mechanism': 'quantity_numeric',
        'instance_id': 'COL1-3-3C-A-01',
        'submission': {'value': '0.6', 'unit': 'g'},
        'note_lv': 'Blīvumu prasoša masa→tilpums pāreja: uzdevums prasa V₁ mL (0,600 mL), iesniegts '
                   '0,6 g; V-04 bloķē tiešu masas un tilpuma salīdzinājumu bez deklarēta ρ, tāpēc '
                   '2. klase (MC-3B-01) un instances satura modelis MC-3C-01.',
    },
    {
        'id': 'NUM-IMPLAUSIBLE-NEGATIVE',
        'mechanism': 'quantity_numeric',
        'instance_id': 'COL1-3-3B-A-01',
        'submission': {'value': '-5', 'unit': 'mol/L'},
        'note_lv': 'Negatīva koncentrācija ir fiziski neiespējama; skaitliskais vērtētājs to '
                   'atgriež kā OUT_OF_TOLERANCE ar to pašu 3. klases paraksturu MC-3A-02.',
    },
    {
        'id': 'CLASS-PHYSICAL-TAXONOMY',
        'mechanism': 'quantity_classify_probe',
        'instance_id': 'COL1-3-3B-A-01',
        'classify': {'raw': '-1.5', 'unit': 'g/L', 'expected_unit': 'g/L',
                     'rule_id': 'nonnegative_concentration'},
        'note_lv': 'Klasifikācijas zondējums: klasifikators atgriež taksonomijas klasi '
                   'PHYSICALLY_IMPLAUSIBLE; tas pats lielums caur grade() nāk kā OUT_OF_TOLERANCE. '
                   'Abi ceļi ir kartēti; šis ieraksts pārbauda taksonomijas skatu.',
    },
    {
        'id': 'CONSERVATION-IMBALANCE',
        'mechanism': 'conservation',
        'instance_id': None,
        'conservation': {
            'species_in': [{'id': 'Mg', 'mass_g': 4.8, 'moles': 0.2, 'nu': 1}],
            'species_out': [{'id': 'MgO', 'mass_g': 7.0, 'moles': 0.2, 'nu': 1}],
        },
        'source_ref': 'data/engine_taxonomy.json#/engine_vectors/conservation_vectors#EV-N17-CONS-03',
        'note_lv': 'Neviena bankas instance nenes konservācijas ierakstu, tāpēc šis gadījums '
                   'izmanto dzinēja paša sasaldēto vektoru EV-N17-CONS-03 (masa 4,8 g iepretim '
                   '7,0 g). Paraksturs MC-1C-01, nevis izdomāta instance.',
    },
    {
        'id': 'ORD-BANK-TRANSPOSE',
        'mechanism': 'method_instance',
        'instance_id': 'COL1-2-2A-A-01',
        'submission': {'order': ['S2', 'S1', 'S3', 'S4']},
        'note_lv': 'Bankas kārtošanas instance: divi soļi pārvietoti; N19 atgriež WRONG_ORDER un '
                   'instances noklusējuma paraksturu MC-2A-01.',
    },
    {
        'id': 'ORD-CARD-TRANSPOSE-PAIR',
        'mechanism': 'method_card_ordering',
        'card_id': 'MC-EX03',
        'submission': {'order': ['S1', 'S3', 'S2', 'S4', 'S5', 'S6']},
        'note_lv': 'Kartītes MC-EX03 transponēts pāris S2/S3: N19 atgriež divus remediation '
                   'ierakstus ar atšķirīgiem step_id un vienu unikālu paraksturu MC-2C-01.',
    },
    {
        'id': 'ORD-CARD-DOUBLE-TRANSPOSE',
        'mechanism': 'method_card_ordering',
        'card_id': 'MC-EX03',
        'submission': {'order': ['S2', 'S1', 'S4', 'S3', 'S5', 'S6']},
        'note_lv': 'Divi transponēti pāri vienā kartītes atbildē: četri remediation ieraksti; '
                   'paraksturs paliek viens, jo visi kartītes soļi dala MC-2C-01.',
    },
    {
        'id': 'ORD-CARD-BLANK',
        'mechanism': 'method_card_ordering',
        'card_id': 'MC-EX03',
        'submission': {'order': []},
        'note_lv': 'Tukša kārtošanas atbilde: BLANK_RESPONSE, nevis WRONG_ORDER.',
    },
    {
        'id': 'MATCH-WRONG-PAIRS',
        'mechanism': 'method_instance',
        'instance_id': 'COL1-1-1B-A-01',
        'submission': {'pairs': [
            {'left_id': 'L1', 'right_id': 'R1'},
            {'left_id': 'L2', 'right_id': 'R3'},
            {'left_id': 'L3', 'right_id': 'R2'},
        ]},
        'note_lv': 'Nepareizi saistīti pāri: WRONG_PAIRING, daļējs verdikts, MC-1B-01.',
    },
    {
        'id': 'MATCH-SYNONYM-ID',
        'mechanism': 'method_instance',
        'instance_id': 'COL1-1-1B-A-01',
        'submission': {'pairs': [
            {'left_id': 'L1', 'right_id': 'R1'},
            {'left_id': 'L2', 'right_id': 'Ūdens molekulas'},
        ]},
        'note_lv': 'Sinonīms teksta vietā: identitātes noteikums nozīmē, ka teksts nav id, tāpēc '
                   'pāris ir nezināms un verdikts WRONG_PAIRING.',
    },
    {
        'id': 'SEQ-DISTRACTOR-STEP',
        'mechanism': 'method_card_sequence',
        'card_id': 'MC-EX01',
        'prompt_id': 'SEQ-EX01-1',
        'submission': {'next_step_id': 'S1'},
        'note_lv': 'Secības distraktors: deklarētais kluču solis S1 atgriež savu paraksturu '
                   'MC-1C-01 un remediation ierakstu ar kartītes soli.',
    },
    {
        'id': 'SELF-BLANK',
        'mechanism': 'method_instance',
        'instance_id': 'COL1-1-1B-B-01',
        'submission': {'text': '   '},
        'note_lv': 'Tukšs pašnovērtējums: vienīgā teksta pārbaude (atstarpju tests) dod '
                   'BLANK_RESPONSE un 0 punktus; saturs netiek lasīts.',
    },
    {
        'id': 'SELF-NONBLANK-PENDING',
        'mechanism': 'method_instance',
        'instance_id': 'COL1-1-1B-B-01',
        'submission': {'text': 'MgCl2 šķīdumā disociē jonos.'},
        'note_lv': 'Nebalts pašnovērtējums paliek pending ar NONE kļūdu: assemble dod '
                   'gaidīšanas etiķeti, nevis kļūdas modeli.',
    },
    {
        'id': 'OPT-WRONG-SELECTION',
        'mechanism': 'quantity_option',
        'instance_id': 'COL1-1-1A-A-01',
        'submission': {'selected_ids': ['HOM']},
        'note_lv': 'Nepareiza variantu izvēle: WRONG_OPTION_SELECTION; instances saistītais '
                   'paraksturs MC-1A-01 tiek pievienots kā satura modelis.',
    },
    {
        'id': 'GRAPH-READ-OUT-OF-DOMAIN',
        'mechanism': 'graph_reading',
        'instance_id': 'COL1-2-2D-B-01',
        'submission': {'x': '90', 'value': '75'},
        'note_lv': 'Nolasījums ārpus datu diapazona (0–60 min): OUT_OF_DOMAIN_EXTRAPOLATION ar '
                   'validity klasi; N15 no-extrapolation mantojums.',
    },
    {
        'id': 'GRAPH-READ-INTERCEPT-DROP',
        'mechanism': 'graph_reading',
        'instance_id': 'COL1-7-7B-B-01',
        'submission': {'x': '0', 'value': '0.02'},
        'note_lv': 'Nolasījums krustpunktā (x = 0, A = 0,02) deklarētā diapazona iekšpusē, bet '
                   'ārpus absorbances tolerances: OUT_OF_TOLERANCE.',
    },
    {
        'id': 'GRAPH-DRAW-WRONG-DIRECTION',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [{'x': 0, 'y': 0.4003}, {'x': 0.016, 'y': 0}],
        'note_lv': 'Apvērsts asu virziens: līnijas slīpuma zīme neatbilst kalibrācijas taisnei, '
                   'tāpēc E_GRAPH_WRONG_DIRECTION.',
    },
    {
        'id': 'GRAPH-DRAW-DOUBLE-BACK',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [{'x': 0, 'y': 0}, {'x': 0.008, 'y': 0.2}, {'x': 0.004, 'y': 0.1},
                        {'x': 0.016, 'y': 0.4}],
        'draw_extra': {'path_reversals': 1},
        'note_lv': 'Zīmējums atgriežas atpakaļ pa savu ceļu (path_reversals = 1): '
                   'E_GRAPH_DOUBLE_BACK.',
    },
    {
        'id': 'GRAPH-DRAW-EMPTY',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [],
        'note_lv': 'Tukšs grafika iesniegums: E_GRAPH_EMPTY_SUBMISSION, nevis kluss nulle.',
    },
    {
        'id': 'GRAPH-DRAW-OUT-OF-AXIS',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [{'x': 0, 'y': 0}, {'x': 0.03, 'y': 0.4}],
        'note_lv': 'Atzīme ārpus attēla asu diapazona (x = 0,03 > 0,018): '
                   'E_GRAPH_OUT_OF_AXIS_RANGE.',
    },
    {
        'id': 'GRAPH-DRAW-NOT-ASSESSED',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [{'x': 0.017, 'y': 0}, {'x': 0.0175, 'y': 0.4}],
        'note_lv': 'Visi novilktie punkti ir asu iekšpusē, bet ārpus vērtējamā diapazona (0–0,016): '
                   'N18 atgriež not_assessed ar NOT_ASSESSED un nulles automātisko punktu, nevis '
                   'klusu tolerances neizpildi.',
    },
    {
        'id': 'GRAPH-PAYLOAD-MALFORMED',
        'mechanism': 'graph_drawing',
        'figure_id': 'FIG-T67-CAL-PRACTICE',
        'draw_points': [{'x': 0, 'y': 0}],
        'draw_malformed': True,
        'note_lv': 'Strukturāli bojāts grafika iesniegums (trūkst asu): dzinējs met '
                   'E_GRAPH_PAYLOAD_MALFORMED; vērtēšanas maršruts to pārvērš stāvoklī invalid '
                   'ar saglabātu ievadu, nevis klusu nulli.',
    },
    {
        'id': 'STATE-MANUAL-PENDING',
        'mechanism': 'state',
        'state': 'manual_pending',
        'instance_id': 'COL1-7-7A-A-01',
        'note_lv': 'Q03 manuālā rubrika: stāvoklis manual_pending, nav dzinēja izsaukuma; '
                   'etiķete feedback.pending_review, punkti paliek gaidīšanas kategorijā.',
    },
    {
        'id': 'STATE-UNATTEMPTED',
        'mechanism': 'state',
        'state': 'unattempted',
        'instance_id': 'COL1-4-4A-A-01',
        'note_lv': 'Nav atbildes: stāvoklis unattempted ar N23 deklarēto error_class UNATTEMPTED; '
                   'nekāds dzinējs netiek izsaukts.',
    },
    {
        'id': 'STATE-INCOMPLETE',
        'mechanism': 'state',
        'state': 'incomplete',
        'instance_id': 'COL1-2-2B-A-01',
        'missing': [{'field': 'values.m', 'name': 'input.missing.value'}],
        'note_lv': 'Nepabeigta atbilde: N22 completion atgriež incomplete, tāpēc trūkst soļa un '
                   'punkti netiek piešķirti; stāvokļa etiķete aizstāj kļūdas modeli.',
    },
]


# --------------------------------------------------------------------------- #
# Coverage                                                                     #
# --------------------------------------------------------------------------- #

def required_families() -> tuple[list[dict], dict]:
    taxonomy = load_json(ROOT / 'data/engine_taxonomy.json')
    contract = load_json(ROOT / 'data/method_engine_contract.json')
    graph = load_json(ROOT / 'data/graph_scoring_contract.json')
    responses = load_json(ROOT / 'data/response_types.json')

    required: dict[tuple[str, str], str] = {}

    def add(kind: str, value: str, source: str) -> None:
        required[(kind, value)] = source

    for cls in taxonomy['error_taxonomy']['classes']:
        add('error_class', cls['id'], 'engine_taxonomy.error_taxonomy.classes[].id')
        add('signature', cls['signature'], 'engine_taxonomy.error_taxonomy.classes[].signature')
        for n05 in cls.get('n05_error_classes', []):
            add('error_class', n05, 'engine_taxonomy.error_taxonomy.classes[].n05_error_classes')
    fallback = taxonomy['error_taxonomy']['fallback']
    add('signature', fallback['signature'], 'engine_taxonomy.error_taxonomy.fallback.signature')
    add('signature', taxonomy['conservation']['imbalance_signature'],
        'engine_taxonomy.conservation.imbalance_signature')
    for entry in contract['signature_registry']:
        add('signature', entry['signature'], 'method_engine_contract.signature_registry[].signature')
    for value in graph['verdict_record']['error_class_vocabulary']:
        add('error_class', value, 'graph_scoring_contract.verdict_record.error_class_vocabulary')
    for path in sorted((ROOT / 'data/bank').glob('*.json')):
        for question in load_json(path)['questions']:
            for signature in question.get('misconception_signatures') or []:
                add('signature', signature, 'data/bank/*.json#/questions[]/misconception_signatures')
    for value in responses['types']['Q01']['error_surfaces']:
        add('error_class', value, 'response_types.types[].error_surfaces')
    for type_row in responses['types'].values():
        for value in type_row.get('error_surfaces') or []:
            add('error_class', value, 'response_types.types[].error_surfaces')
    for state in ['graded', 'incomplete', 'invalid', 'unattempted', 'manual_pending']:
        add('slot_state', state, 'grading_policy.rubric_policy.slot_state_rules')

    rows = [
        {'match_kind': kind, 'match_value': value, 'source': source}
        for (kind, value), source in sorted(required.items(), key=lambda row: (row[0][0], row[0][1]))
    ]
    counts: dict[str, int] = {}
    for (kind, _value) in required:
        counts[kind] = counts.get(kind, 0) + 1
    return rows, counts


# --------------------------------------------------------------------------- #
# Island and registry validation                                               #
# --------------------------------------------------------------------------- #

def validate_island(island: dict, terms: set[str], anchors: set[str], concepts: set[str],
                    chains: dict[str, set[str]], cards: dict[str, set[str]],
                    required: list[dict]) -> dict:
    findings: list[dict] = []
    mapped: dict[tuple[str, str], dict] = {}
    for index, row in enumerate(island.get('mapping', [])):
        where = f'mapping[{index}]'
        kind = row.get('match_kind')
        value = row.get('match_value')
        if kind not in {'signature', 'error_class', 'slot_state'}:
            findings.append({'check': 'match_kind', 'field': where, 'value': kind})
        if not isinstance(value, str) or not value:
            findings.append({'check': 'match_value', 'field': where, 'value': value})
            continue
        key = (kind, value)
        if key in mapped:
            findings.append({'check': 'duplicate', 'kind': kind, 'value': value})
        mapped[key] = row
        if not isinstance(row.get('priority'), int):
            findings.append({'check': 'priority', 'kind': kind, 'value': value})
        if row.get('feedback_key') not in terms:
            findings.append({'check': 'feedback_key', 'kind': kind, 'value': value,
                             'feedback_key': row.get('feedback_key')})
        name = row.get('misconception_name') or {}
        for field in ('island', 'field'):
            if not isinstance(name.get(field), str):
                findings.append({'check': 'misconception_name', 'kind': kind, 'value': value, 'field': field})
        if not isinstance(row.get('specificity_note_lv'), str) or not row['specificity_note_lv']:
            findings.append({'check': 'specificity_note_lv', 'kind': kind, 'value': value})
        remediation = row.get('remediation') or {}
        for concept_id in remediation.get('concept_ids', []):
            if concept_id not in anchors or concept_id not in concepts:
                findings.append({'check': 'concept_id', 'kind': kind, 'value': value, 'id': concept_id})
        for chain_id in remediation.get('chain_ids', []):
            if chain_id not in chains:
                findings.append({'check': 'chain_id', 'kind': kind, 'value': value, 'id': chain_id})

    ordering = island.get('ordering_rule') or {}
    if ordering.get('rule') != 'priority-ascending-then-match_value' or ordering.get('proposed') is not True:
        findings.append({'check': 'ordering_rule', 'value': ordering.get('rule')})
    if not ordering.get('n09_gap_notice_lv'):
        findings.append({'check': 'n09_gap_notice_lv'})
    resolution = island.get('remediation_resolution') or {}
    if resolution.get('null_chain_allowed') is not True:
        findings.append({'check': 'null_chain_allowed'})
    if (island.get('unmapped_rule') or {}).get('id') != 'E_FEEDBACK_UNMAPPED':
        findings.append({'check': 'unmapped_rule'})
    render = island.get('render_contract') or {}
    for key in ('root', 'verdict_labels', 'state_labels', 'copy_keys'):
        if key not in render:
            findings.append({'check': 'render_contract', 'field': key})

    missing = [row for row in required if (row['match_kind'], row['match_value']) not in mapped]
    extra = [
        {'match_kind': kind, 'match_value': value}
        for (kind, value) in sorted(mapped)
        if not any(row['match_kind'] == kind and row['match_value'] == value for row in required)
    ]
    return {
        'mapping_rows': len(mapped),
        'required_families': len(required),
        'missing': missing,
        'extra': extra,
        'findings': findings,
    }


# --------------------------------------------------------------------------- #
# Node driver                                                                  #
# --------------------------------------------------------------------------- #

NODE_DRIVER = r'''
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const ROOT = process.argv[2];
const CASES_PATH = process.argv[3];
const OUT_PATH = process.argv[4];
const MODULE_PATH = process.argv[5];
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const cases = JSON.parse(fs.readFileSync(CASES_PATH, 'utf8'));

const islands = {
  'sim-conventions': read('data/conventions.json'),
  'sim-terms': read('data/terms.json'),
  'sim-engines': read('data/engine_taxonomy.json'),
  'sim-graph-scoring': read('data/graph_scoring_contract.json'),
  'sim-method-engine': read('data/method_engine_contract.json'),
  'sim-method-cards': read('data/method_cards.json'),
  'sim-chains': read('data/chains.json'),
  'sim-exam-policy': read('data/exam_policy.json'),
  'sim-response-types': read('data/response_types.json'),
  'sim-feedback-classification': read('data/feedback_classification.json')
};
const figures = { island_id: 'sim-figures', figures: [] };
['data/figures_t12.json', 'data/figures_t23.json', 'data/figures_t4.json',
 'data/figures_t5.json', 'data/figures_t67.json'].forEach((p) => {
  (read(p).figures || []).forEach((f) => { figures.figures.push(f); });
});
islands['sim-figures'] = figures;

const registry = Object.create(null);
Object.keys(islands).forEach((id) => { registry[id] = { id, textContent: JSON.stringify(islands[id]) }; });
const doc = {
  getElementById(id) { return registry[id] || null; },
  querySelector() { return null; },
  querySelectorAll() { return []; },
  createElement() { return {}; }
};
const sandbox = { console, document: doc, JSON, Error, String, Object, Array, Math, Number, Boolean,
  RegExp, isFinite, parseInt, parseFloat, Date, Map, Set };
sandbox.globalThis = sandbox;
sandbox.window = sandbox;
vm.createContext(sandbox);
['src/figure-framework.js', 'src/graph-capture.js', 'src/quantity-engine.js', 'src/method-engine.js',
 'src/graph-scoring-engine.js'].forEach((relative) => {
  vm.runInContext(fs.readFileSync(path.join(ROOT, relative), 'utf8'), sandbox, { filename: relative });
});
vm.runInContext(fs.readFileSync(MODULE_PATH, 'utf8'), sandbox, { filename: MODULE_PATH });

const Q = sandbox.SimEngines;
const G = sandbox.SimGraphScoring;
const ME = new sandbox.SimMethodEngine.MethodEngine(islands['sim-method-engine'], islands['sim-terms']);
G.load(doc);

const bank = Object.create(null);
fs.readdirSync(path.join(ROOT, 'data/bank')).sort().forEach((file) => {
  if (!file.endsWith('.json')) return;
  read('data/bank/' + file).questions.forEach((q) => { bank[q.question_id] = q; });
});
const cardsById = Object.create(null);
islands['sim-method-cards'].cards.forEach((c) => { cardsById[c.card_id] = c; });
const terms = {};
islands['sim-terms'].terms.forEach((t) => { terms[t.key] = t.text_lv; });
const anchors = read('data/anchor_registry.json').concepts.map((c) => c.concept_id);
const concepts = read('data/concept_summaries.json').concepts.map((c) => c.id);
const cardMap = {};
islands['sim-method-cards'].cards.forEach((c) => { cardMap[c.card_id] = c.steps.map((s) => s.step_id); });
const registries = {
  concept_ids: Array.from(new Set(anchors.concat(concepts))),
  chain_ids: islands['sim-chains'].chains.map((c) => c.id),
  method_cards: cardMap
};
const context = {
  doc,
  terms,
  classificationNames: {
    engine_taxonomy_classes: islands['sim-engines'].error_taxonomy.classes.map((c) => ({ id: c.id, name_lv: c.name_lv, signature: c.signature })),
    method_signature_registry: islands['sim-method-engine'].signature_registry.map((e) => ({ signature: e.signature, note_lv: e.note_lv }))
  },
  remediationRegistries: registries
};

const FB = sandbox.SimFeedback;
const loaded = FB.loadClassification(doc);
const classification = loaded.classification;
const stateFamilies = classification.assembly_rules.state_families || [];

function rubricOf(instance, card) {
  if (instance && instance.rubric) return instance.rubric;
  if (card && card.__rubric) return card.__rubric;
  return [];
}
function bindingOf(rubric, criterionId) {
  for (let i = 0; i < rubric.length; i += 1) {
    if (rubric[i].criterion_id === criterionId) return String(rubric[i].engine_binding || '');
  }
  return '';
}
function gradingOf(rubric, criterionId) {
  for (let i = 0; i < rubric.length; i += 1) {
    if (rubric[i].criterion_id === criterionId) return String(rubric[i].grading || '');
  }
  return '';
}
function round(value) { return Math.round(Number(value) * 1000000) / 1000000; }

function baseSlot(def, extra) {
  const slot = {
    slot_id: extra.slot_id,
    topic: extra.topic === undefined ? null : extra.topic,
    slot_points: extra.slot_points,
    instance_id: def.instance_id === undefined ? null : def.instance_id,
    family_id: extra.family_id === null ? null : extra.family_id,
    type_id: extra.type_id === null ? null : extra.type_id,
    state: extra.state,
    verdict_class: extra.verdict_class,
    error_class: extra.error_class,
    criteria: extra.criteria,
    task: extra.task,
    outcome_ids: extra.outcome_ids,
    misconception_signatures: extra.misconception_signatures,
    raw_input: extra.raw_input
  };
  return slot;
}

function slotFromVerdict(def, slotId, verdict, options) {
  const instance = options.instance || null;
  const rubric = options.rubric || [];
  const criteria = [];
  let autoPoints = 0;
  let autoMax = 0;
  let pendingPoints = 0;
  let pendingMax = 0;
  let maxPoints = 0;
  const signature = verdict.signature && verdict.signature !== 'NONE' ? String(verdict.signature) : null;
  const diagnosticsSignatures = verdict.diagnostics && verdict.diagnostics.signatures
    ? verdict.diagnostics.signatures.slice() : [];
  const remediation = verdict.diagnostics && verdict.diagnostics.remediation
    ? verdict.diagnostics.remediation : [];
  let remediationAttached = false;
  (verdict.awarded_criteria || []).forEach((row) => {
    const max = Number(row.max_points || 0);
    maxPoints += max;
    if (row.status === 'pending') {
      pendingPoints += Number(row.pending_points || 0);
      pendingMax += max;
    } else {
      autoMax += max;
      autoPoints += Number(row.awarded_points || 0);
    }
    const pending = row.status === 'pending';
    const signatureIds = [];
    if (!pending) {
      if (options.signaturesFromDiagnostics) {
        diagnosticsSignatures.forEach((s) => { if (signatureIds.indexOf(s) === -1) signatureIds.push(s); });
      } else if (signature) {
        signatureIds.push(signature);
      }
    }
    const entries = [];
    if (!pending && !remediationAttached && remediation.length) {
      remediation.forEach((entry) => { entries.push(JSON.parse(JSON.stringify(entry))); });
      remediationAttached = true;
    }
    criteria.push({
      criterion_id: String(row.criterion_id),
      engine_binding: bindingOf(rubric, row.criterion_id),
      grading: gradingOf(rubric, row.criterion_id),
      max_points: max,
      status: row.status,
      awarded_points: Number(row.awarded_points || 0),
      pending_points: Number(row.pending_points || 0),
      verdict_class: pending ? 'pending_self_assessment' : verdict.verdict_class,
      error_class: pending ? 'NONE' : verdict.error_class,
      errors: [],
      missing: [],
      signature_ids: signatureIds,
      feedback_keys: verdict.feedback_key ? [String(verdict.feedback_key)] : [],
      remediation_entries: entries
    });
  });
  return baseSlot(def, {
    slot_id: slotId,
    topic: options.topic === undefined ? null : options.topic,
    slot_points: round(maxPoints),
    family_id: options.family_id === undefined ? null : options.family_id,
    type_id: options.type_id === undefined ? null : options.type_id,
    state: 'graded',
    verdict_class: verdict.verdict_class,
    error_class: verdict.error_class,
    criteria,
    task: {
      auto_points: round(autoPoints), auto_max_points: round(autoMax),
      pending_points: round(pendingPoints), pending_max_points: round(pendingMax),
      max_points: round(maxPoints)
    },
    outcome_ids: options.outcome_ids || [],
    misconception_signatures: options.misconception_signatures || [],
    raw_input: options.raw_input === undefined ? null : options.raw_input
  });
}

function drawingPayload(def) {
  const ctx = islands['sim-graph-scoring'].capture_contract.capture_contexts['CAP-T67-CAL-PRACTICE'];
  const payload = {
    schema_id: 'sim-graph-draw-v1',
    kind: 'line',
    points: def.draw_points,
    axes: ctx.axes,
    span: ctx.span,
    grid: ctx.grid
  };
  if (def.draw_extra) { Object.keys(def.draw_extra).forEach((k) => { payload[k] = def.draw_extra[k]; }); }
  if (def.draw_malformed) { payload.axes = null; }
  return payload;
}

function instanceMeta(instance) {
  return {
    topic: instance && instance.topic !== undefined ? instance.topic : null,
    family_id: instance && instance.family_id ? instance.family_id : null,
    type_id: instance && instance.type_id ? instance.type_id : null,
    outcome_ids: instance && instance.outcome_ids ? instance.outcome_ids.slice() : [],
    misconception_signatures: instance && instance.misconception_signatures
      ? instance.misconception_signatures.slice() : []
  };
}

function resolveItem(item, slot) {
  let kind = 'slot_state';
  let value = String(slot.state);
  if (item.signature_id) {
    kind = 'signature'; value = item.signature_id;
  } else if (item.error_class && item.error_class !== 'NONE' && stateFamilies.indexOf(item.error_class) === -1) {
    kind = 'error_class'; value = item.error_class;
  } else if (stateFamilies.indexOf(String(item.error_class)) !== -1) {
    kind = 'slot_state'; value = String(item.error_class).toLowerCase();
  } else if (item.level === 'criterion' && item.feedback_key === 'feedback.self_assess') {
    kind = 'slot_state'; value = 'manual_pending';
  } else if (item.level === 'criterion' && item.feedback_key === 'feedback.pending_review') {
    kind = 'slot_state'; value = 'manual_pending';
  }
  return { match_kind: kind, match_value: value };
}

const rows = [];
let index = 0;
cases.forEach((def) => {
  index += 1;
  const slotId = 'SWEEP-' + String(index).padStart(2, '0');
  let verdict = null;
  let thrown = null;
  let slot = null;
  const engine = {
    verdict_class: null, error_class: null, taxonomy_class: null, signature: null,
    n05_error_class: null, signatures: [], remediation_entries: 0, threw: null
  };
  try {
    if (def.mechanism === 'quantity_numeric' || def.mechanism === 'quantity_option') {
      const instance = bank[def.instance_id];
      verdict = Q.grade(instance, def.submission, {});
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.taxonomy_class = verdict.taxonomy_class;
      engine.signature = verdict.signature;
      const meta = instanceMeta(instance);
      slot = slotFromVerdict(def, slotId, verdict, Object.assign({ instance: instance, rubric: instance.rubric, raw_input: def.submission }, meta));
    } else if (def.mechanism === 'quantity_classify_probe') {
      const instance = bank[def.instance_id];
      verdict = Q.classify(def.classify);
      engine.verdict_class = null;
      engine.error_class = verdict.taxonomy_class;
      engine.taxonomy_class = verdict.taxonomy_class;
      engine.signature = verdict.signature;
      engine.n05_error_class = verdict.n05_error_class;
      const criteria = [];
      let maxPoints = 0;
      instance.rubric.forEach((row) => {
        const pending = String(row.grading) !== 'auto';
        const max = Number(row.points || 0);
        if (!pending) { maxPoints += max; }
        criteria.push({
          criterion_id: row.criterion_id,
          engine_binding: String(row.engine_binding || ''),
          grading: String(row.grading || ''),
          max_points: max,
          status: pending ? 'pending' : 'denied',
          awarded_points: 0,
          pending_points: pending ? max : 0,
          verdict_class: pending ? 'pending_self_assessment' : 'incorrect',
          error_class: pending ? 'NONE' : verdict.taxonomy_class,
          errors: [], missing: [],
          signature_ids: pending ? [] : [String(verdict.signature)],
          feedback_keys: [String(verdict.feedback_key)],
          remediation_entries: []
        });
      });
      const meta = instanceMeta(instance);
      const pendingMax = criteria.filter((c) => c.status === 'pending').reduce((sum, c) => sum + c.max_points, 0);
      slot = baseSlot(def, {
        slot_id: slotId, topic: meta.topic, slot_points: maxPoints + pendingMax,
        family_id: meta.family_id, type_id: meta.type_id, state: 'graded',
        verdict_class: 'incorrect', error_class: verdict.taxonomy_class,
        criteria: criteria,
        task: { auto_points: 0, auto_max_points: maxPoints, pending_points: pendingMax,
                pending_max_points: pendingMax, max_points: maxPoints + pendingMax },
        outcome_ids: meta.outcome_ids, misconception_signatures: meta.misconception_signatures,
        raw_input: def.classify
      });
    } else if (def.mechanism === 'method_instance') {
      const instance = bank[def.instance_id];
      const spec = ME.specFromInstance(instance);
      verdict = ME.grade(spec, def.submission);
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.signatures = verdict.diagnostics.signatures.slice();
      engine.remediation_entries = verdict.diagnostics.remediation.length;
      const meta = instanceMeta(instance);
      slot = slotFromVerdict(def, slotId, verdict, Object.assign({
        instance: instance, rubric: instance.rubric, signaturesFromDiagnostics: true,
        raw_input: def.submission
      }, meta));
    } else if (def.mechanism === 'method_card_ordering') {
      const card = cardsById[def.card_id];
      const rubric = [{ criterion_id: 'C1_ORDER', grading: 'auto', engine_binding: 'N19-method', points: 2 }];
      const spec = ME.specFromCard(card, 'ordering', null, rubric);
      verdict = ME.grade(spec, def.submission);
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.signatures = verdict.diagnostics.signatures.slice();
      engine.remediation_entries = verdict.diagnostics.remediation.length;
      slot = slotFromVerdict(def, slotId, verdict, {
        rubric: rubric, signaturesFromDiagnostics: true,
        topic: card.topic, family_id: card.family_id, type_id: 'Q08',
        outcome_ids: card.outcome_ids.slice(),
        misconception_signatures: card.steps.map((s) => s.misconception_signature)
          .filter((v, i, a) => v && a.indexOf(v) === i),
        raw_input: def.submission
      });
    } else if (def.mechanism === 'method_card_sequence') {
      const card = cardsById[def.card_id];
      const rubric = [{ criterion_id: 'C1_SEQ', grading: 'auto', engine_binding: 'N19-method', points: 1 }];
      const spec = ME.specFromCard(card, 'sequence', def.prompt_id, rubric);
      verdict = ME.grade(spec, def.submission);
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.signatures = verdict.diagnostics.signatures.slice();
      engine.remediation_entries = verdict.diagnostics.remediation.length;
      slot = slotFromVerdict(def, slotId, verdict, {
        rubric: rubric, signaturesFromDiagnostics: true,
        topic: card.topic, family_id: card.family_id, type_id: 'Q16',
        outcome_ids: card.outcome_ids.slice(),
        misconception_signatures: verdict.diagnostics.signatures.slice(),
        raw_input: def.submission
      });
    } else if (def.mechanism === 'graph_reading') {
      const instance = bank[def.instance_id];
      verdict = G.scoreReading({ kind: 'n05_payload', instance: instance }, def.submission, instance.rubric);
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.signature = null;
      const meta = instanceMeta(instance);
      slot = slotFromVerdict(def, slotId, verdict, Object.assign({
        instance: instance, rubric: instance.rubric, raw_input: def.submission
      }, meta));
    } else if (def.mechanism === 'graph_drawing') {
      const record = G.state.figures[def.figure_id];
      const payload = drawingPayload(def);
      verdict = G.scoreDrawing(record, payload, bank['COL1-7-7B-A-01'].rubric);
      engine.verdict_class = verdict.verdict_class;
      engine.error_class = verdict.error_class;
      engine.signature = null;
      slot = slotFromVerdict(def, slotId, verdict, {
        rubric: bank['COL1-7-7B-A-01'].rubric,
        topic: 7, family_id: 'FAM-7B', type_id: 'Q11',
        outcome_ids: ['P7-03', 'P7-04'],
        misconception_signatures: ['MC-7B-01'],
        raw_input: payload
      });
    } else if (def.mechanism === 'conservation') {
      verdict = Q.checkConservation(def.conservation);
      engine.verdict_class = verdict.verdict === 'BALANCED' ? 'correct' : 'incorrect';
      engine.error_class = verdict.verdict === 'BALANCED' ? 'NONE' : 'IMBALANCED';
      engine.signature = verdict.signature;
      const criteria = [{
        criterion_id: 'C1_CONSERVATION', engine_binding: 'N17-numeric', grading: 'auto',
        max_points: 2, status: verdict.verdict === 'BALANCED' ? 'awarded' : 'denied',
        awarded_points: verdict.verdict === 'BALANCED' ? 2 : 0, pending_points: 0,
        verdict_class: verdict.verdict === 'BALANCED' ? 'correct' : 'incorrect',
        error_class: verdict.verdict === 'BALANCED' ? 'NONE' : 'NONE',
        errors: [], missing: [],
        signature_ids: verdict.verdict === 'BALANCED' ? [] : [String(verdict.signature)],
        feedback_keys: [], remediation_entries: []
      }];
      slot = baseSlot(def, {
        slot_id: slotId, topic: null, slot_points: 2, family_id: null, type_id: null,
        state: 'graded', verdict_class: criteria[0].verdict_class,
        error_class: verdict.verdict === 'BALANCED' ? 'NONE' : 'PHYSICALLY_IMPLAUSIBLE',
        criteria: criteria,
        task: { auto_points: criteria[0].awarded_points, auto_max_points: 2, pending_points: 0,
                pending_max_points: 0, max_points: 2 },
        outcome_ids: [], misconception_signatures: [],
        raw_input: def.conservation
      });
    } else if (def.mechanism === 'state') {
      const instance = bank[def.instance_id];
      const meta = instanceMeta(instance);
      const criteria = instance.rubric.map((row) => {
        const pending = def.state === 'manual_pending' || String(row.grading) !== 'auto';
        const max = Number(row.points || 0);
        return {
          criterion_id: row.criterion_id,
          engine_binding: String(row.engine_binding || ''),
          grading: String(row.grading || ''),
          max_points: max,
          status: pending ? 'pending' : 'denied',
          awarded_points: 0,
          pending_points: pending ? max : 0,
          verdict_class: null,
          error_class: pending ? 'NONE' : (def.state === 'unattempted' ? 'UNATTEMPTED' : 'NONE'),
          errors: [], missing: def.missing || [],
          signature_ids: [], feedback_keys: [], remediation_entries: []
        };
      });
      const pendingMax = criteria.filter((c) => c.pending_points > 0).reduce((sum, c) => sum + c.max_points, 0);
      const maxPoints = criteria.reduce((sum, c) => sum + c.max_points, 0);
      const errorClass = def.state === 'manual_pending' ? 'MANUAL_PENDING'
        : def.state === 'unattempted' ? 'UNATTEMPTED' : '';
      slot = baseSlot(def, {
        slot_id: slotId, topic: meta.topic, slot_points: maxPoints,
        family_id: meta.family_id, type_id: meta.type_id, state: def.state,
        verdict_class: 'NONE', error_class: errorClass,
        criteria: criteria,
        task: { auto_points: 0, auto_max_points: maxPoints - pendingMax, pending_points: pendingMax,
                pending_max_points: pendingMax, max_points: maxPoints },
        outcome_ids: meta.outcome_ids, misconception_signatures: meta.misconception_signatures,
        raw_input: null
      });
    }
    if (!slot) { throw new Error('Unhandled mechanism ' + def.mechanism); }
  } catch (error) {
    thrown = { code: error && error.code ? error.code : null, message: error && error.message ? error.message : String(error) };
    engine.threw = thrown.code;
    if (def.mechanism === 'graph_drawing') {
      const payload = drawingPayload(def);
      const criteria = bank['COL1-7-7B-A-01'].rubric.map((row) => {
        const pending = String(row.grading) !== 'auto';
        const max = Number(row.points || 0);
        return {
          criterion_id: row.criterion_id, engine_binding: String(row.engine_binding || ''),
          grading: String(row.grading || ''), max_points: max,
          status: pending ? 'pending' : 'denied',
          awarded_points: 0, pending_points: pending ? max : 0,
          verdict_class: null, error_class: pending ? 'NONE' : thrown.code,
          errors: pending ? [] : [{ id: thrown.code, field: 'payload', message_key: 'input.error.graph.malformed' }],
          missing: [], signature_ids: [], feedback_keys: [], remediation_entries: []
        };
      });
      const maxPoints = criteria.reduce((sum, c) => sum + c.max_points, 0);
      const pendingMax = criteria.filter((c) => c.status === 'pending').reduce((sum, c) => sum + c.max_points, 0);
      slot = baseSlot(def, {
        slot_id: slotId, topic: 7, slot_points: maxPoints, family_id: 'FAM-7B', type_id: 'Q11',
        state: 'invalid', verdict_class: 'NONE', error_class: thrown.code,
        criteria: criteria,
        task: { auto_points: 0, auto_max_points: maxPoints - pendingMax, pending_points: pendingMax,
                pending_max_points: pendingMax, max_points: maxPoints },
        outcome_ids: ['P7-03', 'P7-04'], misconception_signatures: ['MC-7B-01'],
        raw_input: payload
      });
    }
  }

  let record = null;
  let recordError = null;
  try {
    record = FB.assemble({ schema_version: 1, owner: 'N23', slots: [slot] }, context);
  } catch (error) {
    recordError = { code: error && error.code ? error.code : null, message: error && error.message ? error.message : String(error) };
  }

  const items = record ? record.items : [];
  rows.push({
    case_id: def.id,
    mechanism: def.mechanism,
    instance_id: def.instance_id === undefined ? null : def.instance_id,
    card_id: def.card_id === undefined ? null : def.card_id,
    type_id: slot ? slot.type_id : null,
    payload_class: def.mechanism,
    scripted_input: def.submission === undefined ? (def.classify || def.conservation || null) : def.submission,
    source_note_lv: def.note_lv,
    source_ref: def.source_ref || null,
    engine: engine,
    slot: {
      slot_id: slot ? slot.slot_id : null,
      state: slot ? slot.state : null,
      verdict_class: slot ? slot.verdict_class : null,
      error_class: slot ? slot.error_class : null,
      family_id: slot ? slot.family_id : null,
      instance_id: slot ? slot.instance_id : null
    },
    record: record ? {
      digest: record.digest,
      item_count: items.length,
      unmapped: record.unmapped,
      classification_digest: record.classification_digest,
      error: null
    } : { error: recordError },
    items: items.map((item) => ({
      level: item.level,
      criterion_id: item.criterion_id,
      signature_id: item.signature_id,
      mapped: resolveItem(item, slot),
      misconception_name: item.misconception_name,
      feedback_key: item.feedback_key,
      feedback_text: item.feedback_text,
      priority: item.priority,
      citations: item.citations,
      remediation: item.remediation
    })),
    priority_order: items.map((item) => ({
      priority: item.priority,
      signature_id: item.signature_id,
      feedback_key: item.feedback_key,
      method_card: item.remediation.method_card
    }))
  });
});

const table = FB.classificationTable(context);
const multi = rows.filter((row) => {
  const sigs = row.items.map((item) => item.signature_id).filter((v) => v);
  return sigs.filter((v, i, a) => a.indexOf(v) === i).length >= 2;
})[0] || null;
const ordering = rows.filter((row) => (row.items || []).some((item) => item.remediation.method_card))[0] || null;

const result = {
  module_digest: sandbox.SimFeedback.sha256(fs.readFileSync(MODULE_PATH, 'utf8')),
  module_path: MODULE_PATH,
  island_digest: loaded.digest,
  island_rows: classification.mapping.length,
  table: {
    counts: table.counts,
    unmapped: table.unmapped,
    ordering_rule: table.ordering_rule,
    classification_digest: table.classification_digest,
    rows: table.rows
  },
  cases: rows,
  multi_signature_fixture: multi ? {
    case_id: multi.case_id,
    instance_id: multi.instance_id,
    slot: multi.slot,
    ordering: multi.priority_order,
    items: multi.items
  } : null,
  ordering_fixture: ordering ? {
    case_id: ordering.case_id,
    card_id: ordering.card_id,
    ordering: ordering.priority_order,
    items: ordering.items.filter((item) => item.remediation.method_card)
  } : null
};
fs.writeFileSync(OUT_PATH, JSON.stringify(result, null, 1), 'utf8');
'''


def compile_module(work: Path, tsc: str | None) -> Path:
    """Compile src/feedback.ts with the pinned strict options into `work`."""
    out_dir = work / 'build'
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    config = {
        'compilerOptions': {
            'target': 'ES2018',
            'lib': ['ES2018'],
            'module': 'es2020',
            'strict': True,
            'noImplicitAny': True,
            'strictNullChecks': True,
            'noUnusedLocals': True,
            'noUnusedParameters': True,
            'noImplicitReturns': True,
            'noFallthroughCasesInSwitch': True,
            'forceConsistentCasingInFileNames': True,
            'removeComments': False,
            'newLine': 'lf',
            'declaration': False,
            'sourceMap': False,
            'outDir': str(out_dir),
            'rootDir': str(ROOT / 'src'),
            'types': [],
        },
        'files': [str(ROOT / 'src/ambient.d.ts'), str(ROOT / MODULE_PATH)],
    }
    config_path = work / 'tsconfig.feedback.json'
    config_path.write_text(json.dumps(config, indent=2), encoding='utf-8')
    command = [tsc or 'npx', '--no-install', 'tsc', '-p', str(config_path)] if tsc is None else [tsc, '-p', str(config_path)]
    completed = subprocess.run(command, cwd=str(ROOT), capture_output=True, text=True)
    compiled = out_dir / 'feedback.js'
    if completed.returncode != 0 or not compiled.exists():
        raise SystemExit('tsc failed; the sweep refuses to read a possibly stale compiled module:\n'
                         + completed.stdout + completed.stderr)
    return compiled


def run_node(work: Path, module: Path, cases_path: Path, out_path: Path) -> dict:
    driver = work / 'classify_driver.js'
    driver.write_text(NODE_DRIVER, encoding='utf-8')
    completed = subprocess.run(
        ['node', str(driver), str(ROOT), str(cases_path), str(out_path), str(module)],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if completed.returncode != 0:
        raise SystemExit('Node driver failed:\n' + completed.stdout + completed.stderr)
    return json.loads(out_path.read_text(encoding='utf-8'))


# --------------------------------------------------------------------------- #
# Aggregation                                                                  #
# --------------------------------------------------------------------------- #

def check_results(result: dict, island: dict, terms: set[str], anchors: set[str],
                  concepts: set[str], chains: dict[str, set[str]], cards: dict[str, set[str]]) -> dict:
    unresolved: list[dict] = []
    missing_keys: list[dict] = []
    unmapped: list[dict] = []
    for case in result['cases']:
        for item in case.get('items', []):
            if item['feedback_key'] not in terms:
                missing_keys.append({'case_id': case['case_id'], 'feedback_key': item['feedback_key']})
            for concept_id in item['remediation'].get('concept_ids', []):
                if concept_id not in anchors or concept_id not in concepts:
                    unresolved.append({'case_id': case['case_id'], 'kind': 'concept_id', 'id': concept_id})
            for chain_id in item['remediation'].get('chain_ids', []):
                if chain_id not in chains:
                    unresolved.append({'case_id': case['case_id'], 'kind': 'chain_id', 'id': chain_id})
            card = item['remediation'].get('method_card')
            if card and card.get('card_id'):
                steps = cards.get(card['card_id'])
                if steps is None:
                    unresolved.append({'case_id': case['case_id'], 'kind': 'card_id', 'id': card['card_id']})
                elif card.get('step_id') and card['step_id'] not in steps:
                    unresolved.append({'case_id': case['case_id'], 'kind': 'step_id',
                                       'id': card['step_id'], 'card_id': card['card_id']})
        if case.get('record', {}).get('unmapped'):
            unmapped.extend(case['record']['unmapped'])
        if case.get('record', {}).get('error'):
            unresolved.append({'case_id': case['case_id'], 'kind': 'assemble_error',
                               'id': case['record']['error'].get('code')})
    return {'unresolved_links': unresolved, 'missing_term_keys': missing_keys, 'unmapped': unmapped}


def main() -> int:
    parser = argparse.ArgumentParser(description='N23 classification sweep runner')
    parser.add_argument('--report', default=DEFAULT_REPORT)
    parser.add_argument('--work-dir', default=str(DEFAULT_WORK))
    parser.add_argument('--tsc', default=None, help='optional tsc binary (default: npx --no-install tsc)')
    args = parser.parse_args()

    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)

    island = load_json(ROOT / ISLAND_PATH)
    terms_island = load_json(ROOT / 'data/terms.json')
    terms = {row['key'] for row in terms_island['terms']}
    anchors = {row['concept_id'] for row in load_json(ROOT / 'data/anchor_registry.json')['concepts']}
    concepts = {row['id'] for row in load_json(ROOT / 'data/concept_summaries.json')['concepts']}
    chains = {row['id']: set(row['outcome_ids']) for row in load_json(ROOT / 'data/chains.json')['chains']}
    cards = {row['card_id']: {step['step_id'] for step in row['steps']}
             for row in load_json(ROOT / 'data/method_cards.json')['cards']}

    required, required_counts = required_families()
    island_check = validate_island(island, terms, anchors, concepts, chains, cards, required)

    cases_path = work / 'cases.json'
    cases_path.write_text(json.dumps(CASES, ensure_ascii=False, indent=1), encoding='utf-8')

    module = compile_module(work, args.tsc)
    out1 = work / 'run1.json'
    out2 = work / 'run2.json'
    first = run_node(work, module, cases_path, out1)
    second = run_node(work, module, cases_path, out2)

    parity_first = sha256_bytes(canonical_json_bytes(json.loads(out1.read_text(encoding='utf-8'))))
    parity_second = sha256_bytes(canonical_json_bytes(json.loads(out2.read_text(encoding='utf-8'))))
    parity = parity_first == parity_second

    results_check = check_results(first, island, terms, anchors, concepts, chains, cards)

    module_digest = sha256_bytes(Path(module).read_bytes())
    source_digest = sha256_bytes((ROOT / MODULE_PATH).read_bytes())
    island_digest = sha256_bytes(canonical_json_bytes(island))

    failures = []
    if island_check['missing']:
        failures.append('coverage: ' + str(len(island_check['missing'])) + ' required families are unmapped')
    if island_check['findings']:
        failures.append('island findings: ' + str(len(island_check['findings'])))
    if results_check['unmapped']:
        failures.append('sweep unmapped: ' + str(len(results_check['unmapped'])))
    if results_check['unresolved_links']:
        failures.append('unresolved links: ' + str(len(results_check['unresolved_links'])))
    if results_check['missing_term_keys']:
        failures.append('missing term keys: ' + str(len(results_check['missing_term_keys'])))
    if not parity:
        failures.append('two runs are not byte-identical')
    if first['island_digest'] != island_digest:
        failures.append('module island digest disagrees with the canonical Python digest')
    if first['table']['unmapped']:
        failures.append('classificationTable reports unmapped rows')

    evidence = {
        'schema_version': 1,
        'artifact': 'classification-table',
        'owner': 'N23',
        'status': 'authored',
        'generated_by': 'tools/n23_classification.py',
        'digest_method': "sha256 over canonical JSON: json.dumps(value, ensure_ascii=False, "
                         "sort_keys=True, separators=(',', ':')) -> UTF-8",
        'epistemic_note_lv': 'PROPOSED mācību politika: klasifikācija ir N23 autora kartējums pār '
                             'sasaldētajiem dzinēju vokabulāriem. N09 reģistra nav; prioritāšu '
                             'kārtība nav nekur citur sasaldēta. Šis dokuments nav oficiāls '
                             'eksāmens, atzīme vai proktoringa pierādījums.',
        'island': {
            'path': ISLAND_PATH,
            'island_id': island.get('island_id'),
            'digest': island_digest,
            'module_seen_digest': first['island_digest'],
            'mapping_rows': island_check['mapping_rows'],
            'ordering_rule': (island.get('ordering_rule') or {}).get('rule'),
            'n09_gap_notice_lv': (island.get('ordering_rule') or {}).get('n09_gap_notice_lv'),
            'coverage_counts': first['table']['counts'],
        },
        'module': {
            'source_path': MODULE_PATH,
            'source_digest': source_digest,
            'compiled_path_used': str(module),
            'compiled_digest': module_digest,
            'module_self_digest': first['module_digest'],
            'compile_command': 'npx --no-install tsc -p <work>/tsconfig.feedback.json',
        },
        'coverage': {
            'required_families': len(required),
            'required_by_kind': required_counts,
            'mapped_rows': island_check['mapping_rows'],
            'missing': island_check['missing'],
            'extra_beyond_required': island_check['extra'],
            'island_findings': island_check['findings'],
            'required': required,
            'table': first['table']['rows'],
            'table_note_lv': (
                'Rindas ir SimFeedback.classificationTable() izvade: katra ģimene ar atslēgu, '
                'vārda avotu, remediation id un prioritāti. unmapped ir tukšs.'
            ),
        },
        'sweep': first['cases'],
        'sweep_row_count': len(first['cases']),
        'multi_signature_fixture': first['multi_signature_fixture'],
        'ordering_fixture': first['ordering_fixture'],
        'unmapped': results_check['unmapped'],
        'unresolved_links': results_check['unresolved_links'],
        'missing_term_keys': results_check['missing_term_keys'],
        'parity': {
            'two_run_identical': parity,
            'run1_digest': parity_first,
            'run2_digest': parity_second,
            'note_lv': 'Abi skrējieni ir atsevišķi Node procesi; salīdzināts kanoniskais JSON, '
                       'tāpēc ierakstos nav laikspiedola.',
        },
        'assertions': {
            'zero_unmapped_families': not island_check['missing'],
            'zero_unresolved_remediation_links': not results_check['unresolved_links'],
            'every_feedback_key_resolves': not results_check['missing_term_keys'],
            'two_run_byte_identical': parity,
            'module_island_digest_parity': first['island_digest'] == island_digest,
            'sweep_unmapped_empty': not results_check['unmapped'],
        },
        'failures': failures,
    }

    report_path = ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print('N23 classification sweep')
    print(f"  island rows         : {island_check['mapping_rows']} "
          f"({first['table']['counts']['by_kind']})")
    print(f"  required families   : {len(required)} {required_counts}")
    print(f"  missing             : {len(island_check['missing'])}")
    print(f"  extra beyond required: {len(island_check['extra'])}")
    print(f"  sweep rows          : {len(first['cases'])}")
    print(f"  unmapped            : {len(results_check['unmapped'])}")
    print(f"  unresolved links    : {len(results_check['unresolved_links'])}")
    print(f"  missing term keys   : {len(results_check['missing_term_keys'])}")
    print(f"  two-run parity      : {parity}")
    print(f"  report              : {report_path} ({report_path.stat().st_size} bytes)")
    if failures:
        for failure in failures:
            print('FAIL ' + failure)
        return 1
    print('OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
