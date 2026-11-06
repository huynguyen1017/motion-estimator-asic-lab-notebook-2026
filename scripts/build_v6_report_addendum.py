#!/usr/bin/env python3
"""Append verified V6 findings without rewriting prior measured V5 evidence."""
from pathlib import Path
from io import BytesIO
import pymupdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

root = Path(__file__).resolve().parents[1]
out = root / "deliverables"
src = out / "ENGR852_V5_520MHz_Motion_Estimator_Engineering_Report.pdf"
dest = out / "ENGR852_V6_Motion_Estimator_Engineering_Report.pdf"
if not src.is_file(): raise SystemExit("Missing source report; refusing to invent prior measurements")

navy = colors.HexColor("#152536")
slate = colors.HexColor("#566574")
pale = colors.HexColor("#f0f3f7")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ReportH",fontName="Helvetica-Bold",fontSize=17,leading=21,spaceAfter=10,textColor=navy))
styles.add(ParagraphStyle(name="ReportSub",fontName="Helvetica-Bold",fontSize=11,leading=14,spaceBefore=12,spaceAfter=7,textColor=navy))
styles.add(ParagraphStyle(name="ReportText",fontName="Helvetica",fontSize=9.4,leading=13.7,spaceAfter=7,textColor=navy))
styles.add(ParagraphStyle(name="ReportTable",fontName="Helvetica",fontSize=8.4,leading=11,textColor=navy))
styles.add(ParagraphStyle(name="ReportFoot",fontName="Helvetica",fontSize=8.2,leading=11,textColor=slate))
buffer = BytesIO()
story = []
def p(s,style="ReportText"):story.append(Paragraph(s,styles[style]))
def grid(header,rows,widths):
    a=[[Paragraph(str(x),styles['ReportTable']) for x in header]]
    a.extend([[Paragraph(str(x),styles['ReportTable']) for x in row] for row in rows])
    t=Table(a,colWidths=widths,repeatRows=1,hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),pale),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f8fafb")]),
        ("LINEBELOW",(0,0),(-1,-1),0.35,colors.HexColor("#d6dce3")),
        ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)
    ]))
    story.append(t);story.append(Spacer(1,9))

p("V6 Addendum — Verification and GDS Audit","ReportH")
p("ENGR 852 Motion Estimator  |  November 6, 2026  |  520 MHz","ReportFoot")
p("This dated addendum supersedes earlier ambiguous BestDist captions and updates the GDS-placement checkpoint. Existing V5 timing and physical-design measurements remain historical values until a corrected, signed-off layout is produced.")
p("A. BestDist depends on the stimulus","ReportSub")
grid(["Stimulus","Expected BestDist","Meaning"],[
 ["Team perfect match","0000","Reference equals one search candidate; a 16-bit accumulator still returns zero."],
 ["Perturbed match","0003","The minimum candidate difference is three."],
 ["All-00 reference vs all-FF search","FF00","A separate worst-case directed test: 256 x 255 = 65,280."],
],[2.03*inch,1.38*inch,3.34*inch])
p("The original eight-bit datapath saturates at FF for the extreme input. Its strict-less-than comparator has no valid new best against a reset limit of FF. The corrected sixteen-bit datapath selects FF00, with four-bit vector (8,8), signed (-8,-8), <b>only for that extreme stimulus</b>. No RTL change is needed to make the normal test return 0000; it already does so.")
p("B. Source compatibility and verified regression","ReportSub")
p("The current source preserves the original top/controller/PE/PEend/PEtotal/Comparator hierarchy, 16-element search pipeline, two-port search memory interface, candidate scanning, and signed vector encoding. The changes widen sum and comparator buses to 16 bits and qualify the completed outputs. Reference and search memories remain in the testbench.")
grid(["Verification item","Observed","Outcome"],[
 ["Source match","Clean V6 top.v equals the reviewed verified RTL, byte for byte","PASS"],
 ["Seven revision-aware simulation processes","7/7 exit successfully","PASS"],
 ["Original baseline, three independent expected-value assertions","0000 / 0003 / 0000, corresponding vector checks","PASS"],
 ["Corrected top-level, three directed checks","0000 / 0003 / 0000 with expected vectors","PASS"],
 ["Intentional 8-bit saturation negative control","Original no-selection failure reproduced","PASS as negative control"],
],[2.13*inch,3.18*inch,1.44*inch])

