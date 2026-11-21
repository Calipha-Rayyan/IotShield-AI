"""IoTShield AI — Porcelain Plum Design System, Formatters & Reusable UI Components.
Visual Identity: PORCELAIN PLUM — "Intelligence with elegance."
Light-first, WCAG 2.2 AA compliant, vector SVG iconography, state-driven motion.
"""
from __future__ import annotations

from html import escape
from typing import Any

# ==============================================================================
# APPROVED PORCELAIN PLUM DESIGN TOKENS
# ==============================================================================

BG_MAIN = "#F7F4F8"            # Main application background
SURFACE_MAIN = "#FFFFFF"       # Primary cards & panels
SURFACE_SECONDARY = "#F0EAF3"  # Left navigation rail & secondary surfaces
SOFT_HIGHLIGHT = "#F5EDF2"     # Subtle highlight strips & hover surfaces

PRIMARY_PLUM = "#68435F"       # Primary actions & branding
PRIMARY_HOVER = "#54354F"      # Primary hover state
ROSE_ACCENT = "#B45D7A"        # Key product highlights & attack series
AI_VIOLET = "#7566A8"          # AI information & quarantine containment
CHAMPAGNE = "#8A6528"          # Selected statistics (blocked events, latency)

TEXT_MAIN = "#3D3342"          # Headings & body text (dark plum, never black)
TEXT_SECONDARY = "#746A78"     # Supporting labels & metadata
BORDER_COLOR = "#E3DCE6"       # Crisp panel & table borders

SUCCESS = "#26765F"            # Healthy & verified states
WARNING = "#8F5D17"            # Warning & approval-required states
THREAT = "#AC3C53"             # Critical ransomware-like alerts
INFO = "#3D7590"               # Informational status

# Soft semantic backgrounds (restrained, crisp contrast >= 4.5:1)
BG_SUCCESS = "#EAF5F1"
BORDER_SUCCESS = "#B6DCD0"
BG_WARNING = "#FDF5E6"
BORDER_WARNING = "#EAD09C"
BG_THREAT = "#FCECEF"
BORDER_THREAT = "#E6B5C0"
BG_VIOLET = "#F1EEF8"
BORDER_VIOLET = "#CFC6E6"
BG_INFO = "#EAF3F7"
BORDER_INFO = "#BBD5E2"

# ==============================================================================
# VECTOR SVG ICONOGRAPHY (Zero structural emojis)
# ==============================================================================

BRAND_SHIELD_SVG = """
<svg width="40" height="40" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect width="42" height="42" rx="11" fill="#68435F"/>
  <path d="M21 7.5L32 12V20.6C32 27.6 27.3 33.4 21 35.5C14.7 33.4 10 27.6 10 20.6V12L21 7.5Z"
        fill="#FFFFFF" fill-opacity="0.14" stroke="#F5EDF2" stroke-width="1.8" stroke-linejoin="round"/>
  <path d="M14.5 21.5H17.8L19.8 17L22.3 25L24.2 21.5H27.5"
        stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="21" cy="12.5" r="1.6" fill="#E6B5C0"/>
</svg>
""".strip()

ICONS: dict[str, str] = {
    "camera": (
        '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>'
    ),
    "sensor": (
        '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg>'
    ),
    "plc": (
        '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/>'
        '<line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/>'
        '<line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/>'
        '<line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/>'
        '<line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>'
    ),
    "gateway": (
        '<svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="2" y="14" width="20" height="7" rx="2"/><path d="M6 17.5h.01M10 17.5h.01"/>'
        '<path d="M12 14V9"/><path d="M8.5 7.5a5 5 0 0 1 7 0"/><path d="M5.5 4.5a9.5 9.5 0 0 1 13 0"/></svg>'
    ),
    "check": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>'
    ),
    "alert": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
    ),
    "shield": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
    ),
    "lock": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>'
    ),
    "pulse": (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>'
    ),
}

DEVICE_ICON_MAP = {
    "CAM-01": "camera",
    "TEMP-01": "sensor",
    "PLC-01": "plc",
    "GW-01": "gateway",
}


def _clean_html(raw: str) -> str:
    """Flatten multi-line HTML so Streamlit Markdown never treats indented lines as code blocks."""
    return " ".join(line.strip() for line in raw.splitlines() if line.strip())


# ==============================================================================
# CENTRALIZED FORMATTERS & STATUS MAPPING (Phase 14)
# ==============================================================================

def format_timestamp(ts: str | None) -> str:
    """Format ISO timestamp into clean HH:MM:SS for UI tables and timelines."""
    if not ts:
        return "-"
    s = str(ts)
    return s.split("T")[-1][:8] if "T" in s else s[:8]


def format_full_timestamp(ts: str | None) -> str:
    if not ts:
        return "-"
    s = str(ts)
    return s.replace("T", " ")[:19] if "T" in s else s[:19]


def threat_meta(level: str) -> tuple[str, str, str]:
    """Single source of truth mapping threat level -> (pill_class, display_label, icon_key)."""
    mapping = {
        "LOW": ("pp-pill-success", "Threat: Low", "check"),
        "MEDIUM": ("pp-pill-warning", "Threat: Medium", "alert"),
        "HIGH": ("pp-pill-threat", "Threat: High", "alert"),
        "CONTAINED": ("pp-pill-violet", "Contained", "lock"),
    }
    return mapping.get(level, ("pp-pill-info", f"Threat: {level.title()}", "shield"))


def normalize_event_row(ev: dict) -> dict:
    """Map a backend EventLog dict to a clean, human-readable UI row without internal metadata."""
    cat = str(ev.get("category", "INFO"))
    sev = str(ev.get("severity", "INFO"))
    dev_id = str(ev.get("device_id", "-"))
    msg = str(ev.get("message", ""))
    action = str(
        ev.get(
            "action_taken",
            "Blocked by quarantine" if cat == "BLOCKED" else ("Quarantine" if cat == "RESPONSE" else "Logged"),
        )
    )
    if cat == "BLOCKED":
        norm_sev = "Blocked"
    elif sev == "HIGH" or cat in ("ALERT", "ATTACK"):
        norm_sev = "Alert"
    elif sev == "MEDIUM" or cat == "APPROVAL":
        norm_sev = "Warning"
    else:
        norm_sev = "Info"

    return {
        "Time": format_timestamp(ev.get("timestamp")),
        "Window": ev.get("tick", "-"),
        "Device": dev_id,
        "Severity": norm_sev,
        "Event type": cat,
        "Description": msg,
        "Action taken": action,
    }


