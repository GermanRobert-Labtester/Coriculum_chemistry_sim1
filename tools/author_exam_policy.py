#!/usr/bin/env python3
"""N21 authoring twin for the exam-policy island (#sim-exam-policy).

The island carries the *training policy* the exam shell runs on:

  - the advisory timer contract (limit, threshold ratio, clock and hidden-tab
    rules), labelled as a proposal that reuses the programme's 180-minute
    maximum as an advisory training limit;
  - the 21-slot training plan (slot id, topic, points) derived from the
    planning blueprint ``docs/SIMULATION_BLUEPRINT.json`` so that the slot
    list has exactly one derivation path;
  - the session lifetime contract (states, events, the full transition table,
    the guard error ids and the payload contracts) that the runtime session
    machine implements and that the harness cross-checks;
  - the view-discipline mode registry (which components each mode may render);
  - the Latvian copy used by the shell, and the honesty banner.

Nothing here is an official examination rule. The programme PDF states the
seven topics, the written-on-paper format and the 180-minute maximum; every
other value is a labelled training-policy proposal.

Usage:
    python3 tools/author_exam_policy.py            # write data/exam_policy.json
    python3 tools/author_exam_policy.py --check    # verify the file on disk
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_common import DEST, canonical_json_bytes, load_json, sha256_bytes  # noqa: E402

ROOT = DEST
BLUEPRINT_PATH = ROOT / 'docs/SIMULATION_BLUEPRINT.json'
OUT_PATH = ROOT / 'data/exam_policy.json'

ISLAND_ID = 'sim-exam-policy'
OWNER = 'N21'
SCHEMA_VERSION = 1

# The session lifetime contract. Every (state, event) pair is covered so the
# table can be fixture-tested exhaustively: an uncovered pair is a contract
# bug, not a runtime branch.
STATES = ['not-started', 'running', 'review', 'submitted', 'expired', 'aborted']
TERMINAL_STATES = ['submitted', 'expired', 'aborted']
MUTATION_EVENTS = ['answer', 'flag']
EVENTS = [
    'start', 'navigate', 'flag', 'answer', 'request-review', 'submit', 'expire', 'abort',
]

# Stable error ids. Every rejection the machine can produce is named here; the
# harness asserts that the runtime and this table agree.
#
# The two lists are disjoint on purpose: a *transition* error is the answer
# the transition table gives for a (state, event) pair, while a *runtime*
# error is raised by the machine outside the table — a malformed payload, an
# unknown event, a session that cannot be built. The union is the complete
# set of stable ids the runtime may raise.
ERROR_IDS = [
    'E_SESSION_INVALID_EVENT',
    'E_SESSION_INVALID_TRANSITION',
    'E_SESSION_NOT_STARTED',
    'E_SESSION_ALREADY_STARTED',
    'E_SESSION_REVIEW_REQUIRED',
    'E_SESSION_CONFIRMATION_REQUIRED',
    'E_SESSION_LATE_WRITE',
    'E_SESSION_EXPIRED_WRITE',
    'E_SESSION_ABORTED_WRITE',
    'E_SESSION_TERMINAL',
    'E_SESSION_UNKNOWN_SLOT',
    'E_SESSION_FORM_INVALID',
    'E_SESSION_PAYLOAD_INVALID',
    'E_SESSION_SERIALIZE_INVALID',
    'E_SESSION_MISSING_POLICY',
]

# Raised by the machine outside the transition table. The payload validation
# error is *not* here: it is the guard outcome of the answer event, so it
# belongs to the transition side of the contract.
RUNTIME_ERROR_IDS = [
    'E_SESSION_INVALID_EVENT',
    'E_SESSION_INVALID_TRANSITION',
    'E_SESSION_FORM_INVALID',
    'E_SESSION_SERIALIZE_INVALID',
    'E_SESSION_MISSING_POLICY',
]


def _transition_table() -> list[dict[str, Any]]:
    """Build the exhaustive transition table.

    Each entry is ``{from, event, to, error}``. ``to`` is the next state; when
    it is null the ``error`` id names the rejection. The runtime implements the
    same table and the harness compares the two.
    """
    table: list[dict[str, Any]] = []

    def add(from_state: str, event: str, to: str | None, error: str | None = None) -> None:
        table.append({'from': from_state, 'event': event, 'to': to, 'error': error})

    for state in STATES:
        for event in EVENTS:
            if state == 'not-started':
                if event == 'start':
                    add(state, event, 'running')
                else:
                    add(state, event, None, 'E_SESSION_NOT_STARTED')
                continue
            if state in TERMINAL_STATES:
                late_error = {
                    'submitted': 'E_SESSION_LATE_WRITE',
                    'expired': 'E_SESSION_EXPIRED_WRITE',
                    'aborted': 'E_SESSION_ABORTED_WRITE',
                }[state]
                if event in MUTATION_EVENTS:
                    add(state, event, None, late_error)
                else:
                    add(state, event, None, 'E_SESSION_TERMINAL')
                continue
            # running and review
            if event == 'start':
                add(state, event, None, 'E_SESSION_ALREADY_STARTED')
            elif event == 'navigate':
                add(state, event, state)
            elif event == 'flag':
                add(state, event, state)
            elif event == 'answer':
                add(state, event, state)
            elif event == 'request-review':
                add(state, event, 'review')
            elif event == 'submit':
                if state == 'running':
                    add(state, event, None, 'E_SESSION_REVIEW_REQUIRED')
                else:
                    add(state, event, 'submitted')
            elif event == 'expire':
                add(state, event, 'expired')
            elif event == 'abort':
                add(state, event, 'aborted')
            else:  # pragma: no cover - the event list is closed
                raise AssertionError(f'unhandled event {event!r}')
    return table


def build_island() -> dict[str, Any]:
    blueprint = load_json(BLUEPRINT_PATH)
    slots_in = blueprint['slots']
    slots = [
        {
            'slot_id': slot['slot_id'],
            'topic': slot['topic'],
            'points': slot['points'],
        }
        for slot in slots_in
    ]
    points_total = sum(slot['points'] for slot in slots)
    if points_total != blueprint['points']:
        raise SystemExit(
            f'slot points sum {points_total} does not match the blueprint total {blueprint["points"]}'
        )
    if len(slots) != blueprint['constraints']['top_level_tasks']:
        raise SystemExit('slot count does not match the blueprint constraint')
    if blueprint['working_minutes'] + blueprint['review_minutes'] != blueprint['official_facts']['maximum_minutes']:
        raise SystemExit('working + review minutes do not close on the programme maximum')

    return {
        'schema_version': SCHEMA_VERSION,
        'island_id': ISLAND_ID,
        'owner': OWNER,
        'status': 'training-policy-proposed',
        'title_lv': 'Eksāmena apvalka mācību politika',
        'purpose_lv': (
            'Viens iegults avots eksāmena apvalkam: konsultācijas laika līgums, 21 uzdevuma '
            'vietas plāns, sesijas dzīves cikla līgums un skata režīmu robežas.'
        ),
        'epistemic_labels': {
            'PROGRAMME-SOURCED': 'Fakts, kas nāk tieši no 2025. gada programmas PDF.',
            'PROPOSED': 'Šī treniņsimulatora mācību politikas priekšlikums; programma to nenosaka.',
        },
        'official_facts': [
            {
                'id': 'OF-EX-1',
                'label': 'PROGRAMME-SOURCED',
                'statement_lv': (
                    'Kolokvijs notiek klātienē, darbs tiek rakstīts uz papīra; '
                    'programmas maksimālais laiks ir 180 minūtes.'
                ),
                'source': 'RSU_MedChem_Colloq1_Prog_LV_2025.pdf',
            },
        ],
        'training_policy': [
            {
                'id': 'TP-EX-1',
                'label': 'PROPOSED',
                'statement_lv': (
                    'Konsultācijas taimers ir izglītojošs: tas rāda pagājušo laiku un brīdina '
                    'pie 90 % robežas, bet nav oficiāls eksāmena laika noteikums.'
                ),
                'note_lv': (
                    'Programmas PDF nenosaka konsultācijas taimera uzvedību. Šeit izmantotās '
                    '180 minūtes ir programmas maksimums, kas šajā simulatorā izmantots kā '
                    'izglītojošs treniņa limīts.'
                ),
            },
            {
                'id': 'TP-EX-2',
                'label': 'PROPOSED',
                'statement_lv': (
                    'Eksāmena sesijā ir 21 uzdevuma vieta un 100 punkti; formas A, B un C '
                    'dalās tajā pašā struktūrā.'
                ),
                'note_lv': 'Sadalījums ņemts no plānošanas zīmējuma docs/SIMULATION_BLUEPRINT.json.',
            },
            {
                'id': 'TP-EX-3',
                'label': 'PROPOSED',
                'statement_lv': (
                    'Atbildes ir maināmas līdz iesniegšanai; pēc iesniegšanas mašīna '
                    'noraida vēlāku ierakstīšanu ar stabilu kļūdas id.'
                ),
                'note_lv': 'Strukturāls aizsargs, nevis lietotāja interfeisa konvencija.',
            },
            {
                'id': 'TP-EX-4',
                'label': 'PROPOSED',
                'statement_lv': (
                    'Eksāmena režīmā netiek renderētas palīdzības, darba piemēru un metodes '
                    'kartes; prakse režīmā tās tiek atļautas.'
                ),
                'note_lv': 'Režīmu reģistrs ir vienots avots; nezināms komponents pārtrauc pārbaudi.',
            },
        ],
        'timer': {
            'advisory_limit_seconds': blueprint['official_facts']['maximum_minutes'] * 60,
            'working_seconds': blueprint['working_minutes'] * 60,
            'review_seconds': blueprint['review_minutes'] * 60,
            'threshold_ratio': 0.9,
            'clock': 'monotonic',
            'hidden_tab': 'keeps_counting',
            'basis_lv': (
                'Limīts ir 180 minūtes, t. i. programmas maksimums, izmantots kā izglītojošs '
                'treniņa limīts; 170 + 10 minūšu sadalījums ir PROPOSED.'
            ),
        },
        'exam': {
            'slot_count': len(slots),
            'total_points': points_total,
            'forms': list(blueprint['proposed_forms']),
            'required_types_per_form': list(blueprint['constraints']['required_types_per_form']),
        },
        'slots': slots,
        'session_contract': {
            'states': STATES,
            'terminal_states': TERMINAL_STATES,
            'mutation_events': MUTATION_EVENTS,
            'events': EVENTS,
            'error_ids': ERROR_IDS,
            'runtime_error_ids': RUNTIME_ERROR_IDS,
            'transition_table': _transition_table(),
            'guards': {
                'submit': {'confirmed': 'E_SESSION_CONFIRMATION_REQUIRED'},
                'navigate': {'slot_known': 'E_SESSION_UNKNOWN_SLOT'},
                'flag': {'slot_known': 'E_SESSION_UNKNOWN_SLOT'},
                'answer': {'slot_known': 'E_SESSION_UNKNOWN_SLOT', 'payload_valid': 'E_SESSION_PAYLOAD_INVALID'},
            },
            'payload_contracts': {
                'numeric': {
                    'kind': 'numeric',
                    'required': ['values'],
                    'value_type': 'raw_string_map',
                    'field_types': {'values': 'raw_string_map'},
                    'note_lv': 'Skaitļi tiek glabāti tādi, kā tos ievadīja; parsēšana pieder vērtēšanai.',
                },
                'option_select': {
                    'kind': 'option_select',
                    'required': ['selected'],
                    'value_type': 'string_list',
                    'field_types': {'selected': 'string_list', 'justification': 'raw_string'},
                    'note_lv': 'Izvēles identifikatori un brīvais pamatojums.',
                },
                'ordering': {
                    'kind': 'ordering',
                    'required': ['order'],
                    'value_type': 'string_list',
                    'field_types': {'order': 'string_list'},
                    'note_lv': 'Secība tiek glabāta tāda, kā to izkārtotja.',
                },
                'matching': {
                    'kind': 'matching',
                    'required': ['pairs'],
                    'value_type': 'pair_list',
                    'field_types': {'pairs': 'pair_list'},
                    'note_lv': 'Pāri tiek glabāti tādi, kā tos izkārtotja.',
                },
                'graph': {
                    'kind': 'graph',
                    'required': ['variant'],
                    'value_type': 'raw_string',
                    'field_types': {'variant': 'raw_string'},
                    'note_lv': 'Grafika ieraksts (Q11) vai zīmējuma stāvoklis (plot_state).',
                },
                'method': {
                    'kind': 'method',
                    'required': ['variant'],
                    'value_type': 'raw_string',
                    'field_types': {'variant': 'raw_string'},
                    'note_lv': 'Metodes vektors (Q13) vai pāri (Q17).',
                },
                'raw_text': {
                    'kind': 'raw_text',
                    'required': ['text'],
                    'value_type': 'raw_string',
                    'field_types': {'text': 'raw_string'},
                    'note_lv': 'Neapstrādats ievades teksts, kamēr N22 tipa komponenti nav pievienoti.',
                },
            },
            'named_variants': {
                'Q11_record': {'kind': 'graph', 'variant': 'record'},
                'Q13_vector': {'kind': 'method', 'variant': 'vector'},
                'Q17_pairs': {'kind': 'method', 'variant': 'pairs'},
                'Q18_plot_state': {'kind': 'graph', 'variant': 'plot_state'},
            },
            'terminal_record': {
                'fields': [
                    'schema_version', 'session_id', 'form_id', 'state', 'started_at_ms',
                    'elapsed_ms', 'finished_at_ms', 'answers', 'flags', 'unanswered_slot_ids',
                    'remediation_slot_ids', 'transitions',
                ],
                'consumers': ['N23', 'N25', 'N28'],
            },
        },
        'view_discipline': {
            'default_mode': 'practice',
            'modes': {
                'exam': {
                    'allowed_components': ['input', 'timer', 'navigator', 'map', 'review'],
                    'forbidden_components': ['hint', 'chain', 'method-card', 'term-lookup'],
                },
                'practice': {
                    'allowed_components': [
                        'input', 'timer', 'navigator', 'map', 'review',
                        'hint', 'chain', 'method-card', 'term-lookup',
                    ],
                    'forbidden_components': [],
                },
            },
            'unregistered_component_error': 'E_MODE_COMPONENT_NOT_ALLOWED',
        },
        'copy_lv': {
            'timer_label': 'Izglītojošs laika ierobežojums (mācību politika, nevis oficiāls eksāmens)',
            'timer_threshold': 'Pārsniegta 90 % robeža',
            'timer_expired': 'Laika ierobežojums izsaukts — iesniegšana ir tikai iespējama',
            'navigator_prev': 'Iepriekšējais uzdevums',
            'navigator_next': 'Nākamais uzdevums',
            'navigator_flag': 'Atzīmēt uzdevumu',
            'navigator_unflag': 'Noņemt atzīmējumu',
            'map_label': 'Uzdevumu karte',
            'map_cell_answered': 'atbildēts',
            'map_cell_unanswered': 'nav atbildēts',
            'map_cell_flagged': 'atzīmēts',
            'review_heading': 'Pārbaude un iesniegšana',
            'review_warning': (
                'Ne visas 21 uzdevuma vietas ir atbildētas. Iesniegšana ir galīga un atgriezties '
                'nebūs iespējams.'
            ),
            'review_warning_short': 'Neatbildētas uzdevumu vietas',
            'review_dismiss': 'Aizvērt brīdinājumu',
            'review_confirm': 'Esmu pārliecināts, ka vēlos iesniegt darbu',
            'review_submit': 'Iesniegt darbu',
            'review_one_way': 'Iesniegšana ir galīga: pēc iesniegšanas atbildes nav maināmas.',
            'review_summary': (
                'Šis ir mācību politikas kopsavilkums, nevis oficiāls rezultāta dokuments; '
                'galīgo vērtējumu aprēķina vērtēšanas posms.'
            ),
            'keyboard_hint': (
                'Tastatūra: bultiņas pāriet starp uzdevumu vietām, F atzīmē pašreizējo vietu.'
            ),
            'slot_points': 'punkti',
            'form_pending_note': (
                'Uzdevumu instancēm vēl nav pievienotas (montāžas posms N24); līdz tam '
                'darba vieta ir plāna vieta.'
            ),
            'banner': (
                'Treniņa darba režīms: šis nav oficiāls RSU kolokvija eksāmens, nepiešķir '
                'oficiālu vērtējumu vai apliecību, neveic uzraudzību un pēc noklusējuma '
                'sesijas stāvokli glabā tikai operatīvajā atmiņā.'
            ),
        },
        'conflicts': [
            {
                'id': 'N21-C01',
                'label': 'DOCUMENTED-AND-ACCEPTED',
                'topic': 'Q18 atbildes veids',
                'roadmap_label': 'N21 uzdevuma tekstā Q18 minēts kā "plot state"',
                'schema_label': 'N04 shēma saista Q18 ar option_select klasi',
                'resolution_lv': (
                    'Grafikas klase nes gan Q11 ieraksta, gan plot_state variantus, tāpēc '
                    'planas forma ir pieejama; tipa saiste ar Q18 seko N04 shēmai '
                    '(option_select). Ceļa norāde netiek klusējusi pielīgota.'
                ),
                'owner': 'N21',
            },
            {
                'id': 'N21-C02',
                'label': 'DOCUMENTED-AND-RE-BUDGETED',
                'topic': 'Runtime JS izmērs',
                'roadmap_label': (
                    'Plāna 1.3 sadaļas josla: inline runtime JS 120–220 KiB'
                ),
                'schema_label': (
                    'Izmērītais inline runtime JS pēc N21 ir 266,616 B (260,4 KiB); '
                    'izpildītais griests ir 264 KiB'
                ),
                'resolution_lv': (
                    'AGENTS.md atļauj budžetu noteikt pēc izmērītajām prasībām, nevis pēc '
                    'mantotās grāmatu mantras. N21 paceļ izmērīto JS griestu no 232 KiB uz '
                    '264 KiB (mērījums 266,616 B). Mērīšanas pamats un atkāpe no deklarētās '
                    'joslas ir fiksēta failā tools/byte_budget.py un N21 verifikācijas '
                    'ierakstā. Deklarētā josla 120–220 KiB ir pārsniegta, un tas nav '
                    'klusējami pielāgots.'
                ),
                'owner': 'N21',
            },
            {
                'id': 'N21-C03',
                'label': 'DOCUMENTED-AND-RE-BUDGETED',
                'topic': 'Artefakta kopējais apjoms',
                'roadmap_label': (
                    'Plāna 1.3 sadaļas josla: artefakts kopā 700–1400 KiB'
                ),
                'schema_label': (
                    'Izmērītais artefakts pēc N21 ir 1,403,1 KiB, kas pārsniedz '
                    'deklarēto 1,400 KiB joslu par aptuveni 3 KiB; izpildītais griests ir '
                    '1,440 KiB'
                ),
                'resolution_lv': (
                    'Eksāmena apvalkam jādarbojas vienfaila artefakta iekšienē, tāpēc tā '
                    'runtime ir inline\'ots, un kopējais apjoms pārsniedza plāna joslu, '
                    'kura jau N20 laikā bija 95,9 % izlietota. N21 pārbālansēja griestu '
                    'uz izmērījumu (tools/byte_budget.py) un atkāpi fiksēja kā '
                    'konfliktu, nevis klusējami. Galīgo inline/lazy-load/pārbudžeta '
                    'lēmumu pieņem N31; N22–N25 jāmēra savs pieprasījums.'
                ),
                'owner': 'N21',
            },
        ],
        'citations': {
            'programme_pdf': 'RSU_MedChem_Colloq1_Prog_LV_2025.pdf',
            'blueprint': 'docs/SIMULATION_BLUEPRINT.json',
            'question_schema': 'data/question_schema.json',
            'coverage_island': 'data/coverage.json',
            'chains_island': 'data/chains.json',
        },
        'honesty': {
            'not_an_official_examination': True,
            'no_proctoring_claim': True,
            'in_memory_by_default': True,
            'no_official_grade_claim': True,
            'note_lv': (
                'Šis islands apraksta treniņsimulatora mācību politiku. Tas neko neapstiprina '
                'oficiālu eksāmenu, oficiālu vērtējumu, uzraudzību vai sertifikāciju.'
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify the file on disk instead of writing')
    args = parser.parse_args()

    island = build_island()
    payload = canonical_json_bytes(island)
    if args.check:
        if not OUT_PATH.exists():
            print(f'FAIL {OUT_PATH} does not exist')
            return 1
        on_disk = OUT_PATH.read_bytes()
        if on_disk != payload:
            print(f'FAIL {OUT_PATH} differs from the authored island')
            return 1
        print(f'PASS exam_policy island matches ({len(payload)} bytes, sha256={sha256_bytes(payload)})')
        return 0

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_bytes(payload)
    print(f'wrote {OUT_PATH.relative_to(ROOT)} ({len(payload)} bytes, sha256={sha256_bytes(payload)})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
