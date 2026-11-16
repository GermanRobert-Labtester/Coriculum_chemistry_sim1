# Jautājumu veidi, varianti un vērtēšana

Status: design specification, 2026-11-16. Student prompts are Latvian; implementation guidance is English. The examples are newly authored practice proposals, not recovered RSU exam questions. Programme coverage comes from the supplied 2025 PDF. No student-facing simulator has been built.

## 1. Question-type catalogue

A form must exercise at least eight types and give at least 70/100 points for constructed responses. Selecting prewritten answers contributes at most 10/100 points; baseline forms can use zero multiple choice. A family can combine multiple types in subparts.

| ID | Learner action | Response contract | Family examples | Scoring |
|---|---|---|---|---|
| Q01 | Skaitliska atbilde ar mērvienību | Number + unit + unrounded calculation value; rounding criterion separate. | 2B,3A,3B,4C,5C,6C,7C | Numeric tolerance and dimension; representation checked separately. |
| Q02 | Daudzsoļu aprēķins | Given / formula / substitution / result / interpretation fields. | 1C,3B,3C,4B,4C,6C,7C | Criterion-level points and error-carried-forward policy. |
| Q03 | Formulas pārveidošana | Build an allowed symbolic relation, then name conserved quantity. | 3B,3C,4C,5B,7A | Restricted symbolic templates; valid alternative derivations use manual rubric. |
| Q04 | Vienādojuma koeficienti | Fill integer coefficient fields for a fixed, stated species list. | 1C,1D,6B | Atom/charge conservation, nonzero positive integers and lowest ratio. |
| Q05 | Pusreakcija un elektronu bilance | Species, electrons and medium in structured rows, then combine. | 6B | Atom + charge + electron audit; chemical species whitelist. |
| Q06 | Atbilstību veidošana | Map instruments, quantities or names to descriptions. | 1B,2A,4A,7A | Unique label IDs; keyboard select controls; no position-based key. |
| Q07 | Klasifikācijas tabula | Assign multiple properties with compatible categories. | 1A,1B,4A,5D,6A | Per-cell rubric; allow overlapping reaction classes. |
| Q08 | Darbību secība | Arrange preparation/titration steps and explain a critical step. | 2A,3C,6C,7D | Partial-order constraints; multiple equivalent orders allowed. |
| Q09 | Tabulas aizpildīšana | Complete missing units, concentrations, signs or data. | 2B,3B,4B,5B,7B | Each field scored; derived cells retain dependency metadata. |
| Q10 | Skalas nolasīšana | Read meniscus/balance or two burette readings from an SVG. | 2C,6C | Coordinate-derived answer, scale resolution and sig figs. |
| Q11 | Grafika konstruēšana | Choose axes/units/scale; enter or place measured points. | 2D,5B,7B | Axis choice + coordinates + model; keyboard table equivalent. |
| Q12 | Grafika interpretācija | Read slope, intercept, half-life, activation barrier or concentration. | 2D,5A,5B,5C,7B | Numerical read with scale tolerance plus explanation rubric. |
| Q13 | Kļūdas atrašana un labošana | Locate a wrong step, replace it, explain the consequence. | 2B,3D,4D,5D,6D,7D | Not just selecting an error; correction and reason required. |
| Q14 | Apgalvojums un labojums | Judge each statement and rewrite the false ones. | 1B,4A,5A,6A,7D | Truth field can auto-check; written repair uses visible criteria. |
| Q15 | Īss skaidrojums | Explain mechanism or inference in 2–4 sentences. | 1B,4D,5D,6A,7A | Self-/human-assessed rubric; keywords never impersonate semantic grading. |
| Q16 | Salīdzini un pamato | Compare two cases and justify using the supplied evidence. | 1D,4C,5D,6D,7D | Separate comparison and causal explanation points. |
| Q17 | Saistīts gadījums | Shared data feed several independently scored subparts. | 3D,4D,5C,6C,7C | No answer leakage across subparts; dependencies declared. |
| Q18 | Vairāku atbilžu izvēle ar pamatojumu | Optional several-correct statements plus a required reason. | 1A,5D,7D | At most 10% of paper points; not needed for baseline forms; no 1-of-4 quota. |

## 2. Variant policy

A variant changes numbers, the requested unknown, a graph, evidence, medium or reasoning route. Shuffling options or cosmetic wording does not count. A-D below are four specifications per family, not 112 finished questions. All four must be authored, computed, source-reviewed and difficulty-reviewed before the bank target is met. The 14 worked examples are design exemplars and do not substitute for those 112 instances.

