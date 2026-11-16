"""Learning, mistakes and terminology data for the Topic 13 master.

Glossary / species / usage / contrasts are owned by tools/termbase.py (Task 04).
This module re-exports them so existing build_master call sites keep working.

Task T07: wrong-answer feedback (mistake_qa_rationale), prompt→card links
(PROMPT_QA_LINKS) and retrieval modes (retrieval_mode) are defined here and
validated/exported by tools/recall_matrix.py; qa/t07b holds the evidence.
"""
from __future__ import annotations

import re
from collections import namedtuple

import termbase as TB

# ---------------------------------------------------------------- recall prompts
# (concept id, chapter, question, answer, kind, criterion, mistake, link)
# pid is derived from concept id and kind, so the answer key, coverage matrix and
# weak-spots store use the same identifier even when a chapter repeats a prompt.
Prompt = namedtuple("Prompt", "pid cid ch q a kind criterion mistake link")

_RAW_PROMPTS = [
    (
        'C01', 1,
        'Pabeidz: oksidēšanās ir elektronu ______, un elementa oksidēšanas pakāpe ______.',
        'Atdošana; paaugstinās. Piemērs: S(+4) formāli pāriet S(+6), atdodot 2 e⁻.',
        'cloze', '', '', '',
    ),
    (
        'C02', 1,
        'Pabeidz: reducēšanās ir elektronu ______, un oksidēšanas pakāpe ______.',
        'Pieņemšana; pazeminās. Piemērs: O 0 → −2 (formāli); O₂ nav 2[[w:O^2-]] joni.',
        'cloze', '', '', '',
    ),
    (
        'C03', 1,
        'Kāpēc oksidētājs pats reducējas, lai gan tā nosaukums sākas ar “oksidē”?',
        'Oksidētājs pieņem elektronus, tāpēc tā oksidēšanas pakāpe pazeminās un tas pats reducējas. Vārds “oksidētājs” apzīmē lomu pret otru vielu: tā oksidē otru vielu, bet pati tiek reducēta. Piemērs: KMnO₄ pieņem 5 e⁻ un reducējas par Mn²⁺.',
        'explain', 'Jānosauc elektronu pieņemšana, pakāpes pazemināšanās un tas, ka oksidēšana attiecas uz otru vielu.', '', '',
    ),
    (
        'C04', 1,
        'Kāpēc reducētājs pats oksidējas, lai gan tas “reducē” otru vielu?',
        'Reducētājs atdod elektronus, tāpēc tā oksidēšanas pakāpe paaugstinās un tas pats oksidējas. Vārds “reducētājs” apzīmē lomu: tas reducē otru vielu, bet pats tiek oksidēts. Piemērs: Fe²⁺ atdod 1 e⁻ un kļūst Fe³⁺.',
        'explain', 'Jānosauc elektronu atdošana, pakāpes paaugstināšanās un tas, ka reducēšanās attiecas uz otru vielu.', '', '',
    ),
    (
        'C05', 1,
        'Kāpēc “oksidētājs” un “reducētājs” ir lomas, nevis vielas pastāvīga etiķete?',
        'Viena viela dažādos apstākļos var būt gan oksidētājs, gan reducētājs. Piemērs: H₂O₂ vai SO₃²⁻; lomu nosaka otrs reakcijas partneris un vide.',
        'explain', 'Jānosauc, ka lomu nosaka partneris/vide, un jāmin piemērs (H₂O₂ vai SO₃²⁻).', '', '',
    ),
    (
        'C09', 1,
        'Kas mainītos jonu vienādojumā, ja oksidēšanas pakāpi sāktu rakstīt kā jonu lādiņu?',
        'Rastos nepareizas daļiņas: oksidēšanas pakāpe ir formāla uzskaite (zīme pirms skaitļa, +4), bet jonu lādiņš ir reāls (skaitlis pirms zīmes, [[Fe^3+]]). SO₂ ir kovalenta molekula, tāpēc tajā nav atsevišķu jonu ar lādiņu 4+. Jonu vienādojumā raksta tikai reāli eksistējošas daļiņas, tāpēc abus pierakstus nedrīkst sajaukt.',
        'explain', 'Jānošķir formālā pakāpe (+4) no reālā jonu lādiņa (4+) un jānosauc, ka SO₂ nav jonu.', '', '',
    ),
    (
        'C11', 1,
        'Kāpēc SO₂ un SO₃ aprēķinos bieži raksta [[w:S^4+]] un [[w:S^6+]], lai gan tādu jonu tur nav?',
        'Pareizi raksta oksidēšanas pakāpi kā S(+4) un S(+6) (zīme pirms skaitļa). Pieraksts [[w:S^4+]] / [[w:O^2-]] ir lādiņa forma un maldina, jo SO₂/SO₃ ir kovalenti; tādu jonu tur nav. Brīdinājums jāpatur prātā, rakstot jonu vienādojumus.',
        'explain', 'Jānosauc SO₂/SO₃ kovalentā uzbūve un formālā pakāpe S(+4)/S(+6), nevis jonu lādiņš.', '', '',
    ),
    (
        'C12', 1,
        'Uzraksti dzelzs(III) jonu un sulfāta jonu ar pareizu lādiņa pierakstu.',
        '[[Fe^3+]] un [[SO4^2-]]. Lādiņā vispirms skaitlis, tad zīme; oksidēšanas pakāpē vispirms zīme, tad skaitlis.',
        'cloze', '', '', '',
    ),
    (
        'C06', 1,
        'Students saka: “KMnO₄ ir reducētājs, jo tas reducējas par Mn²⁺.” Kurš jēdziens ir sajaukts?',
        'KMnO₄ pieņem elektronus, tāpēc tas ir oksidētājs un pats reducējas. Reducētājs ir Fe²⁺, kas atdod elektronus. MnO₄⁻/Mn²⁺ ir viena pāra divas formas, nevis divas nesaistītas vielas.',
        'spot', 'Jānosauc, ka KMnO₄ pieņem e⁻ un ir oksidētājs; jāatdala oksidētājs no reducētāja.', 'M01', '#ch1',
    ),
    (
        'C08', 1,
        'Students saka: “Ja atomi abās pusēs sakrīt, lādiņš nav jāpārbauda.” Kas iztrūkst?',
        'Lādiņam arī jāsakrīt: cik elektronu atdots, tik pieņemts. Jonu vienādojumā lādiņa bilance ir obligāta; atomu bilance vien to neaizstāj.',
        'spot', 'Jānosauc lādiņa bilance un atdoto = pieņemto elektronu skaits.', 'M03', '#ch1',
    ),
    (
        'C14', 1,
        'Students sāk pusreakciju ar e⁻ un pēc tam pieliek H⁺, “lai sanāk”. Kāpēc šī secība ir nepareiza?',
        'Vispirms līdzsvaro citus atomus, tad skābekli ar H₂O, tad ūdeņradi ar H⁺, tad lādiņu ar e⁻. Ja sāk ar e⁻, H⁺ un lādiņš sāk pretrunīgi mainīties, un rezultāts bieži nesabalansējas.',
        'spot', 'Jānosauc pareizā secība: atomi → O ar H₂O → H ar H⁺ → lādiņš ar e⁻.', 'M04', '#ch1',
    ),
    (
        'C15', 2,
        'Kāpēc viena atsevišķa elektroda potenciālu nevar izmērīt?',
        'Ķēde nav noslēgta. Lai būtu potenciālu starpība, vajag otru elektrodu un mērinstrumentu; iegūst galvaniskā elementa EDS, nevis viena elektroda absolūto potenciālu.',
        'explain', 'Jānosauc atvērta ķēde un nepieciešamība pēc otrā elektroda; rezultāts ir EDS.', '', '',
    ),
    (
        'C18', 2,
        'Kā aprēķina galvaniskā elementa EDS no diviem elektrodu potenciāliem?',
        'E = E(katods) − E(anods), kur abi ir reducēšanas potenciāli un E₁ ir lielākais. Piemērs: Cu/Zn elements: 0,337 − (−0,763) = 1,100 V.',
        'cloze', '', '', '',
    ),
    (
        'C19', 2,
        'Kāpēc ūdeņraža standartelektroda potenciālu pieņem vienādu ar nulli?',
        'Tā ir starptautiska atskaites vienošanās. Absolūto elektrodu potenciālu nevar izmērīt, tāpēc visus salīdzina pret vienu noteiktu elektrodu, kuram piešķir 0,00 V.',
        'explain', 'Jānosauc atskaites vienošanās un absolūtā potenciāla neizmērāmība.', '', '',
    ),
    (
        'C21', 2,
        'Kāpēc potenciālu tabulā visi ieraksti ir reducēšanās virzienā?',
        'Lai tos varētu salīdzināt vienā skalā: katrs ieraksts ir Ox + ne⁻ → Red. Jo lielāks E°, jo stiprāks oksidētājs ir Ox. Ja vajag oksidēšanās pusreakciju, to apgriež un E° zīmi maina, bet tabulu nemaina.',
        'explain', 'Jānosauc vienotā reducēšanās konvencija un E° saistība ar oksidētāja stiprumu.', '', '',
    ),
    (
        'C25', 2,
        'Kas mainītos E° zīmē un lielumā, ja pusreakciju apgrieztu otrādi?',
        'Zīme mainītos: E° reducēšanai kļūtu −E° oksidēšanai. Lielums nemainītos, un E° netiktu reizināts ar stehiometrisko koeficientu, jo tas ir intensīvs lielums.',
        'explain', 'Jānosauc zīmes maiņa, lieluma nemainība un intensivitāte.', '', '',
    ),
    (
        'C26', 2,
        'Kāpēc E° un E°′ nedrīkst likt vienā darba kolonnā?',
        'Tie attiecas uz dažādu pH: E° parasti pH 0, E°′ pH 7. Ja tos sajauc, šķietamais elektronu plūsmas virziens var apgriezties. Piemērs: H⁺/H₂ ir 0,00 V kā E°, bet −0,414 V kā E°′ (A5).',
        'explain', 'Jānosauc pH 0 un pH 7 atšķirība un jāmin piemērs ar H⁺/H₂.', '', '',
    ),
    (
        'C26', 2,
        'Tabulā ir H⁺/H₂ = 0,00 V un NAD⁺/NADH = −0,3391 V. Kura konvencija ir sajaukta un kāpēc?',
        'Sajaukta E° ar E°′ (A5). 0,00 V ir E° (pH 0); bioloģiskais NAD skaitlis ir E°′ (pH 7). Vienā darba kolonnā abi nedrīkst stāvēt: pie E°′ H⁺/H₂ ir −0,414 V, un sajaukšana apgriež šķietamo elektronu plūsmu starp H₂ un NAD.',
        'spot', 'Jānosauc A5 un jāpaskaidro, ka 0,00 V ir E°, bet NAD skaitlis ir E°′.', 'M09', '#ch2',
    ),
    (
        'C26', 2,
        'Pārrēķini E°(O₂/H₂O) = +1,229 V uz E°′ pie pH 7; parādi m, n un zīmi.',
        'm = 4 (H⁺), n = 4 (e⁻). E°′ = E° − 0,0592·(m/n)·pH = 1,229 − 0,0592·(4/4)·7 = 1,229 − 0,4144 = 0,8146 V ≈ +0,815 V. Mīnuss: augstāks pH pazemina E pāriem ar H⁺.',
        'calc', '', '', '',
    ),
    (
        'C27', 2,
        'Ko pierāda ΔE > 0 un ko tas nepierāda?',
        'ΔE > 0 pierāda, ka reakcija ir termodinamiski iespējama. Tas nepasaka, cik ātri tā notiks; kinētika var būt ļoti lēna.',
        'explain', 'Jānosauc termodinamiskā iespējamība un kinētikas neatkarība.', '', '',
    ),
    (
        'C24', 2,
        'Students dubulto pusreakciju Fe³⁺ + e⁻ → Fe²⁺ un raksta E° = 2·0,77 V. Kas nepareizi?',
        'E° ir intensīvs lielums; tas paliek 0,77 V. Mainās z un ΔG°, nevis E°. Ja pusreakciju dubulto, ΔG° dubultojas, bet potenciāls nemainās.',
        'spot', 'Jānosauc E° nemainība un ΔG°/z maiņa.', 'M20', '#ch2',
    ),
    (
        'C29', 3,
        'Uzraksti Nernsta vienādojumu vispārīgā formā.',
        'E = E° + (RT/nF)·ln([Ox]/[Red]). Pēc pārejas uz decimāllogaritmu 298 K: E = E° + (0,0592/n)·lg([Ox]/[Red]).',
        'cloze', '', '', '',
    ),
    (
        'C31', 3,
        'Kāpēc visā dokumentā lieto 0,0592 V, nevis 0,0591 V?',
        '2,303·RT/F pie 298,15 K ir 0,05917 V (ar ln 10 = 2,3026 — 0,05916 V). Noapaļojot līdz trim zīmīgajiem cipariem, 0,0592. Viens konstants lielums visā dokumentā novērš atšķirības starp piemēriem.',
        'explain', 'Jānosauc 2,303RT/F ≈ 0,05917 V (0,05916 ar ln 10) un noapaļošana uz 0,0592.', '', '',
    ),
    (
        'C33', 3,
        'Kā pareizi orientēt Nernsta koeficientu?',
        'Redukcijai Ox + ne⁻ → Red koeficientā augšā ir [Ox], apakšā [Red]. Apgriezta attiecība maina zīmi un ir bieža kļūda.',
        'cloze', '', '', '',
    ),
    (
        'C35', 3,
        'Kā [H⁺] ienāk MnO₄⁻/Mn²⁺ un Cr₂O₇²⁻/Cr³⁺ Nernsta izteiksmēs?',
        'Attiecīgi kā [H⁺]⁸ un [H⁺]¹⁴, jo pusreakcijās ir 8 un 14 H⁺. Tāpēc pH ietekme ir daudz spēcīgāka nekā vienkārša lineāra attiecība.',
        'cloze', '', '', '',
    ),
    (
        'C36', 3,
        'Kāpēc ūdens un tīras cietas vielas neietilpst Nernsta koeficientā?',
        'To aktivitāte ir aptuveni 1, tāpēc tās nemaina koeficienta vērtību. Koeficientā paliek izšķīdušās un gāzveida formas; gāzes raksta kā daļējo spiedienu, nevis molāro koncentrāciju.',
        'explain', 'Jānosauc aktivitāte 1 un gāzu daļējais spiediens.', '', '',
    ),
    (
        'C36', 3,
        'Kāpēc H₂O aktivitāti Nernsta koeficientā pieņem vienādu ar 1?',
        'Šķīdinātājs ir pārpildā; tā aktivitāte standarta apstākļos ir aptuveni 1. Tāpēc H₂O koeficientā neraksta. Ja H₂O ir reaģents vai produkts, tas joprojām paliek ārpus koeficienta.',
        'explain', 'Jāatbild, ka šķīdinātāja aktivitāte ≈1, un jāsecina, ka H₂O koeficientā neietilpst.', '', '',
    ),
    (
        'C36', 3,
        'Kas ir n Cr₂O₇²⁻/Cr³⁺ Nernsta izteiksmē?',
        'n = 6 (seši elektroni pusreakcijā). H⁺ pakāpe 14 un Cr³⁺ pakāpe 2 ir koeficientā, nevis n vietā.',
        'cloze', '', '', '',
    ),
    (
        'C37', 3,
        'Aprēķini E(MnO₄⁻/Mn²⁺), ja [MnO₄⁻] = [Mn²⁺] = 1 un pH = 3.',
        'E = 1,51 + (0,0592/5)·lg([H⁺]⁸) = 1,51 + 0,01184·(−24) = 1,226 V. Pie pH 0 tas būtu 1,510 V.',
        'calc', '', '', '',
    ),
    (
        'C38', 3,
        'Kāpēc permanganāta oksidējošā spēja strauji krītas, paaugstinoties pH?',
        'Tāpēc, ka pusreakcijā ir 8 H⁺ un Nernsta izteiksmē tie ir astotajā pakāpē. Samazinoties [H⁺], E samazinās par 0,0947 V uz katru pH vienību (pie citām vienības aktivitātēm).',
        'explain', 'Jānosauc 8 H⁺ pakāpe un slīpums −0,0947 V/pH.', '', '',
    ),
    (
        'C38', 3,
        'Ko formāli prognozē Nernsts MnO₄⁻/Mn²⁺ pārim pie pH 7?',
        'E ≈ 0,847 V. Brīdinājums: Mn²⁺ nav dominējošā forma neitrālā/bāziskā vidē; tur MnO₄⁻ reducējas līdz MnO₂ (vai MnO₄²⁻). Formālā līnija nav fizikāla šajā pH.',
        'explain', 'Jānosauc E ≈ 0,847 V un formālās līnijas brīdinājums.', '', '',
    ),
    (
        'C30', 3,
        'Aprēķini 2,303·R·T/F pie T = 298,15 K, R = 8,314 J/(mol·K) un F = 96 485 C/mol. Kādu vērtību lieto dokumentā?',
        '2,303·8,314·298,15/96 485 = 0,05917 V (ar ln 10 = 2,3026 — 0,05916 V). Dokumentā to noapaļo līdz 0,0592 V (trīs zīmīgie cipari), lai visos piemēros būtu viena konstante.',
        'calc', '', '', '#ch3',
    ),
    (
        'C34', 3,
        'Cr₂O₇²⁻ + 14H⁺ + 6e⁻ → 2Cr³⁺ + 7H₂O. Ja [Cr³⁺] dubultojas, bet pārējās aktivitātes paliek 1, par cik voltiem mainās E? Lieto 0,0592 V.',
        'Q satur [Cr³⁺]², tāpēc dubultošanās dod lg(1/2²) = −0,602. ΔE = (0,0592/6)·(−0,602) = −0,00594 V ≈ −0,0059 V. E samazinās, jo produkts ir saucējā.',
        'calc', '', '', '#ch3',
    ),
    (
        'C41', 4,
        'Kāpēc reakcijas virzienu pārbauda četros soļos, nevis tikai pēc E°?',
        'E° vien nosaka virzienu tikai pie standarta apstākļiem. Ja potenciāli ir tuvi, pusreakcijā ir H⁺/OH⁻ vai mainās koncentrācijas, E° var būt maldinošs. Tāpēc pēc E° pārbaudes seko vide, Nernsta korekcija un krustpunkta pārbaude.',
        'explain', 'Jānosauc E° ierobežojums un vismaz viens papildu faktors (tuvu potenciāli, H⁺/OH⁻ vai koncentrācija).', '', '',
    ),
    (
        'C42', 4,
        'Kas jādara, ja |ΔE°| ir mazāks par 0,15 V?',
        'Tā ir tuva robeža: E° vien nepietiek. Aprēķina E abiem pāriem ar Nernstu pie reālajām koncentrācijām un pH. 0,15 V pie z = 1 atbilst lg K ≈ 2,5, ko var pārvarēt ar ~340 reižu koncentrāciju starpību.',
        'calc', '', '', '',
    ),
    (
        'C43', 4,
        'Pie kādas HCl koncentrācijas MnO₂ sāk oksidēt Cl⁻ par Cl₂?',
        'Pie [Mn²⁺] = 1 mol/L un p(Cl₂) = 1 bar: 1,23 + 0,1184·lg c = 1,36 − 0,0592·lg c, tātad c ≈ 5,4 mol/L. Ar CRC 1,224 V — 5,8 mol/L. 12 mol/L HCl dod ΔE ≈ +0,06 V; 1 mol/L — nē.',
        'calc', '', '', '',
    ),
    (
        'C44', 4,
        'Kāpēc MnO₄⁻ standartapstākļos var oksidēt Pb²⁺ tikai ar nelielu rezervi?',
        'E°(MnO₄⁻/Mn²⁺) = 1,51 V ir tikai par 0,05 V augstāks par E°(PbO₂/Pb²⁺) = 1,46 V (CRC 1,455 V). Tāpēc ΔE° = +0,05 V un lg K ≈ 4,2 — iespējams, bet tuva robeža; koncentrācijas var mainīt virzienu. Avota 1,80 V ir kļūdains (A3).',
        'explain', 'Jānosauc 1,51 un 1,46 V, ΔE° +0,05 V un tuvās robežas rezerve.', '', '',
    ),
    (
        'C45', 4,
        'Kāpēc PbO₂/Mn²⁺ virzienu pH vien nepagriež?',
        'Tāpēc ka abiem pāriem pusreakcijā ir H⁺ un to slīpumi gandrīz kompensējas: −0,1184 un −0,0947 V/pH. ΔE mainās tikai par 0,024 V uz pH vienību, un krustpunkts būtu [H⁺] ≈ 130 mol/L — nereāli. Virzienu groza [MnO₄⁻]/[Mn²⁺]: pie 15 mol/L HNO₃ līdzsvars iestājas pie [MnO₄⁻] ≈ 0,013·[Mn²⁺].',
        'calc', '', '', '',
    ),
    (
        'C46', 4,
        'Kas mainītos lēmumā, ja E° starpība būtu tuva un pusreakcijā būtu H⁺?',
        'E° vien nepietiktu: vajadzētu Nernsta izteiksmi ar reālo [H⁺] un koncentrācijām. Tuvas starpības dēļ neliela pH vai koncentrācijas maiņa var apgriezt virzienu; tāpēc vispirms aprēķina E abiem pāriem.',
        'explain', 'Jānosauc Nernsta aprēķins ar reālo [H⁺] un virziena apgriešanās iespēja.', '', '',
    ),
    (
        'C47', 4,
        'Pie kādas [H⁺] dihromāts sāk pārspēt hloru, ja pārējās aktivitātes ir 1?',
        'Pie [H⁺] ≈ 1,65 mol/L (pH ≈ −0,22). Tad 1,33 + (0,0592/6)·14·lg[H⁺] = 1,36. Ar mazāku skābumu dihromāts hlorīdu būtiski neoksidē.',
        'calc', '', '', '',
    ),
    (
        'C48', 4,
        'Kāpēc dihromāta titrēšana tolerē hlorīdu?',
        'Dilutā skābē E(Cr₂O₇²⁻/Cr³⁺) ir zemāks par E(Cl₂/Cl⁻). Hlorīds netiek būtiski oksidēts; tikai ļoti koncentrētā skābē dihromāts pārspēj hloru.',
        'explain', 'Jānosauc zems E dilutā skābē un hlorīda neoksidēšana.', '', '',
    ),
    (
        'C50', 4,
        'Kāpēc MnO₂ + HCl dod Cl₂, lai gan E°(MnO₂/Mn²⁺) < E°(Cl₂/Cl⁻)?',
        'Standarta potenciāli ir tuvi, un reakcija notiek karstā koncentrētā HCl: augsta [H⁺] un [Cl⁻] ceļ MnO₂ un Cl₂ potenciālus, bet Cl₂ aizplūst kā gāze. E° ir tikai sākumpunkts.',
        'explain', 'Jānosauc karsta koncentrēta HCl, [H⁺]/[Cl⁻] un Cl₂ aizplūšana.', '', '',
    ),
    (
        'C51', 4,
        'Kāpēc ΔE° > 0 nenozīmē, ka reakcija notiks ātri?',
        'ΔE° > 0 ir tikai termodinamiska iespējamība. Ātrumu nosaka kinētiskā barjera, katalizators un temperatūra; daudzas redoksa reakcijas bez katalizatora ir lēnas. Piemērs: oksalāts ar KMnO₄ istabas temperatūrā sāk lēni.',
        'explain', 'Jānosauc termodinamiskā iespējamība un kinētiskā barjera/ātrums.', '', '',
    ),
    (
        'C52', 4,
        'Kā no ΔE° aprēķina ΔG° un līdzsvara konstanti?',
        'ΔG° = −zFΔE° un lg K = zΔE°/0,0592. Piemērs MnO₄⁻/Fe²⁺: z = 5, ΔE° = 0,74 V, lg K = 62,5.',
        'calc', '', '', '',
    ),
    (
        'C54', 4,
        'Kāpēc E° vien pietiek tikai tad, kad potenciāli ir tālu viens no otra?',
        'Tālu potenciālu gadījumā nelielas koncentrācijas vai pH izmaiņas virzienu neapgriež. Ja potenciāli ir tuvi, pusreakcijā ir H⁺/OH⁻ vai mainās gāzes spiediens, jāaprēķina E ar Nernstu konkrētajos apstākļos.',
        'explain', 'Jānosauc tālu potenciālu noturība un Nernsta nepieciešamība tuvu/mainīgu apstākļu gadījumā.', '', '',
    ),
    (
        'C53', 4,
        'MnO₄⁻ + 5Fe²⁺ + 8H⁺ → Mn²⁺ + 5Fe³⁺ + 4H₂O; ΔE° = 0,74 V, z = 5. Aprēķini lg K ar 0,0592 V.',
        'lg K = z·ΔE°/0,0592 = 5·0,74/0,0592 = 62,5. Tā ir ļoti liela konstante: līdzsvars ir stipri nobīdīts uz produktiem.',
        'calc', '', '', '#ch4',
    ),
    (
        'C49', 4,
        'Students saka: “Dihromāts skābā vidē vienmēr oksidē hlorīdu, tāpēc jebkura skābe der.” Kas jāpārbauda?',
        'Jāpārbauda [H⁺]: tikai ļoti koncentrētā skābē E(Cr₂O₇²⁻) > E(Cl₂); dilutā skābē hlorīds netiek būtiski oksidēts. Krustpunkts ir [H⁺] ≈ 1,65 mol/L (pH ≈ −0,22).',
        'spot', 'Jānosauc [H⁺] slieksnis ≈1,65 mol/L un tas, ka dilutā skābē hlorīds netiek oksidēts.', 'M27', '#ch4',
    ),
    (
        'C56', 5,
        'Kāpēc hemoglobīna kabatā O₂ nav oksidētājs?',
        'O₂ kā oksidētājs darbojas ūdens vidē; hemoglobīna un mioglobīna hidrofobajā kabatā ūdens nav, tāpēc O₂ tur saistojas ar Fe(II) un tiek pārnests saistīts ar Fe(II), nevis reducēts līdz ūdenim.',
        'explain', 'Jānosauc hidrofobā kabata, ūdens neesamība un O₂ saistīšanās ar Fe(II).', '', '',
    ),
    (
        'C57', 5,
        'Nosauc E° halogenīdu pāriem Cl₂/Cl⁻, Br₂/Br⁻ un I₂/I⁻.',
        'Cl₂/Cl⁻ +1,36 V; Br₂/Br⁻ +1,07 V (avotā kļūdaini 0,96 V); I₂/I⁻ +0,54 V. Stiprākais halogēns ir labs oksidētājs, vājākais — vājš.',
        'cloze', '', '', '',
    ),
    (
        'C60', 5,
        'Kāpēc dzelzs ar atšķaidītu sērskābi dod Fe²⁺, nevis Fe³⁺?',
        'H⁺/H₂ potenciāls 0,00 V var oksidēt Fe līdz Fe²⁺, bet ne līdz Fe³⁺, jo Fe³⁺/Fe²⁺ ir +0,77 V. H⁺ nav pietiekami stiprs oksidētājs otrai pakāpei.',
        'explain', 'Jānosauc Fe³⁺/Fe²⁺ 0,77 V un H⁺ 0,00 V nepietiekamība.', '', '',
    ),
    (
        'C61', 5,
        'Cik elektronu MnO₄⁻ pieņem skābā, neitrālā un bāziskā vidē?',
        'Skābā: 5 e⁻, produkts Mn²⁺; neitrālā: 3 e⁻, produkts MnO₂; bāziskā: 1 e⁻, produkts MnO₄²⁻.',
        'cloze', '', '', '',
    ),
    (
        'C63', 5,
        'Uzraksti Cr₂O₇²⁻ reducēšanās pusreakciju skābā vidē.',
        '[[Cr2O7^2-]] + 14H⁺ + 6e⁻ → 2[[Cr^3+]] + 7H₂O. Hroma oksidēšanas pakāpe +6 → +3, tāpēc 6 e⁻.',
        'cloze', '', '', '',
    ),
    (
        'C64', 5,
        'Kāpēc hroma(VI) savienojumi skābā vidē ir stipri oksidētāji, bet bāziskā — vāji?',
        'H⁺ ir pusreakcijā un Nernsta izteiksmē 14. pakāpē. Augstā skābumā E ir liels, bāziskā — zems; tāpēc bāziskā vidē Cr(III) var oksidēt līdz Cr(VI).',
        'explain', 'Jānosauc H⁺ 14. pakāpe un E atkarība no pH.', '', '',
    ),
    (
        'C65', 5,
        'Kāpēc skābes izdala ūdeņradi no metāliem ar negatīvu potenciālu?',
        'H⁺/H₂ ir 0,00 V. Metāls ar negatīvu E° ir reducētājs pret H⁺; H⁺ tiek reducēts līdz H₂, bet metāls oksidējas līdz jonam.',
        'explain', 'Jānosauc H⁺/H₂ 0,00 V un negatīvs metāla E°.', '', '',
    ),
    (
        'C66', 5,
        'Kāpēc HNO₃ ar dažādiem metāliem dod NO₂, NO vai pat NH₄⁺?',
        'Nitrāta reducēšanās produktu skaits un veids atkarīgs no skābes atšķaidījuma un reducētāja stipruma. Koncentrēta HNO₃ ar vāju reducētāju dod NO₂; ļoti atšķaidīta ar stipru reducētāju var dot NH₄⁺.',
        'explain', 'Jānosauc HNO₃ atšķaidījums un reducētāja stiprums.', '', '',
    ),
    (
        'C69', 5,
        'Kuri savienojumi LEC sauc par ūdeņraža pārnesējiem?',
        'C vitamīns (askorbīnskābe), NADH, FADH₂ un E vitamīns (α-tokoferols). Tie ir reducētās formas, kas var atdot ūdeņradi/elektronus.',
        'cloze', '', '', '',
    ),
    (
        'C72', 5,
        'Kā mainītos H₂S oksidēšanās produkts, ja lietotu vāju, bet pēc tam stipru oksidētāju?',
        'Ar vāju oksidētāju veidojas brīvs sērs S. Stipri oksidētāji ([[MnO4^-]], [[Cr2O7^2-]], HNO₃) var oksidēt tālāk līdz sulfātam [[SO4^2-]]. Produkts ir atkarīgs no oksidētāja stipruma, ne tikai no sēra daudzuma.',
        'explain', 'Jānosauc S ar vāju oksidētāju un SO₄²⁻ ar stipru oksidētāju.', '', '',
    ),
    (
        'C73', 5,
        'Kādas ir SO₄²⁻/SO₃²⁻ E° vērtības skābā un bāziskā vidē?',
        'Skābā: +0,20 V; bāziskā: −0,93 V. Tā ir tā pati pH ietekme, ko rāda Nernsts, nevis divi neatkarīgi pāri.',
        'cloze', '', '', '',
    ),
    (
        'C78', 5,
        'Kāpēc H₂O₂ var būt gan oksidētājs, gan reducētājs?',
        'Tas ir atkarīgs no otrā partnera un no tā, kura H₂O₂ daļa mainās. Kā oksidētājs H₂O₂ pieņem 2 e⁻ un dod H₂O: [[H2O2]] + 2H⁺ + 2e⁻ → 2H₂O. Kā reducētājs tas atdod 2 e⁻ un dod O₂: [[H2O2]] → O₂ + 2H⁺ + 2e⁻.',
        'explain', 'Jānosauc abas lomas un abus produktus (H₂O un O₂).', '', '',
    ),
    (
        'C62', 5,
        'E°(MnO₄⁻/Mn²⁺) = 1,51 V, E°(MnO₄⁻/MnO₂) = 0,60 V, E°(MnO₄⁻/MnO₄²⁻) = 0,56 V un E°(Fe³⁺/Fe²⁺) = 0,77 V. Kurā vidē ΔE pret Fe³⁺/Fe²⁺ ir lielākā?',
        'Skābā: 1,51 − 0,77 = +0,74 V. Neitrālā: 0,60 − 0,77 = −0,17 V. Bāziskā: 0,56 − 0,77 = −0,21 V. Lielākā ir skābajā vidē; neitrālā un bāziskā permanganāts pret Fe³⁺ vairs nav spontāns.',
        'calc', '', '', '#ch5',
    ),
    (
        'C74', 5,
        'Oksidējoties līdz S₄O₆²⁻, viena S₂O₃²⁻ daļiņa atdod cik elektronu? Cik molu S₂O₃²⁻ ir 12,35 mL 0,0200 mol/L šķīduma?',
        '2S₂O₃²⁻ → S₄O₆²⁻ + 2e⁻, tātad viena daļiņa atdod 1 e⁻ (z = 1). n = c·V = 0,0200·0,01235 = 2,470·10⁻⁴ mol.',
        'calc', '', '', '#ch5',
    ),
    (
        'C58', 5,
        'Students saka: “pH ietekmē visus redoksa pārus vienādi.” Kāpēc tas nav pareizi Cl₂/Cl⁻ gadījumā?',
        'Cl₂/Cl⁻ pusreakcijā nav H⁺ vai OH⁻, tāpēc pH tieši nemaina E. MnO₄⁻/Mn²⁺ pusreakcijā ir 8 H⁺, tāpēc pH ietekme ir spēcīga. Vienāda ietekme nav vispārīgs noteikums.',
        'spot', 'Jānosauc Cl₂/Cl⁻ bez H⁺ un MnO₄⁻ ar 8 H⁺.', 'M06', '#ch5',
    ),
    (
        'C81', 6,
        'Nosauc sešus kursa jonu-elektronu metodes soļus.',
        '1) pārbaudi virzienu pēc potenciāliem; 2) uzraksti abas pusreakcijas; 3) atrodi reizinātājus vienādam elektronu skaitam; 4) sareizini un saskaiti; 5) saīsini līdz jonu vienādojumam; 6) pievieno skatītājonus un uzraksti molekulāro vienādojumu.',
        'cloze', '', '', '',
    ),
    (
        'C82', 6,
        'Kā skābā vidē līdzsvarot skābekli un ūdeņradi pusreakcijā?',
        'Vispirms līdzsvaro citus atomus, tad skābekli ar H₂O, tad ūdeņradi ar H⁺, tad lādiņu ar e⁻. Šajā secībā H⁺ skaits izriet no skābekļa, nevis otrādi.',
        'cloze', '', '', '',
    ),
    (
        'C84', 6,
        'Kā atrast pusreakcijas reizinātāju?',
        'Reizinātājs = elektronu mazākais kopīgais daudzkārtnis ÷ elektronu skaits šajā pusreakcijā. Piemērs: 5 un 2 e⁻ → LCM 10; reizinātāji 2 un 5.',
        'calc', '', '', '',
    ),
    (
        'C85', 6,
        'Kāpēc reizinātāji jāsaīsina līdz mazākajiem veselajiem skaitļiem?',
        'Citādi vienādojums ir pareizs pēc būtības, bet nav stehiometriski vienkāršākais. Piemēram, 2:6 jāsaīsina uz 1:3; pretējā gadījumā visi koeficienti palielinās divreiz.',
        'explain', 'Jānosauc mazākie veselie koeficienti un piemērs 2:6 → 1:3.', '', '',
    ),
    (
        'C86', 6,
        'Kas notiek ar elektroniem, saskaitot abas pusreakcijas?',
        'Tiem jāsaīsinās pilnībā: cik atdod, tik pieņem. Galīgajā jonu vienādojumā elektroni neparādās.',
        'cloze', '', '', '',
    ),
    (
        'C87', 6,
        'Kāpēc jonu vienādojumā skatītājoni netiek rakstīti?',
        'Skatītājoni (K⁺, Na⁺, SO₄²⁻) ir abās pusēs vienāda daudzumā un saīsinās. Jonu vienādojums rāda tikai tās daļiņas, kas mainās; skatītājonus pievieno tikai molekulārā vienādojuma sastādīšanai.',
        'explain', 'Jānosauc skatītājonu saīsināšanās abās pusēs.', '', '',
    ),
    (
        'C88', 6,
        'Kas mainītos molekulārajā vienādojumā, ja joniem pieliktu lādiņus?',
        'Molekulārais vienādojums raksta neitrālas formulas vienības, tāpēc lādiņus tur neraksta. Ja pieliktu lādiņus, tas vairs nebūtu molekulārais vienādojums un varētu radīt iespaidu par joniem, kuru šķīdumā nav. Lādiņi paliek jonu vienādojumā.',
        'explain', 'Jānosauc neitrālas formulas vienības un lādiņu vieta jonu vienādojumā.', '', '',
    ),
    (
        'C90', 6,
        'Līdzsvaro: MnO₄⁻ + SO₃²⁻ + H⁺ → Mn²⁺ + SO₄²⁻ + H₂O (skāba vide).',
        '2[[MnO4^-]] + 5[[SO3^2-]] + 6H⁺ → 2[[Mn^2+]] + 5[[SO4^2-]] + 3H₂O. Permanganāts pieņem 5 e⁻, sulfīts atdod 2; LCM 10, reizinātāji 2 un 5.',
        'calc', '', '', '',
    ),
    (
        'C93', 6,
        'Līdzsvaro: MnO₄⁻ + Fe²⁺ + H⁺ → Mn²⁺ + Fe³⁺ + H₂O.',
        '[[MnO4^-]] + 5[[Fe^2+]] + 8H⁺ → [[Mn^2+]] + 5[[Fe^3+]] + 4H₂O. Šī ir titrēšanas reakcija.',
        'calc', '', '', '',
    ),
    (
        'C99', 6,
        'Kāpēc H₃PO₃ pusreakcijā neraksta PO₃³⁻?',
        'H₃PO₃ ir divvērtīgā fosforpaskābes molekula; PO₃³⁻ šķīdumā nav. Pareizi: [[H3PO3]] + H₂O → [[H3PO4]] + 2H⁺ + 2e⁻. Vienādojums ar PO₃³⁻ var formāli balansēties, tāpēc atomu pārbaude vien to nepieķer.',
        'explain', 'Jānosauc H₃PO₃ molekula, nevis PO₃³⁻; jāparāda pusreakcija.', '', '',
    ),
    (
        'C100', 6,
        'Līdzsvaro: Zn + HNO₃ → Zn(NO₃)₂ + N₂O + H₂O.',
        '4Zn + 10HNO₃ → 4Zn(NO₃)₂ + N₂O + 5H₂O. Jonu formā: 4Zn + 2[[NO3^-]] + 10H⁺ → 4[[Zn^2+]] + N₂O + 5H₂O.',
        'calc', '', '', '',
    ),
    (
        'C101', 6,
        'Līdzsvaro: Cr₂O₇²⁻ + Fe²⁺ + H⁺ → Cr³⁺ + Fe³⁺ + H₂O.',
        '[[Cr2O7^2-]] + 6[[Fe^2+]] + 14H⁺ → 2[[Cr^3+]] + 6[[Fe^3+]] + 7H₂O. Dihromāts pieņem 6 e⁻, katrs Fe²⁺ atdod 1.',
        'calc', '', '', '',
    ),
    (
        'C159', 6,
        'Kā rakstīt elektronus pusreakcijās, lai nerastos zīmju kļūda?',
        'Oksidēšanā elektroni ir produkta pusē: Fe²⁺ → Fe³⁺ + e⁻. Reducēšanā — reaģenta pusē: MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O. Viena konvencija visā dokumentā.',
        'cloze', '', '', '',
    ),
    (
        'C160', 6,
        'Kādi bultiņu un stāvokļu simboli tiek lietoti?',
        '→ notiekoša reakcija; ⇌ līdzsvars; ↓ nogulsnes; ↑ gāze. Fāzes (aq), (s), (l), (g) raksta tikai tad, kad tās kaut ko precizē.',
        'cloze', '', '', '',
    ),
    (
        'C161', 6,
        'Kā latviešu tekstā raksta skaitļus un mērvienības?',
        'Decimāldaļu atdala ar komatu (0,0200), starp skaitli un vienību ir nedalāma atstarpe, vienības: mL, L, mol/L. “M” ir mol/L saīsinājums.',
        'cloze', '', '', '',
    ),
    (
        'C162', 6,
        'Kāpēc Nernstā un titrēšanā n nozīmē dažādas lietas?',
        'Nernstā n ir elektronu skaits pusreakcijā. Titrēšanā n ir vielas daudzums molos. Tāpēc titrēšanā lieto z (ekvivalences skaitli), lai abas nozīmes nesajauktos.',
        'explain', 'Jānosauc n kā e⁻ skaits Nernstā un n kā moli titrēšanā; z.', '', '',
    ),
    (
        'C83', 6,
        'Students bāziskā pusreakcijā raksta H⁺ un nepievieno OH⁻. Kas jādara pareizi?',
        'Bāzē H⁺ neitralizē ar OH⁻ un saīsina H₂O. Piemērs: [[MnO4^-]] + 2H₂O + 3e⁻ → MnO₂ + 4OH⁻. H⁺ nedrīkst palikt kā galvenā forma bāziskā šķīdumā.',
        'spot', 'Jānosauc OH⁻ pievienošana un H₂O saīsināšana.', 'M05', '#ch6',
    ),
    (
        'C106', 7,
        'Kādi ir L21 pirmās daļas trīs mēģeņu saturi pirms Na₂SO₃?',
        'Visās trijās ir KMnO₄. Pirmajā pievieno H₂SO₄, otrajā destilētu ūdeni, trešajā NaOH. Pēc tam visās pievieno Na₂SO₃.',
        'cloze', '', '', '',
    ),
    (
        'C107', 7,
        'Kādas krāsas ir MnO₄⁻, Mn²⁺, MnO₄²⁻ un MnO₂ šķīdumā?',
        'MnO₄⁻ violets; Mn²⁺ bezkrāsains; MnO₄²⁻ zaļš; MnO₂ brūns (nogulsnes). Krāsa ir novērojums, nevis tikai dekorācija.',
        'cloze', '', '', '',
    ),
    (
        'C108', 7,
        'Kāpēc skābajā mēģenē pēc Na₂SO₃ pievienošanas violetā krāsa izzūd?',
        '[[MnO4^-]] reducējas līdz bezkrāsainajam [[Mn^2+]], pieņemot 5 e⁻. E° = 1,51 V; skābā vidē Mn²⁺ ir dominējošā forma, tāpēc šķīdums kļūst bezkrāsains.',
        'explain', 'Jānosauc 5 e⁻, Mn²⁺ un bezkrāsainā produkta dominēšana skābā vidē.', '', '',
    ),
    (
        'C109', 7,
        'Kāpēc neitrālajā mēģenē pēc Na₂SO₃ veidojas brūnas nogulsnes?',
        'Neitrālā vidē [[MnO4^-]] pieņem 3 e⁻ un reducējas līdz MnO₂, kas ir brūnas nogulsnes. E° = 0,60 V; nogulsnes traucē beigu punkta novērošanu.',
        'explain', 'Jānosauc 3 e⁻, MnO₂ un brūnās nogulsnes.', '', '',
    ),
    (
        'C110', 7,
        'Kāpēc bāziskajā mēģenē pēc Na₂SO₃ šķīdums kļūst zaļš?',
        'Bāziskā vidē [[MnO4^-]] pieņem tikai 1 e⁻ un veido [[MnO4^2-]] (manganātu), kas ir zaļš. E° = 0,56 V; tas nav MnO₂ un nav Mn²⁺.',
        'explain', 'Jānosauc 1 e⁻, MnO₄²⁻ un zaļā krāsa.', '', '',
    ),
    (
        'C111', 7,
        'Kāpēc KMnO₄ ir stiprākais oksidētājs tieši skābā vidē?',
        'Skābā vidē tas pieņem 5 e⁻ un E° = 1,51 V, turklāt H⁺ ir astotajā pakāpē Nernsta izteiksmē. Neitrālā — 3 e⁻/0,60 V; bāziskā — 1 e⁻/0,56 V.',
        'explain', 'Jānosauc 5/3/1 e⁻ un 1,51/0,60/0,56 V.', '', '',
    ),
    (
        'C112', 7,
        'Vai visus oksidētājus vide ietekmē tāpat kā KMnO₄?',
        'Nē. Ja pusreakcijā nav H⁺, OH⁻ vai ūdens, pH potenciālu tieši nemaina. Piemērs: Cl₂/Cl⁻; arī Fe³⁺/Fe²⁺ nav tieši pH atkarīgs.',
        'explain', 'Jānosauc Cl₂/Cl⁻ bez H⁺ un MnO₄⁻ ar 8 H⁺.', '', '',
    ),
    (
        'C113', 7,
        'Kura no trim reakcijām ir vispiemērotākā titrēšanai?',
        'Skābā: viens šķīstošs bezkrāsains produkts Mn²⁺, nav nogulšņu, beigu punkts ir vāji rozā. Neitrālā MnO₂ nogulsnes, bāziskā zaļais manganāts apgrūtina novērošanu.',
        'explain', 'Jānosauc skāba vide, Mn²⁺, nav nogulšņu, vāji rozā.', '', '',
    ),
    (
        'C115', 7,
        'Students saka: “MnO₄²⁻ ir stabils arī skābā vidē.” Vai tas ir pareizi?',
        'Nē. Skābā vidē manganāts (MnO₄²⁻) nav stabils un disproporcionējas; bāziskā vidē tas ir zaļš MnO₄²⁻. Permanganāts ir MnO₄⁻, manganāts — MnO₄²⁻; tos nedrīkst sajaukt.',
        'spot', 'Jānosauc nestabilitāte skābā vidē un MnO₄²⁻/MnO₄⁻ atšķirība.', 'M18', '#ch7',
    ),
    (
        'C118', 8,
        'Kādas lomas organisma oksidoreduktāzēs ir metālu joniem un koenzīmiem?',
        'Metālu joni (Fe, Cu, Mn, Mo) un organiskie koenzīmi veido oks/red pārus un pārnēsā elektronus. Zn²⁺ parasti ir strukturāls/Lūisa skābes kofaktors, nevis redoksa pāris.',
        'explain', 'Jānosauc Fe/Cu/Mn/Mo redoksa lomas un Zn²⁺ strukturālo lomu.', '', '',
    ),
    (
        'C122', 8,
        'Kāda ir elektronu secība mitohondriju elpošanas ķēdē?',
        'NADH → FMN saturošs proteīns → koenzīms Q → citohromi b → c₁ → c → a → a₃ → O₂. Katrs posms ir nedaudz zemāka potenciāla pāris.',
        'cloze', '', '', '',
    ),
    (
        'C123', 8,
        'Kurš enzīms katalizē elpošanas ķēdes pēdējo posmu?',
        'Citohroma c oksidāze (IV komplekss), kas pārnes elektronus uz O₂. “Citohromkināze” nav pareizs termins, jo kināze pārnes fosfātu.',
        'cloze', '', '', '',
    ),
    (
        'C124', 8,
        'Kā pareizi raksta reducēto un oksidēto NAD formu?',
        'Reducētā: NADH; oksidētā: NAD⁺. “NADH⁺” neeksistē. NADH pārnēsā 2 e⁻ un 1 H⁺ (bieži raksta NADH + H⁺).',
        'cloze', '', '', '',
    ),
    (
        'C125', 8,
        'Uzraksti pareizu O₂ reducēšanās līdz ūdenim pusreakciju un E°.',
        '[[O2]] + 4H⁺ + 4e⁻ → 2H₂O; E° = +1,229 V. Ar H₃O⁺: O₂ + 4H₃O⁺ + 4e⁻ → 6H₂O. Avota 2 e⁻ versija nav sabalansēta.',
        'cloze', '', '', '',
    ),
    (
        'C126', 8,
        'Kāpēc bioloģisko potenciālu tabulā nedrīkst jaukt E° un E°′?',
        'Tie attiecas uz dažādiem pH: E° parasti pH 0, E°′ pH 7. Ja tos sajauc, elektronu plūsmas virziens var izrādīties nepareizs. Viena tabula — viena konvencija.',
        'explain', 'Jānosauc pH 0 vs 7 un nepareiza virziena risks.', '', '',
    ),
    (
        'C129', 9,
        'Kas atrodas biretē un kas koniskajā kolbā titrēšanā?',
        'Biretē ir titrants ar precīzi zināmu koncentrāciju; koniskajā kolbā ir analīts (analizējamā viela) ar nezināmu koncentrāciju.',
        'cloze', '', '', '',
    ),
    (
        'C131', 9,
        'Kā atšķiras ekvivalences punkts no titrēšanas beigu punkta?',
        'Ekvivalences punkts ir teorētisks: n₁z₁ = n₂z₂. Beigu punkts ir tas, ko novēro (piemēram, pirmais noturīgais rozā). Starpība ir titrēšanas kļūda.',
        'explain', 'Jānosauc teorētiskais ekvivalences punkts un novērojamais beigu punkts; starpība ir titrēšanas kļūda.', '', '',
    ),
    (
        'C133', 9,
        'Uzraksti ekvivalentu likumu titrēšanai.',
        'n(titrants)·z(titrants) = n(analīts)·z(analīts). Pēc tam n = c·V, tāpēc c(analīts) = c(T)·V(T)·z(T)/(z(analīts)·V(analīts)).',
        'cloze', '', '', '',
    ),
    (
        'C136', 9,
        'Kāpēc permanganatometrijā lieto tieši KMnO₄?',
        'Tas ir stiprs oksidētājs skābā vidē, pats ir intensīvi violets un reducējas par bezkrāsainu Mn²⁺, tāpēc indikators nav vajadzīgs.',
        'explain', 'Jānosauc stiprs oksidētājs, violeta krāsa un Mn²⁺.', '', '',
    ),
    (
        'C138', 9,
        'Kāpēc permanganatometrijā lieto tikai atšķaidītu H₂SO₄?',
        'HCl būtu oksidējams līdz Cl₂, bet HNO₃ pati ir oksidētājs un varētu reaģēt ar analītu. H₂SO₄ nerada šīs blakusreakcijas.',
        'explain', 'Jānosauc HCl oksidēšanās un HNO₃ pati kā oksidētājs.', '', '',
    ),
    (
        'C139', 9,
        'Kā nosaka beigu punktu permanganatometrijā?',
        'Kad viss reducētājs ir izreaģējis, pirmais liekais KMnO₄ pilieniņš padara šķīdumu vāji rozā. Krāsai jāsaglabājas; konkrētais laiks avotos atšķiras (30 s, 1 min, 1–2 min).',
        'explain', 'Jānosauc pirmā noturīgā rozā un avotu laika atšķirības.', '', '',
    ),
    (
        'C141', 9,
        'Kāpēc KMnO₄ šķīdums nav primārais standarts?',
        'KMnO₄ satur MnO₂ piemaisījumus, sadalās gaismā un reaģē ar organiskām vielām. Tāpēc tā koncentrāciju standartizē, piemēram, ar skābeņskābi vai nātrija oksalātu.',
        'explain', 'Jānosauc MnO₂ piemaisījumi, gaisma un organiskās vielas.', '', '',
    ),
    (
        'C143', 9,
        'Kā pareizi nolasīt biretes tilpumu?',
        'KMnO₄ tumšā krāsā nolasa augšējo meniska malu, ar diviem cipariem aiz komata (0,01 mL). Rādījums jau ir izlietotais tilpums; no 25 mL neko neatņem.',
        'cloze', '', '', '',
    ),
    (
        'C145', 9,
        'Cik titrēšanas reizes un kāda atšķirība ir pieņemama?',
        'Vismaz trīs, labāk vairāk. Konkordantajiem titriem starpība parasti ≤ 0,10 mL; izteiktu izlēcēju izslēdz un pieraksta iemeslu.',
        'explain', 'Jānosauc izlēcēja izslēgšana un iemesla pierakstīšana, nevis vienkārša vidējošana.', '', '',
    ),
    (
        'C148', 9,
        'Kāpēc c(Fe²⁺) rēķina no 10,00 mL, bet m(FeSO₄) no 100,0 mL?',
        'Titrēšanai paņem 10,00 mL alikvotu, tāpēc tā dod koncentrāciju. Visa parauga masa ir 100,0 mL mērkolbā, tāpēc masu rēķina ar V = 0,1000 L.',
        'explain', 'Jānosauc alikvots koncentrācijai un 100 mL masa.', '', '',
    ),
    (
        'C149', 9,
        'Kā hidrāts maina masas aprēķinu?',
        'Ja viela ir kristālhidrāts, jālieto hidrāta molmasa. FeSO₄: 151,91 g/mol bezūdens, 278,02 g/mol heptahidrāts. Mora sāls: 284,04 bezūdens, 392,13 heksahidrāts. Vienādojums pats nemainās.',
        'explain', 'Jānosauc hidrāta molmasa un nemainīgais vienādojums.', '', '',
    ),
    (
        'C150', 9,
        'Aprēķini c(Fe²⁺), ja V(KMnO₄) = 12,35 mL, c = 0,0200 mol/L, alikvots 10,00 mL.',
        'c(Fe²⁺) = 0,0200·12,35·5/(1·10,00) = 0,1235 mol/L. Masu 100,0 mL rēķina atsevišķi: m = 0,1235·0,1000·151,91 = 1,876 g.',
        'calc', '', '', '',
    ),
    (
        'C152', 9,
        'LEC 1. uzdevums: kāda ir KMnO₄ molārā un normālā koncentrācija?',
        'c(KMnO₄) = 0,025·25,00·2/5/3,75 = 0,0667 mol/L (nenoapaļots 0,06667). Normālā (vēsturiska) = c·z = 0,333 ekv/L. 100 mL ir 1,05 g KMnO₄. Avota 0,067 M ir molārā, ne normālā (A18).',
        'calc', '', '', '',
    ),
    (
        'C155', 9,
        'LEC 4. uzdevums: kāpēc w(Fe) ir 0,20 %, nevis 0,19 %?',
        'n(Fe) = 0,022·7,98/1000·5 = 8,778·10⁻⁴ mol 25 mL; 500 mL ir 0,017556 mol; m = 0,9804 g. w = 0,9804/500·100 = 0,1961 %, kas noapaļojas uz 0,20 %. Avots 0,19 % nogriež, nevis noapaļo.',
        'calc', '', '', '',
    ),
    (
        'C134', 9,
        'Cik elektronu uz vienu MnO₄⁻ daļiņu pieņem skābā, neitrālā un bāziskā vidē? Cik molu elektronu pieņem 2,00·10⁻⁴ mol MnO₄⁻ skābā vidē?',
        'Skābā 5 e⁻, neitrālā 3 e⁻, bāziskā 1 e⁻. Skābā vidē: n(e⁻) = 5·2,00·10⁻⁴ = 1,00·10⁻³ mol.',
        'calc', '', '', '#ch9',
    ),
    (
        'C151', 9,
        'LEC §3.1: c(Mora sāls) = 0,132 mol/L. Aprēķini m 100,0 mL bezūdens formā (M = 284,04 g/mol) un heksahidrātā (M = 392,13 g/mol).',
        'Bezūdens: m = 0,132·0,1000·284,04 = 3,749 g ≈ 3,75 g. Heksahidrāts: m = 0,132·0,1000·392,13 = 5,176 g ≈ 5,18 g. Hidrāts jānosauc.',
        'calc', '', '', '#numeric',
    ),
    (
        'C153', 9,
        'LEC pašpārbaudes 2. uzdevums: c(FeSO₄) = 0,0568 mol/L, M(FeSO₄) = 151,91 g/mol. Cik gramu FeSO₄ ir 1 L?',
        'm = c·V·M = 0,0568·1,000·151,91 = 8,628 g/L ≈ 8,63 g/L.',
        'calc', '', '', '#numeric',
    ),
    (
        'C154', 9,
        'H₂O₂ paraugs: 2,00 mL ar ρ = 1,05 g/mL; tajā ir 0,0680294 g H₂O₂. Aprēķini masas daļu w.',
        'Parauga masa = 2,00·1,05 = 2,10 g. w = 0,0680294/2,10·100 = 3,239 % ≈ 3,24 %.',
        'calc', '', '', '#numeric',
    ),
    (
        'C157', 9,
        'c = 0,132 mol/L, V = 0,1000 L, M = 284,04 g/mol. Aprēķini m ar nenoapaļotu c un ar priekšlaicīgi noapaļotu c = 0,13. Kāpēc atbildes atšķiras?',
        'Ar nenoapaļotu c: m = 0,132·0,1000·284,04 = 3,749 g ≈ 3,75 g. Ar c = 0,13: m = 0,13·0,1000·284,04 = 3,693 g ≈ 3,69 g. Atšķirība rodas no priekšlaicīgas noapaļošanas; starprezultātu nenoapaļo.',
        'calc', '', '', '#numeric',
    ),
    (
        'C158', 9,
        'Students molekulārajā vienādojumā sāls formulai pieliek jonu lādiņu. Vai tas ir pareizi?',
        'Nē. Molekulārajā vienādojumā raksta neitrālas formulas vienības; lādiņus tur neraksta. Lādiņi pieder joniem jonu vienādojumā, nevis sāls formulai.',
        'spot', 'Jānosauc neitrāla formulas vienība un lādiņu vieta jonu vienādojumā.', 'M17', '#ch9',
    ),
    (
        'C163', 11,
        'Kuru rakstību lieto dokumentā oksidēšanas pakāpei — vienoto standarta formu vai avota otro variantu?',
        'Dokuments lieto “oksidēšanas pakāpe” visur. Avota otrais variants ir tikai citātos un 11.4. tabulā kolonnā “nelietot”.',
        'cloze', '', '', '',
    ),
    (
        'C164', 11,
        'Kā vienā teikumā nošķirt ekvivalences punktu un beigu punktu?',
        'Ekvivalences punkts ir aprēķinātais punkts, kur n₁z₁ = n₂z₂; beigu punkts ir novērojamā krāsa vai signāls, kas var būt nedaudz aiz tā.',
        'cloze', '', '', '',
    ),
    (
        'C169', 11,
        'Savieno: sulfīds, sulfīts, sulfāts; nitrīts, nitrāts; manganāts, permanganāts.',
        'S²⁻, SO₃²⁻, SO₄²⁻; NO₂⁻, NO₃⁻; MnO₄²⁻, MnO₄⁻. Jaukt visbiežāk sāk tieši manganātu ar permanganātu.',
        'cloze', '', '', '',
    ),
    (
        'C170', 11,
        'Students skābā vidē raksta pusreakciju ar fosfīta jonu PO₃³⁻. Vai tas ir pareizi?',
        'Nē. H₃PO₃ ir divvērtīgā fosforpaskābes molekula; PO₃³⁻ šķīdumā nav. Pareizi: [[H3PO3]] + H₂O → [[H3PO4]] + 2H⁺ + 2e⁻.',
        'spot', 'Jānosauc H₃PO₃ molekula, nevis PO₃³⁻, un jāparāda pusreakcija.', 'M16', '#ch11',
    ),
]

