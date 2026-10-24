# Counter availability

AMD uProf 5.3.521.0 process profiling is available without elevation. Validated categories from the prerequisite audit include cycles not halted, retired instructions, IPC/CPI, L1 data accesses, L1-miss-related L2 requests/fill evidence, DTLB/ITLB and branch events.

Direct L3, Data Fabric, UMC and memory-controller bandwidth PMCs are unavailable. PCM topology access is denied non-admin and is not required. Profiles include process setup/other activity, so internal QPC kernel timing remains primary. No exact L3 miss rate, DRAM traffic, or physical bandwidth will be claimed.
