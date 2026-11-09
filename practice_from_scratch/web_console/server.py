#!/usr/bin/env python3
"""
ENGR 852 Live Operations & 100-Page Sequential Replication Console (`http://127.0.0.1:8788/`)
Modeled after the user's Mac Awareness | Operations Console (`http://127.0.0.1:8769/`).

Capabilities:
  1. Binds on 0.0.0.0:8788 so it is accessible from:
       - This Mac:        http://127.0.0.1:8788/
       - MacBook Air LAN: http://192.168.1.70:8788/
       - SFSU VPN IP:     http://130.212.163.69:8788/
  2. Syncs all 100 Page One-Liners (`Page 1` .. `Page 100`, walking V1 -> V9) and enforces
     the Sequential Order Guardrail (`Page 1 -> Page 2 -> ... -> Page 100`), preventing
     accidental jumps from Page 1 to Page 100.
  3. Visually mirrors live terminal state across:
       - MacBook Air Local Terminal (`zsh`)
       - XQuartz X11 Terminal (`xterm` / `DISPLAY=:0` / `localhost:10.0`)
       - SFSU EDA Server (`926784856@mahmoodi.rcc.at.sfsu.edu`)
  4. Syncs Verdi nWave waveforms (`V9_fig7` .. `V9_fig12`) and 14nm physical layouts
     (`v9_signoff_clean_layout.png`) from the main project & live practice runs.
  5. Syncs live state with GitHub sub-branch `manual-practice-macbook-air`
     (`practice_from_scratch/live_state.json` & `practice_from_scratch/STATUS_DASHBOARD.md`).
"""

import json
import mimetypes
import os
import socket
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO_ROOT = Path("/Users/huynguyen/Developer/portfolio/motion-estimator-asic-lab-notebook-2026")
PRACTICE_DIR = REPO_ROOT / "practice_from_scratch"
CURRICULUM_JSON = PRACTICE_DIR / "curriculum_100pages.json"
LIVE_STATE_JSON = PRACTICE_DIR / "live_state.json"
LOGS_DIR = PRACTICE_DIR / "logs"
SHOTS_DIR = PRACTICE_DIR / "screenshots"
WAVES_DIR = PRACTICE_DIR / "waveforms"
REF_SHOTS_DIR = REPO_ROOT / "evidence" / "screenshots"
PORT = int(os.environ.get("ENGR852_CONSOLE_PORT", "8788"))

STATE_LOCK = threading.Lock()


def get_local_ips():
    ips = {"loopback": "127.0.0.1", "lan": "192.168.1.70", "vpn": "130.212.163.69"}
    try:
        out = subprocess.check_output(["ifconfig"], text=True, timeout=2)
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                addr = line.split()[1]
                if addr.startswith("192.168.") or addr.startswith("10."):
                    ips["lan"] = addr
                elif addr.startswith("130.212."):
                    ips["vpn"] = addr
    except Exception:
        pass
    return ips


def get_xquartz_status():
    display_env = os.environ.get("DISPLAY", "")
    x11_sock = Path("/tmp/.X11-unix/X0").exists()
    xq_running = False
    try:
        res = subprocess.run(["pgrep", "-f", "XQuartz"], capture_output=True, text=True, timeout=1.5)
        xq_running = res.returncode == 0
    except Exception:
        pass
    return {
        "running": xq_running or x11_sock,
        "socket_active": x11_sock,
        "display": display_env or ("/private/tmp/com.apple.launchd/org.xquartz:0" if x11_sock else ":0"),
    }


