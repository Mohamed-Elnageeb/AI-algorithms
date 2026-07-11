# Parallel ODE Integrator — Report

A batch of independent damped harmonic oscillators is integrated forward in
time, once on a single CPU core and once on the GPU (one thread per
oscillator). This report covers the results, a time-complexity analysis of why
the two curves behave as they do, and a recap of the key concepts.

---

## 1. Problem

Each oscillator obeys the ODE

```
x'' + 2·ζ·ω·x' + ω²·x = 0
```

integrated with **semi-implicit (symplectic) Euler** over `S = 1000` fixed steps:

```
a = −2·ζ·ω·v − ω²·x
v ← v + a·dt          (update velocity first…)
x ← x + v·dt          (…then use the new velocity for position)
```

Updating `v` before `x` is what makes the scheme *semi-implicit*; it conserves
energy far better than plain explicit Euler, so the oscillators stay stable over
long runs instead of spiralling out.

The batch of `n` oscillators is **embarrassingly parallel**: oscillator *i* never
reads or writes oscillator *j*'s data, so the `n` problems can be solved in any
order, or all at once.

---

## 2. Hardware

| | |
|---|---|
| GPU | NVIDIA GeForce RTX 2080 Super — 48 SMs × 64 = **3072 CUDA cores**, 8 GB |
| CPU | 20 logical cores (baseline uses **1**) |
| Steps per run | 1000 |
| Precision | `float` (fp32) |

---

## 3. Results

![CPU vs GPU benchmark](benchmark.png)

| n | CPU 1-core (ms) | GPU (ms) | Speedup |
|--:|--:|--:|--:|
| 1,000 | 6.53 | 0.61 | 10.7× |
| 10,000 | 66.3 | 1.03 | 65× |
| 100,000 | 657.2 | 1.40 | 468× |
| 1,000,000 | 6643 | 7.05 | **942×** |

All GPU results are verified bit-for-bit against the single-core CPU reference
(`match = OK` on every row). The sweep runs from n = 1 to n = 10⁶.

