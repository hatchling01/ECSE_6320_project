#include "streaming.h"
#include "pointer_chase.h"
#include "affinity.h"
#include "timer.h"

#include <algorithm>
#include <cstdlib>
#include <numeric>
#include <random>
#include <stdexcept>
#include <vector>

namespace { constexpr std::uint64_t GiB=1024ull*1024*1024; volatile std::uint64_t sink=0; }

StreamResult run_stream(std::uint64_t bytes, std::uint64_t stride,
                        std::uint64_t operations, const std::string& pattern,
                        unsigned read_pct, unsigned cpu, std::uint64_t seed) {
    if (!bytes || bytes > 8*GiB || bytes % 64 || stride < 64 || stride % 64 || stride > bytes)
        throw std::invalid_argument("invalid size/stride or 8 GiB cap exceeded");
    if (bytes > GiB && available_physical_memory() < 16*GiB)
        throw std::runtime_error("RAM gate failed: <16 GiB available");
    if (operations == 0 || read_pct > 100 || read_pct % 10 || (pattern!="sequential" && pattern!="random"))
        throw std::invalid_argument("invalid operations/mix/pattern");
    const auto before=available_physical_memory();
    auto* p=static_cast<std::uint64_t*>(_aligned_malloc(static_cast<size_t>(bytes),64));
    if(!p) throw std::bad_alloc();
    struct Guard{std::uint64_t* p; ~Guard(){_aligned_free(p);}} guard{p};
    const std::uint64_t words=bytes/8, slots=bytes/stride;
    for(std::uint64_t i=0;i<words;++i) p[i]=i*0x9e3779b97f4a7c15ull+seed;
    std::vector<std::uint32_t> order;
    if(pattern=="random"){
        if(slots>UINT32_MAX) throw std::invalid_argument("too many random slots");
        order.resize(static_cast<size_t>(slots)); std::iota(order.begin(),order.end(),0u);
        std::mt19937_64 rng(seed); std::shuffle(order.begin(),order.end(),rng);
    }
    if(!pin_current_thread(cpu)||current_cpu()!=cpu) throw std::runtime_error("affinity verification failed");
    std::uint64_t sum=0, reads=0,writes=0,last_slot=0,last_value=0;
    QpcTimer timer; auto start=timer.now();
    for(std::uint64_t op=0;op<operations;++op){
        const std::uint64_t logical=op%slots;
        const std::uint64_t slot=pattern=="random"?order[static_cast<size_t>(logical)]:logical;
        auto* q=p+(slot*stride/8);
        const bool rd=(op%10)<(read_pct/10);
        if(rd){ for(unsigned j=0;j<8;++j) sum+=static_cast<volatile std::uint64_t*>(q)[j]; ++reads; }
        else { const auto v=seed^op; for(unsigned j=0;j<8;++j) static_cast<volatile std::uint64_t*>(q)[j]=v+j; ++writes; last_slot=slot; last_value=v; }
    }
    auto end=timer.now();
    bool valid=true;
    if(writes) for(unsigned j=0;j<8;++j) valid &= p[last_slot*stride/8+j]==last_value+j;
    sink=sum; const double sec=timer.seconds(start,end);
    return {bytes,stride,operations,reads,writes,reads*64,writes*64,sec,sec*1e9/operations,
            operations*64/sec/static_cast<double>(GiB),100.0*reads/operations,sum,valid,true,cpu,current_cpu(),seed,pattern,before,available_physical_memory()};
}

bool stream_self_test(){
    auto cpu=discover_topology().one_logical_per_core[0];
    auto r=run_stream(64*1024,64,1000,"sequential",70,cpu,77);
    auto w=run_stream(64*1024,256,1000,"random",0,cpu,77);
    return r.read_operations==700&&r.write_operations==300&&r.validation_ok&&w.write_operations==1000&&w.validation_ok;
}