Use family_id + variant_id + schema_version + bank_version + explicit seed for replay. Freeze parameter draws and question order in a manifest using a documented PRNG, never Date.now or Math.random as the sole provenance. Avoid zero/negative concentrations, impossible dilution (c₂≥c₁ when dilution is required), Q≤0, log of a dimensional or nonpositive value, degenerate plots and inaccessible scale ticks. Check point counts, units, calibration interval, reaction medium, percent basis, and expected sig figs before accepting any draw.

Numerical changes must preserve intended step count, difficulty and reading resolution. Structural variants that change reaction medium, stoichiometry, order or concentration basis require a separate reviewed key. Specify whether density or volume additivity is supplied; missing required data is only intentional in a tagged insufficient-data task.

## 3. Twenty-eight question families and four variants each

### FAM-1A — Maisījumu, vielu klašu un reakciju klasifikācija

Topic 1; types: Q07, Q13; coverage: P1-02, P1-03, P1-04.

- **A:** NaCl(aq), ūdens un smiltis; klasificē fāzes un vielu klases

- **B:** CuO + H₂; atšķir aizvietošanu no redoksa un pieļauj abus

- **C:** CaCO₃ sadalīšanās; atrodi nepareizu reakcijas tipu

- **D:** Izveido pretpiemēru apgalvojumam, ka visi maisījumi ir heterogēni

### FAM-1B — Daļiņas, saites un disociācija

Topic 1; types: Q06, Q14, Q15; coverage: P1-05, P1-06, P1-07.

- **A:** NaCl, H₂O un glikoze; atomi/joni/molekulas, disociācija

- **B:** MgCl₂; uzraksti jonus un skaidro elektrovadītspēju

- **C:** Labot apgalvojumu: šķīšana vienmēr veido jonus

- **D:** Salīdzināt jonu un kovalentu saiti ar dotiem piemēriem

### FAM-1C — Bilance un stehiometrija

Topic 1; types: Q04, Q02; coverage: P1-01, P1-03.

- **A:** Mg + O₂ → MgO; m(Mg)=4,80 g, M(Mg)=24,0 g/mol

- **B:** Al + O₂ → Al₂O₃; n(Al)=0,200 mol

- **C:** CaCO₃ → CaO + CO₂; no produkta masas atrod sākuma masu

- **D:** Dotā nepareizā bilance; salabo un izskaidro masas nezūdamību

### FAM-1D — Tabulas un nogulsnēšanās

Topic 1; types: Q16, Q04; coverage: P1-08, P1-09.

- **A:** Dota šķīdības tabula: Na₂CO₃ + CaCl₂; saīsināts jonu vienādojums

- **B:** Dota tabula: AgNO₃ + NaCl; pamato nogulsnes

- **C:** Dota tabula: NaNO₃ + KCl; pamato, kāpēc nav neto reakcijas

- **D:** No dotās periodiskās tabulas atrodi M un prognozē jona lādiņu

### FAM-2A — Trauki un mērījuma izvēle

Topic 2; types: Q06, Q08, Q07; coverage: P2-01, P2-04.

- **A:** Pagatavot precīzu tilpumu; izvēlies mērkolbu un pipeti, secība

- **B:** Atšķirt bireti, mērcilindru un vārglāzi pēc lietojuma

- **C:** Svari + pipetes uzpildītājs; kvalitatīvi/kvantitatīvi novērojumi

- **D:** Labot trauku izvēli dotā atšķaidīšanas procedūrā

### FAM-2B — Vienības, proporcijas un zīmīgie cipari

Topic 2; types: Q01, Q09, Q13; coverage: P2-02, P2-03, P2-05, P2-06, P2-10.

- **A:** 0,00450 kg → mg; pēc tam reizini mērījumus un noapaļo

- **B:** 2,50×10⁻⁶ mol → μmol; nano-, kilo-, mega-, giga- tabula

- **C:** 25,0 °C → K; 18,40−2,15 mL un dalīšanas zīmīgie cipari

- **D:** Apgrieztā proporcija, procenti un kļūdaina 10³ reizinātāja labojums

### FAM-2C — Skala un menisks

Topic 2; types: Q10, Q01; coverage: P2-07, P2-10.

- **A:** Birete: 2,15 un 18,40 mL, iedaļa 0,1 mL

- **B:** Birete: 0,35 un 21,70 mL; vertikālā skala aug uz leju

- **C:** Svari: digitāls 1,204 g; atšķir digitālu un analogu nolasījumu

- **D:** Mērcilindra menisks; nosaki diapazonu un nepamatotu papildu ciparu

### FAM-2D — Grafika veidošana un nolasīšana

Topic 2; types: Q11, Q12; coverage: P2-08, P2-09.

- **A:** c/A dati ar pozitīvu nogriezni; izvēlies asis un interpolē

- **B:** Laiks/koncentrācija; izvēlies skalu un nolasījumu

