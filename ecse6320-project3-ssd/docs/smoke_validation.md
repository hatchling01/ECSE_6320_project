# Phase 1 Minimal Smoke Validation

Status: **passed** on 2026-10-23 local time (artifact timestamp `20261024T010431375251Z` UTC).

This was a functionality check only and is permanently classified **NOT FOR PERFORMANCE ANALYSIS**.

## Corrected invocation

- Validated canonical target: `C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project3-ssd\benchmark_data\fio_smoke_test.bin`
- FIO working directory: `C:\Users\CHOUDN3\Downloads\EcSE_4320\ecse6320-project3-ssd\benchmark_data`
- FIO filename argument: `--filename=fio_smoke_test.bin`
- Executable: `C:\Program Files\fio\fio.exe` (FIO 3.43)
- Config: `configs\fio\smoke.fio`
- Engine/direct: `windowsaio`, `direct=1`
- Workload: `randrw`, 50% read / 50% write
- Block size: 4 KiB
- Concurrency: `iodepth=1`, `numjobs=1`
- File/range: 16 MiB
- Total smoke I/O: 4 MiB
- Output: JSON

Exact argv is preserved in the corresponding metadata file. The runner changed the child working directory to `benchmark_data` and passed only the leaf filename, avoiding FIO's colon-separated multi-file parsing for drive-qualified Windows paths.

## Actual validation

The corrected raw JSON reports FIO 3.43, `windowsaio`, `direct=1`, `iodepth=1`, `numjobs=1`, and the reconstructed canonical target inside `benchmark_data`. It reports 2,031,616 read bytes and 2,162,688 write bytes, totaling exactly 4,194,304 bytes. Both directions include completion-latency percentile keys for p50, p95, p99, and p99.9.

The Python parser completed successfully and emitted two tidy CSV rows, one each for read and write. The disposable target was canonicalized again and deleted after validation; `benchmark_data` contains only `.gitkeep` afterward.

## Audit separation

The earlier invalid smoke artifacts remain under the timestamped smoke directories and are documented in `docs/anomalies.md`. Neither the invalid nor corrected smoke output may be merged into production results or used for performance claims.

