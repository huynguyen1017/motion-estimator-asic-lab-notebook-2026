# Current Project Checkpoint

**Last Updated:** `2026-11-04 17:06:00 PST` (`2026-11-05T01:06:00Z`)

## Objective
Complete the ENGR 852 520 MHz Motion Estimator ASIC design, verification, synthesis, physical implementation, and sign-off workflow, maintaining a timestamped engineering portfolio and presentation deck.

## Completed & Verified Milestones
1. **University EDA Server Access (`UPDATE-001`, `2026-11-04`):**
   - SFSU GlobalProtect VPN connected (`gp-students.sfsu.edu`).
   - Local XQuartz `xterm` launched on macOS.
   - SSH login to `mahmoodi.rcc.at.sfsu.edu` completed with X11 forwarding (`DISPLAY=localhost:12.0`).
2. **520 MHz RTL Verification, Pipeline Timing & Gate-Level Synthesis Audit (`UPDATE-002`, `2026-11-04 16:23–16:33 PST`):**
   - Executed 520 MHz (`1.9230 ns` period, `1ns/100fs`, `#0.9615`) simulation on [`rtl/top.v`](../rtl/top.v) across directed fixture (`ref.txt`, `search.txt`), perturbed non-zero SAD (`Rmem[0] += 3` at `(-2, -3)`), and upper-corner boundary `(+7, +7)` test cases ([`evidence/logs/huy_verification_520mhz.log`](../evidence/logs/huy_verification_520mhz.log)).
   - Derived exact cycle-level pipeline schedule (`4,111` cycles = `7,905.45 ns` at `520 MHz`, `30.88 fps` for `4,096` blocks/frame) and coordinate offset equations (`VectorX = count[3:0] - 8`, `VectorY = count[11:8] - 9`).
   - Verified external memory exclusion (`0` internal memory bits) and hierarchical cell/register breakdown (`3,254` generic cells, `277` flip-flops) via Yosys 0.70 ([`evidence/logs/huy_synthesis_stat.log`](../evidence/logs/huy_synthesis_stat.log)).
   - Prepared 520 MHz Synopsys Design Constraints ([`constraints/top_520mhz.sdc`](../constraints/top_520mhz.sdc)) and 3 technical slides ([`evidence/slides/`](../evidence/slides/)).

## Active Next Step on `mahmoodi.rcc.at.sfsu.edu`
1. **Pending:** run `command -v tcsh; command -v csh` in the existing university Bash session to determine whether a C-shell interpreter is available.
2. **Pending:** verify that a remote `xterm &` actually opens a window on the Mac.
3. **Pending:** load the approved Synopsys setup in a compatible shell, then verify each licensed tool; only afterward upload the exact sources and run VCS.
4. **Pending:** physical implementation, extracted-parasitic timing and PrimeTime setup/hold reports. No completed 14 nm physical sign-off is claimed.

## Links
- **GitHub Repository:** https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026
- **Engineering Log (Google Doc):** https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit
- **Team Presentation (Slides 14–16):** https://docs.google.com/presentation/d/1t5CEEyA1PofPH9xMRqVXnmPm-CgHQKg0qFEm4FciFgU/edit
