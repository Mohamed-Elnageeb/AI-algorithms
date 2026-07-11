#include "ode_solver.h"

__global__ void integrate_kernel(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt,int num_steps) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    OscillatorState& s = states[i];
    const OscillatorParams& p = params[i];
    const float two_zeta_omega = 2.0f * p.zeta * p.omega;
    const float omega_sq =  p.omega * p.omega;
    
    for (int j = 0; i < num_steps; i++)
    {
        float a =  -two_zeta_omega * s.v - omega_sq * s.x;
        s.v += a * dt;
        s.x += s.v * dt;
    }
    }


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
