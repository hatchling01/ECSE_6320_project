#include "aligned_buffer.hpp"
#include "kernels.hpp"
#include "reference.hpp"
#include "test_data.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

namespace {

struct ErrorStats {
    long double max_absolute = 0.0L;
    long double max_relative = 0.0L;
    bool passed = true;
};

struct Totals {
    std::size_t cases = 0;
    std::size_t passed = 0;
    long double max_absolute = 0.0L;
    long double max_relative = 0.0L;
};

template <typename T>
struct Tolerance;

template <>
struct Tolerance<float> {
    static constexpr long double absolute = 2.0e-5L;
    static constexpr long double relative = 2.0e-6L;
};

template <>
struct Tolerance<double> {
    static constexpr long double absolute = 1.0e-12L;
    static constexpr long double relative = 1.0e-12L;
};

template <typename T>
ErrorStats compare_values(const T* actual, const T* expected, std::size_t n) {
    ErrorStats stats;
    for (std::size_t i = 0; i < n; ++i) {
        const long double actual_value = static_cast<long double>(actual[i]);
        const long double expected_value = static_cast<long double>(expected[i]);
        const long double absolute_error = std::fabs(actual_value - expected_value);
        const long double relative_denominator =
            std::max(std::fabs(expected_value), Tolerance<T>::absolute);
        const long double relative_error = absolute_error / relative_denominator;

        stats.max_absolute = std::max(stats.max_absolute, absolute_error);
        stats.max_relative = std::max(stats.max_relative, relative_error);
        if (!std::isfinite(actual_value) || !std::isfinite(expected_value) ||
            absolute_error > Tolerance<T>::absolute +
                                 Tolerance<T>::relative * std::fabs(expected_value)) {
            stats.passed = false;
        }
    }
    return stats;
}

template <typename T>
ErrorStats compare_scalar(T actual, T expected) {
    return compare_values(&actual, &expected, 1);
}

void write_result(std::ofstream& csv,
                  Totals& totals,
                  const std::string& kernel,
                  const std::string& datatype,
                  std::size_t size,
                  const std::string& alignment,
                  std::size_t stride,
                  const ErrorStats& stats) {
    ++totals.cases;
    if (stats.passed) {
        ++totals.passed;
    } else {
        std::cerr << "FAIL: " << kernel << " " << datatype << " n=" << size
                  << " alignment=" << alignment << " stride=" << stride << '\n';
    }
    totals.max_absolute = std::max(totals.max_absolute, stats.max_absolute);
    totals.max_relative = std::max(totals.max_relative, stats.max_relative);

    csv << kernel << ',' << datatype << ',' << size << ',' << alignment << ',';
    if (stride != 0) {
        csv << stride;
    }
    csv << ',' << std::setprecision(18) << stats.max_absolute << ','
        << stats.max_relative << ',' << (stats.passed ? "pass" : "fail") << '\n';
}

template <typename T>
std::string datatype_name() {
    return std::is_same<T, float>::value ? "float32" : "float64";
}

template <typename T>
void verify_alignment(const T* pointer, std::size_t alignment, std::size_t offset) {
    const auto address = reinterpret_cast<std::uintptr_t>(pointer);
    const bool is_aligned = address % alignment == 0;
    if ((offset == 0 && !is_aligned) || (offset != 0 && is_aligned)) {
        throw std::runtime_error("AlignedBuffer returned an unexpected pointer alignment.");
    }
}

template <typename T>
void run_contiguous_cases(std::ofstream& csv, Totals& totals) {
    constexpr std::size_t alignment = 64;
    const std::array<std::size_t, 14> sizes = {
        0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 33, 100, 1003};
    const std::array<std::size_t, 3> offsets = {0, 1, 3};
    const std::string datatype = datatype_name<T>();
    constexpr T axpy_scalar = static_cast<T>(0.375);
    constexpr T stencil_a = static_cast<T>(0.25);
    constexpr T stencil_b = static_cast<T>(-0.5);
    constexpr T stencil_c = static_cast<T>(0.75);

    for (const std::size_t n : sizes) {
        project::AlignedBuffer<T> x(n, alignment, 3);
        project::AlignedBuffer<T> y(n, alignment, 3);
        project::AlignedBuffer<T> output(n, alignment, 3);
        std::vector<T> expected(n, T{});

        for (const std::size_t offset : offsets) {
            T* x_ptr = x.data(offset);
            T* y_ptr = y.data(offset);
            T* output_ptr = output.data(offset);
            verify_alignment(x_ptr, alignment, offset);
            verify_alignment(y_ptr, alignment, offset);
            verify_alignment(output_ptr, alignment, offset);

            const std::string alignment_name = offset == 0
                ? "aligned_64B"
                : "offset_" + std::to_string(offset) + "_elements";

            project::test_data::fill_deterministic(x_ptr, n, 1);
            project::test_data::fill_deterministic(y_ptr, n, 2);
            std::copy(y_ptr, y_ptr + n, expected.begin());
            project::reference::axpy(axpy_scalar, x_ptr, expected.data(), n);
            project::axpy(axpy_scalar, x_ptr, y_ptr, n);
            write_result(csv, totals, "axpy", datatype, n, alignment_name, 0,
                         compare_values(y_ptr, expected.data(), n));

            project::test_data::fill_deterministic(y_ptr, n, 2);
            const T expected_dot = project::reference::dot_product(x_ptr, y_ptr, n);
            const T actual_dot = project::dot_product(x_ptr, y_ptr, n);
            write_result(csv, totals, "dot_product", datatype, n, alignment_name, 0,
                         compare_scalar(actual_dot, expected_dot));

            project::test_data::fill_deterministic(y_ptr, n, 3);
            project::reference::elementwise_multiply(x_ptr, y_ptr, expected.data(), n);
            project::elementwise_multiply(x_ptr, y_ptr, output_ptr, n);
            write_result(csv, totals, "elementwise_multiply", datatype, n,
                         alignment_name, 0,
                         compare_values(output_ptr, expected.data(), n));

            project::reference::stencil_1d_three_point(
                stencil_a, stencil_b, stencil_c, x_ptr, expected.data(), n);
            project::stencil_1d_three_point(
                stencil_a, stencil_b, stencil_c, x_ptr, output_ptr, n);
            write_result(csv, totals, "stencil_1d_three_point", datatype, n,
                         alignment_name, 0,
                         compare_values(output_ptr, expected.data(), n));
        }
    }
}

template <typename T>
void run_stride_cases(std::ofstream& csv, Totals& totals) {
    constexpr std::size_t alignment = 64;
    const std::array<std::size_t, 14> sizes = {
        0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 33, 100, 1003};
    const std::array<std::size_t, 4> strides = {1, 2, 4, 8};
    const std::string datatype = datatype_name<T>();

    for (const std::size_t n : sizes) {
        for (const std::size_t stride : strides) {
            const std::size_t storage_size = n == 0 ? 0 : (n - 1) * stride + 1;
            project::AlignedBuffer<T> x(storage_size, alignment);
            project::AlignedBuffer<T> y(storage_size, alignment);
            project::AlignedBuffer<T> output(storage_size, alignment);
            std::vector<T> expected(n, T{});
            std::vector<T> actual(n, T{});

            project::test_data::fill_deterministic(x.data(), storage_size, 11);
            project::test_data::fill_deterministic(y.data(), storage_size, 23);
            project::reference::elementwise_multiply_strided(
                x.data(), stride, y.data(), stride, expected.data(), 1, n);
            project::elementwise_multiply_strided(
                x.data(), stride, y.data(), stride, output.data(), stride, n);
            for (std::size_t i = 0; i < n; ++i) {
                actual[i] = output.data()[i * stride];
            }
            write_result(csv, totals, "elementwise_multiply_strided", datatype,
                         n, "aligned_64B", stride,
                         compare_values(actual.data(), expected.data(), n));
        }
    }
}

template <typename T>
void run_suite(std::ofstream& csv, Totals& totals) {
    run_contiguous_cases<T>(csv, totals);
    run_stride_cases<T>(csv, totals);
}

void write_type_summary(std::ofstream& summary,
                        const std::string& datatype,
                        const Totals& totals) {
    summary << "| " << datatype << " | " << totals.passed << '/' << totals.cases
            << " | " << std::setprecision(8) << totals.max_absolute << " | "
            << totals.max_relative << " |\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    const std::string csv_path = argc > 1 ? argv[1] : "correctness_results.csv";
    const std::string summary_path = argc > 2 ? argv[2] : "correctness_summary.md";
    std::ofstream csv(csv_path);
    if (!csv) {
        std::cerr << "Unable to open correctness CSV: " << csv_path << '\n';
        return 2;
    }
    csv << "kernel,datatype,size,alignment_condition,stride,max_absolute_error,"
           "max_relative_error,pass_fail\n";

    Totals float_totals;
    Totals double_totals;
    run_suite<float>(csv, float_totals);
    run_suite<double>(csv, double_totals);
    csv.close();

    const bool passed = float_totals.passed == float_totals.cases &&
                        double_totals.passed == double_totals.cases;
    std::ofstream summary(summary_path);
    if (!summary) {
        std::cerr << "Unable to open correctness summary: " << summary_path << '\n';
        return 2;
    }
    summary << "# Phase 1 Correctness Summary\n\n"
            << "Correctness validation only; this is not performance data. No "
               "benchmark was run.\n\n"
            << "- Cases: " << (float_totals.cases + double_totals.cases) << "\n"
            << "- Passed: " << (float_totals.passed + double_totals.passed) << "\n"
            << "- Status: " << (passed ? "PASS" : "FAIL") << "\n"
            << "- Sizes: 0, 1, 2, 3, 7, 8, 15, 16, 17, 31, 32, 33, 100, 1003\n"
            << "- Contiguous pointer conditions: 64-byte-aligned base, plus safe "
               "offsets of 1 and 3 elements.\n"
            << "- Stride cases: elementwise multiply at strides 1, 2, 4, and 8.\n"
            << "- Stencil boundaries: copy input endpoints; apply the three-point "
               "formula to interior elements.\n\n"
            << "| Datatype | Passed / cases | Max absolute error | Max relative error |\n"
            << "|---|---:|---:|---:|\n";
    write_type_summary(summary, "float32", float_totals);
    write_type_summary(summary, "float64", double_totals);
    summary << "\nTolerance rule: `abs(error) <= absolute_tolerance + "
               "relative_tolerance * abs(reference)`. float32 uses absolute "
               "2e-5 and relative 2e-6; float64 uses absolute 1e-12 and "
               "relative 1e-12. Relative error is normalized by "
               "max(abs(reference), absolute_tolerance) for reporting.\n";

    std::cout << "Correctness cases: " << (float_totals.cases + double_totals.cases)
              << "; passed: " << (float_totals.passed + double_totals.passed)
              << "; max absolute error: "
              << std::setprecision(8)
              << std::max(float_totals.max_absolute, double_totals.max_absolute)
              << "; max relative error: "
              << std::max(float_totals.max_relative, double_totals.max_relative)
              << '\n';
    std::cout << "Correctness CSV: " << csv_path << '\n'
              << "Correctness summary: " << summary_path << '\n';
    return passed ? 0 : 1;
}