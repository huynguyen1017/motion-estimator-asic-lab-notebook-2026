# UPDATE-002 — Shell and course setup inspection
First check: 2026-11-04 17:11:12 PST (-0800).
Documented: 2026-11-05T01:12:06Z.
Supplied terminal output; account prompt omitted and blank lines normalized.

$ date '+%Y-%m-%d %H:%M:%S %Z (%z)'
2026-11-04 17:11:12 PST (-0800)
$ ps -p $$ -o comm=
bash
$ cat /packages/synopsys/setup/synopsys_setup.tcl
source /packages/synopsys/setup/synthesis.csh
source /packages/synopsys/setup/vcs_2024.csh
source /packages/synopsys/setup/primetime.csh
source /packages/synopsys/setup/icc2_2021.csh
source /packages/synopsys/setup/verdi_2024.csh
setenv VCS_HOME /packages/synopsys/vcs/W-2024.09-1/
setenv VERDI_HOME /packages/synopsys/verdi/W-2024.09-1/
set path = ( $VERDI_HOME/bin $path ) ; rehash
set path = ( $VCS_HOME/bin $path ) ; rehash

Finding: the current shell is Bash. Despite its .tcl suffix, the setup file contains C-shell syntax. It must not be sourced directly in Bash. Only reading the file is evidenced; no setup execution or failure is claimed.
The setup references synthesis, VCS, PrimeTime, ICC2 and Verdi scripts. These paths are configuration references, not proof that binaries, licenses or sessions are operational. In particular, this file points to ICC2, not evidence of a Fusion Compiler installation.
Next: check command -v tcsh and command -v csh, select an available compatible shell, then load the approved course setup and verify its outcome. No permanent login-shell change is needed.

