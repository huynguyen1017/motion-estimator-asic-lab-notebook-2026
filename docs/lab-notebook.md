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
- **Source Files:** [`rtl/top.v`](../rtl/top.v), [`tb/motion_verification_520mhz_tb.v`](../tb/motion_verification_520mhz_tb.v), [`tb/top_tb.v`](../tb/top_tb.v), [`tb/top_tb_direct.v`](../tb/top_tb_direct.v), [`tb/ref.txt`](../tb/ref.txt), [`tb/search.txt`](../tb/search.txt), [`constraints/top_520mhz.sdc`](../constraints/top_520mhz.sdc)

### 1. 520 MHz Directed Fixture, Perturbed Non-Zero SAD & Corner-Case Simulation
Executed commands:

```sh
iverilog -g2012 -o motion_verification_520mhz.vvp rtl/top.v tb/motion_verification_520mhz_tb.v
vvp motion_verification_520mhz.vvp | tee evidence/logs/motion_verification_520mhz.log
```

Captured simulation output ([`evidence/logs/motion_verification_520mhz.log`](../evidence/logs/motion_verification_520mhz.log)):

```text
VCD info: dumpfile motion_verification_520mhz.vcd opened for output.
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
yosys -p "read_verilog rtl/top.v; hierarchy -check -top top; synth -top top; stat" > evidence/logs/motion_synthesis_stat.log
```

Key findings from [`evidence/logs/motion_synthesis_stat.log`](../evidence/logs/motion_synthesis_stat.log):
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


---

## UPDATE-003 — Remote EDA Server Environment & Synopsys Setup Audit (`2026-11-04 17:06:06 PST`)

### 1. Metadata
- **Server Timestamp:** `2026-11-04 17:06:06 PST (-0800)`
- **Target Host:** `mahmoodi.rcc.at.sfsu.edu` (Rocky Linux 8.10)
- **Working Directory:** `/home/<student-id>`
- **X11 Display Forwarding:** `DISPLAY=localhost:12.0` (`70`-byte `.Xauthority` verified)
- **Global Synopsys Setup Script:** `/packages/synopsys/setup/synopsys_setup.tcl` (`-rwxr-xr-x`, `431` bytes, `Nov 6 2024`)
- **Captured Transcript:** [`evidence/transcripts/03-server-environment-audit-1706pst.txt`](../evidence/transcripts/03-server-environment-audit-1706pst.txt)

### 2. Diagnostic Summary

| Check | Command | Captured Output | Engineering Finding |
| :--- | :--- | :--- | :--- |
| **Working Directory & Display** | `pwd; ls; echo "DISPLAY=$DISPLAY"` | `/home/<student-id>` / `DISPLAY=localhost:12.0` | Confirms clean home directory and active SSH X11 forwarding tunnel. |
| **Server Clock** | `date '+%Y-%m-%d %H:%M:%S %Z (%z)'` | `2026-11-04 17:06:06 PST (-0800)` | Synchronizes server session logs with local engineering notebook timestamps. |
| **Hostname** | `hostname` | `mahmoodi.rcc.at.sfsu.edu` | Confirms execution on the SFSU School of Engineering EDA server. |
| **Synopsys Setup Script** | `ls -l /packages/synopsys/setup/synopsys_setup.tcl` | `-rwxr-xr-x. 1 root root 431 Nov 6 2024 /packages/synopsys/setup/synopsys_setup.tcl` | Confirms the global C-shell Synopsys environment script is present and executable. |
| **Default Login Shell PATH** | Tool check across `vcs`, `verdi`, `dc_shell`, `fc_shell`, `pt_shell`, `xterm` | `/usr/bin/xterm` on default PATH; Synopsys tools not on default `bash` PATH | Default login shell is `bash`; running `csh` followed by `source /packages/synopsys/setup/synopsys_setup.tcl` activates `vcs`, `verdi`, `dc_shell`, `fc_shell`, and `pt_shell`. |
| **Home Directory Dotfiles** | `ls -la "$HOME"` | `.bash_logout`, `.bash_profile`, `.bashrc`, `.config`, `.dbus`, `.esd_auth`, `.kshrc`, `.mozilla`, `.Xauthority` (`70` bytes) | Confirms `.Xauthority` cookie was created at `16:41` upon `ssh -X` login. |


---

## UPDATE-004 — Shell Verification (`bash` vs. `csh`/`tcsh`) & Synopsys Environment Script Inspection (`2026-11-04 17:11:12 PST`)

### 1. Metadata
- **Server Timestamp:** `2026-11-04 17:11:12 PST (-0800)`
- **Target Host:** `mahmoodi.rcc.at.sfsu.edu` (Rocky Linux 8.10)
- **Active Process Shell (`ps -p $$ -o comm=`):** `bash`
- **Available C-Shells:** `/usr/bin/tcsh`, `/usr/bin/csh`
- **Captured Transcript:** [`evidence/transcripts/04-shell-and-setup-inspection-1711pst.txt`](../evidence/transcripts/04-shell-and-setup-inspection-1711pst.txt)

### 2. Captured Contents of `/packages/synopsys/setup/synopsys_setup.tcl`

```tcsh
source /packages/synopsys/setup/synthesis.csh
source /packages/synopsys/setup/vcs_2024.csh
source /packages/synopsys/setup/primetime.csh
source /packages/synopsys/setup/icc2_2021.csh
source /packages/synopsys/setup/verdi_2024.csh
setenv VCS_HOME /packages/synopsys/vcs/W-2024.09-1/
setenv VERDI_HOME /packages/synopsys/verdi/W-2024.09-1/
set path = ( $VERDI_HOME/bin $path ) ; rehash
set path = ( $VCS_HOME/bin $path ) ; rehash
```

### 3. Engineering Findings
1. **Shell Compatibility (`bash` vs. `csh`/`tcsh`):** The login session runs `bash` (`ps -p $$ -o comm=`), whereas `/packages/synopsys/setup/synopsys_setup.tcl` uses C-shell syntax (`setenv`, `set path = (...)`, `rehash`) and sources five tool-specific C-shell setup scripts (`synthesis.csh`, `vcs_2024.csh`, `primetime.csh`, `icc2_2021.csh`, `verdi_2024.csh`).
2. **Confirmed Tool Releases:** `VCS_HOME` and `VERDI_HOME` point to Synopsys `W-2024.09-1` (`/packages/synopsys/vcs/W-2024.09-1/` and `/packages/synopsys/verdi/W-2024.09-1/`).
3. **Required Invocation Sequence:** Invoking `csh` (or `tcsh`) before running `source /packages/synopsys/setup/synopsys_setup.tcl` cleanly loads the entire Synopsys 2024/2021 toolchain.
