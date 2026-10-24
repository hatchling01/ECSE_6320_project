# Phase 3 Variability Diagnostic

CV is computed from the 10 raw repetitions for each configuration; group counts show how high-CV cases distribute by one dimension at a time.

| Dimension | Value | Configurations | CV > 10% | CV > 20% | Median CV | Max CV |
|---|---|---:|---:|---:|---:|---:|
| target_working_set_bytes | 100663296 | 24 | 23 | 12 | 20.481% | 33.890% |
| target_working_set_bytes | 1048576 | 24 | 8 | 7 | 5.742% | 52.051% |
| target_working_set_bytes | 134217728 | 24 | 22 | 11 | 19.910% | 28.039% |
| target_working_set_bytes | 16777216 | 24 | 10 | 5 | 8.775% | 58.783% |
| target_working_set_bytes | 24576 | 24 | 7 | 6 | 2.603% | 94.253% |
| target_working_set_bytes | 25165824 | 24 | 15 | 9 | 13.401% | 80.476% |
| target_working_set_bytes | 262144 | 24 | 5 | 2 | 3.811% | 38.007% |
| target_working_set_bytes | 33554432 | 24 | 22 | 12 | 19.698% | 82.534% |
| target_working_set_bytes | 4194304 | 24 | 11 | 6 | 9.644% | 84.288% |
| target_working_set_bytes | 41943040 | 24 | 22 | 14 | 24.480% | 73.051% |
| target_working_set_bytes | 50331648 | 24 | 18 | 15 | 31.268% | 75.153% |
| target_working_set_bytes | 65536 | 24 | 5 | 4 | 2.853% | 61.950% |
| target_working_set_bytes | 67108864 | 24 | 22 | 12 | 20.933% | 42.734% |
| target_working_set_bytes | 8192 | 24 | 2 | 0 | 1.169% | 19.293% |
| target_working_set_bytes | 8388608 | 24 | 6 | 2 | 6.730% | 56.695% |
| kernel | axpy | 90 | 58 | 38 | 18.120% | 80.476% |
| kernel | dot_product | 90 | 32 | 16 | 6.785% | 46.883% |
| kernel | elementwise_multiply | 90 | 53 | 34 | 14.010% | 90.130% |
| kernel | stencil_1d_three_point | 90 | 55 | 29 | 14.050% | 94.253% |
| datatype | float32 | 180 | 99 | 55 | 11.089% | 94.253% |
| datatype | float64 | 180 | 99 | 62 | 12.415% | 75.153% |
| build | gcc-auto | 120 | 65 | 38 | 11.391% | 94.253% |
| build | gcc-native | 120 | 76 | 46 | 15.200% | 84.288% |
| build | gcc-scalar | 120 | 57 | 33 | 8.203% | 71.282% |
