# Next checks — pending execution

These commands were proposed for the next session. No results have been supplied for them yet. Run them only in the authenticated university shell, and retain the actual output.

```sh
getent passwd "$USER" | cut -d: -f7
ls -l /packages/synopsys/setup/synopsys_setup.tcl
for tool in vcs verdi dc_shell fc_shell pt_shell xterm; do
    command -v "$tool" || echo "$tool: not currently on PATH"
done
ls -la "$HOME"
```

Then test graphical forwarding:

```sh
xterm &
```

Record whether a window actually appears. A missing tool on PATH is not proof it is uninstalled; inspect the approved course setup before changing configuration.

After these checks: load the appropriate university environment, identify the exact team source revision, create a separate working directory, and reproduce one simulation. Preserve failed runs as well as successful runs. Record commands, tool versions, inputs, outputs and interpretation for each step.
