#pragma once

#include <cstdint>
#include <vector>

struct CpuTopology {
    std::vector<unsigned> one_logical_per_core;
    unsigned logical_processors{};
    unsigned processor_groups{};
    unsigned numa_nodes{};
};

CpuTopology discover_topology();
bool pin_current_thread(unsigned cpu_id);
unsigned current_cpu();
std::uint64_t current_thread_affinity_mask();

