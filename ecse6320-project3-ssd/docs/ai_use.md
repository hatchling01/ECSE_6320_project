# AI-Use Disclosure

Codex assisted with repository organization, safety scripting, FIO configuration, experiment orchestration, parsing, plotting, statistical summaries, documentation, and analysis drafting.

Claims in this repository are grounded in actual retained FIO JSON, pre- and post-run target validation, repeated measurements, parser checks, and explicit methodology. Derived CSVs, figures, and reports are regenerable from canonical raw data. Codex did not independently verify or infer internal SSD behavior such as NAND placement, write amplification, garbage collection, SLC-cache boundaries, or thermal throttling.

The student remains responsible for reviewing the commands, evidence, interpretations, limitations, and final submission.

## Independent validation, modification, and rejection

The first Windows FIO smoke attempt exposed an absolute-path colon-parsing hazard and created an unintended regular file named `C`. That smoke run was invalidated, preserved as audit evidence, and excluded from performance analysis. The runner was then redesigned to use `benchmark_data` as its working directory, pass only a basename to FIO, and reconstruct and verify the actual JSON-reported target after every run.

PowerShell execution-policy bypasses were rejected; Python became the active orchestration and safety layer without changing system policy. Raw-disk, partition, and volume benchmarking were rejected in favor of a regular-file-only workflow. Unsupported explanations involving SLC-cache exhaustion, garbage collection, NAND placement, write amplification, or thermal throttling were intentionally withheld. The short device-state run was reported as unresolved, and failed or anomalous runs were retained as audit evidence rather than silently deleted.

## Representative AI workflow

Codex assisted with safety scripting, FIO configuration, experiment orchestration, parsing, plotting, statistics, and documentation/analysis drafting. These were assistance tasks; actual FIO JSON, target validation, repeated measurements, parser checks, and the documented safety controls supplied the evidence.
