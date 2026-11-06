// V3B: full-precision SAD with one-cycle delayed completion qualification.
// Independent 16-bit SAD architecture variant. Original professor RTL is untouched.

/* Module For Top Level Hierarchy */
module top (clock, start, BestDist, motionX, motionY, AddressR, AddressS1, AddressS2, R, S1, S2, completed);
    input clock;
    input start;
    output [15:0] BestDist;
    output [3:0] motionX, motionY;
    output completed;

    wire clock;
    wire start;
    wire [15:0] BestDist;
    wire [3:0] motionX, motionY;

    input [7:0] R, S1, S2;
    output [7:0] AddressR;
    output [9:0] AddressS1, AddressS2;

    wire [15:0] S1S2mux, newDist, PEready;
    wire CompStart;
    wire [3:0] VectorX, VectorY;
    wire [255:0] Accumulate;
    wire [7:0] Rpipe;

    control ctl_u(clock, start, S1S2mux, newDist, CompStart, PEready, VectorX, VectorY, AddressR, AddressS1, AddressS2, completed);

    PEtotal pe_u(clock, R, S1, S2, S1S2mux, newDist, Accumulate);

    reg completed_delayed;
    always @(posedge clock) begin
        if (!start) completed_delayed <= 1'b0;
        else completed_delayed <= completed;
    end
    wire [15:0] qualified_ready = PEready & {16{~completed_delayed}};
    Comparator comp_u(clock, CompStart, Accumulate, qualified_ready, VectorX, VectorY, BestDist, motionX, motionY);
endmodule

