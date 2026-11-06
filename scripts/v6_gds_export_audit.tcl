# Re-export GDS from an immutable routed checkpoint after strict preflight.
source -echo ./setup/fc_common_setup.tcl
source -echo ./setup/fc_flow_setup.tcl
foreach required {DESIGN_NAME DESIGN_LIBRARY RESULTS_PATH GDS_MAP_FILE GDS_FILE} {
    if {![info exists $required]} {error "Missing required variable: $required"}
}
foreach required_file [concat [list $GDS_MAP_FILE] $GDS_FILE] {
    if {![file isfile $required_file]} {error "Missing technology input: $required_file"}
}
open_lib ${RESULTS_PATH}/${DESIGN_LIBRARY}
open_block ${DESIGN_NAME}/signoff_v5
set unplaced [get_flat_cells -filter {physical_status==unplaced}]
puts "UNPLACED_FLAT_CELL_COUNT=[sizeof_collection $unplaced]"
if {[sizeof_collection $unplaced] != 0} {error "Refusing GDS export: unplaced cells"}
set rc [catch {
    write_gds -design ${DESIGN_NAME} -layer_map ${GDS_MAP_FILE} \
      -keep_data_type -fill include -output_pin all \
      -merge_files ${GDS_FILE} -long_names -lib_cell_view frame \
      ./results/v6_signoff_v5_reexport.gds
} output]
puts "GDS_EXPORT_COMMAND_RC=$rc MESSAGE=$output"
if {$rc != 0} {error "GDS export failed"}
puts "GDS_REEXPORT_COMPLETED"
exit
