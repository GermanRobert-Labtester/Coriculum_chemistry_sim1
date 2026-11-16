# notation.md - simboli un vienības

Generated from `termbase.json` (`t16` fields) by `tools/build_glossary.py`; the same fields also emit **16. tabula** in `Master_5_tema_kinetika_un_katalize.html` (chapter 16). `tools/verify_units.py` checks that the two are identical cell for cell; `tools/build_glossary.py --check` fails if either view drifts from the termbase. Edit `termbase.json`, then run the builder.

| Simbols | Nozīme | SI vienība | Rādāmā vienība | Nod. | Piezīme |
|---|---|---|---|---|---|
<!-- notation-table:begin -->
| v | reakcijas ātrums; enzīmu kinētikā — sākotnējais ātrums | mol·L⁻¹·s⁻¹ | µmol·min⁻¹ (daudzuma ātrums noteiktā tilpumā) | 1 | 1 µmol·min⁻¹ ≈ 1,67·10⁻⁸ mol·s⁻¹; dalot ar tilpumu V (L), iegūst mol·L⁻¹·s⁻¹. |
| k | ātruma konstante | pēc pakāpes: 0 — mol·L⁻¹·s⁻¹; 1 — s⁻¹; 2 — L·mol⁻¹·s⁻¹ | min⁻¹ pirmajai pakāpei | 3 | Mazais burts; vienība seko no v = kC<sup>n</sup>. |
| t½ | pusperiods | s | min, h, d | 6 | Lekcijā τ½. |
| E<sub>a</sub> | aktivācijas enerģija | J·mol⁻¹ | kJ·mol⁻¹ | 2 | Formulā ar R = 8,314 J·mol⁻¹·K⁻¹ lieto J·mol⁻¹. |
| γ | van 't Hofa temperatūras koeficients | bezdimensiju | — | 5 | Ātruma pieaugums uz 10 K. |
| K<sub>M</sub> | Mihaelisa konstante | mol·L⁻¹ | mmol·dm⁻³ (tāda pati kā C<sub>S</sub>) | 10 | K<sub>M</sub> = [S] pie v<sub>max</sub>/2. |
| v<sub>max</sub> | maksimālais ātrums | mol·L⁻¹·s⁻¹ | µmol·min⁻¹ (daudzuma ātrums, tāda pati kā v) | 10 | v<sub>max</sub> = k<sub>cat</sub>[E]<sub>akt</sub>; viens centrs: = k<sub>2</sub>[E]₀. |
| A | pirmseksponenciālais faktors | tāda pati kā k | — | 5 | Atkarīga no pakāpes. |
| C<sub>S</sub> | substrāta koncentrācija | mol·L⁻¹ | mmol·dm⁻³ | 10 | mol·L⁻¹ un mol·dm⁻³ ir viens un tas pats. |
| k<sub>cat</sub> | katalītiskā konstante, uz vienu aktīvo centru | s⁻¹ | min⁻¹ | 10 | k<sub>cat</sub> = v<sub>max</sub>/[E]<sub>akt</sub>; [E]<sub>akt</sub> = n[E]₀ (n — centru skaits molekulā). |
| [I] | inhibitora koncentrācija | mol·L⁻¹ | mmol·dm⁻³ | 10 | Tāda pati vienība kā C<sub>S</sub>. |
| K<sub>i</sub> | inhibīcijas konstante | mol·L⁻¹ | mmol·dm⁻³ | 10 | Tāda pati vienība kā [I]. |
| K | līdzsvara konstante | bezdimensiju | — | 8 | Lielais burts; nejaukt ar k. |
| [E]₀ | kopējā fermenta koncentrācija | mol·L⁻¹ | µmol·L⁻¹ | 10 | Visas fermenta formas kopā (E + ES + …); nemainās reakcijas gaitā; nav brīvais ferments [E]. |
<!-- notation-table:end -->

## Display policy

* Formulas use SI base units. `mol·L⁻¹` and `mol·dm⁻³` are the same unit; the document uses `mol·L⁻¹` everywhere except enzyme graphs, where `mmol·dm⁻³` follows the MU Q10 axis.
* `µmol·min⁻¹` is allowed for `v` and `v<sub>max</sub>` in enzyme kinetics (it is an amount per time, not a concentration per time). Inside one equation `v` and `v<sub>max</sub>` use the same unit; `C<sub>S</sub>`, `K<sub>M</sub>`, `[I]`, `K<sub>i</sub>` use the same concentration unit.
* Conversion: 1 µmol·min⁻¹ ≈ 1,67·10⁻⁸ mol·s⁻¹; divide by the reaction volume V (in L) to get mol·L⁻¹·s⁻¹.
* `k` unit by order: 0 → mol·L⁻¹·s⁻¹; 1 → s⁻¹; 2 → L·mol⁻¹·s⁻¹ (derived from `v = kC^n`, see the unit ladder under 16. tabula).
* `t½` in the laboratory and in the document; `τ½` in the lecture text. Glossed at first use (chapter 6) and in chapter 14.
* Symbol sub/superscripts are real HTML (`<sub>`, `<sup>`) or MathML, never `_` / `^` in prose.
* N02-S1 (2026-11-02): quantity symbols are italic inside MathML formulas (`<mi>` single letters are italic by default per MathML Core). Multi-letter identifiers that are not quantities — chemical formulas `KMnO`, `MnSO`, `MnO`, `Mn`, `SO` — carry `mathvariant="normal"` explicitly; function names stay `<mi>ln</mi>` (MathML Core renders multi-char `mi` upright). In running prose the document keeps symbol mentions upright as a deliberate house exception to ISO 80000-2 (prose mentions like "ātruma konstante k" read as words, not as algebra); units (K, s, mol·L⁻¹) are upright everywhere. `tools/verify_text.py` enforces: R1 no ASCII `_`/`^` in visible text (ch. 0–16) outside `<code>`, quoted-source spans and MathML; R2 termbase English terms inside `lang="en"`; R3 the lab chapter's rate constant is lowercase k; R4 `τ½` only in gloss contexts (ch. 6, 12, 14, 16, 17). Units and chemical formulas may use Unicode indices (`mol·L⁻¹`, `H₂O`). SVG text uses `<tspan baseline-shift>`; SVG `<title>`/`<desc>` and aria-labels stay plain text (`Ea`, `vmax`) on purpose.
* Quoted source defects keep the source notation (register entries K8, K10: `mol/L·s`, `23 J/mol`; MU question titles `Vmax`, `Km`).
