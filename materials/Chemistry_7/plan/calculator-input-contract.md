# Calculator input contract (T04/B01.0)

Parent: AGENTS.md §4 (registry J1–J5), §5; INFRA [JS-RUNTIME-REGISTRY]. Scope: the three
JS-driven registry instruments — J2 explorer (`exp-g`, `exp-l`), J3 dilution (`dil-v1`,
`dil-vtot`), J4 quality (`qual-a`, `qual-digits`). Contract-first rule: every expectation
below is derived from `tools/data.py` and normative HTML form-control behavior BEFORE any
test runs; "expected" never means "whatever the code currently does". Runtime confirmation
rule: no bug is asserted without an approved runtime reproduction (ST4.2).

## 1. Numeric authority (tools/data.py)

| Quantity | Value | Authority |
|---|---|---|
| k (origin 9-pt fit slope) | 30.394608 mL·mg⁻¹ | `origin9pt_blank_included.k` |
| J4 handler constants | k = 30.3946, u(k) = 0.093, u(A) = 0.001 A | display-rounded literals, ratified T15 (byte-identical verdict strings); parity with data.py is asserted by the existing C36 quality assertions + numbers_trace |
| u(A) conservative | 0.001 A | `CONSTANTS["u_A_conservative"]` |
| Calibrated span | [0.063, 0.482] A | `A_CAL_MIN`/`A_CAL_MAX` (T03 boundary fixtures); outside → extrapolation flag, never a silent result |
| Stock γ₀ | 0.0400 mg/mL | `CONSTANTS["stock_gamma"]` (J3 literal 0.0400) |
| M (riboflavīns) | 376.36 g/mol | `CONSTANTS["M"]` (J3 literal 376.36) |
| Protocol dilution | V₂ = 10.00 mL; standards V₁ ∈ 0–4.00 mL | `CONSTANTS["total_volume_mL"]`, handout 14. tabula |
| Explorer model | A = k·l·γ; warnings A < 0,1 / A > 1 / A > 2 | §7.3/§10.8 teaching models |
| Quality verdict range | 0,010–2,000 A (per the existing verdict string) | §10.8; A ≤ 0 → no finite concentration (`uncertainty_for_A` raises) |

## 2. Two-layer input model

**Layer 1 — native controls (normative HTML value sanitization, no JS involved).**

| Input | Type | min/max/step | What `.value` can contain |
|---|---|---|---|
| `exp-g` | range | 0 / 0.02 / 0.0005 | always a valid clamped float in [0, 0.02]; a non-numeric set falls back to the min/max midpoint (0.01 — engine-observed, ST4.2); typing arbitrary text is not possible |
| `exp-l` | range | 0.5 / 5 / 0.1 | always a valid clamped float in [0.5, 5] (default 1) |
| `dil-v1` | number | 0 / 10 / 0.1 | a valid float string, or "" (empty) — letters, comma-decimal forms such as "1,5", thousands groups such as "1 500" and mixed separators all sanitize to "" |
| `dil-vtot` | number | 1 / 100 / 0.5 | same as `dil-v1` (range 1–100) |
| `qual-a` | number | 0.010 / 2.000 / 0.001 | same as `dil-v1` |
| `qual-digits` | select | — | "1", "2", "3", "4" (option values) |

