#pragma once

#include <cstdint>

struct QpcTimer {
    std::int64_t frequency{};
    QpcTimer();
    std::int64_t now() const;
    double seconds(std::int64_t start, std::int64_t end) const;
    double calibrated_overhead_ns(std::uint64_t iterations = 200000) const;
};

