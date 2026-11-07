# ENGR 852 Motion Estimator — Synthesis & Timing Constraints (SDC)
# Target Top Module: top (from Course Project/Motion Estimator RTL and Testbench-1.zip)
# Rubric Spec: 520 MHz (1.923 ns), 0.5 ns I/O delay, 0.2 ns clock uncertainty
# External Memories: ROM_R (256x8) and ROM_S (1024x8) excluded from synthesis top

create_clock -name clock -period 1.923 [get_ports clock]
set_clock_uncertainty 0.2 [get_clocks clock]

# Input ports (25 bits excluding clock): start[1], R[7:0], S1[7:0], S2[7:0]
set_input_delay 0.5 -clock clock [get_ports {start R* S1* S2*}]

# Output ports (53 bits): BestDist[15:0], motionX[3:0], motionY[3:0],
# AddressR[7:0], AddressS1[9:0], AddressS2[9:0], completed[1]
set_output_delay 0.5 -clock clock [all_outputs]
