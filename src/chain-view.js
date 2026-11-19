(function (root) {
'use strict';
var ID = 'sim-chains';
var state = { island: null, mounts: Object.create(null), byId: Object.create(null) };
function fail(code, message) {
  var e = new Error(message);
  e.code = code;
  return e;
}
function E(doc, tag, cls, text) {
  var n = doc.createElement(tag);
  if (cls) n.className = cls;
  if (text !== undefined && text !== null) n.textContent = String(text);
  return n;
}
function clear(n) { while (n.firstChild) n.removeChild(n.firstChild); }
function focus(doc, n) { if (n && typeof n.focus === 'function') n.focus(); }
function bytes(hex) {
  var out = [];
  for (var i = 0; i < hex.length; i += 2) out.push(parseInt(hex.slice(i, i + 2), 16));
  return out;
}
function b64(text) {
  var raw = root.atob(text);
  var out = [];
  for (var i = 0; i < raw.length; i += 1) out.push(raw.charCodeAt(i));
  return out;
}
function utf8(arr) { return new TextDecoder('utf-8').decode(new Uint8Array(arr)); }
function unseal(p) {
  if (!p || p.alg !== 'xor-v1') throw fail('E_CHAIN_ALG', 'Unknown chain payload algorithm.');
  var key = bytes(p.key || '');
  var data = b64(p.data || '');
  var out = [];
  for (var i = 0; i < data.length; i += 1) out.push(data[i] ^ key[i % key.length]);
  try {
    return JSON.parse(utf8(out));
  } catch (error) {
    throw fail('E_CHAIN_JSON', 'Invalid chain payload JSON.');
  }
}
function load(doc) {
  if (state.island) return state.island;
  var node = doc && doc.getElementById ? doc.getElementById(ID) : null;
  if (!node) throw fail('E_CHAINS_MISSING', 'Darba piemēru sala #' + ID + ' nav atrasta.');
  var data;
  try { data = JSON.parse(node.textContent || ''); }
  catch (error) { throw fail('E_CHAINS_JSON', 'Darba piemēru sala nav derīgs JSON.'); }
  if (!data || data.island_id !== ID || !Array.isArray(data.chains)) throw fail('E_CHAINS_SHAPE', 'Nepareiza darba piemēru salas forma.');
  state.island = data;
  state.byId = Object.create(null);
  for (var i = 0; i < data.chains.length; i += 1) state.byId[data.chains[i].id] = data.chains[i];
  return data;
}
function get(chainId) {
  if (!state.byId[chainId]) throw fail('E_CHAIN_UNKNOWN', 'Nezināma ķēde: ' + chainId + '.');
  return state.byId[chainId];
}
function refs(chain, stepId) {
  var out = [];
  for (var i = 0; i < (chain.figure_refs || []).length; i += 1) if (chain.figure_refs[i].step_id === stepId) out.push(chain.figure_refs[i]);
  return out;
}
function mountFigure(doc, host, chain, stepId) {
  var list = refs(chain, stepId);
  clear(host);
  host.setAttribute('data-figure-state', 'mounted');
  if (!list.length) return;
  if (!root.SimFigures || typeof root.SimFigures.mountSlot !== 'function') {
    host.appendChild(E(doc, 'p', 'chain-figure-error', 'Attēlu slānis nav ielādēts.'));
    return;
  }
  for (var i = 0; i < list.length; i += 1) {
    try { root.SimFigures.mountSlot(doc, host, chain.outcome_ids[0], [list[i].figure_id], { trigger: 'chain-reveal', defer: false }); }
    catch (error) { host.appendChild(E(doc, 'p', 'chain-figure-error', 'Attēla kļūda.')); }
  }
}
function mountChain(doc, host, chainId, key) {
  var chain = get(chainId);
  key = key || 'index';
  var id = 'chain-' + chainId + '-' + key;
  var article = E(doc, 'article', 'chain');
  article.id = id;
  article.setAttribute('data-revealed-count', '0');
  article.setAttribute('data-revealed-all', 'false');
  article.appendChild(E(doc, 'p', 'chain-banner', chain.banner_lv));
  var title = E(doc, 'h3', 'chain-title', chain.title_lv);
  title.tabIndex = -1;
  article.appendChild(title);
  article.appendChild(E(doc, 'p', 'chain-subtitle', chain.subtitle_lv));
  var mc = chain.master_citation || {};
  article.appendChild(E(doc, 'p', 'chain-citation', (mc.heading_lv || '') + ' ' + (mc.anchor || '')));
  var givens = E(doc, 'dl', 'chain-givens');
  for (var g = 0; g < (chain.givens || []).length; g += 1) {
    var item = chain.givens[g];
    if (item.kind === 'points') continue;
    var row = E(doc, 'div', 'chain-given');
    row.appendChild(E(doc, 'dt', null, item.label_lv));
    row.appendChild(E(doc, 'dd', null, item.display_lv + ' ' + (item.unit || '')));
    givens.appendChild(row);
  }
  article.appendChild(givens);
  var list = E(doc, 'ol', 'chain-steps');
  var map = Object.create(null);
  for (var i = 0; i < chain.steps.length; i += 1) {
    var st = chain.steps[i];
    var li = E(doc, 'li', 'chain-step');
    li.setAttribute('data-step-id', st.step_id);
    li.setAttribute('data-revealed', 'false');
    li.appendChild(E(doc, 'p', 'chain-step-quantity', st.quantity_lv));
    li.appendChild(E(doc, 'p', 'chain-step-statement', st.statement_lv));
    var fig = E(doc, 'div', 'chain-figure-host');
    fig.setAttribute('data-figure-state', 'hidden');
    var rs = refs(chain, st.step_id);
    if (rs.length) {
      var ids = [];
      for (var r = 0; r < rs.length; r += 1) ids.push(rs[r].figure_id);
      fig.appendChild(E(doc, 'p', 'chain-figure-placeholder', 'Attēls: ' + ids.join(', ')));
    }
    li.appendChild(fig);
    var btn = E(doc, 'button', 'chain-reveal-btn', 'Parādīt rezultātu');
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    li.appendChild(btn);
    var result = E(doc, 'div', 'chain-result');
    result.hidden = true;
    li.appendChild(result);
    list.appendChild(li);
    map[st.step_id] = { li: li, btn: btn, result: result, fig: fig };
  }
  article.appendChild(list);
  var allBtn = E(doc, 'button', 'chain-reveal-all', 'Parādīt visus soļus');
  allBtn.id = id + '-reveal-all';
  allBtn.type = 'button';
  var collapseBtn = E(doc, 'button', 'chain-collapse', 'Sakļaut atpakaļ');
  collapseBtn.id = id + '-collapse';
  collapseBtn.type = 'button';
  collapseBtn.hidden = true;
  article.appendChild(allBtn);
  article.appendChild(collapseBtn);
  var confirm = E(doc, 'div', 'chain-confirm');
  confirm.id = id + '-confirm';
  confirm.hidden = true;
  confirm.setAttribute('role', 'group');
  confirm.appendChild(E(doc, 'p', null, 'Vai tiešām vēlaties atklāt visus soļus? Šis ir pašizskaidrošanas treniņš.'));
  var yes = E(doc, 'button', 'chain-confirm-yes', 'Jā, atklāt visus');
  yes.id = id + '-confirm-yes';
  yes.type = 'button';
  var no = E(doc, 'button', 'chain-confirm-no', 'Nē');
  no.id = id + '-confirm-no';
  no.type = 'button';
  confirm.appendChild(yes);
  confirm.appendChild(no);
  article.appendChild(confirm);
  article.appendChild(E(doc, 'p', 'chain-print-note chain-print-note-collapsed', 'Pamatojums ir interaktīvs; drukātajā versijā atklājiet soļus pirms drukāšanas.'));
  clear(host);
  host.appendChild(article);
  var mount = { id: id, chainId: chainId, chain: chain, host: host, element: article, key: key,
    revealed: Object.create(null), steps: map, title: title, confirm: confirm, allBtn: allBtn,
    collapseBtn: collapseBtn, yes: yes, no: no };
  state.mounts[id] = mount;
  var stepIds = Object.keys(map);
  for (var s = 0; s < stepIds.length; s += 1) {
    (function (sid) { map[sid].btn.addEventListener('click', function () { reveal(doc, mount, sid); }); })(stepIds[s]);
  }
  allBtn.addEventListener('click', function () { confirm.hidden = false; focus(doc, yes); });
  yes.addEventListener('click', function () { revealAll(doc, mount); });
  no.addEventListener('click', function () { confirm.hidden = true; focus(doc, allBtn); });
  collapseBtn.addEventListener('click', function () { collapse(doc, mount); });
  return { status: 'OK', chainId: chainId, mountId: id, element: article };
}
function reveal(doc, mount, stepId) {
  var step = null;
  for (var i = 0; i < mount.chain.steps.length; i += 1) if (mount.chain.steps[i].step_id === stepId) step = mount.chain.steps[i];
  if (!step) throw fail('E_CHAIN_STEP', 'Nezināms solis ' + stepId + '.');
  if (mount.revealed[stepId]) return { status: 'ALREADY_REVEALED', stepId: stepId };
  var ref = mount.steps[stepId];
  var payload = unseal(step.sealed);
  clear(ref.result);
  ref.result.hidden = false;
  ref.result.appendChild(E(doc, 'p', 'chain-result-value', (payload.display_lv || payload.value || '') + (payload.unit ? ' ' + payload.unit : '')));
  ref.result.appendChild(E(doc, 'p', 'chain-result-reasoning', payload.reasoning_lv || ''));
  ref.btn.hidden = true;
  ref.btn.setAttribute('aria-expanded', 'true');
  mountFigure(doc, ref.fig, mount.chain, stepId);
  ref.li.setAttribute('data-revealed', 'true');
  mount.revealed[stepId] = true;
  var count = Object.keys(mount.revealed).length;
  mount.element.setAttribute('data-revealed-count', String(count));
  mount.element.setAttribute('data-revealed-all', count === mount.chain.steps.length ? 'true' : 'false');
  mount.collapseBtn.hidden = false;
  return { status: 'REVEALED', chainId: mount.chainId, stepId: stepId };
}
function revealAll(doc, mount) {
  for (var i = 0; i < mount.chain.steps.length; i += 1) reveal(doc, mount, mount.chain.steps[i].step_id);
  mount.element.setAttribute('data-revealed-all', 'true');
  mount.element.setAttribute('data-revealed-count', String(mount.chain.steps.length));
  mount.confirm.hidden = true;
  mount.collapseBtn.hidden = false;
  focus(doc, mount.collapseBtn);
  return { status: 'REVEALED_ALL', chainId: mount.chainId, count: mount.chain.steps.length };
}
function collapse(doc, mount) {
  var host = mount.host, chainId = mount.chainId, key = mount.key;
  delete state.mounts[mount.id];
  var result = mountChain(doc, host, chainId, key);
  var next = state.mounts[result.mountId];
  if (next) focus(doc, next.title);
  return { status: 'COLLAPSED', chainId: chainId, mountId: result.mountId };
}
function openFromLink(payload, doc) {
  payload = payload || {};
  doc = doc || root.document;
  var chain = get(payload.chainId);
  if (!root.SimConceptDrawer || typeof root.SimConceptDrawer.openFromLink !== 'function') throw fail('E_CHAIN_DRAWER', 'Konceptu atvilktne nav ielādēta.');
  root.SimConceptDrawer.openFromLink({ conceptId: chain.outcome_ids[0], source: payload.source || 'chain-link',
    quiet: Boolean(payload.quiet), returnContext: payload.returnContext || null }, doc);
  var m = mounted(payload.chainId);
  if (m) focus(doc, m.title);
}
function errorBox(doc, error) {
  var n = doc && doc.getElementById ? doc.getElementById('sim-chains-error') : null;
  if (n) { n.textContent = 'Darba piemēru kļūda (' + (error.code || 'E_CHAINS_ERROR') + '): ' + (error.message || error); n.hidden = false; }
}
function init(doc) {
  doc = doc || root.document;
  state.island = null; state.mounts = Object.create(null); state.byId = Object.create(null);
  try {
    var island = load(doc);
    var host = doc.getElementById ? doc.getElementById('chain-index') : null;
    if (host) {
      clear(host);
      for (var i = 0; i < island.chains.length; i += 1) {
        var slot = E(doc, 'div', 'chain-index-slot');
        host.appendChild(slot);
        mountChain(doc, slot, island.chains[i].id, 'index');
      }
    }
    return island;
  } catch (error) {
    errorBox(doc, error);
    return null;
  }
}
function mounted(chainId) {
  for (var id in state.mounts) if (state.mounts[id].chainId === chainId) return state.mounts[id];
  return null;
}
root.SimChains = {
  ISLAND_ID: ID, load: load, init: init, mountChain: mountChain,
  revealStep: function (chainId, stepId, doc) { var m = mounted(chainId); if (!m) throw fail('E_CHAIN_MOUNT', 'Ķēde nav montēta.'); return reveal(doc || root.document, m, stepId); },
  revealAll: function (chainId, doc) { var m = mounted(chainId); if (!m) throw fail('E_CHAIN_MOUNT', 'Ķēde nav montēta.'); return revealAll(doc || root.document, m); },
  collapse: function (chainId, doc) { var m = mounted(chainId); if (!m) throw fail('E_CHAIN_MOUNT', 'Ķēde nav montēta.'); return collapse(doc || root.document, m); },
  openFromLink: openFromLink, getState: function () {
    var out = [];
    for (var id in state.mounts) out.push({ mountId: id, chainId: state.mounts[id].chainId, mountKey: state.mounts[id].key,
      revealed: Object.keys(state.mounts[id].revealed).sort(), revealedCount: Object.keys(state.mounts[id].revealed).length });
    return out.sort(function (a, b) { return a.mountId < b.mountId ? -1 : 1; });
  },
  sha256: function (text) { return root.SimFigures.sha256Utf8(text); }, renderError: errorBox
};
if (typeof module !== 'undefined' && module.exports) module.exports = root.SimChains;
})(typeof globalThis !== 'undefined' ? globalThis : this);
