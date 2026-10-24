# Methodology

The native C++ MLC-equivalent uses randomized dependent pointer rings for approximately one-outstanding-request latency, 64-byte streaming/random operations for useful bandwidth, a dependent probe plus disjoint background regions for loaded latency, and one node per normal 4 KiB page for TLB reach. Allocation and index generation occur outside timed regions. Reads feed emitted checksums; writes receive post-timing sample validation. QPC is the mandatory wall timer.

Threads are pinned inside the executable. The Windows topology API selected logical CPUs 0,2,…,30—one per physical core. Production single-thread work uses CPU 0. Loaded-latency reserves CPU 0 for the probe and uses the remaining physical-core representatives.

Python is the executable orchestration layer because Windows PowerShell script execution is restricted. Raw JSON is append-only by unique filename. Every run records timestamp, Git revision, compiler/flags, mode, affinity, sizes, operations, repetition, timing, checksum and memory observations. Analysis reports median, mean, sample standard deviation, CV, min, and max; outliers are retained.

Useful bandwidth counts 64 logical bytes per operation. It is not physical DRAM or memory-controller traffic. Cache labels are representative interpretations, not exact placement guarantees. uProf evidence is process-level and supporting only.

The hard process cap is 8 GiB. Normal allocations are ≤4 GiB. The runner and native executable both check the 16 GiB available-memory gate before allocations over 1 GiB.
