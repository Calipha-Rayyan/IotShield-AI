"""DemoSession: single authoritative backend state wiring environment + detector + agent.
Used by the Streamlit dashboard, demo_scenario.py, and automated tests.
Backend owns the truth; frontend explains the truth.
"""
from __future__ import annotations

from pathlib import Path

from src.agent_controller import AgentController
from src.detector import Detector
from src.device_simulator import VirtualEnvironment
from src.feature_engineering import WINDOW_SECONDS
from src.safe_attack_simulator import DEFAULT_SANDBOX_ROOT
from src.virtual_network import EventLog


class DemoSession:
    def __init__(
        self,
        root,
        seed: int = 42,
        auto_quarantine: bool = False,
        persist_log: bool = True,
        sandbox_dir=None,
        models_dir=None,
    ):
        self.root = Path(root).resolve()
        self.seed = seed
        self.scenario_num: int = 1
        self.target_device: str = "PLC-01"
        self.historical_events: list[dict] = []
        self.is_running: bool = False
        self.last_run_summary: dict | None = None

        # Single canonical absolute sandbox root shared across simulator & environment
        canonical_sandbox = (
            Path(sandbox_dir).resolve()
            if sandbox_dir is not None
            else (self.root / "demo_sandbox").resolve()
        )
        self.sandbox_root = canonical_sandbox

        self.detector = Detector.load(models_dir or self.root / "models")
        self.log = EventLog(self.root / "logs" / "security_events.jsonl" if persist_log else None)
        self.env = VirtualEnvironment(seed, canonical_sandbox, self.log)
        self.agent = AgentController(
            self.detector, self.env.network, self.log, {"auto_quarantine": auto_quarantine}
        )
        self.log.add(
            "-",
            "SYSTEM",
            f"Scenario {self.scenario_id} started: 4 virtual devices ONLINE. SAFE SIMULATION ONLY.",
            "INFO",
            0,
            scenario_id=self.scenario_id,
        )

    @property
    def scenario_id(self) -> str:
        return f"SCEN-{self.scenario_num:03d}"

    # --- dashboard actions --------------------------------------------------
    def set_target_device(self, device_id: str) -> None:
        if device_id in self.env.devices:
            self.target_device = device_id

    def set_auto_quarantine(self, flag: bool) -> None:
        self.agent.policy["auto_quarantine"] = bool(flag)

    def start_normal(self, ticks: int = 10) -> None:
        for _ in range(ticks):
            self.env.step()
        self.log.add(
            "-",
            "TRAFFIC",
            f"Normal simulation: {ticks} windows generated for all devices",
            "INFO",
            self.env.tick,
            scenario_id=self.scenario_id,
        )

    def launch_attack(self, target: str = "PLC-01", ticks: int = 6, severity: float = 0.7, monitor: bool = False) -> None:
        self.set_target_device(target)
        self.env.start_attack(target, severity)
        for _ in range(ticks):
            self.env.step()
            if monitor:
                self.agent.evaluate_new(self.env)

    def run_detection(self) -> list[dict]:
        return self.agent.evaluate_new(self.env)

    def approve_quarantine(self, device_id: str | None = None, by: str = "analyst") -> list[str]:
        ids = [device_id] if device_id else list(self.agent.pending)
        return [d for d in ids if self.agent.approve(d, by, self.env.tick)]

    def advance(self, ticks: int = 5, monitor: bool = True) -> None:
        for _ in range(ticks):
            self.env.step()
            if monitor:
                self.agent.evaluate_new(self.env)

    def reset(self) -> None:
        """Archive current scenario events separately, then cleanly restore all backend state."""
        if self.log.events:
            archived = []
            for ev in self.log.events:
                rec = dict(ev)
                rec.setdefault("scenario_id", self.scenario_id)
                archived.append(rec)
            self.historical_events.extend(archived)

        self.scenario_num += 1
        self.is_running = False
        self.last_run_summary = None
        self.env.reset()
        self.agent.reset()
        self.log.clear()
        self.log.add(
            "-",
            "SYSTEM",
            f"Environment reset ({self.scenario_id}): 4 virtual devices ONLINE, dummy files restored.",
            "INFO",
            0,
            scenario_id=self.scenario_id,
        )

    # --- authoritative state & guided workflow ------------------------------
    def blocked_totals(self) -> dict:
        n = self.env.network.blocked
        return dict(events=sum(v["events"] for v in n.values()), bytes=sum(v["bytes"] for v in n.values()))

    def overview(self) -> dict:
        devs = self.env.devices.values()
        return dict(
            total=len(self.env.devices),
            healthy=sum(d.security_status == "HEALTHY" for d in devs),
            suspicious=sum(d.security_status == "SUSPICIOUS" for d in devs),
            quarantined=sum(d.status == "QUARANTINED" for d in devs),
            threat=self.agent.threat_level(),
        )

    def current_stage(self) -> dict:
        """Authoritative 5-stage guided workflow state derived purely from backend state."""
        ov = self.overview()
        bl = self.blocked_totals()
        quarantined = ov["quarantined"] > 0

        if quarantined and bl["events"] > 0:
            return dict(
                index=5,
                key="COMPLETED",
                title="Demonstration completed successfully",
                primary_action=None,
                description=(
                    f"Virtual gateway rejected {bl['events']:,} outbound connection attempts "
                    f"({bl['bytes']:,.0f} bytes) with 0 bytes delivered."
                ),
            )
        if quarantined:
            return dict(
                index=4,
                key="VERIFY_READY",
                title="Stage 5 — Prevention verification",
                primary_action="Advance simulation and verify blocked traffic",
                description="Device is isolated in quarantine. Advance simulation windows to verify that outbound attempts are rejected.",
            )
        if self.agent.pending:
            return dict(
                index=3,
                key="APPROVAL_READY",
                title="Stage 4 — Analyst approval",
                primary_action="Approve quarantine",
                description=(
                    f"High-risk ransomware-like activity confirmed on {', '.join(self.agent.pending)}. "
                    "Explicit analyst approval is required to quarantine the device."
                ),
            )
        if len(self.env.attacks) > 0:
            return dict(
                index=2,
                key="DETECT_READY",
                title="Stage 3 — AI detection",
                primary_action="Run AI detection",
                description="Safe simulated attack telemetry is active. Run the Random Forest detector to assess risk.",
            )
        if self.env.tick > 0:
            return dict(
                index=1,
                key="ATTACK_READY",
                title="Stage 2 — Safe attack simulation",
                primary_action="Launch safe attack simulation",
                description=f"Normal baseline established. Launch harmless ransomware-like simulation against {self.target_device}.",
            )
        return dict(
            index=0,
            key="NORMAL_READY",
            title="Stage 1 — Normal activity",
            primary_action="Start normal activity",
            description="Generate baseline telemetry across all four virtual IoT and industrial devices.",
        )

    def state_snapshot(self) -> dict:
        """Single source of truth consumed by every dashboard view."""
        ov = self.overview()
        bl = self.blocked_totals()
        stage = self.current_stage()
        return dict(
            scenario_id=self.scenario_id,
            tick=self.env.tick,
            target_device=self.target_device,
            stage=stage,
            threat_level=ov["threat"],
            total_devices=ov["total"],
            healthy_devices=ov["healthy"],
            suspicious_devices=ov["suspicious"],
            quarantined_devices=ov["quarantined"],
            blocked_events=bl["events"],
            blocked_bytes=bl["bytes"],
            pending_approval=list(self.agent.pending),
            active_alerts=list(self.agent.alerts),
            latest_detections=dict(self.agent.latest),
            current_events=list(self.log.events),
            historical_events=list(self.historical_events),
            is_running=self.is_running,
            last_run_summary=self.last_run_summary,
            completion_summary=self.completion_summary(),
        )

    def completion_summary(self) -> dict | None:
        """Return genuine completion metrics whenever a scenario reaches Prevention Verified (COMPLETED)."""
        if self.current_stage()["key"] != "COMPLETED":
            return None
        target = next(iter(self.env.attacks.keys()), self.target_device)
        onset = self.env.attack_onset(target)
        alert = next((a for a in reversed(self.agent.alerts) if a["device_id"] == target), None)
        det = alert or self.agent.latest.get(target, {})
        q_rec = next(
            (r for r in reversed(self.env.network.response_history) if r["device_id"] == target and r["action"] == "QUARANTINE"),
            None,
        )
        q_tick = q_rec["tick"] if q_rec else None
        df = self.env.history_df()
        deliv_after = 0.0
        if not df.empty and q_tick is not None:
            after = df[(df.device_id == target) & (df.tick > q_tick)]
            deliv_after = round(float(after.delivered_bytes.sum()), 1) if len(after) else 0.0
        delay_w = (int(alert["tick"]) - int(onset) + 1) if (alert and onset is not None) else None
        bl = self.blocked_totals()
        return dict(
            status="COMPLETED",
            scenario_id=self.scenario_id,
            target=target,
            detection=det.get("predicted_class", "N/A"),
            probability=det.get("probability"),
            risk=det.get("risk_level", "N/A"),
            quarantine_status="Completed" if self.env.devices[target].status == "QUARANTINED" else self.env.devices[target].status,
            approved_by=q_rec["approved_by"] if q_rec else "N/A",
            blocked_events=bl["events"],
            blocked_bytes=round(bl["bytes"]),
            delivered_bytes_after_quarantine=round(deliv_after),
            detection_delay_windows=delay_w,
            detection_delay_simulated_seconds=(delay_w * WINDOW_SECONDS) if delay_w is not None else None,
            other_device_false_alarms=sum(1 for a in self.agent.alerts if a["device_id"] != target),
        )

    def run_all_operations(
        self,
        target: str | None = None,
        severity: float = 0.7,
        allow_simulated_approval: bool = False,
        normal_ticks: int = 10,
        post_quarantine_ticks: int = 5,
        max_attack_ticks: int = 15,
        progress_callback=None,
    ) -> dict:
        """Execute the full demonstration using the existing backend services (no duplicate engine).
        Respects manual approval by default; only auto-approves when allow_simulated_approval=True
        and explicitly labels it as SIMULATED_APPROVAL (virtual sandbox only)."""
        if self.is_running:
            return dict(status="ALREADY_RUNNING", error="A demonstration workflow is already executing.")

        tgt = target or self.target_device or "PLC-01"
        if tgt not in self.env.devices:
            raise KeyError(f"Unknown target device: {tgt}")

        def _notify(step: int, label: str, detail: str) -> None:
            if progress_callback:
                progress_callback(step, label, detail)

        prev_auto = self.agent.policy["auto_quarantine"]
        self.is_running = True
        try:
            # Force explicit approval handling (never silently bypass manual approval)
            self.agent.policy["auto_quarantine"] = False
            self.set_target_device(tgt)
            self.reset()

            # Stage 1: Normal activity
            self.start_normal(normal_ticks)
            s1 = self.run_detection()
            _notify(1, "Normal activity", f"Generated and assessed {len(s1)} normal telemetry windows across 4 devices.")

            # Stage 2 & 3: Safe attack simulation + AI detection
            onset = self.env.tick + 1
            self.env.start_attack(tgt, severity)
            _notify(2, "Safe attack started", f"Launched harmless ransomware-like simulation on {tgt} at window {onset}.")

            detect_tick = None
            for _ in range(max_attack_ticks):
                self.env.step()
                self.agent.evaluate_new(self.env)
                if tgt in self.agent.pending:
                    detect_tick = self.env.tick
                    break

            det = self.agent.latest.get(tgt, {})
            if tgt not in self.agent.pending and det.get("predicted_class") != "RANSOMWARE_LIKE":
                fail = dict(
                    status="FAILED",
                    scenario_id=self.scenario_id,
                    target=tgt,
                    error=f"AI detector did not confirm high-risk ransomware-like activity on {tgt} within {max_attack_ticks} windows.",
                )
                self.last_run_summary = fail
                return fail

            _notify(
                3,
                "AI detection completed",
                f"Detected {det.get('predicted_class')} on {tgt} (p={det.get('probability', 0):.3f}, Risk: {det.get('risk_level')}).",
            )

            # Stage 4: Approval / quarantine
            if not allow_simulated_approval:
                paused = dict(
                    status="PAUSED_FOR_APPROVAL",
                    scenario_id=self.scenario_id,
                    target=tgt,
                    detection=det.get("predicted_class"),
                    probability=det.get("probability"),
                    risk=det.get("risk_level"),
                    approval_mode="MANUAL_REQUIRED",
                    detect_tick=detect_tick,
                )
                self.last_run_summary = paused
                _notify(
                    4,
                    "Approval/quarantine",
                    f"Paused at Stage 4: manual analyst approval is required to quarantine {tgt}.",
                )
                return paused

            approved = self.approve_quarantine(tgt, by="SIMULATED_APPROVAL (virtual sandbox opt-in)")
            if not approved:
                fail = dict(
                    status="FAILED",
                    scenario_id=self.scenario_id,
                    target=tgt,
                    error=f"Simulated quarantine approval could not be applied to {tgt}.",
                )
                self.last_run_summary = fail
                return fail

            _notify(
                4,
                "Approval/quarantine",
                f"{tgt} isolated via SIMULATED_APPROVAL (virtual sandbox only; not a real human approval).",
            )

            # Stage 5: Advance & verify blocked traffic
            self.advance(post_quarantine_ticks, monitor=True)
            bl = self.blocked_totals()
            _notify(
                5,
                "Prevention verified",
                f"Virtual gateway blocked {bl['events']:,} outbound attempts ({bl['bytes']:,.0f} bytes) with 0 bytes delivered.",
            )

            # Stage 6: Demonstration completed
            summary = self.completion_summary()
            if not summary or summary["blocked_events"] <= 0:
                fail = dict(
                    status="FAILED",
                    scenario_id=self.scenario_id,
                    target=tgt,
                    error="Quarantine applied but no blocked outbound events were verified.",
                )
                self.last_run_summary = fail
                return fail

            summary["approval_mode"] = "SIMULATED_APPROVAL"
            self.last_run_summary = summary
            _notify(6, "Demonstration completed", f"Scenario {self.scenario_id} completed and verified.")
            return summary
        except Exception as exc:
            self.last_run_summary = dict(
                status="FAILED",
                scenario_id=self.scenario_id,
                target=tgt,
                error=str(exc),
            )
            raise
        finally:
            self.agent.policy["auto_quarantine"] = prev_auto
            self.is_running = False

    def run_full_demo(
        self,
        target: str = "PLC-01",
        severity: float = 0.7,
        normal_ticks: int = 10,
        post_quarantine_ticks: int = 6,
        max_attack_ticks: int = 15,
    ) -> dict:
        """Stages 1-5 of the demonstration. The 'analyst approval' is performed right after the alert
        (zero human delay), so detection delay measures telemetry windows only."""
        prev_auto = self.agent.policy["auto_quarantine"]
        self.agent.policy["auto_quarantine"] = False  # always demonstrate the manual-approval path
        self.set_target_device(target)
        self.reset()
        res: dict = dict(target=target, severity=severity, seed=self.seed, scenario_id=self.scenario_id)
        # Stage 1 - normal
        self.start_normal(normal_ticks)
        s1 = self.run_detection()
        res["stage1_normal"] = dict(
            windows_assessed=len(s1),
            predicted_ransomware_like=sum(a["predicted_class"] == "RANSOMWARE_LIKE" for a in s1),
            max_probability=max(a["probability"] for a in s1),
            alerts=len(self.agent.alerts),
            expected="NORMAL",
            result=(
                "NORMAL"
                if not any(a["predicted_class"] == "RANSOMWARE_LIKE" for a in s1)
                else f"NORMAL (no alert raised, but {sum(a['predicted_class'] == 'RANSOMWARE_LIKE' for a in s1)} "
                "window-level false positive(s))"
            ),
            per_device_latest={
                d: dict(cls=a["predicted_class"], prob=a["probability"], risk=a["risk_level"])
                for d, a in self.agent.latest.items()
            },
        )
        # Stage 2/3 - attack + live detection
        onset = self.env.tick + 1
        self.env.start_attack(target, severity)
        detect_tick = None
        for _ in range(max_attack_ticks):
            self.env.step()
            self.agent.evaluate_new(self.env)
            if target in self.agent.pending:
                detect_tick = self.env.tick
                break
        a = self.agent.latest.get(target, {})
        first_flag = next(
            (
                x
                for x in self.agent.assessments
                if x["device_id"] == target and x["predicted_class"] == "RANSOMWARE_LIKE"
            ),
            None,
        )
        res["stage2_attack"] = dict(
            onset_tick=onset,
            files_renamed=self.env.sim.status(target)["locked_demo_files"],
            note_present=self.env.sim.status(target)["note_present"],
        )
        res["stage3_detection"] = dict(
            predicted_class=a.get("predicted_class"),
            probability=a.get("probability"),
            risk_level=a.get("risk_level"),
            timestamp=a.get("timestamp"),
            top_features=a.get("top_features"),
            inference_ms=a.get("inference_ms"),
            first_flagged_tick=first_flag["tick"] if first_flag else None,
            high_alert_tick=detect_tick,
        )
        # Stage 4 - approved quarantine + blocked events
        before_out = self.env.network.blocked[target]["events"]
        approved = self.approve_quarantine(target, by="analyst (scripted approval)")
        q_tick = self.env.tick
        for _ in range(post_quarantine_ticks):
            self.env.step()
            self.agent.evaluate_new(self.env)
        bl = self.env.network.blocked[target]
        res["stage4_prevention"] = dict(
            approved=bool(approved),
            quarantine_tick=q_tick,
            status=self.env.devices[target].status,
            blocked_events_before_quarantine=before_out,
            blocked_events_after=bl["events"],
            blocked_bytes_after=round(bl["bytes"]),
        )
        # Stage 5 - before/after
        df = self.env.history_df()
        t = df[df.device_id == target]
        normal = t[t.tick < onset]
        during = t[(t.tick >= onset) & (t.tick <= q_tick)]
        after = t[t.tick > q_tick]
        delay_w = (detect_tick - onset + 1) if detect_tick else None
        res["stage5_effectiveness"] = dict(
            normal_mean_outbound_bytes=round(float(normal.outbound_bytes.mean())),
            normal_mean_connections=round(float(normal.connection_count.mean()), 1),
            attack_mean_outbound_bytes=round(float(during.outbound_bytes.mean())) if len(during) else None,
            attack_mean_file_rename_rate=round(float(during.file_rename_rate.mean()), 1) if len(during) else None,
            delivered_outbound_bytes_before_quarantine=round(float(during.delivered_bytes.sum())) if len(during) else 0,
            delivered_outbound_bytes_after_quarantine=round(float(after.delivered_bytes.sum())),
            attempted_outbound_bytes_after_quarantine=round(float(after.outbound_bytes.sum())),
            blocked_events=bl["events"],
            detection_delay_windows=delay_w,
            detection_delay_simulated_seconds=(delay_w * WINDOW_SECONDS) if delay_w else None,
            other_devices_false_alarms=sum(1 for x in self.agent.alerts if x["device_id"] != target),
            files_renamed_in_sandbox=self.env.sim.status(target)["locked_demo_files"],
        )
        res["note"] = (
            "Synthetic simulation only. Detection delay is counted in telemetry windows "
            f"({WINDOW_SECONDS} simulated seconds each); human approval time is not included."
        )
        self.agent.policy["auto_quarantine"] = prev_auto
        return res
