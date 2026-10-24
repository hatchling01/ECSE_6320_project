# Phase 2 SIMD Verification

This table reports compiler diagnostics and emitted instructions only. It contains no timing, speedup, throughput, or performance conclusions. GCC scalar/auto/native and Clang auto correctness tests each passed all 448 Phase 1 cases.

Widths below are per element type: XMM packed operations are 128-bit (4 float or 2 double lanes); ZMM packed operations are 512-bit (16 float or 8 double lanes). Scalar SSE scalar-form instructions do not count as vectorized loops. Native support is separate from per-kernel use.

| Kernel | Type | Compiler/build | Vectorized? | Observed width | Key emitted instructions | FMA? | Tail/cleanup observed | Evidence |
|---|---|---|---|---|---|---|---|---|
| AXPY | float32 | GCC scalar | No | None | `mulss`, `addss` | No | Scalar loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| AXPY | float64 | GCC scalar | No | None | `mulsd`, `addsd` | No | Scalar loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| AXPY | float32 | GCC auto | Yes | 128-bit XMM, 4 lanes | `mulps`, `addps` | No | Scalar cleanup branch visible | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| AXPY | float64 | GCC auto | Yes | 128-bit XMM, 2 lanes | `mulpd`, `addpd` | No | Scalar cleanup branch visible | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| AXPY | float32 | GCC native | Yes | 512-bit ZMM, 16 lanes | `vfmadd213ps`, `vfmadd132ps` | Yes, packed; scalar cleanup also present | Masked vector epilogue and scalar path | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| AXPY | float64 | GCC native | Yes | 512-bit ZMM, 8 lanes | `vfmadd213pd`, `vfmadd132pd` | Yes, packed; scalar cleanup also present | Masked vector epilogue and scalar path | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| AXPY | float32 | Clang auto | Yes | 128-bit XMM, 4 lanes | `mulps`, `addps` | No | Scalar cleanup/fallback branch | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| AXPY | float64 | Clang auto | Yes | 128-bit XMM, 2 lanes | `mulpd`, `addpd` | No | Scalar cleanup/fallback branch | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| Dot product | float32 | GCC scalar | No | None | Scalar `mulss`/`addss` form | No | Scalar accumulation loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| Dot product | float64 | GCC scalar | No | None | Scalar `mulsd`/`addsd` form | No | Scalar accumulation loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| Dot product | float32 | GCC auto | Yes | 128-bit XMM, 4 lanes | `mulps`; vector reduction | No | Vector reduction plus scalar reduction/remainder | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| Dot product | float64 | GCC auto | Yes | 128-bit XMM, 2 lanes | `mulpd`; vector reduction | No | Vector reduction plus scalar reduction/remainder | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| Dot product | float32 | GCC native | Yes | 512-bit ZMM, 16 lanes | `vmulps`; scalar `vfmadd231ss` also appears | Scalar cleanup only; no packed FMA observed | Vector epilogues and horizontal/scalar reduction | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| Dot product | float64 | GCC native | Yes | 512-bit ZMM, 8 lanes | `vmulpd`; scalar `vfmadd231sd` also appears | Scalar cleanup only; no packed FMA observed | Vector epilogues and horizontal/scalar reduction | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| Dot product | float32 | Clang auto | No | None | Scalar `mulss`/`addss` form | No | Strict-FP scalar reduction | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| Dot product | float64 | Clang auto | No | None | Scalar `mulsd`/`addsd` form | No | Strict-FP scalar reduction | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| Elementwise multiply | float32 | GCC scalar | No | None | Scalar `mulss` form | No | Scalar loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| Elementwise multiply | float64 | GCC scalar | No | None | Scalar `mulsd` form | No | Scalar loop | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| Elementwise multiply | float32 | GCC auto | Yes | 128-bit XMM, 4 lanes | `mulps` | No | Scalar/short-vector cleanup visible | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| Elementwise multiply | float64 | GCC auto | Yes | 128-bit XMM, 2 lanes | `mulpd` | No | Scalar cleanup branch visible | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| Elementwise multiply | float32 | GCC native | Yes | 512-bit ZMM, 16 lanes | `vmulps` | No | Masked ZMM epilogue | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| Elementwise multiply | float64 | GCC native | Yes | 512-bit ZMM, 8 lanes | `vmulpd` | No | Masked ZMM epilogue | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| Elementwise multiply | float32 | Clang auto | Yes | 128-bit XMM, 4 lanes | `mulps` | No | Scalar cleanup/fallback branch | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| Elementwise multiply | float64 | Clang auto | Yes | 128-bit XMM, 2 lanes | `mulpd` | No | Scalar cleanup/fallback branch | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| 1D three-point stencil | float32 | GCC scalar | No | None | Scalar `mulss`/`addss` form | No | Scalar interior loop; boundary copies remain scalar | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| 1D three-point stencil | float64 | GCC scalar | No | None | Scalar `mulsd`/`addsd` form | No | Scalar interior loop; boundary copies remain scalar | `gcc-scalar-kernels.cpp-vectorization.txt`; `gcc-scalar-kernels.asm` |
| 1D three-point stencil | float32 | GCC auto | Yes | 128-bit XMM, 4 lanes | `mulps`, `addps` | No | Scalar cleanup plus scalar boundary handling | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| 1D three-point stencil | float64 | GCC auto | Yes | 128-bit XMM, 2 lanes | `mulpd`, `addpd` | No | Scalar cleanup plus scalar boundary handling | `gcc-auto-kernels.cpp-vectorization.txt`; `gcc-auto-kernels.asm` |
| 1D three-point stencil | float32 | GCC native | Yes | 512-bit ZMM, 16 lanes | `vfmadd132ps`, `vfmadd231ps` | Yes, packed; scalar cleanup also present | Masked vector epilogue and scalar boundary handling | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| 1D three-point stencil | float64 | GCC native | Yes | 512-bit ZMM, 8 lanes | `vfmadd132pd`, `vfmadd231pd` | Yes, packed; scalar cleanup also present | Masked vector epilogue and scalar boundary handling | `gcc-native-kernels.cpp-vectorization.txt`; `gcc-native-kernels.asm` |
| 1D three-point stencil | float32 | Clang auto | Yes | 128-bit XMM, 4 lanes | `mulps`, `addps` | No | Scalar cleanup plus scalar boundary handling | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |
| 1D three-point stencil | float64 | Clang auto | Yes | 128-bit XMM, 2 lanes | `mulpd`, `addpd` | No | Scalar cleanup plus scalar boundary handling | `clang-auto-kernels.cpp-vectorization.txt`; `clang-auto-kernels.asm` |

## Interpretation Limits

- GCC scalar used `-fno-tree-vectorize`, `-fno-tree-loop-vectorize`, and `-fno-tree-slp-vectorize`. No packed arithmetic is present in the project-kernel object; scalar SSE-form instructions are used for scalar floating-point operations.
- GCC auto vectorizes the dot reduction under this compiler's `-O3` behavior. Clang does not: its remark says it cannot prove floating-point reordering safe under strict FP. No fast-math option was enabled.
- GCC reports alias-versioning for the auxiliary strided multiply loop and also a missed fallback (`no vectype for stmt`) alongside the emitted packed-multiply path. That mixed diagnostic is preserved in the raw report.
- GCC native's host target query resolves `-march=native` to `znver5`. GCC enables SSE-family, AVX, AVX2, FMA, and multiple AVX-512 features. The actual kernel claims above are based on object code, not merely these target features.
- GCC auto and Clang emit 128-bit vectors; GCC native emits 512-bit vectors for the reported main loops. No AVX-512 claim is made for the auto builds.
- Strided elementwise multiply is included in the saved disassembly/report artifacts; the primary table is limited to the four assignment kernels.
- These builds were correctness/code-generation checks only. No runtime comparison, benchmark, working-set sweep, performance conclusion, or plot was produced.