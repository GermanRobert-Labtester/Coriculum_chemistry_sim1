/* N34 Paper Worksheet Generator & Print Mode (F04).
 * Pure, deterministic worksheet generation from #sim-forms and #sim-bank.
 * Strict TypeScript (ES2018, no DOM lib).
 */

interface PaperFormSlot {
  slot_id: string;
  topic: number;
  family_id: string;
  instance_id: string;
  points: number;
  rubric_points?: number;
  type_id: string;
  type_ids?: string[];
  variant_id?: string;
  figure_id?: string;
}

interface PaperConflict {
  id: string;
  slot_id?: string;
  family_id?: string;
  instance_id?: string;
  note_lv?: string;
  slot_points?: number;
  rubric_points?: number;
}

interface PaperFormRecord {
  form_id: string;
  status?: string;
  epistemic_label?: string;
  form_seed?: string;
  total_points?: number;
  total_slots?: number;
  topic_subtotals?: Record<string, { points: number; slots: number }>;
  conflicts?: PaperConflict[];
  slots?: PaperFormSlot[];
}

interface PaperFormsIsland {
  forms?: Record<string, PaperFormRecord> | PaperFormRecord[];
}

interface PaperBankInstance {
  id?: string;
  instance_id?: string;
  prompt_lv?: string;
  stem_lv?: string;
  title_lv?: string;
  figure_id?: string;
}

interface PaperBankIsland {
  instances?: PaperBankInstance[];
}

interface PaperWorksheetSlot {
  slot_id: string;
  topic: number;
  points: number;
  rubric_points: number;
  type_id: string;
  family_id: string;
  variant_id: string;
  instance_id: string;
  figure_id: string;
  stem_lv: string;
  blank_kind: 'short' | 'tall';
}

interface PaperWorksheetModel {
  form_id: string;
  epistemic_label: string;
  total_points: number;
  total_slots: number;
  topic_subtotals: Array<{ topic: number; slots: number; points: number }>;
  conflicts: PaperConflict[];
  slots: PaperWorksheetSlot[];
}

interface PaperInitOptions {
  forms?: PaperFormsIsland | null;
  bank?: PaperBankIsland | null;
}

interface PaperElement {
  id?: string;
  textContent?: string | null;
  innerHTML: string;
  value?: string;
  disabled?: boolean;
  addEventListener?(event: string, listener: () => void): void;
}

interface PaperDocument {
  getElementById(id: string): PaperElement | null;
  documentElement?: {
    classList?: {
      add(cls: string): void;
      remove(cls: string): void;
      contains(cls: string): boolean;
    };
  } | null;
}

interface SimPaperApi {
  readonly VERSION: string;
  getAvailableForms(formsIsland: PaperFormsIsland | null | undefined): PaperFormRecord[];
  buildWorksheetModel(
    formsIsland: PaperFormsIsland | null | undefined,
    bankIsland: PaperBankIsland | null | undefined,
    formId: string
  ): PaperWorksheetModel | null;
  renderWorksheetHTML(model: PaperWorksheetModel | null): string;
  renderEmptyStateHTML(): string;
  applyPrintTheme(doc: PaperDocument, enabled: boolean): boolean;
  init(doc: PaperDocument, opts?: PaperInitOptions): { availableForms: string[]; activeForm: string | null };
}

