/* N02 coverage loader: the one runtime reader of the #sim-coverage island.
 *
 * Cheap invariants only (total count, id uniqueness, topic range and per-topic
 * counts). The heavy anchor check against the frozen masters stays build-time.
 * A missing, empty, truncated or structurally wrong island throws a
 * CoverageError that names #sim-coverage; the view renders the honest error
 * state instead of a blank page.
 */
(function (root) {
  'use strict';

  var ISLAND_ID = 'sim-coverage';
  var DEFAULT_EXPECTED = {
    total: 64,
    perTopic: { 1: 9, 2: 10, 3: 11, 4: 11, 5: 10, 6: 8, 7: 5 }
  };

  function CoverageError(code, message, details) {
    this.name = 'CoverageError';
    this.code = code;
    this.message = message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, CoverageError);
    } else {
      this.stack = (new Error(message)).stack;
    }
  }
  CoverageError.prototype = Object.create(Error.prototype);
  CoverageError.prototype.constructor = CoverageError;

  function fail(code, message, details) {
    throw new CoverageError(code, message, details);
  }

  function parseIslandText(text) {
    if (typeof text !== 'string' || text.trim() === '') {
      fail('E_COVERAGE_EMPTY', '#sim-coverage ir tukša. Pārklājuma dati nav ielādējami.', { island: ISLAND_ID });
    }
    try {
      return JSON.parse(text);
    } catch (error) {
      fail('E_COVERAGE_JSON', '#sim-coverage satur nederīgu JSON. Pārklājuma dati nav ielādējami.', {
        island: ISLAND_ID,
        cause: String(error && error.message ? error.message : error)
      });
    }
  }

  function validateCheap(data, expected) {
    expected = expected || DEFAULT_EXPECTED;
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      fail('E_COVERAGE_SHAPE', '#sim-coverage sakne nav JSON objekts.', { island: ISLAND_ID });
    }
    if (data.island_id !== ISLAND_ID) {
      fail('E_COVERAGE_ID', '#sim-coverage island_id nav "sim-coverage".', { island: ISLAND_ID, found: data.island_id });
    }
    if (!Array.isArray(data.outcomes) || !Array.isArray(data.topics)) {
      fail('E_COVERAGE_SHAPE', '#sim-coverage trūkst outcomes vai topics masīva.', { island: ISLAND_ID });
    }
    if (data.outcomes.length !== expected.total) {
      fail('E_COVERAGE_COUNT', '#sim-coverage paredzēti ' + expected.total + ' rezultāti, atrasti ' + data.outcomes.length + '.', {
        island: ISLAND_ID,
        expected: expected.total,
        found: data.outcomes.length
      });
    }
    if (data.topics.length !== 7) {
      fail('E_COVERAGE_TOPICS', '#sim-coverage paredzētas 7 tēmas, atrastas ' + data.topics.length + '.', {
        island: ISLAND_ID,
        expected: 7,
        found: data.topics.length
      });
    }

    var seen = Object.create(null);
    var counts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0 };
    var i;
    for (i = 0; i < data.outcomes.length; i += 1) {
      var outcome = data.outcomes[i];
      if (!outcome || typeof outcome.id !== 'string' || outcome.id === '') {
        fail('E_COVERAGE_ID', '#sim-coverage rezultātam trūkst id (indekss ' + i + ').', { island: ISLAND_ID, index: i });
      }
      if (seen[outcome.id]) {
        fail('E_COVERAGE_DUPLICATE_ID', '#sim-coverage atkārto rezultāta id ' + outcome.id + '.', {
          island: ISLAND_ID,
          id: outcome.id
        });
      }
      seen[outcome.id] = true;
      var topic = outcome.topic;
      if (typeof topic !== 'number' || topic !== Math.floor(topic) || topic < 1 || topic > 7) {
        fail('E_COVERAGE_TOPIC_RANGE', '#sim-coverage rezultātam ' + outcome.id + ' tēma ir ārpus 1..7.', {
          island: ISLAND_ID,
          id: outcome.id,
          topic: String(topic)
        });
      }
      counts[topic] += 1;
      if (typeof outcome.statement_lv !== 'string' || outcome.statement_lv.trim() === '') {
        fail('E_COVERAGE_STATEMENT', '#sim-coverage rezultātam ' + outcome.id + ' trūkst statement_lv.', {
          island: ISLAND_ID,
          id: outcome.id
        });
      }
    }
    var t;
    for (t = 1; t <= 7; t += 1) {
      if (counts[t] !== expected.perTopic[t]) {
        fail('E_COVERAGE_TOPIC_COUNT', '#sim-coverage tēmai ' + t + ' paredzēti ' + expected.perTopic[t] + ' rezultāti, atrasti ' + counts[t] + '.', {
          island: ISLAND_ID,
          topic: t,
          expected: expected.perTopic[t],
          found: counts[t]
        });
      }
    }

    var topicNumbers = Object.create(null);
    for (i = 0; i < data.topics.length; i += 1) {
      var record = data.topics[i];
      if (!record || typeof record.topic !== 'number' || record.topic < 1 || record.topic > 7) {
        fail('E_COVERAGE_TOPIC_RANGE', '#sim-coverage topics sarakstā ir nederīgs tēmas numurs.', { island: ISLAND_ID });
      }
      if (topicNumbers[record.topic]) {
        fail('E_COVERAGE_TOPIC_DUPLICATE', '#sim-coverage atkārto tēmu ' + record.topic + '.', { island: ISLAND_ID });
      }
      topicNumbers[record.topic] = true;
      if (typeof record.name_lv !== 'string' || record.name_lv.trim() === '') {
        fail('E_COVERAGE_TOPIC_NAME', '#sim-coverage tēmai ' + record.topic + ' trūkst name_lv.', {
          island: ISLAND_ID,
          topic: record.topic
        });
      }
    }

    return {
      island_id: data.island_id,
      title_lv: data.title_lv,
      topics: data.topics,
      outcomes: data.outcomes,
      counts: counts,
      total: data.outcomes.length
    };
  }

  function load(doc, expected) {
    doc = doc || root.document;
    if (!doc || typeof doc.getElementById !== 'function') {
      fail('E_COVERAGE_DOCUMENT', 'Nav pieejams dokumenta konteksts #sim-coverage ielādei.', { island: ISLAND_ID });
    }
    var element = doc.getElementById(ISLAND_ID);
    if (!element) {
      fail('E_COVERAGE_MISSING', 'Dokumentā nav #sim-coverage elementa. Pārklājuma dati nav ielādējami.', { island: ISLAND_ID });
    }
    var text = element.textContent || element.innerText || '';
    var data = parseIslandText(text);
    return validateCheap(data, expected);
  }

  function renderError(doc, error) {
    doc = doc || root.document;
    var detail = error && error.message ? error.message : 'Nezināma pārklājuma datu kļūda.';
    var message = 'Pārklājuma dati nav pieejami. ' + detail;
    var box = doc && doc.getElementById ? doc.getElementById('sim-coverage-error') : null;
    if (box) {
      box.hidden = false;
      box.textContent = message;
    }
    var nav = doc && doc.getElementById ? doc.getElementById('coverage-nav') : null;
    if (nav) {
      nav.textContent = 'Pārklājuma navigācija nav pieejama: #sim-coverage.';
    }
    var list = doc && doc.getElementById ? doc.getElementById('coverage-list') : null;
    if (list) {
      list.textContent = message;
    }
    return message;
  }

  root.SimCoverage = {
    ISLAND_ID: ISLAND_ID,
    DEFAULT_EXPECTED: DEFAULT_EXPECTED,
    CoverageError: CoverageError,
    parseIslandText: parseIslandText,
    validateCheap: validateCheap,
    load: load,
    renderError: renderError
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = root.SimCoverage;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
