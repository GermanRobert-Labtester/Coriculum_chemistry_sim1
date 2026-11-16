# -*- coding: utf-8 -*-
"""Errata and mistake seeds, as data. Every E id is rendered once from here.

Fields:
  where   source reference printed in the source
  says    what the source prints (short quote, markup allowed)
  correct the correction
  why     one sentence
  basis   S / X / S+X, as in SOURCE_LEDGER.md
  kind    ERR / INC / CONV / TYPO
  ch      chapter number where the note is shown inline (0 = appendix only)
"""

import re

E = {}

def e(i, where, says, correct, why, basis, kind, ch, verified=None):
    E[i] = dict(where=where, says=says, correct=correct, why=why,
                basis=basis, kind=kind, ch=ch, verified=verified)

e("E01", "A p.2, A p.16, D",
  "N<sub>A</sub> = 6,023·10<sup>23</sup> (A p.2), 6,022·10<sup>23</sup> (A p.16), 6,02·10<sup>23</sup> (D)",
  "Viena vērtība visur: 6,022·10<sup>23</sup> mol<sup>−1</sup>.",
  "Trīs avota lapas dod trīs ciparu skaitu vienam lielumam. Kopš 2019. gada N<sub>A</sub> ir precīzi 6,022 140 76·10<sup>23</sup> mol<sup>−1</sup>.",
  "S+X", "INC", 13)

e("E02", "A p.16",
  "SI tabula: kg = platīna-irīdija etalons; K = 1/273,16 no ūdens trīskāršā punkta; A = spēks starp vadiem; mol = atomu skaits 12 g <sup>12</sup>C",
  "Kopš 2019. gada 20. maija visas četras vienības definē ar fiksētām konstantēm h, k, e, N<sub>A</sub>.",
  "Tabulā dotās definīcijas ir vēsturiskas. Skatiet SI tabulu pielikumā: tur blakus stāv gan vēsturiskā, gan spēkā esošā definīcija.",
  "X", "ERR", 17,
  verified="BIPM SI brošūra: kopš 20.05.2019 kg, A, K, mol definē h, e, k, N_A")

e("E03", "A p.16",
  "„1 mol = 1000 mmol = 1·10<sup>−6</sup> µmol”",
  "1 mol = 10<sup>6</sup> µmol; 1 µmol = 10<sup>−6</sup> mol.",
  "Mikro- nozīmē miljono daļu, tāpēc vienā molā ir miljons mikromolu, nevis viena.",
  "S", "ERR", 6)

e("E04", "A p.16",
  "Cēzijs rakstīts „Cz”; gaismas intensitātes simbols „I”",
  "Cs. Gaismas intensitāte: <i>I</i><sub>v</sub>.",
  "Cēzija simbols ir Cs; gaismas intensitātes simbolu <i>I</i> aizēno strāvas stiprums <i>I</i>, tāpēc lieto apakšindeksu v.",
  "S+X", "TYPO", 17)

e("E05", "A p.2",
  "„Atommasas mērvienība … ir g/mol. Tātad <sup>12</sup>C: A = 12 g/mol”",
  "Trīs lielumi, trīs apzīmējumi: relatīvā atommasa <i>A</i><sub>r</sub> (bez mērvienības), molmasa <i>M</i> (g/mol), masas skaitlis <i>A</i> (vesels skaitlis).",
  "Avots lieto vienu burtu A trim dažādiem jēdzieniem. Tāpēc ¹²C ir <i>A</i><sub>r</sub> = 12 un <i>M</i> = 12 g/mol, bet masas skaitlis ir 12.",
  "S", "ERR", 2)

e("E06", "A p.2, E s.4",
  "„Pēc relatīvās atommasas, izmantojot A = N + Z, var aprēķināt neitronu skaitu”",
  "<i>A</i> šajā sakarībā ir masas skaitlis, nevis <i>A</i><sub>r</sub>. <i>N</i> = <i>A</i> − <i>Z</i> ir pareizi vienam izotopam.",
  "Hloram <i>A</i><sub>r</sub> = 35,45, un tāpēc no tā nevar iegūt vienu neitronu skaitu: ³⁵Cl ir 18, ³⁷Cl ir 20.",
  "S+X", "ERR", 2)

e("E07", "A p.2",
  "„Tritijs … dabā nav sastopams, to iegūst mākslīgi”",
  "Dabā ir tritija pēdas (kosmisko staru veidotas); rūpnieciski to iegūst mākslīgi. Pusperiods ≈ 12,3 gadi.",
  "Tas ir radioaktīvs un īslaicīgs, tāpēc praktiski viss tritijs ir mākslīgs, bet „nav sastopams” ir pārāk stingri.",
  "X", "CONV", 2,
  verified="NIST (Lucas & Unterweger 2000): tritija pusperiods 12,32 g.; kosmisko staru pēdas dabā")

e("E08", "A p.1",
  "„16 vertikālās rindas”; grupas 1.A–8.A un 1.B–8.B",
  "IUPAC numerācija: 18 grupas. Kursa shēma ir vecā CAS shēma ar 8 A un 8 B grupām; VIIIB ir trīs kolonnas.",
  "Abas numerācijas apzīmē vienu un to pašu tabulu, tāpēc jāprot lasīt abas. Skatiet periodiskās tabulas attēlu: tur virsū ir IUPAC numuri, apakšā kursa A/B burti.",
  "X", "CONV", 2,
  verified="IUPAC 1–18; CAS: A galvenās grupas, B pārejas metāli")

e("E09", "A p.1–2, E s.9",
  "REN „kā elektrontieksmes un jonizācijas enerģijas pussumma”",
  "Tā ir Mullikena definīcija. Tabulās lietotā REN skala (F = 3,98) ir Paulinga skala.",
  "Abas ir elektronegativitātes mēri, bet nav viena un tā pati skala; sajaucot tās, skaitļi nesakrīt.",
  "X", "CONV", 2,
  verified="IUPAC Gold Book E01990 (electronegativity): Mulliken vidējais; Paulinga skala lietotākā")

e("E10", "A p.3, E s.22, 27",
  "Jonu saite, ja ΔREN ≥ 2; polārā kovalentā, ja ΔREN < 2",
  "Saites raksturo kā nepārtrauktu pāreju. Biežāk lietotās robežas: 0,4 un 1,7 (Paulings); kursa materiāls lieto 2.",
  "Kursa paša piemēri neatbilst tā paša likumam: MgCl₂ ΔREN = 1,85, Al₂S₃ = 0,97, HF = 1,78. Tāpēc atbildē vienmēr pasakiet, kuru kritēriju lietojat.",
  "S+X", "INC", 3,
  verified="Paulinga 1,7 ≈ 50 % jonu raksturs (robeža nav asa; kurss lieto 2)")

e("E11", "A p.4",
  "Valences saišu un molekulāro orbitāļu metodes apraksts atkārtots divreiz",
  "Vienu reizi pietiek.",
  "Tas ir drukas dublējums; saturs nemainās.",
  "S", "TYPO", 3)

e("E12", "E s.30",
  "„π saites enerģija ir apmēram 10 reizes mazāka par σ saites enerģiju”",
  "π saite ir vājāka, bet ne desmitkārt: C–C 347, C=C 614, C≡C 839 kJ/mol, tāpēc π ir ap 65–77 % no σ.",
  "10 reizes mazāka enerģija nozīmētu gandrīz neko; dubultsaite tomēr ir ievērojami stiprāka par vienkāršu.",
  "X", "ERR", 3,
  verified="vidējās saišu enerģijas: C–C 347; C=C 614; C≡C 839 kJ/mol")

e("E13", "A p.4, E s.34",
  "Ūdeņraža saite starp F/O/N atomu un „ūdeņraža atoma kodolu (protonu)”; „starpmolekulārās saites”",
  "Ūdeņradis ir kovalenti saistīts un nes daļlādiņu δ+; tas pievelk cita F/O/N atoma vientuļo elektronu pāri. Tā ir starpmolekulāra mijiedarbība, ≈ 5–40 kJ/mol.",
  "Brīvs protons šķīdumā nepastāv, un ūdeņraža saite nav tāda paša tipa kā kovalentā. CH₄ neveido ūdeņraža saites, jo C–H saite ir gandrīz nepolāra.",
  "X", "ERR", 3)

e("E14", "A p.4, E s.32",
  "Metāliskā saite: „neitrāli atomi un katjoni”, „protonu lādiņi summējoties”",
  "Modelis: katjonu režģis delokalizētu elektronu „jūrā”. Saglabājiet kursa terminu „elektronu gāze”.",
  "Lādiņu saskaitīšana ar protoniem ir maldinoša; svarīgi, ka elektroni ir kopīgi visam režģim un to kustība izskaidro vadītspēju.",
  "X", "CONV", 3)

e("E15", "A p.9 pret E s.36",
  "A: „atomārais kristālrežģis” = dimants, Si, B. E: „atomāra uzbūve” = cēlgāzes, „nemolekulāra” = grafīts, dimants",
  "„Atomu (kovalentais) kristālrežģis” dimantam un silīcijam; „atomārs” tikai vienatomu vielām (cēlgāzēm).",
  "Viens vārds avotā apzīmē divas dažādas lietas, tāpēc tas jānodala.",
  "S", "INC", 10)