CONCEPT_TOTAL = 170
RETRIEVAL_TOTAL = 151


def _finalize(raw):
    seen = {}
    out = []
    for cid, ch, q, a, kind, criterion, mistake, link in raw:
        base = f"{cid}-{kind}"
        seen[base] = seen.get(base, 0) + 1
        pid = base if seen[base] == 1 else f"{base}-{seen[base]}"
        out.append(Prompt(pid, cid, ch, q, a, kind, criterion, mistake, link))
    return out


PROMPTS = _finalize(_RAW_PROMPTS)
PROMPT_BY_PID = {p.pid: p for p in PROMPTS}


def prompt_stats():
    kinds = {}
    for p in PROMPTS:
        kinds[p.kind] = kinds.get(p.kind, 0) + 1
    concepts = len({p.cid for p in PROMPTS})
    return {
        "prompts": len(PROMPTS),
        "concepts": concepts,
        "concept_total": CONCEPT_TOTAL,
        "retrieval_total": RETRIEVAL_TOTAL,
        "concept_pct": 100 * concepts / CONCEPT_TOTAL,
        "kinds": kinds,
    }


def validate_prompts():
    pids = [p.pid for p in PROMPTS]
    assert len(pids) == len(set(pids)), "duplicate prompt id"
    for p in PROMPTS:
        assert re.fullmatch(r"C\d{2,3}", p.cid), p.cid
        assert p.kind in {"cloze", "calc", "explain", "spot"}, p.pid
        assert p.q and p.a, p.pid
        if p.kind in {"explain", "spot"}:
            assert p.criterion, p.pid
        if p.kind == "spot":
            assert p.mistake, p.pid
    assert len({p.cid for p in PROMPTS}) >= 51, "below 30 % concept gate"
    return True



