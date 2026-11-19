"use strict";
/* N22 — the response-type registry module.
 *
 * The typed reader of the `#sim-response-types` island and the single source of
 * the response-input semantics: the render contract, the payload contract, the
 * completion-state model, the error-surface mapping and the ARIA contract of
 * all eighteen response types.
 *
 * Contract (frozen for N22-B, N22-C, N23, N24, N30, N33):
 *
 *   load(islandJson[, termsJson])  validate the island; throws InputsError
 *                                  E_INPUTS_REGISTRY_INVALID naming the defect.
 *                                  The island is never tolerated half-broken.
 *   contractFor(typeId)            the frozen entry; throws InputsError
 *                                  E_INPUTS_UNKNOWN_TYPE naming the type id.
 *                                  There is no fallback contract: a silent
 *                                  fallback text field is the defect class this
 *                                  module exists to prevent.
 *   completion(typeId, contract, instance, payload)
 *                                  the pure completion model. Returns
 *                                  {status, missing[{field_id, name}],
 *                                   errors[{id, field, message_key}]}.
 *                                  No DOM, no session, no mutation of the
 *                                  payload: an error is an annotation, the raw
 *                                  strings are never rewritten.
 *   errorSurfaces(typeId)          the frozen error ids that type can render.
 *   errorMessage(errorId, terms)   the Latvian text for an error id, resolved
 *                                  through the term bank passed in.
 *
 * The module never reads the island or the term bank itself: both are handed
 * in, so the same code runs in the shipped artifact and in the Node harness.
 */
