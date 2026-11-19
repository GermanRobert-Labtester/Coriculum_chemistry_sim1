(function (root) {
'use strict';
var ID = 'sim-figures';
var SVG_NS = ['http', '//www.w3.org/2000/svg'].join(':');
var TYPE_REGISTRY = {
bar: { kind: 'cartesian', requiresAxes: ['x', 'y'] }, chain: { kind: 'flow', requiresAxes: [] }, curve: { kind: 'cartesian', requiresAxes: ['x', 'y'] }, scatter: { kind: 'cartesian', requiresAxes: ['x', 'y'] }, band: { kind: 'scale', requiresAxes: ['x'] }, schema_plot: { kind: 'cartesian', requiresAxes: ['x', 'y'], requiresTolerance: true }, burette: { kind: 'laboratory', requiresAxes: ['y'], requiresTolerance: true }, dilution: { kind: 'laboratory', requiresAxes: [] }, hess_cycle: { kind: 'flow', requiresAxes: [] }
};
var state = {
island: null, loadError: null, renderEvents: []
};
function has(o, k) { return Object.prototype.hasOwnProperty.call(o, k); }
function FiguresError(code, message, details) {
this.name = 'FiguresError';
this.code = code;
this.message = '[' + code + '] ' + message;
this.details = details || {};
if (Error.captureStackTrace) Error.captureStackTrace(this, FiguresError);
else this.stack = (new Error(this.message)).stack;
}
FiguresError.prototype = Object.create(Error.prototype);
FiguresError.prototype.constructor = FiguresError;
function fail(c, m, d) { throw new FiguresError(c, m, d); }
function req(ok, c, m, d) { if (!ok) fail(c, m, d); }
function escXml(s) {
return String(s === undefined || s === null ? '' : s)
.replace(/&/g, '&amp;')
.replace(/</g, '&lt;')
.replace(/>/g, '&gt;')
.replace(/"/g, '&quot;');
}
function fmt(n) {
return Number(n).toFixed(2).replace(/\.00$/, '');
}
function fmtLv(n, decimals) {
var d = decimals !== undefined ? decimals : 2;
return Number(n).toFixed(d).replace('.', ',');
}
function el(tag, attrs, children, text) {
return { tag: tag, attrs: attrs || {}, children: children || [], text: text };
}
function resolveTerm(key, kind, unitOverride, terms) {
if (!key) return '';
var T = root.SimTerms;
if (T && typeof T.resolveFigureLabel === 'function' && (terms || (T.getDefault && T.getDefault()))) {
var ti = terms || T.getDefault();
if (kind === 'title') return T.lookup(key, null, ti);
var spec = { kind: kind, key: key };
if (unitOverride !== undefined) spec.unit = unitOverride;
return T.resolveFigureLabel(spec, ti).text;
}
return key;
}
function resolveTolerance(rec, conventions) {
if (!rec.tolerance_coupling) return null;
var tc = rec.tolerance_coupling;
var absVal = null;
var unit = tc.expected_unit || null;
if (conventions && conventions.tolerances && Array.isArray(conventions.tolerances.quantity_classes)) {
var list = conventions.tolerances.quantity_classes;
for (var i = 0; i < list.length; i += 1) {
if (list[i].id === tc.tolerance_class) {
if (list[i].absolute && list[i].absolute.value !== undefined) absVal = Number(list[i].absolute.value);
if (!unit && list[i].unit) unit = list[i].unit;
break;
}
}
}
if (absVal === null && tc.band_half_width !== undefined) absVal = Number(tc.band_half_width);
return {
toleranceClass: tc.tolerance_class, abs: absVal, unit: unit, sigFigsRule: tc.sig_figs_rule || 'least_of_givens'
};
}
function validateRecordForRender(rec) {
req(rec && typeof rec === 'object', 'E_FIG_RECORD_SHAPE', 'Attēla ieraksts nav objekts.', {});
req(typeof rec.id === 'string' && rec.id.trim(), 'E_FIG_MISSING_ID', 'Attēlam trūkst id.', {});
req(typeof rec.type === 'string' && has(TYPE_REGISTRY, rec.type), 'E_FIG_UNKNOWN_TYPE', 'Nezināms attēla tips: ' + String(rec.type), { id: rec.id, type: rec.type });
req(typeof rec.description_lv === 'string' && rec.description_lv.trim().length >= 20, 'E_FIG_MISSING_DESCRIPTION', 'Attēlam ' + rec.id + ' trūkst apraksta description_lv.', { id: rec.id });
if (rec.has_measured_quantity || rec.type === 'schema_plot') {
req(rec.tolerance_coupling && typeof rec.tolerance_coupling === 'object' && rec.tolerance_coupling.tolerance_class, 'E_FIG_MISSING_TOLERANCE', 'Attēlam ' + rec.id + ' nepieciešama tolerance_coupling.', { id: rec.id });
}
}
function activeTheme(doc, optTheme) {
if (optTheme === 'light' || optTheme === 'dark' || optTheme === 'print') return optTheme;
var rootEl = doc && doc.documentElement;
var attr = rootEl && typeof rootEl.getAttribute === 'function' ? rootEl.getAttribute('data-theme') : null;
return attr === 'dark' ? 'dark' : 'light';
}
function buildAnnotations(rec, W, yStart, terms, children) {
var anns = rec.annotations || [];
var y = yStart;
for (var i = 0; i < anns.length; i += 1) {
var a = anns[i];
var txt = a.text_override_lv || resolveTerm(a.annotation_key, 'annotation', null, terms);
children.push(el('rect', { x: 24, y: fmt(y), width: fmt(W - 48), height: 24, rx: 4, class: 'fig-annot-box' }));
children.push(el('text', { x: 34, y: fmt(y + 16), class: 'fig-annot-text' }, null, txt));
y += 28;
}
}
function renderBar(rec, W, H, terms, children) {
var x0 = 78, x1 = W - 28, y0 = 62, y1 = H - 96;
var pw = x1 - x0, ph = y1 - y0;
var ax = rec.axes || {};
var yMax = Number((ax.y && ax.y.max) || 100);
var yMin = Number((ax.y && ax.y.min) || 0);
var yStep = Number((ax.y && ax.y.step) || (yMax - yMin) / 5);
var span = yMax - yMin || 1;
for (var v = yMin; v <= yMax + 1e-9; v += yStep) {
var py = y1 - ((v - yMin) / span) * ph;
children.push(el('line', { x1: fmt(x0), y1: fmt(py), x2: fmt(x1), y2: fmt(py), class: 'fig-grid' }));
children.push(el('line', { x1: fmt(x0 - 5), y1: fmt(py), x2: fmt(x0), y2: fmt(py), class: 'fig-axis-line' }));
children.push(el('text', { x: fmt(x0 - 8), y: fmt(py + 4), 'text-anchor': 'end', class: 'fig-tick-text' }, null, fmtLv(v, yStep < 1 ? 1 : 0)));
}
children.push(el('line', { x1: fmt(x0), y1: fmt(y0), x2: fmt(x0), y2: fmt(y1), class: 'fig-axis-line' }));
children.push(el('line', { x1: fmt(x0), y1: fmt(y1), x2: fmt(x1), y2: fmt(y1), class: 'fig-axis-line' }));
var series = rec.series || [];
var cats = (series[0] && series[0].data) ? series[0].data.length : 1;
var grpW = pw / Math.max(1, cats);
var barGap = series.length > 1 ? 26 : 8;
var barW = Math.min(72, Math.max(24, (grpW * 0.62 - barGap * Math.max(0, series.length - 1)) / Math.max(1, series.length)));
for (var c = 0; c < cats; c += 1) {
var cxCenter = x0 + (c + 0.5) * grpW;
var totalW = series.length * barW + (series.length - 1) * barGap;
var startX = cxCenter - totalW / 2;
var catLbl = series[0].data[c].label_lv || '';
children.push(el('text', { x: fmt(cxCenter), y: fmt(y1 + 18), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, catLbl));
for (var s = 0; s < series.length; s += 1) {
var pt = series[s].data && series[s].data[c];
if (!pt || pt.value === null || pt.value === undefined) continue;
var val = Number(pt.exact_value !== undefined && pt.exact_value !== null ? pt.exact_value : pt.value);
var bh = Math.max(2, ((val - yMin) / span) * ph);
var bx = startX + s * (barW + barGap);
var by = y1 - bh;
var role = series[s].style_role || (s === 0 ? 'primary' : 'secondary');
children.push(el('rect', {
x: fmt(bx), y: fmt(by), width: fmt(barW), height: fmt(bh), rx: 2, class: 'fig-bar-' + role, 'data-value': String(val), 'data-basis': pt.basis || series[s].basis || ''
}));
var dTxt = pt.display_lv || String(pt.value);
var lblOffset = (series.length > 1 && s % 2 === 1 && bh < 90) ? -22 : -6;
children.push(el('text', { x: fmt(bx + barW / 2), y: fmt(by + lblOffset), 'text-anchor': 'middle', class: 'fig-value-label' }, null, dTxt));
}
}
if (ax.y && ax.y.term_key) {
var yLbl = resolveTerm(ax.y.term_key, 'axis', ax.y.unit, terms);
children.push(el('text', {
x: 18, y: fmt((y0 + y1) / 2), 'text-anchor': 'middle', transform: 'rotate(-90 18 ' + fmt((y0 + y1) / 2) + ')', class: 'fig-axis-label'
}, null, yLbl));
}
var lx = x0;
for (var ls = 0; ls < series.length; ls += 1) {
var sr = series[ls];
var sRole = sr.style_role || (ls === 0 ? 'primary' : 'secondary');
var lTxt = resolveTerm(sr.legend_key, 'legend', null, terms);
children.push(el('rect', { x: fmt(lx), y: fmt(y1 + 30), width: 14, height: 10, rx: 2, class: 'fig-bar-' + sRole }));
children.push(el('text', { x: fmt(lx + 20), y: fmt(y1 + 39), class: 'fig-legend-text' }, null, lTxt));
lx += Math.max(170, lTxt.length * 7 + 44);
}
buildAnnotations(rec, W, H - 36, terms, children);
}
function renderChain(rec, W, H, terms, children) {
var sr = (rec.series && rec.series[0]) || {};
var nodes = sr.nodes || [];
var edges = sr.edges || [];
var nCount = Math.max(1, nodes.length);
var marginX = 24, gap = 26;
var boxW = (W - marginX * 2 - gap * (nCount - 1)) / nCount;
var boxY = 76, boxH = Math.min(116, H - 154);
var pos = Object.create(null);
for (var i = 0; i < nodes.length; i += 1) {
var nd = nodes[i];
var bx = marginX + i * (boxW + gap);
pos[nd.id] = { x: bx, y: boxY, w: boxW, h: boxH };
children.push(el('rect', { x: fmt(bx), y: fmt(boxY), width: fmt(boxW), height: fmt(boxH), rx: 6, class: i === 1 ? 'fig-node-highlight' : 'fig-node-box' }));
children.push(el('text', { x: fmt(bx + 10), y: fmt(boxY + 22), class: 'fig-tick-text' }, null, nd.step || ''));
children.push(el('text', { x: fmt(bx + 10), y: fmt(boxY + 46), class: 'fig-value-label' }, null, nd.title_lv || ''));
children.push(el('text', { x: fmt(bx + 10), y: fmt(boxY + 70), class: 'fig-legend-text' }, null, nd.detail_lv || ''));
}
for (var e = 0; e < edges.length; e += 1) {
var ed = edges[e];
var a = pos[ed.from], b = pos[ed.to];
if (!a || !b) continue;
var x1 = a.x + a.w, y1 = a.y + a.h / 2;
var x2 = b.x, y2 = b.y + b.h / 2;
if (Math.abs(a.x - b.x) > boxW + gap + 5) {
var arcY = boxY - 14;
children.push(el('path', {
d: 'M ' + fmt(a.x + a.w * 0.5) + ' ' + fmt(a.y) + ' L ' + fmt(a.x + a.w * 0.5) + ' ' + fmt(arcY) + ' L ' + fmt(b.x + b.w * 0.5) + ' ' + fmt(arcY) + ' L ' + fmt(b.x + b.w * 0.5) + ' ' + fmt(b.y), class: 'fig-arrow-line'
}));
children.push(el('text', { x: fmt((a.x + b.x + b.w) / 2), y: fmt(arcY - 4), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, ed.label_lv || ''));
} else {
children.push(el('line', { x1: fmt(x1), y1: fmt(y1), x2: fmt(x2 - 5), y2: fmt(y2), class: 'fig-arrow-line' }));
children.push(el('polygon', { points: fmt(x2) + ',' + fmt(y2) + ' ' + fmt(x2 - 8) + ',' + fmt(y2 - 4) + ' ' + fmt(x2 - 8) + ',' + fmt(y2 + 4), class: 'fig-arrow-head' }));
if (ed.label_lv) {
children.push(el('text', { x: fmt((x1 + x2) / 2), y: fmt(y1 - 8), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, ed.label_lv));
}
}
}
buildAnnotations(rec, W, H - 38, terms, children);
}
function renderBand(rec, W, H, terms, children) {
var x0 = 44, x1 = W - 44, yBand = 86, bandH = 44, yAxis = 152;
var ax = (rec.axes && rec.axes.x) || {};
var xMin = Number(ax.min !== undefined ? ax.min : -1);
var xMax = Number(ax.max !== undefined ? ax.max : 4);
var span = xMax - xMin || 1;
var pw = x1 - x0;
var bands = (rec.series && rec.series[0] && rec.series[0].bands) || [];
for (var i = 0; i < bands.length; i += 1) {
var b = bands[i];
var bx1 = x0 + ((Number(b.min_exp) - xMin) / span) * pw;
var bx2 = x0 + ((Number(b.max_exp) - xMin) / span) * pw;
var role = b.style_role || 'primary';
children.push(el('rect', { x: fmt(bx1), y: fmt(yBand), width: fmt(bx2 - bx1), height: fmt(bandH), class: 'fig-band-' + role }));
children.push(el('text', { x: fmt((bx1 + bx2) / 2), y: fmt(yBand + 26), 'text-anchor': 'middle', class: 'fig-value-label' }, null, b.label_lv || ''));
}
children.push(el('line', { x1: fmt(x0), y1: fmt(yAxis), x2: fmt(x1), y2: fmt(yAxis), class: 'fig-axis-line' }));
var tLabels = ax.tick_labels || [];
var step = Number(ax.step || 1);
var idx = 0;
for (var e = xMin; e <= xMax + 1e-9; e += step) {
var tx = x0 + ((e - xMin) / span) * pw;
children.push(el('line', { x1: fmt(tx), y1: fmt(yAxis - 5), x2: fmt(tx), y2: fmt(yAxis + 6), class: 'fig-axis-line' }));
children.push(el('text', { x: fmt(tx), y: fmt(yAxis + 22), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, tLabels[idx] || String(e)));
idx += 1;
}
if (ax.term_key) {
children.push(el('text', { x: fmt((x0 + x1) / 2), y: fmt(yAxis + 42), 'text-anchor': 'middle', class: 'fig-axis-label' }, null, resolveTerm(ax.term_key, 'axis', ax.unit, terms)));
}
buildAnnotations(rec, W, H - 36, terms, children);
}
function renderCartesianPlot(rec, W, H, terms, conventions, children) {
var x0 = 84, x1 = W - (rec.reading_strip ? 132 : 36), y0 = 64, y1 = H - 98 - Math.max(0, (rec.annotations || []).length - 1) * 28;
var pw = x1 - x0, ph = y1 - y0;
var ax = rec.axes || {};
var xMin = Number(ax.x && ax.x.min !== undefined ? ax.x.min : 0);
var xMax = Number(ax.x && ax.x.max !== undefined ? ax.x.max : 10);
var xStep = Number(ax.x && ax.x.step ? ax.x.step : (xMax - xMin) / 5);
var yMin = Number(ax.y && ax.y.min !== undefined ? ax.y.min : 0);
var yMax = Number(ax.y && ax.y.max !== undefined ? ax.y.max : 1);
var yStep = Number(ax.y && ax.y.step ? ax.y.step : (yMax - yMin) / 5);
var xSpan = xMax - xMin || 1, ySpan = yMax - yMin || 1;
function px(x) { return x0 + ((x - xMin) / xSpan) * pw; }
function py(y) { return y1 - ((y - yMin) / ySpan) * ph; }
var xDec = xStep >= 1 ? 0 : Math.max(1, Math.ceil(-Math.log10(xStep)));
for (var xv = xMin; xv <= xMax + 1e-9; xv += xStep) {
var sx = px(xv);
children.push(el('line', { x1: fmt(sx), y1: fmt(y0), x2: fmt(sx), y2: fmt(y1), class: 'fig-grid' }));
children.push(el('line', { x1: fmt(sx), y1: fmt(y1), x2: fmt(sx), y2: fmt(y1 + 5), class: 'fig-axis-line' }));
children.push(el('text', { x: fmt(sx), y: fmt(y1 + 19), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, fmtLv(xv, xDec)));
}

var yDec = yStep >= 1 ? 0 : Math.max(1, Math.ceil(-Math.log10(yStep)));
for (var yv = yMin; yv <= yMax + 1e-9; yv += yStep) {
var sy = py(yv);
children.push(el('line', { x1: fmt(x0), y1: fmt(sy), x2: fmt(x1), y2: fmt(sy), class: 'fig-grid' }));
children.push(el('line', { x1: fmt(x0 - 5), y1: fmt(sy), x2: fmt(x0), y2: fmt(sy), class: 'fig-axis-line' }));
children.push(el('text', { x: fmt(x0 - 8), y: fmt(sy + 4), 'text-anchor': 'end', class: 'fig-tick-text' }, null, fmtLv(yv, yDec)));
}
children.push(el('line', { x1: fmt(x0), y1: fmt(y0), x2: fmt(x0), y2: fmt(y1), class: 'fig-axis-line' }));
children.push(el('line', { x1: fmt(x0), y1: fmt(y1), x2: fmt(x1), y2: fmt(y1), class: 'fig-axis-line' }));
if (rec.buffer_region) {
var br = rec.buffer_region;
children.push(el('rect', {
x: fmt(px(+br.x_min)), y: fmt(y0), width: fmt(px(+br.x_max) - px(+br.x_min)), height: fmt(ph),
class: 'fig-buffer-region', 'data-buffer-region': 'true', 'data-buffer-x-min': '' + br.x_min, 'data-buffer-x-max': '' + br.x_max
}));
if (br.label_lv) children.push(el('text', { x: fmt(px(+br.x_min) + 4), y: fmt(y0 + 13), class: 'fig-tick-text' }, null, br.label_lv));
}
if (rec.indicator_band) {
var ib = rec.indicator_band;
var ibTop = py(+ib.y_max), ibBot = py(+ib.y_min);
children.push(el('rect', {
x: fmt(x0), y: fmt(ibTop), width: fmt(pw), height: fmt(Math.max(2, ibBot - ibTop)),
class: 'fig-indicator-band', 'data-indicator-band': 'true', 'data-indicator-y-min': '' + ib.y_min, 'data-indicator-y-max': '' + ib.y_max
}));
if (ib.label_lv) children.push(el('text', { x: fmt(x1 - 6), y: fmt(ibTop + 13), 'text-anchor': 'end', class: 'fig-tick-text' }, null, ib.label_lv));
}
var tol = resolveTolerance(rec, conventions);
var tr = rec.target_readout;
if (tol && tol.abs && tr && tr.expected_value !== undefined) {
var tx1 = px(Math.max(xMin, Number(tr.expected_value) - tol.abs));
var tx2 = px(Math.min(xMax, Number(tr.expected_value) + tol.abs));
children.push(el('rect', {
x: fmt(tx1), y: fmt(y0), width: fmt(Math.max(2, tx2 - tx1)), height: fmt(ph), class: 'fig-band-tol', 'data-tolerance-class': tol.toleranceClass, 'data-tolerance-abs': String(tol.abs)
}));
}
var srList=rec.series||[],hasCm=false;
function ac(t,a,k,s){children.push(el(t,a,k,s));}
for(var s=0;s<srList.length;s+=1){
var sr=srList[s];
if(sr.line)ac('line',{x1:fmt(px(sr.line.x1)),y1:fmt(py(sr.line.y1)),x2:fmt(px(sr.line.x2)),y2:fmt(py(sr.line.y2)),class:'fig-data-line'});
var cm=sr.curve_model||null,gen=cm?generateCurvePoints(cm):null,pts=gen?gen.points:(sr.points||[]);
if(gen)hasCm=true;
if(sr.shade_tail_from!==undefined&&pts.length>=2){
var sf=+sr.shade_tail_from,tp=[],k,t0,sx0,sy0,sd,j;
for(k=0;k<pts.length;k+=1)if(pts[k].x>=sf-1e-9){if(!tp.length&&k>0&&pts[k].x>sf+1e-9){t0=(sf-pts[k-1].x)/(pts[k].x-pts[k-1].x);tp.push({x:sf,y:pts[k-1].y+t0*(pts[k].y-pts[k-1].y)});}tp.push(pts[k]);}
if(tp.length>=2){
sx0=px(sf);sy0=py(0);sd='M '+fmt(sx0)+' '+fmt(sy0);
for(j=0;j<tp.length;j+=1)sd+=' L '+fmt(px(tp[j].x))+' '+fmt(py(tp[j].y));
ac('path',{d:sd+' L '+fmt(px(tp[tp.length-1].x))+' '+fmt(sy0)+' Z',class:sr.style_role==='secondary'?'fig-tail-shade-secondary':'fig-tail-shade-primary','data-tail-series':sr.id||''+s,'data-tail-start-x':fmt(sx0),'data-tail-threshold':''+sf});
}
}
if(rec.type==='curve'&&pts.length>=2){
var d='M '+fmt(px(pts[0].x))+' '+fmt(py(pts[0].y));
for(var q=1;q<pts.length;q+=1)d+=' L '+fmt(px(pts[q].x))+' '+fmt(py(pts[q].y));
var pa={d:d,class:sr.style_role==='secondary'?'fig-data-line fig-data-line-alt':'fig-data-line'};
if(gen){pa['data-curve-class']=cm.function_class;pa['data-point-count']=''+pts.length;pa['data-peak-x']=fmt(px(gen.peak.x));pa['data-peak-y']=fmt(py(gen.peak.y));}
ac('path',pa);
}
if(!gen)for(var p=0;p<pts.length;p+=1){
var pt=pts[p],cx=px(pt.x),cy=py(pt.y);
ac('circle',{cx:fmt(cx),cy:fmt(cy),r:4.5,class:'fig-point-dot','data-point-id':pt.id||''});
if(pt.label_lv){
var txO=pt.x>=(xMax*0.75)?-8:8,anc=pt.x>=(xMax*0.75)?'end':'start',dyO=(pt.label_pos==='below'||(p>0&&p%2===1&&pt.x<xMax*0.75))?16:-8;
ac('text',{x:fmt(cx+txO),y:fmt(cy+dyO),'text-anchor':anc,class:'fig-tick-text'},null,pt.label_lv);
}
}
}
if(rec.fit_line){
var fl=rec.fit_line,sp=rec.span||(rec.kinetics_spec&&rec.kinetics_spec.span_s)||{},sx=Math.max(+fl.x_min,+sp.x_min),ex=Math.min(+fl.x_max,+sp.x_max);
if(ex>=sx){
var slv=+fl.slope,itv=+fl.intercept,ya=slv*sx+itv,yb=slv*ex+itv,tf=rec.tolerance_fields||{},pa=(tf.point_acceptance||{}),pv=Math.abs(+pa.abs_value||0);
if(pv>0)ac('polygon',{points:fmt(px(sx))+','+fmt(py(ya-pv))+' '+fmt(px(ex))+','+fmt(py(yb-pv))+' '+fmt(px(ex))+','+fmt(py(yb+pv))+' '+fmt(px(sx))+','+fmt(py(ya+pv)),class:'fig-band-tol fig-tol-band','data-tol-band':'true','data-tol-value':''+pv});
ac('line',{x1:fmt(px(sx)),y1:fmt(py(ya)),x2:fmt(px(ex)),y2:fmt(py(yb)),class:'fig-data-line fig-fit-line','data-fit-line':'true','data-fit-x-min':''+sx,'data-fit-x-max':''+ex,'data-fit-slope':''+slv,'data-fit-intercept':''+itv,'data-fit-clipped':'true'});
}
}
if(rec.reading_spec){
var rd=rec.reading_spec,rx=px(+rd.concentration_x),ry=py(+rd.signal);
if(rx>=px(xMin)-.01&&rx<=px(xMax)+.01&&ry>=py(yMax)-.01&&ry<=py(yMin)+.01){
ac('line',{x1:fmt(x0),y1:fmt(ry),x2:fmt(rx),y2:fmt(ry),class:'fig-reading-line','data-reading-signal':''+rd.signal,'data-reading-clipped':'true'});
ac('line',{x1:fmt(rx),y1:fmt(ry),x2:fmt(rx),y2:fmt(y1),class:'fig-reading-line','data-reading-x':''+rd.concentration_x,'data-reading-clipped':'true'});
ac('circle',{cx:fmt(rx),cy:fmt(ry),r:5,class:'fig-reading-dot','data-reading-dot':'true'});
}
}
if(rec.signal_marker){
var sm=rec.signal_marker,smy=py(+sm.signal);
ac('line',{x1:fmt(x0),y1:fmt(smy),x2:fmt(x0+12),y2:fmt(smy),class:'fig-reading-line','data-signal-marker':'true','data-signal-value':''+sm.signal});
}
if(rec.equivalence_marker){
var eq=rec.equivalence_marker,eqx=px(+eq.x);
ac('line',{x1:fmt(eqx),y1:fmt(y0),x2:fmt(eqx),y2:fmt(y1),class:'fig-equivalence-line','data-equivalence-x':''+eq.x});
if(eq.label_lv)ac('text',{x:fmt(eqx+5),y:fmt(y0+13),class:'fig-tick-text'},null,eq.label_lv);
}
if(rec.half_equivalence_marker){
var hq=rec.half_equivalence_marker,hx=px(+hq.x),hy=py(+hq.y);
ac('line',{x1:fmt(hx),y1:fmt(y0),x2:fmt(hx),y2:fmt(y1),class:'fig-half-line','data-half-equivalence-x':''+hq.x});
ac('circle',{cx:fmt(hx),cy:fmt(hy),r:4,class:'fig-reading-dot','data-half-equivalence-y':''+hq.y});
if(hq.label_lv)ac('text',{x:fmt(hx+5),y:fmt(hy-6),class:'fig-tick-text'},null,hq.label_lv);
}
if(rec.endpoint_marker){
var em=rec.endpoint_marker,emx=px(+em.x);
ac('line',{x1:fmt(emx),y1:fmt(y0),x2:fmt(emx),y2:fmt(y1),class:'fig-endpoint-line','data-endpoint-x':''+em.x});
if(em.label_lv)ac('text',{x:fmt(emx+5),y:fmt(y0+27),class:'fig-tick-text'},null,em.label_lv);
}
if(rec.reading_strip){
var rs=rec.reading_strip,stTop=y0+10,stBot=y1-10,stX=W-98,stW=26;
var stPx=(stBot-stTop)/(+rs.view_max_ml-+rs.view_min_ml),stY=stTop+(+rs.declared_reading_ml-+rs.view_min_ml)*stPx;
ac('rect',{x:fmt(stX),y:fmt(stTop),width:stW,height:fmt(stBot-stTop),class:'fig-strip-box','data-reading-strip':'true'});
var stDiv=Math.round((+rs.view_max_ml-+rs.view_min_ml)/(+rs.minor_division_ml));
for(var sd=0;sd<=stDiv;sd+=1){
var sv=+rs.view_min_ml+sd*(+rs.minor_division_ml),sy=stTop+(sv-+rs.view_min_ml)*stPx;
var sMaj=(Math.round(sv*10)%5===0);
ac('line',{x1:fmt(stX),y1:fmt(sy),x2:fmt(stX+(sMaj?stW:stW/2)),y2:fmt(sy),class:sMaj?'fig-tick-major':'fig-tick-minor'});
if(sMaj)ac('text',{x:fmt(stX+stW+4),y:fmt(sy+4),class:'fig-tick-text'},null,fmtLv(sv,rs.reported_decimals||2)+' mL');
}
ac('line',{x1:fmt(stX),y1:fmt(stY),x2:fmt(stX+stW),y2:fmt(stY),class:'fig-strip-meniscus','data-strip-meniscus-y':fmt(stY),'data-strip-reading-ml':''+rs.declared_reading_ml});
}
if(rec.preview_line){
var pl=rec.preview_line,psp=rec.span||{},px1=Math.max(+pl.x_min,+psp.x_min),px2=Math.min(+pl.x_max,+psp.x_max);
if(px2>=px1)ac('line',{x1:fmt(px(px1)),y1:fmt(py(+pl.slope*px1+ +pl.intercept)),x2:fmt(px(px2)),y2:fmt(py(+pl.slope*px2+ +pl.intercept)),class:'fig-draw-line','data-drawn-line':'true','data-drawn-x-min':''+px1,'data-drawn-x-max':''+px2,'data-drawn-beyond':(+pl.x_max>+psp.x_max||+pl.x_min<+psp.x_min)?'not_assessed':'none'});
}
if(rec.half_life_marker){
var hm=rec.half_life_marker,hx=px(+hm.t_s),hy=py(+hm.C_mol_l);
ac('line',{x1:fmt(hx),y1:fmt(y0),x2:fmt(hx),y2:fmt(y1),class:'fig-threshold-line fig-hl-line','data-half-life-x':''+hm.t_s});
ac('line',{x1:fmt(x0),y1:fmt(hy),x2:fmt(hx),y2:fmt(hy),class:'fig-threshold-line','data-half-life-y':''+hm.C_mol_l});
ac('text',{x:fmt(hx+5),y:fmt(hy-5),class:'fig-tick-text'},null,'t½');
}
if(rec.threshold_line){
var tx=+rec.threshold_line.x,tpx=px(tx);
ac('line',{x1:fmt(tpx),y1:fmt(y0),x2:fmt(tpx),y2:fmt(y1),class:'fig-threshold-line','data-threshold-x':fmt(tpx),'data-threshold-val':''+tx});
if(rec.threshold_line.label_lv)ac('text',{x:fmt(tpx+6),y:fmt(y0+52),'text-anchor':'start',class:'fig-tick-text'},null,rec.threshold_line.label_lv);
}
if(rec.energy_markers){
var lvs=rec.energy_markers.levels||[],ars=rec.energy_markers.arrows||[],i,lv,ar,ly,lx1,lx2,lb,isS,isP,axp,ay1,ay2;
for(i=0;i<lvs.length;i+=1){
lv=lvs[i];ly=py(lv.y);lx1=px(lv.x1);lx2=px(lv.x2);ac('line',{x1:fmt(lx1),y1:fmt(ly),x2:fmt(lx2),y2:fmt(ly),class:'fig-level-line'});
if(lv.label_lv){lb=lv.label_lv;isS=!lb.indexOf('S:');isP=!lb.indexOf('P:');ac('text',{x:fmt(isS?lx1+4:isP?lx2-4:(lx1+lx2)/2),y:fmt(ly-6),'text-anchor':isS?'start':isP?'end':'middle',class:'fig-tick-text'},null,lb);}
}
for(i=0;i<ars.length;i+=1){
ar=ars[i];axp=px(ar.x);ay1=py(ar.y_from);ay2=py(ar.y_to);
ac('line',{x1:fmt(axp),y1:fmt(ay1),x2:fmt(axp),y2:fmt(ay2),class:ar.role==='dh'?'fig-hess-direct':'fig-data-line'});
children.push(arrowHead(axp,ay1,axp,ay2));
if(ar.label_lv)ac('text',{x:fmt(axp-6),y:fmt((ay1+ay2)/2+4),'text-anchor':'end',class:'fig-tick-text'},null,ar.label_lv);
}
}
if(hasCm&&srList.length>1)for(var lg=0;lg<srList.length;lg+=1){
var ls=srList[lg],lpy=y0+14+lg*17;
ac('line',{x1:fmt(x1-26),y1:fmt(lpy),x2:fmt(x1-4),y2:fmt(lpy),class:ls.style_role==='secondary'?'fig-data-line fig-data-line-alt':'fig-data-line'});
if(ls.legend_key)ac('text',{x:fmt(x1-32),y:fmt(lpy+4),'text-anchor':'end',class:'fig-tick-text'},null,resolveTerm(ls.legend_key,'legend',null,terms));
}
if (ax.x && ax.x.term_key) {
children.push(el('text', { x: fmt((x0 + x1) / 2), y: fmt(y1 + 38), 'text-anchor': 'middle', class: 'fig-axis-label' }, null, resolveTerm(ax.x.term_key, 'axis', ax.x.unit, terms)));
}
if (ax.y && ax.y.term_key) {
children.push(el('text', {
x: 18, y: fmt((y0 + y1) / 2), 'text-anchor': 'middle', transform: 'rotate(-90 18 ' + fmt((y0 + y1) / 2) + ')', class: 'fig-axis-label'
}, null, resolveTerm(ax.y.term_key, 'axis', ax.y.unit, terms)));
}
buildAnnotations(rec, W, H - 36 - Math.max(0, (rec.annotations || []).length - 1) * 28, terms, children);
}
function badC(c){throw new FiguresError(c||'E_FIG_BAD_CURVE_PARAMS','Invalid curve');}
function _hRoot(cat,cbt,ka,kw){var lo=1e-16,hi=1,mid,f,j;for(j=0;j<80;j+=1){mid=(lo+hi)/2;f=cbt+mid-kw/mid-cat*ka/(ka+mid);if(f<0)lo=mid;else hi=mid;}return(lo+hi)/2;}
var CURVE_FNS={
titration_pH_strong_strong:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<41||n>601)badC();
var ca=+p.C_acid_mol_l,va=+p.V_acid_ml,cb=+p.C_base_mol_l,vmax=+p.V_max_ml,kw=+p.kw_mol2_l2;
if(![ca,va,cb,vmax,kw].every(Number.isFinite)||ca<1e-4||ca>1||va<1||va>100||cb<1e-4||cb>1||vmax<1||vmax>200||kw<=0)badC();
var veq=ca*va/cb;
if(vmax<=veq)badC();
for(var pts=[],i=0;i<n;i+=1){
var v=vmax*i/(n-1),ex=ca*va-cb*v,vt=va+v,ph;
if(ex>1e-12)ph=-Math.log10(ex/vt);
else if(ex<-1e-12)ph=14+Math.log10(-ex/vt);
else ph=7;
pts.push({x:+v.toFixed(6),y:+ph.toFixed(6)});
}
return{points:pts,peak:{x:+veq.toFixed(6),y:7}};
},
titration_pH_weak_strong:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<41||n>601)badC();
var ca=+p.C_acid_mol_l,ka=+p.Ka,Va=+p.V_acid_ml,cb=+p.C_base_mol_l,vmax=+p.V_max_ml,kw=+p.kw_mol2_l2;
if(![ca,ka,Va,cb,vmax,kw].every(Number.isFinite)||ca<1e-4||ca>1||ka<1e-12||ka>1||Va<1||Va>100||cb<1e-4||cb>1||vmax<1||vmax>200||kw<=0)badC();
var veq=ca*Va/cb;
if(vmax<=veq)badC();
function phAt(v){var vt=Va+v,cat=ca*Va/vt,cbt=cb*v/vt,h=_hRoot(cat,cbt,ka,kw);return -Math.log10(h);}
for(var pts=[],i=0;i<n;i+=1){
var v=vmax*i/(n-1),ph=phAt(v);
pts.push({x:+v.toFixed(6),y:+ph.toFixed(6)});
}
return{points:pts,peak:{x:+veq.toFixed(6),y:+phAt(veq).toFixed(6)}};
},
titration_redox_potential:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<41||n>601)badC();
var ca=+p.C_analyte_mol_l,va=+p.V_analyte_ml,ct=+p.C_titrant_mol_l,vmax=+p.V_max_ml,ea=+p.E0_analyte_v,em=+p.E0_titrant_v,nt=+p.electrons_titrant,ns=+p.nernst_slope_v,h=+p.h_plus_mol_l,x0=+p.initial_oxidized_fraction;
if(![ca,va,ct,vmax,ea,em,nt,ns,h,x0].every(Number.isFinite)||ca<1e-4||ca>1||va<1||va>100||ct<1e-4||ct>1||vmax<1||vmax>100||ea<0||ea>2||em<0||em>2||nt<1||nt>8||ns<0.05||ns>0.07||h<1e-7||h>10||x0<1e-12||x0>0.01)badC();
var veq=ca*va/(nt*ct);
if(vmax<=veq||em<=ea)badC();
function eAt(v){
var x=x0+(1-x0)*(v/veq);
if(v<veq-1e-12){x=Math.min(1-1e-12,Math.max(1e-12,x));return ea+ns*Math.log10(x/(1-x));}
if(v<=veq+1e-12){return (ea+nt*em)/(nt+1);}
var y=Math.max(1e-12,(v-veq)/veq);
return em+(ns/nt)*Math.log10(y*Math.pow(h,8));
}
for(var pts=[],i=0;i<n;i+=1){
var v=vmax*i/(n-1),e=eAt(v);
pts.push({x:+v.toFixed(6),y:+e.toFixed(6)});
}
return{points:pts,peak:{x:+veq.toFixed(6),y:+((ea+nt*em)/(nt+1)).toFixed(6)}};
},
energy_profile_single_barrier:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<17||n>201)badC();
var x0=+p.x_min,x1=+p.x_max,xt=+p.x_ts,pf=+p.plateau_frac,er=+p.E_r_kj_mol,et=+p.E_ts_kj_mol,ep=+p.E_p_kj_mol;
if(![x0,x1,xt,pf,er,et,ep].every(Number.isFinite)||x0!==0||x1<.5||x1>10||pf<0||pf>.25||xt<.2||xt>.8||xt<=pf||xt>=1-pf||er<-5000||er>5000||et<-5000||et>5000||ep<-5000||ep>5000||et<=Math.max(er,ep))badC();
for(var pts=[],i=0,x,u,y;i<n;i++){
x=x0+(x1-x0)*i/(n-1);u=(x-x0)/(x1-x0);
y=u<=pf?er:u<=xt?er+(et-er)*.5*(1-Math.cos(Math.PI*(u-pf)/(xt-pf))):u<=1-pf?et-(et-ep)*.5*(1-Math.cos(Math.PI*(u-xt)/(1-pf-xt))):ep;
pts.push({x:+x.toFixed(6),y:+y.toFixed(6)});
}
return{points:pts,peak:{x:+(x0+(x1-x0)*xt).toFixed(6),y:+et.toFixed(6)}};
}, maxwell_boltzmann_3d:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<25||n>201)badC();
var T=+p.T_K,R=+p.R_kj_mol_k,mn=+p.E_min_kj_mol,mx=+p.E_max_kj_mol,ea=+p.Ea_threshold_kj_mol;
if(![T,R,mn,mx,ea].every(Number.isFinite)||T<1||T>5000||R<.0083||R>.00832||mn<0||mn>500||mx<1||mx>1000||ea<.1||ea>1000||mx<=mn||ea<=mn||ea>=mx)badC();
for(var rt=R*T,c=2/Math.sqrt(Math.PI)*Math.pow(rt,-1.5),pts=[],i=0,x;i<n;i++){
x=mn+(mx-mn)*i/(n-1);pts.push({x:+x.toFixed(6),y:x<=0?0:+(c*Math.sqrt(x)*Math.exp(-x/rt)).toFixed(6)});
}
var xp=.5*rt;
return{points:pts,peak:{x:+xp.toFixed(6),y:+(xp<=0?0:c*Math.sqrt(xp)*Math.exp(-.5)).toFixed(6)},ea_threshold:ea};
},
kinetics_decay:function(cm){
var n=cm&&cm.point_count,p=cm&&cm.params||{};
if(!Number.isInteger(n)||n<41||n>201)badC();
var o=+p.order,k=+p.k,c=+p.C0_mol_l,t0=+p.t_min_s,t1=+p.t_max_s;
if(![o,k,c,t0,t1].every(Number.isFinite)||(o!==0&&o!==1&&o!==2)||k<1e-6||k>10||c<1e-4||c>10||t0!==0||t1<1||t1>1e5)badC();
for(var pts=[],i=0,t,v;i<n;i++){t=t0+(t1-t0)*i/(n-1);v=o===0?Math.max(0,c-k*t):o===1?c*Math.exp(-k*t):c/(1+k*c*t);pts.push({x:+t.toFixed(6),y:+v.toFixed(6)});}
return{points:pts,peak:{x:+t1.toFixed(6),y:+pts[n-1].y.toFixed(6)}};
}
};
function generateCurvePoints(cm){
if(!cm||typeof cm.function_class!=='string'||!has(CURVE_FNS,cm.function_class))badC('E_FIG_UNKNOWN_CURVE_CLASS');
return CURVE_FNS[cm.function_class](cm);
}
function arrowHead(x1,y1,x2,y2,cls){
var a=Math.atan2(y2-y1,x2-x1),bx=x2-8*Math.cos(a),by=y2-8*Math.sin(a),nx=-Math.sin(a)*4.2,ny=Math.cos(a)*4.2;
return el('path',{d:'M '+fmt(x2)+' '+fmt(y2)+' L '+fmt(bx+nx)+' '+fmt(by+ny)+' L '+fmt(bx-nx)+' '+fmt(by-ny)+' Z',class:cls||'fig-arrow-head'});
}
function pushWrapped(ch,x,y,anc,cls,s){
if(!s||s.length<=22){ch.push(el('text',{x:fmt(x),y:fmt(y),'text-anchor':anc,class:cls},null,s||''));return;}
var m=s.length>>1,b=s.lastIndexOf(' ',m+5);if(b<8)b=s.indexOf(' ',m-5);
if(b<1){ch.push(el('text',{x:fmt(x),y:fmt(y),'text-anchor':anc,class:cls},null,s));return;}
ch.push(el('text',{x:fmt(x),y:fmt(y-6),'text-anchor':anc,class:cls},[el('tspan',{x:fmt(x),dy:0},null,s.slice(0,b)),el('tspan',{x:fmt(x),dy:14},null,s.slice(b+1))]));
}
function renderHessCycle(rec,W,H,terms,ch){
var hs=rec.hess_spec||{},st=hs.steps||[],bw=212,bi,si,bx,sp,c,rev,sx1,sy1,sx2,sy2;
function ah(t,a,k,s){ch.push(el(t,a,k,s));}
if(hs.constant_condition)ah('text',{x:fmt(W/2),y:66,'text-anchor':'middle',class:'fig-tick-text'},null,hs.constant_condition);
var boxes=[{x:24,y:78,w:bw,t:hs.initial_state_lv},{x:W-24-bw,y:78,w:bw,t:hs.final_state_lv},{x:(W-256)/2,y:196,w:256,t:hs.intermediate_state_lv}];
for(bi=0;bi<3;bi++){bx=boxes[bi];ah('rect',{x:fmt(bx.x),y:fmt(bx.y),width:fmt(bx.w),height:46,rx:6,class:'fig-node-box'});ah('text',{x:fmt(bx.x+bx.w/2),y:fmt(bx.y+27),'text-anchor':'middle',class:'fig-value-label'},null,bx.t||'');}
var dp=hs.direct_path||{},dx1=28+bw,dx2=W-28-bw;
ah('line',{x1:fmt(dx1),y1:101,x2:fmt(dx2),y2:101,class:'fig-hess-direct','data-hess-direct':dp.dh_kj_mol==null?'null':''+dp.dh_kj_mol});
ch.push(arrowHead(dx1,101,dx2,101));ah('text',{x:fmt(W/2),y:90,'text-anchor':'middle',class:'fig-tick-text'},null,dp.label_lv||'');
var coords=[[130,128,W/2-58,192,24,180,'start'],[W/2+58,192,W-130,128,W-24,180,'end']];
for(si=0;si<Math.min(2,st.length);si++){
sp=st[si];c=coords[si];rev=sp.arrow_direction==='reverse';sx1=rev?c[2]:c[0];sy1=rev?c[3]:c[1];sx2=rev?c[0]:c[2];sy2=rev?c[1]:c[3];
ah('line',{x1:fmt(sx1),y1:fmt(sy1),x2:fmt(sx2),y2:fmt(sy2),class:sp.traversal_direction==='reverse'?'fig-data-line fig-hess-reverse':'fig-data-line','data-hess-step':sp.id||''+si,'data-hess-traversal':sp.traversal_direction||'forward'});
ch.push(arrowHead(sx1,sy1,sx2,sy2));pushWrapped(ch,c[4],c[5],c[6],'fig-tick-text',sp.label_lv||'');
}
if(hs.closure_label_lv){ah('rect',{x:40,y:256,width:fmt(W-80),height:28,rx:5,class:'fig-node-box','data-hess-closure':'true'});ah('text',{x:fmt(W/2),y:274,'text-anchor':'middle',class:'fig-tick-text'},null,hs.closure_label_lv);}
buildAnnotations(rec,W,H-36,terms,ch);
}
function renderBurette(rec, W, H, terms, children) {
var bg = rec.burette_geometry || {};
var cols = bg.columns || [];
var dec = Number(bg.reported_decimals !== undefined ? bg.reported_decimals : 2);
var ax = (rec.axes && rec.axes.y) || null;
if (ax && ax.term_key) {
children.push(el('text', {
x: 18, y: 196, 'text-anchor': 'middle', transform: 'rotate(-90 18 196)', class: 'fig-axis-label'
}, null, resolveTerm(ax.term_key, 'axis', ax.unit, terms)));
}
for (var ci = 0; ci < cols.length; ci += 1) {
var col = cols[ci];
var vMin = Number(col.view_min_ml);
var vMax = Number(col.view_max_ml);
var yTop = Number(col.y_top_px);
var yBot = Number(col.y_bottom_px);
var xL = Number(col.x_left_px);
var xR = Number(col.x_right_px);
var xMid = (xL + xR) / 2;
var span = (vMax - vMin) || 1;
var pxPerMl = (yBot - yTop) / span;
var reading = Number(col.declared_reading_ml);
var yRead = yTop + (reading - vMin) * pxPerMl;
var depth = 7;
var isDark = col.solution_clarity === 'dark';
children.push(el('text', { x: fmt(xMid), y: fmt(yTop - 16), 'text-anchor': 'middle', class: 'fig-axis-label' }, null, col.label_lv || ''));
var dFill, dCurve;
if (isDark) {
dCurve = 'M ' + fmt(xL) + ' ' + fmt(yRead) + ' Q ' + fmt(xMid) + ' ' + fmt(yRead + 2 * depth) + ' ' + fmt(xR) + ' ' + fmt(yRead);
dFill = dCurve + ' L ' + fmt(xR) + ' ' + fmt(yBot + 8) + ' L ' + fmt(xL) + ' ' + fmt(yBot + 8) + ' Z';
} else {
dCurve = 'M ' + fmt(xL) + ' ' + fmt(yRead - depth) + ' Q ' + fmt(xMid) + ' ' + fmt(yRead + depth) + ' ' + fmt(xR) + ' ' + fmt(yRead - depth);
dFill = dCurve + ' L ' + fmt(xR) + ' ' + fmt(yBot + 8) + ' L ' + fmt(xL) + ' ' + fmt(yBot + 8) + ' Z';
}
children.push(el('path', { d: dFill, class: isDark ? 'fig-liquid-dark' : 'fig-liquid-clear' }));
children.push(el('path', {
d: dCurve, class: 'fig-meniscus-curve', 'data-column-id': col.id || ('col-' + ci), 'data-meniscus-edge': isDark ? 'upper_edge' : 'lower_meniscus', 'data-meniscus-read-y': fmt(yRead), 'data-declared-reading-ml': String(col.declared_reading_ml)
}));
children.push(el('line', { x1: fmt(xL), y1: fmt(yTop - 8), x2: fmt(xL), y2: fmt(yBot + 10), class: 'fig-glass-wall' }));
children.push(el('line', { x1: fmt(xR), y1: fmt(yTop - 8), x2: fmt(xR), y2: fmt(yBot + 10), class: 'fig-glass-wall' }));
children.push(el('line', { x1: fmt(xL - 8), y1: fmt(yBot + 14), x2: fmt(xR + 8), y2: fmt(yBot + 14), class: 'fig-glass-wall' }));
children.push(el('rect', { x: fmt(xL + 8), y: fmt(yBot + 10), width: fmt(xR - xL - 16), height: 8, rx: 2, class: 'fig-annot-box' }));
var totalTenths = Math.round(span * 10);
for (var t = 0; t <= totalTenths; t += 1) {
var tv = vMin + t * 0.1;
var yv = yTop + (tv - vMin) * pxPerMl;
var absTenths = Math.round(tv * 10);
var isMajor = (absTenths % 10 === 0);
var isHalf = (!isMajor && absTenths % 5 === 0);
var tickLen = isMajor ? 20 : (isHalf ? 14 : 8);
children.push(el('line', {
x1: fmt(xL), y1: fmt(yv), x2: fmt(xL + tickLen), y2: fmt(yv), class: isMajor ? 'fig-tick-major' : 'fig-tick-minor'
}));
if (isMajor || isHalf) {
children.push(el('text', {
x: fmt(xL - 8), y: fmt(yv + 4), 'text-anchor': 'end', class: 'fig-tick-text', 'data-scale-label': 'true'
}, null, fmtLv(tv, dec) + ' mL'));
}
}
var sightX2 = (cols.length > 1) ? (xR + 40) : (xR + 54);
var calloutX = (cols.length > 1) ? (xR + 46) : (xR + 60);
children.push(el('line', {
x1: fmt(xL - 4), y1: fmt(yRead), x2: fmt(sightX2), y2: fmt(yRead), class: 'fig-sight-line', 'data-meniscus-sightline': 'true', 'data-meniscus-read-y': fmt(yRead)
}));
if (!col.hide_reading_label) {
var rTxt = col.display_reading_lv || (fmtLv(reading, dec) + ' mL');
children.push(el('text', { x: fmt(calloutX), y: fmt(yRead + 4), class: 'fig-value-label' }, null, rTxt));
if (cols.length > 1) {
children.push(el('text', {
x: fmt(calloutX), y: fmt(yRead + 18), class: 'fig-tick-text'
}, null, isDark ? 'augšējā mala' : 'apakšējais menisks'));
children.push(el('text', {
x: fmt(calloutX), y: fmt(yRead + 31), class: 'fig-tick-text'
}, null, '(acu līmenī)'));
} else {
children.push(el('text', {
x: fmt(calloutX), y: fmt(yRead + 19), class: 'fig-tick-text'
}, null, isDark ? 'augšējā mala (acu līmenī)' : 'apakšējais menisks (acu līmenī)'));
}
}
if (col.show_parallax_guides) {
var eyeX = xR + 240;
children.push(el('line', { x1: fmt(xMid + 12), y1: fmt(yRead), x2: fmt(eyeX - 10), y2: fmt(yRead - 38), class: 'fig-parallax-line' }));
children.push(el('text', { x: fmt(eyeX), y: fmt(yRead - 34), class: 'fig-tick-text' }, null, 'acs virs meniska → šķiet par mazu'));
children.push(el('line', { x1: fmt(xMid + 12), y1: fmt(yRead), x2: fmt(eyeX - 10), y2: fmt(yRead + 44), class: 'fig-parallax-line' }));
children.push(el('text', { x: fmt(eyeX), y: fmt(yRead + 48), class: 'fig-tick-text' }, null, 'acs zem meniska → šķiet par lielu'));
}
var axX = xR + 22;
children.push(el('text', { x: fmt(axX), y: fmt(yTop + 8), 'text-anchor': 'middle', class: 'fig-tick-text' }, null, 'skala ↓'));
children.push(el('line', { x1: fmt(axX), y1: fmt(yTop + 14), x2: fmt(axX), y2: fmt(yBot - 22), class: 'fig-arrow-line' }));
children.push(el('polygon', {
points: fmt(axX) + ',' + fmt(yBot - 14) + ' ' + fmt(axX - 4) + ',' + fmt(yBot - 24) + ' ' + fmt(axX + 4) + ',' + fmt(yBot - 24), class: 'fig-arrow-head'
}));
}
var anns = rec.annotations || [];
var yAnn = H - 10 - anns.length * 28;
buildAnnotations(rec, W, yAnn, terms, children);
}
function renderDilution(rec, W, H, terms, children) {
var ds = rec.dilution_spec || {};
var steps = ds.steps || [];
var anns = rec.annotations || [];
var yAnn = H - 10 - anns.length * 28;
var availH = yAnn - 68;
var rowH = availH / Math.max(1, steps.length);
for (var i = 0; i < steps.length; i += 1) {
var st = steps[i];
var cy = 68 + i * rowH + rowH * 0.5;
var topY = cy - 44;
var px = 42;
children.push(el('rect', { x: fmt(px - 6), y: fmt(topY), width: 12, height: 64, rx: 3, class: 'fig-glass-wall fig-node-box' }));
children.push(el('rect', { x: fmt(px - 10), y: fmt(topY + 20), width: 20, height: 22, rx: 8, class: 'fig-liquid-clear' }));
children.push(el('line', { x1: fmt(px - 9), y1: fmt(topY + 12), x2: fmt(px + 9), y2: fmt(topY + 12), class: 'fig-flask-mark' }));
children.push(el('text', { x: fmt(px + 16), y: fmt(topY + 24), class: 'fig-value-label' }, null, st.pipette_label_lv || ''));
children.push(el('text', { x: fmt(px + 16), y: fmt(topY + 42), class: 'fig-tick-text' }, null, 'c₁ = ' + String(st.stock_c_mol_l || '').replace('.', ',') + ' mol/L'));
var ax1 = 264, ax2 = 404;
children.push(el('line', { x1: fmt(ax1), y1: fmt(topY + 34), x2: fmt(ax2 - 6), y2: fmt(topY + 34), class: 'fig-arrow-line' }));
children.push(el('polygon', {
points: fmt(ax2) + ',' + fmt(topY + 34) + ' ' + fmt(ax2 - 9) + ',' + fmt(topY + 29) + ' ' + fmt(ax2 - 9) + ',' + fmt(topY + 39), class: 'fig-arrow-head'
}));
children.push(el('text', { x: fmt((ax1 + ax2) / 2), y: fmt(topY + 20), 'text-anchor': 'middle', class: 'fig-value-label' }, null, st.factor_label_lv || ''));
var fx = 438;
var neckTop = topY, neckBot = topY + 30, bulbBot = topY + 72;
var markY = topY + 18;
var dFlask = 'M ' + fmt(fx - 8) + ' ' + fmt(neckTop) + ' L ' + fmt(fx - 8) + ' ' + fmt(neckBot) +
' L ' + fmt(fx - 26) + ' ' + fmt(bulbBot) + ' L ' + fmt(fx + 26) + ' ' + fmt(bulbBot) +
' L ' + fmt(fx + 8) + ' ' + fmt(neckBot) + ' L ' + fmt(fx + 8) + ' ' + fmt(neckTop);
var dLiquid = 'M ' + fmt(fx - 7) + ' ' + fmt(markY) + ' Q ' + fmt(fx) + ' ' + fmt(markY + 4) + ' ' + fmt(fx + 7) + ' ' + fmt(markY) +
' L ' + fmt(fx + 7) + ' ' + fmt(neckBot) + ' L ' + fmt(fx + 25) + ' ' + fmt(bulbBot - 1) +
' L ' + fmt(fx - 25) + ' ' + fmt(bulbBot - 1) + ' L ' + fmt(fx - 7) + ' ' + fmt(neckBot) + ' Z';
children.push(el('path', { d: dLiquid, class: 'fig-liquid-clear' }));
children.push(el('path', { d: dFlask, class: 'fig-glass-wall fig-data-line' }));
children.push(el('line', { x1: fmt(fx - 13), y1: fmt(markY), x2: fmt(fx + 13), y2: fmt(markY), class: 'fig-flask-mark', 'data-flask-mark-y': fmt(markY) }));
children.push(el('text', { x: fmt(fx + 30), y: fmt(topY + 22), class: 'fig-value-label' }, null, st.flask_label_lv || ''));
children.push(el('text', { x: fmt(fx + 30), y: fmt(topY + 42), class: 'fig-tick-text' }, null, st.result_label_lv || ''));
}
buildAnnotations(rec, W, yAnn, terms, children);
}
function fieldTol(f,v){if(!f)return 0;if(f.tolerance_mode==='absolute')return Math.abs(+(f.abs_value!==undefined?f.abs_value:0));var sf=+(f.sig_figs||3);if(v===0)return 0;var e=Math.floor(Math.log(Math.abs(v))/Math.LN10);return .5*Math.pow(10,e-sf+1);}
function evaluateFitLine(rec,drawn){
var sp=rec.span||{},f=rec.fit_line||((rec.grading_reference||{}).fit_line)||{},tf=rec.tolerance_fields||{};
var x1=Math.max(+drawn.x_min,+sp.x_min),x2=Math.min(+drawn.x_max,+sp.x_max);
if(!(x2>=x1))return{status:'NOT_ASSESSED',assessed_x_range:null,slope_ok:false,intercept_ok:false,point_ok:false,beyond_span:'not_assessed',max_point_deviation:0,tolerances:{slope:0,intercept:0,point_acceptance:0}};
var ts=fieldTol(tf.slope,+f.slope),ti=fieldTol(tf.intercept,+f.intercept),tp=fieldTol(tf.point_acceptance,+f.intercept);
var so=Math.abs(+drawn.slope-+f.slope)<=ts,io=Math.abs(+drawn.intercept-+f.intercept)<=ti,md=0,i,x;
for(i=0;i<11;i++){x=x1+(x2-x1)*i/10;md=Math.max(md,Math.abs((+drawn.slope*x+ +drawn.intercept)-(+f.slope*x+ +f.intercept)));}
var po=md<=tp;
return{status:so&&io&&po?'ACCEPTED':'REJECTED',assessed_x_range:{x_min:x1,x_max:x2},slope_ok:so,intercept_ok:io,point_ok:po,beyond_span:'not_assessed',max_point_deviation:+md.toFixed(6),tolerances:{slope:ts,intercept:ti,point_acceptance:tp}};
}
function buildSvgAst(rec, options) {
options = options || {};
validateRecordForRender(rec);
var doc = options.doc || root.document;
var terms = options.terms || (root.SimTerms && root.SimTerms.getDefault ? root.SimTerms.getDefault() : null);
var conventions = options.conventions || null;
var theme = activeTheme(doc, options.theme);
var vb = (rec.print_spec && Array.isArray(rec.print_spec.viewBox) && rec.print_spec.viewBox.length === 4)
? rec.print_spec.viewBox : [0, 0, 760, 360];
var W = Number(vb[2]), H = Number(vb[3]);
var pfx = options.idPrefix ? (options.idPrefix + '-') : '';
var titleId = pfx + rec.id + '-title';
var descId = pfx + rec.id + '-desc';
var titleTxt = resolveTerm(rec.title_key, 'title', null, terms);
var children = [
el('title', { id: titleId }, null, titleTxt), el('desc', { id: descId }, null, rec.description_lv), el('rect', { x: 0, y: 0, width: fmt(W), height: fmt(H), rx: 6, class: 'fig-bg' }), el('text', { x: 24, y: 28, class: 'fig-title-text' }, null, titleTxt)
];
if (rec.subtitle_lv) {
children.push(el('text', { x: 24, y: 46, class: 'fig-subtitle-text' }, null, rec.subtitle_lv));
}
if (rec.type === 'bar') renderBar(rec, W, H, terms, children);
else if (rec.type === 'chain') renderChain(rec, W, H, terms, children);
else if (rec.type === 'band') renderBand(rec, W, H, terms, children);
else if (rec.type === 'burette') renderBurette(rec, W, H, terms, children);
else if (rec.type === 'dilution') renderDilution(rec, W, H, terms, children);
else if (rec.type === 'hess_cycle') renderHessCycle(rec, W, H, terms, children);
else renderCartesianPlot(rec, W, H, terms, conventions, children);
var svgAttrs = {
xmlns: SVG_NS, viewBox: vb.join(' '), role: 'img', 'aria-labelledby': titleId + ' ' + descId, class: 'fig-svg fig-theme-' + theme, 'data-figure-id': rec.id, 'data-figure-type': rec.type, 'data-theme-class': theme
};
if (rec.tolerance_coupling && rec.tolerance_coupling.tolerance_class) {
svgAttrs['data-tolerance-class'] = rec.tolerance_coupling.tolerance_class;
}
return el('svg', svgAttrs, children);
}
function serializeAst(node) {
var out = '<' + node.tag;
var keys = Object.keys(node.attrs || {}).sort();
for (var i = 0; i < keys.length; i += 1) {
out += ' ' + keys[i] + '="' + escXml(node.attrs[keys[i]]) + '"';
}
out += '>';
if (node.text !== undefined && node.text !== null) out += escXml(node.text);
var ch = node.children || [];
for (var j = 0; j < ch.length; j += 1) out += serializeAst(ch[j]);
out += '</' + node.tag + '>';
return out;
}
function mountAst(doc, node) {
var dom = typeof doc.createElementNS === 'function'
? doc.createElementNS(SVG_NS, node.tag)
: doc.createElement(node.tag);
var keys = Object.keys(node.attrs || {}).sort();
for (var i = 0; i < keys.length; i += 1) {
if (typeof dom.setAttribute === 'function') dom.setAttribute(keys[i], String(node.attrs[keys[i]]));
}
if (node.text !== undefined && node.text !== null) dom.textContent = String(node.text);
var ch = node.children || [];
for (var j = 0; j < ch.length; j += 1) dom.appendChild(mountAst(doc, ch[j]));
return dom;
}
function renderFigureSvg(record, options) {
return serializeAst(buildSvgAst(record, options));
}
function renderFigureElement(doc, record, options) {
var opts = Object.assign({}, options || {}, { doc: doc });
return mountAst(doc, buildSvgAst(record, opts));
}
function load(doc) {
doc = doc || root.document;
var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(ID) : null;
req(node, 'E_FIGURES_MISSING', 'Attēlu sala #' + ID + ' nav atrasta.', { island: ID });
var raw = node.textContent !== undefined ? node.textContent : node.innerText;
req(typeof raw === 'string' && raw.trim(), 'E_FIGURES_EMPTY', 'Attēlu sala #' + ID + ' ir tukša.', { island: ID });
var data;
try { data = JSON.parse(raw); } catch (e) {
fail('E_FIGURES_JSON', 'Attēlu sala #' + ID + ' satur bojātu JSON.', { island: ID, cause: String(e.message || e) });
}
req(data && typeof data === 'object' && !Array.isArray(data), 'E_FIGURES_SHAPE', 'Attēlu sala #' + ID + ' nav objekts.', { island: ID });
req(data.island_id === ID, 'E_FIGURES_ID', 'Attēlu salas island_id neatbilst.', { island: ID, found: data.island_id });
req(data.schema_version === 1 && data.status === 'authored', 'E_FIGURES_SHAPE', 'Attēlu salas versija vai statuss nederīgs.', { island: ID });
req(Array.isArray(data.figures) && data.figures.length > 0, 'E_FIGURES_EMPTY', 'Attēlu salā nav ierakstu.', { island: ID });
var byId = Object.create(null);
var byConcept = Object.create(null);
for (var i = 0; i < data.figures.length; i += 1) {
var f = data.figures[i];
validateRecordForRender(f);
req(!has(byId, f.id), 'E_FIG_DUPLICATE_ID', 'Atkārtots attēla id: ' + f.id, { id: f.id });
byId[f.id] = f;
var cids = f.concept_ids || [];
for (var j = 0; j < cids.length; j += 1) {
if (!byConcept[cids[j]]) byConcept[cids[j]] = [];
byConcept[cids[j]].push(f);
}
}
return {
schema_version: 1, format_version: data.format_version || 1, island_id: ID, status: data.status, figures: data.figures.slice(), byId: byId, byConcept: byConcept, total: data.figures.length
};
}
function getByConcept(conceptId, island) {
var isl = island || state.island;
if (!isl || !isl.byConcept) return [];
return (isl.byConcept[conceptId] || []).slice();
}
function getById(figId, island) {
var isl = island || state.island;
req(isl && isl.byId, 'E_FIGURES_NOT_LOADED', 'Attēlu sala #' + ID + ' nav ielādēta.', { island: ID, figureId: figId });
req(has(isl.byId, figId), 'E_FIG_UNKNOWN_ID', 'Attēls nav atrasts: ' + String(figId), { figureId: figId });
return isl.byId[figId];
}
function renderSlotError(doc, container, err) {
var box = doc.createElement('div');
box.className = 'fig-error-slot error-box';
box.setAttribute('role', 'alert');
var code = (err && err.code) ? err.code : 'E_FIGURES_ERROR';
var msg = (err && err.message) ? err.message : String(err);
box.setAttribute('data-error-code', code);
box.textContent = 'Attēlu salas kļūda (' + code + '): ' + msg;
container.appendChild(box);
return box;
}
function activateLazySlot(doc, wrapper, record, options) {
options = options || {};
if (wrapper.getAttribute('data-lazy-state') === 'rendered') return false;
while (wrapper.firstChild) wrapper.removeChild(wrapper.firstChild);
var opts = Object.assign({}, options, { doc: doc });
var svgEl = renderFigureElement(doc, record, opts);
wrapper.appendChild(svgEl);
var cap = doc.createElement('p');
cap.className = 'fig-caption';
var cite = record.citations || {};
var tolTxt = record.tolerance_coupling
? (' · Tolerance (' + record.tolerance_coupling.tolerance_class + ', PROPOSED)')
: ' · Strukturāla shēma (bez mērījuma tolerances)';
cap.textContent = record.id + ' · ' + record.epistemic_label + ' · #' + (cite.master_anchor || '') + tolTxt;
wrapper.appendChild(cap);
wrapper.setAttribute('data-lazy-state', 'rendered');
var svgBytes = renderFigureSvg(record, opts).length;
state.renderEvents.push({
seq: state.renderEvents.length + 1, figureId: record.id, conceptId: options.conceptId || null, trigger: options.trigger || 'lazy-activate', theme: activeTheme(doc, options.theme), svgBytes: svgBytes
});
return true;
}
function mountSlot(doc, container, conceptId, figureIds, options) {
options = options || {};
if (state.loadError) {
container.setAttribute('data-slot-status', 'error-' + state.loadError.code);
renderSlotError(doc, container, state.loadError);
return { status: 'ERROR', error: state.loadError, renderedCount: 0, pendingCount: 0 };
}
var isl = options.island || state.island;
if (!isl) {
var notLoaded = new FiguresError('E_FIGURES_NOT_LOADED', 'Attēlu sala #' + ID + ' nav ielādēta.', { island: ID });
container.setAttribute('data-slot-status', 'error-E_FIGURES_NOT_LOADED');
renderSlotError(doc, container, notLoaded);
return { status: 'ERROR', error: notLoaded, renderedCount: 0, pendingCount: 0 };
}
var list = [];
if (Array.isArray(figureIds) && figureIds.length) {
for (var i = 0; i < figureIds.length; i += 1) {
if (has(isl.byId, figureIds[i])) list.push(isl.byId[figureIds[i]]);
}
} else {
list = getByConcept(conceptId, isl);
}
var rendered = 0, pending = 0;
for (var j = 0; j < list.length; j += 1) {
var rec = list[j];
var card = doc.createElement('figure');
card.className = 'fig-card';
card.setAttribute('data-figure-id', rec.id);
card.setAttribute('data-lazy-slot', 'true');
card.setAttribute('data-lazy-state', 'pending');
if (options.defer) {
var ph = doc.createElement('p');
ph.className = 'fig-lazy-placeholder';
ph.textContent = 'Attēls ' + rec.id + ' gaida atvēršanu (slinkā ielāde).';
card.appendChild(ph);
card._lazyRecord = rec;
card._lazyOptions = Object.assign({}, options, { conceptId: conceptId });
container.appendChild(card);
pending += 1;
if (typeof root.IntersectionObserver === 'function') {
(function (cNode, rObj, opts) {
var obs = new root.IntersectionObserver(function (entries) {
for (var k = 0; k < entries.length; k += 1) {
if (entries[k].isIntersecting) {
activateLazySlot(doc, cNode, rObj, Object.assign({}, opts, { trigger: 'viewport-enter' }));
obs.disconnect();
break;
}
}
});
obs.observe(cNode);
})(card, rec, card._lazyOptions);
}
} else {
container.appendChild(card);
activateLazySlot(doc, card, rec, Object.assign({}, options, { conceptId: conceptId, trigger: options.trigger || 'drawer-open' }));
rendered += 1;
}
}
return { status: 'OK', renderedCount: rendered, pendingCount: pending };
}
function init(doc) {
doc = doc || root.document;
state.island = null;
state.loadError = null;
try {
var isl = load(doc);
state.island = isl;
renderStatus(doc, isl);
return isl;
} catch (err) {
state.loadError = err;
renderError(doc, err);
return null;
}
}
function renderStatus(doc, isl) {
doc = doc || root.document;
var n = doc && doc.getElementById ? doc.getElementById('sim-figures-status') : null;
if (!n || !isl) return;
n.textContent = 'Attēlu sala (#sim-figures): ' + isl.total + ' ieraksti ielādēti (0 SVG parsēti ielādes brīdī — slinkā ielāde aktīva).';
n.hidden = false;
}
function renderError(doc, err) {
doc = doc || root.document;
var b = doc && doc.getElementById ? doc.getElementById('sim-figures-error') : null;
if (!b) return;
var code = err && err.code ? err.code : 'E_FIGURES_ERROR';
b.textContent = 'Attēlu salas kļūda (' + code + '): ' + (err && err.message ? err.message : String(err));
b.hidden = false;
}
function sha256Utf8(str) {
var K = [
1116352408, 1899447441, -1245643825, -373957723, 961987163, 1508970993, -1841331548, -1424204075, -670586216, 310598401, 607225278, 1426881987, 1925078388, -2132889090, -1680079193, -1046744716, -459576895, -272742522, 264347078, 604807628, 770255983, 1249150122, 1555081692, 1996064986, -1740746414, -1473132947, -1341970488, -1084653625, -958395405, -710438585, 113926993, 338241895, 666307205, 773529912, 1294757372, 1396182291, 1695183700, 1986661051, -2117940946, -1838011259, -1564481375, -1474664885, -1035236496, -949202525, -778901479, -694614492, -200395387, 275423344, 430227734, 506948616, 659060556, 883997877, 958139571, 1322822218, 1537002063, 1747873779, 1955562222, 2024104815, -2067236844, -1933114872, -1866530822, -1538233109, -1090935817, -965641998
];
var H = [1779033703, -1150833019, 1013904242, -1521486534, 1359893119, -1694144372, 528734635, 1541459225];
var bytes = [], i, c;
for (i = 0; i < str.length; i += 1) {
c = str.charCodeAt(i);
if (c < 128) bytes.push(c);
else if (c < 2048) { bytes.push(192 | (c >> 6), 128 | (c & 63)); }
else if (c >= 0xd800 && c <= 0xdbff && i + 1 < str.length) {
c = 0x10000 + (((c & 0x3ff) << 10) | (str.charCodeAt(++i) & 0x3ff));
bytes.push(240 | (c >> 18), 128 | ((c >> 12) & 63), 128 | ((c >> 6) & 63), 128 | (c & 63));
} else { bytes.push(224 | (c >> 12), 128 | ((c >> 6) & 63), 128 | (c & 63)); }
}
var bitLen = bytes.length * 8;
bytes.push(0x80);
while ((bytes.length % 64) !== 56) bytes.push(0);
var hi = Math.floor(bitLen / 0x100000000), lo = bitLen >>> 0;
bytes.push((hi >>> 24) & 255, (hi >>> 16) & 255, (hi >>> 8) & 255, hi & 255, (lo >>> 24) & 255, (lo >>> 16) & 255, (lo >>> 8) & 255, lo & 255);
var w = new Array(64);
function r(x, n) { return (x >>> n) | (x << (32 - n)); }
for (i = 0; i < bytes.length; i += 64) {
for (var t = 0; t < 16; t += 1) w[t] = (bytes[i + t * 4] << 24) | (bytes[i + t * 4 + 1] << 16) | (bytes[i + t * 4 + 2] << 8) | bytes[i + t * 4 + 3];
for (t = 16; t < 64; t += 1) {
var s0 = r(w[t - 15], 7) ^ r(w[t - 15], 18) ^ (w[t - 15] >>> 3);
var s1 = r(w[t - 2], 17) ^ r(w[t - 2], 19) ^ (w[t - 2] >>> 10);
w[t] = (w[t - 16] + s0 + w[t - 7] + s1) | 0;
}
var a = H[0], b = H[1], cc = H[2], d = H[3], e = H[4], f = H[5], g = H[6], h = H[7];
for (t = 0; t < 64; t += 1) {
var S1 = r(e, 6) ^ r(e, 11) ^ r(e, 25), ch = (e & f) ^ ((~e) & g), temp1 = (h + S1 + ch + K[t] + w[t]) | 0;
var S0 = r(a, 2) ^ r(a, 13) ^ r(a, 22), maj = (a & b) ^ (a & cc) ^ (b & cc), temp2 = (S0 + maj) | 0;
h = g; g = f; f = e; e = (d + temp1) | 0; d = cc; cc = b; b = a; a = (temp1 + temp2) | 0;
}
H[0] = (H[0] + a) | 0; H[1] = (H[1] + b) | 0; H[2] = (H[2] + cc) | 0; H[3] = (H[3] + d) | 0;
H[4] = (H[4] + e) | 0; H[5] = (H[5] + f) | 0; H[6] = (H[6] + g) | 0; H[7] = (H[7] + h) | 0;
}
var hex = '';
for (i = 0; i < 8; i += 1) hex += ('00000000' + (H[i] >>> 0).toString(16)).slice(-8);
return hex;
}
root.SimFigures = {
ISLAND_ID: ID, TYPE_REGISTRY: TYPE_REGISTRY, CURVE_FNS: CURVE_FNS, generateCurvePoints: generateCurvePoints, FiguresError: FiguresError, load: load, init: init, getByConcept: getByConcept, getById: getById, getDefault: function () { return state.island; }, getDefaultError: function () { return state.loadError; }, setDefaultError: function (e) { state.loadError = e || null; }, renderFigureSvg: renderFigureSvg, renderFigureElement: renderFigureElement, evaluateFitLine: evaluateFitLine, mountSlot: mountSlot, activateLazySlot: activateLazySlot, getRenderEvents: function () { return state.renderEvents.slice(); }, clearRenderEvents: function () { state.renderEvents = []; }, renderStatus: renderStatus, renderError: renderError, sha256Utf8: sha256Utf8
};
if (typeof module !== 'undefined' && module.exports) module.exports = root.SimFigures;
})(typeof globalThis !== 'undefined' ? globalThis : this);
