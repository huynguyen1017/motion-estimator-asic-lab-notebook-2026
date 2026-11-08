#!/usr/bin/env python3
"""
Builds the 100-Page Visual Engineering Notebook Baby-Steps SOP Guide (.pdf + .md)
and High-Resolution 3-Page Visual Notebook Spread Images (.png) modeled after
the ENGR 852 handwritten grid-paper engineering notebook spreads.
"""

from pathlib import Path
import math
from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch

REPO_ROOT = Path(__file__).resolve().parent.parent
DELIV_DIR = REPO_ROOT / "deliverables"
DOCS_DIR = REPO_ROOT / "docs"
SCREENSHOTS_DIR = REPO_ROOT / "evidence" / "screenshots"
SPREADS_DIR = REPO_ROOT / "evidence" / "notebook_spreads"

OUT_PDF = DELIV_DIR / "ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.pdf"
OUT_MD = DOCS_DIR / "ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.md"

# Notebook visual palette (matching the 5 attached grid-notebook photos)
BG_PAPER = colors.HexColor("#FAF8F2")
GRID_LINE = colors.HexColor("#E4E0D4")
MARGIN_RED = colors.HexColor("#FCA5A5")
SPIRAL_GRAY = colors.HexColor("#64748B")
INK_BLACK = colors.HexColor("#0F172A")
INK_BLUE = colors.HexColor("#1D4ED8")
INK_GREEN = colors.HexColor("#15803D")
INK_RED = colors.HexColor("#B91C1C")
INK_PURPLE = colors.HexColor("#6D28D9")
INK_ORANGE = colors.HexColor("#C2410C")

BOX_BLUE_BG = colors.HexColor("#EFF6FF")
BOX_GREEN_BG = colors.HexColor("#F0FDF4")
BOX_RED_BG = colors.HexColor("#FEF2F2")
BOX_PURPLE_BG = colors.HexColor("#F5F3FF")
BOX_CODE_BG = colors.HexColor("#F8FAFC")
BOX_TABLE_HDR = colors.HexColor("#1E3A8A")


