from pathlib import Path
import pymupdf
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'deliverables'
BASE=OUT/'ENGR852_V4_Motion_Estimator_Engineering_Report.pdf'
APPEND=OUT/'_ENGR852_V5_Postroute_Replacement_Sections.pdf'
DEST=OUT/'ENGR852_V5_520MHz_Motion_Estimator_Engineering_Report.pdf'
assert BASE.exists()
PW=letter[0] - 1.24*inch
INK=colors.HexColor('#141a23')
BLUE=colors.HexColor('#155e75')
LIGHT=colors.HexColor('#eff3f6')
GRY=colors.HexColor('#475569')
ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='TitleV5',parent=ss['Heading1'],fontName='Helvetica-Bold',fontSize=17,leading=21,spaceBefore=5,spaceAfter=12,textColor=INK))
ss.add(ParagraphStyle(name='HeadingV5',parent=ss['Heading2'],fontName='Helvetica-Bold',fontSize=12,leading=16,spaceBefore=13,spaceAfter=7,textColor=INK,keepWithNext=1))
ss.add(ParagraphStyle(name='BodyV5',parent=ss['BodyText'],fontName='Helvetica',fontSize=9.3,leading=13.1,spaceAfter=8,textColor=INK))
ss.add(ParagraphStyle(name='TabH',fontName='Helvetica-Bold',fontSize=7.7,leading=10))
ss.add(ParagraphStyle(name='TabB',fontName='Helvetica',fontSize=7.6,leading=10))
ss.add(ParagraphStyle(name='FootV5',fontName='Helvetica',fontSize=8,leading=11,textColor=GRY))
body=[]
def P(v,style='BodyV5'):return Paragraph(v,ss[style])
def h(s):body.append(P(s,'HeadingV5'))
def p(s):body.append(P(s))
def tbl(hd,rows,w):
 data=[[P(str(c),'TabH') for c in hd]]+[[P(str(c),'TabB') for c in row] for row in rows]
 x=Table(data,colWidths=[a*inch for a in w],repeatRows=1,hAlign='LEFT')
 x.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('LINEBELOW',(0,0),(-1,0),.8,GRY),
 ('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#e3e8ed')),
 ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f9fafb')]),
 ('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),5),
 ('BOTTOMPADDING',(0,0),(-1,-1),5),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6)]))
 body.append(x);body.append(Spacer(1,9))
def bullet(t):p('&#8226; '+t)

body.append(P('5. V5 Physical Implementation Results','TitleV5'))
p('This section replaces the earlier V4 physical-status page. It describes work actually performed with Fusion Compiler and IC Validator on November 5, 2026. The original instructor RTL and team slides remain unchanged. The separate V5 experiment uses the corrected <b>16-bit SAD</b> implementation.')
tbl(['Step','Observed evidence','Status'],[
 ('Technology mapping','SAED14 RVT, corrected RTL, zero memory macro cells','PASS'),
 ('Floorplan','35% target; 35.44% reported utilization','PASS'),
 ('Placement','Successful place_opt_v5 design block and native tool log','PASS'),
 ('Clock-tree synthesis','clock_opt_v5 saved; earlier 112.88% over-utilization resolved','PASS'),
 ('Detailed routing','route_opt_v5 saved; zero route shorts and total zero routing violations','PASS'),
 ('Final ICV DRC','242 rules checked; 18 violations across 3 rules','FAIL'),
 ('GDS export','GDS generated; GDS-110 unplaced-cell warnings','REVIEW'),
 ('SPEF extraction','Min, nominal and max routed SPEFs exported (about 8.8 MB each)','PASS'),
 ('PrimeTime setup/hold','Full post-route reports generated for FAST/TYPICAL/SLOW','VIOLATIONS'),
], [1.42,4.40,0.92])
h('5.1 Post-route area and dimensions')
tbl(['Quantity','Measured value','Measurement source'],[
 ('Routed cells','6,310 (5,861 combinational; 449 sequential)','Fusion route_opt area report'),
 ('Standard-cell area','2,781.30 square micrometers','Fusion route_opt area report'),
 ('Buffers and inverters','4,547 cells','Fusion route_opt area report'),
 ('Memory macros','0','Fusion mapped netlist; off-chip/testbench memories'),
 ('DEF die bounding box','92.510 x 50.800 micrometers','Exported floorplan DEF'),
 ('Die bounding area','4,699.508 square micrometers','Calculated from DEF coordinates')
],[1.50,2.65,3.12])
p('<b>Layout interpretation:</b> standard-cell area measures the mapped cell footprints and differs from the enclosing die/core geometry. In particular, the exported GDS is not an accepted final clean layout while unplaced-cell warnings remain.')
h('5.2 Power result: actual tool estimate')
p('At the typical SAED14 corner (<b>0.80 V, 25 C</b>), Fusion Compiler reported total dynamic power of <b>0.728 mW</b>, leakage power of <b>0.000775 mW</b>, and total estimated power of <b>0.729 mW</b>. Activity was estimated through the tool\'s switching-activity propagation, not measured on physical silicon.')
body.append(PageBreak())

