#!/usr/bin/env python3
"""
ENGR 852 Live Operations, Interactive Study Guide, Midterm Exam Prep & 100-Page Sequential Replication Console
(`http://127.0.0.1:8788/`, `http://192.168.1.70:8788/`, `http://130.212.163.69:8788/`)

Capabilities:
  1. Preserves the exact dark-theme Operations Console structure and all 5 original views while adding:
       - Deeply interactive 6-Box Visual Notebook + Three-Method Study Guide + 2 Interactive Review Questions
         on EVERY single page card (Pages 1..100, V1 -> V9, 200 page-linked questions total).
       - Tab 6: Interactive Study Guide (Foundations F0-F17 from basic electricity/CMOS/math to RTL,
         Lectures 1-11 & HW1-HW4 Three-Method cards) + 4 Live Hardware/Timing Simulators:
           (a) Setup & Hold Slack STA Calculator (with Midterm Q3-Q10 & 520 MHz 14nm ASIC presets)
           (b) 8-Bit (8'hFF) Saturation vs. 16-Bit (16'hFFFF) Full-Precision SAD Calculator
           (c) CMOS RC Delay (tau = R*C) & Dynamic Power (P = alpha*C*V^2*f + P_leak) Lab
           (d) 16-PE Systolic Array Cycle & Memory Address (count = 0..4111) Interactive Stepper
       - Tab 7: Interactive Midterm (Q1-Q10 with high-res 3-page spiral-notebook sheets) & V1-V9 Final Exam Prep.
  2. Enforces the Sequential Order Guardrail (`Page 1 -> Page 2 -> ... -> Page 100`) and syncs live with
     MacBook Air (`zsh`), XQuartz (`DISPLAY=:0`), `926784856@mahmoodi.rcc.at.sfsu.edu`, and GitHub sub-branch
     `manual-practice-macbook-air`.
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
from urllib.parse import urlparse

REPO_ROOT = Path("/Users/huynguyen/Developer/portfolio/motion-estimator-asic-lab-notebook-2026")
PRACTICE_DIR = REPO_ROOT / "practice_from_scratch"
CURRICULUM_JSON = PRACTICE_DIR / "curriculum_100pages.json"
STUDY_JSON = PRACTICE_DIR / "study_guide_and_midterm.json"
LIVE_STATE_JSON = PRACTICE_DIR / "live_state.json"
LOGS_DIR = PRACTICE_DIR / "logs"
SHOTS_DIR = PRACTICE_DIR / "screenshots"
WAVES_DIR = PRACTICE_DIR / "waveforms"
REF_SHOTS_DIR = REPO_ROOT / "evidence" / "screenshots"
SPREADS_DIR = REPO_ROOT / "evidence" / "notebook_spreads"
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


def load_study_guide():
    if STUDY_JSON.exists():
        try:
            return json.loads(STUDY_JSON.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


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
  <title>ENGR 852 | Interactive ASIC Operations Console, Study Guide & Midterm Prep (Pages 1–100)</title>
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
      width: 280px;
      background: #090d16;
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      padding: 18px 14px;
      position: sticky;
      top: 0;
      height: 100vh;
      overflow-y: auto;
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
      flex-shrink: 0;
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
      margin: 16px 6px 8px;
      letter-spacing: 0.8px;
    }
    nav button {
      width: 100%;
      text-align: left;
      background: transparent;
      border: 1px solid transparent;
      color: #cbd5e1;
      padding: 9px 11px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 600;
      cursor: pointer;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
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
      min-height: 58px;
      border-bottom: 1px solid var(--border);
      background: rgba(17, 24, 39, 0.94);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 22px;
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(8px);
      flex-wrap: wrap;
      gap: 10px;
    }
    .top-badges { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
    .pill {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      font-family: var(--mono);
      border: 1px solid var(--border);
      background: #1e293b;
      white-space: nowrap;
    }
    .pill.green { background: rgba(16,185,129,0.15); border-color: #059669; color: #34d399; }
    .pill.blue  { background: rgba(59,130,246,0.15); border-color: #2563eb; color: #60a5fa; }
    .pill.amber { background: rgba(245,158,11,0.15); border-color: #d97706; color: #fbbf24; }
    .pill.red   { background: rgba(239,68,68,0.20); border-color: #dc2626; color: #fca5a5; }
    .pill.purple { background: rgba(139,92,246,0.18); border-color: #7c3aed; color: #c4b5fd; }
    .content { padding: 22px; max-width: 1520px; width: 100%; }
    .grid-4 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(440px, 1fr));
      gap: 16px;
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
      gap: 8px;
    }
    .card .big { font-size: 22px; font-weight: 800; margin: 4px 0 8px; }
    .card .meta { font-size: 12.5px; color: #cbd5e1; font-family: var(--mono); line-height: 1.55; }
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
      word-break: break-word;
      margin: 8px 0;
      line-height: 1.45;
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
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
    .btn.emerald { background: #059669; }
    .btn.amber { background: #d97706; }
    .btn.purple { background: #7c3aed; }
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
      border-radius: 11px;
      padding: 15px 17px;
      margin-bottom: 14px;
    }
    .page-item.done { border-left: 5px solid var(--emerald); }
    .page-item.next { border: 2px solid var(--blue); box-shadow: 0 0 18px rgba(59,130,246,0.22); }
    .page-item.locked { opacity: 0.88; border-left: 4px solid #475569; }
    .page-hdr {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 10px;
      flex-wrap: wrap;
    }
    .page-title { font-weight: 700; font-size: 15px; color: #f8fafc; }
    .subtab-bar {
      display: flex;
      gap: 8px;
      margin: 12px 0 10px;
      border-bottom: 1px solid #1e293b;
      padding-bottom: 8px;
      flex-wrap: wrap;
    }
    .subtab-btn {
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      border-radius: 7px;
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .subtab-btn.active {
      background: rgba(59,130,246,0.22);
      border-color: #3b82f6;
      color: #93c5fd;
    }
    .pipeline-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin: 8px 0;
    }
    .pipe-stage {
      flex: 1;
      min-width: 170px;
      background: #0f172a;
      border: 1px solid #334155;
      border-top: 3px solid var(--blue);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 11.5px;
    }
    .pipe-stage:nth-child(2), .pipe-stage:nth-child(3) { border-top-color: var(--emerald); }
    .pipe-stage:last-child { border-top-color: var(--amber); }
    .method-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .method-box {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 11px 12px;
      font-size: 12.5px;
      line-height: 1.5;
    }
    .method-box h4 {
      margin: 0 0 6px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }
    .method-box.m1 { border-left: 4px solid var(--blue); }
    .method-box.m1 h4 { color: #60a5fa; }
    .method-box.m2 { border-left: 4px solid var(--emerald); }
    .method-box.m2 h4 { color: #34d399; }
    .method-box.m3 { border-left: 4px solid var(--purple); }
    .method-box.m3 h4 { color: #c4b5fd; }
    .quiz-card {
      background: #0f172a;
      border: 1px solid #334155;
      border-radius: 9px;
      padding: 12px 14px;
      margin-top: 10px;
    }
    .quiz-opt {
      display: block;
      width: 100%;
      text-align: left;
      background: #111827;
      border: 1px solid #334155;
      color: #e2e8f0;
      padding: 8px 11px;
      border-radius: 7px;
      margin-top: 6px;
      font-size: 12.5px;
      cursor: pointer;
      transition: 0.15s;
    }
    .quiz-opt:hover { background: #1e293b; border-color: #60a5fa; }
    .quiz-opt.correct {
      background: rgba(16,185,129,0.20);
      border-color: #10b981;
      color: #6ee7b7;
      font-weight: 700;
    }
    .quiz-opt.wrong {
      background: rgba(239,68,68,0.20);
      border-color: #ef4444;
      color: #fca5a5;
    }
    .quiz-explain {
      margin-top: 8px;
      padding: 9px 11px;
      border-radius: 7px;
      background: rgba(16,185,129,0.10);
      border: 1px solid #059669;
      color: #d1fae5;
      font-size: 12px;
      line-height: 1.5;
      display: none;
      white-space: pre-wrap;
    }
    .tbl-verify {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      margin: 8px 0;
    }
    .tbl-verify th, .tbl-verify td {
      border: 1px solid #334155;
      padding: 6px 8px;
      text-align: left;
    }
    .tbl-verify th { background: #1e293b; color: #93c5fd; }
    .tbl-verify tr:nth-child(even) { background: rgba(30,41,59,0.4); }
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
      cursor: zoom-in;
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
    .sim-input-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
      gap: 8px;
      margin: 10px 0;
    }
    .sim-field label {
      display: block;
      font-size: 11px;
      color: var(--muted);
      margin-bottom: 3px;
      font-family: var(--mono);
    }
    .sim-field input, .sim-field select {
      width: 100%;
      background: #050811;
      color: #fff;
      border: 1px solid #334155;
      border-radius: 6px;
      padding: 6px 8px;
      font-family: var(--mono);
      font-size: 12px;
    }
    details summary {
      cursor: pointer;
      color: #93c5fd;
      font-size: 12px;
      font-weight: 600;
      margin-top: 6px;
    }
    /* Modal for full-screen notebook sheet zoom */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.86);
      z-index: 100;
      display: none;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-backdrop img {
      max-width: 96vw;
      max-height: 92vh;
      border-radius: 10px;
      border: 2px solid #60a5fa;
    }
  </style>
</head>
<body>
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">M</div>
      <div>
        ENGR 852 Console
        <small>100-PAGE V1→V9 · STUDY & EXAM</small>
      </div>
    </div>
    <div class="workspace-label">OPERATIONS & REPLICATION</div>
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
      <div class="workspace-label">INTERACTIVE STUDY & EXAM PREP</div>
      <button onclick="switchTab('study', this)">
        <span>6. Study Guide & Simulators</span>
        <span class="pill purple">F0–F17</span>
      </button>
      <button onclick="switchTab('midterm', this)">
        <span>7. Midterm (Q1–Q10) & Exam</span>
        <span id="nav-quiz-score" class="pill emerald">Quiz</span>
      </button>
    </nav>
    <div class="sidebar-bottom">
      <div><span class="dot-online"></span><strong>Sequential Guardrail Active</strong></div>
      <div style="margin-top:4px;">Walks Page 1 → Page 100 (V1 → V9) with integrated 3-Method Study Guide & Midterm Prep.</div>
      <div style="margin-top:6px;font-family:var(--mono);font-size:10.5px;" id="sidebar-ips"></div>
    </div>
  </aside>

  <div class="main">
    <header class="topbar">
      <div>
        <strong>ENGR 852 520 MHz SAED14nm Motion Estimator ASIC</strong>
        <span style="color:var(--muted);margin-left:8px;font-size:13px;">Interactive 100-Page One-Liner, 3-Method Study Guide & Midterm Console</span>
      </div>
      <div class="top-badges">
        <span id="badge-guard" class="pill green">ORDER GUARD: IN-SEQUENCE</span>
        <span id="badge-quiz" class="pill purple">MASTERY QUIZ: 0 ANSWERED</span>
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
            <h3><span>Concept & Midterm Mastery</span><span class="pill purple">F0–F17 · Q1–Q15</span></h3>
            <div class="big" id="card-quiz-big">0 Correct</div>
            <div class="meta">200 Page Review Questions +<br>15 Midterm & V1–V9 Exam Problems</div>
          </div>
          <div class="card">
            <h3><span>MacBook Air + XQuartz X11</span><span class="pill green" id="card-xq-pill">X11 READY</span></h3>
            <div class="big" id="card-mac-ip">192.168.1.70</div>
            <div class="meta" id="card-mac-meta">LAN: http://192.168.1.70:8788<br>VPN: http://130.212.163.69:8788</div>
          </div>
          <div class="card">
            <h3><span>SFSU EDA Server (mahmoodi)</span><span class="pill amber">5 Tools OK</span></h3>
            <div class="big" style="font-size:17px;">926784856@mahmoodi</div>
            <div class="meta" id="card-mahmoodi-meta">Dir: ~/me_asic_new_v1<br>vcs · verdi · fc_shell · icv · pt_shell</div>
          </div>
        </div>

        <!-- Next Required Step Hero Card (Now with Interactive 3-Method & Quiz Preview!) -->
        <div class="next-step-hero" id="next-step-box">
          <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
            <div>
              <span class="pill green" id="next-step-badge">NEXT REQUIRED STEP IN SEQUENCE</span>
              <span class="pill blue" id="next-step-stage" style="margin-left:6px;">V1-PREP</span>
              <span class="pill amber" id="next-step-env" style="margin-left:6px;">MACBOOK</span>
              <h2 style="margin:8px 0 4px;font-size:18px;" id="next-step-title">Loading Page 1...</h2>
              <div style="color:#cbd5e1;font-size:13px;" id="next-step-sub"></div>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              <button class="btn emerald" onclick="copyNextStep()" style="padding:9px 15px;font-size:12.5px;">
                📋 Copy Next Page One-Liner
              </button>
              <button class="btn purple" onclick="openPageInChecklist(STATE.next_required_page || 1)" style="padding:9px 15px;font-size:12.5px;">
                📘 Open Interactive 3-Method Guide & Quiz
              </button>
            </div>
          </div>
          <div class="code-box" id="next-step-cmd"></div>
          <div style="font-size:12px;color:#a7f3d0;font-family:var(--mono);" id="next-step-exp"></div>
          <div class="method-grid" id="next-step-methods"></div>
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

      <!-- TAB 2: 100-PAGE CHECKLIST (With Interactive Sub-Tabs for 1-Liner, 3-Method Guide, & Review Quiz) -->
      <section id="tab-checklist" style="display:none;">
        <div class="card" style="margin-bottom:14px;border-left:4px solid var(--purple);">
          <h3><span>Interactive 100-Page Manual (V1 → V9) + Three-Method Study Guide + 200 Review Questions</span></h3>
          <div class="meta">
            Every page below includes <strong>3 interactive tabs</strong>:
            <code>⚡ 1. One-Liner & 6-Box Notebook</code> (Copy-paste one-liner, terminal dry-run preview, verification table, beginner trap & troubleshooting),
            <code>📘 2. Three-Method Study Guide (Basic → Advanced)</code> (Zero-to-ASIC foundation bridge <code>F0–F17</code> + Method 1 Behavior + Method 2 Math/STA Proof + Method 3 RTL/Hardware), and
            <code>🎯 3. Interactive Review Quiz (2 Questions)</code> (Instant grading & whiteboard explanation!).
          </div>
        </div>
        <div class="filter-bar">
          <input type="text" id="search-input" placeholder="Search Page 1..100, RTL, Verdi, 14nm, DRC, PrimeTime, Setup/Hold..." oninput="renderChecklist()" style="flex:1;min-width:240px;">
          <select id="filter-stage" onchange="renderChecklist()">
            <option value="ALL">All Project Stages (V1 → V9 · Pages 1–100)</option>
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

      <!-- TAB 6: INTERACTIVE STUDY GUIDE (F0-F17, L1-L11, HW1-HW4) & 4 HARDWARE SIMULATORS -->
      <section id="tab-study" style="display:none;">
        <div class="card" style="margin-bottom:18px;border-left:4px solid var(--emerald);">
          <h3><span>ENGR 852 Interactive Hardware & Timing Simulators (From Basic CMOS Electricity to 520 MHz 14nm ASIC)</span></h3>
          <div class="meta">
            Use the 4 interactive calculators below to experiment with <strong>Static Timing Analysis (Setup & Hold Slack)</strong>, <strong>8-Bit vs. 16-Bit SAD Saturation</strong>, <strong>CMOS RC Delay & Dynamic Power</strong>, and the <strong>16-PE Systolic Cycle Schedule (Cycles 0..4111)</strong>. Click any preset button to load exact Midterm or Project scenarios!
          </div>
        </div>

        <div class="grid-2">
          <!-- SIMULATOR 1: STA Setup & Hold Slack Calculator -->
          <div class="card">
            <h3><span>Simulator 1: Static Timing Analysis (Setup & Hold Slack Calculator)</span><span class="pill blue">Midterm Q3–Q10 & 520 MHz ASIC</span></h3>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
              <button class="btn secondary" onclick="loadStaPreset('q4')">Preset: Midterm Q4/Q5 (20ns / -1ns Hold)</button>
              <button class="btn secondary" onclick="loadStaPreset('q9')">Preset: Midterm Q9/Q10 (400MHz / -90ps / -820ps)</button>
              <button class="btn emerald" onclick="loadStaPreset('asic_ss')">Preset: 520MHz 14nm ASIC (SS 0.72V)</button>
              <button class="btn emerald" onclick="loadStaPreset('asic_ff')">Preset: 520MHz 14nm ASIC (FF 0.88V)</button>
            </div>
            <div class="sim-input-row">
              <div class="sim-field"><label>Clock Period T_clk (ps)</label><input type="number" id="sta-tclk" value="1923" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_CQ,max (ps)</label><input type="number" id="sta-tcq-max" value="110" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_logic,max (ps)</label><input type="number" id="sta-tlog-max" value="1453" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_setup,max (ps)</label><input type="number" id="sta-tset" value="60" oninput="calcSta()"></div>
              <div class="sim-field"><label>Setup Skew/Unc (ps)</label><input type="number" id="sta-skew-set" value="80" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_CQ,min (ps)</label><input type="number" id="sta-tcq-min" value="45" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_logic,min (ps)</label><input type="number" id="sta-tlog-min" value="55" oninput="calcSta()"></div>
              <div class="sim-field"><label>T_hold,max (ps)</label><input type="number" id="sta-thold" value="30" oninput="calcSta()"></div>
              <div class="sim-field"><label>Hold Skew (ps)</label><input type="number" id="sta-skew-hold" value="70" oninput="calcSta()"></div>
            </div>
            <div class="code-box" id="sta-result-box"></div>
          </div>

          <!-- SIMULATOR 2: 8-Bit vs 16-Bit SAD Saturation Calculator -->
          <div class="card">
            <h3><span>Simulator 2: 8-Bit (8'hFF) Saturation Trap vs. 16-Bit (16'hFFFF) SAD Lab</span><span class="pill green">V1 Bug → V2 Fix</span></h3>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
              <button class="btn secondary" onclick="loadSadPreset(120, 120, 16)">Preset 1: Exact Match (0000)</button>
              <button class="btn secondary" onclick="loadSadPreset(100, 101, 16)">Preset 2: +1 LSB Offset (0100)</button>
              <button class="btn amber" onclick="loadSadPreset(255, 0, 1)">Preset 3: Max Contrast Row 1 (8-Bit Trap!)</button>
              <button class="btn emerald" onclick="loadSadPreset(255, 0, 16)">Preset 4: Max Contrast Full 16x16 (FF00)</button>
            </div>
            <div class="sim-input-row">
              <div class="sim-field"><label>Ref Pixel R (0..255)</label><input type="number" id="sad-r" min="0" max="255" value="255" oninput="calcSad()"></div>
              <div class="sim-field"><label>Search Pixel S (0..255)</label><input type="number" id="sad-s" min="0" max="255" value="0" oninput="calcSad()"></div>
              <div class="sim-field"><label>Rows Accumulated (1..16)</label><input type="number" id="sad-rows" min="1" max="16" value="16" oninput="calcSad()"></div>
            </div>
            <div class="code-box" id="sad-result-box"></div>
          </div>

          <!-- SIMULATOR 3: CMOS RC Delay & Dynamic Power Calculator -->
          <div class="card">
            <h3><span>Simulator 3: CMOS Physics, RC Delay (τ = R·C) & Power (α·C·V²·f)</span><span class="pill purple">Foundations F7–F12</span></h3>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
              <button class="btn secondary" onclick="loadCmosPreset(0.72, 1.35, 520)">SAED14nm SS (0.72V, -40°C)</button>
              <button class="btn emerald" onclick="loadCmosPreset(0.80, 1.00, 520)">SAED14nm TT (0.80V, 25°C)</button>
              <button class="btn secondary" onclick="loadCmosPreset(0.88, 0.78, 520)">SAED14nm FF (0.88V, 125°C)</button>
            </div>
            <div class="sim-input-row">
              <div class="sim-field"><label>Supply V_DD (Volts)</label><input type="number" step="0.02" id="cmos-vdd" value="0.80" oninput="calcCmos()"></div>
              <div class="sim-field"><label>Eff. R_on (kΩ)</label><input type="number" step="0.05" id="cmos-ron" value="1.00" oninput="calcCmos()"></div>
              <div class="sim-field"><label>Load C_load (fF)</label><input type="number" step="1" id="cmos-cload" value="18" oninput="calcCmos()"></div>
              <div class="sim-field"><label>Clock Freq f (MHz)</label><input type="number" step="10" id="cmos-freq" value="520" oninput="calcCmos()"></div>
              <div class="sim-field"><label>Activity α (0.05..1.0)</label><input type="number" step="0.05" id="cmos-alpha" value="0.20" oninput="calcCmos()"></div>
            </div>
            <div class="code-box" id="cmos-result-box"></div>
          </div>

          <!-- SIMULATOR 4: 16-PE Systolic Cycle & Address Stepper -->
          <div class="card">
            <h3><span>Simulator 4: 16-PE Systolic Cycle & Memory Address Stepper (0..4111)</span><span class="pill amber">control.v Schedule</span></h3>
            <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;">
              <button class="btn secondary" onclick="setCycleStep(0)">Cycle 0 (Start)</button>
              <button class="btn secondary" onclick="setCycleStep(15)">Cycle 15 (16 PEs Active)</button>
              <button class="btn secondary" onclick="setCycleStep(256)">Cycle 256 (0x0100 · PE0 Done)</button>
              <button class="btn secondary" onclick="setCycleStep(271)">Cycle 271 (Row 0 All 16 PEs Done)</button>
              <button class="btn emerald" onclick="setCycleStep(4111)">Cycle 4111 (0x100F · Completed Hold)</button>
            </div>
            <div class="sim-input-row">
              <div class="sim-field" style="grid-column: span 2;">
                <label>Scrub Cycle Counter `count` (0 .. 4111 = 13'h100F)</label>
                <input type="range" id="cyc-slider" min="0" max="4111" value="256" oninput="syncCycleInput(this.value)">
              </div>
              <div class="sim-field">
                <label>Exact Cycle `count`</label>
                <input type="number" id="cyc-num" min="0" max="4111" value="256" oninput="syncCycleSlider(this.value)">
              </div>
            </div>
            <div class="code-box" id="cyc-result-box"></div>
          </div>
        </div>

        <!--Lectures & Homeworks Three-Method Cards -->
        <div class="card" style="margin-bottom:18px;">
          <h3><span>Lectures 1–11 & Homework 1–4 Three-Method Master Guide (Method 1 Behavior · Method 2 Proof · Method 3 RTL)</span></h3>
          <div id="lectures-container"></div>
        </div>

        <!-- Zero-to-Course Foundations F0-F17 -->
        <div class="card">
          <h3><span>Zero-to-ASIC Foundations (F0–F17): Basic Electricity, Electronics, Binary Math & CMOS Logic</span></h3>
          <div id="foundations-container" class="grid-2" style="margin-top:12px;"></div>
        </div>
      </section>

      <!-- TAB 7: INTERACTIVE MIDTERM (Q1-Q10) & V1-V9 EXAM PREP -->
      <section id="tab-midterm" style="display:none;">
        <div class="card" style="margin-bottom:16px;border-left:4px solid var(--blue);">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;">
            <div>
              <h3 style="margin:0;"><span>ENGR 852 Interactive Midterm (Q1–Q10) & V1–V9 Project Exam Center</span></h3>
              <div class="meta" style="margin-top:4px;">
                Includes all <strong>10 actual ENGR 852 Midterm Questions (Q1–Q10)</strong> with your high-resolution <strong>3-page spiral-notebook visual sheets</strong> (click any sheet to zoom full-screen!) + <strong>5 V1–V9 Project Defense Questions (Q11–Q15)</strong>.
              </div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
              <span class="pill green" id="exam-score-pill">Exam Score: 0 / 15</span>
              <button class="btn secondary" onclick="resetQuizScores()">↺ Reset Quiz Answers</button>
            </div>
          </div>
        </div>
        <div id="midterm-container"></div>
      </section>
    </main>
  </div>

  <!-- Full-screen image zoom modal -->
  <div id="img-modal" class="modal-backdrop" onclick="this.classList.remove('open')">
    <img id="img-modal-target" src="" alt="Zoomed Spiral Notebook Sheet">
  </div>

  <script>
    let CURRICULUM = [];
    let STUDY = {};
    let STATE = {};
    let PAGE_SUBTAB = {}; // page_num -> 'exec' | 'study' | 'quiz'
    let QUIZ_ANSWERS = JSON.parse(localStorage.getItem('engr852_quiz_answers') || '{}');

    function zoomImage(url) {
      if (!url) return;
      document.getElementById('img-modal-target').src = url;
      document.getElementById('img-modal').classList.add('open');
    }

    function switchTab(tabId, btn) {
      for (const id of ['overview', 'checklist', 'terminals', 'waveforms', 'github', 'study', 'midterm']) {
        const el = document.getElementById('tab-' + id);
        if (el) el.style.display = (id === tabId) ? 'block' : 'none';
      }
      document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
    }

    function openPageInChecklist(pageNum) {
      PAGE_SUBTAB[pageNum] = 'study';
      const navBtns = document.querySelectorAll('nav button');
      switchTab('checklist', navBtns[1]);
      renderChecklist();
      setTimeout(() => {
        const card = document.getElementById('page-card-' + pageNum);
        if (card) card.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 80);
    }

    function setPageSubtab(pageNum, tabName) {
      PAGE_SUBTAB[pageNum] = tabName;
      renderChecklist();
    }

    function copyText(txt) {
      navigator.clipboard.writeText(txt);
    }

    function copyNextStep() {
      const nextNum = STATE.next_required_page || 1;
      const item = CURRICULUM.find(p => p.page_num === nextNum) || CURRICULUM[0];
      if (item) copyText(item.one_liner);
    }

    function answerQuiz(qKey, chosenIdx, correctIdx) {
      QUIZ_ANSWERS[qKey] = { chosen: chosenIdx, correct: chosenIdx === correctIdx };
      localStorage.setItem('engr852_quiz_answers', JSON.stringify(QUIZ_ANSWERS));
      updateQuizBadges();
      renderChecklist();
      renderMidtermBank();
    }

    function resetQuizScores() {
      QUIZ_ANSWERS = {};
      localStorage.removeItem('engr852_quiz_answers');
      updateQuizBadges();
      renderChecklist();
      renderMidtermBank();
    }

    function updateQuizBadges() {
      const vals = Object.values(QUIZ_ANSWERS);
      const totalAns = vals.length;
      const totalRight = vals.filter(v => v.correct).length;
      document.getElementById('badge-quiz').textContent = `MASTERY QUIZ: ${totalRight}/${totalAns} CORRECT`;
      document.getElementById('card-quiz-big').textContent = `${totalRight} Correct (${totalAns} Tried)`;
      document.getElementById('nav-quiz-score').textContent = `${totalRight}✓`;

      const examRight = Object.entries(QUIZ_ANSWERS)
        .filter(([k, v]) => k.startsWith('exam_') && v.correct).length;
      const ep = document.getElementById('exam-score-pill');
      if (ep) ep.textContent = `Exam Score: ${examRight} / 15`;
    }

    async function refreshAll() {
      try {
        if (CURRICULUM.length === 0) {
          const cr = await fetch('/api/curriculum');
          CURRICULUM = await cr.json();
        }
        if (!STUDY.foundations) {
          const st = await fetch('/api/study');
          STUDY = await st.json();
          renderStudyGuide();
          renderMidtermBank();
          calcSta();
          calcSad();
          calcCmos();
          setCycleStep(256);
        }
        const sr = await fetch('/api/state');
        STATE = await sr.json();
        updateQuizBadges();
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
        const tm = nextItem.three_methods || {};
        document.getElementById('next-step-methods').innerHTML = `
          <div class="method-box m1"><h4>Method 1 · Understand Behavior</h4>${tm.method1 || ''}</div>
          <div class="method-box m2"><h4>Method 2 · Prove It (Math / STA)</h4>${tm.method2 || ''}</div>
          <div class="method-box m3"><h4>Method 3 · Think in RTL & Hardware</h4>${tm.method3 || ''}</div>
        `;
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
          <img src="${donePages[0].screenshot_file}?t=${Date.now()}" onclick="zoomImage('${donePages[0].screenshot_file}')" style="max-width:100%;border-radius:8px;border:1px solid #334155;cursor:zoom-in;">
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
          ${w.img_url ? `<img src="${w.img_url}" alt="${w.title}" onclick="zoomImage('${w.img_url}')">` : ''}
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

    function escapeHtml(s) {
      return String(s || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
    }

    function toggleDryRun(pnum) {
      const el = document.getElementById('dryrun-box-' + pnum);
      if (el) el.style.display = (el.style.display === 'none') ? 'block' : 'none';
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
        if (q && !(
          p.title.toLowerCase().includes(q) ||
          p.one_liner.toLowerCase().includes(q) ||
          p.step_id.toLowerCase().includes(q) ||
          (p.foundation_text || '').toLowerCase().includes(q)
        )) return false;
        return true;
      });

      document.getElementById('checklist-container').innerHTML = filtered.map(p => {
        const rec = doneMap[String(p.page_num)];
        const isDone = rec && rec.status === 'PASS';
        const isNext = p.page_num === nextNum;
        const cls = isDone ? 'done' : (isNext ? 'next' : 'locked');
        const activeSub = PAGE_SUBTAB[p.page_num] || 'exec';

        const statusBadge = isDone
          ? `<span class="pill green">✓ COMPLETED (PASS · ${rec.updated_at})</span>`
          : (isNext
              ? `<span class="pill blue">▶ NEXT REQUIRED STEP (RUN NOW)</span>`
              : `<span class="pill amber">🔒 LOCKED (Complete Page ${p.page_num - 1} First)</span>`);

        // Count quiz questions answered on this page
        const qList = p.quiz_questions || [];
        let qCorrectCount = 0;
        qList.forEach((_, qi) => {
          const a = QUIZ_ANSWERS[`p${p.page_num}_q${qi}`];
          if (a && a.correct) qCorrectCount++;
        });

        // Pipeline stages HTML
        const pipeHtml = (p.pipeline_stages || []).map(st => `
          <div class="pipe-stage">
            <strong style="color:#f8fafc;display:block;margin-bottom:3px;">${escapeHtml(st.title)}</strong>
            <span style="color:#94a3b8;">${(st.items || []).map(escapeHtml).join(' · ')}</span>
          </div>
        `).join('');

        // Verification Table HTML
        const rows = p.table_rows || [];
        const tblHtml = rows.length ? `
          <table class="tbl-verify">
            <thead><tr>${rows[0].map(c => `<th>${escapeHtml(c)}</th>`).join('')}</tr></thead>
            <tbody>
              ${rows.slice(1).map(r => `<tr>${r.map(c => `<td>${escapeHtml(c)}</td>`).join('')}</tr>`).join('')}
            </tbody>
          </table>
        ` : '';

        // Subtab 1: Execution & 6-Box Notebook
        const execView = `
          <div class="pipeline-row">${pipeHtml}</div>
          <div style="margin:6px 0;font-size:11.5px;color:#fbbf24;font-weight:700;">
            Box 5 · Combined Copy-Paste Page ${p.page_num} One-Liner (${escapeHtml(p.where_badge)}):
          </div>
          <div class="code-box">${escapeHtml(p.one_liner)}</div>
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div style="font-size:11.5px;color:#a7f3d0;font-family:var(--mono);">
              Expected Output: ${escapeHtml((p.expected_out || [])[0] || '')}
            </div>
            <button class="btn secondary" onclick="toggleDryRun(${p.page_num})">▶ Simulate / Preview Full Terminal Output</button>
          </div>
          <div id="dryrun-box-${p.page_num}" class="code-box" style="display:none;color:#38bdf8;border-color:#0284c7;">
# === INTERACTIVE TERMINAL PREVIEW FOR PAGE ${p.page_num} (${escapeHtml(p.step_id)}) ===
$ ${escapeHtml(p.one_liner)}
${(p.expected_out || []).map(escapeHtml).join('\n')}
# Exit Code   : 0 (PASS -> Unlocks Page ${Math.min(100, p.page_num + 1)})
          </div>
          <details>
            <summary>Show Box 2 Verification Table, Box 3 Beginner Trap, Box 4 Line-by-Line Code & Box 6 Troubleshooting</summary>
            <div style="margin-top:8px;">
              <strong style="color:#93c5fd;font-size:12px;">Box 2 · Hardware-to-Verilog / Command-to-Action Verification Table:</strong>
              ${tblHtml}
              <div style="background:rgba(239,68,68,0.12);border:1px solid #dc2626;border-radius:7px;padding:8px 11px;margin:8px 0;font-size:12px;color:#fecaca;">
                <strong>Box 3 · [!] Critical Engineering Note / Beginner Trap:</strong><br>
                ${(p.trap_notes || []).map(escapeHtml).join('<br>')}
              </div>
              <strong style="color:#93c5fd;font-size:12px;">Box 4 · Line-by-Line Commented Code & Individual Terminal Commands:</strong>
              <div class="code-box" style="color:#cbd5e1;">${escapeHtml((p.code_block || p.individual_commands || []).join('\n'))}</div>
              <div style="background:rgba(245,158,11,0.12);border:1px solid #d97706;border-radius:7px;padding:8px 11px;margin:8px 0;font-size:12px;color:#fde68a;">
                <strong>Box 6 · Live Verification Checks & Fallback Troubleshooting (If XYZ Fails → Option A / B):</strong><br>
                ${(p.fallback_notes || []).map(escapeHtml).join('<br>')}
              </div>
            </div>
            ${isDone && rec ? `
              <div style="margin-top:8px;">
                <strong style="color:#34d399;">Captured Live Terminal Output (${escapeHtml(rec.step_id)}.log):</strong>
                <div class="code-box" style="color:#f8fafc;">${escapeHtml(rec.log_excerpt || '')}</div>
                ${rec.screenshot_file ? `<img src="${rec.screenshot_file}?t=${Date.now()}" onclick="zoomImage('${rec.screenshot_file}')" style="max-width:100%;border-radius:8px;border:1px solid #334155;margin-top:6px;cursor:zoom-in;">` : ''}
              </div>
            ` : ''}
          </details>
        `;

        // Subtab 2: Three-Method Study Guide (Basic -> Advanced)
        const tm = p.three_methods || {};
        const studyView = `
          <div style="background:rgba(139,92,246,0.12);border:1px solid #7c3aed;border-radius:8px;padding:10px 12px;margin-bottom:10px;font-size:12.5px;line-height:1.5;">
            <span class="pill purple">${escapeHtml(p.foundation_ref || 'F0–F17 Foundation')}</span>
            <div style="margin-top:6px;color:#e2e8f0;">${escapeHtml(p.foundation_text || '')}</div>
          </div>
          <div class="method-grid">
            <div class="method-box m1">
              <h4>Method 1 — Understand Behavior (Plain Words & Trace)</h4>
              ${escapeHtml(tm.method1 || '')}
            </div>
            <div class="method-box m2">
              <h4>Method 2 — Prove It (Math / Table / STA Timing)</h4>
              <div style="white-space:pre-wrap;">${escapeHtml(tm.method2 || '')}</div>
            </div>
            <div class="method-box m3">
              <h4>Method 3 — Think in RTL & 14nm Hardware</h4>
              ${escapeHtml(tm.method3 || '')}
            </div>
          </div>
          <div style="margin-top:10px;">
            <strong style="color:#93c5fd;font-size:12px;">Command & Signal Meaning Breakdown for Page ${p.page_num}:</strong>
            <div class="code-box" style="color:#e2e8f0;">${escapeHtml((p.cmd_explanations || []).join('\n'))}</div>
          </div>
        `;

        // Subtab 3: Interactive Review Quiz (2 Questions per Page)
        const quizView = qList.map((qObj, qi) => {
          const qKey = `p${p.page_num}_q${qi}`;
          const saved = QUIZ_ANSWERS[qKey];
          return `
            <div class="quiz-card">
              <div style="font-weight:700;font-size:13px;color:#93c5fd;">
                Question ${qi + 1} of ${qList.length} · ${escapeHtml(qObj.q)}
              </div>
              ${(qObj.options || []).map((opt, oi) => {
                let optCls = 'quiz-opt';
                if (saved) {
                  if (oi === qObj.answer) optCls += ' correct';
                  else if (oi === saved.chosen && !saved.correct) optCls += ' wrong';
                }
                return `<button class="${optCls}" onclick="answerQuiz('${qKey}', ${oi}, ${qObj.answer})">${escapeHtml(opt)}</button>`;
              }).join('')}
              <div class="quiz-explain" style="display:${saved ? 'block' : 'none'};">
                <strong>${saved && saved.correct ? '✓ CORRECT!' : '✗ REVIEW STEP-BY-STEP PROOF:'}</strong> ${escapeHtml(qObj.explain)}
              </div>
            </div>
          `;
        }).join('');

        return `
          <div class="page-item ${cls}" id="page-card-${p.page_num}">
            <div class="page-hdr">
              <div>
                ${statusBadge}
                <span class="pill blue" style="margin-left:6px;">${escapeHtml(p.v_stage)}</span>
                <span class="pill secondary" style="margin-left:6px;">${escapeHtml(p.env_tag)}</span>
                <span class="pill purple" style="margin-left:6px;">Quiz: ${qCorrectCount}/${qList.length}✓</span>
                <div class="page-title" style="margin-top:6px;">${escapeHtml(p.title)}</div>
                <div style="font-size:12px;color:var(--muted);">${escapeHtml(p.subtitle)}</div>
              </div>
              <button class="btn ${isNext ? 'emerald' : ''}" onclick='copyText(${JSON.stringify(p.one_liner)})'>
                📋 Copy Page ${p.page_num} One-Liner
              </button>
            </div>

            <div class="subtab-bar">
              <button class="subtab-btn ${activeSub === 'exec' ? 'active' : ''}" onclick="setPageSubtab(${p.page_num}, 'exec')">
                ⚡ 1. One-Liner & 6-Box Notebook
              </button>
              <button class="subtab-btn ${activeSub === 'study' ? 'active' : ''}" onclick="setPageSubtab(${p.page_num}, 'study')">
                📘 2. Three-Method Study Guide (Basic → Advanced)
              </button>
              <button class="subtab-btn ${activeSub === 'quiz' ? 'active' : ''}" onclick="setPageSubtab(${p.page_num}, 'quiz')">
                🎯 3. Interactive Review Quiz (${qCorrectCount}/${qList.length}✓)
              </button>
            </div>

            <div style="display:${activeSub === 'exec' ? 'block' : 'none'};">${execView}</div>
            <div style="display:${activeSub === 'study' ? 'block' : 'none'};">${studyView}</div>
            <div style="display:${activeSub === 'quiz' ? 'block' : 'none'};">${quizView}</div>
          </div>
        `;
      }).join('');
    }

    // === TAB 6: SIMULATORS & STUDY GUIDE RENDERING ===
    function loadStaPreset(name) {
      const setVal = (id, v) => { document.getElementById(id).value = v; };
      if (name === 'q4') {
        // Midterm Q4/Q5: T_clk=20000ps (20ns), Tcq_max=6000, Tlog_max=10000 (2 gates * 5ns), Tset=3000, Skew=1000; Hold: Tcq_min=2000, Tlog_min=0 (B[0]=A[1]), Thold=2000, Skew=1000
        setVal('sta-tclk', 20000); setVal('sta-tcq-max', 6000); setVal('sta-tlog-max', 10000);
        setVal('sta-tset', 3000); setVal('sta-skew-set', 1000);
        setVal('sta-tcq-min', 2000); setVal('sta-tlog-min', 0); setVal('sta-thold', 2000); setVal('sta-skew-hold', 1000);
      } else if (name === 'q9') {
        // Midterm Q9/Q10: 400 MHz -> 2500 ps; Tcq_max=950, Tlog_max=210+200+180=590, Tset=300, Skew=750; Hold P4: Tcq_min=300, Tlog_min=30, Thold=400, Skew=750
        setVal('sta-tclk', 2500); setVal('sta-tcq-max', 950); setVal('sta-tlog-max', 590);
        setVal('sta-tset', 300); setVal('sta-skew-set', 750);
        setVal('sta-tcq-min', 300); setVal('sta-tlog-min', 30); setVal('sta-thold', 400); setVal('sta-skew-hold', 750);
      } else if (name === 'asic_ss') {
        // 520 MHz (1923 ps) SAED14nm SS 0.72V corner (+220 ps setup slack, 0 ps hold slack)
        setVal('sta-tclk', 1923); setVal('sta-tcq-max', 110); setVal('sta-tlog-max', 1453);
        setVal('sta-tset', 60); setVal('sta-skew-set', 80);
        setVal('sta-tcq-min', 45); setVal('sta-tlog-min', 55); setVal('sta-thold', 30); setVal('sta-skew-hold', 70);
      } else if (name === 'asic_ff') {
        // 520 MHz (1923 ps) SAED14nm FF 0.88V corner (+710 ps setup slack, 0 ps hold slack)
        setVal('sta-tclk', 1923); setVal('sta-tcq-max', 75); setVal('sta-tlog-max', 1018);
        setVal('sta-tset', 40); setVal('sta-skew-set', 80);
        setVal('sta-tcq-min', 35); setVal('sta-tlog-min', 55); setVal('sta-thold', 20); setVal('sta-skew-hold', 70);
      }
      calcSta();
    }

    function calcSta() {
      const tclk = Number(document.getElementById('sta-tclk').value || 0);
      const tcqMax = Number(document.getElementById('sta-tcq-max').value || 0);
      const tlogMax = Number(document.getElementById('sta-tlog-max').value || 0);
      const tset = Number(document.getElementById('sta-tset').value || 0);
      const skewSet = Number(document.getElementById('sta-skew-set').value || 0);
      const tcqMin = Number(document.getElementById('sta-tcq-min').value || 0);
      const tlogMin = Number(document.getElementById('sta-tlog-min').value || 0);
      const thold = Number(document.getElementById('sta-thold').value || 0);
      const skewHold = Number(document.getElementById('sta-skew-hold').value || 0);

      const tminSetup = tcqMax + tlogMax + tset + skewSet;
      const setupSlack = tclk - tminSetup;
      const fmaxMhz = tminSetup > 0 ? (1000000 / tminSetup).toFixed(2) : '0';
      const fcurMhz = tclk > 0 ? (1000000 / tclk).toFixed(2) : '0';

      const holdArr = tcqMin + tlogMin;
      const holdReq = thold + skewHold;
      const holdSlack = holdArr - holdReq;

      document.getElementById('sta-result-box').textContent =
`[1] SETUP CHECK (Slowest Max Path vs. Next Clock Edge T_clk = ${tclk} ps [${fcurMhz} MHz]):
    T_req,setup = T_CQ,max (${tcqMax}) + T_logic,max (${tlogMax}) + T_setup (${tset}) + T_skew (${skewSet}) = ${tminSetup} ps
    Setup Slack = T_clk (${tclk}) - T_req,setup (${tminSetup}) = ${setupSlack >= 0 ? '+' : ''}${setupSlack} ps  --> ${setupSlack >= 0 ? '✓ SETUP PASS' : '✗ SETUP VIOLATION!'}
    Fastest Allowed Period T_min = ${tminSetup} ps (${(tminSetup/1000).toFixed(3)} ns)  =>  f_max = ${fmaxMhz} MHz

[2] HOLD CHECK (Fastest Min Path vs. Same Clock Edge — Independent of T_clk!):
    Min Arrival = T_CQ,min (${tcqMin}) + T_logic,min (${tlogMin}) = ${holdArr} ps
    Hold Window = T_hold,max (${thold}) + T_skew (${skewHold}) = ${holdReq} ps
    Hold Slack  = ${holdArr} - ${holdReq} = ${holdSlack >= 0 ? '+' : ''}${holdSlack} ps  --> ${holdSlack >= 0 ? '✓ HOLD PASS' : '✗ HOLD VIOLATION (Add >= ' + Math.abs(holdSlack) + ' ps delay buffer)!'}`;
    }

    function loadSadPreset(r, s, rows) {
      document.getElementById('sad-r').value = r;
      document.getElementById('sad-s').value = s;
      document.getElementById('sad-rows').value = rows;
      calcSad();
    }

    function calcSad() {
      const r = Math.min(255, Math.max(0, Number(document.getElementById('sad-r').value || 0)));
      const s = Math.min(255, Math.max(0, Number(document.getElementById('sad-s').value || 0)));
      const rows = Math.min(16, Math.max(1, Number(document.getElementById('sad-rows').value || 1)));
      const diff = Math.abs(r - s);
      const pixels = rows * 16;
      const trueSad = pixels * diff;
      const sad8 = Math.min(255, trueSad);
      const hex8 = '0x' + sad8.toString(16).toUpperCase().padStart(2, '0');
      const hex16 = '0x' + trueSad.toString(16).toUpperCase().padStart(4, '0');
      const cmp8 = sad8 < 255;
      const cmp16 = trueSad < 65535;

      document.getElementById('sad-result-box').textContent =
`Per-Pixel |R - S| = |${r} - ${s}| = ${diff}   |   Pixels Accumulated = ${rows} rows * 16 = ${pixels} pixels
Mathematical True SAD = ${pixels} * ${diff} = ${trueSad} (${hex16})

• V1 8-Bit Baseline (rtl/8bit/top.v, Init BestDist = 8'hFF [255]):
  Accumulate[7:0] = ${sad8} (${hex8}) ${trueSad > 255 ? '[SATURATED AT 8\'hFF!]' : '[No Overflow]'}
  comp.v Strict '<' Check (${hex8} < 0xFF): ${cmp8 ? '1 -> newBest=1 (Latches motionX/Y)' : '0 -> newBest=0 (FAILS! motionX/Y remain xx!)'}

• V2–V9 16-Bit Upgrade (rtl/16bit/top.v, Init BestDist = 16'hFFFF [65,535]):
  Accumulate[15:0] = ${trueSad} (${hex16}) [100% Exact Full Precision]
  comp.v Strict '<' Check (${hex16} < 0xFFFF): ${cmp16 ? '1 -> newBest=1 (PASS! Latches exact motionX/motionY)' : '0'}`;
    }

    function loadCmosPreset(vdd, ron, freq) {
      document.getElementById('cmos-vdd').value = vdd;
      document.getElementById('cmos-ron').value = ron;
      document.getElementById('cmos-freq').value = freq;
      calcCmos();
    }

    function calcCmos() {
      const vdd = Number(document.getElementById('cmos-vdd').value || 0.8);
      const ron = Number(document.getElementById('cmos-ron').value || 1.0); // kOhm
      const cload = Number(document.getElementById('cmos-cload').value || 18); // fF
      const freq = Number(document.getElementById('cmos-freq').value || 520); // MHz
      const alpha = Number(document.getElementById('cmos-alpha').value || 0.2);

      // tau = R (10^3) * C (10^-15) = R*C * 10^-12 s = R*C ps
      const tauPs = (ron * cload).toFixed(2);
      const tpdPs = (0.69 * ron * cload).toFixed(2);
      // Energy per switching cycle E = C * V^2 (fJ)
      const energyFj = (cload * vdd * vdd).toFixed(2);
      // Dynamic power across 8,230 cells: P_dyn = N_cells * alpha * C * V^2 * f
      const pDynMw = (8230 * alpha * cload * 1e-15 * vdd * vdd * freq * 1e6 * 1e3).toFixed(3);

      document.getElementById('cmos-result-box').textContent =
`[1] RC Gate & Interconnect Delay (F9: τ = R_on · C_load):
    τ_RC = ${ron} kΩ * ${cload} fF = ${tauPs} ps   |   50% Propagation Delay t_p ≈ 0.69·τ = ${tpdPs} ps

[2] Dynamic Switching Energy & 8,230-Cell Chip Power (F10: P_dyn = α · C_total · V_DD² · f):
    Energy per 0→1→0 Gate Cycle (C·V_DD²) = ${energyFj} fJ
    Estimated 8,230-Cell Core Dynamic Power at ${freq} MHz (V_DD = ${vdd}V, α = ${alpha}) = ${pDynMw} mW`;
    }

    function setCycleStep(val) {
      document.getElementById('cyc-slider').value = val;
      document.getElementById('cyc-num').value = val;
      renderCycleStep(val);
    }
    function syncCycleInput(val) {
      document.getElementById('cyc-num').value = val;
      renderCycleStep(Number(val));
    }
    function syncCycleSlider(val) {
      const c = Math.min(4111, Math.max(0, Number(val || 0)));
      document.getElementById('cyc-slider').value = c;
      renderCycleStep(c);
    }

    function renderCycleStep(count) {
      const hexCount = '13\'h' + count.toString(16).toUpperCase().padStart(4, '0');
      const addrR = count & 0xFF;
      const colJ = count & 0xF;
      const rowI = (count >> 4) & 0xF;
      const searchV = (count >> 8) & 0xF;
      const activePes = Math.min(16, count + 1);
      const completed = count >= 4111;
      const timeNs = (count * 1.923).toFixed(2);

      document.getElementById('cyc-result-box').textContent =
`Cycle count = ${count} (${hexCount})   |   Physical Elapsed Time @ 520 MHz = ${timeNs} ns
• Reference AddressR[7:0] = 8'h${addrR.toString(16).toUpperCase().padStart(2,'0')} (Pixel Row i=${rowI}, Col j=${colJ} of 16x16 Ref Block)
• Vertical Search Row v   = ${searchV} (Displacement dy = ${searchV - 8})
• Active Systolic PEs     = ${activePes} / 16 PEs (${activePes === 16 ? 'Full 16-PE Pipeline Operating in Parallel!' : 'Filling Rpipe[0..14] Shift Register'})
• Completion Hold Flag    = Completed = ${completed ? '1\'b1 (Cycle 4111 Freeze Active -> BestDist, motionX, motionY Latched!)' : '1\'b0 (Searching...)'}`;
    }

    function renderStudyGuide() {
      const lecs = STUDY.lectures_and_homeworks || [];
      document.getElementById('lectures-container').innerHTML = lecs.map(l => `
        <div class="page-item" style="margin-top:10px;">
          <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
            <div>
              <span class="pill blue">${escapeHtml(l.tag)}</span>
              <span class="pill green" style="margin-left:6px;">${escapeHtml(l.pages_linked)}</span>
              <div class="page-title" style="margin-top:5px;">${escapeHtml(l.title)}</div>
            </div>
          </div>
          <div class="method-grid">
            <div class="method-box m1"><h4>Method 1 · Understand Behavior</h4>${escapeHtml(l.method1)}</div>
            <div class="method-box m2"><h4>Method 2 · Prove It (Math / Table)</h4>${escapeHtml(l.method2)}</div>
            <div class="method-box m3"><h4>Method 3 · Think in RTL & Hardware</h4>${escapeHtml(l.method3)}</div>
          </div>
        </div>
      `).join('');

      const fnds = STUDY.foundations || [];
      document.getElementById('foundations-container').innerHTML = fnds.map(f => `
        <div class="card" style="background:#0f172a;">
          <h3><span>${escapeHtml(f.id)} · ${escapeHtml(f.category)}</span></h3>
          <div style="font-weight:700;font-size:14px;color:#f8fafc;margin-bottom:6px;">${escapeHtml(f.title)}</div>
          <div style="font-size:12.5px;color:#cbd5e1;line-height:1.5;">${escapeHtml(f.basic_concept)}</div>
          <div class="code-box" style="font-size:11.5px;padding:8px;">${escapeHtml(f.equation)}</div>
          <div style="font-size:12px;color:#93c5fd;line-height:1.45;"><strong>14nm Project & Exam Link:</strong> ${escapeHtml(f.asic_connection)}</div>
        </div>
      `).join('');
    }

    function renderMidtermBank() {
      const bank = STUDY.midterm_and_exam_bank || [];
      document.getElementById('midterm-container').innerHTML = bank.map((qObj, idx) => {
        const qKey = `exam_${qObj.id}`;
        const saved = QUIZ_ANSWERS[qKey];
        const linkedBtns = (qObj.linked_pages || []).map(pn =>
          `<button class="btn secondary" style="padding:4px 9px;font-size:11px;" onclick="openPageInChecklist(${pn})">↗ Jump to Page ${pn}</button>`
        ).join(' ');

        return `
          <div class="page-item ${saved && saved.correct ? 'done' : ''}">
            <div class="page-hdr">
              <div>
                <span class="pill blue">${escapeHtml(qObj.id)} · ${escapeHtml(qObj.source)}</span>
                <span class="pill purple" style="margin-left:6px;">${escapeHtml(qObj.topic)}</span>
                ${saved ? (saved.correct ? '<span class="pill green" style="margin-left:6px;">✓ SOLVED</span>' : '<span class="pill red" style="margin-left:6px;">✗ REVIEW</span>') : ''}
              </div>
              <div style="display:flex;gap:6px;flex-wrap:wrap;">${linkedBtns}</div>
            </div>

            <div class="code-box" style="color:#f8fafc;font-size:13px;margin-top:10px;">${escapeHtml(qObj.prompt)}</div>

            <div style="margin-top:8px;">
              ${(qObj.options || []).map((opt, oi) => {
                let optCls = 'quiz-opt';
                if (saved) {
                  if (oi === qObj.correct_index) optCls += ' correct';
                  else if (oi === saved.chosen && !saved.correct) optCls += ' wrong';
                }
                return `<button class="${optCls}" onclick="answerQuiz('${qKey}', ${oi}, ${qObj.correct_index})">${escapeHtml(opt)}</button>`;
              }).join('')}
            </div>

            <div class="quiz-explain" style="display:${saved ? 'block' : 'none'};">
              <strong>✓ Official Answer & Step-by-Step Whiteboard Proof:</strong>\n${escapeHtml(qObj.short_answer)}\n\n${escapeHtml(qObj.whiteboard_proof)}
              ${qObj.rtl_fix ? `\n\n<strong>Synthesizable Verilog / STA Implementation:</strong>\n${escapeHtml(qObj.rtl_fix)}` : ''}
            </div>

            ${qObj.sheet_img ? `
              <details style="margin-top:10px;" ${saved ? 'open' : ''}>
                <summary>📓 View 3-Page Spiral-Notebook Visual Solution Sheet for ${escapeHtml(qObj.id)} (Click Image to Zoom Full-Screen)</summary>
                <img src="${qObj.sheet_img}" alt="${escapeHtml(qObj.id)} Spiral Notebook Sheet" onclick="zoomImage('${qObj.sheet_img}')" style="width:100%;border-radius:9px;border:1px solid #334155;margin-top:8px;cursor:zoom-in;">
              </details>
            ` : ''}
          </div>
        `;
      }).join('');
    }

    refreshAll();
    setInterval(refreshAll, 3500);
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
        if path == "/api/study":
            self._send_json(load_study_guide())
            return
        if path == "/api/state":
            self._send_json(build_merged_state())
            return
        if path.startswith("/files/"):
            rel = path[len("/files/"):]
            if rel.startswith("ref_screenshots/"):
                target = REF_SHOTS_DIR / rel[len("ref_screenshots/"):]
            elif rel.startswith("spreads/"):
                target = SPREADS_DIR / rel[len("spreads/"):]
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
    (PRACTICE_DIR / "index.html").write_text(INDEX_HTML, encoding="utf-8")

    t = threading.Thread(target=background_git_and_remote_sync, daemon=True)
    t.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), ConsoleRequestHandler)
    ips = get_local_ips()
    print("ENGR852_LIVE_CONSOLE_LISTENING:")
    print(f"  Local URL : http://127.0.0.1:{PORT}/")
    print(f"  LAN URL   : http://{ips['lan']}:{PORT}/")
    print(f"  VPN URL   : http://{ips['vpn']}:{PORT}/")
    server.serve_forever()


if __name__ == "__main__":
    main()