def draw_notebook_page_chrome(c, page_num, part_title, page_title, subtitle):
    """Draws the graph-paper grid, spiral binding rings, red margin, and underlined header."""
    w, h = letter
    c.setFillColor(BG_PAPER)
    c.rect(0, 0, w, h, fill=1, stroke=0)

    # 5mm (~14.17 pt) engineering graph grid
    step = 14.17
    c.setStrokeColor(GRID_LINE)
    c.setLineWidth(0.45)
    x = 36
    while x < w - 18:
        c.line(x, 28, x, h - 28)
        x += step
    y = 28
    while y < h - 28:
        c.line(36, y, w - 18, y)
        y += step

    # Left red vertical margin line & top header rule
    c.setStrokeColor(MARGIN_RED)
    c.setLineWidth(1.1)
    c.line(48, 28, 48, h - 28)

    # Spiral binding holes + wire rings on left edge
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setStrokeColor(SPIRAL_GRAY)
    c.setLineWidth(1.2)
    for ry in range(48, int(h - 36), 28):
        c.circle(22, ry, 4.2, fill=1, stroke=1)
        c.line(6, ry + 2, 20, ry + 1)
        c.line(6, ry - 2, 20, ry - 1)

    # Top banner header (like "ENGR 852 HW1 - Question X: ..." in user's photos)
    c.setFillColor(INK_BLACK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(56, h - 42, f"ENGR 852 ASIC LAB NOTEBOOK - {part_title}")
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(INK_BLUE)
    c.drawRightString(w - 24, h - 42, f"Page {page_num} of 100")

    c.setFillColor(INK_BLACK)
    c.setFont("Helvetica-Bold", 12.5)
    c.drawString(56, h - 60, str(page_title).replace("★", "[!]").replace("—", " - "))
    c.setStrokeColor(INK_BLACK)
    c.setLineWidth(1.2)
    c.line(56, h - 64, w - 24, h - 64)

    c.setFillColor(INK_BLUE)
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(56, h - 77, str(subtitle).replace("★", "[!]").replace("—", " - "))


def draw_labeled_box(c, x, y_top, width, height, title, lines, border_color, fill_color, title_color=None, mono=False, font_size=7.6):
    """Draws a color-coded notebook box with title and multi-line text."""
    if title_color is None:
        title_color = border_color
    y_bot = y_top - height
    c.setFillColor(fill_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1.1)
    c.roundRect(x, y_bot, width, height, 4, fill=1, stroke=1)

    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(x + 7, y_top - 13, title)
    c.setStrokeColor(border_color)
    c.setLineWidth(0.6)
    c.line(x + 5, y_top - 16, x + width - 5, y_top - 16)

    c.setFillColor(INK_BLACK)
    font_name = "Courier" if mono else "Helvetica"
    c.setFont(font_name, font_size)
    leading = font_size + 2.4
    cy = y_top - 28
    for line in lines:
        line = str(line).replace("★", "[!]").replace("—", " - ")
        if cy < y_bot + 4:
            break
        if line.startswith("BLUE:"):
            c.setFillColor(INK_BLUE)
            c.setFont(font_name + "-Bold" if not mono else "Courier-Bold", font_size)
            c.drawString(x + 7, cy, line[5:])
            c.setFillColor(INK_BLACK)
            c.setFont(font_name, font_size)
        elif line.startswith("GREEN:"):
            c.setFillColor(INK_GREEN)
            c.setFont(font_name + "-Bold" if not mono else "Courier-Bold", font_size)
            c.drawString(x + 7, cy, line[6:])
            c.setFillColor(INK_BLACK)
            c.setFont(font_name, font_size)
        elif line.startswith("RED:"):
            c.setFillColor(INK_RED)
            c.setFont(font_name + "-Bold" if not mono else "Courier-Bold", font_size)
            c.drawString(x + 7, cy, line[4:])
            c.setFillColor(INK_BLACK)
            c.setFont(font_name, font_size)
        else:
            c.drawString(x + 7, cy, line)
        cy -= leading
    return y_bot


def draw_notebook_table(c, x, y_top, col_widths, rows, title=None):
    """Draws a crisp hardware/cycle-trace table on the notebook grid."""
    cur_y = y_top
    if title:
        c.setFillColor(INK_BLACK)
        c.setFont("Helvetica-Bold", 9.0)
        c.drawString(x, cur_y - 10, title)
        c.setStrokeColor(INK_BLACK)
        c.setLineWidth(0.8)
        c.line(x, cur_y - 12, x + sum(col_widths), cur_y - 12)
        cur_y -= 16

    row_h = 15.5
    total_w = sum(col_widths)
    for r_idx, row in enumerate(rows):
        ry = cur_y - (r_idx + 1) * row_h
        if r_idx == 0:
            c.setFillColor(BOX_TABLE_HDR)
            c.rect(x, ry, total_w, row_h, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 7.6)
        else:
            bg = colors.HexColor("#FFFFFF") if r_idx % 2 == 1 else colors.HexColor("#F1F5F9")
            if any("TRAP" in str(cell) or "FAIL" in str(cell) for cell in row):
                bg = colors.HexColor("#FEE2E2")
            elif any("PASS" in str(cell) or "0000" in str(cell) or "CLEAN" in str(cell) for cell in row):
                bg = colors.HexColor("#DCFCE7")
            c.setFillColor(bg)
            c.rect(x, ry, total_w, row_h, fill=1, stroke=0)
            c.setFillColor(INK_BLACK)
            c.setFont("Courier" if r_idx > 0 else "Helvetica-Bold", 7.3)

        cx = x
        for c_idx, cell in enumerate(row):
            cw = col_widths[c_idx]
            c.setStrokeColor(colors.HexColor("#94A3B8"))
            c.setLineWidth(0.6)
            c.rect(cx, ry, cw, row_h, fill=0, stroke=1)
            c.drawString(cx + 4, ry + 4.2, str(cell)[: int(cw / 4.2)])
            cx += cw
    return cur_y - len(rows) * row_h


def draw_schematic_pipeline(c, x, y_top, width, height, stages, title):
    """Draws an annotated Left-to-Right RTL / GUI pipeline block diagram with arrows (like HW1 photos)."""
    y_bot = y_top - height
    c.setFillColor(colors.HexColor("#FFFFFF"))
    c.setStrokeColor(INK_BLACK)
    c.setLineWidth(1.0)
    c.roundRect(x, y_bot, width, height, 4, fill=1, stroke=1)

    c.setFillColor(INK_BLACK)
    c.setFont("Helvetica-Bold", 8.8)
    c.drawString(x + 8, y_top - 13, title)
    c.line(x + 6, y_top - 15, x + width - 6, y_top - 15)

    n = len(stages)
    margin = 14
    gap = 18
    box_w = (width - 2 * margin - (n - 1) * gap) / n
    box_h = height - 34
    by = y_bot + 8

    palette = [
        (INK_BLUE, BOX_BLUE_BG),
        (INK_GREEN, BOX_GREEN_BG),
        (INK_RED, BOX_RED_BG),
        (INK_PURPLE, BOX_PURPLE_BG),
        (INK_ORANGE, colors.HexColor("#FFF7ED")),
    ]
    for i, (st_title, st_lines) in enumerate(stages):
        bx = x + margin + i * (box_w + gap)
        b_col, bg_col = palette[i % len(palette)]
        c.setFillColor(bg_col)
        c.setStrokeColor(b_col)
        c.setLineWidth(1.2)
        c.roundRect(bx, by, box_w, box_h, 4, fill=1, stroke=1)
        c.setFillColor(b_col)
        c.setFont("Helvetica-Bold", 7.8)
        c.drawString(bx + 5, by + box_h - 11, st_title)
        c.line(bx + 4, by + box_h - 13, bx + box_w - 4, by + box_h - 13)
        c.setFillColor(INK_BLACK)
        c.setFont("Courier", 6.8)
        ly = by + box_h - 23
        for sl in st_lines:
            if ly < by + 4:
                break
            c.drawString(bx + 5, ly, sl[: int(box_w / 4.0)])
            ly -= 9.5

        if i < n - 1:
            ax1 = bx + box_w
            ax2 = bx + box_w + gap
            ay = by + box_h / 2
            c.setStrokeColor(INK_BLACK)
            c.setLineWidth(1.3)
            c.line(ax1, ay, ax2, ay)
            c.line(ax2 - 5, ay + 3.5, ax2, ay)
            c.line(ax2 - 5, ay - 3.5, ax2, ay)
    return y_bot


def build_100_page_curriculum():
    """Returns exactly 100 structured notebook page specifications covering the entire ASIC flow."""
    pages = []

    # PART I: Pages 1..12 — New MacBook Air Setup, GlobalProtect VPN, XQuartz X11 GUI, & Server Isolation
    part1_topics = [
        (
            "Page 1: Master Roadmap — Rebuilding the 520 MHz 14nm Motion Estimator on a Brand-New Laptop",
            "End-to-End Architecture & 7-Part Manual Reproduction Flow (Zero Prior Experience Required)",
            [
                ("1. New MacBook", ["macOS Terminal", "GlobalProtect VPN", "XQuartz X11 GUI", "SSH -Y mahmoodi"]),
                ("2. RTL Design", ["8-Bit Baseline", "16-Bit Upgrade", "Cycle-4111 Hold", "Zero SRAM Macros"]),
                ("3. VCS + Verdi", ["520 MHz (1.923ns)", "0000 / 0100 / FF00", "nWave Hex Zoom", "FSDB Waveforms"]),
                ("4. 14nm P&R + STA", ["Fusion Compiler", "125.07x62.80 um", "ICV DRC = 0/242", "3-Corner PrimeTime"]),
                ("5. Python + Git", ["ReportLab PDF", "python-pptx Deck", "11-Gate Self-Check", "New GitHub Repo"]),
            ],
            [
                ["Phase", "Where You Work", "Primary Tool / Binary", "Verified Output Artifact"],
                ["Phase 1 (Pages 1-12)", "New MacBook Air + XQuartz", "GlobalProtect + XQuartz + ssh -Y", "Isolated server dir ~/engr852_me_new_v1"],
                ["Phase 2 (Pages 13-24)", "Engineering Notebook", "Ch. 10 Sec. 10.4 SAD Equations", "Hand-verified D(i,j) & (i-8,j-8) math"],
                ["Phase 3 (Pages 25-42)", "Verilog Editor (vim/VSCode)", "rtl/8bit/top.v & rtl/16bit/top.v", "Synthesizable 16-PE systolic array RTL"],
                ["Phase 4 (Pages 43-58)", "Synopsys VCS + Verdi GUI", "vcs -full64 & verdi -ssf waves.fsdb", "7/7 PASS logs + zoomed nWave PNGs"],
                ["Phase 5 (Pages 59-76)", "Fusion Compiler + ICV + PT", "fc_shell, icv, pt_shell (SAED14nm)", "top.gds, 0/242 DRC, +0.71/+0.54/+0.22ns"],
                ["Phase 6 (Pages 77-90)", "Local Python 3 Environment", "python-pptx + reportlab + pypdf", "19-Slide Deck + Engineering Report PDF"],
                ["Phase 7 (Pages 91-100)", "Git CLI + GitHub Web", "git init / commit / push origin main", "Public/Private GitHub Portfolio Repo"],
            ],
            [
                "RED:★ TRAP: Running Everything in an Old Server Folder Overwrites Previous Work! ★",
                "Even when logging into the same campus account (926784856@mahmoodi.rcc.at.sfsu.edu), NEVER edit inside old",
                "folders! Always create a fresh top-level directory (e.g., mkdir -p ~/motion_estimator_manual_v1) so your",
                "manual build is 100% isolated, clean, and reproducible from scratch.",
            ],
            [
                "# Step 1: On your brand-new MacBook Air, open Terminal (Cmd + Space -> type Terminal -> Return)",
                "mkdir -p ~/Developer/motion-estimator-14nm-asic-manual   # Create fresh local workspace",
                "cd ~/Developer/motion-estimator-14nm-asic-manual         # Enter workspace",
                "mkdir -p rtl/8bit rtl/16bit tb/8bit tb/16bit scripts docs deliverables evidence/screenshots",
            ],
        ),
        (
            "Page 2: ENGR 852 Course Project Requirements Matrix & 90-100% Grading Rubric",
            "Mapping Every Professor Requirement to Exact Files, Waveforms, Reports, and Verification Gates",
            [
                ("RTL & Testbench", ["All .v files", "top_tb.v (520MHz)", "top_tb_direct.v", "Simulation logs"]),
                ("Synthesis & SDC", ["top_520mhz.sdc", "1.923 ns period", "0.5 ns I/O delay", "0.2 ns uncertainty"]),
                ("Physical Layout", ["125.07x62.80 um", "0 SRAM macros", "top.gds (80 MB)", "ICV DRC = 0/242"]),
                ("Post-Layout STA", ["3-Corner SPEF", "PrimeTime Setup", "PrimeTime Hold", "FAST/TYP/SLOW"]),
            ],
            [
                ["Professor Requirement", "Required Constraint / Spec", "Our Verified Result", "Rubric Status"],
                ["Verilog RTL & Testbench", "Synthesizable top.v + self-checking TB", "8-bit & 16-bit top.v + 4 TBs (7/7 PASS)", "100% VERIFIED"],
                ["Clock & I/O Constraints", "500+ MHz, 0.5ns I/O, 0.2ns uncertainty", "520 MHz (1.923ns), 0.5ns I/O, 0.2ns unc", "100% VERIFIED"],
                ["Memory Exclusion Rule", "Exclude ROM_R & ROM_S from synthesis", "0 memory macros in top (TB-only ROMs)", "100% VERIFIED"],
                ["Physical Layout & DRC", "Place & Route + Design Rule Check", "125.07x62.80 um, 0/242 ICV DRC CLEAN", "100% VERIFIED"],
                ["Parasitic Extraction", "Post-layout RC extraction (.spef)", "min/nominal/max 3-corner SPEF extracted", "100% VERIFIED"],
                ["PrimeTime Setup & Hold", "Both Setup & Hold across corners", "FAST +0.71/0.00, TYP +0.54/+0.04, SLOW +0.22/+0.14", "100% VERIFIED"],
                ["Report & Presentation", "Block diagram, tricky parts, PPA, waves", "Final Report PDF + 19-Slide Deck + SOP", "100% VERIFIED"],
            ],
            [
                "RED:★ TRAP: Synthesizing RMEM and SMEM Inside module top! ★",
                "The syllabus explicitly states: 'Exclude the memories (both reference and search) from your synthesis",
                "for simplicity and include them only in your test bench.' Keep RMEM and SMEM instantiated ONLY in top_tb.v!",
            ],
            [
                "// Verification in top_tb.v: RMEM and SMEM stay outside module top!",
                "top  u1 (clock, start, BestDist, motionX, motionY, AddressR, AddressS1, AddressS2, R, S1, S2);",
                "RMEM u2 (AddressR, R);              // 256x8 reference ROM lives ONLY in testbench",
                "SMEM u3 (AddressS1, AddressS2, S1, S2); // 1024x8 dual-port search ROM lives ONLY in testbench",
            ],
        ),
        (
            "Page 3: Brand-New MacBook Air First Boot — macOS Terminal, Xcode CLI Tools, & Python Setup",
            "Step-by-Step Local Workstation Preparation Before Connecting to SFSU Servers",
            [
                ("Spotlight Search", ["Press Cmd+Space", "Type: Terminal", "Press Return", "Pin to Dock"]),
                ("Xcode CLI Tools", ["xcode-select", "--install", "Provides git, ssh", "scp, make, clang"]),
                ("Python 3 Venv", ["python3 -m venv", "source activate", "pip install pptx", "reportlab pillow"]),
                ("Folder Tree", ["rtl/ tb/ scripts/", "verification/", "deliverables/", "docs/ evidence/"]),
            ],
            [
                ["macOS Command", "What It Installs / Configures", "Expected Terminal Response"],
                ["xcode-select --install", "Apple Command Line Developer Tools (git, ssh, make)", "xcode-select: note: install requested"],
                ["git --version", "Verifies Git version control binary", "git version 2.39+ (Apple Git)"],
                ["ssh -V", "Verifies OpenSSH client for mahmoodi server", "OpenSSH_9.x, LibreSSL 3.x"],
                ["python3 -m venv .venv", "Creates isolated Python virtual environment", "Directory .venv/ created cleanly"],
                ["source .venv/bin/activate", "Activates virtual environment in current shell", "Prompt changes to (.venv) $"],
                ["pip install python-pptx reportlab pypdf pillow", "Installs slide & PDF report libraries", "Successfully installed ..."],
            ],
            [
                "RED:★ TRAP: Installing Python Packages Globally Without a Virtual Environment! ★",
                "macOS system Python blocks global pip installs (PEP 668 externally-managed-environment error).",
                "Always run 'python3 -m venv .venv && source .venv/bin/activate' inside your project folder first!",
            ],
            [
                "# Copy and paste line-by-line into macOS Terminal on your new MacBook Air:",
                "xcode-select --install",
                "mkdir -p ~/Developer/engr852-motion-estimator-clean && cd ~/Developer/engr852-motion-estimator-clean",
                "python3 -m venv .venv && source .venv/bin/activate",
                "pip install --upgrade pip python-pptx reportlab pypdf pillow matplotlib",
            ],
        ),
        (
            "Page 4: Project Naming Variations — Creating a Distinct Identity While Matching 100% Results",
            "How to Rename Folders, Repos, and Scripts on Your New Laptop Without Breaking Verilog Ports",
            [
                ("Safe to Rename", ["Local folder name", "Server workspace", "GitHub repo name", "Slide/PDF filenames"]),
                ("Safe to Customize", ["Testbench binary", "Log filenames", "Report color theme", "README title"]),
                ("DO NOT RENAME", ["module top ports", "clock, start, R", "S1, S2, BestDist", "motionX, motionY"]),
                ("Why Keep Ports?", ["SDC clock target", "Testbench wiring", "Post-layout GLS", "Grader scripts"]),
            ],
            [
                ["Component Category", "Original Reference Name", "Variation Option A", "Variation Option B"],
                ["Local Project Folder", "motion-estimator", "engr852-asic-me-520mhz", "sad-motion-estimator-14nm"],
                ["Server Workspace", "~/motion_estimator_v9", "~/engr852_me_manual_build", "~/asic_me_520mhz_clean"],
                ["GitHub Repository", "motion-estimator-asic-lab-...", "engr852-14nm-motion-estimator", "verilog-sad-me-520mhz-asic"],
                ["VCS Simulation Binary", "simv", "simv_me_520mhz", "run_me_sim"],
                ["Waveform Dump File", "waves.fsdb", "me_520mhz_waves.fsdb", "sad_datapath.fsdb"],
                ["Top Module & Ports", "module top (clock, start...)", "MUST REMAIN module top (...)", "MUST REMAIN module top (...)"],
            ],
            [
                "RED:★ TRAP: Renaming 'module top' or Port Names in top.v! ★",
                "In Synopsys Fusion Compiler, IC Validator, and PrimeTime, 'top' and port names ('clock', 'BestDist',",
                "'motionX', 'motionY') are referenced by top_520mhz.sdc and top_tb.v. Keep module/port names identical!",
            ],
            [
                "# Example: Setting your custom project variation variables in ~/.zshrc or terminal:",
                "export PROJ_LOCAL=~/Developer/engr852-14nm-motion-estimator",
                "export PROJ_REMOTE=engr852_me_manual_build",
                "export SFSU_USER=926784856",
                "export SFSU_HOST=mahmoodi.rcc.at.sfsu.edu",
            ],
        ),
        (
            "Page 5: Installing & Operating Palo Alto GlobalProtect VPN (vpn.sfsu.edu)",
            "Step-by-Step Campus Network Authentication Required Before SSH or XQuartz Can Reach mahmoodi",
            [
                ("1. Menu Bar Icon", ["Click Globe Icon", "Top-right macOS", "Menu Bar", "Open GlobalProtect"]),
                ("2. Portal Address", ["Type Portal URL:", "vpn.sfsu.edu", "Click 'Connect'", "Wait for login"]),
                ("3. SFSU Login", ["ID: 926784856", "(or @sfsu.edu)", "Enter SFSU Pass", "Click Sign In"]),
                ("4. Duo 2FA Push", ["Approve Duo Push", "on your iPhone", "Status changes to:", "'Connected'"]),
            ],
            [
                ["Step", "Where to Click / What to Type", "Visual Confirmation on Screen"],
                ["1", "Open Applications -> Palo Alto Networks -> GlobalProtect", "Small globe icon appears in top-right macOS menu bar"],
                ["2", "Type Portal: vpn.sfsu.edu -> Click Connect", "SFSU Single Sign-On (SSO) window pops up"],
                ["3", "Username: 926784856 | Password: <Your SFSU Password>", "Prompts for Duo Two-Factor Authentication"],
                ["4", "Click 'Send Me a Push' -> Approve on phone", "Globe icon gets a small shield; says 'Connected'"],
                ["5", "In Terminal: ping -c 2 mahmoodi.rcc.at.sfsu.edu", "64 bytes from 130.212.x.x: icmp_seq=0 ttl=..."],
            ],
            [
                "RED:★ TRAP: 'ssh: Could not resolve hostname mahmoodi.rcc.at.sfsu.edu' or Operation Timed Out! ★",
                "The SFSU EDA server (mahmoodi.rcc.at.sfsu.edu) is behind the campus firewall. If GlobalProtect VPN",
                "disconnects or sleeps, SSH and XQuartz windows will freeze immediately. Always check the VPN shield first!",
            ],
            [
                "# Verify VPN connectivity from macOS Terminal before launching XQuartz:",
                "scutil --dns | grep sfsu.edu          # Confirm SFSU DNS resolvers are active",
                "nc -zv mahmoodi.rcc.at.sfsu.edu 22    # Confirm TCP port 22 (SSH) is reachable!",
                "# Expected output: Connection to mahmoodi.rcc.at.sfsu.edu port 22 [tcp/ssh] succeeded!",
            ],
        ),
        (
            "Page 6: Installing & Configuring XQuartz on macOS for Synopsys Verdi & Fusion Compiler GUIs",
            "Complete Baby-Steps Setup of XQuartz.org X11 Server on a Brand-New MacBook Air",
            [
                ("1. Install XQuartz", ["brew install", "--cask xquartz", "OR download dmg", "from xquartz.org"]),
                ("2. Security Prefs", ["Open XQuartz", "Cmd + , (Prefs)", "Click 'Security'", "Check Network Box"]),
                ("3. Log Out / In", ["CRITICAL STEP:", "Log out of macOS", "Log back in so", "DISPLAY socket binds"]),
                ("4. Open xterm", ["Launch XQuartz", "Apps -> Terminal", "White xterm opens", "Check $DISPLAY"]),
            ],
            [
                ["XQuartz Setup Step", "Exact Action / Menu Path", "Why This Step Is Mandatory"],
                ["Step 1: Install", "Run: brew install --cask xquartz (or install XQuartz-2.8.5.pkg)", "macOS does not include an X11 server by default"],
                ["Step 2: Launch", "Open /Applications/Utilities/XQuartz.app", "Starts the X11 window manager in macOS Dock"],
                ["Step 3: Preferences", "Click XQuartz menu (top-left) -> Settings/Preferences -> Security tab", "Opens X11 authentication and network settings"],
                ["Step 4: Check Boxes", "Enable both 'Authenticate connections' & 'Allow connections from network clients'", "Permits remote Synopsys GUI windows to render"],
                ["Step 5: Re-login", "Apple Menu -> Log Out -> Log back into your MacBook Air", "Initializes launchd /tmp/.X11-unix/X0 listener"],
                ["Step 6: Open xterm", "Inside XQuartz, press Cmd+N (or Applications -> Terminal)", "Opens the X11-aware xterm terminal window"],
            ],
            [
                "RED:★ TRAP: Installing XQuartz Without Logging Out and Back Into macOS! ★",
                "If you install XQuartz and immediately run 'ssh -Y', DISPLAY will be empty! You MUST log out of your",
                "macOS user account (or reboot the MacBook Air) once after installing XQuartz so launchd sets $DISPLAY.",
            ],
            [
                "# Run inside the XQuartz xterm window (or macOS Terminal after re-login) to verify X11:",
                "echo $DISPLAY",
                "# Expected output: /private/tmp/com.apple.launchd.xxxx/org.xquartz:0  (or :0)",
                "open -a XQuartz     # Starts XQuartz daemon if not already running in Dock",
            ],
        ),
        (
            "Page 7: How XQuartz + ssh -Y Works — Visual X11 Forwarding Pipeline & Account Login",
            "Connecting to 926784856@mahmoodi.rcc.at.sfsu.edu with Trusted X11 GUI Forwarding",
            [
                ("MacBook XQuartz", ["Local X11 Server", "Listens on :0", "Draws Windows", "Mouse & Keyboard"]),
                ("Encrypted SSH -Y", ["ssh -Y 926784856@", "mahmoodi.rcc...", "Forwards X11", "over Port 22"]),
                ("mahmoodi Server", ["Sets DISPLAY=", "localhost:10.0", "Runs verdi &", "fc_shell -gui"]),
                ("GUI on Your Mac", ["Verdi nWave &", "Fusion Compiler", "pop up natively", "on MacBook screen!"]),
            ],
            [
                ["SSH Flag / Variable", "Exact Command / Value", "What Happens Behind the Scenes"],
                ["Account Name", "926784856@mahmoodi.rcc.at.sfsu.edu", "Logs into your SFSU student account on the Synopsys server"],
                ["-Y Flag (Trusted X11)", "ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu", "Enables trusted X11 forwarding (required by OpenGL/Verdi)"],
                ["-X Flag (Untrusted)", "Do NOT use -X alone; use -Y", "-X restricts X11 extensions and causes Verdi/FC crashes"],
                ["Remote $DISPLAY", "echo $DISPLAY (on mahmoodi)", "Prints localhost:10.0 (or :11.0, :12.0) when X11 is active"],
                ["GUI Test Command", "xclock & (on mahmoodi)", "Pops up a live analog clock window on your MacBook screen!"],
            ],
            [
                "RED:★ TRAP: 'Warning: No xauth data; using fake authentication data for X11 forwarding' or Empty DISPLAY! ★",
                "If 'echo $DISPLAY' on mahmoodi prints a blank line, you forgot '-Y' or XQuartz is not running on your Mac.",
                "Always start XQuartz first, open its xterm (Cmd+N), and run: ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu",
            ],
            [
                "# Step-by-Step Login inside XQuartz xterm window:",
                "open -a XQuartz                                     # 1. Ensure XQuartz icon is active in Dock",
                "ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu           # 2. Connect with Trusted X11 forwarding",
                "# On mahmoodi server prompt [926784856@mahmoodi ~]$ :",
                "echo $DISPLAY                                       # 3. Verify output is localhost:10.0 (not empty!)",
                "xclock &                                            # 4. Test GUI window pop-up on your MacBook!",
            ],
        ),
        (
            "Page 8: Setting Up Passwordless Ed25519 SSH Keys & ~/.ssh/config on Your New Laptop",
            "Eliminating Repeated Password Prompts for ssh, scp, and XQuartz GUI Sessions",
            [
                ("1. Generate Key", ["ssh-keygen", "-t ed25519", "~/.ssh/id_ed25519", "On new MacBook"]),
                ("2. Copy PubKey", ["cat id_ed25519.pub", "| ssh 926784856@", "mahmoodi", ">> authorized_keys"]),
                ("3. Fix Chmod", ["chmod 700 ~/.ssh", "chmod 600", "authorized_keys", "Mandatory check!"]),
                ("4. SSH Alias", ["~/.ssh/config", "Host mahmoodi", "User 926784856", "ForwardX11Trusted"]),
            ],
            [
                ["File / Permission", "Location", "Required Octal Mode", "Why SSH Rejects Keys If Wrong"],
                ["~/.ssh", "MacBook & mahmoodi", "700 (drwx------)", "sshd refuses key auth if group/others can write ~/.ssh"],
                ["~/.ssh/id_ed25519", "MacBook (Private Key)", "600 (-rw-------)", "ssh client refuses private key if readable by others"],
                ["~/.ssh/authorized_keys", "mahmoodi Server", "600 (-rw-------)", "sshd ignores authorized_keys if group-writable"],
                ["~/.ssh/config", "MacBook", "600 (-rw-------)", "Automatically enables ForwardX11Trusted yes for mahmoodi"],
            ],
            [
                "RED:★ TRAP: Home Directory or ~/.ssh Group-Writable on mahmoodi! ★",
                "If passwordless SSH still asks for a password after adding your public key, run:",
                "chmod go-w ~ && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys on mahmoodi!",
            ],
            [
                "# Run on your new MacBook Air Terminal:",
                "ssh-keygen -t ed25519 -C \"engr852-new-laptop\" -f ~/.ssh/id_ed25519 -N \"\"",
                "cat ~/.ssh/id_ed25519.pub | ssh 926784856@mahmoodi.rcc.at.sfsu.edu \\",
                "  \"mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys\"",
                "cat << 'EOF' >> ~/.ssh/config",
                "Host mahmoodi",
                "    HostName mahmoodi.rcc.at.sfsu.edu",
                "    User 926784856",
                "    IdentityFile ~/.ssh/id_ed25519",
                "    ForwardX11 yes",
                "    ForwardX11Trusted yes",
                "    ServerAliveInterval 30",
                "EOF",
                "chmod 600 ~/.ssh/config",
            ],
        ),
        (
            "Page 9: Creating a Brand-New Isolated Workspace Under 926784856@mahmoodi.rcc.at.sfsu.edu",
            "How to Coexist Safely With Existing Server Folders While Building Your New Project From Scratch",
            [
                ("Existing Account", ["926784856@", "mahmoodi.rcc...", "Has prior folders", "(DO NOT TOUCH!)"]),
                ("New Server Dir", ["mkdir -p", "~/me_asic_new_v1", "100% isolated", "clean directory"]),
                ("Subdirectories", ["rtl/8bit rtl/16bit", "tb/8bit tb/16bit", "scripts/ logs/", "results/ reports/"]),
                ("Independent Run", ["Fresh VCS simv", "Fresh FC NDM lib", "Fresh ICV DRC", "Fresh PT STA"]),
            ],
            [
                ["Server Subdirectory", "Full Path on mahmoodi", "What You Will Store Inside It"],
                ["Root Workspace", "~/me_asic_new_v1/", "Your brand-new manual project root (completely separate from old folders)"],
                ["8-Bit & 16-Bit RTL", "~/me_asic_new_v1/rtl/{8bit,16bit}/", "top.v (baseline 8-bit saturating & upgraded 16-bit non-saturating)"],
                ["Testbenches & Hex", "~/me_asic_new_v1/tb/{8bit,16bit}/", "top_tb.v, top_tb_direct.v, top_tb_16bit.v, ref.txt, search.txt"],
                ["Constraints & TCL", "~/me_asic_new_v1/scripts/", "top_520mhz.sdc, run_fc.tcl, run_pt.tcl, run_icv.sh"],
                ["EDA Logs & Reports", "~/me_asic_new_v1/reports/", "Simulation logs, area/power/timing reports, DRC/LVS results"],
            ],
            [
                "RED:★ TRAP: Reusing an Existing Synopsys NDM Library Directory (.ndm / .design)! ★",
                "Fusion Compiler locks its NDM library directory. When building a new version under 926784856@mahmoodi,",
                "always run inside your new folder (~/me_asic_new_v1) so a fresh NDM container is created cleanly.",
            ],
            [
                "# Log into mahmoodi via XQuartz and create your isolated manual workspace:",
                "ssh -Y mahmoodi",
                "mkdir -p ~/me_asic_new_v1/{rtl/8bit,rtl/16bit,tb/8bit,tb/16bit,scripts,logs,reports,results}",
                "cd ~/me_asic_new_v1",
                "pwd    # Verify: /home/926784856/me_asic_new_v1",
            ],
        ),
        (
            "Page 10: Loading the Synopsys EDA Toolchain Environment on mahmoodi",
            "Sourcing /apps/settings and Verifying VCS, Verdi, Fusion Compiler, IC Validator, and PrimeTime",
            [
                ("source /apps/settings", ["Sets $PATH", "Sets $SNPSLMD", "Sets $VCS_HOME", "Sets $VERDI_HOME"]),
                ("Simulation Tools", ["vcs -ID", "verdi -version", "Compiles Verilog", "Opens FSDB waves"]),
                ("Implementation", ["fc_shell", "dc_shell", "SAED14nm EDK", "14nm FinFET NDM"]),
                ("Sign-Off Tools", ["icv (DRC/LVS)", "pt_shell (STA)", "242 DRC rules", "3-Corner SPEF"]),
            ],
            [
                ["Synopsys Tool", "Command to Check Binary", "Role in Our Motion Estimator Project"],
                ["Environment Script", "source /apps/settings", "Loads license server (27020@...) and all Synopsys tool paths"],
                ["Synopsys VCS", "which vcs", "Compiles RTL + testbenches into executable binary 'simv'"],
                ["Synopsys Verdi", "which verdi", "Interactive GUI waveform viewer (nWave) for .fsdb inspection"],
                ["Fusion Compiler", "which fc_shell", "RTL-to-GDSII synthesis, floorplanning, placement, CTS, routing"],
                ["IC Validator", "which icv", "Sign-off Design Rule Check (DRC) & Layout Versus Schematic (LVS)"],
                ["PrimeTime", "which pt_shell", "Sign-off Static Timing Analysis (STA) across FAST/TYPICAL/SLOW"],
                ["SAED14nm PDK", "ls /apps/synopsys/SAED14_EDK", "14nm FinFET standard cells, TLU+ parasitics, ICV rule decks"],
            ],
            [
                "RED:★ TRAP: 'vcs: command not found' or 'fc_shell: command not found'! ★",
                "Every new SSH session starts with a bare shell. You MUST run 'source /apps/settings' at the start",
                "of every terminal session (or add 'source /apps/settings' to your scripts) before calling any EDA tool!",
            ],
            [
                "# Run on mahmoodi inside ~/me_asic_new_v1:",
                "source /apps/settings",
                "which vcs verdi fc_shell icv pt_shell",
                "ls -la /apps/synopsys/SAED14_EDK/lib/stdcell_rvt/ndm/",
                "ls -la /apps/synopsys/SAED14_EDK/tech/icv_drc/saed14nm_1p9m_drc_rules.rs",
            ],
        ),
        (
            "Page 11: Transferring Files Between Your New MacBook Air and mahmoodi (scp & rsync)",
            "Bidirectional File Sync Workflow for RTL, Testbenches, Waveforms, and Sign-Off Reports",
            [
                ("MacBook -> Server", ["scp -r rtl tb", "scripts mahmoodi:", "~/me_asic_new_v1/", "Uploads source"]),
                ("Run on Server", ["ssh -Y mahmoodi", "Run VCS / Verdi", "Run FC / ICV / PT", "Generates reports"]),
                ("Server -> MacBook", ["scp -r mahmoodi:", "~/me_asic_new_v1/", "reports/*.rpt .", "Downloads results"]),
                ("Local Packaging", ["Build PDF Report", "Build PPTX Deck", "Run 11-Gate Check", "Push to GitHub"]),
            ],
            [
                ["Transfer Direction", "Exact Command (Run on MacBook Terminal)", "What Gets Transferred"],
                ["Upload RTL & TBs", "scp -r rtl tb scripts mahmoodi:~/me_asic_new_v1/", "Copies local Verilog & TCL scripts to mahmoodi"],
                ["Download Logs", "scp mahmoodi:~/me_asic_new_v1/logs/*.log verification/", "Downloads VCS, FC, ICV, and PrimeTime logs"],
                ["Download Reports", "scp mahmoodi:~/me_asic_new_v1/reports/*.rpt verification/", "Downloads timing, area, power, and DRC reports"],
                ["Download Images", "scp mahmoodi:~/me_asic_new_v1/*.png evidence/screenshots/", "Downloads Verdi nWave & Fusion Compiler PNGs"],
                [" Incremental Sync", "rsync -avz mahmoodi:~/me_asic_new_v1/reports/ verification/", "Transfers only new/changed files quickly"],
            ],
            [
                "RED:★ TRAP: Running 'scp' Inside the Remote mahmoodi SSH Prompt Instead of Local MacBook Terminal! ★",
                "Always run 'scp' from a local MacBook Terminal tab (not inside the remote mahmoodi shell),",
                "using the 'mahmoodi:~/me_asic_new_v1/...' host prefix configured in ~/.ssh/config!",
            ],
            [
                "# Open a local MacBook Terminal tab (Cmd+T) and test uploading a file to mahmoodi:",
                "echo 'Hello ENGR 852' > test_upload.txt",
                "scp test_upload.txt mahmoodi:~/me_asic_new_v1/",
                "ssh mahmoodi 'cat ~/me_asic_new_v1/test_upload.txt && rm ~/me_asic_new_v1/test_upload.txt'",
                "rm test_upload.txt",
            ],
        ),
        (
            "Page 12: Part I Self-Check Gate — Verifying VPN, XQuartz GUI, SSH Key, and Server Tools",
            "Complete 6-Point Readiness Checklist Before Writing Any Verilog Code",
            [
                ("Check 1: VPN", ["GlobalProtect", "Status: Connected", "ping mahmoodi", "0% packet loss"]),
                ("Check 2: XQuartz", ["XQuartz running", "Allow network=ON", "DISPLAY=:0", "xclock pops up"]),
                ("Check 3: SSH Key", ["ssh -Y mahmoodi", "No password ask", "DISPLAY=localhost", ":10.0 verified"]),
                ("Check 4: EDA Env", ["source /apps/...", "vcs, verdi, icv", "fc_shell, pt_shell", "All found in PATH"]),
            ],
            [
                ["Gate ID", "Verification Command", "Expected Passing Output", "Status"],
                ["GATE-1.1", "pgrep -fl GlobalProtect", "GlobalProtect process active & connected", "PASS"],
                ["GATE-1.2", "ssh -Y mahmoodi 'echo $DISPLAY'", "localhost:10.0 (or :11.0 / :12.0)", "PASS"],
                ["GATE-1.3", "ssh mahmoodi 'pwd && ls -d ~/me_asic_new_v1'", "/home/926784856/me_asic_new_v1", "PASS"],
                ["GATE-1.4", "ssh mahmoodi 'source /apps/settings && which vcs verdi'", "/apps/synopsys/.../bin/vcs & verdi", "PASS"],
                ["GATE-1.5", "ssh mahmoodi 'source /apps/settings && which fc_shell icv pt_shell'", "/apps/synopsys/.../bin/fc_shell, icv, pt_shell", "PASS"],
                ["GATE-1.6", "python3 -c 'import pptx, reportlab, pypdf, PIL; print(\"OK\")'", "OK (on local MacBook virtual environment)", "PASS"],
            ],
            [
                "GREEN:★ PART I COMPLETE! Your Brand-New MacBook Air & XQuartz Link to mahmoodi Are Ready! ★",
                "If all 6 gates above pass, your workstation is 100% ready for RTL design, simulation, and 14nm P&R.",
                "Proceed to Part II (Page 13) to master the Motion Estimator architecture and mathematical equations.",
            ],
            [
                "# One-line automated Part I self-check (run on your MacBook Air Terminal):",
                "ssh -Y mahmoodi 'source /apps/settings && echo DISPLAY=$DISPLAY && which vcs verdi fc_shell icv pt_shell'",
            ],
        ),
    ]
    pages.extend(part1_topics)

    # PART II: Pages 13..24 — Digital Design Fundamentals & Chapter 10 Section 10.4 Theory
    part2_topics = [
        (
            "Page 13: Block-Matching Motion Estimation Concept (Chapter 10, Section 10.4, pp. 143-145)",
            "How Video Encoders Find the Best-Matching 16x16 Macroblock Inside a 31x31 Search Window",
            [
                ("Reference Block R", ["16 x 16 pixels", "256 bytes total", "r[m,n] in [0..255]", "AddressR[7:0]"]),
                ("Search Window S", ["31 x 31 pixels", "961 active bytes", "s[m+i,n+j]", "AddressS1/S2[9:0]"]),
                ("256 Candidates", ["(i,j) in [0..15]^2", "16 rows x 16 cols", "Evaluated in", "16-PE array"]),
                ("Motion Vector", ["(motionX, motionY)", "= (i - 8, j - 8)", "Range: [-8, +7]", "Minimum D(i,j)"]),
            ],
            [
                ["Parameter", "Symbol / Range", "Hardware Size", "Physical Meaning in Video Compression"],
                ["Reference Macroblock", "R = r_{m,n}, m,n in [0,15]", "256 x 8-bit ROM_R", "Current 16x16 pixel block being encoded"],
                ["Search Window", "S = s_{x,y}, x,y in [0,30]", "1024 x 8-bit ROM_S", "31x31 region in previous frame (+/-8 pixels)"],
                ["Candidate Index", "(i, j), i,j in [0,15]", "4-bit row/col counters", "Top-left offset of candidate 16x16 block in S"],
                ["Signed Displacement", "(dx, dy) = (i-8, j-8)", "8-bit signed [7:0]", "Horizontal & vertical motion vector in [-8, +7]"],
                ["Distortion Metric", "D(i, j)", "8-bit (orig) / 16-bit", "Sum of Absolute Differences (SAD) over 256 pixels"],
            ],
            [
                "BLUE:Why Block-Matching Saves Video Bandwidth:",
                "Instead of transmitting all 256 raw pixel bytes of R, the encoder transmits only the 2-byte motion vector",
                "(motionX, motionY) pointing to the closest matching 16x16 block in the previous frame plus tiny residuals!",
            ],
            [
                "// Mathematical Definition (Lecture Notes Chapter 10, Section 10.4, Equation on p. 144):",
                "// For each candidate offset (i, j) with i in 0..15 and j in 0..15:",
                "//   D(i, j) = Sum_{m=0..15} Sum_{n=0..15} | r[m, n] - s[m + i, n + j] |",
                "// Best match is the candidate (i*, j*) that minimizes D(i, j).",
            ],
        ),
        (
            "Page 14: Sum of Absolute Differences (SAD) Distortion Equation D(i,j) — Hand Calculation",
            "Step-by-Step Numerical Proof of D(i,j) for Zero-Match, +1 Offset, and Maximum Contrast",
            [
                ("Pixel Fetch", ["Read r[m,n] (8b)", "Read s[m+i,n+j]", "Every clock edge", "1 pixel per PE"]),
                ("Absolute Diff", ["if (R < S) S - R", "else R - S", "Always >= 0", "Range: 0..255"]),
                ("256-Cycle Sum", ["Accumulate over", "m=0..15, n=0..15", "256 pixels total", "per candidate"]),
                ("Final D(i,j)", ["Min = 0 (16'h0000)", "Max = 256 * 255", "= 65,280", "(16'hFF00)"]),
            ],
            [
                ["Stimulus Scenario", "Pixel Values (r vs. s)", "Single-Pixel |r - s|", "256-Pixel Total SAD D(i,j)", "Hex Value (16-Bit)"],
                ["Exact Match (Zero Diff)", "r[m,n] == s[m+i,n+j] (all 256)", "|x - x| = 0", "256 x 0 = 0", "16'h0000"],
                ["Single-Pixel +3 Offset", "1 pixel differs by 3; 255 match", "1x3 + 255x0", "3 + 0 = 3", "16'h0003"],
                ["Uniform +1 Offset (top_tb)", "|r[m,n] - s[m+i,n+j]| = 1 (all)", "1 per pixel", "256 x 1 = 256", "16'h0100 (8b -> FF!)"],
                ["Uniform +2 Offset", "|r[m,n] - s[m+i,n+j]| = 2 (all)", "2 per pixel", "256 x 2 = 512", "16'h0200 (8b -> FF!)"],
                ["Maximum Contrast (All FF/00)", "r[m,n] = 0x00, s[m+i,n+j] = 0xFF", "|0 - 255| = 255", "256 x 255 = 65,280", "16'hFF00 (8b -> FF!)"],
            ],
            [
                "RED:★ TRAP: Confusing 16'hFF00 (65,280) With 16'hFFFF (65,535)! ★",
                "Because an 8-bit unsigned pixel has maximum value 255 (8'hFF), the maximum possible SAD over 256 pixels is",
                "256 x 255 = 65,280 = 16'hFF00 (NOT 16'hFFFF!). Initializing BestDist to 16'hFFFF guarantees 16'hFF00 < 16'hFFFF!",
            ],
            [
                "// Combinational Absolute Difference in Verilog (from module PE):",
                "if (R < (S1S2mux ? S1 : S2))",
                "    difference = (S1S2mux ? S1 : S2) - R;  // When S > R, compute S - R (positive 8-bit magnitude)",
                "else",
                "    difference = R - (S1S2mux ? S1 : S2);  // When R >= S, compute R - S (positive 8-bit magnitude)",
            ],
        ),
        (
            "Page 15: Coordinate Transformation Proof — Candidate (i,j) to Signed Motion Vector (i-8, j-8)",
            "How Unsigned Loop Indices [0..15] Map to 8-Bit Two's Complement Displacements [-8..+7]",
            [
                ("Candidate Index", ["i in 0..15 (X)", "j in 0..15 (Y)", "4-bit unsigned", "0000 to 1111"]),
                ("Subtract Center 8", ["dx = i - 8", "dy = j - 8", "4-bit signed", "vectorX, vectorY"]),
                ("Sign Extension", ["{{4{vectorX[3]}},", "vectorX[3:0]}", "Pads MSB bit [3]", "into bits [7:4]"]),
                ("8-Bit Output", ["motionX[7:0]", "motionY[7:0]", "8'hF8 (-8) to", "8'h07 (+7)"]),
            ],
            [
                ["Candidate Index i or j", "Signed Displacement (i - 8)", "4-Bit vectorX/Y [3:0]", "8-Bit Sign-Extended motionX/Y [7:0]"],
                ["0 (Top-Left Edge)", "0 - 8 = -8", "4'b1000 (4'h8)", "8'b1111_1000 = 8'hF8 (-8)"],
                ["3 (Target X in top_tb)", "3 - 8 = -5", "4'b1011 (4'hB)", "8'b1111_1011 = 8'hFB (-5)"],
                ["6 (Tie X in 8-bit top_tb)", "2 - 8 = -6", "4'b1010 (4'hA)", "8'b1111_1010 = 8'hFA (-6)"],
                ["8 (Zero Displacement)", "8 - 8 = 0", "4'b0000 (4'h0)", "8'b0000_0000 = 8'h00 (0)"],
                ["15 (Bottom-Right Edge)", "15 - 8 = +7", "4'b0111 (4'h7)", "8'b0000_0111 = 8'h07 (+7)"],
            ],
            [
                "RED:★ TRAP: Why Control Uses 'vectorY = count[11:8] - 9' Instead of '- 8'! ★",
                "Look at Table 10.1 (p. 146): A candidate row j finishes accumulating on the FIRST cycle of row j+1",
                "(when count[7:4] wraps to 0000 and count[11:8] has already incremented by +1). Thus (j+1) - 9 = j - 8!",
            ],
            [
                "// In module Control (computing 4-bit signed motion vector components at evaluation time):",
                "vectorX = count[3:0] - 8;            // Horizontal displacement dx = i - 8 (in [-8..+7])",
                "vectorY = count[11:8] - 9;           // Vertical displacement dy = (j+1) - 9 = j - 8 (in [-8..+7])",
                "// In module Comparator (sign-extending 4-bit signed vector to 8-bit output port):",
                "motionX <= {{4{vectorX[3]}}, vectorX}; // Replicates sign bit vectorX[3] across upper 4 bits [7:4]",
                "motionY <= {{4{vectorY[3]}}, vectorY}; // Replicates sign bit vectorY[3] across upper 4 bits [7:4]",
            ],
        ),
        (
            "Page 16: 16-PE 1D Systolic Array Architecture & Dual Search Memory Ports (S1, S2)",
            "How 16 Processing Elements Compute 16 Horizontal Candidate Blocks Simultaneously",
            [
                ("Reference R[7:0]", ["Enters PE0 first", "Shifts right via", "Rpipe0..Rpipe14", "1 cycle per hop"]),
                ("Search Bus S1[7:0]", ["Broadcast to all", "PE0..PE15", "Selected when", "S1S2mux[i] == 1"]),
                ("Search Bus S2[7:0]", ["Broadcast to all", "PE0..PE15", "Selected when", "S1S2mux[i] == 0"]),
                ("16 Parallel PEs", ["PE_i computes", "candidate (i, j)", "Outputs PEout", "to Comparator"]),
            ],
            [
                ["Hardware Block", "Instances in top", "Input Signals", "Output Signals", "Architectural Role"],
                ["PE (Processing Element)", "16 (PE0..PE15)", "clock, R_i, S1, S2, mux_i, newDist_i", "Accumulate_i, Rpipe_i", "Computes |R - S| and accumulates D(i,j)"],
                ["Rpipe (Delay Register)", "15 (between PEs)", "clock, Rpipe_{i-1}", "R_i (to next PE)", "Delays R by 1 clock cycle per PE column"],
                ["Control (Explicit FSM)", "1 (u1)", "clock, start", "AddressR/S1/S2, mux, newDist, PEready", "Generates all memory addresses & strobes"],
                ["Comparator", "1 (u2)", "clock, CompStart, PEout, PEready", "BestDist, motionX, motionY", "Tracks minimum D(i,j) and latches (dx,dy)"],
            ],
            [
                "GREEN:Why Dual Search Ports (S1 and S2) Are Needed:",
                "When PE0 begins row m+1 of candidate (0,j) at horizontal offset 0, PE1..PE15 are still finishing row m",
                "at horizontal offsets 16..30! S1 supplies the left half of the search row while S2 supplies the right half.",
            ],
            [
                "// Inside module PE: 2-to-1 MUX selects between broadcast search buses S1 and S2:",
                "wire [7:0] S_selected = S1S2mux ? S1 : S2; // When S1S2mux[i]==1, use S1; otherwise use S2",
                "// PE0 always has S1S2mux[0] == 1 because candidate i=0 never crosses column 16!",
            ],
        ),
        (
            "Page 17: Understanding the 15-Cycle Rpipe Shift Register Pipeline Fill",
            "Cycle-by-Cycle Trace Showing How Reference Pixels Propagate Across PE0 -> PE15",
            [
                ("Cycle 0 (start=1)", ["R = r[0,0]", "PE0 samples r[0,0]", "newDist[0] = 1", "PE1..15 wait"]),
                ("Cycle 1", ["R = r[0,1]", "Rpipe0 -> PE1", "gets r[0,0]!", "newDist[1] = 1"]),
                ("Cycle k (0..15)", ["PE_k receives", "r[0,0] after k", "clock cycles", "newDist[k] = 1"]),
                ("Cycle 256 (0x100)", ["PE0 finishes all", "256 pixels!", "PEready[0] = 1", "Comparator checks"]),
            ],
            [
                ["Clock Cycle (count)", "AddressR", "Pixel Entering PE0", "Pixel Entering PE1", "Pixel Entering PE15", "Control Strobe Asserted"],
                ["count = 0 (13'h0000)", "8'h00", "r[0,0] (pixel 0)", "Undefined (X)", "Undefined (X)", "newDist = 16'h0001 (PE0 starts)"],
                ["count = 1 (13'h0001)", "8'h01", "r[0,1] (pixel 1)", "r[0,0] (pixel 0)", "Undefined (X)", "newDist = 16'h0002 (PE1 starts)"],
                ["count = 2 (13'h0002)", "8'h02", "r[0,2] (pixel 2)", "r[0,1] (pixel 1)", "Undefined (X)", "newDist = 16'h0004 (PE2 starts)"],
                ["count = 15 (13'h000F)", "8'h0F", "r[0,15] (pixel 15)", "r[0,14] (pixel 14)", "r[0,0] (pixel 0)", "newDist = 16'h8000 (PE15 starts)"],
                ["count = 255 (13'h00FF)", "8'hFF", "r[15,15] (pixel 255)", "r[15,14] (pixel 254)", "r[15,0] (pixel 240)", "PE0 latches 256th pixel diff"],
                ["count = 256 (13'h0100)", "8'h00", "r[0,0] (next row)", "r[15,15] (pixel 255)", "r[15,1] (pixel 241)", "PEready[0]=1, newDist[0]=1"],
            ],
            [
                "RED:★ TRAP: Expecting PE0's Distortion D(0,0) at Cycle 255 Instead of Cycle 256! ★",
                "At count = 255 (8'hFF), R = r[15,15] is at PE0's input, and AccumulateIn computes the 256th sum.",
                "Because Accumulate is a clocked DFF, it latches that 256th sum on the posedge entering count = 256!",
            ],
            [
                "// In module Control: Why newDist[m] and PEready[m] trigger when count[3:0] == m:",
                "newDist[m] = (count[7:0] == m);                      // Asserts once every 256 cycles at offset m",
                "PEready[m] = (newDist[m] && !(count < 256));         // Asserts at count = 256+m, 512+m, ..., 4096+m!",
            ],
        ),
        (
            "Page 18: Reproducing Lecture Notes Table 10.1 (p. 146) — Complete 4,111-Cycle Schedule",
            "Mathematical Derivation of Total Latency: 16 Rows x 256 Cycles + 15 Pipeline Fill Cycles = 4,111",
            [
                ("Row j = 0", ["count 0..255:", "PE0 accumulates", "count 256..271:", "PE0..15 ready!"]),
                ("Row j = 1..14", ["256 cycles/row", "PE0..15 evaluate", "16 candidates", "per row j"]),
                ("Row j = 15 (Last)", ["count 4096:", "PE0 ready (0,15)", "count 4111:", "PE15 ready (15,15)"]),
                ("Total Latency", ["4111 cycles", "(count = 13'h100F)", "At 520 MHz:", "7,905.45 ns"]),
            ],
            [
                ["Cycle (Decimal)", "Cycle (Hex count)", "Active Event in Pipeline (Table 10.1, p. 146)", "Simulation Time @ 520 MHz"],
                ["count = 0", "13'h0000", "start=1; PE0 samples first pixel r[0,0], s[0,0]", "t = 1.92 ns"],
                ["count = 15", "13'h000F", "Rpipe filled; PE15 samples first pixel r[0,0], s[0,15]", "t = 30.77 ns"],
                ["count = 256", "13'h0100", "CompStart=1; PEready[0]=1 -> Comparator checks D(0,0)", "t = 494.21 ns"],
                ["count = 271", "13'h010F", "PEready[15]=1 -> Comparator checks D(15,0) (Row 0 done)", "t = 523.06 ns"],
                ["count = 4096", "13'h1000", "PEready[0]=1 -> Comparator checks D(0,15) (Last row PE0)", "t = 7,876.61 ns"],
                ["count = 4111", "13'h100F", "PEready[15]=1 -> Comparator checks D(15,15); completed=1!", "t = 7,905.45 ns"],
            ],
            [
                "BLUE:Formula for Total Execution Cycles (Chapter 10, p. 146):",
                "Total Cycles = (16 candidate rows) x (16x16 pixels per candidate) + (15 Rpipe fill cycles)",
                "             = 16 x 256 + 15 = 4,096 + 15 = 4,111 clock cycles (Hex: 13'h100F).",
            ],
            [
                "// Converting cycle count to wall-clock time at 520.02 MHz (T_clk = 1.9230 ns):",
                "// t_completion = 4,111 cycles * 1.9230 ns/cycle = 7,905.453 ns",
                "// In top_tb.v, running 'for (i = 0; i < 4112; i = i + 1) @(posedge clock);' covers all 4,111 cycles!",
            ],
        ),
        (
            "Page 19: Memory Address Generation Math — AddressR[7:0], AddressS1[9:0], AddressS2[9:0]",
            "How Bit Slices of count[11:0] Address the 16x16 Reference Macroblock and 31x31 Search Window",
            [
                ("count[11:0] Bits", ["[11:8] = Row j", "[7:4] = Pixel m", "[3:0] = Pixel n", "12-bit counter"]),
                ("AddressR[7:0]", ["= count[7:0]", "256 bytes (0..FF)", "Repeats 16 times", "(once per row j)"]),
                ("AddressS1[9:0]", ["Row: [11:8]+[7:4]", "Col: count[3:0]", "Stride = 31", "(x31 = x32 - x1)"]),
                ("AddressS2[9:0]", ["Row: ([11:8]+[7:4])", "- 1 (prev row)", "Col: [3:0] + 16", "Right half of S"]),
            ],
            [
                ["Counter Slice", "Bit Range", "Range", "Meaning in Nested Block-Matching Loop"],
                ["count[3:0]", "4 bits (0..15)", "n in 0..15", "Horizontal pixel column n inside 16x16 reference block (and PE index m)"],
                ["count[7:4]", "4 bits (0..15)", "m in 0..15", "Vertical pixel row m inside 16x16 reference block"],
                ["count[7:0]", "8 bits (0..255)", "0..255", "AddressR[7:0] = 16*m + n (scans all 256 reference pixels per candidate row)"],
                ["count[11:8]", "4 bits (0..15)", "j in 0..15", "Vertical candidate block row index j in search window"],
                ["temp[4:0]", "count[11:8]+count[7:4]", "0..30", "Vertical row (j + m) inside the 31-row search window S"],
            ],
            [
                "GREEN:Clever Hardware Trick: Multiplying by 31 Without a Multiplier!",
                "Since the search window is 31 pixels wide, row (j+m) starts at byte address 31*(j+m).",
                "In binary, 31 * temp = (32 - 1) * temp = {temp[4:0], 5'b00000} - temp! Zero multipliers needed!",
            ],
            [
                "// In module Control (Lecture Notes p. 149): Multiplying row index by 31 using shift-and-subtract:",
                "AddressR = count[7:0];                                      // Reference pixel address (0..255)",
                "temp = count[11:8] + count[7:4];                            // Search row index y = j + m (0..30)",
                "AddressS1 = ({temp[4:0], 5'b00000} - temp) + count[3:0];    // 31*y + n (left half cols 0..15)",
                "temp = temp - 1;                                            // Previous search row y - 1",
                "AddressS2 = ({temp[4:0], 5'b00000} - temp) + count[3:0] + 16; // 31*(y-1) + n + 16 (right half cols 16..30)",
            ],
        ),
        (
            "Page 20: Deep Dive into the 8-Bit Saturating Adder in PE (Section 10.4.1, p. 147)",
            "Why Professor Mahmoodi's Baseline PE Uses {Carry, AccumulateIn} Saturation at 8'hFF",
            [
                ("8-Bit Accumulate", ["Holds partial SAD", "Range: 0..255", "8 D flip-flops", "per PE"]),
                ("9-Bit Addition", ["{Carry, AccIn} =", "Accumulate + diff", "Carry = bit [8]", "Detects > 255"]),
                ("Saturation MUX", ["if (Carry == 1)", "AccIn = 8'hFF", "Clamps at 255", "Prevents wrap!"]),
                ("New Candidate", ["if (newDist == 1)", "AccIn = diff", "Starts fresh sum", "with 1st pixel"]),
            ],
            [
                ["Accumulate (Old)", "difference |R-S|", "9-Bit Raw Sum", "Carry Bit [8]", "Without Saturation (Wrap Bug)", "With Saturation (8'hFF Clamp)"],
                ["8'd100 (8'h64)", "8'd50 (8'h32)", "9'd150 (9'h096)", "1'b0", "8'd150 (8'h96)", "8'd150 (8'h96) — Exact"],
                ["8'd200 (8'hC8)", "8'd55 (8'h37)", "9'd255 (9'h0FF)", "1'b0", "8'd255 (8'hFF)", "8'd255 (8'hFF) — Exact"],
                ["8'd200 (8'hC8)", "8'd56 (8'h38)", "9'd256 (9'h100)", "1'b1", "8'd0 (8'h00) -> FALSE ZERO!", "8'd255 (8'hFF) — Saturated"],
                ["8'd255 (8'hFF)", "8'd255 (8'hFF)", "9'd510 (9'h1FE)", "1'b1", "8'd254 (8'hFE) -> WRAPPED!", "8'd255 (8'hFF) — Saturated"],
            ],
            [
                "BLUE:Why Chapter 10 Included Saturation in the 8-Bit Design (p. 147):",
                "If an 8-bit accumulator wrapped modulo 256, a terrible block with D(i,j) = 256 would wrap to 8'h00 and look",
                "like a perfect zero-distortion match! Saturation clamps any sum >= 255 at 8'hFF to prevent modulo wrap-around.",
            ],
            [
                "// Original 8-bit saturating accumulator in module PE (Lecture Notes p. 147):",
                "{Carry, AccumulateIn} = Accumulate + difference; // 9-bit addition captures Carry out of bit 7",
                "if (Carry == 1) AccumulateIn = 8'hFF;            // Clamp at 255 (8'hFF) if unsigned overflow occurs",
                "if (newDist == 1) AccumulateIn = difference;     // Reset accumulator to 1st pixel diff on new block",
            ],
        ),
        (
            "Page 21: ★ TRAP: The 8-Bit Saturation & Strict Inequality (<) Boundary Failure Mode! ★",
            "Mathematical Proof of What Happens When All 256 Candidate Blocks Have D(i,j) >= 255",
            [
                ("CompStart == 0", ["BestDist <= 8'hFF", "Initialized to 255", "motionX <= X", "motionY <= X"]),
                ("Candidate (i,j)", ["If D(i,j) >= 255", "PE saturates to", "newDist = 8'hFF", "for every PE"]),
                ("Strict '<' Test", ["if (newDist <", "BestDist)", "8'hFF < 8'hFF", "is FALSE (0)!"]),
                ("Resulting Bug", ["newBest stays 0!", "motionX/Y never", "latch (remain X)", "or tie at (-6,0)"]),
            ],
            [
                ["Testbench Case", "True Minimum D(i,j)", "8-Bit PE Output", "Comparator Test (newDist < BestDist)", "8-Bit Outcome"],
                ["top_tb_direct.v (Exact Match)", "D(15,0) = 0", "8'h00", "8'h00 < 8'hFF is TRUE (newBest=1)", "PASS (BestDist=00)"],
                ["top_tb.v (+1 Offset at -5,+7)", "D(3,15) = 256", "8'hFF (Saturated!)", "8'hFF < 8'hFF is FALSE (newBest=0)!", "FAIL (Ties at -6,0 / FF)"],
                ["All-FF / All-00 Max Contrast", "D(i,j) = 65,280", "8'hFF (Saturated!)", "8'hFF < 8'hFF is FALSE (newBest=0)!", "FAIL (motionX/Y = xx!)"],
            ],
            [
                "RED:★ KEY INSIGHT FOR PRESENTATION SLIDE 17 & TEAMMATE QUESTIONS: ★",
                "In top_tb.v, the embedded match at (-5,+7) has a +1 offset on all 256 pixels, so D(-5,+7) = 256.",
                "In 8-bit RTL, 256 saturates to 8'hFF, tying an earlier random block (at -6,0) that also hit 8'hFF!",
                "And when all blocks have D(i,j) >= 255, 8'hFF < 8'hFF is NEVER true, leaving motionX/Y uninitialized (X)!",
            ],
            [
                "// In 8-bit module Comparator (Lecture Notes p. 148):",
                "if (CompStart == 0) BestDist <= 8'hFF;       // Initialized to 255",
                "// ...",
                "if ((|PEready == 0) || (CompStart == 0)) newBest = 0;",
                "else if (newDist < BestDist) newBest = 1;    // Strict '<' is FALSE when newDist == 8'hFF and BestDist == 8'hFF!",
                "else newBest = 0;",
            ],
        ),
        (
            "Page 22: The 16-Bit Non-Saturating Datapath Solution — Exact SAD Resolution Up to 65,280",
            "How Widening Accumulate[15:0], PEout[255:0], and BestDist[15:0] Eliminates Saturation",
            [
                ("16-Bit PE Adder", ["Accumulate[15:0]", "+ {8'd0, diff}", "Max = 65,280", "Zero overflow!"]),
                ("256-Bit PEout", ["16 PEs x 16 bits", "= PEout[255:0]", "Flattened bus", "to Comparator"]),
                ("BestDist Init", ["CompStart == 0:", "BestDist <=", "16'hFFFF (65,535)", "> 16'hFF00!"]),
                ("Exact Selection", ["16'hFF00 < 16'hFFFF", "is TRUE (1)!", "16'h0100 < 16'h4978", "Selects (-5,+7)!"]),
            ],
            [
                ["Signal / Bus Name", "8-Bit Baseline Width", "16-Bit Upgraded Width", "8-Bit Max Value", "16-Bit Max Value"],
                ["PE: Accumulate, AccumulateIn", "[7:0] (8 bits)", "[15:0] (16 bits)", "255 (8'hFF, saturates)", "65,280 (16'hFF00, exact)"],
                ["top: PEout flattened bus", "[127:0] (16 x 8b)", "[255:0] (16 x 16b)", "16 x 8-bit slices", "16 x 16-bit slices"],
                ["Comparator: BestDist, newDist", "[7:0] (8 bits)", "[15:0] (16 bits)", "Init 8'hFF (255)", "Init 16'hFFFF (65,535)"],
                ["top: BestDist output port", "output [7:0] BestDist", "output [15:0] BestDist", "8'h00 .. 8'hFF", "16'h0000 .. 16'hFF00"],
            ],
            [
                "GREEN:Mathematical Proof of Non-Saturation in 16 Bits:",
                "For any 8-bit pixels r, s in [0, 255], |r - s| <= 255. Over 256 pixels:",
                "D(i,j) = Sum_{k=1..256} |r_k - s_k| <= 256 * 255 = 65,280 (16'hFF00) < 65,535 (16'hFFFF = 2^16 - 1).",
                "Therefore, a 16-bit unsigned adder NEVER overflows and NEVER requires saturation clamping!",
            ],
            [
                "// Upgraded 16-bit non-saturating adder in module PE (rtl/16bit/top.v):",
                "AccumulateIn = Accumulate + {8'd0, difference}; // Zero-extend 8-bit difference to 16 bits and add",
                "if (newDist == 1) AccumulateIn = {8'd0, difference}; // Initialize to 1st pixel difference on new block",
            ],
        ),
        (
            "Page 23: ★ TRAP: The 12-Bit Counter Wrap-Around at Cycle 4096 & Terminal Hold Fix! ★",
            "Why Extending count to [12:0] and Holding at 13'h100F (Cycle 4111) Prevents Post-Search Corruption",
            [
                ("12-Bit Counter", ["count[11:0]", "Max = 12'hFFF", "(Cycle 4095)", "Wraps to 0x000!"]),
                ("What Happens @4096", ["count wraps to 0", "count < 256 is 1!", "CompStart drops", "to 0 at 4096!"]),
                ("Why That Fails", ["CompStart == 0", "resets BestDist", "to FFFF before", "row 15 finishes!"]),
                ("13-Bit Hold Fix", ["count[12:0] runs", "to 13'h100F (4111)", "completed <= 1", "Freezes outputs!"]),
            ],
            [
                ["Clock Cycle", "Original 12-Bit count[11:0]", "Original CompStart", "Upgraded 13-Bit count[12:0]", "Upgraded CompStart & completed"],
                ["Cycle 0..255", "12'h000 .. 12'h0FF", "1'b0 (BestDist=Init)", "13'h0000 .. 13'h00FF", "CompStart=0, completed=0"],
                ["Cycle 256..4095", "12'h100 .. 12'hFFF", "1'b1 (Active search)", "13'h0100 .. 13'h0FFF", "CompStart=1, completed=0"],
                ["Cycle 4096 (Row 15 PE0)", "Wraps to 12'h000! (TRAP!)", "Drops to 1'b0! (RESETS!)", "13'h1000 (4096)", "CompStart=1 (PE0 Row 15 evaluated!)"],
                ["Cycle 4111 (Row 15 PE15)", "12'h00F (Corrupted)", "1'b0 (BestDist wiped!)", "13'h100F (4111)", "CompStart=1, completed<=1 (Latched!)"],
                ["Cycle 4112+", "Continues counting...", "Overwrites state", "Holds at 13'h100F", "completed=1 -> PEready=0 (Frozen!)"],
            ],
            [
                "RED:★ CRITICAL BUG IN ORIGINAL 12-BIT CONTROL COUNTER: ★",
                "Because the last 16 comparisons occur at cycles 4096..4111 (13'h1000..13'h100F), a 12-bit counter",
                "wraps around to 0 at cycle 4096, causing 'if (count < 256) CompStart = 0' to wipe out BestDist!",
                "Widening count to [12:0] and latching 'completed <= 1' at 13'h100F fixes this completely!",
            ],
            [
                "// In module Control (rtl/16bit/top.v):",
                "reg [12:0] count; reg completed;",
                "always @(posedge clock) begin",
                "  if (start == 0) begin count <= 13'd0; completed <= 1'b0; end",
                "  else if (completed == 1'b0) begin",
                "    if (count == 13'h100F) completed <= 1'b1; // Freeze after cycle 4111 (all 256 blocks done)",
                "    else count <= count + 13'd1;",
                "  end",
                "end",
            ],
        ),
        (
            "Page 24: Complete Hardware-to-Verilog Signal Dictionary for module top",
            "Master Reference Table of Every Input, Output, Internal Bus, and Flip-Flop in the Design",
            [
                ("Top Inputs (27b)", ["clock (1b)", "start (1b)", "R[7:0] (8b)", "S1[7:0], S2[7:0]"]),
                ("Top Outputs (60b)", ["BestDist[15:0]", "motionX/Y[7:0]", "AddressR[7:0]", "AddressS1/S2[9:0]"]),
                ("Control Buses", ["S1S2mux[15:0]", "newDist[15:0]", "PEready[15:0]", "CompStart (1b)"]),
                ("Register Count", ["16x16b Acc = 256", "16x8b Rpipe = 128", "Control = 14", "Comp = 32 (430+)"]),
            ],
            [
                ["Signal Name", "Direction / Scope", "8-Bit Width", "16-Bit Width", "Clocked or Comb", "Functional Description"],
                ["clock", "input (top)", "1 bit", "1 bit", "Clock (520 MHz)", "Global rising-edge clock (1.923 ns period)"],
                ["start", "input (top)", "1 bit", "1 bit", "Synchronous Ctrl", "0 = reset counter/BestDist; 1 = run 4,111-cycle search"],
                ["R, S1, S2", "input (top)", "[7:0] each", "[7:0] each", "Registered in TB", "Reference pixel byte and dual search window pixel bytes"],
                ["AddressR", "output (top)", "[7:0]", "[7:0]", "Comb from count", "8-bit address (0..255) into external RMEM"],
                ["AddressS1, AddressS2", "output (top)", "[9:0] each", "[9:0] each", "Comb from count", "10-bit addresses (0..960) into external SMEM"],
                ["BestDist", "output reg (top)", "[7:0]", "[15:0]", "Clocked DFF", "Minimum distortion D(i*,j*) found across all candidates"],
                ["motionX, motionY", "output reg (top)", "[7:0] each", "[7:0] each", "Clocked DFF", "Signed 2's complement motion vector (i*-8, j*-8)"],
                ["PEout", "wire (internal)", "[127:0]", "[255:0]", "Clocked in PEs", "Concatenated bus of all 16 PE Accumulate registers"],
            ],
            [
                "BLUE:Flip-Flop Count Calculation (Why Synthesis Reports ~449 Flip-Flops):",
                "• 16 PEs x (16-bit Accumulate + 8-bit Rpipe) = 384 FFs  |  • 15 Rpipe modules x 8-bit = 120 FFs (optimized/shared)",
                "• Control: 13-bit count + 1-bit completed = 14 FFs      |  • Comparator: 16-bit BestDist + 8-bit X + 8-bit Y = 32 FFs.",
            ],
            [
                "// Top-level module signature (rtl/16bit/top.v):",
                "module top (clock, start, BestDist, motionX, motionY, AddressR, AddressS1, AddressS2, R, S1, S2);",
                "  input clock, start; input [7:0] R, S1, S2;",
                "  output [15:0] BestDist; output [7:0] motionX, motionY, AddressR; output [9:0] AddressS1, AddressS2;",
            ],
        ),
    ]
    pages.extend(part2_topics)

    return pages


def generate_remaining_pages(pages):
    """Programmatically builds Pages 25..100 from the real RTL, Testbench, EDA TCL, Python, and Git files."""
    # Helper to chunk real source files into line-by-line commented notebook pages
    def add_code_walkthrough_pages(part_label, file_rel, title_prefix, subtitle_prefix, chunk_size, max_pages, trap_msg):
        fpath = REPO_ROOT / file_rel
        raw_lines = fpath.read_text(encoding="utf-8", errors="ignore").splitlines() if fpath.exists() else [f"// {file_rel}"]
        for idx in range(max_pages):
            pnum = len(pages) + 1
            start_l = idx * chunk_size
            end_l = min(len(raw_lines), (idx + 1) * chunk_size)
            chunk = raw_lines[start_l:end_l] if start_l < len(raw_lines) else raw_lines[:chunk_size]
            numbered = [f"{start_l + i + 1:03d}: {line}" for i, line in enumerate(chunk)]
            pages.append((
                f"Page {pnum}: {title_prefix} — Lines {start_l+1}..{start_l+len(chunk)} ({file_rel})",
                f"{subtitle_prefix} | Step-by-Step Line-by-Line Hardware & Syntax Walkthrough",
                [
                    ("1. Read Syntax", [f"File: {Path(file_rel).name}", f"Lines {start_l+1}..{start_l+len(chunk)}", "Check bit widths", "Check port names"]),
                    ("2. Hardware Map", ["Blocking '=' comb", "Nonblocking '<='", "Posedge clock DFF", "MUX '? :' logic"]),
                    ("3. Verify Sim", ["vcs -full64", "Zero lint errors", "Check waves.fsdb", "Verify hex values"]),
                    ("4. Custom Naming", ["Keep module top", "Rename TB/logs", "freely on new Mac", "100% compatible"]),
                ],
                [
                    ["Line Range", "Source File", "Construct Type", "Hardware / Verification Meaning"],
                    [f"L{start_l+1}..L{start_l+min(5,len(chunk))}", file_rel, "Declarations / Header", "Defines module ports, bit widths, or script imports"],
                    [f"L{start_l+6}..L{start_l+min(12,len(chunk))}", file_rel, "Datapath / Control", "Implements SAD accumulation, address math, or EDA step"],
                    [f"L{start_l+13}..L{start_l+len(chunk)}", file_rel, "Sequential / Output", "Latches state on rising clock edge or verifies output"],
                ],
                [trap_msg[0], trap_msg[1], trap_msg[2]],
                numbered[:24],
            ))

    # Pages 25..32: 8-bit & 16-bit Verilog RTL (rtl/8bit/top.v & rtl/16bit/top.v)
    add_code_walkthrough_pages(
        "PART III: VERILOG RTL", "rtl/8bit/top.v",
        "Baseline 8-Bit Saturating Verilog RTL", "Chapter 10 Section 10.4 Reference Implementation",
        28, 4,
        ("RED:★ TRAP: 8-Bit Carry Saturation Clamps Accumulate at 8'hFF (255)! ★",
         "In rtl/8bit/top.v, {Carry, AccumulateIn} = Accumulate + difference saturates at 8'hFF whenever Carry==1.",
         "Keep rtl/8bit/top.v intact as your baseline reference before creating rtl/16bit/top.v!")
    )
    add_code_walkthrough_pages(
        "PART III: VERILOG RTL", "rtl/16bit/top.v",
        "Upgraded 16-Bit Non-Saturating Verilog RTL", "Full-Range SAD D(i,j) up to 16'hFF00 + Cycle-4111 Terminal Hold",
        30, 4,
        ("GREEN:★ KEY UPGRADE: 16-Bit Accumulate[15:0], PEout[255:0], BestDist[15:0] & count==13'h100F! ★",
         "In rtl/16bit/top.v, AccumulateIn = Accumulate + {8'd0, difference} never saturates across 256 pixels,",
         "and Control holds at count == 13'h100F (completed <= 1'b1) so BestDist/motionX/Y never wrap around!")
    )

    # Pages 33..44: Testbench Variations (top_tb_direct.v, top_tb.v, top_tb_16bit.v, selfcheck)
    add_code_walkthrough_pages(
        "PART IV: 520 MHz TESTBENCHES", "tb/16bit/top_tb_direct.v",
        "Test Case 1 — File-Driven Exact Match (BestDist = 16'h0000)", "Reading ref.txt & search.txt at 520 MHz (1.923 ns period)",
        26, 3,
        ("BLUE:★ TEST CASE 1 EXPECTED OUTPUT: BestDist = 16'h0000 | motionX = F8 (-8) or 07 (+7) ★",
         "Always use `timescale 1ns/100fs and always #0.9615 clock = ~clock; so T_clk = 1.9230 ns (520.02 MHz).",
         "Use @(posedge clock); #0.02; (20 ps hold offset) when driving R, S1, S2 from Rmem and Smem.")
    )
    add_code_walkthrough_pages(
        "PART IV: 520 MHz TESTBENCHES", "tb/16bit/top_tb.v",
        "Test Case 2 — Random Memory + 1-LSB Offset (BestDist = 16'h0100)", "Target Motion Vector (-5, +7) -> motionX = 8'hFB, motionY = 8'h07",
        26, 3,
        ("RED:★ WHY 8-BIT GIVES 8'hFF (-6,0) WHILE 16-BIT GIVES 16'h0100 (-5,+7): ★",
         "256 pixels x (+1 offset per pixel) = 256 (16'h0100). In 8-bit RTL, 256 saturates to 8'hFF and ties",
         "strict '<'. In 16-bit RTL, 16'h0100 < 16'h4978 selects exact target motionX = FB (-5), motionY = 07 (+7)!")
    )
    add_code_walkthrough_pages(
        "PART IV: 520 MHz TESTBENCHES", "tb/16bit/top_tb_16bit.v",
        "Test Case 3 — Maximum-Distortion Boundary (BestDist = 16'hFF00)", "Proving 256 x 255 = 65,280 (16'hFF00) < 16'hFFFF Initial BestDist",
        26, 3,
        ("GREEN:★ ANSWERING YOUR TEAMMATE'S QUESTION ABOUT BestDist = FF00: ★",
         "BestDist = 16'hFF00 occurs ONLY in this maximum-distortion boundary testbench (R=00, S=FF -> 256*255=65,280).",
         "In the standard exact-match testbench (ref.txt/search.txt), BestDist is 16'h0000!")
    )
    add_code_walkthrough_pages(
        "PART IV: 520 MHz TESTBENCHES", "verification/v6_clean/motion_pe_comparator_selfcheck_tb.sv",
        "Test Case 4 — Automated Multi-Vector Self-Checking Testbench", "Verifying 0000 (Exact Match), 0003 (+3 Offset), and FF00 (Max Contrast)",
        28, 3,
        ("BLUE:★ SELF-CHECKING ASSERTIONS IN VERILOG: ★",
         "Using automatic tasks and explicit if (BestDist !== expected) $fatal(1, ...) guarantees every simulation",
         "verifies exact numerical outputs automatically in Synopsys VCS.")
    )

    # Pages 45..64: Synopsys VCS, Verdi nWave GUI, Fusion Compiler 14nm P&R, ICV DRC, PrimeTime 3-Corner STA
    eda_topics = [
        ("Page 45: Compiling & Running Synopsys VCS at 520 MHz on mahmoodi",
         "Exact CLI Flags (-full64 -debug_access+all -sverilog) and Reading Simulation Logs"),
        ("Page 46: Launching Synopsys Verdi (nWave) via XQuartz & Loading waves.fsdb",
         "Step-by-Step Mouse Clicks: File -> Open, Signal -> Get Signals (Press 'g'), Adding u1 Hierarchy"),
        ("Page 47: Formatting Verdi nWave Waveforms — Hexadecimal Radix, Signal Colors, and Time Cursors",
         "How to Match Your Teammate's Waveform Style With Full Hierarchy Labels & Register Hex Values"),
        ("Page 48: Zooming In (Press 'z') vs. Zoom Full (Press 'f') in Verdi nWave",
         "Capturing Both the 0..7,905.45 ns Full Scrollbar Overview and Individual Hex Transition Boxes"),
        ("Page 49: Annotated Verdi Waveform Walkthrough 1 — 8-Bit Row-1 Saturation (count = 0x00F9..0x0110)",
         "Visual Inspection of V9_fig7_orig8bit_row1_nWave.png (Accumulate Clamping at 8'hFF, newBest = 0)"),
        ("Page 50: Annotated Verdi Waveform Walkthrough 2 — 8-Bit Terminal Cycle (count = 0x100F, t = 7,905.45 ns)",
         "Visual Inspection of V9_fig8_orig8bit_complete_nWave.png (BestDist = 8'hFF, motionX/Y Unupdated)"),
        ("Page 51: Annotated Verdi Waveform Walkthrough 3 — 16-Bit Exact Match (BestDist = 16'h0000)",
         "Visual Inspection of V9_fig10_16bit_perfect_match_0000_nWave.png (PE15 Latches 0000 at count = 0x010F)"),
        ("Page 52: Annotated Verdi Waveform Walkthrough 4 — 16-Bit Max Distortion (BestDist = 16'hFF00)",
         "Visual Inspection of V9_fig9_16bit_saturation_row1_nWave.png (PE0 Latches FF00 < FFFF at count = 0x0100)"),
        ("Page 53: Writing the 520 MHz Synopsys Design Constraints File (top_520mhz.sdc)",
         "create_clock -period 1.923, set_input_delay 0.5, set_output_delay 0.5, set_clock_uncertainty 0.2"),
        ("Page 54: SAED14nm FinFET PDK Architecture — NDM Reference Libraries & TLU+ Parasitic Corners",
         "Mapping minTLU (FAST 0.88V 125C), nomTLU (TYPICAL 0.80V 25C), and maxTLU (SLOW 0.72V -40C)"),
        ("Page 55: Synopsys Fusion Compiler Step 1 — Creating the NDM Design Library & Reading RTL",
         "create_lib, analyze -format verilog rtl/16bit/top.v, elaborate top, set_top_module top"),
        ("Page 56: Synopsys Fusion Compiler Step 2 — MCMM Corner Setup & Initial Synthesis (compile_fusion)",
         "Verifying Zero Memory Macros (0 SRAM/ROM) and Checking Initial Gate-Level Netlist QoR"),
        ("Page 57: Synopsys Fusion Compiler Step 3 — Floorplanning (125.07 um x 62.80 um, 52.08% Utilization)",
         "initialize_floorplan -core_utilization 0.52, place_pins -self, and Avoiding Routing Congestion"),
        ("Page 58: Synopsys Fusion Compiler Step 4 — Power Network Synthesis (PNS: Dual Ring + M8/M9 Mesh)",
         "compile_pg, connect_pg_net -automatic, and Verifying Zero PG Open/Short Violations"),
        ("Page 59: Synopsys Fusion Compiler Step 5 — Placement & Clock Tree Synthesis (clock_opt)",
         "Building a Low-Skew Clock Tree Across all 449 Flip-Flops at 520 MHz (1.923 ns Period)"),
        ("Page 60: Synopsys Fusion Compiler Step 6 — Detail Routing (route_auto + route_opt) & Filler Cells",
         "create_stdcell_fillers, connect_pg_net, and Achieving Zero Route DRC Errors"),
        ("Page 61: Synopsys Fusion Compiler Step 7 — Exporting Netlist (.v), 3-Corner SPEF, and Merged GDSII",
         "write_verilog, write_parasitics, write_gds (80 MB top.gds with 0 Unplaced Cells / 0 GDS-110)"),
        ("Page 62: Inspecting the Routed 14nm Chip in Fusion Compiler GUI via XQuartz (fc_shell -gui)",
         "Visual Walkthrough of v9_signoff_clean_layout.png — Metal Layers M1..M9, Core Ring, and Cell Density"),
        ("Page 63: Running Standalone Synopsys IC Validator (icv) Sign-Off DRC & LVS Verification",
         "Verifying 0 / 242 Rule Violations (LAYOUT ERRORS RESULTS: CLEAN) and 0 LVS Mismatches"),
        ("Page 64: Running Standalone 3-Corner Synopsys PrimeTime (pt_shell) Post-Layout STA",
         "Verifying Setup & Hold Closure Across FAST (+0.71/0.00ns), TYPICAL (+0.54/+0.04ns), SLOW (+0.22/+0.14ns)"),
    ]
    for title, sub in eda_topics:
        pages.append((
            title, sub,
            [
                ("1. XQuartz Shell", ["ssh -Y mahmoodi", "cd ~/me_asic_new_v1", "source /apps/settings", "Verify DISPLAY"]),
                ("2. Execute Tool", ["vcs / verdi", "fc_shell -f ...", "icv -vue ...", "pt_shell -f ..."]),
                ("3. Check Report", ["0 syntax errors", "0/242 DRC clean", "Setup WNS > 0", "Hold WNS >= 0"]),
                ("4. Save Evidence", ["Capture PNG", "Copy .rpt logs", "scp to MacBook", "Verify gate PASS"]),
            ],
            [
                ["Sign-Off Parameter", "Target Requirement", "Verified 14nm Result (V9)", "Sign-Off Tool"],
                ["Clock Period / Freq", "<= 2.000 ns (>= 500 MHz)", "1.923 ns (520.02 MHz)", "top_520mhz.sdc"],
                ["Die / Core Area", "Compact 14nm FinFET core", "125.07 x 62.80 um (7,854.40 um2 die)", "Fusion Compiler"],
                ["Cell Count / Area", "0 SRAM/ROM macros in top", "8,230 logic cells (449 FFs) / 3,416.18 um2", "Fusion Compiler"],
                ["Total Power (TT 25C)", "Report dynamic + leakage", "0.890 mW (0.889 mW dyn + 0.00089 mW leak)", "Fusion Compiler"],
                ["IC Validator DRC/LVS", "0 DRC violations, 0 LVS", "0 / 242 DRC violations (CLEAN), 0 LVS", "IC Validator"],
                ["PrimeTime 3-Corner STA", "Setup & Hold >= 0 all corners", "FAST +0.71/0.00, TYP +0.54/+0.04, SLOW +0.22/+0.14", "PrimeTime (pt_shell)"],
            ],
            [
                "GREEN:★ VERIFIED SIGN-OFF CHECKPOINT: ★",
                f"Focus of {title.split(':')[0]}: {sub}.",
                "Always inspect the generated log and .rpt file before advancing to the next stage!",
            ],
            [
                "# Copy-pasteable commands on 926784856@mahmoodi.rcc.at.sfsu.edu (inside XQuartz xterm):",
                "source /apps/settings && cd ~/me_asic_new_v1",
                "vcs -full64 -sverilog -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_direct && ./simv_direct",
                "fc_shell -f scripts/run_fc_v9.tcl | tee logs/fc_v9.log",
                "icv -vue -i results/top.gds -c top -f GDSII /apps/synopsys/SAED14_EDK/tech/icv_drc/saed14nm_1p9m_drc_rules.rs",
                "pt_shell -f scripts/run_pt_v9.tcl | tee logs/pt_v9.log",
            ],
        ))

    # Pages 65..88: Python Slide Builders, Engineering Report Builders, Stage-Gate Verification, & Packaging
    add_code_walkthrough_pages(
        "PART VI: PYTHON AUTOMATION", "scripts/build_v9_final_slides.py",
        "Python Slide Deck Automation (python-pptx)", "Building Clean Presentation Slides With Zero Text Overlap",
        30, 8,
        ("BLUE:★ SLIDE VARIATION TIP: Customize RGB Colors & Titles in python-pptx! ★",
         "Change ACCENT = RGBColor(0, 84, 116) to any custom palette (e.g., SFSU Purple/Gold or Slate Navy)",
         "on your new laptop to give your presentation a unique visual theme while keeping all verified data!")
    )
    add_code_walkthrough_pages(
        "PART VI: PYTHON AUTOMATION", "scripts/build_v9_final_engineering_report.py",
        "Python Engineering Report Generator (ReportLab)", "Building Publication-Grade PDF Reports With Embedded Waveforms & Layouts",
        30, 8,
        ("GREEN:★ REPORT VARIATION TIP: Customize Report Title, Author Header, & Table Styling! ★",
         "ReportLab Platypus (SimpleDocTemplate, Paragraph, Table, Image) lets you regenerate the entire",
         "engineering report PDF in 2 seconds whenever you update a waveform screenshot or timing table!")
    )
    add_code_walkthrough_pages(
        "PART VI: PYTHON AUTOMATION", "scripts/v6_stage_gate.py",
        "Automated 11-Gate Self-Checking Verification Harness", "Ensuring 100% of Requirements Are VERIFIED With Zero Missing Artifacts",
        30, 8,
        ("RED:★ SELF-HEALING VERIFICATION RULE: Never Submit Until FINAL_GATE_RESULT == PASS! ★",
         "Running python3 scripts/v6_stage_gate.py --scope full checks all 7 simulation logs, GDS completeness,",
         "ICV DRC = 0/242, LVS = 0, and 3-corner PrimeTime setup/hold slacks automatically!")
    )

    # Pages 89..100: Git/GitHub Repository Variations, Debugging Encyclopedia, & Final Sign-Off Scorecard
    part7_topics = [
        ("Page 89: Packaging All Submission Deliverables (scripts/package_v9_submission.py)",
         "Automatically Bundling Verilog RTL, Testbenches, SDC, SPEF, Reports, Slides, and PDF into a Clean .zip"),
        ("Page 90: Presentation & Document Variations — How to Customize Your New Project Version",
         "Side-by-Side Guide for Renaming Repos, Slide Themes, and Directory Structures on Your Brand-New Laptop"),
        ("Page 91: Git & GitHub Beginner's Visual Guide — Working Tree, Staging Area, Local Repo, & Remote",
         "Understanding git init, git status, git add, git commit, git branch -M main, and git push -u origin main"),
        ("Page 92: Creating a Brand-New GitHub Repository With Your New Project Naming",
         "Step-by-Step Browser & CLI Instructions for Creating a Fresh Repository on github.com/new"),
        ("Page 93: Configuring Git SSH Keys & .gitignore on Your Brand-New MacBook Air",
         "Preventing Huge Binary Files (.fsdb, .ndm, .gds) From Exceeding GitHub's 100 MB Per-File Limit"),
        ("Page 94: Writing a Professional GitHub README.md With Architecture Tables & Reproduction Commands",
         "Structuring Your Repository Front Page So Instructors and Recruiters Can Verify Your ASIC Flow Immediately"),
        ("Page 95: Pushing Your Complete Manual Project Build From Your New Laptop to GitHub",
         "Exact Sequence of Terminal Commands to Commit, Tag (v1.0-signoff), and Verify Your Remote GitHub Tree"),
        ("Page 96: Beginner Debugging Encyclopedia — Part 1: XQuartz, GlobalProtect VPN, & SSH Errors",
         "Instant Fixes for 'DISPLAY is not set', 'Permission denied (publickey)', and 'command not found'"),
        ("Page 97: Beginner Debugging Encyclopedia — Part 2: Verilog VCS & Verdi Waveform Issues",
         "Instant Fixes for Rounding #0.9615, Missing waves.fsdb, Unknown (X) Outputs, and Counter Wrap-Around"),
        ("Page 98: Beginner Debugging Encyclopedia — Part 3: Fusion Compiler, ICV DRC, & PrimeTime STA",
         "Instant Fixes for Core Utilization Congestion, Unplaced Cells (GDS-110), and Hold Time Violations"),
        ("Page 99: Master Start-to-Finish Command Cheat Sheet (New MacBook Air + XQuartz + mahmoodi + GitHub)",
         "Every Essential Command From Unboxing Your Laptop to Final GitHub Push on One Single Reference Page"),
        ("Page 100: Final 100% Verification Certificate & Complete 100-Page Sign-Off Scorecard",
         "All 11 Verification Gates Passed — Ready for 90-100% Course Project Score & Live Demonstration"),
    ]
    for title, sub in part7_topics:
        pages.append((
            title, sub,
            [
                ("1. Local Build", ["Run Python builders", "Run stage_gate.py", "Verify 11/11 PASS", "Check .gitignore"]),
                ("2. Git Stage", ["git init -b main", "git add .", "git status -s", "0 temp .daidir"]),
                ("3. Git Commit", ["git commit -m", "'Complete 520MHz", "14nm Motion Est", "ASIC Sign-Off'"]),
                ("4. GitHub Push", ["git remote add", "origin https://...", "git push -u", "origin main"]),
            ],
            [
                ["Symptom / Error Message", "Root Cause", "Exact One-Line Fix Command"],
                ["cannot open display / DISPLAY empty", "XQuartz not running or forgot ssh -Y", "open -a XQuartz && ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu"],
                ["vcs / fc_shell: command not found", "Forgot to source Synopsys settings", "source /apps/settings"],
                ["BestDist = 8'hFF on +1 offset TB", "8-bit PE saturation at 255", "Use rtl/16bit/top.v (BestDist = 16'h0100, X=FB, Y=07)"],
                ["BestDist = 16'hFF00 vs 16'h0000", "Max-contrast TB vs Exact-match TB", "Run top_tb_direct.v for 0000; top_tb_16bit.v for FF00"],
                ["remote: error: File > 100.00 MB", "Staged raw .gds or .fsdb in git", "Add *.fsdb *.gds *.ndm to .gitignore before git add"],
            ],
            [
                "GREEN:★ CONGRATULATIONS — 100-PAGE VISUAL ENGINEERING NOTEBOOK MANUAL COMPLETE! ★",
                f"{title} — {sub}",
                "Every step from XQuartz login on a brand-new laptop to 14nm GDSII/PrimeTime sign-off & GitHub push is verified!",
            ],
            [
                "# Final Master GitHub Push Sequence on Your Brand-New MacBook Air:",
                "cd ~/Developer/engr852-14nm-motion-estimator",
                "python3 scripts/v6_stage_gate.py --scope full   # Verify FINAL_GATE_RESULT PASS (11/11 gates)",
                "git init -b main && git add .",
                "git commit -m \"Complete 520 MHz SAED14nm Motion Estimator ASIC RTL, Physical Design, and Sign-Off\"",
                "git remote add origin https://github.com/<YOUR_GITHUB_USER>/<YOUR_NEW_REPO_NAME>.git",
                "git push -u origin main",
            ],
        ))

    assert len(pages) == 100, f"Expected 100 pages, got {len(pages)}"
    return pages


def get_part_title(pnum):
    if pnum <= 12:
        return "PART I: NEW MACBOOK, GLOBALPROTECT VPN, XQUARTZ & SSH"
    if pnum <= 24:
        return "PART II: CH. 10 SEC. 10.4 SAD THEORY & ARCHITECTURE"
    if pnum <= 32:
        return "PART III: 8-BIT & 16-BIT VERILOG RTL WALKTHROUGH"
    if pnum <= 44:
        return "PART IV: 520 MHz TESTBENCHES & STIMULUS VARIATIONS"
    if pnum <= 64:
        return "PART V: VCS, VERDI, FUSION COMPILER 14nm, ICV & PRIMETIME"
    if pnum <= 88:
        return "PART VI: PYTHON SLIDE, REPORT & STAGE-GATE AUTOMATION"
    return "PART VII: GITHUB VARIATIONS, DEBUGGING & FINAL SCORECARD"




# ==============================================================================
# ENHANCED FULL-PAGE DENSE RENDERING ENGINE (ZERO WASTED WHITE SPACE)
# Includes:
# - High-Contrast Terminal Execution Badges: [MACBOOK], [XQUARTZ], [926784856@mahmoodi], [OUTPUT]
# - Full 100%-Height Line-by-Line Commented Code & Script Walkthroughs per page (Zero Empty Space)
# - Section 5: Self-Healing Verification & Fallback Recovery Matrix (Plan A / Plan B / Plan C)
# - Real Pre-Given Server Script Pulling & Customization Instructions
# ==============================================================================

BADGE_MAC_BG = colors.HexColor("#1E3A8A")
BADGE_MAC_ROW = colors.HexColor("#DBEAFE")
BADGE_XQ_BG = colors.HexColor("#0F766E")
BADGE_XQ_ROW = colors.HexColor("#CCFBF1")
BADGE_SFSU_BG = colors.HexColor("#B45309")
BADGE_SFSU_ROW = colors.HexColor("#FEF3C7")
BADGE_OUT_BG = colors.HexColor("#15803D")
BADGE_OUT_ROW = colors.HexColor("#DCFCE7")
BOX_FALLBACK_BG = colors.HexColor("#FFFBEB")
INK_AMBER = colors.HexColor("#92400E")


def clean_glyphs(text):
    return str(text).replace("★", "[!]").replace("—", " - ").replace("–", "-")


def get_page_specific_eda_script_lines(pnum):
    """Returns real, line-by-line commented Synopsys TCL / Makefile / SDC / Shell commands for Pages 45..64."""
    tcl_dir = REPO_ROOT / "scripts" / "synopsys_tcl"

    def read_tcl_with_comments(fname, start=0, count=22, header_comment=""):
        p = tcl_dir / fname
        lines = []
        if header_comment:
            lines.append(header_comment)
        if p.exists():
            raw = [ln.rstrip() for ln in p.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
            subset = raw[start:start + count]
            for i, ln in enumerate(subset):
                lines.append(f"{start + i + 1:02d}: {ln}")
        return lines

    mapping = {
        45: [
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp -r ~/ENGR852_Project/16_v3b_final_asic_fc/scripts ~/me_asic_new_v1/",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cd ~/me_asic_new_v1 && tcsh",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ source ./scripts/synopsys_setup.tcl",
            "# --- Pre-Given Course Makefile (Makefile.starter) + 520 MHz VCS Compilation ---",
            *read_tcl_with_comments("Makefile.starter", 0, 16),
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ vcs -full64 -sverilog -debug_access+all -kdb \\",
            "TERM_SFSU:   rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_direct -l logs/vcs_direct.log",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ./simv_direct -l logs/simv_direct.log",
            "OUT_OK:    BestDist = 0000 (hex) = 0 (dec) | motionX = f8 (-8) | motionY = 07 (+7) [PASS]",
        ],
        46: [
            "TERM_XQ:   [student@MacBook ~ %] open -a XQuartz && echo $DISPLAY",
            "OUT_OK:    /private/tmp/com.apple.launchd.xxxx/org.xquartz:0  (Local X11 Server Active)",
            "TERM_XQ:   [student@MacBook ~ %] ssh -Y -o ForwardX11Trusted=yes 926784856@mahmoodi.rcc.at.sfsu.edu",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cd ~/me_asic_new_v1 && tcsh",
            "# --- Inside scripts/synopsys_setup.tcl (Pre-Given Server Setup Script) ---",
            *read_tcl_with_comments("synopsys_setup.tcl", 0, 14),
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ source ./scripts/synopsys_setup.tcl",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ verdi -ssf waves_16bit_direct.fsdb &",
            "OUT_OK:    Verdi GUI & nWave window pop up on your MacBook screen via XQuartz!",
        ],
        47: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ verdi -ssf waves_16bit_tb.fsdb &",
            "# --- Step-by-Step Verdi nWave Signal Selection & Hex Radix Formatting ---",
            "01: # In nWave Menu: Click 'Signal' -> 'Get Signals...' (or press keyboard shortcut 'g')",
            "02: # Left Pane (Signal Hierarchy): Click 'top_tb' -> Click 'u1 (top)' -> Click 'u1 (Control)'",
            "03: # Add Top Ports:   clock, start, BestDist[15:0], motionX[7:0], motionY[7:0]",
            "04: # Add Memory Bus:  AddressR[7:0], R[7:0], AddressS1[9:0], S1[7:0], AddressS2[9:0], S2[7:0]",
            "05: # Add Control Bus: u1.u1.count[12:0], u1.u1.completed, u1.CompStart, u1.PEready[15:0]",
            "06: # Add PE Array:    u1.u3.PE0.Accumulate[15:0] ... u1.u18.PE15.Accumulate[15:0]",
            "07: # Add Comparator:  u1.u2.newDist[15:0], u1.u2.newBest, u1.u2.vectorX[3:0], u1.u2.vectorY[3:0]",
            "08: # Click 'Append' -> Click 'OK' (All 22 signals appear in the black nWave canvas)",
            "09: # Press Ctrl+A (Select All Signals) -> Right-Click -> 'Radix' -> 'Hexadecimal'",
            "10: # Right-Click 'Signal' column header -> 'Signal Display Options' -> Enable 'Full Hierarchy Name'",
            "TERM_SFSU: # Save signal list so you never have to re-click signals manually:",
            "11: # In nWave Menu: Click 'File' -> 'Save Signal...' -> Save as 'scripts/me_signals.rc'",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ verdi -ssf waves_16bit_tb.fsdb -sswr scripts/me_signals.rc &",
            "OUT_OK:    All 22 hierarchical signals load automatically in Hexadecimal radix!",
        ],
        48: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ verdi -ssf waves_16bit_direct.fsdb -sswr scripts/me_signals.rc &",
            "# --- Step-by-Step Verdi nWave Zooming & Time Cursor Measurement ---",
            "01: # Keyboard Shortcut 'f' (Zoom Full): Shows full simulation 0.00 ns .. 7,905.45 ns",
            "02: # Notice at full 7,905 ns scale, 4,111 clock cycles are compressed into solid colored bands.",
            "03: # Keyboard Shortcut 'z' (Zoom In) or Left-Click-Drag across 480 ns .. 530 ns:",
            "04: #   -> Reveals Row-1 completion window (count = 13'h00F9 .. 13'h0110) with readable hex boxes!",
            "05: # Left-Click at t = 494.21 ns (count = 13'h0100): Yellow Primary Cursor (Marker A) snaps to edge",
            "06: # Middle-Click at t = 523.06 ns (count = 13'h010F): White Delta Cursor (Marker B) snaps to edge",
            "07: # Top Ruler displays: Cursor = 494.211 ns | Marker = 523.056 ns | Delta = 28.845 ns (15 cycles)",
            "08: # Jump to Terminal Cycle 4111: Click 'Search' -> 'By Value' -> Signal: count -> Value: 13'h100F",
            "09: # Press 'z' 3 times around t = 7,905.45 ns to inspect final BestDist, motionX, motionY, completed=1",
            "TERM_MAC:  [student@MacBook ~ %] # Press Cmd+Shift+4 on MacBook to capture crisp PNG of nWave window!",
            "OUT_OK:    Full-screen waveform PNG captured with top ruler, scrollbar, and hex register transitions!",
        ],
        49: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ vcs -full64 -sverilog -debug_access+all rtl/8bit/top.v tb/8bit/top_tb.v -o simv_8b",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ./simv_8b -l logs/simv_8bit_row1.log",
            "# --- Waveform Verification: V9_fig7_orig8bit_row1_nWave.png (count = 0x00F9..0x0110) ---",
            "01: # At count = 12'h00FF (t = 492.29 ns): PE0 finishes accumulating 256th pixel of candidate (0,0)",
            "02: # Because true SAD D(0,0) > 255, 8-bit PE0 saturates: PE0.Accumulate[7:0] clamps at 8'hFF (255)!",
            "03: # At count = 12'h0100 (t = 494.21 ns): CompStart asserts (0 -> 1) and PEready[0] asserts (16'h0001)",
            "04: # Comparator tests strict inequality: if (newDist < BestDist) -> (8'hFF < 8'hFF) == FALSE (0)!",
            "05: # Consequently, u1.u2.newBest remains 1'b0 across all 16 PEs in Row 1 (count = 0x0100..0x010F)!",
            "OUT_OK:    Verified 8-bit saturation & strict '<' tie behavior in Verdi nWave at 520 MHz!",
        ],
        50: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'BestDist|motionX|motionY' logs/simv_8bit_row1.log",
            "# --- Waveform Verification: V9_fig8_orig8bit_complete_nWave.png (count = 0x100F, t = 7,905.45 ns) ---",
            "01: # In 8-bit random+1 offset testbench (top_tb.v), candidate (-5,+7) has true SAD = 256 (9'h100).",
            "02: # In 8-bit PE, 256 triggers Carry == 1 -> clamps to 8'hFF, tying earlier saturated blocks!",
            "03: # In 8-bit max-contrast testbench (all pixels |0x00 - 0xFF| = 255), all 256 blocks saturate to 8'hFF.",
            "04: # At count = 12'h100F (t = 7,905.45 ns): BestDist stays 8'hFF and motionX/Y never update (or tie)!",
            "05: # Furthermore, without the 13-bit counter fix, 12-bit count[11:0] wraps to 12'h000 at cycle 4096!",
            "OUT_OK:    Proved why 16-bit non-saturating datapath + 13-bit terminal hold is architecturally required!",
        ],
        51: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ vcs -full64 -sverilog -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_16b_0000",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ./simv_16b_0000 -l logs/simv_16b_0000.log",
            "# --- Waveform Verification: V9_fig10_16bit_perfect_match_0000_nWave.png ---",
            "01: # At count < 256: CompStart == 0 initializes BestDist[15:0] <= 16'hFFFF (65,535).",
            "02: # At count = 13'h0100 (PE0 ready): D(0,0) = 16'h0909 < 16'hFFFF -> newBest=1, BestDist <= 16'h0909.",
            "03: # At count = 13'h0101 (PE1 ready): D(1,0) = 16'h07C7 < 16'h0909 -> newBest=1, BestDist <= 16'h07C7.",
            "04: # At count = 13'h010F (PE15 ready): Exact match D(15,0) = 16'h0000 < BestDist -> newBest=1!",
            "05: # Comparator latches BestDist <= 16'h0000, motionX <= 8'h07 (+7), motionY <= 8'hF8 (-8)!",
            "OUT_OK:    BestDist = 16'h0000 verified in both VCS log and Verdi nWave (answers teammate Q3)!",
        ],
        52: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ vcs -full64 -sverilog -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_16bit.v -o simv_16b_ff00",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ./simv_16b_ff00 -l logs/simv_16b_ff00.log",
            "# --- Waveform Verification: V9_fig9_16bit_saturation_row1_nWave.png ---",
            "01: # Stimulus: All reference pixels R = 8'h00, all search pixels S = 8'hFF -> |R - S| = 255 per cycle.",
            "02: # Across 256 pixels: PE0.Accumulate[15:0] counts 0x00FF, 0x01FE, 0x02FD ... up to 16'hFF00 (65,280).",
            "03: # At count = 13'h0100 (t = 494.21 ns): PEready[0] = 1, newDist = 16'hFF00, BestDist = 16'hFFFF.",
            "04: # Because 16'hFF00 (65,280) < 16'hFFFF (65,535) is TRUE, newBest = 1 asserts on the first block!",
            "05: # Comparator latches BestDist <= 16'hFF00, motionX <= 8'hF8 (-8), motionY <= 8'hF8 (-8)!",
            "OUT_OK:    BestDist = 16'hFF00 verified for max-distortion stress test (answers teammate Q1 & Q2)!",
        ],
        53: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ cp ~/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/common/sdc/top.sdc ./common/sdc/top.sdc",
            "# --- Complete Line-by-Line Commented 520 MHz SDC File (constraints/top_520mhz.sdc) ---",
            "01: # Course Project Specification: Clock = 520 MHz (1.923 ns), I/O Delay = 0.5 ns, Uncertainty = 0.2 ns",
            "02: create_clock -name clock -period 1.923 [get_ports clock]   ;# 1000 / 1.923 = 520.02 MHz",
            "03: set_clock_uncertainty 0.2 [get_clocks clock]               ;# 200 ps jitter + skew margin",
            "04: # Constrain all 25 data/control input ports (exclude clock port itself!):",
            "05: set_input_delay 0.5 -clock clock [get_ports {start R* S1* S2*}]",
            "06: # Constrain all 60 output ports (BestDist[15:0], motionX[7:0], motionY[7:0], AddressR/S1/S2):",
            "07: set_output_delay 0.5 -clock clock [all_outputs]",
            "08: # Note: Reference (ROM_R) and Search (ROM_S) memories are EXCLUDED from top.v synthesis!",
            "09: # Available internal register-to-register setup budget = 1.923 - 0.200 = 1.723 ns",
            "10: # Available I/O path budget = 1.923 - 0.500 - 0.200 = 1.223 ns",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ cat common/sdc/top.sdc",
            "OUT_OK:    SDC verified: period=1.923, uncertainty=0.2, input_delay=0.5, output_delay=0.5",
        ],
        54: [
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp -r ~/ENGR852_Project/16_v3b_final_asic_fc/{setup,common,scripts} ~/me_asic_new_v1/",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp rtl/16bit/top.v ~/me_asic_new_v1/common/rtl/verilog/top.v",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp constraints/top_520mhz.sdc ~/me_asic_new_v1/common/sdc/top.sdc",
            "# --- Inspecting Pre-Given Course Setup Files (setup/fc_common_setup.tcl & setup/mcmm_setup.tcl) ---",
            "01: set DESIGN_NAME       \"top\"                              ;# Must match module top in top.v",
            "02: set DESIGN_LIBRARY    \"top.dlib\"                         ;# NDM container in ./results/top.dlib",
            "03: set VERILOG_PATH      \"./common/rtl/verilog\"             ;# Reads ./common/rtl/verilog/top.v",
            "04: set SDC_FILE          \"./common/sdc/top.sdc\"             ;# Reads 520 MHz (1.923 ns) constraints",
            "05: set DB_FF             \"./common/liberty/saed14rvt_ff0p88v125c.db\" ;# FAST corner (0.88V, 125C)",
            "06: set DB_TT             \"./common/liberty/saed14rvt_tt0p8v25c.db\"   ;# TYPICAL corner (0.80V, 25C)",
            "07: set DB_SS             \"./common/liberty/saed14rvt_ss0p72vm40c.db\" ;# SLOW corner (0.72V, -40C)",
            "08: set REFERENCE_LIBRARY \"./common/ndm/saed14rvt_frame_timing.ndm\"   ;# 14nm FinFET RVT NDM cells",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ls -la common/liberty/ common/ndm/",
            "OUT_OK:    All 3 Liberty .db corners (FF, TT, SS) and SAED14nm NDM reference library verified!",
        ],
        55: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/initial_syn.tcl' | tee logs/01_initial_syn.log",
            "# --- Actual Pre-Given Script 1: scripts/initial_syn.tcl (Lines 1..55) ---",
            *read_tcl_with_comments("initial_syn.tcl", 0, 22),
            "OUT_OK:    Created ./results/top.dlib (block: top/inital_syn) and ./results/top_initial_syn.v!",
        ],
        56: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/compile_flow.tcl' | tee logs/02_compile.log",
            "# --- Actual Pre-Given Script 2: scripts/compile_flow.tcl (MCMM + compile_fusion) ---",
            *read_tcl_with_comments("compile_flow.tcl", 0, 22),
            "OUT_OK:    Completed compile_fusion (initial_map -> logic_opto -> final_opto) with 0 memory macros!",
        ],
        57: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ sed -i 's/-core_utilization 0.6/-core_utilization 0.35/g' scripts/manual_floorplan_creation.tcl",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/manual_floorplan_creation.tcl' | tee logs/03_floorplan.log",
            "# --- Actual Pre-Given Script 3: scripts/manual_floorplan_creation.tcl ---",
            *read_tcl_with_comments("manual_floorplan_creation.tcl", 0, 22),
            "OUT_OK:    Floorplan initialized (2:1 aspect ratio, M3/M4 I/O pins, M5 clock pin, tap/boundary cells)!",
        ],
        58: [
            "# --- Actual Pre-Given Script 4: scripts/create_pg_network.tcl (Called by manual_floorplan_creation.tcl) ---",
            *read_tcl_with_comments("create_pg_network.tcl", 0, 22),
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'check_pg_connectivity|check_pg_drc|Error' logs/03_floorplan.log",
            "OUT_OK:    M1 stdcell rails + M5/M6/M7 PG mesh + M6/M7 core rings compiled with 0 PG DRC errors!",
        ],
        59: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/place_opt.tcl' | tee logs/04_place_opt.log",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/clock_opt.tcl' | tee logs/05_clock_opt.log",
            "# --- Actual Pre-Given Script 5 & 6: scripts/clock_opt.tcl (2x Width/Spacing NDR + VSS Shielding) ---",
            *read_tcl_with_comments("clock_opt.tcl", 8, 22),
            "OUT_OK:    Clock tree synthesized across 449 DFFs with target_skew 0.1 ns and M2..M5 VSS shielding!",
        ],
        60: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/route_opt.tcl' | tee logs/06_route_opt.log",
            "# --- Actual Pre-Given Script 7: scripts/route_opt.tcl (Global, Track, Detail Route + Redundant Vias) ---",
            *read_tcl_with_comments("route_opt.tcl", 8, 22),
            "OUT_OK:    Detail routing + route_opt + add_redundant_vias + check_routes + check_lvs completed cleanly!",
        ],
        61: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f ./scripts/signoff.tcl' | tee logs/07_signoff.log",
            "# --- Actual Pre-Given Script 8 & 9: scripts/signoff.tcl + scripts/write_data.tcl ---",
            *read_tcl_with_comments("signoff.tcl", 6, 15),
            *read_tcl_with_comments("write_data.tcl", 0, 10),
            "OUT_OK:    Exported results/top.v, results/top.sdc, results/top.spef.{min,nom,max}, and results/top.gds!",
        ],
        62: [
            "TERM_XQ:   [student@MacBook ~ %] ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -gui'",
            "# --- Inside Fusion Compiler GUI Command Console (Inspecting Routed 14nm Layout): ---",
            "01: open_lib ./results/top.dlib",
            "02: open_block top/signoff_v5",
            "03: # In left 'View Settings' panel -> Check Metal Layers M1, M2, M3, M4, M5, M6, M7",
            "04: # Press 'f' to Fit Full Die Area (125.07 um x 62.80 um) in the layout canvas",
            "05: gui_write_window_image -format png -file ./results/v9_signoff_clean_layout.png",
            "OUT_OK:    Saved high-resolution 14nm routed chip layout image ./results/v9_signoff_clean_layout.png!",
        ],
        63: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ cat signoff_drc_run/top.LAYOUT_ERRORS",
            "# --- Verifying Standalone Synopsys IC Validator (ICV) DRC & LVS Sign-Off Reports ---",
            "01: # In scripts/signoff.tcl, Fusion Compiler invokes ICV with SAED14nm 1p9m DRC & Metal Fill runsets:",
            "02: set_app_options -name signoff.check_drc.runset -value ${DRC_RUNSET_FILE}",
            "03: signoff_check_drc    ;# Runs ICV across all 242 SAED14nm FinFET design rules",
            "04: signoff_fix_drc      ;# Automatically repairs any spacing/width/via enclosure issues",
            "05: signoff_check_drc    ;# Re-verifies 0 remaining DRC violations",
            "06: # Run preflight placement audit to verify 0 unplaced cells before/after GDS export:",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'LAYOUT ERRORS RESULTS|Total Error' signoff_drc_run/top.LAYOUT_ERRORS",
            "OUT_OK:    LAYOUT ERRORS RESULTS : CLEAN (0 / 242 rule violations; UNPLACED_FLAT_CELL_COUNT = 0)!",
        ],
        64: [
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; pt_shell -f ./scripts/v5_prime_time_extracted_corners.tcl' | tee logs/08_primetime.log",
            "# --- Actual 3-Corner PrimeTime Script: scripts/v5_prime_time_extracted_corners.tcl ---",
            *read_tcl_with_comments("v5_prime_time_extracted_corners.tcl", 0, 21),
            "OUT_OK:    FAST: Setup +0.71ns / Hold 0.00ns | TYP: +0.54ns / +0.04ns | SLOW: +0.22ns / +0.14ns (0 violations)!",
        ],
    }
    return mapping.get(pnum, [])


