# Manual Screen-Reader & Keyboard Execution Protocol (N33 -> N38)

**Policy ID:** `n33-screen-reader-protocol-v1` | **Owner:** `N33` | **Execution Target:** `N38` (Phase VIII) | **Status:** `UNVERIFIED`

## 1. Declared Environment and Honest Epistemic Scope

- **Target Deliverable:** `output/simulator.html` (offline single-file artifact, `lang="lv"`).
- **Approved Browser:** Falkon (per `AGENTS.md` workspace policy).
- **Available Assistive Tooling:** Linux offline environment (AT-SPI / Orca if installed by executor).
- **Honest Availability Statement:** Full **NVDA** (Windows) and **VoiceOver** (macOS) verification is **UNAVAILABLE** in this offline Linux workspace unless the Phase VIII executor supplies that environment. Accordingly, this protocol is staged as **`UNVERIFIED`** in `evidence/VERIFICATION_LEDGER.md` and must not be claimed as verified by inference from static or Node-harness checks.

## 2. Mandatory Defect-Filing Rule

1. **Keyboard-Completion Blocking Rule:** Any scenario or sub-step that cannot be completed by keyboard alone (without pointer/mouse input) **must be filed as a blocking defect and fixed in source**, never documented around.
2. **Discrepancy Rule:** Every mismatch between **Expected Announcement** (derived from the N33 Name Table and live-region contract) and **Observed Announcement** must be filed as a **defect** with scenario ID, step number, element ID, expected string, and observed string—never dismissed as a note.

---

## 3. Scripted Scenarios (Execution Order)

### Scenario 1 — Start Screen (`#sakums`), Theme Toggle (`m`), and Section Jumps (`1`–`9`)
**Precondition:** Open `output/simulator.html` in Falkon with screen reader active. Focus starts at document top.

| Step | Key / Action | Target Element / Region | Expected Announcement (from N33 Name Table) | Observed | Status |
|---|---|---|---|---|---|
| 1.1 | `Tab` into `#sim-nav` | `#sim-nav` (`navigation`, `"Galvenā navigācija"`) | Landmark `"Galvenā navigācija"`, navigation links (`Sākums`, `Saturs un mērķi`, `Prakse`, `Eksāmena simulācija`, …) | — | `UNVERIFIED` |
| 1.2 | Press `m` | `#theme-toggle-btn` (`button`) | Button `"Pārslēgt uz tumšo režīmu"` (or `"Pārslēgt uz gaišo režīmu"`), `#theme-status` updates | — | `UNVERIFIED` |
| 1.3 | Press `1` | `#sakums-virsraksts` (`h1`, `tabindex="-1"`) | `#sim-live-view` (`polite`): `"Skats: Pirmā kolokvija treniņsimulators"`, heading level 1 | — | `UNVERIFIED` |
| 1.4 | `Tab` to `#sakums-form-picker` | `#sakums-pick-A` (`radio`, `aria-checked="true"`) | Radiogroup `"Treniņdarba formas izvēle (PROPOSED)"`, radio `"A forma (sēkla 100001)"`, checked | — | `UNVERIFIED` |

### Scenario 2 — Practice Path (`#prakse`) with Hints (`h`), Drawer Escape, and Skip (`s`)
**Precondition:** Navigate to `#prakse` via key `3`.

| Step | Key / Action | Target Element / Region | Expected Announcement (from N33 Name Table) | Observed | Status |
|---|---|---|---|---|---|
| 2.1 | Press `3` | `#prakse-virsraksts` (`h2`, `tabindex="-1"`) | `#sim-live-view` (`polite`): `"Skats: Prakse"`, heading level 2 `"Prakse"` | — | `UNVERIFIED` |
| 2.2 | `Tab` to topic filter & start practice item | `#prakse-runner-item-host` | Interactive response control (`Q01`–`Q18`) announces N22 `name`, `role`, and `state` | — | `UNVERIFIED` |
| 2.3 | Press `h` (outside text input) | `#hint-drawer` (`dialog`, `aria-modal="true"`) | Dialog `"Palīdzības kāpnes — pakāpeniska atsauce"`, focus on `#hint-drawer-close` (`button`, `"Aizvērt"`) | — | `UNVERIFIED` |
| 2.4 | `Tab` through `#hint-drawer` past last control | Next element outside `#hint-drawer` | Focus escapes drawer in document order (no focus trap) | — | `UNVERIFIED` |
| 2.5 | Press `Escape` while drawer open | Invoking hint button | Drawer closes; focus returns to exact invoking control | — | `UNVERIFIED` |
| 2.6 | Press `s` (outside text input) | `#prakse-skip-btn` (`button`, `"Izlaist uzdevumu"`) | Task skipped; `#sim-live-verdict` (`polite`) announces verdict/status once | — | `UNVERIFIED` |

