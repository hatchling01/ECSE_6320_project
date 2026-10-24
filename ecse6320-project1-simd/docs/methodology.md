# Methodology Skeleton

Phases 1–6 are complete. Phase 6 consolidated reporting and validated existing artifacts only; the sections below record measurement methodology and results.

## Hardware/software environment
The Phase 0 host/toolchain snapshot is in `docs/environment.md` and `data/metadata/environment.json`. Measurements were collected on the same native Windows host; no BIOS, power, affinity, SMT, security, or virtualization setting was changed for this project.

## Build variants

Phase 2 uses separate CMake preset/build directories so variants cannot share objects:

| Preset/build directory | Compiler | Release flags |
|---|---|---|
| `gcc-scalar` / `build-gcc-scalar` | MSYS2 UCRT64 G++ 16.2.0 | `-O3 -DNDEBUG -fno-tree-vectorize -fno-tree-loop-vectorize -fno-tree-slp-vectorize -fopt-info-vec-all` |
| `gcc-auto` / `build-gcc-auto` | MSYS2 UCRT64 G++ 16.2.0 | `-O3 -DNDEBUG -fopt-info-vec-all` |
| `gcc-native` / `build-gcc-native` | MSYS2 UCRT64 G++ 16.2.0 | `-O3 -DNDEBUG -march=native -fopt-info-vec-all` |
| `clang-auto` / `build-clang-auto` | LLVM Clang++ 23.1.4, GNU/Windows target `x86_64-w64-windows-gnu` | `-O3 -DNDEBUG -Rpass=loop-vectorize -Rpass-missed=loop-vectorize -Rpass-analysis=loop-vectorize` |

`-DNDEBUG` is the CMake Release configuration define. No intrinsics, fast-math flags, explicit ISA flags on the auto variants, runtime comparisons, or timing targets were added. Configure/build/test with `cmake --preset <name>`, `cmake --build --preset <name>`, and `ctest --preset <name>`.

For this host, GCC's `-march=native` resolves to `znver5` (`gcc-native-target.txt`). GCC reports SSE/SSE2/SSE3/SSE4/SSE4a, AVX, AVX2, FMA, and AVX-512 feature families enabled. This is compiler target capability, not a claim that every kernel uses every ISA. The actual emitted instructions are listed in `results/tables/simd_verification.md` and the saved object-code excerpts.

The scalar control disables GCC loop and SLP tree vectorization explicitly. Its `kernels.cpp` vector report has no optimized vector-loop records, and its targeted kernel object contains no packed arithmetic instructions; scalar floating-point SSE forms such as `mulss`/`addss` remain, as expected for scalar arithmetic on x86-64.

## Compiler diagnostics and SIMD verification

GCC `-fopt-info-vec-all` output is preserved per build in `results/compiler_reports/*-compile.log`; kernel-source-specific lines are separately retained in `*-kernels.cpp-vectorization.txt`. Clang success, missed, and analysis remarks are captured similarly. Targeted `objdump -d -C -Mintel` output contains only project kernel symbols under `results/disassembly/`.

Observed in object code and reports:

- GCC auto and Clang auto use 128-bit XMM packed arithmetic for AXPY, elementwise multiplication, and the three-point stencil (4 float lanes or 2 double lanes). Clang also vectorizes the auxiliary strided elementwise loop.
- GCC auto vectorizes dot product at 128 bits. Clang leaves dot product scalar because it cannot prove floating-point reassociation safe under strict FP; no fast-math option was enabled.
- GCC native uses 512-bit ZMM main-loop arithmetic for all four kernels (16 float lanes or 8 double lanes). This AVX-512 use is verified by the emitted ZMM instructions; it is not inferred from CPU support alone.
- GCC native emits packed FMA in AXPY and stencil. Dot product has packed vector multiply/reduction and scalar FMA in cleanup, but no packed FMA was observed. Elementwise multiplication uses packed multiply only. GCC auto and Clang auto emitted separate packed multiply/add operations, not FMA.
- GCC auto exposes scalar and/or shorter-vector epilogues. GCC native uses masked ZMM epilogues for AXPY, elementwise multiply, strided multiply, and stencil; dot has vector epilogues and a horizontal/scalar reduction. Clang emits scalar cleanup/fallback paths. Stencil endpoints remain scalar boundary handling.
- GCC reports both an alias-versioned vectorized path and a missed fallback path for the auxiliary strided elementwise loop; the fallback diagnostic is `no vectype for stmt`. The object contains packed multiply in the optimized path. This does not change the primary contiguous-kernel conclusions.

The complete per-kernel/type/build matrix is `results/tables/simd_verification.md` with a CSV equivalent at `results/tables/simd_verification.csv`. All four variants passed the correctness suite (448 cases each). This phase records code generation only and makes no performance claims.

## Correctness testing
Implemented kernels are compared to separately implemented references. The reference uses `long double` intermediate arithmetic and accumulation, then converts to the requested datatype. Deterministic, nonconstant inputs use an index/seed formula. The harness tests AXPY, dot product, elementwise multiply, and 1D three-point stencil for float32 and float64 at sizes 0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 33, 100, and 1003. This includes empty/small cases and awkward future-tail sizes.

