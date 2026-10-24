#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "kernels.hpp"
#include "reference.hpp"
#include "test_data.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <vector>

namespace {

struct Options {
    std::string kernel;
    std::string datatype;
    std::string build;
    std::string compiler;
    std::string flags;
    std::string output;
    std::size_t n = 0;
    std::uint64_t target_working_set_bytes = 0;
    std::size_t warmups = 0;
    std::size_t repetitions = 0;
    std::size_t batch = 1;
    std::size_t stride = 1;
    std::size_t span_elements = 0;
    bool verify_only = false;
    bool dot_accuracy_only = false;
};

volatile long double benchmark_sink = 0.0L;

std::string csv_quote(const std::string& value) {
    std::string result = "\"";
    for (const char character : value) {
        if (character == '"') {
            result += "\"\"";
        } else {
            result += character;
        }
    }
    result += '"';
    return result;
}

std::string timestamp_utc() {
    using namespace std::chrono;
    const auto now = system_clock::now();
    const auto milliseconds_part = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;
    const std::time_t now_time = system_clock::to_time_t(now);
    std::tm utc_time{};
    gmtime_s(&utc_time, &now_time);

    std::ostringstream output;
    output << std::put_time(&utc_time, "%Y-%m-%dT%H:%M:%S") << '.'
           << std::setw(3) << std::setfill('0') << milliseconds_part.count() << 'Z';
    return output.str();
}

std::string set_single_thread_affinity() {
    DWORD_PTR process_mask = 0;
    DWORD_PTR system_mask = 0;
    if (!GetProcessAffinityMask(GetCurrentProcess(), &process_mask, &system_mask) ||
        (process_mask & static_cast<DWORD_PTR>(1)) == 0) {
        throw std::runtime_error("Logical processor 0 is not available to this process.");
    }
    if (SetThreadAffinityMask(GetCurrentThread(), static_cast<DWORD_PTR>(1)) == 0) {
        throw std::runtime_error("Unable to pin benchmark thread to logical processor 0.");
    }
    return "logical_cpu_0;mask=0x1";
}

Options parse_options(int argc, char* argv[]) {
    std::map<std::string, std::string> values;
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string key = argv[index];
        if (key == "--verify-only") {
            options.verify_only = true;
            continue;
        }
        if (key == "--dot-accuracy-only") {
            options.dot_accuracy_only = true;
            continue;
        }
        if (key.rfind("--", 0) != 0 || index + 1 >= argc) {
            throw std::invalid_argument("Expected --key value arguments.");
        }
        values[key] = argv[++index];
    }

    const auto read_string = [&values](const std::string& key) -> std::string {
        const auto found = values.find(key);
        if (found == values.end()) {
            throw std::invalid_argument("Missing option " + key);
        }
        return found->second;
    };
    const auto read_size = [&read_string](const std::string& key) {
        return static_cast<std::size_t>(std::stoull(read_string(key)));
    };

    options.kernel = read_string("--kernel");
    options.datatype = read_string("--datatype");
    options.build = read_string("--build");
    options.compiler = read_string("--compiler");
    options.flags = read_string("--flags");
    options.n = read_size("--n");
    options.target_working_set_bytes = std::stoull(read_string("--target-working-set-bytes"));
    options.warmups = read_size("--warmups");
    options.repetitions = read_size("--repetitions");
    options.batch = read_size("--batch");
    if (values.count("--stride") != 0) {
        options.stride = read_size("--stride");
    }
    options.span_elements = values.count("--span-elements") != 0
        ? read_size("--span-elements")
        : options.n;
    if (!options.verify_only) {
        options.output = read_string("--output");
    }
    if (options.n == 0 || options.batch == 0 || options.stride == 0 ||
        options.span_elements == 0) {
        throw std::invalid_argument("N, stride, span, and batch count must be positive.");
    }
    if (options.kernel == "elementwise_multiply_strided") {
        if (options.n != options.span_elements / options.stride) {
            throw std::invalid_argument("Strided N must equal floor(span_elements / stride).");
        }
    } else if (options.stride != 1 || options.span_elements != options.n) {
        throw std::invalid_argument("Stride/span options are supported only for strided multiply.");
    }
    return options;
}

std::size_t arrays_in_working_set(const std::string& kernel) {
    if (kernel == "elementwise_multiply" || kernel == "elementwise_multiply_strided") {
        return 3;
    }
    if (kernel == "axpy" || kernel == "dot_product" || kernel == "stencil_1d_three_point") {
        return 2;
    }
    throw std::invalid_argument("Unsupported kernel: " + kernel);
}

