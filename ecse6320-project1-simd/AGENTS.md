# Project Rules

- Never fabricate benchmark results.
- Preserve raw data.
- Verify correctness before benchmarking.
- Record exact compiler versions and flags.
- Verify SIMD using compiler reports and disassembly, not just compiler flags.
- Distinguish measured results from theory and interpretation.
- Final measurements must run natively on Windows, not in a VM, WSL, Docker, or cloud environment.
- Do not alter BIOS, SMT, overclocking, security, or virtualization settings.
- Do not fabricate unavailable L3/DF/UMC metrics.
- Label bytes/time bandwidth as effective bandwidth.
- Investigate unstable or implausible measurements.
- Preserve anomalies honestly.
- Do not rewrite pre-experiment hypotheses after seeing results.
- Generate the final README from real measurements only.
- Disclose AI assistance.

Before future project work, read `AGENTS.md`, `docs/project_spec.md`, and `docs/plan.md`.
