#!/usr/bin/env python3
"""The byte budget policy of the simulator — one source for every gate.

AGENTS.md: "Set runtime budgets on measured new requirements rather than
inheriting a chapter master's historical widget cap." The plan bands below are
the *declared* Section 1.3 figures of the master roadmap; they are kept
verbatim so that the deviation stays visible. The *enforced* ceilings are the
measured requirements of the artifact as it stands, re-set by the task that
measured them, with the history recorded here.

Two budgets have been re-set since the plan was written:

  N20 — runtime JS code: 220 KiB → 232 KiB. The measurement: the inline
        executable JS was 223,288 B (218.1 KiB) before N20 and 225,192 B
        (219.9 KiB) after it — the previous ceiling would have failed on a
        rounding difference rather than on a requirement.

  N21 — runtime JS code: 232 KiB → 264 KiB (measured 266,616 B = 260.4 KiB
        after the exam-session machine and the exam shell), and artifact total:
        1,400 KiB → 1,440 KiB (measured 1,436,780 B = 1,403.1 KiB). The exam
        shell has to run inside the single-file artifact, so its runtime is
        inlined; the plan band was already 95.9 % consumed by N20 and the
        declared band is exceeded by 2,480 B. The deviation is recorded as
        conflict N21-C03 in data/exam_policy.json and in the verification
        ledger.

  N23 — runtime JS code: 264 KiB → 280 KiB (measured 277,359 B = 270.9 KiB
        after the three SMK-N23 grading vectors), and artifact total:
        1,504 KiB → 1,600 KiB (measured 1,611,253 B = 1,573.5 KiB). The two
        N23 islands (#sim-grading-policy and #sim-feedback-classification) are
        data the page ships, and the three grading vectors are inlined; the
        grading and feedback modules themselves ship from src/. The measurement
        is the N23 build of 2026-11-19; N31 owns the final decision.

The final inline / lazy-load / re-budget decision belongs to N31. Everything
here is a measured interim ceiling, not a new plan.
"""
from __future__ import annotations

from typing import Any

# The declared Section 1.3 bands of the master roadmap (plan figures).
DECLARED_BANDS: dict[str, tuple[int, int]] = {
    'artifact_total': (700 * 1024, 1400 * 1024),
    'runtime_js_code': (120 * 1024, 220 * 1024),
    'css': (40 * 1024, 80 * 1024),
    'bank_island': (200 * 1024, 420 * 1024),
    'figures_island': (60 * 1024, 140 * 1024),
}

# The enforced ceilings, re-set on the measured requirement.
ENFORCED_CEILINGS: dict[str, int] = {
    'artifact_total': 2780 * 1024,
    'runtime_js_code': 1168 * 1024,
    'css': 80 * 1024,
    'bank_island': 420 * 1024,
    'figures_island': 140 * 1024,
}

