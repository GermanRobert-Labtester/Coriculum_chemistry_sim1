/* N06 start view: single-sources the official seven-topic list inside
 * #sakums from the loaded #sim-coverage model so start screen and objectives
 * view share one truth. All text uses textContent; no innerHTML is used.
 */
(function (root) {
  'use strict';

  function renderStartTopics(coverage, doc) {
    doc = doc || root.document;
    if (!doc || typeof doc.getElementById !== 'function') {
      return 0;
    }
    var list = doc.getElementById('sakums-oficialas-temas');
    if (!list || !coverage || !Array.isArray(coverage.topics)) {
      return 0;
    }
    while (list.firstChild) {
      list.removeChild(list.firstChild);
    }
    var i;
    for (i = 0; i < coverage.topics.length; i += 1) {
      var topic = coverage.topics[i];
      var li = doc.createElement('li');
      var link = doc.createElement('a');
      link.setAttribute('href', '#tema-' + topic.topic);
      link.textContent = topic.name_lv;
      li.appendChild(link);
      list.appendChild(li);
    }
    return coverage.topics.length;
  }

  root.SimStartView = {
    renderStartTopics: renderStartTopics
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = root.SimStartView;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
