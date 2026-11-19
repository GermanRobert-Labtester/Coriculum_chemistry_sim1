"use strict";
/* N23 — classification and feedback assembly.
 *
 * This module is the second half of the N23 grading layer. It consumes a
 * graded CORE record (the shape frozen in docs/GRADING_FORMAT.md §4, with
 * `feedback: null`) and the N23 classification island, and produces:
 *
 *   - a FeedbackRecord (§5) that names the error model, cites the rule that
 *     binds it, and carries resolvable remediation links;
 *   - a coverage table for the classification sweep and the build gate;
 *   - the §8 score-report DOM stub for #rezultati.
 *
 * What this module deliberately does NOT do:
 *   - it never re-derives a tolerance, a unit factor or a plausibility bound;
 *   - it never calls a grading engine and never re-scores a criterion;
 *   - it never reads a learner's wording; the only text it copies is the raw
 *     payload it preserves byte-for-byte for the invalid state;
 *   - it never invents learner-facing copy: every visible string is a
 *     #sim-terms key that must resolve, or the copied raw input.
 *
 * N09 gap (frozen, visible): no misconception registry exists in this
 * workspace. The classification island is N23-authored PROPOSED policy over
 * the frozen engine vocabularies; its priority field is authored here because
 * the roadmap's registry priority field does not exist yet.
 */