e("E16", "E s.14–15",
  "„Enerģijas līmenis ir aprēķināms pēc formulas 2n²”; „līmeņu skaits sakrīt ar grupas perioda numuru”",
  "2n² ir lielākais elektronu skaits līmenī n (2, 8, 18, 32). Līmeņu skaits sakrīt ar perioda numuru.",
  "2n² nav līmeņa enerģija, bet ietilpība. Trešais līmenis nepiepildās pirms 4s; aizpildīšanās kārtību rāda atsevišķa shēma.",
  "S", "ERR", 2)

e("E17", "A p.5, E s.50",
  "Īstie šķīdumi < 1 nm; koloīdi 1–100 nm; rupjie > 1000 nm",
  "Rupjdispersās sistēmas parasti sākas pie 100 nm; IUPAC ļauj koloīdiem stiepties līdz ≈ 1 µm.",
  "Diapazons 100–1000 nm avotā nepaliek nekur. Attēlā robeža ir novilkta pie 100 nm un atzīmēta kā vienošanās.",
  "S+X", "INC", 4)

e("E18", "A p.6",
  "Labi šķīstošas > 10 g; mazšķīstošas 0,1–10 g; praktiski nešķīstošas < 0,01 g uz 100 g ūdens",
  "Diapazons 0,01–0,1 g paliek bez klases. Ja lieto šīs trīs klases, robežas jānorāda viennozīmīgi.",
  "Trūkstošais intervalls nozīmē, ka vielu ar šķīdību 0,05 g/100 g nevar iekļaut nevienā klasē. Šķīdības tabula lieto citas robežas (1 g un 0,001 g), tāpēc tā ir uzziņa, nevis definīcija.",
  "S", "INC", 5)

e("E19", "D p.7 pret D p.3",
  "„Šķīdums: šķidrums, ko iegūst, sajaucot cietu vai gāzveida vielu ar šķīdinātāju”",
  "Šķīdums ir vienfāzes maisījums; tas var būt gāzveida, šķidrs vai ciets.",
  "D p.3 pati uzskaita gāzveida, šķidros un cietos šķīdumus, kā arī šķidrumu šķīdumus šķidrumos. Definīcija jālasa plaši.",
  "S", "INC", 5)

e("E20", "D p.4",
  "NaCl benzolā = koloīds šķīdums; gaiss un audi tabulā kā dispersās sistēmas",
  "NaCl benzolā praktiski nešķīst; piemērs ilustrē principu, ka koloīds ir stāvoklis, nevis vielu klase.",
  "Gaiss ir īsts gāzu maisījums. Audus kā „solidosolus” avots klasificē pats un atzīmē ar zvaigznītēm; tā ir kursa konvencija, nevis vispārpieņemta klasifikācija.",
  "X", "CONV", 4)

e("E21", "D p.5",
  "Mākslīgā niere = elektrodialīze",
  "Hemodialīze: difūzija pa koncentrācijas gradientu un ultrafiltrācija caur puscaurlaidīgu membrānu.",
  "Elektrodialīze jonus pārvieto elektriskā laukā (atsāļošana); tā nav tas pats process, ar ko attīra asinis.",
  "X", "ERR", 4)

e("E22", "D p.8",
  "„Gāzu šķīdība, paaugstinot T, vienmēr samazinās”",
  "Parasti, ūdenī. H₂, He un Ne šķīdībai ūdenī ir minimums ap 30–60 °C; organiskos šķīdinātājos tā bieži pieaug.",
  "„Vienmēr” ir pārāk stingri, un eksāmenā to var prasīt kā izņēmumu.",
  "X", "ERR", 5)

e("E23", "D p.10",
  "„BaCl·2H₂O”",
  "BaCl₂·2H₂O.",
  "Kristālhidrātā bārija hlorīda formula ir BaCl₂; indekss 2 pieder hloram.",
  "S", "TYPO", 5)

e("E24", "D p.9–10",
  "„Hidrāti” gan solvatācijas apvalkam, gan CuSO₄·5H₂O",
  "Trīs atsevišķi jēdzieni: hidratācija/solvatācija (apvalks šķīdumā), kristālhidrāts (ūdens kristāla režģī), hidrolīze (reakcija ar ūdeni).",
  "Ja visu sauc par „hidrātu”, zūd atšķirība starp šķīšanu un kristālu uzbūvi.",
  "S", "CONV", 5)

e("E25", "A p.7, E s.54 pret D p.11",
  "Stiprs α > 0,7, vājš α < 0,1 pret stiprs α > 30 %, vidēji stiprs 3–30 %, vājš < 3 %; D arī „α < 30 % → vājš”",
  "α ir atkarīgs no koncentrācijas un temperatūras. Elektrolīta stiprumu drošāk raksturo K<sub>a</sub> / K<sub>b</sub>. Abas shēmas ir jāparāda.",
  "Avotā ir divas nesavienojamas skalas un viena paša pretstata teikumi. Zemāk dotās α vērtības ir ilustratīvas atšķaidītiem šķīdumiem.",
  "S", "INC", 7)

e("E26", "A p.6 pret A p.11, E s.40",
  "Arrhenius 1887 (A p.6) un 1886 (A p.11)",
  "Disociācijas teorija publicēta 1887. gadā; disertācija 1884.",
  "Divi gadi vienā mācību materiālā; izvēlieties vienu un turiet to.",
  "S+X", "INC", 8,
  verified="Arrēniusa disertācija 1884; disociācijas teorija publicēta 1887")

e("E27", "B #3, A p.7, D p.11, E s.41",
  "„NH₄OH” un „NH₃·H₂O” lietoti kā sinonīmi",
  "Atsevišķs NH₄OH nav zināms. Rakstiet NH₃(aq) vai NH₃·H₂O: NH₃ + H₂O ⇌ NH₄⁺ + OH⁻, K<sub>b</sub> = 1,8·10<sup>−5</sup>.",
  "Amonjaks ir bāze bez OH grupas; hidroksīdjons rodas no ūdens, nevis no „NH₄OH”.",
  "X", "CONV", 7)

e("E28", "A p.7, E s.54",
  "„Vājo elektrolītu šķīdumi … sāļu anjoni HPO₄²⁻, HCO₃⁻”",
  "Tie ir amfiprotiski joni (amfolīti), nevis šķīdumi. HCO₃⁻ ūdenī vairāk darbojas kā bāze: NaHCO₃(aq) pH ≈ 8,3.",
  "Jons nav šķīdums. Turklāt HCO₃⁻ var gan atdot, gan pieņemt protonu, tāpēc to nevar vienkārši saukt par „vāju elektrolītu”.",
  "X", "CONV", 7)

e("E29", "A p.7, E s.56",
  "pH = −lg[H₃O⁺], tad [H⁺] = 10<sup>−pH</sup>; [H⁺] = [OH⁻] = 10<sup>−7</sup> bez temperatūras",
  "H⁺ un H₃O⁺ ir viens un tas pats jons divos pierakstos. pH = −lg <i>a</i>(H⁺). Neitrāla vide ir 7,00 tikai 25 °C. Kw 1,0·10⁻¹⁴ un 6,81 nav nolasīti no primārās līdzsvara tabulas.",
  "K<sub>w</sub> mainās ar temperatūru: 37 °C neitrāls pH ir ≈ 6,81. Tāpēc „pH 7 = neitrāls” nav universāla likumsakarība.",
  "S+X", "CONV", 8)

e("E30", "D p.11",
  "H₃BO₃ uzskaitīta kā parasta vāja skābe-elektrolīts",
  "B(OH)₃ + 2 H₂O ⇌ B(OH)₄⁻ + H₃O⁺: Lūisa skābe, kas pievieno OH⁻, nevis atdod protonu.",
  "Tā ir noderīga nianse, bet skābes definīciju tā nemaina: ūdeņraža jonu avots joprojām ir ūdens.",
  "X", "CONV", 8)

e("E31", "A p.11, E s.40",
  "Skābes skaita pēc „ūdeņraža atomu skaita, kas spēj aizvietoties”",
  "Definīcija ir pareiza, bet viegli pārprastama: CH₃COOH ir vienvērtīga ar četriem H; H₃PO₃ ir divvērtīga ar trim.",
  "Skaita tikai skābos ūdeņražus (tos, kas saistīti ar skābekli), ne visus H atomus.",
  "S", "CONV", 8)

e("E32", "A p.8",
  "Vājas skābes un vājas bāzes sāls: „hidrolizējas katjons un anjons … pH = 7”",
  "pH ≈ 7 + ½(pK<sub>a</sub> − pK<sub>b</sub>). NH₄CH₃COO ≈ 7 nejauši; NH₄F ir skābs; (NH₄)₂CO₃ bāzisks. Al₂S₃ hidrolizējas pilnīgi.",
  "Ja abi joni hidrolizējas, pH nosaka tas, kurš ir stiprāks; vienāds pH nav noteikums.",
  "S+X", "ERR", 9)

