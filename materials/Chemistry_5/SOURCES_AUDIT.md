# SOURCES_AUDIT.md — zinātniskā audita grāmata (N06, 2. kārta)

Datums: 2026-11-02. Uzdevums: pārbaudīt katru reģistra labojumu pret nosauktu, citējamu avotu.

Līmeņi:
- **[G]** — IUPAC Gold Book definīcija nolasīta burtiski (XML ogles spogulis, doi 10.1351/goldbook.…).
- **[V]** — raksts/raksts citāts pārbaudīts tiešsaistē šajā sesijā (atvērta pieeja; lasīts vai citāts pārbaudīts).
- **[B]** — grāmata nosaukta ar izdevumu, bet sadaļa/lapa **nav atvērta**; HTML nekad nedod lapu.
- **[N]** — ārējs avots nav vajadzīgs (aritmētika, ortogrāfija, iekšēja konsekvence, avota iekšēja pretruna).

Noteikums: HTML nekad necitē lapu, kura nav personīgi apskatīta. Grāmatām tiek dots izdevums un tēma, nevis lapa.

## 1. Šajā sesijā tiešsaistē lasītās autoritātes

| Avots | Kas apstiprināts |
|---|---|
| IUPAC Gold Book O04322 (order of reaction) | Pakāpe no empīriska diferenciālā ātruma likuma; eksponenti “pozitīvi vai negatīvi veseli vai racionāli neveseli skaitļi”. |
| IUPAC Gold Book M03989 (molecularity) | Molekularitāte = reaģējošo molekulāro vienību skaits elementārreakcijas “mikroskopiskajā notikumā”. |
| IUPAC Gold Book E02035 (elementary reaction) | Elementārreakcija notiek vienā solī, caur vienu pārejas stāvokli. |
| IUPAC Gold Book R05156 (rate of reaction) | v = −(1/a)d[A]/dt = −(1/b)d[B]/dt…; laika vienība — sekunde. |
| IUPAC Gold Book C00876 (catalyst) | “increases the rate of a reaction without modifying the overall standard Gibbs energy change”. |
| IUPAC Gold Book H02716 (half life) | Pusperiodam “nozīme ir tikai īpašos gadījumos”; pirmais minētais — pirmā pakāpe. |
| IUPAC Gold Book A00092 (activated complex) | ‡ komplekss ir atomu kopa pie potenciālās enerģijas virsmas sērkociņa punkta. |
| IUPAC Gold Book A00446 (Arrhenius equation) | k = A·e^(−Ea/RT); Ea un A tiek uzskatīti par temperatūrai neatkarīgiem. |
| IUPAC Gold Book O04365 (oxidation state) | Oksidēšanas pakāpe ir elektronu skaitīšanas lielums (jonu aproksimācija). |
| Johnson & Goody 2011, Biochemistry 50(39), 8264.–8269. lpp. (PMC3381512) | M&M 1913 lietoja ātrā līdzsvara pieņēmumu (K_S = disociācijas konstante); viņu izvestā konstante bija V/K_S; stacionāro tuvinājumu ieviesa Briggs & Haldane 1925; K_M nosaukums, iespējams, nāk no B&H atsauces uz “Michaelis and Menten's constant”. |
| Briggs & Haldane 1925, Biochem. J. 19(2), 338.–339. lpp. (PubMed 16743508) | Citāts pārbaudīts: “A Note on the Kinetics of Enzyme Action”. |
| Miłek 2018, Braz. J. Chem. Eng. 35(3), doi:10.1590/0104-6632.20180353s20160617 | Katalāze (Aspergillus niger, EC 1.11.1.6; 20–50 °C, pH 6,9; 0,015 M H₂O₂): Ea = 12,9 ± 0,7 kJ·mol⁻¹; deaktivācija 158,7 ± 1,7 kJ·mol⁻¹; tajā citēti Altomare 1974 (19,7 kJ·mol⁻¹) un Hooda 2014 (23,5 kJ·mol⁻¹). |
| Koshland 1958, PNAS 44(2), 98.–104. lpp. (PMC335371) | Citāts pārbaudīts (“Application of a Theory of Enzyme Specificity to Protein Synthesis”); raksta pamatteksts tiešsaistē nav brīvi lasāms, tāpēc burtiski citāti netiek doti. |

## 2. Reģistra rindas (12. tabula) — autoritāte un statuss

