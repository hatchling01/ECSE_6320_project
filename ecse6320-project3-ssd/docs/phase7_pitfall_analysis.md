# Phase 7: Misleading Benchmark Setup

The experiment held the target, 512 MiB active range, sequential access, 128 KiB block size, QD1, one job, and three-repetition policy fixed. Only cache bypass changed: A used `direct=1`; B and C used `direct=0`, with C immediately following B in every repetition. No cache flush, elevated privilege, or system setting change was used.

Median throughput was 630.5 MiB/s direct, 566.4 MiB/s on the first buffered pass, and 7,420.3 MiB/s on the immediate second buffered pass. The second buffered pass differed from the first by +1210.1%. These results are host-stack observations: buffered reads may include filesystem/page-cache behavior, read-ahead, and memory copies, so they cannot be interpreted as an isolated SSD measurement even if the second-pass speedup is modest. This is why all primary project results use `direct=1`.

Additional reproducibility pitfalls encountered or controlled in this project include Windows FIO's colon parsing of absolute drive-qualified filenames, configured QD versus inferred occupancy, misleadingly short burst tests, inadequate tail sample counts, uncertain device state, and ordinary run-to-run noise. The failed Phase 0 filename attempt remains preserved and excluded from performance analysis.
