# Engineering Lab Notebook — 520 MHz Motion Estimator ASIC

**Author:** Huy Nguyen  
**Course:** ENGR 852 — Advanced Digital Design (San Francisco State University, Fall 2026)  
**Repository:** https://github.com/huynguyen1017/motion-estimator-asic-lab-notebook-2026

---

## UPDATE-001 — University EDA Server Access & X11 Display Forwarding

- **Documentation Timestamp:** `2026-11-04 16:58:00 PST` (`2026-11-05T00:58:00Z`)
- **Event Timestamp:** Individual terminal command timestamps were not captured in the prompt; session verified on `2026-11-04`.
- **Target Host:** `mahmoodi.rcc.at.sfsu.edu` via SFSU GlobalProtect VPN (`gp-students.sfsu.edu`)

### 1. VPN Authentication & Connection
GlobalProtect was configured with the student portal (`gp-students.sfsu.edu`) and transitioned from `Not Connected` to `Connected (Best Available Gateway)`.

- **Evidence:** [`evidence/screenshots/01-vpn-disconnected.png`](../evidence/screenshots/01-vpn-disconnected.png), [`evidence/screenshots/02-vpn-connected.png`](../evidence/screenshots/02-vpn-connected.png)

### 2. Local X11 Environment (`XQuartz xterm`)
XQuartz was launched on macOS (`huynguyen@iMac ~ %`) to provide a local X11 display server for remote GUI forwarding (`Verdi` and `Fusion Compiler`).

- **Evidence:** [`evidence/screenshots/03-local-xterm.png`](../evidence/screenshots/03-local-xterm.png)

### 3. Authenticated SSH Session with X11 Forwarding
Executed from the local terminal (student ID redacted as `<student-id>`):

```sh
ssh -X <student-id>@mahmoodi.rcc.at.sfsu.edu
```

Recorded terminal output ([`evidence/transcripts/01-ssh-login.txt`](../evidence/transcripts/01-ssh-login.txt)):

```text
Last login: Sat Oct 24 20:22:42 on ttys014
huynguyen@iMac ~ % ssh -X <student-id>@mahmoodi.rcc.at.sfsu.edu
The authenticity of host 'mahmoodi.rcc.at.sfsu.edu (130.212.15.54)' can't be established.
ED25519 key fingerprint is: SHA256:cCDUO4TpOgwYrKC25XEUUIPssDJx45DW12xBHLf+OiM
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'mahmoodi.rcc.at.sfsu.edu' (ED25519) to the list of known hosts.
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
<student-id>@mahmoodi.rcc.at.sfsu.edu's password:
Activate the web console with: systemctl enable --now cockpit.socket
/usr/bin/xauth: file /home/<student-id>/.Xauthority does not exist
[<student-id>@mahmoodi ~]$
```

### 4. Remote Working Directory & X11 Display Verification
Executed on `mahmoodi.rcc.at.sfsu.edu` ([`evidence/transcripts/02-session-status.txt`](../evidence/transcripts/02-session-status.txt)):

```text
[<student-id>@mahmoodi ~]$ pwd; ls; echo "DISPLAY=$DISPLAY"
/home/<student-id>
DISPLAY=localhost:12.0
[<student-id>@mahmoodi ~]$
```

---

## UPDATE-002 — 520 MHz RTL Verification, Pipeline Schedule Analysis, Gate-Level Synthesis Audit & Technical Slides

- **Execution Timestamp:** `2026-11-04 16:23:55 PST` to `2026-11-04 16:33:14 PST` (`2026-11-05T00:23:55Z` to `2026-11-05T00:33:14Z`)
- **Documentation Timestamp:** `2026-11-04 17:06:00 PST` (`2026-11-05T01:06:00Z`)
- **Tools Used (Local Workstation):** `Icarus Verilog 13.0` (`/opt/homebrew/bin/iverilog`, `/opt/homebrew/bin/vvp`), `Yosys 0.70` (`/opt/homebrew/bin/yosys`)
- **Source Files:** [`rtl/top.v`](../rtl/top.v), [`tb/huy_verification_520mhz_tb.v`](../tb/huy_verification_520mhz_tb.v), [`tb/top_tb.v`](../tb/top_tb.v), [`tb/top_tb_direct.v`](../tb/top_tb_direct.v), [`tb/ref.txt`](../tb/ref.txt), [`tb/search.txt`](../tb/search.txt), [`constraints/top_520mhz.sdc`](../constraints/top_520mhz.sdc)

