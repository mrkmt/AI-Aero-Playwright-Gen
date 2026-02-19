from __future__ import annotations

import asyncio
import json
import os
import sys
import threading
import uuid
from dataclasses import dataclass, field


@dataclass
class RecorderHandle:
    session_id: str
    base_url: str
    app_profile: str = "default"
    stop_event: threading.Event = field(default_factory=threading.Event)
    steps: list[dict] = field(default_factory=list)
    error: str | None = None
    thread: threading.Thread | None = None
    status: str = "recording"


_RECORDER_HANDLES: dict[str, RecorderHandle] = {}
_RECORDER_LOCK = threading.Lock()


def _recording_worker(handle: RecorderHandle) -> None:
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        handle.error = f"Playwright unavailable: {exc}"
        return

    script = """
(() => {
  if (window.__akosRecorderInstalled) return;
  window.__akosRecorderInstalled = true;

  function isStableId(id) {
    if (!id) return false;
    if (/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i.test(id)) return false;
    return true;
  }

  function escapeAttr(v) {
    return String(v).replace(/"/g, '\\\\"');
  }

  function stableSelector(el) {
    if (!el || !el.tagName) return "";
    const tag = el.tagName.toLowerCase();

    const dataTestId = el.getAttribute && (el.getAttribute("data-testid") || el.getAttribute("data-test"));
    if (dataTestId) return `[data-testid="${escapeAttr(dataTestId)}"]`;

    const name = el.getAttribute && el.getAttribute("name");
    if (name) return `${tag}[name="${escapeAttr(name)}"]`;

    const ariaLabel = el.getAttribute && el.getAttribute("aria-label");
    if (ariaLabel) return `${tag}[aria-label="${escapeAttr(ariaLabel)}"]`;

    if (el.id && isStableId(el.id)) return "#" + el.id;

    const parts = [];
    let node = el;
    while (node && node.nodeType === Node.ELEMENT_NODE && parts.length < 6) {
      let part = node.tagName.toLowerCase();
      if (node.className && typeof node.className === "string") {
        const cls = node.className.trim().split(/\\s+/).slice(0, 2).join(".");
        if (cls) part += "." + cls;
      }
      const parent = node.parentElement;
      if (parent) {
        const siblings = Array.from(parent.children).filter((x) => x.tagName === node.tagName);
        if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      }
      parts.unshift(part);
      node = parent;
    }
    return parts.join(" > ");
  }

  function send(actionType, target, value) {
    const payload = {
      action_type: actionType,
      selector_snapshot: target ? stableSelector(target) : location.href,
      value: value ?? null,
      timestamp: new Date().toISOString(),
    };
    window.__akosRecord(payload);
  }

  document.addEventListener("click", (e) => {
    const t = e.target instanceof Element ? e.target.closest("button,a,input,select,textarea,[role='button']") || e.target : null;
    if (!t) return;
    send("click", t, null);
  }, true);

  document.addEventListener("change", (e) => {
    const t = e.target;
    if (!(t instanceof HTMLInputElement || t instanceof HTMLTextAreaElement || t instanceof HTMLSelectElement)) return;
    let value = t.value ?? "";
    send("fill", t, value);
  }, true);
})();
"""

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            def _push_step(_source: object, payload: dict) -> None:
                if not isinstance(payload, dict):
                    return
                action = payload.get("action_type")
                selector = str(payload.get("selector_snapshot") or "")
                if action not in {"click", "fill"} or not selector:
                    return
                handle.steps.append(
                    {
                        "action_type": action,
                        "selector_snapshot": selector,
                        "input_value_masked": payload.get("value"),
                    }
                )

            page.expose_binding("__akosRecord", _push_step)
            page.add_init_script(script)
            page.goto(handle.base_url, wait_until="domcontentloaded")
            page.evaluate(script)

            while not handle.stop_event.is_set():
                page.wait_for_timeout(250)

            context.close()
            browser.close()
    except Exception as exc:
        handle.error = f"{type(exc).__name__}: {exc}"


def _build_steps(base_url: str, events: list[dict]) -> list[dict]:
    steps: list[dict] = [
        {
            "id": str(uuid.uuid4()),
            "order": 1,
            "action_type": "goto",
            "selector_snapshot": base_url,
            "input_value_masked": None,
            "assertion": "page_loaded",
            "timeout_ms": 15000,
            "platform": "web",
        }
    ]

    order = 2
    for event in events:
        action = event.get("action_type")
        selector = str(event.get("selector_snapshot") or "")
        if action not in {"click", "fill", "tap"} or not selector:
            continue
        steps.append(
            {
                "id": str(uuid.uuid4()),
                "order": order,
                "action_type": action,
                "selector_snapshot": selector,
                "input_value_masked": event.get("input_value_masked") or event.get("value"),
                "assertion": None,
                "timeout_ms": 10000,
                "platform": event.get("platform", "web"),
            }
        )
        order += 1

    return steps


def start_recording(app_profile: str, base_url: str) -> dict:
    session_id = str(uuid.uuid4())

    handle = RecorderHandle(session_id=session_id, base_url=base_url, app_profile=app_profile)

    # Start Playwright recording thread (skipped during tests)
    if "PYTEST_CURRENT_TEST" not in os.environ:
        worker = threading.Thread(target=_recording_worker, args=(handle,), daemon=True)
        handle.thread = worker
        worker.start()

    with _RECORDER_LOCK:
        _RECORDER_HANDLES[session_id] = handle

    return {"session_id": session_id, "status": "recording"}


def stop_recording(session_id: str) -> dict | None:
    handle: RecorderHandle | None = None
    with _RECORDER_LOCK:
        handle = _RECORDER_HANDLES.pop(session_id, None)

    if handle is None:
        return None

    handle.stop_event.set()
    if handle.thread:
        handle.thread.join(timeout=15)

    steps = _build_steps(handle.base_url, handle.steps)
    source = "live" if not handle.error else f"live ({handle.error})"

    return {"session_id": session_id, "status": "stopped", "steps": steps, "source": source}


def session_steps(session_id: str) -> list[dict]:
    with _RECORDER_LOCK:
        if session_id in _RECORDER_HANDLES:
            handle = _RECORDER_HANDLES[session_id]
            return _build_steps(handle.base_url, handle.steps)
    return []


def handle_extension_message(session_id: str, message: dict) -> None:
    with _RECORDER_LOCK:
        handle = _RECORDER_HANDLES.get(session_id)
        if not handle:
            return
        if message:
            handle.steps.append(message)
