
`timescale 1ns/100fs

module motion_v5_16bit_top_regression_tb;
    wire [15:0] BestDist;
    wire [3:0] motionX, motionY;
    wire [7:0] R, S1, S2;
    wire [7:0] AddressR;
    wire [9:0] AddressS1, AddressS2;
    wire       completed;

    reg        clock;
    reg        start;
    reg [7:0]  Rmem[0:255];
    reg [7:0]  Smem[0:1023];

    integer    i;
    integer    Expected_motionX, Expected_motionY;
    integer signed x, y;
    realtime   t_start, t_match, t_complete;

    top dut (
        .clock(clock),
        .start(start),
        .BestDist(BestDist),
        .motionX(motionX),
        .motionY(motionY),
        .AddressR(AddressR),
        .AddressS1(AddressS1),
        .AddressS2(AddressS2),
        .R(R),
        .S1(S1),
        .S2(S2),
        .completed(completed)
    );

    ROM_R memR_u(.clock(clock), .AddressR(AddressR), .R(R));
    ROM_S memS_u(.clock(clock), .AddressS1(AddressS1), .AddressS2(AddressS2), .S1(S1), .S2(S2));

    // Team 520 MHz clock modification: half-period = 0.9615 ns -> period = 1.9230 ns
    always #0.9615 clock = ~clock;

    task automatic decode_motion(input [3:0] mx, input [3:0] my, output integer signed sx, output integer signed sy);
        begin
            sx = (mx >= 8) ? (mx - 16) : mx;
            sy = (my >= 8) ? (my - 16) : my;
        end
    endtask

    initial begin
        // Native VCS FSDB remains available in the V3 evidence. This regression uses portable VCD.
        // No vendor-specific FSDB call required for local test.
`ifdef ENABLE_FSDB
`ifndef IVL_SIM
        $fsdbDumpfile("motion_v5_16bit_top_regression.fsdb");
`endif
`ifndef IVL_SIM
        $fsdbDumpvars(0, motion_v5_16bit_top_regression_tb);
`endif
`endif
        $dumpfile("motion_v5_16bit_top_regression.vcd");
        $dumpvars(0, motion_v5_16bit_top_regression_tb);

        clock = 1'b0;
        start = 1'b0;

        // =========================================================================
        // TEST 1: Direct Fixture (ref.txt & search.txt) at 520 MHz
        // =========================================================================
        $display("=== TEST 1: Direct Fixture (ref.txt & search.txt) at 520 MHz ===");
        $readmemh("ref.txt", memR_u.Rmem);
        $readmemh("search.txt", memS_u.Smem);

        @(posedge clock); #0.02;
        start = 1'b1;
        t_start = $realtime;

        for (i = 0; i < 4112; i = i + 1) begin
            if (dut.ctl_u.count >= 256 && dut.ctl_u.count <= 272) begin
                $display("  [T1] count=%4d t=%0.4f ns | PEready=%04h newDist_comp=%04h BestDist=%04h Vec=(%01h,%01h) out=(%01h,%01h) newBest=%b",
                    dut.ctl_u.count, $realtime, dut.PEready, dut.comp_u.newDist, BestDist,
                    dut.VectorX, dut.VectorY, motionX, motionY, dut.comp_u.newBest);
            end
            if (dut.comp_u.newBest == 1'b1) begin
                t_match = $realtime;
                $display("  [T1 newBest] count=%4d t=%0.4f ns -> newDist=%04h at VectorX=%01h VectorY=%01h",
                    dut.ctl_u.count, $realtime, dut.comp_u.newDist, dut.VectorX, dut.VectorY);
            end
            if (completed == 1'b1 && dut.ctl_u.count == 13'd4111) begin
                t_complete = $realtime;
            end
            @(posedge clock); #0.02;
        end

        decode_motion(motionX, motionY, x, y);
        $display("  [T1 RESULT] BestDist=%04h (%0d), motionX=%01h (%0d), motionY=%01h (%0d), elapsed_complete=%0.4f ns",
            BestDist, BestDist, motionX, x, motionY, y, t_complete - t_start);

        if (BestDist !== 16'h0000 || motionX !== 4'h7 || motionY !== 4'h8) $fatal(1, "V5 T1 reference fixture mismatch");
        $display("V5_TOP_REGRESSION_T1_PASS");
        start = 1'b0;
        @(posedge clock); #0.02;
        @(posedge clock); #0.02;

        // =========================================================================
        // TEST 2: Perturbed Non-Zero SAD Match at (-2, -3) [motionX=4'hE, motionY=4'hD]
        // =========================================================================
        $display("\n=== TEST 2: Perturbed Imperfect Match (SAD=3) at (-2, -3) ===");
        for (i = 0; i < 1024; i = i + 1) begin
            Smem[i] = ((i * 73 + 41) ^ (i >> 2)) & 8'hFF;
        end
        Expected_motionX = -2;
        Expected_motionY = -3;
        for (i = 0; i < 256; i = i + 1) begin
            Rmem[i] = Smem[32*8 + 8 + (((i/16) + Expected_motionY)*32) + ((i%16) + Expected_motionX)];
        end
        // Perturb pixel 0 by +3 (wrapping safely away from 255)
        if (Rmem[0] <= 8'd252) Rmem[0] = Rmem[0] + 8'd3;
        else Rmem[0] = Rmem[0] - 8'd3;

        for (i = 0; i < 256; i = i + 1) memR_u.Rmem[i] = Rmem[i];
        for (i = 0; i < 1024; i = i + 1) memS_u.Smem[i] = Smem[i];

        start = 1'b1;
        t_start = $realtime;
        for (i = 0; i < 4112; i = i + 1) begin
            if (dut.comp_u.newBest == 1'b1) begin
                $display("  [T2 newBest] count=%4d t=%0.4f ns -> newDist=%04h (%0d) at VectorX=%01h VectorY=%01h",
                    dut.ctl_u.count, $realtime - t_start, dut.comp_u.newDist, dut.comp_u.newDist, dut.VectorX, dut.VectorY);
            end
            if (completed == 1'b1 && dut.ctl_u.count == 13'd4111) begin
                t_complete = $realtime;
            end
            @(posedge clock); #0.02;
        end
        decode_motion(motionX, motionY, x, y);
        $display("  [T2 RESULT] BestDist=%04h (%0d), motionX=%01h (%0d), motionY=%01h (%0d), Expected=(%0d, %0d), elapsed=%0.4f ns",
            BestDist, BestDist, motionX, x, motionY, y, Expected_motionX, Expected_motionY, t_complete - t_start);

        if (BestDist !== 16'h0003 || motionX !== 4'hE || motionY !== 4'hD) $fatal(1, "V5 T2 nonzero SAD mismatch");
        $display("V5_TOP_REGRESSION_T2_PASS");

        start = 1'b0;
        @(posedge clock); #0.02;
        @(posedge clock); #0.02;

        // =========================================================================
        // TEST 3: Final Boundary Candidate (+7, +7) at count=4111 (completed=1)
        // =========================================================================
        $display("\n=== TEST 3: Upper Boundary Candidate (+7, +7) at count=4111 ===");
        Expected_motionX = 7;
        Expected_motionY = 7;
        for (i = 0; i < 256; i = i + 1) begin
            Rmem[i] = Smem[32*8 + 8 + (((i/16) + Expected_motionY)*32) + ((i%16) + Expected_motionX)];
        end
        for (i = 0; i < 256; i = i + 1) memR_u.Rmem[i] = Rmem[i];

        start = 1'b1;
        t_start = $realtime;
        for (i = 0; i < 4113; i = i + 1) begin
            if (dut.comp_u.newBest == 1'b1) begin
                $display("  [T3 newBest] count=%4d t=%0.4f ns -> newDist=%04h (%0d) at VectorX=%01h VectorY=%01h completed=%b",
                    dut.ctl_u.count, $realtime - t_start, dut.comp_u.newDist, dut.comp_u.newDist, dut.VectorX, dut.VectorY, completed);
            end
            @(posedge clock); #0.02;
        end
        decode_motion(motionX, motionY, x, y);
        $display("  [T3 RESULT] BestDist=%04h (%0d), motionX=%01h (%0d), motionY=%01h (%0d), Expected=(%0d, %0d)",
            BestDist, BestDist, motionX, x, motionY, y, Expected_motionX, Expected_motionY);

        if (BestDist !== 16'h0000 || motionX !== 4'h7 || motionY !== 4'h7) $fatal(1, "V5 T3 last-boundary mismatch");
        $display("V5_TOP_REGRESSION_T3_PASS");
        $display("V5_TOP_REGRESSION_PASS 3/3");
        $finish;
    end
endmodule
