#pragma once

#include "pointer_chase.h"

LatencyResult run_tlb_latency(std::uint64_t pages, std::uint64_t operations,
                              unsigned cpu, std::uint64_t seed);

