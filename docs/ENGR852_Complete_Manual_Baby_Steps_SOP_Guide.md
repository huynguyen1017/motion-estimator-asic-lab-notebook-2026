# ENGR 852 Advanced Digital Design — Motion Estimator ASIC Complete Manual Reproduction Guide (Baby-Steps SOP)

## 1. Purpose and Scope

This Standard Operating Procedure (SOP) provides a self-contained, command-by-command, click-by-click manual for reproducing the entire **ENGR 852 Motion Estimator 14nm ASIC project at 520 MHz (`1.923 ns` clock period)** from scratch on a brand-new MacBook Air (macOS) connected to the SFSU EDA server (`mahmoodi.rcc.at.sfsu.edu`).

All terminology, equations, and architectural explanations strictly follow **Chapter 10, Section 10.4 (*Example of Explicit Style—Motion Estimator*, pp. 143–150)** of the ENGR 852 lecture notes (`motion_estimator.pdf`):

- **Block Matching Distortion Metric**: For a $16 \times 16$ reference macroblock $R$ (`r_{m,n}`) and a $31 \times 31$ search window $S$ (`s_{m+i,n+j}`), the Sum of Absolute Differences (SAD) distortion figure at candidate index $(i,j) \in [0,15] \times [0,15]$ is:
  $$D(i,j) = \sum_{m=0}^{15} \sum_{n=0}^{15} |r_{m,n} - s_{m+i,n+j}|$$
