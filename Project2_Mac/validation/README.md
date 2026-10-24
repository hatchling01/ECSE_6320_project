# Mac memory-profiling feasibility check

## Result: specific cache/TLB counter validation has NOT passed

Tested on the M4 Pro / macOS 26.6.2 with Xcode 26.0.1 on October 23, 2026.

- The native ARM64 pointer-chasing probe compiles with warnings treated as errors.
- Its assertions validate the initialized pointer ring. Three trials of each of four
  modes completed. Median ns/load: cache 0.899, memory 112.116, tlb-local 6.086,
  tlb-spread 45.564. These are feasibility measurements, not final cache-level baselines.
- A custom manual CPU Counters recording completes normally (exit status 0).
- Exporting that recording with `xctrace export --toc` aborts (SIGABRT / status -6):
  `Could not cast value of type 'NSNull' ... to 'NSString'`.
- Consequently, no individual cache/TLB miss values or runtime correlations have
  been validated. Recording success and event database availability are insufficient.

The custom template requests FIXED_CYCLES, FIXED_INSTRUCTIONS,
L1D_CACHE_MISS_LD_NONSPEC, L1D_TLB_MISS_NONSPEC, and L2_TLB_MISS_DATA.
It copies and edits Xcode's private template archive format. The export failure
may involve this generated configuration or an Instruments compatibility issue;
it has not been established to be a general failure of Instruments CPU Counters.

## Evidence and reproduction

`results-20261023-145026/` contains all 12 native trial outputs, the original
`memory.trace` recording, recording/export logs, and `summary.json`.

From the project root:

```sh
python3 validation/run_validation.py
```

This creates a new timestamped results directory and returns a nonzero status
if recording/export fails. It requires the installed Xcode path used in the script.
It installs nothing, needs no sudo, and does not alter security settings or the
system-wide developer directory. The probe allocates at most 128 MiB of backing
storage plus its small index array and runs each timed trial for about two seconds.

## Limitations and next check

The two TLB modes have the same node count but also change cache mapping and
footprint. The page-spread mode is deliberately simple and has cache conflicts;
its slowdown is NOT proof of a TLB penalty. No core pinning or frequency locking
was performed. Whole-process counter recording also includes initialization.

Next: create and save a manual counter template through the supported Instruments
GUI, then repeat capture/export. If that fails too, evaluate a newer compatible
Xcode or an alternative counter collector (which may require administrator access).
Do not run the full project suite until individual event values are readable and
their response to controlled workloads has been checked.
