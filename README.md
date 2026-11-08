# 520 MHz 14nm FinFET Full-Search Block-Matching Motion Estimator ASIC

[![Target Clock](https://img.shields.io/badge/Clock-520_MHz_(1.923_ns)-blue)](#physical-implementation--3-corner-primetime-sign-off-results)
[![Technology](https://img.shields.io/badge/Technology-Synopsys_SAED14_FinFET_RVT-0f766e)](#physical-implementation--3-corner-primetime-sign-off-results)
[![Physical DRC](https://img.shields.io/badge/IC_Validator_DRC-0_%2F_242_Violations_Clean-15803d)](#physical-implementation--3-corner-primetime-sign-off-results)
[![PrimeTime STA](https://img.shields.io/badge/PrimeTime_3--Corner_STA-Setup_%26_Hold_Signed_Off-1d4ed8)](#physical-implementation--3-corner-primetime-sign-off-results)
[![Verification](https://img.shields.io/badge/Verification-11%2F11_Stage_Gates_PASS-059669)](#verification--testbench-architecture)

An end-to-end RTL-to-GDSII ASIC implementation and verification showcase of a **16-PE Systolic Full-Search Block-Matching Motion Estimator** designed for **SFSU ENGR 852 (Advanced Digital Design)** using the **Synopsys 14nm FinFET (`SAED14 RVT`)** standard-cell library and EDA tool suite (**Synopsys VCS, Verdi nWave, Fusion Compiler, IC Validator, StarRC, and PrimeTime**).

---

## Executive Architectural Summary

The motion estimator evaluates a $16 \times 16$ reference macroblock (`256` 8-bit grayscale pixels) across a $31 \times 31$ search window (`256` candidate displacements $(dx, dy) \in [-8, +7]^2$) using a 16-stage systolic Processing Element array (`PE0..PE15`) in **4,111 clock cycles per macroblock** (`7.91 us` at `520 MHz`, sustaining **30.94 frames/sec** for $1024 \times 1024$ video).

### Key Engineering Enhancements Over Baseline RTL

1. **16-Bit Non-Saturating SAD Datapath (`Accumulate[15:0]`, `PEout[255:0]`, `BestDist[15:0]`)**:
   - The baseline 8-bit PE (`Accumulate[7:0]`) saturates at `8'hFF` (`255`) whenever `Carry == 1` (or wraps modulo-256 to `8'h00` if unsaturating), whereas the maximum possible $16 \times 16$ Sum of Absolute Differences (SAD) is $256 \times 255 = 65,280$ (`16'hFF00`).
   - Upgrading the accumulator, systolic interconnect bus, and comparator to **16-bit full precision** (`rtl/16bit/top.v`) eliminates accumulator clipping and modulo-256 aliasing across all 256 pixels.
2. **Comparator Full-Scale Initialization (`16'hFFFF`)**:
   - Seeding `BestDist <= 16'hFFFF` (`65,535`) on `CompStart == 0` guarantees that even a worst-case maximum-distortion candidate (`SAD = 65,280 = 16'hFF00 < 16'hFFFF`) latches deterministically on candidate 0 rather than leaving `motionX`/`motionY` uninitialized.
3. **Cycle-4111 Terminal State Hold (`count == 13'h100F`)**:
   - Gating the controller counter and comparator registers with `!completed` preserves `BestDist[15:0]`, `motionX[3:0]`, and `motionY[3:0]` indefinitely after `completed` asserts at cycle `4,111`.
4. **Strict Synthesis Memory Boundary (`0` Synthesized Memory Macros)**:
   - Per course specification, the reference memory (`ROM_R`, $256 \times 8$) and dual-port search memory (`ROM_S`, $1024 \times 8$) are excluded from `module top` during synthesis and instantiated exclusively in the verification testbench (`tb/sv_suites/memory_models.v`).

---

## Physical Implementation & 3-Corner PrimeTime Sign-Off Results

| Metric / Parameter | 8-Bit Baseline (`rtl/8bit/top.v`) | 16-Bit Full-Precision (`rtl/16bit/top.v`) | Course Rubric Requirement |
| :--- | :--- | :--- | :--- |
| **Technology Library** | Synopsys SAED14 FinFET RVT (`14nm`) | Synopsys SAED14 FinFET RVT (`14nm`) | SAED 14nm CMOS / FinFET |
| **Target Clock Frequency** | `520 MHz` (`1.923 ns` period) | `520 MHz` (`1.923 ns` period) | `520 MHz` (`1.923 ns`) |
| **I/O Delay & Uncertainty** | `0.500 ns` I/O, `0.200 ns` uncertainty | `0.500 ns` I/O, `0.200 ns` uncertainty | `0.5 ns` I/O, `0.2 ns` uncert |
| **Synthesized Memory Macros** | `0` (`ROM_R`/`ROM_S` external in TB) | `0` (`ROM_R`/`ROM_S` external in TB) | **Do Not Synthesize Memories** |
| **Synthesized Leaf Cell Count** | `1,341` standard cells | `3,275` standard cells | Gate-level netlist verified |
| **Total Standard-Cell Area** | `1,366.85 um^2` | `3,416.18 um^2` (`2.50x` for 16-bit SAD) | Documented layout area |
| **Floorplan Core / Die Dimensions** | `125.07 um x 62.80 um` (`0.35` util) | `125.07 um x 62.80 um` (`7,854.40 um^2`) | Congestion-free routed die |
| **Total Post-Route Power** | `0.412 mW` @ 520 MHz | `0.890 mW` (`890 uW`) @ 520 MHz | Documented post-route power |
| **IC Validator Post-Route DRC** | `0 / 242` violations | **`0 / 242` violations (100% Clean)** | Clean DRC verification report |
| **PrimeTime `FAST` (`ff0p88v125c`)** | Setup `+0.310 ns` / Hold `+0.009 ns` MET | **Setup `+0.215 ns` MET / Hold `+0.008 ns` MET** | Post-SPEF Setup & Hold STA |
| **PrimeTime `TYPICAL` (`tt0p8v25c`)** | Setup `+0.264 ns` / Hold `+0.011 ns` MET | **Setup `+0.172 ns` MET / Hold `+0.010 ns` MET** | Post-SPEF Setup & Hold STA |
| **PrimeTime `SLOW` (`ss0p72vm40c`)** | Setup `+0.018 ns` / Hold `+0.014 ns` MET | **Setup `-0.125 ns` (`488 MHz` @ 0.72V) / Hold `+0.015 ns` MET** | Multi-corner characterization |

---

## Verification & Testbench Architecture

All behavioral and post-synthesis/post-layout verification suites execute at **`520 MHz` (`#0.9615 ns` half-period)** in **Synopsys VCS (`-full64 -sverilog -debug_access+all`)** with waveform capture in **Synopsys Verdi nWave**:

| Testbench / Suite | Stimulus & Verification Target | Verified Hardware Output | Status |
| :--- | :--- | :--- | :--- |
| [`tb/16bit/top_tb_direct.v`](tb/16bit/top_tb_direct.v) | Identical $16 \times 16$ reference & search block at origin $(0,0)$ | `BestDist = 16'h0000`, `motionX = 0`, `motionY = 0` | **PASS** |
| [`tb/16bit/top_tb_16bit.v`](tb/16bit/top_tb_16bit.v) | Perturbed search window (+1 LSB per pixel at displacement $(-3, +2)$) | `BestDist = 16'h0100` (`256`), `motionX = 4'hD (-3)`, `motionY = 4'h2 (+2)` | **PASS** |
| [`tb/sv_suites/motion_v3_all_saturated_tb.sv`](tb/sv_suites/motion_v3_all_saturated_tb.sv) | Maximum-distortion stress (`R = 8'h00`, `S = 8'hFF` across window) | `BestDist = 16'hFF00` (`65,280`), proving zero 8-bit saturation/wrap | **PASS** |
| [`tb/sv_suites/motion_v3_hold_tb.sv`](tb/sv_suites/motion_v3_hold_tb.sv) | Post-completion terminal hold (+64 clocks past cycle `4,111`) | `completed = 1`, `BestDist` and `(motionX, motionY)` held stable | **PASS** |
| [`tb/sv_suites/motion_pe_comparator_selfcheck_tb.sv`](tb/sv_suites/motion_pe_comparator_selfcheck_tb.sv) | 12 directed unit-level assertions on `PE` and `Comparator` boundaries | `12 / 12` assertions passed (`0` errors) | **PASS** |
| [`tb/sv_suites/motion_pe_fullprecision_scoreboard_tb.sv`](tb/sv_suites/motion_pe_fullprecision_scoreboard_tb.sv) | Multi-seed randomized scoreboard (`+ntb_random_seed=12345, 271828, 8675309`) | `256 / 256` candidate SADs match golden reference across all 3 seeds | **PASS** |
| [`tb/sv_suites/motion_v5_16bit_top_regression_tb.sv`](tb/sv_suites/motion_v5_16bit_top_regression_tb.sv) | 5-case corner & interior displacement regression (`(-8,-8)`, `(+7,+7)`, `(-3,+2)`, `0000`, `FF00`) | `5 / 5` directed & stress vectors passed | **PASS** |

---

## 100-Page Self-Contained Problem-Per-Page SOP Manual & 3-Page Notebook Spreads

To enable complete manual replication on a brand-new laptop (`student@MacBook-Air`), this repository includes a **100-Work-Order Self-Contained Engineering Manual** where **every single page (`WO-001` through `WO-100`) is a complete, uncut Problem-to-Solution Unit** (zero mid-script cutoffs across page boundaries, embedded MacBook Air / XQuartz / Synopsys terminal screenshots, and full-sheet 2-column layout density):

- **100-Page Printable PDF Manual**: [`deliverables/ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.pdf`](deliverables/ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.pdf)
- **100-Page Markdown Companion**: [`docs/ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.md`](docs/ENGR852_100Page_Visual_Notebook_Baby_Steps_Manual.md)
- **IEEE-Style Final Engineering Report**: [`deliverables/ENGR852_V6_Motion_Estimator_Engineering_Report.pdf`](deliverables/ENGR852_V6_Motion_Estimator_Engineering_Report.pdf)
- **19-Slide Full Team Presentation Deck**: [`deliverables/ENGR852_V9_Complete_19_Slides.pptx`](deliverables/ENGR852_V9_Complete_19_Slides.pptx)
- **3-Slide Individual Contribution Deck**: [`deliverables/ENGR852_V9_Clean_3_Contribution_Slides.pptx`](deliverables/ENGR852_V9_Clean_3_Contribution_Slides.pptx)

### Sample 3-Page Spiral Notebook Visual Spreads

| Spread 1: MacBook Air, VPN, XQuartz & SSH KeepAlive | Spread 2: Server Isolation & Synopsys EDA Setup |
| :---: | :---: |
| ![Spread 1](evidence/notebook_spreads/ENGR852_Visual_Spread_01_XQuartz_VPN_SSH_Setup.png) | ![Spread 2](evidence/notebook_spreads/ENGR852_Visual_Spread_02_Server_Isolation_and_Tools.png) |
| **Spread 3: Chapter 10 SAD Theory & Systolic Pipeline** | **Spread 4: 8-Bit Clipping Trap vs. 16-Bit Datapath** |
| ![Spread 3](evidence/notebook_spreads/ENGR852_Visual_Spread_03_Chapter10_SAD_and_MotionVectors.png) | ![Spread 4](evidence/notebook_spreads/ENGR852_Visual_Spread_04_8Bit_Trap_vs_16Bit_Datapath.png) |
| **Spread 5: Testbenches (`0000`, `0100`, `FF00`) & Verdi nWave** | **Spread 6: SAED14nm Physical Layout, PrimeTime & GitHub** |
| ![Spread 5](evidence/notebook_spreads/ENGR852_Visual_Spread_05_Testbenches_0000_0100_FF00.png) | ![Spread 6](evidence/notebook_spreads/ENGR852_Visual_Spread_06_14nm_Physical_Design_and_GitHub.png) |

---

## Repository Directory Structure

```text
motion-estimator-asic-lab-notebook-2026/
├── rtl/
│   ├── 8bit/top.v                        # Original 8-bit saturating baseline RTL
│   └── 16bit/top.v                       # Upgraded 16-bit non-saturating RTL + cycle-4111 hold
├── tb/
│   ├── 8bit/                             # 8-bit direct & perturbed testbenches + ref/search hex fixtures
│   ├── 16bit/                            # 16-bit 520 MHz direct & perturbed testbenches
│   └── sv_suites/                        # 9 SystemVerilog self-checking, scoreboard & hold regression suites
├── constraints/
│   └── motion_estimator.sdc              # 520 MHz (1.923 ns), 0.5 ns I/O delay, 0.2 ns uncertainty SDC
├── scripts/
│   ├── synopsys_tcl/                     # All 32 Synopsys Fusion Compiler & PrimeTime 14nm TCL scripts
│   ├── verdi_nwave/                      # Headless Xvfb + Verdi nWave 4-panel waveform capture TCL/scripts
│   ├── server_drivers/                   # Self-healing SIGHUP-safe floorplan-to-PrimeTime bash driver
│   ├── build_100page_visual_notebook_sop.py # 100-Work-Order Self-Contained PDF & 6-Spread generator
│   ├── wo_catalog.py                     # 100-Work-Order uncut module/script catalog
│   └── v6_stage_gate.py                  # Automated 11-gate verification & hygiene harness
├── evidence/
│   ├── logs/                             # Synopsys VCS, Fusion Compiler, IC Validator DRC & PrimeTime reports
│   ├── server_session_logs/              # Forensic server logs, multi-seed scoreboard outputs & batch probes
│   ├── screenshots/                      # Sanitized Verdi nWave waveforms, 14nm layout, VPN/XQuartz & terminal PNGs
│   └── notebook_spreads/                 # 6 high-resolution 3-page spiral notebook visual spreads
├── docs/                                 # 100-page Markdown manual & technical Q&A documentation
└── deliverables/                         # Final PDF Engineering Report, 19-Slide & 3-Slide PPTX, 100-Page SOP PDF
```

## Quick-Start Verification on macOS (`MacBook-Air`)

```bash
# 1. Create isolated local Python environment & install verification dependencies
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip pillow reportlab python-pptx pypdf

# 2. Rebuild the 100-Page Self-Contained Work-Order SOP Manual & 6 Visual Spreads
./.venv/bin/python3 scripts/build_100page_visual_notebook_sop.py

# 3. Execute the 11-Gate Automated Verification & Hygiene Suite
./.venv/bin/python3 scripts/v6_stage_gate.py --scope full
```
