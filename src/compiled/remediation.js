"use strict";
/* N28 — Missed-item remediation queue, study handoffs, and alternate-variant retries.
 *
 * Epistemic & architectural boundaries:
 *   - Policy (deduplication, confirm-required vs auto-resolve, cyclic variant
 *     selection, recommend-only rule) is PROPOSED training policy over
 *     #sim-remediation-policy (official_counterpart_status: UNDETERMINED).
 *   - Recommend-only: never forces remediation gating and never re-grades or
 *     alters original graded attempts.
 *   - Absolute link integrity: validates anchor/chain/method-card links at
 *     write time and re-validates on read/render (dangling links fail loudly
 *     naming the broken id).
 *   - Zero wall-clock millisecond APIs, zero network calls, zero F10 exports,
 *     and zero learner answer text in queue state or handoffs.
 */
(function (root) {
    'use strict';
    const ISLAND_ID = 'sim-remediation-policy';
    const SCHEMA_VERSION = 1;
    const DEFAULT_CYCLE_ORDER = ['A', 'B', 'C', 'D'];
    const ONE_CORRECT_EVIDENCE_COPY_LV = 'Viena pareiza atbilde ir pierādījums virzībai, nevis pilnīga apguve — apstipriniet pabeigšanu manuāli vai praktizējiet tālāk.';
    const ERRORS = [
        'E_REMEDIATION_POLICY_INVALID',
        'E_REMEDIATION_DANGLING_LINK',
        'E_REMEDIATION_NO_LINKS',
        'E_REMEDIATION_NOT_FOUND',
        'E_REMEDIATION_NO_ALTERNATE_VARIANT',
        'E_REMEDIATION_EPHEMERAL_UNAVAILABLE',
        'E_REMEDIATION_DRAWER_UNAVAILABLE',
        'E_REMEDIATION_CHAIN_UNAVAILABLE'
    ];
    class RemediationError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'RemediationError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, RemediationError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new RemediationError(code, message, details);
    }
    function isObject(value) {
        return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
    }
    function isText(value) {
        return typeof value === 'string';
    }
    function has(source, key) {
        return Object.prototype.hasOwnProperty.call(source, key);
    }
    function copyJson(value) {
        return JSON.parse(JSON.stringify(value));
    }
    function uniqueSorted(items) {
        const seen = {};
        const out = [];
        for (let i = 0; i < items.length; i += 1) {
            const item = items[i];
            if (!isText(item) || item === '' || has(seen, item)) {
                continue;
            }
            seen[item] = true;
            out.push(item);
        }
        out.sort();
        return out;
    }
    function pushUniqueOrdered(list, value) {
        if (!isText(value) || value === '' || list.indexOf(value) >= 0) {
            return;
        }
        list.push(value);
    }
    function unionSorted(a, b) {
        return uniqueSorted(a.concat(b));
    }
    function canonicalText(value) {
        if (value === null || value === undefined) {
            return 'null';
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        if (typeof value === 'number') {
            return isFinite(value) ? String(value) : 'null';
        }
        if (typeof value === 'string') {
            return JSON.stringify(value);
        }
        if (Array.isArray(value)) {
            const parts = [];
            for (let i = 0; i < value.length; i += 1) {
                parts.push(canonicalText(value[i]));
            }
            return '[' + parts.join(',') + ']';
        }
        if (typeof value === 'object') {
            const rec = value;
            const keys = Object.keys(rec).sort();
            const parts = [];
            for (let i = 0; i < keys.length; i += 1) {
                if (rec[keys[i]] === undefined) {
                    continue;
                }
                parts.push(JSON.stringify(keys[i]) + ':' + canonicalText(rec[keys[i]]));
            }
            return '{' + parts.join(',') + '}';
        }
        return 'null';
    }
    function sha256Hex(value) {
        const text = typeof value === 'string' ? value : canonicalText(value);
        if (root.SimStore && typeof root.SimStore.digestValue === 'function') {
            return typeof value === 'string'
                ? root.SimStore.digestValue(JSON.parse(JSON.stringify(text)))
                : root.SimStore.digestValue(value);
        }
        if (root.SimMastery && typeof root.SimMastery.digestOfMap === 'function') {
            return root.SimMastery.digestOfMap(value);
        }
        return text;
    }
    /* ---------------------------------------------------------------- policy */
    function validatePolicy(raw) {
        const errors = [];
        if (!isObject(raw)) {
            return { valid: false, errors: ['Remediation policy must be a JSON object'] };
        }
        if (raw.island_id !== ISLAND_ID) {
            errors.push('island_id must be "' + ISLAND_ID + '"');
        }
        if (raw.epistemic_label !== 'PROPOSED') {
            errors.push('epistemic_label must be "PROPOSED"');
        }
        if (raw.official_counterpart_status !== 'UNDETERMINED') {
            errors.push('official_counterpart_status must be "UNDETERMINED"');
        }
        if (raw.recommend_only !== true) {
            errors.push('recommend_only must be true (no forced remediation gating)');
        }
        if (raw.regrade_original_attempt !== false) {
            errors.push('regrade_original_attempt must be false');
        }
        if (raw.require_resolvable_links !== true) {
            errors.push('require_resolvable_links must be true');
        }
        const rp = raw.resolution_policy;
        if (!isObject(rp)) {
            errors.push('resolution_policy must be an object');
        }
        else {
            const supported = Array.isArray(rp.supported_modes) ? rp.supported_modes : [];
            if (supported.indexOf('confirm_required') < 0 || supported.indexOf('one_correct_resolves') < 0) {
                errors.push('resolution_policy.supported_modes must declare confirm_required and one_correct_resolves');
            }
            if (!isText(rp.mode) || supported.indexOf(rp.mode) < 0) {
                errors.push('resolution_policy.mode "' + String(rp.mode) + '" is not in supported_modes');
            }
            if (!isText(rp.one_correct_evidence_copy_lv) || rp.one_correct_evidence_copy_lv.trim() === '') {
                errors.push('resolution_policy.one_correct_evidence_copy_lv is required');
            }
        }
        const vs = raw.variant_selection;
        if (!isObject(vs) || !Array.isArray(vs.cycle_order) || vs.cycle_order.length === 0) {
            errors.push('variant_selection.cycle_order must be a non-empty array');
        }
        else if (vs.never_reserve_failed_instance !== true) {
            errors.push('variant_selection.never_reserve_failed_instance must be true');
        }
        return { valid: errors.length === 0, errors: errors };
    }
    function loadPolicy(doc) {
        if (isObject(doc) && doc.island_id === ISLAND_ID) {
            const check = validatePolicy(doc);
            if (!check.valid) {
                return fail('E_REMEDIATION_POLICY_INVALID', check.errors.join('; '), { errors: check.errors });
            }
            return { policy: copyJson(doc), digest: sha256Hex(doc) };
        }
        const targetDoc = doc || root.document;
        if (!targetDoc || typeof targetDoc.getElementById !== 'function') {
            return fail('E_REMEDIATION_POLICY_INVALID', 'Nav dokumenta atkārtošanas politikas salas ielādei.', {});
        }
        const node = targetDoc.getElementById(ISLAND_ID);
        if (!node || !isText(node.textContent) || node.textContent.trim() === '') {
            return fail('E_REMEDIATION_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav atrasta vai ir tukša.', {});
        }
        let parsed;
        try {
            parsed = JSON.parse(node.textContent);
        }
        catch (err) {
            return fail('E_REMEDIATION_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav derīgs JSON.', { cause: String(err) });
        }
        const check = validatePolicy(parsed);
        if (!check.valid) {
            return fail('E_REMEDIATION_POLICY_INVALID', check.errors.join('; '), { errors: check.errors });
        }
        return { policy: parsed, digest: sha256Hex(parsed) };
    }
    /* ------------------------------------------------------------ registries */
    function parseIslandJson(doc, id) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const node = doc.getElementById(id);
        if (!node || !isText(node.textContent) || node.textContent.trim() === '') {
            return null;
        }
        try {
            const parsed = JSON.parse(node.textContent);
            return isObject(parsed) ? parsed : null;
        }
        catch (_err) {
            return null;
        }
    }
    function buildRegistries(doc, overrides) {
        const opts = overrides || {};
        const targetDoc = doc || root.document;
        const conceptIds = {};
        const anchorsByConcept = {};
        const chainIds = {};
        const methodCards = {};
        let cov = opts.coverage || null;
        if (!cov && targetDoc && root.SimCoverage && typeof root.SimCoverage.load === 'function') {
            try {
                cov = root.SimCoverage.load(targetDoc, root.COVERAGE_INVARIANTS);
            }
            catch (_err) {
                cov = parseIslandJson(targetDoc, 'sim-coverage');
            }
        }
        else if (!cov && targetDoc) {
            cov = parseIslandJson(targetDoc, 'sim-coverage');
        }
        if (cov && Array.isArray(cov.outcomes)) {
            for (let i = 0; i < cov.outcomes.length; i += 1) {
                const oc = cov.outcomes[i];
                if (isObject(oc) && isText(oc.id) && oc.id !== '') {
                    conceptIds[oc.id] = true;
                    anchorsByConcept[oc.id] = isText(oc.master_anchor) && oc.master_anchor !== '' ? oc.master_anchor : oc.id;
                }
            }
        }
        const reg = opts.anchorRegistry || root.ANCHOR_REGISTRY || null;
        if (reg && Array.isArray(reg.concepts)) {
            for (let i = 0; i < reg.concepts.length; i += 1) {
                const c = reg.concepts[i];
                if (isObject(c) && isText(c.concept_id) && c.concept_id !== '') {
                    conceptIds[c.concept_id] = true;
                    if (!has(anchorsByConcept, c.concept_id) && isText(c.master_anchor) && c.master_anchor !== '') {
                        anchorsByConcept[c.concept_id] = c.master_anchor;
                    }
                }
            }
        }
        if (Array.isArray(opts.conceptIds)) {
            for (let i = 0; i < opts.conceptIds.length; i += 1) {
                if (isText(opts.conceptIds[i]) && opts.conceptIds[i] !== '') {
                    conceptIds[opts.conceptIds[i]] = true;
                    if (!has(anchorsByConcept, opts.conceptIds[i])) {
                        anchorsByConcept[opts.conceptIds[i]] = opts.conceptIds[i];
                    }
                }
            }
        }
        let chainsData = opts.chains || null;
        if (!chainsData && targetDoc && root.SimChains && typeof root.SimChains.load === 'function') {
            try {
                chainsData = root.SimChains.load(targetDoc);
            }
            catch (_err) {
                chainsData = parseIslandJson(targetDoc, 'sim-chains');
            }
        }
        else if (!chainsData && targetDoc) {
            chainsData = parseIslandJson(targetDoc, 'sim-chains');
        }
        if (chainsData && Array.isArray(chainsData.chains)) {
            for (let i = 0; i < chainsData.chains.length; i += 1) {
                const ch = chainsData.chains[i];
                if (isObject(ch) && isText(ch.id) && ch.id !== '') {
                    chainIds[ch.id] = true;
                }
            }
        }
        if (Array.isArray(opts.chainIds)) {
            for (let i = 0; i < opts.chainIds.length; i += 1) {
                if (isText(opts.chainIds[i]) && opts.chainIds[i] !== '') {
                    chainIds[opts.chainIds[i]] = true;
                }
            }
        }
        const mcData = opts.methodCards || (targetDoc ? parseIslandJson(targetDoc, 'sim-method-cards') : null);
        if (mcData && Array.isArray(mcData.cards)) {
            for (let i = 0; i < mcData.cards.length; i += 1) {
                const card = mcData.cards[i];
                if (!isObject(card) || !isText(card.card_id) || card.card_id === '') {
                    continue;
                }
                const stepsMap = {};
                if (Array.isArray(card.steps)) {
                    for (let s = 0; s < card.steps.length; s += 1) {
                        if (isObject(card.steps[s]) && isText(card.steps[s].step_id)) {
                            stepsMap[card.steps[s].step_id] = true;
                        }
                    }
                }
                methodCards[card.card_id] = stepsMap;
            }
        }
        return {
            concept_ids: conceptIds,
            anchors_by_concept: anchorsByConcept,
            chain_ids: chainIds,
            method_cards: methodCards
        };
    }
    function validateLinks(links, registries, contextLabel) {
        const concepts = Array.isArray(links.concept_ids) ? links.concept_ids : [];
        const chains = Array.isArray(links.chain_ids) ? links.chain_ids : [];
        if (concepts.length === 0) {
            fail('E_REMEDIATION_NO_LINKS', 'Atkārtošanas ierakstam jābūt vismaz vienai derīgai koncepta enkura saitei.', {
                context: contextLabel || ''
            });
        }
        for (let i = 0; i < concepts.length; i += 1) {
            const cid = concepts[i];
            if (!has(registries.concept_ids, cid)) {
                fail('E_REMEDIATION_DANGLING_LINK', 'Atkārtošanas saite atsaucas uz neeksistējošu koncepta enkuru "' + cid + '".', { kind: 'concept_id', id: cid, anchor: cid, context: contextLabel || '' });
            }
        }
        for (let i = 0; i < chains.length; i += 1) {
            const chId = chains[i];
            if (!has(registries.chain_ids, chId)) {
                fail('E_REMEDIATION_DANGLING_LINK', 'Atkārtošanas saite atsaucas uz neeksistējošu darba piemēra ķēdi "' + chId + '".', { kind: 'chain_id', id: chId, chain_id: chId, context: contextLabel || '' });
            }
        }
        if (links.method_card && isText(links.method_card.card_id) && links.method_card.card_id !== '') {
            const hasCardRegistry = Object.keys(registries.method_cards).length > 0;
            if (hasCardRegistry) {
                const cardSteps = registries.method_cards[links.method_card.card_id];
                if (!cardSteps) {
                    fail('E_REMEDIATION_DANGLING_LINK', 'Atkārtošanas saite atsaucas uz neeksistējošu metodes karti "' + links.method_card.card_id + '".', { kind: 'card_id', id: links.method_card.card_id, context: contextLabel || '' });
                }
                if (isText(links.method_card.step_id) && links.method_card.step_id !== '' && !has(cardSteps, links.method_card.step_id)) {
                    fail('E_REMEDIATION_DANGLING_LINK', 'Metodes kartē "' + links.method_card.card_id + '" nav soļa "' + links.method_card.step_id + '".', { kind: 'step_id', id: links.method_card.step_id, card_id: links.method_card.card_id, context: contextLabel || '' });
                }
            }
        }
    }
    function validateQueueLinks(queue, registries) {
        if (!Array.isArray(queue)) {
            return;
        }
        for (let i = 0; i < queue.length; i += 1) {
            const entry = queue[i];
            if (!isObject(entry)) {
                continue;
            }
            validateLinks({
                concept_ids: Array.isArray(entry.concept_ids) ? entry.concept_ids : [],
                chain_ids: Array.isArray(entry.chain_ids) ? entry.chain_ids : [],
                method_card: isObject(entry.method_card) ? entry.method_card : null
            }, registries, isText(entry.id) ? entry.id : 'queue[' + i + ']');
        }
    }
    /* --------------------------------------------------------------- helpers */
    function loadTermsMap(doc) {
        const out = {};
        if (doc && root.SimTerms && typeof root.SimTerms.load === 'function') {
            try {
                const loaded = root.SimTerms.load(doc);
                if (loaded && Array.isArray(loaded.terms)) {
                    for (let i = 0; i < loaded.terms.length; i += 1) {
                        const t = loaded.terms[i];
                        if (isObject(t) && isText(t.key) && isText(t.text_lv)) {
                            out[t.key] = t.text_lv;
                        }
                    }
                    return out;
                }
            }
            catch (_err) {
                /* fallback */
            }
        }
        const parsed = doc ? parseIslandJson(doc, 'sim-terms') : null;
        if (parsed && Array.isArray(parsed.terms)) {
            for (let i = 0; i < parsed.terms.length; i += 1) {
                const t = parsed.terms[i];
                if (isObject(t) && isText(t.key) && isText(t.text_lv)) {
                    out[t.key] = t.text_lv;
                }
            }
        }
        return out;
    }
    function termText(termsMap, key, fallback) {
        return has(termsMap, key) && isText(termsMap[key]) ? termsMap[key] : fallback;
    }
    function nextQueueSeq(queue) {
        let maxSeq = 0;
        for (let i = 0; i < queue.length; i += 1) {
            const o = Number(queue[i].opened_seq || 0);
            const t = Number(queue[i].retried_seq || 0);
            const r = Number(queue[i].resolved_seq || 0);
            if (o > maxSeq) {
                maxSeq = o;
            }
            if (t > maxSeq) {
                maxSeq = t;
            }
            if (r > maxSeq) {
                maxSeq = r;
            }
        }
        return maxSeq + 1;
    }
    function inferVariantFromId(instanceId) {
        const m = /-([A-D])-(?:[0-9]+|EPH-[0-9]+)$/.exec(instanceId);
        return m ? m[1] : '';
    }
    function isBankInstanceEligible(inst) {
        if (!isObject(inst)) {
            return false;
        }
        const ephMeta = inst.extensions && inst.extensions.data ? inst.extensions.data.ephemeral : undefined;
        const isEph = Boolean((ephMeta && ephMeta.frozen_bank_member === false) || /-EPH-[0-9]+$/.test(String(inst.question_id || '')));
        if (isEph) {
            return false;
        }
        const rev = inst.review;
        if (!isObject(rev) || rev.accessibility !== 'passed' || rev.calculation !== 'passed' ||
            rev.content !== 'passed' || rev.source !== 'passed') {
            return false;
        }
        const wf = inst.extensions && inst.extensions.data ? inst.extensions.data.review_workflow : undefined;
        if (isObject(wf) && wf.state !== 'accepted') {
            return false;
        }
        return true;
    }
    function buildNewEntryId(queue, familyId, outcomeId, seq) {
        const base = familyId + '::' + outcomeId;
        let existsBase = false;
        for (let i = 0; i < queue.length; i += 1) {
            if (queue[i].id === base) {
                existsBase = true;
                break;
            }
        }
        return existsBase ? base + '::' + String(seq) : base;
    }
    function normalizeQueueItem(raw, idx) {
        const slotId = isText(raw.slot_id) ? raw.slot_id : '';
        const slotIds = Array.isArray(raw.slot_ids) ? uniqueSorted(raw.slot_ids) : (slotId ? [slotId] : []);
        const familyId = isText(raw.family_id) ? raw.family_id : '';
        const instanceId = isText(raw.instance_id) ? raw.instance_id : '';
        const conceptIds = Array.isArray(raw.concept_ids) ? uniqueSorted(raw.concept_ids) : [];
        const outcomeIds = Array.isArray(raw.outcome_ids) && raw.outcome_ids.length > 0
            ? uniqueSorted(raw.outcome_ids)
            : conceptIds.slice();
        const outcomeId = isText(raw.outcome_id) && raw.outcome_id !== ''
            ? raw.outcome_id
            : (outcomeIds.length > 0 ? outcomeIds[0] : '');
        const dedupKey = isText(raw.dedup_key) && raw.dedup_key !== ''
            ? raw.dedup_key
            : (familyId && outcomeId ? familyId + '::' + outcomeId : (familyId || slotId));
        const id = isText(raw.id) && raw.id !== '' ? raw.id : (slotId + '::' + (instanceId || String(idx)));
        const state = raw.state === 'resolved'
            ? 'resolved'
            : (raw.state === 'retried' ? 'retried' : 'open');
        const sigId = isText(raw.signature_id) && raw.signature_id !== '' ? raw.signature_id : null;
        const sigIds = Array.isArray(raw.signature_ids) ? uniqueSorted(raw.signature_ids) : (sigId ? [sigId] : []);
        const gradedDigest = isText(raw.graded_digest) ? raw.graded_digest : '';
        const gradedDigests = Array.isArray(raw.graded_digests) ? raw.graded_digests.slice() : (gradedDigest ? [gradedDigest] : []);
        const attemptedIds = Array.isArray(raw.attempted_instance_ids)
            ? raw.attempted_instance_ids.slice()
            : (instanceId ? [instanceId] : []);
        const attemptedVariants = Array.isArray(raw.attempted_variant_ids)
            ? raw.attempted_variant_ids.slice()
            : (inferVariantFromId(instanceId) ? [inferVariantFromId(instanceId)] : []);
        const mc = isObject(raw.method_card) && isText(raw.method_card.card_id) && isText(raw.method_card.step_id)
            ? { card_id: raw.method_card.card_id, step_id: raw.method_card.step_id }
            : null;
        const lastVerdict = raw.last_retry_verdict === 'correct' || raw.last_retry_verdict === 'incorrect' || raw.last_retry_verdict === 'partial'
            ? raw.last_retry_verdict
            : null;
        return {
            id: id,
            dedup_key: dedupKey,
            slot_id: slotId,
            slot_ids: slotIds,
            topic: Number(raw.topic || 0),
            family_id: familyId,
            outcome_id: outcomeId,
            outcome_ids: outcomeIds,
            instance_id: instanceId,
            signature_id: sigId,
            signature_ids: sigIds,
            concept_ids: conceptIds,
            chain_ids: Array.isArray(raw.chain_ids) ? uniqueSorted(raw.chain_ids) : [],
            method_card: mc,
            graded_digest: gradedDigest,
            graded_digests: gradedDigests,
            state: state,
            miss_count: typeof raw.miss_count === 'number' && raw.miss_count >= 1 ? Math.floor(raw.miss_count) : 1,
            retry_count: typeof raw.retry_count === 'number' && raw.retry_count >= 0 ? Math.floor(raw.retry_count) : 0,
            attempted_instance_ids: attemptedIds,
            attempted_variant_ids: attemptedVariants,
            last_retry_instance_id: isText(raw.last_retry_instance_id) && raw.last_retry_instance_id !== '' ? raw.last_retry_instance_id : null,
            last_retry_variant_id: isText(raw.last_retry_variant_id) && raw.last_retry_variant_id !== '' ? raw.last_retry_variant_id : null,
            last_retry_verdict: lastVerdict,
            last_retry_digest: isText(raw.last_retry_digest) && raw.last_retry_digest !== '' ? raw.last_retry_digest : null,
            resolved_reason: isText(raw.resolved_reason) && raw.resolved_reason !== '' ? raw.resolved_reason : null,
            resolved_reason_lv: isText(raw.resolved_reason_lv) && raw.resolved_reason_lv !== '' ? raw.resolved_reason_lv : null,
            opened_seq: typeof raw.opened_seq === 'number' && isFinite(raw.opened_seq) ? raw.opened_seq : idx + 1,
            retried_seq: typeof raw.retried_seq === 'number' && isFinite(raw.retried_seq) ? raw.retried_seq : null,
            resolved_seq: typeof raw.resolved_seq === 'number' && isFinite(raw.resolved_seq) ? raw.resolved_seq : null
        };
    }
    /* --------------------------------------------------- lifecycle transitions */
    function applyMissToDraft(draft, missInput, registries) {
        if (!Array.isArray(draft.remediation_queue)) {
            draft.remediation_queue = [];
        }
        const conceptIds = uniqueSorted(missInput.concept_ids || []);
        const chainIds = uniqueSorted(missInput.chain_ids || []);
        const mc = isObject(missInput.method_card) && isText(missInput.method_card.card_id) && isText(missInput.method_card.step_id)
            ? { card_id: missInput.method_card.card_id, step_id: missInput.method_card.step_id }
            : null;
        validateLinks({ concept_ids: conceptIds, chain_ids: chainIds, method_card: mc }, registries, missInput.family_id + '/' + missInput.slot_id);
        const outcomeIds = uniqueSorted(Array.isArray(missInput.outcome_ids) && missInput.outcome_ids.length > 0
            ? missInput.outcome_ids
            : conceptIds);
        const primaryOutcomeId = isText(missInput.outcome_id) && missInput.outcome_id !== ''
            ? missInput.outcome_id
            : (outcomeIds.length > 0 ? outcomeIds[0] : conceptIds[0]);
        const familyId = isText(missInput.family_id) ? missInput.family_id : '';
        const dedupKey = familyId + '::' + primaryOutcomeId;
        const incomingSigs = [];
        if (isText(missInput.signature_id) && missInput.signature_id !== '') {
            incomingSigs.push(missInput.signature_id);
        }
        if (Array.isArray(missInput.signature_ids)) {
            for (let i = 0; i < missInput.signature_ids.length; i += 1) {
                if (isText(missInput.signature_ids[i]) && missInput.signature_ids[i] !== '') {
                    incomingSigs.push(missInput.signature_ids[i]);
                }
            }
        }
        const sigIds = uniqueSorted(incomingSigs);
        const primarySig = sigIds.length > 0 ? sigIds[0] : null;
        const variantId = isText(missInput.variant_id) && missInput.variant_id !== ''
            ? missInput.variant_id
            : inferVariantFromId(missInput.instance_id);
        const seq = nextQueueSeq(draft.remediation_queue);
        // Coalesce ONLY into an active (open or retried) entry for (family_id, outcome_id).
        // Resolved entries are never resurrected; a new miss opens a new entry.
        let existingIdx = -1;
        for (let i = 0; i < draft.remediation_queue.length; i += 1) {
            const q = draft.remediation_queue[i];
            if (!isObject(q) || q.state === 'resolved') {
                continue;
            }
            const qOutcome = isText(q.outcome_id) && q.outcome_id !== ''
                ? q.outcome_id
                : (Array.isArray(q.outcome_ids) && q.outcome_ids.length ? q.outcome_ids[0] : (Array.isArray(q.concept_ids) && q.concept_ids.length ? q.concept_ids[0] : ''));
            const qKey = isText(q.dedup_key) && q.dedup_key !== '' ? q.dedup_key : (String(q.family_id || '') + '::' + String(qOutcome));
            if (qKey === dedupKey || (q.family_id === familyId && qOutcome === primaryOutcomeId)) {
                existingIdx = i;
                break;
            }
        }
        if (existingIdx >= 0) {
            const cur = normalizeQueueItem(draft.remediation_queue[existingIdx], existingIdx);
            cur.miss_count += 1;
            cur.state = 'open';
            cur.slot_id = missInput.slot_id || cur.slot_id;
            cur.slot_ids = unionSorted(cur.slot_ids, missInput.slot_id ? [missInput.slot_id] : []);
            cur.outcome_ids = unionSorted(cur.outcome_ids, outcomeIds);
            cur.concept_ids = unionSorted(cur.concept_ids, conceptIds);
            cur.chain_ids = unionSorted(cur.chain_ids, chainIds);
            cur.signature_ids = unionSorted(cur.signature_ids, sigIds);
            cur.signature_id = cur.signature_id || primarySig;
            if (cur.method_card === null && mc !== null) {
                cur.method_card = mc;
            }
            if (isText(missInput.instance_id) && missInput.instance_id !== '') {
                cur.instance_id = missInput.instance_id;
                pushUniqueOrdered(cur.attempted_instance_ids, missInput.instance_id);
            }
            if (variantId) {
                pushUniqueOrdered(cur.attempted_variant_ids, variantId);
            }
            if (isText(missInput.graded_digest) && missInput.graded_digest !== '') {
                cur.graded_digest = missInput.graded_digest;
                pushUniqueOrdered(cur.graded_digests, missInput.graded_digest);
            }
            cur.resolved_seq = null;
            cur.resolved_reason = null;
            cur.resolved_reason_lv = null;
            draft.remediation_queue[existingIdx] = cur;
            return { entry: copyJson(cur), action: 'coalesced' };
        }
        const newId = buildNewEntryId(draft.remediation_queue, familyId, primaryOutcomeId, seq);
        const created = {
            id: newId,
            dedup_key: dedupKey,
            slot_id: missInput.slot_id || '',
            slot_ids: missInput.slot_id ? [missInput.slot_id] : [],
            topic: Number(missInput.topic || 0),
            family_id: familyId,
            outcome_id: primaryOutcomeId,
            outcome_ids: outcomeIds,
            instance_id: missInput.instance_id || '',
            signature_id: primarySig,
            signature_ids: sigIds,
            concept_ids: conceptIds,
            chain_ids: chainIds,
            method_card: mc,
            graded_digest: missInput.graded_digest || '',
            graded_digests: missInput.graded_digest ? [missInput.graded_digest] : [],
            state: 'open',
            miss_count: 1,
            retry_count: 0,
            attempted_instance_ids: missInput.instance_id ? [missInput.instance_id] : [],
            attempted_variant_ids: variantId ? [variantId] : [],
            last_retry_instance_id: null,
            last_retry_variant_id: null,
            last_retry_verdict: null,
            last_retry_digest: null,
            resolved_reason: null,
            resolved_reason_lv: null,
            opened_seq: seq,
            retried_seq: null,
            resolved_seq: null
        };
        draft.remediation_queue.push(created);
        return { entry: copyJson(created), action: 'created' };
    }
    function applyGradedRecordDraft(draft, fullRecord, options) {
        if (!isObject(fullRecord) || fullRecord.record_kind !== 'graded-record') {
            return [];
        }
        const opts = options || {};
        const doc = opts.doc || root.document || (activeInitState ? activeInitState.doc : null);
        const registries = opts.registries || (doc
            ? buildRegistries(doc, {
                coverage: opts.coverage || null,
                chains: opts.chains || null,
                methodCards: opts.methodCards || null,
                anchorRegistry: opts.anchorRegistry || null
            })
            : (activeInitState ? activeInitState.registries : buildRegistries(null, {
                coverage: opts.coverage || null,
                chains: opts.chains || null,
                methodCards: opts.methodCards || null,
                anchorRegistry: opts.anchorRegistry || null
            })));
        const slots = Array.isArray(fullRecord.slots) ? fullRecord.slots : [];
        const feedback = isObject(fullRecord.feedback) ? fullRecord.feedback : null;
        const fbItems = feedback && Array.isArray(feedback.items) ? feedback.items : [];
        const bySlotFb = {};
        for (let i = 0; i < fbItems.length; i += 1) {
            const item = fbItems[i];
            if (!isObject(item) || !isText(item.slot_id)) {
                continue;
            }
            if (!has(bySlotFb, item.slot_id)) {
                bySlotFb[item.slot_id] = [];
            }
            bySlotFb[item.slot_id].push(item);
        }
        const touched = [];
        for (let i = 0; i < slots.length; i += 1) {
            const slot = slots[i];
            const needsRemediation = slot.state === 'invalid' || slot.state === 'incomplete' ||
                (slot.state === 'graded' && (slot.verdict_class === 'incorrect' || slot.verdict_class === 'partial'));
            if (!needsRemediation) {
                continue;
            }
            const slotItems = has(bySlotFb, slot.slot_id) ? bySlotFb[slot.slot_id] : [];
            const conceptIds = [];
            const chainIds = [];
            const sigIds = [];
            let methodCard = null;
            for (let s = 0; s < slotItems.length; s += 1) {
                const item = slotItems[s];
                if (isText(item.signature_id) && item.signature_id !== '') {
                    pushUniqueOrdered(sigIds, item.signature_id);
                }
                const rem = isObject(item.remediation) ? item.remediation : null;
                if (!rem) {
                    continue;
                }
                if (Array.isArray(rem.concept_ids)) {
                    for (let c = 0; c < rem.concept_ids.length; c += 1) {
                        if (isText(rem.concept_ids[c]) && rem.concept_ids[c] !== '') {
                            pushUniqueOrdered(conceptIds, rem.concept_ids[c]);
                        }
                    }
                }
                if (Array.isArray(rem.chain_ids)) {
                    for (let c = 0; c < rem.chain_ids.length; c += 1) {
                        if (isText(rem.chain_ids[c]) && rem.chain_ids[c] !== '') {
                            pushUniqueOrdered(chainIds, rem.chain_ids[c]);
                        }
                    }
                }
                if (methodCard === null && isObject(rem.method_card) &&
                    isText(rem.method_card.card_id) && isText(rem.method_card.step_id)) {
                    methodCard = { card_id: rem.method_card.card_id, step_id: rem.method_card.step_id };
                }
            }
            if (conceptIds.length === 0 && chainIds.length === 0 && methodCard === null && sigIds.length === 0) {
                continue;
            }
            const slotOutcomes = Array.isArray(slot.outcome_ids) && slot.outcome_ids.length > 0
                ? uniqueSorted(slot.outcome_ids)
                : uniqueSorted(conceptIds);
            const outcomeId = slotOutcomes.length > 0 ? slotOutcomes[0] : (conceptIds[0] || '');
            const res = applyMissToDraft(draft, {
                slot_id: String(slot.slot_id || ''),
                topic: Number(slot.topic || 0),
                family_id: isText(slot.family_id) ? slot.family_id : '',
                outcome_id: outcomeId,
                outcome_ids: slotOutcomes,
                instance_id: isText(slot.instance_id) ? slot.instance_id : '',
                signature_id: sigIds.length > 0 ? sigIds[0] : null,
                signature_ids: sigIds,
                concept_ids: conceptIds,
                chain_ids: chainIds,
                method_card: methodCard,
                graded_digest: isText(fullRecord.digest) ? fullRecord.digest : ''
            }, registries);
            touched.push(res);
        }
        return touched;
    }
    function addMiss(store, missInput, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const registries = opts.registries || buildRegistries(doc, {
            coverage: opts.coverage || null,
            chains: opts.chains || null
        });
        let outcome = null;
        const nextState = store.update(function (draft) {
            outcome = applyMissToDraft(draft, missInput, registries);
            if (!Array.isArray(draft.events)) {
                draft.events = [];
            }
            draft.events.push({
                event: 'remediation-state',
                entry_id: outcome.entry.id,
                dedup_key: outcome.entry.dedup_key,
                slot_id: outcome.entry.slot_id,
                family_id: outcome.entry.family_id,
                outcome_id: outcome.entry.outcome_id,
                state: outcome.entry.state,
                miss_count: outcome.entry.miss_count,
                concept_ids: outcome.entry.concept_ids.slice(),
                chain_ids: outcome.entry.chain_ids.slice(),
                signature_id: outcome.entry.signature_id,
                graded_digest: outcome.entry.graded_digest
            });
        });
        return {
            entry: outcome.entry,
            action: outcome.action,
            state: nextState
        };
    }
    function resolveEntry(store, entryId, options) {
        const opts = options || {};
        const pol = opts.policy || (function () {
            try {
                return loadPolicy(opts.doc).policy;
            }
            catch (_err) {
                return {
                    resolution_policy: {
                        manual_resolve_copy_lv: 'Izglītojamais manuāli apstiprināja atrisināšanu.'
                    }
                };
            }
        })();
        const rp = isObject(pol.resolution_policy) ? pol.resolution_policy : {};
        const reason = isText(opts.reason) && opts.reason !== '' ? opts.reason : 'learner_confirmed';
        const reasonLv = isText(opts.reason_lv) && opts.reason_lv !== ''
            ? opts.reason_lv
            : (isText(rp.manual_resolve_copy_lv) ? rp.manual_resolve_copy_lv : 'Izglītojamais manuāli apstiprināja atrisināšanu.');
        let resolvedEntry = null;
        const nextState = store.update(function (draft) {
            const queue = Array.isArray(draft.remediation_queue) ? draft.remediation_queue : [];
            let foundIdx = -1;
            for (let i = 0; i < queue.length; i += 1) {
                if (queue[i].id === entryId || ((queue[i].slot_id === entryId || queue[i].dedup_key === entryId) && queue[i].state !== 'resolved')) {
                    foundIdx = i;
                    break;
                }
            }
            if (foundIdx < 0) {
                return fail('E_REMEDIATION_NOT_FOUND', 'Atkārtošanas rindā nav ieraksta "' + entryId + '".', { id: entryId });
            }
            const cur = normalizeQueueItem(queue[foundIdx], foundIdx);
            const seq = nextQueueSeq(queue);
            cur.state = 'resolved';
            cur.resolved_seq = seq;
            cur.resolved_reason = reason;
            cur.resolved_reason_lv = reasonLv;
            queue[foundIdx] = cur;
            resolvedEntry = copyJson(cur);
            if (!Array.isArray(draft.events)) {
                draft.events = [];
            }
            draft.events.push({
                event: 'remediation-state',
                entry_id: cur.id,
                dedup_key: cur.dedup_key,
                slot_id: cur.slot_id,
                family_id: cur.family_id,
                outcome_id: cur.outcome_id,
                state: 'resolved',
                resolved_reason: reason,
                concept_ids: cur.concept_ids.slice(),
                chain_ids: cur.chain_ids.slice(),
                signature_id: cur.signature_id,
                graded_digest: cur.graded_digest
            });
        });
        return {
            resolved: resolvedEntry,
            state: nextState
        };
    }
    function slotVerdictForRetry(slot) {
        if (slot.state !== 'graded') {
            return 'incorrect';
        }
        if (slot.verdict_class === 'correct') {
            return 'correct';
        }
        if (slot.verdict_class === 'auto_passed_pending_review') {
            const task = isObject(slot.task) ? slot.task : {};
            const autoMax = Number(task.auto_max_points || 0);
            const autoPts = Number(task.auto_points || 0);
            if (autoMax > 0 && autoPts === autoMax) {
                return 'correct';
            }
        }
        if (slot.verdict_class === 'partial') {
            return 'partial';
        }
        return 'incorrect';
    }
    function recordRetryVerdict(store, entryId, retryGradedRecord, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const pol = opts.policy || loadPolicy(doc).policy;
        const policyCheck = validatePolicy(pol);
        if (!policyCheck.valid) {
            fail('E_REMEDIATION_POLICY_INVALID', policyCheck.errors.join('; '), { errors: policyCheck.errors });
        }
        const rp = pol.resolution_policy || {};
        const policyMode = isText(rp.mode) ? rp.mode : 'confirm_required';
        const autoResolve = policyMode === 'one_correct_resolves' || rp.auto_resolve_on_correct_retry === true;
        if (!isObject(retryGradedRecord) || retryGradedRecord.record_kind !== 'graded-record') {
            fail('E_REMEDIATION_NOT_FOUND', 'Atkārtojuma vērtējumam jābūt graded-record objektam.', {});
        }
        if (root.SimStore && typeof root.SimStore.digestOf === 'function' && isText(retryGradedRecord.digest) && retryGradedRecord.digest !== '') {
            const expected = root.SimStore.digestOf(retryGradedRecord);
            if (expected !== retryGradedRecord.digest) {
                fail('E_REMEDIATION_POLICY_INVALID', 'Atkārtojuma vērtēšanas ieraksta digest neatbilst saturam.', {
                    expected: expected,
                    actual: retryGradedRecord.digest
                });
            }
        }
        const slots = Array.isArray(retryGradedRecord.slots) ? retryGradedRecord.slots : [];
        let targetSlot = null;
        if (isText(opts.slot_id) && opts.slot_id !== '') {
            for (let i = 0; i < slots.length; i += 1) {
                if (slots[i].slot_id === opts.slot_id) {
                    targetSlot = slots[i];
                    break;
                }
            }
        }
        else if (slots.length > 0) {
            targetSlot = slots[0];
        }
        if (!targetSlot) {
            fail('E_REMEDIATION_NOT_FOUND', 'Atkārtojuma vērtēšanas ierakstā nav uzdevuma slota.', {});
        }
        const verdict = slotVerdictForRetry(targetSlot);
        const retryInstanceId = isText(targetSlot.instance_id) ? targetSlot.instance_id : '';
        const retryVariantId = inferVariantFromId(retryInstanceId);
        const retryDigest = isText(retryGradedRecord.digest) ? retryGradedRecord.digest : sha256Hex(retryGradedRecord);
        let updatedEntry = null;
        let masteryEvents = [];
        let masteryOutcomeState = null;
        let policyCopyLv = '';
        const nextState = store.update(function (draft) {
            const queue = Array.isArray(draft.remediation_queue) ? draft.remediation_queue : [];
            let foundIdx = -1;
            for (let i = 0; i < queue.length; i += 1) {
                if (queue[i].id === entryId || ((queue[i].dedup_key === entryId || queue[i].slot_id === entryId) && queue[i].state !== 'resolved')) {
                    foundIdx = i;
                    break;
                }
            }
            if (foundIdx < 0) {
                return fail('E_REMEDIATION_NOT_FOUND', 'Atkārtošanas rindā nav ieraksta "' + entryId + '".', { id: entryId });
            }
            const cur = normalizeQueueItem(queue[foundIdx], foundIdx);
            const seq = nextQueueSeq(queue);
            cur.retry_count += 1;
            if (retryInstanceId) {
                pushUniqueOrdered(cur.attempted_instance_ids, retryInstanceId);
            }
            if (retryVariantId) {
                pushUniqueOrdered(cur.attempted_variant_ids, retryVariantId);
            }
            cur.last_retry_instance_id = retryInstanceId || cur.last_retry_instance_id;
            cur.last_retry_variant_id = retryVariantId || cur.last_retry_variant_id;
            cur.last_retry_verdict = verdict;
            cur.last_retry_digest = retryDigest;
            cur.retried_seq = seq;
            if (verdict === 'correct') {
                if (autoResolve) {
                    cur.state = 'resolved';
                    cur.resolved_seq = seq;
                    cur.resolved_reason = 'auto_one_correct';
                    const autoCopy = isText(rp.auto_resolve_copy_lv)
                        ? rp.auto_resolve_copy_lv
                        : 'Atrisināts automātiski pēc deklarētās politikas (viena pareiza atbilde atrisina).';
                    cur.resolved_reason_lv = autoCopy;
                    policyCopyLv = autoCopy;
                }
                else {
                    cur.state = 'retried';
                    cur.resolved_seq = null;
                    cur.resolved_reason = null;
                    cur.resolved_reason_lv = null;
                    policyCopyLv = isText(rp.one_correct_evidence_copy_lv)
                        ? rp.one_correct_evidence_copy_lv
                        : ONE_CORRECT_EVIDENCE_COPY_LV;
                }
            }
            else {
                cur.state = 'open';
                cur.miss_count += 1;
                policyCopyLv = 'Atkārtojuma mēģinājums nebija pilnīgi pareizs; ieraksts paliek atvērts nākamajam variantam.';
            }
            queue[foundIdx] = cur;
            updatedEntry = copyJson(cur);
            // Update outcome progress stats in draft (consistent practice path)
            if (!isObject(draft.progress)) {
                draft.progress = {};
            }
            if (!isObject(draft.progress.outcomes)) {
                draft.progress.outcomes = {};
            }
            const oids = Array.isArray(targetSlot.outcome_ids) && targetSlot.outcome_ids.length > 0
                ? targetSlot.outcome_ids
                : cur.outcome_ids;
            for (let j = 0; j < oids.length; j += 1) {
                const oid = String(oids[j]);
                const stat = draft.progress.outcomes[oid] || { attempts: 0, first_attempt_correct: null, correct_count: 0 };
                if (stat.attempts === 0) {
                    stat.first_attempt_correct = verdict === 'correct';
                }
                stat.attempts += 1;
                if (verdict === 'correct') {
                    stat.correct_count += 1;
                }
                draft.progress.outcomes[oid] = stat;
            }
            // Update mastery in the exact same transaction
            if (root.SimMastery && typeof root.SimMastery.applyGradedRecordDraft === 'function') {
                const mRes = root.SimMastery.applyGradedRecordDraft(draft, retryGradedRecord, opts.coverage || null, opts.masteryPolicy || null, opts.masteryPolicyDigest || '', opts.day !== undefined ? opts.day : null);
                if (mRes && mRes.mastery && mRes.mastery.outcomes) {
                    masteryEvents = mRes.events || [];
                    const outNode = mRes.mastery.outcomes[cur.outcome_id];
                    masteryOutcomeState = outNode ? outNode.state : null;
                }
            }
            if (!Array.isArray(draft.events)) {
                draft.events = [];
            }
            draft.events.push({
                event: 'task-answered',
                slot_id: targetSlot.slot_id,
                topic: targetSlot.topic,
                family_id: targetSlot.family_id,
                type_id: targetSlot.type_id,
                source: 'remediation_retry',
                graded_digest: retryDigest
            });
            draft.events.push({
                event: 'remediation-state',
                entry_id: cur.id,
                dedup_key: cur.dedup_key,
                slot_id: cur.slot_id,
                family_id: cur.family_id,
                outcome_id: cur.outcome_id,
                state: cur.state,
                retry_count: cur.retry_count,
                retry_instance_id: retryInstanceId,
                retry_verdict: verdict,
                resolved_reason: cur.resolved_reason,
                concept_ids: cur.concept_ids.slice(),
                chain_ids: cur.chain_ids.slice(),
                signature_id: cur.signature_id,
                graded_digest: retryDigest
            });
        });
        return {
            entry: updatedEntry,
            verdict: verdict,
            policy_mode: policyMode,
            policy_copy_lv: policyCopyLv,
            mastery_events: masteryEvents,
            mastery_state: masteryOutcomeState,
            state: nextState
        };
    }
    /* -------------------------------------------- alternate variant selection */
    function selectRetryInstance(entry, bankQuestions, options) {
        const opts = options || {};
        const norm = normalizeQueueItem(entry, 0);
        const familyId = norm.family_id;
        const cycle = Array.isArray(opts.cycleOrder) && opts.cycleOrder.length > 0
            ? opts.cycleOrder.slice()
            : DEFAULT_CYCLE_ORDER.slice();
        const excludedList = [];
        if (norm.instance_id) {
            pushUniqueOrdered(excludedList, norm.instance_id);
        }
        for (let i = 0; i < norm.attempted_instance_ids.length; i += 1) {
            pushUniqueOrdered(excludedList, norm.attempted_instance_ids[i]);
        }
        if (norm.last_retry_instance_id) {
            pushUniqueOrdered(excludedList, norm.last_retry_instance_id);
        }
        if (Array.isArray(opts.additionalExcludedIds)) {
            for (let i = 0; i < opts.additionalExcludedIds.length; i += 1) {
                pushUniqueOrdered(excludedList, opts.additionalExcludedIds[i]);
            }
        }
        const excludedSet = {};
        for (let i = 0; i < excludedList.length; i += 1) {
            excludedSet[excludedList[i]] = true;
        }
        // Group eligible bank instances of this family by variant_id and collect frozen seeds
        const eligibleByVariant = {};
        const frozenSeeds = {};
        const bankList = Array.isArray(bankQuestions) ? bankQuestions : [];
        for (let i = 0; i < bankList.length; i += 1) {
            const q = bankList[i];
            if (!isObject(q) || q.family_id !== familyId) {
                continue;
            }
            if (q.seed !== undefined && q.seed !== null) {
                frozenSeeds[String(q.seed)] = true;
            }
            if (!isBankInstanceEligible(q)) {
                continue;
            }
            const vid = isText(q.variant_id) ? q.variant_id : inferVariantFromId(String(q.question_id || ''));
            if (vid && !has(eligibleByVariant, vid)) {
                eligibleByVariant[vid] = q;
            }
        }
        const lastVariant = norm.last_retry_variant_id
            || (norm.attempted_variant_ids.length > 0 ? norm.attempted_variant_ids[norm.attempted_variant_ids.length - 1] : '')
            || inferVariantFromId(norm.instance_id);
        const startIdx = lastVariant ? cycle.indexOf(lastVariant) : -1;
        const cyclicOrder = [];
        for (let offset = 1; offset <= cycle.length; offset += 1) {
            const idx = startIdx >= 0 ? (startIdx + offset) % cycle.length : (offset - 1) % cycle.length;
            cyclicOrder.push(cycle[idx]);
        }
        // 1. Prefer an eligible bank variant whose instance_id has NOT been attempted
        for (let i = 0; i < cyclicOrder.length; i += 1) {
            const letter = cyclicOrder[i];
            const candidate = eligibleByVariant[letter];
            if (!candidate) {
                continue;
            }
            const qid = String(candidate.question_id || '');
            if (qid && !has(excludedSet, qid)) {
                return {
                    source: 'bank',
                    family_id: familyId,
                    variant_id: letter,
                    instance_id: qid,
                    instance: candidate,
                    excluded_instance_ids: excludedList,
                    ephemeral_attempt: null
                };
            }
        }
        // 2. All bank letters attempted: fall back to N20 runtime ephemeral variant path
        if (opts.allowEphemeralFallback === false) {
            return fail('E_REMEDIATION_NO_ALTERNATE_VARIANT', 'Visi bankas varianti saimē "' + familyId + '" jau ir izpildīti.', { family_id: familyId, excluded_instance_ids: excludedList });
        }
        const ve = opts.variantEngine || root.SimVariantEngine;
        if (!ve || typeof ve.instantiateEphemeral !== 'function') {
            return fail('E_REMEDIATION_EPHEMERAL_UNAVAILABLE', 'Visi bankas varianti saimē "' + familyId + '" ir mēģināti, bet N20 efemērais dzinējs nav ielādēts.', { family_id: familyId, excluded_instance_ids: excludedList });
        }
        if (typeof ve.isLoaded === 'function' && !ve.isLoaded()) {
            const targetDoc = opts.doc || root.document;
            const templates = root.SimFamilyTemplates;
            if (typeof ve.load === 'function' && templates) {
                const conv = targetDoc ? parseIslandJson(targetDoc, 'sim-conventions') : null;
                ve.load(templates, conv);
            }
        }
        const nextLetter = cyclicOrder.length > 0 ? cyclicOrder[0] : 'A';
        let attempt = typeof opts.ephemeralAttempt === 'number' && opts.ephemeralAttempt >= 0
            ? Math.floor(opts.ephemeralAttempt)
            : Math.max(0, norm.retry_count);
        for (let guard = 0; guard < 128; guard += 1) {
            const inst = ve.instantiateEphemeral(familyId, nextLetter, attempt, frozenSeeds);
            const qid = String(inst.question_id || '');
            if (qid && !has(excludedSet, qid) && qid !== norm.instance_id) {
                return {
                    source: 'ephemeral',
                    family_id: familyId,
                    variant_id: nextLetter,
                    instance_id: qid,
                    instance: inst,
                    excluded_instance_ids: excludedList,
                    ephemeral_attempt: attempt
                };
            }
            attempt += 1;
        }
        return fail('E_REMEDIATION_NO_ALTERNATE_VARIANT', 'Neizdevās izveidot unikālu efemēro atkārtojuma variantu saimei "' + familyId + '".', { family_id: familyId, excluded_instance_ids: excludedList });
    }
    /* --------------------------------------------------- study & retry handoff */
    function buildStudyHandoff(entry, targetKind, registries, options) {
        const opts = options || {};
        validateLinks({ concept_ids: entry.concept_ids, chain_ids: entry.chain_ids, method_card: entry.method_card }, registries, entry.id);
        const cIdx = typeof opts.conceptIndex === 'number' && opts.conceptIndex >= 0 && opts.conceptIndex < entry.concept_ids.length
            ? opts.conceptIndex
            : 0;
        const conceptId = entry.concept_ids[cIdx];
        const anchor = registries.anchors_by_concept[conceptId] || conceptId;
        let chainId = null;
        if (entry.chain_ids.length > 0) {
            const chIdx = typeof opts.chainIndex === 'number' && opts.chainIndex >= 0 && opts.chainIndex < entry.chain_ids.length
                ? opts.chainIndex
                : 0;
            chainId = entry.chain_ids[chIdx];
        }
        if (targetKind === 'chain' && chainId === null) {
            fail('E_REMEDIATION_CHAIN_UNAVAILABLE', 'Šim atkārtošanas ierakstam nav piesaistītas darba piemēra ķēdes.', {
                entry_id: entry.id,
                family_id: entry.family_id
            });
        }
        return {
            schema_version: SCHEMA_VERSION,
            contract: 'N28-study-handoff',
            entry_id: entry.id,
            family_id: entry.family_id,
            outcome_id: entry.outcome_id,
            target_kind: targetKind,
            concept_id: conceptId,
            master_anchor: anchor,
            chain_id: chainId,
            return_context: {
                target_section: '#atskats',
                queue_list_id: 'atskats-remediation-list',
                entry_id: entry.id,
                elementId: opts.returnElementId || null,
                label_lv: 'Atgriezties atkārtošanas rindā'
            }
        };
    }
    function buildRetryHandoff(entry, bankQuestions, options) {
        const sel = selectRetryInstance(entry, bankQuestions, options);
        const ephData = sel.source === 'ephemeral' && sel.instance && sel.instance.extensions && sel.instance.extensions.data
            ? sel.instance.extensions.data.ephemeral
            : null;
        const handoff = {
            schema_version: SCHEMA_VERSION,
            contract: 'N28-to-N30-remediation-retry',
            entry_source: 'remediation_retry',
            remediation_entry_id: entry.id,
            family_id: entry.family_id,
            outcome_id: entry.outcome_id,
            outcome_ids: entry.outcome_ids.slice(),
            topic: entry.topic,
            excluded_instance_ids: sel.excluded_instance_ids.slice(),
            selected_instance_id: sel.instance_id,
            selected_variant_id: sel.variant_id,
            selection_source: sel.source,
            ephemeral_spec: sel.source === 'ephemeral'
                ? {
                    family_id: entry.family_id,
                    variant_id: sel.variant_id,
                    attempt: ephData ? Number(ephData.attempt) : Number(sel.ephemeral_attempt || 0),
                    seed: String(sel.instance.seed || '')
                }
                : null,
            filters: {
                topic: entry.topic,
                outcome_id: entry.outcome_id,
                family_ids: [entry.family_id],
                instance_ids: [sel.instance_id]
            },
            counts_against_practice_bound: true
        };
        return { handoff: handoff, selection: sel };
    }
    /* --------------------------------------------------- queue snapshot (N29) */
    function getQueueSnapshot(storeOrState, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const pol = opts.policy || (function () {
            try {
                return loadPolicy(doc).policy;
            }
            catch (_err) {
                return {
                    policy_id: 'sim-colloq1-remediation-v1',
                    epistemic_label: 'PROPOSED',
                    recommend_only: true
                };
            }
        })();
        const registries = opts.registries || buildRegistries(doc, {
            coverage: opts.coverage || null,
            chains: opts.chains || null
        });
        const rawState = typeof storeOrState.getState === 'function' ? storeOrState.getState() : storeOrState;
        const rawQueue = isObject(rawState) && Array.isArray(rawState.remediation_queue) ? rawState.remediation_queue : [];
        const entries = [];
        for (let i = 0; i < rawQueue.length; i += 1) {
            if (isObject(rawQueue[i])) {
                entries.push(normalizeQueueItem(rawQueue[i], i));
            }
        }
        validateQueueLinks(entries, registries);
        const activeEntries = [];
        const resolvedEntries = [];
        const byOutcome = {};
        let openCount = 0;
        let retriedCount = 0;
        for (let i = 0; i < entries.length; i += 1) {
            const e = entries[i];
            if (e.state === 'resolved') {
                resolvedEntries.push(e);
            }
            else {
                activeEntries.push(e);
                if (e.state === 'retried') {
                    retriedCount += 1;
                }
                else {
                    openCount += 1;
                }
            }
            for (let j = 0; j < e.outcome_ids.length; j += 1) {
                const oid = e.outcome_ids[j];
                if (!has(byOutcome, oid)) {
                    byOutcome[oid] = [];
                }
                byOutcome[oid].push(e);
            }
        }
        const payload = {
            schema_version: SCHEMA_VERSION,
            contract: 'N28-queue-state-snapshot',
            policy_id: isText(pol.policy_id) ? pol.policy_id : 'sim-colloq1-remediation-v1',
            epistemic_label: 'PROPOSED',
            recommend_only: true,
            active_count: activeEntries.length,
            open_count: openCount,
            retried_count: retriedCount,
            resolved_count: resolvedEntries.length,
            active_entries: activeEntries,
            resolved_entries: resolvedEntries,
            by_outcome: byOutcome
        };
        return {
            schema_version: payload.schema_version,
            contract: payload.contract,
            policy_id: payload.policy_id,
            epistemic_label: payload.epistemic_label,
            recommend_only: payload.recommend_only,
            active_count: payload.active_count,
            open_count: payload.open_count,
            retried_count: payload.retried_count,
            resolved_count: payload.resolved_count,
            active_entries: payload.active_entries,
            resolved_entries: payload.resolved_entries,
            by_outcome: payload.by_outcome,
            digest: sha256Hex(payload)
        };
    }
    /* ---------------------------------------------------------------- DOM UI */
    function clearNode(node) {
        if (!node) {
            return;
        }
        while (node.firstChild) {
            node.removeChild(node.firstChild);
        }
    }
    function makeEl(doc, tag, className, text) {
        const el = doc.createElement(tag);
        if (className) {
            el.className = className;
        }
        if (text !== undefined && text !== null) {
            el.textContent = String(text);
        }
        return el;
    }
    function safeDomId(raw) {
        return raw.replace(/[^A-Za-z0-9_-]+/g, '-');
    }
    function renderError(doc, error) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-remediation-error');
        if (box) {
            const code = isObject(error) && isText(error.code) ? error.code : 'E_REMEDIATION';
            const msg = isObject(error) && isText(error.message) ? error.message : String(error);
            box.textContent = 'Atkārtošanas rindas kļūda (' + code + '): ' + msg;
            box.hidden = false;
        }
    }
    function clearError(doc) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-remediation-error');
        if (box) {
            box.textContent = '';
            box.hidden = true;
        }
    }
    function openStudyAnchor(doc, entry, registries, options) {
        const opts = options || {};
        const handoff = buildStudyHandoff(entry, 'anchor', registries, {
            conceptIndex: opts.conceptIndex,
            returnElementId: opts.returnElementId
        });
        const drawer = opts.drawerApi || root.SimConceptDrawer;
        if (!drawer || typeof drawer.openFromLink !== 'function') {
            fail('E_REMEDIATION_DRAWER_UNAVAILABLE', 'Konceptu atvilktne nav ielādēta.', { concept_id: handoff.concept_id });
        }
        const triggerEl = doc && typeof doc.getElementById === 'function' && handoff.return_context.elementId
            ? doc.getElementById(handoff.return_context.elementId)
            : null;
        const drawerState = drawer.openFromLink({
            conceptId: handoff.concept_id,
            source: 'remediation-queue',
            quiet: Boolean(opts.quiet),
            returnContext: {
                elementId: handoff.return_context.elementId,
                triggerEl: triggerEl,
                anchor: handoff.return_context.target_section,
                labelLv: handoff.return_context.label_lv
            }
        }, doc);
        return { handoff: handoff, drawer_state: drawerState };
    }
    function openStudyChain(doc, entry, registries, options) {
        const opts = options || {};
        const handoff = buildStudyHandoff(entry, 'chain', registries, {
            chainIndex: opts.chainIndex,
            returnElementId: opts.returnElementId
        });
        const chainsApi = opts.chainsApi || root.SimChains;
        if (!chainsApi || typeof chainsApi.mountChain !== 'function') {
            fail('E_REMEDIATION_CHAIN_UNAVAILABLE', 'Darba piemēru ķēžu modulis nav ielādēts.', { chain_id: handoff.chain_id });
        }
        const host = doc && typeof doc.getElementById === 'function' ? doc.getElementById('atskats-remediation-chain-host') : null;
        if (!host) {
            fail('E_REMEDIATION_CHAIN_UNAVAILABLE', '#atskats-remediation-chain-host nav atrasts.', { chain_id: handoff.chain_id });
        }
        clearNode(host);
        host.hidden = false;
        host.setAttribute('data-entry-id', entry.id);
        host.setAttribute('data-chain-id', String(handoff.chain_id));
        const bar = makeEl(doc, 'div', 'remediation-study-bar');
        bar.appendChild(makeEl(doc, 'span', 'remediation-study-label', 'Darba piemēra studēšana (' + handoff.chain_id + ' · ' + entry.family_id + ')'));
        const returnBtn = makeEl(doc, 'button', 'btn-control remediation-return-btn', handoff.return_context.label_lv);
        returnBtn.type = 'button';
        returnBtn.id = 'atskats-remediation-chain-return';
        returnBtn.setAttribute('data-return-entry', entry.id);
        returnBtn.setAttribute('data-return-target', handoff.return_context.elementId || 'atskats-remediation-list');
        returnBtn.addEventListener('click', function () {
            returnToQueue(doc, host, handoff.return_context);
            if (typeof opts.onReturn === 'function') {
                opts.onReturn();
            }
        });
        bar.appendChild(returnBtn);
        host.appendChild(bar);
        const mountBox = makeEl(doc, 'div', 'remediation-chain-mount');
        host.appendChild(mountBox);
        const res = chainsApi.mountChain(doc, mountBox, handoff.chain_id, 'rem-' + safeDomId(entry.id));
        const el = res.element;
        return {
            handoff: handoff,
            mount_id: res.mountId,
            initial_state: {
                chain_id: String(handoff.chain_id),
                revealed_count: el && typeof el.getAttribute === 'function' ? el.getAttribute('data-revealed-count') : '0',
                revealed_all: el && typeof el.getAttribute === 'function' ? el.getAttribute('data-revealed-all') : 'false',
                return_affordance_id: returnBtn.id
            }
        };
    }
    function returnToQueue(doc, studyHost, returnContext) {
        const host = studyHost || (doc && doc.getElementById ? doc.getElementById('atskats-remediation-chain-host') : null);
        if (host) {
            host.hidden = true;
            clearNode(host);
        }
        const drawer = root.SimConceptDrawer;
        if (drawer && typeof drawer.getState === 'function' && drawer.getState().isOpen && typeof drawer.closeAll === 'function') {
            drawer.closeAll(doc);
        }
        let targetEl = null;
        const targetId = returnContext && returnContext.elementId ? returnContext.elementId : 'atskats-remediation-list';
        if (doc && typeof doc.getElementById === 'function') {
            targetEl = doc.getElementById(targetId) || doc.getElementById('atskats-remediation-list');
        }
        if (targetEl && typeof targetEl.focus === 'function') {
            targetEl.focus();
            return { returned: true, restored_focus_id: targetEl.id || targetId };
        }
        return { returned: true, restored_focus_id: null };
    }
    function launchRetry(doc, store, entryId, options) {
        const opts = options || {};
        const pathState = opts.practicePath || null;
        const retryHost = doc && typeof doc.getElementById === 'function' ? doc.getElementById('atskats-remediation-retry-host') : null;
        if (pathState && (pathState.exhausted === true || Number(pathState.remaining) <= 0)) {
            const msg = 'Prakses ceļa limits ir sasniegts (0 atlikušo uzdevumu). Atkārtojuma mēģinājums neapiet ceļa ierobežojumu; varat pārskatīt jēdziena avotu vai sākt jaunu prakses ceļu.';
            if (retryHost) {
                clearNode(retryHost);
                retryHost.hidden = false;
                retryHost.setAttribute('data-retry-status', 'PATH_EXHAUSTED');
                retryHost.appendChild(makeEl(doc, 'p', 'remediation-bound-notice', msg));
            }
            return {
                status: 'PATH_EXHAUSTED',
                bound_respected: true,
                bypassed: false,
                remaining_after: 0,
                reason_lv: msg,
                handoff: null,
                starter_result: null
            };
        }
        const st = store.getState();
        const queue = Array.isArray(st.remediation_queue) ? st.remediation_queue : [];
        let found = null;
        for (let i = 0; i < queue.length; i += 1) {
            if (queue[i].id === entryId || ((queue[i].dedup_key === entryId || queue[i].slot_id === entryId) && queue[i].state !== 'resolved')) {
                found = normalizeQueueItem(queue[i], i);
                break;
            }
        }
        if (!found) {
            fail('E_REMEDIATION_NOT_FOUND', 'Atkārtošanas rindā nav ieraksta "' + entryId + '".', { id: entryId });
        }
        let bankQuestions = opts.bankQuestions || null;
        if (!bankQuestions && doc && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const loadedBank = root.SimBank.load(doc);
                bankQuestions = loadedBank ? loadedBank.questions : null;
            }
            catch (_err) {
                bankQuestions = null;
            }
        }
        const built = buildRetryHandoff(found, bankQuestions, {
            variantEngine: opts.variantEngine,
            doc: doc
        });
        if (pathState) {
            pathState.remaining = Math.max(0, Number(pathState.remaining) - 1);
            pathState.used = Number(pathState.used || 0) + 1;
            if (pathState.remaining === 0) {
                pathState.exhausted = true;
            }
        }
        if (retryHost) {
            clearNode(retryHost);
            retryHost.hidden = false;
            retryHost.setAttribute('data-retry-status', 'LAUNCHED');
            retryHost.setAttribute('data-entry-id', found.id);
            retryHost.setAttribute('data-selected-instance-id', built.handoff.selected_instance_id);
            retryHost.setAttribute('data-selection-source', built.handoff.selection_source);
            retryHost.appendChild(makeEl(doc, 'h4', 'remediation-retry-title', 'Atkārtojuma uzdevums sagatavots (' + built.handoff.selected_instance_id + ')'));
            retryHost.appendChild(makeEl(doc, 'p', 'remediation-retry-meta', 'Saime: ' + built.handoff.family_id +
                ' · Variants: ' + built.handoff.selected_variant_id +
                ' (' + (built.handoff.selection_source === 'ephemeral' ? 'N20 efemērais variants' : 'bankas alternatīvais variants') + ')' +
                ' · Izslēgtie iepriekšējie: ' + built.handoff.excluded_instance_ids.join(', ')));
        }
        let starterResult = null;
        if (typeof opts.practiceStarter === 'function') {
            starterResult = opts.practiceStarter(built.handoff);
        }
        else if (root.SimPractice && typeof root.SimPractice.startPath === 'function') {
            starterResult = root.SimPractice.startPath(built.handoff);
        }
        return {
            status: 'LAUNCHED',
            bound_respected: true,
            bypassed: false,
            remaining_after: pathState ? pathState.remaining : null,
            reason_lv: null,
            handoff: built.handoff,
            starter_result: starterResult
        };
    }
    function renderQueue(doc, store, options) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const termsMap = loadTermsMap(doc);
        let pol;
        try {
            pol = opts.policy || loadPolicy(doc).policy;
        }
        catch (_err) {
            pol = {
                policy_id: 'sim-colloq1-remediation-v1',
                epistemic_label: 'PROPOSED',
                recommend_only: true,
                resolution_policy: {
                    mode: 'confirm_required',
                    one_correct_evidence_copy_lv: ONE_CORRECT_EVIDENCE_COPY_LV
                }
            };
        }
        const registries = opts.registries || buildRegistries(doc, {
            coverage: opts.coverage || null,
            chains: opts.chains || null
        });
        let snapshot;
        try {
            snapshot = getQueueSnapshot(store, {
                doc: doc,
                registries: registries,
                policy: pol
            });
            clearError(doc);
        }
        catch (err) {
            renderError(doc, err);
            throw err;
        }
        const headingEl = doc.getElementById('atskats-remediation-heading');
        if (headingEl) {
            headingEl.textContent = termText(termsMap, 'remediation.queue.title', 'Atkārtošanas rinda (PROPOSED — ieteikums)');
        }
        const honestyEl = doc.getElementById('atskats-remediation-honesty');
        if (honestyEl) {
            honestyEl.textContent = termText(termsMap, 'remediation.queue.honesty_note', 'PROPOSED mācību politika: atkārtošana ir tikai ieteikums bez piespiedu ierobežošanas; sākotnējais vērtējums paliek nemainīts.');
        }
        const countEl = doc.getElementById('atskats-remediation-count');
        if (countEl) {
            countEl.textContent = String(snapshot.active_count);
        }
        const statusEl = doc.getElementById('atskats-remediation-status');
        if (statusEl) {
            statusEl.textContent =
                'Aktīvie vienumi: ' + snapshot.active_count +
                    ' (atvērti: ' + snapshot.open_count + ', atkārtoti: ' + snapshot.retried_count + ')' +
                    ' · Atrisināti: ' + snapshot.resolved_count +
                    ' · Režīms: tikai ieteikums (bez piespiedu bloķēšanas)';
        }
        const listEl = doc.getElementById('atskats-remediation-list');
        if (listEl) {
            clearNode(listEl);
            if (snapshot.active_entries.length === 0) {
                listEl.appendChild(makeEl(doc, 'li', 'atskats-empty', termText(termsMap, 'remediation.queue.empty', 'Atkārtošanas rinda ir tukša (0 atvērtu vienumu).')));
            }
            else {
                for (let i = 0; i < snapshot.active_entries.length; i += 1) {
                    const item = snapshot.active_entries[i];
                    const domSlug = safeDomId(item.id);
                    const hasChain = item.chain_ids.length > 0;
                    const li = makeEl(doc, 'li', 'atskats-rem-row remediation-item');
                    li.id = 'rem-item-' + domSlug;
                    li.setAttribute('data-remediation-id', item.id);
                    li.setAttribute('data-dedup-key', item.dedup_key);
                    li.setAttribute('data-slot-id', item.slot_id);
                    li.setAttribute('data-family-id', item.family_id);
                    li.setAttribute('data-outcome-id', item.outcome_id);
                    li.setAttribute('data-state', item.state);
                    li.setAttribute('data-miss-count', String(item.miss_count));
                    li.setAttribute('data-retry-count', String(item.retry_count));
                    li.setAttribute('data-has-chain', hasChain ? 'true' : 'false');
                    const header = makeEl(doc, 'div', 'remediation-item-header');
                    const stateLabel = item.state === 'retried'
                        ? termText(termsMap, 'remediation.state.retried', 'Atkārtots (gaida apstiprinājumu)')
                        : termText(termsMap, 'remediation.state.open', 'Atvērts');
                    const badge = makeEl(doc, 'span', 'badge remediation-badge remediation-badge-' + item.state, stateLabel);
                    header.appendChild(badge);
                    header.appendChild(makeEl(doc, 'strong', 'remediation-item-title', item.family_id + ' · ' + item.outcome_id + ' (' + item.topic + '. tēma)'));
                    header.appendChild(makeEl(doc, 'span', 'remediation-item-counts', 'Kļūdas: ' + item.miss_count + ' · Atkārtojumi: ' + item.retry_count));
                    li.appendChild(header);
                    const metaText = 'Uzdevums: ' + item.instance_id +
                        (item.signature_ids.length ? ' · Kļūdu pazīmes: ' + item.signature_ids.join(', ') : '') +
                        ' · Enkuri: ' + item.concept_ids.join(', ') +
                        (hasChain ? ' · Piemēri: ' + item.chain_ids.join(', ') : ' · Piemēri: nav darba ķēdes');
                    li.appendChild(makeEl(doc, 'p', 'remediation-item-meta', metaText));
                    if (item.state === 'retried') {
                        const rp = isObject(pol.resolution_policy) ? pol.resolution_policy : {};
                        const evidenceCopy = isText(rp.one_correct_evidence_copy_lv)
                            ? rp.one_correct_evidence_copy_lv
                            : termText(termsMap, 'remediation.policy.one_correct_evidence', ONE_CORRECT_EVIDENCE_COPY_LV);
                        li.appendChild(makeEl(doc, 'p', 'remediation-evidence-note', evidenceCopy));
                    }
                    const actions = makeEl(doc, 'div', 'remediation-actions');
                    const anchorBtn = makeEl(doc, 'button', 'btn-control remediation-anchor-btn', termText(termsMap, 'remediation.action.study_anchor', 'Atvērt jēdzienu atvilktni') + ' (' + item.concept_ids[0] + ')');
                    anchorBtn.type = 'button';
                    anchorBtn.id = 'rem-anchor-btn-' + domSlug;
                    anchorBtn.setAttribute('data-concept-id', item.concept_ids[0]);
                    anchorBtn.setAttribute('data-master-anchor', registries.anchors_by_concept[item.concept_ids[0]] || item.concept_ids[0]);
                    (function (entrySnapshot, btnId) {
                        anchorBtn.addEventListener('click', function () {
                            openStudyAnchor(doc, entrySnapshot, registries, { returnElementId: btnId });
                        });
                    })(item, anchorBtn.id);
                    actions.appendChild(anchorBtn);
                    if (hasChain) {
                        const chainBtn = makeEl(doc, 'button', 'btn-control remediation-chain-btn', termText(termsMap, 'remediation.action.study_chain', 'Atvērt darba piemēra ķēdi') + ' (' + item.chain_ids[0] + ')');
                        chainBtn.type = 'button';
                        chainBtn.id = 'rem-chain-btn-' + domSlug;
                        chainBtn.setAttribute('data-chain-id', item.chain_ids[0]);
                        (function (entrySnapshot, btnId) {
                            chainBtn.addEventListener('click', function () {
                                openStudyChain(doc, entrySnapshot, registries, { returnElementId: btnId });
                            });
                        })(item, chainBtn.id);
                        actions.appendChild(chainBtn);
                    }
                    const retryBtn = makeEl(doc, 'button', 'btn-control remediation-retry-btn', termText(termsMap, 'remediation.action.retry', 'Mēģināt citu variantu'));
                    retryBtn.type = 'button';
                    retryBtn.id = 'rem-retry-btn-' + domSlug;
                    retryBtn.setAttribute('data-entry-id', item.id);
                    (function (entryId) {
                        retryBtn.addEventListener('click', function () {
                            launchRetry(doc, store, entryId, {
                                bankQuestions: opts.bankQuestions,
                                practicePath: opts.practicePath,
                                practiceStarter: opts.practiceStarter
                            });
                        });
                    })(item.id);
                    actions.appendChild(retryBtn);
                    const resolveBtn = makeEl(doc, 'button', 'btn-control remediation-resolve-btn', termText(termsMap, 'remediation.action.resolve', 'Atzīmēt kā apgūtu'));
                    resolveBtn.type = 'button';
                    resolveBtn.id = 'rem-resolve-btn-' + domSlug;
                    resolveBtn.setAttribute('data-entry-id', item.id);
                    (function (entryId) {
                        resolveBtn.addEventListener('click', function () {
                            resolveEntry(store, entryId, { policy: pol, doc: doc });
                            renderQueue(doc, store, opts);
                        });
                    })(item.id);
                    actions.appendChild(resolveBtn);
                    li.appendChild(actions);
                    listEl.appendChild(li);
                }
            }
        }
        const resSummaryEl = doc.getElementById('atskats-remediation-resolved-summary');
        if (resSummaryEl) {
            resSummaryEl.textContent = 'Atrisinātie atkārtošanas vienumi (' + snapshot.resolved_count + ')';
        }
        const resListEl = doc.getElementById('atskats-remediation-resolved-list');
        if (resListEl) {
            clearNode(resListEl);
            if (snapshot.resolved_entries.length === 0) {
                resListEl.appendChild(makeEl(doc, 'li', 'atskats-empty', 'Nav atrisinātu atkārtošanas vienumu.'));
            }
            else {
                for (let i = 0; i < snapshot.resolved_entries.length; i += 1) {
                    const item = snapshot.resolved_entries[i];
                    const li = makeEl(doc, 'li', 'atskats-rem-resolved-row');
                    li.setAttribute('data-remediation-id', item.id);
                    li.setAttribute('data-state', 'resolved');
                    li.setAttribute('data-resolved-reason', item.resolved_reason || '');
                    const resolvedLabel = termText(termsMap, 'remediation.state.resolved', 'Atrisināts');
                    const reasonCopy = item.resolved_reason_lv || 'Atrisināts.';
                    li.textContent = '[' + resolvedLabel + '] ' + item.family_id + ' · ' + item.outcome_id +
                        ' (kļūdas: ' + item.miss_count + ', atkārtojumi: ' + item.retry_count + ') — ' + reasonCopy;
                    resListEl.appendChild(li);
                }
            }
        }
        return snapshot;
    }
    let activeInitState = null;
    function renderFromStore(doc, store, coverage) {
        if (!store) {
            return null;
        }
        const registries = activeInitState && activeInitState.doc === doc
            ? activeInitState.registries
            : buildRegistries(doc, { coverage: coverage || null });
        const bankQuestions = activeInitState ? activeInitState.bankQuestions : null;
        const pol = activeInitState ? activeInitState.policy : undefined;
        return renderQueue(doc, store, {
            registries: registries,
            coverage: coverage || null,
            bankQuestions: bankQuestions,
            policy: pol
        });
    }
    function init(doc, options) {
        doc = doc || root.document;
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const loadedPol = opts.policy
            ? { policy: opts.policy, digest: sha256Hex(opts.policy) }
            : loadPolicy(doc);
        const registries = buildRegistries(doc, {
            coverage: opts.coverage || null,
            chains: opts.chains || null
        });
        let bankQuestions = opts.bank && Array.isArray(opts.bank.questions)
            ? opts.bank.questions
            : null;
        if (!bankQuestions && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const b = root.SimBank.load(doc);
                bankQuestions = b && Array.isArray(b.questions) ? b.questions : null;
            }
            catch (_err) {
                bankQuestions = null;
            }
        }
        const store = opts.store || (root.SimStore ? root.SimStore.createStore({ optIn: false, doc: doc }) : null);
        activeInitState = {
            doc: doc,
            store: store,
            registries: registries,
            bankQuestions: bankQuestions,
            policy: loadedPol.policy
        };
        function refresh() {
            if (!store) {
                return null;
            }
            return renderQueue(doc, store, {
                registries: registries,
                coverage: opts.coverage || null,
                bankQuestions: bankQuestions,
                policy: loadedPol.policy,
                practicePath: opts.practicePath,
                practiceStarter: opts.practiceStarter
            });
        }
        if (store) {
            refresh();
        }
        return {
            policy: loadedPol.policy,
            policyDigest: loadedPol.digest,
            registries: registries,
            store: store,
            refresh: refresh,
            getSnapshot: function () {
                return store ? getQueueSnapshot(store, { doc: doc, registries: registries, policy: loadedPol.policy }) : null;
            },
            addMiss: function (missInput) {
                const res = addMiss(store, missInput, { doc: doc, registries: registries });
                refresh();
                return res;
            },
            recordRetryVerdict: function (entryId, retryGradedRecord, rOpts) {
                const res = recordRetryVerdict(store, entryId, retryGradedRecord, {
                    ...(rOpts || {}),
                    policy: (rOpts && rOpts.policy) || loadedPol.policy,
                    coverage: (rOpts && rOpts.coverage) || opts.coverage || null,
                    doc: doc
                });
                refresh();
                return res;
            },
            resolveEntry: function (entryId, rOpts) {
                const res = resolveEntry(store, entryId, { ...(rOpts || {}), policy: loadedPol.policy, doc: doc });
                refresh();
                return res;
            }
        };
    }
    const api = {
        ISLAND_ID: ISLAND_ID,
        SCHEMA_VERSION: SCHEMA_VERSION,
        ONE_CORRECT_EVIDENCE_COPY_LV: ONE_CORRECT_EVIDENCE_COPY_LV,
        errors: ERRORS.slice(),
        RemediationError: RemediationError,
        validatePolicy: validatePolicy,
        loadPolicy: loadPolicy,
        buildRegistries: buildRegistries,
        validateLinks: validateLinks,
        validateQueueLinks: validateQueueLinks,
        applyMissToDraft: applyMissToDraft,
        applyGradedRecordDraft: applyGradedRecordDraft,
        addMiss: addMiss,
        resolveEntry: resolveEntry,
        recordRetryVerdict: recordRetryVerdict,
        selectRetryInstance: selectRetryInstance,
        buildStudyHandoff: buildStudyHandoff,
        buildRetryHandoff: buildRetryHandoff,
        getQueueSnapshot: getQueueSnapshot,
        openStudyAnchor: openStudyAnchor,
        openStudyChain: openStudyChain,
        returnToQueue: returnToQueue,
        launchRetry: launchRetry,
        renderQueue: renderQueue,
        renderFromStore: renderFromStore,
        renderError: renderError,
        init: init
    };
    root.SimRemediation = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
