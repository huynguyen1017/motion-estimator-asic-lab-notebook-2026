from pathlib import Path
import re

root = Path(__file__).resolve().parent.parent
src = (root / "rtl/professor/top.v").read_text()
outdir = root / "rtl/full_precision_variant"
outdir.mkdir(parents=True, exist_ok=True)
text = src

def edit_module(name, fn):
    global text
    pattern = r"(?ms)^module " + re.escape(name) + r"\s*\(.*?^endmodule"
    found = re.search(pattern, text)
    if not found:
        raise RuntimeError(f"Missing module: {name}")
    old = found.group(0)
    new = fn(old)
    if new == old:
        raise RuntimeError(f"Module unchanged: {name}")
    text = text[:found.start()] + new + text[found.end():]

def top_fix(v):
    v = v.replace("output [7:0] BestDist;", "output [15:0] BestDist;")
    v = v.replace("wire [7:0] BestDist;", "wire [15:0] BestDist;")
    v = v.replace("wire [127:0] Accumulate;", "wire [255:0] Accumulate;")
    return v

def pe_fix(v, last=False):
    if not last:
        v = v.replace("output [7:0] Accumulate, Rpipe;", "output [15:0] Accumulate;\n\toutput [7:0] Rpipe;")
        v = v.replace("reg [7:0] Accumulate, AccumulateIn, difference, selected_s, difference_temp, Rpipe;", "reg [15:0] Accumulate, AccumulateIn;\n\treg [7:0] difference, selected_s, difference_temp, Rpipe;")
    else:
        v = v.replace("output [7:0] Accumulate;", "output [15:0] Accumulate;")
        v = v.replace("reg [7:0] Accumulate, AccumulateIn, difference, selected_s;", "reg [15:0] Accumulate, AccumulateIn;\n\treg [7:0] difference, selected_s;")
    v = v.replace("\n\treg Carry;", "")
    v = v.replace("{Carry,AccumulateIn} = Accumulate + difference;", "AccumulateIn = Accumulate + {8'h00, difference};")
    v = re.sub(r"(?m)^\s*if \(Carry == 1\) AccumulateIn = 8'hFF;[^\n]*\n", "\n", v)
    return v

def comp_fix(v):
    v = v.replace("input [8*16-1:0] PEout;", "input [16*16-1:0] PEout;")
    v = v.replace("output [7:0] BestDist;", "output [15:0] BestDist;")
    v = v.replace("reg [7:0] BestDist, newDist;", "reg [15:0] BestDist, newDist;")
    v = v.replace("if (CompStart == 0) BestDist <= 8'hFF;", "if (CompStart == 0) begin BestDist <= 16'hFFFF; motionX <= 4'h0; motionY <= 4'h0; end")
    v = v.replace("8'hFF", "16'hFFFF")
    for i in range(16):
        old = f"PEout[{8*i+7}:{8*i}]"
        new = f"PEout[{16*i+15}:{16*i}]"
        v = v.replace(old, new)
    return v

def pe_total_fix(v):
    v = v.replace("output [127:0] Accumulate;", "output [255:0] Accumulate;")
    for i in range(16):
        v = v.replace(f"Accumulate[{8*i+7}:{8*i}]", f"Accumulate[{16*i+15}:{16*i}]")
    return v

edit_module("top", top_fix)
edit_module("PE", lambda s: pe_fix(s, False))
edit_module("PEend", lambda s: pe_fix(s, True))
edit_module("Comparator", comp_fix)
edit_module("PEtotal", pe_total_fix)
assert "wire [255:0] Accumulate" in text
assert "output [255:0] Accumulate" in text
assert "output [15:0] BestDist" in text
assert text.count("16'hFFFF") >= 3
dest = outdir / "top_full_precision.v"
dest.write_text("// Independent 16-bit SAD architecture variant. Original professor RTL is untouched.\n" + text)
print("CREATED", dest)
print("ORIGINAL_AND_VARIANT_BYTE_COUNTS", len(src), len(text))
