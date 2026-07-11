# Parallel ODE Integrator

Integrate a large batch of independent ODEs (damped harmonic oscillators)
forward in time with a fixed-step method, once on a single CPU core and once on
the GPU, and compare wall-clock time as the batch size grows.

Each oscillator obeys `x'' + 2·ζ·ω·x' + ω²·x = 0`, integrated with semi-implicit
(symplectic) Euler. Every oscillator in the batch is independent, which makes
this an ideal first "embarrassingly parallel" CUDA problem: one GPU thread per
oscillator.

## Results

Measured on an NVIDIA GeForce RTX 2080 Super (48 SMs, 3072 CUDA cores) vs a
single CPU core, 1000 integration steps per run. Every GPU result is verified
bit-for-bit against the CPU reference.

![CPU vs GPU benchmark](benchmark.png)

| n | CPU 1-core (ms) | GPU (ms) | Speedup |
|--:|--:|--:|--:|
| 1,000 | 6.53 | 0.66 | 9.9× |
| 10,000 | 67.1 | 1.00 | 67× |
| 100,000 | 656.7 | 1.32 | 499× |
| 1,000,000 | 6538 | 7.25 | **902×** |

The GPU line is nearly flat until the hardware saturates (thousands of cores sit
idle at small n), while the single-core CPU rises linearly. They cross at about
**n = 107** — below that the GPU's transfer + launch overhead isn't worth it.

📄 **See [REPORT.md](REPORT.md)** for the full write-up: time-complexity analysis,
why the curves behave as they do, and a recap of the CUDA concepts.

## Files

- `include/ode_solver.h` — shared structs and function declarations.
- `src/ode_solver_cpu.cpp` — single-core CPU reference.
- `src/ode_solver_gpu.cu` — CUDA kernel (one thread per oscillator) + host wrapper.
- `src/benchmark.cpp` — generates data, times both, checks correctness, writes
  `results.csv`, then auto-plots.
- `plot_results.py` — renders `results.csv` into `benchmark.png` and opens it.
- `build.bat` / `run.bat` — Windows build and run+plot helpers.

## Build & run (Windows)

Needs the CUDA Toolkit, Visual Studio (C++), and Python + matplotlib for the plot.

```
cuda-hpc\01_parallel_ode_integrator\build.bat     # compile (loads x64 toolchain)
cuda-hpc\01_parallel_ode_integrator\run.bat       # run + auto-plot + open graph
```

`build.bat` loads the 64-bit MSVC environment automatically, so it works from
any terminal. `run.bat` runs the benchmark, which writes `results.csv`, renders
`benchmark.png`, and opens it.

## Build with CMake (Linux, or Windows with a configured generator)

```
cmake -B build -S cuda-hpc
cmake --build build --parallel
```
