from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

R=Path(__file__).resolve().parent.parent
PIC=R/'evidence/screenshots'
S=R/'slides'
S.mkdir(exist_ok=True)
a=PIC/'V4_original_controller_progress_nWave_1472px.png'
b=PIC/'V3_Verdi_original_saturated_window_only.png'
c=PIC/'V4_corrected_SAD_fullprecision_nWave_2240px.png'
for x in (a,b,c):
 assert x.exists(),f'Missing real Synopsys capture: {x}'
 Image.open(x).verify()

deck=Presentation()
deck.slide_width=Inches(13.333)
deck.slide_height=Inches(7.5)
INK=RGBColor(10,13,18)
SECONDARY=RGBColor(42,47,53)
LIGHT=RGBColor(220,225,231)
WHITE=RGBColor(255,255,255)
def text(s,x,y,w,h,t,pt=16,bold=False,clr=INK,font='Arial',align=None):
 shape=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
 f=shape.text_frame;f.clear();f.word_wrap=True
 for v in ('margin_top','margin_left','margin_right','margin_bottom'):
  setattr(f,v,Inches(0))
 p=f.paragraphs[0];p.text=t;p.font.name=font;p.font.size=Pt(pt);p.font.bold=bold;p.font.color.rgb=clr
 if align:p.alignment=align
 return shape
def base(title,subtitle):
 s=deck.slides.add_slide(deck.slide_layouts[6])
 text(s,.48,.28,12.2,.60,title,34,True)
 text(s,.52,.95,12.25,.35,subtitle,19,True)
 return s
def insert(s,f,x,y,w,h):
 im=Image.open(f);cw,ch=im.size
 scale=min(w/cw,h/ch);tw=cw*scale;th=ch*scale
 s.shapes.add_picture(str(f),Inches(x+(w-tw)/2),Inches(y+(h-th)/2),width=Inches(tw),height=Inches(th))
 return tw,th
def line(s,x,y,w):
 from pptx.enum.shapes import MSO_SHAPE
 l=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(.018))
 l.fill.solid();l.fill.fore_color.rgb=INK;l.line.fill.background()
def fig(s,x,y,w,description):
 text(s,x,y,w,.32,description,16,True)
def table(s,x,y,width,colw,headers,rows):
 from pptx.enum.shapes import MSO_SHAPE
 heights=.49
 for j,row in enumerate([headers]+rows):
  ty=y+j*.58
  for k,v in enumerate(row):
   xx=x+sum(colw[:k])
   rec=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(xx),Inches(ty),Inches(colw[k]-.025),Inches(.54))
   rec.fill.solid(); rec.fill.fore_color.rgb=RGBColor(232,236,240) if j==0 else (WHITE if j%2 else RGBColor(245,247,249))
   rec.line.color.rgb=LIGHT
   text(s,xx+.08,ty+.105,colw[k]-.14,.38,v,15,j==0 or k==0)
s=base('Original RTL: 8-bit SAD Saturation','VCS + Verdi   |   Directed high-contrast test')
insert(s,a,.50,1.50,12.32,2.73)
fig(s,.55,4.30,12.1,'Figure 1. PEready updates while newBest stays low; BestDist remains FF.')
insert(s,b,.53,4.75,8.50,1.75)
text(s,9.24,4.83,3.65,1.22,'At completion:\nBestDist = FF\nmotionX = X, motionY = X',18,True)
text(s,.60,6.65,12.1,.41,'All 256 pixels differ by FF, so the correct SAD is FF00. The 8-bit comparator cannot select an FF candidate against an FF reset value.',15)

s=base('16-bit SAD: Corrected Motion Vector','VCS + Verdi   |   Separate RTL and self-checking testbench')
insert(s,c,.52,1.52,12.25,2.63)
fig(s,.59,4.34,12.04,'Figure 2. newBest asserts and BestDist updates from FFFF to FF00.')
line(s,.58,4.90,12.05)
text(s,.65,5.13,5.78,.33,'Original RTL',18,True)
text(s,6.75,5.13,5.77,.33,'16-bit corrected RTL',18,True)
text(s,.65,5.57,5.80,.67,'BestDist = FF\nmotionX / motionY = X / X',18)
text(s,6.75,5.57,5.60,.67,'BestDist = FF00\nmotionX / motionY = 8 / 8',18)
text(s,.64,6.55,12.07,.46,'Encoded 4-bit vector (8,8) is signed (-8,-8). With equal SADs, the first candidate wins; the completion-hold test kept outputs stable.',15)

s=base('14 nm Synthesis: Area and Timing','Fusion Compiler   |   SAED14 RVT   |   520 MHz')
text(s,.58,1.48,7,.33,'Mapped design comparison',19,True)
table(s,.58,1.96,7.15,[3.15,1.94,2.06],['Metric','Original 8-bit','16-bit V3B'],[
 ['Standard-cell area','881.96 µm²','1,193.03 µm²'],
 ['Mapped cells','1,693','1,905'],
 ['Sequential cells','280','416'],
 ['Memory macros','0','0'],
])
text(s,8.02,1.50,4.65,.32,'Timing constraints',19,True)
text(s,8.05,2.02,4.55,2.00,'Clock: 1.923 ns (520 MHz)\nInput delay: 0.5 ns\nOutput delay: 0.5 ns\nClock uncertainty: 0.2 ns',17)
line(s,8.02,4.48,4.58)
text(s,8.05,4.70,4.55,.35,'Compile-stage setup slack',17,True)
text(s,8.05,5.14,4.60,.41,'+0.06 ns  (MET)',21,True)
line(s,.60,5.62,12.05)
text(s,.66,5.84,12.05,.56,'The 16-bit datapath uses 311.07 µm² more cell area (+35.3%) to preserve the full SAD. Synthesis, floorplan and placement are recorded; final routed setup/hold are separate checks.',16)
text(s,.66,6.63,12.05,.37,'Reference and search memories are in the testbench, not in the synthesized motion estimator.',15,False,SECONDARY)
out=S/'ENGR852_Motion_Estimator_V4_Detailed_Waveform_3_Slides.pptx'
deck.save(out)
print('CREATED',out,'slides',len(deck.slides),'bytes',out.stat().st_size)
for sl in deck.slides:
 for sh in sl.shapes:
  if sh.has_text_frame:
   assert 'university' not in sh.text.lower()
print('PASS: no forbidden wording in new slide text')
