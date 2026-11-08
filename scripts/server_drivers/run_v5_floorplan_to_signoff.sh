#!/usr/bin/env bash
set -u
set -o pipefail
umask 077
SOURCE="$HOME/ENGR852_Project/16_v3b_final_asic_fc"
WORK="$HOME/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix"
stamp() { printf '[%s] %s\n' "$(date '+%F %T %Z')" "$*"; }
fail() { stamp "STOPPED: $*"; exit 1; }
mkdir -p "$WORK" || exit 1
stamp "CLONING_ORIGINAL_V3B_TO_PRESERVED_V5"
rsync -a "$SOURCE/" "$WORK/" || fail "rsync clone"
cd "$WORK" || fail "cd"
mkdir -p v5_stage_logs pt_reports pt_session
rm -rf "$WORK/results/write_floorplan_files"
python3 - <<'PY'
from pathlib import Path
d=Path('scripts')
remap={
'manual_floorplan_creation.tcl':[('manual_floorplan','manual_floorplan_v5'),('-core_utilization 0.6','-core_utilization 0.35')],
'place_opt.tcl':[('manual_floorplan','manual_floorplan_v5'),('place_opt','place_opt_v5')],
'clock_opt.tcl':[('place_opt','place_opt_v5'),('clock_opt','clock_opt_v5')],
'route_opt.tcl':[('clock_opt','clock_opt_v5'),('route_opt','route_opt_v5')],
'signoff.tcl':[('route_opt','route_opt_v5'),('signoff','signoff_v5')]}
for filename,changes in remap.items():
 p=d/filename;s=p.read_text()
 for old,new in changes:
  if old.startswith('-core'):
   assert old in s
   s=s.replace(old,new,1)
  else:
   token='${DESIGN_NAME}/'+old
   assert token in s,(filename,token)
   s=s.replace(token,'${DESIGN_NAME}/'+new)
 p.write_text(s)
print("V5_BLOCKS_CREATED_FLOORPLAN_UTILIZATION_035",flush=True)
PY
test "$?" -eq 0 || fail "TCL generation"
sha256sum common/rtl/verilog/top.v common/sdc/top.sdc > v5_stage_logs/input_checksums.sha256
stamp "CLONE_OK"
do_fc() {
 local stage="$1";local filename="$2";local log="v5_stage_logs/${stage}.log"
 stamp "BEGIN ${stage}"
 timeout 10800 tcsh -c "source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/${filename}" >"$log" 2>&1
 local result=$?
 stamp "END ${stage} exit=${result}"
 test "$result" -eq 0 || fail "$stage exit=$result"
 if grep -En '^Error:|^Fatal:|PLACE-004|PLACE-006|CMD-081|OPT-907' "$log" > "v5_stage_logs/${stage}_errors.txt";then
  tail -n 15 "v5_stage_logs/${stage}_errors.txt"
  fail "$stage tool errors"
 fi
 case "$stage" in
 floorplan) test -d results/top.dlib/top/design_label.manual_floorplan_v5 || fail "missing floorplan block" ;;
 placement) test -d results/top.dlib/top/design_label.place_opt_v5 || fail "missing placement block" ;;
 cts) test -d results/top.dlib/top/design_label.clock_opt_v5 || fail "missing CTS block" ;;
 route) test -d results/top.dlib/top/design_label.route_opt_v5 || fail "missing route block" ;;
 signoff) test -s results/top.spef && test -s results/top.v && test -s results/top.gds || fail "missing final exports" ;;
 esac
 stamp "CHECKPOINT_PASS ${stage}"
}
do_fc floorplan manual_floorplan_creation.tcl
do_fc placement place_opt.tcl
do_fc cts clock_opt.tcl
do_fc route route_opt.tcl
do_fc signoff signoff.tcl
stamp "SIGNOFF_EXPORTS_AVAILABLE_PRIMETIME_STARTING"
cat > scripts/v5_prime_time_top.tcl <<'TCL'
set search_path [list ./common/liberty .]
set link_path [list * ./common/liberty/saed14rvt_ff0p88v125c.db ./common/liberty/saed14rvt_ss0p72vm40c.db ./common/liberty/saed14rvt_tt0p8v25c.db]
read_verilog ./results/top.v
current_design top
link_design
read_sdc ./results/top.sdc
read_parasitics ./results/top.spef
update_timing
redirect -file ./pt_reports/V5_post_layout_timing_setup.rpt {
 report_timing -delay_type max -max_paths 30 -input_pins -nets
}
redirect -file ./pt_reports/V5_post_layout_timing_hold.rpt {
 report_timing -delay_type min -max_paths 30 -input_pins -nets
}
redirect -file ./pt_reports/V5_post_layout_constraint_violations.rpt {
 report_constraint -all_violators
}
exit
TCL
timeout 10800 tcsh -c 'source ./scripts/synopsys_setup.tcl; pt_shell -f ./scripts/v5_prime_time_top.tcl' > v5_stage_logs/primetime.log 2>&1
rc=$?
stamp "PRIMETIME_EXIT $rc"
test "$rc" -eq 0 || fail "PT return=$rc"
if grep -En '^Error:|^Fatal:' v5_stage_logs/primetime.log > v5_stage_logs/primetime_errors.txt;then
 tail -n 15 v5_stage_logs/primetime_errors.txt
 fail "PrimeTime has errors"
fi
test -s pt_reports/V5_post_layout_timing_setup.rpt && test -s pt_reports/V5_post_layout_timing_hold.rpt || fail "missing PT reports"
stamp "PT_SETUP_HOLD_CREATED_AUDIT_NUMBERS_FOR_FINAL_CLAIM"
