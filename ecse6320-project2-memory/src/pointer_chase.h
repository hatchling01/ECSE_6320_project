#pragma once

#include <cstdint>
#include <string>
#include <vector>

struct LatencyResult {
    std::uint64_t working_set_bytes{};
    std::uint64_t spacing_bytes{};
    std::uint64_t operations{};
    double elapsed_seconds{};
    double ns_per_load{};
    std::uint64_t final_index{};
    unsigned requested_cpu{};
    unsigned observed_cpu{};
    bool affinity_ok{};
    std::uint64_t seed{};
    std::uint64_t available_before{};
    std::uint64_t available_after{};
};

struct LoadedResult {
    unsigned workers{};
    std::vector<unsigned> worker_cpus;
    unsigned probe_cpu{};
    bool affinity_ok{};
    std::uint64_t total_allocation_bytes{};
    std::uint64_t worker_operations{};
    std::uint64_t probe_operations{};
    double elapsed_seconds{};
    double worker_gib_per_s{};
    double worker_ops_per_s{};
    double probe_ns_per_load{};
    double l_inferred{};
    std::uint64_t probe_final_index{};
    std::uint64_t checksum{};
    std::uint64_t available_before{};
    std::uint64_t available_after{};
};

LatencyResult run_pointer_latency(std::uint64_t bytes, std::uint64_t spacing,
                                  std::uint64_t operations, unsigned cpu,
                                  std::uint64_t seed, unsigned target_ms = 250);
LoadedResult run_loaded_latency(unsigned workers, std::uint64_t probe_bytes,
                                std::uint64_t worker_region_bytes,
                                unsigned warmup_ms, unsigned duration_ms,
                                std::uint64_t seed);
bool pointer_chain_self_test();
std::uint64_t available_physical_memory();

