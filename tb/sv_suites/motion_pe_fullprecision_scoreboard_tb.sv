`timescale 1ns/100fs
// Independent ENGR 852 deterministic VCS scoreboard. Original top.v unchanged.
// Checks 16 blocks x 256 pixel pairs for both PE and PEend with a 16-bit SAD reference.
// Seeded stress + boundary patterns. Fatal exit on ANY mismatch.
module motion_pe_fullprecision_scoreboard_tb;
    reg clock = 1'b0;
    always #0.9615 clock = ~clock;
    reg [7:0] R=0, S1=0, S2=0;
    reg S1S2mux=1, newDist=1;
    wire [7:0] PE_acc, PEend_acc, Rpipe;
    PE pe_dut(clock, R, S1, S2, S1S2mux, newDist, PE_acc, Rpipe);
    PEend peend_dut(clock, R, S1, S2, S1S2mux, newDist, PEend_acc);
    reg [31:0] rng = 32'h13579bdf;
    integer full_sad=0, expected_sat=0, value=0, checks=0, failures=0;
    integer saturated_samples=0, trials=0, tr=0, px=0, seed=271828;
    reg [7:0] selected_s;
    initial begin
        if ($value$plusargs("SEED=%d", seed)) begin end
        rng=seed;
        $display("MOTION_SAD_SCOREBOARD_START seed=%0d cycles=16x256",seed);
        // Settle the uninitialized accumulator before the first scored edge.
        newDist=0; #0.02; newDist=1;
        for (tr=0; tr<16; tr=tr+1) begin
            full_sad=0;
            expected_sat=0;
            for(px=0; px<256; px=px+1) begin
                @(negedge clock); #0.02;
                newDist = (px==0);
                // Use deterministic PRNG so every run can be reproduced.
                rng = rng * 32'd1664525 + 32'd1013904223;
                R = rng[31:24];
                rng = rng * 32'd1664525 + 32'd1013904223;
                S1 = rng[23:16];
                rng = rng * 32'd1664525 + 32'd1013904223;
                S2 = rng[15:8];
                S1S2mux = rng[5];
                // Three explicit boundary patterns before randomized trials.
                if (tr==0) begin R=8'd0; S1=8'd0; S2=8'd0; end
                if (tr==1) begin R=8'd255; S1=0; S2=0; end
                if (tr==2) begin R=8'd255; S1=8'd254; S2=8'd254; end
                selected_s = S1S2mux ? S1 : S2;
                if (R >= selected_s) value = R-selected_s;
                else value = selected_s-R;
                full_sad = full_sad + value;
                if (full_sad > 255) expected_sat = 255;
                else expected_sat = full_sad;
                @(posedge clock); #0.02;
                checks=checks+1;
                if (full_sad > 255) saturated_samples=saturated_samples+1;
                if ((PE_acc !== expected_sat[7:0]) ||
                    (PEend_acc !== expected_sat[7:0])) begin
                    failures=failures+1;
                    $display("FAIL seed=%0d block=%0d pixel=%0d full=%0d expected=%0d PE=%h PEend=%h",
                             seed,tr,px,full_sad,expected_sat,PE_acc,PEend_acc);
                    if (failures>10) $fatal(1,"Too many mismatches");
                end
            end
            trials=trials+1;
            $display("BLOCK_SUMMARY seed=%0d block=%0d full_SAD=%0d saturated=%0d",seed,tr,full_sad,expected_sat);
        end
        $display("MOTION_SCOREBOARD_RESULT seed=%0d blocks=%0d samples=%0d pe_comparisons=%0d failures=%0d saturated_samples=%0d",
                 seed,trials,checks,checks*2,failures,saturated_samples);
        if (failures) $fatal(1,"MOTION_SCOREBOARD_FAIL");
        $display("MOTION_SCOREBOARD_PASS");
        $finish;
    end
endmodule