- **C:** Dotā grafikā samainītas asis un nav vienību; labot

- **D:** No datu tabulas izvēlies mērogu, uzzīmē un nosaki slīpumu

### FAM-3A — Koncentrācijas un daļiņu daudzums

Topic 3; types: Q01, Q02, Q09; coverage: P3-01, P3-02, P3-04, P3-05, P3-06.

- **A:** m=2,922 g NaCl, M=58,44 g/mol, V=250,0 mL; c un joni

- **B:** n=0,0250 mol, V=100,0 mL; c un m pie dotas M

- **C:** Dota c un V; aprēķini n un m, formulē šķīdinātāju/vielu

- **D:** Atšķir w, γ un c dotajās etiķetēs un aizpildi vienību tabulu

### FAM-3B — Blīvums un pārejas w/c/γ

Topic 3; types: Q02, Q03, Q09; coverage: P3-07, P3-08, P3-09.

- **A:** w=10,0 %, ρ=1,070 g/mL, M=58,44 g/mol; γ un c

- **B:** c=0,250 mol/L, M=40,00 g/mol, ρ=1,010 g/mL; w

- **C:** V=200,0 mL, ρ=1,050 g/mL, w=4,00 %; m un γ

- **D:** Dota γ un M; izsaki c, pēc tam izskaidro trūkstošo ρ pārejai uz w

### FAM-3C — Atšķaidīšana un pagatavošana

Topic 3; types: Q02, Q08, Q03; coverage: P3-10, P3-11.

- **A:** 0,500 mol/L → 100,0 mL 0,0500 mol/L; V₁ un darbību secība

- **B:** 0,200 mol/L → 250,0 mL 0,0200 mol/L; V₁

- **C:** Doti c₁, V₁, V₂; atrod c₂ un pamato gatavā tilpuma nozīmi

- **D:** Labot instrukciju pievienot V₂ ūdens, nevis atšķaidīt līdz V₂

### FAM-3D — Medicīniskas etiķetes un nepietiekami dati

Topic 3; types: Q17, Q13, Q15; coverage: P3-03, P3-11.

- **A:** 0,9 % NaCl, skaidri dots m/V; masa 250,0 mL un ko etiķete vēl nepasaka

- **B:** 5 % glikoze ar skaidru m/m bāzi; dots ρ un tilpums

- **C:** 3 % H₂O₂, 70 % etanols, 5 % jods: no dotām etiķešu bāzēm izvēlies pārrēķinu

- **D:** Dota analīžu rinda mg/L; pārvērt mmol/L tikai ar norādītu vielu un M

### FAM-4A — Sistēma, enerģija un termodinamikas likumi

Topic 4; types: Q07, Q14, Q06; coverage: P4-01, P4-04, P4-05, P4-06.

- **A:** Atvērts, slēgts, izolēts; siltums sistēmā un darbs uz sistēmu

- **B:** Dota q un w; ΔU un ekso/endotermiska interpretācija

- **C:** Standartstāvoklis, kinētiskā/potenciālā enerģija; maldīga definīcija

- **D:** Otrais likums: sistēmas ΔS nav vienīgais patvaļīguma kritērijs

### FAM-4B — Hesa likums un reakcijas ΔS

Topic 4; types: Q02, Q09; coverage: P4-02, P4-03, P4-09.

- **A:** Divas saskaitāmas reakcijas ar ΔH; ΔS no dotas S tabulas

- **B:** Apgriez reakciju, maini ΔH zīmi un sareizini koeficientus

- **C:** Trūkstoša ΔH no termokīmiskā cikla

- **D:** Labot izlaistus stehiometriskos koeficientus ΔS aprēķinā

### FAM-4C — ΔG un temperatūras robeža

Topic 4; types: Q02, Q16; coverage: P4-02, P4-08, P4-10, P4-11.

- **A:** ΔH=40,0 kJ/mol, ΔS=150 J/(mol K), T=298 K

- **B:** ΔH=−20,0 kJ/mol, ΔS=−80,0 J/(mol K), T=298 K

- **C:** Atrod T robežu un norāda pieņēmumu par ΔH,ΔS nemainību

- **D:** Salīdzina ΔG divās temperatūrās, nesecinot reakcijas ātrumu

### FAM-4D — Kalorimetrija un skaidrojuma kļūdas

Topic 4; types: Q17, Q13, Q15; coverage: P4-04, P4-07, P4-11.

- **A:** m=100,0 g, c_p=4,18 J/(g K), ΔT=5,00 K; q videi un reakcijai

- **B:** Sadegšanas siltums dotai pārtikas masai, neizmanto kā medicīnisku rekomendāciju

