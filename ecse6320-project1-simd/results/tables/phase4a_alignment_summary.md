# Phase 4A Alignment Measurements

- Initial raw samples: `data/raw/phase4a_alignment_raw.csv` (540 rows); targeted rerun rows: 175.
- Summary: 108 configurations, 715 observations; initial repetitions 5, maximum per configuration 10; 3 warmups; logical CPU 0.
- One additional five-sample run was collected for 35 initial configurations with CV >20%; the separate file is `data/raw/phase4a_alignment_targeted_reruns.csv` and the selection is `data/metadata/phase4a_alignment_rerun_selection.csv`.
- Scope: AXPY and elementwise multiply, float32/float64, GCC scalar/auto/native, and the three selected Phase 3 working sets.
- Alignment states: 64-byte aligned; one element offset (4/8 B); cache-line crossing (60/56 B). All input/output pointer residues were validated and every measured case passed correctness.
- Median configuration CV: 12.933%; maximum CV: 120.594%; CV >10%: 61/108; CV >20%: 31/108.
- Alignment overhead is `(offset median ns/element / aligned median ns/element - 1) * 100`; negative values mean the offset case measured faster. Do not infer a causal benefit from small differences relative to CV.
- SIMD speedup is scalar median / vector-build median at the same condition. The change in speedup is reported relative to the aligned condition.
- Effective bandwidth is useful logical bytes/time, not measured memory-controller bandwidth. Phase 3 raw data and plots were not modified.

## Median Alignment Overhead

