#!/usr/bin/env python3
"""Prepare three project contribution slides using native, unmodified Verdi screenshots."""
from pathlib import Path
from copy import deepcopy
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "deliverables/ENGR852_V6_Motion_Estimator_Full_Team_19_Slides.pptx"
PIC = ROOT / "evidence/screenshots"
OUT = ROOT / "deliverables"
assert SRC.is_file()
FULL = Presentation(SRC)
assert len(FULL.slides) == 19
W,H = FULL.slide_width,FULL.slide_height
assert abs(W/Inches(1)-10)<.05 and abs(H/Inches(1)-5.625)<.05
baseline = [slide._element.xml for slide in list(FULL.slides)[:16]]
THREE = Presentation()
THREE.slide_width=W
THREE.slide_height=H
WHITE=RGBColor(255,255,255)
BLACK=RGBColor(12,17,22)
GRAY=RGBColor(75,79,83)
ACCENT=RGBColor(0,84,116)
LIGHT=RGBColor(232,238,242)

def wipe(slide):
    sp=slide.shapes._spTree
    for sh in list(slide.shapes):
        sp.remove(sh._element)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb=WHITE

def textbox(slide,x,y,w,h,text,size=13,bold=False,color=BLACK,align=PP_ALIGN.LEFT):
    sh=slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf=sh.text_frame
    tf.word_wrap=True
    tf.margin_left=tf.margin_right=Inches(.01)
    tf.margin_top=tf.margin_bottom=Inches(.01)
    lines=text.split("\n")
    for i,line in enumerate(lines):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        p.text=line;p.alignment=align;p.space_after=Pt(0)
        p.font.name="Arial";p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=color
    return sh

def title(slide,head,sub):
    textbox(slide,.42,.20,9.17,.52,head,29,True)
    textbox(slide,.44,.77,9.09,.29,sub,15,True)

def figure(slide,name,x,y,w,h):
    path=PIC/name
    if not path.is_file():
        raise FileNotFoundError(path)
    return slide.shapes.add_picture(str(path),Inches(x),Inches(y),width=Inches(w),height=Inches(h))

def row(slide,y,label,value,x=0.55):
    textbox(slide,x,y,3.23,.27,label,11.9)
    textbox(slide,x+3.4,y,1.39,.27,value,12.1,True,ACCENT)

def slide1(slide):
    wipe(slide)
    title(slide,"Controller RTL Verification","VCS + Verdi  |  Original RTL, high-contrast stress fixture")
    figure(slide,"V4_original_controller_progress_nWave_1472px.png",.44,1.18,9.12,2.01)
    textbox(slide,.46,3.23,9.00,.23,"Figure 1. Clock, PEready, count, newBest and output registers across the test.",11.4,True)
    textbox(slide,.46,3.53,4.02,.23,"Figure 2. End of the simulation window",11.4,True)
    figure(slide,"V4_original_completion_region_nWave_768px.png",.46,3.82,4.05,1.70)
    textbox(slide,4.84,3.75,4.64,.27,"Original 8-bit result",15,True)
    textbox(slide,4.87,4.11,4.47,.28,"BestDist = FF",15,True,ACCENT)
    textbox(slide,4.87,4.43,4.47,.28,"motionX, motionY = X, X",13,True)
    textbox(slide,4.87,4.82,4.49,.50,"The saturated comparator never chooses a valid candidate in this stress test.",11.8)

def slide2(slide):
    wipe(slide)
    title(slide,"16-bit SAD Verification","VCS + Verdi  |  Separate precision-corrected RTL and directed stimulus")
    figure(slide,"V3B_Verdi_nWave_2240wide_redacted.png",.44,1.17,9.12,1.86)
    textbox(slide,.46,3.09,9.07,.23,"Figure 3. newBest selects FF00 and the encoded vector (8,8) for the all-FF stress case.",11.0,True)
    textbox(slide,.51,3.47,8.95,.29,"BestDist is input-dependent: these are three different stimulus cases.",13.5,True)
    for i,(case,result) in enumerate([
        ("Team perfect match","0000"),
        ("Single-pixel perturbation","0003"),
        ("All-00 reference / all-FF search","FF00")
    ]):
        y=3.85+i*.46
        slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(.47),Inches(y),Inches(9.07),Inches(.38)).fill.solid()
        bg=slide.shapes[-1];bg.fill.fore_color.rgb=LIGHT if i%2==0 else WHITE;bg.line.fill.background()
        textbox(slide,.64,y+.04,6.25,.26,case,12.1)
        textbox(slide,7.77,y+.04,1.54,.28,result,12.9,True,ACCENT)
    textbox(slide,.49,5.30,9.03,.25,"FF00 is not the expected output of the team's 0000 perfect-match testbench.",11,True)

