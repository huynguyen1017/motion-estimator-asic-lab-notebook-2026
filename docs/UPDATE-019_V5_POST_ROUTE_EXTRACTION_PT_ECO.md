# UPDATE-019 — V5 routed physical implementation, extracted PrimeTime and timing ECO

**Date:** November 5, 2026, PST. **Design:** ENGR 852 16-bit SAD Motion Estimator, SAED14 RVT, 520 MHz. All numbers below are from actual Synopsys Fusion Compiler / IC Validator / PrimeTime reports unless explicitly identified as calculations. The previous V3 and V4 artifacts remain intact.

## Recovered from the interruption

The V5 isolated workspace `20_v5b_520MHz_14nm_cts_area_fix` started with the same corrected 16-bit V3B RTL and unchanged 520 MHz timing specification, but resized the floorplan from 60% to a **35% target utilization**. Synopsys reported an initial **35.44% floorplan utilization**. The original V3B CTS had failed at **112.88% over-utilization**, requiring 1,977 square micrometers against 1,752 available; the floorplan change was a measured correction.

| Tool stage | Native tool checkpoint |
|---|---|
| Full 16-bit VCS testbench | PASS: 3/3 directed motion-vector tests (original fixture, SAD=3 perturbation, final boundary) |
| Initial SAED14 mapping | PASS; original 16-bit mapped area 1,193.03 µm² |
| V5 new floorplan | PASS; reported 35.44% utilization |
| V5 place_opt | PASS; finalized November 5 at 10:43:52 PST |
| V5 clock_opt (CTS) | PASS; finalized November 5 at 10:55:55 PST |
| V5 route_opt / detailed route | PASS; finalized November 5 at 11:01:27 PST; **zero route shorts, zero floating-route violations, total 0 route violations** |
| V5 signoff tool script | Completed the command sequence at 11:04:18 PST; final DRC/GDS are **NOT clean** (see below) |
| Extracted parasitics | PRESENT; three genuine routed SPEF corners, approx. 8.8 MB each |
| PrimeTime post-route max/min timing | EXECUTED for three PVT / SPEF combinations using a compatible SDC 2.1 derivative; reports contain genuine timed paths and violations |
| Physical sign-off | **NOT PASSED** until DRC, all setup and all hold paths close, and GDS unplaced-cell warnings are eliminated |

### Extracted SPEF / actual exported design files

The course `write_parasitics -format SPEF -output ./results/top.spef` command generates **multiple filenames**, not a single file named `top.spef`. The missing-single-file assertion was a script error rather than missing extraction:

- `top.spef.minTLU_125.spef`: fast parasitic scenario.
- `top.spef.nomTLU_25.spef`: nominal parasitic scenario.
- `top.spef.maxTLU_-40.spef`: slow parasitic scenario.

The course flow also generated `results/top.v` (a real routed gate-level netlist), `results/top.sdc`, and `results/top.gds` (about 20 MB). The GDS is **not accepted as clean final layout** because Fusion issued `GDS-110` unplaced-cell warnings.

## Quantitative routed results

| Property | Measured |
|---|---:|
| Technology mapped to | SAED14 RVT |
| Clock target | 520 MHz / 1.923 ns |
| Input delay | 0.500 ns |
| Output delay | 0.500 ns |
| Clock uncertainty | 0.200 ns |
| Routed cell count | 6,310 |
| Routed combinational cells | 5,861 |
| Routed sequential cells | 449 |
| Routed buffer/inverter cells | 4,547 |
| Macro/black box count | **0** (testbench memories excluded) |
| Routed standard-cell area | **2,781.30 µm²** |
| Floorplan DEF die bounding box | 92.510 µm × 50.800 µm = **4,699.508 µm²** (bounding/die area, not cell area) |
| Typical-corner voltage / temp | 0.80 V / 25°C |
| Typical estimated dynamic power | 7.28e+08 pW = **0.728 mW** |
| Typical estimated leakage power | 7.75e+05 pW = **0.000775 mW** |
| Typical estimated total power | 7.29e+08 pW = **0.729 mW** |

These are post-route **Fusion Compiler report** values. Power uses the tool's internally propagated switching-activity assumptions; it is not a measured chip-lab power figure or a VCD-driven final activity annotation.

## PrimeTime timing: true post-layout setup AND hold