(function (root) {
    'use strict';
    /* ------------------------------------------------------------- contracts */
    const ISLAND_ID = 'sim-feedback-classification';
    const DOC_ELEMENT_ID = 'sim-feedback-classification';
    const TERMS_ELEMENT_ID = 'sim-terms';
    const CHAINS_ELEMENT_ID = 'sim-chains';
    const CARDS_ELEMENT_ID = 'sim-method-cards';
    /* --------------------------------------------------------------- errors */
    class FeedbackError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'FeedbackError';
            this.code = code;
            this.details = details || {};
        }
    }
    const ERRORS = [
        'E_FEEDBACK_CLASSIFICATION_INVALID',
        'E_FEEDBACK_UNMAPPED',
        'E_FEEDBACK_REMEDIATION_UNRESOLVED',
        'E_FEEDBACK_RECORD_INVALID',
    ];
    function fail(code, message, details) {
        throw new FeedbackError(code, message, details);
    }
    /* ------------------------------------------------------------ SHA-256 */
    /*
     * Compact SHA-256 (FIPS 180-4) with the same shape as the hash used by
     * src/figure-framework.js (sha256Utf8). Kept local on purpose: the feedback
     * module must digest its own canonical record without depending on any
     * other runtime module being loaded first. Algorithm attributed to FIPS
     * 180-4; rounding constants are the published first 32 bits of the fractional
     * parts of the cube roots of the first 64 primes.
     */
    const SHA256_K = [
        1116352408, 1899447441, -1245643825, -373957723, 961987163, 1508970993,
        -1841331548, -1424204075, -670586216, 310598401, 607225278, 1426881987,
        1925078388, -2132889090, -1680079193, -1046744716, -459576895, -272742522,
        264347078, 604807628, 770255983, 1249150122, 1555081692, 1996064986,
        -1740746414, -1473132947, -1341970488, -1084653625, -958395405, -710438585,
        113926993, 338241895, 666307205, 773529912, 1294757372, 1396182291,
        1695183700, 1986661051, -2117940946, -1838011259, -1564481375, -1474664885,
        -1035236496, -949202525, -778901479, -694614492, -200395387, 275423344,
        430227734, 506948616, 659060556, 883997877, 958139571, 1322822218,
        1537002063, 1747873779, 1955562222, 2024104815, -2067236844, -1933114872,
        -1866530822, -1538233109, -1090935817, -965641998,
    ];
    function sha256(text) {
        const H = [1779033703, -1150833019, 1013904242, -1521486534,
            1359893119, -1694144372, 528734635, 1541459225];
        const bytes = [];
        let i;
        let c;
        for (i = 0; i < text.length; i += 1) {
            c = text.charCodeAt(i);
            if (c < 128) {
                bytes.push(c);
            }
            else if (c < 2048) {
                bytes.push(192 | (c >> 6), 128 | (c & 63));
            }
            else if (c >= 0xd800 && c <= 0xdbff && i + 1 < text.length) {
                c = 0x10000 + (((c & 0x3ff) << 10) | (text.charCodeAt(++i) & 0x3ff));
                bytes.push(240 | (c >> 18), 128 | ((c >> 12) & 63), 128 | ((c >> 6) & 63), 128 | (c & 63));
            }
            else {
                bytes.push(224 | (c >> 12), 128 | ((c >> 6) & 63), 128 | (c & 63));
            }
        }
        const bitLen = bytes.length * 8;
        bytes.push(0x80);
        while ((bytes.length % 64) !== 56) {
            bytes.push(0);
        }
        const hi = Math.floor(bitLen / 0x100000000);
        const lo = bitLen >>> 0;
        bytes.push((hi >>> 24) & 255, (hi >>> 16) & 255, (hi >>> 8) & 255, hi & 255, (lo >>> 24) & 255, (lo >>> 16) & 255, (lo >>> 8) & 255, lo & 255);
        const w = new Array(64);
        function r(x, n) { return (x >>> n) | (x << (32 - n)); }
        for (i = 0; i < bytes.length; i += 64) {
            for (let t = 0; t < 16; t += 1) {
                w[t] = (bytes[i + t * 4] << 24) | (bytes[i + t * 4 + 1] << 16) |
                    (bytes[i + t * 4 + 2] << 8) | bytes[i + t * 4 + 3];
            }
            for (let t = 16; t < 64; t += 1) {
                const s0 = r(w[t - 15], 7) ^ r(w[t - 15], 18) ^ (w[t - 15] >>> 3);
                const s1 = r(w[t - 2], 17) ^ r(w[t - 2], 19) ^ (w[t - 2] >>> 10);
                w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0;
            }
            let a = H[0];
            let b = H[1];
            let cc = H[2];
            let d = H[3];
            let e = H[4];
            let f = H[5];
            let g = H[6];
            let h = H[7];
            for (let t = 0; t < 64; t += 1) {
                const S1 = r(e, 6) ^ r(e, 11) ^ r(e, 25);
                const ch = (e & f) ^ ((~e) & g);
                const temp1 = (h + S1 + ch + SHA256_K[t] + w[t]) | 0;
                const S0 = r(a, 2) ^ r(a, 13) ^ r(a, 22);
                const maj = (a & b) ^ (a & cc) ^ (b & cc);
                const temp2 = (S0 + maj) | 0;
                h = g;
                g = f;
                f = e;
                e = (d + temp1) | 0;
                d = cc;
                cc = b;
                b = a;
                a = (temp1 + temp2) | 0;
            }
            H[0] = (H[0] + a) | 0;
            H[1] = (H[1] + b) | 0;
            H[2] = (H[2] + cc) | 0;
            H[3] = (H[3] + d) | 0;
            H[4] = (H[4] + e) | 0;
            H[5] = (H[5] + f) | 0;
            H[6] = (H[6] + g) | 0;
            H[7] = (H[7] + h) | 0;
        }
        let hex = '';
        for (i = 0; i < 8; i += 1) {
            hex += ('00000000' + (H[i] >>> 0).toString(16)).slice(-8);
        }
        return hex;
    }
    /* --------------------------------------------------------- canonical JSON */
    /*
     * N04 serialization rule: sorted keys, no insignificant whitespace, UTF-8.
     * The module emits the same text Python's
     * `json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))`
     * produces for a value without non-finite numbers, which is what the
     * classification island and the feedback record contain.
     */
    function canonical(value) {
        if (value === null || value === undefined) {
            return 'null';
        }
        if (typeof value === 'boolean') {
            return value ? 'true' : 'false';
        }
        if (typeof value === 'number') {
            if (!isFinite(value)) {
                fail('E_FEEDBACK_RECORD_INVALID', 'Canonical JSON refuses a non-finite number.', {});
            }
            return String(value);
        }
        if (typeof value === 'string') {
            return JSON.stringify(value);
        }
        if (Array.isArray(value)) {
            return '[' + value.map(function (item) { return canonical(item); }).join(',') + ']';
        }
        if (typeof value === 'object') {
            const record = value;
            const keys = Object.keys(record).filter(function (key) {
                return record[key] !== undefined;
            }).sort();
            return '{' + keys.map(function (key) {
                return JSON.stringify(key) + ':' + canonical(record[key]);
            }).join(',') + '}';
        }
        return 'null';
    }
    function digestOf(value) { return sha256(canonical(value)); }
    /* ------------------------------------------------------------- documents */
    function asDocument(source) {
        if (!source) {
            return null;
        }
        const candidate = source;
        if (typeof candidate.getElementById !== 'function') {
            return null;
        }
        return candidate;
    }
    function readIslandText(doc, id) {
        if (!doc) {
            return null;
        }
        const node = doc.getElementById(id);
        if (!node) {
            return null;
        }
        const raw = node.textContent !== undefined ? node.textContent : node.innerText;
        if (typeof raw !== 'string' || !raw.trim()) {
            return null;
        }
        return raw;
    }
    function isClassificationDoc(value) {
        if (!value || typeof value !== 'object') {
            return false;
        }
        const candidate = value;
        return candidate.island_id === ISLAND_ID && Array.isArray(candidate.mapping);
    }
    function requireString(value, field) {
        if (typeof value !== 'string' || !value) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'Field ' + field + ' must be a non-empty string.', { field: field });
        }
        return value;
    }
    function requireStringArray(value, field) {
        if (!Array.isArray(value)) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'Field ' + field + ' must be an array.', { field: field });
        }
        const out = [];
        for (let i = 0; i < value.length; i += 1) {
            out.push(requireString(value[i], field + '[' + i + ']'));
        }
        return out;
    }
    const MATCH_KINDS = { signature: true, error_class: true, slot_state: true };
    const CITE_KINDS = {
        conventions_ref: true, engine_rule: true, graph_rule: true, contract_rule: true,
    };
    function validateClassification(doc) {
        if (doc.schema_version !== 1) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'schema_version must be 1.', { field: 'schema_version' });
        }
        if (doc.island_id !== ISLAND_ID) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'island_id mismatch.', { field: 'island_id', value: doc.island_id });
        }
        requireString(doc.owner, 'owner');
        requireString(doc.epistemic_note, 'epistemic_note');
        const ordering = doc.ordering_rule;
        if (!ordering || ordering.rule !== 'priority-ascending-then-match_value' || ordering.proposed !== true) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'ordering_rule must declare the proposed priority rule.', { field: 'ordering_rule' });
        }
        requireString(ordering.n09_gap_notice_lv, 'ordering_rule.n09_gap_notice_lv');
        if (!doc.assembly_rules || !Array.isArray(doc.assembly_rules.resolution_precedence)) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'assembly_rules.resolution_precedence is required.', { field: 'assembly_rules.resolution_precedence' });
        }
        const resolution = doc.remediation_resolution;
        if (!resolution || resolution.null_chain_allowed !== true) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'remediation_resolution.null_chain_allowed must be true.', { field: 'remediation_resolution' });
        }
        requireStringArray(resolution.concept_ids_must_resolve_in, 'remediation_resolution.concept_ids_must_resolve_in');
        requireStringArray(resolution.chain_ids_must_resolve_in, 'remediation_resolution.chain_ids_must_resolve_in');
        if (!doc.unmapped_rule || doc.unmapped_rule.id !== 'E_FEEDBACK_UNMAPPED') {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'unmapped_rule must name E_FEEDBACK_UNMAPPED.', { field: 'unmapped_rule' });
        }
        const render = doc.render_contract;
        if (!render || render.root !== 'section.score-report' || !render.verdict_labels || !render.state_labels) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'render_contract is incomplete.', { field: 'render_contract' });
        }
        if (!Array.isArray(doc.mapping) || !doc.mapping.length) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'mapping must be a non-empty array.', { field: 'mapping' });
        }
        const seen = {};
        for (let i = 0; i < doc.mapping.length; i += 1) {
            const entry = doc.mapping[i];
            const where = 'mapping[' + i + ']';
            if (!entry || typeof entry !== 'object') {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + ' must be an object.', { field: where });
            }
            if (!MATCH_KINDS[entry.match_kind]) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.match_kind is not declared.', { field: where + '.match_kind', value: entry.match_kind });
            }
            const value = requireString(entry.match_value, where + '.match_value');
            const key = entry.match_kind + '\u0000' + value;
            if (seen[key]) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'Duplicate mapping for ' + entry.match_kind + ' ' + value + '.', { field: where, match_kind: entry.match_kind, match_value: value });
            }
            seen[key] = true;
            const nameRef = entry.misconception_name;
            if (!nameRef || typeof nameRef !== 'object') {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.misconception_name is required.', { field: where + '.misconception_name' });
            }
            requireString(nameRef.island, where + '.misconception_name.island');
            requireString(nameRef.field, where + '.misconception_name.field');
            if (nameRef.declared_text_lv !== null && typeof nameRef.declared_text_lv !== 'string') {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.misconception_name.declared_text_lv must be a string or null.', { field: where + '.misconception_name.declared_text_lv' });
            }
            requireString(entry.feedback_key, where + '.feedback_key');
            if (!Array.isArray(entry.citations)) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.citations must be an array.', { field: where + '.citations' });
            }
            for (let c = 0; c < entry.citations.length; c += 1) {
                const citation = entry.citations[c];
                if (!citation || !CITE_KINDS[citation.kind] || typeof citation.id !== 'string' || !citation.id) {
                    fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.citations[' + c + '] is not a declared citation.', { field: where + '.citations[' + c + ']' });
                }
            }
            if (!entry.remediation || typeof entry.remediation !== 'object') {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.remediation is required.', { field: where + '.remediation' });
            }
            requireStringArray(entry.remediation.concept_ids, where + '.remediation.concept_ids');
            requireStringArray(entry.remediation.chain_ids, where + '.remediation.chain_ids');
            if (typeof entry.priority !== 'number' || !isFinite(entry.priority) || Math.floor(entry.priority) !== entry.priority) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', where + '.priority must be an integer.', { field: where + '.priority' });
            }
            requireString(entry.specificity_note_lv, where + '.specificity_note_lv');
        }
    }
    let digestMemo = null;
    function loadClassification(source) {
        let doc = source;
        if (!isClassificationDoc(doc)) {
            const asDoc = asDocument(source);
            const text = readIslandText(asDoc, DOC_ELEMENT_ID);
            if (text === null) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'No #' + DOC_ELEMENT_ID + ' island was supplied.', { field: 'doc', island_id: ISLAND_ID });
            }
            try {
                doc = JSON.parse(text);
            }
            catch (error) {
                fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'The classification island holds broken JSON.', { field: 'doc', island_id: ISLAND_ID });
            }
        }
        const classification = doc;
        validateClassification(classification);
        if (digestMemo && digestMemo.ref === classification) {
            return { classification: classification, digest: digestMemo.digest };
        }
        const digest = digestOf(classification);
        digestMemo = { ref: classification, digest: digest };
        setRenderContract(classification.render_contract);
        return { classification: classification, digest: digest };
    }
    /* -------------------------------------------------------------- indexing */
    const indexMemo = [];
    function indexOf(classification) {
        for (let i = 0; i < indexMemo.length; i += 1) {
            if (indexMemo[i].ref === classification) {
                return indexMemo[i].index;
            }
        }
        const byKey = {};
        for (let i = 0; i < classification.mapping.length; i += 1) {
            const entry = classification.mapping[i];
            byKey[entry.match_kind + '\u0000' + entry.match_value] = entry;
        }
        const index = { entries: classification.mapping.slice(), byKey: byKey };
        indexMemo.unshift({ ref: classification, index: index });
        if (indexMemo.length > 4) {
            indexMemo.pop();
        }
        return index;
    }
    function lookup(index, kind, value) {
        const entry = index.byKey[kind + '\u0000' + value];
        return entry === undefined ? null : entry;
    }
    /* ---------------------------------------------------------------- context */
    function classificationFromContext(context) {
        if (context.classification) {
            const cached = digestMemo && digestMemo.ref === context.classification
                ? digestMemo.digest : digestOf(context.classification);
            validateClassification(context.classification);
            digestMemo = { ref: context.classification, digest: cached };
            setRenderContract(context.classification.render_contract);
            return { classification: context.classification, digest: cached };
        }
        return loadClassification(context.doc);
    }
    function termsFromContext(context) {
        const direct = context.terms || context.termsMap;
        if (direct && typeof direct === 'object') {
            return direct;
        }
        const doc = asDocument(context.doc);
        const text = readIslandText(doc, TERMS_ELEMENT_ID);
        if (text === null) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'No terms map was supplied to the feedback module.', { field: 'terms', island_id: TERMS_ELEMENT_ID });
        }
        let island;
        try {
            island = JSON.parse(text);
        }
        catch (error) {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'The terms island holds broken JSON.', { field: 'terms' });
        }
        const map = {};
        const list = island.terms || [];
        for (let i = 0; i < list.length; i += 1) {
            if (typeof list[i].key === 'string' && typeof list[i].text_lv === 'string') {
                map[list[i].key] = list[i].text_lv;
            }
        }
        return map;
    }
    function termText(terms, key, field) {
        const text = terms[key];
        if (typeof text !== 'string') {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'Term key ' + key + ' does not resolve in #sim-terms.', { field: field, key: key });
        }
        return text;
    }
    function loadTermsMap(source) {
        if (source && typeof source === 'object') {
            const candidate = source;
            if (candidate.byKey && typeof candidate.byKey === 'object') {
                const byKey = candidate.byKey;
                const out = {};
                const keys = Object.keys(byKey);
                for (let i = 0; i < keys.length; i += 1) {
                    const entry = byKey[keys[i]];
                    if (entry && typeof (entry.primary_lv || entry.text_lv) === 'string') {
                        out[keys[i]] = String(entry.primary_lv || entry.text_lv);
                    }
                }
                return out;
            }
            if (typeof candidate.getElementById === 'function') {
                return termsFromContext({ doc: source });
            }
            return candidate;
        }
        return termsFromContext({ doc: source });
    }
    function criterionLabel(criterionId, termsSource) {
        const id = typeof criterionId === 'string' ? criterionId : String(criterionId || '');
        const map = loadTermsMap(termsSource);
        const key = 'feedback.criterion.' + id;
        const text = map[key];
        if (typeof text === 'string' && text.length > 0) {
            return text;
        }
        return id;
    }
    function registriesFromContext(context) {
        if (context.remediationRegistries) {
            return context.remediationRegistries;
        }
        const doc = asDocument(context.doc);
        if (!doc) {
            return null;
        }
        const out = {};
        let any = false;
        const chainsText = readIslandText(doc, CHAINS_ELEMENT_ID);
        if (chainsText !== null) {
            try {
                const island = JSON.parse(chainsText);
                out.chain_ids = (island.chains || []).map(function (chain) { return String(chain.id); });
                any = true;
            }
            catch (error) { /* a broken island is not a registry; the build gate reports it */ }
        }
        const cardsText = readIslandText(doc, CARDS_ELEMENT_ID);
        if (cardsText !== null) {
            try {
                const island = JSON.parse(cardsText);
                const cardMap = {};
                (island.cards || []).forEach(function (card) {
                    cardMap[String(card.card_id)] = (card.steps || []).map(function (step) { return String(step.step_id); });
                });
                out.method_cards = cardMap;
                any = true;
            }
            catch (error) { /* same */ }
        }
        return any ? out : null;
    }
    function namesFromContext(context) {
        const taxonomy = {};
        const registryMap = {};
        const names = context.classificationNames;
        if (!names) {
            return { taxonomy: taxonomy, registry: registryMap };
        }
        const classes = names.engine_taxonomy_classes || [];
        for (let i = 0; i < classes.length; i += 1) {
            const row = classes[i];
            if (typeof row.id === 'string' && typeof row.name_lv === 'string') {
                taxonomy[row.id] = row.name_lv;
            }
            if (typeof row.signature === 'string' && typeof row.name_lv === 'string') {
                taxonomy[row.signature] = row.name_lv;
            }
        }
        const sigs = names.method_signature_registry || [];
        for (let i = 0; i < sigs.length; i += 1) {
            const row = sigs[i];
            if (typeof row.signature === 'string' && typeof row.note_lv === 'string') {
                registryMap[row.signature] = row.note_lv;
            }
        }
        return { taxonomy: taxonomy, registry: registryMap };
    }
    /* ------------------------------------------------------------- utilities */
    function pushUnique(list, seen, value) {
        if (!seen[value]) {
            seen[value] = true;
            list.push(value);
        }
    }
    function numberOr(value, fallback) {
        return typeof value === 'number' && isFinite(value) ? value : fallback;
    }
    function sumCriteria(criteria, field) {
        let total = 0;
        for (let i = 0; i < criteria.length; i += 1) {
            const raw = criteria[i][field];
            if (typeof raw === 'number' && isFinite(raw)) {
                total += raw;
            }
        }
        return total;
    }
    function isStateFamily(rules, value) {
        const list = rules.state_families || [];
        for (let i = 0; i < list.length; i += 1) {
            if (list[i] === value) {
                return true;
            }
        }
        return false;
    }
    function isNonCorrect(slot) {
        if (slot.state !== 'graded') {
            return true;
        }
        return String(slot.verdict_class || 'NONE') !== 'correct';
    }
    const EMPTY_BOUND_POLICY = {
        apply_states: [], apply_verdicts: [], skip_error_classes: [], skip_signature_families: [],
    };
    function boundSignaturePolicy(rules) {
        const raw = rules['bound_signature_policy'];
        if (!raw || typeof raw !== 'object') {
            return EMPTY_BOUND_POLICY;
        }
        const policy = raw;
        const readList = function (field) {
            const value = policy[field];
            if (!Array.isArray(value)) {
                return [];
            }
            return value.map(function (item) { return String(item); });
        };
        return {
            apply_states: readList('apply_states'),
            apply_verdicts: readList('apply_verdicts'),
            skip_error_classes: readList('skip_error_classes'),
            skip_signature_families: readList('skip_signature_families'),
        };
    }
    function listContains(list, value) {
        for (let i = 0; i < list.length; i += 1) {
            if (list[i] === value) {
                return true;
            }
        }
        return false;
    }
    function stringListFrom(value) {
        if (!Array.isArray(value)) {
            return [];
        }
        return value.map(function (item) { return String(item); });
    }
    function engineSignatureAlias(rules, error) {
        const raw = rules['engine_signature_alias_rule'];
        if (!raw || typeof raw !== 'object') {
            return [];
        }
        const rule = raw;
        if (stringListFrom(rule['suppressed_for_error_classes']).indexOf(error) === -1) {
            return [];
        }
        return stringListFrom(rule['alias_signatures']);
    }
    function genericCopyKeys(rules) {
        return stringListFrom(rules['generic_copy_keys']);
    }
    function boundSignaturesApply(rules, slot, verdict, error) {
        const policy = boundSignaturePolicy(rules);
        if (!policy.apply_states.length && !policy.apply_verdicts.length) {
            return false;
        }
        if (policy.apply_states.length && !listContains(policy.apply_states, String(slot.state))) {
            return false;
        }
        if (policy.apply_verdicts.length && !listContains(policy.apply_verdicts, verdict)) {
            return false;
        }
        if (error && listContains(policy.skip_error_classes, error)) {
            return false;
        }
        if (!error && listContains(policy.skip_error_classes, 'NONE')) {
            return false;
        }
        return true;
    }
    function nameFor(entry, names) {
        if (entry.match_kind === 'slot_state' || entry.match_value === 'NONE') {
            return null;
        }
        const ref = entry.misconception_name;
        if (ref.island === 'engine_taxonomy') {
            const resolved = names.taxonomy[entry.match_value];
            if (typeof resolved === 'string') {
                return resolved;
            }
        }
        else if (ref.island === 'method_engine_contract') {
            const resolved = names.registry[entry.match_value];
            if (typeof resolved === 'string') {
                return resolved;
            }
        }
        return ref.declared_text_lv === null ? null : ref.declared_text_lv;
    }
    function newRemediationState() {
        return { concepts: [], conceptSeen: {}, chains: [], chainSeen: {} };
    }
    function addMappingRemediation(state, entry) {
        for (let i = 0; i < entry.remediation.concept_ids.length; i += 1) {
            pushUnique(state.concepts, state.conceptSeen, entry.remediation.concept_ids[i]);
        }
        for (let i = 0; i < entry.remediation.chain_ids.length; i += 1) {
            pushUnique(state.chains, state.chainSeen, entry.remediation.chain_ids[i]);
        }
    }
    function addOutcomes(state, slot) {
        const outcomes = slot.outcome_ids || [];
        for (let i = 0; i < outcomes.length; i += 1) {
            pushUnique(state.concepts, state.conceptSeen, String(outcomes[i]));
        }
    }
    function assertResolvable(registries, state, methodCard, slotId) {
        if (!registries) {
            return;
        }
        if (registries.concept_ids) {
            const known = {};
            registries.concept_ids.forEach(function (id) { known[id] = true; });
            for (let i = 0; i < state.concepts.length; i += 1) {
                if (!known[state.concepts[i]]) {
                    fail('E_FEEDBACK_REMEDIATION_UNRESOLVED', 'Concept id ' + state.concepts[i] + ' does not resolve.', { slot_id: slotId, kind: 'concept_id', id: state.concepts[i] });
                }
            }
        }
        if (registries.chain_ids) {
            const known = {};
            registries.chain_ids.forEach(function (id) { known[id] = true; });
            for (let i = 0; i < state.chains.length; i += 1) {
                if (!known[state.chains[i]]) {
                    fail('E_FEEDBACK_REMEDIATION_UNRESOLVED', 'Chain id ' + state.chains[i] + ' does not resolve.', { slot_id: slotId, kind: 'chain_id', id: state.chains[i] });
                }
            }
        }
        if (methodCard && methodCard.card_id !== null && registries.method_cards) {
            const steps = registries.method_cards[methodCard.card_id];
            if (!steps) {
                fail('E_FEEDBACK_REMEDIATION_UNRESOLVED', 'Method card ' + methodCard.card_id + ' does not resolve.', { slot_id: slotId, kind: 'card_id', id: methodCard.card_id });
            }
            if (methodCard.step_id !== null && steps.indexOf(methodCard.step_id) === -1) {
                fail('E_FEEDBACK_REMEDIATION_UNRESOLVED', 'Step ' + methodCard.step_id + ' does not resolve in ' + methodCard.card_id + '.', { slot_id: slotId, kind: 'step_id', id: methodCard.step_id, card_id: methodCard.card_id });
            }
        }
    }
    function makeItem(slot, level, criterionId, entry, signatureId, names, terms, registries, methodCard, note, includeOutcomes, keyOverride, errorClass, verdictClass) {
        const state = newRemediationState();
        addMappingRemediation(state, entry);
        if (includeOutcomes) {
            addOutcomes(state, slot);
        }
        assertResolvable(registries, state, methodCard, slot.slot_id);
        const key = keyOverride === null ? entry.feedback_key : keyOverride;
        return {
            slot_id: slot.slot_id,
            level: level,
            criterion_id: criterionId,
            verdict_class: verdictClass,
            error_class: errorClass,
            signature_id: signatureId,
            misconception_name: nameFor(entry, names),
            feedback_key: key,
            feedback_text: termText(terms, key, 'mapping.feedback_key'),
            citations: entry.citations.map(function (citation) {
                return { kind: citation.kind, id: citation.id };
            }),
            remediation: {
                concept_ids: state.concepts.slice().sort(),
                chain_ids: state.chains.slice().sort(),
                method_card: methodCard,
                note: note,
            },
            priority: entry.priority,
        };
    }
    function requireEntry(index, kind, value, slotId) {
        const entry = lookup(index, kind, value);
        if (!entry) {
            fail('E_FEEDBACK_UNMAPPED', 'No classification entry for ' + kind + ' ' + value + ' (slot ' + slotId + ').', { slot_id: slotId, match_kind: kind, match_value: value });
        }
        return entry;
    }
    function pendingKeyFor(criterion, rules) {
        const table = (rules.pending_label_rule || {});
        const grading = String(criterion.grading || 'self');
        const key = table[grading] || table['human-review'];
        return key === undefined ? 'feedback.pending_review' : key;
    }
    function sortItems(items) {
        const indexed = items.map(function (item, position) {
            return { item: item, position: position };
        });
        indexed.sort(function (a, b) {
            if (a.item.priority !== b.item.priority) {
                return a.item.priority - b.item.priority;
            }
            const av = a.item.signature_id === null ? '' : a.item.signature_id;
            const bv = b.item.signature_id === null ? '' : b.item.signature_id;
            if (av !== bv) {
                return av < bv ? -1 : 1;
            }
            if (a.item.feedback_key !== b.item.feedback_key) {
                return a.item.feedback_key < b.item.feedback_key ? -1 : 1;
            }
            return a.position - b.position;
        });
        return indexed.map(function (row) { return row.item; });
    }
    function assemble(coreRecord, context) {
        if (!coreRecord || !Array.isArray(coreRecord.slots)) {
            fail('E_FEEDBACK_RECORD_INVALID', 'A core record with a slots array is required.', { field: 'slots' });
        }
        const loaded = classificationFromContext(context || {});
        const classification = loaded.classification;
        const index = indexOf(classification);
        const terms = termsFromContext(context || {});
        const names = namesFromContext(context || {});
        const registries = registriesFromContext(context || {});
        const rules = classification.assembly_rules;
        const items = [];
        for (let s = 0; s < coreRecord.slots.length; s += 1) {
            const slot = coreRecord.slots[s];
            if (!slot || typeof slot.slot_id !== 'string' || !slot.slot_id) {
                fail('E_FEEDBACK_RECORD_INVALID', 'Slot at index ' + s + ' has no slot_id.', { field: 'slots[' + s + ']' });
            }
            if (typeof slot.state !== 'string' || !slot.state) {
                fail('E_FEEDBACK_RECORD_INVALID', 'Slot ' + slot.slot_id + ' has no state.', { slot_id: slot.slot_id });
            }
            const criteria = Array.isArray(slot.criteria) ? slot.criteria : [];
            let hasPending = false;
            for (let c = 0; c < criteria.length; c += 1) {
                if (String(criteria[c].status || '') === 'pending') {
                    hasPending = true;
                    break;
                }
            }
            if (!isNonCorrect(slot) && !hasPending) {
                continue;
            }
            const slotItems = [];
            /* ---- task level ---- */
            const signatures = [];
            const signatureSeen = {};
            const verdict = String(slot.verdict_class || 'NONE');
            const slotError = slot.error_class === undefined || slot.error_class === null ? '' : String(slot.error_class);
            const alias = engineSignatureAlias(rules, slotError);
            for (let c = 0; c < criteria.length; c += 1) {
                const list = criteria[c].signature_ids || [];
                for (let i = 0; i < list.length; i += 1) {
                    const value = String(list[i]);
                    if (alias.indexOf(value) === -1) {
                        pushUnique(signatures, signatureSeen, value);
                    }
                }
            }
            let errorEntry = null;
            if (slotError && slotError !== 'NONE' && !isStateFamily(rules, slotError)) {
                errorEntry = requireEntry(index, 'error_class', slotError, slot.slot_id);
            }
            if (boundSignaturesApply(rules, slot, verdict, slotError)) {
                const policy = boundSignaturePolicy(rules);
                const skip = policy.skip_signature_families || [];
                const bound = slot.misconception_signatures || [];
                for (let i = 0; i < bound.length; i += 1) {
                    const value = String(bound[i]);
                    if (skip.indexOf(value) === -1) {
                        pushUnique(signatures, signatureSeen, value);
                    }
                }
            }
            const pendingOnly = signatures.length === 0 &&
                (verdict === 'pending_self_assessment' || verdict === 'auto_passed_pending_review' ||
                    (verdict === 'correct' && hasPending)) &&
                (slotError === '' || slotError === 'NONE');
            /* The pending label is carried by the criterion-level cards; a task-level
             * card would only repeat it (assembly_rules.pending_only_rule_lv). */
            if (pendingOnly) {
                /* no task item */
            }
            else if (signatures.length) {
                const usedKeys = [];
                for (let i = 0; i < signatures.length; i += 1) {
                    const entry = requireEntry(index, 'signature', signatures[i], slot.slot_id);
                    usedKeys.push(entry.feedback_key);
                    slotItems.push(makeItem(slot, 'task', null, entry, signatures[i], names, terms, registries, null, '', true, null, slot.error_class === undefined ? null : slot.error_class, slot.verdict_class === undefined ? null : slot.verdict_class));
                }
                /* The engine's own class stays visible when it carries copy of its own
                 * and no signature card already says the same thing. */
                if (errorEntry && genericCopyKeys(rules).indexOf(errorEntry.feedback_key) === -1 &&
                    usedKeys.indexOf(errorEntry.feedback_key) === -1) {
                    slotItems.push(makeItem(slot, 'task', null, errorEntry, null, names, terms, registries, null, '', true, null, slot.error_class === undefined ? null : slot.error_class, slot.verdict_class === undefined ? null : slot.verdict_class));
                }
            }
            else {
                const error = slot.error_class === undefined || slot.error_class === null ? '' : String(slot.error_class);
                let entry = null;
                let keyOverride = null;
                if (error && error !== 'NONE' && !isStateFamily(rules, error)) {
                    entry = requireEntry(index, 'error_class', error, slot.slot_id);
                }
                else if (verdict === 'pending_self_assessment' || verdict === 'auto_passed_pending_review') {
                    entry = requireEntry(index, 'slot_state', 'manual_pending', slot.slot_id);
                    let selfOnly = false;
                    for (let c = 0; c < criteria.length; c += 1) {
                        if (criteria[c].status === 'pending') {
                            selfOnly = String(criteria[c].grading || '') === 'self';
                            if (!selfOnly) {
                                break;
                            }
                        }
                    }
                    keyOverride = selfOnly ? 'feedback.self_assess' : 'feedback.pending_review';
                }
                else {
                    entry = requireEntry(index, 'slot_state', slot.state, slot.slot_id);
                }
                if (!entry) {
                    fail('E_FEEDBACK_UNMAPPED', 'Slot ' + slot.slot_id + ' is non-correct but carries neither a signature nor an error class.', { slot_id: slot.slot_id, match_kind: 'signature', match_value: '' });
                }
                slotItems.push(makeItem(slot, 'task', null, entry, null, names, terms, registries, null, '', entry.match_kind !== 'slot_state', keyOverride, slot.error_class === undefined ? null : slot.error_class, slot.verdict_class === undefined ? null : slot.verdict_class));
            }
            /* ---- criterion level ---- */
            if (slot.state === 'graded') {
                for (let c = 0; c < criteria.length; c += 1) {
                    const criterion = criteria[c];
                    const status = String(criterion.status || '');
                    if (status === 'pending') {
                        const entry = requireEntry(index, 'slot_state', 'manual_pending', slot.slot_id);
                        const key = pendingKeyFor(criterion, rules);
                        slotItems.push(makeItem(slot, 'criterion', criterion.criterion_id, entry, null, names, terms, registries, null, '', false, key, criterion.error_class === undefined ? null : criterion.error_class, criterion.verdict_class === undefined ? slot.verdict_class === undefined ? null : slot.verdict_class : criterion.verdict_class));
                        continue;
                    }
                    if (status !== 'denied') {
                        continue;
                    }
                    const remediationEntries = criterion.remediation_entries || [];
                    if (remediationEntries.length) {
                        for (let r = 0; r < remediationEntries.length; r += 1) {
                            const row = remediationEntries[r];
                            const signature = row.misconception_signature === undefined || row.misconception_signature === null
                                ? null : String(row.misconception_signature);
                            let entry;
                            if (signature !== null) {
                                entry = requireEntry(index, 'signature', signature, slot.slot_id);
                            }
                            else {
                                const slotError = slot.error_class === undefined || slot.error_class === null ? '' : String(slot.error_class);
                                if (slotError && slotError !== 'NONE' && !isStateFamily(rules, slotError)) {
                                    entry = requireEntry(index, 'error_class', slotError, slot.slot_id);
                                }
                                else {
                                    entry = requireEntry(index, 'slot_state', slot.state, slot.slot_id);
                                }
                            }
                            const cardId = row.card_id === undefined || row.card_id === null ? null : String(row.card_id);
                            const stepId = row.step_id === undefined || row.step_id === null ? null : String(row.step_id);
                            slotItems.push(makeItem(slot, 'criterion', criterion.criterion_id, entry, signature, names, terms, registries, { card_id: cardId, step_id: stepId }, String(row.note_lv || ''), true, null, criterion.error_class === undefined ? null : criterion.error_class, criterion.verdict_class === undefined ? slot.verdict_class === undefined ? null : slot.verdict_class : criterion.verdict_class));
                        }
                        continue;
                    }
                    const ownSignatures = [];
                    const ownSeen = {};
                    const list = criterion.signature_ids || [];
                    let novel = false;
                    for (let i = 0; i < list.length; i += 1) {
                        const value = String(list[i]);
                        if (alias.indexOf(value) !== -1) {
                            continue;
                        }
                        pushUnique(ownSignatures, ownSeen, value);
                        if (!signatureSeen[value]) {
                            novel = true;
                        }
                    }
                    if (novel) {
                        for (let i = 0; i < ownSignatures.length; i += 1) {
                            if (signatureSeen[ownSignatures[i]]) {
                                continue;
                            }
                            const entry = requireEntry(index, 'signature', ownSignatures[i], slot.slot_id);
                            slotItems.push(makeItem(slot, 'criterion', criterion.criterion_id, entry, ownSignatures[i], names, terms, registries, null, '', true, null, criterion.error_class === undefined ? null : criterion.error_class, criterion.verdict_class === undefined ? slot.verdict_class === undefined ? null : slot.verdict_class : criterion.verdict_class));
                        }
                        continue;
                    }
                    const criterionError = criterion.error_class === undefined || criterion.error_class === null
                        ? '' : String(criterion.error_class);
                    const slotError = slot.error_class === undefined || slot.error_class === null ? '' : String(slot.error_class);
                    if (criterionError && criterionError !== 'NONE' && criterionError !== slotError && !isStateFamily(rules, criterionError)) {
                        const entry = requireEntry(index, 'error_class', criterionError, slot.slot_id);
                        slotItems.push(makeItem(slot, 'criterion', criterion.criterion_id, entry, null, names, terms, registries, null, '', true, null, criterion.error_class === undefined ? null : criterion.error_class, criterion.verdict_class === undefined ? slot.verdict_class === undefined ? null : slot.verdict_class : criterion.verdict_class));
                    }
                }
            }
            const sorted = sortItems(slotItems);
            for (let i = 0; i < sorted.length; i += 1) {
                items.push(sorted[i]);
            }
        }
        /* §4 digest rule: the digest is computed over the record with its own
         * digest field removed, so the base object carries no digest property. */
        const base = {
            schema_version: 1,
            owner: 'N23',
            record_kind: 'feedback-record',
            classification_digest: loaded.digest,
            items: items,
            ordering_rule: classification.ordering_rule.rule,
            unmapped: [],
        };
        const record = base;
        record.digest = digestOf(base);
        return record;
    }
    function classificationTable(context) {
        const loaded = classificationFromContext(context || {});
        const classification = loaded.classification;
        const index = indexOf(classification);
        const registries = registriesFromContext(context || {});
        const names = namesFromContext(context || {});
        const rows = [];
        const byKind = { signature: 0, error_class: 0, slot_state: 0 };
        for (let i = 0; i < index.entries.length; i += 1) {
            const entry = index.entries[i];
            const state = newRemediationState();
            addMappingRemediation(state, entry);
            assertResolvable(registries, state, null, '<classification>');
            byKind[entry.match_kind] = (byKind[entry.match_kind] || 0) + 1;
            rows.push({
                match_kind: entry.match_kind,
                match_value: entry.match_value,
                feedback_key: entry.feedback_key,
                misconception_name: {
                    island: entry.misconception_name.island,
                    field: entry.misconception_name.field,
                    name: nameFor(entry, names),
                },
                remediation: {
                    concept_ids: state.concepts.slice().sort(),
                    chain_ids: state.chains.slice().sort(),
                },
                priority: entry.priority,
                specificity_note_lv: entry.specificity_note_lv,
            });
        }
        const unmapped = [];
        const required = context && context.requiredFamilies ? context.requiredFamilies : [];
        for (let i = 0; i < required.length; i += 1) {
            const key = required[i];
            if (!lookup(index, key.match_kind, key.match_value)) {
                unmapped.push({ match_kind: key.match_kind, match_value: key.match_value });
            }
        }
        return {
            schema_version: 1,
            island_id: ISLAND_ID,
            classification_digest: loaded.digest,
            ordering_rule: classification.ordering_rule.rule,
            counts: { total: rows.length, by_kind: byKind },
            rows: rows,
            unmapped: unmapped,
        };
    }
    /* ------------------------------------------------------------ render stub */
    function escapeHtml(value) {
        if (root.SimStore && typeof root.SimStore.escapeHtml === 'function') {
            return root.SimStore.escapeHtml(value);
        }
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
    function fillCopy(text, values) {
        return text.replace(/\{([a-z_]+)\}/gi, function (match, key) {
            const value = values[key];
            return value === undefined ? match : value;
        });
    }
    function jsonForDisplay(value) {
        try {
            return JSON.stringify(value === undefined ? null : value);
        }
        catch (error) {
            return String(value);
        }
    }
    function criterionErrorText(criterion) {
        const parts = [];
        const errorClass = criterion.error_class;
        const errors = criterion.errors || [];
        if (typeof errorClass === 'string' && errorClass && errorClass !== 'NONE') {
            let repeated = false;
            for (let i = 0; i < errors.length; i += 1) {
                if (errors[i].id === errorClass) {
                    repeated = true;
                    break;
                }
            }
            if (!repeated) {
                parts.push(errorClass);
            }
        }
        for (let i = 0; i < errors.length; i += 1) {
            const id = errors[i].id;
            const field = errors[i].field;
            if (typeof id === 'string' && id) {
                parts.push(field ? id + '@' + field : id);
            }
        }
        const missing = criterion.missing || [];
        for (let i = 0; i < missing.length; i += 1) {
            const field = missing[i].field;
            const name = missing[i].name;
            if (typeof field === 'string' && field) {
                parts.push(name ? field + '=' + name : field);
            }
        }
        return parts.join(', ');
    }
    function stateLabelFor(slot, render, terms) {
        const state = String(slot.state);
        if (state === 'graded') {
            const key = render.verdict_labels[String(slot.verdict_class || 'NONE')] || 'feedback.incorrect';
            return termText(terms, key, 'render_contract.verdict_labels');
        }
        const key = render.state_labels[state];
        if (key === undefined) {
            fail('E_FEEDBACK_RECORD_INVALID', 'Slot state ' + state + ' has no render label.', { state: state });
        }
        return termText(terms, key, 'render_contract.state_labels');
    }
    function buildScoreReport(fullRecord, termsMap) {
        if (!fullRecord || !Array.isArray(fullRecord.slots)) {
            fail('E_FEEDBACK_RECORD_INVALID', 'A full record with a slots array is required.', { field: 'slots' });
        }
        if (!termsMap || typeof termsMap !== 'object') {
            fail('E_FEEDBACK_CLASSIFICATION_INVALID', 'buildScoreReport needs the resolved #sim-terms map.', { field: 'termsMap' });
        }
        const terms = termsMap;
        const feedback = (fullRecord.feedback || {});
        const items = Array.isArray(feedback.items) ? feedback.items : [];
        const totals = fullRecord.totals || {};
        const slots = fullRecord.slots;
        const autoPoints = numberOr(totals.auto_points, 0);
        const autoMax = numberOr(totals.auto_max_points, 0);
        const pendingPoints = numberOr(totals.pending_external_points, 0);
        const pendingMax = numberOr(totals.pending_max_points, 0);
        const digest = typeof fullRecord.digest === 'string'
            ? String(fullRecord.digest) : '';
        const render = declaredRender === null ? DEFAULT_RENDER : declaredRender;
        const html = [];
        html.push('<section class="score-report" data-graded-digest="' + escapeHtml(digest) + '">');
        html.push('  <div class="score-totals">');
        html.push('    <p class="score-auto">' + escapeHtml(fillCopy(termText(terms, 'feedback.results.auto_total', 'render_contract.copy_keys'), { auto: String(autoPoints), auto_max: String(autoMax) })) + '</p>');
        html.push('    <p class="score-pending">' + escapeHtml(fillCopy(termText(terms, 'feedback.results.pending_total', 'render_contract.copy_keys'), { pending: String(pendingPoints), pending_max: String(pendingMax) })) + '</p>');
        html.push('    <p class="score-unblended-note">' + escapeHtml(termText(terms, 'feedback.results.unblended', 'render_contract.copy_keys')) + '</p>');
        html.push('    <p class="score-honesty-note">' + escapeHtml(termText(terms, 'feedback.results.honesty', 'render_contract.copy_keys')) + '</p>');
        html.push('  </div>');
        html.push('  <ul class="score-slots">');
        for (let s = 0; s < slots.length; s += 1) {
            const slot = slots[s];
            const criteria = Array.isArray(slot.criteria) ? slot.criteria : [];
            const task = slot.task || {};
            const slotAuto = numberOr(task.auto_points, sumCriteria(criteria, 'awarded_points'));
            const slotMax = numberOr(task.max_points, numberOr(slot.slot_points, 0));
            html.push('    <li class="score-slot" data-slot-id="' + escapeHtml(slot.slot_id) +
                '" data-state="' + escapeHtml(slot.state) + '">');
            html.push('      <div class="score-slot-row">');
            html.push('        <span class="score-slot-id">' + escapeHtml(slot.slot_id) + '</span>');
            html.push('        <span class="score-slot-points" data-auto="' + escapeHtml(String(slotAuto)) +
                '" data-pending="' + escapeHtml(String(numberOr(task.pending_points, 0))) + '">' +
                escapeHtml(String(slotAuto) + '/' + String(slotMax)) + '</span>');
            html.push('        <span class="score-slot-state">' +
                escapeHtml(stateLabelFor(slot, render, terms)) + '</span>');
            html.push('      </div>');
            html.push('      <details class="score-criteria">');
            html.push('        <summary>' + escapeHtml(termText(terms, 'feedback.results.criterion_disclosure', 'render_contract.copy_keys')) + '</summary>');
            html.push('        <table class="criteria-table">');
            html.push('          <tr><th>criterion_id</th><th>engine_binding</th><th>status</th>' +
                '<th>awarded/max</th><th>error</th></tr>');
            for (let c = 0; c < criteria.length; c += 1) {
                const criterion = criteria[c];
                const awarded = numberOr(criterion.awarded_points, 0);
                const max = numberOr(criterion.max_points, 0);
                const label = criterionLabel(criterion.criterion_id, terms);
                html.push('          <tr data-criterion-id="' + escapeHtml(criterion.criterion_id) + '">' +
                    '<td><span class="criterion-label">' + escapeHtml(label) + '</span></td>' +
                    '<td>' + escapeHtml(String(criterion.engine_binding || '')) + '</td>' +
                    '<td>' + escapeHtml(String(criterion.status || '')) + '</td>' +
                    '<td>' + escapeHtml(String(awarded) + '/' + String(max)) + '</td>' +
                    '<td>' + escapeHtml(criterionErrorText(criterion)) + '</td></tr>');
            }
            html.push('        </table>');
            if (slot.state === render.raw_preserved_only_state) {
                html.push('        <p class="score-raw">' + escapeHtml(fillCopy(termText(terms, 'feedback.results.raw_preserved', 'render_contract.copy_keys'), { raw: jsonForDisplay(slot.raw_input) })) + '</p>');
            }
            html.push('      </details>');
            html.push('      <div class="feedback-cards">');
            html.push('        <h4>' + escapeHtml(termText(terms, 'feedback.results.task_level', 'render_contract.copy_keys')) + '</h4>');
            for (let i = 0; i < items.length; i += 1) {
                const item = items[i];
                if (item.slot_id !== slot.slot_id) {
                    continue;
                }
                html.push('        <article class="feedback-card" data-level="' + escapeHtml(item.level) +
                    '" data-signature="' + escapeHtml(item.signature_id === null ? '' : item.signature_id) + '">');
                if (item.misconception_name !== null) {
                    html.push('          <p class="feedback-misconception">' + escapeHtml(fillCopy(termText(terms, 'feedback.results.misconception', 'render_contract.copy_keys'), { name: item.misconception_name })) + '</p>');
                }
                html.push('          <p class="feedback-text">' + escapeHtml(item.feedback_text) + '</p>');
                if (item.citations.length) {
                    const ids = item.citations.map(function (citation) { return citation.id; }).join(', ');
                    html.push('          <p class="feedback-citations">' + escapeHtml(termText(terms, 'feedback.citation_label', 'render_contract.copy_keys') + ': ' + ids) + '</p>');
                }
                const links = [];
                for (let k = 0; k < item.remediation.concept_ids.length; k += 1) {
                    const conceptId = item.remediation.concept_ids[k];
                    links.push('<a data-concept="' + escapeHtml(conceptId) + '">' + escapeHtml(conceptId) + '</a>');
                }
                for (let k = 0; k < item.remediation.chain_ids.length; k += 1) {
                    const chainId = item.remediation.chain_ids[k];
                    links.push('<a data-chain="' + escapeHtml(chainId) + '">' + escapeHtml(chainId) + '</a>');
                }
                if (item.remediation.method_card) {
                    const cardId = item.remediation.method_card.card_id === null ? '' : item.remediation.method_card.card_id;
                    const stepId = item.remediation.method_card.step_id === null ? '' : item.remediation.method_card.step_id;
                    if (cardId) {
                        const label = stepId ? cardId + ' · ' + stepId : cardId;
                        links.push('<a data-card="' + escapeHtml(cardId) + '" data-step="' + escapeHtml(stepId) + '">' +
                            escapeHtml(label) + '</a>');
                    }
                }
                if (links.length) {
                    html.push('          <p class="feedback-remediation">' + escapeHtml(termText(terms, 'feedback.results.remediation', 'render_contract.copy_keys')) + ' ' +
                        links.join(' | ') + '</p>');
                }
                html.push('        </article>');
            }
            html.push('      </div>');
            html.push('    </li>');
        }
        html.push('  </ul>');
        html.push('</section>');
        const text = html.join('\n');
        return { html: text, digest: sha256(text) };
    }
    /* The render contract lives in the classification island. buildScoreReport
     * takes a record and a terms map (the frozen §6 signature); when the record
     * carries the island-owning context, the module uses it. Otherwise the
     * declared §8 defaults are used, which is exactly what the contract fixes. */
    const DEFAULT_RENDER = {
        root: 'section.score-report',
        root_attributes: ['data-graded-digest'],
        blocks: [],
        copy_keys: [],
        verdict_labels: {
            correct: 'feedback.correct',
            partial: 'feedback.partial',
            incorrect: 'feedback.incorrect',
            pending_self_assessment: 'feedback.self_assess',
            auto_passed_pending_review: 'feedback.pending_review',
            not_assessed: 'feedback.error.out_of_domain',
        },
        state_labels: {
            invalid: 'feedback.results.malformed_zero',
            incomplete: 'feedback.results.incomplete_zero',
            unattempted: 'feedback.results.unattempted',
            manual_pending: 'feedback.pending_review',
        },
        honesty_note_once: true,
        unblended_totals: true,
        raw_preserved_only_state: 'invalid',
        remediation_attributes: ['data-concept', 'data-chain', 'data-card', 'data-step'],
        link_resolvers: {},
        escape_rule_lv: '',
        digest_rule: '',
        structure_note_lv: '',
    };
    let declaredRender = null;
    /* The island owns the render contract. Loading it makes §8 authoritative for
     * every later buildScoreReport call; the defaults above are the same §8
     * declarations and exist only for the degenerate call-before-load case. */
    function setRenderContract(render) { declaredRender = render; }
    /* ----------------------------------------------------------------- export */
    const api = {
        ISLAND_ID: ISLAND_ID,
        loadClassification: loadClassification,
        loadTermsMap: loadTermsMap,
        criterionLabel: criterionLabel,
        assemble: assemble,
        classificationTable: classificationTable,
        buildScoreReport: buildScoreReport,
        setRenderContract: setRenderContract,
        canonicalText: canonical,
        digestOf: digestOf,
        sha256: sha256,
        FeedbackError: FeedbackError,
        errors: ERRORS,
    };
    root.SimFeedback = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
