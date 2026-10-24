cmake_minimum_required(VERSION 3.20)
project(memory_bench LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(memory_bench
    src/main.cpp
    src/affinity.cpp
    src/timer.cpp
    src/pointer_chase.cpp
    src/streaming.cpp
    src/tlb.cpp
)
target_include_directories(memory_bench PRIVATE src)
target_compile_definitions(memory_bench PRIVATE BENCH_COMPILER_FLAGS="$<$<CONFIG:Release>:-O3 -DNDEBUG -march=native>$<$<CONFIG:Debug>:-O0 -g>")
if(MINGW)
    target_compile_options(memory_bench PRIVATE -Wall -Wextra -Wpedantic)
    target_link_libraries(memory_bench PRIVATE psapi)
endif()
enable_testing()
add_test(NAME native_self_test COMMAND memory_bench self-test)
set_tests_properties(native_self_test PROPERTIES
    ENVIRONMENT_MODIFICATION "PATH=path_list_prepend:C:/msys64/ucrt64/bin")

