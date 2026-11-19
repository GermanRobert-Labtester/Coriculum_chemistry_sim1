# N05 Verification Record — Golden Vectors, Independent Oracle & Cross-Language Seed Policy

**Status:** closed 2026-11-17 (UTC).  
**Label:** **VERIFIED (2026-11-17, this environment)**.  
**PRNG Scope Notice:** **NON-CRYPTOGRAPHIC** — SplitMix64 (`splitmix64-u64-v1`) is a deterministic 64-bit integer PRNG for reproducible sampling, form assembly, and test generation only. It provides no cryptographic strength and must never be used for security, authentication, tokens, or proctoring.

---

## 1. Cross-Language PRNG Twins & Seed Policy (`data/seed_policy.json`, `tools/prng.py`, `src/prng.js`)

- **Algorithm:** SplitMix64 (`splitmix64-u64-v1`), zero third-party libraries.
- **Constants:**
  - `MASK_64 = 0xFFFFFFFFFFFFFFFF` (`18446744073709551615`)
  - `GAMMA = 0x9E3779B97F4A7C15` (`11400714819323198485`)
  - `MUL1 = 0xBF58476D1CE4E5B9` (`13787848793156543929`)
  - `MUL2 = 0x94D049BB133111EB` (`10723151780598845931`)
  - `SHIFT1 = 30`, `SHIFT2 = 27`, `SHIFT3 = 31`
- **JavaScript integer-safety rule:** All PRNG state, step multiplication, shifts, and rejection sampling use ES `BigInt` (`0x...n & 0xFFFFFFFFFFFFFFFFn`). Floating-point `Number`, `Math.random()`, `Date.now()`, and 32-bit signed bitwise ops (`| 0`, `>>`) are forbidden inside PRNG computations. 64-bit integers cross JSON boundaries as exact decimal strings so `JSON.parse` cannot round them to float64.
- **Fisher-Yates shuffle rule:** Non-mutating copy; top-down `for i = n - 1 down to 1: j = nextInt(i + 1); swap(arr[i], arr[j])` using unbiased 64-bit rejection sampling (`threshold = ((1 << 64) - bound) % bound`).
- **Illegal seed & bound rejection:** `0`, negative integers, integers `> 2^64 - 1`, floats (`1.5`, `NaN`, `Infinity`), booleans, strings, and `null` are rejected identically in both Python and JavaScript with `E_PRNG_INVALID_SEED` (10/10 cases). Bounds `<= 0` or non-integer are rejected with `E_PRNG_INVALID_BOUND` (3/3 cases).

### 1.1 Cross-Language Contract Value Table (`data/prng_contract_vectors.json`)

- **Table SHA-256:** `eb5dd65faae6eda2d098dec424bf11d8c066b8fa1cb0abba1f58cbfee5f617c6`
- **11 Declared Seeds × 100 `nextU64()` Draws (1,100 draws, 0 divergences across Python & JavaScript):**

| Seed (decimal) | First 100 `nextU64()` Draws SHA-256 (Python == JavaScript) |
|---|---|
| `1` | `3b5e7ac481811f733b2f37d614367e0e263855548af7b9391d4efe3c4d46438b` |
| `2` | `396e34989b87308d55ab661789f891876ea52af0238cd2e02fe7d1844f58579e` |
| `42` | `07697948a7dc77722c38b9d8784240b4ab282463ce80c4e97f33951fcd8dc58e` |
| `1337` | `88f1f33cae90850cf8173b84e1757298c289750ce8b11d28d0f62514ab685d9e` |
| `2025` | `95100de30b3f926da90dbca986d1b819eb6271a8cc7afed9b961d9718df26231` |
| `20261116` | `5297a15a80cf2f31d96d11690ff592e2e3df9669c5441337e65b55319371e2d9` |
| `240001` | `ec5fd0ba0f59e55501c22cb067db533d6115a1340c8561ba269468b8eb8b86a5` |
| `2147483647` | `aa57745f3f07b737db322e7d0070b6044ef4fc500d022de12d41b87cf28107b8` |
| `4294967295` | `ffe86d5accc6ea84f8b4ea43d2e65ef6770053bbc89e2e558237f92cb70d11e6` |
| `9007199254740993` | `06878cb34efb4f0d552950fccd6c9e0fbd87352bc583fbc9e5692a6dc6aa1e52` |
| `18446744073709551615` | `69517e56d7ded704d8f3bfd30f463141ecd9eb9e3c28cbbfee042d51575c011f` |

