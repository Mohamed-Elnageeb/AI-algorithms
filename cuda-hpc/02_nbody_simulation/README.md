# GPU N-body Simulation

Simulate `n` gravitating bodies with all-pairs (O(n²)) forces, on a single CPU
core and on the GPU (one thread per body), and compare wall-clock time as `n`
grows. This reuses the CUDA workflow from project 01 and adds the key new idea:
**each body interacts with every other**, so there's O(n²) work to parallelise.

## The physics

Softened gravitational acceleration on body *i*:

```
a_i = Σ_j  G · m_j · (r_j − r_i) / (|r_j − r_i|² + ε²)^(3/2)
```

The softening `ε` keeps the force finite when two bodies nearly coincide.
Integrated with semi-implicit Euler (`v += a·dt; pos += v·dt`).

## Status: scaffold — you write the core

- `src/nbody_cpu.cpp` — **TODO:** the double loop (accelerations from old
  positions, then move the bodies).
- `src/nbody_gpu.cu` — **TODO:** the body of `update_velocities` (one thread's
  force loop). The rest (position kernel, host wrapper, timing) is provided.
- Everything else (benchmark, build) is ready.

Why two GPU kernels per step? A thread must read every position while computing
its force, so no thread may *move* a body during that pass — velocities are
updated first (positions read-only), positions second. See the comments in the
`.cu`.

## Build & run (Windows)

```
cuda-hpc\02_nbody_simulation\build.bat
cuda-hpc\02_nbody_simulation\nbody.exe
```

Or with CMake: `cmake -B build -S cuda-hpc && cmake --build build`.

## Next, once it's correct

- Add `results.csv` + a plot (like project 01).
- Optimise the kernel with **shared-memory tiling**: load a tile of bodies into
  fast shared memory so each is read once per tile instead of once per thread —
  the classic N-body speedup.
