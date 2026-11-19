"use strict";
/* N25 — versioned, opt-in local store.
 *
 * Invariants enforced by code:
 *   - Default mode is in-memory only (AGENTS.md compliance): zero localStorage
 *     writes and zero localStorage keys unless the learner explicitly opts in.
 *   - One canonical JSON serialization (sorted keys, UTF-8, SHA-256) matching
 *     the N04/N23 digest discipline.
 *   - Schema version 2 with documented v1 -> v2 migration.
 *   - Newer-version guard: if a stored payload carries schema_version > 2,
 *     this v2 runtime ignores its data with a visible Latvian notice and locks
 *     localStorage writes so an older file never overwrites a newer store.
 *   - Destructive erase requires an explicit two-step confirmation and removes
 *     all schema keys, leaving zero localStorage residue.
 */
(function (root) {
    'use strict';
    const SCHEMA_VERSION = 2;
    const SCHEMA_KEY = 'sim_colloq1_store_v2';
    const LEGACY_V1_KEY = 'sim_colloq1_store_v1';
    const SCHEMA_KEYS = [SCHEMA_KEY];
    const LEGACY_KEYS_CLEANED_ON_ERASE = [LEGACY_V1_KEY, SCHEMA_KEY];
    const STORAGE_KIND = 'sim-colloq1-store';
    const MAX_EVENTS_DEFAULT = 200;
    const EXPORT_FORMAT = 'sim-colloq1-progress-export';
    const EXPORT_FILENAME = 'kimija-kolokvijs1-progress-v2.json';
    const ERRORS = [
        'E_STORE_SCHEMA',
        'E_STORE_WRITE_BLOCKED_NEWER_VERSION',
        'E_STORE_ERASE_CONFIRMATION_REQUIRED',
        'E_STORE_MIGRATION_FAILED'
    ];
    class StoreError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'StoreError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, StoreError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new StoreError(code, message, details);
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
    /**
     * Single runtime HTML-escaping helper for markup-building paths (N35).
     * Preserves UTF-8 Latvian diacritics verbatim while escaping & < > " '.
     */
    function escapeHtml(raw) {
        const text = raw === null || raw === undefined ? '' : String(raw);
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
    /* --------------------------------------------------------- canonical text */
    function numberText(value) {
        if (!isFinite(value)) {
            return fail('E_STORE_SCHEMA', 'Kanoniālajā projektcijā nav atbalstīts skaitlis.', { value: String(value) });
        }
        return String(value);
    }
    function canonicalText(value) {
        if (value === null || value === undefined) {
            return 'null';
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        if (typeof value === 'number') {
            return numberText(value);
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
            const record = value;
            const keys = Object.keys(record).sort();
            const parts = [];
            for (let i = 0; i < keys.length; i += 1) {
                if (record[keys[i]] === undefined) {
                    continue;
                }
                parts.push(JSON.stringify(keys[i]) + ':' + canonicalText(record[keys[i]]));
            }
            return '{' + parts.join(',') + '}';
        }
        return fail('E_STORE_SCHEMA', 'Kanoniālajā projektcijā nav atbalstīta vērtība.', {
            value_type: typeof value
        });
    }
    function sortedValue(value) {
        if (Array.isArray(value)) {
            const items = [];
            for (let i = 0; i < value.length; i += 1) {
                items.push(sortedValue(value[i]));
            }
            return items;
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
    /* N25-DIGEST-BEGIN — compact SHA-256 over UTF-8 matching N17/N23. */
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
    function sha256(text) {
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
    /* N25-DIGEST-END */
    function digestValue(value) {
        return sha256(canonicalText(value));
    }
    function digestOf(record) {
        if (!isObject(record)) {
            return fail('E_STORE_SCHEMA', 'Kopsavilkumu var aprēķināt tikai objektam.', {});
        }
        const stripped = {};
        const keys = Object.keys(record);
        for (let i = 0; i < keys.length; i += 1) {
            if (keys[i] !== 'digest') {
                stripped[keys[i]] = record[keys[i]];
            }
        }
        return digestValue(stripped);
    }
    /* --------------------------------------------------------- default & norm */
    function createEmptyTopics() {
        const out = {};
        for (let t = 1; t <= 7; t += 1) {
            out[String(t)] = {
                practiced_tasks: 0,
                practiced_sessions: 0,
                outcomes_correct_once: [],
                outcomes_first_pass: []
            };
        }
        return out;
    }
    function createDefaultState() {
        return sortedValue({
            schema_version: SCHEMA_VERSION,
            storage_kind: STORAGE_KIND,
            settings: {
                opt_in: false,
                theme: null
            },
            progress: {
                topics: createEmptyTopics(),
                outcomes: {},
                outcomes_correct_once: [],
                outcomes_first_pass: [],
                form_history: []
            },
            remediation_queue: [],
            events: [],
            events_pruned_count: 0
        });
    }
    function boundEvents(events, maxEvents, priorPruned) {
        const valid = [];
        for (let i = 0; i < events.length; i += 1) {
            if (isObject(events[i])) {
                valid.push(sortedValue(copyJson(events[i])));
            }
        }
        if (valid.length <= maxEvents) {
            return { events: valid, pruned_count: priorPruned };
        }
        const overflow = valid.length - maxEvents;
        return {
            events: valid.slice(overflow),
            pruned_count: priorPruned + overflow
        };
    }
    function normalizeFormEntry(entry) {
        return {
            session_id: isText(entry.session_id) ? entry.session_id : '',
            form_id: isText(entry.form_id) ? entry.form_id : '',
            auto_points: Number(entry.auto_points !== undefined ? entry.auto_points : (entry.auto_score || 0)),
            auto_max_points: Number(entry.auto_max_points !== undefined ? entry.auto_max_points : (entry.auto_max || 0)),
            pending_external_points: Number(entry.pending_external_points !== undefined
                ? entry.pending_external_points
                : (entry.pending_points || 0)),
            pending_max_points: Number(entry.pending_max_points !== undefined ? entry.pending_max_points : (entry.pending_max || 0)),
            pending_count: Number(entry.pending_count || 0),
            elapsed_ms: Number(entry.elapsed_ms || 0),
            unblended: true,
            graded_digest: isText(entry.graded_digest) ? entry.graded_digest : ''
        };
    }
    function uniquePreservingOrder(items) {
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
        return out;
    }
    function normalizeRemediationItem(raw, idx) {
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
        const mc = isObject(raw.method_card) && isText(raw.method_card.card_id) && isText(raw.method_card.step_id)
            ? { card_id: raw.method_card.card_id, step_id: raw.method_card.step_id }
            : null;
        const sigId = isText(raw.signature_id) && raw.signature_id !== '' ? raw.signature_id : null;
        const sigIds = Array.isArray(raw.signature_ids)
            ? uniqueSorted(raw.signature_ids)
            : (sigId ? [sigId] : []);
        const gradedDigest = isText(raw.graded_digest) ? raw.graded_digest : '';
        const gradedDigests = Array.isArray(raw.graded_digests)
            ? uniquePreservingOrder(raw.graded_digests)
            : (gradedDigest ? [gradedDigest] : []);
        const attemptedIds = Array.isArray(raw.attempted_instance_ids)
            ? uniquePreservingOrder(raw.attempted_instance_ids)
            : (instanceId ? [instanceId] : []);
        const attemptedVariants = Array.isArray(raw.attempted_variant_ids)
            ? uniquePreservingOrder(raw.attempted_variant_ids)
            : [];
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
            miss_count: typeof raw.miss_count === 'number' && isFinite(raw.miss_count) && raw.miss_count >= 1
                ? Math.floor(raw.miss_count)
                : 1,
            retry_count: typeof raw.retry_count === 'number' && isFinite(raw.retry_count) && raw.retry_count >= 0
                ? Math.floor(raw.retry_count)
                : 0,
            attempted_instance_ids: attemptedIds,
            attempted_variant_ids: attemptedVariants,
            last_retry_instance_id: isText(raw.last_retry_instance_id) && raw.last_retry_instance_id !== ''
                ? raw.last_retry_instance_id
                : null,
            last_retry_variant_id: isText(raw.last_retry_variant_id) && raw.last_retry_variant_id !== ''
                ? raw.last_retry_variant_id
                : null,
            last_retry_verdict: lastVerdict,
            last_retry_digest: isText(raw.last_retry_digest) && raw.last_retry_digest !== ''
                ? raw.last_retry_digest
                : null,
            resolved_reason: isText(raw.resolved_reason) && raw.resolved_reason !== '' ? raw.resolved_reason : null,
            resolved_reason_lv: isText(raw.resolved_reason_lv) && raw.resolved_reason_lv !== '' ? raw.resolved_reason_lv : null,
            opened_seq: typeof raw.opened_seq === 'number' && isFinite(raw.opened_seq) ? raw.opened_seq : idx + 1,
            retried_seq: typeof raw.retried_seq === 'number' && isFinite(raw.retried_seq) ? raw.retried_seq : null,
            resolved_seq: typeof raw.resolved_seq === 'number' && isFinite(raw.resolved_seq) ? raw.resolved_seq : null
        };
    }
    function normalizeV2(raw, maxEvents) {
        const def = createDefaultState();
        const rawSettings = isObject(raw.settings) ? raw.settings : {};
        const rawProgress = isObject(raw.progress) ? raw.progress : {};
        const rawTopics = isObject(rawProgress.topics) ? rawProgress.topics : {};
        const topics = createEmptyTopics();
        for (let t = 1; t <= 7; t += 1) {
            const k = String(t);
            const src = isObject(rawTopics[k]) ? rawTopics[k] : {};
            topics[k] = {
                practiced_tasks: typeof src.practiced_tasks === 'number' && isFinite(src.practiced_tasks) ? src.practiced_tasks : 0,
                practiced_sessions: typeof src.practiced_sessions === 'number' && isFinite(src.practiced_sessions) ? src.practiced_sessions : 0,
                outcomes_correct_once: Array.isArray(src.outcomes_correct_once) ? uniqueSorted(src.outcomes_correct_once) : [],
                outcomes_first_pass: Array.isArray(src.outcomes_first_pass) ? uniqueSorted(src.outcomes_first_pass) : []
            };
        }
        const rawOutcomes = isObject(rawProgress.outcomes) ? rawProgress.outcomes : {};
        const outcomes = {};
        const outcomeKeys = Object.keys(rawOutcomes).sort();
        for (let i = 0; i < outcomeKeys.length; i += 1) {
            const oid = outcomeKeys[i];
            const st = rawOutcomes[oid];
            if (!isObject(st)) {
                continue;
            }
            outcomes[oid] = {
                attempts: typeof st.attempts === 'number' && isFinite(st.attempts) ? st.attempts : 0,
                first_attempt_correct: typeof st.first_attempt_correct === 'boolean' ? st.first_attempt_correct : null,
                correct_count: typeof st.correct_count === 'number' && isFinite(st.correct_count) ? st.correct_count : 0
            };
        }
        const rawHistory = Array.isArray(rawProgress.form_history) ? rawProgress.form_history : [];
        const formHistory = [];
        for (let i = 0; i < rawHistory.length; i += 1) {
            if (isObject(rawHistory[i])) {
                formHistory.push(normalizeFormEntry(rawHistory[i]));
            }
        }
        const rawRem = Array.isArray(raw.remediation_queue) ? raw.remediation_queue : [];
        const remQueue = [];
        for (let i = 0; i < rawRem.length; i += 1) {
            if (isObject(rawRem[i])) {
                remQueue.push(normalizeRemediationItem(rawRem[i], i));
            }
        }
        const rawEvents = Array.isArray(raw.events) ? raw.events : [];
        const priorPruned = typeof raw.events_pruned_count === 'number' && isFinite(raw.events_pruned_count)
            ? raw.events_pruned_count
            : 0;
        const bounded = boundEvents(rawEvents, maxEvents, priorPruned);
        const theme = rawSettings.theme === 'light' || rawSettings.theme === 'dark' ? rawSettings.theme : null;
        const out = {
            schema_version: SCHEMA_VERSION,
            storage_kind: STORAGE_KIND,
            settings: {
                opt_in: Boolean(rawSettings.opt_in),
                theme: theme
            },
            progress: {
                topics: topics,
                outcomes: outcomes,
                outcomes_correct_once: Array.isArray(rawProgress.outcomes_correct_once)
                    ? uniqueSorted(rawProgress.outcomes_correct_once)
                    : def.progress.outcomes_correct_once,
                outcomes_first_pass: Array.isArray(rawProgress.outcomes_first_pass)
                    ? uniqueSorted(rawProgress.outcomes_first_pass)
                    : def.progress.outcomes_first_pass,
                form_history: formHistory
            },
            remediation_queue: remQueue,
            events: bounded.events,
            events_pruned_count: bounded.pruned_count
        };
        if (isObject(raw.mastery)) {
            out.mastery = copyJson(raw.mastery);
        }
        if (isObject(raw.self_assessments)) {
            out.self_assessments = copyJson(raw.self_assessments);
        }
        if (isObject(raw.practice_history)) {
            out.practice_history = {
                attempted_instance_ids: Array.isArray(raw.practice_history.attempted_instance_ids)
                    ? uniqueSorted(raw.practice_history.attempted_instance_ids)
                    : [],
                skipped_instance_ids: Array.isArray(raw.practice_history.skipped_instance_ids)
                    ? uniqueSorted(raw.practice_history.skipped_instance_ids)
                    : []
            };
        }
        return sortedValue(out);
    }
    /* -------------------------------------------------------------- migration */
    function migrateV1ToV2(raw, maxEvents) {
        if (!isObject(raw) || raw.schema_version !== 1) {
            return fail('E_STORE_MIGRATION_FAILED', 'v1->v2 migrācijai nepieciešams objekts ar schema_version: 1.', {
                schema_version: isObject(raw) ? raw.schema_version : null
            });
        }
        const cap = typeof maxEvents === 'number' && maxEvents > 0 ? maxEvents : MAX_EVENTS_DEFAULT;
        const rawSettings = isObject(raw.settings) ? raw.settings : {};
        const optIn = Boolean(rawSettings.opt_in !== undefined ? rawSettings.opt_in : raw.opt_in);
        const themeRaw = rawSettings.theme !== undefined ? rawSettings.theme : raw.theme;
        const theme = themeRaw === 'light' || themeRaw === 'dark' ? themeRaw : null;
        const correctOutcomes = uniqueSorted(Array.isArray(raw.correct_outcomes)
            ? raw.correct_outcomes
            : (isObject(raw.progress) && Array.isArray(raw.progress.outcomes_correct_once) ? raw.progress.outcomes_correct_once : []));
        const topics = createEmptyTopics();
        const outcomes = {};
        for (let i = 0; i < correctOutcomes.length; i += 1) {
            const oid = correctOutcomes[i];
            outcomes[oid] = { attempts: 1, first_attempt_correct: true, correct_count: 1 };
            const m = /^P([1-7])-/.exec(oid);
            if (m) {
                topics[m[1]].outcomes_correct_once.push(oid);
                topics[m[1]].outcomes_first_pass.push(oid);
            }
        }
        if (Array.isArray(raw.practiced_topics)) {
            for (let i = 0; i < raw.practiced_topics.length; i += 1) {
                const tk = String(raw.practiced_topics[i]);
                if (has(topics, tk)) {
                    topics[tk].practiced_sessions = Math.max(1, topics[tk].practiced_sessions);
                    topics[tk].practiced_tasks = Math.max(1, topics[tk].practiced_tasks);
                }
            }
        }
        for (let t = 1; t <= 7; t += 1) {
            const k = String(t);
            topics[k].outcomes_correct_once.sort();
            topics[k].outcomes_first_pass.sort();
        }
        const formsRaw = Array.isArray(raw.forms)
            ? raw.forms
            : (isObject(raw.progress) && Array.isArray(raw.progress.form_history) ? raw.progress.form_history : []);
        const formHistory = [];
        for (let i = 0; i < formsRaw.length; i += 1) {
            if (isObject(formsRaw[i])) {
                formHistory.push(normalizeFormEntry(formsRaw[i]));
            }
        }
        const remRaw = Array.isArray(raw.remediation_queue)
            ? raw.remediation_queue
            : (Array.isArray(raw.remediation) ? raw.remediation : []);
        const remQueue = [];
        for (let i = 0; i < remRaw.length; i += 1) {
            if (isObject(remRaw[i])) {
                remQueue.push(normalizeRemediationItem(remRaw[i], i));
            }
        }
        const bounded = boundEvents(Array.isArray(raw.events) ? raw.events : [], cap, 0);
        const state = sortedValue({
            schema_version: SCHEMA_VERSION,
            storage_kind: STORAGE_KIND,
            settings: { opt_in: optIn, theme: theme },
            progress: {
                topics: topics,
                outcomes: outcomes,
                outcomes_correct_once: correctOutcomes,
                outcomes_first_pass: correctOutcomes.slice(),
                form_history: formHistory
            },
            remediation_queue: remQueue,
            events: bounded.events,
            events_pruned_count: bounded.pruned_count
        });
        return { state: state, migrated: true, from_version: 1 };
    }
    /* --------------------------------------------------------------- store */
    function readIslandCopy(doc) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return {};
        }
        const node = doc.getElementById('sim-analytics');
        if (!node || !isText(node.textContent) || node.textContent === '') {
            return {};
        }
        try {
            const parsed = JSON.parse(node.textContent);
            return isObject(parsed) && isObject(parsed.copy_lv) ? parsed.copy_lv : {};
        }
        catch (_err) {
            return {};
        }
    }
    function formatCopy(template, vars) {
        let out = template;
        const keys = Object.keys(vars);
        for (let i = 0; i < keys.length; i += 1) {
            out = out.split('{' + keys[i] + '}').join(String(vars[keys[i]]));
        }
        return out;
    }
    function hasStorageApi(candidate) {
        return Boolean(candidate &&
            typeof candidate.getItem === 'function' &&
            typeof candidate.setItem === 'function' &&
            typeof candidate.removeItem === 'function');
    }
    function createStore(options) {
        const opts = options || {};
        const maxEvents = typeof opts.maxEvents === 'number' && opts.maxEvents > 0
            ? Math.floor(opts.maxEvents)
            : MAX_EVENTS_DEFAULT;
        const copy = readIslandCopy(opts.doc);
        let state = createDefaultState();
        let optIn = Boolean(opts.optIn);
        let backing = hasStorageApi(opts.storage) ? opts.storage : null;
        let degraded = false;
        let newerVersionLocked = false;
        let erasePending = false;
        let migratedFromV1 = false;
        let notice = null;
        if (optIn && !backing) {
            degraded = true;
            optIn = false;
            notice = {
                code: 'STORAGE_UNAVAILABLE',
                message_lv: copy.storage_degraded_notice || 'Pārlūka localStorage nav pieejama; sesija droši turpina darbu operatīvajā atmiņā.'
            };
        }
        function loadFromBacking() {
            if (!backing) {
                return;
            }
            let rawText = null;
            try {
                rawText = backing.getItem(SCHEMA_KEY);
            }
            catch (_err) {
                degraded = true;
                backing = null;
                optIn = false;
                notice = {
                    code: 'STORAGE_READ_ERROR',
                    message_lv: copy.storage_degraded_notice || 'Pārlūka localStorage nav pieejama; sesija droši turpina darbu operatīvajā atmiņā.'
                };
                return;
            }
            if (rawText === null || rawText === undefined || rawText === '') {
                return;
            }
            let parsed;
            try {
                parsed = JSON.parse(String(rawText));
            }
            catch (_err) {
                newerVersionLocked = true;
                optIn = false;
                state = createDefaultState();
                notice = {
                    code: 'CORRUPT_STORE_IGNORED',
                    message_lv: copy.corrupt_store_notice || 'Saglabātie lokālie dati nav nolasāmi; tie tiek ignorēti bez pārrakstīšanas, un sesija darbojas operatīvajā atmiņā.'
                };
                return;
            }
            if (!isObject(parsed) || typeof parsed.schema_version !== 'number') {
                newerVersionLocked = true;
                optIn = false;
                state = createDefaultState();
                notice = {
                    code: 'CORRUPT_STORE_IGNORED',
                    message_lv: copy.corrupt_store_notice || 'Saglabātie lokālie dati nav nolasāmi; tie tiek ignorēti bez pārrakstīšanas, un sesija darbojas operatīvajā atmiņā.'
                };
                return;
            }
            if (parsed.schema_version > SCHEMA_VERSION) {
                newerVersionLocked = true;
                optIn = false;
                state = createDefaultState();
                notice = {
                    code: 'NEWER_VERSION_IGNORED',
                    found_version: parsed.schema_version,
                    supported_version: SCHEMA_VERSION,
                    message_lv: formatCopy(copy.newer_version_notice || 'Atrasts jaunākas versijas krātuves ieraksts (schema_version {found} > {supported}). Esošie dati netiek pārrakstīti un tiek ignorēti; sesija darbojas operatīvajā atmiņā.', { found: parsed.schema_version, supported: SCHEMA_VERSION })
                };
                return;
            }
            if (parsed.schema_version === 1) {
                const mig = migrateV1ToV2(parsed, maxEvents);
                state = mig.state;
                migratedFromV1 = true;
                if (opts.optIn || state.settings.opt_in) {
                    optIn = true;
                    state.settings.opt_in = true;
                }
                notice = {
                    code: 'MIGRATED_V1_TO_V2',
                    found_version: 1,
                    supported_version: SCHEMA_VERSION,
                    message_lv: copy.migrated_v1_notice || 'Vecākās v1 krātuves dati tika droši pārcelti uz v2 formātu.'
                };
                if (optIn) {
                    persist();
                }
                return;
            }
            if (parsed.schema_version === SCHEMA_VERSION) {
                state = normalizeV2(parsed, maxEvents);
                if (opts.optIn || state.settings.opt_in) {
                    optIn = true;
                    state.settings.opt_in = true;
                }
                return;
            }
            newerVersionLocked = true;
            optIn = false;
            state = createDefaultState();
            notice = {
                code: 'CORRUPT_STORE_IGNORED',
                message_lv: copy.corrupt_store_notice || 'Saglabātie lokālie dati nav nolasāmi; tie tiek ignorēti bez pārrakstīšanas, un sesija darbojas operatīvajā atmiņā.'
            };
        }
        function persist() {
            if (!optIn || !backing || newerVersionLocked) {
                return false;
            }
            try {
                backing.setItem(SCHEMA_KEY, canonicalText(state));
                return true;
            }
            catch (_err) {
                degraded = true;
                backing = null;
                optIn = false;
                state.settings.opt_in = false;
                notice = {
                    code: 'STORAGE_WRITE_ERROR',
                    message_lv: copy.storage_degraded_notice || 'Pārlūka localStorage nav pieejama; sesija droši turpina darbu operatīvajā atmiņā.'
                };
                return false;
            }
        }
        if ((optIn || opts.probeExisting) && backing) {
            loadFromBacking();
        }
        function getState() {
            return sortedValue(copyJson(state));
        }
        function getDigest() {
            return digestValue(state);
        }
        function setOptIn(enabled, storageOverride) {
            if (storageOverride !== undefined) {
                backing = hasStorageApi(storageOverride) ? storageOverride : null;
            }
            if (enabled) {
                if (newerVersionLocked) {
                    return fail('E_STORE_WRITE_BLOCKED_NEWER_VERSION', 'Jaunākas versijas krātuve ir aizsargāta pret pārrakstīšanu; vispirms izdzēsiet to divos soļos.', { found_version: notice ? notice.found_version : null });
                }
                if (!backing) {
                    degraded = true;
                    optIn = false;
                    state.settings.opt_in = false;
                    notice = {
                        code: 'STORAGE_UNAVAILABLE',
                        message_lv: copy.storage_degraded_notice || 'Pārlūka localStorage nav pieejama; sesija droši turpina darbu operatīvajā atmiņā.'
                    };
                    return { opt_in: false, mode: 'memory', notice: notice };
                }
                const hadExisting = backing.getItem(SCHEMA_KEY);
                if (hadExisting !== null && hadExisting !== undefined && hadExisting !== '') {
                    const prevOptIn = optIn;
                    optIn = true;
                    loadFromBacking();
                    if (newerVersionLocked) {
                        optIn = prevOptIn;
                        return { opt_in: false, mode: 'memory', notice: notice };
                    }
                }
                optIn = true;
                state.settings.opt_in = true;
                persist();
                if (!notice || notice.code === 'OPT_IN_DISABLED') {
                    notice = {
                        code: 'OPT_IN_ENABLED',
                        message_lv: copy.enabled_state_notice || 'Lokālā saglabāšana pārlūkā (localStorage) ir ieslēgta.'
                    };
                }
                return { opt_in: true, mode: 'localStorage', notice: notice };
            }
            optIn = false;
            state.settings.opt_in = false;
            erasePending = false;
            if (backing && !newerVersionLocked) {
                try {
                    for (let i = 0; i < SCHEMA_KEYS.length; i += 1) {
                        backing.removeItem(SCHEMA_KEYS[i]);
                    }
                }
                catch (_err) {
                    /* ignore */
                }
            }
            notice = {
                code: 'OPT_IN_DISABLED',
                message_lv: copy.disabled_state_notice || 'Pēc noklusējuma dati glabājas tikai operatīvajā atmiņā (bez localStorage).'
            };
            return { opt_in: false, mode: 'memory', notice: notice };
        }
        function update(mutator) {
            const draft = getState();
            mutator(draft);
            draft.settings.opt_in = optIn;
            state = normalizeV2(draft, maxEvents);
            persist();
            return getState();
        }
        function setState(nextState) {
            if (!isObject(nextState) || nextState.schema_version !== SCHEMA_VERSION) {
                return fail('E_STORE_SCHEMA', 'Krātuves stāvoklim jābūt v2 objektam.', {
                    schema_version: isObject(nextState) ? nextState.schema_version : null
                });
            }
            const next = normalizeV2(nextState, maxEvents);
            next.settings.opt_in = optIn;
            state = next;
            persist();
            return getState();
        }
        function setTheme(theme) {
            return update(function (draft) {
                draft.settings.theme = theme === 'light' || theme === 'dark' ? theme : null;
            });
        }
        function exportProgress(exportOptions) {
            const snapshot = getState();
            const storeDigest = digestValue(snapshot);
            const envelope = {
                export_format: EXPORT_FORMAT,
                schema_version: SCHEMA_VERSION,
                filename: EXPORT_FILENAME,
                store_digest: storeDigest,
                store: snapshot
            };
            if (exportOptions && exportOptions.includeSession !== undefined) {
                envelope.optional_session_export = copyJson(exportOptions.includeSession);
            }
            const ordered = sortedValue(envelope);
            const text = canonicalText(ordered);
            return {
                filename: EXPORT_FILENAME,
                store_digest: storeDigest,
                parsed: ordered,
                text: text
            };
        }
        function importProgress(rawText) {
            if (typeof rawText !== 'string' || rawText.trim() === '') {
                return fail('E_STORE_IMPORT_JSON', 'Importa fails ir tukšs vai nav teksts.', {});
            }
            let parsed;
            try {
                parsed = JSON.parse(rawText);
            }
            catch (_err) {
                return fail('E_STORE_IMPORT_JSON', 'Importa fails satur nederīgu JSON sintaksi.', {});
            }
            if (!isObject(parsed) || Array.isArray(parsed)) {
                return fail('E_STORE_IMPORT_SHAPE', 'Importa faila sakne nav JSON objekts.', {});
            }
            if (parsed.export_format !== EXPORT_FORMAT) {
                return fail('E_STORE_IMPORT_SHAPE', 'Neatbilstošs eksporta formāts.', { export_format: parsed.export_format });
            }
            const ver = Number(parsed.schema_version);
            if (!isFinite(ver) || ver > SCHEMA_VERSION || ver < 1) {
                return fail('E_STORE_IMPORT_VERSION', 'Neatbalstīta importa shēmas versija.', { schema_version: parsed.schema_version });
            }
            if (!isObject(parsed.store)) {
                return fail('E_STORE_IMPORT_SHAPE', 'Importa failā trūkst store objekta.', {});
            }
            const candidate = ver === 1 ? migrateV1ToV2(parsed.store, maxEvents).state : normalizeV2(parsed.store, maxEvents);
            const actualDigest = digestValue(candidate);
            if (typeof parsed.store_digest === 'string' && parsed.store_digest !== '' && parsed.store_digest !== actualDigest) {
                return fail('E_STORE_IMPORT_DIGEST', 'Importa faila SHA-256 kontrolsumma nesakrīt.', {
                    expected: parsed.store_digest,
                    actual: actualDigest
                });
            }
            setState(candidate);
            return {
                imported: true,
                store_digest: getDigest(),
                state: getState()
            };
        }
        function requestErase() {
            erasePending = true;
            return {
                pending: true,
                prompt_lv: copy.erase_confirm_prompt || 'Vai tiešām neatgriezeniski dzēst visus lokāli saglabātos progresa datus?'
            };
        }
        function cancelErase() {
            erasePending = false;
            return { pending: false };
        }
        function confirmErase() {
            if (!erasePending) {
                return fail('E_STORE_ERASE_CONFIRMATION_REQUIRED', 'Dzēšanai nepieciešams divsoļu apstiprinājums.', {});
            }
            const removedKeys = [];
            const keysToClean = migratedFromV1 ? LEGACY_KEYS_CLEANED_ON_ERASE : SCHEMA_KEYS;
            if (backing) {
                for (let i = 0; i < keysToClean.length; i += 1) {
                    const key = keysToClean[i];
                    try {
                        backing.removeItem(key);
                        removedKeys.push(key);
                    }
                    catch (_err) {
                        /* ignore */
                    }
                }
            }
            erasePending = false;
            migratedFromV1 = false;
            optIn = false;
            newerVersionLocked = false;
            degraded = false;
            state = createDefaultState();
            notice = {
                code: 'ERASE_COMPLETE',
                message_lv: copy.erase_done_notice || 'Visi lokālie progresa dati ir dzēsti, un sesija atgriezta operatīvajā atmiņā.'
            };
            return {
                erased: true,
                store_digest: getDigest(),
                removed_keys: removedKeys
            };
        }
        function erase(confirmed) {
            if (confirmed !== true) {
                return fail('E_STORE_ERASE_CONFIRMATION_REQUIRED', 'Dzēšanai nepieciešams divsoļu apstiprinājums.', {});
            }
            erasePending = true;
            return confirmErase();
        }
        return {
            SCHEMA_VERSION: SCHEMA_VERSION,
            SCHEMA_KEY: SCHEMA_KEY,
            SCHEMA_KEYS: SCHEMA_KEYS.slice(),
            MAX_EVENTS: maxEvents,
            getMode: function () { return optIn && backing && !newerVersionLocked ? 'localStorage' : 'memory'; },
            isOptedIn: function () { return optIn; },
            isDegraded: function () { return degraded; },
            isNewerVersionLocked: function () { return newerVersionLocked; },
            isErasePending: function () { return erasePending; },
            getNotice: function () { return notice ? copyJson(notice) : null; },
            getState: getState,
            getDigest: getDigest,
            setOptIn: setOptIn,
            update: update,
            setState: setState,
            setTheme: setTheme,
            exportProgress: exportProgress,
            importProgress: importProgress,
            requestErase: requestErase,
            cancelErase: cancelErase,
            confirmErase: confirmErase,
            erase: erase
        };
    }
    const api = {
        SCHEMA_VERSION: SCHEMA_VERSION,
        SCHEMA_KEY: SCHEMA_KEY,
        SCHEMA_KEYS: SCHEMA_KEYS.slice(),
        LEGACY_V1_KEY: LEGACY_V1_KEY,
        MAX_EVENTS_DEFAULT: MAX_EVENTS_DEFAULT,
        EXPORT_FILENAME: EXPORT_FILENAME,
        errors: ERRORS.slice(),
        StoreError: StoreError,
        escapeHtml: escapeHtml,
        canonicalText: canonicalText,
        digestValue: digestValue,
        digestOf: digestOf,
        createDefaultState: createDefaultState,
        migrateV1ToV2: migrateV1ToV2,
        createStore: createStore
    };
    root.SimStore = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