# ---------------------------------------------------------------- mistakes
# Fields: id, type, chapter, title, wrong, why, check, correct, source
# Types (5): Jēdzieni, Pieraksts, Aprēķins, Laboratorija, Avota kļūda
MISTAKES = [
    ("M01", "Jēdzieni", 1, "Oksidētājs it kā pats oksidējas",
     "“KMnO₄ oksidējas par Mn²⁺, tāpēc KMnO₄ ir reducētājs.”",
     "Vārdi “oksidētājs” un “oksidējas” skan līdzīgi, tādēļ reaģenta funkciju viegli sajaukt ar procesa nosaukumu.",
     "Uzskaiti elektronus: KMnO₄ mangāns pieņem 5 e⁻ (reducējas) un atņem tos otram, tātad KMnO₄ ir oksidētājs.",
     "KMnO₄ ir oksidētājs; tas reducējas par Mn²⁺; reducētājs ir Fe²⁺, kas oksidējas par Fe³⁺.",
     "F1"),
    ("M02", "Jēdzieni", 1, "Oksidēšanas pakāpe = lādiņš = valence",
     "“SO₂ sērs ir [[w:S^4+]] jons, tāpēc tam ir lādiņš 4+.”",
     "Trīs teorētiski atšķirīgi jēdzieni tiek sapludināti vienā, formālu elektronu uzskaiti uztverot kā reālu jonu.",
     "Pārbaudi molekulas dabu: SO₂ ir kovalents savienojums ar kopējo lādiņu 0, kurā brīva [[w:S^4+]] jona nav.",
     "Sēra oksidēšanas pakāpe SO₂ ir +4; molekulas lādiņš ir 0; kovalentā saitē daļiņa nav brīvs jons.",
     "F2"),
    ("M03", "Pieraksts", 6, "Atomi sabalansēti, lādiņš nē",
     "[[Fe^2+]] + [[MnO4^-]] → [[Fe^3+]] + [[Mn^2+]].",
     "Koeficientus mēdz piemeklēt tikai pēc atomu skaita, nepārbaudot kopējo lādiņu bilanci abās pusēs.",
     "Saskaiti lādiņus: kreisajā pusē lādiņu summa ir +1 (2 − 1), bet labajā pusē +5 (3 + 2); bilance nesakrīt.",
     "[[MnO4^-]] + 8H⁺ + 5[[Fe^2+]] → [[Mn^2+]] + 4H₂O + 5[[Fe^3+]]; lādiņu summa abās pusēs ir +17.",
     "F3"),
    ("M04", "Pieraksts", 6, "Nepareiza pusreakcijas līdzsvarošanas secība",
     "Vispirms pieraksta e⁻ un tikai pēc tam mēģina pielāgot H⁺ un H₂O.",
     "Ja soļu secība nav nostiprināta, atomu un lādiņu bilance sāk viena otru jaukt.",
     "Pārbaudi stingru secību: citi atomi → O ar H₂O → H ar H⁺ → lādiņu starpība ar e⁻.",
     "Kārtība: citi atomi, tad O ar H₂O, tad H ar H⁺, un tikai beigās lādiņš ar e⁻ (bāzē H⁺ neitralizē ar OH⁻).",
     "F4"),
    ("M05", "Pieraksts", 6, "H⁺ bāziskā vidē",
     "Bāziskā pusreakcijā vienkārši pieraksta H⁺ un nepievieno OH⁻.",
     "Skābās vides algoritmu mehāniski pārnes uz bāzisku vidi, kur H⁺ jonu koncentrācija ir niecīga.",
     "Pārbaudi vidi: bāziskā vidē (pH > 7) reaģentos nevar būt brīvs H⁺; katram H⁺ jāpievieno OH⁻ abās pusēs.",
     "Bāzē lieto OH⁻ un H₂O: [[MnO4^-]] + 2H₂O + 3e⁻ → MnO₂ + 4OH⁻.",
     "F5"),
    ("M06", "Aprēķins", 3, "E° izmanto kā E pie cita pH",
     "“Cr₂O₇²⁻/Cl⁻ virzienu nosaka tikai no E° = 1,33 V; skābums reakciju neietekmē.”",
     "Standartpotenciāls E° ir tabulas skaitlis, tādēļ rodas kārdinājums izlaist Nernsta aprēķinu reālos apstākļos.",
     "Pārbaudi pusreakciju: Cr₂O₇²⁻ satur 14 H⁺, tāpēc pie pH 3 potenciāls krīt par 0,28 V (E = 1,05 V pret Cl₂ 1,36 V).",
     "E° der tikai pie [H⁺] = 1 mol/L (pH 0); citos apstākļos E obligāti jārēķina ar Nernsta vienādojumu.",
     "F6"),
    ("M07", "Aprēķins", 3, "Nernsta koeficients apgriezts",
     "E = E° + (0,0592/n)·lg([Red]/[Ox]).",
     "Attiecību intuitīvi jauc ar vispārējo līdzsvara konstantes “produkti/izejvielas” daļu.",
     "Pārbaudi robežgadījumu: ja oksidētāja [Ox] koncentrācija pieaug, šķīduma potenciālam E obligāti jāpieaug.",
     "E = E° + (0,0592/n)·lg([Ox]/[Red]) redukcijas pusreakcijai Ox + ne⁻ → Red.",
     "F7"),
    ("M08", "Aprēķins", 2, "EDS kā potenciālu summa",
     "“EDS = E(katods) + E(anods)” vai “E₁ + E₂”.",
     "Potenciālu starpību intuitīvi jauc ar termodinamisko reakcijas funkciju summēšanu.",
     "Pārbaudi definīciju: EDS ir divu elektrodu potenciālu starpība E(katods) − E(anods) > 0, nekad ne summa.",
     "EDS = E(katods) − E(anods) = E(+) − E(−); katods ir pozitīvākais elektrods.",
     "F8"),
    ("M09", "Aprēķins", 8, "E° un E°′ sajaukšana",
     "Bioloģiskajā tabulā H⁺/H₂ 0,00 V liek blakus NAD⁺/NADH −0,32 V.",
     "Abas vērtības saucas par standartpotenciāliem, ignorējot, ka viena definēta pie pH 0, bet otra pie pH 7.",
     "Pārbaudi atsauces pH: pie pH 7 ūdeņraža elektroda potenciāls E°′(H⁺/H₂) ir −0,414 V, nevis 0,00 V.",
     "Vienā aprēķinā drīkst lietot tikai vienu konvenciju: vai nu visus E° (pH 0), vai visus E°′ (pH 7).",
     "F9"),
    ("M10", "Jēdzieni", 4, "ΔE > 0 nozīmē “ātri”",
     "“Ja reakcijas ΔE > 0, tā istabas temperatūrā noritēs momentāni.”",
     "Termodinamisko patvaļīgumu (ΔG < 0) sajauc ar reakcijas kinētisko ātrumu.",
     "Pārbaudi kinētiku: ΔE > 0 nosaka tikai līdzsvara stāvokli; augsta aktivācijas enerģija var reakciju padarīt lēnu.",
     "ΔE > 0 nozīmē, ka reakcija ir termodinamiski iespējama; reālu ātrumu nosaka kinētika un temperatūra.",
     "F10"),
    ("M11", "Jēdzieni", 7, "Mn krāsas bez iemesla",
     "“Skābā bezkrāsains, neitrālā brūns, bāziskā zaļš” — iegaumēts bez pusreakcijas un elektronu skaita.",
     "Krāsu tabulu iegaumē kā izolētu vizuālu sarakstu, nesaistot to ar pieņemtajiem elektroniem un produktu.",
     "Pārbaudi elektronus: skābē 5 e⁻ dod Mn²⁺ (bezkrāsains), neitrālā 3 e⁻ dod MnO₂ (brūns), bāzē 1 e⁻ dod MnO₄²⁻ (zaļš).",
     "Krāsa ir mangāna savienojuma sekas: skābē Mn²⁺, neitrālā MnO₂(s) nogulsnes, bāzē MnO₄²⁻ jons.",
     "F11"),
    ("M12", "Laboratorija", 9, "HCl vai HNO₃ permanganatometrijā",
     "“Permanganātometrijā skābas vides radīšanai var izmantot jebkuru stipru skābi (HCl vai HNO₃).”",
     "Tiek pieņemts, ka skābes loma ir tikai H⁺ joni, aizmirstot par anjona redoksa aktivitāti.",
     "Pārbaudi anjona redoksu: Cl⁻ oksidējas par Cl₂ (patērē titrantu), bet NO₃⁻ pati ir spēcīgs oksidētājs.",
     "Permanganātometrijā lieto tikai atšķaidītu H₂SO₄; sulfāta anjons SO₄²⁻ šajos apstākļos ir redoksa ziņā inerts.",
     "D3/F12"),
    ("M13", "Laboratorija", 9, "Ekvivalences punkts = beigu punkts",
     "“Titrēšanas beigu punkts ir precīzi tas pats, kas ekvivalences punkts.”",
     "Eksperimentāli novēroto indikatora krāsas maiņu uztver kā teorētisko stehiometrisko robežu.",
     "Pārbaudi teoriju pret praksi: ekvivalences punkts ir n₁z₁ = n₂z₂, bet beigu punktu pamana ar 1 lieku titranta pilienu.",
     "Ekvivalences punkts ir teorētiskais brīdis; beigu punkts ir novērotā indikācija; to starpība ir titrēšanas kļūda.",
     "A10/F13"),
    ("M14", "Laboratorija", 9, "Biretes rādījuma atņemšana no 25 mL",
     "“Biretes menisks ir pie 12,35 mL, tātad izlietotais tilpums ir 25 − 12,35 = 12,65 mL.”",
     "Biretes nulli augšā sajauc ar mērcilindra nulli apakšā.",
     "Pārbaudi biretes skalu: skala sākas ar 0,00 mL augšā, tāpēc meniska rādījums tieši uzrāda izlietoto tilpumu.",
     "Biretes nolasījumu pieraksta tieši (12,35 mL); no biretes kopējā tilpuma to nekad neatņem.",
     "L25 p.3/F14"),
    ("M15", "Aprēķins", 9, "Alikvots pret mērkolbu: masas aprēķins no nepareiza tilpuma",
     "“c(Fe²⁺) = 0,1235 mol/L, tāpēc mērkolbā 100 mL ir m = 0,1235·0,01000·151,91 = 0,188 g.”",
     "Titrēšanai paņemto alikvota tilpumu (10,00 mL) kļūdaini ievieto kopējās mērkolbas masas aprēķinā.",
     "Pārbaudi tilpumus: 10,00 mL alikvots dod koncentrāciju, bet masu rēķina no visas 100,0 mL (0,1000 L) mērkolbas.",
     "n(mērkolbā) = c·V(mērkolba) = 0,1235·0,1000 = 0,01235 mol; m = 0,01235·151,91 = 1,876 g.",
     "D5/A16/F15"),
    ("M16", "Jēdzieni", 6, "Neeksistējoša daļiņa stipri skābā vidē",
     "“[[PO3^3-]] + H₂O − 2e⁻ → [[PO4^3-]] + 2H⁺” stipri skābā šķīdumā.",
     "Vienādojums formāli balansējas pēc atomiem un lādiņa, tādēļ nepamana daļiņas disociācijas robežu konkrētajā pH.",
     "Pārbaudi pH: fosfītskābe ar pKa1 = 1,3 skābā vidē (pH 0) eksistē kā H₃PO₃ molekula, nevis PO₃³⁻ jons.",
     "[[H3PO3]] + H₂O → [[H3PO4]] + 2H⁺ + 2e⁻; skābā vidē sulfīts ir HSO₃⁻/SO₂·H₂O, sulfīds ir H₂S.",
     "A14/A15/F16"),
    ("M17", "Pieraksts", 6, "Lādiņš uz neitrālas formulas vienības",
     "“K₂SO₄²⁻”, “2KOH⁻”, “MnSO₄²⁻” molekulārajā vienādojumā.",
     "Atsevišķo jonu lādiņus automātiski pārnes uz veselu sāls vai bāzes formulu.",
     "Pārbaudi elektroneitralitāti: molekulārajā vienādojumā formulas vienība ir neitrāla ar kopējo lādiņu 0.",
     "Molekulārajā vienādojumā raksta K₂SO₄, KOH, MnSO₄ bez lādiņa; lādiņus uzrāda tikai jonu vienādojumā.",
     "B2/F17"),
    ("M18", "Jēdzieni", 5, "Manganāts sajaukts ar permanganātu",
     "“Bāziskā vidē veidojas brūns MnO₂, tāpēc KMnO₄ ir manganāts.”",
     "Permanganāta un manganāta nosaukumi un krāsas ir līdzīgas, un avotā bija sajaukta etiķete (A12).",
     "Pārbaudi oksidēšanas pakāpi: permanganātā MnO₄⁻ mangānam ir +7, bet manganātā MnO₄²⁻ ir +6.",
     "KMnO₄ ir kālija permanganāts (+7, violets); K₂MnO₄ ir kālija manganāts (+6, zaļš); brūns MnO₂ ir oksīds (+4).",
     "A12/F18"),
    ("M19", "Pieraksts", 1, "Oksidēšanas pakāpe rakstīta kā lādiņš",
     "“[[w:Mn^7+]]”, “[[w:S^4+]]”, “[[w:O^2-]]” uzskatot par reāliem brīviem joniem.",
     "Abiem pierakstiem lieto augšējos indeksus, tādēļ bieži sajauc zīmes un skaitļa secību.",
     "Pārbaudi standartu: jona lādiņam skaitlis ir pirms zīmes (Fe³⁺, SO₄²⁻); oksidēšanas pakāpei zīme ir pirms skaitļa (+7, +4, −2).",
     "Oksidēšanas pakāpi raksta ar zīmi pa priekšu (+7, +4, −2); reālu daudaudzatomi jona lādiņu ar skaitli pa priekšu (MnO₄⁻).",
     "B1"),
    ("M20", "Pieraksts", 2, "E° reizināšana ar stehiometriju",
     "“2Fe³⁺ + 2e⁻ → 2Fe²⁺, tāpēc E° = 2·0,77 = 1,54 V.”",
     "Standartpotenciālu sajauc ar ekstensīvu termodinamisko funkciju (Gibsa enerģiju ΔG°).",
     "Pārbaudi fizikālo dabu: E° ir intensīvs lielums (spriegums); koeficientu reizināšana nemaina elektronu potenciālu starpību.",
     "E°(Fe³⁺/Fe²⁺) paliek 0,77 V; koeficienti maina tikai kopējo enerģiju ΔG° = −zFΔE° caur elektronu skaitu z.",
     "F8"),
    ("M21", "Pieraksts", 6, "Nesamazināti reizinātāji un sajaukti koeficienti",
     "Pusreakcijām ar 6e⁻ un 2e⁻ lieto reizinātājus 2 un 6, un gala vienādojumā atstāj koeficientus 2 un 6.",
     "Mazāko kopīgo dalāmo aizstāj ar vienkāršu savstarpēju sareizināšanu, aizmirstot saīsināt līdz mazākajiem veselajiem skaitļiem.",
     "Pārbaudi dalāmību: elektronu skaitiem 6 un 2 LCM ir 6, tādēļ reizinātāji ir 1 un 3, nevis 2 un 6.",
     "Reizinātāji jāsamazina līdz mazākajiem veselajiem skaitļiem (1 pret 3); gala vienādojuma koeficientiem jābūt saīsinātiem.",
     "B3"),
    ("M22", "Aprēķins", 9, "Normālā koncentrācija sajaukta ar molāro",
     "“c(KMnO₄) = 0,020 mol/L, tātad šķīduma normālā koncentrācija arī ir 0,020.”",
     "Skaitlisko vērtību automātiski pārnes, aizmirstot, ka redoksā ekvivalences faktors ir pieņemto elektronu skaits z.",
     "Pārbaudi z skaitu: permanganātam skābā vidē z = 5, tādēļ normālā koncentrācija cN = 5·c = 0,100 ekv/L.",
     "c(KMnO₄) = 0,020 mol/L; normālā koncentrācija ir 0,100 ekv/L; mūsdienu aprēķinos lieto molāro koncentrāciju.",
     "A18/T5"),
    ("M23", "Aprēķins", 9, "Noapaļošana pirms pēdējā soļa",
     "“c = 0,132 mol/L noapaļo uz 0,13; m = 0,13·0,1·284 = 3,69 g.”",
     "Starprezultātu noapaļo par agru, un noapaļošanas kļūda nākamajos reizinājumos pieaug līdz pat 1,6%.",
     "Salīdzini ar nenoapaļotu vērtību: 0,132·0,1·284,04 = 3,75 g; priekšlaicīga noapaļošana rada nobīdi par 0,06 g.",
     "Starprezultātus aprēķinos patur ar neatslēgtiem cipariem; noapaļo tikai vienu reizi gala atbildē (3,75 g vai ar 2 cipariem 3,7 g).",
     "A17/F15"),
    ("M24", "Avota kļūda", 5, "Avota tabulas etiķetes pārbīde",
     "“Cu²⁺/Cu pusreakcijas rindā elementa kolonnā avotā ierakstīts Pb.”",
     "Kursa oriģinālajā lekcijas tabulā teksta šūnas bija mehāniski nobīdītas sagatavošanas laikā.",
     "Pārbaudi pusreakcijas ķīmiju: Cu²⁺ + 2e⁻ → Cu atbilst varam (Cu), nevis svinam (Pb).",
     "13.A tabulā etiķetes piesaistītas atbilstošajām rindām; svina un vara rindas ir stingri atdalītas.",
     "A1"),
    ("M25", "Jēdzieni", 8, "O₂ reducēšana ar 2 e⁻ elpošanas ķēdē",
     "“O₂ + 2e⁻ + 2H₃O⁺ → H₂O + 2H₂O (vai O₂ reducēšana par H₂O₂ kā elpošanas gala produkts).”",
     "Skābekļa molekulas pilno reducēšanu par diviem ūdens molekulu atomiem kļūdaini uzraksta ar 2 e⁻.",
     "Saskaiti elektronus: viena O₂ reducēšanai līdz 2 H₂O nepieciešami 4 e⁻; 2 e⁻ reducēšana rada toksisku peroksīdu H₂O₂.",
     "Elpošanas ķēdes terminālā reducēšana: O₂ + 4 H⁺ + 4 e⁻ → 2 H₂O (E° = 1,229 V; E°′ = +0,815 V).",
     "A4"),
    ("M26", "Aprēķins", 4, "PbO₂ potenciāls pieņemts kā 1,80 V",
     "“PbO₂/Pb²⁺ E° = 1,80 V, tāpēc PbO₂ standartapstākļos oksidē Mn²⁺ par MnO₄⁻.”",
     "Kursa lekcijas tabulā norādīta nekritiska vērtība +1,80 V, lai gan CRC rokasgrāmatas standartpotenciāls ir +1,455 V.",
     "Pārbaudi standartpotenciālus: E°(PbO₂/Pb²⁺) = 1,455 V < E°(MnO₄⁻/Mn²⁺) = 1,51 V; standartapstākļos reakcija nenotiek.",
     "PbO₂ oksidē Mn²⁺ tikai koncentrētā HNO₃, kur Nernsta nobīde augstas [H⁺] un zemas [Pb²⁺] dēļ paceļ E virs 1,51 V.",
     "A3/D10"),
    ("M27", "Aprēķins", 4, "“Skābā vidē” pieņemta bez koncentrācijas skaitļa",
     "“Tā kā vide ir skāba, dihromāts noteikti oksidēs hlorīdu par Cl₂.”",
     "Apzīmējumu “skāba vide” pieņem par pietiekamu bez konkrētās H⁺ koncentrācijas aprēķina.",
     "Aprēķini Nernsta robežu: E(Cr₂O₇²⁻) pārsniedz E(Cl₂) tikai tad, ja [H⁺] ≳ 1,65 mol/L; parastā skābā vidē reakcija nenotiek.",
     "Dihromāts hlorīdu oksidē tikai koncentrētā skābē ([H⁺] ≳ 1,65 mol/L); atšķaidītā skābē Cl⁻ titrēšanu netraucē.",
     "A13"),
    ("M28", "Jēdzieni", 8, "“Citohromkināze” vietā “citohromoksidāze”",
     "“Mitohondriju elpošanas ķēdes IV kompleksu sauc par citohromkināzi.”",
     "Kināzes fermentus (kas pārnes fosfātu grupas) sajauc ar oksidāzēm (kas pārnes elektronus uz skābekli).",
     "Pārbaudi fermenta klasi: IV komplekss pārnes elektronus no citohroma c uz skābekli, tāpēc tas ir oksidāze, nevis kināze.",
     "IV kompleksa nosaukums ir citohroma c oksidāze (citohromoksidāze); kināzes ir fosfotransferāzes no ATF.",
     "A6"),
    ("M29", "Jēdzieni", 8, "“NADH⁺” vietā “NADH”",
     "“Reducētais nikotīnamīda koferments ir NADH⁺.”",
     "Oksidētās formas NAD⁺ pozitīvo lādiņu mehāniski pārnes uz reducēto formu.",
     "Saskaiti lādiņu bilanci: NAD⁺ pieņem 2 e⁻ un H⁺, tāpēc kopējais lādiņš ir +1 − 2 + 1 = 0 (elektroneitrāls NADH).",
     "Oksidētā forma ir NAD⁺ (ar pozitīvu lādiņu); reducētā forma ir elektroneitrāls NADH (bez lādiņa).",
     "A7"),
]