### Scenario 3 — Full Graded Exam (`#eksamens`)
**Precondition:** Navigate to `#eksamens` via key `4`.

| Step | Key / Action | Target Element / Region | Expected Announcement (from N33 Name Table) | Observed | Status |
|---|---|---|---|---|---|
| 3.1 | Press `4` | `#eksamens-virsraksts` (`h2`, `tabindex="-1"`) | `#sim-live-view` (`polite`): `"Skats: Eksāmena simulācija"`, heading level 2 | — | `UNVERIFIED` |
| 3.2 | `Tab` to `#exam-start`, press `Enter` | `#exam-start` (`button`, `"Sākt treniņsesiju"`) | Exam shell opens; `#exam-slot-host` receives focus | — | `UNVERIFIED` |
| 3.3 | Focus numeric answer `<input>`, type `t` and `1` | Numeric `<input>` (`Q01`) | Characters `t`/`1` enter input (no topic/section jump); input-guard suppresses shortcuts | — | `UNVERIFIED` |
| 3.4 | `Tab` out of input, press `n` then `p` | `#exam-next` / `#exam-prev` | Advances to next / previous question; `#exam-slot-status` updates | — | `UNVERIFIED` |
| 3.5 | Press `f` | `#exam-flag` (`button`, `aria-pressed`) | Button `"Atzīmēt uzdevumu"`, `aria-pressed` toggles `"true"` / `"false"` | — | `UNVERIFIED` |
| 3.6 | Trigger timer threshold | `#sim-live-timer` (`alert`, `aria-live="assertive"`) | Assertive announcement fires **exactly once** for threshold | — | `UNVERIFIED` |
| 3.7 | Press `r`, `Tab` to submit, `Enter` | `#exam-review-button` (`button`, `"Pārbaude un iesniegšana"`) | Review screen opens; submission posts `#sim-live-verdict` (`polite`) once | — | `UNVERIFIED` |

### Scenario 4 — Revision Session with Self-Assessment (`#atskats`)
**Precondition:** Navigate to `#atskats` via key `6`.

| Step | Key / Action | Target Element / Region | Expected Announcement (from N33 Name Table) | Observed | Status |
|---|---|---|---|---|---|
| 4.1 | Press `6` | `#atskats-virsraksts` (`h2`, `tabindex="-1"`) | `#sim-live-view` (`polite`): `"Skats: Atskats un atkārtošana"`, heading level 2 | — | `UNVERIFIED` |
| 4.2 | Press `c` | `#atskats-revision-heading` (`h3`) | Focus moves to self-assessment criteria section | — | `UNVERIFIED` |
| 4.3 | `Tab` through criteria controls, toggle with `Space`/`Enter` | Revision self-assessment controls | Name, role, and checked/pressed state announced; `#sim-live-verdict` (`polite`) updates once | — | `UNVERIFIED` |

### Scenario 5 — Concept Drawer Round Trips (`#saturs`)
**Precondition:** Press `t` (topic jump) or `2` to enter `#saturs`.

| Step | Key / Action | Target Element / Region | Expected Announcement (from N33 Name Table) | Observed | Status |
|---|---|---|---|---|---|
| 5.1 | Press `t` | `#saturs-virsraksts` (`h2`, `tabindex="-1"`) | `#sim-live-view` (`polite`): `"Skats: Mācību mērķi un programmas pārklājums"` | — | `UNVERIFIED` |
| 5.2 | `Tab` to a concept map node, press `Enter` | `#concept-drawer` (`dialog`, `aria-modal="true"`) | Dialog `"Koncepta atvilktne"`, focus enters `#concept-drawer-close` (`button`, `"Aizvērt"`) | — | `UNVERIFIED` |
| 5.3 | `Tab` through all links/buttons inside `#concept-drawer` and past end | Next focusable element outside `#concept-drawer` | Focus walks in, through, and escapes out of `#concept-drawer` (no focus trap) | — | `UNVERIFIED` |
| 5.4 | Press `Escape` | Exact invoking concept node | `#concept-drawer` closes; focus restores to invoking concept node | — | `UNVERIFIED` |

---

## 4. Execution Recording Template

```text
Execution Date: YYYY-MM-DD
Executor: <name>
Environment: <OS / Browser / Screen Reader + Version>
Scenario ID: <1..5>
Step ID: <e.g. 3.3>
Expected: <from table above>
Observed: <verbatim speech / braille output>
Result: PASS | DEFECT (<defect-id>)
```
