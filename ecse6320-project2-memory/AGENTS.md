# Permanent safety and evidence rules

- Never change BIOS, SMT, power, Hyper-V/VBS, pagefile, security, large-page privilege, NUMA, clocks, timings, drivers, registry, or PowerShell execution policy. Never require administrator rights.
- No benchmark process may intentionally allocate over 8 GiB. Normal runs stay at or below about 4 GiB. Before a process allocates more than 1 GiB, require at least 16 GiB available physical memory; otherwise stop the phase.
- Do not base conclusions on paging. Stop and preserve an invalid record if paging, trimming, thrashing, repeated allocation failure, or loss of responsiveness is suspected.
- Pin controlled measurements. Primary concurrency uses at most 16 physical cores and avoids SMT siblings.
- Preserve every raw record. Never overwrite canonical raw data, fabricate results, silently delete outliers, or rewrite pre-experiment hypotheses.
- Useful/effective bandwidth is logical benchmark traffic, not physical DRAM traffic.
- AMD uProf is process-level supporting evidence. It does not replace benchmark timing. No direct L3, DF, UMC, or memory-controller counters are available.
- Do not claim an exact cache boundary from one noisy point or equate aggregate Windows L3 with a pinned core's local LLC automatically.
- Large pages are unavailable; do not claim a measured large-page benefit.
- Generate plots from canonical parsed data. Distinguish measurements, theory, and interpretation.
- Active automation is Python, never executable PowerShell scripts.
