# N16 chain format — worked example records

Status: authored 2026-11-17. This is the format contract for `data/chains.json` (EX01–EX14). The chains are training material, not official colloquium questions. The machine-readable field tables are in `data/chain_schema.json`; the validator is `tools/validate_chains.py`.

## 1. Record shape

| Field | Type | Required | Rule |
|---|---|---|---|
| `id` | string | yes | `EX01`–`EX14`; unique; matches the design-exemplar id. |
| `topic` | integer 1–7 | yes | Programme topic; at least two chains per topic. |
| `title_lv` | string | yes | Learner-facing Latvian title. |
| `subtitle_lv` | string | yes | One-line scope statement; givens may appear here, results may not. |
| `outcome_ids` | string[] | yes | Each id resolves `#sim-coverage`; all belong to `topic`; the first is primary. |
| `master_citation` | object | yes | `path`, `anchor`, `heading_lv`, `freeze_id`; the anchor resolves in the frozen master and equals the primary outcome's anchor. |
| `epistemic_label` | string | yes | Names the training-policy and synthetic-given status. |
| `banner_lv` | string | yes | Fixed honesty banner (see §5). |
| `givens` | object[] | yes | Declared inputs; each has `id`, `label_lv`, `value`, `display_lv`, `unit`, `source`. |
| `steps` | object[] | yes | Ordered reasoning chain; at least three steps. |
| `figure_refs` | object[] | yes | `figure_id`, `step_id`, `role` (`data`, `method`, `print`). May be empty. |
| `back_links` | object | yes | `method_card_ids`, `practice_item_ids`; bidirectional against `data/chain_references.json`. |

## 2. Step shape

| Field | Type | Required | Rule |
|---|---|---|---|
| `step_id` | string | yes | `S1`, `S2`, … unique within the chain; ascending order. |
| `quantity_lv` | string | yes | What quantity the step determines. |
| `statement_lv` | string | yes | The learner-facing task for this step. It must not contain this or any later step's result value. |
| `result.kind` | `numeric` \| `symbolic` | yes | Numeric results are recomputed; symbolic results are equation/sequence statements. |
| `result.value` | string | yes | Canonical dot-decimal value (`0.2`, `266.6666666666666667`) or symbolic text (`2:1:2`). |
| `result.display_lv` | string | yes | Latvian display (comma decimal, `×10³` where useful). |
| `result.unit` | string | yes | Canonical unit; `1` for dimensionless. |
| `result.sig_figs` | integer | numeric | 2–6; the display must be correctly rounded to this precision. |
| `result.public` | boolean | no | Only for a result that is already a declared given (for example a burette reading). The leak scan skips public results. |
| `reasoning_lv` | string | yes | The self-explanation text, sealed until the step is revealed. |
| `recompute` | object | numeric | Independent authoring recompute (see §3). |
| `citations.conventions_refs` | string[] | yes | At least one; two are allowed for the demonstrated multi-citation case. |
| `citations.master_refs` | string[] | no | `#anchor` references into the chain's master. |

## 3. Recompute grammar

The recompute block is an authoring-time second opinion, not a runtime calculator. It is evaluated by the Python validator with `decimal.Decimal` and compared with the declared result. Runtime rendering never recomputes a chain value; it decrypts the authored payload.

| Operation | Operands | Meaning |
|---|---|---|
| `add` | 2+ | Sum. |
| `subtract` | 2 | First minus second. |
| `multiply` | 2+ | Product. |
| `divide` | 2 | First divided by second. |
| `negate` | 1 | Sign change. |
| `scale` | 1 + `factor: {num, den}` | Multiply by an exact rational factor (unit prefix). |
| `multiply_ratio` | value + `num` + `den` | Stoichiometric ratio `value × num / den`. |
| `power` | base + exponent | Integer power. |
| `log10` | 1 | Decimal logarithm. |
| `linfit_component` | `points: [[x,y],…]` + `component: slope\|intercept` | Least-squares line; independent of the figure renderer. |
| `nernst` | `E0`, `slope`, `n`, `Q` | `E = E0 − (slope/n)·log10(Q)` at the declared temperature. |

Operands reference a `given` id, a prior `step` id, a literal `number`, or a `constant` with a resolving `conventions_ref`. Forward step references fail with the chain and step id. A missing operand fails by name.

Every numeric result is checked twice: the recompute value must equal `result.value` within a 1e-9 relative tolerance, and `result.display_lv` must be the declared value correctly rounded to its displayed precision. A scratch chain with one altered intermediate fails the gate by chain and step id (recorded in `evidence/N16_CORPUS_RECORD.json`).

## 4. Citation rules

A conventions reference is a dotted path with optional list selectors, for example:

- `atomic_masses.elements[O]`
- `compound_molar_masses.compounds[NaCl]`
- `unit_system.conversions[ml_to_l]`
- `constants.values[N_A]`
- `tolerances.quantity_classes[burette_volume]`
- `kinetics.integrated_forms[order=1]`
- `concentration_bases.bases[id=molar]`
- `potentials.reference_values[Cu2_Cu]`
- `rounding.rule`

A reference that does not resolve is a dangling citation and fails the build. A step may cite two entries; EX03 S5 demonstrates the form (a unit conversion plus the burette tolerance rule). The validator records it as `multi_citation`.

## 5. Honesty banner and reveal keys

The fixed banner is:

> Mācību materiāls patstāvīgai sagatavošanai: nav oficiāls RSU kolokvija eksāmens, neapliecina eksāmena saturu un nepiešķir vērtējumu.

The copy lint rejects positive official-exam claims (`oficiāls eksāmens`, `īsts eksāmens`, `eksāmena jautājums`, `oficiāls uzdevums`, `RSU eksāmens`, `garantēts vērtējums`, `proktors`) in chain text. The banner's negation is allowed.

Reveal keys are per step. The build seals `result.value`, `result.display_lv`, `result.unit`, `result.sig_figs` and `reasoning_lv` into a base64 payload XORed with a key derived from `chain_id:step_id` (SHA-256 hex). The pre-reveal DOM and the `#sim-chains` island contain the key and ciphertext, never the plaintext. This is inspection resistance for an offline single-file artifact, not cryptographic secrecy: a determined reader can decrypt the payload. The build gate enforces the property it can enforce — no plaintext result or reasoning before the reveal — and the evidence states this limit explicitly. Reveal state is in memory only; chains always open collapsed and are not written to storage or the URL.

## 6. Print rule (N34 precursor)

Under the print stylesheet:

- a fully revealed chain prints its steps, results and reasoning;
- a collapsed chain prints its step statements and a note that the reasoning is interactive;
- a partially revealed chain prints only the steps whose results the learner has opened.

The print CSS keys off `data-revealed-count` on the chain article and `data-revealed` on each step. Buttons, confirmation panels and the reveal controls are hidden in print.

## 7. Handoff

The format is frozen for N19 (method-card example references), N20 (practice-item teaching links), N29 (revision view) and N34 (print mode). `data/chain_references.json` is the forward contract: N19/N20 replace the `declared-pending-*` statuses with authored cards/items while preserving the chain ids. The chain renderer exposes `SimChains.openFromLink` and `SimChains.mountChain` for those consumers.
