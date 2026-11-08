set search_path [list ./common/liberty .]
set link_path [list * ./common/liberty/saed14rvt_ff0p88v125c.db]
read_verilog ./results/top.v
current_design top
link_design
read_sdc ./results/top_primetime_FAST.sdc
read_parasitics ./results/top.spef.minTLU_125.spef
update_timing
redirect -file ./pt_reports/v5_FAST_v2_report_setup.rpt { report_timing -delay_type max -max_paths 30 -slack_lesser_than 100 -input_pins -nets }
redirect -file ./pt_reports/v5_FAST_v2_report_hold.rpt { report_timing -delay_type min -max_paths 30 -slack_lesser_than 100 -input_pins -nets }
redirect -file ./pt_reports/v5_FAST_v2_report_global.rpt { report_global_timing }
redirect -file ./pt_reports/v5_FAST_v2_report_constraints.rpt { report_constraint -all_violators }
redirect -file ./pt_reports/v5_FAST_v2_report_check_timing.rpt { check_timing -verbose }
puts "V5_PVT_REPORTS_WRITTEN FAST"
puts "V5_ECO_FIX_START"
get_lib_cells */SAEDRVT14_BUF_ECO*
fix_eco_timing -type hold -pba_mode exhaustive -buffer_list {SAEDRVT14_BUF_ECO_1 SAEDRVT14_BUF_ECO_2 SAEDRVT14_BUF_ECO_3}
write_changes -format icc2tcl -output ./results/v5_FAST_hold_eco.tcl
puts "V5_ECO_FIX_SCRIPT_COMPLETE"
exit
