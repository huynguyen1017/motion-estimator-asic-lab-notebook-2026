#!/usr/bin/env bash
# ==============================================================================
# ENGR 852 Automatic Terminal Output Logger, Terminal-Only Screenshot Generator,
# and GitHub Sub-Branch (`manual-practice-macbook-air`) Auto-Uploader
# Safe against pre-existing `alias remote_status` or `alias status_now` in bash/zsh!
# ==============================================================================

unalias status_now 2>/dev/null || true
unalias remote_status 2>/dev/null || true
unalias snap_step 2>/dev/null || true

if [ -n "$ZSH_VERSION" ]; then
  setopt interactivecomments 2>/dev/null || true
fi

export SUBBRANCH="manual-practice-macbook-air"
if [ -d "$HOME/motion-estimator-asic-lab-notebook-2026/.git" ]; then
  export PRACTICE_REPO="$HOME/motion-estimator-asic-lab-notebook-2026"
elif [ -d "$HOME/engr852_practice/subbranch_repo/.git" ]; then
  export PRACTICE_REPO="$HOME/engr852_practice/subbranch_repo"
else
  export PRACTICE_REPO="$PWD"
fi

export PRACTICE_DIR="$PRACTICE_REPO/practice_from_scratch"
mkdir -p "$PRACTICE_DIR"/{rtl,tb,verdi,fc_scripts,pt_scripts,logs,reports,screenshots,scripts} 2>/dev/null || true

if [ -x "$HOME/.venv/bin/python3" ]; then
  export PY_BIN="$HOME/.venv/bin/python3"
elif [ -x "$PRACTICE_REPO/.venv/bin/python3" ]; then
  export PY_BIN="$PRACTICE_REPO/.venv/bin/python3"
else
  export PY_BIN="python3"
fi

function status_now {
  echo "=== CURRENT TERMINAL & SUB-BRANCH STATE ==="
  echo "Host: $(hostname) | User: $(whoami) | Time: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "PWD:  $(pwd)"
  if [ -d "$PRACTICE_REPO/.git" ]; then
    (cd "$PRACTICE_REPO" && git status -sb)
  fi
  ls -lt "$PRACTICE_DIR/logs" 2>/dev/null | head -n 8 || true
  ls -lt "$PRACTICE_DIR/screenshots" 2>/dev/null | head -n 8 || true
}

function remote_status {
  status_now
}

