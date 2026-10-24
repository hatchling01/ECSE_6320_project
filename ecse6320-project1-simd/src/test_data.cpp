#include "test_data.hpp"

#include <cstdint>

namespace project::test_data {

template <typename T>
void fill_deterministic(T* values, std::size_t n, std::uint32_t seed) {
    for (std::size_t i = 0; i < n; ++i) {
        const std::uint64_t mixed =
            (static_cast<std::uint64_t>(i) * 37U +
             static_cast<std::uint64_t>(seed) * 17U + 11U) % 101U;
        const int numerator = static_cast<int>(mixed) - 50;
        values[i] = static_cast<T>(numerator) / static_cast<T>(19);
    }
}

template void fill_deterministic<float>(float*, std::size_t, std::uint32_t);
template void fill_deterministic<double>(double*, std::size_t, std::uint32_t);

}  // namespace project::test_data