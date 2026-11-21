import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session")
def trained_root(tmp_path_factory):
    """Train a small model in a temporary project folder (does not overwrite the real model)."""
    from train_model import train
    root = tmp_path_factory.mktemp("proj")
    train(root=root, n_normal=120, n_attack=120, quiet=True)
    return root


@pytest.fixture()
def session(trained_root, tmp_path):
    from src.session import DemoSession
    return DemoSession(trained_root, seed=42, persist_log=False, sandbox_dir=tmp_path / "demo_sandbox")