e("E33", "A p.8",
  "Zn²⁺ + 2Cl⁻ + H₂O ⇌ Zn(OH)₂ + H⁺ + Cl⁻ un Zn²⁺ + H₂O ⇌ Zn(OH)₂ + H⁺",
  "Pirmais solis: Zn²⁺ + H₂O ⇌ ZnOH⁺ + H⁺; kopā: Zn²⁺ + 2 H₂O ⇌ Zn(OH)₂ + 2 H⁺.",
  "Abi avota vienādojumi nesabalansējas H un O ziņā. Pieņemtais solis un kopējais vienādojums saglabā atomus un lādiņu +2 = +2; līdzsvara apjomu bilance nepierāda.",
  "S", "ERR", 9)

e("E34", "A p.10",
  "„MnO₃ – mangāna(VI) oksīds” starp skābajiem oksīdiem",
  "Lietojiet Mn₂O₇ (VII), MnO₂ (IV), MnO (II).",
  "MnO₃ nav parasts, izolējams oksīds; eksāmenā drošāk lietot stabilus piemērus.",
  "X", "CONV", 10)

e("E35", "A p.10",
  "Fe₂O₃ uzskaitīts starp amfotērajiem oksīdiem",
  "Fe₂O₃ galvenokārt ir bāzisks; vāji amfotērs tikai sakausējumā ar sārmiem.",
  "Ikdienas reakcijās tas reaģē ar skābēm, nevis ar sārmiem, tāpēc amfotērās īpašības jāatzīmē kā nosacītas.",
  "X", "CONV", 10)

e("E36", "A p.10–12",
  "(a) Na₂O + HCl → 2NaCl + H₂O; (b) SO₃ + NaOH → Na₂SO₄ + H₂O; (c) NaOH + CO₂ → Na₂CO₃ + H₂O; (d) 2Al(OH)₃ + 2HCl → Al₂(SO₄)₃ + 3H₂O; (e) Ba(OH)₂ + MgSO₄ → BaSO₄↓ + Mg(OH)₂; H₂SO₄ + BaCl₂ → BaSO₄ + 2HCl",
  "(a) Na₂O + 2HCl → 2NaCl + H₂O; (b) SO₃ + 2NaOH → Na₂SO₄ + H₂O; (c) 2NaOH + CO₂ → Na₂CO₃ + H₂O; (d) 2Al(OH)₃ + 3H₂SO₄ → Al₂(SO₄)₃ + 6H₂O; (e) Ba(OH)₂ + MgSO₄ → BaSO₄↓ + Mg(OH)₂↓. Rinda H₂SO₄ + BaCl₂ → BaSO₄↓ + 2HCl atomu ziņā jau sakrīt; ↓ pie BaSO₄ ir šķīdības atzīme.",
  "Rindās (a)–(d) trūkst koeficienta vai ir sajaukta skābe. Abas (e) nogulsnes un BaSO₄ šķīdības atzīme no atomu bilances neizriet.",
  "S", "ERR", 10)

e("E37", "A p.13, D p.16",
  "„Fe + CuSO → FeSO + Cu↓” (iespiests abos failos)",
  "Fe + CuSO₄ → FeSO₄ + Cu↓.",
  "Vara nogulsnējas uz dzelzs virsmas kā metāls, nevis kā sāls.",
  "S", "TYPO", 11)

e("E38", "A p.15",
  "„2NaOH + H₂SO₄²⁻ → 2H₂O + Na₂SO₄”",
  "2NaOH + H₂SO₄ → Na₂SO₄ + 2H₂O.",
  "Skābes molekula nav lādēta; sulfātjons SO₄²⁻ ir tikai produkta pusē.",
  "S", "TYPO", 8)

e("E39", "A p.12",
  "„2NaCl + H₂SO₄ → Na₂SO₄ + 2HCl”; „Aktīvākās skābes reaģē ar sāļiem”",
  "Nepieciešams ciets NaCl, koncentrēta H₂SO₄ un karsēšana: mazgaistoša skābe izspiež gaistošu.",
  "Ūdens šķīdumā visi joni paliek šķīdumā, tāpēc apmaiņa nenotiek. Šī reakcija ir laboratorijas metode HCl iegūšanai.",
  "X", "CONV", 10)

e("E40", "D p.15",
  "„Zn(OH)₂↓ + NaOH → Na₂[Zn(OH)₄]”",
  "Zn(OH)₂ + 2NaOH → Na₂[Zn(OH)₄]. Jonu forma: Zn(OH)₂ + 2OH⁻ → [Zn(OH)₄]²⁻.",
  "Cinks ir amfotērs: viens Zn²⁺ saista divus OH⁻ papildus, tāpēc vajag divus NaOH. Jonu vienādojums zem tā avotā jau ir pareizs.",
  "S", "ERR", 11)

e("E41", "D p.15–16",
  "Nodaļu virsraksti „Reakcijas mehānisms – savienošanās / aizvietošanas / sadalīšanas / apmaiņas”",
  "Tie ir reakciju veidi. Mehānisms ir pakāpenisks saišu pārraušanas un veidošanas ceļš.",
  "Veids atbild uz „kas ar ko”, mehānisms uz „kā soli pa solim”. Terminus nedrīkst lietot kā sinonīmus.",
  "S+X", "ERR", 11)

e("E42", "D p.17",
  "Gāzi veidojoša apmaiņa: „H₂S, HF, HCl, HI, NH₃”",
  "Biežākie gadījumi ir CO₂ (caur H₂CO₃) un SO₂ (caur H₂SO₃); B #7 lieto K₂SO₃ + HCl.",
  "Saraksts izlaiž tieši tos piemērus, kas visbiežāk sastopami uzdevumos.",
  "S", "CONV", 11)

e("E43", "A p.13, p.14, E s.45",
  "„Mg⁺²O⁻²”, „Mn⁺⁷”, „O⁻”; lietoti gan „oksidēšanās pakāpe”, gan „oksidēšanas pakāpe”",
  "Jona lādiņš: Mg²⁺ (vispirms skaitlis, tad zīme). Oksidēšanas pakāpe: +2 vai (II). Viens termins: oksidēšanas pakāpe.",
  "Jona lādiņš un oksidēšanas pakāpe ir dažādi lielumi ar atšķirīgu pierakstu; sajaukt tos nozīmē zaudēt punktus redoksuzdevumos.",
  "S+X", "CONV", 12,
  verified="IUPAC Red Book: jona lādiņš ar arābu cipariem (Mg²⁺), oksidēšanas pakāpe ar romiešu (II)")

e("E44", "A p.14",
  "„H₂ – 2e⁻ =→ 2H⁺”",
  "H₂ − 2e⁻ → 2H⁺.",
  "Avota defekts ir =→ un domuzīme, nevis atomu skaits: H un lādiņš sakrīt, ja abi elektroni ir labajā pusē (0 = +2 + 2·(−1)).",
  "S", "TYPO", 12)

e("E45", "A p.14, E s.45",
  "Skābeklim „parasti −2”, ūdeņradim „parasti +1”",
  "Izņēmumi: peroksīdos O = −1, OF₂ O = +2; metālu hidrīdos H = −1.",
  "„Parasti” ir pareizi, bet eksāmenā izņēmumi ir tieši tie, ko prasa.",
  "X", "CONV", 12,
  verified="oksidēšanas pakāpju likumi: peroksīdos O = −1, OF₂ O = +2, hidrīdos H = −1")

e("E46", "A p.13, p.14",
  "C + O₂ → CO₂ + 409 kJ/mol; C₃H₈ + 5O₂ → 3CO₂ + 4H₂O(g) + 2200; C₂H₅OH + 3O₂ → 2CO₂ + 3H₂O(g) + 1292; „+Q / −Q”",
  "Literatūra: CO₂ 393,5; propāns 2043 (H₂O(g)) vai 2220 (H₂O(l)); etanols 1235 (H₂O(g)) vai 1367 (H₂O(l)). Šie aizstājumi nav nolasīti no primārās termokīmijas tabulas.",
  "Skaitļi atšķiras tāpēc, ka avotā sajaucas ūdens agregātstāvokļi. Vienmēr norādiet, vai ūdens ir gāze vai šķidrums. +Q zīme ir pretēja ΔH zīmei.",
  "X", "ERR", 11)

e("E47", "E s.48",
  "Standartpotenciāli: Br₂/2Br⁻ +0,96 V; O₂/H₂O +1,21865 V; PbO₂/Pb²⁺ +1,80 V; „NH₄OH” NO₃⁻ rindā",
  "Literatūra ≈ +1,07 V; +1,229 V; +1,455 V. +0,96 V ir NO₃⁻/NO vērtība. Lietojiet reducēšanās potenciālus. Šie volti nav nolasīti no primārās elektrodu tabulas.",
  "Tabula avotā satur pārbīdītas vērtības. Aizstājošos voltus nedrīkst saukt par pārbaudītiem, kamēr primārā tabula nav nolasīta.",
  "X", "ERR", 12)

