from pathlib import Path
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, Flowable, Preformatted, HRFlowable)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PIL import Image as PILImage

ROOT=Path(__file__).resolve().parent.parent
GIT=Path.home()/'Developer/portfolio/motion-estimator-asic-lab-notebook-2026'
OUT=ROOT/'report';OUT.mkdir(exist_ok=True)
PDF=OUT/'ENGR852_V4_Motion_Estimator_Engineering_Report.pdf'
BLACK=colors.HexColor('#111820')
GRAY=colors.HexColor('#4e5862')
LIGHT=colors.HexColor('#eff1f4')
TEAL=colors.HexColor('#00769b')
W,H=letter
PAGE_W=W-1.24*inch
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='ReportTitle',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=23,leading=28,textColor=BLACK,spaceAfter=16))
styles.add(ParagraphStyle(name='ReportDeck',parent=styles['Normal'],fontName='Helvetica',fontSize=12,leading=17,textColor=GRAY,spaceAfter=12))
styles.add(ParagraphStyle(name='SectionHeaderCustom',parent=styles['Heading1'],fontName='Helvetica-Bold',fontSize=15.2,leading=19,textColor=BLACK,spaceBefore=16,spaceAfter=8,keepWithNext=1))
styles.add(ParagraphStyle(name='SubHeaderCustom',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=11.5,leading=15,textColor=BLACK,spaceBefore=12,spaceAfter=7,keepWithNext=1))
styles.add(ParagraphStyle(name='ParagraphCustom',parent=styles['BodyText'],fontName='Helvetica',fontSize=9.3,leading=12.9,spaceAfter=6.2,textColor=BLACK))
styles.add(ParagraphStyle(name='CaptionCustom',parent=styles['Normal'],fontName='Helvetica-Bold',fontSize=8.8,leading=12,spaceAfter=12,textColor=BLACK))
styles.add(ParagraphStyle(name='TableBodyCustom',fontName='Helvetica',fontSize=7.85,leading=10.15,spaceAfter=0))
styles.add(ParagraphStyle(name='TableHeaderCustom',fontName='Helvetica-Bold',fontSize=7.85,leading=10.15,spaceAfter=0))
styles.add(ParagraphStyle(name='SmallCustom',fontName='Helvetica',fontSize=8.2,leading=11,spaceAfter=6))
styles.add(ParagraphStyle(name='CodeCustom',fontName='Courier',fontSize=7.5,leading=10.5))
def P(t,style='ParagraphCustom'):return Paragraph(t,styles[style])
def H1(t):story.append(P(t,'SectionHeaderCustom'))
def H2(t):story.append(P(t,'SubHeaderCustom'))
def bullet(s):story.append(P('&#8226; '+s))
def caption(s):story.append(P(s,'CaptionCustom'))
def table(head,rows,widths=None):
 data=[[P(x,'TableHeaderCustom') for x in head]]
 for row in rows:data.append([P(str(x),'TableBodyCustom') for x in row])
 n=len(head)
 if widths is None:widths=[PAGE_W/n]*n
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([
  ('BACKGROUND',(0,0),(-1,0),LIGHT),('LINEBELOW',(0,0),(-1,0),.8,GRAY),
  ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f8f9fa')]),
  ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,1),(-1,-1),.2,colors.HexColor('#d0d4d9')),
  ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
  ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)
 ]))
 story.append(t);story.append(Spacer(1,10))
def picture(path,maxw,maxh):
 im=PILImage.open(path);w,h=im.size;scale=min(maxw/w,maxh/h)
 story.append(Image(str(path),width=w*scale,height=h*scale,hAlign='CENTER'))

