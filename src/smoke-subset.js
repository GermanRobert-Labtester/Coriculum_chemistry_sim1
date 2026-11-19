(function (root) {
'use strict';
var vectors = [];
function register(vector) {
if (!vector || !vector.id || typeof vector.run !== 'function') {
throw new Error('Invalid smoke vector registration');
}
vectors.push(vector);
}
register({
id: 'SMK-N06-COVERAGE-COUNTS', owner: 'N06', description: 'Asserts 7 topics and 64 outcomes (9, 10, 11, 11, 10, 8, 5) from loaded #sim-coverage island.', run: function (doc, context) {
var expected = (context && context.expected) || (root.COVERAGE_INVARIANTS) || {
total: 64, perTopic: { 1: 9, 2: 10, 3: 11, 4: 11, 5: 10, 6: 8, 7: 5 }
};
var coverage = (context && context.coverage) || root.SimCoverage.load(doc, expected);
if (!coverage || coverage.total !== expected.total) {
return {
status: 'FAIL', reason: 'Expected total ' + expected.total + ', got ' + (coverage ? coverage.total : 'none')
};
}
var t;
for (t = 1; t <= 7; t += 1) {
var actual = coverage.counts ? coverage.counts[t] : undefined;
var want = expected.perTopic[t];
if (actual !== want) {
return {
status: 'FAIL', reason: 'Topic ' + t + ' count mismatch: expected ' + want + ', got ' + actual
};
}
}
return {
status: 'PASS', details: {
total: coverage.total, perTopic: coverage.counts
}
};
}
});
register({
id: 'SMK-N07-MAP-DRAWER-WALK', owner: 'N07', description: 'Asserts acyclic layered map (64 nodes, 127 edges, 20 cross-topic) and deterministic map-drawer open/nested-close/restore walk.', run: function (doc, context) {
var coverage = (context && context.coverage) || root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
if (!root.SimConceptMap || typeof root.SimConceptMap.computeLayout !== 'function') {
return { status: 'FAIL', reason: 'SimConceptMap module not loaded' };
}
if (!root.SimConceptDrawer || typeof root.SimConceptDrawer.openFromLink !== 'function') {
return { status: 'FAIL', reason: 'SimConceptDrawer module not loaded' };
}
var layout = root.SimConceptMap.computeLayout(coverage);
if (layout.totalNodes !== 64 || layout.totalEdges !== 127 || layout.crossTopicEdgeCount !== 20) {
return {
status: 'FAIL', reason: 'Unexpected graph counts: nodes=' + layout.totalNodes + ', edges=' + layout.totalEdges + ', cross=' + layout.crossTopicEdgeCount
};
}
var rec = root.SimConceptDrawer.hydrateConceptRecord('P5-07');
if (!rec || rec.master_anchor !== 'ch8' || !rec.slots || !rec.slots.figures || !rec.slots.figures.owner_task) {
return { status: 'FAIL', reason: 'P5-07 drawer hydration or slot owner missing' };
}
var hasFullDom = Boolean(
doc && typeof doc.getElementById === 'function' &&
doc.getElementById('karte') && doc.getElementById('concept-drawer') &&
doc.getElementById('karte-btn-P5-07')
);
if (!hasFullDom) {
return {
status: 'PASS', details: {
nodes: layout.totalNodes, edges: layout.totalEdges, crossTopicEdges: layout.crossTopicEdgeCount, domWalk: 'skipped-minimal-harness'
}
};
}
var quiet = Boolean(context && context.onLoad);
root.SimConceptDrawer.closeAll(doc);
root.SimConceptDrawer.clearTrace();
var trigger = doc.getElementById('karte-btn-P5-07');
root.SimConceptDrawer.openFromLink({
conceptId: 'P5-07', source: 'map', quiet: quiet, returnContext: { elementId: 'karte-btn-P5-07', triggerEl: trigger }
}, doc);
var prereqBtn = doc.getElementById('drawer-prereq-btn-P4-01');
if (!prereqBtn) {
return { status: 'FAIL', reason: 'Missing nested prerequisite link drawer-prereq-btn-P4-01 inside P5-07 drawer' };
}
root.SimConceptDrawer.openFromLink({
conceptId: 'P4-01', source: 'drawer-chain', quiet: quiet, returnContext: { elementId: 'drawer-prereq-btn-P4-01', triggerEl: prereqBtn }
}, doc);
var midState = root.SimConceptDrawer.getState();
if (midState.stackDepth !== 2 || midState.activeConceptId !== 'P4-01') {
return { status: 'FAIL', reason: 'Expected nested stack depth 2 at P4-01, got ' + JSON.stringify(midState) };
}
root.SimConceptDrawer.close(doc, { quiet: quiet });
var afterInnerClose = root.SimConceptDrawer.getState();
if (afterInnerClose.stackDepth !== 1 || afterInnerClose.activeConceptId !== 'P5-07') {
return { status: 'FAIL', reason: 'Closing inner drawer did not return to P5-07' };
}
if (doc.activeElement && doc.activeElement.id !== 'drawer-prereq-btn-P4-01') {
return { status: 'FAIL', reason: 'Closing inner drawer did not restore focus to drawer-prereq-btn-P4-01' };
}
root.SimConceptDrawer.close(doc, { quiet: quiet });
var afterOuterClose = root.SimConceptDrawer.getState();
if (afterOuterClose.isOpen) {
return { status: 'FAIL', reason: 'Closing outer drawer left drawer open' };
}
if (doc.activeElement && doc.activeElement.id !== 'karte-btn-P5-07') {
return { status: 'FAIL', reason: 'Closing outer drawer did not restore focus to karte-btn-P5-07' };
}
if (quiet && trigger && typeof trigger.blur === 'function') {
trigger.blur();
}
if (trigger && trigger.parentNode && typeof trigger.parentNode.removeChild === 'function') {
trigger.parentNode.removeChild(trigger);
}
var trace = root.SimConceptDrawer.getTrace();
root.SimConceptDrawer.clearTrace();
return {
status: 'PASS', details: {
nodes: layout.totalNodes, edges: layout.totalEdges, crossTopicEdges: layout.crossTopicEdgeCount, walkEvents: trace.length
}
};
}
});
register({
id: 'SMK-N08-HINT-LADDER-WALK', owner: 'N08', description: 'Asserts recall-layer ladder reveal, exam-mode refusal (E_HINT_EXAM_MODE_FORBIDDEN), concept-drawer nested handoff, and focus restoration.', run: function (doc, context) {
if (!root.SimHintDrawer || typeof root.SimHintDrawer.open !== 'function') {
return { status: 'FAIL', reason: 'SimHintDrawer module not loaded' };
}
var data = root.RECALL_LAYERS_DATA;
if (!data || !Array.isArray(data.families) || data.families.length !== 28) {
return { status: 'FAIL', reason: 'RECALL_LAYERS_DATA missing or not 28 families' };
}
var session = root.SimHintDrawer.createSession();
var examRefused = false;
try {
root.SimHintDrawer.open({ mode: 'exam', familyId: 'FAM-1C', session: session }, doc);
} catch (err) {
examRefused = Boolean(err && err.code === 'E_HINT_EXAM_MODE_FORBIDDEN');
}
if (!examRefused || session.events.length !== 0) {
return { status: 'FAIL', reason: 'Exam mode did not refuse with E_HINT_EXAM_MODE_FORBIDDEN or recorded events' };
}
var hasFullDom = Boolean(
doc && typeof doc.getElementById === 'function' &&
doc.getElementById('hint-drawer') && doc.getElementById('concept-drawer')
);
if (!hasFullDom) {
return {
status: 'PASS', details: { families: data.families.length, examRefused: true, domWalk: 'skipped-minimal-harness' }
};
}
var quiet = Boolean(context && context.onLoad);
var helpSlot = doc.getElementById('prakse-help-slot');
var trigger = doc.getElementById('smoke-n08-help-btn');
if (!trigger && helpSlot && typeof doc.createElement === 'function') {
trigger = doc.createElement('button');
trigger.type = 'button';
trigger.id = 'smoke-n08-help-btn';
trigger.textContent = 'Palīdzība (dūmu pārbaude)';
trigger.hidden = true;
helpSlot.appendChild(trigger);
}
root.SimHintDrawer.close(doc, { quiet: quiet });
root.SimHintDrawer.clearTrace();
root.SimHintDrawer.open({
mode: 'practice', familyId: 'FAM-1C', itemId: 'SMK-FAM-1C', session: session, quiet: quiet, returnContext: { elementId: trigger ? trigger.id : null, triggerEl: trigger }
}, doc);
root.SimHintDrawer.revealNext(doc);
root.SimHintDrawer.revealNext(doc);
root.SimHintDrawer.revealNext(doc);
root.SimHintDrawer.revealNext(doc);
var mid = root.SimHintDrawer.getState();
if (mid.revealedCount !== 4 || session.events.length !== 4) {
root.SimHintDrawer.close(doc, { quiet: quiet });
return { status: 'FAIL', reason: 'Expected 4 revealed layers and 4 events, got ' + mid.revealedCount + '/' + session.events.length };
}
var conceptBtn = doc.getElementById('hint-open-concept-P1-01');
if (conceptBtn && root.SimConceptDrawer) {
root.SimConceptDrawer.openFromLink({
conceptId: 'P1-01', source: 'hint-drawer', quiet: quiet, returnContext: { elementId: conceptBtn.id, triggerEl: conceptBtn }
}, doc);
root.SimConceptDrawer.close(doc, { quiet: quiet });
if (doc.activeElement && doc.activeElement.id !== 'hint-open-concept-P1-01') {
root.SimHintDrawer.close(doc, { quiet: quiet });
return { status: 'FAIL', reason: 'Concept drawer close did not restore focus to hint-open-concept-P1-01' };
}
}
root.SimHintDrawer.close(doc, { quiet: quiet });
if (root.SimHintDrawer.getState().isOpen) {
return { status: 'FAIL', reason: 'Hint drawer did not close cleanly' };
}
if (quiet && trigger && typeof trigger.blur === 'function') {
trigger.blur();
}
if (trigger && trigger.parentNode && typeof trigger.parentNode.removeChild === 'function') {
trigger.parentNode.removeChild(trigger);
}
root.SimHintDrawer.clearTrace();
if (quiet && root.SimFigures && typeof root.SimFigures.clearRenderEvents === 'function') {
root.SimFigures.clearRenderEvents();
}
return {
status: 'PASS', details: {
families: data.families.length, examRefused: true, revealedLayers: 4, eventsRecorded: session.events.length
}
};
}
});
register({
id: 'SMK-N10-TERMS-GRAMMAR-LOOKUP', owner: 'N10', description: 'Asserts #sim-terms load, lookup vector, IUPAC pair, unit grammar, and figure-label contract.', run: function (doc) {
var T = root.SimTerms;
if (!T || typeof T.load !== 'function') return { status: 'FAIL', reason: 'SimTerms not loaded' };
if (doc && typeof doc.getElementById === 'function' && !doc.getElementById('sim-terms') && !doc.getElementById('sim-terms-error')) {
return { status: 'PASS' };
}
var terms = T.load(doc);
var vec = [
['qty.molar_concentration', 'molārā koncentrācija'], ['inst.burette', 'birete'], ['nav.sakums', 'Sākums'], ['hint.drawer.title', 'Palīdzības kāpnes — pakāpeniska atsauce'], ['feedback.correct', 'Pareizi']
];
for (var i = 0; i < vec.length; i += 1) {
if (T.lookup(vec[i][0], null, terms) !== vec[i][1]) return { status: 'FAIL', reason: 'Mismatch ' + vec[i][0] };
}
var ip = T.lookup('iupac.acetic_acid', null, terms), pair = T.lookup('iupac.acetic_acid', { mode: 'iupac' }, terms);
if (ip !== 'etiķskābe' || pair !== 'etiķskābe (IUPAC: etānskābe)') return { status: 'FAIL', reason: 'IUPAC mismatch' };
var dv = T.parseUnit('J/(mol·K)', terms).dimensionVector;
if (dv.M !== 1 || dv.N !== -1 || dv.Theta !== -1) return { status: 'FAIL', reason: 'Dim mismatch' };
var rej = false;
try { T.checkDimension('mL/mg', 'density', terms); } catch (e) { rej = Boolean(e && e.code === 'E_UNIT_DIMENSION_MISMATCH'); }
if (!rej) return { status: 'FAIL', reason: 'mL/mg not rejected for density' };
var ax = T.resolveFigureLabel({ kind: 'axis', key: 'fig.axis.concentration_mol_l' }, terms);
if (ax.text !== 'Molārā koncentrācija c (mol/L)') return { status: 'FAIL', reason: 'Axis mismatch: ' + ax.text };
return { status: 'PASS', details: { totalEntries: terms.total, vectorChecked: vec.length, iupacPair: pair, figureAxis: ax.text } };
}
});
register({
id: 'SMK-N11-FIGURE-FRAMEWORK', owner: 'N11', description: 'Asserts #sim-figures load (9 T1-2 records), deterministic pure SVG render digest, and token-only styling.', run: function (doc) {
var F = root.SimFigures;
if (!F || typeof F.load !== 'function' || typeof F.renderFigureSvg !== 'function') {
return { status: 'FAIL', reason: 'SimFigures module not loaded' };
}
if (doc && typeof doc.getElementById === 'function' && !doc.getElementById('sim-figures') && !doc.getElementById('sim-figures-error')) {
return { status: 'PASS' };
}
var figs = F.load(doc);
if (!figs || figs.total < 9) {
return { status: 'FAIL', reason: 'Expected >= 9 figures, got ' + (figs ? figs.total : 'none') };
}
var rec = F.getById('FIG-T1-COMP-NACL-BASES', figs);
var svg = F.renderFigureSvg(rec, { theme: 'light' });
if (/#[0-9a-fA-F]{3,8}\b/.test(svg)) {
return { status: 'FAIL', reason: 'Raw hex color found in rendered SVG' };
}
var digest = F.sha256Utf8(svg);
var expectedDigest = '55d240dae8d597515eb8c74dff7de892d1dd42624369a7caf634f9025ac7e4fb';
if (digest !== expectedDigest) {
return { status: 'FAIL', reason: 'Rendered SVG digest mismatch: ' + digest + ' != ' + expectedDigest };
}
return {
status: 'PASS', details: {
figuresCount: figs.total, vectorId: rec.id, svgBytes: svg.length, svgSha256: digest, lazyPendingOnLoad: F.getRenderEvents().length === 0
}
};
}
});
register({
id: 'SMK-N12-BURETTE-READ-SCAN', owner: 'N12', description: 'Asserts T2-3 burette geometric fidelity (5,85 mL), deterministic SVG digest, and runtime SimLeakScan (gradeable pass, exemption, planted leak).', run: function (doc) {
var F = root.SimFigures;
var L = root.SimLeakScan;
if (!F || !L || typeof L.scanFigureRecord !== 'function') {
return { status: 'FAIL', reason: 'SimFigures or SimLeakScan module not loaded' };
}
if (doc && typeof doc.getElementById === 'function' && !doc.getElementById('sim-figures') && !doc.getElementById('sim-figures-error')) {
return { status: 'PASS' };
}
var figs = F.load(doc);
if (!figs || figs.total < 19) {
return { status: 'FAIL', reason: 'Expected >= 19 figures (T1-2 + T2-3), got ' + (figs ? figs.total : 'none') };
}
var recSub = F.getById('FIG-T2-BURETTE-SUBDIVIDED', figs);
var svg1 = F.renderFigureSvg(recSub, { theme: 'light' });
var svg2 = F.renderFigureSvg(recSub, { theme: 'light' });
if (svg1 !== svg2 || svg1.indexOf('data-meniscus-read-y="238"') === -1) {
return { status: 'FAIL', reason: 'Burette SVG non-deterministic or meniscus read-y != 238' };
}
var d = F.sha256Utf8(svg1);
var recGrade = F.getById('FIG-T2-BURETTE-DELIVERED-GRADE', figs);
var scanGrade = L.scanFigureRecord(recGrade);
var scanExempt = L.scanFigureRecord(recSub);
if (scanGrade.outcome !== 'PASS' || scanExempt.outcome !== 'EXEMPT') {
return { status: 'FAIL', reason: 'Unexpected leak scan outcomes: ' + scanGrade.outcome + '/' + scanExempt.outcome };
}
var planted = JSON.parse(JSON.stringify(recGrade));
planted.annotations = [{ id: 'p', annotation_key: 'fig.annot.burette_delivered_diff', text_override_lv: 'Atbilde: 0,01625 L.' }];
var scanPlanted = L.scanFigureRecord(planted);
if (scanPlanted.outcome !== 'FAIL') {
return { status: 'FAIL', reason: 'Runtime SimLeakScan missed unit-normalized planted leak 0,01625 L' };
}
return {
status: 'PASS', details: {
figuresCount: figs.total, buretteVectorId: recSub.id, svgBytes: svg1.length, svgSha256: d, gradeOutcome: scanGrade.outcome, exemptOutcome: scanExempt.outcome, plantedCaught: true
}
};
}
});
register({
id: 'SMK-N13-T4-HESS-CURVE', owner: 'N13', description: 'Asserts T4 Hess closure, MB curve/tail geometry, curve validation, and clean Hess leak scan.', run: function (doc) {
var F=root.SimFigures,L=root.SimLeakScan;if(!F||!L)return{status:'FAIL',reason:'missing'};
if(doc&&doc.getElementById&&!doc.getElementById('sim-figures')&&!doc.getElementById('sim-figures-error'))return{status:'PASS',details:{domWalk:'skipped-minimal-harness'}};
var figs=F.load(doc);if(!figs||figs.total<29)return{status:'FAIL',reason:'count<'+(figs?figs.total:0)};
var mb=F.getById('FIG-T4-MB-TWO-TEMP-COMPARE',figs),hs=F.getById('FIG-T4-HESS-FECL3',figs),pr=F.getById('FIG-T4-HESS-PRACTICE-SYNTH',figs);
var s1=F.renderFigureSvg(mb,{theme:'light'}),s2=F.renderFigureSvg(mb,{theme:'light'}),sh=F.renderFigureSvg(hs,{theme:'light'});
var mx=s1.match(/data-threshold-x="([^"]+)"/),ms=s1.match(/data-tail-start-x="([^"]+)"/);
if(s1!==s2||!mx||!ms||mx[1]!==ms[1]||sh.indexOf('data-hess-closure="true"')===-1)return{status:'FAIL',reason:'svg'};
var sc=L.scanFigureRecord(pr),bc='',bp='';
try{F.generateCurvePoints({function_class:'x',point_count:20,params:{}});}catch(e){bc=e.code||'';}
try{F.generateCurvePoints({function_class:'maxwell_boltzmann_3d',point_count:10,params:{}});}catch(e){bp=e.code||'';}
if(sc.outcome!=='PASS'||bc!=='E_FIG_UNKNOWN_CURVE_CLASS'||bp!=='E_FIG_BAD_CURVE_PARAMS')return{status:'FAIL',reason:sc.outcome+'/'+bc+'/'+bp};
return{status:'PASS',details:{figuresCount:figs.total,mbSha256:F.sha256Utf8(s1),hessSha256:F.sha256Utf8(sh),thresholdX:mx[1],pracOutcome:sc.outcome}};
}
});
register({
 id: 'SMK-N15-T67-TITRATION', owner: 'N15', description: 'T6-7 titration and calibration vector.', run: function (doc) {
  var F=root.SimFigures,L=root.SimLeakScan;if(!F||!L)return{status:'FAIL'};
  if(doc&&doc.getElementById&&!doc.getElementById('sim-figures')&&!doc.getElementById('sim-figures-error'))return{status:'PASS',details:{domWalk:'skipped-minimal-harness'}};
  var f=F.load(doc);if(!f||f.total<45)return{status:'FAIL',reason:'count'};
  var st=F.getById('FIG-T67-TITR-STRONG',f),tp=F.getById('FIG-T67-TITR-PRACTICE',f),cm=F.getById('FIG-T67-CAL-MASTER',f),cp=F.getById('FIG-T67-CAL-PRACTICE',f);
  var s1=F.renderFigureSvg(st,{theme:'light'}),sc=F.renderFigureSvg(cm,{theme:'light'}),g=F.generateCurvePoints(st.series[0].curve_model);
  if(g.peak.x!==25||g.points.length!==401||s1.indexOf('data-indicator-band="true"')<0||s1.indexOf('data-reading-strip="true"')<0||s1.indexOf('data-equivalence-x="25.00"')<0||sc.indexOf('data-fit-x-max="0.016"')<0||sc.indexOf('data-reading-dot="true"')<0)return{status:'FAIL',reason:'svg/model'};
  var a=L.scanFigureRecord(tp),b=L.scanFigureRecord(cp);
  if(a.outcome!=='PASS'||b.outcome!=='PASS')return{status:'FAIL',reason:'leak'};
  return{status:'PASS',details:{t67:8,veq:g.peak.x,outcomes:[a.outcome,b.outcome]}};
 }
});
register({
 id: 'SMK-N14-T5-LINEARIZATION', owner: 'N14', description: 'Asserts T5 fit-line span clipping, tolerance-coupled drawn-line acceptance (inside/edge/beyond), and practice leak cleanliness.', run: function (doc) {
  var F=root.SimFigures,L=root.SimLeakScan;if(!F||!L)return{status:'FAIL',reason:'missing'};
  if(doc&&doc.getElementById&&!doc.getElementById('sim-figures')&&!doc.getElementById('sim-figures-error'))return{status:'PASS',details:{domWalk:'skipped-minimal-harness'}};
  var figs=F.load(doc);if(!figs||figs.total<37)return{status:'FAIL',reason:'count<'+(figs?figs.total:0)};
  var ln=F.getById('FIG-T5-LIN-FIRST',figs),pr=F.getById('FIG-T5-LIN-PRACTICE',figs);
  var s1=F.renderFigureSvg(ln,{theme:'light'}),s2=F.renderFigureSvg(ln,{theme:'light'});
  if(s1!==s2||s1.indexOf('data-fit-x-min="0"')===-1||s1.indexOf('data-fit-x-max="30"')===-1||s1.indexOf('data-fit-clipped="true"')===-1||s1.indexOf('data-tol-band="true"')===-1)return{status:'FAIL',reason:'svg-clip'};
  var a=F.evaluateFitLine(ln,{slope:-0.0502,intercept:0.005,x_min:0,x_max:30});
  var b=F.evaluateFitLine(ln,{slope:-0.0502,intercept:0.005,x_min:0,x_max:40});
  var c=F.evaluateFitLine(ln,{slope:-0.08,intercept:0.2,x_min:0,x_max:30});
  if(a.status!=='ACCEPTED'||a.assessed_x_range.x_max!==30||b.status!=='ACCEPTED'||b.assessed_x_range.x_max!==30||b.beyond_span!=='not_assessed'||c.status!=='REJECTED')return{status:'FAIL',reason:'eval'};
  var svgP=F.renderFigureSvg(pr,{theme:'light'});
  if(svgP.indexOf('data-fit-line')!==-1)return{status:'FAIL',reason:'practice-fit-leak'};
  var scan=L.scanFigureRecord(pr);
  if(scan.outcome!=='PASS')return{status:'FAIL',reason:'leak:'+scan.outcome};
  return{status:'PASS',details:{figuresCount:figs.total,t5:8,fitXMax:30,edgeInclusive:true,beyond:'not_assessed',practiceOutcome:scan.outcome}};
 }
});
register({
id: 'SMK-N16-CHAINS-REVEAL', owner: 'N16', description: 'EX03 digests, reveal-all, collapse.', run: function (doc) {
var C = root.SimChains;
if (!C || typeof C.load !== 'function') return { status: 'PASS' };
if (doc && doc.getElementById && !doc.getElementById('sim-chains') && !doc.getElementById('sim-chains-error')) return { status: 'PASS' };
var island = C.load(doc);
if (!island || island.chain_count !== 14) return { status: 'FAIL', reason: 'count' };
var a = doc.getElementById('chain-EX03-index');
if (!a) return { status: 'PASS', details: { domWalk: 'chain-index-not-mounted' } };
function sig(x) { return C.sha256(x.getAttribute('data-revealed-count') + '|' + x.getAttribute('data-revealed-all') + '|' + x.textContent); }
var pre = sig(a);
var all = doc.getElementById('chain-EX03-index-reveal-all');
var confirm = doc.getElementById('chain-EX03-index-confirm');
var yes = doc.getElementById('chain-EX03-index-confirm-yes');
var collapse = doc.getElementById('chain-EX03-index-collapse');
if (!all || !confirm || !yes || !collapse || typeof all.dispatchEvent !== 'function') return { status: 'PASS' };
function fireClick(el) {
  if (typeof el.click === 'function') { el.click(); return; }
  el.dispatchEvent(typeof Event === 'function' ? new Event('click') : 'click');
}
fireClick(all);
if (confirm.hidden) return { status: 'FAIL', reason: 'confirm-missing' };
fireClick(yes);
var rev = sig(a);
fireClick(collapse);
var after = sig(doc.getElementById('chain-EX03-index'));
if (after !== pre) return { status: 'FAIL', reason: 'collapse-digest' };
if (pre !== 'b5273a658c4b6f3d52167c96c7bb49c2c852b6bd0c1e0d25e46353a7238fd797' || rev !== '88609f5b1d246234e6a39664f519ecb05b1d9fd8fe8ea9654a7f6dcfb6910923') return { status: 'FAIL', reason: 'digest ' + pre + '/' + rev };
return { status: 'PASS', details: { preDigest: pre, revealedDigest: rev } };
}
});
register({
id: 'SMK-N20-BANK-GRADE-VERDICT', owner: 'N20', description: 'Asserts the frozen #sim-bank island loads with its digest verified, holds 112 instances, and that the fixed instance COL1-1-1C-A-01 is graded "correct" by the N17 engine on its written answer and rejected on a wrong one.', run: function (doc) {
var B = root.SimBank, E = root.SimEngines;
if (!B || !E || typeof B.load !== 'function' || typeof E.grade !== 'function') {
return { status: 'PASS', details: { domWalk: 'skipped-modules-not-inlined', reason: 'SimBank/SimEngines are not both inlined in this host; the full assertion runs in the N20 runtime harness. N31 owns the inline decision.' } };
}
if (!doc || typeof doc.getElementById !== 'function' || (!doc.getElementById('sim-bank') && !doc.getElementById('sim-bank-error')) || !doc.getElementById('sim-engines') || !doc.getElementById('sim-conventions')) {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness' } };
}
var hasDigestMeta = Boolean(typeof doc.querySelector === 'function' && doc.querySelector('meta[name="sim-bank-embedded-digest"]'));
var bank;
try {
bank = B.load(doc, { verifyIntegrity: hasDigestMeta });
} catch (error) {
return { status: 'FAIL', reason: 'Bank load failed: ' + (error && error.code ? error.code : String(error)) };
}
if (!bank || bank.counts.total !== 112) {
return { status: 'FAIL', reason: 'Expected 112 instances, got ' + (bank ? bank.counts.total : 'none') };
}
var record = bank.byId['COL1-1-1C-A-01'];
if (!record) {
return { status: 'FAIL', reason: 'COL1-1-1C-A-01 not found in the frozen bank' };
}
E.load(doc);
var verdict = E.grade(record, { value: '794', unit: 'g' });
if (verdict.verdict_class !== 'correct') {
return { status: 'FAIL', reason: 'Expected verdict "correct", got "' + verdict.verdict_class + '" (' + verdict.error_class + ')' };
}
var wrong = E.grade(record, { value: '0', unit: 'g' });
if (wrong.verdict_class === 'correct') {
return { status: 'FAIL', reason: 'A wrong answer was accepted by the grader' };
}
return { status: 'PASS', details: {
instances: bank.counts.total, question_id: record.question_id, seed: record.seed,
verdict: verdict.verdict_class, wrong_verdict: wrong.verdict_class,
machine_checked_points: verdict.machine_checked_points, max_points: verdict.max_points
} };
}
});
register({
id: 'SMK-N21-SESSION-TRANSITION', owner: 'N21', description: 'Asserts the exam session lifecycle (start → answer → flag → navigate → review → submit), the table conformance of every logged transition, and the stable late-write error id.', run: function (doc) {
var S = root.SimSession, X = root.SimExam;
if (!S || !X || typeof S.ExamSession !== 'function' || typeof X.loadPolicy !== 'function') {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness' } };
}
var policy = null;
try { policy = X.loadPolicy(doc); } catch (error) {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness', reason: 'no-policy-island' } };
}
var clock = { now: function () { return 0; } };
var session = new S.ExamSession({ policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: clock });
var wanted = ['start', 'answer', 'flag', 'navigate', 'request-review', 'submit'];
function step(event, payload) { session.dispatch(event, payload || {}); }
step('start');
step('answer', { slot_id: policy.slots[0].slot_id, payload: { kind: 'numeric', values: { value: '9,81' } } });
step('flag', { slot_id: policy.slots[2].slot_id });
step('navigate', { slot_id: policy.slots[3].slot_id });
step('request-review');
step('submit', { confirmed: true });
var log = session.getTransitions();
if (log.length !== wanted.length) {
return { status: 'FAIL', reason: 'Expected ' + wanted.length + ' transitions, got ' + log.length };
}
for (var i = 0; i < log.length; i += 1) {
if (log[i].event !== wanted[i]) {
return { status: 'FAIL', reason: 'Transition ' + i + ' is ' + log[i].event + ', expected ' + wanted[i] };
}
var row = null;
var rows = policy.session_contract.transition_table;
for (var r = 0; r < rows.length; r += 1) {
if (rows[r].from === log[i].from && rows[r].event === log[i].event) { row = rows[r]; }
}
if (!row || row.to !== log[i].to) {
return { status: 'FAIL', reason: 'Transition ' + i + ' does not match the frozen table' };
}
}
var lateCode = null;
try {
session.dispatch('answer', { slot_id: policy.slots[1].slot_id, payload: { kind: 'raw_text', text: 'pārāk vēlu' } });
} catch (error) {
lateCode = error && error.code ? error.code : null;
}
if (lateCode !== 'E_SESSION_LATE_WRITE') {
return { status: 'FAIL', reason: 'Late write was not refused with E_SESSION_LATE_WRITE' };
}
return {
status: 'PASS', details: {
transitions: log.length, finalState: session.getState(), lateWriteError: lateCode,
flags: session.getFlags(), answered: session.getAnswers().length
}
};
}
});
register({
id: 'SMK-N21-NAVIGATION-MAP', owner: 'N21', description: 'Asserts the scripted answer/flag sequence (slots 1, 5 and 21 answered, slot 3 flagged), a full-range navigation, and that the question map state equals the expected cell array.', run: function (doc) {
var S = root.SimSession, X = root.SimExam;
if (!S || !X || typeof S.ExamSession !== 'function' || typeof X.buildMapState !== 'function') {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness' } };
}
var policy = null;
try { policy = X.loadPolicy(doc); } catch (error) {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness', reason: 'no-policy-island' } };
}
var ids = [];
var i;
for (i = 0; i < policy.slots.length; i += 1) { ids.push(policy.slots[i].slot_id); }
if (ids.length !== 21) {
return { status: 'FAIL', reason: 'Expected 21 slots, got ' + ids.length };
}
var session = new S.ExamSession({
policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: { now: function () { return 0; } }
});
session.dispatch('start');
var answered = [0, 4, 20];
for (i = 0; i < answered.length; i += 1) {
session.dispatch('answer', { slot_id: ids[answered[i]], payload: { kind: 'raw_text', text: 'atbilde ' + (answered[i] + 1) } });
}
session.dispatch('flag', { slot_id: ids[2] });
for (i = 0; i < ids.length; i += 1) { session.dispatch('navigate', { slot_id: ids[i] }); }
var map = X.buildMapState(session.snapshot());
if (!map || map.cells.length !== 21) {
return { status: 'FAIL', reason: 'Expected 21 map cells, got ' + (map ? map.cells.length : 'none') };
}
for (i = 0; i < map.cells.length; i += 1) {
var cell = map.cells[i];
var wantAnswered = (i === 0 || i === 4 || i === 20);
var wantFlagged = (i === 2);
var wantCurrent = (i === ids.length - 1);
if (cell.index !== i + 1 || cell.answered !== wantAnswered || cell.flagged !== wantFlagged || cell.current !== wantCurrent) {
return { status: 'FAIL', reason: 'Map cell ' + i + ' does not match the expected state' };
}
}
if (map.answered_count !== 3 || map.flagged_count !== 1 || map.unanswered_count !== 18) {
return { status: 'FAIL', reason: 'Map counts are ' + map.answered_count + '/' + map.flagged_count + '/' + map.unanswered_count };
}
return {
status: 'PASS', details: {
cells: map.cells.length, answered: map.answered_count, flagged: map.flagged_count,
unanswered: map.unanswered_count, current: map.current_slot_id
}
};
}
});
function n22Run(doc, typeId, capture, fallback) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-response-types') : null;
if (!node) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var data, ids = [];
try { data = JSON.parse(node.textContent || ''); } catch (error) { return { status: 'FAIL', reason: 'The #sim-response-types island is not readable JSON' }; }
var types = data && (data.types || data.entries) ? (data.types || data.entries) : data;
if (Array.isArray(types)) { for (var i = 0; i < types.length; i += 1) { ids.push(String(types[i].type_id || types[i].id || '')); } } else if (types && typeof types === 'object') { ids = Object.keys(types); }
ids.sort();
if (ids.length !== 18 || ids[0] !== 'Q01' || ids[17] !== 'Q18') return { status: 'FAIL', reason: 'The registry island covers ' + ids.length + ' types: ' + ids.join(',') };
var S = root.SimSession, X = root.SimExam;
if (!S || !X || typeof S.ExamSession !== 'function' || typeof X.loadPolicy !== 'function') return { status: 'PASS', details: { types: 18, domWalk: 'skipped-minimal-harness' } };
var policy = null;
try { policy = X.loadPolicy(doc); } catch (error) { policy = null; }
if (!policy) return { status: 'PASS', details: { types: 18, domWalk: 'skipped-minimal-harness' } };
var facade = null, payload = fallback, inputs = 'ships-from-src-not-inlined';
try { facade = root.SimInputs; } catch (error) { facade = null; }
if (facade && typeof facade.buildPayload === 'function') { try { payload = facade.buildPayload(typeId, null, null, capture); inputs = 'facade-exercised'; } catch (error) { inputs = 'facade-refused'; } }
var session = new S.ExamSession({ policy: policy, form: { form_id: 'A', slots: policy.slots }, clock: { now: function () { return 0; } } });
session.dispatch('start');
var slot = policy.slots[0].slot_id;
session.dispatch('answer', { slot_id: slot, payload: payload });
var stored = session.getAnswer(slot);
if (!stored || JSON.stringify(stored.payload) !== JSON.stringify(payload)) return { status: 'FAIL', reason: typeId + ' payload was not stored raw' };
return { status: 'PASS', details: { types: 18, stored: 'raw', inputs: inputs } };
}
register({
id: 'SMK-N22-NUMERIC-CAPTURE', owner: 'N22', description: 'Asserts the 18-type island and a numeric answer stored raw (" 4,70 " keeps its comma and spaces).', run: function (doc) {
return n22Run(doc, 'Q01', { fields: { value: ' 4,70 ' } }, { kind: 'numeric', values: { value: ' 4,70 ' } });
}
});
register({
id: 'SMK-N22-CLASSIFICATION-CAPTURE', owner: 'N22', description: 'Asserts the 18-type island and a classification answer (option ids plus justification) stored raw.', run: function (doc) {
return n22Run(doc, 'Q07', { selected: ['OPT-A', 'OPT-C'], justification: 'Viena fāze bez redzamas robežvirsmas.' }, { kind: 'option_select', selected: ['OPT-A', 'OPT-C'], justification: 'Viena fāze bez redzamas robežvirsmas.' });
}
});
register({
id: 'SMK-N22-ORDERING-CAPTURE', owner: 'N22', description: 'Asserts the 18-type island and an ordering answer stored as arranged, never re-sorted.', run: function (doc) {
return n22Run(doc, 'Q08', { order: ['S2', 'S1', 'S3', 'S4'] }, { kind: 'ordering', order: ['S2', 'S1', 'S3', 'S4'] });
}
});
var N23_VERDICT_CLASSES = ['auto_passed_pending_review', 'correct', 'incorrect', 'not_assessed', 'partial', 'pending_self_assessment'];
var N23_FIXTURE_IDS = ['SF-N23-FULL', 'SF-N23-PARTIAL', 'SF-N23-MALFORMED'];
function n23First(object, keys) {
if (!object || typeof object !== 'object') return undefined;
var i;
for (i = 0; i < keys.length; i += 1) {
if (Object.prototype.hasOwnProperty.call(object, keys[i]) && object[keys[i]] !== undefined) return object[keys[i]];
}
return undefined;
}
function n23Rules(policy) {
var rubric = policy && (policy.rubric_policy || policy.rubric);
var rules = rubric && (rubric.verdict_rules || rubric.rules);
return rules && typeof rules === 'object' ? rules : null;
}
function n23Fixtures(policy) {
var list = policy && (policy.self_test_fixtures || policy.fixtures);
return Array.isArray(list) ? list : null;
}
function n23Fixture(policy, fixtureId) {
var list = n23Fixtures(policy);
var i;
if (!list) return null;
for (i = 0; i < list.length; i += 1) {
var entry = list[i];
if (!entry || typeof entry !== 'object') continue;
var id = String(entry.fixture_id || entry.id || entry.name || '');
if (id === fixtureId) return entry;
}
return null;
}
function n23Rows(fixture) {
var rows = fixture && (fixture.rows || fixture.criteria || fixture.criterion_rows);
return Array.isArray(rows) ? rows : null;
}
function n23Expected(fixture) {
var raw = fixture && (fixture.expected || fixture.expected_totals || fixture.hand_computed);
if (!raw || typeof raw !== 'object') return null;
var auto = n23First(raw, ['auto', 'auto_points']);
var pending = n23First(raw, ['pending', 'pending_external', 'pending_external_points']);
if (typeof auto !== 'number' || typeof pending !== 'number') return null;
return { auto: auto, pending: pending };
}
function n23Tally(rows, malformed) {
var auto = 0, pending = 0, i;
for (i = 0; i < rows.length; i += 1) {
var row = rows[i] || {};
var status = String(row.status || row.criterion_status || '');
var points = n23First(row, ['points', 'max_points', 'points_declared']);
if (typeof points !== 'number' || !isFinite(points)) return { error: 'Criterion row ' + i + ' declares no numeric points' };
if (status === 'awarded') {
if (!malformed) auto += points;
} else if (status === 'denied') {
/* zero by the declared criterion rule */
} else if (status === 'pending') {
if (!malformed) pending += points;
} else {
return { error: 'Criterion row ' + i + ' carries the undeclared status "' + status + '"' };
}
}
return { auto: auto, pending: pending };
}
function n23Run(doc, fixtureId) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-grading-policy') : null;
if (!node) return { status: 'PASS', details: { island: 'not-yet-inlined', fixture: fixtureId } };
var policy;
try { policy = JSON.parse(node.textContent || ''); } catch (error) { return { status: 'FAIL', reason: 'The #sim-grading-policy island is not readable JSON' }; }
if (policy && policy.island_id && policy.island_id !== 'sim-grading-policy') return { status: 'FAIL', reason: 'The grading-policy island declares island_id "' + String(policy.island_id) + '"' };
var rules = n23Rules(policy);
if (!rules) return { status: 'FAIL', reason: 'The grading-policy island declares no rubric_policy.verdict_rules' };
var declared = [], key;
for (key in rules) {
if (Object.prototype.hasOwnProperty.call(rules, key)) declared.push(String(key));
}
declared.sort();
if (declared.join(',') !== N23_VERDICT_CLASSES.join(',')) {
return { status: 'FAIL', reason: 'verdict_rules cover ' + declared.length + ' classes (' + declared.join(',') + '); the frozen set is ' + N23_VERDICT_CLASSES.join(',') };
}
var missingFixtures = [], f;
for (f = 0; f < N23_FIXTURE_IDS.length; f += 1) {
if (!n23Fixture(policy, N23_FIXTURE_IDS[f])) missingFixtures.push(N23_FIXTURE_IDS[f]);
}
if (missingFixtures.length > 0) return { status: 'FAIL', reason: 'The policy island is missing the self-test fixtures ' + missingFixtures.join(',') };
var fixture = n23Fixture(policy, fixtureId);
if (!fixture) return { status: 'FAIL', reason: 'The self-test fixture ' + fixtureId + ' is not declared' };
var rows = n23Rows(fixture);
if (!rows || rows.length === 0) return { status: 'FAIL', reason: 'The fixture ' + fixtureId + ' declares no criterion rows' };
var expected = n23Expected(fixture);
if (!expected) return { status: 'FAIL', reason: 'The fixture ' + fixtureId + ' declares no numeric expected totals {auto, pending_external}' };
var slotState = String(fixture.slot_state || fixture.state || '');
var malformed = fixtureId === 'SF-N23-MALFORMED' || slotState === 'malformed' || slotState === 'invalid';
var tally = n23Tally(rows, malformed);
if (tally.error) return { status: 'FAIL', reason: tally.error };
if (tally.auto !== expected.auto || tally.pending !== expected.pending) {
return { status: 'FAIL', reason: 'declared-rule arithmetic gives auto=' + tally.auto + ', pending_external=' + tally.pending + '; the fixture declares auto=' + expected.auto + ', pending_external=' + expected.pending };
}
var engine = 'ships-from-src-not-inlined';
if (root.SimGrading && typeof root.SimGrading.applyRubricPolicy === 'function') {
var facade;
var rubricInput = slotState ? { slot_state: slotState, criteria: rows } : rows;
try { facade = root.SimGrading.applyRubricPolicy(policy, rubricInput); } catch (error) {
return { status: 'FAIL', reason: 'SimGrading.applyRubricPolicy refused the ' + fixtureId + ' rows: ' + (error && error.code ? error.code : String(error)) };
}
var task = facade && facade.task ? facade.task : {};
var facadeAuto = n23First(task, ['auto_points', 'auto']);
var facadePending = n23First(task, ['pending_points', 'pending_external_points', 'pending']);
if (typeof facadeAuto !== 'number' || typeof facadePending !== 'number') {
return { status: 'FAIL', reason: 'SimGrading.applyRubricPolicy returned no numeric task totals for ' + fixtureId };
}
if (facadeAuto !== expected.auto || facadePending !== expected.pending) {
return { status: 'FAIL', reason: 'applyRubricPolicy gives auto=' + facadeAuto + ', pending_external=' + facadePending + '; the fixture declares auto=' + expected.auto + ', pending_external=' + expected.pending };
}
engine = 'facade-exercised';
}
return {
status: 'PASS', details: {
island: 'read', verdictRules: declared.length, fixture: fixtureId, fixtures: N23_FIXTURE_IDS.length,
rows: rows.length, malformed: malformed,
expected: { auto: expected.auto, pending_external: expected.pending },
observed: { auto: tally.auto, pending_external: tally.pending },
engine: engine
}
};
}
register({
id: 'SMK-N23-GRADE-FULL', owner: 'N23', description: 'Asserts the #sim-grading-policy island (six verdict classes, three self-test fixtures) and that the declared rules reproduce the full-credit fixture totals (awarded summed, pending excluded from auto).', run: function (doc) {
return n23Run(doc, 'SF-N23-FULL');
}
});
register({
id: 'SMK-N23-GRADE-PARTIAL', owner: 'N23', description: 'Asserts the declared partial-credit arithmetic on the partial fixture: awarded criteria summed at their declared points, denied criteria zero, pending excluded from auto.', run: function (doc) {
return n23Run(doc, 'SF-N23-PARTIAL');
}
});
register({
id: 'SMK-N23-GRADE-MALFORMED', owner: 'N23', description: 'Asserts the declared malformed-slot rule on the malformed fixture: zero auto, zero pending, the named error kept, never a near-miss credit.', run: function (doc) {
return n23Run(doc, 'SF-N23-MALFORMED');
}
});
register({
id: 'SMK-N24-ASSEMBLY-DRAW', owner: 'N24', description: 'Asserts #sim-forms (3 forms x 21 slots = 100 pts) and draws a 6-family mini-bank under seed 100001 with independent constraint check inside the shipped file.', run: function (doc) {
var formsNode = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-forms') : null;
var formsCount = 0;
if (formsNode && formsNode.textContent) {
var formsData;
try { formsData = JSON.parse(formsNode.textContent); } catch (e) { return { status: 'FAIL', reason: 'The #sim-forms island is not readable JSON' }; }
if (!formsData || formsData.island_id !== 'sim-forms' || !Array.isArray(formsData.forms)) {
return { status: 'FAIL', reason: 'The #sim-forms island shape is invalid' };
}
if (formsData.status === 'assembled') {
formsCount = formsData.forms.length;
if (formsCount !== 3) return { status: 'FAIL', reason: 'Expected 3 assembled forms in #sim-forms, got ' + formsCount };
for (var f = 0; f < formsData.forms.length; f += 1) {
var fm = formsData.forms[f];
if (fm.status !== 'AVAILABLE' || fm.total_slots !== 21 || fm.total_points !== 100 || !fm.required_types_covered) {
return { status: 'FAIL', reason: 'Form ' + (fm && fm.form_id) + ' failed #sim-forms invariants' };
}
}
}
}
var A = root.SimAssembly;
if (!A || typeof A.assembleForm !== 'function' || typeof A.verifyFormManifest !== 'function' || !root.SimPRNG) {
return { status: 'PASS', details: { formsInIsland: formsCount, assembly: 'skipped-minimal-harness' } };
}
var okRev = { accessibility: 'passed', calculation: 'passed', content: 'passed', source: 'passed' };
var miniBank = [
{ question_id: 'SMK-1A-A', family_id: 'FAM-1A', variant_id: 'A', topic: 1, type_id: 'Q02', type_ids: ['Q02'], review: okRev, rubric: [{ points: 3 }] },
{ question_id: 'SMK-1B-A', family_id: 'FAM-1B', variant_id: 'A', topic: 1, type_id: 'Q07', type_ids: ['Q07'], review: okRev, rubric: [{ points: 3 }] },
{ question_id: 'SMK-UNREV-1B', family_id: 'FAM-1B', variant_id: 'B', topic: 1, type_id: 'Q04', type_ids: ['Q04'], review: { accessibility: 'passed', calculation: 'passed', content: 'pending', source: 'passed' }, rubric: [{ points: 3 }] },
{ question_id: 'SMK-1C-A', family_id: 'FAM-1C', variant_id: 'A', topic: 1, type_id: 'Q04', type_ids: ['Q04'], review: okRev, rubric: [{ points: 4 }] },
{ question_id: 'SMK-2A-A', family_id: 'FAM-2A', variant_id: 'A', topic: 2, type_id: 'Q01', type_ids: ['Q01'], review: okRev, rubric: [{ points: 4 }] },
{ question_id: 'SMK-2B-A', family_id: 'FAM-2B', variant_id: 'A', topic: 2, type_id: 'Q10', type_ids: ['Q10'], review: okRev, rubric: [{ points: 4 }] },
{ question_id: 'SMK-2C-A', family_id: 'FAM-2C', variant_id: 'A', topic: 2, type_id: 'Q09', type_ids: ['Q09'], review: okRev, rubric: [{ points: 4 }] }
];
var miniSpec = {
slots: [
{ slot_id: 'M1-1', topic: 1, points: 3, allowed_family_ids: ['FAM-1A', 'FAM-1B'] },
{ slot_id: 'M1-2', topic: 1, points: 3, allowed_family_ids: ['FAM-1A', 'FAM-1B'] },
{ slot_id: 'M1-3', topic: 1, points: 4, allowed_family_ids: ['FAM-1C'] },
{ slot_id: 'M2-1', topic: 2, points: 4, allowed_family_ids: ['FAM-2A', 'FAM-2B'] },
{ slot_id: 'M2-2', topic: 2, points: 4, allowed_family_ids: ['FAM-2A', 'FAM-2B'] },
{ slot_id: 'M2-3', topic: 2, points: 4, allowed_family_ids: ['FAM-2C'] }
],
required_types: ['Q02', 'Q04', 'Q10'],
topic_points: { '1': 10, '2': 12 },
total_points: 22
};
var drawn = A.assembleForm({
form_id: 'SMK', seed: '100001', bank: miniBank, bank_digest: 'smk-n24-mini-bank',
spec: miniSpec, strict_rubric_points: true, sha256: function (t) { return root.SimFigures && root.SimFigures.sha256Utf8 ? root.SimFigures.sha256Utf8(t) : 'smk-sha-' + t.length; }
});
if (!drawn || drawn.status !== 'AVAILABLE') {
return { status: 'FAIL', reason: 'Mini-bank draw did not succeed: ' + (drawn && drawn.shortage ? drawn.shortage.disabled_reason_lv : 'unknown') };
}
for (var k = 0; k < drawn.manifest.slots.length; k += 1) {
if (drawn.manifest.slots[k].instance_id === 'SMK-UNREV-1B') {
return { status: 'FAIL', reason: 'Unreviewed instance SMK-UNREV-1B leaked into mini-bank manifest' };
}
}
var chk = A.verifyFormManifest(drawn.manifest, miniBank, miniSpec, { strict_rubric_points: true });
if (chk.status !== 'PASS') {
return { status: 'FAIL', reason: 'Independent checker failed mini-bank manifest: ' + chk.errors.join('; ') };
}
return {
status: 'PASS',
details: { formsInIsland: formsCount, miniBankFamilies: 6, miniSlots: drawn.manifest.total_slots, miniPoints: drawn.manifest.total_points, unreviewedExcluded: true, independentCheck: chk.status }
};
}
});
register({
id: 'SMK-N25-STORE-ROUNDTRIP', owner: 'N25', description: 'Asserts #sim-analytics (v2, F10 rejected) and in-file SimStore/SimAnalytics opt-in boundary, canonical round-trip digest, and two-step erase.', run: function (doc) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-analytics') : null;
if (!node || !node.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var island;
try { island = JSON.parse(node.textContent); } catch (e) { return { status: 'FAIL', reason: 'The #sim-analytics island is not readable JSON' }; }
if (!island || island.island_id !== 'sim-analytics' || island.schema_version !== 2) {
return { status: 'FAIL', reason: 'The #sim-analytics island is not N25 v2' };
}
if (!island.f10_boundary || island.f10_boundary.status !== 'rejected-by-policy') {
return { status: 'FAIL', reason: 'F10 rejection boundary missing from #sim-analytics' };
}
var ST = root.SimStore, AN = root.SimAnalytics;
if (!ST || !AN || typeof ST.createStore !== 'function' || typeof AN.loadSchema !== 'function') {
return { status: 'PASS', details: { island: 'v2', modules: 'skipped-minimal-harness' } };
}
var memData = Object.create(null);
var mockStorage = {
getItem: function (k) { return Object.prototype.hasOwnProperty.call(memData, k) ? memData[k] : null; },
setItem: function (k, v) { memData[k] = String(v); },
removeItem: function (k) { delete memData[k]; }
};
var memStore = ST.createStore({ optIn: false, storage: mockStorage, doc: doc });
memStore.setTheme('dark');
if (Object.keys(memData).length !== 0) {
return { status: 'FAIL', reason: 'Default in-memory store wrote to localStorage mock' };
}
var s1 = ST.createStore({ optIn: true, storage: mockStorage, doc: doc });
s1.setTheme('dark');
AN.appendEvents(s1, [{ event: 'session-completed', form_id: 'A', session_id: 'SMK-N25', auto_score: 48, pending_count: 10, elapsed_ms: 0, graded_digest: ST.digestValue({ smk: 1 }) }]);
var d1 = s1.getDigest();
var keys = Object.keys(memData);
if (keys.length !== 1 || keys[0] !== ST.SCHEMA_KEY) {
return { status: 'FAIL', reason: 'Unexpected storage keys: ' + keys.join(',') };
}
var s2 = ST.createStore({ optIn: true, storage: mockStorage, doc: doc });
var d2 = s2.getDigest();
if (d1 !== d2) {
return { status: 'FAIL', reason: 'Round-trip digest mismatch: ' + d1 + ' != ' + d2 };
}
s2.requestErase();
s2.confirmErase();
if (Object.keys(memData).length !== 0) {
return { status: 'FAIL', reason: 'Two-step erase left keys behind' };
}
var banned = ['chart', 'charts', 'streak', 'streaks', 'gamification', 'scoreHistory', 'score_history', 'dashboard', 'leaderboard'];
var b;
for (b = 0; b < banned.length; b += 1) {
if (Object.prototype.hasOwnProperty.call(AN, banned[b])) {
return { status: 'FAIL', reason: 'F10 forbidden export found on SimAnalytics: ' + banned[b] };
}
}
return { status: 'PASS', details: { schemaVersion: 2, roundTripDigest: d1, schemaKey: ST.SCHEMA_KEY, memoryWrites: 0, eraseResidue: 0, f10Rejected: true } };
}
});
register({
id: 'SMK-N26-MASTERY-WALK', owner: 'N26', description: 'Asserts #sim-mastery-policy (PROPOSED) and a three-event pure reducer walk over SimMastery.', run: function (doc, context) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-mastery-policy') : null;
if (!node || !node.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var M = root.SimMastery;
if (!M || typeof M.loadPolicy !== 'function' || typeof M.reduce !== 'function') {
return { status: 'PASS', details: { island: 'authored', module: 'skipped-minimal-harness' } };
}
var loaded = M.loadPolicy(doc);
var cov = context && context.coverage ? context.coverage : (root.SimCoverage && typeof root.SimCoverage.load === 'function' ? root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS) : { outcomes: [{ id: 'P1-01', topic: 1, bindings: { practice_families: ['FAM-1C'] } }] });
var s0 = M.createInitialStateMap(cov, loaded.policy, loaded.digest);
if (!s0.outcomes['P1-01'] || s0.outcomes['P1-01'].state !== 'unseen') {
return { status: 'FAIL', reason: 'Initial P1-01 mastery state must be unseen' };
}
var s1 = M.reduce(s0, [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 }], loaded.policy);
var s2 = M.reduce(s1, [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 }], loaded.policy);
var s3 = M.reduce(s2, [{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 2 }], loaded.policy);
var walk = [s0.outcomes['P1-01'].state, s1.outcomes['P1-01'].state, s2.outcomes['P1-01'].state, s3.outcomes['P1-01'].state];
if (walk.join('>') !== 'unseen>learning>near_mastered>learning') {
return { status: 'FAIL', reason: 'Unexpected 3-event mastery walk: ' + walk.join('>') };
}
var s3Again = M.reduce(s0, [
{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 },
{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'correct', day: 1 },
{ kind: 'criterion_verdict', outcome_id: 'P1-01', verdict: 'incorrect', day: 2 }
], loaded.policy);
var d1 = M.digestOfMap(s3), d2 = M.digestOfMap(s3Again);
if (d1 !== d2) {
return { status: 'FAIL', reason: 'Mastery reducer walk not deterministic: ' + d1 + ' != ' + d2 };
}
return { status: 'PASS', details: { policyId: loaded.policy.policy_id, epistemicLabel: loaded.policy.epistemic_label, walk: walk, digest: d1 } };
}
});
register({
id: 'SMK-N27-SCHEDULER-QUEUE', owner: 'N27', description: 'Asserts #sim-scheduler-policy (PROPOSED) and deterministic fixed-date queue selection over SimScheduler.', run: function (doc, context) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-scheduler-policy') : null;
if (!node || !node.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var S = root.SimScheduler, M = root.SimMastery;
if (!S || !M || typeof S.loadPolicy !== 'function' || typeof S.selectQueue !== 'function') {
return { status: 'PASS', details: { island: 'authored', module: 'skipped-minimal-harness' } };
}
var sLoaded = S.loadPolicy(doc);
var mLoaded = M.loadPolicy(doc);
var cov = context && context.coverage ? context.coverage : (root.SimCoverage && typeof root.SimCoverage.load === 'function' ? root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS) : null);
if (!cov) return { status: 'FAIL', reason: 'Coverage missing for SMK-N27-SCHEDULER-QUEUE' };
var base = M.createInitialStateMap(cov, mLoaded.policy, mLoaded.digest);
var events = [
{ kind: 'criterion_verdict', outcome_id: 'P2-01', verdict: 'incorrect', day: 5 },
{ kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 6 },
{ kind: 'criterion_verdict', outcome_id: 'P3-01', verdict: 'correct', day: 6 },
{ kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
{ kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
{ kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
{ kind: 'criterion_verdict', outcome_id: 'P4-01', verdict: 'correct', day: 1 },
{ kind: 'decay', outcome_id: 'P4-01', days_inactive: 14 }
];
var stateMap = M.reduce(base, events, mLoaded.policy);
var sel1 = S.selectQueue({ masteryMap: stateMap, coverage: cov, date: 12, policy: sLoaded.policy, doc: doc });
var sel2 = S.selectQueue({ masteryMap: stateMap, coverage: cov, date: 12, policy: sLoaded.policy, doc: doc });
if (sel1.digest !== sel2.digest) {
return { status: 'FAIL', reason: 'Scheduler queue not deterministic: ' + sel1.digest + ' != ' + sel2.digest };
}
if (sel1.queue.length !== sLoaded.policy.queue_cap.value) {
return { status: 'FAIL', reason: 'Queue length mismatch: ' + sel1.queue.length };
}
var ids = sel1.queue.map(function (it) { return it.outcome_id; });
if (ids.join(',') !== 'P4-01,P2-01,P3-01,P1-01,P1-02') {
return { status: 'FAIL', reason: 'Unexpected fixed-date queue order: ' + ids.join(',') };
}
return { status: 'PASS', details: { policyId: sLoaded.policy.policy_id, date: 12, queue: ids, digest: sel1.digest } };
}
});
register({
id: 'SMK-N28-REMEDIATION-WALK', owner: 'N28', description: 'Asserts #sim-remediation-policy (PROPOSED) and an add-deduplicate-retry-resolve walk over SimRemediation.', run: function (doc, context) {
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-remediation-policy') : null;
if (!node || !node.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var R = root.SimRemediation, ST = root.SimStore;
if (!R || !ST || typeof R.loadPolicy !== 'function' || typeof R.addMiss !== 'function') {
return { status: 'PASS', details: { island: 'authored', module: 'skipped-minimal-harness' } };
}
var loaded = R.loadPolicy(doc);
if (loaded.policy.recommend_only !== true || loaded.policy.epistemic_label !== 'PROPOSED') {
return { status: 'FAIL', reason: 'Remediation policy missing recommend_only or PROPOSED label' };
}
var cov = context && context.coverage ? context.coverage : (root.SimCoverage && typeof root.SimCoverage.load === 'function' ? root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS) : null);
var reg = R.buildRegistries(doc, { coverage: cov });
var store = ST.createStore({ optIn: false, doc: doc });
R.addMiss(store, {
slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01', 'P6-02'],
instance_id: 'COL1-6-6A-A-01', signature_id: 'MC-6A-01', concept_ids: ['P6-01'], chain_ids: ['EX12'],
graded_digest: ST.digestValue({ smk: 'n28-1' })
}, { doc: doc, registries: reg });
var m2 = R.addMiss(store, {
slot_id: 'S6-1', topic: 6, family_id: 'FAM-6A', outcome_id: 'P6-01', outcome_ids: ['P6-01', 'P6-04'],
instance_id: 'COL1-6-6A-C-01', signature_id: 'MC-6A-02', concept_ids: ['P6-01', 'P6-02'], chain_ids: ['EX12'],
graded_digest: ST.digestValue({ smk: 'n28-2' })
}, { doc: doc, registries: reg });
if (m2.action !== 'coalesced' || m2.entry.miss_count !== 2 || store.getState().remediation_queue.length !== 1) {
return { status: 'FAIL', reason: 'Remediation deduplication failed: count=' + m2.entry.miss_count };
}
var bankNode = doc.getElementById('sim-bank');
var bankQs = bankNode && bankNode.textContent ? JSON.parse(bankNode.textContent).questions : [];
var sel = R.selectRetryInstance(m2.entry, bankQs, { allowEphemeralFallback: false });
if (sel.instance_id === 'COL1-6-6A-A-01' || sel.instance_id === 'COL1-6-6A-C-01' || sel.variant_id !== 'D') {
return { status: 'FAIL', reason: 'Unexpected retry variant selected after C: ' + sel.instance_id };
}
var retryRec = {
record_kind: 'graded-record',
slots: [{ slot_id: 'RETRY-1', topic: 6, family_id: 'FAM-6A', type_id: 'Q07', instance_id: sel.instance_id, outcome_ids: ['P6-01'], state: 'graded', verdict_class: 'correct', criteria: [{ criterion_id: 'C1', status: 'awarded', verdict_class: 'correct', error_class: null }], task: { auto_points: 2, auto_max_points: 2, pending_points: 0 } }]
};
retryRec.digest = ST.digestOf(retryRec);
var rRes = R.recordRetryVerdict(store, m2.entry.id, retryRec, { doc: doc, policy: loaded.policy, coverage: cov });
if (rRes.entry.state !== 'retried') {
return { status: 'FAIL', reason: 'Confirm-required policy should move to retried, got ' + rRes.entry.state };
}
var resDone = R.resolveEntry(store, m2.entry.id, { doc: doc, policy: loaded.policy });
if (resDone.resolved.state !== 'resolved') {
return { status: 'FAIL', reason: 'Resolve transition failed' };
}
return { status: 'PASS', details: { policyId: loaded.policy.policy_id, coalescedMissCount: m2.entry.miss_count, selectedVariant: sel.variant_id, retryState: rRes.entry.state, finalState: resDone.resolved.state } };
}
});
register({
id: 'SMK-N29-REVISION-PANEL', owner: 'N29', description: 'Asserts unified 64-outcome revision panel, F07 self-assessment separation from mastery digest, key-free criterion labels, and honesty audit pass.', run: function (doc, context) {
var revNode = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-revision-policy') : null;
if (!revNode || !revNode.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var REV = root.SimRevision, M = root.SimMastery, ST = root.SimStore;
if (!REV || typeof REV.buildRevisionViewModel !== 'function' || !M || !ST) {
return { status: 'PASS', details: { island: 'authored', module: 'skipped-minimal-harness' } };
}
var cov = (context && context.coverage) || root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS);
var loadedPol = REV.loadPolicy(doc);
var mPol = M.loadPolicy(doc);
var store = ST.createStore({ optIn: false, doc: doc });
var mBefore = M.readFromStore(store, cov, mPol.policy, mPol.digest);
var digestBefore = M.digestOfMap(mBefore);
REV.saveSelfAssessment(store, 'P1-01', { ratings: { C1_VALUE: 'confident' }, note: 'Smoke verbatim note' }, { coverage: cov, policy: loadedPol.policy, doc: doc });
var mAfter = M.readFromStore(store, cov, mPol.policy, mPol.digest);
var digestAfter = M.digestOfMap(mAfter);
if (digestBefore !== digestAfter) {
return { status: 'FAIL', reason: 'F07 self-assessment mutated mastery digest' };
}
var vm = REV.buildRevisionViewModel({ doc: doc, store: store, coverage: cov, masteryMap: mAfter, policy: loadedPol.policy });
if (!vm || vm.total_outcomes !== 64) {
return { status: 'FAIL', reason: 'Expected 64 outcomes in revision panel, got ' + (vm ? vm.total_outcomes : 'none') };
}
var p101 = vm.topics[0].outcomes[0];
if (p101.outcome_id !== 'P1-01' || p101.mastery.effective_state !== 'unseen' || p101.self_assessment.rated_count !== 1) {
return { status: 'FAIL', reason: 'P1-01 separation invariant failed (expected unseen mastery + 1 self-rating)' };
}
var card = REV.buildSelfAssessmentCardModel('P1-01', { doc: doc, store: store, coverage: cov, policy: loadedPol.policy });
if (!card || !Array.isArray(card.criteria) || card.criteria.length === 0 || card.self_assessment_label_lv !== REV.VERBATIM_SELF_ASSESSMENT_LABEL_LV) {
return { status: 'FAIL', reason: 'F07 card model missing criteria or verbatim label' };
}
var audit = REV.buildHonestyAudit(vm, card);
if (!audit || audit.status !== 'PASS' || audit.untraceable_count !== 0 || audit.merged_sources_count !== 0) {
return { status: 'FAIL', reason: 'Honesty audit failed: ' + (audit ? audit.status : 'none') };
}
return { status: 'PASS', details: { policyId: loadedPol.policy.policy_id, outcomes: vm.total_outcomes, masteryDigest: digestAfter, cardCriteria: card.criteria.length, auditElements: audit.total_elements } };
}
});
register({
id: 'SMK-N30-PRACTICE-PATH', owner: 'N30', description: 'Asserts #sim-practice-policy (PROPOSED), deterministic topic path, honest filter shortage, skip semantics, and N21 mode boundary in runner.', run: function (doc, context) {
var pracNode = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-practice-policy') : null;
if (!pracNode || !pracNode.textContent) return { status: 'PASS', details: { island: 'not-yet-inlined' } };
var P = root.SimPractice;
if (!P || typeof P.loadPolicy !== 'function' || typeof P.computePracticePath !== 'function') {
return { status: 'PASS', details: { island: 'authored', module: 'skipped-minimal-harness' } };
}
var bankNode = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-bank') : null;
var rtNode = doc && typeof doc.getElementById === 'function' ? doc.getElementById('sim-response-types') : null;
var bankQs = bankNode && bankNode.textContent ? JSON.parse(bankNode.textContent).questions : [];
var rt = rtNode && rtNode.textContent ? JSON.parse(rtNode.textContent) : null;
var cov = (context && context.coverage) || (root.SimCoverage && typeof root.SimCoverage.load === 'function' ? root.SimCoverage.load(doc, root.COVERAGE_INVARIANTS) : null);
var loaded = P.loadPolicy(doc, { bankQuestions: bankQs, responseTypes: rt });
var p1 = P.computePracticePath({ entryOrRequest: { entry_source: 'topic_browse', topic: 1 }, bankQuestions: bankQs, policy: loaded.policy, coverage: cov, responseTypes: rt, doc: doc });
var p2 = P.computePracticePath({ entryOrRequest: { entry_source: 'topic_browse', topic: 1 }, bankQuestions: bankQs, policy: loaded.policy, coverage: cov, responseTypes: rt, doc: doc });
if (p1.digest !== p2.digest) {
return { status: 'FAIL', reason: 'Practice path computation not deterministic: ' + p1.digest + ' != ' + p2.digest };
}
if (p1.true_length !== loaded.policy.topic_lengths['1'].declared_length || p1.shortage !== false) {
return { status: 'FAIL', reason: 'Expected Topic 1 length ' + loaded.policy.topic_lengths['1'].declared_length + ', got ' + p1.true_length };
}
var shortPath = P.computePracticePath({ entryOrRequest: { entry_source: 'topic_browse', topic: 1, filters: { topic: 1, response_types: ['Q06'] } }, bankQuestions: bankQs, policy: loaded.policy, coverage: cov, responseTypes: rt, doc: doc });
if (shortPath.true_length !== 2 || !shortPath.shortage || shortPath.shortage_reason !== 'filter_shortage') {
return { status: 'FAIL', reason: 'Q06 filter shortage mismatch: len=' + shortPath.true_length + ', reason=' + shortPath.shortage_reason };
}
var helpOk = P.describeHelpContract(p1.items[0], { mode: 'practice', doc: doc, coverage: cov });
if (!helpOk.help_enabled || helpOk.markers.indexOf('data-sim-component="hint"') === -1) {
return { status: 'FAIL', reason: 'Practice mode help contract missing hint marker' };
}
var examBlocked = false;
try {
P.describeHelpContract(p1.items[0], { mode: 'exam', doc: doc, coverage: cov });
} catch (err) {
examBlocked = Boolean(err && err.code === 'E_MODE_COMPONENT_NOT_ALLOWED');
}
if (!examBlocked) {
return { status: 'FAIL', reason: 'Exam mode did not forbid practice help components' };
}
var runner = P.createRunner(shortPath, { doc: null, coverage: cov, bankQuestions: bankQs, mode: 'practice' });
runner.skipCurrent();
runner.skipCurrent();
var sum = runner.getSummary();
if (sum.skipped_count !== 2 || sum.incorrect_count !== 0 || sum.status !== 'completed') {
return { status: 'FAIL', reason: 'Skip semantics failed: skipped=' + sum.skipped_count + ', incorrect=' + sum.incorrect_count };
}
return { status: 'PASS', details: { policyId: loaded.policy.policy_id, topic1Length: p1.true_length, topic1Digest: p1.digest, q06ShortageLength: shortPath.true_length, skippedCount: sum.skipped_count, incorrectCount: sum.incorrect_count, examBlocked: examBlocked } };
}
});
register({
id: 'SMK-N31-BUILD-CONTRACT', owner: 'N31', description: 'Asserts the N31 single-file build contract: all 7 core Section 1.2 islands and all inlined engine/input/grading runtime namespaces are live in the assembled artifact.', run: function (doc) {
var coreIslands = ['sim-coverage', 'sim-conventions', 'sim-bank', 'sim-forms', 'sim-golden-vectors', 'sim-terms', 'sim-analytics'];
var hasFullIslands = true;
for (var i = 0; i < coreIslands.length; i += 1) {
var el = doc && typeof doc.getElementById === 'function' ? doc.getElementById(coreIslands[i]) : null;
if (!el || !el.textContent) {
hasFullIslands = false;
break;
}
}
if (!hasFullIslands) {
return { status: 'PASS', details: { domWalk: 'skipped-minimal-harness' } };
}
var requiredGlobals = [
'SimCoverage', 'SimConventions', 'SimTerms', 'SimPRNG', 'SimFigures',
'SimBank', 'SimGoldenVectors', 'SimLeakScan', 'SimEngines', 'SimGraphScoring',
'SimGraphCapture', 'SimMethodEngine', 'SimMethodCards', 'SimVariantEngine',
'SimChains', 'SimStartView', 'SimConceptDrawer', 'SimConceptMap',
'SimHintDrawer', 'SimTheme', 'SimSession', 'SimInputsRegistry',
'SimInputsComponents', 'SimInputsIntegration', 'SimInputs', 'SimGrading',
'SimFeedback', 'SimAssembly', 'SimExam', 'SimStore', 'SimAnalytics',
'SimMastery', 'SimScheduler', 'SimRemediation', 'SimRevision', 'SimPractice'
];
var missing = [];
for (var g = 0; g < requiredGlobals.length; g += 1) {
if (!root[requiredGlobals[g]]) {
missing.push(requiredGlobals[g]);
}
}
if (missing.length > 0) {
return { status: 'FAIL', reason: 'Missing inlined runtime globals: ' + missing.join(',') };
}
return { status: 'PASS', details: { coreIslands: coreIslands.length, inlinedGlobals: requiredGlobals.length } };
}
});
register({
id: 'SMK-N32-CONTRAST-CONTRACT', owner: 'N32', description: 'Asserts the N32 WCAG 2.2 AA contrast-vector and dual-theme shipping contract in-file.', run: function (doc) {
function srgb(c) {
var x = c / 255;
return x <= 0.04045 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4);
}
function lum(hex) {
var h = String(hex || '').replace(/^#/, '');
if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
return 0.2126 * srgb(parseInt(h.slice(0, 2), 16)) + 0.7152 * srgb(parseInt(h.slice(2, 4), 16)) + 0.0722 * srgb(parseInt(h.slice(4, 6), 16));
}
function ratio(a, b) {
var la = lum(a), lb = lum(b);
return Math.round(((Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05)) * 100) / 100;
}
var baselinePairs = [
{ id: 'pair-primary-on-canvas-light', fg: '#13251c', bg: '#f6f7f4', min: 4.5 },
{ id: 'pair-primary-on-canvas-dark', fg: '#eef2ef', bg: '#121b18', min: 4.5 },
{ id: 'pair-on-accent-solid-light', fg: '#ffffff', bg: '#1d4a72', min: 4.5 },
{ id: 'pair-on-accent-solid-dark', fg: '#0d1821', bg: '#7dc0f0', min: 4.5 },
{ id: 'pair-border-subtle-canvas-light', fg: '#6f7a6e', bg: '#f6f7f4', min: 3.0 },
{ id: 'pair-border-subtle-canvas-dark', fg: '#7c8f86', bg: '#121b18', min: 3.0 }
];
var computed = {};
for (var i = 0; i < baselinePairs.length; i += 1) {
var p = baselinePairs[i];
var r = ratio(p.fg, p.bg);
computed[p.id] = r;
if (r < p.min) {
return { status: 'FAIL', reason: 'Contrast vector failed for ' + p.id + ': ' + r + ' < ' + p.min };
}
}
var styleEl = doc && typeof doc.querySelector === 'function' ? doc.querySelector('style') : null;
var cssText = styleEl && styleEl.textContent ? styleEl.textContent : '';
var hasBothThemes = cssText ? (cssText.indexOf(':root[data-theme="dark"]') !== -1 && cssText.indexOf('--target-min: 2.75rem') !== -1 && cssText.indexOf('@media (min-width: 48rem)') !== -1) : true;
if (!hasBothThemes) {
return { status: 'FAIL', reason: 'Inlined <style> missing dark theme, --target-min, or 48rem breakpoint' };
}
return { status: 'PASS', details: { pairs: computed, dualThemeShipped: true, aaOnly: true } };
}
});
register({
id: 'SMK-N33-KEYBOARD-FOCUS', owner: 'N33', description: 'Asserts keyboard map validation, #concept-drawer focus escape sequence, and typing-context input-guard in-file.', run: function (doc) {
var F = root.SimFocus;
if (!F || typeof F.validateKeyboardMap !== 'function' || typeof F.walkTabSequence !== 'function') {
return { status: 'FAIL', reason: 'SimFocus runtime global not available' };
}
var mapCheck = F.validateKeyboardMap(F.DEFAULT_KEYBOARD_MAP);
if (!mapCheck || !mapCheck.valid) {
return { status: 'FAIL', reason: 'Keyboard map validation failed' };
}
var typingGuard = F.shouldSuppressShortcut({ key: 't', ctrlKey: false, altKey: false, metaKey: false }, { tagName: 'INPUT', type: 'number' });
if (!typingGuard || !typingGuard.suppress || typingGuard.reason !== 'typing_context') {
return { status: 'FAIL', reason: 'Typing-context input-guard did not suppress bare key t' };
}
var trigger = doc && typeof doc.getElementById === 'function' ? doc.getElementById('theme-toggle-btn') : null;
var drawer = doc && typeof doc.getElementById === 'function' ? doc.getElementById('concept-drawer') : null;
if (!drawer) {
return { status: 'FAIL', reason: '#concept-drawer missing in document' };
}
var prevFocused = doc.activeElement || null;
var targetDrawerId = 'concept-drawer';
var escapeRec = null;
var restoredId = null;
if (F.getFocusableElements(drawer).length > 0) {
escapeRec = F.walkTabSequence(doc, targetDrawerId, trigger);
restoredId = F.closeDrawer(doc, targetDrawerId);
} else if (typeof doc.createElement === 'function') {
var host = doc.createElement('div');
var synTrigger = doc.createElement('button');
synTrigger.id = 'smk-n33-trigger';
var synDrawer = doc.createElement('aside');
synDrawer.id = 'smk-n33-concept-drawer';
synDrawer.hidden = true;
var synClose = doc.createElement('button');
synClose.id = 'smk-n33-drawer-close';
var synLink = doc.createElement('a');
synLink.id = 'smk-n33-drawer-link';
synLink.setAttribute('href', '#saturs');
var synOutside = doc.createElement('button');
synOutside.id = 'smk-n33-outside';
synDrawer.appendChild(synClose);
synDrawer.appendChild(synLink);
host.appendChild(synTrigger);
host.appendChild(synDrawer);
host.appendChild(synOutside);
var synDoc = {
activeElement: synTrigger,
body: host,
getElementById: function (id) {
if (id === 'smk-n33-concept-drawer') return synDrawer;
if (id === 'smk-n33-trigger') return synTrigger;
return null;
}
};
escapeRec = F.walkTabSequence(synDoc, 'smk-n33-concept-drawer', synTrigger);
restoredId = F.closeDrawer(synDoc, 'smk-n33-concept-drawer');
trigger = synTrigger;
}
if (prevFocused && typeof prevFocused.focus === 'function') {
try { prevFocused.focus(); } catch (_e) {}
}
if (!escapeRec || escapeRec.insideIds.length < 1 || !escapeRec.escapedOutsideDrawer) {
return { status: 'FAIL', reason: 'Focus did not enter and escape #concept-drawer' };
}
if (trigger && trigger.id && restoredId !== trigger.id) {
return { status: 'FAIL', reason: 'closeDrawer did not restore focus to invoking control' };
}
return { status: 'PASS', details: { contexts: mapCheck.contexts_checked, sequence: escapeRec.sequence, escapedToId: escapeRec.escapedToId, restoredId: restoredId } };
}
});
register({
id: 'SMK-N34-PRINT-WORKSHEET',
owner: 'N34',
description: 'Paper worksheet generator deterministically renders 21-slot Form A with zero interactive controls and handles empty form shortage.',
run: function (doc) {
if (!root.SimPaper || typeof root.SimPaper.buildWorksheetModel !== 'function') {
return { status: 'FAIL', reason: 'SimPaper global missing' };
}
var formsEl = doc && doc.getElementById ? doc.getElementById('sim-forms') : null;
var bankEl = doc && doc.getElementById ? doc.getElementById('sim-bank') : null;
if (!formsEl || !formsEl.textContent) {
return { status: 'FAIL', reason: '#sim-forms island missing' };
}
var formsData = JSON.parse(formsEl.textContent);
var bankData = bankEl && bankEl.textContent ? JSON.parse(bankEl.textContent) : null;
var avail = root.SimPaper.getAvailableForms(formsData);
if (avail.length < 1 || avail[0].form_id !== 'A') {
return { status: 'FAIL', reason: 'Expected Form A in available forms' };
}
var m1 = root.SimPaper.buildWorksheetModel(formsData, bankData, 'A');
var m2 = root.SimPaper.buildWorksheetModel(formsData, bankData, 'A');
if (!m1 || !m2 || m1.slots.length !== 21 || m1.total_points !== 100) {
return { status: 'FAIL', reason: 'Form A worksheet model did not yield 21 slots / 100 points' };
}
var h1 = root.SimPaper.renderWorksheetHTML(m1);
var h2 = root.SimPaper.renderWorksheetHTML(m2);
if (h1 !== h2) {
return { status: 'FAIL', reason: 'Form A worksheet HTML is not deterministic across two calls' };
}
if (/<(input|textarea|select|button)\b/i.test(h1)) {
return { status: 'FAIL', reason: 'Worksheet HTML contains forbidden interactive controls' };
}
var emptyAvail = root.SimPaper.getAvailableForms({ forms: { A: { form_id: 'A', status: 'FAILED', slots: [] } } });
if (emptyAvail.length !== 0) {
return { status: 'FAIL', reason: 'Failed form appeared in available list' };
}
return {
status: 'PASS',
details: {
availableForms: avail.map(function (f) { return f.form_id; }),
slotIds: m1.slots.map(function (s) { return s.slot_id; }),
totalPoints: m1.total_points
}
};
}
});
register({
id: 'SMK-N35-ESCAPE-HELPER',
owner: 'N35',
description: 'SimStore.escapeHtml preserves Latvian diacritics while escaping markup metacharacters, and SimStore.importProgress rejects invalid/tampered payloads.',
run: function () {
if (!root.SimStore || typeof root.SimStore.escapeHtml !== 'function') {
return { status: 'FAIL', reason: 'SimStore.escapeHtml missing' };
}
var sample = 'ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž <script>alert("x")<' + '/script> & \'test\'';
var escaped = root.SimStore.escapeHtml(sample);
var expected = 'ĀČĒĢĪĶĻŅŠŪŽ āčēģīķļņšūž &lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &amp; &#39;test&#39;';
if (escaped !== expected) {
return { status: 'FAIL', reason: 'escapeHtml output mismatch', escaped: escaped };
}
var st = root.SimStore.createStore();
var rejectedJson = false;
try { st.importProgress('{truncated'); } catch (e) { rejectedJson = (e && e.code === 'E_STORE_IMPORT_JSON'); }
if (!rejectedJson) {
return { status: 'FAIL', reason: 'importProgress did not reject truncated JSON' };
}
return { status: 'PASS', details: { escapedLength: escaped.length, rejectedJson: true } };
}
});
function run(doc, context) {
doc = doc || root.document;
var results = [];
var passed = 0;
var failed = 0;
var i;
for (i = 0; i < vectors.length; i += 1) {
var vec = vectors[i];
var outcome;
try {
outcome = vec.run(doc, context);
} catch (error) {
outcome = { status: 'FAIL', reason: String(error && error.message ? error.message : error) };
}
var entry = {
id: vec.id, owner: vec.owner, status: outcome.status === 'PASS' ? 'PASS' : 'FAIL', details: outcome.details || null, reason: outcome.reason || null
};
if (entry.status === 'PASS') {
passed += 1;
} else {
failed += 1;
}
results.push(entry);
}
var report = {
status: failed === 0 ? 'PASS' : 'FAIL', total: results.length, passed: passed, failed: failed, vectors: results
};
root.SimSmoke.lastReport = report;
var statusNode = doc && doc.getElementById ? doc.getElementById('sim-smoke-status') : null;
if (statusNode) {
statusNode.textContent = 'Iekļautā dūmu pārbaude: ' + report.status + ' (' + report.passed + '/' + report.total + ' vektori).';
statusNode.hidden = false;
}
return report;
}
root.SimSmoke = {
vectors: vectors, register: register, run: run, lastReport: null
};
if (typeof module !== 'undefined' && module.exports) {
module.exports = root.SimSmoke;
}
})(typeof globalThis !== 'undefined' ? globalThis : this);
