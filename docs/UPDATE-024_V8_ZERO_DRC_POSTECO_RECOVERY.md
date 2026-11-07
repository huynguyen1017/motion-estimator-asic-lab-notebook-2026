# ENGR 852 — V8 recovery checkpoint: zero-DRC layout and post-ECO timing

## Provenance
Recovered and verified following an interrupted Fusion Compiler session. This is a **measured, partial ASIC sign-off checkpoint**, not a claim of final timing closure. University-server artifacts are retained in their original working directory.

Server project (under the university account): `~/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix`.
Reference tool setup: Fusion Compiler X-2025.06-SP2a, ICV W-2024.09-3, PrimeTime S-2021.06-SP4.

## Physical implementation — validated

- Source layout checkpoint: `top.dlib:top/v8_remove_filler07`.
- Geometry-repair script: `scripts/v8_move_delay08.tcl`.
- New repaired block: **`top.dlib:top/v8_move_delay08`**.
- One `SAEDRVT14_DEL_R2V2_1` instance was moved by `{+0.444, 0.0}` micrometres, followed by localized `route_detail`.
- `MOVE08_MOVE_RC=0`, `MOVE08_LEGALITY=0`, `MOVE08_ROUTE_RC=0`, `MOVE08_CHECK_ROUTES_RC=0`, `MOVE08_ICV_RC=0`.
- **Independent ICV DRC: 0 violations at 100% of 242 rules**, reported in `v8_trial/move_delay08.log`, with ICV output in `v8_trial/icv_move_delay08/`.
- This replaces the prior best partial 4-violation checkpoint **for DRC purposes only**. Do not overwrite or delete the earlier checkpoints.

## Post-ECO extraction — completed

Extraction script: `scripts/v8_posteco_export09.tcl`.
Copied analysis/export block: `top.dlib:top/v8_posteco_export09`.
Run evidence: `v8_trial/posteco_export09.log` and `v8_trial/posteco_export09.exit` (exit 0).

Extracted artifacts under `v8_trial/posteco09/`:
- `top.v`: new post-ECO gate-level netlist
- `top.sdc`: original Fusion Compiler SDC (version 2.2)
- `top_pt21.sdc`: compatibility copy changing only the SDC version declaration to 2.1 (retained as diagnostic, not used in final corner runs)
- `top.spef.minTLU_125.spef` (FAST)
- `top.spef.nomTLU_25.spef` (TYPICAL)
- `top.spef.maxTLU_-40.spef` (SLOW)

All netlist/SDC/SPEF export commands returned success; extraction did not reuse V5 SPEF.

## Corrected PrimeTime runs — completed but timing NOT closed

Run scripts: `scripts/v8_pt11_FAST.tcl`, `scripts/v8_pt11_TYPICAL.tcl`, `scripts/v8_pt11_SLOW.tcl`.
Reports/logs: `v8_trial/pt11/` (`*_setup.rpt`, `*_hold.rpt`, `*_global.rpt`, `*_check_timing.rpt`, `*_violators.rpt`, `*.log`, `exit_codes.txt`).
Each PT exit code was 0 with no leading `Error:` diagnostics observed in the final PT11 logs.

**Use each existing PT-compatible per-corner SDC** (`results/top_primetime_FAST.sdc`, `...TYPICAL.sdc`, `...SLOW.sdc`) with the **new V8 netlist/SPEF** and corresponding SAED14 Liberty library. Do not use the failed PT09/PT10 logs as sign-off evidence: PT09 rejected SDC 2.2; PT10's single exported SDC referenced SLOW library cells during FAST/TYPICAL runs.

| Corner | Setup worst negative slack | Hold WNS | Hold TNS |
|---|---:|---:|---:|
| FAST | No setup violations in PT global report | -0.14 ns | -12.96 ns |
| TYPICAL | No setup violations in PT global report | -0.12 ns | -4.76 ns |
| SLOW | -0.06 ns (TNS -0.29 ns) | -0.09 ns | -1.24 ns |

FAST: 402 hold-violating register-to-register paths in `FAST_global.rpt`. The SLOW maximum-delay critical path starts at `S1[1]` and ends at `pe_u/pe7/Accumulate_reg[15]`. The PT `check_timing` reports warn that 25 input ports with parasitics lack driving cells, which should be reviewed as part of constraint adequacy.

## Remaining sign-off requirements

1. Preserve the **zero-ICV-violation V8 block** as an accepted DRC checkpoint. Re-run connectivity and physical verification after any new ECO.
2. Fix SLOW setup (WNS -0.06 ns). Test changes in separately named blocks rather than modifying `v8_move_delay08`.
3. Address FAST/TYPICAL/SLOW hold with **small, placement-aware, incremental ECO batches** and re-evaluate setup. The previous V5 large ECO inserted approximately 731 buffers and created excessive routing violations; it must not be directly replayed on V8.
4. Export fresh post-ECO netlist, SDC and three SPEF files after *each accepted ECO*, then execute all three PT corners with compatible SDC and check `report_global_timing`, `check_timing`, setup, hold and parasitic annotation.
5. Require **zero ICV DRC, legal placement, connected routing and nonnegative setup/hold slack at all corners** before declaring physical sign-off. Do not label unfinished work as completed on presentation slides.
6. Only after validation, update the V8 presentation into a new release using measured technical results; preserve teammates' original slides and do not add desktop-wide screenshots.

## Published presentation state

The corrected wording (exact-match SAD `0x0000` versus maximum-contrast SAD `0xFF00`) is already published in commit `a625b8d`: `deliverables/ENGR852_V8_Clean_3_Contribution_Slides.pptx` and `deliverables/ENGR852_V8_Complete_19_Slides.pptx`.

**Status:** ICV DRC ✅, post-ECO extraction ✅, post-ECO three-corner PrimeTime execution ✅, SLOW setup ❌, FAST/TYPICAL/SLOW hold ❌, therefore final physical sign-off **NOT YET**.