class Architecture(Flowable):
 def __init__(self,width=PAGE_W,height=190):
  Flowable.__init__(self);self.width=width;self.height=height
 def draw(self):
  c=self.canv;c.setStrokeColor(GRAY);c.setLineWidth(.85)
  def box(x,y,w,h,title,desc,fill=colors.white):
   c.setFillColor(fill);c.roundRect(x,y,w,h,6,stroke=1,fill=1)
   c.setFillColor(BLACK);c.setFont('Helvetica-Bold',9);c.drawCentredString(x+w/2,y+h-16,title)
   c.setFillColor(GRAY);c.setFont('Helvetica',7.7);c.drawCentredString(x+w/2,y+13,desc)
  def arrow(x1,y1,x2,y2):
   c.setStrokeColor(GRAY);c.line(x1,y1,x2,y2)
   c.line(x2,y2,x2-5,y2+3);c.line(x2,y2,x2-5,y2-3)
  box(5,118,108,53,'Reference memory','256 x 8 (testbench)',LIGHT)
  box(5,30,108,53,'Search memory','1024 x 8 (testbench)',LIGHT)
  box(135,60,107,95,'Controller','addresses / PEready')
  box(266,60,94,95,'16 PE chain','16-bit SAD')
  box(380,60,126,95,'Comparator','BestDist / motion')
  arrow(113,146,135,146);arrow(113,56,135,82)
  arrow(242,108,266,108);arrow(360,108,380,108)
  c.setFont('Helvetica',8.2);c.setFillColor(GRAY);c.drawString(135,21,'Reference/search data and addresses cross the memory interface')
  c.setFont('Helvetica-Bold',9);c.setFillColor(BLACK);c.drawString(5,181,'External testbench memories are NOT synthesized inside top.')

story=[]
story.append(P('ENGR 852 Motion Estimator','ReportTitle'))
story.append(P('V4 design, verification, and 14 nm implementation record  |  November 4, 2026','ReportDeck'))
story.append(P('<b>Document scope:</b> actual VCS/Verdi verification, full-precision SAD correction, mapped SAED14 synthesis measurements, physical-flow checkpoint, and outstanding sign-off evidence. Measurements are labeled by their flow stage.','ParagraphCustom'))
story.append(HRFlowable(width='100%',thickness=1,color=GRAY))
H1('1. Design target and memory boundary')
story.append(P('The design compares an 8-bit grayscale <b>16 x 16</b> reference block against candidate positions in a <b>31 x 31</b> search window. A 16-PE systolic datapath performs absolute differences and accumulation while the controller generates search/reference addresses and candidate vectors. The comparator selects the minimum sum of absolute differences (SAD).'))
story.append(Architecture())
table(['Course setting','Required value'],[
 ['Clock frequency and cycle','520 MHz; 1.923 ns period'],
 ['Input and output delay','0.500 ns each'],
 ['Clock uncertainty','0.200 ns'],
 ['Reference/search memory','Outside synthesizable top; testbench models drive R, S1, S2'],
 ['SAD precision','16 bits to accommodate 256 x 255 = 65,280 (FF00)']
],[2.35*inch,4.92*inch])
story.append(P('The provided top-level RTL has memory-data inputs R/S1/S2 and address outputs AddressR/AddressS1/AddressS2; only the controller, processing elements and comparator belong in the physical chip.'))

