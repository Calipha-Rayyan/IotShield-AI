from src.agent_controller import AgentController


class FakeDetector:
    def __init__(self, p):
        self.p = p

    def predict_window(self, rec, dev):
        return dict(predicted_class="RANSOMWARE_LIKE" if self.p >= 0.5 else "NORMAL", probability=self.p, top_features=[],
                    inference_ms=0.1, timestamp="t")


def test_risk_assessment_levels(session):
    ag = session.agent
    assert ag.risk_level(0.1, "HIGH", 0)[0] == "LOW"
    assert ag.risk_level(0.6, "LOW", 1)[0] == "MEDIUM"
    assert ag.risk_level(0.95, "HIGH", 1)[0] == "MEDIUM"   # not yet confirmed by consecutive windows
    assert ag.risk_level(0.95, "HIGH", 2)[0] == "HIGH"
    assert ag.risk_level(0.80, "HIGH", 3)[0] == "HIGH"     # criticality bonus lifts 0.80 -> 0.90
    assert ag.risk_level(0.80, "LOW", 3)[0] == "MEDIUM"


def test_normal_environment_gives_no_alert(session):
    session.start_normal(10)
    res = session.run_detection()
    assert len(res) == 40
    assert not session.agent.alerts and not session.agent.pending


def test_attack_alert_requires_approval_then_quarantine_blocks(session):
    session.start_normal(8)
    session.run_detection()
    session.launch_attack("PLC-01", ticks=6, severity=0.8)
    session.run_detection()
    assert "PLC-01" in session.agent.pending                      # approval requested, not yet quarantined
    assert session.env.devices["PLC-01"].status == "ONLINE"
    assert session.approve_quarantine("PLC-01") == ["PLC-01"]     # quarantine approval
    dev = session.env.devices["PLC-01"]
    assert dev.status == "QUARANTINED" and dev.security_status == "QUARANTINED"
    session.advance(4)
    b = session.env.network.blocked["PLC-01"]
    assert b["events"] > 0 and b["bytes"] > 0                      # blocked simulated events
    last = session.env.windows_for("PLC-01")[-1]
    assert last["delivered_bytes"] == 0 and last["blocked_bytes"] > 0
    assert any(e["category"] == "BLOCKED" for e in session.log.events)
    assert session.env.network.response_history[0]["action"] == "QUARANTINE"
    assert session.env.devices["CAM-01"].status == "ONLINE"       # others unaffected


def test_auto_quarantine_only_when_enabled(session):
    session.set_auto_quarantine(True)
    session.launch_attack("PLC-01", ticks=6, severity=0.8, monitor=True)
    assert session.env.devices["PLC-01"].status == "QUARANTINED"
    assert session.env.network.response_history[0]["approved_by"].startswith("AUTO-MODE")


def test_reject_and_release_are_reversible(session):
    session.launch_attack("PLC-01", ticks=6, severity=0.8)
    session.run_detection()
    assert session.agent.reject("PLC-01") and session.env.devices["PLC-01"].status == "ONLINE"
    session.agent.assess("PLC-01", session.env.windows_for("PLC-01")[-1])
    session.agent.assess("PLC-01", session.env.windows_for("PLC-01")[-1])
    session.approve_quarantine("PLC-01")
    assert session.agent.release("PLC-01") and session.env.devices["PLC-01"].status == "ONLINE"


def test_environment_reset(session):
    session.launch_attack("PLC-01", ticks=6, severity=0.8, monitor=True)
    session.approve_quarantine()
    session.reset()
    assert all(d.status == "ONLINE" and d.security_status == "HEALTHY" for d in session.env.devices.values())
    assert session.env.tick == 0 and not session.env.history and not session.agent.pending
    assert session.blocked_totals()["events"] == 0 and not session.env.attacks
    assert session.env.sim.status("PLC-01")["locked_demo_files"] == 0


def test_full_demo_is_reproducible(session):
    a = session.run_full_demo()
    b = session.run_full_demo()
    assert a["stage1_normal"]["result"] == "NORMAL"
    assert a["stage3_detection"]["predicted_class"] == "RANSOMWARE_LIKE"
    assert a["stage4_prevention"]["status"] == "QUARANTINED" and a["stage4_prevention"]["blocked_events_after"] > 0
    assert a["stage5_effectiveness"]["delivered_outbound_bytes_after_quarantine"] == 0
    for k in ("stage1_normal", "stage4_prevention", "stage5_effectiveness"):
        assert a[k] == b[k]
    assert a["stage3_detection"]["probability"] == b["stage3_detection"]["probability"]


def test_release_clears_blocked_activity_label(session):
    session.launch_attack("PLC-01", ticks=6, severity=0.8, monitor=True)
    session.approve_quarantine("PLC-01")
    session.advance(2)
    assert session.env.devices["PLC-01"].activity == "Blocked by quarantine"
    session.agent.release("PLC-01")
    dev = session.env.devices["PLC-01"]
    assert dev.status == "ONLINE" and "Blocked" not in dev.activity