For elementwise comparisons, a value passes when `abs(error) <= abs_tol + rel_tol * abs(reference)`. float32 uses `abs_tol=2e-5`, `rel_tol=2e-6`; float64 uses `abs_tol=1e-12`, `rel_tol=1e-12`. Dot product uses the same combined criterion against a long-double accumulation to allow ordinary float accumulation error while catching indexing or arithmetic defects. Reported relative error divides absolute error by `max(abs(reference), abs_tol)`. Phase 2 reruns all 448 cases per compiler variant and records each variant separately under `data/processed/`.

All 448 correctness cases passed. Maximum observed errors were: float32 absolute `3.0517578125e-4`, relative `8.15349974300169e-7`; float64 absolute `3.410605131648481e-13`, relative `9.112246e-16`. The largest float32 absolute difference is from the 1003-element dot product and remains within the combined tolerance because its reference magnitude is larger. See `data/processed/correctness_results.csv` and `results/tables/correctness_summary.md`. These are correctness results, not performance measurements.

## Kernel definitions and stencil boundary
AXPY computes `y[i] = a*x[i] + y[i]`; dot product accumulates `x[i]*y[i]`; elementwise multiplication computes `z[i] = x[i]*y[i]`. The 1D stencil computes `a*x[i-1] + b*x[i] + c*x[i+1]` for interior indices. For `n > 0`, the chosen boundary convention copies `x[0]` and `x[n-1]` to the corresponding output endpoints; `n=1` copies its only element and `n=0` does nothing.

## Deterministic initialization
Test inputs are filled by a fixed integer index/seed formula mapped to nontrivial signed fractions. No random state or external dataset is used.

## Aligned-buffer design
`src/aligned_buffer.hpp` owns typed storage through `std::vector<T>`, checks power-of-two alignment and allocation overflow, and returns an aligned interior pointer. It reserves extra elements so tests can use offsets 1 and 3 while keeping pointers correctly aligned for `T`; these pointers are intentionally offset from a 64-byte boundary. The helper supports float and double. Phase 1 verifies both the aligned base and safe offsets; it does not measure alignment performance.

## Stride correctness foundation
Stride support is implemented for elementwise multiplication, the simplest independent kernel for validating stepped addressing without adding stencil-neighbor or reduction semantics. It checks strides 1, 2, 4, and 8 against a logical contiguous reference at every test size and datatype. Performance measurements are described separately below.

## Phase 4C Fixed-Span Stride

Scope is the existing `elementwise_multiply_strided` kernel, float32, and GCC scalar/auto/native. Each of three arrays is allocated at the same fixed span; useful N is `span_elements / stride`, exactly divisible for all selected spans. Aggregate allocation therefore remains constant at each span while useful work decreases as stride increases:

| Span class | Elements per buffer | Bytes per buffer | Three-array allocated span |
|---|---:|---:|---:|
| Small/cache-resident | 2,048 | 8,192 B | 24,576 B |
| Intermediate/cache-scale | 2,097,152 | 8,388,608 B | 25,165,824 B |
| Large/DRAM-sensitive | 11,184,808 | 44,739,232 B | 134,217,696 B |

The fixed spans approximate the 24 KiB, 24 MiB, and 128 MiB Phase 3 active-working-set points. The aggregate fixed allocation includes x, y, and z; the `allocated_span_bytes` raw field is per buffer and `allocated_total_bytes` records all three. Useful N is the logical number of updates: 2,048/2,097,152/11,184,808 at stride 1; divide by 2, 4, or 8 at the corresponding stride. No same-N-across-strides comparison or working-set sweep was used.

The validated Phase 3 `benchmark_runner` was extended with fixed-span allocation and dispatch to the existing strided API. It preserves `std::chrono::steady_clock`, logical CPU 0 affinity, three warmups, and the Phase 3 batching policy: 128 calls through N=4,096; 32 through N=65,536; one otherwise. Only the small span is batched (128 calls for all four strides). Five initial repetitions were collected. Each of the 36 build/span/stride configurations ran the independent strided reference comparison before any timing; existing float32 absolute/relative tolerances were unchanged. Correctness manifests record max errors and PASS status.

The initial matrix is 3 spans × 4 strides × 3 builds = 36 configurations and 180 timed samples. Configurations with initial CV >20% were eligible for exactly one five-sample rerun; 13 were selected, adding 65 separate raw rows, for 245 total observations and a maximum of 10 per configuration. Initial and rerun files remain separate. Build order rotates across span/stride points to reduce systematic build-order bias.

Per-call useful work is N elementwise multiplies and useful logical bytes are `3*N*sizeof(float)` (two useful input values read and one useful output value written). Batch multiplies both totals. `useful_effective_bandwidth_gib_per_s` is these useful logical bytes divided by elapsed time; it is not physical memory bandwidth and does not count cache-line overfetch. Raw rows record stride, per-buffer and aggregate allocation, useful N, batch, useful elements/s, elapsed time, ns/useful-element, GFLOP/s, effective useful bandwidth, build/flags, repetition, affinity, and timer. The analysis adds variability and scalar-relative speedups.

