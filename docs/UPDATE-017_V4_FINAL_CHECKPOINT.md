# UPDATE-017 — V4 detailed waveform captures, slides, and 90–100 rubric audit

**Date:** 2026-11-04 PST  
**Project:** ENGR 852 Motion Estimator — 520 MHz, SAED14 RVT  
**Status:** Native simulation, technology mapping, floorplan and placement evidence exist; final post-layout sign-off is not yet available.

## Native waveform capture improvement

The teammate reference showed controller progress and module completion at two zoom ranges. The current independent RTL contribution is different: a directed SAD-saturation failure and the full-precision correction. The captured nWave traces expose `clock`, `start`, `completed`, `count[12:0]`, `PEready[15:0]`, `newBest`, `BestDist`, `motionX`, and `motionY`.

V4 uses actual Verdi nWave application captures at 2240-pixel display resolution. The original controller-progress pane was cropped to its **real nWave display window**, preserving signal list, waveform ruler and values; the correction uses the earlier genuine V3B nWave FSDB view. The original full-resolution V3 files are preserved and not replaced in the archive. No waveform data was drawn or recreated. The cropped screenshots omit account identifiers and desktop windows.

## Exact measured results: original vs corrected

| Criterion | Unmodified professor RTL | Separate corrected RTL (V3B) |
| --- | --- | --- |
| Corner-case stimulus | 256 reference pixels 00, search pixels FF | Same |
| Mathematical SAD | 256 × 255 = 65,280 = FF00 | Same |
| Observed BestDist | FF (saturated 8 bits) | FF00 (full 16 bits) |
| Observed motionX, motionY | X, X (not selected) | 8, 8 = signed -8,-8 |
| Verdi / VCS evidence | Reproduced no-selection bug | Directed 16-bit test passes; stable output after completion |
| Mapped SAED14 area | 881.96 μm² | 1,193.03 μm² |
| Mapped cell count | 1,693 | 1,905 |
| Sequential cells | 280 | 416 |
| Memory macro cells | 0 | 0 |

**Additional cell area:** 311.07 μm² (+35.27%). **Corrected compile setup slack:** +0.06 ns at the mapped-design stage. This is *not* PrimeTime post-route slack.

## Clock / I/O constraints

- Clock frequency 520 MHz; period constrained to 1.923 ns.
- Input delay 0.5 ns, output delay 0.5 ns.
- Clock uncertainty 0.2 ns.
- Search and reference memory arrays remain in simulation testbench, not the synthesizable top.
- 16×16 pixel SAD needs 16-bit unsigned accumulation because the maximum is 65,280.

## Required course deliverables: evidence audit

| Requirement | Confirmed evidence | Remaining gap |
| --- | --- | --- |
| Debugged Verilog RTL and interface | Professor source archive, V3 widened and V3B hold variant, source hashes | Full randomized end-to-end checker for every case, final integration decision |
| Verilog stimulus and simulation | VCS logs, V3B directed tests, three-seed independent PE scoreboard | Expanded top-level functional coverage across seeds |
| Waveforms | Actual Verdi nWave FSDB screenshots (V1–V4) | Additional controller internal signal view optional |
| Synthesis files | Native Fusion mapped design + cell, timing and initial power reports | Final post-route optimized netlist |
| 520 MHz constraints | SDC period 1.923ns, I/O 0.5ns and uncertainty 0.2ns | Ensure final PrimeTime modes/corners use exactly the intended SDC |
| Physical area and layout | Synopsys floorplan DEF and V3B placement logs | Routed layout and final core/cell utilization after CTS |
| DRC | Not yet produced | Run actual DRC on routed design and archive full result |
| Parasitics | Tech TLUP files used by flow | Actual routed parasitic extraction / SPEF |
| Setup / hold | +0.06ns compile setup slack only | **Post-layout PrimeTime setup and hold**, complete path reports |
| Power | Initial flow generated preliminary power report | Final power report with stated corner, activity assumptions and units |
| Written report and presentation | V4 editable 3-slide and 19-slide decks; engineering record and source evidence | Final signoff section must be populated with genuine reports |