def get_page_specific_part7_lines(pnum):
    """Returns rich, page-specific command/script blocks for Pages 89..100."""
    mapping = {
        89: [
            "TERM_MAC:  [student@MacBook ~ %] cd ~/Developer/engr852-14nm-motion-estimator",
            "TERM_MAC:  [student@MacBook ~ %] source .venv/bin/activate",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/package_v9_submission.py",
            "# --- Inside scripts/package_v9_submission.py (Automated Deliverable Bundler) ---",
            "01: # Collects all required rubric folders into a single clean submission archive:",
            "02: #   01_RTL_and_Testbenches/ -> rtl/8bit/top.v, rtl/16bit/top.v, top_tb.v, top_tb_direct.v, ref.txt, search.txt",
            "03: #   02_Simulation_Logs_and_Waveforms/ -> 7 VCS logs + 4 zoomed Verdi nWave PNGs (0000, 0100, FF00, 8-bit)",
            "04: #   03_Synthesis_and_Constraints/ -> top_520mhz.sdc, top.v (gate-level netlist), area/power/timing .rpt",
            "05: #   04_Physical_Design_GDS_DRC_SPEF/ -> v9_signoff_clean_layout.png, top.LAYOUT_ERRORS, 3-corner .spef",
            "06: #   05_PrimeTime_3Corner_PostLayout_STA/ -> FAST, TYPICAL, SLOW setup & hold timing reports",
            "07: #   06_Engineering_Report_and_Slides/ -> Engineering Report PDF + 19-Slide Presentation (.pptx & .pdf)",
            "TERM_MAC:  [student@MacBook ~ %] unzip -l deliverables/ENGR852_Motion_Estimator_Final_Master_Package_V9.zip | head -n 20",
            "OUT_OK:    Created clean, rubric-complete submission .zip with 0 temporary .daidir or lock files!",
        ],
        90: [
            "# --- Customizing Project Naming, Slide Palette, & Report Headers on Your New Laptop ---",
            "TERM_MAC:  [student@MacBook ~ %] export MY_NEW_REPO=\"engr852-520mhz-motion-estimator-asic\"",
            "TERM_MAC:  [student@MacBook ~ %] mkdir -p ~/Developer/$MY_NEW_REPO && cd ~/Developer/$MY_NEW_REPO",
            "01: # Variation 1 (Server Folder): Use ~/me_asic_new_v1 on 926784856@mahmoodi.rcc.at.sfsu.edu",
            "02: # Variation 2 (Testbench Shift): Edit TARGET_DX / TARGET_DY in tb/top_tb.v (e.g. (+3,-4) -> X=03, Y=FC)",
            "03: # Variation 3 (Slide Theme): In scripts/build_v9_final_slides.py, change RGBColor(15, 23, 42) to:",
            "04: #     NAVY_THEME  = RGBColor(12, 35, 64)   # Classic Engineering Navy",
            "05: #     SFSU_PURPLE = RGBColor(35, 17, 97)   # SFSU Gator Purple & Gold",
            "06: #     SLATE_TEAL  = RGBColor(15, 118, 110) # Modern Silicon Teal",
            "07: # Variation 4 (Keep Identical): NEVER rename 'module top' or its 11 ports (clock, start, BestDist, etc.)!",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/build_v9_final_slides.py && python3 scripts/build_v9_final_engineering_report.py",
            "OUT_OK:    Regenerated customized presentation deck (.pptx) and engineering report (.pdf) in 3 seconds!",
        ],
        91: [
            "# --- Git Dataflow Commands: Working Tree -> Staging Index -> Local Repo -> GitHub Remote ---",
            "TERM_MAC:  [student@MacBook ~ %] cd ~/Developer/engr852-14nm-motion-estimator",
            "TERM_MAC:  [student@MacBook ~ %] git init -b main",
            "OUT_OK:    Initialized empty Git repository in .../engr852-14nm-motion-estimator/.git/",
            "TERM_MAC:  [student@MacBook ~ %] git config user.name \"Your Full Name\"",
            "TERM_MAC:  [student@MacBook ~ %] git config user.email \"your_email@sfsu.edu\"",
            "TERM_MAC:  [student@MacBook ~ %] git status -s",
            "01: # '??' means untracked file in Working Tree; 'A ' means staged in Index; 'M ' means modified",
            "02: # Always inspect 'git status' before committing to ensure no >100 MB .fsdb or .ndm files are staged!",
            "TERM_MAC:  [student@MacBook ~ %] git add rtl/ tb/ constraints/ scripts/ verification/ docs/ deliverables/ README.md",
            "TERM_MAC:  [student@MacBook ~ %] git diff --cached --stat",
            "OUT_OK:    All Verilog RTL, testbenches, SDC, TCL scripts, reports, and slides staged cleanly!",
        ],
        92: [
            "# --- Creating a Brand-New GitHub Repository via Browser or GitHub CLI (gh) ---",
            "01: # Option A (Web Browser): Open https://github.com/new on your MacBook Air",
            "02: #   -> Repository name: engr852-520mhz-motion-estimator-asic (or your custom project name)",
            "03: #   -> Description: 520 MHz 16-PE Systolic Motion Estimator ASIC in Synopsys SAED14nm FinFET",
            "04: #   -> Visibility: Public (or Private) -> Leave 'Add a README' UNCHECKED -> Click 'Create repository'",
            "05: # Option B (Command Line via GitHub CLI 'gh' on your MacBook Terminal):",
            "TERM_MAC:  [student@MacBook ~ %] brew install gh && gh auth login",
            "TERM_MAC:  [student@MacBook ~ %] gh repo create engr852-520mhz-motion-estimator-asic --public --source=. --remote=origin",
            "TERM_MAC:  [student@MacBook ~ %] git remote -v",
            "OUT_OK:    origin  git@github.com:<YOUR_USERNAME>/engr852-520mhz-motion-estimator-asic.git (fetch/push)",
        ],
        93: [
            "# --- Configuring GitHub SSH Keys & Critical .gitignore Rules for Synopsys ASIC Projects ---",
            "TERM_MAC:  [student@MacBook ~ %] ssh-keygen -t ed25519 -C \"github-macbook\" -f ~/.ssh/id_ed25519_github -N \"\"",
            "TERM_MAC:  [student@MacBook ~ %] pbcopy < ~/.ssh/id_ed25519_github.pub  # Copies public key to clipboard",
            "01: # Paste key at https://github.com/settings/keys -> Click 'Add SSH key', then test connection:",
            "TERM_MAC:  [student@MacBook ~ %] ssh -T git@github.com",
            "OUT_OK:    Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.",
            "TERM_MAC:  [student@MacBook ~ %] cat << 'EOF' > .gitignore",
            "02: *.fsdb",
            "03: *.vpd",
            "04: *.ndm",
            "05: *.dlib/",
            "06: simv*",
            "07: csrc/",
            "08: *.daidir/",
            "09: verdiLog/",
            "10: .venv/",
            "11: EOF",
            "OUT_OK:    .gitignore created — prevents Synopsys binary databases from exceeding GitHub's 100 MB limit!",
        ],
        94: [
            "# --- Generating a Publication-Grade GitHub README.md With Full Verification Tables ---",
            "TERM_MAC:  [student@MacBook ~ %] head -n 25 README.md",
            "01: # # 520 MHz 16-PE Systolic Motion Estimator ASIC (Synopsys SAED14nm FinFET)",
            "02: # - **Architecture**: 16-PE 1D Systolic Array + 13-Bit Explicit FSM + 16-Bit Non-Saturating SAD",
            "03: # - **Clock Target**: 520.02 MHz (1.923 ns period, 0.5 ns I/O delay, 0.2 ns clock uncertainty)",
            "04: # - **Physical Layout**: 125.07 um x 62.80 um die, 8,230 cells (449 FFs), 0 SRAM/ROM macros",
            "05: # - **DRC / LVS Sign-Off**: 0 / 242 ICV DRC violations (CLEAN), 0 LVS mismatches",
            "06: # - **Post-Layout PrimeTime STA**:",
            "07: #   - FAST (minTLU_125): Setup WNS = +0.71 ns | Hold WNS = 0.00 ns (0 violations)",
            "08: #   - TYPICAL (nomTLU_25): Setup WNS = +0.54 ns | Hold WNS = +0.04 ns (0 violations)",
            "09: #   - SLOW (maxTLU_-40): Setup WNS = +0.22 ns | Hold WNS = +0.14 ns (0 violations)",
            "OUT_OK:    README.md documents architecture, 3 testbench regimes (0000, 0100, FF00), and full sign-off metrics!",
        ],
        95: [
            "# --- Executing the Final Commit, Annotated Release Tag, and Push to GitHub ---",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/v6_stage_gate.py --scope full",
            "OUT_OK:    FINAL_GATE_RESULT: PASS (All 11/11 RTL, Simulation, GDS, DRC, LVS, and 3-Corner STA Gates Verified)",
            "TERM_MAC:  [student@MacBook ~ %] git add -A",
            "TERM_MAC:  [student@MacBook ~ %] git status -s",
            "TERM_MAC:  [student@MacBook ~ %] git commit -m \"Complete 520 MHz SAED14nm Motion Estimator ASIC RTL, P&R & Sign-Off\"",
            "TERM_MAC:  [student@MacBook ~ %] git tag -a v1.0-signoff -m \"Verified 520 MHz SAED14nm Sign-Off Release\"",
            "TERM_MAC:  [student@MacBook ~ %] git push -u origin main --tags",
            "OUT_OK:    Branch 'main' set up to track 'origin/main'; tag 'v1.0-signoff' pushed to GitHub!",
        ],
        96: [
            "# --- Live Diagnostic & Self-Healing Commands for VPN, XQuartz, and SSH Issues ---",
            "TERM_MAC:  [student@MacBook ~ %] # Symptom 1: 'ssh: connect to host mahmoodi.rcc.at.sfsu.edu port 22: Operation timed out'",
            "TERM_MAC:  [student@MacBook ~ %] scutil --dns | grep sfsu.edu && nc -zv mahmoodi.rcc.at.sfsu.edu 22",
            "01: # Fix 1: Click GlobalProtect globe icon in macOS menu bar -> Connect to vpn.sfsu.edu -> Approve Duo push.",
            "TERM_XQ:   [student@MacBook ~ %] # Symptom 2: 'Error: Can't open display:' when running verdi or fc_shell -gui",
            "TERM_XQ:   [student@MacBook ~ %] open -a XQuartz && /opt/X11/bin/xdpyinfo -display :0 | head -n 5",
            "02: # Fix 2: Open XQuartz -> Settings -> Security -> Enable 'Allow connections from network clients' -> Log out/in of macOS!",
            "TERM_SFSU: [926784856@mahmoodi ~]$ # Symptom 3: SSH still asks for password after adding Ed25519 key",
            "TERM_SFSU: [926784856@mahmoodi ~]$ chmod go-w ~ && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys",
            "OUT_OK:    All VPN, XQuartz DISPLAY socket, and SSH key permission issues resolved!",
        ],
        97: [
            "# --- Live Diagnostic & Self-Healing Commands for Synopsys VCS & Verdi Waveform Issues ---",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ # Symptom 1: 'vcs: command not found' or 'verdi: command not found'",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; which vcs verdi'",
            "01: # Symptom 2: Clock frequency in waveform is 500 MHz (2.0 ns) instead of 520 MHz (1.923 ns):",
            "02: # Fix 2: Check top of testbench! Must be `timescale 1ns/10ps (or 1ns/100fs), NOT `timescale 1ns/1ns!",
            "03: # Symptom 3: Verdi says 'Cannot open FSDB file waves.fsdb':",
            "04: # Fix 3: Ensure testbench initial block calls $fsdbDumpfile(\"waves.fsdb\"); $fsdbDumpvars(0, top_tb);",
            "05: #        and compile with vcs -full64 -sverilog -debug_access+all -kdb!",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ls -lh *.fsdb",
            "OUT_OK:    waves.fsdb generated cleanly with full hierarchical signal visibility!",
        ],
        98: [
            "# --- Live Diagnostic & Self-Healing Commands for Fusion Compiler, ICV DRC, & PrimeTime STA ---",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ # Symptom 1: 'Error: Required design library results/top.dlib is locked'",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ rm -f results/top.dlib/**/lock* && ps -u $USER | grep fc_shell",
            "01: # Symptom 2: Pre-given sta_post_layout.tcl fails with 'Cannot find file i2c_master_top.v':",
            "02: # Fix 2: The course template sta_post_layout.tcl had 'i2c_master_top' from Lab 4! Replace with 'top':",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ sed -i 's/i2c_master_top/top/g' scripts/sta_post_layout.tcl",
            "03: # Symptom 3: High routing congestion or DRC errors during route_opt:",
            "04: # Fix 3: Lower floorplan utilization from 0.60 to 0.35..0.52 in scripts/manual_floorplan_creation.tcl!",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; fc_shell -no_log -f scripts/v6_gds_preflight.tcl'",
            "OUT_OK:    UNPLACED_FLAT_CELL_COUNT=0 | PLACEMENT_PREFLIGHT_PASSED!",
        ],
        99: [
            "# --- Master Start-to-Finish Command Cheat Sheet (New MacBook + XQuartz + mahmoodi + GitHub) ---",
            "TERM_XQ:   [student@MacBook ~ %] open -a XQuartz && ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu",
            "TERM_SFSU: [926784856@mahmoodi ~]$ mkdir -p ~/me_asic_new_v1 && cd ~/me_asic_new_v1",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ cp -r ~/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/{setup,common,scripts} .",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ source ./scripts/synopsys_setup.tcl",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ vcs -full64 -sverilog -debug_access+all common/rtl/verilog/top.v tb/top_tb_direct.v -o simv && ./simv",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ foreach s (initial_syn compile_flow manual_floorplan_creation place_opt clock_opt route_opt signoff)",
            "TERM_SFSU:   fc_shell -no_log -f ./scripts/${s}.tcl | tee logs/${s}.log",
            "TERM_SFSU: end",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ pt_shell -f ./scripts/v5_prime_time_extracted_corners.tcl | tee logs/pt_3corner.log",
            "OUT_OK:    Complete RTL-to-GDSII + 3-Corner PrimeTime Sign-Off executed from scratch in ~/me_asic_new_v1!",
        ],
        100: [
            "# --- Final 11-Gate Self-Checking Verification Harness Execution & Rubric Sign-Off ---",
            "TERM_MAC:  [student@MacBook ~ %] cd ~/Developer/engr852-14nm-motion-estimator && source .venv/bin/activate",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/v6_stage_gate.py --scope full",
            "OUT_OK:    [PASS] G1: 8-Bit & 16-Bit RTL Synthesizable (0 SRAM/ROM Macros Inside top.v)",
            "OUT_OK:    [PASS] G2: 520 MHz (1.923 ns) VCS Regression (7/7 Self-Checking Testbenches PASS)",
            "OUT_OK:    [PASS] G3: Verdi nWave Waveforms Captured (0000 Exact, 0100 +1 Offset, FF00 Max Contrast)",
            "OUT_OK:    [PASS] G4: Synopsys Fusion Compiler 14nm Routed Layout (125.07 x 62.80 um, 8,230 Cells)",
            "OUT_OK:    [PASS] G5: Merged GDSII Export Verified (results/top.gds, 0 Unplaced Cells / 0 GDS-110)",
            "OUT_OK:    [PASS] G6: Standalone ICV DRC Clean (0 / 242 Violations) & LVS Clean (0 Errors)",
            "OUT_OK:    [PASS] G7: 3-Corner PrimeTime Post-Layout STA (Setup & Hold >= 0.00 ns Across FF/TT/SS)",
            "OUT_OK:    FINAL_GATE_RESULT: PASS — 100% Ready for 90-100% Course Project Grading & Live Demo!",
        ],
    }
    return mapping.get(pnum, [])


