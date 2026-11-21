"""Reproducible SYNTHETIC dataset generator (fixed seed, scenario-level split)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.feature_engineering import DEVICE_IDS, make_scenario  # noqa: E402

SEED = 42
DATA_NOTICE = ("SYNTHETIC SIMULATION DATA. Produced by src/data_generator.py with a fixed random seed. "
               "It contains no real network traffic and no real ransomware behaviour.")


def generate_dataset(seed: int = SEED, n_normal: int = 240, n_attack: int = 240) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows, sid = [], 0
    for kind, n in (("normal", n_normal), ("attack", n_attack)):
        for i in range(n):
            rows += make_scenario(sid, DEVICE_IDS[i % len(DEVICE_IDS)], kind, rng)
            sid += 1
    return pd.DataFrame(rows)


def split_by_scenario(df: pd.DataFrame, seed: int = SEED, fractions=(0.6, 0.2, 0.2)):
    """Whole scenarios go to exactly one split, so windows of one simulated attack never leak across splits.
    Stratified by scenario type and device."""
    rng = np.random.default_rng(seed + 1)
    assign = {}
    scen = df.drop_duplicates("scenario_id")[["scenario_id", "scenario_type", "device_id"]]
    for _, g in scen.groupby(["scenario_type", "device_id"]):
        ids = rng.permutation(g["scenario_id"].to_numpy())
        a, b = int(len(ids) * fractions[0]), int(len(ids) * (fractions[0] + fractions[1]))
        for j, s in enumerate(ids):
            assign[int(s)] = "train" if j < a else "val" if j < b else "test"
    part = df["scenario_id"].map(assign)
    out = {n: df[part == n].reset_index(drop=True) for n in ("train", "val", "test")}
    sets = {n: set(d["scenario_id"]) for n, d in out.items()}
    assert not (sets["train"] & sets["val"] or sets["train"] & sets["test"] or sets["val"] & sets["test"]), "leakage"
    return out


def write_dataset(out_dir, seed: int = SEED, **kw) -> dict:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = generate_dataset(seed, **kw)
    parts = split_by_scenario(df, seed)
    for name, d in parts.items():
        d.to_csv(out_dir / f"{name}.csv", index=False, encoding="utf-8")
    df.to_csv(out_dir / "full_dataset.csv", index=False, encoding="utf-8")
    (out_dir / "DATASET_README.txt").write_text(
        DATA_NOTICE + f"\nSeed: {seed}\nSplit: scenario-level 60/20/20 (train/val/test), stratified by type and device.\n"
        + "\n".join(f"{n}: {len(d)} windows, {d['scenario_id'].nunique()} scenarios, "
                    f"{int(d['label'].sum())} ransomware-like windows" for n, d in parts.items()) + "\n",
        encoding="utf-8")
    return parts


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=DATA_NOTICE)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "data" / "generated"))
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    for n, d in write_dataset(a.out, a.seed).items():
        print(f"{n}: {len(d)} windows, {d['scenario_id'].nunique()} scenarios, positives={int(d['label'].sum())}")
    print(DATA_NOTICE)