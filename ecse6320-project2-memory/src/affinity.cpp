#include "affinity.h"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <bit>
#include <stdexcept>

CpuTopology discover_topology() {
    CpuTopology result{};
    result.processor_groups = GetActiveProcessorGroupCount();
    result.logical_processors = GetActiveProcessorCount(ALL_PROCESSOR_GROUPS);
    ULONG highest_node = 0;
    if (GetNumaHighestNodeNumber(&highest_node)) {
        result.numa_nodes = highest_node + 1;
    }

    DWORD bytes = 0;
    GetLogicalProcessorInformationEx(RelationProcessorCore, nullptr, &bytes);
    if (GetLastError() != ERROR_INSUFFICIENT_BUFFER || bytes == 0) {
        throw std::runtime_error("processor topology size query failed");
    }
    std::vector<unsigned char> storage(bytes);
    auto* info = reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(storage.data());
    if (!GetLogicalProcessorInformationEx(RelationProcessorCore, info, &bytes)) {
        throw std::runtime_error("processor topology query failed");
    }
    DWORD offset = 0;
    while (offset < bytes) {
        auto* item = reinterpret_cast<PSYSTEM_LOGICAL_PROCESSOR_INFORMATION_EX>(storage.data() + offset);
        if (item->Relationship == RelationProcessorCore && item->Processor.GroupCount > 0) {
            const auto& group = item->Processor.GroupMask[0];
            if (group.Group == 0 && group.Mask != 0) {
                result.one_logical_per_core.push_back(static_cast<unsigned>(std::countr_zero(group.Mask)));
            }
        }
        if (item->Size == 0) break;
        offset += item->Size;
    }
    if (result.one_logical_per_core.empty()) {
        throw std::runtime_error("no physical-core CPU mapping discovered");
    }
    return result;
}

bool pin_current_thread(unsigned cpu_id) {
    if (cpu_id >= 64) return false;
    const DWORD_PTR mask = static_cast<DWORD_PTR>(1ull << cpu_id);
    return SetThreadAffinityMask(GetCurrentThread(), mask) != 0;
}

unsigned current_cpu() {
    return GetCurrentProcessorNumber();
}

std::uint64_t current_thread_affinity_mask() {
    const DWORD_PTR process = SetThreadAffinityMask(GetCurrentThread(), ~DWORD_PTR{0});
    if (process == 0) return 0;
    SetThreadAffinityMask(GetCurrentThread(), process);
    return static_cast<std::uint64_t>(process);
}

