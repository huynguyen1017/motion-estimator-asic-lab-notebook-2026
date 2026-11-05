# UPDATE-004 — Live terminal readback and TCSH environment confirmation

**Evidence capture:** 2026-11-04 17:26:03 PST (-0800), iMac. Individual command execution timestamps were not captured.

## Reproduced observations

The existing SSH Terminal application's scrollback was read directly without changing the current shell. The relevant redacted excerpt is stored in [the terminal transcript](../evidence/transcripts/04-tcsh-and-synopsys-startup.txt).

- `command -v tcsh` returned `/usr/bin/tcsh`, and `command -v csh` returned `/usr/bin/csh`.
- `ps -p $$ -o comm=` in an earlier nested shell returned `tcsh`.
- `source /packages/synopsys/setup/synopsys_setup.tcl` was already invoked in that C-shell session. The console printed startup messages naming Synthesis O-2018.06-SP4, VCS W-2024.09-1, PrimeTime S-2021.06-SP4, IC Compiler II S-2021.06-SP5-1, and Verdi W-2024.09-1.
- A subsequent `tcsh` command created another nested C-shell, and `echo $version` reported `tcsh 6.20.00 (Astron) 2016-11-24 (x86_64-unknown-linux)`.
- The iMac's X11 window inventory contains two local windows titled `xterm` and `ENGR 852 - SFSU Linux Server`.

## Scope and limitations

This is an inspection of terminal scrollback, not a new invocation of the university tools. Startup messages do not independently verify tool executables, licensing, remote X11 display, 14 nm libraries, simulation, timing closure, or physical implementation. The content is a redacted excerpt; private identifiers and unrelated terminal activity are excluded.

## Next guided check

In the current university `tcsh` session, type `which vcs` and inspect the returned path or missing-command message. Then test the remaining tools individually; test `xterm &` only after recording the tool-path check.
