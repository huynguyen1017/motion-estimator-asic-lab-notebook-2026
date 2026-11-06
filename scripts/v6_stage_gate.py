#!/usr/bin/env python3
"""Verify real evidence before promoting an RTL or physical-design checkpoint."""
from argparse import ArgumentParser
from pathlib import Path
from hashlib import sha256
import json
import re
import sys

parser = ArgumentParser()
parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
parser.add_argument("--scope", choices=["rtl", "full"], default="full")
parser.add_argument("--flow")
parser.add_argument("--report")
args = parser.parse_args()
repo = Path(args.repo).expanduser().resolve()
flow = Path(args.flow).expanduser().resolve() if args.flow else None
report_path = Path(args.report).expanduser().resolve() if args.report else repo/"verification"/"v6_clean"/"qa_runs"/"stage_gate.json"

checks = []
def gate(name, passed, detail):
    checks.append({"name": name, "pass": passed, "detail": str(detail)[:350]})
    print(("PASS" if passed is True else "FAIL" if passed is False else "PENDING"),
          name, "-", detail)

def read(path):
    return path.read_text(errors="replace") if path.is_file() else ""

p = repo/"verification"/"v6_clean"
summary = p/"qa_runs"/"summary.json"
if summary.is_file():
    try:
        entries = json.loads(summary.read_text())
        passing = [x for x in entries if x.get("status") == "PASS"]
        gate("seven simulation runs", len(entries) == 7 and len(passing) == 7,
             f"{len(passing)}/{len(entries)} exited successfully")
        log = read(p/"qa_runs"/"motion_fullmotion_v2_tb.run.log")
        gate("three checked baseline vectors",
             all(f"MOTION_BASELINE_T{n}_PASS" in log for n in range(1,4)),
             "Each result has an explicit failure assertion")
        log = read(p/"qa_runs"/"motion_v5_16bit_top_regression_tb.run.log")
        gate("three checked corrected-top vectors", "V5_TOP_REGRESSION_PASS 3/3" in log,
             "Observed corrected RTL passes all three directed checks")
    except (ValueError, TypeError) as exc:
        gate("parse simulation summary", False, exc)
else:
    gate("simulation summary present", False, summary)

source = p/"top.v"
verified = repo/"rtl"/"verified"/"top.v"
gate("corrected RTL byte match", source.is_file() and verified.is_file()
     and sha256(source.read_bytes()).digest() == sha256(verified.read_bytes()).digest(),
     "Release RTL matches previously reviewed 16-bit implementation")
gate("professor baseline preserved", (repo/"rtl"/"top.v").is_file(),
     "Original baseline remains separately available")
slide3 = repo/"deliverables"/"ENGR852_V6_Motion_Estimator_3_Contribution_Slides.pptx"
slide19 = repo/"deliverables"/"ENGR852_V6_Motion_Estimator_Full_Team_19_Slides.pptx"
gate("V6 three-slide presentation", slide3.is_file() and slide3.stat().st_size > 20000,
     slide3.name)
gate("V6 combined presentation", slide19.is_file() and slide19.stat().st_size > 100000,
     slide19.name)

if args.scope == "full":
    if flow is None or not flow.is_dir():
        for name in ["GDS placement completeness", "ICV DRC zero violations",
                     "post-ECO extracted SPEF", "PrimeTime setup and hold at all corners"]:
            gate(name, None, "Server artifact not provided; cannot certify")
    else:
        gds = flow/"results"/"v6_signoff_v5_reexport.gds"
        log = read(flow/"v6_probe"/"gds_export_audit.log")
        placed = ("V6_GDS_UNPLACED_CELL_COUNT=0" in log or
                  "UNPLACED_FLAT_CELL_COUNT=0" in log)
        exported = ("V6_GDS_REEXPORT_COMPLETED" in log or
                    "GDS_REEXPORT_COMPLETED" in log)
        gate("GDS placement completeness",
             placed and exported and "GDS-110" not in log
             and gds.is_file() and gds.stat().st_size > 100000,
             f"Unplaced check + export log + GDS file: {gds.name}")
        # Physical closure must use ICV/STA reports from the same final checkpoint.
        for name in ["ICV DRC zero violations", "post-ECO extracted SPEF",
                     "PrimeTime setup and hold at all corners"]:
            gate(name, None, "Final post-ECO output not supplied; no status promotion")

ok = all(c["pass"] is True for c in checks)
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps({"scope": args.scope, "all_passed": ok,
                                  "gates": checks}, indent=2)+"\n")
print("FINAL_GATE_RESULT", "PASS" if ok else "INCOMPLETE", "report", report_path)
sys.exit(0 if ok else 1)
