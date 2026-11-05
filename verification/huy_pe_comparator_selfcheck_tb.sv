`timescale 1ns/100fs
// Independent ENGR852 self-check: 520 MHz PE saturation and comparator selection.
// The DUT modules below are from the unchanged professor-supplied top.v.
// Pass/fail uses strict four-state comparisons; a failure exits with $fatal.
module huy_pe_comparator_selfcheck_tb;
  reg clock = 0;
  always #0.9615 clock = ~clock;

  reg [7:0] R = 0, S1 = 0, S2 = 0;
  reg S1S2mux = 1, newDist = 1;
  wire [7:0] PE_acc, PEend_acc, Rpipe;
  PE pe_u(clock, R, S1, S2, S1S2mux, newDist, PE_acc, Rpipe);
  PEend peend_u(clock, R, S1, S2, S1S2mux, newDist, PEend_acc);

  reg CompStart = 0;
  reg [127:0] PEout = 0;
  reg [15:0] PEready = 0;
  reg [3:0] vectorX = 0, vectorY = 0;
  wire [7:0] BestDist;
  wire [3:0] motionX, motionY;
  Comparator comp_u(clock, CompStart, PEout, PEready, vectorX, vectorY,
                    BestDist, motionX, motionY);

  integer checks = 0;
  integer failures = 0;

  task automatic check_pe(input [7:0] expected, input string test_name);
    begin
      @(posedge clock); #0.02;
      checks = checks + 1;
      if (PE_acc !== expected || PEend_acc !== expected) begin
        failures = failures + 1;
        $display("FAIL PE %-30s PE=%h PEend=%h expected=%h",
                 test_name, PE_acc, PEend_acc, expected);
      end else
        $display("PASS PE %-30s PE=%h PEend=%h",
                 test_name, PE_acc, PEend_acc);
    end
  endtask

  task automatic check_comp(input [7:0] want_dist,
                            input [3:0] want_x, want_y,
                            input string test_name);
    begin
      @(posedge clock); #0.02;
      checks = checks + 1;
      if (BestDist !== want_dist ||
          motionX !== want_x || motionY !== want_y) begin
        failures = failures + 1;
        $display("FAIL COMP %-25s got=%h (%h,%h) expected=%h (%h,%h)",
                 test_name, BestDist, motionX, motionY,
                 want_dist, want_x, want_y);
      end else
        $display("PASS COMP %-25s got=%h (%h,%h)",
                 test_name, BestDist, motionX, motionY);
    end
  endtask

  initial begin
    $display("HUY_INDEPENDENT_VCS_520MHZ_PE_COMPARATOR_TEST_BEGIN");
    // Force a defined newDist transition because PE has no reset port.
    newDist=0; #0.02; newDist=1; #0.02;

    check_pe(8'd0, "newDist reset: zero difference");

    @(negedge clock); #0.02;
    R=8'd255; S1=8'd254; newDist=1;
    check_pe(8'd1, "newDist begins with SAD=1");

    @(negedge clock); #0.02;
    R=8'd255; S1=8'd0; newDist=0;
    check_pe(8'hff, "1+255=256 saturates to 255");
    $display("REFERENCE_FULL_PRECISION_SAD=256; DUT_SATURATED_SAD=255");

    @(negedge clock); #0.02;
    R=8'd0; S1=8'd0;
    check_pe(8'hff, "saturation persists after +0");

    @(negedge clock); #0.02;
    newDist=1; R=0; S1=0;
    check_pe(8'd0, "newDist clears saturation");

    @(negedge clock); #0.02;
    newDist=0; R=0; S1=3;
    check_pe(8'd3, "absolute diff when R < S1");

    @(negedge clock); #0.02;
    R=8; S1=99; S2=8; S1S2mux=0;
    check_pe(8'd3, "S2 mux path: no added SAD");

    @(negedge clock); #0.02;
    PEready=16'h0001; PEout[7:0]=8'd5;
    vectorX=4'he; vectorY=4'hd; CompStart=1;
    check_comp(8'd5, 4'he, 4'hd, "first winner: (-2,-3)");

    @(negedge clock); #0.02;
    PEout[7:0]=8'd5; vectorX=4'd3; vectorY=4'd4;
    check_comp(8'd5, 4'he, 4'hd, "equal-SAD tie keeps first");

    @(negedge clock); #0.02;
    PEout[7:0]=8'd3;
    check_comp(8'd3, 4'd3, 4'd4, "strictly smaller wins");

    @(negedge clock); #0.02;
    CompStart=0; PEready=0;
    @(posedge clock); #0.02;
    checks=checks+1;
    if (BestDist !== 8'hff) begin
      failures=failures+1;
      $display("FAIL COMP reset BestDist=%h", BestDist);
    end else
      $display("PASS COMP reset BestDist=ff");

    @(negedge clock); #0.02;
    CompStart=1; PEready=16'h0001; PEout[7:0]=8'hff;
    vectorX=4'd7; vectorY=4'd7;
    check_comp(8'hff, 4'd3, 4'd4, "SAD=255 cannot beat reset ff");
    $display("OBSERVATION all-saturated candidates cannot update motionX/Y");

    if (failures != 0)
      $fatal(1, "HUY_INDEPENDENT_TEST_FAIL checks=%0d failures=%0d",
             checks, failures);
    $display("HUY_INDEPENDENT_TEST_PASS checks=%0d failures=%0d",
             checks, failures);
    $finish;
  end
endmodule
