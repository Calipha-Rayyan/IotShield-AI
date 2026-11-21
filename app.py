"""IoTShield AI — AI-Powered Ransomware Detection and Prevention Simulator for IoT/IIoT Networks.
Porcelain Plum Edition — "Intelligence with elegance."
SAFE SIMULATION ONLY — NO REAL RANSOMWARE IS RUNNING.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.detector import MODEL_FILE  # noqa: E402
from src.feature_engineering import DEVICE_IDS  # noqa: E402
from src.report_generator import build_security_report, report_filename  # noqa: E402
from src.safe_attack_simulator import BANNER, SandboxViolation  # noqa: E402
from src.session import DemoSession  # noqa: E402
from src.ui_theme import (  # noqa: E402
    AI_VIOLET,
    BG_MAIN,
    BORDER_COLOR,
    BRAND_SHIELD_SVG,
    CHAMPAGNE,
    INFO,
    PRIMARY_PLUM,
    ROSE_ACCENT,
    SUCCESS,
    SURFACE_MAIN,
    TEXT_MAIN,
    TEXT_SECONDARY,
    THREAT,
    WARNING,
    format_timestamp,
    get_css,
    normalize_event_row,
    render_complete_demo_panel,
    render_completion_summary,
    render_detection_panel,
    render_device_grid,
    render_event_timeline,
    render_header_badges,
    render_header_brand,
    render_metric_strip,
    render_posture_and_kpis,
    render_prevention_sequence,
    render_safe_strip,
)

logger = logging.getLogger("iotshield.app")
SHOW_TECHNICAL_DETAILS = os.environ.get("IOTSHIELD_SHOW_TECHNICAL_DETAILS", "0") == "1"

# ---------------------------------------------------------------- Page Config
st.set_page_config(
    page_title="IoTShield AI — Porcelain Plum",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(get_css(), unsafe_allow_html=True)

NAV_ITEMS = [
    "Overview",
    "Devices",
    "Network Traffic",
    "AI Detection",
    "Prevention Center",
    "Security Events",
    "Model Evaluation",
]

DEVICE_SERIES_STYLE = {
    "CAM-01": dict(color=SUCCESS, dash="solid", symbol="circle"),
    "TEMP-01": dict(color=INFO, dash="dot", symbol="diamond"),
    "PLC-01": dict(color=ROSE_ACCENT, dash="solid", symbol="square"),
    "GW-01": dict(color=AI_VIOLET, dash="dash", symbol="triangle-up"),
}


# ---------------------------------------------------------------- Helpers
def show_df(df: pd.DataFrame) -> None:
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True)


def show_fig(fig: go.Figure, height: int = 370) -> None:
    """Apply consistent Porcelain Plum light styling to every Plotly chart."""
    fig.update_layout(
        paper_bgcolor=SURFACE_MAIN,
        plot_bgcolor=BG_MAIN,
        font=dict(color=TEXT_MAIN, family="Aptos, Segoe UI, sans-serif", size=13),
        title_font=dict(color=TEXT_MAIN, size=15),
        margin=dict(l=18, r=18, t=48, b=28),
        xaxis=dict(
            gridcolor=BORDER_COLOR,
            linecolor=BORDER_COLOR,
            zerolinecolor=BORDER_COLOR,
            tickfont=dict(color=TEXT_SECONDARY),
            title_font=dict(color=TEXT_MAIN),
        ),
        yaxis=dict(
            gridcolor=BORDER_COLOR,
            linecolor=BORDER_COLOR,
            zerolinecolor=BORDER_COLOR,
            tickfont=dict(color=TEXT_SECONDARY),
            title_font=dict(color=TEXT_MAIN),
        ),
        legend=dict(
            font=dict(color=TEXT_MAIN, size=12),
            bgcolor="rgba(255, 255, 255, 0.92)",
            bordercolor=BORDER_COLOR,
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        hoverlabel=dict(bgcolor=SURFACE_MAIN, bordercolor=PRIMARY_PLUM, font_color=TEXT_MAIN),
        height=height,
    )
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def run_safe_action(fn, success_msg: str | None = None) -> bool:
    """Execute a backend simulation action with friendly UI error handling and server logging."""
    try:
        res = fn()
        if success_msg is not None:
            st.session_state.flash = success_msg(res) if callable(success_msg) else success_msg
        st.session_state.ui_error = None
        return True
    except SandboxViolation:
        logger.exception("Sandbox validation rejected a path during simulation.")
        st.session_state.ui_error = (
            "Simulation stopped safely because the virtual device could not be validated inside the "
            "demonstration sandbox. No external files were modified."
        )
        return False
    except Exception:
        logger.exception("Unexpected error during simulation step.")
        st.session_state.ui_error = (
            "The simulation encountered an unexpected error and stopped safely. Please reset the demonstration."
        )
        return False


def prevention_step_index(snap: dict) -> int:
    """Map authoritative backend snapshot to the 6-step Prevention Center sequence."""
    if snap["quarantined_devices"] > 0 and snap["blocked_events"] > 0:
        return 6
    if snap["quarantined_devices"] > 0:
        return 4
    if snap["pending_approval"]:
        return 2
    if snap["active_alerts"] or snap["suspicious_devices"] > 0:
        return 1
    return 0


# ---------------------------------------------------------------- Model & Session Init
if not (ROOT / "models" / MODEL_FILE).exists():
    st.warning("No trained model found yet. Training one now on synthetic data (about 10–20 seconds)...")
    from train_model import train
    train(ROOT, quiet=True)
    st.rerun()

if "S" not in st.session_state:
    st.session_state.S = DemoSession(ROOT)
    st.session_state.flash = None
    st.session_state.ui_error = None
    st.session_state.active_page = "Overview"
    st.session_state.attack_intensity = 0.70
    st.session_state.allow_sim_approval = False
    st.session_state.pending_run_all = False

S: DemoSession = st.session_state.S
env, agent = S.env, S.agent


# ---------------------------------------------------------------- Confirmation Dialog (Run All Operations)
@st.dialog("Confirm Complete Security Demonstration")
def confirm_run_all_dialog(target_dev: str, intensity_val: float, allow_sim: bool) -> None:
    st.markdown(
        f"You are about to run the complete IoT/IIoT security demonstration targeting **`{target_dev}`** "
        f"(simulated intensity `{intensity_val:.2f}`)."
    )
    st.markdown(
        """
