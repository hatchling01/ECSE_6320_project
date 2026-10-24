# Phase 5B Effective Bandwidth, Roofline, and Synthesis

## Scope and Data Sources

This is analysis of existing Phase 3B and Phase 5A evidence. It performs no new benchmark, Phase 3 rerun, broad sweep, or additional uProf profile. Phase 3B supplies all runtime, ns/element, GFLOP/s, effective bandwidth, and scalar/auto/native speedups. The Phase 5A process-level counters are supporting architectural evidence only; profiler timings are not substituted for Phase 3B medians.

Representative Phase 3B points use the existing target working sets 24 KiB, 24 MiB, and 128 MiB for all four kernels, float32/float64, and scalar/auto/native builds. Raw and processed Phase 3B data remain unchanged.

## Arithmetic Intensity and Useful Traffic

Arithmetic intensity is useful FLOPs divided by useful algorithmic bytes. Counts are: AXPY 2 FLOPs and 3 element transfers per useful element; dot product 2 FLOPs and 2 transfers; elementwise multiply 1 FLOP and 3 transfers; three-point stencil 5 interior FLOPs, with copied boundaries, and `(4N-4)*sizeof(T)` useful bytes for N>=2. The exact finite-N stencil intensity is `5(N-2)/((4N-4)*sizeof(T))`; the large-N limit is 5/(4*sizeof(T)). For float32/float64, the limiting intensities are AXPY 0.16667/0.08333, dot 0.25000/0.12500, elementwise 0.08333/0.04167, and stencil 0.31250/0.15625 FLOP/B.

These are algorithmic/useful counts. They do not include cache-line overfetch, write-allocate traffic, reuse effects, or physical transactions. None of those traffic components was directly measured.

## Bandwidth Reference and Compute Assumptions

No new copy/stream measurement was necessary. The effective streaming-bandwidth reference reuses the median GCC-native Phase 3B useful effective bandwidth at 128 MiB for the streaming kernels AXPY, elementwise multiply, and stencil: 36.965 GiB/s float32 and 39.044 GiB/s float64. The component kernel rates and CVs are listed in `results/tables/roofline_summary.md`. This reference is based on useful bytes/time and is not physical DRAM bandwidth.

The estimated theoretical single-core compute ceiling assumes the Windows CIM-reported 4.3 GHz maximum clock, one 512-bit FMA per core cycle, and the observed native 16-lane float32/8-lane float64 ZMM width, yielding 137.6/68.8 GFLOP/s. The 4.3 GHz value is a platform-reported maximum used as an explicit assumption, not an observed sustained or AVX-512 operating frequency. The single-FMA/cycle throughput is also assumed, not established by project measurements. Native AXPY/stencil disassembly contains packed FMA; elementwise multiply uses `vmulps/vmulpd`; dot product uses packed multiply/reduction without observed packed FMA. Thus the common compute line is an optimistic hardware roof, especially for non-FMA/reduction kernels.

## Roofline and SIMD Compression

The roofline-style figure plots measured native GCC GFLOP/s from Phase 3B against algorithmic intensity for representative working sets, with `P_roof=min(P_compute, AI×BW_reference)`. A 512-bit vector is 4× the lane width of GCC auto's 128-bit XMM and 16× scalar float lanes, but those ratios are not expected speedups: memory/data supply, operation mix, dependency chains, compiler-generated reductions, and large working-set behavior constrain achieved throughput.

For float32 elementwise multiply, Phase 3B native speedup is 6.1375x at 24 KiB, 2.6522x at 24 MiB, and 0.9694x at 128 MiB. This compression accompanies lower useful effective bandwidth and the Phase 5A process-level observations: native instructions/update fall from 1.329 (small) to 0.900 (intermediate), then rise to 3.281 at large size (including harness activity); IPC declines from 2.618 to 1.113 to 0.983; L2 requests/update rise from 0.00475 to 0.1956 to 0.2063. The 128 MiB Phase 3B CV is 23.41%; these trends are consistent with increasing data-supply pressure and reduced arithmetic-side benefit, but do not prove exact L3/DRAM causality.

Across kernels, low-intensity AXPY/elementwise behavior compresses toward 1× at large working sets. Dot product shows weak SIMD gains across sizes, consistent with its reduction dependency as well as low useful intensity. The stencil's higher useful intensity and native FMA correlate with sustained speedups in several Phase 3B points, though variability remains and no compute-bound classification is asserted solely from the roofline. Phase 4C further demonstrates that non-unit strides select scalar paths in GCC auto/native despite `-march=native`; SIMD width matters only when the compiler emits and executes packed instructions.

## Limits

The roof uses useful logical bytes and a reference derived from useful effective bandwidth. It is not a physical DRAM roofline. uProf reports no direct L3 PMCs, DF/UMC counters, or memory-controller bandwidth. Phase 5A counters are process-level, include setup/warmup/checksum/runtime work, use sampled event counts, and show sparse DTLB events. No exact cache-residency boundary, physical-bandwidth saturation, write-allocate traffic, or causal counter-to-speedup relation is claimed. Variability is preserved from Phase 3B; high-CV values should not support fine-grained conclusions.

See `results/tables/roofline_summary.md`, `results/tables/roofline_summary.csv`, and `results/plots/roofline.png`. The Phase 6 final report and requirement audit are linked from `README.md`; Phase 6 adds no measurements.
