# Anomalies and retained failures

- Phase 0: GCC 16.2 was discoverable, but both CMake's compiler probe and a direct compilation exited nonzero without compiler diagnostics. No installation was changed. The already-installed Clang 23.1.4 succeeded with the MinGW/UCRT target and became the documented active compiler.
- Failed build directories are ignored build artifacts and retained locally until final cleanup if useful; they contain no measurement data.
- The first CTest invocation lacked the MSYS2 runtime directory in its environment and failed at process startup (`0xc0000139`); the smoke suite itself passed because its Python runner supplied the runtime path. CTest was subsequently configured with the same explicit runtime path and retested.
- Phase 4's 512 MiB dependent-load set had 15.9% CV and a 128.96 ns median, above the 1 GiB median of 118.87 ns. It stayed below the 20% rerun threshold; all samples remain canonical and the non-monotonic point is not used as a boundary.
- uProf sampled process-level counter values were not monotonic across every representative size. Operation counts and setup costs differ, and no direct L3 event exists; interpretation is limited to supporting L1/L2/DTLB evidence.
