# Final Table Set

## Environment

| Item | Value |
|---|---|
| SSD | KIOXIA KXG80ZNV1T02 REV2, firmware APGA4102 |
| Interface / filesystem | NVMe / NTFS |
| OS | Windows 11 Enterprise build 26200 |
| FIO | 3.43, windowsaio |
| Python | Anaconda Python 3.13.9 |
| Target | One 8 GiB regular file, basename-only FIO target |

## QD1 baseline

| Workload | Median IOPS | Median MiB/s | Mean clat us | p99 us |
|---|---:|---:|---:|---:|
| randread_4k_qd1 | 15,769 | 61.6 | 56.9 | 87.6 |
| randwrite_4k_qd1 | 37,681 | 147.2 | 20.0 | 45.8 |
| seqread_128k_qd1 | 7,162 | 895.2 | 131.1 | 203.8 |
| seqwrite_128k_qd1 | 17,384 | 2,172.9 | 47.8 | 73.2 |

## Block-size/pattern headlines

| Metric | Configuration | Result |
|---|---|---:|
| Highest QD1 IOPS | sequential write, 4k | 43,003 IOPS |
| Highest QD1 throughput | sequential write, 256k | 3,122.0 MiB/s |

## Read/write mix

| Read/write | Median IOPS | Median MiB/s | Weighted mean clat us |
|---|---:|---:|---:|
| 100/0 | 89,340 | 349.0 | 79.7 |
| 70/30 | 124,004 | 484.4 | 52.3 |
| 50/50 | 126,274 | 493.3 | 48.4 |
| 0/100 | 147,770 | 577.2 | 32.9 |

## Queue-depth and knee

| Item | Result |
|---|---:|
| Knee | QD16 |
| QD16 4 KiB random-read IOPS | 156,847 |
| QD16 mean clat | 85.4 us |
| QD16 inferred L | 13.40 |
| Maximum observed 4 KiB IOPS | 171,868 at QD32 |
| Maximum observed 128 KiB sequential read | 5,158.6 MiB/s at QD32 |

## Tail latency

| QD | p50 us | p95 us | p99 us | p99.9 us | Median completed reads |
|---:|---:|---:|---:|---:|---:|
| 8 | 81.4 | 107.0 | 138.2 | 187.4 | 2,697,465 |
| 16 | 88.6 | 136.2 | 175.1 | 242.7 | 4,155,216 |

## Working set

| Active range | Median IOPS | p99 us |
|---:|---:|---:|
| 256 MiB | 143,114 | 171.0 |
| 8 GiB | 141,571 | 173.1 |

## Device state

| Pass | Size | Median/aggregate throughput | Time-series evidence |
|---|---:|---:|---|
| Sequential write, 1 MiB, QD8 | 8 GiB | 5,142.5 MiB/s | One 1-second interval; transition unresolved |

## Buffered pitfall

| Setup | Median MiB/s | Mean clat us |
|---|---:|---:|
| Direct | 630.5 | 182.4 |
| Buffered first | 566.4 | 212.9 |
| Buffered immediate second | 7,420.3 | 3.0 |

## Hypotheses and limitations

See [hypothesis outcomes](../../docs/hypothesis_outcomes.md) and the final report's [limitations](../../README.md#19-limitations). Detailed canonical summaries remain in `data/parsed`.
