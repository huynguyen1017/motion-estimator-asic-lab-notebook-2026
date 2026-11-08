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
wvScrollUp -win $w 10
catch {verdiDockWidgetMaximize -dock windowDock_nWave_2}
