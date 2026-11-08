set search_path [list ./common/liberty .]
set link_path [list * ./common/liberty/saed14rvt_tt0p8v25c.db]
read_verilog ./results/top.v
current_design top
link_design
read_sdc ./results/top_primetime_TYPICAL.sdc
read_parasitics ./results/top.spef.nomTLU_25.spef
update_timing
redirect -file ./pt_reports/v5_TYPICAL_v2_report_setup.rpt { report_timing -delay_type max -max_paths 30 -slack_lesser_than 100 -input_pins -nets }
redirect -file ./pt_reports/v5_TYPICAL_v2_report_hold.rpt { report_timing -delay_type min -max_paths 30 -slack_lesser_than 100 -input_pins -nets }
redirect -file ./pt_reports/v5_TYPICAL_v2_report_global.rpt { report_global_timing }
redirect -file ./pt_reports/v5_TYPICAL_v2_report_constraints.rpt { report_constraint -all_violators }
redirect -file ./pt_reports/v5_TYPICAL_v2_report_check_timing.rpt { check_timing -verbose }
puts "V5_PVT_REPORTS_WRITTEN TYPICAL"
exit
