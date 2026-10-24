#include "affinity.h"
#include "pointer_chase.h"
#include "streaming.h"
#include "timer.h"
#include "tlb.h"

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>

#ifndef BENCH_COMPILER_FLAGS
#define BENCH_COMPILER_FLAGS "unknown"
#endif

namespace {
using Args=std::map<std::string,std::string>;
std::string esc(const std::string&s){std::string o;for(char c:s){if(c=='"'||c=='\\')o+='\\';o+=c;}return o;}
Args parse(int argc,char**argv){Args a;for(int i=2;i<argc;++i){std::string k=argv[i];if(k.rfind("--",0)!=0)throw std::invalid_argument("expected --option");if(i+1>=argc)throw std::invalid_argument("missing option value");a[k.substr(2)]=argv[++i];}return a;}
std::uint64_t u(const Args&a,const std::string&k,std::uint64_t d){auto it=a.find(k);return it==a.end()?d:std::stoull(it->second);}
std::string s(const Args&a,const std::string&k,const std::string&d){auto it=a.find(k);return it==a.end()?d:it->second;}
std::string now(){SYSTEMTIME x{};GetSystemTime(&x);char b[40];snprintf(b,sizeof(b),"%04u-%02u-%02uT%02u:%02u:%02u.%03uZ",x.wYear,x.wMonth,x.wDay,x.wHour,x.wMinute,x.wSecond,x.wMilliseconds);return b;}
std::string compiler(){std::ostringstream o;
#ifdef __clang__
o<<"Clang "<<__clang_major__<<'.'<<__clang_minor__<<'.'<<__clang_patchlevel__;
#else
o<<"GCC "<<__GNUC__<<'.'<<__GNUC_MINOR__<<'.'<<__GNUC_PATCHLEVEL__;
#endif
return o.str();}
void meta(const Args&a,const std::string&mode){std::cout<<"\"schema_version\":1,\"status\":\"VALID\",\"timestamp_utc\":\""<<now()<<"\",\"mode\":\""<<mode<<"\",\"git_commit\":\""<<esc(s(a,"git-commit","uncommitted"))<<"\",\"compiler\":\""<<compiler()<<"\",\"compiler_flags\":\""<<esc(BENCH_COMPILER_FLAGS)<<"\",\"classification\":\""<<esc(s(a,"classification","unspecified"))<<"\",\"repetition\":"<<u(a,"repetition",0)<<',';}
void latency_json(const Args&a,const std::string&mode,const LatencyResult&r){std::cout<<'{';meta(a,mode);std::cout<<"\"working_set_bytes\":"<<r.working_set_bytes<<",\"spacing_bytes\":"<<r.spacing_bytes<<",\"operations\":"<<r.operations<<",\"elapsed_seconds\":"<<r.elapsed_seconds<<",\"ns_per_load\":"<<r.ns_per_load<<",\"final_index\":"<<r.final_index<<",\"seed\":"<<r.seed<<",\"requested_cpu\":"<<r.requested_cpu<<",\"observed_cpu\":"<<r.observed_cpu<<",\"affinity_ok\":"<<(r.affinity_ok?"true":"false")<<",\"available_before\":"<<r.available_before<<",\"available_after\":"<<r.available_after<<"}\n";}
}

