# UPDATE-009 — SHA-256 verified after original RTL upload

**Evidence date:** November 4, 2026 (individual execution time not captured in the supplied university Linux terminal excerpt).

## Remote integrity verification

The user ran the following commands from an authenticated SFSU Linux shell:

```text
$ cd ~/ENGR852_Project
$ sha256sum "Motion Estimator RTL and Testbench-1.zip"
b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6  Motion Estimator RTL and Testbench-1.zip
```

The remote SHA-256 matches the previously measured local iMac ZIP SHA-256, **b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6**.

**Result: PASS — Original professor-provided ZIP transferred intact.** This validates the archive's bytes, not the RTL's functionality.

## Next milestone — inspect without extracting

```tcsh
unzip -l "Motion Estimator RTL and Testbench-1.zip"
```

The original archive contains **ten regular files** (Makefile, top.v, top_tb.v, top_tb_direct.v, ref.txt, ref_binary.txt, ref_hex.txt, search.txt, search_binary.txt, search_hex.txt) under one folder. Check this listing on the university server before extracting into a newly named clean directory, leaving the previously manually created `00_original_baseline` untouched.

**Not yet performed:** Extraction on university server, source-file checksums, VCS compilation, simulation, Verdi waveform review, physical design or timing sign-off.
