/* N04 bank loader: the single runtime reader of the #sim-bank island.
 *
 * Reads #sim-bank, asserts cheap invariants (root shape, type count / known
 * renderer registry, id uniqueness, family structure, payload_class
 * discriminator, and required-type registry presence on populated banks),
 * maps instances to typed payload records, and hands them to N22 renderers,
 * N17-N19 engines, and N24 assembly.
 *
 * A missing, empty, truncated, or structurally invalid island throws a
 * BankError naming #sim-bank.
 */
(function (root) {
  'use strict';

  var ISLAND_ID = 'sim-bank';
  var REQUIRED_TYPES = ['Q02', 'Q04', 'Q10', 'Q11', 'Q12', 'Q13', 'Q15'];
  var TYPE_PAYLOAD_CLASS = {
    Q01: 'numeric',
    Q02: 'numeric',
    Q03: 'method',
    Q04: 'method',
    Q05: 'method',
    Q06: 'matching',
    Q07: 'option_select',
    Q08: 'ordering',
    Q09: 'numeric',
    Q10: 'numeric',
    Q11: 'graph',
    Q12: 'graph',
    Q13: 'method',
    Q14: 'option_select',
    Q15: 'method',
    Q16: 'method',
    Q17: 'method',
    Q18: 'option_select'
  };
  var RENDERER_REGISTRY = {
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
  var FAMILY_RE = /^FAM-[1-7][A-D]$/;
  var DIGEST_META = 'sim-bank-embedded-digest';

  /* N20 integrity check: the frozen island carries the SHA-256 of its own
   * embedded text. The digest is taken over the island *text* as it sits in
   * the document, not over a re-serialisation of the parsed JSON, because
   * re-serialising would route the numbers through the language's float
   * printer and could report a mismatch that never existed. */
  function islandDigest(text) {
    if (root.SimFigures && typeof root.SimFigures.sha256Utf8 === 'function') {
      return root.SimFigures.sha256Utf8(text);
    }
    return null;
  }

  function verifyIntegrity(doc, text) {
    var meta = doc && doc.querySelector ? doc.querySelector('meta[name="' + DIGEST_META + '"]') : null;
    var expected = meta ? (meta.getAttribute('content') || '') : '';
    if (!expected) {
      fail('E_BANK_DIGEST_MISSING', '#sim-bank integritātes zīmogs nav atrasts; sala nav pārbaudāma.', { island: ISLAND_ID });
    }
    var actual = islandDigest(text);
    if (actual === null) {
      fail('E_BANK_DIGEST_UNAVAILABLE', 'SHA-256 palīgs nav pieejams; #sim-bank integritāti nevar pārbaudīt.', { island: ISLAND_ID });
    }
    if (actual !== expected) {
      fail('E_BANK_DIGEST_MISMATCH', '#sim-bank sala integritātes zīmogs nesakrīt ar iestrādāto saturu.', {
        island: ISLAND_ID, expected: expected, actual: actual
      });
    }
    return actual;
  }

  function BankError(code, message, details) {
    this.name = 'BankError';
    this.code = code;
    this.message = message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, BankError);
    } else {
      this.stack = (new Error(message)).stack;
    }
  }
  BankError.prototype = Object.create(Error.prototype);
  BankError.prototype.constructor = BankError;

  function fail(code, message, details) {
    throw new BankError(code, message, details);
  }

  function parseIslandText(text) {
    if (typeof text !== 'string' || text.trim() === '') {
      fail('E_BANK_EMPTY', '#sim-bank ir tukša. Uzdevumu banka nav ielādējama.', { island: ISLAND_ID });
    }
    try {
      return JSON.parse(text);
    } catch (error) {
      fail('E_BANK_JSON', '#sim-bank satur nederīgu JSON. Uzdevumu banka nav ielādējama.', {
        island: ISLAND_ID,
        cause: String(error && error.message ? error.message : error)
      });
    }
  }

  function mapTypedRecord(q) {
    var engineBindings = [];
    var i;
    if (Array.isArray(q.rubric)) {
      for (i = 0; i < q.rubric.length; i += 1) {
        engineBindings.push({
          criterion_id: q.rubric[i].criterion_id,
          engine_binding: q.rubric[i].engine_binding,
          points: q.rubric[i].points,
          grading: q.rubric[i].grading,
          carry_forward: Boolean(q.rubric[i].carry_forward)
        });
      }
    }
    return {
      question_id: q.question_id,
      schema_version: q.schema_version,
      bank_version: q.bank_version,
      family_id: q.family_id,
      variant_id: q.variant_id,
      seed: q.seed,
      topic: q.topic,
      outcome_ids: q.outcome_ids.slice(),
      type_id: q.type_id,
      type_ids: q.type_ids.slice(),
      difficulty: q.difficulty,
      time_minutes: q.time_minutes,
      stem_lv: q.stem_lv,
      feedback_lv: q.feedback_lv,
      misconception_signatures: Array.isArray(q.misconception_signatures) ? q.misconception_signatures.slice() : [],
      givens: q.givens || {},
      payload_class: q.payload_class,
      payload: q.payload,
      rubric: q.rubric,
      review: q.review,
      extensions: q.extensions || null,
      renderer_key: RENDERER_REGISTRY[q.type_id],
      engine_bindings: engineBindings
    };
  }

  function validateAndMap(data, options) {
    options = options || {};
    var knownRenderers = options.rendererRegistry || RENDERER_REGISTRY;
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      fail('E_BANK_SHAPE', '#sim-bank sakne nav JSON objekts.', { island: ISLAND_ID });
    }
    if (data.island_id !== ISLAND_ID) {
      fail('E_BANK_ID', '#sim-bank island_id nav "sim-bank".', { island: ISLAND_ID, found: data.island_id });
    }
    if (!Array.isArray(data.questions)) {
      fail('E_BANK_SHAPE', '#sim-bank trūkst questions masīva.', { island: ISLAND_ID });
    }

    var seenIds = Object.create(null);
    var seenTypes = Object.create(null);
    var byId = Object.create(null);
    var byType = Object.create(null);
    var byFamily = Object.create(null);
    var records = [];
    var i;

    for (i = 0; i < data.questions.length; i += 1) {
      var q = data.questions[i];
      if (!q || typeof q !== 'object' || Array.isArray(q)) {
        fail('E_BANK_INSTANCE', '#sim-bank ieraksts indeksā ' + i + ' nav objekts.', { island: ISLAND_ID, index: i });
      }
      if (typeof q.question_id !== 'string' || q.question_id.trim() === '') {
        fail('E_BANK_QUESTION_ID', '#sim-bank ierakstam indeksā ' + i + ' trūkst question_id.', { island: ISLAND_ID, index: i });
      }
      if (seenIds[q.question_id]) {
        fail('E_BANK_DUPLICATE_ID', '#sim-bank atkārto question_id ' + q.question_id + '.', {
          island: ISLAND_ID,
          question_id: q.question_id
        });
      }
      seenIds[q.question_id] = true;

      if (typeof q.family_id !== 'string' || !FAMILY_RE.test(q.family_id)) {
        fail('E_BANK_FAMILY_FORMAT', '#sim-bank jautājumam ' + q.question_id + ' ir nederīgs family_id: ' + q.family_id + '.', {
          island: ISLAND_ID,
          question_id: q.question_id,
          family_id: q.family_id
        });
      }

      if (typeof q.type_id !== 'string' || !Object.prototype.hasOwnProperty.call(TYPE_PAYLOAD_CLASS, q.type_id) || !Object.prototype.hasOwnProperty.call(knownRenderers, q.type_id)) {
        fail('E_BANK_UNKNOWN_TYPE', '#sim-bank satur neatpazītu jautājuma tipu ' + String(q.type_id) + ' (nav reģistrēts renderētājs).', {
          island: ISLAND_ID,
          question_id: q.question_id,
          type_id: q.type_id
        });
      }

      var expectedClass = TYPE_PAYLOAD_CLASS[q.type_id];
      if (q.payload_class !== expectedClass) {
        fail('E_BANK_PAYLOAD_CLASS', '#sim-bank jautājumam ' + q.question_id + ' tips ' + q.type_id + ' prasa payload_class "' + expectedClass + '", atrasts "' + String(q.payload_class) + '".', {
          island: ISLAND_ID,
          question_id: q.question_id,
          expected: expectedClass,
          found: q.payload_class
        });
      }

      if (!q.payload || typeof q.payload !== 'object' || Array.isArray(q.payload)) {
        fail('E_BANK_PAYLOAD', '#sim-bank jautājumam ' + q.question_id + ' trūkst payload objekta.', {
          island: ISLAND_ID,
          question_id: q.question_id
        });
      }

      seenTypes[q.type_id] = true;
      if (Array.isArray(q.type_ids)) {
        var j;
        for (j = 0; j < q.type_ids.length; j += 1) {
          seenTypes[q.type_ids[j]] = true;
        }
      }

      var record = mapTypedRecord(q);
      records.push(record);
      byId[record.question_id] = record;
      if (!byType[record.type_id]) {
        byType[record.type_id] = [];
      }
      byType[record.type_id].push(record);
      if (!byFamily[record.family_id]) {
        byFamily[record.family_id] = [];
      }
      byFamily[record.family_id].push(record);
    }

    var shouldCheckRequired = options.enforceRequiredTypes !== false && data.status !== 'pre-N20-schema-only';
    if (shouldCheckRequired) {
      var missingRequired = [];
      for (i = 0; i < REQUIRED_TYPES.length; i += 1) {
        if (!seenTypes[REQUIRED_TYPES[i]]) {
          missingRequired.push(REQUIRED_TYPES[i]);
        }
      }
      if (missingRequired.length > 0) {
        fail('E_BANK_MISSING_REQUIRED_TYPE', '#sim-bank trūkst obligāto formas tipu: ' + missingRequired.join(', ') + '.', {
          island: ISLAND_ID,
          missing: missingRequired
        });
      }
    }

    return {
      island_id: data.island_id,
      schema_version: data.schema_version,
      bank_version: data.bank_version || '0.0.0-pre-N20',
      status: data.status || 'unknown',
      questions: records,
      byId: byId,
      byType: byType,
      byFamily: byFamily,
      counts: {
        total: records.length,
        types: Object.keys(byType).length,
        families: Object.keys(byFamily).length
      }
    };
  }

  function load(doc, options) {
    if (!doc || typeof doc.getElementById !== 'function') {
      fail('E_BANK_DOM', 'Nav pieejams DOM dokuments #sim-bank nolasīšanai.', { island: ISLAND_ID });
    }
    var el = doc.getElementById(ISLAND_ID);
    if (!el) {
      fail('E_BANK_MISSING', 'Trūkst #sim-bank salas elementa.', { island: ISLAND_ID });
    }
    if (!options || options.verifyIntegrity !== false) {
      verifyIntegrity(doc, el.textContent);
    }
    var data = parseIslandText(el.textContent);
    return validateAndMap(data, options);
  }

  function getForRenderer(bank, typeId) {
    if (!bank || !bank.byType) {
      return [];
    }
    return bank.byType[typeId] || [];
  }

  function getForAssembly(bank) {
    return bank && Array.isArray(bank.questions) ? bank.questions.slice() : [];
  }

  function getEngineBindings(record) {
    return record && Array.isArray(record.engine_bindings) ? record.engine_bindings.slice() : [];
  }

  function renderStatus(doc, bank) {
    var box = doc && doc.getElementById ? doc.getElementById('sim-bank-status') : null;
    if (!box) {
      return;
    }
    box.textContent = 'Uzdevumu bankas shēma (#sim-bank): ' + bank.counts.total + ' jautājumi, statuss: ' + bank.status + '.';
    box.hidden = false;
  }

  function renderError(doc, error) {
    var box = doc && doc.getElementById ? doc.getElementById('sim-bank-error') : null;
    if (!box) {
      return;
    }
    var code = error && error.code ? error.code : 'E_BANK';
    var msg = error && error.message ? error.message : String(error);
    box.textContent = '[' + code + '] ' + msg;
    box.hidden = false;
  }

  root.SimBank = {
    ISLAND_ID: ISLAND_ID,
    REQUIRED_TYPES: REQUIRED_TYPES,
    TYPE_PAYLOAD_CLASS: TYPE_PAYLOAD_CLASS,
    RENDERER_REGISTRY: RENDERER_REGISTRY,
    BankError: BankError,
    DIGEST_META: DIGEST_META,
    parseIslandText: parseIslandText,
    verifyIntegrity: verifyIntegrity,
    islandDigest: islandDigest,
    validateAndMap: validateAndMap,
    load: load,
    getForRenderer: getForRenderer,
    getForAssembly: getForAssembly,
    getEngineBindings: getEngineBindings,
    renderStatus: renderStatus,
    renderError: renderError
  };
})(typeof window !== 'undefined' ? window : globalThis);
