# Phase 1 Correctness Summary

Correctness validation only; this is not performance data. No benchmark was run.

- Cases: 448
- Passed: 448
- Status: PASS
- Sizes: 0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 33, 100, 1003
- Contiguous pointer conditions: 64-byte-aligned base, plus safe offsets of 1 and 3 elements.
- Stride cases: elementwise multiply at strides 1, 2, 4, and 8.
- Stencil boundaries: copy input endpoints; apply the three-point formula to interior elements.

| Datatype | Passed / cases | Max absolute error | Max relative error |
|---|---:|---:|---:|
| float32 | 224/224 | 0.00030517578 | 8.1534997e-07 |
| float64 | 224/224 | 3.4106051e-13 | 9.112246e-16 |

Tolerance rule: `abs(error) <= absolute_tolerance + relative_tolerance * abs(reference)`. float32 uses absolute 2e-5 and relative 2e-6; float64 uses absolute 1e-12 and relative 1e-12. Relative error is normalized by max(abs(reference), absolute_tolerance) for reporting.
