cmake_minimum_required(VERSION 3.20)
project(ecse6320_project1_simd LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(project_kernels src/kernels.cpp)
target_include_directories(project_kernels PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_library(project_reference src/reference.cpp)
target_include_directories(project_reference PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_library(project_test_data src/test_data.cpp)
target_include_directories(project_test_data PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

add_executable(correctness_tests
	src/correctness_tests.cpp
)
target_link_libraries(correctness_tests PRIVATE project_kernels project_reference project_test_data)

add_executable(benchmark_runner src/benchmark.cpp)
target_link_libraries(benchmark_runner PRIVATE project_kernels project_reference project_test_data)

add_executable(alignment_benchmark src/alignment_benchmark.cpp)
target_link_libraries(alignment_benchmark PRIVATE project_kernels project_reference project_test_data)

set(PROJECT_CORRECTNESS_CSV
	${CMAKE_CURRENT_SOURCE_DIR}/data/processed/correctness_results.csv
	CACHE FILEPATH "Correctness CSV output path")
set(PROJECT_CORRECTNESS_SUMMARY
	${CMAKE_CURRENT_SOURCE_DIR}/results/tables/correctness_summary.md
	CACHE FILEPATH "Correctness summary output path")

include(CTest)
if(BUILD_TESTING)
	add_test(
		NAME kernel_correctness
		COMMAND correctness_tests
			${PROJECT_CORRECTNESS_CSV}
			${PROJECT_CORRECTNESS_SUMMARY}
	)
endif()
