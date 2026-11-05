# UPDATE-015 — V3 native Synopsys RTL and ASIC evidence

**Date:** 2026-11-04 PST. **Source:** ENGR852 professor-provided motion estimator, separately preserved original RTL and independent 16-bit engineering variant.

## Course toolchain recovered
The official university Fusion Compiler tutorial requires copying its complete workspace and sourcing the **project-local** `scripts/synopsys_setup.tcl` with `tcsh`, which loads Fusion Compiler X-2025.06-SP2a and the SAED14 timing and physical technology libraries. The previous bare `fc_shell` license failure came from a different launch environment. Synopsys VCS W-2024.09-1 and Verdi W-2024.09-1 are the RTL verification and waveform tools. VS Code with the Verilog-HDL extension is installed locally.

## Native VCS reproducible discovery
- The untouched professor RTL uses an 8-bit saturating SAD and comparator reset value FF.
- Directed all-high-contrast fixture: 256 reference pixels = 00; search pixels = FF. Every candidate has true SAD 256×255 = **65,280 (FF00)**.
- Original RTL, native VCS: `BestDist=ff`; `motionX=x`; `motionY=x`; `completed=1`; `newbest=0`. **No valid match was selected.**
- Independent widened-accumulator variant: 16-bit PE accumulators, 16-bit comparator, 256-bit aggregate PE bus, explicit vector initialization.
- V3B also qualifies comparator PEready with a delayed completion bit so the final candidate can be evaluated, then prevents further updates after completion.
- V3B native VCS: `BestDist=ff00`, `motionX=8`, `motionY=8` (signed vector −8,−8), `completed=1`, `newbest=1`. **Self-check PASS**, stable for 13 additional clocks.
- V3B source SHA-256 `26470f5fb232a06d0bf998cc35e8bdc0600a81bc69b49d60563534fa8d5a05eb`. Memories are testbench-only; source variant is experimental and does not overwrite teammate files.

## SAED14 Fusion Compiler mapping results (real tool reports)
| Metric | Professor 8-bit RTL | V3B 16-bit corrected RTL |
| --- | ---: | ---: |
| Total mapped cell area (µm²) | 881.96 | 1,193.03 |
| Reported mapped cell count | 1,693 | 1,905 |
| Technology | SAED14 RVT | SAED14 RVT |
| Constraint | 1.923 ns period, 0.5 ns IO, 0.2 ns uncertainty | Same |

Reported area changes are synthesis-stage measurements; **not final placed/routed layout area**. The original design's first CTS attempt reported overutilization of 111.73% (required 1,456 µm² versus available 1,303 µm²), requiring a larger floorplan before complete physical sign-off. Physical timing, routing DRC, parasitics and PrimeTime results must not be represented as passed unless produced by subsequent stage logs.

## Waveform evidence and capture method
Native university Synopsys VCS created FSDB; Verdi nWave displayed the actual FSDB on the XQuartz iMac display. The 2240-pixel nWave screenshot was captured from its **specific X11 application window** and cropped to the waveform panel to exclude university account paths. No desktop, unrelated applications, or invented waveform graphics are included. The original full-app screen remains private on the iMac.

## Deliverables and required follow-up
- `rtl/experimental/top_full_precision_finish_hold.v` — corrected, separately named RTL.
- `verification/huy_v3_hold_tb.sv` — deterministic VCS stimulus and assertions.
- `scripts/build_finish_hold_variant.py` — derivation of the hold variant from the earlier widened design.
- `evidence/screenshots/V3B_Verdi_nWave_2240wide_redacted.png` — native Verdi window-only waveform.
- Continue floorplan utilization correction, placement, clock-tree, routing, DRC/parasitic extraction and PrimeTime setup/hold for final full grading requirements.

Avoid claiming these incomplete physical metrics have been measured.