/* N18 drawn-response capture component.
 *
 * Records a drawn line or curve segment on a rendered figure as a geometric
 * payload in figure coordinates. The payload is device-agnostic by
 * construction: the pointer path and the keyboard path are the same ordered
 * list of points, and the projection onto the declared assessment grid is
 * performed by SimGraphScoring, so the scorer never learns which device drew
 * the line.
 *
 * The keyboard map steps the active point by the increments the engine
 * declares (N18-CAPTURE-KEY-01): the coarse x step is the grid step, so every
 * grid point is reachable; the fine x and y steps are a tenth of the
 * corresponding step and are never coarser than half the declared tolerance
 * band of the assessed axis, so the keyboard path is not structurally
 * penalised. The diagonal step moves the active point by (fine_x, fine_y) in
 * one action, which lets a straight line be traced exactly.
 *
 * The component owns no chemistry: it never inspects the learner's geometry
 * and never grades it. Validity classes belong to the engine.
 */
(function (root) {
'use strict';

var DEFAULTS = {
  pointerSampleRatio: 0.1
};

/* The keyboard map: arrow keys step the active point, Shift selects the fine
 * increment, Alt selects the diagonal increment, Enter commits the response
 * and Escape cancels it. */
var KEY_STEPS = {
  ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1]
};

function round12(value) { return Number(Number(value).toFixed(12)); }

function create(options) {
  var settings = Object.assign({}, DEFAULTS, options || {});
  var engine = settings.engine || root.SimGraphScoring;
  if (!engine || typeof engine.capturePath !== 'function') {
    throw new Error('SimGraphCapture needs SimGraphScoring.capturePath');
  }
  if (typeof engine.keyboardIncrements !== 'function') {
    throw new Error('SimGraphCapture needs SimGraphScoring.keyboardIncrements');
  }
  var context = settings.context;
  if (!context) { throw new Error('SimGraphCapture needs a capture context'); }
  var contextId = settings.contextId || context.id;
  if (!contextId) { throw new Error('SimGraphCapture needs a capture context id'); }
  var increments = engine.keyboardIncrements(contextId);
  var axes = context.axes || {};
  var grid = context.grid || {};
  var element = settings.element || null;
  var bounds = settings.bounds || null;
  var path = [];
  var active = null;
  var committed = null;
  var cancelled = false;

  function gridStep() {
    var step = Number(grid.step);
    return step > 0 ? step : (Number(grid.x_max) - Number(grid.x_min)) / 10;
  }

  /* Client coordinates to figure coordinates. The renderer owns the mapping
   * from pixels to the plotted rectangle; the capture only works in figure
   * coordinates. */
  function toFigure(clientX, clientY) {
    var box = bounds;
    if (!box && element && typeof element.getBoundingClientRect === 'function') {
      box = element.getBoundingClientRect();
    }
    if (!box) { return null; }
    var width = box.width || (box.right - box.left) || 1;
    var height = box.height || (box.bottom - box.top) || 1;
    var xAxis = axes.x || {};
    var yAxis = axes.y || {};
    var x = Number(xAxis.min) + ((clientX - (box.left || 0)) / width) *
      (Number(xAxis.max) - Number(xAxis.min));
    var y = Number(yAxis.max) - ((clientY - (box.top || 0)) / height) *
      (Number(yAxis.max) - Number(yAxis.min));
    return [round12(x), round12(y)];
  }

  function push(point) {
    if (!point) { return; }
    var rounded = [round12(point[0]), round12(point[1])];
    var last = path[path.length - 1];
    /* A movement that does not change x updates the current point instead of
     * adding a vertex. The keyboard's axis-aligned stepping would otherwise
     * leave vertical runs in the path, and the projection reads the path as a
     * function of x: a run would carry no y value of its own. Merging it
     * leaves the path a polyline through the placed points, which is exactly
     * what a pointer drag produces. */
    if (last && last[0] === rounded[0]) { path[path.length - 1] = rounded; return; }
    path.push(rounded);
  }

  /* Pointer sampling: a sample is taken only once the pointer has moved far
   * enough from the last sample, so the raw path stays light. The sampling
   * rate is an input detail only, because the payload is projected onto the
   * grid. */
  function pointerSample(point) {
    if (!point) { return; }
    var last = path[path.length - 1];
    var minDistance = gridStep() * settings.pointerSampleRatio;
    if (last) {
      var dx = point[0] - last[0];
      var dy = point[1] - last[1];
      if (Math.sqrt(dx * dx + dy * dy) < minDistance) { return; }
    }
    push(point);
  }

  /* Both devices share the same start: the first point of the response. */
  function begin(point) {
    path = [];
    cancelled = false;
    committed = null;
    active = point ? [round12(point[0]), round12(point[1])] : null;
    push(active);
    return active;
  }

  function move(point) { pointerSample(point); }

  function end() {
    if (path.length) { committed = payload(); }
    return committed;
  }

  function cancel() {
    path = [];
    active = null;
    committed = null;
    cancelled = true;
  }

  /* The keyboard map: the active point is stepped, and every position it
   * occupies is appended to the same raw path a pointer drag would produce. */
  function keyDown(event) {
    if (cancelled) { return null; }
    var key = event.key;
    if (key === 'Enter') { return end(); }
    if (key === 'Escape') { cancel(); return null; }
    var step = KEY_STEPS[key];
    if (!step) { return null; }
    var diagonal = Boolean(event.altKey);
    var fine = Boolean(event.shiftKey) || diagonal;
    var dx = fine ? increments.fine_x : increments.coarse_x;
    var dy = fine ? increments.fine_y : increments.coarse_y;
    if (!active) {
      var xAxis = axes.x || {};
      var yAxis = axes.y || {};
      active = [round12(Number(xAxis.min)), round12(Number(yAxis.max))];
      push(active);
      return active;
    }
    var moveX = step[0] * dx;
    /* The diagonal step moves x and y together: right goes up, left goes
     * down, so a straight line can be traced exactly in either direction. */
    var moveY = diagonal
      ? (step[0] !== 0 ? step[0] * increments.fine_y : step[1] * increments.fine_y)
      : step[1] * dy;
    active = [round12(active[0] + moveX), round12(active[1] + moveY)];
    push(active);
    return active;
  }

  /* A reading mark: the single marked point, captured with the same
   * device-agnostic structure as a drawn response. */
  function mark(point) {
    var target = point || active;
    if (!target) { return null; }
    return engine.capturePath(contextId, [[target[0], target[1]]]);
  }

  /* The payload: the raw path projected onto the declared grid. The component
   * never adds a device marker. */
  function payload() {
    return engine.capturePath(contextId, path);
  }

  return {
    contextId: contextId,
    increments: increments,
    pointer: { begin: begin, move: move, end: end },
    keyboard: { begin: begin, keyDown: keyDown, cancel: cancel },
    mark: mark,
    toFigure: toFigure,
    path: function () { return path.map(function (point) { return { x: point[0], y: point[1] }; }); },
    payload: payload,
    active: function () { return active ? { x: active[0], y: active[1] } : null; },
    committed: function () { return committed; },
    cancelled: function () { return cancelled; },
    reset: function () { path = []; active = null; committed = null; cancelled = false; }
  };
}

root.SimGraphCapture = {
  create: create,
  KEY_STEPS: KEY_STEPS,
  DEFAULTS: DEFAULTS
};

if (typeof module !== 'undefined' && module.exports) { module.exports = root.SimGraphCapture; }
})(typeof globalThis !== 'undefined' ? globalThis : this);
