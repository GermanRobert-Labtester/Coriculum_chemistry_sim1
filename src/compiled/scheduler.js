"use strict";
/* N27 — Offline Leitner scheduler for spaced practice selection.
 *
 * Pure, deterministic day-granular Leitner box model and queue selection over
 * #sim-scheduler-policy, consuming N26 MasteryMap and N24/N26 availability.
 *
 * Epistemic & architectural boundaries:
 *   - Intervals, box mapping, queue cap, and selection rules are PROPOSED
 *     training policy (no official RSU schedule exists: UNDETERMINED).
 *   - Standard 3-box day-granular Leitner scheme; no third-party algorithm
 *     (Anki/SuperMemo/SM-2) is copied.
 *   - Day granularity only: pure selection consumes an explicit day/date or
 *     injected DayClock; runtime calls defaultDayClock() only for display.
 *   - Zero wall-clock millisecond APIs, zero network APIs, zero F10
 *     streaks/charts/gamification, and zero grading/key material in handoffs.
 */
(function (root) {
    'use strict';
    const ISLAND_ID = 'sim-scheduler-policy';
    const SCHEMA_VERSION = 1;
    const MASTERY_STATES = ['unseen', 'learning', 'near_mastered', 'mastered', 'needs_review'];
    const REASON_CODES = ['overdue', 'due_today', 'new', 'least_recently_practiced', 'unavailable'];
    const ERRORS = [
        'E_SCHEDULER_POLICY_INVALID',
        'E_SCHEDULER_INVALID_DATE',
        'E_SCHEDULER_UNKNOWN_STATE',
        'E_SCHEDULER_UNAVAILABLE_OUTCOME',
        'E_SCHEDULER_HANDOFF_INVALID'
    ];
    class SchedulerError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'SchedulerError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, SchedulerError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new SchedulerError(code, message, details);
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
                return fail('E_SCHEDULER_POLICY_INVALID', 'Kanoniālajā projektcijā nav atbalstīts bezgalīgs skaitlis.', {});
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
        return fail('E_SCHEDULER_POLICY_INVALID', 'Kanoniālajā projektcijā nav atbalstīta vērtība.', {
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
        const masteryApi = root.SimMastery;
        if (masteryApi && typeof masteryApi.digestValue === 'function') {
            return masteryApi.digestValue(value);
        }
        const storeApi = root.SimStore;
        if (storeApi && typeof storeApi.digestValue === 'function') {
            return storeApi.digestValue(value);
        }
        return sha256Fallback(canonicalText(value));
    }
    /* -------------------------------------------------------- day-clock API */
    function pad2(n) {
        return n < 10 ? '0' + String(n) : String(n);
    }
    function calendarToDay(year, month, day) {
        if (!isPositiveInt(year) || !isPositiveInt(month) || !isPositiveInt(day) || month > 12 || day > 31) {
            return fail('E_SCHEDULER_INVALID_DATE', 'Nederīgs kalendāra datums.', {
                year: year,
                month: month,
                day: day
            });
        }
        const utcMs = Date.UTC(year, month - 1, day);
        const check = new Date(utcMs);
        if (check.getUTCFullYear() !== year || check.getUTCMonth() + 1 !== month || check.getUTCDate() !== day) {
            return fail('E_SCHEDULER_INVALID_DATE', 'Nepastāvošs kalendāra datums.', {
                year: year,
                month: month,
                day: day
            });
        }
        return Math.floor(utcMs / 86400000);
    }
    function toDayNumber(dateInput) {
        if (typeof dateInput === 'number') {
            if (!isFinite(dateInput) || Math.floor(dateInput) !== dateInput) {
                return fail('E_SCHEDULER_INVALID_DATE', 'Dienas indeksam jābūt veselam skaitlim.', {
                    date: dateInput
                });
            }
            return dateInput;
        }
        if (typeof dateInput === 'string') {
            const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateInput.trim());
            if (!m) {
                return fail('E_SCHEDULER_INVALID_DATE', 'Datumam jābūt YYYY-MM-DD formātā.', {
                    date: dateInput
                });
            }
            return calendarToDay(parseInt(m[1], 10), parseInt(m[2], 10), parseInt(m[3], 10));
        }
        if (dateInput instanceof Date) {
            if (isNaN(dateInput.getTime())) {
                return fail('E_SCHEDULER_INVALID_DATE', 'Nederīgs Date objekts.', {});
            }
            return calendarToDay(dateInput.getFullYear(), dateInput.getMonth() + 1, dateInput.getDate());
        }
        return fail('E_SCHEDULER_INVALID_DATE', 'Trūkst derīga datuma vai dienas indeksa.', {
            date: dateInput
        });
    }
    function dayNumberToIso(dayNum) {
        if (!isFinite(dayNum) || Math.floor(dayNum) !== dayNum) {
            return fail('E_SCHEDULER_INVALID_DATE', 'Dienas indeksam jābūt veselam skaitlim.', { day: dayNum });
        }
        if (dayNum < 10000) {
            return 'day-' + String(dayNum);
        }
        const d = new Date(dayNum * 86400000);
        return String(d.getUTCFullYear()) + '-' + pad2(d.getUTCMonth() + 1) + '-' + pad2(d.getUTCDate());
    }
    function defaultDayClock() {
        return {
            todayDay: function () {
                const d = new Date();
                return calendarToDay(d.getFullYear(), d.getMonth() + 1, d.getDate());
            },
            todayIso: function () {
                const d = new Date();
                return String(d.getFullYear()) + '-' + pad2(d.getMonth() + 1) + '-' + pad2(d.getDate());
            },
            isInjected: false
        };
    }
    function createFixedDayClock(dateInput) {
        const fixedDay = toDayNumber(dateInput);
        const fixedIso = typeof dateInput === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateInput.trim())
            ? dateInput.trim()
            : dayNumberToIso(fixedDay);
        return {
            todayDay: function () { return fixedDay; },
            todayIso: function () { return fixedIso; },
            isInjected: true
        };
    }
    /* --------------------------------------------------- policy validation */
    function validatePolicy(rawPolicy) {
        const errors = [];
        const nonInc = [];
        if (!isObject(rawPolicy)) {
            return {
                valid: false,
                policy_id: '',
                queue_cap: 0,
                boxes: [],
                non_increasing_pairs: [],
                errors: ['Plānotāja politikai jābūt JSON objektam.']
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
            errors.push('Trūkst godīguma piezīmes honesty_note_lv.');
        }
        if (!Array.isArray(rawPolicy.predecessor_decisions) || rawPolicy.predecessor_decisions.length === 0) {
            errors.push('Trūkst atsauču uz priekšteča plāna lēmumiem (predecessor_decisions).');
        }
        const qCapObj = isObject(rawPolicy.queue_cap) ? rawPolicy.queue_cap : null;
        const qCapVal = qCapObj ? qCapObj.value : null;
        if (!isPositiveInt(qCapVal)) {
            errors.push('Rindas limitam (queue_cap.value) jābūt pozitīvam veselam skaitlim.');
        }
        else if (qCapObj && qCapObj.epistemic_label !== 'PROPOSED') {
            errors.push('queue_cap jābūt marķētam ar epistemic_label="PROPOSED".');
        }
        const rawBoxes = Array.isArray(rawPolicy.boxes) ? rawPolicy.boxes : [];
        const boxes = [];
        const byBoxNum = {};
        if (rawBoxes.length < 2) {
            errors.push('Politikā jādefinē vismaz divas Leitnera kastes (boxes).');
        }
        for (let i = 0; i < rawBoxes.length; i += 1) {
            const b = rawBoxes[i];
            if (!isObject(b) || !isPositiveInt(b.box)) {
                errors.push('Kastei indeksā ' + i + ' jābūt pozitīvam veselam numuram (box).');
                continue;
            }
            const bKey = String(b.box);
            if (has(byBoxNum, bKey)) {
                errors.push('Dublēts kastes numurs: box ' + b.box + '.');
                continue;
            }
            if (!isPositiveInt(b.interval_days)) {
                errors.push('Kastes box ' + b.box + ' interval_days jābūt pozitīvam veselam skaitlim.');
            }
            if (b.epistemic_label !== 'PROPOSED') {
                errors.push('Kastei box ' + b.box + ' jābūt marķētai ar epistemic_label="PROPOSED".');
            }
            if (!isText(b.label_key) || b.label_key.trim() === '') {
                errors.push('Kastei box ' + b.box + ' trūkst term-atslēgas label_key.');
            }
            const states = Array.isArray(b.mastery_states) ? b.mastery_states.filter(isText) : [];
            const spec = {
                box: b.box,
                role: isText(b.role) ? b.role : '',
                interval_days: typeof b.interval_days === 'number' ? b.interval_days : 0,
                epistemic_label: isText(b.epistemic_label) ? b.epistemic_label : '',
                label_key: isText(b.label_key) ? b.label_key : '',
                mastery_states: states
            };
            byBoxNum[bKey] = spec;
            boxes.push(spec);
        }
        boxes.sort(function (a, b) { return a.box - b.box; });
        for (let i = 0; i < boxes.length; i += 1) {
            if (boxes[i].box !== i + 1) {
                errors.push('Kastu numuriem jāveido secība no 1 bez izlaidumiem (box ' + boxes[i].box + ').');
            }
            if (i > 0) {
                const prev = boxes[i - 1];
                const cur = boxes[i];
                if (!(cur.interval_days > prev.interval_days)) {
                    nonInc.push({
                        lower_box: prev.box,
                        upper_box: cur.box,
                        lower_days: prev.interval_days,
                        upper_days: cur.interval_days
                    });
                    errors.push('Leitnera intervāli nav stingri pieaugoši starp box ' + prev.box +
                        ' (' + prev.interval_days + ' d.) un box ' + cur.box +
                        ' (' + cur.interval_days + ' d.).');
                }
            }
        }
        const stateToBox = isObject(rawPolicy.state_to_box) ? rawPolicy.state_to_box : {};
        for (let i = 0; i < MASTERY_STATES.length; i += 1) {
            const sid = MASTERY_STATES[i];
            const mapped = stateToBox[sid];
            if (!isPositiveInt(mapped) || !has(byBoxNum, String(mapped))) {
                errors.push('Apguves stāvoklim "' + sid + '" trūkst derīga kartējuma uz kasti (state_to_box).');
            }
            else {
                const boxSpec = byBoxNum[String(mapped)];
                if (boxSpec.mastery_states.indexOf(sid) < 0) {
                    errors.push('Stāvoklis "' + sid + '" norādīts uz box ' + mapped + ', bet nav iekļauts box ' + mapped + '.mastery_states.');
                }
            }
        }
        if (isPositiveInt(stateToBox.needs_review) && stateToBox.needs_review !== 1) {
            errors.push('Stāvoklim "needs_review" jābūt piespiestam uz agrīno 1. kasti (box 1).');
        }
        const reasonTemplates = isObject(rawPolicy.reason_templates) ? rawPolicy.reason_templates : {};
        for (let i = 0; i < REASON_CODES.length; i += 1) {
            const rc = REASON_CODES[i];
            const tpl = reasonTemplates[rc];
            if (!isObject(tpl) || !isText(tpl.term_key) || tpl.term_key.trim() === '') {
                errors.push('Trūkst iemesla veidnes term_key priekš "' + rc + '".');
            }
        }
        return {
            valid: errors.length === 0,
            policy_id: isText(rawPolicy.policy_id) ? rawPolicy.policy_id : '',
            queue_cap: isPositiveInt(qCapVal) ? qCapVal : 0,
            boxes: boxes,
            non_increasing_pairs: nonInc,
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
                return fail('E_SCHEDULER_POLICY_INVALID', 'Nav dokumenta plānotāja politikas salas ielādei.', {});
            }
            const node = docOrObj.getElementById(ISLAND_ID);
            if (!node || !isText(node.textContent) || node.textContent === '') {
                return fail('E_SCHEDULER_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav atrasta vai ir tukša.', {});
            }
            try {
                parsed = JSON.parse(node.textContent);
            }
            catch (err) {
                return fail('E_SCHEDULER_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav derīgs JSON.', {
                    reason: String(err)
                });
            }
        }
        const check = validatePolicy(parsed);
        if (!check.valid) {
            return fail('E_SCHEDULER_POLICY_INVALID', check.errors.join(' '), {
                errors: check.errors,
                non_increasing_pairs: check.non_increasing_pairs
            });
        }
        const clean = sortedValue(copyJson(parsed));
        return { policy: clean, digest: digestValue(clean) };
    }
    /* -------------------------------------------------- box mapping & trace */
    function boxForState(stateId, policy) {
        if (!isText(stateId) || MASTERY_STATES.indexOf(stateId) < 0) {
            return fail('E_SCHEDULER_UNKNOWN_STATE', 'Nezināms apguves stāvoklis "' + String(stateId) + '".', {
                state: stateId
            });
        }
        const stateToBox = isObject(policy.state_to_box) ? policy.state_to_box : {};
        const boxNum = stateToBox[stateId];
        const boxes = Array.isArray(policy.boxes) ? policy.boxes : [];
        for (let i = 0; i < boxes.length; i += 1) {
            if (boxes[i] && boxes[i].box === boxNum) {
                return {
                    box: boxes[i].box,
                    role: boxes[i].role || '',
                    interval_days: boxes[i].interval_days,
                    epistemic_label: boxes[i].epistemic_label || 'PROPOSED',
                    label_key: boxes[i].label_key || '',
                    mastery_states: Array.isArray(boxes[i].mastery_states) ? boxes[i].mastery_states.slice() : []
                };
            }
        }
        return fail('E_SCHEDULER_POLICY_INVALID', 'Stāvoklim "' + stateId + '" nav atrasta kaste politikā.', {
            state: stateId,
            box: boxNum
        });
    }
    function traceBoxHistory(sequence, policy) {
        const out = [];
        for (let i = 0; i < sequence.length; i += 1) {
            const item = sequence[i];
            const st = isText(item) ? item : item.state;
            const b = boxForState(st, policy);
            out.push({
                step: i,
                state: st,
                box: b.box,
                role: b.role,
                interval_days: b.interval_days,
                event: !isText(item) && isText(item.event) ? item.event : null,
                day: !isText(item) && typeof item.day === 'number' ? item.day : null
            });
        }
        return out;
    }
    /* --------------------------------------------------- availability & terms */
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
    function computeFamilyAvailability(coverage, bankQuestions, policy, termsMap) {
        const covOutcomes = Array.isArray(coverage && coverage.outcomes) ? coverage.outcomes : [];
        const byFamily = {};
        const byOutcome = {};
        const unavailKey = (policy && isObject(policy.reason_templates) && isObject(policy.reason_templates.unavailable))
            ? String(policy.reason_templates.unavailable.term_key || 'scheduler.reason.unavailable')
            : 'scheduler.reason.unavailable';
        const unavailText = (termsMap && isText(termsMap[unavailKey]))
            ? termsMap[unavailKey]
            : 'Pagaidām nav pieejams praksei: nav treniņformai derīgu uzdevumu.';
        const outcomesByFamily = {};
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oc = covOutcomes[i];
            if (!isObject(oc) || !isText(oc.id)) {
                continue;
            }
            const fams = oc.bindings && Array.isArray(oc.bindings.practice_families)
                ? oc.bindings.practice_families.filter(isText)
                : [];
            for (let j = 0; j < fams.length; j += 1) {
                const fam = fams[j];
                if (!has(outcomesByFamily, fam)) {
                    outcomesByFamily[fam] = [];
                }
                if (outcomesByFamily[fam].indexOf(oc.id) < 0) {
                    outcomesByFamily[fam].push(oc.id);
                }
                if (!has(byFamily, fam)) {
                    byFamily[fam] = {
                        family_id: fam,
                        topic: Number(oc.topic || 0),
                        available: false,
                        eligible_count: 0,
                        pending_count: 0,
                        eligible_instance_ids: []
                    };
                }
            }
        }
        if (!Array.isArray(bankQuestions)) {
            const famKeys = Object.keys(byFamily).sort();
            for (let i = 0; i < famKeys.length; i += 1) {
                const fk = famKeys[i];
                byFamily[fk].available = true;
                byFamily[fk].eligible_count = 1;
            }
            for (let i = 0; i < covOutcomes.length; i += 1) {
                const oc = covOutcomes[i];
                const fams = oc.bindings && Array.isArray(oc.bindings.practice_families)
                    ? oc.bindings.practice_families.filter(isText).sort()
                    : [];
                byOutcome[oc.id] = {
                    outcome_id: oc.id,
                    topic: Number(oc.topic || 0),
                    available: true,
                    eligible_count: 1,
                    total_count: 1,
                    pending_review_count: 0,
                    eligible_families: fams,
                    eligible_instance_ids: [],
                    reason_key: null,
                    reason_lv: null
                };
            }
            return { by_family: sortedValue(byFamily), by_outcome: sortedValue(byOutcome) };
        }
        const eligInstByOutcome = {};
        const eligFamsByOutcome = {};
        const totalByOutcome = {};
        const pendingByOutcome = {};
        const sortedBank = bankQuestions.slice().sort(function (a, b) {
            const qa = isObject(a) && isText(a.question_id) ? a.question_id : '';
            const qb = isObject(b) && isText(b.question_id) ? b.question_id : '';
            return qa < qb ? -1 : (qa > qb ? 1 : 0);
        });
        for (let i = 0; i < sortedBank.length; i += 1) {
            const q = sortedBank[i];
            if (!isObject(q)) {
                continue;
            }
            const fam = isText(q.family_id) ? q.family_id : '';
            const qid = isText(q.question_id) ? q.question_id : '';
            const eligible = isBankInstanceEligible(q);
            if (fam) {
                if (!has(byFamily, fam)) {
                    byFamily[fam] = {
                        family_id: fam,
                        topic: Number(q.topic || 0),
                        available: false,
                        eligible_count: 0,
                        pending_count: 0,
                        eligible_instance_ids: []
                    };
                }
                if (eligible) {
                    byFamily[fam].eligible_count += 1;
                    byFamily[fam].available = true;
                    if (qid && byFamily[fam].eligible_instance_ids.indexOf(qid) < 0) {
                        byFamily[fam].eligible_instance_ids.push(qid);
                    }
                }
                else {
                    byFamily[fam].pending_count += 1;
                }
            }
            let oids = [];
            if (Array.isArray(q.outcome_ids) && q.outcome_ids.length > 0) {
                oids = q.outcome_ids.filter(isText);
            }
            else if (fam && has(outcomesByFamily, fam)) {
                oids = outcomesByFamily[fam];
            }
            for (let j = 0; j < oids.length; j += 1) {
                const oid = oids[j];
                totalByOutcome[oid] = (totalByOutcome[oid] || 0) + 1;
                if (eligible) {
                    if (!has(eligInstByOutcome, oid)) {
                        eligInstByOutcome[oid] = [];
                    }
                    if (qid && eligInstByOutcome[oid].indexOf(qid) < 0) {
                        eligInstByOutcome[oid].push(qid);
                    }
                    if (fam) {
                        if (!has(eligFamsByOutcome, oid)) {
                            eligFamsByOutcome[oid] = [];
                        }
                        if (eligFamsByOutcome[oid].indexOf(fam) < 0) {
                            eligFamsByOutcome[oid].push(fam);
                        }
                    }
                }
                else {
                    pendingByOutcome[oid] = (pendingByOutcome[oid] || 0) + 1;
                }
            }
        }
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oc = covOutcomes[i];
            const oid = oc.id;
            const insts = (eligInstByOutcome[oid] || []).slice().sort();
            const fams = (eligFamsByOutcome[oid] || []).slice().sort();
            const eligCount = insts.length;
            const totCount = totalByOutcome[oid] || 0;
            const pendCount = pendingByOutcome[oid] || 0;
            const available = eligCount > 0;
            byOutcome[oid] = {
                outcome_id: oid,
                topic: Number(oc.topic || 0),
                available: available,
                eligible_count: eligCount,
                total_count: totCount,
                pending_review_count: pendCount,
                eligible_families: fams,
                eligible_instance_ids: insts,
                reason_key: available ? null : unavailKey,
                reason_lv: available ? null : unavailText
            };
        }
        return {
            by_family: sortedValue(byFamily),
            by_outcome: sortedValue(byOutcome)
        };
    }
    function resolveTermsMap(docOrTerms) {
        const out = {};
        if (docOrTerms && typeof docOrTerms.getElementById === 'function') {
            const node = docOrTerms.getElementById('sim-terms');
            if (node && isText(node.textContent) && node.textContent.trim() !== '') {
                try {
                    const parsed = JSON.parse(node.textContent);
                    return resolveTermsMap(parsed);
                }
                catch (_err) {
                    /* ignore malformed #sim-terms fallback */
                }
            }
            const termsApi = root.SimTerms;
            if (termsApi && typeof termsApi.getDefault === 'function') {
                const def = termsApi.getDefault();
                if (def) {
                    return resolveTermsMap(def);
                }
            }
            return out;
        }
        if (isObject(docOrTerms)) {
            if (Array.isArray(docOrTerms.terms)) {
                for (let i = 0; i < docOrTerms.terms.length; i += 1) {
                    const item = docOrTerms.terms[i];
                    if (isObject(item) && isText(item.key) && isText(item.text_lv)) {
                        out[item.key] = item.text_lv;
                    }
                }
                return out;
            }
            if (isObject(docOrTerms.byKey)) {
                const keys = Object.keys(docOrTerms.byKey);
                for (let i = 0; i < keys.length; i += 1) {
                    const entry = docOrTerms.byKey[keys[i]];
                    if (isObject(entry) && isText(entry.text_lv)) {
                        out[keys[i]] = entry.text_lv;
                    }
                }
                return out;
            }
            const directKeys = Object.keys(docOrTerms);
            for (let i = 0; i < directKeys.length; i += 1) {
                if (isText(docOrTerms[directKeys[i]])) {
                    out[directKeys[i]] = docOrTerms[directKeys[i]];
                }
            }
            return out;
        }
        const termsApi = root.SimTerms;
        if (termsApi && typeof termsApi.getDefault === 'function') {
            const def = termsApi.getDefault();
            if (def) {
                return resolveTermsMap(def);
            }
        }
        return out;
    }
    const FALLBACK_TERM_TEXT = {
        'scheduler.queue.title': 'Ieteicamie atkārtojumi nākamajai praksei (PROPOSED)',
        'scheduler.queue.honesty_note': 'PROPOSED mācību politika: Leitnera intervālu rinda ir tikai patstāvīgas mācīšanās palīgs, nevis oficiāls programmas vai eksāmena grafiks.',
        'scheduler.queue.status_summary': 'Aktīvā diena: {date} · Rindā: {count}/{cap} · Kavēti: {overdue} · Šodien: {due_today} · Jauni: {new_count} · Nepieejami: {excluded}',
        'scheduler.queue.empty_unavailable': 'Pašlaik nav pieejamu mācību mērķu praksei (visi mērķi gaida recenziju vai nav derīgu uzdevumu).',
        'scheduler.queue.action_practice': 'Praktizēt šo mērķi',
        'scheduler.queue.handoff_heading': 'Prakses ceļa sagatave mērķim {outcome_id} (N27 → N30)',
        'scheduler.queue.handoff_note': 'Izvēles dati bez atbilžu atslēgām: sagatavoti treniņformai derīgie bankas uzdevumi.',
        'scheduler.reason.overdue': 'Nokavēts par {days} d. (kaste {box}, intervāls {interval} d.)',
        'scheduler.reason.due_today': 'Atkārtojums pienācis šodien (kaste {box}, intervāls {interval} d.)',
        'scheduler.reason.new': 'Jauns mērķis — vēl nav mēģināts (kaste {box})',
        'scheduler.reason.least_recently_practiced': 'Agrāka atkārtošana — pēdējā prakse pirms {days} d. (kaste {box}, intervāls {interval} d.)',
        'scheduler.reason.unavailable': 'Pagaidām nav pieejams praksei: nav treniņformai derīgu uzdevumu.',
        'scheduler.box.1.label': '1. kaste (sākuma / atkārtošanas)',
        'scheduler.box.2.label': '2. kaste (vidējā)',
        'scheduler.box.3.label': '3. kaste (vēlākā)',
        'scheduler.topic.summary_line': '{topic}. tēma — 1. kaste: {b1} · 2. kaste: {b2} · 3. kaste: {b3} · Kavēti: {overdue} · Nepieejami: {unavailable}'
    };
    function termText(key, termsMap, params) {
        let tpl = has(termsMap, key) ? termsMap[key] : (FALLBACK_TERM_TEXT[key] || key);
        if (params) {
            const pKeys = Object.keys(params);
            for (let i = 0; i < pKeys.length; i += 1) {
                const pk = pKeys[i];
                tpl = tpl.split('{' + pk + '}').join(String(params[pk]));
            }
        }
        return tpl;
    }
    /* ------------------------------------------------ pure queue selection */
    function resolveOutcomeAvailability(outcome, availabilityInput, familyMap, computedFromBank, unavailKey, termsMap) {
        const oid = outcome.id;
        const topic = Number(outcome.topic || 0);
        const fams = outcome.bindings && Array.isArray(outcome.bindings.practice_families)
            ? outcome.bindings.practice_families.filter(isText).sort()
            : [];
        if (isObject(availabilityInput) && has(availabilityInput, oid)) {
            const raw = availabilityInput[oid];
            if (isObject(raw)) {
                const isAvail = raw.available === true && (typeof raw.eligible_count !== 'number' || raw.eligible_count > 0);
                const instIds = Array.isArray(raw.eligible_instance_ids)
                    ? raw.eligible_instance_ids.filter(isText).slice().sort()
                    : (computedFromBank && has(computedFromBank.by_outcome, oid)
                        ? computedFromBank.by_outcome[oid].eligible_instance_ids.slice()
                        : []);
                const eligFams = Array.isArray(raw.eligible_families)
                    ? raw.eligible_families.filter(isText).slice().sort()
                    : fams;
                return {
                    outcome_id: oid,
                    topic: topic,
                    available: isAvail,
                    eligible_count: typeof raw.eligible_count === 'number' ? raw.eligible_count : (isAvail ? Math.max(1, instIds.length) : 0),
                    total_count: typeof raw.total_count === 'number' ? raw.total_count : 0,
                    pending_review_count: typeof raw.pending_review_count === 'number' ? raw.pending_review_count : 0,
                    eligible_families: isAvail ? eligFams : [],
                    eligible_instance_ids: isAvail ? instIds : [],
                    reason_key: isAvail ? null : unavailKey,
                    reason_lv: isAvail ? null : (isText(raw.reason_lv) && raw.reason_lv ? raw.reason_lv : termText(unavailKey, termsMap))
                };
            }
            if (typeof raw === 'boolean') {
                return {
                    outcome_id: oid,
                    topic: topic,
                    available: raw,
                    eligible_count: raw ? 1 : 0,
                    total_count: 1,
                    pending_review_count: raw ? 0 : 1,
                    eligible_families: raw ? fams : [],
                    eligible_instance_ids: [],
                    reason_key: raw ? null : unavailKey,
                    reason_lv: raw ? null : termText(unavailKey, termsMap)
                };
            }
        }
        if (familyMap) {
            const eligFams = [];
            let eligCount = 0;
            let pendCount = 0;
            const instIds = [];
            for (let i = 0; i < fams.length; i += 1) {
                const fam = fams[i];
                const entry = familyMap[fam];
                let famOk = false;
                if (entry === true) {
                    famOk = true;
                    eligCount += 1;
                }
                else if (typeof entry === 'number' && entry > 0) {
                    famOk = true;
                    eligCount += entry;
                }
                else if (Array.isArray(entry) && entry.length > 0) {
                    famOk = true;
                    eligCount += entry.length;
                    for (let k = 0; k < entry.length; k += 1) {
                        if (isObject(entry[k]) && isText(entry[k].question_id)) {
                            instIds.push(entry[k].question_id);
                        }
                        else if (isText(entry[k])) {
                            instIds.push(entry[k]);
                        }
                    }
                }
                else if (isObject(entry)) {
                    const ec = typeof entry.eligible_count === 'number' ? entry.eligible_count : 0;
                    const pc = typeof entry.pending_count === 'number' ? entry.pending_count : 0;
                    pendCount += pc;
                    if (entry.available === true || ec > 0) {
                        famOk = true;
                        eligCount += Math.max(1, ec);
                        if (Array.isArray(entry.eligible_instance_ids)) {
                            for (let k = 0; k < entry.eligible_instance_ids.length; k += 1) {
                                if (isText(entry.eligible_instance_ids[k])) {
                                    instIds.push(entry.eligible_instance_ids[k]);
                                }
                            }
                        }
                    }
                }
                if (famOk) {
                    eligFams.push(fam);
                }
            }
            instIds.sort();
            const avail = eligFams.length > 0 && eligCount > 0;
            return {
                outcome_id: oid,
                topic: topic,
                available: avail,
                eligible_count: avail ? eligCount : 0,
                total_count: eligCount + pendCount,
                pending_review_count: pendCount,
                eligible_families: eligFams,
                eligible_instance_ids: instIds,
                reason_key: avail ? null : unavailKey,
                reason_lv: avail ? null : termText(unavailKey, termsMap)
            };
        }
        if (computedFromBank && has(computedFromBank.by_outcome, oid)) {
            return computedFromBank.by_outcome[oid];
        }
        return {
            outcome_id: oid,
            topic: topic,
            available: true,
            eligible_count: 1,
            total_count: 1,
            pending_review_count: 0,
            eligible_families: fams,
            eligible_instance_ids: [],
            reason_key: null,
            reason_lv: null
        };
    }
    function selectQueue(input) {
        if (!isObject(input) || !isObject(input.coverage) || !Array.isArray(input.coverage.outcomes)) {
            return fail('E_SCHEDULER_POLICY_INVALID', 'Rindas atlasei nepieciešama seguma sala (#sim-coverage).', {});
        }
        const polCheck = validatePolicy(input.policy);
        if (!polCheck.valid) {
            return fail('E_SCHEDULER_POLICY_INVALID', polCheck.errors.join(' '), {
                errors: polCheck.errors,
                non_increasing_pairs: polCheck.non_increasing_pairs
            });
        }
        const policy = input.policy;
        let currentDay;
        let currentDateIso;
        if (input.date !== undefined && input.date !== null) {
            currentDay = toDayNumber(input.date);
            currentDateIso = typeof input.date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(input.date.trim())
                ? input.date.trim()
                : dayNumberToIso(currentDay);
        }
        else if (input.clock && typeof input.clock.todayDay === 'function') {
            currentDay = input.clock.todayDay();
            currentDateIso = typeof input.clock.todayIso === 'function' ? input.clock.todayIso() : dayNumberToIso(currentDay);
        }
        else {
            return fail('E_SCHEDULER_INVALID_DATE', 'Atlasei jānorāda deterministisks datums vai injicēts DayClock.', {});
        }
        const termsMap = resolveTermsMap(input.terms || input.doc);
        const templates = isObject(policy.reason_templates) ? policy.reason_templates : {};
        const unavailKey = isObject(templates.unavailable) && isText(templates.unavailable.term_key)
            ? templates.unavailable.term_key : 'scheduler.reason.unavailable';
        const computedFromBank = Array.isArray(input.bankQuestions)
            ? computeFamilyAvailability(input.coverage, input.bankQuestions, policy, termsMap)
            : null;
        const rawOutcomesMap = isObject(input.masteryMap) && isObject(input.masteryMap.outcomes)
            ? input.masteryMap.outcomes
            : {};
        const candidates = [];
        const excluded = [];
        const topicBuckets = {};
        const covTopics = Array.isArray(input.coverage.topics) ? input.coverage.topics : [];
        for (let t = 1; t <= 7; t += 1) {
            let tName = String(t) + '. tēma';
            for (let i = 0; i < covTopics.length; i += 1) {
                if (covTopics[i] && Number(covTopics[i].topic) === t && isText(covTopics[i].name_lv)) {
                    tName = covTopics[i].name_lv;
                    break;
                }
            }
            topicBuckets[String(t)] = {
                topic: t,
                name_lv: tName,
                total_outcomes: 0,
                available_outcomes: 0,
                unavailable_outcomes: 0,
                box_1: 0,
                box_2: 0,
                box_3: 0,
                overdue: 0,
                due_today: 0,
                never_seen: 0,
                scheduled_later: 0,
                next_outcome_id: null
            };
        }
        const covOutcomes = input.coverage.outcomes.slice().sort(function (a, b) {
            const ida = String(a && a.id || '');
            const idb = String(b && b.id || '');
            return ida < idb ? -1 : (ida > idb ? 1 : 0);
        });
        for (let i = 0; i < covOutcomes.length; i += 1) {
            const oc = covOutcomes[i];
            if (!isObject(oc) || !isText(oc.id)) {
                continue;
            }
            const oid = oc.id;
            const topic = Number(oc.topic || 0);
            const tb = topicBuckets[String(topic)];
            if (tb) {
                tb.total_outcomes += 1;
            }
            const avail = resolveOutcomeAvailability(oc, input.availability || null, input.familyAvailability || null, computedFromBank, unavailKey, termsMap);
            if (!avail.available || avail.eligible_count <= 0) {
                if (tb) {
                    tb.unavailable_outcomes += 1;
                }
                excluded.push({
                    outcome_id: oid,
                    topic: topic,
                    statement_lv: isText(oc.statement_lv) ? oc.statement_lv : '',
                    eligible_families: oc.bindings && Array.isArray(oc.bindings.practice_families)
                        ? oc.bindings.practice_families.filter(isText).slice().sort()
                        : [],
                    eligible_count: 0,
                    pending_review_count: avail.pending_review_count,
                    reason_code: 'unavailable',
                    reason_key: avail.reason_key || unavailKey,
                    reason_lv: avail.reason_lv || termText(unavailKey, termsMap)
                });
                continue;
            }
            if (tb) {
                tb.available_outcomes += 1;
            }
            const entry = isObject(rawOutcomesMap[oid]) ? rawOutcomesMap[oid] : {};
            const state = isText(entry.state) ? entry.state : 'unseen';
            const box = boxForState(state, policy);
            const lastDay = typeof entry.last_practiced_day === 'number' && isFinite(entry.last_practiced_day)
                ? Math.floor(entry.last_practiced_day)
                : null;
            if (tb) {
                if (box.box === 1) {
                    tb.box_1 += 1;
                }
                else if (box.box === 2) {
                    tb.box_2 += 1;
                }
                else if (box.box === 3) {
                    tb.box_3 += 1;
                }
            }
            const isNeverSeen = state === 'unseen' || lastDay === null;
            let daysSince = null;
            let overdueDays = 0;
            let tier;
            let reasonCode;
            if (isNeverSeen) {
                daysSince = null;
                overdueDays = 0;
                tier = 2;
                reasonCode = 'new';
                if (tb) {
                    tb.never_seen += 1;
                }
            }
            else {
                daysSince = Math.max(0, currentDay - lastDay);
                const rawOverdue = daysSince - box.interval_days;
                overdueDays = Math.max(0, rawOverdue);
                if (rawOverdue > 0) {
                    tier = 1;
                    reasonCode = 'overdue';
                    if (tb) {
                        tb.overdue += 1;
                    }
                }
                else if (rawOverdue === 0) {
                    tier = 1;
                    reasonCode = 'due_today';
                    if (tb) {
                        tb.due_today += 1;
                    }
                }
                else {
                    tier = 3;
                    reasonCode = 'least_recently_practiced';
                    if (tb) {
                        tb.scheduled_later += 1;
                    }
                }
            }
            const tpl = templates[reasonCode];
            const reasonKey = isObject(tpl) && isText(tpl.term_key) ? tpl.term_key : ('scheduler.reason.' + reasonCode);
            const reasonLv = termText(reasonKey, termsMap, {
                days: reasonCode === 'overdue' ? overdueDays : (daysSince !== null ? daysSince : 0),
                box: box.box,
                interval: box.interval_days
            });
            candidates.push({
                outcome_id: oid,
                topic: topic,
                statement_lv: isText(oc.statement_lv) ? oc.statement_lv : '',
                master_anchor: isText(oc.master_anchor) ? oc.master_anchor : '',
                mastery_state: state,
                box: box.box,
                box_role: box.role,
                box_label_key: box.label_key,
                box_label_lv: termText(box.label_key, termsMap),
                interval_days: box.interval_days,
                last_practiced_day: lastDay,
                days_since_practice: daysSince,
                overdue_days: overdueDays,
                tier: tier,
                reason_code: reasonCode,
                reason_key: reasonKey,
                reason_lv: reasonLv,
                eligible_families: avail.eligible_families.slice().sort(),
                eligible_instance_ids: avail.eligible_instance_ids.slice().sort()
            });
        }
        candidates.sort(function (a, b) {
            if (a.tier !== b.tier) {
                return a.tier - b.tier;
            }
            if (a.tier === 1) {
                if (a.overdue_days !== b.overdue_days) {
                    return b.overdue_days - a.overdue_days;
                }
                return a.outcome_id < b.outcome_id ? -1 : (a.outcome_id > b.outcome_id ? 1 : 0);
            }
            if (a.tier === 2) {
                if (a.topic !== b.topic) {
                    return a.topic - b.topic;
                }
                return a.outcome_id < b.outcome_id ? -1 : (a.outcome_id > b.outcome_id ? 1 : 0);
            }
            /* tier === 3: least-recently-practiced (oldest last_practiced_day first), tie-break outcome_id */
            const da = a.last_practiced_day !== null ? a.last_practiced_day : 0;
            const db = b.last_practiced_day !== null ? b.last_practiced_day : 0;
            if (da !== db) {
                return da - db;
            }
            return a.outcome_id < b.outcome_id ? -1 : (a.outcome_id > b.outcome_id ? 1 : 0);
        });
        for (let i = 0; i < candidates.length; i += 1) {
            const tb = topicBuckets[String(candidates[i].topic)];
            if (tb && tb.next_outcome_id === null) {
                tb.next_outcome_id = candidates[i].outcome_id;
            }
        }
        const queueCap = polCheck.queue_cap;
        const queue = [];
        const limit = Math.min(queueCap, candidates.length);
        for (let i = 0; i < limit; i += 1) {
            const c = candidates[i];
            queue.push({
                rank: i + 1,
                outcome_id: c.outcome_id,
                topic: c.topic,
                statement_lv: c.statement_lv,
                master_anchor: c.master_anchor,
                mastery_state: c.mastery_state,
                box: c.box,
                box_role: c.box_role,
                box_label_key: c.box_label_key,
                box_label_lv: c.box_label_lv,
                interval_days: c.interval_days,
                last_practiced_day: c.last_practiced_day,
                days_since_practice: c.days_since_practice,
                overdue_days: c.overdue_days,
                tier: c.tier,
                reason_code: c.reason_code,
                reason_key: c.reason_key,
                reason_lv: c.reason_lv,
                eligible_families: c.eligible_families,
                eligible_instance_ids: c.eligible_instance_ids
            });
        }
        const perTopic = [];
        for (let t = 1; t <= 7; t += 1) {
            const tb = topicBuckets[String(t)];
            perTopic.push({
                topic: tb.topic,
                name_lv: tb.name_lv,
                total_outcomes: tb.total_outcomes,
                available_outcomes: tb.available_outcomes,
                unavailable_outcomes: tb.unavailable_outcomes,
                box_1: tb.box_1,
                box_2: tb.box_2,
                box_3: tb.box_3,
                overdue: tb.overdue,
                due_today: tb.due_today,
                never_seen: tb.never_seen,
                scheduled_later: tb.scheduled_later,
                next_outcome_id: tb.next_outcome_id,
                summary_lv: termText('scheduler.topic.summary_line', termsMap, {
                    topic: tb.topic,
                    b1: tb.box_1,
                    b2: tb.box_2,
                    b3: tb.box_3,
                    overdue: tb.overdue,
                    unavailable: tb.unavailable_outcomes
                })
            });
        }
        const payload = sortedValue({
            schema_version: SCHEMA_VERSION,
            policy_id: polCheck.policy_id,
            policy_digest: digestValue(sortedValue(policy)),
            epistemic_label: 'PROPOSED',
            official_counterpart_status: 'UNDETERMINED',
            current_day: currentDay,
            current_date_iso: currentDateIso,
            queue_cap: queueCap,
            total_eligible: candidates.length,
            total_excluded: excluded.length,
            queue: queue,
            excluded: excluded,
            per_topic: perTopic
        });
        payload.digest = digestValue(payload);
        return payload;
    }
    function digestOfQueue(selection) {
        if (!isObject(selection)) {
            return fail('E_SCHEDULER_POLICY_INVALID', 'Nepieciešams atlases rezultāts digest aprēķinam.', {});
        }
        const clone = copyJson(selection);
        delete clone.digest;
        return digestValue(sortedValue(clone));
    }
    /* --------------------------------------------------- N27 -> N30 handoff */
    function buildPracticeHandoff(queueItem, bankQuestions, coverage) {
        if (!isObject(queueItem) || !isText(queueItem.outcome_id) || queueItem.outcome_id === '') {
            return fail('E_SCHEDULER_HANDOFF_INVALID', 'Prakses nodošanai nepieciešams derīgs rindas vienums.', {});
        }
        let familyIds = Array.isArray(queueItem.eligible_families)
            ? queueItem.eligible_families.filter(isText).slice().sort()
            : [];
        let instanceIds = Array.isArray(queueItem.eligible_instance_ids)
            ? queueItem.eligible_instance_ids.filter(isText).slice().sort()
            : [];
        if (Array.isArray(bankQuestions) && coverage) {
            const avail = computeFamilyAvailability(coverage, bankQuestions, null, null);
            const entry = avail.by_outcome[queueItem.outcome_id];
            if (!entry || !entry.available || entry.eligible_instance_ids.length === 0) {
                return fail('E_SCHEDULER_UNAVAILABLE_OUTCOME', 'Mērķim "' + queueItem.outcome_id + '" nav derīgu bankas uzdevumu praksei.', {
                    outcome_id: queueItem.outcome_id
                });
            }
            familyIds = entry.eligible_families.slice().sort();
            instanceIds = entry.eligible_instance_ids.slice().sort();
        }
        if (familyIds.length === 0 && instanceIds.length === 0) {
            return fail('E_SCHEDULER_UNAVAILABLE_OUTCOME', 'Mērķim "' + queueItem.outcome_id + '" nav norādītu derīgu uzdevumu vai saimju.', {
                outcome_id: queueItem.outcome_id
            });
        }
        /* Contract: selection data ONLY; never include rubric, payload keys, or answers. */
        return sortedValue({
            schema_version: SCHEMA_VERSION,
            contract: 'N27-to-N30-practice-entry',
            entry_source: 'scheduler_queue',
            outcome_id: queueItem.outcome_id,
            topic: Number(queueItem.topic || 0),
            mastery_state: queueItem.mastery_state,
            box: queueItem.box,
            reason_code: queueItem.reason_code,
            reason_lv: queueItem.reason_lv,
            filters: {
                topic: Number(queueItem.topic || 0),
                outcome_id: queueItem.outcome_id,
                family_ids: familyIds,
                instance_ids: instanceIds
            }
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
    function renderHandoffHost(doc, handoff, termsMap) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const host = doc.getElementById('prakse-scheduler-handoff');
        if (!host) {
            return;
        }
        clearNode(host);
        host.hidden = false;
        host.setAttribute('data-outcome-id', handoff.outcome_id);
        host.setAttribute('data-topic', String(handoff.topic));
        host.appendChild(makeEl(doc, 'h4', 'scheduler-handoff-title', termText('scheduler.queue.handoff_heading', termsMap, { outcome_id: handoff.outcome_id })));
        host.appendChild(makeEl(doc, 'p', 'scheduler-handoff-note', termText('scheduler.queue.handoff_note', termsMap)));
        host.appendChild(makeEl(doc, 'p', 'scheduler-handoff-meta', 'Saimes: ' + (handoff.filters.family_ids.join(', ') || '—') +
            ' · Derīgie uzdevumi (' + handoff.filters.instance_ids.length + '): ' +
            (handoff.filters.instance_ids.join(', ') || '—')));
    }
    function startPracticeFromQueueItem(queueItem, options) {
        const opts = options || {};
        const handoff = buildPracticeHandoff(queueItem, opts.bankQuestions, opts.coverage);
        const termsMap = resolveTermsMap(opts.terms || opts.doc);
        if (opts.doc) {
            renderHandoffHost(opts.doc, handoff, termsMap);
        }
        if (typeof opts.practiceStarter === 'function') {
            return {
                handoff: handoff,
                started_via: 'practiceStarter',
                starter_result: opts.practiceStarter(handoff)
            };
        }
        const practiceApi = root.SimPractice;
        if (practiceApi && typeof practiceApi.startPath === 'function') {
            return {
                handoff: handoff,
                started_via: 'SimPractice',
                starter_result: practiceApi.startPath(handoff)
            };
        }
        return {
            handoff: handoff,
            started_via: 'handoff_host',
            starter_result: null
        };
    }
    function buildPrakseSchedulerViewModel(selection, policy, termsMap) {
        let overdueCount = 0;
        let dueTodayCount = 0;
        let newCount = 0;
        for (let i = 0; i < selection.per_topic.length; i += 1) {
            overdueCount += selection.per_topic[i].overdue;
            dueTodayCount += selection.per_topic[i].due_today;
            newCount += selection.per_topic[i].never_seen;
        }
        return sortedValue({
            view: 'prakse_scheduler',
            policy_id: selection.policy_id,
            epistemic_label: 'PROPOSED',
            official_counterpart_status: 'UNDETERMINED',
            title_lv: termText('scheduler.queue.title', termsMap),
            honesty_note_lv: isText(policy.honesty_note_lv) ? policy.honesty_note_lv : termText('scheduler.queue.honesty_note', termsMap),
            status_summary_lv: termText('scheduler.queue.status_summary', termsMap, {
                date: selection.current_date_iso,
                count: selection.queue.length,
                cap: selection.queue_cap,
                overdue: overdueCount,
                due_today: dueTodayCount,
                new_count: newCount,
                excluded: selection.total_excluded
            }),
            empty_note_lv: selection.queue.length === 0 ? termText('scheduler.queue.empty_unavailable', termsMap) : null,
            action_label_lv: termText('scheduler.queue.action_practice', termsMap),
            current_day: selection.current_day,
            current_date_iso: selection.current_date_iso,
            queue_cap: selection.queue_cap,
            queue: selection.queue,
            excluded_count: selection.total_excluded,
            excluded: selection.excluded,
            per_topic: selection.per_topic,
            selection_digest: selection.digest
        });
    }
    function renderPrakseQueue(doc, selection, policy, options) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return null;
        }
        const opts = options || {};
        const termsMap = resolveTermsMap(opts.terms || doc);
        const vm = buildPrakseSchedulerViewModel(selection, policy, termsMap);
        const headingEl = doc.getElementById('prakse-scheduler-heading');
        if (headingEl) {
            headingEl.textContent = vm.title_lv;
        }
        const honestyEl = doc.getElementById('prakse-scheduler-honesty');
        if (honestyEl) {
            honestyEl.textContent = vm.honesty_note_lv;
        }
        const statusEl = doc.getElementById('prakse-scheduler-status');
        if (statusEl) {
            statusEl.textContent = vm.status_summary_lv;
        }
        const queueEl = doc.getElementById('prakse-scheduler-queue');
        if (queueEl) {
            clearNode(queueEl);
            if (selection.queue.length === 0) {
                const emptyLi = makeEl(doc, 'li', 'scheduler-queue-empty', vm.empty_note_lv);
                queueEl.appendChild(emptyLi);
            }
            else {
                for (let i = 0; i < selection.queue.length; i += 1) {
                    const item = selection.queue[i];
                    const li = makeEl(doc, 'li', 'scheduler-queue-item scheduler-tier-' + item.tier);
                    li.setAttribute('data-outcome-id', item.outcome_id);
                    li.setAttribute('data-box', String(item.box));
                    li.setAttribute('data-reason-code', item.reason_code);
                    const headerRow = makeEl(doc, 'div', 'scheduler-item-head');
                    const boxBadge = makeEl(doc, 'span', 'scheduler-box-badge scheduler-box-' + item.box, item.box + '. kaste (' + item.interval_days + ' d.)');
                    headerRow.appendChild(boxBadge);
                    headerRow.appendChild(makeEl(doc, 'strong', 'scheduler-item-title', ' ' + item.rank + '. ' + item.outcome_id + ' — ' + item.statement_lv));
                    li.appendChild(headerRow);
                    const metaRow = makeEl(doc, 'div', 'scheduler-item-meta');
                    metaRow.appendChild(makeEl(doc, 'span', 'scheduler-item-reason', item.reason_lv));
                    const btn = makeEl(doc, 'button', 'btn-control scheduler-accept-btn', vm.action_label_lv);
                    btn.type = 'button';
                    btn.setAttribute('data-outcome-id', item.outcome_id);
                    btn.addEventListener('click', function () {
                        const started = startPracticeFromQueueItem(item, {
                            doc: doc,
                            bankQuestions: opts.bankQuestions,
                            coverage: opts.coverage,
                            terms: termsMap,
                            practiceStarter: opts.practiceStarter
                        });
                        if (typeof opts.onAccept === 'function') {
                            opts.onAccept(item, started);
                        }
                    });
                    metaRow.appendChild(btn);
                    li.appendChild(metaRow);
                    queueEl.appendChild(li);
                }
            }
        }
        const topicsEl = doc.getElementById('prakse-scheduler-topics');
        if (topicsEl) {
            clearNode(topicsEl);
            for (let i = 0; i < selection.per_topic.length; i += 1) {
                const tp = selection.per_topic[i];
                const chip = makeEl(doc, 'div', 'scheduler-topic-chip');
                chip.setAttribute('id', 'prakse-scheduler-topic-' + tp.topic);
                chip.setAttribute('data-topic', String(tp.topic));
                chip.textContent = tp.summary_lv;
                topicsEl.appendChild(chip);
            }
        }
        return vm;
    }
    let activeDocClock = null;
    let activePracticeStarter;
    function renderFromStore(doc, store, coverage, options) {
        if (!doc || typeof doc.getElementById !== 'function' || !coverage) {
            return null;
        }
        const opts = options || {};
        let policy = opts.policy || null;
        if (!policy) {
            try {
                policy = loadPolicy(doc).policy;
            }
            catch (_err) {
                return null;
            }
        }
        let bankQuestions = opts.bankQuestions !== undefined ? opts.bankQuestions : null;
        if (!bankQuestions && root.SimBank && typeof root.SimBank.load === 'function') {
            try {
                const bank = root.SimBank.load(doc);
                bankQuestions = Array.isArray(bank.questions) ? bank.questions : null;
            }
            catch (_err) {
                bankQuestions = null;
            }
        }
        let masteryMap = opts.masteryMap || null;
        const masteryApi = root.SimMastery;
        if (!masteryMap && store && masteryApi && typeof masteryApi.readFromStore === 'function') {
            try {
                const mLoaded = masteryApi.loadPolicy(doc);
                masteryMap = masteryApi.readFromStore(store, coverage, mLoaded.policy, mLoaded.digest);
            }
            catch (_err) {
                masteryMap = { schema_version: 1, outcomes: {} };
            }
        }
        if (!masteryMap) {
            masteryMap = { schema_version: 1, outcomes: {} };
        }
        const clock = opts.clock || (opts.date !== undefined ? createFixedDayClock(opts.date) : (activeDocClock || defaultDayClock()));
        const sel = selectQueue({
            masteryMap: masteryMap,
            coverage: coverage,
            date: opts.date,
            clock: clock,
            policy: policy,
            availability: opts.availability,
            familyAvailability: opts.familyAvailability,
            bankQuestions: bankQuestions,
            doc: doc
        });
        renderPrakseQueue(doc, sel, policy, {
            coverage: coverage,
            bankQuestions: bankQuestions,
            practiceStarter: opts.practiceStarter || activePracticeStarter
        });
        return sel;
    }
    function renderError(doc, error) {
        if (!doc || typeof doc.getElementById !== 'function') {
            return;
        }
        const box = doc.getElementById('sim-scheduler-error');
        if (!box) {
            return;
        }
        const code = isObject(error) && isText(error.code) ? error.code : 'E_SCHEDULER_POLICY_INVALID';
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
            return fail('E_SCHEDULER_POLICY_INVALID', 'Nav seguma salas (#sim-coverage) plānotāja inicializēšanai.', {});
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
        const clock = opts.clock || (opts.date !== undefined ? createFixedDayClock(opts.date) : defaultDayClock());
        activeDocClock = clock;
        activePracticeStarter = opts.practiceStarter;
        const masteryApi = root.SimMastery;
        const store = opts.store || (opts.masteryApp && opts.masteryApp.store) || null;
        let lastSelection = null;
        function readMasteryMap() {
            if (store && masteryApi && typeof masteryApi.readFromStore === 'function') {
                const mLoaded = masteryApi.loadPolicy(doc);
                return masteryApi.readFromStore(store, coverage, mLoaded.policy, mLoaded.digest);
            }
            if (opts.masteryApp && typeof opts.masteryApp.readFromStore === 'function') {
                return opts.masteryApp.readFromStore();
            }
            return { schema_version: 1, outcomes: {} };
        }
        function refresh(nextOpts) {
            const r = nextOpts || {};
            const mMap = r.masteryMap || readMasteryMap();
            const sel = selectQueue({
                masteryMap: mMap,
                coverage: coverage,
                date: r.date,
                clock: r.clock || clock,
                policy: loaded.policy,
                availability: r.availability,
                familyAvailability: r.familyAvailability,
                bankQuestions: r.bankQuestions !== undefined ? r.bankQuestions : bankQuestions,
                doc: doc
            });
            lastSelection = sel;
            renderPrakseQueue(doc, sel, loaded.policy, {
                coverage: coverage,
                bankQuestions: r.bankQuestions !== undefined ? r.bankQuestions : bankQuestions,
                practiceStarter: opts.practiceStarter
            });
            return sel;
        }
        refresh();
        return {
            policy: loaded.policy,
            policyDigest: loaded.digest,
            clock: clock,
            refresh: refresh,
            getLastSelection: function () { return lastSelection; },
            acceptOutcome: function (outcomeId, overrideStarter) {
                const sel = lastSelection || refresh();
                for (let i = 0; i < sel.queue.length; i += 1) {
                    if (sel.queue[i].outcome_id === outcomeId) {
                        return startPracticeFromQueueItem(sel.queue[i], {
                            doc: doc,
                            bankQuestions: bankQuestions,
                            coverage: coverage,
                            practiceStarter: overrideStarter || opts.practiceStarter
                        });
                    }
                }
                return fail('E_SCHEDULER_UNAVAILABLE_OUTCOME', 'Mērķis "' + outcomeId + '" nav aktīvajā ieteikumu rindā.', {
                    outcome_id: outcomeId
                });
            }
        };
    }
    const api = {
        ISLAND_ID: ISLAND_ID,
        SCHEMA_VERSION: SCHEMA_VERSION,
        MASTERY_STATES: MASTERY_STATES.slice(),
        REASON_CODES: REASON_CODES.slice(),
        errors: ERRORS.slice(),
        SchedulerError: SchedulerError,
        canonicalText: canonicalText,
        digestValue: digestValue,
        toDayNumber: toDayNumber,
        dayNumberToIso: dayNumberToIso,
        defaultDayClock: defaultDayClock,
        createFixedDayClock: createFixedDayClock,
        validatePolicy: validatePolicy,
        loadPolicy: loadPolicy,
        boxForState: boxForState,
        traceBoxHistory: traceBoxHistory,
        computeFamilyAvailability: computeFamilyAvailability,
        resolveTermsMap: resolveTermsMap,
        selectQueue: selectQueue,
        digestOfQueue: digestOfQueue,
        buildPracticeHandoff: buildPracticeHandoff,
        startPracticeFromQueueItem: startPracticeFromQueueItem,
        buildPrakseSchedulerViewModel: buildPrakseSchedulerViewModel,
        renderPrakseQueue: renderPrakseQueue,
        renderFromStore: renderFromStore,
        renderError: renderError,
        init: init
    };
    root.SimScheduler = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