(function (root) {
    'use strict';
    /* ------------------------------------------------------------- constants */
    const ISLAND_ID = 'sim-response-types';
    const ISLAND_VERSION = 1;
    const REGISTRY_INVALID = 'E_INPUTS_REGISTRY_INVALID';
    const UNKNOWN_TYPE = 'E_INPUTS_UNKNOWN_TYPE';
    const UNKNOWN_ERROR_ID = 'E_INPUTS_UNKNOWN_ERROR_ID';
    const TERM_UNRESOLVED = 'E_INPUTS_TERM_UNRESOLVED';
    /* The eighteen type ids in canonical order (N04). */
    const TYPE_IDS = [
        'Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06',
        'Q07', 'Q08', 'Q09', 'Q10', 'Q11', 'Q12',
        'Q13', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18'
    ];
    /* The completed-types contract: render + grading binding per form. */
    const COMPLETED_TYPES = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15'];
    /* The frozen error vocabulary a response surface may carry: the four N17
     * class ids, the N19 blank id and the six N18 graph validity ids. */
    const INPUTS_ERROR_IDS = [
        'UNREADABLE_INPUT', 'DIMENSIONAL_INCONSISTENCY', 'PHYSICALLY_IMPLAUSIBLE', 'OUT_OF_DOMAIN',
        'BLANK_RESPONSE',
        'E_GRAPH_PAYLOAD_MALFORMED', 'E_GRAPH_EMPTY_SUBMISSION', 'E_GRAPH_OUT_OF_AXIS_RANGE',
        'E_GRAPH_WRONG_DIRECTION', 'E_GRAPH_DOUBLE_BACK', 'E_GRAPH_NON_MONOTONIC'
    ];
    const MODULE_ERROR_IDS = [REGISTRY_INVALID, UNKNOWN_TYPE, UNKNOWN_ERROR_ID, TERM_UNRESOLVED];
    const PAYLOAD_KINDS = ['numeric', 'option_select', 'ordering', 'matching', 'graph', 'method'];
    const MODELS = ['numeric', 'vector', 'rows', 'pairs', 'order', 'selection', 'text', 'template', 'pair_map', 'graph'];
    const GRAPH_MODES = ['record', 'plot_state', 'read'];
    const GRADING_CLASSES = ['auto', 'self', 'pending', 'mixed'];
    /* ---------------------------------------------------------------- errors */
    class InputsError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'InputsError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, InputsError);
            }
            else {
                this.stack = new Error(message).stack;
            }
        }
    }
    function fail(code, message, details) {
        throw new InputsError(code, message, details);
    }
    /* The announcement strings the components read instead of composing text:
     * the verdict states, the group label, the error prefix and the
     * input-preservation notice. */
    const ANNOUNCEMENT_KEYS = [
        'complete', 'incomplete', 'invalid', 'pending_grading',
        'group_label', 'completion_announce', 'error_prefix', 'input_preserved'
    ];
    /* ------------------------------------------------------------------ state */
    let island = null;
    let termBank = null;
    let errorIndex = null;
    function has(value, key) {
        return Object.prototype.hasOwnProperty.call(value, key);
    }
    function isPlainObject(value) {
        return typeof value === 'object' && value !== null && !Array.isArray(value);
    }
    function isNonEmptyString(value) {
        return typeof value === 'string' && value.trim() !== '';
    }
    function isBlank(value) {
        return typeof value !== 'string' || value.trim() === '';
    }
    /* A defect in the island is a build defect, not a learner error: it throws
     * with the path and the defect code so the fixture names the exact hole. */
    function defect(path, code, detail) {
        return fail(REGISTRY_INVALID, '#sim-response-types: ' + path + ' ' + detail + ' (kods ' + code + '); reģistrs nav ielādējams.', { defect: code, path: path });
    }
    function requireString(holder, key, path) {
        const value = holder[key];
        if (!isNonEmptyString(value)) {
            defect(path + '.' + key, 'missing_string', 'neprasa nepieciešamo tekstu');
        }
        return value;
    }
    function requireBoolean(holder, key, path) {
        if (typeof holder[key] !== 'boolean') {
            defect(path + '.' + key, 'missing_boolean', 'neprasa nepieciešamo loģisko vērtību');
        }
        return holder[key];
    }
    function requireStringArray(holder, key, path) {
        const value = holder[key];
        if (!Array.isArray(value) || value.length === 0) {
            defect(path + '.' + key, 'missing_list', 'neprasa nepieciešamo sarakstu');
        }
        const list = value;
        const out = [];
        for (let i = 0; i < list.length; i += 1) {
            if (!isNonEmptyString(list[i])) {
                defect(path + '.' + key + '[' + i + ']', 'bad_list_item', 'satur tukšu elementu');
            }
            out.push(list[i]);
        }
        return out;
    }
    function deepFreeze(value) {
        if (value === null || typeof value !== 'object' || Object.isFrozen(value)) {
            return value;
        }
        const keys = Object.keys(value);
        for (let i = 0; i < keys.length; i += 1) {
            deepFreeze(value[keys[i]]);
        }
        return Object.freeze(value);
    }
    /* ------------------------------------------------------- island validation */
    function validateRule(rule, path) {
        const model = rule.model;
        if (typeof model !== 'string' || MODELS.indexOf(model) === -1) {
            defect(path + '.model', 'unknown_model', 'nosauc nezināmu pabeigtības modeli ' + String(model));
        }
        if (model === 'graph') {
            const variants = rule.variant_rules;
            if (!isPlainObject(variants)) {
                defect(path + '.variant_rules', 'missing_variant_rules', 'grafa modelim trūkst variantu noteikumu');
            }
            const names = Object.keys(variants);
            if (names.length === 0) {
                defect(path + '.variant_rules', 'empty_variant_rules', 'grafa modelim nav neviena varianta');
            }
            for (let i = 0; i < names.length; i += 1) {
                const variantRule = variants[names[i]];
                if (!isPlainObject(variantRule)) {
                    defect(path + '.variant_rules.' + names[i], 'bad_variant_rule', 'nav objekts');
                }
                const mode = variantRule.mode;
                if (typeof mode !== 'string' || GRAPH_MODES.indexOf(mode) === -1) {
                    defect(path + '.variant_rules.' + names[i] + '.mode', 'unknown_graph_mode', 'nosauc nezināmu grafa režīmu');
                }
                const emits = variantRule.emits;
                if (!Array.isArray(emits) || emits.length === 0) {
                    defect(path + '.variant_rules.' + names[i] + '.emits', 'missing_emits', 'nenosauc izsūtāmos kļūdu id');
                }
            }
            return;
        }
        const emits = rule.emits;
        if (!Array.isArray(emits) || emits.length === 0) {
            defect(path + '.emits', 'missing_emits', 'nenosauc izsūtāmos kļūdu id');
        }
    }
    function collectEmits(rule, out) {
        if (Array.isArray(rule.emits)) {
            const list = rule.emits;
            for (let i = 0; i < list.length; i += 1) {
                if (typeof list[i] === 'string' && out.indexOf(list[i]) === -1) {
                    out.push(list[i]);
                }
            }
        }
        if (isPlainObject(rule.variant_rules)) {
            const variants = rule.variant_rules;
            const names = Object.keys(variants);
            for (let i = 0; i < names.length; i += 1) {
                collectEmits(variants[names[i]], out);
            }
        }
    }
    function validateContract(entry, typeId) {
        const path = 'types.' + typeId;
        requireString(entry, 'id', path);
        if (entry.id !== typeId) {
            defect(path + '.id', 'id_mismatch', 'nesakrīt ar atslēgu ' + typeId);
        }
        requireString(entry, 'name_key', path);
        requireString(entry, 'renderer_key', path);
        requireString(entry, 'engine_binding', path);
        const kind = requireString(entry, 'payload_kind', path);
        if (PAYLOAD_KINDS.indexOf(kind) === -1) {
            defect(path + '.payload_kind', 'unknown_payload_kind', 'nosauc nezināmu datu klasi ' + kind);
        }
        if (!has(entry, 'payload_variant')) {
            defect(path + '.payload_variant', 'missing_variant_slot', 'neprasa varianta lauku');
        }
        if (entry.payload_variant !== null && !isNonEmptyString(entry.payload_variant)) {
            defect(path + '.payload_variant', 'bad_variant', 'nav ne null, ne teksts');
        }
        requireBoolean(entry, 'required_per_form', path);
        const completed = requireBoolean(entry, 'completed_type', path);
        if (completed !== (COMPLETED_TYPES.indexOf(typeId) !== -1)) {
            defect(path + '.completed_type', 'completed_type_drift', 'nesakrīt ar saldēto septiņu tipu sarakstu');
        }
        const grading = entry.grading_binding;
        if (!isPlainObject(grading)) {
            defect(path + '.grading_binding', 'missing_grading_binding', 'neprasa vērtēšanas piesaisti');
        }
        const gradingObject = grading;
        const gradingClass = requireString(gradingObject, 'class', path + '.grading_binding');
        if (GRADING_CLASSES.indexOf(gradingClass) === -1) {
            defect(path + '.grading_binding.class', 'unknown_grading_class', 'nosauc nezināmu vērtēšanas klasi');
        }
        requireString(gradingObject, 'engine', path + '.grading_binding');
        requireStringArray(gradingObject, 'consumes', path + '.grading_binding');
        const adapter = requireString(gradingObject, 'adapter', path + '.grading_binding');
        if (adapter !== 'none') {
            defect(path + '.grading_binding.adapter', 'adapter_required', 'prasa adapteri "' + adapter + '": datu līgums neatbilst dzinējam un to nedrīkst slēpt');
        }
        const fields = entry.fields;
        if (!Array.isArray(fields) || fields.length === 0) {
            defect(path + '.fields', 'missing_fields', 'neprasa neviena lauka veidnes');
        }
        const fieldList = fields;
        for (let i = 0; i < fieldList.length; i += 1) {
            const fieldPath = path + '.fields[' + i + ']';
            if (!isPlainObject(fieldList[i])) {
                defect(fieldPath, 'bad_field', 'nav objekts');
            }
            const field = fieldList[i];
            const keys = ['role', 'source', 'control', 'value_type', 'label_key', 'payload_path'];
            for (let k = 0; k < keys.length; k += 1) {
                requireString(field, keys[k], fieldPath);
            }
            requireBoolean(field, 'required', fieldPath);
            const labelKey = field.label_key;
            if (labelKey.indexOf('input.') !== 0) {
                defect(fieldPath + '.label_key', 'outside_input_namespace', 'neietilpst input.* nosaukumtelpā (' + labelKey + ')');
            }
        }
        const rule = entry.completion_rule;
        if (!isPlainObject(rule)) {
            defect(path + '.completion_rule', 'missing_completion_rule', 'neprasa pabeigtības noteikumu');
        }
        const ruleObject = rule;
        validateRule(ruleObject, path + '.completion_rule');
        const surfaces = requireStringArray(entry, 'error_surfaces', path);
        for (let i = 0; i < surfaces.length; i += 1) {
            if (INPUTS_ERROR_IDS.indexOf(surfaces[i]) === -1) {
                defect(path + '.error_surfaces[' + i + ']', 'unknown_error_id', 'nosauc id ' + surfaces[i] + ', kas nav saldētajā kļūdu vārdnīcā');
            }
            if (surfaces.indexOf(surfaces[i]) !== i) {
                defect(path + '.error_surfaces[' + i + ']', 'duplicate_error_id', 'atkārto id ' + surfaces[i]);
            }
        }
        const emits = [];
        collectEmits(ruleObject, emits);
        for (let i = 0; i < emits.length; i += 1) {
            if (surfaces.indexOf(emits[i]) === -1) {
                defect(path + '.completion_rule', 'emit_not_declared', 'izsūta ' + emits[i] + ', bet tas nav error_surfaces sarakstā');
            }
        }
        const feedback = entry.feedback_keys;
        if (!isPlainObject(feedback)) {
            defect(path + '.feedback_keys', 'missing_feedback_keys', 'neprasa atgriezeniskās saites atslēgas');
        }
        const feedbackObject = feedback;
        const feedbackIds = Object.keys(feedbackObject);
        if (feedbackIds.length !== surfaces.length) {
            defect(path + '.feedback_keys', 'feedback_coverage', 'nesedz tieši error_surfaces sarakstu');
        }
        for (let i = 0; i < surfaces.length; i += 1) {
            if (!has(feedbackObject, surfaces[i])) {
                defect(path + '.feedback_keys', 'feedback_coverage', 'trūkst atslēgas priekš ' + surfaces[i]);
            }
            if (!isNonEmptyString(feedbackObject[surfaces[i]])) {
                defect(path + '.feedback_keys.' + surfaces[i], 'bad_feedback_key', 'nav teksts');
            }
        }
        const keyboard = entry.keyboard;
        if (!isPlainObject(keyboard)) {
            defect(path + '.keyboard', 'missing_keyboard', 'neprasa tastatūras līgumu');
        }
        const keyboardObject = keyboard;
        requireString(keyboardObject, 'path_key', path + '.keyboard');
        requireString(keyboardObject, 'parity_key', path + '.keyboard');
        requireString(keyboardObject, 'abort_rule_key', path + '.keyboard');
        const alternative = entry.accessible_alternative;
        if (!isPlainObject(alternative)) {
            defect(path + '.accessible_alternative', 'missing_alternative', 'neprasa pieejamo alternatīvu');
        }
        const alternativeObject = alternative;
        requireString(alternativeObject, 'label_key', path + '.accessible_alternative');
        requireStringArray(alternativeObject, 'term_keys', path + '.accessible_alternative');
        return entry;
    }
    function validateIsland(document) {
        if (!isPlainObject(document)) {
            defect('(root)', 'not_an_object', 'sakne nav JSON objekts');
        }
        const doc = document;
        if (doc.schema_version !== ISLAND_VERSION) {
            defect('schema_version', 'schema_version', 'nav ' + String(ISLAND_VERSION));
        }
        if (doc.island_id !== ISLAND_ID) {
            defect('island_id', 'island_id', 'nav "' + ISLAND_ID + '"');
        }
        requireString(doc, 'owner', '(root)');
        requireString(doc, 'status', '(root)');
        if (!isPlainObject(doc.types)) {
            defect('types', 'missing_types', 'neprasa tipu karti');
        }
        const types = doc.types;
        const keys = Object.keys(types);
        if (keys.length !== TYPE_IDS.length) {
            const unknown = [];
            const absent = [];
            for (let i = 0; i < keys.length; i += 1) {
                if (TYPE_IDS.indexOf(keys[i]) === -1) {
                    unknown.push(keys[i]);
                }
            }
            for (let i = 0; i < TYPE_IDS.length; i += 1) {
                if (!has(types, TYPE_IDS[i])) {
                    absent.push(TYPE_IDS[i]);
                }
            }
            defect('types', 'type_count', 'satur ' + keys.length + ' tipus, nevis ' + TYPE_IDS.length +
                '; nezināmi id: [' + unknown.sort().join(', ') + ']; trūkst: [' + absent.join(', ') + ']');
        }
        for (let i = 0; i < TYPE_IDS.length; i += 1) {
            if (!has(types, TYPE_IDS[i])) {
                defect('types', 'missing_type', 'trūkst tipa ' + TYPE_IDS[i]);
            }
            if (!isPlainObject(types[TYPE_IDS[i]])) {
                defect('types.' + TYPE_IDS[i], 'bad_type', 'nav objekts');
            }
            validateContract(types[TYPE_IDS[i]], TYPE_IDS[i]);
        }
        const completed = doc.completed_types;
        if (!Array.isArray(completed) || completed.length !== COMPLETED_TYPES.length) {
            defect('completed_types', 'completed_types', 'nesakrīt ar septiņu tipu sarakstu');
        }
        for (let i = 0; i < COMPLETED_TYPES.length; i += 1) {
            if (completed[i] !== COMPLETED_TYPES[i]) {
                defect('completed_types[' + i + ']', 'completed_types', 'nesakrīt ar ' + COMPLETED_TYPES[i]);
            }
        }
        if (!Array.isArray(doc.conflicts) || doc.conflicts.length === 0) {
            defect('conflicts', 'missing_conflicts', 'neprasa konfliktu sarakstu');
        }
        if (!isPlainObject(doc.announcement_keys)) {
            defect('announcement_keys', 'missing_announcement_keys', 'neprasa paziņojumu atslēgu bloku');
        }
        const announcements = doc.announcement_keys;
        for (let i = 0; i < ANNOUNCEMENT_KEYS.length; i += 1) {
            const name = ANNOUNCEMENT_KEYS[i];
            if (!isNonEmptyString(announcements[name]) || announcements[name].indexOf('input.') !== 0) {
                defect('announcement_keys.' + name, 'bad_announcement_key', 'neprasa input.* atslēgu paziņojumam "' + name + '"');
            }
        }
        /* The error-message index must be a function: one id, one key. */
        const index = {};
        for (let i = 0; i < TYPE_IDS.length; i += 1) {
            const entry = types[TYPE_IDS[i]];
            for (let k = 0; k < entry.error_surfaces.length; k += 1) {
                const id = entry.error_surfaces[k];
                const key = entry.feedback_keys[id];
                if (has(index, id) && index[id] !== key) {
                    defect('types.' + TYPE_IDS[i] + '.feedback_keys.' + id, 'feedback_key_conflict', 'kartē ' + id + ' uz ' + key + ', bet citur uz ' + index[id]);
                }
                index[id] = key;
            }
        }
        errorIndex = index;
        return deepFreeze({
            schema_version: doc.schema_version,
            island_id: doc.island_id,
            owner: doc.owner,
            status: doc.status,
            completed_types: completed.slice(),
            announcement_keys: announcements,
            conflicts: doc.conflicts.slice(),
            types: types
        });
    }
    /* ----------------------------------------------------------- term support */
    function loadTermBank(source) {
        if (source === null || source === undefined) {
            termBank = null;
            return;
        }
        const bank = {};
        if (isPlainObject(source) && Array.isArray(source.terms)) {
            const list = source.terms;
            for (let i = 0; i < list.length; i += 1) {
                if (isPlainObject(list[i])) {
                    const entry = list[i];
                    if (isNonEmptyString(entry.key) && isNonEmptyString(entry.text_lv)) {
                        bank[entry.key] = { text_lv: entry.text_lv };
                    }
                }
            }
        }
        else if (isPlainObject(source) && isPlainObject(source.byKey)) {
            const byKey = source.byKey;
            const keys = Object.keys(byKey);
            for (let i = 0; i < keys.length; i += 1) {
                const entry = byKey[keys[i]];
                if (isPlainObject(entry) && isNonEmptyString(entry.text_lv)) {
                    bank[keys[i]] = { text_lv: entry.text_lv };
                }
            }
        }
        else if (isPlainObject(source)) {
            const keys = Object.keys(source);
            for (let i = 0; i < keys.length; i += 1) {
                const value = source[keys[i]];
                if (typeof value === 'string') {
                    bank[keys[i]] = { text_lv: value };
                }
                else if (isPlainObject(value) && isNonEmptyString(value.text_lv)) {
                    bank[keys[i]] = { text_lv: value.text_lv };
                }
            }
        }
        else {
            fail(REGISTRY_INVALID, '#sim-terms nav ne masīvs, ne karte; terminu banka nav ielādējama.', {
                defect: 'term_bank_shape'
            });
        }
        termBank = bank;
    }
    function termText(key) {
        if (termBank === null) {
            fail(TERM_UNRESOLVED, 'Terminu banka nav ielādēta, tāpēc atslēgu "' + key + '" nevar atrisināt.', {
                key: key, reason: 'terms_not_loaded'
            });
        }
        const bank = termBank;
        if (!has(bank, key)) {
            fail(TERM_UNRESOLVED, '#sim-terms trūkst atslēgas "' + key + '"; tukšs nosaukums netiek izgudrots.', {
                key: key, reason: 'missing_key'
            });
        }
        return bank[key].text_lv;
    }
    function substitute(pattern, values) {
        return pattern.replace(/\{([a-z_]+)\}/g, function (_token, name) {
            const value = has(values, name) ? values[name] : '';
            return isNonEmptyString(value) ? value : '—';
        });
    }
    function labelFor(labelKey, values) {
        return substitute(termText(labelKey), values);
    }
    /* ------------------------------------------------------------ entry access */
    function selectContract(typeId, contract) {
        if (island === null) {
            fail(REGISTRY_INVALID, '#sim-response-types nav ielādēta; contractFor nav izpildāms.', {
                defect: 'not_loaded'
            });
        }
        const types = island.types;
        if (typeof typeId !== 'string' || !has(types, typeId)) {
            fail(UNKNOWN_TYPE, 'Nezināms atbildes tips "' + String(typeId) + '": reģistrā #sim-response-types ' +
                'šāda tipa nav, un rezerves ievades lauks netiek renderēts.', { type_id: String(typeId) });
        }
        const entry = types[typeId];
        if (contract === null || contract === undefined) {
            return entry;
        }
        if (!isPlainObject(contract)) {
            fail(REGISTRY_INVALID, 'Pabeigtības modelim nodotā līgums nav objekts.', { defect: 'bad_contract' });
        }
        if (contract.id !== typeId) {
            fail(REGISTRY_INVALID, 'Līgums tipam "' + typeId + '" nosauc tipu "' + String(contract.id) + '".', {
                defect: 'contract_mismatch', type_id: typeId
            });
        }
        if (!isPlainObject(contract.completion_rule) ||
            !isNonEmptyString(contract.completion_rule.model)) {
            fail(REGISTRY_INVALID, 'Līgumam tipam "' + typeId + '" trūkst completion_rule.model.', {
                defect: 'bad_contract', type_id: typeId
            });
        }
        return contract;
    }
    /* -------------------------------------------------------------- resolving */
    function resolvePath(source, path) {
        const parts = path.split('.');
        let cursor = { instance: source };
        for (let i = 0; i < parts.length; i += 1) {
            if (cursor === null || cursor === undefined || typeof cursor !== 'object') {
                return null;
            }
            cursor = cursor[parts[i]];
        }
        return cursor === undefined ? null : cursor;
    }
    function arrayAt(source, path) {
        const value = resolvePath(source, path);
        return Array.isArray(value) ? value : null;
    }
    function idOf(item) {
        if (typeof item === 'string') {
            return item;
        }
        if (!isPlainObject(item)) {
            return '';
        }
        const record = item;
        const keys = ['field_id', 'step_id', 'id', 'item_id', 'option_id', 'part_id', 'left_id'];
        for (let i = 0; i < keys.length; i += 1) {
            if (isNonEmptyString(record[keys[i]])) {
                return record[keys[i]];
            }
        }
        return '';
    }
    function nameOf(item) {
        if (!isPlainObject(item)) {
            return '';
        }
        const record = item;
        const keys = ['label_lv', 'prompt_lv', 'text_lv', 'label'];
        for (let i = 0; i < keys.length; i += 1) {
            if (isNonEmptyString(record[keys[i]])) {
                return record[keys[i]];
            }
        }
        return '';
    }
    function instanceList(instance, path) {
        return arrayAt(instance, path);
    }
    /* ---------------------------------------------------------------- verdicts */
    function errorRecord(contract, id, field) {
        const keys = contract.feedback_keys;
        return { id: id, field: field, message_key: has(keys, id) ? keys[id] : '' };
    }
    function verdict(_contract, status, missing, errors) {
        return { status: status, missing: missing, errors: errors };
    }
    function invalid(contract, id, field) {
        return verdict(contract, 'invalid', [], [errorRecord(contract, id, field)]);
    }
    /* The structural error id for a kind whose payload body is not readable. */
    function malformedId(contract) {
        if (contract.payload_kind === 'graph') {
            return 'E_GRAPH_PAYLOAD_MALFORMED';
        }
        return 'UNREADABLE_INPUT';
    }
    function missingFor(rule, slot, values, fieldId) {
        const missingMap = (rule.missing || {});
        const key = has(missingMap, slot) ? missingMap[slot] : '';
        return { field_id: fieldId, name: labelFor(key, values) };
    }
    function emptyResult() {
        return { missing: [], errors: [], fatal: false };
    }
    function malformed(result, contract, field, id) {
        result.errors.push(errorRecord(contract, id === undefined ? malformedId(contract) : id, field));
        result.fatal = true;
        return result;
    }
    function requireFieldIds(instance, path, result, contract) {
        const list = instanceList(instance, path);
        if (list === null) {
            malformed(result, contract, path);
            return null;
        }
        return list;
    }
    function stringMapCheck(value, result, contract, field) {
        if (!isPlainObject(value)) {
            malformed(result, contract, field);
            return null;
        }
        const record = value;
        const keys = Object.keys(record);
        for (let i = 0; i < keys.length; i += 1) {
            if (typeof record[keys[i]] !== 'string') {
                malformed(result, contract, field + '.' + keys[i]);
                return null;
            }
        }
        return record;
    }
    /* numeric / numeric-with-steps ------------------------------------------- */
    function modelNumeric(contract, rule, instance, payload) {
        const result = emptyResult();
        const values = stringMapCheck(payload[rule.values_path], result, contract, rule.values_path);
        if (values === null) {
            return result;
        }
        const fields = requireFieldIds(instance, rule.fields_from, result, contract);
        if (fields === null) {
            return result;
        }
        const groups = [fields];
        if (rule.include_steps === true) {
            const steps = requireFieldIds(instance, rule.steps_from, result, contract);
            if (steps === null) {
                return result;
            }
            groups.push(steps);
        }
        for (let g = 0; g < groups.length; g += 1) {
            const slot = g === 0 ? 'value' : 'step';
            const group = groups[g];
            for (let i = 0; i < group.length; i += 1) {
                const id = idOf(group[i]);
                if (id === '') {
                    result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.fields_from));
                    result.fatal = true;
                    return result;
                }
                if (!has(values, id) || isBlank(values[id])) {
                    const label = nameOf(group[i]);
                    result.missing.push(missingFor(rule, slot, { label: label === '' ? id : label }, id));
                }
            }
        }
        return result;
    }
    /* vector ---------------------------------------------------------------- */
    function modelVector(contract, rule, instance, payload) {
        const result = emptyResult();
        const raw = payload[rule.vector_path];
        const species = requireFieldIds(instance, rule.species_from, result, contract);
        if (species === null) {
            return result;
        }
        if (!Array.isArray(raw)) {
            return malformed(result, contract, rule.vector_path);
        }
        const vector = raw;
        for (let i = 0; i < species.length; i += 1) {
            const code = idOf(species[i]) === '' ? String(species[i]) : idOf(species[i]);
            if (i >= vector.length || isBlank(vector[i])) {
                result.missing.push(missingFor(rule, 'coefficient', { species: code }, 'vector[' + i + ']'));
            }
            else if (typeof vector[i] !== 'string') {
                return malformed(result, contract, rule.vector_path + '[' + i + ']');
            }
        }
        const extra = rule.required_fields;
        if (Array.isArray(extra)) {
            const list = extra;
            for (let i = 0; i < list.length; i += 1) {
                const spec = list[i];
                const fieldId = spec.field_id;
                const labelKey = spec.label_key;
                const value = payload[fieldId];
                if (isBlank(value)) {
                    result.missing.push({ field_id: fieldId, name: labelFor(labelKey, {}) });
                }
                else if (typeof value !== 'string') {
                    return malformed(result, contract, fieldId);
                }
            }
        }
        return result;
    }
    /* rows ------------------------------------------------------------------ */
    function modelRows(contract, rule, instance, payload) {
        const result = emptyResult();
        const rows = stringMapCheck(payload[rule.rows_path], result, contract, rule.rows_path);
        if (rows === null) {
            return result;
        }
        const steps = requireFieldIds(instance, rule.steps_from, result, contract);
        if (steps === null) {
            return result;
        }
        for (let i = 0; i < steps.length; i += 1) {
            const id = idOf(steps[i]);
            if (id === '') {
                result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.steps_from));
                result.fatal = true;
                return result;
            }
            if (!has(rows, id) || isBlank(rows[id])) {
                const label = nameOf(steps[i]);
                result.missing.push(missingFor(rule, 'row', { step: label === '' ? id : label }, id));
            }
        }
        return result;
    }
    /* pairs (Q06) ----------------------------------------------------------- */
    function modelPairs(contract, rule, instance, payload) {
        const result = emptyResult();
        const raw = payload[rule.pairs_path];
        if (!Array.isArray(raw)) {
            return malformed(result, contract, rule.pairs_path);
        }
        const pairs = raw;
        const assigned = {};
        for (let i = 0; i < pairs.length; i += 1) {
            if (!isPlainObject(pairs[i])) {
                return malformed(result, contract, rule.pairs_path + '[' + i + ']');
            }
            const pair = pairs[i];
            if (typeof pair.left_id !== 'string' || typeof pair.right_id !== 'string') {
                return malformed(result, contract, rule.pairs_path + '[' + i + ']');
            }
            if (isNonEmptyString(pair.right_id)) {
                assigned[pair.left_id] = pair.right_id;
            }
        }
        const left = requireFieldIds(instance, rule.left_from, result, contract);
        if (left === null) {
            return result;
        }
        for (let i = 0; i < left.length; i += 1) {
            const id = idOf(left[i]);
            if (id === '') {
                result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.left_from));
                result.fatal = true;
                return result;
            }
            if (!has(assigned, id)) {
                const label = nameOf(left[i]);
                result.missing.push(missingFor(rule, 'pair', { left: label === '' ? id : label }, id));
            }
        }
        return result;
    }
    /* order (Q08) ----------------------------------------------------------- */
    function modelOrder(contract, rule, instance, payload) {
        const result = emptyResult();
        const raw = payload[rule.order_path];
        if (!Array.isArray(raw)) {
            return malformed(result, contract, rule.order_path);
        }
        const order = raw;
        const count = {};
        for (let i = 0; i < order.length; i += 1) {
            if (typeof order[i] !== 'string') {
                return malformed(result, contract, rule.order_path + '[' + i + ']');
            }
            count[order[i]] = (count[order[i]] || 0) + 1;
        }
        const items = requireFieldIds(instance, rule.items_from, result, contract);
        if (items === null) {
            return result;
        }
        for (let i = 0; i < items.length; i += 1) {
            const id = idOf(items[i]);
            if (id === '') {
                result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.items_from));
                result.fatal = true;
                return result;
            }
            if (!has(count, id) || count[id] !== 1) {
                const label = nameOf(items[i]);
                result.missing.push(missingFor(rule, 'order_item', { item: label === '' ? id : label }, id));
            }
        }
        if (rule.explanation_required === true && isBlank(payload[rule.explanation_path])) {
            result.missing.push(missingFor(rule, 'explanation', {}, rule.explanation_path));
        }
        return result;
    }
    /* selection (Q07, Q14, Q18) -------------------------------------------- */
    function modelSelection(contract, rule, instance, payload) {
        const result = emptyResult();
        const raw = payload[rule.selection_path];
        if (!Array.isArray(raw)) {
            return malformed(result, contract, rule.selection_path);
        }
        const selected = raw;
        for (let i = 0; i < selected.length; i += 1) {
            if (typeof selected[i] !== 'string') {
                return malformed(result, contract, rule.selection_path + '[' + i + ']');
            }
        }
        if (selected.length === 0) {
            result.missing.push(missingFor(rule, 'selection', {}, rule.selection_path));
        }
        if (rule.justification_path !== undefined) {
            const options = instanceList(instance, rule.options_from);
            if (options === null) {
                return malformed(result, contract, rule.options_from);
            }
            if (selected.length > 0) {
                const known = {};
                for (let i = 0; i < options.length; i += 1) {
                    known[idOf(options[i])] = true;
                }
                for (let i = 0; i < selected.length; i += 1) {
                    if (!has(known, selected[i])) {
                        return malformed(result, contract, rule.selection_path + '[' + i + ']');
                    }
                }
            }
            const requires = resolvePath(instance, rule.justification_required_from);
            if (requires === true && isBlank(payload[rule.justification_path])) {
                result.missing.push(missingFor(rule, 'justification', {}, rule.justification_path));
            }
        }
        return result;
    }
    /* text (Q15, Q16) ------------------------------------------------------- */
    function modelText(contract, rule, payload) {
        const result = emptyResult();
        const text = payload[rule.text_path];
        if (text === undefined || text === null) {
            result.missing.push(missingFor(rule, 'text', {}, rule.text_path));
            if (rule.blank_error !== undefined) {
                result.errors.push(errorRecord(contract, rule.blank_error, rule.text_path));
            }
            return result;
        }
        if (typeof text !== 'string') {
            return malformed(result, contract, rule.text_path);
        }
        const minimum = typeof rule.min_chars === 'number' ? rule.min_chars : 1;
        if (text.trim().length < minimum) {
            result.missing.push(missingFor(rule, 'text', {}, rule.text_path));
            if (rule.blank_error !== undefined) {
                result.errors.push(errorRecord(contract, rule.blank_error, rule.text_path));
            }
        }
        return result;
    }
    /* template (Q03) -------------------------------------------------------- */
    function modelTemplate(contract, rule, instance, payload) {
        const result = emptyResult();
        if (isBlank(payload[rule.choice_path])) {
            result.missing.push(missingFor(rule, 'template', {}, rule.choice_path));
        }
        else if (typeof payload[rule.choice_path] !== 'string') {
            return malformed(result, contract, rule.choice_path);
        }
        const fillIns = stringMapCheck(payload[rule.fill_ins_path], result, contract, rule.fill_ins_path);
        if (fillIns === null) {
            return result;
        }
        const steps = requireFieldIds(instance, rule.steps_from, result, contract);
        if (steps === null) {
            return result;
        }
        for (let i = 0; i < steps.length; i += 1) {
            const id = idOf(steps[i]);
            if (id === '') {
                result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.steps_from));
                result.fatal = true;
                return result;
            }
            if (!has(fillIns, id) || isBlank(fillIns[id])) {
                const label = nameOf(steps[i]);
                result.missing.push(missingFor(rule, 'fill_in', { slot: label === '' ? id : label }, rule.fill_ins_path + '.' + id));
            }
        }
        if (isBlank(payload[rule.conserved_path])) {
            result.missing.push(missingFor(rule, 'conserved', {}, rule.conserved_path));
        }
        else if (typeof payload[rule.conserved_path] !== 'string') {
            return malformed(result, contract, rule.conserved_path);
        }
        return result;
    }
    /* pair_map (Q17) -------------------------------------------------------- */
    function modelPairMap(contract, rule, instance, payload) {
        const result = emptyResult();
        const map = stringMapCheck(payload[rule.map_path], result, contract, rule.map_path);
        if (map === null) {
            return result;
        }
        const steps = requireFieldIds(instance, rule.steps_from, result, contract);
        if (steps === null) {
            return result;
        }
        for (let i = 0; i < steps.length; i += 1) {
            const id = idOf(steps[i]);
            if (id === '') {
                result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.steps_from));
                result.fatal = true;
                return result;
            }
            if (!has(map, id) || isBlank(map[id])) {
                const label = nameOf(steps[i]);
                result.missing.push(missingFor(rule, 'step', { step: label === '' ? id : label }, id));
            }
        }
        const parts = instanceList(instance, rule.structure_parts_from);
        if (parts !== null && parts.length > 0) {
            const structure = payload[rule.structure_path];
            const placed = {};
            if (isPlainObject(structure)) {
                const record = structure;
                const keys = Object.keys(record);
                for (let i = 0; i < keys.length; i += 1) {
                    placed[keys[i]] = record[keys[i]];
                }
            }
            else if (structure !== undefined && structure !== null) {
                return malformed(result, contract, rule.structure_path);
            }
            for (let i = 0; i < parts.length; i += 1) {
                const partId = idOf(parts[i]);
                if (partId === '') {
                    result.errors.push(errorRecord(contract, 'UNREADABLE_INPUT', rule.structure_parts_from));
                    result.fatal = true;
                    return result;
                }
                if (!has(placed, partId) || isBlank(placed[partId])) {
                    const label = nameOf(parts[i]);
                    result.missing.push(missingFor(rule, 'structure_part', { part: label === '' ? partId : label }, rule.structure_path + '.' + partId));
                }
            }
        }
        return result;
    }
    /* graph: record / plot_state / read ------------------------------------ */
    function pointIsNumeric(point) {
        if (Array.isArray(point)) {
            const pair = point;
            return pair.length >= 2 && typeof pair[0] === 'number' && typeof pair[1] === 'number' &&
                isFinite(pair[0]) && isFinite(pair[1]);
        }
        if (isPlainObject(point)) {
            const record = point;
            return typeof record.x === 'number' && typeof record.y === 'number' &&
                isFinite(record.x) && isFinite(record.y);
        }
        return false;
    }
    function declaredPointCount(instance, rule) {
        const declared = resolvePath(instance, rule.declared_points_from);
        if (typeof declared === 'number' && isFinite(declared) && declared > 0) {
            return declared;
        }
        if (rule.fallback_points_from !== undefined) {
            const fallback = arrayAt(instance, rule.fallback_points_from);
            if (fallback !== null && fallback.length > 0) {
                return fallback.length;
            }
        }
        const primary = arrayAt(instance, rule.declared_points_from);
        if (primary !== null && primary.length > 0) {
            return primary.length;
        }
        /* The N18 payload floor: fewer than two points is E_GRAPH_EMPTY_SUBMISSION. */
        return 2;
    }
    function modelGraphRecord(contract, rule, instance, payload) {
        const result = emptyResult();
        const declared = declaredPointCount(instance, rule);
        const record = payload[rule.record_path];
        if (!isPlainObject(record)) {
            result.missing.push(missingFor(rule, 'record', {}, rule.record_path));
        }
        else {
            const points = record.points;
            if (!Array.isArray(points)) {
                result.missing.push(missingFor(rule, 'record', {}, rule.record_path + '.points'));
            }
            else {
                const list = points;
                for (let i = 0; i < list.length; i += 1) {
                    if (!pointIsNumeric(list[i])) {
                        return malformed(result, contract, rule.record_path + '.points[' + i + ']');
                    }
                }
                if (list.length < declared) {
                    result.missing.push(missingFor(rule, 'point_count', { count: String(declared) }, rule.record_path + '.points'));
                }
            }
        }
        if (rule.require_draw === false) {
            return result;
        }
        const draw = payload[rule.draw_path];
        if (!isPlainObject(draw)) {
            result.missing.push(missingFor(rule, 'draw', {}, rule.draw_path));
            return result;
        }
        const body = draw;
        if (body.schema_id !== rule.draw_schema) {
            return malformed(result, contract, rule.draw_path + '.schema_id', 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        const points = body.points;
        if (!Array.isArray(points)) {
            return malformed(result, contract, rule.draw_path + '.points', 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        const list = points;
        for (let i = 0; i < list.length; i += 1) {
            if (!pointIsNumeric(list[i])) {
                return malformed(result, contract, rule.draw_path + '.points[' + i + ']', 'E_GRAPH_PAYLOAD_MALFORMED');
            }
        }
        const axes = body.axes;
        if (!isPlainObject(axes) || !isPlainObject(axes.x) ||
            !isPlainObject(axes.y)) {
            return malformed(result, contract, rule.draw_path + '.axes', 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        if (!isPlainObject(body.span) || !isPlainObject(body.grid)) {
            return malformed(result, contract, rule.draw_path + '.span', 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        if (list.length < 2) {
            return malformed(result, contract, rule.draw_path + '.points', 'E_GRAPH_EMPTY_SUBMISSION');
        }
        return result;
    }
    function modelPlotState(contract, rule, instance, payload) {
        const result = emptyResult();
        const declared = declaredPointCount(instance, rule);
        const plot = payload[rule.plot_path];
        if (!isPlainObject(plot)) {
            result.missing.push(missingFor(rule, 'point_count', { count: String(declared) }, rule.plot_path));
            return result;
        }
        const points = plot.points;
        if (!Array.isArray(points)) {
            result.missing.push(missingFor(rule, 'point_count', { count: String(declared) }, rule.plot_path + '.points'));
            return result;
        }
        const list = points;
        for (let i = 0; i < list.length; i += 1) {
            if (!pointIsNumeric(list[i])) {
                return malformed(result, contract, rule.plot_path + '.points[' + i + ']', 'E_GRAPH_PAYLOAD_MALFORMED');
            }
        }
        if (list.length < declared) {
            result.missing.push(missingFor(rule, 'point_count', { count: String(declared) }, rule.plot_path + '.points'));
        }
        return result;
    }
    function modelGraphRead(contract, rule, instance, payload) {
        const result = emptyResult();
        const read = payload[rule.read_path];
        if (read !== undefined && read !== null && !isPlainObject(read)) {
            return malformed(result, contract, rule.read_path, 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        const body = isPlainObject(read) ? read : {};
        const axes = rule.axes;
        for (let i = 0; i < axes.length; i += 1) {
            const axis = axes[i];
            const value = body[axis];
            if (value === undefined || value === null) {
                const axisLabel = axis === 'x'
                    ? (isNonEmptyString(resolvePath(instance, 'payload.x_axis.label_lv')) ?
                        resolvePath(instance, 'payload.x_axis.label_lv') : 'x')
                    : (isNonEmptyString(resolvePath(instance, 'payload.y_axis.label_lv')) ?
                        resolvePath(instance, 'payload.y_axis.label_lv') : 'y');
                result.missing.push(missingFor(rule, 'axis', { axis: axisLabel }, rule.read_path + '.' + axis));
            }
            else if (typeof value !== 'string') {
                /* A number where the frozen vocabulary says raw string would break the
                 * input-preservation invariant, so it is a malformed payload. */
                return malformed(result, contract, rule.read_path + '.' + axis, 'E_GRAPH_PAYLOAD_MALFORMED');
            }
            else if (value.trim() === '') {
                const axisLabel = axis === 'x'
                    ? (isNonEmptyString(resolvePath(instance, 'payload.x_axis.label_lv')) ?
                        resolvePath(instance, 'payload.x_axis.label_lv') : 'x')
                    : (isNonEmptyString(resolvePath(instance, 'payload.y_axis.label_lv')) ?
                        resolvePath(instance, 'payload.y_axis.label_lv') : 'y');
                result.missing.push(missingFor(rule, 'axis', { axis: axisLabel }, rule.read_path + '.' + axis));
            }
        }
        const bindingField = rule.binding_field;
        const binding = body[bindingField];
        if (binding === undefined || binding === null) {
            result.missing.push(missingFor(rule, 'binding', {}, rule.read_path + '.' + bindingField));
        }
        else if (typeof binding !== 'string') {
            return malformed(result, contract, rule.read_path + '.' + bindingField, 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        else if (binding.trim() === '') {
            result.missing.push(missingFor(rule, 'binding', {}, rule.read_path + '.' + bindingField));
        }
        return result;
    }
    function modelGraph(contract, rule, instance, payload) {
        const variant = payload.variant;
        const rules = (rule.variant_rules || {});
        if (typeof variant !== 'string' || !has(rules, variant)) {
            const result = emptyResult();
            return malformed(result, contract, 'variant', 'E_GRAPH_PAYLOAD_MALFORMED');
        }
        const active = rules[variant];
        const mode = active.mode;
        if (mode === 'record') {
            return modelGraphRecord(contract, active, instance, payload);
        }
        if (mode === 'plot_state') {
            return modelPlotState(contract, active, instance, payload);
        }
        return modelGraphRead(contract, active, instance, payload);
    }
    /* -------------------------------------------------------------- the model */
    function completion(typeId, contract, instance, payload) {
        const entry = selectContract(typeId, contract);
        if (!isPlainObject(payload)) {
            return invalid(entry, 'UNREADABLE_INPUT', 'payload');
        }
        const body = payload;
        if (body.kind !== entry.payload_kind) {
            return invalid(entry, malformedId(entry), 'kind');
        }
        const rule = entry.completion_rule;
        if (!isPlainObject(instance)) {
            return invalid(entry, malformedId(entry), 'instance');
        }
        let result;
        if (rule.model === 'graph') {
            result = modelGraph(entry, rule, instance, body);
        }
        else {
            if (entry.payload_variant !== null) {
                if (body.variant !== entry.payload_variant) {
                    return invalid(entry, malformedId(entry), 'variant');
                }
            }
            else if (typeof body.variant === 'string' && body.variant !== '') {
                return invalid(entry, malformedId(entry), 'variant');
            }
            if (rule.model === 'numeric') {
                result = modelNumeric(entry, rule, instance, body);
            }
            else if (rule.model === 'vector') {
                result = modelVector(entry, rule, instance, body);
            }
            else if (rule.model === 'rows') {
                result = modelRows(entry, rule, instance, body);
            }
            else if (rule.model === 'pairs') {
                result = modelPairs(entry, rule, instance, body);
            }
            else if (rule.model === 'order') {
                result = modelOrder(entry, rule, instance, body);
            }
            else if (rule.model === 'selection') {
                result = modelSelection(entry, rule, instance, body);
            }
            else if (rule.model === 'text') {
                result = modelText(entry, rule, body);
            }
            else if (rule.model === 'template') {
                result = modelTemplate(entry, rule, instance, body);
            }
            else if (rule.model === 'pair_map') {
                result = modelPairMap(entry, rule, instance, body);
            }
            else {
                fail(REGISTRY_INVALID, 'Nezināms pabeigtības modelis "' + String(rule.model) + '" tipam ' + typeId + '.', {
                    defect: 'unknown_model', type_id: typeId
                });
            }
        }
        if (result.fatal) {
            return verdict(entry, 'invalid', result.missing, result.errors);
        }
        if (result.missing.length > 0) {
            return verdict(entry, 'incomplete', result.missing, result.errors);
        }
        return verdict(entry, 'complete', result.missing, result.errors);
    }
    /* ------------------------------------------------------------------- load */
    function load(islandJson, termsJson) {
        let document = islandJson;
        if (typeof document === 'string') {
            try {
                document = JSON.parse(document);
            }
            catch (error) {
                localDefect('(root)', 'invalid_json', 'nav nolasāms JSON (' +
                    String(error && error.message ? error.message : error) + ')');
            }
        }
        island = validateIsland(document);
        if (termsJson !== undefined) {
            loadTermBank(termsJson);
        }
        return islandSummary();
    }
    function localDefect(path, code, detail) {
        return defect(path, code, detail);
    }
    function islandSummary() {
        const loaded = island;
        if (loaded === null) {
            fail(REGISTRY_INVALID, '#sim-response-types nav ielādēta.', { defect: 'not_loaded' });
        }
        return {
            island_id: loaded.island_id,
            schema_version: loaded.schema_version,
            owner: loaded.owner,
            status: loaded.status,
            type_count: TYPE_IDS.length,
            type_ids: TYPE_IDS.slice(),
            completed_types: loaded.completed_types.slice()
        };
    }
    function contractFor(typeId) {
        return selectContract(typeId, null);
    }
    function errorSurfaces(typeId) {
        return selectContract(typeId, null).error_surfaces.slice();
    }
    /* The A.1.3 mapping: a type may only render the ids it declares, and the
     * record carries the term key the surface resolves through. */
    function errorSurfaceFor(typeId, errorId) {
        const entry = selectContract(typeId, null);
        if (typeof errorId !== 'string' || entry.error_surfaces.indexOf(errorId) === -1) {
            fail(UNKNOWN_ERROR_ID, 'Tips "' + typeId + '" nerāda kļūdas id "' + String(errorId) +
                '": reģistrā šādas kļūdas virsmas nav.', { type_id: typeId, error_id: String(errorId) });
        }
        return { id: errorId, message_key: entry.feedback_keys[errorId] };
    }
    function errorMessage(errorId, terms) {
        if (terms !== undefined) {
            loadTermBank(terms);
        }
        if (errorIndex === null) {
            fail(REGISTRY_INVALID, '#sim-response-types nav ielādēta; kļūdas tekstu nevar atrisināt.', {
                defect: 'not_loaded'
            });
        }
        const index = errorIndex;
        if (typeof errorId !== 'string' || !has(index, errorId)) {
            fail(UNKNOWN_ERROR_ID, 'Nezināms kļūdas id "' + String(errorId) + '": tas nav saldētajā ' +
                'atbilžu kļūdu vārdnīcā.', { error_id: String(errorId) });
        }
        return termText(index[errorId]);
    }
    function typeIds() {
        return TYPE_IDS.slice();
    }
    function completedTypes() {
        return COMPLETED_TYPES.slice();
    }
    /* The term key of one announcement string, so a component never composes
     * Latvian text of its own. */
    function announcementKey(name) {
        if (island === null) {
            fail(REGISTRY_INVALID, '#sim-response-types nav ielādēta; paziņojuma atslēgu nevar atrisināt.', {
                defect: 'not_loaded'
            });
        }
        const keys = island.announcement_keys;
        if (typeof name !== 'string' || !has(keys, name) || !isNonEmptyString(keys[name])) {
            fail(REGISTRY_INVALID, 'Nezināms paziņojuma vārds "' + String(name) + '" reģistrā #sim-response-types.', {
                defect: 'unknown_announcement', name: String(name)
            });
        }
        return keys[name];
    }
    function nameKey(typeId) {
        return selectContract(typeId, null).name_key;
    }
    function loadedTerms() {
        return termBank !== null;
    }
    /* -------------------------------------------------------------- published */
    const api = {
        ISLAND_ID: ISLAND_ID,
        ISLAND_VERSION: ISLAND_VERSION,
        REGISTRY_INVALID: REGISTRY_INVALID,
        UNKNOWN_TYPE: UNKNOWN_TYPE,
        INPUTS_ERROR_IDS: INPUTS_ERROR_IDS.slice(),
        MODULE_ERROR_IDS: MODULE_ERROR_IDS.slice(),
        InputsError: InputsError,
        load: load,
        loadTerms: loadTermBank,
        termsLoaded: loadedTerms,
        islandSummary: islandSummary,
        contractFor: contractFor,
        completion: completion,
        errorSurfaces: errorSurfaces,
        errorSurfaceFor: errorSurfaceFor,
        errorMessage: errorMessage,
        typeIds: typeIds,
        completedTypes: completedTypes,
        nameKey: nameKey,
        announcementKey: announcementKey
    };
    root.SimInputsRegistry = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
