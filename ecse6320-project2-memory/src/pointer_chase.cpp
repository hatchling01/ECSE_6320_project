#include "pointer_chase.h"
#include "affinity.h"
#include "timer.h"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <numeric>
#include <random>
#include <stdexcept>
#include <thread>
#include <vector>

namespace {
constexpr std::uint64_t GiB = 1024ull * 1024 * 1024;
constexpr std::uint64_t kCap = 8 * GiB;
volatile std::uint64_t g_sink = 0;

void gate(std::uint64_t bytes) {
    if (bytes == 0 || bytes > kCap) throw std::invalid_argument("allocation outside 1..8 GiB cap");
    if (bytes > GiB && available_physical_memory() < 16 * GiB)
        throw std::runtime_error("RAM gate failed: <16 GiB available before >1 GiB allocation");
}

struct Aligned {
    unsigned char* p{};
    explicit Aligned(std::uint64_t n) : p(static_cast<unsigned char*>(_aligned_malloc(static_cast<size_t>(n), 64))) {
        if (!p) throw std::bad_alloc();
    }
    ~Aligned() { _aligned_free(p); }
    Aligned(const Aligned&) = delete;
    Aligned& operator=(const Aligned&) = delete;
};

void build_chain(unsigned char* p, std::uint64_t bytes, std::uint64_t spacing, std::uint64_t seed) {
    const std::uint64_t n = bytes / spacing;
    std::vector<std::uint32_t> order(static_cast<size_t>(n));
    std::iota(order.begin(), order.end(), 0u);
    std::mt19937_64 rng(seed);
    std::shuffle(order.begin(), order.end(), rng);
    for (std::uint64_t i = 0; i < n; ++i) {
        const std::uint64_t here = static_cast<std::uint64_t>(order[i]);
        const std::uint64_t next = static_cast<std::uint64_t>(order[(i + 1) % n]);
        *reinterpret_cast<std::uint64_t*>(p + here * spacing) = next;
    }
}
}

std::uint64_t available_physical_memory() {
    MEMORYSTATUSEX s{}; s.dwLength = sizeof(s);
    if (!GlobalMemoryStatusEx(&s)) throw std::runtime_error("GlobalMemoryStatusEx failed");
    return s.ullAvailPhys;
}

LatencyResult run_pointer_latency(std::uint64_t bytes, std::uint64_t spacing,
                                  std::uint64_t operations, unsigned cpu,
                                  std::uint64_t seed, unsigned target_ms) {
    if (spacing < sizeof(std::uint64_t) || spacing % 8 || bytes < 2 * spacing || bytes % spacing)
        throw std::invalid_argument("invalid working set/spacing");
    const auto before = available_physical_memory();
    gate(bytes);
    Aligned a(bytes);
    build_chain(a.p, bytes, spacing, seed);
    if (!pin_current_thread(cpu)) throw std::runtime_error("SetThreadAffinityMask failed");
    const bool affinity = current_cpu() == cpu;
    if (!affinity) throw std::runtime_error("affinity verification failed");
    const std::uint64_t n = bytes / spacing;
    std::uint64_t idx = 0;
    for (std::uint64_t i = 0; i < std::min<std::uint64_t>(n, 1000000); ++i)
        idx = *reinterpret_cast<volatile std::uint64_t*>(a.p + idx * spacing);
    QpcTimer timer;
    if (operations == 0) {
        const std::uint64_t sample = std::max<std::uint64_t>(n, 1000000);
        auto s = timer.now();
        for (std::uint64_t i = 0; i < sample; ++i)
            idx = *reinterpret_cast<volatile std::uint64_t*>(a.p + idx * spacing);
        auto e = timer.now();
        const double sec = std::max(timer.seconds(s, e), 1e-6);
        operations = static_cast<std::uint64_t>(sample * (target_ms / 1000.0) / sec);
        operations = std::clamp<std::uint64_t>(operations, 1000000, 500000000);
    }
    const auto start = timer.now();
    for (std::uint64_t i = 0; i < operations; ++i)
        idx = *reinterpret_cast<volatile std::uint64_t*>(a.p + idx * spacing);
    const auto end = timer.now();
    g_sink = idx;
    const double elapsed = timer.seconds(start, end);
    return {bytes, spacing, operations, elapsed, elapsed * 1e9 / operations, idx,
            cpu, current_cpu(), affinity, seed, before, available_physical_memory()};
}

