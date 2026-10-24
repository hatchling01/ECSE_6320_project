# Phase 3B Dot-Product Accuracy

These are no-timing diagnostics using the Phase 3 deterministic inputs. Full per-build records are in `data/processed/dot_accuracy_phase3b_v4.csv` (18 records: three N scales × two datatypes × three GCC builds). The computed values were identical across the three GCC builds for each input/type in this check.

## Error Bound

Let `u = numeric_limits<T>::epsilon()/2` (round-to-nearest unit roundoff), `N` be the reduction length, and `S = sum_i |x_i*y_i|`. To cover product rounding plus an arbitrary scalar/vector reduction order, use `m=2N` rounded operations. For `m*u < 1`, `gamma_m(u)=m*u/(1-m*u)`; otherwise use the finite conservative product bound `gamma_m(u)=(1+u)^m-1`. The long-double reference and `S` accumulation are also rounded; their `gamma_m(u_long_double)` contribution and denominator correction are included. The resulting comparison bound is

`abs(computed - long_double_reference) <= (gamma_m(u_T) + gamma_m(u_LD)) * S / (1 - gamma_m(u_LD))`.

No empirical tolerance was loosened. A bound can be mathematically valid yet non-informative; that status is called out separately rather than presented as a strong accuracy guarantee.

| N | Type | Build | Computed | Long-double reference | Absolute error | Relative error | Bound | Status |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1,003 | float32 | all three GCC builds | 1,823.07043457 | 1,823.07203837 | 0.0016038 | 8.80e-7 | 0.2804 | Pass, informative |
| 3,145,728 | float32 | all three GCC builds | 5,705,779 | 5,716,331.79273 | 10,552.79 | 1.846e-3 | 4,404,453 | Pass, conservative |
| 16,777,216 | float32 | all three GCC builds | 29,949,242 | 30,487,120.6840 | 537,878.68 | 1.764e-2 | 250,135,832 | Within bound; non-informative |
| 1,003 | float64 | all three GCC builds | 1,823.0720221606643 | 1,823.0720221606648 | 4.72e-13 | 2.59e-16 | 5.22e-10 | Pass, informative |
| 1,572,864 | float64 | all three GCC builds | 2,858,166.00830720 | 2,858,166.00831025 | 3.05e-6 | 1.069e-12 | 1.282e-3 | Pass, informative |
| 8,388,608 | float64 | all three GCC builds | 15,243,557.1552029 | 15,243,557.1551246 | 7.83e-5 | 5.137e-12 | 3.648e-2 | Pass, informative |

All 18 cases are within the calculated bound. For the largest float32 reduction, the bound exceeds the result scale, so the observed 1.764% relative difference is reported but not claimed to meet a tighter accuracy target. Do not interpret this as a performance result or alter the Phase 1 tolerance.