Initial CV median/max was 12.34%/56.26%, with 22/36 above 10% and 13/36 above 20%. After the targeted reruns, CV median/max was 12.34%/68.18%; 22/36 remained above 10% and 11/36 above 20%. Several intermediate/large points remain noisy and should not support fine-grained speedup claims.

At the small span, useful bandwidth from stride 1 to 8 fell from 59.19 to 52.32 GiB/s scalar, 234.38 to 44.12 auto, and 318.44 to 37.37 native. At the intermediate span it fell from 52.44 to 13.58 scalar, 94.17 to 13.78 auto, and 113.50 to 11.77 native. At the large span it fell from 24.47 to 2.48 scalar, 26.51 to 2.69 auto, and 29.56 to 3.43 native. These are useful effective bandwidths, not physical bandwidth measurements.

Scalar-relative auto/native speedups by stride are in `results/tables/phase4c_stride_summary.csv`. Representative endpoints: small-span auto/native is 3.96x/5.38x at stride 1 and 0.84x/0.71x at stride 8; intermediate is 1.79x/2.17x at stride 1 and 1.02x/0.87x at stride 8; large is 1.08x/1.21x at stride 1 and 1.08x/1.38x at stride 8. Several of these comparisons have high CV; the large stride-8 native ratio is especially not evidence of packed SIMD.

Phase 2 GCC auto and native disassembly show runtime checks requiring all three strides to equal one before taking their packed vector loops. GCC auto uses `movups`/`mulps` XMM instructions on that unit-stride path; GCC native uses `vmovups`/`vmulps` ZMM instructions. For strides 2, 4, and 8, both builds branch to scalar `movss`/`mulss` loops. Consequently, SIMD advantage collapses chiefly because the non-unit paths stop using packed SIMD, while useful cache-line utilization also declines. Do not attribute all slowdown to cache behavior. Evidence: `results/disassembly/gcc-auto-kernels.asm` and `results/disassembly/gcc-native-kernels.asm`, `elementwise_multiply_strided<float>`.

Raw data: `data/raw/phase4c_stride_raw.csv` and `data/raw/phase4c_stride_targeted_reruns.csv`. Correctness manifests: `data/processed/phase4c_stride_correctness.csv` and `data/processed/phase4c_stride_rerun_correctness.csv`. Enriched samples/statistics: `data/processed/phase4c_stride_samples.csv` and `data/processed/phase4c_stride_statistics.csv`. Rerun selection and summary: `data/metadata/phase4c_stride_rerun_selection.csv`, `results/tables/phase4c_stride_summary.csv`, and `results/tables/phase4c_stride_summary.md`. Six plots in `results/plots/` show ns/useful-element and useful effective bandwidth against stride for each span. Phase 4D and Phases 5A–5B are documented below; Phase 6 adds the final report and requirement audit without new measurements.

## Phase 3 Timing and Calibration

The benchmark uses `std::chrono::steady_clock` (monotonic). Each sample times only repeated kernel calls; allocation, deterministic initialization, AXPY reset, output checksum traversal, and CSV file I/O are outside the timed interval. A volatile checksum sink prevents dead-code elimination. Each process runs one benchmark thread pinned with `SetThreadAffinityMask` to logical CPU 0; the affinity mask is recorded in every raw sample. No OS-wide affinity, power, SMT, BIOS, or security setting was changed.

Each configuration receives 3 warmup batches. Full-matrix configurations use 10 measured repetitions, selected at the allowed maximum after pilot variability; all raw samples are preserved. Batching is 128 calls for `N <= 4096`, 32 calls for `N <= 65536`, and 1 otherwise. The batch count is recorded. The smallest full-matrix elapsed sample was 2.3 us; zero/nonpositive samples are rejected. All 24 kernel/type/build combinations passed the representative `N=1003` correctness check before collection.

## Pilot Calibration

Pilot scope: elementwise multiply only, float32/float64, GCC scalar/auto/native, and target logical working sets 4 KiB, 512 KiB, 2 MiB, 24 MiB, 48 MiB, and 128 MiB (36 configurations, 5 samples each, 180 timed samples). The corrected pilot is `data/raw/pilot_raw_v2.csv`; the earlier `pilot_raw.csv` is retained but excluded from calibration because benchmark-mode reference buffers were initially resident. No pilot values were discarded.

The corrected pilot's median per-configuration CV was 6.57%, maximum 28.82%, and shortest median elapsed sample 1.3 us. One targeted rerun of the highest-CV point (float64 GCC auto, 512 KiB target, batch 32) reduced CV from 28.82% to 1.51%; it remains separate in `pilot_v2_targeted_rerun_raw.csv`. An earlier pre-fix batch calibration rerun also remains preserved. Because other pilot configurations exceeded 10% CV, full-matrix repetitions were raised to 10, not beyond the user's cap. See `results/tables/pilot_summary_v2.md`.