/* Module For Processing Element (PE) */
module PE (clock, R, S1, S2, S1S2mux, newDist, Accumulate, Rpipe);
    input clock;
    input [7:0] R, S1, S2; // memory inputs
    input S1S2mux, newDist; // control input
    output [15:0] Accumulate;
    output [7:0] Rpipe;
    reg [15:0] Accumulate, AccumulateIn;
    reg [7:0] difference, selected_s, difference_temp, Rpipe;

    always @(posedge clock) Rpipe <= R;
    always @(posedge clock) Accumulate <= AccumulateIn;

    always @(R or S1 or S2 or S1S2mux or newDist or Accumulate)
        begin
        selected_s = (S1S2mux? S1:S2);

        if (R > selected_s)
                difference = R - selected_s;
            else difference = selected_s - R;

        AccumulateIn = Accumulate + {8'h00, difference};

        if (newDist == 1) AccumulateIn = difference;
        end
endmodule

/* Module For The Last Processing Element (PEend) */
module PEend (clock, R, S1, S2, S1S2mux, newDist, Accumulate);
    input clock;
    input [7:0] R, S1, S2; // memory inputs
    input S1S2mux, newDist; // control input
    output [15:0] Accumulate;
    reg [15:0] Accumulate, AccumulateIn;
    reg [7:0] difference, selected_s;

    always @(posedge clock) Accumulate <= AccumulateIn;

    always @(R or S1 or S2 or S1S2mux or newDist or Accumulate)
        begin

        selected_s = (S1S2mux? S1:S2);

        if (R > selected_s)
                difference = R - selected_s;
            else difference = selected_s - R;


        AccumulateIn = Accumulate + {8'h00, difference};

        if (newDist == 1) AccumulateIn = difference;
        end
endmodule

/* Module For Control Unit */
module control (clock, start, S1S2mux, newDist, CompStart, PEready, VectorX, VectorY, AddressR, AddressS1, AddressS2, completed);
    input clock;
    input start; // = 1 when going
    output [15:0] S1S2mux, newDist, PEready;
    output CompStart;
    output [3:0] VectorX, VectorY;
    output [7:0] AddressR;
    output [9:0] AddressS1, AddressS2;
    output reg completed;

    parameter count_complete = 16*(16*16) + 15; //4111

    reg [15:0] S1S2mux, newDist, PEready;
    reg CompStart;
    reg [3:0] VectorX, VectorY;
    reg [7:0] AddressR;
    reg [9:0] AddressS1, AddressS2;
    reg  [12:0] count, count_temp;
    integer i;

    reg [11:0]  temp;
    always @ (posedge clock)
      begin
          if (start == 0) count <= 12'b0;
          else if (completed == 0) count <= count_temp;
      end

    always @ (count)
        begin
          count_temp = count + 1'b1;
          for (i=0; i<16; i= i+1)
        begin
           newDist[i] = (count[7:0] == i);
           PEready[i] = (newDist[i] && !(count < 256));
           S1S2mux[i] = (count[3:0] >= i);
           CompStart  = (!(count < 256));
        end

        AddressR = count[7:0];
        AddressS1 = (count[11:8] + count[7:4])*32 + count[3:0];

        temp = count[11:0]-16;
        AddressS2 = (temp[11:8] + temp[7:4])*32 + temp[3:0] + 16;

        VectorX = count[3:0] - 8;
        VectorY = count[11:8] - 9;

        completed = (count[12:0] == count_complete); //4111
        end
endmodule

/* Module For Comparator Unit */
module Comparator (clock, CompStart, PEout, PEready, vectorX, vectorY, BestDist, motionX, motionY);
    input clock;
    input CompStart; // goes high when distortion calculation start
    input [16*16-1:0] PEout; // outputs of PEs as one long vector
    input [15:0] PEready; // goes high when that PE has a new distortion
    input [3:0] vectorX, vectorY; // motion vector being evaluated
    output [15:0] BestDist; // best distortion vector so far
    output [3:0] motionX, motionY; // best motion vector so far
    reg [15:0] BestDist, newDist;
    reg [3:0] motionX, motionY;
    reg newBest;
    integer n;

    always @ (posedge clock)
      if (CompStart == 0) begin BestDist <= 16'hFFFF; motionX <= 4'h0; motionY <= 4'h0; end // initialize to highest value
      else if (newBest == 1)
        begin
          BestDist <= newDist;
          motionX <= vectorX;
          motionY <= vectorY;
        end

    always @ (BestDist or PEout or PEready or CompStart)
      begin
        newDist = 16'hFFFF;

        for (n = 0; n <= 15; n = n+1)
        begin
              if (PEready[n] == 1)
            case (n)
              4'b0000: newDist = PEout[15:0];
              4'b0001: newDist = PEout[31:16];
              4'b0010: newDist = PEout[47:32];
              4'b0011: newDist = PEout[63:48];
              4'b0100: newDist = PEout[79:64];
              4'b0101: newDist = PEout[95:80];
              4'b0110: newDist = PEout[111:96];
              4'b0111: newDist = PEout[127:112];
              4'b1000: newDist = PEout[143:128];
              4'b1001: newDist = PEout[159:144];
              4'b1010: newDist = PEout[175:160];
              4'b1011: newDist = PEout[191:176];
              4'b1100: newDist = PEout[207:192];
              4'b1101: newDist = PEout[223:208];
              4'b1110: newDist = PEout[239:224];
              4'b1111: newDist = PEout[255:240];
              default: newDist = 16'hFFFF;
            endcase
         end

        if ((|PEready == 0) || (CompStart == 0)) newBest = 0; // no PE is ready
        else if (newDist < BestDist) newBest = 1;
        else newBest = 0;
      end
endmodule

/* Module For Total 16 Processing Elements (PEtotal)*/
module PEtotal (clock, R, S1, S2, S1S2mux, newDist, Accumulate);
    input clock;
    input [7:0] R, S1, S2; // memory inputs
    input [15:0] S1S2mux, newDist; // control input
    output [255:0] Accumulate;

    wire [7:0] Rpipe0, Rpipe1, Rpipe2, Rpipe3, Rpipe4, Rpipe5, Rpipe6, Rpipe7, Rpipe8, Rpipe9, Rpipe10, Rpipe11, Rpipe12, Rpipe13, Rpipe14;

    PE pe0 (clock, R, S1, S2, S1S2mux[0], newDist[0], Accumulate[15:0], Rpipe0);

    PE pe1 (clock, Rpipe0, S1, S2, S1S2mux[1], newDist[1], Accumulate[31:16], Rpipe1);

    PE pe2 (clock, Rpipe1, S1, S2, S1S2mux[2], newDist[2], Accumulate[47:32], Rpipe2);

    PE pe3 (clock, Rpipe2, S1, S2, S1S2mux[3], newDist[3], Accumulate[63:48], Rpipe3);

    PE pe4 (clock, Rpipe3, S1, S2, S1S2mux[4], newDist[4], Accumulate[79:64], Rpipe4);

    PE pe5 (clock, Rpipe4, S1, S2, S1S2mux[5], newDist[5], Accumulate[95:80], Rpipe5);

    PE pe6 (clock, Rpipe5, S1, S2, S1S2mux[6], newDist[6], Accumulate[111:96], Rpipe6);

    PE pe7 (clock, Rpipe6, S1, S2, S1S2mux[7], newDist[7], Accumulate[127:112], Rpipe7);

    PE pe8 (clock, Rpipe7, S1, S2, S1S2mux[8], newDist[8], Accumulate[143:128], Rpipe8);

    PE pe9 (clock, Rpipe8, S1, S2, S1S2mux[9], newDist[9], Accumulate[159:144], Rpipe9);

    PE pe10 (clock, Rpipe9, S1, S2, S1S2mux[10], newDist[10], Accumulate[175:160], Rpipe10);

    PE pe11 (clock, Rpipe10, S1, S2, S1S2mux[11], newDist[11], Accumulate[191:176], Rpipe11);

    PE pe12 (clock, Rpipe11, S1, S2, S1S2mux[12], newDist[12], Accumulate[207:192], Rpipe12);

    PE pe13 (clock, Rpipe12, S1, S2, S1S2mux[13], newDist[13], Accumulate[223:208], Rpipe13);

    PE pe14 (clock, Rpipe13, S1, S2, S1S2mux[14], newDist[14], Accumulate[239:224], Rpipe14);

    PEend pe15 (clock, Rpipe14, S1, S2, S1S2mux[15], newDist[15], Accumulate[255:240]);
endmodule


/* Module For Reference Block (Memory) */
module ROM_R (clock, AddressR, R);
    input clock;
    input [7:0] AddressR;
    output [7:0] R;

    reg [7:0] R;
    reg [7:0] Rmem[0:255];


    //always @(posedge clock) R <= Rmem[AddressR];
    always @(*) R = Rmem[AddressR];

endmodule

/* Module For Search Block (Memory) */
module ROM_S (clock, AddressS1, AddressS2, S1, S2);
    input clock;
    input   [9:0]   AddressS1, AddressS2;
    output  [7:0]   S1, S2;

    reg [7:0]   S1, S2;
    reg [7:0]   Smem[0:1023];

    /*always @(posedge clock)
     begin
        S1 <= Smem[AddressS1];
        S2 <= Smem[AddressS2];
     end*/

    always @(*)
     begin
        S1 = Smem[AddressS1];
        S2 = Smem[AddressS2];
     end

endmodule
