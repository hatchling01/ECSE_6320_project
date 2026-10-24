#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include "aligned_buffer.hpp"
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
    std::string condition;
    std::string output;
    std::size_t n = 0;
    std::size_t target_working_set_bytes = 0;
    std::size_t offset_elements = 0;
    std::size_t warmups = 3;
    std::size_t repetitions = 5;
    std::size_t batch = 1;
    bool verify_only = false;
};

volatile long double alignment_sink = 0.0L;

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
    for (int index = 1; index < argc; ++index) {
        const std::string key = argv[index];
        if (key.rfind("--", 0) != 0 || index + 1 >= argc) {
            throw std::invalid_argument("Expected --key value arguments.");
        }
        values[key] = argv[++index];
    }
    const auto text = [&values](const std::string& key) {
        const auto found = values.find(key);
        if (found == values.end()) {
            throw std::invalid_argument("Missing option " + key);
        }
        return found->second;
    };
    const auto number = [&text](const std::string& key) {
        return static_cast<std::size_t>(std::stoull(text(key)));
    };
    Options options;
    options.kernel = text("--kernel");
    options.datatype = text("--datatype");
    options.build = text("--build");
    options.compiler = text("--compiler");
    options.flags = text("--flags");
    options.condition = text("--alignment-condition");
    options.output = text("--output");
    options.n = number("--n");
    options.target_working_set_bytes = number("--target-working-set-bytes");
    options.offset_elements = number("--offset-elements");
    options.warmups = number("--warmups");
    options.repetitions = number("--repetitions");
    options.batch = number("--batch");
    const auto verify = values.find("--verify-only");
    options.verify_only = verify != values.end() && verify->second == "true";
    if (options.n == 0 || options.batch == 0 ||
        (!options.verify_only && options.repetitions == 0)) {
        throw std::invalid_argument("N and batch must be positive; timed repetitions must be positive.");
    }
    if (options.kernel != "axpy" && options.kernel != "elementwise_multiply") {
        throw std::invalid_argument("Phase 4A supports AXPY and elementwise_multiply only.");
    }
    return options;
}

std::uint64_t operations_per_element(const std::string& kernel) {
    return kernel == "axpy" ? 2 : 1;
}

template <typename T>
struct Tolerance {
    static constexpr long double absolute = std::is_same<T, float>::value ? 2.0e-5L : 1.0e-12L;
    static constexpr long double relative = std::is_same<T, float>::value ? 2.0e-6L : 1.0e-12L;
};

template <typename T>
bool compare_values(const T* actual, const T* expected, std::size_t n,
                    long double& max_absolute, long double& max_relative) {
    bool passed = true;
    for (std::size_t i = 0; i < n; ++i) {
        const long double actual_value = static_cast<long double>(actual[i]);
        const long double expected_value = static_cast<long double>(expected[i]);
        const long double absolute_error = std::fabs(actual_value - expected_value);
        const long double relative_error = absolute_error /
            std::max(std::fabs(expected_value), Tolerance<T>::absolute);
        max_absolute = std::max(max_absolute, absolute_error);
        max_relative = std::max(max_relative, relative_error);
        passed = passed && std::isfinite(actual_value) && std::isfinite(expected_value) &&
            absolute_error <= Tolerance<T>::absolute +
                              Tolerance<T>::relative * std::fabs(expected_value);
    }
    return passed;
}

template <typename T>
std::uint64_t address_mod_64(const T* pointer) {
    return reinterpret_cast<std::uintptr_t>(pointer) % 64;
}

