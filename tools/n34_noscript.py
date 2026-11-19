#!/usr/bin/env python3
"""N34 single-sourced <noscript> fallback HTML generator.

Generates the static no-JavaScript fallback block directly from the same
canonical JSON islands embedded in output/simulator.html (coverage,
anchor_registry, concept_summaries, conventions, terms) so no drift can occur
between runtime islands and static HTML.
"""
from __future__ import annotations

import html
from typing import Any


def _esc(value: Any) -> str:
    if value is None:
        return ''
    return html.escape(str(value), quote=True)


def _term_text(terms_by_key: dict[str, dict[str, Any]], key: str) -> str:
    entry = terms_by_key.get(key)
    if not entry:
        raise KeyError(f'Missing required noscript term key in terms island: {key!r}')
    text = str(entry.get('text_lv') or '').strip()
    if not text:
        raise ValueError(f'Empty text_lv for noscript term key {key!r}')
    return text


def render_noscript_html(
    coverage: dict[str, Any],
    anchor_registry: dict[str, Any],
    concept_summaries: dict[str, Any],
    conventions: dict[str, Any],
    terms_data: dict[str, Any],
) -> str:
    """Render compact, single-sourced <noscript> fallback HTML."""
    terms_list = terms_data.get('terms') or []
    terms_by_key = {str(t.get('key')): t for t in terms_list if isinstance(t, dict) and t.get('key')}

    notice_text = _term_text(terms_by_key, 'noscript.notice')
    limits_text = _term_text(terms_by_key, 'noscript.limits')

    outcomes_by_id = {
        str(o.get('id')): o for o in (coverage.get('outcomes') or []) if isinstance(o, dict) and o.get('id')
    }
    summaries_by_id = {
        str(c.get('id')): c for c in (concept_summaries.get('concepts') or []) if isinstance(c, dict) and c.get('id')
    }
    anchors_by_id = {
        str(c.get('concept_id')): c for c in (anchor_registry.get('concepts') or []) if isinstance(c, dict) and c.get('concept_id')
    }

    parts: list[str] = [
        '<noscript id="sim-noscript-fallback" class="noscript-fallback">',
        f'<div id="noscript-pazinojums" class="noscript-notice" role="status" data-term-key="noscript.notice"><p><strong>Bez-skripta režīms:</strong> {_esc(notice_text)}</p><p>Skatīt arī: <a href="#noscript-saturs-karte">Jēdzienu karte</a> | <a href="#noscript-metodika">Metodika</a> | <a href="#noscript-termini">Terminu saraksts</a> | <a href="#druka">Druka (#druka)</a> | <a href="#noscript-ierobezojumi">Ierobežojumi</a>.</p></div>',
    ]

    # 1. Concept map as nested lists with N07 ASCII anchors preserved
    parts.append('<section id="noscript-saturs-karte" class="sim-section noscript-section" aria-labelledby="noscript-karte-virsraksts">')
    parts.append('<h2 id="noscript-karte-virsraksts">Programmas jēdzienu karte (statisks pārskats)</h2>')
    parts.append('<ol class="noscript-topic-list">')
    for topic in coverage.get('topics') or []:
        t_num = topic.get('topic')
        t_name = topic.get('official_heading') or topic.get('name_lv') or f'{t_num}. tēma'
        t_anchor = f'#karte-tema-{t_num}'
        parts.append(f'<li><p><strong><a href="{_esc(t_anchor)}">{_esc(t_name)}</a></strong></p><ul class="noscript-concept-list">')
        for oid in topic.get('outcome_ids') or []:
            oid_str = str(oid)
            anchor_rec = anchors_by_id.get(oid_str, {})
            node_id = str(anchor_rec.get('map_node_id') or f'karte-{oid_str}')
            outcome = outcomes_by_id.get(oid_str, {})
            summary = summaries_by_id.get(oid_str, {})
            heading = anchor_rec.get('master_heading_lv') or outcome.get('master_heading_lv') or oid_str
            stmt = outcome.get('statement_lv') or ''
            sum_txt = summary.get('summary_lv') or ''
            dissent = summary.get('dissent_note_lv') or ''
            prereq_edges = anchor_rec.get('prerequisite_edges') or []
            prereq_links = ' '.join(
                f'<a href="{_esc(edge.get("target_anchor") or ("#karte-" + str(edge.get("from"))))}">{_esc(edge.get("from"))}</a>'
                for edge in prereq_edges
                if isinstance(edge, dict) and edge.get('from')
            )
            prereq_html = f' <span>Priekšnosacījumi: {prereq_links}.</span>' if prereq_links else ''
            dissent_html = f' <span>Avotu atšķirība: {_esc(dissent)}</span>' if dissent else ''
            parts.append(
                f'<li id="{_esc(node_id)}"><strong>{_esc(oid_str)} — {_esc(heading)}</strong>: {_esc(stmt)}'
                f'{(" " + _esc(sum_txt)) if sum_txt else ""}{prereq_html}{dissent_html}</li>'
            )
        parts.append('</ul></li>')
    parts.append('</ol></section>')

    # 2. Methodology & conventions summary
    parts.append('<section id="noscript-metodika" class="sim-section noscript-section" aria-labelledby="noscript-metodika-virsraksts">')
    parts.append('<h2 id="noscript-metodika-virsraksts">Metodika un zinātniskās konvencijas</h2>')
    official_facts = coverage.get('official_facts') or []
    training_policy = coverage.get('training_policy') or []
    official_summary = '; '.join(
        str(item.get('statement_lv') or '') for item in official_facts if isinstance(item, dict) and item.get('statement_lv')
    )
    policy_summary = '; '.join(
        str(item.get('statement_lv') or '') for item in training_policy if isinstance(item, dict) and item.get('statement_lv')
    )
    parts.append(
        f'<p><strong>Oficiālie fakti (PROGRAMME-SOURCED):</strong> {_esc(official_summary or "7 tēmas, rakstisks eksāmens uz papīra, maksimums 180 minūtes.")}</p>'
    )
    parts.append(
        f'<p><strong>Treniņpolitikas ietvars (PROPOSED):</strong> {_esc(policy_summary or "100 punktu skala, 21 uzdevumu slots formā (A, B, C).")}</p>'
    )
    conv_rules = conventions.get('rules') or conventions.get('entries') or []
    parts.append(
        f'<p><strong>Zinātniskās konvencijas:</strong> iegultajā konvenciju salā ir fiksētas {_esc(len(conv_rules))} kanoniskās normas '
        '(procentu bāzes w/w, w/v, v/v; zīmīgo ciparu noteikumi; standartkonstantes; avotu pretrunu reģistrs). '
        'Skatīt arī <a href="#metodika">metodikas sadaļu</a> un <a href="#druka">drukas sadaļu</a>.</p>'
    )
    parts.append('</section>')

    # 3. Full terminology reference table single-sourced from #sim-terms
    parts.append('<section id="noscript-termini" class="sim-section noscript-section" aria-labelledby="noscript-termini-virsraksts">')
    parts.append(f'<h2 id="noscript-termini-virsraksts">Terminoloģijas un mērvienību saraksts ({len(terms_list)} ieraksti)</h2>')
    parts.append('<table class="noscript-terms-table"><thead><tr><th>Atslēga</th><th>Termins</th><th>Saīsinājums</th><th>Mērvienība</th></tr></thead><tbody>')
    for term in terms_list:
        if not isinstance(term, dict):
            continue
        k = _esc(term.get('key'))
        txt = _esc(term.get('text_lv'))
        abbr = _esc(term.get('abbr') or '—')
        unit = _esc(term.get('unit') or '—')
        parts.append(f'<tr><td><code>{k}</code></td><td>{txt}</td><td>{abbr}</td><td>{unit}</td></tr>')
    parts.append('</tbody></table></section>')

    # 4. Honest limits
    parts.append('<section id="noscript-ierobezojumi" class="sim-section noscript-section" aria-labelledby="noscript-ierobezojumi-virsraksts">')
    parts.append('<h2 id="noscript-ierobezojumi-virsraksts">Bez-skripta režīma godīgie ierobežojumi</h2>')
    parts.append(f'<p class="noscript-limits" data-term-key="noscript.limits">{_esc(limits_text)}</p>')
    parts.append('<p>Papīra drukai izmantojiet pārlūka drukas komandu (<code>Ctrl+P</code>) vai pārejiet uz <a href="#druka">drukas sadaļu</a>.</p>')
    parts.append('</section>')

    parts.append('</noscript>')
    return '\n'.join(parts)
