#!/usr/bin/env python3
"""
render_terminal_screenshot.py
Renders ONLY the terminal window output (prompt, command, stdout/stderr, exit code badge)
into a clean macOS Dark Terminal PNG screenshot (`practice_from_scratch/screenshots/<step>_terminal.png`).
Works with Pillow (PIL) on MacBook Air (`~/.venv/bin/python3`) AND has a built-in zero-dependency
pure-Python (`zlib` + `struct` + 8x12 bitmap font) fallback so it ALSO works directly on
`926784856@mahmoodi.rcc.at.sfsu.edu` where Pillow is not installed!
"""
import sys
import os
import zlib
import struct
from datetime import datetime

def clean_lines(text, max_cols=112, max_lines=48):
    raw = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    wrapped = []
    for line in raw:
        # Strip basic ANSI escape codes if any
        clean = ""
        i = 0
        while i < len(line):
            if line[i] == "\x1b" and i + 1 < len(line) and line[i+1] == "[":
                i += 2
                while i < len(line) and not ("@" <= line[i] <= "~"):
                    i += 1
                i += 1
            else:
                ch = line[i]
                clean += ch if 32 <= ord(ch) <= 126 or ch == "\t" else " "
                i += 1
        clean = clean.expandtabs(4)
        if not clean:
            wrapped.append("")
        else:
            while len(clean) > max_cols:
                wrapped.append(clean[:max_cols])
                clean = "  " + clean[max_cols:]
            wrapped.append(clean)
    if len(wrapped) > max_lines:
        wrapped = (
            wrapped[:16]
            + [f"... [{len(wrapped) - max_lines} middle lines omitted in screenshot; full output in logs/] ..."]
            + wrapped[-(max_lines - 17):]
        )
    return wrapped

def render_with_pil(title, subtitle, lines, exit_code, out_path):
    from PIL import Image, ImageDraw, ImageFont
    font_candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Courier New.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/liberation-mono/LiberationMono-Regular.ttf",
    ]
    font = None
    title_font = None
    for fc in font_candidates:
        if os.path.exists(fc):
            try:
                font = ImageFont.truetype(fc, 15)
                title_font = ImageFont.truetype(fc, 14)
                break
            except Exception:
                pass
    if font is None:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()

    line_h = 21
    pad_x = 24
    header_h = 56
    footer_h = 34
    width = 1180
    height = header_h + max(8, len(lines)) * line_h + footer_h + 24

    img = Image.new("RGB", (width, height), (18, 20, 26))
    draw = ImageDraw.Draw(img)

    # Outer border & title bar
    draw.rounded_rectangle([2, 2, width - 3, height - 3], radius=12, fill=(24, 26, 33), outline=(68, 74, 90), width=2)
    draw.rounded_rectangle([4, 4, width - 5, header_h], radius=10, fill=(38, 41, 52))
    draw.rectangle([4, header_h - 10, width - 5, header_h], fill=(38, 41, 52))

    # Traffic lights
    draw.ellipse([18, 18, 32, 32], fill=(255, 95, 86))
    draw.ellipse([40, 18, 54, 32], fill=(255, 189, 46))
    draw.ellipse([62, 18, 76, 32], fill=(39, 201, 63))

    # Title & status pill
    draw.text((94, 10), title[:78], fill=(235, 239, 245), font=title_font)
    draw.text((94, 30), subtitle[:95], fill=(156, 166, 184), font=title_font)

    badge_ok = (exit_code == 0)
    badge_bg = (22, 120, 62) if badge_ok else (165, 42, 42)
    badge_txt = f"EXIT={exit_code} PASS" if badge_ok else f"EXIT={exit_code} CHECK"
    draw.rounded_rectangle([width - 175, 14, width - 20, 42], radius=8, fill=badge_bg)
    draw.text((width - 158, 20), badge_txt, fill=(255, 255, 255), font=title_font)

    y = header_h + 12
    for idx, line in enumerate(lines):
        if line.startswith("$ ") or line.startswith("huynguyen@MacBook-Air") or line.startswith("[926784856@mahmoodi"):
            color = (110, 231, 183)
        elif "PASS" in line or "LOGGER_ACTIVE" in line or "REMOTE_LOGGER_READY" in line or "BestDist" in line:
            color = (134, 239, 172)
        elif "ERROR" in line or "command not found" in line or "No such file" in line:
            color = (252, 165, 165)
        elif line.startswith("===") or line.startswith("..."):
            color = (147, 197, 253)
        else:
            color = (226, 232, 240)
        draw.text((pad_x, y), line, fill=color, font=font)
        y += line_h

    # Footer bar
    draw.line([(12, height - footer_h), (width - 12, height - footer_h)], fill=(52, 58, 72), width=1)
    footer_msg = f"Auto-Captured Terminal Output Only (No Desktop Windows) | Branch: manual-practice-macbook-air | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    draw.text((pad_x, height - footer_h + 8), footer_msg, fill=(130, 142, 160), font=title_font)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path, "PNG")

