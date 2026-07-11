# Parallel ODE Integrator

Integrate a large batch of independent ODEs (damped harmonic oscillators)
forward in time with a fixed-step method, once on the CPU and once on the GPU,
and compare wall-clock time as the batch size grows.

Each oscillator obeys `x'' + 2·ζ·ω·x' + ω²·x = 0`, integrated with semi-implicit
(symplectic) Euler. Every oscillator in the batch is independent, which makes
this an ideal first "embarrassingly parallel" CUDA problem: one GPU thread per
oscillator.

## Results

Measured on an NVIDIA GeForce RTX 2080 Super (48 SMs, 3072 CUDA cores) vs a
20-logical-core CPU, 1000 integration steps per run. All GPU and multi-threaded
results are verified bit-for-bit against the single-core reference.

![CPU vs GPU benchmark](benchmark.png)

| n | CPU 1-core (ms) | CPU 20-thread (ms) | GPU (ms) | GPU vs 1-core | GPU vs 20-thread |
|--:|--:|--:|--:|--:|--:|
| 1,000 | 6.53 | 1.77 | 0.66 | 9.9× | 2.7× |
| 10,000 | 67.1 | 8.00 | 1.00 | 67× | 8.0× |
| 100,000 | 656.7 | 67.0 | 1.32 | 499× | 51× |
| 1,000,000 | 6538 | 514.9 | 7.25 | **902×** | **71×** |

**Reading the graph:**
- The **GPU line is almost flat** from n=1 to n=100,000 — thousands of CUDA cores
  sit mostly idle at small n, so adding more oscillators is nearly free until the
  hardware saturates.
- The **CPU (1 core) line rises linearly** — one worker doing oscillators one at a
  time, so 10× the work is 10× the time.
- The **CPU (20 threads) line** sits ~13× below the single core at large n (real
  parallel scaling), but carries a fixed thread-launch overhead that makes it
  *slower* than a single core for tiny batches.
- Crossover: the GPU overtakes the single-core CPU at about **n = 107**. Below
  that, the GPU's data-transfer + launch overhead isn't worth it.

The honest headline: against a *fully parallel* 20-thread CPU baseline, the GPU
is still **71× faster** at a million oscillators (902× against a single core).

## Files

- `include/ode_solver.h` — shared structs and function declarations.
- `src/ode_solver_cpu.cpp` — single-core reference + `integrate_cpu_parallel`
  (std::thread, one slice per core).
- `src/ode_solver_gpu.cu` — CUDA kernel (one thread per oscillator) + host wrapper.
- `src/benchmark.cpp` — generates data, times all three variants, checks
  correctness, writes `results.csv`.
- `plot_results.py` — renders `results.csv` into `benchmark.png`.

## Build & run

**Windows (with the CUDA Toolkit + Visual Studio):** run the helper script from
the repo root — it loads the 64-bit MSVC environment automatically, so it works
from any terminal:

```
cuda-hpc\01_parallel_ode_integrator\build.bat
cuda-hpc\01_parallel_ode_integrator\benchmark.exe
python cuda-hpc\01_parallel_ode_integrator\plot_results.py
```

**With CMake (Linux, or Windows with a configured generator):**

```
cmake -B build -S cuda-hpc
cmake --build build --parallel
```

## Possible next steps

- Swap Euler for RK4 (more arithmetic per step — shifts the crossover left).
- Try `float` vs `double` and compare accuracy against speed.
- Use CUDA events to separate kernel time from memory-transfer time.
