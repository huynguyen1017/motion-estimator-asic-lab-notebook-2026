from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

R=Path(__file__).resolve().parent.parent
out=R/'deliverables'
src3=out/'ENGR852_Motion_Estimator_V4_Detailed_Waveform_3_Slides.pptx'
src19=out/'ENGR852_V4_Full_Team_19_Slides.pptx'
assert src3.exists() and src19.exists()
COLOR=RGBColor(12,20,30)
GRAY=RGBColor(65,72,80)
BORDER=RGBColor(220,225,231)
FILL=RGBColor(237,241,245)
WHITE=RGBColor(255,255,255)
def text(s,x,y,w,h,title,pt=16,bold=False,fg=COLOR,align=None):
 a=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
 f=a.text_frame;f.clear();f.word_wrap=True
 for k in ('margin_top','margin_bottom','margin_left','margin_right'):setattr(f,k,Inches(0))
 p=f.paragraphs[0];p.text=title;p.font.name='Arial';p.font.bold=bold;p.font.size=Pt(pt);p.font.color.rgb=fg
 if align:p.alignment=align
 return a
def section(s,x,y,title,w):
 text(s,x,y,w,.34,title,18,True)
def rect(s,x,y,w,h,fill,border=BORDER):
 z=s.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
 z.fill.solid();z.fill.fore_color.rgb=fill;z.line.color.rgb=border
 return z
def table(s,x,y,widths,rows):
 h=.47
 for rowidx,row in enumerate(rows):
  yy=y+rowidx*(h+.025)
  xx=x
  for colidx,value in enumerate(row):
   ww=widths[colidx]
   rect(s,xx,yy,ww-.02,h,FILL if rowidx==0 else WHITE if rowidx%2 else RGBColor(248,249,251))
   text(s,xx+.08,yy+.105,ww-.12,.30,value,12.7 if rowidx else 13.8,rowidx==0 or colidx==0)
   xx+=ww
def replacement(slide):
 for sh in list(slide.shapes):
  node=sh._element;node.getparent().remove(node)
 text(slide,.5,.32,12.30,.55,'14 nm Routed ASIC: Area, Power, and Timing',32,True)
 text(slide,.51,.98,12.25,.35,'Fusion Compiler + PrimeTime  |  520 MHz  |  Results before hold ECO',19,True)
 section(slide,.54,1.51,'Physical implementation',6.1)
 table(slide,.54,1.94,[3.56,2.70],[
  ('Report metric','Synopsys result'),
  ('Routed standard-cell area','2,781.30 µm²'),
  ('Die boundary','92.51 × 50.80 µm'),
  ('Mapped cells','6,310'),
  ('Sequential cells','449'),
  ('Memory macro cells','0'),
  ('Typical power (0.8V, 25°C)','0.729 mW'),
 ])
 section(slide,7.15,1.51,'PrimeTime: extracted RC',5.62)
 table(slide,7.15,1.94,[1.86,1.94,1.95],[
  ('Corner','Setup WNS','Hold WNS'),
  ('Fast','+0.52 ns','−0.14 ns'),
  ('Typical','+0.30 ns','−0.12 ns'),
  ('Slow','−0.06 ns','−0.09 ns'),
 ])
 text(slide,7.20,4.42,5.48,.78,'Setup: 17 slow-corner violations\nHold: 402 fast / 120 typical / 33 slow',15,True)
 rect(slide,.56,5.70,12.2,.018,COLOR,COLOR)
 text(slide,.61,5.88,12.0,.72,'CTS and route completed. Final ICV DRC: 18 violations. PrimeTime hold repair and physical recheck are required before sign-off.',17,True)
 text(slide,.60,6.82,12.0,.30,'SDC: 1.923 ns clock   |   0.50 ns input/output delays   |   0.20 ns clock uncertainty',13.2,False,GRAY)

for stem,source,idx,outfile in [
('3',src3,2,'ENGR852_Motion_Estimator_V5_Routed_3_Slides.pptx'),
('19',src19,18,'ENGR852_V5_Full_Team_19_Slides.pptx')]:
 p=Presentation(source);assert len(p.slides)==int(stem)
 replacement(p.slides[idx])
 dest=out/outfile;p.save(dest)
 assert all('university' not in x.text.lower() for slide in p.slides for x in slide.shapes if x.has_text_frame)
 print('V5_SLIDES_CREATED',dest.name,len(p.slides),dest.stat().st_size)
# Ensure first 16 team slides in complete deck remain the same content and placement
a=Presentation(src19)
b=Presentation(out/'ENGR852_V5_Full_Team_19_Slides.pptx')
for idx in range(16):
 sa,sb=a.slides[idx],b.slides[idx]
 assert len(sa.shapes)==len(sb.shapes)
 for u,v in zip(sa.shapes,sb.shapes):
  assert (u.shape_type,u.left,u.top,u.width,u.height,u.text if u.has_text_frame else None)==(v.shape_type,v.left,v.top,v.width,v.height,v.text if v.has_text_frame else None)
print('V5_TEAM_FIRST_16_UNCHANGED')