Consequences (all confirmed at runtime in ST4.2):
- Both "," and "." decimals: the canonical display format is the decimal comma (`fmt`), but
  the canonical *input* path through `type=number`/`type=range` controls accepts only the
  dot form ("1,5" never reaches a handler — Layer 1 turns it into ""). A handler-level
  comma normalization (J3's `replace(',','.')`) remains required as a defensive path for
  any value that reaches the handler unsanitized (programmatic/AT/paste edge paths).
- Thousands separators (space, thin space, NBSP) never survive Layer 1 → "".
- "1.234" with no comma present is unambiguous (dot = decimal point) → accepted as 1.234.
  Mixed separators ("1.234,5", "1,234.5") sanitize to "" → invalid state; no ambiguous
  input can reach a handler, so nothing is silently half-parsed.
- "1e3" is a valid floating-point number per HTML → reaches handlers as 1000 (J3: clamped
  with write-back; J4: flagged as extrapolation + implausible).

**Layer 2 — handler contract (per `.value` state the handlers can receive).**

| State | Required behavior | Status announcement |
|---|---|---|
| Valid float | Compute per §1; display with decimal comma; range flags per §1 | no invalid status; range warnings as designed |
| "" (empty — erased field or sanitized garbage) | INVALID state: the status region shows an explanatory message; outputs show the cleared state ("—"), never plausible numeric results | required |
| Parseable but out of bounds | Clamp with visible write-back (echo) + warning (J3 1–100 mL, V₁ ≥ 0, V₁ ≤ V_tot; explorer/quality flags per §1) | warning string |
| A ≤ 0 (J4) | Cleared "—" + the existing "Ievadiet absorbances vērtību…" message | required |

**Stale-output rule (ST4.1.3):** after any invalid input the output region shows the
invalid-status message or the cleared state — never the previous valid value and never a
plausible recomputed default presented without an invalid status. Errors are announced via
the `role="status"` regions (`exp-warn`, `dil-warn`, `qual-verdict`; implicit
aria-live=polite; readouts carry `aria-live="polite"`). The static no-JS fallback
(15./25./10. tabula) stays untouched.

**Pinned invalid-status strings** (fixtures assert them exactly; the J3 patch must produce
this byte-exact string, mirroring J4's existing pattern): J3 →
`Nederīga ievade: ievadiet tilpumu.`; J4 → the existing `Ievadiet absorbances vērtību no
0,010 līdz 2,000.` (unchanged).

## 3. Clamp bounds (per instrument, from data.py + native attributes)

| Instrument | Field | Bounds | On violation |
|---|---|---|---|
| J2 explorer | γ | [0, 0.02] mg/mL (native range) | impossible via UI; sanitizer clamps |
| J2 explorer | l | [0.5, 5] cm (native range) | impossible via UI; sanitizer clamps |
| J3 dilution | V_tot | [1, 100] mL | JS clamp + write-back "1.00"/"100.00" + status |
| J3 dilution | V₁ | [0, V_tot] mL; protocol warning above 4.00 | JS clamp + write-back + status |
| J4 quality | A | (0, 2.000]; calibrated span [0.063, 0.482] | A ≤ 0 → invalid state; outside span → extrapolation suffix; A > 2 → implausible suffix |

## 4. Reset semantics

No reset control exists in the UI (deliberate: the no-JS fallback tables are the static
restore path, and AGENTS §4 forbids a fifth widget). "Reset" is therefore contractual
*recoverability*: after any invalid or clamped state, entering the protocol defaults
(V₁ = 2.00 / V_tot = 10.00; A = 0.086; γ = 0.0085 / l = 1) must restore exactly the
protocol outputs and clear the invalid status. Fixture `reset-after-invalid` asserts this.

## 5. Fixture table (tools/behaviour.py, B01)

Expected values are computed in Python from the §1 constants (same literals as the
handlers); each case asserts the expected output value or the expected invalid-status
string.

| Case | Instrument | Input (set) | Expected |
|---|---|---|---|
| j2-comma | J2 | exp-l 1, exp-g "1,5" | echo ∈ [0, 0.02]; A = fmt(k·1·echo, 3) — computed from the echoed sanitized value, not assumed |
| j2-clamp-hi | J2 | exp-g "99" | echo "0.02"; A "0,608"; no invalid status |
| j2-clamp-lo | J2 | exp-l "0", exp-g 0.0085 | echo "0.5"; A "0,129" |
| j3-comma | J3 | dil-v1 "1,5" | Layer 1 → "" → invalid status + outputs "—" (ST4.2 confirms) |
| j3-dot | J3 | dil-v1 "1.5" | γ "0,0060"; water "8,50"; c "1,59·10⁻⁵"; µmol "15,9" |
| j3-thousands | J3 | dil-v1 "1 500" | invalid status + "—" |
| j3-empty | J3 | dil-v1 "" | invalid status + "—" |
| j3-malformed | J3 | dil-v1 "abc" | invalid status + "—" |
| j3-stale | J3 | dil-v1 2 → "abc" | after invalid: γ = "—", status non-empty — never "0,0080" |
| j3-neg | J3 | dil-v1 "-1" | write-back "0" + status (existing behavior) |
| j3-exp | J3 | dil-v1 "1e3" | clamp to V_tot + write-back + status |
| j3-zero | J3 | dil-v1 "0" | γ "0,0000"; c "0" (valid boundary, no invalid status) |
| j3-vtot-lo / hi | J3 | dil-vtot "0.5" / "500" | clamp write-back "1.00" / "100.00" + status |
| j3-reset | J3 | after j3-invalid: V₁ 2.00, V_tot 10.00 | γ "0,0080", water "8,00", status cleared |
| j4-comma / thousands / malformed | J4 | qual-a "1,5" / "1 500" / "abc" | invalid message "Ievadiet absorbances vērtību…" + "—" |
| j4-dot | J4 | qual-a "1.5" | c "0,04935"; u(c)/c "0,3"; U "±0,00031"; "Pietiekami" + extrapolation suffix (1.5 > 0.482) |
| j4-neg / zero | J4 | qual-a "-1" / "0" | invalid message + "—" (existing) |
| j4-exp | J4 | qual-a "1e3" | valid float → extrapolation + "A > 2: rādījums nav ticams." |
| j4-cal-lo / cal-hi | J4 | qual-a "0.063" / "0.482" | "Pietiekami" verdict, NO extrapolation suffix (span endpoints, T03 parity) |
| j4-outside | J4 | qual-a "0.483" | extrapolation suffix present |
| aria/keyboard | all | focus each input | dil-warn role="status"; every input focusable (document.activeElement echoes) |

Regression rule (ST4.3.2): fixtures live beside the 31 existing C36 assertions; the
negative fixtures for C36 (write-back removal, stale-results restore, listener removal)
must keep failing their mutants after any patch. No storage/network calls — the B5/B6
raw-scans remain the gate.
