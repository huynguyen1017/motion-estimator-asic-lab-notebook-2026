# UPDATE-016 — V3 university Synopsys results and three-slide delivery

**Lab date:** November 4, 2026 (PST). **Project:** ENGR 852 520 MHz 14 nm motion estimator.  
**Scope:** User's independently executed verification and ASIC work; original teaching RTL, testbench fixtures, and teammate slides remain preserved.

## Correct course-specific Fusion Compiler setup

The full instructor-provided `/packages/synopsys/setup/Fusion_Compiler_setup` example was copied into a new server workspace. In `tcsh`, sourcing **the copied workspace's** `scripts/synopsys_setup.tcl` discovered Fusion Compiler X-2025.06-SP2a with valid tool access. This is distinct from sourcing the general older VCS-only setup script. The previous `Fusion-Compiler-NX` startup error from a direct bare launch does not apply to the corrected official workflow.

The official example completed `make run_initial_syn` and `make run_compile_flow` with exit code 0. The motion-estimator workspaces use the same instructor scripts, but replace the demonstration I²C top with the actual `top` motion estimator and its own SDC. The student's unmodified professor RTL ZIP was preserved and SHA-256 validated. The reference/search arrays remain testbench-only, not synthesized.

## Independent VCS corner case and correction

The directed fixture places all 256 reference pixels at `00` and all 1,024 search pixels at `FF`. Thus each of the 256 required pixel differences is 255 and the true complete SAD for every matching window is **65,280 = 16'hFF00**.

**Original 8-bit RTL — actual university VCS observation:**

```text
V3_ALL_SATURATED BestDist=ff motionX=x motionY=x completed=1 newbest=0
OBSERVED_NO_VALID_MOTION_VECTOR: all saturated SADs tie reset sentinel FF
PASS: Reproduced no-selection case in unmodified textbook RTL
```

Because the original comparator initializes BestDist to 8'hFF and only updates on strictly smaller newDist, saturated 8'hFF candidates never produce a valid winner.

**Separate experimental 16-bit RTL — actual university VCS observation:**

```text
V3_ALL_SATURATED BestDist=ff00 motionX=8 motionY=8 completed=1 newbest=1
PASS: Corrected full-precision variant selected (-8,-8) with nonzero 16-bit SAD
```

In a tie, the controller's first candidate is (-8,-8), encoded as X=4'h8, Y=4'h8. The V3B separate variant additionally holds stable outputs after completion; the directed V3B check observed the corrected result unchanged for 13 additional clocks. This test establishes this corner-case correction, not proof of complete functionality for every possible image.

**Native waveform evidence:** VCS W-2024.09-1 produced FSDB; Verdi W-2024.09-1 nWave displayed the original and V3B corrected signals. Screenshots were captured from specific X11 *application windows*, not the full iMac desktop; the titles were excluded/redacted to avoid account identifiers. No signal drawings were synthesized.

## Real SAED14 Fusion Compiler mapped measurements

| Reported metric | Original professor 8-bit RTL | Independent corrected 16-bit V3B |
| --- | ---: | ---: |
| Mapped standard-cell area | 881.96 µm² | 1,193.03 µm² |
| Mapped cell instances | 1,693 | 1,905 |
| Sequential cell instances | 280 | 416 |
| Macros / black boxes | 0 | 0 |
| Compile-stage setup slack | First run invalid input-delay SDC; not comparable | +0.06 ns (MET) |

The corrected 16-bit design costs **311.07 µm²** additional cell area (**35.27%** relative increase) and 212 additional cells. These figures are from the Synopsys technology-mapped report and may change after floorplan/CTS/routing. Do not label them final GDS area or physical sign-off.

Required SDC constraints: clock 1.923 ns (approximately 520 MHz), 0.5 ns input delay, 0.5 ns output delay, 0.2 ns clock uncertainty. The earlier motion design's input-delay constraint contained an unsupported collection expression; it was replaced by explicit user input ports and reloaded. The updated Fusion timing path showed 0.5 ns input delay and 0.2 ns uncertainty.

## Physical implementation checkpoint

Both architectures completed the initial synth/compile/floorplan work; the 16-bit V3B also completed `make run_placement` without reported placement errors. **Clock-tree synthesis was attempted** but a finalized successful V3B clock-tree report was not recovered before connection interruption.

