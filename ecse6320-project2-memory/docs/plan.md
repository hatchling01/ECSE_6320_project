# Phase plan and gates

0. Implement, test, smoke, document, commit.
1. Five-repetition representative dependent-load hierarchy baseline.
2. Three-repetition pattern/stride/direction and mix matrices.
3. Three-repetition loaded-latency sweep, numerical knee, Little's Law.
4. Dense working-set, compact streaming sweep, representative uProf evidence, TLB sweep, large-page limitation.
5. Same-kernel small-reuse versus 1 GiB pitfall.
6. Regenerate canonical artifacts, audit every requirement, report, clean rebuild/test and final commit.

Each gate requires valid affinity/correctness, preserved raw data, parsed outputs, anomaly review, `git diff --check`, a clean phase commit, and no safety violation.

All six experimental/reporting phases completed their gates. Phase commits and final status are recorded in Git history. Phase 6 collected no new performance measurement or profiler data.
