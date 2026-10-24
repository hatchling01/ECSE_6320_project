# Project Specification Summary

## Kernels (future implementation)

1. AXPY: `y[i] = a*x[i] + y[i]`
2. Dot product: `sum += x[i]*y[i]`
3. Elementwise multiply: `z[i] = x[i]*y[i]`
4. 1D three-point stencil: `y[i] = a*x[i-1] + b*x[i] + c*x[i+1]`

Test both float32 and float64. The Phase 1 scalar kernels and references are implemented; no performance benchmarks have been run.

## Required Experiments (planned)

- Scalar vs auto-vectorized vs CPU-targeted builds.
- Working-set sweep through cache and DRAM regimes.
- Alignment and vector-width-tail behavior.
- Strides 1, 2, 4, and 8.
- Datatype comparison.
- Compiler vectorization reports and targeted disassembly.
- Representative AMD uProf metrics.
- Effective memory bandwidth, arithmetic intensity, and roofline analysis.
- At least one negative case where SIMD gives little benefit or fails.

## Reported Metrics

Where meaningful, report runtime, speedup, throughput, cycles/element, GFLOP/s, effective GiB/s, and variability/error information. Effective bandwidth is bytes processed divided by measured runtime; it is not a direct memory-controller counter.

## Measurement Constraints

Run final measurements natively on Windows/bare metal. Verify correctness before timing. Record compiler versions, flags, environment, and evidence of emitted SIMD. Preserve raw data and anomalies. The current uProf host reports no direct L3, DF, or UMC PMCs; do not invent these values. Cache/DRAM boundaries may instead be inferred cautiously from controlled working-set sweeps.
