# UPDATE-011 — University VCS baseline, 520 MHz, and independent self-check

**Date:** November 4, 2026. These results were observed directly from the existing authenticated SFSU SSH Terminal via the connected iMac. Individual commands were run in unique per-test directories, preserving the extracted professor baseline.

## Input provenance

The professor-supplied ZIP was verified byte-for-byte after SCP (SHA-256 `b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6`). Its `top.v` SHA-256 is `fe71b2be40444c8ff23971d68b6cf736298ebddd5f24390ff7b08f87107a10c6`. A new independent VCS workspace was created for each run. The RTL was not modified.

## Run A — Unmodified professor original at 50 MHz

**Directory:** `~/ENGR852_Project/01_vcs_professor_baseline_20261104`  
**Command:** `make test`, from the original Makefile.  
**Clock:** `always #10 clock = ~clock` at `1ns/10ps` timescale (20 ns period = 50 MHz).  
**Observed simulation result:** `BestDist=0`, `motionX=-2`, `motionY=-3`; the testbench reported that the DUT coordinates match expected coordinates. The VCS simulation finished at approximately 82,280 ns.  
**Output artifacts:** `simv`, `vcs.log`, `simv.log`, `novas.fsdb`; a separately captured `baseline_console.log` is also stored on the server.

**Interpretation:** A baseline smoke test of the unchanged source completed. The supplied testbench prints `All tests completed` even after motion mismatches, so this message alone is not a strict verification assertion.

## Run B — Personal testbench copy at nominal 520 MHz

**Directory:** `~/ENGR852_Project/02_vcs_520mhz_independent_20261104`  
**Command:** `make test` using the original `top.v` and a modified **testbench copy**.  
**Only changes:** `1ns/10ps` -> `1ns/100fs`; `#10` clock toggle -> `#0.9615`; three `@(posedge clock);#10;` post-edge delays -> `#0.02`. The changes were count-checked before editing. `cmp` confirmed unchanged RTL (`ORIGINAL_RTL_CMP_EXIT=0`).  
**Run result:** `VCS_520MHZ_MAKE_EXIT=0`; `BestDist=0`; `motionX=-2`, `motionY=-3`; DUT motion outputs matched the testbench's expectations. Simulation finished at approximately **7,910.2805 ns**.  
**Output artifacts:** `simv`, `vcs.log`, `simv.log`, `novas.fsdb`, `vcs_520mhz_console.log`.

**Interpretation:** Real university VCS verification at a **1.923 ns simulation clock period**. This is not evidence that the routed 14 nm implementation meets setup or hold timing.

## Run C — New independent self-checking VCS testbench

**Directory:** `~/ENGR852_Project/03_vcs_precision_selfcheck_20261104`  
**Source:** [`verification/motion_pe_comparator_selfcheck_tb.sv`](../verification/motion_pe_comparator_selfcheck_tb.sv) (independent 520 MHz testbench), with the unchanged professor's `top.v`.  
**Testbench SHA-256:** `76c9781bc69845fb4fb1b3f5d6ad73993238532152444d3e567eeaf947cf5608`.  
**Result:** `PRECISION_COMPILE_EXIT=0`, `PRECISION_SIM_EXIT=0`, **`MOTION_INDEPENDENT_TEST_PASS checks=12 failures=0`**.

The test covered PE and PEend reset-by-`newDist`, saturation, saturation persistence, S1/S2 selection, unsigned absolute difference when R < S1, comparator initial minimum-distortion selection, equal-SAD tie retention, strictly smaller distortion update, BestDist reinitialization and an all-255 candidate after reinitialization.

**Measured behavior:** A full-precision sum of `1+255=256` appears as saturated `8'hFF` in both PE and PEend. With `BestDist` initialized to `8'hFF`, a candidate whose saturated SAD equals 255 never causes `newDist < BestDist`; motion coordinates can remain unchanged. This is a **measured submodule-level architectural limitation**, not yet a demonstrated incorrect motion vector in the full design. The initial local testbench iteration had an incorrect expectation for the uninitialized PE; a controlled `newDist` transition was added before retesting. The corrected run passed in both local Icarus and university Synopsys VCS.

**Evidence excerpt:** [`evidence/logs/motion_vcs_precision_12check_terminal_excerpt.log`](../evidence/logs/motion_vcs_precision_12check_terminal_excerpt.log). Full university VCS logs are retained in the per-test server directory.

## Physical-design readiness (not sign-off)

On the university server, `which vcs`, `which verdi`, and `which pt_shell` resolved to licensed-tool installation paths. `which fc_shell` did not resolve from the current interactive PATH. The professor's Fusion Compiler tutorial has `common/liberty`, `common/ndm`, `common/tlup`, `common/nxtgrd`, `common/tf`, `common/gds`, and scripts referring to `saed14nm` technology collateral, but no Fusion Compiler executable, license checkout, mapped synthesis, placement, route, DRC, or PrimeTime analysis has yet been verified.

## Next evidence targets

1. Verify X11 remote display and launch Verdi against the existing `novas.fsdb` waveform; capture original screenshots.
2. Expand from submodule-directed tests to full motion-estimator reference-model checks with strict simulation PASS/FAIL, corners, seeds and saturating-SAD coverage.
3. Find and verify the instructor-prescribed Fusion Compiler executable and technology setup before running synthesis or routing.
4. Create **three new slides distinct from the existing team slides**, based only on actual passing logs/reports and correctly labeled limitations.
