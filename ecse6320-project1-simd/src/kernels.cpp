#include "kernels.hpp"

namespace project {
namespace {

template <typename T>
void axpy_impl(T a, const T* x, T* y, std::size_t n) noexcept {
    for (std::size_t i = 0; i < n; ++i) {
        y[i] = a * x[i] + y[i];
    }
}

template <typename T>
T dot_product_impl(const T* x, const T* y, std::size_t n) noexcept {
    T sum{};
    for (std::size_t i = 0; i < n; ++i) {
        sum += x[i] * y[i];
    }
    return sum;
}

template <typename T>
void elementwise_multiply_impl(const T* x, const T* y, T* z, std::size_t n) noexcept {
    for (std::size_t i = 0; i < n; ++i) {
        z[i] = x[i] * y[i];
    }
}

template <typename T>
void elementwise_multiply_strided_impl(
    const T* x,
    std::size_t x_stride,
    const T* y,
    std::size_t y_stride,
    T* z,
    std::size_t z_stride,
    std::size_t n) noexcept {
    for (std::size_t i = 0; i < n; ++i) {
        z[i * z_stride] = x[i * x_stride] * y[i * y_stride];
    }
}

template <typename T>
void stencil_1d_three_point_impl(
    T a,
    T b,
    T c,
    const T* x,
    T* y,
    std::size_t n) noexcept {
    if (n == 0) {
        return;
    }
    y[0] = x[0];
    if (n == 1) {
        return;
    }
    y[n - 1] = x[n - 1];
    for (std::size_t i = 1; i + 1 < n; ++i) {
        y[i] = a * x[i - 1] + b * x[i] + c * x[i + 1];
    }
}

}  // namespace

template <typename T>
void axpy(T a, const T* x, T* y, std::size_t n) noexcept {
    axpy_impl(a, x, y, n);
}

template <typename T>
T dot_product(const T* x, const T* y, std::size_t n) noexcept {
    return dot_product_impl(x, y, n);
}

template <typename T>
void elementwise_multiply(const T* x, const T* y, T* z, std::size_t n) noexcept {
    elementwise_multiply_impl(x, y, z, n);
}

template <typename T>
void elementwise_multiply_strided(
    const T* x,
    std::size_t x_stride,
    const T* y,
    std::size_t y_stride,
    T* z,
    std::size_t z_stride,
    std::size_t n) noexcept {
    elementwise_multiply_strided_impl(x, x_stride, y, y_stride, z, z_stride, n);
}

template <typename T>
void stencil_1d_three_point(
    T a,
    T b,
    T c,
    const T* x,
    T* y,
    std::size_t n) noexcept {
    stencil_1d_three_point_impl(a, b, c, x, y, n);
}

template void axpy<float>(float, const float*, float*, std::size_t) noexcept;
template void axpy<double>(double, const double*, double*, std::size_t) noexcept;
template float dot_product<float>(const float*, const float*, std::size_t) noexcept;
template double dot_product<double>(const double*, const double*, std::size_t) noexcept;
template void elementwise_multiply<float>(const float*, const float*, float*, std::size_t) noexcept;
template void elementwise_multiply<double>(const double*, const double*, double*, std::size_t) noexcept;
template void elementwise_multiply_strided<float>(
    const float*, std::size_t, const float*, std::size_t, float*, std::size_t, std::size_t) noexcept;
template void elementwise_multiply_strided<double>(
    const double*, std::size_t, const double*, std::size_t, double*, std::size_t, std::size_t) noexcept;
template void stencil_1d_three_point<float>(float, float, float, const float*, float*, std::size_t) noexcept;
template void stencil_1d_three_point<double>(double, double, double, const double*, double*, std::size_t) noexcept;

}  // namespace project