# ---------------------------------------------------------------- T07 recall feedback (qa/t07b)
# Wrong-answer feedback is composed from the sourced mistake-atlas cards
# themselves (task T07.1.3: no invented distractors). The tempting form is
# the card's wrong form, the catching check is its check line, and the deep
# link names the atlas entry (10.3). MISTAKE_QA_LEAD adds one optional,
# card-specific sentence that names the temptation when the wrong form alone
# does not; every sentence restates card content, never a new claim.
MISTAKE_QA_LEAD = {
    "M03": "Kļūda slēpjas lādiņu summā: atomu skaits viens pats neko negarantē.",
    "M05": "Bāziskā vidē brīva H⁺ nav; katram H⁺ abās pusēs jāpieliek OH⁻.",
    "M06": "E° vērtība der tikai pie [H⁺] = 1 mol/L (pH 0); citā vidē jārēķina E.",
    "M09": "Skaitlis 0,00 V pieder pie pH 0; pie pH 7 ūdeņraža elektrodam ir E°′ = −0,414 V.",
    "M16": "Formāli sabalansēts vienādojums vēl nepierāda, ka daļiņa pastāv dotajā pH.",
    "M17": "Lādiņš pieder joniem; neitrālas formulas vienības lādiņš ir 0.",
    "M18": "MnO₄⁻ (violets, Mn +7) un MnO₄²⁻ (zaļš, Mn +6) ir dažādi joni ar dažādām krāsām.",
    "M20": "E° ir intensīvs lielums, ko stehiometriskais reizinātājs nemaina.",
    "M23": "Noapaļošana pirms pēdējā soļa pārnes kļūdu uz gala atbildi.",
    "M27": "“Skāba vide” nav skaitlis; virziens jālemj pie konkrētas [H⁺] vērtības.",
}