- **Bounded & Shuffle Cross-Language Fixtures:**
  - `BOUND-21-S1` (50 draws): `c391e6575c4a9afe67a52834d979593da2eb26c518693f13cf31fec1e7e47efa`
  - `BOUND-7-N24A` (50 draws): `4dd871e31f916c5f44538213c3c175b26a090be5fa70e6b447f67b2ccf408ccc`
  - `BOUND-1-EDGE` (5 draws): `fd76db5c8ad0929aeca788d3e83adb863069b1dc11c4c707e9c14286388dc970`
  - `RANGE-10-20` (30 draws): `6400e73fcbfd74f0d3ec62f01fcb5022d8114acdaf22c116a6a9e1ac8aaf8abf`
  - `BOUND-BIG-U64SEED` (25 draws): `2e1fac594cbc4c4de8c3ca380f7a0857104abdfc3f59d0ada080dc11cb33b72b`
  - `SHUFFLE-21-SLOTS` (20 draws consumed): `d21fff4fe26f215845a19091ae38cc34cd9a0dff74257fcba89fb28802fdfb32`
  - `SHUFFLE-4-OPTIONS` (3 draws consumed): `a041b1759a026921bf7f8350e9ba54b07f64e327899580afb51d76a8b36247c2`
  - `SHUFFLE-1-ITEM` (0 draws consumed): `990655330780a126452411bec34a926252b3960edd17abf31b7b74d88f64148c`
  - `SHUFFLE-EMPTY` (0 draws consumed): `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

### 1.2 Perturbation Catches

- **JS GAMMA altered (`0x9E3779B97F4A7C15n -> 0x9E3779B97F4A7C16n`):** Caught (`16` stream/bounded/shuffle divergences); first divergence on seed `1`, `draw_index=0`: Python `10451216379200822465` vs JS `10905525725756348110`.
- **Python MUL1 altered (`0xBF58476D1CE4E5B9 -> 0xBF58476D1CE4E5BA`):** Caught (`17` divergences); first divergence on seed `1`, `draw_index=0`: Python `16781798957938450705` vs JS `10451216379200822465`.

### 1.3 Seed Vocabulary (`data/seed_policy.json`)

| Consumer | Range (inclusive) | Recording Rule |
|---|---|---|
| `N24_assembly` | `100000`–`199999` (`form_A=100001`, `form_B=100002`, `form_C=100003`, sweep `100101`–`100110`, training `101000`–`199999`) | Form manifest records `form_seed`, `policy_id`, `prng_contract_digest` |
| `N27_sample_selection` | `200000`–`299999` | Session log records `sample_seed`, `policy_id` |
| `N30_workload_generation` | `300000`–`399999` | Practice attempt metadata records `workload_seed`, `family_id`, `policy_id` |
| `N20_bank_authoring` | `400000`–`499999` | Authoring manifest records numeric `prng_seed` + `policy_id` |
| `N05_N36_verification` | `500000`–`599999` + 11 contract seeds | Test manifest records sweep seeds + `policy_id` |

---

## 2. Independent Oracle & First Vector Stratum (`tools/golden_oracle.py`, `data/golden_vectors.json`)

- **Oracle import manifest (`tools/golden_oracle.py --manifest`):**
  - `oracle_version`: `1.0.0`, `oracle_digest`: `f7781ddc23fa2f33b7d580959aa7e8c02d6e7aff7dc9e9f79a7602db9e5bb493`
  - `imports`: `["__future__", "argparse", "ast", "decimal", "fractions", "hashlib", "json", "pathlib", "re", "sys", "typing"]`
  - `disallowed_imports`: `[]` (`independent_of_engines: true`)
- **Hand-computed spot checks (`evidence/N05_ORACLE_RECORD.json`):**
  1. `SPOT-1-NUMERIC-CONVERSION-SIGFIG` (`GV-S1-T2-Q01-01`): `4,50×10³ mg -> 4.50 g`, `3 sig figs == 3`, `correct`, `NONE`, `2.0/2.0` — **agreed**.
  2. `SPOT-2-TOLERANCE-EDGE-AND-HALF-UP` (`GV-S1-T2-Q10-01`, `GV-S1-T4-Q09-01`): inclusive burette boundary `|16.30 - 16.25| = 0.05 <= 0.05` (`correct`), and `1.125` rounded `half_up` to `1.13` (`|1.14 - 1.13| = 0.01 <= 0.01`, `correct`) — **agreed**.
  3. `SPOT-3-V04-DENSITY-DEFECT-ERROR-CLASS` (`GV-S1-T3-Q02-02`): `w = 10.0 % (m/m)`, `ρ = 1.070 g/mL -> γ = 107.0 g/L`; submitted `100.0 g/L` (`= 107.0 / 1.070`, omitted `ρ`) -> `incorrect`, `DIMENSIONAL_INCONSISTENCY` — **agreed**.

### 2.1 Stratum 1 Coverage Table (40 Active Vectors, 0 Retired)

- **By Topic (all 7 topics):** T1: `9`, T2: `11`, T3: `6`, T4: `4`, T5: `3`, T6: `3`, T7: `4`.
- **By Fixed Type (11 types, ≥ 2 instances each):** `Q01` (6), `Q02` (7), `Q06` (4), `Q07` (3), `Q08` (3), `Q09` (3), `Q10` (3), `Q12` (3), `Q14` (3), `Q15` (3), `Q18` (2). (Types `Q03`, `Q04`, `Q05`, `Q11`, `Q13`, `Q16`, `Q17` are deferred to Phase IV strata `S2-N17`–`S4-N19` per the out-of-scope rule.)
- **By Verdict Class:** `correct` (16), `incorrect` (15), `auto_passed_pending_review` (5), `partial` (2), `pending_self_assessment` (2).
- **By Error Class:** `NONE` (23), `OUT_OF_TOLERANCE` (4), `WRONG_OPTION_SELECTION` (3), `DIMENSIONAL_INCONSISTENCY` (2 — V-04 density defect + blocked `mg -> L`), `WRONG_PAIRING` (2), `BLANK_RESPONSE` (1), `OUT_OF_DOMAIN_EXTRAPOLATION` (1), `SIG_FIG_MISMATCH` (1), `UNLABELED_PERCENT_BASIS` (1), `UNREADABLE_INPUT` (1), `WRONG_ORDER` (1).
- **N04 Schema Validator Cross-Check (`tools/validate_bank.py`):** `PASS` (`40/40` instances, `0` violations).

---

## 3. Growth Protocol, Replay Parity, Perturbation-and-Revert & Build Gate

- **Growth protocol (`data/golden_vector_protocol.json`):** Append-only; existing active vectors are never edited in place. A retired-ID reuse fixture (`GV-S1-T1-Q02-01` placed in `retired_ids`) failed `validate_golden_vectors.py` and caused `tools/build.py` gate order 4 (`golden_vectors`, owner `N05`) to exit `1` without writing any artifact.
- **Twice-fresh-process oracle replay:**
  - Replay 1 stdout SHA-256: `290ae55ccc9a4b2beff2229405bc5383d6911fef28245e0cdf89073ab3b8634d`
  - Replay 2 stdout SHA-256: `290ae55ccc9a4b2beff2229405bc5383d6911fef28245e0cdf89073ab3b8634d`
  - `results_sha256`: `5fc0f2638d76332ff970c34217fe9ff9541aa7dcb75a707daeccb479094f5a79` (**identical**)
- **Conventions perturbation-and-revert proof:**
  - Scratch conventions copy changed `tolerances.quantity_classes[id=burette_volume].absolute.value` from `"0.05"` to `"0.01"`.
  - Perturbed `results_sha256`: `c01b7f4c334fbc22bf291c8f5525b46dc1503c33840117a041271bf0e81b8b17` — flipped **only** `GV-S1-T2-Q10-01` (`correct / NONE` -> `incorrect / OUT_OF_TOLERANCE`).
  - Restored `results_sha256`: `5fc0f2638d76332ff970c34217fe9ff9541aa7dcb75a707daeccb479094f5a79` (**restored identical**).
- **Build & Runtime (`output/simulator.html`, `src/golden-vectors-loader.js`):**
  - `output/simulator.html`: `299,856` bytes (`sha256=e624bff466a7ff9baf3f59ccb1441cfd5e505ca4471c69d8b473d2a24de92669`), gates 1–4 `PASS`, double-build parity `true`.
  - Runtime harness (`node tools/check_golden_vectors_runtime.js --json`): `PASS`, 40 active vectors, `SimPRNG` smoke OK, honest named degradation on truncated (`E_VECTORS_JSON`), missing (`E_VECTORS_MISSING`), and retired-ID reuse (`E_VECTORS_RETIRED_REUSE`).
- **Corpus parity:** Two consecutive runs of `python3 tools/n05_corpus.py` produced byte-identical `N05_PRNG_CONTRACT.json`, `N05_ORACLE_RECORD.json`, and `N05_CORPUS_RECORD.json`.
- **Handoff:** Seed vocabulary handed to **N24**, **N27**, **N30**; vector format & growth protocol handed to **N17–N19**, **N36**; `#sim-golden-vectors` smoke island handed to runtime loaders.
