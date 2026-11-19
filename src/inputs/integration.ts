/* N22 — the response-input session integration module.
 *
 * Ownership: N22-C. This module is the join between the eighteen response
 * components (SimInputsComponents) and the exam session machine
 * (SimSession.ExamSession). It owns three things and nothing else:
 *
 *   1. the payload builder — one frozen vocabulary per type id, turning a
 *      component's emitted capture into the session payload the machine
 *      accepts. Raw strings pass through untouched; the builder never parses,
 *      rounds, re-orders or translates a value, because normalisation belongs
 *      to grading (docs/EXAM_SHELL_FORMAT.md §1.5).
 *   2. the write path — every answer goes through
 *      session.dispatch('answer', {slot_id, payload}); the module never reaches
 *      the answer map, and it re-reads the stored payload to prove the machine
 *      kept it byte for byte.
 *   3. the two completion overlays — the navigator map cells and the review
 *      warning list — which delegate the completion verdict to
 *      SimInputsRegistry.completion and never compute one of their own.
 *
 * The composed-response driver (B.1.3's consumer side) stores one ordered-map
 * payload for a multi-part instance, and the Q03 manual-rubric path is a
 * first-class "pending, never scored" record.
 *
 * The vocabularies below are the frozen per-type payload table of
 * data/exam_policy.json (session_contract.payload_contracts + named_variants)
 * and data/question_schema.json (payload_class). The registry (N22-A)
 * documents the same table; when a contract is passed in, the builder checks
 * that the two agree and refuses a mismatch loudly (E_INPUTS_CONTRACT_MISMATCH)
 * rather than drifting silently.
 *
 * No DOM, no island reading, no network: everything the module needs is passed
 * in. Compiled to src/compiled/inputs/integration.js by tools/compile_n21_ts.py.
 */