# T07.1.3: prompts whose feedback names the most plausible wrong path even
# though they are not spot prompts. Keyed by exact pid; the linked card must
# exist in MISTAKES (validated by validate_mistakes()).
PROMPT_QA_LINKS = {
    "C03-explain": "M01",
    "C05-explain": "M01",
    "C09-explain": "M02",
    "C11-explain": "M19",
    "C26-explain": "M09",
    "C26-calc": "M09",
    "C27-explain": "M10",
    "C46-explain": "M06",
    "C54-explain": "M06",
    "C111-explain": "M11",
    "C131-explain": "M13",
    "C148-explain": "M15",
    "C157-calc": "M23",
}

MISTAKE_BY_ID = {m[0]: m for m in MISTAKES}


def feedback_mistake_id(p: Prompt) -> str:
    """Atlas card behind a prompt's wrong-answer feedback, or ''."""
    return p.mistake or PROMPT_QA_LINKS.get(p.pid, "")


def mistake_qa_rationale(mid: str) -> str | None:
    """Wrong-answer feedback text composed from the sourced atlas card."""
    m = MISTAKE_BY_ID.get(mid)
    if m is None:
        return None
    lead = MISTAKE_QA_LEAD.get(mid)
    sentences = []
    if lead:
        sentences.append(f"Kārdinošā atbilde: {lead}")
    sentences.append(f"Šī ir atlanta {mid} kļūda — nepareizais pieraksts: {m[4]}")
    sentences.append(f"Pieķeršanas pārbaude: {m[6]}")
    out = []
    for s in sentences:
        out.append(s if (s.endswith((".", "!", "?", "”")) or s.endswith((".", "!", "?", "”"))) else s + ".")
    return " ".join(out)


