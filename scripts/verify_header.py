"""Self-contained Chrome CDP verification for the Unified Header at 986px, 1366px, and 1440px."""
from __future__ import annotations

import asyncio
import base64
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parent.parent
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS_DIR = ROOT / "evidence" / "screenshots"
SHOTS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR = ROOT / ".chrome_tmp_hdr"
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


async def eval_js(ws, expr: str, msg_id: int):
    res = await send_cmd(ws, "Runtime.evaluate", {"expression": expr, "awaitPromise": True}, msg_id=msg_id)
    return res.get("result", {}).get("result", {}).get("value")


async def main():
    st_proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"), "--server.headless=true", "--server.port=8502"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    chrome_proc = None
    try:
        # Wait for Streamlit health endpoint
        for _ in range(40):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen("http://localhost:8502/_stcore/health", timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:
                pass

        chrome_proc = subprocess.Popen([
            CHROME_PATH,
            "--headless=new",
            "--remote-debugging-port=9226",
            "--window-size=1440,900",
            f"--user-data-dir={TEMP_DIR}",
            "http://localhost:8502",
        ])

        ws_url = None
        for _ in range(25):
            time.sleep(0.5)
            try:
                with urllib.request.urlopen("http://localhost:9226/json", timeout=2) as r:
                    for t in json.loads(r.read().decode()):
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
            mid = 1

            def nid():
                nonlocal mid
                mid += 1
                return mid

            for _ in range(60):
                await asyncio.sleep(0.8)
                ready = await eval_js(
                    ws,
                    "Boolean(document.querySelector('.pp-header-inner')) && Boolean(document.querySelector('[data-testid=\"stDownloadButton\"] button')) && !document.querySelector('[data-testid=\"stSkeleton\"]')",
                    nid(),
                )
                if ready:
                    break
            await asyncio.sleep(2.0)

            for width, height, fname in (
                (986, 768, "20_header_986px.png"),
                (1366, 768, "21_header_1366px.png"),
                (1440, 900, "22_header_1440px.png"),
            ):
                await send_cmd(
                    ws,
                    "Emulation.setDeviceMetricsOverride",
                    {"width": width, "height": height, "deviceScaleFactor": 1.0, "mobile": False},
                    msg_id=nid(),
                )
                await asyncio.sleep(1.2)
                metrics = await eval_js(
                    ws,
                    """
                    (() => {
                        const btn = document.querySelector('[data-testid="stDownloadButton"] button');
                        const rect = btn ? btn.getBoundingClientRect() : null;
                        return JSON.stringify({
                            overflow: document.documentElement.scrollWidth > window.innerWidth,
                            btnText: btn ? btn.innerText.trim() : null,
                            btnWidth: rect ? Math.round(rect.width) : null,
                            truncated: btn ? btn.scrollWidth > btn.clientWidth + 2 : null
                        });
                    })()
                    """,
                    nid(),
                )
                print(f"{width}x{height} -> {metrics}", flush=True)
                shot = await send_cmd(ws, "Page.captureScreenshot", {"format": "png"}, msg_id=nid())
                (SHOTS_DIR / fname).write_bytes(base64.b64decode(shot["result"]["data"]))
                print(f"Saved {fname}", flush=True)
    finally:
        if chrome_proc:
            chrome_proc.terminate()
            try:
                chrome_proc.wait(timeout=3)
            except Exception:
                chrome_proc.kill()
        st_proc.terminate()
        try:
            st_proc.wait(timeout=3)
        except Exception:
            st_proc.kill()


if __name__ == "__main__":
    asyncio.run(main())
