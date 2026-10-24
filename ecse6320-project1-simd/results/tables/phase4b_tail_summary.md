# Phase 4B Tail-Handling Measurements

- Initial configurations: 96; initial timed samples: 480.
- Initial raw samples: `data/raw/phase4b_tail_raw.csv`.
- Targeted raw samples: 70 rows in `data/raw/phase4b_tail_targeted_reruns.csv`.
- Scope: AXPY float32, GCC scalar/auto/native; N=base+r for r=0..15; bases N=3,072 (24 KiB) and N=524,288 (4 MiB).
- Actual emitted widths from Phase 2: scalar 1 float/iteration; GCC auto 128-bit XMM (4 floats); GCC native 512-bit ZMM (16 floats). The native disassembly shows a masked ZMM epilogue plus a scalar fallback path; the auto disassembly shows vector chunks and scalar/short-vector cleanup.
- Timing: 5 initial repetitions, 3 warmups, CPU affinity logical CPU 0; small base batch 128, larger base batch 1. Maximum observations/configuration: 10.
- Correctness: every timed configuration passed its verification-only reference check with existing float32 tolerances; see `data/processed/phase4b_tail_correctness.csv`.
- Initial CV median/max: 2.56% / 116.21%; CV >10%: 25/96; CV >20% and rerun: 14.
- Final CV median/max: 2.56% / 111.10%; CV >10%: 25/96; CV >20%: 13/96.
- Measured normalized overhead across builds/bases/remainders: -50.416% to 64.676%. Native: small -36.885% to 13.934%; larger -16.225% to 47.848%.
- At r=15, added elements are 0.488% of the small base and 0.0029% of the larger base; this is the expected first-order work increase before any cleanup cost.
- No systematic positive native tail penalty was resolved: native overhead is non-monotonic across remainders, changes sign, and is not consistently larger than scalar/auto. The sample variability exceeds the expected added-work share; the result is inconclusive, not evidence of zero cost.
- Remainders were collected in ascending order, with each build/configuration in a separate process rather than a fully interleaved sequence. Given Phase 3B's observed time/frequency drift, this ordering is an additional limitation on causal interpretation.
- Compare `normalized_time_overhead_percent` for the requested ratio and `median_ns_per_element` for per-element cost. No penalty is claimed unless the effect is consistent and larger than the observed variability.

## Remainder Statistics

