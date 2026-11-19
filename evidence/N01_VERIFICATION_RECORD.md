# N01 verification record — source freeze and repository-local verification

**Task:** N01, Phase I (P0, High risk). **Recorded:** 2026-11-16T22:06:09Z (UTC). **Workspace:** `/home/robertsrff/Chemistry_Med/Chemistry_1st_coriculum`.

**Epistemic labels:** the V-01 reproduction, the repository-local PASS, the inventory checker PASS and the programme-PDF digest reproduction are **VERIFIED (2026-11-16)** in this environment. The committed `evidence/PREPARATION_VERIFICATION.json` stays **DOCUMENTED BUT NOT RERUN** in repository-local terms. The full-workspace default mode was re-run in the author workspace present in this environment and reproduced the committed record except its timestamp; that run is not a clean-clone reproduction.

## 1. V-01 reproduction — the clean-clone crash

Reproduction command (a real `git clone` at commit `677156a32bc917e146ca1e3e7e5988ef925a1733`, with no sibling `Chemistry_1`–`Chemistry_7` directories):

```
cd /tmp/opencode/n01-clean-clone && python3 tools/verify_preparation.py
```

Exit code `1`. Verbatim traceback from the pre-N01 script (`sha256 d2edb7033dba7f7d80c908959d29eb49623111d97ab7c4d7a85cf45543a1d102`):

```
Traceback (most recent call last):
  File "/tmp/opencode/n01-clean-clone/tools/verify_preparation.py", line 292, in <module>
    raise SystemExit(main())
                     ^^^^^^
  File "/tmp/opencode/n01-clean-clone/tools/verify_preparation.py", line 273, in main
    verify_data(masters)
  File "/tmp/opencode/n01-clean-clone/tools/verify_preparation.py", line 177, in verify_data
    check(row['master_anchor'] in masters[topic].ids, f"Missing coverage anchor: {row['outcome_id']} #{row['master_anchor']}")
                                  ~~~~~~~^^^^^^^
KeyError: 1
```

**Failing location:** `tools/verify_preparation.py` line 177, function `verify_data`, expression `masters[topic].ids`; exception `KeyError: 1`.

**Failing manifest entry class:** `canonical-master` (7 entries). Their `source` fields are `Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html` through `Chemistry_7/...`; the first absent source is the Chemistry_1 master. In `verify_copies`, every record is skipped at `if not src.is_file() or not dst.is_file(): continue` before the canonical-master branch can populate the `masters` dictionary, so `masters` stays empty. The dictionary is keyed by programme topic, not by a manifest key: `KeyError: 1` is the absent topic-1 entry, not a literal `COPY_MANIFEST` key. This distinction is recorded so the finding is not restated as a manifest-schema defect.

**Two-environment boundary (never conflated):**

- **Published repository alone:** FAILS with the traceback above. The crash is a property of the published repository, because the sibling source trees are not published.
- **Author full workspace:** PASSES. With the sibling trees present, the default mode ran on 2026-11-16 (UTC), status PASS, 174 files, 30,083,827 bytes, 15,978 preserved files, 13 of 14 examples recomputed. Output was identical to the committed record except `checked_utc`.
- The author-workspace PASS does not transfer to a clean clone; the clean-clone failure does not invalidate the author-workspace record.

The registry handover is `evidence/V01_CONFLICT_ENTRY.json` (status `documented-and-accepted`, external owner, N01 mitigation).

## 2. Assertion classification — runnable-locally versus sibling-dependent

The table is read from `verify_preparation.py` against `COPY_MANIFEST.json` (174 records, 30,083,827 bytes, roles 7/35/65/18/49).