e("E48", "D p.2",
  "„pH 7,32–7,45, 7,4 – neitrāla vide”",
  "Arteriālās asinis 7,35–7,45 ir vāji sārmainas. Neitrāls ūdens ir 7,00 pie 25 °C un ≈ 6,8 pie 37 °C. Intervāls 7,35–7,45 nav apstiprināts klīniskais slieksnis.",
  "7,4 ir sārmains, nevis neitrāls. 7,32 drīzāk ir venozās asinis.",
  "S+X", "ERR", 8)

e("E49", "D p.2",
  "Stabilizējamie parametri: „asins gāzu sastāvs (skābeklis, slāpeklis)”",
  "O₂ un CO₂ (p<sub>O₂</sub>, p<sub>CO₂</sub>). N₂ nav regulējama asins gāze.",
  "Slāpeklis asinīs ir izšķīdis, bet organisms to neregulē, tāpēc tas nav homeostāzes parametrs.",
  "X", "ERR", 14)

e("E50", "D p.2",
  "„temperatūra 36,5–38,6 °C”",
  "Parastā kodola temperatūra ≈ 36,1–37,5 °C. Šis diapazons nav nolasīts no klīniskā avota. <span class=\"tag\">[UNVERIFIED]</span> C-12.",
  "38,6 °C jau ir drudzis; augšējā robeža avotā ir pārāk augsta.",
  "X", "ERR", 14)

e("E51", "D p.1",
  "„vairāk nekā 70 % šķidruma”; „bezšūnu … šūnu citoplazmas šķidrums”; „iekšējās vides tilpums ≈ 14,5 L”",
  "Pieaugušam cilvēkam kopējais ūdens ≈ 50–60 % no masas; > 70 % ir zīdaiņa rādītājs. Citoplazma ir šūnu iekšienē, tāpēc nevar būt „bezšūnu” fāzē. 14,5 L atbilst šūnas ārpusē esošajam šķidrumam. Diapazons nav nolasīts no fizioloģijas avota. <span class=\"tag\">[UNVERIFIED]</span> C-13.",
  "Trīs teikumi vienā rindkopā sajauc kopējo ūdeni, ārpusšūnu šķidrumu un šūnu iekšējo vidi.",
  "S+X", "ERR", 14)

e("E52", "D p.2",
  "„Mononukleāro (mono – viens; nucleum – šūna)”",
  "nucleus = kodols.",
  "Morfoloģija nozīmē uzbūvi, un „mononukleārs” nozīmē vienu kodolu, nevis vienu šūnu.",
  "X", "ERR", 14)

e("E53", "D p.3",
  "„Hiperaldosteronisms (Kušinga sindroms)”; „Diabetes inspidus”; „preperāti”",
  "Primārais hiperaldosteronisms = Konna sindroms; Kušings = hiperkortizolisms. Diabetes insipidus. preparāti.",
  "Trīs dažādas kļūdas vienā laboratorijas lapā; terminoloģija medicīnā ir daļa no atbildes.",
  "X", "ERR", 14)

e("E54", "D p.12",
  "Olbaltumvielas, ogļhidrāti, tauki „kopā ar nukleīnskābēm ir organisma enerģijas avots”; 55–60 / 20–25 / 15–20 %",
  "Nukleīnskābes uzglabā un pārraida informāciju; tās nav kurināmais. Procenti ir uztura vadlīniju diapazoni, nevis konstantes.",
  "Nukleīnskābes organismā netiek oksidētas enerģijas ieguvei tādā pašā nozīmē kā glikoze, tauki un olbaltumvielas.",
  "X", "ERR", 14)

e("E55", "D p.13",
  "„Hlorofils katalizēts bioķīmisks process”",
  "Hlorofils absorbē gaismu; CO₂ fiksāciju katalizē enzīms (Rubisco).",
  "Hlorofils nav enzīms; tas pārveido gaismas enerģiju, bet oglekļa saistīšanu veic olbaltumvielas.",
  "X", "CONV", 14)

e("E56", "D p.13",
  "„Visi lipīdi ir ūdenī nešķīstoši … vitamīni K, E, D, A”",
  "Amfifīlie lipīdi (fosfolipīdi) veido micellas un divslāņus. Taukos šķīstošie vitamīni ir lipofīli, nevis lipīdi stingrā nozīmē.",
  "Fosfolipīdi ir gan ūdenī šķīstoša galva, gan tauku astes, tāpēc tie nav vienkārši „nešķīstoši”.",
  "X", "CONV", 14)

e("E57", "D p.15",
  "Krebsa cikls: „ķīmiskā enerģija pārnesta uz … ATP”",
  "Cikls dod NADH, FADH₂ un vienu GTP/ATP; lielākā daļa ATP rodas oksidatīvajā fosforilēšanā.",
  "Ja ATP pieskaita tikai ciklam, zūd elpošanas ķēdes loma.",
  "X", "CONV", 14)

e("E58", "D p.18",
  "„Aprēķinot n_B, n_A jādala ar stehiometrijas rādītāju b”",
  "Formula virs teikuma ir pareiza: n<sub>B</sub> = n<sub>A</sub> · b / a (dala ar a, reizina ar b).",
  "Teikums ir pretējs formulai. Ja to iegaumē, visi aprēķini apgriežas otrādi. Simboliskā pārbaude: dalītājs ir a, reizinātājs ir b.",
  "S", "ERR", 13)

e("E59", "D p.19–20",
  "„m_Al / V₀,O₂ = 4 mol·26,98154 / 4 mol·26,98154”; „101,061 g/mol”; „M_H₂SO₄ = 23+16+1 = 40”; attiecība „2,20”",
  "4·M<sub>Al</sub> : 3·V₀; 101,961 (Al₂O₃); tā ir M<sub>NaOH</sub>; 0,225 / 0,102 = 2,21.",
  "Četras skaitļu kļūdas vienā piemērā; studentam jāredz, ka 188,95 g un 62,3 L tomēr iznāk pareizi, jo kļūdas viena otru neizlabo.",
  "S", "TYPO", 13)

e("E60", "D p.19–20",
  "V₀ = 22,4 L/mol „normālos apstākļos”",
  "Norādiet T un p: 0 °C un 101,325 kPa → 22,414 L/mol; 0 °C un 100 kPa → 22,711 L/mol; 25 °C un 100 kPa → 24,79 L/mol. Šie skaitļi seko no pV = nRT (R = 8,314462618 J/(mol·K)). Nosaukumi IUPAC STP un SATP šajā piegājienā nav pārlasīti.",
  "22,4 nav universāla konstante. 100 g Al vajag 62,3 L O₂ pie 0 °C un 101,325 kPa un 68,9 L pie 25 °C un 100 kPa. Šī aritmētika nav IUPAC nosaukuma pārbaude.",
  "S+X", "CONV", 13)

e("E61", "B, C",
  "B nosaukts „…2025”, bet kājenē „…2021”; C „2020” un apraksta Zoom kursu",
  "Versijas atšķiras. Materiāls citē faila nosaukumu tā, kā tas saņemts, un neapgalvo konkrētu gadu.",
  "Gadu nevar pierādīt no pašiem failiem, tāpēc to nelieto kā faktu.",
  "S", "INC", 1)


# ---------------------------------------------------------------- mistakes
M = {}

def m(i, wrong, feels, right, check, tag, ch):
    M[i] = dict(wrong=wrong, feels=feels, right=right, check=check, tag=tag, ch=ch)

m("M01", "Mainīt indeksus, nevis koeficientus, lai sabalansētu vienādojumu",
  "Šķiet, ka „2” pie formulas ir vienkāršākais veids, kā izlīdzināt skābekli.",
  "Maina tikai koeficientus formulas priekšā; indeksi ir vielas sastāvs un tos mainīt nedrīkst.",
  "Pārbaudiet, vai katra formula joprojām ir tā pati viela, un tad skaitiet atomus abās pusēs.", "avots", 11)

m("M02", "Rakstīt „NaCl molekula” un skaitīt formulvienību kā molekulu",
  "Ikdienā sāls „molekula” izklausās dabiski, un formula ir viena.",
  "Jonu kristālā atsevišķu molekulu nav; NaCl ir formulvienība, kas dod divus jonus.",
  "Ja savienojumā ir metāls un nemetāls, jautājiet: vai tas ir jonu režģis? Ja jā, tā ir formulvienība.", "avots", 2)

m("M03", "Aizmirst, cik jonu dod viena formulvienība",
  "Al₂(SO₄)₃ izskatās „liela”, tāpēc šķiet, ka jonu skaits ir mazs.",
  "Skaita katru jonu: 2 Al³⁺ + 3 SO₄²⁻ = 5 joni.",
  "Saskaitiet indeksus ārpus iekavām un iekavās atsevišķi; pārbaudiet lādiņu summu = 0.", "avots", 7)

m("M04", "Salīdzināt gramus, nevis molus, un izvēlēties ierobežojošo reaģentu pēc masas",
  "9 g pret 9 g izskatās vienādi, tāpēc šķiet, ka vielas ir līdzvērtīgas.",
  "Vielas reaģē molu attiecībā, kas ņemta no koeficientiem; masa jāpārvērš molos.",
  "Daliet katru masu ar savu molmasu un tad salīdziniet attiecību ar koeficientu attiecību.", "avots", 13)