# ==============================================================================
# GLOBAL PORCELAIN PLUM STYLESHEET
# ==============================================================================

def get_css() -> str:
    """Return the refined Porcelain Plum light stylesheet with state-driven animations."""
    return f"""
<style>
:root {{
    --bg-main: {BG_MAIN};
    --surface-main: {SURFACE_MAIN};
    --surface-secondary: {SURFACE_SECONDARY};
    --soft-highlight: {SOFT_HIGHLIGHT};
    --plum-primary: {PRIMARY_PLUM};
    --plum-hover: {PRIMARY_HOVER};
    --rose-accent: {ROSE_ACCENT};
    --ai-violet: {AI_VIOLET};
    --champagne: {CHAMPAGNE};
    --text-main: {TEXT_MAIN};
    --text-secondary: {TEXT_SECONDARY};
    --border-color: {BORDER_COLOR};
    --success: {SUCCESS};
    --warning: {WARNING};
    --threat: {THREAT};
    --info: {INFO};

    --font-heading: 'Aptos Display', 'Segoe UI Semibold', 'Segoe UI', system-ui, -apple-system, sans-serif;
    --font-body: 'Aptos', 'Segoe UI', system-ui, -apple-system, sans-serif;
    --font-mono: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
}}

/* Base Light Canvas */
.stApp {{
    background-color: var(--bg-main) !important;
    color: var(--text-main) !important;
    font-family: var(--font-body) !important;
    overflow-x: hidden;
}}

.block-container {{
    padding-top: 3.25rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1360px !important;
}}

header[data-testid="stHeader"] {{
    background-color: transparent !important;
    background: transparent !important;
    backdrop-filter: none !important;
    -webkit-backdrop-filter: none !important;
    box-shadow: none !important;
    height: 2.5rem !important;
    pointer-events: none;
}}

header[data-testid="stHeader"] * {{
    pointer-events: auto;
}}

/* Left Navigation Rail / Sidebar */
section[data-testid="stSidebar"] {{
    background-color: var(--surface-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}}

section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {{
    color: var(--text-main) !important;
}}

/* Sidebar Left Navigation Rail Buttons */
section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] button[kind="secondary"] {{
    background-color: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.55rem 0.9rem !important;
    min-height: 2.5rem !important;
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    color: var(--text-main) !important;
    box-shadow: none !important;
    transition: background-color 160ms ease, color 160ms ease, border-color 160ms ease !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover {{
    background-color: var(--surface-main) !important;
    border-color: var(--border-color) !important;
    color: var(--plum-primary) !important;
}}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"],
section[data-testid="stSidebar"] button[kind="primary"] {{
    background-color: var(--plum-primary) !important;
    border: 1px solid var(--plum-primary) !important;
    border-left: 4px solid var(--rose-accent) !important;
    border-radius: 10px !important;
    justify-content: flex-start !important;
    text-align: left !important;
    padding: 0.55rem 0.9rem !important;
    min-height: 2.5rem !important;
    font-size: 0.94rem !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(104, 67, 95, 0.16) !important;
}}

/* Typography */
h1, h2, h3, h4 {{
    font-family: var(--font-heading) !important;
    color: var(--text-main) !important;
    letter-spacing: -0.015em;
}}

p, li, label {{
    color: var(--text-main);
    font-size: 0.95rem;
    line-height: 1.5;
}}

/* Main Workspace Buttons */
button[data-testid="stBaseButton-secondary"],
button[kind="secondary"] {{
    background-color: var(--surface-main) !important;
    color: var(--plum-primary) !important;
    border: 1.5px solid #D6C9D8 !important;
    border-radius: 10px !important;
    font-family: var(--font-body) !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    min-height: 2.65rem !important;
    padding: 0.45rem 1rem !important;
    transition: background-color 180ms ease, border-color 180ms ease, box-shadow 180ms ease !important;
    box-shadow: 0 1px 2px rgba(61, 51, 66, 0.05) !important;
}}

button[data-testid="stBaseButton-secondary"]:hover,
button[kind="secondary"]:hover {{
    background-color: var(--soft-highlight) !important;
    border-color: var(--rose-accent) !important;
    color: var(--plum-hover) !important;
    box-shadow: 0 3px 10px rgba(104, 67, 95, 0.12) !important;
}}

button[kind="primary"],
button[data-testid="stBaseButton-primary"] {{
    background-color: var(--plum-primary) !important;
    color: #FFFFFF !important;
    border: 1.5px solid var(--plum-primary) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    min-height: 2.75rem !important;
    padding: 0.5rem 1.15rem !important;
    box-shadow: 0 3px 12px rgba(104, 67, 95, 0.2) !important;
    transition: background-color 180ms ease, transform 140ms ease, box-shadow 180ms ease !important;
}}

button[kind="primary"] *,
button[data-testid="stBaseButton-primary"] * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}}

button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover {{
    background-color: var(--plum-hover) !important;
    border-color: var(--plum-hover) !important;
    box-shadow: 0 5px 16px rgba(84, 53, 79, 0.28) !important;
}}

button:focus-visible {{
    outline: 2.5px solid var(--rose-accent) !important;
    outline-offset: 2px !important;
}}

/* DataFrames & Expanders */
div[data-testid="stDataFrame"] {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    overflow: hidden;
}}

details[data-testid="stExpander"] {{
    background-color: var(--surface-main) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
}}

/* ==========================================================================
   STATE-DRIVEN MOTION (Phase 12)
   ========================================================================== */

@keyframes ppPageReveal {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes ppAlertSlide {{
    from {{ opacity: 0; transform: translateX(-8px); }}
    to   {{ opacity: 1; transform: translateX(0); }}
}}

@keyframes ppCountPop {{
    0%   {{ transform: scale(0.92); opacity: 0.7; }}
    60%  {{ transform: scale(1.04); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}

.pp-reveal {{
    animation: ppPageReveal 300ms cubic-bezier(0.16, 1, 0.3, 1) both;
}}

.pp-alert-reveal {{
    animation: ppAlertSlide 280ms cubic-bezier(0.16, 1, 0.3, 1) both;
}}

.pp-count-pop {{
    animation: ppCountPop 380ms cubic-bezier(0.16, 1, 0.3, 1) both;
}}

/* ==========================================================================
   PORCELAIN PLUM COMPONENTS
   ========================================================================== */

.pp-header {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-top: 3.5px solid var(--plum-primary);
    border-radius: 14px;
    padding: 16px 22px;
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
    box-shadow: 0 2px 10px rgba(61, 51, 66, 0.04);
}}

.pp-brand-wrap {{
    display: flex;
    align-items: center;
    gap: 14px;
}}

.pp-brand-title {{
    font-family: var(--font-heading);
    font-size: 1.85rem;
    font-weight: 700;
    color: var(--plum-primary);
    line-height: 1.15;
}}

.pp-brand-sub {{
    font-size: 0.93rem;
    color: var(--text-secondary);
    margin-top: 2px;
}}

.pp-header-badges {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}}

/* Semantic Pills — Never wrap mid-word */
.pp-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.82rem;
    font-weight: 600;
    white-space: nowrap;
    line-height: 1.2;
    border: 1px solid transparent;
}}

.pp-pill-success {{ background-color: {BG_SUCCESS}; color: {SUCCESS}; border-color: {BORDER_SUCCESS}; }}
.pp-pill-warning {{ background-color: {BG_WARNING}; color: {WARNING}; border-color: {BORDER_WARNING}; }}
.pp-pill-threat  {{ background-color: {BG_THREAT};  color: {THREAT};  border-color: {BORDER_THREAT}; }}
.pp-pill-violet  {{ background-color: {BG_VIOLET};  color: {AI_VIOLET}; border-color: {BORDER_VIOLET}; }}
.pp-pill-info    {{ background-color: {BG_INFO};    color: {INFO};    border-color: {BORDER_INFO}; }}
.pp-pill-plum    {{ background-color: {SOFT_HIGHLIGHT}; color: {PRIMARY_PLUM}; border-color: #DECBD6; }}

/* Safe Simulation Strip */
.pp-safe-strip {{
    background-color: var(--soft-highlight);
    border: 1px solid #E2D2DC;
    border-radius: 10px;
    padding: 9px 16px;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
    color: var(--plum-primary);
    font-size: 0.88rem;
}}

/* Page Heading */
.pp-page-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    flex-wrap: wrap;
    gap: 10px;
    margin: 2px 0 16px 0;
}}

.pp-page-title {{
    font-family: var(--font-heading);
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-main);
    line-height: 1.2;
}}

.pp-page-sub {{
    font-size: 0.94rem;
    color: var(--text-secondary);
    margin-top: 3px;
}}

/* Asymmetric Security Posture + Supporting KPI Grid */
.pp-posture-grid {{
    display: grid;
    grid-template-columns: minmax(280px, 1.35fr) minmax(320px, 2fr);
    gap: 16px;
    margin-bottom: 18px;
}}

@media (max-width: 980px) {{
    .pp-posture-grid {{ grid-template-columns: 1fr; }}
}}

.pp-hero-posture {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-left: 5px solid {SUCCESS};
    border-radius: 14px;
    padding: 20px 22px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(61, 51, 66, 0.04);
    transition: border-color 240ms ease, background-color 240ms ease;
}}

.pp-hero-posture.posture-high {{ border-left-color: {THREAT}; background-color: #FFF9FA; }}
.pp-hero-posture.posture-medium {{ border-left-color: {WARNING}; background-color: #FFFDF8; }}
.pp-hero-posture.posture-contained {{ border-left-color: {AI_VIOLET}; background-color: #FAF9FD; }}

.pp-kpis-2x2 {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}}

.pp-kpi-card {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px 18px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(61, 51, 66, 0.04);
    transition: border-color 180ms ease, box-shadow 180ms ease;
}}

.pp-kpi-card:hover {{
    border-color: #D2C3D6;
    box-shadow: 0 4px 14px rgba(104, 67, 95, 0.08);
}}

.pp-kpi-label {{
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 6px;
}}

.pp-kpi-value {{
    font-family: var(--font-heading);
    font-size: 1.95rem;
    font-weight: 700;
    line-height: 1.15;
    color: var(--text-main);
    white-space: nowrap;
}}

.pp-kpi-meta {{
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 4px;
}}

/* Guided 5-Stage Demonstration Panel */
.pp-guided-card {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-left: 4px solid var(--plum-primary);
    border-radius: 14px;
    padding: 18px 22px 16px 22px;
    margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(61, 51, 66, 0.04);
}}

.pp-stepper {{
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin-top: 12px;
}}

.pp-stepper-6 {{
    display: grid;
    grid-template-columns: repeat(6, minmax(0, 1fr));
    gap: 8px;
    margin-top: 10px;
}}

@media (max-width: 1020px) {{
    .pp-stepper, .pp-stepper-6 {{
        grid-template-columns: repeat(auto-fit, minmax(145px, 1fr));
    }}
}}

.pp-step {{
    background-color: var(--bg-main);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 10px 12px;
    display: flex;
    align-items: center;
    gap: 9px;
    transition: background-color 220ms ease, border-color 220ms ease;
}}

.pp-step-done {{ background-color: {BG_SUCCESS}; border-color: {BORDER_SUCCESS}; }}
.pp-step-active {{
    background-color: {BG_VIOLET};
    border: 1.5px solid var(--plum-primary);
    box-shadow: 0 2px 10px rgba(104, 67, 95, 0.12);
}}

.pp-step-num {{
    width: 24px;
    height: 24px;
    min-width: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    background-color: #E3DCE6;
    color: var(--text-main);
}}

.pp-step-done .pp-step-num {{ background-color: {SUCCESS}; color: #FFFFFF; }}
.pp-step-active .pp-step-num {{ background-color: var(--plum-primary); color: #FFFFFF; }}

.pp-step-title {{
    font-size: 0.83rem;
    font-weight: 600;
    color: var(--text-main);
    line-height: 1.25;
}}

/* Balanced 2x2 Device Cards */
.pp-device-section-tag {{
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin: 10px 0 8px 0;
}}

.pp-device-grid {{
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
    margin-bottom: 14px;
}}

@media (max-width: 780px) {{
    .pp-device-grid {{ grid-template-columns: 1fr; }}
}}

.pp-device-card {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-top: 3.5px solid {SUCCESS};
    border-radius: 14px;
    padding: 16px 18px;
    box-shadow: 0 2px 8px rgba(61, 51, 66, 0.04);
    transition: border-color 220ms ease, box-shadow 200ms ease, background-color 220ms ease;
}}

.pp-device-card:hover {{ box-shadow: 0 5px 16px rgba(104, 67, 95, 0.08); }}
.pp-device-card.dev-suspicious {{ border-top-color: {THREAT}; background-color: #FFF9FA; }}
.pp-device-card.dev-quarantined {{ border-top-color: {AI_VIOLET}; background-color: #FAF9FD; }}

.pp-device-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}}

.pp-device-id-group {{
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}}

.pp-device-icon {{
    width: 36px;
    height: 36px;
    min-width: 36px;
    border-radius: 9px;
    background-color: var(--soft-highlight);
    color: var(--plum-primary);
    display: flex;
    align-items: center;
    justify-content: center;
}}

.pp-device-id {{
    font-family: var(--font-mono);
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
    white-space: nowrap;
}}

.pp-device-name {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-main);
}}

.pp-device-sub {{
    font-size: 0.83rem;
    color: var(--text-secondary);
    margin-bottom: 10px;
}}

.pp-kv-list {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px 14px;
    padding-top: 10px;
    border-top: 1px solid var(--border-color);
}}

.pp-kv-label {{ font-size: 0.78rem; color: var(--text-secondary); }}
.pp-kv-val {{
    font-family: var(--font-mono);
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-main);
    white-space: nowrap;
}}

/* AI Detection Showcase */
.pp-ai-hero {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-left: 5px solid var(--ai-violet);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(61, 51, 66, 0.05);
}}

.pp-ai-hero.ai-threat {{ border-left-color: {THREAT}; background-color: #FFF9FA; }}
.pp-ai-hero.ai-healthy {{ border-left-color: {SUCCESS}; }}

.pp-ai-metrics {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(175px, 1fr));
    gap: 12px;
    margin-top: 14px;
}}

.pp-ai-tile {{
    background-color: var(--bg-main);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 12px 14px;
}}

/* Metric Strip & Timeline */
.pp-metric-strip {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}}

.pp-timeline-card {{
    background-color: var(--surface-main);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px 18px;
    height: 100%;
    box-shadow: 0 2px 8px rgba(61, 51, 66, 0.04);
}}

.pp-timeline-item {{
    display: flex;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid #F0EAF3;
    align-items: flex-start;
}}
.pp-timeline-item:last-child {{ border-bottom: none; }}

.pp-dot {{
    width: 9px;
    height: 9px;
    min-width: 9px;
    border-radius: 50%;
    margin-top: 6px;
}}

/* Unified Top Header Container (Scoped to explicit Streamlit container key) */
.st-key-pp_unified_header {{
    background-color: var(--surface-main) !important;
    border: 1px solid var(--border-color) !important;
    border-top: 3.5px solid var(--plum-primary) !important;
    border-radius: 14px !important;
    padding: 22px 26px 22px 26px !important;
    margin-top: 4px !important;
    margin-bottom: 14px !important;
    box-shadow: 0 2px 12px rgba(61, 51, 66, 0.05) !important;
    box-sizing: border-box !important;
}}

.st-key-pp_unified_header > [data-testid="stVerticalBlock"] {{
    gap: 0.35rem !important;
}}

.st-key-pp_unified_header [data-testid="stHorizontalBlock"] {{
    align-items: center !important;
    gap: 1rem !important;
}}

.st-key-pp_unified_header [data-testid="stMarkdownContainer"] p {{
    margin-bottom: 0 !important;
}}

.st-key-header_download_report {{
    display: flex !important;
    justify-content: flex-end !important;
    width: 100% !important;
}}

.st-key-header_download_report button {{
    min-width: 176px !important;
    white-space: nowrap !important;
    padding: 0.55rem 1.2rem !important;
    background-color: var(--plum-primary) !important;
    color: #FFFFFF !important;
    border: 1.5px solid var(--plum-primary) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 3px 10px rgba(104, 67, 95, 0.18) !important;
}}

.st-key-header_download_report button:hover {{
    background-color: var(--plum-hover) !important;
    border-color: var(--plum-hover) !important;
}}

.st-key-header_download_report button * {{
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    white-space: nowrap !important;
    overflow: visible !important;
    text-overflow: clip !important;
}}

@media (max-width: 767px) {{
    .st-key-header_download_report {{
        justify-content: flex-start !important;
    }}
    .st-key-header_download_report button {{
        width: 100% !important;
    }}
}}

/* Reduced Motion Accessibility */
@media (prefers-reduced-motion: reduce) {{
    *, ::before, ::after {{
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }}
}}
</style>
"""


