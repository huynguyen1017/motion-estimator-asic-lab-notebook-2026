# University server — next verified hand-on steps

Last verified terminal checks: 2026-11-04 17:11:12 PST; see [UPDATE-001](UPDATE-001.md), [UPDATE-002](UPDATE-002.md), and [server diagnostics](../evidence/transcripts/03-environment-diagnostics.txt).

## Current status

SFSU GlobalProtect connected, SSH authenticated to `mahmoodi.rcc.at.sfsu.edu`, and `DISPLAY=localhost:12.0` assigned. The user's command `ps -p $$ -o comm=` returned `bash`. The course setup file `/packages/synopsys/setup/synopsys_setup.tcl` references C-shell scripts and uses `source`, `setenv`, and `rehash`; it is **not a Bash script**. The absence of `vcs`, `verdi`, `dc_shell`, `fc_shell`, and `pt_shell` from the unconfigured PATH does not prove the programs are unavailable.

## Step 1 — Check for a compatible shell (verified)

In the **existing university Linux shell**, type the following command exactly, then press Enter:

```bash
command -v tcsh; command -v csh
```

**Observed output (user-supplied):** `/usr/bin/tcsh` and `/usr/bin/csh` both returned; the interpreters are available. The command's execution timestamp was not captured. Do not run `source /packages/synopsys/setup/synopsys_setup.tcl` from Bash.

## Step 1a — Enter the compatible shell (pending)

```bash
tcsh
```

Press Enter. This starts an interactive C-shell inside the existing SSH session; it does not permanently change your login shell. Then verify the shell before sourcing the approved course setup.

## Step 2 — Check graphical forwarding (pending, after Step 1)

```bash
xterm &
```

A new graphical terminal must actually appear on the Mac. The existence of `DISPLAY` alone is not proof that X11 applications work.

## Step 3 — Select and load the university tool setup (pending)

After confirming a compatible C shell exists, inspect the university's approved startup guidance and load its setup in that shell. Log all stdout/stderr. Confirm individual binaries with `command -v vcs`, `command -v verdi`, and the available synthesis/timing tools. The existing setup references ICC2; do **not** assume Fusion Compiler is installed merely because it is required by the course workflow.

## Step 4 — Reproduce the team RTL run (pending on university server)

The user's remote home directory initially contained only dotfiles. No Verilog sources were yet observed there. Transfer a **copy** of the exact project revision to a dedicated server directory before running VCS. Do not run the local Icarus commands from the empty server home directory. The existing local Icarus/Yosys results and three technical slides are separately documented in [lab-notebook.md](lab-notebook.md).

## Record and publication rules

Capture command text, tool version, current directory, timestamps, stdout/stderr, source-file checksum, waveform or report paths, and clear pass/fail interpretation. Redact student identifiers and credentials before public upload. Preserve the team source and previous results. A 520 MHz simulation clock is not evidence of achieved post-layout timing.
