# Project 2 cross-platform comparison tables

All numbers come from the Mac [`summary.csv`](../../data/processed/summary.csv) or Windows [`summary.csv`](../../../ecse6320-project2-memory/data/parsed/summary.csv). The machine-readable, provenance-labeled form is [`mac_windows_project2_comparison.csv`](mac_windows_project2_comparison.csv). GB/s is decimal; GiB/s is binary. They are not silently converted because payload definitions also differ.

## Platform

| Attribute | Mac | Windows/AMD |
|---|---|---|
| CPU | Apple M4 Pro | AMD Ryzen 9 9950X |
| Cores / threads | 8 P + 4 E / 12 | 16 / 32 |
| Memory | 24 GiB unified | ~61.65 GiB OS-visible, four DIMMs |
| Page / cache line | 16 KiB / 128 B | 4 KiB / 64 B operation spacing |
| OS | macOS 26.6.2 | Windows 11 Enterprise build 26200 |
| Timer | `CLOCK_MONOTONIC` | QPC |
| Placement | QoS hint, not pinned | Hard-pinned physical-core representatives |

## Latency

| Region | Mac ns/access | Windows ns/load | Comparability |
|---|---:|---:|---|
| L1-compatible representative | 0.969 at 64 KiB | 1.262 at 16 KiB | MODERATE |
| L2-compatible representative | 7.836 at 4 MiB | 3.328 at 512 KiB | LOW |
| LLC/L3 representative | N/A | 11.973 at 16 MiB | Unsupported on Mac |
| 512 MiB large chain | 121.177 | 111.876 | MODERATE |

## Bandwidth and pattern

| 64 B read pattern | Mac GB/s | Windows GiB/s | Within-platform normalized | Comparability |
|---|---:|---:|---|---|
| Sequential | 13.094 | 29.234 | 1.000 / 1.000 | LOW |
| Random | 2.310 | 2.641 | 0.176 / 0.090 | LOW |

Mac uses a 256 MiB address span and 8 useful bytes/access. Windows uses a 1 GiB working set and 64 logical useful bytes/operation.

## Stride normalized to 64 B

| Stride | Mac GB/s | Mac ratio | Windows GiB/s | Windows ratio | Comparability |
|---:|---:|---:|---:|---:|---|
| 64 B | 13.094 | 1.000 | 29.234 | 1.000 | MODERATE normalized |
| 256 B | 2.936 | 0.224 | 11.566 | 0.396 | MODERATE normalized |
| 1024 B | 2.644 | 0.202 | 10.331 | 0.353 | MODERATE normalized |

## Read/write normalized to pure read

| Read percentage | Mac GB/s | Mac ratio | Windows GiB/s | Windows ratio | Comparability |
|---:|---:|---:|---:|---:|---|
| 100% | 96.068 | 1.000 | 31.954 | 1.000 | LOW |
| 70% | 26.497 | 0.276 | 28.477 | 0.891 | LOW |
| 50% | 25.264 | 0.263 | 25.450 | 0.796 | LOW |
| 0% | 137.444 | 1.431 | 18.840 | 0.590 | LOW |

## Loaded concurrency

| Item | Mac | Windows/AMD | Comparability |
|---|---:|---:|---|
| Sampled workers | 0, 1, 2, 4, 7, 11 | 0, 1, 2, 4, 8, 12, 15 | LOW |
| Loaded bandwidth span | 98.080–236.294 GB/s (1–11 workers) | 3.713–35.199 GiB/s (1–15 workers) | LOW |
| Probe latency span | 120.023–176.184 ns | 123.868–193.454 ns | LOW |
| Final / unloaded latency | 1.468× | 1.562× | LOW |
| Knee outcome | Four-worker saturation candidate | Predefined knee unresolved | Not a direct numeric comparison |

## Working-set transitions

| Platform | Observed regions | Interpretation |
|---|---|---|
| Mac | 128–256 KiB; broad 8–64 MiB rise | Compatible with leaving P-core L1 and then shared-cache/translation effects; not exact capacity proof |
| Windows | 48–64 KiB; 512 KiB–2 MiB; 16–32 MiB | Representative hierarchy transitions; not exact placement proof |

## TLB / page locality

| Platform | Small region | Large region | Native page | Comparability |
|---|---|---|---:|---|
| Mac | 0.955 ns at 64 spread nodes | 16.162 ns at 8,192 spread nodes | 16 KiB | LOW; compact/spread also changes footprint/cache mapping |
| Windows | ~3.0 ns at 16–64 pages | 18.257 ns at 16,384 pages | 4 KiB | LOW across platforms |

## Dependencies

| Function | Mac | Windows/AMD |
|---|---|---|
| Compiler/build | Apple Clang 21 / Make | Clang 23.1.4 / CMake / Ninja |
| Python analysis | Python 3.13.15, Matplotlib 3.10.8 | Python 3.13.9, NumPy, Pandas, Matplotlib |
| Profiler | Xcode/Instruments 26.0.1 | AMD uProf 5.3.521.0 |
| Platform APIs | pthread QoS, signposts, macOS system tools | Windows affinity/topology/QPC APIs |

## Requirement coverage

| Requirement group | Mac | Windows/AMD |
|---|---|---|
| Latency hierarchy | PARTIAL: L1/L2/large; conventional LLC not claimed | COMPLETE |
| Pattern/stride/mix | COMPLETE | COMPLETE |
| Working-set and concurrency | COMPLETE | COMPLETE |
| Little's Law / pitfall | COMPLETE | COMPLETE |
| Cache counters | PARTIAL | PARTIAL |
| TLB evidence | PARTIAL | COMPLETE |
| Huge/large pages | NOT APPLICABLE / PLATFORM LIMITATION | NOT APPLICABLE / PLATFORM LIMITATION |
| Repetitions / statistics | COMPLETE / PARTIAL for CV | COMPLETE |
| Hard pinning | PARTIAL | COMPLETE |
| Raw/processed data, plots, environment | COMPLETE | COMPLETE |

The row-level coverage matrix and methodology rationale are in the [full comparison report](../../docs/MAC_VS_WINDOWS_COMPARISON.md).