| Kernel | Type | Build | Condition | Size | Median overhead | CV aligned/offset |
|---|---|---|---|---|---:|---:|
| axpy | float32 | gcc-scalar | offset_one_element | small | -0.281% | 0.60% / 0.21% |
| axpy | float32 | gcc-scalar | cache_line_crossing | small | -0.140% | 0.60% / 15.59% |
| axpy | float32 | gcc-scalar | offset_one_element | intermediate | 6.334% | 8.08% / 46.05% |
| axpy | float32 | gcc-scalar | cache_line_crossing | intermediate | 3.428% | 8.08% / 5.19% |
| axpy | float32 | gcc-scalar | offset_one_element | large | -24.825% | 21.63% / 16.53% |
| axpy | float32 | gcc-scalar | cache_line_crossing | large | -28.390% | 21.63% / 17.52% |
| axpy | float32 | gcc-auto | offset_one_element | small | 17.588% | 23.31% / 1.63% |
| axpy | float32 | gcc-auto | cache_line_crossing | small | 19.598% | 23.31% / 8.92% |
| axpy | float32 | gcc-auto | offset_one_element | intermediate | 4.710% | 9.00% / 28.49% |
| axpy | float32 | gcc-auto | cache_line_crossing | intermediate | -4.216% | 9.00% / 12.80% |
| axpy | float32 | gcc-auto | offset_one_element | large | -3.631% | 20.57% / 14.55% |
| axpy | float32 | gcc-auto | cache_line_crossing | large | -8.680% | 20.57% / 16.54% |
| axpy | float32 | gcc-native | offset_one_element | small | 20.513% | 2.76% / 1.42% |
| axpy | float32 | gcc-native | cache_line_crossing | small | 19.231% | 2.76% / 1.90% |
| axpy | float32 | gcc-native | offset_one_element | intermediate | -19.491% | 120.59% / 37.43% |
| axpy | float32 | gcc-native | cache_line_crossing | intermediate | -0.107% | 120.59% / 16.72% |
| axpy | float32 | gcc-native | offset_one_element | large | -5.401% | 6.55% / 13.58% |
| axpy | float32 | gcc-native | cache_line_crossing | large | -18.897% | 6.55% / 24.14% |
| axpy | float64 | gcc-scalar | offset_one_element | small | 0.543% | 1.31% / 60.90% |
| axpy | float64 | gcc-scalar | cache_line_crossing | small | 0.000% | 1.31% / 0.56% |
| axpy | float64 | gcc-scalar | offset_one_element | intermediate | 8.203% | 14.32% / 36.79% |
| axpy | float64 | gcc-scalar | cache_line_crossing | intermediate | 12.433% | 14.32% / 13.80% |
| axpy | float64 | gcc-scalar | offset_one_element | large | -1.980% | 27.20% / 18.28% |
| axpy | float64 | gcc-scalar | cache_line_crossing | large | -21.956% | 27.20% / 15.19% |
| axpy | float64 | gcc-auto | offset_one_element | small | 18.357% | 1.02% / 1.82% |
| axpy | float64 | gcc-auto | cache_line_crossing | small | 15.942% | 1.02% / 1.80% |
| axpy | float64 | gcc-auto | offset_one_element | intermediate | 47.940% | 6.34% / 16.20% |
| axpy | float64 | gcc-auto | cache_line_crossing | intermediate | 11.569% | 6.34% / 21.58% |
| axpy | float64 | gcc-auto | offset_one_element | large | -3.045% | 19.49% / 8.40% |
| axpy | float64 | gcc-auto | cache_line_crossing | large | -11.536% | 19.49% / 19.05% |
| axpy | float64 | gcc-native | offset_one_element | small | 27.273% | 1.15% / 2.99% |
| axpy | float64 | gcc-native | cache_line_crossing | small | 29.870% | 1.15% / 2.14% |
| axpy | float64 | gcc-native | offset_one_element | intermediate | -39.117% | 48.28% / 120.49% |
| axpy | float64 | gcc-native | cache_line_crossing | intermediate | -42.602% | 48.28% / 11.88% |
| axpy | float64 | gcc-native | offset_one_element | large | 4.512% | 17.31% / 18.85% |
| axpy | float64 | gcc-native | cache_line_crossing | large | 8.063% | 17.31% / 21.54% |
| elementwise_multiply | float32 | gcc-scalar | offset_one_element | small | -0.825% | 1.85% / 0.90% |
| elementwise_multiply | float32 | gcc-scalar | cache_line_crossing | small | -0.619% | 1.85% / 1.29% |
| elementwise_multiply | float32 | gcc-scalar | offset_one_element | intermediate | 27.440% | 1.91% / 8.17% |
| elementwise_multiply | float32 | gcc-scalar | cache_line_crossing | intermediate | 5.522% | 1.91% / 17.91% |
| elementwise_multiply | float32 | gcc-scalar | offset_one_element | large | -21.962% | 32.21% / 13.07% |
| elementwise_multiply | float32 | gcc-scalar | cache_line_crossing | large | -5.427% | 32.21% / 24.28% |
| elementwise_multiply | float32 | gcc-auto | offset_one_element | small | 17.021% | 0.92% / 1.04% |
| elementwise_multiply | float32 | gcc-auto | cache_line_crossing | small | 14.184% | 0.92% / 1.48% |
| elementwise_multiply | float32 | gcc-auto | offset_one_element | intermediate | -25.232% | 38.73% / 24.43% |
| elementwise_multiply | float32 | gcc-auto | cache_line_crossing | intermediate | -41.003% | 38.73% / 8.79% |
| elementwise_multiply | float32 | gcc-auto | offset_one_element | large | -19.834% | 27.22% / 11.53% |
| elementwise_multiply | float32 | gcc-auto | cache_line_crossing | large | 3.118% | 27.22% / 28.53% |
| elementwise_multiply | float32 | gcc-native | offset_one_element | small | 39.130% | 4.94% / 5.25% |
| elementwise_multiply | float32 | gcc-native | cache_line_crossing | small | 41.304% | 4.94% / 3.27% |
| elementwise_multiply | float32 | gcc-native | offset_one_element | intermediate | 6.794% | 7.41% / 30.03% |
| elementwise_multiply | float32 | gcc-native | cache_line_crossing | intermediate | 52.246% | 7.41% / 55.85% |
| elementwise_multiply | float32 | gcc-native | offset_one_element | large | -0.013% | 10.45% / 16.94% |
| elementwise_multiply | float32 | gcc-native | cache_line_crossing | large | 7.955% | 10.45% / 37.89% |
| elementwise_multiply | float64 | gcc-scalar | offset_one_element | small | 0.000% | 2.33% / 2.10% |
| elementwise_multiply | float64 | gcc-scalar | cache_line_crossing | small | 3.968% | 2.33% / 0.21% |
| elementwise_multiply | float64 | gcc-scalar | offset_one_element | intermediate | -0.671% | 52.71% / 48.26% |
| elementwise_multiply | float64 | gcc-scalar | cache_line_crossing | intermediate | -57.230% | 52.71% / 10.56% |
| elementwise_multiply | float64 | gcc-scalar | offset_one_element | large | 23.989% | 13.14% / 25.04% |
| elementwise_multiply | float64 | gcc-scalar | cache_line_crossing | large | 13.219% | 13.14% / 26.68% |
| elementwise_multiply | float64 | gcc-auto | offset_one_element | small | 11.972% | 1.25% / 1.49% |
| elementwise_multiply | float64 | gcc-auto | cache_line_crossing | small | 14.085% | 1.25% / 2.27% |
| elementwise_multiply | float64 | gcc-auto | offset_one_element | intermediate | -59.672% | 18.64% / 8.81% |
| elementwise_multiply | float64 | gcc-auto | cache_line_crossing | intermediate | -58.649% | 18.64% / 7.96% |
| elementwise_multiply | float64 | gcc-auto | offset_one_element | large | 3.958% | 27.47% / 24.64% |
| elementwise_multiply | float64 | gcc-auto | cache_line_crossing | large | -4.163% | 27.47% / 16.40% |
| elementwise_multiply | float64 | gcc-native | offset_one_element | small | 33.333% | 5.16% / 3.22% |
| elementwise_multiply | float64 | gcc-native | cache_line_crossing | small | 35.417% | 5.16% / 5.48% |
| elementwise_multiply | float64 | gcc-native | offset_one_element | intermediate | 20.702% | 7.88% / 18.95% |
| elementwise_multiply | float64 | gcc-native | cache_line_crossing | intermediate | 5.227% | 7.88% / 12.60% |
| elementwise_multiply | float64 | gcc-native | offset_one_element | large | 2.898% | 8.44% / 25.73% |
| elementwise_multiply | float64 | gcc-native | cache_line_crossing | large | -5.133% | 8.44% / 11.11% |

