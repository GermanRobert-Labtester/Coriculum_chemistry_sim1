# AGENTS.md — Chemistry_1st_coriculum

Purpose: prepare and later implement an independent offline Latvian first-colloquium practice simulator from the supplied 2025 programme. Student prompts are Latvian; implementation communication/planning may be English.

Read README.md, MASTER_WORKSPACE_AUDIT_AND_35_TASK_ROADMAP.md, COPY_MANIFEST.json and docs/PROGRAMME_COVERAGE_MATRIX.csv before authoring. Current status is material consolidation and planning; no simulator has been implemented.

Treat materials/, reference_plans/ and reference_governance/ as frozen reference snapshots. AGENTS.snapshot.md files describe their original source workspaces, not active contracts here. Preserve the programme PDF, its extracted text, manifests and source baseline evidence. Never write to sibling Chemistry_1–7 or run imported builders against their source directories. New implementation belongs to destination-owned data/, src/, tools/ and output/ paths described in the plan. Do not hand-edit imported masters to create the simulator.

The supplied programme establishes seven topics, a written-on-paper examination and a maximum 180 minutes. Point weights, question counts, pass marks, allowed aids and exact exam question types are not specified; label practice design choices. Chemistry_6 maps to programme Topic 6 despite its local Topic 13 label. Do not silently use all content in a master as assessable programme scope.

Use explicit percentage bases, units, reaction medium, constants and assumptions. Source conflicts remain visible. Separate machine-checked, self-assessed, human-reviewed and pending points; keyword matching is not semantic grading. Four variant specifications are not four finished questions. No official exam/grade or proctoring claim.

Implement semantic HTML/CSS and Python precomputation first; strict TypeScript handles necessary response/session logic. Keep the tool offline, with local assets, no CDN/network/analytics, and in-memory sessions by default. Set runtime budgets on measured new requirements rather than inheriting a chapter master’s historical widget cap.

Follow the parent visual policy: lite-shot with Falkon, inspect PNGs; do not use webshot or Chrome/Chromium without explicit user authorization. Blank captures or blocked X displays are UNVERIFIED. PDF page inspection may use Poppler rendering. Static checks do not establish visual, accessibility, print, scientific or instructor acceptance.

Run python3 tools/verify_preparation.py after preparation changes and before implementation intake. Keep verification evidence current and report exactly what ran. Future product gates are defined in the roadmap. Do not spawn subagents merely because the roadmap has independent workstreams.
