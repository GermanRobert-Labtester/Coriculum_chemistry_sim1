# -*- coding: utf-8 -*-
"""F04: source-conflict comparison ledger for K1–K23.

The ledger is data, not prose in ``ch15_16.html``.  Every entry keeps the short
source excerpt, the document treatment, the warrant, the confidence and the
lecturer status apart.  A source location is mandatory before an entry may be
labelled as checked against the source.
"""
from __future__ import annotations

import html
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / 'build' / 'qa'
OPENED = '2026-11-07'

# Source inventory metadata.  The hashes are computed from the files, so a
# replaced handout cannot silently keep an old provenance record.
SOURCES = [
    {
        'id': 'A',
        'file': '3. temata apraksts.pdf',
        'kind': 'PDF',
        'pages': '1',
        'role': 'Temata apraksts, sasniedzamie rezultāti, 55 % slieksnis',
        'opened': OPENED,
    },
    {
        'id': 'B',
        'file': '3. Sem_Koncentrāciju_apr_Darab_lapa_2020_MF.pdf',
        'kind': 'PDF',
        'pages': '14',
        'role': 'Teorija un risinātie piemēri; satur K1–K12 avota vietas',
        'opened': OPENED,
    },
    {
        'id': 'C',
        'file': '3_Seminars_Koncentraciju aprekini_2023.docx',
        'kind': 'DOCX',
        'pages': '—',
        'role': 'Semināra uzdevumi ar īsām atbildēm; satur K7, K13–K15',
        'opened': OPENED,
    },
    {
        'id': 'D',
        'file': 'Papilduzdevumi. Koncentrāciju aprēķini..pdf',
        'kind': 'PDF',
        'pages': '2',
        'role': 'Papilduzdevumi P1–P13; satur K16, K18, K20, K22',
        'opened': OPENED,
    },
    {
        'id': 'E',
        'file': 'Papilduzdevumi. Koncentrāciju aprēķini. Atbildes. .pdf',
        'kind': 'PDF',
        'pages': '5',
        'role': 'Papilduzdevumu atslēga un “Kā plānot?”; satur K16–K21',
        'opened': OPENED,
    },
    {
        'id': 'F',
        'file': '3_SEM_Atbildes_konc_papilduzd_pec_nodarb_2023.pdf',
        'kind': 'PDF',
        'pages': '2',
        'role': 'P10–P13 pilnie risinājumi; satur K18–K22',
        'opened': OPENED,
    },
]

