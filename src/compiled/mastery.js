"use strict";
/* N26 — Mastery state machine over the 64 outcomes.
 *
 * Pure, deterministic state machine and view renderers over #sim-mastery-policy.
 * Epistemic boundary:
 *   - Policy thresholds are PROPOSED training policy (no official RSU mastery
 *     standard exists in the 2025 programme: UNDETERMINED).
 *   - Mastery transitions derive solely from machine-graded criterion verdicts
 *     and explicit decay events; self-assessment (N29), manual-pending criteria,
 *     click counts, and unattempted slots never advance or regress mastery.
 *   - Zero wall-clock calls (Date.now / performance.now) and zero network APIs.
 */
(function (root) {
    'use strict';
    const ISLAND_ID = 'sim-mastery-policy';
    const SCHEMA_VERSION = 1;
    const STATES = ['unseen', 'learning', 'near_mastered', 'mastered', 'needs_review'];
    const STATE_ORDER = {
        unseen: 0,
        learning: 1,
        near_mastered: 2,
        mastered: 3,
        needs_review: 4
    };
    const ERRORS = [
        'E_MASTERY_POLICY_INVALID',
        'E_MASTERY_UNKNOWN_STATE',
        'E_MASTERY_UNKNOWN_OUTCOME',
        'E_MASTERY_UNMAPPED_CRITERION',
        'E_MASTERY_INVALID_EVENT'
    ];
    class MasteryError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'MasteryError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, MasteryError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new MasteryError(code, message, details);
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
    function isPositiveInt(value) {
        return typeof value === 'number' && isFinite(value) && Math.floor(value) === value && value > 0;
    }
    /* --------------------------------------------------- canonical & sha256 */
    function canonicalText(value) {
        if (value === null || value === undefined) {
            return 'null';
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        if (typeof value === 'number') {
            if (!isFinite(value)) {
                return fail('E_MASTERY_INVALID_EVENT', 'Kanoniālajā projektcijā nav atbalstīts bezgalīgs skaitlis.', {});
            }
            return String(value);
        }
        if (typeof value === 'string') {
            return JSON.stringify(value);
        }
        if (Array.isArray(value)) {
            const items = [];
            for (let i = 0; i < value.length; i += 1) {
                items.push(canonicalText(value[i]));
            }
            return '[' + items.join(',') + ']';
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
        return fail('E_MASTERY_INVALID_EVENT', 'Kanoniālajā projektcijā nav atbalstīta vērtība.', {
            value_type: typeof value
        });
    }
    function sortedValue(value) {
        if (Array.isArray(value)) {
            const out = [];
            for (let i = 0; i < value.length; i += 1) {
                out.push(sortedValue(value[i]));
            }
            return out;
        }
        if (isObject(value)) {
            const keys = Object.keys(value).sort();
            const out = {};
            for (let i = 0; i < keys.length; i += 1) {
                if (value[keys[i]] !== undefined) {
                    out[keys[i]] = sortedValue(value[keys[i]]);
                }
            }
            return out;
        }
        return value;
    }
    const SHA_K = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
    ];
    function sha256Fallback(text) {
        const bytes = [];
        const encoded = unescape(encodeURIComponent(text));
        for (let i = 0; i < encoded.length; i += 1) {
            bytes.push(encoded.charCodeAt(i) & 0xff);
        }
        const bitLength = bytes.length * 8;
        bytes.push(0x80);
        while (bytes.length % 64 !== 56) {
            bytes.push(0);
        }
        const high = Math.floor(bitLength / 0x100000000);
        const low = bitLength >>> 0;
        bytes.push((high >>> 24) & 0xff, (high >>> 16) & 0xff, (high >>> 8) & 0xff, high & 0xff);
        bytes.push((low >>> 24) & 0xff, (low >>> 16) & 0xff, (low >>> 8) & 0xff, low & 0xff);
        const h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
        const w = new Array(64);
        for (let block = 0; block < bytes.length; block += 64) {
            for (let t = 0; t < 16; t += 1) {
                w[t] = ((bytes[block + t * 4] << 24) | (bytes[block + t * 4 + 1] << 16) |
                    (bytes[block + t * 4 + 2] << 8) | bytes[block + t * 4 + 3]) >>> 0;
            }
            for (let j = 16; j < 64; j += 1) {
                const g0 = (w[j - 15] >>> 7 | w[j - 15] << 25) ^ (w[j - 15] >>> 18 | w[j - 15] << 14) ^ (w[j - 15] >>> 3);
                const g1 = (w[j - 2] >>> 17 | w[j - 2] << 15) ^ (w[j - 2] >>> 19 | w[j - 2] << 13) ^ (w[j - 2] >>> 10);
                w[j] = (w[j - 16] + g0 + w[j - 7] + g1) >>> 0;
            }
            let a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
            for (let m = 0; m < 64; m += 1) {
                const s1 = (e >>> 6 | e << 26) ^ (e >>> 11 | e << 21) ^ (e >>> 25 | e << 7);
                const ch = (e & f) ^ (~e & g);
                const temp1 = (hh + s1 + ch + SHA_K[m] + w[m]) >>> 0;
                const s0 = (a >>> 2 | a << 30) ^ (a >>> 13 | a << 19) ^ (a >>> 22 | a << 10);
                const maj = (a & b) ^ (a & c) ^ (b & c);
                const temp2 = (s0 + maj) >>> 0;
                hh = g;
                g = f;
                f = e;
                e = (d + temp1) >>> 0;
                d = c;
                c = b;
                b = a;
                a = (temp1 + temp2) >>> 0;
            }
            h[0] = (h[0] + a) >>> 0;
            h[1] = (h[1] + b) >>> 0;
            h[2] = (h[2] + c) >>> 0;
            h[3] = (h[3] + d) >>> 0;
            h[4] = (h[4] + e) >>> 0;
            h[5] = (h[5] + f) >>> 0;
            h[6] = (h[6] + g) >>> 0;
            h[7] = (h[7] + hh) >>> 0;
        }
        let hex = '';
        for (let z = 0; z < 8; z += 1) {
            hex += ('00000000' + h[z].toString(16)).slice(-8);
        }
        return hex;
    }
    function digestValue(value) {
        const storeApi = root.SimStore;
        if (storeApi && typeof storeApi.digestValue === 'function') {
            return storeApi.digestValue(value);
        }
        return sha256Fallback(canonicalText(value));
    }
    /* --------------------------------------------------- policy validation */
    function validatePolicy(rawPolicy) {
        const errors = [];
        if (!isObject(rawPolicy)) {
            return {
                valid: false,
                initial_state: '',
                states: [],
                unreachable_states: [],
                errors: ['Apguves politikai jābūt JSON objektam.']
            };
        }
        if (rawPolicy.island_id !== ISLAND_ID) {
            errors.push('Politikas island_id jābūt "' + ISLAND_ID + '".');
        }
        if (rawPolicy.epistemic_label !== 'PROPOSED') {
            errors.push('Politikas epistemic_label jābūt "PROPOSED".');
        }
        if (rawPolicy.official_counterpart_status !== 'UNDETERMINED') {
            errors.push('Politikas official_counterpart_status jābūt "UNDETERMINED".');
        }
        const th = isObject(rawPolicy.thresholds) ? rawPolicy.thresholds : {};
        const requiredThresholds = [
            'learning_to_near_mastered_streak',
            'near_mastered_to_mastered_streak',
            'needs_review_to_near_mastered_streak',
            'decay_inactivity_days',
            'decay_miss_count'
        ];
        for (let i = 0; i < requiredThresholds.length; i += 1) {
            const k = requiredThresholds[i];
            const item = th[k];
            if (!isObject(item) || !isPositiveInt(item.value)) {
                errors.push('Slieksnim "' + k + '" jābūt pozitīvam veselam skaitlim.');
            }
            else if (item.epistemic_label !== 'PROPOSED') {
                errors.push('Slieksnim "' + k + '" jābūt marķētam ar epistemic_label="PROPOSED".');
            }
        }
        const rawStates = Array.isArray(rawPolicy.states) ? rawPolicy.states : [];
        const stateIds = [];
        const byId = {};
        for (let i = 0; i < rawStates.length; i += 1) {
            const st = rawStates[i];
            if (!isObject(st) || !isText(st.id) || st.id === '') {
                errors.push('Stāvoklim indeksā ' + i + ' trūkst derīga id.');
                continue;
            }
            if (has(byId, st.id)) {
                errors.push('Dublēts stāvokļa id "' + st.id + '".');
                continue;
            }
            byId[st.id] = st;
            stateIds.push(st.id);
        }
        for (let i = 0; i < STATES.length; i += 1) {
            if (!has(byId, STATES[i])) {
                errors.push('Politikā trūkst obligātā stāvokļa "' + STATES[i] + '".');
            }
        }
        const initialState = isText(rawPolicy.initial_state) ? rawPolicy.initial_state : '';
        if (!initialState || !has(byId, initialState)) {
            errors.push('Sākuma stāvoklis "' + initialState + '" nav deklarēts stāvokļu sarakstā.');
        }
        const adj = {};
        for (let i = 0; i < stateIds.length; i += 1) {
            const id = stateIds[i];
            const st = byId[id];
            adj[id] = [];
            if (!isText(st.label_lv) || st.label_lv.trim() === '') {
                errors.push('Stāvoklim "' + id + '" trūkst label_lv.');
            }
            if (!isText(st.icon) || st.icon.trim() === '') {
                errors.push('Stāvoklim "' + id + '" trūkst ikonas (icon).');
            }
            if (!isObject(st.entry_rule) || !isText(st.entry_rule.kind)) {
                errors.push('Stāvoklim "' + id + '" trūkst entry_rule.');
            }
            else if (st.entry_rule.kind === 'transition') {
                const froms = Array.isArray(st.entry_rule.from_states) ? st.entry_rule.from_states : [];
                if (froms.length === 0) {
                    errors.push('Stāvoklim "' + id + '" trūkst ieejas stāvokļu (entry_rule.from_states).');
                }
                for (let f = 0; f < froms.length; f += 1) {
                    if (!has(byId, String(froms[f]))) {
                        errors.push('Stāvokļa "' + id + '" entry_rule atsaucas uz nezināmu stāvokli "' + String(froms[f]) + '".');
                    }
                }
            }
            const exits = Array.isArray(st.exit_paths) ? st.exit_paths : [];
            if (exits.length === 0) {
                errors.push('Stāvoklim "' + id + '" trūkst izejas ceļu (exit_paths).');
            }
            for (let e = 0; e < exits.length; e += 1) {
                const ex = exits[e];
                if (!isObject(ex) || !isText(ex.to_state) || !has(byId, ex.to_state)) {
                    errors.push('Stāvokļa "' + id + '" exit_paths satur nederīgu mērķi "' + (ex && ex.to_state) + '".');
                }
                else {
                    adj[id].push(ex.to_state);
                }
            }
            if (!isObject(st.regression_rule) || !isText(st.regression_rule.to_state) || !has(byId, st.regression_rule.to_state)) {
                errors.push('Stāvoklim "' + id + '" trūkst derīga regression_rule.');
            }
            else {
                adj[id].push(st.regression_rule.to_state);
            }
        }
        const reachable = {};
        const queue = [];
        if (initialState && has(byId, initialState)) {
            reachable[initialState] = true;
            queue.push(initialState);
        }
        while (queue.length > 0) {
            const cur = queue.shift();
            const nexts = adj[cur] || [];
            for (let i = 0; i < nexts.length; i += 1) {
                const nxt = nexts[i];
                if (!has(reachable, nxt)) {
                    reachable[nxt] = true;
                    queue.push(nxt);
                }
            }
        }
        const unreachable = [];
        for (let i = 0; i < stateIds.length; i += 1) {
            if (!has(reachable, stateIds[i])) {
                unreachable.push(stateIds[i]);
            }
        }
        if (unreachable.length > 0) {
            errors.push('Nesasniedzami apguves stāvokļi politikā: ' + unreachable.join(', '));
        }
        return {
            valid: errors.length === 0,
            initial_state: initialState,
            states: stateIds,
            unreachable_states: unreachable,
            errors: errors
        };
    }
    function loadPolicy(docOrObj) {
        let parsed = null;
        if (isObject(docOrObj) && docOrObj.island_id === ISLAND_ID) {
            parsed = docOrObj;
        }
        else {
            if (!docOrObj || typeof docOrObj.getElementById !== 'function') {
                return fail('E_MASTERY_POLICY_INVALID', 'Nav dokumenta apguves politikas salas ielādei.', {});
            }
            const node = docOrObj.getElementById(ISLAND_ID);
            if (!node || !isText(node.textContent) || node.textContent === '') {
                return fail('E_MASTERY_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav atrasta vai ir tukša.', {});
            }
            try {
                parsed = JSON.parse(node.textContent);
            }
            catch (err) {
                return fail('E_MASTERY_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav derīgs JSON.', {
                    reason: String(err)
                });
            }
        }
        const check = validatePolicy(parsed);
        if (!check.valid) {
            return fail('E_MASTERY_POLICY_INVALID', check.errors.join(' '), {
                errors: check.errors,
                unreachable_states: check.unreachable_states
            });
        }
        const clean = sortedValue(copyJson(parsed));
        return { policy: clean, digest: digestValue(clean) };
    }
    /* -------------------------------------------- per-criterion outcome map */
    function coverageOutcomeSet(coverage) {
        const ids = [];
        const idSet = {};
        const byFamily = {};
        const list = coverage && Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        for (let i = 0; i < list.length; i += 1) {
            const oc = list[i];
            if (!isObject(oc) || !isText(oc.id) || oc.id === '') {
                continue;
            }
            if (!has(idSet, oc.id)) {
                idSet[oc.id] = true;
                ids.push(oc.id);
            }
            const fams = oc.bindings && Array.isArray(oc.bindings.practice_families)
                ? oc.bindings.practice_families
                : [];
            for (let j = 0; j < fams.length; j += 1) {
                const fam = fams[j];
                if (!isText(fam) || fam === '') {
                    continue;
                }
                if (!has(byFamily, fam)) {
                    byFamily[fam] = [];
                }
                if (byFamily[fam].indexOf(oc.id) < 0) {
                    byFamily[fam].push(oc.id);
                }
            }
        }
        return { ids: ids, idSet: idSet, byFamily: byFamily };
    }
    function resolveCriterionOutcomes(instanceOrSlot, criterion, coverage) {
        if (!isObject(instanceOrSlot) || !isObject(criterion)) {
            return fail('E_MASTERY_UNMAPPED_CRITERION', 'Kritērija sasaistei nepieciešams uzdevuma un kritērija objekts.', {});
        }
        let rawIds = [];
        if (Array.isArray(criterion.outcome_ids) && criterion.outcome_ids.length > 0) {
            rawIds = criterion.outcome_ids;
        }
        else if (Array.isArray(instanceOrSlot.outcome_ids) && instanceOrSlot.outcome_ids.length > 0) {
            rawIds = instanceOrSlot.outcome_ids;
        }
        else if (coverage && isText(instanceOrSlot.family_id)) {
            const cov = coverageOutcomeSet(coverage);
            if (has(cov.byFamily, instanceOrSlot.family_id)) {
                rawIds = cov.byFamily[instanceOrSlot.family_id];
            }
        }
        const resolved = [];
        const seen = {};
        for (let i = 0; i < rawIds.length; i += 1) {
            const oid = rawIds[i];
            if (isText(oid) && oid.trim() !== '' && !has(seen, oid)) {
                seen[oid] = true;
                resolved.push(oid);
            }
        }
        resolved.sort();
        if (resolved.length === 0) {
            return fail('E_MASTERY_UNMAPPED_CRITERION', 'Kritērijs "' + String(criterion.criterion_id || '') + '" nav sasaistīts ne ar vienu mācību mērķi.', {
                question_id: instanceOrSlot.question_id || instanceOrSlot.instance_id || null,
                slot_id: instanceOrSlot.slot_id || null,
                family_id: instanceOrSlot.family_id || null,
                criterion_id: criterion.criterion_id || null
            });
        }
        if (coverage && Array.isArray(coverage.outcomes) && coverage.outcomes.length > 0) {
            const cov = coverageOutcomeSet(coverage);
            for (let i = 0; i < resolved.length; i += 1) {
                if (!has(cov.idSet, resolved[i])) {
                    return fail('E_MASTERY_UNKNOWN_OUTCOME', 'Kritērijs atsaucas uz nezināmu mācību mērķi "' + resolved[i] + '".', { outcome_id: resolved[i], criterion_id: criterion.criterion_id || null });
                }
            }
        }
        return resolved;
    }
    function verifyBankCriterionMapping(questions, coverage) {
        const fams = {};
        const unmapped = [];
        let totalCriteria = 0;
        for (let i = 0; i < questions.length; i += 1) {
            const q = questions[i];
            if (!isObject(q)) {
                continue;
            }
            if (isText(q.family_id)) {
                fams[q.family_id] = true;
            }
            const rubric = Array.isArray(q.rubric) ? q.rubric : [];
            for (let c = 0; c < rubric.length; c += 1) {
                totalCriteria += 1;
                try {
                    resolveCriterionOutcomes(q, rubric[c], coverage);
                }
                catch (err) {
                    unmapped.push({
                        question_id: q.question_id || null,
                        family_id: q.family_id || null,
                        criterion_id: rubric[c] ? rubric[c].criterion_id : null,
                        error: err.message
                    });
                }
            }
        }
        return {
            total_instances: questions.length,
            total_criteria: totalCriteria,
            families_covered: Object.keys(fams).sort(),
            unmapped: unmapped
        };
    }
    function extractCriterionEvents(gradedRecord, coverage, options) {
        if (!isObject(gradedRecord) || gradedRecord.record_kind !== 'graded-record') {
            return fail('E_MASTERY_INVALID_EVENT', 'Nepieciešams N23 vērtēšanas ieraksts (graded-record).', {});
        }
        const day = options && typeof options.day === 'number' && isFinite(options.day)
            ? Math.floor(options.day)
            : null;
        const digest = isText(gradedRecord.digest) ? gradedRecord.digest : '';
        const slots = Array.isArray(gradedRecord.slots) ? gradedRecord.slots : [];
        const events = [];
        for (let i = 0; i < slots.length; i += 1) {
            const slot = slots[i];
            if (!isObject(slot)) {
                continue;
            }
            if (slot.state === 'unattempted' || slot.state === 'manual_pending') {
                continue;
            }
            const criteria = Array.isArray(slot.criteria) ? slot.criteria : [];
            for (let c = 0; c < criteria.length; c += 1) {
                const cr = criteria[c];
                if (!isObject(cr)) {
                    continue;
                }
                /* Self-assessed and pending criteria never enter mastery state transitions. */
                if (cr.status === 'pending' || cr.grading === 'self' || cr.grading === 'manual') {
                    continue;
                }
                let verdict = null;
                if (cr.status === 'awarded') {
                    verdict = 'correct';
                }
                else if (cr.status === 'denied') {
                    verdict = 'incorrect';
                }
                else {
                    continue;
                }
                const oids = resolveCriterionOutcomes(slot, cr, coverage);
                for (let k = 0; k < oids.length; k += 1) {
                    events.push({
                        kind: 'criterion_verdict',
                        outcome_id: oids[k],
                        verdict: verdict,
                        day: day,
                        slot_id: isText(slot.slot_id) ? slot.slot_id : undefined,
                        criterion_id: isText(cr.criterion_id) ? cr.criterion_id : undefined,
                        graded_digest: digest
                    });
                }
            }
        }
        return events;
    }
    /* ---------------------------------------------------------- pure reducer */
    function makeEmptyEntry(outcomeId) {
        return {
            outcome_id: outcomeId,
            state: 'unseen',
            consecutive_correct: 0,
            miss_in_mastered: 0,
            attempts: 0,
            correct_count: 0,
            incorrect_count: 0,
            last_practiced_day: null,
            last_verdict: null
        };
    }
    function createInitialStateMap(coverage, policy, policyDigest) {
        const cov = coverageOutcomeSet(coverage);
        const outcomes = {};
        const sortedIds = cov.ids.slice().sort();
        for (let i = 0; i < sortedIds.length; i += 1) {
            outcomes[sortedIds[i]] = makeEmptyEntry(sortedIds[i]);
        }
        const pDigest = policyDigest || digestValue(sortedValue(policy));
        return sortedValue({
            schema_version: SCHEMA_VERSION,
            policy_id: isText(policy.policy_id) ? policy.policy_id : 'sim-colloq1-mastery-policy-v1',
            policy_digest: pDigest,
            outcomes: outcomes
        });
    }
    function normalizeStateMap(rawMap, coverage, policy, policyDigest) {
        const base = createInitialStateMap(coverage, policy, policyDigest);
        if (!isObject(rawMap)) {
            return base;
        }
        const rawOutcomes = isObject(rawMap.outcomes) ? rawMap.outcomes : {};
        const keys = Object.keys(rawOutcomes).sort();
        for (let i = 0; i < keys.length; i += 1) {
            const oid = keys[i];
            if (!has(base.outcomes, oid) && coverage && Array.isArray(coverage.outcomes) && coverage.outcomes.length > 0) {
                continue;
            }
            const src = rawOutcomes[oid];
            if (!isObject(src)) {
                continue;
            }
            const st = src.state;
            if (STATES.indexOf(st) < 0) {
                return fail('E_MASTERY_UNKNOWN_STATE', 'Krātuvē atrasts nezināms apguves stāvoklis "' + String(st) + '".', {
                    outcome_id: oid,
                    state: st
                });
            }
            base.outcomes[oid] = {
                outcome_id: oid,
                state: st,
                consecutive_correct: typeof src.consecutive_correct === 'number' && isFinite(src.consecutive_correct)
                    ? Math.max(0, Math.floor(src.consecutive_correct)) : 0,
                miss_in_mastered: typeof src.miss_in_mastered === 'number' && isFinite(src.miss_in_mastered)
                    ? Math.max(0, Math.floor(src.miss_in_mastered)) : 0,
                attempts: typeof src.attempts === 'number' && isFinite(src.attempts)
                    ? Math.max(0, Math.floor(src.attempts)) : 0,
                correct_count: typeof src.correct_count === 'number' && isFinite(src.correct_count)
                    ? Math.max(0, Math.floor(src.correct_count)) : 0,
                incorrect_count: typeof src.incorrect_count === 'number' && isFinite(src.incorrect_count)
                    ? Math.max(0, Math.floor(src.incorrect_count)) : 0,
                last_practiced_day: typeof src.last_practiced_day === 'number' && isFinite(src.last_practiced_day)
                    ? Math.floor(src.last_practiced_day) : null,
                last_verdict: src.last_verdict === 'correct' || src.last_verdict === 'incorrect' || src.last_verdict === 'decay'
                    ? src.last_verdict : null
            };
        }
        return sortedValue(base);
    }
    function reduceEntry(entry, event, policy) {
        const th = policy.thresholds;
        const l2nm = th.learning_to_near_mastered_streak.value;
        const nm2m = th.near_mastered_to_mastered_streak.value;
        const nr2nm = th.needs_review_to_near_mastered_streak.value;
        const decayDays = th.decay_inactivity_days.value;
        const decayMiss = th.decay_miss_count.value;
        const next = {
            outcome_id: entry.outcome_id,
            state: entry.state,
            consecutive_correct: entry.consecutive_correct,
            miss_in_mastered: entry.miss_in_mastered,
            attempts: entry.attempts,
            correct_count: entry.correct_count,
            incorrect_count: entry.incorrect_count,
            last_practiced_day: entry.last_practiced_day,
            last_verdict: entry.last_verdict
        };
        if (event.kind === 'decay') {
            let inactive = typeof event.days_inactive === 'number' && isFinite(event.days_inactive)
                ? Math.floor(event.days_inactive)
                : null;
            if (inactive === null && typeof event.current_day === 'number' && isFinite(event.current_day) &&
                entry.last_practiced_day !== null) {
                inactive = Math.floor(event.current_day) - entry.last_practiced_day;
            }
            if (inactive === null || inactive < 0) {
                return fail('E_MASTERY_INVALID_EVENT', 'Novecošanas notikumam (decay) jānorāda days_inactive.', {
                    outcome_id: entry.outcome_id
                });
            }
            if (entry.state === 'mastered' && inactive >= decayDays) {
                next.state = 'needs_review';
                next.consecutive_correct = 0;
                next.miss_in_mastered = 0;
                next.last_verdict = 'decay';
            }
            return next;
        }
        if (event.kind !== 'criterion_verdict' || (event.verdict !== 'correct' && event.verdict !== 'incorrect')) {
            return fail('E_MASTERY_INVALID_EVENT', 'Nezināms apguves notikums.', {
                kind: event.kind,
                verdict: event.verdict
            });
        }
        const eventDay = typeof event.day === 'number' && isFinite(event.day)
            ? Math.floor(event.day)
            : entry.last_practiced_day;
        next.attempts += 1;
        next.last_practiced_day = eventDay;
        next.last_verdict = event.verdict;
        if (event.verdict === 'correct') {
            next.correct_count += 1;
            if (entry.state === 'unseen') {
                next.state = 'learning';
                next.consecutive_correct = 1;
                next.miss_in_mastered = 0;
            }
            else if (entry.state === 'learning') {
                const streak = entry.consecutive_correct + 1;
                if (streak >= l2nm) {
                    next.state = 'near_mastered';
                    next.consecutive_correct = 0;
                }
                else {
                    next.state = 'learning';
                    next.consecutive_correct = streak;
                }
            }
            else if (entry.state === 'near_mastered') {
                const streak = entry.consecutive_correct + 1;
                if (streak >= nm2m) {
                    next.state = 'mastered';
                    next.consecutive_correct = 0;
                    next.miss_in_mastered = 0;
                }
                else {
                    next.state = 'near_mastered';
                    next.consecutive_correct = streak;
                }
            }
            else if (entry.state === 'mastered') {
                next.state = 'mastered';
                next.consecutive_correct = entry.consecutive_correct + 1;
                next.miss_in_mastered = 0;
            }
            else if (entry.state === 'needs_review') {
                const streak = entry.consecutive_correct + 1;
                if (streak >= nr2nm) {
                    next.state = 'near_mastered';
                    next.consecutive_correct = 0;
                }
                else {
                    next.state = 'needs_review';
                    next.consecutive_correct = streak;
                }
            }
            return next;
        }
        /* event.verdict === 'incorrect' */
        next.incorrect_count += 1;
        next.consecutive_correct = 0;
        if (entry.state === 'unseen') {
            next.state = 'learning';
        }
        else if (entry.state === 'learning') {
            next.state = 'learning';
        }
        else if (entry.state === 'near_mastered') {
            next.state = 'learning';
        }
        else if (entry.state === 'needs_review') {
            next.state = 'learning';
        }
        else if (entry.state === 'mastered') {
            const misses = entry.miss_in_mastered + 1;
            if (misses >= decayMiss) {
                next.state = 'needs_review';
                next.miss_in_mastered = 0;
            }
            else {
                next.state = 'mastered';
                next.miss_in_mastered = misses;
            }
        }
        return next;
    }
    function reduce(stateMap, events, policy) {
        if (!isObject(stateMap) || !isObject(stateMap.outcomes)) {
            return fail('E_MASTERY_INVALID_EVENT', 'Stāvokļu kartei jābūt derīgam MasteryMap objektam.', {});
        }
        if (!Array.isArray(events)) {
            return fail('E_MASTERY_INVALID_EVENT', 'Notikumiem jābūt sarakstam.', {});
        }
        const check = validatePolicy(policy);
        if (!check.valid) {
            return fail('E_MASTERY_POLICY_INVALID', check.errors.join(' '), { errors: check.errors });
        }
        const nextOutcomes = copyJson(stateMap.outcomes);
        for (let i = 0; i < events.length; i += 1) {
            const ev = events[i];
            if (!isObject(ev) || !isText(ev.outcome_id) || ev.outcome_id === '') {
                return fail('E_MASTERY_INVALID_EVENT', 'Notikumam indeksā ' + i + ' trūkst outcome_id.', { index: i });
            }
            if (!has(nextOutcomes, ev.outcome_id)) {
                return fail('E_MASTERY_UNKNOWN_OUTCOME', 'Nezināms mācību mērķis "' + ev.outcome_id + '".', {
                    outcome_id: ev.outcome_id
                });
            }
            nextOutcomes[ev.outcome_id] = reduceEntry(nextOutcomes[ev.outcome_id], ev, policy);
        }
        return sortedValue({
            schema_version: SCHEMA_VERSION,
            policy_id: isText(policy.policy_id) ? policy.policy_id : stateMap.policy_id,
            policy_digest: stateMap.policy_digest || digestValue(sortedValue(policy)),
            outcomes: nextOutcomes
        });
    }
    function digestOfMap(stateMap) {
        return digestValue(sortedValue(stateMap));
    }
    /* --------------------------------------------------- store integration */
    function readFromStore(store, coverage, policy, policyDigest) {
        const st = store && typeof store.getState === 'function' ? store.getState() : null;
        const rawMastery = isObject(st) ? st.mastery : undefined;
        return normalizeStateMap(rawMastery, coverage, policy, policyDigest);
    }
    function writeToStore(store, stateMap) {
        if (!store || typeof store.update !== 'function') {
            return fail('E_MASTERY_INVALID_EVENT', 'Nederīga krātuve (SimStore) apguves saglabāšanai.', {});
        }
        return store.update(function (draft) {
            draft.mastery = sortedValue(copyJson(stateMap));
        });
    }
    function applyGradedRecordDraft(draft, fullRecord, coverage, policy, policyDigest, day) {
        const doc = root.document;
        let resolvedCov = coverage || null;
        if (!resolvedCov && doc && root.SimCoverage && typeof root.SimCoverage.load === 'function') {
            try {
                resolvedCov = root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
            }
            catch (_err) {
                resolvedCov = null;
            }
        }
        let resolvedPolicy = policy || null;
        let resolvedDigest = policyDigest || '';
        if (!resolvedPolicy && doc) {
            try {
                const loaded = loadPolicy(doc);
                resolvedPolicy = loaded.policy;
                resolvedDigest = loaded.digest;
            }
            catch (_err) {
                return null;
            }
        }
        if (!resolvedPolicy || !resolvedCov) {
            return null;
        }
        const current = normalizeStateMap(draft.mastery, resolvedCov, resolvedPolicy, resolvedDigest);
        const events = extractCriterionEvents(fullRecord, resolvedCov, { day: day });
        const next = reduce(current, events, resolvedPolicy);
        draft.mastery = next;
        return { events: events, mastery: next };
    }
    function ingestGradedRecord(store, fullRecord, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        let cov = opts.coverage || null;
        if (!cov && doc && root.SimCoverage && typeof root.SimCoverage.load === 'function') {
            cov = root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
        }
        let pol = opts.policy || null;
        let polDigest = opts.policyDigest || '';
        if (!pol) {
            const loaded = loadPolicy(doc);
            pol = loaded.policy;
            polDigest = loaded.digest;
        }
        const events = extractCriterionEvents(fullRecord, cov, { day: opts.day });
        let nextMastery = createInitialStateMap(cov, pol, polDigest);
        const nextState = store.update(function (draft) {
            const current = normalizeStateMap(draft.mastery, cov, pol, polDigest);
            nextMastery = reduce(current, events, pol);
            draft.mastery = nextMastery;
        });
        return { events: events, mastery: nextMastery, state: nextState };
    }
    /* -------------------------------------------------- availability & views */
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
    function computeAvailability(coverage, bankQuestions, policy) {
        const out = {};
        const covOutcomes = coverage && Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        const availCopy = (policy && isObject(policy.availability_copy_lv)) ? policy.availability_copy_lv : {};
        const pendingReason = isText(availCopy.unavailable_reason_pending_lv)
            ? availCopy.unavailable_reason_pending_lv
            : 'Pagaidām nav pieejams praksei: mērķa uzdevumi gaida recenziju (0 derīgu treniņformai).';
        const emptyReason = isText(availCopy.unavailable_reason_empty_lv)
            ? availCopy.unavailable_reason_empty_lv
            : 'Pagaidām nav pieejams praksei: šim mācību mērķim pašlaik nav treniņformai derīgu uzdevumu.';
        if (!Array.isArray(bankQuestions)) {
            for (let i = 0; i < covOutcomes.length; i += 1) {
                const oc = covOutcomes[i];
                out[oc.id] = {
                    outcome_id: oc.id,
                    available: true,
                    eligible_count: 1,
                    total_count: 1,
                    pending_review_count: 0,
                    reason_lv: null
                };
            }
            return out;
        }
        const cov = coverageOutcomeSet(coverage);
        const eligibleByOutcome = {};
        const totalByOutcome = {};
        const pendingByOutcome = {};
        for (let i = 0; i < bankQuestions.length; i += 1) {
            const q = bankQuestions[i];
            if (!isObject(q)) {
                continue;
            }
            let oids = [];
            if (Array.isArray(q.outcome_ids) && q.outcome_ids.length > 0) {
                oids = q.outcome_ids.filter(isText);
            }
            else if (isText(q.family_id) && has(cov.byFamily, q.family_id)) {
                oids = cov.byFamily[q.family_id];
            }
            const eligible = isBankInstanceEligible(q);
            for (let j = 0; j < oids.length; j += 1) {
                const oid = oids[j];
                totalByOutcome[oid] = (totalByOutcome[oid] || 0) + 1;
                if (eligible) {
                    eligibleByOutcome[oid] = (eligibleByOutcome[oid] || 0) + 1;
                }
                else {
                    pendingByOutcome[oid] = (pendingByOutcome[oid] || 0) + 1;
                }
            }
        }
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oid = covOutcomes[i].id;
            const elig = eligibleByOutcome[oid] || 0;
            const tot = totalByOutcome[oid] || 0;
            const pend = pendingByOutcome[oid] || 0;
            const available = elig > 0;
            out[oid] = {
                outcome_id: oid,
                available: available,
                eligible_count: elig,
                total_count: tot,
                pending_review_count: pend,
                reason_lv: available ? null : (pend > 0 ? pendingReason : emptyReason)
            };
        }
        return out;
    }
    function stateMetaMap(policy) {
        const out = {};
        const list = Array.isArray(policy.states) ? policy.states : [];
        for (let i = 0; i < list.length; i += 1) {
            const st = list[i];
            if (isObject(st) && isText(st.id)) {
                out[st.id] = st;
            }
        }
        return out;
    }
    function buildCounts(rows) {
        const counts = {
            unseen: 0,
            learning: 0,
            near_mastered: 0,
            mastered: 0,
            needs_review: 0,
            unavailable: 0
        };
        for (let i = 0; i < rows.length; i += 1) {
            const key = rows[i].effective_state;
            counts[key] = (counts[key] || 0) + 1;
        }
        return counts;
    }
    function buildViewRows(coverage, masteryMap, policy, availability) {
        const covTopics = Array.isArray(coverage.topics) ? coverage.topics : [];
        const covOutcomes = Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        const meta = stateMetaMap(policy);
        const availCopy = isObject(policy.availability_copy_lv) ? policy.availability_copy_lv : {};
        const unavailLabel = isText(availCopy.unavailable_label_lv) ? availCopy.unavailable_label_lv : 'Pagaidām nav pieejams';
        const unavailIcon = isText(availCopy.unavailable_icon) ? availCopy.unavailable_icon : '⊘';
        const byTopic = { '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [] };
        const allRows = [];
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oc = covOutcomes[i];
            const entry = masteryMap && masteryMap.outcomes && masteryMap.outcomes[oc.id]
                ? masteryMap.outcomes[oc.id]
                : makeEmptyEntry(oc.id);
            const avail = availability && availability[oc.id]
                ? availability[oc.id]
                : { outcome_id: oc.id, available: true, eligible_count: 1, total_count: 1, pending_review_count: 0, reason_lv: null };
            const stMeta = meta[entry.state] || {};
            const effectiveState = avail.available ? entry.state : 'unavailable';
            const row = {
                outcome_id: oc.id,
                topic: Number(oc.topic),
                statement_lv: oc.statement_lv || '',
                master_anchor: oc.master_anchor || '',
                state: entry.state,
                effective_state: effectiveState,
                available: avail.available,
                eligible_count: avail.eligible_count,
                reason_lv: avail.reason_lv,
                icon: avail.available ? (stMeta.icon || '○') : unavailIcon,
                label_lv: avail.available ? (stMeta.label_lv || entry.state) : unavailLabel,
                short_label_lv: avail.available ? (stMeta.short_label_lv || stMeta.label_lv || entry.state) : unavailLabel,
                attempts: entry.attempts,
                consecutive_correct: entry.consecutive_correct,
                last_practiced_day: entry.last_practiced_day
            };
            allRows.push(row);
            const tk = String(oc.topic);
            if (has(byTopic, tk)) {
                byTopic[tk].push(row);
            }
        }
        const topicName = {};
        for (let i = 0; i < covTopics.length; i += 1) {
            topicName[String(covTopics[i].topic)] = covTopics[i].name_lv || (String(covTopics[i].topic) + '. tēma');
        }
        const topics = [];
        for (let t = 1; t <= 7; t += 1) {
            const tk = String(t);
            const rows = byTopic[tk] || [];
            topics.push({
                topic: t,
                name_lv: topicName[tk] || (tk + '. tēma'),
                outcomes_total: rows.length,
                counts: buildCounts(rows),
                outcomes: rows
            });
        }
        const totalCounts = buildCounts(allRows);
        const isFresh = totalCounts.unseen + totalCounts.unavailable === allRows.length &&
            allRows.every(function (r) { return r.attempts === 0; });
        return {
            schema_version: 1,
            policy_id: policy.policy_id,
            epistemic_label: 'PROPOSED',
            official_counterpart_status: 'UNDETERMINED',
            total_outcomes: allRows.length,
            is_fresh: isFresh,
            counts: totalCounts,
            topics: topics,
            outcomes: allRows
        };
    }
    function buildAtskatsViewModel(coverage, masteryMap, policy, availability) {
        const base = buildViewRows(coverage, masteryMap, policy, availability);
        const copy = isObject(policy.copy_lv) ? policy.copy_lv : {};
        return sortedValue({
            view: 'atskats',
            title_lv: copy.atskats_section_title || 'Mācību mērķu apguves stāvoklis (PROPOSED)',
            honesty_note_lv: copy.atskats_honesty_note || policy.honesty_note_lv || '',
            fresh_note_lv: base.is_fresh ? (copy.fresh_learner_note_lv || '') : null,
            epistemic_label: base.epistemic_label,
            official_counterpart_status: base.official_counterpart_status,
            total_outcomes: base.total_outcomes,
            is_fresh: base.is_fresh,
            counts: base.counts,
            topics: base.topics
        });
    }
    function buildPrakseViewModel(coverage, masteryMap, policy, availability) {
        const base = buildViewRows(coverage, masteryMap, policy, availability);
        const copy = isObject(policy.copy_lv) ? policy.copy_lv : {};
        return sortedValue({
            view: 'prakse',
            title_lv: copy.prakse_section_title || 'Tēmu apguves indikatori praksei (PROPOSED)',
            honesty_note_lv: copy.prakse_honesty_note || policy.honesty_note_lv || '',
            epistemic_label: base.epistemic_label,
            official_counterpart_status: base.official_counterpart_status,
            total_outcomes: base.total_outcomes,
            is_fresh: base.is_fresh,
            counts: base.counts,
            topics: base.topics
        });
    }
    /* ------------------------------------------------------------- DOM views */
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
    function renderStatePills(doc, container, counts, policy) {
        clearNode(container);
        const meta = stateMetaMap(policy);
        const availCopy = isObject(policy.availability_copy_lv) ? policy.availability_copy_lv : {};
        for (let i = 0; i < STATES.length; i += 1) {
            const sid = STATES[i];
            const st = meta[sid] || {};
            const pill = makeEl(doc, 'span', 'mastery-pill mastery-state-' + sid);
            pill.setAttribute('data-mastery-state', sid);
            const iconSpan = makeEl(doc, 'span', 'mastery-icon', st.icon || '○');
            iconSpan.setAttribute('aria-hidden', 'true');
            pill.appendChild(iconSpan);
            pill.appendChild(makeEl(doc, 'span', 'mastery-pill-text', ' ' + (st.label_lv || sid) + ': ' + (counts[sid] || 0)));
            container.appendChild(pill);
        }
        if ((counts.unavailable || 0) > 0) {
            const pill = makeEl(doc, 'span', 'mastery-pill mastery-state-unavailable');
            pill.setAttribute('data-mastery-state', 'unavailable');
            const iconSpan = makeEl(doc, 'span', 'mastery-icon', availCopy.unavailable_icon || '⊘');
            iconSpan.setAttribute('aria-hidden', 'true');
            pill.appendChild(iconSpan);
            pill.appendChild(makeEl(doc, 'span', 'mastery-pill-text', ' ' + (availCopy.unavailable_label_lv || 'Pagaidām nav pieejams') + ': ' + counts.unavailable));
            container.appendChild(pill);
        }
    }
    function renderOutcomeRow(doc, row) {
        const li = makeEl(doc, 'li', 'mastery-outcome-row mastery-state-' + row.effective_state);
        li.setAttribute('data-outcome-id', row.outcome_id);
        li.setAttribute('data-mastery-state', row.effective_state);
        li.setAttribute('data-available', row.available ? 'true' : 'false');
        const badge = makeEl(doc, 'span', 'mastery-badge mastery-state-' + row.effective_state);
        const iconSpan = makeEl(doc, 'span', 'mastery-icon', row.icon);
        iconSpan.setAttribute('aria-hidden', 'true');
        badge.appendChild(iconSpan);
        badge.appendChild(makeEl(doc, 'span', 'mastery-state-label', ' ' + row.label_lv));
        li.appendChild(badge);
        const textSpan = makeEl(doc, 'span', 'mastery-outcome-text', ' ' + row.outcome_id + ' — ' + row.statement_lv);
        li.appendChild(textSpan);
        if (!row.available && row.reason_lv) {
            li.appendChild(makeEl(doc, 'span', 'mastery-unavailable-reason', ' (' + row.reason_lv + ')'));
        }
        return li;
    }
    function renderAtskats(doc, coverage, masteryMap, policy, availability) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const vm = buildAtskatsViewModel(coverage, masteryMap, policy, availability);
        const honestyEl = doc.getElementById('atskats-mastery-honesty');
        if (honestyEl) {
            honestyEl.textContent = vm.honesty_note_lv;
        }
        const freshEl = doc.getElementById('atskats-mastery-fresh-note');
        if (freshEl) {
            if (vm.fresh_note_lv) {
                freshEl.textContent = vm.fresh_note_lv;
                freshEl.hidden = false;
            }
            else {
                freshEl.textContent = '';
                freshEl.hidden = true;
            }
        }
        const summaryEl = doc.getElementById('atskats-mastery-summary');
        if (summaryEl) {
            renderStatePills(doc, summaryEl, vm.counts, policy);
        }
        const topicsEl = doc.getElementById('atskats-mastery-topics');
        if (topicsEl) {
            clearNode(topicsEl);
            for (let i = 0; i < vm.topics.length; i += 1) {
                const tp = vm.topics[i];
                const block = makeEl(doc, 'details', 'mastery-topic-details');
                block.setAttribute('data-topic', String(tp.topic));
                const summary = makeEl(doc, 'summary', 'mastery-topic-summary', tp.topic + '. ' + tp.name_lv + ' — Apgūti (pašmācībā): ' +
                    (tp.counts.mastered || 0) + '/' + tp.outcomes_total +
                    ' | Nav mēģināti: ' + (tp.counts.unseen || 0));
                block.appendChild(summary);
                const ul = makeEl(doc, 'ul', 'mastery-outcome-list');
                for (let j = 0; j < tp.outcomes.length; j += 1) {
                    ul.appendChild(renderOutcomeRow(doc, tp.outcomes[j]));
                }
                block.appendChild(ul);
                topicsEl.appendChild(block);
            }
        }
        return vm;
    }
    function renderPrakse(doc, coverage, masteryMap, policy, availability) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const vm = buildPrakseViewModel(coverage, masteryMap, policy, availability);
        const honestyEl = doc.getElementById('prakse-mastery-honesty');
        if (honestyEl) {
            honestyEl.textContent = vm.honesty_note_lv;
        }
        const gridEl = doc.getElementById('prakse-mastery-topics');
        if (gridEl) {
            clearNode(gridEl);
            for (let i = 0; i < vm.topics.length; i += 1) {
                const tp = vm.topics[i];
                const card = makeEl(doc, 'article', 'panel mastery-topic-card');
                card.setAttribute('id', 'prakse-mastery-topic-' + tp.topic);
                card.setAttribute('data-topic', String(tp.topic));
                const heading = makeEl(doc, 'h3', 'mastery-card-title', tp.topic + '. ' + tp.name_lv);
                card.appendChild(heading);
                const pills = makeEl(doc, 'div', 'mastery-card-pills');
                renderStatePills(doc, pills, tp.counts, policy);
                card.appendChild(pills);
                const ul = makeEl(doc, 'ul', 'mastery-outcome-list');
                for (let j = 0; j < tp.outcomes.length; j += 1) {
                    ul.appendChild(renderOutcomeRow(doc, tp.outcomes[j]));
                }
                card.appendChild(ul);
                gridEl.appendChild(card);
            }
        }
        return vm;
    }
    function renderFromStore(doc, store, coverage, options) {
        if (!doc || typeof doc.getElementById !== 'function' || !coverage) {
            return null;
        }
        const opts = options || {};
        let policy = opts.policy || null;
        let policyDigest = opts.policyDigest || '';
        if (!policy) {
            try {
                const loaded = loadPolicy(doc);
                policy = loaded.policy;
                policyDigest = loaded.digest;
            }
            catch (_err) {
                return null;
            }
        }
        let bankQuestions = opts.bankQuestions || null;
        if (!bankQuestions && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const bank = root.SimBank.load(doc);
                bankQuestions = Array.isArray(bank.questions) ? bank.questions : null;
            }
            catch (_err) {
                bankQuestions = null;
            }
        }
        const availability = opts.availability || computeAvailability(coverage, bankQuestions, policy);
        const map = readFromStore(store, coverage, policy, policyDigest);
        const atskats = renderAtskats(doc, coverage, map, policy, availability);
        const prakse = renderPrakse(doc, coverage, map, policy, availability);
        if (root.SimScheduler && typeof root.SimScheduler.renderFromStore === 'function') {
            root.SimScheduler.renderFromStore(doc, store, coverage, {
                masteryMap: map,
                bankQuestions: bankQuestions,
                availability: availability
            });
        }
        if (root.SimRevision && typeof root.SimRevision.renderFromStore === 'function') {
            root.SimRevision.renderFromStore(doc, store, coverage, {
                masteryMap: map,
                bankQuestions: bankQuestions,
                availability: availability
            });
        }
        return { mastery: map, atskats: atskats, prakse: prakse };
    }
    function renderError(doc, error) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-mastery-error');
        if (!box) {
            return;
        }
        const code = isObject(error) && isText(error.code) ? error.code : 'E_MASTERY_POLICY_INVALID';
        const msg = error && error.message ? String(error.message) : String(error);
        box.textContent = '[' + code + '] ' + msg;
        box.hidden = false;
    }
    function init(doc, options) {
        doc = doc || root.document;
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const loaded = opts.policy
            ? { policy: sortedValue(copyJson(opts.policy)), digest: digestValue(opts.policy) }
            : loadPolicy(doc);
        let coverage = opts.coverage || null;
        if (!coverage && root.SimCoverage && typeof root.SimCoverage.load === 'function') {
            coverage = root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
        }
        if (!coverage) {
            return fail('E_MASTERY_POLICY_INVALID', 'Nav seguma salas (#sim-coverage) apguves skatu inicializēšanai.', {});
        }
        let bankQuestions = null;
        if (opts.bank && Array.isArray(opts.bank.questions)) {
            bankQuestions = opts.bank.questions;
        }
        else if (root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const b = root.SimBank.load(doc);
                bankQuestions = Array.isArray(b.questions) ? b.questions : null;
            }
            catch (_err) {
                bankQuestions = null;
            }
        }
        const availability = opts.availability || computeAvailability(coverage, bankQuestions, loaded.policy);
        const storeApi = root.SimStore;
        const store = opts.store || (storeApi && typeof storeApi.createStore === 'function'
            ? storeApi.createStore({ optIn: false, doc: doc })
            : null);
        function refresh() {
            const map = readFromStore(store, coverage, loaded.policy, loaded.digest);
            const atskats = renderAtskats(doc, coverage, map, loaded.policy, availability);
            const prakse = renderPrakse(doc, coverage, map, loaded.policy, availability);
            if (root.SimScheduler && typeof root.SimScheduler.renderFromStore === 'function') {
                root.SimScheduler.renderFromStore(doc, store, coverage, {
                    masteryMap: map,
                    bankQuestions: bankQuestions,
                    availability: availability
                });
            }
            if (root.SimRevision && typeof root.SimRevision.renderFromStore === 'function') {
                root.SimRevision.renderFromStore(doc, store, coverage, {
                    masteryMap: map,
                    bankQuestions: bankQuestions,
                    availability: availability
                });
            }
            return { mastery: map, atskats: atskats, prakse: prakse };
        }
        refresh();
        return {
            policy: loaded.policy,
            policyDigest: loaded.digest,
            coverage: coverage,
            availability: availability,
            store: store,
            refresh: refresh,
            readFromStore: function () {
                return readFromStore(store, coverage, loaded.policy, loaded.digest);
            },
            ingestGradedRecord: function (fullRecord, day) {
                const res = ingestGradedRecord(store, fullRecord, {
                    coverage: coverage,
                    policy: loaded.policy,
                    policyDigest: loaded.digest,
                    day: day,
                    doc: doc
                });
                refresh();
                return res;
            }
        };
    }
    const api = {
        ISLAND_ID: ISLAND_ID,
        SCHEMA_VERSION: SCHEMA_VERSION,
        STATES: STATES.slice(),
        STATE_ORDER: copyJson(STATE_ORDER),
        errors: ERRORS.slice(),
        MasteryError: MasteryError,
        canonicalText: canonicalText,
        digestValue: digestValue,
        validatePolicy: validatePolicy,
        loadPolicy: loadPolicy,
        resolveCriterionOutcomes: resolveCriterionOutcomes,
        verifyBankCriterionMapping: verifyBankCriterionMapping,
        extractCriterionEvents: extractCriterionEvents,
        createInitialStateMap: createInitialStateMap,
        normalizeStateMap: normalizeStateMap,
        reduce: reduce,
        digestOfMap: digestOfMap,
        readFromStore: readFromStore,
        writeToStore: writeToStore,
        applyGradedRecordDraft: applyGradedRecordDraft,
        ingestGradedRecord: ingestGradedRecord,
        computeAvailability: computeAvailability,
        buildAtskatsViewModel: buildAtskatsViewModel,
        buildPrakseViewModel: buildPrakseViewModel,
        renderAtskats: renderAtskats,
        renderPrakse: renderPrakse,
        renderFromStore: renderFromStore,
        renderError: renderError,
        init: init
    };
    root.SimMastery = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
