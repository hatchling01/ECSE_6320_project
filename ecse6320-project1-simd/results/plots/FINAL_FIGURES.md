# Final Figure Index

These are selected existing figures; Phase 6 generated no replacement plots. The index includes 12 figures spanning working-set behavior, datatype, alignment, tails, stride, and the roofline-style synthesis.

| # | Figure | What it shows |
|---:|---|---|
| 1 | [Phase 3B elementwise speedup vs working set](phase3b_speedup_vs_working_set_elementwise_multiply.png) | Scalar-relative GCC auto/native speedups across working-set sizes for both datatypes. |
| 2 | [Phase 3B elementwise effective bandwidth](phase3b_effective_bandwidth_vs_working_set_elementwise_multiply.png) | Useful effective GiB/s across working-set sizes; not physical DRAM bandwidth. |
| 3 | [Phase 3B AXPY nanoseconds per element](phase3b_ns_per_element_vs_working_set_axpy.png) | Per-element timing and working-set trend for the two datatypes/builds. |
| 4 | [Phase 3B stencil throughput](phase3b_throughput_vs_working_set_stencil_1d_three_point.png) | Throughput across the sweep for the higher-arithmetic-intensity stencil. |
| 5 | [Phase 3B elementwise datatype comparison](phase3b_float32_vs_float64_elementwise_multiply.png) | Float32/float64 per-element timing comparison across working sets. |
| 6 | [AXPY alignment overhead](phase4a_alignment_overhead_axpy.png) | Alignment-condition contrast and variability for AXPY. |
| 7 | [Elementwise alignment overhead](phase4a_alignment_overhead_elementwise_multiply.png) | Alignment-condition contrast and variability for elementwise multiply. |
| 8 | [Small-base tail overhead](phase4b_tail_overhead_small_cache.png) | AXPY timing variation across remainders 0–15 at the small base. |
| 9 | [Larger-base tail overhead](phase4b_tail_overhead_larger_cache.png) | AXPY timing variation across remainders 0–15 at the 4 MiB base. |
| 10 | [Large-span stride timing](phase4c_stride_ns_per_useful_element_large_dram_sensitive.png) | Useful-element timing versus stride for fixed large spans and three GCC builds. |
| 11 | [Large-span stride effective bandwidth](phase4c_stride_useful_effective_bandwidth_large_dram_sensitive.png) | Useful effective bandwidth versus stride; excludes physical traffic. |
| 12 | [Useful-byte roofline-style view](roofline.png) | Phase 3B native achieved performance, useful-bandwidth reference, and estimated compute ceiling. |