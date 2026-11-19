/* N19 method card view.
 *
 * Renders the authored method cards with the same collapse-and-reveal
 * discipline as the worked chains: the step statements are public teaching
 * content, the reasoning, the misconception note, the safety entry and the
 * grading rules stay sealed until the learner asks for them.
 *
 * The module is intentionally NOT inlined into output/simulator.html: the
 * Section 1.3 runtime-JS ceiling has 83 bytes of headroom (the N17 and N18
 * precedent). It is verified from src/ against the shipped islands by
 * tools/check_n19_runtime.js; N31 must lazy-load or re-budget before
 * inlining it. See evidence/N19_VERIFICATION_RECORD.md.
 */
(function (root) {
'use strict';

var CARDS_ID = 'sim-method-cards';
var TERMS_ID = 'sim-terms';
var state = { mounts: {}, bound: false, trace: [] };

function CardError(code, message, detail) {
  var error = new Error(message);
  error.name = 'SimMethodCardError';
  error.code = code;
  error.detail = detail || {};
  return error;
}

function readIsland(doc, id) {
  var node = doc && typeof doc.getElementById === 'function' ? doc.getElementById(id) : null;
  if (!node) { throw CardError('E_METHOD_CARD_ISLAND', 'Island #' + id + ' was not found.', { island: id }); }
  var raw = node.textContent !== undefined ? node.textContent : node.innerText;
  if (typeof raw !== 'string' || !raw.trim()) {
    throw CardError('E_METHOD_CARD_ISLAND_EMPTY', 'Island #' + id + ' is empty.', { island: id });
  }
  try { return JSON.parse(raw); } catch (error) {
    throw CardError('E_METHOD_CARD_ISLAND_JSON', 'Island #' + id + ' holds broken JSON.', { island: id });
  }
}

function bytesOf(hex) {
  var out = [];
  for (var i = 0; i < hex.length; i += 2) { out.push(parseInt(hex.substr(i, 2), 16)); }
  return out;
}

function unseal(blob) {
  if (!blob || blob.alg !== 'xor-v1') {
    throw CardError('E_METHOD_CARD_ALG', 'Unknown method card payload algorithm.', {});
  }
  var raw = root.atob(blob.data);
  var key = bytesOf(blob.key || '');
  var out = [];
  for (var i = 0; i < raw.length; i += 1) { out.push(raw.charCodeAt(i) ^ key[i % key.length]); }
  var text = '';
  for (var j = 0; j < out.length; j += 1) { text += String.fromCharCode(out[j]); }
  try {
    return JSON.parse(decodeURIComponent(escape(text)));
  } catch (error) {
    throw CardError('E_METHOD_CARD_JSON', 'Invalid method card payload JSON.', {
      cause: String(error && error.message ? error.message : error)
    });
  }
}

function load(doc) {
  var island = readIsland(doc, CARDS_ID);
  var terms = readIsland(doc, TERMS_ID);
  if (island.island_id !== CARDS_ID) {
    throw CardError('E_METHOD_CARD_ISLAND_ID', 'Island id mismatch for #' + CARDS_ID + '.', {});
  }
  var byId = {};
  var byOutcome = {};
  var list = island.cards || [];
  for (var i = 0; i < list.length; i += 1) {
    var card = list[i];
    byId[card.card_id] = card;
    var outcomes = card.outcome_ids || [];
    for (var o = 0; o < outcomes.length; o += 1) {
      if (!byOutcome[outcomes[o]]) { byOutcome[outcomes[o]] = []; }
      byOutcome[outcomes[o]].push(card);
    }
  }
  var termsByKey = {};
  var termList = terms.terms || [];
  for (var t = 0; t < termList.length; t += 1) { termsByKey[termList[t].key] = termList[t]; }
  return { island: island, cardsById: byId, cardsByOutcome: byOutcome, termsByKey: termsByKey };
}

function makeElement(doc, tag, className, text) {
  var el = doc.createElement(tag);
  if (className) { el.className = className; }
  if (text !== undefined && text !== null) { el.textContent = text; }
  return el;
}

function focusElement(doc, element) {
  if (!element || typeof element.focus !== 'function') { return false; }
  try { element.focus(); } catch (error) { return false; }
  return true;
}

/* Mount one card into a host element. The card opens collapsed: the step
 * statements are visible, the notes are not. */
function mountCard(doc, host, cardId, trigger, loaded) {
  if (!loaded) { loaded = load(doc); }
  var card = loaded.cardsById[cardId];
  if (!card) { throw CardError('E_METHOD_CARD_UNKNOWN', 'Method card ' + cardId + ' is unknown.', { card_id: cardId }); }
  if (!host) { throw CardError('E_METHOD_CARD_HOST', 'The method card needs a host element.', {}); }
  while (host.firstChild) { host.removeChild(host.firstChild); }

  var mountId = 'method-card-' + cardId + '-' + String(Object.keys(state.mounts).length + 1);
  var article = makeElement(doc, 'article', 'method-card');
  article.id = mountId;
  article.setAttribute('data-card-id', cardId);
  article.setAttribute('data-card-topic', String(card.topic));
  article.setAttribute('data-chain-id', card.chain_id || '');
  article.setAttribute('data-revealed-count', '0');

  article.appendChild(makeElement(doc, 'p', 'method-card-banner', card.banner_lv));
  var heading = makeElement(doc, 'h3', 'method-card-title', card.title_lv);
  heading.setAttribute('tabindex', '-1');
  article.appendChild(heading);
  article.appendChild(makeElement(doc, 'p', 'method-card-subtitle', card.subtitle_lv));
  var citation = card.master_citation || {};
  article.appendChild(makeElement(doc, 'p', 'method-card-citation',
    (citation.heading_lv || '') + ' ' + (citation.anchor || '')));
  article.appendChild(makeElement(doc, 'p', 'method-card-order-citation', card.order_citation_lv));

  var list = makeElement(doc, 'ol', 'method-card-steps');
  list.setAttribute('data-card-id', cardId);
  var steps = card.steps || [];
  var revealed = {};
  for (var i = 0; i < steps.length; i += 1) {
    var step = steps[i];
    var item = makeElement(doc, 'li', 'method-card-step');
    item.setAttribute('data-step-id', step.step_id);
    if (step.critical) { item.setAttribute('data-critical', 'true'); }
    item.appendChild(makeElement(doc, 'p', 'method-card-step-statement', step.statement_lv));
    var note = makeElement(doc, 'div', 'method-card-step-note');
    note.id = mountId + '-note-' + step.step_id;
    note.hidden = true;
    item.appendChild(note);
    var button = makeElement(doc, 'button', 'btn btn-secondary method-card-reveal', 'Atklāt soļa pamatojumu');
    button.type = 'button';
    button.id = mountId + '-reveal-' + step.step_id;
    button.setAttribute('data-step-id', step.step_id);
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-controls', note.id);
    item.appendChild(button);
    list.appendChild(item);
  }
  article.appendChild(list);

  var mount = {
    id: mountId, cardId: cardId, card: card, host: host, element: article,
    revealed: revealed, trigger: trigger || null, loaded: loaded,
    heading: heading
  };
  state.mounts[mountId] = mount;
  bindReveal(doc, mount);
  host.appendChild(article);
  focusElement(doc, heading);
  state.trace.push({ action: 'mount-card', card_id: cardId, mount_id: mountId, trigger: trigger || null });
  return mount;
}

/* Mount every card that belongs to one coverage outcome (the map slot). */
function mountOutcomeSlot(doc, host, outcomeId, trigger, loaded) {
  if (!loaded) { loaded = load(doc); }
  var cards = loaded.cardsByOutcome[outcomeId] || [];
  var mounts = [];
  for (var i = 0; i < cards.length; i += 1) {
    var slotHost = makeElement(doc, 'div', 'method-card-slot');
    host.appendChild(slotHost);
    mounts.push(mountCard(doc, slotHost, cards[i].card_id, trigger, loaded));
  }
  return mounts;
}

function bindReveal(doc, mount) {
  var buttons = mount.element.querySelectorAll('.method-card-reveal');
  for (var i = 0; i < buttons.length; i += 1) {
    bindRevealButton(doc, mount, buttons[i]);
  }
}

function bindRevealButton(doc, mount, button) {
  button.addEventListener('click', function () {
    revealStep(doc, mount.id, button.getAttribute('data-step-id'));
    focusElement(doc, button);
  });
}

function findStep(card, stepId) {
  var steps = card.steps || [];
  for (var i = 0; i < steps.length; i += 1) {
    if (steps[i].step_id === stepId) { return steps[i]; }
  }
  return null;
}

/* Reveal one step: the reasoning, the misconception note and the safety entry.
 * The revealed text is returned so the caller (N23's remediation path) can
 * reuse it without re-reading the DOM. */
function revealStep(doc, mountId, stepId) {
  var mount = state.mounts[mountId];
  if (!mount) { throw CardError('E_METHOD_CARD_MOUNT', 'Method card mount ' + mountId + ' is unknown.', {}); }
  var step = findStep(mount.card, stepId);
  if (!step) { throw CardError('E_METHOD_CARD_STEP', 'Step ' + stepId + ' is unknown in ' + mount.cardId + '.', {}); }
  var payload = unseal(step.sealed);
  var note = doc.getElementById(mount.id + '-note-' + stepId);
  if (note) {
    while (note.firstChild) { note.removeChild(note.firstChild); }
    if (payload.reasoning_lv) {
      note.appendChild(makeElement(doc, 'p', 'method-card-reasoning', payload.reasoning_lv));
    }
    if (payload.misconception_note_lv) {
      note.appendChild(makeElement(doc, 'p', 'method-card-misconception', payload.misconception_note_lv));
    }
    if (payload.safety && payload.safety.entry_lv) {
      note.appendChild(makeElement(doc, 'p', 'method-card-safety', payload.safety.entry_lv));
    }
    note.hidden = false;
  }
  var button = doc.getElementById(mount.id + '-reveal-' + stepId);
  if (button) {
    button.setAttribute('aria-expanded', 'true');
    button.textContent = 'Pamatojums atklāts';
  }
  mount.revealed[stepId] = payload;
  mount.element.setAttribute('data-revealed-count', String(Object.keys(mount.revealed).length));
  state.trace.push({ action: 'reveal-step', card_id: mount.cardId, step_id: stepId });
  return payload;
}

/* The remediation path of N28: a wrong ordering verdict names the step, and
 * the step's note is the text the learner is sent to. */
function stepNote(card, stepId, loaded) {
  var source = loaded ? loaded.cardsById[card] : null;
  if (!source) { return null; }
  var step = findStep(source, stepId);
  if (!step) { return null; }
  var payload = unseal(step.sealed);
  return {
    card_id: source.card_id,
    step_id: stepId,
    note_lv: payload.misconception_note_lv || '',
    reasoning_lv: payload.reasoning_lv || '',
    misconception_signature: payload.misconception_signature || null,
    feedback_key: payload.feedback_key || null
  };
}

function cardRules(card, loaded) {
  var source = loaded ? loaded.cardsById[card] : null;
  if (!source) { return null; }
  return unseal(source.sealed_rules);
}

function trace() { return state.trace.slice(); }

function reset() { state = { mounts: {}, bound: false, trace: [] }; }

/* Unseal one card: the statements stay as they are, the diagnostics and the
 * grading rules come back. A runtime consumer calls this when it needs the
 * card's signature, note or rules — for display or for grading. */
function unsealCard(card) {
  var out = {};
  var keys = Object.keys(card);
  for (var k = 0; k < keys.length; k += 1) { out[keys[k]] = card[keys[k]]; }
  var steps = [];
  var list = card.steps || [];
  for (var i = 0; i < list.length; i += 1) {
    var payload = unseal(list[i].sealed);
    steps.push({
      step_id: list[i].step_id,
      statement_lv: list[i].statement_lv,
      critical: Boolean(list[i].critical),
      misconception_signature: payload.misconception_signature || null,
      misconception_note_lv: payload.misconception_note_lv || '',
      feedback_key: payload.feedback_key || null,
      reasoning_lv: payload.reasoning_lv || '',
      safety: payload.safety || null,
      quantity_links: payload.quantity_links || null
    });
  }
  var rules = unseal(card.sealed_rules);
  out.steps = steps;
  out.free_order_groups = rules.free_order_groups || [];
  out.sequence_prompts = rules.sequence_prompts || [];
  out.matching = rules.matching || null;
  return out;
}

function unsealCards(cardsById) {
  var out = {};
  var keys = Object.keys(cardsById);
  for (var i = 0; i < keys.length; i += 1) { out[keys[i]] = unsealCard(cardsById[keys[i]]); }
  return out;
}

root.SimMethodCards = {
  load: load,
  mountCard: mountCard,
  mountOutcomeSlot: mountOutcomeSlot,
  revealStep: revealStep,
  stepNote: stepNote,
  cardRules: cardRules,
  unseal: unseal,
  unsealCard: unsealCard,
  unsealCards: unsealCards,
  trace: trace,
  reset: reset,
  CardError: CardError
};
}(typeof globalThis !== 'undefined' ? globalThis : this));