**The 90–100 range requires all major implementation steps, so the current artifacts must not be labeled fully signed off.** Completion depends on the actual remaining routed-and-extracted tool runs.

## CTS blocker and command recovery

Earlier original 8-bit CTS failed with `PLACE-004`: utilization 111.73%, required area 1,456 µm², available 1,303 µm². A larger core or lower target utilization and re-run through CTS is needed. This affects one flow checkpoint, not proof that the separate V3B 16-bit placement failed.

V3B initial synthesis, mapping, floorplan and placement returned exit 0 and had no placement errors in the inspected output. The V3B `make run_cts` terminal became unresponsive during an SSH disruption; a successful final CTS report was **not** verified. It is incorrect to proceed to route under an assumption that this run passed.

After a fresh authenticated terminal session, inspect:
```sh
cd ~/ENGR852_Project/16_v3b_final_asic_fc
grep -E '^Error:|PLACE-004|PLACE-006|clock_opt failed' v3b_cts.out | tail -20
tail -n 40 v3b_cts.out
ls -lh logs/clock_opt.log results/*clock* 2>/dev/null
```
Only if clean, continue the instructor flow: `make run_route`, `make run_signoff`, and `make run_pt`. Use an appropriate lower core utilization and regenerate checkpoints when CTS is overfilled. Back up each stage log first; do not overwrite existing evidence.

A [resume and log audit script](../scripts/resume_v3_physical_flow.sh) is available, but was *not* executed through signoff. It must be reviewed against the local course scripts before use.

## V4 presentation files

- [Your three contribution slides (PPTX)](../deliverables/ENGR852_Motion_Estimator_V4_Detailed_Waveform_3_Slides.pptx)
- [Your three contribution slides (PDF)](../deliverables/ENGR852_Motion_Estimator_V4_Detailed_Waveform_3_Slides.pdf)
- [Complete 19 slides (PPTX)](../deliverables/ENGR852_V4_Full_Team_19_Slides.pptx)
- [Complete 19 slides (PDF)](../deliverables/ENGR852_V4_Full_Team_19_Slides.pdf)
- [Original controller-progress nWave figure](../evidence/screenshots/V4_original_controller_progress_nWave_1472px.png)
- [Corrected 16-bit nWave figure](../evidence/screenshots/V4_corrected_SAD_fullprecision_nWave_2240px.png)

QA: exactly 3 and 19 slides; corresponding 3-page and 19-page PDFs; original slides 1–16 unchanged in text, object geometry and shape counts. The V4 slides have **no occurrences of the word the user requested removed** and no miniature annotation boxes. All screenshots use actual application-window data without personal desktop capture.

## Evidence integrity

Screenshots are crops of original Synopsys application windows, not synthesized diagrams. The professor's RTL and teammates' slides were not overwritten. Proprietary tool/library content and credentials were not published.


## V4 electronic report and ready-to-submit source package

A six-page [engineering report](../deliverables/ENGR852_V4_Motion_Estimator_Engineering_Report.pdf) was generated from measured output and user-provided project instructions. It includes architecture, testbench-only memory boundary, VCS evidence, exact SAD-corner math, two cropped Verdi nWave application figures, native technology mapping numbers and the detailed 90–100 rubric gap analysis.

The [ZIP evidence bundle](../deliverables/ENGR852_V4_Submission_and_Evidence_Bundle.zip) contains 28 items: report, PPTX/PDF decks, RTL source variants, simulation testbenches, constraints, captured logs, annotated evidence provenance, scripts, README and cryptographic SHA-256 file manifest. The archive was opened and its member checksums verified. No passwords or student-ID strings were found in its included text files. Proprietary technology libraries are excluded.

The user-facing slides and the report do not contain the word the user requested removed.
