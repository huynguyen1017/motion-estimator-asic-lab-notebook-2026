from pathlib import Path

root = Path(__file__).resolve().parent.parent
status = root / "docs/CURRENT_STATUS.md"
s = status.read_text()
changes = [
 ("5. **14 nm physical-flow blocker:**", "5. **14 nm mapped ASIC evidence recovered in V3:**"),
]
lines = s.splitlines()
for i, line in enumerate(lines):
    if line.startswith("5. **14 nm physical-flow blocker:**"):
        lines[i] = "5. **14 nm mapped ASIC evidence recovered in V3:** The official course-local Fusion setup successfully launched Fusion Compiler X-2025.06-SP2a. The original 8-bit RTL mapped to 1,693 cells / 881.96 square micrometers; the corrected 16-bit V3B mapped to 1,905 cells / 1,193.03 square micrometers. Both floorplans and V3B placement completed. The original 8-bit CTS stage failed at 111.73% over-utilization; V3B CTS final success, routing, DRC, parasitics and PrimeTime sign-off are not verified. See [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md)."
    if line.startswith("7. **Remaining required actions:**"):
        lines[i] = "7. **Remaining required actions:** Recover the V3B CTS job, adjust floorplan utilization if necessary, then complete routing, DRC, extraction, final PPA, and PrimeTime post-layout setup/hold with valid output artifacts. Do not mistake an initial mapped report for routed sign-off."
    if line.startswith("- **Physical ASIC status remains blocked:**"):
        lines[i] = "- **V3 supersedes this historical V2 license blocker:** The official local Fusion setup enabled actual SAED14 mapping, floorplan, and V3B placement. Original area 881.96 um2; V3B area 1,193.03 um2. Routing, extraction, DRC and final PrimeTime setup/hold remain unverified. See [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md)."
s = "\n".join(lines) + "\n"
if "**LATEST CHECKPOINT:**" not in s:
    s = s.replace("## Objective", "**LATEST CHECKPOINT:** Native VCS/Verdi V3 RTL evidence and native Fusion Compiler SAED14 mapped results are verified in [UPDATE-016](UPDATE-016_V3_PPA_AND_SLIDES.md). Earlier V2 license statements are historical and superseded.\n\n## Objective",1)
status.write_text(s)

readme = root / "README.md"
r = readme.read_text()
section = """
## V3: Native Verdi verification and SAED14 mapped ASIC results (November 4, 2026)

The [V3 engineering record](docs/UPDATE-016_V3_PPA_AND_SLIDES.md) supersedes the earlier V2 Fusion Compiler license blocker. The instructor's copied project-specific Fusion setup enabled Synopsys Fusion Compiler X-2025.06-SP2a with the SAED14 RVT library.

University Synopsys VCS reproduced a no-selection corner case in the original 8-bit saturating SAD. A **separate**, independent 16-bit RTL variant measured full distance FF00 and deterministic first candidate (-8,-8) for the all-high-contrast fixture; testbench FSDB was displayed in Verdi nWave, not a drawn waveform.

Mapped cell area (Fusion Compiler): **881.96 um2** (original 8-bit), **1,193.03 um2** (corrected V3B). Corrected design compile-stage setup slack: **+0.06 ns**. Native mapped synthesis, floorplan, and V3B placement completed. Clock-tree final completion, routing, DRC, parasitic extraction, and PrimeTime **post-layout setup/hold** are not yet verified.

**Deliverables:** [three-slide PPTX](deliverables/ENGR852_Huy_V3_Independent_3_Slides.pptx), [three-page PDF](deliverables/ENGR852_Huy_V3_Independent_3_Slides.pdf), and [native Verdi V3B capture](evidence/screenshots/V3B_Verdi_nWave_2240wide_redacted.png). Teaching source and teammate slides were not overwritten.

"""
if "## V3: Native Verdi verification" not in r:
    assert "## Key Technical Results Completed" in r
    r = r.replace("## Key Technical Results Completed", section + "## Key Technical Results Completed",1)
readme.write_text(r)
print("UPDATED_CURRENT_STATUS_AND_README")
