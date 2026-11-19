/* N03 conventions loader: the one runtime reader of the #sim-conventions island.
 *
 * The heavy work (schema, bidirectional factors, composition chains, citations,
 * registry traceability) is build-time in tools/validate_conventions.py. This
 * loader keeps only cheap invariants and exposes the accessors every consumer
 * uses: conversion chains, atomic/compound masses, tolerances, potential
 * symbols, rounding and derived-vector expectations.
 *
 * A missing, empty, truncated or structurally wrong island throws a
 * ConventionsError that names #sim-conventions, so a consumer never silently
 * falls back to a local copy.
 */
(function (root) {
  'use strict';

  var ISLAND_ID = 'sim-conventions';
  var EXPECTED_CONFLICTS = 22;
  var EXPECTED_V = 12;
  var EXPECTED_C = 10;

  function ConventionsError(code, message, details) {
    this.name = 'ConventionsError';
    this.code = code;
    this.message = message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ConventionsError);
    } else {
      this.stack = (new Error(message)).stack;
    }
  }
  ConventionsError.prototype = Object.create(Error.prototype);
  ConventionsError.prototype.constructor = ConventionsError;

  function fail(code, message, details) {
    throw new ConventionsError(code, message, details);
  }

  function parseIslandText(text) {
    if (typeof text !== 'string' || text.trim() === '') {
      fail('E_CONVENTIONS_EMPTY', '#sim-conventions ir tukša. Konvenciju dati nav ielādējami.', { island: ISLAND_ID });
    }
    try {
      return JSON.parse(text);
    } catch (error) {
      fail('E_CONVENTIONS_JSON', '#sim-conventions satur nederīgu JSON. Konvenciju dati nav ielādējami.', {
        island: ISLAND_ID,
        cause: String(error && error.message ? error.message : error)
      });
    }
  }

  function rational(value, label) {
    if (!value || typeof value !== 'object' || typeof value.num !== 'number' || typeof value.den !== 'number' || value.den === 0) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions: nederīga racionāla vērtība ' + label + '.', { island: ISLAND_ID, label: label });
    }
    return value.num / value.den;
  }

  function byId(list, id, label) {
    var i;
    for (i = 0; i < list.length; i += 1) {
      if (list[i] && list[i].id === id) {
        return list[i];
      }
    }
    fail('E_CONVENTIONS_REF', '#sim-conventions: nav atrasts ' + label + ' ' + id + '.', { island: ISLAND_ID, id: id, label: label });
  }

  function uniqueIds(list, label) {
    var seen = Object.create(null);
    var i;
    for (i = 0; i < list.length; i += 1) {
      var id = list[i] && list[i].id;
      if (!id) {
        fail('E_CONVENTIONS_SHAPE', '#sim-conventions: ' + label + ' ierakstam trūkst id (indekss ' + i + ').', { island: ISLAND_ID, label: label, index: i });
      }
      if (seen[id]) {
        fail('E_CONVENTIONS_DUPLICATE_ID', '#sim-conventions: atkārtots ' + label + ' id ' + id + '.', { island: ISLAND_ID, id: id, label: label });
      }
      seen[id] = true;
    }
    return seen;
  }

  function validateCheap(data) {
    if (!data || typeof data !== 'object' || Array.isArray(data)) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions sakne nav JSON objekts.', { island: ISLAND_ID });
    }
    if (data.island_id !== ISLAND_ID) {
      fail('E_CONVENTIONS_ID', '#sim-conventions island_id nav "sim-conventions".', { island: ISLAND_ID, found: data.island_id });
    }
    if (data.schema_version !== 1) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions schema_version nav 1.', { island: ISLAND_ID, found: data.schema_version });
    }
    var sections = [
      'epistemic_contract', 'citation_index', 'atomic_masses', 'compound_molar_masses',
      'constants', 'unit_system', 'concentration_bases', 'percentage_basis', 'density',
      'titration', 'potentials', 'thermodynamics', 'spectrophotometry', 'tolerances',
      'rounding', 'consumer_contract', 'derived_vectors', 'conflicts'
    ];
    var i;
    for (i = 0; i < sections.length; i += 1) {
      if (!data[sections[i]]) {
        fail('E_CONVENTIONS_SECTION', '#sim-conventions trūkst sadaļas ' + sections[i] + '.', { island: ISLAND_ID, section: sections[i] });
      }
    }
    var unit = data.unit_system || {};
    if (!Array.isArray(unit.conversions) || !unit.conversions.length) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions nav nevienas vienību pārejas.', { island: ISLAND_ID });
    }
    if (!Array.isArray(unit.chains) || !unit.chains.length) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions nav nevienas kompozīcijas ķēdes.', { island: ISLAND_ID });
    }
    var conversionIds = uniqueIds(unit.conversions, 'conversion');
    var chainIds = uniqueIds(unit.chains, 'chain');
    var toleranceIds = uniqueIds(data.tolerances.quantity_classes || [], 'tolerance');
    var vectors = data.derived_vectors || [];
    uniqueIds(vectors, 'derived_vector');
    var conflicts = data.conflicts || {};
    var entries = conflicts.entries || [];
    if (!Array.isArray(entries) || entries.length !== EXPECTED_CONFLICTS) {
      fail('E_CONVENTIONS_CONFLICT_COUNT', '#sim-conventions paredzēti ' + EXPECTED_CONFLICTS + ' konflikti, atrasti ' + (entries ? entries.length : 0) + '.', {
        island: ISLAND_ID, expected: EXPECTED_CONFLICTS, found: entries ? entries.length : 0
      });
    }
    var vCount = 0;
    var cCount = 0;
    var conflictIds = Object.create(null);
    for (i = 0; i < entries.length; i += 1) {
      var entryId = entries[i] && entries[i].id;
      if (!entryId) {
        fail('E_CONVENTIONS_SHAPE', '#sim-conventions konfliktam trūkst id (indekss ' + i + ').', { island: ISLAND_ID, index: i });
      }
      if (conflictIds[entryId]) {
        fail('E_CONVENTIONS_DUPLICATE_ID', '#sim-conventions atkārto konflikta id ' + entryId + '.', { island: ISLAND_ID, id: entryId });
      }
      conflictIds[entryId] = true;
      if (/^V-\d\d$/.test(entryId)) {
        vCount += 1;
      } else if (/^C\d\d$/.test(entryId)) {
        cCount += 1;
      }
    }
    if (vCount !== EXPECTED_V || cCount !== EXPECTED_C) {
      fail('E_CONVENTIONS_CONFLICT_COUNT', '#sim-conventions paredzēti ' + EXPECTED_V + ' V un ' + EXPECTED_C + ' C konflikti, atrasti ' + vCount + ' un ' + cCount + '.', {
        island: ISLAND_ID, v: vCount, c: cCount
      });
    }
    if (!Array.isArray(data.citation_index) || !data.citation_index.length) {
      fail('E_CONVENTIONS_SHAPE', '#sim-conventions nav citātu indeksa.', { island: ISLAND_ID });
    }
    // Cheap vector resolution: every vector must point at a real path.
    for (i = 0; i < vectors.length; i += 1) {
      try {
        resolvePath(data, vectors[i].source_ref, conversionIds, chainIds, toleranceIds);
      } catch (error) {
        fail('E_CONVENTIONS_REF', '#sim-conventions vektors ' + vectors[i].id + ' neizšķiras: ' + (error.message || error), {
          island: ISLAND_ID, vector: vectors[i].id
        });
      }
    }
    return {
      island_id: data.island_id,
      schema_version: data.schema_version,
      title_lv: data.title_lv,
      data: data,
      counts: {
        conversions: unit.conversions.length,
        chains: unit.chains.length,
        tolerance_classes: (data.tolerances.quantity_classes || []).length,
        conflicts: entries.length,
        citations: data.citation_index.length,
        vectors: vectors.length
      }
    };
  }

  function splitPath(expression) {
    var parts = [];
    var buffer = '';
    var depth = 0;
    var i;
    for (i = 0; i < expression.length; i += 1) {
      var char = expression.charAt(i);
      if (char === '[') { depth += 1; }
      if (char === ']') { depth -= 1; }
      if (char === '.' && depth === 0) {
        parts.push(buffer);
        buffer = '';
      } else {
        buffer += char;
      }
    }
    parts.push(buffer);
    return parts;
  }

  function resolvePath(root, expression, conversionIds, chainIds, toleranceIds) {
    var parts = splitPath(String(expression || ''));
    var current = root;
    var i;
    for (i = 0; i < parts.length; i += 1) {
      var match = /^([A-Za-z0-9_]+)(?:\[id=([^\]]+)\])?$/.exec(parts[i]);
      if (!match) {
        throw new Error('invalid path segment ' + parts[i]);
      }
      current = current[match[1]];
      if (match[2] !== undefined) {
        if (!Array.isArray(current)) {
          throw new Error(match[1] + ' is not a list');
        }
        var found = null;
        var j;
        for (j = 0; j < current.length; j += 1) {
          if (current[j] && current[j].id === match[2]) {
            found = current[j];
            break;
          }
        }
        if (!found) {
          throw new Error(match[1] + '[id=' + match[2] + '] not found');
        }
        current = found;
      }
    }
    return current;
  }

  function findChain(data, from, to) {
    var chains = data.unit_system.chains;
    var i;
    for (i = 0; i < chains.length; i += 1) {
      if (chains[i].from === from && chains[i].to === to && chains[i].kind !== 'symbolic') {
        return chains[i];
      }
    }
    return null;
  }

  function findConversion(data, from, to) {
    var conversions = data.unit_system.conversions;
    var i;
    for (i = 0; i < conversions.length; i += 1) {
      if (conversions[i].from === from && conversions[i].to === to && conversions[i].conversion_class !== 'blocked') {
        return { conversion: conversions[i], reversed: false };
      }
      if (conversions[i].to === from && conversions[i].from === to && conversions[i].conversion_class !== 'blocked') {
        return { conversion: conversions[i], reversed: true };
      }
    }
    return null;
  }

  function load(doc) {
    doc = doc || root.document;
    if (!doc || typeof doc.getElementById !== 'function') {
      fail('E_CONVENTIONS_MISSING', 'Nav pieejams dokumenta konteksts #sim-conventions ielādei.', { island: ISLAND_ID });
    }
    var element = doc.getElementById(ISLAND_ID);
    if (!element) {
      fail('E_CONVENTIONS_MISSING', 'Dokumentā nav #sim-conventions elementa. Konvenciju dati nav ielādējami.', { island: ISLAND_ID });
    }
    var text = element.textContent || element.innerText || '';
    var data = parseIslandText(text);
    return validateCheap(data);
  }

  function model(loaded) {
    var data = loaded && loaded.data ? loaded.data : loaded;
    return {
      raw: data,
      conversion: function (id) {
        return byId(data.unit_system.conversions, id, 'conversion');
      },
      chain: function (id) {
        var record = byId(data.unit_system.chains, id, 'chain');
        var answer = {
          id: record.id, from: record.from, to: record.to, kind: record.kind,
          exactness: record.exactness, formula: record.formula || null,
          requires: record.requires || []
        };
        if (record.kind !== 'symbolic') {
          answer.factor = rational(record.factor, 'chain ' + id + '.factor');
          answer.offset = rational(record.offset || { num: 0, den: 1 }, 'chain ' + id + '.offset');
        }
        return answer;
      },
      conversionFactor: function (from, to) {
        var chain = findChain(data, from, to);
        if (chain) {
          return rational(chain.factor, 'chain ' + chain.id + '.factor');
        }
        var direct = findConversion(data, from, to);
        if (!direct) {
          fail('E_CONVENTIONS_REF', '#sim-conventions: nav pārejas ' + from + ' -> ' + to + '.', {
            island: ISLAND_ID, from: from, to: to
          });
        }
        var factor = rational(direct.conversion.factor, 'conversion ' + direct.conversion.id + '.factor');
        return direct.reversed ? 1 / factor : factor;
      },
      convert: function (value, from, to) {
        var chain = findChain(data, from, to);
        if (chain) {
          return Number(value) * rational(chain.factor, 'chain ' + chain.id + '.factor') +
            rational(chain.offset || { num: 0, den: 1 }, 'chain ' + chain.id + '.offset');
        }
        var direct = findConversion(data, from, to);
        if (!direct) {
          fail('E_CONVENTIONS_REF', '#sim-conventions: nav pārejas ' + from + ' -> ' + to + '.', {
            island: ISLAND_ID, from: from, to: to
          });
        }
        var factor = rational(direct.conversion.factor, 'conversion ' + direct.conversion.id + '.factor');
        var offset = rational(direct.conversion.offset || { num: 0, den: 1 }, 'conversion ' + direct.conversion.id + '.offset');
        if (direct.reversed) {
          return (Number(value) - offset) / factor;
        }
        return Number(value) * factor + offset;
      },
      atomicMass: function (symbol) {
        return this.element(symbol);
      },
      element: function (symbol) {
        var elements = data.atomic_masses.elements;
        var i;
        for (i = 0; i < elements.length; i += 1) {
          if (elements[i].symbol === symbol) {
            return Number(elements[i].value);
          }
        }
        fail('E_CONVENTIONS_REF', '#sim-conventions: nav atoma simbols ' + symbol + '.', { island: ISLAND_ID, symbol: symbol });
      },
      compoundMolarMass: function (formula) {
        var compounds = data.compound_molar_masses.compounds;
        var i;
        for (i = 0; i < compounds.length; i += 1) {
          if (compounds[i].formula === formula) {
            return Number(compounds[i].working_value);
          }
        }
        fail('E_CONVENTIONS_REF', '#sim-conventions: nav savienojuma ' + formula + '.', { island: ISLAND_ID, formula: formula });
      },
      tolerance: function (id) {
        var record = byId(data.tolerances.quantity_classes, id, 'tolerance');
        return {
          id: record.id, unit: record.unit,
          absolute: Number(record.absolute.value),
          significant_figures: record.significant_figures.mode,
          rounding: record.rounding.mode,
          label: record.absolute.label
        };
      },
      potential: function (id) {
        return byId(data.potentials.symbols, id, 'potential symbol');
      },
      rounding: function () {
        return {
          rule: data.rounding.rule,
          final_only: data.rounding.final_only,
          guard_digits: data.rounding.guard_digits
        };
      },
      vectorExpectation: function (id) {
        var vectors = data.derived_vectors;
        var i;
        for (i = 0; i < vectors.length; i += 1) {
          if (vectors[i].id === id) {
            var value = resolvePath(data, vectors[i].source_ref);
            if (value && typeof value === 'object' && typeof value.num === 'number' && typeof value.den === 'number') {
              value = value.num / value.den;
            } else if (typeof value === 'string' && value.trim() !== '' && isFinite(Number(value))) {
              value = Number(value);
            }
            return { id: id, kind: vectors[i].kind, unit: vectors[i].unit, source_ref: vectors[i].source_ref, value: value };
          }
        }
        fail('E_CONVENTIONS_REF', '#sim-conventions: nav vektora ' + id + '.', { island: ISLAND_ID, vector: id });
      },
      roundHalfUp: function (value, decimals) {
        var factor = Math.pow(10, decimals);
        var scaled = Number(value) * factor;
        var rounded = Math.floor(Math.abs(scaled) + 0.5 + 1e-12) * (scaled < 0 ? -1 : 1);
        return rounded / factor;
      }
    };
  }

  function renderError(doc, error) {
    doc = doc || root.document;
    var detail = error && error.message ? error.message : 'Nezināma konvenciju datu kļūda.';
    var message = 'Konvenciju dati nav pieejami. ' + detail;
    var box = doc && doc.getElementById ? doc.getElementById('sim-conventions-error') : null;
    if (box) {
      box.hidden = false;
      box.textContent = message;
    }
    var status = doc && doc.getElementById ? doc.getElementById('sim-conventions-status') : null;
    if (status) {
      status.hidden = false;
      status.textContent = message;
    }
    return message;
  }

  function renderStatus(doc, loaded) {
    doc = doc || root.document;
    var status = doc && doc.getElementById ? doc.getElementById('sim-conventions-status') : null;
    if (!status) {
      return '';
    }
    var counts = loaded.counts;
    var text = 'Konvenciju kopa ielādēta: ' + counts.conversions + ' vienību pārejas, ' +
      counts.chains + ' ķēdes, ' + counts.tolerance_classes + ' tolerances, ' +
      counts.conflicts + ' konflikti.';
    status.hidden = false;
    status.textContent = text;
    return text;
  }

  root.SimConventions = {
    ISLAND_ID: ISLAND_ID,
    EXPECTED_CONFLICTS: EXPECTED_CONFLICTS,
    ConventionsError: ConventionsError,
    parseIslandText: parseIslandText,
    validateCheap: validateCheap,
    load: load,
    model: model,
    renderError: renderError,
    renderStatus: renderStatus
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = root.SimConventions;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
