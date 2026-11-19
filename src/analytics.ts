/* N25 — local, privacy-safe analytics and honest progress record.
 *
 * Boundary note (F10):
 *   The predecessor plan's F10 (analytics dashboards, completionist charts,
 *   streaks and gamification) is REJECTED by workspace policy
 *   (Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md §4.3 &
 *   evidence/VERIFICATION_LEDGER.md). Completionist visualization serves the
 *   tracker, not the learner. This module exports ZERO chart, streak,
 *   gamification, or score-history components; it provides only an honest,
 *   unblended, opt-in local progress summary (#atskats).
 */
(function (this: void, root: any): void {
  'use strict';

  const ISLAND_ID = 'sim-analytics';
  const SCHEMA_VERSION = 2;

  const EVENT_SESSION = 'session-completed';
  const EVENT_TASK = 'task-answered';
  const EVENT_REMEDIATION = 'remediation-state';

  const STATE_GRADED = 'graded';
  const STATE_INCOMPLETE = 'incomplete';
  const STATE_INVALID = 'invalid';
  const STATE_UNATTEMPTED = 'unattempted';

  const ERRORS = [
    'E_ANALYTICS_SCHEMA',
    'E_ANALYTICS_GRADED_DIGEST',
    'E_ANALYTICS_REMEDIATION_NOT_FOUND'
  ];

  const F10_BOUNDARY = {
    rejected_feature: 'F10',
    status: 'rejected-by-policy',
    ledger_reference: 'Coriculum_chemistry_sim1_MASTER_SIM_40_TASK_ROADMAP.md §4.3 (F10 REJECTED) & evidence/VERIFICATION_LEDGER.md',
    reasoning_lv: 'F10 vizuālie atskaišu paneļi, sērijas (streaks) un spēļošana ir noraidīti ar politiku: tie kalpo izsekotājam, nevis izglītojamam.',
    reasoning_en: 'Completionist visualization serves the tracker, not the learner; no chart, streak, or score-history components are exported.',
    forbidden_exports: ['chart', 'charts', 'streak', 'streaks', 'gamification', 'scoreHistory', 'score_history', 'dashboard', 'leaderboard']
  };

  class AnalyticsError extends Error {
    public readonly code: string;
    public readonly details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super(message);
      this.name = 'AnalyticsError';
      this.code = code;
      this.details = details || {};
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, AnalyticsError);
      } else {
        this.stack = new Error(message).stack;
      }
    }
  }

  function fail(code: string, message: string, details?: Record<string, unknown>): never {
    throw new AnalyticsError(code, message, details);
  }

  function isObject(value: unknown): value is Record<string, any> {
    return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
  }

  function isText(value: unknown): value is string {
    return typeof value === 'string';
  }

  function has(source: Record<string, unknown>, key: string): boolean {
    return Object.prototype.hasOwnProperty.call(source, key);
  }

  function pushUnique(list: string[], value: string): void {
    if (value === '' || list.indexOf(value) >= 0) { return; }
    list.push(value);
  }

  function getStoreApi(): any {
    const api = (root as any).SimStore;
    if (!api || typeof api.digestOf !== 'function') {
      return fail('E_ANALYTICS_SCHEMA', 'SimStore modulis nav ielādēts.', {});
    }
    return api;
  }

  function loadSchema(doc: unknown): Record<string, unknown> {
    if (isObject(doc) && doc.island_id === ISLAND_ID) {
      if (doc.schema_version !== SCHEMA_VERSION) {
        return fail('E_ANALYTICS_SCHEMA', 'Analītikas salas schema_version neatbilst v2.', {
          schema_version: doc.schema_version
        });
      }
      return doc as Record<string, unknown>;
    }
    if (!doc || typeof (doc as any).getElementById !== 'function') {
      return fail('E_ANALYTICS_SCHEMA', 'Nav dokumenta analītikas salas ielādei.', {});
    }
    const node = (doc as any).getElementById(ISLAND_ID);
    if (!node || !isText(node.textContent) || node.textContent === '') {
      return fail('E_ANALYTICS_SCHEMA', 'Sala #' + ISLAND_ID + ' nav atrasta vai ir tukša.', {});
    }
    let parsed: unknown;
    try {
      parsed = JSON.parse(node.textContent);
    } catch (error) {
      return fail('E_ANALYTICS_SCHEMA', 'Sala #' + ISLAND_ID + ' nav derīgs JSON.', { reason: String(error) });
    }
    if (!isObject(parsed) || parsed.island_id !== ISLAND_ID || parsed.schema_version !== SCHEMA_VERSION) {
      return fail('E_ANALYTICS_SCHEMA', 'Salas #' + ISLAND_ID + ' shēma neatbilst N25 v2 līgumam.', {});
    }
    if (!isObject(parsed.f10_boundary) || parsed.f10_boundary.status !== 'rejected-by-policy') {
      return fail('E_ANALYTICS_SCHEMA', 'Analītikas salā trūkst F10 noraidījuma robežas.', {});
    }
    return parsed as Record<string, unknown>;
  }

  /* -------------------------------------------------------- pure event chain */

  /**
   * Pure function chain: GradedRecord in -> digest-linked events out.
   * Zero wall-clock dependence, zero answer text, zero mutation.
   * Matches SimGrading.toAnalyticsEvents byte-for-byte over canonical JSON.
   */
  function extractEvents(fullRecord: unknown): Array<Record<string, unknown>> {
    if (!isObject(fullRecord) || fullRecord.record_kind !== 'graded-record') {
      return fail('E_ANALYTICS_SCHEMA', 'Analītikai nepieciešams N23 vērtēšanas ieraksts (graded-record).', {});
    }
    if (!isText(fullRecord.digest) || fullRecord.digest === '') {
      return fail('E_ANALYTICS_GRADED_DIGEST', 'Vērtēšanas ierakstam nav digest lauka.', {});
    }
    const storeApi = getStoreApi();
    const expectedDigest = storeApi.digestOf(fullRecord);
    if (expectedDigest !== fullRecord.digest) {
      return fail('E_ANALYTICS_GRADED_DIGEST', 'Vērtēšanas ieraksta digest neatbilst saturam.', {
        expected: expectedDigest,
        actual: fullRecord.digest
      });
    }
    const digest = fullRecord.digest as string;
    const session = isObject(fullRecord.session) ? fullRecord.session : {};
    const totals = isObject(fullRecord.totals) ? fullRecord.totals : {};
    const slots = Array.isArray(fullRecord.slots) ? fullRecord.slots as Array<Record<string, any>> : [];
    const feedback = isObject(fullRecord.feedback) ? fullRecord.feedback : null;
    const items = feedback && Array.isArray(feedback.items) ? feedback.items as Array<Record<string, any>> : [];

    let pendingCount = 0;
    for (let i = 0; i < slots.length; i += 1) {
      const task = isObject(slots[i].task) ? slots[i].task : {};
      if (Number(task.pending_points || 0) > 0) { pendingCount += 1; }
    }

    const events: Array<Record<string, unknown>> = [{
      event: EVENT_SESSION,
      form_id: session.form_id,
      session_id: session.session_id,
      auto_score: totals.auto_points,
      pending_count: pendingCount,
      elapsed_ms: session.elapsed_ms,
      graded_digest: digest
    }];

    const bySlot: Record<string, Array<Record<string, any>>> = {};
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      if (!isObject(item) || !isText(item.slot_id)) { continue; }
      if (!has(bySlot, item.slot_id)) { bySlot[item.slot_id] = []; }
      bySlot[item.slot_id].push(item);
    }

    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      if (slot.state === STATE_UNATTEMPTED) { continue; }
      const verdicts: Array<Record<string, unknown>> = [];
      const criteria = Array.isArray(slot.criteria) ? slot.criteria : [];
      for (let c = 0; c < criteria.length; c += 1) {
        const criterion = criteria[c];
        verdicts.push({
          criterion_id: criterion.criterion_id,
          status: criterion.status,
          verdict_class: criterion.verdict_class,
          error_class: criterion.error_class
        });
      }
      events.push({
        event: EVENT_TASK,
        slot_id: slot.slot_id,
        topic: slot.topic,
        family_id: slot.family_id,
        type_id: slot.type_id,
        criterion_verdicts: verdicts,
        graded_digest: digest
      });
    }

    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      const needsRemediation = slot.state === STATE_INVALID || slot.state === STATE_INCOMPLETE ||
        (slot.state === STATE_GRADED && slot.verdict_class === 'incorrect');
      if (!needsRemediation) { continue; }
      const slotItems = has(bySlot, slot.slot_id) ? bySlot[slot.slot_id] : [];
      const conceptIds: string[] = [];
      const chainIds: string[] = [];
      let signatureId: string | null = null;
      for (let s = 0; s < slotItems.length; s += 1) {
        const item = slotItems[s];
        if (signatureId === null && isText(item.signature_id) && item.signature_id !== '') {
          signatureId = item.signature_id;
        }
        const remediation = isObject(item.remediation) ? item.remediation : null;
        if (!remediation) { continue; }
        if (Array.isArray(remediation.concept_ids)) {
          for (let c = 0; c < remediation.concept_ids.length; c += 1) {
            const id = remediation.concept_ids[c];
            if (isText(id) && id !== '') { pushUnique(conceptIds, id); }
          }
        }
        if (Array.isArray(remediation.chain_ids)) {
          for (let c = 0; c < remediation.chain_ids.length; c += 1) {
            const id = remediation.chain_ids[c];
            if (isText(id) && id !== '') { pushUnique(chainIds, id); }
          }
        }
      }
      if (conceptIds.length === 0 && chainIds.length === 0 && signatureId === null) { continue; }
      events.push({
        event: EVENT_REMEDIATION,
        slot_id: slot.slot_id,
        state: 'open',
        concept_ids: conceptIds,
        chain_ids: chainIds,
        signature_id: signatureId,
        graded_digest: digest
      });
    }
    return events;
  }

  function isAutoCorrectSlot(slot: Record<string, any>): boolean {
    if (slot.state !== STATE_GRADED) { return false; }
    if (slot.verdict_class === 'correct') { return true; }
    if (slot.verdict_class === 'auto_passed_pending_review') {
      const task = isObject(slot.task) ? slot.task : {};
      const autoMax = Number(task.auto_max_points || 0);
      const autoPts = Number(task.auto_points || 0);
      return autoMax > 0 && autoPts === autoMax;
    }
    return false;
  }

  function recomputeOutcomeRollups(draft: any): void {
    const outcomes = draft.progress.outcomes || {};
    const allCorrectOnce: string[] = [];
    const allFirstPass: string[] = [];
    const byTopicCorrect: Record<string, string[]> = { '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [] };
    const byTopicFirst: Record<string, string[]> = { '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [] };

    const ids = Object.keys(outcomes).sort();
    for (let i = 0; i < ids.length; i += 1) {
      const oid = ids[i];
      const st = outcomes[oid];
      if (!st) { continue; }
      const m = /^P([1-7])-/.exec(oid);
      if (Number(st.correct_count || 0) > 0) {
        allCorrectOnce.push(oid);
        if (m && byTopicCorrect[m[1]]) { byTopicCorrect[m[1]].push(oid); }
      }
      if (st.first_attempt_correct === true) {
        allFirstPass.push(oid);
        if (m && byTopicFirst[m[1]]) { byTopicFirst[m[1]].push(oid); }
      }
    }
    draft.progress.outcomes_correct_once = allCorrectOnce;
    draft.progress.outcomes_first_pass = allFirstPass;
    for (let t = 1; t <= 7; t += 1) {
      const tk = String(t);
      draft.progress.topics[tk].outcomes_correct_once = byTopicCorrect[tk];
      draft.progress.topics[tk].outcomes_first_pass = byTopicFirst[tk];
    }
  }

  function nextQueueSeq(queue: Array<Record<string, any>>): number {
    let maxSeq = 0;
    for (let i = 0; i < queue.length; i += 1) {
      const o = Number(queue[i].opened_seq || 0);
      const r = Number(queue[i].resolved_seq || 0);
      if (o > maxSeq) { maxSeq = o; }
      if (r > maxSeq) { maxSeq = r; }
    }
    return maxSeq + 1;
  }

  function ingestGradedRecord(store: any, fullRecord: unknown): {
    events: Array<Record<string, unknown>>;
    state: Record<string, unknown>;
  } {
    const events = extractEvents(fullRecord);
    const record = fullRecord as Record<string, any>;
    const session = record.session as Record<string, any>;
    const totals = record.totals as Record<string, any>;
    const slots = Array.isArray(record.slots) ? record.slots as Array<Record<string, any>> : [];
    const feedback = isObject(record.feedback) ? record.feedback : null;
    const fbItems = feedback && Array.isArray(feedback.items) ? feedback.items as Array<Record<string, any>> : [];

    const bySlotFb: Record<string, Array<Record<string, any>>> = {};
    for (let i = 0; i < fbItems.length; i += 1) {
      const item = fbItems[i];
      if (!isObject(item) || !isText(item.slot_id)) { continue; }
      if (!has(bySlotFb, item.slot_id)) { bySlotFb[item.slot_id] = []; }
      bySlotFb[item.slot_id].push(item);
    }

    let pendingCount = 0;
    for (let i = 0; i < slots.length; i += 1) {
      if (slots[i].task && Number(slots[i].task.pending_points || 0) > 0) { pendingCount += 1; }
    }

    const nextState = store.update(function (draft: any): void {
      const seenSessionTopics: Record<string, boolean> = {};

      draft.progress.form_history.push({
        session_id: session.session_id,
        form_id: session.form_id,
        auto_points: totals.auto_points,
        auto_max_points: totals.auto_max_points,
        pending_external_points: totals.pending_external_points,
        pending_max_points: totals.pending_max_points,
        pending_count: pendingCount,
        elapsed_ms: session.elapsed_ms,
        unblended: true,
        graded_digest: record.digest
      });

      for (let i = 0; i < slots.length; i += 1) {
        const slot = slots[i];
        if (slot.state === STATE_UNATTEMPTED) { continue; }
        const tk = String(slot.topic);
        if (has(draft.progress.topics, tk)) {
          draft.progress.topics[tk].practiced_tasks += 1;
          if (!has(seenSessionTopics, tk)) {
            seenSessionTopics[tk] = true;
            draft.progress.topics[tk].practiced_sessions += 1;
          }
        }
        const autoCorrect = isAutoCorrectSlot(slot);
        const oids = Array.isArray(slot.outcome_ids) ? slot.outcome_ids : [];
        for (let j = 0; j < oids.length; j += 1) {
          const oid = oids[j];
          if (!isText(oid) || oid === '') { continue; }
          const stat = draft.progress.outcomes[oid] || {
            attempts: 0,
            first_attempt_correct: null,
            correct_count: 0
          };
          if (stat.attempts === 0) {
            stat.first_attempt_correct = autoCorrect;
          }
          stat.attempts += 1;
          if (autoCorrect) {
            stat.correct_count += 1;
          }
          draft.progress.outcomes[oid] = stat;
        }
      }

      recomputeOutcomeRollups(draft);

      if ((root as any).SimRemediation && typeof (root as any).SimRemediation.applyGradedRecordDraft === 'function') {
        (root as any).SimRemediation.applyGradedRecordDraft(draft, fullRecord, {
          doc: (root as any).document || null
        });
      } else {
      for (let i = 0; i < slots.length; i += 1) {
        const slot = slots[i];
        const needsRemediation = slot.state === STATE_INVALID || slot.state === STATE_INCOMPLETE ||
          (slot.state === STATE_GRADED && slot.verdict_class === 'incorrect');
        if (!needsRemediation) { continue; }
        const slotItems = has(bySlotFb, slot.slot_id) ? bySlotFb[slot.slot_id] : [];
        const conceptIds: string[] = [];
        const chainIds: string[] = [];
        let methodCard: { card_id: string; step_id: string } | null = null;
        let signatureId: string | null = null;

        for (let s = 0; s < slotItems.length; s += 1) {
          const item = slotItems[s];
          if (signatureId === null && isText(item.signature_id) && item.signature_id !== '') {
            signatureId = item.signature_id;
          }
          const rem = isObject(item.remediation) ? item.remediation : null;
          if (!rem) { continue; }
          if (Array.isArray(rem.concept_ids)) {
            for (let c = 0; c < rem.concept_ids.length; c += 1) {
              if (isText(rem.concept_ids[c])) { pushUnique(conceptIds, rem.concept_ids[c]); }
            }
          }
          if (Array.isArray(rem.chain_ids)) {
            for (let c = 0; c < rem.chain_ids.length; c += 1) {
              if (isText(rem.chain_ids[c])) { pushUnique(chainIds, rem.chain_ids[c]); }
            }
          }
          if (methodCard === null && isObject(rem.method_card) &&
              isText(rem.method_card.card_id) && isText(rem.method_card.step_id)) {
            methodCard = { card_id: rem.method_card.card_id, step_id: rem.method_card.step_id };
          }
        }

        if (conceptIds.length === 0 && chainIds.length === 0 && methodCard === null && signatureId === null) {
          continue;
        }

        const itemId = String(slot.slot_id) + '::' + String(slot.instance_id || '');
        const seq = nextQueueSeq(draft.remediation_queue);
        let existing: Record<string, any> | null = null;
        for (let q = 0; q < draft.remediation_queue.length; q += 1) {
          if (draft.remediation_queue[q].id === itemId) {
            existing = draft.remediation_queue[q];
            break;
          }
        }
        if (existing) {
          existing.state = 'open';
          existing.concept_ids = conceptIds;
          existing.chain_ids = chainIds;
          existing.method_card = methodCard;
          existing.signature_id = signatureId;
          existing.graded_digest = record.digest;
          existing.opened_seq = seq;
          existing.resolved_seq = null;
        } else {
          draft.remediation_queue.push({
            id: itemId,
            slot_id: slot.slot_id,
            topic: Number(slot.topic || 0),
            family_id: isText(slot.family_id) ? slot.family_id : '',
            instance_id: isText(slot.instance_id) ? slot.instance_id : '',
            signature_id: signatureId,
            concept_ids: conceptIds,
            chain_ids: chainIds,
            method_card: methodCard,
            graded_digest: record.digest,
            state: 'open',
            opened_seq: seq,
            resolved_seq: null
          });
        }
      }
      }

      for (let i = 0; i < events.length; i += 1) {
        draft.events.push(events[i]);
      }

      if ((root as any).SimMastery && typeof (root as any).SimMastery.applyGradedRecordDraft === 'function') {
        (root as any).SimMastery.applyGradedRecordDraft(draft, fullRecord);
      }
    });

    return { events: events, state: nextState };
  }

  function appendEvents(store: any, events: Array<Record<string, unknown>>): Record<string, unknown> {
    if (!Array.isArray(events)) {
      return fail('E_ANALYTICS_SCHEMA', 'Notikumiem jābūt sarakstam.', {});
    }
    return store.update(function (draft: any): void {
      for (let i = 0; i < events.length; i += 1) {
        if (isObject(events[i])) {
          draft.events.push(events[i]);
        }
      }
    });
  }

  function resolveRemediationItem(store: any, itemId: string): {
    resolved: Record<string, unknown>;
    state: Record<string, unknown>;
  } {
    let resolvedItem: Record<string, any> | null = null;
    const nextState = store.update(function (draft: any): void {
      const queue = draft.remediation_queue || [];
      for (let i = 0; i < queue.length; i += 1) {
        if (queue[i].id === itemId || (queue[i].slot_id === itemId && queue[i].state === 'open')) {
          resolvedItem = queue[i];
          break;
        }
      }
      if (!resolvedItem) {
        return fail('E_ANALYTICS_REMEDIATION_NOT_FOUND', 'Atkārtošanas rindā nav ieraksta "' + itemId + '".', {
          id: itemId
        });
      }
      resolvedItem.state = 'resolved';
      resolvedItem.resolved_seq = nextQueueSeq(queue);
      draft.events.push({
        event: EVENT_REMEDIATION,
        slot_id: resolvedItem.slot_id,
        state: 'resolved',
        concept_ids: (resolvedItem.concept_ids || []).slice(),
        chain_ids: (resolvedItem.chain_ids || []).slice(),
        signature_id: resolvedItem.signature_id || null,
        graded_digest: resolvedItem.graded_digest || ''
      });
    });
    return {
      resolved: resolvedItem as unknown as Record<string, unknown>,
      state: nextState
    };
  }

  /* ----------------------------------------------------------- progress view */

  function outcomeStatusOf(stat: Record<string, any> | undefined): 'unattempted' | 'attempted' | 'first_pass_correct' | 'correct_after_retry' {
    if (!stat || Number(stat.attempts || 0) === 0) {
      return 'unattempted';
    }
    if (stat.first_attempt_correct === true) {
      return 'first_pass_correct';
    }
    if (Number(stat.correct_count || 0) > 0) {
      return 'correct_after_retry';
    }
    return 'attempted';
  }

  function buildProgressSummary(state: Record<string, any>, coverage: Record<string, any> | null) {
    const covTopics = coverage && Array.isArray(coverage.topics) ? coverage.topics : [];
    const covOutcomes = coverage && Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
    const progress = isObject(state.progress) ? state.progress : {};
    const topicProgress = isObject(progress.topics) ? progress.topics : {};
    const outcomesMap = isObject(progress.outcomes) ? progress.outcomes : {};
    const formHistory = Array.isArray(progress.form_history) ? progress.form_history : [];
    const remQueue = Array.isArray(state.remediation_queue) ? state.remediation_queue : [];

    const outcomeRows: Array<{
      id: string;
      topic: number;
      statement_lv: string;
      master_anchor: string;
      status: 'unattempted' | 'attempted' | 'first_pass_correct' | 'correct_after_retry';
      attempts: number;
      correct_count: number;
    }> = [];

    const topicOutcomeTotal: Record<string, number> = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 };
    const topicOutcomeCorrect: Record<string, number> = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 };
    const topicOutcomeFirst: Record<string, number> = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 };

    for (let i = 0; i < covOutcomes.length; i += 1) {
      const oc = covOutcomes[i];
      const tk = String(oc.topic);
      const stat = outcomesMap[oc.id];
      const status = outcomeStatusOf(stat);
      if (has(topicOutcomeTotal, tk)) { topicOutcomeTotal[tk] += 1; }
      if (status === 'first_pass_correct' || status === 'correct_after_retry') {
        if (has(topicOutcomeCorrect, tk)) { topicOutcomeCorrect[tk] += 1; }
      }
      if (status === 'first_pass_correct') {
        if (has(topicOutcomeFirst, tk)) { topicOutcomeFirst[tk] += 1; }
      }
      outcomeRows.push({
        id: oc.id,
        topic: Number(oc.topic),
        statement_lv: oc.statement_lv || '',
        master_anchor: oc.master_anchor || '',
        status: status,
        attempts: stat ? Number(stat.attempts || 0) : 0,
        correct_count: stat ? Number(stat.correct_count || 0) : 0
      });
    }

    const topicNameById: Record<string, string> = {};
    for (let i = 0; i < covTopics.length; i += 1) {
      topicNameById[String(covTopics[i].topic)] = covTopics[i].name_lv || (String(covTopics[i].topic) + '. tēma');
    }

    const topicRows: Array<{
      topic: number;
      name_lv: string;
      practiced_tasks: number;
      practiced_sessions: number;
      outcomes_total: number;
      outcomes_correct_once: number;
      outcomes_first_pass: number;
      zero_activity: boolean;
    }> = [];

    let totalPracticedTasks = 0;
    for (let t = 1; t <= 7; t += 1) {
      const tk = String(t);
      const tp = isObject(topicProgress[tk]) ? topicProgress[tk] : {};
      const practicedTasks = Number(tp.practiced_tasks || 0);
      const practicedSessions = Number(tp.practiced_sessions || 0);
      totalPracticedTasks += practicedTasks;
      const tot = topicOutcomeTotal[tk] || 0;
      const corr = topicOutcomeCorrect[tk] || 0;
      const first = topicOutcomeFirst[tk] || 0;
      topicRows.push({
        topic: t,
        name_lv: topicNameById[tk] || (tk + '. tēma'),
        practiced_tasks: practicedTasks,
        practiced_sessions: practicedSessions,
        outcomes_total: tot,
        outcomes_correct_once: corr,
        outcomes_first_pass: first,
        zero_activity: practicedTasks === 0 && practicedSessions === 0 && corr === 0
      });
    }

    const openRem: Array<Record<string, any>> = [];
    const resolvedRem: Array<Record<string, any>> = [];
    for (let i = 0; i < remQueue.length; i += 1) {
      if (remQueue[i].state === 'resolved') { resolvedRem.push(remQueue[i]); }
      else { openRem.push(remQueue[i]); }
    }

    const outcomesCorrectOnceCount = outcomeRows.length > 0
      ? outcomeRows.filter(function (r) { return r.status === 'first_pass_correct' || r.status === 'correct_after_retry'; }).length
      : (Array.isArray(progress.outcomes_correct_once) ? progress.outcomes_correct_once.length : 0);
    const outcomesFirstPassCount = outcomeRows.length > 0
      ? outcomeRows.filter(function (r) { return r.status === 'first_pass_correct'; }).length
      : (Array.isArray(progress.outcomes_first_pass) ? progress.outcomes_first_pass.length : 0);

    return {
      sessions_count: formHistory.length,
      total_practiced_tasks: totalPracticedTasks,
      outcomes_total: covOutcomes.length || 64,
      outcomes_correct_once_count: outcomesCorrectOnceCount,
      outcomes_first_pass_count: outcomesFirstPassCount,
      topics: topicRows,
      outcomes: outcomeRows,
      form_history: formHistory.slice(),
      open_remediation_count: openRem.length,
      open_remediation: openRem,
      resolved_remediation_count: resolvedRem.length,
      events_count: Array.isArray(state.events) ? state.events.length : 0,
      events_pruned_count: Number(state.events_pruned_count || 0),
      has_activity: formHistory.length > 0 || totalPracticedTasks > 0 || (Array.isArray(state.events) && state.events.length > 0)
    };
  }

  /* ---------------------------------------------------------------- DOM UI */

  function clearNode(node: any): void {
    if (!node) { return; }
    while (node.firstChild) { node.removeChild(node.firstChild); }
  }

  function makeEl(doc: any, tag: string, className?: string | null, text?: string | null): any {
    const el = doc.createElement(tag);
    if (className) { el.className = className; }
    if (text !== undefined && text !== null) { el.textContent = String(text); }
    return el;
  }

  function formatDuration(ms: number): string {
    const total = Math.max(0, Math.floor(Number(ms || 0) / 1000));
    const m = Math.floor(total / 60);
    const s = total % 60;
    return (m < 10 ? '0' + m : String(m)) + ':' + (s < 10 ? '0' + s : String(s));
  }

  function renderProgressView(
    doc: any,
    store: any,
    coverage: Record<string, any> | null,
    schema?: Record<string, any> | null
  ) {
    if (!doc || typeof doc.getElementById !== 'function') { return null; }
    const state = store.getState();
    const summary = buildProgressSummary(state, coverage);
    const copy = (schema && isObject(schema.copy_lv)) ? schema.copy_lv : {};
    const statusLabels = isObject(copy.outcome_states_lv) ? copy.outcome_states_lv : {
      unattempted: 'Nav mēģināts',
      attempted: 'Mēģināts (gaida pareizu atbildi)',
      first_pass_correct: 'Pareizi ar pirmo mēģinājumu',
      correct_after_retry: 'Pareizi pēc atkārtošanas'
    };

    const honestyNode = doc.getElementById('atskats-honesty-note');
    if (honestyNode && isText(copy.honesty_banner)) {
      honestyNode.textContent = copy.honesty_banner;
    }

    const noticeNode = doc.getElementById('atskats-storage-notice');
    if (noticeNode) {
      const storeNotice = store.getNotice();
      if (storeNotice && storeNotice.message_lv) {
        noticeNode.textContent = storeNotice.message_lv;
      } else {
        noticeNode.textContent = store.isOptedIn()
          ? (copy.enabled_state_notice || 'Lokālā saglabāšana pārlūkā (localStorage) ir ieslēgta.')
          : (copy.disabled_state_notice || 'Pēc noklusējuma dati glabājas tikai operatīvajā atmiņā (bez localStorage).');
      }
    }

    const sessionsEl = doc.getElementById('atskats-sessions-count');
    if (sessionsEl) { sessionsEl.textContent = String(summary.sessions_count); }

    const correctEl = doc.getElementById('atskats-outcomes-correct');
    if (correctEl) {
      correctEl.textContent = summary.outcomes_correct_once_count + ' / ' + summary.outcomes_total;
    }

    const firstPassEl = doc.getElementById('atskats-outcomes-first-pass');
    if (firstPassEl) {
      firstPassEl.textContent = summary.outcomes_first_pass_count + ' / ' + summary.outcomes_total;
    }

    const remCountEl = doc.getElementById('atskats-remediation-count');
    if (remCountEl) { remCountEl.textContent = String(summary.open_remediation_count); }

    const zeroEl = doc.getElementById('atskats-zero-notice');
    if (zeroEl) {
      zeroEl.hidden = summary.has_activity;
      if (!summary.has_activity && isText(copy.zero_activity_notice)) {
        zeroEl.textContent = copy.zero_activity_notice;
      }
    }

    const topicsBody = doc.getElementById('atskats-topics-body');
    if (topicsBody) {
      clearNode(topicsBody);
      for (let i = 0; i < summary.topics.length; i += 1) {
        const row = summary.topics[i];
        const tr = makeEl(doc, 'tr');
        tr.setAttribute('data-topic', String(row.topic));
        tr.appendChild(makeEl(doc, 'td', null, row.topic + '. ' + row.name_lv));
        tr.appendChild(makeEl(doc, 'td', null, String(row.practiced_tasks)));
        tr.appendChild(makeEl(doc, 'td', null, row.outcomes_correct_once + ' / ' + row.outcomes_total));
        tr.appendChild(makeEl(doc, 'td', null, row.outcomes_first_pass + ' / ' + row.outcomes_total));
        tr.appendChild(makeEl(doc, 'td', null, row.zero_activity ? '0 (nav aktivitāšu)' : 'Aktīvs'));
        topicsBody.appendChild(tr);
      }
    }

    const formsList = doc.getElementById('atskats-forms-list');
    if (formsList) {
      clearNode(formsList);
      if (summary.form_history.length === 0) {
        formsList.appendChild(makeEl(doc, 'li', 'atskats-empty', 'Nav pabeigtu formu (0 sesijas).'));
      } else {
        for (let i = 0; i < summary.form_history.length; i += 1) {
          const fm = summary.form_history[i];
          const li = makeEl(doc, 'li', 'atskats-form-row');
          li.setAttribute('data-graded-digest', fm.graded_digest || '');
          li.setAttribute('data-unblended', 'true');
          const text = 'Forma ' + fm.form_id + ' (' + fm.session_id + '): '
            + 'automātiski ' + fm.auto_points + '/' + fm.auto_max_points + ' p.'
            + ' | atsevišķi gaida ārējo vērtējumu ' + fm.pending_external_points + '/' + fm.pending_max_points + ' p.'
            + ' (' + fm.pending_count + ' vietas)'
            + ' | laiks ' + formatDuration(fm.elapsed_ms);
          li.textContent = text;
          formsList.appendChild(li);
        }
      }
    }

    const remList = doc.getElementById('atskats-remediation-list');
    if (remList) {
      clearNode(remList);
      if (summary.open_remediation.length === 0) {
        remList.appendChild(makeEl(doc, 'li', 'atskats-empty', 'Atkārtošanas rinda ir tukša (0 atvērtu vienumu).'));
      } else {
        for (let i = 0; i < summary.open_remediation.length; i += 1) {
          const item = summary.open_remediation[i];
          const li = makeEl(doc, 'li', 'atskats-rem-row');
          li.setAttribute('data-remediation-id', item.id);
          li.setAttribute('data-slot-id', item.slot_id);
          const desc = item.slot_id + ' (' + item.family_id + ', ' + item.instance_id + ')'
            + (item.signature_id ? ' — ' + item.signature_id : '')
            + (item.concept_ids && item.concept_ids.length ? ' | koncepti: ' + item.concept_ids.join(', ') : '')
            + (item.chain_ids && item.chain_ids.length ? ' | piemēri: ' + item.chain_ids.join(', ') : '');
          li.appendChild(makeEl(doc, 'span', null, desc));
          remList.appendChild(li);
        }
      }
    }

    const outcomesList = doc.getElementById('atskats-outcomes-list');
    if (outcomesList) {
      clearNode(outcomesList);
      for (let i = 0; i < summary.outcomes.length; i += 1) {
        const oc = summary.outcomes[i];
        const li = makeEl(doc, 'li', 'atskats-outcome-row');
        li.setAttribute('data-outcome-id', oc.id);
        li.setAttribute('data-outcome-status', oc.status);
        const label = statusLabels[oc.status] || oc.status;
        li.textContent = oc.id + ' (' + oc.topic + '. tēma): ' + label + ' — ' + oc.statement_lv;
        outcomesList.appendChild(li);
      }
    }

    return summary;
  }

  function renderSettingsStorage(
    doc: any,
    store: any,
    schema?: Record<string, any> | null
  ): void {
    if (!doc || typeof doc.getElementById !== 'function') { return; }
    const copy = (schema && isObject(schema.copy_lv)) ? schema.copy_lv : {};
    const consentNode = doc.getElementById('store-consent-copy');
    if (consentNode && isText(copy.consent_body)) {
      consentNode.textContent = copy.consent_body;
    }

    const toggleBtn = doc.getElementById('store-opt-in-toggle');
    const optedIn = store.isOptedIn();
    if (toggleBtn) {
      toggleBtn.textContent = optedIn
        ? (copy.opt_in_disable_label || 'Izslēgt lokālo saglabāšanu')
        : (copy.opt_in_enable_label || 'Ieslēgt lokālo saglabāšanu');
      if (typeof toggleBtn.setAttribute === 'function') {
        toggleBtn.setAttribute('aria-pressed', optedIn ? 'true' : 'false');
      }
    }

    const statusNode = doc.getElementById('store-status');
    if (statusNode) {
      statusNode.textContent = optedIn
        ? (copy.enabled_state_notice || 'Lokālā saglabāšana pārlūkā (localStorage) ir ieslēgta.')
        : (copy.disabled_state_notice || 'Pēc noklusējuma dati glabājas tikai operatīvajā atmiņā (bez localStorage).');
    }

    const noticeNode = doc.getElementById('store-notice');
    if (noticeNode) {
      const storeNotice = store.getNotice();
      if (storeNotice && storeNotice.message_lv) {
        noticeNode.textContent = storeNotice.message_lv;
        noticeNode.hidden = false;
      } else {
        noticeNode.textContent = '';
        noticeNode.hidden = true;
      }
    }

    const confirmBox = doc.getElementById('store-erase-confirm-box');
    const confirmPrompt = doc.getElementById('store-erase-prompt');
    if (confirmPrompt && isText(copy.erase_confirm_prompt)) {
      confirmPrompt.textContent = copy.erase_confirm_prompt;
    }
    if (confirmBox) {
      confirmBox.hidden = !store.isErasePending();
    }
  }

  function safeBrowserStorage(): any {
    try {
      return (root as any).localStorage || null;
    } catch (_err) {
      return null;
    }
  }

  function init(doc?: any, options?: {
    store?: any;
    storage?: any;
    coverage?: Record<string, any> | null;
    schema?: Record<string, any> | null;
    probeExisting?: boolean;
  }) {
    doc = doc || (root as any).document;
    if (!doc || typeof doc.getElementById !== 'function') { return null; }
    const opts = options || {};

    let schema: Record<string, any> | null = opts.schema || null;
    if (!schema) {
      try {
        schema = loadSchema(doc);
      } catch (_err) {
        return null;
      }
    }

    let coverage: Record<string, any> | null = opts.coverage || null;
    if (!coverage && (root as any).SimCoverage && typeof (root as any).SimCoverage.load === 'function') {
      try {
        coverage = (root as any).SimCoverage.load(doc, (root as any).COVERAGE_INVARIANTS);
      } catch (_err) {
        coverage = null;
      }
    }

    const storeApi = getStoreApi();
    const storage = opts.storage !== undefined ? opts.storage : safeBrowserStorage();
    const store = opts.store || storeApi.createStore({
      optIn: false,
      probeExisting: opts.probeExisting !== undefined ? Boolean(opts.probeExisting) : Boolean(storage),
      storage: storage,
      doc: doc
    });

    function refresh() {
      renderSettingsStorage(doc, store, schema);
      const progressSummary = renderProgressView(doc, store, coverage, schema);
      if ((root as any).SimMastery && typeof (root as any).SimMastery.renderFromStore === 'function') {
        (root as any).SimMastery.renderFromStore(doc, store, coverage);
      }
      if ((root as any).SimRemediation && typeof (root as any).SimRemediation.renderFromStore === 'function') {
        (root as any).SimRemediation.renderFromStore(doc, store, coverage);
      }
      if ((root as any).SimRevision && typeof (root as any).SimRevision.renderFromStore === 'function') {
        (root as any).SimRevision.renderFromStore(doc, store, coverage);
      }
      return progressSummary;
    }

    /* Restore theme from opted-in store if present, without touching sim_theme_v1. */
    const savedTheme = store.getState().settings.theme;
    if ((savedTheme === 'light' || savedTheme === 'dark') &&
        (root as any).SimTheme && typeof (root as any).SimTheme.applyTheme === 'function') {
      (root as any).SimTheme.applyTheme(doc, savedTheme);
    }

    const themeBtn = doc.getElementById('theme-toggle');
    if (themeBtn && typeof themeBtn.addEventListener === 'function') {
      themeBtn.addEventListener('click', function (): void {
        if (!store.isOptedIn()) { return; }
        const currentTheme = doc.documentElement && typeof doc.documentElement.getAttribute === 'function'
          ? doc.documentElement.getAttribute('data-theme')
          : null;
        if (currentTheme === 'light' || currentTheme === 'dark') {
          store.setTheme(currentTheme);
          refresh();
        }
      });
    }

    const toggleBtn = doc.getElementById('store-opt-in-toggle');
    if (toggleBtn && typeof toggleBtn.addEventListener === 'function') {
      toggleBtn.addEventListener('click', function (): void {
        try {
          store.setOptIn(!store.isOptedIn(), storage);
        } catch (error) {
          const noticeNode = doc.getElementById('store-notice');
          if (noticeNode) {
            noticeNode.textContent = (error as Error).message;
            noticeNode.hidden = false;
          }
          return;
        }
        refresh();
      });
    }

    const exportBtn = doc.getElementById('store-export-btn');
    if (exportBtn && typeof exportBtn.addEventListener === 'function') {
      exportBtn.addEventListener('click', function (): void {
        const exported = store.exportProgress();
        const statusNode = doc.getElementById('store-export-status');
        if (statusNode) {
          const copy = (schema && isObject(schema.copy_lv)) ? schema.copy_lv : {};
          const tmpl = isText(copy.export_ready_notice)
            ? copy.export_ready_notice
            : 'Progresa eksporta fails ir sagatavots: {filename} (SHA-256: {digest}).';
          statusNode.textContent = tmpl
            .split('{filename}').join(exported.filename)
            .split('{digest}').join(exported.store_digest.slice(0, 16) + '...');
          statusNode.hidden = false;
        }
        if (doc.body && typeof doc.createElement === 'function') {
          const link = doc.createElement('a');
          link.setAttribute('download', exported.filename);
          link.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(exported.text));
          if (typeof link.click === 'function') {
            doc.body.appendChild(link);
            link.click();
            if (typeof doc.body.removeChild === 'function') {
              doc.body.removeChild(link);
            }
          }
        }
      });
    }

    const eraseReqBtn = doc.getElementById('store-erase-request');
    if (eraseReqBtn && typeof eraseReqBtn.addEventListener === 'function') {
      eraseReqBtn.addEventListener('click', function (): void {
        store.requestErase();
        refresh();
      });
    }

    const eraseConfirmBtn = doc.getElementById('store-erase-confirm');
    if (eraseConfirmBtn && typeof eraseConfirmBtn.addEventListener === 'function') {
      eraseConfirmBtn.addEventListener('click', function (): void {
        store.confirmErase();
        refresh();
      });
    }

    const eraseCancelBtn = doc.getElementById('store-erase-cancel');
    if (eraseCancelBtn && typeof eraseCancelBtn.addEventListener === 'function') {
      eraseCancelBtn.addEventListener('click', function (): void {
        store.cancelErase();
        refresh();
      });
    }

    refresh();

    return {
      store: store,
      schema: schema,
      coverage: coverage,
      refresh: refresh,
      ingestGradedRecord: function (fullRecord: unknown) {
        const res = ingestGradedRecord(store, fullRecord);
        refresh();
        return res;
      },
      resolveRemediationItem: function (itemId: string) {
        const res = resolveRemediationItem(store, itemId);
        refresh();
        return res;
      }
    };
  }

  const api = {
    ISLAND_ID: ISLAND_ID,
    SCHEMA_VERSION: SCHEMA_VERSION,
    F10_BOUNDARY: F10_BOUNDARY,
    errors: ERRORS.slice(),
    AnalyticsError: AnalyticsError,
    loadSchema: loadSchema,
    extractEvents: extractEvents,
    ingestGradedRecord: ingestGradedRecord,
    appendEvents: appendEvents,
    resolveRemediationItem: resolveRemediationItem,
    buildProgressSummary: buildProgressSummary,
    renderProgressView: renderProgressView,
    renderSettingsStorage: renderSettingsStorage,
    init: init
  };

  root.SimAnalytics = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