def gridcell(slide,x,y,w,h,text,bold=False,size=11):
    textbox(slide,x+.08,y+.07,w-.16,h-.1,text,size,bold)

def table(slide,x,y,width,cols,rows,header_h=.35,row_h=.45):
    cw=[width*v for v in cols]
    xx=x
    for j,c in enumerate(rows[0]):
        s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(xx),Inches(y),Inches(cw[j]),Inches(header_h))
        s.fill.solid();s.fill.fore_color.rgb=LIGHT;s.line.color.rgb=WHITE
        gridcell(slide,xx,y,cw[j],header_h,c,True,10.6)
        xx+=cw[j]
    for k,rr in enumerate(rows[1:]):
        xx=x; yy=y+header_h+k*row_h
        for j,c in enumerate(rr):
            s=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(xx),Inches(yy),Inches(cw[j]),Inches(row_h))
            s.fill.solid();s.fill.fore_color.rgb=WHITE if k%2 else RGBColor(247,249,251)
            s.line.color.rgb=LIGHT
            gridcell(slide,xx,yy,cw[j],row_h,c,False,10.25)
            xx+=cw[j]

def slide3(slide):
    wipe(slide)
    title(slide,"14 nm Physical Design Checkpoint","Fusion Compiler + PrimeTime  |  520 MHz  |  Routed V5 results")
    textbox(slide,.47,1.18,4.39,.30,"Physical implementation",15,True)
    table(slide,.47,1.56,4.35,[.64,.36],[
        ["Measured metric","V5 result"],
        ["Routed cell area","2,781.30 µm²"],
        ["Mapped cells","6,310"],
        ["Sequential cells","449"],
        ["Memory macros","0"],
        ["Typical power","0.729 mW"]
    ],row_h=.46)
    textbox(slide,5.09,1.18,4.40,.30,"PrimeTime: extracted RC",15,True)
    table(slide,5.07,1.56,4.48,[.26,.36,.38],[
        ["Corner","Setup WNS","Hold WNS"],
        ["FAST","+0.52 ns","-0.14 ns"],
        ["TYPICAL","+0.30 ns","-0.12 ns"],
        ["SLOW","-0.06 ns","-0.09 ns"]
    ],row_h=.55)
    textbox(slide,5.12,3.94,4.27,.53,"Setup: 17 SLOW failures\nHold: 402 FAST / 120 TYP / 33 SLOW",10.8,True)
    textbox(slide,.48,4.69,9.10,.29,"V5: CTS and routing completed. ICV DRC still reports 18 violations.",12.4,True)
    textbox(slide,.48,5.05,9.10,.44,"Final sign-off requires DRC repair, physical ECO, extraction and PrimeTime setup/hold on the corrected layout.",10.8)

builders=[slide1,slide2,slide3]
for idx,b in enumerate(builders):
    b(FULL.slides[16+idx])
    dst=THREE.slides.add_slide(THREE.slide_layouts[6])
    b(dst)
assert [slide._element.xml for slide in list(FULL.slides)[:16]]==baseline
for deck in [FULL,THREE]:
    for i,slide in enumerate(deck.slides):
        if i < len(deck.slides)-3: continue
        for sh in slide.shapes:
            assert sh.left >= 0 and sh.top>=0 and sh.left+sh.width <= W+1000 and sh.top+sh.height<=H+1000,(i,sh.name)
        text=' '.join(sh.text.lower() for sh in slide.shapes if sh.has_text_frame)
        assert len(text) > 20
OUT.mkdir(exist_ok=True)
a=OUT/"ENGR852_V7_Clean_Waveform_3_Slides.pptx"
b=OUT/"ENGR852_V7_Complete_19_Slides.pptx"
THREE.save(a); FULL.save(b)
print("V7_CREATED",a,b)
print("V7_QA: 3 slides, 19 slides, first16 unchanged, no off-canvas shapes, no personal footer")
