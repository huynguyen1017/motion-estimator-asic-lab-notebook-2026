**LATEST V7 checkpoint:** Three clean PowerPoint slides, full 19-slide copy, and a three-page rendered preview. Verified visual layout with original team slides unchanged. FF00 stress case explicitly distinguished from 0000 perfect match. GDS export placement was clean in the prior run, but zero-violation ICV and post-ECO PrimeTime remain unverified. See [UPDATE-022](UPDATE-022_V7_SLIDE_QA_AND_SIGNOFF_STATUS.md).

**LATEST V6 checkpoint (November 6, 2026):** The name-neutral RTL suite was rerun with explicit full-motion assertions: 7/7 tests passed; local RTL stage gate exits 0. Separate perfect-match and all-FF stress cases are labeled correctly in V6 slides, and the combined deck slide 19 clipping was fixed. Fusion Compiler reported 0 unplaced cells and generated a fresh warning-free GDS from the V5 checkpoint. Final ICV DRC, hold repair, SLOW setup, post-ECO SPEF and post-layout PrimeTime remain open; full-stage gate correctly exits 1. See [UPDATE-021](UPDATE-021_V6_GDS_REGRESSION_AND_SLIDE_CORRECTION.md).

**NOVEMBER 5 V5 PHYSICAL CHECKPOINT:** CTS and detailed routing pass; three extracted SPEFs and gate netlist exist; mapped post-route cell area 2,781.30 µm², typical estimated total power 0.729 mW. PrimeTime extracted fast/typical/slow timing reports show hold violations at all corners and 17 slow-corner setup violations. IC Validator reports 18 DRC violations. 731-buffer hold ECO generated, physical re-route attempted. [Full record](UPDATE-019_V5_POST_ROUTE_EXTRACTION_PT_ECO.md).

# Current Project Checkpoint

**Evidence capture:** `2026-11-04 17:26:03 PST` (`2026-11-05T01:26:03Z`); command execution times not separately captured.

**LATEST CHECKPOINT V4:** New native Verdi nWave figure captures, three-slide V4 PPTX/PDF, and complete 19-slide V4 PPTX/PDF were delivered. Original team slides 1–16 retain their text and layout. The remaining CTS/route/DRC/SPEF/PrimeTime sign-off status is detailed in [UPDATE-017](UPDATE-017_V4_FINAL_CHECKPOINT.md).

**LATEST CHECKPOINT:** Native VCS/Verdi V3 RTL evidence and native Fusion Compiler SAED14 mapped results are verified in [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md). Earlier V2 license statements are historical and superseded.

## Objective
Complete the ENGR 852 520 MHz Motion Estimator ASIC design, verification, synthesis, physical implementation, and sign-off workflow, maintaining a timestamped engineering portfolio and presentation deck.

## Completed & Verified Milestones
1. **University EDA Server Access (`UPDATE-001`, `2026-11-04 16:40 PST`):**
   - SFSU GlobalProtect VPN connected (`gp-students.sfsu.edu`).
   - Local XQuartz `xterm` launched on macOS.
   - SSH login to `mahmoodi.rcc.at.sfsu.edu` completed with X11 forwarding (`DISPLAY=localhost:12.0`).
2. **Remote EDA Server Environment & Synopsys Setup Audit (`UPDATE-002`, `2026-11-04 17:06:06 PST`):**
   - Verified server clock (`2026-11-04 17:06:06 PST (-0800)`), hostname (`mahmoodi.rcc.at.sfsu.edu`), working directory (`/home/<student-id>`), X11 forwarding cookie (`.Xauthority`, `70` bytes, `DISPLAY=localhost:12.0`), and global C-shell setup file (`/packages/synopsys/setup/synopsys_setup.tcl`, `431` bytes, `Nov 6 2024`) in [`evidence/transcripts/03-environment-diagnostics.txt`](../evidence/transcripts/03-environment-diagnostics.txt).
   - Identified that default login shell is `bash` (where `vcs`, `verdi`, `dc_shell`, `fc_shell`, and `pt_shell` are not on `PATH` until switching to `csh` and sourcing `/packages/synopsys/setup/synopsys_setup.tcl`).
