#pragma once

#include <cstddef>
#include <cstdint>

namespace project::test_data {

template <typename T>
void fill_deterministic(T* values, std::size_t n, std::uint32_t seed);

extern template void fill_deterministic<float>(float*, std::size_t, std::uint32_t);
extern template void fill_deterministic<double>(double*, std::size_t, std::uint32_t);

}  // namespace project::test_data