# ==============================================================================
# HTML COMPONENT RENDERERS
# ==============================================================================

def render_header_brand() -> str:
    """Render the left-side logo, title, and subtitle for the unified header top row."""
    return _clean_html(f"""
    <div class="pp-header-inner pp-reveal">
        <div class="pp-brand-wrap">
            {BRAND_SHIELD_SVG}
            <div style="min-width:0;">
                <div class="pp-brand-title">IoTShield AI</div>
                <div class="pp-brand-sub">Intelligent ransomware detection and prevention for connected environments.</div>
            </div>
        </div>
    </div>
    """)


def render_header_badges(threat_level: str) -> str:
    """Render the full-width bottom status badges row separated by a subtle hairline divider."""
    pill_cls, pill_label, icon_key = threat_meta(threat_level)
    return _clean_html(f"""
    <div class="pp-header-badges" style="border-top:1px solid {BORDER_COLOR}; padding-top:14px; padding-bottom:2px; margin-top:10px; margin-bottom:0;">
        <span class="pp-pill pp-pill-success">{ICONS["pulse"]} Engine active</span>
        <span class="pp-pill pp-pill-plum">{ICONS["shield"]} Safe simulation</span>
        <span class="pp-pill {pill_cls}">{ICONS[icon_key]} {escape(pill_label)}</span>
    </div>
    """)


