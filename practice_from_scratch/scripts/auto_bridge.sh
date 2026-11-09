#!/usr/bin/env bash
# ==============================================================================
# ENGR 852 Auto-Evidence & Live Operations Console Bridge (`auto_bridge.sh`)
# Compatible with both macOS `zsh` (MacBook Air / XQuartz xterm) and Linux `bash`
# (`926784856@mahmoodi.rcc.at.sfsu.edu`).
#
# Features:
#   1. Exports all 5 Synopsys toolchains natively in `bash` on mahmoodi:
#      vcs, verdi, fc_shell, icv, pt_shell + LM_LICENSE_FILE
#   2. Strict Sequential Page 1 -> Page 100 Guardrail (`snap_step "pageNNN_..." "..."`):
#      Prevents accidentally jumping from Page 1 to Page 100 out of order!
#   3. Live Terminal & XQuartz Telemetry Sync:
#      Streams terminal commands, IP addresses, $DISPLAY, logs, rendered terminal
#      screenshots, and Verdi nWave / 14nm layout PNGs to BOTH:
#        - Live Operations Console Web Server (`http://127.0.0.1:8788`, `http://192.168.1.70:8788`, `http://130.212.163.69:8788`)
#        - GitHub Sub-Branch (`manual-practice-macbook-air`: `practice_from_scratch/live_state.json` & `STATUS_DASHBOARD.md`)
# ==============================================================================

unalias status_now 2>/dev/null || true
unalias remote_status 2>/dev/null || true
unalias snap_step 2>/dev/null || true

if [ -n "${ZSH_VERSION:-}" ]; then
  _BRIDGE_SRC="${(%):-%N}"
elif [ -n "${BASH_SOURCE[0]:-}" ]; then
  _BRIDGE_SRC="${BASH_SOURCE[0]}"
else
  _BRIDGE_SRC="$0"
fi
export AUTO_BRIDGE_SCRIPT_DIR="$(cd "$(dirname "$_BRIDGE_SRC")" 2>/dev/null && pwd)"
export AUTO_BRIDGE_REPO_ROOT="$(cd "$AUTO_BRIDGE_SCRIPT_DIR/../.." 2>/dev/null && pwd)"
export AUTO_BRIDGE_PRACTICE_DIR="$AUTO_BRIDGE_REPO_ROOT/practice_from_scratch"
export AUTO_BRIDGE_LOG_DIR="$AUTO_BRIDGE_PRACTICE_DIR/logs"
export AUTO_BRIDGE_SHOT_DIR="$AUTO_BRIDGE_PRACTICE_DIR/screenshots"
export AUTO_BRIDGE_WAVE_DIR="$AUTO_BRIDGE_PRACTICE_DIR/waveforms"
export AUTO_BRIDGE_STATE_JSON="$AUTO_BRIDGE_PRACTICE_DIR/live_state.json"
export AUTO_BRIDGE_BRANCH="manual-practice-macbook-air"
export AUTO_BRIDGE_WEB_URLS="${AUTO_BRIDGE_WEB_URLS:-http://127.0.0.1:8788 http://192.168.1.70:8788 http://130.212.163.69:8788}"

mkdir -p "$AUTO_BRIDGE_LOG_DIR" "$AUTO_BRIDGE_SHOT_DIR" "$AUTO_BRIDGE_WAVE_DIR" 2>/dev/null || true

# Export Synopsys EDA Toolchain natively in bash on mahmoodi.rcc.at.sfsu.edu
if [ -d "/packages/synopsys" ]; then
  export SYNOPSYS="/packages/synopsys"
  export VCS_HOME="/packages/synopsys/vcs/W-2024.09-1"
  export VERDI_HOME="/packages/synopsys/verdi/W-2024.09-1"
  export NOVAS_HOME="/packages/synopsys/verdi/W-2024.09-1"
  export FC_HOME="/packages/synopsys/fc/X-2025.06-SP2a"
  export ICV_HOME_DIR="/packages/synopsys/ic_validator/W-2024.09-3"
  export PT_HOME="/packages/synopsys/primetime/U-2022.12-SP5-1"
  export SCL_HOME="/packages/synopsys/scl/2025.03"
  export LM_LICENSE_FILE="/packages/synopsys/license/synopsys.lic"
  export SNPSLMD_LICENSE_FILE="27020@engrlic.rcc.at.sfsu.edu:/packages/synopsys/license/synopsys.lic"
  export LD_LIBRARY_PATH="/packages/synopsys/verdi/W-2024.09-1/share/PLI/VCS/LINUX64:${LD_LIBRARY_PATH:-}"
  case ":$PATH:" in
    *":/packages/synopsys/vcs/W-2024.09-1/bin:"*) ;;
    *)
      export PATH="/packages/synopsys/vcs/W-2024.09-1/bin:/packages/synopsys/verdi/W-2024.09-1/bin:/packages/synopsys/fc/X-2025.06-SP2a/bin:/packages/synopsys/ic_validator/W-2024.09-3/bin/linux64:/packages/synopsys/primetime/U-2022.12-SP5-1/bin:/packages/synopsys/syn/W-2024.09-SP4/bin:/packages/synopsys/scl/2025.03/linux64/bin:$PATH"
      ;;
  esac
