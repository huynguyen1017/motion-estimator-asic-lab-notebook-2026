#!/usr/bin/env python3
"""Build a clearly labeled V6 slide revision without changing team slides 1–16."""
from pathlib import Path
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
SOURCE_FULL = OUT / "ENGR852_V5_Full_Team_19_Slides.pptx"
SOURCE_CONTRIBUTION = next(iter(sorted(OUT.glob("ENGR852_*V5_Routed_3_Slides.pptx"))), None)
if not SOURCE_FULL.is_file() or SOURCE_CONTRIBUTION is None:
    raise SystemExit("ERROR: source presentation missing; refusing to create incomplete deck")

def set_text(slide, shape_index, old_fragment, text):
    sh = slide.shapes[shape_index]
    if not sh.has_text_frame or old_fragment not in sh.text:
        raise RuntimeError(f"Shape {shape_index} does not contain expected text: {old_fragment}")
    # Preserve the existing shape geometry; use its first run for a stable style.
    tf = sh.text_frame
    first = tf.paragraphs[0]
    if first.runs:
        first.runs[0].text = text
        for run in first.runs[1:]:
            run.text = ""
        for par in tf.paragraphs[1:]:
            for run in par.runs:
                run.text = ""
    else:
        sh.text = text

def annotate(slides, offset):
    first, second = slides[offset], slides[offset+1]
    set_text(first, 1, "Directed high-contrast test",
             "VCS + Verdi  |  High-contrast stress test: reference 00 / search FF")
    set_text(first, 6, "All 256 pixels",
             "Stress case: 256 x |00 - FF| = FF00. Original 8-bit RTL saturates at FF and cannot select a winner.")
    set_text(second, 1, "Separate RTL and self-checking testbench",
             "VCS + Verdi  |  Independent high-contrast stress test (not the team's perfect-match case)")
    set_text(second, 9, "Encoded 4-bit vector",
             "Stress test: FF00 at (-8,-8). Team perfect-match test: BestDist 0000. Both are correct for their inputs.")

def scale_slide(slide, ratio):
    for shape in slide.shapes:
        shape.left = int(round(shape.left*ratio))
        shape.top = int(round(shape.top*ratio))
        shape.width = int(round(shape.width*ratio))
        shape.height = int(round(shape.height*ratio))
        if shape.has_text_frame:
            for paragraph in shape.text_frame.paragraphs:
                if paragraph.space_before:
                    paragraph.space_before = int(paragraph.space_before*ratio)
                if paragraph.space_after:
                    paragraph.space_after = int(paragraph.space_after*ratio)
                for run in paragraph.runs:
                    if run.font.size:
                        run.font.size = int(round(run.font.size*ratio))

full = Presentation(SOURCE_FULL)
part = Presentation(SOURCE_CONTRIBUTION)
assert len(full.slides) == 19 and len(part.slides) == 3
assert round(full.slide_width / part.slide_width, 4) == 0.75
assert round(full.slide_height / part.slide_height, 4) == 0.75
team_geometry = [
    [(s.shape_type, s.left,s.top,s.width,s.height,s.text if s.has_text_frame else None)
     for s in sl.shapes] for sl in list(full.slides)[:16]
]
annotate(full.slides, 16)
annotate(part.slides, 0)
scale_slide(full.slides[18], full.slide_width / part.slide_width)
assert all(
 [(s.shape_type, s.left,s.top,s.width,s.height,s.text if s.has_text_frame else None)
 for s in sl.shapes] == pre
 for sl, pre in zip(list(full.slides)[:16], team_geometry))
for i in range(16,19):
    slide = full.slides[i]
    assert all(s.left >= 0 and s.top >= 0 and
               s.left+s.width <= full.slide_width+1000 and
               s.top+s.height <= full.slide_height+1000 for s in slide.shapes),(i+1,"out of page")
for deck in [full, part]:
    assert not any("university" in shape.text.lower()
                   for sl in deck.slides for shape in sl.shapes if shape.has_text_frame)
path1 = OUT / "ENGR852_V6_Motion_Estimator_3_Contribution_Slides.pptx"
path2 = OUT / "ENGR852_V6_Motion_Estimator_Full_Team_19_Slides.pptx"
part.save(path1)
full.save(path2)
print("V6_SLIDES_CREATED",path1,path2)
print("CHECKS_OK team_slides_1_to_16_unchanged; slide_19_scaled; FF00_stress_vs_0000_perfect_match_labeled")