### 1. 520 MHz Directed Fixture, Perturbed Non-Zero SAD & Corner-Case Simulation
Executed commands:

```sh
iverilog -g2012 -o huy_verification_520mhz.vvp rtl/top.v tb/huy_verification_520mhz_tb.v
vvp huy_verification_520mhz.vvp | tee evidence/logs/huy_verification_520mhz.log
```

Captured simulation output ([`evidence/logs/huy_verification_520mhz.log`](../evidence/logs/huy_verification_520mhz.log)):

```text
VCD info: dumpfile huy_verification_520mhz.vcd opened for output.
=== TEST 1: Direct Fixture (ref.txt & search.txt) at 520 MHz ===
  [T1] count= 256 t=493.2695 ns | PEready=0001 newDist_comp=ff BestDist=ff Vec=(8,8) out=(x,x) newBest=0
  ...
  [T1] count= 270 t=520.1915 ns | PEready=4000 newDist_comp=ff BestDist=ff Vec=(6,8) out=(x,x) newBest=0
  [T1] count= 271 t=522.1145 ns | PEready=8000 newDist_comp=00 BestDist=ff Vec=(7,8) out=(x,x) newBest=1
  [T1 newBest] count= 271 t=522.1145 ns -> newDist=00 at VectorX=7 VectorY=8
  [T1] count= 272 t=524.0375 ns | PEready=0000 newDist_comp=ff BestDist=00 Vec=(8,8) out=(7,8) newBest=0
  [T1 RESULT] BestDist=00 (0), motionX=7 (7), motionY=8 (-8), elapsed_complete=7905.4530 ns

=== TEST 2: Perturbed Imperfect Match (SAD=3) at (-2, -3) ===
  [T2 newBest] count=1542 t=2965.2660 ns -> newDist=03 (3) at VectorX=e VectorY=d
  [T2 RESULT] BestDist=03 (3), motionX=e (-2), motionY=d (-3), Expected=(-2, -3), elapsed=7905.4530 ns

=== TEST 3: Upper Boundary Candidate (+7, +7) at count=4111 ===
  [T3 newBest] count=4111 t=7905.4530 ns -> newDist=00 (0) at VectorX=7 VectorY=7 completed=1
  [T3 RESULT] BestDist=00 (0), motionX=7 (7), motionY=7 (7), Expected=(7, 7)
```

### 2. Gate-Level Synthesis Hierarchy & Memory-Boundary Audit (`module top`)
Executed command:

```sh
yosys -p "read_verilog rtl/top.v; hierarchy -check -top top; synth -top top; stat" > evidence/logs/huy_synthesis_stat.log
```

Key findings from [`evidence/logs/huy_synthesis_stat.log`](../evidence/logs/huy_synthesis_stat.log):
- **External Memory Exclusion Confirmed:** `0` memories and `0` memory bits inside `module top` (`ROM_R` `256×8` and `ROM_S` `1024×8` reside in the testbench, connected via `12` top-level ports / `71` port bits).
- **Submodule Cell & Register Breakdown (`3,254` total cells, `277` flip-flops):**
  - `PE` (`×15`): `172` cells each (`2,580` cells total), `16` DFFs each (`Accumulate[7:0]` + `Rpipe[7:0]` = `240` DFFs).
  - `PEend` (`×1`): `164` cells, `8` DFFs (`Accumulate[7:0]` only, omitting `Rpipe`).
  - `PEtotal` combined: `2,744` cells (`84.3%` of total logic), `248` DFFs.
  - `Comparator` (`×1`): `353` cells (`10.8%`), `16` DFFs (`BestDist[7:0]`, `motionX[3:0]`, `motionY[3:0]`).
  - `control` (`×1`): `157` cells (`4.8%`), `13` DFFs (`count[12:0]`).

### 3. Technical Presentation Slides Created
- **Slide 14:** [`evidence/slides/slide14-direct-perturbed-verification.png`](../evidence/slides/slide14-direct-perturbed-verification.png)
- **Slide 15:** [`evidence/slides/slide15-pipeline-schedule-timing.png`](../evidence/slides/slide15-pipeline-schedule-timing.png)
- **Slide 16:** [`evidence/slides/slide16-synthesis-hierarchy-sdc.png`](../evidence/slides/slide16-synthesis-hierarchy-sdc.png)
