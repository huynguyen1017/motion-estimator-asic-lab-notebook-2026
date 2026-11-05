# Current Project Checkpoint

**Evidence capture:** `2026-11-04 17:26:03 PST` (`2026-11-05T01:26:03Z`); command execution times not separately captured.

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
5. **14 nm physical-flow blocker:** Verified SAED14 technology and RVT NDM/Liberty paths. Fusion Compiler X-2025.06-SP2 initial-map run **stopped before synthesis** because `Fusion-Compiler-NX` license was unavailable; Design Compiler O-2018.06-SP4 returned `DCSH-1` (not enabled). **No** 14 nm mapped area, power, placement, route, extraction, DRC, or PrimeTime sign-off has been produced.
6. **Presentation delivered:** Original **16 slides unchanged in a copy** plus 3 new evidence-backed contribution slides = **19 slides**. [Editable Google Slides](https://docs.google.com/presentation/d/1oQlE86P-1ajHd4VskT9jGiLGEXkxlMnqQ0_dutpmTPo/edit), [PPTX](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pptx), [PDF](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pdf).
7. **Remaining required actions:** Obtain instructor-approved tool license(s), then perform mapped synthesis, 14 nm floorplan, placement, CTS, routing, extraction, DRC, and PrimeTime setup/hold analysis. Add measured physical reports/screenshots to a future slide revision. Do not label any generic Yosys cell count or an SDC constraint as post-layout sign-off.

## Links
- **GitHub Repository:** https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026
- **Engineering Log (Google Doc):**
  - Tab 1 (`UPDATE-001`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.0
  - Tab 2 (`UPDATE-002`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.hxb3dr2qxpwb
  - Tab 3 (`UPDATE-003`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.yztt97virfy0
- **Team Presentation (Slides 14–16):** https://docs.google.com/presentation/d/1t5CEEyA1PofPH9xMRqVXnmPm-CgHQKg0qFEm4FciFgU/edit