- **C:** Nenoslēgta sistēma ar siltuma zudumiem; nosaki secinājuma robežu

- **D:** Labot ΔS<0 nozīmē neiespējams un ΔG<0 nozīmē ātrs

### FAM-5A — Faktori, sadursmes un enerģijas grafiki

Topic 5; types: Q12, Q14, Q16; coverage: P5-01, P5-02, P5-04, P5-07.

- **A:** Enerģijas profilā Eᵣ=20, Eₚ=−10, maksimumi 100/60 kJ/mol

- **B:** Divu temperatūru Maksvela–Bolcmaņa līknes; skaidro virs Eₐ daļu

- **C:** Virsmas laukums, koncentrācija un gāzes spiediens; kontrolē pārējos faktorus

- **D:** Labot apgalvojumu katalizators maina ΔH vai līdzsvara stāvokli

### FAM-5B — Reakcijas pakāpe un k

Topic 5; types: Q09, Q02, Q11; coverage: P5-05, P5-09.

- **A:** c dubultojas, v četrkāršojas; nosaki pakāpi un k

- **B:** c dubultojas, v dubultojas; pirmā pakāpe, k vienības

- **C:** c mainās, v nemainās; nulltā pakāpe

- **D:** No c(t), ln c(t), 1/c(t) datiem izvēlas lineāru attēlojumu un k

### FAM-5C — Pusperiods un modelis

Topic 5; types: Q12, Q02, Q17; coverage: P5-08, P5-10.

- **A:** Pirmās pakāpes modelis: 80→40 mg 30 min; daudzums pēc 90 min

- **B:** Pirmās pakāpes modelis: t½=20 min, sākumā 64 mg; pēc 60 min

- **C:** No nulltās pakāpes grafika nosaki t½ pie dotā c₀

- **D:** Salīdzini pirmās/otrās pakāpes t½ atkarību no sākuma c

### FAM-5D — Katalīze, enzīmi un mehānismi

Topic 5; types: Q15, Q13, Q16, Q18; coverage: P5-03, P5-06.

- **A:** Enzīms un nebioloģisks katalizators; kopīgais un atšķirīgais

- **B:** Daudzstadiju mehānismā dota lēnā stadija; atvasini nosacītu ātruma likumu

- **C:** Atšķir homogēnu/heterogēnu katalīzi dotās fāzēs

- **D:** Labot reakcijas kopējo koeficientu automātisku lietošanu par pakāpēm

### FAM-6A — Redoksa lomas un potenciālu tabula

Topic 6; types: Q07, Q14, Q15; coverage: P6-01, P6-02, P6-04.

- **A:** Doti Zn²⁺/Zn un Cu²⁺/Cu E°; oksidētājs un reducētājs

- **B:** Atpazīst oksidēšanos un reducēšanos no elektronu pārneses

- **C:** Bioloģisks donor/akceptor pāris ar dotu reakciju, vienota E°′ konvencija

- **D:** Labot oksidētājs atdod elektronus un nekritiski sajauktus E°/E°′

### FAM-6B — Pusreakcijas dažādās vidēs

Topic 6; types: Q05, Q04; coverage: P6-05, P6-06.

- **A:** MnO₄⁻ + Fe²⁺ skābā vidē → Mn²⁺ un Fe³⁺

- **B:** MnO₄⁻ + SO₃²⁻ neitrālā vidē → MnO₂ un SO₄²⁻

- **C:** MnO₄⁻ + SO₃²⁻ stipri bāziskā vidē → MnO₄²⁻ un SO₄²⁻

- **D:** Dotā pusreakcijā izlaists H₂O/OH⁻/e⁻; atjauno bilanci

### FAM-6C — Titrēšana un koncentrācija

Topic 6; types: Q17, Q02, Q08, Q10; coverage: P6-07, P6-08.

- **A:** 0,02000 mol/L KMnO₄, 18,60 mL, 25,00 mL Fe²⁺ skābā vidē

- **B:** 0,01500 mol/L KMnO₄, 20,00 mL, 25,00 mL Fe²⁺ skābā vidē

- **C:** No dotas Fe²⁺ koncentrācijas atrod vajadzīgo titranta tilpumu

- **D:** Biretes divi nolasījumi, pārtitrēšanas kļūdas virziens un dotais beigu punkta kritērijs

### FAM-6D — Nernsts un nepamatots secinājums

Topic 6; types: Q02, Q13, Q16; coverage: P6-03.

- **A:** E°=0,340 V, Cu²⁺/Cu, a(Cu²⁺)=0,0100, T=298,15 K

- **B:** Tas pats pāris, a(Cu²⁺)=0,100; salīdzini E ar E°

- **C:** Dots Q un n; E=E°−(RT/nF)ln Q, constants given

