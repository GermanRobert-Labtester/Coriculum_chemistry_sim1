# Variant engine format, the family templates and the ephemeral retry contract

**Owner:** N20 · **Status:** frozen interface for N24, N28, N30 and N31
**Data:** `data/family_templates/topic1..7.json` (the frozen templates) · `data/bank/FAM-*.json` (the
frozen bank)
**Twins:** `tools/variant_engine.py` (authoring) · `src/variant-engine.js` (runtime)
**Runtime asset:** `src/variant-templates.js` (generated; ships from `src/`, not inlined)

This document is the contract the downstream tasks read. It describes what a family template is,
what the engine guarantees, what the frozen bank is, and what a consumer may rely on.

**Epistemic note.** The 2025 programme fixes seven topics, a written-on-paper examination and a
maximum of 180 minutes. It fixes **no** point weight, no question count, no pass mark, no allowed
aid and no exact exam question type. The family count (28), the variant count (4 per family), the
instance count (112), the required types and every point weight are **PROPOSED training policy**.
Nothing in this format is an official examination, grade or proctoring claim.

---

## 1. One authority per concern

| Concern | Authority | Where |
|---|---|---|
| Physical constants | `#sim-conventions` | resolved **by reference** (`molar_mass:NaCl`, `potential:Cu2_Cu`, `nernst_slope`); no constant is copied by value into a template |
| Arithmetic | the variant engine | fixed-point integers at scale 10⁻⁹; the engine computes and never grades |
| Grading | N17 (numeric, graph), N18 (graph criterion discipline), N19 (option_select, ordering, matching) | the engine never decides a verdict |
| Leak rules | N12 (`tools/leak_scan.py`) | token-boundary and unit-normalised; **not** semantic grading |
| Instance format | N04 (`data/question_schema.json`) | the engine emits schema-valid instances only |

## 2. What a family template is

A family template declares **one** learning family and **four** parameterisations of it. It is
data, not prose: the engine reads ranges, recipes and payload shapes, and never interprets the
Latvian text.

```jsonc
{
  "family_id": "FAM-3A",          // FAM-[1-7][A-D]
  "topic": 3,
  "title_lv": "…",
  "point_weight": 6.0,            // PROPOSED training policy
  "slot_id": "S3-2",
  "type_mix": ["Q02", "Q09"],      // the response types the family uses
  "outcome_ids": ["P3-07"],        // resolve in #sim-coverage
  "policy_label": "PROPOSED training policy (N20). …",
  "variants": [ /* A, B, C, D */ ]
}
```

### 2.1 A variant

| Field | Meaning |
|---|---|
| `variant_id` | `A`…`D` |
| `type_id`, `type_ids` | the response type(s); the payload class must match the N04 schema's type→class map |
| `spec_lv`, `stem_lv`, `feedback_lv` | the Latvian text; `{placeholder}` tokens are substituted with the computed values |
| `parameters` | the **inputs**: `int` (drawn), `constant` (resolved from the conventions), `fixed` (an authored factor, e.g. a counting datum) |
| `derived` | the **recipe**: each entry is `op` + `args` → a value id, with its declared unit, display precision and role |
| `payload` | the response payload: `numeric`, `option_select`, `ordering`, `matching`, `graph` or `method` |
| `rubric` | the criteria: `grading` (`auto`/`self`), `engine_binding`, `points`; the points sum to the family weight |
| `source_refs` | the master path, its sha256 and the locator |
| `misconception_signatures` | the N19 signature ids the item probes |
| `seed_key`, `seed_algorithm` | `FAM-<family>-<variant>` and `fnv1a64-utf8-v1` |
| `leak_scan_exemption` | an optional N12 exemption with its reason code, reason and scope |

### 2.2 Parameter kinds

| Kind | Meaning | Drawn? |
|---|---|---|
| `int` | an integer range: `min`, `max`, `step`, `decimals`; the base value is `drawn / 10**decimals` | yes (SplitMix64) |
| `constant` | a conventions reference; the value is resolved, never authored | no |
| `fixed` | an authored factor stated by the task (stoichiometry, counting, a percentage basis) | no |

### 2.3 Recipe operations

`identity`, `add`, `sub`, `mul`, `div`, `mul_div`, `lin`, `pow_int`, `percent`, `negate`,
`log10_pow10`, `round_decimals`.

Every operation is exact integer arithmetic. `log10_pow10` is the only one that looks
transcendental: it is the exact decimal logarithm of an exact power of ten, computed by counting
trailing decimal zeros, and it **refuses** a value that is not an exact power of ten.

**The dimension is part of the contract.** Every derived value declares the unit it produces, and
the review gate proves that the N17 engine's computed dimension equals the declared unit's
dimension. A recipe that drops a factor (a missing ΔT, a missing density) fails the gate — it
cannot reach the bank.

## 3. What the engine guarantees

1. **Determinism.** The same family, variant and seed produce byte-identical instances. Proven
   for all 112 in `evidence/N20_DETERMINISM_RECORD.json`.