def render_header(threat_level: str) -> str:
    """Backward-compatible combined header renderer."""
    return render_header_brand() + render_header_badges(threat_level)


def render_safe_strip(banner_text: str, scenario_id: str, tick: int) -> str:
    sim_time = tick * 5
    return _clean_html(f"""
    <div class="pp-safe-strip">
        <div style="display:flex; align-items:center; gap:8px;">
            {ICONS["shield"]}
            <span><strong>{escape(banner_text)}</strong> Virtual environment only &mdash; dummy files in isolated sandbox.</span>
        </div>
        <span style="font-family:var(--font-mono); font-size:0.82rem; color:{TEXT_SECONDARY}; white-space:nowrap;">
            {escape(scenario_id)} &bull; Window {tick} ({sim_time}s simulated)
        </span>
    </div>
    """)


def render_posture_and_kpis(snap: dict) -> str:
    threat = snap["threat_level"]
    pending = snap["pending_approval"]
    if threat == "HIGH":
        posture_cls = "posture-high pp-alert-reveal"
        posture_color = THREAT
        posture_title = "High threat detected"
        posture_desc = (
            f"Confirmed ransomware-like behaviour on {', '.join(pending)}. Human analyst approval is required to quarantine the affected device."
            if pending
            else "Active ransomware-like behaviour detected. Inspect AI Detection and Prevention Center."
        )
        pill = f'<span class="pp-pill pp-pill-threat">{ICONS["alert"]} Approval required</span>'
    elif threat == "MEDIUM":
        posture_cls = "posture-medium pp-alert-reveal"
        posture_color = WARNING
        posture_title = "Suspicious activity"
        posture_desc = "Elevated anomaly score observed in simulated telemetry. Monitoring for confirmation."
        pill = f'<span class="pp-pill pp-pill-warning">{ICONS["alert"]} Monitoring</span>'
    elif threat == "CONTAINED":
        posture_cls = "posture-contained pp-alert-reveal"
        posture_color = AI_VIOLET
        posture_title = "Threat contained"
        posture_desc = "Affected virtual device is isolated in quarantine. Subsequent simulated outbound attempts are rejected by the virtual gateway."
        pill = f'<span class="pp-pill pp-pill-violet">{ICONS["lock"]} Quarantined</span>'
    else:
        posture_cls = ""
        posture_color = SUCCESS
        posture_title = "All systems healthy"
        posture_desc = "All four virtual IoT and industrial devices are operating within normal baseline telemetry."
        pill = f'<span class="pp-pill pp-pill-success">{ICONS["check"]} Healthy posture</span>'

    susp_color = THREAT if snap["suspicious_devices"] > 0 else (AI_VIOLET if snap["quarantined_devices"] > 0 else TEXT_MAIN)
    blocked_anim = "pp-count-pop" if snap["blocked_events"] > 0 else ""

    return _clean_html(f"""
    <div class="pp-posture-grid pp-reveal">
        <div class="pp-hero-posture {posture_cls}">
            <div>
                <div style="display:flex; justify-content:space-between; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
                    <span style="font-size:0.84rem; font-weight:700; color:{TEXT_SECONDARY};">Current security posture</span>
                    {pill}
                </div>
                <div style="font-family:var(--font-heading); font-size:1.75rem; font-weight:700; color:{posture_color}; line-height:1.2; margin-bottom:8px;">
                    {posture_title}
                </div>
                <div style="font-size:0.93rem; color:{TEXT_MAIN}; line-height:1.5;">
                    {escape(posture_desc)}
                </div>
            </div>
            <div style="margin-top:14px; padding-top:10px; border-top:1px solid {BORDER_COLOR}; display:flex; justify-content:space-between; font-size:0.82rem; color:{TEXT_SECONDARY};">
                <span>Threat level: <strong style="color:{posture_color}; white-space:nowrap;">{escape(threat)}</strong></span>
                <span>Scenario: <strong style="color:{PRIMARY_PLUM}; font-family:var(--font-mono);">{escape(snap["scenario_id"])}</strong></span>
            </div>
        </div>
        <div class="pp-kpis-2x2">
            <div class="pp-kpi-card">
                <div class="pp-kpi-label">Virtual devices</div>
                <div class="pp-kpi-value">{snap["total_devices"]}</div>
                <div class="pp-kpi-meta">2 IoT &bull; 2 IIoT nodes</div>
            </div>
            <div class="pp-kpi-card">
                <div class="pp-kpi-label">Healthy devices</div>
                <div class="pp-kpi-value" style="color:{SUCCESS};">{snap["healthy_devices"]}</div>
                <div class="pp-kpi-meta">Operating within baseline</div>
            </div>
            <div class="pp-kpi-card">
                <div class="pp-kpi-label">Suspicious / Quarantined</div>
                <div class="pp-kpi-value" style="color:{susp_color};">{snap["suspicious_devices"]} / {snap["quarantined_devices"]}</div>
                <div class="pp-kpi-meta">Flagged or isolated nodes</div>
            </div>
            <div class="pp-kpi-card">
                <div class="pp-kpi-label">Blocked simulated events</div>
                <div class="pp-kpi-value {blocked_anim}" style="color:{CHAMPAGNE};">{snap["blocked_events"]:,}</div>
                <div class="pp-kpi-meta">{snap["blocked_bytes"]:,.0f} bytes rejected</div>
            </div>
        </div>
    </div>
    """)