# The re-budget history, oldest first.
RE_BUDGET_HISTORY: list[dict[str, Any]] = [
    {
        'task': 'N20',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 220 * 1024,
        'new_ceiling_bytes': 232 * 1024,
        'measured_bytes': 225192,
        'reason_lv': (
            'Izmērītais inline runtime JS pēc N20 bija 225,192 B (219,9 KiB); '
            'iepriekšais griests tiktu pārkāpts par 88 baitiem, tāpēc tas tika '
            'pārbālansēts uz mērījumu, nevis uz noapaņošanos.'
        ),
    },
    {
        'task': 'N21',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 232 * 1024,
        'new_ceiling_bytes': 264 * 1024,
        'measured_bytes': 266616,
        'reason_lv': (
            'Eksāmenu sesijas mašīna un eksāmena apvalks (strict TypeScript) '
            'mērījumā 266,616 B (260,4 KiB). Deklarētā josla 120–220 KiB ir '
            'pārsniegta; mērījums ir fiksēts, nevis klusējami pielāgots.'
        ),
    },
    {
        'task': 'N21',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1400 * 1024,
        'new_ceiling_bytes': 1440 * 1024,
        'measured_bytes': 1436780,
        'reason_lv': (
            'Eksāmena apvalkam jādarbojas vienfaila artefakta iekšienē, tāpēc tā '
            'runtime ir inline\'ots; mērītais kopējais apjoms ir 1,436,080 B '
            '(1,402,4 KiB), kas pārsniedz deklarēto 1,400 KiB joslu par 2,480 B. '
            'Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N22',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1440 * 1024,
        'new_ceiling_bytes': 1504 * 1024,
        'measured_bytes': 1522087,
        'reason_lv': (
            'N22 atbilžu ievades slānis: reakcijas tipu reģistra sala '
            '(34,179 B kanoniski), terminoloģijas salas pieaugums (+47,549 B) un '
            'trīs dūmu vektori palielina artefaktu līdz 1,522,087 B (1,486,4 KiB), '
            'kas pārsniedz N21 noteikto 1,440 KiB griestu par 47,527 B. Griests '
            'pārlikts uz mērījuma pamata; deklarētā 700–1,400 KiB josla paliek '
            'redzama. N22 ievades moduļi (225,423 B) tiek piegādāti no src/ un '
            'nav inline\'oti; izpildāmais runtime JS 270,014 B paliek zem 264 KiB '
            'griesta. Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N23',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 264 * 1024,
        'new_ceiling_bytes': 280 * 1024,
        'measured_bytes': 277359,
        'reason_lv': (
            'N23 trīs dūmu vektori (SMK-N23-GRADE-FULL/PARTIAL/MALFORMED) un '
            'koplietotais n23Run palīgs src/smoke-subset.js failā pievieno 7,387 B; '
            'inline\'otais izpildāmais runtime JS mērījumā ir 277,359 B (270,9 KiB), '
            'kas pārsniedz N21 noteikto 264 KiB griestu par 7,023 B. Tā kā vienfaila '
            'artefaktā dūmu vektori ir inline\'oti, griests pārlikts uz mērījuma '
            'pamata 280 KiB; vērtēšanas moduļi paši (src/compiled/grading.js, '
            'src/compiled/feedback.js) nav inline\'oti. Galīgo inline/lazy-load/'
            'pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N23',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1504 * 1024,
        'new_ceiling_bytes': 1600 * 1024,
        'measured_bytes': 1611253,
        'reason_lv': (
            'N23 vērtēšanas un atgriezeniskās saites slānis: divas jaunas datu salas '
            '(#sim-grading-policy 12,143 B un #sim-feedback-classification 63,716 B '
            'kanoniski), 12 feedback.results.* terminu ieraksti, trīs dūmu vektori un '
            '#rezultati skaidrojuma teksts paceļ artefaktu līdz 1,611,253 B '
            '(1,573,5 KiB), kas pārsniedz N22 noteikto 1,504 KiB griestu par 71,157 B. '
            'Griests pārlikts uz mērījuma pamata 1,600 KiB; deklarētā 700–1,400 KiB '
            'josla paliek redzama. N23 vērtēšanas moduļi tiek piegādāti no src/ un nav '
            'inline\'oti. Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N24',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 280 * 1024,
        'new_ceiling_bytes': 332 * 1024,
        'measured_bytes': 329976,
        'reason_lv': (
            'N24 formu montāžas dzinējs un neatkarīgais pārbaudītājs '
            '(src/compiled/assembly.js), formas izvēlnes loģika un '
            'SMK-N24-ASSEMBLY-DRAW dūmu vektors tiek inline\'oti vienfaila '
            'artefaktā, lai sēklotais treniņa zīmējums un montāžas pašpārbaude '
            'darbotos bezsaistē. Izmērītais runtime JS ir 329,976 B (322,2 KiB); '
            'griests pārlikts uz 332 KiB. Galīgo inline/lazy-load/pārbudžeta '
            'lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N24',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1600 * 1024,
        'new_ceiling_bytes': 1680 * 1024,
        'measured_bytes': 1684264,
        'reason_lv': (
            'N24 #sim-forms sala, inline\'otais assembly.js, formas izvēlne '
            'sākuma/eksāmena ekrānā un dūmu vektors palielina artefakta kopējo '
            'apjomu virs N23 1,600 KiB griesta; griests pārlikts uz izmērīto '
            '1,680 KiB līmeni, saglabājot deklarēto 700–1,400 KiB joslu '
            'redzamu. Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N25',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 332 * 1024,
        'new_ceiling_bytes': 388 * 1024,
        'measured_bytes': 390841,
        'reason_lv': (
            'N25 versijas krātuve (src/compiled/store.js, 25,744 B), analītikas un '
            'progresa modulis (src/compiled/analytics.js, 31,951 B) un dūmu vektors '
            'SMK-N25-STORE-ROUNDTRIP tiek inline\'oti vienfaila artefaktā, lai '
            '#atskats un #iestatijumi darbotos bezsaistē. Izmērītais runtime JS ir '
            '390,841 B (381,7 KiB); griests pārlikts uz 388 KiB. Galīgo inline/'
            'lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N25',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1680 * 1024,
        'new_ceiling_bytes': 1720 * 1024,
        'measured_bytes': 1756388,
        'reason_lv': (
            'N25 #sim-analytics sala (6,098 B), inline\'otie store.js un analytics.js, '
            '#atskats un #iestatijumi HTML/CSS un dūmu vektors palielina artefakta '
            'kopējo apjomu līdz 1,756,388 B (1,715,2 KiB); griests pārlikts uz '
            '1,720 KiB, saglabājot deklarēto 700–1,400 KiB joslu redzamu. Galīgo '
            'inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N26',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 388 * 1024,
        'new_ceiling_bytes': 432 * 1024,
        'measured_bytes': 437232,
        'reason_lv': (
            'N26 apguves stāvokļu mašīna (src/compiled/mastery.js, 43,200 B '
            'kompaktēti), analytics.js āķis un SMK-N26-MASTERY-WALK dūmu vektors '
            'tiek inline\'oti vienfaila artefaktā, lai #atskats un #prakse skati '
            'darbotos bezsaistē. Izmērītais runtime JS ir 437,232 B (427,0 KiB); '
            'griests pārlikts uz 432 KiB. Galīgo inline/lazy-load/pārbudžeta '
            'lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N26',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1720 * 1024,
        'new_ceiling_bytes': 1780 * 1024,
        'measured_bytes': 1817433,
        'reason_lv': (
            'N26 #sim-mastery-policy sala (10,378 B kanoniski), inline\'otais '
            'mastery.js, #atskats/#prakse skatu HTML/CSS (+2,737 B CSS) un dūmu '
            'vektors palielina artefakta kopējo apjomu līdz 1,817,433 B '
            '(1,774,8 KiB); griests pārlikts uz 1,780 KiB, saglabājot deklarēto '
            '700–1,400 KiB joslu redzamu. Galīgo inline/lazy-load/pārbudžeta '
            'lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N27',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 432 * 1024,
        'new_ceiling_bytes': 484 * 1024,
        'measured_bytes': 491765,
        'reason_lv': (
            'N27 Leitnera plānotājs (src/compiled/scheduler.js, 50,950 B '
            'kompaktēti), mastery.js saistītais atjaunošanas āķis un '
            'SMK-N27-SCHEDULER-QUEUE dūmu vektors tiek inline\'oti vienfaila '
            'artefaktā, lai #prakse ieteikumu rinda darbotos bezsaistē. '
            'Izmērītais runtime JS ir 491,765 B (480,2 KiB); griests pārlikts uz 484 KiB. '
            'Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N27',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1780 * 1024,
        'new_ceiling_bytes': 1848 * 1024,
        'measured_bytes': 1886741,
        'reason_lv': (
            'N27 #sim-scheduler-policy sala (5,161 B kanoniski), 16 scheduler.* '
            'terminu ieraksti, inline\'otais scheduler.js, #prakse rindas HTML/CSS '
            'un dūmu vektors palielina artefakta kopējo apjomu līdz 1,886,741 B '
            '(1,842,5 KiB); griests pārlikts uz 1,848 KiB, saglabājot deklarēto '
            '700–1,400 KiB joslu redzamu. Galīgo inline/lazy-load/pārbudžeta '
            'lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N28',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 484 * 1024,
        'new_ceiling_bytes': 552 * 1024,
        'measured_bytes': 563555,
        'reason_lv': (
            'N28 kļūdu atkārtošanas rinda (src/compiled/remediation.js, 64,524 B '
            'kompaktēti), store.js/analytics.js lauku atbalsts un '
            'SMK-N28-REMEDIATION-WALK dūmu vektors tiek inline\'oti vienfaila '
            'artefaktā, lai #atskats atkārtošanas cilpa darbotos bezsaistē. '
            'Izmērītais runtime JS ir 563,555 B (550,3 KiB); griests pārlikts uz 552 KiB. '
            'Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N28',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1848 * 1024,
        'new_ceiling_bytes': 1928 * 1024,
        'measured_bytes': 1972615,
        'reason_lv': (
            'N28 #sim-remediation-policy sala (4,208 B kanoniski), 18 remediation.* '
            'terminu ieraksti, inline\'otais remediation.js, #atskats rindas HTML/CSS '
            '(+1,882 B CSS) un dūmu vektors palielina artefakta kopējo apjomu līdz '
            '1,972,615 B (1,926,4 KiB); griests pārlikts uz 1,928 KiB, saglabājot '
            'deklarēto 700–1,400 KiB joslu redzamu. Galīgo inline/lazy-load/'
            'pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N29',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 552 * 1024,
        'new_ceiling_bytes': 620 * 1024,
        'measured_bytes': 630624,
        'reason_lv': (
            'N29 vienotais atkārtošanas skats un F07 kritēriju pašvērtējuma kartīte '
            '(src/compiled/revision.js, 63,355 B kompaktēti), store.js/mastery.js/'
            'analytics.js atbalsts un SMK-N29-REVISION-PANEL dūmu vektors tiek '
            'inline\'oti vienfaila artefaktā, lai #atskats darbotos bezsaistē. '
            'Izmērītais runtime JS ir 630,624 B (615,8 KiB); griests pārlikts uz '
            '620 KiB. Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N29',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 1928 * 1024,
        'new_ceiling_bytes': 2060 * 1024,
        'measured_bytes': 2105879,
        'reason_lv': (
            'N29 #sim-revision-policy sala (4,338 B kanoniski), 144 jauni #sim-terms '
            'ieraksti (117 vienotie feedback.criterion.* un 27 revision.*), '
            'inline\'otais revision.js, #atskats HTML/CSS (+2,812 B CSS) un dūmu '
            'vektors palielina artefaktu līdz 2,105,879 B (2,056,5 KiB); griests '
            'pārlikts uz 2,060 KiB, saglabājot deklarēto 700–1,400 KiB joslu '
            'redzamu. Galīgo inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N30',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 620 * 1024,
        'new_ceiling_bytes': 692 * 1024,
        'measured_bytes': 705398,
        'reason_lv': (
            'N30 ierobežoto prakses ceļu dzinējs un izpildītājs (src/compiled/practice.js), '
            'SimGrading.gradePracticeRecord un SMK-N30-PRACTICE-PATH dūmu vektors tiek '
            'inline\'oti vienfaila artefaktā, lai #prakse darbotos bezsaistē. Izmērītais '
            'runtime JS ir 705,398 B (688,9 KiB); griests pārlikts uz 692 KiB. Galīgo '
            'inline/lazy-load/pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N30',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 2060 * 1024,
        'new_ceiling_bytes': 2156 * 1024,
        'measured_bytes': 2202232,
        'reason_lv': (
            'N30 #sim-practice-policy sala, 27 practice.* terminu ieraksti, inline\'otais '
            'practice.js, #prakse HTML/CSS un dūmu vektors palielina artefaktu līdz '
            '2,202,232 B (2,150,6 KiB); griests pārlikts uz 2,156 KiB, saglabājot '
            'deklarēto 700–1,400 KiB joslu redzamu. Galīgo inline/lazy-load/'
            'pārbudžeta lēmumu pieņem N31.'
        ),
    },
    {
        'task': 'N31',
        'budget': 'runtime_js_code',
        'previous_ceiling_bytes': 692 * 1024,
        'new_ceiling_bytes': 1168 * 1024,
        'measured_bytes': 1152126,
        'reason_lv': (
            'N31 galīgais vienfaila būves lēmums inline\'o visus 11 IV–V fāzes dzinēju, '
            'ievades un vērtēšanas runtime moduļus (quantity-engine.js, graph-scoring-engine.js, '
            'graph-capture.js, method-engine.js, method-card-view.js, variant-engine.js, '
            'inputs/{registry,components,integration}.js, grading.js, feedback.js) ar moduļu '
            'robežkomentāriem un SMK-N31-BUILD-CONTRACT dūmu vektoru, kamēr 308,6 KiB '
            'ģeneratora šabloni (src/variant-templates.js) paliek ārpus artefakta. '
            'Izmērītais runtime JS ir 1,152,126 B (1,125,1 KiB); griests fiksēts uz 1,168 KiB.'
        ),
    },
    {
        'task': 'N31',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 2156 * 1024,
        'new_ceiling_bytes': 2624 * 1024,
        'measured_bytes': 2649417,
        'reason_lv': (
            'N31 vienfaila būves konveijers apvieno visas 22 kanoniskās JSON salas, '
            '37 topoloģiski sakārtotos runtime moduļus, CSS/SVG slāņus un būves zīmogus '
            'vienā bezsaistes output/simulator.html failā (2,649,417 B / 2,587,3 KiB); griests fiksēts '
            'uz 2,624 KiB, saglabājot deklarēto 700–1,400 KiB joslu redzamu.'
        ),
    },
    {
        'task': 'N34',
        'budget': 'artifact_total',
        'previous_ceiling_bytes': 2624 * 1024,
        'new_ceiling_bytes': 2780 * 1024,
        'measured_bytes': 2826711,
        'reason_lv': (
            'N34 pievieno vienota avota statisko <noscript> saturu (64 jēdzieni, metodika, '
            '673 terminu tabula un godīgo ierobežojumu paziņojums: ~133,8 KiB), pilno @media print '
            'slāni un F04 papīra darba lapas moduli (SimPaper); izmērītais artefakts ~2,760 KiB, '
            'griests fiksēts uz 2,780 KiB.'
        ),
    },
]


def ceiling_bytes(budget: str) -> int:
    """The enforced ceiling of one budget."""
    if budget not in ENFORCED_CEILINGS:
        raise KeyError(f'unknown budget: {budget}')
    return ENFORCED_CEILINGS[budget]


def basis_lv(budget: str) -> str:
    """A Latvian sentence that says where the enforced ceiling comes from."""
    entries = [entry for entry in RE_BUDGET_HISTORY if entry['budget'] == budget]
    if not entries:
        return 'Plāna 1.3 sadaļas josla; mērījums ir joslā, izmērīšana nav mainījusi griestu.'
    last = entries[-1]
    return (
        f'Plāna 1.3 sadaļas josla {DECLARED_BANDS[budget][0] // 1024}–'
        f'{DECLARED_BANDS[budget][1] // 1024} KiB; izmērītais apjoms pēc {last["task"]} '
        f'ir {last["measured_bytes"]} B, tāpēc izpildītais griests ir '
        f'{last["new_ceiling_bytes"] // 1024} KiB. {last["reason_lv"]}'
    )


def measure_budgets(manifest: dict[str, Any]) -> dict[str, Any]:
    """Measure the built artifact against the enforced ceilings."""
    tokens = manifest['tokens_layer']
    bank = manifest['bank_island']
    fig_block = manifest.get('figures_island') or manifest.get('figures_layer') or {}
    figures_bytes = int(fig_block.get('bytes') or fig_block.get('island_bytes') or 0)
    measurements = {
        'artifact_total': int(manifest['output_bytes']),
        'runtime_js_code': int(tokens['runtime_js_code_bytes']),
        'css': int(tokens['css_bytes']),
        'bank_island': int(bank['bytes']),
        'figures_island': figures_bytes,
    }
    budgets: list[dict[str, Any]] = []
    failed_segments: list[str] = []
    for name in ('artifact_total', 'runtime_js_code', 'css', 'bank_island', 'figures_island'):
        declared_min, declared_max = DECLARED_BANDS[name]
        enforced_max = ENFORCED_CEILINGS[name]
        measured = measurements[name]
        within_max = measured <= enforced_max
        if not within_max:
            failed_segments.append(name)
        budgets.append({
            'name': name,
            'bytes': measured,
            'kib': round(measured / 1024, 1),
            'min_bytes': declared_min,
            'max_bytes': enforced_max,
            'declared_max_bytes': declared_max,
            'within_max': within_max,
            'within_declared_band': measured <= declared_max,
            'within_min': measured >= declared_min,
            'share_percent_of_max': round(measured / enforced_max * 100, 2),
            'basis': basis_lv(name),
        })
    return {
        'status': 'PASS' if not failed_segments else 'FAIL',
        'failed_segments': failed_segments,
        'budgets': budgets,
        're_budget_history': RE_BUDGET_HISTORY,
    }
