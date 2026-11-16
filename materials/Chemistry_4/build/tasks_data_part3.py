# ruff: noqa: E501
"""Detailed specifications for Tasks 11 through 15."""

TASKS_PART3 = """
---

### TASK-11: Workspace Skills Integration — Synoptic Matrix Architect for Reaction & System Classifications

#### 1. Strategic Objective & Domain Scope
Deploy the dedicated workspace skill `synoptic-matrix-architect` across the master study document to transform fragmented tabular data into publication-grade, interactive synoptic comparison matrices. Target three foundational pedagogical areas: (1) The Four Enthalpy-Entropy Sign Cases Matrix; (2) The Comprehensive 6-Reaction Comparative Ledger (U Q6); and (3) The Thermodynamic System Types Matrix (Open, Closed, Isolated). Implement sticky dual axes, exact-difference highlighting, mobile horizontal reflow, and interactive cell occlusion for active recall.

#### 2. Deep Domain & Pedagogical Rationale
First-year medical students struggle to synthesize multi-variable thermodynamic conditions. When comparing systems or reaction classes across four or more attributes (e.g., $\\Delta H$ sign, $\\Delta S$ sign, temperature sensitivity, spontaneity criteria, biological examples, entropy of surroundings), static standard HTML tables induce high cognitive split-attention. Students lose track of column headers while scrolling vertically, and cannot isolate exact differences between subtle cases (e.g., Case 2 vs Case 3). Furthermore, on mobile viewports ($390\\text{ px}$), standard markdown tables break the layout, forcing frustrating horizontal page scrolls. By engineering synoptic matrices with sticky row/column headers, subtle differential shading, and active cell recall modes, the master document empowers students to mentally internalize the structural patterns of thermodynamics.

#### 3. Workspace Skills Applied & Technical Synergy
- `synoptic-matrix-architect`: Supplies the core architecture for sticky-axis matrices, cell-level isolation, and differential attribute styling.
- `break-ui`: Ensures zero horizontal body overflow on narrow viewports through localized touch-scroll containers with visual scroll cues.
- `impeccable`: Implements the calm, high-legibility typographic tokens and high-contrast borders.

#### 4. Features & Interactive Add-on Innovations
- **Cell Occlusion Active Recall Mode**: A toggle on synoptic matrices that masks individual cells (e.g., hiding Spontaneity Verdict or Crossover Formula) with interactive click-to-reveal covers, allowing students to test themselves on matrix relationships without leaving the page.
- **Synoptic Difference Filter**: A button allowing students to highlight only the attributes that change between adjacent rows (e.g., highlighting that Case 2 and Case 3 differ in both $\\Delta H$ sign and the direction of temperature dependence).
- **Responsive Matrix Reflow Switcher**: Automatically converts complex matrices into stacked, labeled cards on screens narrower than $640\\text{ px}$ if horizontal scrolling is disabled.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Synoptic Decision Tree Flowchart**:
  - A clean, accessible inline SVG algorithm flowchart (`viewBox="0 0 860 380"`).
  - Guides students through the decision path: Step 1: Evaluate $\\Delta H$ (Exo vs Endo); Step 2: Evaluate $\\Delta S$ (Dispersal vs Ordering); Step 3: Check Temperature Regime ($T \\gtrless \\Delta H/\\Delta S$); Step 4: Final Spontaneity Verdict.
  - Links visually and colorimetrically to the four quadrants of the Synoptic Sign Matrix.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Refactor the Four-Case Matrix in Section 7.2 using `synoptic-matrix-architect` semantics with `class="synoptic-matrix"` and responsive sticky header positioning.
- **Substep 2**: Rebuild the Table of Six Seminar Reactions (Section 12.6) as an interactive synoptic ledger with sortable columns and exact-difference highlight bars.
- **Substep 3**: Add CSS tokens and minimal vanilla JavaScript in `build/style.css` and `build/script.js` to enable cell masking and responsive edge cues.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: The Four-Case Synoptic Matrix Implementation**
  - *Substep A.1*: Author the semantic HTML table structure in `build/part_6_9.html` containing 4 rows (Cases 1 to 4) and 7 attribute columns: Case ID, $\\Delta H$, $\\Delta S$, Condition for Spontaneity, Crossover Formula, Reaction Plot Line Style, and Clinical/Biological Prototype.
  - *Substep A.2*: Apply CSS sticky positioning (`position: sticky; top: 0; z-index: 10`) to the header row and the first column (Case ID), utilizing the background token `var(--surface)` to prevent content bleed-through.
  - *Substep A.3*: Add subtle row hover isolation (`tbody tr:hover`) with a high-contrast left border accent (`var(--accent)`).
- **Subtask B: Seminar Task U Q6 Reaction Ledger Matrix**
  - *Substep B.1*: Build the synoptic table for the six reactions in `build/part_10_12.html`, incorporating chemical equation strings, calculated $\\Delta_r H$, $\\Delta_r S$, $\\Delta_r G(298\\text{ K})$, $T_{\\text{cross}}$, and Physical Validity tags.
  - *Substep B.2*: Implement differential cell highlighting for the zero line: values where $\\Delta G < 0$ display a subtle negative indicator bar, while positive values show an uphill indicator.
  - *Substep B.3*: Integrate sorting buttons in the table header allowing students to order reactions by enthalpy, entropy, or free energy.
- **Subtask C: Responsive Mobile Touch & Occlusion Layer**
  - *Substep C.1*: Encase all synoptic matrices inside `<div class="matrix-scroll-wrapper" tabindex="0" role="region" aria-label="Tabulas ritināšanas apgabals">`.
  - *Substep C.2*: Implement CSS gradient scroll hints on wrapper boundaries indicating hidden horizontal content on mobile viewports.
  - *Substep C.3*: Write the vanilla JS toggle `toggleMatrixOcclusion(matrixId)` that attaches click handlers to `.cell-occlude` elements for interactive recall.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - The Four-Case Matrix maintains alignment and sticky headers on desktop viewports ($1440\\text{ px}$) and tablet viewports ($768\\text{ px}$).
  - Mobile viewport ($390\\text{ px}$) exhibits zero horizontal body scroll; table wrapper scrolls smoothly with visible edge indicators.
- **Acceptance Gate**:
  - All three targeted matrices strictly implement `synoptic-matrix-architect` patterns.
  - Cell occlusion mode functions without JavaScript console errors.

---

### TASK-12: Workspace Skills Integration — State Scrubber Lab for Dynamic Calorimetry & Thermodynamic Cycles

#### 1. Strategic Objective & Domain Scope
Deploy the workspace skill `state-scrubber-lab` to construct deterministic, interactive multi-phase state scrubbers in the master study document. Engineer two distinct interactive state machines: (1) The Solution Calorimetry 5-Phase Scrubber, visually guiding students through the experimental thermogram of acid-base neutralization; and (2) The Ideal Gas 4-Process Thermodynamic Cycle Scrubber, interactively demonstrating the conversion of heat into mechanical work. Link state transitions directly to synchronized SVG vector geometry and variable gauges.

#### 2. Deep Domain & Pedagogical Rationale
Thermodynamics is fundamentally the science of state transitions and path integrals. Medical students frequently struggle with static diagrams of dynamic laboratory experiments. In the calorimetry practical (L and LA), students fail to understand why the peak temperature is not the true end-state of the reaction and why linear regression extrapolation to the mixing instant $t_0$ is physically required to compensate for Newton cooling heat leaks. Similarly, understanding the Carnot cycle or general thermodynamic cycles requires observing how pressure, volume, temperature, and internal energy fluctuate synchronously. A deterministic state scrubber allows students to scrub back and forth through time and process stages, directly visualizing cause-and-effect relationships without video files or heavy external frameworks.

#### 3. Workspace Skills Applied & Technical Synergy
- `state-scrubber-lab`: Supplies the core architecture for state-machine scrubbers, parameter dials, and synchronized SVG geometry.
- `animate`: Provides smooth, low-overhead CSS transitions (120–160 ms) respecting `prefers-reduced-motion`.
- `cognitive-deload-auditor`: Synchronizes visual changes with concise, step-by-step explanatory prose panels.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Calorimetry 5-Phase Scrubber**:
  - Scrub slider and discrete step buttons for the 5 experimental phases:
    1. *Phase 0 (Pre-period)*: $t = 0\\text{–}40\\text{ s}$, baseline temperature equilibrium ($295.0\\text{ K}$), steady sensor trace.
    2. *Phase 1 (Mixing)*: $t = 40\\text{ s}$, acid poured into base, immediate chemical neutralization occurs.
    3. *Phase 2 (Exothermic Rise)*: $t = 40\\text{–}60\\text{ s}$, steep temperature increase as $1673.6\\text{ J}$ of heat is transferred to solution.
    4. *Phase 3 (Peak Temperature)*: $t = 60\\text{ s}$, maximum temperature attained ($297.15\\text{ K}$), cooling rate balances heat release.
    5. *Phase 4 (Post-period & Extrapolation)*: $t = 60\\text{–}180\\text{ s}$, slow exponential cooling; dashed regression line projects back to $t = 40\\text{ s}$ yielding true $\\Delta T = 2.0\\text{ K}$.
  - Synchronized SVG thermogram highlighting the active curve segment and moving an animated tracker crosshair along the coordinates.
- **Keyboard Navigation Controls**: Left/Right arrow keys advance or reverse the scrubber; spacebar toggles automatic playback.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Reactive Thermogram Curve**:
  - Integrates state-scrubber anchors directly into `figures.py` `OUT["trace"]`.
  - Defines dynamic SVG groups with IDs: `#trace-phase-0`, `#trace-phase-1`, `#trace-phase-2`, `#trace-phase-3`, `#trace-phase-4`.
  - Renders a reactive crosshair circle and callout tag that moves along the $(t, T)$ path as the scrubber advances.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author the state machine data structures in `build/script.js` defining phase metadata, coordinate points, and explanatory text strings.
- **Substep 2**: Build the state scrubber UI component in `build/instruments.html` with slider range inputs, step buttons, state description panels, and gauge readouts.
- **Substep 3**: Update `build/figures.py` and `build/style.css` to bind SVG element opacity and highlight classes to the active state.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Calorimeter State Machine Architecture**
  - *Substep A.1*: Define the JavaScript state array `calorimetryStates` in `build/script.js` containing the 5 phases with exact timestamps, temperatures, physical descriptions, and error implications.
  - *Substep A.2*: Code the scrubber update function `setCalorimeterPhase(phaseIndex)` that updates the slider value, activates the matching step button, and populates the narrative card.
  - *Substep A.3*: Add a live mathematical gauge showing instantaneous $T(t)$, elapsed time $t$, and the calculated extrapolated $\\Delta T$.
- **Subtask B: SVG Dynamic Binding & Visual Synchronization**
  - *Substep B.1*: Tag SVG curve segments in `build/figures.py` with corresponding `data-phase` attributes.
  - *Substep B.2*: In `setCalorimeterPhase`, dynamically update SVG classes, illuminating the active curve segment while dimming inactive phases to `var(--faint)`.
  - *Substep B.3*: Translate the SVG tracker crosshair to the exact coordinate point $(X(t), Y(T))$ of the current phase.
- **Subtask C: Accessible Keyboard Navigation & Static Fallback**
  - *Substep C.1*: Bind `keydown` listeners allowing students to step through the scrubber using Arrow keys with full ARIA live-region announcements (`aria-live="polite"`).
  - *Substep C.2*: Build a static, high-density 5-phase timeline table directly beneath the interactive component, serving as a complete static fallback when JavaScript is disabled or when printing.
  - *Substep C.3*: Style the scrubber controls with minimum $44\\text{ px}$ touch targets compliant with WCAG 2.2 touch target criteria.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - Stepping to Phase 0 displays $t = 20\\text{ s}, T = 295.0\\text{ K}$; Phase 3 displays $t = 60\\text{ s}, T = 297.15\\text{ K}$; Phase 4 displays extrapolated $T_{\\text{ext}} = 297.0\\text{ K}, \\Delta T = 2.0\\text{ K}$.
  - Playback completes without UI stutter; memory usage remains constant.
- **Acceptance Gate**:
  - Scrubber operates deterministically in both forward and reverse directions.
  - Static fallback table prints flawlessly in print preview without broken layout.

---

### TASK-13: Workspace Skills Integration — SVG Spatial Occlusion Workstation for Apparatus & Anatomy

#### 1. Strategic Objective & Domain Scope
Deploy the workspace skill `svg-spatial-occlusion` to upgrade the static apparatus and system vector diagrams in the master study document into interactive spatial-memory and image-occlusion workstations. Target three critical physical apparatus figures: (1) The Bomb Calorimeter Cutaway; (2) The Two-Beaker Solution Calorimeter Blueprint; and (3) The Thermodynamic System Boundaries Plate (Open, Closed, Isolated). Implement spatial pin masking, click-to-reveal testing, and automated recall scoring to solidify students' mastery of apparatus design prior to laboratory examinations.

#### 2. Deep Domain & Pedagogical Rationale
In the RSU laboratory practical and introductory test, students are tested on experimental apparatus anatomy: identifying the ignition wire, oxygen inlet, bomb vessel, water jacket, stirrer, Beckmann thermometer, inner beaker, outer insulating beaker, and air gap. Passive viewing of labeled diagrams results in rapid forgetting (the illusion of competence). Image occlusion—a proven active recall technique widely popularized by medical flashcard platforms like Anki—forces the brain to actively retrieve the identity and functional role of each physical component from memory. By building inline SVG spatial occlusion workstations directly into the master document, students can practice identifying apparatus parts and system boundary rules interactively without third-party apps or external software.

#### 3. Workspace Skills Applied & Technical Synergy
- `svg-spatial-occlusion`: Supplies the semantic structure for inline SVG pin masking, label callouts, and occlusion layer states.
- `interactive-study-guide`: Governs the study session state, recall score tracking, and pin reveal logic.
- `break-ui`: Ensures pins and callout tags scale proportionally without overlapping on mobile screens.

#### 4. Features & Interactive Add-on Innovations
- **Three-Mode Spatial Study Workstation**:
  - *Mode 1: Explore / Learn*: All labels are visible with leader lines connecting to components; hovering or tapping an apparatus part highlights its name, material, and thermodynamic function.
  - *Mode 2: Test All (Masked)*: All labels are concealed beneath numbered occlusion pins; clicking a pin flips it to reveal the correct label and functional description.
  - *Mode 3: Random Drill*: The workstation highlights one random component pin at a time, prompting the student to mentally name it before clicking "Rādīt atbildi", tracking session accuracy percentage.
- **Functional Role Inspection Drawer**: Clicking any revealed apparatus label opens a concise micro-panel explaining its thermodynamic purpose (e.g., *Air Gap*: minimizes conductive and convective heat losses between inner and outer beakers).

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Layered Bomb Calorimeter (`calorimeters`)**:
  - Re-architects the bomb calorimeter SVG in `figures.py` with semantic grouped layers: `#layer-shell`, `#layer-bomb`, `#layer-ignition`, `#layer-oxygen`, `#layer-stirrer`, `#layer-sensor`.
  - Places interactive occlusion pin targets (`circle` and `rect` masks) at precise coordinate anchors.
  - Features high-contrast occlusion badges with numbers ($1\\text{ to }8$) styled using `var(--accent)` and `var(--ink)`.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Refactor `build/figures.py` to embed structured occlusion pin anchors and data attributes into the calorimeter and system type SVGs.
- **Substep 2**: Author the interactive occlusion engine in `build/script.js` with mode switching (Learn, Test, Drill) and pin reveal state managers.
- **Substep 3**: Update `build/style.css` with pin styling, reveal transitions, and print-media rules ensuring all labels print unmasked.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: SVG Layering & Pin Coordinate Anchoring**
  - *Substep A.1*: Map exact coordinates for the 7 key components of the solution calorimeter: Inner beaker $(120, 200)$, Outer beaker $(95, 100)$, Thermometer sensor bulb $(300, 304)$, Stirrer $(180, 255)$, Solution $(120, 280)$, Air gap $(110, 150)$, Thermometer scale $(294, 40)$.
  - *Substep A.2*: Map exact coordinates for the 8 key components of the bomb calorimeter: Steel bomb $(620, 155)$, Sample crucible $(662, 240)$, Ignition wires $(674, 254)$, Oxygen valve $(760, 90)$, Water jacket $(560, 135)$, Outer insulation $(540, 105)$, Motorized stirrer, Beckmann thermometer.
  - *Substep A.3*: Embed `<g class="occlusion-pin" data-pin-id="...">` wrappers around each label, containing both the text label and the overlying mask rectangle.
- **Subtask B: Interactive Occlusion State Controller**
  - *Substep B.1*: Build the mode toolbar above each plate with buttons: "Mācīties (visi redzami)", "Pārbaudīt sevi (aizsegts)", "Nejaušs treniņš".
  - *Substep B.2*: Code click-to-reveal event handlers on pins: clicking an active mask applies `.revealed` to the group, transitioning opacity and displaying the hidden text.
  - *Substep B.3*: Implement session scoring: tracks total pins revealed and displays a summary score bar (e.g., "7/7 apgūti").
- **Subtask C: Accessibility & Print De-occlusion**
  - *Substep C.1*: Ensure all pins are keyboard-focusable (`tabindex="0"`) with `Enter` and `Space` activating reveal.
  - *Substep C.2*: Add ARIA attributes: `role="button"`, `aria-expanded="false"` (when masked), `aria-expanded="true"` (when revealed).
  - *Substep C.3*: In `@media print`, force `.occlusion-pin .mask { display: none !important; }` and `.occlusion-pin text { opacity: 1 !important; }`, guaranteeing that all labels are permanently visible in printouts and PDF exports.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - In "Test All" mode, clicking Pin 3 on the Bomb Calorimeter reveals "Aizdedzes vadi / paraugs".
  - In `@media print` preview, zero occlusion masks are rendered; all apparatus labels display cleanly with leader lines.
- **Acceptance Gate**:
  - All pins scale accurately on screen resize from $1440\\text{ px}$ down to $390\\text{ px}$.
  - Zero JavaScript errors during rapid mode switching.

---

### TASK-14: Workspace Skills Integration — Lexicon Morphology Weaver & Etymological Terminology Rail

#### 1. Strategic Objective & Domain Scope
Deploy the specialized workspace skill `lexicon-morphology-weaver` to build an authoritative scientific etymology and terminology morphology rail across the master document. Deconstruct the Greek and Latin roots of foundational physical and biochemical terms (*entropia*, *isobārs*, *isohors*, *isotermisks*, *adiabātisks*, *endergonisks*, *eksergonisks*, *katabolisms*, *anabolisms*, *homeostāze*). Purge all lingering Russianisms, obsolete medical terms (*siltumsaturs*), and typographical defects. Synthesize a publication-grade, bilingual Latvian-English Medical Chemistry Glossary with over 50 verified technical terms. Directly resolves **S3**, **S6**, **S7**, **S8**, **S21**, **S26**, **S29**, and **S30**.

#### 2. Deep Domain & Pedagogical Rationale
Medical terminology is deeply rooted in classical Greek and Latin. When first-year students encounter terms like *endergonisks* or *adiabātisks* as arbitrary strings of letters, they rely on rote memorization and frequently confuse them (e.g., calling an endothermic reaction "endergonic", or mixing up *isobārs* and *isohors*). Morphological decomposition unlocks the intrinsic physical meaning:
- *en-tropē* (Greek: $\\varepsilon\\nu$ = in, within + $\\tau\\rho\\omicron\\pi\\eta$ = turning, transformation) $\\implies$ transformation content / inward turning.
- *en-derg-on* (Greek: $\\varepsilon\\nu$ = in + $\\varepsilon\\rho\\gamma\\omicron\\nu$ = work) $\\implies$ requiring work to enter ($\Delta G > 0$).
- *ek-serg-on* (Greek: $\\varepsilon\\xi$ = out + $\\varepsilon\\rho\\gamma\\omicron\\nu$ = work) $\\implies$ releasing work outward ($\Delta G < 0$).
- *iso-bar-os* (Greek: $\\iota\\sigma\\omicron\\varsigma$ = equal + $\\beta\\alpha\\rho\\omicron\\varsigma$ = weight, pressure) $\\implies$ constant pressure ($p = \\text{const}$).
- *iso-chor-a* (Greek: $\\iota\\sigma\\omicron\\varsigma$ = equal + $\\chi\\omega\\rho\\alpha$ = space, volume) $\\implies$ constant volume ($V = \\text{const}$).
- *a-dia-bat-os* (Greek: $\\alpha$- = not + $\\delta\\iota\\alpha$ = through + $\\beta\\alpha\\iota\\nu\\omega$ = to go) $\\implies$ not passing through / impenetrable to heat ($Q = 0$).
- *kat-a-bol-e* (Greek: $\\kappa\\alpha\\tau\\alpha$ = down + $\\beta\\alpha\\lambda\\lambda\\omega$ = to throw) $\\implies$ throwing down / degrading complex molecules to simple ones.
- *an-a-bol-e* (Greek: $\\alpha\\nu\\alpha$ = up + $\\beta\\alpha\\lambda\\lambda\\omega$ = to throw) $\\implies$ throwing up / synthesizing complex cellular structures.
- *homeo-stasis* (Greek: $\\omicron\\mu\\omicron\\iota\\omicron\\varsigma$ = similar + $\\sigma\\tau\\alpha\\sigma\\iota\\varsigma$ = standing) $\\implies$ standing in a similar state (correcting the notes' false claim of Latin origin, S21).
Furthermore, standardizing Latvian chemical terms (*entalpija*, *stāvokļa parametri*, *īpatnējā siltumietilpība*, *veidošanās entalpija*, *dislāpekļa tetraoksīds*) eliminates the confusion caused by contradictory lecture slides and Soviet-era textbooks.

#### 3. Workspace Skills Applied & Technical Synergy
- `lexicon-morphology-weaver`: Formats terminology into aligned morphological decomposition rails with color-tagged prefixes, roots, and suffixes.
- `polish`: Refines Latvian scientific prose style, ensuring natural, idiomatic academic phrasing without Anglicisms or Russian sentence structures.
- `impeccable`: Implements the high-legibility tabular glossary layout with clear typographic delimiters.

#### 4. Features & Interactive Add-on Innovations
- **Interactive Morphological Root Explorer**: Hovering over or clicking a technical term in prose displays an elegant, non-intrusive micro-popover breaking down its prefix, root, language of origin (Greek vs Latin), literal translation, and exact modern physical definition.
- **Bilingual Terminology Filter & Search**: A live search bar in Chapter 14 allowing students to filter the glossary simultaneously by Latvian term, English equivalent, or classical root.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Classical Etymological Branching Tree**:
  - An inline SVG graphic (`viewBox="0 0 860 360"`) illustrating how common Greek roots branch into modern thermodynamic vocabulary (e.g., the root $\\varepsilon\\rho\\gamma\\omicron\\nu$ branching into *enerģija*, *eksergonisks*, *endergonisks*, and *ergonometriskais tests* in physiology).

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Rewrite Chapter 14 in `part_13_14.html`, structuring the comprehensive terminology correction table into three explicit columns: Sastopams (Found) $\\to$ Ieteicams (Recommended) $\\to$ Iemesls un etimoloģija (Reason & Etymology).
- **Substep 2**: Expand the Bilingual Latvian-English Glossary to $\\ge 50$ rigorous entries, providing exact definitions, unit dimensions, and exam pitfalls for every term.
- **Substep 3**: Update CSS and JavaScript to embed morphological span tagging and tooltips across all 16 chapters.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Classical Greek & Latin Morphological Rails**
  - *Substep A.1*: Author morphological breakdown cards for the 8 core process terms: *izobārs*, *izohors*, *izotermisks*, *adiabātisks*, *endergonisks*, *eksergonisks*, *entropija*, *homeostāze*.
  - *Substep A.2*: Format roots using semantic HTML: `<span class="morph"><span class="prefix">en-</span><span class="root">derg-</span><span class="suffix">-onisks</span></span>`.
  - *Substep A.3*: Add a dedicated correction block for *homeostāze*, explicitly citing Greek *homoios + stasis* and correcting K p.15.
- **Subtask B: Latvian Chemical Nomenclature Normalization**
  - *Substep B.1*: Enforce standard naming for state variables vs functions: $V, p, T, n, c$ are **stāvokļa lielumi (parametri)**; $U, H, S, G, F$ are **stāvokļa funkcijas** (correcting S26).
  - *Substep B.2*: Enforce standard thermal terms: eliminate *siltumsaturs* $\\to$ **entalpija**; *siltumkapacitāte* $\\to$ **īpatnējā siltumietilpība** ($c$); *rašanās siltums* $\\to$ **veidošanās entalpija** ($\\Delta_f H^\\circ$).
  - *Substep B.3*: Enforce chemical compound names: rename $\\text{N}_2\\text{O}_4$ to **dislāpekļa tetraoksīds**; rename Cl⁻ to **hlorīda jons**; standardize amino acid abbreviations: **Leu**, **Gly**, **Leu-Gly** (correcting U Q3's non-standard "Lei", S30).
- **Subtask C: 50+ Term Bilingual Medical Chemistry Glossary**
  - *Substep C.1*: Compile the master glossary list covering all foundational concepts: Open/Closed/Isolated System, State Function, Internal Energy, Enthalpy, Entropy, Gibbs Energy, Helmholtz Energy, Spontaneous, Equilibrium, Steady State, Heat, Work, Specific Heat Capacity, Calorimeter, Bomb Calorimeter, Standard State, Formation Enthalpy, Combustion Enthalpy, Coupled Reactions, Endergonic, Exergonic, Exothermic, Endothermic, Adiabatic, Isobaric, Isochoric, Isothermal, Reversible, Microstate, Phosphoryl Group Transfer Potential, Limiting Reagent, Respiratory Quotient, Atwater Factors, etc.
  - *Substep C.2*: Format each glossary item with phonetic cues, English translation, definition, and typical student misconception.
  - *Substep C.3*: Cross-link glossary terms to their primary chapter sections using anchor tags.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - The string *siltumsaturs* appears 0 times outside historical correction blocks.
  - The string *enderģisk* or *ekserģisk* appears 0 times outside quotation notes.
  - Greek etymology of homeostasis is explicitly affirmed; Latin origin is corrected.
- **Acceptance Gate**:
  - Chapter 14 contains $\\ge 50$ distinct, fully defined bilingual entries.
  - Morphological rails render cleanly with clear visual demarcation of prefixes and roots.

---

### TASK-15: Workspace Skills Integration — Cognitive Deload Auditor & Dual-Coding Layout Architecture

#### 1. Strategic Objective & Domain Scope
Deploy the specialized workspace skill `cognitive-deload-auditor` to systematically audit, restructure, and visually refine the entire master study document for optimal cognitive efficiency. Eliminate extraneous cognitive load, eradicate split-attention effects between equations and legends, enforce dual-coding concept architecture (pairing every abstract mathematical rule with a visual schema and concrete clinical example), implement redundant visual sign-coding, and chunk dense paragraphs into scannable, intellectually digestible arguments.

#### 2. Deep Domain & Pedagogical Rationale
Cognitive Load Theory (Sweller) demonstrates that working memory is strictly limited ($\approx 4\\text{–}7$ discrete information elements). In first-year medical chemistry, students face immense intrinsic cognitive load: navigating abstract mathematical symbols ($U, H, S, G$), sign rules ($+, -$), temperature units ($\text{K}$ vs $^\circ\text{C}$), energy orders of magnitude ($\text{J}$ vs $\text{kJ}$), and biological contexts. When study materials introduce *extraneous* cognitive load—such as separating an equation from the definitions of its symbols, burying key rules inside unbroken walls of dense prose, or using ambiguous color encodings—working memory is exhausted before chemical comprehension can occur. By applying cognitive deloading principles, every equation becomes self-contained (adjacent legend, units, and worked example), every rule is dual-coded, and visual signaling guides the reader's attention directly to the core principles.

#### 3. Workspace Skills Applied & Technical Synergy
- `cognitive-deload-auditor`: Guides the systematic audit of split-attention, visual hierarchy, signaling, and chunking.
- `tufte-margin-scholar`: Places secondary notes, historical context, and technical caveats in reserved marginal gutters, keeping the main reading path unburdened.
- `impeccable`: Governs whitespace distribution, typographic measure ($60\\text{–}68\\text{ ch}$), and line-height balance ($1.55\\text{–}1.65$).

#### 4. Features & Interactive Add-on Innovations
- **Dual-Coding Concept Infocards**: Compact, visually framed modular cards for core laws (1st Law, Hess, 2nd Law, Gibbs, 3rd Law) combining:
  - The Mathematical Formula in large, crisp semantic MathML.
  - An Adjacent Parameter Legend with explicit SI units.
  - A 1-Sentence Verbal Rule explaining the physical meaning.
  - A Miniature SVG Schematic illustrating the physical mechanism.
  - A Concrete Clinical / Biological Example.
  - The Classic Student Trap (Biežākā kļūda) highlighted in red.
- **Focus Mode / Density Toggle**: A UI control allowing students to switch between "Standard Study View" (full prose, historical notes, derivations) and "High-Yield Cram View" (condensing text to core infocards, formulas, and ledgers for rapid pre-exam review).

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Enhanced Vector Plate: Redundant Sign-Coding Architecture**:
  - Standardizes visual encoding across all SVG figures:
    - Exothermic / Exergonic: Mercury-red color (`var(--accent)`), negative sign prefix ($-$), directional down-arrow, solid line.
    - Endothermic / Endergonic: Cool slate/ink color (`var(--ink)`), positive sign prefix ($+$), directional up-arrow, dashed line.
  - Guarantees that colorblind students or monochrome printouts convey identical thermodynamic meaning without ambiguity.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Perform a systematic prose-density audit across all 16 chapters; break down all paragraphs longer than 4 sentences into numbered steps, comparison bullet points, or structured spec tables.
- **Substep 2**: Reformat every mathematical equation into an integrated dual-coding block containing adjacent symbol definitions, units, and a worked ledger.
- **Substep 3**: Update CSS and markup to enforce redundant sign cues (color + sign + text + line style) across all tables, callouts, and SVG plates.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Split-Attention Elimination & Equation Co-location**
  - *Substep A.1*: Audit every formula occurrence ($\\Delta U = Q - A$, $H = U + pV$, $\\Delta G = \\Delta H - T\\Delta S$, $q = cm\\Delta T$, $\\Delta G^\\circ = -RT \\ln K$); place an aligned definition ledger directly adjacent to the equation.
  - *Substep A.2*: Ensure every symbol row lists: Symbol, Name, SI Unit, Physical Role, and Sign Meaning.
  - *Substep A.3*: Eliminate all references requiring students to scroll backwards or search other chapters for basic symbol meanings.
- **Subtask B: Paragraph Chunking & Visual Signaling**
  - *Substep B.1*: Enforce the strict rule: maximum 4 sentences per prose paragraph; convert chronological procedures (e.g., calorimetry steps) into numbered `<ol>` lists.
  - *Substep B.2*: Implement typographic signaling: bold the first 2–4 words of key explanatory sentences (*lead-in signaling*) to allow fast visual skimming during revision.
  - *Substep B.3*: Standardize all semantic callout boxes into three distinct roles with dedicated visual left borders: **Noteikums** (Rule, $3\\text{ px}$ dark border), **Biežākā kļūda** (Mistake, $4\\text{ px}$ mercury-red border), **Pārbaudīts** (Verified, $2\\text{ px}$ muted border).
- **Subtask C: Dual-Coding Infocard Implementation**
  - *Substep C.1*: Design the HTML/CSS template for the Dual-Coding Infocards in `build/style.css` using zero-gradient flat framing.
  - *Substep C.2*: Deploy infocards at the start of Chapters 2, 3, 4, 5, 6, 7, 8, 10, and 11.
  - *Substep C.3*: Verify that infocards reflow cleanly without text truncation across mobile ($390\\text{ px}$) and desktop ($1440\\text{ px}$) viewports.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - Zero paragraphs exceed 4 sentences in length across Chapters 1 through 12.
  - Every equation is followed immediately by an aligned symbol legend.
  - Redundant sign coding is present on 100% of signed quantities.
- **Acceptance Gate**:
  - Document successfully passes the cognitive deload audit checklist.
  - High-yield infocards are present for all 7 RSU course learning outcomes.
"""
