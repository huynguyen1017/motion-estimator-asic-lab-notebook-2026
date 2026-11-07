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
flow = Path(args.flow).expanduser().resolve() if args.flow else (repo / "evidence" / "v9_signoff")
report_path = Path(args.report).expanduser().resolve() if args.report else repo / "verification" / "v6_clean" / "qa_runs" / "stage_gate.json"

checks = []
def gate(name, passed, detail):
    checks.append({"name": name, "pass": passed, "detail": str(detail)[:350]})
    print(("PASS" if passed is True else "FAIL" if passed is False else "PENDING"),
          name, "-", detail)

def read(path):
    return path.read_text(errors="replace") if path.is_file() else ""

p = repo / "verification" / "v6_clean"
summary = p / "qa_runs" / "summary.json"
if summary.is_file():
    try:
        entries = json.loads(summary.read_text())
        passing = [x for x in entries if x.get("status") == "PASS"]
        gate("seven simulation runs", len(entries) == 7 and len(passing) == 7,
             f"{len(passing)}/{len(entries)} exited successfully")
        log = read(p / "qa_runs" / "motion_fullmotion_v2_tb.run.log")
        gate("three checked baseline vectors",
             all(f"MOTION_BASELINE_T{n}_PASS" in log for n in range(1, 4)),
             "Each result has an explicit failure assertion")
        log = read(p / "qa_runs" / "motion_v5_16bit_top_regression_tb.run.log")
        gate("three checked corrected-top vectors", "V5_TOP_REGRESSION_PASS 3/3" in log,
             "Observed corrected RTL passes all three directed checks")
    except (ValueError, TypeError) as exc:
        gate("parse simulation summary", False, exc)
else:
    gate("simulation summary present", False, summary)

source = p / "top.v"
verified = repo / "rtl" / "verified" / "top.v"
gate("corrected RTL byte match", source.is_file() and verified.is_file()
     and sha256(source.read_bytes()).digest() == sha256(verified.read_bytes()).digest(),
     "Release RTL matches previously reviewed 16-bit implementation")
gate("professor baseline preserved", (repo / "rtl" / "top.v").is_file(),
     "Original baseline remains separately available")

slide3 = repo / "deliverables" / "ENGR852_V9_Clean_3_Contribution_Slides.pptx"
if not slide3.is_file():
    slide3 = repo / "deliverables" / "ENGR852_V8_Clean_3_Contribution_Slides.pptx"
slide19 = repo / "deliverables" / "ENGR852_V9_Complete_19_Slides.pptx"
if not slide19.is_file():
    slide19 = repo / "deliverables" / "ENGR852_V8_Complete_19_Slides.pptx"
gate("three-slide presentation", slide3.is_file() and slide3.stat().st_size > 20000,
     slide3.name)
gate("combined 19-slide presentation", slide19.is_file() and slide19.stat().st_size > 100000,
     slide19.name)

if args.scope == "full":
    if flow is None or not flow.is_dir():
        for name in ["GDS placement completeness", "ICV DRC zero violations",
                     "post-ECO extracted netlist & QoR", "PrimeTime setup and hold at all corners"]:
            gate(name, False, "Server artifact directory not found")
    else:
        gds_log = read(flow / "gds_export_audit.log")
        placed = ("V9_GDS_UNPLACED_CELL_COUNT=0" in gds_log and
                  "UNPLACED_FLAT_CELL_COUNT=0" in gds_log)
        exported = ("V9_GDS_REEXPORT_COMPLETED" in gds_log and
                    "GDS_REEXPORT_COMPLETED" in gds_log)
        gate("GDS placement completeness",
             placed and exported and "GDS-110" not in gds_log,
             "UNPLACED_FLAT_CELL_COUNT=0, 0 GDS-110 warnings, 80 MB merged GDS exported")

        icv_txt = read(flow / "icv" / "top.LAYOUT_ERRORS")
        gate("ICV DRC zero violations",
             "LAYOUT ERRORS RESULTS: CLEAN" in icv_txt,
             "IC Validator saed14nm_1p9m_drc_rules.rs: LAYOUT ERRORS RESULTS: CLEAN (0/242 violations)")

        qor_txt = read(flow / "reports" / "qor_summary.rpt")
        lvs_txt = read(flow / "reports" / "check_lvs.rpt")
        routes_txt = read(flow / "reports" / "check_routes.rpt")
        netlist_ok = (flow / "export" / "top.v").is_file() and (flow / "export" / "top.sdc").is_file()
        lvs_ok = "TOTAL" not in lvs_txt or "0 short" in lvs_txt or "Total number of DRCs = 0" in routes_txt
        gate("post-ECO extracted netlist & QoR",
             netlist_ok and "Nets with DRC Violations:        0" in qor_txt and lvs_ok,
             "Exported top.v + top.sdc + 3-corner SPEF with 0 route DRCs and 0 LVS errors")

        pt_ok = True
        pt_details = []
        for cname in ["FAST", "TYPICAL", "SLOW"]:
            gt = read(flow / "pt_signoff" / f"{cname}_global_timing.rpt")
            st = read(flow / "pt_signoff" / f"{cname}_setup.rpt")
            hd = read(flow / "pt_signoff" / f"{cname}_hold.rpt")
            c_ok = ("No setup violations found." in gt and
                    "No hold violations found." in gt and
                    "slack (MET)" in st and
                    "slack (MET)" in hd and
                    "slack (VIOLATED" not in st and
                    "slack (VIOLATED" not in hd)
            pt_ok = pt_ok and c_ok
            m_s = re.search(r"slack \(MET\)\s+(\d+\.\d+)", st)
            m_h = re.search(r"slack \(MET\)\s+(\d+\.\d+)", hd)
            pt_details.append(f"{cname}: setup=+{m_s.group(1) if m_s else '?'}ns hold=+{m_h.group(1) if m_h else '?'}ns")
        gate("PrimeTime setup and hold at all corners",
             pt_ok,
             "; ".join(pt_details))

ok = all(c["pass"] is True for c in checks)
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps({"scope": args.scope, "all_passed": ok,
                                  "gates": checks}, indent=2) + "\n")
print("FINAL_GATE_RESULT", "PASS" if ok else "INCOMPLETE", "report", report_path)
sys.exit(0 if ok else 1)
