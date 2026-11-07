#!/usr/bin/env bash
# Read-only recovery audit for the ENGR 852 V8 ASIC physical-design checkpoint.
# Run on the university server; does not change the design, launch tools,
# capture the desktop, or delete any files.
set -u
ROOT="${1:-$HOME/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix}"
if [[ ! -d "$ROOT/v8_trial" ]]; then
  echo "Missing V8 trial directory: $ROOT/v8_trial" >&2
  exit 2
fi
cd "$ROOT" || exit 2
printf '\nENGR852 V8 recovery audit | %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
echo "Checkpoint: top.dlib:top/v8_move_delay08"
for item in move_delay08 posteco_export09; do
  exit_file="v8_trial/${item}.exit"
  [[ -f "$exit_file" ]] && printf '%-19s process_exit=%s\n' "$item" "$(cat "$exit_file")" || printf '%-19s process_exit=not_recorded\n' "$item"
done
echo
echo "Independent DRC and placement:"
grep -E '^MOVE08_LEGALITY=|^MOVE08_(MOVE|ROUTE|CHECK_ROUTES|ICV)_RC=' v8_trial/move_delay08.log 2>/dev/null | tail -5 || true
grep -E '100%.*Total Violations:' v8_trial/move_delay08.log 2>/dev/null | tail -1 || true
echo
echo "Post-ECO netlist and parasitics:"
for f in top.v top.sdc top.spef.minTLU_125.spef top.spef.nomTLU_25.spef top.spef.maxTLU_-40.spef; do
  [[ -s "v8_trial/posteco09/$f" ]] && echo "PRESENT $f" || echo "MISSING $f"
done
echo
echo "PrimeTime PT11:"
[[ -f v8_trial/pt11/exit_codes.txt ]] && cat v8_trial/pt11/exit_codes.txt || echo "No exit codes found"
for corner in FAST TYPICAL SLOW; do
  echo "$corner"
  log="v8_trial/pt11/${corner}.log"
  if [[ -f "$log" ]]; then
    errcount=$(grep -c '^Error:' "$log" || true)
    echo "  PT error lines: $errcount"
  else
    echo "  PT log missing"
  fi
  for kind in setup hold; do
    report="v8_trial/pt11/${corner}_${kind}.rpt"
    line=$(grep -m1 'slack (' "$report" 2>/dev/null || true)
    printf '  %-5s %s\n' "$kind" "${line:-no violating path in report; inspect global timing}"
  done
done
echo
echo "Acceptance requires DRC=0, legal placement, routing integrity,"
echo "and setup/hold WNS >= 0 at all three corners, with valid parasitics."
echo "Do not report physical sign-off until all gates pass."