| ID | Sev. | Labojuma būtība (Pareizi kolonna) | Autoritāte | Līmenis | Statuss |
|---|---|---|---|---|---|
| K1 |  | Vidējais ΔC/Δt; momentānais −(1/ν)dC/dt | IUPAC Gold Book O04322 (order of reaction) un R05156 (rate of reaction): pakāpe nāk no empīriska ātruma likuma; v definēta ar koeficientiem. | G | confirmed |
| K2 |  | Koeficienti = eksponenti tikai elementārstadijā | IUPAC Gold Book O04322 un E02035 (elementary reaction): eksponenti ir empīriska likuma lielums; elementārreakcija notiek vienā solī. | G | confirmed |
| K3 |  | Ea ir barjera; aktīva ir daļa virs barjeras | Atkins, Physical Chemistry (sadaļa par aktivācijas barjeru) — nav atvērta. | B | confirmed (grāmata pārbaudāma) |
| K4 |  | Nav automātiska; jonu reakcija var būt lēna | Laidler, Chemical Kinetics (jonu reakciju ātrumi) — nav atvērta; atbalsta arī šī dokumenta 12. nodaļas MnO₄⁻ piemērs. | B | confirmed (grāmata pārbaudāma) |
| K5 |  | Attēli pārzīmēti un numurēti no 1 | Iekšēja konsekvence: attēlu numerācija; grāmata nav vajadzīga. | N | confirmed (nav grāmatas jautājums) |
| K6 |  | Daļa virs Ea ≈ e−Ea/RT | IUPAC Gold Book A00446 (Arrhenius equation): k = A·e^(−Ea/RT); daļa virs barjeras seko eksponentam. Atkins — pārbaudāma. | G | confirmed |
| K7 |  | Sadalījumam ir maksimums un gara aste; kopējais laukums nemainās | Atkins, Physical Chemistry (Maksvela–Bolcmaņa sadalījuma forma) — nav atvērta; dokumenta 4. nodaļa rāda formu ar aprēķinu. | B | confirmed (grāmata pārbaudāma) |
| K8 |  | Vienība atkarīga no pakāpes | IUPAC Gold Book O04322: k definēts ātruma likumā, tāpēc vienība seko no pakāpēm. | G | confirmed |
| K9 |  | Bezdimensiju daļa, parasti ≪1; 1 nav pamatots | Laidler, Chemical Kinetics (steriskais faktors) — nav atvērta. | B | viens avots (mīkstināts HTML) |
| K10 |  | Nav apstiprināts: iespējama vienības kļūda (23 J → 23 kJ); avota skaitlis paliek 23 J/mol | Kursa avots: Kinetika p.6, 5. tabula, sleja “Ea, J/mol”; katalāzei iespiests 23, bez katalizatora 79 000. Miłek 2018, Braz. J. Chem. Eng. 35(3), doi:10.1590/0104-6632.20180353s20160617 (atvērta pieeja, lasīta): katalāzei (Aspergillus niger, 20–50 °C, pH 6,9, 0,015 M H₂O₂) Ea = 12,9 ± 0,7 kJ·mol⁻¹; tajā citēti Altomare 1974 (19,7) un Hooda 2014 (23,5). Vencipara vērtība literatūrā nav atrasta. | V | open — atvērta 2026-11-08: literatūras vērtības ir konteksts, nevis kursa vērtība; jāapstiprina docētājai |
| K11 |  | Pakāpe var būt 0, daļskaitlis, negatīva; ierobežota ir molekularitāte | IUPAC Gold Book O04322: eksponenti var būt 'pozitīvi vai negatīvi veseli vai racionāli neveseli skaitļi'. | G | confirmed |
| K12 |  | Nulles pakāpe rodas no piesātinājuma, nevis no vienas molekulas | Atkins, Physical Chemistry (nulles pakāpe = piesātinājums) — nav atvērta. | B | confirmed (grāmata pārbaudāma) |
| K13 |  | Abi ir sastopami; lieto “pakāpe”, pirmajā reizē “kārta” iekavās | Lietojuma izvēle (abas formas avotā); AkadTerm jau fiksēts N01. | N | confirmed (nav grāmatas jautājums) |
| K14 |  | t½ konstants tikai pirmajai pakāpei; plaši lietots medicīnā | IUPAC Gold Book H02716 (half life): 'The half life of a reaction has meaning only in special cases: For a first-order reaction…'. | G | confirmed |
| K15 |  | 2,9¹⁰ ≈ 42 070,7 ≈ 4,2·10⁴ | Aritmētika: 2,9¹⁰ = 42 070,7233…; pārrēķināts neatkarīgi (numbers.json + bc). | N | confirmed (nav grāmatas jautājums) |
| K16 |  | Aptuvens noteikums pie istabas T un mērenas Ea | IUPAC Gold Book A00446: Ea un A Arrēniusa vienādojumā; γ = exp(10·Ea/RT²) seko no tās. Atkins — pārbaudāma. | G | confirmed (divu formu skaidrojums jau dokumentā) |
| K17 |  | Piedāvātais labojums: aktors / akceptors / induktors; piemērs nav apstiprināts | Kursa avots: Kinetika p.8–9; abas vietas attiecas uz vienu procesu. Laidler, Chemical Kinetics; Silbey–Alberty–Bawendi, Physical Chemistry (inducētās reakcijas sadaļa) — nav atvērtas; klasiskais piemērs bez lapas. | B | open — atvērta 2026-11-08: avots lieto “faktors” tajā pašā rindkopā; grāmatu lappuses nav atvērtas; jāapstiprina docētājam |
| K18 |  | NH₃·H₂O ⇌ NH₄⁺ + OH⁻; NH₄OH nav izolējams | Atkins, Physical Chemistry (skābju–bāzu līdzsvars, NH₃·H₂O) — nav atvērta. | B | confirmed (grāmata pārbaudāma) |
| K19 |  | Pd un Au brīvajā atomā ir d¹⁰; aktivitāte saistīta ar virsmu | Atkins, Physical Chemistry (pārejas metālu d-orbitāles) — nav atvērta. | B | confirmed (grāmata pārbaudāma) |
| K20 |  | 1 nm = 10⁻⁹ m = 10⁻⁷ cm | BIPM, SI brošūra (prefiksu tabula: nano = 10⁻⁹) — nav atvērta. | B | confirmed (grāmata pārbaudāma) |
| K21 |  | Katalizators nepadara termodinamiski neiespējamu reakciju iespējamu | IUPAC Gold Book C00876 (catalyst): 'increases the rate of a reaction without modifying the overall standard Gibbs energy change'. | G | confirmed |
| K22 |  | Nepieciešams CS ≫ [E]₀; stacionārais tuvinājums | Briggs & Haldane 1925, Biochem. J. 19(2), 338.–339. lpp. (PubMed 16743508, citāts pārbaudīts); Johnson & Goody 2011, Biochemistry 50(39), 8264.–8269. lpp. (PMC3381512, lasīts): M&M 1913 lietoja ātrā līdzsvara pieņēmumu; viņu konstante bija V/K_S, nevis K_M; stacionāro tuvinājumu ieviesa B&H. | V | confirmed + J&G piesardzības piezīme pievienota |
| K23 |  | Tīrā nekonkurentā ir apgriezeniska: vmax ↓, KM nemainās; jauktā mainās abi | Cornish-Bowden, Fundamentals of Enzyme Kinetics, 4. izd.; Segel, Enzyme Kinetics (tīrās nekonkurentās inhibīcijas sadaļas) — nav atvērtas. | B | confirmed (grāmatas pārbaudāmas) |
| K24 |  | Vēsturisks modelis; inducētā atbilstība precīzāk | Koshland 1958, PNAS 44(2), 98.–104. lpp. (PMC335371: citāts pārbaudīts; teksta pamatteksts tiešsaistē nav lasāms — skanēts PDF). | V | confirmed (citāts; teksts netiek citēts burtiski) |
| K25 |  | Otrā definīcija ir pareizā | IUPAC Gold Book A00446 (Ea Arrēniusa vienādojumā); deck 10 ir avota iekšēja pretruna. | G | confirmed |
| K26 |  | “Arrēniusa” | Ortogrāfija; AkadTerm fiksēts N01. | N | confirmed (nav grāmatas jautājums) |
| K27 |  | Temats 5; failu gadi atšķiras | Kosmētiska failu numerācija; PDF netiek laboti. | N | confirmed (nav grāmatas jautājums) |
| K28 |  | Īsta hiperbola tikai tuvojas vmax | Ar roku zīmēta avota skice; nolasījums ar pielaidi (MU Q10). | N | confirmed (nav grāmatas jautājums) |
| L1 |  | Kurss abās lapās norāda MnO; MnO₂ nav avota forma | Kursa avots: 5LW p.3 un 5LD p.5 (MnO). IUPAC Red Book, neorganisko savienojumu nomenklatūra (MnO₂ = mangāna(IV) oksīds) — pārbaudāma; nomenklatūra nenosaka kursa reagentu. | B | open — atvērta 2026-11-08: abas kursa lapas iespiež MnO; jautājums par drukas kļūdu un faktisko reagentu jāapstiprina docētājam |
| L2 |  | Papildināt ar novērojumiem un “heterogēni” | Atslēgas nepilnība (nav atbildes); papildinājums ar birkām. | N | confirmed (nav grāmatas jautājums) |
| L3 |  | k (mazais burts); K ir līdzsvara konstante | IUPAC Gold Book O04322: k ir ātruma konstante; K rezervēta līdzsvara konstantei (dokumenta 14. tabula). | G | confirmed |
| L4 |  | Mn(+VII) oksidēšanas pakāpe; MnO₄⁻ | IUPAC Gold Book O04365 (oxidation state): oksidēšanas pakāpe ir skaitīšanas lielums, nevis brīvs jons. | G | confirmed |
| L5 |  | redokss / oksidēšanās–reducēšanās | Terminoloģija (redokss); AkadTerm. | N | confirmed (nav grāmatas jautājums) |
| L6 |  | Balansēts: 2KMnO₄ + 5H₂C₂O₄ + 3H₂SO₄ → … | Aritmētika: vienādojuma bilance pārrēķināta (atomu un lādiņu skaits). | N | confirmed (nav grāmatas jautājums) |
| L7 |  | Mn²⁺ ir produkts un autokatalizators | Piezīme (nav kļūda); autokatalīzes apraksts ar modeli (N07-S3). | N | confirmed (nav grāmatas jautājums) |
| N1 |  | Nosaukums un asis jāsaskaņo | Jauns, kosmētisks (grafika virsraksts pret asīm). | N | confirmed (nav grāmatas jautājums) |

