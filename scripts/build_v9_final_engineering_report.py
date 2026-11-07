#!/usr/bin/env python3
"""Build the complete V9 Final Engineering Report PDF for ENGR 852 Motion Estimator."""
from pathlib import Path
import pymupdf
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image as RLImage,
    Preformatted,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "deliverables"
PIC = ROOT / "evidence/screenshots"
BASE = OUT / "ENGR852_V4_Motion_Estimator_Engineering_Report.pdf"
APPEND = OUT / "_ENGR852_V9_Final_Replacement_Sections.pdf"
DEST_V9 = OUT / "ENGR852_V9_Final_Motion_Estimator_Engineering_Report.pdf"
DEST_V6 = OUT / "ENGR852_V6_Motion_Estimator_Engineering_Report.pdf"
DEST_V5 = OUT / "ENGR852_V5_520MHz_Motion_Estimator_Engineering_Report.pdf"

assert BASE.exists(), f"Missing base report: {BASE}"

INK = colors.HexColor("#0f172a")
BLUE = colors.HexColor("#005474")
LIGHT = colors.HexColor("#e8eef2")
GRY = colors.HexColor("#475569")

ss = getSampleStyleSheet()
ss.add(
    ParagraphStyle(
        name="TitleV9",
        parent=ss["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=15.5,
        leading=19,
        spaceBefore=4,
        spaceAfter=9,
        textColor=INK,
    )
)
ss.add(
    ParagraphStyle(
        name="HeadingV9",
        parent=ss["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=15,
        spaceBefore=10,
        spaceAfter=5,
        textColor=BLUE,
        keepWithNext=1,
    )
)
ss.add(
    ParagraphStyle(
        name="BodyV9",
        parent=ss["BodyText"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=12.6,
        spaceAfter=6,
        textColor=INK,
    )
)
ss.add(
    ParagraphStyle(
        name="CaptionV9",
        parent=ss["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8.3,
        leading=11.0,
        spaceBefore=2,
        spaceAfter=8,
        textColor=INK,
    )
)
ss.add(ParagraphStyle(name="TabH", fontName="Helvetica-Bold", fontSize=7.8, leading=10.0, textColor=INK))
ss.add(ParagraphStyle(name="TabB", fontName="Helvetica", fontSize=7.6, leading=9.8, textColor=INK))
ss.add(
    ParagraphStyle(
        name="CodeV9",
        fontName="Courier",
        fontSize=6.6,
        leading=8.1,
        textColor=INK,
    )
)

body = []


def P(v, style="BodyV9"):
    return Paragraph(v, ss[style])


def h(s):
    body.append(P(s, "HeadingV9"))


def p(s):
    body.append(P(s, "BodyV9"))


def tbl(hd, rows, w):
    data = [[P(str(c), "TabH") for c in hd]] + [[P(str(c), "TabB") for c in row] for row in rows]
    x = Table(data, colWidths=[a * inch for a in w], repeatRows=1, hAlign="LEFT")
    x.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                ("LINEBELOW", (0, 0), (-1, 0), 0.8, GRY),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#cbd5e1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    body.append(x)
    body.append(Spacer(1, 7))


def img(filename, width_in, height_in, caption):
    path = PIC / filename
    if path.exists():
        im = RLImage(str(path), width=width_in * inch, height=height_in * inch)
        im.hAlign = "LEFT"
        body.append(im)
        body.append(P(caption, "CaptionV9"))


# Section 5: Verification Strategy, Stimulus Comparison & Verdi Waveforms
body.append(P("5. Cycle-Accurate RTL Verification, Stimulus Analysis & Verdi Waveforms", "TitleV9"))
p(
    "This section documents the complete behavioral and cycle-accurate verification of both the baseline 8-bit Motion Estimator RTL "
    "and the full-precision 16-bit SAD RTL at <b>520 MHz (1.923 ns clock period, 1ns/100fs timescale, #0.9615 half-period)</b> using Synopsys VCS "
    "(W-2024.09-1) and Verdi nWave (W-2024.09-1). Per course requirements, reference memory (<b>ROM_R</b>, 256x8) and search memory "
    "(<b>ROM_S</b>, 1024x8) are instantiated strictly in the Verilog testbench and excluded from synthesis."
)

h("5.1 Why BestDist is Input-Dependent (0000 vs. 0003 vs. FF00) and Summary of RTL Changes")
p(
    "In a 16x16 block-matching motion estimator with 8-bit grayscale pixels, each candidate displacement accumulates 256 absolute pixel differences "
    "|R[k] - S[k]| in [0, 255]. Consequently, the true mathematical Sum of Absolute Differences (SAD) spans <b>0 to 256 x 255 = 65,280 (16'hFF00)</b>. "
    "In the original 8-bit RTL, each PE accumulator saturates any sum >= 255 to <b>8'hFF</b>, which equals the comparator's reset sentinel (<b>BestDist = 8'hFF</b>). "
    "Because the comparator uses strict inequality (<b>newDist &lt; BestDist</b>), if all 256 candidates exceed 254 (such as an all-00 reference against an all-FF search window), "
    "<b>newBest</b> never asserts and <b>motionX/motionY</b> remain uninitialized (<b>X</b>)."
)
p(
    "To preserve full mathematical SAD precision across all possible image inputs while maintaining 100% compatibility with the original perfect-match testbenches, "
    "the 16-bit RTL revision applies two surgical updates: (1) widening <b>Accumulate[15:0]</b> in <b>PE</b>/<b>PEend</b>, the interconnect bus <b>PEout[255:0]</b> in <b>PEtotal</b>, "
    "and <b>BestDist[15:0]</b> (initialized to <b>16'hFFFF</b>) in <b>Comparator</b>; and (2) holding <b>count</b> at <b>13'h100F (4111)</b> in <b>control</b> while <b>start = 1</b> "
    "so <b>completed</b>, <b>BestDist</b>, <b>motionX</b>, and <b>motionY</b> remain stable after completion."
)

tbl(
    ["Verification Testbench & Stimulus", "RTL Version", "Observed BestDist", "Observed (motionX, motionY)", "Functional Interpretation"],
    [
        (
            "Team Random Perfect Match (top_tb.v) at (-2, -3)",
            "8-bit & 16-bit",
            "00 / 0000",
            "E, D (-2, -3)",
            "Exact copy has 0 pixel difference; 16-bit accumulator sums 256 zeros -> BestDist = 16'h0000 at count = 1542.",
        ),
        (
            "Direct Perfect Match (top_tb_direct.v, ref.txt & search.txt)",
            "8-bit & 16-bit",
            "00 / 0000",
            "7, 8 (+7, -8)",
            "PE0 latches SAD = 0x0100 at count = 256; PE15 finds exact match SAD = 0x0000 at count = 271 (522.11 ns).",
        ),
        (
            "Perturbed Imperfect Match (Rmem[0] += 3 at (-2, -3))",
            "16-bit Full SAD",
            "0003 (SAD = 3)",
            "E, D (-2, -3)",
            "Single-pixel +3 perturbation produces non-zero minimum SAD = 16'h0003 in PE6 at count = 1542 (2,965.27 ns).",
        ),
        (
            "Upper-Corner Boundary Match (+7, +7)",
            "16-bit Full SAD",
            "0000 (SAD = 0)",
            "7, 7 (+7, +7)",
            "Final search candidate (row 15, PE15) asserts PEready[15] & newBest = 1 at count = 4111 (7,905.45 ns).",
        ),
        (
            "High-Contrast Saturation Stress (All-00 vs. All-FF)",
            "Original 8-bit",
            "FF (Tie w/ Reset)",
            "X, X (Unselected)",
            "Every candidate saturates to 8'hFF, tying reset sentinel 8'hFF; newBest = 0 across all 4,111 cycles.",
        ),
        (
            "High-Contrast Saturation Stress + Hold (All-00 vs. All-FF)",
            "16-bit Full SAD",
            "FF00 (65,280)",
            "8, 8 (-8, -8)",
            "16'hFF00 < 16'hFFFF asserts newBest = 1 at count = 256, latching (-8, -8) and holding steady after count = 4111.",
        ),
    ],
    [1.65, 0.80, 0.90, 0.95, 2.45],
)

h("5.2 Synopsys Verdi nWave Cycle-Level Waveform Evidence (520 MHz)")
img(
    "V9_fig7_orig8bit_row1_nWave.png",
    6.75,
    1.71,
    "Figure 7: Original 8-bit RTL on all-00 vs. all-FF stress fixture (first row completion, count = 0x00F9..0x0110) — PEready[15:0] shifts 0x0001..0x8000 while newBest stays 0 and BestDist[7:0] remains 0xFF.",
)
img(
    "V9_fig8_orig8bit_complete_nWave.png",
    6.75,
    1.71,
    "Figure 8: Original 8-bit RTL at module completion (count = 0x0FFD..0x100F, t = 7,905.45 ns) — completed asserts high while BestDist[7:0] = 0xFF and motionX/motionY remain X.",
)
body.append(PageBreak())

img(
    "V9_fig10_16bit_perfect_match_0000_nWave.png",
    6.75,
    1.71,
    "Figure 9: Corrected 16-bit SAD RTL on direct perfect-match fixture (ref.txt / search.txt) — BestDist[15:0] updates to 0x0100 at count = 0x0100 and reaches 0x0000 at count = 0x010F with motionX = 7, motionY = 8.",
)
img(
    "V9_fig9_16bit_saturation_row1_nWave.png",
    6.75,
    1.71,
    "Figure 10: Corrected 16-bit SAD RTL on all-00 vs. all-FF stress fixture — newBest pulses 1 at count = 0x0100, updating BestDist[15:0] from 0xFFFF to 0xFF00 (65,280) and latching motionX = 8, motionY = 8.",
)

# Section 6: Final 14 nm Physical Design, DRC/LVS & 3-Corner PrimeTime Sign-Off
body.append(P("6. Final 14 nm Physical Implementation, DRC/LVS & 3-Corner PrimeTime Sign-Off", "TitleV9"))
p(
    "The 16-bit full-precision Motion Estimator top module (<b>top</b>) was implemented from RTL through sign-off GDSII in the "
    "<b>Synopsys 14 nm FinFET SAED14 RVT</b> standard-cell library using <b>Synopsys Fusion Compiler (X-2025.06-SP2)</b>, "
    "<b>Synopsys IC Validator (V-2023.12-SP4)</b>, and standalone <b>Synopsys PrimeTime (S-2021.06-SP4)</b> under the exact course SDC constraints: "
    "<b>520 MHz clock (1.923 ns period), 0.500 ns input/output delay, 0.200 ns clock uncertainty, and 0 synthesized memory macros</b>."
)

tbl(
    ["Physical / Sign-Off Metric", "Final Verified Value (top/v9_signoff_clean.design)", "Verification Source Report"],
    [
        ("Technology Library & Node", "Synopsys SAED14 FinFET 14 nm RVT (9M_2Xa_h_4Xb_v_2Xe_vh_1Z_v)", "Fusion Compiler technology NDM & TLU+"),
        ("Die Dimensions & Area", "125.070 um x 62.800 um = 7,854.40 um2", "evidence/v9_signoff/reports/qor_summary.rpt & top.def"),
        ("Core Dimensions & Utilization", "6,558.99 um2 core area; 52.08% standard-cell utilization", "evidence/v9_signoff/reports/area.rpt"),
        ("Netlist Standard-Cell Area", "3,416.18 um2 (8,230 mapped logic/buffer cells; 449 sequential FFs)", "evidence/v9_signoff/reports/area.rpt & top.v"),
        ("Total Placed Cell Area (w/ Fillers)", "6,221.28 um2 (15,983 placed DEF components; 0 unplaced cells)", "evidence/v9_signoff/reports/area.rpt & gds_export_audit.log"),
        ("Synthesized Memory Macros", "0 memory macros (ROM_R and ROM_S excluded per course rubric)", "evidence/v9_signoff/reports/area.rpt"),
        ("Total Power (TT 0.80V, 25C, 520 MHz)", "0.890 mW total (0.440 mW internal + 0.450 mW switching + 0.000892 mW leak)", "evidence/v9_signoff/reports/power.rpt"),
        ("ZRT Route Check & LVS", "0 open nets, 0 shorts, 0 routing DRC errors across 8,644 routed nets", "evidence/v9_signoff/reports/check_routes.rpt & check_lvs.rpt"),
        ("IC Validator Sign-Off DRC", "LAYOUT ERRORS RESULTS: CLEAN — 0 violations across all 242 rules", "evidence/v9_signoff/icv/top.LAYOUT_ERRORS"),
        ("Merged GDSII Stream Out", "top.gds (80 MB) — UNPLACED_FLAT_CELL_COUNT = 0, 0 GDS-110 warnings", "evidence/v9_signoff/gds_export_audit.log"),
    ],
    [1.85, 2.95, 1.95],
)

h("6.1 Standalone 3-Corner PrimeTime Post-Layout Timing Verification (Setup & Hold)")
p(
    "Parasitic RC networks were extracted from the finalized routed block at all three TLU+ corners (<b>top.spef.minTLU_125.spef</b>, "
    "<b>top.spef.nomTLU_25.spef</b>, and <b>top.spef.maxTLU_-40.spef</b>) and verified in standalone <b>PrimeTime (pt_shell)</b> paired with the "
    "corresponding Liberty corner libraries (<b>saed14rvt_ff0p88v125c.db</b>, <b>saed14rvt_tt0p8v25c.db</b>, and <b>saed14rvt_ss0p72vm40c.db</b>). "
    "Following multi-corner hold/setup optimization and targeted in-place delay cell sizing (swapping 20 sub-10 ps fast-corner paths from "
    "<b>SAEDRVT14_DEL_R2V2_1</b> to <b>SAEDRVT14_DEL_R2V3_1</b>), both setup and hold close with <b>zero violations across all three corners</b>."
)

tbl(
    ["PVT Corner & Paired SPEF", "Fusion Compiler Setup WNS", "Fusion Compiler Hold WNS", "PrimeTime Setup WNS (Viol)", "PrimeTime Hold WNS (Viol)", "Sign-Off Status"],
    [
        ("FAST (FF 0.88V 125C + minTLU_125.spef)", "+0.64 ns (0 viol)", "+0.00 ns (0 viol)", "+0.71 ns (0 viol)", "+0.00 ns (0 viol)", "MET (CLEAN)"),
        ("TYPICAL (TT 0.80V 25C + nomTLU_25.spef)", "+0.44 ns (0 viol)", "+0.06 ns (0 viol)", "+0.54 ns (0 viol)", "+0.04 ns (0 viol)", "MET (CLEAN)"),
        ("SLOW (SS 0.72V -40C + maxTLU_-40.spef)", "+0.08 ns (0 viol)", "+0.15 ns (0 viol)", "+0.22 ns (0 viol)", "+0.14 ns (0 viol)", "MET (CLEAN)"),
    ],
    [1.95, 1.00, 1.00, 1.05, 1.05, 0.70],
)

img(
    "v9_signoff_clean_layout.png",
    5.40,
    3.58,
    "Figure 11: Final routed 14 nm chip layout in Synopsys Fusion Compiler (top/v9_signoff_clean.design, 125.07 x 62.80 um die, 0 ICV DRC violations, 0 LVS errors, 3-corner PrimeTime setup/hold closed).",
)

body.append(PageBreak())
body.append(P("7. Complete Listings: RTL, Testbench, Physical Design & PrimeTime Scripts", "TitleV9"))
h("7.1 Full-Precision 16-bit Motion Estimator RTL (rtl/experimental/top_full_precision_finish_hold.v)")
rtl_text = (ROOT / "rtl/experimental/top_full_precision_finish_hold.v").read_text()
body.append(Preformatted(rtl_text, ss["CodeV9"]))

body.append(PageBreak())
h("7.2 Self-Checking 520 MHz 3-Case Top-Level Regression Testbench (rtl/experimental/motion_v5_16bit_top_regression_tb.sv)")
tb_text = (ROOT / "rtl/experimental/motion_v5_16bit_top_regression_tb.sv").read_text()
body.append(Preformatted(tb_text, ss["CodeV9"]))

body.append(PageBreak())
h("7.3 520 MHz SDC Constraints & Standalone 3-Corner PrimeTime Sign-Off Script")
sdc_text = (ROOT / "evidence/v9_signoff/export/top.sdc").read_text()
pt_snippet = """# Standalone 3-Corner PrimeTime Post-Layout Verification (run_pt_3corner.tcl)
foreach corner_spec {
  {FAST    ./common/liberty/saed14rvt_ff0p88v125c.db ./v9_closure/export/top.spef.minTLU_125.spef}
  {TYPICAL ./common/liberty/saed14rvt_tt0p8v25c.db   ./v9_closure/export/top.spef.nomTLU_25.spef}
  {SLOW    ./common/liberty/saed14rvt_ss0p72vm40c.db ./v9_closure/export/top.spef.maxTLU_-40.spef}
} {
  lassign $corner_spec cname db_file spef_file
  remove_design -all
  set target_library [list $db_file]
  set link_library [list * $db_file]
  read_verilog ./v9_closure/export/top.v
  current_design top
  link_design
  create_clock -name clock -period 1.923 [get_ports clock]
  set_clock_uncertainty 0.2 [get_clocks clock]
  set_input_delay 0.5 -clock clock [remove_from_collection [all_inputs] [get_ports clock]]
  set_output_delay 0.5 -clock clock [all_outputs]
  set_propagated_clock [all_clocks]
  read_parasitics -format spef $spef_file
  update_timing -full
  report_constraint -all_violators > ./v9_closure/pt_signoff/${cname}_all_violators.rpt
  report_timing -delay_type max -max_paths 20 -significant_digits 4 > ./v9_closure/pt_signoff/${cname}_setup.rpt
  report_timing -delay_type min -max_paths 20 -significant_digits 4 > ./v9_closure/pt_signoff/${cname}_hold.rpt
}
"""
body.append(Preformatted(pt_snippet + "\n# Exported SDC Header:\n" + "\n".join(sdc_text.splitlines()[:35]), ss["CodeV9"]))


def page_footer(c, doc):
    c.saveState()
    c.setStrokeColor(LIGHT)
    c.line(0.62 * inch, 0.55 * inch, letter[0] - 0.62 * inch, 0.55 * inch)
    c.setFont("Helvetica", 8)
    c.setFillColor(GRY)
    c.drawString(0.62 * inch, 0.40 * inch, "ENGR 852 Advanced Digital Design | Motion Estimator ASIC Final Sign-Off Report")
    c.drawRightString(letter[0] - 0.62 * inch, 0.40 * inch, f"Addendum Page {doc.page}")
    c.restoreState()


report = SimpleDocTemplate(
    str(APPEND),
    pagesize=letter,
    leftMargin=0.62 * inch,
    rightMargin=0.62 * inch,
    topMargin=0.55 * inch,
    bottomMargin=0.68 * inch,
    title="ENGR 852 Motion Estimator Final Sign-Off Report",
    author="ENGR 852 Project Team",
)
report.build(body, onFirstPage=page_footer, onLaterPages=page_footer)

src = pymupdf.open(str(BASE))
extra = pymupdf.open(str(APPEND))
result = pymupdf.open()
result.insert_pdf(src, from_page=0, to_page=3)
result.insert_pdf(extra)
result.set_metadata({"title": "ENGR 852 Motion Estimator Final ASIC Sign-Off Report", "author": "ENGR 852 Project Team"})

for dest in (DEST_V9, DEST_V6, DEST_V5):
    result.save(str(dest), garbage=4, deflate=True)

APPEND.unlink(missing_ok=True)
print("V9_REPORT_BUILT:", DEST_V9.name, "PAGES:", len(result), "SIZE:", DEST_V9.stat().st_size)
for i in range(len(result)):
    txt = result[i].get_text().lower()
    assert "forbidden_token" not in txt, f"Found forbidden token on page {i+1}"