- **D:** Labot apgrieztu Q vai pieņēmumu, ka E° vienmēr nosaka virzienu

### FAM-7A — Likums un metodes lietojums

Topic 7; types: Q03, Q06, Q15; coverage: P7-01, P7-02.

- **A:** A=εlc: l=1,00 cm, c=2,00×10⁻⁵ mol/L, ε=12500 L/(mol cm)

- **B:** No dotas A, ε un l atrod c

- **C:** Nosauc A, T, ε, l un c un salīdzini A ar %T kā papildtreniņu

- **D:** Pamatot spektrofotometrijas lietojumu dotam absorbējošam analītam

### FAM-7B — Kalibrēšanas grafiks

Topic 7; types: Q11, Q12, Q09; coverage: P7-03, P7-04.

- **A:** γ=0/0,004/0,008/0,012 mg/mL; A=0,010/0,210/0,410/0,610

- **B:** c=0/2/4/6×10⁻⁵ mol/L; A=0,020/0,220/0,420/0,620

- **C:** Dota taisne ar nenulles nogriezni; interpolē, neatmet nogriezni

- **D:** Punkti ar izlecēju; atšķir diagnostiku no pamatojuma dzēst punktu

### FAM-7C — Nezināms paraugs un atšķaidījums

Topic 7; types: Q17, Q02; coverage: P7-04.

- **A:** A=0,350, A=50γ+0,010; atšķaidījums 5,00; sākotnēji 25,00 mL

- **B:** A=0,410, A=50γ+0,010; atšķaidījums 2,00; sākotnēji 10,00 mL

- **C:** Dota sākotnējā koncentrācija un atšķaidījums; paredzi A diapazonā

- **D:** Atrod n no masas ar doto M, nesaistot γ ar molāro c bez M

### FAM-7D — Kalibrēšanas derīgums un laboratorijas soļi

Topic 7; types: Q13, Q08, Q16, Q18; coverage: P7-05.

- **A:** A ārpus standartu diapazona; izplāno atšķaidījumu un atkārtotu mērījumu

- **B:** R² tuvu 1, bet nobīdīts tukšais paraugs; labo secinājumu

- **C:** 440 nm ir protokola iestatījums; nav dots spektrs lokālas virsotnes pierādījumam

- **D:** Tukšais paraugs, kivetes orientācija un mērījuma secība ar dotu procedūru

## 4. Fourteen worked design examples

All givens are explicit pedagogical inputs. They are not claims about clinical product labels, measured laboratory data or official answer keys. Numerical derivations are checked by tools/verify_preparation.py; scientific/source approval and usability remain pending. SVG/graph prompts here specify future authoring and do not claim that figures exist.

### EX01 — Masas nezūdamība (Topic 1, Q02)

Sabalansē Mg + O₂ → MgO. Magnija masa ir 4,80 g, M(Mg)=24,0 g/mol, M(MgO)=40,0 g/mol; skābeklis ir pārākumā. Aprēķini MgO masu.

**Expected answer / criteria:** {"coefficients": [2, 1, 2], "n_Mg_mol": 0.2, "m_MgO_g": 8.0, "display_lv": "8,00 g"}

**Rubric:** Bilance 2:1:2: 1 pt (auto); n=m/M: 1 pt (auto-or-method); n(MgO)=n(Mg): 1 pt (manual); m=8,00 g ar vienību: 1 pt (auto).

**Variant:** 4,80 g vietā 7,20 g → 12,0 g; strukturāls variants: dota MgO masa, jāatrod Mg masa.

### EX02 — Joni un elektrolīts (Topic 1, Q15)

Izskaidro, kāpēc NaCl ūdens šķīdums vada elektrisko strāvu; uzraksti disociāciju. Salīdzini ar glikozes šķīdumu.

**Expected answer / criteria:** {"equation": "NaCl → Na⁺ + Cl⁻", "criteria": ["šķīdumā kustīgi joni", "Na⁺ un Cl⁻", "glikoze dotajā modelī neveido jonus"]}

**Rubric:** Disociācija un lādiņi: 1 pt (structured-auto); Kustīgu jonu loma: 1 pt (self-or-human); Glikozes salīdzinājums: 1 pt (self-or-human).

**Variant:** MgCl₂ variants prasa divus Cl⁻; nav pieņemama tikai vielas nosaukuma nomaiņa.

### EX03 — Birete (Topic 2, Q10)

Biretes iedaļa ir 0,1 mL, vērtības pieaug uz leju. SVG specifikācijā sākuma menisks ir 2,15 mL un beigu menisks 18,40 mL. Nolasījumu pieraksti līdz 0,01 mL; aprēķini izlietoto tilpumu.