## Working-Set Sweep

The full sweep uses exactly 15 target footprints: 8 KiB, 24 KiB, 64 KiB, 256 KiB, 1 MiB, 4 MiB, 8 MiB, 16 MiB, 24 MiB, 32 MiB, 40 MiB, 48 MiB, 64 MiB, 96 MiB, and 128 MiB. The points are log-spaced with additional sampling around reported L2/L3 scales (Windows reports 16 MiB aggregate L2 and 64 MiB L3). They span small/cache-scale through beyond-LLC/DRAM-sensitive footprints without claiming an exact cache boundary.

Full matrix: four kernels × two datatypes × three GCC builds × 15 footprints × 10 repetitions = **3,600 timed samples**. The count was printed and checked against the 4,000 cap before collection. Raw input, output, and any scratch arrays are not included in the timed region; footprint bytes are the kernel's logical arrays.

## Datatype
Both float32 and float64 were measured in every kernel/build/working-set combination. Do not assume one datatype is faster; compare the measured tables and account for variability.

## Phase 4A Alignment

Scope is restricted to AXPY and elementwise multiplication; float32 and float64; GCC scalar, auto-vectorized, and native-targeted builds; and the three existing Phase 3 target working sets: 24,576 B, 25,165,824 B, and 134,217,728 B. Each target size is divided by active arrays times `sizeof(T)` and rounded down to select N. The target and actual active-array byte counts are both recorded.

Each active buffer comes from `AlignedBuffer<T>` with a 64-byte-aligned base and extra capacity for the offset. All participating pointers use the same element offset:

| Condition | float32 offset | float32 mod 64 | float64 offset | float64 mod 64 |
|---|---:|---:|---:|---:|
| 64-byte aligned | 0 elements / 0 B | 0 | 0 elements / 0 B | 0 |
| One element offset | 1 element / 4 B | 4 | 1 element / 8 B | 8 |
| Cache-line crossing | 15 elements / 60 B | 60 | 7 elements / 56 B | 56 |

The crossing pointer begins one element before a 64-byte boundary. Every x/y/output pointer residue is checked against the configured condition, and each individual benchmark process compares the kernel result with the independent reference before warmups or timing. All 108 configurations passed this gate.

The initial matrix has 2 kernels × 2 datatypes × 3 builds × 3 working sets × 3 conditions = 108 configurations and 540 timed samples at five repetitions. There are three warmups. A single additional five-repetition run was permitted for configurations whose initial CV exceeded 20%; 35 configurations were selected, adding 175 rows. Initial and rerun raw files are separate, for 715 total observations and at most 10 observations per configuration. The build order rotates across conditions/sizes. Batching is 128 calls for `N <= 4096`, 32 for `N <= 65536`, and one otherwise. The benchmark thread is pinned to logical CPU 0.

The timer is `std::chrono::steady_clock`. Allocation, deterministic initialization, AXPY destination reset, correctness comparison, checksum traversal, and CSV I/O are outside the timed region. The timed section contains only repeated kernel calls. Raw samples record timestamps, compiler/flags, N, target/actual working-set bytes, exact offsets, pointer residues, repetition, batch, elapsed time, derived useful-work metrics, correctness status, and affinity.

Overhead is `(offset median ns/element / aligned median ns/element - 1) * 100`; SIMD speedup is scalar median / vector-build median at the same condition. The 72 measured offset-vs-aligned contrasts ranged from -59.67% to +52.25%. The maximum positive contrast was native float32 elementwise multiplication at the intermediate working set; its offset CV was 55.85%. Overall median configuration CV was 12.93%, maximum 120.59%, and 31/108 configurations remained above 20% CV after the targeted reruns. The measurements therefore do not establish a stable universal alignment penalty or benefit. Comparisons with high CV must be treated as inconclusive; no points were repeatedly rerun to seek a preferred result.

Raw files: `data/raw/phase4a_alignment_raw.csv` and `data/raw/phase4a_alignment_targeted_reruns.csv`. Selection manifest: `data/metadata/phase4a_alignment_rerun_selection.csv`. Statistics and derived overheads: `data/processed/phase4a_alignment_statistics.csv` and `results/tables/phase4a_alignment_overhead.csv`; summary: `results/tables/phase4a_alignment_summary.md`. Separate AXPY and elementwise plots are in `results/plots/phase4a_alignment_overhead_axpy.png` and `results/plots/phase4a_alignment_overhead_elementwise_multiply.png`. Phase 4B tail handling is documented below; Phase 4C, Phase 5, and Phase 6 remain unstarted.

## Phase 4B Tail Handling

Scope is AXPY, float32, and GCC scalar/auto/native only. The two bases are N=3,072 (24 KiB logical AXPY working set) and N=524,288 (4 MiB). Each base is divisible by 16; testing N=base+r for r=0..15 covers every native 16-float remainder and all 4-float auto-vector remainder classes. The 4 MiB point is cache-resident within the host's 64 MiB L3; no working-set sweep was run.

