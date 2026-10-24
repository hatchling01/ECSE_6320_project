# Phase 3: Block Size and Access Pattern

The complete required matrix contains 24 configurations (six block sizes × two patterns × two directions), each with three validated QD=1 repetitions. Reads used 2 s ramp plus 8 s measured time; writes were bounded to 256 MiB per repetition.

The highest median IOPS in this QD=1 sweep was 43,003 for sequential write at 4k. The highest median throughput was 3,122.0 MiB/s for sequential write at 256k. These are QD=1 observations, not claims of device or interface maxima.

Across the matrix, small blocks emphasize IOPS and larger blocks convert fewer operations into higher bandwidth. Completion latency generally increases with transfer size. Sequential/random and read/write differences are treated as host-visible measurements; no internal NAND/controller cause is asserted.

The maximum IOPS coefficient of variation was 9.7%. All original runs are retained. Extreme percentiles are not used as a primary Phase 3 conclusion because bounded large-block writes can provide relatively few p99.9 tail observations.