body.append(P('6. Extracted PrimeTime Timing and DRC','TitleV5'))
p('The required <b>1.923 ns period, 0.500 ns input delay, 0.500 ns output delay, and 0.200 ns clock uncertainty</b> were preserved in all runs. Fusion Compiler exported SDC version 2.2; a copy was adjusted only for PrimeTime SDC 2.1 syntax and the matching FF, TT or SS library. The original design constraints were not relaxed.')
tbl(['Paired PVT / SPEF','Setup WNS','Setup violations','Hold WNS','Hold TNS','Hold violations'],[
 ('FAST: FF 0.88V 125C / minTLU_125','+0.52 ns','0','-0.14 ns','-12.96 ns','402'),
 ('TYPICAL: TT 0.80V 25C / nomTLU_25','+0.30 ns','0','-0.12 ns','-4.76 ns','120'),
 ('SLOW: SS 0.72V -40C / maxTLU_-40','-0.06 ns','17','-0.09 ns','-1.24 ns','33'),
], [2.17,0.85,0.96,0.85,0.81,1.02])
p('<b>Interpretation:</b> Fast and typical setup paths pass, but the slow setup group fails on 17 input-to-register paths. Hold paths fail at every corner. This is actual post-route, SPEF-annotated PrimeTime timing, not the earlier +0.06 ns compile-stage setup estimate.')
h('6.1 Final ICV design-rule violations')
tbl(['ICV check','Violations','What fails'],[
 ('M2.S.2','6','Insufficient spacing for wide/parallel M2 shapes'),
 ('M2.S.3','6','Insufficient extra spacing for another M2 width/run-length condition'),
 ('M5.W.1','6','M5 widths outside the permitted discrete set'),
 ('<b>Total</b>','<b>18</b>','<b>3 distinct rule checks; sign-off NOT passed</b>'),
],[1.28,0.97,5.02])
p('The routed design\'s zero short / floating-route violations are not equivalent to an ICV DRC pass. ICV ran 242 checks and the final results file reports 18 violations. Unplaced cells identified by GDS-110 and incomplete filler-cell coverage must also be resolved before calling the layout complete.')
h('6.2 Timing repair: native PrimeTime ECO')
p('Using the course-provided <b>fix_eco_timing -type hold</b> procedure and the SAED14 ECO buffer set, PrimeTime generated <b>731 insert_buffer commands</b>, additional cell-sizing changes, and an estimated buffer-area increase of <b>412.70 square micrometers</b>. PrimeTime reported no remaining FAST hold violations in the <i>unrouted in-memory ECO model</i>. The changes were applied in a new Fusion Compiler block, <b>signoff_v5_holdfix1</b>, and routing was started. Final improvement requires completion of that route, new SPEF, final ICV DRC, and fresh three-corner PrimeTime max/min reports.')
body.append(PageBreak())