3. **520 MHz RTL Verification, Pipeline Timing & Gate-Level Synthesis Audit (`UPDATE-003`, `2026-11-04 16:23–16:33 PST`):**
   - Executed 520 MHz (`1.9230 ns` period, `1ns/100fs`, `#0.9615`) simulation on [`rtl/top.v`](../rtl/top.v) across directed fixture (`ref.txt`, `search.txt`), perturbed non-zero SAD (`Rmem[0] += 3` at `(-2, -3)`), and upper-corner boundary `(+7, +7)` test cases ([`evidence/logs/huy_verification_520mhz.log`](../evidence/logs/huy_verification_520mhz.log)).
   - Derived exact cycle-level pipeline schedule (`4,111` cycles = `7,905.45 ns` at `520 MHz`, `30.88 fps` for `4,096` blocks/frame) and coordinate offset equations (`VectorX = count[3:0] - 8`, `VectorY = count[11:8] - 9`).
   - Verified external memory exclusion (`0` internal memory bits) and hierarchical cell/register breakdown (`3,254` generic cells, `277` flip-flops) via Yosys 0.70 ([`evidence/logs/huy_synthesis_stat.log`](../evidence/logs/huy_synthesis_stat.log)).
   - Prepared 520 MHz Synopsys Design Constraints ([`constraints/top_520mhz.sdc`](../constraints/top_520mhz.sdc)) and 3 technical slides ([`evidence/slides/`](../evidence/slides/)).

## Current status — November 4, 2026, after university tool execution

1. **Verified source:** Professor ZIP and untouched `top.v` transferred, SHA-256 validated, and extracted into `00_professor_zip_verified_20261104` without overwriting experiments.
2. **Actual university Synopsys VCS:** Baseline 50 MHz perfect-match simulation, separate 520 MHz simulation, and independent 12/12 PE/PEend/comparator directed checks all ran successfully; original `top.v` unchanged.
3. **Extended independent testing:** Three reproducible seeded VCS runs validated `16 blocks × 256 pixels × 2 variants × 3 seeds = 24,576` PE comparisons, **0 mismatches** against the saturating-SAD reference. Measured total of **10,656** samples where the full SAD exceeded 255. See [UPDATE-013](UPDATE-013.md), [new SystemVerilog checker](../verification/huy_pe_fullprecision_scoreboard_tb.sv).
4. **Actual waveform evidence:** Fresh trusted X11 (`ssh -Y`) repaired display forwarding. Verdi/nWave opened FSDB from university VCS and app-only screenshots were captured, privacy-reviewed, and saved in [screenshots](../evidence/screenshots/). An unsupported `wvZoomFull` replay command was removed; current waveform view does not depend on it.
5. **14 nm mapped ASIC evidence recovered in V3:** The official course-local Fusion setup successfully launched Fusion Compiler X-2025.06-SP2a. The original 8-bit RTL mapped to 1,693 cells / 881.96 square micrometers; the corrected 16-bit V3B mapped to 1,905 cells / 1,193.03 square micrometers. Both floorplans and V3B placement completed. The original 8-bit CTS stage failed at 111.73% over-utilization; V3B CTS final success, routing, DRC, parasitics and PrimeTime sign-off are not verified. See [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md).
6. **Presentation delivered:** Original **16 slides unchanged in a copy** plus 3 new evidence-backed contribution slides = **19 slides**. [Editable Google Slides](https://docs.google.com/presentation/d/1oQlE86P-1ajHd4VskT9jGiLGEXkxlMnqQ0_dutpmTPo/edit), [PPTX](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pptx), [PDF](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pdf).
7. **Remaining required actions:** Recover the V3B CTS job, adjust floorplan utilization if necessary, then complete routing, DRC, extraction, final PPA, and PrimeTime post-layout setup/hold with valid output artifacts. Do not mistake an initial mapped report for routed sign-off.

## Links
- **GitHub Repository:** https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026
- **Engineering Log (Google Doc):**
  - Tab 1 (`UPDATE-001`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.0
  - Tab 2 (`UPDATE-002`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.hxb3dr2qxpwb
  - Tab 3 (`UPDATE-003`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.yztt97virfy0
- **Team Presentation (Slides 14–16):** https://docs.google.com/presentation/d/1t5CEEyA1PofPH9xMRqVXnmPm-CgHQKg0qFEm4FciFgU/edit


## V2 delivery checkpoint — November 4, 2026 (after reconnect)

The live 19-slide copy was re-exported and QA-rendered. **The original 16 teammate slides remain unchanged.** Slides 17–19 use new measured VCS waveforms for directed match, perturbed nonzero SAD, and PE/comparator saturation. Figure-caption wrapping on slide 17 has been repaired.

- Reproducible VCS testbench: [verification/huy_fullmotion_v2_tb.sv](../verification/huy_fullmotion_v2_tb.sv).
- Actual detailed Surfer views of Synopsys FSDB/VCD: [evidence/screenshots](../evidence/screenshots/).
- Detailed evidence and recovery instructions: [UPDATE-014](UPDATE-014.md).
- **V3 supersedes this historical V2 license blocker:** The official local Fusion setup enabled actual SAED14 mapping, floorplan, and V3B placement. Original area 881.96 um2; V3B area 1,193.03 um2. Routing, extraction, DRC and final PrimeTime setup/hold remain unverified. See [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md).

