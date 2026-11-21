"""Chrome CDP Visual Verification for Download Report Header & One-Click Run All Operations."""
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
TEMP_DIR = ROOT / ".chrome_tmp_v2"
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
    await asyncio.sleep(1.5)
    res = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=msg_id)
    data = base64.b64decode(res["result"]["data"])
    path.write_bytes(data)
    print(f"Captured: {path.name} ({len(data):,} bytes)", flush=True)


async def main():
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        "--remote-debugging-port=9224",
        "--window-size=1440,900",
        f"--user-data-dir={TEMP_DIR}",
        "http://localhost:8501",
    ])
    try:
        ws_url = None
        for _ in range(25):
            time.sleep(0.6)
            try:
                with urllib.request.urlopen("http://localhost:9224/json", timeout=2) as req:
                    for t in json.loads(req.read().decode()):
                        if t.get("type") == "page" and "webSocketDebuggerUrl" in t:
                            ws_url = t["webSocketDebuggerUrl"]
                            break
                    if ws_url:
                        break
            except Exception:
                pass
        if not ws_url:
            raise RuntimeError("CDP unavailable")

        async with websockets.connect(ws_url, max_size=30_000_000) as ws:
            mid = 100

            def next_id() -> int:
                nonlocal mid
                mid += 1
                return mid

            for _ in range(30):
                await asyncio.sleep(0.8)
                ready = await eval_js(
                    ws,
                    "Boolean(document.querySelector('.pp-header')) && !document.querySelector('[data-testid=\"stSkeleton\"]') && Boolean(document.querySelector('[data-testid=\"stDownloadButton\"] button'))",
                    next_id(),
                )
                if ready:
                    break
            await asyncio.sleep(1.5)

            async def check_overflow(tag: str):
                res = await eval_js(
                    ws,
                    "JSON.stringify({scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth, overflow: document.documentElement.scrollWidth > window.innerWidth})",
                    next_id(),
                )
                print(f"Overflow [{tag}]: {res}", flush=True)

            await set_viewport(ws, 1440, 900, 1.0, next_id())
            await check_overflow("1440x900 Initial")
            await take_shot(ws, SHOTS_DIR / "17_header_download_and_overview.png", next_id())

            # Check the simulation-only opt-in checkbox
            chk = await eval_js(
                ws,
                """
                (() => {
                    const labels = Array.from(document.querySelectorAll('label'));
                    const target = labels.find(l => l.innerText && l.innerText.includes('Allow simulation-only automatic quarantine approval'));
                    if (target) { target.click(); return true; }
                    return false;
                })()
                """,
                next_id(),
            )
            print("Checked opt-in checkbox:", chk, flush=True)
            await asyncio.sleep(2.0)

            # Click Run All Operations -> opens Confirmation Dialog
            clk = await eval_js(
                ws,
                """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const target = btns.find(b => b.innerText && b.innerText.includes('Run All Operations'));
                    if (target) { target.click(); return true; }
                    return false;
                })()
                """,
                next_id(),
            )
            print("Clicked Run All Operations:", clk, flush=True)
            await asyncio.sleep(2.0)
            await take_shot(ws, SHOTS_DIR / "18_run_all_confirmation_dialog.png", next_id())

            # Click Confirm and Run inside the dialog
            conf = await eval_js(
                ws,
                """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const target = btns.find(b => b.innerText && b.innerText.trim() === 'Confirm and Run');
                    if (target) { target.click(); return true; }
                    return false;
                })()
                """,
                next_id(),
            )
            print("Clicked Confirm and Run:", conf, flush=True)

            # Wait for completion summary to appear
            for _ in range(30):
                await asyncio.sleep(1.0)
                done = await eval_js(
                    ws,
                    "document.body.innerText.includes('DEMONSTRATION COMPLETED')",
                    next_id(),
                )
                if done:
                    break
            await asyncio.sleep(1.5)
            await eval_js(ws, "window.scrollTo(0, 480);", next_id())
            await take_shot(ws, SHOTS_DIR / "19_one_click_completed_summary.png", next_id())

            # Responsive overflow checks at 1366x768, 1920x1080, 125% zoom
            await eval_js(ws, "window.scrollTo(0, 0);", next_id())
            await set_viewport(ws, 1366, 768, 1.0, next_id())
            await check_overflow("1366x768 Completed")
            await take_shot(ws, SHOTS_DIR / "14_responsive_1366x768.png", next_id())

            await set_viewport(ws, 1920, 1080, 1.0, next_id())
            await check_overflow("1920x1080 Completed")

            await set_viewport(ws, 1093, 614, 1.25, next_id())
            await check_overflow("1366x768 @ 125% zoom")

            print("Visual verification complete!", flush=True)
    finally:
        chrome_proc.terminate()
        try:
            chrome_proc.wait(timeout=3)
        except Exception:
            chrome_proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