| Id | Assertion | Class | Repository-local treatment |
|---|---|---|---|
| A01 | manifest['destination'] equals the current workspace path | runnable-locally (location-sensitive) | not asserted; a clean clone or scratch copy has a different absolute path |
| A02 | no duplicate destination paths | runnable-locally | asserted |
| A03 | source file and destination file both exist | sibling-dependent | source half not asserted; destination half asserted |
| A04 | source bytes == destination bytes == manifest bytes | sibling-dependent (source half); runnable-locally (manifest-only half) | destination bytes == manifest bytes asserted; 174/174 |
| A05 | source SHA-256 == destination SHA-256 == manifest SHA-256 | sibling-dependent (source half); runnable-locally (manifest-only half) | destination SHA-256 == manifest SHA-256 asserted; 174/174 |
| A06 | role counts 7/35/65/18/49 | runnable-locally | asserted |
| A07 | canonical master loads no remote resource and every local src/resource exists | runnable-locally (destination files only) | asserted from the published master |
| A08 | COPY_MANIFEST has 174 file records | runnable-locally | asserted |
| A09 | manifest byte total equals 30,083,827 | runnable-locally | asserted |
| A10 | published tree contains exactly the declared destinations (no undeclared, no absent) | runnable-locally | asserted |
| A11 | source-workspace preservation baseline (15,978 files: path, bytes, mtime_ns, sha256) | sibling-dependent | NOT ASSERTED; recorded honestly |
| A12 | programme PDF SHA-256 and byte size | runnable-locally | asserted |
| A13 | programme extraction contains '180 minutes' and '2025' | runnable-locally | asserted |
| A14 | roadmap 14 sections, 20 T / 10 F / 5 B cards, 3 steps and 2x3 substeps per card | runnable-locally | asserted |
| A15 | README/roadmap/type-doc links resolve and tables are not malformed | runnable-locally | asserted |
| A16 | 64 coverage rows, 28 families, 18 types, 21 slots, 100 points, 170+10 minutes, family/outcome symmetry | runnable-locally | asserted |
| A17 | every coverage master_path exists | runnable-locally | asserted |
| A18 | every coverage master_anchor resolves inside masters[topic].ids | runnable-locally if masters are parsed from published destinations; sibling-transitively dependent in the default mode | asserted from published destinations (64/64); a missing master fails by name instead of raising |
| A19 | 14 examples, 2 per topic; 13 numeric examples independently recomputed; 29 numeric fields; EX11 atom/charge balance; rubric points > 0 | runnable-locally | asserted |
| A20 | optional Draft 2020-12 schema structure check when jsonschema is installed | runnable-locally (environment-dependent) | asserted when the library is present |

**Boundary reading:** the published file set, the manifest's own recorded hashes/sizes/totals, the role counts, the master resource scan, the programme identity, the plan structure, the design-data contracts and the 13-of-14 example arithmetic are all runnable inside the published repository. Only the source-to-copy identity and the 15,978-file preservation baseline require the unpublished siblings. The N01 brief's phrasing that the example recomputation "depends on sources" is imprecise: `verify_examples` reads only `docs/EXAMPLE_QUESTIONS.json` and runs in repository-local mode (see A19).

## 3. Repository-local PASS — published set only (workspace and clean copy)

Command:

```
python3 tools/verify_preparation.py --repo-local --report evidence/REPO_LOCAL_VERIFICATION.json
```

Scope line (also embedded in the record): *Repository-local: published file set only (174 COPY_MANIFEST destinations and their recorded hashes/totals); sibling source trees and the 15,978-file preservation baseline are not asserted*

Verbatim output:

