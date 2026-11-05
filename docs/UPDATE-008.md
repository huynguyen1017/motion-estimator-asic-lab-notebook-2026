# UPDATE-008 — Original professor-provided RTL archive transferred

**Date:** 2026-11-04 (local terminal output; exact command timestamp not present).  
**Evidence:** Copy/paste of the iMac Terminal `scp` session. Personal university account identifier redacted.

## Verified transfer report

The transfer command was executed in the **local macOS Terminal**, rather than from inside the SSH session:

```sh
scp "$HOME/Developer/coursework/sfsu/2026-fall/sfsu-engr852-2026-fall/Course Project/Motion Estimator RTL and Testbench-1.zip" <student-id>@mahmoodi.rcc.at.sfsu.edu:/home/<student-id>/ENGR852_Project/
```

The SSH client prompted for authentication and returned:

```text
Motion Estimator RTL and Testbench-1.zip  100% 8307  109.9KB/s  00:00
```

**Result:** SCP reported 100% completion for the original 8,307-byte professor-provided archive. This was an actual file-transfer attempt from the iMac to the university server, unlike the earlier unsuccessful attempts.

## Source provenance

Original local file verified by checksum before transfer:

```text
SHA-256: b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6
Size: 8307 bytes
```

The university server has **not yet returned its own SHA-256 calculation**. The next milestone is a byte-for-byte comparison with `sha256sum`, followed by `unzip -l` and extraction in an independently named source directory. Previously attempted manual reconstructions in `00_original_baseline` must be preserved and not treated as the original ZIP contents.

## Next hands-on step

In the **existing university SSH session**:

```tcsh
cd ~/ENGR852_Project
sha256sum "Motion Estimator RTL and Testbench-1.zip"
```

Accept the transfer as source-integrity verified only if the remote digest exactly matches the local checksum above.

**Progress boundaries:** No successful VCS run, functional verification, Verdi waveform, Fusion Compiler physical implementation, or timing sign-off is claimed by this file-transfer milestone.
