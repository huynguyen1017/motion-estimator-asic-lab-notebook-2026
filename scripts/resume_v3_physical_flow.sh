#!/usr/bin/env bash
# Resume the instructor-prescribed Fusion Compiler/PrimeTime stages after a dropped SSH session.
# Runs on the authorized SFSU Linux server; does not require nor store a password.
# Example: nohup bash resume_v3_physical_flow.sh cts > v3_master.log 2>&1 < /dev/null &
set -Eeuo pipefail
umask 077

STAGE="${1:-cts}"
WORKDIR="${2:-$HOME/ENGR852_Project/16_v3b_final_asic_fc}"
cd "$WORKDIR"
test -r scripts/synopsys_setup.tcl || { echo "FAIL: official course setup missing"; exit 2; }
test -d results/top.dlib || { echo "FAIL: mapped design library results/top.dlib missing"; exit 3; }

mkdir -p logs/v3_resume
STAMP="$(date +%Y%m%d_%H%M%S)"
SUMMARY="logs/v3_resume/summary_${STAMP}.txt"

fatal() { printf 'FAILED: %s\n' "$*" | tee -a "$SUMMARY"; exit 1; }
report() { printf '%s\n' "$*" | tee -a "$SUMMARY"; }

declare -A SCRIPT
SCRIPT[cts]=clock_opt.tcl
SCRIPT[route]=route_opt.tcl
SCRIPT[signoff]=signoff.tcl
SCRIPT[pt]=sta_post_layout.tcl
FLOW=(cts route signoff pt)

start=-1
for i in "${!FLOW[@]}"; do
  if [[ "${FLOW[$i]}" == "$STAGE" ]]; then start="$i"; break; fi
done
(( start >= 0 )) || fatal "Unknown stage '$STAGE' (valid: cts, route, signoff, pt)"

report "V3_RESUME_START=$(date -Is) HOST=$(hostname) FIRST_STAGE=$STAGE"
report "WORKDIR=$WORKDIR"
report "SOURCE_SHA256=$(sha256sum common/rtl/verilog/top.v | awk '{print $1}')"
report "SDC_SHA256=$(sha256sum common/sdc/top.sdc | awk '{print $1}')"

for (( i=start; i<${#FLOW[@]}; i++ )); do
    name="${FLOW[$i]}"
    tcl="${SCRIPT[$name]}"
    test -r "scripts/$tcl" || fatal "Missing course script scripts/$tcl"
    log="logs/v3_resume/${STAMP}_${name}.log"

    if [[ "$name" == pt ]]; then
      # PrimeTime post-layout timing requires extracted interconnect parasitics.
      if ! find results -type f \( -iname '*.spef' -o -iname '*.spef.gz' \) -print -quit | grep -q .; then
        fatal "Cannot run post-layout PrimeTime: no extracted SPEF found under results"
      fi
    fi

    report "BEGIN $name $(date -Is) SCRIPT=$tcl LOG=$log"
    set +e
    if [[ "$name" == pt ]]; then
      timeout 14400 tcsh -c "source scripts/synopsys_setup.tcl; pt_shell -f scripts/$tcl" >"$log" 2>&1
    else
      timeout 14400 tcsh -c "source scripts/synopsys_setup.tcl; fc_shell -no_log -f scripts/$tcl" >"$log" 2>&1
    fi
    rc=$?
    set -e
    report "EXIT_CODE $name $rc"
    (( rc == 0 )) || fatal "$name tool process failed; see $log"
    if grep -n -E '^Error:|^Fatal:|PLACE-004|PLACE-006|Error-\[' "$log" > "${log}.errors"; then
      tail -n 12 "${log}.errors" | tee -a "$SUMMARY"
      fatal "$name had tool errors despite shell exit code 0"
    fi

    if [[ "$name" == pt ]]; then
      grep -q 'PrimeTime' "$log" || fatal "PrimeTime completion marker missing"
    else
      grep -q 'Thank you for using Fusion Compiler' "$log" || fatal "Fusion Compiler completion marker missing"
    fi
    report "STAGE_PASSED_PROCESS_AND_ERROR_SCAN $name $(date -Is)"
done

report "ALL_REQUESTED_STAGES_PROCESS_COMPLETED $(date -Is)"
report "IMPORTANT: verify routing, DRC, extracted SPEF and PrimeTime setup AND hold report contents independently before claiming physical signoff."
