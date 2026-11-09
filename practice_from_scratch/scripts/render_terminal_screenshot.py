#!/usr/bin/env python3
"""
Renders a terminal log file into a high-contrast macOS Terminal / XQuartz screenshot PNG
so that every one-liner executed on the MacBook Air or SFSU EDA server (mahmoodi)
automatically produces a visual screenshot of the COMPLETE terminal output on the GitHub sub-branch.

Supports BOTH CLI flag syntax:
  python3 render_terminal_screenshot.py --log <log> --out <png> [--title <title>] [--host <host>] [--exit-code <code>]
AND legacy positional syntax:
  python3 render_terminal_screenshot.py <step_id> <exit_code> <cmd_str> <log_file> <out_png>
"""

import argparse
import os
import re
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    text = ANSI_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "".join(ch if (32 <= ord(ch) <= 126 or ch in ("\n", "\t")) else " " for ch in text)


def load_mono_font(size: int):
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
        "/usr/share/fonts/ liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/gnu-free/FreeMono.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_line(line: str, max_chars: int = 128):
    line = line.expandtabs(4)
    if not line:
        return [""]
    out = []
    while len(line) > max_chars:
        out.append(line[:max_chars])
        line = "  " + line[max_chars:]
    out.append(line)
    return out


def render_terminal_png(log_path: str, out_path: str, title: str, host: str, exit_code: int):
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            raw = strip_ansi(f.read())
    else:
        raw = f"[Log file not found: {log_path}]"

    raw_lines = raw.splitlines()
    wrapped = []
    for rl in raw_lines:
        wrapped.extend(wrap_line(rl, max_chars=128))

    # Never truncate typical step output; allow up to 260 full lines dynamically!
    max_lines = 260
    if len(wrapped) > max_lines:
        head_part = wrapped[:110]
        tail_part = wrapped[-145:]
        omitted = len(wrapped) - 255
        wrapped = head_part + [f"   ... [{omitted} intermediate output lines in full .log file] ..."] + tail_part

    line_h = 19
    pad_x = 22
    header_h = 44
    footer_h = 34
    width = 1220
    body_h = max(240, len(wrapped) * line_h + 24)
    height = header_h + body_h + footer_h

    img = Image.new("RGB", (width, height), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    font_body = load_mono_font(13)
    font_title = load_mono_font(13)

    # Top macOS Terminal Window Chrome
    draw.rectangle([0, 0, width, header_h], fill=(30, 41, 59))
    draw.line([0, header_h, width, header_h], fill=(71, 85, 105), width=1)

    # Traffic lights
    draw.ellipse([16, 15, 30, 29], fill=(239, 68, 68))
    draw.ellipse([38, 15, 52, 29], fill=(245, 158, 11))
    draw.ellipse([60, 15, 74, 29], fill=(34, 197, 94))

    header_str = f"Terminal Output Auto-Capture — {title}  [{host}]"
    draw.text((92, 14), header_str[:105], fill=(226, 232, 240), font=font_title)

    # Render each line of terminal output
    y = header_h + 12
    for line in wrapped:
        low = line.lower()
        if line.startswith("=== ") or line.startswith("# ===="):
            color = (147, 197, 253)  # Soft blue banner
        elif line.startswith("$ ") or "command       :" in low:
            color = (253, 224, 71)   # Yellow command highlight
        elif any(k in low for k in ["error", "fail", "fatal", "trap", "violation", "syntax error", "command not found"]):
            color = (252, 165, 165)  # Red alert
        elif any(k in low for k in ["pass", "success", "clean", "0000", "0100", "ff00", "exit_code     : 0", "ready"]):
            color = (134, 239, 172)  # Green pass
        else:
            color = (241, 245, 249)  # Crisp white/slate terminal text
        draw.text((pad_x, y), line, fill=color, font=font_body)
        y += line_h

    # Bottom status bar
    fy = height - footer_h
    draw.rectangle([0, fy, width, height], fill=(2, 6, 23))
    draw.line([0, fy, width, fy], fill=(51, 65, 85), width=1)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    badge_col = (34, 197, 94) if exit_code == 0 else (239, 68, 68)
    status_str = f"EXIT_CODE={exit_code}  |  Lines Captured: {len(raw_lines)}  |  Host: {host}  |  Timestamp: {ts}"
    draw.text((pad_x, fy + 9), status_str, fill=badge_col, font=font_body)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path, "PNG")


def main():
    # Support both flag-based (--log / --out) and legacy positional invocations
    if len(sys.argv) == 6 and not sys.argv[1].startswith("-"):
        step_id = sys.argv[1]
        try:
            exit_code = int(sys.argv[2])
        except ValueError:
            exit_code = 0
        cmd_str = sys.argv[3]
        log_path = sys.argv[4]
        out_path = sys.argv[5]
        host = os.uname().nodename
        title = f"{step_id}: {cmd_str[:48]}"
        render_terminal_png(log_path, out_path, title, host, exit_code)
        return

    parser = argparse.ArgumentParser(description="Render terminal log to PNG")
    parser.add_argument("--log", required=True, help="Path to terminal log file")
    parser.add_argument("--out", required=True, help="Path to output PNG file")
    parser.add_argument("--title", default="Terminal Step", help="Step title")
    parser.add_argument("--host", default=os.uname().nodename, help="Hostname")
    parser.add_argument("--exit-code", type=int, default=0, help="Command exit code")
    args, _ = parser.parse_known_args()
    render_terminal_png(args.log, args.out, args.title, args.host, args.exit_code)


if __name__ == "__main__":
    main()
