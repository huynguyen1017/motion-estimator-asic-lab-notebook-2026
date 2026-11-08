`timescale 1ns/100fs
module motion_regression_tb;
  reg clock=0, start=0;
  wire [15:0] BestDist;
  wire [3:0] motionX, motionY;
  wire [7:0] AddressR, R, S1, S2;
  wire [9:0] AddressS1, AddressS2;
  wire completed;
  integer case_id=0, passes=0, i, j, x, y, xx, yy, cycles;
  integer sad, delta, golden_sad, golden_x, golden_y;
  reg [31:0] random_state=32'h8522026;
  reg [15:0] saved_sad;
  reg [3:0] saved_x, saved_y;
  top dut(clock,start,BestDist,motionX,motionY,AddressR,AddressS1,AddressS2,R,S1,S2,completed);
  ROM_R memR(clock,AddressR,R);
  ROM_S memS(clock,AddressS1,AddressS2,S1,S2);
  always #0.9615 clock=~clock;

  // Same deterministic stimulus under Icarus and VCS.
  function automatic [7:0] pixel;
    begin
      random_state=random_state ^ (random_state << 13);
      random_state=random_state ^ (random_state >> 17);
      random_state=random_state ^ (random_state << 5);
      pixel=random_state[7:0];
    end
  endfunction

  // Independent full-search reference, all 256 candidates and 256 pixels.
  // Strict less-than preserves the first candidate in row-major tie order.
  task reference_model;
    begin
      golden_sad=65536; golden_x=0; golden_y=0;
      for (yy=0; yy<16; yy=yy+1)
        for (xx=0; xx<16; xx=xx+1) begin
          sad=0;
          for (j=0;j<256;j=j+1) begin
            delta=integer'(memR.Rmem[j])-integer'(memS.Smem[(yy+j/16)*32+xx+j%16]);
            sad=sad+((delta<0)?-delta:delta);
          end
          if (sad<golden_sad) begin
            golden_sad=sad; golden_x=xx-8; golden_y=yy-8;
          end
        end
    end
  endtask

  task reset_search;
    begin
      @(negedge clock); start=0;
      repeat(3) @(negedge clock);
      if (dut.ctl_u.count !== 0 || completed !== 0 || BestDist !== 16'hffff)
        $fatal(1,"RESET_FAIL case=%0d",case_id);
    end
  endtask

  task run_case;
    begin
      reference_model;
      start=1; cycles=0;
      while (completed !== 1 && cycles<4115) begin
        @(posedge clock); #0.02; cycles=cycles+1;
      end
      if (cycles != 4111) $fatal(1,"COMPLETION_CYCLE_FAIL case=%0d cycles=%0d",case_id,cycles);
      // The final candidate commits on the edge following count=4111.
      @(posedge clock); #0.02;
      if (BestDist !== golden_sad[15:0] || motionX !== golden_x[3:0] || motionY !== golden_y[3:0])
        $fatal(1,"GOLDEN_FAIL case=%0d got=%h,%h,%h expected=%h,%h,%h",case_id,BestDist,motionX,motionY,golden_sad[15:0],golden_x[3:0],golden_y[3:0]);
      saved_sad=BestDist; saved_x=motionX; saved_y=motionY;
      repeat(12) begin
        @(posedge clock); #0.02;
        if (BestDist !== saved_sad || motionX !== saved_x || motionY !== saved_y || completed !== 1)
          $fatal(1,"HOLD_FAIL case=%0d",case_id);
      end
      passes=passes+1;
      $display("CASE_PASS id=%0d SAD=%04h vector=(%0d,%0d) cycles=%0d golden_candidates=256 hold_cycles=12",case_id,BestDist,golden_x,golden_y,cycles);
    end
  endtask

  initial begin
    $dumpfile("motion_regression.vcd");
    $dumpvars(1,motion_regression_tb);
    $dumpvars(0,dut.ctl_u);
    $dumpvars(0,dut.comp_u);
    $dumpvars(0,dut.completed_delayed,dut.qualified_ready);
    reset_search;
    case_id=1;
    $readmemh("ref.txt",memR.Rmem); $readmemh("search.txt",memS.Smem);
    run_case;
    reset_search; case_id=2;
    for(i=0;i<256;i=i+1) memR.Rmem[i]=0;
    for(i=0;i<1024;i=i+1) memS.Smem[i]=255;
    run_case;
    reset_search; case_id=3;
    for(i=0;i<256;i=i+1) memR.Rmem[i]=37;
    for(i=0;i<1024;i=i+1) memS.Smem[i]=37;
    run_case;
    // Exact match at each extreme coordinate, then perturbed interior match.
    for(case_id=4;case_id<=8;case_id=case_id+1) begin
      reset_search;
      for(i=0;i<1024;i=i+1) memS.Smem[i]=pixel();
      case(case_id)
        4: begin x=0;y=0;end
        5: begin x=15;y=0;end
        6: begin x=0;y=15;end
        7: begin x=15;y=15;end
        8: begin x=6;y=5;end
      endcase
      for(i=0;i<256;i=i+1) memR.Rmem[i]=memS.Smem[(y+i/16)*32+x+i%16];
      if(case_id==8) memR.Rmem[0]=(memR.Rmem[0]<=252)?memR.Rmem[0]+3:memR.Rmem[0]-3;
      run_case;
    end
    // Unrelated images exercise nonzero minima and comparison ordering.
    for(case_id=9;case_id<=14;case_id=case_id+1) begin
      reset_search;
      for(i=0;i<1024;i=i+1) memS.Smem[i]=pixel();
      for(i=0;i<256;i=i+1) memR.Rmem[i]=pixel();
      if(case_id==14) begin
        start=1; repeat(97) @(negedge clock); reset_search;
      end
      run_case;
    end
    $display("REGRESSION_PASS cases=%0d candidate_scores=%0d pixel_differences=%0d",passes,passes*256,passes*256*256);
    $finish;
  end
  initial begin #200000; $fatal(1,"WATCHDOG_TIMEOUT"); end
endmodule
