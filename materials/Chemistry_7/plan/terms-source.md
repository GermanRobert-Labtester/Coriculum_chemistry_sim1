# T03.1 / T04 — terminu avotu pieraksts (scratchpad, nav piegāde)

## Angļu termini (IUPAC Gold Book)

<a id="t04-schema"></a>
## [T04-SHHEMA] Termiņu avota shēma

Katram strīdīgajam terminam fiksē piecos laukos:

| Lauks | Nozīme |
|---|---|
| Kanoniskā forma | forma, ko šis dokuments lieto pamattekstā |
| Alternatīvas | formas, kas saglabātas kā atpazīstami varianti, nevis dzīvā teksta formas |
| Gramatika | dzimte, locījumi, diakritikas; rakstības variants |
| Proveniencs | resurss ar URL un vaicājuma datums |
| Statuss | `avots` (resurss apliecina formu/nozīmi) · `nav pārbaudīts` (resurss nepieejams vai neatradās) · `mājas stils` (apzināta redakcijas izvēle bez valodas iestādes apliecinājuma; nekad nesauc par normu) |

<a id="t04-query-log"></a>
## [T04-QUERY-LOG] 2026-11-09 vaicājumi — tezaurs.lv un AkadTerm

Vaicāts 2026-11-09 (šīs darba runas laikā) ar tiešu lapu izgūšanu; katram rezultātam fiksēts URL un precīzs statuss, arī negatīvie rezultāti.

| Termins | Resurss / URL | Rezultāts (precīzs) | Statuss |
|---|---|---|---|
| kivete | tezaurs.lv/_search/kivete; mlvv.tezaurs.lv/kivete:1; llvv.tezaurs.lv/kivete:1 | Atrasts vārdos (1) abos; MLVV: dsk. ģen. -šu, s. dz., “lēzens, taisnstūrveida trauks”, cilme no fr. *cuvette*; LLVV 2. ķīm.: “neliels (parasti četrstūrains) stikla trauks (optiskajā aparatūrā šķidrumu īpašību pētīšanai)” | **avots** |
| kivete | akadterm.lv/term.php?term=cuvette&lang=EN&exact=1 | “Atrasts 1 termins”: EN cuvette → LV **kivete (IETEICAMS)**; ķivete (IATE); otrais šķirklis EN cell; cuvette → LV kivete (VVC izstrādātie ķīmijas un ķīmiskās tehnoloģijas termini) | **avots** |
| kuvete | tezaurs.lv/_search/kuvete | “Vārdos nav. … Citās vārdnīcās nav šķirkļa __kuvete__” — nav nevienā iekļautajā vārdnīcā | **avots** (negatīvs rezultāts: variants nav apliecināts) |
| absorbance | tezaurs.lv/_search/absorbance | “Citās vārdnīcās nav šķirkļa __absorbance__” | **avots** (negatīvs: neangliska forma nelietoama kā latvisks vārds) |
| absorbance | akadterm.lv/term.php?term=absorbance&lang=EN&exact=1 | “Atrasti 4 termini”; šķirklis 1: EN absorbance → LV **absorbcija** (IATE); DE rindā arī “Extinktion; optische Dichte” | **avots** |
| absorbcija (procesa vārds) | tezaurs.lv/_search/absorbcija | Atrasts vārdos (4); savienojumi “absorbcijas koeficients”, “absorbcijas spektrs” u. c. — apliecina procesa/parādības nozīmi | **avots** |
| transmitance | tezaurs.lv/_search/transmitance | “Citās vārdnīcās nav šķirkļa __transmitance__” | **avots** (negatīvs) |
| transmittance | akadterm.lv/term.php?term=transmittance&lang=EN&exact=1 | “Atrasti 5 termini”; EN transmittance → LV **caurlaides koeficients** (Latviešu-angļu enerģētikas un elektrotehnikas vārdnīca — 2006) | **avots** |
| caurlaidība | tezaurs.lv/_search/caurlaidība | Atrasts vārdos (12) ar savienojumu “gaismas caurlaidība”; fizikā nozīmē arī magnētisko/dielektrisko caurlaidību (permeability) — daudznozīmīgs | **avots** |
| molar absorbance coefficient | akadterm.lv/term.php?term=molar+absorbance+coefficient&lang=EN&exact=1 | EN molar absorption coefficient u. c. → LV **molārais absorbcijas koeficients** (IATE); “molar absorptivity” atzīmēts kā ATCELTS | **avots** |
| specific absorbance | akadterm.lv/term.php?term=specific+absorbance&lang=EN&exact=1 | EN specific absorbance → LV **īpatnējā absorbcija**; īpatnējais optiskais blīvums (IATE) | **avots** |
| specific absorptivity | akadterm.lv/term.php?term=specific+absorptivity&lang=EN&exact=1 | “Atrasti 0 termini” — tieša AkadTerm šķirkļa nav | **avots** (negatīvs) |
| absorptance | akadterm.lv/term.php?term=absorptance&lang=EN&exact=1 | EN absorptance → LV **absorbcijas koeficients** (IATE + enerģētikas vārdnīca 2006) | **avots** |

