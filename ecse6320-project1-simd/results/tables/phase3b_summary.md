# Phase 3B Stabilization and Validation

This is a versioned reprocessing of the Phase 3 v3 dataset. Original raw v3 samples are unchanged. For only explicitly selected rerun configurations, Phase 3B uses the ten rerun samples instead of the ten original samples; every other configuration uses the original v3 samples.

- Original and Phase 3B configurations: 360.
- Configurations selectively rerun: 40 (cap 40); targeted raw rows: 400.
- Phase 3B configurations above 10% CV: 190; above 20% CV: 100.
- Phase 3B median configuration CV: 10.403%; maximum CV: 111.854%.
- Rerun configurations with median-time shift >=5%: 31/40.
- Rerun configurations that changed a speedup direction across 1.0: 12.
- No original sample was deleted or overwritten; see `data/processed/phase3b_samples.csv` for the merged source-labelled set.
- Detailed original-versus-rerun medians, CVs, relative changes, and speedup-direction checks: `data/processed/phase3b_rerun_comparison.csv`.
- Phase 3B statistics/tables: `data/processed/phase3b_statistics.csv`, `results/tables/phase3b_scalar_vs_simd.md`, and `results/tables/phase3b_datatype_summary.csv`.
- Dot accuracy uses a separate N-dependent floating-point bound; see `data/processed/dot_accuracy_phase3b_v4.csv` and `results/tables/dot_accuracy_phase3b.md`. The largest float32 bound is valid but non-informative.
- Because 31/40 rerun medians shifted by at least 5%, 20 separate `phase3b_*.png` plots were generated; original Phase 3 plots were left untouched.

High-CV residual configurations remain explicitly unstable; do not repeatedly rerun them for a preferred result. No Phase 4 work was performed.