m("M05", "Uzskatīt, ka „48 g” un „48 mL” šķīduma ir viens un tas pats",
  "Abos uzdevumos ir 48, un procenti ir vieni un tie paši.",
  "Molaritātei vajag šķīduma tilpumu; masu pārvērš tilpumā ar blīvumu ρ.",
  "Uzrakstiet, kas dots: masa vai tilpums. Ja tilpums, c = n / V; ja masa, vispirms V = m / ρ.", "avots", 6)

m("M06", "„Skābais sāls ⇒ skābs šķīdums”",
  "Nosaukumā ir vārds „skābs”, tāpēc šķiet, ka arī pH būs zem 7.",
  "Skābais sāls satur aizvietojamu H, bet tā šķīdums var būt bāzisks: NaHCO₃ pH ≈ 8,3.",
  "Skābais sāls ir par sastāvu; par vidi lemj hidrolīze, ne nosaukums.", "avots", 10)

m("M07", "Aizmirst, ka amfotērie hidroksīdi šķīst sārma pārākumā",
  "„Nešķīstoša bāze” šķiet nešķīstoša visos apstākļos.",
  "Al(OH)₃ un Zn(OH)₂ šķīst gan skābē, gan sārmā, veidojot kompleksus vai hidroksosāļus.",
  "Ja nogulsnes pazūd, pievienojot NaOH pārākumu, tās bija amfotēras.", "avots", 10)

m("M08", "Saukt par elektrolītu jebkuru vadītāju vai jebko, kas reaģē ar ūdeni",
  "Varš vada strāvu, un CaO ar ūdeni dod sārmu, tāpēc abi šķiet „elektrolīti”.",
  "Elektrolīts vada strāvu jonu dēļ šķīdumā vai kausējumā. Metāls vada ar elektroniem; CaO vispirms jāizšķīdina un jāreaģē.",
  "Jautājiet: vai šajā šķīdumā ir brīvi joni? Ja nav, tas nav elektrolīts.", "avots", 7)

m("M09", "Jaukt „stiprs elektrolīts”, „šķīstošs” un „koncentrēts”",
  "Visi trīs vārdi ikdienā nozīmē „stiprs”.",
  "Stiprums ir disociācijas pakāpe, šķīdība ir cik daudz izšķīst, koncentrācija ir cik daudz ir šķīdumā.",
  "Atšķaidīta HCl ir stiprs elektrolīts; koncentrēts cukurs ir neelektrolīts.", "avots", 7)

m("M10", "Uzskatīt, ka polāras saites nozīmē polāru molekulu",
  "CO₂ saites ir polāras, tāpēc šķiet, ka arī molekula ir polāra.",
  "Molekulas polaritāti nosaka arī ģeometrija: CO₂ ir lineāra, dipoli kompensējas, molekula ir nepolāra.",
  "Uzzīmējiet molekulu un pārbaudiet, vai dipolu summa nav nulle.", "papildinājums", 3)

m("M11", "Uzskatīt jonu un kovalento saiti par slēdzi, kas ieslēdzas pie „metāls + nemetāls”",
  "„Metāls ar nemetālu = jonu saite” ir vienkāršs noteikums, ko viegli lietot bez domāšanas.",
  "Saite ir nepārtraukta pāreja; lēmumu nosaka ΔREN un jāpasaka lietotais kritērijs.",
  "Aprēķiniet ΔREN un ierakstiet to atbildē; ja tā ir robeža, atzīmējiet, ka tā ir vienošanās.", "avots", 3)

m("M12", "Zīmēt ūdeņraža saiti molekulas iekšpusē vai no jebkura H",
  "Ja H ir molekulā, šķiet, ka tas var veidot ūdeņraža saiti.",
  "Ūdeņraža saite iet no δ+ H (pie F/O/N) uz cita F/O/N vientuļo pāri; CH₄ to neveido.",
  "Pārbaudiet abus galus: donors ar H–F/O/N un akceptors ar vientuļo pāri.", "papildinājums", 3)

m("M13", "Jaukt oksidēšanas pakāpi, jona lādiņu un valenci; „O vienmēr −2, H vienmēr +1”",
  "Skaitļi izskatās līdzīgi, un skābeklis tiešām parasti ir −2.",
  "Jona lādiņš ir veselai daļiņai (Fe³⁺), oksidēšanas pakāpe ir atomam (+3); valence ir saišu skaits.",
  "Peroksīdā O ir −1, OF₂ O ir +2, metālu hidrīdā H ir −1; pārbaudiet izņēmumus.", "avots", 12)

m("M14", "„Oksidētājs oksidējas”",
  "Vārds „oksidētājs” skan tā, it kā tas būtu tas, kas oksidējas.",
  "Oksidētājs pievieno elektronus un pats reducējas; reducētājs atdod elektronus un pats oksidējas.",
  "Uzrakstiet pusreakciju: ja elektroni ir kreisajā pusē, tā ir reducēšanās.", "avots", 12)

m("M15", "Uzskatīt redoksreakciju par piekto veidu blakus četriem",
  "Mācību grāmatā redoks ir atsevišķa rinda, tāpēc šķiet, ka tas ir piektais veids.",
  "Redoks ir otrs klasifikācijas aspekts: aizvietošana vienmēr ir redoks, apmaiņa parasti nav, savienošanās un sadalīšanās dažreiz.",
  "Pārbaudiet oksidēšanas pakāpju izmaiņas; ja tādu nav, reakcija nav redoks.", "papildinājums", 11)

m("M16", "Rakstīt apmaiņas reakciju, kurā neveidojas ne nogulsnes, ne gāze, ne vājš elektrolīts",
  "Formulas „apmainās” uz papīra, tāpēc šķiet, ka reakcija notiek.",
  "Ja visi joni paliek šķīdumā, ķīmiski nekas nav mainījies; vienādojums ir tikai jonu saraksts.",
  "Pārbaudiet trīs pazīmes: nogulsnes, gāze, vājš elektrolīts (ūdens, skābe, komplekss).", "avots", 11)

m("M17", "Saīsinātajos jonu vienādojumos sadalīt nešķīstošus sāļus, vājus elektrolītus, gāzes un ūdeni",
  "Visas formulas izskatās vienādi, tāpēc gribas sadalīt visu.",
  "Sadalīt drīkst tikai stiprus elektrolītus šķīdumā. Nogulsnes, gāzes, ūdens un vājās skābes raksta molekulāri.",
  "Pārbaudiet lādiņu summu abās pusēs un to, vai katrs jons tiešām ir brīvs.", "avots", 11)

m("M18", "Lasīt šķīdības tabulu kā „šķīst / nešķīst” bez temperatūras un bez „maz šķīst”",
  "Tabulā ir tikai burti, un tos gribas nolasīt kā jā/nē.",
  "Tabula attiecas uz 20 °C, un tajā ir arī „mazšķīstošs” un „reaģē ar ūdeni”.",
  "Pirms atbildes pasakiet temperatūru un to, vai „mazšķīstošs” ir pietiekami nogulsnēm.", "avots", 5)

m("M19", "Uzskatīt pH 7 par neitrālu jebkurā temperatūrā; atšķaidīt skābi „aiz” pH 7",
  "Skolā pH 7 ir neitrāls, un atšķaidīšana „virza uz neitrālu”.",
  "Neitrāls pH ir ½pK<sub>w</sub>: 7,00 pie 25 °C, 6,81 pie 37 °C. Skābes atšķaidīšana tuvinās neitrālajam pH, bet nepārsniedz to. 37 °C vērtība nav nolasīta no primārās līdzsvara tabulas. <span class=\"tag\">[UNVERIFIED]</span> C-07.",
  "Aprēķiniet pH no koncentrācijas un pārbaudiet robežu: bezgalīga atšķaidīšana dod neitrālu ūdeni.", "papildinājums", 8)

m("M20", "Saukt asins pH 7,4 par neitrālu",
  "7,4 ir tuvu 7, un asinis „šķiet neitrālas”.",
  "7,4 ir vāji sārmains; neitrāls pie 37 °C ir ≈ 6,8. Arī šis 6,8 nav nolasīts no primārās tabulas. <span class=\"tag\">[UNVERIFIED]</span> C-07.",
  "Salīdziniet ar ½pK<sub>w</sub> pie ķermeņa temperatūras, nevis ar 7.", "avots", 8)

m("M21", "Jaukt piesātinātu ar koncentrētu; uzskatīt pārsātinātu par stabilu",
  "„Piesātināts” skan kā „pilns”, un pilns šķiet stiprs.",
  "Piesātināts nozīmē līdzsvaru ar neizšķīdušo vielu; koncentrēts nozīmē daudz vielas. Pārsātināts ir nestabils.",
  "Ja šķīdumā ir nogulsnes, tas ir piesātināts; ja nav, tas var būt pārsātināts.", "avots", 5)

