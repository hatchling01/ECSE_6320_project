# Phase 7 Direct vs Buffered Reads

| Setup | direct | Median MiB/s | Mean clat us | p99 us | Throughput CV |
|---|---:|---:|---:|---:|---:|
| Direct I/O | 1 | 630.5 | 182.4 | 272.4 | 4.3% |
| Buffered first | 0 | 566.4 | 212.9 | 321.5 | 0.6% |
| Buffered immediate second | 0 | 7,420.3 | 3.0 | 9.8 | 6.0% |