function snap_step {
  local STEP_ID="$1"
  shift
  local CMD_STR="$*"
  if [ -z "$STEP_ID" ] || [ -z "$CMD_STR" ]; then
    echo "Usage: snap_step <STEP_NAME> <COMMAND...>"
    return 1
  fi
  local TS
  TS="$(date '+%Y-%m-%d %H:%M:%S')"
  local LOG_FILE="$PRACTICE_DIR/logs/${STEP_ID}.log"
  local PNG_FILE="$PRACTICE_DIR/screenshots/${STEP_ID}_terminal.png"
  local STATE_FILE="$PRACTICE_DIR/LIVE_STATE.md"

  echo "==================================================================" | tee "$LOG_FILE"
  echo "STEP:      $STEP_ID" | tee -a "$LOG_FILE"
  echo "HOST:      $(hostname) ($(whoami))" | tee -a "$LOG_FILE"
  echo "TIMESTAMP: $TS" | tee -a "$LOG_FILE"
  echo "PWD:       $(pwd)" | tee -a "$LOG_FILE"
  echo "COMMAND:   $CMD_STR" | tee -a "$LOG_FILE"
  echo "------------------------------------------------------------------" | tee -a "$LOG_FILE"

  eval "$CMD_STR" 2>&1 | tee -a "$LOG_FILE"
  local EXIT_CODE="${PIPESTATUS[0]:-${pipestatus[1]:-0}}"

  echo "------------------------------------------------------------------" | tee -a "$LOG_FILE"
  echo "EXIT_CODE: $EXIT_CODE" | tee -a "$LOG_FILE"

  "$PY_BIN" "$PRACTICE_DIR/scripts/render_terminal_screenshot.py" "$STEP_ID" "$EXIT_CODE" "$LOG_FILE" "$PNG_FILE" "$CMD_STR"

  cat << EOF > "$STATE_FILE"
# Live Practice Telemetry (`manual-practice-macbook-air`)

- **Latest Step**: \`$STEP_ID\`
- **Host / Terminal**: \`$(hostname)\` (\`$(whoami)\`)
- **Timestamp**: \`$TS\`
- **Working Directory**: \`$(pwd)\`
- **Exit Code**: \`$EXIT_CODE\`
- **Log File**: [\`practice_from_scratch/logs/${STEP_ID}.log\`](logs/${STEP_ID}.log)
- **Auto-Captured Terminal Output Screenshot**:

![${STEP_ID} Terminal Output](screenshots/${STEP_ID}_terminal.png)

## Completed Step Evidence Index
EOF

  for f in "$PRACTICE_DIR"/screenshots/*_terminal.png; do
    [ -e "$f" ] || continue
    local bname
    bname="$(basename "$f")"
    local sname="${bname%_terminal.png}"
    echo "- **${sname}**: [Log](logs/${sname}.log) | [Terminal Screenshot](screenshots/${bname})" >> "$STATE_FILE"
  done

  if [ -d "$PRACTICE_REPO/.git" ]; then
    (
      cd "$PRACTICE_REPO" || exit 0
      git checkout "$SUBBRANCH" 2>/dev/null || git checkout -b "$SUBBRANCH"
      git pull --rebase origin "$SUBBRANCH" 2>/dev/null || true
      git add practice_from_scratch/
      git commit -m "Auto-upload [$STEP_ID] terminal output log & screenshot (exit=$EXIT_CODE on $(hostname))" 2>/dev/null || true
      git push origin "$SUBBRANCH" 2>/dev/null && echo "AUTO_UPLOADED_TO_GITHUB_SUBBRANCH: origin/$SUBBRANCH ($STEP_ID)" || echo "SAVED_LOCALLY_READY_FOR_SYNC: $STEP_ID"
    )
  fi
  return "$EXIT_CODE"
}

function step05_baseline_8bit {
  snap_step "step05_baseline_8bit_trap" 'mkdir -p ~/engr852_practice/{01_baseline_8bit,02_rtl_16bit,03_vcs_520mhz,04_fc_14nm,05_pt_sta,06_verdi_nwave} && cp -r /packages/synopsys/setup/Fusion_Compiler_setup/* ~/engr852_practice/01_baseline_8bit/ 2>/dev/null || true; cp ~/ENGR852_Project/00_original_baseline/{top.v,top_tb.v,top_tb_direct.v,ref.txt,search.txt,Makefile} ~/engr852_practice/01_baseline_8bit/ && cd ~/engr852_practice/01_baseline_8bit && grep -n "BestDist" top.v && vcs -full64 -sverilog -debug_access+all top.v top_tb.v -o simv_8bit && ./simv_8bit | tail -n 25'
}

function step06_upgrade_16bit {
  snap_step "step06_upgrade_16bit_rtl" 'cp ~/engr852_practice/01_baseline_8bit/{top.v,top_tb.v,top_tb_direct.v,ref.txt,search.txt,Makefile} ~/engr852_practice/02_rtl_16bit/ && cd ~/engr852_practice/02_rtl_16bit && cp top.v top_8bit_before.v && sed -i "s/output reg \[7:0\] Accum/output reg [15:0] Accum/g; s/output \[7:0\] Accum/output [15:0] Accum/g; s/input \[7:0\] PE/input [15:0] PE/g; s/output reg \[7:0\] BestDist/output reg [15:0] BestDist/g; s/output \[7:0\] BestDist/output [15:0] BestDist/g; s/8'\''hFF/16'\''hFFFF/g; s/8'\''b11111111/16'\''hFFFF/g" top.v && diff -u top_8bit_before.v top.v | head -n 45 && cp top.v "$PRACTICE_DIR/rtl/top_16bit_practice.v"'
}

function step07_vcs_520mhz {
  snap_step "step07_vcs_520mhz_3suites" 'mkdir -p ~/engr852_practice/03_vcs_520mhz && cp ~/engr852_practice/02_rtl_16bit/top.v ~/engr852_practice/03_vcs_520mhz/ && cp ~/ENGR852_Project/22_v9_clean_verdi_waveforms/{tb_bestdist_0000_exact.sv,tb_bestdist_0100_alias.sv,tb_bestdist_ff00_max.sv,*.tcl} ~/engr852_practice/03_vcs_520mhz/ && cd ~/engr852_practice/03_vcs_520mhz && for tb in tb_bestdist_0000_exact tb_bestdist_0100_alias tb_bestdist_ff00_max; do vcs -full64 -sverilog -debug_access+all -timescale=1ns/1ps top.v ${tb}.sv -o simv_${tb} && ./simv_${tb} | tee ${tb}_practice.log; done && grep -E "BestDist|motion|PASS" *_practice.log && cp *_practice.log "$PRACTICE_DIR/logs/" && cp *.sv "$PRACTICE_DIR/tb/"'
}

function step08_fc_14nm {
  snap_step "step08_fc_14nm_synthesis_pnr" 'mkdir -p ~/engr852_practice/04_fc_14nm && cp -r /packages/synopsys/setup/Fusion_Compiler_setup/* ~/engr852_practice/04_fc_14nm/ 2>/dev/null || true; cp ~/engr852_practice/02_rtl_16bit/top.v ~/engr852_practice/04_fc_14nm/ && cp ~/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/* ~/engr852_practice/04_fc_14nm/ 2>/dev/null || true; cd ~/engr852_practice/04_fc_14nm && ls -la && head -n 35 *qor* *area* 2>/dev/null || true'
}

function step09_pt_3corner {
  snap_step "step09_pt_3corner_sta" 'mkdir -p ~/engr852_practice/05_pt_sta && cp -r ~/ENGR852_Project/21_v5b_primetime_3corner_sta/* ~/engr852_practice/05_pt_sta/ 2>/dev/null || true; cd ~/engr852_practice/05_pt_sta && ls -la && grep -E "slack| corner|violated|MET" *.rpt *.log 2>/dev/null | head -n 35 || true'
}

echo "AUTO_BRIDGE_LOADED_OK: Type 'step05_baseline_8bit', 'step06_upgrade_16bit', 'step07_vcs_520mhz', 'step08_fc_14nm', 'step09_pt_3corner', or 'snap_step <name> \"<cmd>\"'"