(function (this: void, root: any): void {
  'use strict';

  /* ------------------------------------------------------------- vocabulary */

  interface PayloadSpec {
    kind: string;
    variant: string | null;
    /** Capture keys that must be present (at least one of them). */
    core: string[];
    /** Capture keys copied verbatim into the payload when present. */
    carries: string[];
  }

  /**
   * The frozen per-type table. `Q11` and `Q18` carry an alternative shape:
   * Q18 is `option_select` per the N04 schema, but the graph class declares a
   * `plot_state` variant (exam_policy named_variants.Q18_plot_state), which is
   * used only when the capture actually carries a plot state.
   */
  const VOCABULARY: Record<string, PayloadSpec> = {
    Q01: { kind: 'numeric', variant: null, core: ['fields'], carries: ['fields'] },
    Q02: { kind: 'numeric', variant: null, core: ['fields'], carries: ['fields'] },
    Q03: { kind: 'method', variant: 'Q03_template', core: ['choice'], carries: ['choice', 'fill_ins', 'conserved'] },
    Q04: { kind: 'method', variant: 'Q04_vector', core: ['vector'], carries: ['vector'] },
    Q05: { kind: 'method', variant: 'Q05_rows', core: ['rows'], carries: ['rows'] },
    Q06: { kind: 'matching', variant: null, core: ['pairs'], carries: ['pairs'] },
    Q07: { kind: 'option_select', variant: null, core: ['selected'], carries: ['selected', 'justification'] },
    Q08: { kind: 'ordering', variant: null, core: ['order'], carries: ['order', 'explanation'] },
    Q09: { kind: 'numeric', variant: null, core: ['fields'], carries: ['fields'] },
    Q10: { kind: 'numeric', variant: null, core: ['fields'], carries: ['fields'] },
    Q11: { kind: 'graph', variant: 'Q11_record', core: ['record'], carries: ['record', 'draw_payload'] },
    Q12: { kind: 'graph', variant: 'Q12_read', core: ['read'], carries: ['read'] },
    Q13: {
      kind: 'method',
      variant: 'Q13_vector',
      core: ['vector'],
      carries: ['vector', 'located', 'replacement', 'reason']
    },
    Q14: { kind: 'option_select', variant: null, core: ['selected'], carries: ['selected', 'justification'] },
    Q15: { kind: 'method', variant: 'Q15_text', core: ['text'], carries: ['text'] },
    Q16: { kind: 'method', variant: 'Q16_text', core: ['text'], carries: ['text'] },
    Q17: { kind: 'method', variant: 'Q17_pairs', core: ['pair_map'], carries: ['pair_map', 'structure'] },
    Q18: { kind: 'option_select', variant: null, core: ['selected'], carries: ['selected', 'justification'] }
  };

  const PLOT_STATE_SPEC: PayloadSpec = {
    kind: 'graph',
    variant: 'Q18_plot_state',
    core: ['plot_state'],
    carries: ['plot_state']
  };

  /** The capture key whose value becomes `payload.values` for numeric types. */
  const FIELD_CAPTURE_KEYS = ['fields', 'values'];

  /**
   * The declared type of every ride-along, taken from the registry's field
   * table (`value_type`): the builder checks the shape so a component cannot
   * smuggle a parsed value into a slot the contract declares raw.
   */
  const CARRY_KINDS: Record<string, string> = {
    text: 'raw_string',
    choice: 'raw_string',
    conserved: 'raw_string',
    located: 'raw_string',
    replacement: 'raw_string',
    reason: 'raw_string',
    justification: 'raw_string',
    explanation: 'raw_string',
    fill_ins: 'raw_string_map',
    rows: 'raw_string_map',
    pair_map: 'raw_string_map',
    record: 'object',
    draw_payload: 'object',
    plot_state: 'object',
    structure: 'object',
    read: 'read',
    pairs: 'pairs',
    selected: 'string_list',
    order: 'string_list',
    vector: 'json_list'
  };

  /* ----------------------------------------------------------------- errors */

  /**
   * The single error type this module raises. `code` is a stable id; the
   * messages are Latvian because they reach the learner-facing surface.
   */
  class InputsError extends Error {
    public readonly code: string;
    public readonly details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super(message);
      this.name = 'InputsError';
      this.code = code;
      this.details = details || {};
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, InputsError);
      } else {
        this.stack = new Error(message).stack;
      }
    }
  }

  /* ---------------------------------------------------------------- helpers */

  function isPlainObject(value: unknown): boolean {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
  }

  function has(source: Record<string, unknown>, key: string): boolean {
    return Object.prototype.hasOwnProperty.call(source, key) && source[key] !== undefined && source[key] !== null;
  }

  function copyJson<T>(value: T): T {
    return JSON.parse(JSON.stringify(value)) as T;
  }

  /**
   * A deterministic projection of any JSON value: sorted keys, no whitespace.
   * The same projection feeds the content digest, so two payloads digest equal
   * exactly when their content is equal.
   */
  function canonical(value: unknown): string {
    if (value === null || value === undefined) { return 'null'; }
    if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
    if (typeof value === 'number') { return String(value); }
    if (typeof value === 'string') { return JSON.stringify(value); }
    if (Array.isArray(value)) {
      return '[' + value.map(function (item: unknown): string { return canonical(item); }).join(',') + ']';
    }
    if (typeof value === 'object') {
      const record = value as Record<string, unknown>;
      const keys = Object.keys(record).sort();
      return '{' + keys.map(function (key: string): string {
        return JSON.stringify(key) + ':' + canonical(record[key]);
      }).join(',') + '}';
    }
    return 'null';
  }

  /**
   * A 64-bit content identity in 16 lowercase hex characters: two independent
   * FNV-1a 32-bit lanes over the UTF-16 code units of the canonical
   * projection. This is an identity token for the trace and the parity table,
   * not a cryptographic seal — the engines keep their own SHA-256 digests.
   */
  function fnv1a32(text: string, seed: number): number {
    let hash = seed >>> 0;
    for (let index = 0; index < text.length; index += 1) {
      const code = text.charCodeAt(index);
      hash ^= code & 0xff;
      hash = Math.imul(hash, 0x01000193) >>> 0;
      hash ^= (code >>> 8) & 0xff;
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash >>> 0;
  }

  function pad8(value: number): string {
    const hex = (value >>> 0).toString(16);
    return '00000000'.slice(hex.length) + hex;
  }

  function contentDigest(value: unknown): string {
    const text = canonical(value);
    return pad8(fnv1a32(text, 0x811c9dc5)) + pad8(fnv1a32(text, 0x9e3779b9));
  }

  /** Reads a raw string, accepting the component's own `{value: "…"}` wrapper. */
  function asRawString(value: unknown, where: string): string {
    if (typeof value === 'string') { return value; }
    if (isPlainObject(value) && typeof (value as Record<string, unknown>).value === 'string') {
      return (value as Record<string, string>).value;
    }
    throw new InputsError(
      'E_INPUTS_CAPTURE_TYPE',
      'Ievades laukam "' + where + '" jābūt neapstrādātai virknei.',
      { where: where, received: typeof value }
    );
  }

  function asStringList(value: unknown, where: string): string[] {
    if (!Array.isArray(value)) {
      throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Ievades laukam "' + where + '" jābūt sarakstam.', { where: where });
    }
    const out: string[] = [];
    for (let index = 0; index < value.length; index += 1) {
      const item = value[index];
      if (typeof item !== 'string') {
        throw new InputsError(
          'E_INPUTS_CAPTURE_TYPE',
          'Ievades saraksta "' + where + '" elements ' + String(index) + ' nav virkne.',
          { where: where, index: index }
        );
      }
      out.push(item);
    }
    return out;
  }

  function asPairList(value: unknown): Array<Record<string, string>> {
    if (!Array.isArray(value)) {
      throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Pāru laukam jābūt sarakstam.', { where: 'pairs' });
    }
    const out: Array<Record<string, string>> = [];
    for (let index = 0; index < value.length; index += 1) {
      const pair = value[index];
      if (!isPlainObject(pair)) {
        throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Pāris ' + String(index) + ' nav objekts.', { index: index });
      }
      const record = pair as Record<string, unknown>;
      const left = record.left_id;
      const right = record.right_id;
      if (typeof left !== 'string' || typeof right !== 'string') {
        throw new InputsError(
          'E_INPUTS_CAPTURE_TYPE',
          'Pārim ' + String(index) + ' jābūt left_id un right_id virknēm (N19 forma).',
          { index: index }
        );
      }
      out.push({ left_id: left, right_id: right });
    }
    return out;
  }

  function asRead(value: unknown): Record<string, string> {
    if (!isPlainObject(value)) {
      throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Nolasījuma laukam jābūt objektam.', { where: 'read' });
    }
    const record = value as Record<string, unknown>;
    const out: Record<string, string> = {};
    if (has(record, 'x')) { out.x = asRawString(record.x, 'read.x'); }
    if (has(record, 'y')) { out.y = asRawString(record.y, 'read.y'); }
    if (has(record, 'figure_binding')) { out.figure_binding = asRawString(record.figure_binding, 'read.figure_binding'); }
    if (!has(out, 'x') && !has(out, 'y')) {
      throw new InputsError('E_INPUTS_CAPTURE_INVALID', 'Nolasījumam jābūt vismaz x vai y vērtībai.', {});
    }
    return out;
  }

  function asRawStringMap(value: unknown, where: string): Record<string, string> {
    if (!isPlainObject(value)) {
      throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Ievades laukam "' + where + '" jābūt objektam.', { where: where });
    }
    const record = value as Record<string, unknown>;
    const out: Record<string, string> = {};
    const keys = Object.keys(record);
    for (let index = 0; index < keys.length; index += 1) {
      const key = keys[index];
      out[key] = asRawString(record[key], where + '.' + key);
    }
    return out;
  }

  /* --------------------------------------------------------- contract check */

  function declaredKind(contract: unknown): string | null {
    if (!isPlainObject(contract)) { return null; }
    const record = contract as Record<string, unknown>;
    if (typeof record.kind === 'string') { return record.kind; }
    if (typeof record.payload_kind === 'string') { return record.payload_kind; }
    if (isPlainObject(record.payload) && typeof (record.payload as Record<string, unknown>).kind === 'string') {
      return (record.payload as Record<string, string>).kind;
    }
    return null;
  }

  function declaredVariant(contract: unknown): string | null {
    if (!isPlainObject(contract)) { return null; }
    const record = contract as Record<string, unknown>;
    if (typeof record.variant === 'string') { return record.variant; }
    if (typeof record.payload_variant === 'string') { return record.payload_variant; }
    if (isPlainObject(record.payload) && typeof (record.payload as Record<string, unknown>).variant === 'string') {
      return (record.payload as Record<string, string>).variant;
    }
    return null;
  }

  /**
   * The registry documents the same vocabulary. A contract that disagrees is a
   * contract break, not something to paper over: the builder refuses it.
   */
  function assertContractAgreement(typeId: string, contract: unknown, spec: PayloadSpec, allowedKinds: string[]): void {
    if (!isPlainObject(contract)) { return; }
    const declaredType = (contract as Record<string, unknown>).type_id;
    if (typeof declaredType === 'string' && declaredType !== typeId) {
      throw new InputsError(
        'E_INPUTS_CONTRACT_MISMATCH',
        'Reģistra līgums attiecas uz tipu ' + declaredType + ', nevis ' + typeId + '.',
        { type_id: typeId, contract_type_id: declaredType }
      );
    }
    const kind = declaredKind(contract);
    if (kind !== null && allowedKinds.indexOf(kind) === -1) {
      throw new InputsError(
        'E_INPUTS_CONTRACT_MISMATCH',
        'Reģistra līgums tipam ' + typeId + ' paredz datu veidu ' + kind + ', bet iesaldētā tabula — ' +
          allowedKinds.join(' vai ') + '.',
        { type_id: typeId, contract_kind: kind, vocabulary_kinds: allowedKinds }
      );
    }
    const variant = declaredVariant(contract);
    if (variant !== null && spec.variant !== null && variant !== spec.variant) {
      throw new InputsError(
        'E_INPUTS_CONTRACT_MISMATCH',
        'Reģistra līgums tipam ' + typeId + ' paredz variantu ' + variant + ', bet iesaldētā tabula — ' +
          spec.variant + '.',
        { type_id: typeId, contract_variant: variant, vocabulary_variant: spec.variant }
      );
    }
  }

  /* ----------------------------------------------------------- the builder */

  function specFor(typeId: string, capture: Record<string, unknown>): PayloadSpec {
    if (!Object.prototype.hasOwnProperty.call(VOCABULARY, typeId)) {
      throw new InputsError(
        'E_INPUTS_UNKNOWN_TYPE',
        'Nezināms atbildes tips "' + typeId + '": komponents netiek izvēlēts pēc noklusējuma.',
        { type_id: typeId, known: Object.keys(VOCABULARY).sort() }
      );
    }
    const base = VOCABULARY[typeId];
    if (typeId === 'Q18' && has(capture, 'plot_state')) { return PLOT_STATE_SPEC; }
    return base;
  }

  function readFieldMap(capture: Record<string, unknown>): Record<string, string> {
    let source: unknown = null;
    for (let index = 0; index < FIELD_CAPTURE_KEYS.length; index += 1) {
      const key = FIELD_CAPTURE_KEYS[index];
      if (has(capture, key)) { source = capture[key]; break; }
    }
    if (!isPlainObject(source)) {
      throw new InputsError(
        'E_INPUTS_CAPTURE_INVALID',
        'Skaitliskajai atbildei jānāk ar lauku karti (fields).',
        { expected: FIELD_CAPTURE_KEYS }
      );
    }
    const record = source as Record<string, unknown>;
    const out: Record<string, string> = {};
    const keys = Object.keys(record);
    for (let index = 0; index < keys.length; index += 1) {
      const key = keys[index];
      out[key] = asRawString(record[key], 'fields.' + key);
    }
    return out;
  }

  /**
   * A component may hand over its capture (what the learner did) or an
   * already-prepared payload in the frozen vocabulary (N22-B's `payloadOf`
   * returns exactly that). A prepared payload is accepted only when its kind
   * and variant match the frozen table — the passthrough is a contract check,
   * not a bypass.
   */
  function preparedPayload(source: Record<string, unknown>, spec: PayloadSpec, typeId: string): Record<string, unknown> | null {
    if (typeof source.kind !== 'string') { return null; }
    if (source.kind !== spec.kind) {
      throw new InputsError(
        'E_INPUTS_CONTRACT_MISMATCH',
        'Sagatavotais datums tipam ' + typeId + ' ir veids ' + source.kind + ', bet iesaldētā tabula — ' + spec.kind + '.',
        { type_id: typeId, payload_kind: source.kind, vocabulary_kind: spec.kind }
      );
    }
    const variant = source.variant === undefined ? null : source.variant;
    if (variant !== spec.variant) {
      throw new InputsError(
        'E_INPUTS_CONTRACT_MISMATCH',
        'Sagatavotais datums tipam ' + typeId + ' ir variants ' + String(variant) + ', bet iesaldētā tabula — ' +
          String(spec.variant) + '.',
        { type_id: typeId, payload_variant: variant, vocabulary_variant: spec.variant }
      );
    }
    return copyJson(source);
  }

  /**
   * Turns a component capture into the session payload. Structural honesty:
   * the raw strings are copied, never interpreted, and an absent ride-along is
   * simply absent — never defaulted, because a default would invent an answer.
   */
  function buildPayload(typeId: string, contract: unknown, instance: unknown, capture: unknown): Record<string, unknown> {
    void instance;
    if (typeof typeId !== 'string' || typeId === '') {
      throw new InputsError('E_INPUTS_UNKNOWN_TYPE', 'Atbildes tips nav norādīts.', { type_id: String(typeId) });
    }
    if (!isPlainObject(capture)) {
      throw new InputsError('E_INPUTS_CAPTURE_INVALID', 'Komponenta ievades kopums nav objekts.', { type_id: typeId });
    }
    const source = capture as Record<string, unknown>;
    const spec = specFor(typeId, source);
    assertContractAgreement(typeId, contract, spec, spec === PLOT_STATE_SPEC ? ['option_select', 'graph'] : [spec.kind]);
    const prepared = preparedPayload(source, spec, typeId);
    if (prepared !== null) { return prepared; }

    let coreSeen = false;
    for (let index = 0; index < spec.core.length; index += 1) {
      if (has(source, spec.core[index])) { coreSeen = true; break; }
    }
    if (!coreSeen) {
      throw new InputsError(
        'E_INPUTS_CAPTURE_INVALID',
        'Atbildei tipam ' + typeId + ' jābūt vismaz vienam no laukiem: ' + spec.core.join(', ') + '.',
        { type_id: typeId, expected: spec.core }
      );
    }

    const payload: Record<string, unknown> = { kind: spec.kind };
    if (spec.variant !== null) { payload.variant = spec.variant; }

    if (spec.kind === 'numeric') {
      payload.values = readFieldMap(source);
      return payload;
    }

    for (let index = 0; index < spec.carries.length; index += 1) {
      const key = spec.carries[index];
      if (!has(source, key)) { continue; }
      const value = source[key];
      const carryKind = Object.prototype.hasOwnProperty.call(CARRY_KINDS, key) ? CARRY_KINDS[key] : 'object';
      if (carryKind === 'raw_string') {
        payload[key] = asRawString(value, key);
      } else if (carryKind === 'raw_string_map') {
        payload[key] = asRawStringMap(value, key);
      } else if (carryKind === 'string_list') {
        payload[key] = asStringList(value, key);
      } else if (carryKind === 'pairs') {
        payload.pairs = asPairList(value);
      } else if (carryKind === 'read') {
        payload.read = asRead(value);
      } else if (carryKind === 'json_list') {
        /* A coefficient vector may hold numbers: the value is copied verbatim,
         * never stringified, because a coercion here would be a silent
         * adapter. */
        if (!Array.isArray(value)) {
          throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Ievades laukam "' + key + '" jābūt sarakstam.', { where: key });
        }
        payload[key] = copyJson(value);
      } else {
        if (!isPlainObject(value)) {
          throw new InputsError('E_INPUTS_CAPTURE_TYPE', 'Ievades laukam "' + key + '" jābūt objektam.', { where: key });
        }
        payload[key] = copyJson(value);
      }
    }
    return payload;
  }

  /* -------------------------------------------------------- the write path */

  interface Dispatchable {
    dispatch?: unknown;
    getAnswer?: unknown;
    getAnswers?: unknown;
  }

  function assertSession(session: unknown): Dispatchable {
    if (!session || typeof session !== 'object') {
      throw new InputsError('E_INPUTS_SESSION_INVALID', 'Sesijas mašīna nav nodota.', {});
    }
    const machine = session as Dispatchable;
    if (typeof machine.dispatch !== 'function') {
      throw new InputsError('E_INPUTS_SESSION_INVALID', 'Sesijas mašīnai nav dispatch metodes.', {});
    }
    return machine;
  }

  /**
   * The only write path. The answer goes through the machine's own `answer`
   * event, and the stored payload is read back and digested, so a builder
   * that quietly rewrote a value could not pass unnoticed.
   */
  function answer(
    session: unknown, slotId: string, typeId: string, contract: unknown, instance: unknown, capture: unknown
  ): Record<string, unknown> {
    const machine = assertSession(session);
    const payload = buildPayload(typeId, contract, instance, capture);
    (machine.dispatch as (event: string, body: Record<string, unknown>) => unknown).call(session, 'answer', {
      slot_id: slotId,
      payload: payload
    });
    let stored: Record<string, unknown> | null = null;
    if (typeof machine.getAnswer === 'function') {
      const found = (machine.getAnswer as (id: string) => Record<string, unknown> | null).call(session, slotId);
      if (found && isPlainObject(found.payload)) { stored = found.payload as Record<string, unknown>; }
    }
    const digest = contentDigest(payload);
    if (stored !== null && contentDigest(stored) !== digest) {
      throw new InputsError(
        'E_INPUTS_STORE_MISMATCH',
        'Sesijas mašīna saglabāja citādu datumu nekā komponents nodeva.',
        { slot_id: slotId, type_id: typeId, digest: digest, stored_digest: contentDigest(stored) }
      );
    }
    return {
      slot_id: slotId,
      type_id: typeId,
      kind: payload.kind,
      variant: payload.variant === undefined ? null : payload.variant,
      payload: payload,
      payload_digest: digest
    };
  }

  /**
   * The only-writer guard: the integration offers no setter, the machine's
   * accessors hand out deep copies, and a write exists only as a dispatch.
   */
  function assertOnlyWriter(session: unknown): Record<string, unknown> {
    const machine = assertSession(session);
    const record = session as Record<string, unknown>;
    const setterNames = ['setAnswer', 'setAnswers', 'writeAnswer', 'setAnswerMap'];
    const setters = setterNames.filter(function (name: string): boolean {
      return typeof record[name] === 'function';
    });
    let deepCopies = false;
    if (typeof machine.getAnswers === 'function' && typeof machine.getAnswer === 'function') {
      const before = contentDigest((machine.getAnswers as () => unknown).call(session));
      const copy = (machine.getAnswers as () => Array<Record<string, unknown>>).call(session);
      if (copy.length > 0 && isPlainObject(copy[0]) && isPlainObject(copy[0].payload)) {
        (copy[0].payload as Record<string, unknown>).n22_mutation_probe = true;
        const after = contentDigest((machine.getAnswers as () => unknown).call(session));
        deepCopies = before === after;
      } else {
        deepCopies = true;
      }
    }
    return {
      writer: 'dispatch',
      checks: { has_dispatch: true, public_setters: setters, copies_are_deep: deepCopies },
      ok: setters.length === 0 && deepCopies
    };
  }

  /* --------------------------------------------------------- completion I/O */

  interface CompletionVerdict {
    status: string;
    missing?: Array<Record<string, unknown>>;
    errors?: Array<Record<string, unknown>>;
  }

  interface CompletionBinding {
    index: number;
    shape: string;
  }

  let completionBinding: CompletionBinding | null = null;

  function isVerdict(value: unknown): boolean {
    if (!isPlainObject(value)) { return false; }
    const status = (value as Record<string, unknown>).status;
    return typeof status === 'string' && ['complete', 'incomplete', 'invalid'].indexOf(status) !== -1;
  }

  function completionCandidates(payload: unknown, typeId: string, contract: unknown, instance: unknown): Array<{ shape: string; args: unknown[] }> {
    return [
      /* The documented signature of N22-A's registry. */
      { shape: '(type_id, contract, instance, payload)', args: [typeId, contract, instance, payload] },
      { shape: '(payload, type_id, contract, instance)', args: [payload, typeId, contract, instance] },
      { shape: '(type_id, contract, payload, instance)', args: [typeId, contract, payload, instance] },
      { shape: '(payload, type_id)', args: [payload, typeId] },
      { shape: '(answer, type_id, contract, instance)', args: [{ slot_id: null, payload: payload }, typeId, contract, instance] },
      { shape: '({type_id, contract, instance, payload})', args: [{ type_id: typeId, contract: contract, instance: instance, payload: payload }] }
    ];
  }

  /**
   * The completion verdict belongs to SimInputsRegistry (N22-A). This module
   * owns the *call*, never the model: the candidate shapes below are the
   * documented signatures the sibling may expose, and the first shape that
   * returns a verdict-shaped object is cached for the rest of the session.
   * Every payload passed is the raw stored payload — no adapter, no rewrite.
   */
  function resolveCompletion(payload: unknown, typeId: string, contract: unknown, instance: unknown): CompletionVerdict {
    const registry = root.SimInputsRegistry;
    if (!registry || registry.stub === true || typeof registry.completion !== 'function') {
      throw new InputsError(
        'E_INPUTS_INCOMPLETE',
        'Pabeigtības modelis nav pieejams: trūkst SimInputsRegistry.completion.',
        { missing: ['SimInputsRegistry.completion'] }
      );
    }
    const candidates = completionCandidates(payload, typeId, contract, instance);
    const order: number[] = [];
    if (completionBinding !== null) { order.push(completionBinding.index); }
    for (let index = 0; index < candidates.length; index += 1) {
      if (order.indexOf(index) === -1) { order.push(index); }
    }
    let lastError: unknown = null;
    for (let step = 0; step < order.length; step += 1) {
      const candidate = candidates[order[step]];
      try {
        const verdict = registry.completion.apply(registry, candidate.args);
        if (isVerdict(verdict)) {
          completionBinding = { index: order[step], shape: candidate.shape };
          return verdict as CompletionVerdict;
        }
      } catch (error) {
        lastError = error;
      }
    }
    throw new InputsError(
      'E_INPUTS_COMPLETION_BINDING',
      'SimInputsRegistry.completion neatgriež pabeigtības spriedumu nevienā no deklarētajām formām.',
      {
        tried: candidates.map(function (candidate: { shape: string }): string { return candidate.shape; }),
        last_error: lastError === null ? null : String((lastError as Error).message || lastError)
      }
    );
  }

  function completionForSlot(answerOrPayload: unknown, typeId: string, contract: unknown, instance: unknown): CompletionVerdict {
    const payload = isPlainObject(answerOrPayload) && isPlainObject((answerOrPayload as Record<string, unknown>).payload)
      ? (answerOrPayload as Record<string, unknown>).payload
      : answerOrPayload;
    return resolveCompletion(payload, typeId, contract, instance);
  }

  function normaliseAnswers(answers: unknown): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    if (Array.isArray(answers)) {
      for (let index = 0; index < answers.length; index += 1) {
        const entry = answers[index];
        if (isPlainObject(entry) && typeof (entry as Record<string, unknown>).slot_id === 'string') {
          out[(entry as Record<string, string>).slot_id] = entry;
        }
      }
      return out;
    }
    if (isPlainObject(answers)) {
      const record = answers as Record<string, unknown>;
      const keys = Object.keys(record);
      for (let index = 0; index < keys.length; index += 1) { out[keys[index]] = record[keys[index]]; }
    }
    return out;
  }

  interface SlotBinding {
    type_id: string;
    contract?: unknown;
    instance?: unknown;
  }

  function bindingFor(bindings: unknown, slotId: string): SlotBinding | null {
    if (Array.isArray(bindings)) {
      for (let index = 0; index < bindings.length; index += 1) {
        const entry = bindings[index];
        if (isPlainObject(entry) && (entry as Record<string, unknown>).slot_id === slotId) {
          return entry as unknown as SlotBinding;
        }
      }
      return null;
    }
    if (isPlainObject(bindings)) {
      const value = (bindings as Record<string, unknown>)[slotId];
      if (typeof value === 'string') { return { type_id: value }; }
      if (isPlainObject(value)) { return value as unknown as SlotBinding; }
    }
    return null;
  }

  /**
   * The navigator overlay: the N21 map cells plus the completion verdict. The
   * N21 `answered` flag keeps its frozen meaning (an answer exists); `complete`
   * is the refinement N22 adds, and an incomplete or invalid cell keeps its
   * missing list so the review surface can name it.
   */
  function completionMapState(mapState: unknown, answers: unknown, bindings: unknown): Record<string, unknown> {
    if (!isPlainObject(mapState) || !Array.isArray((mapState as Record<string, unknown>).cells)) {
      throw new InputsError('E_INPUTS_MAP_INVALID', 'Kartes stāvoklim jābūt ar šūnu sarakstu.', {});
    }
    const state = mapState as Record<string, unknown>;
    const rawCells = state.cells as Array<Record<string, unknown>>;
    const answerMap = normaliseAnswers(answers);
    const cells: Array<Record<string, unknown>> = [];
    const incompleteSlots: string[] = [];
    const invalidSlots: string[] = [];
    let complete = 0;
    for (let index = 0; index < rawCells.length; index += 1) {
      const cell = rawCells[index];
      const slotId = String(cell.slot_id);
      const stored = Object.prototype.hasOwnProperty.call(answerMap, slotId) ? answerMap[slotId] : null;
      const next: Record<string, unknown> = {};
      const keys = Object.keys(cell);
      for (let k = 0; k < keys.length; k += 1) { next[keys[k]] = cell[keys[k]]; }
      if (stored === null) {
        next.complete = false;
        next.completion_status = 'unanswered';
        next.missing = [];
        next.errors = [];
        cells.push(next);
        continue;
      }
      const binding = bindingFor(bindings, slotId);
      if (binding === null) {
        throw new InputsError(
          'E_INPUTS_BINDING_MISSING',
          'Atbildētajai vietai ' + slotId + ' nav piesaistīts atbildes tips.',
          { slot_id: slotId }
        );
      }
      const verdict = completionForSlot(stored, binding.type_id, binding.contract, binding.instance);
      next.complete = verdict.status === 'complete';
      next.completion_status = verdict.status;
      next.missing = Array.isArray(verdict.missing) ? copyJson(verdict.missing) : [];
      next.errors = Array.isArray(verdict.errors) ? copyJson(verdict.errors) : [];
      if (verdict.status === 'complete') { complete += 1; }
      if (verdict.status === 'incomplete') { incompleteSlots.push(slotId); }
      if (verdict.status === 'invalid') { invalidSlots.push(slotId); }
      cells.push(next);
    }
    const answeredCount = cells.filter(function (cell: Record<string, unknown>): boolean {
      return cell.answered === true;
    }).length;
    return {
      overlay: 'n22-completion',
      cells: cells,
      answered_count: answeredCount,
      complete_count: complete,
      incomplete_count: incompleteSlots.length,
      invalid_count: invalidSlots.length,
      unanswered_count: cells.length - answeredCount,
      incomplete_slot_ids: incompleteSlots,
      invalid_slot_ids: invalidSlots,
      current_slot_id: state.current_slot_id === undefined ? null : state.current_slot_id
    };
  }

  /**
   * The review overlay: the unanswered warning list, naming every slot that is
   * unanswered, incomplete or invalid, with the Latvian missing-field names the
   * completion model returned. The consumer renders it with role="alert".
   */
  function reviewMissingList(reviewState: unknown, answers: unknown, bindings: unknown): Record<string, unknown> {
    if (!isPlainObject(reviewState) || !Array.isArray((reviewState as Record<string, unknown>).rows)) {
      throw new InputsError('E_INPUTS_MAP_INVALID', 'Pārbaudes stāvoklim jābūt ar rindu sarakstu.', {});
    }
    const state = reviewState as Record<string, unknown>;
    const rows = state.rows as Array<Record<string, unknown>>;
    const asCells = rows.map(function (row: Record<string, unknown>): Record<string, unknown> {
      const cell: Record<string, unknown> = {};
      const keys = Object.keys(row);
      for (let k = 0; k < keys.length; k += 1) { cell[keys[k]] = row[keys[k]]; }
      cell.current = false;
      return cell;
    });
    const overlay = completionMapState({ cells: asCells, current_slot_id: null }, answers, bindings);
    const cells = overlay.cells as Array<Record<string, unknown>>;
    const unanswered: string[] = [];
    const entries: Array<Record<string, unknown>> = [];
    const names: string[] = [];
    for (let index = 0; index < cells.length; index += 1) {
      const cell = cells[index];
      const slotId = String(cell.slot_id);
      if (cell.completion_status === 'unanswered') { unanswered.push(slotId); continue; }
      if (cell.completion_status === 'complete') { continue; }
      const missing = (cell.missing || []) as Array<Record<string, unknown>>;
      const missingNames: string[] = [];
      for (let m = 0; m < missing.length; m += 1) {
        const name = missing[m].name;
        const fieldId = missing[m].field_id;
        if (typeof name === 'string' && name !== '') { missingNames.push(name); }
        else if (typeof fieldId === 'string' && fieldId !== '') { missingNames.push(fieldId); }
      }
      entries.push({
        slot_id: slotId,
        index: cell.index,
        type_id: (bindingFor(bindings, slotId) || { type_id: '' }).type_id,
        completion_status: cell.completion_status,
        missing: copyJson(missing),
        missing_names_lv: missingNames
      });
      for (let n = 0; n < missingNames.length; n += 1) {
        if (names.indexOf(missingNames[n]) === -1) { names.push(missingNames[n]); }
      }
    }
    const total = unanswered.length + entries.length;
    return {
      role: 'alert',
      overlay: 'n22-review',
      count: total,
      unanswered_count: unanswered.length,
      incomplete_count: entries.length,
      unanswered_slot_ids: unanswered,
      incomplete: entries,
      missing_names_lv: names,
      text_lv: total === 0
        ? 'Visas atbildes ir pabeigtas.'
        : 'Pirms iesniegšanas jāpabeidz ' + String(total) + ' uzdevumi'
          + (names.length === 0 ? '.' : ': ' + names.join('; ') + '.')
    };
  }

  /* ------------------------------------------------------ composed responses */

  interface ComposedPart {
    part_id: string;
    type_id: string;
    contract?: unknown;
    instance?: unknown;
    capture: unknown;
  }

  /**
   * B.1.3's consumer side: a composed instance's parts are stored as one
   * ordered-map payload, with a per-part completion verdict attached. The
   * machine still sees a single answer, so a half-complete composed response
   * stays one answer with a named missing part list — exactly what N23's
   * per-criterion grading consumes.
   */
  function composedDriver(session: unknown, slotId: string, parts: unknown): Record<string, unknown> {
    const machine = assertSession(session);
    if (!Array.isArray(parts) || parts.length === 0) {
      throw new InputsError('E_INPUTS_COMPOSED_INVALID', 'Saliktajai atbildei jābūt ar vismaz vienu daļu.', {});
    }
    const built: Array<Record<string, unknown>> = [];
    const partOrder: string[] = [];
    const incomplete: string[] = [];
    let invalid = false;
    for (let index = 0; index < parts.length; index += 1) {
      const part = parts[index] as ComposedPart;
      if (!isPlainObject(part) || typeof part.part_id !== 'string' || typeof part.type_id !== 'string') {
        throw new InputsError('E_INPUTS_COMPOSED_INVALID', 'Daļai ' + String(index) + ' jābūt ar part_id un type_id.', { index: index });
      }
      const payload = buildPayload(part.type_id, part.contract, part.instance, part.capture);
      const verdict = completionForSlot(payload, part.type_id, part.contract, part.instance);
      if (verdict.status !== 'complete') {
        incomplete.push(part.part_id);
        if (verdict.status === 'invalid') { invalid = true; }
      }
      partOrder.push(part.part_id);
      built.push({
        part_id: part.part_id,
        type_id: part.type_id,
        kind: payload.kind,
        variant: payload.variant === undefined ? null : payload.variant,
        payload: payload,
        completion: copyJson(verdict)
      });
    }
    const status = incomplete.length === 0 ? 'complete' : (invalid ? 'invalid' : 'incomplete');
    const payload: Record<string, unknown> = {
      kind: 'method',
      variant: 'composed',
      part_order: partOrder,
      parts: built.map(function (part: Record<string, unknown>): Record<string, unknown> {
        return {
          part_id: part.part_id,
          type_id: part.type_id,
          kind: part.kind,
          variant: part.variant,
          payload: part.payload
        };
      }),
      completion: { status: status, incomplete_part_ids: incomplete }
    };
    (machine.dispatch as (event: string, body: Record<string, unknown>) => unknown).call(session, 'answer', {
      slot_id: slotId,
      payload: payload
    });
    return {
      slot_id: slotId,
      status: status,
      payload: payload,
      payload_digest: contentDigest(payload),
      parts: built
    };
  }

  /* ------------------------------------------------------- the Q03 corner case */

  /**
   * Q03 is the manual-rubric corner case: the learner picks a restricted
   * template and types the fill-ins, and a human rubric grades it. The path is
   * pending — no verdict, no points, no signature — and it says so in its own
   * record rather than pretending to auto-score.
   */
  function q03PendingPath(payload: unknown): Record<string, unknown> {
    if (!isPlainObject(payload)) {
      throw new InputsError('E_INPUTS_CAPTURE_INVALID', 'Q03 ceļam nepieciešams sagatavotais datums.', {});
    }
    const record = payload as Record<string, unknown>;
    return {
      class: 'pending',
      engine: 'manual-rubric-pending',
      graded: false,
      verdict: null,
      points_awarded: 0,
      points_pending: null,
      payload_kind: record.kind === undefined ? null : record.kind,
      payload_variant: record.variant === undefined ? null : record.variant,
      payload_digest: contentDigest(payload),
      note_lv: 'Manuāli vērtējams (Q03): dzinējs nepiešķir punktus un nesniedz verdiktu; '
        + 'atbilde tiek saglabāta un nodota cilvēka vērtējumam.'
    };
  }

  /* ---------------------------------------------------------------- facade */

  const MODULE_API: Record<string, unknown> = {
    buildPayload: buildPayload,
    answer: answer,
    completionForSlot: completionForSlot,
    completionMapState: completionMapState,
    reviewMissingList: reviewMissingList,
    composedDriver: composedDriver,
    q03PendingPath: q03PendingPath,
    assertOnlyWriter: assertOnlyWriter,
    contentDigest: contentDigest,
    canonical: canonical
  };

  /**
   * The aggregate downstream tasks read: the registry, the components and this
   * module's functions in one place. A missing sibling is named, not glossed
   * over — an input layer without its registry or its components is not
   * "empty", it is incomplete.
   */
  function buildFacade(): Record<string, unknown> {
    const registry = root.SimInputsRegistry;
    const components = root.SimInputsComponents;
    const missing: string[] = [];
    if (!registry || registry.stub === true || typeof registry.completion !== 'function' || typeof registry.contractFor !== 'function') {
      missing.push('SimInputsRegistry');
    }
    if (!components || components.stub === true) { missing.push('SimInputsComponents'); }
    if (missing.length > 0) {
      throw new InputsError(
        'E_INPUTS_INCOMPLETE',
        'N22 ievades slānis nav pilnīgs: trūkst ' + missing.join(', ') + '.',
        { missing: missing }
      );
    }
    const facade: Record<string, unknown> = {
      registry: registry,
      components: components
    };
    const keys = Object.keys(MODULE_API);
    for (let index = 0; index < keys.length; index += 1) { facade[keys[index]] = MODULE_API[keys[index]]; }
    return facade;
  }

  let facadeCache: Record<string, unknown> | null = null;

  function facade(): Record<string, unknown> {
    if (facadeCache === null) { facadeCache = buildFacade(); }
    return facadeCache;
  }

  /* ----------------------------------------------------------------- export */

  const api = {
    InputsError: InputsError,
    MODULE_API: MODULE_API,
    VOCABULARY: VOCABULARY,
    isPlainObject: isPlainObject,
    has: has,
    copyJson: copyJson,
    canonical: canonical,
    contentDigest: contentDigest,
    asRawString: asRawString,
    asStringList: asStringList,
    asPairList: asPairList,
    asRawStringMap: asRawStringMap,
    asRead: asRead,
    declaredKind: declaredKind,
    declaredVariant: declaredVariant,
    assertContractAgreement: assertContractAgreement,
    specFor: specFor,
    readFieldMap: readFieldMap,
    preparedPayload: preparedPayload,
    buildPayload: buildPayload,
    assertSession: assertSession,
    answer: answer,
    assertOnlyWriter: assertOnlyWriter,
    isVerdict: isVerdict,
    completionCandidates: completionCandidates,
    resolveCompletion: resolveCompletion,
    completionForSlot: completionForSlot,
    normaliseAnswers: normaliseAnswers,
    bindingFor: bindingFor,
    completionMapState: completionMapState,
    reviewMissingList: reviewMissingList,
    composedDriver: composedDriver,
    q03PendingPath: q03PendingPath,
    buildFacade: buildFacade,
    facade: facade,
    vocabulary: function (): Record<string, PayloadSpec> { return copyJson(VOCABULARY); },
    completionBinding: function (): CompletionBinding | null { return completionBinding; }
  };

  root.SimInputsIntegration = api;

  /* `SimInputs` is built on first access, so this module can load before its
   * siblings exist (the artifact never inlines them); reading the aggregate is
   * the moment it must be complete, and it throws E_INPUTS_INCOMPLETE naming
   * whatever is missing. */
  Object.defineProperty(root, 'SimInputs', {
    configurable: true,
    enumerable: true,
    get: function (): Record<string, unknown> { return facade(); }
  });

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
