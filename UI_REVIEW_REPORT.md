# IoTShield AI — Porcelain Plum Architecture & Visual Review Report

## 1. Acceptance Criteria Audit (14 / 14 Verified)

| # | Acceptance Criterion | Verification | Status |
|---|---|---|---|
| 1 | Full demonstration no longer raises `SandboxViolation` for valid device paths | Verified for both `PLC-01` and `CAM-01` in `pytest` and `demo_scenario.py` | **PASS** |
| 2 | Invalid and out-of-sandbox paths remain rejected | Traversal, cross-device, outside files, and symlinks strictly raise `SandboxViolation` | **PASS** |
| 3 | All four devices function correctly | `CAM-01`, `TEMP-01`, `PLC-01`, `GW-01` verified in balanced 2×2 grid & telemetry | **PASS** |
| 4 | Environment reset returns dashboard to consistent normal state | Verified in `test_reset_consistency_and_historical_log_separation`, `test_app.py`, and `13_after_reset.png` (`SCEN-002`, 4 healthy, Threat LOW, 0 blocked) | **PASS** |
| 5 | Only one primary demonstration action is available at a time | Verified in `test_app.py` and Overview screenshots (`01`, `05`, `13`) | **PASS** |
| 6 | Duplicate action controls are removed | Sidebar contains only the 7 navigation items, collapsed settings, and 1 report download | **PASS** |
| 7 | Raw backend metadata is hidden by default | `IOTSHIELD_SHOW_TECHNICAL_DETAILS=0` default; verified in `test_app.py` & `06`, `10` | **PASS** |
| 8 | Streamlit developer controls hidden in viewer mode | `[client] toolbarMode = "viewer"` active — `Deploy` chrome gone in Chrome screenshots | **PASS** |
| 9 | Coherent professional light Porcelain Plum theme | `#F7F4F8` / `#FFFFFF` / `#F0EAF3` / `#68435F` / `#3D3342` verified across all 7 pages | **PASS** |
| 10 | Readable navigation and typography | Single left rail with 15px labels, zero mid-word wrapping on device IDs & status pills | **PASS** |
| 11 | Meaningful state-driven animations | `ppPageReveal`, `ppAlertSlide`, `ppCountPop` tied to real state changes + `prefers-reduced-motion` | **PASS** |
| 12 | Quarantine prevents subsequent simulated outbound events | Verified: `153` blocked events in Chrome UI, `182` in CLI demo, `0` bytes delivered | **PASS** |
| 13 | All automated tests pass (apart from documented Windows symlink skip) | **25 passed, 1 skipped** across 26 collected tests | **PASS** |
| 14 | Genuine Chrome screenshots cover all stages & viewports | 16 screenshots inspected at 1366×768, 1440×900, 1920×1080, 125% zoom (`overflow: false`) | **PASS** |

---

## 2. Responsive & Zoom Verification Matrix

| Viewport | `scrollWidth` | `innerWidth` | Horizontal Overflow |
|---|---:|---:|---|
| 1366 × 768 | 1366 | 1366 | `false` |
| 1440 × 900 | 1440 | 1440 | `false` |
| 1920 × 1080 | 1920 | 1920 | `false` |
| 1366 × 768 @ 125% zoom | 1093 | 1093 | `false` |

---

## 3. Download Report & One-Click Demonstration Visual Review

- **Header Download Report (`17_header_download_and_overview.png`)**: Primary Plum (`#68435F`) button with pure white text and Material download icon sits cleanly in the upper-right header across all 7 pages; zero duplicate sidebar download control; zero overflow at 1366×768, 1440×900, 1920×1080, and 125% zoom.
- **Confirmation Dialog (`18_run_all_confirmation_dialog.png`)**: Native `st.dialog` clearly communicates all 6 sandbox & approval safety facts with `Cancel` and Primary Plum `Confirm and Run` actions.
- **Manual Approval Safety (`19_one_click_completed_summary.png`)**: With opt-in unchecked (default), `Run All Operations` executes Stages 1–3, detects `RANSOMWARE_LIKE (HIGH risk)` on `PLC-01`, and pauses cleanly at Stage 4 requesting manual analyst approval. With opt-in checked, executes all stages with explicit `SIMULATED_APPROVAL` labelling and displays the **DEMONSTRATION COMPLETED** summary panel.
