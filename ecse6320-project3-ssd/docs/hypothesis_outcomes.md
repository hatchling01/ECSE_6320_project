# Final Hypothesis Outcomes

The original wording remains unchanged in `docs/hypotheses.md`.

| # | Outcome | Evidence |
|---:|---|---|
| 1 | Supported | QD1 exposed 56.9 us mean clat for 4 KiB random read while throughput was 61.6 MiB/s. |
| 2 | Supported | 4 KiB random-read IOPS increased from 19,801 at QD1 to 156,847 at QD16. |
| 3 | Supported | QD16-to-QD32 gained only 9.6% IOPS while latency rose 49.2%. |
| 4 | Supported | Larger blocks traded IOPS for bandwidth; 256 KiB sequential write reached 3,122.0 MiB/s at QD1. |
| 5 | Supported | Sequential large-block bandwidth substantially exceeded small-block random bandwidth. |
| 6 | Supported | Read/write endpoints differed across QD1, mix, and concurrency results; no internal cause is asserted. |
| 7 | Supported | 100/0, 70/30, 50/50, and 0/100 produced distinct IOPS and direction-specific latency distributions. |
| 8 | Supported | Read p50 rose from 81.4 to 88.6 us from QD8 to QD16, while p99.9 rose from 187.4 to 242.7 us. |
| 9 | Not resolved | The safe 8 GiB pass completed in 1.59 s and yielded one 1-second log interval. |
| 10 | Supported | The immediate buffered second pass reached 7,420.3 MiB/s, far above direct I/O. |
| 11 | Partially supported | Range affected results slightly (143,114 versus 141,571 IOPS), but the effect was small. |
| 12 | Supported | Inferred L tracked QD but differed from configured depth, including 13.40 at configured QD16. |
