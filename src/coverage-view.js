/* N02/N06 coverage & objectives view: renders topic navigation and the
 * 64-outcome objectives index from the loaded #sim-coverage island alone.
 * Both regions (plus the start-view official topic list) consume the same
 * model, so changing a topic name or outcome in #sim-coverage changes every
 * view's rendering in one place. All runtime text is written through
 * textContent; no innerHTML is used (preserving N35 markup-character escaping).
 */
(function (root) {
  'use strict';

  var SimCoverage = root.SimCoverage;
  if (!SimCoverage) {
    throw new Error('SimCoverage loader must be evaluated before the coverage view');
  }

  function buildModel(data) {
    var byId = Object.create(null);
    var i;
    for (i = 0; i < data.outcomes.length; i += 1) {
      byId[data.outcomes[i].id] = data.outcomes[i];
    }
    var nav = [];
    var sections = [];
    for (i = 0; i < data.topics.length; i += 1) {
      var topic = data.topics[i];
      var outcomeIds = Array.isArray(topic.outcome_ids) ? topic.outcome_ids : [];
      var outcomes = [];
      var j;
      for (j = 0; j < outcomeIds.length; j += 1) {
        var outcome = byId[outcomeIds[j]];
        if (!outcome) {
          throw new SimCoverage.CoverageError(
            'E_COVERAGE_TOPIC_LINK',
            '#sim-coverage tēma ' + topic.topic + ' atsaucas uz neesošu rezultātu ' + outcomeIds[j] + '.',
            { island: SimCoverage.ISLAND_ID, topic: topic.topic, outcome: outcomeIds[j] }
          );
        }
        outcomes.push({
          id: outcome.id,
          statement_lv: outcome.statement_lv,
          master_anchor: outcome.master_anchor
        });
      }
      nav.push({
        topic: topic.topic,
        label: topic.name_lv,
        count: outcomes.length,
        href: '#tema-' + topic.topic
      });
      sections.push({
        topic: topic.topic,
        id: 'tema-' + topic.topic,
        headingId: 'tema-' + topic.topic + '-virsraksts',
        title: topic.name_lv,
        count: outcomes.length,
        mapHref: '#karte-tema-' + topic.topic,
        practiceHref: '#prakse-tema-' + topic.topic,
        outcomes: outcomes
      });
    }
    return {
      title_lv: data.title_lv || 'Pārklājuma indekss',
      total: data.outcomes.length,
      nav: nav,
      sections: sections
    };
  }

  function makeElement(doc, tag, className, text) {
    var node = doc.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined && text !== null) {
      node.textContent = String(text);
    }
    return node;
  }

  function term(key, fallback) {
    if (root.SimTerms && typeof root.SimTerms.getDefault === 'function' && root.SimTerms.getDefault()) {
      return root.SimTerms.lookup(key);
    }
    return fallback;
  }

  function clear(node) {
    while (node.firstChild) {
      node.removeChild(node.firstChild);
    }
  }

  function render(data, doc) {
    doc = doc || root.document;
    var model = buildModel(data);
    var nav = doc.getElementById('coverage-nav');
    if (nav) {
      clear(nav);
      var list = makeElement(doc, 'ul', 'coverage-nav-list');
      var i;
      for (i = 0; i < model.nav.length; i += 1) {
        var item = model.nav[i];
        var li = makeElement(doc, 'li', 'coverage-nav-item');
        var link = makeElement(doc, 'a', null, item.label + ' (' + item.count + ')');
        link.setAttribute('href', item.href);
        li.appendChild(link);
        list.appendChild(li);
      }
      nav.appendChild(list);
    }

    var target = doc.getElementById('coverage-list');
    if (target) {
      clear(target);
      var s;
      for (s = 0; s < model.sections.length; s += 1) {
        var section = model.sections[s];
        var sectionNode = makeElement(doc, 'section', 'coverage-topic');
        sectionNode.id = section.id;
        sectionNode.setAttribute('aria-labelledby', section.headingId);
        var heading = makeElement(doc, 'h3', null, section.topic + '. ' + section.title);
        heading.id = section.headingId;
        sectionNode.appendChild(heading);

        var meta = makeElement(doc, 'div', 'coverage-topic-meta');
        meta.appendChild(makeElement(doc, 'p', 'coverage-count', section.count + ' ' + term('objectives.outcomes_count_suffix', 'rezultāti')));
        var mapLink = makeElement(doc, 'a', 'coverage-topic-link', term('objectives.map_link_short', 'Konceptu karte'));
        mapLink.setAttribute('href', section.mapHref);
        meta.appendChild(mapLink);
        var practiceLink = makeElement(doc, 'a', 'coverage-topic-link', term('objectives.practice_link_short', 'Praktiskie uzdevumi [N30]'));
        practiceLink.setAttribute('href', section.practiceHref);
        practiceLink.setAttribute('data-slot-owner', 'N30');
        meta.appendChild(practiceLink);
        sectionNode.appendChild(meta);

        var ol = makeElement(doc, 'ol', 'coverage-outcomes');
        var k;
        for (k = 0; k < section.outcomes.length; k += 1) {
          var outcome = section.outcomes[k];
          var li = makeElement(doc, 'li', 'coverage-outcome');
          li.id = 'rezultats-' + outcome.id;
          li.setAttribute('data-master-anchor', outcome.master_anchor);
          li.appendChild(makeElement(doc, 'span', 'coverage-outcome-id', outcome.id));
          li.appendChild(makeElement(doc, 'span', 'coverage-outcome-text', ' — ' + outcome.statement_lv));
          ol.appendChild(li);
        }
        sectionNode.appendChild(ol);
        target.appendChild(sectionNode);
      }
    }

    var total = doc.getElementById('coverage-total');
    if (total) {
      total.textContent = String(model.total);
    }
    return model;
  }

  SimCoverage.buildModel = buildModel;
  SimCoverage.render = render;

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SimCoverage;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