# Compact 5x7 uppercase/ASCII fallback glyph generator for pure-stdlib Linux servers without PIL
GLYPHS_5X7 = {
    ' ': [0,0,0,0,0,0,0],
    '!': [4,4,4,4,0,0,4],
    '"': [10,10,10,0,0,0,0],
    '#': [10,31,10,10,31,10,0],
    '$': [4,15,20,14,5,30,4],
    '%': [24,25,2,4,8,19,3],
    '&': [12,18,20,8,21,18,13],
    "'": [4,4,8,0,0,0,0],
    '(': [2,4,8,8,8,4,2],
    ')': [8,4,2,2,2,4,8],
    '*': [0,4,21,14,21,4,0],
    '+': [0,4,4,31,4,4,0],
    ',': [0,0,0,0,4,4,8],
    '-': [0,0,0,31,0,0,0],
    '.': [0,0,0,0,0,12,12],
    '/': [1,1,2,4,8,16,16],
    '0': [14,17,19,21,25,17,14],
    '1': [4,12,4,4,4,4,14],
    '2': [14,17,1,2,4,8,31],
    '3': [31,2,4,2,1,17,14],
    '4': [2,6,10,18,31,2,2],
    '5': [31,16,30,1,1,17,14],
    '6': [6,8,16,30,17,17,14],
    '7': [31,1,2,4,8,8,8],
    '8': [14,17,17,14,17,17,14],
    '9': [14,17,17,15,1,2,12],
    ':': [0,12,12,0,12,12,0],
    ';': [0,12,12,0,12,4,8],
    '<': [2,4,8,16,8,4,2],
    '=': [0,0,31,0,31,0,0],
    '>': [8,4,2,1,2,4,8],
    '?': [14,17,1,2,4,0,4],
    '@': [14,17,1,13,21,21,14],
    'A': [14,17,17,31,17,17,17],
    'B': [30,17,17,30,17,17,30],
    'C': [14,17,16,16,16,17,14],
    'D': [28,18,17,17,17,18,28],
    'E': [31,16,16,30,16,16,31],
    'F': [31,16,16,30,16,16,16],
    'G': [14,17,16,23,17,17,15],
    'H': [17,17,17,31,17,17,17],
    'I': [14,4,4,4,4,4,14],
    'J': [7,2,2,2,2,18,12],
    'K': [17,18,20,24,20,18,17],
    'L': [16,16,16,16,16,16,31],
    'M': [17,27,21,21,17,17,17],
    'N': [17,17,25,21,19,17,17],
    'O': [14,17,17,17,17,17,14],
    'P': [30,17,17,30,16,16,16],
    'Q': [14,17,17,17,21,18,13],
    'R': [30,17,17,30,20,18,17],
    'S': [15,16,16,14,1,1,30],
    'T': [31,4,4,4,4,4,4],
    'U': [17,17,17,17,17,17,14],
    'V': [17,17,17,17,17,10,4],
    'W': [17,17,17,21,21,21,10],
    'X': [17,17,10,4,10,17,17],
    'Y': [17,17,17,10,4,4,4],
    'Z': [31,1,2,4,8,16,31],
    '[': [14,8,8,8,8,8,14],
    '\\': [16,16,8,4,2,1,1],
    ']': [14,2,2,2,2,2,14],
    '^': [4,10,17,0,0,0,0],
    '_': [0,0,0,0,0,0,31],
    '`': [8,4,2,0,0,0,0],
    '{': [2,4,4,8,4,4,2],
    '|': [4,4,4,4,4,4,4],
    '}': [8,4,4,2,4,4,8],
    '~': [0,0,8,21,2,0,0],
}