Phase 2 object code, not processor capability, establishes the tested widths. GCC scalar uses a scalar loop. GCC auto AXPY uses 128-bit XMM `mulps`/`addps` for four floats, then shorter-vector/scalar cleanup. GCC native uses 512-bit ZMM packed FMA for sixteen floats and a masked ZMM epilogue for the remaining elements, with a scalar fallback path in the dispatch/versioning structure. See `results/disassembly/gcc-auto-kernels.asm`, `results/disassembly/gcc-native-kernels.asm`, and `results/tables/simd_verification.md`.

The validated Phase 3 `benchmark_runner` was reused unchanged. Its `std::chrono::steady_clock` timed region includes repeated AXPY calls only; allocation, deterministic initialization, per-repetition y reset, checksum traversal, and file I/O stay outside the timer. Each process pins one thread to logical CPU 0. There are three warmups and five initial repetitions. The small base uses 128 calls per batch; the larger base uses one. A verification-only reference check with the existing float32 tolerances ran for every one of the 96 build/base/remainder configurations before timing. The correctness manifest records maximum absolute/relative errors and PASS status.

The initial matrix contains 2 bases × 16 remainders × 3 builds = 96 configurations and 480 timed samples. Initial CV >20% selected 14 configurations for one additional five-repetition run (70 rows), producing 550 observations total and never more than 10 observations/configuration. Initial and targeted raw data remain separate. The runner stores N and repetitions; the processed sample file explicitly adds base N, remainder, correctness status, observed lane count, and measurement source. Batching and the number of repetitions are recorded per row.

For each build/base, normalized overhead is `(median elapsed_ns at base+r / median elapsed_ns at base - 1) * 100`; median ns/element and GFLOP/s are also reported. Final CV median/max was 2.56%/111.10%; 25/96 configurations exceeded 10% CV and 13/96 remained above 20%. Normalized overhead ranged from -50.416% to +64.676% across all builds/bases. Native ranged from -36.885% to +13.934% at the small base and -16.225% to +47.848% at the larger base. At r=15, the added element count alone is 0.488% of the small base and 0.0029% of the larger base. The observed variation is much larger, the curves are non-monotonic, and native does not show a consistent positive excess over scalar/auto. No systematic native tail penalty was resolved; these measurements are inconclusive, not proof of zero cost.

Remainders were run in ascending order and each build/configuration used a separate process. This is not a fully interleaved design; the time/frequency drift identified in Phase 3B can confound comparisons. No additional repetitions were used beyond the single CV-threshold rerun.

Raw data: `data/raw/phase4b_tail_raw.csv` and `data/raw/phase4b_tail_targeted_reruns.csv`. Correctness manifests: `data/processed/phase4b_tail_correctness.csv` and `data/processed/phase4b_tail_rerun_correctness.csv`. Enriched samples and statistics: `data/processed/phase4b_tail_samples.csv` and `data/processed/phase4b_tail_statistics.csv`. Selection and outputs: `data/metadata/phase4b_tail_rerun_selection.csv`, `results/tables/phase4b_tail_overhead.csv`, and `results/tables/phase4b_tail_summary.md`. Plots: `results/plots/phase4b_tail_overhead_small_cache.png` and `results/plots/phase4b_tail_overhead_larger_cache.png`.

## Stride
Phase 4C measured float32 fixed-span elementwise multiply at strides 1, 2, 4, and 8 for GCC scalar/auto/native over three allocated spans. It collected 180 initial and 65 targeted-rerun observations. Non-unit stride took scalar runtime paths in auto/native disassembly; useful bandwidth fell with stride, with residual variability documented in the Phase 4C summary.

## Phase 5A Representative AMD uProf

Scope is nine process-level profiles of float32 elementwise multiply: GCC scalar/auto/native at 24,576 B (`N=2,048`), 25,165,824 B (`N=2,097,152`), and 134,217,728 B (`N=11,184,810`) Phase 3B target working sets. This is a representative set, not a sweep. Each profiled `benchmark_runner` used three warmup batches; the profile collection repetitions were 1,000 at small span with batch 128, 100 at intermediate span with batch 1, and 10 at large span with batch 1. The harness was pinned to logical CPU 0; uProf was also invoked with `--affinity 0`.

AMD uProf CLI 5.3.521.0 used a custom six-core-PMC event bundle, each sampled at interval 250,000: `CYCLES_NOT_IN_HALT` (PMCx076), `RETIRED_INST` (PMCx0C0), one build-specific FP-uop event (`SCALAR_UOPS_RETIRED` PMCx008/0x04; `PACK_128_UOPS_RETIRED` PMCx008/0x08; or `PACK_512_UOPS_RETIRED` PMCx008/0x20), `L1_DC_ACCESSES_ALL` (PMCx029/0x07), `L2_CACHE_ACCESS_FROM_L1_DC_MISS` (PMCx060/0xE0), and `L1_DTLB_MISSES` (PMCx045/0xFF). uProf reports IPC/CPI as retired instructions/cycles and cycles/instructions. The exact per-case command and output locations are in `results/uprof/phase5a/command_manifest.csv`.