std::uint64_t flops_per_element(const std::string& kernel) {
    if (kernel == "elementwise_multiply" || kernel == "elementwise_multiply_strided") {
        return 1;
    }
    if (kernel == "axpy" || kernel == "dot_product") {
        return 2;
    }
    throw std::invalid_argument("Unsupported kernel: " + kernel);
}

std::uint64_t useful_bytes_per_element(const std::string& kernel) {
    if (kernel == "dot_product") {
        return 2;
    }
    if (kernel == "axpy" || kernel == "elementwise_multiply" ||
        kernel == "elementwise_multiply_strided") {
        return 3;
    }
    throw std::invalid_argument("Unsupported kernel: " + kernel);
}

template <typename T>
T axpy_call(T a, T b, T c, const T* x, T* y, T* output, std::size_t n) {
    (void)b;
    (void)c;
    (void)output;
    project::axpy(a, x, y, n);
    return T{};
}

template <typename T>
T dot_call(T a, T b, T c, const T* x, T* y, T* output, std::size_t n) {
    (void)a;
    (void)b;
    (void)c;
    (void)output;
    return project::dot_product(x, y, n);
}

template <typename T>
T multiply_call(T a, T b, T c, const T* x, T* y, T* output, std::size_t n) {
    (void)a;
    (void)b;
    (void)c;
    project::elementwise_multiply(x, y, output, n);
    return T{};
}

template <typename T>
T stencil_call(T a, T b, T c, const T* x, T* y, T* output, std::size_t n) {
    (void)y;
    project::stencil_1d_three_point(a, b, c, x, output, n);
    return T{};
}

template <typename T>
using KernelCall = T (*)(T, T, T, const T*, T*, T*, std::size_t);

template <typename T>
KernelCall<T> select_kernel(const std::string& kernel) {
    if (kernel == "axpy") {
        return &axpy_call<T>;
    }
    if (kernel == "dot_product") {
        return &dot_call<T>;
    }
    if (kernel == "elementwise_multiply") {
        return &multiply_call<T>;
    }
    if (kernel == "stencil_1d_three_point") {
        return &stencil_call<T>;
    }
    throw std::invalid_argument("Unsupported kernel: " + kernel);
}

template <typename T>
struct Tolerance {
    static constexpr long double absolute = std::is_same<T, float>::value ? 2.0e-5L : 1.0e-12L;
    static constexpr long double relative = std::is_same<T, float>::value ? 2.0e-6L : 1.0e-12L;
};

template <typename T>
bool matches_reference(T actual, T expected, long double& max_absolute, long double& max_relative) {
    const long double actual_value = static_cast<long double>(actual);
    const long double expected_value = static_cast<long double>(expected);
    const long double absolute_error = std::fabs(actual_value - expected_value);
    const long double relative_error = absolute_error /
        std::max(std::fabs(expected_value), Tolerance<T>::absolute);
    max_absolute = std::max(max_absolute, absolute_error);
    max_relative = std::max(max_relative, relative_error);
    return std::isfinite(actual_value) && std::isfinite(expected_value) &&
           absolute_error <= Tolerance<T>::absolute +
                                Tolerance<T>::relative * std::fabs(expected_value);
}