```json
{
  "schema_version": 1,
  "checked_utc": "2026-11-16T22:10:23.657639+00:00",
  "scope": "Repository-local: published file set only (174 COPY_MANIFEST destinations and their recorded hashes/totals); sibling source trees and the 15,978-file preservation baseline are not asserted",
  "status": "PASS",
  "checks": {
    "copies": {
      "files": 174,
      "bytes": 30083827,
      "roles": {
        "canonical-master": 7,
        "course-source": 35,
        "supporting-reference-data": 65,
        "planning-reference": 18,
        "archived-governance-reference": 49
      },
      "manifest_sha256": "07d49735060796c3d34191b66b5fe9991232279f5849147c7e2b0f5ad59b72c9",
      "master_resource_check": "Static loaded-resource attributes only; no browser acceptance",
      "hash_matches": 174,
      "hash_format": {
        "algorithm": "sha256",
        "recorded_lengths": [
          64
        ],
        "all_lowercase_hex": true,
        "inspection_prefix_example": "07d49735060796c3",
        "rule": "Full 64-character digests compare by equality; shorter lowercase hex values compare as prefixes"
      },
      "published_set": {
        "declared": 174,
        "enumerated": 174,
        "undeclared": [],
        "absent": []
      },
      "manifest_destination_recorded": "/home/robertsrff/Chemistry_Med/Chemistry_1st_coriculum",
      "manifest_matches_committed_record": true,
      "sibling_source_identity": "NOT ASSERTED in repository-local mode"
    },
    "preservation": {
      "status": "NOT ASSERTED",
      "reason": "Requires the unpublished sibling Chemistry_1 through Chemistry_7 trees and their baseline",
      "scope": "All regular non-symlink files under Chemistry_1 through Chemistry_7"
    },
    "programme": {
      "sha256": "f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9",
      "bytes": 353208,
      "pages_inspected": 4,
      "year": 2025,
      "page_render_review": "Four Poppler PNGs directly inspected during preparation"
    },
    "roadmap": {
      "sections": 14,
      "core_tasks": 20,
      "feature_proposals": 10,
      "diagnostics": 5,
      "core_card_shape": "3 main steps; 2 subtasks with 3 substeps each",
      "sha256": "e218fdf1d83dce3f5bc132bd7ea99ffcd398a67b153b960a225fafc9ecdc66a9"
    },
    "design_data": {
      "coverage_rows": 64,
      "core_programme_paraphrase_rows": 63,
      "supplementary_application_rows": 1,
      "families": 28,
      "variant_specifications": 112,
      "question_types": 18,
      "slots": 21,
      "points": 100,
      "minutes": 180,
      "schema_check": "Draft 2020-12 schema structure checked with installed jsonschema; no release instances exist",
      "scope": "Specifications only; no 112-item release bank or three assembled forms yet"
    },
    "examples": {
      "examples": 14,
      "independently_recomputed_numeric_examples": 13,
      "numeric_fields_checked": 29,
      "net_redox_atom_charge_balance": true,
      "limit": "Arithmetic and one structured balance; no official-key, complete scientific or learner-trial acceptance"
    }
  },
  "failures": [],
  "not_performed": [
    "Simulator runtime",
    "Browser rendering of masters/application",
    "Accessibility/assistive technology",
    "Assessment paper/PDF rendering",
    "Full chemistry/source verification",
    "Student/instructor trial",
    "Source-to-copy identity against the sibling Chemistry_1 through Chemistry_7 trees",
    "The 15,978-file source-workspace preservation baseline (evidence/source_workspace_baseline.json)",
    "Full-workspace default-mode PASS issued from a clean clone (the siblings are not published)"
  ],
  "mode": "repo-local",
  "environment": {
    "python": "3.12.16",
    "platform": "Linux-7.3.3-200.fc44.x86_64-x86_64-with-glibc2.43",
    "workspace": "/home/robertsrff/Chemistry_Med/Chemistry_1st_coriculum"
  },
  "not_asserted": [
    "Source-to-copy identity against the sibling Chemistry_1 through Chemistry_7 trees",
    "The 15,978-file source-workspace preservation baseline (evidence/source_workspace_baseline.json)",
    "Full-workspace default-mode PASS issued from a clean clone (the siblings are not published)"
  ]
}
```

**Hash-format reading:** all 174 manifest values are 64 lowercase hex characters. The inspection's `07d49735060796c3` is a 16-character prefix of the manifest file digest `07d49735060796c3d34191b66b5fe9991232279f5849147c7e2b0f5ad59b72c9`, not a stored short digest. The comparator accepts a full digest by equality and a 4–64 character lowercase hex value as a prefix; the short-hash fixture below proves the prefix path.

**Clean-copy confirmation:** the committed report above was written in the workspace (the siblings happen to exist there but this mode never reads them). The same command was also run on `/tmp/opencode/n01-published`, a byte-identical copy of the published tree with no `.git` metadata and no sibling `Chemistry_1`–`Chemistry_7` directories. It returned `PASS` with the same 174 files, 30,083,827 bytes and 174 hash matches; the only differences were `checked_utc` and `environment.workspace` (`/tmp/opencode/n01-published`). The default mode on that same copy still failed with `KeyError: 1` (§6), which is the two-environment boundary visible in one tree.

## 4. Negative fixtures — the verifier must be able to fail

All fixture trees are `cp -a` copies of the clean published copy; only the named target file was mutated, so byte content elsewhere is untouched. The copies are byte-exact (no line-ending normalization, no re-encoding).

| Fixture | Result | First named failure |
|---|---|---|
| tamper | `FAIL` (exit 1) | Published size mismatch: materials/Chemistry_1/SOURCE_LEDGER.md |
| delete | `FAIL` (exit 1) | Missing published file: materials/Chemistry_3/build/taskbase.py |
| truncate | `FAIL` (exit 1) | Published size mismatch: materials/Chemistry_4/build/source_conflicts.json |
| deleted master (supplemental) | `FAIL` (exit 1) | Missing published file: materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html |
| short-hash prefix | `PASS` (exit 0) | none |

