# Negative Cases: SIMD Expectations and Pitfalls

This report reuses committed Phase 3B/4C measurements and Phase 2 code-generation evidence. No benchmark was run to prepare it.

## Case 1: Vectorized but No Useful Large-Span Speedup

| Kernel | Type | Aggregate working set | N | Build | Median ns/element | Speedup vs scalar | Useful effective GiB/s | CV | SIMD evidence |
|---|---|---:|---:|---|---:|---:|---:|---:|---|
| elementwise_multiply | float32 | 134,217,728 B | 11,184,810 | gcc-scalar | 0.441871610 | 1.000000x | 25.300 | 25.73% | scalar instructions: `mulss` |
| elementwise_multiply | float32 | 134,217,728 B | 11,184,810 | gcc-auto | 0.466704396 | 0.946791x | 23.957 | 19.92% | 128-bit XMM, 4 float lanes: `mulps` |
| elementwise_multiply | float32 | 134,217,728 B | 11,184,810 | gcc-native | 0.455823568 | 0.969392x | 24.519 | 23.41% | 512-bit ZMM, 16 float lanes: `vmovups; vmulps; masked ZMM epilogue` |

GCC native speedup is 0.969392x (scalar/native median ns/element). Phase 2 disassembly verifies packed 512-bit ZMM `vmulps` for 16 float lanes, followed by a masked ZMM epilogue. The loop is genuinely vectorized, but widening arithmetic does not yield substantial speedup at this 128 MiB working set: native and scalar CVs are 23.41% and 25.73%. This is consistent with memory/data-supply limitations, but does not establish direct DRAM saturation. Effective bandwidth is useful bytes/time; Phase 5 roofline/controller evidence has not been collected.

Evidence: `data/processed/phase3b_statistics.csv`, `results/disassembly/gcc-native-kernels.asm`, and `results/tables/simd_verification.md`.

## Case 2: Native ISA Does Not Guarantee Vectorization

Phase 4C's unit-stride paths use packed XMM/ZMM instructions. For runtime strides 2, 4, and 8, GCC auto/native branch to scalar `mulss`/`vmulss` loops. The measured native/scalar speedups illustrate the resulting collapse (and occasional noisy reversal):

| Aggregate span | Stride 1 | Stride 2 | Stride 4 | Stride 8 |
|---|---:|---:|---:|---:|
| Small (24 KiB) | 5.380x | 0.891x | 0.825x | 0.714x |
| Intermediate (24 MiB) | 2.169x | 1.675x | 0.864x | 0.865x |
| Large (~128 MiB) | 1.208x | 1.099x | 0.957x | 1.383x |

The small-span native speedup falls from 5.380x at stride 1 to 0.891x, 0.825x, and 0.714x at strides 2, 4, and 8. Phase 2 `gcc-native-kernels.asm` and `gcc-auto-kernels.asm` show the packed path guarded on unit strides and scalar single-precision instructions on the non-unit fallback. `-march=native` identifies a target capability; it is not proof that this runtime access pattern vectorized.

Evidence: `data/processed/phase4c_stride_statistics.csv`, `results/tables/phase4c_stride_summary.md`, and the two GCC Phase 2 disassemblies.

## Sources

- Phase 3B large-span measurements use original `phase3_raw_v3` rows; all ten samples and their CVs remain available in `data/processed/phase3b_statistics.csv` and `data/processed/phase3b_samples.csv`.
- Phase 4C uses 180 initial rows plus 65 targeted rerun rows; 11/36 merged groups remain above 20% CV. No sample was discarded.
- No Phase 5 roofline, direct physical bandwidth, or broad uProf claim is made.
