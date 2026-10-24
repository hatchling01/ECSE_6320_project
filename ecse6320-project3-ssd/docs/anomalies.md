# Anomaly and Rerun Log

This log records unexpected output, noisy trials, failures, and reruns. Original raw results are never deleted.

## 2026-10-23 — first smoke invocation invalidated

The first Python-driven smoke invocation supplied the validated absolute Windows path through FIO's `--filename` option. FIO treats a colon in a filename value as a multi-file separator, so the `C:` drive prefix caused an unintended 8 MiB file named `C` to be created in the repository root in addition to the intended disposable target. The raw smoke JSON, parsed CSV, metadata, and log are retained for audit but are invalid and permanently classified `NOT FOR PERFORMANCE ANALYSIS`.

At that point, further FIO activity was stopped pending explicit authorization to remove the unintended file. The runner was hardened to set its working directory to the validated `benchmark_data` directory and pass only the target leaf filename to FIO. Actual JSON is reconstructed against that fixed working directory and compared with the validated canonical path.

Resolution: the user explicitly authorized deletion of only the exact unintended path. Before deletion it resolved exactly as expected, was a regular 8,388,608-byte file, had only the ordinary `:$DATA` stream, and was neither a directory nor a reparse/device/volume path. It was deleted without deleting any other file. One corrected smoke invocation then passed all target, JSON, percentile, parser, and cleanup checks. Both attempts remain excluded from performance analysis.

## 2026-10-24 - Phase 4 analysis conversion failure

All twelve Phase 4 FIO runs completed and passed target validation. The first derived-analysis invocation failed because inactive-direction percentile cells for pure read/write jobs are blank, not numeric zeros. The parser was corrected to preserve those cells as missing values. Analysis was regenerated without rerunning or altering any FIO result.

## 2026-10-24 - device-state time-series limitation

The single authorized 8 GiB state pass completed in 1.59 seconds. With 1-second averaging, FIO emitted only one bandwidth-log interval. The run is valid, but early/middle/late transition behavior is unresolved; the report does not infer cache exhaustion, garbage collection, or thermal throttling.