2. **Cross-language identity.** The Python twin and the JavaScript twin produce the same canonical
   bytes. Proven for all 112 in `evidence/N20_RUNTIME_RECORD.json`.
3. **Exactness.** No float reaches an emitted number. A value that cannot be represented exactly
   fails rather than being approximated.
4. **Schema validity.** Every emitted instance passes the N04 schema validation.
5. **Honesty about precision.** The payload's `sig_figs` is the significant-figure count of the
   *written* answer form. When a whole answer cannot carry its declared precision in plain
   notation (`680`), the written form is scientific (`6,80 × 10²`) — the form N17 parses and
   counts the same way.

## 4. The frozen bank

`data/bank/FAM-*.json` — 28 files, 112 instances, canonical bytes.

| Digest | Covers |
|---|---|
| `1c263cdb37396f0eb910c52cf9e6a0b30725533358d57fd7de85c4b58c78acb6` | the bank files in family order (**the** frozen reference) |
| `07fec72a5484bd8e9bf705e2127f3a5b482d5b65c59c32fbee7ab2cd3299bac1` | the `#sim-bank` island the artifact embeds, and its embedded text |

**The island is a runtime projection.** It keeps the identity, the stem, the payload, the rubric,
the givens, the review state and the engine metadata, and drops the per-instance audit tables
(`draws`, `derived`, `review_workflow`). Those stay in the bank files and in the evidence records.
Both digests are recorded so that neither the authored bank nor the embedded island can change
unnoticed.

**Review state.** Every instance carries `review` (four fields) and
`extensions.data.review_workflow` with the state, the stages, the named checks and the sign-off.
The sign-off is the **N20 task author's preparation pass**, not an RSU instructor's acceptance.

### 4.1 The runtime integrity check

`src/bank-loader.js` verifies the island digest at load:

| Situation | Error code |
|---|---|
| the island text does not match the digest | `E_BANK_DIGEST_MISMATCH` |
| the digest meta element is missing | `E_BANK_DIGEST_MISSING` |
| the SHA-256 helper is unavailable | `E_BANK_DIGEST_UNAVAILABLE` |

The digest is taken over the island **text as embedded**, not over a re-serialisation of the parsed
JSON, so a mismatch can never be a float-printer artefact. `options.verifyIntegrity === false`
skips the check; only a test harness may use it.

## 5. The ephemeral retry contract

A retry instantiates a **fresh** instance from the **same** templates, through the **same** code
path, and never persists it.

| Rule | Statement |
|---|---|
| Seed | `deriveSeed('{family}-{variant}-EPH-{attempt}')` — FNV-1a-64 over UTF-8 |
| Exclusion | a retry seed that is already a frozen seed is **skipped**; the attempt counter advances until an unused seed is found. The rule is total, deterministic and documented. |
| Determinism | the same attempt reproduces the same ephemeral instance, byte for byte |
| Identity | the ephemeral instance carries its own question id (`…-EPH-{attempt}`) and `extensions.data.ephemeral` (`attempt`, `seed`, `persisted: false`, `frozen_bank_member: false`, `excluded_frozen_seeds: true`), so it can never be confused with the frozen instance |
| Persistence | never written to the bank, never stored; the instance lives in the in-memory session only |
| Grading | the same N17/N19 engines grade the ephemeral instance; the verdict class for an equivalent submission is the same |

```js
// src/variant-engine.js
SimVariantEngine.load(SimFamilyTemplates, conventions);
const retry = SimVariantEngine.instantiateEphemeral('FAM-1A', 'A', 0, frozenSeeds);
```

**The runtime modules ship from `src/` and are not inlined into the artifact**, exactly like the
N17/N18/N19 engine modules. `SimVariantEngine` needs `SimPRNG` (`src/prng.js`) and the SHA-256
helper (`src/figure-framework.js`); the templates ship as `src/variant-templates.js`, a generated
asset whose `template_digest` must equal the digest the Python twin computes over
`data/family_templates/*.json`.

## 6. What a consumer may rely on

- The instance ids `COL1-{topic}-{family}-{variant}-01` are stable for the frozen bank.
- The seed is recorded per instance; the same seed reproduces the instance anywhere.
- The payload's `expected_value` is the computed answer rounded to the declared precision.
- The rubric's `engine_binding` names the engine that grades the criterion.
- The `method` payload class carries **self-assessed criteria only** — N17 denies machine
  criteria on it, so an instance of that class is never claimed to be machine graded.
- The bank's `source_refs` carry the master path and its sha256; the content is traceable to the
  frozen masters.

## 7. What a consumer may **not** assume

- No official examination, grade or proctoring status; the bank is training material.
- No claim that the four variants are four different question *forms*: they are four
  parameterisations of one family template.
- No semantic grading: N12's scanner is a token-boundary and unit-normalised rule.
- No renderer-level accessibility acceptance: the review is a mechanical structural check.
- No claim that the embedded island is a byte copy of the bank files: it is the projection
  described in §4.
