#!/usr/bin/env python3
"""Fail-fast local RTL regression; use the existing corrected design unchanged."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
out = root / "qa_runs"
out.mkdir(exist_ok=True)
tests = sorted(root.glob("motion_*tb.sv"))
results = []
for executable in ("iverilog", "vvp"):
    if shutil.which(executable) is None:
        print(f"ERROR missing required simulator executable: {executable}", file=sys.stderr)
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
        # This negative-control test reproduces the original 8-bit saturation limit.
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
    compile_cmd = ["iverilog", "-g2012", "-Wall", "-DIVL_SIM", "-s", module,
                   "-o", str(binary), str(rtl), str(tb)]
    try:
        compiled = subprocess.run(compile_cmd, cwd=root, text=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
        compile_log.write_text(compiled.stdout)
        if compiled.returncode:
            results.append({"test": stem, "status": "COMPILE_FAIL",
                            "detail": compiled.stdout[-500:]})
            print(stem, "COMPILE_FAIL")
            continue
        executed = subprocess.run(["vvp", str(binary)], cwd=root, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=65)
        run_log.write_text(executed.stdout)
        status = "PASS" if executed.returncode == 0 else "RUN_FAIL"
        results.append({"test": stem, "rtl": str(rtl.relative_to(project)),
                        "status": status, "detail": executed.stdout[-500:]})
        print(stem, status)
    except subprocess.TimeoutExpired:
        results.append({"test": stem, "status": "TIMEOUT",
                        "detail": "Simulator exceeded configured time limit"})
        print(stem, "TIMEOUT")
(out / "summary.json").write_text(json.dumps(results, indent=2))
print("SUMMARY", sum(x["status"] == "PASS" for x in results), "/", len(results))
sys.exit(0 if all(x["status"] == "PASS" for x in results) else 1)
