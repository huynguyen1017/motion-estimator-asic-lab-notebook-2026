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

## Step 1a — Enter the compatible shell (verified)

```bash
tcsh
```

The terminal showed `tcsh 6.20.00` from `echo $version`. A prior `tcsh` session had already invoked the course setup file and printed startup banners. The user then entered another `tcsh` subshell, which is now active. Full redacted excerpt: [UPDATE-004](UPDATE-004.md).

## Step 2 — Check whether VCS resolves in the current shell (pending)

In the **current university SSH Terminal window**, type **only this command**:

```tcsh
which vcs
```

Press Enter and inspect the output. If a full executable path appears, report it. If `vcs: Command not found.` or no usable path appears, report that instead. The setup messages alone do not prove tool availability or licenses.

## Step 3 — Graphical forwarding check (pending)

After the executable paths are checked, run:

```tcsh
xterm &
```

Observe whether a **new remote** Xterm window appears on the Mac. The two existing local XQuartz windows do not establish remote forwarding success.

## Step 4 — Reproduce the team RTL run (pending on university server)

The user's remote home directory initially contained only dotfiles. No Verilog sources were yet observed there. Transfer a **copy** of the exact project revision to a dedicated server directory before running VCS. Do not run the local Icarus commands from the empty server home directory. The existing local Icarus/Yosys results and three technical slides are separately documented in [lab-notebook.md](lab-notebook.md).

## Record and publication rules

Capture command text, tool version, current directory, timestamps, stdout/stderr, source-file checksum, waveform or report paths, and clear pass/fail interpretation. Redact student identifiers and credentials before public upload. Preserve the team source and previous results. A 520 MHz simulation clock is not evidence of achieved post-layout timing.
