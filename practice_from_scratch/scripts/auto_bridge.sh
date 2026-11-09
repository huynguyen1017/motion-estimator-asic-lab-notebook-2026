#!/usr/bin/env bash
# ==============================================================================
# ENGR 852 Auto-Evidence Bridge (auto_bridge.sh)
# Compatible with BOTH macOS (zsh/bash) on MacBook Air AND Linux (bash) on
# 926784856@mahmoodi.rcc.at.sfsu.edu.
#
# Automatically:
#   1. Exports all Synopsys EDA toolchains (VCS, Verdi, Fusion Compiler, ICV,
#      PrimeTime) natively into bash on mahmoodi.rcc.at.sfsu.edu.
#   2. Sanitizes any accidental Gmail auto-hyperlinks ([file.sv](http://...))
#      when copying and pasting commands from Gmail.
#   3. Captures 100% of terminal stdout/stderr for each page's command into
#      practice_from_scratch/logs/<page_id>.log
#   4. Renders a full-height terminal screenshot PNG into
#      practice_from_scratch/screenshots/<page_id>_terminal.png
#   5. Updates practice_from_scratch/STATUS_DASHBOARD.md and auto-pushes to
#      GitHub sub-branch: manual-practice-macbook-air (NEVER touches main).
# ==============================================================================

unalias remote_status 2>/dev/null || true
unalias status_now 2>/dev/null || true
unalias snap_step 2>/dev/null || true

# 1. Native Bash Synopsys Toolchain Setup on mahmoodi.rcc.at.sfsu.edu
if [ -d "/packages/synopsys" ]; then
    export TOOLSET="VCS"
    export CG_PROGNAME="Synopsys"
    export VCS="/packages/synopsys/vcs/W-2024.09-1"
    export VCS_HOME="/packages/synopsys/vcs/W-2024.09-1"
    export VCS_CC="gcc"
    export VIRSIMHOME="/packages/synopsys/vcs/W-2024.09-1/gui/virsim"
    export VERDI_HOME="/packages/synopsys/verdi/W-2024.09-1"
    export NOVAS_HOME="/packages/synopsys/verdi/W-2024.09-1"
    export FC_HOME="/packages/synopsys/fc/X-2025.06-SP2a"
    export ICV_HOME_DIR="/packages/synopsys/ic_validator/W-2024.09-3"
    export PT_HOME="/packages/synopsys/primetime/U-2022.12-SP5-1"
    export SYNOPSYS_LC_ROOT="/packages/synopsys/library_compiler/S-2021.06-SP4"
    export XKEYSYMDB="/usr/share/X11/XKeysymDB"
    export LM_LICENSE_FILE="/packages/synopsys/license/synopsys.lic"
    export SNPSLMD_LICENSE_FILE="/packages/synopsys/license/synopsys.lic"
    unset LANG
    unset LC_ALL
    export PATH="$VCS_HOME/bin:$VIRSIMHOME/bin:$VERDI_HOME/bin:$FC_HOME/bin:$ICV_HOME_DIR/bin/linux64:$PT_HOME/bin:$SYNOPSYS_LC_ROOT/bin:/usr/local/X11R6/bin:$PATH"
fi

# 2. Locate the cloned repository root
if [ -n "${BASH_SOURCE[0]}" ]; then
    _BRIDGE_SCRIPT_PATH="${BASH_SOURCE[0]}"
elif [ -n "$ZSH_VERSION" ]; then
    eval '_BRIDGE_SCRIPT_PATH="${(%):-%x}"'
else
    _BRIDGE_SCRIPT_PATH="$0"
fi

export BRIDGE_SCRIPT_DIR="$(cd "$(dirname "$_BRIDGE_SCRIPT_PATH")" && pwd)"
export BRIDGE_REPO_ROOT="$(cd "$BRIDGE_SCRIPT_DIR/../.." && pwd)"
export BRIDGE_LOG_DIR="$BRIDGE_REPO_ROOT/practice_from_scratch/logs"
export BRIDGE_IMG_DIR="$BRIDGE_REPO_ROOT/practice_from_scratch/screenshots"
export BRIDGE_RENDER_PY="$BRIDGE_SCRIPT_DIR/render_terminal_screenshot.py"
export BRIDGE_BRANCH="manual-practice-macbook-air"

mkdir -p "$BRIDGE_LOG_DIR" "$BRIDGE_IMG_DIR"

function status_now {
    echo "=== LOCAL MACBOOK AIR TERMINAL STATE ==="
    echo "User@Host : $(whoami)@$(hostname)"
    echo "PWD       : $(pwd)"
    echo "Shell     : $SHELL"
    echo "DISPLAY   : ${DISPLAY:-<not set>}"
    echo "Branch    : $(git -C "$BRIDGE_REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null)"
}

function remote_status {
    echo "=== REMOTE MAHMOODI SERVER TERMINAL STATE ==="
    echo "User@Host : $(whoami)@$(hostname)"
    echo "PWD       : $(pwd)"
    echo "DISPLAY   : ${DISPLAY:-<not set>}"
    echo "VCS       : $(which vcs 2>/dev/null || echo 'not found')"
    echo "Verdi     : $(which verdi 2>/dev/null || echo 'not found')"
    echo "FC Shell  : $(which fc_shell 2>/dev/null || echo 'not found')"
    echo "ICV       : $(which icv 2>/dev/null || echo 'not found')"
    echo "PrimeTime : $(which pt_shell 2>/dev/null || echo 'not found')"
}

