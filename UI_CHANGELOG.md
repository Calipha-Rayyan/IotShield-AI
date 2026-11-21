# IoTShield AI — Critical Engineering & Porcelain Plum UX Rebuild Changelog
**Visual Identity**: **PORCELAIN PLUM** — *"Intelligence with elegance."*  
**Platform**: Windows 11, Google Chrome, Python 3.13.2, Streamlit 1.67.0  

---

## 1. Critical Bug Fixes

### 1.1 Canonical Sandbox Path Validation (`src/safe_attack_simulator.py`)
- **Fixed**: `SandboxViolation` false rejections for valid device paths (e.g., `D:\IoTShield_AI\demo_sandbox\CAM-01\dummy_file_002.demo`).
- **Root Cause & Fix**:
  - Anchored `DEFAULT_SANDBOX_ROOT` to the project location (`PROJECT_ROOT / "demo_sandbox"`), independent of current working directory.
  - Created the sandbox directory *before* canonicalizing `self.root` via `os.path.realpath`.
  - Replaced naive `Path.parents` checks with `os.path.normcase` + `os.path.realpath` + `os.path.commonpath` validation (handling Windows drive letters and path casing safely).
  - Enforced per-device directory boundaries (`device_id` check) so cross-device paths, directory traversal (`..`), cross-drive paths, and symlink escapes remain strictly rejected.
  - Added server-side Python `logging` of rejected `(root, candidate, device_id)` without exposing internal file paths in the user interface.

### 1.2 Single Authoritative Backend State & Consistent Reset (`src/session.py`)
- **Fixed**: Stale threat badge, suspicious counts, and completed timeline stages persisting after clicking Reset.
- **Root Cause & Fix**:
  - Created `DemoSession.state_snapshot()` and `DemoSession.current_stage()` as the single source of truth read by all 7 pages.
  - Introduced `scenario_id` (`SCEN-001`, `SCEN-002`, ...) and `historical_events` archival so `reset()` archives prior scenario events separately, increments `scenario_id`, restores all 4 devices to `HEALTHY` / `ONLINE`, restores all sandbox dummy files, zeroes blocked counters, clears alerts/approvals/detections, and resets the workflow to Stage 1 (`NORMAL_READY`).

---

## 2. Interaction & Presentation Overhaul

### 2.1 Guided 5-Stage Demonstration Flow (Zero Duplicate Controls)
- Replaced duplicated sidebar buttons, 5-button rows, and "Run Complete Demo Automatically" with **one guided primary action at a time** on Overview:
  1. `Start normal activity`
  2. `Launch safe attack simulation`
  3. `Run AI detection`
  4. `Approve quarantine`
  5. `Advance simulation and verify blocked traffic` → `Demonstration completed successfully.`
- Secondary controls limited strictly to `Reset demonstration` and `Release quarantine` (shown only when a device is quarantined).

### 2.2 Single Left-Rail Navigation & Viewer Mode
- Replaced the top horizontal navigation bar with a single left-rail sidebar navigation (`Overview`, `Devices`, `Network Traffic`, `AI Detection`, `Prevention Center`, `Security Events`, `Model Evaluation`).
- Placed `Environment Settings` (Target device `PLC-01` default, Attack intensity, Manual approval default ON) in an expandable sidebar section, plus a single `Download Security Report` action.
- Added `[client] toolbarMode = "viewer"` in `.streamlit/config.toml` to hide Streamlit developer chrome (`Deploy`, `Rerun`, `Always rerun`) from the presentation view.

### 2.3 Raw Backend Metadata Hidden by Default
- Removed raw Python dicts, object representations, internal paths, and stack traces from the default UI.
- Gated `Advanced technical evidence` behind `IOTSHIELD_SHOW_TECHNICAL_DETAILS=1` (disabled by default).
- Added friendly user-facing error handling (`run_safe_action`) with server-side exception logging.

---

## 3. Porcelain Plum Visual Identity & State-Driven Motion
- Adopted the **Porcelain Plum** light palette (`#F7F4F8` background, `#FFFFFF` surface, `#F0EAF3` left rail, `#68435F` primary plum, `#B45D7A` rose accent, `#7566A8` AI violet, `#3D3342` dark plum text, `#26765F` success, `#8F5D17` warning, `#AC3C53` threat).
- Balanced 2×2 device grid separating IoT Edge (`CAM-01`, `TEMP-01`) and Industrial IIoT (`PLC-01`, `GW-01`).
- State-driven CSS transitions (`ppPageReveal`, `ppAlertSlide`, `ppCountPop`) with `prefers-reduced-motion` support.
- 6-step Prevention Center response sequence (`Suspicious activity detected` → `Quarantine requested` → `Analyst approval` → `Device isolated` → `Gateway blocks traffic` → `Prevention verified`).

---

## 4. Download Experience & One-Click Demonstration Upgrade

### 4.1 Upper-Right Header "Download Report" Action
- Removed the buried sidebar download control (zero duplicate download buttons).
- Added a Primary Plum native `st.download_button("Download Report", ..., type="primary", icon=":material/download:", on_click="ignore", width="content")` in the upper-right main header, visible across all 7 navigation pages without mutating or resetting application state.
- Upgraded `src/report_generator.py` with dynamic scenario filenames (`IoTShield_AI_Security_Report_SCEN-00X.md`), all 23 real current-scenario evidence fields, explicit empty-state messaging (`"No completed attack-detection demonstration is available in this scenario."`), synthetic vs. real-world distinction, and optional collapsed CSV event-log export on Security Events.

### 4.2 Prominent "Complete Security Demonstration" & "Run All Operations"
- Added a dedicated **Complete Security Demonstration** panel on Overview featuring the prominent **`Run All Operations`** button (`icon=":material/play_circle:"`, `type="primary"`).
- Added an explicit opt-in checkbox (`"Allow simulation-only automatic quarantine approval"`, default unchecked) so manual analyst approval remains the default policy. When enabled, quarantine approval is explicitly labelled `SIMULATED_APPROVAL` (virtual sandbox only).
- Added a native `@st.dialog` confirmation modal listing all safety guarantees with `Cancel` and `Confirm and Run`.
- Added real-time execution progress via `st.status` + `st.progress` updated strictly after each real backend stage completes (zero fake sleeps), concurrency guard (`is_running`), and a **DEMONSTRATION COMPLETED** summary panel.
