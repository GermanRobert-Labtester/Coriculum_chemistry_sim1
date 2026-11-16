# Pirmā kolokvija simulācijas darba telpa

Prepared 2026-11-16. Materials and implementation plan are ready. **The simulator itself has not been implemented.** This workspace uses the supplied 2025 programme and copies from Chemistry_1–7; the original workspaces are preserved.

Start with [the master implementation plan](MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md). It follows the individual workspaces’ 14-section, 20-core-task / 10-feature / 5-diagnostic structure. The [question-type and variant specification](docs/QUESTION_TYPES_AND_VARIANTS.md) describes 18 response types, 28 families with four variant specifications each, and 14 worked examples.

## Copied master materials

| Programme topic | Master |
|---|---|
| 1. Ievads, šķīdumi un ķīmiskās reakcijas | [Open HTML master](<materials/Chemistry_1/Master_temats_1_skidumi_un_kimiskas_reakcijas.html>) |
| 2. Aprēķini, mērījumi un grafiskās metodes | [Open HTML master](<materials/Chemistry_2/Master_2_tema_merijumi_un_grafiki.html>) |
| 3. Šķīdumi un koncentrāciju aprēķini | [Open HTML master](<materials/Chemistry_3/Master_3_tema_skidumi_un_koncentracijas.html>) |
| 4. Termodinamika | [Open HTML master](<materials/Chemistry_4/Master_4_temats_termodinamika.html>) |
| 5. Kinētika un katalīze | [Open HTML master](<materials/Chemistry_5/Master_5_tema_kinetika_un_katalize.html>) |
| 6. Oksidēšanās un reducēšanās | [Open HTML master](<materials/Chemistry_6/Master_oksidesanas_reducesanas_procesi.html>) |
| 7. Spektrofotometrija un analīzes metodes | [Open HTML master](<materials/Chemistry_7/Master_spektrofotometrija_SEM7_LD6B.html>) |

Chemistry_6’s local Topic 13 label maps to programme Topic 6 (redox). Chemistry_7 is programme Topic 7 (spectrophotometry), including its Lab 6B. The numbered folders represent source workspaces, not automatically the local topic/lab numbers.

## Programme and planning files

- [Original programme PDF](RSU_MedChem_Colloq1_Prog_LV_2025.pdf): seven topics, written-on-paper examination, maximum 180 minutes.
- [Coverage matrix](docs/PROGRAMME_COVERAGE_MATRIX.csv): programme outcomes → copied master anchors → planned families.
- [Proposed form blueprint](docs/SIMULATION_BLUEPRINT.json): three A/B/C forms, 21 tasks, 100 practice points, 170 working minutes + 10 review. Weights and formats are proposals.
- [Family specifications](docs/QUESTION_FAMILIES.json): 28 families × four authoring specifications; not 112 finished questions.
- [Worked example data](docs/EXAMPLE_QUESTIONS.json): 14 proposed questions with answers, rubrics and variants.
- [Proposed instance schema](docs/QUESTION_SCHEMA.json): contracts for future authoring.
- [Copy manifest](COPY_MANIFEST.json): 174 files and their original/destination paths, roles, sizes and SHA-256.
- [Inspection ledger](evidence/INSPECTION_LEDGER.md) and [preparation verification](evidence/PREPARATION_VERIFICATION.json).

## Snapshot boundaries

materials/Chemistry_n contains the canonical master, every top-level course PDF/DOCX and selected source/conflict/calculation records. reference_plans/Chemistry_n contains 18 master/deep/improvement plan references. reference_governance/Chemistry_n contains archived source AGENTS.snapshot.md, visual policies and five detailed governance shards. Those are reference records, not active instructions for this new workspace. Imported code is supporting evidence, not a complete executable generator checkout. Caches, node_modules, screenshots, backup masters and unrelated numbered workspaces were not copied.

The snapshot totals 30,083,827 bytes (about 28.7 MiB), including seven masters and 35 course documents. Identical documents are kept under their source topic names to preserve provenance. No new external chemistry research or browser validation was performed; historical source labels remain historical.

## Verify the preparation

From this directory: `python3 tools/verify_preparation.py --report evidence/PREPARATION_VERIFICATION.json`. This rechecks copy hashes, all preserved source-file hashes and inventory, plan structure, coverage anchors, type/family/variant records, blueprint totals and independently computed numerical examples. It does not run any copied generator. Future application, accessibility and print checks are separate roadmap gates.
