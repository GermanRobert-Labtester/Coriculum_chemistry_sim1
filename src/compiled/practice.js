"use strict";
/* N30 — Bounded practice paths with filters, honest shortage handling,
 * skip semantics, N22 input rendering, N21 mode-boundary help surfaces, and
 * N23/N26/N27/N28/N29 grading-to-mastery loop integration.
 *
 * Epistemic & architectural invariants:
 *   - Policy lengths, ordering rules, filter semantics, and shortage copy are
 *     PROPOSED training policy (official counterpart: UNDETERMINED) loaded
 *     from #sim-practice-policy (data/practice_policy.json).
 *   - Review eligibility is absolute and shared with N24: unreviewed or
 *     pending-review instances are NEVER drawn into practice paths.
 *   - One pure engine (`computePracticePath`) serves topic browse, scheduler
 *     queue handoffs (`N27-to-N30-practice-entry`), revision panel handoffs,
 *     and remediation retries (`N28-to-N30-remediation-retry`).
 *   - Skipped items record as `skipped`, never `incorrect`, and never feed
 *     mastery regression or remediation.
 *   - Practice answers grade through N23 (`SimGrading.gradePracticeRecord` +
 *     `SimFeedback.assemble`) and feed `SimMastery`, `SimRemediation`, and
 *     `SimStore` identically to exam sessions.
 *   - Zero network calls, zero `Date.now`/`performance.now`, zero F10 exports.
 */
