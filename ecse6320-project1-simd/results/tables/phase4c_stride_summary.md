# Phase 4C Fixed-Span Stride Measurements

- Scope: `elementwise_multiply_strided`, `float32`, GCC scalar/auto/native; 36 configurations.
- Initial data: `data/raw/phase4c_stride_raw.csv`; 180 timed samples.
- Targeted reruns: 65 rows in `data/raw/phase4c_stride_targeted_reruns.csv`; 13 configurations selected by initial CV >20%.
- Total observations: 245; maximum per configuration: 10.
- Fixed allocated spans are per input/output buffer; aggregate bytes include all three float32 arrays. Useful N is span_elements/stride. Allocated span remains fixed as stride changes.
- Initial CV median/max: 12.34% / 56.26%; >10%: 22/36; >20%: 13/36.
- Final CV median/max: 12.34% / 68.18%; >10%: 22/36; >20%: 11/36.
- Useful effective bandwidth counts only logical bytes (two useful float reads plus one useful float write per updated element). It is not physical memory bandwidth.
- Speedups are scalar median ns/useful-element divided by auto/native median ns/useful-element for the same span and stride.

## Fixed Spans

| Span | Elements/buffer | Bytes/buffer | Aggregate allocated bytes |
|---|---:|---:|---:|
| small_cache | 2,048 | 8,192 | 24,576 |
| intermediate_cache_scale | 2,097,152 | 8,388,608 | 25,165,824 |
| large_dram_sensitive | 11,184,808 | 44,739,232 | 134,217,696 |

## Results by Stride

