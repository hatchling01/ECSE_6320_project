# Pre-Experiment Hypotheses

These hypotheses are recorded before measurements. They must not be rewritten later to match measured data. Results may support, reject, or qualify them; preserve the original statements and document interpretation separately.

1. SIMD should outperform scalar code when data supply is sufficient.
2. SIMD gains should compress for large DRAM-resident streaming workloads.
3. float32 may outperform float64 because of more lanes and fewer bytes per element.
4. Misalignment may cause some overhead, but not necessarily a large penalty.
5. Tail handling should matter most for small arrays and become less important for large arrays.
6. Larger stride should reduce cache-line utilization and effective SIMD efficiency.
7. Streaming kernels should become memory-bound sooner than kernels with more arithmetic per byte.
8. A large vectorized streaming kernel should provide a useful negative case where SIMD speedup is much smaller than vector width suggests.
9. GCC and Clang may generate different SIMD code, so emitted instructions must be verified.
10. Working-set sweeps should reveal approximate cache/DRAM regime transitions, although boundaries may be blurred.
