# Hypotheses recorded before the compact experiment suite

1. Dependent random pointer-chase latency should increase as the footprint leaves
   L1 and cluster-shared L2. Larger data should reach a slow memory-dominated region.
   Apple system-level caching and translation overhead prevent assuming a clean L3 plateau.
2. Sequential access should outperform random access through prefetching/locality.
   Sparse accesses should deliver fewer useful bytes per second than dense streaming.
3. Read/write mixtures should change useful throughput, but software operation ratios
   need not equal DRAM traffic ratios because of write allocation and writeback.
4. Increasing background workers should raise throughput initially, then give
   diminishing returns while dependent probe latency rises. A knee may not be
   resolved at the selected discrete load levels.
5. Spreading the same number of nodes over more native pages should increase latency.
   Distributing offsets within pages reduces, but does not eliminate, cache confounding.
   Without data-TLB counters this is evidence of a page-locality effect, not an isolated TLB penalty.
6. A cache-resident streaming test may report much higher bandwidth than a large test.
   Calling that result DRAM bandwidth would be misleading.
7. Larger/strided multiply kernels should have more cache-related stall pressure per
   element than a small sequential kernel. Counter-assisted profiling is separate from
   uninstrumented timing so profiler overhead is not silently mixed into baseline results.
