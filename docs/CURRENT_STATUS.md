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

## Active Next Step on `mahmoodi.rcc.at.sfsu.edu`
1. **Verified:** `tcsh` and `csh` exist at `/usr/bin/tcsh` and `/usr/bin/csh`; `echo $version` returned `tcsh 6.20.00` in the existing SSH Terminal session.
2. **Observed:** the approved setup script was already sourced within an earlier `tcsh` shell and printed configuration banners for Synthesis, VCS, PrimeTime, ICC2, and Verdi. This is startup evidence, not a tool/license check; see [UPDATE-004](UPDATE-004.md) and [terminal excerpt](../evidence/transcripts/04-tcsh-and-synopsys-startup.txt).
3. **Next guided action:** in the current `tcsh` prompt run `which vcs`, then inspect its output before any further commands.
4. **Pending:** verify that remote `xterm &` actually opens a forwarded window on the Mac. Two local XQuartz xterm windows already exist, which is not a remote-GUI proof.
5. **Pending:** transfer a source copy, run licensed RTL verification, and complete physical implementation, extraction and PrimeTime setup/hold sign-off. None of these university outcomes is yet evidenced.

## Links
- **GitHub Repository:** https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026
- **Engineering Log (Google Doc):**
  - Tab 1 (`UPDATE-001`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.0
  - Tab 2 (`UPDATE-002`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.hxb3dr2qxpwb
  - Tab 3 (`UPDATE-003`): https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit?tab=t.yztt97virfy0
- **Team Presentation (Slides 14–16):** https://docs.google.com/presentation/d/1t5CEEyA1PofPH9xMRqVXnmPm-CgHQKg0qFEm4FciFgU/edit