body.append(P('7. Requirements and Sign-off Decision','TitleV5'))
p('The course grading rubric specifies all major design elements correctly verified and implemented, completed Verilog testbenches, physical design, power/area, routed layout, DRC, parasitic extraction, and post-layout PrimeTime setup and hold. The following evidence-based audit distinguishes completed deliverables from acceptance gates that still must pass.')
tbl(['Submission item','Evidence available now','Rubric status'],[
 ('Debugged RTL and Verilog testbench','Separate 16-bit SAD RTL; VCS original fixture and 3/3 regression; saturation and completion-hold corner tests','VERIFIED for documented cases'),
 ('Simulated waveforms','Genuine Synopsys Verdi FSDB captures plus local VCD and native VCS logs','AVAILABLE'),
 ('Gate-level netlist and constraints','SAED14 full routed netlist and 520 MHz SDC; correct 0.5 ns delays / 0.2 ns uncertainty','AVAILABLE'),
 ('Layout files, area, power','Exported GDS/DEF; 2,781.30 square micrometer cell area; 0.729 mW typical estimated power','NEEDS clean final GDS'),
 ('Design-rule checking','ICV report contains 18 M2/M5 violations','NOT PASSED'),
 ('Parasitic extraction','Routed SPEF at fast, typical and slow scenarios','VERIFIED, pre-ECO'),
 ('PrimeTime setup and hold','Three-corner valid report set with quantified worst paths and violations','NOT CLOSED'),
 ('Presentation and electronic report','V4 team and three personal slides; updated physical figures in this V5 report','READY for revision'),
 ('Demonstration preparation','Verilog stimulus, VCS logs, Verdi captures, physical-flow outputs','SUPPORTED')
],[1.63,4.12,1.52])
h('7.1 Required final acceptance checks')
bullet('Finish the new ECO route and legalize all inserted cells, with no broken nets, shorts or floating routes.')
bullet('Rerun final ICV DRC until the applicable rule violations are zero; resolve GDS-110 unplaced-cell and filler warnings.')
bullet('Export the new gate-level netlist, layout and <b>new</b> extracted min/nom/max SPEFs after any ECO.')
bullet('Rerun PrimeTime max (setup) and min (hold) with actual extracted RC at all three corners; achieve nonnegative worst slack at each.')
bullet('Refresh final area and estimated power using the finalized post-ECO netlist and documented switching assumptions.')
bullet('Add final native layout and timing figures to the presentation and retain the complete scripts and source in the project package.')
p('<b>Conclusion:</b> Functional correctness, complete routing and parasitic extraction are demonstrated. The current physical design is not yet a clean sign-off implementation, so no guaranteed grading percentage is claimed. The engineering record identifies the specific outstanding errors and preserves every successful and failed checkpoint.')
p('Versioned evidence: github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026/docs/UPDATE-019_V5_POST_ROUTE_EXTRACTION_PT_ECO.md')
def page(c,doc):
 c.saveState();c.setStrokeColor(LIGHT);c.line(.62*inch,.58*inch,letter[0]-.62*inch,.58*inch)
 c.setFont('Helvetica',8);c.setFillColor(GRY)
 c.drawString(.62*inch,.42*inch,'ENGR 852 | Motion Estimator | V5 routed and extracted results')
 c.drawRightString(letter[0]-.62*inch,.42*inch,f'Revision section page {doc.page}')
 c.restoreState()
report=SimpleDocTemplate(str(APPEND),pagesize=letter,leftMargin=.62*inch,rightMargin=.62*inch,topMargin=.6*inch,bottomMargin=.75*inch,
 title='ENGR852 V5 Physical implementation addendum',author='ENGR 852 Project Team')
report.build(body,onFirstPage=page,onLaterPages=page)
src=pymupdf.open(BASE);extra=pymupdf.open(APPEND)
result=pymupdf.open()
result.insert_pdf(src,from_page=0,to_page=3)
result.insert_pdf(extra)
result.set_metadata({'title':'ENGR 852 Motion Estimator: V5 Routing, Extraction and PrimeTime Report','author':'ENGR 852 Project Team'})
result.save(DEST,garbage=4,deflate=True)
print('V5_REPORT_FINAL',DEST.name,'PAGES',len(result),'SIZE',DEST.stat().st_size,'ADDENDUM',len(extra))
for i in range(len(result)):
 s=result[i].get_text()
 print('PAGE',i+1,'CHARS',len(s),'TOP',s[:45].replace('\n','|'))
assert len(result)>=7
assert all('chatgpt' not in result[i].get_text().lower() for i in range(len(result)))
for j in (4,5,len(result)-1):
 result[j].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(OUT/f'_QA_V5_report_p{j+1}.png')
