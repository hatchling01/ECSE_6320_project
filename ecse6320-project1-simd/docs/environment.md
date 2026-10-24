# Environment Snapshot

Captured 2026-10-23. This records the current host/toolchain; it is not a benchmark result. Values are not inferred where the OS or tool did not report them.

## Host

- OS: Microsoft Windows 11 Enterprise, version 10.0.26200, build 26200, 64-bit.
- Execution target: native Windows/bare-metal as supplied for this project; no VM, WSL, Docker, or cloud measurements are planned.
- CPU (Windows CIM): AMD Ryzen 9 9950X 16-Core Processor, AuthenticAMD, 16 cores / 32 logical processors; reported max clock 4300 MHz.
- Memory: 66,199,183,360 bytes installed (approximately 61.7 GiB).
- uProf-reported CPU: Family `0x1a`, Model `0x44`, two CCX; supported profile type `core`; available PMCs: core 6, L3 0, DF 0, UMC 0. uProf did not name a Zen generation in its system-info output.

## Software

| Tool | Version | Executable / installation path |
|---|---|---|
| Git | 2.54.0.windows.1 | `C:\Program Files\Git\cmd\git.exe` |
| Conda | 25.11.0 | `C:\Users\CHOUDN3\AppData\Local\anaconda3\Scripts\conda.exe` |
| Python | 3.13.9 | `C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe` |
| CMake | 4.4.4 | `C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe` |
| Clang / clang++ | 23.1.4 | `C:\Program Files\LLVM\bin\clang.exe`, `clang++.exe` |
| MSYS2 | 20260611 | `C:\msys64` |
| GCC / G++ | 16.2.0 | `C:\msys64\ucrt64\bin\gcc.exe`, `g++.exe` |
| UCRT64 Make | 4.4.1 | `C:\msys64\ucrt64\bin\mingw32-make.exe` |
| Ninja | 1.13.2 | `C:\msys64\ucrt64\bin\ninja.exe` |
| GNU objdump | 2.47.20260726 | `C:\msys64\ucrt64\bin\objdump.exe` |
| AMD uProf CLI / PCM / Sys | 5.3.521.0 | `C:\Program Files\AMD\AMDuProf\bin\AMDuProfCLI.exe`, `AMDuProfPcm.exe`, `AMDPerf\AMDuProfSys.exe` |
| PowerShell | 5.1.26100.9711 | Windows PowerShell |

The normal `python` resolves to Anaconda. A WindowsApps Python alias also exists later in `where.exe` results. MSYS2 has its own UCRT64 Python dependency, isolated from normal Windows PATH; it is not the primary Python.

## Profiling Availability

AMD uProf reports the Ryzen 9 9950X and core profiling support. Its system-info output reports no L3, DF, or UMC PMCs, so direct L3 and memory-controller bandwidth measurements are unavailable. Effective bandwidth will be calculated as processed bytes / runtime; cache/DRAM transitions may be inferred cautiously from controlled working-set sweeps.

No kernels or benchmarks have been run. No BIOS, power, affinity, SMT, security, or virtualization settings were changed for this snapshot.
