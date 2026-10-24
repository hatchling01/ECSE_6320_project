# AI Use Disclosure

Codex assisted with repository setup, C++ implementation, experiment and analysis scripts, debugging, data processing, plotting, and project documentation, including this final report. The project specifications, original hypotheses, and collected raw measurements remain the source of experimental requirements and measured values.

AI-generated code and explanations were checked against correctness tests, compiler diagnostics, targeted disassembly, preserved raw measurements, and AMD uProf evidence where applicable. No AI-generated value is presented as a measurement. Raw observations and anomalies were retained; analysis conclusions are qualified by sample variability and available hardware counters. Phase 6 used existing data only and collected no benchmark timings, uProf profiles, or new plots.

## Independent validation, modification, and rejection

Codex-generated C++ and scripts were independently checked with correctness tests. Compiler diagnostics and targeted disassembly were used to verify emitted SIMD/vector instructions rather than trusting generated source, compiler flags, or optimization reports alone. Conclusions were checked against retained raw measurements and available AMD uProf evidence.

Results showing compressed or absent SIMD speedup at large working sets were retained rather than changed to match the expected optimization. uProf limitations were respected: useful/effective bandwidth was not presented as directly measured physical DRAM traffic, and unavailable L3/DF/UMC counters were not invented. Generated interpretations that exceeded the measured data or profiler evidence were rejected or explicitly qualified.

## Representative AI workflow

Codex assisted with repository setup, C++ implementation, experiment automation, debugging, parsing, plotting, and documentation/analysis drafting. These were assistance tasks; measurements came from the independently executed benchmark and profiling workflow and were validated as described above.
