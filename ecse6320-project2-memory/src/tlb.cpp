#include "tlb.h"

#include <stdexcept>

LatencyResult run_tlb_latency(std::uint64_t pages, std::uint64_t operations,
                              unsigned cpu, std::uint64_t seed) {
    if (pages < 2 || pages > (8ull * 1024 * 1024 * 1024 / 4096)) {
        throw std::invalid_argument("page count outside safe range");
    }
    return run_pointer_latency(pages * 4096, 4096, operations, cpu, seed, 250);
}