story.append(PageBreak())
H1('2. Functional RTL validation')
story.append(P('The original source ZIP was preserved separately. Baseline directed and randomized tests were executed with Synopsys VCS W-2024.09-1; Verdi W-2024.09-1 displayed genuine FSDB waveform data. The clock toggles every 0.9615 ns, producing the target period of 1.923 ns at timescale 1ns/100fs.'))
table(['Stimulus / scenario','Observed result','Interpretation'],[
 ['Directed reference/search fixture','BestDist=00; X=7; Y=8; candidate count 271','Perfect match, signed vector (+7,-8)'],
 ['Single-pixel +3 perturbation','BestDist=03; X=E; Y=D; candidate count 1542','Nonzero SAD, signed vector (-2,-3)'],
 ['Upper-corner boundary','BestDist=00; X=7; Y=7; count 4111','Last candidate, signed vector (+7,+7)'],
 ['PE / PEend / comparator directed','12 checks, 0 failures','Saturation, mux path, strict-less-than behavior'],
 ['Randomized saturating-PE scoreboard','3 seeds, 24,576 PE comparisons, 0 mismatches','The original 8-bit *saturating* behavior matches its reference']
],[2.08*inch,2.64*inch,2.55*inch])
story.append(P('<b>Interpretation:</b> the randomized PE scoreboard establishes agreement with the defined saturating 8-bit behavior; it does <b>not</b> prove that 8-bit SAD gives the correct minimum for every image. This motivated the separate full-precision correction.'))
H2('2.1 Reproduced saturation defect')
story.append(P('For the directed all-high-contrast fixture, all 256 reference pixels are 00 and every search pixel is FF. Each candidate has a true SAD of 256 x 255 = 65,280 (hex FF00). Original PEs saturate at 8-bit FF. The original comparator initializes BestDist to FF and updates only when newDist is <b>strictly smaller</b>, so no saturated candidate can be accepted.'))
table(['Output','Original RTL / VCS observation','Corrected variant / VCS observation'],[
 ['BestDist','FF','FF00'],
 ['motionX / motionY','X / X (unknown)','8 / 8 = signed (-8,-8)'],
 ['completed','1','1'],
 ['Comparator newBest','0; no valid winner','1 on first equal-SAD candidate']
],[1.40*inch,2.90*inch,2.97*inch])
story.append(P('The 16-bit fix widens the PE accumulators, comparator datapath and best-distance register. The independent V3B hold variant also avoids output changes after completion; its directed run retained the corrected result for 13 further clock cycles. The professor source and teammate implementation were not overwritten.'))

story.append(PageBreak())
H1('3. Native waveform evidence')
picdir=ROOT/'evidence/screenshots'
picture(picdir/'V4_original_controller_progress_nWave_1472px.png',PAGE_W,2.36*inch)
caption('Figure 1. Original 8-bit VCS trace displayed in Verdi nWave. PEready pulses occur but newBest stays low; BestDist remains FF and motionX/Y are unknown.')
picture(picdir/'V4_corrected_SAD_fullprecision_nWave_2240px.png',PAGE_W,2.10*inch)
caption('Figure 2. Corrected 16-bit Verdi nWave trace. NewBest updates BestDist to FF00, and the first candidate is encoded as 8,8 (signed -8,-8).')
story.append(P('Both images were captured from the nWave application window without including unrelated desktop applications. Cropping was limited to the waveform panels; the original raw evidence is preserved in earlier V3 records.'))
story.append(P('As in the team controller slide, the signal list includes clock, start, completed, count[12:0], PEready[15:0], newBest, BestDist and motionX/Y. This contribution focuses on the comparator and SAD-precision failure rather than repeating the controller-row demonstration.'))

story.append(PageBreak())
H1('4. SAED14 Fusion Compiler synthesis results')
story.append(P('The instructor-prescribed local Fusion Compiler setup loaded X-2025.06-SP2a and SAED14 RVT libraries. The example environment and motion-estimator mapped compile completed. The numbers below were read from native Synopsys reports and are <b>mapped-cell measurements</b>, not final routed core area.'))
table(['Report metric','Original 8-bit RTL','Corrected 16-bit V3B'],[
 ['Mapped standard-cell area','881.96 um2','1,193.03 um2'],
 ['Mapped cell count','1,693','1,905'],
 ['Combinational cells','1,413','1,489'],
 ['Sequential cells','280','416'],
 ['Memory macros / black boxes','0','0'],
 ['Compile-stage setup slack','First SDC run invalid input-delay collection','+0.06 ns (MET)']
],[2.52*inch,2.15*inch,2.60*inch])
story.append(P('Corrected implementation area grows by <b>311.07 um2 (35.3%)</b> relative to the original. The 16-bit datapath preserves SAD values up to 65,280 without loss. Timing impact requires further optimization and post-route analysis.'))
H2('4.1 Timing methodology')
bullet('Clock 1.923 ns and uncertainty 0.200 ns are set in the design constraints.')
bullet('External input delay and output delay are each 0.500 ns.')
bullet('An unsupported expression in the first motion-estimator input-delay command was corrected, and the reloaded timing path confirmed 0.500 ns input delay and 0.200 ns uncertainty.')
bullet('The measured +0.06 ns path is a compile-stage max-delay setup report. It is <b>not</b> a post-layout PrimeTime setup or hold measurement.')
H2('4.2 Power assumptions')
story.append(P('The mapped flow can produce preliminary power reports, but a verified numeric final power figure and activity assumptions were not recovered in the evidence available for this report. A legitimate final power value must identify the cell library corner, clock rate, toggle/activity basis, and post-route extracted interconnect model. A nominal estimate is not inserted as a measured result.'))

