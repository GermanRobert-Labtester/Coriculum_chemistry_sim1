#!/usr/bin/env python3
"""N02/N03 build gate and single-file precursor assembly.

The gate registry declares the coverage check as order 1 (N02) and the
conventions check as order 2 (N03). The full N31 pipeline will extend this
registry; at N02/N03 the build emits a minimal, honest single-file shell that
embeds the #sim-coverage and #sim-conventions islands and their runtime loaders,
so both islands are proven in the artifact rather than only in data.

The build is deterministic: sorted keys, declared separators, UTF-8, no
timestamps in content, and the same source set produces byte-identical output.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from coverage_common import (  # noqa: E402
    COVERAGE_PATH, DEST, EXPECTED_PER_TOPIC, EXPECTED_TOTAL, canonical_json_bytes,
    escape_json_for_script, load_json, sha256_bytes, sha256_file,
)
from validate_coverage import format_summary as format_coverage_summary  # noqa: E402
from validate_coverage import validate as validate_coverage  # noqa: E402
from validate_conventions import format_summary as format_conventions_summary  # noqa: E402
from validate_conventions import validate as validate_conventions  # noqa: E402
from validate_bank import SCHEMA_PATH, _collect_bank_files  # noqa: E402
from validate_bank import format_summary as format_bank_summary  # noqa: E402
from validate_bank import validate_bank  # noqa: E402
import validate_bank_review  # noqa: E402
from validate_golden_vectors import GOLDEN_VECTORS_PATH, PROTOCOL_PATH, SEED_POLICY_PATH  # noqa: E402
from validate_golden_vectors import format_summary as format_golden_summary  # noqa: E402
from validate_golden_vectors import validate_all as validate_golden_vectors  # noqa: E402
from validate_tokens import STYLES_PATH, TOKENS_PATH, emit_tokens_css  # noqa: E402
from n34_noscript import render_noscript_html  # noqa: E402
from validate_tokens import format_summary as format_tokens_summary  # noqa: E402
from validate_tokens import validate_tokens  # noqa: E402
from validate_n06_shell import format_summary as format_shell_summary  # noqa: E402
from validate_n06_shell import validate_shell  # noqa: E402
from validate_n07_map import (  # noqa: E402
    REGISTRY_PATH, SUMMARIES_PATH, build_runtime_projections,
)
from validate_n07_map import format_summary as format_n07_summary  # noqa: E402
from validate_n07_map import validate_all as validate_n07_map  # noqa: E402
from validate_n08_layers import (  # noqa: E402
    N08_TERM_STUBS_PATH, RECALL_LAYERS_PATH,
    build_runtime_projection as build_n08_projection,
)
from validate_n08_layers import format_summary as format_n08_summary  # noqa: E402
from validate_n08_layers import validate_all as validate_n08_layers  # noqa: E402
from validate_terms import TERMS_PATH  # noqa: E402
from validate_terms import format_summary as format_terms_summary  # noqa: E402
from validate_terms import validate_all as validate_terms  # noqa: E402
from validate_figures import (  # noqa: E402
    CALIBRATION_CONTRACT_PATH, ENERGY_CONTRACT_PATH, FIGURES_T12_PATH, FIGURES_T23_PATH, FIGURES_T4_PATH,
    FIGURES_T5_PATH, FIGURES_T67_PATH, FIGURE_SCHEMA_PATH, KINETICS_CONTRACT_PATH, READING_CONTRACT_PATH,
    TITRATION_CONTRACT_PATH,
)
from validate_figures import format_summary as format_figures_summary  # noqa: E402
from validate_figures import validate_figures  # noqa: E402
from leak_scan import format_summary as format_leak_summary  # noqa: E402
from leak_scan import scan_figures_dataset  # noqa: E402
from validate_chains import (  # noqa: E402
    CHAINS_PATH, CHAIN_REFS_PATH, CHAIN_SCHEMA_PATH,
    build_runtime_projection, format_summary as format_chains_summary,
    validate_chains,
)
from validate_engines import (  # noqa: E402
    format_summary as format_engines_summary,
    validate as validate_engines,
)
from validate_graph_scoring import (  # noqa: E402
    CONTRACT_PATH as GRAPH_SCORING_CONTRACT_PATH,
    format_summary as format_graph_scoring_summary,
    validate as validate_graph_scoring,
)
from validate_method_cards import (  # noqa: E402
    CARDS_PATH as METHOD_CARDS_PATH,
    CONTRACT_PATH as METHOD_ENGINE_CONTRACT_PATH,
    build_runtime_projection as build_method_cards_projection,
    format_summary as format_method_cards_summary,
    validate as validate_method_cards,
)
import validate_n21_shell  # noqa: E402
import validate_n22_inputs  # noqa: E402
import assemble_forms  # noqa: E402
import validate_n24_assembly  # noqa: E402
import validate_n25_analytics  # noqa: E402
import validate_n26_mastery  # noqa: E402
import validate_n27_scheduler  # noqa: E402
import validate_n28_remediation  # noqa: E402
import validate_n29_revision  # noqa: E402
import validate_n30_practice  # noqa: E402
import validate_n31_build_policy  # noqa: E402
import check_artifact  # noqa: E402
import check_contrast  # noqa: E402
import check_a11y  # noqa: E402

# N23's validator is authored in parallel with this wiring. The import is guarded
# so that gates 1-18 still run and gate 19 fails with a named message instead of
# a raw ModuleNotFoundError while the sibling artifact is not in place.
try:  # pragma: no cover - the branch is an integration-state probe
    import validate_n23_grading  # noqa: E402
    N23_GRADING_IMPORT_ERROR = None
except ImportError as error:  # pragma: no cover
    validate_n23_grading = None
    N23_GRADING_IMPORT_ERROR = str(error)

CONVENTIONS_PATH = 'data/conventions.json'
N06_TERM_STUBS_PATH = 'data/n06_term_stubs.json'
SHELL_PATH = 'src/shell.html'
LOADER_PATH = 'src/coverage-loader.js'
VIEW_PATH = 'src/coverage-view.js'
CONVENTIONS_LOADER_PATH = 'src/conventions-loader.js'
BANK_LOADER_PATH = 'src/bank-loader.js'
PRNG_JS_PATH = 'src/prng.js'
VARIANT_ENGINE_JS_PATH = 'src/variant-engine.js'
VARIANT_TEMPLATES_JS_PATH = 'src/variant-templates.js'
BANK_DIR = 'data/bank'
FAMILY_TEMPLATE_DIR = 'data/family_templates'
GOLDEN_VECTORS_LOADER_PATH = 'src/golden-vectors-loader.js'
TERMS_LOADER_JS_PATH = 'src/terms-loader.js'
FIGURE_FRAMEWORK_JS_PATH = 'src/figure-framework.js'
CHAIN_VIEW_JS_PATH = 'src/chain-view.js'
ENGINE_TAXONOMY_PATH = 'data/engine_taxonomy.json'
GRAPH_SCORING_JS_PATH = 'src/graph-scoring-engine.js'
GRAPH_CAPTURE_JS_PATH = 'src/graph-capture.js'
ENGINE_JS_PATH = 'src/quantity-engine.js'
METHOD_ENGINE_JS_PATH = 'src/method-engine.js'
METHOD_CARD_VIEW_JS_PATH = 'src/method-card-view.js'
LEAK_SCAN_JS_PATH = 'src/leak-scan.js'
START_VIEW_JS_PATH = 'src/start-view.js'
CONCEPT_MAP_JS_PATH = 'src/concept-map.js'
CONCEPT_DRAWER_JS_PATH = 'src/concept-drawer.js'
HINT_DRAWER_JS_PATH = 'src/hint-drawer.js'
THEME_TOGGLE_JS_PATH = 'src/theme-toggle.js'
SMOKE_SUBSET_JS_PATH = 'src/smoke-subset.js'
EXAM_POLICY_PATH = 'data/exam_policy.json'
SESSION_TS_PATH = 'src/session.ts'
EXAM_TS_PATH = 'src/exam.ts'
SESSION_JS_PATH = 'src/compiled/session.js'
EXAM_JS_PATH = 'src/compiled/exam.js'
RESPONSE_TYPES_PATH = 'data/response_types.json'
INPUTS_REGISTRY_TS_PATH = 'src/inputs/registry.ts'
INPUTS_COMPONENTS_TS_PATH = 'src/inputs/components.ts'
INPUTS_INTEGRATION_TS_PATH = 'src/inputs/integration.ts'
INPUTS_REGISTRY_JS_PATH = 'src/compiled/inputs/registry.js'
INPUTS_COMPONENTS_JS_PATH = 'src/compiled/inputs/components.js'
INPUTS_INTEGRATION_JS_PATH = 'src/compiled/inputs/integration.js'
OUTPUT_PATH = 'output/simulator.html'
MANIFEST_PATH = 'output/build-manifest.json'
GRADING_POLICY_PATH = 'data/grading_policy.json'
FEEDBACK_CLASSIFICATION_PATH = 'data/feedback_classification.json'
GRADING_TS_PATH = 'src/grading.ts'
FEEDBACK_TS_PATH = 'src/feedback.ts'
GRADING_JS_PATH = 'src/compiled/grading.js'
FEEDBACK_JS_PATH = 'src/compiled/feedback.js'
ASSEMBLY_TS_PATH = 'src/assembly.ts'
ASSEMBLY_JS_PATH = 'src/compiled/assembly.js'
ANALYTICS_SCHEMA_PATH = 'data/analytics_schema.json'
STORE_TS_PATH = 'src/store.ts'
ANALYTICS_TS_PATH = 'src/analytics.ts'
STORE_JS_PATH = 'src/compiled/store.js'
ANALYTICS_JS_PATH = 'src/compiled/analytics.js'
MASTERY_POLICY_PATH = 'data/mastery_policy.json'
MASTERY_TS_PATH = 'src/mastery.ts'
MASTERY_JS_PATH = 'src/compiled/mastery.js'
SCHEDULER_POLICY_PATH = 'data/scheduler_policy.json'
SCHEDULER_TS_PATH = 'src/scheduler.ts'
SCHEDULER_JS_PATH = 'src/compiled/scheduler.js'
REMEDIATION_POLICY_PATH = 'data/remediation_policy.json'
REMEDIATION_TS_PATH = 'src/remediation.ts'
REMEDIATION_JS_PATH = 'src/compiled/remediation.js'
REVISION_POLICY_PATH = 'data/revision_policy.json'
REVISION_TS_PATH = 'src/revision.ts'
REVISION_JS_PATH = 'src/compiled/revision.js'
PRACTICE_POLICY_PATH = 'data/practice_policy.json'
PRACTICE_TS_PATH = 'src/practice.ts'
PRACTICE_JS_PATH = 'src/compiled/practice.js'
BUILD_POLICY_JSON_PATH = 'data/build_policy.json'
BUILD_POLICY = 'N31 idempotent single-file build pipeline (data/build_policy.json v1.0.0-n31): 22 canonical JSON islands + 4 JS data projections + 37 topologically ordered inlined runtime modules (with /* === MODULE: <path> === */ boundaries) + CSS/SVG layers + deterministic SHA-256 composite stamp + 28 build gates (coverage through artifact_contract)'
JSON_EMISSION = 'sorted keys; separators (",", ":"); ensure_ascii=False; UTF-8; "</" escaped as "<\\/" before embedding'


def coverage_gate(island_path: Path, repo_root: Path, masters_root: Path,
                  conventions_path: Path | None = None,
                  schema_path: Path | None = None,
                  bank_path: Path | None = None,
                  golden_vectors_path: Path | None = None,
                  tokens_path: Path | None = None,
                  styles_path: Path | None = None) -> dict:
    return validate_coverage(island_path=island_path, repo_root=repo_root, masters_root=masters_root)


def conventions_gate(island_path: Path, repo_root: Path, masters_root: Path,
                     conventions_path: Path | None = None,
                     schema_path: Path | None = None,
                     bank_path: Path | None = None,
                     golden_vectors_path: Path | None = None,
                     tokens_path: Path | None = None,
                     styles_path: Path | None = None) -> dict:
    target = conventions_path or (repo_root / CONVENTIONS_PATH)
    return validate_conventions(island_path=target, repo_root=repo_root)


def bank_gate(island_path: Path, repo_root: Path, masters_root: Path,
              conventions_path: Path | None = None,
              schema_path: Path | None = None,
              bank_path: Path | None = None,
              golden_vectors_path: Path | None = None,
              tokens_path: Path | None = None,
              styles_path: Path | None = None) -> dict:
    target_schema = schema_path or (repo_root / SCHEMA_PATH)
    return validate_bank(
        schema_path=target_schema,
        repo_root=repo_root,
        bank_path=bank_path,
        require_all_required_types=bank_path is not None,
    )


def golden_vectors_gate(island_path: Path, repo_root: Path, masters_root: Path,
                        conventions_path: Path | None = None,
                        schema_path: Path | None = None,
                        bank_path: Path | None = None,
                        golden_vectors_path: Path | None = None,
                        tokens_path: Path | None = None,
                        styles_path: Path | None = None) -> dict:
    return validate_golden_vectors(
        repo_root=repo_root,
        vectors_path=golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH),
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        schema_path=schema_path or (repo_root / SCHEMA_PATH),
    )


def tokens_gate(island_path: Path, repo_root: Path, masters_root: Path,
                conventions_path: Path | None = None,
                schema_path: Path | None = None,
                bank_path: Path | None = None,
                golden_vectors_path: Path | None = None,
                tokens_path: Path | None = None,
                styles_path: Path | None = None,
                summaries_path: Path | None = None,
                registry_path: Path | None = None) -> dict:
    return validate_tokens(
        tokens_path=tokens_path or (repo_root / TOKENS_PATH),
        styles_path=styles_path or (repo_root / STYLES_PATH),
        repo_root=repo_root,
    )


def wcag_contract_gate(island_path: Path, repo_root: Path, masters_root: Path,
                       conventions_path: Path | None = None,
                       schema_path: Path | None = None,
                       bank_path: Path | None = None,
                       golden_vectors_path: Path | None = None,
                       tokens_path: Path | None = None,
                       styles_path: Path | None = None,
                       summaries_path: Path | None = None,
                       registry_path: Path | None = None) -> dict:
    return check_contrast.validate_n32_contract(
        tokens_path=tokens_path or (repo_root / TOKENS_PATH),
        styles_path=styles_path or (repo_root / STYLES_PATH),
        repo_root=repo_root,
    )


def a11y_contract_gate(island_path: Path, repo_root: Path, masters_root: Path,
                       conventions_path: Path | None = None,
                       schema_path: Path | None = None,
                       bank_path: Path | None = None,
                       golden_vectors_path: Path | None = None,
                       tokens_path: Path | None = None,
                       styles_path: Path | None = None,
                       summaries_path: Path | None = None,
                       registry_path: Path | None = None) -> dict:
    rep = check_a11y.validate_n33_contract(
        repo_root=repo_root,
        html_path=repo_root / 'src' / 'shell.html',
    )
    if rep.get('status') != 'PASS':
        raise RuntimeError(check_a11y.format_summary(rep))
    return rep


def concept_map_gate(island_path: Path, repo_root: Path, masters_root: Path,
                     conventions_path: Path | None = None,
                     schema_path: Path | None = None,
                     bank_path: Path | None = None,
                     golden_vectors_path: Path | None = None,
                     tokens_path: Path | None = None,
                     styles_path: Path | None = None,
                     summaries_path: Path | None = None,
                     registry_path: Path | None = None) -> dict:
    return validate_n07_map(
        island_path=island_path,
        summaries_path=summaries_path or (repo_root / SUMMARIES_PATH),
        registry_path=registry_path or (repo_root / REGISTRY_PATH),
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        repo_root=repo_root,
        masters_root=masters_root,
    )


def recall_layers_gate(island_path: Path, repo_root: Path, masters_root: Path,
                       conventions_path: Path | None = None,
                       schema_path: Path | None = None,
                       bank_path: Path | None = None,
                       golden_vectors_path: Path | None = None,
                       tokens_path: Path | None = None,
                       styles_path: Path | None = None,
                       summaries_path: Path | None = None,
                       registry_path: Path | None = None,
                       layers_path: Path | None = None) -> dict:
    return validate_n08_layers(
        repo_root=repo_root,
        layers_path=layers_path or (repo_root / RECALL_LAYERS_PATH),
        coverage_path=island_path,
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        golden_vectors_path=golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH),
    )


def terminology_gate(island_path: Path, repo_root: Path, masters_root: Path,
                     conventions_path: Path | None = None,
                     schema_path: Path | None = None,
                     bank_path: Path | None = None,
                     golden_vectors_path: Path | None = None,
                     tokens_path: Path | None = None,
                     styles_path: Path | None = None,
                     summaries_path: Path | None = None,
                     registry_path: Path | None = None,
                     layers_path: Path | None = None,
                     terms_path: Path | None = None,
                     extra_data_paths: list[Path] | None = None) -> dict:
    return validate_terms(
        repo_root=repo_root,
        terms_path=terms_path or (repo_root / TERMS_PATH),
        coverage_path=island_path,
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        golden_vectors_path=golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH),
        extra_data_paths=extra_data_paths,
    )


def _resolve_figure_paths(
    repo_root: Path,
    figures_path: Path | None,
    figures_t23_path: Path | None,
    figures_t4_path: Path | None = None,
    figures_t5_path: Path | None = None,
    figures_t67_path: Path | None = None,
) -> list[Path]:
    if figures_path is not None:
        return [figures_path]
    paths = [repo_root / FIGURES_T12_PATH]
    t23 = figures_t23_path or (repo_root / FIGURES_T23_PATH)
    if t23.exists():
        paths.append(t23)
    t4 = figures_t4_path or (repo_root / FIGURES_T4_PATH)
    if t4.exists():
        paths.append(t4)
    t5 = figures_t5_path or (repo_root / FIGURES_T5_PATH)
    if t5.exists():
        paths.append(t5)
    t67 = figures_t67_path or (repo_root / FIGURES_T67_PATH)
    if t67.exists():
        paths.append(t67)
    return paths


def figures_gate(island_path: Path, repo_root: Path, masters_root: Path,
                 conventions_path: Path | None = None,
                 schema_path: Path | None = None,
                 bank_path: Path | None = None,
                 golden_vectors_path: Path | None = None,
                 tokens_path: Path | None = None,
                 styles_path: Path | None = None,
                 summaries_path: Path | None = None,
                 registry_path: Path | None = None,
                 layers_path: Path | None = None,
                 terms_path: Path | None = None,
                 extra_data_paths: list[Path] | None = None,
                 figures_path: Path | None = None,
                 figures_t23_path: Path | None = None,
                 figures_t4_path: Path | None = None,
                 figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None) -> dict:
    fig_paths = _resolve_figure_paths(repo_root, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path)
    return validate_figures(
        repo_root=repo_root,
        figures_paths=fig_paths,
        terms_path=terms_path or (repo_root / TERMS_PATH),
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        coverage_path=island_path,
        summaries_path=summaries_path or (repo_root / SUMMARIES_PATH),
        masters_root=masters_root,
    )


def figure_leak_scan_gate(island_path: Path, repo_root: Path, masters_root: Path,
                          conventions_path: Path | None = None,
                          schema_path: Path | None = None,
                          bank_path: Path | None = None,
                          golden_vectors_path: Path | None = None,
                          tokens_path: Path | None = None,
                          styles_path: Path | None = None,
                          summaries_path: Path | None = None,
                          registry_path: Path | None = None,
                          layers_path: Path | None = None,
                          terms_path: Path | None = None,
                          extra_data_paths: list[Path] | None = None,
                          figures_path: Path | None = None,
                          figures_t23_path: Path | None = None,
                          figures_t4_path: Path | None = None,
                 figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None) -> dict:
    fig_paths = _resolve_figure_paths(repo_root, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path)
    return scan_figures_dataset(
        repo_root=repo_root,
        figures_paths=fig_paths,
        terms_path=terms_path or (repo_root / TERMS_PATH),
        golden_vectors_path=golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH),
    )


def chains_gate(island_path: Path, repo_root: Path, masters_root: Path,
                conventions_path: Path | None = None,
                schema_path: Path | None = None,
                bank_path: Path | None = None,
                golden_vectors_path: Path | None = None,
                tokens_path: Path | None = None,
                styles_path: Path | None = None,
                summaries_path: Path | None = None,
                registry_path: Path | None = None,
                layers_path: Path | None = None,
                terms_path: Path | None = None,
                extra_data_paths: list[Path] | None = None,
                figures_path: Path | None = None,
                figures_t23_path: Path | None = None,
                figures_t4_path: Path | None = None,
                figures_t5_path: Path | None = None,
                figures_t67_path: Path | None = None,
                chains_path: Path | None = None) -> dict:
    fig_paths = _resolve_figure_paths(repo_root, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path)
    return validate_chains(
        repo_root=repo_root,
        chains_path=chains_path or (repo_root / CHAINS_PATH),
        schema_path=repo_root / CHAIN_SCHEMA_PATH,
        refs_path=repo_root / CHAIN_REFS_PATH,
        coverage_path=island_path,
        conventions_path=conventions_path or (repo_root / CONVENTIONS_PATH),
        summaries_path=summaries_path or (repo_root / SUMMARIES_PATH),
        figure_paths=fig_paths,
    )


def engines_gate(island_path: Path, repo_root: Path, masters_root: Path,
                 conventions_path: Path | None = None,
                 schema_path: Path | None = None,
                 bank_path: Path | None = None,
                 golden_vectors_path: Path | None = None,
                 tokens_path: Path | None = None,
                 styles_path: Path | None = None,
                 summaries_path: Path | None = None,
                 registry_path: Path | None = None,
                 layers_path: Path | None = None,
                 terms_path: Path | None = None,
                 extra_data_paths: list[Path] | None = None,
                 figures_path: Path | None = None,
                 figures_t23_path: Path | None = None,
                 figures_t4_path: Path | None = None,
                 figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None) -> dict:
    return validate_engines(repo_root=repo_root)


def graph_scoring_gate(island_path: Path, repo_root: Path, masters_root: Path,
                        conventions_path: Path | None = None,
                        schema_path: Path | None = None,
                        bank_path: Path | None = None,
                        golden_vectors_path: Path | None = None,
                        tokens_path: Path | None = None,
                        styles_path: Path | None = None,
                        summaries_path: Path | None = None,
                        registry_path: Path | None = None,
                        layers_path: Path | None = None,
                        terms_path: Path | None = None,
                        extra_data_paths: list[Path] | None = None,
                        figures_path: Path | None = None,
                        figures_t23_path: Path | None = None,
                        figures_t4_path: Path | None = None,
                        figures_t5_path: Path | None = None,
                        figures_t67_path: Path | None = None,
                        chains_path: Path | None = None) -> dict:
    return validate_graph_scoring(repo_root=repo_root)


def bank_review_gate(island_path: Path, repo_root: Path, masters_root: Path,
                     conventions_path: Path | None = None,
                     schema_path: Path | None = None,
                     bank_path: Path | None = None,
                     golden_vectors_path: Path | None = None,
                     tokens_path: Path | None = None,
                     styles_path: Path | None = None,
                     summaries_path: Path | None = None,
                     registry_path: Path | None = None,
                     layers_path: Path | None = None,
                     terms_path: Path | None = None,
                     extra_data_paths: list[Path] | None = None,
                     figures_path: Path | None = None,
                     figures_t23_path: Path | None = None,
                     figures_t4_path: Path | None = None,
                     figures_t5_path: Path | None = None,
                     figures_t67_path: Path | None = None,
                     chains_path: Path | None = None) -> dict:
    """N20: the practice bank must be reviewed before it can be frozen.

    The gate re-runs every mechanical check over the bank and refuses the
    build when an instance is not in the accepted review state. It reads the
    bank only; it never promotes anything, so a build cannot promote an
    instance that no review pass has accepted.
    """
    if bank_path is None:
        return {'status': 'FAIL',
                'errors': ['N20 bank review gate: uzdevumu banka nav norādīts (--bank).'],
                'violations': []}
    report = validate_bank_review.run_gate(repo_root, bank_path)
    return {
        'status': report['status'],
        'instances': report['instances'],
        'template_digest': report.get('template_digest'),
        'review_stages': report.get('review_stages'),
        'review_checks': report.get('review_checks'),
        'errors': [f"[{v.get('code')}] {v.get('question_id')}: {v.get('message')}"
                   for v in report.get('violations', [])],
        'violations': report.get('violations', []),
    }


def method_cards_gate(island_path: Path, repo_root: Path, masters_root: Path,
                       conventions_path: Path | None = None,
                       schema_path: Path | None = None,
                       bank_path: Path | None = None,
                       golden_vectors_path: Path | None = None,
                       tokens_path: Path | None = None,
                       styles_path: Path | None = None,
                       summaries_path: Path | None = None,
                       registry_path: Path | None = None,
                       layers_path: Path | None = None,
                       terms_path: Path | None = None,
                       extra_data_paths: list[Path] | None = None,
                       figures_path: Path | None = None,
                       figures_t23_path: Path | None = None,
                       figures_t4_path: Path | None = None,
                       figures_t5_path: Path | None = None,
                       figures_t67_path: Path | None = None,
                       chains_path: Path | None = None) -> dict:
    return validate_method_cards(repo_root=repo_root)


def exam_shell_gate(island_path: Path, repo_root: Path, masters_root: Path,
                    conventions_path: Path | None = None,
                    schema_path: Path | None = None,
                    bank_path: Path | None = None,
                    golden_vectors_path: Path | None = None,
                    tokens_path: Path | None = None,
                    styles_path: Path | None = None,
                    summaries_path: Path | None = None,
                    registry_path: Path | None = None,
                    layers_path: Path | None = None,
                    terms_path: Path | None = None,
                    extra_data_paths: list[Path] | None = None,
                    figures_path: Path | None = None,
                    figures_t23_path: Path | None = None,
                    figures_t4_path: Path | None = None,
                    figures_t5_path: Path | None = None,
                    figures_t67_path: Path | None = None,
                    chains_path: Path | None = None) -> dict:
    """N21: the exam session contract, the mode registry and the shell markup."""
    return validate_n21_shell.run_gate(repo_root=repo_root)


def response_inputs_gate(island_path: Path, repo_root: Path, masters_root: Path,
                         conventions_path: Path | None = None,
                         schema_path: Path | None = None,
                         bank_path: Path | None = None,
                         golden_vectors_path: Path | None = None,
                         tokens_path: Path | None = None,
                         styles_path: Path | None = None,
                         summaries_path: Path | None = None,
                         registry_path: Path | None = None,
                         layers_path: Path | None = None,
                         terms_path: Path | None = None,
                         extra_data_paths: list[Path] | None = None,
                         figures_path: Path | None = None,
                         figures_t23_path: Path | None = None,
                         figures_t4_path: Path | None = None,
                         figures_t5_path: Path | None = None,
                         figures_t67_path: Path | None = None,
                         chains_path: Path | None = None) -> dict:
    """N22: the response-type registry, the completion model and the input contracts."""
    return validate_n22_inputs.run_gate(repo_root=repo_root)


def grading_gate(island_path: Path, repo_root: Path, masters_root: Path,
                 conventions_path: Path | None = None,
                 schema_path: Path | None = None,
                 bank_path: Path | None = None,
                 golden_vectors_path: Path | None = None,
                 tokens_path: Path | None = None,
                 styles_path: Path | None = None,
                 summaries_path: Path | None = None,
                 registry_path: Path | None = None,
                 layers_path: Path | None = None,
                 terms_path: Path | None = None,
                 extra_data_paths: list[Path] | None = None,
                 figures_path: Path | None = None,
                 figures_t23_path: Path | None = None,
                 figures_t4_path: Path | None = None,
                 figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None) -> dict:
    """N23: the grading-policy island, the classification totality and the no-tolerance scan."""
    if validate_n23_grading is None:
        return {
            'status': 'FAIL',
            'errors': [
                'N23 grading gate: tools/validate_n23_grading.py nav pieejams ('
                + str(N23_GRADING_IMPORT_ERROR) + '). Šis validates ir N23 paralēli '
                'autora artefakts; bez tā 19. vārti nevar pārbaudīt ne '
                'data/grading_policy.json, ne data/feedback_classification.json. '
                'Būve tiek atteikta ar nosauktu iemeslu, nevis klusējot.'
            ],
            'violations': [],
        }
    return validate_n23_grading.run_gate(repo_root=repo_root)


def form_assembly_gate(island_path: Path, repo_root: Path, masters_root: Path,
                       conventions_path: Path | None = None,
                       schema_path: Path | None = None,
                       bank_path: Path | None = None,
                       golden_vectors_path: Path | None = None,
                       tokens_path: Path | None = None,
                       styles_path: Path | None = None) -> dict:
    """N24: deterministic A/B/C form assembly, independent checker and Python/JS parity."""
    return validate_n24_assembly.run_gate(repo_root=repo_root)


def analytics_gate(island_path: Path, repo_root: Path, masters_root: Path,
                   conventions_path: Path | None = None,
                   schema_path: Path | None = None,
                   bank_path: Path | None = None,
                   golden_vectors_path: Path | None = None,
                   tokens_path: Path | None = None,
                   styles_path: Path | None = None) -> dict:
    """N25: versioned opt-in local store, analytics schema, F10 boundary and no-network scan."""
    return validate_n25_analytics.run_gate(repo_root=repo_root)


def mastery_gate(island_path: Path, repo_root: Path, masters_root: Path,
                 conventions_path: Path | None = None,
                 schema_path: Path | None = None,
                 bank_path: Path | None = None,
                 golden_vectors_path: Path | None = None,
                 tokens_path: Path | None = None,
                 styles_path: Path | None = None) -> dict:
    """N26: mastery policy reachability, criterion mapping totality, TS parity and shell touchpoints."""
    return validate_n26_mastery.run_gate(repo_root=repo_root)


def scheduler_gate(island_path: Path, repo_root: Path, masters_root: Path,
                   conventions_path: Path | None = None,
                   schema_path: Path | None = None,
                   bank_path: Path | None = None,
                   golden_vectors_path: Path | None = None,
                   tokens_path: Path | None = None,
                   styles_path: Path | None = None) -> dict:
    """N27: Leitner scheduler box-interval monotonicity, N10 term lint, TS parity and shell touchpoints."""
    return validate_n27_scheduler.run_gate(repo_root=repo_root)


def remediation_gate(island_path: Path, repo_root: Path, masters_root: Path,
                     conventions_path: Path | None = None,
                     schema_path: Path | None = None,
                     bank_path: Path | None = None,
                     golden_vectors_path: Path | None = None,
                     tokens_path: Path | None = None,
                     styles_path: Path | None = None) -> dict:
    """N28: remediation policy, link integrity, N10 term lint, TS parity and shell touchpoints."""
    return validate_n28_remediation.run_gate(repo_root=repo_root)


def revision_gate(island_path: Path, repo_root: Path, masters_root: Path,
                  conventions_path: Path | None = None,
                  schema_path: Path | None = None,
                  bank_path: Path | None = None,
                  golden_vectors_path: Path | None = None,
                  tokens_path: Path | None = None,
                  styles_path: Path | None = None) -> dict:
    """N29: revision policy, F07 self-assessment contract, single-sourced criteria, N10 term lint and TS parity."""
    return validate_n29_revision.run_gate(repo_root=repo_root)


def practice_gate(island_path: Path, repo_root: Path, masters_root: Path,
                  conventions_path: Path | None = None,
                  schema_path: Path | None = None,
                  bank_path: Path | None = None,
                  golden_vectors_path: Path | None = None,
                  tokens_path: Path | None = None,
                  styles_path: Path | None = None) -> dict:
    """N30: bounded practice path policy vs N20 live counts, 18-type filter lint, N10 terms, TS parity and shell touchpoints."""
    return validate_n30_practice.validate_all(repo_root=repo_root)


def build_policy_gate(island_path: Path, repo_root: Path, masters_root: Path,
                      conventions_path: Path | None = None,
                      schema_path: Path | None = None,
                      bank_path: Path | None = None,
                      golden_vectors_path: Path | None = None,
                      tokens_path: Path | None = None,
                      styles_path: Path | None = None) -> dict:
    """N31: build policy artifact, forward module dependency order, skeleton insertion points, and deterministic stamp fixtures."""
    return validate_n31_build_policy.validate_all(repo_root=repo_root)


# The registry order is the build order. Coverage is the first gate (N02);
# conventions is the second (N03); bank is the third (N04); golden_vectors is
# the fourth (N05); tokens is the fifth (N06); concept_map is the seventh (N07,
# after post-assembly n06_shell order 6 in build); recall_layers is the eighth
# (N08); terminology is the ninth (N10); figures is the tenth (N11);
# figure_leak_scan is the eleventh (N12); chains is the twelfth (N16) and
# engines the thirteenth (N17).
GATES = [
    {'order': 1, 'id': 'coverage', 'owner': 'N02', 'check': coverage_gate},
    {'order': 2, 'id': 'conventions', 'owner': 'N03', 'check': conventions_gate},
    {'order': 3, 'id': 'bank', 'owner': 'N04', 'check': bank_gate},
    {'order': 4, 'id': 'golden_vectors', 'owner': 'N05', 'check': golden_vectors_gate},
    {'order': 5, 'id': 'tokens', 'owner': 'N06', 'check': tokens_gate},
    {'order': 7, 'id': 'concept_map', 'owner': 'N07', 'check': concept_map_gate},
    {'order': 8, 'id': 'recall_layers', 'owner': 'N08', 'check': recall_layers_gate},
    {'order': 9, 'id': 'terminology', 'owner': 'N10', 'check': terminology_gate},
    {'order': 10, 'id': 'figures', 'owner': 'N11', 'check': figures_gate},
    {'order': 11, 'id': 'figure_leak_scan', 'owner': 'N12', 'check': figure_leak_scan_gate},
    {'order': 12, 'id': 'chains', 'owner': 'N16', 'check': chains_gate},
    {'order': 13, 'id': 'engines', 'owner': 'N17', 'check': engines_gate},
    {'order': 14, 'id': 'graph_scoring', 'owner': 'N18', 'check': graph_scoring_gate},
    {'order': 15, 'id': 'method_cards', 'owner': 'N19', 'check': method_cards_gate},
    {'order': 16, 'id': 'bank_review', 'owner': 'N20', 'check': bank_review_gate},
    {'order': 17, 'id': 'exam_shell', 'owner': 'N21', 'check': exam_shell_gate},
    {'order': 18, 'id': 'response_inputs', 'owner': 'N22', 'check': response_inputs_gate},
    {'order': 19, 'id': 'grading', 'owner': 'N23', 'check': grading_gate},
    {'order': 20, 'id': 'form_assembly', 'owner': 'N24', 'check': form_assembly_gate},
    {'order': 21, 'id': 'analytics', 'owner': 'N25', 'check': analytics_gate},
    {'order': 22, 'id': 'mastery', 'owner': 'N26', 'check': mastery_gate},
    {'order': 23, 'id': 'scheduler', 'owner': 'N27', 'check': scheduler_gate},
    {'order': 24, 'id': 'remediation', 'owner': 'N28', 'check': remediation_gate},
    {'order': 25, 'id': 'revision', 'owner': 'N29', 'check': revision_gate},
    {'order': 26, 'id': 'practice', 'owner': 'N30', 'check': practice_gate},
    {'order': 27, 'id': 'build_policy', 'owner': 'N31', 'check': build_policy_gate},
    {'order': 29, 'id': 'wcag_contract', 'owner': 'N32', 'check': wcag_contract_gate},
    {'order': 30, 'id': 'a11y_contract', 'owner': 'N33', 'check': a11y_contract_gate},
]


def _replace_once(text: str, placeholder: str, value: str) -> str:
    count = text.count(placeholder)
    if count != 1:
        raise SystemExit(f'Build template insertion point {placeholder} occurs {count} times; expected exactly once')
    return text.replace(placeholder, value)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.', suffix='.tmp', delete=False)
    temporary = Path(handle.name)
    try:
        with handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _source_record(repo_root: Path, relative: str) -> dict:
    path = repo_root / relative
    return {'path': relative, 'sha256': sha256_file(path), 'bytes': path.stat().st_size}


def _required_source_record(repo_root: Path, relative: str, owner: str) -> dict:
    """A source record for a file the passed gate proves must exist.

    A missing file is a named build refusal, not a traceback: the N23 grading
    modules ship from src/, so an absent compiled module means the compile step
    was skipped, and the message says so.
    """
    path = repo_root / relative
    if not path.exists():
        raise SystemExit(
            f'Build input {relative} is missing ({owner}). The N23 grading layer ships '
            f'from src/; run "python3 tools/compile_n21_ts.py" and commit the compiled '
            f'modules before building. Refusing build.'
        )
    return _source_record(repo_root, relative)


def _required_json(repo_root: Path, relative: str, island_id: str) -> dict:
    """Load a required JSON island; a missing file is a named build refusal."""
    path = repo_root / relative
    if not path.exists():
        raise SystemExit(
            f'Build island {relative} is missing. N23 inlines it as "#{island_id}"; '
            f'gate 19 (grading) refuses the build without it. Refusing build.'
        )
    return load_json(path)


def _format_gate_summary(gate_id: str, report: dict) -> str:
    if gate_id == 'coverage':
        raw = format_coverage_summary(report).splitlines()[0]
    elif gate_id == 'conventions':
        raw = format_conventions_summary(report)
    elif gate_id == 'bank':
        raw = format_bank_summary(report)
    elif gate_id == 'bank_review':
        raw = (f"N20 bank review: {report.get('instances', 0)} instances, "
               f"{len(report.get('violations') or [])} review violations")
    elif gate_id == 'exam_shell':
        contract = report.get('contract') or {}
        alignment = report.get('blueprint_alignment') or {}
        raw = (f"N21 exam shell: {contract.get('transition_count', 0)} session transitions, "
               f"{alignment.get('slot_count', 0)} slots, {alignment.get('points_total', 0)} points, "
               f"advisory limit {alignment.get('advisory_limit_seconds', 0)}s")
    elif gate_id == 'response_inputs':
        island = report.get('island') or {}
        raw = (f"N22 response inputs: {report.get('type_count', 0)} response types, "
               f"{len(report.get('completed_types') or [])} completed types, "
               f"{island.get('bytes', 0)} island bytes")
    elif gate_id == 'grading':
        summary = report.get('summary_lv') or report.get('summary')
        if isinstance(summary, str) and summary:
            raw = 'N23 grading: ' + summary
        else:
            islands = report.get('islands') or {}
            policy = islands.get('policy') or {}
            classification = islands.get('classification') or {}
            forms = report.get('score_forms') or {}
            raw = (f"N23 grading: {len(report.get('frozen_verdict_classes') or [])} verdict classes, "
                   f"{len(forms)} score forms, {policy.get('bytes', 0)} policy-island bytes, "
                   f"{classification.get('rows', 0)} classification rows")
    elif gate_id == 'form_assembly':
        forms_map = report.get('forms') or {}
        raw = (f"N24 form_assembly: {len(forms_map)} forms (21 slots, 100 pts each), "
               f"{report.get('forms_island_bytes', 0)} island bytes, parity={report.get('js_parity', {}).get('status')}")
    elif gate_id == 'analytics':
        schema_info = report.get('schema') or {}
        shell_info = report.get('shell') or {}
        raw = (f"N25 analytics: schema v{schema_info.get('schema_version', 2)} ({schema_info.get('bytes', 0)}B), "
               f"touchpoints {shell_info.get('required_ids_present', 0)}/{shell_info.get('required_ids_total', 0)}, "
               f"ts_drift={report.get('ts_drift')}")
    elif gate_id == 'mastery':
        pol_info = report.get('policy') or {}
        map_info = report.get('criterion_mapping') or {}
        shell_info = report.get('shell') or {}
        raw = (f"N26 mastery: {len(pol_info.get('states') or [])} states ({pol_info.get('bytes', 0)}B), "
               f"criteria={map_info.get('criteria_count', 0)}, "
               f"touchpoints {shell_info.get('required_ids_present', 0)}/{shell_info.get('required_ids_total', 0)}, "
               f"ts_drift={report.get('ts_drift')}")
    elif gate_id == 'scheduler':
        pol_info = report.get('policy') or {}
        shell_info = report.get('shell') or {}
        raw = (f"N27 scheduler: {len(pol_info.get('boxes') or [])} boxes, cap={pol_info.get('queue_cap', 0)} "
               f"({pol_info.get('bytes', 0)}B), terms={report.get('terms_lint', {}).get('status')}, "
               f"touchpoints {shell_info.get('required_ids_present', 0)}/{shell_info.get('required_ids_total', 0)}, "
               f"ts_drift={report.get('ts_drift')}")
    elif gate_id == 'remediation':
        pol_info = report.get('policy') or {}
        shell_info = report.get('shell') or {}
        raw = (f"N28 remediation: mode={pol_info.get('resolution_mode')}, "
               f"recommend_only={pol_info.get('recommend_only')} ({pol_info.get('bytes', 0)}B), "
               f"terms={report.get('terms_lint', {}).get('status')}, "
               f"touchpoints {shell_info.get('required_ids_present', 0)}/{shell_info.get('required_ids_total', 0)}, "
               f"ts_drift={report.get('ts_drift')}")
    elif gate_id == 'practice':
        raw = validate_n30_practice.format_summary(report)
    elif gate_id == 'build_policy':
        raw = validate_n31_build_policy.format_summary(report)
    elif gate_id == 'artifact_contract':
        raw = check_artifact.format_summary(report)
    elif gate_id == 'wcag_contract':
        raw = check_contrast.format_summary(report)
    elif gate_id == 'a11y_contract':
        raw = check_a11y.format_summary(report)
    elif gate_id == 'golden_vectors':
        raw = format_golden_summary(report)
    elif gate_id == 'tokens':
        raw = format_tokens_summary(report)
    elif gate_id == 'n06_shell':
        raw = format_shell_summary(report)
    elif gate_id == 'concept_map':
        raw = format_n07_summary(report)
    elif gate_id == 'recall_layers':
        raw = format_n08_summary(report)
    elif gate_id == 'terminology':
        raw = format_terms_summary(report)
    elif gate_id == 'figures':
        raw = format_figures_summary(report)
    elif gate_id == 'chains':
        return format_chains_summary(report)
    elif gate_id == 'graph_scoring':
        return format_graph_scoring_summary(report)
    elif gate_id == 'engines':
        return format_engines_summary(report)
    elif gate_id == 'figure_leak_scan':
        raw = format_leak_summary(report)
    else:
        raw = report.get('status', 'FAIL')
    # Keep build-manifest.json deterministic across builds (no wall-clock timings).
    return re.sub(r'\s*\(\d+(?:\.\d+)?\s*ms\)$', '', raw)


def _first_gate_error(report: dict) -> str:
    errors = report.get('errors') or []
    if errors:
        return errors[0]
    violations = report.get('violations') or []
    if violations:
        v = violations[0]
        return f'[{v.get("level")}] {v.get("file")} ({v.get("question_id")}) {v.get("field")}: {v.get("message")}'
    return 'unknown failure'


BANK_PROJECTION_DROPPED = ('draws', 'derived', 'review_workflow')


def _project_bank_instance(instance: dict) -> dict:
    """The runtime projection of one frozen bank instance.

    The island carries everything a renderer, a grader or an analytics
    consumer needs: the identity, the seed, the stem, the payload, the
    rubric, the givens, the review state and the engine metadata. The
    per-instance *audit tables* — the drawn values, the derived values and
    the review workflow record — are the audit trail, not runtime data: they
    live in the frozen bank files (``data/bank/*.json``) and in the N20
    evidence records, and the artifact has no byte room for them inside the
    Section 1.3 budget (700–1400 KiB total, 200–420 KiB for the bank).

    The projection is deterministic, so the island digest is a stable
    reference; the digest over the frozen bank files is recorded next to it.
    """
    projected = copy.deepcopy(instance)
    data = projected.get('extensions', {}).get('data')
    if isinstance(data, dict):
        for key in BANK_PROJECTION_DROPPED:
            data.pop(key, None)
    return projected


def _load_bank_island(bank_path: Path | None) -> dict:
    if bank_path is None:
        return {
            'island_id': 'sim-bank',
            'schema_version': 1,
            'bank_version': '0.0.0-pre-N20',
            'status': 'pre-N20-schema-only',
            'questions': [],
        }
    questions: list[dict] = []
    for file_path in _collect_bank_files(bank_path):
        raw = load_json(file_path)
        if isinstance(raw, dict) and isinstance(raw.get('questions'), list):
            questions.extend(raw['questions'])
        elif isinstance(raw, list):
            questions.extend(raw)
        elif isinstance(raw, dict):
            questions.append(raw)
    return {
        'island_id': 'sim-bank',
        'schema_version': 1,
        'bank_version': '1.0.0-n20',
        'status': 'frozen-reviewed-bank',
        'questions': [_project_bank_instance(question) for question in questions],
    }


def _bank_source_digest(bank_path: Path | None) -> str | None:
    """SHA-256 over the frozen bank files, in family order.

    This is the digest of the *authored* bank. It is the reference for
    "any bank change is a new digest and a deliberate act"; the island digest
    covers the runtime projection that the artifact embeds.
    """
    if bank_path is None:
        return None
    digest = hashlib.sha256()
    for path in sorted(Path(bank_path).glob('*.json')):
        digest.update(path.read_bytes())
    return digest.hexdigest()


def run_gates(island_path: Path, repo_root: Path, masters_root: Path,
              conventions_path: Path | None = None,
              schema_path: Path | None = None,
              bank_path: Path | None = None,
              golden_vectors_path: Path | None = None,
              tokens_path: Path | None = None,
              styles_path: Path | None = None,
              summaries_path: Path | None = None,
              registry_path: Path | None = None,
              layers_path: Path | None = None,
              terms_path: Path | None = None,
              extra_data_paths: list[Path] | None = None,
              figures_path: Path | None = None,
              figures_t23_path: Path | None = None,
              figures_t4_path: Path | None = None,
              figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None,
                 skip_gate_ids: set[str] | None = None) -> tuple[list[dict], dict[str, dict]]:
    gate_records: list[dict] = []
    reports: dict[str, dict] = {}
    for gate in GATES:
        if skip_gate_ids and gate['id'] in skip_gate_ids:
            continue
        if gate['id'] == 'concept_map':
            report = gate['check'](
                island_path, repo_root, masters_root,
                conventions_path, schema_path, bank_path, golden_vectors_path,
                tokens_path, styles_path, summaries_path, registry_path,
            )
        elif gate['id'] == 'recall_layers':
            report = gate['check'](
                island_path, repo_root, masters_root,
                conventions_path, schema_path, bank_path, golden_vectors_path,
                tokens_path, styles_path, summaries_path, registry_path, layers_path,
            )
        elif gate['id'] == 'terminology':
            report = gate['check'](
                island_path, repo_root, masters_root,
                conventions_path, schema_path, bank_path, golden_vectors_path,
                tokens_path, styles_path, summaries_path, registry_path, layers_path,
                terms_path, extra_data_paths,
            )
        elif gate['id'] in ('figures', 'figure_leak_scan', 'chains'):
            report = gate['check'](
                island_path, repo_root, masters_root,
                conventions_path, schema_path, bank_path, golden_vectors_path,
                tokens_path, styles_path, summaries_path, registry_path, layers_path,
                terms_path, extra_data_paths, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path, chains_path,
            )
        else:
            report = gate['check'](
                island_path, repo_root, masters_root,
                conventions_path, schema_path, bank_path, golden_vectors_path,
                tokens_path, styles_path,
            )
        status = report.get('status', 'FAIL')
        summary = _format_gate_summary(gate['id'], report)
        gate_records.append({
            'order': gate['order'],
            'id': gate['id'],
            'owner': gate['owner'],
            'status': status,
            'summary': summary,
        })
        reports[gate['id']] = report
        if status != 'PASS':
            first = _first_gate_error(report)
            print(f'FAIL {gate["id"]} gate (order {gate["order"]}, owner {gate["owner"]}): {first}', file=sys.stderr)
            for error in report.get('errors', [])[1:]:
                print(f'  - {error}', file=sys.stderr)
            for v in report.get('violations', [])[1:10]:
                print(f'  - [{v.get("level")}] {v.get("file")} ({v.get("question_id")}) {v.get("field")}: {v.get("message")}', file=sys.stderr)
            print('Refusing build. The artifact was not written.', file=sys.stderr)
            return gate_records, reports
    return gate_records, reports


def compact_js_source(text: str) -> str:
    """Conservative JS compaction: drop blank lines, full-line // comments and
    own-line /* … */ block comments, strip per-line indentation, keep line
    breaks (ASI safety). The N20 runtime budget needs the freed bytes; no
    source line is reordered or joined.

    A block comment is only removed when no line inside it contains a quote or
    a backtick, so a ``/*`` that lives inside a string literal is never
    mistaken for a comment start.
    """
    lines = text.splitlines()
    kept: list[str] = []
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith('/* === MODULE: ') or stripped.startswith('/* === BOOTSTRAP: '):
            kept.append(stripped)
            index += 1
            continue
        if stripped.startswith('/*'):
            if stripped.endswith('*/') and stripped.count('/*') == 1 and not any(ch in stripped for ch in "'\"`"):
                index += 1
                continue
            block: list[str] = []
            cursor = index
            while cursor < len(lines):
                block.append(lines[cursor])
                if cursor > index and '*/' in lines[cursor]:
                    break
                cursor += 1
            body = '\n'.join(block)
            if cursor < len(lines) and not any(ch in body for ch in "'\"`"):
                index = cursor + 1
                continue
        if not stripped or stripped.startswith('//'):
            index += 1
            continue
        kept.append(stripped)
        index += 1
    return '\n'.join(kept)


def compact_shell_inline_script(document: str) -> str:
    match = re.search(r'<script>([\s\S]*?)</script>', document)
    if not match:
        return document
    return document[:match.start(1)] + compact_js_source(match.group(1)) + document[match.end(1):]


def build(island_path: Path, repo_root: Path, masters_root: Path,
          output_path: Path, manifest_path: Path,
          conventions_path: Path | None = None,
          schema_path: Path | None = None,
          bank_path: Path | None = None,
          golden_vectors_path: Path | None = None,
          tokens_path: Path | None = None,
          styles_path: Path | None = None,
          summaries_path: Path | None = None,
          registry_path: Path | None = None,
          layers_path: Path | None = None,
          terms_path: Path | None = None,
          extra_data_paths: list[Path] | None = None,
          figures_path: Path | None = None,
          figures_t23_path: Path | None = None,
          figures_t4_path: Path | None = None,
          figures_t5_path: Path | None = None,
                 figures_t67_path: Path | None = None,
                 chains_path: Path | None = None) -> dict:
    gate_records, reports = run_gates(
        island_path, repo_root, masters_root,
        conventions_path, schema_path, bank_path, golden_vectors_path,
        tokens_path, styles_path, summaries_path, registry_path, layers_path,
        terms_path, extra_data_paths, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path, chains_path,
        skip_gate_ids={'form_assembly'},
    )
    if any(record['status'] != 'PASS' for record in gate_records) or len(gate_records) != len(GATES) - 1:
        raise SystemExit(1)

    island = load_json(island_path)
    island_bytes = canonical_json_bytes(island)
    island_text = escape_json_for_script(island_bytes.decode('utf-8'))
    invariants = {
        'total': EXPECTED_TOTAL,
        'perTopic': {str(t): EXPECTED_PER_TOPIC[t] for t in range(1, 8)},
    }
    invariants_text = canonical_json_bytes(invariants).decode('utf-8')

    conventions_file = conventions_path or (repo_root / CONVENTIONS_PATH)
    conventions = load_json(conventions_file)
    conventions_bytes = canonical_json_bytes(conventions)
    conventions_text = escape_json_for_script(conventions_bytes.decode('utf-8'))

    schema_file = schema_path or (repo_root / SCHEMA_PATH)
    bank_island = _load_bank_island(bank_path)
    bank_bytes = canonical_json_bytes(bank_island)
    bank_text = escape_json_for_script(bank_bytes.decode('utf-8'))
    bank_digest = sha256_bytes(bank_bytes)
    # The runtime integrity check digests the island *as embedded*, so the
    # artifact carries the digest of the escaped text that the browser sees.
    bank_embedded_digest = sha256_bytes(bank_text.encode('utf-8'))

    # N24 pipeline order: bank verified first (gates 3 and 16), then assembly,
    # then #sim-forms island generation.
    bank_verified = (
        reports.get('bank', {}).get('status') == 'PASS'
        and reports.get('bank_review', {}).get('status') == 'PASS'
    )
    forms_island = assemble_forms.assemble_frozen_forms(
        bank_island=bank_island,
        bank_digest=bank_digest,
        bank_embedded_digest=bank_embedded_digest,
        bank_verified=bank_verified,
        repo_root=repo_root,
    )
    forms_report = validate_n24_assembly.validate_assembled_island(
        forms_island=forms_island,
        bank_questions=bank_island['questions'],
        bank_digest=bank_digest,
        repo_root=repo_root,
    )
    gate_records = [g for g in gate_records if g['id'] != 'form_assembly']
    gate_records.append({
        'order': 20,
        'id': 'form_assembly',
        'owner': 'N24',
        'status': forms_report['status'],
        'summary': _format_gate_summary('form_assembly', forms_report),
    })
    reports['form_assembly'] = forms_report
    if forms_report['status'] != 'PASS':
        first = _first_gate_error(forms_report)
        print(f'FAIL form_assembly gate (order 20, owner N24): {first}', file=sys.stderr)
        for error in forms_report.get('errors', [])[1:]:
            print(f'  - {error}', file=sys.stderr)
        print('Refusing build. The artifact was not written.', file=sys.stderr)
        raise SystemExit(1)
    forms_bytes = canonical_json_bytes(forms_island)
    forms_digest = sha256_bytes(forms_bytes)
    forms_text = escape_json_for_script(forms_bytes.decode('utf-8'))

    golden_file = golden_vectors_path or (repo_root / GOLDEN_VECTORS_PATH)
    golden_island = load_json(golden_file)
    golden_bytes = canonical_json_bytes(golden_island)
    golden_text = escape_json_for_script(golden_bytes.decode('utf-8'))

    tokens_file = tokens_path or (repo_root / TOKENS_PATH)
    tokens_data = load_json(tokens_file)
    tokens_bytes = canonical_json_bytes(tokens_data)
    tokens_digest = sha256_bytes(tokens_bytes)
    tokens_css = emit_tokens_css(tokens_data)
    styles_file = styles_path or (repo_root / STYLES_PATH)
    styles_css = styles_file.read_text(encoding='utf-8')

    summaries_file = summaries_path or (repo_root / SUMMARIES_PATH)
    summaries_data = load_json(summaries_file)
    summaries_bytes = canonical_json_bytes(summaries_data)
    summaries_digest = sha256_bytes(summaries_bytes)

    registry_file = registry_path or (repo_root / REGISTRY_PATH)
    registry_data = load_json(registry_file)
    registry_bytes = canonical_json_bytes(registry_data)
    registry_digest = sha256_bytes(registry_bytes)

    compact_summaries, compact_registry = build_runtime_projections(summaries_data, registry_data)
    compact_summaries_bytes = canonical_json_bytes(compact_summaries)
    compact_summaries_text = escape_json_for_script(compact_summaries_bytes.decode('utf-8'))
    compact_registry_bytes = canonical_json_bytes(compact_registry)
    compact_registry_text = escape_json_for_script(compact_registry_bytes.decode('utf-8'))

    layers_file = layers_path or (repo_root / RECALL_LAYERS_PATH)
    layers_data = load_json(layers_file)
    layers_bytes = canonical_json_bytes(layers_data)
    layers_digest = sha256_bytes(layers_bytes)
    compact_layers = build_n08_projection(layers_data)
    compact_layers_bytes = canonical_json_bytes(compact_layers)
    compact_layers_text = escape_json_for_script(compact_layers_bytes.decode('utf-8'))

    terms_file = terms_path or (repo_root / TERMS_PATH)
    terms_data = load_json(terms_file)
    terms_bytes = canonical_json_bytes(terms_data)
    terms_digest = sha256_bytes(terms_bytes)
    terms_text = escape_json_for_script(terms_bytes.decode('utf-8'))

    fig_paths = _resolve_figure_paths(repo_root, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path)
    if len(fig_paths) == 1:
        figures_data = load_json(fig_paths[0])
    else:
        merged_figs = []
        for fp in fig_paths:
            merged_figs.extend(load_json(fp).get('figures', []))
        figures_data = {
            'schema_version': 1,
            'format_version': 1,
            'island_id': 'sim-figures',
            'status': 'authored',
            'owner': 'N11+N12+N13+N14+N15',
            'figures': merged_figs,
        }
    figures_bytes = canonical_json_bytes(figures_data)
    figures_digest = sha256_bytes(figures_bytes)
    figures_text = escape_json_for_script(figures_bytes.decode('utf-8'))
    chains_file = chains_path or (repo_root / CHAINS_PATH)
    chains_data = load_json(chains_file)
    chains_projection = build_runtime_projection(chains_data)
    chains_bytes = canonical_json_bytes(chains_projection)
    chains_digest = sha256_bytes(chains_bytes)
    chains_text = escape_json_for_script(chains_bytes.decode('utf-8'))
    engines_file = repo_root / ENGINE_TAXONOMY_PATH
    engines_data = load_json(engines_file)
    engines_bytes = canonical_json_bytes(engines_data)
    engines_digest = sha256_bytes(engines_bytes)
    engines_text = escape_json_for_script(engines_bytes.decode('utf-8'))
    graph_scoring_file = repo_root / GRAPH_SCORING_CONTRACT_PATH
    graph_scoring_data = load_json(graph_scoring_file)
    graph_scoring_bytes = canonical_json_bytes(graph_scoring_data)
    graph_scoring_digest = sha256_bytes(graph_scoring_bytes)
    graph_scoring_text = escape_json_for_script(graph_scoring_bytes.decode('utf-8'))
    method_cards_file = repo_root / METHOD_CARDS_PATH
    method_cards_data = load_json(method_cards_file)
    method_cards_projection = build_method_cards_projection(method_cards_data)
    method_cards_bytes = canonical_json_bytes(method_cards_projection)
    method_cards_digest = sha256_bytes(method_cards_bytes)
    method_cards_text = escape_json_for_script(method_cards_bytes.decode('utf-8'))
    method_engine_file = repo_root / METHOD_ENGINE_CONTRACT_PATH
    method_engine_data = load_json(method_engine_file)
    method_engine_bytes = canonical_json_bytes(method_engine_data)
    method_engine_digest = sha256_bytes(method_engine_bytes)
    method_engine_text = escape_json_for_script(method_engine_bytes.decode('utf-8'))
    exam_policy_file = repo_root / EXAM_POLICY_PATH
    exam_policy_data = load_json(exam_policy_file)
    exam_policy_bytes = canonical_json_bytes(exam_policy_data)
    exam_policy_digest = sha256_bytes(exam_policy_bytes)
    exam_policy_text = escape_json_for_script(exam_policy_bytes.decode('utf-8'))
    response_types_file = repo_root / RESPONSE_TYPES_PATH
    response_types_data = load_json(response_types_file)
    response_types_bytes = canonical_json_bytes(response_types_data)
    response_types_digest = sha256_bytes(response_types_bytes)
    response_types_text = escape_json_for_script(response_types_bytes.decode('utf-8'))
    grading_policy_data = _required_json(repo_root, GRADING_POLICY_PATH, 'sim-grading-policy')
    grading_policy_bytes = canonical_json_bytes(grading_policy_data)
    grading_policy_digest = sha256_bytes(grading_policy_bytes)
    grading_policy_text = escape_json_for_script(grading_policy_bytes.decode('utf-8'))
    feedback_classification_data = _required_json(
        repo_root, FEEDBACK_CLASSIFICATION_PATH, 'sim-feedback-classification')
    feedback_classification_bytes = canonical_json_bytes(feedback_classification_data)
    feedback_classification_digest = sha256_bytes(feedback_classification_bytes)
    feedback_classification_text = escape_json_for_script(feedback_classification_bytes.decode('utf-8'))
    analytics_schema_data = _required_json(repo_root, ANALYTICS_SCHEMA_PATH, 'sim-analytics')
    analytics_bytes = canonical_json_bytes(analytics_schema_data)
    analytics_digest = sha256_bytes(analytics_bytes)
    analytics_text = escape_json_for_script(analytics_bytes.decode('utf-8'))
    mastery_policy_data = _required_json(repo_root, MASTERY_POLICY_PATH, 'sim-mastery-policy')
    mastery_policy_bytes = canonical_json_bytes(mastery_policy_data)
    mastery_policy_digest = sha256_bytes(mastery_policy_bytes)
    mastery_policy_text = escape_json_for_script(mastery_policy_bytes.decode('utf-8'))
    scheduler_policy_data = _required_json(repo_root, SCHEDULER_POLICY_PATH, 'sim-scheduler-policy')
    scheduler_policy_bytes = canonical_json_bytes(scheduler_policy_data)
    scheduler_policy_digest = sha256_bytes(scheduler_policy_bytes)
    scheduler_policy_text = escape_json_for_script(scheduler_policy_bytes.decode('utf-8'))
    remediation_policy_data = _required_json(repo_root, REMEDIATION_POLICY_PATH, 'sim-remediation-policy')
    remediation_policy_bytes = canonical_json_bytes(remediation_policy_data)
    remediation_policy_digest = sha256_bytes(remediation_policy_bytes)
    remediation_policy_text = escape_json_for_script(remediation_policy_bytes.decode('utf-8'))
    revision_policy_data = _required_json(repo_root, REVISION_POLICY_PATH, 'sim-revision-policy')
    revision_policy_bytes = canonical_json_bytes(revision_policy_data)
    revision_policy_digest = sha256_bytes(revision_policy_bytes)
    revision_policy_text = escape_json_for_script(revision_policy_bytes.decode('utf-8'))
    practice_policy_data = _required_json(repo_root, PRACTICE_POLICY_PATH, 'sim-practice-policy')
    practice_policy_bytes = canonical_json_bytes(practice_policy_data)
    practice_policy_digest = sha256_bytes(practice_policy_bytes)
    practice_policy_text = escape_json_for_script(practice_policy_bytes.decode('utf-8'))
    reading_contract_file = repo_root / READING_CONTRACT_PATH
    reading_contract_bytes = canonical_json_bytes(load_json(reading_contract_file))
    reading_contract_digest = sha256_bytes(reading_contract_bytes)
    energy_contract_file = repo_root / ENERGY_CONTRACT_PATH
    energy_contract_bytes = canonical_json_bytes(load_json(energy_contract_file))
    energy_contract_digest = sha256_bytes(energy_contract_bytes)
    kinetics_contract_file = repo_root / KINETICS_CONTRACT_PATH
    kinetics_contract_bytes = canonical_json_bytes(load_json(kinetics_contract_file))
    kinetics_contract_digest = sha256_bytes(kinetics_contract_bytes)
    titration_contract_file = repo_root / TITRATION_CONTRACT_PATH
    titration_contract_bytes = canonical_json_bytes(load_json(titration_contract_file))
    titration_contract_digest = sha256_bytes(titration_contract_bytes)
    calibration_contract_file = repo_root / CALIBRATION_CONTRACT_PATH
    calibration_contract_bytes = canonical_json_bytes(load_json(calibration_contract_file))
    calibration_contract_digest = sha256_bytes(calibration_contract_bytes)

    island_relative = str(island_path.relative_to(repo_root)) if island_path.is_relative_to(repo_root) else str(island_path)
    conventions_relative = str(conventions_file.relative_to(repo_root)) if conventions_file.is_relative_to(repo_root) else str(conventions_file)
    schema_relative = str(schema_file.relative_to(repo_root)) if schema_file.is_relative_to(repo_root) else str(schema_file)
    golden_relative = str(golden_file.relative_to(repo_root)) if golden_file.is_relative_to(repo_root) else str(golden_file)
    tokens_relative = str(tokens_file.relative_to(repo_root)) if tokens_file.is_relative_to(repo_root) else str(tokens_file)
    styles_relative = str(styles_file.relative_to(repo_root)) if styles_file.is_relative_to(repo_root) else str(styles_file)
    summaries_relative = str(summaries_file.relative_to(repo_root)) if summaries_file.is_relative_to(repo_root) else str(summaries_file)
    registry_relative = str(registry_file.relative_to(repo_root)) if registry_file.is_relative_to(repo_root) else str(registry_file)
    layers_relative = str(layers_file.relative_to(repo_root)) if layers_file.is_relative_to(repo_root) else str(layers_file)
    terms_relative = str(terms_file.relative_to(repo_root)) if terms_file.is_relative_to(repo_root) else str(terms_file)
    fig_relatives = [str(fp.relative_to(repo_root)) if fp.is_relative_to(repo_root) else str(fp) for fp in fig_paths]
    source_records = [
        {'path': island_relative, 'sha256': sha256_file(island_path), 'bytes': island_path.stat().st_size},
        {'path': conventions_relative, 'sha256': sha256_file(conventions_file), 'bytes': conventions_file.stat().st_size},
        {'path': schema_relative, 'sha256': sha256_file(schema_file), 'bytes': schema_file.stat().st_size},
        {'path': golden_relative, 'sha256': sha256_file(golden_file), 'bytes': golden_file.stat().st_size},
        {'path': tokens_relative, 'sha256': sha256_file(tokens_file), 'bytes': tokens_file.stat().st_size},
        {'path': styles_relative, 'sha256': sha256_file(styles_file), 'bytes': styles_file.stat().st_size},
        {'path': summaries_relative, 'sha256': sha256_file(summaries_file), 'bytes': summaries_file.stat().st_size},
        {'path': registry_relative, 'sha256': sha256_file(registry_file), 'bytes': registry_file.stat().st_size},
        {'path': layers_relative, 'sha256': sha256_file(layers_file), 'bytes': layers_file.stat().st_size},
        {'path': terms_relative, 'sha256': sha256_file(terms_file), 'bytes': terms_file.stat().st_size},
        _source_record(repo_root, CHAINS_PATH),
        _source_record(repo_root, CHAIN_SCHEMA_PATH),
        _source_record(repo_root, CHAIN_REFS_PATH),
        _source_record(repo_root, ENGINE_TAXONOMY_PATH),
        _source_record(repo_root, GRAPH_SCORING_CONTRACT_PATH),
        _source_record(repo_root, METHOD_CARDS_PATH),
        _source_record(repo_root, METHOD_ENGINE_CONTRACT_PATH),
        _source_record(repo_root, GRAPH_SCORING_JS_PATH),
        _source_record(repo_root, GRAPH_CAPTURE_JS_PATH),
    ] + [
        {'path': frel, 'sha256': sha256_file(fp), 'bytes': fp.stat().st_size}
        for frel, fp in zip(fig_relatives, fig_paths)
    ] + [
        _source_record(repo_root, FIGURE_SCHEMA_PATH),
        _source_record(repo_root, READING_CONTRACT_PATH),
        _source_record(repo_root, ENERGY_CONTRACT_PATH),
        _source_record(repo_root, KINETICS_CONTRACT_PATH),
        _source_record(repo_root, TITRATION_CONTRACT_PATH),
        _source_record(repo_root, CALIBRATION_CONTRACT_PATH),
        _source_record(repo_root, N06_TERM_STUBS_PATH),
        _source_record(repo_root, N08_TERM_STUBS_PATH),
        _source_record(repo_root, SEED_POLICY_PATH),
        _source_record(repo_root, PROTOCOL_PATH),
    ]
    source_records += [_source_record(repo_root, relative) for relative in [
        SHELL_PATH, LOADER_PATH, VIEW_PATH, CONVENTIONS_LOADER_PATH, BANK_LOADER_PATH,
        PRNG_JS_PATH, GOLDEN_VECTORS_LOADER_PATH, TERMS_LOADER_JS_PATH, FIGURE_FRAMEWORK_JS_PATH,
        LEAK_SCAN_JS_PATH, START_VIEW_JS_PATH, CONCEPT_MAP_JS_PATH, CONCEPT_DRAWER_JS_PATH,
        HINT_DRAWER_JS_PATH, THEME_TOGGLE_JS_PATH, SMOKE_SUBSET_JS_PATH, CHAIN_VIEW_JS_PATH,
        ENGINE_JS_PATH, VARIANT_ENGINE_JS_PATH, VARIANT_TEMPLATES_JS_PATH,
        EXAM_POLICY_PATH, SESSION_TS_PATH, EXAM_TS_PATH, SESSION_JS_PATH, EXAM_JS_PATH,
    ]]
    source_records += [_source_record(repo_root, relative) for relative in [
        RESPONSE_TYPES_PATH, INPUTS_REGISTRY_TS_PATH, INPUTS_COMPONENTS_TS_PATH,
        INPUTS_INTEGRATION_TS_PATH, INPUTS_REGISTRY_JS_PATH, INPUTS_COMPONENTS_JS_PATH,
        INPUTS_INTEGRATION_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N23') for relative in [
        GRADING_POLICY_PATH, FEEDBACK_CLASSIFICATION_PATH, GRADING_TS_PATH, FEEDBACK_TS_PATH,
        GRADING_JS_PATH, FEEDBACK_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N24') for relative in [
        ASSEMBLY_TS_PATH, ASSEMBLY_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N25') for relative in [
        ANALYTICS_SCHEMA_PATH, STORE_TS_PATH, ANALYTICS_TS_PATH, STORE_JS_PATH, ANALYTICS_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N26') for relative in [
        MASTERY_POLICY_PATH, MASTERY_TS_PATH, MASTERY_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N27') for relative in [
        SCHEDULER_POLICY_PATH, SCHEDULER_TS_PATH, SCHEDULER_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N28') for relative in [
        REMEDIATION_POLICY_PATH, REMEDIATION_TS_PATH, REMEDIATION_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N29') for relative in [
        REVISION_POLICY_PATH, REVISION_TS_PATH, REVISION_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N30') for relative in [
        PRACTICE_POLICY_PATH, PRACTICE_TS_PATH, PRACTICE_JS_PATH,
    ]]
    source_records += [_required_source_record(repo_root, relative, 'N19/N31') for relative in [
        METHOD_ENGINE_JS_PATH, METHOD_CARD_VIEW_JS_PATH, BUILD_POLICY_JSON_PATH,
    ]]
    source_records += [
        {'path': str(path.relative_to(repo_root)), 'sha256': sha256_file(path),
         'bytes': path.stat().st_size}
        for path in sorted((repo_root / FAMILY_TEMPLATE_DIR).rglob('*.json'))
    ]
    if bank_path is not None and bank_path.is_dir():
        source_records += [
            {'path': str(path.relative_to(repo_root)) if path.is_relative_to(repo_root) else str(path),
             'sha256': sha256_file(path),
             'bytes': path.stat().st_size}
            for path in sorted(bank_path.glob('*.json'))
        ]

    # Deduplicate and sort source_records deterministically by path (N31 A.1.3)
    dedup_sources: dict[str, dict] = {}
    for rec in source_records:
        dedup_sources[rec['path']] = rec
    source_records = [dedup_sources[k] for k in sorted(dedup_sources.keys())]

    build_policy_data = _required_json(repo_root, BUILD_POLICY_JSON_PATH, 'build-policy')

    shell = (repo_root / SHELL_PATH).read_text(encoding='utf-8')
    loader = compact_js_source((repo_root / LOADER_PATH).read_text(encoding='utf-8'))
    view = compact_js_source((repo_root / VIEW_PATH).read_text(encoding='utf-8'))
    conventions_loader = compact_js_source((repo_root / CONVENTIONS_LOADER_PATH).read_text(encoding='utf-8'))
    bank_loader = compact_js_source((repo_root / BANK_LOADER_PATH).read_text(encoding='utf-8'))
    prng_js = compact_js_source((repo_root / PRNG_JS_PATH).read_text(encoding='utf-8'))
    golden_loader = compact_js_source((repo_root / GOLDEN_VECTORS_LOADER_PATH).read_text(encoding='utf-8'))
    terms_loader_js = compact_js_source((repo_root / TERMS_LOADER_JS_PATH).read_text(encoding='utf-8'))
    figure_framework_js = compact_js_source((repo_root / FIGURE_FRAMEWORK_JS_PATH).read_text(encoding='utf-8'))
    chain_view_js = compact_js_source((repo_root / CHAIN_VIEW_JS_PATH).read_text(encoding='utf-8'))
    leak_scan_js = compact_js_source((repo_root / LEAK_SCAN_JS_PATH).read_text(encoding='utf-8'))
    quantity_engine_js = compact_js_source((repo_root / ENGINE_JS_PATH).read_text(encoding='utf-8'))
    graph_scoring_engine_js = compact_js_source((repo_root / GRAPH_SCORING_JS_PATH).read_text(encoding='utf-8'))
    graph_capture_js = compact_js_source((repo_root / GRAPH_CAPTURE_JS_PATH).read_text(encoding='utf-8'))
    method_engine_js = compact_js_source((repo_root / METHOD_ENGINE_JS_PATH).read_text(encoding='utf-8'))
    method_card_view_js = compact_js_source((repo_root / METHOD_CARD_VIEW_JS_PATH).read_text(encoding='utf-8'))
    variant_engine_js = compact_js_source((repo_root / VARIANT_ENGINE_JS_PATH).read_text(encoding='utf-8'))
    start_view_js = compact_js_source((repo_root / START_VIEW_JS_PATH).read_text(encoding='utf-8'))
    concept_map_js = compact_js_source((repo_root / CONCEPT_MAP_JS_PATH).read_text(encoding='utf-8'))
    concept_drawer_js = compact_js_source((repo_root / CONCEPT_DRAWER_JS_PATH).read_text(encoding='utf-8'))
    hint_drawer_js = compact_js_source((repo_root / HINT_DRAWER_JS_PATH).read_text(encoding='utf-8'))
    theme_toggle_js = compact_js_source((repo_root / THEME_TOGGLE_JS_PATH).read_text(encoding='utf-8'))
    smoke_subset_js = compact_js_source((repo_root / SMOKE_SUBSET_JS_PATH).read_text(encoding='utf-8'))
    session_js = compact_js_source((repo_root / SESSION_JS_PATH).read_text(encoding='utf-8'))
    inputs_registry_js = compact_js_source((repo_root / INPUTS_REGISTRY_JS_PATH).read_text(encoding='utf-8'))
    inputs_components_js = compact_js_source((repo_root / INPUTS_COMPONENTS_JS_PATH).read_text(encoding='utf-8'))
    inputs_integration_js = compact_js_source((repo_root / INPUTS_INTEGRATION_JS_PATH).read_text(encoding='utf-8'))
    grading_js = compact_js_source((repo_root / GRADING_JS_PATH).read_text(encoding='utf-8'))
    feedback_js = compact_js_source((repo_root / FEEDBACK_JS_PATH).read_text(encoding='utf-8'))
    assembly_js = compact_js_source((repo_root / ASSEMBLY_JS_PATH).read_text(encoding='utf-8'))
    exam_js = compact_js_source((repo_root / EXAM_JS_PATH).read_text(encoding='utf-8'))
    store_js = compact_js_source((repo_root / STORE_JS_PATH).read_text(encoding='utf-8'))
    analytics_js = compact_js_source((repo_root / ANALYTICS_JS_PATH).read_text(encoding='utf-8'))
    mastery_js = compact_js_source((repo_root / MASTERY_JS_PATH).read_text(encoding='utf-8'))
    scheduler_js = compact_js_source((repo_root / SCHEDULER_JS_PATH).read_text(encoding='utf-8'))
    remediation_js = compact_js_source((repo_root / REMEDIATION_JS_PATH).read_text(encoding='utf-8'))
    revision_js = compact_js_source((repo_root / REVISION_JS_PATH).read_text(encoding='utf-8'))
    practice_js = compact_js_source((repo_root / PRACTICE_JS_PATH).read_text(encoding='utf-8'))

    # Assemble each module with its declared boundary separator comment (N31 B.1.2)
    module_manifest_records: list[dict] = []
    inlined_modules_by_placeholder: dict[str, str] = {}
    for mod in build_policy_data['module_order']:
        mod_rel = mod['path']
        mod_file = repo_root / mod_rel
        raw_bytes = mod_file.read_bytes()
        raw_sha256 = sha256_bytes(raw_bytes)
        compacted_body = compact_js_source(raw_bytes.decode('utf-8'))
        separator = f"/* === MODULE: {mod_rel} === */"
        wrapped = f"{separator}\n{compacted_body}"
        wrapped_bytes = wrapped.encode('utf-8')
        inlined_sha256 = sha256_bytes(wrapped_bytes)
        inlined_modules_by_placeholder[mod['placeholder']] = wrapped
        module_manifest_records.append({
            'order': mod['order'],
            'id': mod['id'],
            'path': mod_rel,
            'owner_task': mod['owner_task'],
            'provides': mod['provides'],
            'consumes': mod['consumes'],
            'raw_bytes': len(raw_bytes),
            'raw_sha256': raw_sha256,
            'inlined_bytes': len(wrapped_bytes),
            'inlined_sha256': inlined_sha256,
        })

    island_stamp_records = [
        {'island_id': 'sim-coverage', 'bytes': len(island_bytes), 'sha256': sha256_bytes(island_bytes)},
        {'island_id': 'sim-conventions', 'bytes': len(conventions_bytes), 'sha256': sha256_bytes(conventions_bytes)},
        {'island_id': 'sim-bank', 'bytes': len(bank_bytes), 'sha256': bank_digest},
        {'island_id': 'sim-forms', 'bytes': len(forms_bytes), 'sha256': forms_digest},
        {'island_id': 'sim-golden-vectors', 'bytes': len(golden_bytes), 'sha256': sha256_bytes(golden_bytes)},
        {'island_id': 'sim-terms', 'bytes': len(terms_bytes), 'sha256': terms_digest},
        {'island_id': 'sim-analytics', 'bytes': len(analytics_bytes), 'sha256': analytics_digest},
        {'island_id': 'sim-mastery-policy', 'bytes': len(mastery_policy_bytes), 'sha256': mastery_policy_digest},
        {'island_id': 'sim-scheduler-policy', 'bytes': len(scheduler_policy_bytes), 'sha256': scheduler_policy_digest},
        {'island_id': 'sim-remediation-policy', 'bytes': len(remediation_policy_bytes), 'sha256': remediation_policy_digest},
        {'island_id': 'sim-revision-policy', 'bytes': len(revision_policy_bytes), 'sha256': revision_policy_digest},
        {'island_id': 'sim-practice-policy', 'bytes': len(practice_policy_bytes), 'sha256': practice_policy_digest},
        {'island_id': 'sim-figures', 'bytes': len(figures_bytes), 'sha256': figures_digest},
        {'island_id': 'sim-chains', 'bytes': len(chains_bytes), 'sha256': chains_digest},
        {'island_id': 'sim-engines', 'bytes': len(engines_bytes), 'sha256': engines_digest},
        {'island_id': 'sim-graph-scoring', 'bytes': len(graph_scoring_bytes), 'sha256': graph_scoring_digest},
        {'island_id': 'sim-method-cards', 'bytes': len(method_cards_bytes), 'sha256': method_cards_digest},
        {'island_id': 'sim-method-engine', 'bytes': len(method_engine_bytes), 'sha256': method_engine_digest},
        {'island_id': 'sim-exam-policy', 'bytes': len(exam_policy_bytes), 'sha256': exam_policy_digest},
        {'island_id': 'sim-response-types', 'bytes': len(response_types_bytes), 'sha256': response_types_digest},
        {'island_id': 'sim-grading-policy', 'bytes': len(grading_policy_bytes), 'sha256': grading_policy_digest},
        {'island_id': 'sim-feedback-classification', 'bytes': len(feedback_classification_bytes), 'sha256': feedback_classification_digest},
    ]

    stamp_info = validate_n31_build_policy.compute_build_stamp(
        version=build_policy_data['version'],
        iso_date=build_policy_data['iso_date'],
        policy_id=build_policy_data['policy_id'],
        sources=source_records,
        islands=island_stamp_records,
        modules=module_manifest_records,
    )
    build_id = stamp_info['build_id']
    composite_digest = stamp_info['composite_digest']

    document = shell
    document = _replace_once(document, '__BUILD_ID__', build_id)
    document = _replace_once(document, '__BUILD_VERSION__', str(build_policy_data['version']))
    document = _replace_once(document, '__BUILD_ISO_DATE__', str(build_policy_data['iso_date']))
    document = _replace_once(document, '__COMPOSITE_DIGEST__', composite_digest)
    document = _replace_once(document, '__ISLAND_DIGEST__', sha256_bytes(island_bytes))
    document = _replace_once(document, '__CONVENTIONS_DIGEST__', sha256_bytes(conventions_bytes))
    document = _replace_once(document, '__BANK_DIGEST__', sha256_bytes(bank_bytes))
    document = _replace_once(document, '__BANK_EMBEDDED_DIGEST__', bank_embedded_digest)
    document = _replace_once(document, '__FORMS_DIGEST__', forms_digest)
    document = _replace_once(document, '__GOLDEN_VECTORS_DIGEST__', sha256_bytes(golden_bytes))
    document = _replace_once(document, '__TOKENS_DIGEST__', tokens_digest)
    document = _replace_once(document, '__CONCEPT_SUMMARIES_DIGEST__', summaries_digest)
    document = _replace_once(document, '__ANCHOR_REGISTRY_DIGEST__', registry_digest)
    document = _replace_once(document, '__RECALL_LAYERS_DIGEST__', layers_digest)
    document = _replace_once(document, '__TERMS_DIGEST__', terms_digest)
    document = _replace_once(document, '__ANALYTICS_DIGEST__', analytics_digest)
    document = _replace_once(document, '__MASTERY_POLICY_DIGEST__', mastery_policy_digest)
    document = _replace_once(document, '__SCHEDULER_POLICY_DIGEST__', scheduler_policy_digest)
    document = _replace_once(document, '__REMEDIATION_POLICY_DIGEST__', remediation_policy_digest)
    document = _replace_once(document, '__REVISION_POLICY_DIGEST__', revision_policy_digest)
    document = _replace_once(document, '__PRACTICE_POLICY_DIGEST__', practice_policy_digest)
    document = _replace_once(document, '__FIGURES_DIGEST__', figures_digest)
    document = _replace_once(document, '__CHAINS_DIGEST__', chains_digest)
    document = _replace_once(document, '__ENGINES_DIGEST__', engines_digest)
    document = _replace_once(document, '__GRAPH_SCORING_DIGEST__', graph_scoring_digest)
    document = _replace_once(document, '__METHOD_CARDS_DIGEST__', method_cards_digest)
    document = _replace_once(document, '__METHOD_ENGINE_DIGEST__', method_engine_digest)
    document = _replace_once(document, '__EXAM_POLICY_DIGEST__', exam_policy_digest)
    document = _replace_once(document, '__RESPONSE_TYPES_DIGEST__', response_types_digest)
    document = _replace_once(document, '__GRADING_POLICY_DIGEST__', grading_policy_digest)
    document = _replace_once(document, '__FEEDBACK_CLASSIFICATION_DIGEST__', feedback_classification_digest)
    document = _replace_once(document, '__READING_CONTRACT_DIGEST__', reading_contract_digest)
    document = _replace_once(document, '__ENERGY_CONTRACT_DIGEST__', energy_contract_digest)
    document = _replace_once(document, '__KINETICS_CONTRACT_DIGEST__', kinetics_contract_digest)
    noscript_html = render_noscript_html(
        coverage=island,
        anchor_registry=registry_data,
        concept_summaries=summaries_data,
        conventions=conventions,
        terms_data=terms_data,
    )
    document = _replace_once(document, '__TOKENS_CSS__', tokens_css)
    document = _replace_once(document, '__STYLES_CSS__', styles_css)
    document = _replace_once(document, '__SIM_NOSCRIPT_HTML__', noscript_html)
    document = _replace_once(document, '__SIM_COVERAGE_JSON__', island_text)
    document = _replace_once(document, '__SIM_CONVENTIONS_JSON__', conventions_text)
    document = _replace_once(document, '__SIM_BANK_JSON__', bank_text)
    document = _replace_once(document, '__SIM_FORMS_JSON__', forms_text)
    document = _replace_once(document, '__SIM_GOLDEN_VECTORS_JSON__', golden_text)
    document = _replace_once(document, '__SIM_TERMS_JSON__', terms_text)
    document = _replace_once(document, '__SIM_ANALYTICS_JSON__', analytics_text)
    document = _replace_once(document, '__SIM_MASTERY_POLICY_JSON__', mastery_policy_text)
    document = _replace_once(document, '__SIM_SCHEDULER_POLICY_JSON__', scheduler_policy_text)
    document = _replace_once(document, '__SIM_REMEDIATION_POLICY_JSON__', remediation_policy_text)
    document = _replace_once(document, '__SIM_REVISION_POLICY_JSON__', revision_policy_text)
    document = _replace_once(document, '__SIM_PRACTICE_POLICY_JSON__', practice_policy_text)
    document = _replace_once(document, '__SIM_FIGURES_JSON__', figures_text)
    document = _replace_once(document, '__SIM_CHAINS_JSON__', chains_text)
    document = _replace_once(document, '__SIM_ENGINES_JSON__', engines_text)
    document = _replace_once(document, '__SIM_GRAPH_SCORING_JSON__', graph_scoring_text)
    document = _replace_once(document, '__SIM_METHOD_CARDS_JSON__', method_cards_text)
    document = _replace_once(document, '__SIM_METHOD_ENGINE_JSON__', method_engine_text)
    document = _replace_once(document, '__SIM_EXAM_POLICY_JSON__', exam_policy_text)
    document = _replace_once(document, '__SIM_RESPONSE_TYPES_JSON__', response_types_text)
    document = _replace_once(document, '__SIM_GRADING_POLICY_JSON__', grading_policy_text)
    document = _replace_once(document, '__SIM_FEEDBACK_CLASSIFICATION_JSON__', feedback_classification_text)
    document = _replace_once(document, '__COVERAGE_INVARIANTS__', invariants_text)
    document = _replace_once(document, '__CONCEPT_DRAWER_JSON__', compact_summaries_text)
    document = _replace_once(document, '__ANCHOR_REGISTRY_JSON__', compact_registry_text)
    document = _replace_once(document, '__RECALL_LAYERS_JSON__', compact_layers_text)
    for mod in build_policy_data['module_order']:
        ph = mod['placeholder']
        document = _replace_once(document, ph, inlined_modules_by_placeholder[ph])
    document = compact_shell_inline_script(document)

    shell_report = validate_shell(html_text=document, repo_root=repo_root)
    gate_records.append({
        'order': 6,
        'id': 'n06_shell',
        'owner': 'N06',
        'status': shell_report['status'],
        'summary': format_shell_summary(shell_report),
    })
    if shell_report['status'] != 'PASS':
        first = _first_gate_error(shell_report)
        print(f'FAIL n06_shell gate (order 6, owner N06): {first}', file=sys.stderr)
        for error in shell_report.get('errors', [])[1:]:
            print(f'  - {error}', file=sys.stderr)
        print('Refusing build. The artifact was not written.', file=sys.stderr)
        raise SystemExit(1)

    output_bytes = document.encode('utf-8')
    contract_report = check_artifact.check_artifact(
        html_path=output_path,
        manifest_path=None,
        policy_path=repo_root / BUILD_POLICY_JSON_PATH,
        html_bytes=output_bytes,
    )
    gate_records.append({
        'order': 28,
        'id': 'artifact_contract',
        'owner': 'N31',
        'status': contract_report['status'],
        'summary': _format_gate_summary('artifact_contract', contract_report),
    })
    reports['artifact_contract'] = contract_report
    gate_records.sort(key=lambda g: g['order'])
    if contract_report['status'] != 'PASS':
        first = _first_gate_error(contract_report)
        print(f'FAIL artifact_contract gate (order 28, owner N31): {first}', file=sys.stderr)
        for error in contract_report.get('errors', [])[1:]:
            print(f'  - {error}', file=sys.stderr)
        print('Refusing build. The artifact was not written.', file=sys.stderr)
        raise SystemExit(1)

    _atomic_write(output_path, output_bytes)
    forms_out_dir = output_path.parent / 'forms'
    form_manifest_records: dict[str, Any] = {}
    for fm in forms_island['forms']:
        fid = fm['form_id']
        fm_path = forms_out_dir / f'form_{fid}.json'
        fm_bytes = canonical_json_bytes(fm)
        _atomic_write(fm_path, fm_bytes)
        form_manifest_records[fid] = {
            'path': str(fm_path.relative_to(repo_root)) if fm_path.is_relative_to(repo_root) else str(fm_path),
            'form_seed': fm['form_seed'],
            'manifest_digest': fm['manifest_digest'],
            'sha256': sha256_bytes(fm_bytes),
            'bytes': len(fm_bytes),
            'total_slots': fm['total_slots'],
            'total_points': fm['total_points'],
        }

    manifest = {
        'schema_version': 1,
        'artifact': 'simulator-build-manifest',
        'task': 'N02/N03/N04/N05/N06/N07/N08/N10/N11/N12/N13/N14/N15/N16/N17/N18/N19/N20/N21/N22/N23/N24/N25/N26/N27/N28/N29/N30/N31',
        'policy_id': build_policy_data['policy_id'],
        'version': build_policy_data['version'],
        'iso_date': build_policy_data['iso_date'],
        'build_policy': BUILD_POLICY,
        'build_id': build_id,
        'composite_digest': composite_digest,
        'output': str(output_path.relative_to(repo_root)) if output_path.is_relative_to(repo_root) else str(output_path),
        'output_sha256': sha256_bytes(output_bytes),
        'output_bytes': len(output_bytes),
        'module_order': module_manifest_records,
        'composition_table': contract_report['composition_table'],
        'island': {
            'id': 'sim-coverage',
            'source': island_relative,
            'digest': sha256_bytes(island_bytes),
            'bytes': len(island_bytes),
            'emission': JSON_EMISSION,
        },
        'conventions_island': {
            'id': 'sim-conventions',
            'source': conventions_relative,
            'digest': sha256_bytes(conventions_bytes),
            'bytes': len(conventions_bytes),
            'emission': JSON_EMISSION,
        },
        'bank_island': {
            'id': 'sim-bank',
            'source': str(bank_path) if bank_path else schema_relative,
            'digest': sha256_bytes(bank_bytes),
            'embedded_digest': bank_embedded_digest,
            'source_digest': _bank_source_digest(bank_path),
            'bytes': len(bank_bytes),
            'questions_count': len(bank_island['questions']),
            'status': bank_island.get('status'),
            'projection': {
                'dropped_extension_fields': list(BANK_PROJECTION_DROPPED),
                'reason': 'The drawn values, the derived values and the review '
                          'workflow record are the audit trail. They stay in the '
                          'frozen bank files and in the N20 evidence records; the '
                          'artifact embeds the runtime projection so that the '
                          'Section 1.3 budget (700–1400 KiB total) holds.',
                'audit_trail': ['data/bank/*.json', 'evidence/N20_REVIEW_WORKFLOW.json',
                                'evidence/N20_RECOMPUTE_RECORD.json',
                                'evidence/N20_LEAK_SCAN_RECORD.json'],
            },
            'review_gate': 'N20 bank_review (order 16): every instance must be in the '
                           'accepted review state; the gate refuses the build otherwise.',
            'emission': JSON_EMISSION,
        },
        'forms_island': {
            'id': 'sim-forms',
            'digest': forms_digest,
            'bytes': len(forms_bytes),
            'policy_id': forms_island['policy_id'],
            'prng_contract_digest': forms_island['prng_contract_digest'],
            'bank_digest': bank_digest,
            'forms_count': len(forms_island['forms']),
            'shortages_count': len(forms_island['shortages']),
            'manifests': form_manifest_records,
            'conflicts': forms_island['conflicts'],
            'assembly_module': {
                'typescript_source': ASSEMBLY_TS_PATH,
                'runtime_module': ASSEMBLY_JS_PATH,
                'compacted_js_bytes': len(assembly_js.encode('utf-8')),
                'module_digest': sha256_file(repo_root / ASSEMBLY_JS_PATH),
                'inlined_in_artifact': True,
            },
            'emission': JSON_EMISSION,
        },
        'analytics_layer': {
            'id': 'sim-analytics',
            'source': ANALYTICS_SCHEMA_PATH,
            'digest': analytics_digest,
            'bytes': len(analytics_bytes),
            'schema_version': analytics_schema_data.get('schema_version'),
            'max_events': (analytics_schema_data.get('store_contract') or {}).get('max_events'),
            'f10_status': (analytics_schema_data.get('f10_boundary') or {}).get('status'),
            'typescript_sources': [STORE_TS_PATH, ANALYTICS_TS_PATH],
            'runtime_modules': [STORE_JS_PATH, ANALYTICS_JS_PATH],
            'store_compacted_js_bytes': len(store_js.encode('utf-8')),
            'analytics_compacted_js_bytes': len(analytics_js.encode('utf-8')),
            'store_module_digest': sha256_file(repo_root / STORE_JS_PATH),
            'analytics_module_digest': sha256_file(repo_root / ANALYTICS_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'mastery_layer': {
            'id': 'sim-mastery-policy',
            'source': MASTERY_POLICY_PATH,
            'digest': mastery_policy_digest,
            'bytes': len(mastery_policy_bytes),
            'policy_id': mastery_policy_data.get('policy_id'),
            'epistemic_label': mastery_policy_data.get('epistemic_label'),
            'official_counterpart_status': mastery_policy_data.get('official_counterpart_status'),
            'states': [s.get('id') for s in (mastery_policy_data.get('states') or [])],
            'typescript_source': MASTERY_TS_PATH,
            'runtime_module': MASTERY_JS_PATH,
            'mastery_compacted_js_bytes': len(mastery_js.encode('utf-8')),
            'mastery_module_digest': sha256_file(repo_root / MASTERY_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'scheduler_layer': {
            'id': 'sim-scheduler-policy',
            'source': SCHEDULER_POLICY_PATH,
            'digest': scheduler_policy_digest,
            'bytes': len(scheduler_policy_bytes),
            'policy_id': scheduler_policy_data.get('policy_id'),
            'epistemic_label': scheduler_policy_data.get('epistemic_label'),
            'official_counterpart_status': scheduler_policy_data.get('official_counterpart_status'),
            'boxes': [{'box': b.get('box'), 'interval_days': b.get('interval_days')} for b in (scheduler_policy_data.get('boxes') or [])],
            'queue_cap': (scheduler_policy_data.get('queue_cap') or {}).get('value'),
            'typescript_source': SCHEDULER_TS_PATH,
            'runtime_module': SCHEDULER_JS_PATH,
            'scheduler_compacted_js_bytes': len(scheduler_js.encode('utf-8')),
            'scheduler_module_digest': sha256_file(repo_root / SCHEDULER_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'remediation_layer': {
            'id': 'sim-remediation-policy',
            'source': REMEDIATION_POLICY_PATH,
            'digest': remediation_policy_digest,
            'bytes': len(remediation_policy_bytes),
            'policy_id': remediation_policy_data.get('policy_id'),
            'epistemic_label': remediation_policy_data.get('epistemic_label'),
            'official_counterpart_status': remediation_policy_data.get('official_counterpart_status'),
            'recommend_only': remediation_policy_data.get('recommend_only'),
            'resolution_mode': (remediation_policy_data.get('resolution_policy') or {}).get('mode'),
            'typescript_source': REMEDIATION_TS_PATH,
            'runtime_module': REMEDIATION_JS_PATH,
            'remediation_compacted_js_bytes': len(remediation_js.encode('utf-8')),
            'remediation_module_digest': sha256_file(repo_root / REMEDIATION_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'revision_layer': {
            'id': 'sim-revision-policy',
            'source': REVISION_POLICY_PATH,
            'digest': revision_policy_digest,
            'bytes': len(revision_policy_bytes),
            'policy_id': revision_policy_data.get('policy_id'),
            'epistemic_label': revision_policy_data.get('epistemic_label'),
            'official_counterpart_status': revision_policy_data.get('official_counterpart_status'),
            'note_max_length': (revision_policy_data.get('self_assessment') or {}).get('note_max_length'),
            'typescript_source': REVISION_TS_PATH,
            'runtime_module': REVISION_JS_PATH,
            'revision_compacted_js_bytes': len(revision_js.encode('utf-8')),
            'revision_module_digest': sha256_file(repo_root / REVISION_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'practice_layer': {
            'id': 'sim-practice-policy',
            'source': PRACTICE_POLICY_PATH,
            'digest': practice_policy_digest,
            'bytes': len(practice_policy_bytes),
            'policy_id': practice_policy_data.get('policy_id'),
            'epistemic_label': practice_policy_data.get('epistemic_label'),
            'official_counterpart_status': practice_policy_data.get('official_counterpart_status'),
            'topic_lengths': {
                k: v.get('declared_length')
                for k, v in sorted((practice_policy_data.get('topic_lengths') or {}).items())
                if isinstance(v, dict)
            },
            'typescript_source': PRACTICE_TS_PATH,
            'runtime_module': PRACTICE_JS_PATH,
            'practice_compacted_js_bytes': len(practice_js.encode('utf-8')),
            'practice_module_digest': sha256_file(repo_root / PRACTICE_JS_PATH),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'variant_engine_layer': {
            'id': 'n20-variant-engine',
            'runtime_module': VARIANT_ENGINE_JS_PATH,
            'template_asset': VARIANT_TEMPLATES_JS_PATH,
            'template_data': FAMILY_TEMPLATE_DIR,
            'template_files': sorted(
                str(path.relative_to(repo_root))
                for path in (repo_root / FAMILY_TEMPLATE_DIR).rglob('*.json')),
            'template_digest': reports['bank_review'].get('template_digest'),
            'inlined_in_artifact': True,
            'templates_inlined_in_artifact': False,
            'note': 'N31 inlines src/variant-engine.js (SimVariantEngine) into the single-file '
                    'artifact for seed derivation and remediation support, while '
                    'src/variant-templates.js (308.6 KiB raw generator templates) remains in '
                    'src/ as an authoring asset because all 112 reviewed instances are '
                    'embedded in #sim-bank.',
            'ephemeral_contract': {
                'seed_key_pattern': '{family}-{variant}-EPH-{attempt}',
                'exclusion_rule': 'A retry seed that is already a frozen seed is skipped; '
                                   'the attempt counter advances until an unused seed is found.',
                'persistence': 'never persisted; the instance lives in the in-memory session only.',
                'identity': 'The ephemeral instance carries its own question id (-EPH-{attempt}) '
                            'so that it cannot be confused with the frozen instance.',
            },
        },
        'golden_vectors_island': {
            'id': 'sim-golden-vectors',
            'source': golden_relative,
            'digest': sha256_bytes(golden_bytes),
            'bytes': len(golden_bytes),
            'vectors_count': len([v for v in golden_island.get('vectors', []) if v.get('status') == 'active']),
            'emission': JSON_EMISSION,
        },
        'chains_island': {
            'id': 'sim-chains',
            'source': str(chains_file.relative_to(repo_root)) if chains_file.is_relative_to(repo_root) else str(chains_file),
            'digest': chains_digest,
            'bytes': len(chains_bytes),
            'chain_count': len(chains_projection['chains']),
            'step_count': sum(len(c['steps']) for c in chains_projection['chains']),
            'sealed': True,
        },
        'engines_island': {
            'id': 'sim-engines',
            'source': str(engines_file.relative_to(repo_root)) if engines_file.is_relative_to(repo_root) else str(engines_file),
            'digest': engines_digest,
            'bytes': len(engines_bytes),
            'engine_count': 2,
            'error_class_count': len(engines_data['error_taxonomy']['classes']),
            'vector_count': len(engines_data['engine_vectors']['classification_vectors']),
            'runtime_module': ENGINE_JS_PATH,
            'inlined_in_artifact': True,
        },
        'graph_scoring_island': {
            'id': 'sim-graph-scoring',
            'source': str(graph_scoring_file.relative_to(repo_root)) if graph_scoring_file.is_relative_to(repo_root) else str(graph_scoring_file),
            'digest': graph_scoring_digest,
            'bytes': len(graph_scoring_bytes),
            'reading_vectors': len(graph_scoring_data['graph_vectors']['reading_vectors']),
            'drawing_vectors': len(graph_scoring_data['graph_vectors']['drawing_vectors']),
            'validity_cases': len(graph_scoring_data['graph_vectors']['validity_corpus']),
            'capture_contexts': len(graph_scoring_data['capture_contract']['capture_contexts']),
            'runtime_module': GRAPH_SCORING_JS_PATH,
            'capture_module': GRAPH_CAPTURE_JS_PATH,
            'inlined_in_artifact': True,
        },
        'method_cards_layer': {
            'id': 'sim-method-cards',
            'source': str(method_cards_file.relative_to(repo_root)) if method_cards_file.is_relative_to(repo_root) else str(method_cards_file),
            'digest': method_cards_digest,
            'bytes': len(method_cards_bytes),
            'cards_count': len(method_cards_projection.get('cards', [])),
            'step_count': sum(len(c.get('steps') or []) for c in method_cards_projection.get('cards', [])),
            'free_order_group_count': sum(len(c.get('free_order_groups') or []) for c in method_cards_data.get('cards', [])),
            'sequence_prompt_count': sum(len(c.get('sequence_prompts') or []) for c in method_cards_data.get('cards', [])),
            'runtime_module': METHOD_ENGINE_JS_PATH,
            'card_view_module': METHOD_CARD_VIEW_JS_PATH,
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'method_engine_layer': {
            'id': 'sim-method-engine',
            'source': str(method_engine_file.relative_to(repo_root)) if method_engine_file.is_relative_to(repo_root) else str(method_engine_file),
            'digest': method_engine_digest,
            'bytes': len(method_engine_bytes),
            'engines': ['ordering', 'matching', 'sequence', 'self_assessment'],
            'signature_count': len(method_engine_data.get('signature_registry', [])),
            'stratum_vectors': sum(
                len(method_engine_data.get('method_vectors', {}).get(key, []))
                for key in ('ordering_vectors', 'matching_vectors', 'sequence_vectors', 'self_assessment_vectors')
            ),
            'inlined_in_artifact': True,
            'emission': JSON_EMISSION,
        },
        'exam_shell_layer': {
            'id': 'sim-exam-policy',
            'source': str(exam_policy_file.relative_to(repo_root)) if exam_policy_file.is_relative_to(repo_root) else str(exam_policy_file),
            'digest': exam_policy_digest,
            'bytes': len(exam_policy_bytes),
            'session_states': exam_policy_data['session_contract']['states'],
            'session_events': exam_policy_data['session_contract']['events'],
            'transition_count': len(exam_policy_data['session_contract']['transition_table']),
            'error_ids': exam_policy_data['session_contract']['error_ids'],
            'slot_count': exam_policy_data['exam']['slot_count'],
            'points_total': exam_policy_data['exam']['total_points'],
            'advisory_limit_seconds': exam_policy_data['timer']['advisory_limit_seconds'],
            'threshold_ratio': exam_policy_data['timer']['threshold_ratio'],
            'modes': sorted(exam_policy_data['view_discipline']['modes'].keys()),
            'typescript_sources': [SESSION_TS_PATH, EXAM_TS_PATH],
            'runtime_modules': [SESSION_JS_PATH, EXAM_JS_PATH],
            'session_js_bytes': len(session_js.encode('utf-8')),
            'exam_js_bytes': len(exam_js.encode('utf-8')),
            'session_module_digest': sha256_file(repo_root / SESSION_JS_PATH),
            'exam_module_digest': sha256_file(repo_root / EXAM_JS_PATH),
            'timer': exam_policy_data['timer'],
            'view_discipline': exam_policy_data['view_discipline'],
            'conflicts': exam_policy_data['conflicts'],
            'slots': exam_policy_data['slots'],
            'payload_contracts': exam_policy_data['session_contract']['payload_contracts'],
            'named_variants': exam_policy_data['session_contract']['named_variants'],
            'inlined_in_artifact': True,
            'note': 'The N21 session machine and exam shell are authored in strict '
                    'TypeScript and compiled to local JavaScript by '
                    'tools/compile_n21_ts.py; build gate 17 (exam_shell) refuses a '
                    'build whose compiled modules differ from their sources.',
            'emission': JSON_EMISSION,
        },
        'response_inputs_layer': {
            'id': 'sim-response-types',
            'source': str(response_types_file.relative_to(repo_root)) if response_types_file.is_relative_to(repo_root) else str(response_types_file),
            'digest': response_types_digest,
            'bytes': len(response_types_bytes),
            'type_count': len(response_types_data.get('types', {})),
            'completed_types': response_types_data.get('completed_types', []),
            'conflicts': response_types_data.get('conflicts', []),
            'typescript_sources': [INPUTS_REGISTRY_TS_PATH, INPUTS_COMPONENTS_TS_PATH, INPUTS_INTEGRATION_TS_PATH],
            'runtime_modules': [INPUTS_REGISTRY_JS_PATH, INPUTS_COMPONENTS_JS_PATH, INPUTS_INTEGRATION_JS_PATH],
            'registry_js_bytes': len((repo_root / INPUTS_REGISTRY_JS_PATH).read_text(encoding='utf-8').encode('utf-8')),
            'components_js_bytes': len((repo_root / INPUTS_COMPONENTS_JS_PATH).read_text(encoding='utf-8').encode('utf-8')),
            'integration_js_bytes': len((repo_root / INPUTS_INTEGRATION_JS_PATH).read_text(encoding='utf-8').encode('utf-8')),
            'registry_module_digest': sha256_file(repo_root / INPUTS_REGISTRY_JS_PATH),
            'components_module_digest': sha256_file(repo_root / INPUTS_COMPONENTS_JS_PATH),
            'integration_module_digest': sha256_file(repo_root / INPUTS_INTEGRATION_JS_PATH),
            'inlined_in_artifact': True,
            'note': 'N31 inlines the N22 response-input modules (registry.js, components.js, '
                    'integration.js) into the single-file artifact in topological order; '
                    'build gate 18 (response_inputs) validates the registry island and '
                    'refuses a build whose compiled modules differ from their sources.',
            'emission': JSON_EMISSION,
        },
        'grading_layer': {
            'ids': ['sim-grading-policy', 'sim-feedback-classification'],
            'typescript_sources': [GRADING_TS_PATH, FEEDBACK_TS_PATH],
            'runtime_modules': [GRADING_JS_PATH, FEEDBACK_JS_PATH],
            'module_files': [
                {
                    'path': relative,
                    'bytes': (repo_root / relative).stat().st_size,
                    'sha256': sha256_file(repo_root / relative),
                }
                for relative in [GRADING_TS_PATH, FEEDBACK_TS_PATH, GRADING_JS_PATH, FEEDBACK_JS_PATH]
            ],
            'islands': [
                {
                    'id': 'sim-grading-policy',
                    'source': GRADING_POLICY_PATH,
                    'digest': grading_policy_digest,
                    'bytes': len(grading_policy_bytes),
                    'inlined_in_artifact': True,
                    'emission': JSON_EMISSION,
                },
                {
                    'id': 'sim-feedback-classification',
                    'source': FEEDBACK_CLASSIFICATION_PATH,
                    'digest': feedback_classification_digest,
                    'bytes': len(feedback_classification_bytes),
                    'inlined_in_artifact': True,
                    'emission': JSON_EMISSION,
                },
            ],
            'inlined_in_artifact': True,
            'note': 'N31 inlines the N23 grading (src/compiled/grading.js) and feedback '
                    '(src/compiled/feedback.js) modules into the single-file artifact '
                    'alongside the two policy islands (#sim-grading-policy and '
                    '#sim-feedback-classification).',
            'emission': JSON_EMISSION,
        },
        'tokens_layer': {
            'source': tokens_relative,
            'digest': tokens_digest,
            'bytes': len(tokens_bytes),
            'styles_source': styles_relative,
            'css_bytes': shell_report['byte_accounting']['css_bytes'],
            'runtime_js_bytes': shell_report['byte_accounting']['runtime_js_bytes'],
            'runtime_js_code_bytes': shell_report['byte_accounting']['runtime_js_code_bytes'],
            'embedded_js_data_bytes': shell_report['byte_accounting']['embedded_js_data_bytes'],
            'template_overhead_bytes': shell_report['byte_accounting']['template_overhead_bytes'],
        },
        'concept_map_layer': {
            'summaries_source': summaries_relative,
            'summaries_digest': summaries_digest,
            'summaries_bytes': len(summaries_bytes),
            'embedded_summaries_bytes': len(compact_summaries_bytes),
            'registry_source': registry_relative,
            'registry_digest': registry_digest,
            'registry_bytes': len(registry_bytes),
            'embedded_registry_bytes': len(compact_registry_bytes),
            'layout_digest': reports['concept_map']['layout']['layout_digest'],
            'concept_map_js_bytes': len(concept_map_js.encode('utf-8')),
            'concept_drawer_js_bytes': len(concept_drawer_js.encode('utf-8')),
        },
        'recall_layers_layer': {
            'source': layers_relative,
            'digest': layers_digest,
            'bytes': len(layers_bytes),
            'embedded_layers_bytes': len(compact_layers_bytes),
            'hint_drawer_js_bytes': len(hint_drawer_js.encode('utf-8')),
            'authored_families': reports['recall_layers']['summary']['authored_families'],
            'gap_families': reports['recall_layers']['summary']['gap_families'],
        },
        'terms_island': {
            'id': 'sim-terms',
            'source': terms_relative,
            'digest': terms_digest,
            'bytes': len(terms_bytes),
            'terms_loader_js_bytes': len(terms_loader_js.encode('utf-8')),
            'total_entries': reports['terminology']['total_entries'],
            'counts_by_class': reports['terminology']['counts_by_class'],
            'emission': JSON_EMISSION,
        },
        'figures_island': {
            'id': 'sim-figures',
            'sources': fig_relatives,
            'digest': figures_digest,
            'bytes': len(figures_bytes),
            'figure_framework_js_bytes': len(figure_framework_js.encode('utf-8')),
            'leak_scan_js_bytes': len(leak_scan_js.encode('utf-8')),
            'reading_contract_digest': reading_contract_digest,
            'energy_contract_digest': energy_contract_digest,
            'kinetics_contract_digest': kinetics_contract_digest,
            'titration_contract_digest': titration_contract_digest,
            'calibration_contract_digest': calibration_contract_digest,
            'figures_count': reports['figures']['figures_count'],
            't12_slots_closed': reports['figures']['t12_slots_closed'],
            't23_slots_closed': reports['figures']['t23_slots_closed'],
            't4_slots_closed': reports['figures']['t4_slots_closed'],
            't5_slots_closed': reports['figures']['t5_slots_closed'],
            't67_slots_closed': reports['figures']['t67_slots_closed'],
            'recomputed_count': len(reports['figures']['recompute_table']),
            'burette_geometry_count': len(reports['figures']['burette_geometry_table']),
            'dilution_arithmetic_count': len(reports['figures']['dilution_arithmetic_table']),
            'curve_generation_count': len(reports['figures']['curve_generation_table']),
            'hess_cycle_count': len(reports['figures']['hess_cycle_table']),
            'mb_honesty_count': len(reports['figures']['mb_honesty_table']),
            'kinetics_transform_count': len(reports['figures']['kinetics_transform_table']),
            'kinetics_tolerance_count': len(reports['figures']['kinetics_tolerance_table']),
            'kinetics_span_count': len(reports['figures']['kinetics_span_table']),
            'leak_scan_status': reports['figure_leak_scan']['status'],
            'leak_scan_exempt_count': reports['figure_leak_scan']['exempt_figures'],
            'leak_scan_flags_count': reports['figure_leak_scan']['flags_count'],
            'emission': JSON_EMISSION,
        },
        'gates': gate_records,
        'sources': source_records,
    }
    _atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8'))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--island', default=str(DEST / COVERAGE_PATH))
    parser.add_argument('--conventions', default=str(DEST / CONVENTIONS_PATH))
    parser.add_argument('--schema', default=str(DEST / SCHEMA_PATH))
    parser.add_argument('--bank', default=str(DEST / BANK_DIR),
                        help='Practice bank directory (N20 frozen bank).')
    parser.add_argument('--golden-vectors', default=str(DEST / GOLDEN_VECTORS_PATH))
    parser.add_argument('--tokens', default=str(DEST / TOKENS_PATH))
    parser.add_argument('--styles', default=str(DEST / STYLES_PATH))
    parser.add_argument('--concept-summaries', default=str(DEST / SUMMARIES_PATH))
    parser.add_argument('--anchor-registry', default=str(DEST / REGISTRY_PATH))
    parser.add_argument('--recall-layers', default=str(DEST / RECALL_LAYERS_PATH))
    parser.add_argument('--terms', default=str(DEST / TERMS_PATH))
    parser.add_argument('--figures', default=None)
    parser.add_argument('--figures-t23', default=None)
    parser.add_argument('--figures-t4', default=None)
    parser.add_argument('--figures-t5', default=None)
    parser.add_argument('--figures-t67', default=None)
    parser.add_argument('--chains', default=None)
    parser.add_argument('--extra-data', action='append', default=[])
    parser.add_argument('--repo-root', default=str(DEST))
    parser.add_argument('--masters-root', default=None)
    parser.add_argument('--out', default=str(DEST / OUTPUT_PATH))
    parser.add_argument('--manifest-out', default=str(DEST / MANIFEST_PATH))
    parser.add_argument('--check-only', action='store_true', help='Run the gates without writing the artifact')
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    masters_root = Path(args.masters_root) if args.masters_root else repo_root
    island_path = Path(args.island)
    if not island_path.is_absolute():
        island_path = repo_root / island_path
    conventions_path = Path(args.conventions)
    if not conventions_path.is_absolute():
        conventions_path = repo_root / conventions_path
    schema_path = Path(args.schema)
    if not schema_path.is_absolute():
        schema_path = repo_root / schema_path
    bank_path = Path(args.bank) if args.bank else None
    if bank_path is not None and not bank_path.is_absolute():
        bank_path = repo_root / bank_path
    golden_path = Path(args.golden_vectors)
    if not golden_path.is_absolute():
        golden_path = repo_root / golden_path
    tokens_path = Path(args.tokens)
    if not tokens_path.is_absolute():
        tokens_path = repo_root / tokens_path
    styles_path = Path(args.styles)
    if not styles_path.is_absolute():
        styles_path = repo_root / styles_path
    summaries_path = Path(args.concept_summaries)
    if not summaries_path.is_absolute():
        summaries_path = repo_root / summaries_path
    registry_path = Path(args.anchor_registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    layers_path = Path(args.recall_layers)
    if not layers_path.is_absolute():
        layers_path = repo_root / layers_path
    terms_path = Path(args.terms)
    if not terms_path.is_absolute():
        terms_path = repo_root / terms_path
    figures_path = Path(args.figures) if args.figures else None
    if figures_path is not None and not figures_path.is_absolute():
        figures_path = repo_root / figures_path
    figures_t23_path = Path(args.figures_t23) if args.figures_t23 else None
    if figures_t23_path is not None and not figures_t23_path.is_absolute():
        figures_t23_path = repo_root / figures_t23_path
    figures_t4_path = Path(args.figures_t4) if args.figures_t4 else None
    if figures_t4_path is not None and not figures_t4_path.is_absolute():
        figures_t4_path = repo_root / figures_t4_path
    figures_t5_path = Path(args.figures_t5) if args.figures_t5 else None
    if figures_t5_path is not None and not figures_t5_path.is_absolute():
        figures_t5_path = repo_root / figures_t5_path
    figures_t67_path = Path(args.figures_t67) if args.figures_t67 else None
    if figures_t67_path is not None and not figures_t67_path.is_absolute():
        figures_t67_path = repo_root / figures_t67_path
    chains_path = Path(args.chains) if args.chains else None
    if chains_path is not None and not chains_path.is_absolute():
        chains_path = repo_root / chains_path
    extra_data_paths = []
    for raw_ep in args.extra_data:
        ep = Path(raw_ep)
        if not ep.is_absolute():
            ep = repo_root / ep
        extra_data_paths.append(ep)
    if args.check_only:
        gates, reports = run_gates(
            island_path, repo_root, masters_root,
            conventions_path, schema_path, bank_path, golden_path,
            tokens_path, styles_path, summaries_path, registry_path, layers_path,
            terms_path, extra_data_paths, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path, chains_path,
        )
        if any(gate['status'] != 'PASS' for gate in gates):
            return 1
        print(format_coverage_summary(reports['coverage']))
        print(format_conventions_summary(reports['conventions']))
        print(format_bank_summary(reports['bank']))
        print(format_golden_summary(reports['golden_vectors']))
        print(format_tokens_summary(reports['tokens']))
        print(format_n07_summary(reports['concept_map']))
        print(format_n08_summary(reports['recall_layers']))
        print(format_terms_summary(reports['terminology']))
        print(format_figures_summary(reports['figures']))
        print(format_leak_summary(reports['figure_leak_scan']))
        print(format_chains_summary(reports['chains']))
        for gate in gates:
            print(f'  gate {gate["order"]}: {gate["id"]} ({gate["owner"]}) {gate["status"]}')
        return 0
    output_path = Path(args.out)
    if not output_path.is_absolute():
        output_path = repo_root / output_path
    manifest_path = Path(args.manifest_out)
    if not manifest_path.is_absolute():
        manifest_path = repo_root / manifest_path
    manifest = build(
        island_path, repo_root, masters_root, output_path, manifest_path,
        conventions_path, schema_path, bank_path, golden_path,
        tokens_path, styles_path, summaries_path, registry_path, layers_path,
        terms_path, extra_data_paths, figures_path, figures_t23_path, figures_t4_path, figures_t5_path, figures_t67_path, chains_path,
    )
    print(f'PASS build: {manifest["output"]} ({manifest["output_bytes"]} bytes, sha256={manifest["output_sha256"]})')
    print(f'  build id: {manifest["build_id"]}')
    print(f'  island: #sim-coverage {manifest["island"]["bytes"]} canonical bytes, sha256={manifest["island"]["digest"]}')
    print(f'  island: #sim-conventions {manifest["conventions_island"]["bytes"]} canonical bytes, sha256={manifest["conventions_island"]["digest"]}')
    print(f'  island: #sim-bank {manifest["bank_island"]["bytes"]} canonical bytes, sha256={manifest["bank_island"]["digest"]}')
    print(f'  island: #sim-golden-vectors {manifest["golden_vectors_island"]["bytes"]} canonical bytes, sha256={manifest["golden_vectors_island"]["digest"]}')
    print(f'  island: #sim-terms {manifest["terms_island"]["bytes"]} canonical bytes, sha256={manifest["terms_island"]["digest"]}')
    print(f'  island: #sim-figures {manifest["figures_island"]["bytes"]} canonical bytes, sha256={manifest["figures_island"]["digest"]}')
    print(f'  island: #sim-engines {manifest["engines_island"]["bytes"]} canonical bytes, sha256={manifest["engines_island"]["digest"]}')
    print(f'  island: #sim-graph-scoring {manifest["graph_scoring_island"]["bytes"]} canonical bytes, sha256={manifest["graph_scoring_island"]["digest"]}')
    print(f'  tokens: {manifest["tokens_layer"]["css_bytes"]} CSS bytes, sha256={manifest["tokens_layer"]["digest"]}')
    print(f'  concept_map: layout={manifest["concept_map_layer"]["layout_digest"][:16]}..., summaries={manifest["concept_map_layer"]["embedded_summaries_bytes"]}B, registry={manifest["concept_map_layer"]["embedded_registry_bytes"]}B')
    for gate in manifest['gates']:
        print(f'  gate {gate["order"]}: {gate["id"]} ({gate["owner"]}) {gate["status"]}')
    print(f'  manifest: {manifest_path} ({manifest_path.stat().st_size} bytes)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
