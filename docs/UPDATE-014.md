# UPDATE-014 — V2 full-motion traces, repaired slides and grading readiness

**Date:** 2026-11-04 (PST). **Scope:** Huy's independent verification and presentation revision. Original professor/team `top.v` retained. No private university identifier appears in this public record.

## Run reproduced on SFSU Synopsys VCS

- Work directory: `~/ENGR852_Project/09_v2_fullmotion_waveform_20261104/`.
- Testbench: [`verification/huy_fullmotion_v2_tb.sv`](../verification/huy_fullmotion_v2_tb.sv).
- RTL: unchanged reference source `top.v` (memories remain testbench-only).
- Simulated clock period: `1.923 ns` (`always #0.9615`; `timescale 1ns/100fs`).
- Compiler: Synopsys VCS W-2024.09-1, `V2_COMPILE_EXIT=0`.
- Simulation: `V2_SIM_EXIT=0`.
- FSDB output: `huy_motion_v2_520mhz.fsdb`, 43 KB on the university server.
- Directed T1: `BestDist=00`, `motionX=7`, `motionY=8` interpreted as `(+7,-8)`; `newBest` at count 271, simulation time 522.1145 ns. Full-search elapsed duration 7905.4530 ns.
- Perturbed T2: `BestDist=03`, `motionX=E`, `motionY=D` interpreted as `(-2,-3)`; `newBest` at count 1542, 2965.2660 ns relative to that test.
- Boundary T3: `BestDist=00`, `motionX=7`, `motionY=7` interpreted as `(+7,+7)`; final candidate count 4111, 7905.4530 ns relative to that test. (The data-dependent comparator latches on the next relevant edge.)
- An independent PE/comparator VCS test previously passed **12/12** directed assertions. A separate three-seed VCS stress test made **24,576** PE/PEend comparisons against `min(full_precision_SAD,255)` with **zero mismatches**. These results do not prove a globally optimal full-precision motion vector in every saturation/tie case.

## Visual evidence: V1 retained / V2 generated from real simulator output

Verdi/nWave previously captured the original FSDB. A replay error caused by an unsupported `wvZoomFull` command was investigated and its use removed in the active replay script, with V1 preserved. New Verdi sessions were unreliable due to a Verdi-Elite license fallback warning, so V2 evidence used Synopsys `fsdb2vcd` conversion followed by Surfer 0.7.0 to display the **same actual VCS signals**; no waveform traces were invented, retimed, or redrawn.

Current public V2 screenshots:
- `evidence/screenshots/V2_Direct_Surfer_Waveform_Detailed.png` and full-application counterpart.
- `evidence/screenshots/V2_Perturbed_Surfer_Waveform_Detailed.png` and full-application counterpart.
- `evidence/screenshots/V2_PESaturation_Surfer_Waveform_Detailed.png` and full-application counterpart.

V2 screenshots contain actual app-window pixels. Private local status-path footer was masked only in the full-application versions; the detailed screenshots are native image crops of the real app, not generated approximations. Earlier V1 screenshots remain intact.

## Slide QA

A **copy** of the 16-slide teammate deck was extended to 19. Only slides 17–19 were updated to include V2 waveforms and academic, concise signal explanations:
17. Top-Level RTL Verification — 520 MHz, directed/perturbed matches.
18. PE RTL Verification — saturation, carry, comparator, 12/12 and 24,576 checks.
19. ASIC Synthesis and Timing Constraints — 1.923 ns, 0.5 ns input/output, 0.2 ns uncertainty; verified vs pending clearly separated.

Text-wrap overlap on slide 17 was corrected and PDF re-rendered. Pixel comparison against the V1 archive confirmed teammate slides 1, 4, 6, 10, 14, 16 were unchanged, and the other 1–16 slides were not edited in the source deck.

## Course-project major requirements: status

| Required element | Verified status |
| --- | --- |
| Original/debugged RTL, separate simulation testbench memories | Available; module `top` has no synthesized RAM |
| Simulation outputs and detailed waveform evidence | VCS verified, V2 evidence captured |
| 520 MHz SDC: 1.923 ns, 0.5 ns I/O delay, 0.2 ns uncertainty | Constraint script available; not proof of meeting timing |
| Generic gate synthesis | Yosys 3,254 generic cells; 277 DFFs, **not mapped SAED14 area** |
| 14 nm technology-mapped netlist, timing and power | **Not achieved** — license blocked |
| Placement, CTS, routing, layout, area, DRC, extraction | **Not achieved** — license blocked |
| PrimeTime post-layout setup and hold | **Not achieved** — needs extracted physical design |
| Final documentation, source listings, presentation and demo readiness | V2 presentation documented; final complete report requires actual PPA results |

Fusion Compiler X-2025.06-SP2 started but the `Fusion-Compiler-NX` license was not available, stopping before synthesis. Alternative Design Compiler O-2018.06-SP4 returned `DCSH-1` (not enabled). No mapped area, power, routed floorplan, DRC, parasitics, or post-layout PrimeTime reports exist. These are still major **grading blockers** under the instructor's 90–100-point criterion. The 2020 motion-estimator example report uses 32/28 nm at 130/260 MHz and must not be copied as the Fall 2026 14 nm, 520 MHz implementation.

**Required next milestone:** authorized university Fusion Compiler/Design Compiler access (or an instructor-approved equivalent) for SAED14 mapped synthesis; physical steps follow only after successful mapping. Preserve all tool logs and ask the instructor/IT about entitlement. Do not mislabel VCS behavioral results or Yosys statistics as physical sign-off.

## Interrupted-session recovery

- Live copy: [Google Slides](https://docs.google.com/presentation/d/1oQlE86P-1ajHd4VskT9jGiLGEXkxlMnqQ0_dutpmTPo/edit).
- Canonical public trace/repro archive: this repository, including `verification/`, `docs/`, `evidence/screenshots/` and `deliverables/`.
- Engineering log: [ENGR852 PROJECT Google Doc](https://docs.google.com/document/d/1UiReAPBHExrSvBnu2zGagSj2VUrMGXPIKgPJlKSNW7U/edit).
- Resume by reading this status, then check versioned file names and the most recent revision before any edits. Keep V1 and V2 independent and never overwrite the team's original Slides deck.
