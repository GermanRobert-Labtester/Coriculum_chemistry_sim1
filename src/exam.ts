/* N21 — the exam shell: timer bar, slot navigator, question map, flags,
 * keyboard contract and the review-and-submit screen.
 *
 * Two rules shape this module:
 *
 *  1. The shell never mutates the session. It dispatches events on the
 *     session machine and re-renders from the resulting snapshot. The answer
 *     map has no reachable setter, so "the machine is the only writer" is a
 *     structural property rather than a convention.
 *
 *  2. The mode registry is the single source of truth for what may render.
 *     In exam mode the help surfaces (hint ladder, worked chains, method
 *     cards, term lookup) are not merely hidden — they are never created,
 *     because the render contract refuses an unregistered component outright.
 */
(function (this: void, root: any): void {
  'use strict';

  /* ------------------------------------------------------------------ types */

  interface SlotPlan {
    slot_id: string;
    topic: number;
    points: number;
  }

  interface SlotPlan {
    slot_id: string;
    topic: number;
    points: number;
  }

  interface ModeDefinition {
    allowed_components: string[];
    forbidden_components: string[];
  }

  interface ViewDiscipline {
    default_mode: string;
    modes: Record<string, ModeDefinition>;
    unregistered_component_error: string;
  }

  interface MapCell {
    slot_id: string;
    index: number;
    answered: boolean;
    flagged: boolean;
    current: boolean;
    points: number;
    topic: number;
  }

  interface MapState {
    cells: MapCell[];
    answered_count: number;
    flagged_count: number;
    unanswered_count: number;
    current_slot_id: string | null;
  }

  interface ReviewRow {
    slot_id: string;
    index: number;
    answered: boolean;
    flagged: boolean;
    points: number;
  }

  interface ReviewState {
    rows: ReviewRow[];
    answered_count: number;
    unanswered_count: number;
    flagged_count: number;
    unanswered_slot_ids: string[];
    remediation_slot_ids: string[];
    can_submit: boolean;
    submitted: boolean;
  }

  interface TimerState {
    elapsed_ms: number;
    limit_ms: number;
    remaining_ms: number;
    threshold_reached: boolean;
    threshold_ratio: number;
    label: string;
    threshold_label: string;
    expired_label: string;
  }

  /* ----------------------------------------------------------- mode registry */

  /**
   * The mode registry. It is the single source mapping a mode to the set of
   * components that mode may render. The registry is consulted by the render
   * contract, so an unregistered component fails loudly instead of leaking
   * into a mode that has no business showing it.
   *
   * The N08 hint drawer already looks for `SimModeRegistry.getMode()`, so this
   * global is also how the practice help surface learns which mode it is in.
   */
  interface ModeRegistry {
    getMode(): string;
    setMode(mode: string): void;
    modes(): string[];
    allowedComponents(mode?: string): string[];
    forbiddenComponents(mode?: string): string[];
    isAllowed(component: string, mode?: string): boolean;
    assertAllowed(component: string, mode?: string): void;
  }

  class ModeRegistryError extends Error {
    public readonly code: string;
    public readonly details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super(message);
      this.name = 'ModeRegistryError';
      this.code = code;
      this.details = details || {};
    }
  }

  function createModeRegistry(discipline: ViewDiscipline): ModeRegistry {
    let current = discipline.default_mode || 'practice';

    function definition(mode?: string): ModeDefinition {
      const name = mode || current;
      const found = discipline.modes[name];
      if (!found) {
        throw new ModeRegistryError(
          discipline.unregistered_component_error,
          'Režīms "' + String(name) + '" nav reģistrēts.',
          { mode: String(name) }
        );
      }
      return found;
    }

    return {
      getMode: function (): string { return current; },
      setMode: function (mode: string): void {
        /* Setting an unknown mode is itself a contract violation. */
        definition(mode);
        current = mode;
      },
      modes: function (): string[] { return Object.keys(discipline.modes).sort(); },
      allowedComponents: function (mode?: string): string[] {
        return definition(mode).allowed_components.slice();
      },
      forbiddenComponents: function (mode?: string): string[] {
        return definition(mode).forbidden_components.slice();
      },
      isAllowed: function (component: string, mode?: string): boolean {
        return definition(mode).allowed_components.indexOf(component) !== -1;
      },
      assertAllowed: function (component: string, mode?: string): void {
        const name = mode || current;
        const def = definition(name);
        if (def.allowed_components.indexOf(component) === -1) {
          throw new ModeRegistryError(
            discipline.unregistered_component_error,
            'Komponents "' + component + '" nav atļauts režīmā "' + name + '".',
            { component: component, mode: name }
          );
        }
      },
    };
  }

  /* -------------------------------------------------------------- utilities */

  function makeElement(doc: any, tag: string, className?: string | null, text?: string | null): any {
    const el = doc.createElement(tag);
    if (className) { el.className = className; }
    if (text !== undefined && text !== null) { el.textContent = String(text); }
    return el;
  }

  function clear(node: any): void {
    if (!node) { return; }
    while (node.firstChild) { node.removeChild(node.firstChild); }
  }

  function formatClock(ms: number): string {
    const total = Math.max(0, Math.floor(ms / 1000));
    const minutes = Math.floor(total / 60);
    const seconds = total % 60;
    const pad = function (value: number): string { return value < 10 ? '0' + value : String(value); };
    return pad(minutes) + ':' + pad(seconds);
  }

  /* ------------------------------------------------------- pure render state */

  /**
   * The question map is a pure function of the session snapshot. Nothing here
   * touches the DOM, so the same function serves the screen, the fixture and
   * the responsive test data.
   */
  function buildMapState(snapshot: any): MapState {
    const answers: Record<string, boolean> = {};
    (snapshot.answers || []).forEach(function (answer: any): void {
      answers[answer.slot_id] = true;
    });
    const flags: Record<string, boolean> = {};
    (snapshot.flags || []).forEach(function (slotId: string): void {
      flags[slotId] = true;
    });
    const points: Record<string, number> = snapshot.points_by_slot || {};
    const slots: SlotPlan[] = snapshot.slots || [];
    const topicBySlot: Record<string, number> = {};
    slots.forEach(function (slot: SlotPlan): void {
      topicBySlot[slot.slot_id] = slot.topic;
    });
    const cells: MapCell[] = (snapshot.slot_ids || []).map(function (slotId: string, index: number): MapCell {
      return {
        slot_id: slotId,
        index: index + 1,
        answered: answers[slotId] === true,
        flagged: flags[slotId] === true,
        current: snapshot.current_slot_id === slotId,
        points: points[slotId] === undefined ? 0 : points[slotId],
        topic: topicBySlot[slotId] === undefined ? 0 : topicBySlot[slotId],
      };
    });
    return {
      cells: cells,
      answered_count: cells.filter(function (cell: MapCell): boolean { return cell.answered; }).length,
      flagged_count: cells.filter(function (cell: MapCell): boolean { return cell.flagged; }).length,
      unanswered_count: cells.filter(function (cell: MapCell): boolean { return !cell.answered; }).length,
      current_slot_id: snapshot.current_slot_id,
    };
  }

  /** The review table is likewise a pure function of the snapshot. */
  function buildReviewState(snapshot: any): ReviewState {
    const answers: Record<string, boolean> = {};
    (snapshot.answers || []).forEach(function (answer: any): void {
      answers[answer.slot_id] = true;
    });
    const flags: Record<string, boolean> = {};
    (snapshot.flags || []).forEach(function (slotId: string): void {
      flags[slotId] = true;
    });
    const points: Record<string, number> = snapshot.points_by_slot || {};
    const rows: ReviewRow[] = (snapshot.slot_ids || []).map(function (slotId: string, index: number): ReviewRow {
      return {
        slot_id: slotId,
        index: index + 1,
        answered: answers[slotId] === true,
        flagged: flags[slotId] === true,
        points: points[slotId] === undefined ? 0 : points[slotId],
      };
    });
    const unanswered = rows
      .filter(function (row: ReviewRow): boolean { return !row.answered; })
      .map(function (row: ReviewRow): string { return row.slot_id; });
    const remediation: string[] = [];
    unanswered.concat(rows
      .filter(function (row: ReviewRow): boolean { return row.flagged; })
      .map(function (row: ReviewRow): string { return row.slot_id; })
    ).forEach(function (slotId: string): void {
      if (remediation.indexOf(slotId) === -1) { remediation.push(slotId); }
    });
    const submitted = snapshot.state === 'submitted';
    return {
      rows: rows,
      answered_count: rows.filter(function (row: ReviewRow): boolean { return row.answered; }).length,
      unanswered_count: unanswered.length,
      flagged_count: rows.filter(function (row: ReviewRow): boolean { return row.flagged; }).length,
      unanswered_slot_ids: unanswered,
      remediation_slot_ids: remediation.sort(),
      can_submit: !submitted,
      submitted: submitted,
    };
  }

  /** The timer state is a pure function of the snapshot and the policy. */
  function buildTimerState(snapshot: any, copy: Record<string, string>): TimerState {
    return {
      elapsed_ms: snapshot.elapsed_ms,
      limit_ms: snapshot.limit_ms,
      remaining_ms: snapshot.remaining_ms,
      threshold_reached: snapshot.threshold_reached,
      threshold_ratio: snapshot.threshold_ratio,
      label: copy.timer_label || '',
      threshold_label: copy.timer_threshold || '',
      expired_label: copy.timer_expired || '',
    };
  }

  /* -------------------------------------------------------------- the shell */

  interface ShellOptions {
    policy: any;
    session: any;
    doc?: any;
    formId?: string;
    confirm?: boolean;
    manifest?: any;
    instancesById?: Record<string, any>;
  }

  /**
   * The exam shell. It owns the DOM of the exam section and nothing else:
   * every change goes through `session.dispatch`, and every render reads the
   * snapshot the machine hands back.
   */
  class ExamShell {
    private readonly doc: any;
    private readonly session: any;
    private readonly registry: ModeRegistry;
    private readonly copy: Record<string, string>;
    private readonly mode = 'exam';
    private readonly manifest: any;
    private readonly instancesById: Record<string, any>;
    private confirmation = false;
    private warningDismissed = false;
    private bound = false;
    private timerHandle: any = null;

    constructor(options: ShellOptions) {
      this.doc = options.doc || (root as any).document;
      this.session = options.session;
      this.copy = (options.policy && options.policy.copy_lv) || {};
      this.registry = createModeRegistry(options.policy.view_discipline);
      this.registry.setMode('exam');
      this.confirmation = options.confirm === true;
      this.manifest = options.manifest || null;
      this.instancesById = options.instancesById || {};
    }

    public getRegistry(): ModeRegistry {
      return this.registry;
    }

    public getSession(): any {
      return this.session;
    }

    /* ------------------------------------------------------ render contract */

    /**
     * The render contract. A component that the current mode does not register
     * is not rendered and not hidden — it is refused, and the refusal is
     * loud. This is how mode creep is caught.
     */
    private assertRenderable(component: string): void {
      this.registry.assertAllowed(component, this.mode);
    }

    public render(): void {
      const snapshot = this.session.snapshot();
      this.renderTimer(snapshot);
      this.renderNavigator(snapshot);
      this.renderMap(snapshot);
      this.renderSlot(snapshot);
      this.renderReview(snapshot);
    }

    private renderTimer(snapshot: any): void {
      this.assertRenderable('timer');
      const bar = this.doc.getElementById('exam-timer-bar');
      if (!bar) { return; }
      const timer = buildTimerState(snapshot, this.copy);
      const value = this.doc.getElementById('exam-timer-value');
      if (value) { value.textContent = formatClock(timer.elapsed_ms); }
      const label = this.doc.getElementById('exam-timer-label');
      if (label) { label.textContent = timer.label; }
      const threshold = this.doc.getElementById('exam-timer-threshold');
      if (threshold) {
        /* The threshold is a status indication only. It never changes the
         * state of the session and it never blocks a control. */
        threshold.textContent = timer.threshold_reached ? timer.threshold_label : '';
        threshold.hidden = !timer.threshold_reached;
      }
      const expired = this.doc.getElementById('exam-timer-expired');
      if (expired) {
        expired.textContent = snapshot.state === 'expired' ? timer.expired_label : '';
        expired.hidden = snapshot.state !== 'expired';
      }
      bar.setAttribute('data-exam-state', snapshot.state);
      bar.setAttribute('data-threshold', timer.threshold_reached ? 'true' : 'false');
    }

    private renderNavigator(snapshot: any): void {
      this.assertRenderable('navigator');
      const status = this.doc.getElementById('exam-slot-status');
      if (status) {
        const index = snapshot.slot_ids.indexOf(snapshot.current_slot_id) + 1;
        status.textContent = snapshot.current_slot_id
          ? 'Uzdevuma vieta ' + index + ' no ' + snapshot.slot_ids.length + ' (' + snapshot.current_slot_id + ')'
          : '';
      }
      const flagButton = this.doc.getElementById('exam-flag');
      if (flagButton) {
        const flagged = snapshot.current_slot_id
          ? (snapshot.flags || []).indexOf(snapshot.current_slot_id) !== -1
          : false;
        flagButton.setAttribute('aria-pressed', flagged ? 'true' : 'false');
        flagButton.textContent = flagged
          ? (this.copy.navigator_unflag || 'Noņemt atzīmējumu')
          : (this.copy.navigator_flag || 'Atzīmēt uzdevumu');
      }
      const prev = this.doc.getElementById('exam-prev');
      const next = this.doc.getElementById('exam-next');
      const index = snapshot.slot_ids.indexOf(snapshot.current_slot_id);
      if (prev) { prev.disabled = index <= 0; }
      if (next) { next.disabled = index === -1 || index >= snapshot.slot_ids.length - 1; }
    }

    private renderMap(snapshot: any): void {
      this.assertRenderable('map');
      const host = this.doc.getElementById('exam-map');
      if (!host) { return; }
      clear(host);
      const map = buildMapState(snapshot);
      map.cells.forEach((cell: MapCell): void => {
        const button = makeElement(this.doc, 'button', 'exam-map-cell');
        button.setAttribute('type', 'button');
        button.setAttribute('id', 'exam-map-' + cell.slot_id);
        button.setAttribute('data-sim-component', 'map');
        button.setAttribute('data-slot-id', cell.slot_id);
        button.setAttribute('data-answered', cell.answered ? 'true' : 'false');
        button.setAttribute('data-flagged', cell.flagged ? 'true' : 'false');
        if (cell.current) { button.setAttribute('aria-current', 'true'); }
        button.setAttribute(
          'aria-label',
          'Uzdevuma vieta ' + cell.index + ' — ' +
          (cell.answered ? (this.copy.map_cell_answered || 'atbildēts') : (this.copy.map_cell_unanswered || 'nav atbildēts')) +
          (cell.flagged ? ', ' + (this.copy.map_cell_flagged || 'atzīmēts') : '')
        );
        button.textContent = String(cell.index);
        button.addEventListener('click', (): void => { this.navigate(cell.slot_id); });
        host.appendChild(button);
      });
    }

    private renderSlot(snapshot: any): void {
      this.assertRenderable('input');
      const host = this.doc.getElementById('exam-slot-host');
      if (!host) { return; }
      clear(host);
      const slotId = snapshot.current_slot_id;
      if (!slotId) { return; }
      const index = snapshot.slot_ids.indexOf(slotId) + 1;
      const heading = makeElement(this.doc, 'h3', 'exam-slot-heading');
      heading.setAttribute('id', 'exam-slot-heading');
      heading.textContent = 'Uzdevuma vieta ' + index + ' (' + slotId + ')';
      host.appendChild(heading);

      const meta = makeElement(this.doc, 'p', 'exam-slot-meta');
      const points = (snapshot.points_by_slot || {})[slotId];
      let boundSlot: any = null;
      if (this.manifest && Array.isArray(this.manifest.slots)) {
        for (let i = 0; i < this.manifest.slots.length; i += 1) {
          if (this.manifest.slots[i].slot_id === slotId) {
            boundSlot = this.manifest.slots[i];
            break;
          }
        }
      }
      const inst = boundSlot && boundSlot.instance_id ? this.instancesById[boundSlot.instance_id] : null;
      if (boundSlot && boundSlot.instance_id) {
        meta.textContent = (points === undefined ? '' : points + ' ' + (this.copy.slot_points || 'punkti')) +
          ' — ' + boundSlot.instance_id + ' (' + boundSlot.family_id + ', ' + boundSlot.type_id +
          (boundSlot.ephemeral ? ', efemers treniņa variants' : '') + ')';
      } else {
        meta.textContent = (points === undefined ? '' : points + ' ' + (this.copy.slot_points || 'punkti')) +
          (this.copy.form_pending_note ? ' — ' + this.copy.form_pending_note : '');
      }
      host.appendChild(meta);

      if (inst && inst.stem_lv) {
        const stem = makeElement(this.doc, 'p', 'exam-slot-stem', inst.stem_lv);
        stem.setAttribute('id', 'exam-slot-stem');
        host.appendChild(stem);
      }

      const label = makeElement(this.doc, 'label', 'exam-answer-label', 'Jūsu atbilde');
      label.setAttribute('for', 'exam-answer-input');
      host.appendChild(label);
      const input = makeElement(this.doc, 'input', 'exam-answer-input');
      input.setAttribute('type', 'text');
      input.setAttribute('id', 'exam-answer-input');
      input.setAttribute('data-sim-component', 'input');
      input.setAttribute('data-slot-id', slotId);
      const existing = this.session.getAnswer(slotId);
      if (existing && existing.payload && typeof existing.payload.text === 'string') {
        input.value = existing.payload.text;
      }
      const self = this;
      input.addEventListener('input', function (): void {
        self.recordAnswer(slotId, { kind: 'raw_text', text: input.value }, { incremental: true });
      });
      host.appendChild(input);

      const hint = makeElement(this.doc, 'p', 'exam-keyboard-hint', this.copy.keyboard_hint || '');
      host.appendChild(hint);
    }

    private renderReview(snapshot: any): void {
      this.assertRenderable('review');
      const host = this.doc.getElementById('exam-review');
      if (!host) { return; }
      clear(host);
      const review = buildReviewState(snapshot);
      const isReview = snapshot.state === 'review';
      host.hidden = !isReview && snapshot.state !== 'submitted';
      if (host.hidden) { return; }

      const heading = makeElement(this.doc, 'h3', 'exam-review-heading', this.copy.review_heading || 'Pārbaude');
      heading.setAttribute('id', 'exam-review-heading');
      host.appendChild(heading);

      const summary = makeElement(this.doc, 'p', 'exam-review-summary', this.copy.review_summary || '');
      host.appendChild(summary);

      const table = makeElement(this.doc, 'table', 'exam-review-table');
      const caption = makeElement(this.doc, 'caption', null, 'Uzdevumu vietu pārbaudes kopsavilkums');
      table.appendChild(caption);
      const thead = makeElement(this.doc, 'thead');
      const headRow = makeElement(this.doc, 'tr');
      ['Uzdevuma vieta', 'Punkti', 'Atbilde', 'Atzīmējums'].forEach((label: string): void => {
        const th = makeElement(this.doc, 'th', null, label);
        th.setAttribute('scope', 'col');
        headRow.appendChild(th);
      });
      thead.appendChild(headRow);
      table.appendChild(thead);
      const tbody = makeElement(this.doc, 'tbody');
      review.rows.forEach((row: ReviewRow): void => {
        const tr = makeElement(this.doc, 'tr');
        tr.setAttribute('data-slot-id', row.slot_id);
        const nameCell = makeElement(this.doc, 'th', null, row.index + '. ' + row.slot_id);
        nameCell.setAttribute('scope', 'row');
        tr.appendChild(nameCell);
        tr.appendChild(makeElement(this.doc, 'td', null, String(row.points)));
        tr.appendChild(makeElement(this.doc, 'td', null, row.answered ? 'jā' : 'nē'));
        tr.appendChild(makeElement(this.doc, 'td', null, row.flagged ? 'jā' : 'nē'));
        tbody.appendChild(tr);
      });
      table.appendChild(tbody);
      host.appendChild(table);

      /* The unanswered warning carries an accessible alert role so that a
       * screen reader announces it when it appears. */
      if (review.unanswered_count > 0 && !this.warningDismissed) {
        const warning = makeElement(this.doc, 'div', 'exam-review-warning');
        warning.setAttribute('role', 'alert');
        warning.setAttribute('id', 'exam-review-warning');
        warning.setAttribute('data-sim-component', 'review');
        warning.appendChild(makeElement(this.doc, 'strong', null, this.copy.review_warning_short || ''));
        warning.appendChild(makeElement(this.doc, 'span', null, ' ' + (this.copy.review_warning || '')));
        const dismiss = makeElement(this.doc, 'button', 'btn-control', this.copy.review_dismiss || 'Aizvērt');
        dismiss.setAttribute('type', 'button');
        dismiss.setAttribute('id', 'exam-review-warning-dismiss');
        const self = this;
        dismiss.addEventListener('click', function (): void {
          self.warningDismissed = true;
          self.render();
        });
        warning.appendChild(dismiss);
        host.appendChild(warning);
      }

      const oneWay = makeElement(this.doc, 'p', 'exam-review-one-way', this.copy.review_one_way || '');
      host.appendChild(oneWay);

      const confirmLabel = makeElement(this.doc, 'label', 'exam-review-confirm-label');
      const confirmBox = makeElement(this.doc, 'input', 'exam-review-confirm');
      confirmBox.setAttribute('type', 'checkbox');
      confirmBox.setAttribute('id', 'exam-review-confirm');
      confirmBox.setAttribute('data-sim-component', 'review');
      if (this.confirmation) { confirmBox.checked = true; }
      const self = this;
      confirmBox.addEventListener('change', function (): void {
        self.confirmation = confirmBox.checked === true;
        self.render();
      });
      confirmLabel.appendChild(confirmBox);
      confirmLabel.appendChild(makeElement(this.doc, 'span', null, ' ' + (this.copy.review_confirm || '')));
      host.appendChild(confirmLabel);

      const submit = makeElement(this.doc, 'button', 'btn-control exam-review-submit', this.copy.review_submit || 'Iesniegt darbu');
      submit.setAttribute('type', 'button');
      submit.setAttribute('id', 'exam-review-submit');
      submit.setAttribute('data-sim-component', 'review');
      submit.setAttribute('aria-describedby', 'exam-review-heading');
      /* The button is only enabled with an explicit confirmation, and the
       * machine refuses an unconfirmed submit as well: the gate is structural,
       * not a UI convention. */
      submit.disabled = !this.confirmation || review.submitted;
      submit.addEventListener('click', function (): void { self.submit(); });
      host.appendChild(submit);
      if (review.submitted) {
        const doneNote = makeElement(this.doc, 'p', 'status-box', 'Darbs iesniegts — treniņsesija pabeigta.');
        doneNote.setAttribute('id', 'exam-review-submitted');
        doneNote.setAttribute('role', 'status');
        host.appendChild(doneNote);
        const liveVerdict = this.doc.getElementById('sim-live-verdict');
        if (liveVerdict) {
          liveVerdict.textContent = 'Eksāmena treniņsesija iesniegta.';
        }
      }
    }

    /* ------------------------------------------------------------- commands */

    public navigate(slotId: string): void {
      this.session.dispatch('navigate', { slot_id: slotId });
      this.render();
      this.focusSlot(slotId);
    }

    public toggleFlag(slotId?: string): void {
      const target = slotId || this.session.getCurrentSlotId();
      if (!target) { return; }
      this.session.dispatch('flag', { slot_id: target });
      this.render();
    }

    public recordAnswer(slotId: string, payload: any, options?: { incremental?: boolean }): void {
      this.session.dispatch('answer', { slot_id: slotId, payload: payload });
      if (options && options.incremental) {
        const snapshot = this.session.snapshot();
        this.renderNavigator(snapshot);
        this.renderMap(snapshot);
        return;
      }
      this.render();
    }

    public requestReview(): void {
      this.session.dispatch('request-review');
      this.render();
    }

    public submit(): void {
      this.session.dispatch('submit', { confirmed: this.confirmation === true });
      this.render();
    }

    public dismissWarning(): void {
      this.warningDismissed = true;
      this.render();
    }

    /**
     * Move the focus to the slot region. Focus is never trapped: the shell
     * moves focus *into* the slot on navigation but never intercepts Tab.
     */
    public focusSlot(_slotId?: string): void {
      const host = this.doc.getElementById('exam-slot-host');
      if (!host) { return; }
      if (typeof host.focus === 'function') { host.focus(); }
    }

    /* ---------------------------------------------------------- keyboard */

    /**
     * The keyboard contract: arrow keys move between slots, the documented
     * shortcut toggles the flag, and no widget traps the focus.
     */
    public handleKey(event: any): boolean {
      if (!event) { return false; }
      const key = String(event.key || '');
      const snapshot = this.session.snapshot();
      const slotIds = snapshot.slot_ids || [];
      const index = slotIds.indexOf(snapshot.current_slot_id);
      if (key === 'ArrowRight' || key === 'ArrowDown') {
        if (index >= 0 && index < slotIds.length - 1) {
          this.navigate(slotIds[index + 1]);
          return true;
        }
        return false;
      }
      if (key === 'ArrowLeft' || key === 'ArrowUp') {
        if (index > 0) {
          this.navigate(slotIds[index - 1]);
          return true;
        }
        return false;
      }
      if (key === 'f' || key === 'F') {
        this.toggleFlag();
        return true;
      }
      return false;
    }

    public bindKeyboard(target?: any): void {
      const node = target || this.doc.getElementById('exam-shell');
      if (!node || this.bound) { return; }
      const self = this;
      node.addEventListener('keydown', function (event: any): void {
        if (self.handleKey(event)) {
          if (typeof event.preventDefault === 'function') { event.preventDefault(); }
          if (typeof event.stopPropagation === 'function') { event.stopPropagation(); }
        }
      });
      this.bound = true;
    }

    /* ---------------------------------------------------------- the timer */

    /**
     * Start the advisory timer. The elapsed time is derived from the
     * monotonic clock at every tick, not from counting ticks, so a
     * background tab that throttles its timers still reports honest elapsed
     * time when it becomes visible again. The limit is advisory: reaching it
     * expires the session, but no answer is ever lost because of it.
     */
    public startTimer(intervalMs?: number): void {
      if (this.timerHandle !== null) { return; }
      const period = intervalMs === undefined ? 1000 : intervalMs;
      const self = this;
      const tick = function (): void {
        self.tick();
      };
      if (typeof (root as any).setInterval === 'function') {
        this.timerHandle = (root as any).setInterval(tick, period);
      }
    }

    public stopTimer(): void {
      if (this.timerHandle !== null && typeof (root as any).clearInterval === 'function') {
        (root as any).clearInterval(this.timerHandle);
      }
      this.timerHandle = null;
    }

    /**
     * One timer tick. The expiry transition is driven by the elapsed time,
     * never by the number of ticks, which is what keeps the hidden-tab
     * behaviour honest.
     */
    public tick(): void {
      const snapshot = this.session.snapshot();
      if (snapshot.state === 'running' || snapshot.state === 'review') {
        if (snapshot.elapsed_ms >= snapshot.limit_ms) {
          this.session.dispatch('expire');
        }
      }
      this.render();
    }
  }

  /* --------------------------------------------------- the practice surface */

  /**
   * The practice surface. It renders the same components as the exam shell
   * and adds the help surfaces, but it is built from a *practice* context:
   * it never receives an exam session, so it structurally cannot read the
   * exam answer map. The two-way boundary is architectural, not cosmetic.
   */
  function renderPracticeSurface(doc: any, options: { host_id: string; practice: any; copy?: Record<string, string> }): void {
    const host = doc.getElementById(options.host_id);
    if (!host) { return; }
    clear(host);
    const practice = options.practice || {};
    const copy = options.copy || {};

    const heading = makeElement(doc, 'h3', 'practice-shell-heading', copy.practice_heading || 'Prakse');
    host.appendChild(heading);

    const input = makeElement(doc, 'input', 'practice-answer-input');
    input.setAttribute('type', 'text');
    input.setAttribute('id', 'practice-answer-input');
    input.setAttribute('data-sim-component', 'input');
    host.appendChild(input);

    const hint = makeElement(doc, 'button', 'btn-control practice-hint-button', copy.practice_hint || 'Palīdzības kāpnes');
    hint.setAttribute('type', 'button');
    hint.setAttribute('id', 'practice-hint-button');
    hint.setAttribute('data-sim-component', 'hint');
    host.appendChild(hint);

    const chain = makeElement(doc, 'a', 'practice-chain-link', copy.practice_chain || 'Darba piemērs');
    chain.setAttribute('href', '#piemeri');
    chain.setAttribute('id', 'practice-chain-link');
    chain.setAttribute('data-sim-component', 'chain');
    host.appendChild(chain);

    const method = makeElement(doc, 'button', 'btn-control practice-method-button', copy.practice_method || 'Metodes karte');
    method.setAttribute('type', 'button');
    method.setAttribute('id', 'practice-method-button');
    method.setAttribute('data-sim-component', 'method-card');
    host.appendChild(method);

    const term = makeElement(doc, 'button', 'btn-control practice-term-button', copy.practice_term || 'Terminu skaidrojums');
    term.setAttribute('type', 'button');
    term.setAttribute('id', 'practice-term-button');
    term.setAttribute('data-sim-component', 'term-lookup');
    host.appendChild(term);

    if (practice.item_id) {
      const context = makeElement(doc, 'p', 'practice-context');
      context.setAttribute('data-item-id', String(practice.item_id));
      context.textContent = String(practice.item_id);
      host.appendChild(context);
    }
  }

  /* --------------------------------------------------- the island and the boot */

  /**
   * The exam-policy loader. It reads the frozen island, checks the cheap
   * invariants the shell depends on, and raises a named error instead of
   * rendering a half-built exam.
   */
  class ExamPolicyError extends Error {
    public readonly code: string;

    constructor(code: string, message: string) {
      super(message);
      this.name = 'ExamPolicyError';
      this.code = code;
    }
  }

  function loadPolicy(doc: any): any {
    const node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-exam-policy') : null;
    if (!node || typeof node.textContent !== 'string' || node.textContent.length === 0) {
      throw new ExamPolicyError(
        'E_EXAM_POLICY_MISSING',
        'Eksāmena mācību politikas sala (#sim-exam-policy) nav pieejama.'
      );
    }
    let policy: any;
    try {
      policy = JSON.parse(node.textContent);
    } catch (error) {
      throw new ExamPolicyError(
        'E_EXAM_POLICY_INVALID',
        'Eksāmena mācību politikas sala nav nolasāma.'
      );
    }
    if (!policy || policy.island_id !== 'sim-exam-policy' || !policy.session_contract || !policy.view_discipline) {
      throw new ExamPolicyError(
        'E_EXAM_POLICY_INVALID',
        'Eksāmena mācību politikas sala neatbilst līgumam.'
      );
    }
    if (!Array.isArray(policy.slots) || policy.slots.length !== policy.exam.slot_count) {
      throw new ExamPolicyError(
        'E_EXAM_POLICY_INVALID',
        'Uzdevumu vietu skaits neatbilst līgumā deklarētajam skaitam.'
      );
    }
    return policy;
  }

  function loadFormsIsland(doc: any): any | null {
    const node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-forms') : null;
    if (!node || typeof node.textContent !== 'string' || node.textContent.trim() === '') {
      return null;
    }
    try {
      const parsed = JSON.parse(node.textContent);
      if (parsed && parsed.island_id === 'sim-forms' && Array.isArray(parsed.forms)) {
        return parsed;
      }
    } catch (_err) {
      return null;
    }
    return null;
  }

  function loadBankIndex(doc: any): { list: any[]; byId: Record<string, any> } {
    const node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-bank') : null;
    const byId: Record<string, any> = {};
    if (!node || typeof node.textContent !== 'string' || node.textContent.trim() === '') {
      return { list: [], byId: byId };
    }
    try {
      const parsed = JSON.parse(node.textContent);
      const list = parsed && Array.isArray(parsed.questions) ? parsed.questions : [];
      for (let i = 0; i < list.length; i += 1) {
        if (list[i] && list[i].question_id) { byId[list[i].question_id] = list[i]; }
      }
      return { list: list, byId: byId };
    } catch (_err) {
      return { list: [], byId: byId };
    }
  }

  interface ExamApp {
    shell: ExamShell;
    session: any;
    policy: any;
    manifest?: any;
    selectedFormId?: string;
    selectForm?: (formId: string) => void;
    start?: () => void;
  }

  /**
   * Boot the exam section. The session starts only on an explicit learner
   * action, so the timer never runs before the session exists, and nothing is
   * persisted: the session lives in memory for as long as the page does.
   */
  function init(doc: any, options?: { formId?: string; formsIsland?: any }): ExamApp | null {
    doc = doc || (root as any).document;
    if (!doc || typeof doc.getElementById !== 'function') { return null; }
    if (!doc.getElementById('exam-shell')) { return null; }

    let policy: any;
    try {
      policy = loadPolicy(doc);
    } catch (error) {
      const status = doc.getElementById('sim-exam-status');
      if (status) {
        status.textContent = 'Eksāmena simulācija nav pieejama: ' + (error as Error).message;
        status.hidden = false;
      }
      return null;
    }

    const status = doc.getElementById('sim-exam-status');
    if (status) {
      /* The status line is derived from the frozen policy, never hard-coded:
       * the slot count, the point total and the advisory limit are the
       * training-policy numbers of the island. */
      const limitMinutes = Math.round(policy.timer.advisory_limit_seconds / 60);
      status.textContent = 'Treniņsesija: ' + policy.exam.slot_count + ' uzdevuma vietu, '
        + policy.exam.total_points + ' punkti, izglītojošs ' + limitMinutes
        + ' minūšu taimers (mācību politika, PROPOSED; nevis oficiāls eksāmens).';
      status.hidden = false;
    }

    const formsIsland = (options && options.formsIsland) || loadFormsIsland(doc);
    const bankData = loadBankIndex(doc);
    const formEntriesById: Record<string, any> = {};
    if (formsIsland && Array.isArray(formsIsland.forms)) {
      for (let i = 0; i < formsIsland.forms.length; i += 1) {
        const entry = formsIsland.forms[i];
        if (entry && entry.form_id) { formEntriesById[entry.form_id] = entry; }
      }
    }

    let selectedChoice = (options && options.formId) || 'A';
    if (formEntriesById[selectedChoice] && formEntriesById[selectedChoice].status === 'SHORTAGE') {
      const avail = ['A', 'B', 'C'].filter(function (id: string): boolean {
        return formEntriesById[id] && formEntriesById[id].status === 'AVAILABLE';
      });
      if (avail.length > 0 && !(options && options.formId)) { selectedChoice = avail[0]; }
    }

    let app: ExamApp | null = null;
    let activeManifest: any = null;
    let activeInstancesById: Record<string, any> = bankData.byId;

    const startButton = doc.getElementById('exam-start');
    const entry = doc.getElementById('exam-entry');
    const shellNode = doc.getElementById('exam-shell');

    const readSeedValue = function (): string {
      const examInput = doc.getElementById('exam-seed-input');
      const sakumsInput = doc.getElementById('sakums-seed-input');
      const raw = (examInput && examInput.value) || (sakumsInput && sakumsInput.value) || '101001';
      return String(raw);
    };

    const syncSeedInputs = function (val: string): void {
      const examInput = doc.getElementById('exam-seed-input');
      const sakumsInput = doc.getElementById('sakums-seed-input');
      if (examInput && examInput.value !== val) { examInput.value = val; }
      if (sakumsInput && sakumsInput.value !== val) { sakumsInput.value = val; }
    };

    const renderPickerState = function (): void {
      const choices = ['A', 'B', 'C', 'SEEDED'];
      const prefixes = ['sakums', 'exam'];
      const selectedEntry = formEntriesById[selectedChoice];
      const isSelectedDisabled = Boolean(selectedEntry && selectedEntry.status === 'SHORTAGE');
      const reasonText = isSelectedDisabled
        ? String(selectedEntry.disabled_reason_lv || (selectedChoice + ' forma pagaidām nav pieejama: gaida recenziju.'))
        : '';

      /* Collect any shortage message across forms so disabled forms always expose an accessible reason. */
      const shortageNotes: string[] = [];
      ['A', 'B', 'C'].forEach(function (fid: string): void {
        const f = formEntriesById[fid];
        if (f && f.status === 'SHORTAGE' && f.disabled_reason_lv) {
          shortageNotes.push(String(f.disabled_reason_lv));
        }
      });

      for (let p = 0; p < prefixes.length; p += 1) {
        const pref = prefixes[p];
        for (let c = 0; c < choices.length; c += 1) {
          const cid = choices[c];
          const btn = doc.getElementById(pref + '-pick-' + cid);
          if (!btn) { continue; }
          const formObj = formEntriesById[cid];
          const disabled = Boolean(formObj && formObj.status === 'SHORTAGE');
          btn.disabled = disabled;
          btn.setAttribute('aria-disabled', disabled ? 'true' : 'false');
          btn.setAttribute('aria-checked', selectedChoice === cid ? 'true' : 'false');
          if (disabled) {
            btn.setAttribute('aria-describedby', pref === 'sakums' ? 'sakums-form-reason' : 'exam-form-shortage');
          } else if (typeof btn.removeAttribute === 'function') {
            btn.removeAttribute('aria-describedby');
          }
        }
        const seedWrap = doc.getElementById(pref + '-seed-wrap');
        if (seedWrap) { seedWrap.hidden = selectedChoice !== 'SEEDED'; }
      }

      const sakumsReason = doc.getElementById('sakums-form-reason');
      if (sakumsReason) {
        sakumsReason.textContent = shortageNotes.join(' ');
        sakumsReason.hidden = shortageNotes.length === 0;
      }
      const examShortage = doc.getElementById('exam-form-shortage');
      if (examShortage) {
        examShortage.textContent = reasonText || shortageNotes.join(' ');
        examShortage.hidden = !reasonText && shortageNotes.length === 0;
      }
      const sakumsSummary = doc.getElementById('sakums-form-selected-summary');
      if (sakumsSummary) {
        sakumsSummary.textContent = isSelectedDisabled
          ? reasonText
          : (selectedChoice === 'SEEDED'
            ? 'Izvēlēts sēklots treniņa zīmējums (sēkla ' + readSeedValue() + ', 21 vieta, 100 punkti, PROPOSED).'
            : 'Izvēlēta ' + selectedChoice + ' forma (21 vieta, 100 punkti, PROPOSED).');
      }
      const entryNote = doc.getElementById('exam-entry-note');
      if (entryNote) {
        entryNote.textContent = isSelectedDisabled
          ? reasonText
          : (selectedChoice === 'SEEDED'
            ? 'Sēklots treniņa zīmējums (sēkla ' + readSeedValue() + ', 21 uzdevuma vieta, 100 punkti, PROPOSED). Sesija tiek glabāta tikai operatīvajā atmiņā.'
            : 'Treniņforma ' + selectedChoice + ' (' + policy.exam.slot_count + ' uzdevuma vieta, ' + policy.exam.total_points + ' punkti, PROPOSED). Sesija tiek glabāta tikai operatīvajā atmiņā un pazūd, kad lapa tiek aizvērta.');
      }
      if (startButton) {
        startButton.disabled = isSelectedDisabled;
        startButton.setAttribute('aria-disabled', isSelectedDisabled ? 'true' : 'false');
      }
    };

    const selectForm = function (choice: string): void {
      selectedChoice = choice;
      renderPickerState();
    };

    ['sakums', 'exam'].forEach(function (pref: string): void {
      ['A', 'B', 'C', 'SEEDED'].forEach(function (cid: string): void {
        const btn = doc.getElementById(pref + '-pick-' + cid);
        if (btn) {
          btn.addEventListener('click', function (): void {
            if (btn.disabled) { return; }
            selectForm(cid);
          });
        }
      });
      const seedInput = doc.getElementById(pref + '-seed-input');
      if (seedInput) {
        seedInput.addEventListener('input', function (): void {
          syncSeedInputs(String(seedInput.value || '101001'));
          renderPickerState();
        });
      }
    });

    renderPickerState();

    const start = function (): void {
      if (app) { return; }
      const chosenEntry = formEntriesById[selectedChoice];
      if (chosenEntry && chosenEntry.status === 'SHORTAGE') {
        throw new ExamPolicyError(
          'E_EXAM_FORM_DISABLED',
          String(chosenEntry.disabled_reason_lv || (selectedChoice + ' forma pagaidām nav pieejama.'))
        );
      }

      let formForSession: any = { form_id: selectedChoice, slots: policy.slots };
      activeInstancesById = bankData.byId;

      if (selectedChoice === 'SEEDED') {
        const asm = (root as any).SimAssembly;
        if (asm && typeof asm.assembleSeededTrainingForm === 'function' && bankData.list.length > 0) {
          const seedVal = readSeedValue();
          const bankDigest = (formsIsland && formsIsland.bank_digest) || 'runtime-sim-bank';
          const seededRes = asm.assembleSeededTrainingForm({
            seed: seedVal,
            bank: bankData.list,
            bank_digest: bankDigest,
          });
          if (seededRes.status === 'SHORTAGE') {
            throw new ExamPolicyError('E_EXAM_FORM_DISABLED', seededRes.shortage.disabled_reason_lv);
          }
          activeManifest = seededRes.manifest;
          activeInstancesById = seededRes.instances_by_id || bankData.byId;
          formForSession = activeManifest;
        }
      } else if (chosenEntry && chosenEntry.status === 'AVAILABLE' && Array.isArray(chosenEntry.slots)) {
        activeManifest = chosenEntry;
        formForSession = chosenEntry;
      }

      const session = new (root as any).SimSession.ExamSession({
        policy: policy,
        form: formForSession,
        sessionId: 'SES-' + formForSession.form_id + '-N24',
      });
      session.dispatch('start');
      const shell = new ExamShell({
        policy: policy,
        session: session,
        doc: doc,
        manifest: activeManifest,
        instancesById: activeInstancesById,
      });
      shell.render();
      shell.bindKeyboard();
      shell.startTimer();
      if (entry) { entry.hidden = true; }
      if (shellNode) { shellNode.hidden = false; }
      app = { shell: shell, session: session, policy: policy, manifest: activeManifest };
      bindControls(doc, app);
    };

    if (startButton) {
      startButton.addEventListener('click', start);
    }

    /* The controls are bound once the session exists; until then they do
     * nothing, because there is no session to act on. */
    function bindControls(document2: any, current: ExamApp): void {
      const prev = document2.getElementById('exam-prev');
      const next = document2.getElementById('exam-next');
      const flag = document2.getElementById('exam-flag');
      const review = document2.getElementById('exam-review-button');
      if (prev) {
        prev.addEventListener('click', function (): void {
          const snapshot = current.session.snapshot();
          const ids = snapshot.slot_ids;
          const index = ids.indexOf(snapshot.current_slot_id);
          if (index > 0) { current.shell.navigate(ids[index - 1]); }
        });
      }
      if (next) {
        next.addEventListener('click', function (): void {
          const snapshot = current.session.snapshot();
          const ids = snapshot.slot_ids;
          const index = ids.indexOf(snapshot.current_slot_id);
          if (index >= 0 && index < ids.length - 1) { current.shell.navigate(ids[index + 1]); }
        });
      }
      if (flag) {
        flag.addEventListener('click', function (): void { current.shell.toggleFlag(); });
      }
      if (review) {
        review.addEventListener('click', function (): void { current.shell.requestReview(); });
      }
    }

    return {
      get shell(): ExamShell | null {
        return app ? app.shell : null;
      },
      get session(): any {
        return app ? app.session : null;
      },
      get policy(): any {
        return app ? app.policy : policy;
      },
      get manifest(): any {
        return activeManifest;
      },
      get selectedFormId(): string {
        return selectedChoice;
      },
      selectForm: selectForm,
      start: start,
    } as ExamApp;
  }

  /* ----------------------------------------------------------------- export */

  const api = {
    ExamShell: ExamShell,
    ExamPolicyError: ExamPolicyError,
    ModeRegistryError: ModeRegistryError,
    createModeRegistry: createModeRegistry,
    buildMapState: buildMapState,
    buildReviewState: buildReviewState,
    buildTimerState: buildTimerState,
    renderPracticeSurface: renderPracticeSurface,
    loadPolicy: loadPolicy,
    loadFormsIsland: loadFormsIsland,
    init: init,
    formatClock: formatClock,
  };

  root.SimExam = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
