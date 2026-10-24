# Methodology

## Benchmark target and safety

All I/O targets are ordinary disposable files strictly inside `benchmark_data`. Scripts canonicalize and validate every target immediately before invoking FIO. Drive roots, device syntax, physical disks, volumes, partitions, directories, and paths outside the benchmark directory are rejected. Primary experiments use `windowsaio` with `direct=1`.

The executable orchestration and safety layer is native Python from the existing Anaconda environment. Windows restricts `.ps1` execution on this host, so PowerShell scripts are reference material only and are not required to run the project. This is an orchestration choice, not a storage benchmark limitation, and no execution-policy setting is changed or bypassed.

The tiny smoke file is 16 MiB with only 4 MiB of measured mixed I/O; it validates mechanics and is excluded from analysis. The production file is one 8 GiB regular file, selected conservatively from the working-set objective, direct-I/O behavior, approximately 61.65 GiB RAM, free-space reserve, setup cost, and endurance risk. It does not fill the SSD and is ignored by Git. One direct sequential initialization pass populated the range before production reads; its 8 GiB of logical writes is recorded but excluded from performance analysis.

## Experimental discipline

- Production reads are time-based where stable comparisons benefit; write-capable jobs are bounded by logical I/O size.
- Main configurations use three repeated trials. Summaries include median, mean, standard deviation, coefficient of variation, and min/max where useful.
- Raw noisy trials and reruns are retained. A rerun never overwrites its predecessor, and selection/merge decisions are documented.
- Warmup, runtime, ramp time, repetitions, seed/data pattern, engine, direct setting, block size, access mode/mix, `iodepth`, `numjobs`, range, file size, and timestamp are recorded per result.
- Random offsets remain block-aligned. Primary data uses a consistent incompressible/randomized buffer policy.

## Completed matrix

The completed work covers QD=1 baselines; required 4-256 KiB block sizes; sequential/random patterns; required 100/0, 70/30, 50/50, and 0/100 mixes; staged concurrency through observed diminishing returns; mid-QD and near-knee tails; 256 MiB, 2 GiB, and 8 GiB ranges; one conservative 8 GiB state observation; and a buffered-versus-direct pitfall. QD128/256 were not run because scaling had already ended by QD64.

## Metrics, units, and queue terminology

Canonical input is FIO JSON. Parsing preserves reported unit fields and adds explicitly named conversions. Reports distinguish ns, µs, ms, IOPS, decimal MB/s/GB/s, and binary MiB/s/GiB/s.

`iodepth` is per-job configured depth; `numjobs` duplicates jobs. Their product is only aggregate configured concurrency and is not automatically achieved device queue occupancy. Achieved throughput and mean response time may be used for Little's-Law estimates (`L = λW`), labeled as inferred occupancy and not forced to equal configured depth.

## Burst, steady state, and causal claims

Short and longer runs are labeled separately. A throughput decline alone does not prove SLC exhaustion, garbage collection, thermal throttling, or interface saturation. Such claims require corroborating time-series, temperature/telemetry, recovery, or other evidence. If telemetry or a safe transition is unavailable, the limitation is reported.

## Data provenance

Saved configs/manifests, wrapper logs, immutable timestamped JSON, environment metadata, and parser version make every result traceable. Parsed CSV and plots are regenerated from raw JSON; conclusions are never based on undocumented manual edits.