Speedup peaks near **n = 1,000,000 (~900–1000×)** and would *fall* beyond that:
past a few million oscillators the run becomes bound by PCIe data transfer and
GPU memory allocation (which don't scale with more cores) rather than by the
cheap, highly-parallel arithmetic — the classic low-arithmetic-intensity limit.

---

## 4. Time-complexity analysis

Let `n` = number of oscillators, `S` = steps per oscillator, `P` = number of
parallel workers.

### CPU (1 core)
The work is one inner loop of `S` steps per oscillator, done sequentially:

```
T_cpu(n) = Θ(n · S)
```

With `S` fixed, this is **linear in n** — double the oscillators, double the
time. On the log-log plot that is a straight line of slope 1, which is exactly
what the red curve shows.

### GPU
The GPU does the *same total work* `Θ(n · S)`, but spreads it over `P ≈ 3072`
cores, plus two costs the CPU doesn't pay: a fixed launch/setup overhead `L`,
and copying the data across the PCIe bus, which is `Θ(n)`:

```
T_gpu(n) = L  +  Θ(n)          +  Θ(n · S / P)
           ^^^    ^^^^^^^          ^^^^^^^^^^^^^
        overhead  transfer         compute (parallel)
```

This produces the two regimes you see in the green curve:

- **Small n (n ≲ P):** there is more hardware than work, so the compute term is
  negligible and `T_gpu ≈ L`, a **flat line**. Every extra oscillator is nearly
  free because it just lights up an idle core.
- **Large n (n ≫ P):** the cores are saturated and pipelined, so
  `T_gpu ≈ Θ(n·S/P)` — linear again, but with a slope reduced by the factor `P`.
  That's why the green line eventually rises, but stays ~900× below the CPU.

### Crossover
The GPU wins once its overhead is cheaper than the CPU's linear work:

```
L  ≈  T_cpu(n*)  =  c · n* · S      ⇒      n*  ≈  L / (c · S)
```

Measured crossover: **n\* ≈ 102**. Below it, the single core is faster because
the GPU's fixed overhead `L` dominates a tiny workload; above it, the GPU's
parallelism takes over.

### Speedup ceiling
For large n the speedup tends toward

```
speedup = T_cpu / T_gpu  →  (n·S) / (n·S/P + Θ(n))  ≈  P / (1 + P/S)
```

With `S = 1000` and `P = 3072`, memory transfer (the `Θ(n)` term) starts to
bite, which is why the observed 942× is below the raw core count of 3072 — the
classic lesson that on the GPU, **moving data, not doing math, is often the
bottleneck** (this problem does only ~1000 flops per oscillator but must ship
every oscillator across the bus). More arithmetic per byte (e.g. RK4, or more
steps) would push the speedup higher.

---

## 5. Concepts recap

**GPU execution model**
- **Thread** — one worker running the kernel for one oscillator. GPUs have
  thousands of weak threads vs a CPU's few strong cores.
- **Kernel** — the per-thread function (`__global__ void integrate_kernel`).
  Launched from the CPU, run by every thread at once.
- **Block / grid** — threads are grouped into blocks; the launch is a grid of
  blocks. `integrate_kernel<<<blocks, threads>>>(...)` picks the shape.
- **Global index** — `int i = blockIdx.x * blockDim.x + threadIdx.x;` turns
  each thread's (block #, lane #) into a unique array index `0…n−1`. The
  `if (i >= n) return;` guard stops the few extra threads from touching memory
  that isn't theirs.
- **`__global__`** — a marker meaning "GPU kernel, called from the host." The
  `void` after it is the return type: kernels can't return values (which
  thread's would it be?), so results come out through memory.

**Host/device memory dance** (`integrate_gpu`)
1. `cudaMalloc` — allocate memory on the GPU (separate from CPU RAM).
2. `cudaMemcpy(..., HostToDevice)` — copy inputs over.
3. launch the kernel.
4. `cudaMemcpy(..., DeviceToHost)` — copy results back.
5. `cudaFree` — release GPU memory.

**C++ fundamentals that bit us**
- **Pointer vs reference** — `*` is a variable holding an address (can start
  empty, be reassigned; needed by `cudaMalloc`); `&` in a declaration is a
  permanent alias to an existing object (great for `OscillatorState& s`).
- **`size_t`** — the right type for "a count of bytes"; non-negative, 64-bit on
  x64. A `size_t` declared as 32-bit was the tell that the build had picked up a
  32-bit compiler.
- **`-O2`** — the compiler's optimization level; at `-O2` it hoists
  loop-invariant math for you (why the manual optimization barely moved the CPU
  time).

**Build/toolchain lessons**
- Keep standard-library headers (`<cstring>`, `<thread>`, …) out of `.cu`
  files — nvcc's frontend chokes on them with some MSVC versions. Put plain C++
  in `.cpp`, CUDA in `.cu`.
- On Windows, nvcc needs the **64-bit** `cl.exe`; a 32-bit developer prompt
  causes a `size_t` redeclaration error. `build.bat` loads the x64 environment
  automatically to avoid this.

---

## 6. Reproduce

```
cuda-hpc\01_parallel_ode_integrator\build.bat     # compile (loads x64 toolchain)
cuda-hpc\01_parallel_ode_integrator\run.bat       # run + auto-plot + open graph
```

`run.bat` runs `benchmark.exe`, which writes `results.csv`, calls
`plot_results.py` to render `benchmark.png`, and opens it.

## 6b. Extensions: kernel timing & RK4

Two experiments confirm the analysis above (regenerated whenever you run the
benchmark):

- **Kernel vs transfer (CUDA events).** `integrate_gpu` optionally times *just*
  the kernel with CUDA events, separately from the `std::chrono` total that also
  includes the PCIe copies. On the main graph the **GPU-kernel-only** line sits
  far below the **GPU-total** line, and the gap between them *is* the memory
  transfer cost — direct proof that at large n this problem is transfer-bound,
  not compute-bound.

- **RK4 raises the speedup.** Classic 4th-order Runge-Kutta does 4 derivative
  evaluations per step instead of Euler's 1 — 4× the arithmetic for the same
  data transfer. Higher arithmetic intensity means more compute to hide behind
  the transfer, so the GPU speedup *increases* vs Euler (see
  `speedup_comparison.png`). This is the lever that matters for real workloads:
  the GPU wins biggest when there's plenty of math per byte moved.

See [LESSONS.md](LESSONS.md) for a concept-by-concept FAQ.

## 7. Possible next steps

- Swap Euler for **RK4** — 4× the arithmetic per step raises the compute-to-
  transfer ratio and should push the speedup past 900×.
- Separate kernel time from transfer time with **CUDA events** to see the
  `Θ(n)` bus cost directly.
- Compare `float` vs `double` for accuracy vs speed.
