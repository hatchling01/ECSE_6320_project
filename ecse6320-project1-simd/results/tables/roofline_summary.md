# Phase 5B Roofline-Style Analysis

Analysis uses existing Phase 3B statistics only. No new benchmark, copy/stream study, or uProf profile was run.

## Effective Streaming-Bandwidth Reference

The existing 128 MiB GCC-native Phase 3B effective bandwidths provide a usable, large-working-set reference. For each datatype, the reference is the median of useful effective bandwidth for AXPY, elementwise multiply, and the three-point stencil. This is a useful-byte algorithmic reference, not a copy benchmark or physical DRAM bandwidth. No direct L3/DF/UMC counters are available.

| Type | Reference (GiB/s) | Source kernels (GiB/s; CV) |
|---|---:|---|
| float32 | 36.965 | axpy: 36.965 (11.9% CV); elementwise_multiply: 24.519 (23.4% CV); stencil_1d_three_point: 49.457 (25.9% CV) |
| float64 | 39.044 | axpy: 39.044 (13.6% CV); elementwise_multiply: 28.443 (23.9% CV); stencil_1d_three_point: 47.552 (25.4% CV) |

## Compute Ceiling Assumption

The estimated theoretical single-core compute ceiling assumes the Windows CIM-reported 4.3 GHz maximum clock (not a measured sustained AVX-512 frequency), one 512-bit vector FMA per core cycle, and observed native widths of 16 float32 or 8 float64 lanes. That yields 137.6 GFLOP/s float32 and 68.8 GFLOP/s float64 under the stated assumption. The Phase 2 evidence observes packed FMA in native AXPY and stencil, but not in elementwise multiply or dot product; dot also has a reduction dependency. The common compute roof is an optimistic hardware upper bound for those kernels, not a measured or per-kernel sustained ceiling.

## Arithmetic Intensity

| Kernel | Type | FLOPs/useful element | Useful logical bytes/useful element | Intensity (FLOP/B) |
|---|---|---:|---:|---:|
| axpy | float32 | 2 | 12 | 0.166667 |
| dot_product | float32 | 2 | 8 | 0.250000 |
| elementwise_multiply | float32 | 1 | 12 | 0.083333 |
| stencil_1d_three_point | float32 | 5 interior; average 5(N-2)/N | 16 asymptotic; average 16(1-1/N) | 0.312500 |
| axpy | float64 | 2 | 24 | 0.083333 |
| dot_product | float64 | 2 | 16 | 0.125000 |
| elementwise_multiply | float64 | 1 | 24 | 0.041667 |
| stencil_1d_three_point | float64 | 5 interior; average 5(N-2)/N | 32 asymptotic; average 32(1-1/N) | 0.156250 |

Assumptions: AXPY counts one multiply plus one add (2 FLOPs); dot counts one multiply plus one accumulation add (2 FLOPs); elementwise multiply counts one multiply. For the three-point stencil, each interior output uses three multiplies and two adds (5 FLOPs); copied endpoints perform no floating-point operation. For N>=2 its useful-byte total is `(4N-4)*sizeof(T)` including three input values plus one output for each interior point and the two copied endpoints; the table gives the large-N per-element limit. All byte counts are useful logical algorithmic bytes, not measured physical traffic.

## Representative Native Points

The roofline plot uses GCC-native Phase 3B medians at small (24 KiB), intermediate (24 MiB), and large (128 MiB) target footprints. The CSV retains scalar/auto/native data at all 72 selected kernel/type/build/size points, including runtime, ns/element, GFLOP/s, useful effective bandwidth, CV, and speedups.

