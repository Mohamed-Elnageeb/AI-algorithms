#include "ode_solver.h"

__global__ void integrate_kernel(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt,int num_steps) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    OscillatorState& s = states[i];
    const OscillatorParams& p = params[i];
    const float two_zeta_omega = 2.0f * p.zeta * p.omega;
    const float omega_sq =  p.omega * p.omega;
    
    for (int j = 0; j < num_steps; j++)
    {
        float a =  -two_zeta_omega * s.v - omega_sq * s.x;
        s.v += a * dt;
        s.x += s.v * dt;
    }
    }


void integrate_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
    // --- 1. Rent GPU desk space. 'd_' = "device" (lives on GPU) ---
    size_t states_bytes = n * sizeof(OscillatorState);
    size_t params_bytes = n * sizeof(OscillatorParams);
    OscillatorState* d_states;
    OscillatorParams* d_params; 
    cudaMalloc(&d_states, states_bytes);
    cudaMalloc(&d_params, params_bytes);

    // --- 2. Mail data CPU -> GPU ---
    cudaMemcpy(d_states, states, states_bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_params, params, params_bytes, cudaMemcpyHostToDevice); 

    // --- 3. Launch the workers ---
    int threads = 256; 
    int blocks = (n + threads - 1) / threads; //enough blocks to cover all n
    integrate_kernel<<<blocks, threads>>>(d_states, d_params, n, dt, num_steps);

    // --- 4. Mail results GPU -> CPU (direction flips!) ---
    cudaMemcpy(states, d_states, states_bytes, cudaMemcpyDeviceToHost);
    cudaMemcpy(params, d_params, params_bytes, cudaMemcpyDeviceToHost); 

    // --- 5. Return the desks ---
    cudaFree(d_states);
    cudaFree(d_params);
}
