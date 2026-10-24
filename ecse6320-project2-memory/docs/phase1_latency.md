# Phase 1 — dependent-load hierarchy baseline

Five independent deterministic randomized-ring trials were run per size on pinned CPU 0. Auto-calibration made each timed interval approximately 250 ms or longer. All checksums remained in range and every run reported successful affinity.

| Interpretation | Working set | Median ns/load | Mean | SD | CV | Min–max |
|---|---:|---:|---:|---:|---:|---:|
| L1 representative | 16 KiB | 1.262 | 1.261 | 0.020 | 1.59% | 1.236–1.281 |
| L2 representative | 512 KiB | 3.328 | 3.332 | 0.011 | 0.33% | 3.321–3.350 |
| LLC representative | 16 MiB | 11.973 | 11.906 | 0.535 | 4.49% | 11.102–12.530 |
| DRAM-sensitive | 512 MiB | 111.876 | 112.395 | 1.146 | 1.02% | 111.261–114.071 |

The ordering is monotonic and the largest step is between the 16 MiB and 512 MiB representatives. The 16 MiB label is deliberately “LLC representative”: Windows exposes 64 MiB aggregate L3 while uProf reports two cache domains, and size alone cannot prove exact residency. Likewise, the 512 MiB point is interpreted as DRAM-sensitive, not a direct DRAM-only latency measurement. QPC provides nanoseconds; no cycles were inferred from the nominal 4.3 GHz WMI field.

All CVs are below the 20% rerun threshold, so no bounded rerun was needed. Raw samples are in `data/raw/phase1`, canonical statistics in `data/parsed/summary.csv`, and the figure is `results/plots/phase1_hierarchy_latency.png`.