m("M22", "Uzskatīt, ka atšķaidīšana padara elektrolītu stiprāku, jo α pieaug",
  "α tiešām pieaug, un šķiet, ka viela kļūst „stiprāka”.",
  "Atšķaidot α pieaug, bet jonu koncentrācija krīt; elektrolīta stiprumu nosaka vielas raksturs.",
  "Skaitiet jonus tilpumā, nevis tikai disociācijas pakāpi.", "avots", 7)

m("M23", "Uzskatīt, ka NaCl hidrolizējas, un ka „vāja skābe + vāja bāze ⇒ pH 7”",
  "Sāls no stipras skābes un stipras bāzes šķiet „neitrāls”, tāpēc tam gribas pieskaitīt hidrolīzi.",
  "Stipras skābes un stipras bāzes sāls nehidrolizējas. Vājas skābes un vājas bāzes sāls pH nosaka tas, kurš ir stiprāks.",
  "Nosakiet sāli veidojošo skābi un bāzi un to stiprumu; tikai tad lemjiet par pH.", "avots", 9)

m("M24", "Lietot nesabalansēta vienādojuma attiecības; lietot 22,4 L/mol šķidrumiem, cietām vielām vai citiem apstākļiem",
  "22,4 L/mol ir vienīgais gāzes tilpums, ko atceras.",
  "Vispirms sabalansējiet vienādojumu; 22,4 L/mol attiecas tikai uz gāzi 0 °C un 101,325 kPa.",
  "Uzrakstiet apstākļus blakus tilpumam; ja tie nav doti, pieņemiet un pasakiet to.", "avots", 13)

m("M25", "Neitralizēt ar vienādiem molu skaitļiem, nevis vienādiem H⁺ un OH⁻ moliem",
  "„Skābe + bāze 1:1” ir vienkāršs noteikums, kas der HCl un NaOH.",
  "H₂SO₄ dod divus H⁺, H₃PO₄ trīs; attiecība jāņem no vienādojuma.",
  "Līdzsvarojiet vienādojumu un skaitiet H⁺ un OH⁻, nevis formulas.", "avots", 13)

m("M26", "Jaukt mL un L, mmol un µmol, g un mg vienā rindā",
  "Skaitļi izskatās mazi, un vienības šķiet saprotamas.",
  "Pirms dalīšanas pārvērš visu vienā sistēmā: moli un litri.",
  "Uzrakstiet vienību pie katra skaitļa un pārbaudiet, vai tās saīsinās.", "avots", 6)

m("M27", "Uzskatīt, ka jebkurš metāls ar skābi dod H₂, un ka Fe ar HCl dod Fe³⁺",
  "„Metāls + skābe → ūdeņradis” ir pazīstama shēma.",
  "H₂ izdala metāli, kas aktivitātes rindā ir pirms ūdeņraža. Fe ar HCl dod Fe²⁺, nevis Fe³⁺.",
  "Pārbaudiet metāla vietu rindā un to, kuru jonu tas šajā reakcijā veido.", "avots", 10)

m("M28", "Kļūdīties sāļu formulās: lādiņu bilance, sulfāts/sulfīts, nitrāts/nitrīts, Fe(II)/Fe(III)",
  "Indeksi šķiet kosmētiski, un „sulfāts” skan līdzīgi „sulfītam”.",
  "Formula ir lādiņu bilance: Fe³⁺ + 3 Cl⁻ = FeCl₃; SO₄²⁻ nav SO₃²⁻; NO₃⁻ nav NO₂⁻.",
  "Saskaitiet lādiņus: pozitīvo summa = negatīvo summa.", "avots", 10)

m("M29", "Jaukt A, A<sub>r</sub> un M; „tritija dabā nav”",
  "Visi trīs apzīmē „atommasu”, un avots lieto vienu burtu.",
  "<i>A</i> ir masas skaitlis (nuklonu skaits), <i>A</i><sub>r</sub> relatīvā atommasa, <i>M</i> molmasa g/mol.",
  "Uzrakstiet, ko meklējat: skaitli, attiecību vai masu uz molu.", "avots", 2)

m("M30", "Aizpildīt 3d pirms 4s; uzskatīt, ka grupas numurs vienmēr dod valences elektronus",
  "Grupas numurs der A grupām, tāpēc šķiet, ka der visām.",
  "4s aizpildās pirms 3d (4s ir zemāka enerģija). d-bloka elementiem valences elektroni ir arī iekšējā līmenī.",
  "Lietojiet aizpildīšanās shēmu un skaitiet pēc tās, nevis pēc grupas numura.", "avots", 2)

m("M31", "Uzskatīt, ka 5 % glikoze paliek izotoniska arī organismā",
  "Uz etiķetes ir „izotonisks”, un šķīdums tiešām ir izotonisks ar asinīm.",
  "Glikoze tiek metabolizēta, tāpēc pēc laika šķīdums kļūst hipotonisks attiecībā pret šūnām; tāpēc to lieto arī kā šķīdinātāju.",
  "Izotoniskums ir brīdis, nevis nemainīga īpašība.", "papildinājums", 14)

m("M32", "Uzskatīt, ka visi bārija sāļi ir indīgi",
  "Bārija jons ir indīgs, un „bārija sāls” skan vienādi.",
  "BaSO₄ praktiski nešķīst, tāpēc bārija joni neuzsūcas un to lieto kā kontrastvielu. Šķīstošie Ba²⁺ sāļi ir indīgi.",
  "Pirms bīstamības sprieduma pārbaudiet šķīdību.", "papildinājums", 14)

m("M33", "Sajaukt šķīdību ar koncentrāciju: no „ap 88 g/100 g ūdens” uzrakstīt 0,88 mol/L",
  "Abi skaitļi saka „cik daudz izšķīdis”, un avots tos lieto blakus vienā nodaļā.",
  "Šķīdība ir masas attiecība pret šķīdinātāju pie noteiktas temperatūras (g/100 g H₂O); koncentrācija ir daudzums pret šķīduma tilpumu (mol/L). Lai no vienas iegūtu otru, vajag ρ un temperatūru.",
  "Uzrakstiet pamatu un mērvienību: g/100 g ūdens nav mol/L; pārbaudiet, vai dots tilpums vai masa.", "papildinājums", 5)


