"use strict";
/* N22-B — the eighteen response-input components.
 *
 * Ownership: N22-B (components and parity slice). This module is a pure
 * description layer: it reads a per-type contract out of the shipped
 * #sim-response-types registry (`data/response_types.json`, authoritative),
 * the bank instance, the current response payload and the term island, and
 * returns a JSON-serialisable RENDER DESCRIPTION. It never creates DOM, never
 * reads an island file, never writes the session and never grades.
 *
 * What it publishes (global `SimInputsComponents`):
 *
 *   render(typeId, contract, instance, payload, terms[, context])
 *       the per-type render description (fields, surfaces, live regions);
 *   keyboardContracts([typeId][, contract, terms])
 *       the documented key map per type (the accessibility contract);
 *   initialState(typeId, contract, instance)
 *       the interaction state an applyKey chain starts from;
 *   applyKey(typeId, contract, state, keyEvent)
 *       one keyboard step: next state + emitted interaction events;
 *   pointerEvent(typeId, contract, state, action)
 *       one pointer step over the same primitives (parity by construction);
 *   cancel(typeId, contract, state, reason)
 *       the abort path (navigate-away, Escape): discard, never emit partials;
 *   payloadOf(typeId, contract, state)
 *       the answer payload in the FROZEN session vocabulary;
 *   committed(typeId, contract, state)
 *       what is actually committed (placements, drawn payload, pairs, order);
 *   compose(parts[, terms])
 *       the composed-response container (per-part labels, per-part
 *       completion, ordered payload map);
 *   completionOf(contract, payload[, instance])
 *       the completion verdict (defers to SimInputsRegistry.completion when
 *       the registry module is loaded).
 *
 * Contract binding. The registry entry is the authority for *what* a widget
 * shows (controls, label term keys, payload paths, completion models, error
 * surfaces); this module is the authority for *which field ids* it needs.
 * A contract field template is expanded as follows (the documented rule):
 *
 *   repeat  iff  payload_path carries an element token ([index], [step_id],
 *                [field_id], [part_id])  or  value_type is "string_list";
 *   otherwise the template is one field and `source`/`option_source` only
 *                supplies its options.
 *
 * The element source is `source` (an instance path), or "none"/"static"/
 * "sim-figures" for the non-repeating cases. The renderer supplies the
 * `{slot}` values the label pattern asks for (for example {species} from the
 * species list, {step} from the authored step prompt), resolves them through
 * the term island and never writes a literal label.
 *
 * A field the renderer needs and the contract does not declare, a contract
 * field the renderer cannot place, a missing term key, or an unresolvable
 * slot all throw InputsError E_INPUTS_CONTRACT_VIOLATION (or
 * E_INPUTS_TERM_MISSING) naming the field id: a disagreement is loud, never a
 * silently degraded widget.
 *
 * Spatial capture delegates geometry to N18 (`SimGraphCapture` over
 * `SimGraphScoring`): the Q11 plot and its coordinate table feed one
 * device-free `sim-graph-draw-v1` payload, and neither device marks the
 * payload. The component never pre-validates geometry; the six E_GRAPH_*
 * validity classes belong to the engine (the registry lists them as the
 * surfaces Q11/Q12 may show, and the component renders them as messages only).
 *
 * Compiled artefact: src/compiled/inputs/components.js (tools/compile_n21_ts.py).
 */