Kopskaits: 36 rindas; 25 ar nosauktu grāmatu/rakstu, 11 bez ārēja avota (aritmētika/ortogrāfija/iekšēja konsekvence — uzskaitītas augstāk).

## 3. Uzdevuma 1.–7. punkta statuss

1. **K10, katalāzes Ea — softened + diapazons.** Avota “23 J·mol⁻¹” paliek kā iespiests ar vienību kļūdas skaidrojumu; papildināts: publicētie mērījumi 12,9 ± 0,7 (Miłek 2018, lasīts), 19,7 (Altomare 1974), 23,5 (Hooda 2014) kJ·mol⁻¹. Viencipara vērtība nav atrasta — sākotnējā darba piezīmju pieņēmums “single-digit kJ/mol” **netiek apstiprināts** (AGENTS.md netiek labots; šis ir piezīmē. “nav zināms” paliek par konkrētā kursa mērījuma vērtību — jāapstiprina docētājai).
2. **K22, Mihaelisa–Mentenas atvasinājums — confirmed + piezīme.** Johnson & Goody 2011 apstiprina: M&M lietoja ātrā līdzsvaru; B&H ieviesa stacionāro. HTML teikums “stacionārais jeb Brigsa–Haldana, nevis Mihaelisa sākotnējais ātrā līdzsvara pieņēmums” paliek; pievienota vēstures piezīme (V/K_S pret K_M). Cornish-Bowden un Segel sadaļas paliek pārbaudāmas.
3. **K16, γ un Ea — confirmed.** Abas vērtību kopas (diferenciālā 51,9/82,2/103,7 un divu punktu 54/85/107) jau ir dokumentā ar skaidrojumu; Gold Book A00446 fiksē Arrēniusa formu. Atkins/Laidler sadaļas pārbaudāmas.
4. **K18/K19 — confirmed (mīkstas formulējuma piezīmes).** Abas jau ir bez ciparu apgalvojumiem; grāmatas nosauktas, sadaļas pārbaudāmas.
5. **K17, inducētā reakcija — still open.** Klasiskā piemēra lapa nav apskatīta (grāmatas nav atvērtas); HTML saglabā avota piemēru ar “apšaubāms” birku un klasisko piemēru bez lapas.
6. **Farmakokinētiskais pusperiods — confirmed (bez izmaiņām).** HTML neapgalvo “4–5 pusperiodi līdz stacionāram stāvoklim”; tur ir tikai precīza aritmētika (1/2⁵ = 3,125 %; 5 × 4 h = 20 h) ar norādi “aprēķina piemērs, ne zāļu ieteikums”.
7. **IUPAC Gold Book kā autoritāte — confirmed un pievienots.** O04322/M03989 definīcijas nolasītas burtiski; Gold Book kodi pievienoti 12. tabulas rindām K1, K2, K8, K11, K14, K16, K21, K22, K25, L3, L4.

