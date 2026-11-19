#!/usr/bin/env python3
"""N33 Static Accessibility, Keyboard Map, Focus, and ARIA Name-Role-Value Checker.

Implements:
  - Main Step A fixtures (keyboard map collision validation, drawer tab-escape
    over #concept-drawer, typing-context input-guard over numeric answer input)
  - Main Step B static semantic checks over output/simulator.html + N22
    18-component rendering:
      * B.1.1 Accessible name computation (aria-labelledby -> aria-label ->
        native <label> -> textContent -> title/placeholder/alt) + empty-label
        scratch fixture
      * B.1.2 Landmarks (9 Section 1.2 anchors, 1 <main>, unique <nav> labels)
        and per-view heading hierarchy without level skips + exam-map list rule
      * B.1.3 Live-region audit (timer_threshold=assertive, verdict_posted=polite,
        view_changed=polite) + single-announcement Node harness fixture

Also serves as Build Gate 30 (``a11y_contract``) in ``tools/build.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_SECTIONS = [
    "sakums",
    "saturs",
    "prakse",
    "eksamens",
    "rezultati",
    "atskats",
    "metodika",
    "druka",
    "iestatijumi",
]

LIVE_REGION_CONTRACT = {
    "timer_threshold": {"id": "sim-live-timer", "politeness": "assertive", "role": "alert"},
    "verdict_posted": {"id": "sim-live-verdict", "politeness": "polite", "role": "status"},
    "view_changed": {"id": "sim-live-view", "politeness": "polite", "role": "status"},
}

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class DOMNode:
    """Lightweight HTML DOM node for static a11y inspection."""

    def __init__(self, tag: str, attrs: dict[str, str], parent: DOMNode | None = None) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[DOMNode] = []
        self.text_parts: list[str] = []

    @property
    def id(self) -> str:
        return self.attrs.get("id", "")

    def collect_text(self) -> str:
        parts = list(self.text_parts)
        for ch in self.children:
            parts.append(ch.collect_text())
        return " ".join(p.strip() for p in parts if p and p.strip()).strip()


class DOMBuilder(HTMLParser):
    """Parse HTML into a DOMNode tree, skipping raw text inside script/style."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = DOMNode("document", {})
        self.stack: list[DOMNode] = [self.root]
        self.id_map: dict[str, DOMNode] = {}
        self.all_nodes: list[DOMNode] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t in ("script", "style"):
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return
        attr_dict = {k.lower(): ("" if v is None else str(v)) for k, v in attrs}
        parent = self.stack[-1]
        node = DOMNode(t, attr_dict, parent=parent)
        parent.children.append(node)
        self.all_nodes.append(node)
        if node.id and node.id not in self.id_map:
            self.id_map[node.id] = node
        if t not in VOID_TAGS:
            self.stack.append(node)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t in ("script", "style"):
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return
        if self._skip_depth > 0 or t in VOID_TAGS:
            return
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == t:
                del self.stack[idx:]
                break

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if data and data.strip():
            self.stack[-1].text_parts.append(data)


def parse_dom(html_text: str) -> DOMBuilder:
    builder = DOMBuilder()
    builder.feed(html_text)
    builder.close()
    return builder


def find_wrapping_label(node: DOMNode) -> DOMNode | None:
    cur = node.parent
    while cur is not None:
        if cur.tag == "label":
            return cur
        cur = cur.parent
    return None


def compute_accessible_name(
    node: DOMNode,
    id_map: dict[str, DOMNode],
    label_for_map: dict[str, DOMNode],
) -> tuple[str, str, str | None]:
    """Compute accessible name following ARIA precedence.

    Returns (name, source, error_or_None).
    """
    labelledby = node.attrs.get("aria-labelledby")
    if labelledby is not None:
        tokens = [tok for tok in labelledby.split() if tok]
        parts = []
        for tok in tokens:
            ref = id_map.get(tok)
            if ref is not None:
                txt = ref.collect_text()
                if txt:
                    parts.append(txt)
        resolved = " ".join(parts).strip()
        if resolved:
            return resolved, "aria-labelledby", None

    if "aria-label" in node.attrs:
        raw_label = node.attrs["aria-label"]
        if raw_label.strip() == "":
            ident = node.id or f"<{node.tag}>"
            return "", "aria-label", f'E_EMPTY_ARIA_LABEL: component "{ident}" has empty aria-label=""'
        return raw_label.strip(), "aria-label", None

    if node.id and node.id in label_for_map:
        lbl_text = label_for_map[node.id].collect_text()
        if lbl_text:
            return lbl_text, "label[for]", None

    wrap_lbl = find_wrapping_label(node)
    if wrap_lbl is not None:
        lbl_text = wrap_lbl.collect_text()
        if lbl_text:
            return lbl_text, "label[wrapping]", None

    text = node.collect_text()
    if text:
        return text, "textContent", None

    for fallback_attr in ("title", "placeholder", "alt"):
        val = node.attrs.get(fallback_attr, "").strip()
        if val:
            return val, fallback_attr, None

    return "", "none", f'E_MISSING_ACCESSIBLE_NAME: interactive <{node.tag} id="{node.id}"> has no accessible name'


