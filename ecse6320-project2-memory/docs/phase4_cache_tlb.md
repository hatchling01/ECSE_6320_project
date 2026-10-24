# Phase 4 — working sets, counters, and TLB

## Dense dependent-load sweep

Three pinned repetitions were collected at 18 working sets from 16 KiB through 1 GiB. Median latency stayed near 1.24–1.27 ns through 48 KiB, rose to 2.99 ns at 64 KiB, increased from 3.33 ns at 512 KiB to 5.19/9.23 ns at 1/2 MiB, remained 10.1–11.7 ns through 16 MiB, then rose sharply to 66.9 ns at 32 MiB and 97.3 ns at 64 MiB. It reached 102–129 ns from 128–512 MiB and 118.9 ns at 1 GiB.

These are transition regions consistent with hierarchy effects, not exact boundary proofs. AMD's official product page confirms aggregate 1,280 KB L1, 16 MB L2, and 64 MB L3 for the processor: <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-9-9950x.html>. It does not establish per-core/per-domain allocation. Windows reports the same aggregates, while uProf reports two cache domains. The pinned thread's sharp 16–32 MiB transition is therefore reported empirically without equating it to the aggregate 64 MiB L3.

The 512 MiB three-trial set was noisier (median 128.96 ns, mean 136.50 ns, CV 15.9%) and exceeded the 1 GiB median (118.87 ns). It remains below the 20% rerun threshold and is retained as an anomaly, not hidden.

## Streaming working sets

Median sequential useful read bandwidth was 36.21 GiB/s at 32 KiB, 36.13 at 512 KiB, 32.92 at 16 MiB, 31.05 at 128 MiB, and 28.74 at 1 GiB. The gradual decline illustrates reuse/locality without claiming that each point has one exclusive residency level.

## Process-level uProf evidence

Four representative profiles used cycles, retired instructions, L1 data accesses, L2 requests from L1D misses (including prefetch), and L1 DTLB misses. Timed kernels were lengthened to dominate. Selected process rows were:

| Case | IPC | CPI | L2 requests from L1D misses / 1k instructions | L1 DTLB event count |
|---|---:|---:|---:|---:|
| 16 KiB | 0.3219 | 3.1070 | 0.430 | 0 |
| 512 KiB | 0.1237 | 8.0848 | 423.807 | 136,000,000 |
| 16 MiB | 0.0173 | 57.8880 | 325.147 | 70,750,000 |
| 512 MiB | 0.0263 | 38.0060 | 185.024 | 42,250,000 |

The counter patterns support a major increase in L1-miss-related L2 requests beyond the L1-scale case, but they are sampled, process-wide, and include setup. Raw totals are not directly comparable because calibrated operation counts differ. The LLC/DRAM ordering of individual sampled values is not monotonic and is not used to manufacture an L3 miss rate. No L3, DF, UMC, or memory-controller counter was available.

## Normal-page TLB study

| Pages | Virtual span | Median ns/page access |
|---:|---:|---:|
| 16 | 64 KiB | 3.057 |
| 64 | 256 KiB | 3.002 |
| 256 | 1 MiB | 4.222 |
| 1,024 | 4 MiB | 6.012 |
| 4,096 | 16 MiB | 10.914 |
| 16,384 | 64 MiB | 18.257 |

The increasing trend beyond 64 pages supports greater translation/cache pressure, but page-selected data residency and page-table activity also change. Additional uProf profiles sampled 4,000,000 L1 DTLB events for 500,000,000 low-page operations (about 0.008/op) versus 101,500,000 for 100,000,000 high-page operations (about 1.015/op). These sampled process-level values support, but do not uniquely isolate, TLB misses.

## Large pages

Windows reports a 2 MiB large-page minimum, but the current token lacks `SeLockMemoryPrivilege`. Enabling it requires a prohibited system/security-policy change. No change was made. The 4 KiB-versus-large-page comparison is **UNAVAILABLE ON THIS TEST CONFIGURATION**; no simulation is presented as huge pages.