story.append(PageBreak())
H1('5. Physical implementation and sign-off status')
table(['Required stage','Checkpoint','Evidence needed for final submission'],[
 ['Logic synthesis and mapping','PASS','Technology-mapped netlist, reports, tool scripts'],
 ['Floorplan','PASS','Generated floorplan DEF, utilization/core dimensions'],
 ['Placement (V3B)','PASS in reviewed log','Placed-cell layout and post-place checks'],
 ['Clock-tree synthesis (V3B)','NOT VERIFIED','CTS completion log, skew and congestion/timing'],
 ['Detailed routing','NOT VERIFIED','Routed layout, routing reports, final optimized netlist'],
 ['Design-rule checking','NOT VERIFIED','Complete DRC report and violation count'],
 ['Parasitic extraction','NOT VERIFIED','Extracted RC data, SPEF or approved equivalent'],
 ['PrimeTime setup/hold','NOT VERIFIED','Post-layout max and min path reports including slack'],
 ['Final layout area/power','NOT VERIFIED','Layout bounding box/core area; final power report']
],[2.08*inch,1.57*inch,3.62*inch])
H2('5.1 Clock-tree congestion diagnosed')
story.append(P('An earlier clock-tree stage on the original 8-bit design failed with Fusion Compiler PLACE-004 / PLACE-006: <b>111.73% utilization</b>, requiring approximately <b>1,456 um2</b> in only <b>1,303 um2</b> available placement area. Placement success at a prior stage cannot establish a later CTS pass. A larger floorplan / lower target utilization and CTS rerun are indicated, followed by fresh timing, route and physical verification.'))
story.append(P('The corrected V3B placement run returned exit code 0 with no reported placement errors. Its CTS command was launched, but the final CTS report was not recovered after the SSH terminal became unresponsive. No route or sign-off results are claimed.'))
H2('5.2 Minimum post-route sign-off package')
bullet('Complete placed-and-routed design (DEF/GDS or approved layout formats), gate-level Verilog and SDC.')
bullet('DRC report with explicit pass/fail and rule check summary; verified post-route area and utilization.')
bullet('Extracted parasitic data / SPEF and extraction consistency report.')
bullet('PrimeTime setup report using max delay, and hold report using min delay, each with worst path and slack.')
bullet('Power report at documented activity, voltage and process corner; full scripts and source listings.')