| Base | Build | r | N | Median elapsed (ns) | Median ns/element | GFLOP/s | CV | Tail overhead |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| small_cache | gcc-scalar | 0 | 3072 | 72100 | 0.18335978 | 10.908 | 50.43% | 0.000% |
| small_cache | gcc-scalar | 1 | 3073 | 73000 | 0.18558819 | 10.777 | 0.06% | 1.248% |
| small_cache | gcc-scalar | 2 | 3074 | 71900 | 0.18273219 | 10.945 | 0.59% | -0.277% |
| small_cache | gcc-scalar | 3 | 3075 | 72100 | 0.18318089 | 10.918 | 15.83% | 0.000% |
| small_cache | gcc-scalar | 4 | 3076 | 71500 | 0.18159745 | 11.013 | 0.23% | -0.832% |
| small_cache | gcc-scalar | 5 | 3077 | 72600 | 0.18433133 | 10.85 | 0.18% | 0.693% |
| small_cache | gcc-scalar | 6 | 3078 | 71800 | 0.1822409 | 10.974 | 0.25% | -0.416% |
| small_cache | gcc-scalar | 7 | 3079 | 73300 | 0.18598774 | 10.753 | 4.54% | 1.664% |
| small_cache | gcc-scalar | 8 | 3080 | 72600 | 0.18415179 | 10.861 | 0.33% | 0.693% |
| small_cache | gcc-scalar | 9 | 3081 | 72400 | 0.18358488 | 10.894 | 0.19% | 0.416% |
| small_cache | gcc-scalar | 10 | 3082 | 71400 | 0.18099043 | 11.05 | 0.51% | -0.971% |
| small_cache | gcc-scalar | 11 | 3083 | 71300 | 0.18067832 | 11.069 | 0.67% | -1.110% |
| small_cache | gcc-scalar | 12 | 3084 | 71400 | 0.18087305 | 11.057 | 0.98% | -0.971% |
| small_cache | gcc-scalar | 13 | 3085 | 71600 | 0.18132091 | 11.03 | 0.19% | -0.693% |
| small_cache | gcc-scalar | 14 | 3086 | 70400 | 0.17822424 | 11.222 | 5.07% | -2.358% |
| small_cache | gcc-scalar | 15 | 3087 | 72200 | 0.1827219 | 10.946 | 2.47% | 0.139% |
| larger_cache | gcc-scalar | 0 | 524288 | 98800 | 0.18844604 | 10.613 | 2.79% | 0.000% |
| larger_cache | gcc-scalar | 1 | 524289 | 128100 | 0.24433089 | 8.1856 | 10.26% | 29.656% |
| larger_cache | gcc-scalar | 2 | 524290 | 162700 | 0.31032444 | 6.4449 | 19.49% | 64.676% |
| larger_cache | gcc-scalar | 3 | 524291 | 108200 | 0.20637394 | 9.6911 | 2.41% | 9.514% |
| larger_cache | gcc-scalar | 4 | 524292 | 100400 | 0.19149634 | 10.444 | 0.24% | 1.619% |
| larger_cache | gcc-scalar | 5 | 524293 | 116900 | 0.22296693 | 8.9699 | 60.60% | 18.320% |
| larger_cache | gcc-scalar | 6 | 524294 | 115600 | 0.22048698 | 9.0708 | 8.31% | 17.004% |
| larger_cache | gcc-scalar | 7 | 524295 | 106800 | 0.20370211 | 9.8183 | 1.42% | 8.097% |
| larger_cache | gcc-scalar | 8 | 524296 | 99500 | 0.18977829 | 10.539 | 1.00% | 0.709% |
| larger_cache | gcc-scalar | 9 | 524297 | 106900 | 0.20389207 | 9.8091 | 1.55% | 8.198% |
| larger_cache | gcc-scalar | 10 | 524298 | 109700 | 0.20923215 | 9.5588 | 10.37% | 11.032% |
| larger_cache | gcc-scalar | 11 | 524299 | 118250 | 0.22553924 | 8.8688 | 21.30% | 19.686% |
| larger_cache | gcc-scalar | 12 | 524300 | 104700 | 0.19969483 | 10.015 | 5.24% | 5.972% |
| larger_cache | gcc-scalar | 13 | 524301 | 110500 | 0.2107568 | 9.4896 | 2.58% | 11.842% |
| larger_cache | gcc-scalar | 14 | 524302 | 96100 | 0.18329131 | 10.912 | 1.31% | -2.733% |
| larger_cache | gcc-scalar | 15 | 524303 | 105900 | 0.20198244 | 9.9839 | 25.94% | 7.186% |
| small_cache | gcc-auto | 0 | 3072 | 21400 | 0.054423014 | 36.749 | 1.59% | 0.000% |
| small_cache | gcc-auto | 1 | 3073 | 20200 | 0.05135454 | 38.945 | 2.55% | -5.607% |
| small_cache | gcc-auto | 2 | 3074 | 20100 | 0.051083686 | 39.151 | 0.27% | -6.075% |
| small_cache | gcc-auto | 3 | 3075 | 19900 | 0.050558943 | 39.558 | 1.09% | -7.009% |
| small_cache | gcc-auto | 4 | 3076 | 20100 | 0.051050471 | 39.177 | 1.11% | -6.075% |
| small_cache | gcc-auto | 5 | 3077 | 21000 | 0.05331898 | 37.51 | 0.72% | -1.869% |
| small_cache | gcc-auto | 6 | 3078 | 20000 | 0.050763483 | 39.398 | 1.11% | -6.542% |
| small_cache | gcc-auto | 7 | 3079 | 19900 | 0.050493261 | 39.609 | 0.87% | -7.009% |
| small_cache | gcc-auto | 8 | 3080 | 20100 | 0.050984172 | 39.228 | 1.63% | -6.075% |
| small_cache | gcc-auto | 9 | 3081 | 20200 | 0.051221194 | 39.046 | 111.10% | -5.607% |
| small_cache | gcc-auto | 10 | 3082 | 20200 | 0.051204575 | 39.059 | 1.39% | -5.607% |
| small_cache | gcc-auto | 11 | 3083 | 21300 | 0.05397543 | 37.054 | 1.67% | -0.467% |
| small_cache | gcc-auto | 12 | 3084 | 20050 | 0.050791383 | 39.377 | 20.72% | -6.308% |
| small_cache | gcc-auto | 13 | 3085 | 21200 | 0.053687196 | 37.253 | 1.59% | -0.935% |
| small_cache | gcc-auto | 14 | 3086 | 20100 | 0.050885045 | 39.304 | 0.82% | -6.075% |
| small_cache | gcc-auto | 15 | 3087 | 20100 | 0.050868562 | 39.317 | 0.96% | -6.075% |
| larger_cache | gcc-auto | 0 | 524288 | 72200 | 0.13771057 | 16.261 | 105.55% | 0.000% |
| larger_cache | gcc-auto | 1 | 524289 | 61300 | 0.11692025 | 17.106 | 2.89% | -15.097% |
| larger_cache | gcc-auto | 2 | 524290 | 36600 | 0.069808694 | 28.65 | 1.75% | -49.307% |
| larger_cache | gcc-auto | 3 | 524291 | 42800 | 0.081634054 | 24.5 | 3.19% | -40.720% |
| larger_cache | gcc-auto | 4 | 524292 | 41800 | 0.079726565 | 25.086 | 13.99% | -42.105% |
| larger_cache | gcc-auto | 5 | 524293 | 47300 | 0.09021673 | 22.169 | 16.86% | -34.488% |
| larger_cache | gcc-auto | 6 | 524294 | 37400 | 0.071334023 | 28.037 | 3.78% | -48.199% |
| larger_cache | gcc-auto | 7 | 524295 | 39600 | 0.075529997 | 26.48 | 1.63% | -45.152% |
| larger_cache | gcc-auto | 8 | 524296 | 39700 | 0.075720585 | 26.413 | 2.79% | -45.014% |
| larger_cache | gcc-auto | 9 | 524297 | 38000 | 0.072478004 | 27.595 | 1.73% | -47.368% |
| larger_cache | gcc-auto | 10 | 524298 | 39200 | 0.07476664 | 26.75 | 2.61% | -45.706% |
| larger_cache | gcc-auto | 11 | 524299 | 50500 | 0.096319085 | 20.764 | 6.65% | -30.055% |
| larger_cache | gcc-auto | 12 | 524300 | 37850 | 0.072191493 | 27.712 | 20.18% | -47.576% |
| larger_cache | gcc-auto | 13 | 524301 | 37400 | 0.07133307 | 28.037 | 1.16% | -48.199% |
| larger_cache | gcc-auto | 14 | 524302 | 35800 | 0.068281258 | 29.291 | 1.48% | -50.416% |
| larger_cache | gcc-auto | 15 | 524303 | 42400 | 0.080869268 | 24.731 | 8.58% | -41.274% |
| small_cache | gcc-native | 0 | 3072 | 12200 | 0.031026204 | 64.462 | 1.59% | 0.000% |
| small_cache | gcc-native | 1 | 3073 | 12200 | 0.031016108 | 64.483 | 1.06% | 0.000% |
| small_cache | gcc-native | 2 | 3074 | 13900 | 0.035326529 | 56.615 | 2.48% | 13.934% |
| small_cache | gcc-native | 3 | 3075 | 12200 | 0.030995935 | 64.525 | 0.73% | 0.000% |
| small_cache | gcc-native | 4 | 3076 | 11700 | 0.029715946 | 67.304 | 0.93% | -4.098% |
| small_cache | gcc-native | 5 | 3077 | 10100 | 0.02564389 | 77.991 | 2.97% | -17.213% |
| small_cache | gcc-native | 6 | 3078 | 12200 | 0.030965724 | 64.588 | 1.46% | 0.000% |
| small_cache | gcc-native | 7 | 3079 | 12200 | 0.030955667 | 64.609 | 0.73% | 0.000% |
| small_cache | gcc-native | 8 | 3080 | 9700 | 0.024604302 | 81.287 | 1.72% | -20.492% |
| small_cache | gcc-native | 9 | 3081 | 9900 | 0.025103457 | 79.67 | 15.55% | -18.852% |
| small_cache | gcc-native | 10 | 3082 | 12300 | 0.031179023 | 64.146 | 2.28% | 0.820% |
| small_cache | gcc-native | 11 | 3083 | 7700 | 0.019512245 | 102.5 | 4.35% | -36.885% |
| small_cache | gcc-native | 12 | 3084 | 10000 | 0.025332361 | 78.95 | 1.14% | -18.033% |
| small_cache | gcc-native | 13 | 3085 | 9700 | 0.024564425 | 81.419 | 3.02% | -20.492% |
| small_cache | gcc-native | 14 | 3086 | 9300 | 0.023543827 | 84.948 | 4.53% | -23.770% |
| small_cache | gcc-native | 15 | 3087 | 12300 | 0.031128523 | 64.25 | 0.36% | 0.820% |
| larger_cache | gcc-native | 0 | 524288 | 30200 | 0.057601929 | 34.721 | 8.27% | 0.000% |
| larger_cache | gcc-native | 1 | 524289 | 25550 | 0.048732665 | 41.097 | 30.84% | -15.397% |
| larger_cache | gcc-native | 2 | 524290 | 33600 | 0.06408667 | 31.21 | 71.88% | 11.258% |
| larger_cache | gcc-native | 3 | 524291 | 32400 | 0.061797742 | 32.364 | 26.52% | 7.285% |
| larger_cache | gcc-native | 4 | 524292 | 32300 | 0.061606891 | 32.464 | 14.86% | 6.954% |
| larger_cache | gcc-native | 5 | 524293 | 31800 | 0.060653108 | 32.974 | 10.25% | 5.298% |
| larger_cache | gcc-native | 6 | 524294 | 44650 | 0.085162142 | 23.488 | 39.91% | 47.848% |
| larger_cache | gcc-native | 7 | 524295 | 29900 | 0.057028963 | 35.07 | 11.18% | -0.993% |
| larger_cache | gcc-native | 8 | 524296 | 35000 | 0.066756184 | 29.96 | 5.18% | 15.894% |
| larger_cache | gcc-native | 9 | 524297 | 30000 | 0.057219477 | 34.953 | 5.08% | -0.662% |
| larger_cache | gcc-native | 10 | 524298 | 36500 | 0.069616897 | 28.731 | 28.16% | 20.861% |
| larger_cache | gcc-native | 11 | 524299 | 31000 | 0.059126567 | 33.826 | 5.58% | 2.649% |
| larger_cache | gcc-native | 12 | 524300 | 31700 | 0.060461568 | 33.079 | 14.86% | 4.967% |
| larger_cache | gcc-native | 13 | 524301 | 30700 | 0.058554151 | 34.156 | 10.02% | 1.656% |
| larger_cache | gcc-native | 14 | 524302 | 30400 | 0.05798185 | 34.494 | 8.96% | 0.662% |
| larger_cache | gcc-native | 15 | 524303 | 25300 | 0.04825454 | 41.447 | 3.96% | -16.225% |

## Evidence and Interpretation

The native path has two possible cleanup routes in the saved Phase 2 object: a masked 16-lane ZMM epilogue and a scalar loop fallback for the alias/versioning path. GCC auto processes four floats per XMM iteration, then uses short-vector/scalar cleanup. This timing matrix spans every native remainder and therefore the auto remainder classes as well.

Do not attribute overhead to the cleanup instructions alone: the prescribed ratio also includes the extra r elements, and measurements are limited to these two cache-resident bases. Treat any differences smaller than the per-configuration CV as unresolved. No stride, negative-case, roofline, broad uProf, or Phase 4C work is included.

Plots: `results/plots/phase4b_tail_overhead_small_cache.png` and `results/plots/phase4b_tail_overhead_larger_cache.png`.