def load_curriculum():
    if CURRICULUM_JSON.exists():
        try:
            return json.loads(CURRICULUM_JSON.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def build_merged_state():
    with STATE_LOCK:
        state = {
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "epoch": time.time(),
            "active_terminal": "MACBOOK_AIR_TERMINAL",
            "host": socket.gethostname(),
            "user": os.environ.get("USER", "huynguyen"),
            "ip_addresses": get_local_ips(),
            "xquartz": get_xquartz_status(),
            "mahmoodi": {
                "account": "926784856@mahmoodi.rcc.at.sfsu.edu",
                "workspace": "~/me_asic_new_v1",
                "tools": ["vcs", "verdi", "fc_shell", "icv", "pt_shell"],
            },
            "github": {
                "repo": "huynguyen1017/motion-estimator-asic-lab-notebook-2026",
                "branch": "manual-practice-macbook-air",
                "last_commit": "",
            },
            "guardrail_alert": "",
            "completed_pages": {},
            "terminal_feed": [],
        }
        if LIVE_STATE_JSON.exists():
            try:
                saved = json.loads(LIVE_STATE_JSON.read_text(encoding="utf-8"))
                if isinstance(saved, dict):
                    state["active_terminal"] = saved.get("active_terminal", state["active_terminal"])
                    state["guardrail_alert"] = saved.get("guardrail_alert", "")
                    state["completed_pages"] = saved.get("completed_pages", {})
                    state["terminal_feed"] = saved.get("terminal_feed", [])
                    state["mahmoodi"]["last_pwd"] = saved.get("pwd", "~/me_asic_new_v1")
                    state["mahmoodi"]["last_host"] = saved.get("host", "mahmoodi.rcc.at.sfsu.edu")
            except Exception:
                pass

        # Scan logs directory so any pageNNN_*.log is reflected immediately
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        for lf in sorted(LOGS_DIR.glob("page*.log")):
            sname = lf.stem
            if len(sname) >= 7 and sname[:4] == "page" and sname[4:7].isdigit():
                pnum = int(sname[4:7])
                txt = lf.read_text(encoding="utf-8", errors="ignore")
                ec = 0
                for ln in txt.splitlines():
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
                    "log_file": f"/files/logs/{lf.name}",
                    "screenshot_file": f"/files/screenshots/{sname}_terminal.png"
                    if (SHOTS_DIR / f"{sname}_terminal.png").exists()
                    else "",
                    "log_excerpt": "\n".join(txt.splitlines()[-22:]),
                    "updated_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(lf.stat().st_mtime)),
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

        try:
            git_out = subprocess.check_output(
                ["git", "-C", str(REPO_ROOT), "log", "-n", "1", "--oneline"],
                text=True,
                timeout=1.5,
            ).strip()
            state["github"]["last_commit"] = git_out
        except Exception:
            pass

        # Waveform & Layout Gallery items (Reference V9 vs Live Captured)
        gallery_specs = [
            {
                "id": "fig7",
                "page_num": 49,
                "stage": "V1 / V5",
                "title": "Fig 7: 8-Bit Baseline Row-1 Saturation (count = 0x00F9..0x0110)",
                "desc": "PE0..PE15 Accumulate[7:0] clamps at 8'hFF (255); strict '<' comparator (8'hFF < 8'hFF) fails -> newBest=0.",
                "tcl_cmd": "verdi -ssf waves_sat.fsdb -play scripts/verdi_nwave/fig7_orig8bit_row1.tcl",
                "filename": "V9_fig7_orig8bit_row1_nWave.png",
            },
            {
                "id": "fig8",
                "page_num": 50,
                "stage": "V1 / V5",
                "title": "Fig 8: 8-Bit Baseline Terminal Cycle 4111 (t = 7,905.45 ns)",
                "desc": "At count=13'h100F, BestDist remains 8'hFF and motionX/motionY remain unupdated ('xx').",
                "tcl_cmd": "verdi -ssf waves_hold.fsdb -play scripts/verdi_nwave/fig8_orig8bit_complete.tcl",
                "filename": "V9_fig8_orig8bit_complete_nWave.png",
            },
            {
                "id": "fig10",
                "page_num": 51,
                "stage": "V3 / V5",
                "title": "Fig 10: 16-Bit Exact Match (BestDist = 16'h0000 at 520 MHz)",
                "desc": "Candidate progression 0909 -> 07C7 -> 0000 in top_tb_direct.v; latches motionX=07 (+7), motionY=F8 (-8).",
                "tcl_cmd": "verdi -ssf waves_reg.fsdb -play scripts/verdi_nwave/fig10_16bit_0000.tcl",
                "filename": "V9_fig10_16bit_perfect_match_0000_nWave.png",
            },
            {
                "id": "fig11",
                "page_num": 51,
                "stage": "V3 / V5",
                "title": "Fig 11: 16-Bit +1 LSB Offset Match (BestDist = 16'h0100, X=FB [-5], Y=07 [+7])",
                "desc": "Resolves 256*1 = 256 (16'h0100) without 8-bit saturation and latches exact target (-5, +7).",
                "tcl_cmd": "verdi -ssf waves_reg.fsdb -play scripts/verdi_nwave/fig11_16bit_0100.tcl",
                "filename": "V9_fig11_16bit_offset1_0100_nWave.png",
            },
            {
                "id": "fig9",
                "page_num": 52,
                "stage": "V4 / V5",
                "title": "Fig 9: 16-Bit Max-Contrast Row-1 Progression (BestDist = 16'hFF00 < 16'hFFFF)",
                "desc": "Accumulates 256*255 = 65,280 (16'hFF00) < 16'hFFFF initial BestDist -> newBest=1 at count=0x0100.",
                "tcl_cmd": "verdi -ssf waves_sat.fsdb -play scripts/verdi_nwave/fig9_16bit_sat_row1.tcl",
                "filename": "V9_fig9_16bit_saturation_row1_nWave.png",
            },
            {
                "id": "layout",
                "page_num": 62,
                "stage": "V8 / V9",
                "title": "SAED14nm FinFET Routed Chip Layout (125.07 x 62.80 um, 0/242 ICV DRC CLEAN)",
                "desc": "8,230 standard cells (449 FFs, 0 SRAM macros), M1..M9 routing, +0.71/+0.54/+0.22 ns 3-corner PrimeTime STA.",
                "tcl_cmd": "fc_shell -gui -f v9_closure/capture_layout_gui.tcl",
                "filename": "v9_signoff_clean_layout.png",
            },
        ]
        for g in gallery_specs:
            fn = g["filename"]
            live_f = WAVES_DIR / fn
            ref_f = REF_SHOTS_DIR / fn
            g["live_captured"] = live_f.exists() or (str(g["page_num"]) in state["completed_pages"])
            g["img_url"] = f"/files/waveforms/{fn}" if live_f.exists() else (f"/files/ref_screenshots/{fn}" if ref_f.exists() else "")
        state["waveform_gallery"] = gallery_specs
        return state


def background_git_and_remote_sync():
    """Periodically pulls new logs/screenshots/live_state.json pushed from MacBook Air or mahmoodi."""
    while True:
        time.sleep(6)
        try:
            subprocess.run(
                ["git", "-C", str(REPO_ROOT), "fetch", "origin", "manual-practice-macbook-air"],
                capture_output=True,
                timeout=4,
            )
            # Check if remote branch is ahead
            local_rev = subprocess.check_output(
                ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True, timeout=2
            ).strip()
            remote_rev = subprocess.check_output(
                ["git", "-C", str(REPO_ROOT), "rev-parse", "origin/manual-practice-macbook-air"],
                text=True,
                timeout=2,
            ).strip()
            if local_rev != remote_rev:
                subprocess.run(
                    ["git", "-C", str(REPO_ROOT), "pull", "--rebase", "origin", "manual-practice-macbook-air"],
                    capture_output=True,
                    timeout=5,
                )
        except Exception:
            pass


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>ENGR 852 | Mac & ASIC Operations Console (Pages 1–100)</title>
  <style>
    :root {
      --bg: #0b1120;
      --panel: #111827;
      --panel-alt: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --muted: #94a3b8;
      --blue: #3b82f6;
      --emerald: #10b981;
      --amber: #f59e0b;
      --red: #ef4444;
      --purple: #8b5cf6;
      --mono: "SFMono-Regular", Menlo, Monaco, Consolas, monospace;
      --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: var(--sans);
      background: var(--bg);
      color: var(--text);
      display: flex;
      min-height: 100vh;
    }
    .sidebar {
      width: 265px;
      background: #090d16;
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 18px 14px;
      position: sticky;
      top: 0;
      height: 100vh;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 11px;
      font-weight: 700;
      font-size: 15px;
      letter-spacing: 0.3px;
      padding-bottom: 16px;
      border-bottom: 1px solid #1e293b;
    }
    .brand-icon {
      width: 34px;
      height: 34px;
      border-radius: 9px;
      background: linear-gradient(135deg, #2563eb, #10b981);
      display: grid;
      place-items: center;
      font-weight: 800;
      color: #fff;
    }
    .brand small {
      display: block;
      font-size: 10px;
      color: var(--muted);
      font-weight: 600;
      margin-top: 2px;
    }
    .workspace-label {
      font-size: 10.5px;
      font-weight: 700;
      color: var(--muted);
      margin: 18px 6px 8px;
      letter-spacing: 0.8px;
    }
    nav button {
      width: 100%;
      text-align: left;
      background: transparent;
      border: 1px solid transparent;
      color: #cbd5e1;
      padding: 10px 12px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    nav button:hover { background: #1e293b; color: #fff; }
    nav button.active {
      background: rgba(37, 99, 235, 0.18);
      border-color: #2563eb;
      color: #60a5fa;
    }
    .sidebar-bottom {
      margin-top: auto;
      padding-top: 14px;
      border-top: 1px solid #1e293b;
      font-size: 11.5px;
      color: var(--muted);
    }
    .dot-online {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--emerald);
      margin-right: 6px;
      box-shadow: 0 0 8px var(--emerald);
    }
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .topbar {
      height: 58px;
      border-bottom: 1px solid var(--border);
      background: rgba(17, 24, 39, 0.92);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 22px;
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(8px);
    }
    .top-badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .pill {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11.5px;
      font-weight: 700;
      font-family: var(--mono);
      border: 1px solid var(--border);
      background: #1e293b;
    }
    .pill.green { background: rgba(16,185,129,0.15); border-color: #059669; color: #34d399; }
    .pill.blue  { background: rgba(59,130,246,0.15); border-color: #2563eb; color: #60a5fa; }
    .pill.amber { background: rgba(245,158,11,0.15); border-color: #d97706; color: #fbbf24; }
    .pill.red   { background: rgba(239,68,68,0.20); border-color: #dc2626; color: #fca5a5; }
    .content { padding: 22px; max-width: 1480px; width: 100%; }
    .grid-4 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 11px;
      padding: 15px 16px;
    }
    .card h3 {
      margin: 0 0 8px;
      font-size: 12.5px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .card .big { font-size: 23px; font-weight: 800; margin: 4px 0 8px; }
    .card .meta { font-size: 12px; color: #cbd5e1; font-family: var(--mono); line-height: 1.5; }
    .alert-banner {
      background: rgba(239, 68, 68, 0.16);
      border: 2px solid var(--red);
      border-radius: 11px;
      padding: 14px 18px;
      margin-bottom: 18px;
      display: none;
    }
    .alert-banner.visible { display: block; }
    .next-step-hero {
      background: linear-gradient(135deg, rgba(16,185,129,0.14), rgba(37,99,235,0.14));
      border: 2px solid var(--emerald);
      border-radius: 12px;
      padding: 16px 18px;
      margin-bottom: 20px;
    }
    .code-box {
      background: #050811;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 11px 13px;
      font-family: var(--mono);
      font-size: 12px;
      color: #a7f3d0;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-all;
      margin: 8px 0;
    }
    .btn {
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 7px;
      padding: 7px 13px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .btn.emerald { background: #059669; }
    .btn.secondary { background: #334155; }
    .btn:hover { opacity: 0.92; }
    .filter-bar {
      display: flex;
      gap: 10px;
      margin-bottom: 14px;
      flex-wrap: wrap;
      align-items: center;
    }
    .filter-bar input, .filter-bar select {
      background: #0f172a;
      color: #fff;
      border: 1px solid var(--border);
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 13px;
    }
    .page-item {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      margin-bottom: 11px;
    }
    .page-item.done { border-left: 5px solid var(--emerald); }
    .page-item.next { border: 2px solid var(--blue); box-shadow: 0 0 16px rgba(59,130,246,0.22); }
    .page-item.locked { opacity: 0.78; border-left: 4px solid #475569; }
    .page-hdr {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .page-title { font-weight: 700; font-size: 14.5px; color: #f8fafc; }
    .wave-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(410px, 1fr));
      gap: 16px;
    }
    .wave-card {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 11px;
      padding: 14px;
    }
    .wave-card img {
      width: 100%;
      border-radius: 7px;
      border: 1px solid #334155;
      margin-top: 8px;
      background: #000;
    }
    .term-feed {
      background: #050811;
      border: 1px solid #334155;
      border-radius: 10px;
      padding: 14px;
      font-family: var(--mono);
      font-size: 12px;
      max-height: 440px;
      overflow-y: auto;
    }
    .feed-row {
      padding: 6px 0;
      border-bottom: 1px dashed #1e293b;
    }
    details summary {
      cursor: pointer;
      color: #93c5fd;
      font-size: 12px;
      font-weight: 600;
      margin-top: 6px;
    }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">M</div>
      <div>
        ENGR 852 Console
        <small>MAC AWARENESS · 100-PAGE SYNC</small>
      </div>
    </div>
    <div class="workspace-label">OPERATIONS VIEWS</div>
    <nav>
      <button class="active" onclick="switchTab('overview', this)">
        <span>1. Overview & Order Guard</span>
        <span id="nav-prog" class="pill blue">0/100</span>
      </button>
      <button onclick="switchTab('checklist', this)">
        <span>2. 100-Page One-Liners</span>
        <span class="pill green">V1→V9</span>
      </button>
      <button onclick="switchTab('terminals', this)">
        <span>3. Live Terminal Mirror</span>
        <span class="pill amber">SSH/X11</span>
      </button>
      <button onclick="switchTab('waveforms', this)">
        <span>4. Verdi Waveforms & Layout</span>
        <span class="pill blue">6 Figs</span>
      </button>
      <button onclick="switchTab('github', this)">
        <span>5. GitHub Sub-Branch Sync</span>
        <span class="pill green">Live</span>
      </button>
    </nav>
    <div class="sidebar-bottom">
      <div><span class="dot-online"></span><strong>Sequential Guardrail Active</strong></div>
      <div style="margin-top:6px;">Prevents skipping Page 1 → Page 100 out of order.</div>
      <div style="margin-top:6px;font-family:var(--mono);font-size:10.5px;" id="sidebar-ips"></div>
    </div>
  </aside>

  <div class="main">
    <header class="topbar">
      <div>
        <strong>ENGR 852 520 MHz SAED14nm Motion Estimator ASIC</strong>
        <span style="color:var(--muted);margin-left:8px;font-size:13px;">Live 100-Page One-Liner & Terminal Sync Console</span>
      </div>
      <div class="top-badges">
        <span id="badge-guard" class="pill green">ORDER GUARD: IN-SEQUENCE</span>
        <span id="badge-term" class="pill blue">TERM: MACBOOK / MAHMOODI</span>
        <span id="badge-gh" class="pill amber">BRANCH: manual-practice-macbook-air</span>
        <button class="btn secondary" onclick="refreshAll()">↻ Sync Now</button>
      </div>
    </header>

    <main class="content">
      <!-- Out-of-order guardrail alert -->
      <div id="guardrail-banner" class="alert-banner">
        <h3 style="margin:0 0 6px;color:#fca5a5;">[!] SEQUENTIAL ORDER GUARDRAIL BLOCKED AN OUT-OF-ORDER COMMAND!</h3>
        <div id="guardrail-msg" style="font-family:var(--mono);font-size:12.5px;"></div>
      </div>

      <!-- TAB 1: OVERVIEW -->
      <section id="tab-overview">
        <div class="grid-4">
          <div class="card">
            <h3><span>Sequential Progress (V1 → V9)</span><span class="pill green" id="card-stage-pill">V1-PREP</span></h3>
            <div class="big" id="card-prog-big">0 / 100 Pages</div>
            <div class="meta" id="card-prog-meta">Next Required Step: Page 1</div>
          </div>
          <div class="card">
            <h3><span>MacBook Air Local Terminal</span><span class="pill blue">zsh</span></h3>
            <div class="big" id="card-mac-ip">192.168.1.70</div>
            <div class="meta" id="card-mac-meta">Console: http://127.0.0.1:8788<br>LAN: http://192.168.1.70:8788</div>
          </div>
          <div class="card">
            <h3><span>XQuartz X11 + GlobalProtect VPN</span><span class="pill green" id="card-xq-pill">X11 READY</span></h3>
            <div class="big" id="card-vpn-ip">130.212.163.69</div>
            <div class="meta" id="card-xq-meta">DISPLAY=:0 -> localhost:10.0<br>VPN Console: http://130.212.163.69:8788</div>
          </div>
          <div class="card">
            <h3><span>SFSU EDA Server (mahmoodi)</span><span class="pill amber">5 Tools OK</span></h3>
            <div class="big" style="font-size:17px;">926784856@mahmoodi</div>
            <div class="meta" id="card-mahmoodi-meta">Dir: ~/me_asic_new_v1<br>vcs · verdi · fc_shell · icv · pt_shell</div>
          </div>
        </div>

        <!-- Next Required Step Hero Card -->
        <div class="next-step-hero" id="next-step-box">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
            <div>
              <span class="pill green" id="next-step-badge">NEXT REQUIRED STEP IN SEQUENCE</span>
              <span class="pill blue" id="next-step-stage" style="margin-left:6px;">V1-PREP</span>
              <span class="pill amber" id="next-step-env" style="margin-left:6px;">MACBOOK</span>
              <h2 style="margin:8px 0 4px;font-size:18px;" id="next-step-title">Loading Page 1...</h2>
              <div style="color:#cbd5e1;font-size:13px;" id="next-step-sub"></div>
            </div>
            <button class="btn emerald" onclick="copyNextStep()" style="padding:10px 16px;font-size:13px;">
              📋 Copy Next Page One-Liner
            </button>
          </div>
          <div class="code-box" id="next-step-cmd"></div>
          <div style="font-size:12px;color:#a7f3d0;font-family:var(--mono);" id="next-step-exp"></div>
        </div>

        <!-- Live Terminal Activity & Latest Screenshot -->
        <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:16px;">
          <div class="card">
            <h3><span>Live Terminal Execution Feed (MacBook Air · XQuartz · mahmoodi)</span></h3>
            <div class="term-feed" id="overview-feed"></div>
          </div>
          <div class="card">
            <h3><span>Latest Auto-Captured Terminal Screenshot</span><span class="pill green" id="latest-shot-lbl"> PNG </span></h3>
            <div id="latest-shot-wrap" style="text-align:center;color:var(--muted);padding:12px;">
              Run Page 1 one-liner to capture your first live terminal screenshot!
            </div>
          </div>
        </div>
      </section>

      <!-- TAB 2: 100-PAGE CHECKLIST -->
      <section id="tab-checklist" style="display:none;">
        <div class="filter-bar">
          <input type="text" id="search-input" placeholder="Search Page 1..100, RTL, Verdi, 14nm, DRC, PrimeTime..." oninput="renderChecklist()" style="flex:1;min-width:240px;">
          <select id="filter-stage" onchange="renderChecklist()">
            <option value="ALL">All Project Stages (V1 → V9)</option>
            <option value="V1">V1: Setup, Theory & 8-Bit Baseline Trap (Pages 1–28)</option>
            <option value="V2">V2: 16-Bit Non-Saturating RTL & Hold Fix (Pages 29–32)</option>
            <option value="V3">V3: 520 MHz 0000 & 0100 Testbenches (Pages 33–38)</option>
            <option value="V4">V4: FF00 & SV Self-Checking Testbenches (Pages 39–44)</option>
            <option value="V5">V5: VCS & Verdi nWave Waveform Capture (Pages 45–52)</option>
            <option value="V6">V6: 520 MHz SDC, Synthesis & Floorplan (Pages 53–58)</option>
            <option value="V7">V7: CTS, Routing & Merged GDSII (Pages 59–61)</option>
            <option value="V8">V8: Layout GUI, 0/242 DRC & 3-Corner STA (Pages 62–64)</option>
            <option value="V9">V9: Final Workbook, Python & GitHub Sign-Off (Pages 65–100)</option>
          </select>
          <select id="filter-status" onchange="renderChecklist()">
            <option value="ALL">All Statuses (100 Pages)</option>
            <option value="NEXT">Next Required Step</option>
            <option value="PASS">Completed (PASS)</option>
            <option value="LOCKED">Locked (Pending Earlier Pages)</option>
          </select>
        </div>
        <div id="checklist-container"></div>
      </section>

      <!-- TAB 3: LIVE TERMINAL MIRROR -->
      <section id="tab-terminals" style="display:none;">
        <div class="card" style="margin-bottom:16px;">
          <h3><span>How Your Terminals Connect & Sync With This Console</span></h3>
          <div class="meta">
            • <strong>MacBook Air Local Terminal (zsh)</strong> & <strong>XQuartz xterm</strong>: Sourcing <code>practice_from_scratch/scripts/auto_bridge.sh</code> hooks <code>snap_step</code>, <code>status_now</code>, and <code>remote_status</code> directly to <code>http://192.168.1.70:8788/api/telemetry</code> and GitHub <code>manual-practice-macbook-air</code>.<br>
            • <strong>University EDA Server (926784856@mahmoodi.rcc.at.sfsu.edu)</strong>: Automatically loads <code>auto_bridge.sh</code> from <code>~/.bashrc</code>, exports all 5 Synopsys tools in <code>bash</code>, and pushes every executed page log + PNG screenshot to <code>manual-practice-macbook-air</code>.
          </div>
        </div>
        <div class="card">
          <h3><span>Full Live Terminal Stream & Command History</span></h3>
          <div class="term-feed" id="full-term-feed" style="max-height:620px;"></div>
        </div>
      </section>

      <!-- TAB 4: WAVEFORMS & LAYOUT GALLERY -->
      <section id="tab-waveforms" style="display:none;">
        <div class="card" style="margin-bottom:16px;">
          <h3><span>How the Main Project Captured Waveforms & Layouts (And How Pages 45–64 Sync Them Here)</span></h3>
          <div class="meta">
            In <code>~/ENGR852_Project/22_v9_clean_verdi_waveforms/</code> and <code>20_v5b_520MHz_14nm_cts_area_fix/v9_closure/</code>, Synopsys VCS generates the 520 MHz FSDB waveform dumps (<code>waves_sat.fsdb</code>, <code>waves_hold.fsdb</code>, <code>waves_reg.fsdb</code>) and Synopsys Verdi nWave replays the automated TCL scripts (<code>fig7_orig8bit_row1.tcl</code> .. <code>fig12_16bit_ff00.tcl</code>) over XQuartz/Xvfb X11 to capture crisp hexadecimal waveforms. Running the one-liners on <strong>Pages 49–52 & Page 62</strong> automatically syncs these exact waveforms into <code>practice_from_scratch/waveforms/</code>!
          </div>
        </div>
        <div class="wave-grid" id="waveform-grid"></div>
      </section>

      <!-- TAB 5: GITHUB SUB-BRANCH SYNC -->
      <section id="tab-github" style="display:none;">
        <div class="card">
          <h3><span>GitHub Sub-Branch Live Status (manual-practice-macbook-air)</span></h3>
          <div class="meta" id="gh-details" style="margin-bottom:12px;"></div>
          <a class="btn emerald" href="https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026/tree/manual-practice-macbook-air/practice_from_scratch" target="_blank" style="text-decoration:none;display:inline-block;">
            ↗ Open GitHub Sub-Branch (manual-practice-macbook-air)
          </a>
        </div>
      </section>
    </main>
  </div>

  <script>
    let CURRICULUM = [];
    let STATE = {};

    function switchTab(tabId, btn) {
      for (const id of ['overview', 'checklist', 'terminals', 'waveforms', 'github']) {
        document.getElementById('tab-' + id).style.display = (id === tabId) ? 'block' : 'none';
      }
      document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    function copyText(txt) {
      navigator.clipboard.writeText(txt);
    }

    function copyNextStep() {
      const nextNum = STATE.next_required_page || 1;
      const item = CURRICULUM.find(p => p.page_num === nextNum) || CURRICULUM[0];
      if (item) copyText(item.one_liner);
    }

    async function refreshAll() {
      try {
        if (CURRICULUM.length === 0) {
          const cr = await fetch('/api/curriculum');
          CURRICULUM = await cr.json();
        }
        const sr = await fetch('/api/state');
        STATE = await sr.json();
        renderUI();
      } catch (e) {
        console.error(e);
      }
    }

    function renderUI() {
      const doneCount = STATE.total_passed_pages || 0;
      const nextNum = STATE.next_required_page || 1;
      document.getElementById('nav-prog').textContent = `${doneCount}/100`;
      document.getElementById('card-prog-big').textContent = `${doneCount} / 100 Pages`;
      document.getElementById('card-prog-meta').textContent = `Highest In-Order: Page ${STATE.highest_sequential_page || 0} · Next Required: Page ${nextNum}`;

      const ips = STATE.ip_addresses || {};
      document.getElementById('card-mac-ip').textContent = ips.lan || '192.168.1.70';
      document.getElementById('card-vpn-ip').textContent = ips.vpn || '130.212.163.69';
      document.getElementById('sidebar-ips').innerHTML = `Local: http://127.0.0.1:8788<br>LAN: http://${ips.lan || '192.168.1.70'}:8788<br>VPN: http://${ips.vpn || '130.212.163.69'}:8788`;

      // Guardrail alert
      const gb = document.getElementById('guardrail-banner');
      const badgeGuard = document.getElementById('badge-guard');
      if (STATE.guardrail_alert) {
        gb.classList.add('visible');
        document.getElementById('guardrail-msg').textContent = STATE.guardrail_alert;
        badgeGuard.className = 'pill red';
        badgeGuard.textContent = 'ORDER GUARD: OUT-OF-ORDER BLOCKED!';
      } else {
        gb.classList.remove('visible');
        badgeGuard.className = 'pill green';
        badgeGuard.textContent = `ORDER GUARD: PAGE ${nextNum} READY`;
      }

      // Next step hero
      const nextItem = CURRICULUM.find(p => p.page_num === nextNum) || CURRICULUM[0];
      if (nextItem) {
        document.getElementById('card-stage-pill').textContent = nextItem.v_stage;
        document.getElementById('next-step-badge').textContent = `NEXT REQUIRED STEP: PAGE ${nextItem.page_num} OF 100`;
        document.getElementById('next-step-stage').textContent = nextItem.v_stage;
        document.getElementById('next-step-env').textContent = nextItem.env_tag;
        document.getElementById('next-step-title').textContent = nextItem.title;
        document.getElementById('next-step-sub').textContent = `${nextItem.subtitle} — (${nextItem.where_badge})`;
        document.getElementById('next-step-cmd').textContent = nextItem.one_liner;
        document.getElementById('next-step-exp').textContent = `Expected Output: ${(nextItem.expected_out || [])[0] || ''}`;
      }

      // Terminal feeds
      const feed = (STATE.terminal_feed || []).slice().reverse();
      const feedHtml = feed.length ? feed.map(f => `
        <div class="feed-row">
          <span class="pill ${f.status === 'PASS' ? 'green' : (f.status === 'BLOCKED_OUT_OF_ORDER' ? 'red' : 'blue')}">${f.status}</span>
          <strong style="color:#93c5fd;margin-left:6px;">[${f.time}] ${f.terminal}</strong>
          <span style="color:#94a3b8;">(${f.host} · IP: ${f.ip || ''} · DISPLAY: ${f.display || ':0'})</span>
          <div style="color:#e2e8f0;margin-top:4px;">$ ${f.command}</div>
          ${f.message ? `<div style="color:#fbbf24;margin-top:2px;">→ ${f.message}</div>` : ''}
        </div>
      `).join('') : '<div style="color:var(--muted);">Waiting for Page 1 execution from MacBook Air, XQuartz, or mahmoodi...</div>';
      document.getElementById('overview-feed').innerHTML = feedHtml;
      document.getElementById('full-term-feed').innerHTML = feedHtml;

      // Latest screenshot
      const donePages = Object.values(STATE.completed_pages || {}).sort((a, b) => b.page_num - a.page_num);
      if (donePages.length && donePages[0].screenshot_file) {
        document.getElementById('latest-shot-lbl').textContent = donePages[0].step_id;
        document.getElementById('latest-shot-wrap').innerHTML = `
          <img src="${donePages[0].screenshot_file}?t=${Date.now()}" style="max-width:100%;border-radius:8px;border:1px solid #334155;">
        `;
      }

      // Waveform gallery
      const wgrid = document.getElementById('waveform-grid');
      wgrid.innerHTML = (STATE.waveform_gallery || []).map(w => `
        <div class="wave-card">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="pill blue">Page ${w.page_num} · ${w.stage}</span>
            <span class="pill ${w.live_captured ? 'green' : 'amber'}">${w.live_captured ? 'SYNCED TO SUB-BRANCH' : 'REFERENCE V9 TARGET'}</span>
          </div>
          <h4 style="margin:8px 0 4px;">${w.title}</h4>
          <div style="font-size:12px;color:#cbd5e1;margin-bottom:6px;">${w.desc}</div>
          <div class="code-box" style="font-size:11px;padding:7px;">${w.tcl_cmd}</div>
          ${w.img_url ? `<img src="${w.img_url}" alt="${w.title}">` : ''}
        </div>
      `).join('');

      // GitHub details
      document.getElementById('gh-details').innerHTML = `
        Repository: <strong>${(STATE.github || {}).repo}</strong><br>
        Active Sub-Branch: <strong>${(STATE.github || {}).branch}</strong> (Main branch remains 100% untouched)<br>
        Latest Commit: <code>${(STATE.github || {}).last_commit || 'N/A'}</code><br>
        Completed Pages Logged: <strong>${doneCount} / 100</strong>
      `;

      renderChecklist();
    }

    function renderChecklist() {
      const q = (document.getElementById('search-input').value || '').toLowerCase();
      const stg = document.getElementById('filter-stage').value;
      const sts = document.getElementById('filter-status').value;
      const nextNum = STATE.next_required_page || 1;
      const doneMap = STATE.completed_pages || {};

      const filtered = CURRICULUM.filter(p => {
        const isDone = doneMap[String(p.page_num)] && doneMap[String(p.page_num)].status === 'PASS';
        const isNext = p.page_num === nextNum;
        if (stg !== 'ALL' && !p.v_stage.startsWith(stg)) return false;
        if (sts === 'PASS' && !isDone) return false;
        if (sts === 'NEXT' && !isNext) return false;
        if (sts === 'LOCKED' && (isDone || isNext)) return false;
        if (q && !(p.title.toLowerCase().includes(q) || p.one_liner.toLowerCase().includes(q) || p.step_id.toLowerCase().includes(q))) return false;
        return true;
      });

      document.getElementById('checklist-container').innerHTML = filtered.map(p => {
        const rec = doneMap[String(p.page_num)];
        const isDone = rec && rec.status === 'PASS';
        const isNext = p.page_num === nextNum;
        const cls = isDone ? 'done' : (isNext ? 'next' : 'locked');
        const statusBadge = isDone
          ? `<span class="pill green">✓ COMPLETED (PASS · ${rec.updated_at})</span>`
          : (isNext
              ? `<span class="pill blue">▶ NEXT REQUIRED STEP (RUN NOW)</span>`
              : `<span class="pill amber">🔒 LOCKED (Complete Page ${p.page_num - 1} First)</span>`);

        return `
          <div class="page-item ${cls}">
            <div class="page-hdr">
              <div>
                ${statusBadge}
                <span class="pill blue" style="margin-left:6px;">${p.v_stage}</span>
                <span class="pill secondary" style="margin-left:6px;">${p.env_tag}</span>
                <div class="page-title" style="margin-top:6px;">${p.title}</div>
                <div style="font-size:12px;color:var(--muted);">${p.subtitle}</div>
              </div>
              <button class="btn ${isNext ? 'emerald' : ''}" onclick='copyText(${JSON.stringify(p.one_liner)})'>
                📋 Copy Page ${p.page_num} One-Liner
              </button>
            </div>
            <div class="code-box">${p.one_liner}</div>
            <div style="font-size:11.5px;color:#a7f3d0;font-family:var(--mono);">
              Expected Output: ${(p.expected_out || [])[0] || ''}
            </div>
            <details>
              <summary>Show Individual Smaller Commands on Page ${p.page_num} ${isDone ? ' + Captured Log & Terminal Screenshot' : ''}</summary>
              <div class="code-box" style="color:#cbd5e1;margin-top:6px;">${(p.individual_commands || []).join('\n') || 'See Section 4 of Page ' + p.page_num}</div>
              ${isDone && rec ? `
                <div style="margin-top:8px;">
                  <strong>Captured Terminal Output (${rec.step_id}.log):</strong>
                  <div class="code-box" style="color:#f8fafc;">${rec.log_excerpt || ''}</div>
                  ${rec.screenshot_file ? `<img src="${rec.screenshot_file}?t=${Date.now()}" style="max-width:100%;border-radius:8px;border:1px solid #334155;margin-top:6px;">` : ''}
                </div>
              ` : ''}
            </details>
          </div>
        `;
      }).join('');
    }

    refreshAll();
    setInterval(refreshAll, 3000);
  </script>
</body>
</html>
"""


class ConsoleRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/curriculum":
            self._send_json(load_curriculum())
            return
        if path == "/api/state":
            self._send_json(build_merged_state())
            return
        if path.startswith("/files/"):
            rel = path[len("/files/"):]
            if rel.startswith("ref_screenshots/"):
                target = REF_SHOTS_DIR / rel[len("ref_screenshots/"):]
            else:
                target = PRACTICE_DIR / rel
            target = target.resolve()
            if target.exists() and target.is_file():
                ctype, _ = mimetypes.guess_type(str(target))
                data = target.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", ctype or "application/octet-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
        self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/telemetry":
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            try:
                incoming = json.loads(raw.decode("utf-8", errors="ignore"))
                with STATE_LOCK:
                    LIVE_STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
                    LIVE_STATE_JSON.write_text(json.dumps(incoming, indent=2), encoding="utf-8")
                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, status=400)
            return
        self.send_error(404, "Not Found")


def main():
    PRACTICE_DIR.mkdir(parents=True, exist_ok=True)
    # Also write static index.html into practice_from_scratch/ so GitHub sub-branch has the web UI
    (PRACTICE_DIR / "index.html").write_text(INDEX_HTML, encoding="utf-8")

    t = threading.Thread(target=background_git_and_remote_sync, daemon=True)
    t.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), ConsoleRequestHandler)
    ips = get_local_ips()
    print(f"ENGR852_LIVE_CONSOLE_LISTENING:")
    print(f"  Local URL : http://127.0.0.1:{PORT}/")
    print(f"  LAN URL   : http://{ips['lan']}:{PORT}/")
    print(f"  VPN URL   : http://{ips['vpn']}:{PORT}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