def render_guided_console(stage: dict, target_device: str, auto_mode: bool) -> str:
    """Render the single guided 5-stage demonstration stepper card."""
    steps = [
        ("1", "Normal activity"),
        ("2", "Safe attack simulation"),
        ("3", "AI detection"),
        ("4", "Analyst approval"),
        ("5", "Prevention verification"),
    ]
    idx = stage["index"]
    mode_label = "Automatic (virtual)" if auto_mode else "Manual analyst approval"
    items = []
    for i, (num, title) in enumerate(steps):
        if i < idx:
            cls = "pp-step pp-step-done"
            badge = "&#10003;"
        elif i == idx:
            cls = "pp-step pp-step-active"
            badge = num
        else:
            cls = "pp-step"
            badge = num
        items.append(
            f'<div class="{cls}"><div class="pp-step-num">{badge}</div>'
            f'<div class="pp-step-title">{escape(title)}</div></div>'
        )

    status_pill = (
        f'<span class="pp-pill pp-pill-success">{ICONS["check"]} Completed</span>'
        if idx >= 5
        else f'<span class="pp-pill pp-pill-plum">Stage {idx + 1} of 5</span>'
    )

    return _clean_html(f"""
    <div class="pp-guided-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-family:var(--font-heading); font-size:1.18rem; font-weight:700; color:{TEXT_MAIN};">
                    {escape(stage["title"])}
                </div>
                <div style="font-size:0.9rem; color:{TEXT_SECONDARY}; margin-top:2px;">
                    {escape(stage["description"])}
                </div>
                <div style="font-size:0.82rem; color:{TEXT_SECONDARY}; margin-top:5px;">
                    Target: <strong style="color:{PRIMARY_PLUM}; font-family:var(--font-mono);">{escape(target_device)}</strong>
                    &nbsp;&bull;&nbsp; Policy: <strong style="color:{PRIMARY_PLUM};">{escape(mode_label)}</strong>
                </div>
            </div>
            {status_pill}
        </div>
        <div class="pp-stepper">{"".join(items)}</div>
    </div>
    """)


