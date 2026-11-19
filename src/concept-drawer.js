(function (root) {
'use strict';
var DEFAULT_CHAIN_DEPTH = 2;
var OPEN_LINK_CONTRACT = {
version: 1,
owner: 'N07',
consumers: ['N08', 'N16', 'N28', 'N29'],
requiredFields: ['conceptId'],
optionalFields: ['source', 'returnContext'],
returnContextFields: ['elementId', 'triggerEl', 'anchor', 'labelLv']
};
function ConceptDrawerError(code, message, details) {
this.name = 'ConceptDrawerError';
this.code = code;
this.message = message;
this.details = details || {};
if (Error.captureStackTrace) {
Error.captureStackTrace(this, ConceptDrawerError);
} else {
this.stack = (new Error(message)).stack;
}
}
ConceptDrawerError.prototype = Object.create(Error.prototype);
ConceptDrawerError.prototype.constructor = ConceptDrawerError;
var state = {
initialized: false,
doc: null,
coverage: null,
byId: Object.create(null),
topicsByNum: Object.create(null),
summariesById: Object.create(null),
slotTemplates: null,
registryById: Object.create(null),
stack: [],
trace: [],
boundListeners: false
};
function asciiCompare(a, b) {
if (a < b) return -1;
if (a > b) return 1;
return 0;
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
function hydrateConceptRecord(conceptId) {
var outcome = state.byId[conceptId];
var sum = state.summariesById[conceptId];
if (!outcome || !sum) {
throw new ConceptDrawerError(
'E_DRAWER_UNKNOWN_CONCEPT',
'Konceptu atvilktnē nav atrasts jēdziens ' + String(conceptId) + '.',
{ conceptId: conceptId }
);
}
var templates = state.slotTemplates || {};
var figOwner = sum.figOwner || (sum.slots && sum.slots.figures && sum.slots.figures.owner_task);
var chainOwner = (sum.slots && sum.slots.chains && sum.slots.chains.owner_task) || templates.chainsOwner || 'N16';
var practiceOwner = (sum.slots && sum.slots.practice && sum.slots.practice.owner_task) || templates.practiceOwner || 'N30';
if (!figOwner || !chainOwner || !practiceOwner) {
throw new ConceptDrawerError(
'E_DRAWER_SLOT_OWNER',
'Konceptam ' + conceptId + ' trūkst slota atbildīgā uzdevuma identifikatora.',
{ conceptId: conceptId }
);
}
var families = (outcome.bindings && Array.isArray(outcome.bindings.practice_families))
? outcome.bindings.practice_families
: [];
var figStatus = sum.figStatus || (sum.slots && sum.slots.figures && sum.slots.figures.status) || ('pending-' + figOwner);
var figIds = sum.figIds || (sum.slots && sum.slots.figures && sum.slots.figures.figure_ids) || [];
var chainStatus = sum.chainStatus || (sum.slots && sum.slots.chains && sum.slots.chains.status) || ('pending-' + chainOwner);
var chainIds = sum.chainIds || (sum.slots && sum.slots.chains && sum.slots.chains.chain_ids) || [];
var slots = {
figures: (sum.slots && sum.slots.figures) || {
slot_id: 'SLOT-FIG-' + conceptId,
owner_task: figOwner,
status: figStatus,
figure_ids: figIds,
label_lv: figStatus.indexOf('authored-') === 0
? ('Saistītie attēli un shēmas (' + figOwner + ' — ' + figIds.length + ' shēmas)')
: ('Saistītie attēli un shēmas (' + figOwner + ' — gaidīšanas slots)')
},
chains: (sum.slots && sum.slots.chains) || {
slot_id: 'SLOT-CHAIN-' + conceptId,
owner_task: chainOwner,
status: chainStatus,
chain_ids: chainIds,
label_lv: typeof chainStatus === 'string' && chainStatus.indexOf('authored-') === 0
? ('Izstrādātā piemēra ķēde (' + chainOwner + ' — ' + chainIds.join(', ') + ')')
: ('Izstrādātā aprēķina / sprieduma piemēra ķēde (' + chainOwner + ' — gaidīšanas slots)')
},
practice: (sum.slots && sum.slots.practice) || {
slot_id: 'SLOT-PRAC-' + conceptId,
owner_task: practiceOwner,
status: 'pending-' + practiceOwner,
label_lv: 'Ierobežotās prakses ieeja (' + families.join(', ') + '; ' + practiceOwner + ' — gaidīšanas slots)',
families: families,
topic_anchor: '#prakse-tema-' + outcome.topic
}
};
return {
id: outcome.id,
topic: outcome.topic,
topic_name_lv: state.topicsByNum[outcome.topic] ? state.topicsByNum[outcome.topic].name_lv : '',
statement_lv: outcome.statement_lv,
master_path: outcome.master_path,
master_anchor: outcome.master_anchor,
master_heading_lv: outcome.master_heading_lv,
master_freeze_id: outcome.master_freeze_id,
prerequisites: Array.isArray(outcome.prerequisites) ? outcome.prerequisites.slice().sort(asciiCompare) : [],
summary_lv: sum.summary_lv,
conventions_refs: Array.isArray(sum.conventions_refs) ? sum.conventions_refs : [],
dissent_note_lv: sum.dissent_note_lv || null,
slots: slots
};
}
function buildPrerequisiteChain(conceptId) {
var visited = Object.create(null);
visited[conceptId] = true;
var queue = [];
var direct = (state.byId[conceptId] && Array.isArray(state.byId[conceptId].prerequisites))
? state.byId[conceptId].prerequisites.slice().sort(asciiCompare)
: [];
var i;
for (i = 0; i < direct.length; i += 1) {
visited[direct[i]] = true;
queue.push({ id: direct[i], depth: 1 });
}
var chain = [];
var head = 0;
var maxDepth = 0;
while (head < queue.length) {
var cur = queue[head];
head += 1;
if (cur.depth > maxDepth) {
maxDepth = cur.depth;
}
var outcome = state.byId[cur.id];
chain.push({
id: cur.id,
depth: cur.depth,
topic: outcome ? outcome.topic : null,
statement_lv: outcome ? outcome.statement_lv : '',
master_anchor: outcome ? outcome.master_anchor : ''
});
var nextPrereqs = (outcome && Array.isArray(outcome.prerequisites))
? outcome.prerequisites.slice().sort(asciiCompare)
: [];
for (i = 0; i < nextPrereqs.length; i += 1) {
var pid = nextPrereqs[i];
if (!visited[pid]) {
visited[pid] = true;
queue.push({ id: pid, depth: cur.depth + 1 });
}
}
}
chain.sort(function (a, b) {
if (a.depth !== b.depth) return a.depth - b.depth;
return asciiCompare(a.id, b.id);
});
return { items: chain, maxDepth: maxDepth };
}
function recordTrace(action, extra) {
var top = state.stack.length ? state.stack[state.stack.length - 1] : null;
var stackIds = [];
var i;
for (i = 0; i < state.stack.length; i += 1) {
stackIds.push(state.stack[i].conceptId);
}
var entry = {
seq: state.trace.length + 1,
action: action,
conceptId: (extra && extra.conceptId) || (top ? top.conceptId : null),
stackDepth: state.stack.length,
stackIds: stackIds,
source: (extra && extra.source) || (top ? top.source : null),
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
var drawer = doc && doc.getElementById ? doc.getElementById('concept-drawer') : null;
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
function renderTopFrame(doc) {
doc = doc || state.doc || root.document;
var backdrop = doc.getElementById('concept-drawer-backdrop');
var drawer = doc.getElementById('concept-drawer');
if (!backdrop || !drawer || state.stack.length === 0) {
return null;
}
var frame = state.stack[state.stack.length - 1];
var record = hydrateConceptRecord(frame.conceptId);
var titleEl = doc.getElementById('concept-drawer-title');
if (titleEl) {
titleEl.textContent = record.id + ' — ' + record.statement_lv;
}
var topicEl = doc.getElementById('concept-drawer-topic');
if (topicEl) {
topicEl.textContent = record.topic + '. tēma (' + record.topic_name_lv + ') · #' + record.master_anchor;
}
var breadcrumbEl = doc.getElementById('concept-drawer-breadcrumb');
var backBtn = doc.getElementById('concept-drawer-back');
if (breadcrumbEl) {
if (state.stack.length > 1) {
var trail = [];
var sIdx;
for (sIdx = 0; sIdx < state.stack.length; sIdx += 1) {
trail.push(state.stack[sIdx].conceptId);
}
breadcrumbEl.textContent = 'Atvilktnes ceļš: ' + trail.join(' → ');
breadcrumbEl.hidden = false;
} else {
breadcrumbEl.textContent = '';
breadcrumbEl.hidden = true;
}
}
if (backBtn) {
if (state.stack.length > 1) {
var prevId = state.stack[state.stack.length - 2].conceptId;
backBtn.textContent = 'Atpakaļ uz ' + prevId;
backBtn.hidden = false;
} else {
backBtn.hidden = true;
}
}
var summaryEl = doc.getElementById('concept-drawer-summary');
if (summaryEl) {
summaryEl.textContent = record.summary_lv;
}
var citationEl = doc.getElementById('concept-drawer-citation');
if (citationEl) {
citationEl.textContent = 'Meistara avots: ' + record.master_path + ' #' + record.master_anchor +
' («' + record.master_heading_lv + '», ' + record.master_freeze_id + ').';
}
var dissentEl = doc.getElementById('concept-drawer-dissent');
if (dissentEl) {
if (record.dissent_note_lv) {
dissentEl.textContent = 'Konvencija un avotu atšķirība: ' + record.dissent_note_lv;
dissentEl.hidden = false;
} else {
dissentEl.textContent = '';
dissentEl.hidden = true;
}
}
var prereqHost = doc.getElementById('concept-drawer-prereqs');
if (prereqHost) {
clear(prereqHost);
var chainData = buildPrerequisiteChain(record.id);
if (chainData.items.length === 0) {
prereqHost.appendChild(
makeElement(doc, 'p', 'drawer-empty-note', 'Nav iepriekšēju priekšnosacījumu (sākuma slāņa jēdziens).')
);
} else {
var visibleItems = [];
var cIdx;
for (cIdx = 0; cIdx < chainData.items.length; cIdx += 1) {
if (frame.chainExpanded || chainData.items[cIdx].depth <= DEFAULT_CHAIN_DEPTH) {
visibleItems.push(chainData.items[cIdx]);
}
}
var ul = makeElement(doc, 'ul', 'drawer-prereq-list');
for (cIdx = 0; cIdx < visibleItems.length; cIdx += 1) {
var item = visibleItems[cIdx];
var li = makeElement(doc, 'li', 'drawer-prereq-item');
var btn = makeElement(
doc,
'button',
'drawer-prereq-btn',
item.id + ' (' + item.depth + '. pakāpe, #' + item.master_anchor + ') — ' + item.statement_lv
);
btn.type = 'button';
btn.id = 'drawer-prereq-btn-' + item.id;
btn.setAttribute('data-concept-open', item.id);
btn.setAttribute('data-chain-depth', String(item.depth));
(function (targetConceptId, triggerBtn) {
triggerBtn.addEventListener('click', function () {
openFromLink({
conceptId: targetConceptId,
source: 'drawer-chain',
returnContext: {
elementId: triggerBtn.id,
triggerEl: triggerBtn
}
}, doc);
});
})(item.id, btn);
li.appendChild(btn);
ul.appendChild(li);
}
prereqHost.appendChild(ul);
if (chainData.maxDepth > DEFAULT_CHAIN_DEPTH) {
var toggleBtn = makeElement(
doc,
'button',
'btn-control drawer-chain-toggle',
frame.chainExpanded
? 'Saīsināt priekšnosacījumu ķēdi (līdz ' + DEFAULT_CHAIN_DEPTH + '. pakāpei)'
: 'Parādīt visu priekšnosacījumu ķēdi (' + chainData.items.length + ' jēdzieni, dziļums ' + chainData.maxDepth + ')'
);
toggleBtn.type = 'button';
toggleBtn.id = 'concept-drawer-chain-toggle';
toggleBtn.setAttribute('aria-expanded', frame.chainExpanded ? 'true' : 'false');
toggleBtn.addEventListener('click', function () {
frame.chainExpanded = !frame.chainExpanded;
recordTrace('toggle-chain', {
conceptId: frame.conceptId,
targetId: 'concept-drawer-chain-toggle'
});
renderTopFrame(doc);
focusElement(doc, null, 'concept-drawer-chain-toggle');
});
prereqHost.appendChild(toggleBtn);
}
}
}
var slotsHost = doc.getElementById('concept-drawer-slots');
if (slotsHost) {
clear(slotsHost);
var slotOrder = ['figures', 'chains', 'practice'];
var s;
for (s = 0; s < slotOrder.length; s += 1) {
var kind = slotOrder[s];
var slot = record.slots[kind];
var isFigAuthored = (kind === 'figures' && typeof slot.status === 'string' && slot.status.indexOf('authored-') === 0);
var isChainAuthored = (kind === 'chains' && typeof slot.status === 'string' && slot.status.indexOf('authored-') === 0);
var slotBox = makeElement(doc, 'div', (isFigAuthored || isChainAuthored) ? ('drawer-slot drawer-slot-' + kind) : 'pending-slot drawer-slot');
slotBox.id = 'drawer-slot-' + kind + '-' + record.id;
slotBox.setAttribute('data-slot-kind', kind);
slotBox.setAttribute('data-slot-id', slot.slot_id);
slotBox.setAttribute('data-slot-owner', slot.owner_task);
slotBox.setAttribute('data-slot-status', slot.status);
if (isFigAuthored) {
slotBox.appendChild(makeElement(doc, 'span', 'badge badge-official', slot.owner_task + ' — inline SVG attēli'));
slotBox.appendChild(makeElement(doc, 'p', 'drawer-slot-label', slot.label_lv));
if (root.SimFigures && typeof root.SimFigures.mountSlot === 'function') {
root.SimFigures.mountSlot(doc, slotBox, record.id, slot.figure_ids, { trigger: 'drawer-open' });
}
} else if (isChainAuthored) {
slotBox.appendChild(makeElement(doc, 'span', 'badge badge-official', slot.owner_task + ' — darba piemēra ķēde'));
slotBox.appendChild(makeElement(doc, 'p', 'drawer-slot-label', slot.label_lv));
if (root.SimChains && typeof root.SimChains.mountChain === 'function') {
var chainIds = slot.chain_ids || [];
for (var ci = 0; ci < chainIds.length; ci += 1) {
var chainHost = makeElement(doc, 'div', 'chain-slot');
slotBox.appendChild(chainHost);
try {
root.SimChains.mountChain(doc, chainHost, chainIds[ci], 'drawer-' + record.id);
} catch (chainError) {
chainHost.appendChild(makeElement(doc, 'p', 'chain-error', 'Darba piemēru ķēde nav ielādēta (' + (chainError.code || 'E_CHAIN') + ').'));
}
}
}
} else {
slotBox.appendChild(makeElement(doc, 'span', 'badge badge-pending', slot.owner_task + ' — gaidīšanas slots'));
slotBox.appendChild(makeElement(doc, 'p', 'drawer-slot-label', slot.label_lv));
}
slotsHost.appendChild(slotBox);
}
}
var statusEl = doc.getElementById('concept-drawer-status');
if (statusEl) {
statusEl.textContent = 'Atvērta koncepta atvilktne: ' + record.id + ' (#' + record.master_anchor + ').';
}
backdrop.hidden = false;
drawer.hidden = false;
setBackgroundInert(doc, true);
return record;
}
function bindDrawerChrome(doc) {
if (state.boundListeners || !doc) return;
var closeBtn = doc.getElementById('concept-drawer-close');
if (closeBtn) {
closeBtn.addEventListener('click', function () {
close(doc);
});
}
var backBtn = doc.getElementById('concept-drawer-back');
if (backBtn) {
backBtn.addEventListener('click', function () {
close(doc);
});
}
var drawer = doc.getElementById('concept-drawer');
if (drawer) {
drawer.addEventListener('keydown', function (event) {
if (!event || state.stack.length === 0) return;
if (event.key === 'Escape') {
if (typeof event.preventDefault === 'function') event.preventDefault();
close(doc);
return;
}
});
}
var backdrop = doc.getElementById('concept-drawer-backdrop');
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
var coverage = deps.coverage || (root.SimCoverage ? root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS) : null);
var summaries = deps.summaries || root.CONCEPT_DRAWER_DATA;
var registry = deps.registry || root.ANCHOR_REGISTRY || null;
if (!coverage || !Array.isArray(coverage.outcomes)) {
throw new ConceptDrawerError('E_DRAWER_NO_COVERAGE', 'Konceptu atvilktnei trūkst #sim-coverage datu.', {});
}
if (!summaries || !Array.isArray(summaries.concepts)) {
throw new ConceptDrawerError('E_DRAWER_NO_SUMMARIES', 'Konceptu atvilktnei trūkst konceptu kopsavilkumu datu.', {});
}
state.doc = doc;
state.coverage = coverage;
state.byId = Object.create(null);
state.topicsByNum = Object.create(null);
state.summariesById = Object.create(null);
state.registryById = Object.create(null);
state.slotTemplates = summaries.slotTemplates || null;
state.stack = [];
state.trace = [];
state.boundListeners = false;
var i;
for (i = 0; i < coverage.topics.length; i += 1) {
state.topicsByNum[coverage.topics[i].topic] = coverage.topics[i];
}
for (i = 0; i < coverage.outcomes.length; i += 1) {
state.byId[coverage.outcomes[i].id] = coverage.outcomes[i];
}
for (i = 0; i < summaries.concepts.length; i += 1) {
state.summariesById[summaries.concepts[i].id] = summaries.concepts[i];
}
if (registry && Array.isArray(registry.concepts)) {
for (i = 0; i < registry.concepts.length; i += 1) {
state.registryById[registry.concepts[i].concept_id] = registry.concepts[i];
}
}
bindDrawerChrome(doc);
state.initialized = true;
return getState();
}
function openFromLink(payload, doc) {
doc = doc || state.doc || root.document;
if (!state.initialized) {
init(doc);
}
if (!payload || typeof payload.conceptId !== 'string' || !payload.conceptId) {
throw new ConceptDrawerError('E_DRAWER_BAD_PAYLOAD', 'Atvēršanas pieprasījumā trūkst conceptId.', { payload: payload });
}
var ret = payload.returnContext || {};
var triggerEl = ret.triggerEl || payload.triggerEl || (doc && doc.activeElement) || null;
var triggerId = ret.elementId || (triggerEl && triggerEl.id) || null;
var source = payload.source || 'direct';
state.stack.push({
conceptId: payload.conceptId,
source: source,
returnTarget: triggerEl,
returnTargetId: triggerId,
chainExpanded: false,
depth: state.stack.length + 1
});
renderTopFrame(doc);
var focusOpts = payload.focusOpts || (payload.quiet ? { preventScroll: true } : null);
var focusedId = focusElement(doc, null, 'concept-drawer-close', focusOpts);
recordTrace('open', {
conceptId: payload.conceptId,
source: source,
targetId: focusedId,
restoredToId: triggerId
});
return getState();
}
function close(doc, options) {
doc = doc || state.doc || root.document;
options = options || {};
if (state.stack.length === 0) {
return getState();
}
var popped = state.stack.pop();
var restoredId = null;
var focusOpts = options.quiet ? { preventScroll: true } : null;
if (state.stack.length > 0) {
renderTopFrame(doc);
restoredId = focusElement(doc, null, popped.returnTargetId || 'concept-drawer-close', focusOpts);
recordTrace('close-nested', {
conceptId: popped.conceptId,
source: popped.source,
targetId: state.stack[state.stack.length - 1].conceptId,
restoredToId: restoredId
});
} else {
var backdrop = doc.getElementById('concept-drawer-backdrop');
var drawer = doc.getElementById('concept-drawer');
var slotsHost = doc.getElementById('concept-drawer-slots');
if (slotsHost) clear(slotsHost);
if (backdrop) backdrop.hidden = true;
if (drawer) drawer.hidden = true;
setBackgroundInert(doc, false);
restoredId = focusElement(doc, popped.returnTarget, popped.returnTargetId, focusOpts);
recordTrace('close-restore', {
conceptId: popped.conceptId,
source: popped.source,
restoredToId: restoredId
});
}
return getState();
}
function closeAll(doc) {
while (state.stack.length > 0) {
close(doc);
}
return getState();
}
function getState() {
var top = state.stack.length ? state.stack[state.stack.length - 1] : null;
var stackIds = [];
var i;
for (i = 0; i < state.stack.length; i += 1) {
stackIds.push(state.stack[i].conceptId);
}
return {
initialized: state.initialized,
isOpen: state.stack.length > 0,
stackDepth: state.stack.length,
stackIds: stackIds,
activeConceptId: top ? top.conceptId : null,
activeSource: top ? top.source : null,
activeChainExpanded: top ? top.chainExpanded : false
};
}
function getTrace() {
return state.trace.slice();
}
function clearTrace() {
state.trace = [];
}
root.SimConceptDrawer = {
DEFAULT_CHAIN_DEPTH: DEFAULT_CHAIN_DEPTH,
OPEN_LINK_CONTRACT: OPEN_LINK_CONTRACT,
ConceptDrawerError: ConceptDrawerError,
init: init,
open: openFromLink,
openFromLink: openFromLink,
close: close,
closeAll: closeAll,
hydrateConceptRecord: hydrateConceptRecord,
buildPrerequisiteChain: buildPrerequisiteChain,
getFocusableInsideDrawer: getFocusableInsideDrawer,
getState: getState,
getTrace: getTrace,
clearTrace: clearTrace
};
if (typeof module !== 'undefined' && module.exports) {
module.exports = root.SimConceptDrawer;
}
})(typeof globalThis !== 'undefined' ? globalThis : this);