Exact failure lines:

```
# tamper: materials/Chemistry_1/SOURCE_LEDGER.md, +1 byte
Published size mismatch: materials/Chemistry_1/SOURCE_LEDGER.md
Published hash mismatch: materials/Chemistry_1/SOURCE_LEDGER.md

# delete: materials/Chemistry_3/build/taskbase.py
Missing published file: materials/Chemistry_3/build/taskbase.py
Copied role counts differ
Declared files absent from the published set: ['materials/Chemistry_3/build/taskbase.py']

# truncate: materials/Chemistry_4/build/source_conflicts.json, 9,473 -> 4,736 bytes
Published size mismatch: materials/Chemistry_4/build/source_conflicts.json
Published hash mismatch: materials/Chemistry_4/build/source_conflicts.json

# supplemental: deleted canonical master, graceful failure (no traceback)
Missing published file: materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html
Copied role counts differ
Missing one or more topic masters
```

The short-hash fixture rewrote all 174 manifest digests to their first 16 characters and still returned `PASS` with `hash_matches: 174` and `recorded_lengths: [16]`, proving the manifest's own format is honored. The deleted-master fixture proves a missing canonical master fails by name instead of reproducing the V-01 `KeyError` in repository-local mode.

## 5. Source-freeze inventory and checker

Artifact: `evidence/SOURCE_FREEZE_INVENTORY.json` — 19 entries, 18 `FROZEN`, 1 `UNAVAILABLE`. Frozen entries carry id, path, role, byte size, SHA-256 and consuming tasks. The completeness rule is recorded in the artifact: every consumed source has exactly one entry with status `FROZEN` or `UNAVAILABLE`; an unavailable source carries its consequence and is never dropped. `SIBLING-SOURCES` is the recorded `UNAVAILABLE` entry (the original `Chemistry_1`–`Chemistry_7` trees), with the consequence that default-mode source comparison and the preservation baseline cannot run from a clean clone.

Checker: `python3 tools/check_source_inventory.py`. Green pass on the live workspace and on the clean published copy:

```
PASS source-freeze-inventory: 19 entries, 18 frozen, 1 unavailable, root=/tmp/opencode/n01-published
  OK C1-MASTER: 1018215 bytes sha256=037f847f78a5b30ebcd761cf2ad3875a9809b607a809850598dedb8af20d7b39 (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html)
  OK C2-MASTER: 969738 bytes sha256=35819d730d74909b0b556aa8aee24d5babaa878cfe9a1afd732cb9dc51d8efea (materials/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html)
  OK C3-MASTER: 1039699 bytes sha256=d64268ce5410004f9002d36b9815a58e25a40435c0b92e81b84d8fd95997888f (materials/Chemistry_3/Master_3_tema_skidumi_un_koncentracijas.html)
  OK C4-MASTER: 2502506 bytes sha256=6ec59d7845049c6554c7ca5b3c3d7ff75cabc938fdb1893042b994641d2a2845 (materials/Chemistry_4/Master_4_temats_termodinamika.html)
  OK C5-MASTER: 1518065 bytes sha256=04e0efba7f27a0e6b4b532caa773e1d6a88f69f020e0fdbbd55437646e0fe3bb (materials/Chemistry_5/Master_5_tema_kinetika_un_katalize.html)
  OK C6-MASTER: 1829918 bytes sha256=0213a11a7c78f9aa8f8715264f584b4c2c84a8d8f187c0f1028483d65db8bdd7 (materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html)
  OK C7-MASTER: 348993 bytes sha256=a4879bbd2c2519fb705e6f39cf5c4199d27d3dafcce4a89d272df9cd31ff6b3f (materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html)
  OK COPY-MANIFEST: 57793 bytes sha256=07d49735060796c3d34191b66b5fe9991232279f5849147c7e2b0f5ad59b72c9 (COPY_MANIFEST.json)
  OK PROGRAMME-PDF: 353208 bytes sha256=f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9 (RSU_MedChem_Colloq1_Prog_LV_2025.pdf)
  OK SIMULATION-BLUEPRINT: 8267 bytes sha256=97235e27857a28199685acec39780829663acf55668ec98c6e14cfbb028a7197 (docs/SIMULATION_BLUEPRINT.json)
  OK AGENTS-MD: 2743 bytes sha256=93c8dd5b1a7f1a330cbbbc941df99ac84a9235c0505c2aa1ff118e2e5d1bc548 (AGENTS.md)
  OK PREDECESSOR-ROADMAP: 76047 bytes sha256=e218fdf1d83dce3f5bc132bd7ea99ffcd398a67b153b960a225fafc9ecdc66a9 (MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md)
  OK COVERAGE-MATRIX: 22611 bytes sha256=89c38b9e44a82840380e012d46303dacd1f22b70548b62917118e9b16aaac3c0 (docs/PROGRAMME_COVERAGE_MATRIX.csv)
  OK QUESTION-FAMILIES: 46937 bytes sha256=7e168dc21b82f5b713c0e1ccf854889e5450c73db0decf23dc2d1aa80064dde4 (docs/QUESTION_FAMILIES.json)
  OK QUESTION-SCHEMA: 5350 bytes sha256=5984f03b845c0d7248311b0311cd6ffb419762809b845db2a32c33dd7eb1ac88 (docs/QUESTION_SCHEMA.json)
  OK EXAMPLE-QUESTIONS: 17375 bytes sha256=f5c9f2b62b14473126035af49efe5ba3eacf171628a2b4b84189f0c096126506 (docs/EXAMPLE_QUESTIONS.json)
  OK QUESTION-TYPES-DOC: 29562 bytes sha256=537aa96baab9afcc2986391b3bc27a3c788cbc349452c79cf2db6d58e67a3136 (docs/QUESTION_TYPES_AND_VARIANTS.md)
  OK PROGRAMME-EXTRACT: 12135 bytes sha256=3aa14e35597d1ea8e44652eeba0a578d1a487ed61a76630f811f644f82467580 (evidence/programme_extracted.txt)
  UNAVAILABLE SIBLING-SOURCES: Chemistry_1 through Chemistry_7 (parent workspace, not published) - recorded, not present
  PDF f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9 == inspection anchor f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9
```

