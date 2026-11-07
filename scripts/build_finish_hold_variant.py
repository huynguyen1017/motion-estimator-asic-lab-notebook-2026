from pathlib import Path
r=Path.home()/"Developer/coursework/sfsu/2026-fall/sfsu-engr852-2026-fall/contributions/motion-v3-university-tool-flow-2026-11-04"
src=(r/"rtl/full_precision_variant/top_full_precision.v").read_text()
assert src.count("Comparator comp_u(clock, CompStart, Accumulate, PEready,")==1
src=src.replace("Comparator comp_u(clock, CompStart, Accumulate, PEready,",
"""reg completed_delayed;
    always @(posedge clock) begin
        if (!start) completed_delayed <= 1'b0;
        else completed_delayed <= completed;
    end
    wire [15:0] qualified_ready = PEready & {16{~completed_delayed}};
    Comparator comp_u(clock, CompStart, Accumulate, qualified_ready,""")
src="// V3B: full-precision SAD with one-cycle delayed completion qualification.\n"+src
dest=r/"rtl/full_precision_variant/top_full_precision_finish_hold.v"
dest.write_text(src)
orig=(r/"verification/motion_v3_full_precision_tb.sv").read_text()
assert "repeat (4112)" in orig
test=orig.replace("repeat (4112)","repeat (4125)")
test=test.replace("module motion_v3_full_precision_tb;", "module motion_v3_hold_tb;")
test=test.replace("$fsdbDumpvars(0, motion_v3_full_precision_tb);","$fsdbDumpvars(0, motion_v3_hold_tb);")
test=test.replace("motion_v3_full_precision.fsdb","motion_v3_hold.fsdb")
test=test.replace("motion_v3_full_precision_tb)","motion_v3_hold_tb)")
test=test.replace("PASS: Corrected full-precision variant selected (-8,-8) with nonzero 16-bit SAD","PASS: 16-bit output stays valid after completed remains high for 13 additional clocks")
(r/"verification/motion_v3_hold_tb.sv").write_text(test)
# For independent Icarus smoke check, disable Synopsys FSDB system tasks.
smoke=test.replace(' $fsdbDumpfile("motion_v3_hold.fsdb");','').replace(' $fsdbDumpvars(0, motion_v3_hold_tb);','')
(r/"verification/motion_v3_hold_icarus_tb.sv").write_text(smoke)
print("V3B_VARIANT_CREATED",dest)