int main(int argc,char**argv){
  std::cout<<std::setprecision(12);
  try{
    if(argc<2)throw std::invalid_argument("mode required");std::string mode=argv[1];Args a=parse(argc,argv);auto topo=discover_topology();unsigned cpu=static_cast<unsigned>(u(a,"cpu",topo.one_logical_per_core[0]));
    if(mode=="info"){
      QpcTimer t;SYSTEM_INFO si{};GetSystemInfo(&si);std::cout<<'{';meta(a,mode);std::cout<<"\"logical_processors\":"<<topo.logical_processors<<",\"physical_cores\":"<<topo.one_logical_per_core.size()<<",\"processor_groups\":"<<topo.processor_groups<<",\"numa_nodes\":"<<topo.numa_nodes<<",\"page_size\":"<<si.dwPageSize<<",\"allocation_granularity\":"<<si.dwAllocationGranularity<<",\"qpc_frequency\":"<<t.frequency<<",\"physical_core_cpus\":[";for(size_t i=0;i<topo.one_logical_per_core.size();++i){if(i)std::cout<<',';std::cout<<topo.one_logical_per_core[i];}std::cout<<"]}\n";
    }else if(mode=="self-test"){
      bool p=pointer_chain_self_test(),st=stream_self_test();std::cout<<'{';meta(a,mode);std::cout<<"\"pointer_chain\":"<<(p?"true":"false")<<",\"streaming\":"<<(st?"true":"false")<<",\"affinity\":true,\"allocation_cap_bytes\":"<<(8ull*1024*1024*1024)<<"}\n";return(p&&st)?0:2;
    }else if(mode=="calibrate"){
      QpcTimer t;auto n=u(a,"operations",200000);volatile std::uint64_t x=0;auto b=t.now();for(std::uint64_t i=0;i<n;++i)x+=i;auto e=t.now();std::cout<<'{';meta(a,mode);std::cout<<"\"qpc_frequency\":"<<t.frequency<<",\"qpc_call_ns\":"<<t.calibrated_overhead_ns()<<",\"empty_loop_ns_per_iteration\":"<<t.seconds(b,e)*1e9/n<<",\"checksum\":"<<x<<"}\n";
    }else if(mode=="latency"){
      auto r=run_pointer_latency(u(a,"bytes",16*1024),u(a,"spacing",64),u(a,"operations",0),cpu,u(a,"seed",12345),static_cast<unsigned>(u(a,"target-ms",250)));latency_json(a,mode,r);
    }else if(mode=="tlb"){
      auto r=run_tlb_latency(u(a,"pages",16),u(a,"operations",0),cpu,u(a,"seed",12345));latency_json(a,mode,r);
    }else if(mode=="stream"||mode=="mix"){
      auto r=run_stream(u(a,"bytes",64*1024),u(a,"stride",64),u(a,"operations",1000000),s(a,"pattern","sequential"),static_cast<unsigned>(u(a,"read-pct",100)),cpu,u(a,"seed",12345));std::cout<<'{';meta(a,mode);std::cout<<"\"working_set_bytes\":"<<r.working_set_bytes<<",\"stride_bytes\":"<<r.stride_bytes<<",\"pattern\":\""<<r.pattern<<"\",\"requested_read_pct\":"<<u(a,"read-pct",100)<<",\"actual_read_pct\":"<<r.actual_read_pct<<",\"operations\":"<<r.operations<<",\"read_operations\":"<<r.read_operations<<",\"write_operations\":"<<r.write_operations<<",\"useful_read_bytes\":"<<r.useful_read_bytes<<",\"useful_write_bytes\":"<<r.useful_write_bytes<<",\"elapsed_seconds\":"<<r.elapsed_seconds<<",\"ns_per_operation\":"<<r.ns_per_operation<<",\"useful_gib_per_s\":"<<r.useful_gib_per_s<<",\"checksum\":"<<r.checksum<<",\"validation_ok\":"<<(r.validation_ok?"true":"false")<<",\"affinity_ok\":"<<(r.affinity_ok?"true":"false")<<",\"requested_cpu\":"<<r.requested_cpu<<",\"observed_cpu\":"<<r.observed_cpu<<",\"seed\":"<<r.seed<<",\"available_before\":"<<r.available_before<<",\"available_after\":"<<r.available_after<<"}\n";
    }else if(mode=="loaded-latency"){
      auto r=run_loaded_latency(static_cast<unsigned>(u(a,"workers",0)),u(a,"probe-bytes",512ull*1024*1024),u(a,"worker-bytes",128ull*1024*1024),static_cast<unsigned>(u(a,"warmup-ms",1000)),static_cast<unsigned>(u(a,"duration-ms",5000)),u(a,"seed",12345));std::cout<<'{';meta(a,mode);std::cout<<"\"workers\":"<<r.workers<<",\"probe_cpu\":"<<r.probe_cpu<<",\"worker_cpus\":[";for(size_t i=0;i<r.worker_cpus.size();++i){if(i)std::cout<<',';std::cout<<r.worker_cpus[i];}std::cout<<"],\"affinity_ok\":"<<(r.affinity_ok?"true":"false")<<",\"total_allocation_bytes\":"<<r.total_allocation_bytes<<",\"worker_operations\":"<<r.worker_operations<<",\"probe_operations\":"<<r.probe_operations<<",\"elapsed_seconds\":"<<r.elapsed_seconds<<",\"worker_gib_per_s\":"<<r.worker_gib_per_s<<",\"worker_ops_per_s\":"<<r.worker_ops_per_s<<",\"probe_ns_per_load\":"<<r.probe_ns_per_load<<",\"l_inferred\":"<<r.l_inferred<<",\"probe_final_index\":"<<r.probe_final_index<<",\"checksum\":"<<r.checksum<<",\"available_before\":"<<r.available_before<<",\"available_after\":"<<r.available_after<<"}\n";
    }else throw std::invalid_argument("unknown mode");
    return 0;
  }catch(const std::exception&e){std::cerr<<"{\"schema_version\":1,\"status\":\"INVALID\",\"error\":\""<<esc(e.what())<<"\"}\n";return 2;}
}