**Vaicājuma robeža:** AkadTerm rezultātu apgabals dažos tiešajos LV vaicājumos (term.php?term=kivete&lang=LV) lapas tekstā neizvilkās — šo gadījumu statuss balstās uz nolasāmajiem EN→LV šķirkļiem (cuvette, cell, absorbance, transmittance, absorptance, molar absorbance coefficient, specific absorbance), nevis uz neatrasto LV indeksu. IATE norāde “kivete (IETEICAMS)” ir ES terminoloģijas datubāzes ieteikums latviešu formai; tā nav Latvijas valodas iestādes norma. tezaurs.lv (MLVV/LLVV) ir LU MII publicētās akadēmiskās vārdnīcas; tie nav terminoloģijas lēmumi, bet gan lietošanas apliecinājumi ar gramatiku.

- **absorptance, α** — "Ratio of the absorbed to the incident radiant power.
  Also called absorption factor." Avots: IUPAC Gold Book, šķirklis A00035
  (https://old.goldbook.iupac.org/html/A/A00035.html; skatīts caur meklētāja
  citātu — tiešā lapa šajā vidē atgrieza HTTP 403, tāpēc pilns šķirkļa teksts
  nav pārbaudīts). Statuss rindai: **avots** (definīcija, vairāki saskanīgi
  citāti) + piezīme par 403.
