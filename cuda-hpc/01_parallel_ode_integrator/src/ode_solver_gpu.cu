#include "ode_solver.h"

// TODO: write __global__ void integrate_kernel(...) here.
//   - One thread handles one oscillator (index = blockIdx.x * blockDim.x + threadIdx.x).
//   - Guard against index >= n.
//   - Same Euler update as the CPU version, looped num_steps times inside the kernel
//     (so we only pay one kernel-launch overhead for the whole run).

void integrate_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
    // TODO:
    //   1. cudaMalloc device buffers for states and params.
    //   2. cudaMemcpy host -> device.
    //   3. Launch integrate_kernel<<<blocks, threads>>>(...).
    //   4. cudaMemcpy device -> host (results back into `states`).
    //   5. cudaFree device buffers.
    //   6. Check every CUDA call's return value.
}
