# N39 — Reproducible QA Runner & SHA-256 Evidence Chain Format

**Owner Task:** N39 | **Phase:** Phase VIII | **Runner:** [`tools/qa_runner.py`](../tools/qa_runner.py) | **Independent Verifier:** [`tools/verify_qa_manifest.py`](../tools/verify_qa_manifest.py) | **Registry:** [`data/qa_registry.json`](../data/qa_registry.json) | **Manifest Schema:** [`data/qa_manifest_schema.json`](../data/qa_manifest_schema.json)

---

## 1. One-Command QA Execution

Run the complete local offline QA pipeline from the repository root:

```bash
python3 tools/qa_runner.py
```

By default this command:
1. Validates [`data/qa_registry.json`](../data/qa_registry.json): every registered suite file exists and matches its recorded SHA-256 digest (sourced from [`evidence/VERIFICATION_LEDGER.md`](../evidence/VERIFICATION_LEDGER.md) and versioned `update_history`).
2. Checks every build source file recorded in [`output/build-manifest.json`](../output/build-manifest.json) (all 132 sources) for tampering before any suite runs. Any mismatch refuses the run immediately (exit code `2`) naming the altered file(s).
3. Executes all **15 registered suites** in declared 5-tier order inside isolated per-suite environments (`TMPDIR`, `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `XDG_DATA_HOME`), continuing on failure to collect the complete diagnostic picture:
   - **Tier 1 — Build, Source Integrity & Static Gates:** `N01-PREP-LOCAL`, `N01-SOURCE-INVENTORY`, `N31-BUILD-PIPELINE` (rebuilds `output/simulator.html` and asserts its SHA-256 matches the ledger), `N31-ARTIFACT-CONTRACT`, `N31-RUNTIME-SMOKE`, `N32-WCAG-CONTRACT`, `N33-A11Y-CONTRACT`, `N34-NOSCRIPT-PRINT`
   - **Tier 2 — Audits (N35):** `N35-AUDIT-PERF`, `N35-AUDIT-STORAGE`, `N35-AUDIT-SECURITY`
   - **Tier 3 — Property & Mutation Corpus (N36):** `N36-PROPERTY-SUITE`, `N36-MUTATION-SUITE`
   - **Tier 4 — Visual Regression Matrix (N37):** `N37-VISUAL-MATRIX` (`lite-shot --engine falkon --cdp`, 73 unique renders / 219 cells)
   - **Tier 5 — Browser Offline Smoke & Staged Protocols (N38):** `N38-BROWSER-SMOKE` (3 fresh Falkon runs + calibration + N33/N35 protocols)
4. Writes the SHA-256-chained run manifest (`evidence/N39_QA_MANIFEST.json`) using the two-pass trailer rule and exits `0` only if every single registered suite passed (a skipped, failed, or timed-out suite always yields `overall_verdict = "FAIL"` and non-zero exit).

### Expected Runtime

| Tier | Suites | Expected Wall Time |
|---|---|---:|
| Tier 1 (`build_and_static_gates`) | 8 suites (`N01` + `N31`–`N34`) | `~50 s` |
| Tier 2 (`audits`) | 3 suites (`N35`) | `~4 s` |
| Tier 3 (`property_and_mutation`) | 2 suites (`N36`) | `~4 s` |
| Tier 4 (`visual_matrix`) | 1 suite (`N37`, 73 Falkon CDP renders) | `~550–650 s` |
| Tier 5 (`browser_smoke`) | 1 suite (`N38`, 3 Falkon runs + protocols) | `~35–45 s` |
| **Full QA pass total** | **15 suites** | **`~11–12 min`** |

No CI service, cloud runner, network fetch, or auto-fixing is performed. Everything runs locally and read-only with respect to repository sources.

---

## 2. Suite Registry & Versioned Update Rule

Every suite addition or legitimate modification (for example, a Phase VIII defect fix) MUST go through a versioned registry update — quiet digest edits are forbidden:

```bash
python3 tools/qa_runner.py --update-suite <SUITE_ID> --file <REL_PATH> --reason "<explicit reason>"
```

This increments `registry_version`, updates the file's `expected_sha256` and `bytes`, and appends an immutable entry to `update_history` recording `{version, timestamp, suite_id, path, previous_sha256, new_sha256, reason}`. Updating without a non-empty `--reason` is refused.

---

## 3. Two-Pass Manifest Trailer Format

To resolve the self-reference paradox (recording a file's SHA-256 inside the file itself) while keeping the manifest valid RFC 8259 JSON, `tools/qa_runner.py` writes the manifest in two passes:

1. **Pass 1:** Construct the complete manifest body object (without `manifest_trailer`), serialize with `json.dumps(body, sort_keys=True, indent=2, ensure_ascii=False) + "\n"`, write those exact UTF-8 bytes to disk, and compute `body_sha256 = SHA256(body_bytes)` and `body_bytes = len(body_bytes)`.
2. **Pass 2:** Replace the final `\n}\n` (3 bytes at EOF) with `,\n  "manifest_trailer": { ... }\n}\n` containing `algorithm: "sha256"`, `format: "two-pass-json-trailer-v1"`, `body_bytes`, `body_sha256`, and `recompute_rule`, then atomically replace the target file via `os.replace`.

### Recomputing the Manifest Self-Digest Independently

Any maintainer can recompute `manifest_trailer.body_sha256` in two independent ways:

- **Raw byte-slicing (zero JSON-serializer trust):** Find the exact trailer marker `,\n  "manifest_trailer":` in the raw UTF-8 file bytes, take all bytes preceding it, append `\n}\n`, assert `len == body_bytes`, and verify `SHA256 == body_sha256`.
- **Canonical JSON recomputation:** Parse the JSON file, delete top-level key `"manifest_trailer"`, serialize with `json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False) + "\n"`, and verify `SHA256 == body_sha256`.

---

## 4. Normalized Verdict Vector & Exclusion Rule

Two full runs over unchanged sources produce distinct `run_id` (`sequence_number`), timestamps (`started_utc`, `finished_utc`), per-suite `duration_ms`, and per-run log directory paths. Determinism is therefore asserted over the **normalized verdict vector**:

- **Included fields (in declared registry order):** `suite_id`, `tier`, `verdict`, `exit_code`, `timed_out`.
- **Excluded fields (by design):** `duration_ms`, `started_utc`, `finished_utc`, `run_id`, `sequence_number`, `stdout_path`, `stderr_path`, `report_path`.
- **Comparison key:** `normalized_verdict_vector_sha256` (SHA-256 of canonical compact sorted-key UTF-8 JSON of `normalized_verdict_vector`).

Two fresh-process runs over unchanged sources prove reproducibility when their `artifact.sha256`, `sources_composite_sha256`, `suites_composite_sha256`, and `normalized_verdict_vector_sha256` are identical.

---

## 5. Independent Maintainer Verification Procedure

To verify a recorded QA run manifest and frozen evidence pack without trusting `tools/qa_runner.py`:

```bash
python3 tools/verify_qa_manifest.py \
  --manifest evidence/N39_QA_MANIFEST.json \
  --pack evidence/N39_EVIDENCE_PACK.json
```

`tools/verify_qa_manifest.py` imports **nothing** from `tools/qa_runner.py`. It independently:
1. Validates the manifest against `data/qa_manifest_schema.json` and recomputes `manifest_trailer.body_sha256` via both raw byte-slicing and canonical JSON serialization.
2. Re-hashes `output/simulator.html`, `output/build-manifest.json`, `data/qa_registry.json`, all 132 build sources from the manifest's own paths, and every registered suite file on disk.
3. Reads every suite's raw captured `stdout`, `stderr`, and structured JSON report file from disk, verifies their SHA-256 digests, and independently re-derives each suite's verdict (`PASS` / `FAIL` / `TIMEOUT` / `SKIPPED`) from raw exit code, timeout flag, and report status fields (`status == "PASS"` / `pass == true`).
4. Independently recomputes `normalized_verdict_vector`, `normalized_verdict_vector_sha256`, and `overall_verdict`, asserting exact agreement with the manifest.
5. When `--pack` is provided, verifies every digest in `evidence/N39_EVIDENCE_PACK.json` and asserts zero unexplained absent ledger items.

Exit code `0` means complete end-to-end cryptographic and verdict agreement; exit code `1` names every discrepancy.
