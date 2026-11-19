/* N19 method verdict engines — runtime twin of tools/method_engine.py.
 *
 * Grades the three non-numeric response types the N04 schema declares
 * (ordering, matching, sequence) and keeps the self-assessment path honestly
 * pending. Every comparison is structural: a step id, a position, a pair
 * identity. The module contains no similarity, keyword, tokenising or case
 * folding routine, and the only string operation it performs on learner text
 * is the blankness test on the self-assessment path.
 *
 * The module is intentionally NOT inlined into output/simulator.html: the
 * Section 1.3 runtime-JS ceiling had 83 bytes of headroom when N17 landed.
 * It is validated from src/ against the shipped islands; N31 must lazy-load
 * or re-budget before inlining it. See evidence/N19_VERIFICATION_RECORD.md.
 */
(function (root) {
'use strict';

var ORDERING = 'ordering';
var MATCHING = 'matching';
var SEQUENCE = 'sequence';
var SELF_ASSESSMENT = 'self_assessment';
var CANONICAL_DECIMALS = 6;

/* ------------------------------------------------------------- projection */
function canonicalNumber(value) {
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  return Number(value).toFixed(CANONICAL_DECIMALS);
}

function canonicalProjection(value) {
  if (value === null || value === undefined) { return 'null'; }
  if (typeof value === 'boolean') { return value ? 'true' : 'false'; }
  if (typeof value === 'number') { return canonicalNumber(value); }
  if (typeof value === 'string') { return JSON.stringify(value); }
  if (Array.isArray(value)) {
    var items = [];
    for (var i = 0; i < value.length; i += 1) { items.push(canonicalProjection(value[i])); }
    return '[' + items.join(',') + ']';
  }
  if (typeof value === 'object') {
    var keys = Object.keys(value).sort();
    var parts = [];
    for (var k = 0; k < keys.length; k += 1) {
      parts.push(JSON.stringify(keys[k]) + ':' + canonicalProjection(value[keys[k]]));
    }
    return '{' + parts.join(',') + '}';
  }
  return 'null';
}

/* A compact SHA-256 over UTF-8 text. */
var SHA_K = [
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
  var bytes = [];
  var encoded = unescape(encodeURIComponent(text));
  for (var i = 0; i < encoded.length; i += 1) { bytes.push(encoded.charCodeAt(i) & 0xff); }
  var bitLength = bytes.length * 8;
  bytes.push(0x80);
  while (bytes.length % 64 !== 56) { bytes.push(0); }
  var high = Math.floor(bitLength / 0x100000000);
  var low = bitLength >>> 0;
  bytes.push((high >>> 24) & 0xff, (high >>> 16) & 0xff, (high >>> 8) & 0xff, high & 0xff);
  bytes.push((low >>> 24) & 0xff, (low >>> 16) & 0xff, (low >>> 8) & 0xff, low & 0xff);
  var h = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
  var w = new Array(64);
  for (var block = 0; block < bytes.length; block += 64) {
    for (var t = 0; t < 16; t += 1) {
      w[t] = ((bytes[block + t * 4] << 24) | (bytes[block + t * 4 + 1] << 16) |
        (bytes[block + t * 4 + 2] << 8) | bytes[block + t * 4 + 3]) >>> 0;
    }
    for (var j = 16; j < 64; j += 1) {
      var g0 = (w[j - 15] >>> 7 | w[j - 15] << 25) ^ (w[j - 15] >>> 18 | w[j - 15] << 14) ^ (w[j - 15] >>> 3);
      var g1 = (w[j - 2] >>> 17 | w[j - 2] << 15) ^ (w[j - 2] >>> 19 | w[j - 2] << 13) ^ (w[j - 2] >>> 10);
      w[j] = (w[j - 16] + g0 + w[j - 7] + g1) >>> 0;
    }
    var a = h[0], b = h[1], c = h[2], d = h[3], e = h[4], f = h[5], g = h[6], hh = h[7];
    for (var m = 0; m < 64; m += 1) {
      var s1 = (e >>> 6 | e << 26) ^ (e >>> 11 | e << 21) ^ (e >>> 25 | e << 7);
      var ch = (e & f) ^ (~e & g);
      var temp1 = (hh + s1 + ch + SHA_K[m] + w[m]) >>> 0;
      var s0 = (a >>> 2 | a << 30) ^ (a >>> 13 | a << 19) ^ (a >>> 22 | a << 10);
      var maj = (a & b) ^ (a & c) ^ (b & c);
      var temp2 = (s0 + maj) >>> 0;
      hh = g; g = f; f = e; e = (d + temp1) >>> 0; d = c; c = b; b = a; a = (temp1 + temp2) >>> 0;
    }
    h[0] = (h[0] + a) >>> 0; h[1] = (h[1] + b) >>> 0; h[2] = (h[2] + c) >>> 0; h[3] = (h[3] + d) >>> 0;
    h[4] = (h[4] + e) >>> 0; h[5] = (h[5] + f) >>> 0; h[6] = (h[6] + g) >>> 0; h[7] = (h[7] + hh) >>> 0;
  }
  var hex = '';
  for (var z = 0; z < 8; z += 1) { hex += ('00000000' + h[z].toString(16)).slice(-8); }
  return hex;
}

function digestOf(value) { return sha256(canonicalProjection(value)); }

/* --------------------------------------------------------------- helpers */
function MethodError(code, message, detail) {
  var error = new Error(message);
  error.name = 'SimMethodError';
  error.code = code;
  error.detail = detail || {};
  return error;
}

/* The one and only text operation: is the recorded answer empty? */
function isBlank(text) {
  if (typeof text !== 'string') { return true; }
  var trimmed = text.replace(/^\s+|\s+$/g, '');
  return trimmed === '';
}

function copyObject(value) { return JSON.parse(JSON.stringify(value)); }

function pushUnique(list, seen, entry) {
  var key = String(entry.card_id) + '|' + String(entry.step_id);
  if (seen[key]) { return; }
  seen[key] = true;
  list.push(entry);
}

/* ---------------------------------------------------------------- engine */
function MethodEngine(contract, terms) {
  this.contract = contract || {};
  this.termsByKey = {};
  var list = (terms && terms.terms) || [];
  for (var i = 0; i < list.length; i += 1) { this.termsByKey[list[i].key] = list[i]; }
  this.signatureRegistry = {};
  var reg = this.contract.signature_registry || [];
  for (var r = 0; r < reg.length; r += 1) { this.signatureRegistry[reg[r].signature] = reg[r]; }
  this.feedbackCache = {};
}

MethodEngine.prototype.feedbackText = function (key) {
  if (!key) { return ''; }
  if (Object.prototype.hasOwnProperty.call(this.feedbackCache, key)) { return this.feedbackCache[key]; }
  var entry = this.termsByKey[key];
  if (!entry) { throw MethodError('E_METHOD_FEEDBACK_KEY', 'Feedback key ' + key + ' does not resolve in #sim-terms.', { key: key }); }
  var text = entry.text_lv || '';
  this.feedbackCache[key] = text;
  return text;
};

MethodEngine.prototype.signatureNote = function (signature) {
  if (!signature) { return ''; }
  var entry = this.signatureRegistry[signature];
  return entry ? (entry.note_lv || '') : '';
};

MethodEngine.prototype.splitRubric = function (rubric) {
  var auto = [];
  var pending = [];
  var items = rubric || [];
  for (var i = 0; i < items.length; i += 1) {
    var item = items[i];
    var binding = item.engine_binding;
    var isAuto = (item.grading === 'auto' || item.grading === 'mixed') &&
      binding !== 'self-assessed' && binding !== 'human-review';
    if (isAuto) { auto.push(item); } else { pending.push(item); }
  }
  return { auto: auto, pending: pending };
};

MethodEngine.prototype.criterion = function (id, status, points, maxPoints, pendingPoints) {
  return {
    criterion_id: id,
    status: status,
    awarded_points: points,
    pending_points: pendingPoints || 0,
    max_points: maxPoints
  };
};

MethodEngine.prototype.verdictClass = function (machinePoints, autoMax, hasPending, errorClass) {
  if (autoMax <= 0 && hasPending) {
    return errorClass === 'BLANK_RESPONSE' ? 'incorrect' : 'pending_self_assessment';
  }
  if (machinePoints === autoMax && autoMax > 0) { return hasPending ? 'auto_passed_pending_review' : 'correct'; }
  if (machinePoints > 0) { return 'partial'; }
  return 'incorrect';
};

MethodEngine.prototype.envelope = function (spec, verdictClass, errorClass, awarded, machinePoints,
  pendingPoints, maxPoints, diagnostics, submission) {
  var sorted = awarded.slice().sort(function (a, b) {
    if (a.criterion_id < b.criterion_id) { return -1; }
    if (a.criterion_id > b.criterion_id) { return 1; }
    return 0;
  });
  return {
    engine: spec.engine || 'N19',
    kind: spec.kind,
    verdict_class: verdictClass,
    error_class: errorClass,
    awarded_criteria: sorted,
    machine_checked_points: machinePoints,
    self_assessed_points: 0,
    human_reviewed_points: 0,
    pending_points: pendingPoints,
    max_points: maxPoints,
    diagnostics: diagnostics,
    replay: {
      spec_digest: digestOf(spec),
      submission_digest: digestOf(submission),
      source_ref: spec.source_ref === undefined ? null : spec.source_ref
    }
  };
};

/* --------------------------------------------------------- spec builders */
MethodEngine.prototype.specFromInstance = function (instance) {
  var payload = instance.payload || {};
  var rubric = instance.rubric || [];
  var signatures = instance.misconception_signatures || [];
  var defaultSignature = signatures.length ? signatures[0] : null;
  if (instance.payload_class === ORDERING) {
    var itemIds = [];
    var items = payload.items || [];
    for (var i = 0; i < items.length; i += 1) { itemIds.push(items[i].item_id); }
    var freeGroups = [];
    var rules = payload.partial_order_rules || [];
    for (var r = 0; r < rules.length; r += 1) {
      if (rules[r] && rules[r].type === 'free_order_group') {
        freeGroups.push((rules[r].item_ids || []).slice());
      }
    }
    return {
      kind: ORDERING, engine: 'N19-ordering', item_ids: itemIds,
      correct_order: (payload.correct_order || []).slice(), free_groups: freeGroups,
      step_meta: {}, default_signature: defaultSignature, rubric: rubric,
      source_ref: instance.question_id
    };
  }
  if (instance.payload_class === MATCHING) {
    var correctPairs = {};
    var pairs = payload.correct_pairs || [];
    for (var p = 0; p < pairs.length; p += 1) { correctPairs[pairs[p].left_id] = pairs[p].right_id; }
    return {
      kind: MATCHING, engine: 'N19-matching',
      left_items: payload.left_items || [], right_items: payload.right_items || [],
      correct_pairs: correctPairs, pair_meta: {}, default_signature: defaultSignature,
      rubric: rubric, source_ref: instance.question_id
    };
  }
  if (instance.payload_class === 'method') {
    return {
      kind: SELF_ASSESSMENT, engine: 'N19-self', rubric: rubric,
      default_signature: defaultSignature, source_ref: instance.question_id
    };
  }
  throw MethodError('E_METHOD_PAYLOAD_CLASS', 'Payload class ' + instance.payload_class + ' is not graded by the N19 engines.', {});
};

MethodEngine.prototype.specFromCard = function (card, kind, promptId, rubric) {
  var steps = card.steps || [];
  var itemIds = [];
  var stepMeta = {};
  var defaultSignature = null;
  for (var i = 0; i < steps.length; i += 1) {
    itemIds.push(steps[i].step_id);
    stepMeta[steps[i].step_id] = {
      signature: steps[i].misconception_signature,
      note_lv: steps[i].misconception_note_lv || '',
      feedback_key: steps[i].feedback_key
    };
    if (!defaultSignature && steps[i].misconception_signature) { defaultSignature = steps[i].misconception_signature; }
  }
  var freeGroups = [];
  var groups = card.free_order_groups || [];
  for (var g = 0; g < groups.length; g += 1) { freeGroups.push((groups[g].step_ids || []).slice()); }
  var base = {
    rubric: rubric || [], default_signature: defaultSignature,
    card_id: card.card_id, source_ref: card.card_id
  };
  if (kind === ORDERING) {
    base.kind = ORDERING; base.engine = 'N19-ordering';
    base.item_ids = itemIds; base.correct_order = itemIds.slice();
    base.free_groups = freeGroups; base.step_meta = stepMeta;
    return base;
  }
  if (kind === MATCHING) {
    if (!card.matching) { throw MethodError('E_METHOD_NO_MATCHING', 'Card ' + card.card_id + ' declares no matching exercise.', {}); }
    var correctPairs = {};
    var pairMeta = {};
    var mp = card.matching.correct_pairs || [];
    for (var p = 0; p < mp.length; p += 1) {
      correctPairs[mp[p].left_id] = mp[p].right_id;
      pairMeta[mp[p].left_id] = {
        signature: mp[p].misconception_signature,
        note_lv: mp[p].note_lv || '',
        feedback_key: mp[p].feedback_key
      };
    }
    base.kind = MATCHING; base.engine = 'N19-matching';
    base.left_items = card.matching.left_items; base.right_items = card.matching.right_items;
    base.correct_pairs = correctPairs; base.pair_meta = pairMeta;
    return base;
  }
  if (kind === SEQUENCE) {
    var prompts = card.sequence_prompts || [];
    var chosen = null;
    for (var s = 0; s < prompts.length; s += 1) {
      if (promptId === null || promptId === undefined || prompts[s].prompt_id === promptId) { chosen = prompts[s]; break; }
    }
    if (!chosen) { throw MethodError('E_METHOD_NO_PROMPT', 'Card ' + card.card_id + ' has no sequence prompt ' + promptId + '.', {}); }
    var distractors = {};
    var dl = chosen.distractors || [];
    for (var d = 0; d < dl.length; d += 1) {
      distractors[dl[d].step_id] = { signature: dl[d].misconception_signature, note_lv: dl[d].note_lv || '' };
    }
    base.kind = SEQUENCE; base.engine = 'N19-sequence';
    base.acceptance_step_ids = (chosen.acceptance_step_ids || []).slice();
    base.distractors = distractors; base.step_meta = stepMeta;
    base.prompt_id = chosen.prompt_id;
    base.source_ref = card.card_id + '#' + chosen.prompt_id;
    return base;
  }
  if (kind === SELF_ASSESSMENT) {
    base.kind = SELF_ASSESSMENT; base.engine = 'N19-self';
    return base;
  }
  throw MethodError('E_METHOD_KIND', 'Unsupported card engine kind ' + kind + '.', {});
};

/* ------------------------------------------------------------- ordering */
MethodEngine.prototype.stepDiagnostic = function (index, submittedId, expectedId, status, stepMeta, defaultSignature) {
  var meta = (submittedId ? stepMeta[submittedId] : null) || (expectedId ? stepMeta[expectedId] : null) || {};
  var signature = meta.signature || defaultSignature || null;
  var feedbackKey = meta.feedback_key || null;
  return {
    position: index,
    step_id: submittedId === undefined ? null : submittedId,
    expected_step_id: expectedId === undefined ? null : expectedId,
    status: status,
    misconception_signature: signature,
    misconception_note_lv: meta.note_lv || '',
    feedback_key: feedbackKey,
    feedback_text: this.feedbackText(feedbackKey)
  };
};

MethodEngine.prototype.gradeOrdering = function (spec, submission) {
  var split = this.splitRubric(spec.rubric);
  var correctOrder = spec.correct_order || [];
  var itemIds = spec.item_ids || [];
  var freeGroups = spec.free_groups || [];
  var stepMeta = spec.step_meta || {};
  var defaultSignature = spec.default_signature || null;

  var order = submission && submission.order;
  order = Array.isArray(order) ? order.slice() : [];

  var awarded = [];
  var pendingPoints = 0;
  var maxPoints = 0;
  for (var p = 0; p < split.pending.length; p += 1) {
    var item = split.pending[p];
    var points = Number(item.points || 0);
    maxPoints += points;
    pendingPoints += points;
    awarded.push(this.criterion(item.criterion_id, 'pending', 0, points, points));
  }

  var perStep = [];
  var signatures = [];
  var remediation = [];
  var remediationSeen = {};
  var wrongPositions = [];
  var errorClass = 'NONE';
  var matched = false;

  if (!order.length) {
    errorClass = 'BLANK_RESPONSE';
    matched = false;
  } else {
    var isPermutation = order.length === correctOrder.length && order.length === itemIds.length;
    if (isPermutation) {
      for (var q = 0; q < order.length; q += 1) {
        if (itemIds.indexOf(order[q]) === -1) { isPermutation = false; break; }
      }
    }
    if (isPermutation) {
      for (var w = 0; w < order.length; w += 1) {
        var seen = {};
        for (var x = 0; x < order.length; x += 1) {
          if (seen[order[x]]) { isPermutation = false; break; }
          seen[order[x]] = true;
        }
        if (!isPermutation) { break; }
      }
    }
    matched = isPermutation;
    var span = Math.max(correctOrder.length, order.length);
    for (var index = 0; index < span; index += 1) {
      var submittedId = index < order.length ? order[index] : null;
      var expectedId = index < correctOrder.length ? correctOrder[index] : null;
      var status = 'correct';
      if (submittedId === null) {
        status = 'missing_step';
      } else if (itemIds.indexOf(submittedId) === -1) {
        status = 'unknown_step';
      } else if (submittedId !== expectedId) {
        var sameGroup = false;
        for (var gi = 0; gi < freeGroups.length; gi += 1) {
          if (freeGroups[gi].indexOf(submittedId) !== -1 && freeGroups[gi].indexOf(expectedId) !== -1) {
            sameGroup = true; break;
          }
        }
        status = sameGroup ? 'free_order_equivalent' : 'misplaced';
      }
      if (status === 'correct' || status === 'free_order_equivalent') {
        perStep.push(this.stepDiagnostic(index, submittedId, expectedId, status, stepMeta, defaultSignature));
        continue;
      }
      matched = false;
      wrongPositions.push(index);
      var metas = [];
      if (submittedId) { metas.push(stepMeta[submittedId] || null); }
      if (expectedId) { metas.push(stepMeta[expectedId] || null); }
      for (var mi = 0; mi < metas.length; mi += 1) {
        var sig = (metas[mi] && metas[mi].signature) || defaultSignature;
        if (sig && signatures.indexOf(sig) === -1) { signatures.push(sig); }
      }
      perStep.push(this.stepDiagnostic(index, submittedId, expectedId, status, stepMeta, defaultSignature));
      var involved = submittedId ? [submittedId] : [];
      if (expectedId && involved.indexOf(expectedId) === -1) { involved.push(expectedId); }
      for (var ii = 0; ii < involved.length; ii += 1) {
        var meta = stepMeta[involved[ii]];
        if (!meta) { continue; }
        pushUnique(remediation, remediationSeen, {
          card_id: spec.card_id || null,
          step_id: involved[ii],
          misconception_signature: meta.signature || defaultSignature || null,
          note_lv: meta.note_lv || '',
          feedback_key: meta.feedback_key || null,
          feedback_text: this.feedbackText(meta.feedback_key)
        });
      }
    }
    if (!matched && errorClass === 'NONE') { errorClass = 'WRONG_ORDER'; }
  }

  var machinePoints = 0;
  var autoMax = 0;
  for (var ai = 0; ai < split.auto.length; ai += 1) {
    var autoItem = split.auto[ai];
    var autoPoints = Number(autoItem.points || 0);
    autoMax += autoPoints;
    var passed = matched;
    var criterionId = autoItem.criterion_id;
    if (criterionId.indexOf('_STEP_') !== -1 && perStep.length) {
      var stepId = criterionId.split('_STEP_')[1];
      var stepStatus = null;
      for (var si = 0; si < perStep.length; si += 1) {
        if (perStep[si].step_id === stepId) { stepStatus = perStep[si].status; break; }
      }
      passed = stepStatus === 'correct' || stepStatus === 'free_order_equivalent';
    }
    var awardedPoints = passed ? autoPoints : 0;
    machinePoints += awardedPoints;
    maxPoints += autoPoints;
    awarded.push(this.criterion(criterionId, passed ? 'awarded' : 'denied', awardedPoints, autoPoints));
  }

  var diagnostics = {
    per_step: perStep,
    wrong_positions: wrongPositions,
    signatures: signatures.slice().sort(),
    remediation: remediation
  };
  var verdictClass = this.verdictClass(machinePoints, autoMax, split.pending.length > 0, errorClass);
  return this.envelope(spec, verdictClass, errorClass, awarded, machinePoints, pendingPoints, maxPoints, diagnostics, submission);
};

/* ------------------------------------------------------------- matching */
MethodEngine.prototype.gradeMatching = function (spec, submission) {
  var split = this.splitRubric(spec.rubric);
  var correctPairs = spec.correct_pairs || {};
  var pairMeta = spec.pair_meta || {};
  var defaultSignature = spec.default_signature || null;
  var rightIds = {};
  var rights = spec.right_items || [];
  for (var ri = 0; ri < rights.length; ri += 1) { rightIds[rights[ri].id] = true; }

  var pairs = submission && submission.pairs;
  pairs = Array.isArray(pairs) ? pairs.slice() : [];

  var awarded = [];
  var pendingPoints = 0;
  var maxPoints = 0;
  for (var p = 0; p < split.pending.length; p += 1) {
    var item = split.pending[p];
    var points = Number(item.points || 0);
    maxPoints += points;
    pendingPoints += points;
    awarded.push(this.criterion(item.criterion_id, 'pending', 0, points, points));
  }

  var pairMap = {};
  var leftCounts = {};
  var rightCounts = {};
  for (var i = 0; i < pairs.length; i += 1) {
    var pair = pairs[i];
    if (!pair || typeof pair !== 'object') { continue; }
    var leftId = pair.left_id;
    if (leftId === undefined || leftId === null) { continue; }
    leftCounts[leftId] = (leftCounts[leftId] || 0) + 1;
    if (pair.right_id !== undefined && pair.right_id !== null) {
      rightCounts[pair.right_id] = (rightCounts[pair.right_id] || 0) + 1;
    }
    pairMap[leftId] = pair.right_id === undefined ? null : pair.right_id;
  }
  var duplicateLeft = false;
  for (var key in leftCounts) {
    if (Object.prototype.hasOwnProperty.call(leftCounts, key) && leftCounts[key] > 1) { duplicateLeft = true; }
  }

  var perPair = [];
  var signatures = [];
  var remediation = [];
  var remediationSeen = {};
  var pairStatuses = {};

  var leftKeys = Object.keys(correctPairs);
  for (var lk = 0; lk < leftKeys.length; lk += 1) {
    var lid = leftKeys[lk];
    var expectedRight = correctPairs[lid];
    var count = leftCounts[lid] || 0;
    var submittedRight = Object.prototype.hasOwnProperty.call(pairMap, lid) ? pairMap[lid] : null;
    var status;
    if (count === 0) {
      status = 'unmatched';
    } else if (count > 1) {
      status = 'repeated_left';
    } else if (!Object.prototype.hasOwnProperty.call(rightIds, submittedRight)) {
      status = 'unknown_right';
    } else if ((rightCounts[submittedRight] || 0) > 1) {
      status = 'repeated_right';
    } else if (submittedRight !== expectedRight) {
      status = 'wrong_pair';
    } else {
      status = 'correct';
    }
    pairStatuses[lid] = status;
    var meta = pairMeta[lid] || {};
    var signature = meta.signature || defaultSignature || null;
    if (status !== 'correct' && signature && signatures.indexOf(signature) === -1) { signatures.push(signature); }
    perPair.push({
      left_id: lid,
      submitted_right_id: submittedRight,
      expected_right_id: expectedRight,
      status: status,
      misconception_signature: signature,
      misconception_note_lv: meta.note_lv || '',
      feedback_key: meta.feedback_key || null,
      feedback_text: this.feedbackText(meta.feedback_key)
    });
    if (status !== 'correct' && meta.signature) {
      pushUnique(remediation, remediationSeen, {
        card_id: spec.card_id || null,
        step_id: lid,
        misconception_signature: signature,
        note_lv: meta.note_lv || '',
        feedback_key: meta.feedback_key || null,
        feedback_text: this.feedbackText(meta.feedback_key)
      });
    }
  }

  var allMatched = !duplicateLeft && pairs.length > 0;
  if (allMatched) {
    var expectedKeys = Object.keys(correctPairs);
    if (expectedKeys.length !== Object.keys(pairMap).length) { allMatched = false; }
    for (var ek = 0; ek < expectedKeys.length && allMatched; ek += 1) {
      if (pairMap[expectedKeys[ek]] !== correctPairs[expectedKeys[ek]]) { allMatched = false; }
    }
  }
  var errorClass = 'NONE';
  if (!pairs.length) {
    errorClass = 'BLANK_RESPONSE';
  } else if (!allMatched) {
    errorClass = 'WRONG_PAIRING';
  }

  var machinePoints = 0;
  var autoMax = 0;
  for (var ai = 0; ai < split.auto.length; ai += 1) {
    var autoItem = split.auto[ai];
    var autoPoints = Number(autoItem.points || 0);
    autoMax += autoPoints;
    var criterionId = autoItem.criterion_id;
    var passed = allMatched;
    if (criterionId.indexOf('_PAIR_') !== -1) {
      var left = criterionId.split('_PAIR_')[1];
      var expectedValue = Object.prototype.hasOwnProperty.call(correctPairs, left) ? correctPairs[left] : undefined;
      var actualValue = Object.prototype.hasOwnProperty.call(pairMap, left) ? pairMap[left] : undefined;
      passed = !duplicateLeft && actualValue === expectedValue;
    }
    var awardedPoints = passed ? autoPoints : 0;
    machinePoints += awardedPoints;
    maxPoints += autoPoints;
    awarded.push(this.criterion(criterionId, passed ? 'awarded' : 'denied', awardedPoints, autoPoints));
  }

  var diagnostics = {
    per_pair: perPair,
    pair_statuses: pairStatuses,
    signatures: signatures.slice().sort(),
    remediation: remediation
  };
  var verdictClass = this.verdictClass(machinePoints, autoMax, split.pending.length > 0, errorClass);
  return this.envelope(spec, verdictClass, errorClass, awarded, machinePoints, pendingPoints, maxPoints, diagnostics, submission);
};

/* ------------------------------------------------------------- sequence */
MethodEngine.prototype.gradeSequence = function (spec, submission) {
  var split = this.splitRubric(spec.rubric);
  var acceptance = spec.acceptance_step_ids || [];
  var distractors = spec.distractors || {};
  var stepMeta = spec.step_meta || {};
  var defaultSignature = spec.default_signature || null;

  var nextStepId = submission ? submission.next_step_id : null;
  if (nextStepId === undefined) { nextStepId = null; }

  var awarded = [];
  var pendingPoints = 0;
  var maxPoints = 0;
  for (var p = 0; p < split.pending.length; p += 1) {
    var item = split.pending[p];
    var points = Number(item.points || 0);
    maxPoints += points;
    pendingPoints += points;
    awarded.push(this.criterion(item.criterion_id, 'pending', 0, points, points));
  }

  var errorClass = 'NONE';
  var signatures = [];
  var remediation = [];
  var status;
  var signature;
  var note = '';
  var feedbackKey = null;

  if (!nextStepId) {
    errorClass = 'BLANK_RESPONSE';
    status = 'blank';
    signature = defaultSignature;
  } else if (acceptance.indexOf(nextStepId) !== -1) {
    status = 'accepted';
    signature = defaultSignature;
  } else if (Object.prototype.hasOwnProperty.call(distractors, nextStepId)) {
    status = 'distractor';
    var entry = distractors[nextStepId];
    signature = entry.signature || defaultSignature;
    note = entry.note_lv || '';
    feedbackKey = (stepMeta[nextStepId] || {}).feedback_key || null;
    errorClass = 'WRONG_ORDER';
  } else {
    status = 'unknown';
    signature = defaultSignature;
    errorClass = 'WRONG_ORDER';
  }

  if (status !== 'accepted' && status !== 'blank' && signature && signatures.indexOf(signature) === -1) {
    signatures.push(signature);
  }
  if (status !== 'accepted' && status !== 'blank') {
    var meta = stepMeta[nextStepId] || {};
    var key = feedbackKey || meta.feedback_key || null;
    remediation.push({
      card_id: spec.card_id || null,
      step_id: nextStepId,
      misconception_signature: signature || null,
      note_lv: note || (meta.note_lv || ''),
      feedback_key: key,
      feedback_text: this.feedbackText(key)
    });
  }

  var passed = status === 'accepted';
  var machinePoints = 0;
  var autoMax = 0;
  for (var ai = 0; ai < split.auto.length; ai += 1) {
    var autoItem = split.auto[ai];
    var autoPoints = Number(autoItem.points || 0);
    autoMax += autoPoints;
    var awardedPoints = passed ? autoPoints : 0;
    machinePoints += awardedPoints;
    maxPoints += autoPoints;
    awarded.push(this.criterion(autoItem.criterion_id, passed ? 'awarded' : 'denied', awardedPoints, autoPoints));
  }

  var diagnostics = {
    per_step: [{
      submitted_step_id: nextStepId,
      status: status,
      accepted_step_ids: acceptance,
      misconception_signature: signature || null,
      misconception_note_lv: note,
      feedback_key: feedbackKey,
      feedback_text: this.feedbackText(feedbackKey)
    }],
    signatures: signatures.slice().sort(),
    remediation: remediation
  };
  var verdictClass = this.verdictClass(machinePoints, autoMax, split.pending.length > 0, errorClass);
  return this.envelope(spec, verdictClass, errorClass, awarded, machinePoints, pendingPoints, maxPoints, diagnostics, submission);
};

/* ------------------------------------------------------ self assessment */
MethodEngine.prototype.gradeSelfAssessment = function (spec, submission) {
  var split = this.splitRubric(spec.rubric);
  var text = submission ? submission.text : null;
  var blank = isBlank(text);

  var awarded = [];
  var pendingPoints = 0;
  var maxPoints = 0;
  var errorClass = 'NONE';
  for (var p = 0; p < split.pending.length; p += 1) {
    var item = split.pending[p];
    var points = Number(item.points || 0);
    maxPoints += points;
    if (blank) {
      awarded.push(this.criterion(item.criterion_id, 'denied', 0, points, 0));
    } else {
      pendingPoints += points;
      awarded.push(this.criterion(item.criterion_id, 'pending', 0, points, points));
    }
  }
  if (blank) { errorClass = 'BLANK_RESPONSE'; }
  var machinePoints = 0;
  var autoMax = 0;
  for (var ai = 0; ai < split.auto.length; ai += 1) {
    var autoItem = split.auto[ai];
    var autoPoints = Number(autoItem.points || 0);
    autoMax += autoPoints;
    maxPoints += autoPoints;
    awarded.push(this.criterion(autoItem.criterion_id, 'denied', 0, autoPoints));
  }

  var diagnostics = {
    per_step: [],
    per_pair: [],
    text_recorded: true,
    text_parsed: false,
    signatures: [],
    remediation: []
  };
  var verdictClass = this.verdictClass(machinePoints, autoMax, split.pending.length > 0, errorClass);
  return this.envelope(spec, verdictClass, errorClass, awarded, machinePoints, pendingPoints, maxPoints, diagnostics, submission);
};

/* -------------------------------------------------------------- dispatch */
MethodEngine.prototype.grade = function (spec, submission) {
  var kind = spec.kind;
  if (kind === ORDERING) { return this.gradeOrdering(spec, submission || {}); }
  if (kind === MATCHING) { return this.gradeMatching(spec, submission || {}); }
  if (kind === SEQUENCE) { return this.gradeSequence(spec, submission || {}); }
  if (kind === SELF_ASSESSMENT) { return this.gradeSelfAssessment(spec, submission || {}); }
  throw MethodError('E_METHOD_KIND', 'Unsupported engine kind ' + kind + '.', {});
};

MethodEngine.prototype.gradeInstance = function (instance, submission) {
  return this.grade(this.specFromInstance(instance), submission);
};

MethodEngine.prototype.oracleView = function (record) {
  return {
    verdict_class: record.verdict_class,
    error_class: record.error_class,
    awarded_criteria: record.awarded_criteria,
    machine_checked_points: record.machine_checked_points,
    self_assessed_points: record.self_assessed_points,
    human_reviewed_points: record.human_reviewed_points,
    pending_points: record.pending_points,
    max_points: record.max_points
  };
};

/* The spec of one contract vector. ``spec_source`` decides where it comes from:
 * ``card`` merges the card's step metadata, free-order groups and pair
 * metadata; ``self_contained`` uses the vector's spec verbatim. */
function specForVector(cardsById, vector) {
  var spec = copyObject(vector.spec || {});
  if ((vector.spec_source || 'card') === 'self_contained') { return spec; }
  var card = cardsById[vector.card_id];
  if (!card) { throw MethodError('E_METHOD_CARD', 'Vector ' + vector.id + ' names an unknown card.', {}); }
  var steps = card.steps || [];
  var stepMeta = {};
  var defaultSignature = null;
  for (var i = 0; i < steps.length; i += 1) {
    stepMeta[steps[i].step_id] = {
      signature: steps[i].misconception_signature,
      note_lv: steps[i].misconception_note_lv || '',
      feedback_key: steps[i].feedback_key
    };
    if (!defaultSignature && steps[i].misconception_signature) { defaultSignature = steps[i].misconception_signature; }
  }
  if (spec.card_id === undefined) { spec.card_id = card.card_id; }
  if (spec.default_signature === undefined) { spec.default_signature = defaultSignature; }
  if (spec.kind === ORDERING) {
    if (spec.step_meta === undefined) { spec.step_meta = stepMeta; }
    if (spec.free_groups === undefined) {
      var groups = card.free_order_groups || [];
      var freeGroups = [];
      for (var g = 0; g < groups.length; g += 1) { freeGroups.push((groups[g].step_ids || []).slice()); }
      spec.free_groups = freeGroups;
    }
  } else if (spec.kind === MATCHING) {
    if (spec.pair_meta === undefined) {
      var pairMeta = {};
      var matching = card.matching || {};
      var mp = matching.correct_pairs || [];
      for (var p = 0; p < mp.length; p += 1) {
        pairMeta[mp[p].left_id] = {
          signature: mp[p].misconception_signature,
          note_lv: mp[p].note_lv || '',
          feedback_key: mp[p].feedback_key
        };
      }
      spec.pair_meta = pairMeta;
    }
  } else if (spec.kind === SEQUENCE) {
    if (spec.step_meta === undefined) { spec.step_meta = stepMeta; }
  }
  return spec;
}

/* ----------------------------------------------------------------- island */
function readIsland(doc, id) {
  var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(id) : null;
  if (!node) { throw MethodError('E_METHOD_ISLAND_MISSING', 'Island #' + id + ' was not found.', { island: id }); }
  var raw = node.textContent !== undefined ? node.textContent : node.innerText;
  if (typeof raw !== 'string' || !raw.trim()) {
    throw MethodError('E_METHOD_ISLAND_EMPTY', 'Island #' + id + ' is empty.', { island: id });
  }
  try { return JSON.parse(raw); } catch (error) {
    throw MethodError('E_METHOD_ISLAND_JSON', 'Island #' + id + ' holds broken JSON.', { island: id });
  }
}

function load(doc) {
  var contract = readIsland(doc, 'sim-method-engine');
  var terms = readIsland(doc, 'sim-terms');
  var cards = readIsland(doc, 'sim-method-cards');
  if (contract.island_id !== 'sim-method-engine') {
    throw MethodError('E_METHOD_ISLAND_ID', 'Island id mismatch for #sim-method-engine.', {});
  }
  var byId = {};
  var list = cards.cards || [];
  for (var i = 0; i < list.length; i += 1) { byId[list[i].card_id] = list[i]; }
  return {
    contract: contract,
    cards: cards,
    cardsById: byId,
    engine: new MethodEngine(contract, terms)
  };
}

root.SimMethodEngine = {
  MethodEngine: MethodEngine,
  MethodError: MethodError,
  specForVector: specForVector,
  load: load,
  canonicalProjection: canonicalProjection,
  sha256: sha256,
  digestOf: digestOf,
  ORDERING: ORDERING,
  MATCHING: MATCHING,
  SEQUENCE: SEQUENCE,
  SELF_ASSESSMENT: SELF_ASSESSMENT
};
}(typeof globalThis !== 'undefined' ? globalThis : this));
