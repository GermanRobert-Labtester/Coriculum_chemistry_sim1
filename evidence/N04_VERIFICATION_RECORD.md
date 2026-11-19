# N04 Verification Record — QUESTION_SCHEMA, Validator, and `#sim-bank` Loader

**Status:** closed 2026-11-17 (UTC).  
**Label:** **VERIFIED (2026-11-17, this environment)**.

## 1. Schema Self-Check & Cross-Island Consistency (`data/question_schema.json`)

- **Types:** All 18 response types (`Q01`–`Q18`) defined and matched verbatim against `docs/QUESTION_TYPES_AND_VARIANTS.md`.
- **Required per-form types:** `["Q02", "Q04", "Q10", "Q11", "Q12", "Q13", "Q15"]`, matched verbatim against `docs/SIMULATION_BLUEPRINT.json`.
- **Payload classes:** 6 payload classes (`numeric`, `option_select`, `ordering`, `matching`, `graph`, `method`) defined once in `payload_classes` and referenced by name in `types`.
- **Discriminator rule:** Every instance MUST declare `payload_class` explicitly and `payload_class == types[type_id].payload_class`.
- **Typed extension slot:** `extensions` (`extension_type`, `data`) declared in `shared_core.properties`.
- **Cross-island bindings:**
  - `outcome_ids` checked against `data/coverage.json` (N02, 64 outcomes).
  - `tolerance_class` checked against `data/conventions.json` (N03, 12 `quantity_classes`).
  - `misconception_signatures` checked against N09 stub regex `^MC-[1-7][A-D]-[0-9]{2}$` until N09 lands.
- **Self-check result:** `PASS bank-schema: 18 types, 6 payload classes, 0 files, 0 instances, 0 violations (2.743 ms)` (`evidence/N04_VALIDATION_RECORD.json`).

## 2. Permanent Negative Corpus & Set-Level Checks (`tools/fixtures/n04/`)

All negative fixtures were rejected with exit code `1` and exact field/level attribution recorded in `evidence/N04_CORPUS_RECORD.json`:

| Fixture | Level | Named Field(s) | Outcome |
|---|---|---|---|
| `schema_malformed.json` | `schema` | `<root>` | `FAIL` (caught before instance checks) |
| `neg_missing_stem.json` | `instance` | `stem_lv` | `FAIL` |
| `neg_bad_tolerance.json` | `instance` | `payload.tolerance_class` | `FAIL` |
| `neg_bad_outcome.json` | `instance` | `outcome_ids` | `FAIL` |
| `neg_bad_family.json` | `instance` | `family_id` | `FAIL` |
| `neg_discriminator_mismatch.json` | `instance` | `payload_class` | `FAIL` |
| `neg_bad_misconception.json` | `instance` | `misconception_signatures` | `FAIL` |
| `neg_duplicate_id/` | `set` | `question_id` (`COL1-1-1A-A-01`) | `FAIL` |

## 3. Full-Size 112-Instance Scratch Bank & Build Gate (`tools/build.py`)

- **Valid 18-type scratch bank:** `PASS` (18 files, 18 instances, 0 violations).
- **Full-size 112-instance scratch bank (28 families × 4 variants, all 18 types + 7 required types):** `PASS` in `~40 ms` (`fast_gate_under_1000ms: true`, 0 violations).
- **Build gate (`order: 3, id: bank, owner: N04`):**
  - Invalid scratch bank (`neg_missing_stem.json`): refused build (`returncode: 1`), named `stem_lv`, wrote no artifact (`artifact_written: false`).
  - Clean 112-instance scratch bank: `PASS`, built artifact (`returncode: 0`, `artifact_written: true`).

## 4. Runtime Loader (`src/bank-loader.js`) & Degradation (`tools/check_bank_runtime.js`)

- **Shipped `#sim-bank` in `output/simulator.html`:** loads cleanly (`status: pre-N20-schema-only`, 0 questions).
- **112-instance scratch bank:** `PASS`, 112 records mapped, 18 types resolved, 28 families indexed, `getForRenderer` / `getForAssembly` / `getEngineBindings` verified.
- **Unknown type (`Q99`):** fails loudly at load with `E_BANK_UNKNOWN_TYPE` naming `Q99`.
- **Truncated `#sim-bank`:** fails honestly with `E_BANK_JSON` naming `#sim-bank` and renders error in `#sim-bank-error`.
- **Missing `#sim-bank`:** fails honestly with `E_BANK_MISSING` naming `#sim-bank`.
- **Missing required type (`Q15` omitted):** fails loudly with `E_BANK_MISSING_REQUIRED_TYPE` naming `Q15`.

## 5. Authoring Workflow Contract & Frozen Handoff

- **Authoring workflow contract:** Questions are authored as source JSON files in `data/bank/`, validated exclusively by `tools/validate_bank.py`, and frozen into `#sim-bank` inside `output/simulator.html` at build time by `tools/build.py`. Direct hand-editing or surgery inside `#sim-bank` / `output/simulator.html` is forbidden; any emergency fix to a shipped island must be routed back through `data/bank/`, revalidated by `tools/validate_bank.py`, and rebuilt by `tools/build.py`.
- **Frozen handoff:** `data/question_schema.json` (`2c55d0dd1c9208664ea08727bcd89328d64311bfb06e5ca3c435b35ed8ae2f2d`) and `SimBank` (`src/bank-loader.js`, `206b2d025439abbeb0672f8d7a448d68772e9842036d65c76d2954c60a6a3363`) are frozen for **N20** (authoring), **N22** (rendering), **N24** (assembly), and **N05** (vector format).
- **Corpus parity:** Two consecutive runs of `python3 tools/n04_corpus.py` produced byte-identical `evidence/N04_CORPUS_RECORD.json` (`99245e9799c783eb0d9cf5bbfa09bac8aa1924f5328537125c3fae62d0bdf4e1`).
