#!/bin/bash
export LM_LICENSE_FILE=/packages/synopsys/license/synopsys.lic
export SNPSLMD_LICENSE_FILE=/packages/synopsys/license/synopsys.lic
export VERDI_HOME=/packages/synopsys/verdi/W-2024.09-1
export PATH=$VERDI_HOME/bin:$PATH

pkill -f "Xvfb :94" 2>/dev/null || true
Xvfb :94 -screen 0 1920x1080x24 -nolisten tcp >/dev/null 2>&1 &
XVFB_PID=$!
sleep 2
export DISPLAY=:94

# Helper function to run verdi/nWave script and screenshot
run_nwave_shot() {
  local tcl_file=$1
  local out_png=$2
  verdi -play "$tcl_file" > "${tcl_file}.log" 2>&1 &
  local vpid=$!
  sleep 14
  gnome-screenshot -f "$out_png"
  kill -9 $vpid 2>/dev/null || true
  pkill -f "verdi" 2>/dev/null || true
  pkill -f "nWave" 2>/dev/null || true
  sleep 2
}

cat << "TCL1" > fig7_orig8bit_row1.tcl
verdiWindowResize -win $_Verdi_1 "0" "0" "1900" "1040"
set w [wvCreateWindow]
wvOpenFile -win $w {motion_v3_all_saturated.fsdb}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/clock}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/start}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/ctl_u/count[12:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/S1S2mux[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/newDist[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/CompStart}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/PEready[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/VectorX[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/VectorY[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressR[7:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressS1[9:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressS2[9:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/comp_u/newBest}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/BestDist[7:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/motionX[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/motionY[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/completed}
puts "RANGE=[wvGetFileTimeRange -win $w] UNIT=[wvGetWindowTimeUnit -win $w]"
wvZoom -win $w 4800000 5260000
TCL1

cat << "TCL2" > fig8_orig8bit_complete.tcl
verdiWindowResize -win $_Verdi_1 "0" "0" "1900" "1040"
set w [wvCreateWindow]
wvOpenFile -win $w {motion_v3_all_saturated.fsdb}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/clock}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/start}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/ctl_u/count[12:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/S1S2mux[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/newDist[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/CompStart}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/PEready[15:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/VectorX[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/VectorY[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressR[7:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressS1[9:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/AddressS2[9:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/dut/comp_u/newBest}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/BestDist[7:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/motionX[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/motionY[3:0]}
wvAddSignal -win $w {/motion_v3_all_saturated_tb/completed}
wvZoom -win $w 78720000 79179725
TCL2

cat << "TCL3" > fig9_16bit_sat_row1.tcl
verdiWindowResize -win $_Verdi_1 "0" "0" "1900" "1040"
set w [wvCreateWindow]
wvOpenFile -win $w {motion_v3_hold.fsdb}
wvAddSignal -win $w {/motion_v3_hold_tb/clock}
wvAddSignal -win $w {/motion_v3_hold_tb/start}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/ctl_u/count[12:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/S1S2mux[15:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/newDist[15:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/CompStart}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/PEready[15:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/VectorX[3:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/VectorY[3:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/AddressR[7:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/AddressS1[9:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/AddressS2[9:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/dut/comp_u/newBest}
wvAddSignal -win $w {/motion_v3_hold_tb/BestDist[15:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/motionX[3:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/motionY[3:0]}
wvAddSignal -win $w {/motion_v3_hold_tb/completed}
wvZoom -win $w 4800000 5260000
TCL3

cat << "TCL4" > fig10_16bit_perfect_match.tcl
verdiWindowResize -win $_Verdi_1 "0" "0" "1900" "1040"
set w [wvCreateWindow]
wvOpenFile -win $w {motion_v5_16bit_top_regression.fsdb}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/clock}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/start}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/ctl_u/count[12:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/S1S2mux[15:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/newDist[15:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/CompStart}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/PEready[15:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/VectorX[3:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/VectorY[3:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/AddressR[7:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/AddressS1[9:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/AddressS2[9:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/dut/comp_u/newBest}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/BestDist[15:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/motionX[3:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/motionY[3:0]}
wvAddSignal -win $w {/motion_v5_16bit_top_regression_tb/completed}
wvZoom -win $w 4900000 5320000
TCL4

run_nwave_shot fig7_orig8bit_row1.tcl raw_fig7.png
run_nwave_shot fig8_orig8bit_complete.tcl raw_fig8.png
run_nwave_shot fig9_16bit_sat_row1.tcl raw_fig9.png
run_nwave_shot fig10_16bit_perfect_match.tcl raw_fig10.png

kill -9 $XVFB_PID 2>/dev/null || true
ls -lh raw_fig*.png