def _device_card_html(dev_id: str, d, sim) -> str:
    w = d.last_window or {}
    locked = sim.status(dev_id)["locked_demo_files"]
    icon_svg = ICONS.get(DEVICE_ICON_MAP.get(dev_id, "plc"), ICONS["plc"])

    if d.status == "QUARANTINED":
        card_cls = "pp-device-card dev-quarantined pp-alert-reveal"
        pill = f'<span class="pp-pill pp-pill-violet">{ICONS["lock"]} Quarantined</span>'
    elif d.security_status == "SUSPICIOUS":
        card_cls = "pp-device-card dev-suspicious pp-alert-reveal"
        pill = f'<span class="pp-pill pp-pill-threat">{ICONS["alert"]} Suspicious</span>'
    else:
        card_cls = "pp-device-card"
        pill = f'<span class="pp-pill pp-pill-success">{ICONS["check"]} Healthy</span>'

    crit_colors = {"LOW": SUCCESS, "MEDIUM": WARNING, "HIGH": THREAT}
    crit_c = crit_colors.get(d.criticality, TEXT_MAIN)
    deliv_conn = w.get("delivered_connections", 0)
    out_val = f'{w.get("delivered_bytes", 0):,.0f} B' if w else "0 B"
    sandbox_c = THREAT if locked > 0 else SUCCESS

    return f"""
    <div class="{card_cls}">
        <div class="pp-device-top">
            <div class="pp-device-id-group">
                <div class="pp-device-icon">{icon_svg}</div>
                <div>
                    <div class="pp-device-id">{escape(d.device_id)}</div>
                    <div class="pp-device-name">{escape(d.name)}</div>
                </div>
            </div>
            {pill}
        </div>
        <div class="pp-device-sub">{escape(d.device_type)} &bull; Activity: <strong>{escape(d.activity)}</strong></div>
        <div class="pp-kv-list">
            <div>
                <div class="pp-kv-label">Simulated IP</div>
                <div class="pp-kv-val">{escape(d.ip)}</div>
            </div>
            <div>
                <div class="pp-kv-label">Criticality</div>
                <div class="pp-kv-val" style="color:{crit_c};">{escape(d.criticality)}</div>
            </div>
            <div>
                <div class="pp-kv-label">Delivered connections</div>
                <div class="pp-kv-val">{deliv_conn} &bull; {out_val}</div>
            </div>
            <div>
                <div class="pp-kv-label">Sandbox files</div>
                <div class="pp-kv-val" style="color:{sandbox_c};">{locked} .locked_demo</div>
            </div>
        </div>
    </div>
    """


def render_device_grid(devices: dict, sim) -> str:
    """Render 4 virtual devices in a balanced 2x2 grid with subtle IoT vs IIoT separation."""
    iot_ids = [k for k, v in devices.items() if v.device_type == "IoT"]
    iiot_ids = [k for k, v in devices.items() if v.device_type != "IoT"]

    iot_cards = "".join(_device_card_html(k, devices[k], sim) for k in iot_ids)
    iiot_cards = "".join(_device_card_html(k, devices[k], sim) for k in iiot_ids)

    return _clean_html(f"""
    <div>
        <div class="pp-device-section-tag">IoT Edge Devices</div>
        <div class="pp-device-grid">{iot_cards}</div>
        <div class="pp-device-section-tag">Industrial (IIoT) Devices &amp; Infrastructure</div>
        <div class="pp-device-grid">{iiot_cards}</div>
    </div>
    """)


