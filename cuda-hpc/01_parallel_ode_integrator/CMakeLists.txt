cmake_minimum_required(VERSION 3.18)
project(parallel_ode_integrator LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)

add_executable(benchmark
    src/benchmark.cpp
    src/ode_solver_cpu.cpp
    src/ode_solver_gpu.cu
)

target_include_directories(benchmark PRIVATE include)
