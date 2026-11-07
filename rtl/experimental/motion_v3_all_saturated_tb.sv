`timescale 1ns/100fs
module motion_v3_all_saturated_tb;
reg clock = 0;
reg start = 0;
wire [7:0] BestDist;
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
 $fsdbDumpfile("motion_v3_all_saturated.fsdb");
`endif
`ifdef DUMP_FSDB
 $fsdbDumpvars(0, motion_v3_all_saturated_tb);
`endif
 for (i = 0; i < 256; i = i+1) memR.Rmem[i] = 8'h00;
 for (i = 0; i < 1024; i = i+1) memS.Smem[i] = 8'hFF;
 @(posedge clock); #0.02;
 start = 1'b1;
 repeat (4117) @(posedge clock);
 #0.02;
 $display("V3_ALL_SATURATED BestDist=%02h motionX=%h motionY=%h completed=%b newbest=%0d",BestDist,motionX,motionY,completed,newbest_count);
 if (BestDist !== 8'hFF || newbest_count != 0) $fatal(1, "Unexpected selection");
 if ((^motionX === 1'bx) && (^motionY === 1'bx)) begin
  $display("OBSERVED_NO_VALID_MOTION_VECTOR: all saturated SADs tie reset sentinel FF");
 end else begin
  $display("OBSERVED_VECTOR=%h,%h; no newBest event occurred",motionX,motionY);
 end
 $display("PASS: Reproduced no-selection case in unmodified textbook RTL");
 $finish;
end
endmodule