def mistake_qa_pointer(mid: str) -> str:
    """Closing pointer sentence; renderers turn it into a link to #{mid}."""
    return f"Pilns skaidrojums un pareizā forma: {mid} kļūdu atlantā (10.3)."


def retrieval_mode(p: Prompt) -> str:
    """T07.1.2 retrieval mode: factual, procedural, transfer or diagnostic."""
    q = p.q.lower()
    if p.kind == "spot":
        return "diagnostic"
    if p.kind == "calc":
        if any(w in q for w in ("nosaki", "virzien", "salīdzini", "pielieto", "kurā pusē")):
            return "transfer"
        return "procedural"
    if p.kind == "explain":
        if q.startswith(("kāpēc", "kas mainītos", "kur", "vai")):
            return "transfer"
        return "factual"
    return "factual"


def validate_mistakes() -> bool:
    """T07: feedback wiring must reference existing atlas cards only."""
    mids = [m[0] for m in MISTAKES]
    assert len(mids) == len(set(mids)), "duplicate mistake id"
    unknown_lead = sorted(set(MISTAKE_QA_LEAD) - set(mids))
    assert not unknown_lead, f"MISTAKE_QA_LEAD: unknown cards {unknown_lead}"
    pids = {p.pid for p in PROMPTS}
    unknown_links = sorted(set(PROMPT_QA_LINKS) - pids)
    assert not unknown_links, f"PROMPT_QA_LINKS: unknown pids {unknown_links}"
    for pid, mid in sorted(PROMPT_QA_LINKS.items()):
        assert mid in MISTAKE_BY_ID, f"{pid}: unknown mistake {mid}"
        assert mistake_qa_rationale(mid), pid
    for p in PROMPTS:
        if p.kind == "spot":
            assert feedback_mistake_id(p), f"{p.pid}: spot prompt without feedback"
    return True


