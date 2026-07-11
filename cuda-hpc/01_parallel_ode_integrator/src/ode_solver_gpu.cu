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

    // --- 5. Return the desks ---
    cudaFree(d_states);
    cudaFree(d_params);
}


// Number of CUDA cores per SM for each GPU architecture ("compute capability").
// This ratio is fixed by the hardware design and isn't reported by the driver,
// so we look it up. Values from NVIDIA's helper_cuda.h.
static int cores_per_sm(int major, int minor) {
    int sm = (major << 4) + minor;   // e.g. 7.5 -> 0x75
    switch (sm) {
        case 0x30: case 0x32: case 0x35: case 0x37: return 192;  // Kepler
        case 0x50: case 0x52: case 0x53:            return 128;  // Maxwell
        case 0x60:                                  return  64;  // Pascal GP100
        case 0x61: case 0x62:                       return 128;  // Pascal
        case 0x70: case 0x72: case 0x75:            return  64;  // Volta / Turing (RTX 2080)
        case 0x80:                                  return  64;  // Ampere A100
        case 0x86: case 0x87: case 0x89:            return 128;  // Ampere / Ada
        case 0x90:                                  return 128;  // Hopper
        default:                                    return  64;  // reasonable fallback
    }
}

void get_device_info(DeviceInfo* info) {
    cudaDeviceProp prop;
    cudaGetDeviceProperties(&prop, 0);   // device 0

    // Copy the name by hand rather than pulling <cstring> into this .cu file
    // (a standard-library include here trips an nvcc/MSVC frontend bug).
    int k = 0;
    for (; k < (int)sizeof(info->name) - 1 && prop.name[k] != '\0'; k++)
        info->name[k] = prop.name[k];
    info->name[k] = '\0';

    info->sms          = prop.multiProcessorCount;
    info->cores_per_sm = cores_per_sm(prop.major, prop.minor);
    info->total_cores  = info->sms * info->cores_per_sm;
    info->mem_gb       = prop.totalGlobalMem / 1e9;
}
