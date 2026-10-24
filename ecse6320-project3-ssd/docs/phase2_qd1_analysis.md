# Phase 2: QD=1 Baseline Analysis

All four required configurations completed three validated repetitions against the regular 8 GiB production file using FIO 3.43, `windowsaio`, `direct=1`, `iodepth=1`, and one job. Initialization is recorded separately and excluded from performance results.

## Headline results

| Workload | Median IOPS | Median MiB/s | Mean clat (µs) | p50 (µs) | p95 (µs) | p99 (µs) | p99.9 (µs) | IO count | CV IOPS |
|---|---|---|---|---|---|---|---|---|---|
| randread_4k_qd1 | 15,769 | 61.6 | 56.9 | 60.2 | 72.2 | 87.6 | 129.5 | 236,551 | 5.1% |
| randwrite_4k_qd1 | 37,681 | 147.2 | 20.0 | 18.0 | 31.4 | 45.8 | 77.3 | 262,144 | 4.7% |
| seqread_128k_qd1 | 7,162 | 895.2 | 131.1 | 124.4 | 175.1 | 203.8 | 244.7 | 107,430 | 3.2% |
| seqwrite_128k_qd1 | 17,384 | 2,172.9 | 47.8 | 44.3 | 55.6 | 73.2 | 230.4 | 32,768 | 0.7% |

The identity check `IOPS × block size ≈ bytes/s` passed every run within 0.2%, confirming consistent unit extraction. Random 4 KiB results are IOPS-oriented, whereas sequential 128 KiB results deliver much higher bandwidth per operation. Read/write asymmetry is reported as observed behavior only; this phase does not attribute it to SLC caching, garbage collection, or temperature.

Median p99.9 tail sample counts were approximately 237 (random read), 262 (random write), 107 (sequential read), and 33 (sequential write). The sequential-write p99.9 estimate therefore has the strongest finite-sample caveat.

QD=1 Little's-Law sanity values (`IOPS × mean clat seconds`) are stored per run. They are broadly near, but not required to equal, one because completion latency excludes all host-side timing components and configured queue depth is not identical to inferred average occupancy.

Variability is preserved in the run and summary CSV files. No configuration exceeded the 20% IOPS CV rerun threshold.