## 4. Docētājai: kā atvērt grāmatas (lapas netiek apgalvotas)

- Atkins, *Physical Chemistry* (jebkura izdevuma sadaļas par Maksvela–Bolcmaņa sadalījumu, aktivācijas barjeru, molekularitāti, nulles pakāpi, skābju–bāzu līdzsvaru NH₃/H₂O, pārejas metālu d-orbitālēm).
- Laidler, *Chemical Kinetics* (jonu reakcijas, steriskais faktors, inducētās reakcijas).
- Cornish-Bowden, *Fundamentals of Enzyme Kinetics*, 4. izd. (stacionārās kinētikas nodaļa; tīrā nekonkurentā inhibīcija).
- Segel, *Enzyme Kinetics* (unireaktantu nodaļa).
- Silbey–Alberty–Bawendi, *Physical Chemistry* (inducētās reakcijas).
- BIPM, *SI brošūra* (prefiksu tabula); IUPAC Red Book (MnO₂ nomenklatūra).

## 5. Grozījumi dokumentā (N06.3, minimāli)

- 12. tabulas 25 rindu “Kāpēc” šūnām pievienots avota nosaukums (Gold Book kodi; Miłek 2018; Briggs–Haldane 1925; Johnson–Goody 2011; Koshland 1958; grāmatas ar atzīmi “pārbaudāma”).
- 6. tabulas piezīme: publicētais diapazons ar datiem un nosacījumiem; “literatūra šeit netiek izdomāta” aizvietots.
- 10. nodaļā: vēstures piezīme par K_M nosaukumu ar abiem rakstiem.
- 9. nodaļā: Koshland 1958 atsauce inducētās atbilstības modelim.
- Atklāto jautājumu sarakstā: katalāzes Ea jautājums papildināts ar publicēto diapazonu.
- numbers.json: lit.ea.cat.* (3 ieraksti, kind source) kā literatūras konstantes.

