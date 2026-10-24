# Phase 5 pitfall

| Same kernel and 1 GiB useful work | Median useful GiB/s | CV |
|---|---:|---:|
| 16 MiB repeatedly reused: cache-reuse bandwidth | 35.262 | 0.67% |
| 1 GiB single span: DRAM-sensitive useful bandwidth | 31.369 | 19.29% |

The cache-reuse result is 12.4% higher and must not be called physical DRAM bandwidth.
