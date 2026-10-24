# Phase 5: Queue Depth, Parallelism, and Saturation Knee

The primary staged sweep tested 4 KiB random reads through QD64. QD128 and QD256 were not run because scaling had already ended: QD16 to QD32 added 9.6% median IOPS while mean completion latency rose 49.2%, and QD64 did not improve the median.

The numerical knee rule, defined before final selection, is the earliest measured QD for which the next doubling adds less than 10% median IOPS while median mean completion latency rises at least 20%. It selects **QD16**, at 156,847 IOPS and 85.4 us. QD1-QD8 are underutilized/scaling; QD16 is the knee; QD32-QD64 are diminishing-return/post-knee points.

The highest observed median 4 KiB result across the Phase 5 read, mixed, and bounded-write configurations was **171,868 IOPS** (4K random read, QD32). The highest observed median 128 KiB sequential-read throughput was **5,158.6 MiB/s** at QD32. These are maxima within the tested regular-file Windows stack, not raw-device specifications.

Little's Law was calculated per run as `L_inferred = IOPS x mean completion latency in seconds`. It follows the configured-QD trend but is not forced to equal `iodepth`: configured depth is a submission limit, while the estimate uses completed I/O rate and FIO completion latency and can differ due to host scheduling, batching, ramp/runtime boundaries, and time outside the measured completion-latency interval.

The mixed 70/30 and bounded write subset provide direction comparisons without a broad write sweep. All configurations have three repetitions, all actual JSON targets resolved to the single regular file, and no upper-QD extension was needed.
