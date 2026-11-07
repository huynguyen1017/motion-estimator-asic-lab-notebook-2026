from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
from pathlib import Path
import math

ROOT=Path(__file__).resolve().parent.parent
REPO=Path.home()/"Developer/portfolio/motion-estimator-asic-lab-notebook-2026"
OUTPUT=ROOT/"slides"
OUTPUT.mkdir(parents=True,exist_ok=True)
ORIGINAL=ROOT/"evidence/screenshots/V3_Verdi_original_saturated_window_only.png"
CORRECTED=REPO/"evidence/screenshots/V3B_Verdi_nWave_2240wide_redacted.png"
assert ORIGINAL.exists() and CORRECTED.exists(), "Actual application screenshots are required"
for p in (ORIGINAL,CORRECTED):
    im=Image.open(p); im.verify()
    
p=Presentation();p.slide_width=Inches(13.333);p.slide_height=Inches(7.5)
BLACK=RGBColor(17,20,23); MID=RGBColor(50,58,65); LIGHT=RGBColor(245,246,248); BORDER=RGBColor(204,211,218)
ACCENT=RGBColor(0,79,123)
def txt(slide,x,y,w,h,text,size=16,bold=False,color=BLACK,font='Arial',align=None):
    box=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame=box.text_frame;frame.clear();frame.word_wrap=True
    frame.margin_left=Inches(.02);frame.margin_right=Inches(.02)
    frame.margin_top=Inches(.02);frame.margin_bottom=Inches(.02)
    pp=frame.paragraphs[0];pp.text=text;pp.font.name=font;pp.font.size=Pt(size);pp.font.bold=bold;pp.font.color.rgb=color
    if align is not None: pp.alignment=align
    return box
def rect(s,x,y,w,h,fill=LIGHT,border=None):
    a=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    a.fill.solid();a.fill.fore_color.rgb=fill
    a.line.fill.background() if border is None else None
    if border is not None:a.line.color.rgb=border
    return a
def base(title,sub,n):
    s=p.slides.add_slide(p.slide_layouts[6])
    txt(s,.42,.18,12.5,.62,title,37,True)
    txt(s,.45,.85,12.4,.34,sub,18,True,MID)
    rect(s,.44,1.33,12.45,.025,BLACK)
    txt(s,.45,7.13,11.4,.2,"ENGR 852  |  V3 independent verification and SAED14 implementation  |  Native university Synopsys output",10,False,MID)
    txt(s,12.55,7.12,.36,.22,str(n),10,False,MID,align=PP_ALIGN.RIGHT)
    return s
def fit_image(s,file,x,y,maxw,maxh):
    im=Image.open(file);w,h=im.size; ratio=min(maxw/w,maxh/h)
    W=w*ratio;H=h*ratio
    s.shapes.add_picture(str(file),Inches(x+(maxw-W)/2),Inches(y+(maxh-H)/2),width=Inches(W),height=Inches(H))
    return (W,H)
def note(s,x,y,w,heading,details):
    rect(s,x,y,w,1.00,LIGHT)
    txt(s,x+.12,y+.12,w-.24,.26,heading,15,True,BLACK)
    txt(s,x+.12,y+.46,w-.24,.46,details,14,False,MID)
s=base("SAD Saturation — Original RTL","VCS + Verdi nWave  |  Directed 16×16 high-contrast corner case",1)
fit_image(s,ORIGINAL,.51,1.62,12.24,3.15)
txt(s,.51,4.87,12.05,.26,"Figure 1: Original 8-bit datapath; full VCS result: completed = 1, BestDist = FF, motionX/Y = X.",15,True)
note(s,.51,5.24,3.9,"Stimulus","Reference pixels = 00; search pixels = FF.")
note(s,4.55,5.24,3.9,"Expected 16-bit SAD","256 × |00 − FF| = 65,280 = FF00.")
note(s,8.59,5.24,4.12,"Observed failure","8-bit output saturates at FF; no newBest event.")
txt(s,.53,6.51,12.1,.40,"Cause: the comparator resets BestDist to FF and accepts a candidate only when newDist < BestDist. FF cannot beat FF.",14,False,MID)
s=base("16-bit SAD — Verification After RTL Change","VCS + Verdi nWave  |  Separate full-precision and completion-hold variant",2)
fit_image(s,CORRECTED,.50,1.75,12.32,2.63)
txt(s,.55,4.51,12.15,.28,"Figure 2: Synopsys FSDB shown in Verdi nWave; newBest asserts and BestDist becomes FF00.",15,True)
note(s,.52,5.00,3.95,"BestDist","FF00 (65,280 decimal), 16-bit accumulator.")
note(s,4.65,5.00,3.95,"Selected vector","motionX=8, motionY=8 → (−8,−8).")
note(s,8.78,5.00,3.95,"Tie handling","All search candidates equal; first is retained.")
txt(s,.56,6.33,12.03,.48,"Original professor RTL retained separately. The wider accumulator fixes the FF no-selection corner case; further varied-image regression is still required.",14,False,MID)
s=base("520 MHz ASIC Implementation","Synopsys Fusion Compiler X-2025.06-SP2a  |  SAED14 RVT library",3)
txt(s,.58,1.60,5.75,.35,"Measured mapped-design comparison",19,True)
headers=["Metric","Original 8-bit","16-bit V3B"]
rows=[["Standard-cell area","881.96 µm²","1,193.03 µm²"],["Total mapped cells","1,693","1,905"],["Sequential cells","280","416"],["Macro / memory cells","0","0"]]
xs=[.62,3.4,5.55];widths=[2.68,2.1,2.12]
for i,h in enumerate(headers):
    rect(s,xs[i],2.15,widths[i],.50,RGBColor(231,235,238))
    txt(s,xs[i]+.09,2.22,widths[i]-.18,.27,h,13,True)
for rowidx,row in enumerate(rows):
    y=2.66+rowidx*.64
    for i,value in enumerate(row):
        rect(s,xs[i],y,widths[i],.60, RGBColor(248,249,250) if rowidx%2==0 else RGBColor(238,241,244))
        txt(s,xs[i]+.10,y+.13,widths[i]-.15,.34,value,14, i==0)
txt(s,7.83,1.61,4.8,.34,"Required course constraints",19,True)
for j,v in enumerate(["Clock period: 1.923 ns  (520 MHz)","Input and output delay: 0.5 ns","Clock uncertainty: 0.2 ns","Reference/search memories: testbench only"]):
    txt(s,7.86,2.21+j*.56,4.8,.38,v,15)
rect(s,7.82,4.64,4.78,1.47,RGBColor(246,247,248))
txt(s,7.95,4.78,4.57,.31,"Implementation checkpoint",16,True)
txt(s,7.95,5.18,4.40,.80,"Synthesis, floorplan and placement completed. CTS / route / DRC / extraction / PrimeTime final setup and hold are not yet verified.",14)
txt(s,.62,5.60,6.7,.34,"V3B compile-stage setup slack: +0.06 ns (MET).",15,True)
txt(s,.62,6.13,6.78,.66,"Area increased by 311.07 µm² (35.3%) versus the 8-bit baseline. This is the area cost of the corrected wider datapath; not post-route area.",13,False,MID)
out=OUTPUT/"ENGR852_Motion_Estimator_V3_Independent_3_Slides.pptx"
p.save(out)
print("CREATED",out,"slides",len(p.slides),"bytes",out.stat().st_size)