All nine valid profiles completed and retain raw databases, report exports, and profiler-instrumented timing CSVs beneath `results/uprof/phase5a/`. The first two smoke attempts exposed CLI issues: uProf rejects combining predefined `--config cpi` with custom events, and a subsequent invocation lacked the harness CSV. Those attempts remain recorded; they are not included in the nine-case summary. The valid run set uses custom events only, whitespace-free metadata tokens in the launched program arguments, and checks for raw DB, report, and harness CSV before marking a case complete.

The uProf report aggregates the entire target process, not just timed kernel calls. Consequently, `process_cycles_per_useful_update`, `process_instructions_per_useful_update`, and event rates include allocation/initialization, warmups, checksums, and runtime overhead; they are architectural context rather than kernel-exclusive cycles/element. Event counts are sampled at the 250,000 interval; zero or sparse L1 DTLB samples do not prove the underlying event never occurred. FP-uop events are width-specific categories and are not interchangeable instruction counts. The Phase 3B median runtime, ns/element, speedup, and useful effective bandwidth remain the performance cross-check; profiler timings do not replace them.

Phase 3B comparisons show small-span speedups of 3.318x auto and 6.138x native, intermediate speedups of 2.258x/2.652x, and large-span speedups of 0.947x/0.969x. uProf process counters show retired instructions/update and cycles/update generally rising at the large span, while IPC declines across scalar/auto/native from 2.336/1.365/0.983 at large span. The L2-request event per useful update rises from roughly 0.005–0.011 in the small case to approximately 0.196–0.210 at intermediate/large spans, consistent with more L1D-miss-related L2 requests. Its definition includes hardware/software prefetches; this is not a physical traffic rate or causal proof. Full measurements and Phase 3B links are in `results/tables/uprof_summary.md`, `results/tables/uprof_summary.csv`, and `docs/uprof_analysis.md`.

The host reports six core PMCs but no direct L3 PMCs, DF/UMC counters, or memory-controller bandwidth counters. No L3 miss rate, physical DRAM bandwidth, exact cache residency, or DRAM saturation is reported. Phase 5B reuses the Phase 3B measurements for a useful-byte roofline-style synthesis; no new uProf profiles are included.

## Effective bandwidth
Compute known useful logical bytes / measured runtime and call it **effective bandwidth**. This is not direct memory-controller or DRAM bandwidth. Per call: AXPY `3*N*sizeof(T)` (read x, read/write y); dot product `2*N*sizeof(T)` (read x and y); elementwise multiply `3*N*sizeof(T)` (two reads and one write); stencil uses `4*(N-2)+4` elements for `N>=2` (three input values and one output for interiors; copied endpoints read/write once), and two elements for `N=1`. Operations per call: 2N for AXPY/dot, N for elementwise multiply, and `5*(N-2)` for stencil when N>=2. Batch multiplies both totals.

`phase3_raw_v3.csv` is the canonical timestamped measurement file. `phase3_samples_corrected.csv` preserves those elapsed values and recalculates only operations, useful bytes, GFLOP/s, and effective GiB/s using the exact stencil endpoint convention. `phase3_raw.csv` is retained as superseded because it initialized inactive buffers; `phase3_raw_v2.csv` is retained as partial because a large float32 dot correctness gate stopped it. Neither is mixed into v3 statistics.

## Arithmetic Intensity

Arithmetic intensity is useful floating-point operations divided by useful algorithmic bytes. Counts are per useful element and exclude cache-line overfetch, write allocation, and other physical traffic.

| Kernel | FLOPs/useful element | Useful logical bytes/useful element, float32 | Intensity, float32 | Useful logical bytes/useful element, float64 | Intensity, float64 |
|---|---:|---:|---:|---:|---:|
| AXPY | 2 (multiply + add) | 12 | 0.166667 | 24 | 0.083333 |
| Dot product | 2 (multiply + accumulate add) | 8 | 0.250000 | 16 | 0.125000 |
| Elementwise multiply | 1 (multiply) | 12 | 0.083333 | 24 | 0.041667 |
| Three-point stencil | 5 interior (3 multiplies + 2 adds) | 16 asymptotic | 0.312500 | 32 asymptotic | 0.156250 |

For the stencil with N>=2, useful bytes are `(4N-4)*sizeof(T)` including interior input/output accesses and copied endpoints; useful operations are `5*(N-2)`. Thus finite-N intensity is `5*(N-2)/((4N-4)*sizeof(T))`; the table gives the large-N limit. Endpoint copies have no floating-point operation. These bytes count the stated logical accesses, not actual cache or memory-controller traffic.

## Phase 5B Roofline-Style Analysis

No new benchmark was necessary. The existing Phase 3B 128 MiB GCC-native effective bandwidths for AXPY, elementwise multiply, and stencil provide a per-datatype useful streaming-bandwidth reference: median 36.965 GiB/s float32 and 39.044 GiB/s float64. The component values vary (float32 24.519–49.457 GiB/s; float64 28.443–47.552 GiB/s), so this reference is a summary of useful bytes/time from three different kernels, not a measured copy ceiling or physical DRAM bandwidth.

