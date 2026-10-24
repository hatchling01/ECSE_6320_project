# Project 2 dependency comparison

## Mac dependency inventory

| Dependency | Purpose | Required / optional | Version if known | Mac-specific? |
|---|---|---|---|---|
| Apple Clang | Build native C benchmark and validation probe | Required | 21.0.0 (`clang-2100.3.34.2`) | Yes |
| POSIX pthreads | Background workers and synchronization | Required | macOS system library | No, but API usage is POSIX |
| GNU Make-compatible `make` | Build and task entry points | Required | Not documented in source project | No |
| Python | Orchestration, validation, analysis | Required | 3.13.15 | No |
| Matplotlib | Generate plots | Required | 3.10.8 | No |
| Python standard library | CSV/JSON, statistics, subprocesses, XML/plist parsing | Required | Python 3.13.15 | No |
| `clock_gettime(CLOCK_MONOTONIC)` | Wall-clock timing | Required | macOS system API | Platform API |
| `pthread_set_qos_class_self_np` | User-interactive scheduling hint | Required by current source, but failure is nonfatal | macOS system API | Yes |
| `os_signpost` | Mark profiled measurement regions | Required for counter workflow | macOS system API | Yes |
| Xcode / Instruments via `xcrun xctrace` | Guided counter recording/export | Optional for timing suite; required for counter evidence | Xcode 26.0.1 | Yes |
| `caffeinate` | Prevent idle sleep during runs | Operationally recommended | System version not documented | Yes |
| `sysctl`, `sw_vers`, `uname`, `pmset`, `vm_stat`, `xcode-select` | Environment capture | Required by current capture script | System versions not documented | Yes |

The recorded environment also contained NumPy 2.5.4, Pillow 13.0.0, and Matplotlib transitive dependencies. The project scripts do not import NumPy or Pandas, so they are not listed as direct project requirements.

## Functional comparison

| Function | Windows Project 2 | Mac Project 2 | Consequence |
|---|---|---|---|
| Native compiler | Clang 23.1.4; CMake/Ninja build | Apple Clang 21.0.0; Makefile | Both use optimized native code; build recipes are platform-specific |
| Language | C++ | C11 | Implementations are analogous, not shared binaries |
| Timing | Windows QPC | `CLOCK_MONOTONIC` | Both report elapsed nanoseconds without fixed-frequency cycle conversion |
| Thread control | `SetThreadAffinityMask` to physical-core representatives | pthread workers plus user-interactive QoS hint; no hard affinity | Mac placement has greater scheduler uncertainty |
| Profiler | AMD uProf 5.3.521.0 | Xcode/Instruments 26.0.1 | Counter names, scope, and export limitations differ |
| Cache evidence | Process-level L1/L2 miss evidence; direct L3 unavailable | L1D-related stall percentages; raw miss counts unavailable | Counter magnitudes are not directly comparable |
| TLB evidence | Normal-page sweep plus low/high DTLB profiles | Page-locality sweep; attempted raw event export failed | Only behavioral curves can be contrasted, at low comparability |
| Page size | 4 KiB normal; 2 MiB large-page privilege unavailable | 16 KiB native; explicit 2 MiB allocation rejected | Page-count experiments represent different memory spans |
| Analysis | Python 3.13.9, NumPy, Pandas, Matplotlib | Python 3.13.15, Matplotlib; standard-library CSV/statistics | Mac analysis has fewer direct third-party dependencies |
| Orchestration | Python because PowerShell script execution is restricted | Python invoked through Make and `caffeinate` | Both retain scriptable, auditable workflows |
| Environment capture | Windows/CIM and project configuration | `sysctl`, `sw_vers`, `pmset`, `vm_stat` | Evidence is rich but platform schemas differ |
| Elevated privileges | Not required; unavailable large-page privilege documented | No sudo required; no security changes | Baseline reproduction is unprivileged on both systems |

## Reproduction impact

The Mac baseline is compact: Apple Clang, Make, Python, and Matplotlib reproduce timing and plots. Counter reproduction is harder because it depends on an installed matching Xcode/Instruments version, private/export-sensitive trace formats, and signpost parsing. The Windows build has more tools (CMake, Ninja, NumPy/Pandas, AMD uProf) but stronger hard-affinity control. AMD uProf is Windows/AMD-specific; Instruments, `xctrace`, QoS, signposts, and the macOS environment commands are Mac-specific.
