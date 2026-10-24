# Hypothesis outcomes

The original wording remains unchanged in `hypotheses.md`.

| # | Outcome | Evidence |
|---:|---|---|
| 1 | Supported | Representative medians increased 1.262→3.328→11.973→111.876 ns/load. |
| 2 | Supported | Dense transitions appeared near 48–64 KiB, 512 KiB–2 MiB, and 16–32 MiB, with gradual regions. |
| 3 | Supported | 1 GiB 64 B read: 29.234 sequential vs 2.641 random GiB/s. |
| 4 | Supported | Sequential read/write bandwidth declined materially from 64 to 1024 B; random was already locality-limited. |
| 5 | Supported | Pure read/write rates differed for both patterns. |
| 6 | Supported | Exact deterministic 70/30 and 50/50 mixes produced distinct rates. |
| 7 | Supported | Background throughput rose through all tested worker counts. |
| 8 | Not resolved | Latency rose, but no adjacent step met the preregistered knee rule. |
| 9 | Supported | Comparative `L=lambda W` rose 8.0→113.7; it is not hardware queue occupancy. |
| 10 | Partially supported | Process-level L2-request evidence rose greatly beyond 16 KiB, but sampled totals were not monotonic and no L3 PMC exists. |
| 11 | Supported | Normal-page access rose from ~3.0 ns at 16–64 pages to 18.3 ns at 16,384; uProf DTLB evidence rose per operation. |
| 12 | Not resolved | Large-page testing was unavailable without prohibited privilege changes. |
| 13 | Supported | 16 MiB reuse exceeded the 1 GiB span by 12.4% median bandwidth. |
| 14 | Partially supported | All primary results were pinned and controlled; an unpinned comparison was intentionally unnecessary. |
| 15 | Supported | Hierarchy ordering is qualitatively AMAT-consistent; exact AMAT is not computable from unavailable hit/miss probabilities. |