**Expected answer / criteria:** {"initial_mL": 2.15, "final_mL": 18.4, "delivered_mL": 16.25, "display_lv": "16,25 mL"}

**Rubric:** Pareizs skalas virziens un nolasījumi: 2 pt (auto); Vbeigu−Vsākuma ar vienību: 1 pt (auto); Divas decimālvietas pēc dotās instrukcijas: 1 pt (auto).

**Variant:** 0,35→21,70 mL dod 21,35 mL; cits variants maina skalas iedaļu. Šis ir SVG authoring piemērs, attēls vēl nav izveidots.

### EX04 — Vienības un precizitāte (Topic 2, Q01)

Pārvērt 0,00450 kg miligramos, saglabājot trīs zīmīgos ciparus. Atsevišķi noapaļo 2,50×3,42 pēc reizināšanas noteikuma.

**Expected answer / criteria:** {"mass_mg": 4500, "mass_display": "4,50×10³ mg", "product": 8.55, "significant_figures": 3}

**Rubric:** Vienību ķēde kg→g→mg: 1 pt (auto); Nepārprotami trīs zīmīgie cipari: 1 pt (auto); Reizinājums 8,55: 1 pt (auto).

**Variant:** Pārvērst 2,50×10⁻⁶ mol mikromolos; cits variants pārbauda saskaitīšanas decimālvietas.

### EX05 — Koncentrācija no iesvara (Topic 3, Q02)

2,922 g NaCl izšķīdina un papildina līdz 250,0 mL gatavā šķīduma. Dots M=58,44 g/mol. Aprēķini n un c.

**Expected answer / criteria:** {"n_mol": 0.05, "c_mol_L": 0.2, "display_lv": "n=0,05000 mol; c=0,2000 mol/L"}

**Rubric:** n=m/M: 1 pt (auto-or-method); V=0,2500 L: 1 pt (auto); c=n/V: 1 pt (auto-or-method); Rezultāts un zīmīgie cipari: 1 pt (auto).

**Variant:** Maini iesvaru uz 1,461 g pie tā paša V → c=0,1000 mol/L.

### EX06 — Atšķaidījums (Topic 3, Q08)

No c₁=0,500 mol/L šķīduma jāpagatavo 100,0 mL šķīduma ar c₂=0,0500 mol/L. Atrodi V₁ un apraksti procedūru.

**Expected answer / criteria:** {"V1_mL": 10.0, "display_lv": "10,0 mL", "sequence": ["nomēra V₁ ar piemērotu pipeti", "pārnes mērkolbā", "pievieno šķīdinātāju un sajauc", "papildina līdz 100,0 mL atzīmei", "samaisa"]}

**Rubric:** c₁V₁=c₂V₂: 1 pt (auto-or-method); V₁=10,0 mL: 1 pt (auto); Atšķaida līdz gala tilpumam: 1 pt (self-or-human); Pamatota mērtrauku secība: 1 pt (partial-order).

**Variant:** c₁=0,200, c₂=0,0200, V₂=250,0 mL → V₁=25,0 mL; precīzi 90,0 mL ūdens nav universāla instrukcija.

### EX07 — Gibsa enerģija (Topic 4, Q02)

ΔH=40,0 kJ/mol, ΔS=150 J/(mol K), T=298 K. Aprēķini ΔG; secini par patvaļīgumu dotajos apstākļos. Pieņemot ΔH un ΔS nemainīgus, atrodi robežtemperatūru.

**Expected answer / criteria:** {"delta_G_kJ_mol": -4.7, "boundary_T_K": 266.6666666667, "spontaneous": true, "note": "Patvaļīgs šajos apstākļos; nav secinājuma par ātrumu."}

**Rubric:** ΔS=0,150 kJ/(mol K): 1 pt (auto); ΔG=40,0−298×0,150: 1 pt (auto-or-method); ΔG=−4,7 kJ/mol: 1 pt (auto); Pareizs secinājums un T robeža ar pieņēmumu: 2 pt (mixed).

**Variant:** ΔH=−20,0 kJ/mol un ΔS=−80,0 J/(mol K) → pie 298 K ΔG=3,84 kJ/mol; mainās temperatūras nosacījuma virziens.

### EX08 — Kalorimetrija un zīme (Topic 4, Q17)

Izolēta kalorimetra vienkāršotajā modelī šķīduma masa ir 100,0 g, cₚ=4,18 J/(g K), ΔT=+5,00 K. Kalorimetra siltumietilpību ignorē. Aprēķini šķīduma un reakcijas siltumu, izskaidro zīmi.

**Expected answer / criteria:** {"q_solution_J": 2090, "q_reaction_J": -2090, "process": "eksotermisks"}