def is_interactive_element(node: DOMNode) -> bool:
    if node.tag == "button":
        return True
    if node.tag == "a" and "href" in node.attrs:
        return True
    if node.tag == "input" and node.attrs.get("type", "").lower() != "hidden":
        return True
    if node.tag in ("select", "textarea"):
        return True
    role = node.attrs.get("role", "").lower()
    if role in ("button", "radio", "tab", "checkbox", "link", "slider", "combobox"):
        return True
    if node.attrs.get("tabindex") == "0":
        return True
    return False


def audit_html_semantics(html_text: str) -> dict[str, Any]:
    dom = parse_dom(html_text)
    label_for_map: dict[str, DOMNode] = {}
    for n in dom.all_nodes:
        if n.tag == "label" and "for" in n.attrs:
            label_for_map[n.attrs["for"]] = n

    # 1. Interactive elements & name table
    interactive_entries: list[dict[str, Any]] = []
    name_errors: list[str] = []
    for n in dom.all_nodes:
        if not is_interactive_element(n):
            continue
        name, source, err = compute_accessible_name(n, dom.id_map, label_for_map)
        role = n.attrs.get("role") or n.tag
        entry = {
            "id": n.id or None,
            "tag": n.tag,
            "role": role,
            "name": name,
            "name_source": source,
            "term_key": n.attrs.get("data-term-key"),
        }
        interactive_entries.append(entry)
        if err:
            name_errors.append(err)

    # 2. Landmarks & 9 required sections
    mains = [n for n in dom.all_nodes if n.tag == "main" or n.attrs.get("role") == "main"]
    navs = [n for n in dom.all_nodes if n.tag == "nav"]
    nav_labels = [n.attrs.get("aria-label", "").strip() for n in navs]
    missing_nav_labels = [n.id or "<nav>" for n in navs if not n.attrs.get("aria-label", "").strip()]

    section_results: list[dict[str, Any]] = []
    section_errors: list[str] = []
    for sec_id in REQUIRED_SECTIONS:
        sec = dom.id_map.get(sec_id)
        if sec is None or sec.tag != "section":
            section_errors.append(f"Missing required <section id='{sec_id}'>")
            continue
        lbl_id = sec.attrs.get("aria-labelledby", "").strip()
        lbl_node = dom.id_map.get(lbl_id) if lbl_id else None
        heading_text = lbl_node.collect_text() if lbl_node else ""
        if not lbl_id or not heading_text:
            section_errors.append(f"Section #{sec_id} missing valid aria-labelledby heading")
        section_results.append({
            "id": sec_id,
            "aria_labelledby": lbl_id,
            "heading_text": heading_text,
        })

    # 3. Heading hierarchy per section (no level skips)
    heading_skips: list[dict[str, Any]] = []
    h1_count = sum(1 for n in dom.all_nodes if n.tag == "h1")
    for sec_id in REQUIRED_SECTIONS + ["piemeri"]:
        sec = dom.id_map.get(sec_id)
        if sec is None:
            continue
        sec_headings: list[tuple[int, str]] = []

        def _walk_h(node: DOMNode) -> None:
            if node.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
                sec_headings.append((int(node.tag[1]), node.id or node.collect_text()[:40]))
            for ch in node.children:
                _walk_h(ch)

        _walk_h(sec)
        prev_lvl = None
        for lvl, ident in sec_headings:
            if prev_lvl is not None and lvl > prev_lvl + 1:
                heading_skips.append({
                    "section": sec_id,
                    "from_level": prev_lvl,
                    "to_level": lvl,
                    "heading": ident,
                })
            prev_lvl = lvl

    # 4. Live-region audit
    live_region_results: dict[str, Any] = {}
    live_errors: list[str] = []
    for event_name, expected in LIVE_REGION_CONTRACT.items():
        node = dom.id_map.get(expected["id"])
        if node is None:
            live_errors.append(f"Missing live region #{expected['id']} for event {event_name}")
            continue
        pol = node.attrs.get("aria-live", "")
        role = node.attrs.get("role", "")
        ok = (pol == expected["politeness"] and role == expected["role"])
        if not ok:
            live_errors.append(
                f"Live region #{expected['id']} mismatch: got aria-live={pol!r} role={role!r}, "
                f"expected aria-live={expected['politeness']!r} role={expected['role']!r}"
            )
        live_region_results[event_name] = {
            "id": expected["id"],
            "politeness": pol,
            "role": role,
            "pass": ok,
        }

    exam_timer_bar = dom.id_map.get("exam-timer-bar")
    if exam_timer_bar and "aria-live" in exam_timer_bar.attrs:
        live_errors.append("#exam-timer-bar still carries aria-live (risks double announcement with #sim-live-timer)")

    landmarks_pass = (
        len(mains) == 1
        and len(missing_nav_labels) == 0
        and len(section_errors) == 0
        and h1_count == 1
        and len(heading_skips) == 0
    )

    return {
        "interactive_count": len(interactive_entries),
        "interactive_controls": interactive_entries,
        "name_errors": name_errors,
        "landmarks": {
            "main_count": len(mains),
            "nav_count": len(navs),
            "nav_labels": nav_labels,
            "missing_nav_labels": missing_nav_labels,
            "required_sections": section_results,
            "section_errors": section_errors,
            "h1_count": h1_count,
            "heading_skips": heading_skips,
            "exam_navigator_list_rule": (
                "Repeated question summary buttons in #exam-map/#exam-navigator "
                "carry numbered item labels inside a declared group/list container "
                "and are intentionally permitted as list items."
            ),
            "pass": landmarks_pass,
        },
        "live_regions": {
            "channels": live_region_results,
            "errors": live_errors,
            "pass": len(live_errors) == 0,
        },
    }


