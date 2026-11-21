import json

import numpy as np

from src.detector import Detector
from src.feature_engineering import generate_window


def test_model_artifacts_saved(trained_root):
    assert (trained_root / "models" / "ransomware_rf.joblib").exists()
    assert json.loads((trained_root / "models" / "feature_order.json").read_text(encoding="utf-8"))[0] == "connection_count"
    ev = trained_root / "evidence" / "evaluation"
    for f in ("metrics.json", "classification_report_test.txt", "confusion_matrix_test.png", "confusion_matrix_test.json"):
        assert (ev / f).exists()


def test_metrics_are_consistent_and_labelled_synthetic(trained_root):
    m = json.loads((trained_root / "evidence" / "evaluation" / "metrics.json").read_text(encoding="utf-8"))
    t = m["metrics"]["test"]
    assert "SYNTHETIC" in m["note"]
    assert t["tn"] + t["fp"] + t["fn"] + t["tp"] == t["n"]
    assert abs(t["accuracy"] - (t["tn"] + t["tp"]) / t["n"]) < 1e-9
    assert abs(t["false_positive_rate"] - t["fp"] / (t["fp"] + t["tn"])) < 1e-9
    assert abs(t["false_negative_rate"] - t["fn"] / (t["fn"] + t["tp"])) < 1e-9
    assert m["inference_ms_single_window_mean"] > 0


def test_ml_predictions_normal_vs_attack(trained_root):
    det = Detector.load(trained_root / "models")
    rng = np.random.default_rng(11)
    normal = [det.predict_window(generate_window("PLC-01", "normal", rng), "PLC-01") for _ in range(40)]
    attack = [det.predict_window(generate_window("PLC-01", "attack", rng, 0.8), "PLC-01") for _ in range(40)]
    assert sum(r["predicted_class"] == "NORMAL" for r in normal) >= 36
    assert sum(r["predicted_class"] == "RANSOMWARE_LIKE" for r in attack) >= 36
    r = attack[0]
    assert 0 <= r["probability"] <= 1 and r["timestamp"] and r["inference_ms"] > 0 and r["top_features"]