# Phase 3 Variability and Anomalies

Across 360 configurations, 198 exceeded 10% CV; max CV was 94.253% and median CV was 11.473%.
The raw samples are preserved; no outlier was discarded. One highest-CV configuration was rerun once, as required.

| Kernel | Type | Build | N | Target bytes | CV | Median ns/element | Min | Max |
|---|---|---|---:|---:|---:|---:|---:|---:|
| stencil_1d_three_point | float32 | gcc-auto | 3072 | 24,576 | 94.253% | 0.104523 | 0.104523 | 0.554403 |
| elementwise_multiply | float32 | gcc-auto | 2048 | 24,576 | 90.130% | 0.0478745 | 0.0476837 | 0.242996 |
| elementwise_multiply | float32 | gcc-native | 349525 | 4,194,304 | 84.288% | 0.069666 | 0.0689507 | 0.353051 |
| stencil_1d_three_point | float32 | gcc-native | 4194304 | 33,554,432 | 82.534% | 0.180149 | 0.0828505 | 0.724173 |
| axpy | float32 | gcc-native | 3145728 | 25,165,824 | 80.476% | 0.0854174 | 0.0599225 | 0.38449 |
| stencil_1d_three_point | float64 | gcc-auto | 3145728 | 50,331,648 | 75.153% | 0.641362 | 0.563049 | 2.71403 |
| axpy | float64 | gcc-native | 2621440 | 41,943,040 | 73.051% | 0.269222 | 0.169373 | 0.988121 |
| stencil_1d_three_point | float64 | gcc-scalar | 1572864 | 25,165,824 | 71.282% | 0.484753 | 0.360616 | 1.86577 |
| axpy | float64 | gcc-native | 2097152 | 33,554,432 | 71.056% | 0.288725 | 0.146818 | 0.973272 |
| elementwise_multiply | float32 | gcc-native | 4194304 | 50,331,648 | 69.987% | 0.23284 | 0.219941 | 0.964594 |
| elementwise_multiply | float64 | gcc-native | 1048576 | 25,165,824 | 69.360% | 0.235891 | 0.166988 | 0.925064 |
| axpy | float32 | gcc-native | 5242880 | 41,943,040 | 67.710% | 0.211782 | 0.175858 | 0.798702 |
| axpy | float32 | gcc-native | 4194304 | 33,554,432 | 62.348% | 0.108385 | 0.0729561 | 0.374913 |
| stencil_1d_three_point | float32 | gcc-native | 8192 | 65,536 | 61.950% | 0.0707626 | 0.0705719 | 0.243378 |
| axpy | float32 | gcc-auto | 4194304 | 33,554,432 | 60.950% | 0.209272 | 0.146151 | 0.71888 |
| axpy | float64 | gcc-auto | 2621440 | 41,943,040 | 59.943% | 0.324879 | 0.234566 | 1.10298 |
| axpy | float64 | gcc-scalar | 1048576 | 16,777,216 | 58.783% | 0.228071 | 0.1894 | 0.755882 |
| axpy | float32 | gcc-native | 1048576 | 8,388,608 | 56.695% | 0.0630856 | 0.0491142 | 0.178146 |
| stencil_1d_three_point | float64 | gcc-native | 1536 | 24,576 | 54.407% | 0.0940959 | 0.0935872 | 0.290426 |
| elementwise_multiply | float32 | gcc-auto | 2796202 | 33,554,432 | 53.605% | 0.298387 | 0.238323 | 0.906301 |

## Targeted Reruns

| Raw file | Configuration | Original median | Original CV | Rerun median | Rerun CV | Median difference | Speedup direction changed? |
|---|---|---:|---:|---:|---:|---:|---|
| `phase3_v3_targeted_rerun_raw.csv` | stencil_1d_three_point float32 gcc-auto, N=3072, 24,576 B | 0.104523 | 94.253% | 0.113169 | 0.823% | +8.27% | no |

## Phase 3B Selective Reruns

Selected the top 40 of 117 v3 configurations with CV >20%, ranked by original CV. This is below the approximate 40-configuration cap. The selected set covers all four kernels, both datatypes, and all three builds. Original raw samples remain in `phase3_raw_v3.csv`; the 400 new repetitions are in `phase3b_targeted_reruns.csv`; the selection reasons and original medians/CVs are in `data/metadata/phase3b_rerun_selection.csv`. Rerun order was rotated native → auto → scalar. No selected configuration was rerun more than once.

The v3 worst point rerun CV fell from 94.253% to 0.823%. Across the 40 selected configurations, 31 median timings shifted by at least 5%, and 12 crossed the scalar/vector speedup threshold of 1.0. The rerun comparison table reports each original/rerun median, CV, percent change, and whether auto/native speedup direction changed. Phase 3B uses rerun samples only for selected configurations; it retains original v3 samples for every other group.

After selective replacement, 190/360 merged configurations remain above 10% CV and 100/360 above 20%; median CV is 10.403%, and max CV is 111.854%. Residual noisy points remain marked as such; no further reruns were performed.

Large-N dot-product accuracy diagnostics are in `results/tables/dot_accuracy_phase3b.md` and `data/processed/dot_accuracy_phase3b_v4.csv`. All 18 computed errors are within the N-dependent bound, but the three largest float32 cases have a valid bound larger than the reference scale and are labeled non-informative rather than a strong accuracy guarantee.
