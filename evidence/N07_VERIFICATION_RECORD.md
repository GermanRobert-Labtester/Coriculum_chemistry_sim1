# N07 Verification Record — Concept Map, ASCII Anchor Graph & Concept Drawer

**Status:** closed 2026-11-17 (UTC).  
**Label:** **VERIFIED (2026-11-17, this environment)**.  
**Visual inspection note:** `N07_PAINT_MAP_LIGHT.png`, `N07_PAINT_MAP_DARK.png`, `N07_PAINT_MAP_320.png`, and `N07_PAINT_DRAWER_OPEN.png` were captured via `lite-shot -e falkon --cdp` and visually inspected; they are render checks only, not full WCAG/screen-reader acceptance (deferred to N32/N33/N37/N38).

---

## 1. Layered Map Model, Acyclicity, Wrap Rule & Semantic Structure (`#karte`, `src/concept-map.js`)

- **Graph source:** Single-sourced directly from `#sim-coverage` (`64` outcomes across `7` topics, `127` prerequisite edges including `20` cross-topic edges; zero invented nodes or edges).
- **Declared layout rules (`SimConceptMap.LAYOUT_RULES`):**
  - **Layer rule:** `layer(u) = 0 if prerequisites(u).length === 0 else 1 + max(layer(p) for p in prerequisites(u))`
  - **Tie-break within layer:** ascending ASCII outcome `id` (`P1-01 < P1-02 < ...`)
  - **Wrap threshold:** `3` nodes per row per layer (`wrap_threshold = 3`), paired with fluid token CSS (`min(100%, var(--grid-card-min))`) and `overflow-wrap: anywhere` so wide layers wrap cleanly down to the `320px` viewport class.
- **Layout determinism digests:**
  - Python (`tools/validate_n07_map.py`): `3a43d26087bc177e60cf7b3606b8368397a00d7a79ef119a1d6355625e3be913` (`max_layer = 10`, `64` nodes, `127` edges, `20` cross-topic).
  - Runtime JS (`tools/check_n07_runtime.js`, two runs): `1ee006ae3827293b84696bb1c6509ec4ce03aec2f4787c2b59ec41f30d450f96` (identical across runs).
- **Corner-case & acyclicity fixtures:**
  - **Diamond fixture (`A -> B, A -> C, B -> D, C -> D`):** placed at `{"A": 0, "B": 1, "C": 1, "D": 2}` with layer 1 tie-break order `["B", "C"]` in both Python and JS.
  - **Wide-layer Topic 3 fixture (11 outcomes sharing layer 0):** `wrapped = true`, chunked into `4` rows of sizes `[3, 3, 3, 2]` (`[P3-01..03], [P3-04..06], [P3-07..09], [P3-10..11]`).
  - **Cycle rejection:** Python `validate_n07_map.py` and JS `SimConceptMap.computeLayout` both reject a cyclic graph by name (`Cycle detected in prerequisite graph: P1-01 -> P1-03 -> P1-05 -> P1-01` and JS `ConceptMapError` code `E_MAP_CYCLE`). Injecting a cycle into `tools/build.py` fails gate order `1` (`coverage`) before writing any artifact.
- **Semantic & keyboard accessibility check (`tools/check_n07_runtime.js`):**
  - `64/64` node triggers (`#karte-btn-P1-01`..`#karte-btn-P7-05`) rendered as focusable `<button type="button">` elements with explicit `aria-label` announcing concept ID, statement, master anchor, and layer.
  - `127/127` prerequisite edge links rendered as `<a class="map-edge-link" href="#karte-...">` with `aria-label` announcing edge kind (`Priekšnosacījums` / `Starptēmu priekšnosacījums`), source, and target.
  - `20/20` cross-topic edges rendered in `#karte-starptemu-saites` with named target-drawer triggers (`#karte-cross-open-*`).
  - `7/7` per-topic `<pre id="karte-ascii-tema-N">` ASCII anchor graphs rendered inside collapsible `<details>`.

---

## 2. Anchor-Link Registry & Build-Time Resolution (`data/anchor_registry.json`, `tools/validate_n07_map.py`)

- **Registry pass (`64/64` concepts, `7/7` `#karte-tema-N` anchors, `127/127` prerequisite edge links, `64/64` `#rezultats-P*` links, `#concept-drawer` target):** `PASS`.
- **Negative fixture (`dangling_concept_link`):** Injecting `#karte-P9-99` (`from: "P9-99"`) into `P1-01`'s `prerequisite_edges` failed `validate_n07_map.py` (`P1-01: dangling prerequisite link 'P9-99' -> '#karte-P9-99'`) and caused `tools/build.py` gate order `7` (`concept_map`, owner `N07`) to exit `1` without writing any artifact.

