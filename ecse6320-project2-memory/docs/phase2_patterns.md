# Phase 2 — pattern, stride, and read/write mix

All 60 required trials used a 1 GiB allocation, CPU 0, deterministic indices/schedules, 8,388,608 useful 64-byte operations, and three repetitions. Initialization and random-index shuffling were outside the timed region. Every affinity and write-validation flag passed. The maximum configuration CV was 18.1%, below the 20% bounded-rerun threshold.

## Pure directions: median useful GiB/s

| Pattern | Direction | 64 B | 256 B | 1024 B |
|---|---|---:|---:|---:|
| Sequential | Read | 29.234 | 11.566 | 10.331 |
| Sequential | Write | 18.745 | 10.601 | 7.629 |
| Random | Read | 2.641 | 2.661 | 2.636 |
| Random | Write | 5.121 | 5.096 | 4.766 |

Sequential 64-byte read was 11.1× the corresponding random result and fell 64.7% by 1024-byte stride. Sequential write fell 59.3%. The random results are already dominated by address unpredictability, so additional stride had much less effect. These results support the locality/prefetch hypothesis and show the expected direction asymmetry. They do not measure memory-controller traffic.

## Mixes at 64 B: median useful GiB/s

| Pattern | 100% read | 70/30 | 50/50 | 100% write |
|---|---:|---:|---:|---:|
| Sequential | 31.954 | 28.477 | 25.450 | 18.840 |
| Random | 2.677 | 3.213 | 3.267 | 5.244 |

The deterministic schedules produced exact requested logical operation ratios. Sequential mixes declined as stores increased; randomized stores were faster than randomized reads for this kernel and host. Write allocate/writeback and physical traffic are not observed, so these are useful-operation rates only.

Raw data are in `data/raw/phase2`; canonical parsed data and summary statistics are in `data/parsed`; figures are `phase2_stride_bandwidth.png` and `phase2_mix_bandwidth.png`.
