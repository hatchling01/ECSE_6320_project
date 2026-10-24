# Phase 3 — loaded latency, knee, and Little's Law

One 512 MiB randomized dependent probe ran on CPU 0 while 0/1/2/4/8/12/15 background workers used distinct 128 MiB randomized regions on CPUs 2–30. Each of 21 trials used 1 s warmup, 5 s measurement, and verified affinity. Maximum allocation was 2.375 GiB. The native and Python gates both required at least 16 GiB available before allocations over 1 GiB; the minimum observed pre-run availability was 17.39 GiB. No paging symptom or allocation failure appeared.

| Workers | Median useful GiB/s | Probe ns/load | L inferred (ops) |
|---:|---:|---:|---:|
| 0 | 0.000 | 123.868 | 0.000 |
| 1 | 3.713 | 128.160 | 8.000 |
| 2 | 6.976 | 131.504 | 15.437 |
| 4 | 13.339 | 141.114 | 31.510 |
| 8 | 23.227 | 162.702 | 63.528 |
| 12 | 31.738 | 180.164 | 96.075 |
| 15 | 35.199 | 193.454 | 113.693 |

## Knee decision

The preregistered numerical rule requires the earliest next substantial worker increase to add <10% aggregate bandwidth while increasing probe latency >20%, with the following point confirming diminishing returns. No tested adjacent step satisfied both conditions: even 12→15 workers added about 10.9% bandwidth while latency rose only 7.4%. Therefore: **No clear knee resolved within the tested safe intensity range.** The highest point is not relabeled as a knee.

## Little's Law

`lambda` is background useful 64-byte operations/s, `W` is dependent-probe seconds/load, and `L=lambda×W`. The estimate rose from 8.0 at one worker to 113.7 at 15. It is a comparative host-visible queueing-style concurrency estimate; it is not literal DRAM-controller occupancy, exact outstanding CPU misses, or a hardware queue counter.

Worker throughput CVs were ≤6.51% and probe-latency CVs ≤6.19%, below the rerun threshold. Raw data, canonical statistics and all three requested curve views are retained under the phase directories.
