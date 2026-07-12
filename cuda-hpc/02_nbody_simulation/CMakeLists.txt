cmake_minimum_required(VERSION 3.18)
project(nbody_simulation LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)

if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
    set(CMAKE_CUDA_ARCHITECTURES 75)   # 75 = Turing (RTX 2080)
endif()

add_executable(nbody
    src/benchmark.cpp
    src/nbody_cpu.cpp
    src/nbody_gpu.cu
)
target_include_directories(nbody PRIVATE include)
