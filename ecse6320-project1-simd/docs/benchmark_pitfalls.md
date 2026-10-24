# Benchmark Pitfalls Observed in This Project

These are project-specific observations, not general claims detached from measurements. Numeric evidence and the two negative cases are consolidated in `results/tables/negative_cases.md` and `results/tables/negative_cases.csv`.

1. **Compiler flags do not prove SIMD occurred.** Phase 2's GCC scalar build disables loop/SLP vectorization and its kernel object has scalar `mulss`/`mulsd` forms. The auto/native variants were checked in vectorization reports and disassembly; GCC native elementwise multiply emits packed ZMM `vmulps`, while the strided kernel only reaches packed code on its unit-stride branch. See `results/tables/simd_verification.md` and `results/disassembly/`.

2. **Wider SIMD does not guarantee proportional speedup.** For float32 elementwise multiply at the 134,217,728-byte Phase 3B working set, GCC native emits 512-bit ZMM instructions but measures 0.969392x versus scalar (0.455824 vs 0.441872 ns/element). Useful effective bandwidth is 24.519 vs 25.300 GiB/s, while CV is 23.41% native and 25.73% scalar. This is consistent with data-supply limits, but does not prove physical DRAM saturation. See `results/tables/negative_cases.md`.

3. **Non-unit stride can select a scalar path.** In Phase 4C, the GCC auto/native packed XMM/ZMM paths are guarded on all three runtime strides being one. Strides 2, 4, and 8 branch to scalar `mulss`/`vmulss` loops. The small-span native/scalar speedup falls from 5.380x at stride 1 to 0.891x, 0.825x, and 0.714x at strides 2/4/8. A native ISA target is not a guarantee of vectorization for each access pattern. See `results/tables/phase4c_stride_summary.md` and the GCC disassembly files.

4. **Useful/effective bandwidth is not physical DRAM traffic.** Phase 3 and Phase 4C divide useful logical bytes by elapsed time; Phase 4C counts 12 useful bytes per processed float multiply. This omits cache-line overfetch, write allocation, reuse, and other physical traffic. The host uProf snapshot reports zero L3/DF/UMC PMCs, so no physical memory-controller bandwidth was measured. See `docs/environment.md` and `docs/methodology.md`.

5. **Alignment and tail effects can be smaller than measurement noise.** Phase 4A had 31/108 configurations still above 20% CV after targeted reruns; alignment contrasts crossed zero and did not establish a stable penalty. Phase 4B had 13/96 configurations above 20% CV after reruns, and native tail overhead changed sign across remainders. Neither result supports a universal alignment or tail penalty. See `results/tables/phase4a_alignment_summary.md` and `results/tables/phase4b_tail_summary.md`.

6. **High variability must not be hidden by deleting samples.** Phase 3B retained the original v3 raw data, stored targeted reruns separately, and labeled measurement provenance; 100/360 merged configurations remained above 20% CV. Phase 4A–4C likewise preserve initial and selective rerun files separately. Reruns were bounded by CV policy, not used to discard unfavorable measurements. See `results/tables/phase3b_summary.md` and each Phase 4 summary.

7. **A valid reduction error bound can still allow poor practical accuracy.** The largest Phase 3B float32 dot case (`N=16,777,216`) had 1.764% relative error and a conservative bound of 250,135,832, larger than the result scale. It is labeled within-bound but non-informative, not a strong accuracy guarantee; no tolerance was loosened. See `results/tables/dot_accuracy_phase3b.md`.

Phase 5 roofline and direct bandwidth analysis remains necessary before making stronger compute-vs-memory or physical-bandwidth claims. No new measurement was run to produce this document.