def render_pure_stdlib(title, subtitle, lines, exit_code, out_path):
    scale = 2
    cw = 6 * scale
    ch = 9 * scale
    cols = 114
    width = cols * cw + 32
    all_rows = [
        f"TERMINAL: {title[:90]}",
        f"INFO:     {subtitle[:90]} | EXIT={exit_code}",
        "=" * (cols - 2),
    ] + lines
    height = len(all_rows) * ch + 32

    bg = (24, 26, 33)
    buf = bytearray(width * height * 3)
    for i in range(0, len(buf), 3):
        buf[i] = bg[0]
        buf[i+1] = bg[1]
        buf[i+2] = bg[2]

    def set_px(x, y, c):
        if 0 <= x < width and 0 <= y < height:
            idx = (y * width + x) * 3
            buf[idx] = c[0]
            buf[idx+1] = c[1]
            buf[idx+2] = c[2]

    for r_idx, row_str in enumerate(all_rows):
        if r_idx < 2:
            color = (147, 197, 253)
        elif row_str.startswith("$ ") or "mahmoodi" in row_str or "MacBook-Air" in row_str:
            color = (110, 231, 183)
        elif "PASS" in row_str or "BestDist" in row_str:
            color = (134, 239, 172)
        elif "ERROR" in row_str or "not found" in row_str:
            color = (252, 165, 165)
        else:
            color = (226, 232, 240)
        y0 = 16 + r_idx * ch
        for c_idx, ch_char in enumerate(row_str[:cols]):
            glyph = GLYPHS_5X7.get(ch_char.upper(), GLYPHS_5X7[' '])
            x0 = 16 + c_idx * cw
            for gy in range(7):
                bits = glyph[gy]
                for gx in range(5):
                    if (bits >> (4 - gx)) & 1:
                        for sy in range(scale):
                            for sx in range(scale):
                                set_px(x0 + gx * scale + sx, y0 + gy * scale + sy, color)

    raw_scanlines = bytearray()
    stride = width * 3
    for y in range(height):
        raw_scanlines.append(0)
        raw_scanlines.extend(buf[y * stride : (y + 1) * stride])

    def png_chunk(chunk_type, data):
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(bytes(raw_scanlines), 6)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", idat)
        + png_chunk(b"IEND", b"")
    )
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(png_bytes)

def main():
    if len(sys.argv) < 5:
        print("Usage: render_terminal_screenshot.py <step_id> <exit_code> <log_file> <out_png> [command_str]")
        sys.exit(1)
    step_id = sys.argv[1]
    exit_code = int(sys.argv[2])
    log_file = sys.argv[3]
    out_png = sys.argv[4]
    cmd_str = sys.argv[5] if len(sys.argv) > 5 else step_id

    if os.path.exists(log_file):
        with open(log_file, "r", errors="replace") as f:
            content = f.read()
    else:
        content = f"Log file not found: {log_file}"

    lines = clean_lines(content)
    host = os.uname().nodename
    title = f"{host} — Step: {step_id}"
    subtitle = f"Command: {cmd_str}"
    try:
        render_with_pil(title, subtitle, lines, exit_code, out_png)
    except Exception:
        render_pure_stdlib(title, subtitle, lines, exit_code, out_png)
    print(f"TERMINAL_SCREENSHOT_SAVED: {out_png}")

if __name__ == "__main__":
    main()
