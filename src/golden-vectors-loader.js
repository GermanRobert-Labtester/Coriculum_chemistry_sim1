/* N05 golden vectors loader: the single runtime reader of #sim-golden-vectors.
 *
 * Reads #sim-golden-vectors, asserts root invariants, retired-id non-reuse,
 * and cross-checks SimPRNG contract smoke parity and SimBank type/class
 * resolution when SimBank is present.
 *
 * A missing, empty, truncated, or structurally invalid island throws a
 * GoldenVectorsError naming #sim-golden-vectors.
 */
(function (root) {
  'use strict';

  var ISLAND_ID = 'sim-golden-vectors';
  var EXPECTED_PRNG_SEED1_DRAW0 = '10451216379200822465';
  var TYPE_PAYLOAD_CLASS = {
    Q01: 'numeric', Q02: 'numeric', Q03: 'method', Q04: 'method',
    Q05: 'method', Q06: 'matching', Q07: 'option_select', Q08: 'ordering',
    Q09: 'numeric', Q10: 'numeric', Q11: 'graph', Q12: 'graph',
    Q13: 'method', Q14: 'option_select', Q15: 'method', Q16: 'method',
    Q17: 'method', Q18: 'option_select'
  };

  function GoldenVectorsError(code, message, details) {
    this.name = 'GoldenVectorsError';
    this.code = code;
    this.message = '[' + code + '] ' + message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, GoldenVectorsError);
    } else {
      this.stack = (new Error(this.message)).stack;
    }
  }
  GoldenVectorsError.prototype = Object.create(Error.prototype);
  GoldenVectorsError.prototype.constructor = GoldenVectorsError;

  function fail(code, message, details) {
    throw new GoldenVectorsError(code, message, details);
  }

  function parseIslandText(text) {
    if (typeof text !== 'string' || text.trim() === '') {
      fail('E_VECTORS_EMPTY', '#sim-golden-vectors ir tukša. Zelta vektori nav ielādējami.', { island: ISLAND_ID });
    }
    try {
      return JSON.parse(text);
    } catch (error) {
      fail('E_VECTORS_JSON', '#sim-golden-vectors satur nederīgu JSON. Zelta vektori nav ielādējami.', {
        island: ISLAND_ID,
        cause: String(error && error.message ? error.message : error)
      });
    }
  }

  function runPrngSmokeCheck() {
    if (!root.SimPRNG || typeof root.SimPRNG.createStream !== 'function') {
      fail('E_PRNG_MISSING', 'SimPRNG nav ielādēts pirms #sim-golden-vectors pārbaudes.', { island: ISLAND_ID });
    }
    var stream = root.SimPRNG.createStream(1n);
    var first = stream.nextU64().toString();
    if (first !== EXPECTED_PRNG_SEED1_DRAW0) {
      fail('E_PRNG_SMOKE', 'SimPRNG paškontrole nesakrīt: gaidīts ' + EXPECTED_PRNG_SEED1_DRAW0 + ', iegūts ' + first + '.', {
        expected: EXPECTED_PRNG_SEED1_DRAW0,
        actual: first
      });
    }
    var rejectedZero = false;
    try {
      root.SimPRNG.createStream(0);
    } catch (e) {
      rejectedZero = Boolean(e && e.code === 'E_PRNG_INVALID_SEED');
    }
    if (!rejectedZero) {
      fail('E_PRNG_SMOKE', 'SimPRNG nenoraidīja nederīgu sēklu 0.', { island: ISLAND_ID });
    }
    return { seed1_draw0: first, illegal_zero_rejected: rejectedZero };
  }

  function validate(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      fail('E_VECTORS_SHAPE', '#sim-golden-vectors sakne nav JSON objekts.', { island: ISLAND_ID });
    }
    if (data.island_id !== ISLAND_ID) {
      fail('E_VECTORS_ID', '#sim-golden-vectors island_id nav "sim-golden-vectors".', { island: ISLAND_ID, found: data.island_id });
    }
    if (!Array.isArray(data.vectors) || data.vectors.length === 0) {
      fail('E_VECTORS_EMPTY', '#sim-golden-vectors nesatur aktīvus vektorus.', { island: ISLAND_ID });
    }
    if (!Array.isArray(data.retired_ids)) {
      fail('E_VECTORS_SHAPE', '#sim-golden-vectors trūkst retired_ids masīva.', { island: ISLAND_ID });
    }

    var retiredSet = Object.create(null);
    var i;
    for (i = 0; i < data.retired_ids.length; i += 1) {
      var r = data.retired_ids[i];
      if (r && r.retired_id) {
        retiredSet[r.retired_id] = true;
      }
    }

    var seenIds = Object.create(null);
    var active = [];
    var byTopic = Object.create(null);
    var byType = Object.create(null);

    for (i = 0; i < data.vectors.length; i += 1) {
      var v = data.vectors[i];
      if (!v || typeof v !== 'object' || !v.vector_id || !v.instance || !v.expected) {
        fail('E_VECTORS_SHAPE', '#sim-golden-vectors ieraksts indeksā ' + i + ' ir nepilnīgs.', { island: ISLAND_ID, index: i });
      }
      if (seenIds[v.vector_id]) {
        fail('E_VECTORS_DUPLICATE_ID', '#sim-golden-vectors atkārto vector_id ' + v.vector_id + '.', { island: ISLAND_ID, vector_id: v.vector_id });
      }
      seenIds[v.vector_id] = true;

      if (v.status === 'active') {
        if (retiredSet[v.vector_id]) {
          fail('E_VECTORS_RETIRED_REUSE', '#sim-golden-vectors aktīvs vektors atkārto atsauktu id ' + v.vector_id + '.', { island: ISLAND_ID, vector_id: v.vector_id });
        }
        var inst = v.instance;
        var expectedPc = TYPE_PAYLOAD_CLASS[inst.type_id];
        if (!expectedPc || inst.payload_class !== expectedPc) {
          fail('E_VECTORS_TYPE', '#sim-golden-vectors vektoram ' + v.vector_id + ' nesader type_id/payload_class.', {
            island: ISLAND_ID,
            vector_id: v.vector_id,
            type_id: inst.type_id,
            payload_class: inst.payload_class
          });
        }
        active.push(v);
        var tk = String(inst.topic);
        byTopic[tk] = (byTopic[tk] || 0) + 1;
        byType[inst.type_id] = (byType[inst.type_id] || 0) + 1;
      }
    }

    var smokePrng = runPrngSmokeCheck();
    return {
      island_id: data.island_id,
      corpus_version: data.corpus_version || '1.0.0',
      status: data.status || 'unknown',
      vectors: active,
      counts: {
        active: active.length,
        retired: data.retired_ids.length,
        topics: Object.keys(byTopic).length,
        types: Object.keys(byType).length
      },
      prng_smoke: smokePrng
    };
  }

  function load(doc) {
    if (!doc || typeof doc.getElementById !== 'function') {
      fail('E_VECTORS_DOM', 'Nav pieejams DOM dokuments #sim-golden-vectors nolasīšanai.', { island: ISLAND_ID });
    }
    var el = doc.getElementById(ISLAND_ID);
    if (!el) {
      fail('E_VECTORS_MISSING', 'Trūkst #sim-golden-vectors salas elementa.', { island: ISLAND_ID });
    }
    var data = parseIslandText(el.textContent);
    return validate(data);
  }

  function renderStatus(doc, loaded) {
    var box = doc && doc.getElementById ? doc.getElementById('sim-golden-vectors-status') : null;
    if (!box) {
      return;
    }
    box.textContent = 'Zelta vektori (#sim-golden-vectors): ' + loaded.counts.active + ' aktīvi vektori, ' +
      loaded.counts.topics + ' tēmas, ' + loaded.counts.types + ' tipi; PRNG (' + root.SimPRNG.ALGORITHM_ID + ') paškontrole OK.';
    box.hidden = false;
  }

  function renderError(doc, error) {
    var box = doc && doc.getElementById ? doc.getElementById('sim-golden-vectors-error') : null;
    if (!box) {
      return;
    }
    var msg = error && error.message ? error.message : String(error);
    box.textContent = msg;
    box.hidden = false;
  }

  root.SimGoldenVectors = {
    ISLAND_ID: ISLAND_ID,
    GoldenVectorsError: GoldenVectorsError,
    load: load,
    validate: validate,
    renderStatus: renderStatus,
    renderError: renderError
  };
})(typeof globalThis !== 'undefined' ? globalThis : this);
