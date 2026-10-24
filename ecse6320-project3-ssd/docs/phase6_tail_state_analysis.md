# Phase 6: Tail Latency, Working Set, and Device State

## Tail latency

QD8 represents mid-concurrency and QD16 is the Phase 5 knee. For 4 KiB random read, median p50/p95/p99/p99.9 at QD8 were 81.4/107.0/138.2/187.4 us; at QD16 they were 88.6/136.2/175.1/242.7 us. Each read run completed well over one million I/Os, so p99.9 represents thousands of tail observations. The bounded mixed runs completed about 262 thousand total I/Os each, still providing hundreds of observations in each direction near the 0.1% tail.

## Working set

At fixed 4 KiB random read and QD16, the 256 MiB and 8 GiB active ranges produced 143,114 and 141,571 median IOPS, respectively. These are host-visible range effects only; an active byte range does not identify physical NAND placement or an internal cache boundary.

## Device-state observation

One bounded direct sequential-write pass covered exactly 8 GiB with 1 MiB blocks at QD8. It completed at 5,142.5 MiB/s. FIO's 1-second logger emitted only 1 averaged interval because the pass completed in roughly 1.59 s. Consequently, an early/middle/late comparison is unresolved rather than evidence of stability. No clear burst-to-steady-state transition was observed within the safe 8 GiB test window. Temperature telemetry was unavailable, so thermal causality cannot be evaluated.
