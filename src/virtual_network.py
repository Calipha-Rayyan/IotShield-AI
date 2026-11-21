"""Virtual network controller. Quarantine here ONLY changes simulated state in memory.
It never touches the real network, firewall, routing or any real device."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


class EventLog:
    """Timestamped security event history (in memory, optionally mirrored to a JSON-lines file)."""

    def __init__(self, path=None):
        self.path = Path(path) if path else None
        self.events: list[dict] = []
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, device_id: str, category: str, message: str, severity: str = "INFO", tick: int | None = None, **extra):
        ev = dict(timestamp=datetime.now().isoformat(timespec="milliseconds"), tick=tick, device_id=device_id,
                  category=category, severity=severity, message=message, **extra)
        self.events.append(ev)
        if self.path:
            with open(self.path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(ev) + "\n")
        return ev

    def clear(self):
        self.events = []

    def to_dataframe(self) -> pd.DataFrame:
        cols = ["timestamp", "tick", "device_id", "severity", "category", "message"]
        return pd.DataFrame(self.events, columns=cols) if self.events else pd.DataFrame(columns=cols)


class VirtualNetwork:
    """Simulated gateway/network controller for the dummy environment."""

    def __init__(self, devices: dict, log: EventLog):
        self.devices = devices
        self.log = log
        self.reset()

    def reset(self):
        self.blocked = {d: dict(events=0, bytes=0.0) for d in self.devices}
        self.response_history: list[dict] = []

    def is_quarantined(self, device_id: str) -> bool:
        return self.devices[device_id].status == "QUARANTINED"

    def quarantine(self, device_id: str, approved_by: str, reason: str, tick: int | None = None) -> bool:
        dev = self.devices[device_id]
        if dev.status == "QUARANTINED":
            return False
        dev.status, dev.security_status = "QUARANTINED", "QUARANTINED"
        self.response_history.append(dict(timestamp=datetime.now().isoformat(timespec="milliseconds"), tick=tick,
                                          device_id=device_id, action="QUARANTINE", approved_by=approved_by,
                                          reason=reason, reversible=True))
        self.log.add(device_id, "RESPONSE", f"{device_id} QUARANTINED (virtual only) - approved by {approved_by}. {reason}",
                     "HIGH", tick)
        return True

    def release(self, device_id: str, by: str = "analyst", tick: int | None = None) -> bool:
        dev = self.devices[device_id]
        if dev.status != "QUARANTINED":
            return False
        dev.status, dev.security_status = "ONLINE", "HEALTHY"
        dev.activity = "Released - monitoring resumed"
        self.response_history.append(dict(timestamp=datetime.now().isoformat(timespec="milliseconds"), tick=tick,
                                          device_id=device_id, action="RELEASE", approved_by=by,
                                          reason="Quarantine lifted (virtual)", reversible=True))
        self.log.add(device_id, "RESPONSE", f"{device_id} released from virtual quarantine by {by}", "INFO", tick)
        return True

    def transmit(self, device_id: str, connections: int, out_bytes: float, tick: int | None = None) -> dict:
        """Simulated outbound traffic of one window. Quarantined devices are blocked and the blocks are logged."""
        if self.is_quarantined(device_id):
            b = self.blocked[device_id]
            b["events"] += int(connections)
            b["bytes"] += float(out_bytes)
            self.log.add(device_id, "BLOCKED", f"[BLOCKED_BY_QUARANTINE] Blocked {int(connections)} simulated outbound connections "
                         f"({float(out_bytes):,.0f} bytes) from quarantined {device_id}", "MEDIUM", tick,
                         action_taken="BLOCKED_BY_QUARANTINE")
            return dict(delivered_connections=0, delivered_bytes=0.0, blocked_connections=int(connections),
                        blocked_bytes=float(out_bytes))
        return dict(delivered_connections=int(connections), delivered_bytes=float(out_bytes),
                    blocked_connections=0, blocked_bytes=0.0)