def render_detection_panel(dev_id: str, assessment: dict) -> str:
    """Render executive AI Detection verdict panel without raw JSON."""
    pred = assessment["predicted_class"]
    prob = assessment["probability"]
    risk = assessment["risk_level"]
    short_ts = format_full_timestamp(assessment.get("timestamp"))
    inf_ms = assessment.get("inference_ms", 0.0)
    is_threat = pred == "RANSOMWARE_LIKE"

    hero_cls = "pp-ai-hero ai-threat pp-alert-reveal" if is_threat else "pp-ai-hero ai-healthy pp-reveal"
    pred_color = THREAT if is_threat else SUCCESS
    pill_cls, _, icon_key = threat_meta(risk)

    if is_threat:
        explanation = (
            f"Unusual file-renaming activity and increased outbound traffic were observed in the simulated "
            f"{dev_id} environment, significantly exceeding its normal baseline."
        )
    else:
        explanation = (
            f"Telemetry for {dev_id} aligns with normal baseline patterns. No ransomware-like file-renaming "
            "or abnormal outbound burst was detected in the latest evaluation window."
        )

    return _clean_html(f"""
    <div class="{hero_cls}">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-size:0.84rem; font-weight:600; color:{TEXT_SECONDARY}; margin-bottom:4px;">
                    Detection Verdict &bull; Target: <span style="font-family:var(--font-mono); color:{PRIMARY_PLUM};">{escape(dev_id)}</span>
                </div>
                <div style="font-family:var(--font-heading); font-size:1.7rem; font-weight:700; color:{pred_color}; line-height:1.2;">
                    {escape(pred)}
                </div>
            </div>
            <span class="pp-pill {pill_cls}">{ICONS[icon_key]} Risk: {escape(risk)}</span>
        </div>
        <div style="margin-top:10px; font-size:0.95rem; color:{TEXT_MAIN}; line-height:1.5;">
            {escape(explanation)}
        </div>
        <div class="pp-ai-metrics">
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Model probability (synthetic)</div>
                <div style="font-family:var(--font-heading); font-size:1.55rem; font-weight:700; color:{pred_color};">{prob*100:.1f}% <span style="font-size:0.9rem; color:{TEXT_SECONDARY};">({prob:.3f})</span></div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Target criticality</div>
                <div style="font-family:var(--font-heading); font-size:1.4rem; font-weight:700; color:{TEXT_MAIN};">{escape(str(assessment.get("criticality", "N/A")))}</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Detection timestamp</div>
                <div style="font-family:var(--font-mono); font-size:0.95rem; font-weight:600; color:{TEXT_MAIN}; margin-top:6px;">{escape(short_ts)}</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Inference latency</div>
                <div style="font-family:var(--font-heading); font-size:1.4rem; font-weight:700; color:{CHAMPAGNE};">{inf_ms:.2f} ms</div>
            </div>
        </div>
    </div>
    """)


def render_prevention_sequence(step_done: int) -> str:
    """Render the 6-step Prevention Center sequence (Phase 11)."""
    labels = [
        "Suspicious activity detected",
        "Quarantine requested",
        "Analyst approval",
        "Device isolated",
        "Gateway blocks traffic",
        "Prevention verified",
    ]
    items = []
    for i, label in enumerate(labels):
        if i < step_done:
            cls = "pp-step pp-step-done"
            badge = "&#10003;"
        elif i == step_done:
            cls = "pp-step pp-step-active"
            badge = str(i + 1)
        else:
            cls = "pp-step"
            badge = str(i + 1)
        items.append(
            f'<div class="{cls}"><div class="pp-step-num">{badge}</div>'
            f'<div class="pp-step-title">{escape(label)}</div></div>'
        )
    return _clean_html(f"""
    <div class="pp-guided-card">
        <div style="font-family:var(--font-heading); font-size:1.05rem; font-weight:700; color:{TEXT_MAIN};">
            Response &amp; Containment Sequence
        </div>
        <div class="pp-stepper-6">{"".join(items)}</div>
    </div>
    """)


def render_metric_strip(cards: list[tuple[str, Any, str, str]], pop_indices: set[int] | None = None) -> str:
    pop_indices = pop_indices or set()
    html = ['<div class="pp-metric-strip">']
    for idx, (label, value, subtext, color) in enumerate(cards):
        val_str = str(value)
        font_sz = "1.35rem" if len(val_str) > 10 else "1.8rem"
        anim = "pp-count-pop" if idx in pop_indices else ""
        html.append(f"""
        <div class="pp-kpi-card">
            <div class="pp-kpi-label">{escape(label)}</div>
            <div class="pp-kpi-value {anim}" style="color:{color}; font-size:{font_sz};">{escape(val_str)}</div>
            <div class="pp-kpi-meta">{escape(subtext)}</div>
        </div>
        """)
    html.append("</div>")
    return _clean_html("".join(html))


def render_event_timeline(events: list[dict], limit: int = 6) -> str:
    if not events:
        body = f'<div style="color:{TEXT_SECONDARY}; font-size:0.9rem; padding:12px 0;">No security events recorded in the current scenario yet.</div>'
    else:
        rows = []
        for ev in reversed(events[-limit:]):
            norm = normalize_event_row(ev)
            sev = norm["Severity"]
            dot_c = AI_VIOLET if sev == "Blocked" else (THREAT if sev == "Alert" else (WARNING if sev == "Warning" else SUCCESS))
            rows.append(f"""
            <div class="pp-timeline-item">
                <div class="pp-dot" style="background-color:{dot_c};"></div>
                <div style="flex:1; min-width:0;">
                    <div style="display:flex; justify-content:space-between; gap:8px; font-size:0.8rem; color:{TEXT_SECONDARY};">
                        <span><strong style="color:{PRIMARY_PLUM}; font-family:var(--font-mono);">{escape(norm["Device"])}</strong> &bull; {escape(norm["Event type"])}</span>
                        <span style="font-family:var(--font-mono);">{escape(norm["Time"])}</span>
                    </div>
                    <div style="font-size:0.86rem; color:{TEXT_MAIN}; margin-top:2px; line-height:1.35;">{escape(norm["Description"])}</div>
                </div>
            </div>
            """)
        body = "".join(rows)

    return _clean_html(f"""
    <div class="pp-timeline-card">
        <div style="font-family:var(--font-heading); font-size:1.05rem; font-weight:700; color:{TEXT_MAIN}; margin-bottom:8px;">
            Current Scenario Events
        </div>
        {body}
    </div>
    """)