(function (root: Record<string, unknown>): void {
  'use strict';

  const TALL_TYPES: Record<string, boolean> = {
    Q02: true,
    Q03: true,
    Q08: true,
    Q11: true,
    Q13: true,
    Q15: true,
    Q16: true,
    Q17: true,
    Q18: true
  };

  function escapeHtml(raw: unknown): string {
    const simStore = (root as any).SimStore;
    if (simStore && typeof simStore.escapeHtml === 'function') {
      return simStore.escapeHtml(raw);
    }
    const s = raw === null || raw === undefined ? '' : String(raw);
    return s
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function readJsonIsland(doc: PaperDocument, id: string): unknown {
    const el = doc.getElementById(id);
    if (!el || typeof el.textContent !== 'string') {
      return null;
    }
    const raw = el.textContent.trim();
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw);
    } catch (_err) {
      return null;
    }
  }

  function extractFormMap(formsIsland: PaperFormsIsland | null | undefined): Record<string, PaperFormRecord> {
    const out: Record<string, PaperFormRecord> = {};
    if (!formsIsland || typeof formsIsland !== 'object') {
      return out;
    }
    const raw = formsIsland.forms;
    if (Array.isArray(raw)) {
      for (let i = 0; i < raw.length; i += 1) {
        const rec = raw[i];
        if (rec && typeof rec.form_id === 'string' && rec.form_id) {
          out[rec.form_id] = rec;
        }
      }
    } else if (raw && typeof raw === 'object') {
      const keys = Object.keys(raw);
      for (let i = 0; i < keys.length; i += 1) {
        const k = keys[i];
        const rec = (raw as Record<string, PaperFormRecord>)[k];
        if (rec && typeof rec === 'object') {
          const fid = typeof rec.form_id === 'string' && rec.form_id ? rec.form_id : k;
          out[fid] = rec;
        }
      }
    }
    return out;
  }

  function getAvailableForms(formsIsland: PaperFormsIsland | null | undefined): PaperFormRecord[] {
    const map = extractFormMap(formsIsland);
    const keys = Object.keys(map).sort();
    const result: PaperFormRecord[] = [];
    for (let i = 0; i < keys.length; i += 1) {
      const rec = map[keys[i]];
      if (
        rec &&
        rec.status === 'AVAILABLE' &&
        Array.isArray(rec.slots) &&
        rec.slots.length > 0
      ) {
        result.push(rec);
      }
    }
    return result;
  }

  function indexBankById(bankIsland: PaperBankIsland | null | undefined): Record<string, PaperBankInstance> {
    const map: Record<string, PaperBankInstance> = {};
    if (!bankIsland || !Array.isArray(bankIsland.instances)) {
      return map;
    }
    for (let i = 0; i < bankIsland.instances.length; i += 1) {
      const bankItem: PaperBankInstance = bankIsland.instances[i];
      if (!bankItem || typeof bankItem !== 'object') {
        continue;
      }
      const id = typeof bankItem.instance_id === 'string' && bankItem.instance_id
        ? bankItem.instance_id
        : (typeof bankItem.id === 'string' ? bankItem.id : '');
      if (id) {
        map[id] = bankItem;
      }
    }
    return map;
  }

  function buildWorksheetModel(
    formsIsland: PaperFormsIsland | null | undefined,
    bankIsland: PaperBankIsland | null | undefined,
    formId: string
  ): PaperWorksheetModel | null {
    const available = getAvailableForms(formsIsland);
    let target: PaperFormRecord | null = null;
    for (let i = 0; i < available.length; i += 1) {
      if (available[i].form_id === formId) {
        target = available[i];
        break;
      }
    }
    if (!target || !Array.isArray(target.slots)) {
      return null;
    }

    const bankById = indexBankById(bankIsland);
    const slots: PaperWorksheetSlot[] = [];
    for (let i = 0; i < target.slots.length; i += 1) {
      const s = target.slots[i];
      const inst = bankById[s.instance_id];
      const stem = inst
        ? String(inst.prompt_lv || inst.stem_lv || inst.title_lv || '')
        : '';
      const figId = s.figure_id || (inst && inst.figure_id ? String(inst.figure_id) : '');
      const typeId = String(s.type_id || 'Q01');
      slots.push({
        slot_id: String(s.slot_id),
        topic: Number(s.topic),
        points: Number(s.points),
        rubric_points: typeof s.rubric_points === 'number' ? s.rubric_points : Number(s.points),
        type_id: typeId,
        family_id: String(s.family_id),
        variant_id: String(s.variant_id || ''),
        instance_id: String(s.instance_id),
        figure_id: figId,
        stem_lv: stem || `Uzdevums ${s.instance_id} (${s.family_id}, tips ${typeId}).`,
        blank_kind: TALL_TYPES[typeId] ? 'tall' : 'short'
      });
    }

    const topicSubtotals: Array<{ topic: number; slots: number; points: number }> = [];
    const rawSubtotals = target.topic_subtotals || {};
    for (let t = 1; t <= 7; t += 1) {
      const entry = rawSubtotals[String(t)];
      topicSubtotals.push({
        topic: t,
        slots: entry ? Number(entry.slots) : 0,
        points: entry ? Number(entry.points) : 0
      });
    }

    return {
      form_id: String(target.form_id),
      epistemic_label: String(target.epistemic_label || 'PROPOSED'),
      total_points: typeof target.total_points === 'number' ? target.total_points : 100,
      total_slots: typeof target.total_slots === 'number' ? target.total_slots : slots.length,
      topic_subtotals: topicSubtotals,
      conflicts: Array.isArray(target.conflicts) ? target.conflicts.slice() : [],
      slots: slots
    };
  }

  function renderEmptyStateHTML(): string {
    return (
      '<div id="paper-empty-state" class="paper-empty-state" role="status">' +
      '<p><strong>Papīra darba lapa nav pieejama:</strong> neviena eksāmena forma (A/B/C) pašlaik nav apstiprinātā stāvoklī.</p>' +
      '</div>'
    );
  }

  function renderWorksheetHTML(model: PaperWorksheetModel | null): string {
    if (!model) {
      return renderEmptyStateHTML();
    }

    const parts: string[] = [];
    parts.push(`<div class="paper-sheet" data-form-id="${escapeHtml(model.form_id)}" data-epistemic="${escapeHtml(model.epistemic_label)}">`);
    parts.push('<header class="paper-sheet-header">');
    parts.push(`<h3>Papīra darba lapa — Forma ${escapeHtml(model.form_id)} (${escapeHtml(model.epistemic_label)})</h3>`);
    parts.push(
      `<p class="paper-sheet-meta">Treniņpolitikas papīra variants (nav oficiāls eksāmena dokuments) | ` +
      `Programmas maksimums: 180 min | Skala: ${escapeHtml(model.total_points)} p. | Uzdevumi: ${escapeHtml(model.total_slots)} sloti</p>`
    );
    parts.push('<p class="paper-student-line">Vārds, uzvārds: ______________________________ &nbsp;&nbsp; Datums: ______________</p>');
    parts.push('</header>');

    parts.push('<section class="paper-point-summary" aria-label="Punktu sadalījums pa tēmām">');
    parts.push('<table class="paper-point-table"><thead><tr><th>Tēma</th><th>Sloti</th><th>Punkti</th><th>Iegūtie p.</th></tr></thead><tbody>');
    for (let i = 0; i < model.topic_subtotals.length; i += 1) {
      const row = model.topic_subtotals[i];
      parts.push(`<tr><td>${escapeHtml(row.topic)}. tēma</td><td>${escapeHtml(row.slots)}</td><td>${escapeHtml(row.points)}</td><td></td></tr>`);
    }
    parts.push(`</tbody><tfoot><tr><th>Kopā</th><th>${escapeHtml(model.total_slots)}</th><th>${escapeHtml(model.total_points)}</th><th></th></tr></tfoot></table>`);

    if (model.conflicts.length > 0) {
      parts.push('<div class="paper-conflict-note"><strong>Redzamie avotu konflikti:</strong><ul>');
      for (let i = 0; i < model.conflicts.length; i += 1) {
        const c = model.conflicts[i];
        parts.push(`<li><code>${escapeHtml(c.id)}</code> (${escapeHtml(c.slot_id || '')}): ${escapeHtml(c.note_lv || '')}</li>`);
      }
      parts.push('</ul></div>');
    }
    parts.push('</section>');

    parts.push('<ol class="paper-slot-list">');
    for (let i = 0; i < model.slots.length; i += 1) {
      const slot = model.slots[i];
      const blankClass = slot.blank_kind === 'tall' ? 'paper-answer-blank paper-answer-blank-tall' : 'paper-answer-blank';
      const figHtml = slot.figure_id
        ? `<p class="paper-figure-ref">Saistītais attēls: <code>${escapeHtml(slot.figure_id)}</code></p>`
        : '';
      parts.push(
        `<li class="paper-slot" data-slot-id="${escapeHtml(slot.slot_id)}" data-topic="${escapeHtml(slot.topic)}" data-points="${escapeHtml(slot.points)}" data-type="${escapeHtml(slot.type_id)}">` +
        `<div class="paper-slot-head"><strong>${escapeHtml(slot.slot_id)}</strong> (${escapeHtml(slot.topic)}. tēma, ${escapeHtml(slot.points)} p., ${escapeHtml(slot.type_id)}, <code>${escapeHtml(slot.instance_id)}</code>)</div>` +
        `<p class="paper-slot-stem">${escapeHtml(slot.stem_lv)}</p>` +
        figHtml +
        `<div class="${blankClass}" aria-label="Atbildes vieta rokrakstam">Atbilde:</div>` +
        '<div class="paper-work-grid" aria-label="Aprēķinu melnraksta režģis">Aprēķinu lauks:</div>' +
        '</li>'
      );
    }
    parts.push('</ol>');
    parts.push('</div>');
    return parts.join('\n');
  }

  function applyPrintTheme(doc: PaperDocument, enabled: boolean): boolean {
    const rootEl = doc.documentElement;
    if (!rootEl || !rootEl.classList) {
      return false;
    }
    if (enabled) {
      rootEl.classList.add('theme-print');
    } else {
      rootEl.classList.remove('theme-print');
    }
    return enabled;
  }

  function populateSelect(
    selectEl: PaperElement | null,
    forms: PaperFormRecord[],
    selectedId: string | null
  ): void {
    if (!selectEl) {
      return;
    }
    const optsHtml: string[] = [];
    for (let i = 0; i < forms.length; i += 1) {
      const fid = forms[i].form_id;
      const selAttr = fid === selectedId ? ' selected' : '';
      optsHtml.push(`<option value="${escapeHtml(fid)}"${selAttr}>Forma ${escapeHtml(fid)} (21 slots, 100 p.)</option>`);
    }
    selectEl.innerHTML = optsHtml.join('');
    selectEl.disabled = forms.length === 0;
  }

  function init(doc: PaperDocument, opts?: PaperInitOptions): { availableForms: string[]; activeForm: string | null } {
    const formsIsland = (opts && opts.forms !== undefined)
      ? opts.forms
      : (readJsonIsland(doc, 'sim-forms') as PaperFormsIsland | null);
    const bankIsland = (opts && opts.bank !== undefined)
      ? opts.bank
      : (readJsonIsland(doc, 'sim-bank') as PaperBankIsland | null);

    const available = getAvailableForms(formsIsland);
    const availableIds = available.map((f) => f.form_id);
    const activeForm = availableIds.length > 0 ? availableIds[0] : null;

    const mainSelect = doc.getElementById('paper-form-select');
    const settingsSelect = doc.getElementById('settings-paper-form-select');
    const outputEl = doc.getElementById('paper-worksheet-output');
    const printBtn = doc.getElementById('paper-print-btn');

    populateSelect(mainSelect, available, activeForm);
    populateSelect(settingsSelect, available, activeForm);

    function renderSelected(formId: string | null): void {
      if (!outputEl) {
        return;
      }
      if (!formId) {
        outputEl.innerHTML = renderEmptyStateHTML();
        return;
      }
      const model = buildWorksheetModel(formsIsland, bankIsland, formId);
      outputEl.innerHTML = renderWorksheetHTML(model);
    }

    renderSelected(activeForm);

    function onSelectChange(sourceEl: PaperElement | null, peerEl: PaperElement | null): void {
      if (!sourceEl) {
        return;
      }
      const val = String(sourceEl.value || '');
      if (peerEl) {
        peerEl.value = val;
      }
      renderSelected(val || null);
    }

    if (mainSelect && typeof mainSelect.addEventListener === 'function') {
      mainSelect.addEventListener('change', function (): void {
        onSelectChange(mainSelect, settingsSelect);
      });
    }
    if (settingsSelect && typeof settingsSelect.addEventListener === 'function') {
      settingsSelect.addEventListener('change', function (): void {
        onSelectChange(settingsSelect, mainSelect);
      });
    }
    if (printBtn && typeof printBtn.addEventListener === 'function') {
      printBtn.addEventListener('click', function (): void {
        const win = root as { print?: () => void };
        if (typeof win.print === 'function') {
          win.print();
        }
      });
    }

    return {
      availableForms: availableIds,
      activeForm: activeForm
    };
  }

  const api: SimPaperApi = {
    VERSION: '1.0.0-n34',
    getAvailableForms: getAvailableForms,
    buildWorksheetModel: buildWorksheetModel,
    renderWorksheetHTML: renderWorksheetHTML,
    renderEmptyStateHTML: renderEmptyStateHTML,
    applyPrintTheme: applyPrintTheme,
    init: init
  };

  root.SimPaper = api;
})(typeof globalThis !== 'undefined' ? (globalThis as unknown as Record<string, unknown>) : (this as unknown as Record<string, unknown>));
