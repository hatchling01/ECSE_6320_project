# Permanent Project Rules

These rules apply to every command, script, analysis, and report in this repository.

## Storage safety

- Never benchmark a raw disk, `\\.\PhysicalDrive*`, disk number, partition, volume device, drive root, EFI/recovery partition, or raw NVMe namespace.
- FIO may target only a regular disposable file whose canonical path is strictly inside this repository's `benchmark_data` directory.
- Every script-generated FIO command must run the active Python target validator first and abort unless it prints `SAFE REGULAR-FILE TARGET VERIFIED`.
- Never launch a broad write sweep without validating the target immediately before invocation.
- Use direct I/O for primary experiments (`direct=1`) unless an explicitly labeled pitfall experiment calls for buffering.
- Do not format, repartition, initialize, clean, trim a whole device, secure erase, sanitize, mount/unmount, or change disk, filesystem, power, security, driver, BIOS, firmware, or virtualization settings.
- Never write outside the validated disposable file. Cleanup may delete only an already validated file inside `benchmark_data`.
- Preserve substantial free space and use scientifically justified, conservative file/range sizes.

## Scientific integrity

- Preserve canonical raw FIO JSON; never overwrite it. Reruns receive new timestamps and both original and rerun data are retained.
- Do not fabricate, conceal, or silently alter results. Do not silently delete outliers.
- Record anomalies and any rerun/selection policy in `docs/anomalies.md`.
- Pre-experiment hypotheses in `docs/hypotheses.md` may not be retroactively rewritten to fit results. Add dated amendments instead.
- Record the exact FIO version, command/configuration, target, engine, direct setting, block size, access pattern, mix, queue depth, jobs, range/file size, runtime/ramp time, repetition, and timestamp for every experiment.
- Distinguish configured `iodepth`, `numjobs`, aggregate configured concurrency, achieved depth, and Little's-Law-inferred occupancy.
- Preserve FIO source units and distinguish decimal MB/s and GB/s from binary MiB/s and GiB/s.
- Clearly separate observed behavior from hypotheses about the controller, cache, flash, or NAND.
- Do not claim thermal throttling, garbage collection, SLC-cache exhaustion, or interface saturation without supporting measurements.
- AI-generated parsing, analysis, and interpretation must be checked against raw FIO output.

## Phase control

- Phase 0 and the tiny Phase 1 smoke validation are infrastructure checks, not performance data.
- `data/raw/smoke/` is explicitly excluded from performance analysis.
- Do not execute a later phase without explicit user authorization for that phase.