def render_complete_demo_panel(snap: dict, intensity: float, allow_sim_approval: bool) -> str:
    """Render the Complete Security Demonstration metadata & stepper panel (Task 3)."""
    stage = snap["stage"]
    steps = [
        ("1", "Normal activity"),
        ("2", "Simulated attack"),
        ("3", "AI detection"),
        ("4", "Quarantine"),
        ("5", "Prevention verified"),
    ]
    idx = stage["index"]
    items = []
    for i, (num, title) in enumerate(steps):
        if i < idx:
            cls = "pp-step pp-step-done"
            badge = "&#10003;"
        elif i == idx:
            cls = "pp-step pp-step-active"
            badge = num
        else:
            cls = "pp-step"
            badge = num
        items.append(
            f'<div class="{cls}"><div class="pp-step-num">{badge}</div>'
            f'<div class="pp-step-title">{escape(title)}</div></div>'
        )

    policy_text = (
        "SIMULATED_APPROVAL (opt-in, virtual only)"
        if allow_sim_approval
        else "Manual analyst approval (default)"
    )
    last_run = snap.get("last_run_summary")
    if last_run:
        st_code = last_run.get("status", "")
        if st_code == "COMPLETED":
            last_result = f"Completed ({last_run.get('scenario_id')})"
        elif st_code == "PAUSED_FOR_APPROVAL":
            last_result = "Awaiting manual approval"
        elif st_code == "FAILED":
            last_result = "Stopped safely (review alert)"
        else:
            last_result = st_code
    else:
        last_result = "Ready to run"

    status_pill = (
        f'<span class="pp-pill pp-pill-success">{ICONS["check"]} Completed</span>'
        if idx >= 5
        else f'<span class="pp-pill pp-pill-plum">Stage {idx + 1} of 5</span>'
    )

    return _clean_html(f"""
    <div class="pp-guided-card pp-reveal">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-family:var(--font-heading); font-size:1.25rem; font-weight:700; color:{PRIMARY_PLUM};">
                    Complete Security Demonstration
                </div>
                <div style="font-size:0.88rem; color:{TEXT_SECONDARY}; margin-top:2px;">
                    Normal activity &rarr; Simulated attack &rarr; AI detection &rarr; Quarantine &rarr; Prevention verification
                </div>
                <div style="font-size:0.9rem; color:{TEXT_MAIN}; margin-top:6px;">
                    Run the complete IoT/IIoT attack-detection and prevention workflow in the isolated virtual environment.
                </div>
            </div>
            {status_pill}
        </div>
        <div style="display:flex; flex-wrap:wrap; gap:10px 18px; margin-top:12px; padding-top:10px; border-top:1px solid {BORDER_COLOR}; font-size:0.84rem; color:{TEXT_SECONDARY};">
            <span>Target: <strong style="color:{PRIMARY_PLUM}; font-family:var(--font-mono);">{escape(snap["target_device"])}</strong></span>
            <span>Intensity: <strong style="color:{TEXT_MAIN}; font-family:var(--font-mono);">{intensity:.2f}</strong></span>
            <span>Approval policy: <strong style="color:{WARNING if allow_sim_approval else PRIMARY_PLUM};">{escape(policy_text)}</strong></span>
            <span>Current stage: <strong style="color:{TEXT_MAIN};">{escape(stage["title"])}</strong></span>
            <span>Last execution: <strong style="color:{TEXT_MAIN};">{escape(last_result)}</strong></span>
        </div>
        <div class="pp-stepper">{"".join(items)}</div>
    </div>
    """)


def render_completion_summary(summary: dict) -> str:
    """Render the professional DEMONSTRATION COMPLETED summary screen (Task 4)."""
    delay = (
        f"{summary['detection_delay_windows']} window(s) ({summary['detection_delay_simulated_seconds']}s)"
        if summary.get("detection_delay_windows") is not None
        else "N/A"
    )
    prob = summary.get("probability")
    prob_str = f" ({prob*100:.1f}%)" if prob is not None else ""
    return _clean_html(f"""
    <div class="pp-ai-hero ai-healthy pp-alert-reveal" style="margin-top:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-size:0.8rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:{SUCCESS};">
                    DEMONSTRATION COMPLETED &bull; {escape(str(summary.get("scenario_id", "")))}
                </div>
                <div style="font-family:var(--font-heading); font-size:1.35rem; font-weight:700; color:{TEXT_MAIN}; margin-top:2px;">
                    End-to-End Detection &amp; Virtual Prevention Verified
                </div>
            </div>
            <span class="pp-pill pp-pill-success">{ICONS["check"]} Verified</span>
        </div>
        <div class="pp-ai-metrics">
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Target device</div>
                <div style="font-family:var(--font-mono); font-size:1.25rem; font-weight:700; color:{PRIMARY_PLUM};">{escape(str(summary["target"]))}</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Detection &amp; Risk</div>
                <div style="font-family:var(--font-heading); font-size:1.15rem; font-weight:700; color:{THREAT};">{escape(str(summary["detection"]))}{prob_str} &bull; {escape(str(summary["risk"]))}</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Quarantine</div>
                <div style="font-family:var(--font-heading); font-size:1.15rem; font-weight:700; color:{AI_VIOLET};">{escape(str(summary["quarantine_status"]))}</div>
                <div style="font-size:0.76rem; color:{TEXT_SECONDARY}; margin-top:2px;">{escape(str(summary.get("approved_by", "")))}</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Blocked simulated events</div>
                <div class="pp-count-pop" style="font-family:var(--font-heading); font-size:1.4rem; font-weight:700; color:{CHAMPAGNE};">{summary["blocked_events"]:,}</div>
                <div style="font-size:0.76rem; color:{TEXT_SECONDARY};">{summary["blocked_bytes"]:,} B rejected</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Delivered bytes after quarantine</div>
                <div style="font-family:var(--font-heading); font-size:1.4rem; font-weight:700; color:{SUCCESS};">{summary["delivered_bytes_after_quarantine"]:,} B</div>
            </div>
            <div class="pp-ai-tile">
                <div class="pp-kv-label">Detection delay &amp; false alarms</div>
                <div style="font-family:var(--font-heading); font-size:1.05rem; font-weight:700; color:{TEXT_MAIN};">{escape(delay)}</div>
                <div style="font-size:0.76rem; color:{TEXT_SECONDARY};">Other-device false alarms: {summary["other_device_false_alarms"]}</div>
            </div>
        </div>
        <div style="margin-top:12px; font-size:0.86rem; color:{TEXT_SECONDARY};">
            Full evidence for this scenario is ready &mdash; use <strong>Download Report</strong> in the upper-right header to export the Markdown report.
        </div>
    </div>
    """)
