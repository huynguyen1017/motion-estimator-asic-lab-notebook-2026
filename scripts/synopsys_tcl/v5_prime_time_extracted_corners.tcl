set search_path [list ./common/liberty .]
set link_path [list * ./common/liberty/saed14rvt_ff0p88v125c.db ./common/liberty/saed14rvt_ss0p72vm40c.db ./common/liberty/saed14rvt_tt0p8v25c.db]
read_verilog ./results/top.v
current_design top
link_design
read_sdc ./results/top_primetime_2p1.sdc
report_clocks
check_timing -verbose
foreach {label spef} {minTLU_125 top.spef.minTLU_125.spef nomTLU_25 top.spef.nomTLU_25.spef maxTLU_-40 top.spef.maxTLU_-40.spef} {
  remove_annotated_parasitics
  read_parasitics ./results/$spef
  update_timing
  redirect -file ./pt_reports/v5_${label}_check_timing.rpt { check_timing -verbose }
  redirect -file ./pt_reports/v5_${label}_setup.rpt { report_timing -delay_type max -max_paths 20 -input_pins -nets }
  redirect -file ./pt_reports/v5_${label}_hold.rpt { report_timing -delay_type min -max_paths 20 -input_pins -nets }
  redirect -file ./pt_reports/v5_${label}_constraint.rpt { report_constraint -all_violators }
  redirect -file ./pt_reports/v5_${label}_global.rpt { report_global_timing }
  puts "V5_PRIMETIME_CORNER_DONE $label"
}
puts "V5_PRIMETIME_EXTRACTED_TIMING_REPORTS_WRITTEN"
exit