The estimated theoretical single-core compute ceiling assumes the Windows CIM-reported 4.3 GHz maximum clock and one 512-bit vector FMA per core cycle. With observed GCC-native widths of 16 float32 or 8 float64 lanes and two FLOPs per FMA, ceilings are 137.6 and 68.8 GFLOP/s. The frequency is not a measured sustained/AVX-512 frequency, and issue throughput is an explicit assumption. Phase 2 observed packed FMA in native AXPY/stencil, but not in elementwise multiply or dot; therefore this common FMA peak is an optimistic theoretical upper bound for non-FMA/reduction kernels, not a measured or kernel-specific ceiling.

The roofline-style comparison uses `P_roof = min(P_compute, AI * BW_reference)`, converting useful GiB/s to decimal GB/s for GFLOP/s. It plots Phase 3B native achieved GFLOP/s at 24 KiB, 24 MiB, and 128 MiB against the useful-byte arithmetic intensities above. Scalar/auto/native Phase 3B rows and all derived values are retained in `results/tables/roofline_summary.csv`.

The bandwidth line is the large-working-set effective reference, not a cache-level ceiling. Cache-resident points may exceed it; this is not a contradiction and does not justify a multi-level physical roofline. Elementwise float32 native speedup compresses from 6.1375x at 24 KiB to 2.6522x at 24 MiB and 0.9694x at 128 MiB. Phase 5A counters show process-level instructions/update fall from 1.329 to 0.900 then rise to 3.281, IPC falls 2.618 to 1.113 to 0.983, and L2 requests/useful-update rise 0.00475 to 0.1956 to 0.2063. Given their process-level scope and the large Phase 3B CV (23.41% native), these observations are consistent with increasing data-supply pressure and reduced arithmetic-side benefit, not direct proof of L3/DRAM saturation.

512-bit native vectors provide 4x the float lane width of 128-bit auto vectors and 16x scalar float lanes, but speedup does not scale with lane ratio. Useful intensity, arithmetic mix (FMA versus multiply-only), reduction dependencies, fixed single-core data supply, working-set behavior, and compiler-selected paths all matter. Phase 4C further demonstrates that non-unit strides use scalar paths in both GCC auto/native, regardless of the native ISA target.

Outputs are `results/plots/roofline.png`, `results/tables/roofline_summary.md`, `results/tables/roofline_summary.csv`, and `docs/roofline_analysis.md`. This is an algorithmic useful-byte roofline-style analysis, not a physical DRAM roofline. No write-allocate, actual physical traffic, exact cache residency, or directly measured bandwidth ceiling is claimed.

## Phase 4D Negative Cases and Benchmark Pitfalls

This phase consolidates existing measurements and Phase 2 object-code evidence only; it adds no benchmark runs.

**Vectorized but little large-span speedup.** At the 134,217,728-byte float32 elementwise-multiply working set (`N=11,184,810`), Phase 3B median time was 0.441871610 ns/element scalar and 0.455823568 ns/element native, for native speedup 0.969392x. Useful effective bandwidth was 25.300 versus 24.519 GiB/s. CV was 25.73% scalar and 23.41% native across ten observations; both use original v3 rows. Phase 2 reports and `gcc-native-kernels.asm` verify 512-bit ZMM `vmulps` (16 float lanes) and masked ZMM cleanup. The loop is vectorized, but widening arithmetic did not yield a substantial speedup at this large working set. This is consistent with memory/data-supply limits, not proof of direct DRAM saturation; no Phase 5 roofline/controller evidence exists.

**Native target with a scalar runtime path.** Phase 4C shows GCC auto/native packed XMM/ZMM paths only when all three strides are one. For strides 2, 4, and 8, both disassemblies branch to scalar `mulss`/`vmulss` loops. Small-span native/scalar speedup falls from 5.380x at stride 1 to 0.891x, 0.825x, and 0.714x at strides 2/4/8. At the intermediate span the ratios are 2.169x, 1.675x, 0.864x, and 0.865x; at the large span they are 1.208x, 1.099x, 0.957x, and 1.383x. The last result has scalar CV 31.90%, so it is noisy and does not indicate packed SIMD. The scalar fallback and reduced useful cache-line utilization both matter; do not call this a cache-only effect. See `results/tables/phase4c_stride_summary.csv`, `results/disassembly/gcc-auto-kernels.asm`, and `results/disassembly/gcc-native-kernels.asm`.

**Project-specific pitfalls.** `docs/benchmark_pitfalls.md` records seven evidence-linked lessons: compiler flags do not prove vectorization; wider vectors do not guarantee speedup; non-unit stride can select scalar code; useful/effective bandwidth is not physical DRAM traffic; alignment/tail differences can be obscured by noise; high-CV samples must not be hidden by deletion; and a valid reduction error bound can still be practically non-informative. The complete case table is `results/tables/negative_cases.md` with machine-readable rows in `results/tables/negative_cases.csv`.