- **Four virtual devices** (`CAM-01`, `TEMP-01`, `PLC-01`, `GW-01`) participate inside an isolated Python simulator.
- **Harmless simulated attack**: no real ransomware will execute and no real files are encrypted.
- **Dummy sandbox files only**: only `.demo` dummy text files inside `demo_sandbox/` are renamed.
- **Virtual-only quarantine**: device isolation operates strictly in memory — zero changes to Windows Firewall or host networking.
"""
    )
    if allow_sim:
        st.warning(
            "**Simulation-only automatic approval is enabled.** Quarantine approval will be recorded as "
            "`SIMULATED_APPROVAL` (virtual sandbox only) and is never presented as a real human approval."
        )
    else:
        st.info(
            "**Manual analyst approval is active (default).** The demonstration will run normal activity, "
            "launch the safe attack, run AI detection, and **pause at Stage 4** for your manual approval."
        )

    c_cancel, c_confirm = st.columns(2)
    with c_cancel:
        if st.button("Cancel", key="dlg_cancel_run_all", use_container_width=True):
            st.rerun()
    with c_confirm:
        if st.button("Confirm and Run", key="dlg_confirm_run_all", type="primary", use_container_width=True):
            st.session_state.pending_run_all = True
            st.rerun()


# ---------------------------------------------------------------- Left Navigation Rail (Single Navigation System)
st.sidebar.markdown(
    f"""
    <div style="display:flex; align-items:center; gap:10px; padding:4px 2px 14px 2px; border-bottom:1px solid {BORDER_COLOR}; margin-bottom:14px;">
        {BRAND_SHIELD_SVG}
        <div>
            <div style="font-family:var(--font-heading); font-size:1.12rem; font-weight:700; color:{PRIMARY_PLUM}; line-height:1.15;">IoTShield AI</div>
            <div style="font-size:0.78rem; color:{TEXT_SECONDARY};">Porcelain Plum</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

for page_name in NAV_ITEMS:
    is_active = st.session_state.active_page == page_name
    if st.sidebar.button(
        page_name,
        key=f"nav_{page_name.lower().replace(' ', '_')}",
        type="primary" if is_active else "secondary",
        use_container_width=True,
    ):
        st.session_state.active_page = page_name
        st.rerun()

st.sidebar.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

# Expandable Environment Settings (No duplicated workflow buttons!)
with st.sidebar.expander("Environment Settings", expanded=False):
    cur_target_idx = DEVICE_IDS.index(S.target_device) if S.target_device in DEVICE_IDS else DEVICE_IDS.index("PLC-01")
    chosen_target = st.selectbox(
        "Target virtual device",
        DEVICE_IDS,
        index=cur_target_idx,
        key="env_target_select",
        help="Default target is PLC-01 (Industrial Controller). Choice persists across reruns.",
    )
    S.set_target_device(chosen_target)

    st.session_state.attack_intensity = st.slider(
        "Attack intensity",
        0.10,
        1.00,
        float(st.session_state.attack_intensity),
        0.05,
        key="env_intensity_slider",
        help="Controls synthetic file-rename and outbound burst intensity inside the sandbox.",
    )

    manual_approval = st.checkbox(
        "Manual analyst approval required",
        value=not agent.policy["auto_quarantine"],
        key="env_manual_approval",
        help="Enabled by default so quarantine requires explicit analyst confirmation. Virtual only.",
    )
    S.set_auto_quarantine(not manual_approval)