- **absorbance** — "Logarithm of the ratio of incident to transmitted radiant
  power through a sample (excluding the effects on cell walls)."
  Avots: IUPAC Gold Book, šķirklis A00028 (meklētāja citāts no
  https://goldbook.iupac.org/terms/view/A00028). Statuss: **avots**.
- **internal absorptance, αi** — "Absorptance when surface effects and effects
  of the cuvette such as reflection losses are excluded." Avots: Gold Book
  I03100 (citāts). Lietots formulai α = 1 − T − R (enerģijas bilance;
  atstarošana R parasti maza pret tukšo paraugu). Statuss: **papildinājums**
  (formula) ar Gold Book pamatu.

## Latviešu vēsturiskās formas

- **optiskais blīvums** — lietošana apliecināta: ES vīna regulējuma tulkojums
  ("optiskais blīvums pie 425 nm 1 cm biezumā"), skeneru specifikācijas
  ("Optiskais blīvums 3,2/3,4"), RTU atslēgvārdi. Nozīme = optical density,
  absorbance sinonīms vecākos tekstos. Statuss: **avots** (lietošana
  apliecināta); nav pārbaudīts pret AkadTerm kā kursa standarts.
- **ekstinkcija** — šajā vidē neviens pārbaudāms latviešu avots nebija
  pieejams; rinda formulēta kā "vecākos tekstos var sastapt", statuss
  **nav pārbaudīts**.
- **graduēšana** (graduated test object — "graduētu pēc biezuma testa objektu"
  sastapts RTU tekstā instrumentu, nevis kalibrēšanas nozīmē) — kalibrēšanas
  nozīmē šajā vidē nav pārbaudīta; statuss **nav pārbaudīts**.
- **etalonšķīdums** — šajā vidē neviens pārbaudāms avots nebija pieejams;
  statuss **nav pārbaudīts**.
- **kuvete** — ķīmiskā stikla trauka nosaukuma rakstības variants; dokumentā
  lietots "kivete". Statuss **nav pārbaudīts** (pareizrakstības, nevis
  satura jautājums). *T04 atjauninājums 2026-11-09: tezaurs.lv meklējums
  neko neatrada — skat. [T04-QUERY-LOG](#t04-query-log); variants nav
  apliecināts nevienu no iekļautajām vārdnīcām.*

## C-04 — 440 nm iestatījums, 444 nm literatūra, lokālais spektrs

Trīs atsevišķi apgalvojumi; tos nedrīkst sapludināt vienā.

| # | Apgalvojums | Statuss un avots | Ko tas pamato / ko ne |
|---|---|---|---|
| 1 | LD 6B mērījumi veikti pie 440 nm | **avots** — protokola iestatījums | Pamato tikai mērījuma vilni. Nepamato, ka 440 nm ir maksimums vai uz plakanas joslas daļas. |
| 2 | Riboflavīna absorbcijas maksimums ūdenī ir 444 nm (223, 267, 373, 444 nm) | **avots** — Sheraz u. c., *Beilstein J. Org. Chem.* 10 (2014), 1999–2012, DOI 10.3762/bjoc.10.208; teksts lasīts; ūdens šķīdums | Pamato literatūras maksimumu ūdenī. Nepamato LD 6B šķīdinātāju, pH, jonu spēku vai instrumenta joslas platumu. |
| 3 | Lokālais spektrs LD 6B apstākļos | **nav pieejams** — spektrs šajā darbā netika uzņemts | Nevar apgalvot, ka 440 nm ir uz plakanas virsotnes. Jebkurš plakanuma apgalvojums ir ierobežots secinājums no literatūras joslas formas, nevis mērījums. |

**Piemērojamība:** 3.2. nodaļa (mērījuma viļņa izvēle), 7.2. nodaļa (joslas
platums), 10.1. nodaļa (darba apstākļi), 15.d (avotu pārbaudes līmenis), E24
(labojumu žurnāls). **Aizliegtais formulējums:** “440 nm ir uz joslas plakanās
virsotnes” bez atzīmes, ka tas šajā darbā nav pārbaudīts.

**Avota robeža:** Sheraz u. c. dati iegūti ūdenī; tie neapliecina šī darba pH,
šķīdinātāju vai spektrofotometra joslas platumu. Tāpēc 444 nm drīkst lietot kā
literatūras faktu, nevis kā lokālu kalibrācijas pamatojumu.

<a id="t04-c08"></a>
## [T04-C08] C-08 atrisinājums (2026-11-09)

**Pirms T04:** “kivete” un “absorbance” ir mājas izvēle; AkadTerm statuss
nav pārbaudīts; “caurlaidība” bez pārbaudes.

**Pēc T04 vaicājumiem (2026-11-09, skat. [T04-QUERY-LOG](#t04-query-log)):**

1. **kivete** — nav tikai mājas izvēle: MLVV un LLVV šķirkļi apliecina formu
   ar gramatiku (LLVV 2. ķīm. nozīme ir tieši optiskās aparatūras trauks),
   un AkadTerm/IATE piedāvā to kā ieteicamo (VVC ķīmijas kolekcijā — kā
   vienīgo formu). Dokumenta izvēle ir **avotu atbalstīta**. Tomēr tas nav
   “valodas iestādes apstiprināts termins”: MLVV/LLVV ir vārdnīcu
   apliecinājumi, nevis normatīvs lēmums, un “IETEICAMS” ir IATE statuss.
   Formulējums dzīvajā tekstā: “avotu atbalstīta forma, ko apliecina MLVV,
   LLVV un IATE/AkadTerm; nav valodas iestādes norma”.
2. **kuvete** — negatīvs rezultāts: ne MLVV, ne LLVV, ne Tēzaura kopējais
   indekss šo formu neietver. 22. tabula to turpina uzskaitīt kā atpazīstamu
   rakstības variantu (avotu citāti paliek neskarti), bet “nav pārbaudīts”
   birka tiek aizstāta ar pārbaudītu negatīvu rezultātu.
3. **absorbance** — angliska forma, latviešu vārdnīcās nav (negatīvs);
   AkadTerm/IATE savieno EN absorbance ar LV “absorbcija”, kas šajā darbā
   tieši radītu absorbcija/absorbance sadursmi. “Absorbance” paliek **mājas
   stils**: apzināta nozīmju nošķiršana (process = absorbcija; lielums =
   absorbance), nevis valodas norma, un nevis apgalvojums, ka valodas
   iestāde to ir apstiprinājusi.
4. **transmitance** — angliska forma, vārdnīcās nav (negatīvs); AkadTerm
   apliecina latvisku ekvivalentu “caurlaides koeficients”. “Caurlaidība”
   kāda apliecināta (arī “gaismas caurlaidība”), bet fizikā ir daudznozīmīga
   (arī permeability), tāpēc dokumenta izvēle lietot “transmitance T” ar
   piezīmi paliek mājas stils ar avotu apzīmētu alternatīvu.
5. **molārais absorbcijas koeficients** (ε) — AkadTerm/IATE apliecina
   precīzi šo formu; “molar absorptivity” ir atcelts (ATCELTS). “Īpatnējais
   absorbcijas koeficients” (a) paliek mājas apraksta forma: AkadTerm
   “specific absorptivity” šķirkļa nav, “specific absorbance” ekvivalents ir
   “īpatnējā absorbcija” — cita nozīme; aprakstiskais latvisks variants
   “absorbētā daļa (α)” absorptance vietā ir mājas apraksts, jo AkadTerm
   piedāvā “absorbcijas koeficients”, kas šajā tekstā radītu koeficientu
   sadursmi.

**Ko tas maina produktā:** tikai statusa birkas un vienu piezīmes rindkopu;
kanoniskās formas nemainās. Nekas netiek pasniegts kā “oficiāli apstiprināts”.
Erratum žurnāls (E1–E26) netiek paplašināts: kauns nebija kļūda tekstā, bet
nepārbaudīts statuss, kuru tagad aizstāj pārbaudīts rezultāts (pārvaldības
ieraksts — AGENTS §11 un OPEN_ISSUES ISS-011).

<a id="t19-verify-log"></a>
## [T19-VERIFY-LOG] 2026-11-12 bibliogrāfiskās pārbaudes pieraksts (T19)

Pārbaudes metode: Crossref REST API (`api.crossref.org/works/<DOI>`), Open
Library (jēdzienu `/isbn/<ISBN>.json` un meklēšanas API), izdevēja produktu
lapa; brīvās piekļuves tekstiem — Europe PMC REST + pilnais XML. Datums
2026-11-12. Rezultāti ierakstīti arī `plan/claim-ledger.csv` (shēma: kind,
id, source, status, claim, scope, conditions, reviewer, date).

| Avots | Metode | Rezultāts (precīzs) | Jauns statuss |
|---|---|---|---|
| Sheraz 2014, DOI 10.3762/bjoc.10.208 | Crossref + Europe PMC pilnais teksts (PMC4168737, CC BY, PMID 25246959) | Metadati sakrīt (Beilstein J. Org. Chem. 10, 1999–2012); ievadā teikums “strong absorption at 223, 267, 373 and 444 nm in the UV and visible regions in aqueous solution” | `teksts lasīts` — tēma ievads; apjoms tikai ūdens šķīdumi |
| Currie 1995, DOI 10.1351/pac199567101699 | Crossref; De Gruyter pilnais teksts | Metadati sakrīt (izdevēja ieraksts tagad Walter de Gruyter); pilnais teksts atgrieza HTTP 202 ar tukšu pamattekstu (meklētāju bloks) | `metadati` — paliek tikai nomenklatūras avots |
| Gold Book A00028 / A00035 / M03972 | Crossref + tiešas šķirkļu lapas (iepriekš HTTP 403) | Trīs definīciju teksti lasīti; A00028: logaritms, decadā/naturālā bāze, “extinction” rezervēts citam lielumam; M03972: A/(c·l), L·mol⁻¹·cm⁻¹, “molar absorptivity” nav ieteicams; lapās redzamās atsauces (Green Book 2. izd., p. 32; PAC 2007, 79, 293) ir šķirkļu metadati | `teksts lasīts` (definīciju līmenī) |
| Beer 1852 / Planck 1901 / Einstein 1905 / Lewis 1926 | Crossref | Visi četri: nosaukums, sējums, lappuses, gads sakrīt; Lewis 1926 virsraksts “The Conservation of Photons” | `metadati` (bez izmaiņām, atkārtoti apstiprināts) |
| Skoog 7. izd., ISBN 978-1-305-57721-3 | Cengage produktu lapa (primārais izdevējs) + Open Library + LC klasifikācija | **Gada pretruna atrisināta**: Cengage norāda “7th Edition © 2018”; Open Library kopienas ieraksts (2016) ir novirzība; LC klasifikācijas ieraksts QD79.I5S58 2018 saskan ar 2018 | `metadati` + `lapa nav pārbaudīta` (bez izmaiņām tierā) |
| Atkins 12. izd., ISBN 978-0-19-884781-6 | Open Library; OUP produktu lapa | OL: OUP, 2022; OUP lapa šajā vidē atgrieza tukšu saturu | `metadati` (bez izmaiņām) |
| Green Book 3. izd., ISBN 978-0-85404-433-7 | Open Library | OL: RSC, 3. izd., izdošanas datums 2007-09-30 | `metadati` (bez izmaiņām) |
| Harris 10. izd. | Open Library + izdevēja piedāvājuma meklēšana | **Jauns rezultāts**: drukas ISBN 978-1-319-16430-0 (OL ieraksts: W. H. Freeman, izdošanas datums 2019-12-13); 10. izdevums ar autoriem Harris un Lucy apstiprināts ar izdevēja piedāvājuma ierakstiem; izdevēja produktu lapa nepieejama (tagad 11. izd.) | `nav pārbaudīts` → `metadati` |

**Produkta izmaiņas (T19.2):** n15-d katram ierakstam pievienots identifikators
[R1]–[R8] un precizēts statusa valoda (datumi, metode, derīguma apjoms); n15-src
ierakstiem [S1]–[S3]; E1–E28 nav aiztikti. Jauns gates: `tools/lint_claims.py`
(L1–L7; `--selftest` 7 fiksēti mutantu, visi noķerti; bāzes līnija tīra), lasāms
run.sh solī 2e. Skolo.lv saite (ISS-009) šajā runā netika pārbaudīta — statuss
`nav pārbaudīts` saglabāts (CL-13).
