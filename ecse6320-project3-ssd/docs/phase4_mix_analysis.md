# Phase 4: Read/Write Mix Sweep

The fixed workload is 4 KiB random I/O at `iodepth=8`, one job, `windowsaio`, and `direct=1`. This choice represents a common small-block workload while introducing enough concurrency for mixed-I/O interaction without conflating the result with the later saturation sweep.

| Read/write mix | Median total IOPS | Median MiB/s | Weighted mean clat (µs) | IOPS CV |
|---|---:|---:|---:|---:|
| 100/0 | 89,340 | 349.0 | 79.7 | 5.0% |
| 70/30 | 124,004 | 484.4 | 52.3 | 6.3% |
| 50/50 | 126,274 | 493.3 | 48.4 | 3.2% |
| 0/100 | 147,770 | 577.2 | 32.9 | 1.1% |

Mixed workloads show host-visible read/write asymmetry and latency interaction rather than a linear interpolation of pure endpoints. Read and write percentile series are kept separate because FIO reports direction-specific latency distributions; the weighted mean combines directions by completed I/O count.

All three repetitions per mix are preserved. p99.9 is retained in parsed data, with interpretation conditioned on each direction's completion count.
