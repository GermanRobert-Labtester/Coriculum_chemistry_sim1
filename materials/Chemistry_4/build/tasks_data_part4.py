# ruff: noqa: E501
"""Detailed specifications for Tasks 16 through 20."""

TASKS_PART4 = """
---

### TASK-16: Workspace Skills Integration — Print CSS Alchemist & Publication-Grade PDF Architecture

#### 1. Strategic Objective & Domain Scope
Deploy the specialized workspace skill `print-css-alchemist` to engineer an uncompromising, dual-target screen and publication-grade print architecture. Transform the master HTML document into a flawlessly paginated physical study manual and PDF export artifact. Implement automated unfolding of all `<details>` disclosure widgets via `window.onbeforeprint` and `window.onafterprint` lifecycle handlers, enforce ink-safe monochrome styling, eliminate widow/orphan headings, suppress table row splits mid-page, embed running headers and page counters via `@page`, and generate a dedicated, high-density 1-Page Printable Exam Formula & Rule Sheet.

#### 2. Deep Domain & Pedagogical Rationale
Medical students frequently print study packets or export HTML to PDF for offline annotation on tablet devices (e.g., Apple iPad GoodNotes, Notability). Standard web documents fail catastrophically when printed: interactive `<details>` elements remain collapsed (hiding critical explanations, derivations, and self-test answers), dark backgrounds consume massive quantities of black printer ink, multi-row calculation ledgers split awkwardly across page margins leaving orphaned total rows, and fixed navigation sidebars overlap body text. By deploying `print-css-alchemist`, the master document behaves intelligently: on screen, it offers an interactive, collapsible, dark-mode-capable digital monograph; on print trigger (Ctrl+P / Cmd+P), it instantly transitions into a pristine, ink-efficient, beautifully typeset academic manual.

#### 3. Workspace Skills Applied & Technical Synergy
- `print-css-alchemist`: Provides the automated state-unfolding lifecycle scripts, `@media print` rules, and print pagination architecture.
- `pdf-vector-surgeon`: Ensures that inline SVG vector graphics adapt dynamically to print media, maintaining hairline precision and scalable line weights.
- `impeccable`: Governs the print typographic scale, margins, and contrast ratios.

#### 4. Features & Interactive Add-on Innovations
- **Automated Lifecycle Print Unfolding**:
  - `window.onbeforeprint`: Automatically scans the DOM, records the prior open/closed state of all `<details>` tags, and expands them fully so that all derivations, worked solutions, and self-test answers are printed.
  - `window.onafterprint`: Instantly restores the user's prior open/closed toggle states, returning the screen UI to its exact pre-print configuration.
- **Dedicated Printable 1-Page Cheat Sheet Generator**:
  - A dedicated print view triggered via a "Drukāt formulu kopsavilkumu" button that isolates Appendix A (Formulu lapa) into a compact, ultra-dense 2-column landscape or portrait summary sheet designed to fit exactly onto a single double-sided A4 page.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Print-Adaptive Vector Graphic Styling**:
  - Injects print-specific CSS into SVG plates:
    - Replaces low-contrast grey lines (`var(--muted)`) with crisp black hairlines (`#000000`, `0.75pt`).
    - Converts shaded background fills (`var(--surface)`, `var(--surface-2)`) into pure white or subtle hatching patterns (`stroke-dasharray="2 2"`).
    - Preserves the bold red zero line as a dark solid rule with text markers ($y = 0$).

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author the JavaScript print lifecycle handlers (`openForPrint` and `restoreAfterPrint`) in `build/script.js`.
- **Substep 2**: Rebuild the `@media print` section in `build/style.css` using `print-css-alchemist` rules, establishing `@page` margins, running headers, and page-break rules.
- **Substep 3**: Verify print rendering by exporting a full-document PDF via headless Chromium, inspecting all pages for zero content clipping or orphan headings.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: JavaScript Print Lifecycle & State Persistence**
  - *Substep A.1*: Code `openForPrint()`: queries all `details` elements, stores their `open` attribute state in a WeakMap, and sets `open = true` across the entire document.
  - *Substep A.2*: Code `restoreAfterPrint()`: iterates over the WeakMap, restoring the exact pre-print `open` state.
  - *Substep A.3*: Bind listeners to both `window.addEventListener('beforeprint', ...)` and `window.matchMedia('print').addListener(...)` for cross-browser reliability.
- **Subtask B: Paged Media CSS & Layout Pagination**
  - *Substep B.1*: Declare `@page` rules in `build/style.css`: size A4 portrait, margins $15\\text{ mm}$ top/bottom, $12\\text{ mm}$ left/right.
  - *Substep B.2*: Add running header and footer via CSS Paged Media: `@top-center { content: "Medicīniskā ķīmija · 4. tēma: Termodinamika"; font-size: 8pt; color: #444; }` and `@bottom-right { content: "Lappuse " counter(page) " no " counter(pages); font-size: 8pt; }`.
  - *Substep B.3*: Apply strict page-break controls: `h1, h2, h3 { break-after: avoid; }`, `tr, .ledger-table, .fig-box, .infocard, .callout { break-inside: avoid; }`.
- **Subtask C: Ink-Safe Style Normalization & Cheat Sheet Layout**
  - *Substep C.1*: Force background colors to pure white (`background: #ffffff !important`) and text to pure carbon black (`color: #111111 !important`) in `@media print`.
  - *Substep C.2*: Hide digital-only elements: skip link, theme toggles, interactive sliders, audio controls, and the sticky table of contents rail (`display: none !important`).
  - *Substep C.3*: Format Appendix A (1-page formula sheet) with dense two-column layout (`column-count: 2; column-gap: 8mm`), ensuring it fits exactly onto a single sheet of paper.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - Headless Chrome print command (`google-chrome --headless --print-to-pdf=test.pdf Master_4_temats_termodinamika.html`) executes with exit code 0.
  - All 101 `<details>` elements are verified open in the generated PDF.
  - Zero text or table elements are clipped by page margins.
- **Acceptance Gate**:
  - PDF export contains zero dark backgrounds; ink consumption is strictly minimized.
  - Running headers and page numbers render correctly on all pages beyond the title page.

---

### TASK-17: Anti-AI Slop Aesthetic Redesign & Precision Scientific Energy Ledger Texturing

#### 1. Strategic Objective & Domain Scope
Purge all generic "AI template slop" visual tells and generic web clichés from the master study document, strictly adhering to the design contract in PROMPT §6 and `workspace_skills/design-taste-frontend/references/tells.md`. Engineer a bespoke, intellectually serious, and calm scientific aesthetic: "The Precision Energy Ledger & Laboratory Monograph". Eliminate all floating drop shadows, candy-colored pill badges, generic card grids, gradient text headers, emojis, and marketing buzzwords. Implement a cool low-chroma slate-cyan substrate, deep carbon-indigo ink, a single mercury-red accent, strict baseline grids, tabular lining numerals, and prominent data zero lines.

#### 2. Deep Domain & Pedagogical Rationale
First-year medical students are preparing for demanding, high-stakes medical examinations. When digital study tools look like trendy software marketing landing pages—complete with floating cards, purple gradients, playful emojis, and bouncing animations—they subvert academic authority and induce visual fatigue. Thermodynamics is fundamentally about the accounting of energy and signs: what enters, what leaves, and what the net ledger yields. The design of the master document should mirror this essence: structured like a high-precision scientific field journal and laboratory ledger. Information structure should emerge from whitespace, scale, typographic weight, and ruled data lines, not decorative boxes. Eliminating visual noise respects the student's intellect and maximizes sustained focus.

#### 3. Workspace Skills Applied & Technical Synergy
- `design-taste-frontend`: Enforces zero tolerance for template tells, AI artifacts, and visual decoration.
- `industrial-brutalist-ui`: Informs the restrained, data-dense ledger layout, visible hairlines, and functional typographic hierarchies.
- `impeccable`: Balances typographic scale, line measure ($60\\text{–}68\\text{ ch}$), and WCAG relative luminance contrast ratios.

#### 4. Features & Interactive Add-on Innovations
- **High-Fidelity Accessible Theme Engine**:
  - Fully bespoke Light and Dark themes implemented via `oklch()` color tokens with robust hex fallbacks:
    - *Light Scheme*: Substrate `oklch(0.968 0.006 210)` (cool, low-chroma slate-cyan, never warm cream or yellowed paper); Ink `oklch(0.22 0.025 240)` (deep carbon-indigo); Accent `oklch(0.50 0.19 27)` (mercury thermometer red, measured $\ge 4.5:1$ contrast against ground).
    - *Dark Scheme*: Substrate `oklch(0.18 0.015 220)` (deep slate-charcoal, never OLED jet-black); Ink `oklch(0.92 0.008 210)` (soft linen-white); Accent `oklch(0.72 0.17 27)` (luminous coral-red, contrast $\ge 5.0:1$).
  - Zero layout shift during theme toggling; theme choice persisted in `localStorage`.
- **Strict Data Zero-Line Highlighting**:
  - Every calculation ledger, table, and vector chart features a signature visual zero line (`var(--accent)`), grounding every spontaneity verdict and enthalpy sum against the universal thermodynamic baseline.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Unified Scientific Vector Styling Tokens**:
  - Replaces arbitrary SVG inline styles with global CSS variable inheritance:
    - Axis lines: `stroke: var(--muted); stroke-width: 1.2px;`
    - Grid lines: `stroke: var(--rule); stroke-width: 1.0px; stroke-dasharray: 2 4;`
    - Zero line: `stroke: var(--accent); stroke-width: 2.2px;`
    - Primary reaction curve: `stroke: var(--ink); stroke-width: 2.4px;`
    - Typography inside SVG: strictly inherits the page font family (*Source Serif 4*), eliminating mismatched system font rendering.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Run a comprehensive grep audit across `build/style.css`, purging all forbidden properties: `box-shadow`, `text-shadow`, `linear-gradient`, `radial-gradient`, and border radii larger than $4\\text{ px}$.
- **Substep 2**: Rebuild the color token architecture in `:root` using verified `oklch()` values with exact hex fallbacks for light and dark color schemes.
- **Substep 3**: Enforce tabular lining numerals (`font-variant-numeric: tabular-nums lining-nums`) across all tables, ledgers, and SVG text elements.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Purging AI Template Tells & Decoration**
  - *Substep A.1*: Audit prose across all parts: eradicate marketing copy tells («Field notes», «Dive in», «Unlock», «seamless», «Šajā nodaļā mēs…», «Pamatlikumi vienā vietā», fake testimonials, emoji bullets).
  - *Substep A.2*: Strip all rounded pill tags (`border-radius: 9999px`) and circular numbered medallions on headings; headings must use clean, plain Latvian numerals (`7. Gibsa enerģija`).
  - *Substep A.3*: Remove all card grid bento layouts; structure content linearly as a monograph with a left-aligned reading column and sticky table of contents rail.
- **Subtask B: Typographic & Numerical Precision Texturing**
  - *Substep B.1*: Set body font to *Source Serif 4* at $17\\text{–}19\\text{ px}$, line height $1.58$, measure max $68\\text{ ch}$; headings set in the same family, heavier weight, left-aligned, sentence case.
  - *Substep B.2*: Enforce true typographical Unicode minus characters (`−`, `U+2212`) across all signed numbers, eliminating ugly hyphen-minus keys (`-`).
  - *Substep B.3*: Format all decimals with the Latvian standard comma (e.g., `28,05 kJ/mol`), separated from the unit by a non-breaking space (`&nbsp;`).
- **Subtask C: Contrast Ratio Measurement & Theme Polish**
  - *Substep C.1*: Measure WCAG relative luminance contrast for Light Scheme: Ink on Ground ($\approx 12.8:1$, exceeds $4.5:1$); Muted on Ground ($\approx 5.8:1$); Accent on Ground ($\approx 4.8:1$).
  - *Substep C.2*: Measure WCAG contrast for Dark Scheme: Ink on Ground ($\approx 11.5:1$); Accent on Ground ($\approx 5.2:1$).
  - *Substep C.3*: Document the measured contrast ratios in Section 16 of the master document as verifiable proof of compliance.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - `grep -E 'box-shadow|text-shadow|gradient' build/style.css` returns 0 hits.
  - `grep -E '[\U00010000-\U0010ffff]' build/part_*.html` returns 0 hits (zero emojis).
  - All body text and accent colors achieve WCAG AA ($\ge 4.5:1$) in both light and dark modes.
- **Acceptance Gate**:
  - Automated `lint.mjs` checks from `design-taste-frontend` pass with 0 FAIL across $1440\\text{ px}$, $768\\text{ px}$, and $390\\text{ px}$.
  - The design reads strictly as an authentic scientific energy ledger monograph.

---

### TASK-18: Interactive Add-on Suite — Multi-Variable Thermodynamic Calculators & Dynamic Sandbox

#### 1. Strategic Objective & Domain Scope
Architect and implement a high-performance, zero-dependency, vanilla JavaScript calculation and simulation suite embedded directly within the master document. Build four reactive calculation engines: (1) The Multi-Variable $\\Delta G(T)$ Spontaneity & Crossover Sandbox; (2) The Multi-Reaction Hess Cycle & Thermochemical Equation Solver; (3) The Virtual Solution Calorimetry Simulator with Limiting Reagent & Error Budget Analyzer; and (4) The Food Calorie & Nutritional RQ Metabolic Energy Converter. Incorporate input sanitization accepting both European decimal commas and Anglo-American decimal points, dynamic unit conversions, and real-time test-vector assertion runners.

#### 2. Deep Domain & Pedagogical Rationale
While static worked examples teach passive comprehension, interactive calculation sandboxes empower students to develop genuine chemical intuition. By manipulating continuous sliders for enthalpy, entropy, and temperature, students actively witness the mathematical tug-of-war between the enthalpy term ($\\Delta H$) and the entropy term ($-T\\Delta S$). They observe in real time how an endothermic reaction suddenly transitions across the zero line into exergonic territory as temperature rises, and see why reactions with $\\Delta S < 0$ become non-spontaneous at elevated temperatures. Building these tools directly in vanilla JavaScript without bloated external libraries ensures that the document remains 100% self-contained, lightning-fast, and completely operational offline in any laboratory or hospital environment.

#### 3. Workspace Skills Applied & Technical Synergy
- `prototype`: Drives the rapid, functional development of reactive input controls and calculation state machines.
- `frontend-design`: Structures the clean, brutalist interface for input panels, parameter boxes, and output ledgers.
- `break-ui`: Ensures that inputs, sliders, and result displays scale smoothly without breaking container boundaries on mobile devices.

#### 4. Features & Interactive Add-on Innovations
- **Flexible Decimal Sanitizer**: Automatically parses input strings containing either commas (`28,05`) or dots (`28.05`), stripping accidental whitespace or unit suffixes, preventing NaN errors.
- **Integrated Unit Conversion Shields**: Alerts students with visual warning cues if entered numbers appear in the wrong unit order (e.g., if entropy is entered in $\\text{kJ}$ rather than $\\text{J}$, an alert prompts: *«Vai $\\Delta S$ ir ievadīts J/(mol·K)? Mazāks par 1 liecina par kJ kļūdu!»*).
- **Automated Live Console Test-Vector Runner**: A visible button ("Palaist pārbaudes testus") and underlying console runner that executes certified test vectors against all four calculation engines, displaying a green pass badge in the UI.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Reactive SVG Data Visualizer**:
  - Dynamically binds the $\\Delta G(T)$ calculator output to an inline SVG line graph.
  - As the student moves the temperature slider or adjusts $\\Delta H$ and $\\Delta S$, the slope ($- \\Delta S$) and y-intercept ($\\Delta H$) of the SVG line instantly rotate and translate in real time.
  - Renders a live animated indicator dot at the exact coordinate $(T_{\\text{user}}, \\Delta G_{\\text{calc}})$.

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author the core mathematical engine functions (`calcDeltaG`, `calcHessCycle`, `calcCalorimetry`, `calcNutrition`) in `build/script.js`.
- **Substep 2**: Build the semantic HTML interface containers for all four instruments in `build/instruments.html` with full ARIA accessibility bindings.
- **Substep 3**: Embed the JSON test-vector dataset (`thermo-test-vectors`) and author the automated assertion suite validating all calculations.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Multi-Variable $\\Delta G(T)$ Engine (Instrument A Upgrade)**
  - *Substep A.1*: Code `calcDeltaG(dH, dS, T)`: computes $\\Delta G = \\Delta H - T(\\Delta S / 1000)$, determines Case 1–4, and computes $T_{\\text{cross}} = (\\Delta H \\times 1000) / \\Delta S$.
  - *Substep A.2*: Attach event listeners to $\\Delta H$, $\\Delta S$, and $T$ inputs with debounced rendering ($16\\text{ ms}$, $60\\text{ fps}$).
  - *Substep A.3*: Implement real-time SVG slope update translating the line equation $y = mx + b$ into SVG line endpoints $(x_1, y_1)$ and $(x_2, y_2)$.
- **Subtask B: Multi-Reaction Hess Cycle Solver (Instrument B Upgrade)**
  - *Substep B.1*: Build the dynamic tabular ledger allowing students to enter or edit chemical reaction rows: Stoichiometric coefficient $\\nu$, Chemical formula, $\\Delta_f H^\\circ$, $S^\\circ$, and Phase state.
  - *Substep B.2*: Compute net reaction parameters: $\\Delta_r H^\\circ = \\sum \\nu \\Delta_f H^\\circ(\\text{prod}) - \\sum \\nu \\Delta_f H^\\circ(\\text{react})$, $\\Delta_r S^\\circ = \\sum \\nu S^\\circ(\\text{prod}) - \\sum \\nu S^\\circ(\\text{react})$, and $\\Delta_r G^\\circ = \\Delta_r H^\\circ - T\\Delta_r S^\\circ$.
  - *Substep B.3*: Pre-populate the solver with a dropdown menu containing all six seminar tasks from U Q6.
- **Subtask C: Virtual Calorimetry Practical Simulator (Instrument C Upgrade)**
  - *Substep C.1*: Code the acid-base calorimetry engine: computes limiting reagent between base ($V_b, c_b$) and acid ($V_a, c_a$), total solution mass ($m = V_a + V_b$), total heat absorbed $q = (c \\cdot m + C_{\\text{kal}})\\Delta T$, and molar reaction enthalpy $\\Delta H_r = -q / n_{\\text{lim}}$.
  - *Substep C.2*: Implement dynamic error analysis comparing experimental result against theoretical $-56.19\\text{ kJ/mol}$, calculating percentage deviation and the ideal temperature rise $\\Delta T_{\\text{teor}}$.
  - *Substep C.3*: Integrate input guards preventing negative volumes or impossible concentrations ($> 18\\text{ M}$).

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - Test Vector A.1: $(210\\text{ kJ/mol}, 216\\text{ J/(mol}\\cdot\\text{K)}, 298.15\\text{ K}) \\implies \\Delta G = +145.60\\text{ kJ/mol}$, $T_{\\text{cross}} = 972.2\\text{ K}$, Case 3.
  - Test Vector A.2: $(28.05\\text{ kJ/mol}, 108.72\\text{ J/(mol}\\cdot\\text{K)}, 298.15\\text{ K}) \\implies \\Delta G = -4.36\\text{ kJ/mol}$, $T_{\\text{cross}} = 258.0\\text{ K}$, Case 3.
  - Test Vector C.1: $(0.200\\text{ M}, 160.0\\text{ mL}, 1.00\\text{ M}, 40.0\\text{ mL}, \\Delta T = 2.0\\text{ K}, C_{\\text{kal}} = 0) \\implies q = 1673.6\\text{ J}, n = 0.032\\text{ mol}, \\Delta H_r = -52.3\\text{ kJ/mol}, \\text{Error} = 6.92\\%$.
  - Test Vector C.2: Same with $C_{\\text{kal}} = 20\\text{ J/K} \\implies q = 1713.6\\text{ J}, \\Delta H_r = -53.55\\text{ kJ/mol}, \\text{Error} = 4.70\\%$.
- **Acceptance Gate**:
  - All test vectors execute via the in-browser self-test script and report PASS in the console.
  - Zero external JavaScript dependencies; total script size remains $\\le 30\\text{ KB}$.

---

### TASK-19: Comprehensive Vector Plate Expansion — Adding 10+ Precision Inline SVGs

#### 1. Strategic Objective & Domain Scope
Dramatically expand the visual and pedagogical fidelity of the master study document by designing, engineering, and embedding at least 10 brand-new, publication-grade inline SVG vector plates. Fill all critical visual voids in the theoretical narrative, covering abstract concepts that currently exist only as dense text paragraphs: (1) Carnot Heat Engine vs Biological Isothermal Cell; (2) Free Energy vs Reaction Extent Curve $G(\\xi)$ showing equilibrium minimum; (3) Electrostatic Charge Relief & Resonance Delocalization in ATP; (4) Protein Folding & Hydrophobic Effect Entropy-Enthalpy Compensation; (5) Complete Glucose Catabolism Energetics Ledger; (6) Prigogine Dissipative Structure Negentropy Flux; (7) Water Neutralization Discrepancy Cycle; (8) Phase Transition Enthalpy/Entropy Stepped Profiles; (9) Gas Expansion Work Area ($p\\Delta V$) across 4 Processes; and (10) Limiting Reagent Titration Enthalpy Curve.

#### 2. Deep Domain & Pedagogical Rationale
Dual-Coding Theory (Paivio) proves that human memory stores information through two parallel, mutually reinforcing channels: linguistic (prose, formulas) and non-verbal (spatial, visual schemas). The existing master HTML document contains 10 SVGs, but several of the most difficult, abstract concepts in the medical chemistry syllabus remain entirely unvisualized:
- *Why living cells are not heat engines*: A biological cell operates under virtually isothermal conditions ($\\Delta T \\approx 0$ across a $10\\,\\mu\\text{m}$ diameter). A Carnot heat engine requires a temperature gradient ($T_H > T_C$) to extract work ($\eta = 1 - T_C/T_H$). Cells cannot function as heat engines; they are **chemical engines** performing direct isothermal chemomechanical and chemiosmotic transduction!
- *Dynamic equilibrium as a free energy minimum*: Students confuse $\\Delta G = 0$ with $\\Delta G^\\circ = 0$. A visual curve of total Gibbs energy $G$ plotted against reaction extent $\\xi$ from pure reactants to pure products vividly reveals that the minimum of the curve represents equilibrium, where $(\\partial G / \\partial \\xi)_{T,p} = 0$, and the slope at any point is $\\Delta G$.
- *The Hydrophobic Effect in Protein Folding*: Medical students frequently wonder why protein folding (which orders the polypeptide backbone into an $\\alpha$-helix or $\\beta$-sheet, $\\Delta S_{\\text{chain}} < 0$) occurs spontaneously. The answer is the hydrophobic effect: burying non-polar side chains releases structured clathrate water cages back into bulk solvent, resulting in a massive positive solvent entropy gain ($\\Delta S_{\\text{solvent}} \\gg 0$), driving $\\Delta S_{\\text{total}} > 0$.
Visualizing these foundational concepts with precise vector plates transforms abstract mathematical statements into unforgettable mental models.

#### 3. Workspace Skills Applied & Technical Synergy
- `artifact-diagramming`: Governs the structural composition, flow logic, and visual clarity of complex chemical diagrams.
- `dataviz`: Sets exact coordinate frames, numerical tick intervals, and aspect ratios.
- `pdf-vector-surgeon`: Ensures that all newly authored SVG paths use crisp, clean vector geometry that prints and renders flawlessly at any scale.

#### 4. Features & Interactive Add-on Innovations
- **Vector Plate Inspection & Zoom Drawer**: A lightweight modal/drawer allowing students to expand any SVG plate to full-screen width, revealing detailed technical footnotes, mathematical derivations, and high-resolution callout anchors.
- **Layer Toggle Controls**: On complex plates (e.g., Glucose Catabolism Ledger), students can toggle layers on and off to isolate individual metabolic phases (Glycolysis, Krebs Cycle, Oxidative Phosphorylation).

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Complete Inventory of the 10 New SVG Plates**:
  1. `FIG:carnot_vs_cell`: Heat engine with thermal gradient vs isothermal cell chemiosmotic coupling (`viewBox="0 0 900 420"`).
  2. `FIG:reaction_extent_g`: Parabolic curve $G(\\xi)$ showing equilibrium minimum where $(\\partial G/\\partial \\xi) = 0$ (`viewBox="0 0 860 400"`).
  3. `FIG:atp_charge_relief`: Structural chemical formulas illustrating Coulombic repulsion relief and orthophosphate resonance forms (`viewBox="0 0 920 440"`).
  4. `FIG:protein_folding_entropy`: Unfolded polypeptide with rigid water clathrates vs folded protein with liberated disordered bulk water (`viewBox="0 0 880 400"`).
  5. `FIG:glucose_catabolism_ledger`: Complete metabolic waterfall from 1 mol glucose ($-2888\\text{ kJ/mol}$) partitioned into ATP synthesis ($\approx 32\\text{ ATP} \\approx 976\\text{ kJ}$, $\\eta \\approx 34\\%$) and metabolic thermogenesis (`viewBox="0 0 920 460"`).
  6. `FIG:prigogine_flux`: Solar photon flux ($5800\\text{ K}$) driving terrestrial negentropy import and waste infrared radiation ($288\\text{ K}$) (`viewBox="0 0 860 380"`).
  7. `FIG:water_neutralization_discrepancy`: Thermodynamic cycle comparing the course data loop against the NIST $K_w$ loop (`viewBox="0 0 860 380"`).
  8. `FIG:phase_transition_profiles`: Heating curve illustrating enthalpy plateaus ($\\Delta H_{\\text{fus}}, \\Delta H_{\\text{vap}}$) and corresponding entropy jumps (`viewBox="0 0 880 420"`).
  9. `FIG:work_integral_p_v`: Multi-panel $p-V$ diagram comparing work integrals under isobaric, isothermal, and adiabatic expansion (`viewBox="0 0 900 440"`).
  10. `FIG:limiting_reagent_titration`: Temperature rise plotted against acid volume added, demonstrating a sharp apex at the stoichiometric equivalence point ($0.032\\text{ mol}$) (`viewBox="0 0 860 400"`).

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author the procedural Python generation functions for all 10 new SVGs in `build/figures.py`.
- **Substep 2**: Re-run `build/figures.py` to compile the SVGs into `build/figures.html` and verify clean XML syntax and viewBox geometry.
- **Substep 3**: Insert the corresponding figure markers (`<!-- FIG:name -->`) into `build/part_top.html`, `build/part_6_9.html`, and `build/part_10_12.html`, and update `build/build_html.py`.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Bioenergetic & Biophysical Vector Plates (SVGs 1–4)**
  - *Substep A.1*: Code `fig_carnot_vs_cell`: draw high-temperature and low-temperature reservoirs for the heat engine; contrast with a cell membrane showing proton gradient ($\\Delta\\mu_{\\text{H}^+}$) driving ATP synthase at $T = 310\\text{ K}$.
  - *Substep A.2*: Code `fig_reaction_extent_g`: draw parabolic free energy curve $G$ against reaction extent $\\xi$; plot tangent lines showing $\\Delta G < 0$ (forward spontaneous), $\\Delta G > 0$ (reverse spontaneous), and horizontal tangent $\\Delta G = 0$ at equilibrium.
  - *Substep A.3*: Code `fig_atp_charge_relief` and `fig_protein_folding_entropy`: draw molecular structure outlines and solvent water cages using clean SVG geometric paths.
- **Subtask B: Metabolic & System Vector Plates (SVGs 5–7)**
  - *Substep B.1*: Code `fig_glucose_catabolism_ledger`: draw a multi-tiered stacked bar chart partitioning the $-2888\\text{ kJ/mol}$ free energy of glucose into glycolysis, citric acid cycle, electron transport chain, and heat dissipation.
  - *Substep B.2*: Code `fig_prigogine_flux`: construct the open-system entropy flux Sankey diagram showing solar input ($d_e S < 0$), internal metabolic production ($d_i S > 0$), and infrared heat export.
  - *Substep B.3*: Code `fig_water_neutralization_discrepancy`: build the closed thermodynamic cycle diagram contrasting Course vs NIST autoprotolysis data.
- **Subtask C: Physical Chemistry & Practical Plates (SVGs 8–10)**
  - *Substep C.1*: Code `fig_phase_transition_profiles`: plot temperature and entropy vs heat added, highlighting latent heat plateaus.
  - *Substep C.2*: Code `fig_work_integral_p_v`: construct side-by-side $p-V$ expansion plots with hatched integration polygons.
  - *Substep C.3*: Code `fig_limiting_reagent_titration`: plot the calorimetric neutralization titration curve showing $\\Delta T$ peaking at $V_{\\text{acid}} = 32.0\\text{ mL}$ for equivalent base, and plateauing when acid is in excess.

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - `figures.py` compiles all 20 figures (10 original + 10 new) without Python errors.
  - All SVG plates contain valid `<title>` and `<desc>` tags with matching `aria-labelledby` attributes.
  - Total character size of `build/figures.html` increases proportionally while remaining within the self-contained $1\\text{ MB}$ budget.
- **Acceptance Gate**:
  - All 10 new figures are embedded in their respective chapters and render cleanly across desktop and mobile browsers.
  - Zero overlapping text elements across all viewports.

---

### TASK-20: Active Recall Engine, Leitner Spaced-Repetition System & Final Verification Framework

#### 1. Strategic Objective & Domain Scope
Elevate the self-assessment framework (Chapter 15: Paškontrole) into an exhaustive, evidence-based active recall learning engine. Expand the closed recall prompt inventory from 78 to at least 120 items, achieving guaranteed 100% coverage of the 113 curricular concepts cataloged in `build/inventory.json`. Implement a Leitner-inspired, two-box spaced-repetition memory toggle («Zināju» / «Jāatkārto») stored in browser session state with real-time mastery score tracking. Build two full diagnostic assessments: an Introductory Diagnostic Pre-Test (Ievadtests) and a Comprehensive Final Mock Exam (Nobeiguma tests) evaluated against the official RSU $\\ge 55\\%$ passing threshold. Construct an automated pre-flight QA verification harness enforcing zero source defects and strict numerical parity.

#### 2. Deep Domain & Pedagogical Rationale
Cognitive psychology (Roediger & Karpicke) demonstrates that repeated active retrieval practice produces dramatically superior long-term retention and conceptual transfer compared to passive re-reading. In the RSU medical chemistry curriculum, the two computer-graded tests (Ievadtests before class, Nobeiguma tests after class) are high-stakes gates requiring $\\ge 55\\%$ to pass. Students who fail these tests are barred from the laboratory or receive academic penalties. Currently, Chapter 15 contains 78 items, leaving several critical learning outcomes under-tested (e.g., the Third Law, indirect calorimetry and $RQ$, Prigogine's entropy decomposition, and the limiting reagent logic). Expanding to $\\ge 120$ items guarantees that every single concept in the inventory has at least one active recall challenge. Implementing persistent «Zināju» and «Jāatkārto» buttons provides students with immediate metacognitive feedback, allowing them to focus their limited study time exclusively on unmastered concepts.

#### 3. Workspace Skills Applied & Technical Synergy
- `learn-then-test`: Governs the structural alignment between core theoretical prose and matching retrieval test items.
- `interactive-study-guide`: Directs the interactive state management, Leitner box sorting, and progress bar calculations.
- `audit`: Supplies the automated verification routines and statistical reporting metrics.

#### 4. Features & Interactive Add-on Innovations
- **Leitner Active Recall Engine**:
  - Every recall item features a toggle button pair: «Zināju» (I knew it) and «Jāatkārto» (Needs review).
  - Categorizes items into Box 1 (Mastered) and Box 2 (Review Queue), persisting state in browser session memory.
  - A real-time Mastery Dashboard at the top of Chapter 15 displays overall completion: e.g., *«Apgūti 94 no 120 jautājumiem (78%) · 26 atkārtošanai»*.
  - "Filtrēt: Rādīt tikai atkārtojamos" button dynamically hides mastered items, allowing targeted drills.
- **Diagnostic Mock Exam Modes**:
  - *Ievadtests Drill Mode*: A randomized 15-question quiz covering core definitions and qualitative rules, calculating pass/fail against the $55\\%$ threshold.
  - *Nobeiguma Tests Drill Mode*: A randomized 25-question comprehensive exam combining qualitative theory, calculation ledgers, and error analysis.

#### 5. SVG Plate Architecture & Corrected Vector Design
- **Interactive Knowledge Mastery Radial / Matrix SVG**:
  - An inline SVG graphic (`viewBox="0 0 860 240"`) embedded in the Chapter 15 dashboard.
  - Displays real-time mastery percentages across all 7 RSU course learning outcomes (O1 to O7) as filled progress arcs or matrix bars.
  - Updates dynamically via JavaScript as the student marks items «Zināju».

#### 6. 3 Main Task Execution Substeps
- **Substep 1**: Author at least 42 new, high-yield retrieval items in `build/part_15.html`, bringing the total count to $\\ge 120$ items and covering 100% of `build/inventory.json`.
- **Substep 2**: Build the interactive Leitner session manager, mastery dashboard, and mock exam test runners in `build/script.js`.
- **Substep 3**: Assemble the master pre-flight test runner script `build/verify_master.py` executing all 10 acceptance checks from PROMPT §10.

#### 7. 3 Granular Subtasks with 3 Substeps Each
- **Subtask A: Curriculum Inventory Expansion to $\\ge 120$ Items**
  - *Substep A.1*: Map all 113 concept inventory IDs from `build/inventory.json` against existing items; identify the 35 unmapped concepts.
  - *Substep A.2*: Author new retrieval prompts for unrepresented concepts: the Third Law of Thermodynamics, $S^\\circ$ absolute values, indirect calorimetry and $RQ$, Atwater vs bomb combustion factors, Prigogine $d_i S + d_e S$, steady state vs equilibrium, limiting reagent stoichiometry, and thermogram extrapolation.
  - *Substep A.3*: Tag every recall item with its concept ID (`data-concept="ID"`), chapter category, and cognitive difficulty level.
- **Subtask B: Interactive Leitner Engine & Progress Dashboard**
  - *Substep B.1*: Inject the mastery dashboard markup at the start of Chapter 15 with progress bars, stat counters, and filter toggles.
  - *Substep B.2*: Code `handleRecallVote(itemId, status)` in `build/script.js`: updates session storage, recalculates overall percentage, and updates the dashboard SVG progress arcs.
  - *Substep B.3*: Implement the "Atiestatīt progresu" (Reset progress) function allowing students to wipe session state and start a fresh revision cycle.
- **Subtask C: Automated Verification Gate & Pre-Flight QA Suite**
  - *Substep C.1*: Author `build/verify_master.py` integrating all acceptance checks: zero external links, strict anti-slop CSS compliance, decimal comma in prose, true Unicode minus, MathML validation, and numerical ledger diff verification.
  - *Substep C.2*: Program the automated test vector runner validating Instruments A, B, and C with printed console diagnostics.
  - *Substep C.3*: Generate the automated acceptance report confirming that 100% of the 38 source defects (S1–S38) are documented in Appendix C (Izmaiņu žurnāls).

#### 8. Verification Criteria, Test Vectors & Acceptance Gate
- **Test Vectors**:
  - Total `<li data-concept="...">` elements in `part_15.html` count $\\ge 120$.
  - Concept inventory coverage ratio: $\\frac{\\text{Covered Concepts}}{113} = 100\\%$.
  - Marking 66 items «Zināju» out of 120 displays exactly $55\\%$ mastery on the dashboard.
- **Acceptance Gate**:
  - `verify_master.py` runs cleanly with 0 errors and reports 100% compliance across all 10 acceptance gates.
  - Active recall engine operates smoothly without external libraries.
"""
