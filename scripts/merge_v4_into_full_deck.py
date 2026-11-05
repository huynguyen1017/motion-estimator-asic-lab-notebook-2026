from pathlib import Path
from io import BytesIO
from copy import deepcopy
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

root = Path(__file__).resolve().parent.parent
repo = Path.home() / "Developer/portfolio/motion-estimator-asic-lab-notebook-2026"
original = repo / "deliverables/ENGR852_Motion_Estimator_19_Slide_Final_2026-11-04.pptx"
contribution = root / "slides/ENGR852_Huy_V4_Detailed_Waveform_3_Slides.pptx"
output = root / "slides/ENGR852_V4_Full_Team_19_Slides.pptx"
source = Presentation(contribution)
target = Presentation(original)
assert len(source.slides) == 3 and len(target.slides) == 19
assert abs(source.slide_width / source.slide_height - target.slide_width / target.slide_height) < 0.001
scale_x = target.slide_width / source.slide_width
scale_y = target.slide_height / source.slide_height
old_first_16 = [(len(s.shapes), [x.text for x in s.shapes if x.has_text_frame][:2]) for s in list(target.slides)[:16]]
for offset in range(3):
    source_slide = source.slides[offset]
    destination_slide = target.slides[16+offset]
    for item in list(destination_slide.shapes):
        item.element.getparent().remove(item.element)
    for item in source_slide.shapes:
        left = int(item.left*scale_x)
        top = int(item.top*scale_y)
        width = int(item.width*scale_x)
        height = int(item.height*scale_y)
        if item.shape_type == MSO_SHAPE_TYPE.PICTURE:
            destination_slide.shapes.add_picture(BytesIO(item.image.blob), left, top, width=width,height=height)
            continue
        elm = deepcopy(item.element)
        destination_slide.shapes._spTree.insert_element_before(elm, "p:extLst")
        copied = destination_slide.shapes[-1]
        copied.left = left; copied.top = top
        copied.width = width; copied.height = height
        if copied.has_text_frame:
            for p in copied.text_frame.paragraphs:
                if p.font.size is not None:
                    p.font.size = int(p.font.size*scale_x)
                for run in p.runs:
                    if run.font.size is not None:
                        run.font.size = int(run.font.size*scale_x)
new_first_16 = [(len(s.shapes), [x.text for x in s.shapes if x.has_text_frame][:2]) for s in list(target.slides)[:16]]
assert new_first_16 == old_first_16, "The team's existing 16 slides were changed"
target.save(output)
check = Presentation(output)
assert len(check.slides) == 19
for i,heading in zip((16,17,18),("Original RTL:","16-bit SAD:","14 nm Synthesis:")):
    assert any(heading in s.text for s in check.slides[i].shapes if s.has_text_frame)
assert sum(sh.shape_type==MSO_SHAPE_TYPE.PICTURE for slide in list(check.slides)[16:19] for sh in slide.shapes)>=2
print("V4_FULL_DECK_CREATED",output,"bytes",output.stat().st_size)
print("ORIGINAL_FIRST_16_SLIDES_VERIFIED_UNCHANGED")
print("V3_SLIDES",[(i+1,len(s.shapes)) for i,s in enumerate(check.slides) if i>=16])