**Programme PDF digest match, twice:** the live recomputation line above prints `f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9`, equal to the inspection value in the roadmap and the committed record. The inventory entry records the same digest and size 353,208 bytes.

Tamper fixture over a scratch copy (C1 master, 1,018,215 → 1,018,216 bytes; exit 1):

```
FAIL source-freeze-inventory: 19 entries, 18 frozen, 1 unavailable, root=/tmp/opencode/fx-inventory-tamper
  FAIL C1-MASTER: bytes 1018216 != 1018215 (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html)
  FAIL C1-MASTER: sha256 3e89a3205460d5d3180247be516895a8dc902a86d5191602f38b2ac540b6ecf4 != 037f847f78a5b30ebcd761cf2ad3875a9809b607a809850598dedb8af20d7b39 (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html)
  OK C2-MASTER: 969738 bytes sha256=35819d730d74909b0b556aa8aee24d5babaa878cfe9a1afd732cb9dc51d8efea (materials/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html)
  OK C3-MASTER: 1039699 bytes sha256=d64268ce5410004f9002d36b9815a58e25a40435c0b92e81b84d8fd95997888f (materials/Chemistry_3/Master_3_tema_skidumi_un_koncentracijas.html)
  OK C4-MASTER: 2502506 bytes sha256=6ec59d7845049c6554c7ca5b3c3d7ff75cabc938fdb1893042b994641d2a2845 (materials/Chemistry_4/Master_4_temats_termodinamika.html)
  OK C5-MASTER: 1518065 bytes sha256=04e0efba7f27a0e6b4b532caa773e1d6a88f69f020e0fdbbd55437646e0fe3bb (materials/Chemistry_5/Master_5_tema_kinetika_un_katalize.html)
  OK C6-MASTER: 1829918 bytes sha256=0213a11a7c78f9aa8f8715264f584b4c2c84a8d8f187c0f1028483d65db8bdd7 (materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html)
  OK C7-MASTER: 348993 bytes sha256=a4879bbd2c2519fb705e6f39cf5c4199d27d3dafcce4a89d272df9cd31ff6b3f (materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html)
  OK COPY-MANIFEST: 57793 bytes sha256=07d49735060796c3d34191b66b5fe9991232279f5849147c7e2b0f5ad59b72c9 (COPY_MANIFEST.json)
  OK PROGRAMME-PDF: 353208 bytes sha256=f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9 (RSU_MedChem_Colloq1_Prog_LV_2025.pdf)
  OK SIMULATION-BLUEPRINT: 8267 bytes sha256=97235e27857a28199685acec39780829663acf55668ec98c6e14cfbb028a7197 (docs/SIMULATION_BLUEPRINT.json)
  OK AGENTS-MD: 2743 bytes sha256=93c8dd5b1a7f1a330cbbbc941df99ac84a9235c0505c2aa1ff118e2e5d1bc548 (AGENTS.md)
  OK PREDECESSOR-ROADMAP: 76047 bytes sha256=e218fdf1d83dce3f5bc132bd7ea99ffcd398a67b153b960a225fafc9ecdc66a9 (MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md)
  OK COVERAGE-MATRIX: 22611 bytes sha256=89c38b9e44a82840380e012d46303dacd1f22b70548b62917118e9b16aaac3c0 (docs/PROGRAMME_COVERAGE_MATRIX.csv)
  OK QUESTION-FAMILIES: 46937 bytes sha256=7e168dc21b82f5b713c0e1ccf854889e5450c73db0decf23dc2d1aa80064dde4 (docs/QUESTION_FAMILIES.json)
  OK QUESTION-SCHEMA: 5350 bytes sha256=5984f03b845c0d7248311b0311cd6ffb419762809b845db2a32c33dd7eb1ac88 (docs/QUESTION_SCHEMA.json)
  OK EXAMPLE-QUESTIONS: 17375 bytes sha256=f5c9f2b62b14473126035af49efe5ba3eacf171628a2b4b84189f0c096126506 (docs/EXAMPLE_QUESTIONS.json)
  OK QUESTION-TYPES-DOC: 29562 bytes sha256=537aa96baab9afcc2986391b3bc27a3c788cbc349452c79cf2db6d58e67a3136 (docs/QUESTION_TYPES_AND_VARIANTS.md)
  OK PROGRAMME-EXTRACT: 12135 bytes sha256=3aa14e35597d1ea8e44652eeba0a578d1a487ed61a76630f811f644f82467580 (evidence/programme_extracted.txt)
  UNAVAILABLE SIBLING-SOURCES: Chemistry_1 through Chemistry_7 (parent workspace, not published) - recorded, not present
  PDF f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9 == inspection anchor f72763749d56ac712107560579ebc8e3716bfce2f6706402629da65c1d5f38b9
  FAIL C1-MASTER: byte size 1018216 differs from recorded 1018215 (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html)
  FAIL C1-MASTER: sha256 differs from recorded value (materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html)
```

