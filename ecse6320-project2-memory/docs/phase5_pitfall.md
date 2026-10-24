# Phase 5 — cache-reuse benchmark pitfall

The same pinned sequential-read kernel processed exactly 16,777,216 logical 64-byte operations (1 GiB useful bytes) in every trial. Only the working-set span differed: 16 MiB repeatedly reused versus 1 GiB traversed once. Three repetitions were retained.

| Case | Working set | Median useful GiB/s | Mean | SD | CV |
|---|---:|---:|---:|---:|---:|
| Cache-reuse bandwidth | 16 MiB | 35.262 | 35.210 | 0.234 | 0.67% |
| DRAM-sensitive useful bandwidth | 1 GiB | 31.369 | 28.714 | 5.538 | 19.29% |

The small reused span reported 12.4% greater median useful bandwidth. Calling 35.262 GiB/s “DRAM bandwidth” would therefore be misleading: much of the repeated 16 MiB traffic can be served by the cache hierarchy. The 1 GiB case is described only as DRAM-sensitive; useful bytes still do not equal physical memory traffic.

The 1 GiB set approached but did not exceed the 20% CV threshold, and all three values remain canonical. Other avoided pitfalls include migration (all runs pinned), tiny intervals (1 GiB useful work), changing the Balanced plan, assuming nominal sizes prove residency, treating uProf process totals as kernel-only, inventing a direct L3 counter, and equating useful bandwidth with controller traffic.
