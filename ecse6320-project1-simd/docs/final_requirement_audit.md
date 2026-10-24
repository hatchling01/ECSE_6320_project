# Final Requirement Audit

Status meanings: **COMPLETE** means the requested experiment or documentation exists with auditable evidence; **PARTIAL** means coverage exists but does not cover the full requested dimension; **LIMITATION** identifies an interpretation constrained by measurement noise or unavailable hardware counters. A limitation does not imply that a required experiment was skipped.

| Requirement | Status | Evidence and qualification |
|---|---|---|
| Scalar implementation and measurements | COMPLETE | GCC scalar variant, correctness, Phase 3 baseline and Phase 4 comparisons; [SIMD matrix](../results/tables/simd_verification.md), [Phase 3B comparison](../results/tables/phase3b_scalar_vs_simd.md). |
| Compiler auto-vectorization | COMPLETE | GCC and Clang reports and correctness; Clang strict-FP dot remains scalar. |
| CPU-targeted/native implementation | COMPLETE | GCC `-march=native`, resolved as `znver5`; packed ZMM paths verified where generated. |
| float32 and float64 | COMPLETE | Both types in the four-kernel Phase 3 matrix and Phase 4A alignment matrix; [datatype results](../results/tables/phase3b_datatype_summary.csv). |
| Four specified kernels | COMPLETE | AXPY, dot product, elementwise multiply, and 1D three-point stencil implemented, validated, and timed. |
| Correctness before timing | COMPLETE | Phase 1 passed 448 cases; later benchmark configurations have correctness preflights. Tolerances were not loosened. |
| Working-set sweep | COMPLETE | Fifteen Phase 3 targets span 8 KiB–128 MiB; exact cache/DRAM boundaries remain unresolved. |
| Alignment | COMPLETE | Phase 4A covers three pointer conditions, three GCC builds, both types, two kernels, and three spans. **LIMITATION:** residual CV and mixed contrasts do not resolve a stable penalty. |
| Vector tails | COMPLETE | Phase 4B covers all 16 float32 remainders for two AXPY bases and three builds. **LIMITATION:** no systematic penalty was resolved above variability. |
| Strides 1/2/4/8 | COMPLETE | Fixed-span Phase 4C matrix covers three builds and three spans. Non-unit auto/native paths are scalar in examined disassembly. |
| Compiler code-generation reports | COMPLETE | GCC and Clang compiler diagnostics are retained under `results/compiler_reports/`. |
| Targeted disassembly | COMPLETE | Per-variant kernel object disassembly and instruction evidence are retained under `results/disassembly/` and summarized in the SIMD matrix. |
| Representative performance counters | PARTIAL | Nine valid AMD uProf profiles collected six available core events for representative float32 elementwise cases. No L3, DF, UMC, or memory-controller counters were available. |
| Effective bandwidth | COMPLETE | Computed as useful logical bytes divided by elapsed time, explicitly not physical DRAM bandwidth. |
| Arithmetic intensity | COMPLETE | Useful FLOPs/useful logical bytes derived for each kernel and datatype; stencil finite-N convention is documented. |
| Roofline analysis | COMPLETE | Existing Phase 3B measurements reused in a useful-byte roofline-style synthesis. **LIMITATION:** the large-span reference is not a physical DRAM roof and the compute ceiling is estimated. |
| Negative case(s) | COMPLETE | Large-span packed elementwise case near 1x and scalar non-unit-stride execution paths, with data and disassembly evidence. |
| Variability and anomalies | COMPLETE | Raw observations retained; reruns source-labeled and bounded; anomalies and numerical limits documented. No samples were deleted. |
| Reproducibility | COMPLETE | Configuration, environment, raw data, analysis commands, CMake presets, and PowerShell execution-policy workaround documented. Final lightweight verification is recorded in the Phase 6 completion commit. |
| Tool/compiler versions | COMPLETE | Captured in [environment snapshot](environment.md) and metadata. |
| AI use disclosure | COMPLETE | [AI use statement](ai_use.md) identifies assistance and requires independent validation. |
| Data provenance and anomalies | COMPLETE | Canonical Phase 3 v3 data, superseded/partial predecessors, targeted reruns, uProf attempts, and dot-product accuracy limits are preserved and labeled. |

## Data Provenance

`data/raw/phase3_raw_v3.csv` is the canonical original Phase 3 matrix (3,600 rows). Earlier `phase3_raw.csv` is superseded and `phase3_raw_v2.csv` is partial; neither is merged into v3. Phase 3B selected 40 high-CV configurations for one targeted rerun and uses the rerun rows only for those configurations; the original v3 file remains unchanged, and the merged samples include source labels. Phase 4A–4C initial and rerun files remain separate. Analysis scripts consume existing raw/processed data; the Phase 5B generator confirms it reuses 72 Phase 3B points and performs no measurement. uProf retains one incomplete smoke attempt and one rejected CLI combination but excludes them from its nine-profile summary.

## Interpretation Boundaries

The host exposed six core PMCs and no L3/DF/UMC counters. Effective bandwidth is useful-byte/time, not physical traffic. No exact cache residency, physical DRAM bandwidth, L3 miss rate, or DRAM saturation is asserted. The roofline compute ceiling assumes one 512-bit FMA per cycle at the OS-reported 4.3 GHz maximum; it is not measured sustained frequency or throughput. High variability is disclosed alongside results, and close comparisons are not treated as resolved effects.