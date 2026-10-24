# Environment

The host is Windows 11 Enterprise 10.0.26200 (build 26200), AMD Ryzen 9 9950X, 16 physical/32 logical CPUs, one processor group and one Windows NUMA node. SMT, Hyper-V and VBS are active; the Balanced plan remains unchanged. Windows reports aggregate L1/L2/L3 capacities of 1,280 KiB, 16 MiB and 64 MiB. uProf reports two cache domains, so aggregate L3 is not assumed to be uniformly local to a pinned core.

RAM is four Micron 16 GiB modules; OS-visible memory is 64,647,640 KiB. WMI reports `Speed=4800` and `ConfiguredClockSpeed=3600`; these are retained verbatim and are not measured bandwidth. Normal page size is 4096 B and allocation granularity 65536 B. Large-page minimum is 2 MiB, but the token lacks `SeLockMemoryPrivilege`; no security change is permitted.

Primary tools: Git 2.54.0.windows.1, CMake 4.4.4, Ninja 1.13.2, Anaconda Python 3.13.9, and AMD uProf 5.3.521.0. GCC 16.2 was detected but its subprocess exited without diagnostics even for a single source; Phase 0 therefore used the permitted fallback, Clang 23.1.4 targeting the existing MinGW/UCRT environment, with `-O3 -DNDEBUG -march=native`.

QPC frequency is 10 MHz. Windows topology discovery and affinity validation succeeded.

AMD's official Ryzen 9 9950X product page independently lists 16 cores/32 threads and aggregate L1/L2/L3 caches of 1,280 KB/16 MB/64 MB: <https://www.amd.com/en/products/processors/desktops/ryzen/9000-series/amd-ryzen-9-9950x.html>. The vendor page does not resolve the per-core/per-cache-domain topology; the uProf observation of two cache domains remains the local-topology qualifier.
