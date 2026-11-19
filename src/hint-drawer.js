(function (root) {
'use strict';
var MODE_BOUNDARY_ERROR_ID = 'E_HINT_EXAM_MODE_FORBIDDEN';
var ALLOWED_MODES = ['practice'];
function HintDrawerError(code, message, details) {
this.name = 'HintDrawerError';
this.code = code;
this.message = message;
this.details = details || {};
if (Error.captureStackTrace) {
Error.captureStackTrace(this, HintDrawerError);
} else {
this.stack = (new Error(message)).stack;
}
}
HintDrawerError.prototype = Object.create(Error.prototype);
HintDrawerError.prototype.constructor = HintDrawerError;
var state = {
initialized: false,
doc: null,
layersData: null,
familiesById: Object.create(null),
semanticsByLayer: Object.create(null),
defaultSession: null,
active: null,
trace: [],
boundListeners: false
};
function createSession() {
return {
schema_version: 1,
events: [],
items: Object.create(null)
};
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
function resolveMode(payload) {
if (payload && typeof payload.mode === 'string' && payload.mode.trim()) {
return payload.mode.trim().toLowerCase();
}
if (payload && payload.modeRegistry && typeof payload.modeRegistry.getMode === 'function') {
return String(payload.modeRegistry.getMode() || '').trim().toLowerCase();
}
if (root.SimModeRegistry && typeof root.SimModeRegistry.getMode === 'function') {
return String(root.SimModeRegistry.getMode() || '').trim().toLowerCase();
}
return 'practice';
}
function term(key, fallback) {
if (root.SimTerms && typeof root.SimTerms.getDefault === 'function' && root.SimTerms.getDefault()) {
return root.SimTerms.lookup(key);
}
return fallback;
}
function assertPracticeMode(mode, familyId) {
if (ALLOWED_MODES.indexOf(mode) === -1) {
throw new HintDrawerError(
MODE_BOUNDARY_ERROR_ID,
term('hint.exam.forbidden', 'Eksāmena režīmā palīdzības kāpnes nav pieejamas.'),
{ mode: mode, familyId: familyId || null }
);
}
}
function getEffectiveMaxDepth(family, variantClass) {
if (!family || family.status !== 'authored') {
return 0;
}
var depths = family.max_depth_by_variant_class || {};
var vc = variantClass || 'default';
if (typeof depths[vc] === 'number') {
return depths[vc];
}
if (typeof depths['default'] === 'number') {
return depths['default'];
}
return Array.isArray(family.layers) ? family.layers.length : 0;
}
function recordTrace(action, extra) {
var entry = {
seq: state.trace.length + 1,
action: action,
familyId: (extra && extra.familyId) || (state.active ? state.active.familyId : null),
itemId: (extra && extra.itemId) || (state.active ? state.active.itemId : null),
layer: (extra && extra.layer) || null,
targetId: (extra && extra.targetId) || null,
restoredToId: (extra && extra.restoredToId) || null
};
state.trace.push(entry);
return entry;
}
function focusElement(doc, el, fallbackId, focusOpts) {
var target = el;
if ((!target || typeof target.focus !== 'function') && fallbackId && doc && typeof doc.getElementById === 'function') {
target = doc.getElementById(fallbackId);
}
if (target && typeof target.focus === 'function') {
if (focusOpts && focusOpts.preventScroll) {
try {
target.focus({ preventScroll: true });
} catch (_err) {
target.focus();
}
} else {
target.focus();
}
return target.id || fallbackId || null;
}
return null;
}
function getFocusableInsideDrawer(doc) {
var drawer = doc && doc.getElementById ? doc.getElementById('hint-drawer') : null;
if (!drawer) return [];
var found = [];
function walk(node) {
if (!node || node.hidden) return;
var tag = node.tagName;
if (tag === 'BUTTON' || (tag === 'A' && node.getAttribute && node.getAttribute('href'))) {
if (!node.disabled) {
found.push(node);
}
}
var children = node.childNodes || [];
var i;
for (i = 0; i < children.length; i += 1) {
walk(children[i]);
}
}
walk(drawer);
return found;
}
function setBackgroundInert(doc, isInert) {
var ids = ['sim-header', 'sim-main', 'sim-footer'];
var i;
for (i = 0; i < ids.length; i += 1) {
var region = doc && doc.getElementById ? doc.getElementById(ids[i]) : null;
if (region && typeof region.setAttribute === 'function') {
if (isInert) {
region.setAttribute('aria-hidden', 'true');
} else if (typeof region.removeAttribute === 'function') {
region.removeAttribute('aria-hidden');
} else {
region.setAttribute('aria-hidden', 'false');
}
}
}
}
function formatCitationLabel(citation) {
if (!citation) return '';
var prefix = citation.kind === 'concept' ? 'Koncepts' : 'Konvencija';
return '[' + prefix + ': ' + citation.id + ']';
}
function renderActiveDrawer(doc) {
var backdrop = doc.getElementById('hint-drawer-backdrop');
var drawer = doc.getElementById('hint-drawer');
var titleEl = doc.getElementById('hint-drawer-title');
var bodyEl = doc.getElementById('hint-drawer-body');
if (!drawer || !bodyEl || !state.active) return;
var active = state.active;
var family = active.family;
var itemRec = active.itemRecord;
var maxDepth = active.maxDepth;
if (titleEl) {
titleEl.textContent = 'Palīdzības kāpnes: ' + family.family_id + ' — ' + family.title_lv;
}
clear(bodyEl);
var meta = makeElement(doc, 'p', 'hint-meta',
'Saime: ' + family.family_id + ' · Tēma ' + family.topic + ' · Uzdevums: ' + itemRec.itemId
);
bodyEl.appendChild(meta);
if (family.status !== 'authored') {
var gapBox = makeElement(doc, 'p', 'hint-gap-note',
family.gap_reason_lv || 'Šai uzdevumu saimei palīdzības kāpnes vēl nav sagatavotas (reģistrēts iztrūkums).'
);
gapBox.id = 'hint-gap-notice';
bodyEl.appendChild(gapBox);
if (backdrop) backdrop.hidden = false;
drawer.hidden = false;
setBackgroundInert(doc, true);
return;
}
if (family.depth_rule_applied && active.variantClass === 'one_step') {
var depthNote = makeElement(doc, 'p', 'hint-depth-note',
family.depth_rule_reason_lv || 'Dziļuma ierobežojums: viena soļa variantam maksimālais dziļums ir ' + maxDepth + ' slāņi.'
);
depthNote.id = 'hint-depth-note';
bodyEl.appendChild(depthNote);
}
var usedCount = itemRec.usedLayers.length;
var statusLine = makeElement(doc, 'p', 'hint-progress',
'Atklātie slāņi: ' + usedCount + ' no ' + maxDepth + ' (slāņu izmantošana ir informatīva, bez soda punktiem).'
);
statusLine.id = 'hint-progress-line';
bodyEl.appendChild(statusLine);
var ladder = makeElement(doc, 'ol', 'hint-ladder-list', null);
ladder.id = 'hint-drawer-ladder';
var i;
for (i = 0; i < usedCount; i += 1) {
var layerNum = itemRec.usedLayers[i];
var layerObj = family.layers[layerNum - 1];
if (!layerObj) continue;
var sem = state.semanticsByLayer[layerNum] || {};
var li = makeElement(doc, 'li', 'hint-layer-item', null);
li.id = 'hint-layer-item-' + layerNum;
var hdr = makeElement(doc, 'div', 'hint-layer-head',
layerNum + '. ' + (sem.label_lv || layerObj.kind)
);
li.appendChild(hdr);
var txt = makeElement(doc, 'p', 'hint-layer-text', layerObj.text_lv);
li.appendChild(txt);
var cit = makeElement(doc, 'span', 'hint-layer-citation', formatCitationLabel(layerObj.citation));
li.appendChild(cit);
if (layerObj.kind === 'concept_link' && layerObj.concept_id) {
var conceptBtn = makeElement(doc, 'button', 'drawer-action-btn hint-concept-btn',
term('hint.drawer.open_concept', 'Atvērt koncepta atvilktni') + ': ' + layerObj.concept_id
);
conceptBtn.type = 'button';
conceptBtn.id = 'hint-open-concept-' + layerObj.concept_id;
(function (cid, btnEl) {
btnEl.addEventListener('click', function () {
if (root.SimConceptDrawer && typeof root.SimConceptDrawer.openFromLink === 'function') {
root.SimConceptDrawer.openFromLink({
conceptId: cid,
source: 'hint-drawer',
quiet: active.quiet,
returnContext: {
elementId: btnEl.id,
triggerEl: btnEl,
labelLv: 'Palīdzības kāpnes'
}
}, doc);
}
});
})(layerObj.concept_id, conceptBtn);
li.appendChild(conceptBtn);
}
ladder.appendChild(li);
}
bodyEl.appendChild(ladder);
if (usedCount < maxDepth) {
var nextLayerNum = usedCount + 1;
var nextSem = state.semanticsByLayer[nextLayerNum] || {};
var revealBtn = makeElement(doc, 'button', 'cta-link cta-link-primary hint-reveal-btn',
'Atklāt ' + nextLayerNum + '. slāni: ' + (nextSem.label_lv || '') + ' (' + nextLayerNum + ' / ' + maxDepth + ')'
);
revealBtn.type = 'button';
revealBtn.id = 'hint-reveal-next';
revealBtn.addEventListener('click', function () {
revealNext(doc);
});
bodyEl.appendChild(revealBtn);
} else {
var doneNote = makeElement(doc, 'p', 'hint-done-note',
term('hint.drawer.max_depth_reached', 'Sasniegts šīs saimes maksimālais palīdzības dziļums.')
);
doneNote.id = 'hint-done-note';
bodyEl.appendChild(doneNote);
}
if (backdrop) backdrop.hidden = false;
drawer.hidden = false;
setBackgroundInert(doc, true);
}
function bindDrawerChrome(doc) {
if (state.boundListeners || !doc || typeof doc.getElementById !== 'function') {
return;
}
var closeBtn = doc.getElementById('hint-drawer-close');
if (closeBtn) {
closeBtn.addEventListener('click', function () {
close(doc);
});
}
var drawer = doc.getElementById('hint-drawer');
if (drawer) {
drawer.addEventListener('keydown', function (event) {
if (!event || !state.active) return;
if (event.key === 'Escape') {
if (typeof event.preventDefault === 'function') event.preventDefault();
close(doc);
return;
}
});
}
var backdrop = doc.getElementById('hint-drawer-backdrop');
if (backdrop) {
backdrop.addEventListener('click', function (event) {
if (event && event.target === backdrop) {
close(doc);
}
});
}
state.boundListeners = true;
}
function init(doc, deps) {
doc = doc || root.document;
deps = deps || {};
var layersData = deps.layersData || root.RECALL_LAYERS_DATA;
if (!layersData || !Array.isArray(layersData.families)) {
throw new HintDrawerError('E_HINT_NO_DATA', 'Palīdzības kāpnēm trūkst slāņu datu.', {});
}
state.doc = doc;
state.layersData = layersData;
state.familiesById = Object.create(null);
state.semanticsByLayer = Object.create(null);
state.defaultSession = deps.session || createSession();
state.active = null;
state.trace = [];
state.boundListeners = false;
var i;
var semantics = layersData.layer_semantics || [];
for (i = 0; i < semantics.length; i += 1) {
state.semanticsByLayer[semantics[i].layer] = semantics[i];
}
for (i = 0; i < layersData.families.length; i += 1) {
state.familiesById[layersData.families[i].family_id] = layersData.families[i];
}
bindDrawerChrome(doc);
state.initialized = true;
return getState();
}
function open(payload, doc) {
doc = doc || state.doc || root.document;
if (!state.initialized) {
init(doc);
}
if (!payload || typeof payload.familyId !== 'string' || !payload.familyId) {
throw new HintDrawerError('E_HINT_BAD_PAYLOAD', 'Palīdzības pieprasījumā trūkst familyId.', { payload: payload });
}
var mode = resolveMode(payload);
assertPracticeMode(mode, payload.familyId);
var family = state.familiesById[payload.familyId];
if (!family) {
throw new HintDrawerError(
'E_HINT_UNKNOWN_FAMILY',
'Palīdzības kāpnēs nav atrasta saime ' + String(payload.familyId) + '.',
{ familyId: payload.familyId }
);
}
var session = payload.session || state.defaultSession;
var itemId = payload.itemId || payload.familyId;
var variantClass = payload.variantClass || 'default';
var maxDepth = getEffectiveMaxDepth(family, variantClass);
if (!session.items[itemId]) {
session.items[itemId] = {
itemId: itemId,
familyId: family.family_id,
variantClass: variantClass,
maxDepth: maxDepth,
usedLayers: []
};
}
var itemRecord = session.items[itemId];
var ret = payload.returnContext || {};
var triggerEl = ret.triggerEl || payload.triggerEl || (doc && doc.activeElement) || null;
var triggerId = ret.elementId || (triggerEl && triggerEl.id) || null;
var quiet = Boolean(payload.quiet);
state.active = {
mode: mode,
familyId: family.family_id,
family: family,
itemId: itemId,
variantClass: variantClass,
maxDepth: maxDepth,
session: session,
itemRecord: itemRecord,
returnTarget: triggerEl,
returnTargetId: triggerId,
quiet: quiet
};
renderActiveDrawer(doc);
var focusOpts = payload.focusOpts || (quiet ? { preventScroll: true } : null);
var focusedId = focusElement(doc, null, 'hint-drawer-close', focusOpts);
recordTrace('open', {
familyId: family.family_id,
itemId: itemId,
targetId: focusedId,
restoredToId: triggerId
});
return getState();
}
function revealNext(doc) {
doc = doc || state.doc || root.document;
if (!state.active) {
return getState();
}
assertPracticeMode(state.active.mode, state.active.familyId);
var active = state.active;
var itemRec = active.itemRecord;
var maxDepth = active.maxDepth;
if (itemRec.usedLayers.length >= maxDepth) {
return getState();
}
var nextLayer = itemRec.usedLayers.length + 1;
var layerObj = active.family.layers[nextLayer - 1];
if (!layerObj) {
return getState();
}
itemRec.usedLayers.push(nextLayer);
active.session.events.push({
seq: active.session.events.length + 1,
event_type: 'hint_layer_revealed',
mode: active.mode,
item_id: itemRec.itemId,
family_id: itemRec.familyId,
variant_class: itemRec.variantClass,
layer_index: nextLayer,
layer_kind: layerObj.kind,
citation_kind: layerObj.citation ? layerObj.citation.kind : null,
citation_id: layerObj.citation ? layerObj.citation.id : null
});
renderActiveDrawer(doc);
var focusOpts = active.quiet ? { preventScroll: true } : null;
var nextFocusId = itemRec.usedLayers.length < maxDepth ? 'hint-reveal-next' : 'hint-drawer-close';
focusElement(doc, null, nextFocusId, focusOpts);
recordTrace('reveal', {
familyId: active.familyId,
itemId: active.itemId,
layer: nextLayer,
targetId: nextFocusId
});
return getState();
}
function close(doc, options) {
doc = doc || state.doc || root.document;
options = options || {};
if (!state.active) {
return getState();
}
var closing = state.active;
state.active = null;
var backdrop = doc.getElementById('hint-drawer-backdrop');
var drawer = doc.getElementById('hint-drawer');
if (backdrop) backdrop.hidden = true;
if (drawer) drawer.hidden = true;
setBackgroundInert(doc, false);
var focusOpts = options.quiet || closing.quiet ? { preventScroll: true } : null;
var restoredId = focusElement(doc, closing.returnTarget, closing.returnTargetId, focusOpts);
recordTrace('close-restore', {
familyId: closing.familyId,
itemId: closing.itemId,
restoredToId: restoredId
});
return getState();
}
function renderHelpControl(container, options, doc) {
doc = doc || state.doc || root.document;
options = options || {};
if (!container) return null;
var mode = resolveMode(options);
var btnId = options.buttonId || 'practice-help-btn';
var btn = makeElement(doc, 'button', 'cta-link hint-help-control', null);
btn.type = 'button';
btn.id = btnId;
btn.setAttribute('data-family-id', options.familyId || '');
if (ALLOWED_MODES.indexOf(mode) === -1) {
btn.disabled = true;
btn.setAttribute('aria-disabled', 'true');
btn.setAttribute('data-mode-boundary', MODE_BOUNDARY_ERROR_ID);
btn.textContent = 'Eksāmena režīmā palīdzība nav pieejama';
} else {
btn.textContent = options.labelLv || term('hint.practice.help_button', 'Palīdzība (kāpnes)');
btn.addEventListener('click', function () {
open({
mode: mode,
familyId: options.familyId,
itemId: options.itemId || options.familyId,
variantClass: options.variantClass || 'default',
session: options.session,
quiet: Boolean(options.quiet),
returnContext: {
elementId: btn.id,
triggerEl: btn
}
}, doc);
});
}
container.appendChild(btn);
return btn;
}
function renderUsageSummary(container, session, itemId, doc) {
doc = doc || state.doc || root.document;
if (!container) return null;
clear(container);
var rec = session && session.items ? session.items[itemId] : null;
var used = rec && Array.isArray(rec.usedLayers) ? rec.usedLayers : [];
var maxDepth = rec ? rec.maxDepth : 4;
var text;
if (used.length === 0) {
text = 'Izmantotā palīdzība: 0/' + maxDepth + ' slāņi — patstāvīgs risinājums (informatīva atzīme, bez soda punktiem).';
} else {
var names = [];
var i;
for (i = 0; i < used.length; i += 1) {
var sem = state.semanticsByLayer[used[i]];
names.push(used[i] + '. ' + (sem ? sem.label_lv : 'slānis'));
}
text = 'Izmantotā palīdzība: ' + used.length + '/' + maxDepth + ' slāņi (' + names.join(', ') + ') — informatīva atzīme, bez soda punktiem.';
}
var p = makeElement(doc, 'p', 'hint-usage-summary', text);
p.setAttribute('data-penalty', 'none');
container.appendChild(p);
return p;
}
function getRenderedText(doc) {
doc = doc || state.doc || root.document;
var drawer = doc && doc.getElementById ? doc.getElementById('hint-drawer') : null;
return drawer ? (drawer.textContent || '') : '';
}
function getState() {
var active = state.active;
return {
initialized: state.initialized,
isOpen: Boolean(active),
activeFamilyId: active ? active.familyId : null,
activeItemId: active ? active.itemId : null,
revealedCount: active ? active.itemRecord.usedLayers.length : 0,
revealedLayers: active ? active.itemRecord.usedLayers.slice() : [],
maxDepth: active ? active.maxDepth : 0
};
}
function getTrace() {
return state.trace.slice();
}
function clearTrace() {
state.trace = [];
}
root.SimHintDrawer = {
MODE_BOUNDARY_ERROR_ID: MODE_BOUNDARY_ERROR_ID,
HintDrawerError: HintDrawerError,
init: init,
createSession: createSession,
getEffectiveMaxDepth: getEffectiveMaxDepth,
open: open,
revealNext: revealNext,
close: close,
renderHelpControl: renderHelpControl,
renderUsageSummary: renderUsageSummary,
getRenderedText: getRenderedText,
getFocusableInsideDrawer: getFocusableInsideDrawer,
getState: getState,
getTrace: getTrace,
clearTrace: clearTrace
};
if (typeof module !== 'undefined' && module.exports) {
module.exports = root.SimHintDrawer;
}
})(typeof globalThis !== 'undefined' ? globalThis : this);