template <typename T>
int run(const Options& options, const std::string& affinity) {
    const T coefficient_a = static_cast<T>(0.375);
    const T coefficient_b = static_cast<T>(-0.25);
    const T coefficient_c = static_cast<T>(0.625);
    const bool strided = options.kernel == "elementwise_multiply_strided";
    const std::size_t storage_elements = strided ? options.span_elements : options.n;
    std::vector<T> x(storage_elements);
    std::vector<T> y;
    if (options.kernel != "stencil_1d_three_point") {
        y.resize(storage_elements);
    }
    std::vector<T> output;
    if (options.kernel == "elementwise_multiply" ||
        strided ||
        options.kernel == "stencil_1d_three_point") {
        output.resize(storage_elements);
    }
    project::test_data::fill_deterministic(x.data(), storage_elements, 17);
    if (!y.empty()) {
        project::test_data::fill_deterministic(y.data(), storage_elements, 41);
    }

    const KernelCall<T> kernel = strided ? nullptr : select_kernel<T>(options.kernel);
    const auto verify = [&]() {
        std::vector<T> expected(storage_elements, T{});
        long double max_absolute = 0.0L;
        long double max_relative = 0.0L;
        bool pass = true;
        if (options.kernel == "axpy") {
            expected = y;
            project::reference::axpy(coefficient_a, x.data(), expected.data(), options.n);
            project::test_data::fill_deterministic(y.data(), options.n, 41);
            kernel(coefficient_a, coefficient_b, coefficient_c,
                   x.data(), y.data(), output.data(), options.n);
            for (std::size_t i = 0; i < options.n; ++i) {
                pass = matches_reference(y[i], expected[i], max_absolute, max_relative) && pass;
            }
        } else if (options.kernel == "dot_product") {
            const T actual = kernel(coefficient_a, coefficient_b, coefficient_c,
                                    x.data(), y.data(), output.data(), options.n);
            const T reference = project::reference::dot_product(x.data(), y.data(), options.n);
            pass = matches_reference(actual, reference, max_absolute, max_relative);
        } else if (options.kernel == "elementwise_multiply") {
            project::reference::elementwise_multiply(
                x.data(), y.data(), expected.data(), options.n);
            kernel(coefficient_a, coefficient_b, coefficient_c,
                   x.data(), y.data(), output.data(), options.n);
            for (std::size_t i = 0; i < options.n; ++i) {
                pass = matches_reference(output[i], expected[i], max_absolute, max_relative) && pass;
            }
        } else if (strided) {
            project::reference::elementwise_multiply_strided(
                x.data(), options.stride, y.data(), options.stride,
                expected.data(), options.stride, options.n);
            project::elementwise_multiply_strided(
                x.data(), options.stride, y.data(), options.stride,
                output.data(), options.stride, options.n);
            for (std::size_t i = 0; i < options.n; ++i) {
                const std::size_t index = i * options.stride;
                pass = matches_reference(output[index], expected[index],
                                         max_absolute, max_relative) && pass;
            }
        } else {
            project::reference::stencil_1d_three_point(
                coefficient_a, coefficient_b, coefficient_c,
                x.data(), expected.data(), options.n);
            kernel(coefficient_a, coefficient_b, coefficient_c,
                   x.data(), y.data(), output.data(), options.n);
            for (std::size_t i = 0; i < options.n; ++i) {
                pass = matches_reference(output[i], expected[i], max_absolute, max_relative) && pass;
            }
        }
        std::cout << "verify kernel=" << options.kernel
                  << " datatype=" << options.datatype
                  << " build=" << options.build
                  << " N=" << options.n
                  << " max_abs=" << std::setprecision(10) << max_absolute
                  << " max_rel=" << max_relative
                  << " status=" << (pass ? "PASS" : "FAIL") << '\n';
        return pass ? 0 : 1;
    };

    if (options.verify_only) {
        return verify();
    }
    if (options.dot_accuracy_only) {
        if (options.kernel != "dot_product") {
            throw std::invalid_argument("--dot-accuracy-only requires --kernel dot_product.");
        }
        if (options.output.empty()) {
            throw std::invalid_argument("--dot-accuracy-only requires --output <csv>.");
        }

        long double reference = 0.0L;
        long double sum_absolute_products = 0.0L;
        for (std::size_t index = 0; index < options.n; ++index) {
            const long double product = static_cast<long double>(x[index]) *
                                        static_cast<long double>(y[index]);
            reference += product;
            sum_absolute_products += std::fabs(product);
        }
        const T computed = project::dot_product(x.data(), y.data(), options.n);
        const long double absolute_error = std::fabs(
            static_cast<long double>(computed) - reference);
        const long double relative_error = absolute_error /
            std::max(std::fabs(reference), std::numeric_limits<long double>::min());

        // Bound at most N product roundings plus N reduction roundings. This
        // conservative m=2N operation count covers sequential and tree reductions.
        // For mu < 1 use gamma_m; otherwise use its finite product bound.
        const auto forward_error_factor = [](long double unit_roundoff, std::size_t operation_count) {
            const long double m = static_cast<long double>(operation_count);
            const long double mu = m * unit_roundoff;
            if (mu < 1.0L) {
                return mu / (1.0L - mu);
            }
            return std::expm1(m * std::log1p(unit_roundoff));
        };
        const long double type_epsilon =
            static_cast<long double>(std::numeric_limits<T>::epsilon()) / 2.0L;
        const long double reference_epsilon =
            static_cast<long double>(std::numeric_limits<long double>::epsilon()) / 2.0L;
        const std::size_t bound_operations = options.n * 2;
        const long double m_times_unit_roundoff =
            static_cast<long double>(bound_operations) * type_epsilon;
        const long double gamma_type = forward_error_factor(type_epsilon, bound_operations);
        const long double gamma_reference =
            forward_error_factor(reference_epsilon, bound_operations);
        const bool bound_valid = std::isfinite(gamma_type) &&
                                 std::isfinite(gamma_reference) &&
                                 gamma_reference < 1.0L;
        long double error_bound = std::numeric_limits<long double>::infinity();
        if (bound_valid) {
            const long double sum_absolute_upper_bound =
                sum_absolute_products / (1.0L - gamma_reference);
            error_bound = (gamma_type + gamma_reference) * sum_absolute_upper_bound;
        }
        const bool passed = bound_valid && absolute_error <= error_bound;
        const bool bound_informative = bound_valid &&
                                       error_bound < std::fabs(reference);
        const std::string status = !bound_valid
            ? "bound_invalid_unverified"
            : (!passed ? "fail_bound_exceeded"
                       : (bound_informative ? "pass" : "pass_bound_noninformative"));

        const std::filesystem::path output_path(options.output);
        if (output_path.has_parent_path()) {
            std::filesystem::create_directories(output_path.parent_path());
        }
        const bool need_header = !std::filesystem::exists(output_path) ||
                                 std::filesystem::file_size(output_path) == 0;
        std::ofstream csv(options.output, std::ios::out | std::ios::app);
        if (!csv) {
            throw std::runtime_error("Unable to open dot accuracy output: " + options.output);
        }
        if (need_header) {
                 csv << "timestamp_utc,kernel,datatype,build,compiler,compiler_flags,N,"
                     "computed_result,long_double_reference,sum_abs_products,absolute_error,"
                       "relative_error,unit_roundoff,bound_operations,m_times_unit_roundoff,error_bound,bound_method,bound_valid,bound_informative,pass_fail\n";
        }
        csv << csv_quote(timestamp_utc()) << ",dot_product," << csv_quote(options.datatype) << ','
            << csv_quote(options.build) << ',' << csv_quote(options.compiler) << ','
            << csv_quote(options.flags) << ',' << options.n << ','
            << std::setprecision(std::numeric_limits<long double>::max_digits10)
            << static_cast<long double>(computed) << ',' << reference << ','
            << sum_absolute_products << ',' << absolute_error << ',' << relative_error << ','
            << type_epsilon << ',' << bound_operations << ',' << m_times_unit_roundoff << ',' << error_bound << ','
            << csv_quote("gamma_m if m*u<1, else (1+u)^m-1; m=2N; includes long-double reference") << ','
            << (bound_valid ? "true" : "false") << ','
            << (bound_informative ? "true" : "false")
            << ',' << status << '\n';
        csv.close();
        std::cout << "dot_accuracy N=" << options.n << " datatype=" << options.datatype
                  << " build=" << options.build << " abs_error=" << absolute_error
                  << " rel_error=" << relative_error << " bound=" << error_bound
                  << " status=" << status << '\n';
        return bound_valid && !passed ? 1 : 0;
    }
    if (!std::chrono::steady_clock::is_steady) {
        throw std::runtime_error("steady_clock is not monotonic on this platform.");
    }

    const auto run_batch = [&]() {
        T result{};
        for (std::size_t call = 0; call < options.batch; ++call) {
            if (strided) {
                project::elementwise_multiply_strided(
                    x.data(), options.stride, y.data(), options.stride,
                    output.data(), options.stride, options.n);
            } else {
                result = kernel(coefficient_a, coefficient_b, coefficient_c,
                                x.data(), y.data(), output.data(), options.n);
            }
        }
        return result;
    };

    for (std::size_t warmup = 0; warmup < options.warmups; ++warmup) {
        if (options.kernel == "axpy") {
            project::test_data::fill_deterministic(y.data(), options.n, 41);
        }
        const T warmup_result = run_batch();
        benchmark_sink = static_cast<long double>(warmup_result);
    }

    const std::filesystem::path output_path(options.output);
    if (output_path.has_parent_path()) {
        std::filesystem::create_directories(output_path.parent_path());
    }
    const bool need_header = !std::filesystem::exists(output_path) ||
                             std::filesystem::file_size(output_path) == 0;
    std::ofstream csv(options.output, std::ios::out | std::ios::app);
    if (!csv) {
        throw std::runtime_error("Unable to open raw output file: " + options.output);
    }
    if (need_header) {
         csv << "timestamp_utc,kernel,datatype,build,compiler,compiler_flags,N,stride,span_elements,"
             "allocated_span_bytes,allocated_total_bytes,target_working_set_bytes,working_set_bytes,"
             "repetition,batching_count,useful_elements_per_second,"
               "elapsed_ns,ns_per_element,operations_performed,useful_bytes_processed,"
               "gflop_per_s,effective_bandwidth_gib_per_s,cpu_affinity,timer,checksum\n";
    }

    const std::uint64_t operations_per_call = options.kernel == "stencil_1d_three_point"
        ? (options.n > 2 ? static_cast<std::uint64_t>(options.n - 2) * 5 : 0)
        : static_cast<std::uint64_t>(options.n) * flops_per_element(options.kernel);
    const std::uint64_t useful_bytes_per_call = options.kernel == "stencil_1d_three_point"
        ? (options.n == 0 ? 0 : options.n == 1
            ? 2 * sizeof(T)
            : (static_cast<std::uint64_t>(options.n) * 4 - 4) * sizeof(T))
        : static_cast<std::uint64_t>(options.n) *
              useful_bytes_per_element(options.kernel) * sizeof(T);
    const std::uint64_t operations_per_sample = operations_per_call * options.batch;
    const std::uint64_t useful_bytes_per_sample = useful_bytes_per_call * options.batch;
    const std::size_t allocated_span_elements = strided ? options.span_elements : options.n;
    const std::uint64_t allocated_span_bytes =
        static_cast<std::uint64_t>(allocated_span_elements) * sizeof(T);
    const std::uint64_t working_set_bytes =
        allocated_span_bytes * arrays_in_working_set(options.kernel);

    for (std::size_t repetition = 1; repetition <= options.repetitions; ++repetition) {
        if (options.kernel == "axpy") {
            project::test_data::fill_deterministic(y.data(), options.n, 41);
        }
        T dot_result{};
        const auto start = std::chrono::steady_clock::now();
        std::atomic_signal_fence(std::memory_order_seq_cst);
        dot_result = run_batch();
        std::atomic_signal_fence(std::memory_order_seq_cst);
        const auto stop = std::chrono::steady_clock::now();
        const auto elapsed_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
        if (elapsed_ns <= 0) {
            throw std::runtime_error("Timer returned a non-positive sample duration.");
        }

        long double checksum = static_cast<long double>(dot_result);
        const std::size_t checksum_stride = std::max<std::size_t>(1, options.n / 1024);
        const T* observed = options.kernel == "axpy" ? y.data()
                            : options.kernel == "dot_product" ? x.data()
                            : output.data();
        for (std::size_t index = 0; index < options.n; index += checksum_stride) {
            checksum += static_cast<long double>(
                observed[index * (strided ? options.stride : 1)]);
        }
        benchmark_sink = checksum;

        const double ns_per_element = static_cast<double>(elapsed_ns) /
                                      static_cast<double>(options.n * options.batch);
        const double gflop_per_s = static_cast<double>(operations_per_sample) /
                                   static_cast<double>(elapsed_ns);
        const double effective_gib_per_s =
            static_cast<double>(useful_bytes_per_sample) * 1.0e9 /
            static_cast<double>(elapsed_ns) / (1024.0 * 1024.0 * 1024.0);
        const double useful_elements_per_second =
            static_cast<double>(options.n * options.batch) * 1.0e9 /
            static_cast<double>(elapsed_ns);

        csv << csv_quote(timestamp_utc()) << ','
            << csv_quote(options.kernel) << ',' << csv_quote(options.datatype) << ','
            << csv_quote(options.build) << ',' << csv_quote(options.compiler) << ','
            << csv_quote(options.flags) << ',' << options.n << ',' << options.stride << ','
            << allocated_span_elements << ',' << allocated_span_bytes << ',' << working_set_bytes << ','
            << options.target_working_set_bytes << ',' << working_set_bytes << ','
            << repetition << ',' << options.batch << ','
            << std::setprecision(12) << useful_elements_per_second << ',' << elapsed_ns << ','
            << ns_per_element << ','
            << operations_per_sample << ',' << useful_bytes_per_sample << ','
            << gflop_per_s << ',' << effective_gib_per_s << ','
            << csv_quote(affinity) << ',' << csv_quote("std::chrono::steady_clock") << ','
            << std::setprecision(18) << static_cast<double>(checksum) << '\n';
    }
    csv.close();
    std::cout << "Completed " << options.kernel << ' ' << options.datatype
              << ' ' << options.build << " N=" << options.n
              << " batch=" << options.batch << " repetitions=" << options.repetitions
              << " affinity=" << affinity << '\n';
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        if (!std::chrono::steady_clock::is_steady) {
            throw std::runtime_error("steady_clock is not monotonic on this platform.");
        }
        const Options options = parse_options(argc, argv);
        const std::string affinity = set_single_thread_affinity();
        if (options.datatype == "float32") {
            return run<float>(options, affinity);
        }
        if (options.datatype == "float64") {
            return run<double>(options, affinity);
        }
        throw std::invalid_argument("Datatype must be float32 or float64.");
    } catch (const std::exception& error) {
        std::cerr << "benchmark_runner: " << error.what() << '\n';
        return 2;
    }
}