**Rubric:** q=mcₚΔT: 1 pt (auto-or-method); q šķīdumam=+2,09 kJ: 1 pt (auto); q reakcijai=−2,09 kJ: 1 pt (auto); Sistēmas un apkārtnes skaidrojums: 1 pt (self-or-human).

**Variant:** ΔT=−3,00 K → q šķīdumam=−1,25 kJ, reakcijai=+1,25 kJ.

### EX09 — Pusperiods (Topic 5, Q12)

Dota pirmās pakāpes eliminācijas modeļa tabula: t/min=0,30,60,90; m/mg=80,40,20,10. Nosaki t½, k un atlikušo masu 90 minūtēs. Šis ir mācību modelis.

**Expected answer / criteria:** {"half_life_min": 30, "k_min_inverse": 0.023104906018664842, "m90_mg": 10}

**Rubric:** No grafika/tabulas t½=30 min: 1 pt (auto); k=ln2/t½≈0,0231 min⁻¹: 1 pt (auto); m90=10 mg: 1 pt (auto); Nosauc pirmās pakāpes pieņēmumu: 1 pt (self-or-human).

**Variant:** t½=20 min un m₀=64 mg → pēc 60 min 8 mg; nulltās pakāpes variants prasa citu modeli.

### EX10 — Katalizatora profils (Topic 5, Q13)

Enerģijas profila ordināta ir kJ/mol: reaģenti 20, produkti −10, nekatalizētais maksimums 100, katalizētais 60. Nosaki abas tiešās reakcijas aktivācijas enerģijas un ΔH. Izlabo apgalvojumu, ka katalizators padara ΔH negatīvāku.

**Expected answer / criteria:** {"Ea_uncatalysed_kJ_mol": 80, "Ea_catalysed_kJ_mol": 40, "delta_H_kJ_mol": -30, "correction": "Katalizators nodrošina citu ceļu ar zemāku barjeru; sākuma un beigu stāvokļa starpība nemainās."}

**Rubric:** Abas barjeras attiecībā pret reaģentiem: 2 pt (auto); ΔH=−30 kJ/mol: 1 pt (auto); Pamatots apgalvojuma labojums: 1 pt (self-or-human).

**Variant:** Maini produktu enerģiju uz 50: ΔH kļūst pozitīvs, katalizatora princips paliek tas pats.

### EX11 — Pusreakcijas un titrēšana (Topic 6, Q05)

Skābā vidē MnO₄⁻ reaģē ar Fe²⁺, veidojot Mn²⁺ un Fe³⁺. Uzraksti pusreakcijas un kopējo jonu vienādojumu. 25,00 mL Fe²⁺ paraugam vajag 18,60 mL 0,02000 mol/L KMnO₄. Aprēķini c(Fe²⁺).

**Expected answer / criteria:** {"reduction": "MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O", "oxidation": "Fe²⁺ → Fe³⁺ + e⁻", "net": "MnO₄⁻ + 8H⁺ + 5Fe²⁺ → Mn²⁺ + 4H₂O + 5Fe³⁺", "n_MnO4_mol": 0.000372, "c_Fe_mol_L": 0.0744, "display_lv": "0,07440 mol/L"}

**Rubric:** Atomu un lādiņa bilance pusreakcijās: 2 pt (structured-auto); Elektronu attiecība 1:5: 1 pt (auto); n titrantam un n Fe²⁺: 1 pt (auto); c Fe²⁺ un vienība: 1 pt (auto).

**Variant:** c titrantam=0,01500 mol/L, V=20,00 mL, Vpar=25,00 mL → cFe=0,06000 mol/L; bāziska vide ir atsevišķi pārskatāms ģimenes variants.

### EX12 — Nernsta vienādojums (Topic 6, Q13)

Cu²⁺ + 2e⁻ → Cu(s); E°=0,340 V, a(Cu²⁺)=0,0100, a(Cu)=1, T=298,15 K. Dots decimālā logaritma koeficients 0,05916 V. Izmanto E=E°−(0,05916/n)lg Q. Atrodi Q un E, izlabo apgrieztu Q.

**Expected answer / criteria:** {"Q": 100, "n": 2, "E_V": 0.28084, "display_lv": "E≈0,281 V"}

**Rubric:** Q=1/a(Cu²⁺)=100: 1 pt (auto); n=2 un lg100=2: 1 pt (auto); E=0,28084 V pirms noapaļošanas: 1 pt (auto); Pamatots Q labojums: 1 pt (self-or-human).

**Variant:** a(Cu²⁺)=0,100 → E=0,31042 V; cita pusreakcija prasa citu Q un n.

### EX13 — Kalibrēšana ar nenulles nogriezni (Topic 7, Q11)

