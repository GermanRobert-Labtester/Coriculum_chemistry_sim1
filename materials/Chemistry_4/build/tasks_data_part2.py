# ruff: noqa: E501
"""Detailed specifications for Tasks 06 through 10."""

TASKS_PART2 = """
---

### TASK-06: Bioenergetics of ATP Hydrolysis, Phosphoryl Group Transfer Potential & Coupling Mechanics

#### 1. Strategic Objective & Domain Scope
Demystify the chemical and biological nature of adenosine triphosphate (ATP) hydrolysis. Permanently eradicate the widespread biochemical misconception that ATP's phosphoanhydride bonds "store energy" like a physical spring or battery, replacing it with the structural and quantum mechanical realities of electrostatic repulsion relief, resonance stabilization, and superior hydration solvation of products. Distinguish between thermodynamic standard state ($\\Delta G^\\circ$), biochemical standard state ($\\Delta G^{\\circ\\prime}$ at $\\text{pH } 7$), and actual intracellular free energy ($\\Delta G_{\\text{šūnā}}$). Formulate the concept of Phosphoryl Group Transfer Potential and quantify energetic coupling mechanisms. Directly resolves **S22**.

#### 2. Deep Domain & Pedagogical Rationale
- **The "High-Energy Macroergic Bond" Myth (S22)**: Medical students enter university firmly believing that "breaking high-energy bonds in ATP releases energy". In introductory physics and chemistry, *breaking any chemical bond always requires an input of energy* (bond dissociation energy is strictly positive, $\\Delta H > 0$). Energy is released *only* when new, more thermodynamically stable bonds are formed in the products. The lecture notes (K p.16) correctly attempt to dispel this myth by stating that the energy comes from the overall reaction, but immediately reintroduce confusion by citing values like «$-61.0\\text{ kJ/mol}$» for $\\text{ATP} + 2\\text{H}_2\\text{O} \\to \\text{AMP} + \\text{PP}_i$ (which looks like a mechanical doubling of $2 \\times -30.5\\text{ kJ/mol}$, whereas the accepted biochemical $\\Delta G^{\\circ\\prime}$ for pyrophosphate cleavage is $\\approx -45.6\\text{ kJ/mol}$).
- **The Three Structural Pillars of ATP Exergonicity**:
  1. *Electrostatic Repulsion Relief*: At physiological $\\text{pH } 7.4$, ATP carries four localized negative charges ($\\text{ATP}^{4-}$). The dense cluster of negative charges on the tri-phosphate chain exerts massive destabilizing Coulombic repulsion. Hydrolysis separates these charges into $\\text{ADP}^{3-}$ and $\\text{HPO}_4^{2-}$ (inorganic phosphate, $P_i$), drastically lowering electrostatic stress.
  2. *Resonance Stabilization of Products*: In ATP, the bridging oxygen atom between adjacent phosphorus atoms cannot simultaneously participate in resonance with both phosphoryl groups. In free inorganic phosphate ($P_i$), the negative charge is fully delocalized across all four oxygen atoms over multiple equivalent resonance forms, substantially lowering the electronic ground-state energy.
  3. *Solvation Energy*: The separated products $\\text{ADP}^{3-}$ and $P_i$ interact more favorably with water dipoles, releasing a significant enthalpy of hydration relative to the more sterically strained $\\text{ATP}^{4-}$ molecule.
- **Biochemical Standard State ($\\Delta G^{\\circ\\prime}$) vs Cellular $\\Delta G$**: Standard thermodynamic tables assume $[\\text{H}^+] = 1\\text{ M}$ ($\text{pH } 0$), an absurdity in human biology where $\\text{pH } 7.4$ prevails and $[\text{H}^+] \\approx 4 \\times 10^{-8}\\text{ M}$. Biochemical tables use $\\Delta G^{\\circ\\prime}$ ($\text{pH } 7.0$, $[\\text{H}_2\\text{O}] = 55.5\\text{ M}$, $[\\text{Mg}^{2+}] = 1\\text{ mM}$). Furthermore, inside a functioning human cardiomyocyte or erythrocyte, concentrations are far from $1\\text{ M}$ ($[\\text{ATP}] \\approx 5\\text{ mM}$, $[\\text{ADP}] \\approx 0.5\\text{ mM}$, $[P_i] \\approx 5\\text{ mM}$). Using $\\Delta G = \\Delta G^{\\circ\\prime} + RT \\ln \\frac{[\\text{ADP}][P_i]}{[\\text{ATP}]}$, the actual in-cell driving force is $\\Delta G_{\\text{šūnā}} \\approx -50\\text{ to }-55\\text{ kJ/mol}$, nearly double the textbook $-30.5\\text{ kJ/mol}$!
- **Phosphoryl Group Transfer Potential**: ATP occupies an intermediate position on the biological thermodynamic scale. Compounds like phosphoenolpyruvate (PEP, $-61.9\\text{ kJ/mol}$), 1,3-bisphosphoglycerate (1,3-BPG, $-49.4\\text{ kJ/mol}$), and phosphocreatine ($-43.1\\text{ kJ/mol}$) have higher group transfer potentials and can phosphorylate ADP to ATP during substrate-level phosphorylation. ATP in turn phosphorylates glucose (glucose-6-phosphate, $-13.8\\text{ kJ/mol}$) to trap it within the cell.

#### 3. Workspace Skills Applied & Technical Synergy
- `blueprint-spec-sheet`: Formats the phosphorylated compound hierarchy into an aligned thermodynamic datasheet with reaction schemes, $\\Delta G^{\\circ\\prime}$ values, and clinical physiological functions.
- `synoptic-matrix-architect`: Implements the interactive reaction coupling ledger showing how unfavorable anabolic reactions are driven by exergonic phosphate transfer.
- `cognitive-deload-auditor`: Visually balances the electrostatic and resonance contributions to avoid dense text explanations.

#### 4. Features & Interactive Add-on Innovations
- **Interactive ATP Phosphoryl Transfer & Reaction Coupling Simulator**:
  - Allows students to select an endergonic biological reaction (e.g., Glucose phosphorylation to Glucose-6-P, $\\Delta G^{\\circ\\prime} = +13.8\\text{ kJ/mol}$; Glutamate + $\\text{NH}_3$ to Glutamine, $\\Delta G^{\\circ\\prime} = +14.2\\text{ kJ/mol}$).
  - Pairs the reaction with ATP hydrolysis ($\\Delta G^{\\circ\\prime} = -30.5\\text{ kJ/mol}$) via a common phosphorylated intermediate.
  - Generates the net equation and calculates the overall exergonic driving force (e.g., $+13.8 + (-30.5) = -16.7\\text{ kJ/mol}$), illustrating why the coupled process proceeds spontaneously.
- **In-Cell Cellular Free Energy Calculator**:
  - Sliders for intracellular $[\\text{ATP}]$, $[\\text{ADP}]$, and $[P_i]$ in millimolar units, computing the real-time cellular driving force $\\Delta G_{\\text{šūnā}}$ and comparing it against standard $\\Delta G^{\\circ\\prime}$.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Reaction Coupling Waterfall (`coupling`)**:
  - Upgrades `figures.py` `OUT["coupling"]` (`viewBox="0 0 820 400"`).
  - Plots Step 1 (uphill anabolic step, $+30.0\\text{ kJ/mol}$), Step 2 (ATP hydrolysis, $-30.5\\text{ kJ/mol}$), and the Net Sum ($-0.5\\text{ kJ/mol}$) crossing below the bold red zero line.
  - Adds a callout warning that standard states must be identical when adding real physiological pairs.
- **Brand-New Vector Plate: ATP Chemical Structure & Electrostatic Charge Relief**:
  - Precision 2D chemical structure of adenosine-5'-triphosphate showing the adenine base, ribose ring, and the tri-phosphate tail.
  - Color-codes the localized negative formal charges on terminal oxygens with repulsion vectors.
  - Side-by-side comparison with the resonance hybrid of free orthophosphate ($P_i$), illustrating delocalized $\\pi$-electron density across all four P–O bonds.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Chapter 11 in `part_10_12.html`, deconstructing the "macroergic bond" metaphor, explaining resonance and electrostatic repulsion, and updating the $\\Delta G^{\\circ\\prime}$ table.
- **Substep 2**: Detail the mathematical distinction between $\\Delta G^\\circ$ ($\text{pH } 0$), $\\Delta G^{\\circ\\prime}$ ($\text{pH } 7$), and in-cell $\\Delta G_{\\text{šūnā}}$ ($-50\\text{ to }-55\\text{ kJ/mol}$).
- **Substep 3**: Update `build/figures.py` to regenerate the coupling waterfall plate and create the structural charge relief vector graphic.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Chemical Mechanics of ATP Hydrolysis**
  - *Substep A.1*: Quote K p.16's accurate statement that the bond itself is not the energy source; expand with an explicit 3-part structural breakdown: electrostatic repulsion, resonance delocalization, and hydration enthalpy.
  - *Substep A.2*: Provide the complete chemical equation with explicit ionic charges: $\\text{ATP}^{4-} + \\text{H}_2\\text{O} \\to \\text{ADP}^{3-} + \\text{HPO}_4^{2-} + \\text{H}^+$, showing the generation of a proton at physiological pH.
  - *Substep A.3*: Add a critical note on the role of magnesium ions ($\\text{Mg}^{2+}$): in vivo, ATP exists as $\\text{MgATP}^{2-}$, where $\\text{Mg}^{2+}$ coordinates with the $\\beta$ and $\\gamma$ phosphate oxygens to partially shield charge and orient the terminal group for nucleophilic attack.
- **Subtask B: Phosphoryl Group Transfer Potential Cascade**
  - *Substep B.1*: Build a comprehensive hierarchy table of phosphorylated metabolites ranked by $\\Delta G^{\\circ\\prime}$: Phosphoenolpyruvate ($-61.9\\text{ kJ/mol}$), 1,3-Bisphosphoglycerate ($-49.4\\text{ kJ/mol}$), Phosphocreatine ($-43.1\\text{ kJ/mol}$), ATP to ADP ($-30.5\\text{ kJ/mol}$), Glucose-1-phosphate ($-20.9\\text{ kJ/mol}$), Fructose-6-phosphate ($-15.9\\text{ kJ/mol}$), Glucose-6-phosphate ($-13.8\\text{ kJ/mol}$), Glycerol-3-phosphate ($-9.2\\text{ kJ/mol}$).
  - *Substep B.2*: Explain the physiological role of phosphocreatine in skeletal muscle as an immediate temporal buffer of ATP via creatine kinase: $\\text{Phosphocreatine} + \\text{ADP} \\rightleftharpoons \\text{Creatine} + \\text{ATP}$ ($\\Delta G^{\\circ\\prime} = -43.1 - (-30.5) = -12.6\\text{ kJ/mol}$).
  - *Substep B.3*: Clarify the pyrophosphate cleavage pathway: $\\text{ATP} + \\text{H}_2\\text{O} \\to \\text{AMP} + \\text{PP}_i$ ($\\Delta G^{\\circ\\prime} \\approx -45.6\\text{ kJ/mol}$), followed by ubiquitous inorganic pyrophosphatase ($\\text{PP}_i + \\text{H}_2\\text{O} \\to 2P_i$, $\\Delta G^{\\circ\\prime} \\approx -19\\text{ kJ/mol}$), driving fatty acid and amino acid activation forward irreversibly (overall $\\approx -65\\text{ kJ/mol}$). Correct the notes' simplistic $-61.0\\text{ kJ/mol}$ entry.
- **Subtask C: Reaction Coupling Mathematics & Biological Transduction**
  - *Substep C.1*: Formulate the thermodynamic principle of Hess's Law applied to free energies of coupled reactions: $\\Delta G_{\\text{kop}} = \\Delta G_1 + \\Delta G_2$.
  - *Substep C.2*: Provide the worked clinical example of hexokinase in glycolysis: Glucose + $P_i \\to$ G-6-P + $\\text{H}_2\\text{O}$ ($\\Delta G^{\\circ\\prime} = +13.8\\text{ kJ/mol}$); coupled with ATP hydrolysis ($\\Delta G^{\\circ\\prime} = -30.5\\text{ kJ/mol}$), the net reaction Glucose + ATP $\\to$ G-6-P + ADP has $\\Delta G^{\\circ\\prime} = -16.7\\text{ kJ/mol}$, rendering glucose entry into glycolysis essentially irreversible.
  - *Substep C.3*: Connect thermodynamic coupling to mechanical motor proteins (myosin power stroke during actin sliding in muscle contraction) and primary active membrane transport ($\text{Na}^+/\\text{K}^+$-ATPase maintaining resting membrane potential against steep electrochemical gradients).

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. In-cell ATP free energy check: At $T = 310.15\\text{ K}$ ($37^\\circ\\text{C}$), with $[\\text{ATP}] = 5.0\\text{ mM}$, $[\\text{ADP}] = 0.5\\text{ mM}$, $[P_i] = 5.0\\text{ mM}$:
     $\\Delta G = -30.5 + \\frac{8.314 \\cdot 310.15}{1000} \\ln\\left(\\frac{0.0005 \\cdot 0.005}{0.005}\\right) = -30.5 + 2.5786 \\cdot \\ln(0.0005) = -30.5 + 2.5786 \\cdot (-7.6009) = -30.5 - 19.60 = -50.10\\text{ kJ/mol}$.
  2. Coupled hexokinase step: $\\Delta G^{\\circ\\prime} = +13.8 + (-30.5) = -16.7\\text{ kJ/mol}$.
- **Acceptance Gate**:
  - The term *makroerģiskā saite* is explicitly identified as an outdated metaphor; breaking bonds is strictly explained as requiring energy.
  - Table 11 clearly delineates $\\Delta G^\\circ$ vs $\\Delta G^{\\circ\\prime}$ vs $\\Delta G_{\\text{šūnā}}$.

---

### TASK-07: Food Calorimetry, Metabolic Energy Budgets & Respiratory Quotient Energetics

#### 1. Strategic Objective & Domain Scope
Establish a clear, rigorous, and clinically applicable framework for nutritional calorimetry and human metabolic thermodynamics. Clearly separate the thermochemical calorie ($1\\text{ cal} = 4.184\\text{ J}$ exact) from the dietary Calorie ($1\\text{ kcal} = 1\\text{ Cal} = 4.184\\text{ kJ}$). Correct the profound confusion in the lecture notes regarding constant-volume bomb calorimetry (which measures $\\Delta U = q_V$) versus physiological metabolic oxidation (which occurs at constant pressure, measuring $\\Delta H = q_p$). Differentiate physiological Atwater factors from gross bomb heat of combustion, integrate the Respiratory Quotient ($RQ$), and rationalize the universal metabolic caloric equivalent of oxygen ($21.2\\text{ kJ/L } \\text{O}_2$). Directly resolves **S23** and **S24**.

#### 2. Deep Domain & Pedagogical Rationale
- **Calorie Confusion (S23)**: K p.17 defines the calorie twice and attributes $1\\text{ cal} = 4.184\\text{ J}$ to both the $14.5 \\to 15.5^\\circ\\text{C}$ calorie and general definitions. The $15^\\circ\\text{C}$ calorie is actually $4.1855\\text{ J}$; the value **$4.184\\text{ J}$ is the thermochemical calorie, defined exactly by international agreement in 1929**. Furthermore, everyday nutritional terminology refers to "calories" when it strictly means kilocalories ($\text{kcal}$), often capitalized as $\text{Calorie}$ ($\text{Cal}$). In clinical medicine and dietetics, conflating $\text{cal}$ with $\text{kcal}$ leads to a 1000-fold dosage error in parenteral nutrition formulations!
- **Bomb Calorimeter vs Human Body Energetics (S24)**: K p.17–18 cites the classic numbers «sadedzinot kalorimetrā 1 g tauku: 9 kcal/g, olbaltumvielu 4, ogļhidrātu 4». These are **Atwater physiological factors**, *not* bomb calorimeter values!
  - In a bomb calorimeter, combustion is complete: proteins are oxidized to nitrogen oxides ($\text{NO}_x$), water, and $\text{CO}_2$, yielding gross combustion heat of $\\approx 5.65\\text{ kcal/g}$ ($23.6\\text{ kJ/g}$).
  - In the human body, the nitrogen in proteins cannot be oxidized to $\text{NO}_x$; it is excreted as urea ($(\\text{NH}_2)_2\\text{CO}$), uric acid, and creatinine. Urea still contains combustible chemical energy. Accounting for incomplete nitrogen oxidation and human gastrointestinal digestibility ($92\\text{–}98\\%$), the net physiological yield of protein drops to $4.0\\text{ kcal/g}$ ($16.7\\text{ kJ/g}$).
  - For carbohydrates, gross bomb heat is $4.1\\text{ kcal/g} \\approx 17.2\\text{ kJ/g}$, yielding an Atwater factor of $4.0\\text{ kcal/g}$ ($16.7\\text{ kJ/g}$).
  - For fats, gross bomb heat is $9.45\\text{ kcal/g} \\approx 39.5\\text{ kJ/g}$, yielding an Atwater factor of $9.0\\text{ kcal/g}$ ($37.7\\text{ kJ/g}$).
- **Bomb Calorimeter Constant-Volume Physics**: A bomb calorimeter has a rigid, constant volume ($V = \\text{const} \\implies \\Delta V = 0 \\implies A = 0$). By the First Law, the heat released in a bomb calorimeter is the change in internal energy: $q_V = \\Delta U$. In contrast, metabolism in the human body occurs under constant atmospheric pressure ($p = \\text{const}$), where heat exchange is enthalpy: $q_p = \\Delta H$. The conversion formula is $\\Delta H = \\Delta U + \\Delta n_{\\text{gāzes}}RT$. For glucose combustion ($\text{C}_6\\text{H}_{12}\\text{O}_6(s) + 6\\text{O}_2(g) \\to 6\\text{CO}_2(g) + 6\\text{H}_2\\text{O}(l)$), $\\Delta n_{\\text{gāzes}} = 6 - 6 = 0$, meaning $\\Delta H \\approx \\Delta U$. For palmitic acid, $\\Delta n_{\\text{gāzes}} \\ne 0$, introducing a distinct divergence.
- **Respiratory Quotient ($RQ$) & Oxygen Energetics**: K p.13 introduces the equivalence $1\\text{ L } \\text{O}_2 \\leftrightarrow 21.2\\text{ kJ}$. This is the caloric equivalent of oxygen during pure carbohydrate oxidation ($RQ = \\text{V}_{\\text{CO}_2}/\\text{V}_{\\text{O}_2} = 1.00$). For fats, $RQ \\approx 0.70$ and $1\\text{ L } \\text{O}_2 \\leftrightarrow 19.6\\text{ kJ}$; for proteins, $RQ \\approx 0.80$ and $1\\text{ L } \\text{O}_2 \\leftrightarrow 18.8\\text{ kJ}$. This enables indirect calorimetry in clinical intensive care units (ICU) to measure metabolic rate and fuel utilization in critically ill patients. Notes p.17 cite an unsourced «minimālā dienas enerģija 2680 kcal» without specifying sex, body mass, or physical activity level; this must be contextualized against the standard WHO/Harris-Benedict BMR ($1400\\text{–}1800\\text{ kcal/day}$).

#### 3. Workspace Skills Applied & Technical Synergy
- `blueprint-spec-sheet`: Generates the clinical nutrition energy ledger detailing macronutrient Atwater factors, combustion heats, and $RQ$ metrics.
- `dataviz`: Visualizes the macronutrient energy yield comparison bar chart.
- `lexicon-morphology-weaver`: Explains the etymology of calorimetry (*calor* = heat, *metron* = measure) and the distinction between gross, digestible, and metabolizable energy.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Nutritional Thermodynamics & Indirect Calorimetry Calculator**:
  - Inputs for grams of dietary carbohydrate, fat, and protein consumed.
  - Calculates total caloric intake in both kilocalories and megajoules ($\text{MJ}$).
  - Predicts oxygen consumption in liters, carbon dioxide output in liters, and overall respiratory quotient ($RQ$).
  - Evaluates basal metabolic rate (BMR) coverage against user-specified body mass and physical activity level (PAL).
- **Bomb Calorimeter vs Physiological Yield Inspector**:
  - Interactive comparison toggle showing the fate of protein: complete bomb oxidation ($\text{NO}_x$) versus liver urea cycle excretion.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Bomb Calorimeter Technical Cutaway (`calorimeters`)**:
  - Upgrades `figures.py` `OUT["calorimeters"]` (`viewBox="0 0 900 480"`).
  - Left Panel: Open coffee-cup solution calorimeter with fluid meniscus and immersion sensor.
  - Right Panel: Industrial/laboratory bomb calorimeter with thick steel pressure bomb, sample crucible, ignition wire circuit, pressurized oxygen valve, surrounding water bath, motorized helical stirrer, and precision Beckmann differential thermometer.
  - Labels denote $q_V = \\Delta U$ for the bomb calorimeter vs $q_p = \\Delta H$ for constant-pressure systems.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Section 8.2 and Section 8.3 in `part_6_9.html`, clarifying the exact definitions of thermochemical calories, dietary Calories, and SI joules.
- **Substep 2**: Rebuild the food energy table, explicitly contrasting Atwater physiological factors with gross bomb calorimeter values and explaining nitrogen excretion.
- **Substep 3**: Update `build/figures.py` to regenerate the dual calorimeter vector plate with accurate engineering callouts and thermodynamic state labels.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Calorie Definitions & SI Standardization**
  - *Substep A.1*: Author the definitive calorie reference table: $1\\text{ cal} = 4.184\\text{ J}$ (thermochemical, exact); $1\\text{ kcal} = 1000\\text{ cal} = 4.184\\text{ kJ}$; $1\\text{ Cal} = 1\\text{ kcal} = 4184\\text{ J}$.
  - *Substep A.2*: Add an explicit clinical safety warning callout on the fatal difference between $\\text{cal}$ and $\\text{kcal}$ in clinical nutrition and metabolic rate calculations.
  - *Substep A.3*: Convert the unsourced $2680\\text{ kcal}$ daily requirement into standard SI units ($2680 \\times 4.184 = 11,213\\text{ kJ} \\approx 11.2\\text{ MJ}$), and contextualize it as the Total Daily Energy Expenditure (TDEE) for an active adult male, contrasting it with Basal Metabolic Rate (BMR $\\approx 6.7\\text{–}7.5\\text{ MJ/day}$).
- **Subtask B: Bomb Calorimetry Physics vs Human Metabolic Physiology**
  - *Substep B.1*: Detail the constant-volume condition ($A = 0 \\implies q_V = \\Delta U$) in bomb calorimetry, detailing how the calorimeter constant $C_{\\text{kal}}$ (in $\\text{J/K}$ or $\\text{kJ/K}$) is experimentally determined using certified benzoic acid standards ($\\Delta_c U = -26,434\\text{ J/g}$).
  - *Substep B.2*: Provide the mathematical conversion $\\Delta H = \\Delta U + \\Delta n_{\\text{gāzes}}RT$, and calculate the concrete example of tripalmitin combustion ($\\text{C}_{51}\\text{H}_{98}\\text{O}_6 + 72.5\\text{O}_2 \\to 51\\text{CO}_2 + 49\\text{H}_2\\text{O}$), showing $\\Delta n_{\\text{gāzes}} = 51 - 72.5 = -21.5$.
  - *Substep B.3*: Construct the comparative Atwater table: Carbohydrates ($4\\text{ kcal/g} = 16.7\\text{ kJ/g}$ vs $4.1\\text{ kcal/g}$ bomb); Fats ($9\\text{ kcal/g} = 37.7\\text{ kJ/g}$ vs $9.45\\text{ kcal/g}$ bomb); Proteins ($4\\text{ kcal/g} = 16.7\\text{ kJ/g}$ vs $5.65\\text{ kcal/g}$ bomb); Alcohol ($7\\text{ kcal/g} = 29.3\\text{ kJ/g}$).
- **Subtask C: Indirect Calorimetry & Respiratory Quotient ($RQ$)**
  - *Substep C.1*: Define the Respiratory Quotient $RQ = \\frac{\\dot{V}_{\\text{CO}_2}}{\\dot{V}_{\\text{O}_2}}$ and the Respiratory Exchange Ratio ($RER$).
  - *Substep C.2*: Re-derive the $1\\text{ L } \\text{O}_2 \\leftrightarrow 21.2\\text{ kJ}$ equivalence for glucose: $\\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2 \\to 6\\text{CO}_2 + 6\\text{H}_2\\text{O}$, $\\Delta_c H^\\circ = -2808\\text{ kJ/mol}$. For 6 moles of $\\text{O}_2$, molar volume at standard temperature and pressure ($0^\\circ\\text{C}, 1\\text{ atm}$) is $22.414\\text{ L/mol}$, yielding $V = 6 \\times 22.414 = 134.48\\text{ L}$. Thermal yield per liter = $\\frac{2808\\text{ kJ}}{134.48\\text{ L}} = 20.88\\text{ kJ/L}$; at $25^\\circ\\text{C}$ and $1\\text{ bar}$ ($V_m = 24.79\\text{ L/mol}$), yield per liter $\\approx 18.9\\text{ kJ/L}$. Clarify the origin of the notes' $21.2\\text{ kJ/L}$ figure as physiological carbohydrate oxidation.
  - *Substep C.3*: Detail how an $RQ$ of $0.70$ indicates pure lipid oxidation (e.g., in diabetic ketoacidosis or starvation), while $RQ = 1.00$ indicates carbohydrate burning, and $RQ > 1.00$ indicates active lipogenesis.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. Calorie conversion: $2680\\text{ kcal} \\times 4.184\\text{ kJ/kcal} = 11,213.12\\text{ kJ} = 11.213\\text{ MJ}$.
  2. Atwater meal ledger: $100\\text{ g}$ carbs ($1670\\text{ kJ}$) + $30\\text{ g}$ fat ($1131\\text{ kJ}$) + $40\\text{ g}$ protein ($668\\text{ kJ}$) = $3469\\text{ kJ} = 829.1\\text{ kcal}$.
  3. Oxygen yield check: $\\frac{2808}{6 \\times 22.414} = 20.88\\text{ kJ/L}$.
- **Acceptance Gate**:
  - Atwater factors (4/9/4) are strictly labeled physiological, never gross bomb values.
  - Bomb calorimeter heat is mathematically defined as $q_V = \\Delta U$.

---

### TASK-08: Solution Calorimetry Lab Procedure, Limiting Reagent Detection & Thermogram Extrapolation

#### 1. Strategic Objective & Domain Scope
Transform the treatment of the practical laboratory assignment («Neutralizācijas entalpijas noteikšana», L and LA) into an exemplar of empirical scientific rigor. Solve the limiting reagent stoichiometry definitively ($160.0\\text{ mL } 0.200\\text{ M } \\text{NaOH}$ vs $40.0\\text{ mL } 1.00\\text{ M } \\text{HCl}$), enforce the correct negative sign for exothermic reaction enthalpy ($\\Delta H_r = -52.3\\text{ kJ/mol}$, correcting LA's $+52.3\\text{ kJ/mol}$), complete the four blank lab conclusions with evidence-grounded scientific argumentation, formalize calorimeter heat capacity ($C_{\\text{kal}}$) and heat-leak corrections, and implement graphic cooling extrapolation back to the mixing time $t_0$. Directly resolves **S36**, **S37**, and **S38**.

#### 2. Deep Domain & Pedagogical Rationale
- **The Limiting Reagent Logic**: Students frequently calculate enthalpy per mole using the wrong reagent or total moles. 
  - Base solution: $V_b = 160.0\\text{ mL} = 0.160\\text{ L}$, $c_b = 0.200\\text{ M} \\implies n(\\text{OH}^-) = 0.160 \\times 0.200 = 0.0320\\text{ mol}$.
  - Acid solution: $V_a = 40.0\\text{ mL} = 0.040\\text{ L}$, $c_a = 1.00\\text{ M} \\implies n(\\text{H}^+) = 0.040 \\times 1.00 = 0.0400\\text{ mol}$.
  - Neutralization is $1:1$ stoichiometry ($\\text{H}^+ + \\text{OH}^- \\to \\text{H}_2\\text{O}$). Because $0.0320 < 0.0400$, **$\\text{NaOH}$ is strictly the limiting reagent**! There is an excess of $0.0080\\text{ mol } \\text{HCl}$, which remains unreacted and releases zero neutralization heat. Enthalpy must be computed per mole of limiting reagent ($n_{\\text{lim}} = 0.0320\\text{ mol}$).
- **The Inverted Sign Error (S36)**: In the lab answer key LA p.2, the calculation is written as «$-\\Delta H = q/n = 52.3\\text{ kJ/mol}$», leaving students with the impression that $\\Delta H_r = +52.3\\text{ kJ/mol}$. An acid-base neutralization warms the solution ($\\Delta T = +2.0\\text{ K}$), meaning heat is absorbed by the water ($q_{\\text{šķīdums}} = +1673.6\\text{ J}$). By energy conservation, the chemical system released heat ($q_{\\text{reakcija}} = -1673.6\\text{ J}$), and because the reaction was at constant pressure, $\\Delta H_r = \\frac{q_{\\text{reakcija}}}{n_{\\text{lim}}} = \\frac{-1673.6\\text{ J}}{0.0320\\text{ mol}} = **-52.3\\text{ kJ/mol}**$. Printing a positive enthalpy for an exothermic reaction causes students to fail test questions on basic thermochemistry.
- **The Four Blank Conclusions (S38)**: In the official answer key LA p.3, the four conclusion prompts are left completely blank!
  - *Conclusion 1 (Reaction Nature)*: The neutralization is **exothermic** because $\\Delta H_r < 0$ (experimental $-52.3\\text{ kJ/mol}$, theoretical $-56.19\\text{ kJ/mol}$), and **spontaneous (exergonic)** because $\\Delta G^\\circ < 0$ ($-102.2\\text{ to }-104.1\\text{ kJ/mol}$ course data; $-79.9\\text{ kJ/mol}$ accepted data).
  - *Conclusion 2 (Theoretical Discrepancy)*: The relative experimental deviation is $\\frac{|-52.3 - (-56.19)|}{|-56.19|} \\times 100\\% = **6.92\\%**$.
  - *Conclusion 3 (Error Sources & Direction)*: Experimental $|\\Delta H|$ is $3.89\\text{ kJ/mol}$ *lower* than theory. Primary systematic causes: (1) Heat loss to the surrounding ambient air and outer glass beaker; (2) Ignoring the non-zero heat capacity of the inner beaker, thermometer bulb, and stirrer ($C_{\\text{kal}} \\approx 15\\text{–}25\\text{ J/K}$); (3) Slow thermometer response time; (4) Minor temperature differences between initial acid and base. All four factors systematically lower the measured $\\Delta T$.
  - *Conclusion 4 (Theoretical $\\Delta T$ Prediction)*: To achieve the theoretical enthalpy of $-56.19\\text{ kJ/mol}$, the required temperature rise would be $\\Delta T_{\\text{teor}} = \\frac{0.0320\\text{ mol} \\times 56,190\\text{ J/mol}}{4.184\\text{ J/(g}\\cdot\\text{K)} \\times 200\\text{ g}} = **2.15\\text{ K}**$. Since thermometer resolution is $\\pm 0.1\\text{ K}$ for each reading, the uncertainty on $\\Delta T = 2.0\\text{ K}$ is $u(\\Delta T) = \\sqrt{0.1^2 + 0.1^2} = 0.14\\text{ K} \\approx **7\\%**$, which is of the exact same magnitude as the experimental error!
- **Specific Heat Capacity Terminology (S37)**: The lab manual calls $c = 4.184\\text{ J/(g}\\cdot\\text{K)}$ «siltumkapacitāte». The correct IUPAC and Latvian term is **īpatnējā siltumietilpība** (specific heat capacity, lower-case $c$). Siltumietilpība (heat capacity, capital $C$) has units $\\text{J/K}$.

#### 3. Workspace Skills Applied & Technical Synergy
- `state-scrubber-lab`: Drives the time-scrubber simulating the calorimeter thermogram through baseline, mixing, peak, and cooling.
- `blueprint-spec-sheet`: Formats Table 1 and Table 2 into a completed laboratory data sheet.
- `cognitive-deload-auditor`: Visually balances limiting reagent stoichiometry and error analysis.

#### 4. Features & Interactive Add-on Innovations
- **Virtual Solution Calorimetry Laboratory Simulator (Instrument C Upgrade)**:
  - Sliders for $V_{\\text{base}}$, $c_{\\text{base}}$, $V_{\\text{acid}}$, $c_{\\text{acid}}$, and measured $\\Delta T$.
  - Optional input field for calorimeter constant $C_{\\text{kal}}$ (default $0\\text{ J/K}$, adjustable $0\\text{–}50\\text{ J/K}$).
  - Automatically identifies the limiting reagent, computes $n_{\\text{lim}}$, total mass $m_{\\text{tot}}$, heat released $q$, reaction enthalpy $\\Delta H_r$, percentage error against theoretical $-56.19\\text{ kJ/mol}$, and the ideal $\\Delta T_{\\text{teor}}$.
  - Error budget breakdown: decomposes error into thermometer resolution uncertainty vs thermal leakage.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Calorimeter Temperature-Time Cooling Extrapolation (`trace`)**:
  - Upgrades `figures.py` `OUT["trace"]` (`viewBox="0 0 860 450"`).
  - Plots continuous experimental curve: Pre-period baseline at $T_{\\text{init}} = 295.0\\text{ K}$ ($0\\text{–}40\\text{ s}$), rapid exothermic rise upon mixing at $t = 40\\text{ s}$, peak at $T = 297.15\\text{ K}$, and exponential cooling regime ($t > 60\\text{ s}$).
  - Renders the linear regression extrapolation tangent from the cooling phase back to the exact mixing time $t = 40\\text{ s}$, demonstrating how experimentalists correct for heat loss to determine true $\\Delta T = 2.0\\text{ K}$.
  - Features labeled leader lines and mathematical markers.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Chapter 9 in `part_6_9.html`, formalizing the limiting reagent detection, enforcing $\\Delta H_r = -52.3\\text{ kJ/mol}$, and drafting the four blank conclusions with scientific justifications.
- **Substep 2**: Standardize terminology, replacing *siltumkapacitāte* with *īpatnējā siltumietilpība* for $c = 4.184\\text{ J/(g}\\cdot\\text{K)}$ and formalizing the total mass $m = 160 + 40 = 200\\text{ g}$.
- **Substep 3**: Update `build/figures.py` and `build/instruments.html` to synchronize Instrument C and the thermogram extrapolation plate.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Stoichiometric Limiting Reagent & Sign Formalism**
  - *Substep A.1*: Detail the exact molar calculations: $n(\\text{OH}^-) = 0.160 \\times 0.200 = 0.0320\\text{ mol}$; $n(\\text{H}^+) = 0.040 \\times 1.00 = 0.0400\\text{ mol}$; identify $\\text{OH}^-$ as limiting.
  - *Substep A.2*: State the solution assumptions: density $\\rho = 1.00\\text{ g/mL} \\implies m = 200\\text{ g}$; specific heat capacity $c = 4.184\\text{ J/(g}\\cdot\\text{K)}$.
  - *Substep A.3*: Write the step-by-step energy ledger: $q_{\\text{šķīdums}} = c \\cdot m \\cdot \\Delta T = 4.184 \\cdot 200 \\cdot 2.0 = +1673.6\\text{ J} \\implies \\Delta H_r = -\\frac{1673.6}{0.0320} = -52,300\\text{ J/mol} = **-52.3\\text{ kJ/mol}**$.
- **Subtask B: Synthesis of Conclusions 1–4**
  - *Substep B.1*: Author Conclusion 1: Reaction is exothermic ($\\Delta H_r = -52.3\\text{ kJ/mol} < 0$) and exergonic ($\\Delta G^\\circ = -102.2\\text{ kJ/mol} < 0$), proceeding spontaneously to completion.
  - *Substep B.2*: Author Conclusion 2: Relative error is $\\frac{|-52.3 - (-56.19)|}{56.19} \\times 100\\% = 6.92\\% \\approx 6.9\\%$.
  - *Substep B.3*: Author Conclusions 3 and 4: Systematically categorize error sources lowering $\\Delta T$ (heat loss, $C_{\\text{kal}}$, sensor lag), compute theoretical $\\Delta T_{\\text{teor}} = 2.15\\text{ K}$, and demonstrate that thermometer resolution ($u = 0.14\\text{ K} \\approx 7\\%$) accounts for the deviation.
- **Subtask C: Apparatus Calibration & Heat Leak Extrapolation**
  - *Substep C.1*: Formulate the calorimeter heat capacity equation: $q_{\\text{kop}} = (c_{\\text{šķ}} \\cdot m_{\\text{šķ}} + C_{\\text{kal}}) \\cdot \\Delta T$, showing that with $C_{\\text{kal}} = 20\\text{ J/K}$, $q = 1673.6 + 40 = 1713.6\\text{ J} \\implies \\Delta H_r = -53.55\\text{ kJ/mol}$, reducing error to $4.7\\%$.
  - *Substep C.2*: Explain Newton's Law of Cooling ($\\frac{dT}{dt} = -k(T - T_{\\text{amb}})$) governing the post-reaction cooling trace.
  - *Substep C.3*: Author procedure precautions: why acid must be added rapidly, why stirring must be continuous but gentle, and why baseline temperature must stabilize before mixing.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. Base calorimeter calculation: $q = 4.184 \\times 200 \\times 2.0 = 1673.6\\text{ J}$; $n = 0.032\\text{ mol}$; $\\Delta H_r = -52.300\\text{ kJ/mol}$.
  2. Theoretical $\\Delta T$: $\\frac{0.032 \\times 56190}{4.184 \\times 200} = 2.1488\\text{ K} \\approx 2.15\\text{ K}$.
  3. Corrected for $C_{\\text{kal}} = 20\\text{ J/K}$: $q = (836.8 + 20) \\times 2.0 = 1713.6\\text{ J} \\implies \\Delta H_r = -53.55\\text{ kJ/mol}$.
- **Acceptance Gate**:
  - Enthalpy of reaction is unambiguously negative ($-52.3\\text{ kJ/mol}$).
  - All four conclusion prompts have fully articulated, numbered text blocks.

---

### TASK-09: Resolution of Fundamental Course Discrepancies & Hydronium Ion Inconsistencies

#### 1. Strategic Objective & Domain Scope
Confront, forensically dissect, and pedagogically resolve the severe thermodynamic inconsistencies present within the course laboratory manual (Table 2 in L and LA) and standard thermodynamic tables. Expose the mathematical and physical conflict where the course's tabulated values for hydronium ion formation free energy and entropy yield $\\Delta G^\\circ = -102.2\\text{ to }-104.1\\text{ kJ/mol}$, diverging drastically from the fundamental physical constant of water autoprotolysis ($\\Delta G^\\circ = -RT \\ln K_w = -79.9\\text{ kJ/mol}$). Resolve the photosynthesis aqueous vs gaseous oxygen data trap (U Q5), correct reverse reaction sign drops, and rectify chemical table misprints. Directly resolves **S25**, **S28**, **S33**, **S34**, and **S35**.

#### 2. Deep Domain & Pedagogical Rationale
- **The Hydronium Inconsistency Crisis (S34)**: In laboratory Table 2 (LA p.2), theoretical values are calculated for $\\text{H}_3\\text{O}^+(aq) + \\text{OH}^-(aq) \\to 2\\text{H}_2\\text{O}(l)$:
  - Route 1: $\\Delta_r G^\\circ = \\sum \\nu \\Delta_f G^\\circ(\\text{prod}) - \\sum \\nu \\Delta_f G^\\circ(\\text{react}) = 2(-237.19) - [(-213.28) + (-157.00)] = **-104.10\\text{ kJ/mol}**$.
  - Route 2: $\\Delta_r H^\\circ = 2(-286.00) - [(-285.81) + (-230.00)] = -56.19\\text{ kJ/mol}$.
    $\\Delta_r S^\\circ = 2(69.956) - [(-3.854) + (-10.539)] = +154.305\\text{ J/(mol}\\cdot\\text{K)}$.
    $\\Delta_r G^\\circ = \\Delta_r H^\\circ - T\\Delta_r S^\\circ = -56.19 - 298.15 \\times 0.154305 = **-102.196\\text{ kJ/mol}**$.
  - *The Inconsistency*: The two routes within the course's own table disagree by nearly $2\\text{ kJ/mol}$ ($-104.10$ vs $-102.20\\text{ kJ/mol}$)! 
  - *The Deeper Physical Failure*: In international standard chemistry (NIST / IUPAC), the standard Gibbs free energy for water dissociation ($2\\text{H}_2\\text{O} \\rightleftharpoons \\text{H}_3\\text{O}^+ + \\text{OH}^-$) is fixed by the ion product of water $K_w = 1.00 \\times 10^{-14}$ at $298.15\\text{ K}$. Hence, $\\Delta G^\\circ = -RT \\ln K_w = -8.314 \\times 298.15 \\times \\ln(10^{-14}) = **+79.9\\text{ kJ/mol}**$. The reverse reaction (neutralization) MUST equal **$-79.9\\text{ kJ/mol}$**!
  - *Why Course Data Produces $-102\\text{ to }-104\\text{ kJ/mol}$*: The course authors took formation values for $\\text{H}_3\\text{O}^+$ ($\\Delta_f G^\\circ = -213.28\\text{ kJ/mol}$, $S^\\circ = -3.854\\text{ J/(mol}\\cdot\\text{K)}$) from an obsolete Russian or non-standard reference that did not adhere to the conventional definition of standard hydrogen ion convention ($\Delta_f H^\circ(\text{H}^+, aq) = 0$, $S^\circ(\text{H}^+, aq) = 0$). With standard values ($S^\circ(\text{H}_3\text{O}^+) \\approx 69.9$, $\\Delta_f G^\\circ \\approx -237.1$), $\\Delta_r S^\\circ \\approx +80.5\\text{ J/(mol}\\cdot\\text{K)}$ and $\\Delta_r G^\\circ = -56.2 - 298.15 \\times 0.0805 = **-80.2\\text{ kJ/mol}**$, matching $K_w$ perfectly!
  - *Pedagogical Strategy*: If students write $-79.9\\text{ kJ/mol}$ on the lab worksheet, they will be marked wrong by an automated grader expecting the course's $-102.20\\text{ kJ/mol}$. The master document must teach students to use the course numbers on the worksheet, openly expose the mathematical discrepancy in a dedicated Discrepancy Callout, explain the real physical chemistry, and flag the issue for the lecturer (**V**).
- **The Photosynthesis Oxygen Enthalpy Trap (S28)**: In seminar problem U Q5, the table header labels all data as «$\\Delta H^\\circ_r, S^\\circ_r$» (using the reaction subscript $r$ instead of formation $f$). Crucially, **oxygen is listed with $\\Delta H = -11.715\\text{ kJ/mol}$ and $S^\\circ = 110.876\\text{ J/(mol}\\cdot\\text{K)}$**! For pure gaseous $\\text{O}_2(g)$ in its standard state, $\\Delta_f H^\\circ \\equiv 0$ and $S^\\circ = 205.15\\text{ J/(mol}\\cdot\\text{K)}$. The numbers in U Q5 are for **dissolved aqueous oxygen $\\text{O}_2(aq)$**! If a student correctly assumes $\\text{O}_2$ is a gas and sets $\\Delta_f H^\\circ = 0$, their calculated enthalpy shifts by $+70.3\\text{ kJ}$, changing the answer from $+2805.3\\text{ kJ}$ to $+2875.6\\text{ kJ}$. State symbols are completely absent in the problem sheet.
- **Reverse Reaction Sign Drop (S35)**: In LA p.2, the reverse reaction free energy is written as «$\\Delta G^\\circ_{\\text{pretreakcijai}} = |102.196|\\text{ kJ/mol}$». Dropping the sign into an absolute value strip destroys thermodynamic meaning. The reverse reaction (autoprotolysis) is non-spontaneous and endergonic, possessing an unambiguous **$+102.196\\text{ kJ/mol}$** (course data) or $+79.9\\text{ kJ/mol}$ (NIST data). Furthermore, the key writes «$T = 273.15 + 250\\text{ C}$» instead of $25^\\circ\\text{C}$!
- **Table Data Typos (S25, S33)**: K p.19 duplicates $\\Delta H$ into the $\\Delta G$ column for $\\text{CO}_2(g)$ ($-393.5$ instead of $-394.4\\text{ kJ/mol}$); lists $\\text{H}_2\\text{O}(g)$ with $-288.6$ (should be $-228.6\\text{ kJ/mol}$); prints $\\text{N}_2\\text{O}_4$ as «dislāpekļa dioksīds» (tetraoxide); and LA p.2 misprints $2 \\times (-273.19)$ instead of $-237.19$.

#### 3. Workspace Skills Applied & Technical Synergy
- `synoptic-matrix-architect`: Implements the dual-track Course vs IUPAC/NIST discrepancy comparison matrix.
- `tufte-margin-scholar`: Places side-by-side scholarly marginalia explaining the Russian thermodynamic reference origins without disrupting the main study narrative.
- `lexicon-morphology-weaver`: Clarifies ion nomenclature (oxonium vs hydronium, dinitrogen tetraoxide).

#### 4. Features & Interactive Add-on Innovations
- **Thermodynamic Discrepancy & Handbook Cross-Check Inspector**:
  - An interactive comparative panel allowing students to toggle between "Course Exam Key Data" and "IUPAC / NIST International Standards".
  - Displays side-by-side ledgers for the neutralization reaction, highlighting exact numerical discrepancies and providing pre-formatted text for student inquiries to professors.
- **Phase-State Discrepancy Detector**:
  - A diagnostic tool showing the effect of state symbols on thermodynamic sums, proving why using $\\text{O}_2(aq)$ vs $\\text{O}_2(g)$ shifts reaction enthalpy by $70.3\\text{ kJ/mol}$.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Water Autoprotolysis & Neutralization Thermodynamic Cycle**:
  - A precision thermodynamic cycle diagram comparing the Course Data Pathway ($\\Delta G^\\circ = -102.20\\text{ kJ/mol}$) against the NIST/IUPAC Equilibrium Pathway ($\\Delta G^\\circ = -RT \\ln K_w = -79.9\\text{ kJ/mol}$).
  - Visually demonstrates how the choice of $\\text{H}_3\\text{O}^+(aq)$ standard state creates an unclosed thermodynamic cycle of $+22.3\\text{ kJ/mol}$.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Insert the permanent **Discrepancy Block** in Section 9.2 in `part_6_9.html`, providing both course and international numbers while guiding students on how to pass the lab test.
- **Substep 2**: Audit and correct all data typos in Section 5.3 and Chapter 16 (Table 2 and Table 3), documenting S25, S28, S33, S34, and S35 in the master defect register.
- **Substep 3**: Update `build/calc.py` to assert mathematical parity across both data pathways, and draft formal questions for the course director in Section 16.4 («Jautājumi docētājam»).

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Lab Table 2 Forensic Discrepancy Resolution**
  - *Substep A.1*: Document the internal arithmetic discrepancy: $\\Sigma \\Delta_f G^\\circ = -104.10\\text{ kJ/mol}$ vs $\\Delta H - T\\Delta S = -102.20\\text{ kJ/mol}$ (a difference of $1.90\\text{ kJ/mol}$).
  - *Substep A.2*: Document the external physical discrepancy against $K_w = 10^{-14}$: $\\Delta G^\\circ = -79.9\\text{ kJ/mol}$; explicitly prove why standard formation values for aqueous ions require the convention $\\Delta_f G^\\circ(\\text{H}^+, aq) \\equiv 0$.
  - *Substep A.3*: Author an exam-safety notice: instruct students to report $-102.20\\text{ kJ/mol}$ (or $-104.10\\text{ kJ/mol}$) on RSU worksheet forms, while adding an asterisk referencing the physical discrepancy.
- **Subtask B: Seminar Task U Q5 Aqueous State Trap Audit**
  - *Substep B.1*: Audit U Q5 data table: demonstrate that $\\Delta_f H^\\circ = -11.715\\text{ kJ/mol}$ and $S^\\circ = 110.876\\text{ J/(mol}\\cdot\\text{K)}$ correspond to dissolved oxygen $\\text{O}_2(aq)$, while glucose ($-1263.78\\text{ kJ/mol}$, $269.45\\text{ J/(mol}\\cdot\\text{K)}$) is aqueous.
  - *Substep B.2*: Provide both calculations in Chapter 12: Route A (using sheet's aqueous numbers, yielding $+2805.27\\text{ kJ}$ and $+2570.4\\text{ kJ}$); Route B (using gaseous oxygen $\\Delta_f H^\\circ = 0$, yielding $+2875.56\\text{ kJ}$).
  - *Substep B.3*: Explain why aquatic photosynthesis (phytoplankton, cyanobacteria) operates in the aqueous phase, rationalizing the sheet's chosen dataset.
- **Subtask C: Table Typos & Nomenclature Rectification**
  - *Substep C.1*: Correct LA p.2's reverse reaction line: restore the positive sign $\\Delta G^\\circ_{\\text{pretreakcijai}} = +102.196\\text{ kJ/mol}$ and fix the temperature typo ($273.15 + 25^\\circ\\text{C} = 298.15\\text{ K}$, not $250^\\circ\\text{C}$).
  - *Substep C.2*: Correct K p.19: set $\\Delta_f G^\\circ(\\text{CO}_2, g) = -394.38\\text{ kJ/mol}$; $\\Delta_f G^\\circ(\\text{H}_2\\text{O}, g) = -228.57\\text{ kJ/mol}$; rename $\\text{N}_2\\text{O}_4$ from «dislāpekļa dioksīds» to **dislāpekļa tetraoksīds**.
  - *Substep C.3*: Standardize chemical phase notation across all chapters to international brackets: $(s), (l), (g), (aq)$, eliminating Russian-origin abbreviations like $(c), (c.v.), (šķ.)$.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. Lab Route 1: $2(-237.19) - (-213.28 - 157.00) = -474.38 - (-370.28) = -104.10\\text{ kJ/mol}$.
  2. Lab Route 2: $-56.19 - 298.15 \\times 0.154305 = -56.19 - 46.006 = -102.196\\text{ kJ/mol}$.
  3. Physical water autoprotolysis: $-8.314462618 \\times 298.15 \\times \\ln(1.00 \\times 10^{-14}) / 1000 = +79.897\\text{ kJ/mol} \\approx +79.9\\text{ kJ/mol}$.
  4. Photosynthesis aqueous trap difference: $6 \\times (-11.715) = -70.29\\text{ kJ}$.
- **Acceptance Gate**:
  - The Discrepancy Block is prominently displayed in Chapter 9.
  - Reverse reaction free energy is explicitly $+102.2\\text{ kJ/mol}$, never an absolute value.
  - Chemical phase notation is 100% standardized to $(s), (l), (g), (aq)$.

---

### TASK-10: Algorithmic & Pedagogical Solution Engine for Seminar Problem Set (U Q1–Q6)

#### 1. Strategic Objective & Domain Scope
Engineer an exhaustive, algorithmic, step-by-step solution suite for all six problem sets in `4_SEM_Termodinamika_uzdevumi.pdf` (U Q1 through U Q6). Currently, the course sources provide zero answers or solution keys for these tasks. Provide fully verified calculation ledgers, identify underlying curricular traps (kJ vs J, aqueous vs gaseous states, kinetic barriers, non-physical crossover temperatures), draft concise two-sentence spontaneity verdicts, and generate isomorphic transfer variants with fresh numerical parameters for active student mastery. Directly resolves **S28**, **S29**, and **S30**.

#### 2. Deep Domain & Pedagogical Rationale
- **The Zero-Answer Void**: The seminar sheet `4_SEM_Termodinamika_uzdevumi.pdf` contains six complex, multi-part thermodynamic problems. The department provides students with no worked solutions and no official answer key. Without authoritative guidance, students reinforce flawed habits (such as subtracting $\\Delta S$ in Joules directly from $\\Delta H$ in kiloJoules).
- **Deep Dissection of the 6 Seminar Tasks**:
  - **U Q1 (Methane Reforming / Syngas)**: $\\text{CH}_4(g) + \\text{H}_2\\text{O}(g) \\to 3\\text{H}_2(g) + \\text{CO}(g)$. Given $\\Delta H = +210\\text{ kJ/mol}$, $\\Delta S = +216\\text{ J/(K}\\cdot\\text{mol)}$. At $298.15\\text{ K}$, $\\Delta G = 210 - 298.15 \\times 0.216 = +145.60\\text{ kJ/mol}$ (endothermic, non-spontaneous). Crossover: $T_{\\text{cross}} = 210,000 / 216 = 972.2\\text{ K} = 699.1^\\circ\\text{C}$. Spontaneous above $\\approx 972\\text{ K}$. The classic trap: subtracting $210 - 298 \\times 216 = -64,158\\text{ kJ}$, obtaining an absurdly wrong exergonic result!
  - **U Q2 (Cold Pack Dissolution)**: $\\text{NH}_4\\text{NO}_3(s) \\to \\text{NH}_4^+(aq) + \\text{NO}_3^-(aq)$. $\\Delta_r H^\\circ = +28.05\\text{ kJ/mol}$, $\\Delta_r S^\\circ = +108.72\\text{ J/(K}\\cdot\\text{mol)}$. At $298.15\\text{ K}$, $\\Delta G = 28.05 - 298.15 \\times 0.10872 = -4.36\\text{ kJ/mol}$. Spontaneous, endothermic (entropy-driven dissolution, cooling the pack). Crossover: $T_{\\text{cross}} = 258.0\\text{ K} = -15.1^\\circ\\text{C}$. Below $-15.1^\\circ\\text{C}$, $\\text{NH}_4\\text{NO}_3$ will not dissolve spontaneously.
  - **U Q3 (Dipeptide Condensation)**: $\\text{Leu}(s) + \\text{Gly}(s) \\to \\text{Leu-Gly}(s) + \\text{H}_2\\text{O}(l)$. $\\Delta_r H = +21\\text{ kJ/mol}$, $\\Delta_r S = +22\\text{ J/(K}\\cdot\\text{mol)}$. At $298.15\\text{ K}$, $\\Delta G = +14.44\\text{ kJ/mol}$ (endothermic, endergonic). The crucial teaching point: this is a peptide synthesis where $\\Delta S > 0$! Furthermore, the crossover temperature $T_{\\text{cross}} = 21,000 / 22 = 954.5\\text{ K} = 681.4^\\circ\\text{C}$ is biologically meaningless because peptide bonds pyrolyze and decompose far below this temperature. Synthesis in vivo requires ATP coupling.
  - **U Q4 (Ammonium Nitrate Decomposition & Safety)**: $\\text{NH}_4\\text{NO}_3(s) \\to 2\\text{H}_2\\text{O}(g) + \\text{N}_2\\text{O}(g)$. $\\Delta G^\\circ = 2(-229) + 104 - (-184) = -170.0\\text{ kJ/mol}$. The reaction is highly exergonic at $25^\\circ\\text{C}$, yet ammonium nitrate is a stable commercial solid! This proves definitively that thermodynamic feasibility ($\Delta G < 0$) does not imply instantaneous reaction. The reaction has a large activation energy $E_a$, requiring heating ($t^\\circ\\text{C}$ indicated over arrow), and represents an explosive hazard (Beirut port explosion context).
  - **U Q5 (Aqueous Photosynthesis)**: $6\\text{HCO}_3^- + 6\\text{H}_3\\text{O}^+ \\to \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2 + 6\\text{H}_2\\text{O}$. Using sheet's aqueous numbers: $\\Delta_r H = +2805.27\\text{ kJ}$, $\\Delta_r S = +787.63\\text{ J/K}$, $\\Delta G = +2570.45\\text{ kJ}$. Strongly endothermic and endergonic, driven by solar photon absorption ($h\\nu$).
  - **U Q6 (Six Comprehensive Reaction Types)**:
    - R1: Barium sulfate precipitation ($\\Delta H = -44.65\\text{ kJ}$, $\\Delta S = +90.03\\text{ J/K}$, $\\Delta G = -71.49\\text{ kJ}$; Case 1, spontaneous at all $T$).
    - R2: Alumina dissolution in sulfuric acid ($\\Delta H = +110.96\\text{ kJ}$, $\\Delta S = +337.95\\text{ J/K}$, $\\Delta G = +10.20\\text{ kJ}$; Case 3, non-spontaneous at $298\\text{ K}$, spontaneous above $328.3\\text{ K} = 55.2^\\circ\\text{C}$).
    - R3: Ammonia oxidation ($\\Delta H = -906.22\\text{ kJ}$, $\\Delta S = +179.65\\text{ J/K}$, $\\Delta G = -959.78\\text{ kJ}$; Case 1, spontaneous at all $T$).
    - R4: Ethanol combustion ($\\Delta H = -1409.21\\text{ kJ}$, $\\Delta S = -260.58\\text{ J/K}$, $\\Delta G = -1331.52\\text{ kJ}$; Case 2, spontaneous below $T_{\\text{cross}} = 5408\\text{ K}$, physically meaningless crossover).
    - R5: Sodium in water ($\\Delta H = -366.64\\text{ kJ}$, $\\Delta S = -15.42\\text{ J/K}$, $\\Delta G = -362.04\\text{ kJ}$; Case 2, spontaneous below $T_{\\text{cross}} = 23,777\\text{ K}$).
    - R6: Antacid reaction of alum and sodium bicarbonate ($\\Delta H = +37.63\\text{ kJ}$, $\\Delta S = +1021.31\\text{ J/K}$, $\\Delta G = -266.87\\text{ kJ}$; Case 3, endothermic yet spontaneous at $298\\text{ K}$ driven by 6 moles of $\\text{CO}_2$ gas, $T_{\\text{cross}} = 36.8\\text{ K} = -236.3^\\circ\\text{C}$).

#### 3. Workspace Skills Applied & Technical Synergy
- `blueprint-spec-sheet`: Formats each problem ledger with five explicit columns: Substance, State, Stoichiometric $\\nu$, Standard Enthalpy $\\Delta_f H^\\circ$, Standard Entropy $S^\\circ$.
- `synoptic-matrix-architect`: Constructs the comprehensive comparative ledger for U Q6 reactions.
- `cognitive-deload-auditor`: Implements the 3-step structured problem-solving architecture: Given $\\to$ Execution Ledger $\\to$ 2-Sentence Verdict.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Problem Transfer & Drill Generator**:
  - A dynamic module generating isomorphic versions of U Q1–Q6 with randomized numerical values (e.g., varying $\\Delta H$ and $\\Delta S$ by $\\pm 15\\%$) to provide infinite self-testing practice.
  - Interactive validation checking intermediate steps (e.g., checking if the student converted $\\text{J}$ to $\\text{kJ}$ before subtracting).
- **Physical Validity Flag Indicator**:
  - Automatically flags calculated crossover temperatures that exceed boiling, decomposition, or plasma thresholds (e.g., flagging R4's $5408\\text{ K}$ and R5's $23,777\\text{ K}$ as unphysical).

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Comprehensive 6-Reaction Comparative Vector Chart**:
  - Plots all six U Q6 reactions on unified thermodynamic coordinates.
  - Shows signed bars for $\\Delta H$, $T\\Delta S$, and $\\Delta G$ side by side with the prominent red zero line.
  - Visually illustrates why R6 is spontaneous despite being endothermic (the giant positive $T\\Delta S$ bar overwhelms $\\Delta H$).

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author the complete, unrounded mathematical ledgers for all six tasks (U Q1 through U Q6) in Chapter 12 of `part_10_12.html`.
- **Substep 2**: Add explicit two-sentence verdicts and «Kāpēc šādi» explanations for every task, highlighting data caveats (S28, S29, S30).
- **Substep 3**: Update `build/calc.py` to assert that every printed value matches automated code recalculation to the exact decimal precision.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Synthesis Problems (U Q1, U Q2, U Q3)**
  - *Substep A.1*: Solve U Q1 with full tabular ledger: $\\Delta H = +210\\text{ kJ/mol}$, $\\Delta S = +0.216\\text{ kJ/(mol}\\cdot\\text{K)}$, $\\Delta G = +145.60\\text{ kJ/mol}$, $T_{\\text{cross}} = 972.2\\text{ K}$. Include the unit trap warning.
  - *Substep A.2*: Solve U Q2 with full tabular ledger: $\\Delta_r H^\\circ = +28.05\\text{ kJ/mol}$, $\\Delta_r S^\\circ = +108.72\\text{ J/(mol}\\cdot\\text{K)}$, $\\Delta G(298.15\\text{ K}) = -4.36\\text{ kJ/mol}$, $T_{\\text{cross}} = 258.0\\text{ K}$; compute equilibrium constant $K = e^{-\\Delta G^\\circ/RT} = 5.8$.
  - *Substep A.3*: Solve U Q3 with full tabular ledger: $\\Delta_r H = +21\\text{ kJ/mol}$, $\\Delta_r S = +22\\text{ J/(mol}\\cdot\\text{K)}$, $\\Delta G = +14.44\\text{ kJ/mol}$; explain the synthesis counterexample and why biological cells must couple this reaction with ATP.
- **Subtask B: Complex Biochemical & Safety Tasks (U Q4, U Q5)**
  - *Substep B.1*: Solve U Q4: $\\Delta G^\\circ = 2(-229) + 104 - (-184) = -170\\text{ kJ/mol}$; author the safety discussion detailing kinetic stability versus thermodynamic instability.
  - *Substep B.2*: Solve U Q5 using the sheet's aqueous dataset: $\\Delta_r H = +2805.27\\text{ kJ}$, $\\Delta_r S = +787.63\\text{ J/K}$, $\\Delta G = +2570.45\\text{ kJ}$; explain the bioenergetics of light absorption.
  - *Substep B.3*: Provide the gaseous oxygen alternative comparison for U Q5, explaining the $+70.3\\text{ kJ}$ shift and warning students of the sheet's lack of phase labels.
- **Subtask C: The Six Reaction Ledger (U Q6.1–Q6.6)**
  - *Substep C.1*: Format all six reactions into a precision synoptic ledger table with columns for Reaction, $\\Delta_r H$, $\\Delta_r S$, $\\Delta_r G(298\\text{ K})$, Thermodynamic Case, Spontaneity Verdict, and $T_{\\text{cross}}$.
  - *Substep C.2*: Provide explicit notes on physical validity for each crossover temperature: note that R2's $328.3\\text{ K}$ ($55.2^\\circ\\text{C}$) is physically achievable in solution, whereas R4's $5408\\text{ K}$ and R5's $23,777\\text{ K}$ are far beyond molecular existence.
  - *Substep C.3*: Calculate the internal energy change for R4: $\\Delta n_{\\text{gāzes}} = 2 - 4 = -2 \\implies \\Delta U = \\Delta H - \\Delta n_{\\text{gāzes}}RT = -1409.21 - (-2) \\cdot 8.314 \\times 10^{-3} \\cdot 298.15 = -1404.25\\text{ kJ}$.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Verbatim Course Question Wording (`4_SEM_Termodinamika_uzdevumi.pdf`)**:
  - **U Q1 (Anchor `#ch12-1`, Concept `PROB.Q1`)**: «1. Sintēzes gāze ir viena no nozīmīgākajām ķīmiskās rūpniecības izejvielām. Tā ir gāzu maisījums, kas satur mainīgu daudzumu oglekļa monoksīda un ūdeņraža. To sauc arī par ūdens gāzi vai ģeneratorgāzi. Sintēzes gāzi iegūst, karsējot oglekli saturošu kurināmo, pievadot nepietiekamu daudzumu skābekļa, lai varētu notikt degšana un pievadot ūdens tvaiku (lai veidotos ūdeņradis). CH4 (g) + H2O (g) → 3H2 (g) + CO (g). Šajā reakcijā, ΔH = +210 kJ mol-1 un ΔS = +216 J K−1mol-1. Izmantojot termodinamiskos lielumus, seciniet, vai reakcija ir patvaļīga vai nav patvaļīga, ja temperatūra ir 298 K. Ja reakcija nav patvaļīga, tad piedāvājiet temperatūru, kurā reakcija kļūst patvaļīga.»
  - **U Q2 (Anchor `#ch12-2`, Concept `PROB.Q2`)**: «2. Aprēķiniet ΔH° un ΔS° dotajai reakcijai: NH4NO3(s) → NH4+ (aq) + NO3- (aq). Izmantojot aprēķinātos entalpijas un entropijas lielumus, aprēķiniet ΔG 25oC un seciniet par reakcijas iespējamību.»
  - **U Q3 (Anchor `#ch12-3`, Concept `PROB.Q3`)**: «3. Dipeptīds veidojas no aminoskābēm Leicīna un Glicīna. Aprēķiniet ΔGo298K dipeptīda veidošanās reakcijai! Lei(s) + Gly(s) → Lei-Gly(s) + H2O(l). Nosakiet reakcijas patvaļīgumu! Nosakiet, vai reakcija ir eksotermiska vai endotermiska?»
  - **U Q4 (Anchor `#ch12-4`, Concept `PROB.Q4`)**: «4. Anestēzijā izmantojamā slāpekļa(I) oksīda N2O iegūšana vēsturiski notika, sadalot amonija nitrātu saskaņā ar vienādojumu: NH4NO3(s) --t°C--> 2H2O(g) + N2O(g). Aprēķiniet šīs reakcijas ΔG°, ja ΔG°(NH4NO3(c)) = -184 kJ/mol, ΔG°(N2O(g)) = 104 kJ/mol un ΔG°(H2O(g)) = -229 kJ/mol! Vai dotā reakcija standartapstākļos ir iespējama?»
  - **U Q5 (Anchor `#ch12-5`, Concept `PROB.Q5`)**: «5. Aprēķiniet ΔHr, ΔSr, ΔGr un siltuma daudzumu Q hidrogenkarbonāta asimilācijai ūdenī zaļajos augos, kas notiek fotosintēzes procesā standarta apstākļos (298,15 K). Fotosintētiskajā reakcijas centrā reakcija notiek saskaņā ar vienādojumu: 6HCO3- + 6H3O+ --hv--> C6H12O6+6O2+6H2O. Nosakiet, vai reakcija ir eksotermiska vai endotermiska? Nosakiet, vai reakcija ir enderģiska vai ekserģiska ?»
  - **U Q6 (Anchor `#ch12-6`, Concept `PROB.Q6`)**: «6. Aprēķiniet ΔHr, ΔSr, ΔGr un siltuma daudzumu Q dotajām reakcijām standartapstākļos (298,15 K), izmantojot tabulas datus! 1) BaCl2(c) + Na2SO4 (aq) → BaSO4 (c) + 2NaCl(aq); 2) Al2O3 (c) + 3H2SO4 (aq) → Al2(SO4)3 (c)+ 3H2O(l); 3) 4NH3 (g) + 5O2 (g) → 6H2O(g) + 4NO(g); 4) C2H5OH (g) + 3O2 (g) → 2CO2 (g) + 3H2O(l); 5) 2Na(c) + 2H2O(l) → 2NaOH(aq) + H2 (g); 6) Al2(SO4)3 (c) + 6NaHCO3 (c) → 3Na2SO4 (aq) + 2Al(OH)3 (c) + 6CO2 (g).»

- **Problem Mapping & Model Specification Ledger (C03–C06)**:
  - **U1**: Concept `PROB.Q1`. Knowns: $\\Delta H = +210\\text{ kJ/mol}$, $\\Delta S = +216\\text{ J/(K}\\cdot\\text{mol)}$. Model: Isobaric, ideal gas, linear $\\Delta C_p \\approx 0$. Valid range: $373\\text{ K}$ to $\\sim 1100\\text{ K}$; $T_{\\text{cross}} = 972.2\\text{ K}$ ($699.1^\\circ\\text{C}$) is physically achievable in industrial reforming.
  - **U2**: Concept `PROB.Q2`. Knowns: Table values for $\\text{NH}_4\\text{NO}_3(s)$, $\\text{NH}_4^+(aq)$, $\\text{NO}_3^-(aq)$. Model: Dilute solution ($a=1\\text{ mol/L}$), $\\Delta C_p \\approx 0$. Valid range: Eutectic freezing boundary ($\sim 256\\text{ K}$) to $373\\text{ K}$; $T_{\\text{cross}} = 258.0\\text{ K}$ ($-15.1^\\circ\\text{C}$) lies near solvent freezing limit.
  - **U3**: Concept `PROB.Q3`. Knowns: Table values for $\\text{Leu}(s)$, $\\text{Gly}(s)$, $\\text{Leu-Gly}(s)$, $\\text{H}_2\\text{O}(l)$. Model: Solid condensation yielding liquid water. Valid range: $T_{\\text{cross}} = 954.5\\text{ K}$ is biologically fictitious; requires biological ATP coupling in vivo.
  - **U4**: Concept `PROB.Q4`. Knowns: Formation $\\Delta_f G^\\circ$ values. Model: Standard gas evolution. Valid range: Kinetically metastable at $298\\text{ K}$ due to activation barrier $E_a$; thermal initiation requires $t > 200^\\circ\\text{C}$; explosive risk.
  - **U5**: Concept `PROB.Q5`. Knowns: 5 species from course sheet table. Model: Photo-driven endergonic synthesis ($h\\nu$). Valid range: Physiological aqueous conditions $273\\text{--}320\\text{ K}$.
  - **U6**: Concept `PROB.Q6`. Knowns: 6 reactions R1–R6. Model: 4 thermodynamic cases. Valid range: R2 $328.3\\text{ K}$ is physically achievable in solution; R4 ($5408\\text{ K}$) and R5 ($23,777\\text{ K}$) are unphysical plasma limits; R6 ($36.8\\text{ K}$) is cryogenic, meaning spontaneous at all liquid aqueous temperatures.

- **Positive Regression Vector (C03–C06)**:
  - *Clause*: U5 result strictly follows labelled gas/aqueous state input.
  - Aqueous input: $\\text{O}_2(aq) \\implies \\Delta_r H = +2805.27\\text{ kJ}$, $\\Delta_r G = +2570.44\\text{ kJ}$.
  - Gaseous input: $\\text{O}_2(g) \\implies \\Delta_r H = +2875.56\\text{ kJ}$, $\\Delta_r G = +2472.23\\text{ kJ}$.
  - Net positive shift: $\\Delta(\\Delta_r H) = 6 \\times 11.715 = +70.29\\text{ kJ}$.

- **Negative & Boundary Fixtures (C03–C06)**:
  - *Negative Fixture (Invalid Phase or Impossible Sign Rejected)*:
    - Rejecting hybrid mixed-phase error: combining $\\Delta_f H^\\circ(\\text{O}_2, g) = 0$ with $S^\\circ(\\text{O}_2, aq) = 110.876\\text{ J/K}$ yields unphysical $\\Delta_r G = +2640.73\\text{ kJ}$.
    - Rejecting unit confusion: subtracting unscaled Joules gives erroneous $\\Delta G = -64,158\\text{ kJ/mol}$ for U1.
    - Rejecting impossible temperature claims: unphysical crossovers ($5408\\text{ K}$, $23,777\\text{ K}$, $36.8\\text{ K}$) are explicitly flagged as non-operational limits.
  - *Boundary Condition (No Precision Beyond Source Data)*:
    - Number of decimals in reported results strictly respects source precision (2 decimal places for U1, U2, U5; whole numbers / 1 decimal for U3, U4).

- **Test Vectors**:
  1. U Q1: $\\Delta G = 210 - 298.15 \\times 0.216 = +145.600\\text{ kJ/mol}$; $T_{\\text{cross}} = 972.22\\text{ K}$.
  2. U Q2: $\\Delta G = 28.05 - 298.15 \\times 0.10872 = -4.365\\text{ kJ/mol}$; $T_{\\text{cross}} = 258.00\\text{ K}$.
  3. U Q3: $\\Delta G = 21 - 298.15 \\times 0.022 = +14.441\\text{ kJ/mol}$; $T_{\\text{cross}} = 954.55\\text{ K}$.
  4. U Q4: $\\Delta G = -458 + 104 + 184 = -170.00\\text{ kJ/mol}$.
  5. U Q5: $\\Delta_r H = +2805.27\\text{ kJ}$; $\\Delta_r S = +787.63\\text{ J/K}$; $\\Delta G = +2570.45\\text{ kJ}$.
  6. U Q6: R1 ($-71.49\\text{ kJ}$), R2 ($+10.20\\text{ kJ}$), R3 ($-959.78\\text{ kJ}$), R4 ($-1331.52\\text{ kJ}$), R5 ($-362.04\\text{ kJ}$), R6 ($-266.87\\text{ kJ}$).
- **Acceptance Gate**:
  - All six seminar problems have complete mathematical ledgers.
  - Every calculation is verified by `build/calc.py` with zero numerical divergence.
"""
