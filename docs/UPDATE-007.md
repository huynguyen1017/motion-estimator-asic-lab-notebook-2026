# UPDATE-007 — Course Tutorial Inventory and Source Provenance Check

Evidence date: November 4, 2026. Based on a redacted, user-supplied university-server transcript and direct inspection of the professor-provided ZIP on the iMac. Individual command timestamps were not shown.

## Verified university tutorial directories

- `/packages/synopsys/setup/vcs_setup/`: the 1,788,658-byte **Tutorial on Synopsys VCS and VERDI.pdf**, `src/` examples (including `ME/`) and `vcs/` tutorial files.
- `/packages/synopsys/setup/Fusion_Compiler_setup/`: the 2,843,259-byte **Tutorial on Synopsys Fusion Compiler.pdf**, example Makefile, `setup/`, `scripts/`, `common/`, `reports/`, `results/`, and `logs/`.
- The physical implementation tutorial includes `initial_syn.tcl`, `auto_floorplan.tcl`, `place_opt.tcl`, `clock_opt.tcl`, `route_opt.tcl`, `signoff.tcl`, and `sta_post_layout.tcl`, among other scripts.
- Directory availability does not establish tool licensing, available technology libraries, or successful physical implementation.

## Source ZIP independently verified on iMac

- `Course Project/Motion Estimator RTL and Testbench-1.zip`: 8,307 bytes.
- SHA-256: `b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6`.
- Contains `top.v`, `top_tb.v`, `top_tb_direct.v`, `Makefile`, `ref.txt`, `ref_binary.txt`, `ref_hex.txt`, `search.txt`, `search_binary.txt`, and `search_hex.txt`, under a common directory.

## Unsuccessful baseline reconstruction

The university terminal showed two `scp` attempts from the wrong (remote Linux) host. Several subsequent long Python commands attempted to reconstruct memory files and RTL manually, but reported errors including `Unmatched '\''`, `SyntaxError: unexpected character after line continuation character`, and `SyntaxError: invalid character in identifier`. A final here-document returned to the prompt without showing its anticipated success banner; any outputs created by these commands require independent checking. **No reconstructed files are accepted as the professor's original baseline** until checked against the actual ZIP contents and hashes.

## Next work

A new **local iMac Terminal** window was opened and activated, leaving the university SSH session intact. The course archive must be copied from the local iMac to `~/ENGR852_Project/` using `scp` in the local shell. Then verify `sha256sum` and `unzip -l` on the server before extracting into a new named folder. Do not overwrite the existing `00_original_baseline` directory; it may contain partial reconstruction artifacts.

Status: **Transfer and VCS baseline simulation pending**.
