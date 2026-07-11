cmake_minimum_required(VERSION 3.18)
project(parallel_ode_integrator LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)

# Target architecture: 75 = Turing (RTX 2080). CI machines have no GPU to
# auto-detect, so this must be set explicitly.
if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES 75)
endif()

find_package(Threads REQUIRED)

add_executable(benchmark
    src/benchmark.cpp
    src/ode_solver_cpu.cpp
    src/ode_solver_gpu.cu
)

target_include_directories(benchmark PRIVATE include)
target_link_libraries(benchmark PRIVATE Threads::Threads)