fi

function _find_bridge_python() {
  for cand in \
    "$AUTO_BRIDGE_REPO_ROOT/.venv/bin/python3" \
    "$HOME/Developer/motion-estimator-14nm-asic-manual/.venv/bin/python3" \
    "/Users/huynguyen/Developer/portfolio/motion-estimator-asic-lab-notebook-2026/.venv/bin/python3" \
    "/opt/homebrew/bin/python3" \
    "/usr/bin/python3" \
    "$(command -v python3 2>/dev/null)"; do
    if [ -n "$cand" ] && [ -x "$cand" ]; then
      echo "$cand"
      return 0
    fi
  done
  echo "python3"
}

function _detect_terminal_env() {
  local hname
  hname="$(hostname 2>/dev/null || echo unknown)"
  if [[ "$hname" == *"mahmoodi"* ]]; then
    echo "926784856@mahmoodi.rcc.at.sfsu.edu"
  elif [ -n "${XTERM_VERSION:-}" ] || [[ "${TERM_PROGRAM:-}" == *"XQuartz"* ]] || [[ "${DISPLAY:-}" == *"org.xquartz"* && "${TERM:-}" == "xterm"* ]]; then
    echo "XQUARTZ_XTERM"
  else
    echo "MACBOOK_AIR_TERMINAL"
  fi
}

function _detect_ip_summary() {
  if command -v hostname >/dev/null 2>&1 && hostname -I >/dev/null 2>&1; then
    hostname -I 2>/dev/null | awk '{print $1}'
  elif command -v ifconfig >/dev/null 2>&1; then
    ifconfig 2>/dev/null | awk '/inet / && $2 != "127.0.0.1" {print $2}' | paste -sd "," -
  else
    echo "127.0.0.1"
  fi
}

