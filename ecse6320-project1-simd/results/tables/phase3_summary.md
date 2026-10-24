# Phase 3 Core Performance Experiments

Measured results from the configured native Windows GCC matrix. Interpret noisy configurations cautiously; this is not a Phase 4/5 analysis.

- Raw timed samples: 3600 across 360 configurations.
- Working-set sizes: 15; target footprints: 8,192, 24,576, 65,536, 262,144, 1,048,576, 4,194,304, 8,388,608, 16,777,216, 25,165,824, 33,554,432, 41,943,040, 50,331,648, 67,108,864, 100,663,296, 134,217,728 bytes.
- Repetitions per configuration: 10; warmups: 3.
- Affinity: one benchmark thread pinned to logical CPU 0; recorded in each raw row.
- Main timing statistic: median; mean, standard deviation, minimum, maximum, and CV retained.
- Median configuration CV: 11.473%; maximum CV: 94.253%; above 10% CV: 198/360.
- All measurements use `std::chrono::steady_clock`; allocation, initialization, checksum traversal, and CSV writing are outside the timed interval.
- Effective bandwidth is useful logical bytes / measured time, not direct DRAM-controller bandwidth.
- Useful bytes per call: AXPY `3*N*sizeof(T)`; dot `2*N*sizeof(T)`; elementwise multiply `3*N*sizeof(T)`; stencil `4*(N-2)+4` elements for N>=2 and two elements for N=1.
- Canonical raw samples: `data/raw/phase3_raw_v3.csv`. `phase3_raw.csv` and partial `phase3_raw_v2.csv` are retained as superseded datasets; `phase3_samples_corrected.csv` preserves v3 elapsed samples and recalculates only derived operation/useful-byte/throughput fields for exact stencil endpoint accounting.
- No Phase 4 alignment/tail/stride/negative-case experiments, roofline analysis, or broad uProf collection were run.

## Conservative Working-Set Notes

Windows reports 16 MiB aggregate L2 and 64 MiB L3. Some kernels show broad changes around 24–64 MiB, but variability also rises in this region. The target footprint is the aggregate logical arrays for this single-thread workload. Treat behavior as cache-resident, intermediate-transition, or large-working-set/DRAM-sensitive only; no exact L3 boundary is inferred.

## Representative Measured Speedups

| Kernel | Type | Working set | Auto vs scalar | Native vs scalar |
|---|---|---|---:|---:|
| axpy | float32 | small (24,576 B) | 3.574x | 7.443x |
| axpy | float32 | intermediate (25,165,824 B) | 1.958x | 2.269x |
| axpy | float32 | large (134,217,728 B) | 0.953x | 1.017x |
| axpy | float64 | small (24,576 B) | 1.823x | 3.938x |
| axpy | float64 | intermediate (25,165,824 B) | 1.015x | 1.661x |
| axpy | float64 | large (134,217,728 B) | 1.046x | 1.114x |
| dot_product | float32 | small (24,576 B) | 1.003x | 0.968x |
| dot_product | float32 | intermediate (25,165,824 B) | 1.000x | 0.977x |
| dot_product | float32 | large (134,217,728 B) | 1.033x | 1.001x |
| dot_product | float64 | small (24,576 B) | 1.013x | 0.991x |
| dot_product | float64 | intermediate (25,165,824 B) | 0.966x | 0.995x |
| dot_product | float64 | large (134,217,728 B) | 1.038x | 1.069x |
| elementwise_multiply | float32 | small (24,576 B) | 3.912x | 6.137x |
| elementwise_multiply | float32 | intermediate (25,165,824 B) | 2.258x | 2.652x |
| elementwise_multiply | float32 | large (134,217,728 B) | 0.947x | 0.969x |
| elementwise_multiply | float64 | small (24,576 B) | 1.840x | 3.223x |
| elementwise_multiply | float64 | intermediate (25,165,824 B) | 1.323x | 0.847x |
| elementwise_multiply | float64 | large (134,217,728 B) | 0.948x | 1.102x |
| stencil_1d_three_point | float32 | small (24,576 B) | 2.594x | 4.342x |
| stencil_1d_three_point | float32 | intermediate (25,165,824 B) | 2.271x | 4.943x |
| stencil_1d_three_point | float32 | large (134,217,728 B) | 1.236x | 1.181x |
| stencil_1d_three_point | float64 | small (24,576 B) | 1.497x | 2.914x |
| stencil_1d_three_point | float64 | intermediate (25,165,824 B) | 2.157x | 3.169x |
| stencil_1d_three_point | float64 | large (134,217,728 B) | 0.941x | 1.055x |

Full representative tables are in `scalar_vs_simd.md` and `datatype_summary.md`; all measured configurations are in `phase3_statistics.csv` and raw samples remain in `data/raw/phase3_raw_v3.csv`.
