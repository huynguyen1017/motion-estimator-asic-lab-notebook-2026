# UPDATE-013 — Final 2026-11-04 RTL evidence and presentation delivery

**Scope:** SFSU ENGR 852 motion-estimator design, original professor-provided RTL, user's individual independent verification contributions.

## Source integrity and authorship

The original course ZIP (8,307 bytes) was transferred from the iMac, and its server SHA-256 matched the local source: `b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6`. Its `top.v` checksum is `fe71b2be40444c8ff23971d68b6cf736298ebddd5f24390ff7b08f87107a10c6`. The original was preserved; independent testbenches ran from separate server workspaces.

The project's top-level module, PEs, control and comparator are **course/team RTL**, not independently recreated modules. The new scoreboards and waveform captures are additional personal verification work.

## Verified university results

| Evidence | Observed result | Where to inspect |
| --- | --- | --- |
| Original professor baseline VCS | 50 MHz smoke test returned expected (-2,-3), SAD=0 | `~/ENGR852_Project/01_vcs_professor_baseline_20261104/` |
| Independent 520 MHz VCS | Approx. 1.923 ns simulated clock; expected (-2,-3), SAD=0; `make test` exit 0 | `~/ENGR852_Project/02_vcs_520mhz_independent_20261104/` |
| New directed PE/PEend/Comparator checker | **12 checks passed, 0 failures**, university VCS exit 0 | [testbench](../verification/motion_pe_comparator_selfcheck_tb.sv), [log excerpt](../evidence/logs/motion_vcs_precision_12check_terminal_excerpt.log) |
| New deterministic full-precision-SAD scoreboard | 3 fixed seeds × 16 blocks × 256 pixels × 2 PE variants = **24,576 PE checks**, **0 mismatches**; 10,656 samples with full SAD >255 | [source](../verification/motion_pe_fullprecision_scoreboard_tb.sv), [actual logs](../evidence/logs/motion_vcs_sad_scoreboard_three_seed_run_20261104.log) |
| Real waveform viewer | Verdi W-2024.09-1 / nWave opened VCS-generated FSDB; screenshot contains real waveform signals | [privacy-safe nWave image](../evidence/screenshots/Motion_nWave_520MHz_Precision_ACTUAL_traces.png), [application-only image](../evidence/screenshots/Motion_Verdi_application_only_REDACTED.png) |

The three scoreboard seeds were 271828, 12345 and 8675309. Each provided 4,096 samples and 8,192 PE comparisons, zero failures; saturation-count observations were 3,557, 3,549, and 3,550. Both `PE` and `PEend` match the original RTL's 8-bit **saturating** accumulator policy against an independently computed full-precision SAD. This does **not** prove the top-level output is always the globally minimum *full-precision* SAD motion vector.

The 12-check directed test captured these behaviors: full difference 1+255 = 256 becomes `8'hFF`; equal scores retain the earlier evaluated candidate coordinates (strict `<`); a score of 255 cannot replace comparator `BestDist=255` after reinitialization. These are observations at the submodule level, not asserted assignment violations.

## 14 nm implementation attempt: blocked by university licenses

The instructor's `saed14nm_1p9m.tf` and `saed14rvt_frame_timing.ndm` were confirmed present, along with `saed14rvt_tt0p8v25c.db`. Fusion Compiler X-2025.06-SP2 successfully started in batch mode, but the first 14 nm initial-map invocation ended with **`Fusion-Compiler-NX` license unavailable**. The alternate Design Compiler O-2018.06-SP4 invocation returned `Fatal: Design Compiler is not enabled. (DCSH-1)`.

Thus **NO** technology-mapped 14 nm area, power, placement, routing, extracted parasitics, DRC, PrimeTime setup/hold sign-off or routed layout screenshot was produced. The existing generic 3,254-cell Yosys result must not be relabeled as a 14 nm implementation.

## Presentation deliverables — 19 slides

The full presentation retains the 16 original team/contribution slides and adds three evidence-backed individual slides. The **original team Google Slides file was not edited**.

- [Editable 19-slide Google Slides presentation](https://docs.google.com/presentation/d/1oQlE86P-1ajHd4VskT9jGiLGEXkxlMnqQ0_dutpmTPo/edit)
- [19-slide PPTX](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pptx)
- [19-slide PDF](../deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pdf)
- [Drive deliverables folder](https://drive.google.com/drive/folders/1V_4if1sIFlrh5X28RGs4FNnPANZfEcjJ)

Slide 17: University VCS 12-check directed verification, actual Verdi nWave waveform, saturation/tie observations.

Slide 18: Independent 16-bit-reference versus 8-bit-saturating-PE scoreboard, three fixed seeds and actual check counts.

Slide 19: 14 nm constraint/libraries and transparent sign-off readiness, including both real license failures.

The screenshots were captured from the **X11 application window only**, not from the desktop. Window tab account-path metadata was masked while waveform traces were left unchanged. Previously unsafe temporary full-desktop captures were deleted from the iMac.

## Steps required to finish the graded RTL-to-GDS project

University support must enable the authorized Fusion Compiler (or another instructor-approved synthesis/physical) license. Then the class tutorial scripts can be adapted to a private work directory, with `create_clock -period 1.923`, 0.5 ns I/O delays and 0.2 ns uncertainty. Run **technology mapping → floorplan → placement → clock-tree synthesis → routing → parasitic extraction → setup/hold PrimeTime reports → DRC**; preserve actual output paths, tool logs, timestamps, screenshots and report figures. Until those measured reports exist, physical implementation is **pending**, not completed.

## Privacy and provenance

This document deliberately excludes the private 9-digit student account identifier and authentication data. Waveform PNGs are application-only with path metadata removed. The user’s original and teammate-authored slides remain attributed in the presentation; the independent verification sections are clearly labeled.
