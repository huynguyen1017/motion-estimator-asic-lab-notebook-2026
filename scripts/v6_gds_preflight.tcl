# Read-only placement and source-configuration audit for the existing routed checkpoint.
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
set target [get_cells -hierarchical {ctl_u/count_reg[0]}]
if {[sizeof_collection $target] != 1} {error "Controller register not found uniquely"}
foreach attr {physical_status is_placed origin bbox} {
    puts "PLACEMENT_ATTR_$attr=[get_attribute $target $attr]"
}
set unplaced [get_flat_cells -filter {physical_status==unplaced}]
puts "UNPLACED_FLAT_CELL_COUNT=[sizeof_collection $unplaced]"
if {[sizeof_collection $unplaced] != 0} {error "Found unplaced standard cells"}
set check [catch {check_legality} msg]
puts "LEGALITY_COMMAND_RC=$check RESULT=$msg"
if {$check != 0} {error "Placement legality could not run"}
puts "PLACEMENT_PREFLIGHT_PASSED"
exit
