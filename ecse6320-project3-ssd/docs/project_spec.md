# Project Specification Audit

## Objective and learning goals

Characterize the installed NVMe SSD using controlled FIO experiments while learning to separate latency, IOPS, bandwidth, concurrency, access pattern, workload mix, working-set, and device-state effects. The final analysis must identify a throughput–latency saturation knee, discuss Little's Law carefully, characterize tail latency, demonstrate a meaningful benchmark pitfall, preserve raw evidence, and remain reproducible and safe.

## Required experimental knobs

- Block sizes: 4, 16, 32, 64, 128, and 256 KiB. Optional 512 KiB and 1 MiB only when useful for sequential saturation.
- Access patterns: sequential and block-aligned random access.
- Read/write mixes: 100/0, 70/30, 50/50, and 0/100.
- Concurrency: controlled `iodepth` and/or `numjobs` progression from low concurrency toward saturation, stopping when added concurrency is no longer scientifically useful.
- Data: documented and consistent; incompressible/randomized data is preferred for primary measurements.
- Device state: observe burst/steady behavior, cache effects, garbage collection, temperature, and throttling only where safely measurable; do not claim unobserved mechanisms.

## Required experiments

1. QD=1 baselines: 4 KiB random read/write and 128 KiB sequential read/write, reporting throughput, meaningful IOPS, mean latency, p50, p95, p99, and p99.9 when sample counts justify it.
2. Block-size and access-pattern sweeps using the same runs for throughput and latency.
3. Fixed, justified block-size/pattern comparison of the four required read/write mixes.
4. Queue-depth/parallelism sweep producing one interpretable throughput-versus-latency curve and a reproducible knee criterion; distinguish configured concurrency from inferred occupancy.
5. Tail latency at a mid-QD and a near-knee point, with enough completions for p99.9.
6. Regular-file working-set/range comparison without claiming visibility into physical NAND placement.
7. Conservative burst-versus-longer-run device-state comparison; report honestly if no transition is visible.
8. A safe misleading benchmark/pitfall demonstration, preferably buffered versus direct regular-file I/O.

## Common requirements and deliverables

- AI-use disclosure, reproducible repository, hypotheses recorded before performance measurements, correctness/sanity checks, exact environment and tools, repeated trials, statistics/error bars where meaningful, a negative/misleading case, and honest anomaly discussion.
- Preserve every canonical raw JSON result. Do not suppress noisy trials or silently delete outliers.
- Final README/report will cover objective, hypotheses, target safety, environment, methodology, all required experiment analyses, Little's Law, limitations, reproducibility, conclusions, and AI use.
- Trace every result to exact configuration, command, version, target/range, repetition, and timestamp.

## Grading priorities (185 points)

- 40: read/write and queue-depth analysis, knee, and Little's Law.
- 35: block-size and access-pattern sweeps.
- 30: safety and accurate QD=1 baseline.
- 25: tail latency and device state.
- 25: reproducibility and data hygiene.
- 15: AI use and benchmark pitfall.
- 15: report quality.

Items beyond the assignment are labeled as methodology choices rather than requirements.