st.sidebar.markdown("---")
st.sidebar.caption("Safe classroom sandbox: dummy files only, never real networks or host firewalls.")


# ---------------------------------------------------------------- Authoritative Snapshot & Top Header
snap = S.state_snapshot()
stage = snap["stage"]
active_page = st.session_state.active_page

# Unified Full-Width Application Header (Top row: Branding + Download Report | Hairline | Bottom row: Status Badges)
with st.container(key="pp_unified_header", border=False):
    col_hdr, col_dl = st.columns([3.5, 1.3], vertical_alignment="center")
    with col_hdr:
        st.markdown(render_header_brand(), unsafe_allow_html=True)
    with col_dl:
        st.download_button(
            "Download Report",
            data=build_security_report(S),
            file_name=report_filename(S),
            mime="text/markdown",
            key="header_download_report",
            type="primary",
            icon=":material/download:",
            on_click="ignore",
            width="content",
            help=f"Download Markdown security report for {snap['scenario_id']} without resetting state.",
        )
    st.markdown(render_header_badges(snap["threat_level"]), unsafe_allow_html=True)

st.markdown(render_safe_strip(BANNER, snap["scenario_id"], snap["tick"]), unsafe_allow_html=True)

if st.session_state.get("ui_error"):
    st.error(st.session_state.ui_error)

if st.session_state.get("flash"):
    st.info(st.session_state.flash)

if snap["pending_approval"]:
    st.warning(
        f"High-risk alert: quarantine approval requested for {', '.join(snap['pending_approval'])}. "
        "Review and approve quarantine in the Complete Security Demonstration panel on Overview."
    )


