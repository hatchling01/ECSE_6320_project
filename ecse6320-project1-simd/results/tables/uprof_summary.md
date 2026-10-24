# Phase 5A Representative AMD uProf Profiles

Nine representative profiles only: float32 elementwise multiply, GCC scalar/auto/native, and the 24 KiB, 24 MiB, and 128 MiB Phase 3B working-set sizes. No Phase 5B or Phase 6 work was performed.

## Collection Configuration

AMD uProf CLI 5.3.521.0 ran the Phase 3 `benchmark_runner` natively on Windows, with process affinity CPU 0, three warmup batches, and the profile-specific repetitions/batching recorded in the CSV. Each run used a custom six-core-PMC bundle at interval 250,000: `CYCLES_NOT_IN_HALT` (PMCx076), `RETIRED_INST` (PMCx0C0), one FP-uop event (`SCALAR_UOPS_RETIRED` for scalar, `PACK_128_UOPS_RETIRED` for GCC auto, `PACK_512_UOPS_RETIRED` for GCC native), `L1_DC_ACCESSES_ALL` (PMCx029), `L2_CACHE_ACCESS_FROM_L1_DC_MISS` (PMCx060), and `L1_DTLB_MISSES` (PMCx045). The command/configuration for every case is recorded in `results/uprof/phase5a/command_manifest.csv`; raw sessions and report CSVs are under `results/uprof/phase5a/`.

uProf's process-level event totals include harness startup, allocation/initialization, warmups, checksums, and runtime overhead—not just the timed kernel loop. The per-useful-update counter columns normalize those whole-process counts by the configured useful updates and are architectural context, not kernel-exclusive cycles/instructions. PMC counts are sampled at the configured interval. Phase 3B times below remain the performance baseline; profiler timings do not replace them.

## Cross-Check and Architectural Counts

| Size | Build | Phase 3B median ms | Phase 3B ns/element | Phase 3B speedup | Phase 3B effective GiB/s | Phase 3B CV | Process cycles/update | Process instructions/update | IPC | FP-uops/update | L1 accesses/update | L1 accesses/kInst | L2 requests/update | L2 requests/kInst | DTLB misses/update | DTLB misses/kInst |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| small_cache_resident | gcc-scalar | 0.049 | 0.187302 | 1.000x | 59.668 | 0.45% | 1.584 | 6.949 | 4.387 | 0.9993 | 3.444 | 495.621 | 0.01141 | 1.642 | 0.0009508 | 0.137 |
| small_cache_resident | gcc-auto | 0.015 | 0.0564575 | 3.318x | 197.952 | 4.41% | 0.6817 | 2.699 | 3.960 | 1.008 | 1.146 | 424.445 | 0.005705 | 2.113 | 0 | 0.000 |
| small_cache_resident | gcc-native | 0.008 | 0.0305176 | 6.138x | 366.211 | 5.39% | 0.5077 | 1.329 | 2.618 | 0.1873 | 0.5467 | 411.302 | 0.004754 | 3.577 | 0.0009508 | 0.715 |
| intermediate_cache_scale | gcc-scalar | 0.397 | 0.189257 | 1.000x | 59.054 | 5.82% | 1.885 | 6.565 | 3.482 | 1.038 | 3.183 | 484.838 | 0.1979 | 30.148 | 0.001157 | 0.176 |
| intermediate_cache_scale | gcc-auto | 0.176 | 0.0838041 | 2.258x | 133.377 | 21.33% | 1.208 | 2.302 | 1.905 | 1.057 | 0.9282 | 403.218 | 0.1979 | 85.973 | 0.001157 | 0.503 |
| intermediate_cache_scale | gcc-native | 0.150 | 0.0713587 | 2.652x | 156.616 | 33.49% | 0.809 | 0.9004 | 1.113 | 0.1875 | 0.3426 | 380.463 | 0.1956 | 217.224 | 0.001157 | 1.285 |
| large_dram_sensitive | gcc-scalar | 4.942 | 0.441872 | 1.000x | 25.300 | 25.73% | 3.886 | 9.077 | 2.336 | 1.307 | 3.354 | 369.578 | 0.2098 | 23.110 | 0.001719 | 0.189 |
| large_dram_sensitive | gcc-auto | 5.220 | 0.466704 | 0.947x | 23.957 | 19.92% | 3.535 | 4.826 | 1.365 | 1.46 | 1.1 | 228.001 | 0.2046 | 42.394 | 0.001719 | 0.356 |
| large_dram_sensitive | gcc-native | 5.098 | 0.455824 | 0.969x | 24.519 | 23.41% | 3.337 | 3.281 | 0.983 | 0.1874 | 0.5622 | 171.384 | 0.2063 | 62.893 | 0.001719 | 0.524 |

## Interpretation

The Phase 3B cross-check shows the strong small-working-set SIMD speedups and near-1x large-working-set elementwise results already documented in `results/tables/negative_cases.md`. uProf confirms retired-instruction/IPC and cache/TLB event samples are available for these runs. SIMD activity must be interpreted by each selected uop event: scalar FP uops for GCC scalar, 128-bit packed FP uops for auto, and 512-bit packed FP uops for native. Do not compare raw uop counts without the different element widths and useful-update normalization.

The L2 event is `L2_CACHE_ACCESS_FROM_L1_DC_MISS`; uProf describes it as L2 requests due to L1 data-cache misses and notes it includes hardware/software prefetches. L1 DTLB misses count both L2-DTLB hits and misses. These are sampled event counts and can be sparse/noisy. The host reports only six core PMCs, so all six were used; no direct L3, DF/UMC, or memory-controller bandwidth metrics are available. No L3 miss rate, physical DRAM bandwidth, or exact cache-residency conclusion is claimed.

## Collection Anomalies and Limits

The first CLI attempt combining predefined `--config cpi` and custom `--event` options was rejected by uProf. A subsequent attempt combined mutually exclusive `--show-event-count` and `--show-sample-count` flags; uProf warned and selected its default display. A small-scalar smoke attempt produced a report but no harness timing CSV and is retained as incomplete in the manifest; the successful retry uses a numbered attempt directory and whitespace-free runner metadata arguments. These setup attempts are retained but excluded from the nine valid profiles. A small number of event rows, especially L1 DTLB, are zero or sparse at interval 250,000; do not interpret zero samples as proof that the underlying event never occurred. Hyper-V is reported active by uProf; these profiles are native Windows observations on the supplied host, not a cross-machine comparison.

Raw profile databases, report exports, and profiler-instrumented timing files are under `results/uprof/phase5a/`. The machine-readable comparison is `results/tables/uprof_summary.csv`; exact commands and per-case options are in `command_manifest.csv`.

Phase 5A is representative architectural evidence only. No roofline analysis, broad uProf sweep, or Phase 5B work is included.