(function (root) {
    'use strict';
    const ISLAND_ID = 'sim-practice-policy';
    const SCHEMA_VERSION = 1;
    const ERRORS = [
        'E_PRACTICE_POLICY_INVALID',
        'E_PRACTICE_UNKNOWN_TOPIC',
        'E_PRACTICE_UNKNOWN_TYPE',
        'E_PRACTICE_MODE_FORBIDDEN',
        'E_PRACTICE_NO_ACTIVE_PATH',
        'E_PRACTICE_ALREADY_FINISHED',
        'E_PRACTICE_GRADING_FAILED'
    ];
    class PracticeError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'PracticeError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, PracticeError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new PracticeError(code, message, details);
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
    function uniqueSorted(items) {
        const seen = {};
        const out = [];
        for (let i = 0; i < items.length; i += 1) {
            const val = items[i];
            if (!isText(val) || val === '' || has(seen, val)) {
                continue;
            }
            seen[val] = true;
            out.push(val);
        }
        out.sort();
        return out;
    }
    function canonicalText(value) {
        if (value === null || value === undefined) {
            return 'null';
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        if (typeof value === 'number') {
            if (!isFinite(value)) {
                return fail('E_PRACTICE_POLICY_INVALID', 'Kanoniālajā projektcijā nav atbalstīts bezgalīgs skaitlis.', {});
            }
            return String(value);
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
    /* --------------------------------------------------- island & term helpers */
    function readIsland(doc, id) {
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
    function loadTermsMap(docOrTerms) {
        const map = {};
        if (isObject(docOrTerms) && Array.isArray(docOrTerms.terms)) {
            const list = docOrTerms.terms;
            for (let i = 0; i < list.length; i += 1) {
                if (isObject(list[i]) && isText(list[i].key) && isText(list[i].text_lv)) {
                    map[list[i].key] = list[i].text_lv;
                }
            }
            return map;
        }
        const termsMod = root.SimTerms;
        if (termsMod && typeof termsMod.getDefault === 'function') {
            const def = termsMod.getDefault();
            if (def && isObject(def.byKey)) {
                const keys = Object.keys(def.byKey);
                for (let i = 0; i < keys.length; i += 1) {
                    const entry = def.byKey[keys[i]];
                    if (entry && isText(entry.text_lv)) {
                        map[keys[i]] = entry.text_lv;
                    }
                }
            }
        }
        if (docOrTerms && typeof docOrTerms.getElementById === 'function') {
            const island = readIsland(docOrTerms, 'sim-terms');
            if (island && Array.isArray(island.terms)) {
                for (let i = 0; i < island.terms.length; i += 1) {
                    const t = island.terms[i];
                    if (isObject(t) && isText(t.key) && isText(t.text_lv) && !has(map, t.key)) {
                        map[t.key] = t.text_lv;
                    }
                }
            }
        }
        return map;
    }
    function fillTemplate(template, params) {
        if (!params) {
            return template;
        }
        let out = template;
        const keys = Object.keys(params);
        for (let i = 0; i < keys.length; i += 1) {
            const k = keys[i];
            out = out.split('{' + k + '}').join(String(params[k]));
        }
        return out;
    }
    function termText(termsMap, key, fallback, params) {
        const raw = has(termsMap, key) && termsMap[key] !== '' ? termsMap[key] : fallback;
        return fillTemplate(raw, params);
    }
    /* ------------------------------------------------ shared eligibility gate */
    function isReviewEligible(inst, allowEphemeral) {
        if (!isObject(inst)) {
            return false;
        }
        const ephMeta = inst.extensions && isObject(inst.extensions.data) ? inst.extensions.data.ephemeral : undefined;
        const isEph = Boolean((isObject(ephMeta) && ephMeta.frozen_bank_member === false) ||
            /-EPH-[0-9]+$/.test(String(inst.question_id || '')));
        if (isEph && !allowEphemeral) {
            return false;
        }
        const rev = inst.review;
        if (!isObject(rev) || rev.accessibility !== 'passed' || rev.calculation !== 'passed' ||
            rev.content !== 'passed' || rev.source !== 'passed') {
            return false;
        }
        const wf = inst.extensions && isObject(inst.extensions.data) ? inst.extensions.data.review_workflow : undefined;
        if (isObject(wf) && wf.state !== 'accepted') {
            return false;
        }
        return true;
    }
    function instanceTypes(inst) {
        const out = [];
        if (isText(inst.type_id) && inst.type_id !== '') {
            out.push(inst.type_id);
        }
        if (Array.isArray(inst.type_ids)) {
            for (let i = 0; i < inst.type_ids.length; i += 1) {
                const t = inst.type_ids[i];
                if (isText(t) && t !== '' && out.indexOf(t) === -1) {
                    out.push(t);
                }
            }
        }
        return out;
    }
    function instanceOutcomes(inst, byFamilyOutcomes) {
        if (Array.isArray(inst.outcome_ids) && inst.outcome_ids.length > 0) {
            return uniqueSorted(inst.outcome_ids);
        }
        if (isText(inst.family_id) && has(byFamilyOutcomes, inst.family_id)) {
            return byFamilyOutcomes[inst.family_id].slice();
        }
        return [];
    }
    function buildCoverageFamilyMap(coverage) {
        const map = {};
        const outcomes = coverage && Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        for (let i = 0; i < outcomes.length; i += 1) {
            const oc = outcomes[i];
            if (!isObject(oc) || !isText(oc.id)) {
                continue;
            }
            const fams = oc.bindings && Array.isArray(oc.bindings.practice_families) ? oc.bindings.practice_families : [];
            for (let f = 0; f < fams.length; f += 1) {
                const fid = fams[f];
                if (!isText(fid) || fid === '') {
                    continue;
                }
                if (!has(map, fid)) {
                    map[fid] = [];
                }
                if (map[fid].indexOf(oc.id) === -1) {
                    map[fid].push(oc.id);
                }
            }
        }
        const keys = Object.keys(map);
        for (let i = 0; i < keys.length; i += 1) {
            map[keys[i]].sort();
        }
        return map;
    }
    /* ---------------------------------------------------- policy validation */
    function validatePolicy(rawPolicy, options) {
        const opts = options || {};
        const errors = [];
        const topicLengths = {};
        if (!isObject(rawPolicy)) {
            return {
                valid: false,
                policy_id: '',
                topic_lengths: topicLengths,
                errors: ['Prakses politikai jābūt JSON objektam.']
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
        if (!isText(rawPolicy.honesty_note_lv) || rawPolicy.honesty_note_lv.trim() === '') {
            errors.push('Politikai trūkst honesty_note_lv.');
        }
        const tl = isObject(rawPolicy.topic_lengths) ? rawPolicy.topic_lengths : null;
        if (!tl) {
            errors.push('Politikai trūkst topic_lengths.');
        }
        else {
            for (let t = 1; t <= 7; t += 1) {
                const tk = String(t);
                const entry = tl[tk];
                if (!isObject(entry) || !isPositiveInt(entry.declared_length)) {
                    errors.push('Tēmas ' + tk + ' declared_length jābūt pozitīvam veselam skaitlim.');
                }
                else {
                    if (entry.epistemic_label !== 'PROPOSED') {
                        errors.push('Tēmai ' + tk + ' jābūt epistemic_label="PROPOSED".');
                    }
                    topicLengths[tk] = entry.declared_length;
                }
            }
            if (has(topicLengths, '7') && has(topicLengths, '3') && topicLengths['7'] >= topicLengths['3']) {
                errors.push('Tēmas 7 (5 rezultāti) ceļa garumam (' + topicLengths['7'] + ') jābūt īsākam nekā 3. tēmai (' + topicLengths['3'] + ').');
            }
        }
        const ord = isObject(rawPolicy.ordering_rule) ? rawPolicy.ordering_rule : null;
        if (!ord || !Array.isArray(ord.difficulty_order) || ord.difficulty_order.length === 0) {
            errors.push('Politikai trūkst ordering_rule.difficulty_order.');
        }
        const fs = isObject(rawPolicy.filter_semantics) ? rawPolicy.filter_semantics : null;
        const filterTypes = fs && Array.isArray(fs.response_type_vocabulary) ? fs.response_type_vocabulary : [];
        if (filterTypes.length === 0) {
            errors.push('Politikai trūkst filter_semantics.response_type_vocabulary.');
        }
        if (opts.responseTypes && isObject(opts.responseTypes.types)) {
            const regTypes = opts.responseTypes.types;
            for (let i = 0; i < filterTypes.length; i += 1) {
                const rt = filterTypes[i];
                if (!isText(rt) || !has(regTypes, rt)) {
                    errors.push('Filtra atbilžu tips "' + String(rt) + '" nav 18 tipu reģistrā.');
                }
            }
        }
        const bounds = isObject(rawPolicy.bounds_rules) ? rawPolicy.bounds_rules : null;
        if (!bounds || bounds.no_repeat_within_path !== true ||
            bounds.exclude_current_session_answered !== true ||
            bounds.never_pad_with_unreviewed !== true) {
            errors.push('bounds_rules jāaizliedz atkārtojumi, sesijas dublikāti un nerecenzētu uzdevumu pievienošana.');
        }
        const skip = isObject(rawPolicy.skip_semantics) ? rawPolicy.skip_semantics : null;
        if (!skip || skip.advances_without_grading !== true ||
            skip.recorded_as !== 'skipped' || skip.counts_as_incorrect !== false) {
            errors.push('skip_semantics jāieraksta izlaišana kā "skipped" bez vērtēšanas kā nepareizu.');
        }
        if (Array.isArray(opts.bankQuestions)) {
            const bankList = opts.bankQuestions;
            const eligibleByTopic = { '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0 };
            for (let i = 0; i < bankList.length; i += 1) {
                const q = bankList[i];
                if (!isReviewEligible(q, false)) {
                    continue;
                }
                const tk = String(q.topic || '');
                if (has(eligibleByTopic, tk)) {
                    eligibleByTopic[tk] += 1;
                }
            }
            for (let t = 1; t <= 7; t += 1) {
                const tk = String(t);
                if (has(topicLengths, tk) && topicLengths[tk] > eligibleByTopic[tk]) {
                    errors.push('Tēmas ' + tk + ' (topic ' + tk + ') deklarētais ceļa garums (' + topicLengths[tk] +
                        ') pārsniedz derīgo uzdevumu skaitu (' + eligibleByTopic[tk] + ').');
                }
            }
        }
        return {
            valid: errors.length === 0,
            policy_id: isText(rawPolicy.policy_id) ? rawPolicy.policy_id : '',
            topic_lengths: topicLengths,
            errors: errors
        };
    }
    function loadPolicy(doc, options) {
        const targetDoc = doc || root.document;
        const raw = readIsland(targetDoc, ISLAND_ID);
        if (!raw) {
            return fail('E_PRACTICE_POLICY_INVALID', 'Prakses politikas sala #' + ISLAND_ID + ' nav atrasta.', {
                island_id: ISLAND_ID
            });
        }
        const rt = (options && options.responseTypes) || readIsland(targetDoc, 'sim-response-types');
        const check = validatePolicy(raw, {
            bankQuestions: options ? options.bankQuestions : null,
            responseTypes: rt
        });
        if (!check.valid) {
            return fail('E_PRACTICE_POLICY_INVALID', check.errors.join(' '), { errors: check.errors });
        }
        const sorted = sortedValue(raw);
        return { policy: sorted, digest: digestValue(sorted) };
    }
    /* --------------------------------------------------- store attempt history */
    function readAttemptHistory(storeOrState) {
        let state = null;
        if (isObject(storeOrState) && typeof storeOrState.getState === 'function') {
            state = storeOrState.getState();
        }
        else if (isObject(storeOrState)) {
            state = storeOrState;
        }
        if (!state) {
            return { attempted_instance_ids: [], skipped_instance_ids: [], history_empty: true };
        }
        const attempted = [];
        const seen = {};
        function pushAttempt(id) {
            if (isText(id) && id !== '' && !has(seen, id)) {
                seen[id] = true;
                attempted.push(id);
            }
        }
        const ph = isObject(state.practice_history) ? state.practice_history : null;
        if (ph && Array.isArray(ph.attempted_instance_ids)) {
            for (let i = 0; i < ph.attempted_instance_ids.length; i += 1) {
                pushAttempt(ph.attempted_instance_ids[i]);
            }
        }
        const remQueue = Array.isArray(state.remediation_queue) ? state.remediation_queue : [];
        for (let i = 0; i < remQueue.length; i += 1) {
            const item = remQueue[i];
            if (!isObject(item)) {
                continue;
            }
            pushAttempt(item.instance_id);
            pushAttempt(item.last_retry_instance_id);
            if (Array.isArray(item.attempted_instance_ids)) {
                for (let j = 0; j < item.attempted_instance_ids.length; j += 1) {
                    pushAttempt(item.attempted_instance_ids[j]);
                }
            }
        }
        const events = Array.isArray(state.events) ? state.events : [];
        for (let i = 0; i < events.length; i += 1) {
            const ev = events[i];
            if (!isObject(ev)) {
                continue;
            }
            pushAttempt(ev.instance_id);
            pushAttempt(ev.retry_instance_id);
        }
        attempted.sort();
        const skipped = ph && Array.isArray(ph.skipped_instance_ids)
            ? uniqueSorted(ph.skipped_instance_ids)
            : [];
        return {
            attempted_instance_ids: attempted,
            skipped_instance_ids: skipped,
            history_empty: attempted.length === 0
        };
    }
    /* --------------------------------------------------- entry normalization */
    function normalizeEntryRequest(entryOrHandoff) {
        if (!isObject(entryOrHandoff)) {
            return fail('E_PRACTICE_UNKNOWN_TOPIC', 'Prakses ceļa pieprasījumam jābūt objektam.', {});
        }
        if (entryOrHandoff.contract === 'N28-to-N30-remediation-retry' || entryOrHandoff.entry_source === 'remediation_retry') {
            const f = isObject(entryOrHandoff.filters) ? entryOrHandoff.filters : {};
            const topic = typeof entryOrHandoff.topic === 'number' ? entryOrHandoff.topic : (typeof f.topic === 'number' ? f.topic : null);
            const familyIds = Array.isArray(f.family_ids)
                ? uniqueSorted(f.family_ids)
                : (isText(entryOrHandoff.family_id) ? [entryOrHandoff.family_id] : null);
            let instanceIds = Array.isArray(f.instance_ids) && f.instance_ids.length > 0
                ? uniqueSorted(f.instance_ids)
                : (isText(entryOrHandoff.selected_instance_id) ? [entryOrHandoff.selected_instance_id] : null);
            const excluded = Array.isArray(entryOrHandoff.excluded_instance_ids)
                ? uniqueSorted(entryOrHandoff.excluded_instance_ids)
                : [];
            const responseTypes = Array.isArray(f.response_types) && f.response_types.length > 0
                ? uniqueSorted(f.response_types)
                : null;
            return {
                entry_source: 'remediation_retry',
                topic: topic,
                outcome_id: isText(entryOrHandoff.outcome_id) ? entryOrHandoff.outcome_id : (isText(f.outcome_id) ? f.outcome_id : null),
                remediation_entry_id: isText(entryOrHandoff.remediation_entry_id) ? entryOrHandoff.remediation_entry_id : null,
                filters: {
                    topic: topic,
                    outcome_id: isText(entryOrHandoff.outcome_id) ? entryOrHandoff.outcome_id : (isText(f.outcome_id) ? f.outcome_id : null),
                    family_ids: familyIds,
                    instance_ids: instanceIds,
                    response_types: responseTypes,
                    unattempted_only: Boolean(f.unattempted_only)
                },
                excluded_instance_ids: excluded,
                allow_ephemeral: entryOrHandoff.selection_source === 'ephemeral' || entryOrHandoff.allow_ephemeral === true,
                ephemeral_spec: isObject(entryOrHandoff.ephemeral_spec) ? copyJson(entryOrHandoff.ephemeral_spec) : null,
                target_length: isPositiveInt(entryOrHandoff.target_length) ? entryOrHandoff.target_length : 1
            };
        }
        if (entryOrHandoff.contract === 'N27-to-N30-practice-entry' ||
            entryOrHandoff.entry_source === 'scheduler_queue' ||
            entryOrHandoff.entry_source === 'revision_panel') {
            const f = isObject(entryOrHandoff.filters) ? entryOrHandoff.filters : {};
            const topic = typeof entryOrHandoff.topic === 'number' ? entryOrHandoff.topic : (typeof f.topic === 'number' ? f.topic : null);
            const outcomeId = isText(entryOrHandoff.outcome_id) ? entryOrHandoff.outcome_id : (isText(f.outcome_id) ? f.outcome_id : null);
            const src = entryOrHandoff.entry_source === 'revision_panel' ? 'revision_panel' : 'scheduler_queue';
            return {
                entry_source: src,
                topic: topic,
                outcome_id: outcomeId,
                remediation_entry_id: null,
                filters: {
                    topic: topic,
                    outcome_id: outcomeId,
                    family_ids: Array.isArray(f.family_ids) && f.family_ids.length > 0 ? uniqueSorted(f.family_ids) : null,
                    instance_ids: Array.isArray(f.instance_ids) && f.instance_ids.length > 0 ? uniqueSorted(f.instance_ids) : null,
                    response_types: Array.isArray(f.response_types) && f.response_types.length > 0 ? uniqueSorted(f.response_types) : null,
                    unattempted_only: Boolean(f.unattempted_only)
                },
                excluded_instance_ids: Array.isArray(entryOrHandoff.excluded_instance_ids)
                    ? uniqueSorted(entryOrHandoff.excluded_instance_ids)
                    : [],
                allow_ephemeral: false,
                ephemeral_spec: null,
                target_length: isPositiveInt(entryOrHandoff.target_length) ? entryOrHandoff.target_length : null
            };
        }
        const rawFilters = isObject(entryOrHandoff.filters) ? entryOrHandoff.filters : {};
        const topic = typeof entryOrHandoff.topic === 'number'
            ? entryOrHandoff.topic
            : (typeof rawFilters.topic === 'number' ? rawFilters.topic : null);
        if (topic === null || topic < 1 || topic > 7 || Math.floor(topic) !== topic) {
            return fail('E_PRACTICE_UNKNOWN_TOPIC', 'Prakses tēmai jābūt skaitlim no 1 līdz 7.', { topic: topic });
        }
        const rtypes = Array.isArray(rawFilters.response_types) && rawFilters.response_types.length > 0
            ? uniqueSorted(rawFilters.response_types)
            : (isText(rawFilters.response_type) && rawFilters.response_type !== '' ? [rawFilters.response_type] : null);
        return {
            entry_source: 'topic_browse',
            topic: topic,
            outcome_id: isText(rawFilters.outcome_id) && rawFilters.outcome_id !== '' ? rawFilters.outcome_id : null,
            remediation_entry_id: null,
            filters: {
                topic: topic,
                outcome_id: isText(rawFilters.outcome_id) && rawFilters.outcome_id !== '' ? rawFilters.outcome_id : null,
                family_ids: Array.isArray(rawFilters.family_ids) && rawFilters.family_ids.length > 0 ? uniqueSorted(rawFilters.family_ids) : null,
                instance_ids: Array.isArray(rawFilters.instance_ids) && rawFilters.instance_ids.length > 0 ? uniqueSorted(rawFilters.instance_ids) : null,
                response_types: rtypes,
                unattempted_only: Boolean(rawFilters.unattempted_only)
            },
            excluded_instance_ids: Array.isArray(entryOrHandoff.excluded_instance_ids)
                ? uniqueSorted(entryOrHandoff.excluded_instance_ids)
                : [],
            allow_ephemeral: false,
            ephemeral_spec: null,
            target_length: isPositiveInt(entryOrHandoff.target_length) ? entryOrHandoff.target_length : null
        };
    }
    /* --------------------------------------------------- pure path engine */
    function computePracticePath(input) {
        const req = normalizeEntryRequest(input.entryOrRequest);
        const polCheck = validatePolicy(input.policy, { responseTypes: input.responseTypes || null });
        if (!polCheck.valid) {
            return fail('E_PRACTICE_POLICY_INVALID', polCheck.errors.join(' '), { errors: polCheck.errors });
        }
        const policy = input.policy;
        const termsMap = loadTermsMap(input.terms || input.doc);
        const vocabList = Array.isArray(policy.filter_semantics && policy.filter_semantics.response_type_vocabulary)
            ? policy.filter_semantics.response_type_vocabulary
            : [];
        const regTypes = input.responseTypes && isObject(input.responseTypes.types)
            ? input.responseTypes.types
            : null;
        const reqTypes = req.filters.response_types;
        if (Array.isArray(reqTypes)) {
            for (let i = 0; i < reqTypes.length; i += 1) {
                const rt = reqTypes[i];
                const validInReg = regTypes ? has(regTypes, rt) : vocabList.indexOf(rt) >= 0;
                if (!validInReg) {
                    return fail('E_PRACTICE_UNKNOWN_TYPE', 'Nezināms filtra atbilžu tips "' + rt + '".', { type_id: rt });
                }
            }
        }
        const topicKey = req.topic !== null ? String(req.topic) : null;
        let targetLength = req.target_length;
        if (targetLength === null) {
            if (topicKey && isObject(policy.topic_lengths) && isObject(policy.topic_lengths[topicKey])) {
                targetLength = Number(policy.topic_lengths[topicKey].declared_length);
            }
            else {
                targetLength = 6;
            }
        }
        const byFamilyOutcomes = buildCoverageFamilyMap(input.coverage);
        const combinedBank = Array.isArray(input.bankQuestions)
            ? input.bankQuestions.slice()
            : [];
        if (Array.isArray(input.extraInstances)) {
            for (let i = 0; i < input.extraInstances.length; i += 1) {
                if (isObject(input.extraInstances[i])) {
                    combinedBank.push(input.extraInstances[i]);
                }
            }
        }
        const scopedAll = [];
        const seenScopedIds = {};
        for (let i = 0; i < combinedBank.length; i += 1) {
            const q = combinedBank[i];
            if (!isObject(q) || !isText(q.question_id) || q.question_id === '') {
                continue;
            }
            if (has(seenScopedIds, q.question_id)) {
                continue;
            }
            if (req.filters.topic !== null && Number(q.topic) !== req.filters.topic) {
                continue;
            }
            if (Array.isArray(req.filters.family_ids) && req.filters.family_ids.indexOf(String(q.family_id || '')) === -1) {
                continue;
            }
            if (Array.isArray(req.filters.instance_ids) && req.filters.instance_ids.indexOf(q.question_id) === -1) {
                continue;
            }
            if (req.filters.outcome_id !== null) {
                const oids = instanceOutcomes(q, byFamilyOutcomes);
                if (oids.indexOf(req.filters.outcome_id) === -1) {
                    continue;
                }
            }
            seenScopedIds[q.question_id] = true;
            scopedAll.push(q);
        }
        let pendingReviewCount = 0;
        const eligibleScoped = [];
        for (let i = 0; i < scopedAll.length; i += 1) {
            const q = scopedAll[i];
            if (!isReviewEligible(q, req.allow_ephemeral)) {
                pendingReviewCount += 1;
                continue;
            }
            eligibleScoped.push(q);
        }
        const typeFiltered = [];
        for (let i = 0; i < eligibleScoped.length; i += 1) {
            const q = eligibleScoped[i];
            if (Array.isArray(reqTypes) && reqTypes.length > 0) {
                const types = instanceTypes(q);
                let matched = false;
                for (let t = 0; t < types.length; t += 1) {
                    if (reqTypes.indexOf(types[t]) >= 0) {
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    continue;
                }
            }
            typeFiltered.push(q);
        }
        const histObj = input.history || {};
        const attemptedIds = Array.isArray(histObj.attempted_instance_ids) ? uniqueSorted(histObj.attempted_instance_ids) : [];
        const sessionAnsweredIds = Array.isArray(histObj.session_answered_ids) ? uniqueSorted(histObj.session_answered_ids) : [];
        const reqExcludedIds = uniqueSorted(req.excluded_instance_ids.concat(Array.isArray(histObj.excluded_instance_ids) ? histObj.excluded_instance_ids : []));
        const excludedLookup = {};
        for (let i = 0; i < sessionAnsweredIds.length; i += 1) {
            excludedLookup[sessionAnsweredIds[i]] = true;
        }
        for (let i = 0; i < reqExcludedIds.length; i += 1) {
            excludedLookup[reqExcludedIds[i]] = true;
        }
        if (req.filters.unattempted_only) {
            for (let i = 0; i < attemptedIds.length; i += 1) {
                excludedLookup[attemptedIds[i]] = true;
            }
        }
        const candidates = [];
        let excludedCount = 0;
        for (let i = 0; i < typeFiltered.length; i += 1) {
            const q = typeFiltered[i];
            if (has(excludedLookup, q.question_id)) {
                excludedCount += 1;
                continue;
            }
            candidates.push(q);
        }
        const diffOrder = Array.isArray(policy.ordering_rule && policy.ordering_rule.difficulty_order)
            ? policy.ordering_rule.difficulty_order
            : ['foundational', 'application', 'transfer'];
        const famMeta = input.familyMetadata || {};
        function difficultyOf(q) {
            if (isText(q.difficulty) && q.difficulty !== '') {
                return q.difficulty;
            }
            const fm = isText(q.family_id) && has(famMeta, q.family_id)
                ? famMeta[q.family_id]
                : null;
            if (fm && isText(fm.difficulty) && fm.difficulty !== '') {
                return fm.difficulty;
            }
            return null;
        }
        let anyDifficultyDeclared = false;
        for (let i = 0; i < candidates.length; i += 1) {
            if (difficultyOf(candidates[i]) !== null) {
                anyDifficultyDeclared = true;
                break;
            }
        }
        const ordered = candidates.slice().sort(function (a, b) {
            if (anyDifficultyDeclared) {
                const da = difficultyOf(a);
                const db = difficultyOf(b);
                const ra = da !== null && diffOrder.indexOf(da) >= 0 ? diffOrder.indexOf(da) : diffOrder.length;
                const rb = db !== null && diffOrder.indexOf(db) >= 0 ? diffOrder.indexOf(db) : diffOrder.length;
                if (ra !== rb) {
                    return ra - rb;
                }
            }
            const fa = String(a.family_id || '');
            const fb = String(b.family_id || '');
            if (fa !== fb) {
                return fa < fb ? -1 : 1;
            }
            const va = String(a.variant_id || '');
            const vb = String(b.variant_id || '');
            if (va !== vb) {
                return va < vb ? -1 : 1;
            }
            const qa = String(a.question_id || '');
            const qb = String(b.question_id || '');
            return qa < qb ? -1 : (qa > qb ? 1 : 0);
        });
        const chosen = ordered.slice(0, targetLength);
        const trueLength = chosen.length;
        const isShortage = trueLength < targetLength;
        let shortageReason = null;
        let shortageCopyLv = null;
        let exitOptions = null;
        if (isShortage) {
            if (trueLength === 0 && (excludedCount > 0 || (req.filters.unattempted_only && typeFiltered.length > 0))) {
                shortageReason = 'history_exhausted';
                shortageCopyLv = termText(termsMap, 'practice.shortage.exhausted', 'Visi šīs tēmas vai filtra derīgie uzdevumi jau ir mēģināti (pieejami 0 no {target_length}). Atgriezieties vēlāk pēc N27 atkārtošanas intervāliem (1 / 3 / 7 dienas) vai izmantojiet N20 efemēro variantu ceļu neierobežotiem atkārtojumiem.', { target_length: targetLength });
                exitOptions = {
                    scheduler_intervals_note_lv: 'N27 Leitnera atkārtošanas intervāli (1 / 3 / 7 dienas): mērķi atgriežas atkārtošanā pēc noteiktā dienu skaita.',
                    ephemeral_option_lv: 'N20 efemērais variantu ceļš (SimVariantEngine.instantiateEphemeral): neierobežoti atkārtojumi no saimes veidnes bez bankas ierobežojuma.',
                    ephemeral_available: true
                };
            }
            else if (pendingReviewCount > 0) {
                shortageReason = 'pending_review';
                shortageCopyLv = termText(termsMap, 'practice.shortage.pending_review', 'Pieejami {true_length} no {target_length} uzdevumiem: gaida recenziju ({pending_count} neapstiprināti uzdevumi netiek iekļauti).', { true_length: trueLength, target_length: targetLength, pending_count: pendingReviewCount });
            }
            else {
                shortageReason = 'filter_shortage';
                shortageCopyLv = termText(termsMap, 'practice.shortage.filter', 'Pieejami {true_length} no {target_length} uzdevumiem: izvēlētais filtrs atstāj {true_length} derīgus uzdevumus (ceļš netiek mākslīgi papildināts).', { true_length: trueLength, target_length: targetLength });
            }
        }
        const itemIds = chosen.map(function (q) { return String(q.question_id); });
        const digestPayload = sortedValue({
            entry_source: req.entry_source,
            topic: req.topic,
            outcome_id: req.outcome_id,
            filters: req.filters,
            target_length: targetLength,
            true_length: trueLength,
            shortage: isShortage,
            shortage_reason: shortageReason,
            pending_review_count: pendingReviewCount,
            difficulty_mode: anyDifficultyDeclared ? 'declared' : 'absent_family_order',
            item_ids: itemIds
        });
        return {
            schema_version: SCHEMA_VERSION,
            entry_source: req.entry_source,
            topic: req.topic,
            outcome_id: req.outcome_id,
            remediation_entry_id: req.remediation_entry_id,
            filters: copyJson(req.filters),
            target_length: targetLength,
            true_length: trueLength,
            shortage: isShortage,
            shortage_reason: shortageReason,
            shortage_copy_lv: shortageCopyLv,
            pending_review_count: pendingReviewCount,
            history_empty: attemptedIds.length === 0,
            history_attempted_count: attemptedIds.length,
            excluded_count: excludedCount,
            difficulty_mode: anyDifficultyDeclared ? 'declared' : 'absent_family_order',
            items: chosen,
            item_ids: itemIds,
            exit_options: exitOptions,
            digest: digestValue(digestPayload)
        };
    }
    /* --------------------------------------------------- mode & help contract */
    function createFallbackModeRegistry(discipline) {
        let current = isText(discipline.default_mode) ? discipline.default_mode : 'practice';
        const modes = isObject(discipline.modes) ? discipline.modes : {};
        const errCode = isText(discipline.unregistered_component_error)
            ? discipline.unregistered_component_error
            : 'E_MODE_COMPONENT_NOT_ALLOWED';
        function getDef(mode) {
            const m = mode || current;
            const found = modes[m];
            if (!isObject(found)) {
                fail(errCode, 'Režīms "' + String(m) + '" nav reģistrēts.', { mode: m });
            }
            return found;
        }
        return {
            getMode: function () { return current; },
            setMode: function (mode) { getDef(mode); current = mode; },
            modes: function () { return Object.keys(modes).sort(); },
            allowedComponents: function (mode) {
                const list = getDef(mode).allowed_components;
                return Array.isArray(list) ? list.slice() : [];
            },
            forbiddenComponents: function (mode) {
                const list = getDef(mode).forbidden_components;
                return Array.isArray(list) ? list.slice() : [];
            },
            isAllowed: function (component, mode) {
                const list = getDef(mode).allowed_components;
                return Array.isArray(list) && list.indexOf(component) !== -1;
            },
            assertAllowed: function (component, mode) {
                const m = mode || current;
                const list = getDef(m).allowed_components;
                if (!Array.isArray(list) || list.indexOf(component) === -1) {
                    fail(errCode, 'Komponents "' + component + '" nav atļauts režīmā "' + m + '".', {
                        component: component,
                        mode: m
                    });
                }
            }
        };
    }
    function resolveModeRegistry(doc, examPolicy) {
        const pol = examPolicy || readIsland(doc || root.document, 'sim-exam-policy');
        const discipline = pol && isObject(pol.view_discipline) ? pol.view_discipline : {
            default_mode: 'practice',
            modes: {
                exam: {
                    allowed_components: ['input', 'timer', 'navigator', 'map', 'review'],
                    forbidden_components: ['hint', 'chain', 'method-card', 'term-lookup']
                },
                practice: {
                    allowed_components: ['input', 'timer', 'navigator', 'map', 'review', 'hint', 'chain', 'method-card', 'term-lookup'],
                    forbidden_components: []
                }
            },
            unregistered_component_error: 'E_MODE_COMPONENT_NOT_ALLOWED'
        };
        if (root.SimExam && typeof root.SimExam.createModeRegistry === 'function') {
            return root.SimExam.createModeRegistry(discipline);
        }
        return createFallbackModeRegistry(discipline);
    }
    function buildChainByFamilyMap(doc, methodCardsData) {
        const map = {};
        const mc = methodCardsData || readIsland(doc || root.document, 'sim-method-cards');
        const cards = mc && Array.isArray(mc.cards) ? mc.cards : [];
        for (let i = 0; i < cards.length; i += 1) {
            const card = cards[i];
            if (isObject(card) && isText(card.family_id) && isText(card.chain_id)) {
                map[card.family_id] = card.chain_id;
            }
        }
        return map;
    }
    function describeHelpContract(item, options) {
        const opts = options || {};
        const mode = isText(opts.mode) ? opts.mode : 'practice';
        const registry = resolveModeRegistry(opts.doc, opts.examPolicy);
        registry.setMode(mode);
        const helpComponents = ['hint', 'chain', 'term-lookup'];
        for (let i = 0; i < helpComponents.length; i += 1) {
            registry.assertAllowed(helpComponents[i], mode);
        }
        const chainMap = buildChainByFamilyMap(opts.doc, opts.methodCards);
        const famId = isText(item.family_id) ? item.family_id : '';
        const chainId = famId && has(chainMap, famId) ? chainMap[famId] : null;
        const byFamCov = buildCoverageFamilyMap(opts.coverage || readIsland(opts.doc || root.document, 'sim-coverage'));
        const concepts = instanceOutcomes(item, byFamCov);
        const markers = ['data-sim-component="hint"', 'data-sim-component="term-lookup"'];
        if (chainId) {
            markers.push('data-sim-component="chain"');
        }
        return {
            mode: mode,
            help_enabled: true,
            allowed_help_components: helpComponents.slice(),
            hint_family_id: famId,
            concept_ids: concepts,
            chain_id: chainId,
            markers: markers
        };
    }
    /* --------------------------------------------------- DOM & runner helper */
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
    function renderError(doc, err) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('prakse-error');
        if (!box) {
            return;
        }
        const code = isObject(err) && isText(err.code) ? err.code : 'E_PRACTICE_ERROR';
        const msg = isObject(err) && isText(err.message) ? err.message : String(err);
        box.textContent = '[' + code + '] ' + msg;
        box.hidden = false;
    }
    function buildMethodEngine(doc) {
        const me = root.SimMethodEngine;
        const island = readIsland(doc, 'sim-method-engine');
        const termsIsland = readIsland(doc, 'sim-terms');
        if (!me || typeof me.MethodEngine !== 'function' || !island) {
            return undefined;
        }
        const engine = new me.MethodEngine(island, termsIsland);
        const method = Object.create(engine);
        method.MethodEngine = me.MethodEngine;
        method.specForVector = me.specForVector;
        method.sha256 = me.sha256;
        return method;
    }
    function buildGradedSlotSummary(item, payload, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const gradingApi = root.SimGrading;
        const feedbackApi = root.SimFeedback;
        if (!gradingApi || typeof gradingApi.gradePracticeRecord !== 'function' || !feedbackApi || typeof feedbackApi.assemble !== 'function') {
            return fail('E_PRACTICE_GRADING_FAILED', 'Vērtēšanas dzinēji (SimGrading / SimFeedback) nav ielādēti.', {});
        }
        const gCtxInput = opts.gradingContext || {};
        const instancesById = isObject(gCtxInput.bank && gCtxInput.bank.instancesById)
            ? copyJson(gCtxInput.bank.instancesById)
            : {};
        if (Array.isArray(opts.bankQuestions)) {
            for (let i = 0; i < opts.bankQuestions.length; i += 1) {
                const q = opts.bankQuestions[i];
                if (isObject(q) && isText(q.question_id)) {
                    instancesById[q.question_id] = q;
                }
            }
        }
        instancesById[item.question_id] = item;
        let points = 0;
        const rubric = Array.isArray(item.rubric) ? item.rubric : [];
        for (let i = 0; i < rubric.length; i += 1) {
            if (isObject(rubric[i]) && typeof rubric[i].points === 'number') {
                points += Number(rubric[i].points);
            }
        }
        const slotId = 'PRAC-1';
        const examPolicy = gCtxInput.examPolicy || readIsland(doc, 'sim-exam-policy') || {
            session_contract: { terminal_states: ['submitted', 'expired', 'aborted'] }
        };
        const responseTypes = gCtxInput.responseTypes || readIsland(doc, 'sim-response-types');
        const conventions = gCtxInput.conventions || readIsland(doc, 'sim-conventions');
        const termsIsland = gCtxInput.terms || readIsland(doc, 'sim-terms');
        const figuresList = readIsland(doc, 'sim-figures');
        let figuresById = isObject(gCtxInput.figures) ? gCtxInput.figures : {};
        if (Object.keys(figuresById).length === 0 && figuresList && Array.isArray(figuresList.figures)) {
            figuresById = {};
            for (let i = 0; i < figuresList.figures.length; i += 1) {
                const fig = figuresList.figures[i];
                if (isObject(fig) && isText(fig.figure_id)) {
                    figuresById[fig.figure_id] = fig;
                }
            }
        }
        const oracle = gCtxInput.oracle || {
            oracle_version: '1.0.0',
            oracle_digest: digestValue({ owner: 'N30', instance_id: item.question_id }),
            conventions_digest: conventions ? digestValue(conventions) : digestValue({})
        };
        const gContext = {
            doc: doc,
            quantity: gCtxInput.quantity || root.SimEngines,
            method: gCtxInput.method || buildMethodEngine(doc),
            graph: gCtxInput.graph || root.SimGraphScoring,
            inputsRegistry: gCtxInput.inputsRegistry || root.SimInputsRegistry,
            inputsIntegration: gCtxInput.inputsIntegration || root.SimInputsIntegration,
            examPolicy: examPolicy,
            gradingPolicy: gCtxInput.gradingPolicy || readIsland(doc, 'sim-grading-policy'),
            classification: gCtxInput.classification || readIsland(doc, 'sim-feedback-classification'),
            responseTypes: responseTypes,
            conventions: conventions,
            terms: typeof feedbackApi.loadTermsMap === 'function'
                ? feedbackApi.loadTermsMap(doc || termsIsland)
                : loadTermsMap(termsIsland || doc),
            figures: figuresById,
            bank: { instancesById: instancesById },
            oracle: oracle,
            bindingSource: 'N30-practice-path'
        };
        let figureId;
        if (item.type_id === 'Q11') {
            figureId = isText(item.figure_id) ? item.figure_id : (Number(item.topic) === 2 ? 'FIG-T2-PLOT-NACL-DENSITY' :
                Number(item.topic) === 5 ? 'FIG-T5-LIN-FIRST' :
                    Number(item.topic) === 7 ? 'FIG-T67-CAL-MASTER' : undefined);
        }
        const binding = {
            slot_id: slotId,
            type_id: item.type_id,
            instance_id: item.question_id,
            instance: item
        };
        if (figureId) {
            binding.figure_id = figureId;
        }
        const kind = isText(payload.kind) && payload.kind !== '' ? payload.kind : String(item.payload_class || 'numeric');
        const practiceRecord = {
            schema_version: 1,
            session_id: 'PRAC-' + String(item.question_id),
            form_id: 'PRACTICE',
            state: 'submitted',
            started_at_ms: 0,
            finished_at_ms: 1000,
            elapsed_ms: 1000,
            flags: [],
            unanswered_slot_ids: [],
            remediation_slot_ids: [],
            transitions: [{ event: 'start', from: 'not-started', to: 'running' }, { event: 'submit', from: 'review', to: 'submitted' }],
            slots: [{ slot_id: slotId, topic: Number(item.topic), points: points }],
            answers: [{ slot_id: slotId, kind: kind, payload: payload }]
        };
        const core = gradingApi.gradePracticeRecord(practiceRecord, [binding], gContext);
        const fb = feedbackApi.assemble(core, gContext);
        const fullRecord = gradingApi.composeGradedRecord(core, fb);
        let feedbackHtml = '';
        if (typeof feedbackApi.buildScoreReport === 'function') {
            const termsMap = typeof feedbackApi.loadTermsMap === 'function'
                ? feedbackApi.loadTermsMap(doc || termsIsland)
                : {};
            const report = feedbackApi.buildScoreReport(fullRecord, termsMap);
            feedbackHtml = report && isText(report.html) ? report.html : '';
        }
        const slotRecord = Array.isArray(fullRecord.slots) && fullRecord.slots.length > 0 ? fullRecord.slots[0] : {};
        const masteryEffects = [];
        const remediationEffects = [];
        if (opts.store && typeof opts.store.update === 'function') {
            const masteryApi = root.SimMastery;
            const remApi = root.SimRemediation;
            const cov = opts.coverage || readIsland(doc, 'sim-coverage');
            let masteryBefore = {};
            if (masteryApi && typeof masteryApi.readFromStore === 'function' && cov) {
                try {
                    const mp = masteryApi.loadPolicy(doc);
                    masteryBefore = masteryApi.readFromStore(opts.store, cov, mp.policy, mp.digest).outcomes || {};
                }
                catch (_err) {
                    masteryBefore = {};
                }
            }
            if (opts.remediationEntryId && remApi && typeof remApi.recordRetryVerdict === 'function') {
                const retryRes = remApi.recordRetryVerdict(opts.store, opts.remediationEntryId, fullRecord, {
                    slot_id: slotId,
                    coverage: cov,
                    day: opts.day !== undefined ? opts.day : null,
                    doc: doc
                });
                remediationEffects.push({
                    entry_id: retryRes.entry.id,
                    family_id: retryRes.entry.family_id,
                    outcome_id: retryRes.entry.outcome_id,
                    state: retryRes.entry.state,
                    verdict: retryRes.verdict
                });
                opts.store.update(function (draft) {
                    if (!isObject(draft.practice_history)) {
                        draft.practice_history = { attempted_instance_ids: [], skipped_instance_ids: [] };
                    }
                    if (!Array.isArray(draft.practice_history.attempted_instance_ids)) {
                        draft.practice_history.attempted_instance_ids = [];
                    }
                    if (draft.practice_history.attempted_instance_ids.indexOf(item.question_id) === -1) {
                        draft.practice_history.attempted_instance_ids.push(item.question_id);
                    }
                    draft.practice_history.attempted_instance_ids.sort();
                });
            }
            else {
                const analyticsEvents = gradingApi.toAnalyticsEvents(fullRecord);
                opts.store.update(function (draft) {
                    const tk = String(item.topic || '');
                    if (isObject(draft.progress) && isObject(draft.progress.topics) && has(draft.progress.topics, tk)) {
                        draft.progress.topics[tk].practiced_tasks = Number(draft.progress.topics[tk].practiced_tasks || 0) + 1;
                    }
                    const oids = Array.isArray(slotRecord.outcome_ids) ? slotRecord.outcome_ids : [];
                    const autoMax = slotRecord.task ? Number(slotRecord.task.auto_max_points || 0) : 0;
                    const autoPts = slotRecord.task ? Number(slotRecord.task.auto_points || 0) : 0;
                    const autoCorrect = slotRecord.state === 'graded' && (slotRecord.verdict_class === 'correct' ||
                        (slotRecord.verdict_class === 'auto_passed_pending_review' && autoMax > 0 && autoPts === autoMax));
                    if (isObject(draft.progress) && isObject(draft.progress.outcomes)) {
                        for (let j = 0; j < oids.length; j += 1) {
                            const oid = String(oids[j]);
                            const st = draft.progress.outcomes[oid] || { attempts: 0, first_attempt_correct: null, correct_count: 0 };
                            if (st.attempts === 0) {
                                st.first_attempt_correct = autoCorrect;
                            }
                            st.attempts += 1;
                            if (autoCorrect) {
                                st.correct_count += 1;
                            }
                            draft.progress.outcomes[oid] = st;
                        }
                    }
                    if (!isObject(draft.practice_history)) {
                        draft.practice_history = { attempted_instance_ids: [], skipped_instance_ids: [] };
                    }
                    if (!Array.isArray(draft.practice_history.attempted_instance_ids)) {
                        draft.practice_history.attempted_instance_ids = [];
                    }
                    if (draft.practice_history.attempted_instance_ids.indexOf(item.question_id) === -1) {
                        draft.practice_history.attempted_instance_ids.push(item.question_id);
                    }
                    draft.practice_history.attempted_instance_ids.sort();
                    if (remApi && typeof remApi.applyGradedRecordDraft === 'function') {
                        const touched = remApi.applyGradedRecordDraft(draft, fullRecord, { doc: doc, coverage: cov });
                        for (let t = 0; t < touched.length; t += 1) {
                            remediationEffects.push({
                                entry_id: touched[t].entry.id,
                                family_id: touched[t].entry.family_id,
                                outcome_id: touched[t].entry.outcome_id,
                                state: touched[t].entry.state,
                                action: touched[t].action
                            });
                        }
                    }
                    if (!Array.isArray(draft.events)) {
                        draft.events = [];
                    }
                    for (let e = 0; e < analyticsEvents.length; e += 1) {
                        const ev = analyticsEvents[e];
                        if (ev.event === 'session-completed') {
                            continue;
                        }
                        const copyEv = copyJson(ev);
                        copyEv.instance_id = item.question_id;
                        draft.events.push(copyEv);
                    }
                    if (masteryApi && typeof masteryApi.applyGradedRecordDraft === 'function') {
                        masteryApi.applyGradedRecordDraft(draft, fullRecord, cov, null, '', opts.day !== undefined ? opts.day : null);
                    }
                });
            }
            if (masteryApi && typeof masteryApi.readFromStore === 'function' && cov) {
                try {
                    const mp = masteryApi.loadPolicy(doc);
                    const masteryAfter = masteryApi.readFromStore(opts.store, cov, mp.policy, mp.digest).outcomes || {};
                    const oids = Array.isArray(slotRecord.outcome_ids) ? slotRecord.outcome_ids : [];
                    for (let j = 0; j < oids.length; j += 1) {
                        const oid = String(oids[j]);
                        const bState = masteryBefore[oid] ? String(masteryBefore[oid].state) : 'unseen';
                        const aState = masteryAfter[oid] ? String(masteryAfter[oid].state) : 'unseen';
                        masteryEffects.push({ outcome_id: oid, before_state: bState, after_state: aState });
                    }
                }
                catch (_err) {
                    /* ignore */
                }
            }
        }
        return {
            fullRecord: fullRecord,
            slotRecord: slotRecord,
            feedbackHtml: feedbackHtml,
            masteryEffects: masteryEffects,
            remediationEffects: remediationEffects
        };
    }
    /* --------------------------------------------------- path runner & UI */
    const sessionAnsweredRegistry = [];
    function createRunner(pathResult, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const mode = isText(opts.mode) ? opts.mode : 'practice';
        const sessionAnswered = Array.isArray(opts.sessionAnsweredIds)
            ? opts.sessionAnsweredIds
            : sessionAnsweredRegistry;
        let status = pathResult.true_length === 0 ? 'exhausted' : 'active';
        let currentIndex = 0;
        let awaitingNext = false;
        let lastFeedbackText = '';
        const records = [];
        const masteryTransitions = [];
        const remediationTouches = [];
        function currentItem() {
            if (status !== 'active' || currentIndex >= pathResult.items.length) {
                return null;
            }
            return pathResult.items[currentIndex];
        }
        function getSummary() {
            let attempted = 0;
            let correct = 0;
            let partial = 0;
            let incorrect = 0;
            let manualPending = 0;
            let skipped = 0;
            for (let i = 0; i < records.length; i += 1) {
                const rec = records[i];
                if (rec.status === 'skipped') {
                    skipped += 1;
                    continue;
                }
                attempted += 1;
                if (rec.verdict_class === 'correct' ||
                    (rec.verdict_class === 'auto_passed_pending_review' && rec.auto_max_points > 0 && rec.auto_points === rec.auto_max_points)) {
                    correct += 1;
                }
                else if (rec.verdict_class === 'partial') {
                    partial += 1;
                }
                else if (rec.verdict_class === 'pending_self_assessment' || rec.verdict_class === 'auto_passed_pending_review') {
                    manualPending += 1;
                }
                else {
                    incorrect += 1;
                }
            }
            const unvisited = Math.max(0, pathResult.true_length - records.length);
            return sortedValue({
                schema_version: SCHEMA_VERSION,
                status: status,
                entry_source: pathResult.entry_source,
                topic: pathResult.topic,
                outcome_id: pathResult.outcome_id,
                declared_length: pathResult.target_length,
                true_length: pathResult.true_length,
                shortage: pathResult.shortage,
                shortage_reason: pathResult.shortage_reason,
                attempted_count: attempted,
                correct_count: correct,
                partial_count: partial,
                incorrect_count: incorrect,
                manual_pending_count: manualPending,
                skipped_count: skipped,
                unvisited_count: unvisited,
                mastery_effects: masteryTransitions.slice(),
                remediation_effects: remediationTouches.slice(),
                records: copyJson(records),
                path_digest: pathResult.digest
            });
        }
        function renderHelpIntoRunner(item) {
            if (!doc || typeof doc.getElementById !== 'function') {
                return;
            }
            const helpSlot = doc.getElementById('prakse-help-slot');
            if (!helpSlot) {
                return;
            }
            let helpWrap = doc.getElementById('prakse-runner-help');
            if (!helpWrap) {
                helpWrap = makeEl(doc, 'div', 'prakse-runner-help');
                helpWrap.id = 'prakse-runner-help';
                helpSlot.appendChild(helpWrap);
            }
            clearNode(helpWrap);
            const contract = describeHelpContract(item, {
                mode: mode,
                doc: doc,
                coverage: opts.coverage || null
            });
            const termsMap = loadTermsMap(doc);
            const hintBtn = makeEl(doc, 'button', 'btn-control prakse-help-btn', termText(termsMap, 'practice.help.hint_btn', 'Palīdzības kāpnes (N08)'));
            hintBtn.type = 'button';
            hintBtn.id = 'prakse-open-hint';
            hintBtn.setAttribute('data-sim-component', 'hint');
            hintBtn.setAttribute('data-family-id', contract.hint_family_id);
            hintBtn.addEventListener('click', function () {
                if (root.SimHintDrawer && typeof root.SimHintDrawer.open === 'function') {
                    root.SimHintDrawer.open({
                        mode: mode,
                        familyId: contract.hint_family_id,
                        itemId: String(item.question_id || ''),
                        returnContext: { elementId: hintBtn.id, triggerEl: hintBtn }
                    }, doc);
                }
            });
            helpWrap.appendChild(hintBtn);
            if (contract.concept_ids.length > 0) {
                const conceptBtn = makeEl(doc, 'button', 'btn-control prakse-help-btn', termText(termsMap, 'practice.help.concept_btn', 'Koncepta atvilktne (N07)') + ' (' + contract.concept_ids[0] + ')');
                conceptBtn.type = 'button';
                conceptBtn.id = 'prakse-open-concept';
                conceptBtn.setAttribute('data-sim-component', 'term-lookup');
                conceptBtn.setAttribute('data-concept-id', contract.concept_ids[0]);
                conceptBtn.addEventListener('click', function () {
                    if (root.SimConceptDrawer && typeof root.SimConceptDrawer.openConcept === 'function') {
                        root.SimConceptDrawer.openConcept({
                            conceptId: contract.concept_ids[0],
                            source: 'practice-runner',
                            returnContext: { elementId: conceptBtn.id, triggerEl: conceptBtn, labelLv: 'Atgriezties praksē' }
                        }, doc);
                    }
                });
                helpWrap.appendChild(conceptBtn);
            }
            const termBtn = makeEl(doc, 'button', 'btn-control prakse-help-btn', termText(termsMap, 'practice.help.term_btn', 'Terminu uzziņa (N10)'));
            termBtn.type = 'button';
            termBtn.id = 'prakse-open-terms';
            termBtn.setAttribute('data-sim-component', 'term-lookup');
            termBtn.addEventListener('click', function () {
                const termHost = doc.getElementById('prakse-runner-term-host');
                if (!termHost) {
                    return;
                }
                termHost.hidden = !termHost.hidden;
                if (!termHost.hidden) {
                    clearNode(termHost);
                    termHost.appendChild(makeEl(doc, 'h5', 'prakse-term-heading', 'Terminu uzziņa (N10)'));
                    const keys = ['practice.honesty_note', 'nav.prakse'];
                    for (let k = 0; k < keys.length; k += 1) {
                        if (has(termsMap, keys[k])) {
                            termHost.appendChild(makeEl(doc, 'p', 'prakse-term-line', keys[k] + ': ' + termsMap[keys[k]]));
                        }
                    }
                }
            });
            helpWrap.appendChild(termBtn);
            if (contract.chain_id) {
                const chainBtn = makeEl(doc, 'button', 'btn-control prakse-help-btn', termText(termsMap, 'practice.help.chain_btn', 'Atklāt darba piemēra ķēdi (N16)') + ' (' + contract.chain_id + ')');
                chainBtn.type = 'button';
                chainBtn.id = 'prakse-open-chain';
                chainBtn.setAttribute('data-sim-component', 'chain');
                chainBtn.setAttribute('data-chain-id', contract.chain_id);
                chainBtn.addEventListener('click', function () {
                    const chainHost = doc.getElementById('prakse-runner-chain-host');
                    if (!chainHost) {
                        return;
                    }
                    clearNode(chainHost);
                    chainHost.hidden = false;
                    if (root.SimChains && typeof root.SimChains.mountChain === 'function') {
                        root.SimChains.mountChain(doc, chainHost, contract.chain_id, 'prac-' + String(item.question_id || '0'));
                    }
                });
                helpWrap.appendChild(chainBtn);
            }
            else {
                helpWrap.appendChild(makeEl(doc, 'span', 'prakse-no-chain-note', termText(termsMap, 'practice.help.no_chain', 'Šai uzdevumu saimei nav piesaistītas darba piemēra ķēdes.')));
            }
        }
        function renderDom() {
            if (!doc || typeof doc.getElementById !== 'function') {
                return;
            }
            const runnerEl = doc.getElementById('prakse-runner');
            const summaryEl = doc.getElementById('prakse-summary');
            const termsMap = loadTermsMap(doc);
            if (status === 'completed' || status === 'ended_early') {
                if (runnerEl) {
                    runnerEl.hidden = true;
                }
                if (summaryEl) {
                    clearNode(summaryEl);
                    summaryEl.hidden = false;
                    const sum = getSummary();
                    summaryEl.setAttribute('data-status', sum.status);
                    summaryEl.setAttribute('data-skipped-count', String(sum.skipped_count));
                    summaryEl.setAttribute('data-incorrect-count', String(sum.incorrect_count));
                    summaryEl.appendChild(makeEl(doc, 'h4', 'prakse-summary-title', termText(termsMap, 'practice.summary.title', 'Prakses ceļa kopsavilkums (PROPOSED)')));
                    summaryEl.appendChild(makeEl(doc, 'p', 'prakse-summary-counts', termText(termsMap, 'practice.summary.counts', 'Mēģināti: {attempted} · Pareizi: {correct} · Daļēji: {partial} · Nepareizi: {incorrect} · Gaida pašvērtējumu/ārēju: {manual_pending} · Izlaisti: {skipped} (izlaistie netiek skaitīti kā kļūdas)', {
                        attempted: sum.attempted_count,
                        correct: sum.correct_count,
                        partial: sum.partial_count,
                        incorrect: sum.incorrect_count,
                        manual_pending: sum.manual_pending_count,
                        skipped: sum.skipped_count
                    })));
                    summaryEl.appendChild(makeEl(doc, 'h5', 'prakse-summary-mastery-heading', termText(termsMap, 'practice.summary.mastery_heading', 'Ietekme uz apguves stāvokli (N26)')));
                    if (sum.mastery_effects.length === 0) {
                        summaryEl.appendChild(makeEl(doc, 'p', 'prakse-summary-mastery-none', termText(termsMap, 'practice.summary.mastery_none', 'Šajā prakses ceļā apguves stāvoklis nemainījās.')));
                    }
                    else {
                        const ul = makeEl(doc, 'ul', 'prakse-summary-mastery-list');
                        for (let i = 0; i < sum.mastery_effects.length; i += 1) {
                            const eff = sum.mastery_effects[i];
                            ul.appendChild(makeEl(doc, 'li', null, eff.outcome_id + ': ' + eff.before_state + ' → ' + eff.after_state));
                        }
                        summaryEl.appendChild(ul);
                    }
                    const closeBtn = makeEl(doc, 'button', 'btn-control prakse-summary-close', termText(termsMap, 'practice.summary.close', 'Atgriezties pie prakses tēmām'));
                    closeBtn.type = 'button';
                    closeBtn.id = 'prakse-summary-close-btn';
                    closeBtn.addEventListener('click', function () {
                        summaryEl.hidden = true;
                    });
                    summaryEl.appendChild(closeBtn);
                }
                return;
            }
            if (summaryEl) {
                summaryEl.hidden = true;
            }
            if (!runnerEl) {
                return;
            }
            runnerEl.hidden = false;
            const titleEl = doc.getElementById('prakse-runner-title');
            if (titleEl) {
                titleEl.textContent = (pathResult.topic !== null ? pathResult.topic + '. tēmas prakses ceļš' : 'Prakses ceļš') +
                    (pathResult.outcome_id ? ' (' + pathResult.outcome_id + ')' : '');
            }
            const progEl = doc.getElementById('prakse-runner-progress');
            if (progEl) {
                progEl.textContent = status === 'exhausted'
                    ? 'Pieejami 0 no ' + pathResult.target_length + ' uzdevumiem'
                    : termText(termsMap, 'practice.runner.progress', 'Uzdevums {current} no {true_length}', {
                        current: currentIndex + 1,
                        true_length: pathResult.true_length
                    });
            }
            const shortageEl = doc.getElementById('prakse-shortage-banner');
            if (shortageEl) {
                if (pathResult.shortage && pathResult.shortage_copy_lv) {
                    shortageEl.hidden = false;
                    shortageEl.setAttribute('data-shortage-reason', String(pathResult.shortage_reason || ''));
                    shortageEl.textContent = pathResult.shortage_copy_lv;
                }
                else {
                    shortageEl.hidden = true;
                    shortageEl.textContent = '';
                }
            }
            const exhaustedEl = doc.getElementById('prakse-exhausted-panel');
            const itemHost = doc.getElementById('prakse-runner-item-host');
            const controlsEl = doc.getElementById('prakse-runner-controls');
            const fbEl = doc.getElementById('prakse-runner-feedback');
            const chainHost = doc.getElementById('prakse-runner-chain-host');
            const termHost = doc.getElementById('prakse-runner-term-host');
            if (chainHost) {
                chainHost.hidden = true;
                clearNode(chainHost);
            }
            if (termHost) {
                termHost.hidden = true;
                clearNode(termHost);
            }
            if (status === 'exhausted') {
                if (itemHost) {
                    clearNode(itemHost);
                }
                if (controlsEl) {
                    controlsEl.hidden = true;
                }
                if (fbEl) {
                    fbEl.hidden = true;
                }
                if (exhaustedEl) {
                    clearNode(exhaustedEl);
                    exhaustedEl.hidden = false;
                    if (pathResult.exit_options) {
                        exhaustedEl.appendChild(makeEl(doc, 'p', 'prakse-exhausted-intervals', pathResult.exit_options.scheduler_intervals_note_lv));
                        exhaustedEl.appendChild(makeEl(doc, 'p', 'prakse-exhausted-ephemeral', pathResult.exit_options.ephemeral_option_lv));
                    }
                    const ephBtn = makeEl(doc, 'button', 'btn-control prakse-ephemeral-btn', termText(termsMap, 'practice.shortage.ephemeral_cta', 'Ģenerēt N20 efemēro variantu'));
                    ephBtn.type = 'button';
                    ephBtn.id = 'prakse-ephemeral-btn';
                    exhaustedEl.appendChild(ephBtn);
                }
                return;
            }
            if (exhaustedEl) {
                exhaustedEl.hidden = true;
            }
            if (controlsEl) {
                controlsEl.hidden = false;
            }
            const item = currentItem();
            if (!item) {
                return;
            }
            if (itemHost) {
                clearNode(itemHost);
                const meta = makeEl(doc, 'p', 'prakse-item-meta', item.question_id + ' · ' + item.family_id + ' (' + item.type_id + ', ' + String(item.difficulty || '—') + ')');
                itemHost.appendChild(meta);
                const stem = makeEl(doc, 'p', 'prakse-item-stem', item.stem_lv || '');
                stem.id = 'prakse-current-stem';
                itemHost.appendChild(stem);
                const inputsComp = root.SimInputsComponents;
                const rtIsland = readIsland(doc, 'sim-response-types');
                const termsIsland = readIsland(doc, 'sim-terms');
                if (inputsComp && typeof inputsComp.render === 'function' && rtIsland && isObject(rtIsland.types) && rtIsland.types[item.type_id]) {
                    try {
                        const desc = inputsComp.render(item.type_id, rtIsland.types[item.type_id], item, null, termsIsland || { terms: [] });
                        const descBox = makeEl(doc, 'div', 'prakse-n22-input-host');
                        descBox.setAttribute('data-n22-type', item.type_id);
                        descBox.setAttribute('data-n22-fields', String(Array.isArray(desc.fields) ? desc.fields.length : 0));
                        const fields = Array.isArray(desc.fields) ? desc.fields : [];
                        for (let f = 0; f < fields.length; f += 1) {
                            const fld = fields[f];
                            const lbl = makeEl(doc, 'label', 'prakse-input-label', fld.label_lv || fld.field_id || 'Atbilde');
                            const inp = makeEl(doc, 'input', 'prakse-input-field');
                            inp.type = 'text';
                            inp.id = 'prakse-input-' + String(fld.field_id || f);
                            inp.setAttribute('data-field-id', String(fld.field_id || 'value'));
                            descBox.appendChild(lbl);
                            descBox.appendChild(inp);
                        }
                        itemHost.appendChild(descBox);
                    }
                    catch (_err) {
                        const inp = makeEl(doc, 'input', 'prakse-input-field');
                        inp.type = 'text';
                        inp.id = 'prakse-input-fallback';
                        itemHost.appendChild(inp);
                    }
                }
                else {
                    const inp = makeEl(doc, 'input', 'prakse-input-field');
                    inp.type = 'text';
                    inp.id = 'prakse-input-fallback';
                    itemHost.appendChild(inp);
                }
            }
            renderHelpIntoRunner(item);
            const submitBtn = doc.getElementById('prakse-submit-btn');
            const skipBtn = doc.getElementById('prakse-skip-btn');
            const nextBtn = doc.getElementById('prakse-next-btn');
            if (submitBtn) {
                submitBtn.hidden = awaitingNext;
            }
            if (skipBtn) {
                skipBtn.hidden = awaitingNext;
            }
            if (nextBtn) {
                nextBtn.hidden = !awaitingNext;
            }
            if (fbEl) {
                if (awaitingNext && lastFeedbackText) {
                    fbEl.hidden = false;
                    fbEl.textContent = lastFeedbackText;
                }
                else {
                    fbEl.hidden = true;
                    fbEl.textContent = '';
                }
            }
        }
        function submitAnswer(payload, submitOpts) {
            if (status !== 'active') {
                return fail('E_PRACTICE_ALREADY_FINISHED', 'Prakses ceļš jau ir pabeigts vai izsmelts.', { status: status });
            }
            const item = currentItem();
            if (!item) {
                return fail('E_PRACTICE_NO_ACTIVE_PATH', 'Nav aktīva prakses uzdevuma.', {});
            }
            const graded = buildGradedSlotSummary(item, payload, {
                doc: doc,
                bankQuestions: opts.bankQuestions,
                gradingContext: opts.gradingContext,
                store: opts.store,
                coverage: opts.coverage,
                day: opts.day,
                remediationEntryId: pathResult.remediation_entry_id
            });
            const slot = graded.slotRecord;
            const task = isObject(slot.task) ? slot.task : {};
            const rec = {
                index: currentIndex,
                instance_id: String(item.question_id),
                family_id: String(item.family_id || ''),
                type_id: String(item.type_id || ''),
                outcome_ids: Array.isArray(slot.outcome_ids) ? slot.outcome_ids.slice() : [],
                status: 'graded',
                graded: true,
                verdict_class: isText(slot.verdict_class) ? slot.verdict_class : String(slot.state || 'incorrect'),
                auto_points: Number(task.auto_points || 0),
                auto_max_points: Number(task.auto_max_points || 0),
                pending_points: Number(task.pending_points || 0),
                pending_max_points: Number(task.pending_max_points || 0),
                graded_digest: isText(graded.fullRecord.digest) ? graded.fullRecord.digest : null,
                mastery_effects: graded.masteryEffects.slice(),
                remediation_effects: graded.remediationEffects.slice()
            };
            records.push(rec);
            if (sessionAnswered.indexOf(rec.instance_id) === -1) {
                sessionAnswered.push(rec.instance_id);
            }
            for (let i = 0; i < graded.masteryEffects.length; i += 1) {
                masteryTransitions.push(graded.masteryEffects[i]);
            }
            for (let i = 0; i < graded.remediationEffects.length; i += 1) {
                remediationTouches.push(graded.remediationEffects[i]);
            }
            lastFeedbackText = 'Verdikts: ' + String(rec.verdict_class) + ' (' + rec.auto_points + '/' + rec.auto_max_points + ' p.)';
            awaitingNext = true;
            if (!submitOpts || submitOpts.advance !== false) {
                currentIndex += 1;
                awaitingNext = false;
                if (currentIndex >= pathResult.items.length) {
                    status = 'completed';
                    if (typeof opts.onFinished === 'function') {
                        opts.onFinished(getSummary());
                    }
                }
            }
            renderDom();
            return {
                record: rec,
                full_record: graded.fullRecord,
                mastery_effects: graded.masteryEffects,
                remediation_effects: graded.remediationEffects,
                summary: status === 'completed' ? getSummary() : null
            };
        }
        function skipCurrent() {
            if (status !== 'active') {
                return fail('E_PRACTICE_ALREADY_FINISHED', 'Prakses ceļš jau ir pabeigts vai izsmelts.', { status: status });
            }
            const item = currentItem();
            if (!item) {
                return fail('E_PRACTICE_NO_ACTIVE_PATH', 'Nav aktīva prakses uzdevuma.', {});
            }
            const rec = {
                index: currentIndex,
                instance_id: String(item.question_id),
                family_id: String(item.family_id || ''),
                type_id: String(item.type_id || ''),
                outcome_ids: Array.isArray(item.outcome_ids) ? item.outcome_ids.slice() : [],
                status: 'skipped',
                graded: false,
                verdict_class: null,
                auto_points: 0,
                auto_max_points: 0,
                pending_points: 0,
                pending_max_points: 0,
                graded_digest: null,
                mastery_effects: [],
                remediation_effects: []
            };
            records.push(rec);
            currentIndex += 1;
            awaitingNext = false;
            lastFeedbackText = '';
            if (currentIndex >= pathResult.items.length) {
                status = 'completed';
                if (typeof opts.onFinished === 'function') {
                    opts.onFinished(getSummary());
                }
            }
            renderDom();
            const liveVerdict = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-live-verdict') : null;
            if (liveVerdict) {
                liveVerdict.textContent = 'Uzdevums izlaists (' + String(item.question_id) + ').';
            }
            return {
                record: rec,
                status: status,
                summary: status === 'completed' ? getSummary() : null
            };
        }
        function nextItem() {
            if (status !== 'active') {
                return getSummary();
            }
            if (awaitingNext) {
                currentIndex += 1;
                awaitingNext = false;
                lastFeedbackText = '';
                if (currentIndex >= pathResult.items.length) {
                    status = 'completed';
                    if (typeof opts.onFinished === 'function') {
                        opts.onFinished(getSummary());
                    }
                }
                renderDom();
            }
            return { status: status, current_index: currentIndex, item: currentItem() };
        }
        function endEarly() {
            if (status === 'active') {
                status = 'ended_early';
                if (typeof opts.onFinished === 'function') {
                    opts.onFinished(getSummary());
                }
                renderDom();
            }
            return getSummary();
        }
        renderDom();
        return {
            path: pathResult,
            snapshot: function () {
                return {
                    status: status,
                    current_index: currentIndex,
                    true_length: pathResult.true_length,
                    declared_length: pathResult.target_length,
                    current_item_id: currentItem() ? String(currentItem().question_id) : null,
                    records_count: records.length
                };
            },
            currentItem: currentItem,
            render: renderDom,
            submitAnswer: submitAnswer,
            skipCurrent: skipCurrent,
            nextItem: nextItem,
            endEarly: endEarly,
            getSummary: getSummary
        };
    }
    /* --------------------------------------------------- controller & init */
    let activeRunner = null;
    let activeContext = null;
    function renderTopicCards(doc, coverage, bankQuestions, policy, termsMap, onStartTopic) {
        const covTopics = coverage && Array.isArray(coverage.topics) ? coverage.topics : [];
        const covOutcomes = coverage && Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        const outcomesByTopic = {};
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const t = Number(covOutcomes[i].topic || 0);
            outcomesByTopic[t] = (outcomesByTopic[t] || 0) + 1;
        }
        const eligibleByTopic = {};
        const totalByTopic = {};
        for (let i = 0; i < bankQuestions.length; i += 1) {
            const q = bankQuestions[i];
            const t = Number(q.topic || 0);
            totalByTopic[t] = (totalByTopic[t] || 0) + 1;
            if (isReviewEligible(q, false)) {
                eligibleByTopic[t] = (eligibleByTopic[t] || 0) + 1;
            }
        }
        for (let t = 1; t <= 7; t += 1) {
            const card = doc.getElementById('prakse-tema-' + t);
            if (!card) {
                continue;
            }
            clearNode(card);
            let topicTitle = t + '. tēma';
            for (let i = 0; i < covTopics.length; i += 1) {
                if (Number(covTopics[i].topic) === t && isText(covTopics[i].name_lv)) {
                    topicTitle = t + '. ' + covTopics[i].name_lv;
                    break;
                }
            }
            const tlEntry = policy.topic_lengths && policy.topic_lengths[String(t)] ? policy.topic_lengths[String(t)] : {};
            const declared = Number(tlEntry.declared_length || 6);
            const ocCount = outcomesByTopic[t] || Number(tlEntry.outcomes_count || 0);
            const eligCount = eligibleByTopic[t] || 0;
            const totCount = totalByTopic[t] || eligCount;
            card.appendChild(makeEl(doc, 'h4', 'prakse-topic-title', topicTitle));
            card.appendChild(makeEl(doc, 'p', 'prakse-topic-meta', termText(termsMap, 'practice.topic.meta', '{outcomes} mācību mērķi · ceļš: {declared} uzd. · pieejami: {eligible} no {total} derīgiem', { outcomes: ocCount, declared: declared, eligible: eligCount, total: totCount })));
            const btn = makeEl(doc, 'button', 'btn-control prakse-topic-start-btn', termText(termsMap, 'practice.topic.start', 'Sākt tēmas praksi'));
            btn.type = 'button';
            btn.id = 'prakse-start-topic-' + t;
            btn.setAttribute('data-topic', String(t));
            (function (topicNum) {
                btn.addEventListener('click', function () {
                    onStartTopic(topicNum);
                });
            })(t);
            card.appendChild(btn);
        }
    }
    function startPath(entryOrHandoff, options) {
        const opts = options || {};
        const doc = opts.doc || (activeContext ? activeContext.doc : root.document);
        const store = opts.store !== undefined ? opts.store : (activeContext ? activeContext.store : null);
        const cov = opts.coverage !== undefined ? opts.coverage : (activeContext ? activeContext.coverage : readIsland(doc, 'sim-coverage'));
        const rt = opts.responseTypes !== undefined ? opts.responseTypes : (activeContext ? activeContext.responseTypes : readIsland(doc, 'sim-response-types'));
        let bankQuestions = opts.bankQuestions || (activeContext ? activeContext.bankQuestions : null);
        if (!bankQuestions && doc && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const loaded = root.SimBank.load(doc);
                bankQuestions = loaded && Array.isArray(loaded.questions) ? loaded.questions : [];
            }
            catch (_err) {
                bankQuestions = [];
            }
        }
        if (!bankQuestions) {
            bankQuestions = [];
        }
        const policy = opts.policy || (activeContext ? activeContext.policy : loadPolicy(doc, { bankQuestions: bankQuestions, responseTypes: rt }).policy);
        const hist = readAttemptHistory(store);
        const sessionAnswered = Array.isArray(opts.sessionAnsweredIds) ? opts.sessionAnsweredIds : sessionAnsweredRegistry;
        const pathResult = computePracticePath({
            entryOrRequest: entryOrHandoff,
            bankQuestions: bankQuestions,
            policy: policy,
            coverage: cov,
            responseTypes: rt,
            history: {
                attempted_instance_ids: hist.attempted_instance_ids,
                session_answered_ids: sessionAnswered
            },
            familyMetadata: opts.familyMetadata || null,
            doc: doc,
            extraInstances: opts.extraInstances || null
        });
        activeRunner = createRunner(pathResult, {
            doc: doc,
            store: store,
            coverage: cov,
            bankQuestions: bankQuestions,
            gradingContext: opts.gradingContext || null,
            day: opts.day,
            mode: opts.mode || 'practice',
            sessionAnsweredIds: sessionAnswered
        });
        return activeRunner;
    }
    function init(doc, options) {
        doc = doc || root.document;
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const cov = opts.coverage || root.SimCoverage && typeof root.SimCoverage.load === 'function'
            ? (opts.coverage || root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS))
            : readIsland(doc, 'sim-coverage');
        let bankQuestions = opts.bank && Array.isArray(opts.bank.questions)
            ? opts.bank.questions
            : [];
        if (bankQuestions.length === 0 && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const loaded = root.SimBank.load(doc);
                bankQuestions = loaded && Array.isArray(loaded.questions) ? loaded.questions : [];
            }
            catch (_err) {
                bankQuestions = [];
            }
        }
        const rt = readIsland(doc, 'sim-response-types');
        const loadedPol = opts.policy
            ? { policy: sortedValue(opts.policy), digest: digestValue(opts.policy) }
            : loadPolicy(doc, { bankQuestions: bankQuestions, responseTypes: rt });
        const store = opts.store || (root.SimStore ? root.SimStore.createStore({ optIn: false, doc: doc }) : null);
        const termsMap = loadTermsMap(doc);
        activeContext = {
            doc: doc,
            store: store,
            coverage: cov,
            bankQuestions: bankQuestions,
            policy: loadedPol.policy,
            responseTypes: rt
        };
        const typeSelect = doc.getElementById('prakse-filter-type');
        if (typeSelect && rt && isObject(rt.types)) {
            clearNode(typeSelect);
            const allOpt = makeEl(doc, 'option', null, termText(termsMap, 'practice.filter.type_all', 'Visi atbilžu tipi'));
            allOpt.value = '';
            typeSelect.appendChild(allOpt);
            const keys = Object.keys(rt.types).sort();
            for (let i = 0; i < keys.length; i += 1) {
                const k = keys[i];
                const tEntry = rt.types[k];
                const opt = makeEl(doc, 'option', null, k + (isText(tEntry.name_lv) ? ' — ' + tEntry.name_lv : ''));
                opt.value = k;
                typeSelect.appendChild(opt);
            }
        }
        function readUiFilters() {
            const sel = doc.getElementById('prakse-filter-type');
            const chk = doc.getElementById('prakse-filter-unattempted');
            const rType = sel && isText(sel.value) && sel.value !== '' ? [sel.value] : null;
            const unattempted = Boolean(chk && chk.checked);
            return {
                response_types: rType,
                unattempted_only: unattempted
            };
        }
        renderTopicCards(doc, cov, bankQuestions, loadedPol.policy, termsMap, function (topicNum) {
            try {
                const uiFilters = readUiFilters();
                startPath({
                    entry_source: 'topic_browse',
                    topic: topicNum,
                    filters: {
                        topic: topicNum,
                        response_types: uiFilters.response_types,
                        unattempted_only: uiFilters.unattempted_only
                    }
                });
            }
            catch (err) {
                renderError(doc, err);
            }
        });
        const submitBtn = doc.getElementById('prakse-submit-btn');
        if (submitBtn) {
            submitBtn.addEventListener('click', function () {
                if (!activeRunner) {
                    return;
                }
                const item = activeRunner.currentItem();
                if (!item) {
                    return;
                }
                const host = doc.getElementById('prakse-runner-item-host');
                const fields = host && typeof host.querySelectorAll === 'function'
                    ? host.querySelectorAll('input, select, textarea')
                    : [];
                const firstVal = fields.length > 0 && fields[0].value !== undefined ? String(fields[0].value) : '';
                const payload = {
                    kind: 'raw_text',
                    raw: firstVal,
                    value: firstVal
                };
                if (item.payload && isText(item.payload.unit)) {
                    payload.unit = item.payload.unit;
                }
                try {
                    activeRunner.submitAnswer(payload, { advance: false });
                }
                catch (err) {
                    renderError(doc, err);
                }
            });
        }
        const skipBtn = doc.getElementById('prakse-skip-btn');
        if (skipBtn) {
            skipBtn.addEventListener('click', function () {
                if (activeRunner) {
                    activeRunner.skipCurrent();
                }
            });
        }
        const nextBtn = doc.getElementById('prakse-next-btn');
        if (nextBtn) {
            nextBtn.addEventListener('click', function () {
                if (activeRunner) {
                    activeRunner.nextItem();
                }
            });
        }
        const endBtn = doc.getElementById('prakse-end-btn');
        if (endBtn) {
            endBtn.addEventListener('click', function () {
                if (activeRunner) {
                    activeRunner.endEarly();
                }
            });
        }
        return {
            policy: loadedPol.policy,
            policyDigest: loadedPol.digest,
            startPath: startPath,
            getActiveRunner: function () { return activeRunner; }
        };
    }
    const api = {
        ISLAND_ID: ISLAND_ID,
        SCHEMA_VERSION: SCHEMA_VERSION,
        errors: ERRORS.slice(),
        PracticeError: PracticeError,
        isReviewEligible: isReviewEligible,
        validatePolicy: validatePolicy,
        loadPolicy: loadPolicy,
        readAttemptHistory: readAttemptHistory,
        normalizeEntryRequest: normalizeEntryRequest,
        computePracticePath: computePracticePath,
        resolveModeRegistry: resolveModeRegistry,
        describeHelpContract: describeHelpContract,
        createRunner: createRunner,
        startPath: startPath,
        renderError: renderError,
        init: init,
        canonicalText: canonicalText,
        digestValue: digestValue
    };
    root.SimPractice = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