---

## 3. Concept Drawer, Summaries, Wording Rule & Slots (`data/concept_summaries.json`, `src/concept-drawer.js`)

### 3.1 Verbatim Summary Wording Rule
> Kur divi meistari vai avoti jēdzienu formulē atšķirīgi (īpaši V-02 procentu bāzes un V-03 redokspotenciālu pieraksts), kopsavilkums seko #sim-conventions deklarētajam noteikumam un tieši nosauc avotu atšķirību (dissent).

- **Frozen master anchor re-validation:** `64/64` summary citations (`master_path`, `master_anchor`, `master_heading_lv`, `master_freeze_id`) resolved case-exactly against the frozen N01 masters (`freeze_bound = true`).
- **Negative fixture (`broken_master_anchor`):** Changing `P1-01.master_anchor` to `neeksistejoss-enkurs` failed `validate_n07_map.py` (`master_anchor #neeksistejoss-enkurs not found (case-exact)`) and caused `tools/build.py` gate order `7` to refuse the build before writing.
- **Conventions dissent enforcement (`V-02`, `V-03`):** Checked `5` V-02 outcomes (`P3-01`, `P3-03`, `P3-06`, `P3-08`, `P3-09`) and `3` V-03 outcomes (`P6-02`, `P6-03`, `P6-04`). Negative fixture (`missing_v02_v03_dissent`) removing `dissent_note_lv` from `P3-01` and `P6-02` failed `validate_n07_map.py` naming both outcomes and conflict classes.
- **Slot contract (`192/192` slots across `64` concepts):** Every concept declares `figures` (`N11`–`N15`), `chains` (`N16`), and `practice` (`N30`) as non-interactive pending slots with `owner_task` and `status: "pending-<OWNER>"`. Negative fixture (`missing_slot_owner`) deleting `owner_task` from `P1-01.slots.figures` failed `validate_n07_map.py` (`P1-01 slot 'figures': invalid or missing owner_task None`) and caused `tools/build.py` gate order `7` to refuse before writing.

### 3.2 Return-Focus & Nested Restore Fixtures (`tools/check_n07_runtime.js`)

- **Focus-sequence fixture:**
  1. `invoke`: `activeId = "karte-btn-P1-01"`
  2. `opened`: `activeId = "concept-drawer-close"`
  3. `tab-wrap-forward`: `Tab` from last focusable element inside `#concept-drawer` (`preventDefault = true`) wrapped focus to `activeId = "concept-drawer-close"`
  4. `closed-restore`: `activeId = "karte-btn-P1-01"`
- **Nested-drawer restore fixture:**
  1. `outer-open`: `P1-01` opened (`activeId = "concept-drawer-close"`)
  2. `inner-open`: invoked `#drawer-prereq-btn-P1-03` -> `P1-03` opened (`stackDepth = 2`, `activeId = "concept-drawer-close"`)
  3. `inner-close-restore`: closed `P1-03` -> returned to `P1-01` (`stackDepth = 1`, `activeId = "drawer-prereq-btn-P1-03"`)
  4. `outer-close-restore`: closed `P1-01` -> drawer closed (`isOpen = false`, `activeId = "karte-btn-P1-01"`)
- **Direct-link entry with no map state (`direct_link_no_map`):** Fresh VM with `includeMap: false` (`#karte` absent) invoked `SimConceptDrawer.openFromLink({ conceptId: "P4-10", source: "N28", returnContext: { elementId: "rem-link-P4-10", triggerEl } })` -> rendered `P4-10 — ΔG = ΔH − TΔS ar saskaņotām vienībām` with `#ch7` citation, and closing restored focus to `rem-link-P4-10`.

---

## 4. Scripted Walk Trace, Replay Parity, Smoke Vector & Byte Accounting

