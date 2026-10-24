# Project 2 (Mac) — Cache & Memory Performance Profiling

## Overview

This is the separate MacBook implementation of the ECSE 4320/6320 Project 2 assignment. It profiles cache and memory behavior with native C benchmarks, three-trial sweeps, and Instruments-assisted evidence. The independent Windows/AMD implementation is available at [../ecse6320-project2-memory/](../ecse6320-project2-memory/).

The imported measurements are preserved from the original project. The cross-platform analysis uses those existing measurements only; no benchmark was rerun during integration.

## Mac test platform

| Component | Verified project evidence |
|---|---|
| Model identifier | Mac16,8 |
| Processor | Apple M4 Pro, arm64 |
| Cores | 12 physical/logical: 8 performance + 4 efficiency; no SMT reported |
| Memory | 24 GiB unified memory |
| Cache facts recorded | P-core 128 KiB L1D; 16 MiB L2 per four-P-core group; E-core 64 KiB L1D; 4 MiB E-cluster L2; 128 B lines |
| Native page size | 16 KiB |
| OS | macOS 26.6.2 (Darwin 25.6.0, build 25G83) |
| Compiler | Apple Clang 21.0.0 (`clang-2100.3.34.2`) |
| Analysis | Python 3.13.15; Matplotlib 3.10.8 |
| Profiler | Xcode/Instruments 26.0.1 |
| Run state | Battery power; no hard pinning or frequency lock; no swap in use at end |

Sources: [system-before.json](data/raw/20261023-150209/system-before.json), [software-versions.json](data/raw/20261023-150209/software-versions.json), and the [original report](report/REPORT.md).

## Methodology

The native C benchmark uses `clock_gettime(CLOCK_MONOTONIC)`. A dependent randomized pointer ring measures latency and suppresses deliberate memory-level parallelism. Streaming kernels cover sequential/random patterns, 64/128/256/1024 B spacing, software read/write mixes, and footprint sweeps. A dependent 256 MiB probe runs beside up to 11 independent 128 MiB background workers for loaded-latency measurements. Page-locality tests compare compact 128 B nodes with nodes spread one per native 16 KiB page.

Each setting has three independent process trials. Plots report arithmetic mean ± sample standard deviation. Initialization, validation, and signpost setup are outside timed regions. macOS receives a user-interactive QoS hint, but the project does not claim hard affinity. Useful bandwidth counts application payload bytes, not physical DRAM traffic.

## Headline results

| Measurement | Result | Qualification |
|---|---:|---|
| 64 KiB dependent chain | 0.969 ns/access | L1-compatible, not a guaranteed residency proof |
| 4 MiB dependent chain | 7.836 ns/access | L2-compatible |
| 64 MiB dependent chain | 112.137 ns/access | Beyond cluster L2; mixed SLC/translation effects |
| 512 MiB dependent chain | 121.177 ns/access | Large, memory-dominated |
| 64 B sequential / random useful read bandwidth | 13.094 / 2.310 GB/s | 256 MiB address span; 8 useful bytes/access |
| Loaded sweep | 0 → 236.29 GB/s; 120.02 → 176.18 ns | 0 → 11 workers; observed plateau begins at four workers |
| Native-page locality, 8,192 nodes | 6.538 compact / 16.162 spread ns/access | 16 KiB pages; not isolated TLB latency |
| Highest observed useful bandwidth | 137.444 GB/s | 256 MiB software write stream; not DRAM bandwidth |

Canonical values are in [data/processed/summary.csv](data/processed/summary.csv). Cross-platform values and provenance are in [mac_windows_project2_comparison.csv](results/comparison/mac_windows_project2_comparison.csv).

## Key figures

![Mac working-set results](plots/working_set.png)

![Mac access-pattern and stride results](plots/patterns.png)

![Mac loaded-latency results](plots/intensity.png)

Additional figures cover [read/write mixes](plots/read_write.png), [page locality](plots/page_locality.png), [kernel counters](plots/kernel_counters.png), and the [benchmark pitfall](plots/pitfall.png).

## Comparison with Windows Project 2

| Aspect | Mac | Windows/AMD | Interpretation |
|---|---|---|---|
| Timing | `CLOCK_MONOTONIC` | QPC | Both are wall-clock timers; neither assumes a fixed CPU clock |
| Affinity | QoS hint, no hard pinning | Hard affinity to physical-core representatives | Windows provides tighter placement control |
| Dependent large-footprint latency | 121.177 ns at 512 MiB | 111.876 ns at 512 MiB representative | Moderate comparability; node spacing and statistics differ |
| 64 B sequential/random read ratio | 5.67× | 11.07× | Low comparability because footprints and useful-byte definitions differ |
| Page locality | 16 KiB native pages | 4 KiB normal pages | Page-count curves must not be treated as equivalent TLB tests |
| Counter evidence | Instruments L1D-related stall percentages | AMD uProf L1/L2 miss evidence | Neither recovered a complete last-level/DRAM counter story |

See the full [Mac vs Windows comparison](docs/MAC_VS_WINDOWS_COMPARISON.md), [comparison tables](results/comparison/COMPARISON_TABLES.md), and [dependency comparison](docs/dependency_comparison.md).

![Normalized stride comparison](results/comparison/plots/normalized_stride_degradation.png)

## Reproducibility

On the recorded Mac platform:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
make test
make run
caffeinate -i .venv/bin/python scripts/counters.py
make plots
.venv/bin/python scripts/check.py
```

`make run` executes production benchmarks and should only be used when a deliberate rerun is intended. To regenerate only the new comparison outputs from committed data while this folder remains beside the Windows project:

```sh
python3 scripts/generate_comparison.py
```

The complete dependency inventory is in [dependency_comparison.md](docs/dependency_comparison.md). The source inventory and omitted trace-bundle policy are in [source_inventory.md](docs/source_inventory.md).

## Limitations

- The compact Mac campaign is not exhaustive rubric coverage.
- Hard CPU affinity and frequency locking were unavailable/not used; the recorded run was on battery power with other applications present.
- Instruments supplied L1D-related stall percentages, not validated raw cache-miss or data-TLB counts. Custom TLB-counter export failed.
- Explicit 2 MiB allocation returned `KERN_INVALID_ARGUMENT`; no supported large-page alternative was established.
- The page-locality study combines translation, cache mapping, and prefetch effects and therefore does not isolate TLB penalty.
- Mac bandwidth is decimal GB/s and counts 8 useful bytes per operation; Windows uses GiB/s and a 64-byte logical operation. Absolute bandwidth comparisons are intentionally rated low.
- The large original Instruments `.trace` internals remain in the private source copy because they total roughly 660.6 MB and can contain machine metadata. Parsed XML/summaries, logs, raw measurements, processed results, source, scripts, reports, and figures are included here.
- Student review of the original AI-assisted draft remains required; the original report's caveats are preserved.