def test_quarantined_devices_cannot_generate_accepted_outbound_events(session):
    """Verify that quarantined devices have zero delivered connections/bytes,
    and all simulated events are rejected and logged by the virtual controller."""
    session.start_normal(5)
    session.launch_attack("PLC-01", ticks=4, severity=0.8)
    session.run_detection()
    session.approve_quarantine("PLC-01")

    # Confirm device is quarantined
    assert session.env.devices["PLC-01"].status == "QUARANTINED"

    # Snapshot blocked count before advancing
    events_before = session.env.network.blocked["PLC-01"]["events"]
    bytes_before = session.env.network.blocked["PLC-01"]["bytes"]

    # Advance simulation by 5 windows while quarantined
    session.advance(5)

    # Verify quarantined device has strictly zero delivered outbound traffic
    plc_windows = [w for w in session.env.windows_for("PLC-01") if w["tick"] > 9]
    assert len(plc_windows) == 5
    for w in plc_windows:
        assert w["delivered_connections"] == 0, "Quarantined device must not deliver connections"
        assert w["delivered_bytes"] == 0.0, "Quarantined device must not deliver bytes"
        assert w["blocked_connections"] > 0, "Attempted connections must be marked as blocked"
        assert w["blocked_bytes"] > 0.0, "Attempted bytes must be marked as blocked"

    # Verify blocked counters increased
    events_after = session.env.network.blocked["PLC-01"]["events"]
    bytes_after = session.env.network.blocked["PLC-01"]["bytes"]
    assert events_after > events_before
    assert bytes_after > bytes_before

    # Verify security event log contains BLOCKED_BY_QUARANTINE entries
    blocked_logs = [e for e in session.log.events if e["category"] == "BLOCKED" and e["device_id"] == "PLC-01"]
    assert len(blocked_logs) >= 5
    assert all("BLOCKED_BY_QUARANTINE" in e["message"] for e in blocked_logs)

    # Verify unquarantined devices still deliver normal traffic
    cam_windows = [w for w in session.env.windows_for("CAM-01") if w["tick"] > 9]
    assert all(w["delivered_connections"] > 0 and w["delivered_bytes"] > 0 for w in cam_windows)


def test_full_demo_with_cam01_and_repeated_runs(session):
    """Full demonstration must succeed for both PLC-01 and CAM-01 and across repeated resets."""
    r1 = session.run_full_demo(target="CAM-01", severity=0.75)
    assert r1["stage3_detection"]["predicted_class"] == "RANSOMWARE_LIKE"
    assert r1["stage4_prevention"]["status"] == "QUARANTINED"
    assert r1["stage4_prevention"]["blocked_events_after"] > 0
    assert session.env.devices["PLC-01"].status == "ONLINE"
    assert session.env.sim.status("PLC-01")["locked_demo_files"] == 0

    r2 = session.run_full_demo(target="PLC-01", severity=0.75)
    assert r2["stage3_detection"]["predicted_class"] == "RANSOMWARE_LIKE"
    assert r2["stage4_prevention"]["status"] == "QUARANTINED"
    assert r2["stage4_prevention"]["blocked_events_after"] > 0
    assert session.env.devices["CAM-01"].status == "ONLINE"
    assert session.env.sim.status("CAM-01")["locked_demo_files"] == 0


def test_reset_consistency_and_historical_log_separation(session):
    """After reset, every authoritative state metric returns to clean NORMAL and old logs archive."""
    first_scen = session.scenario_id
    session.start_normal(6)
    session.launch_attack("PLC-01", ticks=5, severity=0.8)
    session.run_detection()
    session.approve_quarantine("PLC-01")
    session.advance(3)

    snap_before = session.state_snapshot()
    assert snap_before["quarantined_devices"] == 1
    assert snap_before["blocked_events"] > 0
    assert len(snap_before["current_events"]) > 3

    session.reset()
    snap = session.state_snapshot()
    assert snap["scenario_id"] != first_scen
    assert snap["healthy_devices"] == 4
    assert snap["suspicious_devices"] == 0
    assert snap["quarantined_devices"] == 0
    assert snap["threat_level"] == "LOW"
    assert snap["blocked_events"] == 0 and snap["blocked_bytes"] == 0.0
    assert snap["pending_approval"] == []
    assert snap["latest_detections"] == {}
    assert snap["stage"]["index"] == 0 and snap["stage"]["key"] == "NORMAL_READY"
    # Historical logs are preserved separately from the fresh scenario
    assert len(snap["historical_events"]) >= len(snap_before["current_events"])
    assert len(snap["current_events"]) == 1