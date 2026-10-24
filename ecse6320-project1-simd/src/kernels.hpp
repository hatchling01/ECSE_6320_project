#pragma once

#include <cstddef>

namespace project {

template <typename T>
void axpy(T a, const T* x, T* y, std::size_t n) noexcept;

template <typename T>
T dot_product(const T* x, const T* y, std::size_t n) noexcept;

template <typename T>
void elementwise_multiply(const T* x, const T* y, T* z, std::size_t n) noexcept;

template <typename T>
void elementwise_multiply_strided(
    const T* x,
    std::size_t x_stride,
    const T* y,
    std::size_t y_stride,
    T* z,
    std::size_t z_stride,
    std::size_t n) noexcept;

template <typename T>
void stencil_1d_three_point(
    T a,
    T b,
    T c,
    const T* x,
    T* y,
    std::size_t n) noexcept;

extern template void axpy<float>(float, const float*, float*, std::size_t) noexcept;
extern template void axpy<double>(double, const double*, double*, std::size_t) noexcept;
extern template float dot_product<float>(const float*, const float*, std::size_t) noexcept;
extern template double dot_product<double>(const double*, const double*, std::size_t) noexcept;
extern template void elementwise_multiply<float>(const float*, const float*, float*, std::size_t) noexcept;
extern template void elementwise_multiply<double>(const double*, const double*, double*, std::size_t) noexcept;
extern template void elementwise_multiply_strided<float>(
    const float*, std::size_t, const float*, std::size_t, float*, std::size_t, std::size_t) noexcept;
extern template void elementwise_multiply_strided<double>(
    const double*, std::size_t, const double*, std::size_t, double*, std::size_t, std::size_t) noexcept;
extern template void stencil_1d_three_point<float>(
    float, float, float, const float*, float*, std::size_t) noexcept;
extern template void stencil_1d_three_point<double>(
    double, double, double, const double*, double*, std::size_t) noexcept;

}  // namespace project