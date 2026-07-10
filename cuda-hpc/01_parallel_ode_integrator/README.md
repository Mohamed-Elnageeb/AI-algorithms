# Parallel ODE Integrator

Goal: integrate a large batch of independent ODEs (e.g. damped harmonic oscillators) forward in time using a fixed-step method (start with explicit Euler, then RK4), once on the CPU and once on the GPU, and compare wall-clock time as batch size grows.

## Why this project

- Each ODE in the batch is independent, so it's an easy first "embarrassingly parallel" CUDA problem: one thread per ODE instance.
- Small enough to implement in an evening, but touches the core CUDA workflow: host/device memory management, kernel launch, timing, and correctness-checking against a CPU reference.

## Plan

1. `src/ode_solver_cpu.cpp` — reference CPU implementation (single-threaded loop over all ODE instances).
2. `src/ode_solver_gpu.cu` — CUDA kernel, one thread per ODE instance.
3. `src/benchmark.cpp` — runs both, times them, checks GPU output matches CPU output within tolerance, prints a table across batch sizes.
4. `include/ode_solver.h` — shared struct/function declarations.

## Status

Scaffolding only — solver bodies are TODO. See TODO markers in each file.

## Build

```
cmake -B build -S .
cmake --build build
./build/benchmark
```
