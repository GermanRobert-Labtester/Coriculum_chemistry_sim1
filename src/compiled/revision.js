"use strict";
/* N29 — Unified revision view (#atskats) and F07 criterion self-assessment card.
 *
 * Epistemic & architectural boundaries:
 *   - Every policy threshold, rating label, and card rule is PROPOSED training
 *     policy over #sim-revision-policy (official_counterpart_status: UNDETERMINED).
 *   - Strict evidence separation: self-assessment ratings (F07) persist under
 *     sim_colloq1_store_v2.self_assessments and NEVER feed SimMastery.reduce or
 *     modify graded totals.
 *   - Single-sourced criterion labels: resolved via SimFeedback.criterionLabel /
 *     #sim-terms (feedback.criterion.<criterion_id>) — names only, zero key
 *     content, zero expected answers, zero rubric point internals.
 *   - Optional note is stored verbatim up to note_max_length (500) and is
 *     never parsed, trimmed, or keyword-matched.
 *   - Zero wall-clock calls (Date.now / performance.now), zero network calls,
 *     and zero F10 chart/streak/gamification exports.
 */
(function (root) {
    'use strict';
    const ISLAND_ID = 'sim-revision-policy';
    const SCHEMA_VERSION = 1;
    const NOTE_MAX_LENGTH = 500;
    const VALID_RATINGS = ['confident', 'with_effort', 'not_yet'];
    const VERBATIM_SELF_ASSESSMENT_LABEL_LV = 'Izglītojamā paša novērtējums (F07, PROPOSED) — šis nav automātiskais vērtējums un neietekmē apguves stāvokli.';
    const VERBATIM_NOTE_NEVER_ANALYZED_LV = 'Brīvā teksta piezīme tiek saglabāta burtiski bez analīzes, atslēgvārdu meklēšanas vai automātiskas vērtēšanas.';
    const ERRORS = [
        'E_REVISION_POLICY_INVALID',
        'E_REVISION_DANGLING_ANCHOR',
        'E_REVISION_DANGLING_LINK',
        'E_REVISION_UNKNOWN_OUTCOME',
        'E_REVISION_OUTCOME_UNAVAILABLE',
        'E_REVISION_INVALID_RATING',
        'E_REVISION_NOTE_TOO_LONG',
        'E_REVISION_CARD_ERROR'
    ];
    class RevisionError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'RevisionError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, RevisionError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new RevisionError(code, message, details);
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
                return fail('E_REVISION_CARD_ERROR', 'Kanoniālajā projektcijā nav atbalstīts bezgalīgs skaitlis.', {});
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
    /* ---------------------------------------------------------------- policy */
    function validatePolicy(raw) {
        const errors = [];
        if (!isObject(raw)) {
            return { valid: false, errors: ['Revision policy must be a JSON object'] };
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
        if (!isText(raw.honesty_note_lv) || raw.honesty_note_lv.trim() === '') {
            errors.push('honesty_note_lv must be non-empty');
        }
        const sa = raw.self_assessment;
        if (!isObject(sa)) {
            errors.push('self_assessment must be an object');
        }
        else {
            if (sa.feature_id !== 'F07') {
                errors.push('self_assessment.feature_id must be "F07"');
            }
            if (sa.excluded_from_mastery !== true) {
                errors.push('self_assessment.excluded_from_mastery must be true');
            }
            if (sa.excluded_from_scoring !== true) {
                errors.push('self_assessment.excluded_from_scoring must be true');
            }
            if (sa.key_free_criteria_only !== true) {
                errors.push('self_assessment.key_free_criteria_only must be true');
            }
            if (typeof sa.note_max_length !== 'number' || !isFinite(sa.note_max_length) || sa.note_max_length <= 0) {
                errors.push('self_assessment.note_max_length must be a positive integer');
            }
            if (sa.verbatim_self_assessment_label_lv !== VERBATIM_SELF_ASSESSMENT_LABEL_LV) {
                errors.push('self_assessment.verbatim_self_assessment_label_lv mismatch');
            }
            if (sa.verbatim_note_never_analyzed_lv !== VERBATIM_NOTE_NEVER_ANALYZED_LV) {
                errors.push('self_assessment.verbatim_note_never_analyzed_lv mismatch');
            }
            if (!Array.isArray(sa.ratings) || sa.ratings.length !== 3) {
                errors.push('self_assessment.ratings must list 3 rating states');
            }
            else {
                const ids = sa.ratings.map(function (r) { return isObject(r) && isText(r.id) ? r.id : ''; });
                for (let i = 0; i < VALID_RATINGS.length; i += 1) {
                    if (ids.indexOf(VALID_RATINGS[i]) < 0) {
                        errors.push('self_assessment.ratings missing state "' + VALID_RATINGS[i] + '"');
                    }
                }
            }
        }
        return { valid: errors.length === 0, errors: errors };
    }
    function loadPolicy(source) {
        let parsed = null;
        if (isObject(source) && source.island_id === ISLAND_ID) {
            parsed = copyJson(source);
        }
        else {
            const doc = source && typeof source.getElementById === 'function'
                ? source
                : root.document;
            const node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(ISLAND_ID) : null;
            const raw = node && (node.textContent !== undefined ? node.textContent : node.innerText);
            if (!isText(raw) || raw.trim() === '') {
                return fail('E_REVISION_POLICY_INVALID', 'Trūkst #' + ISLAND_ID + ' datu salas.', { island_id: ISLAND_ID });
            }
            try {
                parsed = JSON.parse(raw);
            }
            catch (err) {
                return fail('E_REVISION_POLICY_INVALID', 'Salas #' + ISLAND_ID + ' JSON nav derīgs.', {
                    cause: err instanceof Error ? err.message : String(err)
                });
            }
        }
        const v = validatePolicy(parsed);
        if (!v.valid) {
            return fail('E_REVISION_POLICY_INVALID', 'Nederīga pārskata politika: ' + v.errors.join('; '), {
                errors: v.errors
            });
        }
        const clean = sortedValue(parsed);
        return { policy: clean, digest: digestValue(clean) };
    }
    /* --------------------------------------------------- single-source terms */
    function loadTermsMap(source) {
        const fb = root.SimFeedback;
        if (fb && typeof fb.loadTermsMap === 'function') {
            try {
                return fb.loadTermsMap(source);
            }
            catch (_err) {
                /* fallback to direct doc/#sim-terms read when SimFeedback throws on non-doc */
            }
        }
        if (isObject(source) && !has(source, 'getElementById')) {
            if (isObject(source.byKey)) {
                const out = {};
                const keys = Object.keys(source.byKey);
                for (let i = 0; i < keys.length; i += 1) {
                    const entry = source.byKey[keys[i]];
                    if (isObject(entry) && isText(entry.primary_lv || entry.text_lv)) {
                        out[keys[i]] = String(entry.primary_lv || entry.text_lv);
                    }
                }
                return out;
            }
            const out = {};
            const keys = Object.keys(source);
            for (let i = 0; i < keys.length; i += 1) {
                if (isText(source[keys[i]])) {
                    out[keys[i]] = String(source[keys[i]]);
                }
            }
            return out;
        }
        const doc = source && typeof source.getElementById === 'function'
            ? source
            : root.document;
        const st = root.SimTerms;
        if (doc && st && typeof st.load === 'function') {
            try {
                const isl = st.load(doc);
                if (isl && isObject(isl.byKey)) {
                    const out = {};
                    const keys = Object.keys(isl.byKey);
                    for (let i = 0; i < keys.length; i += 1) {
                        const entry = isl.byKey[keys[i]];
                        if (isObject(entry) && isText(entry.primary_lv || entry.text_lv)) {
                            out[keys[i]] = String(entry.primary_lv || entry.text_lv);
                        }
                    }
                    return out;
                }
            }
            catch (_err) {
                /* fallback below */
            }
        }
        if (doc && typeof doc.getElementById === 'function') {
            const node = doc.getElementById('sim-terms');
            const raw = node && (node.textContent !== undefined ? node.textContent : node.innerText);
            if (isText(raw) && raw.trim() !== '') {
                try {
                    const parsed = JSON.parse(raw);
                    const list = isObject(parsed) && Array.isArray(parsed.terms) ? parsed.terms : [];
                    const out = {};
                    for (let i = 0; i < list.length; i += 1) {
                        if (isObject(list[i]) && isText(list[i].key) && isText(list[i].text_lv)) {
                            out[list[i].key] = list[i].text_lv;
                        }
                    }
                    return out;
                }
                catch (_err) {
                    return {};
                }
            }
        }
        return {};
    }
    function resolveCriterionLabel(criterionId, termsMap) {
        const fb = root.SimFeedback;
        if (fb && typeof fb.criterionLabel === 'function') {
            return fb.criterionLabel(criterionId, termsMap);
        }
        const key = 'feedback.criterion.' + criterionId;
        if (isText(termsMap[key]) && termsMap[key] !== '') {
            return termsMap[key];
        }
        return criterionId;
    }
    function termText(termsMap, key, fallbackText) {
        if (isText(termsMap[key]) && termsMap[key] !== '') {
            return termsMap[key];
        }
        if (isText(fallbackText)) {
            return fallbackText;
        }
        return fail('E_REVISION_POLICY_INVALID', 'Trūkst terminu atslēgas "' + key + '" (#sim-terms).', { key: key });
    }
    function formatCopy(template, vars) {
        let out = template;
        const keys = Object.keys(vars);
        for (let i = 0; i < keys.length; i += 1) {
            out = out.split('{' + keys[i] + '}').join(String(vars[keys[i]]));
        }
        return out;
    }
    /* --------------------------------------------------- island & data loads */
    function readJsonIsland(doc, id) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const node = doc.getElementById(id);
        const raw = node && (node.textContent !== undefined ? node.textContent : node.innerText);
        if (!isText(raw) || raw.trim() === '') {
            return null;
        }
        try {
            return JSON.parse(raw);
        }
        catch (_err) {
            return null;
        }
    }
    function loadCoverage(doc, explicit) {
        if (isObject(explicit) && Array.isArray(explicit.outcomes)) {
            return explicit;
        }
        if (root.SimCoverage && typeof root.SimCoverage.load === 'function') {
            return root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
        }
        const cov = readJsonIsland(doc, 'sim-coverage');
        if (!isObject(cov) || !Array.isArray(cov.outcomes)) {
            return fail('E_REVISION_POLICY_INVALID', 'Nav seguma salas (#sim-coverage).', { island_id: 'sim-coverage' });
        }
        return cov;
    }
    function loadBankQuestions(doc, explicit) {
        if (Array.isArray(explicit)) {
            return explicit;
        }
        if (root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const b = root.SimBank.load(doc);
                if (b && Array.isArray(b.questions)) {
                    return b.questions;
                }
            }
            catch (_err) {
                /* fallback */
            }
        }
        const raw = readJsonIsland(doc, 'sim-bank');
        return isObject(raw) && Array.isArray(raw.questions) ? raw.questions : [];
    }
    function loadSummariesData(doc, explicit) {
        if (isObject(explicit)) {
            return explicit;
        }
        if (isObject(root.CONCEPT_DRAWER_DATA)) {
            return root.CONCEPT_DRAWER_DATA;
        }
        const raw = readJsonIsland(doc, 'sim-concept-summaries');
        return isObject(raw) ? raw : {};
    }
    function loadAnchorRegistry(doc, explicit) {
        if (isObject(explicit)) {
            return explicit;
        }
        if (isObject(root.ANCHOR_REGISTRY)) {
            return root.ANCHOR_REGISTRY;
        }
        const raw = readJsonIsland(doc, 'sim-anchor-registry');
        return isObject(raw) ? raw : {};
    }
    function loadChainsData(doc, explicit) {
        if (isObject(explicit)) {
            return explicit;
        }
        const raw = readJsonIsland(doc, 'sim-chains');
        return isObject(raw) ? raw : {};
    }
    /* --------------------------------------------------- affordance validation */
    function buildSummaryMap(summariesData) {
        const out = {};
        const list = Array.isArray(summariesData.concepts) ? summariesData.concepts : [];
        for (let i = 0; i < list.length; i += 1) {
            const c = list[i];
            if (isObject(c) && isText(c.id)) {
                out[c.id] = c;
            }
        }
        return out;
    }
    function buildAnchorMap(anchorRegistry) {
        const byAnchorKey = {};
        const byOutcomeId = {};
        const anchors = Array.isArray(anchorRegistry.anchors) ? anchorRegistry.anchors : [];
        for (let i = 0; i < anchors.length; i += 1) {
            const a = anchors[i];
            if (!isObject(a)) {
                continue;
            }
            if (isText(a.anchor)) {
                byAnchorKey[a.anchor] = a;
            }
            if (isText(a.id)) {
                byAnchorKey[a.id] = a;
            }
            if (isText(a.master_path) && isText(a.anchor)) {
                byAnchorKey[a.master_path + '#' + a.anchor] = a;
            }
            if (Array.isArray(a.outcome_ids)) {
                for (let j = 0; j < a.outcome_ids.length; j += 1) {
                    if (isText(a.outcome_ids[j])) {
                        byOutcomeId[a.outcome_ids[j]] = a;
                    }
                }
            }
        }
        const concepts = Array.isArray(anchorRegistry.concepts) ? anchorRegistry.concepts : [];
        for (let i = 0; i < concepts.length; i += 1) {
            const c = concepts[i];
            if (!isObject(c)) {
                continue;
            }
            if (isText(c.concept_id)) {
                byOutcomeId[c.concept_id] = c;
            }
            if (isText(c.master_anchor)) {
                byAnchorKey[c.master_anchor] = c;
                if (isText(c.master_path)) {
                    byAnchorKey[c.master_path + '#' + c.master_anchor] = c;
                }
            }
        }
        return {
            byAnchorKey: byAnchorKey,
            byOutcomeId: byOutcomeId,
            hasRegistry: Object.keys(byAnchorKey).length > 0
        };
    }
    function buildChainSet(chainsData) {
        const ids = {};
        const list = Array.isArray(chainsData.chains) ? chainsData.chains : [];
        for (let i = 0; i < list.length; i += 1) {
            if (isObject(list[i]) && isText(list[i].id)) {
                ids[list[i].id] = true;
            }
        }
        return { ids: ids, hasChains: list.length > 0 };
    }
    function validateOutcomeAffordances(coverage, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const anchorReg = loadAnchorRegistry(doc, opts.anchorRegistry);
        const summariesData = loadSummariesData(doc, opts.conceptSummaries);
        const chainsData = loadChainsData(doc, opts.chains);
        const anchorIndex = buildAnchorMap(anchorReg);
        const summaryMap = buildSummaryMap(summariesData);
        const chainSet = buildChainSet(chainsData);
        const rem = root.SimRemediation;
        const remRegistries = rem && typeof rem.buildRegistries === 'function'
            ? rem.buildRegistries(doc, { coverage: coverage, chains: chainsData, summaries: summariesData })
            : null;
        const outcomes = Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        const resolved = {};
        for (let i = 0; i < outcomes.length; i += 1) {
            const oc = outcomes[i];
            if (!isObject(oc) || !isText(oc.id)) {
                continue;
            }
            const oid = oc.id;
            const anchor = isText(oc.master_anchor) ? oc.master_anchor.trim() : '';
            if (!anchor) {
                return fail('E_REVISION_DANGLING_ANCHOR', 'Mērķim "' + oid + '" trūkst master_anchor.', {
                    outcome_id: oid,
                    anchor: anchor
                });
            }
            if (anchorIndex.hasRegistry) {
                const pathKey = isText(oc.master_path) ? (oc.master_path + '#' + anchor) : anchor;
                const regMatch = anchorIndex.byAnchorKey[pathKey] || anchorIndex.byAnchorKey[anchor];
                if (!regMatch) {
                    return fail('E_REVISION_DANGLING_ANCHOR', 'Mērķa "' + oid + '" enkurs "' + anchor + '" nav atrasts enkuru reģistrā (ANCHOR_REGISTRY).', { outcome_id: oid, anchor: anchor, master_path: oc.master_path || null });
                }
            }
            const sum = summaryMap[oid];
            if (Object.keys(summaryMap).length > 0) {
                if (!sum) {
                    return fail('E_REVISION_DANGLING_ANCHOR', 'Mērķim "' + oid + '" trūkst ieraksta konceptu kopsavilkumos (CONCEPT_DRAWER_DATA).', { outcome_id: oid, anchor: anchor });
                }
                if (isText(sum.master_anchor) && sum.master_anchor !== anchor) {
                    return fail('E_REVISION_DANGLING_ANCHOR', 'Mērķa "' + oid + '" enkurs "' + anchor + '" nesakrīt ar koncepta kopsavilkuma enkuru "' + sum.master_anchor + '".', { outcome_id: oid, anchor: anchor, summary_anchor: sum.master_anchor });
                }
            }
            if (remRegistries && isObject(remRegistries.concept_ids) && !remRegistries.concept_ids[oid]) {
                return fail('E_REVISION_DANGLING_ANCHOR', 'Mērķis "' + oid + '" (enkurs "' + anchor + '") neizšķiras atkārtošanas saišu reģistrā.', { outcome_id: oid, anchor: anchor });
            }
            const chainIdsRaw = sum && Array.isArray(sum.chainIds)
                ? sum.chainIds.filter(isText)
                : (sum && isObject(sum.slots) && isObject(sum.slots.chains) && Array.isArray(sum.slots.chains.chain_ids)
                    ? sum.slots.chains.chain_ids.filter(isText)
                    : []);
            for (let j = 0; j < chainIdsRaw.length; j += 1) {
                const cid = chainIdsRaw[j];
                if (chainSet.hasChains && !chainSet.ids[cid]) {
                    return fail('E_REVISION_DANGLING_LINK', 'Mērķa "' + oid + '" darba piemēra ķēde "' + cid + '" nav atrasta #sim-chains.', { outcome_id: oid, chain_id: cid });
                }
            }
            resolved[oid] = {
                master_anchor: anchor,
                chain_ids: chainIdsRaw
            };
        }
        return resolved;
    }
    /* --------------------------------------------------- criteria resolution */
    function resolveOutcomeCriteria(outcomeId, coverage, bankQuestions, termsSource) {
        const covOutcomes = Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        let outcomeObj = null;
        for (let i = 0; i < covOutcomes.length; i += 1) {
            if (isObject(covOutcomes[i]) && covOutcomes[i].id === outcomeId) {
                outcomeObj = covOutcomes[i];
                break;
            }
        }
        if (!outcomeObj) {
            return fail('E_REVISION_UNKNOWN_OUTCOME', 'Nezināms mācību mērķis "' + outcomeId + '".', {
                outcome_id: outcomeId
            });
        }
        const termsMap = loadTermsMap(termsSource);
        const families = outcomeObj.bindings && Array.isArray(outcomeObj.bindings.practice_families)
            ? outcomeObj.bindings.practice_families.filter(isText)
            : [];
        const seen = {};
        const out = [];
        for (let i = 0; i < bankQuestions.length; i += 1) {
            const q = bankQuestions[i];
            if (!isObject(q)) {
                continue;
            }
            const oids = Array.isArray(q.outcome_ids) ? q.outcome_ids : [];
            if (oids.indexOf(outcomeId) < 0) {
                continue;
            }
            const rubric = Array.isArray(q.rubric) ? q.rubric : [];
            for (let r = 0; r < rubric.length; r += 1) {
                const crit = rubric[r];
                if (!isObject(crit) || !isText(crit.criterion_id) || seen[crit.criterion_id]) {
                    continue;
                }
                seen[crit.criterion_id] = true;
                out.push({
                    criterion_id: crit.criterion_id,
                    label_lv: resolveCriterionLabel(crit.criterion_id, termsMap)
                });
            }
        }
        if (out.length === 0 && families.length > 0) {
            for (let i = 0; i < bankQuestions.length; i += 1) {
                const q = bankQuestions[i];
                if (!isObject(q) || !isText(q.family_id) || families.indexOf(q.family_id) < 0) {
                    continue;
                }
                const rubric = Array.isArray(q.rubric) ? q.rubric : [];
                for (let r = 0; r < rubric.length; r += 1) {
                    const crit = rubric[r];
                    if (!isObject(crit) || !isText(crit.criterion_id) || seen[crit.criterion_id]) {
                        continue;
                    }
                    seen[crit.criterion_id] = true;
                    out.push({
                        criterion_id: crit.criterion_id,
                        label_lv: resolveCriterionLabel(crit.criterion_id, termsMap)
                    });
                }
            }
        }
        /* Contract: names only — never return points, grading, payload, or key values. */
        return out;
    }
    /* --------------------------------------------------- store F07 persistence */
    function isValidRating(value) {
        return value === 'confident' || value === 'with_effort' || value === 'not_yet';
    }
    function normalizeSelfAssessmentMap(raw) {
        if (!isObject(raw)) {
            return {};
        }
        const out = {};
        const keys = Object.keys(raw).sort();
        for (let i = 0; i < keys.length; i += 1) {
            const oid = keys[i];
            const entry = raw[oid];
            if (!isObject(entry)) {
                continue;
            }
            const rawRatings = isObject(entry.ratings) ? entry.ratings : {};
            const ratings = {};
            const rKeys = Object.keys(rawRatings).sort();
            for (let j = 0; j < rKeys.length; j += 1) {
                const cid = rKeys[j];
                const rv = rawRatings[cid];
                if (isValidRating(rv)) {
                    ratings[cid] = rv;
                }
            }
            const note = isText(entry.note) ? entry.note : '';
            const seq = typeof entry.updated_seq === 'number' && isFinite(entry.updated_seq) && entry.updated_seq >= 0
                ? Math.floor(entry.updated_seq)
                : 0;
            out[oid] = {
                schema_version: SCHEMA_VERSION,
                outcome_id: oid,
                ratings: ratings,
                note: note,
                updated_seq: seq
            };
        }
        return out;
    }
    function readSelfAssessments(storeOrState) {
        if (!storeOrState) {
            return {};
        }
        const state = typeof storeOrState.getState === 'function' ? storeOrState.getState() : storeOrState;
        if (!isObject(state)) {
            return {};
        }
        return normalizeSelfAssessmentMap(state.self_assessments);
    }
    function saveSelfAssessment(store, outcomeId, payload, options) {
        if (!store || typeof store.update !== 'function') {
            return fail('E_REVISION_CARD_ERROR', 'Nepieciešama derīga SimStore krātuve pašvērtējuma saglabāšanai.', {});
        }
        const opts = options || {};
        const doc = opts.doc || root.document;
        const cov = loadCoverage(doc, opts.coverage);
        const covOutcomes = Array.isArray(cov.outcomes) ? cov.outcomes : [];
        let knownOutcome = false;
        for (let i = 0; i < covOutcomes.length; i += 1) {
            if (isObject(covOutcomes[i]) && covOutcomes[i].id === outcomeId) {
                knownOutcome = true;
                break;
            }
        }
        if (!knownOutcome) {
            return fail('E_REVISION_UNKNOWN_OUTCOME', 'Nezināms mācību mērķis "' + outcomeId + '".', {
                outcome_id: outcomeId
            });
        }
        let noteMaxLength = NOTE_MAX_LENGTH;
        if (opts.policy && isObject(opts.policy.self_assessment) && typeof opts.policy.self_assessment.note_max_length === 'number') {
            noteMaxLength = opts.policy.self_assessment.note_max_length;
        }
        else {
            try {
                const pol = loadPolicy(doc).policy;
                if (isObject(pol.self_assessment) && typeof pol.self_assessment.note_max_length === 'number') {
                    noteMaxLength = pol.self_assessment.note_max_length;
                }
            }
            catch (_err) {
                noteMaxLength = NOTE_MAX_LENGTH;
            }
        }
        const rawRatings = payload && isObject(payload.ratings) ? payload.ratings : {};
        const cleanRatings = {};
        const ratingKeys = Object.keys(rawRatings).sort();
        for (let i = 0; i < ratingKeys.length; i += 1) {
            const cid = ratingKeys[i];
            const val = rawRatings[cid];
            if (val === '' || val === null || val === undefined) {
                continue;
            }
            if (!isValidRating(val)) {
                return fail('E_REVISION_INVALID_RATING', 'Nederīga pašvērtējuma vērtība kritērijam "' + cid + '": ' + String(val), {
                    outcome_id: outcomeId,
                    criterion_id: cid,
                    value: val
                });
            }
            cleanRatings[cid] = val;
        }
        let note = '';
        if (payload && payload.note !== undefined && payload.note !== null) {
            if (!isText(payload.note)) {
                return fail('E_REVISION_CARD_ERROR', 'Pašvērtējuma piezīmei jābūt teksta virknei.', { outcome_id: outcomeId });
            }
            /* Store verbatim — never trim, normalize, or parse learner text. */
            note = payload.note;
        }
        if (note.length > noteMaxLength) {
            return fail('E_REVISION_NOTE_TOO_LONG', 'Brīvā teksta piezīme pārsniedz deklarēto maksimumu (' + note.length + ' > ' + noteMaxLength + ' rakstzīmes).', { outcome_id: outcomeId, length: note.length, max_length: noteMaxLength });
        }
        let savedRecord = null;
        const nextState = store.update(function (draft) {
            const current = normalizeSelfAssessmentMap(draft.self_assessments);
            let maxSeq = 0;
            const existingKeys = Object.keys(current);
            for (let i = 0; i < existingKeys.length; i += 1) {
                if (current[existingKeys[i]].updated_seq > maxSeq) {
                    maxSeq = current[existingKeys[i]].updated_seq;
                }
            }
            const entry = sortedValue({
                schema_version: SCHEMA_VERSION,
                outcome_id: outcomeId,
                ratings: cleanRatings,
                note: note,
                updated_seq: maxSeq + 1
            });
            current[outcomeId] = entry;
            /* Separation invariant: ONLY draft.self_assessments is written; draft.mastery is untouched. */
            draft.self_assessments = sortedValue(current);
            savedRecord = entry;
        });
        return {
            record: savedRecord,
            self_assessments: readSelfAssessments(nextState),
            state: nextState
        };
    }
    /* --------------------------------------------------- view model & audit */
    function buildRevisionViewModel(options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const loadedPol = opts.policy ? { policy: sortedValue(copyJson(opts.policy)), digest: digestValue(opts.policy) } : loadPolicy(doc);
        const policy = loadedPol.policy;
        const termsMap = loadTermsMap(opts.terms || doc);
        const coverage = loadCoverage(doc, opts.coverage);
        const bankQuestions = loadBankQuestions(doc, opts.bankQuestions);
        /* A.1.2: On-read affordance validation against anchors & chains (same rigor as N28). */
        const affordanceMap = validateOutcomeAffordances(coverage, {
            doc: doc,
            anchorRegistry: opts.anchorRegistry,
            conceptSummaries: opts.conceptSummaries,
            chains: opts.chains
        });
        const masteryApi = root.SimMastery;
        const remApi = root.SimRemediation;
        let masteryMap = opts.masteryMap || null;
        if (!masteryMap && masteryApi && typeof masteryApi.readFromStore === 'function') {
            const mLoaded = typeof masteryApi.loadPolicy === 'function' ? masteryApi.loadPolicy(doc) : { policy: {}, digest: '' };
            masteryMap = masteryApi.readFromStore(opts.store || null, coverage, mLoaded.policy, mLoaded.digest);
        }
        if (!masteryMap) {
            masteryMap = { schema_version: 1, outcomes: {} };
        }
        let availability = opts.availability || null;
        if (!availability && masteryApi && typeof masteryApi.computeAvailability === 'function') {
            availability = masteryApi.computeAvailability(coverage, bankQuestions);
        }
        if (!availability) {
            availability = {};
        }
        let queueSnapshot = opts.queueSnapshot || null;
        if (!queueSnapshot && opts.store && remApi && typeof remApi.getQueueSnapshot === 'function') {
            queueSnapshot = remApi.getQueueSnapshot(opts.store, {
                doc: doc,
                coverage: coverage,
                chains: loadChainsData(doc, opts.chains)
            });
        }
        if (!queueSnapshot) {
            queueSnapshot = { active_entries: [], by_outcome: {}, active_count: 0 };
        }
        const selfAssessments = opts.selfAssessments
            ? normalizeSelfAssessmentMap(opts.selfAssessments)
            : readSelfAssessments(opts.store);
        const covTopics = Array.isArray(coverage.topics) ? coverage.topics : [];
        const covOutcomes = Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        const topicNames = {};
        for (let i = 0; i < covTopics.length; i += 1) {
            if (isObject(covTopics[i])) {
                topicNames[String(covTopics[i].topic)] = isText(covTopics[i].name_lv)
                    ? covTopics[i].name_lv
                    : String(covTopics[i].topic) + '. tēma';
            }
        }
        /* Eligible family/instance mapping per outcome from bank (selection-only, no keys). */
        const eligibleByOutcome = {};
        for (let i = 0; i < bankQuestions.length; i += 1) {
            const q = bankQuestions[i];
            if (!isObject(q) || !isText(q.question_id) || !isText(q.family_id)) {
                continue;
            }
            const rev = q.review;
            const wf = q.extensions && q.extensions.data ? q.extensions.data.review_workflow : null;
            const isEph = Boolean((q.extensions && q.extensions.data && q.extensions.data.ephemeral && q.extensions.data.ephemeral.frozen_bank_member === false) || /-EPH-[0-9]+$/.test(q.question_id));
            const eligible = !isEph && isObject(rev) && rev.accessibility === 'passed' && rev.calculation === 'passed' &&
                rev.content === 'passed' && rev.source === 'passed' && (!isObject(wf) || wf.state === 'accepted');
            if (!eligible) {
                continue;
            }
            const oids = Array.isArray(q.outcome_ids) ? q.outcome_ids : [];
            for (let j = 0; j < oids.length; j += 1) {
                const oid = oids[j];
                if (!isText(oid)) {
                    continue;
                }
                if (!eligibleByOutcome[oid]) {
                    eligibleByOutcome[oid] = { family_ids: [], instance_ids: [] };
                }
                if (eligibleByOutcome[oid].family_ids.indexOf(q.family_id) < 0) {
                    eligibleByOutcome[oid].family_ids.push(q.family_id);
                }
                if (eligibleByOutcome[oid].instance_ids.indexOf(q.question_id) < 0) {
                    eligibleByOutcome[oid].instance_ids.push(q.question_id);
                }
            }
        }
        const masteryOutcomes = isObject(masteryMap.outcomes) ? masteryMap.outcomes : {};
        const queueByOutcome = isObject(queueSnapshot.by_outcome) ? queueSnapshot.by_outcome : {};
        const stateLabels = {
            unseen: { icon: '○', label_lv: 'Nav mēģināts' },
            learning: { icon: '◔', label_lv: 'Apgūšanas procesā' },
            near_mastered: { icon: '◑', label_lv: 'Gandrīz apgūts' },
            mastered: { icon: '●', label_lv: 'Apgūts (pašmācībā)' },
            needs_review: { icon: '↻', label_lv: 'Jāatkārto' },
            unavailable: { icon: '⊘', label_lv: 'Pagaidām nav pieejams' }
        };
        const byTopic = { '1': [], '2': [], '3': [], '4': [], '5': [], '6': [], '7': [] };
        const allRows = [];
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oc = covOutcomes[i];
            if (!isObject(oc) || !isText(oc.id)) {
                continue;
            }
            const oid = oc.id;
            const mEntry = isObject(masteryOutcomes[oid]) ? masteryOutcomes[oid] : {
                outcome_id: oid,
                state: 'unseen',
                consecutive_correct: 0,
                attempts: 0,
                last_practiced_day: null
            };
            const avail = isObject(availability[oid]) ? availability[oid] : {
                outcome_id: oid,
                available: true,
                eligible_count: eligibleByOutcome[oid] ? eligibleByOutcome[oid].instance_ids.length : 1,
                reason_lv: null
            };
            const available = Boolean(avail.available);
            const rawState = isText(mEntry.state) ? mEntry.state : 'unseen';
            const effectiveState = available ? rawState : 'unavailable';
            const stMeta = stateLabels[effectiveState] || stateLabels.unseen;
            const lastDay = typeof mEntry.last_practiced_day === 'number' && isFinite(mEntry.last_practiced_day)
                ? mEntry.last_practiced_day
                : null;
            const lastPracticedLv = lastDay !== null
                ? formatCopy(termText(termsMap, 'revision.panel.last_practiced_day', 'Pēdējā prakse: {day}. diena'), { day: lastDay })
                : termText(termsMap, 'revision.panel.last_practiced_never', 'Pēdējā prakse: nav mēģināts (0)');
            const qEntries = Array.isArray(queueByOutcome[oid]) ? queueByOutcome[oid] : [];
            const activeQ = qEntries.filter(function (qe) {
                return isObject(qe) && (qe.state === 'open' || qe.state === 'retried');
            });
            let qOpen = 0;
            let qRetried = 0;
            const qIds = [];
            for (let qIdx = 0; qIdx < activeQ.length; qIdx += 1) {
                if (activeQ[qIdx].state === 'retried') {
                    qRetried += 1;
                }
                else {
                    qOpen += 1;
                }
                if (isText(activeQ[qIdx].id)) {
                    qIds.push(activeQ[qIdx].id);
                }
            }
            const criteriaList = resolveOutcomeCriteria(oid, coverage, bankQuestions, termsMap);
            const saEntry = selfAssessments[oid] || null;
            const saRatings = saEntry ? saEntry.ratings : {};
            const ratedCount = Object.keys(saRatings).length;
            const saSummaryLv = ratedCount > 0
                ? formatCopy(termText(termsMap, 'revision.sa.summary_present', 'Pašvērtējums (F07): {rated} no {total} kritērijiem novērtēti'), { rated: ratedCount, total: criteriaList.length })
                : termText(termsMap, 'revision.sa.summary_none', 'Pašvērtējums (F07): vēl nav aizpildīts');
            const aff = affordanceMap[oid] || { master_anchor: oc.master_anchor || '', chain_ids: [] };
            const eligData = eligibleByOutcome[oid] || {
                family_ids: (oc.bindings && Array.isArray(oc.bindings.practice_families)) ? oc.bindings.practice_families.slice().sort() : [],
                instance_ids: []
            };
            const row = {
                outcome_id: oid,
                topic: Number(oc.topic),
                statement_lv: isText(oc.statement_lv) ? oc.statement_lv : '',
                mastery: {
                    source: 'N26:SimMastery',
                    state: rawState,
                    effective_state: effectiveState,
                    icon: stMeta.icon,
                    label_lv: stMeta.label_lv,
                    attempts: typeof mEntry.attempts === 'number' ? mEntry.attempts : 0,
                    consecutive_correct: typeof mEntry.consecutive_correct === 'number' ? mEntry.consecutive_correct : 0,
                    last_practiced_day: lastDay,
                    last_practiced_lv: lastPracticedLv
                },
                availability: {
                    source: 'N24/N26:Eligibility',
                    available: available,
                    eligible_count: typeof avail.eligible_count === 'number' ? avail.eligible_count : 0,
                    reason_lv: available ? null : (isText(avail.reason_lv) ? avail.reason_lv : 'Pagaidām nav pieejams praksei.')
                },
                queue: {
                    source: 'N28:SimRemediation',
                    active_count: activeQ.length,
                    open_count: qOpen,
                    retried_count: qRetried,
                    entry_ids: qIds.sort()
                },
                self_assessment: {
                    source: 'N29:F07',
                    criteria_total: criteriaList.length,
                    rated_count: ratedCount,
                    has_ratings: ratedCount > 0,
                    has_note: Boolean(saEntry && saEntry.note.length > 0),
                    summary_lv: saSummaryLv,
                    updated_seq: saEntry ? saEntry.updated_seq : 0,
                    ratings: copyJson(saRatings)
                },
                affordances: {
                    source: 'N02/N07/N16/N30:Affordances',
                    concept_id: oid,
                    master_anchor: aff.master_anchor,
                    chain_ids: aff.chain_ids.slice(),
                    has_chain: aff.chain_ids.length > 0,
                    practice_available: available && eligData.instance_ids.length > 0,
                    practice_reason_lv: available ? null : (isText(avail.reason_lv) ? avail.reason_lv : 'Pagaidām nav pieejams praksei.'),
                    family_ids: eligData.family_ids.slice().sort(),
                    instance_ids: eligData.instance_ids.slice().sort()
                }
            };
            allRows.push(row);
            const tk = String(oc.topic);
            if (has(byTopic, tk)) {
                byTopic[tk].push(row);
            }
        }
        const totalCounts = {
            unseen: 0, learning: 0, near_mastered: 0, mastered: 0, needs_review: 0, unavailable: 0
        };
        const topics = [];
        for (let t = 1; t <= 7; t += 1) {
            const tk = String(t);
            const rows = byTopic[tk] || [];
            const counts = {
                unseen: 0, learning: 0, near_mastered: 0, mastered: 0, needs_review: 0, unavailable: 0
            };
            let topicAttempts = 0;
            let selfRatedCount = 0;
            for (let r = 0; r < rows.length; r += 1) {
                const eff = rows[r].mastery.effective_state;
                counts[eff] = (counts[eff] || 0) + 1;
                totalCounts[eff] = (totalCounts[eff] || 0) + 1;
                topicAttempts += rows[r].mastery.attempts;
                if (rows[r].self_assessment.has_ratings || rows[r].self_assessment.has_note) {
                    selfRatedCount += 1;
                }
            }
            const isEmptyTopic = topicAttempts === 0;
            const summaryLine = formatCopy(termText(termsMap, 'revision.topic.summary_line', '{topic}. tēma — Apgūti: {mastered} · Gandrīz apgūti: {near_mastered} · Apgūšanā: {learning} · Jāatkārto: {needs_review} · Nav mēģināti: {unseen} · Nepieejami: {unavailable} · Pašvērtēti: {self_rated}'), {
                topic: t,
                mastered: counts.mastered,
                near_mastered: counts.near_mastered,
                learning: counts.learning,
                needs_review: counts.needs_review,
                unseen: counts.unseen,
                unavailable: counts.unavailable,
                self_rated: selfRatedCount
            });
            topics.push({
                topic: t,
                name_lv: topicNames[tk] || (tk + '. tēma'),
                outcomes_total: rows.length,
                counts: counts,
                self_rated_outcomes_count: selfRatedCount,
                is_empty_topic: isEmptyTopic,
                empty_notice_lv: isEmptyTopic
                    ? termText(termsMap, 'revision.panel.empty_topic', 'Šajā tēmā pašlaik nav reģistrētu automātisko mēģinājumu (godīgs sākuma stāvoklis: 0).')
                    : null,
                summary_line_lv: summaryLine,
                outcomes: rows
            });
        }
        const model = sortedValue({
            schema_version: SCHEMA_VERSION,
            contract: 'N29-revision-view-model',
            policy_id: policy.policy_id,
            policy_digest: loadedPol.digest,
            epistemic_label: 'PROPOSED',
            official_counterpart_status: 'UNDETERMINED',
            title_lv: termText(termsMap, 'revision.panel.title', 'Vienotais atkārtošanas pārskats un kritēriju pašvērtējums (PROPOSED)'),
            honesty_note_lv: termText(termsMap, 'revision.panel.honesty_note', policy.honesty_note_lv),
            total_outcomes: allRows.length,
            counts: totalCounts,
            topics: topics
        });
        model.digest = digestValue(model);
        return model;
    }
    function startPracticeFromOutcome(outcomeId, options) {
        const opts = options || {};
        const vm = opts.viewModel || buildRevisionViewModel(opts);
        let targetRow = null;
        const topics = Array.isArray(vm.topics) ? vm.topics : [];
        for (let i = 0; i < topics.length; i += 1) {
            const rows = Array.isArray(topics[i].outcomes) ? topics[i].outcomes : [];
            for (let j = 0; j < rows.length; j += 1) {
                if (rows[j].outcome_id === outcomeId) {
                    targetRow = rows[j];
                    break;
                }
            }
            if (targetRow) {
                break;
            }
        }
        if (!targetRow) {
            return fail('E_REVISION_UNKNOWN_OUTCOME', 'Nezināms mācību mērķis "' + outcomeId + '".', { outcome_id: outcomeId });
        }
        if (!targetRow.availability.available || !targetRow.affordances.practice_available || targetRow.affordances.instance_ids.length === 0) {
            return fail('E_REVISION_OUTCOME_UNAVAILABLE', 'Mērķim "' + outcomeId + '" pašlaik nav treniņformai derīgu uzdevumu praksei.', { outcome_id: outcomeId, reason_lv: targetRow.availability.reason_lv });
        }
        /* Exact N27/N29 -> N30 selection-only handoff contract (zero keys, zero answers). */
        return sortedValue({
            schema_version: SCHEMA_VERSION,
            contract: 'N27-to-N30-practice-entry',
            entry_source: 'revision_panel',
            outcome_id: targetRow.outcome_id,
            topic: targetRow.topic,
            mastery_state: targetRow.mastery.state,
            filters: {
                topic: targetRow.topic,
                outcome_id: targetRow.outcome_id,
                family_ids: targetRow.affordances.family_ids.slice().sort(),
                instance_ids: targetRow.affordances.instance_ids.slice().sort()
            }
        });
    }
    function buildSelfAssessmentCardModel(outcomeId, options) {
        const opts = options || {};
        const doc = opts.doc || root.document;
        const loadedPol = opts.policy ? { policy: sortedValue(copyJson(opts.policy)), digest: digestValue(opts.policy) } : loadPolicy(doc);
        const policy = loadedPol.policy;
        const termsMap = loadTermsMap(opts.terms || doc);
        const coverage = loadCoverage(doc, opts.coverage);
        const bankQuestions = loadBankQuestions(doc, opts.bankQuestions);
        const covOutcomes = Array.isArray(coverage.outcomes) ? coverage.outcomes : [];
        let outcomeObj = null;
        for (let i = 0; i < covOutcomes.length; i += 1) {
            if (isObject(covOutcomes[i]) && covOutcomes[i].id === outcomeId) {
                outcomeObj = covOutcomes[i];
                break;
            }
        }
        if (!outcomeObj) {
            return fail('E_REVISION_UNKNOWN_OUTCOME', 'Nezināms mācību mērķis "' + outcomeId + '".', { outcome_id: outcomeId });
        }
        const criteria = resolveOutcomeCriteria(outcomeId, coverage, bankQuestions, termsMap);
        const saMap = opts.selfAssessments
            ? normalizeSelfAssessmentMap(opts.selfAssessments)
            : readSelfAssessments(opts.store);
        const saved = saMap[outcomeId] || null;
        const savedRatings = saved ? saved.ratings : {};
        const noteMaxLength = isObject(policy.self_assessment) && typeof policy.self_assessment.note_max_length === 'number'
            ? policy.self_assessment.note_max_length
            : NOTE_MAX_LENGTH;
        const ratingOptions = [
            { id: '', label_lv: termText(termsMap, 'revision.rating.unrated', 'Nav novērtēts') },
            { id: 'confident', label_lv: termText(termsMap, 'revision.rating.confident', 'Protu droši') },
            { id: 'with_effort', label_lv: termText(termsMap, 'revision.rating.with_effort', 'Protu ar piepūli') },
            { id: 'not_yet', label_lv: termText(termsMap, 'revision.rating.not_yet', 'Vēl neprotu') }
        ];
        const criteriaRows = criteria.map(function (c) {
            const current = has(savedRatings, c.criterion_id) ? savedRatings[c.criterion_id] : '';
            return {
                criterion_id: c.criterion_id,
                label_lv: c.label_lv,
                current_rating: current
            };
        });
        const card = sortedValue({
            schema_version: SCHEMA_VERSION,
            contract: 'N29-f07-self-assessment-card',
            source: 'N29:F07',
            epistemic_label: 'PROPOSED',
            official_counterpart_status: 'UNDETERMINED',
            outcome_id: outcomeId,
            topic: Number(outcomeObj.topic),
            statement_lv: isText(outcomeObj.statement_lv) ? outcomeObj.statement_lv : '',
            title_lv: formatCopy(termText(termsMap, 'revision.sa.card_title', 'Kritēriju pašvērtējuma kartīte (F07) — {outcome_id}'), { outcome_id: outcomeId }),
            self_assessment_label_lv: termText(termsMap, 'revision.sa.label_own', VERBATIM_SELF_ASSESSMENT_LABEL_LV),
            note_label_lv: termText(termsMap, 'revision.sa.note_label', 'Izvēles brīvā teksta piezīme (nav obligāta)'),
            note_never_analyzed_lv: termText(termsMap, 'revision.sa.note_policy', VERBATIM_NOTE_NEVER_ANALYZED_LV),
            note_max_length: noteMaxLength,
            note: saved ? saved.note : '',
            key_free_criteria_only: true,
            excluded_from_mastery: true,
            rating_options: ratingOptions,
            criteria: criteriaRows
        });
        card.digest = digestValue(card);
        return card;
    }
    /* --------------------------------------------------- honesty audit (C.1) */
    function buildHonestyAudit(viewModel, cardModel) {
        const entries = [];
        const topics = Array.isArray(viewModel.topics) ? viewModel.topics : [];
        for (let t = 0; t < topics.length; t += 1) {
            const tp = topics[t];
            const rows = Array.isArray(tp.outcomes) ? tp.outcomes : [];
            for (let r = 0; r < rows.length; r += 1) {
                const row = rows[r];
                const oid = row.outcome_id;
                const checks = [
                    [oid + '.mastery', row.mastery, 'N26:SimMastery'],
                    [oid + '.availability', row.availability, 'N24/N26:Eligibility'],
                    [oid + '.queue', row.queue, 'N28:SimRemediation'],
                    [oid + '.self_assessment', row.self_assessment, 'N29:F07'],
                    [oid + '.affordances', row.affordances, 'N02/N07/N16/N30:Affordances']
                ];
                for (let k = 0; k < checks.length; k += 1) {
                    const elName = checks[k][0];
                    const block = checks[k][1];
                    const expectedSrc = checks[k][2];
                    const actualSrc = isObject(block) && isText(block.source) ? block.source : '';
                    const traceable = actualSrc === expectedSrc;
                    entries.push({
                        element: elName,
                        source: actualSrc || 'UNTRACEABLE',
                        single_source: traceable,
                        merged: false,
                        traceable: traceable
                    });
                }
            }
        }
        if (cardModel && isObject(cardModel)) {
            const cardSrc = isText(cardModel.source) ? cardModel.source : '';
            entries.push({
                element: 'card.' + String(cardModel.outcome_id || '') + '.self_assessment',
                source: cardSrc || 'UNTRACEABLE',
                single_source: cardSrc === 'N29:F07',
                merged: false,
                traceable: cardSrc === 'N29:F07'
            });
            const criteria = Array.isArray(cardModel.criteria) ? cardModel.criteria : [];
            for (let c = 0; c < criteria.length; c += 1) {
                const crit = criteria[c];
                const ok = isObject(crit) && isText(crit.label_lv) && crit.label_lv !== '' && !has(crit, 'points') && !has(crit, 'expected');
                entries.push({
                    element: 'card.' + String(cardModel.outcome_id || '') + '.criterion.' + String(crit.criterion_id || c),
                    source: ok ? 'N23/N10:CriteriaLabels' : 'UNTRACEABLE',
                    single_source: ok,
                    merged: false,
                    traceable: ok
                });
            }
        }
        const untraceable = entries.filter(function (e) { return !e.traceable; });
        const merged = entries.filter(function (e) { return e.merged; });
        return {
            schema_version: SCHEMA_VERSION,
            contract: 'N29-honesty-audit',
            status: untraceable.length === 0 && merged.length === 0 ? 'PASS' : 'FAIL',
            total_elements: entries.length,
            untraceable_count: untraceable.length,
            merged_sources_count: merged.length,
            entries: entries
        };
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
    function safeDomId(raw) {
        return raw.replace(/[^A-Za-z0-9_-]+/g, '-');
    }
    function renderError(doc, error) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-revision-error');
        if (box) {
            const code = isObject(error) && isText(error.code) ? error.code : 'E_REVISION';
            const msg = isObject(error) && isText(error.message) ? error.message : String(error);
            box.textContent = 'Pārskata kļūda (' + code + '): ' + msg;
            box.hidden = false;
        }
    }
    function clearError(doc) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-revision-error');
        if (box) {
            box.textContent = '';
            box.hidden = true;
        }
    }
    function openStudyAnchor(doc, outcomeId, returnElementId) {
        const drawer = root.SimConceptDrawer;
        if (!drawer || typeof drawer.openFromLink !== 'function') {
            return fail('E_REVISION_CARD_ERROR', 'Konceptu atvilktne nav ielādēta.', { outcome_id: outcomeId });
        }
        const triggerEl = doc && typeof doc.getElementById === 'function' && returnElementId
            ? doc.getElementById(returnElementId)
            : null;
        drawer.openFromLink({
            conceptId: outcomeId,
            source: 'revision-panel',
            returnContext: {
                elementId: returnElementId || 'atskats-revision-panel',
                triggerEl: triggerEl,
                anchor: '#atskats',
                labelLv: 'Atgriezties atkārtošanas pārskatā'
            }
        }, doc);
    }
    function openStudyChain(doc, outcomeId, chainId, returnElementId) {
        const chainsApi = root.SimChains;
        if (!chainsApi || typeof chainsApi.mountChain !== 'function') {
            return fail('E_REVISION_CARD_ERROR', 'Darba piemēru ķēžu modulis nav ielādēts.', { chain_id: chainId });
        }
        const host = doc && typeof doc.getElementById === 'function' ? doc.getElementById('atskats-revision-chain-host') : null;
        if (!host) {
            return fail('E_REVISION_CARD_ERROR', '#atskats-revision-chain-host nav atrasts.', { chain_id: chainId });
        }
        clearNode(host);
        host.hidden = false;
        host.setAttribute('data-outcome-id', outcomeId);
        host.setAttribute('data-chain-id', chainId);
        const bar = makeEl(doc, 'div', 'remediation-study-bar');
        bar.appendChild(makeEl(doc, 'span', 'remediation-study-label', 'Darba piemēra studēšana (' + chainId + ' · ' + outcomeId + ')'));
        const returnBtn = makeEl(doc, 'button', 'btn-control revision-chain-return-btn', 'Atgriezties atkārtošanas pārskatā');
        returnBtn.type = 'button';
        returnBtn.id = 'atskats-revision-chain-return';
        returnBtn.addEventListener('click', function () {
            clearNode(host);
            host.hidden = true;
            const target = returnElementId && doc.getElementById(returnElementId)
                ? doc.getElementById(returnElementId)
                : doc.getElementById('atskats-revision-panel');
            if (target && typeof target.focus === 'function') {
                target.focus();
            }
        });
        bar.appendChild(returnBtn);
        host.appendChild(bar);
        const mountHost = makeEl(doc, 'div', 'revision-chain-mount');
        mountHost.id = 'atskats-revision-chain-mount';
        host.appendChild(mountHost);
        chainsApi.mountChain(doc, mountHost, chainId);
    }
    function renderPracticeHandoff(doc, handoff) {
        const host = doc && typeof doc.getElementById === 'function' ? doc.getElementById('atskats-revision-handoff') : null;
        if (!host) {
            return;
        }
        clearNode(host);
        host.hidden = false;
        host.setAttribute('data-contract', handoff.contract);
        host.setAttribute('data-outcome-id', handoff.outcome_id);
        host.appendChild(makeEl(doc, 'h4', 'revision-handoff-title', 'Prakses ceļa sagatave mērķim ' + handoff.outcome_id + ' (N29 → N30)'));
        host.appendChild(makeEl(doc, 'p', 'revision-handoff-meta', 'Tēma: ' + handoff.topic + ' · Saimes: ' + (handoff.filters.family_ids || []).join(', ') +
            ' · Derīgie uzdevumi: ' + (handoff.filters.instance_ids || []).length));
        if (typeof host.focus === 'function') {
            host.focus();
        }
    }
    function openSelfAssessmentCard(doc, outcomeId, options) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const host = doc.getElementById('atskats-self-assessment-host');
        if (!host) {
            return null;
        }
        const termsMap = loadTermsMap(opts.terms || doc);
        const cardModel = buildSelfAssessmentCardModel(outcomeId, {
            doc: doc,
            store: opts.store,
            coverage: opts.coverage,
            bankQuestions: opts.bankQuestions,
            terms: termsMap,
            policy: opts.policy
        });
        clearNode(host);
        host.hidden = false;
        host.setAttribute('data-outcome-id', outcomeId);
        host.setAttribute('data-source', 'N29:F07');
        const card = makeEl(doc, 'article', 'panel revision-sa-card');
        card.id = 'atskats-sa-card';
        card.setAttribute('data-outcome-id', outcomeId);
        card.setAttribute('data-source', 'self-assessment-f07');
        card.setAttribute('aria-labelledby', 'atskats-sa-title');
        const header = makeEl(doc, 'div', 'revision-sa-header');
        const title = makeEl(doc, 'h4', 'revision-sa-title', cardModel.title_lv);
        title.id = 'atskats-sa-title';
        header.appendChild(title);
        const closeBtn = makeEl(doc, 'button', 'btn-control revision-sa-close-btn', termText(termsMap, 'revision.sa.close', 'Aizvērt kartīti'));
        closeBtn.type = 'button';
        closeBtn.id = 'atskats-sa-close';
        closeBtn.addEventListener('click', function () {
            clearNode(host);
            host.hidden = true;
            const ret = opts.returnElementId && doc.getElementById(opts.returnElementId)
                ? doc.getElementById(opts.returnElementId)
                : doc.getElementById('atskats-revision-panel');
            if (ret && typeof ret.focus === 'function') {
                ret.focus();
            }
        });
        header.appendChild(closeBtn);
        card.appendChild(header);
        const ownLabel = makeEl(doc, 'p', 'scope-note revision-sa-own-label', cardModel.self_assessment_label_lv);
        ownLabel.id = 'atskats-sa-label';
        card.appendChild(ownLabel);
        card.appendChild(makeEl(doc, 'p', 'revision-sa-outcome-stmt', cardModel.outcome_id + ' — ' + cardModel.statement_lv));
        const liveEl = makeEl(doc, 'p', 'setting-status revision-sa-live', '');
        liveEl.id = 'atskats-sa-live';
        liveEl.setAttribute('role', 'status');
        liveEl.setAttribute('aria-live', 'polite');
        card.appendChild(liveEl);
        const draftRatings = {};
        const ratingLabelById = {};
        for (let r = 0; r < cardModel.rating_options.length; r += 1) {
            ratingLabelById[cardModel.rating_options[r].id] = cardModel.rating_options[r].label_lv;
        }
        const criteriaList = makeEl(doc, 'ul', 'revision-sa-criteria-list');
        criteriaList.id = 'atskats-sa-criteria-list';
        const annTemplate = termText(termsMap, 'revision.sa.announcement', 'Kritērijs "{label}": izvēlēts stāvoklis "{rating}"');
        for (let i = 0; i < cardModel.criteria.length; i += 1) {
            const crit = cardModel.criteria[i];
            if (crit.current_rating) {
                draftRatings[crit.criterion_id] = crit.current_rating;
            }
            const li = makeEl(doc, 'li', 'revision-sa-criterion-row');
            li.setAttribute('data-criterion-id', crit.criterion_id);
            const selectId = 'rev-sa-select-' + safeDomId(outcomeId) + '-' + safeDomId(crit.criterion_id);
            const labelEl = makeEl(doc, 'label', 'revision-sa-criterion-label', crit.label_lv);
            labelEl.setAttribute('for', selectId);
            li.appendChild(labelEl);
            const selectEl = makeEl(doc, 'select', 'revision-sa-select');
            selectEl.id = selectId;
            selectEl.setAttribute('data-criterion-id', crit.criterion_id);
            selectEl.setAttribute('aria-label', crit.label_lv);
            for (let o = 0; o < cardModel.rating_options.length; o += 1) {
                const optData = cardModel.rating_options[o];
                const optEl = makeEl(doc, 'option', null, optData.label_lv);
                optEl.value = optData.id;
                optEl.setAttribute('value', optData.id);
                if (crit.current_rating === optData.id) {
                    optEl.selected = true;
                    optEl.setAttribute('selected', 'selected');
                }
                selectEl.appendChild(optEl);
            }
            selectEl.value = crit.current_rating || '';
            selectEl.addEventListener('change', function (ev) {
                const nextVal = ev && ev.target && typeof ev.target.value === 'string' ? ev.target.value : selectEl.value;
                selectEl.value = nextVal;
                if (nextVal === '') {
                    delete draftRatings[crit.criterion_id];
                }
                else {
                    draftRatings[crit.criterion_id] = nextVal;
                }
                const rLabel = ratingLabelById[nextVal] || nextVal;
                liveEl.textContent = formatCopy(annTemplate, { label: crit.label_lv, rating: rLabel });
            });
            li.appendChild(selectEl);
            criteriaList.appendChild(li);
        }
        card.appendChild(criteriaList);
        const noteWrap = makeEl(doc, 'div', 'revision-sa-note-wrap');
        const noteLabel = makeEl(doc, 'label', 'revision-sa-note-label', cardModel.note_label_lv);
        noteLabel.setAttribute('for', 'atskats-sa-note');
        noteWrap.appendChild(noteLabel);
        const noteArea = makeEl(doc, 'textarea', 'revision-sa-note');
        noteArea.id = 'atskats-sa-note';
        noteArea.setAttribute('rows', '3');
        noteArea.setAttribute('maxlength', String(cardModel.note_max_length));
        noteArea.setAttribute('aria-describedby', 'atskats-sa-note-policy atskats-sa-note-counter');
        noteArea.value = cardModel.note || '';
        noteArea.textContent = cardModel.note || '';
        const counterTpl = termText(termsMap, 'revision.sa.note_counter', '{count} no {max} rakstzīmēm');
        const counterEl = makeEl(doc, 'p', 'setting-status revision-sa-counter', formatCopy(counterTpl, { count: (cardModel.note || '').length, max: cardModel.note_max_length }));
        counterEl.id = 'atskats-sa-note-counter';
        noteArea.addEventListener('input', function () {
            const len = String(noteArea.value || '').length;
            counterEl.textContent = formatCopy(counterTpl, { count: len, max: cardModel.note_max_length });
        });
        const notePolicyEl = makeEl(doc, 'p', 'scope-note revision-sa-note-policy', cardModel.note_never_analyzed_lv);
        notePolicyEl.id = 'atskats-sa-note-policy';
        noteWrap.appendChild(noteArea);
        noteWrap.appendChild(counterEl);
        noteWrap.appendChild(notePolicyEl);
        card.appendChild(noteWrap);
        const statusEl = makeEl(doc, 'p', 'setting-status revision-sa-status', '');
        statusEl.id = 'atskats-sa-status';
        statusEl.setAttribute('role', 'status');
        statusEl.setAttribute('aria-live', 'polite');
        statusEl.hidden = true;
        const actions = makeEl(doc, 'div', 'revision-sa-actions');
        const saveBtn = makeEl(doc, 'button', 'btn-control revision-sa-save-btn', termText(termsMap, 'revision.sa.save', 'Saglabāt pašvērtējumu'));
        saveBtn.type = 'button';
        saveBtn.id = 'atskats-sa-save';
        saveBtn.addEventListener('click', function () {
            try {
                clearError(doc);
                const noteText = isText(noteArea.value) ? noteArea.value : '';
                if (opts.store) {
                    saveSelfAssessment(opts.store, outcomeId, {
                        ratings: draftRatings,
                        note: noteText
                    }, {
                        coverage: opts.coverage,
                        policy: opts.policy,
                        doc: doc
                    });
                }
                statusEl.textContent = formatCopy(termText(termsMap, 'revision.sa.saved_status', 'Pašvērtējums mērķim {outcome_id} saglabāts atsevišķā F07 sadaļā (apguves stāvoklis paliek nemainīts).'), { outcome_id: outcomeId });
                statusEl.hidden = false;
                if (typeof opts.onSaved === 'function') {
                    opts.onSaved();
                }
            }
            catch (err) {
                renderError(doc, err);
            }
        });
        actions.appendChild(saveBtn);
        card.appendChild(actions);
        card.appendChild(statusEl);
        host.appendChild(card);
        if (typeof host.focus === 'function') {
            host.focus();
        }
        return cardModel;
    }
    function renderRevisionPanel(doc, options) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        clearError(doc);
        const vm = buildRevisionViewModel({
            doc: doc,
            store: opts.store,
            coverage: opts.coverage,
            masteryMap: opts.masteryMap,
            availability: opts.availability,
            queueSnapshot: opts.queueSnapshot,
            selfAssessments: opts.selfAssessments,
            bankQuestions: opts.bankQuestions,
            anchorRegistry: opts.anchorRegistry,
            conceptSummaries: opts.conceptSummaries,
            chains: opts.chains,
            terms: opts.terms,
            policy: opts.policy
        });
        const termsMap = loadTermsMap(opts.terms || doc);
        const headingEl = doc.getElementById('atskats-revision-heading');
        if (headingEl) {
            headingEl.textContent = vm.title_lv;
        }
        const honestyEl = doc.getElementById('atskats-revision-honesty');
        if (honestyEl) {
            honestyEl.textContent = vm.honesty_note_lv;
        }
        const statusEl = doc.getElementById('atskats-revision-status');
        if (statusEl) {
            statusEl.textContent =
                'Kopā mērķi: ' + vm.total_outcomes +
                    ' · Apgūti: ' + (vm.counts.mastered || 0) +
                    ' · Gandrīz apgūti: ' + (vm.counts.near_mastered || 0) +
                    ' · Apgūšanā: ' + (vm.counts.learning || 0) +
                    ' · Jāatkārto: ' + (vm.counts.needs_review || 0) +
                    ' · Nav mēģināti: ' + (vm.counts.unseen || 0) +
                    ((vm.counts.unavailable || 0) > 0 ? ' · Nepieejami: ' + vm.counts.unavailable : '');
        }
        const panelEl = doc.getElementById('atskats-revision-panel');
        if (!panelEl) {
            return vm;
        }
        clearNode(panelEl);
        const anchorBtnLabel = termText(termsMap, 'revision.action.study_anchor', 'Atvērt jēdzienu');
        const chainBtnTpl = termText(termsMap, 'revision.action.study_chain', 'Darba piemērs ({chain_id})');
        const noChainText = termText(termsMap, 'revision.panel.no_chain', 'Darba piemēra ķēde nav piesaistīta');
        const practiceBtnLabel = termText(termsMap, 'revision.action.practice', 'Praktizēt mērķi');
        const saBtnLabel = termText(termsMap, 'revision.action.self_assess', 'Pašvērtēt kritērijus (F07)');
        for (let t = 0; t < vm.topics.length; t += 1) {
            const tp = vm.topics[t];
            const topicCard = makeEl(doc, 'section', 'panel revision-topic-card');
            topicCard.id = 'atskats-revision-topic-' + tp.topic;
            topicCard.setAttribute('data-topic', String(tp.topic));
            topicCard.setAttribute('aria-labelledby', 'atskats-revision-topic-title-' + tp.topic);
            const tTitle = makeEl(doc, 'h4', 'revision-topic-title', tp.topic + '. ' + tp.name_lv);
            tTitle.id = 'atskats-revision-topic-title-' + tp.topic;
            topicCard.appendChild(tTitle);
            const tSummary = makeEl(doc, 'p', 'revision-topic-summary', tp.summary_line_lv);
            tSummary.setAttribute('data-source', 'N26:SimMastery+N29:F07');
            topicCard.appendChild(tSummary);
            if (tp.is_empty_topic && tp.empty_notice_lv) {
                topicCard.appendChild(makeEl(doc, 'p', 'setting-status revision-topic-empty', tp.empty_notice_lv));
            }
            const ul = makeEl(doc, 'ul', 'revision-outcome-list');
            for (let r = 0; r < tp.outcomes.length; r += 1) {
                const row = tp.outcomes[r];
                const li = makeEl(doc, 'li', 'revision-outcome-row revision-state-' + row.mastery.effective_state);
                li.id = 'atskats-rev-row-' + safeDomId(row.outcome_id);
                li.setAttribute('data-outcome-id', row.outcome_id);
                li.setAttribute('data-mastery-state', row.mastery.effective_state);
                li.setAttribute('data-available', row.availability.available ? 'true' : 'false');
                const top = makeEl(doc, 'div', 'revision-outcome-head');
                /* Mastery badge (N26 source) — strictly separated from F07 self-rating badge. */
                const mBadge = makeEl(doc, 'span', 'mastery-badge revision-mastery-badge mastery-state-' + row.mastery.effective_state);
                mBadge.setAttribute('data-source', 'mastery-n26');
                const mIcon = makeEl(doc, 'span', 'mastery-icon', row.mastery.icon);
                mIcon.setAttribute('aria-hidden', 'true');
                mBadge.appendChild(mIcon);
                mBadge.appendChild(makeEl(doc, 'span', 'mastery-state-label', ' ' + row.mastery.label_lv));
                top.appendChild(mBadge);
                /* Distinct F07 self-assessment badge (N29:F07 source). */
                const saBadge = makeEl(doc, 'span', 'revision-self-badge');
                saBadge.setAttribute('data-source', 'self-assessment-f07');
                saBadge.setAttribute('data-rated-count', String(row.self_assessment.rated_count));
                saBadge.textContent = row.self_assessment.summary_lv;
                top.appendChild(saBadge);
                if (row.queue.active_count > 0) {
                    const qBadge = makeEl(doc, 'span', 'revision-queue-badge', 'Atkārtošanas rindā (N28): ' + row.queue.active_count);
                    qBadge.setAttribute('data-source', 'remediation-n28');
                    top.appendChild(qBadge);
                }
                li.appendChild(top);
                li.appendChild(makeEl(doc, 'p', 'revision-outcome-statement', row.outcome_id + ' — ' + row.statement_lv));
                const metaLine = makeEl(doc, 'p', 'revision-outcome-meta', row.mastery.last_practiced_lv);
                metaLine.setAttribute('data-source', 'mastery-n26');
                li.appendChild(metaLine);
                if (!row.availability.available && row.availability.reason_lv) {
                    const unavailNote = makeEl(doc, 'p', 'setting-status revision-unavailable-note', row.availability.reason_lv);
                    unavailNote.setAttribute('data-source', 'availability-n24-n26');
                    li.appendChild(unavailNote);
                }
                const actions = makeEl(doc, 'div', 'revision-outcome-actions');
                const anchorBtn = makeEl(doc, 'button', 'btn-control revision-anchor-btn', anchorBtnLabel);
                anchorBtn.type = 'button';
                anchorBtn.id = 'rev-anchor-' + safeDomId(row.outcome_id);
                anchorBtn.setAttribute('data-anchor', row.affordances.master_anchor);
                anchorBtn.addEventListener('click', function () {
                    try {
                        openStudyAnchor(doc, row.outcome_id, anchorBtn.id);
                    }
                    catch (err) {
                        renderError(doc, err);
                    }
                });
                actions.appendChild(anchorBtn);
                if (row.affordances.has_chain) {
                    const cid = row.affordances.chain_ids[0];
                    const chainBtn = makeEl(doc, 'button', 'btn-control revision-chain-btn', formatCopy(chainBtnTpl, { chain_id: cid }));
                    chainBtn.type = 'button';
                    chainBtn.id = 'rev-chain-' + safeDomId(row.outcome_id);
                    chainBtn.setAttribute('data-chain-id', cid);
                    chainBtn.setAttribute('data-has-chain', 'true');
                    chainBtn.addEventListener('click', function () {
                        try {
                            openStudyChain(doc, row.outcome_id, cid, chainBtn.id);
                        }
                        catch (err) {
                            renderError(doc, err);
                        }
                    });
                    actions.appendChild(chainBtn);
                }
                else {
                    const noChain = makeEl(doc, 'span', 'revision-no-chain', noChainText);
                    noChain.setAttribute('data-has-chain', 'false');
                    actions.appendChild(noChain);
                }
                const practiceBtn = makeEl(doc, 'button', 'btn-control revision-practice-btn', practiceBtnLabel);
                practiceBtn.type = 'button';
                practiceBtn.id = 'rev-practice-' + safeDomId(row.outcome_id);
                practiceBtn.setAttribute('data-outcome-id', row.outcome_id);
                if (!row.affordances.practice_available) {
                    practiceBtn.disabled = true;
                    practiceBtn.setAttribute('aria-disabled', 'true');
                }
                practiceBtn.addEventListener('click', function () {
                    try {
                        const handoff = startPracticeFromOutcome(row.outcome_id, { viewModel: vm });
                        renderPracticeHandoff(doc, handoff);
                        if (root.SimPractice && typeof root.SimPractice.startPath === 'function') {
                            root.SimPractice.startPath(handoff);
                        }
                        if (typeof opts.onPracticeEntry === 'function') {
                            opts.onPracticeEntry(handoff);
                        }
                    }
                    catch (err) {
                        renderError(doc, err);
                    }
                });
                actions.appendChild(practiceBtn);
                const saBtn = makeEl(doc, 'button', 'btn-control revision-sa-btn', saBtnLabel);
                saBtn.type = 'button';
                saBtn.id = 'rev-sa-open-' + safeDomId(row.outcome_id);
                saBtn.setAttribute('data-outcome-id', row.outcome_id);
                saBtn.addEventListener('click', function () {
                    try {
                        openSelfAssessmentCard(doc, row.outcome_id, {
                            store: opts.store,
                            coverage: opts.coverage,
                            bankQuestions: opts.bankQuestions,
                            terms: termsMap,
                            policy: opts.policy,
                            returnElementId: saBtn.id,
                            onSaved: function () {
                                renderRevisionPanel(doc, opts);
                            }
                        });
                    }
                    catch (err) {
                        renderError(doc, err);
                    }
                });
                actions.appendChild(saBtn);
                li.appendChild(actions);
                ul.appendChild(li);
            }
            topicCard.appendChild(ul);
            panelEl.appendChild(topicCard);
        }
        return vm;
    }
    function renderFromStore(doc, store, coverage, options) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        return renderRevisionPanel(doc, {
            store: store,
            coverage: coverage,
            bankQuestions: opts.bankQuestions,
            masteryMap: opts.masteryMap,
            availability: opts.availability,
            policy: opts.policy
        });
    }
    function init(doc, options) {
        doc = doc || root.document;
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const loadedPol = opts.policy ? { policy: sortedValue(copyJson(opts.policy)), digest: digestValue(opts.policy) } : loadPolicy(doc);
        const coverage = loadCoverage(doc, opts.coverage);
        const bankQuestions = opts.bank && Array.isArray(opts.bank.questions)
            ? opts.bank.questions
            : loadBankQuestions(doc);
        const storeApi = root.SimStore;
        const store = opts.store || (storeApi && typeof storeApi.createStore === 'function'
            ? storeApi.createStore({ optIn: false, doc: doc })
            : null);
        function refresh() {
            return renderRevisionPanel(doc, {
                store: store,
                coverage: coverage,
                bankQuestions: bankQuestions,
                policy: loadedPol.policy
            });
        }
        const vm = refresh();
        return {
            policy: loadedPol.policy,
            policyDigest: loadedPol.digest,
            coverage: coverage,
            store: store,
            viewModel: vm,
            refresh: refresh,
            openSelfAssessmentCard: function (outcomeId) {
                return openSelfAssessmentCard(doc, outcomeId, {
                    store: store,
                    coverage: coverage,
                    bankQuestions: bankQuestions,
                    policy: loadedPol.policy,
                    onSaved: refresh
                });
            },
            saveSelfAssessment: function (outcomeId, payload) {
                const res = saveSelfAssessment(store, outcomeId, payload, {
                    coverage: coverage,
                    policy: loadedPol.policy,
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
        NOTE_MAX_LENGTH: NOTE_MAX_LENGTH,
        VALID_RATINGS: VALID_RATINGS.slice(),
        VERBATIM_SELF_ASSESSMENT_LABEL_LV: VERBATIM_SELF_ASSESSMENT_LABEL_LV,
        VERBATIM_NOTE_NEVER_ANALYZED_LV: VERBATIM_NOTE_NEVER_ANALYZED_LV,
        errors: ERRORS.slice(),
        RevisionError: RevisionError,
        canonicalText: canonicalText,
        digestValue: digestValue,
        validatePolicy: validatePolicy,
        loadPolicy: loadPolicy,
        loadTermsMap: loadTermsMap,
        resolveCriterionLabel: resolveCriterionLabel,
        validateOutcomeAffordances: validateOutcomeAffordances,
        resolveOutcomeCriteria: resolveOutcomeCriteria,
        readSelfAssessments: readSelfAssessments,
        saveSelfAssessment: saveSelfAssessment,
        buildRevisionViewModel: buildRevisionViewModel,
        startPracticeFromOutcome: startPracticeFromOutcome,
        buildSelfAssessmentCardModel: buildSelfAssessmentCardModel,
        buildHonestyAudit: buildHonestyAudit,
        renderRevisionPanel: renderRevisionPanel,
        openSelfAssessmentCard: openSelfAssessmentCard,
        renderFromStore: renderFromStore,
        renderError: renderError,
        clearError: clearError,
        init: init
    };
    root.SimRevision = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
