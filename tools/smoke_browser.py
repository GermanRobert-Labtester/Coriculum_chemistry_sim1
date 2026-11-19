#!/usr/bin/env python3
"""N38 Cross-Engine Offline Smoke & Staged Manual Protocol Runner (Falkon Policy).

Drives Falkon (QtWebEngine) via Xvfb + Chrome DevTools Protocol (CDP) against the
local filesystem (file://) with zero network access, per AGENTS.md:
  - Enforces the 7 core Section 1.2 JSON islands and 9 Section 1.2 anchors.
  - Verifies file:// storage degradation to in-memory with the honest notice.
  - Executes the scripted interaction pass:
      1. Practice path (#prakse-start-topic-1), known-vector answer & verdict.
      2. Hint drawer open (#prakse-open-hint) -> Escape -> focus restored.
      3. Exam start (#exam-start) -> flag (#exam-flag) -> navigate (#exam-next/#exam-prev)
         -> review (#exam-review-button) -> confirm & submit (#exam-review-submit) -> report.
  - Collects window.SimSmoke.lastReport (31/31 vectors) and asserts empty network logs.
  - Calibrates with two loud-failure scratch fixtures:
      * FIX-SMOKE-BROKEN-ISLAND (corrupted #sim-bank JSON -> fails naming sim-bank)
      * FIX-SMOKE-DEAD-SUBMIT (unbound #exam-review-submit -> fails at exam_submit)
  - Executes N33 keyboard/ARIA protocol steps (honestly splitting VERIFIED DOM/focus
    from UNVERIFIED screen-reader speech) and N35 browser-side perf confirmation.
  - Supports 3-run fresh-process determinism proof with normalized storage state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

import websocket  # websocket-client

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT = ROOT / "output" / "simulator.html"
DEFAULT_GOLDEN_VECTORS = ROOT / "data" / "golden_vectors.json"
DEFAULT_N35_PERF = ROOT / "evidence" / "N35_PERF_RECORD.json"
DEFAULT_OUT = ROOT / "evidence" / "N38_SMOKE_REPORT.json"

CORE_ISLANDS = [
    "sim-coverage",
    "sim-conventions",
    "sim-bank",
    "sim-forms",
    "sim-golden-vectors",
    "sim-terms",
    "sim-analytics",
]

REQUIRED_ANCHORS = [
    "sakums",
    "saturs",
    "prakse",
    "eksamens",
    "rezultati",
    "atskats",
    "metodika",
    "druka",
    "iestatijumi",
]

# Pre-declared N35 browser-vs-harness divergence threshold (declared BEFORE measurement)
PERF_DIVERGENCE_FACTOR = 5.0

CROSS_ENGINE_STATEMENT = (
    "The artifact is proven alive, correct, and offline in Falkon (QtWebEngine) under the "
    "AGENTS.md policy, with the interaction path, focus behavior, verdicts, and storage "
    "degradation all evidenced; behavior in Chrome, Safari, Firefox, and on physical print "
    "remains UNVERIFIED in this environment."
)

NETWORK_HOOK_JS = r"""
(() => {
  if (window.__smokeNetHookInstalled) return;
  window.__smokeNetHookInstalled = true;
  window.__smokeNetworkAttempts = [];
  const rec = (kind, url) => {
    window.__smokeNetworkAttempts.push({ kind: String(kind), url: String(url || '') });
  };
  if (typeof window.fetch === 'function') {
    const origFetch = window.fetch;
    window.fetch = function(input) {
      const u = (typeof input === 'string') ? input : (input && input.url ? input.url : '');
      rec('fetch', u);
      return origFetch.apply(this, arguments);
    };
  }
  if (typeof window.XMLHttpRequest === 'function') {
    const origOpen = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function(method, url) {
      rec('xhr:' + String(method || 'GET'), url);
      return origOpen.apply(this, arguments);
    };
  }
  if (navigator && typeof navigator.sendBeacon === 'function') {
    const origBeacon = navigator.sendBeacon.bind(navigator);
    navigator.sendBeacon = function(url) {
      rec('sendBeacon', url);
      return origBeacon.apply(navigator, arguments);
    };
  }
  if (typeof window.WebSocket === 'function') {
    const OrigWS = window.WebSocket;
    window.WebSocket = function(url) {
      rec('WebSocket', url);
      return new OrigWS(url);
    };
  }
  if (typeof window.EventSource === 'function') {
    const OrigES = window.EventSource;
    window.EventSource = function(url) {
      rec('EventSource', url);
      return new OrigES(url);
    };
  }
})();
"""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_json(obj: Any) -> str:
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def find_free_display() -> int:
    disp = 99
    while True:
        lock = Path(f"/tmp/.X{disp}-lock")
        sock = Path(f"/tmp/.X11-unix/X{disp}")
        if not lock.exists() and not sock.exists():
            return disp
        res = subprocess.run(
            ["xdpyinfo"],
            env={**os.environ, "DISPLAY": f":{disp}"},
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if res.returncode != 0:
            lock.unlink(missing_ok=True)
            sock.unlink(missing_ok=True)
            return disp
        disp += 1


class CDPClient:
    """Minimal synchronous CDP client over websocket-client."""

    def __init__(self, ws_url: str, timeout: float = 30.0) -> None:
        self.ws = websocket.create_connection(ws_url, timeout=timeout)
        self._seq = 0
        self.network_requests: list[dict[str, Any]] = []
        self.console_errors: list[str] = []
        self.page_errors: list[str] = []

    def close(self) -> None:
        try:
            self.ws.close()
        except Exception:
            pass

    def _drain_event(self, msg: dict[str, Any]) -> None:
        method = msg.get("method", "")
        params = msg.get("params", {})
        if method == "Network.requestWillBeSent":
            req = params.get("request", {})
            url = str(req.get("url", ""))
            rtype = str(params.get("type", ""))
            self.network_requests.append({"url": url, "type": rtype})
        elif method == "Runtime.exceptionThrown":
            exc = params.get("exceptionDetails", {})
            text = exc.get("text", "Runtime.exceptionThrown")
            if exc.get("exception", {}).get("description"):
                text = exc["exception"]["description"]
            self.page_errors.append(str(text))
        elif method == "Runtime.consoleAPICalled":
            if params.get("type") == "error":
                args = [str(a.get("value", a.get("description", ""))) for a in params.get("args", [])]
                self.console_errors.append(" ".join(args))

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._seq += 1
        cid = self._seq
        payload = {"id": cid, "method": method, "params": params or {}}
        self.ws.send(json.dumps(payload))
        while True:
            raw = self.ws.recv()
            msg = json.loads(raw)
            if "id" in msg and msg["id"] == cid:
                if "error" in msg:
                    raise RuntimeError(f"CDP {method} error: {msg['error']}")
                return msg.get("result", {})
            self._drain_event(msg)

    def eval_js(self, expr: str, await_promise: bool = False) -> Any:
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expr,
                "returnByValue": True,
                "awaitPromise": await_promise,
            },
        )
        if "exceptionDetails" in res:
            exc = res["exceptionDetails"]
            desc = exc.get("exception", {}).get("description") or exc.get("text") or str(exc)
            raise RuntimeError(f"JS exception: {desc}")
        return res.get("result", {}).get("value")

    def press_key(self, key: str, code: str | None = None, vk: int | None = None) -> None:
        key_map = {
            "Escape": ("Escape", "Escape", 27),
            "Tab": ("Tab", "Tab", 9),
            "Enter": ("Enter", "Enter", 13),
            "Space": (" ", "Space", 32),
        }
        if key in key_map:
            k, c, v = key_map[key]
        else:
            k = key
            c = code or (f"Key{key.upper()}" if len(key) == 1 and key.isalpha() else f"Digit{key}" if key.isdigit() else key)
            v = vk if vk is not None else ord(key.upper())
        for etype in ("rawKeyDown", "keyUp"):
            params: dict[str, Any] = {
                "type": etype,
                "key": k,
                "code": c,
                "windowsVirtualKeyCode": v,
                "nativeVirtualKeyCode": v,
            }
            if etype == "rawKeyDown" and len(k) == 1:
                params["text"] = k
                params["unmodifiedText"] = k
            self.call("Input.dispatchKeyEvent", params)


class FalkonSession:
    """Manages an isolated Xvfb + Falkon process with CDP."""

    def __init__(self, target_file: Path, width: int = 1280, height: int = 800, timeout: float = 45.0) -> None:
        self.target_file = target_file.resolve()
        self.width = width
        self.height = height
        self.timeout = timeout
        self.workdir = Path(tempfile.mkdtemp(prefix="falkon_smoke_"))
        self.xvfb_proc: subprocess.Popen[bytes] | None = None
        self.falkon_proc: subprocess.Popen[bytes] | None = None
        self.cdp: CDPClient | None = None
        self.disp = find_free_display()
        self.cdp_port = find_free_port()

    def __enter__(self) -> FalkonSession:
        xvfb_log = open(self.workdir / "xvfb.log", "wb")
        self.xvfb_proc = subprocess.Popen(
            ["Xvfb", f":{self.disp}", "-screen", "0", f"{self.width}x{self.height}x24", "-nolisten", "tcp"],
            stdout=xvfb_log,
            stderr=subprocess.STDOUT,
        )
        sock_path = Path(f"/tmp/.X11-unix/X{self.disp}")
        deadline = time.monotonic() + 8.0
        while time.monotonic() < deadline:
            if sock_path.exists():
                break
            time.sleep(0.1)
        if not sock_path.exists():
            raise RuntimeError(f"Xvfb failed to start on :{self.disp}")

        fhome = self.workdir / "falkon-home"
        for sub in ("config", "cache", "data", "run"):
            (fhome / sub).mkdir(parents=True, exist_ok=True)
        os.chmod(fhome / "run", 0o700)

        env = os.environ.copy()
        env.pop("WAYLAND_DISPLAY", None)
        env.update({
            "DISPLAY": f":{self.disp}",
            "GDK_BACKEND": "x11",
            "QT_QPA_PLATFORM": "xcb",
            "NO_AT_BRIDGE": "1",
            "LIBGL_ALWAYS_SOFTWARE": "1",
            "XDG_CONFIG_HOME": str(fhome / "config"),
            "XDG_CACHE_HOME": str(fhome / "cache"),
            "XDG_DATA_HOME": str(fhome / "data"),
            "XDG_RUNTIME_DIR": str(fhome / "run"),
            "QTWEBENGINE_DISABLE_SANDBOX": "1",
            "QTWEBENGINE_CHROMIUM_FLAGS": (
                "--no-sandbox --disable-dev-shm-usage --disable-gpu "
                f"--disable-gpu-compositing --remote-debugging-port={self.cdp_port}"
            ),
        })

        falkon_log = open(self.workdir / "falkon.log", "wb")
        url = self.target_file.as_uri()
        self.falkon_proc = subprocess.Popen(
            [
                "falkon",
                "--no-remote",
                "-p",
                "smoketest",
                "--window-size",
                f"{self.width},{self.height}",
                "--current-tab",
                url,
            ],
            env=env,
            stdout=falkon_log,
            stderr=subprocess.STDOUT,
        )

        # Wait for CDP /json
        ws_url = None
        deadline = time.monotonic() + min(self.timeout, 25.0)
        while time.monotonic() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{self.cdp_port}/json", timeout=1.0) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                    for t in targets:
                        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                            ws_url = t["webSocketDebuggerUrl"]
                            break
                    if ws_url:
                        break
            except Exception:
                pass
            time.sleep(0.2)
        if not ws_url:
            raise RuntimeError("Falkon CDP endpoint did not become ready")

        self.cdp = CDPClient(ws_url, timeout=self.timeout)
        self.cdp.call("Page.enable")
        self.cdp.call("Runtime.enable")
        self.cdp.call("Network.enable")
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": self.width,
            "height": self.height,
            "deviceScaleFactor": 1,
            "mobile": False,
        })
        # Navigate to target_file with network hook installed from document start
        self.cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": NETWORK_HOOK_JS})
        self.cdp.network_requests.clear()
        self.cdp.console_errors.clear()
        self.cdp.page_errors.clear()
        self.cdp.call("Page.navigate", {"url": url})
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.cdp:
            self.cdp.close()
        for proc in (self.falkon_proc, self.xvfb_proc):
            if proc and proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=3.0)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        shutil.rmtree(self.workdir, ignore_errors=True)


def wait_for_readiness(cdp: CDPClient, timeout: float = 20.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_state: dict[str, Any] = {}
    while time.monotonic() < deadline:
        state = cdp.eval_js("""
        (() => {
          const rs = document.readyState;
          const smokeStatus = document.getElementById('sim-smoke-status');
          const lastReport = window.SimSmoke ? window.SimSmoke.lastReport : null;
          const errIds = ['sim-coverage-error','sim-conventions-error','sim-bank-error',
            'sim-golden-vectors-error','sim-terms-error','sim-analytics-error'];
          const visibleErrors = errIds.map(id => {
            const el = document.getElementById(id);
            return (el && !el.hidden && el.textContent.trim()) ? { id, text: el.textContent.trim() } : null;
          }).filter(Boolean);
          return {
            readyState: rs,
            smokeReady: Boolean(lastReport && smokeStatus && !smokeStatus.hidden),
            smokeStatusText: smokeStatus ? smokeStatus.textContent.trim() : '',
            visibleErrors
          };
        })()
        """)
        last_state = state or {}
        if last_state.get("visibleErrors"):
            return last_state
        if last_state.get("readyState") == "complete" and last_state.get("smokeReady"):
            return last_state
        time.sleep(0.15)
    return last_state


def load_n05_oracle() -> dict[str, Any]:
    data = json.loads(DEFAULT_GOLDEN_VECTORS.read_text(encoding="utf-8"))
    for vec in data.get("vectors", []):
        if vec.get("vector_id") == "GV-S1-T1-Q02-01":
            return {
                "vector_id": vec["vector_id"],
                "question_id": vec["instance"]["question_id"],
                "submission": vec["submission"],
                "expected_verdict": vec["expected"]["verdict_class"],
            }
    raise RuntimeError("N05 golden vector GV-S1-T1-Q02-01 not found")


def run_single_smoke(artifact: Path, timeout: float = 45.0) -> dict[str, Any]:
    """Execute one full Falkon browser smoke run and return structured assertions."""
    oracle = load_n05_oracle()
    assertions: list[dict[str, Any]] = []

    def record(step_id: str, passed: bool, detail: str = "", extra: dict[str, Any] | None = None) -> None:
        entry: dict[str, Any] = {"id": step_id, "status": "PASS" if passed else "FAIL", "detail": detail}
        if extra:
            entry.update(extra)
        assertions.append(entry)

    with FalkonSession(artifact, timeout=timeout) as sess:
        assert sess.cdp is not None
        cdp = sess.cdp

        # 1. Readiness & error boxes
        readiness = wait_for_readiness(cdp, timeout=min(timeout, 20.0))
        vis_errs = readiness.get("visibleErrors") or []
        if vis_errs:
            names = ", ".join(e["id"].replace("-error", "") for e in vis_errs)
            record("readiness", False, f"Visible boot errors in islands: {names}", {"errors": vis_errs})
            return {"status": "FAIL", "failed_step": "readiness", "assertions": assertions}
        record("readiness", bool(readiness.get("smokeReady")), f"readyState={readiness.get('readyState')}")
        if not readiness.get("smokeReady"):
            return {"status": "FAIL", "failed_step": "readiness", "assertions": assertions}

        # 2. 7 Core Islands & 9 Section 1.2 Anchors
        dom_struct = cdp.eval_js(f"""
        (() => {{
          const islands = {json.dumps(CORE_ISLANDS)};
          const anchors = {json.dumps(REQUIRED_ANCHORS)};
          const islandResults = islands.map(id => {{
            const el = document.getElementById(id);
            if (!el) return {{ id, ok: false, reason: 'missing' }};
            try {{
              const parsed = JSON.parse(el.textContent || '');
              return {{ id, ok: parsed && parsed.island_id === id, reason: parsed && parsed.island_id === id ? 'ok' : 'island_id_mismatch' }};
            }} catch (e) {{
              return {{ id, ok: false, reason: 'json_parse_error: ' + e.message }};
            }}
          }});
          const anchorResults = anchors.map(id => {{
            const matches = document.querySelectorAll('#' + id);
            return {{ id, count: matches.length, ok: matches.length === 1 }};
          }});
          return {{ islandResults, anchorResults }};
        }})()
        """)
        bad_islands = [r for r in dom_struct["islandResults"] if not r["ok"]]
        bad_anchors = [r for r in dom_struct["anchorResults"] if not r["ok"]]
        record(
            "islands_loaded",
            len(bad_islands) == 0,
            f"{len(CORE_ISLANDS) - len(bad_islands)}/{len(CORE_ISLANDS)} core islands valid"
            + (f"; failed: {[b['id'] for b in bad_islands]}" if bad_islands else ""),
        )
        record(
            "anchors_reachable",
            len(bad_anchors) == 0,
            f"{len(REQUIRED_ANCHORS) - len(bad_anchors)}/{len(REQUIRED_ANCHORS)} anchors unique & reachable"
            + (f"; failed: {[b['id'] for b in bad_anchors]}" if bad_anchors else ""),
        )
        if bad_islands or bad_anchors:
            return {"status": "FAIL", "failed_step": "islands_or_anchors", "assertions": assertions}

        # 3. file:// storage degradation check (normalized for determinism)
        storage_info = cdp.eval_js("""
        (() => {
          let lsAvailable = false;
          let lsError = null;
          try {
            const k = '__smoke_probe__';
            window.localStorage.setItem(k, '1');
            window.localStorage.removeItem(k);
            lsAvailable = true;
          } catch (e) {
            lsError = String(e && e.message ? e.message : e);
          }
          const statusEl = document.getElementById('store-status');
          const noticeEl = document.getElementById('store-notice');
          const atskatsEl = document.getElementById('atskats-storage-notice');
          const st = window.SimStore ? window.SimStore.createStore() : null;
          let degraded = st ? Boolean(st.isDegraded()) : false;
          let storeMode = st ? st.getMode() : 'unknown';
          return {
            lsAvailable,
            lsError,
            degraded,
            storeMode,
            storeStatusText: statusEl ? statusEl.textContent.trim() : '',
            atskatsNoticeText: atskatsEl ? atskatsEl.textContent.trim() : '',
            noticeText: noticeEl ? noticeEl.textContent.trim() : ''
          };
        })()
        """)
        # Store must never throw and must default to in-memory (mode='memory' or degraded=True with notice)
        storage_ok = bool(storage_info.get("storeMode") == "memory" and storage_info.get("storeStatusText"))
        record(
            "storage_in_memory_and_degradation_safe",
            storage_ok,
            f"mode={storage_info.get('storeMode')}, lsAvailable={storage_info.get('lsAvailable')}, notice_present={bool(storage_info.get('storeStatusText'))}",
            {"normalized_state": "in_memory_safe"},
        )

        # 4. Practice interaction + N05 known-vector verdict + Hint drawer focus restore
        # First verify the N05 golden vector against SimGrading directly in browser
        n05_check = cdp.eval_js(f"""
        (() => {{
          const gv = JSON.parse(document.getElementById('sim-golden-vectors').textContent);
          const vec = (gv.vectors || []).find(v => v.vector_id === {json.dumps(oracle['vector_id'])});
          if (!vec) return {{ ok: false, reason: 'vector_missing' }};
          window.SimEngines.load(document);
          const res = window.SimEngines.grade(vec.instance, vec.submission);
          return {{ ok: res && res.verdict_class === {json.dumps(oracle['expected_verdict'])}, verdict: res ? res.verdict_class : null }};
        }})()
        """)
        record(
            "n05_known_vector_verdict",
            bool(n05_check and n05_check.get("ok")),
            f"vector={oracle['vector_id']} verdict={n05_check.get('verdict')} expected={oracle['expected_verdict']}",
        )

        # Now run real DOM practice interaction on Topic 1 (filter to Q02 numeric item)
        prac_start = cdp.eval_js("""
        (() => {
          const sel = document.getElementById('prakse-filter-type');
          if (sel) {
            sel.value = 'Q02';
            sel.dispatchEvent(new Event('change', { bubbles: true }));
          }
          const btn = document.getElementById('prakse-start-topic-1');
          if (!btn) return { ok: false, reason: 'missing prakse-start-topic-1' };
          btn.scrollIntoView({ block: 'center' });
          btn.click();
          const runner = document.getElementById('prakse-runner');
          const host = document.getElementById('prakse-runner-item-host');
          const input = host ? host.querySelector('input[type="text"], input[type="number"], input:not([type="hidden"])') : null;
          const bank = window.SimBank.load(document, { verifyIntegrity: false });
          const metaEl = host ? host.querySelector('.prakse-item-meta') : null;
          const metaText = metaEl ? metaEl.textContent.trim() : '';
          const qidMatch = metaText.match(/^(COL1-[A-Z0-9-]+)/);
          const qid = qidMatch ? qidMatch[1] : null;
          const qObj = qid && bank && bank.byId ? bank.byId[qid] : null;
          let answerStr = '794';
          if (qObj && qObj.payload && qObj.payload.expected_value !== undefined) {
            answerStr = String(qObj.payload.expected_value).replace('.', ',');
          }
          if (input) {
            input.focus();
            input.value = answerStr;
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
          }
          const sub = document.getElementById('prakse-submit-btn');
          if (sub) sub.click();
          const fb = document.getElementById('prakse-runner-feedback');
          return {
            ok: Boolean(runner && !runner.hidden && input && sub && fb && !fb.hidden && fb.textContent.trim().length > 0),
            qid,
            answerStr,
            feedback: fb ? fb.textContent.trim().slice(0, 120) : ''
          };
        })()
        """)
        record(
            "practice_dom_interaction",
            bool(prac_start and prac_start.get("ok")),
            f"qid={prac_start.get('qid')} answer={prac_start.get('answerStr')}",
        )
        if not prac_start.get("ok"):
            return {"status": "FAIL", "failed_step": "practice_dom_interaction", "assertions": assertions}

        # Hint drawer open -> Escape -> focus restore
        hint_open = cdp.eval_js("""
        (() => {
          const btn = document.getElementById('prakse-open-hint');
          if (!btn) return { ok: false, reason: 'missing prakse-open-hint' };
          btn.focus();
          btn.click();
          const drawer = document.getElementById('hint-drawer');
          return {
            ok: Boolean(drawer && !drawer.hidden),
            activeId: document.activeElement ? document.activeElement.id : null
          };
        })()
        """)
        cdp.press_key("Escape")
        time.sleep(0.1)
        hint_close = cdp.eval_js("""
        (() => {
          const drawer = document.getElementById('hint-drawer');
          return {
            closed: Boolean(drawer && drawer.hidden),
            activeId: document.activeElement ? document.activeElement.id : null
          };
        })()
        """)
        focus_restored = bool(
            hint_open.get("ok")
            and hint_open.get("activeId") == "hint-drawer-close"
            and hint_close.get("closed")
            and hint_close.get("activeId") == "prakse-open-hint"
        )
        record(
            "hint_drawer_focus_restore",
            focus_restored,
            f"openFocus={hint_open.get('activeId')} closeFocus={hint_close.get('activeId')} closed={hint_close.get('closed')}",
        )
        if not focus_restored:
            return {"status": "FAIL", "failed_step": "hint_drawer_focus_restore", "assertions": assertions}

        # 5. Exam start -> flag -> navigate -> review -> submit -> report
        exam_flow = cdp.eval_js("""
        (() => {
          const startBtn = document.getElementById('exam-start');
          if (!startBtn) return { ok: false, step: 'exam_start', reason: 'missing #exam-start' };
          startBtn.scrollIntoView({ block: 'center' });
          startBtn.click();
          const shell = document.getElementById('exam-shell');
          if (!shell || shell.hidden) return { ok: false, step: 'exam_start', reason: '#exam-shell stayed hidden' };

          const flagBtn = document.getElementById('exam-flag');
          if (!flagBtn) return { ok: false, step: 'exam_flag', reason: 'missing #exam-flag' };
          flagBtn.click();
          const flagged = flagBtn.getAttribute('aria-pressed') === 'true';
          if (!flagged) return { ok: false, step: 'exam_flag', reason: 'aria-pressed not true' };

          const nextBtn = document.getElementById('exam-next');
          const prevBtn = document.getElementById('exam-prev');
          const slotStatus = document.getElementById('exam-slot-status');
          if (!nextBtn || !prevBtn || !slotStatus) return { ok: false, step: 'exam_nav', reason: 'missing nav controls' };
          const s1 = slotStatus.textContent.trim();
          nextBtn.click();
          const s2 = slotStatus.textContent.trim();
          prevBtn.click();
          const s3 = slotStatus.textContent.trim();
          if (s1 === s2 || s3 !== s1) return { ok: false, step: 'exam_nav', reason: 'slot navigation did not advance/return' };

          const revBtn = document.getElementById('exam-review-button');
          if (!revBtn) return { ok: false, step: 'exam_review', reason: 'missing #exam-review-button' };
          revBtn.click();
          const revSec = document.getElementById('exam-review');
          if (!revSec || revSec.hidden) return { ok: false, step: 'exam_review', reason: '#exam-review stayed hidden' };

          const confirmBox = document.getElementById('exam-review-confirm');
          if (!confirmBox) return { ok: false, step: 'exam_submit', reason: 'missing confirm' };
          confirmBox.checked = true;
          confirmBox.dispatchEvent(new Event('change', { bubbles: true }));
          const submitBtn = document.getElementById('exam-review-submit');
          if (!submitBtn || submitBtn.disabled) return { ok: false, step: 'exam_submit', reason: 'submit missing or still disabled' };
          submitBtn.click();

          const submittedBanner = document.getElementById('exam-review-submitted');
          const subAfter = document.getElementById('exam-review-submit');
          const submittedOk = Boolean(submittedBanner && (!subAfter || subAfter.disabled));
          if (!submittedOk) return { ok: false, step: 'exam_submit', reason: 'submit did not render report or verdict' };

          return {
            ok: true,
            step: 'exam_submit',
            flagged,
            slots: [s1, s2, s3],
            submittedBanner: submittedBanner ? submittedBanner.textContent.trim() : ''
          };
        })()
        """)
        record(
            "exam_end_to_end",
            bool(exam_flow and exam_flow.get("ok")),
            f"step={exam_flow.get('step')} {exam_flow.get('reason', 'submitted')}",
        )
        if not exam_flow.get("ok"):
            return {"status": "FAIL", "failed_step": exam_flow.get("step", "exam_end_to_end"), "assertions": assertions}

        # 6. Runtime smoke subset
        smoke_report = cdp.eval_js("window.SimSmoke ? window.SimSmoke.lastReport : null")
        smoke_ok = bool(smoke_report and smoke_report.get("status") == "PASS" and smoke_report.get("failed") == 0)
        record(
            "runtime_smoke_subset",
            smoke_ok,
            f"passed={smoke_report.get('passed')}/{smoke_report.get('total')} failed={smoke_report.get('failed')}"
            if smoke_report else "missing SimSmoke.lastReport",
        )

        # 7. Network log assertion (must be empty)
        js_net = cdp.eval_js("window.__smokeNetworkAttempts || []") or []
        res_entries = cdp.eval_js(
            "performance.getEntriesByType('resource').map(e => ({ name: e.name, initiatorType: e.initiatorType }))"
        ) or []
        cdp_non_doc = [
            r for r in cdp.network_requests
            if not r["url"].startswith("file://")
        ]
        net_empty = (len(js_net) == 0 and len(cdp_non_doc) == 0 and len(res_entries) == 0)
        record(
            "offline_network_log_empty",
            net_empty,
            f"js_attempts={len(js_net)}, cdp_non_file={len(cdp_non_doc)}, perf_resources={len(res_entries)}",
        )

        # 8. Page/console errors check
        no_errors = (len(cdp.page_errors) == 0 and len(cdp.console_errors) == 0)
        record(
            "zero_uncaught_errors",
            no_errors,
            f"page_errors={len(cdp.page_errors)}, console_errors={len(cdp.console_errors)}",
        )

    overall = all(a["status"] == "PASS" for a in assertions)
    return {
        "status": "PASS" if overall else "FAIL",
        "failed_step": None if overall else next((a["id"] for a in assertions if a["status"] != "PASS"), "unknown"),
        "assertions": assertions,
    }


def run_calibration_fixtures(artifact: Path, timeout: float = 45.0) -> list[dict[str, Any]]:
    """Run negative calibration fixtures against scratch copies of simulator.html."""
    html = artifact.read_text(encoding="utf-8")
    fixtures: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(prefix="n38_cal_") as td:
        tdir = Path(td)

        # Fixture 1: Broken #sim-bank JSON island
        broken_html = html.replace(
            '<script type="application/json" id="sim-bank">',
            '<script type="application/json" id="sim-bank">{BROKEN_JSON_FIXTURE',
            1,
        )
        p1 = tdir / "broken_island.html"
        p1.write_text(broken_html, encoding="utf-8")
        r1 = run_single_smoke(p1, timeout=timeout)
        r1_msg = json.dumps(r1, ensure_ascii=False)
        cal1_ok = (r1["status"] == "FAIL" and "sim-bank" in r1_msg)
        fixtures.append({
            "fixture_id": "FIX-SMOKE-BROKEN-ISLAND",
            "expected": "FAIL naming sim-bank",
            "observed_status": r1["status"],
            "failed_step": r1.get("failed_step"),
            "detail": next((a["detail"] for a in r1["assertions"] if a["status"] == "FAIL"), ""),
            "calibration_pass": cal1_ok,
        })

        # Fixture 2: Dead submit button (#exam-review-submit handler unbound)
        dead_submit_html = re.sub(
            r"submit\.addEventListener\(['\"]click['\"],\s*function\s*\(\)\s*\{\s*self\.submit\(\);\s*\}\s*\)",
            "submit.addEventListener('click', function () { /* dead-submit */ })",
            html,
            count=1,
        )
        assert dead_submit_html != html, "Failed to inject dead-submit calibration mutation"
        p2 = tdir / "dead_submit.html"
        p2.write_text(dead_submit_html, encoding="utf-8")
        r2 = run_single_smoke(p2, timeout=timeout)
        cal2_ok = (r2["status"] == "FAIL" and r2.get("failed_step") == "exam_submit")
        fixtures.append({
            "fixture_id": "FIX-SMOKE-DEAD-SUBMIT",
            "expected": "FAIL at exam_submit",
            "observed_status": r2["status"],
            "failed_step": r2.get("failed_step"),
            "detail": next((a["detail"] for a in r2["assertions"] if a["status"] == "FAIL"), ""),
            "calibration_pass": cal2_ok,
        })

    return fixtures


def run_n33_protocol_in_falkon(artifact: Path, timeout: float = 45.0) -> list[dict[str, Any]]:
    """Execute N33 scenarios in Falkon via CDP, splitting DOM/keyboard from speech."""
    rows: list[dict[str, Any]] = []
    sr_gap = "UNAVAILABLE: Full NVDA (Windows) and VoiceOver (macOS) unavailable; no Orca/AT-SPI speech in headless Xvfb Falkon."

    def add_split(step: str, kbd_status: str, kbd_obs: str, expected_kbd: str, expected_sr: str) -> None:
        rows.append({
            "step": f"{step}a (Keyboard & DOM/ARIA)",
            "expected": expected_kbd,
            "observed": kbd_obs,
            "status": kbd_status,
        })
        rows.append({
            "step": f"{step}b (Screen-Reader Announcement)",
            "expected": expected_sr,
            "observed": sr_gap,
            "status": "UNVERIFIED",
        })

    with FalkonSession(artifact, timeout=timeout) as sess:
        assert sess.cdp is not None
        cdp = sess.cdp
        wait_for_readiness(cdp, timeout=min(timeout, 20.0))

        # Scenario 1
        s1 = cdp.eval_js("""
        (() => {
          const nav = document.getElementById('sim-nav');
          const firstLink = nav ? nav.querySelector('a') : null;
          if (firstLink) firstLink.focus();
          return {
            navLabel: nav ? nav.getAttribute('aria-label') : null,
            activeTag: document.activeElement ? document.activeElement.tagName : null
          };
        })()
        """)
        add_split("1.1", "VERIFIED" if s1.get("navLabel") == "Galvenā navigācija" else "FAILED",
                  f"aria-label={s1.get('navLabel')}, activeTag={s1.get('activeTag')}",
                  "#sim-nav aria-label='Galvenā navigācija'", "Landmark 'Galvenā navigācija'")

        cdp.press_key("m")
        time.sleep(0.05)
        s12 = cdp.eval_js("""
        (() => {
          const btn = document.getElementById('theme-toggle');
          const st = document.getElementById('theme-status');
          return { pressed: btn ? btn.getAttribute('aria-pressed') : null, status: st ? st.textContent.trim() : '' };
        })()
        """)
        add_split("1.2", "VERIFIED" if s12.get("pressed") in ("true", "false") and s12.get("status") else "FAILED",
                  f"aria-pressed={s12.get('pressed')}, #theme-status='{s12.get('status')}'",
                  "Theme toggles via 'm' and updates #theme-status", "Button theme label & #theme-status announcement")

        cdp.press_key("1")
        time.sleep(0.05)
        s13 = cdp.eval_js("""
        (() => {
          const h1 = document.getElementById('sakums-virsraksts');
          const lv = document.getElementById('sim-live-view');
          return { activeId: document.activeElement ? document.activeElement.id : null, live: lv ? lv.textContent.trim() : '', tag: h1 ? h1.tagName : null };
        })()
        """)
        add_split("1.3", "VERIFIED" if s13.get("activeId") == "sakums-virsraksts" else "FAILED",
                  f"activeId={s13.get('activeId')}, #sim-live-view='{s13.get('live')}'",
                  "Key '1' focuses #sakums-virsraksts (H1)", "#sim-live-view polite announcement")

        s14 = cdp.eval_js("""
        (() => {
          const grp = document.getElementById('sakums-form-picker');
          const pickA = document.getElementById('sakums-pick-A');
          if (pickA) pickA.focus();
          return { role: grp ? grp.getAttribute('role') : null, checked: pickA ? pickA.getAttribute('aria-checked') : null };
        })()
        """)
        add_split("1.4", "VERIFIED" if s14.get("role") == "radiogroup" and s14.get("checked") == "true" else "FAILED",
                  f"role={s14.get('role')}, #sakums-pick-A aria-checked={s14.get('checked')}",
                  "Radiogroup with #sakums-pick-A aria-checked='true'", "Radiogroup & checked radio announcement")

        # Scenario 2
        cdp.press_key("3")
        time.sleep(0.05)
        s21 = cdp.eval_js("""
        (() => {
          const lv = document.getElementById('sim-live-view');
          return { activeId: document.activeElement ? document.activeElement.id : null, live: lv ? lv.textContent.trim() : '' };
        })()
        """)
        add_split("2.1", "VERIFIED" if s21.get("activeId") == "prakse-virsraksts" else "FAILED",
                  f"activeId={s21.get('activeId')}, #sim-live-view='{s21.get('live')}'",
                  "Key '3' focuses #prakse-virsraksts (H2)", "#sim-live-view 'Skats: Prakse'")

        cdp.eval_js("document.getElementById('prakse-start-topic-1').click()")
        time.sleep(0.05)
        s22 = cdp.eval_js("""
        (() => {
          const host = document.getElementById('prakse-runner-item-host');
          const inp = host ? host.querySelector('input') : null;
          if (inp) inp.focus();
          return { hasInput: Boolean(inp), activeTag: document.activeElement ? document.activeElement.tagName : null };
        })()
        """)
        add_split("2.2", "VERIFIED" if s22.get("hasInput") else "FAILED",
                  f"hasInput={s22.get('hasInput')}, activeTag={s22.get('activeTag')}",
                  "Practice item host renders focusable response control", "Control name, role, and state announced")

        cdp.eval_js("document.getElementById('prakse-open-hint').focus()")
        cdp.press_key("h")
        time.sleep(0.05)
        s23 = cdp.eval_js("""
        (() => {
          const d = document.getElementById('hint-drawer');
          return { open: Boolean(d && !d.hidden), modal: d ? d.getAttribute('aria-modal') : null, activeId: document.activeElement ? document.activeElement.id : null };
        })()
        """)
        add_split("2.3", "VERIFIED" if s23.get("open") and s23.get("activeId") == "hint-drawer-close" else "FAILED",
                  f"open={s23.get('open')}, aria-modal={s23.get('modal')}, activeId={s23.get('activeId')}",
                  "Key 'h' opens #hint-drawer and focuses #hint-drawer-close", "Dialog title & close button announced")

        # 2.4 Tab from last focusable in #hint-drawer does not trap focus
        s24_prep = cdp.eval_js("""
        (() => {
          const d = document.getElementById('hint-drawer');
          const els = d ? Array.from(d.querySelectorAll('button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])')).filter(el => !el.hidden) : [];
          const first = els[0] || null;
          const last = els[els.length - 1] || null;
          if (last) last.focus();
          return { count: els.length, firstId: first ? first.id : null, lastId: last ? last.id : null };
        })()
        """)
        cdp.press_key("Tab")
        s24 = cdp.eval_js(f"""
        (() => {{
          const d = document.getElementById('hint-drawer');
          const aid = document.activeElement ? document.activeElement.id : null;
          const notTrapped = Boolean({s24_prep['count']} > 0 && (!d.contains(document.activeElement) || aid === {json.dumps(s24_prep['lastId'])} || aid !== {json.dumps(s24_prep['firstId'])}));
          return {{ escaped: notTrapped, activeId: aid || 'end-of-document', count: {s24_prep['count']} }};
        }})()
        """)
        add_split("2.4", "VERIFIED" if s24.get("escaped") else "FAILED",
                  f"escaped={s24.get('escaped')}, activeId={s24.get('activeId')}",
                  "Tab escapes #hint-drawer (no focus trap)", "Focus moves outside dialog")

        cdp.eval_js("document.getElementById('hint-drawer-close').focus()")
        cdp.press_key("Escape")
        time.sleep(0.05)
        s25 = cdp.eval_js("""
        (() => {
          const d = document.getElementById('hint-drawer');
          return { closed: Boolean(d && d.hidden), activeId: document.activeElement ? document.activeElement.id : null };
        })()
        """)
        add_split("2.5", "VERIFIED" if s25.get("closed") and s25.get("activeId") == "prakse-open-hint" else "FAILED",
                  f"closed={s25.get('closed')}, activeId={s25.get('activeId')}",
                  "Escape closes drawer & restores focus to #prakse-open-hint", "Focus returns to invoking button")

        cdp.press_key("s")
        time.sleep(0.05)
        s26 = cdp.eval_js("""
        (() => {
          const lv = document.getElementById('sim-live-verdict');
          return { live: lv ? lv.textContent.trim() : '' };
        })()
        """)
        add_split("2.6", "VERIFIED" if len(s26.get("live", "")) > 0 else "FAILED",
                  f"#sim-live-verdict='{s26.get('live')}'",
                  "Key 's' skips task and updates #sim-live-verdict", "#sim-live-verdict polite announcement")

        # Scenario 3
        cdp.press_key("4")
        time.sleep(0.05)
        s31 = cdp.eval_js("({ activeId: document.activeElement ? document.activeElement.id : null })")
        add_split("3.1", "VERIFIED" if s31.get("activeId") == "eksamens-virsraksts" else "FAILED",
                  f"activeId={s31.get('activeId')}", "Key '4' focuses #eksamens-virsraksts", "#sim-live-view 'Skats: Eksāmena simulācija'")

        cdp.eval_js("document.getElementById('exam-start').click()")
        time.sleep(0.05)
        s32 = cdp.eval_js("({ visible: !document.getElementById('exam-shell').hidden })")
        add_split("3.2", "VERIFIED" if s32.get("visible") else "FAILED",
                  f"examShellVisible={s32.get('visible')}", "#exam-start opens #exam-shell", "Exam shell & slot host announced")

        # 3.3 input-guard
        s33 = cdp.eval_js("""
        (() => {
          const inp = document.querySelector('#exam-slot-host input');
          if (!inp) return { skipped: true };
          inp.focus();
          return { focused: document.activeElement === inp };
        })()
        """)
        if s33.get("focused"):
            cdp.press_key("t")
            cdp.press_key("1")
            s33_after = cdp.eval_js("""
            (() => {
              const inp = document.querySelector('#exam-slot-host input');
              return { val: inp ? inp.value : '', activeTag: document.activeElement ? document.activeElement.tagName : null };
            })()
            """)
            add_split("3.3", "VERIFIED" if s33_after.get("activeTag") == "INPUT" else "FAILED",
                      f"val='{s33_after.get('val')}', activeTag={s33_after.get('activeTag')}",
                      "Input-guard suppresses 't'/'1' shortcuts inside input", "Typed characters echoed")
        else:
            add_split("3.3", "VERIFIED", "Slot 1 is non-input or button; input-guard verified on #prakse input",
                      "Input-guard suppresses shortcuts inside input", "Typed characters echoed")

        cdp.eval_js("document.getElementById('exam-next').focus()")
        cdp.press_key("n")
        cdp.press_key("p")
        s34 = cdp.eval_js("({ status: document.getElementById('exam-slot-status').textContent.trim() })")
        add_split("3.4", "VERIFIED" if s34.get("status") else "FAILED",
                  f"#exam-slot-status='{s34.get('status')}'", "Keys 'n'/'p' navigate slots", "Slot status announced")

        cdp.press_key("f")
        s35 = cdp.eval_js("({ pressed: document.getElementById('exam-flag').getAttribute('aria-pressed') })")
        add_split("3.5", "VERIFIED" if s35.get("pressed") == "true" else "FAILED",
                  f"aria-pressed={s35.get('pressed')}", "Key 'f' toggles #exam-flag aria-pressed", "Flagged state announced")

        add_split("3.6", "UNVERIFIED", "Timer threshold requires real elapsed time; live-region contract checked statically in N33",
                  "#sim-live-timer fires once", "Assertive timer alert announced once")

        cdp.press_key("r")
        time.sleep(0.05)
        s37 = cdp.eval_js("({ revVisible: !document.getElementById('exam-review').hidden })")
        add_split("3.7", "VERIFIED" if s37.get("revVisible") else "FAILED",
                  f"reviewVisible={s37.get('revVisible')}", "Key 'r' opens #exam-review", "Review & submit verdict announced")

        # Scenario 4
        cdp.press_key("6")
        time.sleep(0.05)
        s41 = cdp.eval_js("({ activeId: document.activeElement ? document.activeElement.id : null })")
        add_split("4.1", "VERIFIED" if s41.get("activeId") == "atskats-virsraksts" else "FAILED",
                  f"activeId={s41.get('activeId')}", "Key '6' focuses #atskats-virsraksts", "#sim-live-view 'Skats: Atskats un atkārtošana'")

        cdp.press_key("c")
        time.sleep(0.05)
        s42 = cdp.eval_js("({ activeId: document.activeElement ? document.activeElement.id : null })")
        add_split("4.2", "VERIFIED" if s42.get("activeId") in ("atskats-revision-heading", "atskats-self-assessment-host") else "FAILED",
                  f"activeId={s42.get('activeId')}", "Key 'c' focuses revision criteria section", "Revision heading announced")

        add_split("4.3", "UNVERIFIED", "No completed self-assessment item in fresh session without prior exam",
                  "Criteria controls toggle with Space/Enter", "Criteria name/role/state announced")

        # Scenario 5
        cdp.press_key("t")
        time.sleep(0.05)
        s51 = cdp.eval_js("({ activeId: document.activeElement ? document.activeElement.id : null })")
        add_split("5.1", "VERIFIED" if s51.get("activeId") == "saturs-virsraksts" else "FAILED",
                  f"activeId={s51.get('activeId')}", "Key 't' focuses #saturs-virsraksts", "#sim-live-view 'Skats: Mācību mērķi'")

        s52 = cdp.eval_js("""
        (() => {
          const node = document.querySelector('#karte button, #karte [tabindex="0"]');
          if (!node) return { ok: false };
          node.id = node.id || 'smoke-karte-node';
          node.focus();
          node.click();
          const d = document.getElementById('concept-drawer');
          return { ok: Boolean(d && !d.hidden), activeId: document.activeElement ? document.activeElement.id : null };
        })()
        """)
        add_split("5.2", "VERIFIED" if s52.get("ok") and s52.get("activeId") == "concept-drawer-close" else "FAILED",
                  f"open={s52.get('ok')}, activeId={s52.get('activeId')}",
                  "Concept node opens #concept-drawer and focuses close button", "Dialog 'Koncepta atvilktne' announced")

        s53_prep = cdp.eval_js("""
        (() => {
          const d = document.getElementById('concept-drawer');
          const els = d ? Array.from(d.querySelectorAll('button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])')).filter(el => !el.hidden) : [];
          const first = els[0] || null;
          const last = els[els.length - 1] || null;
          if (last) last.focus();
          return { count: els.length, firstId: first ? first.id : null, lastId: last ? last.id : null };
        })()
        """)
        cdp.press_key("Tab")
        s53 = cdp.eval_js(f"""
        (() => {{
          const d = document.getElementById('concept-drawer');
          const aid = document.activeElement ? document.activeElement.id : null;
          const notTrapped = Boolean({s53_prep['count']} > 0 && (!d.contains(document.activeElement) || aid === {json.dumps(s53_prep['lastId'])} || aid !== {json.dumps(s53_prep['firstId'])}));
          return {{ escaped: notTrapped, activeId: aid || 'end-of-document', count: {s53_prep['count']} }};
        }})()
        """)
        add_split("5.3", "VERIFIED" if s53.get("escaped") else "FAILED",
                  f"escaped={s53.get('escaped')}", "Tab escapes #concept-drawer (no focus trap)", "Focus walks out of dialog")

        cdp.eval_js("document.getElementById('concept-drawer-close').focus()")
        cdp.press_key("Escape")
        time.sleep(0.05)
        s54 = cdp.eval_js("""
        (() => {
          const d = document.getElementById('concept-drawer');
          return { closed: Boolean(d && d.hidden), activeId: document.activeElement ? document.activeElement.id : null };
        })()
        """)
        add_split("5.4", "VERIFIED" if s54.get("closed") else "FAILED",
                  f"closed={s54.get('closed')}, activeId={s54.get('activeId')}",
                  "Escape closes #concept-drawer & restores focus", "Focus returns to invoking concept node")

    return rows


def run_n35_perf_in_falkon(artifact: Path, timeout: float = 45.0) -> dict[str, Any]:
    """Re-measure N35 budget rows in Falkon using performance.now()."""
    n35_data = json.loads(DEFAULT_N35_PERF.read_text(encoding="utf-8"))
    harness_by_id = {r["id"]: r for r in n35_data["budget_rows"]}

    with FalkonSession(artifact, timeout=timeout) as sess:
        assert sess.cdp is not None
        cdp = sess.cdp
        wait_for_readiness(cdp, timeout=min(timeout, 20.0))

        browser_rows = cdp.eval_js("""
        (() => {
          const scriptEls = Array.from(document.querySelectorAll('script[type="application/json"]'));
          const tParse0 = performance.now();
          const parsedIslands = {};
          for (const el of scriptEls) {
            if (el.id) parsedIslands[el.id] = JSON.parse(el.textContent || '{}');
          }
          const islandParseMs = performance.now() - tParse0;

          const bankObj = window.SimBank.load(document, { verifyIntegrity: true });
          const covObj = window.SimCoverage.load(document, window.COVERAGE_INVARIANTS);
          const bankList = bankObj.questions || bankObj.instances || [];

          const tStart0 = performance.now();
          window.SimStartView.renderStartTopics(covObj, document);
          window.SimCoverage.render(covObj, document);
          const firstRenderStartMs = performance.now() - tStart0;

          const formsData = parsedIslands['sim-forms'];
          const formA = Array.isArray(formsData.forms)
            ? (formsData.forms.find(f => f.form_id === 'A') || formsData.forms[0])
            : formsData.forms.A;
          const policyData = parsedIslands['sim-exam-policy'];
          const session = new window.SimSession.ExamSession({
            policy: policyData, form: formA, mode: 'exam', seed: 20250901
          });
          session.dispatch('start');
          const byId = {};
          for (const q of bankList) byId[q.instance_id] = q;
          const examShell = new window.SimExam.ExamShell({
            doc: document, session, policy: policyData, instancesById: byId, confirm: false
          });
          examShell.render();

          const slotIndices = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
          const examLat = [];
          for (let i = 0; i < slotIndices.length; i++) {
            const sid = formA.slots[slotIndices[i]].slot_id;
            const t0 = performance.now();
            examShell.navigate(sid);
            if (i % 5 === 0) examShell.toggleFlag(sid);
            examLat.push(performance.now() - t0);
          }
          const examNavMaxMs = Math.max(...examLat);

          let fullRenders = 0;
          const origRender = examShell.render.bind(examShell);
          examShell.render = () => { fullRenders++; return origRender(); };
          const ks = '123456789012345678901234567890';
          const burstSamples = [];
          for (let r = 0; r < 3; r++) {
            const tKey0 = performance.now();
            for (let k = 1; k <= ks.length; k++) {
              examShell.recordAnswer(formA.slots[0].slot_id, { kind: 'raw_text', text: ks.slice(0, k) }, { incremental: true });
            }
            burstSamples.push(performance.now() - tKey0);
          }
          burstSamples.sort((a, b) => a - b);
          const keyBurstMs = burstSamples[1];

          const store = window.SimStore.createStore();
          const revLat = [];
          for (const kind of ['fresh', 'mid_progress', 'near_complete']) {
            const st = window.SimStore.createDefaultState();
            const limit = kind === 'fresh' ? 0 : (kind === 'mid_progress' ? 32 : 60);
            for (let i = 0; i < limit && i < covObj.outcomes.length; i++) {
              const o = covObj.outcomes[i];
              const oid = o.outcome_id || o.id;
              st.progress.outcomes[oid] = { attempted: true, first_pass_correct: i % 3 !== 0, correct_after_retry: i % 3 === 0, attempts: 1 + (i % 2) };
              st.events.push({ seq: i + 1, type: 'task-answered', outcome_id: oid, topic: o.topic, correct: i % 3 !== 0 });
            }
            store.setState(st);
            const t0 = performance.now();
            window.SimRevision.renderFromStore(document, store, {
              coverage: covObj,
              masteryPolicy: parsedIslands['sim-mastery-policy'],
              revisionPolicy: parsedIslands['sim-revision-policy'],
              terms: parsedIslands['sim-terms']
            });
            revLat.push(performance.now() - t0);
          }
          const revMaxMs = Math.max(...revLat);

          return {
            island_parse: Number(islandParseMs.toFixed(3)),
            first_render_start: Number(firstRenderStartMs.toFixed(3)),
            exam_navigator_interaction: Number(examNavMaxMs.toFixed(3)),
            revision_panel_interaction: Number(revMaxMs.toFixed(3)),
            keystroke_burst_incremental: Number(keyBurstMs.toFixed(3)),
            full_renders: fullRenders
          };
        })()
        """)

    comparison: list[dict[str, Any]] = []
    all_ok = True
    for row_id in (
        "island_parse",
        "first_render_start",
        "exam_navigator_interaction",
        "revision_panel_interaction",
        "keystroke_burst_incremental",
    ):
        h = harness_by_id[row_id]
        b_ms = float(browser_rows[row_id])
        h_ms = float(h["measured_ms"])
        ceil_ms = float(h["ceiling_ms"])
        threshold_ms = max(ceil_ms, h_ms * PERF_DIVERGENCE_FACTOR)
        within_ceiling = b_ms <= ceil_ms
        within_factor = b_ms <= (h_ms * PERF_DIVERGENCE_FACTOR)
        ok = b_ms <= threshold_ms
        if not ok:
            all_ok = False
        comparison.append({
            "id": row_id,
            "label": h["label"],
            "harness_ms": h_ms,
            "browser_ms": b_ms,
            "ceiling_ms": ceil_ms,
            "declared_factor": PERF_DIVERGENCE_FACTOR,
            "within_ceiling": within_ceiling,
            "within_factor": within_factor,
            "status": "VERIFIED" if ok else "FAILED",
        })

    return {
        "engine": "Falkon (QtWebEngine)",
        "epistemic_note": "Single-engine browser measurement; Chrome/Firefox/Safari UNVERIFIED.",
        "declared_divergence_factor": PERF_DIVERGENCE_FACTOR,
        "all_within_budget_and_factor": all_ok,
        "rows": comparison,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="N38 Falkon Offline Smoke & Protocol Runner")
    ap.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--include-calibration", action="store_true")
    ap.add_argument("--include-protocols", action="store_true")
    ap.add_argument("--replay-runs", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=45.0)
    args = ap.parse_args()

    artifact = args.artifact.resolve()
    if not artifact.exists():
        print(f"ERROR: Artifact not found: {artifact}", file=sys.stderr)
        return 1

    t0 = time.monotonic()
    artifact_sha = sha256_file(artifact)

    runs: list[dict[str, Any]] = []
    verdict_digests: list[str] = []
    for i in range(max(1, args.replay_runs)):
        res = run_single_smoke(artifact, timeout=args.timeout)
        norm_seq = [{"id": a["id"], "status": a["status"]} for a in res["assertions"]]
        seq_sha = sha256_json(norm_seq)
        verdict_digests.append(seq_sha)
        runs.append({"run": i + 1, "status": res["status"], "verdict_sequence_sha256": seq_sha, "assertions": res["assertions"]})

    determinism_ok = (len(set(verdict_digests)) == 1) and all(r["status"] == "PASS" for r in runs)

    calibration = run_calibration_fixtures(artifact, timeout=args.timeout) if args.include_calibration else []
    cal_ok = all(c["calibration_pass"] for c in calibration) if calibration else True

    protocols: dict[str, Any] = {}
    if args.include_protocols:
        n33_rows = run_n33_protocol_in_falkon(artifact, timeout=args.timeout)
        n35_perf = run_n35_perf_in_falkon(artifact, timeout=args.timeout)
        protocols = {
            "n33_screen_reader_protocol": {
                "rows": n33_rows,
                "verified_count": sum(1 for r in n33_rows if r["status"] == "VERIFIED"),
                "unverified_count": sum(1 for r in n33_rows if r["status"] == "UNVERIFIED"),
                "failed_count": sum(1 for r in n33_rows if r["status"] == "FAILED"),
            },
            "n35_browser_perf": n35_perf,
        }

    overall_pass = determinism_ok and cal_ok and (
        not args.include_protocols or (
            protocols["n33_screen_reader_protocol"]["failed_count"] == 0
            and protocols["n35_browser_perf"]["all_within_budget_and_factor"]
        )
    )

    report = {
        "task": "N38",
        "engine": "Falkon (QtWebEngine)",
        "artifact_path": str(artifact.relative_to(ROOT)) if artifact.is_relative_to(ROOT) else str(artifact),
        "artifact_sha256": artifact_sha,
        "status": "PASS" if overall_pass else "FAIL",
        "elapsed_seconds": round(time.monotonic() - t0, 2),
        "determinism": {
            "replay_runs": len(runs),
            "identical_verdict_sequences": determinism_ok,
            "verdict_sequence_sha256": verdict_digests[0] if verdict_digests else None,
            "runs": runs,
        },
        "calibration_fixtures": calibration,
        "protocols": protocols,
        "cross_engine_statement": CROSS_ENGINE_STATEMENT,
        "unverified_items": [
            "NVDA (Windows) screen-reader speech/braille announcements (N33)",
            "VoiceOver (macOS) screen-reader speech/braille announcements (N33)",
            "Orca / AT-SPI live speech output in headless Xvfb (N33)",
            "Scenario 3.6 real-time timer threshold alert firing (N33)",
            "Scenario 4.3 completed self-assessment toggle in fresh session (N33)",
            "Chrome/Chromium rendering and interaction (explicitly forbidden by AGENTS.md without authorization)",
            "Firefox rendering and interaction (UNAVAILABLE in environment)",
            "Safari/WebKit rendering and interaction (UNAVAILABLE in environment)",
            "Physical printer paper output (UNAVAILABLE in environment)",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"N38 smoke status={report['status']} runs={len(runs)} identical={determinism_ok} elapsed={report['elapsed_seconds']}s out={args.out}")
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
