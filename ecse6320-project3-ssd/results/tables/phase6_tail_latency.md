# Phase 6 Tail Latency

| Workload | QD | Direction | p50 us | p95 us | p99 us | p99.9 us | Median I/Os |
|---|---:|---|---:|---:|---:|---:|---:|
| 4K random 70/30 | 8 | read | 75.3 | 116.2 | 179.2 | 280.6 | 183,413 |
| 4K random 70/30 | 8 | write | 18.6 | 34.0 | 50.9 | 96.8 | 78,731 |
| 4K random 70/30 | 16 | read | 89.6 | 148.5 | 230.4 | 354.3 | 183,413 |
| 4K random 70/30 | 16 | write | 31.4 | 61.7 | 78.3 | 146.4 | 78,731 |
| 4K random read | 8 | read | 81.4 | 107.0 | 138.2 | 187.4 | 2,697,465 |
| 4K random read | 16 | read | 88.6 | 136.2 | 175.1 | 242.7 | 4,155,216 |
