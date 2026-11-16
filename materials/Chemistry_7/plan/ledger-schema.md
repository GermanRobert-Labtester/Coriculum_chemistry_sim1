# Claim/Source Ledger Schema — T09 (lab-6b plan, 2026-11-12)

Canonical schema contract for `plan/claim-ledger.csv`. Established by T09 of
`lab-6b-integration-execution-plan.md`; realized as a harmonized superset of the
T19 provenance ledger (owner ruling this turn: **single-file ledger**, no
`plan/sources.csv` — see the recorded deviation below). The ledger is the shared
substrate for the B05 source/claim/applicability matrix (T03/B05 rows
CRB-01–CRB-05) and the future public claim atlas (T14 of the lab-6b plan).

Gates that bind this schema:

- `tools/ledger_lint.py` (T09): schema header, referential integrity, enums,
  non-empty claim text, unresolved→next_action; `--selftest` (5 fixtures);
  `--atlas-fields` prints the T14 public field selection.
- `tools/lint_claims.py` (T19): ledger ↔ src/15*/16* provenance parity
  (L1–L7), unchanged semantics over the renamed columns.

## Header (14 columns, fixed order)

```
kind,id,citation,provenance,source_id,source_scope,conditions,claim_text_lv,chapter_anchor,applicability,status,reviewer,updated,next_action
```

| Column | Meaning | Filled by |
|---|---|---|
| `kind` | `source` (registry row) or `claim` (claim→source row) | both |
| `id` | Row registry ID. Source rows: `R1`–`R10`, `S1`–`S4`, `NOSRC`, `SKOLO`. Claim rows: `C-01`…`C-10`, `CL-…`, `CRB-…`. **T09 mapping note:** the task's `claim_id` is this column on claim rows (documented alias — no duplicate column). | both |
| `citation` | Full bibliographic identity (old source-row `source` cell), verbatim | source rows |
| `provenance` | Evidence tier — the T19 `status` vocabulary, unchanged: `avots`, `aprēķins`, `papildinājums`, `nav pārbaudīts`, `teksts lasīts`, `metadati`, `lapa nav pārbaudīta` | both |
| `source_id` | Foreign key: the referenced source row's `id` (old claim-row `source` cell). Source rows self-register (`source_id` = `id`). | both |
| `source_scope` | What the source can warrant (old `scope` cell) | both |
| `conditions` | Recorded boundaries/limitations and governing errata (old cell, verbatim) | both |
| `claim_text_lv` | The claim text (old `claim` cell, verbatim; source rows keep their descriptive registry label) | both |
| `chapter_anchor` | Product locator **only where the row text already records one** (e.g. CRB rows carry `src/NN:LL` locators); empty otherwise — never invented | claim rows (mostly CRB) |
| `applicability` | Source-scope vs claim-use match: `matched` \| `partial` \| `unmatched` (see derivation rules) | claim rows; SKOLO `unmatched` |
| `status` | T09 support verdict: `supported` \| `conditional` \| `unsupported` \| `unresolved` (see derivation rules). `unresolved` is a first-class state, never a failure to hide. | claim rows; SKOLO `unresolved` |
| `reviewer` | Who recorded the row (T04/T07/T19/CR (B05)) | both |
| `updated` | Last update date, ISO (old `date` cell) | both |
| `next_action` | Required (non-empty) whenever `status` is `unresolved`; must restate an already-recorded reopen condition (open issue ID, erratum, or `plan/speciation-conditions.md` reopening rule) — never an invented plan | rows with `status=unresolved` |

## Derivation rules (T09 columns on claim rows)

`applicability` — does the recorded `source_scope` cover what **this row's**
`claim_text_lv` asserts from `source_id`:

| provenance tier | default | override to `partial` when |
|---|---|---|
| `teksts lasīts` | `matched` | the conditions explicitly narrow below the claim (e.g. R1 aqueous maximum does not warrant flatness at 440 nm → CRB-01/02/03) |
| `metadati`, `lapa nav pārbaudīta` | `partial` | — |
| `avots` (course attribution: claim asserts what the course/protocol says) | `matched` | — |
| `aprēķins` (internal `data.py` authority) | `matched` | — |
| `nav pārbaudīts` | `unmatched` | — |

`status` — is the claim as published fully backed?

| verdict | when |
|---|---|
| `supported` | claim within recorded scope, no governing qualifier (attribution claims, `data.py` computations without attached caveats, read definitions within scope) |
| `conditional` | published wording carries an explicit qualifier/erratum governing it (E7 simplification, E18/E19/E25 diagnostic-not-proof, E24 limited inference, E26 simplified estimates, `l = 1 cm` assumption) |
| `unsupported` | live claim overreaches its source (none on the 2026-11-12 baseline — T03/B05 replaced every unsupported wording; the value stays in the enum for future rows) |
| `unresolved` | `provenance` is `nav pārbaudīts` (book leads with pages never read, SKOLO identity unchecked, no-source general statements) |

Per-row values were set during the T09 migration from each row's own recorded
scope/conditions text; no judgment goes beyond text already in the ledger or
the open-issue ledger (ISS-009) and `plan/speciation-conditions.md` (ST7.3
reopening conditions).

## T14 consumption contract (field selection only)

The atlas generator must consume the CSV with **filtering + field selection
only — no transformation**:

1. filter rows to `kind == "claim"`;
2. select public fields: `id` (public claim key), `claim_text_lv`,
   `chapter_anchor`, `status`, `source_scope`;
3. resolve the citation by joining `source_id` to the source row's `citation`
   (plain CSV join, no rewriting);
4. deterministic row order by `id`.

`tools/ledger_lint.py --atlas-fields` prints exactly this selection as the
reproducible DoD proof.

## Recorded deviation — ST9.1.2 (`plan/sources.csv` not created)

Owner ruling 2026-11-12 (this session): the ledger stays a **single file**.
Reasons, in priority order:

1. Student-visible prose names this file as the single map:
   `src/16_ch15_labojumu_zurnals.part` lines 55, 67 and 101 — "Pilns
   apgalvojumu un avotu karte ar identifikatoriem, derīguma apjomiem un
   nosacījumiem: *plan/claim-ledger.csv*". Splitting the source registry out
   would make visible prose false or force a product rebuild with no content
   benefit.
2. Two synchronized CSVs are exactly the "two divergent claim formats" failure
   mode this task exists to prevent.
3. Referential integrity (the task's stated purpose of `sources.csv`) is
   already machine-enforced twice: `ledger_lint.py` R2 and `lint_claims.py`
   L1/L2. The registry columns (`citation`, `source_scope`, `conditions`,
   provenance tier) live in the source rows of the same file.

If a future task still requires `plan/sources.csv`, it must first amend this
contract and the src/16 prose, and re-run both lints plus the full
`run.sh verify --strict` on a rebuilt master.
