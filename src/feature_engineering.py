"""Feature definitions and the synthetic telemetry generator for IoTShield AI.

ALL DATA PRODUCED HERE IS SYNTHETIC. The numeric profiles are invented prototype
settings, not measurements from real devices or real ransomware.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURES = [
    "connection_count",
    "unique_destinations",
    "outbound_bytes",
    "failed_connection_rate",
    "file_write_rate",
    "file_rename_rate",
    "cpu_usage",
    "device_activity_score",
]
CLASS_NAMES = {0: "NORMAL", 1: "RANSOMWARE_LIKE"}
WINDOW_SECONDS = 5  # one simulated time window = 5 seconds of telemetry

# (mean, standard deviation) of normal behaviour per device. Prototype values.
PROFILES = {
    "CAM-01": dict(connection_count=(18, 4), unique_destinations=(3, 1), outbound_bytes=(900_000, 180_000),
                   failed_connection_rate=(0.02, 0.01), file_write_rate=(6, 2), file_rename_rate=(0.4, 0.3),
                   cpu_usage=(35, 7)),
    "TEMP-01": dict(connection_count=(4, 1.5), unique_destinations=(1.5, 0.5), outbound_bytes=(8_000, 2_000),
                    failed_connection_rate=(0.01, 0.01), file_write_rate=(1, 0.5), file_rename_rate=(0.1, 0.1),
                    cpu_usage=(8, 2)),
    "PLC-01": dict(connection_count=(10, 3), unique_destinations=(2, 0.8), outbound_bytes=(120_000, 30_000),
                   failed_connection_rate=(0.015, 0.01), file_write_rate=(4, 1.5), file_rename_rate=(0.3, 0.2),
                   cpu_usage=(22, 5)),
    "GW-01": dict(connection_count=(60, 12), unique_destinations=(12, 3), outbound_bytes=(2_500_000, 500_000),
                  failed_connection_rate=(0.03, 0.015), file_write_rate=(10, 3), file_rename_rate=(0.8, 0.5),
                  cpu_usage=(40, 8)),
}
DEVICE_IDS = list(PROFILES)

# Caps used only to scale the derived activity index to 0-100 (prototype setting).
_ACTIVITY_CAPS = dict(connection_count=150, unique_destinations=40, outbound_bytes=10_000_000,
                      failed_connection_rate=0.5, file_write_rate=150, file_rename_rate=80, cpu_usage=100)


def activity_score(v: dict) -> float:
    """Derived overall activity indicator, 0-100: mean of capped, scaled features."""
    parts = [min(max(v[k] / cap, 0.0), 1.0) for k, cap in _ACTIVITY_CAPS.items()]
    return round(100.0 * float(np.mean(parts)), 3)


def _finish(v: dict) -> dict:
    v["failed_connection_rate"] = round(float(np.clip(v["failed_connection_rate"], 0, 1)), 4)
    v["cpu_usage"] = round(float(np.clip(v["cpu_usage"], 0, 100)), 2)
    v["connection_count"] = int(max(0, round(v["connection_count"])))
    v["unique_destinations"] = int(max(1, round(v["unique_destinations"])))
    for k in ("outbound_bytes", "file_write_rate", "file_rename_rate"):
        v[k] = round(max(0.0, float(v[k])), 3)
    v["device_activity_score"] = activity_score(v)
    return {k: v[k] for k in FEATURES}


def generate_window(device_id: str, mode: str, rng: np.random.Generator, severity: float = 0.7,
                    drift: float = 1.0) -> dict:
    """One telemetry window. mode is 'normal' or 'attack'; severity in (0, 1] only matters for attack.
    drift scales the device baseline (per-run variation: busier or quieter than the average profile)."""
    p = PROFILES[device_id]
    v = {k: max(0.0, float(rng.normal(m, s))) for k, (m, s) in p.items()}
    for k in ("connection_count", "outbound_bytes", "file_write_rate", "cpu_usage"):
        v[k] *= drift
    if mode == "normal":
        if rng.random() < 0.12:  # benign burst (e.g. backup or firmware download)
            v["connection_count"] *= rng.uniform(1.4, 2.2)
            v["outbound_bytes"] *= rng.uniform(1.5, 3.0)
            v["file_write_rate"] *= rng.uniform(1.5, 4.0)
        if rng.random() < 0.05:  # benign rename burst (e.g. log rotation)
            v["file_rename_rate"] += rng.uniform(2, 12)
    elif mode == "attack":
        s = float(np.clip(severity, 0.05, 1.0))

        def n() -> float:
            return float(rng.normal(1.0, 0.10))

        v["connection_count"] *= (1 + 2.0 * s) * n()
        v["unique_destinations"] *= (1 + 3.0 * s) * n()
        v["outbound_bytes"] *= (1 + 4.0 * s) * n()
        v["failed_connection_rate"] += (0.30 * s) * n()
        v["file_write_rate"] *= (1.0 + 10.0 * s) * n()
        v["file_rename_rate"] += (45.0 * s) * n()
        v["cpu_usage"] += (35 * s) * n()
    else:
        raise ValueError(f"unknown mode {mode!r}")
    return _finish(v)


def make_scenario(scenario_id: int, device_id: str, kind: str, rng: np.random.Generator,
                  n_normal_only: int = 20, n_pre: int = 8, n_attack: int = 12) -> list[dict]:
    """A scenario is one continuous run on one device.
    'normal': only normal windows. 'attack': normal windows, then attack onset with ramping severity."""
    rows = []
    drift = float(np.exp(rng.normal(0.0, 0.2)))  # per-run baseline variation
    if kind == "normal":
        for i in range(n_normal_only):
            rows.append(dict(scenario_id=scenario_id, device_id=device_id, scenario_type=kind, window_index=i,
                             **generate_window(device_id, "normal", rng, drift=drift), label=0))
    else:
        sev = float(rng.uniform(0.03, 1.0))  # includes weak, stealthy attacks
        for i in range(n_pre):
            rows.append(dict(scenario_id=scenario_id, device_id=device_id, scenario_type=kind, window_index=i,
                             **generate_window(device_id, "normal", rng, drift=drift), label=0))
        for k in range(n_attack):
            s = sev * min(1.0, 0.6 + 0.1 * k)
            rows.append(dict(scenario_id=scenario_id, device_id=device_id, scenario_type=kind,
                             window_index=n_pre + k, **generate_window(device_id, "attack", rng, s, drift), label=1))
    return rows


def extract_features(record: dict) -> pd.DataFrame:
    """Feature extraction: pick the model features, in the saved order, from a telemetry record."""
    missing = [f for f in FEATURES if f not in record]
    if missing:
        raise KeyError(f"telemetry record is missing features: {missing}")
    return pd.DataFrame([[record[f] for f in FEATURES]], columns=FEATURES)