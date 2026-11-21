"""AI agent: ML prediction -> risk assessment -> decision -> (approved) virtual quarantine -> evidence log.

Everything the agent does happens inside the virtual environment and is logged and reversible."""
from __future__ import annotations

from copy import deepcopy

# PROTOTYPE CONFIGURATION - these thresholds are chosen by the authors for the demo.
# They are NOT scientifically validated risk weights.
DEFAULT_POLICY = {
    "_note": "Prototype configuration settings, not validated values.",
    "ml_threshold": 0.5,                                   # probability needed to call a window RANSOMWARE_LIKE
    "medium_score": 0.5,                                   # risk score for MEDIUM
    "high_score": 0.85,                                    # risk score for HIGH
    "criticality_bonus": {"LOW": 0.0, "MEDIUM": 0.05, "HIGH": 0.10},  # added when the ML model flags the window
    "confirm_windows": 2,                                  # consecutive flagged windows required before HIGH
    "auto_quarantine": False,                              # False = human approval required (default)
}


class AgentController:
    def __init__(self, detector, network, log, policy: dict | None = None):
        self.detector, self.network, self.log = detector, network, log
        self.policy = deepcopy(DEFAULT_POLICY)
        if policy:
            self.policy.update(policy)
        self.reset()

    def reset(self):
        self.streak: dict[str, int] = {}
        self.processed: dict[str, int] = {}     # last tick already assessed per device
        self.latest: dict[str, dict] = {}
        self.assessments: list[dict] = []
        self.pending: dict[str, dict] = {}      # device_id -> assessment waiting for human approval
        self.alerts: list[dict] = []

    # --- risk policy ------------------------------------------------------
    def risk_level(self, prob: float, criticality: str, streak: int) -> tuple[str, float]:
        p = self.policy
        flagged = prob >= p["ml_threshold"]
        score = min(1.0, prob + (p["criticality_bonus"].get(criticality, 0.0) if flagged else 0.0))
        if flagged and score >= p["high_score"] and streak >= p["confirm_windows"]:
            return "HIGH", score
        if score >= p["medium_score"]:
            return "MEDIUM", score
        return "LOW", score

    def assess(self, device_id: str, window: dict) -> dict:
        dev = self.network.devices[device_id]
        det = self.detector.predict_window(window, device_id)
        flagged = det["predicted_class"] == "RANSOMWARE_LIKE"
        self.streak[device_id] = self.streak.get(device_id, 0) + 1 if flagged else 0
        level, score = self.risk_level(det["probability"], dev.criticality, self.streak[device_id])
        a = dict(tick=window["tick"], device_id=device_id, criticality=dev.criticality, risk_level=level,
                 risk_score=round(score, 4), streak=self.streak[device_id], **det)
        self.latest[device_id] = a
        self.assessments.append(a)
        if dev.status != "QUARANTINED":
            dev.security_status = "SUSPICIOUS" if level in ("MEDIUM", "HIGH") else "HEALTHY"
        if level == "HIGH" and dev.status != "QUARANTINED" and device_id not in self.pending:
            self._raise_alert(a)
        return a

    def _raise_alert(self, a: dict):
        d = a["device_id"]
        feats = ", ".join(f"{f['feature']} (z={f['z_score']})" for f in a["top_features"]) or "n/a"
        self.alerts.append(a)
        self.log.add(d, "ALERT", f"HIGH risk: {a['predicted_class']} p={a['probability']:.3f}, "
                     f"criticality={a['criticality']}. Top features: {feats}", "HIGH", a["tick"])
        if self.policy["auto_quarantine"]:
            self.network.quarantine(d, "AUTO-MODE (explicitly enabled)", "High ransomware-like risk", a["tick"])
        else:
            self.pending[d] = a
            self.log.add(d, "APPROVAL", f"Quarantine of {d} requested - waiting for analyst approval", "HIGH", a["tick"])

    # --- monitoring loop --------------------------------------------------
    def evaluate_new(self, env) -> list[dict]:
        """Assess every telemetry window not assessed yet, in time order. Quarantined devices are skipped."""
        out = []
        for d in env.devices:
            for w in env.windows_for(d):
                if w["tick"] <= self.processed.get(d, 0):
                    continue
                self.processed[d] = w["tick"]
                if self.network.is_quarantined(d):
                    continue
                out.append(self.assess(d, w))
        return out

    # --- human-in-the-loop actions ---------------------------------------
    def approve(self, device_id: str, by: str = "analyst", tick: int | None = None) -> bool:
        a = self.pending.pop(device_id, None)
        if a is None:
            return False
        return self.network.quarantine(device_id, by, "High ransomware-like risk (approved)", tick or a["tick"])

    def reject(self, device_id: str, by: str = "analyst") -> bool:
        a = self.pending.pop(device_id, None)
        if a:
            self.log.add(device_id, "APPROVAL", f"Quarantine of {device_id} REJECTED by {by}", "INFO", a["tick"])
        return a is not None

    def release(self, device_id: str, by: str = "analyst") -> bool:
        return self.network.release(device_id, by)

    def threat_level(self) -> str:
        order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
        live = [a["risk_level"] for d, a in self.latest.items() if not self.network.is_quarantined(d)]
        lv = max(live, key=order.get) if live else "LOW"
        if lv == "LOW" and any(self.network.is_quarantined(d) for d in self.network.devices):
            return "CONTAINED"
        return lv