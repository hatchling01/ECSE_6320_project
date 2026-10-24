# Phase 3 Pilot Calibration

Elementwise multiply only; this is calibration data, not a full matrix or performance conclusion.

- Raw samples: 180; configurations: 36.
- Warmups: 3 per configuration.
- Repetitions: 5 per configuration.
- Batching: 128 calls for N <= 4096; 32 calls for N <= 32768; otherwise 1 call. Batch is recorded per raw sample.
- Affinity: logical CPU 0, set on each benchmark process and recorded in the raw CSV.
- Median configuration CV: 8.7910%; maximum configuration CV: 32.8108%.
- Shortest median timed sample: 1200 ns.
- Timer: `std::chrono::steady_clock`; non-positive elapsed samples are rejected.
- Timing stability rule for proceeding: maximum CV <= 10%; observed above rule; review needed.
- Any per-configuration CV above 10% requires at most one targeted rerun; do not repeatedly rerun for a preferred value.
- Recommendation: proceed with 3 warmups and 5 repetitions only if the pilot is credible under the stated stability rule.

| Datatype | Build | Target footprint (bytes) | N | Batch | Median ns/element | CV |
|---|---|---:|---:|---:|---:|---:|
| float32 | gcc-auto | 134217728 | 11184810 | 1 | 0.383967 | 12.185% |
| float32 | gcc-auto | 2097152 | 174762 | 1 | 0.0795367 | 13.493% |
| float32 | gcc-auto | 25165824 | 2097152 | 1 | 0.197554 | 10.248% |
| float32 | gcc-auto | 4096 | 341 | 128 | 0.0893512 | 4.923% |
| float32 | gcc-auto | 50331648 | 4194304 | 1 | 0.293827 | 11.545% |
| float32 | gcc-auto | 524288 | 43690 | 1 | 0.112154 | 16.962% |
| float32 | gcc-native | 134217728 | 11184810 | 1 | 0.366309 | 6.361% |
| float32 | gcc-native | 2097152 | 174762 | 1 | 0.0703814 | 4.600% |
| float32 | gcc-native | 25165824 | 2097152 | 1 | 0.121689 | 19.254% |
| float32 | gcc-native | 4096 | 341 | 128 | 0.0274927 | 5.893% |
| float32 | gcc-native | 50331648 | 4194304 | 1 | 0.252748 | 13.263% |
| float32 | gcc-native | 524288 | 43690 | 1 | 0.0572213 | 32.811% |
| float32 | gcc-scalar | 134217728 | 11184810 | 1 | 0.371191 | 5.084% |
| float32 | gcc-scalar | 2097152 | 174762 | 1 | 0.310708 | 0.998% |
| float32 | gcc-scalar | 25165824 | 2097152 | 1 | 0.432491 | 18.071% |
| float32 | gcc-scalar | 4096 | 341 | 128 | 0.23827 | 1.577% |
| float32 | gcc-scalar | 50331648 | 4194304 | 1 | 0.302649 | 16.715% |
| float32 | gcc-scalar | 524288 | 43690 | 1 | 0.272374 | 1.519% |
| float64 | gcc-auto | 25165824 | 1048576 | 1 | 0.284386 | 17.349% |
| float64 | gcc-auto | 4096 | 170 | 128 | 0.0965074 | 8.206% |
| float64 | gcc-auto | 50331648 | 2097152 | 1 | 0.486612 | 9.376% |
| float64 | gcc-auto | 524288 | 21845 | 32 | 0.130751 | 3.586% |
| float64 | gcc-auto | 134217728 | 5592405 | 1 | 0.739771 | 7.490% |
| float64 | gcc-auto | 2097152 | 87381 | 1 | 0.178529 | 15.925% |
| float64 | gcc-native | 25165824 | 1048576 | 1 | 0.280476 | 14.629% |
| float64 | gcc-native | 4096 | 170 | 128 | 0.0551471 | 5.893% |
| float64 | gcc-native | 50331648 | 2097152 | 1 | 0.513649 | 4.621% |
| float64 | gcc-native | 524288 | 21845 | 32 | 0.0969902 | 1.458% |
| float64 | gcc-native | 134217728 | 5592405 | 1 | 0.880086 | 21.795% |
| float64 | gcc-native | 2097152 | 87381 | 1 | 0.148774 | 4.107% |
| float64 | gcc-scalar | 25165824 | 1048576 | 1 | 0.374889 | 30.948% |
| float64 | gcc-scalar | 4096 | 170 | 128 | 0.275735 | 5.068% |
| float64 | gcc-scalar | 50331648 | 2097152 | 1 | 0.578213 | 3.795% |
| float64 | gcc-scalar | 524288 | 21845 | 32 | 0.267653 | 14.620% |
| float64 | gcc-scalar | 134217728 | 5592405 | 1 | 0.81557 | 7.293% |
| float64 | gcc-scalar | 2097152 | 87381 | 1 | 0.226594 | 10.642% |
