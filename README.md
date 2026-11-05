# Motion Estimator ASIC Lab Notebook

**Huy Nguyen · ENGR 852, Advanced Digital Design · Fall 2026**

An evidence-based engineering notebook documenting my progression through a motion-estimation ASIC course project: remote laboratory access, RTL simulation, waveform analysis, synthesis, physical implementation and timing verification.

**Current milestone: university server access established.** The evidence published here supports environment-access progress only. Motion-estimator simulation, synthesis and physical sign-off are not yet demonstrated by my recorded runs.

## Verified progress

| Step | Evidence | Result and scope |
| --- | --- | --- |
| Open university VPN | [Initial screen](evidence/screenshots/01-vpn-disconnected.png) | Portal configured; initially disconnected |
| Connect VPN | [Connected screen](evidence/screenshots/02-vpn-connected.png) | GlobalProtect displayed Connected |
| Open XQuartz terminal | [xterm screen](evidence/screenshots/03-local-xterm.png) | Local terminal opened on iMac |
| Log in using SSH with X11 forwarding requested | [Login transcript](evidence/transcripts/01-ssh-login.txt) | University shell prompt reached |
| Check remote location and display | [Status transcript](evidence/transcripts/02-session-status.txt) | Home directory confirmed; DISPLAY=localhost:12.0 |

A populated DISPLAY variable is evidence of an assigned forwarding address, not proof that a graphical application has opened successfully. The home-directory `ls` produced no visible entries; hidden contents have not yet been checked.

## Engineering objective

The course project uses a 16 × 16 reference block and a 31 × 31 search window. Its required implementation checks include a 520 MHz clock target (rounded period 1.923 ns), 0.5 ns input/output delays, 0.2 ns clock uncertainty, and exclusion of reference/search memories from the synthesis top. Required deliverables include RTL/testbench evidence, mapped netlist, timing and power reports, layout area, design-rule checking, extracted parasitics, and post-layout PrimeTime setup/hold verification.

These are **requirements**, not measured achievements. Requirements are transcribed from the supplied ENGR 852 course project rubric, pages 1–2. Course PDFs, licensed libraries, credentials and teammate source files are not redistributed here.

## Notebook

- [Completed steps and observations](docs/lab-notebook.md)
- [Next checks — not yet executed](docs/next-steps.md)
- [Evidence provenance and limitations](docs/evidence-policy.md)
- [Screenshot and transcript checksums](evidence/manifest.json)

## Scope of my contribution

This repository documents steps I performed and outputs I supplied while learning the engineering workflow. Team results can guide expected behavior, but are not presented as my own execution evidence. Design-source attribution and applicable licenses will be recorded before any reference RTL is published.

## Evidence preview

### University VPN connected
![GlobalProtect displaying Connected](evidence/screenshots/02-vpn-connected.png)

### Local XQuartz terminal
![Local xterm ready for commands](evidence/screenshots/03-local-xterm.png)

## Status of remaining stages

| Stage | Status |
| --- | --- |
| Open a remote graphical window | Pending |
| Verify university tool environment | Pending |
| Obtain and identify exact team RTL/testbench version | Pending |
| Create an independent working directory | Pending |
| Execute VCS simulation and inspect Verdi waveforms | Pending |
| Synthesis and physical implementation | Pending |
| Post-layout PrimeTime setup/hold verification | Pending |

Record date: 4 November 2026. Evidence is a point-in-time record, not a live connection monitor.
