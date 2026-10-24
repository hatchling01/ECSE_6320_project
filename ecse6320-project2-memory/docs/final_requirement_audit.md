# Final requirement audit

| Requirement | Status | Repository evidence |
|---|---|---|
| Custom MLC-equivalent | COMPLETE | `src/`, `docs/methodology.md` |
| Approximately one-outstanding dependent-load latency | COMPLETE | `data/raw/phase1`, `docs/phase1_latency.md` |
| L1/L2/LLC/DRAM representatives | COMPLETE | Phase 1 table/figure with qualified labels |
| Sequential and random access | COMPLETE | Phase 2 full matrix |
| 64/256/1024 B strides | COMPLETE | Phase 2 full matrix |
| 100/0, 70/30, 50/50, 0/100 mixes | COMPLETE | Phase 2 deterministic mix matrix |
| Intensity sweep and throughput-latency curve | COMPLETE | Phase 3, 0–15 workers and three curve views |
| Saturation knee | COMPLETE | Numerical rule applied; unresolved rather than invented |
| Little's Law | COMPLETE | `phase3_knee.md`, with interpretation limits |
| Dense working-set sweep | COMPLETE | 18 sizes, 16 KiB–1 GiB |
| Cache-miss impact | PARTIAL | uProf L1/L2 evidence; direct L3 PMC unavailable |
| TLB-miss/page-locality impact | COMPLETE | Six page counts plus low/high DTLB profiles |
| Normal 4 KiB pages | COMPLETE | Phase 4 TLB mode |
| Large-page comparison | LIMITATION | Unavailable: missing `SeLockMemoryPrivilege`; no policy change |
| Pinning/topology | COMPLETE | Windows API; CPUs 0,2,…,30 |
| Repetitions/statistics/error bars | COMPLETE | 3 or 5 repeats, mean/median/SD/CV/min/max |
| Counter evidence | PARTIAL | Six uProf profiles; no L3/DF/UMC/controller events |
| Misleading benchmark case | COMPLETE | Phase 5 same-kernel/same-work comparison |
| Raw and processed data | COMPLETE | `data/raw`, `data/parsed` |
| Plotting code | COMPLETE | `scripts/python/plot_results.py` |
| Environment and topology | COMPLETE | `config/environment.json`, `docs/environment.md` |
| AI-use disclosure | COMPLETE | `docs/ai_use.md` |
| Anomalies and limitations | COMPLETE | `docs/anomalies.md`, README |
