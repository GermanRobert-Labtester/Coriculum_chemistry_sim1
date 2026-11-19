/* N23 — the grading core.
 *
 * This module is the only writer of a graded record. It consumes a terminal
 * session record (N21), a form's slot bindings (authored data today, N24's
 * manifests later) and the frozen engines, and it emits one canonical,
 * digest-sealed record per GRADING_FORMAT §4.
 *
 * Honesty rules that live in code, not in a comment:
 *   - only terminal states grade; a running session is refused by id;
 *   - an unattempted slot scores zero and is never sent to an engine;
 *   - the N22 completion gate runs *before* every engine call: an invalid or
 *     incomplete response stops there, with its named errors/missing list and
 *     its raw payload preserved byte for byte;
 *   - a Q03/Q05 manual-rubric slot is pending-external and is never handed to
 *     an engine that could pretend to score it;
 *   - the engines' criterion points are re-checked against the declared rubric
 *     and the slot's point weight; a disagreement is a loud
 *     E_GRADING_BINDING_POINTS (the N23-C01 guard), never a silent zero;
 *   - an engine verdict class that the policy island does not declare is a loud
 *     E_GRADING_UNKNOWN_VERDICT naming the slot, criterion and verdict;
 *   - auto points and pending-external points are two separate sums everywhere.
 *
 * The module holds no tolerance, unit factor or scientific constant of its own.
 * Its only numeric literals outside the declared SHA-256 block are 0 and 1,
 * which are structural (indexing and ordering); every point value is read from
 * the policy island, the exam-policy slots or the bank rubric.
 */