CONFLICTS = [
    {
        'id': 'K1',
        'topic': 'Mols, vielas daudzums un Avogadro konstante',
        'sources': [
            {'source': 'B', 'location': 'B 3. lpp.', 'kind': 'elided',
             'quote': '«Vielas daudzums ir daļiņu … skaits»'},
            {'source': 'B', 'location': 'B 3. lpp.', 'kind': 'verbatim',
             'quote': '«Mols ir vielas daudzums, kurš satur tikpat daudz molekulu, cik atomu ir 12 gramos C-12 izotopa»'},
            {'source': 'B', 'location': 'B 3. lpp.', 'kind': 'normalized',
             'quote': '«skaitli sauc par Avogadro skaitli, un tas ir aptuveni 6,022·10²³»'},
        ],
        'analysis': 'Dokuments nošķir vielas daudzumu n (mol) no daļiņu skaita N. Lieto N = nN_A un N_A = 6,02214076·10²³ mol⁻¹; mols tiek skaidrots ar fiksētu N_A, nevis ar 12 g C-12.',
        'warrant': 'SI definīcija (2019) un N_A fiksētā vērtība; kursa formulējums saglabāts citātā.',
        'confidence': 'C·X',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K2',
        'topic': 'Šķīdības un disperso sistēmu joslu robi',
        'sources': [
            {'source': 'B', 'location': 'B 1. lpp.', 'quote': '«vairāk nekā 10g vielas»; «no 0,1g līdz 10g vielas»; «mazāk par 0,01g vielas»'},
            {'source': 'B', 'location': 'B 1. lpp.', 'quote': '«mazāki par 1nm»; «no 100 nm līdz 1 nm»; «lielāks par 1000 nm»'},
        ],
        'analysis': 'Dokuments parāda abas neklasificētās joslas — 0,01–0,1 g un 100–1000 nm — kā “avotā nav klasificēts”, nevis pievieno tām jaunu klasi.',
        'warrant': 'Avota trīs joslas citētas burtiski; robs ir avota klasifikācijas īpašība, nevis aprēķina kļūda.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K3',
        'topic': 'Disociācijas pakāpes klases un α = 1 idealizācija',
        'sources': [
            {'source': 'B', 'location': 'B 2. lpp.', 'quote': '«Stiprie elektrolīti (α > 0,7)»; «Vājie elektrolīti ir (α < 0,1)»'},
            {'source': 'C', 'location': 'C 19. un 20. jautājums', 'quote': '«0,70 un 0,70 mol/L»; «1,5 : 0,50 mol/L»'},
        ],
        'analysis': 'Dokuments rāda α klases kā diapazonus un atzīmē, ka C19–C20 klusi pieņem pilnīgu disociāciju (α = 1). Uzdevuma atbilde netiek mainīta; idealizācija tiek nosaukta.',
        'warrant': 'α ir atkarīgs no koncentrācijas; avotā nav klases 0,1–0,7.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K4',
        'topic': 'Amonjaka apzīmējums, bāzes konstante un Ostvalda tuvinājums',
        'sources': [
            {'source': 'B', 'location': 'B 2. lpp.', 'kind': 'verbatim',
             'quote': '«Vājie elektrolīti ir (α < 0,1) CH3COOH, H2CO3, HCN, HF, NH3 · H2O»'},
            {'source': 'B', 'location': 'B 2. lpp.', 'kind': 'reconstructed',
             'quote': '«Kdis = [OH−][NH4+] / [NH4OH] = 1,79 · 10−5»'},
            {'source': 'B', 'location': 'B 2. lpp.', 'kind': 'verbatim',
             'quote': '«Ka = C · α2»'},
            {'source': 'B', 'location': 'B 2. lpp.', 'kind': 'reconstructed',
             'quote': '«α = √(Ka/C)»'},
        ],
        'analysis': 'Avots B raksta NH₃ · H₂O vājo elektrolītu sarakstā, bet piemērā lieto jonu NH₄OH un konstanti K_dis = 1,79·10⁻⁵. Ostvalda likumu tas pieraksta ar skābes konstanti K_a = C·α² un α = √(K_a/C). Skaitlis 1,79·10⁻⁵ atbilst amonjaka bāzes konstantei K_b; apzīmējums K_dis ar hipotētisko daļiņu NH₄OH nav standarta, jo NH₄OH kā atsevišķs savienojums nav definēts.',
        'warrant': 'Avota simboli (K_dis, NH₄OH, K_a bāzei) un standarta bāzes konstante K_b nav viens un tas pats lielums; tāpēc citēts avots un nosaukta atšķirība, nevis klusi pārzīmēta formula. Standarta vērtība šajā darbvietā nav pārbaudīta primārajā avotā.',
        'confidence': 'C·X',
        'lecturer': 'Atvērts · 16.d (K4)',
        'status': 'Daļēji atrisināts; politika V',
    },
    {
        'id': 'K5',
        'topic': 'Simbolu un mērvienību sadursmes (M, w, mL/L)',
        'sources': [
            {'source': 'B', 'location': 'B 3. lpp.', 'quote': '«Mērvienību (mol/l) kā saīsināto variantu mēdz aizstāt ar lielo burtu M»'},
            {'source': 'C', 'location': 'C 3.1. un 3.2. jautājums', 'quote': '«0,10 M»; «0,200 M»'},
            {'source': 'E', 'location': 'E 1. lpp.', 'kind': 'verbatim',
             'quote': '«c – molārā koncentrācija – mol/l»'},
            {'source': 'E', 'location': 'E 1. lpp.', 'kind': 'verbatim',
             'quote': '«ρ (ro) – šķīduma blīvums – g/ml»'},
        ],
        'analysis': 'Dokuments tekstā lieto c(B), mol/L un M(B), g/mol. Kursa C un c ar apakšindeksu M, kā arī “M” tiek paskaidroti 14. nodaļas pārejas tabulā; avotu citātos kursa rakstība paliek.',
        'warrant': 'Viens simbols diviem lielumiem rada pārneses kļūdu; mērvienību vienotība ir dokumenta konvencija, nevis docētāja apstiprināta politika.',
        'confidence': 'H',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K6',
        'topic': 'Tilpuma vienība blīvuma formulā',
        'sources': [
            {'source': 'B', 'location': 'B 3. lpp.', 'quote': '«Všķ. – šķīduma tilpums (l)»; «ρ – šķīduma blīvums (g/ml)»'},
            {'source': 'E', 'location': 'E 1. lpp.', 'quote': '«V – šķīduma tilpums – l»; «ρ (ro) – šķīduma blīvums – g/ml»'},
        ],
        'analysis': 'Dokuments lieto V mL ar ρ g/mL vai pārrēķina ρ uz g/L. Katrā uzdevumā mērvienības tiek pārbaudītas pirms ievietošanas formulā.',
        'warrant': 'g/mL · L dod 1000 g, nevis g; tas ir dimensiju pārbaudes jautājums.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K7',
        'topic': 'Formulu numerācija avotos',
        'sources': [
            {'source': 'C', 'location': 'C formulas', 'kind': 'verbatim',
             'quote': '«(7) mšķīdumam = mvielai + mšķīdinātājs»'},
            {'source': 'C', 'location': 'C formulas', 'kind': 'reconstructed',
             'quote': '«(7) γ = m(vielai)/V(šķīdumam)»'},
            {'source': 'E', 'location': 'E 1. lpp.', 'kind': 'reconstructed',
             'quote': '«(7) c1 · V1 = c2 · V2»'},
        ],
        'analysis': 'Dokuments nelieto avotu formulu numurus kā vienotu sistēmu. Avoti tiek citēti pēc jautājuma numura, bet formulas apzīmētas ar lielumu nosaukumiem.',
        'warrant': 'C vienā laidienā ir divas dažādas formulas ar numuru (7) un nav (8); E numerācija atšķiras.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K8',
        'topic': 'Nepareizi vielu nosaukumi un “vienmolāra” pret kursa C ar indeksu M',
        'sources': [
            {'source': 'B', 'location': 'B 5. lpp.', 'kind': 'verbatim',
             'quote': '«ρ 10%KOH = 1,11 g/ml»'},
            {'source': 'B', 'location': 'B 8. lpp.', 'kind': 'verbatim',
             'quote': '«vienmolāra (CM = 1 mol/l)»'},
            {'source': 'B', 'location': 'B 8. lpp.', 'kind': 'verbatim',
             'quote': '«vienmolāra (CM = 0,1 mol/l)»'},
            {'source': 'B', 'location': 'B 8. lpp.', 'kind': 'verbatim',
             'quote': '«Lai pagatavotu 200 ml vienmolāra kalcija karbonāta šķīduma»'},
        ],
        'analysis': 'Dokuments lieto ρ(10 % Na₂CO₃), 0,1 mol/L un CaCl₂. “Vienmolāra” pretruna atzīmēta kā avota defekts, nevis klusi pārtulkota.',
        'warrant': 'Trīs nosaukumu vai simbolu kļūdas vienā avota blokā; tās maina vielas identitāti, nevis tikai pareizrakstību.',
        'confidence': 'C',
        'lecturer': 'Netieši · 16.d (vienmolārs, K8)',
        'status': 'Atrisināts dokumentā; politika V',
    },
    {
        'id': 'K9',
        'topic': 'Neitralizācijas molu attiecība',
        'sources': [
            {'source': 'B', 'location': 'B 12. lpp.', 'quote': '«n skābes = 2n sārma»'},
            {'source': 'B', 'location': 'B 12. lpp.', 'quote': '«2n NaOH = n H2SO4»; «n NaOH = n H2SO4 / 2»'},
        ],
        'analysis': 'Dokuments lieto n(H₂SO₄) = n(NaOH)/2. Uzdevuma beigas avotā jau dod 0,005 mol un 0,49 g; burtiskā pirmā rinda dotu 1,96 g.',
        'warrant': 'Reakcija H₂SO₄ + 2NaOH → Na₂SO₄ + 2H₂O prasa pusi skābes molu uz vienu sārma molu; attiecība 1:2 nav 2:1.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K10',
        'topic': 'Fizioloģiskais šķīdums: 0,88 % pret 0,9 %',
        'sources': [
            {'source': 'B', 'location': 'B 6. lpp.', 'quote': '«Fizioloģiskais šķīdums ir 0,88% nātrija hlorīda (NaCl) šķīdums»'},
            {'source': 'A', 'location': 'A 1. lpp.', 'quote': '«0.9 % NaCl šķīdums»'},
        ],
        'analysis': 'Uzdevumā saglabāts avota B skaitlis 0,88 %. Standarts 0,9 % minēts kā konteksts, nevis aizstāts uzdevuma datos.',
        'warrant': 'Viens kurss lieto divus skaitļus; fakts ir pārbaudāms, bet eksāmena izvēle ir docētāja politika.',
        'confidence': 'C (fakts) · V (politika)',
        'lecturer': 'Atvērts · 16.d (K10)',
        'status': 'Daļēji atrisināts; politika V',
    },
    {
        'id': 'K11',
        'topic': '0,85 g NaCl un neizmantotais blīvums',
        'sources': [
            {'source': 'B', 'location': 'B 14. lpp.', 'kind': 'elided',
             'quote': '«9. Cik gramu NaCl ir 100 mililitros šķīduma, ρ = 1,01 g/ml: … a) 0,85% šķīduma; b) 0,85 M šķīduma? Atbilde: a) 0,85 g; b) 4,97 g»'},
        ],
        'analysis': 'Dokuments parāda abas atbildes: 0,85 g, ja procentu lasa kā m/V, un 0,86 g, ja 0,85 % ir w/w un lieto doto ρ. Procenta bāze nosaukta.',
        'warrant': 'Jautājums nenosaka procenta veidu; blīvums ir dots, bet atslēgā nav izmantots.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K12',
        'topic': 'Molmasas izvēle 96 % H₂SO₄ uzdevumā: 98 pret 98,08 g/mol',
        'sources': [
            {'source': 'B', 'location': 'B 10. lpp.', 'kind': 'verbatim',
             'quote': '«MH2SO4 = (2 · 1) + 32 + (4 · 16) = 98 (g/mol)»'},
            {'source': 'B', 'location': 'B 10. lpp.', 'kind': 'reconstructed',
             'quote': '«mšķ. = 100 · 4,9 / 96% = 5,1 (g) 96% H2SO4 šķīduma»'},
            {'source': 'B', 'location': 'B 10. lpp.', 'kind': 'reconstructed',
             'quote': '«V = 5,1 / 1,84 = 2,77 (ml)»'},
            {'source': 'B', 'location': 'B 11. lpp.', 'kind': 'verbatim',
             'quote': '«jāņem 2,77 ml 96% H2SO4»'},
        ],
        'analysis': 'Avots B lieto savu noapaļoto molmasu M = 98 g/mol: 4,900 g tīras vielas, 5,104 g 96 % šķīduma, 2,774 mL. Ar M = 98,08 g/mol tie paši dati dod 4,904 g, 5,108 g un 2,776 mL jeb 2,78 mL. Starpība 0,004 mL rodas no molmasas, nevis no noapaļošanas: ar M = 98 arī starprezultāts 5,1 g dod 2,77 mL, un 2,774 mL noapaļojas uz 2,77 mL. Avota atbilde 2,77 mL tāpēc nav priekšlaicīgas noapaļošanas kļūda — tā ir konsekventa ar avota M.',
        'warrant': 'Aritmētika: 0,1·98·0,5/0,96/1,84 = 2,774 mL un 5,1/1,84 = 2,7717 mL — abas vērtības noapaļojas uz 2,77 mL. 2,78 mL parādās tikai ar M = 98,08. Students drīkst lietot abas molmasas, ja tā ir norādīta; sajaukt 98,08 starprezultātu ar 98 atbildi nedrīkst.',
        'confidence': 'C',
        'lecturer': 'Atvērts · 16.d (K12): kuru M vērtību pieņem eksāmenā?',
        'status': 'Aprēķins pārbaudīts; avota atbilde nav kļūda; M izvēle V',
    },
    {
        'id': 'K13',
        'topic': '300,0 mL ūdens kā galīgais šķīduma tilpums',
        'sources': [
            {'source': 'C', 'location': 'C 10. jautājums', 'quote': '«ja 18 g glikozes (C6H12O6) izšķīdināja 300,0 mL ūdens»'},
            {'source': 'C', 'location': 'C 10. jautājums, atbilde', 'quote': '«60 mg/mL»'},
        ],
        'analysis': 'Atbilde 60 mg/mL ir nosacīta: tā atbilst šķīduma tilpumam 300,0 mL. Uzdevumā nav dots ne galīgais šķīduma tilpums, ne blīvums, tāpēc citu tilpumu ar dotajiem datiem noteikt nevar. Dokuments atbildi saglabā ar šo nosacījumu redzamu.',
        'warrant': 'γ = m(viela)/V(šķīdums); ūdens tilpums nav šķīduma tilpums. Trūkst galīgā tilpuma, tāpēc atbilde nav viennozīmīga.',
        'confidence': 'H',
        'lecturer': 'Atvērts · 16.d (K13)',
        'status': 'Nosacīta atbilde; galīgais tilpums nav dots; politika V',
    },
    {
        'id': 'K14',
        'topic': 'Mācību blīvumi C 7., 13. un 17. jautājumā',
        'sources': [
            {'source': 'C', 'location': 'C 7. jautājums', 'quote': '«Šķīduma blīvums ρ =1,07 g/mL»'},
            {'source': 'C', 'location': 'C 13. jautājums', 'quote': '«blīvums ρ=1,07 g/mL»'},
            {'source': 'C', 'location': 'C 17. jautājums', 'quote': '«šķīduma blīvums ρ=1,07 g/mL»'},
        ],
        'analysis': 'Dokuments lieto doto ρ. Ar reālu ≈1,005 g/mL C7 atbilde būtu 0,995 %, nevis 0,93 %; starpība parādīta kā ilustratīva piezīme, nevis kā aizvietota atbilde.',
        'warrant': 'Dotos blīvumus nosaka uzdevums; “reālāks” blīvums nav avota datos un mainītu atbildi.',
        'confidence': 'H·X',
        'lecturer': 'Atvērts · 16.d (K14)',
        'status': 'Daļēji atrisināts; politika V',
    },
    {
        'id': 'K15',
        'topic': 'Zīmīgo ciparu politika atslēgās',
        'sources': [
            {'source': 'C', 'location': 'C 24. jautājums, atbilde', 'quote': '«0,001 mol»'},
            {'source': 'C', 'location': 'C 10. jautājums, atsauce', 'quote': '«60 mg/mL»'},
            {'source': 'C', 'location': 'C 9. jautājums, atbilde', 'quote': '«150 g»'},
            {'source': 'C', 'location': 'C 20. jautājums, atbilde', 'quote': '«1,5 : 0,50 mol/L»'},
        ],
        'analysis': 'Dokuments atzīmē, kur beigu nulle nav viennozīmīga: C24 10 mL precizitāte nav skaidra; C10 60 mg/mL pie K13 nosacījuma atbilst 6,0·10¹ mg/mL; C9 150 g ir aprēķina vērtība, bet ar vienu zīmīgo ciparu — 2·10² g.',
        'warrant': 'Avotā nav vienotas zīmīgo ciparu politikas; dokumenta līgums ir 16.g, nevis avota labojums.',
        'confidence': 'H',
        'lecturer': 'Atvērts · 16.d (K15)',
        'status': 'Daļēji atrisināts; vērtēšanas politika V',
    },
    {
        'id': 'K16',
        'topic': 'Formalīns (HCOOH) un formaldehīds (HCHO)',
        'sources': [
            {'source': 'D', 'location': 'D P5', 'quote': '«720 ml 8% (ρ = 1,03 g/mL) formalīna šķīduma (HCOOH)»'},
            {'source': 'E', 'location': 'E P5', 'quote': '«formalīna šķīduma (HCOOH)»; «Atbilde: 0,75 mol/l»'},
        ],
        'analysis': 'Dokuments saglabā uzdevumā iespiesto HCOOH un atslēgas 0,75 mol/L, bet atzīmē, ka formalīns ir HCHO (M = 30,03 g/mol) un ar to pašiem datiem iegūst 1,15 mol/L. HCOOH ir skudrskābe (M = 46,03 g/mol).',
        'warrant': 'Vielas identitāte maina molmasu un atbildi; eksāmena izvēle starp iespiesto formulu un pareizo identitāti ir docētāja politika.',
        'confidence': 'C (identitāte) · V (politika)',
        'lecturer': 'Atvērts · 16.d (K16)',
        'status': 'Daļēji atrisināts; politika V',
    },
    {
        'id': 'K17',
        'topic': 'Šķīduma masa, vielas masa un tilpumu aditivitāte',
        'sources': [
            {'source': 'E', 'location': 'E P7', 'quote': '«m(šķīd) = 62,1 g»'},
            {'source': 'D', 'location': 'D P4, P5, P7, P9', 'quote': '«pievienoja 1 litru ūdens»; «cik mililitru ūdens ir jāpievieno»'},
        ],
        'analysis': 'Dokuments labo apzīmējumu uz m(H₂SO₄) = 62,1 g, jo šķīdums ir 345 g (300 mL · 1,15 g/mL). Tālāk 62,1/98 = 0,634 mol, 0,634/0,7 = 0,905 L, un 0,905 − 0,300 = 0,61 L ūdens — tas ir avota atbilde. Kur tiek saskaitīti vai atņemti tilpumi, atklāti norādīts tilpumu aditivitātes pieņēmums.',
        'warrant': '62,1 g ir izšķīdušās vielas masa, nevis šķīduma masa; tilpumi reāli nav precīzi aditīvi.',
        'confidence': 'C / H',
        'lecturer': 'Atvērts · 16.d (K17)',
        'status': 'Daļēji atrisināts; pieņēmums atklāts, politika V',
    },
    {
        'id': 'K18',
        'topic': 'Rehidrona summa bez KCl un “hipernātriēmija”',
        'sources': [
            {'source': 'E', 'location': 'E P10', 'quote': '«m(šķīd.) = 1000 + 3,5+2,9+10=1018,9g»'},
            {'source': 'D', 'location': 'D P10', 'quote': '«var attīstīties hipernātriēmija»'},
            {'source': 'F', 'location': 'F 10. uzdevums', 'quote': '«m(šķīd.) = 1000 + 3,5 + 2,5 + 2,9 + 10 =1018,9g»'},
        ],
        'analysis': 'Dokuments lieto 1018,9 g arī ar 2,5 g KCl; summa bez KCl ir 1016,4 g. Termins labots uz “hipernatrēmija” (oficiālās Rehydron PIL rakstība; “hipernatriēmija” arī ir sastopams variants). B05: darba lapas sastāvs atbilst klasiskajam Rehydron 01-0036, bet pašreizējais LV produkts ir Optim ar citu sastāvu.',
        'warrant': 'E rindā izlaista sastāvdaļa, lai gan rezultāts atbilst summai ar to; F to parāda pareizi.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K19',
        'topic': 'ACC dienas deva: maksimums pret intervālu',
        'sources': [
            {'source': 'D', 'location': 'D P11', 'quote': '«no 3 līdz 5 mL 20% šķīduma vai 6-10 ml 10% šķīduma trīs līdz četras reizes dienā»'},
            {'source': 'F', 'location': 'F 11. uzdevums', 'quote': '«dienas laikā tiks uzņemti 4g acetilcisteīna»'},
        ],
        'analysis': 'Dokuments rāda pilnu intervālu 1,8–4,0 g/dienā, nevis tikai maksimumu. 10 % ACC šķīdums skaidrots kā 100 mg/mL (m/V), kas ar ρ = 1 g/mL skaitliski sakrīt ar w.',
        'warrant': 'Deva ir intervāls; maksimums ir tikai augšējā robeža. Procenta veids ir jānosauc.',
        'confidence': 'H',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K20',
        'topic': 'ACC pulvera un šķīduma atšķirīgie saucēji',
        'sources': [
            {'source': 'D', 'location': 'D P12', 'quote': '«masas daļu procentos 1 pulvera paciņā»; «molāro koncentrāciju 200ml šķīduma»; «ρ (šķīdumam) =1,01g/ml»'},
            {'source': 'F', 'location': 'F 12. uzdevums', 'kind': 'reconstructed',
             'quote': '«W% = 100mg/3000mg · 100 = 3,33%»'},
            {'source': 'F', 'location': 'F 12. uzdevums', 'kind': 'reconstructed',
             'quote': '«CM = 0,1 g/(179,2 g/mol·0,2 L) = 0,00279 (mol/l)»'},
        ],
        'analysis': 'Dokuments nosauc abus saucējus: w attiecas uz 3 g pulvera (100/3000 = 3,33 %, 2800/3000 = 93,33 %), c — uz 0,2 L šķīduma (0,1/(179,2·0,2) = 0,00279 mol/L, 2,8/(342,3·0,2) = 0,041 mol/L). Doto ρ = 1,01 g/mL izmanto tikai tur, kur tas maina rezultātu.',
        'warrant': 'Pulvera masa un šķīduma tilpums ir dažādi jautājumi; saucēju sajaukšana maina mērvienību un atbildi.',
        'confidence': 'H',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K21',
        'topic': 'Maalox 13,4 g pret 13,5 g un 0,0994 pret 0,100 mol',
        'sources': [
            {'source': 'E', 'location': 'E P13', 'quote': '«13,4 g Mg(OH)2»; «0,0994 mol Al(OH)3»'},
            {'source': 'F', 'location': 'F 13. uzdevums', 'quote': '«13490mg = 13,4g Mg(OH)2»; «355 ml · 0,00028 mol = 0,0994 mol Al(OH)3»'},
        ],
        'analysis': 'Dokuments rāda 13,49 g → 13,5 g, ja noapaļo beigās, un atslēgas molu skaitu pret 0,100 mol ar M = 78,00. Atslēgas vērtības netiek pasludinātas par neiespējamām; atšķirība ir noapaļošanā.',
        'warrant': 'Atslēgas masa ir nogriezta, nevis noapaļota; atslēgas molu skaits izriet no 0,00028 mol precizitātes, nevis no precīza M.',
        'confidence': 'C',
        'lecturer': 'Atvērts · 16.d (K21)',
        'status': 'Aprēķins pārbaudīts; atslēgas politika V',
    },
    {
        'id': 'K22',
        'topic': 'Drukas un valodas kļūdas D/E/F',
        'sources': [
            {'source': 'D', 'location': 'D P12', 'quote': '«ūdnes»; «lieto lieto»; «saharīna, and garšas aizvietotāja»'},
            {'source': 'E', 'location': 'E 2. lpp.', 'quote': '«Aprēķieniet»; «vienādojumd»; «Pieņem V=1lirs»'},
            {'source': 'D', 'location': 'D P13', 'quote': '«10 ml of suspensijas»; «molu Al(OH)3 and Mg(OH)2»'},
        ],
        'analysis': 'Dokuments citē avota rakstību un skaidrojumā lieto labotos pierakstus. “Saharīna” atzīts par pareizu ģenitīvu, nevis drukas kļūdu.',
        'warrant': 'Drukas un valodas kļūdas nemaina aprēķinu, bet traucē avota un jēdziena atrašanu.',
        'confidence': 'C',
        'lecturer': 'Nav atvērts jautājums',
        'status': 'Atrisināts dokumentā',
    },
    {
        'id': 'K23',
        'topic': 'Etiķešu procentu veids nav norādīts',
        'sources': [
            {'source': 'A', 'location': 'A 1. lpp.', 'kind': 'elided',
             'quote': '«0.9 % NaCl šķīdums, 5 % glikozes šķīdums, 3 % ūdeņraža peroksīda … 70 % etanola/spirta … 5 % joda … šķīdums»'},
            {'source': 'D', 'location': 'D P11–P12', 'kind': 'verbatim',
             'quote': '«100 mg acetilcisteīna»'},
            {'source': 'D', 'location': 'D P11', 'kind': 'verbatim',
             'quote': '«10% ACC»'},
            {'source': 'D', 'location': 'D P5', 'kind': 'elided',
             'quote': '«8% … formalīna»'},
        ],
        'analysis': 'Dokuments nosauc visticamāko veidu: 70 % etanols V/V, 0,9 % NaCl m/V, ACC m/V. H₂O₂ un joda etiķetes paliek ne viennozīmīgas; tās nav pasludinātas par noteiktām.',
        'warrant': 'Kursā māca w (m/m), bet etiķetēs lieto arī m/V un V/V; bez etiķetes teksta veidu nevar pierādīt.',
        'confidence': 'V·X',
        'lecturer': 'Atvērts · 16.d (K23)',
        'status': 'Daļēji atrisināts; politika V',
    },
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def source_inventory():
    rows = []
    for source in SOURCES:
        path = ROOT / source['file']
        rows.append({
            **source,
            'bytes': path.stat().st_size if path.exists() else None,
            'sha256': _sha256(path) if path.exists() else None,
        })
    return rows


# Which authority each resolution actually rests on.  A source quotation is not
# a chemistry law, and neither is a convention the course happens to use; the
# card has to say which one it is using.
WARRANT_KINDS = {
    'source': 'Avota teksts',
    'chemistry': 'Ķīmijas likums ārpus avota',
    'arithmetic': 'Aritmētika un mērvienības',
    'convention': 'Kursa vai dokumenta konvencija',
    'external': 'Ārējs avots — šajā darbvietā nav pārbaudīts',
}

WARRANT = {
    'K1': 'external',      # SI mole definition; the Brochure was not reopened here
    'K2': 'source',        # the gap is a property of B's own bands
    'K3': 'chemistry',     # α depends on concentration; α = 1 is an exercise assumption
    'K4': 'chemistry',     # base constant vs acid constant, and the NH4OH species
    'K5': 'convention',    # M = mol/L is a course writing habit
    'K6': 'arithmetic',    # g/mL · L needs the 1000 factor
    'K7': 'source',        # duplicate (7) and missing (8) are C's own labels
    'K8': 'source',        # KOH header, vienmolāra, kalcija karbonāta — all in B
    'K9': 'chemistry',     # ratio comes from the balanced equation
    'K10': 'source',       # 0,88 % and 0,9 % are both printed in the handouts
    'K11': 'arithmetic',   # m/V and w/w readings of the same line
    'K12': 'arithmetic',   # M = 98 against M = 98,08
    'K13': 'chemistry',    # γ denominator is solution volume, not solvent volume
    'K14': 'arithmetic',   # conditional recomputation with a different ρ
    'K15': 'convention',   # no single sig-fig policy in the keys
    'K16': 'external',     # identity of formalin outside the handouts
    'K17': 'chemistry',    # solute mass vs solution mass; additive volumes
    'K18': 'arithmetic',   # the printed sum does not add up
    'K19': 'arithmetic',   # dose interval is arithmetic on the printed range
    'K20': 'arithmetic',   # powder denominator against solution volume
    'K21': 'arithmetic',   # 13 490 mg and 0,00028 mol/mL
    'K22': 'source',       # typography, quoted from D/E/F
    'K23': 'convention',   # m/m, m/V and V/V are labels, not one quantity
}

FIDELITY = {
    'verbatim': 'burtisks citāts',
    'normalized': 'citāts ar atjaunotiem augšrakstiem',
    'elided': 'citāts ar izlaistu starpdaļu (…)',
    'reconstructed': 'formula pārzīmēta no avota izklājuma',
}

_CLAIMS = None


def refresh_claims():
    """Load build/qa/source-claims.json, but only while it still matches the files."""
    global _CLAIMS
    path = QA / 'source-claims.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        _CLAIMS = None
        return None
    if not data.get('sources'):
        _CLAIMS = None
        return None
    for row in data['sources']:
        target = ROOT / row['file']
        if not target.exists() or _sha256(target) != row.get('sha256'):
            _CLAIMS = None
            return None
    _CLAIMS = {(record['id'], record['source'], record['location'], record['quote']): record
               for record in data.get('quotes', [])}
    return _CLAIMS


def claims():
    return _CLAIMS if _CLAIMS is not None else refresh_claims() or {}


def validate():
    errors = []
    ids = [item['id'] for item in CONFLICTS]
    if ids != [f'K{i}' for i in range(1, 24)]:
        errors.append(f'conflict ids are not K1–K23 in order: {ids}')
    for item in CONFLICTS:
        if not item.get('sources'):
            errors.append(f"{item['id']}: no source record")
        for source in item.get('sources', []):
            if not source.get('source') or not source.get('location'):
                errors.append(f"{item['id']}: source location missing; entry must not be marked verified")
            if not source.get('quote'):
                errors.append(f"{item['id']}: short source excerpt missing")
            if source.get('kind', 'verbatim') not in FIDELITY:
                errors.append(f"{item['id']}: unknown quote kind {source.get('kind')!r}")
        if item['id'] not in WARRANT:
            errors.append(f"{item['id']}: warrant kind missing")
        elif WARRANT[item['id']] not in WARRANT_KINDS:
            errors.append(f"{item['id']}: unknown warrant kind {WARRANT[item['id']]!r}")
        for key in ('topic', 'analysis', 'warrant', 'confidence', 'lecturer', 'status'):
            if not item.get(key):
                errors.append(f"{item['id']}: {key} missing")
    return errors


def _source_field(item_id, source):
    location = source.get('location') or 'Vieta nav norādīta'
    quote = source.get('quote') or 'Citāts nav norādīts'
    kind = source.get('kind', 'verbatim')
    record = claims().get((item_id, source.get('source'), location, quote))
    if record and record.get('observed') == kind:
        verdict = f'Pārbaudīts avotā {OPENED}: {FIDELITY[kind]}. Vieta: {record.get("scope", "—")}.'
        cls = 'conflict-check is-checked'
    else:
        verdict = ('Nav pārbaudīts: skenēšanas atskaite trūkst, avots mainījies vai '
                   'citāts neatbilst deklarētajam veidam.')
        cls = 'conflict-check is-unchecked'
    return (
        '<div class="conflict-source-record">'
        f'<dt>Avots</dt><dd>{html.escape(source.get("source", "—"))}</dd>'
        f'<dt>Vieta</dt><dd class="conflict-loc">{html.escape(location)}</dd>'
        f'<dt>Citāts</dt><dd class="conflict-quote">{html.escape(quote)}</dd>'
        f'<dt>Citāta veids</dt><dd class="conflict-kind">{html.escape(FIDELITY[kind])}</dd>'
        f'<dt>Pārbaude</dt><dd class="{cls}">{html.escape(verdict)}</dd>'
        '</div>'
    )



def render():
    refresh_claims()
    inventory = source_inventory()
    rows = []
    for source in inventory:
        short_sha = (source['sha256'] or '—')[:12]
        rows.append(
            '<tr>'
            f'<th scope="row">{html.escape(source["id"])}</th>'
            f'<td>{html.escape(source["file"])}</td>'
            f'<td>{html.escape(source["kind"])}</td>'
            f'<td class="num">{html.escape(source["pages"])}</td>'
            f'<td><code>{html.escape(short_sha)}</code></td>'
            f'<td>{html.escape(source["opened"])}</td>'
            f'<td>{html.escape(source["role"])}</td>'
            '</tr>'
        )
    table = (
        '<div class="table-wrap compact">'
        '<table data-unit-exempt="source-inventory">'
        '<caption>25. tabula. Avotu inventārs: fails, apjoms, SHA-256 un atvēršanas datums</caption>'
        '<thead><tr><th scope="col">ID</th><th scope="col">Fails</th><th scope="col">Tips</th>'
        '<th scope="col">Lpp.</th><th scope="col">SHA-256</th><th scope="col">Atvērts</th>'
        '<th scope="col">Loma</th></tr></thead>'
        '<tbody>' + ''.join(rows) + '</tbody></table>'
        '</div>'
    )

    index_items = ''.join(
        f'<li><a href="#k-k{html.escape(item["id"][1:])}">{html.escape(item["id"])} · {html.escape(item["topic"])}</a></li>'
        for item in CONFLICTS
    )
    index = (
        '<nav class="conflict-index-nav" aria-label="Avotu konfliktu saraksts">'
        '<h4>Konfliktu saraksts</h4>'
        '<p class="muted">Saite ved uz attiecīgo konfliktu. Ieraksti ir aizvērti; atveriet tos ar kopsavilkuma rindu. Filtrs nav vajadzīgs, jo visi 23 ieraksti ir vienā sarakstā.</p>'
        f'<ol class="conflict-index">{index_items}</ol>'
        '</nav>'
    )

    cards = []
    for item in CONFLICTS:
        source_records = ''.join(_source_field(item['id'], source) for source in item['sources'])
        rows = [claims().get((item['id'], s.get('source'), s.get('location'), s.get('quote')))
                for s in item['sources']]
        checked = [r for s, r in zip(item['sources'], rows)
                   if r and r.get('observed') == s.get('kind', 'verbatim')]
        if rows and len(checked) == len(item['sources']):
            kinds = {r['observed'] for r in checked}
            verification = (f'Pārbaudīts avotā {OPENED}: visi {len(rows)} fragmenti '
                            f'atrasti norādītajā vietā.')
            if 'reconstructed' in kinds:
                verification += ' Daļa formulu pārzīmēta, jo teksta slānis tās nenes.'
        else:
            verification = ('Nav pārbaudīts: skenēšanas atskaite trūkst, avots mainījies '
                            'vai kāds fragments neatbilst deklarētajam veidam.')
        warrant_kind = WARRANT.get(item['id'], 'source')
        cards.append(
            f'<details class="conflict" id="k-k{item["id"][1:]}">'
            f'<summary><span class="conflict-id">{html.escape(item["id"])}</span> '
            f'<span class="conflict-topic">{html.escape(item["topic"])}</span> '
            f'<span class="conflict-meta">{html.escape(item["confidence"])} · {html.escape(item["status"])}</span></summary>'
            '<div class="conflict-grid">'
            '<section class="conflict-part conflict-source" aria-label="Avotā">'
            '<h4>Avotā</h4>'
            f'<dl class="conflict-fields">{source_records}</dl>'
            '</section>'
            '<section class="conflict-part conflict-analysis" aria-label="Dokumenta traktējums">'
            '<h4>Dokumenta traktējums</h4>'
            f'<p>{html.escape(item["analysis"])}</p>'
            '<dl class="conflict-fields">'
            f'<dt>Pamatojuma veids</dt><dd class="conflict-warrant-kind">{html.escape(WARRANT_KINDS[warrant_kind])}</dd>'
            f'<dt>Pamatojums</dt><dd>{html.escape(item["warrant"])}</dd>'
            f'<dt>Ticamība</dt><dd>{html.escape(item["confidence"])}</dd>'
            '</dl>'
            '</section>'
            '<section class="conflict-part conflict-policy" aria-label="Neatrisinātais">'
            '<h4>Neatrisinātais un statuss</h4>'
            '<dl class="conflict-fields">'
            f'<dt>Docētāja statuss</dt><dd>{html.escape(item["lecturer"])}</dd>'
            f'<dt>Risinājuma statuss</dt><dd class="conflict-status">{html.escape(item["status"])}</dd>'
            f'<dt>Pārbaude</dt><dd class="conflict-verification">{html.escape(verification)}</dd>'
            f'<dt>Datums</dt><dd>{OPENED}</dd>'
            '</dl>'
            '</section>'
            '</div>'
            '</details>'
        )

    return (
        '<p class="conflict-intro">Katrs ieraksts atsevišķi rāda <strong>avota tekstu</strong>, '
        '<strong>dokumenta traktējumu</strong> un <strong>neatrisināto politiku</strong>. '
        'Trīs daļas nav sajauktas: citāts paliek citāts, aprēķins paliek aprēķins, bet '
        'docētāja neapstiprinātā izvēle paliek redzama. Katrs fragments tiek saukts par '
        'pārbaudītu tikai tad, ja skenēšanas atskaite atrod to norādītajā vietā un avota '
        'baiti nav mainījušies; citāta veids pasaka, vai tas ir burtisks, ar izlaistu '
        'starpdaļu, ar atjaunotiem augšrakstiem vai pārzīmēta formula. “Pamatojuma veids” '
        'nošķir avota tekstu no ķīmijas likuma, aritmētikas, kursa konvencijas un ārēja '
        'avota, kas šajā darbvietā nav pārbaudīts.</p>'
        + table + index + '<div class="conflict-list">' + ''.join(cards) + '</div>'
    )


def audit(doc):
    errors = []
    cards = re.findall(r'<details class="conflict" id="k-k(\d+)">([\s\S]*?)</details>', doc)
    if [int(number) for number, _ in cards] != list(range(1, 24)):
        errors.append(f'conflict cards are not K1–K23 in order: {[n for n, _ in cards]}')
    for number, body in cards:
        for required in ('conflict-source', 'conflict-analysis', 'conflict-policy',
                         'Avotā', 'Dokumenta traktējums', 'Neatrisinātais un statuss',
                         'Pamatojuma veids', 'Pamatojums', 'Ticamība', 'Docētāja statuss',
                         'Risinājuma statuss', 'Pārbaude', 'Datums', 'Citāta veids'):
            if required not in body:
                errors.append(f'K{number}: missing {required}')
        if 'Pārbaudīts avotā' in body and 'conflict-loc' not in body:
            errors.append(f'K{number}: marked verified without a source location')
        if 'Pārbaudīts avotā' in body and 'is-checked' not in body:
            errors.append(f'K{number}: claims verification without a checked fragment')
        if re.search(r'\sstyle="', body):
            errors.append(f'K{number}: inline style in conflict card')
    if not claims():
        errors.append('source-claims report is missing or stale; every card must stay unverified '
                      'until tools/check_source_claims.py has run against these exact files')
    if doc.count('class="conflict"') != 23:
        errors.append(f"conflict card count {doc.count('class=\"conflict\"')} != 23")
    if '25. tabula. Avotu inventārs' not in doc:
        errors.append('source inventory table is missing')
    for source in SOURCES:
        if source['file'] not in doc:
            errors.append(f"source inventory lacks {source['id']}: {source['file']}")
    k13 = next((body for number, body in cards if number == '13'), '')
    for needle in ('Nosacīta atbilde', 'galīgais tilpums nav dots'):
        if needle not in k13:
            errors.append(f'K13 acceptance detail missing: {needle}')
    return errors


def report():
    QA.mkdir(parents=True, exist_ok=True)
    data = {
        'schema': 'f04-conflict-ledger/2',
        'opened': OPENED,
        'sources': source_inventory(),
        'warrant_kinds': WARRANT,
        'warrant_glossary': WARRANT_KINDS,
        'verified_fragments': len(claims()),
        'conflicts': CONFLICTS,
        'counts': {
            'sources': len(SOURCES),
            'conflicts': len(CONFLICTS),
        },
    }
    (QA / 'conflicts.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return f"conflicts: {len(CONFLICTS)} records; sources: {len(SOURCES)}; report build/qa/conflicts.json"
