# UPDATE-018: V5 full-precision regression and physical congestion correction

Date: November 5, 2026 (PST). Design: ENGR 852 Motion Estimator, SAED14 RVT, 520 MHz.

## Recovered actual Synopsys CTS failure

The V3B CTS log (from the original 16-bit implementation workspace) was inspected after the authenticated server login resumed. The earlier stalled command was not a valid CTS success. Its `clock_opt -to final_opto` stage failed with:
- `PLACE-006`: **112.88%** estimated placement utilization.
- **1,977 µm² required** versus **1,752 µm² available**.
- `PLACE-004`, `OPT-907`, and an explicit clock-tree optimization failure.

The original V3B work directory, logs, RTL and previous results are preserved for comparison.

## Congestion-repair V5 run — live checkpoint

A **new isolated workspace** `20_v5b_520MHz_14nm_cts_area_fix` was created on the course EDA host from the validated V3B mapped compile library and project scripts. Instead of modifying previous design blocks, all new physical-design blocks use distinct `_v5` names. The course floorplan utilization setting was reduced from 0.60 to **0.35**.

The new Synopsys Fusion Compiler floorplan stage **passed** and reported **35.44% actual core utilization**, verified from its generated tool output. The next stage is placement. The run is launched with `nohup` and timestamped stage logs; it is configured to stop on identified Synopsys errors and to require valid design-block outputs before starting each subsequent phase.

The job's intended sequence is:
`manual_floorplan_v5 -> place_opt_v5 -> clock_opt_v5 -> route_opt_v5 -> signoff_v5 -> extracted PrimeTime setup and hold`.

**A stage is not marked complete until its output log and artifacts have been inspected.** This file records the valid checkpoint, not a claim of complete sign-off.

## 520 MHz full-precision top-level regression — measured results

A portable self-checking testbench derived from the prior 520 MHz verification suite was run with Icarus Verilog against the *separate* V3B 16-bit full-precision, completion-hold RTL. The simulator uses a 0.9615 ns half-period, giving the required 1.923 ns full period. These results are actual local software simulator output; they are **not** represented as Synopsys VCS results or physical timing signoff.

| Test | Measured `BestDist` | Decoded `motionX, motionY` | Assertion |
|---|---|---|---|
| Original reference/search fixture | `0000` | (+7, -8) | PASS |
| One-pixel 3-level perturbation | `0003` | (-2, -3) | PASS |
| Last-window / boundary candidate | `0000` | (+7, +7) | PASS |

**3/3 top-level directed tests passed.** Earlier V3 tests separately reproduced the 8-bit saturation failure, confirmed the corrected FF00 full-precision SAD for an all-high-contrast block, and checked completion output stability. The original teaching RTL and the team presentation source remain unchanged.

Testbench: [motion_v5_16bit_top_regression_tb.sv](../verification/motion_v5_16bit_top_regression_tb.sv)
Run log: [V5_16bit_regression_results.log](../evidence/logs/V5_16bit_regression_results.log)

## Requirements coverage — course rubric audit

| Instructor requirement | Current factual checkpoint | Finish-line evidence |
|---|---|---|
| Debugged RTL | V3B widened SAD, corner-case fix, completion hold, top 3/3 regression | Broader random end-to-end coverage and documented remaining corner cases |
| Verilog testbench and stimuli | Original tests + new V5 self-checking testbench | Include final VCS run output |
| Functional waveforms | Actual Verdi/nWave FSDB V3/V4; local VCD | Final selected comparison figures |
| Synthesis gate netlist | V3B mapped SAED14 result | Export final gate-level Verilog |
| 520 MHz timing / 0.5 ns I/O / 0.2 ns uncertainty | Constraint files and compile-stage validation | Confirm final CTS and PrimeTime SDC readback |
| Memories excluded | Data inputs/addresses on RTL `top`; arrays in testbench | Retain no memory macros report |
| Physical layout | Floorplan V5 passed | Placement, CTS, route and GDS/DEF |
| Area and power | V3B mapped cell area 1,193.03 µm² | Post-route core/layout area and final power |
| DRC | Runset located in course files | Genuine complete DRC report / violation counts |
| Parasitic extraction | Course technology RC models configured | Extract routed SPEF and validate annotation |
| PrimeTime setup and hold | Compile-stage max slack is not sign-off | Post-layout max + min reports with worst slack |
| Report and slides | V4 full team deck, 3-slide contribution deck and six-page report | Add real final physical sign-off table and layout figures |
| Reproducibility | Source/scripts, hashes, logs and versioned checkpoint | Archive successful final layout / PT artifacts |
| Demo | RTL/waveforms and project slides prepared | Demonstrate completed physical results if requested |

**The 90–100 grading bracket is a project target, not a result asserted by this checkpoint.** All missing physical reports must be generated and checked.


## Independent Synopsys VCS crosscheck (November 5, 2026)

The same self-checking 16-bit top test was copied to an authenticated SFSU Linux session and rerun using **Synopsys VCS W-2024.09-1**. This is separate from the local Icarus run. The VCS source file order was corrected to put the timescaled testbench before `top.v`, resolving a compile-order timescale error without changing RTL logic.

The native VCS log shows all three target results and **`V5_TOP_REGRESSION_PASS 3/3`**, with **`V5_NATIVE_VCS_EXIT=0`**. The original raw run output was recovered and saved as [V5_native_synopsys_vcs_results.log](../evidence/logs/V5_native_synopsys_vcs_results.log). This gives an independently reproduced Synopsys functional test to accompany the mapped physical flow.
