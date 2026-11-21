# IoTShield AI – Implementation Test Report (Phase 1: application only)

Date of runs: 17 November 2026. Every number below was produced by running the code in this project; nothing is estimated.
**All data is synthetic simulation data. These results do not describe real-world IoT/IIoT ransomware detection.**

## 1. Test environment (where it actually ran)

| Item | Value |
|---|---|
| OS | Linux container (NOT Windows) |
| Python | 3.12.3 |
| scikit-learn / pandas / numpy | 1.9.1 / 3.0.6 / 2.5.4 |
| streamlit / plotly / pytest | 1.67.0 / 7.1.0 / 9.2.0 |
| Screenshots | Headless Chromium driving the real Streamlit app |

## 2. Automated tests (pytest) – 21 run, 21 passed

Raw output: `evidence/test_results/pytest_output.txt`

| Required area | Tests | Result |
|---|---|---|
| Normal traffic generation | `test_normal_traffic_generation_is_plausible_and_reproducible`, `test_four_virtual_devices_with_required_fields` | PASSED |
| Ransomware-like event generation | `test_ransomware_like_events_exceed_normal`, `test_attack_renames_and_writes_note_without_encryption` | PASSED |
| Feature extraction | `test_feature_extraction_order_and_missing_feature`, `test_dataset_split_has_no_scenario_leakage_and_is_reproducible` | PASSED |
| ML predictions | `test_ml_predictions_normal_vs_attack`, `test_model_artifacts_saved`, `test_metrics_are_consistent_and_labelled_synthetic` | PASSED |
| Risk assessment | `test_risk_assessment_levels`, `test_normal_environment_gives_no_alert` | PASSED |
| Quarantine approval | `test_attack_alert_requires_approval_then_quarantine_blocks`, `test_auto_quarantine_only_when_enabled`, `test_reject_and_release_are_reversible` | PASSED |
| Blocked simulated events | same quarantine test (blocked count, zero delivered bytes, BLOCKED log entries) | PASSED |
| Environment reset | `test_environment_reset`, `test_reset_restores_and_leaves_foreign_files` | PASSED |
| Sandbox path restrictions | `test_path_restrictions` (`../`, `..`, `/etc`, unknown id, empty id, outside path), `test_symlink_escape_is_refused`, `test_creates_dummy_files_only_in_sandbox` | PASSED |
| Reproducible full demo | `test_full_demo_is_reproducible` | PASSED |
| Dashboard controls | `test_all_dashboard_controls_work` (Streamlit AppTest clicks Start Normal, Run AI Detection, Launch Attack, Approve Quarantine, Advance, Reset, Run Full Demo) | PASSED |

Note: the unit tests that need a model train a small temporary model (120+120 scenarios), so they do not depend on the shipped model.

## 3. Model evaluation (`python train_model.py`, seed 42)

Random Forest, 200 trees, max depth 12, class-weight balanced. Scenario-level split (no scenario appears in two splits, verified by an assertion).

| Split | Windows (scenarios) | Accuracy | Precision | Recall | F1 | FPR | FNR |
|---|---|---|---|---|---|---|---|
| Train (not a performance claim) | 5,760 (288) | 99.86% | 99.54% | 100.00% | 99.77% | 0.20% | 0.00% |
| Validation | 1,920 (96) | 96.88% | 99.05% | 90.45% | 94.56% | 0.37% | 9.55% |
| **Held-out test** | 1,920 (96) | **97.76%** | **98.72%** | **93.75%** | **96.17%** | **0.52%** | **6.25%** |

Test confusion matrix (TN, FP, FN, TP) = **1337, 7, 36, 540**. Grouped 5-fold CV F1 on train+val: 98.48% ± 0.70%.
Inference time for one window through `Detector.predict_window`: mean 11.3 ms (p95 16.0 ms; includes DataFrame creation and Random Forest thread start-up).
Most important features: `file_rename_rate` (0.454), `failed_connection_rate` (0.285), `device_activity_score` (0.094).

