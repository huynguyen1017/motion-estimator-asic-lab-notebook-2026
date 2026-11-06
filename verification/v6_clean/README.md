# Revision-aware, name-neutral motion-estimator verification

This folder contains tested source copies with no personal-name prefixes in the Verilog or filenames. The instructor's RTL module hierarchy and algorithm are preserved, and `top.v` is the existing V3B/V5 16-bit precision and completion-qualified implementation, not the unmodified 8-bit professor baseline.

`python3 run_regression.py` requires `iverilog` and `vvp`. The runner discovers each testbench's actual module name, checks simulator availability, chooses the correct revision of RTL, uses Python execution timeouts, stores isolated logs under `qa_runs/`, and fails if any test fails. `IVL_SIM` guards only VCS/Verdi-specific FSDB waveform tasks; it does not change functional stimulus or hardware logic. VCS waveform generation remains enabled when `IVL_SIM` is not defined.

| Suite | RTL revision used | Purpose |
|---|---|---|
| motion_fullmotion_v2_tb | professor baseline `rtl/top.v` | Original 8-bit behavior |
| motion_pe_comparator_selfcheck_tb | professor baseline `rtl/top.v` | Processing element and comparator checks |
| motion_pe_fullprecision_scoreboard_tb | professor baseline `rtl/top.v` | Saturating 8-bit datapath checks |
| motion_v3_all_saturated_tb | professor baseline `rtl/top.v` | **Negative control**: reproduce original saturation/tie behavior |
| motion_v3_full_precision_tb | `rtl/experimental/top_full_precision_finish_hold.v` | Historical full-precision stage |
| motion_v3_hold_tb | `rtl/experimental/top_full_precision_finish_hold.v` | Historical completion-qualification stage |
| motion_v5_16bit_top_regression_tb | `verification/v6_clean/top.v` | Current 16-bit top-level directed regression (3 vectors) |

**Measured local result (November 5, 2026): 7/7 simulation processes pass.** One is an intentional negative-control reproduction, not a proof that the old RTL is correct. V5 current top-level passes 3/3 documented directed vectors. This is **not** gate-level signoff and does not imply post-layout setup/hold or ICV DRC closure. Real V5 Synopsys VCS and PrimeTime evidence remain in the earlier commit.

Do not substitute the original 8-bit `rtl/top.v` for the V5 corrected 16-bit design. Do not synthesize the testbench memory models. Preserve the 520 MHz (1.923 ns), 0.5 ns input/output delay, and 0.2 ns clock uncertainty constraints.
