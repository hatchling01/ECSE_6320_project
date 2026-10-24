# Phase Plan

Each phase is independently rerunnable. Advancing requires explicit authorization; later phases are not implied by this plan.

## Phase 0 — repository, safety, methodology, hypotheses

Create the repository and documentation, capture the pre-test environment, implement target validation and parser infrastructure, and commit the baseline. No performance benchmarking.

Status: complete.

## Phase 1 — target validation and tiny FIO smoke test

Use a tiny disposable regular file to validate `windowsaio`, `direct=1`, JSON, latency percentiles, configured QD=1, parser behavior, and safe cleanup. Mark all smoke artifacts `NOT FOR PERFORMANCE ANALYSIS`.

Status: minimal validation complete; see `docs/smoke_validation.md`. No production measurement was collected.

## Phase 2 — QD=1 baseline

Run only the four required latency baselines with an approved runtime, repetition policy, and production file strategy.

## Phase 3 — block-size and access-pattern sweep

Compare required block sizes under controlled sequential/random conditions.

## Phase 4 — read/write mix sweep

Compare 100/0, 70/30, 50/50, and 0/100 at fixed justified settings.

## Phase 5 — concurrency sweep and knee analysis

Sweep useful `iodepth`/`numjobs`, produce the throughput-latency curve, define the knee numerically, and evaluate Little's Law without equating configured and inferred occupancy.

## Phase 6 — tail latency, working set, and device state

Collect statistically defensible tails and conservative range/burst/steady observations.

## Phase 7 — benchmark pitfall

Demonstrate one safe, meaningful misleading setup, tentatively buffered versus direct regular-file I/O.

## Phase 8 — final analysis and reproducibility audit

Regenerate parsed tables/plots from canonical raw JSON, audit every claim, document anomalies/limitations, and complete the report.

