# UPDATE-012 — Fusion Compiler executable validation and X11 forwarding blocker

**Evidence:** Direct readback from the existing SFSU SSH Terminal on November 4, 2026. All work was performed in the user's home directory or by reading instructor-provided, system-wide files; no course setup files were edited.

## Tool paths and versions

- `vcs` resolved to `/packages/synopsys/vcs/W-2024.09-1//bin/vcs`.
- `verdi` resolved to `/packages/synopsys/verdi/W-2024.09-1//bin/verdi`.
- `pt_shell` resolved to `/packages/synopsys/primetime/S-2021.06-SP4/bin/pt_shell`.
- `fc_shell` did not appear on the interactive shell's PATH, despite two installations existing:
  - `/packages/synopsys/fc/W-2024.09-SP3-1/bin/fc_shell`
  - `/packages/synopsys/fc/X-2025.06-SP2a/bin/fc_shell`

The **older W-2024.09** launcher reported it could not find `linux64/nwtn/bin/dgcom_exec`, so that launcher was not used.

The newer **X-2025.06-SP2a** launcher returned:

```text
fc_shell version X-2025.06-SP2
build date: Oct 15, 2025
```

## Batch startup verified

From the user's independent `~/ENGR852_Project/04_fc_startup_probe_20261104` directory, a Tcl probe was executed with the documented batch flags:

```sh
/packages/synopsys/fc/X-2025.06-SP2a/bin/fc_shell -batch -file probe.tcl
```

Contents of `probe.tcl`:

```tcl
puts "ENGR852_FC_STARTUP_TCL_OK"
exit
```

Observed result:

```text
FC_BATCH_PROBE_EXIT=0
ENGR852_FC_STARTUP_TCL_OK
Fusion Compiler (TM), Version X-2025.06-SP2 for linux64
```

The initial attempt using `-no_gui` returned an unsupported-option error; that diagnostic is preserved locally as `fc_invalid_no_gui_flag.log`. The corrected `-batch -file` invocation succeeded.

**Scope:** This verifies that Fusion Compiler starts and executes Tcl. It does not establish successful technology mapping, a working design license for synthesis, PDK completeness, area/power/timing metrics, physical routing, DRC, or PrimeTime sign-off.

## 14 nm collateral seen in professor tutorial

The university tutorial at `/packages/synopsys/setup/Fusion_Compiler_setup/` includes `common/liberty`, `common/ndm`, `common/tlup`, `common/nxtgrd`, `common/tf`, `common/gds`, `common/runsets`, and scripts referencing SAED 14 nm design-rule and layout files. These are existence/filename observations only; the complete configuration has not yet been validated for the motion-estimator design.

## X11 forwarding status

- On the **iMac**, XQuartz was running and `xdpyinfo -display :0` reported an X.Org display successfully.
- Inside the **university SSH session**, `DISPLAY=localhost:11.0` was set, but `xdpyinfo -display "$DISPLAY"` returned `unable to open display`.
- Therefore, remote GUI forwarding is currently **not working**, even though remote `verdi` is present on PATH. No Verdi GUI screenshots are claimed.

**Next actions:** Validate the supplied Fusion Compiler technology setup with a non-destructive synthesis smoke test; repair or renew the SSH X11 display before trying Verdi GUI screenshots. Continue to preserve all working originals and report measured results only.
