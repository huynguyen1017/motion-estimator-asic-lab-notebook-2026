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
wvScrollUp -win $w 10
catch {verdiDockWidgetMaximize -dock windowDock_nWave_2}
