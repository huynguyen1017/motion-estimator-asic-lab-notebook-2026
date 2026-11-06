# UPDATE-020 — November 5, 2026 — Revision-aware RTL QA and isolated signoff diagnostics

## Source-preserving corrections

- Reviewed the published V5 checkpoints and class motion-estimator requirements.
- Created name-neutral, revision-aware test copies in `verification/v6_clean/` without changing instructor RTL, algorithm, datapath architecture, or the V5 physical netlist.
- Added `run_regression.py`, which checks tool availability, selects the RTL revision corresponding to each existing test, detects the actual top module name, logs compilation and simulation separately, and returns nonzero on failure.
- Corrected local-only simulator compatibility by guarding VCS-specific `$fsdbDumpfile/$fsdbDumpvars` statements with `IVL_SIM`. Native VCS/Verdi behavior is unchanged.
- Corrected a staging filename/module mismatch in the test runner by discovering the module from Verilog rather than assuming it equals the filename.
- The original 8-bit all-saturated test is intentionally a **negative control** and must be run with the professor baseline, not the corrected 16-bit RTL.

## Verified results

- Local Icarus Verilog simulation: **7/7 revision-aware tests passed**.
- Current corrected V5 16-bit top-level: **3/3 directed vectors passed** (also documented by native VCS evidence in previous checkpoints).
- Functional RTL is not to be reworked for post-route DRC/timing failures; such revisions require renewed simulation, synthesis, routing, and STA and must remain deliberate.

## Unresolved post-layout acceptance gates

- Existing V5 ICV signoff: **18 violations**, six each under `M2.S.2`, `M2.S.3`, `M5.W.1`. Zero router violation count is not equal to zero ICV violations.
- Existing V5 `write_gds`: `GDS-110` warnings for unplaced cells require diagnosis before final layout may be called clean.
- Existing three-corner PrimeTime: FAST holds 402 violations (WNS -0.14 ns), TYPICAL holds 120 (-0.12 ns), SLOW holds 33 (-0.09 ns); SLOW setup has 17 violating paths (WNS -0.06 ns).
- PrimeTime SLOW in-memory setup ECO trial reduced 17 to 2 violating paths / WNS -0.02 ns but was **not physically implemented**. FAST hold in-memory ECO generated 731 buffer insertions and congested physical routing; must not be blindly reapplied.
- A controlled ICV run on the **pre-signoff-fill** `route_opt_v5` block found 435 rule violations, so removing all fill/finishing stages does not constitute a fix.
- Newly copied Fusion Compiler design blocks must be saved to the library before external ICV checks; otherwise ICV returns `Design view ... not found` / fatal #420. Corrected the copy/open/save/check sequencing in isolated diagnostics.

## Acceptance rule

Mark a stage VERIFIED only when its own tool log and final artifact agree. Before asserting full signoff, require a routed/final layout with **zero applicable ICV DRC violations, zero GDS unplaced-cell warnings, extracted SPEF from that exact corrected layout, and PrimeTime setup and hold with nonnegative WNS and zero violating paths at FAST, TYPICAL, and SLOW corners**. Existing measured area and power remain V5 estimates until revised after a physical ECO. No grade can be guaranteed.

## Integrity

No supplied instructor source, teammate slide, or older published evidence was overwritten during this audit. Only a new isolated verification folder, its checks, and this checkpoint note were added. No full-desktop screenshots were captured. The professor's original design remains the comparison baseline.
