#pragma once

#include <cstdint>
#include <string>

struct StreamResult {
    std::uint64_t working_set_bytes{};
    std::uint64_t stride_bytes{};
    std::uint64_t operations{};
    std::uint64_t read_operations{};
    std::uint64_t write_operations{};
    std::uint64_t useful_read_bytes{};
    std::uint64_t useful_write_bytes{};
    double elapsed_seconds{};
    double ns_per_operation{};
    double useful_gib_per_s{};
    double actual_read_pct{};
    std::uint64_t checksum{};
    bool validation_ok{};
    bool affinity_ok{};
    unsigned requested_cpu{};
    unsigned observed_cpu{};
    std::uint64_t seed{};
    std::string pattern;
    std::uint64_t available_before{};
    std::uint64_t available_after{};
};

StreamResult run_stream(std::uint64_t bytes, std::uint64_t stride,
                        std::uint64_t operations, const std::string& pattern,
                        unsigned read_pct, unsigned cpu, std::uint64_t seed);
bool stream_self_test();