No new measurements, direct memory-bandwidth claims, roofline analysis, or broad uProf runs were performed for Phase 4D. Representative uProf profiles are documented in Phase 5A above; the Phase 5B roofline synthesis is documented above and does not add measurements.

## Phase 3 Results and Limitations
The final v3 matrix contained 3,600 samples (4 kernels × 2 datatypes × 3 GCC builds × 15 working sets × 10 repetitions). Configuration CV median was 11.47%, maximum 94.25%; 198/360 configurations exceeded 10%. The highest-CV configuration (stencil float32, GCC auto, 24 KiB target) was rerun exactly once; CV decreased from 94.25% to 0.82%. Both raw sets are retained; no outlier was discarded. Review `results/tables/phase3_anomalies.md`.

The runner's representative correctness gate passed at N=1003 for all kernel/type/build combinations. Verify-only probes of very large dot products show float32 differences from the long-double reference beyond the Phase 1 tight tolerance (up to 1.76% relative at N=16,777,216) across the build variants, consistent with accumulated sequential-reduction rounding/cancellation. Tolerances were not loosened. Therefore, large-N dot-product timings are reported, but equivalent-accuracy at those sizes was not established and must not be implied.

Windows reports 16 MiB aggregate L2 and 64 MiB L3. Some measurements shift around 24–64 MiB, but variability also rises there. Interpret only as cache-resident behavior, intermediate transition, or large-working-set/DRAM-sensitive behavior; direct L3/DF/UMC counters are unavailable and no exact L3 boundary is claimed. Phase 4A alignment, Phase 4B tail, Phase 4C stride, Phase 4D negative-case evidence, and Phase 5A–5B analyses are documented above. No broad uProf sweep or Phase 6 work has been performed.

## Phase 3B Variability Diagnosis and Selective Reruns

The v3 raw file confirms process/thread affinity was set for every sample (`logical_cpu_0;mask=0x1`), the harness uses one thread, batching was recorded, and allocation/initialization/checksum/file I/O were outside timed regions. Timer samples were positive (minimum 2.2 us). The original v3 loop measured 10 repetitions of a build consecutively, in scalar→auto→native order; this can confound build comparisons with transient scheduling/frequency state. Repetition-position analysis found median first-to-last drift of -1.68% scalar, -4.90% auto, and -7.12% native; 48/120, 48/120, and 66/120 configs respectively had >10% absolute first/last drift.

Windows telemetry observed logical CPU 0 actual frequency from approximately 4.76–5.22 GHz across five short idle samples (% maximum 86–100%). The system processor queue was zero in those samples while context-switch rate was nonzero. This supports dynamic frequency/background scheduling as plausible contributors, but does not establish causality for any individual timed outlier; no settings or services were changed. CV was elevated at both some small points and larger 24–100 MiB footprints; AXPY/elementwise/stencil were noisier than dot, and native was noisier than scalar in this dataset. See `results/tables/phase3_variability_diagnostic.md`.

The bounded rerun policy selected the top 40 of 117 configurations with CV >20%, stratified by the score ranking across kernels, datatypes, builds, and sizes. One rerun per selected config used the same N, batch, 3 warmups, and 10 repetitions; order rotated native→auto→scalar. Original v3 data remain unchanged. Phase 3B substitutes rerun rows only for selected configurations and uses original v3 rows everywhere else; provenance is in `phase3b_samples.csv` and exact comparisons in `phase3b_rerun_comparison.csv`.

After substitution, median CV was 10.40%, max CV 111.85%, with 190/360 above 10% and 100/360 above 20% (original v3: 11.47%, 94.25%, 198/360, 117/360). Thirty-one rerun medians shifted by at least 5%; 12 selected configurations crossed the scalar/vector speedup ratio of 1.0. Residual high-CV points remain unstable and must be shown with uncertainty; no further repetitions were used to seek preferred results. See `results/tables/phase3b_summary.md`.

### Dot-Product Error Bound

For dot product, let `u=epsilon(T)/2`, `S=sum_i |x_i*y_i|`, and `m=2N`, counting up to N product roundings and N reduction roundings; this covers scalar and compiler-dependent reduction orders conservatively. Use `gamma_m(u)=m*u/(1-m*u)` if `m*u<1`, otherwise use `(1+u)^m-1`. Include long-double reference/sum accumulation rounding by comparing with `(gamma_m(u_T)+gamma_m(u_LD))*S/(1-gamma_m(u_LD))`. The exact computed values, long-double reference, `S`, errors, bound parameters, and status are in `data/processed/dot_accuracy_phase3b_v4.csv`.

All 18 small/intermediate/largest points (float32/float64 × three GCC builds) were within that bound. Fifteen bounds are informative; the three largest float32 build cases (`N=16,777,216`) have relative error 1.764% and a valid bound larger than the reference magnitude, so they are labeled `pass_bound_noninformative`, not strong accuracy guarantees. No tolerance was loosened. See `results/tables/dot_accuracy_phase3b.md` and `data/processed/dot_accuracy_phase3b_v4.csv`.
