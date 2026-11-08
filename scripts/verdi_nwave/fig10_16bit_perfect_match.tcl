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
wvScrollUp -win $w 10
catch {verdiDockWidgetMaximize -dock windowDock_nWave_2}