template <typename T>
int run(const Options& options, const std::string& affinity) {
    constexpr std::size_t alignment = 64;
    const T coefficient = static_cast<T>(0.375);
    const std::size_t extra = (alignment / sizeof(T)) - 1;
    project::AlignedBuffer<T> x(options.n, alignment, extra);
    project::AlignedBuffer<T> y(options.n, alignment, extra);
    project::AlignedBuffer<T> output(
        options.kernel == "elementwise_multiply" ? options.n : 0,
        alignment,
        extra);
    T* x_pointer = x.data(options.offset_elements);
    T* y_pointer = y.data(options.offset_elements);
    T* output_pointer = options.kernel == "elementwise_multiply"
        ? output.data(options.offset_elements)
        : nullptr;
    project::test_data::fill_deterministic(x_pointer, options.n, 31);
    project::test_data::fill_deterministic(y_pointer, options.n, 47);

    std::vector<T> expected(options.n, T{});
    if (options.kernel == "axpy") {
        std::copy(y_pointer, y_pointer + options.n, expected.begin());
        project::reference::axpy(coefficient, x_pointer, expected.data(), options.n);
        project::test_data::fill_deterministic(y_pointer, options.n, 47);
        project::axpy(coefficient, x_pointer, y_pointer, options.n);
    } else {
        project::reference::elementwise_multiply(
            x_pointer, y_pointer, expected.data(), options.n);
        project::elementwise_multiply(x_pointer, y_pointer, output_pointer, options.n);
    }
    long double max_absolute = 0.0L;
    long double max_relative = 0.0L;
    const T* actual = options.kernel == "axpy" ? y_pointer : output_pointer;
    const bool correct = compare_values(actual, expected.data(), options.n,
                                        max_absolute, max_relative);
    const std::uint64_t x_mod64 = address_mod_64(x_pointer);
    const std::uint64_t y_mod64 = address_mod_64(y_pointer);
    const std::uint64_t output_mod64 = options.kernel == "axpy"
        ? y_mod64
        : address_mod_64(output_pointer);
    const bool expected_modulo = options.condition == "aligned_64B"
        ? x_mod64 == 0 && y_mod64 == 0 && output_mod64 == 0
        : options.condition == "offset_one_element"
            ? x_mod64 == sizeof(T) && y_mod64 == sizeof(T) && output_mod64 == sizeof(T)
            : options.condition == "cache_line_crossing"
                ? x_mod64 == alignment - sizeof(T) && y_mod64 == alignment - sizeof(T) &&
                  output_mod64 == alignment - sizeof(T)
                : false;
    if (!correct || !expected_modulo) {
        std::cerr << "FAIL correctness/alignment kernel=" << options.kernel
                  << " datatype=" << options.datatype << " condition=" << options.condition
                  << " max_abs=" << max_absolute << " max_rel=" << max_relative
                  << " x_mod64=" << x_mod64 << " y_mod64=" << y_mod64
                  << " output_mod64=" << output_mod64 << '\n';
        return 1;
    }
    if (options.verify_only) {
        std::cout << "Verified " << options.kernel << ' ' << options.datatype << ' '
                  << options.build << ' ' << options.condition << " offset="
                  << options.offset_elements * sizeof(T) << " ptr_mod64=" << x_mod64 << '/'
                  << y_mod64 << '/' << output_mod64 << " N=" << options.n
                  << " correctness=pass\n";
        return 0;
    }

    const std::size_t arrays = options.kernel == "axpy" ? 2 : 3;
    const std::uint64_t working_set_bytes =
        static_cast<std::uint64_t>(options.n) * arrays * sizeof(T);
    const std::uint64_t operations_per_call =
        static_cast<std::uint64_t>(options.n) * operations_per_element(options.kernel);
    const std::uint64_t useful_bytes_per_call =
        static_cast<std::uint64_t>(options.n) * 3 * sizeof(T);
    const std::size_t offset_bytes = options.offset_elements * sizeof(T);
    const auto call_kernel = [&]() {
        if (options.kernel == "axpy") {
            project::axpy(coefficient, x_pointer, y_pointer, options.n);
        } else {
            project::elementwise_multiply(x_pointer, y_pointer, output_pointer, options.n);
        }
    };

    for (std::size_t warmup = 0; warmup < options.warmups; ++warmup) {
        if (options.kernel == "axpy") {
            project::test_data::fill_deterministic(y_pointer, options.n, 47);
        }
        for (std::size_t batch = 0; batch < options.batch; ++batch) {
            call_kernel();
        }
    }

    const std::filesystem::path output_path(options.output);
    if (output_path.has_parent_path()) {
        std::filesystem::create_directories(output_path.parent_path());
    }
    const bool need_header = !std::filesystem::exists(output_path) ||
                             std::filesystem::file_size(output_path) == 0;
    std::ofstream csv(options.output, std::ios::out | std::ios::app);
    if (!csv) {
        throw std::runtime_error("Unable to open alignment raw output: " + options.output);
    }
    if (need_header) {
        csv << "timestamp_utc,kernel,datatype,build,compiler,compiler_flags,N,working_set_bytes,"
             "target_working_set_bytes,alignment_condition,offset_elements,offset_bytes,"
             "x_address_mod64,y_address_mod64,"
               "output_address_mod64,repetition,batching_count,elapsed_ns,ns_per_element,"
               "operations_performed,useful_bytes_processed,gflop_per_s,effective_bandwidth_gib_per_s,"
               "correctness,max_absolute_error,max_relative_error,cpu_affinity\n";
    }

    for (std::size_t repetition = 1; repetition <= options.repetitions; ++repetition) {
        if (options.kernel == "axpy") {
            project::test_data::fill_deterministic(y_pointer, options.n, 47);
        }
        const auto start = std::chrono::steady_clock::now();
        std::atomic_signal_fence(std::memory_order_seq_cst);
        for (std::size_t batch = 0; batch < options.batch; ++batch) {
            call_kernel();
        }
        std::atomic_signal_fence(std::memory_order_seq_cst);
        const auto stop = std::chrono::steady_clock::now();
        const auto elapsed_ns =
            std::chrono::duration_cast<std::chrono::nanoseconds>(stop - start).count();
        if (elapsed_ns <= 0) {
            throw std::runtime_error("steady_clock returned a non-positive duration.");
        }

        long double checksum = 0.0L;
        const std::size_t checksum_stride = std::max<std::size_t>(1, options.n / 1024);
        for (std::size_t index = 0; index < options.n; index += checksum_stride) {
            checksum += static_cast<long double>(actual[index]);
        }
        alignment_sink = checksum;

        const std::uint64_t operations = operations_per_call * options.batch;
        const std::uint64_t useful_bytes = useful_bytes_per_call * options.batch;
        const double ns_per_element = static_cast<double>(elapsed_ns) /
                                      static_cast<double>(options.n * options.batch);
        const double gflop_per_s = static_cast<double>(operations) /
                                   static_cast<double>(elapsed_ns);
        const double effective_gib_per_s = static_cast<double>(useful_bytes) * 1.0e9 /
            static_cast<double>(elapsed_ns) / (1024.0 * 1024.0 * 1024.0);

        csv << csv_quote(timestamp_utc()) << ',' << csv_quote(options.kernel) << ','
            << csv_quote(options.datatype) << ',' << csv_quote(options.build) << ','
            << csv_quote(options.compiler) << ',' << csv_quote(options.flags) << ','
            << options.n << ',' << working_set_bytes << ',' << options.target_working_set_bytes
            << ',' << csv_quote(options.condition) << ','
            << options.offset_elements << ',' << offset_bytes << ',' << x_mod64 << ','
            << y_mod64 << ',' << output_mod64 << ',' << repetition << ',' << options.batch << ','
            << elapsed_ns << ',' << std::setprecision(12) << ns_per_element << ','
            << operations << ',' << useful_bytes << ',' << gflop_per_s << ','
            << effective_gib_per_s << ",pass," << std::setprecision(18)
            << max_absolute << ',' << max_relative << ',' << csv_quote(affinity) << '\n';
    }
    csv.close();
    std::cout << "Completed " << options.kernel << ' ' << options.datatype << ' '
              << options.build << ' ' << options.condition << " offset=" << offset_bytes
              << " ptr_mod64=" << x_mod64 << '/' << y_mod64 << '/' << output_mod64
              << " N=" << options.n << " batch=" << options.batch
              << " reps=" << options.repetitions << " correctness=pass\n";
    return 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        if (!std::chrono::steady_clock::is_steady) {
            throw std::runtime_error("steady_clock is not monotonic.");
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
        std::cerr << "alignment_benchmark: " << error.what() << '\n';
        return 2;
    }
}