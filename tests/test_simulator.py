import numpy as np
import pandas as pd
import pytest

from src.data_generator import generate_dataset, split_by_scenario
from src.feature_engineering import DEVICE_IDS, FEATURES, extract_features, generate_window


def test_four_virtual_devices_with_required_fields(session):
    devs = session.env.devices
    assert set(devs) == {"CAM-01", "TEMP-01", "PLC-01", "GW-01"}
    for d in devs.values():
        assert d.device_id and d.name and d.device_type and d.ip and d.criticality and d.status and d.security_status
    assert devs["CAM-01"].device_type == "IoT" and devs["PLC-01"].device_type == "IIoT"


def test_normal_traffic_generation_is_plausible_and_reproducible():
    a = [generate_window("PLC-01", "normal", np.random.default_rng(1)) for _ in range(3)]
    b = [generate_window("PLC-01", "normal", np.random.default_rng(1)) for _ in range(3)]
    assert a == b
    rng = np.random.default_rng(0)
    w = pd.DataFrame([generate_window("PLC-01", "normal", rng) for _ in range(300)])
    assert 6 < w.connection_count.mean() < 16 and w.file_rename_rate.mean() < 3
    assert w.failed_connection_rate.between(0, 1).all()


def test_ransomware_like_events_exceed_normal():
    rng = np.random.default_rng(0)
    n = pd.DataFrame([generate_window("PLC-01", "normal", rng) for _ in range(200)])
    a = pd.DataFrame([generate_window("PLC-01", "attack", rng, 0.8) for _ in range(200)])
    for col in ("file_write_rate", "file_rename_rate", "outbound_bytes", "connection_count", "failed_connection_rate"):
        assert a[col].mean() > 2 * n[col].mean(), col


def test_feature_extraction_order_and_missing_feature():
    rec = generate_window("CAM-01", "normal", np.random.default_rng(3))
    df = extract_features({**rec, "extra": 1})
    assert list(df.columns) == FEATURES and df.shape == (1, 8) and not df.isna().any().any()
    rec.pop("cpu_usage")
    with pytest.raises(KeyError):
        extract_features(rec)


def test_dataset_split_has_no_scenario_leakage_and_is_reproducible():
    df = generate_dataset(seed=7, n_normal=40, n_attack=40)
    parts = split_by_scenario(df, seed=7)
    ids = {k: set(v.scenario_id) for k, v in parts.items()}
    assert not (ids["train"] & ids["test"]) and not (ids["train"] & ids["val"]) and not (ids["val"] & ids["test"])
    assert sum(len(v) for v in parts.values()) == len(df)
    pd.testing.assert_frame_equal(df, generate_dataset(seed=7, n_normal=40, n_attack=40))
    assert set(df.device_id) == set(DEVICE_IDS)