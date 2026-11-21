"""Dummy IoT/IIoT environment: four virtual devices and a tick-based telemetry generator.
No real devices, no real network, no hospital/medical devices (IoMT is out of scope for the prototype)."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.feature_engineering import FEATURES, WINDOW_SECONDS, generate_window
from src.safe_attack_simulator import SafeAttackSimulator
from src.virtual_network import EventLog, VirtualNetwork


@dataclass
class Device:
    device_id: str
    name: str
    device_type: str  # IoT, IIoT, IIoT infrastructure
    ip: str  # simulated, non-routable address
    criticality: str  # LOW / MEDIUM / HIGH (prototype setting)
    role: str
    status: str = "ONLINE"  # ONLINE / QUARANTINED
    security_status: str = "HEALTHY"  # HEALTHY / SUSPICIOUS / QUARANTINED
    activity: str = "Idle"
    last_window: dict = field(default_factory=dict)


def default_devices() -> dict:
    ds = [
        Device("CAM-01", "Smart Security Camera", "IoT", "10.10.1.11", "MEDIUM", "Sends simulated monitoring data to the gateway"),
        Device("TEMP-01", "Smart Temperature Sensor", "IoT", "10.10.1.12", "LOW", "Sends periodic temperature telemetry"),
        Device("PLC-01", "Industrial PLC", "IIoT", "10.10.2.21", "HIGH", "Sends industrial telemetry to monitoring systems"),
        Device("GW-01", "Industrial Network Gateway", "IIoT infrastructure", "10.10.2.1", "HIGH",
               "Receives device traffic and tracks virtual connections"),
    ]
    return {d.device_id: d for d in ds}


class VirtualEnvironment:
    def __init__(self, seed: int, sandbox_root, log: EventLog):
        self.seed = seed
        self.log = log
        self.devices = default_devices()
        self.network = VirtualNetwork(self.devices, log)
        self.sim = SafeAttackSimulator(sandbox_root, list(self.devices))
        self._init_state()

    def _init_state(self):
        self.rng = np.random.default_rng(self.seed)
        self.tick = 0
        self.history: list[dict] = []
        self.attacks: dict[str, dict] = {}

    # --- control -------------------------------------------------------
    def reset(self):
        for d in self.devices.values():
            d.status, d.security_status, d.activity, d.last_window = "ONLINE", "HEALTHY", "Idle", {}
        self.network.reset()
        self.sim.reset()
        self._init_state()

    def start_attack(self, device_id: str, severity: float = 0.7):
        if device_id not in self.devices:
            raise KeyError(device_id)
        self.attacks[device_id] = dict(onset_tick=self.tick + 1, severity=severity, k=0)
        self.log.add(device_id, "ATTACK", f"Safe ransomware-like SIMULATION started on {device_id} (dummy files only)",
                     "HIGH", self.tick + 1)

    def attack_onset(self, device_id: str):
        a = self.attacks.get(device_id)
        return a["onset_tick"] if a else None

    # --- one simulated time window ---------------------------------------
    def step(self) -> list[dict]:
        self.tick += 1
        recs = []
        for dev_id, dev in self.devices.items():
            a = self.attacks.get(dev_id)
            if a:
                sev = a["severity"] * min(1.0, 0.6 + 0.1 * a["k"])
                a["k"] += 1
                raw = generate_window(dev_id, "attack", self.rng, sev)
                files = max(1, round(raw["file_rename_rate"] * WINDOW_SECONDS / 60))
                fs = self.sim.advance(dev_id, files)
                mode = "attack"
            else:
                raw = generate_window(dev_id, "normal", self.rng)
                fs = None
                mode = "normal"
            tx = self.network.transmit(dev_id, raw["connection_count"], raw["outbound_bytes"], self.tick)
            rec = dict(tick=self.tick, sim_time_s=self.tick * WINDOW_SECONDS, device_id=dev_id, mode=mode,
                       true_label=int(mode == "attack"), **raw, **tx,
                       locked_demo_files=(fs or self.sim.status(dev_id))["locked_demo_files"])
            dev.last_window = rec
            if not self.network.is_quarantined(dev_id):
                dev.activity = "Abnormal (simulated attack)" if mode == "attack" else "Normal"
            else:
                dev.activity = "Blocked by quarantine"
            self.history.append(rec)
            recs.append(rec)
        return recs

    def history_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.history)

    def windows_for(self, device_id: str) -> list[dict]:
        return [r for r in self.history if r["device_id"] == device_id]


__all__ = ["Device", "VirtualEnvironment", "default_devices", "FEATURES"]