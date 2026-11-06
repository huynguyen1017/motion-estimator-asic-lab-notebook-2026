# UPDATE-021 — V6: real 520 MHz regressions, GDS re-export and clear test-case labels

**Execution date:** November 6, 2026 (PST).
**Implementation:** ENGR 852 motion estimator, SAED14, Synopsys VCS / Verdi / Fusion Compiler / ICV / PrimeTime.

## Correct interpretation of BestDist

The previously shown hexadecimal `FF00` is **not** the expected result of the team perfect-match testbench. It belongs to a separate directed **high-contrast stress test**, in which 256 reference pixels are `00` and the corresponding search pixels are `FF`. The 16-bit SAD is `256 * 255 = 65280 = 16'hFF00`.

The team's perfect-match case contains an exact match and therefore must produce `16'h0000`, even after widening the accumulator. The nonzero perturbation case gives `16'h0003`.

The original 8-bit professor RTL saturates to `8'hFF` in the stress case and fails to select a motion vector because the comparator's strict-less-than logic never sees a value smaller than its reset `FF`. Corrected full-precision RTL returns `FF00` with signed vector `(-8,-8)` **for this stress stimulus only**. This is a genuine corner-case failure; it does not mean the team source/testbench should report `FF00`.

## V6 source alignment and exact changes

The name-neutral source of record is `verification/v6_clean/top.v`, byte-identical to `rtl/verified/top.v`. It retains the original `top`, `control`, `PE`, `PEend`, `PEtotal`, and `Comparator` hierarchy, candidate-scanning scheme, 16-PE pipeline, signed four-bit vector convention, and reference/search memory interfaces. Corrections widen the accumulator buses, individual PE outputs and comparator datapath from 8 to 16 bits, initialize `BestDist` to `FFFF`, and hold completed results stable. No reference/search arrays are included in the synthesizable module hierarchy. Professor-original RTL remains archived unchanged in `rtl/top.v`.

Every new verification source and script in `verification/v6_clean/` was checked for the user's personal-name identifier and was name-neutral. Older original evidence/testbench file names are preserved for reproducibility rather than rewritten retrospectively.

## Actual RTL run — November 6, 2026

`cd verification/v6_clean && python3 run_regression.py`

**Result: 7/7 simulation processes passed, exit 0**, using Icarus Verilog. The original saturation reproduction is intentionally a *negative control* and is not proof of the original RTL's correctness.

The previously print-only three-case baseline motion testbench was revised in the V6 clean copy to add independent `$fatal` assertions for all three final output tuples. Rerunning the full suite returned:

| Directed case | BestDist | motionX | motionY | Result |
|---|---:|---:|---:|---|
| Original exact match | `00` | `7` | `8` (signed -8) | PASS |
| +3 perturbation | `03` | `E` (signed -2) | `D` (signed -3) | PASS |
| Upper boundary | `00` | `7` | `7` | PASS |

The corrected V5 16-bit top-level test likewise reports `3/3` passing cases and matching values `0000, 0003, 0000`. Previous Synopsys VCS/Verdi native waveform captures remain evidence of the actual hardware-description simulation; the name-neutral local regression is a separate validation pass.

## GDS placement investigation — successful new export

The earlier `v5_stage_logs/signoff.log` contained `GDS-110` unplaced-cell warnings. A fresh **read-only diagnostic on the routed `top/signoff_v5` checkpoint** found:

- `ctl_u/count_reg[0]`: `physical_status=placed`; `is_placed=true`, origin `34.1560 9.2000`.
- `get_flat_cells -filter {physical_status==unplaced}`: **zero** cells.
- `check_legality`: completed without error.
- The native `write_gds` command returned **0**, with **no `GDS-110` warnings**.
- New actual tool-produced GDS: `results/v6_signoff_v5_reexport.gds`, approximately **80 MB**.

The new export is retained **on the engineering server** and was not included in the public repository because it embeds foundry/standard-cell library geometry and other licensed technology content. The original GDS was not overwritten. This establishes clean placement and GDS export for the *existing V5 checkpoint*. It does not establish final sign-off after unresolved DRC/timing ECOs.

Reproduction scripts: `scripts/v6_gds_placement_audit.tcl` and `scripts/v6_gds_export_audit.tcl` in the authenticated `20_v5b_520MHz_14nm_cts_area_fix` workspace; logs in `v6_probe/gds_placement_audit.log` and `v6_probe/gds_export_audit.log`.

## Presentations: geometry and test-case labeling fixed

The V5 full-team deck contained a scale mismatch on slide 19: a 13.33 x 7.5-inch physical-results slide was appended to a 10 x 5.625-inch team file without proportional geometry scaling. V6 scales slide 19 to the team canvas and checks all its objects fit. Slides 1–16 are preserved unchanged, including text and object geometry.

The two independent Verdi waveform slides now explicitly distinguish the all-`00`/all-`FF` stress test from the team's normal `0000` perfect match. The slides use actual existing Synopsys nWave captures and never represent recreated waveform data.

- `deliverables/ENGR852_V6_Motion_Estimator_3_Contribution_Slides.pptx`
- `deliverables/ENGR852_V6_Motion_Estimator_Full_Team_19_Slides.pptx`

PPTX validation passed; Apple Keynote PDF export timed out with AppleEvent `-1712`. That is an export-program limitation, not evidence that a PDF was created. No PDF success is claimed without an actual verified file.

## Physical-design gates still open

The existing V5 extracted three-corner PrimeTime measurements are FAST hold WNS `-0.14 ns` (402 paths), TYPICAL hold WNS `-0.12 ns` (120 paths), SLOW hold WNS `-0.09 ns` (33 paths), and SLOW setup WNS `-0.06 ns` (17 paths). An in-memory SLOW timing ECO improved to `-0.02 ns` with two remaining paths, **not yet physically placed/routed**.

The baseline V5 ICV DRC result remains **18 violations**. Additional isolated ICV/repair trials produced nonzero counts (8, 12, 41, 435 depending on checkpoint); an ordinary routing tool's zero-violation result does not override sign-off ICV. Runs that worsen DRC must be rejected rather than promoted.

**Acceptance conditions for complete sign-off remain:**

1. ICV DRC completes with zero applicable violations on the final **corrected** layout.
2. All final-layout standard cells are placed, and the final GDS export has zero unplaced-cell warnings.
3. Hold ECO routes legally without creating new DRC issues.
4. The SLOW setup and all three hold checks meet nonnegative slack with zero violating paths at 520 MHz, 0.5 ns input/output delays, and 0.2 ns uncertainty.
5. SPEF, power, layout area, gate-level netlist, DRC and PrimeTime reports are regenerated from the **same** final accepted routed checkpoint.
6. The report and presentation are updated from genuine post-ECO measurements.

The course's 90–100 criteria require completing these steps, not changing status labels or replacing missing reports with estimates.


## Updated electronic engineering report

The [V6 nine-page PDF report](../deliverables/ENGR852_V6_Motion_Estimator_Engineering_Report.pdf) retains the seven-page V5 measured report and appends two pages correcting the normal 0000 / stress-case FF00 distinction, confirming the new zero-unplaced-cell GDS export, and listing the remaining unclosed DRC/setup/hold gates. Both addendum pages were rendered and visually inspected. This is a measured checkpoint report, not a claim of physical sign-off.
