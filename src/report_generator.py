"""Security report (Markdown) and evidence chart generation from REAL session data."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.feature_engineering import WINDOW_SECONDS  # noqa: E402
from src.safe_attack_simulator import BANNER  # noqa: E402

NAVY, TEAL, RED, GREEN = "#0b1b33", "#14b8a6", "#ef4444", "#22c55e"


def report_filename(session) -> str:
    """Return a clean scenario-specific Markdown report filename."""
    scen = getattr(session, "scenario_id", "SCEN-001")
    return f"IoTShield_AI_Security_Report_{scen}.md"


def _compute_scenario_metrics(session) -> dict:
    """Derive current-scenario detection and prevention evidence purely from real backend state."""
    env, agent, net = session.env, session.agent, session.env.network
    target = getattr(session, "target_device", "PLC-01")
    if env.attacks:
        target = next(iter(env.attacks.keys()))

    onset = env.attack_onset(target)
    target_latest = agent.latest.get(target)
    target_alert = next((a for a in reversed(agent.alerts) if a["device_id"] == target), None)
    q_record = next((r for r in reversed(net.response_history) if r["device_id"] == target and r["action"] == "QUARANTINE"), None)
    q_tick = q_record["tick"] if q_record else None

    df = env.history_df()
    normal_windows = 0
    normal_mean_bytes = None
    delivered_after_q = None
    if not df.empty:
        tdf = df[df.device_id == target]
        ndf = tdf[tdf.tick < onset] if onset else tdf
        normal_windows = len(ndf)
        if len(ndf):
            normal_mean_bytes = round(float(ndf.outbound_bytes.mean()), 1)
        if q_tick is not None:
            adf = tdf[tdf.tick > q_tick]
            delivered_after_q = round(float(adf.delivered_bytes.sum()), 1) if len(adf) else 0.0

    delay_windows = None
    if onset is not None and target_alert is not None and target_alert.get("tick") is not None:
        delay_windows = max(1, int(target_alert["tick"]) - int(onset) + 1)

    other_false_alarms = sum(1 for a in agent.alerts if a["device_id"] != target)
    has_demo = bool(env.attacks and (target_latest or target_alert))

    return dict(
        target=target,
        has_demo=has_demo,
        onset=onset,
        normal_windows=normal_windows,
        normal_mean_bytes=normal_mean_bytes,
        target_latest=target_latest,
        target_alert=target_alert,
        q_record=q_record,
        q_tick=q_tick,
        delivered_after_q=delivered_after_q,
        delay_windows=delay_windows,
        other_false_alarms=other_false_alarms,
    )


def build_security_report(session) -> str:
    """Generate a comprehensive Markdown security report from genuine current-scenario state."""
    env, agent, net = session.env, session.agent, session.env.network
    ov = session.overview()
    b = session.blocked_totals()
    scen_id = getattr(session, "scenario_id", "SCEN-001")
    hist_events = getattr(session, "historical_events", [])
    m = _compute_scenario_metrics(session)
    target = m["target"]

    L: list[str] = [
        "# IoTShield AI — Security Demonstration Report",
        f"**{BANNER}**",
        "",
        f"- **Scenario ID:** `{scen_id}`",
        f"- **Generated:** {datetime.now().isoformat(timespec='seconds')}",
        f"- **Simulation Seed:** `{session.seed}`",
        f"- **Simulated Telemetry Windows:** {env.tick} ({env.tick * WINDOW_SECONDS} simulated seconds)",
        f"- **Selected Attack Target:** `{target}`",
        "",
        "> **Safe-Simulation & Synthetic-Data Disclaimer:** All telemetry, alerts, sandbox file renames, "
        "and model metrics in this report come from an isolated classroom simulation using synthetic data and "
        "harmless dummy files. No real ransomware was executed, no real network or firewall was modified, and "
        "synthetic results do not establish real-world malware detection performance.",
        "",
        "## 1. Current Scenario Security Posture",
        f"- **Virtual Devices:** {ov['total']} | **Healthy:** {ov['healthy']} | "
        f"**Suspicious:** {ov['suspicious']} | **Quarantined:** {ov['quarantined']}",
        f"- **Current Threat Level:** {ov['threat']}",
        f"- **Blocked Simulated Events:** {b['events']:,}",
        f"- **Blocked Simulated Outbound Bytes:** {b['bytes']:,.0f} B",
        "",
        "## 2. Virtual Devices & Security States",
        "| Device ID | Name | Type | Simulated IP | Criticality | Status | Security State | Locked Demo Files |",
        "|---|---|---|---|---|---|---|---:|",
    ]
    for d in env.devices.values():
        locked = env.sim.status(d.device_id)["locked_demo_files"]
        L.append(
            f"| {d.device_id} | {d.name} | {d.device_type} | {d.ip} | {d.criticality} | "
            f"{d.status} | {d.security_status} | {locked} |"
        )

    L += ["", "## 3. Normal & Safe Attack Simulation Summary"]
    if m["normal_windows"] > 0:
        L.append(
            f"- **Normal Baseline ({target}):** {m['normal_windows']} windows recorded "
            f"(mean outbound: {m['normal_mean_bytes']:,.1f} B/window)."
        )
    else:
        L.append("- **Normal Baseline:** No normal telemetry windows have been generated in this scenario yet.")

    if not m["has_demo"]:
        L += [
            "- **Attack & Detection Status:** No completed attack-detection demonstration is available in this scenario.",
        ]
    else:
        st_sim = env.sim.status(target)
        L += [
            f"- **Safe Attack Simulation:** Launched on `{target}` at window `{m['onset']}` "
            f"({st_sim['locked_demo_files']} dummy files renamed to `.locked_demo`, "
            f"simulated note present: {'Yes' if st_sim['note_present'] else 'No'}).",
        ]

    L += ["", "## 4. AI Detection & Risk Assessment"]
    det = m["target_alert"] or m["target_latest"]
    if det is None:
        L.append("- No completed attack-detection demonstration is available in this scenario.")
    else:
        delay_str = (
            f"{m['delay_windows']} window(s) ({m['delay_windows'] * WINDOW_SECONDS} simulated seconds)"
            if m["delay_windows"] is not None
            else "N/A (no high-risk alert raised)"
        )
        L += [
            f"- **Target Device:** `{target}`",
            f"- **AI Model Prediction:** `{det['predicted_class']}`",
            f"- **Model Probability (synthetic):** {det['probability']:.4f} ({det['probability']*100:.1f}%)",
            f"- **Risk Assessment:** `{det['risk_level']}` (score: {det.get('risk_score', 'N/A')})",
            f"- **Detection Timestamp:** {det['timestamp']}",
            f"- **Detection Delay:** {delay_str}",
            f"- **False Alarms on Other Virtual Devices:** {m['other_false_alarms']}",
        ]
        feats = det.get("top_features") or []
        if feats:
            L += [
                "",
                "### Important Observed Features",
                "| Feature | Observed Value | Normal Baseline | Deviation (z-score) | Model Importance |",
                "|---|---:|---:|---:|---:|",
            ]
            for f in feats:
                L.append(
                    f"| {f['feature']} | {f['value']} | {f['normal_mean']} | +{f['z_score']}σ | {f['importance']*100:.1f}% |"
                )

    L += ["", "## 5. Approval, Quarantine & Prevention Evidence"]
    q_rec = m["q_record"]
    if q_rec:
        approval_status = f"Approved ({q_rec['approved_by']})"
    elif target in agent.pending:
        approval_status = "Pending manual analyst approval"
    else:
        approval_status = "Not requested"

    deliv_after_str = f"{m['delivered_after_q']:,.0f} B" if m["delivered_after_q"] is not None else "N/A (not yet quarantined)"
    L += [
        f"- **Approval Status:** {approval_status}",
        f"- **Quarantine Result ({target}):** `{env.devices[target].status}` (virtual & reversible)",
        f"- **Blocked Simulated Events:** {b['events']:,}",
        f"- **Blocked Simulated Bytes:** {b['bytes']:,.0f} B",
        f"- **Delivered Outbound Bytes After Quarantine:** {deliv_after_str}",
    ]

    if net.response_history:
        L += ["", "### Response Action History"]
        for r in net.response_history:
            L.append(
                f"- {r['timestamp']} | tick {r['tick']} | {r['device_id']} | {r['action']} | "
                f"approved by: {r['approved_by']} | {r['reason']}"
            )
    else:
        L.append("- **Response Action History:** No quarantine or release actions taken in this scenario.")

    # Synthetic model evaluation metrics (from saved evaluation artifact if present)
    L += ["", "## 6. Synthetic Model Evaluation Metrics (Held-Out Synthetic Test Set)"]
    mpath = Path(session.root) / "evidence" / "evaluation" / "metrics.json"
    if mpath.exists():
        try:
            ev_m = json.loads(mpath.read_text(encoding="utf-8"))
            t = ev_m["metrics"]["test"]
            L += [
                f"- **Note:** {ev_m['note']}",
                f"- **Accuracy:** {t['accuracy']*100:.2f}% | **Precision:** {t['precision']*100:.2f}% | "
                f"**Recall:** {t['recall']*100:.2f}% | **F1-score:** {t['f1']*100:.2f}%",
                f"- **False-Positive Rate:** {t['false_positive_rate']*100:.2f}% | "
                f"**False-Negative Rate:** {t['false_negative_rate']*100:.2f}%",
                f"- **Mean Single-Window CPU Inference:** {ev_m['inference_ms_single_window_mean']} ms",
            ]
        except Exception:
            L.append("- Synthetic evaluation metrics file could not be read.")
    else:
        L.append("- Synthetic evaluation metrics not yet generated (run `python train_model.py`).")

    L += [
        "",
        f"## 7. Current Scenario Event Log (`{scen_id}` — {len(session.log.events)} events)",
    ]
    for e in session.log.events:
        L.append(
            f"- {e['timestamp']} | tick {e['tick']} | {e['device_id']} | {e['severity']} | "
            f"{e['category']} | {e['message']}"
        )

    L += [
        "",
        f"## 8. Historical Scenarios Archive ({len(hist_events)} archived events)",
        (
            f"- {len(hist_events)} event(s) from prior scenarios are archived separately and excluded from "
            f"the current scenario (`{scen_id}`) metrics above."
            if hist_events
            else "- No prior archived scenarios in this session."
        ),
        "",
        "## 9. Safety & Scope Statement",
        "Quarantine operates strictly inside the virtual network controller in memory. No host network interface, "
        "Windows Firewall rule, routing table, or external device was modified. No real ransomware was executed; "
        "only dummy text files inside the isolated sandbox were renamed. Synthetic test metrics do not establish "
        "real-world detection effectiveness.",
    ]
    return "\n".join(L) + "\n"


def plot_timeline(df, target: str, onset: int | None, q_tick: int | None, path) -> None:
    t = df[df.device_id == target]
    fig, axs = plt.subplots(3, 1, figsize=(8, 7), sharex=True, facecolor=NAVY)
    series = [
        ("outbound_bytes", "Outbound bytes attempted", TEAL),
        ("file_rename_rate", "File renames / min", RED),
        ("connection_count", "Connections / window", GREEN),
    ]
    for ax, (col, title, c) in zip(axs, series):
        ax.set_facecolor(NAVY)
        ax.plot(t.tick, t[col], color=c, marker="o", ms=3, label="attempted by device")
        if col == "outbound_bytes":
            ax.plot(t.tick, t.delivered_bytes, color="white", ls="--", lw=1.2, label="delivered to network")
            ax.legend(facecolor=NAVY, labelcolor="white", fontsize=7, loc="upper left")
        if col == "connection_count":
            ax.plot(t.tick, t.delivered_connections, color="white", ls="--", lw=1.2)
        if onset:
            ax.axvline(onset, color=RED, ls=":", lw=1.5)
        if q_tick:
            ax.axvline(q_tick, color="#facc15", ls=":", lw=1.5)
        ax.set_ylabel(title, color="white", fontsize=8)
        ax.tick_params(colors="white", labelsize=8)
        for s in ax.spines.values():
            s.set_color("#334155")
    axs[0].set_title(
        f"{target}: telemetry (SYNTHETIC) - red = attack onset, yellow = quarantine", color="white", fontsize=9
    )
    axs[-1].set_xlabel("Simulated time window (5 s each)", color="white")
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor=NAVY)
    plt.close(fig)
