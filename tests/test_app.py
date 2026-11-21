"""Dashboard test: exercises the guided 5-stage workflow, reset consistency across all 7 pages,
single primary action rule, and hidden technical metadata with Streamlit's headless AppTest harness."""
from pathlib import Path

import pytest

st_testing = pytest.importorskip("streamlit.testing.v1")
ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module", autouse=True)
def _ensure_model():
    if not (ROOT / "models" / "ransomware_rf.joblib").exists():
        import sys
        sys.path.insert(0, str(ROOT))
        from train_model import train
        train(ROOT, quiet=True)


def _main_btn(at, label):
    return next(b for b in at.main.button if b.label == label)


def _nav_btn(at, label):
    return next(b for b in at.sidebar.button if b.label == label)


def test_guided_workflow_single_primary_action_and_reset_consistency():
    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception

    # Sidebar must contain only the 7 navigation items (no duplicate workflow action buttons)
    sidebar_labels = [b.label for b in at.sidebar.button]
    assert sidebar_labels == [
        "Overview",
        "Devices",
        "Network Traffic",
        "AI Detection",
        "Prevention Center",
        "Security Events",
        "Model Evaluation",
    ]

    # Raw technical metadata expander must be hidden by default
    assert not any("Advanced technical evidence" in e.label for e in at.expander)

    # Stage 1: prominent Run All Operations + Stage 1 guided action (no future-stage actions)
    assert [b.label for b in at.main.button] == ["Run All Operations", "Start normal activity"]
    _main_btn(at, "Start normal activity").click().run()
    assert not at.exception

    # Stage 2: Launch safe attack simulation
    assert any(b.label == "Launch safe attack simulation" for b in at.main.button)
    assert not any(b.label == "Approve quarantine" for b in at.main.button)
    _main_btn(at, "Launch safe attack simulation").click().run()
    assert not at.exception

    # Stage 3: Run AI detection
    assert any(b.label == "Run AI detection" for b in at.main.button)
    _main_btn(at, "Run AI detection").click().run()
    assert not at.exception
    assert any("quarantine approval requested" in w.value for w in at.warning)

    # Stage 4: Approve quarantine
    _main_btn(at, "Approve quarantine").click().run()
    assert not at.exception
    sess = at.session_state["S"]
    assert sess.env.devices["PLC-01"].status == "QUARANTINED"

    # Stage 5: Advance simulation and verify blocked traffic
    _main_btn(at, "Advance simulation and verify blocked traffic").click().run()
    assert not at.exception
    assert sess.blocked_totals()["events"] > 0
    assert any("Demonstration completed successfully." in s.value for s in at.success)

    # Reset demonstration -> authoritative clean state
    _main_btn(at, "Reset demonstration").click().run()
    assert not at.exception
    snap = sess.state_snapshot()
    assert snap["healthy_devices"] == 4
    assert snap["suspicious_devices"] == 0
    assert snap["quarantined_devices"] == 0
    assert snap["threat_level"] == "LOW"
    assert snap["blocked_events"] == 0
    assert snap["stage"]["index"] == 0
    assert [b.label for b in at.main.button] == ["Run All Operations", "Start normal activity"]

    # Visit every navigation page after reset to confirm zero exceptions and consistent state
    for page in ("Devices", "Network Traffic", "AI Detection", "Prevention Center", "Security Events", "Model Evaluation"):
        _nav_btn(at, page).click().run()
        assert not at.exception, f"Exception on {page}"