# ------------------------------------------------- F04 mistake→repair route
# Remediation data for the diagnostic route (section #mistake-route in the
# appendix). Kept beside the seeds so the route can never drift from them.
#   concept          definitions.py registry key (grouping + concept anchor)
#   repair_action    one-sentence cognitive heuristic (the added "action")
#   follow_up_prompt one diagnostic probe the learner answers to self-check
#   follow_up_answer short model answer revealed in a native <details>
# repair_anchor (#mNN, the inline mistake card) is derived, not stored, so it
# always matches the card the build emits. Every value is distinct: two seeds
# must never share a heuristic or a probe (mistake_route() enforces this).
ROUTE = {
  "M01": {"concept": "mass_conservation",
    "repair_action": "Sabalansējot mainiet tikai koeficientu formulas priekšā; indekss apzīmē vielas sastāvu un ir nemainīgs kā formulas „vārds”.",
    "follow_up_prompt": "Ja neizdodas izlīdzināt skābekli, kāpēc nedrīkst vienkārši mainīt indeksu pie O uz O₂?",
    "follow_up_answer": "Indeksa maiņa pārveido vielu citā vielā; bilanci vienmēr atrisina koeficients, kas maina atomu skaitu, nemainot formulu."},
  "M02": {"concept": "molekula",
    "repair_action": "Pirms vārda „molekula” pārbaudiet, vai tas ir metāls + nemetāls: jonu režģī nav molekulu, tikai formulvienības.",
    "follow_up_prompt": "Kāpēc NaCl ūdens šķīdumā pareizāk runāt par formulvienību, nevis molekulu?",
    "follow_up_answer": "NaCl ir jonu kristāls, kurā Na⁺ un Cl⁻ turas elektrostatiski; atsevišķas „NaCl molekulas” nepastāv."},
  "M03": {"concept": "disociacija",
    "repair_action": "Uzrakstiet disociācijas vienādojumu un saskaitiet katjonus ar anjoniem atsevišķi; indekss ārpus iekavām reizina visu grupu.",
    "follow_up_prompt": "Cik jonu dod viena Al₂(SO₄)₃ formulvienība un kā to ātri pārbaudīt?",
    "follow_up_answer": "2 Al³⁺ + 3 SO₄²⁻ = 5 joni; pārbaude: lādiņu summa 2·(+3) + 3·(−2) = 0."},
  "M04": {"concept": "stehiometrija",
    "repair_action": "Vienmēr pārvērtiet masas molos un daliet ar koeficientu; vielas reaģē molu attiecībā, ne gramu.",
    "follow_up_prompt": "Kāpēc „9 g pret 9 g” nenozīmē, ka reaģentu ir vienādi?",
    "follow_up_answer": "Mola masas atšķiras, tāpēc vielas daudzums ir citāds; ierobežojošo nosaka mazākā n/koeficients attiecība."},
  "M05": {"concept": "molārā koncentrācija c",
    "repair_action": "Koncentrācijai vajag šķīduma tilpumu; ja dota masa, vispirms V = m / ρ, tad c = n / V.",
    "follow_up_prompt": "Kādā secībā pāriet no „48 g šķīduma” pie molārās koncentrācijas?",
    "follow_up_answer": "48 g → V = m/ρ litros → n = m/M → c = n/V; c formulā iet tilpums, ne masa."},
  "M06": {"concept": "skābais / bāziskais sāls",
    "repair_action": "„Skābais sāls” apraksta sastāvu (ir aizvietojams H); par vidi lemj hidrolīze, tāpēc NaHCO₃ tomēr ir bāzisks.",
    "follow_up_prompt": "Kāpēc NaHCO₃, nesauktots par skābo sāli, ūdenī dod bāzisku vidi?",
    "follow_up_answer": "HCO₃⁻ vairāk pieņem protonu, nekā atdod, tāpēc paliek OH⁻ un pH ≈ 8,3."},
  "M07": {"concept": "amfotērs",
    "repair_action": "Ja nogulsne pazūd, pievienojot NaOH pārākumu, domājiet par amfotēru hidroksīdu un kompleksu.",
    "follow_up_prompt": "Kā vienā eksperimentā atšķirt „nešķīstošu bāzi” no amfotēra hidroksīda?",
    "follow_up_answer": "Pievienojot sārmu pārākumu: Al(OH)₃ un Zn(OH)₂ šķīst atkārtoti (komplekss), patiess nešķīstams paliek nogulsnē."},
  "M08": {"concept": "elektrolits",
    "repair_action": "Elektrolīts vada jonu dēļ šķīdumā vai kausējumā; metāls vada ar elektroniem, tāpēc Cu nav elektrolīts.",
    "follow_up_prompt": "Kāpēc varš vada strāvu, tomēr nav elektrolīts?",
    "follow_up_answer": "Strāvu nes brīvi elektroni, ne joni; elektrolītam šķīdinātājā jārada brīvi joni."},
  "M09": {"concept": "elektrolits",
    "repair_action": "Turiet trīs lielumus atsevišķi: stiprums = disociācijas pilnība, šķīdība = cik izšķīst, koncentrācija = cik ir šķīdumā.",
    "follow_up_prompt": "Vai atšķaidīta HCl ir stiprs elektrolīts? Pamatojiet ar trim lielumiem.",
    "follow_up_answer": "Jā: stiprums (α ≈ 1) ir vielas īpašība; koncentrācija ir zema, bet tas stiprumu nemaina."},
  "M10": {"concept": "polārā / nepolārā saite",
    "repair_action": "Saites polaritāte nav molekulas polaritāte; uzzīmējiet molekulu un pārbaudiet, vai dipolu summa ir nulle.",
    "follow_up_prompt": "Kāpēc CO₂ ar polārām C=O saitēm ir nepolāra molekula?",
    "follow_up_answer": "Lineārā O=C=O ģeometrijā divi dipoli ir pretējos virzienos un summā dod 0."},
  "M11": {"concept": "jonu_saite",
    "repair_action": "Saite ir nepārtraukta pāreja; aprēķiniet ΔREN, ierakstiet to un nosauciet lietoto kritēriju.",
    "follow_up_prompt": "Kāpēc „metāls + nemetāls = jonu saite” nav droši noteikums?",
    "follow_up_answer": "Robeža ir vienošanās, ne slēdzis; daži savienojumi to pārsniedz, tāpēc atbildē jānorāda ΔREN un kritērijs."},
  "M12": {"concept": "ūdeņraža saite",
    "repair_action": "Ūdeņraža saitei vajag donoru H–F/O/N un akceptora vientuļo pāri; tā iet starp molekulām, ne iekšpusē.",
    "follow_up_prompt": "Kāpēc CH₄ neveido ūdeņraža saites, neskaitot uz saviem ūdeņraža atomiem?",
    "follow_up_answer": "C–H saite ir gandrīz nepolāra, tāpēc H nav pietiekami δ+; trūkst arī F/O/N akceptora ar vientuļo pāri."},
  "M13": {"concept": "oksidēšanas pakāpe",
    "repair_action": "Oksidēšanas pakāpe ir atomam, lādiņš — veselai daļiņai; summējiet pakāpes līdz nulij un pārbaudiet izņēmumus.",
    "follow_up_prompt": "Kā atšķirt oksidēšanas pakāpi no jona lādiņa Fe³⁺ piemērā?",
    "follow_up_answer": "Fe³⁺ lādiņš +3 attiecas uz veselu jonu; oksidēšanas pakāpe +3 (III) apzīmē Fe atomu savienojumā."},
  "M14": {"concept": "oksidētājs",
    "repair_action": "Oksidētājs pievieno elektronus un pats reducējas; reducētājs atdod elektronus un pats oksidējas.",
    "follow_up_prompt": "Reakcijā 2Fe³⁺ + 2I⁻ → 2Fe²⁺ + I₂ kurš ir oksidētājs un kā to pārbaudīt?",
    "follow_up_answer": "Fe³⁺ pievieno e⁻ → Fe²⁺ (reducējas), tāpēc ir oksidētājs; pusreakcijā elektroni kreisajā pusē = reducēšanās."},
  "M15": {"concept": "redoks",
    "repair_action": "Redoks ir otrs klasifikācijas aspekts, ne piektais veids; pārbaudiet oksidēšanas pakāpju izmaiņas.",
    "follow_up_prompt": "Kāpēc aizvietošana vienmēr ir redoks, bet apmaiņa parasti nav?",
    "follow_up_answer": "Aizvietošanā vienkāršās vielas elements maina pakāpi (0 → jonam); apmaiņā joni tikai pārkārtojas, pakāpes saglabājas."},
  "M16": {"concept": "apmaina",
    "repair_action": "Apmaiņa notiek tikai, ja veidojas nogulsne, gāze vai vājš elektrolīts; citādi joni paliek šķīdumā.",
    "follow_up_prompt": "Kāpēc NaCl + KNO₃ „reaģē” uz papīra, bet šķīdumā nekas nenotiek?",
    "follow_up_answer": "Visi joni paliek brīvi šķīdumā; bez nogulsnes, gāzes vai vāja elektrolīta nav dzinējspēka."},
  "M17": {"concept": "jonu_vienadojumi",
    "repair_action": "Pilnajā jonu vienādojumā sadaliet tikai stipros elektrolītus; nogulsnes, gāzes, ūdeni un vājās skābes rakstiet molekulāri.",
    "follow_up_prompt": "Kāpēc saīsinātajā vienādojumā H⁺ + OH⁻ → H₂O nesvītro ūdeni?",
    "follow_up_answer": "Ūdens ir produkts un vājš elektrolīts; stipros elektrolītus svītro, bet ūdeni atstāj molekulāri."},
  "M18": {"concept": "skid_tabula",
    "repair_action": "Šķīdības tabula attiecas uz 20 °C un atšķir „mazšķīstošu” un „reaģē ar ūdeni”; nenolasiet to kā jā/nē.",
    "follow_up_prompt": "Kāpēc „M” tabulā nenozīmē pilnīgu nešķīdību?",
    "follow_up_answer": "„Mazšķīstošs” joprojām daļēji šķīst; nogulsnei pietiek, ka koncentrācija sasniedz šķīdības robežu."},
  "M19": {"concept": "pH",
    "repair_action": "Neitrāls pH ir ½pK<sub>w</sub> pie dotās temperatūras (7,00 pie 25 °C); atšķaidīšana tuvinās, bet nepārsniedz neitrālo.",
    "follow_up_prompt": "Kāpēc skābi nevar „atšķaidīt aiz” pH 7?",
    "follow_up_answer": "Bezgalīgi atšķaidot, pH tuvojas neitrālajam ūdenim no skābas puses, bet to nepārsniedz."},
  "M20": {"concept": "pH",
    "repair_action": "7,4 ir vāji sārmains; salīdziniet ar ½pK<sub>w</sub> pie 37\u00a0°C (≈\u00a06,8), nevis ar 7. Arī 6,8 nav nolasīts no primārās tabulas. <span class=\"tag\">[UNVERIFIED]</span> C-07.",
    "follow_up_prompt": "Kāpēc asins pH 7,4 ir sārmains, lai gan tuvu 7?",
    "follow_up_answer": "„7” ir neitrāls tikai 25\u00a0°C; pie 37\u00a0°C neitrāls ir ≈\u00a06,8, tāpēc 7,4 ir virs tā — sārmains. 37\u00a0°C vērtība nav nolasīta no primārās tabulas. <span class=\"tag\">[UNVERIFIED]</span> C-07."},
  "M21": {"concept": "piesātināts / nepiesātināts / pārsātināts",
    "repair_action": "Piesātināts = līdzsvars ar neizšķīdušo vielu; koncentrēts = daudz vielas; pārsātināts ir nestabils.",
    "follow_up_prompt": "Kā atpazīt pārsātinātu šķīdumu un kāpēc tas nestabili?",
    "follow_up_answer": "Tas satur vairāk vielas, nekā līdzsvars ļauj, bez nogulsnēm; traucēšana izsauc kristalizāciju."},
  "M22": {"concept": "disociācijas pakāpe α",
    "repair_action": "Atšķaidot α pieaug, bet jonu koncentrācija krīt; stiprumu nosaka K<sub>a</sub>, ne α.",
    "follow_up_prompt": "Kāpēc etiķskābe, atšķaidot, nekļūst stiprāka, neskaitot, ka α pieaug?",
    "follow_up_answer": "α pieaug, bet tilpums aug ātrāk, tāpēc [H⁺] krīt; stiprums = K<sub>a</sub> paliek nemainīgs."},
  "M23": {"concept": "hidrolīze",
    "repair_action": "Hidrolīze prasa jonu no vājas skābes vai bāzes; stipra skābe + stipra bāze (NaCl) nehidrolizējas.",
    "follow_up_prompt": "Kāpēc NaCl šķīdums ir neitrāls, bet Na₂CO₃ bāzisks?",
    "follow_up_answer": "Na⁺ un Cl⁻ nereaģē ar ūdeni (stipri); CO₃²⁻ no vājas skābes hidrolizējas, atstājot OH⁻."},
  "M24": {"concept": "stehiometrija",
    "repair_action": "Vispirms sabalansējiet; 22,414 L/mol der tikai gāzei pie 0 °C un 101,325 kPa.",
    "follow_up_prompt": "Kāpēc 22,4 L/mol nedrīkst lietot šķidrumam vai citā temperatūrā?",
    "follow_up_answer": "Izbaudījums ir tikai ideālai gāzei normālos apstākļos; citādi V = nRT/p mainās."},
  "M25": {"concept": "neitralizācija",
    "repair_action": "Neitralizācija līdzsvaro H⁺ un OH⁻ molus; H₂SO₄ dod divus, H₃PO₄ trīs — attiecība nāk no vienādojuma.",
    "follow_up_prompt": "Cik mol NaOH vajag 1 mol H₂SO₄ un kāpēc ne 1:1?",
    "follow_up_answer": "2 mol: H₂SO₄ atdod 2 H⁺, katram savs OH⁻; skaitiet protonus, ne formulas."},
  "M26": {"concept": "molārā koncentrācija c",
    "repair_action": "Pirms dalīšanas pārvērtiet visu vienā sistēmā — molos un litros; uzrakstiet vienību pie katra skaitļa.",
    "follow_up_prompt": "Kāpēc „9 g uz litru” jāpārvērš molos pirms mmol/L aprēķina?",
    "follow_up_answer": "9 g/L ÷ 58,44 g/mol = 0,154 mol/L = 154 mmol/L; vienībām jāsaīsinās, ne jājauj."},
  "M27": {"concept": "aktivitātes rinda",
    "repair_action": "H₂ izdala tikai metāli pirms ūdeņraža aktivitātes rindā; Fe ar HCl dod Fe²⁺, ne Fe³⁺.",
    "follow_up_prompt": "Kāpēc Fe ar HCl dod Fe²⁺, bet ne Fe³⁺, un kurš metāls vispār neizdala H₂?",
    "follow_up_answer": "HCl nav pietiekami stiprs oksidētājs līdz Fe³⁺; metāli aiz ūdeņraža (Cu, Ag) H₂ neizdala."},
  "M28": {"concept": "sals",
    "repair_action": "Formula ir lādiņu bilance; uzzīmējiet katjona un aniona lādiņus un pārbaudiet, vai summa ir 0.",
    "follow_up_prompt": "Kā ātri pārbaudīt, ka dzelzs(III) sulfāta formula ir Fe₂(SO₄)₃?",
    "follow_up_answer": "2·(+3) + 3·(−2) = 0; sulfāts ir SO₄²⁻ (ne sulfīts SO₃²⁻), dēļ trīs anioni."},
  "M29": {"concept": "molmasa",
    "repair_action": "A = masas skaitlis (nukloni), A<sub>r</sub> = relatīvā atommasa (bez vienības), M = molmasa g/mol.",
    "follow_up_prompt": "Kāpēc ¹²C ir A = 12, A<sub>r</sub> = 12 un M = 12 g/mol, bet tas nav viens lielums?",
    "follow_up_answer": "Skaitlis sakrīt, bet nozīme un mērvienība atšķiras: skaitlis, attiecība un masa uz molu."},
  "M30": {"concept": "per_tabula",
    "repair_action": "Lietojiet aizpildīšanās shēmu: 4s aizpildās pirms 3d; grupas numurs nedod valences elektronus d-blokam.",
    "follow_up_prompt": "Kāpēc 4s aizpildās pirms 3d, neskaitot uz lielāku n?",
    "follow_up_answer": "4s orbitāle ir zemākas enerģijas nekā 3d (n+l likums); secību rāda shēma, ne grupas numurs."},
  "M31": {"concept": "izotonisks šķīdums",
    "repair_action": "Izotoniskums ir brīža stāvoklis; glikoze metabolizējas, tāpēc šķīdums laika gaitā kļūst hipotonisks.",
    "follow_up_prompt": "Kāpēc 5 % glikoze ilgā laikā šūnām tomēr kļūst hipotoniska?",
    "follow_up_answer": "Glikoze uzsūcas un oksidējas, šķīdināto daļiņu koncentrācija krīt un ūdens ieplūst šūnās."},
  "M32": {"concept": "šķīdība",
    "repair_action": "Bīstamību nosaka šķīdība: BaSO₄ praktiski nešķīst, tāpēc Ba²⁺ neuzsūkas; šķīstošie Ba²⁺ sāļi ir indīgi.",
    "follow_up_prompt": "Kāpēc BaSO₄ droši lieto kā kontrastvielu, neskaitot uz Ba²⁺ indīgumu?",
    "follow_up_answer": "BaSO₄ tabulā ir N; brīvi Ba²⁺ joni nepārvar membrānu, tāpēc tos neuzsūcas."},
  "M33": {"concept": "šķīdība",
    "repair_action": "Pirms skaitļa uzraksti pamatu un mērvienību: g/100 g šķīdinātāja pie temperatūras ir šķīdība, mol/L šķīdumā ir koncentrācija; starp tām vajag ρ.",
    "follow_up_prompt": "Kāpēc no „ap 88 g NaNO₃ uz 100 g ūdens 20 °C” nevar tieši uzrakstīt 0,88 mol/L?",
    "follow_up_answer": "88 g ir masa uz 100 g šķīdinātāja, nevis daudzums uz litru; mol/L vajag šķīduma tilpumu, proti, blīvumu ρ, kuru avots nedod."},
}