def enrich_code_lines_to_fill_box(pnum, raw_code_lines, max_lines=26):
    """Guarantees Section 4 has exactly `max_lines` rich, terminal-tagged lines so Box 4 is 100% full on every page."""
    if 45 <= pnum <= 64:
        custom = get_page_specific_eda_script_lines(pnum)
        if custom:
            raw_code_lines = custom
    elif 89 <= pnum <= 100:
        custom = get_page_specific_part7_lines(pnum)
        if custom:
            raw_code_lines = custom

    enriched = []
    for ln in raw_code_lines:
        s = str(ln)
        if any(s.startswith(p) for p in ("TERM_MAC:", "TERM_XQ:", "TERM_SFSU:", "OUT_OK:")):
            enriched.append(s)
        elif s.startswith("ssh ") or s.startswith("scp ") or s.startswith("rsync ") or s.startswith("xcode-select") or s.startswith("python3 ") or s.startswith("pip ") or s.startswith("git ") or s.startswith("scutil ") or s.startswith("nc "):
            enriched.append("TERM_MAC:  [student@MacBook ~ %] " + s)
        elif s.startswith("open -a XQuartz") or s.startswith("echo $DISPLAY") or s.startswith("xclock"):
            enriched.append("TERM_XQ:   [student@MacBook ~ %] " + s)
        elif s.startswith("source /apps") or s.startswith("which vcs") or s.startswith("vcs ") or s.startswith("fc_shell") or s.startswith("icv ") or s.startswith("pt_shell") or s.startswith("pwd") or s.startswith("ls -la /apps"):
            enriched.append("TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ " + s)
        else:
            enriched.append(s)

    # Rich 25-line bank per Part so every single page fills 100% of Box 4 with zero empty white space
    if pnum <= 12:
        extra = [
            "# --- Step-by-Step Server Workspace Clone & Pre-Given Course Script Setup on mahmoodi ---",
            "TERM_XQ:   [student@MacBook ~ %] open -a XQuartz && /opt/X11/bin/xdpyinfo -display :0 >/dev/null && echo LOCAL_XQUARTZ_OK",
            "OUT_OK:    LOCAL_XQUARTZ_OK (X11 socket /private/tmp/com.apple.launchd.../org.xquartz:0 is active)",
            "TERM_XQ:   [student@MacBook ~ %] ssh -Y -o ForwardX11=yes -o ForwardX11Trusted=yes 926784856@mahmoodi.rcc.at.sfsu.edu",
            "TERM_SFSU: [926784856@mahmoodi ~]$ mkdir -p ~/me_asic_new_v1/{rtl/8bit,rtl/16bit,tb/8bit,tb/16bit,scripts,logs,results,pt_reports}",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp -r ~/ENGR852_Project/16_v3b_final_asic_fc/{setup,common,scripts} ~/me_asic_new_v1/",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cp ~/ENGR852_Project/20_v5b_520MHz_14nm_cts_area_fix/scripts/v5_prime_time_extracted_corners.tcl ~/me_asic_new_v1/scripts/",
            "TERM_SFSU: [926784856@mahmoodi ~]$ cd ~/me_asic_new_v1 && tcsh",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ source ./scripts/synopsys_setup.tcl",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ echo \"DISPLAY=$DISPLAY\" && which vcs verdi fc_shell icv pt_shell",
            "OUT_OK:    DISPLAY=localhost:10.0 | /packages/synopsys/vcs/W-2024.09-1/bin/vcs (All 5 Synopsys tools ready!)",
            "# --- How scripts/synopsys_setup.tcl Configures Your Synopsys Environment on mahmoodi ---",
            "01: source /packages/synopsys/setup/synthesis.csh       ;# Design Compiler / synthesis libs",
            "02: source /packages/synopsys/setup/vcs_2024.csh        ;# Synopsys VCS W-2024.09-1 simulator",
            "03: source /packages/synopsys/setup/primetime_2022.csh  ;# Synopsys PrimeTime 3-corner sign-off STA",
            "04: source /packages/synopsys/setup/verdi_2024.csh      ;# Synopsys Verdi + nWave waveform GUI",
            "05: source /packages/synopsys/setup/fc.csh              ;# Synopsys Fusion Compiler 14nm P&R",
            "06: source /packages/synopsys/setup/ic_validator_2024.csh ;# Synopsys IC Validator DRC & LVS",
            "TERM_MAC:  [student@MacBook ~ %] rsync -avz 926784856@mahmoodi.rcc.at.sfsu.edu:~/me_asic_new_v1/scripts/ ./scripts/synopsys_tcl/",
            "OUT_OK:    Synced all pre-given course TCL scripts to local MacBook for inspection & Git tracking!",
        ]
    elif pnum <= 24:
        extra = [
            "// --- Interactive Hardware Verification of This Architectural Step on mahmoodi ---",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; vcs -full64 -sverilog -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_check && ./simv_check'",
            "OUT_OK:    Cycle 256 (0x0100): CompStart=1, PEready=0x0001 | Cycle 4111 (0x100F): completed=1, BestDist=16'h0000",
            "// --- Comparing 8-Bit Baseline (rtl/8bit/top.v) vs. 16-Bit Non-Saturating Upgrade (rtl/16bit/top.v) ---",
            "01: // In 8-bit PE:  {Carry, AccumulateIn} = Accumulate + difference; if (Carry == 1) AccumulateIn = 8'hFF;",
            "02: // In 16-bit PE: AccumulateIn = Accumulate + {8'd0, difference};  // Exact sum up to 256*255 = 65,280 (16'hFF00)",
            "03: // In 8-bit Control:  reg [11:0] count; // Wraps to 0 at cycle 4096 -> resets BestDist during Row 15!",
            "04: // In 16-bit Control: reg [12:0] count; reg completed; // Holds at count == 13'h100F (cycle 4111)!",
            "05: // In 8-bit Comparator:  if (CompStart == 0) BestDist <= 8'hFF;   // Ties when newDist == 8'hFF!",
            "06: // In 16-bit Comparator: if (CompStart == 0) BestDist <= 16'hFFFF; // 16'hFF00 < 16'hFFFF is always TRUE!",
            "// --- Course Project Syllabus Requirements Checklist (Items 1-5) ---",
            "07: // [x] Clock Period = 1.923 ns (520.02 MHz) | Input Delay = 0.5 ns | Output Delay = 0.5 ns | Uncertainty = 0.2 ns",
            "08: // [x] Exclude Reference (RMEM 256x8) and Search (SMEM 1024x8) memories from top.v synthesis!",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'BestDist|motionX|motionY|PASS' logs/*.log | tail -n 4",
            "OUT_OK:    All SAD D(i,j), motion vector (i-8, j-8), and cycle-4111 hold equations verified in VCS!",
        ]
    elif pnum <= 44:
        extra = [
            "// --- Running This Testbench & Inspecting Waveforms on 926784856@mahmoodi.rcc.at.sfsu.edu ---",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; vcs -full64 -sverilog -debug_access+all -kdb rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_direct && ./simv_direct -l logs/tb_direct.log'",
            "OUT_OK:    BestDist = 0000 (hex) | motionX = 07 (+7) or f8 (-8) | motionY = f8 (-8) or 07 (+7) [PASS]",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; vcs -full64 -sverilog -debug_access+all -kdb rtl/16bit/top.v tb/16bit/top_tb.v -o simv_tb && ./simv_tb -l logs/tb_offset1.log'",
            "OUT_OK:    Expected X = -5 (FB), Y = 7 (07) | Actual BestDist = 0100 (256), motionX = fb (-5), motionY = 07 (+7) [PASS]",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ tcsh -c 'source ./scripts/synopsys_setup.tcl; vcs -full64 -sverilog -debug_access+all -kdb rtl/16bit/top.v tb/16bit/top_tb_16bit.v -o simv_ff00 && ./simv_ff00 -l logs/tb_ff00.log'",
            "OUT_OK:    Max-Contrast Stress Test: BestDist = ff00 (65,280 < 65,535), motionX = f8 (-8), motionY = f8 (-8) [PASS]",
            "// --- Using the Pre-Given Starter Makefile (Course Project/Motion Estimator RTL and Testbench/Makefile) ---",
            "01: # You can also run using make by passing RTL and TB overrides on the command line:",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ make -f scripts/synopsys_tcl/Makefile.starter RTL=rtl/16bit/top.v TB=tb/16bit/top_tb.v test",
            "OUT_OK:    Makefile compiled and executed simv cleanly with +ntb_random_seed=1!",
        ]
    elif pnum <= 64:
        extra = [
            "# --- Post-Stage Automated Quality & Error Audit on 926784856@mahmoodi.rcc.at.sfsu.edu ---",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -En '^Error:|^Fatal:|PLACE-004|PLACE-006|CMD-081|GDS-110' logs/*.log || echo ZERO_TOOL_ERRORS",
            "OUT_OK:    ZERO_TOOL_ERRORS (No synthesis, placement, CTS, routing, DRC, or PrimeTime errors detected!)",
            "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ ls -lh results/top.v results/top.sdc results/top.gds results/*.spef",
            "OUT_OK:    Verified non-empty gate-level netlist (top.v), 3-corner SPEFs, and merged 14nm GDSII (top.gds)!",
            "# --- Key Physical Design & Sign-Off Metrics Summary (SAED14nm FinFET @ 520 MHz / 1.923 ns) ---",
            "01: # Die Dimensions:    125.07 um x 62.80 um = 7,854.40 um^2 (Core Area = 6,558.96 um^2, Util = 52.08%)",
            "02: # Leaf Cell Count:   8,230 standard cells (449 D flip-flops; 0 SRAM/ROM memory macros synthesized)",
            "03: # Total Cell Area:   3,416.18 um^2 (16-bit full-precision non-saturating datapath; 1,366.85 um^2 in 8-bit)",
            "04: # Total Power (TT):  0.890 mW at 520 MHz (0.889 mW dynamic switching + 0.00089 mW cell leakage)",
            "05: # ICV Sign-Off DRC:  0 / 242 rule violations (signoff_drc_run/top.LAYOUT_ERRORS -> CLEAN)",
            "06: # PrimeTime 3-Corner: FAST (+0.71/0.00 ns), TYPICAL (+0.54/+0.04 ns), SLOW (+0.22/+0.14 ns) -> 0 violations!",
        ]
    else:
        extra = [
            "# --- End-to-End Local Regeneration & 11-Gate Verification Commands on Your MacBook Air ---",
            "TERM_MAC:  [student@MacBook ~ %] source .venv/bin/activate",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/build_v9_final_slides.py",
            "OUT_OK:    Generated deliverables/ENGR852_V9_Complete_19_Slides.pptx & 3-slide contribution deck!",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/build_v9_final_engineering_report.py",
            "OUT_OK:    Generated deliverables/ENGR852_V9_Motion_Estimator_Final_Engineering_Report.pdf!",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/package_v9_submission.py",
            "OUT_OK:    Bundled complete rubric submission zip: ENGR852_Motion_Estimator_Final_Master_Package_V9.zip",
            "TERM_MAC:  [student@MacBook ~ %] python3 scripts/v6_stage_gate.py --scope full",
            "OUT_OK:    FINAL_GATE_RESULT: PASS (All 11/11 verification gates verified with zero missing artifacts!)",
            "TERM_MAC:  [student@MacBook ~ %] git status -s && git log -n 2 --oneline",
            "OUT_OK:    Working tree clean — ready for git push -u origin main to your GitHub repository!",
        ]

    for item in extra:
        if len(enriched) >= max_lines:
            break
        if item not in enriched:
            enriched.append(item)

    # Append additional unique diagnostic & rubric-verification commands if needed so Box 4 is 100% full with zero repetition
    unique_tail_bank = [
        "# --- Additional Live Diagnostic & Rubric Verification Commands for This Step ---",
        "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ sha256sum common/rtl/verilog/top.v common/sdc/top.sdc",
        "OUT_OK:    Verified exact SHA-256 checksums for synthesizable 16-bit top.v and 520 MHz top.sdc!",
        "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -i 'memory' reports/*.rpt || echo ZERO_SYNTHESIZED_MEMORIES",
        "OUT_OK:    ZERO_SYNTHESIZED_MEMORIES (Confirms RMEM & SMEM are excluded from synthesis per rubric!)",
        "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'slack \\(MET\\)|No constrained paths' pt_reports/*.rpt | head -n 3",
        "OUT_OK:    slack (MET) +0.71 ns (FAST) | slack (MET) +0.54 ns (TYPICAL) | slack (MET) +0.22 ns (SLOW)",
        "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ grep -E 'LAYOUT ERRORS RESULTS' signoff_drc_run/top.LAYOUT_ERRORS",
        "OUT_OK:    LAYOUT ERRORS RESULTS : CLEAN (0 / 242 SAED14nm FinFET DRC violations across M1..M9)",
        "TERM_SFSU: [926784856@mahmoodi me_asic_new_v1]$ df -h . && ps -u $USER",
        "OUT_OK:    Server disk quota healthy and zero hung background EDA processes on mahmoodi!",
        "TERM_MAC:  [student@MacBook ~ %] ls -lh deliverables/*.pdf deliverables/*.pptx deliverables/*.zip",
        "OUT_OK:    Verified Engineering Report PDF, 19-Slide Presentation PPTX, and Master Submission ZIP!",
    ]
    for u_item in unique_tail_bank:
        if len(enriched) >= max_lines:
            break
        if u_item not in enriched:
            enriched.append(u_item)

    return enriched[:max_lines]


def get_fallback_recovery_lines(pnum):
    """Returns Section 5: 8 concise lines (<= 95 chars each) of Live Checks & Plan A/B/C Fallbacks."""
    if pnum <= 12:
        return [
            "BLUE:[LIVE CHECK] In XQuartz xterm: echo $DISPLAY && ssh -Y 926784856@mahmoodi.rcc.at.sfsu.edu 'echo $DISPLAY'",
            "RED:[IF XYZ FAILS #1] 'ssh: Operation timed out' or 'Could not resolve hostname mahmoodi.rcc.at.sfsu.edu':",
            "  -> Option A: Click GlobalProtect menu bar icon -> Portal: vpn.sfsu.edu -> Connect -> Approve Duo Push.",
            "  -> Option B: Flush macOS DNS cache: dscacheutil -flushcache && sudo killall -HUP mDNSResponder.",
            "RED:[IF XYZ FAILS #2] Remote $DISPLAY is empty or Verdi/FC GUI prints 'Error: Can't open display':",
            "  -> Option A: XQuartz -> Settings -> Security -> Enable 'Allow connections from network clients' & relogin.",
            "  -> Option B: Run inside XQuartz xterm (Cmd+N): ssh -Y -o ForwardX11Trusted=yes 926784856@mahmoodi...",
            "GREEN:[PULL SERVER SCRIPTS] cp -r ~/ENGR852_Project/16_v3b_final_asic_fc/{setup,common,scripts} ~/me_asic_new_v1/",
        ]
    if pnum <= 24:
        return [
            "BLUE:[LIVE CHECK] Verify top.v ports & widths: grep -En 'module top|output|input|Accumulate|count' rtl/16bit/top.v",
            "RED:[IF XYZ FAILS #1] Synthesis includes SRAM/ROM macros or area exceeds 10,000 um^2:",
            "  -> Option A: Remove any RMEM/SMEM instantiation from top.v! Keep memories ONLY in tb/top_tb.v.",
            "  -> Option B: Verify top.v outputs AddressR[7:0], AddressS1[9:0], AddressS2[9:0] and inputs R, S1, S2.",
            "RED:[IF XYZ FAILS #2] BestDist wipes to FFFF at cycle 4096 or motionX/motionY remain 'xx':",
            "  -> Option A: Widen Control count to reg [12:0] count and latch completed <= 1'b1 at 13'h100F (4111).",
            "  -> Option B: In 16-bit PE, use AccumulateIn = Accumulate + {8'd0, difference} (no 8'hFF clamp!).",
            "GREEN:[PULL STARTER RTL] cp ~/ENGR852_Project/16_v3b_final_asic_fc/common/rtl/verilog/top.v ~/me_asic_new_v1/rtl/",
        ]
    if pnum <= 44:
        return [
            "BLUE:[LIVE CHECK] Run VCS & check outputs: ./simv -l logs/sim.log && grep -E 'BestDist|motion|PASS' logs/sim.log",
            "RED:[IF XYZ FAILS #1] Waveform clock period is 2.0 ns (500 MHz) instead of 1.923 ns (520 MHz):",
            "  -> Option A: Set line 1 of testbench to `timescale 1ns/10ps (or 1ns/100fs), NOT `timescale 1ns/1ns!",
            "  -> Option B: Use 'always #0.9615 clock = ~clock;' so 2 * 0.9615 ns = 1.9230 ns (520.02 MHz).",
            "RED:[IF XYZ FAILS #2] VCS fails with 'Unresolved module RMEM/SMEM' or '$readmemh cannot open ref.txt':",
            "  -> Option A: Copy ref.txt and search.txt into your run directory: cp tb/ref.txt tb/search.txt .",
            "  -> Option B: Run starter Makefile: make -f scripts/synopsys_tcl/Makefile.starter RTL=... TB=... test",
            "GREEN:[3-REGIME CHECK] top_tb_direct.v -> 16'h0000 | top_tb.v -> 16'h0100 (-5,+7) | top_tb_16bit.v -> 16'hFF00!",
        ]
    if pnum <= 64:
        return [
            "BLUE:[LIVE CHECK] Scan EDA logs for hidden errors: grep -En '^Error:|^Fatal:|PLACE-004|GDS-110' logs/*.log",
            "RED:[IF XYZ FAILS #1] 'fc_shell: command not found' or 'pt_shell: command not found' on mahmoodi:",
            "  -> Option A: Run inside tcsh: tcsh -c 'source ./scripts/synopsys_setup.tcl; which fc_shell icv pt_shell'.",
            "  -> Option B: In interactive tcsh, run: source ./scripts/synopsys_setup.tcl before invoking EDA tools.",
            "RED:[IF XYZ FAILS #2] Pre-given sta_post_layout.tcl fails with 'Cannot find i2c_master_top' or link error:",
            "  -> Option A: Fix tutorial name in script: sed -i 's/i2c_master_top/top/g' scripts/sta_post_layout.tcl.",
            "  -> Option B: Prepend '*' to link_path: set link_path [list * ./common/liberty/saed14rvt_ff0p88v125c.db ...].",
            "GREEN:[RESUME SCRIPT] If SSH drops during P&R, resume cleanly: bash scripts/resume_v3_physical_flow.sh cts",
        ]
    return [
        "BLUE:[LIVE CHECK] Run automated 11-gate verification harness: python3 scripts/v6_stage_gate.py --scope full",
        "RED:[IF XYZ FAILS #1] Python fails with 'ModuleNotFoundError: No module named pptx / reportlab / PIL':",
        "  -> Option A: Activate virtualenv first: source .venv/bin/activate && pip install python-pptx reportlab pillow.",
        "  -> Option B: Invoke venv Python directly: ./.venv/bin/python3 scripts/build_v9_final_slides.py.",
        "RED:[IF XYZ FAILS #2] 'git push' rejected due to >100 MB file limit or remote repository mismatch:",
        "  -> Option A: Add *.fsdb *.gds *.dlib/ to .gitignore and run: git rm --cached *.gds *.fsdb.",
        "  -> Option B: Set your new repo URL: git remote set-url origin https://github.com/<USER>/<NEW_REPO>.git.",
        "GREEN:[RUBRIC COMPLETE] All 5 deliverables (RTL, 520MHz Synthesis, TBs, 14nm Layout/DRC/SPEF, 3-Corner PT) PASS!",
    ]


def draw_terminal_code_box(c, x, y_top, width, height, title, lines, font_size=6.65):
    """Draws Section 4 with standout color-coded Terminal Pill Badges ([MACBOOK], [XQUARTZ], [926784856@mahmoodi], [OUTPUT])."""
    y_bot = y_top - height
    c.setFillColor(BOX_CODE_BG)
    c.setStrokeColor(INK_PURPLE)
    c.setLineWidth(1.1)
    c.roundRect(x, y_bot, width, height, 4, fill=1, stroke=1)

    # Header bar
    c.setFillColor(INK_PURPLE)
    c.roundRect(x, y_top - 15, width, 15, 4, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 8.0)
    c.drawString(x + 7, y_top - 11, title)

    # Legend pills on right side of header bar
    legend = [
        ("MACBOOK", BADGE_MAC_BG, width - 235),
        ("XQUARTZ", BADGE_XQ_BG, width - 178),
        ("926784856@mahmoodi", BADGE_SFSU_BG, width - 122),
        ("OUTPUT", BADGE_OUT_BG, width - 42),
    ]
    for lbl, bcol, lx in legend:
        pw = len(lbl) * 3.8 + 6
        c.setFillColor(bcol)
        c.roundRect(x + lx, y_top - 13.5, pw, 11, 2, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 5.8)
        c.drawString(x + lx + 3, y_top - 10.2, lbl)

    leading = font_size + 2.2
    cy = y_top - 24.0
    for raw_line in lines:
        if cy < y_bot + 4:
            break
        line = clean_glyphs(raw_line)
        badge_lbl = None
        badge_bg = None
        row_bg = None
        text_col = INK_BLACK
        is_bold = False

        if line.startswith("TERM_MAC:"):
            badge_lbl = "MACBOOK"
            badge_bg = BADGE_MAC_BG
            row_bg = BADGE_MAC_ROW
            line = line[len("TERM_MAC:"):].strip()
            is_bold = True
        elif line.startswith("TERM_XQ:"):
            badge_lbl = "XQUARTZ"
            badge_bg = BADGE_XQ_BG
            row_bg = BADGE_XQ_ROW
            line = line[len("TERM_XQ:"):].strip()
            is_bold = True
        elif line.startswith("TERM_SFSU:"):
            badge_lbl = "926784856@mahmoodi"
            badge_bg = BADGE_SFSU_BG
            row_bg = BADGE_SFSU_ROW
            line = line[len("TERM_SFSU:"):].strip()
            is_bold = True
        elif line.startswith("OUT_OK:"):
            badge_lbl = "EXPECTED"
            badge_bg = BADGE_OUT_BG
            row_bg = BADGE_OUT_ROW
            line = line[len("OUT_OK:"):].strip()
            text_col = INK_GREEN
            is_bold = True

        if row_bg is not None:
            c.setFillColor(row_bg)
            c.rect(x + 3, cy - 2.0, width - 6, leading - 0.3, fill=1, stroke=0)

        text_x = x + 6
        if badge_lbl is not None:
            bw = len(badge_lbl) * 3.7 + 7
            c.setFillColor(badge_bg)
            c.roundRect(x + 5, cy - 1.5, bw, leading - 1.2, 2, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 5.7)
            c.drawString(x + 8, cy + 0.3, badge_lbl)
            text_x = x + 8 + bw

        if line.lstrip().startswith("#") or line.lstrip().startswith("//"):
            c.setFillColor(INK_BLUE if "---" in line else colors.HexColor("#334155"))
            c.setFont("Courier-Bold" if "---" in line else "Courier", font_size)
        else:
            c.setFillColor(text_col)
            c.setFont("Courier-Bold" if is_bold else "Courier", font_size)

        max_chars = int((x + width - text_x - 6) / (font_size * 0.60))
        c.drawString(text_x, cy, line[:max_chars])
        cy -= leading

    return y_bot


def render_100page_pdf_and_md():
    DELIV_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SPREADS_DIR.mkdir(parents=True, exist_ok=True)

    pages = generate_remaining_pages(build_100_page_curriculum())
    c = canvas.Canvas(str(OUT_PDF), pagesize=letter)
    w, h = letter
    avail_w = w - 80

    img_map = {
        5: SCREENSHOTS_DIR / "gp_vpn_connecting.png",
        6: SCREENSHOTS_DIR / "gp_vpn_connected_and_xquartz_xterm.png",
        7: SCREENSHOTS_DIR / "ssh_x11_multi_terminal_mahmoodi.png",
        49: SCREENSHOTS_DIR / "V9_fig7_orig8bit_row1_nWave.png",
        50: SCREENSHOTS_DIR / "V9_fig8_orig8bit_complete_nWave.png",
        51: SCREENSHOTS_DIR / "V9_fig10_16bit_perfect_match_0000_nWave.png",
        52: SCREENSHOTS_DIR / "V9_fig9_16bit_saturation_row1_nWave.png",
        62: SCREENSHOTS_DIR / "v9_signoff_clean_layout.png",
    }

    md_lines = [
        "# ENGR 852 Motion Estimator 14nm ASIC (520 MHz) — 100-Page Visual Engineering Notebook Manual",
        "",
        "Complete high-density baby-steps Standard Operating Procedure (SOP) with zero wasted page space, standout",
        "terminal execution badges (`[MACBOOK]`, `[XQUARTZ]`, `[926784856@mahmoodi]`, `[EXPECTED]`), pre-given server",
        "script pulling instructions, line-by-line commented RTL/TB/TCL/Python code, and Plan A/B/C fallback recovery.",
        "",
    ]

    for idx, (title, sub, stages, tbl_rows, trap_lines, code_lines) in enumerate(pages):
        pnum = idx + 1
        part_title = get_part_title(pnum)
        draw_notebook_page_chrome(c, pnum, part_title, title, sub)

        # 1. Section 1: Annotated Block Diagram / GUI Action Flow (Compact 78 pt height)
        y_cursor = h - 84
        y_cursor = draw_schematic_pipeline(
            c, 56, y_cursor, avail_w, 78, stages,
            "1. Visual Annotated Block Diagram & Step-by-Step Execution Pipeline (Blue=Input -> Green=Action -> Red=Verify)"
        )

        # 2. Section 2: Hardware-to-Verilog / Command Verification Table
        y_cursor -= 6
        num_cols = len(tbl_rows[0])
        if num_cols == 3:
            cwidths = [avail_w * 0.25, avail_w * 0.37, avail_w * 0.38]
        elif num_cols == 4:
            cwidths = [avail_w * 0.22, avail_w * 0.26, avail_w * 0.26, avail_w * 0.26]
        elif num_cols == 5:
            cwidths = [avail_w * 0.18, avail_w * 0.20, avail_w * 0.18, avail_w * 0.22, avail_w * 0.22]
        else:
            cwidths = [avail_w / num_cols] * num_cols
        y_cursor = draw_notebook_table(
            c, 56, y_cursor, cwidths, tbl_rows,
            title="2. Hardware-to-Verilog / Command-to-Action Verification Table"
        )

        # 3. Section 3: [!] TRAP / Key Insight Box (with side-by-side embedded screenshot on visual pages!)
        y_cursor -= 6
        if pnum in img_map and img_map[pnum].exists():
            img_p = img_map[pnum]
            sec3_h = 104
            left_w = avail_w * 0.46
            right_w = avail_w * 0.52
            right_x = 56 + avail_w - right_w
            draw_labeled_box(
                c, 56, y_cursor, left_w, sec3_h,
                "3. [!] Visual Guide & Critical Trap Note",
                trap_lines, INK_RED, BOX_RED_BG, mono=False, font_size=6.8
            )
            c.setFillColor(colors.white)
            c.setStrokeColor(INK_BLUE)
            c.setLineWidth(1.1)
            c.roundRect(right_x, y_cursor - sec3_h, right_w, sec3_h, 4, fill=1, stroke=1)
            c.drawImage(str(img_p), right_x + 4, y_cursor - sec3_h + 4, width=right_w - 8, height=sec3_h - 18, preserveAspectRatio=True)
            c.setFillColor(INK_BLUE)
            c.setFont("Helvetica-Bold", 7.2)
            c.drawString(right_x + 6, y_cursor - 11, f"Live Visual Evidence: {img_p.name}")
            y_cursor -= sec3_h
        else:
            box_col = INK_RED if trap_lines[0].startswith("RED:") else (INK_GREEN if trap_lines[0].startswith("GREEN:") else INK_BLUE)
            box_bg = BOX_RED_BG if trap_lines[0].startswith("RED:") else (BOX_GREEN_BG if trap_lines[0].startswith("GREEN:") else BOX_BLUE_BG)
            y_cursor = draw_labeled_box(
                c, 56, y_cursor, avail_w, 56,
                "3. [!] Critical Engineering Note / Beginner Trap & How to Avoid It",
                trap_lines, box_col, box_bg, mono=False, font_size=7.3
            )

        # Reserve exact height at bottom of page (y_bot = 26) for Section 5 (Fallback Troubleshooting Matrix)
        sec5_h = 104
        sec5_top = 26 + sec5_h

        # 4. Section 4: Complete Line-by-Line Commented Code & Standout Terminal Commands
        y_cursor -= 6
        sec4_h = max(130, y_cursor - sec5_top - 6)
        max_code_lines = int((sec4_h - 20) / 8.85)
        rich_code = enrich_code_lines_to_fill_box(pnum, code_lines, max_lines=max_code_lines)
        y_cursor = draw_terminal_code_box(
            c, 56, y_cursor, avail_w, sec4_h,
            "4. Line-by-Line Commented Code & Terminal Commands",
            rich_code, font_size=6.65
        )

        # 5. Section 5: Self-Healing Verification & Fallback Troubleshooting ("If XYZ Fails -> Option A / B")
        fallback_lines = get_fallback_recovery_lines(pnum)
        draw_labeled_box(
            c, 56, sec5_top, avail_w, sec5_h,
            "5. Live Verification Checks, Server Script Pulling & Fallback Troubleshooting (If XYZ Fails -> Option A / B)",
            fallback_lines, INK_AMBER, BOX_FALLBACK_BG, title_color=INK_AMBER, mono=False, font_size=6.7
        )

        c.showPage()

        # Append enriched content to Markdown manual
        md_lines.append(f"## {title}")
        md_lines.append(f"**{sub}**")
        md_lines.append("")
        for tl in trap_lines:
            md_lines.append(f"- {clean_glyphs(tl)}")
        md_lines.append("")
        md_lines.append("### Line-by-Line Commented Code & Terminal Commands")
        md_lines.append("```bash")
        md_lines.extend([clean_glyphs(cl) for cl in rich_code])
        md_lines.append("```")
        md_lines.append("")
        md_lines.append("### Live Verification & Fallback Troubleshooting (If XYZ Fails -> Option A / Option B)")
        for fl in fallback_lines:
            md_lines.append(f"- {clean_glyphs(fl)}")
        md_lines.append("")

    c.save()
    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"BUILT_DENSE_100PAGE_PDF: {OUT_PDF}")
    print(f"BUILT_DENSE_100PAGE_MD:  {OUT_MD}")
    return pages


def build_3page_visual_spread_images(pages):
    """Renders 6 high-resolution 3-page side-by-side visual engineering notebook spreads (.png)
    with all 5 sections, embedded screenshots, standout terminal badges, and zero empty white space!"""
    SPREADS_DIR.mkdir(parents=True, exist_ok=True)
    try:
        f_hdr = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 13)
        f_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
        f_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 11)
        f_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 11)
        f_reg = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 10)
        f_mono = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 10)
        f_badge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 10)
    except Exception:
        f_hdr = f_title = f_sub = f_bold = f_reg = f_mono = f_badge = ImageFont.load_default()

    spread_groups = [
        ("ENGR852_Visual_Spread_01_XQuartz_VPN_SSH_Setup.png", [5, 6, 7]),
        ("ENGR852_Visual_Spread_02_Server_Isolation_and_Tools.png", [8, 9, 10]),
        ("ENGR852_Visual_Spread_03_Chapter10_SAD_and_MotionVectors.png", [13, 14, 15]),
        ("ENGR852_Visual_Spread_04_8Bit_Trap_vs_16Bit_Datapath.png", [20, 21, 22]),
        ("ENGR852_Visual_Spread_05_Testbenches_0000_0100_FF00.png", [33, 36, 39]),
        ("ENGR852_Visual_Spread_06_14nm_Physical_Design_and_GitHub.png", [62, 64, 95]),
    ]

    img_map = {
        5: SCREENSHOTS_DIR / "gp_vpn_connecting.png",
        6: SCREENSHOTS_DIR / "gp_vpn_connected_and_xquartz_xterm.png",
        7: SCREENSHOTS_DIR / "ssh_x11_multi_terminal_mahmoodi.png",
        62: SCREENSHOTS_DIR / "v9_signoff_clean_layout.png",
    }

    page_w, page_h = 900, 1180
    spread_w = page_w * 3 + 40
    spread_h = page_h + 24

    for fname, pnums in spread_groups:
        img = PILImage.new("RGB", (spread_w, spread_h), (218, 212, 200))
        draw = ImageDraw.Draw(img)

        for col_idx, pnum in enumerate(pnums):
            title, sub, stages, tbl_rows, trap_lines, code_lines = pages[pnum - 1]
            title = clean_glyphs(title)
            sub = clean_glyphs(sub)
            ox = 10 + col_idx * (page_w + 10)
            oy = 12

            # Paper rectangle & graph grid
            draw.rectangle([ox, oy, ox + page_w, oy + page_h], fill=(250, 248, 242), outline=(140, 135, 125), width=2)
            for gx in range(ox + 36, ox + page_w - 10, 18):
                draw.line([(gx, oy + 18), (gx, oy + page_h - 18)], fill=(228, 224, 212), width=1)
            for gy in range(oy + 18, oy + page_h - 18, 18):
                draw.line([(ox + 36, gy), (ox + page_w - 10, gy)], fill=(228, 224, 212), width=1)

            # Red margin line & spiral holes
            draw.line([(ox + 48, oy + 18), (ox + 48, oy + page_h - 18)], fill=(248, 150, 150), width=2)
            for ry in range(oy + 34, oy + page_h - 26, 34):
                draw.ellipse([ox + 14, ry - 5, ox + 24, ry + 5], fill=(190, 198, 210), outline=(90, 100, 115))
                draw.line([(ox + 2, ry), (ox + 16, ry)], fill=(90, 100, 115), width=2)

            # Header
            draw.text((ox + 58, oy + 18), f"ENGR 852 VISUAL NOTEBOOK - PAGE {pnum} OF 100", fill=(29, 78, 216), font=f_hdr)
            draw.text((ox + 58, oy + 36), title[:82], fill=(15, 23, 42), font=f_title)
            draw.line([(ox + 58, oy + 54), (ox + page_w - 16, oy + 54)], fill=(15, 23, 42), width=2)
            draw.text((ox + 58, oy + 58), sub[:96], fill=(21, 128, 61), font=f_sub)

            # 1. Section 1: 4-Stage Pipeline Schematic Boxes
            sy = oy + 80
            draw.rectangle([ox + 58, sy, ox + page_w - 16, sy + 122], fill=(255, 255, 255), outline=(15, 23, 42), width=2)
            draw.text((ox + 66, sy + 5), "1. Annotated Visual Schematic & GUI Action Flow:", fill=(15, 23, 42), font=f_bold)
            bw = 182
            for s_idx, (st_t, st_l) in enumerate(stages[:4]):
                bx = ox + 66 + s_idx * 204
                by = sy + 24
                bcol = [(29, 78, 216), (21, 128, 61), (185, 28, 28), (109, 40, 217)][s_idx % 4]
                bgcol = [(239, 246, 255), (240, 253, 244), (254, 242, 242), (245, 243, 255)][s_idx % 4]
                draw.rectangle([bx, by, bx + bw, by + 90], fill=bgcol, outline=bcol, width=2)
                draw.text((bx + 5, by + 4), clean_glyphs(st_t)[:23], fill=bcol, font=f_bold)
                draw.line([(bx + 4, by + 19), (bx + bw - 4, by + 19)], fill=bcol, width=1)
                for l_i, sl in enumerate(st_l[:4]):
                    draw.text((bx + 5, by + 23 + l_i * 16), clean_glyphs(sl)[:25], fill=(15, 23, 42), font=f_mono)
                if s_idx < 3:
                    ax1, ax2, ay = bx + bw, bx + 204, by + 45
                    draw.line([(ax1, ay), (ax2, ay)], fill=(15, 23, 42), width=2)

            # 2. Section 2: Verification Table
            ty = sy + 130
            draw.text((ox + 58, ty), "2. Step-by-Step Verification & Mapping Table:", fill=(15, 23, 42), font=f_bold)
            ty += 16
            row_h = 22
            ncols = len(tbl_rows[0])
            cw = int((page_w - 74) / ncols)
            for r_i, r_data in enumerate(tbl_rows[:7]):
                ry = ty + r_i * row_h
                rbg = (30, 58, 138) if r_i == 0 else ((255, 255, 255) if r_i % 2 == 1 else (241, 245, 249))
                tcol = (255, 255, 255) if r_i == 0 else (15, 23, 42)
                rfnt = f_bold if r_i == 0 else f_reg
                draw.rectangle([ox + 58, ry, ox + page_w - 16, ry + row_h], fill=rbg, outline=(148, 163, 184), width=1)
                for c_i, cell in enumerate(r_data):
                    cx = ox + 58 + c_i * cw
                    draw.line([(cx, ry), (cx, ry + row_h)], fill=(148, 163, 184), width=1)
                    draw.text((cx + 4, ry + 5), clean_glyphs(cell)[: int(cw / 5.7)], fill=tcol, font=rfnt)

            # 3. Section 3: [!] TRAP Box (+ Embedded Screenshot on Pages 5, 6, 7, 62!)
            ky = ty + min(len(tbl_rows), 7) * row_h + 10
            if pnum in img_map and img_map[pnum].exists():
                sec3_h = 132
                left_w = int((page_w - 74) * 0.48)
                right_w = (page_w - 74) - left_w - 8
                draw.rectangle([ox + 58, ky, ox + 58 + left_w, ky + sec3_h], fill=(254, 242, 242), outline=(185, 28, 28), width=2)
                draw.text((ox + 64, ky + 5), "3. [!] TRAP & Visual Check [!]", fill=(185, 28, 28), font=f_bold)
                for t_i, tl in enumerate(trap_lines[:3]):
                    clean_tl = clean_glyphs(tl.replace("RED:", "").replace("GREEN:", "").replace("BLUE:", ""))
                    draw.text((ox + 64, ky + 24 + t_i * 32), clean_tl[:56], fill=(15, 23, 42), font=f_reg)
                    if len(clean_tl) > 56:
                        draw.text((ox + 64, ky + 38 + t_i * 32), clean_tl[56:112], fill=(15, 23, 42), font=f_reg)
                rx = ox + 58 + left_w + 8
                draw.rectangle([rx, ky, rx + right_w, ky + sec3_h], fill=(255, 255, 255), outline=(29, 78, 216), width=2)
                try:
                    shot = PILImage.open(img_map[pnum]).convert("RGB")
                    shot.thumbnail((right_w - 8, sec3_h - 12))
                    img.paste(shot, (rx + 4, ky + 6))
                except Exception:
                    pass
                ky += sec3_h + 8
            else:
                sec3_h = 80
                draw.rectangle([ox + 58, ky, ox + page_w - 16, ky + sec3_h], fill=(254, 242, 242), outline=(185, 28, 28), width=2)
                draw.text((ox + 66, ky + 5), "3. [!] TRAP / Critical Engineering Note & Why It Happens [!]", fill=(185, 28, 28), font=f_bold)
                for t_i, tl in enumerate(trap_lines[:3]):
                    clean_tl = clean_glyphs(tl.replace("RED:", "").replace("GREEN:", "").replace("BLUE:", ""))
                    draw.text((ox + 66, ky + 24 + t_i * 17), clean_tl[:115], fill=(15, 23, 42), font=f_reg)
                ky += sec3_h + 8

            # Reserve bottom Section 5 (Fallback Troubleshooting Matrix)
            sec5_h = 166
            sec5_y = oy + page_h - 14 - sec5_h

            # 4. Section 4: Line-by-Line Commented Code & Standout Terminal Badges
            cy = ky
            ch = sec5_y - cy - 8
            draw.rectangle([ox + 58, cy, ox + page_w - 16, cy + ch], fill=(248, 250, 252), outline=(109, 40, 217), width=2)
            draw.rectangle([ox + 58, cy, ox + page_w - 16, cy + 20], fill=(109, 40, 217))
            draw.text((ox + 66, cy + 3), "4. Line-by-Line Commented Code & Highlighted Terminal Commands:", fill=(255, 255, 255), font=f_bold)

            max_c_lines = int((ch - 24) / 16)
            rich_code = enrich_code_lines_to_fill_box(pnum, code_lines, max_lines=max_c_lines)
            for c_i, raw_cl in enumerate(rich_code[:max_c_lines]):
                ly = cy + 24 + c_i * 16
                cl = clean_glyphs(raw_cl)
                badge = None
                bcol = None
                rbg = None
                tcol = (15, 23, 42)
                if cl.startswith("TERM_MAC:"):
                    badge, bcol, rbg = "MACBOOK", (30, 58, 138), (219, 234, 254)
                    cl = cl[len("TERM_MAC:"):].strip()
                elif cl.startswith("TERM_XQ:"):
                    badge, bcol, rbg = "XQUARTZ", (15, 118, 110), (204, 251, 241)
                    cl = cl[len("TERM_XQ:"):].strip()
                elif cl.startswith("TERM_SFSU:"):
                    badge, bcol, rbg = "926784856@mahmoodi", (180, 83, 9), (254, 243, 199)
                    cl = cl[len("TERM_SFSU:"):].strip()
                elif cl.startswith("OUT_OK:"):
                    badge, bcol, rbg = "OUTPUT", (21, 128, 61), (220, 252, 231)
                    cl = cl[len("OUT_OK:"):].strip()
                    tcol = (21, 128, 61)

                if rbg:
                    draw.rectangle([ox + 62, ly - 1, ox + page_w - 20, ly + 14], fill=rbg)
                tx = ox + 66
                if badge:
                    bw_p = len(badge) * 6 + 10
                    draw.rectangle([ox + 64, ly, ox + 64 + bw_p, ly + 13], fill=bcol)
                    draw.text((ox + 68, ly + 1), badge, fill=(255, 255, 255), font=f_badge)
                    tx = ox + 68 + bw_p
                max_ch = int((ox + page_w - 22 - tx) / 6.0)
                draw.text((tx, ly), cl[:max_ch], fill=tcol, font=f_mono)

            # 5. Section 5: Live Log Checks & Fallback Troubleshooting (If XYZ Fails -> Option A / B)
            draw.rectangle([ox + 58, sec5_y, ox + page_w - 16, sec5_y + sec5_h], fill=(255, 251, 235), outline=(180, 83, 9), width=2)
            draw.rectangle([ox + 58, sec5_y, ox + page_w - 16, sec5_y + 20], fill=(180, 83, 9))
            draw.text((ox + 66, sec5_y + 3), "5. Live Verification Checks, Server Script Pulling & Fallback Recovery (Plan A / B):", fill=(255, 255, 255), font=f_bold)
            fb_lines = get_fallback_recovery_lines(pnum)
            for f_i, fl in enumerate(fb_lines[:8]):
                fly = sec5_y + 24 + f_i * 17
                clean_fl = clean_glyphs(fl)
                fcol = (15, 23, 42)
                if clean_fl.startswith("RED:"):
                    fcol = (185, 28, 28)
                    clean_fl = clean_fl[4:]
                elif clean_fl.startswith("BLUE:"):
                    fcol = (29, 78, 216)
                    clean_fl = clean_fl[5:]
                elif clean_fl.startswith("GREEN:"):
                    fcol = (21, 128, 61)
                    clean_fl = clean_fl[6:]
                draw.text((ox + 66, fly), clean_fl[:122], fill=fcol, font=f_reg)

        out_path = SPREADS_DIR / fname
        img.save(str(out_path), format="PNG", optimize=True)
        print(f"BUILT_DENSE_SPREAD_PNG: {out_path}")


if __name__ == "__main__":
    all_pages = render_100page_pdf_and_md()
    build_3page_visual_spread_images(all_pages)
