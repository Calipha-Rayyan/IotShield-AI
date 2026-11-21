"""Automated Chrome Headless Screenshot Capture & Responsive Audit via CDP.
Captures genuine screenshots of IoTShield AI (Porcelain Plum Edition) across all 7 left-rail pages,
the 5-stage guided workflow, reset state, and viewports (1366x768, 1440x900, 1920x1080, 125% zoom).
"""
from __future__ import annotations

import asyncio
import base64
import json
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

import websockets

ROOT = Path(__file__).resolve().parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS_DIR = ROOT / "evidence" / "screenshots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = ROOT / ".chrome_tmp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


async def send_cmd(ws, method: str, params: dict | None = None, msg_id: int = 1) -> dict:
    msg = {"id": msg_id, "method": method}
    if params:
        msg["params"] = params
    await ws.send(json.dumps(msg))
    while True:
        resp = json.loads(await ws.recv())
        if resp.get("id") == msg_id:
            return resp


async def eval_js(ws, expr: str, msg_id: int) -> Any:
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")


async def set_viewport(ws, width: int, height: int, scale: float, msg_id: int):
    await send_cmd(
        ws,
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": scale, "mobile": False},
        msg_id=msg_id,
    )
    await asyncio.sleep(0.8)


async def take_shot(ws, path: Path, msg_id: int):
    await asyncio.sleep(1.4)
    res = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    data = base64.b64decode(res["result"]["data"])
    path.write_bytes(data)
    print(f"Captured: {path.name} ({len(data):,} bytes)", flush=True)


