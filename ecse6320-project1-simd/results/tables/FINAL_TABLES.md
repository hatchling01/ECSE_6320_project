# Final Table Index

These existing tables provide the principal correctness, code-generation, performance, variability, profiling, and roofline evidence. Raw data and per-phase details remain available beside them.

| # | Table | Evidence |
|---:|---|---|
| 1 | [Correctness summary](correctness_summary.md) | Phase 1 case count, observed errors, and unchanged tolerances. |
| 2 | [SIMD verification matrix](simd_verification.md) | Compiler reports and packed/scalar instruction evidence by kernel and build. |
| 3 | [Phase 3B scalar-vs-SIMD](phase3b_scalar_vs_simd.md) | Full median times, speedups, throughput, and useful effective bandwidth. |
| 4 | [Phase 3B datatype summary](phase3b_datatype_summary.csv) | Median float32/float64 timings and derived metrics. |
| 5 | [Phase 3B residual anomalies](phase3b_anomalies.md) | High-CV configurations, medians, and sample provenance. |
| 6 | [Phase 3 variability diagnostic](phase3_variability_diagnostic.md) | Variability analysis and measurement caveats. |
| 7 | [Dot-product accuracy](dot_accuracy_phase3b.md) | N-dependent error-bound results and the non-informative largest float32 bound. |
| 8 | [Phase 4A alignment summary](phase4a_alignment_summary.md) | Alignment matrix and overhead contrasts. |
| 9 | [Phase 4B tail summary](phase4b_tail_summary.md) | Remainder matrix, normalized overhead, and variability. |
| 10 | [Phase 4C stride summary](phase4c_stride_summary.md) | Fixed-span stride performance, useful bandwidth, and speedups. |
| 11 | [Negative cases](negative_cases.md) | Measurement and disassembly evidence for two SIMD counterexamples. |
| 12 | [uProf summary](uprof_summary.md) | Nine representative profiles, process-level events, and limits. |
| 13 | [Roofline summary](roofline_summary.md) | Useful arithmetic intensity, bandwidth reference, and all 72 analyzed points. |