## 6. Default-mode status — honest boundary

- **Full-workspace rerun (this environment):** `python3 tools/verify_preparation.py` returned `PASS` with 174 files, 30,083,827 bytes, 15,978 preserved files, status `PASS`, and output identical to the committed `evidence/PREPARATION_VERIFICATION.json` except `checked_utc` (VERIFIED 2026-11-16, author workspace present). This confirms the default path still works where the siblings exist.
- **Clean-clone default mode:** still `FAIL` with `KeyError: 1` at the same expression (`verify_data`, `masters[topic].ids`; the line moved to 259 after the additive edit). The mode flag did not remove the original failure, and the default behavior is otherwise byte-for-byte identical in output.
- **Committed record:** `evidence/PREPARATION_VERIFICATION.json` remains **DOCUMENTED BUT NOT RERUN** as a clean-clone result; the roadmap does not borrow the author's PASS as its own.

## 7. Handoff

The frozen inventory is the citation baseline for **N02** (coverage anchors), **N03** (conventions citations and the V-01 registry entry), **N04** (schema/type contracts) and **N05** (golden vectors). Later tasks cite an inventory id and re-run `tools/check_source_inventory.py`; a changed digest is a visible event, never a silent substitution. The V-01 entry is handed over in `evidence/V01_CONFLICT_ENTRY.json` in the forward-compatible registry format described there.

## 8. Commands run

```
cd /tmp/opencode/n01-clean-clone && python3 tools/verify_preparation.py                 # V-01 reproduction, exit 1
python3 tools/verify_preparation.py                                                     # full workspace, PASS (identical except checked_utc)
python3 tools/verify_preparation.py --repo-local --report evidence/REPO_LOCAL_VERIFICATION.json  # republished set, PASS
python3 tools/check_source_inventory.py                                                 # 19 entries, PASS
python3 tools/check_source_inventory.py --root /tmp/opencode/fx-inventory-tamper        # C1 tamper, exit 1
# negative verifier fixtures: --repo-local in /tmp/opencode/fx-tamper, fx-delete, fx-truncate, fx-prefix, fx-delete-master
```