story.append(PageBreak())
H1('6. Course rubric audit and reproducibility')
story.append(P('The course 90–100 bracket requires every major design and implementation element to be correctly verified and implemented, with clear documentation. RTL and mapped results are substantive, but missing CTS, routing, DRC, extracted parasitics and post-route setup/hold mean the current result cannot responsibly be described as fully satisfying that bracket.'))
table(['Course item','Current evidence','Required before claiming complete'],[
 ['RTL and Verilog testbench','Professor ZIP; independent directed/full-precision testbenches','Broader full-precision top-level regression if not yet done'],
 ['Simulation results','VCS logs, Verdi FSDB screenshots','Retain exact seeds, failing inputs and outcomes'],
 ['Synthesis / gate-level netlist','Fusion compiler mapping reports and intermediate netlist','Export optimized final post-route gate netlist'],
 ['Physical layout / DRC','Floorplan and placement checkpoint','Routed GDS/DEF and complete DRC output'],
 ['Parasitics and final timing','Configured technology models','Extract actual RC and PrimeTime setup + hold'],
 ['Area and power','Cell area from compile stage','Final routed layout area and power with units/corner'],
 ['Report and presentation','Three independent V4 slides plus 19-slide V4 deck','Insert genuine sign-off results once available']
],[1.73*inch,2.40*inch,3.14*inch])
H2('6.1 Safe continuation once SSH is authenticated')
story.append(P('Use a new authenticated Linux terminal, not a local macOS shell. Inspect the existing V3B CTS log before rerunning or changing a stage:'))
story.append(Preformatted('cd ~/ENGR852_Project/16_v3b_final_asic_fc\ntcsh\nsource scripts/synopsys_setup.tcl\ntail -n 40 v3b_cts.out\ngrep -E "^Error:|PLACE-004|PLACE-006" v3b_cts.out | tail -20',styles['CodeCustom']))
story.append(P('After CTS is truly complete, follow the instructor flow: route, signoff and PrimeTime. Never proceed solely because a Makefile command returned code zero; check logs, layout outputs, violations, extraction and the actual max/min timing slack.'))
H2('6.2 Evidence and complete source archive')
story.append(P('The versioned repository contains the professor original source, independent Verilog/SystemVerilog checks, SDC, slide build scripts, native waveform screenshots and a timestamped engineering notebook. Full source text is stored as editable files in the repository rather than raster images or copied code screens.'))
for item in [
 '<b>RTL:</b> rtl/top.v; rtl/experimental/top_full_precision_v3.v; rtl/experimental/top_full_precision_finish_hold.v',
 '<b>Stimulus:</b> tb/top_tb.v; tb/top_tb_direct.v; verification/motion_v3_full_precision_tb.sv; verification/motion_v3_hold_tb.sv; verification/motion_v3_all_saturated_tb.sv',
 '<b>Constraints:</b> constraints/top_520mhz.sdc and the copied course Fusion scripts on the Linux workspace.',
 '<b>Reports:</b> docs/UPDATE-016_V3_PPA_AND_SLIDES.md and docs/UPDATE-017_V4_FINAL_CHECKPOINT.md.',
 '<b>Presentations:</b> deliverables/ENGR852_Motion_Estimator_V4_Detailed_Waveform_3_Slides.pptx and deliverables/ENGR852_V4_Full_Team_19_Slides.pptx.'
]:bullet(item)
story.append(P('<b>Repository:</b> github.com/team-engr852/motion-estimator-asic-lab-notebook-2026','SmallCustom'))
story.append(P('<b>Final assessment caution:</b> this report documents completed work and remaining implementation measurements; it is not a fabricated post-layout sign-off report.','SmallCustom'))

def draw_page(canvas,doc):
 canvas.saveState()
 canvas.setStrokeColor(LIGHT);canvas.line(.62*inch,.59*inch,W-.62*inch,.59*inch)
 canvas.setFont('Helvetica',8)
 canvas.setFillColor(GRAY)
 canvas.drawString(.62*inch,.42*inch,'ENGR 852 | Motion Estimator | V4 measured evidence')
 canvas.drawRightString(W-.62*inch,.42*inch,f'Page {doc.page}')
 canvas.restoreState()

doc=SimpleDocTemplate(str(PDF),pagesize=letter,rightMargin=.62*inch,leftMargin=.62*inch,topMargin=.55*inch,bottomMargin=.70*inch,title='ENGR 852 Motion Estimator V4 Engineering Report',author='ENGR 852 Project Team')
doc.build(story,onFirstPage=draw_page,onLaterPages=draw_page)
print('ENGINEERING_REPORT_CREATED',PDF,'bytes',PDF.stat().st_size)