function _post_live_telemetry() {
  local event_type="$1"
  local step_id="$2"
  local cmd_str="$3"
  local status_str="$4"
  local exit_code="${5:-0}"
  local msg_str="${6:-}"
  local py_bin
  py_bin="$(_find_bridge_python)"
  local term_env
  term_env="$(_detect_terminal_env)"
  local ip_str
  ip_str="$(_detect_ip_summary)"

  "$py_bin" - "$event_type" "$step_id" "$cmd_str" "$status_str" "$exit_code" "$msg_str" "$term_env" "$ip_str" << 'PYEOF' 2>/dev/null || true
import json, os, sys, time, urllib.request
from pathlib import Path

event_type, step_id, cmd_str, status_str, exit_code, msg_str, term_env, ip_str = sys.argv[1:9]
repo_root = Path(os.environ.get("AUTO_BRIDGE_REPO_ROOT", "."))
state_path = repo_root / "practice_from_scratch" / "live_state.json"
logs_dir = repo_root / "practice_from_scratch" / "logs"

state = {
    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
    "epoch": time.time(),
    "last_event": event_type,
    "active_terminal": term_env,
    "host": os.uname().nodename,
    "user": os.environ.get("USER", "student"),
    "ip_addresses": ip_str,
    "display": os.environ.get("DISPLAY", ""),
    "pwd": os.getcwd(),
    "last_step_id": step_id,
    "last_command": cmd_str,
    "last_status": status_str,
    "last_exit_code": int(exit_code) if exit_code.lstrip("-").isdigit() else 0,
    "guardrail_alert": msg_str if status_str == "BLOCKED_OUT_OF_ORDER" else "",
    "completed_pages": {},
    "terminal_feed": [],
}
if state_path.exists():
    try:
        old = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(old, dict):
            state["completed_pages"] = old.get("completed_pages", {})
            state["terminal_feed"] = old.get("terminal_feed", [])[-35:]
            if status_str != "BLOCKED_OUT_OF_ORDER" and status_str == "PASS":
                state["guardrail_alert"] = ""
            elif not msg_str:
                state["guardrail_alert"] = old.get("guardrail_alert", "")
    except Exception:
        pass

# Scan logs_dir for any pageNNN_*.log files so state is always accurate
if logs_dir.exists():
    for lf in sorted(logs_dir.glob("page*.log")):
        sname = lf.stem
        m = sname[:7]
        if m.startswith("page") and m[4:7].isdigit():
            pnum = int(m[4:7])
            txt = lf.read_text(encoding="utf-8", errors="ignore")
            ec = 0
            for ln in txt.splitlines()[:10]:
                if ln.startswith("# Exit Code   :"):
                    try:
                        ec = int(ln.split(":", 1)[1].strip())
                    except Exception:
                        ec = 0
            state["completed_pages"][str(pnum)] = {
                "page_num": pnum,
                "step_id": sname,
                "status": "PASS" if ec == 0 else "FAIL",
                "exit_code": ec,
                "log_file": f"practice_from_scratch/logs/{lf.name}",
                "screenshot_file": f"practice_from_scratch/screenshots/{sname}_terminal.png",
                "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lf.stat().st_mtime)),
            }

if step_id.startswith("page") and step_id[4:7].isdigit() and status_str in ("PASS", "FAIL"):
    pnum = int(step_id[4:7])
    state["completed_pages"][str(pnum)] = {
        "page_num": pnum,
        "step_id": step_id,
        "status": status_str,
        "exit_code": int(exit_code) if exit_code.lstrip("-").isdigit() else 0,
        "log_file": f"practice_from_scratch/logs/{step_id}.log",
        "screenshot_file": f"practice_from_scratch/screenshots/{step_id}_terminal.png",
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

done_nums = sorted(int(k) for k, v in state["completed_pages"].items() if v.get("status") == "PASS")
highest_seq = 0
for n in range(1, 101):
    if n in done_nums:
        highest_seq = n
    else:
        break
state["highest_sequential_page"] = highest_seq
state["next_required_page"] = min(100, highest_seq + 1)
state["total_passed_pages"] = len(done_nums)

feed_item = {
    "time": time.strftime("%H:%M:%S"),
    "terminal": term_env,
    "host": os.uname().nodename,
    "ip": ip_str,
    "display": os.environ.get("DISPLAY", ""),
    "pwd": os.getcwd(),
    "step_id": step_id,
    "command": cmd_str[:240],
    "status": status_str,
    "message": msg_str,
}
state["terminal_feed"].append(feed_item)
state["terminal_feed"] = state["terminal_feed"][-40:]

state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

# Also push via HTTP POST to Live Web Console if reachable
urls = os.environ.get("AUTO_BRIDGE_WEB_URLS", "http://127.0.0.1:8788").split()
payload = json.dumps(state).encode("utf-8")
for u in urls:
    try:
        req = urllib.request.Request(
            u.rstrip("/") + "/api/telemetry",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=0.6).read()
        break
    except Exception:
        pass
PYEOF
}

function status_now() {
  echo "=== LOCAL MACBOOK / XQUARTZ TERMINAL STATE ==="
  echo "Terminal  : $(_detect_terminal_env)"
  echo "User@Host : $(whoami)@$(hostname)"
  echo "IP Addrs  : $(_detect_ip_summary)"
  echo "Date/Time : $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Directory : $(pwd)"
  echo "DISPLAY   : ${DISPLAY:-<unset>}"
  _post_live_telemetry "STATUS_CHECK" "status_now" "status_now" "INFO" 0 "Checked local terminal state"
}

function remote_status() {
  echo "=== REMOTE MAHMOODI SERVER TERMINAL STATE ==="
  echo "Terminal  : $(_detect_terminal_env)"
  echo "User@Host : $(whoami)@$(hostname)"
  echo "IP Addrs  : $(_detect_ip_summary)"
  echo "Date/Time : $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Directory : $(pwd)"
  echo "DISPLAY   : ${DISPLAY:-<unset>}"
  echo "VCS       : $(command -v vcs 2>/dev/null || echo NOT_IN_PATH)"
  echo "Verdi     : $(command -v verdi 2>/dev/null || echo NOT_IN_PATH)"
  echo "FC Shell  : $(command -v fc_shell 2>/dev/null || echo NOT_IN_PATH)"
  echo "ICV       : $(command -v icv 2>/dev/null || echo NOT_IN_PATH)"
  echo "PrimeTime : $(command -v pt_shell 2>/dev/null || echo NOT_IN_PATH)"
  _post_live_telemetry "REMOTE_STATUS" "remote_status" "remote_status" "INFO" 0 "Checked remote mahmoodi EDA toolchain state"
}

function snap_step() {
  local step_name="${1:-unnamed_step}"
  shift || true
  local raw_cmd="$*"

  # Strip accidental Markdown links created by Gmail auto-linking (e.g. [top.v](http://top.v/))
  local clean_cmd
  clean_cmd="$(printf '%s' "$raw_cmd" | sed -E 's/\[([a-zA-Z0-9_.-]+)\]\(https?:\/\/[^)]+\)/\1/g')"

  local py_bin
  py_bin="$(_find_bridge_python)"

  # ============================================================================
  # SEQUENTIAL PAGE 1 -> PAGE 100 GUARDRAIL CHECK
  # Prevents accidentally jumping from Page 1 (`page001_...`) to Page 100 (`page100_...`)
  # ============================================================================
  if [[ "$step_name" =~ ^page([0-9]{3}) ]] && [ "${FORCE_STEP:-0}" != "1" ]; then
    local req_page_num
    req_page_num=$((10#${BASH_REMATCH[1]:-${match[1]}}))
    local next_allowed
    next_allowed="$("$py_bin" - "$AUTO_BRIDGE_LOG_DIR" << 'PYEOF' 2>/dev/null || echo 1
import sys
from pathlib import Path
logs_dir = Path(sys.argv[1])
done = set()
if logs_dir.exists():
    for lf in logs_dir.glob("page*.log"):
        s = lf.stem
        if len(s) >= 7 and s[:4] == "page" and s[4:7].isdigit():
            txt = lf.read_text(encoding="utf-8", errors="ignore")
            if "# Exit Code   : 0" in txt or "Exit Code   : 0" in txt:
                done.add(int(s[4:7]))
highest = 0
for n in range(1, 101):
    if n in done:
        highest = n
    else:
        break
print(highest + 1)
PYEOF
)"
    if [ -n "$next_allowed" ] && [ "$req_page_num" -gt "$next_allowed" ]; then
      local block_msg="STOP! You attempted Page ${req_page_num} (${step_name}), but your next sequential step is Page ${next_allowed} (page$(printf '%03d' "$next_allowed")_...). Complete Page ${next_allowed} first so your V1->V9 build stays in order (or set FORCE_STEP=1 to override)."
      echo "================================================================================"
      echo "[!] SEQUENTIAL ORDER GUARDRAIL BLOCKED OUT-OF-ORDER EXECUTION!"
      echo "    Attempted Step : Page ${req_page_num} (${step_name})"
      echo "    Required Next  : Page ${next_allowed} (page$(printf '%03d' "$next_allowed")_...)"
      echo "    Why Blocked    : Prevents skipping from Page 1 to Page ${req_page_num} before building V1->V9 prerequisites."
      echo "    Live Web Sync  : Alert sent to http://127.0.0.1:8788 & GitHub '${AUTO_BRIDGE_BRANCH}'"
      echo "    Override Option: FORCE_STEP=1 snap_step \"${step_name}\" \"...\""
      echo "================================================================================"
      _post_live_telemetry "GUARDRAIL_BLOCK" "$step_name" "$clean_cmd" "BLOCKED_OUT_OF_ORDER" 2 "$block_msg"
      (
        cd "$AUTO_BRIDGE_REPO_ROOT" 2>/dev/null || exit 0
        git add "$AUTO_BRIDGE_STATE_JSON" 2>/dev/null || true
        git commit -m "Guardrail blocked out-of-order attempt: ${step_name} (requires Page ${next_allowed})" >/dev/null 2>&1 || true
        git push origin "$AUTO_BRIDGE_BRANCH" >/dev/null 2>&1 || true
      )
      return 2
    fi
  fi

  local log_file="$AUTO_BRIDGE_LOG_DIR/${step_name}.log"
  local shot_file="$AUTO_BRIDGE_SHOT_DIR/${step_name}_terminal.png"
  local host_str="$(whoami)@$(hostname)"
  local ts_str="$(date '+%Y-%m-%d %H:%M:%S %Z')"

  {
    echo "# =============================================================================="
    echo "# ENGR 852 Manual Replication Step : ${step_name}"
    echo "# Timestamp                        : ${ts_str}"
    echo "# Host & User                      : ${host_str}"
    echo "# Terminal Environment             : $(_detect_terminal_env)"
    echo "# IP Addresses                     : $(_detect_ip_summary)"
    echo "# Working Directory                : $(pwd)"
    echo "# DISPLAY                          : ${DISPLAY:-<unset>}"
    echo "# Command Executed                 : ${clean_cmd}"
    echo "# =============================================================================="
    echo ""
    echo "\$ ${clean_cmd}"
  } > "$log_file"

  eval "$clean_cmd" > >(tee -a "$log_file") 2> >(tee -a "$log_file" >&2)
  local cmd_exit=$?

  {
    echo ""
    echo "# ------------------------------------------------------------------------------"
    echo "# Exit Code   : ${cmd_exit}"
    echo "# Finished At : $(date '+%Y-%m-%d %H:%M:%S %Z')"
    echo "# ------------------------------------------------------------------------------"
  } >> "$log_file"

  # Render full-height PNG terminal screenshot
  local render_py="$AUTO_BRIDGE_SCRIPT_DIR/render_terminal_screenshot.py"
  if [ -f "$render_py" ]; then
    "$py_bin" "$render_py" \
      --log "$log_file" \
      --out "$shot_file" \
      --title "ENGR 852 Manual Step: ${step_name} (${host_str})" \
      --host "$host_str" \
      --exit-code "$cmd_exit" 2>/dev/null || true
  fi

  local step_status="PASS"
  if [ "$cmd_exit" -ne 0 ]; then
    step_status="FAIL"
  fi

  _post_live_telemetry "STEP_COMPLETE" "$step_name" "$clean_cmd" "$step_status" "$cmd_exit" "Completed ${step_name} (exit=${cmd_exit})"

  # Update STATUS_DASHBOARD.md and push log + screenshot + waveforms + live_state.json to GitHub sub-branch
  (
    cd "$AUTO_BRIDGE_REPO_ROOT" 2>/dev/null || exit 0
    local dash="$AUTO_BRIDGE_PRACTICE_DIR/STATUS_DASHBOARD.md"
    {
      echo "# ENGR 852 Live Manual Replication Status Dashboard (\`${AUTO_BRIDGE_BRANCH}\`)"
      echo ""
      echo "- **Last Updated**: \`$(date '+%Y-%m-%d %H:%M:%S %Z')\`"
      echo "- **Latest Step**: \`${step_name}\` (Status: **${step_status}**, Exit Code: \`${cmd_exit}\`)"
      echo "- **Active Terminal**: \`$(_detect_terminal_env)\` (\`${host_str}\`, IP: \`$(_detect_ip_summary)\`)"
      echo "- **Live Operations Console**: \`http://127.0.0.1:8788/\` | \`http://192.168.1.70:8788/\`"
      echo ""
      echo "## Completed Page Steps (In Sequential Order)"
      echo "| Step / Page ID | Log File | Full Terminal Screenshot |"
      echo "| :--- | :--- | :--- |"
      for lf in $(ls -1 "$AUTO_BRIDGE_LOG_DIR"/*.log 2>/dev/null | sort); do
        local bn="$(basename "$lf" .log)"
        echo "| \`${bn}\` | [logs/${bn}.log](logs/${bn}.log) | [screenshots/${bn}_terminal.png](screenshots/${bn}_terminal.png) |"
      done
    } > "$dash"

    git add "$log_file" "$shot_file" "$dash" "$AUTO_BRIDGE_STATE_JSON" "$AUTO_BRIDGE_WAVE_DIR" 2>/dev/null || true
    git commit -m "Auto-capture ${step_name} (${step_status}, exit=${cmd_exit}) from ${host_str}" >/dev/null 2>&1 || true
    git pull --rebase origin "$AUTO_BRIDGE_BRANCH" >/dev/null 2>&1 || true
    if git push origin "$AUTO_BRIDGE_BRANCH" >/dev/null 2>&1; then
      echo ">>> [AUTO-BRIDGE] Synced log + screenshot + live checklist to Web Console (:8788) & GitHub '${AUTO_BRIDGE_BRANCH}': ${step_name} (${step_status})"
    else
      echo ">>> [AUTO-BRIDGE] Saved locally & updated Web Console (:8788): ${log_file} & ${shot_file}"
    fi
  )

  return $cmd_exit
}

echo "AUTO_BRIDGE_READY: branch=${AUTO_BRIDGE_BRANCH} | live_web=http://127.0.0.1:8788 | order_guard=ACTIVE(Page1->Page100)"