# ---------------------------------------------------------------- mistake triage drill (Task 19)
# 6 representative demonstrated items covering three core fault types:
#   "charge"  -> Lādiņš vai zīme
#   "species" -> Daļiņa vai vide (pH)
#   "calc"    -> Aprēķins vai vienības
MISTAKE_DRILL_ITEMS = [
    {
        "id": "D1",
        "wrong": "[[Fe^2+]] + [[MnO4^-]] → [[Fe^3+]] + [[Mn^2+]]",
        "key": "charge",
        "key_label": "Lādiņš vai zīme",
        "mistake_id": "M03",
        "hint": "Atomi katrā pusē šķiet pa vienam, bet lādiņu summa nav līdzsvarota.",
        "check": "Kreisajā pusē lādiņš ir +1 (2 − 1), labajā pusē +5 (3 + 2). Trūkst 8 H⁺ un 4 H₂O; abās pusēs lādiņam jābūt +17.",
        "correct": "[[MnO4^-]] + 8H⁺ + 5[[Fe^2+]] → [[Mn^2+]] + 4H₂O + 5[[Fe^3+]]",
    },
    {
        "id": "D2",
        "wrong": "[[PO3^3-]] + H₂O − 2e⁻ → [[PO4^3-]] + 2H⁺ (stipri skābā vidē)",
        "key": "species",
        "key_label": "Daļiņa vai vide (pH)",
        "mistake_id": "M16",
        "hint": "Pārbaudi, kādā formā daļiņa var pastāvēt šķīdumā ar pH ≈ 0.",
        "check": "Fosfītskābe ar pKa1 = 1,3 skābā vidē (pH 0) eksistē kā neitrāla molekula H₃PO₃, nevis PO₃³⁻ jons.",
        "correct": "[[H3PO3]] + H₂O → [[H3PO4]] + 2H⁺ + 2e⁻",
    },
    {
        "id": "D3",
        "wrong": "c(Fe²⁺) = 0,1235 mol/L; mērkolbā 100 mL masa m = 0,1235·0,01000·151,91 = 0,188 g",
        "key": "calc",
        "key_label": "Aprēķins vai vienības",
        "mistake_id": "M15",
        "hint": "Pārbaudi, kurš tilpums dots alikvotam un kurš — visai mērkolbai.",
        "check": "Alikvots (10,00 mL = 0,01000 L) dod koncentrāciju c, bet masu m rēķina no visas mērkolbas (100,0 mL = 0,1000 L).",
        "correct": "n(mērkolbā) = 0,1235·0,1000 = 0,01235 mol; m = 0,01235·151,91 = 1,876 g (10× lielāka).",
    },
    {
        "id": "D4",
        "wrong": "2Fe³⁺ + 2e⁻ → 2Fe²⁺, tāpēc E° = 2·0,77 = 1,54 V",
        "key": "charge",
        "key_label": "Lādiņš vai zīme",
        "mistake_id": "M20",
        "hint": "Pārbaudi, vai elektroda potenciāls ir atkarīgs no vienādojuma koeficientiem.",
        "check": "E° ir intensīvs lielums (spriegums); koeficientu reizināšana nemaina potenciālu starpību (mainās tikai ΔG° = −zFΔE°).",
        "correct": "E°(Fe³⁺/Fe²⁺) nemainīgi paliek 0,77 V neatkarīgi no stehiometriskā reizinātāja.",
    },
    {
        "id": "D5",
        "wrong": "Permanganātometrijā skābas vides radīšanai var lietot HCl vai HNO₃",
        "key": "species",
        "key_label": "Daļiņa vai vide (pH)",
        "mistake_id": "M12",
        "hint": "Pārbaudi, vai pievienotās skābes anjons pats neiesaistās redoksa reakcijā ar titrantu.",
        "check": "Cl⁻ oksidējas par Cl₂ (patērē KMnO₄), bet NO₃⁻ pati ir spēcīgs oksidētājs. Titrēšanā der tikai atšķaidīta H₂SO₄.",
        "correct": "Permanganātometrijā izmanto vienīgi atšķaidītu H₂SO₄, kuras SO₄²⁻ anjons ir redoksa ziņā stabils.",
    },
    {
        "id": "D6",
        "wrong": "c = 0,132 mol/L noapaļo uz 0,13; m = 0,13·0,1·284 = 3,69 g",
        "key": "calc",
        "key_label": "Aprēķins vai vienības",
        "mistake_id": "M23",
        "hint": "Salīdzini starprezultātu ar nenoapaļotu vērtību reizinājumā.",
        "check": "Salīdzini ar nenoapaļotu vērtību: 0,132·0,1·284,04 = 3,75 g. Priekšlaicīga noapaļošana radījusi 1,6% novirzi.",
        "correct": "Starprezultātos saglabā vismaz vienu papildu zīmīgo ciparu; noapaļo vienreiz beigās (3,75 g vai ar 2 cipariem 3,7 g).",
    },
]