The original 8-bit architecture's clock-tree phase failed with `PLACE-004` over-utilization: **111.73%** calculated utilization, **1,456 µm²** required versus **1,303 µm²** available. It needs core-area expansion / utilization adjustment followed by a fresh CTS run. Successful placement in a previous stage is not a sign-off result.

**Not yet verified:** final V3B clock-tree completion; route; DRC; extracted parasitics; final routed layout area and power; PrimeTime post-layout setup **and hold**. The course specifically requires these and they must be run from a valid routed/extracted design. No screenshots or numerical sign-off claims have been invented for missing stages.

## V3 slide package — original course/teammate content unchanged

Exactly three contribution slides, in editable PPTX and three-page PDF:

1. **SAD Saturation — Original RTL**: Verdi screenshot and test stimulus, observed `FF`/unknown-vector failure.
2. **16-bit SAD — Verification After RTL Change**: native Verdi V3B nWave figure, `FF00` / (-8,-8) corrected result and tie interpretation.
3. **520 MHz ASIC Implementation**: SAED14 mapped area/cell comparison, explicit 1.923 ns / 0.5 ns / 0.2 ns constraints and truthful physical-flow checkpoint.

Files:
- [V3 slides (PPTX)](../deliverables/ENGR852_Huy_V3_Independent_3_Slides.pptx)
- [V3 slides (PDF)](../deliverables/ENGR852_Huy_V3_Independent_3_Slides.pdf)
- [Original failure — Verdi screenshot](../evidence/screenshots/V3_Verdi_original_saturated_window_only.png)
- [16-bit correction — Verdi screenshot](../evidence/screenshots/V3B_Verdi_nWave_2240wide_redacted.png)
- [Independent source variant](../rtl/experimental/top_full_precision_v3.v)
- [V3B completion-hold source](../rtl/experimental/top_full_precision_finish_hold.v)
- [Saturation testbench](../verification/huy_v3_all_saturated_tb.sv)
- [16-bit testbench](../verification/huy_v3_full_precision_tb.sv)
- [V3B completion-hold testbench](../verification/huy_v3_hold_tb.sv)

## Reproducing with approved tools

On the university **Linux SSH server**, from an authenticated shell:

```sh
cd ~/ENGR852_Project/16_v3b_final_asic_fc
tcsh
source scripts/synopsys_setup.tcl
make run_cts
# Only after successful CTS: make run_route
# Only after successful route: make run_signoff
# Finally, after extraction: make run_pt
```

Every flow step must be checked for `Error:` and valid output artifacts; a Makefile/shell exit code alone does not establish implementation success. Run stages in the course's prescribed order and retain original logs. User must explicitly re-authenticate if a previously opened SSH session has timed out.

**Privacy/attribution:** Do not put university passwords, university ID, SSH home paths, VPN status, personal desktop screenshots, commercial PDK files or proprietary Synopsys tutorial PDFs into public GitHub. Keep official tool/library material on university infrastructure.


## Complete 19-slide presentation copy and verification

The [full editable 19-slide V3 PowerPoint](../deliverables/ENGR852_V3_Full_Team_19_Slides.pptx) and its [19-page PDF](../deliverables/ENGR852_V3_Full_Team_19_Slides.pdf) contain the original 16 previously assembled team slides unchanged, followed by the three independent V3 engineering slides (17–19). The slide-building and slide-merge scripts retain first-16 content and shape counts. Both PDFs were re-exported and page-count verified.

The original failure screenshot was further **cropped to remove the entire Verdi title bar** because it contained a university-account home path. The public GitHub figure and embedded PPTX/PDF now show only the nWave application waveform panel, not the sensitive title bar.


## Resumable physical implementation (SSH-disconnect safe)

The optional [stage resume script](../scripts/resume_v3_physical_flow.sh) runs the **instructor's unchanged stage Tcl** in the corrected local C-shell environment, writes one timestamped log per stage, scans tool error messages and stops immediately if a stage fails. It can be started with nohup on the authenticated Linux server to survive an SSH disconnection. This script has been syntax-checked but **not executed end-to-end** and does not establish final physical signoff by itself. It never stores login credentials.
