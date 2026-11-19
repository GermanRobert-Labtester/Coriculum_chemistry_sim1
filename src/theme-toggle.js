/* N06 theme toggle and in-memory store stub:
 *
 * Honors the masters' id="theme-toggle" convention, keyboard operation
 * (native <button> Enter/Space + explicit keydown support for Space/Enter on
 * custom test nodes), and AGENTS.md's in-memory-by-default session rule.
 * Persistent localStorage opt-in is deferred to N25; when an opted-in storage
 * adapter is supplied, theme state persists and restores cleanly, and when
 * storage is absent or throws, it degrades gracefully to in-memory mode.
 */
(function (root) {
  'use strict';

  var STORAGE_KEY = 'sim_theme_v1';
  var VALID_THEMES = { light: true, dark: true };

  function createMemoryStore() {
    var data = Object.create(null);
    return {
      mode: 'memory',
      persistent: false,
      getItem: function (key) {
        return Object.prototype.hasOwnProperty.call(data, key) ? data[key] : null;
      },
      setItem: function (key, value) {
        data[key] = String(value);
      },
      removeItem: function (key) {
        delete data[key];
      }
    };
  }

  function createStore(options) {
    options = options || {};
    var memory = createMemoryStore();
    var optIn = Boolean(options.optIn);
    var backing = optIn ? options.storage : null;
    var degraded = false;
    var reason = optIn ? 'opt-in-active' : 'default-in-memory-AGENTS-md';

    if (optIn && (!backing || typeof backing.getItem !== 'function' || typeof backing.setItem !== 'function')) {
      degraded = true;
      reason = 'no-persistent-store-degraded-to-memory';
      backing = null;
    }

    return {
      mode: backing ? 'persistent' : 'memory',
      optIn: optIn,
      degraded: degraded,
      reason: reason,
      get: function (key) {
        if (backing) {
          try {
            var val = backing.getItem(key);
            if (val !== null && val !== undefined) {
              return String(val);
            }
          } catch (_err) {
            this.mode = 'memory';
            this.degraded = true;
            this.reason = 'store-read-error-degraded-to-memory';
          }
        }
        return memory.getItem(key);
      },
      set: function (key, value) {
        memory.setItem(key, value);
        if (backing) {
          try {
            backing.setItem(key, String(value));
            return true;
          } catch (_err) {
            this.mode = 'memory';
            this.degraded = true;
            this.reason = 'store-write-error-degraded-to-memory';
            return false;
          }
        }
        return false;
      }
    };
  }

  function detectDefaultTheme(win) {
    if (win && typeof win.matchMedia === 'function') {
      try {
        if (win.matchMedia('(prefers-color-scheme: dark)').matches) {
          return 'dark';
        }
      } catch (_err) {
        return 'light';
      }
    }
    return 'light';
  }

  function term(key, fallback) {
    if (root.SimTerms && typeof root.SimTerms.getDefault === 'function' && root.SimTerms.getDefault()) {
      return root.SimTerms.lookup(key);
    }
    return fallback;
  }

  function normalizeTheme(value) {
    return VALID_THEMES[value] ? value : null;
  }

  function applyTheme(doc, theme) {
    var next = normalizeTheme(theme) || 'light';
    if (doc && doc.documentElement && typeof doc.documentElement.setAttribute === 'function') {
      doc.documentElement.setAttribute('data-theme', next);
    }
    var btn = doc && doc.getElementById ? doc.getElementById('theme-toggle') : null;
    var isDark = next === 'dark';
    if (btn) {
      btn.textContent = isDark ? term('settings.theme.to_light', 'Gaišais režīms') : term('settings.theme.to_dark', 'Tumšais režīms');
      if (typeof btn.setAttribute === 'function') {
        btn.setAttribute('aria-pressed', isDark ? 'true' : 'false');
        btn.setAttribute('aria-label', isDark ? term('settings.theme.aria_to_light', 'Pārslēgt uz gaišo krāsu shēmu') : term('settings.theme.aria_to_dark', 'Pārslēgt uz tumšo krāsu shēmu'));
      }
    }
    var status = doc && doc.getElementById ? doc.getElementById('theme-status') : null;
    if (status) {
      status.textContent = 'Pašreizējā krāsu shēma: ' + (isDark ? 'tumšā' : 'gaišā') + '.';
    }
    return next;
  }

  function init(doc, options) {
    doc = doc || root.document;
    options = options || {};
    var store = options.store || createStore(options);
    var saved = normalizeTheme(store.get(STORAGE_KEY));
    var current = saved || normalizeTheme(options.initialTheme) || detectDefaultTheme(root);
    current = applyTheme(doc, current);

    function setTheme(theme) {
      current = applyTheme(doc, theme);
      store.set(STORAGE_KEY, current);
      return current;
    }

    function toggle() {
      return setTheme(current === 'dark' ? 'light' : 'dark');
    }

    var btn = doc && doc.getElementById ? doc.getElementById('theme-toggle') : null;
    if (btn && typeof btn.addEventListener === 'function') {
      btn.addEventListener('click', function () {
        toggle();
      });
      btn.addEventListener('keydown', function (event) {
        var key = event && event.key;
        if (key === ' ' || key === 'Spacebar') {
          if (typeof event.preventDefault === 'function') {
            event.preventDefault();
          }
          toggle();
        } else if (key === 'Enter' && String(btn.tagName || '').toUpperCase() !== 'BUTTON') {
          toggle();
        }
      });
    }

    return {
      STORAGE_KEY: STORAGE_KEY,
      store: store,
      getTheme: function () { return current; },
      setTheme: setTheme,
      toggle: toggle,
      destroy: function () {}
    };
  }

  root.SimTheme = {
    STORAGE_KEY: STORAGE_KEY,
    createMemoryStore: createMemoryStore,
    createStore: createStore,
    applyTheme: applyTheme,
    init: init
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = root.SimTheme;
  }
})(typeof globalThis !== 'undefined' ? globalThis : this);