# ==============================================================================
# PAGE 1: OVERVIEW
# ==============================================================================
if active_page == "Overview":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Security Overview</div>
                <div class="pp-page-sub">Real-time posture, complete ransomware demonstration, and virtual device fleet.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Asymmetric Security Posture + Supporting KPIs
    st.markdown(render_posture_and_kpis(snap), unsafe_allow_html=True)

    # Complete Security Demonstration Panel (One-Click + Guided Mode unified on single source of truth)
    st.markdown(
        render_complete_demo_panel(
            snap,
            float(st.session_state.attack_intensity),
            bool(st.session_state.allow_sim_approval),
        ),
        unsafe_allow_html=True,
    )

    # Explicit opt-in for simulation-only automatic quarantine approval (Default: unchecked / Manual approval)
    st.session_state.allow_sim_approval = st.checkbox(
        "Allow simulation-only automatic quarantine approval",
        value=bool(st.session_state.allow_sim_approval),
        key="optin_sim_approval_cb",
        help="Default OFF (manual analyst approval). When checked, one-click mode records SIMULATED_APPROVAL strictly inside the virtual sandbox.",
    )
    if st.session_state.allow_sim_approval:
        st.warning(
            "Simulation-only automatic approval is enabled: quarantine approval will be recorded as "
            "`SIMULATED_APPROVAL` inside the virtual sandbox only — it is not a real human approval."
        )

    # Execute One-Click Workflow if confirmed via dialog (Real execution progress, zero fake sleeps!)
    if st.session_state.get("pending_run_all") and not S.is_running:
        st.session_state.pending_run_all = False
        prog_bar = st.progress(0, text="Starting Complete Security Demonstration...")
        with st.status("Executing Complete Security Demonstration...", expanded=True) as status_box:
            def _on_stage(step_num: int, label: str, detail: str) -> None:
                pct = min(100, int((step_num / 6) * 100))
                prog_bar.progress(pct, text=f"Stage {step_num}/6: {label}")
                st.write(f"**{step_num}. {label}** — {detail}")

            try:
                res = S.run_all_operations(
                    target=S.target_device,
                    severity=float(st.session_state.attack_intensity),
                    allow_simulated_approval=bool(st.session_state.allow_sim_approval),
                    progress_callback=_on_stage,
                )
                if res.get("status") == "COMPLETED":
                    status_box.update(label="Complete Security Demonstration finished and verified.", state="complete")
                    st.session_state.flash = (
                        f"Demonstration completed ({res['scenario_id']}): {res['target']} detected as "
                        f"{res['detection']}, isolated via SIMULATED_APPROVAL, and {res['blocked_events']:,} "
                        "simulated outbound events blocked (0 bytes delivered)."
                    )
                    st.session_state.ui_error = None
                elif res.get("status") == "PAUSED_FOR_APPROVAL":
                    status_box.update(label="Paused at Stage 4 — Manual Analyst Approval Required.", state="complete")
                    st.session_state.flash = (
                        f"AI detected {res['detection']} ({res['risk']} risk) on {res['target']}. "
                        "Manual approval is required — click 'Approve quarantine' below to isolate the device."
                    )
                    st.session_state.ui_error = None
                elif res.get("status") == "ALREADY_RUNNING":
                    status_box.update(label="A demonstration is already running.", state="error")
                else:
                    status_box.update(label="Demonstration stopped without completing all stages.", state="error")
                    st.session_state.ui_error = res.get("error", "Demonstration did not complete.")
            except SandboxViolation:
                logger.exception("SandboxViolation during Run All Operations.")
                status_box.update(label="Demonstration stopped safely (sandbox validation).", state="error")
                st.session_state.ui_error = (
                    "Simulation stopped safely because the virtual device could not be validated inside the "
                    "demonstration sandbox. No external files were modified."
                )
            except Exception:
                logger.exception("Unexpected error during Run All Operations.")
                status_box.update(label="Demonstration stopped safely due to an error.", state="error")
                st.session_state.ui_error = (
                    "The demonstration encountered an unexpected error and stopped safely. Logs were preserved."
                )
        st.rerun()

    # Unified Action Row: Prominent Run All Operations + Single Guided Step + Secondary Controls
    col_runall, col_guided, col_sec1, col_sec2 = st.columns([1.6, 1.8, 1.0, 1.0])
    with col_runall:
        if st.button(
            "Run All Operations",
            key="run_all_ops_btn",
            type="primary",
            icon=":material/play_circle:",
            disabled=S.is_running,
            use_container_width=True,
            help="Launch the complete end-to-end demonstration (opens confirmation dialog).",
        ):
            confirm_run_all_dialog(
                S.target_device,
                float(st.session_state.attack_intensity),
                bool(st.session_state.allow_sim_approval),
            )

    with col_guided:
        skey = stage["key"]
        if skey == "NORMAL_READY":
            if st.button("Start normal activity", key="guided_primary_btn", use_container_width=True):
                if run_safe_action(lambda: S.start_normal(10), "10 normal telemetry windows generated across all 4 virtual devices."):
                    st.rerun()
        elif skey == "ATTACK_READY":
            if st.button("Launch safe attack simulation", key="guided_primary_btn", use_container_width=True):
                tgt = S.target_device
                sev = float(st.session_state.attack_intensity)
                if run_safe_action(
                    lambda: S.launch_attack(tgt, ticks=6, severity=sev),
                    f"Safe ransomware-like simulation launched on {tgt} (dummy sandbox files only).",
                ):
                    st.rerun()
        elif skey == "DETECT_READY":
            if st.button("Run AI detection", key="guided_primary_btn", use_container_width=True):
                if run_safe_action(
                    lambda: S.run_detection(),
                    lambda res: f"AI detector assessed {len(res)} new telemetry windows." if res else "No new telemetry to assess.",
                ):
                    st.rerun()
        elif skey == "APPROVAL_READY":
            if st.button("Approve quarantine", key="guided_primary_btn", type="primary", use_container_width=True):
                if run_safe_action(
                    lambda: S.approve_quarantine(),
                    lambda done: f"Virtual quarantine approved for {', '.join(done)}. Advance the simulation to verify blocking.",
                ):
                    st.rerun()
        elif skey == "VERIFY_READY":
            if st.button(
                "Advance simulation and verify blocked traffic",
                key="guided_primary_btn",
                type="primary",
                use_container_width=True,
            ):
                if run_safe_action(
                    lambda: S.advance(5),
                    "Advanced 5 telemetry windows: subsequent outbound attempts from the quarantined device were blocked.",
                ):
                    st.rerun()
        else:
            st.success("Demonstration completed successfully.")

    with col_sec1:
        if snap["quarantined_devices"] > 0:
            if st.button("Release quarantine", key="sec_release_btn", use_container_width=True):
                if run_safe_action(
                    lambda: [agent.release(d) for d, dev in env.devices.items() if dev.status == "QUARANTINED"],
                    "Virtual quarantine released; normal monitoring resumed.",
                ):
                    st.rerun()

    with col_sec2:
        if snap["tick"] > 0 or stage["index"] > 0:
            if st.button("Reset demonstration", key="sec_reset_btn", use_container_width=True):
                if run_safe_action(
                    lambda: S.reset(),
                    "Demonstration reset cleanly: all 4 devices healthy and dummy files restored.",
                ):
                    st.rerun()

    # Professional Final Completion Summary Screen (Task 4)
    if snap.get("completion_summary"):
        st.markdown(render_completion_summary(snap["completion_summary"]), unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Balanced 2x2 Virtual Device Grid (IoT vs IIoT separation)
    st.markdown("### Connected Virtual Devices")
    st.markdown(render_device_grid(env.devices, env.sim), unsafe_allow_html=True)

    # Live Network Overview + Current Scenario Event Timeline
    st.markdown("### Live Traffic & Current Scenario Events")
    left_ov, right_ov = st.columns([1.65, 1.0])
    with left_ov:
        hist = env.history_df()
        if hist.empty:
            st.info("No network telemetry yet. Click **Start normal activity** above to begin Stage 1.")
        else:
            fig = go.Figure()
            for dev_id in DEVICE_IDS:
                sub = hist[hist.device_id == dev_id]
                if not sub.empty:
                    style = DEVICE_SERIES_STYLE.get(dev_id, dict(color=PRIMARY_PLUM, dash="solid", symbol="circle"))
                    fig.add_trace(go.Scatter(
                        x=sub.tick,
                        y=sub.outbound_bytes,
                        mode="lines+markers",
                        name=dev_id,
                        line=dict(color=style["color"], width=2.4, dash=style["dash"]),
                        marker=dict(size=6, symbol=style["symbol"]),
                    ))
            blocked_df = hist[hist.blocked_bytes > 0]
            if not blocked_df.empty:
                fig.add_trace(go.Scatter(
                    x=blocked_df.tick,
                    y=blocked_df.blocked_bytes,
                    mode="markers",
                    name="Blocked traffic",
                    marker=dict(size=9, color=PRIMARY_PLUM, symbol="x"),
                ))
            for dev_id, atk in env.attacks.items():
                fig.add_vline(
                    x=atk["onset_tick"],
                    line_color=THREAT,
                    line_dash="dot",
                    line_width=2,
                    annotation_text=f"Attack onset ({dev_id})",
                    annotation_font_color=THREAT,
                )
            fig.update_layout(
                title="Simulated outbound traffic by device (5-second windows)",
                xaxis_title="Telemetry window",
                yaxis_title="Outbound bytes",
            )
            show_fig(fig, height=340)

    with right_ov:
        st.markdown(render_event_timeline(snap["current_events"], limit=6), unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: DEVICES
# ==============================================================================
elif active_page == "Devices":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Virtual Devices</div>
                <div class="pp-page-sub">Inspect real-time health, network activity, and isolated sandbox file status.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(render_device_grid(env.devices, env.sim), unsafe_allow_html=True)

    st.markdown("#### Device Telemetry Summary")
    rows = []
    for d in env.devices.values():
        w = d.last_window or {}
        rows.append({
            "Device ID": d.device_id,
            "Device name": d.name,
            "Category": d.device_type,
            "Simulated IP": d.ip,
            "Criticality": d.criticality,
            "Connection": d.status,
            "Security status": d.security_status,
            "Activity": d.activity,
            "Delivered connections": w.get("delivered_connections", 0),
            "Blocked connections": w.get("blocked_connections", 0),
        })
    show_df(pd.DataFrame(rows))

    st.markdown("#### Isolated Sandbox File Status (Dummy Files Only)")
    s_rows = []
    for dev_id in env.devices:
        st_info = env.sim.status(dev_id)
        s_rows.append({
            "Device ID": dev_id,
            "Healthy dummy files (.demo)": st_info["dummy_files"],
            "Renamed demo files (.locked_demo)": st_info["locked_demo_files"],
            "Simulated ransom note": "Present" if st_info["note_present"] else "None",
            "Encryption": "None — readable plain text only",
        })
    show_df(pd.DataFrame(s_rows))


# ==============================================================================
# PAGE 3: NETWORK TRAFFIC
# ==============================================================================
elif active_page == "Network Traffic":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Network Traffic</div>
                <div class="pp-page-sub">Compare baseline IoT/IIoT behaviour against simulated attack spikes and blocked outbound attempts.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hist = env.history_df()
    if hist.empty:
        st.info("No telemetry recorded yet for the current scenario. Start Stage 1 on **Overview**.")
    else:
        metric_labels = {
            "outbound_bytes": "Outbound bytes attempted",
            "delivered_bytes": "Outbound bytes delivered to virtual network",
            "connection_count": "Connection count (per 5s window)",
            "file_rename_rate": "File rename rate (files / min)",
            "file_write_rate": "File write rate (writes / min)",
            "failed_connection_rate": "Failed connection ratio (0–1)",
            "cpu_usage": "Simulated CPU usage (%)",
            "device_activity_score": "Composite activity score",
        }
        selected_metric = st.selectbox(
            "Select telemetry metric",
            options=list(metric_labels.keys()),
            format_func=lambda k: metric_labels[k],
            key="traffic_metric_select",
        )

        fig = go.Figure()
        for dev_id in DEVICE_IDS:
            sub = hist[hist.device_id == dev_id]
            if not sub.empty:
                style = DEVICE_SERIES_STYLE.get(dev_id, dict(color=PRIMARY_PLUM, dash="solid", symbol="circle"))
                fig.add_trace(go.Scatter(
                    x=sub.tick,
                    y=sub[selected_metric],
                    mode="lines+markers",
                    name=dev_id,
                    line=dict(color=style["color"], width=2.5, dash=style["dash"]),
                    marker=dict(size=6, symbol=style["symbol"]),
                ))

        for dev_id, atk in env.attacks.items():
            fig.add_vline(
                x=atk["onset_tick"],
                line_color=THREAT,
                line_dash="dot",
                line_width=2,
                annotation_text=f"Attack onset: {dev_id}",
                annotation_font_color=THREAT,
            )

        fig.update_layout(
            title=f"{metric_labels[selected_metric]} — Synthetic Simulation",
            xaxis_title="Telemetry window (5 simulated seconds each)",
            yaxis_title=metric_labels[selected_metric],
        )
        show_fig(fig, height=400)

        st.markdown("#### Latest Window Comparison")
        last = hist[hist.tick == hist.tick.max()]
        show_df(last[[
            "tick",
            "device_id",
            "connection_count",
            "outbound_bytes",
            "delivered_bytes",
            "blocked_connections",
            "file_rename_rate",
            "failed_connection_rate",
        ]])


# ==============================================================================
# PAGE 4: AI DETECTION
# ==============================================================================
elif active_page == "AI Detection":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">AI Detection</div>
                <div class="pp-page-sub">Random Forest classification verdict and feature-level baseline deviation evidence.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    latest = snap["latest_detections"]
    if not latest:
        st.info("No AI detection verdicts yet in this scenario. Complete Stages 1–3 on **Overview**.")
    else:
        default_dev = next(
            (d for d, a in latest.items() if a["predicted_class"] == "RANSOMWARE_LIKE"),
            S.target_device if S.target_device in latest else list(latest)[0],
        )
        dev_list = list(latest.keys())
        chosen_dev = st.selectbox(
            "Inspect device verdict",
            options=dev_list,
            index=dev_list.index(default_dev),
            key="ai_device_select",
        )
        assessment = latest[chosen_dev]

        st.markdown(render_detection_panel(chosen_dev, assessment), unsafe_allow_html=True)
        st.caption(
            "Synthetic simulation notice: Probabilities are Random Forest outputs on synthetic classroom telemetry, "
            "not real-world malware detection accuracy."
        )

        top_feats = assessment.get("top_features") or []
        col_tbl, col_bar = st.columns([1.35, 1.0])
        with col_tbl:
            st.markdown("#### Supporting Feature Evidence")
            if top_feats:
                ev_rows = [
                    {
                        "Feature": f["feature"].replace("_", " ").capitalize(),
                        "Observed value": round(float(f["value"]), 3),
                        "Normal baseline": round(float(f["normal_mean"]), 3),
                        "Deviation (z-score)": f"+{f['z_score']:.2f}σ",
                        "Model importance": f"{f['importance']*100:.1f}%",
                    }
                    for f in top_feats
                ]
                show_df(pd.DataFrame(ev_rows))
            else:
                st.success("All monitored features remained within normal operating baseline for this window.")

        with col_bar:
            st.markdown("#### Feature Contribution Ranking")
            if top_feats:
                fdf = pd.DataFrame(top_feats).sort_values("rank_score")
                fig_attr = go.Figure(go.Bar(
                    x=fdf["rank_score"],
                    y=[s.replace("_", " ").capitalize() for s in fdf["feature"]],
                    orientation="h",
                    marker_color=ROSE_ACCENT if assessment["predicted_class"] == "RANSOMWARE_LIKE" else SUCCESS,
                    text=[f"{v:.2f}" for v in fdf["rank_score"]],
                    textposition="outside",
                ))
                fig_attr.update_layout(
                    title="Importance × Baseline Deviation (Heuristic)",
                    xaxis_title="Contribution score",
                )
                show_fig(fig_attr, height=270)
            else:
                st.caption("Contribution bars appear when features rise above normal baseline.")

        st.markdown("#### All Devices — Latest Classification")
        summary_rows = [
            {
                "Device": d_id,
                "Detection": a["predicted_class"],
                "Probability": f"{a['probability']*100:.1f}% ({a['probability']:.3f})",
                "Risk": a["risk_level"],
                "Window": a["tick"],
                "Inference (ms)": f"{a['inference_ms']:.2f}",
                "Timestamp": format_timestamp(a["timestamp"]),
            }
            for d_id, a in latest.items()
        ]
        show_df(pd.DataFrame(summary_rows))

        if SHOW_TECHNICAL_DETAILS:
            with st.expander("Advanced technical evidence", expanded=False):
                st.json(assessment)


# ==============================================================================
# PAGE 5: PREVENTION CENTER
# ==============================================================================
elif active_page == "Prevention Center":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Prevention Center</div>
                <div class="pp-page-sub">Virtual quarantine approvals and verified outbound traffic blocking evidence.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(render_prevention_sequence(prevention_step_index(snap)), unsafe_allow_html=True)

    q_devs = [d for d in env.devices.values() if d.status == "QUARANTINED"]
    rh = env.network.response_history
    affected_str = ", ".join(d.device_id for d in q_devs) if q_devs else "None"
    approval_status = "Quarantined" if q_devs else ("Pending" if snap["pending_approval"] else "Monitoring")
    approval_sub = (
        "Approved · virtual & reversible"
        if q_devs
        else ("Analyst approval required" if snap["pending_approval"] else "No pending request")
    )
    approval_color = AI_VIOLET if q_devs else (WARNING if snap["pending_approval"] else SUCCESS)
    last_action = rh[-1]["action"].title() if rh else "None yet"
    last_sub = f"{rh[-1]['device_id']} · {format_timestamp(rh[-1]['timestamp'])}" if rh else "No actions recorded"

    pop_set = {2, 3} if snap["blocked_events"] > 0 else set()
    st.markdown(
        render_metric_strip(
            [
                ("Affected device", affected_str, "Isolated in virtual gateway", AI_VIOLET if q_devs else TEXT_MAIN),
                ("Quarantine status", approval_status, approval_sub, approval_color),
                ("Blocked events", f"{snap['blocked_events']:,}", "Rejected outbound attempts", CHAMPAGNE),
                ("Blocked bytes", f"{snap['blocked_bytes']:,.0f} B", "0 bytes delivered while isolated", PRIMARY_PLUM),
                ("Last response", last_action, last_sub, TEXT_MAIN),
            ],
            pop_indices=pop_set,
        ),
        unsafe_allow_html=True,
    )

    if q_devs and snap["blocked_events"] == 0:
        st.info(
            "Device is quarantined. No post-quarantine traffic attempts have been recorded yet. "
            "Advance the simulation on **Overview** to verify blocking."
        )
    elif q_devs and snap["blocked_events"] > 0:
        st.success(
            f"Prevention verified: virtual gateway rejected **{snap['blocked_events']:,}** outbound connection attempts "
            f"(**{snap['blocked_bytes']:,.0f} bytes**) from **{affected_str}**, with **0 bytes** delivered."
        )

    col_rh, col_bl = st.columns([1.15, 1.0])
    with col_rh:
        st.markdown("#### Response Action History")
        if rh:
            rh_df = pd.DataFrame(rh).copy()
            rh_df["timestamp"] = rh_df["timestamp"].apply(format_timestamp)
            show_df(rh_df[["timestamp", "tick", "device_id", "action", "approved_by", "reason", "reversible"]])
        else:
            st.caption("No quarantine or release actions in this scenario yet.")

    with col_bl:
        st.markdown("#### Virtual Gateway Blocked Traffic Ledger")
        blocked_hist = [r for r in env.history if r.get("blocked_connections", 0) > 0]
        if blocked_hist:
            b_df = pd.DataFrame(blocked_hist)[
                ["tick", "device_id", "blocked_connections", "blocked_bytes", "delivered_bytes"]
            ].tail(15)
            show_df(b_df)
        else:
            st.caption("No blocked traffic windows recorded in this scenario yet.")


# ==============================================================================
# PAGE 6: SECURITY EVENTS
# ==============================================================================
elif active_page == "Security Events":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Security Events</div>
                <div class="pp-page-sub">Human-readable security event history for the active simulation scenario.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show_history = st.toggle(
        f"Include archived events from previous scenarios ({len(snap['historical_events'])} archived)",
        value=False,
        key="events_include_history",
    )
    source_events = (
        snap["historical_events"] + snap["current_events"] if show_history else snap["current_events"]
    )

    if not source_events:
        st.info("No security events recorded yet.")
    else:
        f1, f2, f3 = st.columns([1.4, 1.0, 1.0])
        with f1:
            query = st.text_input("Search events", placeholder="e.g. PLC-01, BLOCKED, QUARANTINED...", key="ev_search")
        with f2:
            sev_filter = st.selectbox("Severity", ["All", "Info", "Warning", "Alert", "Blocked"], key="ev_sev")
        with f3:
            dev_opts = ["All"] + sorted({str(e.get("device_id", "-")) for e in source_events})
            dev_filter = st.selectbox("Device", dev_opts, key="ev_dev")

        rows = []
        for e in reversed(source_events):
            row = normalize_event_row(e)
            if sev_filter != "All" and row["Severity"] != sev_filter:
                continue
            if dev_filter != "All" and row["Device"] != dev_filter:
                continue
            if query and query.lower() not in " ".join(str(v) for v in row.values()).lower():
                continue
            rows.append(row)

        scope_label = "all scenarios" if show_history else f"current scenario ({snap['scenario_id']})"
        st.caption(f"Showing {len(rows)} event(s) from {scope_label} (newest first).")
        ev_df = pd.DataFrame(rows)
        show_df(ev_df)

        with st.expander("Export filtered event log (CSV)", expanded=False):
            csv_data = ev_df.to_csv(index=False) if not ev_df.empty else "Time,Window,Device,Severity,Event type,Description,Action taken\n"
            st.download_button(
                "Download Event Log (CSV)",
                data=csv_data,
                file_name=f"IoTShield_AI_Events_{snap['scenario_id']}.csv",
                mime="text/csv",
                key="ev_export_csv",
                icon=":material/table_view:",
                on_click="ignore",
                width="content",
            )

        if SHOW_TECHNICAL_DETAILS:
            with st.expander("Advanced technical evidence", expanded=False):
                st.json(source_events[-15:])


# ==============================================================================
# PAGE 7: MODEL EVALUATION
# ==============================================================================
elif active_page == "Model Evaluation":
    st.markdown(
        """
        <div class="pp-page-head">
            <div>
                <div class="pp-page-title">Model Evaluation</div>
                <div class="pp-page-sub">Held-out synthetic test performance, confusion matrix, and Random Forest feature importance.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    mpath = ROOT / "evidence" / "evaluation" / "metrics.json"
    if not mpath.exists():
        st.info("Run `python train_model.py` to generate synthetic model evaluation results.")
    else:
        m = json.loads(mpath.read_text(encoding="utf-8"))
        t = m["metrics"]["test"]

        st.warning(f"Synthetic simulation results only: {m['note']}")

        st.markdown(
            render_metric_strip([
                ("Accuracy", f"{t['accuracy']*100:.2f}%", "Held-out synthetic test", SUCCESS),
                ("Precision", f"{t['precision']*100:.2f}%", "Positive predictive value", SUCCESS),
                ("Recall", f"{t['recall']*100:.2f}%", "Attack detection rate", SUCCESS),
                ("F1-score", f"{t['f1']*100:.2f}%", "Harmonic mean", PRIMARY_PLUM),
                ("False-positive rate", f"{t['false_positive_rate']*100:.2f}%", f"{t['fp']} false alarms", WARNING),
                ("False-negative rate", f"{t['false_negative_rate']*100:.2f}%", f"{t['fn']} missed windows", THREAT),
                ("Inference time", f"{m['inference_ms_single_window_mean']:.2f} ms", "Mean per window (CPU)", CHAMPAGNE),
            ]),
            unsafe_allow_html=True,
        )

        left_m, right_m = st.columns(2)
        with left_m:
            cm = [[t["tn"], t["fp"]], [t["fn"], t["tp"]]]
            cm_text = [[f"TN: {t['tn']}", f"FP: {t['fp']}"], [f"FN: {t['fn']}", f"TP: {t['tp']}"]]
            fig_cm = go.Figure(go.Heatmap(
                z=cm,
                x=["NORMAL", "RANSOMWARE_LIKE"],
                y=["NORMAL", "RANSOMWARE_LIKE"],
                text=cm_text,
                texttemplate="%{text}",
                textfont=dict(size=14),
                colorscale=[[0.0, "#F7F4F8"], [0.45, "#DFC8D6"], [1.0, "#68435F"]],
                showscale=True,
            ))
            fig_cm.update_layout(
                title="Confusion Matrix (Held-out Synthetic Test Set)",
                xaxis_title="Predicted class",
                yaxis_title="Actual class",
                yaxis_autorange="reversed",
            )
            show_fig(fig_cm, height=370)

        with right_m:
            fi = pd.Series(m["feature_importance"]).sort_values()
            fig_fi = go.Figure(go.Bar(
                x=fi.values,
                y=[k.replace("_", " ").capitalize() for k in fi.index],
                orientation="h",
                marker_color=ROSE_ACCENT,
                text=[f"{v*100:.1f}%" for v in fi.values],
                textposition="outside",
            ))
            fig_fi.update_layout(
                title="Random Forest Feature Importance (Gini)",
                xaxis_title="Relative importance",
                xaxis=dict(range=[0, max(fi.values) * 1.22]),
            )
            show_fig(fig_fi, height=370)

        st.caption(
            f"Scenario-level split (zero leakage): Train {m['sizes']['train']['windows']} windows, "
            f"Validation {m['sizes']['val']['windows']} windows, Test {m['sizes']['test']['windows']} windows. "
            f"Grouped 5-fold cross-validation F1 (train+val): **{m['grouped_cv_f1_train_plus_val']['mean']:.4f}** "
            f"(±{m['grouped_cv_f1_train_plus_val']['std']:.4f})."
        )
