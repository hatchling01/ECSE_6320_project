#include "timer.h"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <stdexcept>

QpcTimer::QpcTimer() {
    LARGE_INTEGER value{};
    if (!QueryPerformanceFrequency(&value) || value.QuadPart <= 0) {
        throw std::runtime_error("QueryPerformanceFrequency failed");
    }
    frequency = value.QuadPart;
}

std::int64_t QpcTimer::now() const {
    LARGE_INTEGER value{};
    if (!QueryPerformanceCounter(&value)) {
        throw std::runtime_error("QueryPerformanceCounter failed");
    }
    return value.QuadPart;
}

double QpcTimer::seconds(std::int64_t start, std::int64_t end) const {
    return static_cast<double>(end - start) / static_cast<double>(frequency);
}

double QpcTimer::calibrated_overhead_ns(std::uint64_t iterations) const {
    const auto start = now();
    for (std::uint64_t i = 0; i < iterations; ++i) {
        (void)now();
    }
    const auto end = now();
    return seconds(start, end) * 1.0e9 / static_cast<double>(iterations);
}