Kalibrēšanas dati: γ/(mg/mL)=0;0,004;0,008;0,012 un A=0,010;0,210;0,410;0,610. Izvēlies asis un iegūsti taisni. Parauga A=0,350. Aprēķini γ mērītajā šķīdumā.

**Expected answer / criteria:** {"slope_mL_mg": 50, "intercept": 0.01, "gamma_measured_mg_mL": 0.0068, "display_lv": "0,00680 mg/mL"}

**Rubric:** Asis ar γ un A, vienības un piemērots mērogs: 1 pt (manual-or-coordinate); Punkti un A=50γ+0,010: 2 pt (auto); γ=(A−0,010)/50: 1 pt (auto-or-method); Interpolācija diapazonā: 1 pt (self-or-human).

**Variant:** A=0,410 → γ=0,00800 mg/mL; nogriežņa piespiedu nulle dod kļūdainu variantu diagnozei.

### EX14 — Atšķaidīts paraugs un masa (Topic 7, Q17)

Izmanto EX13 kalibrēšanas taisni. Pirms mērījuma sākotnējo paraugu atšķaidīja 5,00 reizes. Sākotnējā parauga tilpums ir 25,00 mL, M=376,36 g/mol. No A=0,350 atrodi sākotnējo γ, masu un n.

**Expected answer / criteria:** {"gamma_original_mg_mL": 0.034, "mass_mg": 0.85, "n_mol": 2.2584759273036453e-06}

**Rubric:** Atjauno γ ar atšķaidījuma reizinātāju: 1 pt (auto); m=γV=0,850 mg: 1 pt (auto); mg→g un n=m/M≈2,26×10⁻⁶ mol: 1 pt (auto); Nosauc mērīto un sākotnējo šķīdumu: 1 pt (self-or-human).

**Variant:** A=0,410, atšķaidījums 2,00 un V₀=10,00 mL → m=0,160 mg. Gala testā šīs apakšdaļas apvieno vienā gadījumā, neizmanto EX13 atbildi kā redzamu mājienu.

## 5. Grading rules and feedback

Record earned points per criterion: model/formula, conversion, substitution, result, unit/precision and interpretation where applicable. Each criterion is awarded once. A propagated arithmetic error can retain later method credit if the declared dependency allows it and the result is internally consistent; it cannot earn correctness credit for the original wrong value. Do not punish the same unit error again in every downstream field. Clamp 0 ≤ earned ≤ maximum, do not award negative points, and do not use point totals as an official pass/fail.

Separate machine-checked, learner-confirmed, human-reviewed and pending points. Show a range [confirmed, confirmed + pending] until written work is assessed. A blank response earns zero, an unsubmitted response remains unsubmitted until finalization, and an unreviewed explanation remains pending. Matching a few keywords never establishes that a chemical explanation is correct. Provide a criterion checklist and an example answer for self-assessment only after submission in exam mode.

Parse decimal comma and decimal point, Unicode minus, scientific notation and an explicit unit whitelist into a typed quantity. Require an unambiguous grammar; reject mixed/ambiguous separators, NaN, infinity and code. Never eval a submitted string. Apply dimensional conversion before comparing values using per-item absolute/relative tolerances. Round for display only; check requested significant figures as a separate criterion, including trailing zeros and exact conversion factors.

Check a fixed species list with independent atom/charge/electron counts. Accept proportionate coefficients as balanced but reserve the lowest-integer-ratio criterion. Do not promise arbitrary free-text equation or symbolic equivalence; unsupported but valid alternative methods enter rubric review.

Practice mode: optional graduated hint (concept → formula → first step), then solution and a variant. Hints are recorded and mark the attempt assisted; a retry has its own record. Exam mode: no hints, answer feedback or answer search; finalize then expose results in a separate view. Offline client HTML cannot prevent inspection of bundled answers and is not a secure proctoring system.

## 6. Accessible interactions

Use keyboard-operable selects or up/down controls as alternatives to dragging; a labeled coordinate table as an alternative to plot placement; explicit field labels for coefficients and units; visible focus, error summaries and text descriptions for SVG. An assessment alternative must preserve the required inference: a scale diagram is not accompanied by its answer in alt text before submission. Keep source data/answer annotations for review in a separate answer artifact. No color-only coding or mandatory timed drag gesture.

## 7. Bank release gates

Every released instance needs a unique ID, coverage IDs, source locator and hash, reviewed givens, response schema, key, rubric, bounds, seed, tolerance, difficulty estimate, time estimate and alternate input route. Every outcome needs a reviewed instance; each A/B/C form needs seven-topic and required-slot coverage, at least eight response types, 100 points, 170 minutes work plus 10 review, no repeated instance/family origin and no answer disclosure. These are future gates; the current preparation verifies the plan and copies only.
