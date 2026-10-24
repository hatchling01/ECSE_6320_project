# QD=1 Baseline Summary

Medians across three repetitions. Throughput is binary MiB/s; latency is completion latency.

| Workload | Median IOPS | Median MiB/s | Mean clat (µs) | p50 (µs) | p95 (µs) | p99 (µs) | p99.9 (µs) | IO count | CV IOPS |
|---|---|---|---|---|---|---|---|---|---|
| randread_4k_qd1 | 15,769 | 61.6 | 56.9 | 60.2 | 72.2 | 87.6 | 129.5 | 236,551 | 5.1% |
| randwrite_4k_qd1 | 37,681 | 147.2 | 20.0 | 18.0 | 31.4 | 45.8 | 77.3 | 262,144 | 4.7% |
| seqread_128k_qd1 | 7,162 | 895.2 | 131.1 | 124.4 | 175.1 | 203.8 | 244.7 | 107,430 | 3.2% |
| seqwrite_128k_qd1 | 17,384 | 2,172.9 | 47.8 | 44.3 | 55.6 | 73.2 | 230.4 | 32,768 | 0.7% |
