# ruff: noqa: E501
"""Detailed specifications for Tasks 01 through 05."""

TASKS_PART1 = """
## 2. Exhaustive Deep-Dive Specifications for Tasks 01 through 20

---

### TASK-01: Thermodynamic Sign Conventions, First Law Formalism & Process Ledger Standardization

#### 1. Strategic Objective & Domain Scope
Eliminate the pervasive sign confusion and conceptual ambiguities surrounding heat ($Q$, $q$), work ($A$, $w$), internal energy ($U$), and enthalpy ($H$) across the course materials. Establish an uncompromising, mathematically rigorous, and clinically contextualized First Law framework that bridges the classical Latvian course convention ($Q = \\Delta U + A$) with modern IUPAC standards ($\\Delta U = q + w$), while decisively purging obsolete terminology like *siltumsaturs* (heat content). Directly rectifies source defects **S1**, **S2**, and **S3**.

#### 2. Deep Domain & Pedagogical Rationale
In first-year medical chemistry, sign conventions are the single greatest failure point for students. 
- **The Ambiguity of Symbol $Q$ (S1)**: In the course lecture notes (K p.2–3), equations (2) and (4) define $Q$ as heat *absorbed* by the system ($Q = \\Delta U + p\\Delta V = \\Delta H$), whereas on p.3 equation (6) suddenly writes $Q = -\\Delta H$, representing heat *released*. In laboratory worksheet LA p.1, $q_{\\text{šķīdums}} = c \\cdot m \\cdot \\Delta T$ represents heat absorbed by the calorimeter solution, which equals $-q_{\\text{reakcija}}$. When seminar tasks U Q5 and U Q6 demand «aprēķināt siltuma daudzumu $Q$», students are left entirely blind as to whether a positive or negative quantity is expected.
- **The Isothermal Ideal Gas Fallacy (S2)**: Notes p.3 state that in an isothermal process ($Q = A$), «vienīgā iespēja palielināt iekšējo enerģiju ir pastrādāt darbu». This is fundamentally wrong: for an ideal gas, internal energy $U$ depends solely on temperature ($U = f(T)$); hence in an isothermal process, $\\Delta U = 0$, meaning internal energy does not change at all, let alone increase!
- **The "Heat Content" (*Siltumsaturs*) Anachronism (S3)**: Enthalpy is defined on K p.3 as «sistēmas iekšējā enerģija konstantā spiedienā» and called *siltumsaturs*. This is physically false: $H \\equiv U + pV$. Heat is a path-dependent boundary flux, not a state function stored within a system.
- **Medical Relevance**: In human metabolic physiology, the First Law governs the basal metabolic rate (BMR), dietary caloric intake, mechanical work performed by skeletal muscle, and heat dissipated to maintain core homeothermy ($37^\\circ\\text{C}$). Conflating work done *by* muscle ($A > 0$) with work done *on* the body leads to fatal errors in physiological energy balance equations.

#### 3. Workspace Skills Applied & Technical Synergy
- `blueprint-spec-sheet`: Formats the First Law sign definitions into an engineering-grade specification ledger with dedicated parameter boxes, unit dimensions, and mathematical boundaries.
- `synoptic-matrix-architect`: Constructs the 4-process state-variable transformation matrix (isochoric, isobaric, isothermal, adiabatic).
- `impeccable`: Implements the high-contrast typographic hierarchy for process equations using MathML and tabular numerals.

#### 4. Features & Interactive Add-on Innovations
- **Interactive First-Law Sign-Mirror Sandbox**: A reactive toggle allowing students to view calculations simultaneously in Course Convention ($Q = \\Delta U + A$, where $A = p\\Delta V$ is work done by system) and IUPAC Convention ($\\Delta U = q + w$, where $w = -p\\Delta V$ is work done on system), displaying live directional arrows for heat flux and volume work.
- **Process Path Energy Ledger**: An interactive calculator where students input initial state ($p_1, V_1, T_1$) and choose an expansion path (isobaric, isochoric, isothermal, adiabatic), outputting exact values for $\\Delta U$, $Q$, and $A$ with immediate sign feedback.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Thermodynamic Process $p-V$ Indicator Diagram**:
  - Replaces static bulleted text with a high-precision multi-pathway $p-V$ indicator diagram (`viewBox="0 0 860 480"`).
  - Plots four distinct process lines originating from a common state $(p_0, V_0)$: isobaric horizontal expansion, isothermal hyperbolic expansion ($pV = \\text{const}$), adiabatic steep expansion ($pV^\\gamma = \\text{const}$), and isochoric vertical depressurization.
  - Features hatched SVG polygon areas under each curve corresponding directly to mechanical work $A = \\int p\\,dV$.
  - Explicitly renders the zero-work vertical line for isochoric processes ($A = 0$, $\\Delta U = Q_V$).

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Standardize the universal Sign-Convention Ledger in Chapter 1 of the master document, establishing unambiguous definitions for $Q$, $q_p$, $Q_{\\text{izd}}$, $A$, and $w$.
- **Substep 2**: Refactor Section 3.2 (Pirmais likums) in `part_top.html` to eliminate the isothermal ideal-gas fallacy (S2) and rewrite the four-process energy transformation ledger.
- **Substep 3**: Update `build/figures.py` and `build/calc.py` to generate the new SVG $p-V$ indicator diagram and mathematically re-verify all First Law sample computations.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Universal Sign Ledger & Notation Normalization**
  - *Substep A.1*: Audit all occurrences of symbol $Q$ across `part_top.html`, `part_6_9.html`, and `part_10_12.html`; explicitly replace standalone $Q$ with $q_p$ (absorbed heat at constant pressure) or $Q_{\\text{izd}} = -\\Delta H$ (released reaction heat).
  - *Substep A.2*: Construct the comparative Course vs IUPAC sign reference table in Chapter 1 with permanent cross-links from Chapters 3, 4, 8, and 9.
  - *Substep A.3*: Add a dedicated explanatory callout explaining why U Q5 and U Q6 report both $\\Delta H$ and $Q_{\\text{izd}} = -\\Delta H$ to safeguard student scores on RSU tests.
- **Subtask B: Theoretical Refactoring of Enthalpy & State Functions**
  - *Substep B.1*: Rewrite the theoretical opening of Chapter 4, strictly defining enthalpy as the state function Legendre transform $H \\equiv U + pV$, demonstrating why $\\Delta H = q_p$ strictly holds only when $p = \\text{const}$ and non-$pV$ work is zero.
  - *Substep B.2*: Introduce a dedicated historical-correction box formally retiring *siltumsaturs* and detailing why heat is a path-dependent process quantity that cannot be possessed by matter.
  - *Substep B.3*: Provide the exact conversion formula $\\Delta H = \\Delta U + \\Delta n_{\\text{gāzes}}RT$ for gas-phase reactions with full worked derivations.
- **Subtask C: First-Law Interactive Sign Sandbox & Process Generator**
  - *Substep C.1*: Code the vanilla JavaScript module `firstLawSignConverter` inside `build/script.js` with inputs for $Q$ and $A$, outputting $\\Delta U$ and the corresponding IUPAC pair $(q, w)$.
  - *Substep C.2*: Build the HTML container in `build/instruments.html` with reactive directional SVG arrow indicators representing system boundaries.
  - *Substep C.3*: Write automated console test assertions validating ideal gas expansions across all four thermodynamic pathways.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**: 
  1. Isobaric expansion of 1 mole ideal gas at $101.325\\text{ kPa}$ from $22.4\\text{ L}$ to $44.8\\text{ L}$: $A = p\\Delta V = 2.27\\text{ kJ}$; if $Q = 5.68\\text{ kJ}$, then $\\Delta U = Q - A = +3.41\\text{ kJ}$. IUPAC mirror: $w = -2.27\\text{ kJ}$, $q = +5.68\\text{ kJ}$, $\\Delta U = q + w = +3.41\\text{ kJ}$.
  2. Isothermal expansion at $298.15\\text{ K}$: $\\Delta U = 0\\text{ kJ} \\implies Q = A$.
- **Acceptance Gate**: 
  - Zero instances of *siltumsaturs* outside historical correction quotation blocks.
  - Text explicitly affirms $\\Delta U = 0$ for isothermal ideal gas processes.
  - All test vectors pass within $\\pm 0.01\\text{ kJ}$.

---

### TASK-02: Enthalpy, Thermochemical Equations, Hess's Law & Reaction Energy Profiles

#### 1. Strategic Objective & Domain Scope
Rigidly reformulate Hess's Law of Constant Heat Summation, thermochemical equation stoichiometry, standard formation/combustion enthalpies, and reaction energy coordinates. Correct critical curricular errors in the lecture notes, including the condition of state functions under constant pressure/volume, the massive glucose photosynthesis enthalpy defect ($\\Delta H = 1273\\text{ kJ/mol}$ vs $+2805\\text{ kJ/mol}$), standard pressure definitions, and the conflation of thermodynamic enthalpy change with kinetic activation energy. Directly resolves **S4**, **S5**, **S6**, **S7**, **S8**, and **S10**.

#### 2. Deep Domain & Pedagogical Rationale
- **Hess's Law Foundations (S4)**: K p.3–5 names Hess's Law «enerģijas un reaģējošo vielu daudzuma ekvivalences likums» and states it without specifying constant pressure ($p$) or constant volume ($V$). Because $q$ is a path function, Hess's Law holds *if and only if* the process occurs under conditions where heat equals a state function ($\\Delta H = q_p$ at constant $p$, or $\\Delta U = q_V$ at constant $V$).
- **The Photosynthesis Enthalpy Disaster (S5)**: On K p.4, the notes assert that photosynthesis has «$\\Delta H = 1273\\text{ kJ/mol}$» and «$-\\Delta H_{\\text{sadegšanas}} = -1273$». On p.11, however, glucose combustion enthalpy is given as $-2808\\text{ kJ/mol}$. The number $1273\\text{ kJ/mol}$ is in fact the absolute value of the standard formation enthalpy of solid glucose ($|\\Delta_f H^\\circ| = 1263\\text{ to } 1273\\text{ kJ/mol}$), not the enthalpy of reaction! Photosynthesis ($6\\text{CO}_2 + 6\\text{H}_2\\text{O} \\to \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2$) requires $+2805\\text{ to }+2808\\text{ kJ/mol}$. Teaching $1273\\text{ kJ/mol}$ causes students to fail both quantitative stoichiometry and bioenergetics questions.
- **IUPAC Standard State vs Standard Conditions (S6)**: The notes define standard conditions as $1\\text{ atm}$ and $25^\\circ\\text{C}$. IUPAC defined standard pressure as $p^\\circ = 1\\text{ bar} = 100\\text{ kPa}$ in 1982. Furthermore, standard state does not fix temperature (though $298.15\\text{ K}$ is conventional).
- **Combustion Enthalpy Rules (S7, S8)**: Notes p.5 claim «sadegšanas gadījumā nelieto standartentalpijas», which misleads students into thinking combustion enthalpies cannot be standard values. They are tabulated standard molar values $\\Delta_c H^\\circ$. The formula $\\Delta_r H^\\circ = \\sum \\nu \\Delta_c H^\\circ(\\text{reactants}) - \\sum \\nu \\Delta_c H^\\circ(\\text{products})$ must be formally juxtaposed against the formation formula $\\sum \\nu \\Delta_f H^\\circ(\\text{products}) - \\sum \\nu \\Delta_f H^\\circ(\\text{reactants})$.
- **Thermodynamic $\\Delta H$ vs Kinetic Activation Barrier $E_a$ (S10)**: Notes p.6 define an exothermic reaction as releasing «vairāk enerģijas nekā nepieciešams reakcijas uzsākšanai». This fatally confuses thermodynamics with chemical kinetics. An exothermic reaction simply has $H_{\\text{products}} < H_{\\text{reactants}}$ ($\\Delta H < 0$). Activation energy $E_a$ determines reaction velocity ($k = A e^{-E_a/RT}$), not thermodynamic yield. Highly exothermic reactions (such as glucose oxidation or diamond conversion to graphite) can be kinetically inert at room temperature.

#### 3. Workspace Skills Applied & Technical Synergy
- `synoptic-matrix-architect`: Generates the side-by-side comparative matrix contrasting Formation Enthalpy ($\\Delta_f H^\\circ$) versus Combustion Enthalpy ($\\Delta_c H^\\circ$).
- `blueprint-spec-sheet`: Formats the thermochemical equations, stoichiometry rules, and the 6 seminar reaction enthalpy calculations into a precision ledger.
- `dataviz`: Aligns reaction profile coordinates on a standardized, physically calibrated energy axis.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Multi-Step Hess Cycle Solver**: An interactive tool allowing students to select independent reaction steps (e.g., carbon oxidation to $\\text{CO}$, $\\text{CO}$ to $\\text{CO}_2$) and automatically generate the closed thermodynamic cycle, demonstrating algebraically and visually that the direct pathway enthalpy equals the sum of intermediate steps.
- **Enthalpy vs Activation Energy Sandbox**: An interactive slider where students vary activation energy $E_a$ independently of $\\Delta H$, demonstrating that lowering $E_a$ (catalysis) increases speed without shifting the thermodynamic enthalpy difference.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Multi-Pathway Hess Cycle ($\text{FeCl}_3$)**:
  - Upgrades `figures.py` `OUT["hess"]` to show the full triangular thermodynamic cycle for $\\text{Fe}(s) + \\frac{3}{2}\\text{Cl}_2(g) \\to \\text{FeCl}_3(s)$ ($\\Delta H = -399.5\\text{ kJ/mol}$) and the two-step route via $\\text{FeCl}_2(s)$ ($-341.8\\text{ kJ/mol}$ and $-57.7\\text{ kJ/mol}$).
  - Adds a dynamic vector check line verifying closure: $\\Delta H_1 = \\Delta H_2 + \\Delta H_3$.
- **Upgraded Energy Profiles Plate**:
  - Plots exothermic ($\\Delta H = -70\\text{ kJ/mol}$) and endothermic ($\\Delta H = +55\\text{ kJ/mol}$) reactions on an identical vertical energy scale ($Y_{\\text{scale}}$).
  - Includes a third side-by-side panel illustrating an exothermic reaction with a massive activation barrier ($E_a = 95\\text{ kJ/mol}$) to visually cement that «exothermic does not mean fast».

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Section 4.2 and Section 5.1 in `part_top.html`, establishing the exact physical conditions for Hess's Law and clarifying standard state definitions ($p^\\circ = 1\\text{ bar}$, $298.15\\text{ K}$).
- **Substep 2**: Correct the photosynthesis enthalpy inconsistency across all chapters, establishing $+2805.3\\text{ kJ/mol}$ (from U Q5 data) and $+2808\\text{ kJ/mol}$ (from K p.11 data), while documenting S5 in the defect register.
- **Substep 3**: Update `build/figures.py` to regenerate the Hess cycle and unified energy profile vector graphics with explicit leader lines and mathematical labels.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Hess's Law State-Function Rigor & Calculation Ledger**
  - *Substep A.1*: Formulate Hess's Law strictly as a mathematical consequence of enthalpy being a state function: $\\oint dH = 0$.
  - *Substep A.2*: Author worked ledgers for propene hydrogenation ($-2058\\text{ kJ/mol}$) and $\\text{FeCl}_3$ formation, formatting each calculation with explicit columns: Species, Stoichiometric Coefficient $\\nu$, $\\Delta_f H^\\circ$, and $\\nu \\cdot \\Delta_f H^\\circ$.
  - *Substep A.3*: Add clear pedagogical guidelines detailing how reversing an equation flips the sign of $\\Delta H$ and multiplying coefficients scales $\\Delta H$ proportionally.
- **Subtask B: Photosynthesis vs Respiration Thermochemical Reconciliation**
  - *Substep B.1*: Reconstruct the complete thermochemical equations for cellular respiration ($\\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2 \\to 6\\text{CO}_2 + 6\\text{H}_2\\text{O}$, $\\Delta_c H^\\circ = -2808\\text{ kJ/mol}$) and photosynthesis ($6\\text{CO}_2 + 6\\text{H}_2\\text{O} \\to \\text{C}_6\\text{H}_{12}\\text{O}_6 + 6\\text{O}_2$, $\\Delta_r H^\\circ = +2808\\text{ kJ/mol}$).
  - *Substep B.2*: Insert a high-visibility «Piezīme avotam» block explaining the origin of K p.4's $1273\\text{ kJ/mol}$ error as the standard formation enthalpy $|\\Delta_f H^\\circ|$ of glucose.
  - *Substep B.3*: Align the photosynthesis calculation in Chapter 5 with the seminar task U Q5 calculation ($+2805.27\\text{ kJ}$), explaining the slight difference due to aqueous vs gaseous state conventions.
- **Subtask C: Energy Coordinate Vector Modernization & Reaction Ledger**
  - *Substep C.1*: Modify `build/figures.py` to draw precise reaction profiles with transition-state brackets, activation energy vectors ($E_{a,\\text{forward}}$ and $E_{a,\\text{reverse}}$), and signed reaction enthalpy $\\Delta H$.
  - *Substep C.2*: Construct the Reaction Ledger interactive tool in `instruments.html` pre-loaded with the 6 seminar reactions from U Q6.
  - *Substep C.3*: Implement automated verification script ensuring that all computed reaction enthalpies match hand calculations to within $\\pm 0.01\\text{ kJ/mol}$.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. $\\text{FeCl}_3$ synthesis cycle: $\\Delta H_1 = -399.5\\text{ kJ/mol}$; $\\Delta H_2 + \\Delta H_3 = -341.8 + (-57.7) = -399.5\\text{ kJ/mol}$ (diff = $0.00\\text{ kJ/mol}$).
  2. Propene combustion to formation: $\\Delta_r H = -124 - 2220 + 286 = -2058.0\\text{ kJ/mol}$.
  3. Photosynthesis stoichiometry: $6(-393.5) + 6(-286.0) - (-1273) = -4077 - (-1273) = -2804\\text{ kJ/mol}$.
- **Acceptance Gate**:
  - No occurrence of $\\Delta H = 1273\\text{ kJ/mol}$ representing photosynthesis anywhere in prose or tables.
  - Reaction profiles visibly share a common enthalpy datum with explicit zero lines.

---

### TASK-03: Second Law, Statistical Microstate Dispersal, Entropy & Absolute Third Law

#### 1. Strategic Objective & Domain Scope
Purge the unscientific and misleading portrayal of entropy as mere "chaos and disorder" (*haoss un nesakārtotība*), replacing it with the statistical mechanical reality of energy dispersal over quantized microstates ($S = k \\ln W$). Formulate the Second Law of Thermodynamics rigorously via Clausius and Kelvin-Planck statements, derive the reaction entropy ledger, establish the Third Law of Thermodynamics ($S \\to 0$ as $T \\to 0\\text{ K}$ for a perfect crystal) to explain why absolute standard entropies $S^\\circ$ are positive non-zero quantities, and expose counterexamples to naive synthesis heuristics. Directly resolves **S9**, **S11**, **S12**, **S13**, **S14**, and **S27**.

#### 2. Deep Domain & Pedagogical Rationale
- **The "Cosmic Force" Fallacy (S9)**: K p.6 asserts that «pasaulē ir kāds spēks, kas nosaka patvaļīgo pārvērtību virzienu». There is no mystical "force"; spontaneous direction is a purely statistical consequence of the overwhelming probability of energy dispersing into a vastly larger number of microstates ($\\Delta S_{\\text{kop}} > 0$).
- **The Kelvin Statement Inaccuracy (S11)**: K p.7 states that a process whose sole source of energy is heat cannot produce work. The correct Kelvin-Planck formulation specifies that *no cyclic process is possible whose sole result is the complete conversion of heat from a single reservoir into mechanical work*. Isothermal expansion of an ideal gas converts heat completely into work ($Q = A$), but it is not cyclic because the system's volume expands.
- **Entropy as "Chaos" vs Energy Dispersal (S12, S13)**: Colloquial "chaos" leads students into grave errors. K p.12 teaches the heuristic «sarežģītāks $\\to$ vienkāršāks $\\implies \\Delta S > 0$; sintēze $\\implies \\Delta S < 0$». This heuristic catastrophically fails within the course's own problem set: in seminar task U Q3, the dipeptide condensation of leucine and glycine ($\text{Leu}(s) + \\text{Gly}(s) \\to \\text{Leu-Gly}(s) + \\text{H}_2\\text{O}(l)$) is a synthesis reaction that exhibits a *positive* reaction entropy ($\\Delta_r S = +22\\text{ J/(mol}\\cdot\\text{K)}$)! Similarly, dissolving ammonium nitrate (U Q2) increases entropy despite forming a highly organized ionic solution sphere. Furthermore, K p.9 calls $W$ in $S = k \\ln W$ «termodinamiskā varbūtība». $W$ is not a probability (which must be $\\le 1$), but the integer count of distinct accessible microstates ($W \\ge 1$).
- **Surroundings Entropy vs System Entropy (S14)**: K p.10 states that «eksotermiskas reakcijas rezultātā entropija pieaug». In an exothermic reaction, it is the *surroundings'* entropy that increases ($\\Delta S_{\\text{apk}} = -\\Delta H/T > 0$); the system's own entropy $\\Delta S_{\\text{sist}}$ can be negative (e.g., combustion of ethanol, U Q6.4, where $\\Delta_r S = -260.6\\text{ J/K}$).
- **The Third Law Omission (S27)**: The topic description requires students to know the Third Law, yet the notes mention it only in passing. Without Nernst's Third Law, students cannot comprehend why standard entropies $S^\\circ$ are tabulated as absolute values (and are non-zero for pure elements), whereas enthalpies and free energies are defined relative to arbitrary zero baselines ($\\Delta_f H^\\circ = 0$, $\\Delta_f G^\\circ = 0$).

#### 3. Workspace Skills Applied & Technical Synergy
- `state-scrubber-lab`: Visualizes molecular microstate configurations across discrete thermodynamic states.
- `cognitive-deload-auditor`: Deconstructs the abstract statistical mathematics of Boltzmann combinatorics into intuitive visual ratios.
- `dataviz`: Powers the combinatorial bar charts illustrating the probability of uniform spatial distribution vs all particles occupying a single half.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Molecular Microstate Sandbox**: An interactive simulation where students adjust the number of gas particles ($N = 4, 10, 20, 100$) distributed between two compartments of a partitioned box. Displays real-time macrostate distributions calculated via combinations $W(k) = \\binom{N}{k} = \\frac{N!}{k!(N-k)!}$, showing that the probability of finding all particles in one half drops from $1/16$ ($N=4$) to $7.9 \\times 10^{-31}$ ($N=100$).
- **Entropy Predictor Matrix**: A structured diagnostic widget where students input reaction features ($\\Delta n_{\\text{gāzes}}$, phase transitions, particle count changes) to predict the sign of $\\Delta S$, with automated feedback highlighting counterexamples like peptide synthesis.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Microstate Combinatorial Distribution**:
  - Upgrades `figures.py` `OUT["microstates"]` (`viewBox="0 0 900 480"`).
  - Left Panel: $N=4$ particles across 2 halves with explicit bar heights for arrangements ($1, 4, 6, 4, 1$; total 16).
  - Right Panel: $N=20$ particles with a continuous distribution envelope peaking at $W(10) = 184,756$ out of $1,048,576$ total states.
  - Adds an anatomical molecular box graphic showing particles dispersed uniformly vs clustered, cementing spatial and energetic dispersal.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Refactor Chapter 6 in `part_6_9.html` to redefine entropy rigorously via Boltzmann ($S = k \\ln W$) and Clausius ($dS = dq_{\\text{rev}}/T$), establishing the Third Law of Thermodynamics.
- **Substep 2**: Replace all colloquial references to "chaos/disorder" with the concept of energy dispersal across microstates; showcase U Q3 dipeptide synthesis as a primary proof that synthesis does not require $\\Delta S < 0$.
- **Substep 3**: Update `build/figures.py` to render the upgraded dual-panel microstate combinatorial plate with accessible labels and mathematical annotations.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Statistical Mechanics & Mathematical Formulation of Entropy**
  - *Substep A.1*: Detail the exact physical meaning of Boltzmann's constant $k = R/N_A = 1.380649 \\times 10^{-23}\\text{ J/K}$ and Avogadro's number $N_A = 6.02214076 \\times 10^{23}\\text{ mol}^{-1}$ (correcting the notes' obsolete $6.023 \\times 10^{23}$, S13).
  - *Substep A.2*: Provide the mathematical proof for the isothermal expansion of 1 mole of ideal gas: $\\Delta S = R \\ln(V_2/V_1) = R \\ln 2 = 5.76\\text{ J/(mol}\\cdot\\text{K)}$.
  - *Substep A.3*: Add the reversible heat requirement for Clausius entropy ($dS = dq_{\\text{rev}}/T$), explicitly teaching students that calculating $\\Delta S$ for an irreversible process requires constructing an imaginary reversible path.
- **Subtask B: The Third Law & Absolute Standard Entropies**
  - *Substep B.1*: Author a dedicated section defining the Third Law of Thermodynamics: at $T = 0\\text{ K}$, a perfect crystalline substance possesses exactly one microstate ($W = 1$), hence $S = k \\ln 1 = 0$.
  - *Substep B.2*: Create a comparative infographic explaining why standard molar entropies $S^\\circ$ are absolute positive numbers ($S^\\circ > 0$, even for pure elements like $\\text{O}_2(g) = 205.1\\text{ J/(mol}\\cdot\\text{K)}$), contrasting with $\\Delta_f H^\\circ = 0$.
  - *Substep B.3*: Tabulate temperature dependence of entropy from $0\\text{ K}$ through phase transitions (fusion, vaporization), illustrating vertical entropy jumps $\\Delta S_{\\text{fus}} = \\Delta H_{\\text{fus}}/T_{\\text{fus}}$ and $\\Delta S_{\\text{vap}} = \\Delta H_{\\text{vap}}/T_{\\text{vap}}$.
- **Subtask C: Second Law Formulations & Qualitative Predictor Polish**
  - *Substep C.1*: Formulate the Kelvin-Planck and Clausius statements of the Second Law with explicit diagrams showing why heat cannot spontaneously flow from cold to hot without external work.
  - *Substep C.2*: Formulate the total entropy change of the universe: $\\Delta S_{\\text{kop}} = \\Delta S_{\\text{sist}} + \\Delta S_{\\text{apk}} \\ge 0$, demonstrating why exothermic reactions raise surroundings entropy via $\\Delta S_{\\text{apk}} = -\\Delta H/T$.
  - *Substep C.3*: Rebuild the qualitative entropy prediction rules, establishing $\\Delta n_{\\text{gāzes}}$ as the dominant chemical determinant, followed by phase changes and dissolution.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. Microstate probability: $N=4$ all left = $1/16 = 0.0625$; $N=10$ all left = $1/1024 = 9.77 \\times 10^{-4}$; $N=20$ all left = $9.54 \\times 10^{-7}$; $N=100$ all left = $7.89 \\times 10^{-31}$.
  2. Gas expansion: $\\Delta S = 8.314462618 \\cdot \\ln 2 = 5.763\\text{ J/(mol}\\cdot\\text{K)}$.
  3. Dipeptide entropy check (U Q3): $\\Delta_r S = 281 + 70 - 207 - 122 = +22\\text{ J/(mol}\\cdot\\text{K)}$.
- **Acceptance Gate**:
  - The word *haoss* is strictly qualified as an informal metaphor and replaced by microstate energy dispersal.
  - The Third Law of Thermodynamics has an explicit heading, definition, and pedagogical explanation.

---

### TASK-04: Gibbs Free Energy Derivation, Spontaneity Criteria & 4-Quadrant Phase Matrix

#### 1. Strategic Objective & Domain Scope
Provide an unassailable mathematical and physical derivation of Gibbs Free Energy ($G \\equiv H - TS$) directly from the Second Law of Thermodynamics ($\\Delta S_{\\text{kop}} > 0$). Correct the mathematical error in the four-case $\\Delta H / \\Delta S$ sign matrix (replacing $|T\\Delta S| < \\Delta H$ with $|T\\Delta S| < |\\Delta H|$), eliminate fatalistic assertions that endergonic reactions are «termodinamiski aizliegtas» by formally introducing reaction coupling, and establish the fundamental thermodynamic connection between standard free energy and the chemical equilibrium constant ($\\Delta G^\\circ = -RT \\ln K$). Directly rectifies **S15**, **S16**, **S17**, and **S27**.

#### 2. Deep Domain & Pedagogical Rationale
- **The Physical Meaning of Gibbs Energy**: Students routinely perceive $\\Delta G = \\Delta H - T\\Delta S$ as an arbitrary empirical equation. In reality, it is a direct algebraic restatement of the Second Law of Thermodynamics under conditions of constant temperature and pressure. Since the surroundings act as a thermal reservoir, $\\Delta S_{\\text{apk}} = -\\Delta H/T$. The Second Law requires $\\Delta S_{\\text{kop}} = \\Delta S_{\\text{sist}} + \\Delta S_{\\text{apk}} > 0$. Multiplying through by $-T$ yields $-T\\Delta S_{\\text{kop}} = \\Delta H - T\\Delta S_{\\text{sist}} \\equiv \\Delta G$. Thus, $\\Delta G < 0$ is *identically equivalent* to $\\Delta S_{\\text{kop}} > 0$! This elegant 3-line derivation demystifies the entire subject for medical students.
- **The Case 2 Inequality Error (S17)**: On K p.12–13, in the table of the four $\\Delta H / \\Delta S$ sign combinations, Case 2 ($\\Delta H < 0, \\Delta S < 0$) is printed with the condition «$|T\\Delta S| < \\Delta H$». This is mathematically impossible since $\\Delta H < 0$ and absolute value $|T\\Delta S|$ is positive! The correct physical inequality is $|T\\Delta S| < |\\Delta H|$.
- **The "Thermodynamically Forbidden" Misconception (S17)**: K p.13 labels endothermic syntheses with $\\Delta S < 0$ as «termodinamiski aizliegtas». This is deeply misleading: they are non-spontaneous *in isolation*, but biological life exists precisely by coupling them to strongly exergonic processes (e.g., ATP hydrolysis).
- **Glucose Oxidation Discrepancies (S16)**: K p.11 uses $\\Delta_r S^\\circ = +182.4\\text{ J/(mol}\\cdot\\text{K)}$ for glucose combustion, yielding $\\Delta_r G(310\\text{ K}) = -2864.5\\text{ kJ/mol}$ (printed as $-2865$). Using standard thermodynamic tables ($S^\\circ$: glucose 212.1, $\\text{O}_2$ 205.1, $\\text{CO}_2$ 213.8, $\\text{H}_2\\text{O}(l)$ 69.9), $\\Delta_r S^\\circ \\approx +259.5\\text{ J/(mol}\\cdot\\text{K)}$, which yields $\\Delta_r G(310\\text{ K}) \\approx -2888.4\\text{ kJ/mol}$. Both numbers must be clearly reconciled.
- **The Equilibrium Connection (S27)**: The topic description demands an understanding of equilibrium, yet the notes never link $\\Delta G^\\circ$ to the equilibrium constant $K$. Medical students must understand that $\\Delta G^\\circ = -RT \\ln K$, and that $\\Delta G = 0$ represents dynamic equilibrium, whereas biological death corresponds to cellular equilibrium.

#### 3. Workspace Skills Applied & Technical Synergy
- `synoptic-matrix-architect`: Implements the 4-case sign matrix with responsive sticky axes, active cell highlighting, and crossover temperature formulas.
- `state-scrubber-lab`: Drives the real-time temperature slider visualizing how varying $T$ shifts $\\Delta G$ across the zero line.
- `break-ui`: Ensures that wide synoptic tables reflow gracefully without horizontal viewport overflow on mobile devices ($390\\text{ px}$).

#### 4. Features & Interactive Add-on Innovations
- **Interactive $\\Delta G(T)$ Isobaric Crossover Sandbox (Instrument A Upgrade)**:
  - Sliders for $\\Delta H$ ($-500\\text{ to }+500\\text{ kJ/mol}$) and $\\Delta S$ ($-500\\text{ to }+500\\text{ J/(mol}\\cdot\\text{K)}$).
  - Temperature slider ($0\\text{ to }2000\\text{ K}$) with synchronized Celsius display.
  - Real-time calculation of $\\Delta G$, case categorization (1 to 4), crossover temperature $T_{\\text{cross}} = \\Delta H/\\Delta S$, and spontaneity verdict.
  - Preset buttons for seminar problems: U Q1 (Syngas, $972\\text{ K}$), U Q2 (Cold Pack, $258\\text{ K}$), U Q3 (Peptide, $955\\text{ K}$), U Q6.2 ($328\\text{ K}$), U Q6.6 ($37\\text{ K}$).
  - Boundary guard: alerts student if $\\Delta S$ was accidentally entered in $\\text{kJ}$ rather than $\\text{J}$.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Four-Quadrant $\\Delta G(T)$ Phase Plot**:
  - Upgrades `figures.py` `OUT["dgt"]` (`viewBox="0 0 980 520"`).
  - Left Panel: Plots all four sign cases on unified $(T, \\Delta G)$ axes with the bold red horizontal zero line ($y = 0$).
  - Right Panel: Dedicated plots for seminar tasks U Q1 and U Q2, showing exact crossover intercepts at $972.2\\text{ K}$ and $258.0\\text{ K}$ with highlighted standard temperature ($298.15\\text{ K}$) points.
  - Dashed lines visually denote temperature regimes outside the physical stability of reactants and products.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Section 7.1 in `part_6_9.html`, incorporating the rigorous 3-line Second-Law derivation of Gibbs Free Energy and clarifying the distinction between $\\Delta G$ (reaction driving force at actual concentrations) and $\\Delta G^\\circ$ (standard benchmark).
- **Substep 2**: Rebuild the Four-Case Matrix in Section 7.2 using `synoptic-matrix-architect`, correcting the Case 2 inequality to $|T\\Delta S| < |\\Delta H|$ and refuting the "forbidden reaction" terminology.
- **Substep 3**: Update `build/figures.py` and `build/script.js` to ensure that Instrument A and the $\\Delta G(T)$ SVG visualizer interactively synchronize across all viewports.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Mathematical Derivation & Equilibrium Thermodynamics**
  - *Substep A.1*: Write the exact mathematical derivation $-T\\Delta S_{\\text{kop}} = \\Delta H - T\\Delta S_{\\text{sist}} = \\Delta G$ in semantic MathML with full explanatory narrative.
  - *Substep A.2*: Author the equilibrium section explaining $\\Delta G = \\Delta G^\\circ + RT \\ln Q$ and $\\Delta G^\\circ = -RT \\ln K$, showing that at equilibrium $\\Delta G = 0$ and $Q = K$.
  - *Substep A.3*: Calculate the numerical water autoprotolysis test case: $\\Delta G^\\circ = -8.314 \\cdot 298.15 \\cdot \\ln(10^{-14}) = +79.9\\text{ kJ/mol}$.
- **Subtask B: Synoptic Four-Quadrant Matrix Construction**
  - *Substep B.1*: Structure the matrix in semantic HTML with four explicit quadrants: Case 1 ($\\Delta H < 0, \\Delta S > 0$, spontaneous at all $T$); Case 2 ($\\Delta H < 0, \\Delta S < 0$, enthalpy-driven, spontaneous below $T_{\\text{cross}}$); Case 3 ($\\Delta H > 0, \\Delta S > 0$, entropy-driven, spontaneous above $T_{\\text{cross}}$); Case 4 ($\\Delta H > 0, \\Delta S < 0$, non-spontaneous at all $T$).
  - *Substep B.2*: Add explicit columns for Physical Mechanism, Dominant Factor, Crossover Formula ($T = \\Delta H/\\Delta S$), and Biological / Chemical Concrete Example.
  - *Substep B.3*: Apply responsive CSS ensuring the matrix maintains sticky column headers during vertical reading and scrolls with visible edge shadows on narrow screens.
- **Subtask C: Glucose Catabolic Energy Accounting Reconciliation**
  - *Substep C.1*: Present both glucose combustion calculations side by side: the course key value ($\\Delta_r S = +182.4\\text{ J/(mol}\\cdot\\text{K)} \\implies \\Delta G(310\\text{ K}) = -2864.5\\text{ kJ/mol}$) and the accepted handbook value ($\\Delta_r S = +259.5\\text{ J/(mol}\\cdot\\text{K)} \\implies \\Delta G(310\\text{ K}) = -2888.4\\text{ kJ/mol}$).
  - *Substep C.2*: Recompute the mechanical work check: lifting a $70\\text{ kg}$ student by $3\\text{ meters}$ requires $W = mgh = 70 \\cdot 9.81 \\cdot 3 = 2060.1\\text{ J} = 2.06\\text{ kJ}$; glucose mass required = $\\frac{2.06}{2888.4} \\cdot 180.16 = 0.1285\\text{ g} \\approx 0.13\\text{ g}$ (identical to two significant figures).
  - *Substep C.3*: Connect glucose free energy yield to maximum theoretical ATP synthesis: $\\frac{2888.4\\text{ kJ/mol}}{30.5\\text{ kJ/mol}} \\approx 94.7\\text{ ATP}$ equivalents.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. U Q1 Crossover: $T_{\\text{cross}} = \\frac{210,000}{216} = 972.22\\text{ K} = 699.07^\\circ\\text{C}$. At $298.15\\text{ K}$: $\\Delta G = 210 - 298.15 \\cdot 0.216 = +145.60\\text{ kJ/mol}$.
  2. U Q2 Crossover: $T_{\\text{cross}} = \\frac{28,050}{108.72} = 258.00\\text{ K} = -15.15^\\circ\\text{C}$. At $298.15\\text{ K}$: $\\Delta G = 28.05 - 298.15 \\cdot 0.10872 = -4.365\\text{ kJ/mol}$.
- **Acceptance Gate**:
  - Case 2 condition is strictly printed as $|T\\Delta S| < |\\Delta H|$.
  - Instrument A passes all test vectors within $\\pm 0.05\\text{ kJ/mol}$ and displays an explicit warning if $|\\Delta S| < 1$.

---

### TASK-05: Non-Equilibrium Biological Thermodynamics, Dissipative Structures & Prigogine Negentropy

#### 1. Strategic Objective & Domain Scope
Formulate the thermodynamics of living organisms as open, non-equilibrium dissipative systems that maintain complex internal structural order by continuously importing free energy (negentropy) and dissipating high-entropy heat to the environment. Correct gross historical errors in the notes (Lavoisier's guinea pig experiment dates: 1782–1783, not 1873!), rectify false ecological system classifications (Earth is closed, ecosystems are open), resolve the Prigogine entropy accounting notation collisions ($dS = d_i S + d_e S$), and rigorously contrast steady state (*stacionārs stāvoklis*) with thermodynamic equilibrium. Directly resolves **S18**, **S19**, **S20**, and **S21**.

#### 2. Deep Domain & Pedagogical Rationale
- **Historical Accuracy (S18)**: K p.13 claims Antoine Lavoisier and Pierre-Simon Laplace conducted ice calorimeter experiments on guinea pigs «1782.–1873. gadā». Lavoisier was executed in 1794 during the French Revolution! The famous experiments occurred in the winter of **1782–1783**. Publishing "1873" destroys academic credibility.
- **Thermodynamic System Classification of Earth and Ecosystems (S19)**: K p.14 lists as examples of isolated systems: «ekosistēma un zemeslode, jūra, ezers, purvs, kontinents, sala». Every single one of these is false! Seas, lakes, swamps, and islands exchange both matter and energy with their surroundings (they are **open systems**). The Earth as a whole exchanges negligible matter with space but absorbs high-grade solar radiation ($T \\approx 5800\\text{ K}$) and emits low-grade infrared radiation ($T \\approx 288\\text{ K}$), making it a quintessential **closed system**. There are no isolated systems on Earth, save for an ideal Dewar flask over short intervals.
- **Prigogine Entropy Production Accounting (S20)**: K p.14–15 introduces catastrophic symbol collisions: it denotes organism entropy as $S_i$ and asserts that $\\Delta S_i$ is «vienmēr negatīvs», directly contradicting the Second Law. In Ilya Prigogine's non-equilibrium thermodynamics, the entropy change of an open system is partitioned as $dS = d_i S + d_e S$, where $d_i S \\ge 0$ is the internal entropy *production* (always positive due to irreversible metabolic processes) and $d_e S$ is the entropy *exchange* with the environment. An organism maintains homeostatic order by exporting entropy ($d_e S < 0$) such that $|d_e S| \\ge d_i S$, resulting in $dS_{\\text{org}} \\le 0$. Meanwhile, the universe's total entropy always increases: $dS_{\\text{vis}} = d_i S > 0$.
- **Steady State vs Equilibrium (S21)**: Medical students constantly confuse homeostasis (dynamic steady state) with chemical equilibrium. At equilibrium, free energy is at an absolute minimum ($G = G_{\\text{min}}$), net reaction rates are zero ($v_{\\text{forward}} = v_{\\text{reverse}}$), no work can be extracted, and internal entropy is maximized. For a living cell, thermodynamic equilibrium is biological death. In steady state, continuous flux of matter and energy maintains concentrations constant away from equilibrium, allowing continuous physiological work. Furthermore, K p.15 states that *homeostasis* comes from Latin; it derives from Greek (*homoios* = similar, *stasis* = standing).

#### 3. Workspace Skills Applied & Technical Synergy
- `mook-visual-compendium`: Designs the visual magazine-style micro-spread detailing cellular negentropy import and heat dissipation.
- `cognitive-deload-auditor`: Visually untangles Prigogine's entropy decomposition into clear, color-differentiated balance bars.
- `lexicon-morphology-weaver`: Breaks down the etymologies of homeostasis, dissipative structures, catabolism, and anabolism.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Cellular Negentropy Balance Simulator**: A dynamic widget where students adjust metabolic heat production, nutrient import rate, and growth rate, displaying live signed bar graphs for $\\Delta S_{\\text{org}}$, $\\Delta S_{\\text{env}}$, and $\\Delta S_{\\text{vis}}$. Demonstrates that while $\\Delta S_{\\text{org}}$ can be negative during tissue growth or zero during steady state, $\\Delta S_{\\text{vis}}$ is strictly positive at all times.
- **Steady State vs Equilibrium Diagnostic Comparison**: An interactive tabular matrix with revealable clinical scenarios (e.g., cell membrane potential, glucose homeostasis, rigor mortis) prompting students to classify the state and justify their reasoning.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Organism Entropy Ledger (`entropy_ledger`)**:
  - Upgrades `figures.py` `OUT["entropy_ledger"]` (`viewBox="0 0 860 430"`).
  - Left Panel: "Augšana" (Growth phase) with signed bars: $\\Delta S_{\\text{org}} = -12\\text{ J/K}$, $\\Delta S_{\\text{env}} = +30\\text{ J/K}$, yielding $\\Delta S_{\\text{vis}} = +18\\text{ J/K}$.
  - Right Panel: "Stacionārs stāvoklis" (Steady state) with $\\Delta S_{\\text{org}} = 0\\text{ J/K}$, $\\Delta S_{\\text{env}} = +18\\text{ J/K}$, yielding $\\Delta S_{\\text{vis}} = +18\\text{ J/K}$.
  - Features the bold red vertical zero line as the architectural anchor of the plate.
- **Brand-New Vector Plate: Global Solar-Biosphere Negentropy Cascade**:
  - Schematizes the influx of low-entropy high-energy solar photons ($h\\nu$) driving plant photosynthesis, transmitting chemical free energy through trophic food chains, and dissipating high-entropy degraded infrared heat into the cosmic heat sink.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Section 10 in `part_10_12.html`, correcting Lavoisier's dates (1782–1783), redefining system boundaries (Earth closed, ecosystems open), and providing the Greek etymology of homeostasis.
- **Substep 2**: Re-author the entropy bookkeeping section using the unambiguous notation $\\Delta S_{\\text{org}}$, $\\Delta S_{\\text{env}}$, and $\\Delta S_{\\text{vis}}$, explaining Prigogine's dissipative structures and the theorem of minimum entropy production in linear non-equilibrium regimes.
- **Substep 3**: Update `build/figures.py` to regenerate the organism entropy ledger and create the new biosphere energy cascade diagram.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: System Classification & Historical Integrity**
  - *Substep A.1*: Create a dedicated table in Chapter 2 classifying natural systems: Open (living cell, human body, ecosystem, lake), Closed (Earth as a planet, sealed ampoule), Isolated (universe, ideal thermos flask).
  - *Substep A.2*: Document the Lavoisier-Laplace ice calorimeter guinea pig experiment of 1782–1783 in Chapter 10, explaining how measuring melted ice proved that respiration is a slow combustion process obeying the First Law.
  - *Substep A.3*: Add a formal change-log entry detailing S18 and S19 with exact page citations and historical handbook verification.
- **Subtask B: Prigogine Non-Equilibrium Entropy Bookkeeping**
  - *Substep B.1*: Detail Prigogine's formulation $dS = d_i S + d_e S$, explicitly proving that the Second Law requires $d_i S \\ge 0$, while $d_e S$ can be negative through the export of degraded heat and waste.
  - *Substep B.2*: Provide a clear mathematical walk-through showing why an organism's steady state ($dS_{\\text{org}} = 0$) requires $d_e S = -d_i S$, meaning the rate of entropy export must exactly match the rate of internal metabolic entropy production.
  - *Substep B.3*: Contrast Prigogine's minimum entropy production theorem near equilibrium with complex non-linear self-organizing biochemical oscillations (e.g., Belousov-Zhabotinsky reaction, glycolytic oscillations).
- **Subtask C: Steady State vs Chemical Equilibrium Comparative Matrix**
  - *Substep C.1*: Construct a high-density comparative table contrasting Steady State (*stacionārs stāvoklis*) versus Equilibrium (*termodinamiskais līdzsvars*) across 6 parameters: Free energy $G$, Reaction velocity, Entropy production rate, Membrane gradients, Energy requirement, and Biological meaning.
  - *Substep C.2*: Provide a clinical case study on ischemia/anoxia: when blood flow ceases, nutrient and oxygen supply stops ($d_e S \\to 0$), cellular ATP depletes, ion pumps fail, and the cell inexorably drifts from steady state toward thermodynamic equilibrium (cell lysis and necrosis).
  - *Substep C.3*: Author closed recall questions testing students' ability to identify steady state vs equilibrium in physiological contexts.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  1. Steady state balance: $\\Delta S_{\\text{org}} = 0$; if $\\Delta S_{\\text{env}} = +18\\text{ J/K}$, then $\\Delta S_{\\text{vis}} = \\Delta S_{\\text{org}} + \\Delta S_{\\text{env}} = +18\\text{ J/K} > 0$ (Second Law satisfied).
  2. Growth phase balance: $\\Delta S_{\\text{org}} = -12\\text{ J/K}$, $\\Delta S_{\\text{env}} = +30\\text{ J/K} \\implies \\Delta S_{\\text{vis}} = +18\\text{ J/K} > 0$.
- **Acceptance Gate**:
  - Year 1873 completely eradicated and replaced by 1782–1783.
  - Earth is categorized as a closed system; living organisms and ecosystems are open systems.
  - Notation strictly uses $\\Delta S_{\\text{org}}$, $\\Delta S_{\\text{env}}$, $\\Delta S_{\\text{vis}}$.
"""