function snap_step {
    local step_id="$1"
    shift
    local raw_cmd="$*"
    if [ -z "$step_id" ] || [ -z "$raw_cmd" ]; then
        echo "Usage: snap_step <page_step_name> '<command_to_execute>'"
        return 1
    fi

    # Strip any accidental Gmail auto-hyperlinks like [top.v](http://top.v/)
    local cmd_str
    cmd_str="$(python3 -c 'import re, sys; s = sys.argv[1]; s = re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", s); print(s)' "$raw_cmd" 2>/dev/null || echo "$raw_cmd")"

    local ts
    ts="$(date '+%Y-%m-%d %H:%M:%S %Z')"
    local host_short
    host_short="$(hostname)"
    local start_pwd
    start_pwd="$(pwd)"
    local log_file="$BRIDGE_LOG_DIR/${step_id}.log"
    local img_file="$BRIDGE_IMG_DIR/${step_id}_terminal.png"
    local tmp_out="/tmp/${step_id}_stdout_$$.txt"

    echo "======================================================================"
    echo ">>> [AUTO-BRIDGE] Executing Step: $step_id"
    echo ">>> [AUTO-BRIDGE] Command       : $cmd_str"
    echo "======================================================================"

    # Execute command in current shell context and tee output
    eval "$cmd_str" > "$tmp_out" 2>&1
    local exit_code=$?
    cat "$tmp_out"

    {
        echo "# ===================================================================="
        echo "# STEP_ID       : $step_id"
        echo "# TIMESTAMP     : $ts"
        echo "# HOST          : $(whoami)@${host_short}"
        echo "# WORKING_DIR   : $start_pwd -> $(pwd)"
        echo "# COMMAND       : $cmd_str"
        echo "# EXIT_CODE     : $exit_code"
        echo "# ===================================================================="
        echo ""
        echo "$ $cmd_str"
        cat "$tmp_out"
    } > "$log_file"
    rm -f "$tmp_out"

    # Find Python 3 with Pillow to render full-height terminal screenshot PNG
    local py_bin="python3"
    if [ -x "$HOME/Developer/coursework/sfsu/2026-fall/sfsu-engr852-2026-fall/.venv/bin/python3" ]; then
        py_bin="$HOME/Developer/coursework/sfsu/2026-fall/sfsu-engr852-2026-fall/.venv/bin/python3"
    elif [ -x "$HOME/.venv/bin/python3" ]; then
        py_bin="$HOME/.venv/bin/python3"
    fi

    "$py_bin" "$BRIDGE_RENDER_PY" \
        --log "$log_file" \
        --out "$img_file" \
        --title "ENGR 852 — $step_id" \
        --host "$(whoami)@${host_short}" \
        --exit-code "$exit_code"

    # Update live dashboard & auto-push to GitHub sub-branch
    (
        cd "$BRIDGE_REPO_ROOT" || exit 0
        git checkout "$BRIDGE_BRANCH" >/dev/null 2>&1 || git checkout -b "$BRIDGE_BRANCH" >/dev/null 2>&1
        git pull --rebase origin "$BRIDGE_BRANCH" >/dev/null 2>&1 || true

        local dash="$BRIDGE_REPO_ROOT/practice_from_scratch/STATUS_DASHBOARD.md"
        {
            echo "# Live MacBook Air & Mahmoodi Server Practice Dashboard (\`manual-practice-macbook-air\`)"
            echo ""
            echo "- **Last Updated**: \`$ts\`"
            echo "- **Latest Step**: \`$step_id\` (Exit Code: \`$exit_code\` on \`$(whoami)@${host_short}\`)"
            echo ""
            echo "## Executed Page Steps (Chronological Log & Screenshot Evidence)"
            echo ""
            echo "| Step / Page ID | Exit Code | Host | Terminal Log | Auto-Captured Terminal Screenshot |"
            echo "| :--- | :---: | :--- | :--- | :--- |"
            for lf in $(ls -1 "$BRIDGE_LOG_DIR"/*.log 2>/dev/null | sort -V); do
                local bn
                bn="$(basename "$lf" .log)"
                local ec
                ec="$(grep -m1 '^# EXIT_CODE' "$lf" | awk -F': ' '{print $2}')"
                local hst
                hst="$(grep -m1 '^# HOST' "$lf" | awk -F': ' '{print $2}')"
                echo "| \`$bn\` | \`${ec:-0}\` | \`${hst:-mahmoodi}\` | [${bn}.log](logs/${bn}.log) | [${bn}_terminal.png](screenshots/${bn}_terminal.png) |"
            done
        } > "$dash"

        git add "practice_from_scratch/logs/${step_id}.log" \
                "practice_from_scratch/screenshots/${step_id}_terminal.png" \
                "practice_from_scratch/STATUS_DASHBOARD.md" 2>/dev/null
        git commit -m "Auto-upload [$step_id] terminal output log & screenshot (exit=$exit_code on $host_short)" >/dev/null 2>&1 || true
        git push -u origin "$BRIDGE_BRANCH" >/dev/null 2>&1 && \
            echo ">>> [AUTO-BRIDGE] Uploaded log + screenshot to GitHub branch '$BRIDGE_BRANCH': $step_id" || \
            echo ">>> [AUTO-BRIDGE] Saved locally in $BRIDGE_REPO_ROOT/practice_from_scratch/ (run 'git push' if offline)"
    )

    return $exit_code
}

echo "AUTO_BRIDGE_READY: branch=$BRIDGE_BRANCH | repo=$BRIDGE_REPO_ROOT"