TOP_10_MISTAKES_IDS = ["M01", "M02", "M03", "M05", "M06", "M08", "M12", "M14", "M15", "M16"]


# ---------------------------------------------------------------- glossary (from termbase)
GLOSSARY = TB.GLOSSARY
SPECIES = TB.species_as_tuples()
USAGE = TB.USAGE
CONTRASTS = TB.CONTRASTS
TERMS = TB.TERMS
GATE_ROWS = TB.GATE_ROWS

SYMBOLS = [
    ("E", "Faktiskais elektroda vai elementa potenciāls jebkuros apstākļos (jebkurš pH, koncentrācija). Nernsts saista E ar E°.", "V", "LEC; §5"),
    ("E°", "Standartpotenciāls: pH 0, vienības aktivitātes, 298 K. Darba tabulās līdz 0,01 V; trešo decimāldaļu rāda tikai tur, kur to prasa avots vai pārbaude.", "V", "LEC P037; 3.–5. nod."),
    ("E°′", "Bioloģiskais standartpotenciāls pie pH 7. E°′ = E° − 0,0592·(m/n)·7, kur m = H⁺ skaits pusreakcijā, n = e⁻ skaits. Nedrīkst jaukt ar E° vienā darba kolonnā (A5).", "V", "A5; 2. un 8. nod."),
    ("ΔE", "Potenciālu starpība; E(katods) − E(anods)", "V", "LEC P024"),
    ("c(X)", "Molārā koncentrācija", "mol/L", "LEC §3.1"),
    ("n(X)", "Vielas daudzums; Nernstā n = elektronu skaits", "mol vai skaitlis", "B9"),
    ("m(H⁺)", "H⁺ skaits pusreakcijā (E°′ pārrēķinā); nejaukt ar masu m", "—", "A5; 2. nod."),
    ("V(X)", "Tilpums", "L vai mL", "LEC §3.1"),
    ("M(X)", "Molmasa", "g/mol", "A19"),
    ("z", "Ekvivalences skaitlis; elektroni uz formulas vienību", "—", "LEC §3.1"),
    ("F", "Faradeja konstante", "96 485 C/mol", "LEC P041"),
    ("R", "Universālā gāzu konstante", "8,314 J/(mol·K)", "A21"),
    ("T", "Temperatūra", "K", "LEC P040"),
    ("m", "Masa", "g", "LEC §3.1"),
    ("w", "Masas daļa", "%", "LEC self-test"),
    ("ρ", "Blīvums", "g/mL", "LEC self-test"),
    ("p", "Gāzes daļējais spiediens", "bar", "Nernsts"),
    ("lg", "Decimāllogaritms", "—", "LEC P045"),
    ("ln", "Naturālais logaritms", "—", "LEC P033"),
]

# ---------------------------------------------------------------- Nernst quotient builder (Task 07)
# Teaching aid only: which tokens enter Q. Not a numeric solver.
# enters: True → highlight in quotient; False → omitted (activity ≈ 1 or e⁻ count).
QUOTIENT_CASES = [
    {
        "id": "mno4h",
        "label": "MnO₄⁻/Mn²⁺ (skāba)",
        "half": "MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O",
        "n": 5,
        "Q": "[MnO₄⁻]·[H⁺]⁸ / [Mn²⁺]",
        "tokens": [
            {"sym": "MnO₄⁻", "enters": True, "how": "[Ox]¹"},
            {"sym": "H⁺", "enters": True, "how": "[H⁺]⁸"},
            {"sym": "e⁻", "enters": False, "how": "n = 5 saucējā pie 0,0592"},
            {"sym": "Mn²⁺", "enters": True, "how": "[Red]¹"},
            {"sym": "H₂O", "enters": False, "how": "šķīdinātājs (a ≈ 1)"},
        ],
    },
    {
        "id": "cr2o7",
        "label": "Cr₂O₇²⁻/Cr³⁺ (skāba)",
        "half": "Cr2O7^2- + 14H^+ + 6e^- -> 2Cr^3+ + 7H2O",
        "n": 6,
        "Q": "[Cr₂O₇²⁻]·[H⁺]¹⁴ / [Cr³⁺]²",
        "tokens": [
            {"sym": "Cr₂O₇²⁻", "enters": True, "how": "[Ox]¹"},
            {"sym": "H⁺", "enters": True, "how": "[H⁺]¹⁴"},
            {"sym": "e⁻", "enters": False, "how": "n = 6 saucējā"},
            {"sym": "Cr³⁺", "enters": True, "how": "[Red]² (koeficients 2)"},
            {"sym": "H₂O", "enters": False, "how": "šķīdinātājs (a ≈ 1)"},
        ],
    },
    {
        "id": "cl2",
        "label": "Cl₂/Cl⁻",
        "half": "Cl2 + 2e^- -> 2Cl^-",
        "n": 2,
        "Q": "p(Cl₂)/p° / [Cl⁻]²",
        "tokens": [
            {"sym": "Cl₂", "enters": True, "how": "p(Cl₂)/p° (gāze)"},
            {"sym": "e⁻", "enters": False, "how": "n = 2 saucējā"},
            {"sym": "Cl⁻", "enters": True, "how": "[Red]²"},
            {"sym": "H⁺", "enters": False, "how": "nav pusreakcijā"},
            {"sym": "H₂O", "enters": False, "how": "nav pusreakcijā"},
        ],
    },
    {
        "id": "fe3",
        "label": "Fe³⁺/Fe²⁺",
        "half": "Fe^3+ + e^- -> Fe^2+",
        "n": 1,
        "Q": "[Fe³⁺]/[Fe²⁺]",
        "tokens": [
            {"sym": "Fe³⁺", "enters": True, "how": "[Ox]"},
            {"sym": "e⁻", "enters": False, "how": "n = 1 saucējā"},
            {"sym": "Fe²⁺", "enters": True, "how": "[Red]"},
            {"sym": "H⁺", "enters": False, "how": "nav pusreakcijā"},
        ],
    },
    {
        "id": "o2h2o",
        "label": "O₂/H₂O (skāba)",
        "half": "O2 + 4H^+ + 4e^- -> 2H2O",
        "n": 4,
        "Q": "p(O₂)/p° · [H⁺]⁴",
        "tokens": [
            {"sym": "O₂", "enters": True, "how": "p(O₂)/p°"},
            {"sym": "H⁺", "enters": True, "how": "[H⁺]⁴"},
            {"sym": "e⁻", "enters": False, "how": "n = 4 saucējā"},
            {"sym": "H₂O", "enters": False, "how": "produkts = šķīdinātājs"},
        ],
    },
    {
        "id": "h2o2ox",
        "label": "H₂O₂/H₂O (oksidētājs)",
        "half": "H2O2 + 2H^+ + 2e^- -> 2H2O",
        "n": 2,
        "Q": "[H₂O₂]·[H⁺]²",
        "tokens": [
            {"sym": "H₂O₂", "enters": True, "how": "[Ox]"},
            {"sym": "H⁺", "enters": True, "how": "[H⁺]²"},
            {"sym": "e⁻", "enters": False, "how": "n = 2 saucējā"},
            {"sym": "H₂O", "enters": False, "how": "šķīdinātājs (a ≈ 1)"},
        ],
    },
]


OUTCOMES = [
    ("Zina un izprot", "Kas ir oksidēšanās-reducēšanās reakcijas, oksidētājs un reducētājs, reakcijas virziens.",
     1, "1; 4.1", "12.1–12.5"),
    ("Zina un izprot", "Kā potenciāli nosaka reakcijas virzienu.",
     2, "2; 4.1–4.8", "12.5; I1"),
    ("Prot", "Salīdzināt reakcijā piedalošos oks/red sistēmu potenciālus un noteikt virzienu.",
     2, "4.1–4.8", "4.2–4.5; 12.5"),
    ("Prot", "Uzrakstīt pusreakcijas oksidētājam un reducētājam.",
     6, "6.1–6.3", "piemēri 6.1–6.16; 12.6"),
    ("Prot", "Atrast koeficientus, lai pieņemto un atdoto elektronu skaits būtu vienāds.",
     6, "6.2–6.4", "piemēri 6.1–6.16; I3"),
    ("Prot", "Saīsināt summāro vienādojumu, iegūstot jonu formu.",
     6, "6.4–6.6", "piemēri 6.1–6.16; 12.7"),
    ("Prot", "Sastādīt un vienādot oks/red reakciju gala molekulāro vienādojumu.",
     6, "6", "piemēri 6.1–6.16; 13.C"),
    ("Prot (laboratorija)", "Novērot Mn krāsu maiņu trijās vidēs un izskaidrot to.",
     7, "7.2–7.5", "7.4; L21"),
    ("Prot (laboratorija)", "Titrēt Fe²⁺ ar KMnO₄ un aprēķināt c un m.",
     9, "9.2–9.6", "9.6; I4; 13.C"),
]