| Type | Kernel | Size | N | AI (useful FLOP/B) | Measured GFLOP/s | Useful effective GiB/s | Speedup vs scalar | Roof at point GFLOP/s | CV |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| float32 | axpy | small_cache_resident | 3,072 | 0.16667 | 81.075 | 453.044 | 7.443x | 6.615 | 0.7% |
| float32 | axpy | intermediate_cache_scale | 3,145,728 | 0.16667 | 11.593 | 64.782 | 1.123x | 6.615 | 98.1% |
| float32 | axpy | large_dram_sensitive | 16,777,216 | 0.16667 | 6.615 | 36.965 | 1.017x | 6.615 | 11.9% |
| float64 | axpy | small_cache_resident | 1,536 | 0.08333 | 40.538 | 453.044 | 3.938x | 3.494 | 1.6% |
| float64 | axpy | intermediate_cache_scale | 1,572,864 | 0.08333 | 14.667 | 163.916 | 1.661x | 3.494 | 35.2% |
| float64 | axpy | large_dram_sensitive | 8,388,608 | 0.08333 | 3.494 | 39.044 | 1.114x | 3.494 | 13.6% |
| float32 | dot_product | small_cache_resident | 3,072 | 0.25000 | 5.582 | 20.793 | 0.968x | 9.923 | 20.2% |
| float32 | dot_product | intermediate_cache_scale | 3,145,728 | 0.25000 | 5.474 | 20.394 | 0.977x | 9.923 | 3.1% |
| float32 | dot_product | large_dram_sensitive | 16,777,216 | 0.25000 | 5.323 | 19.830 | 1.001x | 9.923 | 5.0% |
| float64 | dot_product | small_cache_resident | 1,536 | 0.12500 | 5.724 | 42.645 | 0.991x | 5.240 | 35.1% |
| float64 | dot_product | intermediate_cache_scale | 1,572,864 | 0.12500 | 5.367 | 39.989 | 0.995x | 5.240 | 1.2% |
| float64 | dot_product | large_dram_sensitive | 8,388,608 | 0.12500 | 4.701 | 35.025 | 1.069x | 5.240 | 10.4% |
| float32 | elementwise_multiply | small_cache_resident | 2,048 | 0.08333 | 32.768 | 366.211 | 6.138x | 3.308 | 5.4% |
| float32 | elementwise_multiply | intermediate_cache_scale | 2,097,152 | 0.08333 | 14.014 | 156.616 | 2.652x | 3.308 | 33.5% |
| float32 | elementwise_multiply | large_dram_sensitive | 11,184,810 | 0.08333 | 2.194 | 24.519 | 0.969x | 3.308 | 23.4% |
| float64 | elementwise_multiply | small_cache_resident | 1,024 | 0.04167 | 16.698 | 373.224 | 3.223x | 1.747 | 2.7% |
| float64 | elementwise_multiply | intermediate_cache_scale | 1,048,576 | 0.04167 | 3.440 | 76.888 | 0.686x | 1.747 | 111.9% |
| float64 | elementwise_multiply | large_dram_sensitive | 5,592,405 | 0.04167 | 1.273 | 28.443 | 1.102x | 1.747 | 23.9% |
| float32 | stencil_1d_three_point | small_cache_resident | 3,072 | 0.31240 | 102.869 | 306.674 | 5.581x | 12.399 | 2.5% |
| float32 | stencil_1d_three_point | intermediate_cache_scale | 3,145,728 | 0.31250 | 85.580 | 255.047 | 4.943x | 12.403 | 15.5% |
| float32 | stencil_1d_three_point | large_dram_sensitive | 16,777,216 | 0.31250 | 16.595 | 49.457 | 1.181x | 12.403 | 25.9% |
| float64 | stencil_1d_three_point | small_cache_resident | 1,536 | 0.15615 | 40.319 | 240.476 | 2.214x | 6.546 | 0.7% |
| float64 | stencil_1d_three_point | intermediate_cache_scale | 1,572,864 | 0.15625 | 32.686 | 194.826 | 2.095x | 6.551 | 10.2% |
| float64 | stencil_1d_three_point | large_dram_sensitive | 8,388,608 | 0.15625 | 7.978 | 47.552 | 1.055x | 6.551 | 25.4% |

The curve is `P_roof = min(P_compute, AI × BW_reference)`, converting GiB/s to decimal GB/s for GFLOP/s. The plotted reference and intensities both use useful logical bytes. This is a roofline-style algorithmic comparison, not a physical DRAM roofline.

The bandwidth reference is a large-working-set effective rate, not a cache-level bandwidth ceiling. Cache-resident Phase 3B points can exceed its slope because data supply differs by working set; do not treat that as a contradiction or infer an exact cache boundary. A multi-level physical roofline would require cache-level/physical bandwidth measurements that this project does not have.

Plot: `results/plots/roofline.png`. Full machine-readable rows: `results/tables/roofline_summary.csv`.
