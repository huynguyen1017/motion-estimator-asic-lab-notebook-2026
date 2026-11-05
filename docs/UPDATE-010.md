# UPDATE-010 — Original RTL ZIP inventory confirmed on SFSU server

**Evidence:** Command output supplied by the project author on November 4, 2026. Individual execution timestamp was not captured. The personal university account identifier is excluded.

## Command executed

```tcsh
unzip -l "Motion Estimator RTL and Testbench-1.zip"
```

Result: the server successfully listed **11 archive entries: one containing folder and ten regular files**, totaling **37,988 uncompressed bytes**.

| File within `Motion Estimator RTL and Testbench/` | Bytes |
| --- | ---: |
| `Makefile` | 1,803 |
| `ref.txt` | 1,024 |
| `ref_binary.txt` | 2,560 |
| `ref_hex.txt` | 1,024 |
| `search.txt` | 3,072 |
| `search_binary.txt` | 9,216 |
| `search_hex.txt` | 3,072 |
| `top.v` | 8,356 |
| `top_tb.v` | 4,718 |
| `top_tb_direct.v` | 3,143 |

The ZIP file had already passed a remote-to-local SHA-256 comparison in [UPDATE-009](UPDATE-009.md): `b799f2bbb08014f0e66e74ac87ebde2fcb01e20c2825d8c4eaf3c8c32f32ceb6`.

**Interpretation:** Archive inventory and source integrity are verified. This does not verify RTL behavior or show that the archive has been extracted on the university server.

## Next action — extract without overwriting earlier work

Run the following only inside `~/ENGR852_Project` on the university server:

```tcsh
unzip -n "Motion Estimator RTL and Testbench-1.zip" -d 00_professor_zip_verified_20261104
```

`-n` instructs unzip **never to overwrite existing files**. The extraction destination is deliberately distinct from the earlier possibly reconstructed `00_original_baseline` directory. Check extracted files and compare hashes with the source before modifying or compiling them.

**Pending:** Clean extraction, baseline compile and simulation using university VCS, independent functional verification, Verdi waveforms, ASIC implementation, and setup/hold timing sign-off.