## 6. N10 piezīmes (2026-11-03)

- **LibreTexts 5.7 lapa atvērta kā norāde, nevis citāts.** Darba lapa (5LW 4. lpp.) norāda uz “Using Graphs to Determine Integrated Rate Laws” (chem.libretexts.org, CC BY-NC-SA 4.0, labota 13.02.2023). Lapas redzamais teksts apstiprina 3. tabulas slīpuma kolonnu: nulles pakāpei taisne ar slīpumu −k, pirmajai −k, otrajai +k. Salīdzināmā tabula pašā lapā ir attēls, tāpēc burtiski netiek citēta; saskaņā ar AGENTS §13 mācību vietnes dokumentā nav citējamas, un HTML enkurs paliek 5LW p.4. Līmenis: norāde (ne G/V/B/N).
- **Slīpumi ir paša aprēķins** no tabulas integrālajiem likumiem (C = C₀ − kt → −k; ln C = ln C₀ − kt → −k; 1/C = 1/C₀ + kt → +k); jauns numbers.json ieraksts nav vajadzīgs, jo nav skaitliska apgalvojuma.
- **LB kolonna 8. tabulā** nolasīta no 10. nodaļas Lineweaver–Burk attēlojuma (jau `papildinājums`); krustpunktu raksti seko no formulas 1/v = (K_M/v_max)(1/C_S) + 1/v_max ar attiecīgā tipa K_M,app un v_max,app.
- **Vārdu uzbūves plate (12 termini).** Dalījums pa morfēmām ir paša analīze pēc latviešu valodas standarta morfoloģijas (priedēklis/sakne/piedēklis/galotne, divdabju pazīmes -još-/-t-, ģenitīva -as/-a), nevis atvērta vārdnīca: līmenis N, lektora pārbaudāms. Eponīmi (Maksvela–Bolcmaņa, Arrēniusa, van 't Hofa, Mihaelisa) un aizguvumi (enerģija, konstante, substrāts, inhibīcija) apzināti paliek nedalīti; daļējs dalījums (at-/ne- + nedalīts atlikums) atzīmēts.

## 7. N18 piezīmes: Pielikums A un klīniskie enkuri (2026-11-05)

- **Rang, Dale, Ritter, Flower, Henderson.** *Rang & Dale's Pharmacology*, 9. izd., Elsevier, 2019. Nodaļas par farmakokinētiku (zāļu eliminācija, eliminācijas konstante $k_e$, pusperiods $t_{1/2}$, stacionārā koncentrācija $C_{\text{ss}}$, 4–5 pusperiodu eliminācijas likums) un fermentu inhibitoriem kā zālēm. Līmenis: **B** (grāmatas izdevums un temats nosaukts; konkrētas lapas nav atvērtas, lapu numuri netiek apgalvoti).
- **Brunton, Hilal-Dandan, Knollmann.** *Goodman & Gilman's The Pharmacological Basis of Therapeutics*, 13. izd., McGraw-Hill, 2018. Sadaļas par zāļu klīrensu, eliminācijas kinētiku un kovalento fermentu inhibīciju (aspirīns pret ciklooksigenāzi). Līmenis: **B**.
- **Nelson, Cox.** *Lehninger Principles of Biochemistry*, 7. izd., W. H. Freeman / Macmillan Learning, 2017. Nodaļa par fermentu kinētiku, pārejas stāvokļa analogiem un inhibīcijas mehānismiem (metotreksāts un dihidrofolātreduktāze, etanols un metanols pie alkohola dehidrogenāzes). Līmenis: **B**.
- **Pussabrukšanas laiks farmācijā un medicīnā.** Kursa temata apraksts (`5. temata apraksts.pdf`) kā obligātu prasību izvirza jēdzienu "pussabrukšanas laiks farmācijā un medicīnā". Aprēķina piemērs ar $t_{1/2} = 6\ \text{h}$ ir paša aprēķins no pirmās pakāpes eksponenciālā likuma ($100 \cdot (0{,}5)^n$, $93{,}75\ \%$, $96{,}875\ \%$, $99{,}219\ \%$): līmenis **N**.
- **F06 dozēšanas instruments.** Tas lieto to pašu $t_{1/2} = 6\ \text{h}$ piemēru un pirmās pakāpes viena kompartamenta modeli ar acumirklīgu absorbciju. Atkārtoto devu maksimums/minimums un uzkrāšanās koeficients ir atvasināti no $A(t)=A_0e^{-kt}$ un $k=\ln 2/t_{1/2}$; tie ir paša aprēķins (**N**). Farmakokinētikas tēmas autoritāte ir Rang & Dale's Pharmacology, 9. izd. (2019), farmakokinētikas nodaļa, līmenis **B**; konkrēts nodaļas numurs vai lapa netiek apgalvota.
- **Mērvienību pārrēķina piemērs ($\mu\text{mol}\cdot\text{min}^{-1} \to \text{mol}\cdot\text{L}^{-1}\cdot\text{s}^{-1}$).** Paša aprēķins (līmenis **N**) no fermentu aktivitātes starptautiskās vienības (U) definīcijas un spektrofotometra kivetes tilpuma $V = 2{,}0\ \text{mL} = 0{,}0020\ \text{L}$.
- **Grafiku nolasīšanas tolerances.** $v_{\text{max}} \approx 0{,}46 \pm 0{,}02\ \mu\text{mol}\cdot\text{min}^{-1}$ un $K_M \approx 1{,}2 \pm 0{,}2\ \text{mmol}\cdot\text{dm}^{-3}$ ir nolasījumi no kursa pašpārbaudes materiāla `MU_Kin_1_2015_cAB.pdf` ar fiksētām pielaidēm atbilstoši `numbers.json` un K28 defektu reģistram: līmenis **N**.

## 8. T01 dossieri: K10, K17, L1 (2026-11-08)

**Kas atkārtoti atvērts.** Precīzās lappuses: `Kinetika.pdf` 6., 8. un 9. lpp.; `5LW_MCh_Kinetics_2025_LV.pdf` 3. lpp.; `5LD_Kinetics_Laboratorijas_darbs_Atbildes_2026.pdf` 5. lpp. Izvilkums veikts ar `pdftotext -layout`, lappuse pa lappusei; tās pašas lappuses renderētas 140 dpi PNG formātā un pārbaudītas ar `tesseract 5.5.4` OCR. Lapu PNG un OCR SHA-256 ir `archive/T01_2026-11-08/source_pages_sha256.txt`; pirms-labošanas failu SHA-256 ir `archive/T01_2026-11-08/pre_edit_sha256.txt`. Master pirms labojumiem: `archive/Master_5_tema_kinetika_un_katalize.preT01.html`.

**Avotu failu SHA-256.** `Kinetika.pdf` `e744e7c02bbcdccceb0bd5b79527d3be0881a2b60c6a14573f8ce90530753000`; `5LW_MCh_Kinetics_2025_LV.pdf` `921c1ca2efe55d2004678a543399b79f770bcb73119791246a97ca702a9fea32`; `5LD_Kinetics_Laboratorijas_darbs_Atbildes_2026.pdf` `dc8b9eaa8320864b6c6084090bb0d35a319e87a7427a0048c7f34db08530ad4e`.

| ID | Avots un lpp. | Avots saka (burtiski) | Piedāvātais labojums | Pamatojums | Piemērojamība un robežas | Statuss |
|---|---|---|---|---|---|---|
| K10 | `Kinetika.pdf` p.6, 5. tabula | Sleja: `Ea, J/mol`. Šūnu saturs: `2H2O2 → 2H2O + O2; Fermentatīvā katalīze / katalāze; 23`. Tajā pašā tabulā bez katalizatora: `79000`. | `23 kJ·mol⁻¹` — tikai vienības labojums; skaitlis 23 paliek. | 23 J·mol⁻¹ ir mazāk par RT ≈ 2,5 kJ·mol⁻¹ pie 300 K, tāpēc vienība nav fizikāli ticama. Publicētie mērījumi: 12,9 ± 0,7 kJ·mol⁻¹ (Miłek 2018; *Aspergillus niger*, 20–50 °C, pH 6,9, 0,015 M H₂O₂), 19,7 (Altomare 1974, citēts pēc Miłek) un 23,5 (Hooda 2014, citēts pēc Miłek) kJ·mol⁻¹. | Miłek un citētie pētījumi attiecas uz konkrētiem katalāzes avotiem un apstākļiem; tie nepierāda kursa parauga vērtību. Kursa tabula nenosauc organismu, pH vai substrāta koncentrāciju. | **Atvērts.** Avota 23 J·mol⁻¹ paliek master kā iespiests; 23 kJ·mol⁻¹ ir tikai piedāvājums; nepieciešams docētāja apstiprinājums. |
| K17 | `Kinetika.pdf` p.8–9 | p.8: “Piemēram, reakcija H₂O₂ + 2HI → I₂ + 2H₂O sākas tikai tad, ja pievieno vielu, kas satur Fe²⁺ jonus, un sākas reakcija ar tiem: H₂O₂ + 2Fe²⁺ → 2Fe³⁺ + 2OH⁻.” p.9: “6FeSO₄ + 3H₂O₂ + 6HI → 2Fe₂(SO₄)₃ + 2FeI₃ + 6H₂O.” “Šajā reakcijā H₂O₂ ir faktors, HI ir akceptors, bet Fe²⁺ ir induktors (inducē reakciju).” | `“Faktors” → “aktors”`; piemēru uzskatīt par apšaubāmu indukcijas piemēru. | Avots lieto “faktors” tajā pašā rindkopā, kur apraksta indukciju; standarta triāde ir aktors / akceptors / induktors. Vai tas ir drukas kļūda, avots neizšķir. H₂O₂ var oksidēt jodīdu arī bez Fe²⁺, tāpēc piemērs nav droši indukcijas piemērs; tas ir ķīmiskās lietderības arguments, nevis avota labojums. | Abas vietas attiecas uz vienu un to pašu procesu (5.4. sadaļa, 8.–9. lpp.). Laidler un Silbey–Alberty–Bawendi sadaļas nav atvērtas; lapa netiek apgalvota. Klasiskais Fe²⁺/MnO₄⁻/Cl⁻ piemērs ir papildinājums, nevis avota teksts. | **Atvērts.** Master saglabā avota piemēru un “faktors”; labojums un alternatīvais piemērs ir atzīmēti kā neapstiprināti. |
| L1 | `5LW` p.3; `5LD` p.5 | `5LW` p.3: “Otrā mēģenē pievieno lāpstiņu MnO.” `5LD` p.5: tas pats teikums; vienādojums `2 H2O2 ---Katalizators (Fe2O3 vai MnO )---- → 2 H2O + O2↑`. | `MnO₂` (mangāna(IV) oksīds) — agrākais variants “Jābūt MnO₂ (vai jāapstiprina)” tiek saglabāts izcelsmes vēsturē, bet master to vairs nepasniedz kā kursa formu. | MnO un MnO₂ ir dažādas vielas; standarta H₂O₂ demonstrācijā parasti lieto MnO₂. Tomēr IUPAC nomenklatūra nenosaka, kuru vielu kurss faktiski lietoja, un abas kursa lapas iespiež MnO. | Reaģenta identitāte (MnO), mangāna oksidēšanas pakāpe (+II MnO; +IV MnO₂), reakcijas vienādojums un katalizatora loma ir atsevišķi evidenču lauki. Atslēgā nav masas, virsmas laukuma vai laika, tāpēc efektivitātes salīdzinājums nav pierādīts. | **Atvērts.** Kursa forma MnO paliek master; nepieciešams docētāja apstiprinājums par drukas kļūdu un faktisko lāpstiņas saturu. |

**Ko šie dossieri nemaina.** Neviens avota skaitlis, vienība vai reagents nav aizstāts ar literatūras vērtību. K10 avota vērtība paliek 23 J·mol⁻¹; K17 avota piemērs un vārds “faktors” paliek; L1 avota forma paliek MnO. Mainīts ir tikai statuss un tas, kā piedāvātais labojums tiek atzīmēts.

## 9. T07 piezīmes: mehānismi un ātruma kontrole (2026-11-09)

**Kas netika atkārtoti atvērts.** Šajā piegājienā `Kinetika.pdf`, `5LW` un `5LD` lapas netika atvērtas no jauna; T01 dossieri paliek spēkā. Tāpēc neviens jauns avota citāts, lapa vai piemērs netiek apgalvots. K17 paliek **atvērts**: master saglabā avota H₂O₂/HI piemēru ar skaidru **tentatīvs** atzīmi, un 7. attēls neizmanto K17 piemēru.

**Kas mainīts dokumentā.**

- `#ch7` ievadā un piezīmē 7 lēnākās stadijas apgalvojums tagad ir saistīts ar režīmu: viena izteikti lēnāka stadija un kvazistacionāri starpprodukti. Robeža ir atzīmēta kā `papildinājums`, jo avotā tās nav.
- 4. tabulas “Pakāpeniskās” rinda iegūst to pašu nosacījumu; “Sajūgtās” rindas piemērs atzīmēts kā tentatīvs.
- Pēc 4. tabulas pievienotas klašu atzīmes katram avota piemēram, izmantojot tikai tabulas tipu nosaukumus; atzīmes ir `papildinājums`, nevis jauns avota apgalvojums.
- `#fig-7` un `#fig-13` tagad lieto vienus un tos pašus stadiju nosaukumus (`iniciēšana`, `attīstība · N. cikls`, `apraušanās`, `gals`). `#fig-7` rāda divus attīstības posmus un viena nesēja apriti `Br· → H· → Br·`; zarošanās ir raustīta, nesarazotā ķēde — nepārtraukta, tāpēc atšķirība nav tikai krāsā.
- `#instr-chain` statiskais panelis (`#fig-13`) iegūst to pašu līniju kodējumu; abi panelī lieto vienus un tos pašus skaitļus no `numbers.json` (`chain.*`).
- Pievienoti divi ar klaviatūru atverami `details.qa` uzdevumi, kas prasa izskaidrot nesēja apriti un zarošanās ietekmi, nevis atpazīt stadiju nosaukumus.

**Statuss.** K17 un C09 paliek neatrisināti. Jaunais saturs ir modeļa robežu un ilustrācijas skaidrojums; tas neaizstāj avota piemēru un nepasniedz klasisko indukcijas piemēru kā kursa tekstu.