(function (root) {
    'use strict';
    const API_VERSION = 'n22-components-1';
    const QUANTUM_DECIMALS = 12;
    const TYPE_IDS = [
        'Q01', 'Q02', 'Q03', 'Q04', 'Q05', 'Q06', 'Q07', 'Q08', 'Q09',
        'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'Q15', 'Q16', 'Q17', 'Q18'
    ];
    /* Mirrors SimBank.RENDERER_REGISTRY (N04); the contract must agree. */
    const RENDERER_KEYS = {
        Q01: 'renderer-numeric',
        Q02: 'renderer-numeric-multistep',
        Q03: 'renderer-method-formula',
        Q04: 'renderer-method-coefficients',
        Q05: 'renderer-method-half-reaction',
        Q06: 'renderer-matching',
        Q07: 'renderer-option-classification',
        Q08: 'renderer-ordering',
        Q09: 'renderer-numeric-table',
        Q10: 'renderer-numeric-scale',
        Q11: 'renderer-graph-construct',
        Q12: 'renderer-graph-interpret',
        Q13: 'renderer-method-error-repair',
        Q14: 'renderer-option-statement',
        Q15: 'renderer-method-explanation',
        Q16: 'renderer-method-compare',
        Q17: 'renderer-method-case',
        Q18: 'renderer-option-multiselect'
    };
    /* Registry `control` vocabulary → the component's control and ARIA role. */
    const CONTROLS = {
        'text-input': { control: 'textbox', role: 'textbox' },
        'text-input-map': { control: 'textbox', role: 'textbox' },
        'text-input-vector': { control: 'coefficient', role: 'textbox' },
        'select': { control: 'select', role: 'combobox' },
        'checkbox-group': { control: 'checkbox', role: 'checkbox' },
        'radio-group': { control: 'radio', role: 'radio' },
        'textarea': { control: 'textarea', role: 'textbox', multiline: true },
        'coordinate-table': { control: 'coordinate_table', role: 'group' },
        'graph-canvas-keyboard': { control: 'graph_canvas', role: 'group' },
        'select-and-place': { control: 'placement', role: 'group' }
    };
    /* ------------------------------------------------------------- errors */
    class InputsError extends Error {
        constructor(code, message, details) {
            super(message);
            this.name = 'InputsError';
            this.code = code;
            this.details = details || {};
            if (Error.captureStackTrace) {
                Error.captureStackTrace(this, InputsError);
            }
        }
    }
    function fail(code, message, details) {
        throw new InputsError(code, message, details);
    }
    function hasOwn(object, key) {
        return object !== null && object !== undefined
            && Object.prototype.hasOwnProperty.call(object, key);
    }
    function isPlainObject(value) {
        return value !== null && typeof value === 'object' && !Array.isArray(value);
    }
    function clone(value) {
        if (value === null || value === undefined) {
            return value;
        }
        return JSON.parse(JSON.stringify(value));
    }
    function round12(value) {
        const number = Number(value);
        if (!isFinite(number)) {
            return NaN;
        }
        if (number === 0) {
            return 0;
        }
        return Number(number.toFixed(QUANTUM_DECIMALS));
    }
    /* ------------------------------------------------------ term island */
    function termsIndex(terms) {
        const index = Object.create(null);
        function addEntry(entry) {
            if (!isPlainObject(entry)) {
                return;
            }
            const key = entry.key || entry.term_key || entry.id;
            const text = entry.text_lv !== undefined ? entry.text_lv : entry.text;
            if (typeof key === 'string' && typeof text === 'string') {
                index[key] = text;
            }
        }
        if (isPlainObject(terms) && Array.isArray(terms.terms)) {
            terms.terms.forEach(addEntry);
        }
        else if (Array.isArray(terms)) {
            terms.forEach(addEntry);
        }
        else if (isPlainObject(terms)) {
            Object.keys(terms).forEach((key) => {
                if (typeof terms[key] === 'string') {
                    index[key] = terms[key];
                }
            });
        }
        return index;
    }
    function substitute(pattern, slots, details) {
        let missing = null;
        const out = String(pattern).replace(/\{([a-z0-9_]+)\}/gi, (whole, name) => {
            if (slots && hasOwn(slots, name) && slots[name] !== null && slots[name] !== undefined) {
                return String(slots[name]);
            }
            if (missing === null) {
                missing = name;
            }
            return whole;
        });
        if (missing !== null) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'ARIA šablons "' + String(pattern) + '" prasa aizvietotāju {' + String(missing)
                + '}, bet komponente to nenodrošina.', Object.assign({}, details, { slot: missing }));
        }
        return out;
    }
    function resolveTerm(index, key, slots, details) {
        if (typeof key !== 'string' || key === '') {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Laukam nav deklarētas terminu atslēgas (label_key).', details);
        }
        if (!hasOwn(index, key)) {
            fail('E_INPUTS_TERM_MISSING', 'Terminu salā nav atslēgas "' + key + '".', Object.assign({}, details, { term_key: key }));
        }
        return substitute(index[key], slots, details);
    }
    /* ------------------------------------------------------------ paths */
    function readPath(object, path) {
        if (typeof path !== 'string' || path === '') {
            return object;
        }
        let current = object;
        const segments = path.split('.');
        for (let i = 0; i < segments.length; i += 1) {
            if (current === null || current === undefined) {
                return undefined;
            }
            const match = /^([A-Za-z0-9_]+)((?:\[\d+\])*)$/.exec(segments[i]);
            if (!match) {
                return undefined;
            }
            current = current[match[1]];
            const indexes = match[2] ? match[2].match(/\[\d+\]/g) : null;
            if (indexes) {
                for (let j = 0; j < indexes.length; j += 1) {
                    if (current === null || current === undefined) {
                        return undefined;
                    }
                    current = current[Number(indexes[j].slice(1, -1))];
                }
            }
        }
        return current;
    }
    function instancePath(source) {
        if (typeof source !== 'string') {
            return null;
        }
        if (source === 'none' || source === 'static' || source === 'sim-figures') {
            return null;
        }
        return source.indexOf('instance.') === 0 ? source.slice(9) : source;
    }
    function arrayAt(instance, source) {
        const relative = instancePath(source);
        if (relative === null) {
            return null;
        }
        const value = readPath(instance, relative);
        return Array.isArray(value) ? value : null;
    }
    /* -------------------------------------------------------------- plan
     *
     * `planLeaves` is the renderer's knowledge: one leaf per answer-bearing
     * control, carrying the *role* the registry template names, the `{slot}`
     * values its label pattern needs, the authored visible label, and where a
     * commit writes.
     */
    function leaf(fieldId, role, slots, visibleLabel, writes, extra) {
        const out = {
            field_id: fieldId,
            role: role,
            slots: slots || {},
            visible_label: visibleLabel === undefined ? null : visibleLabel,
            writes: writes
        };
        return Object.assign(out, extra || {});
    }
    function inputFields(instance) {
        const fields = readPath(instance, 'payload.input_fields');
        if (!Array.isArray(fields) || !fields.length) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Instancei trūkst payload.input_fields.', {
                type_id: instance && instance.type_id, field_id: 'value'
            });
        }
        return fields;
    }
    /* The registry declares which instance path a step list lives on
     * (completion_rule.steps_from); Q02 keeps its steps in payload.substeps. */
    function stepsFrom(contract, fallback) {
        const rule = isPlainObject(contract) && isPlainObject(contract.completion_rule)
            ? contract.completion_rule : {};
        const declared = typeof rule.steps_from === 'string' ? rule.steps_from : fallback;
        return String(declared).replace(/^instance\./, '');
    }
    function stepsOf(instance, contract, role) {
        const steps = readPath(instance, stepsFrom(contract, 'payload.steps'));
        if (!Array.isArray(steps) || !steps.length) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Instancei trūkst soļu saraksta (' + stepsFrom(contract, 'payload.steps') + ').', {
                type_id: instance && instance.type_id, field_id: role
            });
        }
        return steps;
    }
    function speciesOf(instance, role) {
        const species = readPath(instance, 'payload.species_list');
        if (!Array.isArray(species) || !species.length) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Instancei trūkst payload.species_list.', {
                type_id: instance && instance.type_id, field_id: role
            });
        }
        return species;
    }
    const PLANS = {
        Q01: (_contract, instance) => {
            const out = [];
            inputFields(instance).forEach((field) => {
                out.push(leaf(String(field.field_id), 'value', { label: field.label_lv }, field.label_lv, { kind: 'value', key: String(field.field_id) }));
            });
            const unit = readPath(instance, 'payload.unit');
            out.push(leaf('unit', 'unit', { label: unit === undefined ? '' : unit }, unit === undefined ? null : String(unit), { kind: 'none' }, { unit_only: true }));
            return out;
        },
        Q09: (_contract, instance) => inputFields(instance).map((field) => leaf(String(field.field_id), 'value', { label: field.label_lv }, field.label_lv, { kind: 'value', key: String(field.field_id) })),
        Q10: (_contract, instance) => inputFields(instance).map((field) => leaf(String(field.field_id), 'value', { label: field.label_lv }, field.label_lv, { kind: 'value', key: String(field.field_id) })),
        Q02: (contract, instance) => {
            const out = inputFields(instance).map((field) => leaf(String(field.field_id), 'value', { label: field.label_lv }, field.label_lv, { kind: 'value', key: String(field.field_id) }));
            stepsOf(instance, contract, 'step').forEach((step) => {
                out.push(leaf(String(step.step_id), 'step', { step: step.prompt_lv }, step.prompt_lv, { kind: 'value', key: String(step.step_id) }, { step_id: step.step_id }));
            });
            return out;
        },
        Q03: (contract, instance) => {
            const out = [
                leaf('choice', 'choice', {}, null, { kind: 'value', key: 'template' })
            ];
            stepsOf(instance, contract, 'fill_in').forEach((step) => {
                out.push(leaf('fill_' + String(step.step_id), 'fill_in', { slot: step.prompt_lv }, step.prompt_lv, { kind: 'fill_in', step_id: String(step.step_id) }, { step_id: step.step_id }));
            });
            out.push(leaf('conserved', 'conserved', {}, null, { kind: 'value', key: 'conserved' }));
            return out;
        },
        Q04: (_contract, instance) => speciesOf(instance, 'coefficient')
            .map((name, index) => leaf('coef_' + String(index), 'coefficient', { species: String(name) }, String(name), { kind: 'vector', index: index })),
        Q05: (contract, instance) => stepsOf(instance, contract, 'row')
            .map((step) => leaf('row_' + String(step.step_id), 'row', { step: step.prompt_lv }, step.prompt_lv, { kind: 'row', step_id: String(step.step_id) }, { step_id: step.step_id })),
        Q06: (_contract, instance) => {
            const left = readPath(instance, 'payload.left_items');
            const right = readPath(instance, 'payload.right_items');
            if (!Array.isArray(left) || !Array.isArray(right) || !left.length || !right.length) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Q06 instancei trūkst left_items/right_items.', {
                    type_id: 'Q06', field_id: 'pair'
                });
            }
            return left.map((item) => leaf('pair_' + String(item.id), 'pair', { left: item.text_lv }, item.text_lv, { kind: 'pair', left_id: String(item.id) }, { options: right.map((option) => ({ value: String(option.id), text_lv: option.text_lv })) }));
        },
        Q07: (_contract, instance) => optionLeaves(instance, 'option'),
        Q08: (_contract, instance) => {
            const items = readPath(instance, 'payload.items');
            if (!Array.isArray(items) || !items.length) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Q08 instancei trūkst payload.items.', {
                    type_id: 'Q08', field_id: 'position'
                });
            }
            /* One slot per POSITION, each offering the items as options (the
             * "per position a select of items" variant): no drag handle and no
             * position-based key is needed. */
            const out = items.map((_item, index) => leaf('slot_' + String(index + 1), 'position', { position: String(index + 1) }, null, { kind: 'position_slot', position: index + 1 }, { item_count: items.length }));
            out.push(leaf('explanation', 'explanation', {}, null, { kind: 'value', key: 'explanation' }));
            return out;
        },
        Q11: (_contract, instance) => {
            const points = readPath(instance, 'payload.points');
            if (!Array.isArray(points) || !points.length) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Q11 instancei trūkst payload.points.', {
                    type_id: 'Q11', field_id: 'record'
                });
            }
            const out = [];
            points.forEach((_point, index) => {
                out.push(leaf('pt' + String(index) + '_x', 'record', {}, null, { kind: 'row', row_index: index, axis: 'x' }, { row_index: index, axis: 'x' }));
                out.push(leaf('pt' + String(index) + '_y', 'record', {}, null, { kind: 'row', row_index: index, axis: 'y' }, { row_index: index, axis: 'y' }));
            });
            out.push(leaf('draw_payload', 'draw_payload', {}, null, { kind: 'draw' }));
            return out;
        },
        Q12: (_contract, _instance) => [
            leaf('read_x', 'read_x', {}, null, { kind: 'value', key: 'read_x' }),
            leaf('read_y', 'read_y', {}, null, { kind: 'value', key: 'read_y' }),
            leaf('figure_binding', 'figure_binding', {}, null, { kind: 'value', key: 'figure_binding' })
        ],
        Q13: (_contract, instance) => {
            const out = speciesOf(instance, 'coefficient').map((name, index) => leaf('coef_' + String(index), 'coefficient', { species: String(name) }, String(name), { kind: 'vector', index: index }));
            out.push(leaf('located', 'located', {}, null, { kind: 'value', key: 'located' }));
            out.push(leaf('replacement', 'replacement', {}, null, { kind: 'value', key: 'replacement' }));
            out.push(leaf('reason', 'reason', {}, null, { kind: 'value', key: 'reason' }));
            return out;
        },
        Q14: (_contract, instance) => optionLeaves(instance, 'option')
            .concat([leaf('justification', 'justification', {}, null, { kind: 'value', key: 'justification' })]),
        Q18: (_contract, instance) => optionLeaves(instance, 'option')
            .concat([leaf('justification', 'justification', {}, null, { kind: 'value', key: 'justification' })]),
        Q15: (_contract, _instance) => [leaf('text', 'text', {}, null, { kind: 'value', key: 'text' })],
        Q16: (_contract, _instance) => [leaf('text', 'text', {}, null, { kind: 'value', key: 'text' })],
        Q17: (contract, instance) => {
            const out = stepsOf(instance, contract, 'pair').map((step) => leaf('pair_' + String(step.step_id), 'pair', { step: step.prompt_lv }, step.prompt_lv, { kind: 'pair_map', step_id: String(step.step_id) }, { step_id: step.step_id }));
            const parts = readPath(instance, 'payload.structure_parts');
            if (Array.isArray(parts)) {
                parts.forEach((part) => {
                    out.push(leaf('place_' + String(part.part_id), 'structure', { part: part.text_lv }, part.text_lv, { kind: 'placement', part_id: String(part.part_id) }));
                });
            }
            /* The palette and the placement target are the keyboard controls of the
             * structure part; they are interaction state, not answers. The target is
             * two coordinate cells, so the same key model as the Q11 table applies:
             * Left/Right move focus, Up/Down adjust the focused coordinate. */
            out.push(leaf('palette', 'structure_palette', {}, null, { kind: 'palette' }, { transient: true }));
            out.push(leaf('target_x', 'structure_target', {}, null, { kind: 'target', axis: 'x' }, { transient: true }));
            out.push(leaf('target_y', 'structure_target', {}, null, { kind: 'target', axis: 'y' }, { transient: true }));
            return out;
        }
    };
    function optionLeaves(instance, role) {
        const options = readPath(instance, 'payload.options');
        if (!Array.isArray(options) || !options.length) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Instancei trūkst payload.options.', {
                type_id: instance && instance.type_id, field_id: role
            });
        }
        return options.map((option) => leaf('opt_' + String(option.option_id), role, { option: option.text_lv }, option.text_lv, { kind: 'selected', option_id: String(option.option_id) }));
    }
    function planLeaves(typeId, contract, instance) {
        const builder = PLANS[typeId];
        if (typeof builder !== 'function') {
            fail('E_INPUTS_UNKNOWN_TYPE', 'N22 komponentei nav reģistrēta renderētāja tipam "' + String(typeId) + '".', { type_id: typeId });
        }
        return builder(contract, instance);
    }
    /* --------------------------------------------------- contract binding */
    function assertContractShape(typeId, contract) {
        if (!isPlainObject(contract)) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipam ' + typeId + ' nav līguma objekta.', {
                type_id: typeId
            });
        }
        if (contract.id !== undefined && contract.id !== typeId) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Līguma id "' + String(contract.id) + '" nesakrīt ar renderēto tipu ' + typeId + '.', { type_id: typeId, contract_type_id: contract.id });
        }
        if (contract.renderer_key !== RENDERER_KEYS[typeId]) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipa ' + typeId + ' renderer_key "' + String(contract.renderer_key)
                + '" nesakrīt ar bankas reģistru ("' + RENDERER_KEYS[typeId] + '").', { type_id: typeId, renderer_key: contract.renderer_key });
        }
        if (contract.fields !== undefined && !Array.isArray(contract.fields)) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipa ' + typeId + ' līguma fields nav masīvs.', {
                type_id: typeId, field_id: null
            });
        }
    }
    function templateRepeats(template) {
        const path = typeof template.payload_path === 'string' ? template.payload_path : '';
        if (/\[(index|step_id|field_id|part_id)\]/.test(path)) {
            return true;
        }
        return template.value_type === 'string_list';
    }
    function leavesFor(_contract, leaves, role) {
        return leaves.filter((entry) => entry.role === role);
    }
    /* Options for a scalar select/radio group. */
    function contractOptions(env, template) {
        const source = template.option_source !== undefined ? template.option_source : template.source;
        const out = [];
        if (source === 'sim-figures') {
            const figures = Array.isArray(env.context.figures) ? env.context.figures : null;
            if (figures === null) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Lauks "' + String(template.role) + '" prasa sim-figures opcijas, bet kontekstā nav attēlu saraksta.', {
                    type_id: env.typeId, field_id: String(template.role), option_source: 'sim-figures'
                });
            }
            figures.forEach((figure) => {
                if (!figure || typeof figure.id !== 'string') {
                    return;
                }
                out.push({ value: figure.id, text_lv: null, figure_id: figure.id,
                    title_key: typeof figure.title_key === 'string' ? figure.title_key : null });
            });
            return out;
        }
        const list = arrayAt(env.instance, source);
        if (list === null) {
            const scalar = readPath(env.instance, instancePath(source) || '');
            if (scalar === undefined || scalar === null) {
                return out;
            }
            out.push({ value: String(scalar), text_lv: String(scalar) });
            return out;
        }
        list.forEach((entry) => {
            if (!isPlainObject(entry)) {
                out.push({ value: String(entry), text_lv: String(entry) });
                return;
            }
            const value = entry.option_id !== undefined ? entry.option_id
                : (entry.id !== undefined ? entry.id
                    : (entry.item_id !== undefined ? entry.item_id
                        : (entry.part_id !== undefined ? entry.part_id
                            : (entry.step_id !== undefined ? entry.step_id : entry.template_id))));
            const text = entry.text_lv !== undefined ? entry.text_lv
                : (entry.label_lv !== undefined ? entry.label_lv : entry.prompt_lv);
            out.push({ value: value === undefined ? null : String(value),
                text_lv: text === undefined ? null : String(text) });
        });
        return out;
    }
    /* ------------------------------------------------------------ render */
    function makeEnv(typeId, contract, instance, payload, terms, context) {
        return {
            typeId: typeId,
            contract: contract,
            instance: instance,
            payload: isPlainObject(payload) ? payload : null,
            terms: terms,
            termIndex: termsIndex(terms),
            context: isPlainObject(context) ? context : {},
            prefix: 'inputs-' + typeId.toLowerCase() + '-'
        };
    }
    function rawFor(writes, payload) {
        if (!payload) {
            return undefined;
        }
        switch (writes.kind) {
            case 'value':
                if (writes.key === 'read_x' || writes.key === 'read_y') {
                    if (!payload.read) {
                        return undefined;
                    }
                    return writes.key === 'read_x' ? payload.read.x : payload.read.y;
                }
                if (writes.key === 'figure_binding') {
                    return payload.read ? payload.read.figure_binding : undefined;
                }
                if (writes.key === 'template') {
                    return payload.choice;
                }
                return payload.values && hasOwn(payload.values, writes.key)
                    ? payload.values[writes.key] : payload[writes.key];
            case 'fill_in':
                return payload.fill_ins && hasOwn(payload.fill_ins, writes.step_id)
                    ? payload.fill_ins[writes.step_id] : undefined;
            case 'row':
                return payload.rows && hasOwn(payload.rows, writes.step_id)
                    ? payload.rows[writes.step_id] : undefined;
            case 'pair_map':
                return payload.pair_map && hasOwn(payload.pair_map, writes.step_id)
                    ? payload.pair_map[writes.step_id] : undefined;
            case 'vector':
                return Array.isArray(payload.vector) ? payload.vector[writes.index] : undefined;
            case 'pair': {
                const pairs = Array.isArray(payload.pairs) ? payload.pairs : [];
                for (let i = 0; i < pairs.length; i += 1) {
                    if (pairs[i] && pairs[i].left_id === writes.left_id) {
                        return pairs[i].right_id;
                    }
                }
                return undefined;
            }
            case 'position_slot': {
                const order = Array.isArray(payload.order) ? payload.order : [];
                const at = Number(writes.position) - 1;
                return order[at] === undefined || order[at] === null ? undefined : order[at];
            }
            case 'selected':
                return Array.isArray(payload.selected) && payload.selected.indexOf(writes.option_id) !== -1
                    ? writes.option_id : undefined;
            case 'placement': {
                const structure = isPlainObject(payload.structure) ? payload.structure : null;
                const placement = structure && structure.placements
                    ? structure.placements.filter((entry) => entry.part_id === writes.part_id)[0] : null;
                return placement ? placement : undefined;
            }
            case 'row_coordinate': {
                const table = payload.record && Array.isArray(payload.record.points)
                    ? payload.record.points : [];
                const point = table[writes.row_index];
                return point ? point[writes.axis] : undefined;
            }
            default:
                return undefined;
        }
    }
    function leafRaw(leafEntry, payload) {
        if (!payload) {
            return undefined;
        }
        if (leafEntry.role === 'record') {
            return rawFor({ kind: 'row_coordinate', row_index: leafEntry.writes.row_index,
                axis: leafEntry.writes.axis }, payload);
        }
        if (leafEntry.role === 'draw_payload') {
            return payload.draw_payload === undefined ? undefined : payload.draw_payload;
        }
        if (leafEntry.role === 'structure_palette' || leafEntry.role === 'structure_target') {
            return undefined;
        }
        if (leafEntry.role === 'unit') {
            return undefined;
        }
        return rawFor(leafEntry.writes, payload);
    }
    /* The registry publishes the announcement keys; resolve through it when it
     * is loaded so a component never invents an announcement phrase. */
    function announcementText(env, name) {
        const registry = root.SimInputsRegistry;
        if (registry && typeof registry.announcementKey === 'function') {
            try {
                const key = registry.announcementKey(name);
                if (typeof key === 'string' && key) {
                    return resolveTerm(env.termIndex, key, {}, { type_id: env.typeId, field_id: null });
                }
            }
            catch (ignored) {
                /* fall through to the term bank's own state keys */
            }
        }
        const fallbackKey = name === 'complete' ? 'input.state.complete'
            : (name === 'invalid' ? 'input.state.invalid' : 'input.state.incomplete');
        return resolveTerm(env.termIndex, fallbackKey, {}, { type_id: env.typeId, field_id: null });
    }
    function errorRecord(contract, env, fieldId, errorId) {
        if (!errorId) {
            return null;
        }
        const surfaces = Array.isArray(contract.error_surfaces) ? contract.error_surfaces : [];
        if (surfaces.length && surfaces.indexOf(String(errorId)) === -1) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Kļūdas klase "' + String(errorId) + '" nav deklarēta lauka "' + fieldId
                + '" tipa error_surfaces sarakstā.', {
                type_id: env.typeId, field_id: fieldId, error_id: String(errorId)
            });
        }
        const registry = root.SimInputsRegistry;
        if (registry && typeof registry.errorMessage === 'function' && env.terms !== undefined) {
            try {
                const message = registry.errorMessage(String(errorId), env.terms);
                if (typeof message === 'string' && message) {
                    return { id: String(errorId), message: message, source: 'SimInputsRegistry.errorMessage' };
                }
            }
            catch (ignored) {
                /* Fall through to the contract's own feedback_keys mapping: the
                 * registry refused (for example it was never loaded), and the record
                 * of which path ran is the caller's evidence. */
            }
        }
        const feedbackKeys = isPlainObject(contract.feedback_keys) ? contract.feedback_keys : {};
        const key = feedbackKeys[String(errorId)];
        if (typeof key !== 'string' || !key) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Līgumam nav feedback_keys ieraksta kļūdas klasei "' + String(errorId) + '".', {
                type_id: env.typeId, field_id: fieldId, error_id: String(errorId)
            });
        }
        return {
            id: String(errorId),
            message: resolveTerm(env.termIndex, key, {}, { type_id: env.typeId, field_id: fieldId })
        };
    }
    function storesFor(template, leafEntry, position) {
        let path = typeof template.payload_path === 'string' ? template.payload_path : '';
        if (!path) {
            return '';
        }
        path = path.replace(/\[index\]/g, '[' + String(position) + ']');
        path = path.replace(/\[field_id\]/g, '[' + String(leafEntry.field_id) + ']');
        path = path.replace(/\[step_id\]/g, '[' + String(leafEntry.step_id === undefined
            ? leafEntry.field_id : leafEntry.step_id) + ']');
        path = path.replace(/\[part_id\]/g, '[' + String(leafEntry.writes && leafEntry.writes.part_id
            ? leafEntry.writes.part_id : '') + ']');
        return path;
    }
    function describeLeaf(env, template, leafEntry, position) {
        const mapped = CONTROLS[template.control] || { control: 'textbox', role: 'textbox' };
        const details = { type_id: env.typeId, field_id: leafEntry.field_id };
        const ariaName = resolveTerm(env.termIndex, template.label_key, leafEntry.slots, details);
        const raw = leafRaw(leafEntry, env.payload);
        const rawText = raw === undefined || raw === null
            ? null : (typeof raw === 'object' ? null : String(raw));
        const errorId = env.context.errors && hasOwn(env.context.errors, leafEntry.field_id)
            ? env.context.errors[leafEntry.field_id] : null;
        const error = errorRecord(env.contract, env, leafEntry.field_id, errorId);
        let state;
        if (error) {
            state = 'error';
        }
        else if (rawText === null || rawText === '') {
            state = 'empty';
        }
        else if (env.typeId === 'Q15' || env.typeId === 'Q16' || env.typeId === 'Q03') {
            state = 'pending';
        }
        else {
            state = 'filled';
        }
        const field = {
            field_id: leafEntry.field_id,
            role: mapped.role,
            control: mapped.control,
            visible_label: leafEntry.visible_label,
            aria_name: ariaName,
            required: template.required === false ? false : true,
            stores: storesFor(template, leafEntry, position),
            error: error,
            state: state,
            state_text: stateTextFor(env, template, leafEntry, mapped.control, state, rawText, error, null),
            value: rawText,
            multiline: Boolean(mapped.multiline),
            min_length: null,
            describedby: error ? env.prefix + 'error-' + leafEntry.field_id : null,
            transient: Boolean(leafEntry.transient),
            options: null,
            checked: null,
            rows: null
        };
        if (mapped.control === 'select' || mapped.control === 'radio') {
            const options = contractOptions(env, template);
            if (!options.length) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Lauka "' + leafEntry.field_id + '" opciju avots "' + String(template.option_source
                    || template.source) + '" ir tukšs, tāpēc izvēles lauks netiek renderēts tukšs.', {
                    type_id: env.typeId, field_id: leafEntry.field_id,
                    option_source: template.option_source || template.source
                });
            }
            field.options = options.map((option) => {
                let text = option.text_lv;
                if ((text === null || text === undefined) && typeof option.title_key === 'string') {
                    text = resolveTerm(env.termIndex, option.title_key, {}, {
                        type_id: env.typeId, field_id: leafEntry.field_id
                    });
                }
                return {
                    value: option.value,
                    text_lv: text === undefined ? null : text,
                    selected: rawText !== null && String(option.value) === rawText
                };
            });
        }
        if (field.options) {
            field.state_text = stateTextFor(env, template, leafEntry, mapped.control, state, rawText, error, field.options);
        }
        if (mapped.control === 'checkbox') {
            field.checked = rawText !== null && rawText !== '';
            field.options = [{
                    value: String(leafEntry.writes.option_id),
                    text_lv: leafEntry.visible_label,
                    selected: field.checked
                }];
        }
        if (mapped.control === 'placement') {
            field.placement = raw === null || raw === undefined ? null : {
                part_id: raw.part_id,
                x: raw.x,
                y: raw.y,
                text_lv: resolveTerm(env.termIndex, 'input.q17.structure_part', { part: leafEntry.visible_label === null ? '' : leafEntry.visible_label }, details)
            };
        }
        return field;
    }
    /* The shipped term bank has response-level state phrases (complete,
     * incomplete, invalid, pending_grading) and *per-field missing* messages,
     * but no per-field "filled" phrase. So a field's text equivalence is: the
     * completion rule's missing message when empty, the Latvian error message
     * when in error, the pending phrase while a self-assessed answer waits, and
     * the stored text itself once filled. Nothing is invented and no state is
     * communicated by colour alone. */
    const ROLE_MISSING_KEY = {
        value: 'value', step: 'step', coefficient: 'coefficient', row: 'row',
        pair: 'pair', option: 'selection', position: 'order_item',
        choice: 'template', fill_in: 'fill_in', conserved: 'conserved',
        explanation: 'explanation', justification: 'justification', text: 'text',
        read_x: 'axis', read_y: 'axis', figure_binding: 'binding',
        record: 'record', draw_payload: 'point_count', structure: 'structure_part'
    };
    function missingMessageKey(contract, role) {
        const rule = isPlainObject(contract) && isPlainObject(contract.completion_rule)
            ? contract.completion_rule : {};
        const table = isPlainObject(rule.missing) ? rule.missing : {};
        const name = ROLE_MISSING_KEY[role];
        if (!name) {
            return null;
        }
        if (typeof table[name] === 'string') {
            return table[name];
        }
        if (role === 'pair' && typeof table.step === 'string') {
            return table.step;
        }
        return null;
    }
    function stateTexts(env) {
        return {
            empty: resolveTerm(env.termIndex, 'input.state.incomplete', {}, { type_id: env.typeId, field_id: null }),
            error: resolveTerm(env.termIndex, 'input.state.invalid', {}, { type_id: env.typeId, field_id: null }),
            pending: resolveTerm(env.termIndex, 'input.state.pending_grading', {}, { type_id: env.typeId, field_id: null })
        };
    }
    function stateTextFor(env, _template, leafEntry, control, state, rawText, error, options) {
        if (state === 'error' && error) {
            return error.message;
        }
        if (state === 'pending') {
            return stateTexts(env).pending;
        }
        if (state === 'filled') {
            if (control === 'checkbox') {
                return leafEntry.visible_label === null ? String(rawText) : String(leafEntry.visible_label);
            }
            if (Array.isArray(options) && options.length) {
                const chosen = options.filter((option) => String(option.value) === String(rawText))[0];
                if (chosen && chosen.text_lv) {
                    return String(chosen.text_lv);
                }
            }
            return rawText === null ? '' : String(rawText);
        }
        const key = missingMessageKey(env.contract, leafEntry.role);
        if (key) {
            const slots = Object.assign({}, leafEntry.slots);
            if (key === 'input.missing.read_axis' && slots.axis === undefined) {
                slots.axis = leafEntry.role === 'read_x' ? 'x' : 'y';
            }
            try {
                return resolveTerm(env.termIndex, key, slots, {
                    type_id: env.typeId, field_id: leafEntry.field_id
                });
            }
            catch (ignored) {
                return stateTexts(env).empty;
            }
        }
        return stateTexts(env).empty;
    }
    function describeCoordinateTable(env, template, leaves) {
        const details = { type_id: env.typeId, field_id: 'record' };
        const ariaName = resolveTerm(env.termIndex, template.label_key, {}, details);
        const pointCount = leaves.length / 2;
        const rows = [];
        for (let i = 0; i < pointCount; i += 1) {
            const xLeaf = leaves[i * 2];
            const yLeaf = leaves[i * 2 + 1];
            rows.push({
                row_index: i,
                cells: [
                    { axis: 'x', field_id: xLeaf.field_id, stores: storesFor(template, xLeaf, i),
                        value: leafRaw(xLeaf, env.payload) === undefined ? null
                            : String(leafRaw(xLeaf, env.payload)), state: leafRaw(xLeaf, env.payload) ? 'filled' : 'empty' },
                    { axis: 'y', field_id: yLeaf.field_id, stores: storesFor(template, yLeaf, i),
                        value: leafRaw(yLeaf, env.payload) === undefined ? null
                            : String(leafRaw(yLeaf, env.payload)), state: leafRaw(yLeaf, env.payload) ? 'filled' : 'empty' }
                ]
            });
        }
        return {
            field_id: 'record',
            role: 'group',
            control: 'coordinate_table',
            visible_label: null,
            aria_name: ariaName,
            required: template.required === false ? false : true,
            stores: storesFor(template, leaves[0], 0).replace(/\.x$|\.y$/, '') || 'record',
            error: null,
            state: rows.every((row) => row.cells.every((cell) => cell.state === 'filled'))
                ? 'filled' : 'empty',
            state_text: rows.every((row) => row.cells.every((cell) => cell.state === 'filled'))
                ? String(rows.length) + ' / ' + String(rows.length)
                : resolveTerm(env.termIndex, missingMessageKey(env.contract, 'record') || 'input.state.incomplete', {}, { type_id: env.typeId, field_id: 'record' }),
            value: null,
            multiline: false,
            min_length: null,
            describedby: env.prefix + 'table-help',
            transient: false,
            options: null,
            checked: null,
            rows: rows
        };
    }
    function render(typeId, contract, instance, payload, terms, context) {
        assertContractShape(typeId, contract);
        if (!isPlainObject(instance)) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipam ' + typeId + ' nav instances.', { type_id: typeId });
        }
        const env = makeEnv(typeId, contract, instance, payload, terms, context);
        const leaves = planLeaves(typeId, contract, instance);
        if (!Array.isArray(contract.fields) || !contract.fields.length) {
            const first = leaves.filter((entry) => !entry.transient)[0] || leaves[0] || null;
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Reģistra līgumā tipam ' + typeId + ' nav neviena lauka, tāpēc vadīklu "'
                + String(first ? first.field_id : '') + '" nevar novietot.', {
                type_id: typeId, field_id: first ? first.field_id : null, role: first ? first.role : null
            });
        }
        const fields = [];
        const usedRoles = Object.create(null);
        contract.fields.forEach((template) => {
            const role = template.role;
            if (typeof role !== 'string' || !role) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipa ' + typeId + ' līguma laukam nav role lauka.', { type_id: typeId, field_id: null });
            }
            if (usedRoles[role]) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipa ' + typeId + ' līgums deklarē role "' + role + '" divreiz.', {
                    type_id: typeId, field_id: role
                });
            }
            usedRoles[role] = true;
            const roleLeaves = leavesFor(contract, leaves, role);
            const optional = template.required === false;
            const mapped = CONTROLS[template.control] || { control: 'textbox', role: 'textbox' };
            if (!roleLeaves.length) {
                if (optional) {
                    return;
                }
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Reģistra līgums deklarē lauku "' + role + '" (control ' + String(template.control)
                    + '), bet instance tam nedod nevienu elementu (source "'
                    + String(template.source) + '").', {
                    type_id: typeId, field_id: role, source: template.source
                });
            }
            if (mapped.control === 'coordinate_table') {
                fields.push(describeCoordinateTable(env, template, roleLeaves));
                return;
            }
            const repeats = templateRepeats(template);
            if (!repeats && roleLeaves.length > 1) {
                /* Non-repeating template with several leaves means the renderer and
                 * the registry disagree about the widget's granularity. */
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Lauks "' + role + '" ir vienlaidus līgumā, bet renderētājs tam plāno '
                    + roleLeaves.length + ' vadīklas.', { type_id: typeId, field_id: role });
            }
            roleLeaves.forEach((leafEntry, position) => {
                fields.push(describeLeaf(env, template, leafEntry, position));
            });
        });
        /* A planned control the contract never names is a contract gap. */
        leaves.forEach((leafEntry) => {
            if (leafEntry.transient) {
                return;
            }
            if (!usedRoles[leafEntry.role]) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Reģistra līgumā trūkst lauka "' + leafEntry.role + '" (vadīkla "'
                    + leafEntry.field_id + '"), ko renderētājs prasa tipam ' + typeId + '.', {
                    type_id: typeId, field_id: leafEntry.field_id, role: leafEntry.role
                });
            }
        });
        const errors = fields.filter((field) => field.error !== null);
        const errorText = errors.length
            ? errors.map((field) => resolveTerm(env.termIndex, 'input.error.prefix', {
                message: field.error.message
            }, { type_id: typeId, field_id: field.field_id })).join(' ')
            : '';
        const completion = completionOf(contract, payload, instance);
        const stateText = announcementText(env, completion.status === 'complete' ? 'complete'
            : (completion.status === 'invalid' ? 'invalid' : 'incomplete'));
        const keyboard = isPlainObject(contract.keyboard) ? contract.keyboard : {};
        const hintKey = typeof keyboard.path_key === 'string' ? keyboard.path_key : null;
        const parityKey = typeof keyboard.parity_key === 'string' ? keyboard.parity_key : null;
        const abortKey = typeof keyboard.abort_rule_key === 'string' ? keyboard.abort_rule_key : null;
        const keyboardHint = hintKey
            ? resolveTerm(env.termIndex, hintKey, {}, { type_id: typeId, field_id: null }) : '';
        const parityNote = parityKey
            ? resolveTerm(env.termIndex, parityKey, {}, { type_id: typeId, field_id: null }) : '';
        const abortNote = abortKey
            ? resolveTerm(env.termIndex, abortKey, {}, { type_id: typeId, field_id: null }) : '';
        const nameKey = typeof contract.name_key === 'string' ? contract.name_key : null;
        const nameText = nameKey
            ? resolveTerm(env.termIndex, nameKey, {}, { type_id: typeId, field_id: null }) : '';
        const groupText = resolveTerm(env.termIndex, 'input.group.label', { type: nameText }, { type_id: typeId, field_id: null });
        const alternative = isPlainObject(contract.accessible_alternative)
            ? contract.accessible_alternative : {};
        const altLabel = typeof alternative.label_key === 'string'
            ? resolveTerm(env.termIndex, alternative.label_key, {}, { type_id: typeId, field_id: null })
            : '';
        const altDetails = Array.isArray(alternative.term_keys)
            ? alternative.term_keys.map((key) => ({
                key: key, text_lv: resolveTerm(env.termIndex, key, {}, { type_id: typeId, field_id: null })
            })) : [];
        const live = [
            { id: env.prefix + 'live-state', politeness: 'polite', text: stateText },
            { id: env.prefix + 'live-error', politeness: 'polite', text: errorText }
        ];
        if (typeId === 'Q17') {
            const statics = staticsFor(env);
            const targetText = statics.filter((entry) => entry.id === env.prefix + 'target-text')[0];
            live.push({
                id: env.prefix + 'live-target', politeness: 'polite',
                text: targetText ? targetText.text_lv : ''
            });
        }
        return {
            api_version: API_VERSION,
            type_id: typeId,
            renderer_key: contract.renderer_key,
            payload_kind: contract.payload_kind,
            payload_variant: contract.payload_variant === undefined ? null : contract.payload_variant,
            role: 'group',
            labelledby: env.prefix + 'label',
            describedby: env.prefix + 'hint',
            label_text_lv: groupText,
            name_text_lv: nameText,
            help_text_lv: keyboardHint,
            parity_note_lv: parityNote,
            abort_note_lv: abortNote,
            accessible_alternative: {
                label_key: alternative.label_key === undefined ? null : alternative.label_key,
                label_text_lv: altLabel,
                details: altDetails
            },
            fields: fields,
            surfaces: surfacesFor(env),
            parts: [],
            static: staticsFor(env),
            live: live,
            keyboard_hint: keyboardHint,
            completion: completion,
            error_count: errors.length
        };
    }
    function surfacesFor(env) {
        const out = [];
        if (env.typeId === 'Q11') {
            const graph = isPlainObject(env.contract.graph) ? env.contract.graph : {};
            const xAxis = readPath(env.instance, 'payload.x_axis') || {};
            const yAxis = readPath(env.instance, 'payload.y_axis') || {};
            out.push({
                surface_id: 'plot',
                control: 'plot',
                role: 'group',
                aria_name: resolveTerm(env.termIndex, 'input.q11.draw_surface', {}, { type_id: env.typeId, field_id: 'plot' }),
                describedby: env.prefix + 'hint',
                capture_context_id: graph.capture_context_id
                    || (env.context.capture_context_id === undefined ? null : env.context.capture_context_id),
                figure_id: graph.figure_id
                    || (env.context.figure_id === undefined ? null : env.context.figure_id),
                keyboard_path: 'table',
                axes_text_lv: axisLabel(env, xAxis) + ' / ' + axisLabel(env, yAxis)
            });
        }
        const structureParts = readPath(env.instance, 'payload.structure_parts');
        if (env.typeId === 'Q17' && Array.isArray(structureParts) && structureParts.length) {
            out.push({
                surface_id: 'palette',
                control: 'palette',
                role: 'listbox',
                aria_name: resolveTerm(env.termIndex, 'input.q17.structure_part', { part: String(structureParts.length) }, { type_id: env.typeId, field_id: 'palette' }),
                describedby: env.prefix + 'hint',
                keyboard_path: 'select_and_place',
                options: structureParts.map((part) => ({
                    value: String(part.part_id), text_lv: part.text_lv
                }))
            });
        }
        return out;
    }
    function axisLabel(_env, axis) {
        const label = axis && axis.label_lv !== undefined ? String(axis.label_lv) : '';
        const unit = axis && axis.unit !== undefined ? String(axis.unit) : '';
        return unit === '' ? label : label + ' (' + unit + ')';
    }
    function staticsFor(env) {
        const out = [];
        if (env.typeId === 'Q05') {
            const medium = readPath(env.instance, 'payload.medium');
            if (medium !== undefined) {
                out.push({ id: env.prefix + 'medium', text_lv: 'Reakcijas vide: ' + String(medium) });
            }
        }
        if (env.typeId === 'Q11') {
            const xAxis = readPath(env.instance, 'payload.x_axis') || {};
            const yAxis = readPath(env.instance, 'payload.y_axis') || {};
            out.push({ id: env.prefix + 'axis-x', text_lv: axisLabel(env, xAxis) });
            out.push({ id: env.prefix + 'axis-y', text_lv: axisLabel(env, yAxis) });
        }
        if (env.typeId === 'Q17') {
            const structure = isPlainObject(env.contract.structure) ? env.contract.structure : {};
            const fallback = isPlainObject(structure.target_start) ? structure.target_start : { x: 0, y: 0 };
            const target = env.payload && env.payload.structure && env.payload.structure.target
                ? env.payload.structure.target : fallback;
            out.push({
                id: env.prefix + 'target-text',
                text_lv: resolveTerm(env.termIndex, 'input.q17.structure_part', { part: 'x = ' + String(target.x) + ', y = ' + String(target.y) }, { type_id: env.typeId, field_id: 'target' })
            });
        }
        return out;
    }
    /* ------------------------------------------------- keyboard contracts */
    function keyboardContracts(typeId, contract, terms) {
        const index = terms === undefined || terms === null ? null : termsIndex(terms);
        function decorate(entry, typeKey) {
            const out = clone(Object.assign({ type_id: typeKey }, entry));
            if (contract && isPlainObject(contract.keyboard) && index) {
                out.path_key = contract.keyboard.path_key || null;
                out.parity_key = contract.keyboard.parity_key || null;
                out.abort_rule_key = contract.keyboard.abort_rule_key || null;
                out.path_text_lv = out.path_key ? resolveTerm(index, out.path_key, {}, {
                    type_id: typeKey, field_id: null
                }) : '';
                out.parity_text_lv = out.parity_key ? resolveTerm(index, out.parity_key, {}, {
                    type_id: typeKey, field_id: null
                }) : '';
                out.abort_text_lv = out.abort_rule_key ? resolveTerm(index, out.abort_rule_key, {}, {
                    type_id: typeKey, field_id: null
                }) : '';
            }
            return out;
        }
        if (typeof typeId === 'string') {
            const entry = KEYBOARD[typeId];
            if (!entry) {
                fail('E_INPUTS_UNKNOWN_TYPE', 'Nav tastatūras līguma tipam "' + typeId + '".', {
                    type_id: typeId
                });
            }
            return decorate(entry, typeId);
        }
        const out = {};
        TYPE_IDS.forEach((id) => { out[id] = decorate(KEYBOARD[id] || {}, id); });
        return out;
    }
    const KEYBOARD = {
        Q01: keyboardText(),
        Q02: keyboardText(),
        Q09: keyboardText(),
        Q10: keyboardText(),
        Q03: keyboardSelect(),
        Q04: keyboardText(),
        Q05: keyboardText(),
        Q06: {
            interaction: 'select',
            focus_order: 'labās puses pāri autorētajā secībā (left_items kārtība)',
            keys: selectKeys('izvēlēto labās puses vērtību fokusētajam kreisajam elementam', 'fokuss uz nākamo/iepriekšējo kreiso elementu'),
            pointer_equivalent_lv: 'noklikšķināt uz nolaižamā saraksta un izvēlēties vērtību',
            abort_lv: 'Escape atceļ neatstiprināto izvēli; pāreja prom atmet nepabeigto izvēli.',
            select_based: true
        },
        Q07: keyboardCheckboxGroup(),
        Q14: keyboardCheckboxGroup(),
        Q18: keyboardCheckboxGroup(),
        Q08: {
            interaction: 'select',
            focus_order: 'sakārtojamie vienumi autorētajā secībā, tad pamatojuma lauks',
            keys: selectKeys('izvēlēto vietu secībā fokusētajam vienumam', 'fokuss uz nākamo/iepriekšējo lauku'),
            pointer_equivalent_lv: 'noklikšķināt uz vietas nolaižamā saraksta un izvēlēties pozīciju',
            abort_lv: 'Escape atceļ neatstiprināto vietas izvēli; vilkšana nav pieejama vispār.',
            select_based: true,
            drag_forbidden: true
        },
        Q11: {
            interaction: 'table',
            focus_order: 'koordinātu tabulas šūnas punktu kārtībā (x, y)',
            keys: [
                { key: 'ArrowLeft', effect_lv: 'fokuss uz iepriekšējo koordinātu šūnu' },
                { key: 'ArrowRight', effect_lv: 'fokuss uz nākamo koordinātu šūnu' },
                { key: 'ArrowUp', effect_lv: 'palielina fokusēto koordinātu par deklarēto rupjo soli (Shift — smalkais solis)' },
                { key: 'ArrowDown', effect_lv: 'samazina fokusēto koordinātu par deklarēto soli' },
                { key: 'Enter', effect_lv: 'apstiprina rindu un novieto punktu caur to pašu uztveršanas ceļu kā norāde' },
                { key: 'Escape', effect_lv: 'atmet nepabeigto rindu' },
                { key: 'Tab', effect_lv: 'netiek pārtverts; fokuss atstāj komponenti' }
            ],
            pointer_equivalent_lv: 'vilkt līniju uz attēla; abi ceļi rada vienu sim-graph-draw-v1 ķermeni',
            abort_lv: 'Pāreja prom zīmēšanas laikā atmet ceļu: neviens daļējs punktu saraksts netiek izsniegts.',
            capture_component: 'SimGraphCapture',
            table_path: true
        },
        Q12: {
            interaction: 'table',
            focus_order: 'x vērtība, y vērtība, grafa piesaiste',
            keys: [
                { key: 'ArrowLeft', effect_lv: 'fokuss uz iepriekšējo lauku' },
                { key: 'ArrowRight', effect_lv: 'fokuss uz nākamo lauku' },
                { key: 'ArrowUp', effect_lv: 'palielina fokusēto nolasījumu par deklarēto soli' },
                { key: 'ArrowDown', effect_lv: 'samazina fokusēto nolasījumu par deklarēto soli' },
                { key: 'Enter', effect_lv: 'apstiprina lauku' },
                { key: 'Escape', effect_lv: 'atmet neapstiprināto labojumu' },
                { key: 'Tab', effect_lv: 'netiek pārtverts' }
            ],
            pointer_equivalent_lv: 'noklikšķināt uz attēla vienu reizi; koordinātas nolasītas ar to pašu kvantu',
            abort_lv: 'Pāreja prom pirms apstiprināšanas atmet atzīmi.',
            table_path: true
        },
        Q13: keyboardSelect(),
        Q15: keyboardText(),
        Q16: keyboardText(),
        Q17: {
            interaction: 'palette',
            focus_order: 'palete, novietošanas mērķis, soļu atbildes',
            keys: [
                { key: 'ArrowUp', effect_lv: 'paletē — iepriekšējais elements; mērķī — augšup' },
                { key: 'ArrowDown', effect_lv: 'paletē — nākamais elements; mērķī — lejup' },
                { key: 'ArrowLeft', effect_lv: 'mērķī — pa kreisi; citur — fokuss uz iepriekšējo lauku' },
                { key: 'ArrowRight', effect_lv: 'mērķī — pa labi; citur — fokuss uz nākamo lauku' },
                { key: 'Enter', effect_lv: 'paletē — izvēlas elementu; mērķī — novieto izvēlēto elementu' },
                { key: 'Escape', effect_lv: 'atmet nepabeigto novietošanu (neviens daļējs novietojums netiek izsniegts)' },
                { key: 'Tab', effect_lv: 'netiek pārtverts' }
            ],
            pointer_equivalent_lv: 'noklikšķināt uz paletes elementa un pēc tam uz mērķa vietas',
            abort_lv: 'Pāreja prom novietošanas laikā atmet mērķi un izvēli; placements paliek nemainīts.',
            palette_and_place: true
        }
    };
    function keyboardText() {
        return {
            interaction: 'text',
            focus_order: 'lauki autorētajā secībā',
            keys: [
                { key: 'ArrowLeft', effect_lv: 'fokuss uz iepriekšējo lauku' },
                { key: 'ArrowRight', effect_lv: 'fokuss uz nākamo lauku' },
                { key: 'Enter', effect_lv: 'apstiprina lauku (teksts tiek glabāts jau rakstīšanas laikā)' },
                { key: 'Tab', effect_lv: 'netiek pārtverts' }
            ],
            pointer_equivalent_lv: 'noklikšķināt laukā un rakstīt',
            abort_lv: 'Ierakstītais teksts netiek dzēsts, ja lietotājs pāriet prom.',
            raw_storage: true
        };
    }
    function keyboardSelect() {
        return {
            interaction: 'select',
            focus_order: 'lauki autorētajā secībā',
            keys: selectKeys('izvēlēto vērtību fokusētajā laukā', 'fokuss uz nākamo/iepriekšējo lauku'),
            pointer_equivalent_lv: 'noklikšķināt uz nolaižamā saraksta un izvēlēties vērtību',
            abort_lv: 'Escape atceļ neatstiprināto izvēli.'
        };
    }
    function selectKeys(commitEffect, focusEffect) {
        return [
            { key: 'ArrowUp', effect_lv: 'iepriekšējā vērtība: ' + commitEffect },
            { key: 'ArrowDown', effect_lv: 'nākamā vērtība: ' + commitEffect },
            { key: 'ArrowLeft', effect_lv: focusEffect },
            { key: 'ArrowRight', effect_lv: focusEffect },
            { key: 'Enter', effect_lv: 'apstiprina izvēli' },
            { key: 'Escape', effect_lv: 'atceļ neatstiprināto izvēli' },
            { key: 'Tab', effect_lv: 'netiek pārtverts; fokuss atstāj komponenti' }
        ];
    }
    function keyboardCheckboxGroup() {
        return {
            interaction: 'checkbox',
            focus_order: 'apgalvojumi autorētajā secībā',
            keys: [
                { key: 'ArrowLeft', effect_lv: 'fokuss uz iepriekšējo apgalvojumu' },
                { key: 'ArrowRight', effect_lv: 'fokuss uz nākamo apgalvojumu' },
                { key: 'Enter', effect_lv: 'pārslēdz atzīmi fokusētajam apgalvojumam' },
                { key: 'Space', effect_lv: 'pārslēdz atzīmi fokusētajam apgalvojumam' },
                { key: 'Tab', effect_lv: 'netiek pārtverts' }
            ],
            pointer_equivalent_lv: 'noklikšķināt uz atzīmes lodziņa',
            abort_lv: 'Atzīmes tiek glabātas uzreiz; pāreja prom tās nedzēš.',
            never_color_only: true
        };
    }
    /* -------------------------------------------------------- interaction */
    /* `options.capture_context_id` (and `options.figure_id`) let the assembler
     * bind a spatial instance to the shipped N18 capture context, because the
     * registry is type-level and carries no per-instance figure. */
    function initialState(typeId, contract, instance, options) {
        assertContractShape(typeId, contract);
        if (!isPlainObject(instance)) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Tipam ' + typeId + ' nav instances.', { type_id: typeId });
        }
        const opts = isPlainObject(options) ? options : {};
        const graph = isPlainObject(contract.graph) ? contract.graph : {};
        const state = {
            type_id: typeId,
            instance: clone(instance),
            capture_context_id: opts.capture_context_id
                || graph.capture_context_id || contract.capture_context_id || null,
            figure_id: opts.figure_id || graph.figure_id || null,
            figures: Array.isArray(opts.figures) ? clone(opts.figures) : null,
            values: {},
            selections: {},
            cursors: {},
            order: [],
            pairs: {},
            placements: [],
            gesture: null,
            capture: null,
            target: null,
            focus: 0,
            cancelled: false
        };
        if (typeId === 'Q17') {
            const structure = isPlainObject(contract.structure) ? contract.structure : {};
            const start = isPlainObject(structure.target_start) ? structure.target_start : { x: 0, y: 0 };
            state.target = { x: Number(start.x), y: Number(start.y) };
        }
        return state;
    }
    function parseRaw(text) {
        if (typeof text === 'number') {
            return isFinite(text) ? text : null;
        }
        if (typeof text !== 'string') {
            return null;
        }
        const trimmed = text.replace(/\s+/g, '');
        if (!trimmed) {
            return null;
        }
        const hasComma = trimmed.indexOf(',') !== -1;
        const hasDot = trimmed.indexOf('.') !== -1;
        if (hasComma && hasDot) {
            return null;
        }
        if (!/^[+-]?(\d+([.,]\d*)?|[.,]\d+)([eE][+-]?\d+)?$/.test(trimmed)) {
            return null;
        }
        const value = Number(trimmed.replace(',', '.'));
        return isFinite(value) ? value : null;
    }
    function quantize(value) { return round12(value); }
    function formatRaw(value, decimals) {
        const number = Number(value);
        if (!isFinite(number)) {
            return '';
        }
        let text = number.toFixed(decimals);
        if (/^-0[.,]0+$/.test(text)) {
            text = text.slice(1);
        }
        return text.replace('.', ',');
    }
    function captureSettings(contract, state) {
        const graph = isPlainObject(contract.graph) ? contract.graph : {};
        const contextId = (state && typeof state.capture_context_id === 'string'
            && state.capture_context_id) || graph.capture_context_id || contract.capture_context_id;
        if (typeof contextId !== 'string' || !contextId) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Grafika līgumam jādeklarē graph.capture_context_id.', {
                type_id: contract.id, field_id: 'draw_payload'
            });
        }
        const engine = root.SimGraphScoring;
        if (!engine || typeof engine.capturePath !== 'function') {
            fail('E_INPUTS_GRAPH_ENGINE_MISSING', 'SimGraphScoring nav ielādēts: grafika uztveršana nav iespējama.', {
                type_id: contract.id, context_id: contextId
            });
        }
        const engineState = engine.state;
        const captureContract = engineState && engineState.contract
            ? engineState.contract.capture_contract : null;
        const context = captureContract && captureContract.capture_contexts
            ? captureContract.capture_contexts[contextId] : null;
        if (!context) {
            fail('E_INPUTS_GRAPH_CONTEXT_MISSING', 'Uztveršanas konteksts "' + contextId + '" nav atrasts N18 līgumā.', {
                type_id: contract.id, context_id: contextId
            });
        }
        return { contextId: contextId, context: context, engine: engine };
    }
    function newCapture(contract, ratio, state) {
        const settings = captureSettings(contract, state);
        const component = root.SimGraphCapture;
        if (!component || typeof component.create !== 'function') {
            fail('E_INPUTS_CAPTURE_MISSING', 'SimGraphCapture nav ielādēts: grafika uztveršana nav iespējama.', {
                type_id: contract.id
            });
        }
        const options = {
            engine: settings.engine,
            context: settings.context,
            contextId: settings.contextId
        };
        if (ratio !== null) {
            options.pointerSampleRatio = ratio;
        }
        return component.create(options);
    }
    function captureFromPath(contract, path, state) {
        const api = newCapture(contract, 0, state);
        if (path.length) {
            api.pointer.begin([path[0].x, path[0].y]);
            for (let i = 1; i < path.length; i += 1) {
                api.pointer.move([path[i].x, path[i].y]);
            }
        }
        return api;
    }
    function appendCapturePoint(state, contract, point) {
        const path = state.capture && Array.isArray(state.capture.path) ? state.capture.path : [];
        const api = captureFromPath(contract, path, state);
        if (!path.length) {
            api.pointer.begin([point.x, point.y]);
        }
        else {
            api.pointer.move([point.x, point.y]);
        }
        state.capture = {
            context_id: (state.capture && state.capture.context_id) || captureSettings(contract, state).contextId,
            path: api.path(),
            committed: api.pointer.end() || null
        };
        return state.capture;
    }
    function focusIndex(planned, state) {
        if (typeof state.focus !== 'number' || state.focus < 0 || state.focus >= planned.length) {
            return 0;
        }
        return state.focus;
    }
    function moveFocus(state, planned, delta) {
        const count = planned.length;
        if (!count) {
            return;
        }
        state.focus = ((focusIndex(planned, state) + delta) % count + count) % count;
    }
    function optionList(leafEntry, contract, instance, typeId, state) {
        if (Array.isArray(leafEntry.options)) {
            return leafEntry.options;
        }
        const template = templateForRole(contract, leafEntry.role);
        if (!template) {
            return [];
        }
        const context = state && Array.isArray(state.figures) ? { figures: state.figures } : {};
        return contractOptions({ typeId: typeId, instance: instance, context: context, termIndex: null }, template).filter((option) => option.value !== null);
    }
    function templateForRole(contract, role) {
        const templates = Array.isArray(contract.fields) ? contract.fields : [];
        for (let i = 0; i < templates.length; i += 1) {
            if (templates[i].role === role) {
                return templates[i];
            }
        }
        return null;
    }
    function leafById(planned, fieldId) {
        for (let i = 0; i < planned.length; i += 1) {
            if (planned[i].field_id === fieldId) {
                return planned[i];
            }
        }
        return null;
    }
    function cursorValue(leafEntry, state, options) {
        const cursor = typeof state.cursors[leafEntry.field_id] === 'number'
            ? state.cursors[leafEntry.field_id] : 0;
        const option = options[Math.max(0, Math.min(options.length - 1, cursor))];
        return option ? String(option.value) : '';
    }
    function cycleSelect(state, leafEntry, options, delta) {
        if (!options.length) {
            return;
        }
        const current = typeof state.cursors[leafEntry.field_id] === 'number'
            ? state.cursors[leafEntry.field_id] : 0;
        state.cursors[leafEntry.field_id] = ((current + delta) % options.length + options.length) % options.length;
    }
    function applyKey(typeId, contract, state, event) {
        const planned = planLeaves(typeId, contract, state.instance);
        const next = clone(state);
        const events = [];
        const key = event && event.key !== undefined ? String(event.key) : '';
        if (!key) {
            return { state: next, events: events };
        }
        if (key === 'Tab') {
            events.push({ kind: 'focus_out' });
            return { state: next, events: events };
        }
        if (key === 'Escape') {
            return cancel(typeId, contract, next, 'escape');
        }
        if (key === 'ArrowLeft') {
            moveFocus(next, planned, -1);
            return { state: next, events: events };
        }
        if (key === 'ArrowRight') {
            moveFocus(next, planned, 1);
            return { state: next, events: events };
        }
        const leafEntry = planned[focusIndex(planned, next)];
        if (!leafEntry) {
            return { state: next, events: events };
        }
        const control = (CONTROLS[(templateForRole(contract, leafEntry.role) || {}).control]
            || { control: 'textbox' }).control;
        if (key === 'ArrowUp' || key === 'ArrowDown') {
            /* In a list, ArrowDown moves to the next option. On a target or a
             * coordinate cell, ArrowUp increases the value. */
            const listDelta = key === 'ArrowDown' ? 1 : -1;
            const axisDelta = key === 'ArrowUp' ? 1 : -1;
            const fine = Boolean(event && event.shiftKey);
            if (control === 'select' || control === 'radio') {
                cycleSelect(next, leafEntry, optionList(leafEntry, contract, next.instance, typeId, next), listDelta);
                events.push({ kind: 'cursor', field_id: leafEntry.field_id });
                return { state: next, events: events };
            }
            if (leafEntry.role === 'structure_palette') {
                const options = structureOptions(contract, next.instance);
                cycleSelect(next, leafEntry, options, listDelta);
                const value = cursorValue(leafEntry, next, options);
                if (value) {
                    next.gesture = { part_id: value, x: next.target ? next.target.x : 0,
                        y: next.target ? next.target.y : 0 };
                }
                events.push({ kind: 'palette_selection', part_id: value });
                return { state: next, events: events };
            }
            if (leafEntry.role === 'structure_target') {
                const axis = leafEntry.writes.axis;
                stepTarget(next, contract, axis === 'x' ? axisDelta : 0, axis === 'y' ? axisDelta : 0, fine);
                events.push({ kind: 'target', x: next.target.x, y: next.target.y });
                return { state: next, events: events };
            }
            if (leafEntry.role === 'record') {
                stepCoordinate(next, contract, leafEntry, axisDelta, fine);
                events.push({ kind: 'field_value', field_id: leafEntry.field_id,
                    raw: next.values[leafEntry.field_id] === undefined ? '' : next.values[leafEntry.field_id] });
                return { state: next, events: events };
            }
            return { state: next, events: events };
        }
        if (key === 'Enter') {
            return commitFocus(typeId, contract, next, leafEntry, control, events);
        }
        if ((key === ' ' || key === 'Space') && control === 'checkbox') {
            return toggleCheckbox(typeId, contract, next, leafEntry, events);
        }
        const textLike = control === 'textbox' || control === 'textarea'
            || control === 'coefficient' || control === 'graph_canvas'
            || control === 'placement' || control === 'coordinate_table';
        if (key === 'Backspace' && textLike) {
            const raw = next.values[leafEntry.field_id] === undefined
                ? '' : String(next.values[leafEntry.field_id]);
            next.values[leafEntry.field_id] = raw.slice(0, Math.max(0, raw.length - 1));
            events.push({ kind: 'field_value', field_id: leafEntry.field_id,
                raw: next.values[leafEntry.field_id] });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, next) });
            return { state: next, events: events };
        }
        if (key.length === 1 && textLike) {
            const raw = next.values[leafEntry.field_id] === undefined
                ? '' : String(next.values[leafEntry.field_id]);
            /* Stored exactly as typed: no separator rewriting, no coercion, no trim. */
            next.values[leafEntry.field_id] = raw + key;
            events.push({ kind: 'field_value', field_id: leafEntry.field_id,
                raw: next.values[leafEntry.field_id] });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, next) });
            return { state: next, events: events };
        }
        return { state: next, events: events };
    }
    function structureOptions(_contract, instance) {
        const parts = readPath(instance, 'payload.structure_parts');
        if (!Array.isArray(parts)) {
            return [];
        }
        return parts.map((part) => ({ value: String(part.part_id), text_lv: part.text_lv }));
    }
    function stepTarget(state, contract, dx, dy, fine) {
        const structure = isPlainObject(contract.structure) ? contract.structure : {};
        const step = isPlainObject(structure.step) ? structure.step : { x: 1, y: 1 };
        const factor = fine ? 0.5 : 1;
        if (!state.target) {
            state.target = { x: 0, y: 0 };
        }
        state.target.x = quantize(Number(state.target.x) + dx * Number(step.x) * factor);
        state.target.y = quantize(Number(state.target.y) + dy * Number(step.y) * factor);
        if (state.gesture) {
            state.gesture.x = state.target.x;
            state.gesture.y = state.target.y;
        }
    }
    function stepCoordinate(state, contract, leafEntry, delta, fine) {
        let step;
        if (isPlainObject(contract.graph) && contract.graph.capture_context_id) {
            const settings = captureSettings(contract, state);
            const increments = settings.engine.keyboardIncrements(settings.contextId);
            step = leafEntry.writes.axis === 'x'
                ? (fine ? increments.fine_x : increments.coarse_x)
                : (fine ? increments.fine_y : increments.coarse_y);
        }
        else {
            const steps = contract.keyboard && contract.keyboard.table_steps
                ? contract.keyboard.table_steps : { x: 1, y: 1 };
            step = Number(leafEntry.writes.axis === 'x' ? steps.x : steps.y);
            if (fine) {
                step = step / 10;
            }
        }
        const decimals = Number(contract.read_decimals === undefined ? 3 : contract.read_decimals);
        const current = parseRaw(state.values[leafEntry.field_id]);
        const base = current === null ? 0 : current;
        state.values[leafEntry.field_id] = formatRaw(quantize(base + delta * step), decimals);
    }
    function commitFocus(typeId, contract, state, leafEntry, control, events) {
        const writes = leafEntry.writes;
        if (control === 'checkbox') {
            return toggleCheckbox(typeId, contract, state, leafEntry, events);
        }
        if (leafEntry.role === 'structure_palette') {
            const options = structureOptions(contract, state.instance);
            const value = cursorValue(leafEntry, state, options);
            if (!value) {
                events.push({ kind: 'palette_selection', part_id: null });
                return { state: state, events: events };
            }
            state.gesture = { part_id: value, x: state.target ? state.target.x : 0,
                y: state.target ? state.target.y : 0 };
            state.selections.palette = value;
            events.push({ kind: 'palette_selection', part_id: value });
            return { state: state, events: events };
        }
        if (leafEntry.role === 'structure_target' || writes.kind === 'placement') {
            if (!state.gesture || !state.gesture.part_id) {
                events.push({ kind: 'placement_rejected', reason: 'NO_PALETTE_SELECTION' });
                return { state: state, events: events };
            }
            const placement = {
                part_id: String(state.gesture.part_id),
                x: quantize(state.target ? state.target.x : 0),
                y: quantize(state.target ? state.target.y : 0)
            };
            state.placements = (state.placements || []).concat([placement]);
            state.gesture = null;
            events.push({ kind: 'placement', placement: placement });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
            return { state: state, events: events };
        }
        if (writes.kind === 'position_slot') {
            const options = optionList(leafEntry, contract, state.instance, typeId, state);
            const value = cursorValue(leafEntry, state, options);
            const position = Number(writes.position);
            const order = Array.isArray(state.order) ? state.order.slice() : [];
            while (order.length < position) {
                order.push(null);
            }
            if (value) {
                for (let i = 0; i < order.length; i += 1) {
                    if (order[i] === value) {
                        order[i] = null;
                    }
                }
                order[position - 1] = value;
            }
            else {
                order[position - 1] = null;
            }
            state.order = order;
            events.push({ kind: 'selection', field_id: leafEntry.field_id, value: value });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
            return { state: state, events: events };
        }
        if (writes.kind === 'pair') {
            const options = optionList(leafEntry, contract, state.instance, typeId, state);
            const value = cursorValue(leafEntry, state, options);
            state.pairs = state.pairs || {};
            if (value) {
                state.pairs[writes.left_id] = value;
            }
            else {
                delete state.pairs[writes.left_id];
            }
            events.push({ kind: 'selection', field_id: leafEntry.field_id, value: value });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
            return { state: state, events: events };
        }
        if (writes.kind === 'row') {
            return commitRow(typeId, contract, state, leafEntry, events);
        }
        if (control === 'select' || control === 'radio') {
            const options = optionList(leafEntry, contract, state.instance, typeId, state);
            const value = cursorValue(leafEntry, state, options);
            const mapped = radioStoreKey(leafEntry, state);
            if (value) {
                state.values[mapped] = value;
            }
            else {
                delete state.values[mapped];
            }
            events.push({ kind: 'selection', field_id: leafEntry.field_id, value: value });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
            return { state: state, events: events };
        }
        const rawText = state.values[leafEntry.field_id] === undefined
            ? '' : String(state.values[leafEntry.field_id]);
        state.values[leafEntry.field_id] = rawText;
        events.push({ kind: 'commit', field_id: leafEntry.field_id, raw: rawText });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    /* The value map key a select/radio leaf writes. The leaf id is the renderer's
     * own id, except where the frozen payload names the key differently. */
    function radioStoreKey(leafEntry, _state) {
        if (leafEntry.writes && leafEntry.writes.kind === 'value') {
            return leafEntry.writes.key;
        }
        return leafEntry.field_id;
    }
    function toggleCheckbox(typeId, contract, state, leafEntry, events) {
        const optionId = String(leafEntry.writes.option_id);
        const selected = Array.isArray(state.selections.__selected)
            ? state.selections.__selected.slice() : [];
        const at = selected.indexOf(optionId);
        if (at === -1) {
            selected.push(optionId);
        }
        else {
            selected.splice(at, 1);
        }
        state.selections.__selected = selected;
        events.push({ kind: 'selection', field_id: leafEntry.field_id, value: optionId,
            selected: selected.slice() });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    function commitRow(typeId, contract, state, leafEntry, events) {
        const rowIndex = Number(leafEntry.writes.row_index);
        const row = {
            x: state.values['pt' + rowIndex + '_x'],
            y: state.values['pt' + rowIndex + '_y']
        };
        const xValue = parseRaw(row.x === undefined ? '' : row.x);
        const yValue = parseRaw(row.y === undefined ? '' : row.y);
        if (xValue === null || yValue === null) {
            events.push({
                kind: 'row_rejected',
                row_index: rowIndex,
                reason: 'UNREADABLE_INPUT',
                raw: { x: row.x === undefined ? '' : row.x, y: row.y === undefined ? '' : row.y }
            });
            return { state: state, events: events };
        }
        appendCapturePoint(state, contract, { x: quantize(xValue), y: quantize(yValue) });
        events.push({
            kind: 'row_commit', row_index: rowIndex, x: quantize(xValue), y: quantize(yValue),
            draw_payload: state.capture ? state.capture.committed : null
        });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    function cancel(_typeId, _contract, state, reason) {
        const next = clone(state);
        const events = [];
        let discarded = false;
        if (next.gesture) {
            next.gesture = null;
            discarded = true;
        }
        if (next.selections && next.selections.palette) {
            delete next.selections.palette;
        }
        if (next.capture && ((next.capture.path && next.capture.path.length)
            || (next.capture.committed && next.capture.committed.points
                && next.capture.committed.points.length))) {
            next.capture = { context_id: next.capture.context_id, path: [], committed: null };
            discarded = true;
        }
        next.cancelled = true;
        events.push({ kind: 'cancel', reason: String(reason), discarded: discarded,
            committed: committed(_typeId, _contract, next) });
        return { state: next, events: events };
    }
    function pointerEvent(typeId, contract, state, action) {
        const planned = planLeaves(typeId, contract, state.instance);
        const next = clone(state);
        const events = [];
        if (!isPlainObject(action)) {
            return { state: next, events: events };
        }
        if (action.kind === 'select') {
            const leafEntry = leafById(planned, String(action.field_id));
            if (!leafEntry) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Norādes darbība mērķē lauku "' + String(action.field_id) + '", ko plāns nepazīst.', {
                    type_id: typeId, field_id: String(action.field_id)
                });
            }
            const control = (CONTROLS[(templateForRole(contract, leafEntry.role) || {}).control]
                || { control: 'textbox' }).control;
            const options = leafEntry.role === 'structure_palette'
                ? structureOptions(contract, next.instance)
                : optionList(leafEntry, contract, next.instance, typeId, next);
            let index = -1;
            for (let i = 0; i < options.length; i += 1) {
                if (String(options[i].value) === String(action.value)) {
                    index = i;
                }
            }
            if (index === -1 && control !== 'checkbox') {
                events.push({ kind: 'selection_rejected', field_id: leafEntry.field_id,
                    reason: 'UNKNOWN_OPTION', value: action.value });
                return { state: next, events: events };
            }
            if (index !== -1) {
                next.cursors[leafEntry.field_id] = index;
            }
            if (control === 'checkbox') {
                return toggleCheckbox(typeId, contract, next, leafEntry, events);
            }
            if (leafEntry.role === 'structure_palette') {
                const value = String(action.value);
                next.selections.palette = value;
                next.gesture = { part_id: value, x: next.target ? next.target.x : 0,
                    y: next.target ? next.target.y : 0 };
                events.push({ kind: 'palette_selection', part_id: value });
                return { state: next, events: events };
            }
            return commitFocus(typeId, contract, next, leafEntry, control, events);
        }
        if (action.kind === 'text') {
            const leafEntry = leafById(planned, String(action.field_id));
            if (!leafEntry) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Norādes ievade mērķē lauku "' + String(action.field_id) + '", ko plāns nepazīst.', {
                    type_id: typeId, field_id: String(action.field_id)
                });
            }
            next.values[leafEntry.field_id] = String(action.text === undefined ? '' : action.text);
            events.push({ kind: 'field_value', field_id: leafEntry.field_id,
                raw: next.values[leafEntry.field_id] });
            events.push({ kind: 'payload', payload: payloadOf(typeId, contract, next) });
            return { state: next, events: events };
        }
        if (action.kind === 'place') {
            return placeStructure(typeId, contract, next, events, action);
        }
        if (action.kind === 'draw_begin' || action.kind === 'draw_move' || action.kind === 'draw_end') {
            return drawAction(typeId, contract, next, events, action);
        }
        if (action.kind === 'read') {
            return readAction(typeId, contract, next, events, action);
        }
        events.push({ kind: 'action_rejected', reason: 'UNKNOWN_ACTION', action: action.kind });
        return { state: next, events: events };
    }
    function placeStructure(typeId, contract, state, events, action) {
        const partId = action.part_id === undefined || action.part_id === null
            ? (state.gesture ? state.gesture.part_id : null) : String(action.part_id);
        if (!partId) {
            events.push({ kind: 'placement_rejected', reason: 'NO_PALETTE_SELECTION' });
            return { state: state, events: events };
        }
        const placement = {
            part_id: partId,
            x: quantize(action.x === undefined ? (state.target ? state.target.x : 0) : action.x),
            y: quantize(action.y === undefined ? (state.target ? state.target.y : 0) : action.y)
        };
        state.placements = (state.placements || []).concat([placement]);
        state.gesture = null;
        events.push({ kind: 'placement', placement: placement });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    function drawAction(typeId, contract, state, events, action) {
        if (action.kind === 'draw_begin') {
            const point = { x: quantize(action.x), y: quantize(action.y) };
            state.capture = { context_id: captureSettings(contract, state).contextId, path: [point],
                committed: null };
            events.push({ kind: 'draw_begin', point: point });
            return { state: state, events: events };
        }
        if (!state.capture) {
            events.push({ kind: 'action_rejected', reason: 'NO_DRAW_IN_PROGRESS' });
            return { state: state, events: events };
        }
        if (action.kind === 'draw_move') {
            const point = { x: quantize(action.x), y: quantize(action.y) };
            const path = state.capture.path || [];
            const api = newCapture(contract, null, state);
            if (path.length) {
                api.pointer.begin([path[0].x, path[0].y]);
                for (let i = 1; i < path.length; i += 1) {
                    api.pointer.move([path[i].x, path[i].y]);
                }
                api.pointer.move([point.x, point.y]);
            }
            else {
                api.pointer.begin([point.x, point.y]);
            }
            state.capture.path = api.path();
            events.push({ kind: 'draw_move', point: point, path: state.capture.path.slice() });
            return { state: state, events: events };
        }
        const api = captureFromPath(contract, state.capture.path || [], state);
        const committedPayload = api.pointer.end();
        state.capture = {
            context_id: state.capture.context_id,
            path: state.capture.path || [],
            committed: committedPayload === undefined ? null : committedPayload
        };
        events.push({ kind: 'draw_end', draw_payload: state.capture.committed });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    function readAction(typeId, contract, state, events, action) {
        const decimals = Number(contract.read_decimals === undefined ? 2 : contract.read_decimals);
        state.values.read_x = formatRaw(quantize(action.x), decimals);
        state.values.read_y = formatRaw(quantize(action.y), decimals);
        events.push({ kind: 'read', x: state.values.read_x, y: state.values.read_y });
        events.push({ kind: 'payload', payload: payloadOf(typeId, contract, state) });
        return { state: state, events: events };
    }
    function payloadOf(typeId, contract, state) {
        if (!state) {
            return null;
        }
        switch (typeId) {
            case 'Q01':
            case 'Q09':
            case 'Q10':
            case 'Q02':
                return { kind: 'numeric', values: numericValues(state) };
            case 'Q03':
                return {
                    kind: 'method', variant: 'Q03_template',
                    choice: firstDefinedDefined(state.values.choice, state.values.template),
                    fill_ins: fillInsOf(state),
                    conserved: firstDefined(state.values.conserved, '')
                };
            case 'Q04':
                return { kind: 'method', variant: 'Q04_vector', vector: vectorOf(state) };
            case 'Q05':
                return { kind: 'method', variant: 'Q05_rows', rows: rowsOf(state) };
            case 'Q06':
                return { kind: 'matching', pairs: pairsOf(state) };
            case 'Q07':
            case 'Q14':
            case 'Q18': {
                const payload = { kind: 'option_select', selected: selectedOf(state) };
                if (state.values.justification !== undefined) {
                    payload.justification = state.values.justification;
                }
                return payload;
            }
            case 'Q08': {
                const payload = { kind: 'ordering', order: orderOf(state) };
                if (state.values.explanation !== undefined) {
                    payload.explanation = state.values.explanation;
                }
                return payload;
            }
            case 'Q11':
                return {
                    kind: 'graph', variant: 'Q11_record',
                    record: recordOf(contract, state),
                    draw_payload: state.capture ? state.capture.committed : null
                };
            case 'Q12':
                return {
                    kind: 'graph', variant: 'Q12_read',
                    read: {
                        x: firstDefined(state.values.read_x, ''),
                        y: firstDefined(state.values.read_y, ''),
                        figure_binding: firstDefined(state.values.figure_binding, '')
                    }
                };
            case 'Q13':
                return {
                    kind: 'method', variant: 'Q13_vector', vector: vectorOf(state),
                    located: firstDefined(state.values.located, ''),
                    replacement: firstDefined(state.values.replacement, ''),
                    reason: firstDefined(state.values.reason, '')
                };
            case 'Q15':
                return { kind: 'method', variant: 'Q15_text', text: firstDefined(state.values.text, '') };
            case 'Q16':
                return { kind: 'method', variant: 'Q16_text', text: firstDefined(state.values.text, '') };
            case 'Q17': {
                const payload = {
                    kind: 'method', variant: 'Q17_pairs', pair_map: pairMapOf(state)
                };
                if (state.placements && state.placements.length) {
                    payload.structure = { placements: state.placements.slice() };
                }
                return payload;
            }
            default:
                fail('E_INPUTS_UNKNOWN_TYPE', 'N22 komponente neprot veidot ķermeni tipam "' + String(typeId) + '".', {
                    type_id: typeId
                });
        }
    }
    function firstDefined(value, fallback) {
        return value === undefined || value === null ? fallback : value;
    }
    function firstDefinedDefined(value, fallback) {
        const chosen = firstDefined(value, fallback);
        return chosen === undefined || chosen === null ? '' : chosen;
    }
    function numericValues(state) {
        const out = {};
        Object.keys(state.values).sort().forEach((key) => {
            if (key === 'unit') {
                return;
            }
            if (key === 'template' || key === 'choice' || key === 'conserved') {
                return;
            }
            if (key === 'located' || key === 'replacement' || key === 'reason') {
                return;
            }
            if (key === 'text' || key === 'justification' || key === 'explanation') {
                return;
            }
            if (key === 'read_x' || key === 'read_y' || key === 'figure_binding') {
                return;
            }
            if (key.indexOf('fill_') === 0 || key.indexOf('row_') === 0) {
                return;
            }
            if (key.indexOf('pair_') === 0 || key.indexOf('opt_') === 0) {
                return;
            }
            if (key.indexOf('place_') === 0) {
                return;
            }
            if (key.indexOf('pt') === 0) {
                return;
            }
            out[key] = state.values[key];
        });
        return out;
    }
    function fillInsOf(state) {
        const out = {};
        Object.keys(state.values).sort().forEach((key) => {
            if (key.indexOf('fill_') === 0) {
                out[key.slice(5)] = state.values[key];
            }
        });
        return out;
    }
    function rowsOf(state) {
        const out = {};
        Object.keys(state.values).sort().forEach((key) => {
            if (key.indexOf('row_') === 0) {
                out[key.slice(4)] = state.values[key];
            }
        });
        return out;
    }
    function pairMapOf(state) {
        const out = {};
        Object.keys(state.values).sort().forEach((key) => {
            if (key.indexOf('pair_') === 0) {
                out[key.slice(5)] = state.values[key];
            }
        });
        return out;
    }
    function vectorOf(state) {
        const keys = Object.keys(state.values).filter((key) => key.indexOf('coef_') === 0);
        keys.sort((a, b) => Number(a.split('_')[1]) - Number(b.split('_')[1]));
        return keys.map((key) => state.values[key]);
    }
    function selectedOf(state) {
        return Array.isArray(state.selections.__selected) ? state.selections.__selected.slice() : [];
    }
    function orderOf(state) {
        return (state.order || []).filter((item) => item !== null && item !== undefined);
    }
    function pairsOf(state) {
        const pairs = state.pairs || {};
        return Object.keys(pairs).sort().map((left) => ({
            left_id: left, right_id: pairs[left]
        }));
    }
    function recordOf(contract, state) {
        const graph = isPlainObject(contract.graph) ? contract.graph : {};
        const instance = state.instance || {};
        const xAxis = readPath(instance, 'payload.x_axis') || {};
        const yAxis = readPath(instance, 'payload.y_axis') || {};
        const mode = readPath(instance, 'payload.mode');
        const figureId = state.figure_id || graph.figure_id;
        const contextId = state.capture_context_id || graph.capture_context_id;
        /* The record is the constructed table the learner filled: the placed
         * points in figure coordinates plus the declared axes. The registry's
         * Q11_record completion rule reads record.points for the declared count. */
        const placed = state.capture && Array.isArray(state.capture.path)
            ? state.capture.path : [];
        return {
            figure_id: figureId === undefined ? null : figureId,
            capture_context_id: contextId === undefined ? null : contextId,
            mode: mode === undefined ? 'construct' : mode,
            points: placed.map((point) => ({ x: point.x, y: point.y })),
            x_axis: { label_lv: xAxis.label_lv === undefined ? '' : xAxis.label_lv,
                unit: xAxis.unit === undefined ? '' : xAxis.unit },
            y_axis: { label_lv: yAxis.label_lv === undefined ? '' : yAxis.label_lv,
                unit: yAxis.unit === undefined ? '' : yAxis.unit }
        };
    }
    function committed(_typeId, _contract, state) {
        return {
            placements: state && Array.isArray(state.placements) ? clone(state.placements) : [],
            draw_payload: state && state.capture ? clone(state.capture.committed) : null,
            pairs: state && state.pairs ? clone(state.pairs) : {},
            order: state && Array.isArray(state.order) ? clone(orderOf(state)) : []
        };
    }
    /* -------------------------------------------------------- completion */
    /* The registry module (N22-A) owns the completion verdict. When it is
     * loaded the component consumes it verbatim and says so in `source`; when it
     * is absent (or refuses because it was never loaded) the component falls
     * back to the contract's own completion_rule and records that too, so N23
     * always knows which path produced the missing list. */
    function completionOf(contract, payload, instance) {
        const registry = root.SimInputsRegistry;
        if (registry && typeof registry.completion === 'function') {
            try {
                const verdict = registry.completion(contract && typeof contract.id === 'string' ? contract.id : '', contract, instance, payload);
                if (isPlainObject(verdict) && typeof verdict.status === 'string') {
                    return {
                        status: verdict.status,
                        missing: Array.isArray(verdict.missing) ? verdict.missing : [],
                        errors: Array.isArray(verdict.errors) ? verdict.errors : [],
                        source: 'SimInputsRegistry.completion'
                    };
                }
            }
            catch (error) {
                const cause = error;
                const local = localCompletion(contract, payload, instance);
                local.source = 'component_fallback';
                local.registry_error = {
                    code: cause && cause.code ? String(cause.code) : null,
                    message: cause && cause.message ? String(cause.message) : String(cause)
                };
                return local;
            }
        }
        return localCompletion(contract, payload, instance);
    }
    function missingEntry(fieldId, labelKey, reason, extra) {
        return Object.assign({
            field_id: fieldId,
            label_key: labelKey === undefined ? null : labelKey,
            reason: reason
        }, extra || {});
    }
    function localCompletion(contract, payload, instance) {
        const rule = isPlainObject(contract) && isPlainObject(contract.completion_rule)
            ? contract.completion_rule : {};
        const body = isPlainObject(payload) ? payload : {};
        const missing = [];
        const ruleMissing = isPlainObject(rule.missing) ? rule.missing : {};
        const model = rule.model;
        if (model === 'numeric') {
            const values = isPlainObject(body.values) ? body.values : {};
            const fields = readPath(instance || {}, String(rule.fields_from || '').replace(/^instance\./, ''));
            if (Array.isArray(fields)) {
                fields.forEach((field) => {
                    if (values[field.field_id] === undefined || String(values[field.field_id]) === '') {
                        missing.push(missingEntry(String(field.field_id), ruleMissing.value, 'empty', { slot: field.label_lv }));
                    }
                });
            }
            if (rule.include_steps) {
                const steps = readPath(instance || {}, String(rule.steps_from || '').replace(/^instance\./, ''));
                if (Array.isArray(steps)) {
                    steps.forEach((step) => {
                        if (values[step.step_id] === undefined || String(values[step.step_id]) === '') {
                            missing.push(missingEntry(String(step.step_id), ruleMissing.step, 'empty', { slot: step.prompt_lv }));
                        }
                    });
                }
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'vector') {
            const vector = Array.isArray(body.vector) ? body.vector : [];
            const species = readPath(instance || {}, String(rule.species_from || '').replace(/^instance\./, ''));
            const count = Array.isArray(species) ? species.length : vector.length;
            for (let i = 0; i < count; i += 1) {
                if (vector[i] === undefined || vector[i] === null || String(vector[i]) === '') {
                    missing.push(missingEntry('coef_' + String(i), ruleMissing.coefficient, 'empty', { slot: Array.isArray(species) ? String(species[i]) : String(i) }));
                }
            }
            const required = Array.isArray(rule.required_fields) ? rule.required_fields : [];
            required.forEach((entry) => {
                const value = body[entry.field_id];
                if (value === undefined || value === null || String(value) === '') {
                    missing.push(missingEntry(String(entry.field_id), entry.label_key, 'empty'));
                }
            });
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'rows') {
            const rows = isPlainObject(body.rows) ? body.rows : {};
            const steps = readPath(instance || {}, String(rule.steps_from || '').replace(/^instance\./, ''));
            const list = Array.isArray(steps) ? steps.map((step) => String(step.step_id)) : Object.keys(rows);
            list.forEach((stepId) => {
                if (rows[stepId] === undefined || String(rows[stepId]) === '') {
                    missing.push(missingEntry('row_' + stepId, ruleMissing.row, 'empty', { slot: stepId }));
                }
            });
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'pairs') {
            const pairs = Array.isArray(body.pairs) ? body.pairs : [];
            const assigned = {};
            pairs.forEach((pair) => { if (pair && pair.left_id) {
                assigned[pair.left_id] = pair.right_id;
            } });
            const left = readPath(instance || {}, String(rule.left_from || '').replace(/^instance\./, ''));
            if (Array.isArray(left)) {
                left.forEach((item) => {
                    if (!assigned[item.id]) {
                        missing.push(missingEntry('pair_' + String(item.id), ruleMissing.pair, 'unassigned', { slot: item.text_lv }));
                    }
                });
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'selection') {
            if (!Array.isArray(body.selected) || !body.selected.length) {
                missing.push(missingEntry('selected', ruleMissing.selection, 'empty'));
            }
            if (rule.justification_path) {
                const value = body[rule.justification_path];
                const required = readPath(instance || {}, String(rule.justification_required_from || '').replace(/^instance\./, ''));
                if (required !== false && (value === undefined || String(value).trim() === '')) {
                    missing.push(missingEntry(String(rule.justification_path), ruleMissing.justification, 'empty'));
                }
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'order') {
            const order = Array.isArray(body.order) ? body.order : [];
            const items = readPath(instance || {}, String(rule.items_from || '').replace(/^instance\./, ''));
            if (Array.isArray(items)) {
                items.forEach((item) => {
                    if (order.indexOf(item.item_id) === -1) {
                        missing.push(missingEntry('place_' + String(item.item_id), ruleMissing.order_item, 'unplaced', { slot: item.text_lv }));
                    }
                });
            }
            if (rule.explanation_required) {
                const explanation = body[String(rule.explanation_path || 'explanation')];
                if (explanation === undefined || String(explanation).trim() === '') {
                    missing.push(missingEntry('explanation', ruleMissing.explanation, 'empty'));
                }
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'text') {
            const text = body[String(rule.text_path || 'text')];
            const length = text === undefined || text === null ? 0 : String(text).trim().length;
            const min = Number(rule.min_chars || 1);
            if (length < min) {
                missing.push(missingEntry(String(rule.text_path || 'text'), ruleMissing.text, length === 0 ? 'blank' : 'below_min_chars', { length: length, min_chars: min }));
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'template') {
            if (!body[String(rule.choice_path || 'choice')]) {
                missing.push(missingEntry('choice', ruleMissing.template, 'empty'));
            }
            const fills = isPlainObject(body[String(rule.fill_ins_path || 'fill_ins')])
                ? body[String(rule.fill_ins_path || 'fill_ins')] : {};
            const steps = readPath(instance || {}, String(rule.steps_from || '').replace(/^instance\./, ''));
            if (Array.isArray(steps)) {
                steps.forEach((step) => {
                    if (fills[step.step_id] === undefined || String(fills[step.step_id]) === '') {
                        missing.push(missingEntry('fill_' + String(step.step_id), ruleMissing.fill_in, 'empty', { slot: step.prompt_lv }));
                    }
                });
            }
            if (!body[String(rule.conserved_path || 'conserved')]) {
                missing.push(missingEntry('conserved', ruleMissing.conserved, 'empty'));
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'graph') {
            const variants = isPlainObject(rule.variant_rules) ? rule.variant_rules : {};
            const declaredVariant = body.variant === undefined ? (contract.payload_variant) : body.variant;
            const variantRule = variants[String(declaredVariant)] || null;
            if (!variantRule) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Grafika pabeigtības noteikums nepazīst variantu "' + String(declaredVariant) + '".', {
                    type_id: contract && contract.id, field_id: 'variant'
                });
            }
            if (variantRule.mode === 'record') {
                const points = body.draw_payload && Array.isArray(body.draw_payload.points)
                    ? body.draw_payload.points : [];
                const declared = readPath(instance || {}, String(variantRule.declared_points_from || '').replace(/^instance\./, ''));
                const min = Array.isArray(declared) ? declared.length : 2;
                if (!body[String(variantRule.record_path || 'record')]) {
                    missing.push(missingEntry('record', variantRule.missing.record, 'empty'));
                }
                if (points.length < min) {
                    missing.push(missingEntry('draw_payload', variantRule.missing.point_count, 'points_below_minimum', { count: points.length, min_points: min }));
                }
                return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                    errors: [], source: 'component_fallback' };
            }
            const read = isPlainObject(body[String(variantRule.read_path || 'read')])
                ? body[String(variantRule.read_path || 'read')] : {};
            const axes = Array.isArray(variantRule.axes) ? variantRule.axes : ['x', 'y'];
            axes.forEach((axis) => {
                if (read[axis] === undefined || String(read[axis]) === '') {
                    missing.push(missingEntry('read_' + axis, variantRule.missing.axis, 'empty', { axis: axis }));
                }
            });
            const bindingField = String(variantRule.binding_field || 'figure_binding');
            if (read[bindingField] === undefined || String(read[bindingField]) === '') {
                missing.push(missingEntry(bindingField, variantRule.missing.binding, 'empty'));
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        if (model === 'pair_map') {
            const map = isPlainObject(body[String(rule.map_path || 'pair_map')])
                ? body[String(rule.map_path || 'pair_map')] : {};
            const steps = readPath(instance || {}, String(rule.steps_from || '').replace(/^instance\./, ''));
            if (Array.isArray(steps)) {
                steps.forEach((step) => {
                    if (map[step.step_id] === undefined || String(map[step.step_id]) === '') {
                        missing.push(missingEntry('pair_' + String(step.step_id), ruleMissing.step, 'empty', { slot: step.prompt_lv }));
                    }
                });
            }
            const parts = readPath(instance || {}, String(rule.structure_parts_from || '').replace(/^instance\./, ''));
            if (Array.isArray(parts)) {
                const placements = body.structure && Array.isArray(body.structure.placements)
                    ? body.structure.placements : [];
                parts.forEach((part) => {
                    const placed = placements.filter((entry) => entry.part_id === part.part_id)[0];
                    if (!placed) {
                        missing.push(missingEntry('place_' + String(part.part_id), ruleMissing.structure_part, 'unplaced', { slot: part.text_lv }));
                    }
                });
            }
            return { status: missing.length ? 'incomplete' : 'complete', missing: missing,
                errors: [], source: 'component_fallback' };
        }
        fail('E_INPUTS_CONTRACT_VIOLATION', 'Nezināms completion_rule.model "' + String(model) + '".', {
            type_id: contract && contract.id, field_id: null
        });
    }
    /* ----------------------------------------------------------- compose */
    function compose(parts, terms) {
        if (!Array.isArray(parts) || !parts.length) {
            fail('E_INPUTS_CONTRACT_VIOLATION', 'Apvienotajai atbildei nav nevienas daļas.', {
                type_id: 'composed', field_id: 'parts'
            });
        }
        const index = termsIndex(terms);
        const partIds = [];
        const payload = {};
        const missing = [];
        const described = [];
        const liveParts = [];
        parts.forEach((part, position) => {
            if (!isPlainObject(part) || typeof part.part_id !== 'string' || !part.part_id) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Apvienotās atbildes daļai ' + position + ' trūkst part_id.', {
                    type_id: 'composed', field_id: 'parts'
                });
            }
            if (partIds.indexOf(part.part_id) !== -1) {
                fail('E_INPUTS_CONTRACT_VIOLATION', 'Apvienotās atbildes daļas id "' + part.part_id + '" atkārtojas.', {
                    type_id: 'composed', field_id: part.part_id
                });
            }
            partIds.push(part.part_id);
            payload[String(position)] = part.payload === undefined ? null : part.payload;
            const labelKey = typeof part.label_key === 'string' ? part.label_key : null;
            const labelText = labelKey ? resolveTerm(index, labelKey, {}, {
                type_id: 'composed', field_id: part.part_id
            }) : '';
            const verdict = completionOf(part.contract, part.payload, part.instance);
            if (verdict.status !== 'complete') {
                verdict.missing.forEach((entry) => {
                    missing.push({
                        part_id: part.part_id,
                        part_index: position,
                        type_id: part.type_id === undefined ? null : part.type_id,
                        field_id: entry.field_id === undefined ? null : entry.field_id,
                        name: entry.name === undefined ? null : entry.name,
                        reason: entry.reason === undefined ? 'incomplete' : entry.reason,
                        label_key: entry.label_key === undefined ? null : entry.label_key
                    });
                });
                liveParts.push(labelText + ': ' + resolveTerm(index, 'input.state.incomplete', {}, { type_id: 'composed', field_id: part.part_id }));
            }
            described.push({
                part_id: part.part_id,
                part_index: position,
                type_id: part.type_id === undefined ? null : part.type_id,
                renderer_key: part.contract && part.contract.renderer_key
                    ? part.contract.renderer_key : null,
                label_key: labelKey,
                label_text_lv: labelText,
                completion: { status: verdict.status, missing: verdict.missing, source: verdict.source }
            });
        });
        const status = missing.length ? 'incomplete' : 'complete';
        /* The term bank has no "composed response" phrase; the group's name is
         * the mechanical join of the part names the registry declares, wrapped in
         * the shipped group label. No prose is invented. */
        const partNames = parts.map((part) => {
            const key = part.contract && typeof part.contract.name_key === 'string'
                ? part.contract.name_key : null;
            return key ? resolveTerm(index, key, {}, { type_id: 'composed', field_id: part.part_id }) : '';
        }).filter((name) => name !== '');
        return {
            api_version: API_VERSION,
            role: 'group',
            labelledby: 'inputs-composed-label',
            describedby: 'inputs-composed-help',
            label_text_lv: resolveTerm(index, 'input.group.label', {
                type: partNames.join(' · ')
            }, { type_id: 'composed', field_id: 'parts' }),
            part_names_lv: partNames,
            parts: described,
            part_ids: partIds,
            payload: payload,
            verdict: { status: status, missing: missing, errors: [] },
            live: [{
                    id: 'inputs-composed-live',
                    politeness: 'polite',
                    text: status === 'complete'
                        ? resolveTerm(index, 'input.state.complete', {}, { type_id: 'composed', field_id: null })
                        : liveParts.join(' ')
                }],
            ordering: 'part_index'
        };
    }
    function renderComposed(part, terms) {
        return render(part.type_id, part.contract, part.instance, part.payload, terms, part.context);
    }
    /* -------------------------------------------------------------- api */
    const api = {
        api_version: API_VERSION,
        TYPE_IDS: TYPE_IDS.slice(),
        RENDERER_KEYS: clone(RENDERER_KEYS),
        CONTROLS: clone(CONTROLS),
        InputsError: InputsError,
        render: render,
        renderComposed: renderComposed,
        keyboardContracts: keyboardContracts,
        initialState: initialState,
        applyKey: applyKey,
        pointerEvent: pointerEvent,
        cancel: cancel,
        payloadOf: payloadOf,
        committed: committed,
        compose: compose,
        completionOf: completionOf,
        termsIndex: termsIndex,
        parseRaw: parseRaw,
        formatRaw: formatRaw,
        quantize: quantize,
        planLeaves: planLeaves
    };
    root.SimInputsComponents = api;
    if (typeof module !== 'undefined' && module.exports) {
        module.exports = api;
    }
})(typeof globalThis !== 'undefined' ? globalThis : this);
