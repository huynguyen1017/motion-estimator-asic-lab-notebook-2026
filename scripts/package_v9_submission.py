#!/usr/bin/env python3
"""Package the V9 Final Verified Submission and Evidence Bundle for ENGR 852 Motion Estimator."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import json

REPO = Path("/Users/huynguyen/Developer/portfolio/motion-estimator-asic-lab-notebook-2026")
OUT = REPO / "deliverables"
OUT.mkdir(exist_ok=True)
ARCHIVE_V9 = OUT / "ENGR852_V9_Final_Submission_and_Evidence_Bundle.zip"
ARCHIVE_V4 = OUT / "ENGR852_V4_Submission_and_Evidence_Bundle.zip"

items = [
    ("report/ENGR852_V9_Final_Motion_Estimator_Engineering_Report.pdf", OUT / "ENGR852_V9_Final_Motion_Estimator_Engineering_Report.pdf"),
    ("presentation/ENGR852_V9_Complete_19_Slides.pptx", OUT / "ENGR852_V9_Complete_19_Slides.pptx"),
    ("presentation/ENGR852_V9_Complete_19_Slides.pdf", OUT / "ENGR852_V9_Complete_19_Slides.pdf"),
    ("presentation/ENGR852_V9_Clean_3_Contribution_Slides.pptx", OUT / "ENGR852_V9_Clean_3_Contribution_Slides.pptx"),
    ("rtl/top_original_8bit.v", REPO / "rtl/top.v"),
    ("rtl/top_16bit_full_precision_finish_hold.v", REPO / "rtl/experimental/top_full_precision_finish_hold.v"),
    ("constraints/top_520mhz.sdc", REPO / "constraints/top_520mhz.sdc"),
    ("testbench/top_tb.v", REPO / "tb/top_tb.v"),
    ("testbench/top_tb_direct.v", REPO / "tb/top_tb_direct.v"),
    ("testbench/motion_verification_520mhz_tb.v", REPO / "tb/motion_verification_520mhz_tb.v"),
    ("verification/motion_v5_16bit_top_regression_tb.sv", REPO / "rtl/experimental/motion_v5_16bit_top_regression_tb.sv"),
    ("verification/motion_v3_all_saturated_tb.sv", REPO / "rtl/experimental/motion_v3_all_saturated_tb.sv"),
    ("verification/motion_v3_full_precision_tb.sv", REPO / "rtl/experimental/motion_v3_full_precision_tb.sv"),
    ("verification/motion_v3_hold_tb.sv", REPO / "rtl/experimental/motion_v3_hold_tb.sv"),
    ("verification/motion_pe_fullprecision_scoreboard_tb.sv", REPO / "rtl/experimental/motion_pe_fullprecision_scoreboard_tb.sv"),
    ("evidence/waveforms/V9_fig7_orig8bit_row1_nWave.png", REPO / "evidence/screenshots/V9_fig7_orig8bit_row1_nWave.png"),
    ("evidence/waveforms/V9_fig8_orig8bit_complete_nWave.png", REPO / "evidence/screenshots/V9_fig8_orig8bit_complete_nWave.png"),
    ("evidence/waveforms/V9_fig9_16bit_saturation_row1_nWave.png", REPO / "evidence/screenshots/V9_fig9_16bit_saturation_row1_nWave.png"),
    ("evidence/waveforms/V9_fig10_16bit_perfect_match_0000_nWave.png", REPO / "evidence/screenshots/V9_fig10_16bit_perfect_match_0000_nWave.png"),
    ("evidence/layout/v9_signoff_clean_layout.png", REPO / "evidence/screenshots/v9_signoff_clean_layout.png"),
    ("physical_design/netlist_and_sdc/top.v", REPO / "evidence/v9_signoff/export/top.v"),
    ("physical_design/netlist_and_sdc/top.sdc", REPO / "evidence/v9_signoff/export/top.sdc"),
    ("physical_design/reports/qor_summary.rpt", REPO / "evidence/v9_signoff/reports/qor_summary.rpt"),
    ("physical_design/reports/qor.rpt", REPO / "evidence/v9_signoff/reports/qor.rpt"),
    ("physical_design/reports/area_utilization.rpt", REPO / "evidence/v9_signoff/reports/area_utilization.rpt"),
    ("physical_design/reports/design_physical.rpt", REPO / "evidence/v9_signoff/reports/design_physical.rpt"),
    ("physical_design/reports/power.rpt", REPO / "evidence/v9_signoff/reports/power.rpt"),
    ("physical_design/reports/timing_max.rpt", REPO / "evidence/v9_signoff/reports/timing_max.rpt"),
    ("physical_design/reports/timing_min.rpt", REPO / "evidence/v9_signoff/reports/timing_min.rpt"),
    ("physical_design/reports/global_timing_max.rpt", REPO / "evidence/v9_signoff/reports/global_timing_max.rpt"),
    ("physical_design/reports/global_timing_min.rpt", REPO / "evidence/v9_signoff/reports/global_timing_min.rpt"),
    ("physical_design/reports/clock_qor.rpt", REPO / "evidence/v9_signoff/reports/clock_qor.rpt"),
    ("physical_design/reports/constraints_violators.rpt", REPO / "evidence/v9_signoff/reports/constraints_violators.rpt"),
    ("physical_design/reports/check_legality.rpt", REPO / "evidence/v9_signoff/reports/check_legality.rpt"),
    ("physical_design/reports/check_routes.rpt", REPO / "evidence/v9_signoff/reports/check_routes.rpt"),
    ("physical_design/reports/check_lvs.rpt", REPO / "evidence/v9_signoff/reports/check_lvs.rpt"),
    ("physical_design/drc_icv/top.LAYOUT_ERRORS", REPO / "evidence/v9_signoff/icv/top.LAYOUT_ERRORS"),
    ("physical_design/gds_audit/gds_export_audit.log", REPO / "evidence/v9_signoff/gds_export_audit.log"),
    ("primetime_signoff/FAST_violators.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_violators.rpt"),
    ("primetime_signoff/FAST_global_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_global_timing.rpt"),
    ("primetime_signoff/FAST_setup.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_setup.rpt"),
    ("primetime_signoff/FAST_hold.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_hold.rpt"),
    ("primetime_signoff/FAST_check_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_check_timing.rpt"),
    ("primetime_signoff/FAST_analysis_coverage.rpt", REPO / "evidence/v9_signoff/pt_signoff/FAST_analysis_coverage.rpt"),
    ("primetime_signoff/TYPICAL_violators.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_violators.rpt"),
    ("primetime_signoff/TYPICAL_global_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_global_timing.rpt"),
    ("primetime_signoff/TYPICAL_setup.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_setup.rpt"),
    ("primetime_signoff/TYPICAL_hold.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_hold.rpt"),
    ("primetime_signoff/TYPICAL_check_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_check_timing.rpt"),
    ("primetime_signoff/TYPICAL_analysis_coverage.rpt", REPO / "evidence/v9_signoff/pt_signoff/TYPICAL_analysis_coverage.rpt"),
    ("primetime_signoff/SLOW_violators.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_violators.rpt"),
    ("primetime_signoff/SLOW_global_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_global_timing.rpt"),
    ("primetime_signoff/SLOW_setup.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_setup.rpt"),
    ("primetime_signoff/SLOW_hold.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_hold.rpt"),
    ("primetime_signoff/SLOW_check_timing.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_check_timing.rpt"),
    ("primetime_signoff/SLOW_analysis_coverage.rpt", REPO / "evidence/v9_signoff/pt_signoff/SLOW_analysis_coverage.rpt"),
]

manifest = {}
for arc, src in items:
    if not src.is_file():
        raise SystemExit(f"MISSING REQUIRED PACKAGE FILE {arc}: {src}")
    data = src.read_bytes()
    manifest[arc] = {"sha256": sha256(data).hexdigest(), "bytes": len(data)}

notice = """ENGR 852 Motion Estimator - V9 Final Verified ASIC Sign-Off Package
===================================================================
All project requirements are 100% VERIFIED:
- Clock Frequency: 520 MHz (1.923 ns clock period)
- Input / Output Delay: 0.500 ns | Clock Uncertainty: 0.200 ns
- Synthesized Memory Macros: 0 (ROM_R and ROM_S in testbench only)
- Physical Design Area: 3,416.18 um2 netlist cell area (52.08% util; 7,854.40 um2 die)
- Total Power (TT 0.80V 25C): 0.890 mW (0.889 mW dynamic + 0.000892 mW leakage)
- IC Validator Sign-Off DRC: CLEAN (0 violations across all 242 rules)
- ZRT Routing & LVS: CLEAN (0 open nets, 0 shorts, 0 routing DRCs across 8,644 nets)
- Standalone 3-Corner PrimeTime STA (Setup & Hold with SPEF):
  * FAST (FF 0.88V 125C + minTLU_125.spef): Setup WNS = +0.71 ns (0 viol) | Hold WNS = +0.00 ns (0 viol)
  * TYPICAL (TT 0.80V 25C + nomTLU_25.spef): Setup WNS = +0.54 ns (0 viol) | Hold WNS = +0.04 ns (0 viol)
  * SLOW (SS 0.72V -40C + maxTLU_-40.spef): Setup WNS = +0.22 ns (0 viol) | Hold WNS = +0.14 ns (0 viol)
"""

for archive in (ARCHIVE_V9, ARCHIVE_V4):
    with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=6) as z:
        z.writestr("READ_ME_FIRST.txt", notice)
        for arc, src in items:
            z.write(src, arc)
        z.writestr("SHA256_MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(items) + 2

print("V9_PACKAGE_CREATED:", ARCHIVE_V9.name, "BYTES:", ARCHIVE_V9.stat().st_size, "FILES:", len(manifest) + 2)
