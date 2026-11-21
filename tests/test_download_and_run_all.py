"""Automated tests for Download Report UX and One-Click 'Run All Operations' workflow."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.report_generator import build_security_report, report_filename

st_testing = pytest.importorskip("streamlit.testing.v1")
ROOT = Path(__file__).resolve().parent.parent


def test_report_empty_state_and_dynamic_filename(session):
    """Empty-state report must clearly state no demonstration is available and include scenario ID."""
    fname = report_filename(session)
    assert fname == f"IoTShield_AI_Security_Report_{session.scenario_id}.md"
    md = build_security_report(session)
    assert session.scenario_id in md
    assert "No completed attack-detection demonstration is available in this scenario." in md
    assert "SAFE SIMULATION ONLY" in md
    for dev in ("CAM-01", "TEMP-01", "PLC-01", "GW-01"):
        assert dev in md


def test_run_all_manual_mode_pauses_at_approval_stage(session):
    """Default manual approval mode must pause at Stage 4 and request explicit approval."""
    res = session.run_all_operations(target="PLC-01", severity=0.75, allow_simulated_approval=False)
    assert res["status"] == "PAUSED_FOR_APPROVAL"
    assert res["approval_mode"] == "MANUAL_REQUIRED"
    assert "PLC-01" in session.agent.pending
    assert session.env.devices["PLC-01"].status == "ONLINE"
    assert session.current_stage()["key"] == "APPROVAL_READY"

    # Manual approval followed by advance completes prevention verification
    assert session.approve_quarantine("PLC-01", by="analyst") == ["PLC-01"]
    session.advance(5)
    assert session.blocked_totals()["events"] > 0
    summary = session.completion_summary()
    assert summary is not None
    assert summary["status"] == "COMPLETED"
    assert summary["delivered_bytes_after_quarantine"] == 0


def test_run_all_one_click_simulated_approval_and_report_evidence(session):
    """One-click opt-in auto-approval completes all stages, labels SIMULATED_APPROVAL, and populates report."""
    res = session.run_all_operations(target="PLC-01", severity=0.75, allow_simulated_approval=True)
    assert res["status"] == "COMPLETED"
    assert res["target"] == "PLC-01"
    assert res["detection"] == "RANSOMWARE_LIKE"
    assert res["risk"] == "HIGH"
    assert res["quarantine_status"] == "Completed"
    assert "SIMULATED_APPROVAL" in res["approved_by"]
    assert res["blocked_events"] > 0
    assert res["delivered_bytes_after_quarantine"] == 0
    assert res["other_device_false_alarms"] == 0

    # Virtual-only and reversible (no host network modification)
    assert session.env.network.response_history[0]["reversible"] is True
    assert "SIMULATED_APPROVAL" in session.env.network.response_history[0]["approved_by"]

    # Downloaded report contains real scenario ID, detection result, and quarantine evidence
    snap_before = session.state_snapshot()
    md = build_security_report(session)
    assert session.scenario_id in md
    assert "RANSOMWARE_LIKE" in md
    assert "SIMULATED_APPROVAL" in md
    assert f"{res['blocked_events']:,}" in md
    assert "0 B" in md

    # Report generation must NOT mutate or reset scenario state
    snap_after = session.state_snapshot()
    assert snap_after["scenario_id"] == snap_before["scenario_id"]
    assert snap_after["blocked_events"] == snap_before["blocked_events"]
    assert snap_after["quarantined_devices"] == snap_before["quarantined_devices"]


def test_run_all_respects_target_selection_cam01(session):
    """Selecting CAM-01 must attack and quarantine CAM-01 while PLC-01 remains healthy."""
    res = session.run_all_operations(target="CAM-01", severity=0.75, allow_simulated_approval=True)
    assert res["status"] == "COMPLETED"
    assert res["target"] == "CAM-01"
    assert session.env.devices["CAM-01"].status == "QUARANTINED"
    assert session.env.devices["PLC-01"].status == "ONLINE"
    assert session.env.devices["PLC-01"].security_status == "HEALTHY"


def test_run_all_prevents_concurrent_duplicate_execution(session):
    """When is_running is True, repeated activation must not launch a duplicate simulation."""
    session.is_running = True
    try:
        res = session.run_all_operations(target="PLC-01", allow_simulated_approval=True)
        assert res["status"] == "ALREADY_RUNNING"
        assert session.env.tick == 0
    finally:
        session.is_running = False


def test_run_all_failed_execution_does_not_claim_success(session):
    """Invalid target or failed run must not claim COMPLETED."""
    with pytest.raises(KeyError):
        session.run_all_operations(target="INVALID-99", allow_simulated_approval=True)
    assert session.is_running is False
    assert session.completion_summary() is None


def test_reset_after_full_one_click_demo(session):
    """Reset after one-click demonstration restores clean baseline state."""
    res = session.run_all_operations(target="PLC-01", severity=0.75, allow_simulated_approval=True)
    assert res["status"] == "COMPLETED"
    session.reset()
    snap = session.state_snapshot()
    assert snap["healthy_devices"] == 4
    assert snap["suspicious_devices"] == 0
    assert snap["quarantined_devices"] == 0
    assert snap["threat_level"] == "LOW"
    assert snap["blocked_events"] == 0
    assert snap["pending_approval"] == []
    assert snap["stage"]["index"] == 0
    assert snap["completion_summary"] is None


def test_header_download_and_run_all_buttons_in_streamlit_ui():
    """Verify Download Report is in main header (not sidebar) and Run All Operations is prominent on Overview."""
    at = st_testing.AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception

    # Sidebar must NOT contain a duplicate download button
    assert not any(
        "Download" in str(getattr(el, "label", "")) for el in at.sidebar
    )

    # Overview must contain prominent Run All Operations button and opt-in checkbox (default unchecked)
    assert any(b.label == "Run All Operations" for b in at.main.button)
    cb = next(c for c in at.main.checkbox if "Allow simulation-only automatic quarantine approval" in c.label)
    assert cb.value is False

    # Enable simulation-only opt-in and trigger confirmed execution cleanly via session state
    cb.check().run()
    assert not at.exception
    assert any("SIMULATED_APPROVAL" in w.value for w in at.warning)

    at.session_state["pending_run_all"] = True
    at.run()
    assert not at.exception
    sess = at.session_state["S"]
    assert sess.current_stage()["key"] == "COMPLETED"
    assert sess.blocked_totals()["events"] > 0
    assert "SIMULATED_APPROVAL" in sess.env.network.response_history[0]["approved_by"]
