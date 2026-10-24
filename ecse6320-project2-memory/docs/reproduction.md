# Reproduction guide

Use native Windows from the repository root. No administrator rights or setting changes are required. Active automation is Python, never `.ps1`.

## Exact tools

- Python: `C:\Users\CHOUDN3\AppData\Local\anaconda3\python.exe` 3.13.9 (numpy 2.3.5, pandas 2.3.3, matplotlib 3.10.6)
- CMake: `C:\Users\CHOUDN3\AppData\Local\Microsoft\WinGet\Packages\Kitware.CMake_Microsoft.Winget.Source_8wekyb3d8bbwe\cmake-4.4.4-windows-x86_64\bin\cmake.exe`
- Ninja: `C:\msys64\ucrt64\bin\ninja.exe` 1.13.2
- Active compiler: `C:\Program Files\LLVM\bin\clang++.exe` 23.1.4, target `x86_64-w64-windows-gnu`, UCRT sysroot, `-O3 -DNDEBUG -march=native`
- uProf: `C:\Program Files\AMD\AMDuProf\bin\AMDuProfCLI.exe` 5.3.521.0

Configure with Ninja, the Clang path, compiler target, `C:/msys64/ucrt64` sysroot, `C:/msys64/ucrt64/bin/windres.exe`, Release, and the recorded release flags. Build with `cmake --build <dir> -j 4`; test with `ctest --test-dir <dir> --output-on-failure`. CTest adds the MSYS2 UCRT runtime path.

The executable modes are `info`, `self-test`, `calibrate`, `latency`, `stream`, `mix`, `loaded-latency`, and `tlb`; run without executable PowerShell scripts. Phase orchestration is `python scripts/python/run_experiment.py phaseN`. It refuses to overwrite a raw filename and enforces allocation/RAM gates. Do not run phases merely to regenerate the report.

Canonical raw JSON is in `data/raw/phase1` through `phase5`; smoke is separately labeled under `data/raw/smoke`. Run `parse_results.py`, `analyze_uprof.py`, and `plot_results.py` to regenerate parsed CSVs and figures, then `validate_results.py`.

uProf reproduction uses `run_uprof.py representative` and `run_uprof.py tlb`; commands and events are captured in manifests. The profiles are process-level supporting evidence. Binary sessions remain locally under ignored `profiler/raw`; portable CSV reports and manifests are versioned.

CPU 0 is the primary thread. Loaded-latency uses 0 for the probe and 2,4,…,30 for workers. Large pages are not reproducible in this configuration because the token lacks `SeLockMemoryPrivilege`; do not alter policy.