LoadedResult run_loaded_latency(unsigned workers, std::uint64_t probe_bytes,
                                std::uint64_t worker_region_bytes,
                                unsigned warmup_ms, unsigned duration_ms,
                                std::uint64_t seed) {
    auto topo = discover_topology();
    if (workers + 1 > topo.one_logical_per_core.size() || workers > 15)
        throw std::invalid_argument("workers exceed physical-core policy");
    const std::uint64_t total = probe_bytes + workers * worker_region_bytes;
    const auto before = available_physical_memory(); gate(total);
    Aligned probe(probe_bytes); build_chain(probe.p, probe_bytes, 64, seed);
    std::vector<std::unique_ptr<Aligned>> bufs;
    for (unsigned w = 0; w < workers; ++w) {
        bufs.push_back(std::make_unique<Aligned>(worker_region_bytes));
        auto* q = reinterpret_cast<std::uint64_t*>(bufs.back()->p);
        const auto words = worker_region_bytes / 8;
        for (std::uint64_t i = 0; i < words; ++i) q[i] = i + 17 * w;
    }
    const unsigned probe_cpu = topo.one_logical_per_core[0];
    if (!pin_current_thread(probe_cpu) || current_cpu() != probe_cpu)
        throw std::runtime_error("probe affinity failed");
    std::atomic<int> phase{0};
    std::atomic<unsigned> ready{0};
    std::vector<std::uint64_t> counts(workers), sums(workers);
    std::vector<unsigned char> affinity_ok(workers, 0);
    std::vector<std::thread> threads;
    for (unsigned w = 0; w < workers; ++w) {
        threads.emplace_back([&, w] {
            const unsigned cpu = topo.one_logical_per_core[w + 1];
            affinity_ok[w] = pin_current_thread(cpu) && current_cpu() == cpu;
            auto* q = reinterpret_cast<volatile std::uint64_t*>(bufs[w]->p);
            const std::uint64_t lines = worker_region_bytes / 64;
            std::uint64_t state = seed + 0x9e3779b97f4a7c15ull * (w + 1), sum = 0, local = 0;
            ready.fetch_add(1);
            while (phase.load(std::memory_order_acquire) == 0) Sleep(0);
            while (phase.load(std::memory_order_acquire) < 3) {
                state ^= state << 13; state ^= state >> 7; state ^= state << 17;
                const auto base = (state % lines) * 8;
                for (unsigned j = 0; j < 8; ++j) sum += q[base + j];
                if (phase.load(std::memory_order_relaxed) == 2) ++local;
            }
            counts[w] = local; sums[w] = sum;
        });
    }
    while (ready.load() != workers) Sleep(0);
    phase.store(1, std::memory_order_release);
    std::uint64_t idx = 0;
    const auto warm_end = std::chrono::steady_clock::now() + std::chrono::milliseconds(warmup_ms);
    while (std::chrono::steady_clock::now() < warm_end)
        idx = *reinterpret_cast<volatile std::uint64_t*>(probe.p + idx * 64);
    QpcTimer timer; const auto start = timer.now();
    phase.store(2, std::memory_order_release);
    std::uint64_t probe_ops = 0;
    const auto finish = std::chrono::steady_clock::now() + std::chrono::milliseconds(duration_ms);
    while (std::chrono::steady_clock::now() < finish) {
        idx = *reinterpret_cast<volatile std::uint64_t*>(probe.p + idx * 64); ++probe_ops;
    }
    const auto end = timer.now(); phase.store(3, std::memory_order_release);
    for (auto& t : threads) t.join();
    const auto worker_ops = std::accumulate(counts.begin(), counts.end(), std::uint64_t{0});
    const auto checksum = std::accumulate(sums.begin(), sums.end(), std::uint64_t{idx});
    g_sink = checksum;
    const double elapsed = timer.seconds(start, end);
    const double ops_s = elapsed ? worker_ops / elapsed : 0;
    bool all_affinity = std::all_of(affinity_ok.begin(), affinity_ok.end(), [](unsigned char x){return x != 0;});
    std::vector<unsigned> cpus;
    for (unsigned w = 0; w < workers; ++w) cpus.push_back(topo.one_logical_per_core[w + 1]);
    return {workers, cpus, probe_cpu, all_affinity, total, worker_ops, probe_ops, elapsed,
            ops_s * 64 / static_cast<double>(GiB), ops_s,
            elapsed * 1e9 / probe_ops, ops_s * elapsed / probe_ops,
            idx, checksum, before, available_physical_memory()};
}

bool pointer_chain_self_test() {
    auto r = run_pointer_latency(64 * 1024, 64, 200000, discover_topology().one_logical_per_core[0], 123, 10);
    return r.final_index < r.working_set_bytes / r.spacing_bytes && r.affinity_ok && r.ns_per_load > 0;
}
