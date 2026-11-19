/* N07 concept map & ASCII anchor graph:
 *
 * Builds the deterministic, acyclic, layered concept map over the loaded
 * #sim-coverage island (zero invented structural nodes or edges).
 * - Layer rule: layer(u) = 0 if prerequisites(u).length === 0 else 1 + max(layer(p))
 * - Tie-break within layer: ascending ASCII outcome id
 * - Wrap rule: chunk each layer into rows of at most WRAP_THRESHOLD (3) nodes
 * - Semantic structure: layered <ol>/<ul> lists with keyboard-focusable node
 *   buttons and named edge links (all text via textContent, no innerHTML).
 */
(function (root) {
  'use strict';

  var DEFAULT_WRAP_THRESHOLD = 3;
  var LAYOUT_RULES = {
    layerRule: '0 if prerequisites.length === 0 else 1 + max(layer(p))',
    tieBreak: 'ascending ASCII outcome id',
    wrapThreshold: DEFAULT_WRAP_THRESHOLD
  };

  function ConceptMapError(code, message, details) {
    this.name = 'ConceptMapError';
    this.code = code;
    this.message = message;
    this.details = details || {};
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ConceptMapError);
    } else {
      this.stack = (new Error(message)).stack;
    }
  }
  ConceptMapError.prototype = Object.create(Error.prototype);
  ConceptMapError.prototype.constructor = ConceptMapError;

  function asciiCompare(a, b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
  }

  function assertAcyclic(outcomes) {
    var byId = Object.create(null);
    var ids = [];
    var i;
    for (i = 0; i < outcomes.length; i += 1) {
      var o = outcomes[i];
      byId[o.id] = o;
      ids.push(o.id);
    }
    ids.sort(asciiCompare);

    for (i = 0; i < ids.length; i += 1) {
      var oid = ids[i];
      var prereqs = Array.isArray(byId[oid].prerequisites) ? byId[oid].prerequisites : [];
      var j;
      for (j = 0; j < prereqs.length; j += 1) {
        if (!byId[prereqs[j]]) {
          throw new ConceptMapError(
            'E_MAP_MISSING_PREREQ',
            'Konceptam ' + oid + ' norādīts neesošs priekšnosacījums ' + prereqs[j] + '.',
            { outcomeId: oid, missingPrerequisite: prereqs[j] }
          );
        }
      }
    }

    var WHITE = 0;
    var GRAY = 1;
    var BLACK = 2;
    var color = Object.create(null);
    for (i = 0; i < ids.length; i += 1) {
      color[ids[i]] = WHITE;
    }
    var stack = [];

    function visit(nodeId) {
      color[nodeId] = GRAY;
      stack.push(nodeId);
      var prereqs = Array.isArray(byId[nodeId].prerequisites) ? byId[nodeId].prerequisites.slice().sort(asciiCompare) : [];
      var k;
      for (k = 0; k < prereqs.length; k += 1) {
        var target = prereqs[k];
        if (color[target] === GRAY) {
          var idx = stack.indexOf(target);
          var cycle = stack.slice(idx).concat([target]);
          throw new ConceptMapError(
            'E_MAP_CYCLE',
            'Konceptu kartes priekšnosacījumu grafā atrasts cikls: ' + cycle.join(' -> ') + '.',
            { cycle: cycle }
          );
        }
        if (color[target] === WHITE) {
          visit(target);
        }
      }
      stack.pop();
      color[nodeId] = BLACK;
    }

    for (i = 0; i < ids.length; i += 1) {
      if (color[ids[i]] === WHITE) {
        visit(ids[i]);
      }
    }
    return true;
  }

  function chunkArray(items, size) {
    var rows = [];
    var i;
    for (i = 0; i < items.length; i += size) {
      rows.push(items.slice(i, i + size));
    }
    return rows;
  }

  function computeLayout(coverageData, options) {
    options = options || {};
    var wrapThreshold = typeof options.wrapThreshold === 'number' && options.wrapThreshold >= 1
      ? Math.floor(options.wrapThreshold)
      : DEFAULT_WRAP_THRESHOLD;

    if (!coverageData || !Array.isArray(coverageData.outcomes) || !Array.isArray(coverageData.topics)) {
      throw new ConceptMapError('E_MAP_INPUT', 'Konceptu kartei trūkst derīgu pārklājuma datu (outcomes/topics).', {});
    }

    var outcomes = coverageData.outcomes;
    var topics = coverageData.topics;
    assertAcyclic(outcomes);

    var byId = Object.create(null);
    var dependents = Object.create(null);
    var i;
    for (i = 0; i < outcomes.length; i += 1) {
      byId[outcomes[i].id] = outcomes[i];
      dependents[outcomes[i].id] = [];
    }
    for (i = 0; i < outcomes.length; i += 1) {
      var o = outcomes[i];
      var ps = Array.isArray(o.prerequisites) ? o.prerequisites : [];
      var j;
      for (j = 0; j < ps.length; j += 1) {
        dependents[ps[j]].push(o.id);
      }
    }

    var globalMemo = Object.create(null);
    function getGlobalLayer(id) {
      if (Object.prototype.hasOwnProperty.call(globalMemo, id)) {
        return globalMemo[id];
      }
      var ps = Array.isArray(byId[id].prerequisites) ? byId[id].prerequisites : [];
      var layer = 0;
      var k;
      for (k = 0; k < ps.length; k += 1) {
        var pl = getGlobalLayer(ps[k]) + 1;
        if (pl > layer) {
          layer = pl;
        }
      }
      globalMemo[id] = layer;
      return layer;
    }

    var localMemo = Object.create(null);
    function getLocalLayer(id) {
      if (Object.prototype.hasOwnProperty.call(localMemo, id)) {
        return localMemo[id];
      }
      var topic = byId[id].topic;
      var ps = Array.isArray(byId[id].prerequisites) ? byId[id].prerequisites : [];
      var layer = 0;
      var k;
      for (k = 0; k < ps.length; k += 1) {
        if (byId[ps[k]].topic === topic) {
          var pl = getLocalLayer(ps[k]) + 1;
          if (pl > layer) {
            layer = pl;
          }
        }
      }
      localMemo[id] = layer;
      return layer;
    }

    var sortedIds = Object.keys(byId).sort(asciiCompare);
    var nodesById = Object.create(null);
    var maxLayer = 0;

    for (i = 0; i < sortedIds.length; i += 1) {
      var id = sortedIds[i];
      var out = byId[id];
      var gl = getGlobalLayer(id);
      var ll = getLocalLayer(id);
      if (gl > maxLayer) {
        maxLayer = gl;
      }
      var prereqSorted = (Array.isArray(out.prerequisites) ? out.prerequisites.slice() : []).sort(asciiCompare);
      var depSorted = dependents[id].slice().sort(asciiCompare);
      nodesById[id] = {
        id: id,
        topic: out.topic,
        statement_lv: out.statement_lv,
        master_anchor: out.master_anchor,
        master_heading_lv: out.master_heading_lv,
        master_path: out.master_path,
        master_freeze_id: out.master_freeze_id,
        layer: gl,
        localLayer: ll,
        prerequisites: prereqSorted,
        dependents: depSorted,
        mapNodeId: 'karte-' + id,
        mapButtonId: 'karte-btn-' + id,
        objectivesAnchor: '#rezultats-' + id
      };
    }

    var edges = [];
    var crossTopicEdges = [];
    for (i = 0; i < sortedIds.length; i += 1) {
      var toId = sortedIds[i];
      var toNode = nodesById[toId];
      var pIdx;
      for (pIdx = 0; pIdx < toNode.prerequisites.length; pIdx += 1) {
        var fromId = toNode.prerequisites[pIdx];
        var fromNode = nodesById[fromId];
        var isCross = fromNode.topic !== toNode.topic;
        var edgeLabel = isCross
          ? 'Starptēmu priekšnosacījums no ' + fromId + ' (#' + fromNode.master_anchor + ', ' + fromNode.topic + '. tēma) uz ' + toId + ' (#' + toNode.master_anchor + ', ' + toNode.topic + '. tēma)'
          : 'Priekšnosacījums no ' + fromId + ' (#' + fromNode.master_anchor + ') uz ' + toId + ' (#' + toNode.master_anchor + ')';
        var edge = {
          id: fromId + '->' + toId,
          from: fromId,
          to: toId,
          fromTopic: fromNode.topic,
          toTopic: toNode.topic,
          fromAnchor: fromNode.master_anchor,
          toAnchor: toNode.master_anchor,
          targetHref: '#' + fromNode.mapNodeId,
          toHref: '#' + toNode.mapNodeId,
          kind: isCross ? 'cross-topic' : 'intra-topic',
          label_lv: edgeLabel
        };
        edges.push(edge);
        if (isCross) {
          crossTopicEdges.push(edge);
        }
      }
    }

    var topicRecords = topics.slice().sort(function (a, b) {
      return a.topic - b.topic;
    });
    var topicLayouts = [];
    for (i = 0; i < topicRecords.length; i += 1) {
      var tRec = topicRecords[i];
      var tNum = tRec.topic;
      var tNodes = [];
      var idx;
      for (idx = 0; idx < sortedIds.length; idx += 1) {
        var candidate = nodesById[sortedIds[idx]];
        if (candidate.topic === tNum) {
          tNodes.push(candidate);
        }
      }
      var layerBuckets = Object.create(null);
      var layerNums = [];
      for (idx = 0; idx < tNodes.length; idx += 1) {
        var ln = tNodes[idx].layer;
        if (!layerBuckets[ln]) {
          layerBuckets[ln] = [];
          layerNums.push(ln);
        }
        layerBuckets[ln].push(tNodes[idx]);
      }
      layerNums.sort(function (a, b) { return a - b; });
      var layers = [];
      for (idx = 0; idx < layerNums.length; idx += 1) {
        var lNum = layerNums[idx];
        var bucket = layerBuckets[lNum].slice().sort(function (a, b) {
          return asciiCompare(a.id, b.id);
        });
        var rows = chunkArray(bucket, wrapThreshold);
        layers.push({
          layer: lNum,
          nodeCount: bucket.length,
          wrapped: bucket.length > wrapThreshold,
          rowCount: rows.length,
          nodes: bucket,
          rows: rows
        });
      }
      topicLayouts.push({
        topic: tNum,
        name_lv: tRec.name_lv,
        anchorId: 'karte-tema-' + tNum,
        headingId: 'karte-tema-' + tNum + '-virsraksts',
        nodeCount: tNodes.length,
        layers: layers,
        asciiGraph: buildTopicAsciiGraph(tNum, layers, nodesById)
      });
    }

    return {
      rules: {
        layerRule: LAYOUT_RULES.layerRule,
        tieBreak: LAYOUT_RULES.tieBreak,
        wrapThreshold: wrapThreshold
      },
      totalNodes: sortedIds.length,
      totalEdges: edges.length,
      crossTopicEdgeCount: crossTopicEdges.length,
      maxLayer: maxLayer,
      nodesById: nodesById,
      edges: edges,
      crossTopicEdges: crossTopicEdges,
      topics: topicLayouts
    };
  }

  function buildTopicAsciiGraph(topicNum, layers, nodesById) {
    var lines = ['T' + topicNum + ' ASCII enkuru grafs:'];
    var i;
    for (i = 0; i < layers.length; i += 1) {
      var lyr = layers[i];
      var nodeLabels = [];
      var j;
      for (j = 0; j < lyr.nodes.length; j += 1) {
        var n = lyr.nodes[j];
        nodeLabels.push(n.id + ' (#' + n.master_anchor + ')');
      }
      lines.push('  L' + lyr.layer + ': ' + nodeLabels.join(' | '));
      for (j = 0; j < lyr.nodes.length; j += 1) {
        var target = lyr.nodes[j];
        var p;
        for (p = 0; p < target.prerequisites.length; p += 1) {
          var src = nodesById[target.prerequisites[p]];
          if (src.topic === topicNum) {
            lines.push('    ' + src.id + ' (#' + src.master_anchor + ') --> ' + target.id + ' (#' + target.master_anchor + ')');
          } else {
            lines.push('    ' + src.id + ' (#' + src.master_anchor + ') =[T' + src.topic + '->T' + topicNum + ']=> ' + target.id + ' (#' + target.master_anchor + ')');
          }
        }
      }
    }
    return lines.join('\n');
  }

  function makeElement(doc, tag, className, text) {
    var el = doc.createElement(tag);
    if (className) {
      el.className = className;
    }
    if (text !== undefined && text !== null) {
      el.textContent = String(text);
    }
    return el;
  }

  function clear(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function openConceptFromTrigger(conceptId, triggerEl, source, doc) {
    if (root.SimConceptDrawer && typeof root.SimConceptDrawer.openFromLink === 'function') {
      root.SimConceptDrawer.openFromLink({
        conceptId: conceptId,
        source: source || 'map',
        returnContext: {
          elementId: triggerEl && triggerEl.id ? triggerEl.id : null,
          triggerEl: triggerEl || null
        }
      }, doc);
    }
  }

  function render(coverageData, doc, options) {
    doc = doc || root.document;
    var container = doc && doc.getElementById ? doc.getElementById('karte') : null;
    if (!container) {
      return null;
    }
    var layout = computeLayout(coverageData, options);

    if (typeof container.className === 'string') {
      container.className = 'concept-map-region';
    }
    clear(container);

    var heading = makeElement(doc, 'h3', 'map-heading', 'Konceptu karte un priekšnosacījumu grafs');
    heading.id = 'karte-virsraksts';
    container.appendChild(heading);

    var meta = makeElement(
      doc,
      'p',
      'map-meta',
      layout.totalNodes + ' jēdzieni · ' + layout.topics.length + ' tēmas · ' +
      layout.totalEdges + ' priekšnosacījumu saites (' + layout.crossTopicEdgeCount +
      ' starptēmu saites) · deterministisks slāņu izkārtojums (rindas slieksnis: ' +
      layout.rules.wrapThreshold + ' mezgli).'
    );
    meta.id = 'karte-kopsavilkums';
    container.appendChild(meta);

    var nav = makeElement(doc, 'nav', 'map-topic-nav');
    nav.id = 'karte-temu-nav';
    nav.setAttribute('aria-label', 'Konceptu kartes tēmu navigācija');
    var navList = makeElement(doc, 'ul', 'coverage-nav-list');
    var i;
    for (i = 0; i < layout.topics.length; i += 1) {
      var tl = layout.topics[i];
      var navLi = makeElement(doc, 'li', 'coverage-nav-item');
      var navA = makeElement(doc, 'a', null, tl.topic + '. ' + tl.name_lv + ' (' + tl.nodeCount + ')');
      navA.setAttribute('href', '#' + tl.anchorId);
      navLi.appendChild(navA);
      navList.appendChild(navLi);
    }
    var crossNavLi = makeElement(doc, 'li', 'coverage-nav-item');
    var crossNavA = makeElement(doc, 'a', null, 'Starptēmu saites (' + layout.crossTopicEdgeCount + ')');
    crossNavA.setAttribute('href', '#karte-starptemu-saites');
    crossNavLi.appendChild(crossNavA);
    navList.appendChild(crossNavLi);
    nav.appendChild(navList);
    container.appendChild(nav);

    // Named cross-topic connections panel
    var crossSec = makeElement(doc, 'section', 'map-cross-section');
    crossSec.id = 'karte-starptemu-saites';
    crossSec.setAttribute('aria-labelledby', 'karte-starptemu-virsraksts');
    var crossH = makeElement(doc, 'h4', 'map-cross-heading', 'Starptēmu priekšnosacījumu saites (' + layout.crossTopicEdgeCount + ')');
    crossH.id = 'karte-starptemu-virsraksts';
    crossSec.appendChild(crossH);

    var crossList = makeElement(doc, 'ul', 'map-cross-list');
    for (i = 0; i < layout.crossTopicEdges.length; i += 1) {
      var ce = layout.crossTopicEdges[i];
      var ceLi = makeElement(doc, 'li', 'map-cross-item');
      ceLi.setAttribute('data-edge-id', ce.id);
      var ceLink = makeElement(
        doc,
        'a',
        'map-edge-link map-cross-edge-link',
        ce.from + ' (#' + ce.fromAnchor + ', T' + ce.fromTopic + ') → ' + ce.to + ' (#' + ce.toAnchor + ', T' + ce.toTopic + ')'
      );
      ceLink.id = 'karte-edge-' + ce.from + '-' + ce.to;
      ceLink.setAttribute('href', ce.toHref);
      ceLink.setAttribute('data-edge-from', ce.from);
      ceLink.setAttribute('data-edge-to', ce.to);
      ceLink.setAttribute('data-edge-kind', 'cross-topic');
      ceLink.setAttribute('aria-label', ce.label_lv);
      ceLi.appendChild(ceLink);

      var openTargetBtn = makeElement(doc, 'button', 'map-cross-open-btn', 'Atvērt ' + ce.to);
      openTargetBtn.type = 'button';
      openTargetBtn.id = 'karte-cross-open-' + ce.from + '-' + ce.to;
      openTargetBtn.setAttribute('data-concept-open', ce.to);
      openTargetBtn.setAttribute('aria-label', 'Atvērt mērķa koncepta ' + ce.to + ' atvilktni no starptēmu saites ' + ce.from + ' uz ' + ce.to);
      (function (conceptId, btnEl) {
        btnEl.addEventListener('click', function () {
          openConceptFromTrigger(conceptId, btnEl, 'map-cross-edge', doc);
        });
      })(ce.to, openTargetBtn);
      ceLi.appendChild(openTargetBtn);
      crossList.appendChild(ceLi);
    }
    crossSec.appendChild(crossList);
    container.appendChild(crossSec);

    // Per-topic layered regions
    for (i = 0; i < layout.topics.length; i += 1) {
      var tLayout = layout.topics[i];
      var tSec = makeElement(doc, 'section', 'map-topic');
      tSec.id = tLayout.anchorId;
      tSec.setAttribute('aria-labelledby', tLayout.headingId);
      tSec.setAttribute('data-topic', String(tLayout.topic));

      var tHead = makeElement(doc, 'h4', 'map-topic-heading', tLayout.topic + '. ' + tLayout.name_lv);
      tHead.id = tLayout.headingId;
      tSec.appendChild(tHead);

      var layerOl = makeElement(doc, 'ol', 'map-layers');
      layerOl.setAttribute('aria-label', tLayout.topic + '. tēmas priekšnosacījumu slāņi');

      var lIdx;
      for (lIdx = 0; lIdx < tLayout.layers.length; lIdx += 1) {
        var lyr = tLayout.layers[lIdx];
        var layerLi = makeElement(doc, 'li', 'map-layer');
        layerLi.setAttribute('data-layer', String(lyr.layer));
        layerLi.setAttribute('data-wrap-rows', String(lyr.rowCount));
        layerLi.setAttribute('data-wrapped', lyr.wrapped ? 'true' : 'false');

        var layerH = makeElement(
          doc,
          'h5',
          'map-layer-heading',
          'Slānis ' + lyr.layer + ' (' + lyr.nodeCount + (lyr.nodeCount === 1 ? ' jēdziens' : ' jēdzieni') +
          (lyr.wrapped ? ', sadalīts ' + lyr.rowCount + ' rindās' : '') + ')'
        );
        layerLi.appendChild(layerH);

        var rowsWrap = makeElement(doc, 'div', 'map-layer-rows');
        var rIdx;
        for (rIdx = 0; rIdx < lyr.rows.length; rIdx += 1) {
          var rowNodes = lyr.rows[rIdx];
          var rowUl = makeElement(doc, 'ul', 'map-row-nodes');
          rowUl.setAttribute('data-row', String(rIdx));
          rowUl.setAttribute('aria-label', 'Slāņa ' + lyr.layer + ' rinda ' + (rIdx + 1));

          var nIdx;
          for (nIdx = 0; nIdx < rowNodes.length; nIdx += 1) {
            var node = rowNodes[nIdx];
            var nodeLi = makeElement(doc, 'li', 'map-node');
            nodeLi.id = node.mapNodeId;
            nodeLi.setAttribute('data-concept-id', node.id);
            nodeLi.setAttribute('data-layer', String(node.layer));
            nodeLi.setAttribute('data-master-anchor', node.master_anchor);

            var nodeBtn = makeElement(doc, 'button', 'map-node-btn');
            nodeBtn.type = 'button';
            nodeBtn.id = node.mapButtonId;
            nodeBtn.setAttribute('data-concept-open', node.id);
            nodeBtn.setAttribute(
              'aria-label',
              node.id + ': ' + node.statement_lv + ' (#' + node.master_anchor + ', ' + node.layer + '. slānis)'
            );
            nodeBtn.appendChild(makeElement(doc, 'span', 'map-node-id', node.id));
            nodeBtn.appendChild(makeElement(doc, 'span', 'map-node-anchor', '#' + node.master_anchor));
            nodeBtn.appendChild(makeElement(doc, 'span', 'map-node-title', node.statement_lv));
            (function (conceptId, btnEl) {
              btnEl.addEventListener('click', function () {
                openConceptFromTrigger(conceptId, btnEl, 'map', doc);
              });
            })(node.id, nodeBtn);
            nodeLi.appendChild(nodeBtn);

            if (node.prerequisites.length > 0) {
              var edgeUl = makeElement(doc, 'ul', 'map-edge-list');
              edgeUl.setAttribute('aria-label', node.id + ' priekšnosacījumu saites');
              var pIdx;
              for (pIdx = 0; pIdx < node.prerequisites.length; pIdx += 1) {
                var prereqId = node.prerequisites[pIdx];
                var srcNode = layout.nodesById[prereqId];
                var isCross = srcNode.topic !== node.topic;
                var edgeLi = makeElement(doc, 'li', 'map-edge-item');
                var edgeA = makeElement(
                  doc,
                  'a',
                  isCross ? 'map-edge-link map-edge-cross' : 'map-edge-link',
                  '← ' + prereqId + ' (#' + srcNode.master_anchor + (isCross ? ', T' + srcNode.topic + ' → T' + node.topic : '') + ')'
                );
                edgeA.setAttribute('href', '#' + srcNode.mapNodeId);
                edgeA.setAttribute('data-edge-from', prereqId);
                edgeA.setAttribute('data-edge-to', node.id);
                edgeA.setAttribute('data-edge-kind', isCross ? 'cross-topic' : 'intra-topic');
                edgeA.setAttribute(
                  'aria-label',
                  (isCross ? 'Starptēmu priekšnosacījums no ' : 'Priekšnosacījums no ') +
                  prereqId + ' (#' + srcNode.master_anchor + ') uz ' + node.id + ' (#' + node.master_anchor + ')'
                );
                edgeLi.appendChild(edgeA);
                edgeUl.appendChild(edgeLi);
              }
              nodeLi.appendChild(edgeUl);
            }

            rowUl.appendChild(nodeLi);
          }
          rowsWrap.appendChild(rowUl);
        }
        layerLi.appendChild(rowsWrap);
        layerOl.appendChild(layerLi);
      }
      tSec.appendChild(layerOl);

      var asciiDetails = makeElement(doc, 'details', 'map-ascii-details');
      asciiDetails.appendChild(makeElement(doc, 'summary', 'map-ascii-summary', 'ASCII enkuru grafs (' + tLayout.topic + '. tēma)'));
      var asciiPre = makeElement(doc, 'pre', 'map-ascii-graph', tLayout.asciiGraph);
      asciiPre.id = 'karte-ascii-tema-' + tLayout.topic;
      asciiDetails.appendChild(asciiPre);
      tSec.appendChild(asciiDetails);

      container.appendChild(tSec);
    }

    return layout;
  }

  root.SimConceptMap = {
    LAYOUT_RULES: LAYOUT_RULES,
    DEFAULT_WRAP_THRESHOLD: DEFAULT_WRAP_THRESHOLD,
    ConceptMapError: ConceptMapError,
    assertAcyclic: assertAcyclic,
    computeLayout: computeLayout,
    buildTopicAsciiGraph: buildTopicAsciiGraph,
    render: render
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = root.SimConceptMap;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
