"""ML detector wrapper: loads the saved Random Forest and scores one telemetry window."""
from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_FILE = "ransomware_rf.joblib"
FEATURE_FILE = "feature_order.json"
BASELINE_FILE = "baseline_stats.json"


class ModelNotTrainedError(FileNotFoundError):
    pass


class Detector:
    def __init__(self, model, feature_order, baseline, threshold: float = 0.5):
        self.model = model
        if hasattr(model, "n_jobs"):
            model.n_jobs = 1  # one window at a time: multi-threading only adds start-up delay (large on Windows)
        self.features = list(feature_order)
        self.baseline = baseline  # {device_id: {feature: {"mean":..,"std":..}}} from NORMAL training windows
        self.threshold = threshold
        self.importances = dict(zip(self.features, map(float, model.feature_importances_)))

    @classmethod
    def load(cls, models_dir, threshold: float = 0.5) -> "Detector":
        d = Path(models_dir)
        if not (d / MODEL_FILE).exists():
            raise ModelNotTrainedError(f"No trained model in {d}. Run: python train_model.py")
        model = joblib.load(d / MODEL_FILE)
        feats = json.loads((d / FEATURE_FILE).read_text(encoding="utf-8"))
        base = json.loads((d / BASELINE_FILE).read_text(encoding="utf-8"))
        return cls(model, feats, base, threshold)

    def predict_proba_frame(self, df: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(df[self.features])[:, 1]

    def predict_window(self, record: dict, device_id: str | None = None) -> dict:
        """Score one window. Returns predicted class, ransomware-like probability, top contributing features."""
        t0 = time.perf_counter()
        x = pd.DataFrame([[record[f] for f in self.features]], columns=self.features)
        prob = float(self.model.predict_proba(x)[0, 1])
        ms = (time.perf_counter() - t0) * 1000.0
        return dict(
            predicted_class="RANSOMWARE_LIKE" if prob >= self.threshold else "NORMAL",
            probability=round(prob, 4),
            top_features=self.explain(record, device_id),
            inference_ms=round(ms, 3),
            timestamp=datetime.now().isoformat(timespec="milliseconds"),
        )

    def explain(self, record: dict, device_id: str | None, k: int = 3) -> list[dict]:
        """Simple, transparent explanation: global RF importance x how far the value is above this
        device's normal training baseline (z-score). It is a heuristic ranking, not a causal explanation."""
        base = self.baseline.get(device_id or "", None)
        out = []
        for f in self.features:
            if base is None:
                continue
            m, s = base[f]["mean"], max(base[f]["std"], 1e-9)
            z = (record[f] - m) / s
            if z > 0:
                out.append(dict(feature=f, value=record[f], normal_mean=round(m, 3), z_score=round(z, 2),
                                importance=round(self.importances[f], 4), rank_score=self.importances[f] * z))
        out.sort(key=lambda d: d["rank_score"], reverse=True)
        for d in out:
            d["rank_score"] = round(d["rank_score"], 3)
        return out[:k]