- **Coordinate Transformation to Signed Motion Vector**: The 256 candidate positions $(i,j) \in [0,15] \times [0,15]$ map to signed displacements $(i-8, j-8) \in [-8,+7] \times [-8,+7]$ (`8'hF8` to `8'h07` in 8-bit two's complement).
- **8-Bit Baseline Datapath (Section 10.4.1, pp. 147–148)**: Each of the 16 Processing Elements (`PE0..PE15`) contains an 8-bit saturating accumulator:
  ```verilog
  {Carry, AccumulateIn} = Accumulate + difference;
  if (Carry == 1) AccumulateIn = 8'hFF; // saturated
  ```
  The `Comparator` initializes `BestDist <= 8'hFF` when `CompStart == 0` and updates `BestDist`, `motionX`, and `motionY` only on strict inequality (`if (newDist < BestDist) newBest = 1;`).
- **16-Bit Non-Saturating Datapath Extension**: Because 256 pixel differences of up to `8'hFF` (`255`) can sum to $256 \times 255 = 65,280$ (`16'hFF00`), any candidate block whose cumulative SAD exceeds `255` saturates an 8-bit accumulator at `8'hFF`. Extending `Accumulate[15:0]`, `AccumulateIn[15:0]`, `PEout[255:0]` (`16 x 16-bit`), and `BestDist[15:0]` (initialized to `16'hFFFF`) eliminates intermediate saturation across all 256 candidate blocks.

---

## 2. Step-by-Step Setup on a New MacBook Air

### Step 2.1 — Open macOS Terminal and Install Command Line Tools
1. Press **Command (`⌘`) + Space** to open Spotlight Search.
2. Type `Terminal` and press **Return**.
3. Install the Apple Xcode Command Line Tools (provides `git`, `ssh`, `scp`, `make`, and `python3`):
   ```bash
   xcode-select --install
   ```
4. Create a clean local working directory for the course project:
   ```bash
   mkdir -p ~/Developer/engr852-motion-estimator
   cd ~/Developer/engr852-motion-estimator
   ```

### Step 2.2 — Connect to SFSU GlobalProtect VPN
1. Open **Palo Alto GlobalProtect** from the macOS menu bar (globe icon in the top-right corner).
2. Enter Portal address: `vpn.sfsu.edu` and click **Connect**.
3. Sign in with your SFSU campus ID (`<SFSU_ID>@sfsu.edu`), password, and Duo two-factor authentication.

### Step 2.3 — Configure Passwordless SSH Key Login to `mahmoodi.rcc.at.sfsu.edu`
1. In macOS Terminal, generate an Ed25519 SSH key pair (press Return at all prompts):
   ```bash
   ssh-keygen -t ed25519 -C "engr852-macbook" -f ~/.ssh/id_ed25519 -N ""
   ```
2. Copy your public key to the SFSU EDA server (replace `<SFSU_ID>` with your 9-digit SFSU student ID):
   ```bash
   cat ~/.ssh/id_ed25519.pub | ssh <SFSU_ID>@mahmoodi.rcc.at.sfsu.edu "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
   ```
3. Add a host alias to `~/.ssh/config` so X11 GUI forwarding works for Synopsys Verdi and Fusion Compiler:
   ```bash
   cat << 'EOF' >> ~/.ssh/config
   Host mahmoodi
       HostName mahmoodi.rcc.at.sfsu.edu
       User <SFSU_ID>
       IdentityFile ~/.ssh/id_ed25519
       ForwardX11 yes
       ForwardX11Trusted yes
       ServerAliveInterval 30
   EOF
   chmod 600 ~/.ssh/config
   ```

---

## 3. Inspecting the Original Course Files and Applying the Exact Modifications

### Step 3.1 — Original Course Files Provided by the Instructor
The original starter directory (`Motion Estimator RTL and Testbench`) contains six files:
- `top.v` — 8-bit saturating RTL (`PE`, `Rpipe`, `Control`, `Comparator`, `RMEM`, `SMEM`, `top`).
- `top_tb.v` — Random reference/search memory testbench with a `16'h01` (`+1`) perturbation at target displacement `(-5, 7)` (`8'hFB`, `8'h07`) and clock toggle `always #2.5 clock = ~clock;` (`200 MHz`, `5.0 ns` period).
- `top_tb_direct.v` — File-driven testbench reading `ref.txt` and `search.txt`.
- `ref.txt` — 256 bytes (`00..FF`) of reference macroblock pixels.
- `search.txt` — 961 bytes (`31 x 31`) of search window pixels where candidate block $(0,0)$, corresponding to signed motion vector `(-8, -8)` (`8'hF8`, `8'hF8`), matches `ref.txt` identically (`D(0,0) = 0`).
- `Makefile` — VCS compilation and simulation rules.

### Step 3.2 — Modification 1: Retargeting Testbenches to 520 MHz (`1.923 ns` Clock Period)
To run both RTL and post-synthesis/post-layout gate-level simulations at **520 MHz** (`T_clk = 1.923 ns`, half-period = `0.9615 ns`) without sub-picosecond rounding error:

1. Change `` `timescale 1ns/10ps `` to `` `timescale 1ns/100fs `` at line 2 of `top_tb.v` and `top_tb_direct.v`.
2. Change the clock generator from `always #2.5 clock = ~clock;` (`200 MHz`) to:
   ```verilog
   always #0.9615 clock = ~clock; // 520.02 MHz (1.9230 ns period)
   ```
3. Change the stimulus application delay inside the `for (i = 0; i < 4112; i = i + 1)` loop from `#1.5;` to `#0.02;` (`20 ps` post-posedge hold margin for 14nm standard cells):
   ```verilog
   @(posedge clock);#0.02; R = Rmem[AddressR]; S1 = Smem[AddressS1]; S2 = Smem[AddressS2];
   ```
4. Add FSDB waveform dumping inside the `initial` block so Synopsys Verdi (`nWave`) can inspect every hierarchy signal:
   ```verilog
   $fsdbDumpfile("waves.fsdb");
   $fsdbDumpvars(0);
   ```

### Step 3.3 — Modification 2: Creating the 16-Bit Non-Saturating Datapath (`rtl/16bit/top.v`)
Copy the original `top.v` to `rtl/16bit/top.v` and apply the following four exact module updates:

1. **`module PE` (`16-bit` accumulator without 8-bit saturation)**:
   ```verilog
   module PE (clock, R, S1, S2, S1S2mux, newDist, Accumulate, Rpipe);
     input clock;
     input [7:0] R, S1, S2;
     input S1S2mux, newDist;
     output [15:0] Accumulate;
     output [7:0] Rpipe;
     reg [15:0] Accumulate, AccumulateIn;
     reg [7:0] Rpipe;
     reg [7:0] difference;

     always @(posedge clock) Rpipe <= R;
     always @(posedge clock) Accumulate <= AccumulateIn;

     always @(R or S1 or S2 or S1S2mux or newDist or Accumulate) begin
       if (R < (S1S2mux ? S1 : S2)) difference = (S1S2mux ? S1 : S2) - R;
       else difference = R - (S1S2mux ? S1 : S2);
       AccumulateIn = Accumulate + {8'd0, difference};
       if (newDist == 1) AccumulateIn = {8'd0, difference};
     end
   endmodule
   ```

2. **`module Control` (terminal count hold at `13'h100F` = cycle 4111)**:
   In the original `Control` module, `count <= count + 1` wraps around after `12'hFFF` (`4095`), allowing `CompStart` to remain asserted past cycle 4111 (`13'h100F`). Extending `count` to `[12:0]` and holding at `13'h100F` freezes `CompStart` cleanly once all 256 candidate blocks plus the 15-cycle `Rpipe` fill complete (`16 * 256 + 15 = 4111` cycles, Table 10.1, p. 146):
   ```verilog
   reg [12:0] count;
   reg completed;
   always @(posedge clock) begin
     if (start == 0) begin
       count <= 13'd0;
       completed <= 1'b0;
     end else if (completed == 1'b0) begin
       if (count == 13'h100F) completed <= 1'b1;
       else count <= count + 13'd1;
     end
   end
   ```

3. **`module Comparator` (`16-bit` `BestDist` initialized to `16'hFFFF`, `256-bit` flattened `PEout`)**:
   ```verilog
   module Comparator (clock, CompStart, PEout, PEready, vectorX, vectorY, BestDist, motionX, motionY);
     input clock;
     input CompStart;
     input [255:0] PEout;
     input [15:0] PEready;
     input [3:0] vectorX, vectorY;
     output [15:0] BestDist;
     output [7:0] motionX, motionY;
     reg [15:0] BestDist, newDist;
     reg [7:0] motionX, motionY;
     reg newBest;
     integer n;

     always @(posedge clock)
       if (CompStart == 0) BestDist <= 16'hFFFF;
       else if (newBest == 1) begin
         BestDist <= newDist;
         motionX <= {{4{vectorX[3]}}, vectorX};
         motionY <= {{4{vectorY[3]}}, vectorY};
       end

     always @(BestDist or PEout or PEready or CompStart) begin
       newDist = 16'hFFFF;
       for (n = 0; n <= 15; n = n + 1) begin
         if (PEready[n] == 1) case (n)
           4'b0000: newDist = PEout[15:0];
           4'b0001: newDist = PEout[31:16];
           // ... (slices [16*n+15 : 16*n] through n = 15)
           4'b1111: newDist = PEout[255:240];
           default: newDist = 16'hFFFF;
         endcase
       end
       if ((|PEready == 0) || (CompStart == 0)) newBest = 0;
       else if (newDist < BestDist) newBest = 1;
       else newBest = 0;
     end
   endmodule
   ```

### Step 3.4 — Why `BestDist` Equals `16'h0000` vs. `16'h0100` vs. `16'hFF00` Across the Testbenches
| Testbench | Reference & Search Stimulus | Candidate Minimum SAD `BestDist` | Selected Motion Vector `(motionX, motionY)` | Technical Explanation (Chapter 10, Section 10.4) |
| :--- | :--- | :--- | :--- | :--- |
| **`top_tb_direct.v`** | `ref.txt` (`00..FF`) & `search.txt` (exact match at $(i,j)=(0,0)$) | **`8'h00`** (8-bit) / **`16'h0000`** (16-bit) | **`8'hF8, 8'hF8`** (`-8, -8`) | Zero pixel difference (`r_{m,n} == s_{m,n}` for all 256 pixels): $D(0,0) = 256 \times 0 = 0$. |
| **`top_tb.v`** | Random `Rmem` embedded at `(-5, 7)` with `+1` (`8'h01`) offset per pixel | **`8'hFF`** (8-bit saturated) / **`16'h0100`** (16-bit exact = `256`) | **`8'hFA, 8'h00`** (8-bit tie) / **`8'hFB, 8'h07`** (16-bit exact `-5, +7`) | At target `(-5, 7)`, $D(3,15) = 256 \times 1 = 256$ (`16'h0100`). In 8-bit RTL, `256` saturates to `8'hFF`, tying the prior `8'hFF` minimum so strict `<` (`255 < 255` false) cannot update `motionX/Y`. In 16-bit RTL, `256 < 16'h4978` updates `motionX = 8'hFB (-5), motionY = 8'h07 (+7)`. |
| **`top_tb_16bit.v`** | High-contrast diagnostic (`Rmem = 8'hFF`, `Smem = 8'h00` at `(-5, 7)` with 1-LSB perturbation at `(-8, -8)`) | **`16'hFF00`** (`65,280`) | **`8'hFB, 8'h07`** (`-5, +7`) | Verifies upper-bound 16-bit accumulation: 256 pixels $\times |255 - 0| = 65,280$ (`16'hFF00`) vs. `16'hFF01` (`65,281`) at `(-8, -8)`, confirming `16'hFF00 < 16'hFF01` selects `(-5, +7)`. |

---

## 4. Running Synopsys VCS Simulation and Capturing Waveforms in Verdi (`nWave`)

### Step 4.1 — Upload Files to the SFSU Server and Run VCS
1. Copy the RTL and testbench files to your server workspace:
   ```bash
   scp -r rtl tb scripts mahmoodi:~/engr852_motion_estimator/
   ```
2. Log into `mahmoodi` with X11 forwarding enabled:
   ```bash
   ssh -Y mahmoodi
   cd ~/engr852_motion_estimator
   source /apps/settings
   ```
3. Compile and run the 520 MHz simulations with Synopsys VCS:
   ```bash
   # 1. File-driven testbench (ref.txt / search.txt -> BestDist = 0000, motionX/Y = F8/F8)
   vcs -full64 -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_direct.v -o simv_direct
   ./simv_direct | tee logs/rtl_16bit_direct_520mhz.log

   # 2. Professor random +1 perturbation testbench (BestDist = 0100, motionX/Y = FB/07)
   vcs -full64 -debug_access+all rtl/16bit/top.v tb/16bit/top_tb.v -o simv_random
   ./simv_random | tee logs/rtl_16bit_random_520mhz.log

   # 3. 16-bit full-scale diagnostic testbench (BestDist = FF00, motionX/Y = FB/07)
   vcs -full64 -debug_access+all rtl/16bit/top.v tb/16bit/top_tb_16bit.v -o simv_diag
   ./simv_diag | tee logs/rtl_16bit_diag_520mhz.log
   ```

### Step 4.2 — Opening Synopsys Verdi (`nWave`) GUI and Inspecting Register Hex Values
1. Launch the Verdi waveform viewer on the generated `waves.fsdb`:
   ```bash
   verdi -ssf waves.fsdb &
   ```
2. **Where to Click in the Verdi nWave Window**:
   - Press **`g`** (or click **Signal -> Get Signals...** in the top menu bar).
   - In the signal hierarchy tree on the left, click `top_tb` -> `dut` (`u1`), select `clock`, `start`, `BestDist`, `motionX`, `motionY`, `AddressR`, `AddressS1`, `AddressS2`, `R`, `S1`, `S2`, and `u1/u2/count`, then click **Add** and **Close**.
   - To view the **full simulation overview** (`0 ns` to `7,920 ns`), press **`f`** (**View -> Zoom -> Zoom Full**).
   - To view **individual hexadecimal values inside each bus transition box** (matching the zoomed-in detail view), hold the **Left Mouse Button** and drag a zoom box across the final clock cycles (`7,895 ns` to `7,910 ns`, around `count = 13'h1006 .. 13'h100F`), or click **View -> Zoom -> Zoom In (`z`)** repeatedly until the hex strings (`100e`, `100f`, `ff00` / `0100` / `0000`, `fb`, `07`) appear inside the green waveform bars.

---

## 5. Running Synopsys Fusion Compiler (`fc_shell`), IC Validator (`icv`), and PrimeTime (`pt_shell`)

### Step 5.1 — 520 MHz Timing Constraints (`top_520mhz.sdc`)
Create `top_520mhz.sdc` with a `1.923 ns` clock period (`520.02 MHz`), `0.5 ns` input/output external delays, and `0.2 ns` clock uncertainty:
```tcl
create_clock -name clock -period 1.923 [get_ports clock]
set_input_delay  0.5 -clock clock [remove_from_collection [all_inputs] [get_ports clock]]
set_output_delay 0.5 -clock clock [all_outputs]
set_clock_uncertainty 0.2 [get_clocks clock]
```

### Step 5.2 — Run Synopsys Fusion Compiler (Synthesis, Floorplan, Placement, CTS, Route, SPEF, GDS)
Run the automated physical implementation script on `mahmoodi`:
```bash
fc_shell -f scripts/server/run_fc_16bit_520mhz.tcl | tee logs/fc_16bit_520mhz.log
```
What `run_fc_16bit_520mhz.tcl` executes step by step:
1. Reads the SAED14nm NDM reference library (`saed14rvt_frame_only.ndm`) and 3-corner parasitics (`max` = `125C`, `nominal` = `25C`, `min` = `-40C`).
2. Analyzes and elaborates `rtl/16bit/top.v` (synthesizing strictly standard cells for `top` with **0 synthesized SRAM/ROM macros**, since `RMEM` and `SMEM` are testbench modules).
3. Applies `top_520mhz.sdc` and runs `compile_fusion -to initial_opto`.
4. Initializes the `125.07 µm × 62.80 µm` core floorplan (`7,854.68 µm²` rectangular outline), places I/O pins (`place_pins -self`), and builds the `M7/M8` power/ground mesh (`compile_pg`).
5. Runs placement optimization (`compile_fusion -from final_place -to final_opto`), Clock Tree Synthesis (`clock_opt`), and detail routing (`route_auto` + `route_opt`).
6. Inserts standard-cell fillers (`create_stdcell_fillers`) and connects PG nets (`connect_pg_net`).
7. Exports post-layout `.v` netlist (`top.out.v`), 3-corner parasitics (`top.out.max.spef`, `top.out.nominal.spef`, `top.out.min.spef`), and merged 14nm OASIS/GDS stream (`top.gds`).

### Step 5.3 — Run Synopsys IC Validator (`icv`) Sign-Off DRC
```bash
icv -vue -i results/top.gds -c top -f GDSII \
    /apps/synopsys/SAED14_EDK/tech/icv_drc/saed14nm_1p9m_drc_rules.rs
```
Verify the sign-off summary in `top.LAYOUT_ERRORS`:
- **Result**: `0 / 242` rule violations (`DRC CLEAN`).

### Step 5.4 — Run Standalone 3-Corner Synopsys PrimeTime (`pt_shell`) Post-Layout STA
```bash
pt_shell -f scripts/server/run_pt_3corner_520mhz.tcl | tee logs/pt_3corner_520mhz.log
```
Verify setup and hold slack across all three corners (`FAST`, `TYPICAL`, `SLOW`):
- **8-Bit Baseline (`520 MHz`)**: Setup Slack = `+0.931 ns` (FAST), `+0.881 ns` (TYPICAL), `+0.822 ns` (SLOW); Hold Slack = `+0.011 ns` (FAST), `+0.015 ns` (TYPICAL), `+0.014 ns` (SLOW); WNS/TNS = `0.000 ns`.
- **16-Bit Datapath (`520 MHz`)**: Setup Slack = `+0.256 ns` (FAST), `+0.172 ns` (TYPICAL), `+0.082 ns` (SLOW); Hold Slack = `+0.011 ns` (FAST), `+0.016 ns` (TYPICAL), `+0.025 ns` (SLOW); WNS/TNS = `0.000 ns`.

---

## 6. Creating and Pushing to a New GitHub Repository from Scratch on a New MacBook Air

1. Create a new repository on [https://github.com/new](https://github.com/new) (for example, `motion-estimator-asic-lab-notebook-2026`), leaving "Add a README file" unchecked.
2. In macOS Terminal inside your project folder, initialize Git, commit all files, and push to `main`:
   ```bash
   cd ~/Developer/engr852-motion-estimator
   git init -b main
   git add .
   git commit -m "Complete 520 MHz 14nm Motion Estimator ASIC RTL, Physical Design, and Sign-Off Package"
   git branch -M main
   git remote add origin https://github.com/<GITHUB_USERNAME>/motion-estimator-asic-lab-notebook-2026.git
   git push -u origin main
   ```