story.append(PageBreak())
p("V6 Addendum — Physical Sign-Off","ReportH")
p("C. GDS re-export from the existing V5 routed checkpoint","ReportSub")
p("A clean native Fusion Compiler diagnostic on top/signoff_v5 located controller count_reg[0] as placed and returned <b>zero unplaced flat cells</b>. Placement legality completed. A fresh write_gds produced an approximately 80 MB GDS file, exit code zero, with <b>zero GDS-110 warnings</b>. The previous GDS output remains archived; the fresh file is retained on the engineering server.")
p("This corrects the earlier GDS-placement uncertainty for that checkpoint. It does not prove that the layout is ICV DRC-clean, nor that future hold/setup repairs preserve routing legality.")
p("D. Outstanding acceptance gates","ReportSub")
grid(["Stage","Current evidence","Required for 90–100 rubric target"],[
 ["ICV DRC","18 V5 baseline violations; isolated repairs still nonzero","Final design with zero applicable ICV violations"],
 ["SLOW setup","-0.06 ns / 17 paths. Trial ECO -0.02 ns / 2 paths, in memory only","Physically implemented, routed and extracted setup with no failing paths"],
 ["FAST hold","-0.14 ns / 402 failing paths","Nonnegative hold slack and no failing paths"],
 ["TYPICAL hold","-0.12 ns / 120 failing paths","Nonnegative hold slack and no failing paths"],
 ["SLOW hold","-0.09 ns / 33 failing paths","Nonnegative hold slack and no failing paths"],
 ["Final extraction","V5 SPEF exists for three corners","Regenerate SPEF, gate-level netlist, power and area after final ECO"],
],[1.31*inch,2.43*inch,3.01*inch])
p("E. Reproducibility and protection rules","ReportSub")
p("Each repair must run from a preserved copy of the design block. Check executable paths, Tcl variables, library inputs, tool licensing, saved database blocks and exact SDC before execution. Inspect log return codes <i>and</i> violation/path counts. If DRC or timing becomes worse, reject the candidate and keep the last good checkpoint; do not advance based on process exit code alone.")
p("The corrected V6 contribution presentation distinguishes normal 0000 from the separate FF00 stress case. Its full 19-slide copy preserves team slides 1–16 and scales the physical-results slide to the same canvas. No new timing or DRC success is claimed in those slides.")
p("The project is not yet fully signed off. Completion requires actual zero-violation ICV and three-corner post-layout PrimeTime setup/hold after all changes, supported by matching final routed files and reports.","ReportText")
p("Verification details: docs/UPDATE-021_V6_GDS_REGRESSION_AND_SLIDE_CORRECTION.md","ReportFoot")

def footer(canvas,doc):
    canvas.saveState()
    canvas.setFont('Helvetica',8)
    canvas.setFillColor(slate)
    canvas.drawString(.61*inch,.47*inch,"ENGR 852  |  V6 Addendum")
    canvas.drawRightString(7.9*inch,.47*inch,f"Addendum page {doc.page}")
    canvas.restoreState()

SimpleDocTemplate(buffer,pagesize=letter,leftMargin=.62*inch,rightMargin=.62*inch,
                  topMargin=.56*inch,bottomMargin=.75*inch,
                  title="ENGR 852 V6 Verification and Physical Audit").build(story,onFirstPage=footer,onLaterPages=footer)
buffer.seek(0)
base=pymupdf.open(src)
extension=pymupdf.open(stream=buffer.getvalue(),filetype="pdf")
count_before=len(base)
base.insert_pdf(extension)
base.save(dest,garbage=4,deflate=True)
base.close()
test=pymupdf.open(dest)
assert len(test)>count_before
last="\n".join(pg.get_text() for pg in list(test)[count_before:])
assert "BestDist" in last and "FF00" in last and "0000" in last
assert "GDS-110" in last
print("V6_REPORT_CREATED",dest,"BASE_PAGES",count_before,
      "APPENDIX_PAGES",len(test)-count_before,"SIZE",dest.stat().st_size)