def run_node_n33_suite(repo_root: Path) -> dict[str, Any]:
    """Run Node verification for:
    - 18 N22 response components (Q01-Q18) name-role-value table
    - Keyboard map validation + scratch collision fixture
    - Focus escape fixture over #concept-drawer
    - Typing-context input-guard fixture over numeric input
    - Live-region single-announcement fixture (each event fires once)
    """
    node_script = r"""
const fs = require('fs');
const path = require('path');
const root = process.argv[1];

const SimFocus = require(path.join(root, 'src/compiled/focus.js'));
const SimTerms = require(path.join(root, 'src/terms-loader.js'));
const SimInputsReg = require(path.join(root, 'src/compiled/inputs/registry.js'));
const SimInputsComp = require(path.join(root, 'src/compiled/inputs/components.js'));

const termsData = JSON.parse(fs.readFileSync(path.join(root, 'data/terms.json'), 'utf8'));
const rtData = JSON.parse(fs.readFileSync(path.join(root, 'data/response_types.json'), 'utf8'));
const kmData = JSON.parse(fs.readFileSync(path.join(root, 'data/keyboard_map.json'), 'utf8'));

// 1. Validate data/keyboard_map.json
const mapValidation = SimFocus.validateKeyboardMap(kmData);

// 2. Scratch collision fixture (A.1.1)
let collisionCaught = false;
let collisionMessage = '';
try {
  const scratchMap = JSON.parse(JSON.stringify(kmData));
  scratchMap.context_shortcuts.exam.push({
    key: 'n',
    action: 'exam_note_scratch',
    target: '#exam-note'
  });
  SimFocus.validateKeyboardMap(scratchMap);
} catch (err) {
  collisionCaught = (err && err.code === 'E_KEYMAP_COLLISION');
  collisionMessage = err ? String(err.message) : '';
}
const collisionFixturePass = collisionCaught
  && collisionMessage.indexOf('"n"') !== -1
  && collisionMessage.indexOf('exam_next') !== -1
  && collisionMessage.indexOf('exam_note_scratch') !== -1;

// 3. Minimal mock DOM for focus escape (A.1.2), typing-guard (A.1.3), and live regions (B.1.3)
function makeEl(tag, id, attrs) {
  const el = {
    tagName: tag.toUpperCase(),
    id: id || '',
    attrs: Object.assign({}, attrs || {}),
    children: [],
    parentNode: null,
    hidden: false,
    disabled: false,
    textContent: '',
    value: '',
    getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null; },
    setAttribute(k, v) { this.attrs[k] = String(v); },
    removeAttribute(k) { delete this.attrs[k]; },
    focus() { mockDoc.activeElement = this; },
    click() { this._clicked = (this._clicked || 0) + 1; },
    querySelectorAll(sel) {
      const res = [];
      const walk = (n) => {
        for (const ch of n.children) {
          if (['A', 'BUTTON', 'INPUT', 'SELECT', 'TEXTAREA'].indexOf(ch.tagName) !== -1 || ch.getAttribute('tabindex') !== null) {
            res.push(ch);
          }
          walk(ch);
        }
      };
      walk(this);
      return res;
    },
    querySelector(sel) {
      const idMatch = sel.match(/^#([a-zA-Z0-9_-]+)$/);
      if (idMatch) return mockDoc.getElementById(idMatch[1]);
      return null;
    }
  };
  if (el.attrs.type) el.type = el.attrs.type;
  return el;
}

const byId = Object.create(null);
const mockDoc = {
  activeElement: null,
  body: makeEl('body', 'body'),
  getElementById(id) { return byId[id] || null; },
  querySelector(sel) {
    const m = sel.match(/^#([a-zA-Z0-9_-]+)$/);
    return m ? (byId[m[1]] || null) : null;
  },
  querySelectorAll(sel) { return this.body.querySelectorAll(sel); }
};

function addChild(parent, child) {
  child.parentNode = parent;
  parent.children.push(child);
  if (child.id) byId[child.id] = child;
  return child;
}

// Build mock sections, live regions, #concept-drawer, and post-drawer focusable element
const liveTimer = addChild(mockDoc.body, makeEl('div', 'sim-live-timer', { 'aria-live': 'assertive', role: 'alert' }));
const liveVerdict = addChild(mockDoc.body, makeEl('div', 'sim-live-verdict', { 'aria-live': 'polite', role: 'status' }));
const liveView = addChild(mockDoc.body, makeEl('div', 'sim-live-view', { 'aria-live': 'polite', role: 'status' }));
const satursSec = addChild(mockDoc.body, makeEl('section', 'saturs'));
const satursHeading = addChild(satursSec, makeEl('h2', 'saturs-virsraksts'));
satursHeading.textContent = 'Mācību mērķi';
const mapNodeTrigger = addChild(satursSec, makeEl('button', 'concept-node-T1-01'));
const numInput = addChild(satursSec, makeEl('input', 'q01-numeric-answer', { type: 'number' }));

const conceptDrawer = addChild(mockDoc.body, makeEl('aside', 'concept-drawer', { role: 'dialog', 'aria-modal': 'true' }));
conceptDrawer.hidden = true;
const drawerClose = addChild(conceptDrawer, makeEl('button', 'concept-drawer-close'));
const drawerLink = addChild(conceptDrawer, makeEl('a', 'concept-drawer-prereq-1', { href: '#saturs' }));
const drawerPracticeBtn = addChild(conceptDrawer, makeEl('button', 'concept-drawer-practice-link'));

const footerBtn = addChild(mockDoc.body, makeEl('button', 'post-drawer-next-control'));

// 3a. Focus escape & restore fixture (A.1.2)
SimFocus.resetForTest();
const escapeTrace = SimFocus.walkTabSequence(mockDoc, 'concept-drawer', mapNodeTrigger);
const restoredId = SimFocus.closeDrawer(mockDoc, 'concept-drawer');
const focusEscapeFixturePass = escapeTrace.insideIds.length === 3
  && escapeTrace.escapedOutsideDrawer === true
  && escapeTrace.escapedToId === 'post-drawer-next-control'
  && restoredId === 'concept-node-T1-01'
  && mockDoc.activeElement === mapNodeTrigger;

// 3b. Typing-context input-guard fixture (A.1.3)
SimFocus.resetForTest();
SimFocus.setContext('exam');
numInput.focus();
let prevented = false;
const typingResult = SimFocus.handleKeyDown(
  mockDoc,
  { key: 't', ctrlKey: false, altKey: false, metaKey: false, preventDefault() { prevented = true; } },
  { activeElement: numInput }
);
const typingFixturePass = typingResult.handled === false
  && typingResult.suppressed === true
  && typingResult.reason === 'typing_context'
  && prevented === false
  && SimFocus.getContext() === 'exam';

// 3c. Live-region single-announcement fixture (B.1.3)
SimFocus.resetForTest();
SimFocus.announce(mockDoc, 'timer_threshold', 'Atlikušas 15 minūtes.');
SimFocus.announce(mockDoc, 'verdict_posted', 'Atbilde ir pareiza.');
SimFocus.announce(mockDoc, 'view_changed', 'Skats: Eksāmena simulācija');
const anns = SimFocus.getAnnouncements();
const byChannel = { timer_threshold: 0, verdict_posted: 0, view_changed: 0 };
for (const a of anns) {
  if (Object.prototype.hasOwnProperty.call(byChannel, a.channel)) byChannel[a.channel] += 1;
}
const liveFixturePass = anns.length === 3
  && byChannel.timer_threshold === 1
  && byChannel.verdict_posted === 1
  && byChannel.view_changed === 1
  && liveTimer.getAttribute('aria-live') === 'assertive'
  && liveVerdict.getAttribute('aria-live') === 'polite'
  && liveView.getAttribute('aria-live') === 'polite';

// 4. N22 18-component name-role-value table (B.1.1)
SimInputsReg.load(rtData, termsData);
const regContracts = SimInputsReg.contracts || rtData.types;
const scratchFixPath = path.join(root, 'tools/fixtures/n22/scratch_instances.json');
const scratchFix = fs.existsSync(scratchFixPath) ? JSON.parse(fs.readFileSync(scratchFixPath, 'utf8')) : { fixture_questions: {}, instances: {} };
const bankDir = path.join(root, 'data/bank');
const bankById = Object.create(null);
if (fs.existsSync(bankDir)) {
  for (const f of fs.readdirSync(bankDir)) {
    if (!f.endsWith('.json')) continue;
    const data = JSON.parse(fs.readFileSync(path.join(bankDir, f), 'utf8'));
    const list = Array.isArray(data) ? data : (data.instances || data.questions || []);
    for (const q of list) {
      if (q && q.question_id) bankById[q.question_id] = q;
    }
  }
}
const figuresList = [];
for (const f of ['figures_t12.json', 'figures_t23.json', 'figures_t4.json', 'figures_t5.json', 'figures_t67.json']) {
  const fp = path.join(root, 'data', f);
  if (fs.existsSync(fp)) {
    const fd = JSON.parse(fs.readFileSync(fp, 'utf8'));
    const items = fd.figures || [];
    for (const fig of items) {
      figuresList.push(fig);
    }
  }
}
const figures = figuresList;
const typeIds = Object.keys(rtData.types).sort();
const componentRows = [];
for (const typeId of typeIds) {
  const contract = regContracts[typeId] || rtData.types[typeId];
  const qid = (scratchFix.fixture_questions || {})[typeId];
  let instance = qid && bankById[qid] ? bankById[qid] : null;
  if (!instance && qid && scratchFix.instances) {
    for (const k of Object.keys(scratchFix.instances)) {
      if (scratchFix.instances[k] && scratchFix.instances[k].question_id === qid) {
        instance = scratchFix.instances[k];
        break;
      }
    }
  }
  if (!instance) {
    instance = { question_id: 'SAMPLE-' + typeId, type_id: typeId, prompt_lv: 'Parauga jautājums ' + typeId, payload: {} };
  }
  const desc = SimInputsComp.render(typeId, contract, instance, null, termsData, {
    figures: figures,
    capture_context_id: typeId === 'Q11' ? 'CAP-T4-KINETICS-SLOPE' : undefined
  });
  const fields = (desc.fields || []).map((f) => ({
    field_id: f.field_id,
    role: f.role,
    control: f.control,
    computed_name: f.aria_name,
    state: f.state,
    state_text: f.state_text,
    non_empty_name: typeof f.aria_name === 'string' && f.aria_name.trim().length > 0,
  }));
  const groupName = desc.name_text_lv || '';
  const allFieldsNamed = fields.length > 0 && fields.every((f) => f.non_empty_name);
  componentRows.push({
    type_id: typeId,
    name_key: contract.name_key,
    computed_name: groupName,
    labelledby: desc.labelledby,
    describedby: desc.describedby,
    field_count: fields.length,
    fields: fields,
    non_empty_name: typeof groupName === 'string' && groupName.trim().length > 0 && allFieldsNamed,
  });
}

console.log(JSON.stringify({
  map_validation: mapValidation,
  collision_fixture: { pass: collisionFixturePass, message: collisionMessage },
  focus_escape_fixture: { pass: focusEscapeFixturePass, trace: escapeTrace, restored_id: restoredId },
  typing_fixture: { pass: typingFixturePass, result: typingResult },
  live_fixture: { pass: liveFixturePass, counts: byChannel },
  components_18: componentRows
}));
"""
    proc = subprocess.run(
        ["node", "-e", node_script, str(repo_root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Node N33 suite failed (rc={proc.returncode}): {proc.stderr or proc.stdout}")
    return json.loads(proc.stdout)


def run_empty_label_scratch_fixture() -> dict[str, Any]:
    """B.1.1 corner-case scratch fixture: empty aria-label="" fails naming component."""
    scratch_html = '<button id="scratch-icon-flag" type="button" aria-label=""></button>'
    dom = parse_dom(scratch_html)
    btn = dom.id_map["scratch-icon-flag"]
    name, source, err = compute_accessible_name(btn, dom.id_map, {})
    passed = (
        err is not None
        and "scratch-icon-flag" in err
        and 'aria-label=""' in err
        and name == ""
        and source == "aria-label"
    )
    return {
        "pass": passed,
        "component": "scratch-icon-flag",
        "error": err,
    }


def validate_n33_contract(
    repo_root: Path = ROOT,
    html_path: Path | None = None,
) -> dict[str, Any]:
    target_html = html_path or (repo_root / "output" / "simulator.html")
    if not target_html.exists():
        target_html = repo_root / "src" / "shell.html"
    html_text = target_html.read_text(encoding="utf-8")

    static_audit = audit_html_semantics(html_text)
    node_suite = run_node_n33_suite(repo_root)
    empty_label_fixture = run_empty_label_scratch_fixture()

    all_18_pass = len(node_suite["components_18"]) == 18 and all(
        c["non_empty_name"] for c in node_suite["components_18"]
    )
    overall_pass = (
        len(static_audit["name_errors"]) == 0
        and static_audit["landmarks"]["pass"]
        and static_audit["live_regions"]["pass"]
        and node_suite["map_validation"]["valid"]
        and node_suite["collision_fixture"]["pass"]
        and node_suite["focus_escape_fixture"]["pass"]
        and node_suite["typing_fixture"]["pass"]
        and node_suite["live_fixture"]["pass"]
        and empty_label_fixture["pass"]
        and all_18_pass
    )

    return {
        "schema_version": 1,
        "owner_task": "N33",
        "target_html": str(target_html.relative_to(repo_root)) if target_html.is_relative_to(repo_root) else str(target_html),
        "status": "PASS" if overall_pass else "FAIL",
        "static_audit": static_audit,
        "node_suite": node_suite,
        "empty_label_fixture": empty_label_fixture,
        "all_18_response_types_pass": all_18_pass,
    }


def format_summary(report: dict[str, Any]) -> str:
    sa = report["static_audit"]
    ns = report["node_suite"]
    return (
        f"a11y_contract {report['status']}: "
        f"controls={sa['interactive_count']} name_errors={len(sa['name_errors'])} "
        f"components_18={len(ns['components_18'])}/18 "
        f"landmarks={sa['landmarks']['pass']} live_regions={sa['live_regions']['pass']} "
        f"collision_fix={ns['collision_fixture']['pass']} "
        f"escape_fix={ns['focus_escape_fixture']['pass']} "
        f"typing_fix={ns['typing_fixture']['pass']} "
        f"empty_label_fix={report['empty_label_fixture']['pass']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="N33 A11y, Keyboard Map, and Focus Contract Checker")
    parser.add_argument("--html", type=Path, default=None, help="Path to HTML file (default: output/simulator.html)")
    parser.add_argument("--json-out", type=Path, default=None, help="Write full JSON report to this path")
    args = parser.parse_args(argv)

    report = validate_n33_contract(ROOT, args.html)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(format_summary(report))
    if report["status"] != "PASS":
        if report["static_audit"]["name_errors"]:
            print("Name errors:", report["static_audit"]["name_errors"][:5], file=sys.stderr)
        if report["static_audit"]["landmarks"]["section_errors"]:
            print("Section errors:", report["static_audit"]["landmarks"]["section_errors"], file=sys.stderr)
        if report["static_audit"]["landmarks"]["heading_skips"]:
            print("Heading skips:", report["static_audit"]["landmarks"]["heading_skips"], file=sys.stderr)
        if report["static_audit"]["live_regions"]["errors"]:
            print("Live region errors:", report["static_audit"]["live_regions"]["errors"], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
