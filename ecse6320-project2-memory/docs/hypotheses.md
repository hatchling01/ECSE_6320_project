# Pre-experiment hypotheses

Recorded before production measurements on 2026-10-23 (America/New_York). These statements are immutable.

1. Dependent-load latency rises from L1 to L2 to LLC to DRAM.
2. Working-set transition regions broadly align with cache capacities but may be gradual.
3. Large sequential accesses outperform randomized ones through locality and prefetching.
4. Increasing stride 64→256→1024 B reduces useful bandwidth and/or raises cost.
5. Pure read and pure write bandwidth differ.
6. 70/30 and 50/50 mixes behave distinctly from pure directions.
7. More memory-generating threads initially raise aggregate throughput.
8. A saturation knee eventually combines diminishing bandwidth gain with rising probe latency.
9. Little's-Law host-visible occupancy rises with load but is not hardware queue depth.
10. L1/L2 miss-related activity rises with larger working sets.
11. More 4 KiB pages eventually increase DTLB pressure and latency.
12. Large pages plausibly reduce TLB pressure, but cannot be tested without a prohibited policy change.
13. Reusing a small cache-resident buffer can be mislabeled as DRAM bandwidth.
14. Pinning supports a more controlled interpretation than migration.
15. Results should fit qualitative AMAT reasoning, without inventing unmeasured hit/miss probabilities.
