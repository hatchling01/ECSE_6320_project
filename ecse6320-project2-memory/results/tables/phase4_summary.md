# Phase 4 summary

| Evidence | Headline |
|---|---|
| Dense latency | ~1.24 ns through 48 KiB; 2.99 ns at 64 KiB; 5.19–9.23 ns at 1–2 MiB; 11.68 ns at 16 MiB; 66.89 ns at 32 MiB; 118.87 ns at 1 GiB |
| Streaming | 36.21 GiB/s at 32 KiB versus 28.74 GiB/s at 1 GiB |
| uProf | L2-request PTI: 0.430 (16 KiB), 423.807 (512 KiB), 325.147 (16 MiB), 185.024 (512 MiB); process-level supporting evidence |
| TLB | 3.057 ns at 16 pages to 18.257 ns at 16,384 pages |
| Large pages | UNAVAILABLE ON THIS TEST CONFIGURATION |

Full statistics are in `data/parsed/summary.csv`; process counter rows are in `data/parsed/uprof_process_summary.csv`.
