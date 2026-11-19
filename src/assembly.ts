/* N24 — Seeded, fair A/B/C form assembly and independent constraint checker.
 *
 * Implements:
 *  - Constraint-driven seeded draw over eligible (review-passed) bank items,
 *    using the frozen N05 SplitMix64 PRNG (SimPRNG).
 *  - Honest shortage policy: never relaxes constraints or substitutes
 *    unreviewed instances; emits a structured ShortageReport naming the
 *    binding constraint, topic/slot/type/family, and shortfall count.
 *  - Independent constraint checker (verifyFormManifest) sharing ZERO helper
 *    logic with assembleForm.
 *  - Seeded training option allowing ephemeral variants via SimVariantEngine.
 */
(function (this: void, root: any): void {
  'use strict';

  /* ---------------------------------------------------------------- types */

  interface SlotSpec {
    slot_id: string;
    topic: number;
    points: number;
    allowed_family_ids?: string[];
  }

  interface BankReview {
    accessibility?: string;
    calculation?: string;
    content?: string;
    source?: string;
  }

  interface BankInstance {
    question_id: string;
    family_id: string;
    variant_id: string;
    topic: number;
    type_id: string;
    type_ids?: string[];
    seed?: string;
    stem_lv?: string;
    rubric?: Array<{ points?: number }>;
    review?: BankReview;
    extensions?: {
      data?: {
        review_workflow?: { state?: string };
        ephemeral?: {
          attempt?: number;
          seed?: string;
          persisted?: boolean;
          frozen_bank_member?: boolean;
        };
      };
    };
  }

  interface AssembledSlot {
    slot_id: string;
    topic: number;
    points: number;
    instance_id: string;
    family_id: string;
    variant_id: string;
    type_id: string;
    type_ids: string[];
    rubric_points: number;
    ephemeral: boolean;
    figure_id?: string;
    ephemeral_meta?: {
      attempt: number;
      seed: string;
      persisted: boolean;
      frozen_bank_member: boolean;
    };
  }

  interface ConflictNotice {
    id: string;
    slot_id: string;
    instance_id: string;
    family_id: string;
    slot_points: number;
    rubric_points: number;
    note_lv: string;
  }

  interface FormManifest {
    schema_version: number;
    form_id: string;
    status: 'AVAILABLE';
    mode: 'frozen-exam-form' | 'seeded-training';
    form_seed: string;
    policy_id: string;
    prng_contract_digest: string;
    bank_digest: string;
    epistemic_label: 'PROPOSED';
    total_slots: number;
    total_points: number;
    topic_subtotals: Record<string, { slots: number; points: number }>;
    covered_types: string[];
    required_types_covered: boolean;
    slots: AssembledSlot[];
    conflicts: ConflictNotice[];
    manifest_digest: string;
  }

  interface ShortageReport {
    schema_version: number;
    form_id: string;
    status: 'SHORTAGE';
    disabled: true;
    binding_constraint: 'slot_family_eligibility' | 'required_type_coverage' | 'topic_slot_count';
    topic: number | null;
    slot_id: string | null;
    missing_family: string | null;
    missing_type: string | null;
    required_count: number;
    available_count: number;
    count_short: number;
    pending_review_families: string[];
    disabled_reason_lv: string;
  }

  interface AssemblySpec {
    slots: SlotSpec[];
    required_types: string[];
    topic_points: Record<string, number>;
    total_points: number;
  }

  interface AssembleOptions {
    form_id: string;
    seed: string | number;
    bank: BankInstance[];
    bank_digest: string;
    expected_bank_digest?: string;
    prng_contract_digest?: string;
    spec?: AssemblySpec;
    allow_ephemeral?: boolean;
    strict_rubric_points?: boolean;
    enforce_seed_range?: boolean;
    figure_map?: Record<string, string>;
    avoid_families_by_slot?: Record<string, string[]>;
    avoid_instances_by_slot?: Record<string, string[]>;
    sha256?: (text: string) => string;
  }

  interface CheckResult {
    status: 'PASS' | 'FAIL';
    checks: Record<string, boolean>;
    errors: string[];
    failure_reasons: Array<{ code: string; topic?: number; slot_id?: string; message: string }>;
  }

  /* ------------------------------------------------------------ constants */

  const POLICY_ID = 'splitmix64-u64-v1';
  const N24_SEED_MIN = 100000;
  const N24_SEED_MAX = 199999;
  const TRAINING_SEED_MIN = 101000;
  const TRAINING_SEED_MAX = 199999;

  const DEFAULT_FORM_SEEDS: Record<string, string> = {
    A: '100001',
    B: '100002',
    C: '100003',
  };

  const DEFAULT_REQUIRED_TYPES: string[] = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15'];

  const DEFAULT_TOPIC_POINTS: Record<string, number> = {
    '1': 10, '2': 12, '3': 20, '4': 15, '5': 16, '6': 15, '7': 12,
  };

  const DEFAULT_SLOTS: SlotSpec[] = [
    { slot_id: 'S1-1', topic: 1, points: 3, allowed_family_ids: ['FAM-1A', 'FAM-1B'] },
    { slot_id: 'S1-2', topic: 1, points: 3, allowed_family_ids: ['FAM-1C'] },
    { slot_id: 'S1-3', topic: 1, points: 4, allowed_family_ids: ['FAM-1D'] },
    { slot_id: 'S2-1', topic: 2, points: 4, allowed_family_ids: ['FAM-2A', 'FAM-2B'] },
    { slot_id: 'S2-2', topic: 2, points: 4, allowed_family_ids: ['FAM-2C'] },
    { slot_id: 'S2-3', topic: 2, points: 4, allowed_family_ids: ['FAM-2D'] },
    { slot_id: 'S3-1', topic: 3, points: 6, allowed_family_ids: ['FAM-3A', 'FAM-3B'] },
    { slot_id: 'S3-2', topic: 3, points: 6, allowed_family_ids: ['FAM-3C'] },
    { slot_id: 'S3-3', topic: 3, points: 8, allowed_family_ids: ['FAM-3D'] },
    { slot_id: 'S4-1', topic: 4, points: 4, allowed_family_ids: ['FAM-4A', 'FAM-4D'] },
    { slot_id: 'S4-2', topic: 4, points: 5, allowed_family_ids: ['FAM-4B'] },
    { slot_id: 'S4-3', topic: 4, points: 6, allowed_family_ids: ['FAM-4C'] },
    { slot_id: 'S5-1', topic: 5, points: 4, allowed_family_ids: ['FAM-5A', 'FAM-5D'] },
    { slot_id: 'S5-2', topic: 5, points: 6, allowed_family_ids: ['FAM-5B'] },
    { slot_id: 'S5-3', topic: 5, points: 6, allowed_family_ids: ['FAM-5C'] },
    { slot_id: 'S6-1', topic: 6, points: 4, allowed_family_ids: ['FAM-6A', 'FAM-6D'] },
    { slot_id: 'S6-2', topic: 6, points: 5, allowed_family_ids: ['FAM-6B'] },
    { slot_id: 'S6-3', topic: 6, points: 6, allowed_family_ids: ['FAM-6C'] },
    { slot_id: 'S7-1', topic: 7, points: 3, allowed_family_ids: ['FAM-7A'] },
    { slot_id: 'S7-2', topic: 7, points: 4, allowed_family_ids: ['FAM-7B'] },
    { slot_id: 'S7-3', topic: 7, points: 5, allowed_family_ids: ['FAM-7C', 'FAM-7D'] },
  ];

  const DEFAULT_Q11_FIGURES: Record<string, string> = {
    'COL1-2-2D-A-01': 'FIG-T2-PLOT-NACL-DENSITY',
    'COL1-2-2D-C-01': 'FIG-T2-PLOT-NACL-DENSITY',
    'COL1-5-5B-D-01': 'FIG-T5-LIN-FIRST',
    'COL1-7-7B-A-01': 'FIG-T67-CAL-MASTER',
  };

  /* --------------------------------------------------------------- errors */

  class AssemblyError extends Error {
    public readonly code: string;
    public readonly details: Record<string, unknown>;

    constructor(code: string, message: string, details?: Record<string, unknown>) {
      super('[' + code + '] ' + message);
      this.name = 'AssemblyError';
      this.code = code;
      this.details = details || {};
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, AssemblyError);
      } else {
        this.stack = new Error(this.message).stack;
      }
    }
  }

  function fail(code: string, message: string, details?: Record<string, unknown>): never {
    throw new AssemblyError(code, message, details);
  }

  /* -------------------------------------------------------------- helpers */

  function canonicalText(value: unknown): string {
    if (value === null || value === undefined) { return 'null'; }
    if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
    if (typeof value === 'number') {
      if (!Number.isFinite(value)) { fail('E_ASSEMBLY_CANONICAL', 'Bezgalīgs skaitlis nav atļauts.'); }
      return Object.is(value, -0) ? '0' : String(value);
    }
    if (typeof value === 'string') { return JSON.stringify(value); }
    if (Array.isArray(value)) {
      const parts: string[] = [];
      for (let i = 0; i < value.length; i += 1) {
        parts.push(canonicalText(value[i]));
      }
      return '[' + parts.join(',') + ']';
    }
    if (typeof value === 'object') {
      const record = value as Record<string, unknown>;
      const keys = Object.keys(record).filter(function (k: string): boolean {
        return record[k] !== undefined;
      }).sort();
      const parts: string[] = [];
      for (let i = 0; i < keys.length; i += 1) {
        parts.push(JSON.stringify(keys[i]) + ':' + canonicalText(record[keys[i]]));
      }
      return '{' + parts.join(',') + '}';
    }
    return 'null';
  }

  function computeSha256(text: string, customSha?: (t: string) => string): string {
    if (typeof customSha === 'function') { return customSha(text); }
    if (root.SimFigures && typeof root.SimFigures.sha256Utf8 === 'function') {
      return root.SimFigures.sha256Utf8(text);
    }
    /* Minimal FNV-1a-free fallback is NOT allowed to impersonate SHA-256;
     * callers without SimFigures must supply a sha256 function. */
    fail('E_ASSEMBLY_DIGEST_UNAVAILABLE', 'SHA-256 palīgs nav pieejams formu manifesta parakstam.');
  }

  function parseSeed(raw: string | number, minAllowed?: number, maxAllowed?: number): { seedNum: number; seedStr: string } {
    let num: number;
    if (typeof raw === 'number') {
      if (!Number.isSafeInteger(raw) || raw < 1) {
        fail('E_ASSEMBLY_SEED_INVALID', 'Sēklai jābūt pozitīvam veselam skaitlim.', { seed: raw });
      }
      num = raw;
    } else if (typeof raw === 'string' && /^[0-9]+$/.test(raw.trim())) {
      num = Number(raw.trim());
      if (!Number.isSafeInteger(num) || num < 1 || String(num) !== raw.trim()) {
        fail('E_ASSEMBLY_SEED_INVALID', 'Sēklas virkne nav derīgs drošs vesels skaitlis.', { seed: raw });
      }
    } else {
      fail('E_ASSEMBLY_SEED_INVALID', 'Nederīgs sēklas formāts.', { seed: raw });
    }
    if (minAllowed !== undefined && num < minAllowed) {
      fail('E_ASSEMBLY_SEED_INVALID', 'Sēkla ' + num + ' ir zem atļautā diapazona [' + minAllowed + ', ' + maxAllowed + '].', { seed: num });
    }
    if (maxAllowed !== undefined && num > maxAllowed) {
      fail('E_ASSEMBLY_SEED_INVALID', 'Sēkla ' + num + ' pārsniedz atļauto diapazonu [' + minAllowed + ', ' + maxAllowed + '].', { seed: num });
    }
    return { seedNum: num, seedStr: String(num) };
  }

  function defaultSpec(): AssemblySpec {
    return {
      slots: DEFAULT_SLOTS.map(function (s: SlotSpec): SlotSpec {
        return {
          slot_id: s.slot_id,
          topic: s.topic,
          points: s.points,
          allowed_family_ids: s.allowed_family_ids ? s.allowed_family_ids.slice() : undefined,
        };
      }),
      required_types: DEFAULT_REQUIRED_TYPES.slice(),
      topic_points: JSON.parse(JSON.stringify(DEFAULT_TOPIC_POINTS)) as Record<string, number>,
      total_points: 100,
    };
  }

  function instanceRubricPoints(inst: BankInstance): number {
    if (!Array.isArray(inst.rubric)) { return 0; }
    let total = 0;
    for (let i = 0; i < inst.rubric.length; i += 1) {
      total += Number(inst.rubric[i].points || 0);
    }
    return Math.round(total * 1000000) / 1000000;
  }

  function isReviewEligible(inst: BankInstance, allowEphemeral: boolean): boolean {
    if (!inst || typeof inst !== 'object') { return false; }
    const ephMeta = inst.extensions && inst.extensions.data ? inst.extensions.data.ephemeral : undefined;
    const isEph = Boolean((ephMeta && ephMeta.frozen_bank_member === false) || /-EPH-[0-9]+$/.test(String(inst.question_id || '')));
    if (isEph && !allowEphemeral) { return false; }
    const rev = inst.review;
    if (!rev || rev.accessibility !== 'passed' || rev.calculation !== 'passed' ||
        rev.content !== 'passed' || rev.source !== 'passed') {
      return false;
    }
    const wf = inst.extensions && inst.extensions.data ? inst.extensions.data.review_workflow : undefined;
    if (wf && wf.state !== 'accepted') { return false; }
    return true;
  }

  function instanceTypes(inst: BankInstance): string[] {
    const out: string[] = [];
    if (typeof inst.type_id === 'string' && inst.type_id) { out.push(inst.type_id); }
    if (Array.isArray(inst.type_ids)) {
      for (let i = 0; i < inst.type_ids.length; i += 1) {
        if (out.indexOf(inst.type_ids[i]) === -1) { out.push(inst.type_ids[i]); }
      }
    }
    return out;
  }

  function resolveFigureId(inst: BankInstance, figureMap: Record<string, string>): string | undefined {
    if (inst.type_id !== 'Q11') { return undefined; }
    if (figureMap[inst.question_id]) { return figureMap[inst.question_id]; }
    if (DEFAULT_Q11_FIGURES[inst.question_id]) { return DEFAULT_Q11_FIGURES[inst.question_id]; }
    if (inst.topic === 2) { return 'FIG-T2-PLOT-NACL-DENSITY'; }
    if (inst.topic === 5) { return 'FIG-T5-LIN-FIRST'; }
    if (inst.topic === 7) { return 'FIG-T67-CAL-MASTER'; }
    return undefined;
  }

  function buildShortage(
    formId: string,
    constraint: 'slot_family_eligibility' | 'required_type_coverage' | 'topic_slot_count',
    topic: number | null,
    slotId: string | null,
    missingFamily: string | null,
    missingType: string | null,
    requiredCount: number,
    availableCount: number,
    pendingFamilies: string[]
  ): ShortageReport {
    const sortedPending = pendingFamilies.slice().sort();
    const targetLabel = missingFamily || missingType || (topic !== null ? String(topic) + '. tēma' : '');
    const slotNote = slotId ? ', vieta ' + slotId : '';
    const countShort = Math.max(1, requiredCount - availableCount);
    const reason = sortedPending.length > 0
      ? formId + ' forma pagaidām nav pieejama: gaida recenziju (' + sortedPending.join(', ') + slotNote + ', iztrūkst ' + countShort + ').'
      : formId + ' forma pagaidām nav pieejama: nepietiek atbilstošu uzdevumu (' + targetLabel + slotNote + ', iztrūkst ' + countShort + ').';
    return {
      schema_version: 1,
      form_id: formId,
      status: 'SHORTAGE',
      disabled: true,
      binding_constraint: constraint,
      topic: topic,
      slot_id: slotId,
      missing_family: missingFamily,
      missing_type: missingType,
      required_count: requiredCount,
      available_count: availableCount,
      count_short: countShort,
      pending_review_families: sortedPending,
      disabled_reason_lv: reason,
    };
  }

  /* ------------------------------------------------------ assembly engine */

  function assembleForm(options: AssembleOptions):
    { status: 'AVAILABLE'; manifest: FormManifest } | { status: 'SHORTAGE'; shortage: ShortageReport } {
    if (!options || typeof options.bank_digest !== 'string' || options.bank_digest.trim() === '') {
      fail('E_ASSEMBLY_BANK_UNVERIFIED', 'Formu montāža apturēta: bankas integritātes zīmogs nav nodots vai banka nav verificēta.', {
        form_id: options ? options.form_id : null,
      });
    }
    if (options.expected_bank_digest && options.bank_digest !== options.expected_bank_digest) {
      fail('E_ASSEMBLY_BANK_UNVERIFIED', 'Formu montāža apturēta: bankas zīmogs ir novecojis vai nesakrīt ar verificēto banku.', {
        expected: options.expected_bank_digest,
        actual: options.bank_digest,
      });
    }
    if (!root.SimPRNG || typeof root.SimPRNG.createStream !== 'function') {
      fail('E_ASSEMBLY_PRNG_UNAVAILABLE', 'SimPRNG (SplitMix64) modulis nav ielādēts.');
    }

    const spec = options.spec || defaultSpec();
    const allowEphemeral = options.allow_ephemeral === true;
    const strictRubric = options.strict_rubric_points === true;
    const enforceRange = options.enforce_seed_range === true;
    const parsedSeed = parseSeed(
      options.seed,
      enforceRange ? N24_SEED_MIN : undefined,
      enforceRange ? N24_SEED_MAX : undefined
    );
    const stream = root.SimPRNG.createStream(parsedSeed.seedNum);
    const figureMap = options.figure_map || DEFAULT_Q11_FIGURES;
    const avoidFamiliesBySlot = options.avoid_families_by_slot || {};
    const avoidInstancesBySlot = options.avoid_instances_by_slot || {};

    /* 1. Filter bank to strictly eligible instances, sorted canonically. */
    const rawBank = Array.isArray(options.bank) ? options.bank.slice() : [];
    rawBank.sort(function (a: BankInstance, b: BankInstance): number {
      return a.question_id < b.question_id ? -1 : (a.question_id > b.question_id ? 1 : 0);
    });

    const eligibleByFamily: Record<string, BankInstance[]> = {};
    const pendingFamiliesMap: Record<string, boolean> = {};
    const allFamiliesInTopic: Record<number, string[]> = {};

    for (let i = 0; i < rawBank.length; i += 1) {
      const q = rawBank[i];
      if (!q || !q.family_id) { continue; }
      if (!allFamiliesInTopic[q.topic]) { allFamiliesInTopic[q.topic] = []; }
      if (allFamiliesInTopic[q.topic].indexOf(q.family_id) === -1) {
        allFamiliesInTopic[q.topic].push(q.family_id);
      }
      if (isReviewEligible(q, allowEphemeral)) {
        if (!eligibleByFamily[q.family_id]) { eligibleByFamily[q.family_id] = []; }
        eligibleByFamily[q.family_id].push(q);
      } else {
        pendingFamiliesMap[q.family_id] = true;
      }
    }

    /* 2. Group slots by topic in canonical order. */
    const slotsByTopic: Record<number, SlotSpec[]> = {};
    const topics: number[] = [];
    for (let i = 0; i < spec.slots.length; i += 1) {
      const slot = spec.slots[i];
      if (!slotsByTopic[slot.topic]) {
        slotsByTopic[slot.topic] = [];
        topics.push(slot.topic);
      }
      slotsByTopic[slot.topic].push(slot);
    }
    topics.sort(function (a: number, b: number): number { return a - b; });

    /* 3. Permute candidate families and instances per topic using SplitMix64. */
    const shuffledInstancesByFamily: Record<string, BankInstance[]> = {};
    const allFamiliesSorted = Object.keys(eligibleByFamily).sort();
    for (let i = 0; i < allFamiliesSorted.length; i += 1) {
      const fam = allFamiliesSorted[i];
      shuffledInstancesByFamily[fam] = stream.shuffle(eligibleByFamily[fam]);
    }

    const topicAssignments: Record<number, Array<{ slot: SlotSpec; family_id: string }>> = {};

    for (let tIdx = 0; tIdx < topics.length; tIdx += 1) {
      const topic = topics[tIdx];
      const topicSlots = slotsByTopic[topic];
      const topicFamilies = (allFamiliesInTopic[topic] || []).slice().sort();
      const eligibleTopicFamilies = topicFamilies.filter(function (f: string): boolean {
        return Array.isArray(eligibleByFamily[f]) && eligibleByFamily[f].length > 0;
      });

      if (eligibleTopicFamilies.length < topicSlots.length) {
        const pendingInTopic = topicFamilies.filter(function (f: string): boolean {
          return pendingFamiliesMap[f] === true && (!eligibleByFamily[f] || eligibleByFamily[f].length === 0);
        });
        return {
          status: 'SHORTAGE',
          shortage: buildShortage(
            options.form_id,
            'topic_slot_count',
            topic,
            topicSlots[0].slot_id,
            pendingInTopic[0] || null,
            null,
            topicSlots.length,
            eligibleTopicFamilies.length,
            pendingInTopic
          ),
        };
      }

      const shuffledTopicFamilies: string[] = stream.shuffle(eligibleTopicFamilies);

      /* Backtrack within the topic over the PRNG-shuffled family order. */
      const chosen: Array<{ slot: SlotSpec; family_id: string } | null> = new Array(topicSlots.length).fill(null);
      const usedFamilies: Record<string, boolean> = {};

      const assignSlot = function (slotIdx: number): boolean {
        if (slotIdx >= topicSlots.length) { return true; }
        const slot = topicSlots[slotIdx];
        const allowed = slot.allowed_family_ids;
        const avoidList = avoidFamiliesBySlot[slot.slot_id] || [];

        const candidates = shuffledTopicFamilies.filter(function (fam: string): boolean {
          if (usedFamilies[fam]) { return false; }
          if (allowed && allowed.indexOf(fam) === -1) { return false; }
          if (strictRubric) {
            const hasMatchingRubric = (shuffledInstancesByFamily[fam] || []).some(function (inst: BankInstance): boolean {
              return instanceRubricPoints(inst) === slot.points;
            });
            if (!hasMatchingRubric) { return false; }
          }
          return true;
        });

        /* Prefer families not in avoidList while keeping PRNG order inside each tier. */
        const preferred = candidates.filter(function (f: string): boolean { return avoidList.indexOf(f) === -1; });
        const fallback = candidates.filter(function (f: string): boolean { return avoidList.indexOf(f) !== -1; });
        const ordered = preferred.concat(fallback);

        for (let c = 0; c < ordered.length; c += 1) {
          const fam = ordered[c];
          usedFamilies[fam] = true;
          chosen[slotIdx] = { slot: slot, family_id: fam };
          if (assignSlot(slotIdx + 1)) { return true; }
          chosen[slotIdx] = null;
          delete usedFamilies[fam];
        }
        return false;
      };

      if (!assignSlot(0)) {
        /* Identify the first unsatisfied slot and its missing/pending families. */
        let failedSlot: SlotSpec = topicSlots[0];
        let missingFam: string | null = null;
        const pendingInSlot: string[] = [];
        for (let s = 0; s < topicSlots.length; s += 1) {
          const slot = topicSlots[s];
          const allowed = slot.allowed_family_ids || topicFamilies;
          const validFams = allowed.filter(function (fam: string): boolean {
            const list = eligibleByFamily[fam] || [];
            if (list.length === 0) { return false; }
            if (!strictRubric) { return true; }
            return list.some(function (inst: BankInstance): boolean {
              return instanceRubricPoints(inst) === slot.points;
            });
          });
          if (validFams.length === 0) {
            failedSlot = slot;
            missingFam = allowed[0] || null;
            for (let a = 0; a < allowed.length; a += 1) {
              if (pendingFamiliesMap[allowed[a]]) { pendingInSlot.push(allowed[a]); }
            }
            break;
          }
        }
        return {
          status: 'SHORTAGE',
          shortage: buildShortage(
            options.form_id,
            'slot_family_eligibility',
            topic,
            failedSlot.slot_id,
            missingFam,
            null,
            1,
            0,
            pendingInSlot
          ),
        };
      }

      topicAssignments[topic] = chosen as Array<{ slot: SlotSpec; family_id: string }>;
    }

    /* 4. Flatten slot assignments in canonical spec order and ensure every
     * required type is reachable among the chosen families (needed when a
     * flexible slot map drops a family that is the sole carrier of a type). */
    const orderedAssignments: Array<{ slot: SlotSpec; family_id: string }> = [];
    const assignmentBySlotId: Record<string, { slot: SlotSpec; family_id: string }> = {};
    for (let tIdx = 0; tIdx < topics.length; tIdx += 1) {
      const list = topicAssignments[topics[tIdx]];
      for (let i = 0; i < list.length; i += 1) {
        assignmentBySlotId[list[i].slot.slot_id] = list[i];
      }
    }
    for (let i = 0; i < spec.slots.length; i += 1) {
      orderedAssignments.push(assignmentBySlotId[spec.slots[i].slot_id]);
    }

    const familyHasType = function (fam: string, slotPts: number, typeId: string): boolean {
      const insts = shuffledInstancesByFamily[fam] || [];
      for (let k = 0; k < insts.length; k += 1) {
        if (strictRubric && instanceRubricPoints(insts[k]) !== slotPts) { continue; }
        if (instanceTypes(insts[k]).indexOf(typeId) !== -1) { return true; }
      }
      return false;
    };

    const canCoverAllRequired = function (assignments: Array<{ slot: SlotSpec; family_id: string }>): string[] {
      const missing: string[] = [];
      for (let r = 0; r < spec.required_types.length; r += 1) {
        const rt = spec.required_types[r];
        let found = false;
        for (let s = 0; s < assignments.length; s += 1) {
          if (familyHasType(assignments[s].family_id, assignments[s].slot.points, rt)) {
            found = true;
            break;
          }
        }
        if (!found) { missing.push(rt); }
      }
      return missing;
    };

    let missingInPool = canCoverAllRequired(orderedAssignments);
    let swapGuard = 0;
    while (missingInPool.length > 0 && swapGuard < 14) {
      swapGuard += 1;
      const needType = missingInPool[0];
      const usedSet: Record<string, boolean> = {};
      for (let s = 0; s < orderedAssignments.length; s += 1) { usedSet[orderedAssignments[s].family_id] = true; }
      let swapped = false;
      for (let s = 0; s < orderedAssignments.length && !swapped; s += 1) {
        const slot = orderedAssignments[s].slot;
        const topicFams = (allFamiliesInTopic[slot.topic] || []).filter(function (f: string): boolean {
          if (usedSet[f]) { return false; }
          if (!eligibleByFamily[f] || eligibleByFamily[f].length === 0) { return false; }
          if (slot.allowed_family_ids && slot.allowed_family_ids.indexOf(f) === -1) { return false; }
          return familyHasType(f, slot.points, needType);
        });
        for (let c = 0; c < topicFams.length; c += 1) {
          const prevFam = orderedAssignments[s].family_id;
          orderedAssignments[s] = { slot: slot, family_id: topicFams[c] };
          const nextMissing = canCoverAllRequired(orderedAssignments);
          if (nextMissing.length < missingInPool.length) {
            missingInPool = nextMissing;
            swapped = true;
            break;
          }
          orderedAssignments[s] = { slot: slot, family_id: prevFam };
        }
      }
      if (!swapped) { break; }
    }

    const pickedBySlot: BankInstance[] = [];
    for (let i = 0; i < orderedAssignments.length; i += 1) {
      const pair = orderedAssignments[i];
      const candidates = shuffledInstancesByFamily[pair.family_id].filter(function (inst: BankInstance): boolean {
        return !strictRubric || instanceRubricPoints(inst) === pair.slot.points;
      });
      const avoidInst = avoidInstancesBySlot[pair.slot.slot_id] || [];
      const preferred = candidates.filter(function (inst: BankInstance): boolean {
        return avoidInst.indexOf(inst.question_id) === -1;
      });
      const ordered = preferred.length > 0 ? preferred.concat(candidates.filter(function (inst: BankInstance): boolean {
        return avoidInst.indexOf(inst.question_id) !== -1;
      })) : candidates;
      pickedBySlot.push(ordered[0]);
    }

    /* 5. Satisfy required_types_per_form without violating any slot constraint. */
    const missingTypes = function (current: BankInstance[]): string[] {
      const present: Record<string, boolean> = {};
      for (let i = 0; i < current.length; i += 1) {
        const ts = instanceTypes(current[i]);
        for (let j = 0; j < ts.length; j += 1) { present[ts[j]] = true; }
      }
      return spec.required_types.filter(function (rt: string): boolean { return !present[rt]; });
    };

    const initialMissing = missingTypes(pickedBySlot);
    if (initialMissing.length > 0) {
      /* Backtracking repair with locked slots so placing one required type
       * may displace a duplicate/movable required type onto another slot. */
      const solveMissing = function (current: BankInstance[], missing: string[], locked: boolean[]): BankInstance[] | null {
        if (missing.length === 0) { return current; }
        const targetType = missing[0];
        const freshMoves: Array<{ s: number; inst: BankInstance }> = [];
        const fallbackMoves: Array<{ s: number; inst: BankInstance }> = [];
        for (let s = 0; s < orderedAssignments.length; s += 1) {
          if (locked[s]) { continue; }
          const pair = orderedAssignments[s];
          const avoidInst = avoidInstancesBySlot[pair.slot.slot_id] || [];
          const candidates = shuffledInstancesByFamily[pair.family_id].filter(function (inst: BankInstance): boolean {
            if (strictRubric && instanceRubricPoints(inst) !== pair.slot.points) { return false; }
            return instanceTypes(inst).indexOf(targetType) !== -1;
          });
          for (let c = 0; c < candidates.length; c += 1) {
            const inst = candidates[c];
            if (avoidInst.indexOf(inst.question_id) === -1) {
              freshMoves.push({ s: s, inst: inst });
            } else {
              fallbackMoves.push({ s: s, inst: inst });
            }
          }
        }
        const moves = freshMoves.concat(fallbackMoves);
        for (let m = 0; m < moves.length; m += 1) {
          const move = moves[m];
          const next = current.slice();
          next[move.s] = move.inst;
          const nextLocked = locked.slice();
          nextLocked[move.s] = true;
          const nextMissing = missingTypes(next);
          const solved = solveMissing(next, nextMissing, nextLocked);
          if (solved) { return solved; }
        }
        return null;
      };

      const initLocked = new Array(orderedAssignments.length).fill(false);
      const repaired = solveMissing(pickedBySlot, initialMissing, initLocked);
      if (!repaired) {
        const stillMissing = missingTypes(pickedBySlot);
        const targetType = stillMissing[0];
        const pendingWithType: string[] = [];
        for (let i = 0; i < rawBank.length; i += 1) {
          const q = rawBank[i];
          if (!isReviewEligible(q, allowEphemeral) && instanceTypes(q).indexOf(targetType) !== -1) {
            if (pendingWithType.indexOf(q.family_id) === -1) { pendingWithType.push(q.family_id); }
          }
        }
        return {
          status: 'SHORTAGE',
          shortage: buildShortage(
            options.form_id,
            'required_type_coverage',
            null,
            null,
            pendingWithType[0] || null,
            targetType,
            1,
            0,
            pendingWithType
          ),
        };
      }
      for (let i = 0; i < repaired.length; i += 1) { pickedBySlot[i] = repaired[i]; }
    }

    /* 6. Build manifest, record N23-C01 conflicts openly, and compute digest. */
    const slotsOut: AssembledSlot[] = [];
    const topicSubtotals: Record<string, { slots: number; points: number }> = {};
    const coveredSet: Record<string, boolean> = {};
    const conflicts: ConflictNotice[] = [];
    let totalPoints = 0;

    for (let i = 0; i < orderedAssignments.length; i += 1) {
      const slot = orderedAssignments[i].slot;
      const inst = pickedBySlot[i];
      const rubPts = instanceRubricPoints(inst);
      const figId = resolveFigureId(inst, figureMap);
      const tKey = String(slot.topic);
      if (!topicSubtotals[tKey]) { topicSubtotals[tKey] = { slots: 0, points: 0 }; }
      topicSubtotals[tKey].slots += 1;
      topicSubtotals[tKey].points += slot.points;
      totalPoints += slot.points;

      const ts = instanceTypes(inst);
      for (let j = 0; j < ts.length; j += 1) { coveredSet[ts[j]] = true; }

      const ephData = inst.extensions && inst.extensions.data ? inst.extensions.data.ephemeral : undefined;
      const isEph = Boolean((ephData && ephData.frozen_bank_member === false) || /-EPH-[0-9]+$/.test(inst.question_id));

      const slotEntry: AssembledSlot = {
        slot_id: slot.slot_id,
        topic: slot.topic,
        points: slot.points,
        instance_id: inst.question_id,
        family_id: inst.family_id,
        variant_id: inst.variant_id,
        type_id: inst.type_id,
        type_ids: ts.slice().sort(),
        rubric_points: rubPts,
        ephemeral: isEph,
      };
      if (figId) { slotEntry.figure_id = figId; }
      if (isEph && ephData) {
        slotEntry.ephemeral_meta = {
          attempt: Number(ephData.attempt || 0),
          seed: String(ephData.seed || ''),
          persisted: false,
          frozen_bank_member: false,
        };
      }
      slotsOut.push(slotEntry);

      if (rubPts !== slot.points) {
        conflicts.push({
          id: 'N23-C01',
          slot_id: slot.slot_id,
          instance_id: inst.question_id,
          family_id: inst.family_id,
          slot_points: slot.points,
          rubric_points: rubPts,
          note_lv: 'Slota punktu mērogs (' + slot.points + ') atšķiras no bankas instances rubrikas summas (' + rubPts + '); konflikts N23-C01 saglabāts redzams bez punktu pārmērošanas.',
        });
      }
    }

    const baseManifest = {
      schema_version: 1,
      form_id: options.form_id,
      status: 'AVAILABLE' as const,
      mode: allowEphemeral ? ('seeded-training' as const) : ('frozen-exam-form' as const),
      form_seed: parsedSeed.seedStr,
      policy_id: POLICY_ID,
      prng_contract_digest: String(options.prng_contract_digest || ''),
      bank_digest: options.bank_digest,
      epistemic_label: 'PROPOSED' as const,
      total_slots: slotsOut.length,
      total_points: totalPoints,
      topic_subtotals: topicSubtotals,
      covered_types: Object.keys(coveredSet).sort(),
      required_types_covered: spec.required_types.every(function (rt: string): boolean { return coveredSet[rt] === true; }),
      slots: slotsOut,
      conflicts: conflicts,
    };

    const digest = computeSha256(canonicalText(baseManifest), options.sha256);
    const manifest: FormManifest = {
      schema_version: baseManifest.schema_version,
      form_id: baseManifest.form_id,
      status: baseManifest.status,
      mode: baseManifest.mode,
      form_seed: baseManifest.form_seed,
      policy_id: baseManifest.policy_id,
      prng_contract_digest: baseManifest.prng_contract_digest,
      bank_digest: baseManifest.bank_digest,
      epistemic_label: baseManifest.epistemic_label,
      total_slots: baseManifest.total_slots,
      total_points: baseManifest.total_points,
      topic_subtotals: baseManifest.topic_subtotals,
      covered_types: baseManifest.covered_types,
      required_types_covered: baseManifest.required_types_covered,
      slots: baseManifest.slots,
      conflicts: baseManifest.conflicts,
      manifest_digest: digest,
    };

    const verification = verifyFormManifest(manifest, rawBank, spec, {
      allow_ephemeral: allowEphemeral,
      strict_rubric_points: strictRubric,
    });
    if (verification.status !== 'PASS') {
      fail('E_ASSEMBLY_CHECK_FAILED', 'Montētais manifests neizturēja neatkarīgo ierobežojumu pārbaudi: ' + verification.errors.join('; '), {
        form_id: options.form_id,
        errors: verification.errors,
      });
    }

    return { status: 'AVAILABLE', manifest: manifest };
  }

  /* -------------------------------------------- coordinated A/B/C set */

  function assembleFormSet(options: {
    bank: BankInstance[];
    bank_digest: string;
    expected_bank_digest?: string;
    prng_contract_digest?: string;
    seeds?: Record<string, string | number>;
    spec?: AssemblySpec;
    strict_rubric_points?: boolean;
    figure_map?: Record<string, string>;
    sha256?: (text: string) => string;
  }): {
    forms: Array<FormManifest | ShortageReport>;
    manifests_by_id: Record<string, FormManifest>;
    shortages: ShortageReport[];
  } {
    const seeds = options.seeds || DEFAULT_FORM_SEEDS;
    const formIds = ['A', 'B', 'C'];
    const usedFamiliesBySlot: Record<string, string[]> = {};
    const usedInstancesBySlot: Record<string, string[]> = {};
    const forms: Array<FormManifest | ShortageReport> = [];
    const manifestsById: Record<string, FormManifest> = {};
    const shortages: ShortageReport[] = [];

    for (let i = 0; i < formIds.length; i += 1) {
      const fid = formIds[i];
      const seed = seeds[fid] !== undefined ? seeds[fid] : DEFAULT_FORM_SEEDS[fid];
      const res = assembleForm({
        form_id: fid,
        seed: seed,
        bank: options.bank,
        bank_digest: options.bank_digest,
        expected_bank_digest: options.expected_bank_digest,
        prng_contract_digest: options.prng_contract_digest,
        spec: options.spec,
        allow_ephemeral: false,
        strict_rubric_points: options.strict_rubric_points,
        enforce_seed_range: true,
        figure_map: options.figure_map,
        avoid_families_by_slot: usedFamiliesBySlot,
        avoid_instances_by_slot: usedInstancesBySlot,
        sha256: options.sha256,
      });
      if (res.status === 'AVAILABLE') {
        forms.push(res.manifest);
        manifestsById[fid] = res.manifest;
        for (let s = 0; s < res.manifest.slots.length; s += 1) {
          const sl = res.manifest.slots[s];
          if (!usedFamiliesBySlot[sl.slot_id]) { usedFamiliesBySlot[sl.slot_id] = []; }
          if (usedFamiliesBySlot[sl.slot_id].indexOf(sl.family_id) === -1) {
            usedFamiliesBySlot[sl.slot_id].push(sl.family_id);
          }
          if (!usedInstancesBySlot[sl.slot_id]) { usedInstancesBySlot[sl.slot_id] = []; }
          if (usedInstancesBySlot[sl.slot_id].indexOf(sl.instance_id) === -1) {
            usedInstancesBySlot[sl.slot_id].push(sl.instance_id);
          }
        }
      } else {
        forms.push(res.shortage);
        shortages.push(res.shortage);
      }
    }
    return { forms: forms, manifests_by_id: manifestsById, shortages: shortages };
  }

  /* ---------------------------------------------- seeded training draw */

  function assembleSeededTrainingForm(options: {
    seed: string | number;
    bank: BankInstance[];
    bank_digest: string;
    prng_contract_digest?: string;
    spec?: AssemblySpec;
    variant_engine?: any;
    frozen_seeds?: string[] | Record<string, boolean>;
    ephemeral_slot_limit?: number;
    figure_map?: Record<string, string>;
    sha256?: (text: string) => string;
  }): {
    status: 'AVAILABLE';
    manifest: FormManifest;
    instances_by_id: Record<string, BankInstance>;
    ephemeral_count: number;
  } | { status: 'SHORTAGE'; shortage: ShortageReport } {
    const parsed = parseSeed(options.seed, TRAINING_SEED_MIN, TRAINING_SEED_MAX);
    const baseResult = assembleForm({
      form_id: 'SEEDED-' + parsed.seedStr,
      seed: parsed.seedNum,
      bank: options.bank,
      bank_digest: options.bank_digest,
      prng_contract_digest: options.prng_contract_digest,
      spec: options.spec,
      allow_ephemeral: true,
      enforce_seed_range: false,
      figure_map: options.figure_map,
      sha256: options.sha256,
    });
    if (baseResult.status !== 'AVAILABLE') {
      return baseResult;
    }

    const bankById: Record<string, BankInstance> = {};
    for (let i = 0; i < options.bank.length; i += 1) {
      bankById[options.bank[i].question_id] = options.bank[i];
    }

    const engine = options.variant_engine || root.SimVariantEngine;
    const canEphemeral = Boolean(engine && typeof engine.isLoaded === 'function' && engine.isLoaded() &&
      typeof engine.instantiateEphemeral === 'function');

    const manifest = baseResult.manifest;
    const instancesById: Record<string, BankInstance> = {};
    const frozenSeeds = options.frozen_seeds || [];
    const ephLimit = options.ephemeral_slot_limit === undefined ? 21 : options.ephemeral_slot_limit;
    let ephemeralCount = 0;

    if (canEphemeral && ephLimit > 0) {
      const ephBank: BankInstance[] = options.bank.slice();
      for (let i = 0; i < manifest.slots.length; i += 1) {
        const slot = manifest.slots[i];
        const orig = bankById[slot.instance_id];
        if (!orig) { continue; }
        let replaced = orig;
        if (ephemeralCount < ephLimit) {
          try {
            const candidate = engine.instantiateEphemeral(slot.family_id, slot.variant_id, i, frozenSeeds) as BankInstance;
            if (candidate && candidate.type_id === slot.type_id && candidate.topic === slot.topic) {
              replaced = candidate;
              slot.instance_id = candidate.question_id;
              slot.ephemeral = true;
              const eph = candidate.extensions && candidate.extensions.data ? candidate.extensions.data.ephemeral : undefined;
              slot.ephemeral_meta = {
                attempt: eph && eph.attempt !== undefined ? Number(eph.attempt) : i,
                seed: eph && eph.seed ? String(eph.seed) : '',
                persisted: false,
                frozen_bank_member: false,
              };
              ephBank.push(candidate);
              ephemeralCount += 1;
            }
          } catch (_err) {
            /* Keep the eligible bank instance when template instantiation is unavailable. */
          }
        }
        instancesById[slot.instance_id] = replaced;
      }

      const recomputedDigest = computeSha256(canonicalText({
        schema_version: manifest.schema_version,
        form_id: manifest.form_id,
        status: manifest.status,
        mode: manifest.mode,
        form_seed: manifest.form_seed,
        policy_id: manifest.policy_id,
        prng_contract_digest: manifest.prng_contract_digest,
        bank_digest: manifest.bank_digest,
        epistemic_label: manifest.epistemic_label,
        total_slots: manifest.total_slots,
        total_points: manifest.total_points,
        topic_subtotals: manifest.topic_subtotals,
        covered_types: manifest.covered_types,
        required_types_covered: manifest.required_types_covered,
        slots: manifest.slots,
        conflicts: manifest.conflicts,
      }), options.sha256);
      manifest.manifest_digest = recomputedDigest;

      const check = verifyFormManifest(manifest, ephBank, options.spec || defaultSpec(), { allow_ephemeral: true });
      if (check.status !== 'PASS') {
        fail('E_ASSEMBLY_CHECK_FAILED', 'Treniņa sēklotais manifests neizturēja pārbaudi: ' + check.errors.join('; '), {
          errors: check.errors,
        });
      }
    } else {
      for (let i = 0; i < manifest.slots.length; i += 1) {
        const slot = manifest.slots[i];
        if (bankById[slot.instance_id]) { instancesById[slot.instance_id] = bankById[slot.instance_id]; }
      }
    }

    return {
      status: 'AVAILABLE',
      manifest: manifest,
      instances_by_id: instancesById,
      ephemeral_count: ephemeralCount,
    };
  }

  /* ------------------------------------- INDEPENDENT CONSTRAINT CHECKER */
  /* Shares ZERO helper functions with assembleForm (N05 oracle discipline). */

  function verifyFormManifest(
    manifest: FormManifest,
    bank: BankInstance[],
    specInput?: AssemblySpec,
    options?: { allow_ephemeral?: boolean; strict_rubric_points?: boolean }
  ): CheckResult {
    const errors: string[] = [];
    const reasons: Array<{ code: string; topic?: number; slot_id?: string; message: string }> = [];
    const allowEph = Boolean(options && options.allow_ephemeral === true);
    const strictRubric = Boolean(options && options.strict_rubric_points === true);

    const specSlots: SlotSpec[] = specInput && Array.isArray(specInput.slots) ? specInput.slots : DEFAULT_SLOTS;
    const reqTypes: string[] = specInput && Array.isArray(specInput.required_types) ? specInput.required_types : DEFAULT_REQUIRED_TYPES;
    const expectedTopicPts: Record<string, number> = specInput && specInput.topic_points ? specInput.topic_points : DEFAULT_TOPIC_POINTS;
    const expectedTotalPts: number = specInput && typeof specInput.total_points === 'number' ? specInput.total_points : 100;

    const recordFail = function (checkKey: string, code: string, message: string, topic?: number, slotId?: string): void {
      checks[checkKey] = false;
      errors.push(message);
      reasons.push({ code: code, topic: topic, slot_id: slotId, message: message });
    };

    const checks: Record<string, boolean> = {
      slot_count: true,
      slot_order: true,
      eligibility: true,
      topic_and_slot_constraints: true,
      per_topic_points_and_counts: true,
      total_points: true,
      family_uniqueness: true,
      instance_uniqueness: true,
      required_types_coverage: true,
      q11_figure_binding: true,
    };

    if (!manifest || !Array.isArray(manifest.slots)) {
      recordFail('slot_count', 'E_CHECK_MANIFEST', 'Manifestam trūkst slots masīva.');
      return { status: 'FAIL', checks: checks, errors: errors, failure_reasons: reasons };
    }

    /* Local independent bank index by question_id. */
    const bankIndex: Record<string, BankInstance> = {};
    if (Array.isArray(bank)) {
      for (let b = 0; b < bank.length; b += 1) {
        const item = bank[b];
        if (item && typeof item.question_id === 'string') {
          bankIndex[item.question_id] = item;
        }
      }
    }

    /* 1. Slot count & order against spec. */
    if (manifest.slots.length !== specSlots.length) {
      /* Detect which topic has fewer slots than spec. */
      const actualPerTopic: Record<number, number> = {};
      const expectedPerTopic: Record<number, number> = {};
      for (let i = 0; i < specSlots.length; i += 1) {
        expectedPerTopic[specSlots[i].topic] = (expectedPerTopic[specSlots[i].topic] || 0) + 1;
      }
      for (let i = 0; i < manifest.slots.length; i += 1) {
        const tp = manifest.slots[i].topic;
        actualPerTopic[tp] = (actualPerTopic[tp] || 0) + 1;
      }
      let badTopic: number | undefined;
      const expTopics = Object.keys(expectedPerTopic);
      for (let i = 0; i < expTopics.length; i += 1) {
        const t = Number(expTopics[i]);
        if ((actualPerTopic[t] || 0) !== expectedPerTopic[t]) {
          badTopic = t;
          break;
        }
      }
      recordFail(
        'slot_count',
        'E_CHECK_SLOT_COUNT',
        'Uzdevumu vietu skaits ir ' + manifest.slots.length + ', bet jābūt ' + specSlots.length +
        (badTopic !== undefined ? ' (tēma ' + badTopic + ': ' + (actualPerTopic[badTopic] || 0) + '/' + expectedPerTopic[badTopic] + ').' : '.'),
        badTopic
      );
    }

    const specBySlotId: Record<string, SlotSpec> = {};
    for (let i = 0; i < specSlots.length; i += 1) {
      specBySlotId[specSlots[i].slot_id] = specSlots[i];
      const drawn = manifest.slots[i];
      if (!drawn || drawn.slot_id !== specSlots[i].slot_id) {
        checks.slot_order = false;
      }
    }
    if (!checks.slot_order) {
      errors.push('Uzdevumu vietu secība vai identifikatori neatbilst plāna vietām.');
      reasons.push({ code: 'E_CHECK_SLOT_ORDER', message: 'Uzdevumu vietu secība vai identifikatori neatbilst plāna vietām.' });
    }

    /* 2. Per-slot checks: eligibility, uniqueness, topic/points, Q11 figure, types. */
    const seenFamilies: Record<string, string> = {};
    const seenInstances: Record<string, string> = {};
    const topicCounts: Record<number, number> = {};
    const topicPoints: Record<number, number> = {};
    const seenTypes: Record<string, boolean> = {};
    let totalPoints = 0;

    for (let i = 0; i < manifest.slots.length; i += 1) {
      const slot = manifest.slots[i];
      const plan = specBySlotId[slot.slot_id];
      const inst = bankIndex[slot.instance_id];

      if (!inst) {
        recordFail('eligibility', 'E_CHECK_INSTANCE_MISSING', 'Instance ' + slot.instance_id + ' nav atrasta bankā (vieta ' + slot.slot_id + ').', slot.topic, slot.slot_id);
        continue;
      }

      /* Independent review & ephemeral gate check. */
      const rev = inst.review;
      const reviewPassed = Boolean(rev && rev.accessibility === 'passed' && rev.calculation === 'passed' &&
        rev.content === 'passed' && rev.source === 'passed');
      const wfState = inst.extensions && inst.extensions.data && inst.extensions.data.review_workflow
        ? inst.extensions.data.review_workflow.state : 'accepted';
      const ephFlag = Boolean(slot.ephemeral || /-EPH-[0-9]+$/.test(inst.question_id) ||
        (inst.extensions && inst.extensions.data && inst.extensions.data.ephemeral && inst.extensions.data.ephemeral.frozen_bank_member === false));

      if (!reviewPassed || wfState !== 'accepted') {
        recordFail('eligibility', 'E_CHECK_UNREVIEWED', 'Instance ' + inst.question_id + ' nav pieņemtā recenzijas stāvoklī (vieta ' + slot.slot_id + ').', slot.topic, slot.slot_id);
      }
      if (ephFlag && !allowEph) {
        recordFail('eligibility', 'E_CHECK_EPHEMERAL_FORBIDDEN', 'Efemerā instance ' + inst.question_id + ' nav atļauta eksāmena formā (vieta ' + slot.slot_id + ').', slot.topic, slot.slot_id);
      }
      if (ephFlag && allowEph && slot.ephemeral !== true) {
        recordFail('eligibility', 'E_CHECK_EPHEMERAL_UNMARKED', 'Efemerā instance ' + inst.question_id + ' nav skaidri marķēta ar ephemeral=true.', slot.topic, slot.slot_id);
      }

      /* Topic, slot points, allowed families, strict rubric check. */
      if (!plan || inst.topic !== plan.topic || slot.topic !== plan.topic || slot.points !== plan.points) {
        recordFail('topic_and_slot_constraints', 'E_CHECK_SLOT_MISMATCH', 'Vieta ' + slot.slot_id + ' neatbilst plāna tēmai vai punktiem.', slot.topic, slot.slot_id);
      }
      if (plan && Array.isArray(plan.allowed_family_ids) && plan.allowed_family_ids.indexOf(inst.family_id) === -1) {
        recordFail('topic_and_slot_constraints', 'E_CHECK_FAMILY_NOT_ALLOWED', 'Saime ' + inst.family_id + ' nav atļauta vietā ' + slot.slot_id + '.', slot.topic, slot.slot_id);
      }
      if (strictRubric && plan) {
        let rSum = 0;
        if (Array.isArray(inst.rubric)) {
          for (let r = 0; r < inst.rubric.length; r += 1) { rSum += Number(inst.rubric[r].points || 0); }
        }
        if (Math.round(rSum * 1000000) / 1000000 !== plan.points) {
          recordFail('topic_and_slot_constraints', 'E_CHECK_RUBRIC_POINTS', 'Rubrikas punkti ' + rSum + ' != slota punkti ' + plan.points + ' vietā ' + slot.slot_id + '.', slot.topic, slot.slot_id);
        }
      }

      /* Family & instance uniqueness within the form. */
      if (seenFamilies[inst.family_id]) {
        recordFail('family_uniqueness', 'E_CHECK_DUPLICATE_FAMILY', 'Saime ' + inst.family_id + ' atkārtojas vietās ' + seenFamilies[inst.family_id] + ' un ' + slot.slot_id + '.', slot.topic, slot.slot_id);
      } else {
        seenFamilies[inst.family_id] = slot.slot_id;
      }
      if (seenInstances[inst.question_id]) {
        recordFail('instance_uniqueness', 'E_CHECK_DUPLICATE_INSTANCE', 'Instance ' + inst.question_id + ' atkārtojas vietā ' + slot.slot_id + '.', slot.topic, slot.slot_id);
      } else {
        seenInstances[inst.question_id] = slot.slot_id;
      }

      /* Q11 figure binding requirement (N23-C03). */
      if (inst.type_id === 'Q11' && (!slot.figure_id || String(slot.figure_id).trim() === '')) {
        recordFail('q11_figure_binding', 'E_CHECK_Q11_FIGURE', 'Q11 vietai ' + slot.slot_id + ' trūkst figure_id.', slot.topic, slot.slot_id);
      }

      topicCounts[slot.topic] = (topicCounts[slot.topic] || 0) + 1;
      topicPoints[slot.topic] = (topicPoints[slot.topic] || 0) + slot.points;
      totalPoints += slot.points;

      if (typeof inst.type_id === 'string') { seenTypes[inst.type_id] = true; }
      if (Array.isArray(inst.type_ids)) {
        for (let t = 0; t < inst.type_ids.length; t += 1) { seenTypes[inst.type_ids[t]] = true; }
      }
    }

    /* 3. Per-topic counts & points & total points. */
    const expectedTopicCounts: Record<string, number> = {};
    for (let i = 0; i < specSlots.length; i += 1) {
      const k = String(specSlots[i].topic);
      expectedTopicCounts[k] = (expectedTopicCounts[k] || 0) + 1;
    }
    const topicKeys = Object.keys(expectedTopicCounts).sort();
    for (let i = 0; i < topicKeys.length; i += 1) {
      const tk = topicKeys[i];
      const tNum = Number(tk);
      const gotCount = topicCounts[tNum] || 0;
      const wantCount = expectedTopicCounts[tk];
      if (gotCount !== wantCount) {
        recordFail('per_topic_points_and_counts', 'E_CHECK_TOPIC_SLOTS', 'Tēmai ' + tk + ' ir ' + gotCount + ' vietas, jābūt ' + wantCount + '.', tNum);
      }
      const gotPts = topicPoints[tNum] || 0;
      const wantPts = Number(expectedTopicPts[tk]);
      if (gotPts !== wantPts) {
        recordFail('per_topic_points_and_counts', 'E_CHECK_TOPIC_POINTS', 'Tēmai ' + tk + ' punktu summa ir ' + gotPts + ', jābūt ' + wantPts + '.', tNum);
      }
    }

    if (totalPoints !== expectedTotalPts) {
      recordFail('total_points', 'E_CHECK_TOTAL_POINTS', 'Kopējā punktu summa ir ' + totalPoints + ', jābūt ' + expectedTotalPts + '.');
    }

    /* 4. Required completed types coverage. */
    for (let i = 0; i < reqTypes.length; i += 1) {
      if (!seenTypes[reqTypes[i]]) {
        recordFail('required_types_coverage', 'E_CHECK_MISSING_TYPE', 'Formā trūkst obligātais uzdevuma tips ' + reqTypes[i] + '.');
      }
    }

    const ok = errors.length === 0;
    return { status: ok ? 'PASS' : 'FAIL', checks: checks, errors: errors, failure_reasons: reasons };
  }

  /* --------------------------------------------------- fairness sweep */

  function runFairnessSweep(options: {
    bank: BankInstance[];
    bank_digest: string;
    prng_contract_digest?: string;
    seeds?: string[];
    spec?: AssemblySpec;
    sha256?: (text: string) => string;
  }): {
    seed_count: number;
    forms_generated: number;
    families_seen: string[];
    families_missing: string[];
    tripled_family_slots_all: Array<{ seed: string; slot_id: string; family_id: string }>;
    tripled_family_slots_flexible: Array<{ seed: string; slot_id: string; family_id: string }>;
    tripled_instance_slots: Array<{ seed: string; slot_id: string; instance_id: string }>;
    all_checks_passed: boolean;
    digests_by_seed: Array<{ base_seed: string; forms: Record<string, string> }>;
  } {
    const seeds = options.seeds || [
      '100101', '100102', '100103', '100104', '100105',
      '100106', '100107', '100108', '100109', '100110',
    ];
    const spec = options.spec || defaultSpec();
    const flexSlots: Record<string, boolean> = {};
    for (let i = 0; i < spec.slots.length; i += 1) {
      const allowed = spec.slots[i].allowed_family_ids;
      if (!allowed || allowed.length > 1) { flexSlots[spec.slots[i].slot_id] = true; }
    }

    const allFamilies: Record<string, boolean> = {};
    for (let i = 0; i < options.bank.length; i += 1) {
      if (isReviewEligible(options.bank[i], false)) {
        allFamilies[options.bank[i].family_id] = true;
      }
    }
    const familiesSeen: Record<string, boolean> = {};
    const tripledAll: Array<{ seed: string; slot_id: string; family_id: string }> = [];
    const tripledFlex: Array<{ seed: string; slot_id: string; family_id: string }> = [];
    const tripledInst: Array<{ seed: string; slot_id: string; instance_id: string }> = [];
    const digestsBySeed: Array<{ base_seed: string; forms: Record<string, string> }> = [];
    let allPassed = true;
    let formsGenerated = 0;

    for (let s = 0; s < seeds.length; s += 1) {
      const baseNum = Number(seeds[s]);
      const triplet = assembleFormSet({
        bank: options.bank,
        bank_digest: options.bank_digest,
        prng_contract_digest: options.prng_contract_digest,
        seeds: { A: String(baseNum), B: String(baseNum + 100), C: String(baseNum + 200) },
        spec: spec,
        sha256: options.sha256,
      });
      if (triplet.shortages.length > 0) { allPassed = false; }
      const formDigests: Record<string, string> = {};
      const slotFams: Record<string, string[]> = {};
      const slotInsts: Record<string, string[]> = {};
      const fids = ['A', 'B', 'C'];
      for (let f = 0; f < fids.length; f += 1) {
        const m = triplet.manifests_by_id[fids[f]];
        if (!m) { continue; }
        formsGenerated += 1;
        formDigests[fids[f]] = m.manifest_digest;
        const chk = verifyFormManifest(m, options.bank, spec);
        if (chk.status !== 'PASS') { allPassed = false; }
        for (let k = 0; k < m.slots.length; k += 1) {
          const sl = m.slots[k];
          familiesSeen[sl.family_id] = true;
          if (!slotFams[sl.slot_id]) { slotFams[sl.slot_id] = []; }
          slotFams[sl.slot_id].push(sl.family_id);
          if (!slotInsts[sl.slot_id]) { slotInsts[sl.slot_id] = []; }
          slotInsts[sl.slot_id].push(sl.instance_id);
        }
      }
      const slotIds = Object.keys(slotFams).sort();
      for (let k = 0; k < slotIds.length; k += 1) {
        const sid = slotIds[k];
        const fams = slotFams[sid];
        if (fams.length === 3 && fams[0] === fams[1] && fams[1] === fams[2]) {
          tripledAll.push({ seed: String(baseNum), slot_id: sid, family_id: fams[0] });
          if (flexSlots[sid]) {
            tripledFlex.push({ seed: String(baseNum), slot_id: sid, family_id: fams[0] });
          }
        }
        const insts = slotInsts[sid];
        if (insts.length === 3 && insts[0] === insts[1] && insts[1] === insts[2]) {
          tripledInst.push({ seed: String(baseNum), slot_id: sid, instance_id: insts[0] });
        }
      }
      digestsBySeed.push({ base_seed: String(baseNum), forms: formDigests });
    }

    const expectedFams = Object.keys(allFamilies).sort();
    const seenList = Object.keys(familiesSeen).sort();
    const missingList = expectedFams.filter(function (f: string): boolean { return !familiesSeen[f]; });

    return {
      seed_count: seeds.length,
      forms_generated: formsGenerated,
      families_seen: seenList,
      families_missing: missingList,
      tripled_family_slots_all: tripledAll,
      tripled_family_slots_flexible: tripledFlex,
      tripled_instance_slots: tripledInst,
      all_checks_passed: allPassed,
      digests_by_seed: digestsBySeed,
    };
  }

  /* --------------------------------------------------------------- export */

  const api = {
    POLICY_ID: POLICY_ID,
    DEFAULT_FORM_SEEDS: DEFAULT_FORM_SEEDS,
    DEFAULT_REQUIRED_TYPES: DEFAULT_REQUIRED_TYPES,
    DEFAULT_TOPIC_POINTS: DEFAULT_TOPIC_POINTS,
    DEFAULT_SLOTS: DEFAULT_SLOTS,
    DEFAULT_Q11_FIGURES: DEFAULT_Q11_FIGURES,
    N24_SEED_RANGE: [N24_SEED_MIN, N24_SEED_MAX],
    TRAINING_SEED_RANGE: [TRAINING_SEED_MIN, TRAINING_SEED_MAX],
    AssemblyError: AssemblyError,
    canonicalText: canonicalText,
    assembleForm: assembleForm,
    assembleFormSet: assembleFormSet,
    assembleSeededTrainingForm: assembleSeededTrainingForm,
    verifyFormManifest: verifyFormManifest,
    runFairnessSweep: runFairnessSweep,
  };

  root.SimAssembly = api;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
