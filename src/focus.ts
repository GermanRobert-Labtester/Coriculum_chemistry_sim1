/* N33 Keyboard-Only Operation & Focus Management Runtime Module.
 *
 * Implements:
 *   - Keyboard map validation (collision detection, reserved browser/AT key guard)
 *   - Typing-context input-guard (suppresses bare-key shortcuts in text/number inputs)
 *   - View transition focus rule (moves focus to declared heading + live-region announce)
 *   - Modal/drawer return-focus rule (restores focus to invoking control on close)
 *   - Drawer trap-guard (Tab past the end of a drawer escapes rather than cycling)
 *   - Single-announcement live-region dispatcher (timer_threshold=assertive,
 *     verdict_posted=polite, view_changed=polite)
 */

(function (root: any): void {
  'use strict';

  interface ShortcutBinding {
    key: string;
    action: string;
    target?: string;
    heading_id?: string;
    label_lv?: string;
  }

  interface KeyboardMapSpec {
    schema_version: number;
    policy_id: string;
    contexts: string[];
    global_shortcuts: ShortcutBinding[];
    context_shortcuts: { [context: string]: ShortcutBinding[] };
    modifier_rules?: {
      no_bare_keys_in_typing_contexts?: boolean;
      typing_context_tags?: string[];
      typing_context_input_types?: string[];
      ignore_when_modifiers_pressed?: string[];
      reserved_browser_at_keys?: string[];
    };
  }

  interface TraceEntry {
    seq: number;
    kind: string;
    context: string;
    targetId: string | null;
    detail?: string;
  }

  interface AnnouncementEntry {
    seq: number;
    channel: string;
    regionId: string;
    politeness: string;
    message: string;
  }

  class FocusError extends Error {
    code: string;
    details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super(message);
      this.name = 'FocusError';
      this.code = code;
      this.details = details || {};
      if (typeof Error.captureStackTrace === 'function') {
        Error.captureStackTrace(this, FocusError);
      }
    }
  }

  const RESERVED_KEYS = ['Tab', 'Shift+Tab', 'F1', 'F5', 'F6', 'F11', 'F12'];
  const TYPING_INPUT_TYPES = ['text', 'number', 'search', 'email', 'url', 'tel', 'password', ''];

  const LIVE_CHANNELS: Record<string, { id: string; politeness: string; role: string }> = {
    timer_threshold: { id: 'sim-live-timer', politeness: 'assertive', role: 'alert' },
    verdict_posted: { id: 'sim-live-verdict', politeness: 'polite', role: 'status' },
    view_changed: { id: 'sim-live-view', politeness: 'polite', role: 'status' },
  };

  const SECTION_CONTEXT_MAP: Record<string, string> = {
    sakums: 'start',
    saturs: 'concept_map',
    prakse: 'practice',
    eksamens: 'exam',
    rezultati: 'results',
    atskats: 'revision',
    metodika: 'methods',
    druka: 'print',
    iestatijumi: 'settings',
  };

  const DEFAULT_KEYBOARD_MAP: KeyboardMapSpec = {
    schema_version: 1,
    policy_id: 'n33-keyboard-map-v1',
    contexts: ['exam', 'practice', 'revision', 'settings', 'drawer-open'],
    global_shortcuts: [
      { key: 't', action: 'topic_jump', target: '#saturs', heading_id: 'saturs-virsraksts' },
      { key: 'm', action: 'theme_toggle', target: '#theme-toggle-btn' },
      { key: '1', action: 'section_jump_1', target: '#sakums', heading_id: 'sakums-virsraksts' },
      { key: '2', action: 'section_jump_2', target: '#saturs', heading_id: 'saturs-virsraksts' },
      { key: '3', action: 'section_jump_3', target: '#prakse', heading_id: 'prakse-virsraksts' },
      { key: '4', action: 'section_jump_4', target: '#eksamens', heading_id: 'eksamens-virsraksts' },
      { key: '5', action: 'section_jump_5', target: '#rezultati', heading_id: 'rezultati-virsraksts' },
      { key: '6', action: 'section_jump_6', target: '#atskats', heading_id: 'atskats-virsraksts' },
      { key: '7', action: 'section_jump_7', target: '#metodika', heading_id: 'metodika-virsraksts' },
      { key: '8', action: 'section_jump_8', target: '#druka', heading_id: 'druka-virsraksts' },
      { key: '9', action: 'section_jump_9', target: '#iestatijumi', heading_id: 'iestatijumi-virsraksts' },
    ],
    context_shortcuts: {
      exam: [
        { key: 'n', action: 'exam_next', target: '#exam-next' },
        { key: 'p', action: 'exam_prev', target: '#exam-prev' },
        { key: 'f', action: 'exam_flag', target: '#exam-flag' },
        { key: 'r', action: 'exam_review', target: '#exam-review-button' },
      ],
      practice: [
        { key: 'h', action: 'practice_hint', target: '#prakse-help-slot button' },
        { key: 's', action: 'practice_skip', target: '#prakse-skip-btn' },
        { key: 'n', action: 'practice_next', target: '#prakse-next-btn' },
      ],
      revision: [
        { key: 'c', action: 'revision_self_check', target: '#atskats-revision-heading' },
      ],
      settings: [
        { key: 'k', action: 'settings_storage_toggle', target: '#store-opt-in-toggle' },
      ],
      'drawer-open': [
        { key: 'Escape', action: 'drawer_close', target: '#concept-drawer-close, #hint-drawer-close' },
      ],
    },
  };

  const state = {
    activeContext: 'start',
    previousContext: 'start',
    drawerReturnMap: Object.create(null) as Record<string, any>,
    openDrawerId: null as string | null,
    trace: [] as TraceEntry[],
    announcements: [] as AnnouncementEntry[],
    map: DEFAULT_KEYBOARD_MAP as KeyboardMapSpec,
    initializedDocs: [] as any[],
  };

  function recordTrace(kind: string, targetId: string | null, detail?: string): TraceEntry {
    const entry: TraceEntry = {
      seq: state.trace.length + 1,
      kind: kind,
      context: state.activeContext,
      targetId: targetId,
      detail: detail,
    };
    state.trace.push(entry);
    return entry;
  }

  function normalizeKey(key: string): string {
    if (!key) return '';
    return key.length === 1 ? key.toLowerCase() : key;
  }

  function validateKeyboardMap(mapSpec: KeyboardMapSpec): {
    valid: boolean;
    contexts_checked: number;
    resolved_bindings: number;
  } {
    if (!mapSpec || !Array.isArray(mapSpec.contexts) || !mapSpec.context_shortcuts) {
      throw new FocusError('E_KEYMAP_INVALID', 'Keyboard map specification is missing contexts or context_shortcuts.');
    }

    const globals = Array.isArray(mapSpec.global_shortcuts) ? mapSpec.global_shortcuts : [];
    let resolvedCount = 0;

    for (let i = 0; i < mapSpec.contexts.length; i += 1) {
      const ctx = mapSpec.contexts[i];
      const byKey: Record<string, string[]> = Object.create(null);
      const combined: ShortcutBinding[] = [];

      if (ctx !== 'drawer-open') {
        for (let g = 0; g < globals.length; g += 1) {
          combined.push(globals[g]);
        }
      }
      const ctxList = Array.isArray(mapSpec.context_shortcuts[ctx]) ? mapSpec.context_shortcuts[ctx] : [];
      for (let c = 0; c < ctxList.length; c += 1) {
        combined.push(ctxList[c]);
      }

      for (let b = 0; b < combined.length; b += 1) {
        const binding = combined[b];
        const k = normalizeKey(binding.key);
        if (RESERVED_KEYS.indexOf(binding.key) !== -1) {
          throw new FocusError(
            'E_KEYMAP_RESERVED_KEY',
            'Reserved browser/AT key "' + binding.key + '" cannot be bound in context "' + ctx + '" (action: ' + binding.action + ').',
            { key: binding.key, context: ctx, action: binding.action }
          );
        }
        if (!byKey[k]) {
          byKey[k] = [];
        }
        byKey[k].push(binding.action);
        if (byKey[k].length > 1) {
          throw new FocusError(
            'E_KEYMAP_COLLISION',
            'Key collision in context "' + ctx + '" for key "' + binding.key + '": actions [' + byKey[k].join(', ') + '].',
            { key: binding.key, context: ctx, actions: byKey[k].slice() }
          );
        }
        resolvedCount += 1;
      }
    }

    return {
      valid: true,
      contexts_checked: mapSpec.contexts.length,
      resolved_bindings: resolvedCount,
    };
  }

  function isTypingContext(el: any): boolean {
    if (!el || typeof el !== 'object') return false;
    const tag = typeof el.tagName === 'string' ? el.tagName.toUpperCase() : '';
    if (tag === 'TEXTAREA' || tag === 'SELECT') return true;
    if (tag === 'INPUT') {
      const inputType = typeof el.type === 'string' ? el.type.toLowerCase() : '';
      return TYPING_INPUT_TYPES.indexOf(inputType) !== -1;
    }
    if (el.isContentEditable === true) return true;
    if (typeof el.getAttribute === 'function' && el.getAttribute('contenteditable') === 'true') {
      return true;
    }
    return false;
  }

  function shouldSuppressShortcut(event: any, activeEl: any): { suppress: boolean; reason: string } {
    if (!event) return { suppress: true, reason: 'no_event' };
    if (event.ctrlKey || event.altKey || event.metaKey) {
      return { suppress: true, reason: 'modifier_pressed' };
    }
    const key = typeof event.key === 'string' ? event.key : '';
    if (key === 'Tab' || key === 'Shift') {
      return { suppress: true, reason: 'reserved_navigation_key' };
    }
    if (key !== 'Escape' && isTypingContext(activeEl)) {
      return { suppress: true, reason: 'typing_context' };
    }
    return { suppress: false, reason: 'ok' };
  }

  function focusEl(el: any): string | null {
    if (!el || typeof el.focus !== 'function') return null;
    try {
      el.focus({ preventScroll: true });
    } catch (_err) {
      el.focus();
    }
    return typeof el.id === 'string' && el.id ? el.id : null;
  }

  function ensureHeadingFocusable(heading: any): void {
    if (!heading || typeof heading.getAttribute !== 'function') return;
    if (heading.getAttribute('tabindex') === null && typeof heading.setAttribute === 'function') {
      heading.setAttribute('tabindex', '-1');
    }
  }

  function announce(doc: any, channel: string, message: string): AnnouncementEntry | null {
    const cfg = LIVE_CHANNELS[channel];
    if (!cfg || !doc || typeof doc.getElementById !== 'function') return null;
    const region = doc.getElementById(cfg.id);
    if (!region) return null;
    if (typeof region.setAttribute === 'function') {
      region.setAttribute('aria-live', cfg.politeness);
      region.setAttribute('role', cfg.role);
    }
    region.textContent = String(message || '');
    const entry: AnnouncementEntry = {
      seq: state.announcements.length + 1,
      channel: channel,
      regionId: cfg.id,
      politeness: cfg.politeness,
      message: region.textContent,
    };
    state.announcements.push(entry);
    return entry;
  }

  function navigateToSection(
    doc: any,
    sectionId: string,
    opts?: { headingId?: string; announce?: boolean }
  ): { sectionId: string; headingId: string | null; context: string } {
    const cleanId = sectionId.replace(/^#/, '');
    const nextCtx = SECTION_CONTEXT_MAP[cleanId] || state.activeContext;
    state.activeContext = nextCtx;
    const targetHeadingId = (opts && opts.headingId) || (cleanId + '-virsraksts');
    let heading = doc && typeof doc.getElementById === 'function' ? doc.getElementById(targetHeadingId) : null;
    if (!heading && doc && typeof doc.getElementById === 'function') {
      const sec = doc.getElementById(cleanId);
      if (sec && typeof sec.querySelector === 'function') {
        heading = sec.querySelector('h1, h2, h3');
      }
    }
    if (heading) {
      ensureHeadingFocusable(heading);
      focusEl(heading);
    }
    const label = heading && typeof heading.textContent === 'string' ? heading.textContent.trim() : cleanId;
    if (!opts || opts.announce !== false) {
      announce(doc, 'view_changed', 'Skats: ' + label);
    }
    recordTrace('view_transition', heading && heading.id ? heading.id : cleanId, nextCtx);
    return {
      sectionId: cleanId,
      headingId: heading && heading.id ? heading.id : null,
      context: nextCtx,
    };
  }

  function isElementVisible(el: any): boolean {
    if (!el) return false;
    let cur = el;
    while (cur) {
      if (cur.hidden === true) return false;
      if (typeof cur.getAttribute === 'function' && cur.getAttribute('hidden') !== null) return false;
      cur = cur.parentNode || null;
    }
    return true;
  }

  function isFocusable(el: any): boolean {
    if (!el || el.disabled === true) return false;
    if (!isElementVisible(el)) return false;
    if (typeof el.getAttribute === 'function' && el.getAttribute('aria-hidden') === 'true') return false;
    const tag = typeof el.tagName === 'string' ? el.tagName.toUpperCase() : '';
    const tabIdxAttr = typeof el.getAttribute === 'function' ? el.getAttribute('tabindex') : null;
    if (tabIdxAttr !== null) {
      const parsed = parseInt(tabIdxAttr, 10);
      if (!isNaN(parsed) && parsed >= 0) return true;
      if (!isNaN(parsed) && parsed < 0) return false;
    }
    if (tag === 'BUTTON' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') {
      return !(tag === 'INPUT' && typeof el.type === 'string' && el.type.toLowerCase() === 'hidden');
    }
    if (tag === 'A' && typeof el.getAttribute === 'function' && el.getAttribute('href') !== null) {
      return true;
    }
    return false;
  }

  function getFocusableElements(container: any): any[] {
    const out: any[] = [];
    if (!container) return out;
    function walk(node: any): void {
      const children = node.children || node.childNodes;
      if (!children || typeof children.length !== 'number') return;
      for (let i = 0; i < children.length; i += 1) {
        const ch = children[i];
        if (isFocusable(ch)) {
          out.push(ch);
        }
        walk(ch);
      }
    }
    if (container.children || container.childNodes) {
      walk(container);
      return out;
    }
    if (typeof container.querySelectorAll === 'function') {
      const candidates = container.querySelectorAll('a, button, input, select, textarea, [tabindex]');
      for (let i = 0; i < candidates.length; i += 1) {
        if (isFocusable(candidates[i])) {
          out.push(candidates[i]);
        }
      }
    }
    return out;
  }

  function openDrawer(doc: any, drawerId: string, triggerEl?: any): string | null {
    if (!doc || typeof doc.getElementById !== 'function') return null;
    const drawer = doc.getElementById(drawerId);
    if (!drawer) return null;
    const invoker = triggerEl || doc.activeElement || null;
    state.drawerReturnMap[drawerId] = invoker;
    if (state.activeContext !== 'drawer-open') {
      state.previousContext = state.activeContext;
    }
    state.openDrawerId = drawerId;
    state.activeContext = 'drawer-open';
    drawer.hidden = false;
    if (typeof drawer.removeAttribute === 'function') {
      drawer.removeAttribute('hidden');
    }
    const inside = getFocusableElements(drawer);
    const target = inside.length > 0 ? inside[0] : drawer;
    const focusedId = focusEl(target);
    recordTrace('drawer_open', focusedId || drawerId, drawerId);
    return focusedId;
  }

  function closeDrawer(doc: any, drawerId: string): string | null {
    if (!doc || typeof doc.getElementById !== 'function') return null;
    const drawer = doc.getElementById(drawerId);
    if (drawer) {
      drawer.hidden = true;
      if (typeof drawer.setAttribute === 'function') {
        drawer.setAttribute('hidden', '');
      }
    }
    const invoker = state.drawerReturnMap[drawerId] || null;
    delete state.drawerReturnMap[drawerId];
    if (state.openDrawerId === drawerId) {
      state.openDrawerId = null;
      state.activeContext = state.previousContext || 'start';
    }
    const restoredId = focusEl(invoker);
    recordTrace('drawer_close_restore', restoredId, drawerId);
    return restoredId;
  }

  function walkTabSequence(
    doc: any,
    drawerId: string,
    triggerEl?: any
  ): {
    drawerId: string;
    invokerId: string | null;
    insideIds: string[];
    escapedToId: string | null;
    escapedOutsideDrawer: boolean;
    sequence: string[];
  } {
    const drawer = doc && typeof doc.getElementById === 'function' ? doc.getElementById(drawerId) : null;
    if (!drawer) {
      throw new FocusError('E_DRAWER_NOT_FOUND', 'Drawer "' + drawerId + '" not found.');
    }
    openDrawer(doc, drawerId, triggerEl);
    const inside = getFocusableElements(drawer);
    const allDocFocusable = getFocusableElements(doc.body || doc);
    const insideIds: string[] = [];
    const sequence: string[] = [];

    for (let i = 0; i < inside.length; i += 1) {
      const id = focusEl(inside[i]) || ('anon-' + i);
      insideIds.push(id);
      sequence.push(id);
    }

    let escapedEl: any = null;
    if (inside.length > 0) {
      const lastInside = inside[inside.length - 1];
      const idx = allDocFocusable.indexOf(lastInside);
      for (let j = idx + 1; j < allDocFocusable.length; j += 1) {
        if (inside.indexOf(allDocFocusable[j]) === -1) {
          escapedEl = allDocFocusable[j];
          break;
        }
      }
    }
    if (!escapedEl && allDocFocusable.length > 0) {
      for (let j = 0; j < allDocFocusable.length; j += 1) {
        if (inside.indexOf(allDocFocusable[j]) === -1) {
          escapedEl = allDocFocusable[j];
          break;
        }
      }
    }

    const escapedToId = focusEl(escapedEl);
    if (escapedToId) {
      sequence.push(escapedToId);
    }
    const escapedOutsideDrawer = Boolean(escapedEl) && inside.indexOf(escapedEl) === -1;
    recordTrace('drawer_tab_escape', escapedToId, drawerId);
    return {
      drawerId: drawerId,
      invokerId: triggerEl && triggerEl.id ? triggerEl.id : null,
      insideIds: insideIds,
      escapedToId: escapedToId,
      escapedOutsideDrawer: escapedOutsideDrawer,
      sequence: sequence,
    };
  }

  function resolveBinding(context: string, key: string): ShortcutBinding | null {
    const norm = normalizeKey(key);
    const ctxList = state.map.context_shortcuts[context] || [];
    for (let i = 0; i < ctxList.length; i += 1) {
      if (normalizeKey(ctxList[i].key) === norm) {
        return ctxList[i];
      }
    }
    if (context !== 'drawer-open') {
      for (let g = 0; g < state.map.global_shortcuts.length; g += 1) {
        if (normalizeKey(state.map.global_shortcuts[g].key) === norm) {
          return state.map.global_shortcuts[g];
        }
      }
    }
    return null;
  }

  function handleKeyDown(
    doc: any,
    event: any,
    opts?: { context?: string; activeElement?: any }
  ): { handled: boolean; suppressed: boolean; reason: string; action: string | null } {
    const activeEl = (opts && opts.activeElement) || (doc && doc.activeElement) || null;
    const guard = shouldSuppressShortcut(event, activeEl);
    if (guard.suppress) {
      return { handled: false, suppressed: true, reason: guard.reason, action: null };
    }

    const ctx = (opts && opts.context) || state.activeContext;
    const binding = resolveBinding(ctx, event.key);
    if (!binding) {
      return { handled: false, suppressed: false, reason: 'unbound_key', action: null };
    }

    if (binding.action === 'drawer_close' && state.openDrawerId) {
      closeDrawer(doc, state.openDrawerId);
      if (typeof event.preventDefault === 'function') event.preventDefault();
      return { handled: true, suppressed: false, reason: 'ok', action: binding.action };
    }

    if (binding.action === 'topic_jump' || binding.action.indexOf('section_jump_') === 0) {
      const secId = (binding.target || '#sakums').replace(/^#/, '');
      navigateToSection(doc, secId, { headingId: binding.heading_id });
      if (typeof event.preventDefault === 'function') event.preventDefault();
      return { handled: true, suppressed: false, reason: 'ok', action: binding.action };
    }

    if (binding.target && doc && typeof doc.querySelector === 'function') {
      const targetEl = doc.querySelector(binding.target);
      if (targetEl && typeof targetEl.click === 'function') {
        if (typeof targetEl.focus === 'function' && targetEl.getAttribute && targetEl.getAttribute('tabindex') === '-1') {
          targetEl.focus();
        }
        targetEl.click();
        recordTrace('shortcut_action', targetEl.id || binding.target, binding.action);
        if (typeof event.preventDefault === 'function') event.preventDefault();
        return { handled: true, suppressed: false, reason: 'ok', action: binding.action };
      }
    }

    return { handled: false, suppressed: false, reason: 'target_unavailable', action: binding.action };
  }

  function init(doc: any, opts?: { map?: KeyboardMapSpec }): { initialized: boolean; valid: boolean } {
    if (opts && opts.map) {
      validateKeyboardMap(opts.map);
      state.map = opts.map;
    } else {
      validateKeyboardMap(state.map);
    }

    if (doc && state.initializedDocs.indexOf(doc) === -1) {
      state.initializedDocs.push(doc);
      if (typeof doc.addEventListener === 'function') {
        doc.addEventListener('keydown', function (event: any): void {
          handleKeyDown(doc, event);
        });
      }
      if (typeof doc.querySelectorAll === 'function') {
        const navLinks = doc.querySelectorAll('#sim-nav a[href^="#"], #sakums-navigacija a[href^="#"]');
        for (let i = 0; i < navLinks.length; i += 1) {
          const link = navLinks[i];
          if (typeof link.addEventListener === 'function') {
            link.addEventListener('click', function (): void {
              const href = typeof link.getAttribute === 'function' ? link.getAttribute('href') : '';
              if (href && href.charAt(0) === '#') {
                navigateToSection(doc, href.slice(1));
              }
            });
          }
        }
      }
    }

    return { initialized: true, valid: true };
  }

  function resetForTest(): void {
    state.activeContext = 'start';
    state.previousContext = 'start';
    state.drawerReturnMap = Object.create(null);
    state.openDrawerId = null;
    state.trace = [];
    state.announcements = [];
  }

  const api = {
    FocusError: FocusError,
    DEFAULT_KEYBOARD_MAP: DEFAULT_KEYBOARD_MAP,
    LIVE_CHANNELS: LIVE_CHANNELS,
    validateKeyboardMap: validateKeyboardMap,
    isTypingContext: isTypingContext,
    shouldSuppressShortcut: shouldSuppressShortcut,
    navigateToSection: navigateToSection,
    openDrawer: openDrawer,
    closeDrawer: closeDrawer,
    getFocusableElements: getFocusableElements,
    walkTabSequence: walkTabSequence,
    announce: announce,
    handleKeyDown: handleKeyDown,
    init: init,
    getContext: function (): string { return state.activeContext; },
    setContext: function (ctx: string): void { state.activeContext = ctx; },
    getTrace: function (): TraceEntry[] { return state.trace.slice(); },
    getAnnouncements: function (): AnnouncementEntry[] { return state.announcements.slice(); },
    resetForTest: resetForTest,
  };

  root.SimFocus = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
