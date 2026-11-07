from pathlib import Path
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor

root=Path.home()/"Developer/portfolio/motion-estimator-asic-lab-notebook-2026"
out=root/"deliverables"
refs=[
    (out/"ENGR852_V7_Complete_19_Slides.pptx",out/"ENGR852_V8_Complete_19_Slides.pptx",19),
    (out/"ENGR852_V7_Clean_Waveform_3_Slides.pptx",out/"ENGR852_V8_Clean_3_Contribution_Slides.pptx",3),
]
for src,dst,count in refs:
    p=Presentation(src);assert len(p.slides)==count
    preserved=[s._element.xml for s in list(p.slides)[:13]] if count==19 else []
    targeted=list(p.slides)[-3:]
    first,second,last=targeted
    for sh in second.shapes:
        if sh.has_text_frame and "FF00 is not the expected output" in sh.text:
            sh.text="Exact match: SAD = 0x0000  |  Maximum contrast: SAD = 0xFF00"
            sh.left=Inches(.53);sh.top=Inches(5.28);sh.width=Inches(8.93);sh.height=Inches(.30)
            para=sh.text_frame.paragraphs[0];para.font.size=Pt(12.0);para.font.bold=True;para.font.name="Arial"
            para.font.color.rgb=RGBColor(0,84,116)
    for sh in last.shapes:
        if sh.has_text_frame:
            if "Final sign-off requires" in sh.text:
                sh.text="520 MHz SDC: 1.923 ns period  |  0.5 ns I/O delay  |  0.2 ns uncertainty"
                para=sh.text_frame.paragraphs[0];para.font.name="Arial";para.font.size=Pt(10.8)
                para.font.color.rgb=RGBColor(12,17,22)
            if "V5: CTS and routing completed" in sh.text:
                sh.text="ICV DRC (routed V5): 18 geometry violations measured."
                para=sh.text_frame.paragraphs[0];para.font.name="Arial";para.font.size=Pt(12);para.font.bold=True
    if count==19:
        for sl in list(p.slides)[13:16]:
            for sh in list(sl.shapes):
                if sh.has_text_frame and ("Executed 520 MHz verification" in sh.text or "Analytical & cycle-accurate" in sh.text or "Yosys 0.70 synthesis" in sh.text):
                    sl.shapes._spTree.remove(sh._element)
        assert [s._element.xml for s in list(p.slides)[:13]] == preserved
    for sl in targeted:
        for sh in sl.shapes:
            assert sh.left>=0 and sh.top>=0 and sh.left+sh.width<=p.slide_width+1500 and sh.top+sh.height<=p.slide_height+1500,(str(dst),sh.name)
            if sh.has_text_frame:
                st=sh.text.lower()
                assert all(k not in st for k in ["selected candidate","non-selected candidate","final sign-off requires","ff00 is not the expected"])
    p.save(dst)
    print("V8_SAVED",str(dst),dst.stat().st_size)
print("V8_QA_PASS")
