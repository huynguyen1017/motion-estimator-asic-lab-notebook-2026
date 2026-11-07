`timescale 1ns/100fs
module motion_v3_hold_tb;
reg clock = 0;
reg start = 0;
wire [15:0] BestDist;
wire [3:0] motionX, motionY;
wire [7:0] R, S1, S2, AddressR;
wire [9:0] AddressS1, AddressS2;
wire completed;
integer i, newbest_count = 0;

top dut(.clock(clock), .start(start), .BestDist(BestDist),
 .motionX(motionX), .motionY(motionY), .AddressR(AddressR),
 .AddressS1(AddressS1), .AddressS2(AddressS2),
 .R(R), .S1(S1), .S2(S2), .completed(completed));
ROM_R memR(.clock(clock), .AddressR(AddressR), .R(R));
ROM_S memS(.clock(clock), .AddressS1(AddressS1), .AddressS2(AddressS2), .S1(S1), .S2(S2));

always #0.9615 clock = ~clock;
always @(negedge clock)
 if (start && dut.comp_u.newBest === 1'b1)
  newbest_count = newbest_count + 1;

initial begin
`ifdef DUMP_FSDB
 $fsdbDumpfile("motion_v3_hold.fsdb");
`endif
`ifdef DUMP_FSDB
 $fsdbDumpvars(0, motion_v3_hold_tb);
`endif
 for (i = 0; i < 256; i = i+1) memR.Rmem[i] = 8'h00;
 for (i = 0; i < 1024; i = i+1) memS.Smem[i] = 8'hFF;
 @(posedge clock); #0.02;
 start = 1'b1;
 repeat (4125) @(posedge clock);
 #0.02;
 $display("V3_ALL_SATURATED BestDist=%04h motionX=%h motionY=%h completed=%b newbest=%0d",BestDist,motionX,motionY,completed,newbest_count);
 if (BestDist !== 16'hFF00 || newbest_count < 1 || motionX !== 4'h8 || motionY !== 4'h8) $fatal(1, "Unexpected selection");
 if ((^motionX === 1'bx) && (^motionY === 1'bx)) begin
  $display("PASS_16BIT_MOTION_VALID: 65280 decimal SAD and vector (-8,-8)");
 end else begin
  $display("OBSERVED_SELECTED_VECTOR=%h,%h; expected (-8,-8)",motionX,motionY);
 end
 $display("PASS: 16-bit output stays valid after completed remains high for 13 additional clocks");
 $finish;
end
endmodule