What these numbers mean: the false negatives are mostly the weakest simulated attacks (low intensity), which were deliberately generated to overlap with normal behaviour. The synthetic data is built by us, so the model is learning our own rules.

**Development note (disclosed for honesty):** my first version of the generator gave 100% on every metric, and a second version with some extra variation still did. I judged that too easy to be meaningful, so I made two adjustments before the final run: per-run baseline drift, more benign bursts and weaker (stealthier) attacks, then attack effects that scale from zero with intensity instead of having a fixed minimum offset. The third version is the one reported here. I did not tune toward a target score, but the generator was changed after seeing results, so the numbers above reflect a simulation I made deliberately harder.

## 4. Demonstration run (`python demo_scenario.py`, seed 42, target PLC-01, intensity 0.7)

Files: `evidence/demo_results/` (`demo_results.json`, `demo_telemetry.csv`, `demo_event_log.csv`, `demo_security_report.md`, `demo_timeline.png`, `demo_console_output.txt`).

| Stage | Result |
|---|---|
| 1 Normal | 10 windows × 4 devices assessed; all NORMAL; max probability 0.0513; 0 alerts |
| 2 Attack | Safe simulation starts at window 11; 20 of 24 dummy files renamed by the end; note file written |
| 3 Detection | PLC-01 `RANSOMWARE_LIKE`, p = 1.0, risk HIGH, alert at window 12; top features: file_rename_rate (19.8/min vs ~0.7 normal), failed_connection_rate (0.139 vs 0.015), device_activity_score |
| 4 Prevention | Quarantine requested, then approved (scripted analyst approval); PLC-01 = QUARANTINED; 182 simulated outbound connections blocked in the next 6 windows (2,330,607 attempted bytes, 0 delivered) |
| 5 Evidence | Normal mean outbound 117,719 B/window; attack mean 400,377 B/window; 800,754 B delivered before quarantine; 0 delivered after; detection delay 2 windows (10 simulated seconds) |

Detection delay counts telemetry windows only. Human approval time is not included in that number.

## 5. Repeated runs (robustness, `evidence/evaluation/`)

- Full demo, 4 target devices × 25 seeds = 100 runs: attack detected and quarantined in **100/100**; mean delay 1.96–2.00 windows; **0 bytes** delivered after quarantine in all runs; **0** false HIGH alerts on non-target devices.
- Normal phase only, seeds 1–25 (1,000 windows): **7 windows (0.70%)** were falsely flagged RANSOMWARE_LIKE, in 7 of 25 runs. None became a HIGH alert, because the policy needs 2 consecutive flagged windows. This matches the test-set false-positive rate (0.52%). For the live demo, the default seed 42 gives a clean normal phase, but a different seed may show a flagged window.

## 6. What was NOT tested / known gaps

- **Not run on Windows.** `README.md` commands, PowerShell activation, `start_demo.bat` and the Windows browser launch are untested. They follow standard Python/Streamlit practice, but please run them once on your laptop before the presentation.
- Metrics on your machine may differ slightly if your scikit-learn/NumPy versions differ; re-run `python train_model.py` and use your own numbers.
- Only one attack type (ransomware-like), four device profiles and one risk policy were tested.
- Real network traffic, real devices and real ransomware were never used (by design); no claim is made about them.
- Manual approval was tested through a scripted approval and through AppTest button clicks and real browser clicks for screenshots; human timing was not measured.
- Pass/fail of the auto-quarantine mode was tested in the unit test only, not shown in screenshots.

## 7. Evidence inventory

- `evidence/screenshots/` – 13 real screenshots of the running dashboard (initial, normal, traffic, attack launched, HIGH alert pending approval, AI explanation, traffic during attack, quarantine approved, blocked events, event log, model evaluation, devices after quarantine, after reset).
- `evidence/evaluation/` – `metrics.json`, `classification_report_test.txt`, `confusion_matrix_test.png/.json`, `feature_importance.png`, console output, multi-seed results.
- `evidence/test_results/pytest_output.txt` – raw pytest output.
- `evidence/demo_results/` – demo outputs listed above.
