################################################################################
#
# Design name:  top
#
# Created by fc write_sdc on Sat Nov  7 10:25:20 2026
#
################################################################################

set sdc_version 2.2
set_units -time ns -resistance MOhm -capacitance fF -voltage V -current uA

################################################################################
#
# Units
# time_unit               : 1e-09
# resistance_unit         : 1000000
# capacitive_load_unit    : 1e-15
# voltage_unit            : 1
# current_unit            : 1e-06
# power_unit              : 1e-12
################################################################################


# Mode: FUNC
# Corner: Typical
# Scenario: FUNC_Typical

# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   1
create_clock -name clock -period 1.923 -waveform {0 0.9615} [get_ports {clock}]
set_propagated_clock [get_clocks {clock}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/setup/mcmm_setup.tcl, \
#   line 45
set_operating_conditions -library saed14rvt_tt0p8v25c.db:saed14rvt_tt0p8v25c \
    -analysis_type on_chip_variation tt0p8v25c
# Warning: Libcell power domain derates are skipped!

# Set latency for io paths.
# -origin useful_skew
set_clock_latency 0.0463676 [get_clocks {clock}]
# Set propagated on clock sources to avoid removing latency for IO paths.
set_propagated_clock  [get_ports {clock}]
set_clock_uncertainty 0.2 [get_clocks {clock}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {start}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[15]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[14]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[13]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[12]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[11]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[10]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[9]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[8]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[7]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[6]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[5]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[4]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {BestDist[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionX[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionX[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionX[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionX[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionY[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionY[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionY[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {motionY[0]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[7]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[6]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[5]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[4]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[3]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[2]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[1]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressR[0]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[9]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[8]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[7]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[6]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[5]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[4]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[3]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[2]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[1]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS1[0]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[9]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[8]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[7]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[6]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[5]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[4]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[3]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[2]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[1]}]
# /home/926784856/ENGR852_Project/16_v3b_final_asic_fc/common/sdc/top.sdc, line \
#   4
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {AddressS2[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[7]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[6]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[5]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[4]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {R[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[7]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[6]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[5]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[4]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S1[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[7]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[6]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[5]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[4]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[3]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[2]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[1]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_input_delay -clock [get_clocks {clock}] 0.5 [get_ports {S2[0]}]
# /home/926784856/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/v9_closure/run_v9_route_and_eco.tcl, \
#   line 35
set_output_delay -clock [get_clocks {clock}] 0.5 [get_ports {completed}]