| Span | Stride | Useful N | Build | Median ns/useful-element | Useful elements/s | Useful effective GiB/s | CV | Auto speedup | Native speedup |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| intermediate_cache_scale | 1 | 2,097,152 | gcc-auto | 0.11906624 | 8.42632e+09 | 94.1715 | 47.14% | 1.794x | - |
| intermediate_cache_scale | 2 | 1,048,576 | gcc-auto | 0.38561821 | 2.61543e+09 | 29.2298 | 68.18% | 1.178x | - |
| intermediate_cache_scale | 4 | 524,288 | gcc-auto | 0.42829514 | 2.33524e+09 | 26.0984 | 38.55% | 1.035x | - |
| intermediate_cache_scale | 8 | 262,144 | gcc-auto | 0.81100464 | 1.23304e+09 | 13.7803 | 6.78% | 1.015x | - |
| large_dram_sensitive | 1 | 11,184,808 | gcc-auto | 0.42152713 | 2.37238e+09 | 26.5134 | 19.47% | 1.084x | - |
| large_dram_sensitive | 2 | 5,592,404 | gcc-auto | 1.024318 | 9.76259e+08 | 10.9105 | 18.64% | 0.894x | - |
| large_dram_sensitive | 4 | 2,796,202 | gcc-auto | 1.7702584 | 5.64889e+08 | 6.31313 | 12.41% | 0.976x | - |
| large_dram_sensitive | 8 | 1,398,101 | gcc-auto | 4.1812787 | 2.40339e+08 | 2.686 | 30.61% | 1.079x | - |
| small_cache | 1 | 2,048 | gcc-auto | 0.047683716 | 2.09715e+10 | 234.375 | 2.41% | 3.960x | - |
| small_cache | 2 | 1,024 | gcc-auto | 0.20446777 | 4.89075e+09 | 54.6583 | 1.62% | 0.944x | - |
| small_cache | 4 | 512 | gcc-auto | 0.21972656 | 4.55111e+09 | 50.8626 | 3.85% | 0.917x | - |
| small_cache | 8 | 256 | gcc-auto | 0.2532959 | 3.94795e+09 | 44.1218 | 4.12% | 0.843x | - |
| intermediate_cache_scale | 1 | 2,097,152 | gcc-native | 0.098466873 | 1.01557e+10 | 113.499 | 9.02% | - | 2.169x |
| intermediate_cache_scale | 2 | 1,048,576 | gcc-native | 0.27122498 | 3.68698e+09 | 41.2052 | 15.43% | - | 1.675x |
| intermediate_cache_scale | 4 | 524,288 | gcc-native | 0.51259995 | 1.96394e+09 | 21.9487 | 33.85% | - | 0.864x |
| intermediate_cache_scale | 8 | 262,144 | gcc-native | 0.95081329 | 1.05348e+09 | 11.7735 | 39.60% | - | 0.865x |
| large_dram_sensitive | 1 | 11,184,808 | gcc-native | 0.37812898 | 2.6446e+09 | 29.5557 | 11.09% | - | 1.208x |
| large_dram_sensitive | 2 | 5,592,404 | gcc-native | 0.8336844 | 1.19949e+09 | 13.4054 | 12.66% | - | 1.099x |
| large_dram_sensitive | 4 | 2,796,202 | gcc-native | 1.8050913 | 5.53989e+08 | 6.1913 | 10.79% | - | 0.957x |
| large_dram_sensitive | 8 | 1,398,101 | gcc-native | 3.2622822 | 3.06534e+08 | 3.42578 | 12.27% | - | 1.383x |
| small_cache | 1 | 2,048 | gcc-native | 0.035095215 | 2.84939e+10 | 318.444 | 2.79% | - | 5.380x |
| small_cache | 2 | 1,024 | gcc-native | 0.2166748 | 4.61521e+09 | 51.579 | 3.38% | - | 0.891x |
| small_cache | 4 | 512 | gcc-native | 0.24414062 | 4.096e+09 | 45.7764 | 3.19% | - | 0.825x |
| small_cache | 8 | 256 | gcc-native | 0.29907227 | 3.34367e+09 | 37.3685 | 3.30% | - | 0.714x |
| intermediate_cache_scale | 1 | 2,097,152 | gcc-scalar | 0.21362305 | 4.69236e+09 | 52.4412 | 49.09% | - | - |
| intermediate_cache_scale | 2 | 1,048,576 | gcc-scalar | 0.45418739 | 2.20902e+09 | 24.6877 | 62.95% | - | - |
| intermediate_cache_scale | 4 | 524,288 | gcc-scalar | 0.44307709 | 2.25694e+09 | 25.2233 | 11.10% | - | - |
| intermediate_cache_scale | 8 | 262,144 | gcc-scalar | 0.8228302 | 1.21532e+09 | 13.5822 | 13.61% | - | - |
| large_dram_sensitive | 1 | 11,184,808 | gcc-scalar | 0.45688759 | 2.18933e+09 | 24.4677 | 19.07% | - | - |
| large_dram_sensitive | 2 | 5,592,404 | gcc-scalar | 0.91599248 | 1.09376e+09 | 12.2237 | 25.20% | - | - |
| large_dram_sensitive | 4 | 2,796,202 | gcc-scalar | 1.7281298 | 5.7866e+08 | 6.46703 | 33.93% | - | - |
| large_dram_sensitive | 8 | 1,398,101 | gcc-scalar | 4.5104753 | 2.21909e+08 | 2.48003 | 31.90% | - | - |
| small_cache | 1 | 2,048 | gcc-scalar | 0.18882751 | 5.29584e+09 | 59.1856 | 0.26% | - | - |
| small_cache | 2 | 1,024 | gcc-scalar | 0.19302368 | 5.18071e+09 | 57.899 | 2.72% | - | - |
| small_cache | 4 | 512 | gcc-scalar | 0.20141602 | 4.96485e+09 | 55.4865 | 5.40% | - | - |
| small_cache | 8 | 256 | gcc-scalar | 0.21362305 | 4.68114e+09 | 52.3158 | 4.86% | - | - |

## SIMD Evidence and Interpretation

Phase 2 GCC auto and native strided-multiply disassembly checks the runtime stride arguments. The packed XMM/ZMM path is guarded for unit strides; non-unit strides branch to scalar `mulss` loops. Therefore any loss of SIMD speedup for strides 2/4/8 reflects the emitted scalar path as well as lower useful cache-line utilization; it must not be attributed to cache behavior alone.

Per-span plots: ns/useful-element and useful effective bandwidth. Treat changes smaller than CV as unresolved. No negative-case consolidation, roofline, broad uProf, or Phase 4D work is included.

Statistics: `data/processed/phase4c_stride_statistics.csv`; merged rows with correctness/provenance: `data/processed/phase4c_stride_samples.csv`; rerun selection: `data/metadata/phase4c_stride_rerun_selection.csv`.
