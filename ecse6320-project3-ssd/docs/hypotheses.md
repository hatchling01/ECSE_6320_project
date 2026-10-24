# Pre-experiment Hypotheses

Recorded 2026-10-23 before any Project 3 performance measurement. These statements must not be rewritten later to match observations. Refinements require dated amendments.

1. **QD=1 latency:** Small random operations should show low throughput but expose device/service latency more directly than high-QD runs.
2. **Queue scaling:** Increasing queue depth should initially raise IOPS/throughput by improving device utilization.
3. **Saturation knee:** Beyond some concurrency level, throughput gains should diminish while latency continues to increase.
4. **Block size:** Small blocks should favor IOPS-oriented characterization, while larger sequential blocks should move toward bandwidth-oriented behavior.
5. **Sequential versus random:** Sequential large-block access is expected to reach higher throughput than small-block random access.
6. **Read versus write:** Read and write behavior are expected to differ because flash writes involve controller/cache/media-management work not required identically for reads.
7. **Mixed workloads:** 70/30 and 50/50 workloads are expected to produce different throughput and tail-latency behavior from pure reads or writes.
8. **Tail latency:** p99/p99.9 latency should increase more sharply than median latency near or beyond the saturation knee.
9. **Device state:** Short burst results may exceed longer sustained-write behavior if caching/device-state effects are significant.
10. **Misleading buffering:** Buffered I/O may produce results that reflect host page-cache behavior rather than storage-device behavior.
11. **Working set/range:** Changing the active range may alter measured performance if host/device caching or internal device state matters.
12. **Little's Law:** Throughput and average latency should show broadly queueing-consistent relationships, but configured FIO queue depth need not equal Little's-Law-inferred occupancy exactly.

## Amendments

None.