def mistake_route():
    """F04: mistake→repair records for the diagnostic route.

    Merges the seeds with ROUTE and derives repair_anchor (#mNN — the inline
    mistake card, a distinct and always-valid in-chapter explanation). Fails
    the build if any seed lacks route data or if two seeds share a
    repair_action / follow_up_prompt (no generic answer for every error).
    """
    missing = sorted(set(M) - set(ROUTE), key=lambda x: int(x[1:]))
    if missing:
        raise SystemExit("ledger mistake_route: no route data for " + ", ".join(missing))
    out = {}
    for mid in M:
        r = ROUTE[mid]
        out[mid] = {
            "wrong": M[mid]["wrong"], "tag": M[mid]["tag"], "ch": M[mid]["ch"],
            "concept": r["concept"],
            "repair_anchor": f"#m{mid[1:]}",
            "repair_action": r["repair_action"],
            "follow_up_prompt": r["follow_up_prompt"],
            "follow_up_answer": r["follow_up_answer"],
        }
    for field in ("repair_action", "follow_up_prompt"):
        seen = {}
        for mid in sorted(out, key=lambda x: int(x[1:])):
            key = out[mid][field].casefold()
            if key in seen:
                raise SystemExit(
                    f"ledger mistake_route: {field} shared by {seen[key]} and {mid}")
            seen[key] = mid
    return out


def validate_mistake_route(html):
    """F04 read-only gate: the built master resolves all 32 M-ids both ways.

    For every seed the route card (#mr-MNN) must link forward to the inline
    mistake card (#mNN), and that card must link back to the route card.
    Returns a list of problems (empty when the wiring is complete).
    """
    problems = []
    if html.count('id="mistake-route"') != 1:
        problems.append("mistake-route: want exactly one #mistake-route section")
    for mid in sorted(M, key=lambda x: int(x[1:])):
        nn = mid[1:]
        card, route = f"m{nn}", f"mr-{mid}"
        if f'id="{card}"' not in html:
            problems.append(f"{mid}: inline mistake card #{card} missing")
            continue
        if f'id="{route}"' not in html:
            problems.append(f"{mid}: route card #{route} missing")
            continue
        rc = re.search(rf'id="{route}"[^>]*>(.*?)</li>', html, re.S)
        if not rc or f'href="#{card}"' not in rc.group(1):
            problems.append(f"{mid}: route card {route} does not link to #{card}")
        mc = re.search(rf'id="{card}"[^>]*>(.*?)</section>', html, re.S)
        if not mc or f'href="#{route}"' not in mc.group(1):
            problems.append(f"{mid}: mistake card #{card} does not link back to #{route}")
    return problems
