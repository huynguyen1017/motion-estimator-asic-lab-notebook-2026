#!/bin/bash
export LM_LICENSE_FILE=/packages/synopsys/license/synopsys.lic
export SNPSLMD_LICENSE_FILE=/packages/synopsys/license/synopsys.lic
export VERDI_HOME=/packages/synopsys/verdi/W-2024.09-1
export PATH=$VERDI_HOME/bin:$PATH
export DBUS_SESSION_BUS_ADDRESS=

for item in \
  "fig7_orig8bit_row1.tcl:raw_fig7.png" \
  "fig8_orig8bit_complete.tcl:raw_fig8.png" \
  "fig9_16bit_sat_row1.tcl:raw_fig9.png" \
  "fig10_16bit_perfect_match.tcl:raw_fig10.png"
do
  tcl="${item%%:*}"
  png="${item##*:}"
  # Ensure wvScrollUp so clock is at the very top
  if ! grep -q "wvScrollUp" "$tcl"; then
    echo "wvScrollUp -win \$w 10" >> "$tcl"
    echo "catch {verdiDockWidgetMaximize -dock windowDock_nWave_2}" >> "$tcl"
  fi
  verdi -play "$tcl" > "${tcl}.run.log" 2>&1 &
  VPID=$!
  sleep 13
  gnome-screenshot -f "$png" >/dev/null 2>&1 || true
  kill -9 $VPID 2>/dev/null || true
  pkill -9 -u 926784856 verdi 2>/dev/null || true
  pkill -9 -u 926784856 novas 2>/dev/null || true
  sleep 1
done
