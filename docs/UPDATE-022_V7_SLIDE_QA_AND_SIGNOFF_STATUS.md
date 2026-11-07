# UPDATE-022 — V7 slide QA, native waveform provenance and physical sign-off status

**Date:** November 6, 2026. **Flow:** 520 MHz, SAED14 motion estimator.

## Team BestDist question: correct resolution

A 16-bit SAD accumulator does **not** change the ideal result of the team's original perfect-match test: `BestDist=16'h0000`. The original directed perturbation fixture should yield `16'h0003`. The separate high-contrast negative-control fixture uses an all-zero 16x16 reference block and an all-FF search window; its actual mathematical SAD is `256*255=65280=16'hFF00`. In that fixture the original 8-bit saturating RTL cannot choose a candidate against its FF reset value; a separate full-precision version can select FF00 with vector (8,8), interpreted as signed (-8,-8).

These cases are distinct and are explicitly labeled in the V7 figures. Do not present the FF00 stress-test waveform as the expected result of the team's normal testbench.

## V7 presentation QA

Rebuilt three individually authored contribution slides in the team's clean white style using the **original native Synopsys Verdi nWave screenshots** without redrawing any signal values. The slides show: (1) original eight-bit controller/PEready and saturation behavior, (2) a separate sixteen-bit SAD correction with the expected-result distinctions, and (3) actual routed-cell area, power and three-corner PrimeTime numbers at the V5 stage.

- `deliverables/ENGR852_V7_Clean_Waveform_3_Slides.pptx` — editable three-slide contribution.
- `deliverables/ENGR852_V7_Complete_19_Slides.pptx` — the same three contribution slides appended to the existing 16 team slides.
- `deliverables/ENGR852_V7_3_Slide_Preview.pdf` — three-page raster preview generated directly from macOS Quick Look renderings; editable PPTX remains the primary file.

**Visual inspection:** Each slide was rendered through Quick Look at 1400 pixels and inspected. No text overflow, collapsed tables, unnecessary author/filename footers, or off-slide shapes were observed. The original team slides 1–16 were compared against their XML before saving and remain unchanged. No generated waveform graphics replace actual Verdi captures.

**Signal detail limitation:** The existing genuine independent Verdi captures show clock, start, completed, count, PEready, newBest, BestDist and motionX/Y, but **do not display AddressR/AddressS1/AddressS2**. The teammate's reference waveform contains address buses and is not reused as independent evidence. Those address buses require a new native Verdi trace configuration and window-only screenshot before being added as personal evidence.

## Repeated physical-signoff investigation

The connected physical database exists and its fresh native GDS re-export previously passed the unplaced-cell check; the new file contains no GDS-110 warnings. Revisited the final V6 isolated DRC candidate and inspected its native ICV rule summary. It still has **12 metal-two spacing violations**: six `M2.S.2` and six `M2.S.3`. The earlier V5 signoff checkpoint recorded 18 ICV violations, and the V6 exploratory candidates did not achieve zero. No rerouted candidate has been promoted to sign-off.

**Post-route V5 timing reference**: FAST setup WNS +0.52 ns, hold WNS -0.14 ns (402 paths); TYPICAL setup +0.30 ns, hold -0.12 ns (120); SLOW setup -0.06 ns (17), hold -0.09 ns (33). A separate in-memory SLOW setup trial reduced violations to 2 but was never physically applied. The severe 731-insertion hold trial congested routing, so replaying it without incremental legality and ICV checks is unsafe.

**Still open:** zero-violation ICV DRC; legal hold correction across all corners; SLOW setup closure; post-ECO route, GDS, parasitics and PrimeTime max/min at the same final checkpoint. The verified mapped/run results are useful but do not meet all 90–100 course requirements until the actual sign-off tools pass.

## Integrity notes

Professor source code and legacy team presentation elements were not overwritten. New source files use neutral filenames and describe only tested behavior. No screen-wide desktop screenshot, personal shell information or credentials are added. The full design cannot responsibly be marked complete solely by changing document status labels.