## Highest Variability

| Kernel | Type | Build | Size | Alignment | Median ns/element | CV |
|---|---|---|---|---|---:|---:|
| axpy | float32 | gcc-native | intermediate | aligned_64B | 0.0887235 | 120.59% |
| axpy | float64 | gcc-native | intermediate | offset_one_element | 0.153828 | 120.49% |
| axpy | float64 | gcc-scalar | small | offset_one_element | 0.188192 | 60.90% |
| elementwise_multiply | float32 | gcc-native | intermediate | cache_line_crossing | 0.130892 | 55.85% |
| elementwise_multiply | float64 | gcc-scalar | intermediate | aligned_64B | 0.447512 | 52.71% |
| axpy | float64 | gcc-native | intermediate | aligned_64B | 0.25266 | 48.28% |
| elementwise_multiply | float64 | gcc-scalar | intermediate | offset_one_element | 0.444508 | 48.26% |
| axpy | float32 | gcc-scalar | intermediate | offset_one_element | 0.214005 | 46.05% |
| elementwise_multiply | float32 | gcc-auto | intermediate | aligned_64B | 0.162053 | 38.73% |
| elementwise_multiply | float32 | gcc-native | large | cache_line_crossing | 0.432251 | 37.89% |

Plots: `results/plots/phase4a_alignment_overhead_axpy.png` and `results/plots/phase4a_alignment_overhead_elementwise_multiply.png`.

Phase 4B (tails, stride, and negative case), Phase 5 (uProf/roofline), and Phase 6 are not included.
