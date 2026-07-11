# Lessons & FAQ

Concepts and gotchas collected while building this project — brief answers to
the questions that came up along the way.

## CUDA

**Why `threads = 256`?**
Threads in a block run in hardware groups of 32 called **warps**, so the block
size should be a multiple of 32. 256 (= 8 warps) is a common sweet spot: large
enough to keep a streaming multiprocessor busy and hide memory latency, small
enough that many blocks fit on each SM (good "occupancy"). 128/256/512 all work;
256 is a safe default. It isn't magic — you can tune it per kernel/GPU.

**Why one thread per oscillator, and what is the index formula?**
The batch is embarrassingly parallel, so we delete the CPU's outer loop and give
each oscillator its own thread. `int i = blockIdx.x * blockDim.x + threadIdx.x;`
turns each thread's (block number, lane number) into a unique global index
`0…n−1`. `if (i >= n) return;` stops the few extra threads (we usually launch
slightly more than `n`) from touching memory that isn't theirs.

**Why `blocks = (n + threads - 1) / threads`?**
That's integer "round up" (ceil) of `n / threads` — enough blocks to cover every
oscillator, with the last block possibly partly idle (handled by the guard).

**What is `__global__`, and why `void` after it?**
`__global__` marks a **kernel**: GPU code launched from the CPU. `void` is its
return type — kernels can't return a value (which of the thousands of threads
would return it?), so results come back through memory.

**The host/device memory dance**
GPU memory is separate from CPU RAM, so every GPU call does:
`cudaMalloc` → `cudaMemcpy(HostToDevice)` → launch kernel →
`cudaMemcpy(DeviceToHost)` → `cudaFree`.

**Kernel time vs transfer time (CUDA events)**
`std::chrono` around the whole call measures compute **plus** the PCIe copies.
CUDA **events** (`cudaEventRecord`/`cudaEventElapsedTime`) time just the kernel.
The gap between them is the memory-transfer cost — which dominates at large n.

**Why does the speedup drop at very large n?**
This kernel has **low arithmetic intensity**: ~1000 cheap flops per oscillator,
but 24 bytes must cross the PCIe bus. Past a few million oscillators the run is
**transfer-bound**, and bus bandwidth doesn't scale with more cores — so the
per-element cost rises and the speedup falls from its ~940× peak.

**Euler vs RK4**
Semi-implicit Euler does 1 derivative evaluation per step; RK4 does 4 (more
accurate). RK4's extra arithmetic raises the compute-to-transfer ratio, so the
GPU speedup goes **up** — more work to hide the transfer behind.

## C++

**Pointer (`*`) vs reference (`&`)** — a pointer holds an address, can start
empty and be reassigned (needed by `cudaMalloc`, which writes an address into
it). A reference declared with `&` is a permanent alias to an existing object
(great for `OscillatorState& s = states[i];`).

**`size_t`** — the right type for "a number of bytes": non-negative, and 64-bit
on x64. Seeing it declared as 32-bit was the clue the build had a 32-bit
compiler (below).

**`-O2`** — the compiler optimization level. At `-O2` the compiler hoists
loop-invariant math itself, which is why manually pulling constants out of the
inner loop barely changed the CPU time.

**Semi-implicit (symplectic) Euler** — updating `v` before using it to update
`x` conserves energy far better than plain explicit Euler, so oscillators stay
stable over long runs.

**Keep standard headers out of `.cu` files** — including `<cstring>`/`<thread>`
in a `.cu` tripped an nvcc frontend bug with this MSVC version. Rule of thumb:
plain C++ in `.cpp`, CUDA in `.cu`.

## Build / toolchain (Windows)

**The `size_t` redeclaration error** — nvcc builds device code as 64-bit; if it
picks up a **32-bit** `cl.exe` (from the plain "Developer Command Prompt", which
defaults to x86), MSVC headers declare `size_t` as 32-bit and everything breaks.
Use the **x64 Native Tools Command Prompt**, or `build.bat`, which calls
`vcvars64.bat` to load the 64-bit toolchain from any terminal.

## Git

- **Develop on a feature branch**, not `main`; open a PR to merge.
- **`git pull --rebase`** when your branch and the remote have diverged (each has
  commits the other doesn't) — it replays your commits on top of theirs.
- **`git reset --hard`** only undoes changes to **tracked** files; untracked
  files need **`git clean -f -d`** (dry-run first with `-n`).
- **`git add .` grabs everything**, including junk (editor config, build
  output). Prefer naming the file, and keep a good `.gitignore`.
- **`git push --force-with-lease`** safely rewrites a branch you own (e.g. after
  amending a commit) without clobbering someone else's work.
- **PowerShell `>>` writes UTF-16**, which git can't read — that's why the first
  `.gitignore` silently didn't work. Write it as plain ASCII.
- **Verified vs unverified commits** — the "Verified" badge means the commit was
  cryptographically **signed** with a key tied to the author's GitHub account.
  Commits made from an automated environment without your signing key show as
  "Unverified" even when authored in your name. To get verified history: sign
  your own commits (GitHub supports SSH signing), or merge the PR through the
  GitHub web UI (the merge commit is signed by GitHub).
