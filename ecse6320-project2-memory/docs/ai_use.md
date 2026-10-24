# AI-use disclosure

Codex assisted with repository organization, C++ benchmark implementation, correctness and resource tests, affinity/timing code, experiment scripting, parser/statistics, uProf command construction, plotting, documentation and analysis drafting. Measurements and claims are grounded in native output, correctness checks, repeated trials, retained raw data, uProf reports and the documented methodology. AI did not independently verify undocumented hardware internals.

The official AMD product page was used only to corroborate published aggregate cache capacities. Local topology, timing and counter statements remain tied to Windows, native benchmark and uProf evidence. No AI-generated value is presented as a measurement.

## Independent validation, modification, and rejection

Codex-generated benchmark code was independently validated with correctness and resource tests. Thread affinity, QPC timing behavior, parser round trips, exact operation mixes, and write checks were explicitly tested. When the intended GCC toolchain failed in practice, the documented Clang fallback was used instead of forcing the original plan.

Large pages were not enabled because doing so required a system/security-policy change. Direct L3, Data Fabric, UMC, and memory-controller counters were unavailable, so interpretations were constrained to timing and the available L1/L2/TLB evidence. The predefined saturation-knee criterion was not met; the result was reported as unresolved rather than selecting a knee after observing the data. Raw anomalies and non-monotonic results were retained rather than discarded. Codex did not independently verify undocumented AMD or Apple internals.

## Representative AI workflow

Codex assisted with native benchmark implementation, affinity/timing code, experiment scripting, parser/statistics code, uProf command construction, plotting, and documentation/analysis drafting. These were assistance tasks; measurements and hardware claims remained subject to independent tests, raw outputs, and available profiler/tool evidence.
