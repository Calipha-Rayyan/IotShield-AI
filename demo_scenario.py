"""One-command demonstration: python demo_scenario.py [--target PLC-01] [--severity 0.7] [--seed 42]

SAFE SIMULATION ONLY - NO REAL RANSOMWARE IS RUNNING. Saves real results into evidence/demo_results/."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.detector import ModelNotTrainedError  # noqa: E402
from src.report_generator import build_security_report, plot_timeline  # noqa: E402
from src.safe_attack_simulator import BANNER  # noqa: E402
from src.session import DemoSession  # noqa: E402


def run(target="PLC-01", severity=0.7, seed=42, out_dir=None, quiet=False) -> dict:
    out = Path(out_dir or ROOT / "evidence" / "demo_results")
    out.mkdir(parents=True, exist_ok=True)
    s = DemoSession(ROOT, seed=seed)
    r = s.run_full_demo(target=target, severity=severity)
    df = s.env.history_df()
    df.to_csv(out / "demo_telemetry.csv", index=False, encoding="utf-8")
    s.log.to_dataframe().to_csv(out / "demo_event_log.csv", index=False, encoding="utf-8")
    (out / "demo_results.json").write_text(json.dumps(r, indent=2, default=str), encoding="utf-8")
    (out / "demo_security_report.md").write_text(build_security_report(s), encoding="utf-8")
    plot_timeline(df, target, r["stage2_attack"]["onset_tick"], r["stage4_prevention"]["quarantine_tick"],
                  out / "demo_timeline.png")
    if not quiet:
        p = print
        p(BANNER)
        p(f"\nSTAGE 1 - Normal environment: expected NORMAL -> {r['stage1_normal']['result']} "
          f"(max p={r['stage1_normal']['max_probability']}, alerts={r['stage1_normal']['alerts']})")
        p(f"STAGE 2 - Safe attack launched on {target} at window {r['stage2_attack']['onset_tick']}; "
          f"dummy files renamed so far: {r['stage2_attack']['files_renamed']}")
        d = r["stage3_detection"]
        p(f"STAGE 3 - AI detection: {d['predicted_class']} p={d['probability']} risk={d['risk_level']} at {d['timestamp']} "
          f"(inference {d['inference_ms']} ms)")
        for f in d["top_features"] or []:
            p(f"          feature {f['feature']}: value={f['value']} normal~{f['normal_mean']} z={f['z_score']}")
        q = r["stage4_prevention"]
        p(f"STAGE 4 - Prevention: {target} status = {q['status']} (approved={q['approved']}), "
          f"blocked simulated events after quarantine = {q['blocked_events_after']}")
        e = r["stage5_effectiveness"]
        p("STAGE 5 - Evidence:")
        for k, v in e.items():
            p(f"          {k}: {v}")
        p(f"\n{r['note']}\nResults saved in {out}")
    return r


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=BANNER)
    ap.add_argument("--target", default="PLC-01")
    ap.add_argument("--severity", type=float, default=0.7)
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    try:
        run(a.target, a.severity, a.seed)
    except ModelNotTrainedError as exc:
        sys.exit(f"{exc}")