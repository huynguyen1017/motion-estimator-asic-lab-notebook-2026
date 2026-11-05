from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile, ZIP_DEFLATED
import json, re

ROOT=Path(__file__).resolve().parent.parent
REPO=Path.home()/'Developer/portfolio/motion-estimator-asic-lab-notebook-2026'
OUT=ROOT/'report';OUT.mkdir(exist_ok=True)
ARCHIVE=OUT/'ENGR852_V4_Submission_and_Evidence_Bundle.zip'
items=[
 ('report/ENGR852_V4_Motion_Estimator_Engineering_Report.pdf',ROOT/'report/ENGR852_V4_Motion_Estimator_Engineering_Report.pdf'),
 ('presentation/ENGR852_V4_Full_Team_19_Slides.pptx',REPO/'deliverables/ENGR852_V4_Full_Team_19_Slides.pptx'),
 ('presentation/ENGR852_V4_Full_Team_19_Slides.pdf',REPO/'deliverables/ENGR852_V4_Full_Team_19_Slides.pdf'),
 ('presentation/ENGR852_Huy_V4_Detailed_Waveform_3_Slides.pptx',REPO/'deliverables/ENGR852_Huy_V4_Detailed_Waveform_3_Slides.pptx'),
 ('presentation/ENGR852_Huy_V4_Detailed_Waveform_3_Slides.pdf',REPO/'deliverables/ENGR852_Huy_V4_Detailed_Waveform_3_Slides.pdf'),
 ('rtl/top_original.v',REPO/'rtl/top.v'),
 ('rtl/top_full_precision_v3.v',REPO/'rtl/experimental/top_full_precision_v3.v'),
 ('rtl/top_full_precision_finish_hold.v',REPO/'rtl/experimental/top_full_precision_finish_hold.v'),
 ('constraints/top_520mhz.sdc',REPO/'constraints/top_520mhz.sdc'),
 ('testbench/top_tb.v',REPO/'tb/top_tb.v'),
 ('testbench/top_tb_direct.v',REPO/'tb/top_tb_direct.v'),
 ('testbench/huy_verification_520mhz_tb.v',REPO/'tb/huy_verification_520mhz_tb.v'),
 ('verification/huy_v3_all_saturated_tb.sv',REPO/'verification/huy_v3_all_saturated_tb.sv'),
 ('verification/huy_v3_full_precision_tb.sv',REPO/'verification/huy_v3_full_precision_tb.sv'),
 ('verification/huy_v3_hold_tb.sv',REPO/'verification/huy_v3_hold_tb.sv'),
 ('verification/huy_pe_fullprecision_scoreboard_tb.sv',REPO/'verification/huy_pe_fullprecision_scoreboard_tb.sv'),
 ('evidence/V4_original_controller_progress_nWave_1472px.png',REPO/'evidence/screenshots/V4_original_controller_progress_nWave_1472px.png'),
 ('evidence/V4_corrected_SAD_fullprecision_nWave_2240px.png',REPO/'evidence/screenshots/V4_corrected_SAD_fullprecision_nWave_2240px.png'),
 ('evidence/V3B_Verdi_nWave_2240wide_redacted.png',REPO/'evidence/screenshots/V3B_Verdi_nWave_2240wide_redacted.png'),
 ('evidence/huy_verification_520mhz.log',REPO/'evidence/logs/huy_verification_520mhz.log'),
 ('evidence/huy_synthesis_stat.log',REPO/'evidence/logs/huy_synthesis_stat.log'),
 ('scripts/build_v4_three_slides.py',REPO/'scripts/build_v4_three_slides.py'),
 ('scripts/merge_v4_into_full_deck.py',REPO/'scripts/merge_v4_into_full_deck.py'),
 ('scripts/build_v4_engineering_report.py',ROOT/'scripts/build_v4_engineering_report.py'),
 ('scripts/resume_v3_physical_flow.sh',REPO/'scripts/resume_v3_physical_flow.sh'),
 ('docs/UPDATE-017_V4_FINAL_CHECKPOINT.md',REPO/'docs/UPDATE-017_V4_FINAL_CHECKPOINT.md'),
]
manifest={}
for arc,src in items:
 if not src.is_file():
  raise SystemExit(f'MISSING REQUIRED PACKAGE FILE {arc}: {src}')
 data=src.read_bytes()
 if src.suffix in ('.md','.py','.sh','.sv','.v','.sdc','.txt','.log'):
  if b'Huongphat12@' in data or b'926784856' in data:
   raise SystemExit(f'SECRET_OR_STUDENT_ID_FOUND {arc}')
 manifest[arc]={'sha256':sha256(data).hexdigest(),'bytes':len(data)}
notice='''ENGR 852 Motion Estimator - V4 package
======================================
Actual VCS/Verdi and Fusion Compiler mapped results are included.
Original source, corrected RTL, testbenches and SDC are editable.
The three additional slides are intended for independent contribution.

IMPORTANT PHYSICAL DESIGN GATES
Synthesis/floorplan/V3B placement: measured.
CTS / routing / DRC / parasitic extraction / post-layout PrimeTime setup & hold: NOT VERIFIED.
No final routed layout or extracted-timing values are fabricated.
Re-authentication to the authorized server is required to resume those stages.

Read the six-page report and docs/UPDATE-017_V4_FINAL_CHECKPOINT.md first.
Only source files and generated evidence are included. No licensed technology libraries.
'''
with ZipFile(ARCHIVE,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('READ_ME_FIRST.txt',notice)
 for arc,src in items:z.write(src,arc)
 z.writestr('SHA256_MANIFEST.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
with ZipFile(ARCHIVE) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(items)+2
 for arc,m in manifest.items():assert sha256(z.read(arc)).hexdigest()==m['sha256']
print('PACKAGE_CREATED',ARCHIVE,'bytes',ARCHIVE.stat().st_size,'files',len(manifest)+2)
