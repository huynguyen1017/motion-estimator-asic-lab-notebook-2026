#!/usr/bin/env bash
# ==============================================================================
# ENGR 852 Live Terminal Auto-Logger, Screenshot Renderer & GitHub Sub-Branch
# Synchronizer (manual-practice-macbook-air)
# Only records and uploads commands as you actually execute them step-by-step.
# ==============================================================================

export PRACTICE_REPO="/home/926784856/motion-estimator-asic-lab-notebook-2026"
if [ ! -d "$PRACTICE_REPO/.git" ]; then
    export PRACTICE_REPO="$HOME/engr852_practice/subbranch_repo"
fi
export PRACTICE_BRANCH="manual-practice-macbook-air"
export PRACTICE_DIR="$PRACTICE_REPO/practice_from_scratch"
export LOG_DIR="$PRACTICE_DIR/logs"
export IMG_DIR="$PRACTICE_DIR/screenshots"
export STATE_FILE="$PRACTICE_DIR/LIVE_STATE.md"

mkdir -p "$LOG_DIR" "$IMG_DIR"

# Load Synopsys EDA tool environment on mahmoodi.rcc.at.sfsu.edu
if [ -f /packages/synopsys/setup/synopsys_setup.sh ]; then
    source /packages/synopsys/setup/synopsys_setup.sh >/dev/null 2>&1 || true
fi

unalias remote_status 2>/dev/null || true
unalias snap_step 2>/dev/null || true

function remote_status {
    echo "=== CURRENT MAHMOODI STATE ==="
    echo "Host: $(hostname) | User: $(whoami) | Time: $(date "+%Y-%m-%d %H:%M:%S %Z")"
    echo "PWD:  $(pwd)"
    echo "Git Sub-Branch Status ($PRACTICE_REPO):"
    git -C "$PRACTICE_REPO" status -sb 2>/dev/null || true
    echo "Executed Step Logs Recorded So Far:"
    ls -lh "$LOG_DIR" 2>/dev/null || true
}

function snap_step {
    local step_id="$1"
    shift
    local cmd_str="$*"
    if [ -z "$step_id" ] || [ -z "$cmd_str" ]; then
        echo "Usage: snap_step <step_id> \"<command_to_run>\""
        return 1
    fi

    local ts
    ts="$(date "+%Y-%m-%d %H:%M:%S %Z")"
    local log_file="$LOG_DIR/${step_id}.log"
    local img_file="$IMG_DIR/${step_id}_terminal.png"
    local prompt_str="[$(whoami)@$(hostname -s) $(basename "$(pwd)")]$"

    echo "==================================================================" | tee "$log_file"
    echo "STEP:      $step_id" | tee -a "$log_file"
    echo "HOST:      $(hostname) ($(whoami))" | tee -a "$log_file"
    echo "TIMESTAMP: $ts" | tee -a "$log_file"
    echo "PWD:       $(pwd)" | tee -a "$log_file"
    echo "COMMAND:   $cmd_str" | tee -a "$log_file"
    echo "------------------------------------------------------------------" | tee -a "$log_file"

    eval "$cmd_str" 2>&1 | tee -a "$log_file"
    local exit_code=${PIPESTATUS[0]}

    echo "------------------------------------------------------------------" | tee -a "$log_file"
    echo "EXIT_CODE: $exit_code" | tee -a "$log_file"
    echo "==================================================================" | tee -a "$log_file"

    # Render terminal output PNG screenshot
    python3 "$PRACTICE_DIR/scripts/render_terminal_screenshot.py" \
        --log "$log_file" \
        --out "$img_file" \
        --title "${step_id} — $(whoami)@$(hostname) — ${ts}" \
        --prompt "$prompt_str" \
        --cmd "$cmd_str" || true

    # Update LIVE_STATE.md (note: backticks escaped so bash does not execute them)
    cat << STATE_EOF > "$STATE_FILE"
# Live Practice Telemetry (\`manual-practice-macbook-air\`)

- **Latest Step Executed**: \`$step_id\`
- **Timestamp**: \`$ts\`
- **Host / Account**: \`$(whoami)@$(hostname)\`
- **Working Directory**: \`$(pwd)\`
- **Command Executed**:
\`\`\`bash
$cmd_str
\`\`\`
- **Exit Code**: \`$exit_code\`
- **Terminal Log**: [\`practice_from_scratch/logs/${step_id}.log\`](logs/${step_id}.log)
- **Auto-Captured Terminal Screenshot**:

![${step_id}](screenshots/${step_id}_terminal.png)
STATE_EOF

    # Keep both local practice repo paths synchronized if both exist
    if [ -d "$HOME/engr852_practice/subbranch_repo/.git" ] && [ "$PRACTICE_REPO" != "$HOME/engr852_practice/subbranch_repo" ]; then
        cp -rf "$PRACTICE_DIR/"* "$HOME/engr852_practice/subbranch_repo/practice_from_scratch/" 2>/dev/null || true
    fi

    # Commit and push ONLY what has been executed so far to origin/manual-practice-macbook-air
    (
        cd "$PRACTICE_REPO" && \
        git checkout "$PRACTICE_BRANCH" >/dev/null 2>&1 && \
        git add practice_from_scratch README.md && \
        git commit -m "Auto-upload [$step_id] terminal output log & screenshot (exit=$exit_code on $(hostname))" && \
        git push origin "$PRACTICE_BRANCH"
    )
    echo "[AUTO-UPLOAD COMPLETE] -> https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026/tree/manual-practice-macbook-air/practice_from_scratch"
    return $exit_code
}

# Current Step 5 helper (only for the step currently being executed)
function step05_baseline_8bit {
    snap_step "step05_baseline_8bit_trap" "mkdir -p ~/engr852_practice/01_baseline_8bit && cp -f ~/ENGR852_Project/00_original_baseline/{top.v,top_tb.v,top_tb_direct.v,ref.txt,search.txt,Makefile} ~/engr852_practice/01_baseline_8bit/ && cd ~/engr852_practice/01_baseline_8bit && grep -n \"BestDist\" top.v && vcs -full64 -sverilog -debug_access+all top.v top_tb.v -o simv_8bit && ./simv_8bit | tail -n 25"
}

echo "AUTO_BRIDGE_LOADED_OK: snap_step & remote_status ready on $(hostname)"