Fusion exported SDC version 2.2, which the installed PrimeTime release rejected. The initial PrimeTime run consequently generated empty, unconstrained reports and was **discarded**. A derived, fully versioned SDC copy changed only the tool version marker to **2.1**, then PVT-specific library references were adjusted to match the selected technology file. The actual clock, delays and uncertainty stayed unchanged.

The error-free PrimeTime rerun selected the matching cell-library corner and its paired extracted SPEF:

| Cell corner / SPEF | Setup WNS | Setup violations | Hold WNS | Hold TNS | Hold violations |
|---|---:|---:|---:|---:|---:|
| FAST (FF, 0.88V, 125°C / minTLU_125) | **+0.52 ns** | **0** | **−0.14 ns** | **−12.96 ns** | **402** |
| TYPICAL (TT, 0.80V, 25°C / nomTLU_25) | **+0.30 ns** | **0** | **−0.12 ns** | **−4.76 ns** | **120** |
| SLOW (SS, 0.72V, −40°C / maxTLU_-40) | **−0.06 ns** | **17** | **−0.09 ns** | **−1.24 ns** | **33** |

**Interpretation:** setup is met at FAST and TYPICAL but fails at SLOW. Hold fails at all three. **Timing closure has NOT been achieved.** Numbers are actual extracted post-layout PrimeTime reports, unlike prior compile-stage slack.

## IC Validator design-rule checks

The final course-run ICV DRC on the routed `signoff_v5` block tested **242 rules** and reported **18 violations across 3 checks**:

- `M2.S.2`: 6 insufficient M2 spacing violations.
- `M2.S.3`: 6 insufficient M2 wide-metal spacing violations, partially overlapping the previous M2 locations.
- `M5.W.1`: 6 invalid M5 metal-width violations.

The earlier route-tool `TOTAL 0 Violations` is a **different check**, not signoff ICV DRC. The course `signoff_fix_drc` stage ran but did not eliminate the final ICV violations. Missing legal filler cell width combinations and `GDS-110` unplaced-cell warnings are additionally recorded. A final sign-off PASS must explicitly rerun ICV and have zero applicable violations and no unplaced cells.

## PrimeTime guided hold repair (in a separate versioned block)

The provided course `scripts/pt_eco.tcl` prescribes `fix_eco_timing -type hold` and `write_changes -format icc2tcl`. This was successfully executed for the FAST corner using the listed SAED14 ECO buffer cells:

- **731 `insert_buffer` commands** in a 146 KB ECO script, plus cell-sizing changes.
- PrimeTime estimated **412.70 µm² additional buffer area**.
- PrimeTime's in-memory ECO optimizer reported no remaining FAST hold violations after the ECO.
- Actual physical repair requires applying these changes in Fusion Compiler, legalization, rerouting, new DRC and SPEF and **all-three-corner PrimeTime recheck**. The ECO in-memory result is NOT final sign-off.

The ECO application was launched in an independent copied design block named `signoff_v5_holdfix1`, preserving the original `signoff_v5` checkpoint. It must be checked for successful route completion, correct power/ground connectivity and final timing before publishing any PASS claim.

## Course 90–100 rubric: remaining acceptance gates

1. Corrected 16-bit RTL plus actual native Synopsys VCS/Verdi verification: accomplished for documented directed fixtures; expand randomized top-level coverage if needed.
2. Synthesized gate-level netlist and exact 1.923ns, 0.5ns, 0.2ns SDC: available, with final ECO netlist still dependent on timing repair.
3. Floorplan, CTS and route: verified completed with native tool reports.
4. Final DRC: **18 violations remain** in current exported checkpoint.
5. Final parasitic extraction: three routed SPEF scenarios verified; repeat after any timing ECO.
6. PrimeTime post-layout setup **and** hold: reports now exist with complete results; violations remain.
7. Final GDS: generated, but **GDS-110 unplaced-cell warning** requires investigation and correction.
8. Final report and presentation: V4 artifacts exist; update the technical physical slide and report with only verified repaired metrics.

**Do not label this project 90–100 ready until the violating steps are corrected, rerun, and checked.** Preserve the failed checkpoints as valid engineering evidence of problem identification and subsequent design optimization.

## Evidence provenance

The V5 work was performed on the authorized course Linux server using Synopsys VCS W-2024.09-1, Fusion Compiler X-2025.06-SP2a, PrimeTime U-2022.12-SP5-3, IC Validator W-2024.09-3, and the SAED14 RVT teaching library. Previous V4 files and teammates' slides are unchanged. Credential strings, individual identifiers and licensed cell libraries are not included in this public notebook.