(function (this: void, root: any): void {
  'use strict';

  /* ------------------------------------------------------------- contracts */

  const ISLAND_ID = 'sim-grading-policy';
  const RESPONSE_TYPES_ID = 'sim-response-types';
  const RECORD_OWNER = 'N23';
  const RECORD_KIND = 'graded-record';
  const FEEDBACK_KIND = 'feedback-record';
  const SCHEMA_VERSION = 1;

  const STATE_GRADED = 'graded';
  const STATE_INCOMPLETE = 'incomplete';
  const STATE_INVALID = 'invalid';
  const STATE_UNATTEMPTED = 'unattempted';
  const STATE_MANUAL_PENDING = 'manual_pending';

  const EVENT_SESSION = 'session-completed';
  const EVENT_TASK = 'task-answered';
  const EVENT_REMEDIATION = 'remediation-state';

  const ERRORS = [
    'E_GRADING_POLICY_INVALID',
    'E_GRADING_SCHEMA',
    'E_GRADING_STATE',
    'E_GRADING_BINDING_UNKNOWN',
    'E_GRADING_BINDING_POINTS',
    'E_GRADING_UNKNOWN_VERDICT',
    'E_GRADING_CONTEXT',
    'E_FEEDBACK_UNMAPPED',
    'E_FEEDBACK_REMEDIATION_UNRESOLVED'
  ];

  interface SlotPlan {
    slot_id: string;
    topic: number;
    points: number;
  }

  interface EngineCriterion {
    criterion_id: string;
    status: string;
    awarded_points: number;
    pending_points: number;
    max_points: number;
  }

  interface EngineVerdict {
    verdict_class: string;
    error_class: string;
    awarded_criteria: EngineCriterion[];
    machine_checked_points: number;
    pending_points: number;
    max_points: number;
    signature?: string;
    feedback_key?: string;
    taxonomy_class?: string;
    diagnostics?: {
      signatures?: string[];
      remediation?: Array<Record<string, unknown>>;
      per_step?: Array<Record<string, unknown>>;
      per_pair?: Array<Record<string, unknown>>;
    };
    validity?: { class?: string | null; reason_lv?: string | null };
    cited_entries?: Array<Record<string, unknown>>;
  }

  interface DeclaredRow {
    criterion_id: string;
    points: number;
    status: string;
    engine_binding?: string;
    grading?: string;
    verdict_class?: string | null;
    error_class?: string | null;
  }

  interface SlotRows {
    slot_state: string;
    criteria: DeclaredRow[];
  }

  interface CompletionItem {
    id?: string;
    field?: string;
    field_id?: string;
    message_key?: string;
    name?: string;
  }

  interface CompletionVerdict {
    status: string;
    missing?: CompletionItem[];
    errors?: CompletionItem[];
  }

  interface CriterionRecord {
    criterion_id: string;
    engine_binding: string;
    grading: string;
    max_points: number;
    status: string;
    awarded_points: number;
    pending_points: number;
    verdict_class: string | null;
    error_class: string | null;
    errors: Array<{ id: string; field: string; message_key: string }>;
    missing: Array<{ field: string; name: string }>;
    signature_ids: string[];
    feedback_keys: string[];
    remediation_entries: Array<Record<string, unknown>>;
  }

  interface SlotRecord {
    slot_id: string;
    topic: number;
    slot_points: number;
    instance_id: string;
    family_id: string;
    type_id: string;
    state: string;
    verdict_class: string | null;
    error_class: string | null;
    taxonomy_class: string | null;
    cited_entries: Array<{ kind: string; id: string }>;
    criteria: CriterionRecord[];
    task: {
      auto_points: number;
      auto_max_points: number;
      pending_points: number;
      pending_max_points: number;
      max_points: number;
    };
    outcome_ids: string[];
    misconception_signatures: string[];
    raw_input: unknown;
  }

  /* --------------------------------------------------------------- errors */

  /**
   * The single error type this module raises. `code` is one of the frozen ids
   * in `errors`; `message` is a Latvian diagnostic for the operator, never a
   * learner-facing string (those come from #sim-terms).
   */
  class GradingError extends Error {
    public readonly code: string;
    public readonly details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super(message);
      this.name = 'GradingError';
      this.code = code;
      this.details = details || {};
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, GradingError);
      } else {
        this.stack = new Error(message).stack;
      }
    }
  }

  function fail(code: string, message: string, details?: Record<string, unknown>): never {
    throw new GradingError(code, message, details);
  }

  function has(source: Record<string, unknown>, key: string): boolean {
    return Object.prototype.hasOwnProperty.call(source, key);
  }

  function isObject(value: unknown): value is Record<string, any> {
    return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
  }

  function isText(value: unknown): value is string {
    return typeof value === 'string';
  }

  function copyJson<T>(value: T): T {
    return JSON.parse(JSON.stringify(value)) as T;
  }

  /* --------------------------------------------------------- canonical text */

  /**
   * The N04 canonical projection, mirrored in TypeScript: sorted keys, no
   * insignificant whitespace, UTF-8. `String(number)` is the number text; for
   * this record's value domain (integer counts and the bank's binary-exact
   * declared points) it agrees with Python's `json.dumps`, and the runtime
   * harness proves the digest against Node's crypto over these bytes.
   */
  function canonical(value: unknown): string {
    if (value === null || value === undefined) { return 'null'; }
    if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
    if (typeof value === 'number') { return numberText(value); }
    if (typeof value === 'string') { return JSON.stringify(value); }
    if (Array.isArray(value)) {
      const items: string[] = [];
      for (let i = 0; i < value.length; i += 1) { items.push(canonical(value[i])); }
      return '[' + items.join(',') + ']';
    }
    if (typeof value === 'object') {
      const record = value as Record<string, unknown>;
      const keys = Object.keys(record).sort();
      const parts: string[] = [];
      for (let i = 0; i < keys.length; i += 1) {
        parts.push(JSON.stringify(keys[i]) + ':' + canonical(record[keys[i]]));
      }
      return '{' + parts.join(',') + '}';
    }
    return fail('E_GRADING_SCHEMA', 'Kanoniālajā projektcijā nav atbalstīta vērtība.', {
      value_type: typeof value
    });
  }

  function numberText(value: number): string {
    if (!isFinite(value)) {
      return fail('E_GRADING_SCHEMA', 'Kanoniālajā projektcijā nav atbalstīts skaitlis.', { value: String(value) });
    }
    return String(value);
  }

  /* N23-DIGEST-BEGIN — same algorithm as the N17 module (src/quantity-engine.js),
   * a compact SHA-256 over UTF-8. It is byte arithmetic, not a scientific
   * quantity: the build gate exempts exactly this block from the numeric-literal
   * scan and the runtime harness proves it against Node's crypto. */
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

  function sha256(text: string): string {
    const bytes: number[] = [];
    const encoded = unescape(encodeURIComponent(text));
    for (let i = 0; i < encoded.length; i += 1) { bytes.push(encoded.charCodeAt(i) & 0xff); }
    const bitLength = bytes.length * 8;
    bytes.push(0x80);
    while (bytes.length % 64 !== 56) { bytes.push(0); }
    const high = Math.floor(bitLength / 0x100000000);
    const low = bitLength >>> 0;
    bytes.push((high >>> 24) & 0xff, (high >>> 16) & 0xff, (high >>> 8) & 0xff, high & 0xff);
    bytes.push((low >>> 24) & 0xff, (low >>> 16) & 0xff, (low >>> 8) & 0xff, low & 0xff);
    const h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
      0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    const w = new Array<number>(64);
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
        hh = g; g = f; f = e; e = (d + temp1) >>> 0; d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
      }
      h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0; h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
      h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0; h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
    }
    let hex = '';
    for (let z = 0; z < 8; z += 1) { hex += ('00000000' + h[z].toString(16)).slice(-8); }
    return hex;
  }
  /* N23-DIGEST-END */

  function digestValue(value: unknown): string {
    return sha256(canonical(value));
  }

  function withoutDigest(record: Record<string, unknown>): Record<string, unknown> {
    const out: Record<string, unknown> = {};
    const keys = Object.keys(record);
    for (let i = 0; i < keys.length; i += 1) {
      if (keys[i] !== 'digest') { out[keys[i]] = record[keys[i]]; }
    }
    return out;
  }

  function digestOf(record: unknown): string {
    if (!isObject(record)) {
      return fail('E_GRADING_SCHEMA', 'Kopsavilkumu var aprēķināt tikai objektam.', {});
    }
    return digestValue(withoutDigest(record));
  }

  /**
   * The emitted record carries its structural keys in canonical order already,
   * so a reader sees the same order the digest uses. `raw_input` is exempt: it
   * is the learner's stored payload and keeps the exact shape and key order it
   * was stored with (the no-normalisation invariant). `canonicalText` sorts it
   * for the digest only, without rewriting the emitted value.
   */
  function sortedValue(value: unknown, keyName?: string): unknown {
    if (keyName === 'raw_input') { return value; }
    if (Array.isArray(value)) {
      const items: unknown[] = [];
      for (let i = 0; i < value.length; i += 1) { items.push(sortedValue(value[i])); }
      return items;
    }
    if (isObject(value)) {
      const keys = Object.keys(value).sort();
      const out: Record<string, unknown> = {};
      for (let i = 0; i < keys.length; i += 1) { out[keys[i]] = sortedValue(value[keys[i]], keys[i]); }
      return out;
    }
    return value;
  }

  /* --------------------------------------------------------------- islands */

  function readIsland(doc: unknown, id: string): Record<string, unknown> | null {
    if (!doc || typeof (doc as any).getElementById !== 'function') { return null; }
    const node = (doc as any).getElementById(id);
    if (!node) { return null; }
    const raw = node.textContent !== undefined ? node.textContent : node.innerText;
    if (typeof raw !== 'string' || raw === '') {
      return fail('E_GRADING_POLICY_INVALID', 'Sala #' + id + ' ir tukša.', { island: id });
    }
    try {
      return JSON.parse(raw) as Record<string, unknown>;
    } catch (error) {
      return fail('E_GRADING_POLICY_INVALID', 'Sala #' + id + ' nav derīgs JSON.', {
        island: id, reason: String(error)
      });
    }
  }

  /* ------------------------------------------------------------ policy load */

  function requireObject(source: Record<string, unknown>, key: string, path: string): Record<string, unknown> {
    const value = source[key];
    if (!isObject(value)) {
      return fail('E_GRADING_POLICY_INVALID', 'Politikas lauks ' + path + ' nav objekts.', { path: path });
    }
    return value as Record<string, unknown>;
  }

  function requireText(source: Record<string, unknown>, key: string, path: string): string {
    const value = source[key];
    if (!isText(value) || value === '') {
      return fail('E_GRADING_POLICY_INVALID', 'Politikas lauks ' + path + ' nav ne tukša virkne.', { path: path });
    }
    return value;
  }

  function requireArray(source: Record<string, unknown>, key: string, path: string): unknown[] {
    const value = source[key];
    if (!Array.isArray(value)) {
      return fail('E_GRADING_POLICY_INVALID', 'Politikas lauks ' + path + ' nav saraksts.', { path: path });
    }
    return value;
  }

  function requireStateRule(rules: Record<string, unknown>, state: string): void {
    if (!isText(rules[state]) || (rules[state] as string) === '') {
      fail('E_GRADING_POLICY_INVALID', 'Politikā nav deklarēts stāvoklis "' + state + '".', {
        path: 'rubric_policy.slot_state_rules.' + state
      });
    }
  }

  /**
   * Validate the island's frozen structure and return it with its canonical
   * digest. A missing rule is a policy defect, never a default.
   */
  function loadPolicy(doc: unknown): { policy: Record<string, unknown>; digest: string } {
    let island: Record<string, unknown> | null = null;
    if (isObject(doc) && doc.island_id === ISLAND_ID) {
      island = doc as Record<string, unknown>;
    } else {
      island = readIsland(doc, ISLAND_ID);
    }
    if (!island) {
      return fail('E_GRADING_POLICY_INVALID', 'Sala #' + ISLAND_ID + ' nav atrasta.', { island: ISLAND_ID });
    }
    if (island.schema_version !== SCHEMA_VERSION) {
      return fail('E_GRADING_POLICY_INVALID', 'Politikas shēmas versija nav atbalstīta.', {
        schema_version: island.schema_version
      });
    }
    if (island.island_id !== ISLAND_ID) {
      return fail('E_GRADING_POLICY_INVALID', 'Politikas salas id neatbilst.', { island_id: island.island_id });
    }
    const rubric = requireObject(island, 'rubric_policy', 'rubric_policy');
    const verdictRules = requireObject(rubric, 'verdict_rules', 'rubric_policy.verdict_rules');
    const verdictKeys = Object.keys(verdictRules);
    if (verdictKeys.length === 0) {
      return fail('E_GRADING_POLICY_INVALID', 'Politikā nav neviena verdikta noteikuma.', {
        path: 'rubric_policy.verdict_rules'
      });
    }
    for (let i = 0; i < verdictKeys.length; i += 1) {
      const rule = verdictRules[verdictKeys[i]];
      if (!isObject(rule) || !isText((rule as Record<string, unknown>).count)) {
        fail('E_GRADING_POLICY_INVALID', 'Verdikta noteikumam nav lauka count.', {
          path: 'rubric_policy.verdict_rules.' + verdictKeys[i]
        });
      }
    }
    requireText(rubric, 'unknown_verdict_rule', 'rubric_policy.unknown_verdict_rule');
    const statusRules = requireObject(rubric, 'criterion_status_rules', 'rubric_policy.criterion_status_rules');
    const statusKeys = ['awarded', 'denied', 'pending'];
    for (let i = 0; i < statusKeys.length; i += 1) {
      requireText(statusRules, statusKeys[i], 'rubric_policy.criterion_status_rules.' + statusKeys[i]);
    }
    const stateRules = requireObject(rubric, 'slot_state_rules', 'rubric_policy.slot_state_rules');
    const states = [STATE_GRADED, STATE_INCOMPLETE, STATE_INVALID, STATE_UNATTEMPTED, STATE_MANUAL_PENDING];
    for (let i = 0; i < states.length; i += 1) { requireStateRule(stateRules, states[i]); }
    const routing = requireObject(rubric, 'pre_grade_routing', 'rubric_policy.pre_grade_routing');
    const manualTypes = requireArray(routing, 'manual_pending_types', 'rubric_policy.pre_grade_routing.manual_pending_types');
    for (let i = 0; i < manualTypes.length; i += 1) {
      if (!isText(manualTypes[i]) || (manualTypes[i] as string) === '') {
        fail('E_GRADING_POLICY_INVALID', 'Manuālās vērtēšanas tipu sarakstā ir nederīgs ieraksts.', {
          path: 'rubric_policy.pre_grade_routing.manual_pending_types'
        });
      }
    }
    requireText(routing, 'unattempted_error_class', 'rubric_policy.pre_grade_routing.unattempted_error_class');
    requireText(routing, 'manual_pending_error_class', 'rubric_policy.pre_grade_routing.manual_pending_error_class');
    const honesty = requireObject(island, 'honesty_accounting', 'honesty_accounting');
    const formMax = honesty.form_max_points;
    if (typeof formMax !== 'number' || !isFinite(formMax) || formMax <= 0) {
      return fail('E_GRADING_POLICY_INVALID', 'Formas maksimālais punktu skaits nav pozitīvs skaitlis.', {
        path: 'honesty_accounting.form_max_points'
      });
    }
    if (honesty.unblended !== true) {
      return fail('E_GRADING_POLICY_INVALID', 'Godīguma uzskaitei jābūt unblended: true.', {
        path: 'honesty_accounting.unblended'
      });
    }
    const analytics = requireObject(island, 'analytics_contract', 'analytics_contract');
    const events = requireArray(analytics, 'event_types', 'analytics_contract.event_types');
    const requiredEvents = [EVENT_SESSION, EVENT_TASK, EVENT_REMEDIATION];
    for (let i = 0; i < requiredEvents.length; i += 1) {
      if (events.indexOf(requiredEvents[i]) < 0) {
        fail('E_GRADING_POLICY_INVALID', 'Analītikas līgumā trūkst notikuma "' + requiredEvents[i] + '".', {
          path: 'analytics_contract.event_types'
        });
      }
    }
    const binding = requireObject(island, 'binding_rule', 'binding_rule');
    if (binding.slot_points_authoritative !== true) {
      return fail('E_GRADING_POLICY_INVALID', 'binding_rule.slot_points_authoritative jābūt true.', {
        path: 'binding_rule.slot_points_authoritative'
      });
    }
    requireText(binding, 'mismatch_rule', 'binding_rule.mismatch_rule');
    requireText(binding, 'conflict_ref', 'binding_rule.conflict_ref');
    requireArray(island, 'self_test_fixtures', 'self_test_fixtures');
    requireArray(island, 'conflicts', 'conflicts');
    return { policy: island, digest: digestValue(island) };
  }

  /* -------------------------------------------------------------- helpers */

  function sumPoints(rows: DeclaredRow[]): number {
    let total = 0;
    for (let i = 0; i < rows.length; i += 1) { total += Number(rows[i].points); }
    return total;
  }

  function pushUnique(list: string[], value: string): void {
    if (value === '' || list.indexOf(value) >= 0) { return; }
    list.push(value);
  }

  /** The engines' own rubric split: `auto`/`mixed` minus the two external
   * bindings is machine-checked; everything else is pending-external. */
  function rubricIsPending(item: Record<string, unknown>): boolean {
    const grading = isText(item.grading) ? item.grading : '';
    const binding = isText(item.engine_binding) ? item.engine_binding : '';
    const machine = (grading === 'auto' || grading === 'mixed') &&
      binding !== 'self-assessed' && binding !== 'human-review';
    return !machine;
  }

  /* ----------------------------------------------------- the pure aggregation */

  /**
   * Map declared criterion rows through the policy's status and slot-state
   * rules. This is the only place points are turned into awarded/pending sums,
   * and it is also the smoke-vector facade probe.
   *
   * Accepted shapes: an array of `{criterion_id, points, status}` rows (the
   * graded shorthand used by the island's self-test fixtures) or an object
   * `{slot_state, criteria}` where the slot state overrides the row statuses
   * (a malformed answer scores zero whatever its rows say).
   */
  function applyRubricPolicy(
    policy: Record<string, unknown>,
    slotRows: DeclaredRow[] | SlotRows
  ): { criteria: CriterionRecord[]; task: SlotRecord['task'] } {
    if (!isObject(policy)) {
      return fail('E_GRADING_POLICY_INVALID', 'Vērtēšanas politika nav objekts.', {});
    }
    const rubric = requireObject(policy, 'rubric_policy', 'rubric_policy');
    const statusRules = requireObject(rubric, 'criterion_status_rules', 'rubric_policy.criterion_status_rules');
    const stateRules = requireObject(rubric, 'slot_state_rules', 'rubric_policy.slot_state_rules');
    const verdictRules = requireObject(rubric, 'verdict_rules', 'rubric_policy.verdict_rules');

    let slotState = STATE_GRADED;
    let declared: DeclaredRow[];
    if (Array.isArray(slotRows)) {
      declared = slotRows;
    } else if (isObject(slotRows) && Array.isArray(slotRows.criteria)) {
      slotState = isText(slotRows.slot_state) ? slotRows.slot_state : '';
      if (slotState === '' || !isText(stateRules[slotState])) {
        return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināms uzdevuma stāvoklis politikā.', {
          slot_state: String(slotRows.slot_state)
        });
      }
      declared = slotRows.criteria;
    } else {
      return fail('E_GRADING_SCHEMA', 'applyRubricPolicy gaida rindu sarakstu vai {slot_state, criteria}.', {});
    }

    const criteria: CriterionRecord[] = [];
    let auto = 0;
    let autoMax = 0;
    let pending = 0;
    let pendingMax = 0;
    let maximum = 0;

    for (let i = 0; i < declared.length; i += 1) {
      const row = declared[i];
      if (!isObject(row) || !isText(row.criterion_id) || row.criterion_id === '') {
        return fail('E_GRADING_SCHEMA', 'Kritērija rindai nav criterion_id.', { index: i });
      }
      const points = row.points;
      if (typeof points !== 'number' || !isFinite(points) || points < 0) {
        return fail('E_GRADING_SCHEMA', 'Kritērija ' + row.criterion_id + ' punkti nav nederīgi.', {
          criterion_id: row.criterion_id, points: String(points)
        });
      }
      const status = row.status;
      if (!isText(status) || !isText(statusRules[status])) {
        return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināms kritērija statuss "' + String(status) + '".', {
          criterion_id: row.criterion_id, status: String(status)
        });
      }
      if (row.verdict_class !== undefined && row.verdict_class !== null && row.verdict_class !== '') {
        if (!has(verdictRules, row.verdict_class)) {
          return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināma verdikta klase "' + String(row.verdict_class) + '".', {
            criterion_id: row.criterion_id, verdict_class: String(row.verdict_class)
          });
        }
      }
      let effective = status;
      if (slotState === STATE_MANUAL_PENDING) { effective = 'pending'; }
      else if (slotState === STATE_INVALID || slotState === STATE_INCOMPLETE || slotState === STATE_UNATTEMPTED) {
        effective = 'denied';
      }
      let awardedPoints = 0;
      let pendingPoints = 0;
      if (effective === 'awarded') { awardedPoints = points; }
      else if (effective === 'pending') { pendingPoints = points; }
      else if (effective !== 'denied') {
        return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināms kritērija statuss "' + effective + '".', {
          criterion_id: row.criterion_id, status: effective
        });
      }
      auto += awardedPoints;
      pending += pendingPoints;
      maximum += points;
      /* The maxima are a property of the form, not of the answer: a
       * manual-rubric slot is wholly pending-external, and elsewhere the
       * rubric's own split decides which maximum a criterion belongs to. A
       * zeroed answer never moves a point from one maximum to the other. */
      if (slotState === STATE_MANUAL_PENDING || status === 'pending') { pendingMax += points; }
      else { autoMax += points; }
      criteria.push({
        criterion_id: row.criterion_id,
        engine_binding: isText(row.engine_binding) ? row.engine_binding : '',
        grading: isText(row.grading) ? row.grading : '',
        max_points: points,
        status: effective,
        awarded_points: awardedPoints,
        pending_points: pendingPoints,
        verdict_class: isText(row.verdict_class) && row.verdict_class !== '' ? row.verdict_class : null,
        error_class: isText(row.error_class) && row.error_class !== '' ? row.error_class : null,
        errors: [],
        missing: [],
        signature_ids: [],
        feedback_keys: [],
        remediation_entries: []
      });
    }
    return {
      criteria: criteria,
      task: {
        auto_points: auto,
        auto_max_points: autoMax,
        pending_points: pending,
        pending_max_points: pendingMax,
        max_points: maximum
      }
    };
  }

  /* -------------------------------------------------------- terminal record */

  function requireTerminalRecord(
    record: unknown,
    terminalStates: string[]
  ): Record<string, unknown> {
    if (!isObject(record)) {
      return fail('E_GRADING_SCHEMA', 'Beigu ieraksts nav objekts.', {});
    }
    if (record.schema_version !== SCHEMA_VERSION) {
      return fail('E_GRADING_SCHEMA', 'Beigu ieraksta schema_version nav 1.', {
        schema_version: record.schema_version
      });
    }
    if (!isText(record.state) || terminalStates.indexOf(record.state) < 0) {
      return fail('E_GRADING_STATE', 'Vērtēt var tikai iesniegtu, beigu termiņu sasniegušu vai pārtrauktu sesiju.', {
        state: record.state, terminal_states: terminalStates
      });
    }
    const requiredText = ['session_id', 'form_id'];
    for (let i = 0; i < requiredText.length; i += 1) {
      if (!isText(record[requiredText[i]]) || record[requiredText[i]] === '') {
        fail('E_GRADING_SCHEMA', 'Beigu ierakstam trūkst lauka ' + requiredText[i] + '.', { field: requiredText[i] });
      }
    }
    const requiredNumberOrNull = ['started_at_ms', 'finished_at_ms', 'elapsed_ms'];
    for (let i = 0; i < requiredNumberOrNull.length; i += 1) {
      const value = record[requiredNumberOrNull[i]];
      if (value !== null && (typeof value !== 'number' || !isFinite(value))) {
        fail('E_GRADING_SCHEMA', 'Beigu ieraksta lauks ' + requiredNumberOrNull[i] + ' nav skaitlis vai null.', {
          field: requiredNumberOrNull[i]
        });
      }
    }
    const listFields = ['flags', 'unanswered_slot_ids', 'remediation_slot_ids', 'transitions'];
    for (let i = 0; i < listFields.length; i += 1) {
      if (!Array.isArray(record[listFields[i]])) {
        fail('E_GRADING_SCHEMA', 'Beigu ieraksta lauks ' + listFields[i] + ' nav saraksts.', { field: listFields[i] });
      }
    }
    if (!Array.isArray(record.answers)) {
      return fail('E_GRADING_SCHEMA', 'Beigu ierakstam nav atbilžu saraksta.', { field: 'answers' });
    }
    return record;
  }

  function indexAnswers(
    record: Record<string, unknown>,
    plans: SlotPlan[]
  ): Record<string, { kind: string; payload: Record<string, unknown> }> {
    const answers = record.answers as unknown[];
    const known: Record<string, boolean> = {};
    for (let i = 0; i < plans.length; i += 1) { known[plans[i].slot_id] = true; }
    const map: Record<string, { kind: string; payload: Record<string, unknown> }> = {};
    for (let i = 0; i < answers.length; i += 1) {
      const answer = answers[i];
      if (!isObject(answer) || !isText(answer.slot_id) || answer.slot_id === '') {
        return fail('E_GRADING_SCHEMA', 'Atbildei nav slot_id.', { index: i });
      }
      if (!has(known, answer.slot_id)) {
        return fail('E_GRADING_SCHEMA', 'Atbilde attiecas uz formā neesošu uzdevumu vietu.', { slot_id: answer.slot_id });
      }
      if (has(map, answer.slot_id)) {
        return fail('E_GRADING_SCHEMA', 'Vienai uzdevumu vietai ir vairākas atbildes.', { slot_id: answer.slot_id });
      }
      if (!isText(answer.kind) || answer.kind === '') {
        return fail('E_GRADING_SCHEMA', 'Atbildei nav datu veida.', { slot_id: answer.slot_id });
      }
      if (!isObject(answer.payload)) {
        return fail('E_GRADING_SCHEMA', 'Atbildes datums nav objekts.', { slot_id: answer.slot_id });
      }
      map[answer.slot_id] = { kind: answer.kind, payload: answer.payload as Record<string, unknown> };
    }
    const declared = (record.unanswered_slot_ids as unknown[]).slice().map(function (entry: unknown): string {
      return isText(entry) ? entry : String(entry);
    }).sort();
    const derived: string[] = [];
    for (let i = 0; i < plans.length; i += 1) {
      if (!has(map, plans[i].slot_id)) { derived.push(plans[i].slot_id); }
    }
    derived.sort();
    if (declared.join('|') !== derived.join('|')) {
      return fail('E_GRADING_SCHEMA', 'unanswered_slot_ids nesakrīt ar atbilžu karti.', {
        declared: declared, derived: derived
      });
    }
    return map;
  }

  /* -------------------------------------------------------------- bindings */

  function requireSlots(examPolicy: unknown): SlotPlan[] {
    if (!isObject(examPolicy) || !Array.isArray(examPolicy.slots)) {
      return fail('E_GRADING_CONTEXT', 'Kontekstā nav ielādētas eksāmena politikas ar slotiem.', {
        missing: ['examPolicy.slots']
      });
    }
    const plans: SlotPlan[] = [];
    for (let i = 0; i < examPolicy.slots.length; i += 1) {
      const slot = examPolicy.slots[i];
      if (!isObject(slot) || !isText(slot.slot_id) || typeof slot.points !== 'number') {
        fail('E_GRADING_POLICY_INVALID', 'Eksāmena politikas slots nav derīgs.', { index: i });
      }
      plans.push({ slot_id: slot.slot_id, topic: Number(slot.topic), points: Number(slot.points) });
    }
    if (plans.length === 0) {
      return fail('E_GRADING_POLICY_INVALID', 'Eksāmena politikā nav neviena slota.', {});
    }
    return plans;
  }

  interface BoundSlot {
    slot_id: string;
    type_id: string;
    instance_id: string;
    instance: Record<string, unknown>;
    figure_id: string | null;
    source_index: number;
  }

  function indexBindings(bindings: unknown, plans: SlotPlan[], bank: unknown): Record<string, BoundSlot> {
    if (!Array.isArray(bindings)) {
      return fail('E_GRADING_CONTEXT', 'Kontekstā nav saišu saraksta.', { missing: ['bindings'] });
    }
    const bySlot: Record<string, BoundSlot> = {};
    const slots: Record<string, SlotPlan> = {};
    for (let i = 0; i < plans.length; i += 1) { slots[plans[i].slot_id] = plans[i]; }
    const instancesById = isObject(bank) && isObject(bank.instancesById) ? bank.instancesById : null;
    for (let i = 0; i < bindings.length; i += 1) {
      const binding = bindings[i];
      if (!isObject(binding) || !isText(binding.slot_id) || !isText(binding.type_id) || !isText(binding.instance_id)) {
        fail('E_GRADING_BINDING_UNKNOWN', 'Saitei trūkst slot_id, type_id vai instance_id.', { index: i });
      }
      const slotId = binding.slot_id as string;
      const typeId = binding.type_id as string;
      const instanceId = binding.instance_id as string;
      if (!has(slots, slotId)) {
        fail('E_GRADING_BINDING_UNKNOWN', 'Saite attiecas uz nezināmu uzdevumu vietu.', { slot_id: slotId });
      }
      if (has(bySlot, slotId)) {
        fail('E_GRADING_BINDING_UNKNOWN', 'Uzdevumu vietai ir vairākas saites.', { slot_id: slotId });
      }
      let instance: Record<string, unknown> | null = null;
      if (isObject(binding.instance)) {
        instance = binding.instance as Record<string, unknown>;
      } else if (instancesById && isObject(instancesById[instanceId])) {
        instance = instancesById[instanceId] as Record<string, unknown>;
      }
      if (!instance) {
        return fail('E_GRADING_BINDING_UNKNOWN', 'Bankā nav instances ' + instanceId + '.', {
          slot_id: slotId, instance_id: instanceId
        });
      }
      if (isText(instance.question_id) && instance.question_id !== instanceId) {
        return fail('E_GRADING_BINDING_UNKNOWN', 'Instances id neatbilst saitei.', {
          slot_id: slotId, instance_id: instanceId, instance_question_id: instance.question_id
        });
      }
      if (!isText(instance.type_id) || instance.type_id !== typeId) {
        return fail('E_GRADING_BINDING_UNKNOWN', 'Saites tips neatbilst instances tipam.', {
          slot_id: slotId, instance_id: instanceId, type_id: typeId,
          instance_type_id: instance.type_id
        });
      }
      if (!Array.isArray(instance.rubric)) {
        return fail('E_GRADING_BINDING_UNKNOWN', 'Instancei nav rubrikas.', { slot_id: slotId, instance_id: instanceId });
      }
      bySlot[slotId] = {
        slot_id: slotId,
        type_id: typeId,
        instance_id: instanceId,
        instance: instance,
        figure_id: isText(binding.figure_id) && binding.figure_id !== '' ? binding.figure_id : null,
        source_index: i
      };
    }
    for (let i = 0; i < plans.length; i += 1) {
      if (!has(bySlot, plans[i].slot_id)) {
        fail('E_GRADING_BINDING_UNKNOWN', 'Formas vietai nav saites.', { slot_id: plans[i].slot_id });
      }
    }
    return bySlot;
  }

  /* ------------------------------------------------------- engine dispatch */

  /**
   * The frozen zero-adapter dispatch of tools/check_n22_runtime.js: the same
   * type groups, the same submission binding, no coercion. The registry's
   * label for Q07/Q14/Q18 says N19-method, but the N19 spec builder refuses
   * payload_class option_select (N22-C05), so these go to the quantity
   * engine's option_select branch exactly as the parity table records.
   */
  function dispatchEngine(
    bound: BoundSlot,
    payload: Record<string, unknown>,
    instance: Record<string, unknown>,
    context: Record<string, any>
  ): EngineVerdict {
    const typeId = bound.type_id;
    const quantity = context.quantity;
    const method = context.method;
    const graph = context.graph;
    if (typeId === 'Q01' || typeId === 'Q02' || typeId === 'Q09' || typeId === 'Q10') {
      const declared = isObject(instance.payload) && Array.isArray((instance.payload as Record<string, unknown>).input_fields)
        ? ((instance.payload as Record<string, unknown>).input_fields as Array<Record<string, unknown>>)
        : [];
      let fieldId = '';
      if (declared.length > 0 && isText(declared[0].field_id) && declared[0].field_id !== '') {
        fieldId = declared[0].field_id as string;
      } else if (isObject(payload.values)) {
        const keys = Object.keys(payload.values);
        fieldId = keys.length > 0 ? keys[0] : 'value';
      } else {
        fieldId = 'value';
      }
      return quantity.grade(instance, { value: (payload.values as Record<string, unknown>)[fieldId] }, {}) as EngineVerdict;
    }
    if (typeId === 'Q07' || typeId === 'Q14' || typeId === 'Q18') {
      return quantity.grade(instance, { selected_ids: (payload.selected as string[]).slice() }, {}) as EngineVerdict;
    }
    if (typeId === 'Q06') {
      const pairs = (payload.pairs as Array<Record<string, unknown>>).map(function (pair: Record<string, unknown>) {
        return { left_id: pair.left_id, right_id: pair.right_id };
      });
      return method.grade(method.specFromInstance(instance), { pairs: pairs }) as EngineVerdict;
    }
    if (typeId === 'Q08') {
      return method.grade(method.specFromInstance(instance), { order: (payload.order as string[]).slice() }) as EngineVerdict;
    }
    if (typeId === 'Q15' || typeId === 'Q16') {
      return method.grade(method.specFromInstance(instance), { text: payload.text }) as EngineVerdict;
    }
    if (typeId === 'Q12') {
      const read = payload.read as Record<string, unknown>;
      return graph.scoreReading(
        { kind: 'n05_payload', instance: instance },
        { x: read.x, value: read.y },
        instance.rubric
      ) as EngineVerdict;
    }
    if (typeId === 'Q11') {
      if (bound.figure_id === null) {
        return fail('E_GRADING_CONTEXT', 'Grafika zīmēšanas vietai nav deklarēta figūra (binding.figure_id).', {
          slot_id: bound.slot_id, instance_id: bound.instance_id, type_id: typeId
        });
      }
      const figures = context.figures;
      const record = isObject(figures) ? figures[bound.figure_id] : null;
      if (!isObject(record)) {
        return fail('E_GRADING_CONTEXT', 'Figūra ' + bound.figure_id + ' nav ielādēta kontekstā.', {
          slot_id: bound.slot_id, figure_id: bound.figure_id
        });
      }
      return graph.scoreDrawing(record, payload.draw_payload, instance.rubric) as EngineVerdict;
    }
    /* Q03, Q04, Q05, Q13, Q17: the frozen N22 table hands the stored payload
     * unparsed to the quantity engine's method branch. Q03/Q05 never reach
     * here (manual pending); the rest report their self-assessed rubric as
     * pending, never as a keyword match. */
    return quantity.grade(instance, copyJson(payload), {}) as EngineVerdict;
  }

  /* ------------------------------------------------------------ row shaping */

  function declaredRowsOf(instance: Record<string, unknown>): DeclaredRow[] {
    const rubric = instance.rubric as Array<Record<string, unknown>>;
    const rows: DeclaredRow[] = [];
    for (let i = 0; i < rubric.length; i += 1) {
      const item = rubric[i];
      if (!isObject(item) || !isText(item.criterion_id) || typeof item.points !== 'number') {
        fail('E_GRADING_BINDING_UNKNOWN', 'Rubrikas ieraksts nav derīgs.', {
          instance_id: instance.question_id, index: i
        });
      }
      rows.push({
        criterion_id: item.criterion_id as string,
        points: Number(item.points),
        /* The declared status records the rubric's own split; a slot-state rule
         * may override the points but never the maximum it belongs to. */
        status: rubricIsPending(item) ? 'pending' : 'denied',
        engine_binding: isText(item.engine_binding) ? item.engine_binding : '',
        grading: isText(item.grading) ? item.grading : ''
      });
    }
    return rows;
  }

  function engineCriterionIndex(verdict: EngineVerdict, slotId: string): Record<string, EngineCriterion> {
    const rows = verdict.awarded_criteria;
    if (!Array.isArray(rows)) {
      return fail('E_GRADING_SCHEMA', 'Dzinēja verdiktam nav awarded_criteria saraksta.', { slot_id: slotId });
    }
    const index: Record<string, EngineCriterion> = {};
    for (let i = 0; i < rows.length; i += 1) {
      const row = rows[i];
      if (!isObject(row) || !isText(row.criterion_id)) {
        fail('E_GRADING_SCHEMA', 'Dzinēja kritērija rinda nav derīga.', { slot_id: slotId });
      }
      if (has(index, row.criterion_id)) {
        fail('E_GRADING_SCHEMA', 'Dzinējs atgrieza kritēriju divreiz.', { slot_id: slotId, criterion_id: row.criterion_id });
      }
      index[row.criterion_id] = row;
    }
    return index;
  }

  function requireEngineRow(
    engineRows: Record<string, EngineCriterion>,
    declared: DeclaredRow,
    bound: BoundSlot,
    policy: Record<string, unknown>
  ): EngineCriterion {
    const row = engineRows[declared.criterion_id];
    if (!row) {
      return fail('E_GRADING_SCHEMA', 'Dzinējs neaptvēra rubrikas kritēriju ' + declared.criterion_id + '.', {
        slot_id: bound.slot_id, instance_id: bound.instance_id, criterion_id: declared.criterion_id
      });
    }
    const statusRules = (policy.rubric_policy as Record<string, unknown>).criterion_status_rules as Record<string, unknown>;
    if (!isText(row.status) || !isText(statusRules[row.status])) {
      return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināms dzinēja kritērija statuss "' + String(row.status) + '".', {
        slot_id: bound.slot_id, criterion_id: declared.criterion_id, status: String(row.status)
      });
    }
    if (Number(row.max_points) !== declared.points) {
      return fail('E_GRADING_BINDING_POINTS', 'Kritērija maksimālie punkti neatbilst rubrikai.', {
        slot_id: bound.slot_id, instance_id: bound.instance_id, criterion_id: declared.criterion_id,
        rubric_points: declared.points, engine_max_points: row.max_points
      });
    }
    const awarded = Number(row.awarded_points);
    const pending = Number(row.pending_points);
    if (row.status === 'awarded') {
      if (awarded !== declared.points || pending !== 0) {
        fail('E_GRADING_BINDING_POINTS', 'Awarded kritērijs neatbilst politikas punktu noteikumam.', {
          slot_id: bound.slot_id, criterion_id: declared.criterion_id,
          awarded_points: awarded, pending_points: pending, max_points: declared.points
        });
      }
    } else if (row.status === 'denied') {
      if (awarded !== 0 || pending !== 0) {
        fail('E_GRADING_BINDING_POINTS', 'Denied kritērijam ir punkti.', {
          slot_id: bound.slot_id, criterion_id: declared.criterion_id,
          awarded_points: awarded, pending_points: pending
        });
      }
    } else if (row.status === 'pending') {
      if (awarded !== 0 || pending !== declared.points) {
        fail('E_GRADING_BINDING_POINTS', 'Pending kritērijs neatbilst politikas punktu noteikumam.', {
          slot_id: bound.slot_id, criterion_id: declared.criterion_id,
          awarded_points: awarded, pending_points: pending, max_points: declared.points
        });
      }
    }
    return row;
  }

  function completionErrors(items: CompletionItem[] | undefined): Array<{ id: string; field: string; message_key: string }> {
    const out: Array<{ id: string; field: string; message_key: string }> = [];
    const list = items || [];
    for (let i = 0; i < list.length; i += 1) {
      const item = list[i];
      out.push({
        id: isText(item.id) ? item.id : '',
        field: isText(item.field) ? item.field : '',
        message_key: isText(item.message_key) ? item.message_key : ''
      });
    }
    return out;
  }

  function completionMissing(items: CompletionItem[] | undefined): Array<{ field: string; name: string }> {
    const out: Array<{ field: string; name: string }> = [];
    const list = items || [];
    for (let i = 0; i < list.length; i += 1) {
      const item = list[i];
      out.push({
        field: isText(item.field_id) ? item.field_id : (isText(item.field) ? item.field : ''),
        name: isText(item.name) ? item.name : ''
      });
    }
    return out;
  }

  function decorateZero(
    base: Omit<SlotRecord, 'state' | 'verdict_class' | 'error_class' | 'taxonomy_class' | 'cited_entries' | 'criteria' | 'task'>,
    policy: Record<string, unknown>,
    state: string,
    errorClass: string | null,
    errors: Array<{ id: string; field: string; message_key: string }>,
    missing: Array<{ field: string; name: string }>,
    declared: DeclaredRow[]
  ): SlotRecord {
    const aggregated = applyRubricPolicy(policy, { slot_state: state, criteria: declared });
    for (let i = 0; i < aggregated.criteria.length; i += 1) {
      aggregated.criteria[i].error_class = errorClass;
      aggregated.criteria[i].errors = errors.slice();
      aggregated.criteria[i].missing = missing.slice();
    }
    return {
      slot_id: base.slot_id,
      topic: base.topic,
      slot_points: base.slot_points,
      instance_id: base.instance_id,
      family_id: base.family_id,
      type_id: base.type_id,
      state: state,
      verdict_class: null,
      error_class: errorClass,
      taxonomy_class: null,
      cited_entries: [],
      criteria: aggregated.criteria,
      task: aggregated.task,
      outcome_ids: base.outcome_ids,
      misconception_signatures: base.misconception_signatures,
      raw_input: base.raw_input
    };
  }

  /* ------------------------------------------------------------ slot grading */

  function gradeSlot(
    plan: SlotPlan,
    bound: BoundSlot,
    answer: { kind: string; payload: Record<string, unknown> } | null,
    context: Record<string, any>,
    policy: Record<string, unknown>,
    responseTypes: Record<string, unknown>
  ): SlotRecord {
    const instance = bound.instance;
    const rubricPoints = sumPoints(declaredRowsOf(instance));
    if (rubricPoints !== plan.points) {
      return fail('E_GRADING_BINDING_POINTS', 'Rubrikas punktu summa neatbilst uzdevumu vietas punktiem.', {
        slot_id: plan.slot_id, instance_id: bound.instance_id,
        slot_points: plan.points, rubric_points: rubricPoints, conflict_ref: 'N23-C01'
      });
    }
    const base = {
      slot_id: plan.slot_id,
      topic: plan.topic,
      slot_points: plan.points,
      instance_id: bound.instance_id,
      family_id: isText(instance.family_id) ? instance.family_id : '',
      type_id: bound.type_id,
      outcome_ids: Array.isArray(instance.outcome_ids) ? (instance.outcome_ids as string[]).slice() : [],
      misconception_signatures: Array.isArray(instance.misconception_signatures)
        ? (instance.misconception_signatures as string[]).slice()
        : [],
      raw_input: answer ? copyJson(answer.payload) : null
    };
    if (!answer) {
      return decorateZero(base, policy, STATE_UNATTEMPTED,
        policyErrorClass(policy, 'unattempted_error_class'), [], [], declaredRowsOf(instance));
    }

    const types = isObject(responseTypes.types) ? responseTypes.types as Record<string, unknown> : {};
    const contract = types[bound.type_id];
    if (!isObject(contract) || !isObject(contract.grading_binding)) {
      return fail('E_GRADING_BINDING_UNKNOWN', 'Atbilžu tipam ' + bound.type_id + ' nav vērtēšanas saites.', {
        slot_id: plan.slot_id, type_id: bound.type_id
      });
    }
    const payload = answer.payload;
    const routing = (policy.rubric_policy as Record<string, unknown>).pre_grade_routing as Record<string, unknown>;
    const manualTypes = routing.manual_pending_types as string[];

    if (manualTypes.indexOf(bound.type_id) >= 0) {
      if (contract.grading_binding.class !== 'pending') {
        return fail('E_GRADING_SCHEMA', 'Politika tipu ' + bound.type_id + ' sauc par manuālu, bet reģistrs ne.', {
          slot_id: plan.slot_id, type_id: bound.type_id, registry_class: contract.grading_binding.class
        });
      }
      const pending = context.inputsIntegration.q03PendingPath(payload);
      if (!isObject(pending) || pending.class !== 'pending' || pending.graded !== false || pending.verdict !== null) {
        return fail('E_GRADING_SCHEMA', 'Manuālās vērtēšanas ceļš neatgrieza pending ierakstu.', {
          slot_id: plan.slot_id, type_id: bound.type_id
        });
      }
      return decorateZero(base, policy, STATE_MANUAL_PENDING,
        policyErrorClass(policy, 'manual_pending_error_class'), [], [], declaredRowsOf(instance));
    }

    const completion = context.inputsRegistry.completion(bound.type_id, contract, instance, payload) as CompletionVerdict;
    if (!isObject(completion) || !isText(completion.status)) {
      return fail('E_GRADING_SCHEMA', 'Pabeigtības pārbaude neatgrieza statusu.', {
        slot_id: plan.slot_id, type_id: bound.type_id
      });
    }
    if (completion.status === 'invalid') {
      const errors = completionErrors(completion.errors);
      const errorClass = errors.length > 0 && errors[0].id !== '' ? errors[0].id : '';
      if (errorClass === '') {
        return fail('E_GRADING_SCHEMA', 'Nederīgai atbildei nav nosaukta kļūda.', { slot_id: plan.slot_id });
      }
      const missing = completionMissing(completion.missing);
      return decorateZero(base, policy, STATE_INVALID, errorClass, errors, missing, declaredRowsOf(instance));
    }
    if (completion.status === 'incomplete') {
      const missing = completionMissing(completion.missing);
      const errors = completionErrors(completion.errors);
      const errorClass = errors.length > 0 && errors[0].id !== '' ? errors[0].id : null;
      return decorateZero(base, policy, STATE_INCOMPLETE, errorClass, errors, missing, declaredRowsOf(instance));
    }
    if (completion.status !== 'complete') {
      return fail('E_GRADING_SCHEMA', 'Nezināms pabeigtības statuss "' + String(completion.status) + '".', {
        slot_id: plan.slot_id, status: String(completion.status)
      });
    }

    const verdict = dispatchEngine(bound, payload, instance, context);
    if (!isObject(verdict) || !isText(verdict.verdict_class)) {
      return fail('E_GRADING_SCHEMA', 'Dzinējs neatgrieza verdikta klasi.', { slot_id: plan.slot_id });
    }
    const verdictRules = (policy.rubric_policy as Record<string, unknown>).verdict_rules as Record<string, unknown>;
    if (!has(verdictRules, verdict.verdict_class)) {
      return fail('E_GRADING_UNKNOWN_VERDICT', 'Nezināma dzinēja verdikta klase "' + String(verdict.verdict_class) + '".', {
        slot_id: plan.slot_id, instance_id: bound.instance_id, verdict_class: String(verdict.verdict_class)
      });
    }
    if (Number(verdict.max_points) !== plan.points) {
      return fail('E_GRADING_BINDING_POINTS', 'Dzinēja maksimālie punkti neatbilst uzdevumu vietai.', {
        slot_id: plan.slot_id, instance_id: bound.instance_id,
        slot_points: plan.points, engine_max_points: verdict.max_points
      });
    }
    /* The N18 record carries its structural diagnosis in validity.class; the
     * slot's error_class is that class whenever the engine sets one, so the two
     * must never disagree. A drift is a contract break, not a data point. */
    const validity = verdict.validity;
    if (validity && isText(validity.class) && isText(verdict.error_class) &&
        validity.class !== verdict.error_class) {
      return fail('E_GRADING_SCHEMA', 'N18 validity.class neatbilst verdikta error_class.', {
        slot_id: plan.slot_id, validity_class: validity.class, error_class: verdict.error_class
      });
    }

    const declared = declaredRowsOf(instance);
    const engineRows = engineCriterionIndex(verdict, plan.slot_id);
    const engineIds = Object.keys(engineRows);
    for (let i = 0; i < engineIds.length; i += 1) {
      let known = false;
      for (let j = 0; j < declared.length; j += 1) {
        if (declared[j].criterion_id === engineIds[i]) { known = true; }
      }
      if (!known) {
        fail('E_GRADING_SCHEMA', 'Dzinējs atgrieza rubrikā neesošu kritēriju ' + engineIds[i] + '.', {
          slot_id: plan.slot_id, criterion_id: engineIds[i]
        });
      }
    }
    for (let i = 0; i < declared.length; i += 1) {
      const engineRow = requireEngineRow(engineRows, declared[i], bound, policy);
      declared[i].status = engineRow.status;
      declared[i].verdict_class = verdict.verdict_class;
      declared[i].error_class = isText(verdict.error_class) ? verdict.error_class : null;
    }

    const aggregated = applyRubricPolicy(policy, { slot_state: STATE_GRADED, criteria: declared });
    if (aggregated.task.auto_points !== Number(verdict.machine_checked_points)) {
      return fail('E_GRADING_BINDING_POINTS', 'Politikas auto summa neatbilst dzinēja summai.', {
        slot_id: plan.slot_id, instance_id: bound.instance_id,
        policy_auto: aggregated.task.auto_points, engine_auto: verdict.machine_checked_points
      });
    }
    if (aggregated.task.pending_points !== Number(verdict.pending_points)) {
      return fail('E_GRADING_BINDING_POINTS', 'Politikas pending summa neatbilst dzinēja summai.', {
        slot_id: plan.slot_id, instance_id: bound.instance_id,
        policy_pending: aggregated.task.pending_points, engine_pending: verdict.pending_points
      });
    }

    const attachments = verdictAttachments(verdict, aggregated.criteria);
    for (let i = 0; i < aggregated.criteria.length; i += 1) {
      const criterion = aggregated.criteria[i];
      const attachment = attachments.criterion[criterion.criterion_id];
      criterion.signature_ids = attachment.signatures;
      criterion.feedback_keys = attachment.feedback_keys;
      criterion.remediation_entries = attachment.remediation;
    }

    return {
      slot_id: base.slot_id,
      topic: base.topic,
      slot_points: base.slot_points,
      instance_id: base.instance_id,
      family_id: base.family_id,
      type_id: base.type_id,
      state: STATE_GRADED,
      verdict_class: verdict.verdict_class,
      error_class: isText(verdict.error_class) ? verdict.error_class : null,
      taxonomy_class: isText(verdict.taxonomy_class) && verdict.taxonomy_class !== 'NONE' ? verdict.taxonomy_class : null,
      cited_entries: attachments.cited,
      criteria: aggregated.criteria,
      task: aggregated.task,
      outcome_ids: base.outcome_ids,
      misconception_signatures: base.misconception_signatures,
      raw_input: base.raw_input
    };
  }

  interface Attachments {
    cited: Array<{ kind: string; id: string }>;
    criterion: Record<string, { signatures: string[]; feedback_keys: string[]; remediation: Array<Record<string, unknown>> }>;
  }

  /**
   * The engine verdicts carry their diagnosis at the task level (N17's
   * signature/feedback_key, N19's diagnostics, N18's cited entries). The record
   * exposes it on the criterion that lost the points: a denied criterion is the
   * place a learner can act on. Nothing is invented and nothing is dropped:
   * an N19 remediation entry whose step has no matching criterion id is
   * attached to the first denied criterion of that slot.
   */
  function verdictAttachments(verdict: EngineVerdict, criteria: CriterionRecord[]): Attachments {
    const out: Attachments = { cited: [], criterion: {} };
    for (let i = 0; i < criteria.length; i += 1) {
      out.criterion[criteria[i].criterion_id] = { signatures: [], feedback_keys: [], remediation: [] };
    }
    const cited = verdict.cited_entries;
    if (Array.isArray(cited)) {
      for (let i = 0; i < cited.length; i += 1) {
        const entry = cited[i];
        if (isObject(entry) && isText(entry.kind)) {
          out.cited.push({ kind: entry.kind, id: isText(entry.id) ? entry.id : '' });
        }
      }
    }

    const taskSignatures: string[] = [];
    if (isText(verdict.signature) && verdict.signature !== '' && verdict.signature !== 'NONE') {
      pushUnique(taskSignatures, verdict.signature);
    }
    const diagnostics = isObject(verdict.diagnostics) ? verdict.diagnostics : null;
    if (diagnostics && Array.isArray(diagnostics.signatures)) {
      for (let i = 0; i < diagnostics.signatures.length; i += 1) {
        const signature = diagnostics.signatures[i];
        if (isText(signature) && signature !== '') { pushUnique(taskSignatures, signature); }
      }
    }
    const taskFeedback: string[] = [];
    if (isText(verdict.feedback_key) && verdict.feedback_key !== '') { pushUnique(taskFeedback, verdict.feedback_key); }

    const denied: CriterionRecord[] = [];
    for (let i = 0; i < criteria.length; i += 1) {
      if (criteria[i].status === 'denied') { denied.push(criteria[i]); }
    }
    for (let i = 0; i < denied.length; i += 1) {
      const bucket = out.criterion[denied[i].criterion_id];
      for (let s = 0; s < taskSignatures.length; s += 1) { pushUnique(bucket.signatures, taskSignatures[s]); }
      for (let f = 0; f < taskFeedback.length; f += 1) { pushUnique(bucket.feedback_keys, taskFeedback[f]); }
    }

    const entries = diagnostics && Array.isArray(diagnostics.remediation) ? diagnostics.remediation : [];
    for (let i = 0; i < entries.length; i += 1) {
      const entry = entries[i];
      if (!isObject(entry)) { continue; }
      const stepId = isText(entry.step_id) ? entry.step_id as string : '';
      let target: CriterionRecord | null = null;
      for (let c = 0; c < criteria.length && stepId !== ''; c += 1) {
        const id = criteria[c].criterion_id;
        if (id.slice(id.length - (stepId.length + '_PAIR_'.length)) === '_PAIR_' + stepId ||
            id.slice(id.length - (stepId.length + '_STEP_'.length)) === '_STEP_' + stepId) {
          target = criteria[c];
        }
      }
      if (!target && denied.length > 0) { target = denied[0]; }
      if (!target && criteria.length > 0) { target = criteria[0]; }
      if (!target) { continue; }
      const bucket = out.criterion[target.criterion_id];
      bucket.remediation.push(copyJson(entry));
      if (isText(entry.misconception_signature) && entry.misconception_signature !== '') {
        pushUnique(bucket.signatures, entry.misconception_signature);
      }
      if (isText(entry.feedback_key) && entry.feedback_key !== '') {
        pushUnique(bucket.feedback_keys, entry.feedback_key);
      }
    }
    return out;
  }

  function policyErrorClass(policy: Record<string, unknown>, key: string): string {
    const routing = (policy.rubric_policy as Record<string, unknown>).pre_grade_routing as Record<string, unknown>;
    const value = routing[key];
    return isText(value) ? value : '';
  }

  /* ------------------------------------------------------- the main entry */

  function requireContext(context: unknown): Record<string, any> {
    if (!isObject(context)) {
      return fail('E_GRADING_CONTEXT', 'Vērtēšanas konteksts nav objekts.', {});
    }
    const required = ['quantity', 'method', 'graph', 'inputsRegistry', 'inputsIntegration'];
    const missing: string[] = [];
    for (let i = 0; i < required.length; i += 1) {
      if (!isObject(context[required[i]])) { missing.push(required[i]); }
    }
    if (!isObject(context.examPolicy)) { missing.push('examPolicy'); }
    if (!isObject(context.bank) || !isObject(context.bank.instancesById)) { missing.push('bank.instancesById'); }
    if (!isObject(context.oracle)) { missing.push('oracle'); }
    if (!isText(context.bindingSource) || context.bindingSource === '') { missing.push('bindingSource'); }
    if (missing.length > 0) {
      fail('E_GRADING_CONTEXT', 'Vērtēšanas kontekstā trūkst: ' + missing.join(', ') + '.', { missing: missing });
    }
    return context as Record<string, any>;
  }

  function resolveResponseTypes(context: Record<string, any>): Record<string, unknown> {
    if (isObject(context.responseTypes)) { return context.responseTypes as Record<string, unknown>; }
    const island = readIsland(context.doc, RESPONSE_TYPES_ID);
    if (!island) {
      return fail('E_GRADING_CONTEXT', 'Kontekstā nav atbilžu tipu reģistra #' + RESPONSE_TYPES_ID + '.', {
        missing: ['responseTypes']
      });
    }
    return island;
  }

  /**
   * Grade one terminal record against one form's bindings. The result is the
   * core graded record with `feedback: null` and its canonical digest; the
   * feedback module completes it through composeGradedRecord.
   */
  function gradeTerminalRecord(
    terminalRecord: unknown,
    bindings: unknown,
    context: unknown
  ): Record<string, unknown> {
    const ctx = requireContext(context);
    const loaded = isObject(ctx.gradingPolicy)
      ? { policy: ctx.gradingPolicy as Record<string, unknown>, digest: digestValue(ctx.gradingPolicy) }
      : loadPolicy(ctx.doc);
    const policy = loaded.policy;
    const plans = requireSlots(ctx.examPolicy);
    const terminalStates = (ctx.examPolicy as Record<string, any>).session_contract
      && Array.isArray((ctx.examPolicy as Record<string, any>).session_contract.terminal_states)
      ? ((ctx.examPolicy as Record<string, any>).session_contract.terminal_states as string[])
      : [];
    if (terminalStates.length === 0) {
      return fail('E_GRADING_CONTEXT', 'Eksāmena politikā nav deklarētu galīgo stāvokļu.', {
        missing: ['examPolicy.session_contract.terminal_states']
      });
    }
    const record = requireTerminalRecord(terminalRecord, terminalStates);
    const answers = indexAnswers(record, plans);
    const bySlot = indexBindings(bindings, plans, ctx.bank);
    const responseTypes = resolveResponseTypes(ctx);

    const slots: SlotRecord[] = [];
    for (let i = 0; i < plans.length; i += 1) {
      const plan = plans[i];
      const bound = bySlot[plan.slot_id];
      const answer = has(answers as Record<string, unknown>, plan.slot_id) ? answers[plan.slot_id] : null;
      slots.push(gradeSlot(plan, bound, answer, ctx, policy, responseTypes));
    }

    const totals = {
      auto_points: 0,
      auto_max_points: 0,
      pending_external_points: 0,
      pending_max_points: 0,
      form_max_points: Number((policy.honesty_accounting as Record<string, unknown>).form_max_points),
      unblended: true,
      slots_total: slots.length,
      slots_graded: 0,
      slots_incomplete: 0,
      slots_invalid: 0,
      slots_unattempted: 0,
      slots_manual_pending: 0
    };
    let slotPoints = 0;
    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      totals.auto_points += slot.task.auto_points;
      totals.auto_max_points += slot.task.auto_max_points;
      totals.pending_external_points += slot.task.pending_points;
      totals.pending_max_points += slot.task.pending_max_points;
      slotPoints += slot.slot_points;
      if (slot.state === STATE_GRADED) { totals.slots_graded += 1; }
      else if (slot.state === STATE_INCOMPLETE) { totals.slots_incomplete += 1; }
      else if (slot.state === STATE_INVALID) { totals.slots_invalid += 1; }
      else if (slot.state === STATE_UNATTEMPTED) { totals.slots_unattempted += 1; }
      else if (slot.state === STATE_MANUAL_PENDING) { totals.slots_manual_pending += 1; }
    }
    if (slotPoints !== totals.form_max_points) {
      return fail('E_GRADING_BINDING_POINTS', 'Formas slotu punktu summa neatbilst politikas form_max_points.', {
        slot_points: slotPoints, form_max_points: totals.form_max_points
      });
    }
    if (totals.auto_max_points + totals.pending_max_points !== totals.form_max_points) {
      return fail('E_GRADING_BINDING_POINTS', 'Auto un pending maksimumi nesaskaita formas maksimumu.', {
        auto_max_points: totals.auto_max_points,
        pending_max_points: totals.pending_max_points,
        form_max_points: totals.form_max_points,
        conflict_ref: (policy.binding_rule as Record<string, unknown>).conflict_ref
      });
    }
    const autoSum = totals.auto_points;
    const pendingSum = totals.pending_external_points;
    if (autoSum > totals.auto_max_points || pendingSum > totals.pending_max_points) {
      return fail('E_GRADING_BINDING_POINTS', 'Kopsummas pārsniedz savus maksimumus.', {
        auto_points: autoSum, auto_max_points: totals.auto_max_points,
        pending_external_points: pendingSum, pending_max_points: totals.pending_max_points
      });
    }

    const normalizedBindings: Array<Record<string, unknown>> = [];
    for (let i = 0; i < plans.length; i += 1) {
      const bound = bySlot[plans[i].slot_id];
      const entry: Record<string, unknown> = {
        slot_id: bound.slot_id,
        type_id: bound.type_id,
        instance_id: bound.instance_id
      };
      if (bound.figure_id !== null) { entry.figure_id = bound.figure_id; }
      normalizedBindings.push(entry);
    }

    const sessionBlock = {
      session_id: record.session_id,
      form_id: record.form_id,
      state: record.state,
      started_at_ms: record.started_at_ms,
      finished_at_ms: record.finished_at_ms,
      elapsed_ms: record.elapsed_ms,
      flags: (record.flags as string[]).slice(),
      unanswered_slot_ids: (record.unanswered_slot_ids as string[]).slice(),
      remediation_slot_ids: (record.remediation_slot_ids as string[]).slice(),
      transition_count: (record.transitions as unknown[]).length,
      terminal_digest: digestValue(record)
    };

    const core: Record<string, unknown> = {
      schema_version: SCHEMA_VERSION,
      owner: RECORD_OWNER,
      record_kind: RECORD_KIND,
      session: sessionBlock,
      grading: {
        policy_digest: loaded.digest,
        classification_digest: null,
        binding: {
          source: ctx.bindingSource,
          binding_digest: digestValue(normalizedBindings)
        },
        oracle: {
          oracle_version: ctx.oracle.oracle_version,
          oracle_digest: ctx.oracle.oracle_digest,
          conventions_digest: ctx.oracle.conventions_digest
        }
      },
      slots: slots,
      totals: totals,
      feedback: null
    };
    core.digest = digestOf(core);
    return sortedValue(core) as Record<string, unknown>;
  }

  /**
   * Grade one bounded practice record against its slot bindings using the exact
   * same N22 completion gate, N17/N18/N19 engine dispatch, and N23 rubric policy.
   */
  function gradePracticeRecord(
    practiceRecord: unknown,
    bindings: unknown,
    context: unknown
  ): Record<string, unknown> {
    const ctx = requireContext(context);
    const loaded = isObject(ctx.gradingPolicy)
      ? { policy: ctx.gradingPolicy as Record<string, unknown>, digest: digestValue(ctx.gradingPolicy) }
      : loadPolicy(ctx.doc);
    const policy = loaded.policy;
    const terminalStates = (ctx.examPolicy as Record<string, any>).session_contract
      && Array.isArray((ctx.examPolicy as Record<string, any>).session_contract.terminal_states)
      ? ((ctx.examPolicy as Record<string, any>).session_contract.terminal_states as string[])
      : [];
    if (terminalStates.length === 0) {
      return fail('E_GRADING_CONTEXT', 'Eksāmena politikā nav deklarētu galīgo stāvokļu.', {
        missing: ['examPolicy.session_contract.terminal_states']
      });
    }
    const record = requireTerminalRecord(practiceRecord, terminalStates);
    const rawSlots = Array.isArray(record.slots) ? record.slots : [];
    const plans: SlotPlan[] = [];
    for (let i = 0; i < rawSlots.length; i += 1) {
      const s = rawSlots[i];
      if (!isObject(s) || !isText(s.slot_id) || typeof s.points !== 'number') {
        return fail('E_GRADING_POLICY_INVALID', 'Prakses slota plāns nav derīgs.', { index: i });
      }
      plans.push({ slot_id: s.slot_id, topic: Number(s.topic), points: Number(s.points) });
    }
    if (plans.length === 0) {
      return fail('E_GRADING_POLICY_INVALID', 'Prakses ierakstā nav neviena slota.', {});
    }
    const answers = indexAnswers(record, plans);
    const bySlot = indexBindings(bindings, plans, ctx.bank);
    const responseTypes = resolveResponseTypes(ctx);

    const slots: SlotRecord[] = [];
    for (let i = 0; i < plans.length; i += 1) {
      const plan = plans[i];
      const bound = bySlot[plan.slot_id];
      const answer = has(answers as Record<string, unknown>, plan.slot_id) ? answers[plan.slot_id] : null;
      slots.push(gradeSlot(plan, bound, answer, ctx, policy, responseTypes));
    }

    const totals = {
      auto_points: 0,
      auto_max_points: 0,
      pending_external_points: 0,
      pending_max_points: 0,
      form_max_points: 0,
      unblended: true,
      slots_total: slots.length,
      slots_graded: 0,
      slots_incomplete: 0,
      slots_invalid: 0,
      slots_unattempted: 0,
      slots_manual_pending: 0
    };
    let slotPoints = 0;
    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      totals.auto_points += slot.task.auto_points;
      totals.auto_max_points += slot.task.auto_max_points;
      totals.pending_external_points += slot.task.pending_points;
      totals.pending_max_points += slot.task.pending_max_points;
      slotPoints += slot.slot_points;
      if (slot.state === STATE_GRADED) { totals.slots_graded += 1; }
      else if (slot.state === STATE_INCOMPLETE) { totals.slots_incomplete += 1; }
      else if (slot.state === STATE_INVALID) { totals.slots_invalid += 1; }
      else if (slot.state === STATE_UNATTEMPTED) { totals.slots_unattempted += 1; }
      else if (slot.state === STATE_MANUAL_PENDING) { totals.slots_manual_pending += 1; }
    }
    totals.form_max_points = slotPoints;
    if (totals.auto_max_points + totals.pending_max_points !== totals.form_max_points) {
      return fail('E_GRADING_BINDING_POINTS', 'Auto un pending maksimumi nesaskaita prakses maksimumu.', {
        auto_max_points: totals.auto_max_points,
        pending_max_points: totals.pending_max_points,
        form_max_points: totals.form_max_points,
        conflict_ref: (policy.binding_rule as Record<string, unknown>).conflict_ref
      });
    }

    const normalizedBindings: Array<Record<string, unknown>> = [];
    for (let i = 0; i < plans.length; i += 1) {
      const bound = bySlot[plans[i].slot_id];
      const entry: Record<string, unknown> = {
        slot_id: bound.slot_id,
        type_id: bound.type_id,
        instance_id: bound.instance_id
      };
      if (bound.figure_id !== null) { entry.figure_id = bound.figure_id; }
      normalizedBindings.push(entry);
    }

    const sessionBlock = {
      session_id: record.session_id,
      form_id: record.form_id,
      state: record.state,
      started_at_ms: record.started_at_ms,
      finished_at_ms: record.finished_at_ms,
      elapsed_ms: record.elapsed_ms,
      flags: (record.flags as string[]).slice(),
      unanswered_slot_ids: (record.unanswered_slot_ids as string[]).slice(),
      remediation_slot_ids: (record.remediation_slot_ids as string[]).slice(),
      transition_count: (record.transitions as unknown[]).length,
      terminal_digest: digestValue(record)
    };

    const core: Record<string, unknown> = {
      schema_version: SCHEMA_VERSION,
      owner: RECORD_OWNER,
      record_kind: RECORD_KIND,
      session: sessionBlock,
      grading: {
        policy_digest: loaded.digest,
        classification_digest: null,
        binding: {
          source: ctx.bindingSource,
          binding_digest: digestValue(normalizedBindings)
        },
        oracle: {
          oracle_version: ctx.oracle.oracle_version,
          oracle_digest: ctx.oracle.oracle_digest,
          conventions_digest: ctx.oracle.conventions_digest
        }
      },
      slots: slots,
      totals: totals,
      feedback: null
    };
    core.digest = digestOf(core);
    return sortedValue(core) as Record<string, unknown>;
  }

  /* -------------------------------------------------------------- assembly */

  function composeGradedRecord(
    core: unknown,
    feedbackRecord: unknown
  ): Record<string, unknown> {
    if (!isObject(core) || core.record_kind !== RECORD_KIND || !Array.isArray(core.slots)) {
      return fail('E_GRADING_SCHEMA', 'Pamata ieraksts nav vērtēšanas ieraksts.', {});
    }
    if (!isObject(feedbackRecord) || feedbackRecord.record_kind !== FEEDBACK_KIND) {
      return fail('E_GRADING_SCHEMA', 'Atsauksmes ieraksts nav feedback-record.', {
        record_kind: isObject(feedbackRecord) ? feedbackRecord.record_kind : null
      });
    }
    if (!isText(feedbackRecord.classification_digest) || feedbackRecord.classification_digest === '') {
      return fail('E_GRADING_SCHEMA', 'Atsauksmes ierakstam nav classification_digest.', {});
    }
    if (isText(core.digest) && core.digest !== '' && digestOf(core) !== core.digest) {
      return fail('E_GRADING_SCHEMA', 'Pamata ieraksta digest neatbilst tā saturam.', {});
    }
    const full: Record<string, unknown> = copyJson(core);
    full.feedback = copyJson(feedbackRecord);
    const grading = full.grading as Record<string, unknown>;
    grading.classification_digest = feedbackRecord.classification_digest;
    delete full.digest;
    full.digest = digestOf(full);
    return sortedValue(full) as Record<string, unknown>;
  }

  /* ------------------------------------------------------------- analytics */

  function toAnalyticsEvents(fullRecord: unknown): Array<Record<string, unknown>> {
    if (!isObject(fullRecord) || fullRecord.record_kind !== RECORD_KIND) {
      return fail('E_GRADING_SCHEMA', 'Analītikai nepieciešams vērtēšanas ieraksts.', {});
    }
    if (!isText(fullRecord.digest) || fullRecord.digest === '') {
      return fail('E_GRADING_SCHEMA', 'Vērtēšanas ierakstam nav digest.', {});
    }
    if (digestOf(fullRecord) !== fullRecord.digest) {
      return fail('E_GRADING_SCHEMA', 'Vērtēšanas ieraksta digest neatbilst tā saturam.', {});
    }
    const digest = fullRecord.digest;
    const session = fullRecord.session as Record<string, unknown>;
    const totals = fullRecord.totals as Record<string, unknown>;
    const slots = fullRecord.slots as SlotRecord[];
    const feedback = isObject(fullRecord.feedback) ? fullRecord.feedback as Record<string, unknown> : null;
    const items = feedback && Array.isArray(feedback.items) ? feedback.items as Array<Record<string, unknown>> : [];

    let pendingCount = 0;
    for (let i = 0; i < slots.length; i += 1) {
      if (Number(slots[i].task.pending_points) > 0) { pendingCount += 1; }
    }
    const events: Array<Record<string, unknown>> = [{
      event: EVENT_SESSION,
      form_id: session.form_id,
      session_id: session.session_id,
      auto_score: totals.auto_points,
      pending_count: pendingCount,
      elapsed_ms: session.elapsed_ms,
      graded_digest: digest
    }];

    const bySlot: Record<string, Array<Record<string, unknown>>> = {};
    for (let i = 0; i < items.length; i += 1) {
      const item = items[i];
      if (!isObject(item) || !isText(item.slot_id)) { continue; }
      if (!has(bySlot, item.slot_id)) { bySlot[item.slot_id] = []; }
      bySlot[item.slot_id].push(item);
    }

    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      if (slot.state === STATE_UNATTEMPTED) { continue; }
      const verdicts: Array<Record<string, unknown>> = [];
      for (let c = 0; c < slot.criteria.length; c += 1) {
        const criterion = slot.criteria[c];
        verdicts.push({
          criterion_id: criterion.criterion_id,
          status: criterion.status,
          verdict_class: criterion.verdict_class,
          error_class: criterion.error_class
        });
      }
      events.push({
        event: EVENT_TASK,
        slot_id: slot.slot_id,
        topic: slot.topic,
        family_id: slot.family_id,
        type_id: slot.type_id,
        criterion_verdicts: verdicts,
        graded_digest: digest
      });
    }

    for (let i = 0; i < slots.length; i += 1) {
      const slot = slots[i];
      const needsRemediation = slot.state === STATE_INVALID || slot.state === STATE_INCOMPLETE ||
        (slot.state === STATE_GRADED && slot.verdict_class === 'incorrect');
      if (!needsRemediation) { continue; }
      const slotItems = has(bySlot, slot.slot_id) ? bySlot[slot.slot_id] : [];
      const conceptIds: string[] = [];
      const chainIds: string[] = [];
      let signatureId: string | null = null;
      for (let s = 0; s < slotItems.length; s += 1) {
        const item = slotItems[s];
        if (signatureId === null && isText(item.signature_id) && item.signature_id !== '') {
          signatureId = item.signature_id;
        }
        const remediation = isObject(item.remediation) ? item.remediation as Record<string, unknown> : null;
        if (!remediation) { continue; }
        if (Array.isArray(remediation.concept_ids)) {
          for (let c = 0; c < remediation.concept_ids.length; c += 1) {
            const id = remediation.concept_ids[c];
            if (isText(id) && id !== '') { pushUnique(conceptIds, id); }
          }
        }
        if (Array.isArray(remediation.chain_ids)) {
          for (let c = 0; c < remediation.chain_ids.length; c += 1) {
            const id = remediation.chain_ids[c];
            if (isText(id) && id !== '') { pushUnique(chainIds, id); }
          }
        }
      }
      if (conceptIds.length === 0 && chainIds.length === 0 && signatureId === null) { continue; }
      events.push({
        event: EVENT_REMEDIATION,
        slot_id: slot.slot_id,
        state: 'open',
        concept_ids: conceptIds,
        chain_ids: chainIds,
        signature_id: signatureId,
        graded_digest: digest
      });
    }
    return events;
  }

  /* ----------------------------------------------------------------- export */

  const api = {
    ISLAND_ID: ISLAND_ID,
    loadPolicy: loadPolicy,
    gradeTerminalRecord: gradeTerminalRecord,
    gradePracticeRecord: gradePracticeRecord,
    applyRubricPolicy: applyRubricPolicy,
    composeGradedRecord: composeGradedRecord,
    toAnalyticsEvents: toAnalyticsEvents,
    canonicalText: canonical,
    digestOf: digestOf,
    errors: ERRORS
  };

  root.SimGrading = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
