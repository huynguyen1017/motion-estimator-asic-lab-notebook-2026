#!/usr/bin/env python3
"""Fail-fast RTL regression supporting both Icarus Verilog (iverilog/vvp) and Synopsys VCS (vcs)."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
out = root / "qa_runs"
out.mkdir(exist_ok=True)
tests = sorted(root.glob("motion_*tb.sv"))
results = []

has_ivl = shutil.which("iverilog") is not None and shutil.which("vvp") is not None
has_vcs = shutil.which("vcs") is not None

if not has_ivl and not has_vcs:
    print("ERROR missing required simulator executable: neither iverilog/vvp nor vcs found", file=sys.stderr)
    sys.exit(2)

if not (root / "top.v").is_file() or not tests:
    print("ERROR missing RTL or testbench inputs", file=sys.stderr)
    sys.exit(2)

for tb in tests:
    source = tb.read_text(errors="replace")
    match = re.search(r"^\s*module\s+([A-Za-z_][A-Za-z0-9_$]*)\b", source, re.M)
    if not match:
        print(f"ERROR no Verilog module declaration in {tb.name}", file=sys.stderr)
        sys.exit(2)
    module = match.group(1)
    stem = tb.stem
    project = root.parents[1]
    if stem.startswith("motion_v5_"):
        rtl = root / "top.v"
    elif stem == "motion_v3_all_saturated_tb":
        # Negative-control test reproducing the original 8-bit saturation limit.
        rtl = project / "rtl/top.v"
    elif stem.startswith("motion_v3_"):
        rtl = project / "rtl/experimental/top_full_precision_finish_hold.v"
    else:
        rtl = project / "rtl/top.v"
    if not rtl.is_file():
        results.append({"test": stem, "status": "RTL_MISSING", "detail": str(rtl)})
        print(stem, "RTL_MISSING")
        continue
    binary = out / f"{stem}.simv"
    compile_log = out / f"{stem}.compile.log"
    run_log = out / f"{stem}.run.log"
    rtl_rel = os.path.relpath(rtl, root)
    if has_ivl:
        compile_cmd = ["iverilog", "-g2012", "-Wall", "-DIVL_SIM", "-s", module,
                       "-o", f"qa_runs/{stem}.simv", rtl_rel, tb.name]
        run_cmd = ["vvp", f"qa_runs/{stem}.simv"]
    else:
        compile_cmd = ["vcs", "-full64", "-sverilog", "+v2k", "-timescale=1ns/100fs",
                       "-top", module, "-o", f"qa_runs/{stem}.simv", rtl_rel, tb.name]
        run_cmd = [f"./qa_runs/{stem}.simv"]
    try:
        compiled = subprocess.run(compile_cmd, cwd=str(root), universal_newlines=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        compile_log.write_text(compiled.stdout)
        if compiled.returncode:
            results.append({"test": stem, "status": "COMPILE_FAIL",
                            "detail": compiled.stdout[-500:]})
            print(stem, "COMPILE_FAIL")
            continue
        executed = subprocess.run(run_cmd, cwd=str(root), universal_newlines=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=65)
        run_log.write_text(executed.stdout)
        status = "PASS" if executed.returncode == 0 and "ERROR" not in executed.stdout and "FAIL" not in executed.stdout else "RUN_FAIL"
        results.append({"test": stem, "rtl": rtl_rel,
                        "status": status, "detail": executed.stdout[-500:]})
        print(stem, status)
    except subprocess.TimeoutExpired:
        results.append({"test": stem, "status": "TIMEOUT",
                        "detail": "Simulator exceeded configured time limit"})
        print(stem, "TIMEOUT")
(out / "summary.json").write_text(json.dumps(results, indent=2))
print("SUMMARY", sum(x["status"] == "PASS" for x in results), "/", len(results))
sys.exit(0 if all(x["status"] == "PASS" for x in results) else 1)
