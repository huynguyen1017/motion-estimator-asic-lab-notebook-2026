# UPDATE-006 — Server environment and source-transfer diagnosis

Evidence: User-supplied SFSU SSH transcript, November 4, 2026. Personal university ID and network-origin address are omitted from this public record.

## Confirmed environment
- Reconnected to `mahmoodi.rcc.at.sfsu.edu` using `ssh -X`.
- The `/packages/synopsys/setup/synopsys_setup.tcl` script is written in C-shell syntax. Sourcing it from Bash produced `setenv: command not found` and parser errors.
- Running `tcsh` before sourcing the approved script produced setup banners for Synthesis, VCS, PrimeTime, IC Compiler II, and Verdi.
- `which vcs` resolved `/packages/synopsys/vcs/W-2024.09-1//bin/vcs`. Tool licensing and successful compilation remain untested.
- The university server contains `/packages/synopsys/setup/vcs_setup` and `/packages/synopsys/setup/Fusion_Compiler_setup`.
- The working directory `~/ENGR852_Project` exists but `pwd; ls -la` showed only `.` and `..`.

## Root cause of two failed transfers

Both attempted `scp` commands were executed at the `[student-id]@mahmoodi` prompt. A path beginning with `~/Downloads` or `$HOME/Developer` therefore referred to the **remote Linux server**, not the author's iMac. The server returned `No such file or directory`; no archive was transferred.

## Source verified independently on iMac
- Source archive: `Course Project/Motion Estimator RTL and Testbench-1.zip`.
- Size: **8,307 bytes**.
- SHA-256: `b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6`.
- The ZIP is in the ENGR852 coursework directory, **not** `~/Downloads`.

## Next operation — not yet verified
Open a **new local macOS Terminal** window showing the iMac prompt and execute the secure copy from local to `~/ENGR852_Project/`, using the exact path and authenticating at the terminal password prompt. Next, check the server file size and SHA-256 digest before unzipping.

No professor-provided RTL or teammate files were changed during diagnosis. This entry records an unsuccessful transfer and must not be represented as a successful source upload.
