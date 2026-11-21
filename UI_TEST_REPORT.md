# IoTShield AI — Final Verification & QA Test Report (Porcelain Plum Edition)
**Environment**: Windows 11 (win32), Python 3.13.2, Streamlit 1.67.0, Pytest 9.2.0, Google Chrome  

---

## 1. Automated Test Suite (`python -m pytest -v`)

Result: **33 passed, 1 skipped** (34 collected) in 88.44s.

- `tests/test_agent.py` (11/11 passed): risk levels, normal baseline, manual approval + quarantine blocking, auto-quarantine toggle, reject/release reversibility, reset, reproducible full demo, release label cleanup, quarantined outbound rejection, full demo with CAM-01 & repeated runs, reset consistency & historical log separation.
- `tests/test_app.py` (1/1 passed): guided 5-stage workflow, single active primary action, zero duplicate sidebar buttons, raw metadata hidden by default, reset consistency across all 7 navigation pages.
- `tests/test_download_and_run_all.py` (8/8 passed): header Download Report placement (zero sidebar duplicate), empty-state report & dynamic scenario filename, real detection & quarantine evidence in downloaded report, state preservation on download, manual-approval pause at Stage 4, one-click `SIMULATED_APPROVAL` opt-in & explicit labelling, `CAM-01` target selection, concurrency guard (`ALREADY_RUNNING`), failed execution non-success handling, and clean reset after full demo.
- `tests/test_detector.py` (3/3 passed): model artifacts, synthetic metric consistency, normal vs. attack classification.
- `tests/test_sandbox.py` (5 passed, 1 skipped): dummy file isolation, UTF-8 note & plain-text check, path traversal restriction, reset foreign-file preservation, Windows path casing & cross-device isolation, symlink escape (skipped on Windows without symlink privileges).
- `tests/test_simulator.py` (5/5 passed): 4 devices, normal traffic reproducibility, attack separation, feature extraction, leakage-free scenario split.

---

## 2. CLI Demonstration Verification (`demo_scenario.py`)

- **`--target PLC-01`**: `RANSOMWARE_LIKE` (`p=1.0`, `HIGH` risk), `QUARANTINED`, **182** blocked simulated events, **0** delivered outbound bytes post-quarantine, **0** false alarms on other devices.
- **`--target CAM-01`**: Completed cleanly without `SandboxViolation`; only `CAM-01` targeted while `PLC-01`, `TEMP-01`, and `GW-01` remained normal.

---

## 3. Chrome Visual & Responsive Screenshots

All 16 screenshots in `evidence/screenshots/` verified at 1366×768, 1440×900, 1920×1080, and 125% browser zoom (`overflow: false` on every viewport), with official Streamlit viewer mode active (`toolbarMode = "viewer"`).