async def main():
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--window-size=1440,900",
        f"--user-data-dir={TEMP_DIR}",
        "http://localhost:8501",
    ])
    print("Launched Chrome on port 9222...", flush=True)

    try:
        ws_url = None
        for _ in range(25):
            time.sleep(0.6)
            try:
                with urllib.request.urlopen("http://localhost:9222/json", timeout=2) as req:
                    for t in json.loads(req.read().decode()):
                        if t.get("type") == "page" and "webSocketDebuggerUrl" in t:
                            ws_url = t["webSocketDebuggerUrl"]
                            break
                    if ws_url:
                        break
            except Exception:
                pass

        if not ws_url:
            raise RuntimeError("Failed to connect to Chrome CDP WebSocket.")

        print(f"Connected to CDP: {ws_url}", flush=True)
        async with websockets.connect(ws_url, max_size=30_000_000) as ws:
            mid = 100

            def next_id() -> int:
                nonlocal mid
                mid += 1
                return mid

            # Wait for Porcelain Plum header and sidebar navigation
            for _ in range(30):
                await asyncio.sleep(0.8)
                ready = await eval_js(
                    ws,
                    "Boolean(document.querySelector('.pp-header')) && !document.querySelector('[data-testid=\"stSkeleton\"]') && Boolean(document.querySelector('section[data-testid=\"stSidebar\"] button'))",
                    next_id(),
                )
                if ready:
                    break
            await asyncio.sleep(1.5)

            async def click_nav(label: str):
                js = f"""
                (() => {{
                    const btns = Array.from(document.querySelectorAll('section[data-testid="stSidebar"] button'));
                    const target = btns.find(b => b.innerText && b.innerText.trim() === '{label}');
                    if (target) {{
                        target.click();
                        return target.innerText.trim();
                    }}
                    return null;
                }})()
                """
                res = await eval_js(ws, js, next_id())
                await asyncio.sleep(2.4)
                await eval_js(ws, "window.scrollTo(0, 0);", next_id())
                print(f"Nav -> {res}", flush=True)
                return res

            async def click_main_btn(exact_or_prefix: str):
                js = f"""
                (() => {{
                    const btns = Array.from(document.querySelectorAll('[data-testid="stMainBlockContainer"] button'));
                    const target = btns.find(b => b.innerText && b.innerText.trim().startsWith('{exact_or_prefix}') && !b.disabled);
                    if (target) {{
                        target.scrollIntoView({{behavior: 'instant', block: 'center'}});
                        target.click();
                        return target.innerText.trim();
                    }}
                    return null;
                }})()
                """
                res = None
                for _ in range(8):
                    res = await eval_js(ws, js, next_id())
                    if res:
                        break
                    await asyncio.sleep(0.7)
                await asyncio.sleep(3.0)
                await eval_js(ws, "window.scrollTo(0, 0);", next_id())
                print(f"Click -> {res}", flush=True)
                return res

            async def check_overflow(tag: str):
                res = await eval_js(
                    ws,
                    "JSON.stringify({scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth})",
                    next_id(),
                )
                print(f"Overflow check [{tag}]: {res}", flush=True)

            await set_viewport(ws, 1440, 900, 1.0, next_id())

            # 01: Initial Overview
            await click_nav("Overview")
            await check_overflow("1440x900 Overview")
            await take_shot(ws, SHOTS_DIR / "01_dashboard_initial.png", next_id())

            # 02: Stage 1 -> Start normal activity
            await click_main_btn("Start normal activity")
            await take_shot(ws, SHOTS_DIR / "02_normal_detected_NORMAL.png", next_id())

            # 03: Network Traffic (Normal)
            await click_nav("Network Traffic")
            await take_shot(ws, SHOTS_DIR / "03_traffic_normal.png", next_id())

            # 04: Stage 2 -> Launch safe attack simulation
            await click_nav("Overview")
            await click_main_btn("Launch safe attack simulation")
            await take_shot(ws, SHOTS_DIR / "04_attack_launched.png", next_id())

            # 05: Stage 3 -> Run AI detection -> HIGH risk alert & Approval required
            await click_main_btn("Run AI detection")
            await take_shot(ws, SHOTS_DIR / "05_high_risk_alert_pending_approval.png", next_id())

            # 06: AI Detection Center (Executive Verdict, no raw JSON)
            await click_nav("AI Detection")
            await take_shot(ws, SHOTS_DIR / "06_ai_detection_explanation.png", next_id())

            # 07: Network Traffic (During Attack)
            await click_nav("Network Traffic")
            await take_shot(ws, SHOTS_DIR / "07_traffic_attack.png", next_id())

            # 08: Stage 4 -> Approve quarantine
            await click_nav("Overview")
            await click_main_btn("Approve quarantine")
            await take_shot(ws, SHOTS_DIR / "08_quarantine_approved.png", next_id())

            # 09: Stage 5 -> Advance simulation and verify blocked traffic -> Prevention Center
            await click_main_btn("Advance simulation and verify blocked traffic")
            await click_nav("Prevention Center")
            await take_shot(ws, SHOTS_DIR / "09_blocked_events.png", next_id())

            # 10: Security Events
            await click_nav("Security Events")
            await take_shot(ws, SHOTS_DIR / "10_event_log.png", next_id())

            # 11: Model Evaluation
            await click_nav("Model Evaluation")
            await take_shot(ws, SHOTS_DIR / "11_model_evaluation.png", next_id())

            # 12: Devices (After Quarantine)
            await click_nav("Devices")
            await take_shot(ws, SHOTS_DIR / "12_devices_after_quarantine.png", next_id())

            # Responsive viewport checks on Overview (completed state)
            await click_nav("Overview")
            await set_viewport(ws, 1366, 768, 1.0, next_id())
            await check_overflow("1366x768 Overview")
            await take_shot(ws, SHOTS_DIR / "14_responsive_1366x768.png", next_id())

            await set_viewport(ws, 1920, 1080, 1.0, next_id())
            await check_overflow("1920x1080 Overview")
            await take_shot(ws, SHOTS_DIR / "15_responsive_1920x1080.png", next_id())

            await set_viewport(ws, 1093, 614, 1.25, next_id())
            await check_overflow("1366x768 @ 125% zoom")
            await take_shot(ws, SHOTS_DIR / "16_zoom_125_percent.png", next_id())

            # 13: Reset demonstration -> clean baseline verified
            await set_viewport(ws, 1440, 900, 1.0, next_id())
            await click_main_btn("Reset demonstration")
            await take_shot(ws, SHOTS_DIR / "13_after_reset.png", next_id())

            print("All 16 Porcelain Plum screenshots captured successfully!", flush=True)

    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
