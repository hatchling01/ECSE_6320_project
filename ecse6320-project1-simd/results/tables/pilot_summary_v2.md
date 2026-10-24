# Phase 3 Pilot Calibration

Elementwise multiply only; this is calibration data, not a full matrix or performance conclusion.

- Raw samples: 180; configurations: 36.
- Warmups: 3 per configuration.
- Repetitions: 5 per configuration.
- Batching: 128 calls for N <= 4096; 32 calls for N <= 65536; otherwise 1 call. Batch is recorded per raw sample.
- Affinity: logical CPU 0, set on each benchmark process and recorded in the raw CSV.
- Median configuration CV: 6.5689%; maximum configuration CV: 28.8249%.
- Configurations above 10% CV: 11/36.
- Shortest median timed sample: 1300 ns.
- Timer: `std::chrono::steady_clock`; non-positive elapsed samples are rejected.
- Calibration conclusion: batching made the smallest samples resolvable, but per-configuration variability remained nonuniform; preserve and interpret CVs rather than treating the pilot as uniformly stable.
- The highest-v2-CV configuration received one targeted rerun. No pilot configuration was repeatedly rerun for a preferred result.
- Planned full-matrix repetitions: 10, chosen at the allowed maximum because pilot variability exceeded 10% in several configurations.

| Datatype | Build | Target footprint (bytes) | N | Batch | Median ns/element | CV |
|---|---|---:|---:|---:|---:|---:|
| float32 | gcc-auto | 134217728 | 11184810 | 1 | 0.421581 | 14.703% |
| float32 | gcc-auto | 2097152 | 174762 | 1 | 0.0841144 | 13.254% |
| float32 | gcc-auto | 25165824 | 2097152 | 1 | 0.161028 | 6.481% |
| float32 | gcc-auto | 4096 | 341 | 128 | 0.0504032 | 3.958% |
| float32 | gcc-auto | 50331648 | 4194304 | 1 | 0.261426 | 18.364% |
| float32 | gcc-auto | 524288 | 43690 | 32 | 0.0609407 | 2.329% |
| float32 | gcc-native | 134217728 | 11184810 | 1 | 0.386328 | 14.447% |
| float32 | gcc-native | 2097152 | 174762 | 1 | 0.0726703 | 14.163% |
| float32 | gcc-native | 25165824 | 2097152 | 1 | 0.0906467 | 6.152% |
| float32 | gcc-native | 4096 | 341 | 128 | 0.0297837 | 6.577% |
| float32 | gcc-native | 50331648 | 4194304 | 1 | 0.239873 | 1.779% |
| float32 | gcc-native | 524288 | 43690 | 32 | 0.045491 | 3.738% |
| float32 | gcc-scalar | 134217728 | 11184810 | 1 | 0.429824 | 9.411% |
| float32 | gcc-scalar | 2097152 | 174762 | 1 | 0.184251 | 2.015% |
| float32 | gcc-scalar | 25165824 | 2097152 | 1 | 0.215626 | 1.890% |
| float32 | gcc-scalar | 4096 | 341 | 128 | 0.252016 | 0.762% |
| float32 | gcc-scalar | 50331648 | 4194304 | 1 | 0.27833 | 6.029% |
| float32 | gcc-scalar | 524288 | 43690 | 32 | 0.182393 | 1.362% |
| float64 | gcc-auto | 25165824 | 1048576 | 1 | 0.322533 | 7.287% |
| float64 | gcc-auto | 4096 | 170 | 128 | 0.101103 | 5.567% |
| float64 | gcc-auto | 50331648 | 2097152 | 1 | 0.549603 | 6.561% |
| float64 | gcc-auto | 524288 | 21845 | 32 | 0.121881 | 28.825% |
| float64 | gcc-auto | 134217728 | 5592405 | 1 | 0.805342 | 4.091% |
| float64 | gcc-auto | 2097152 | 87381 | 1 | 0.255204 | 10.142% |
| float64 | gcc-native | 25165824 | 1048576 | 1 | 0.270844 | 19.647% |
| float64 | gcc-native | 4096 | 170 | 128 | 0.0597426 | 6.675% |
| float64 | gcc-native | 50331648 | 2097152 | 1 | 0.484848 | 13.739% |
| float64 | gcc-native | 524288 | 21845 | 32 | 0.0904097 | 4.798% |
| float64 | gcc-native | 134217728 | 5592405 | 1 | 0.691152 | 7.153% |
| float64 | gcc-native | 2097152 | 87381 | 1 | 0.21515 | 8.093% |
| float64 | gcc-scalar | 25165824 | 1048576 | 1 | 0.312042 | 4.769% |
| float64 | gcc-scalar | 4096 | 170 | 128 | 0.261949 | 2.149% |
| float64 | gcc-scalar | 50331648 | 2097152 | 1 | 0.566292 | 12.849% |
| float64 | gcc-scalar | 524288 | 21845 | 32 | 0.194839 | 9.745% |
| float64 | gcc-scalar | 134217728 | 5592405 | 1 | 0.748104 | 3.266% |
| float64 | gcc-scalar | 2097152 | 87381 | 1 | 0.199128 | 11.197% |

## Targeted Stability Reruns

Reruns are preserved separately; they are not merged into the original five-sample configurations.

| Raw file | Datatype | Build | N | Batch | Samples | Median ns/element | CV |
|---|---|---|---:|---:|---:|---:|---:|
| `pilot_rerun_raw.csv` | float32 | gcc-native | 43690 | 32 | 5 | 0.0477083 | 0.805% |
| `pilot_rerun2_raw.csv` | float64 | gcc-scalar | 1048576 | 1 | 5 | 0.443459 | 16.052% |
| `pilot_v2_targeted_rerun_raw.csv` | float64 | gcc-auto | 21845 | 32 | 5 | 0.103857 | 1.505% |
