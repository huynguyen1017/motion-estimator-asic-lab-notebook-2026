# Live Practice Telemetry (`manual-practice-macbook-air`)

- **Latest Step Executed**: `step07_three_testbenches`
- **Timestamp**: `2026-11-08 18:51:28 PST`
- **Host / Account**: `926784856@mahmoodi.rcc.at.sfsu.edu`
- **Working Directory**: `/home/926784856/motion-estimator-asic-lab-notebook-2026`
- **Command Executed**:
```bash
mkdir -p ~/engr852_practice/03_vcs_520mhz && cp -f ~/ENGR852_Project/22_v9_clean_verdi_waveforms/{top.v,tb_fig7_8_orig8bit.sv,tb_fig9_16bit_sat.sv,tb_fig10_16bit_zero.sv} ~/engr852_practice/03_vcs_520mhz/ && cd ~/engr852_practice/03_vcs_520mhz && vcs -full64 -sverilog top.v tb_fig10_16bit_zero.sv -o simv_zero && ./simv_zero | grep -E 'BestDist|PASS|motion' && vcs -full64 -sverilog top.v tb_fig9_16bit_sat.sv -o simv_sat && ./simv_sat | grep -E 'BestDist|PASS|motion'
```
- **Exit Code**: `1`
- **Terminal Log**: [`practice_from_scratch/logs/step07_three_testbenches.log`](logs/step07_three_testbenches.log)
- **Auto-Captured Terminal Screenshot**:

![step07_three_testbenches](screenshots/step07_three_testbenches_terminal.png)