- **Scripted walk (`P5-07` from map -> expand chain toggle -> open deepest prereq `P1-05` -> close inner -> close outer -> open cross-topic target `P3-02` -> Escape close):** `7` trace events (`open`, `toggle-chain`, `open`, `close-nested`, `close-restore`, `open`, `close-restore`), checkpoints `afterBackFocus = "drawer-prereq-btn-P1-05"`, `afterMapRestoreFocus = "karte-btn-P5-07"`, `afterCrossRestoreFocus = "karte-cross-open-P1-06-P3-02"`.
- **Three-way replay parity (`evidence/N07_CORPUS_RECORD.json`):**
  - In-process run A digest: `6d0d18f455620e2fe596f5f634d78de4531c2e5e44d136065e4d583950656e15`
  - In-process run B digest: `6d0d18f455620e2fe596f5f634d78de4531c2e5e44d136065e4d583950656e15`
  - Fresh Node subprocess (`--walk-only`) digest: `6d0d18f455620e2fe596f5f634d78de4531c2e5e44d136065e4d583950656e15`
- **In-file smoke vector (`src/smoke-subset.js`, `SMK-N07-MAP-DRAWER-WALK`):** `PASS` (`64` nodes, `127` edges, `20` cross-topic edges, `4` walk events).
- **Double-build & corpus parity:**
  - `output/simulator.html`: `432,039` bytes, `sha256 = 883187cc6fb6a2561fb145fd1c85954f5fc09418cafd9d4292d11cac532fab3a`, `build_id = e55c66a1f80557fb` (two consecutive builds + fresh temp build byte-identical).
  - `output/build-manifest.json`: `sha256 = 6a6e5f7deee264079912663c0457d515cd12707d166afcf0bae6f2db8d3b8f8d` (byte-identical).
  - `evidence/N07_CORPUS_RECORD.json`: `12,956` bytes, `sha256 = 9b4bf033792d3d11887edd8e6fa35b408134adb48d1901bdc2b0a3c5d0b229cc` (two consecutive runs byte-identical).
- **Section 1.3 byte accounting:**
  - CSS: `21,721` bytes (ceiling `81,920` B / 80 KiB)
  - Runtime JS (including embedded compact summaries `27,015` B + compact registry `10,599` B + `concept-map.js` `22,138` B + `concept-drawer.js` `23,486` B): `153,235` bytes (ceiling `225,280` B / 220 KiB)
  - Inline SVG figures: `0` bytes (budget `60–140` KiB; N11–N15 pending)
  - Template overhead: `14,888` bytes
- **Prior-phase zero-regression:** `N02`, `N03`, `N05`, `N06` runtime harnesses and `verify_preparation.py --repo-local` all `PASS`.
- **Falkon `lite-shot` render checks:**
  - `evidence/N07_PAINT_MAP_LIGHT.png` (`1280x1024`, `--anchor karte --reduced-motion`, `overflow=false`, `sw=1259, cw=1259`, `colors=4654, ink=42%`)
  - `evidence/N07_PAINT_MAP_DARK.png` (`1280x1024`, `--anchor karte --reduced-motion`, `overflow=false`, `sw=1259, cw=1259`, `colors=4547, ink=42%`)
  - `evidence/N07_PAINT_MAP_320.png` (`320x720`, `--anchor karte-tema-3 --reduced-motion`, `overflow=false`, `sw=299, cw=299`, `colors=2720, ink=57%`)
  - `evidence/N07_PAINT_DRAWER_OPEN.png` (`1280x1024`, scratch preview opening `P3-08` drawer, `overflow=false`, `colors=7530, ink=32%`)

---

## 5. Open-Link Contract Handoff (to N08, N16, N28, N29)

- **Consumer entry point:** `SimConceptDrawer.openFromLink(payload, document)` (contract version `1`, `data/anchor_registry.json` & `src/concept-drawer.js`).
- **Payload shape:**
  ```json
  {
    "conceptId": "P3-08",
    "source": "N08 | N16 | N28 | N29 | map | direct",
    "returnContext": {
      "elementId": "invoking-control-id",
      "triggerEl": "<DOMElement optional>",
      "anchor": "#atskats",
      "labelLv": "Optional return label"
    }
  }
  ```
- **Guarantees:** Requires zero prior concept-map visit or `#karte` DOM state; validates `conceptId` against `#sim-coverage`; enforces `role="dialog"`, `aria-modal="true"`, `Tab` focus loop, `Escape`/button close, and nested stack focus restoration back to `returnContext.triggerEl` / `returnContext.elementId`.
- **Slot closure handoffs:** `figures` (`N11`–`N15`), `chains` (`N16`), and `practice` (`N30`) slots are declared and build-checked on all `64` concepts.
- **Accessibility / visual matrix handoffs:** Focus loop, nested restore, and walk trace vectors handed to **N33** and **N37**.
