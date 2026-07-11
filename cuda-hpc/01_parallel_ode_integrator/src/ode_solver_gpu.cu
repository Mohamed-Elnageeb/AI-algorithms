#include "ode_solver.h"

// --- Kernels: one thread per oscillator, each runs num_steps in registers ---

// Semi-implicit (symplectic) Euler.
__global__ void integrate_kernel(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
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

// Classic 4th-order Runge-Kutta (same math as integrate_cpu_rk4).
__global__ void integrate_kernel_rk4(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    OscillatorState& s = states[i];
    const OscillatorParams& p = params[i];
    const float tzw = 2.0f * p.zeta * p.omega;
    const float w2  = p.omega * p.omega;
    const float h   = dt;

    for (int j = 0; j < num_steps; j++)
    {
        float x = s.x, v = s.v;
        float dx1 = v,             dv1 = -tzw * v  - w2 * x;
        float x2 = x + 0.5f*h*dx1, v2 = v + 0.5f*h*dv1;
        float dx2 = v2,            dv2 = -tzw * v2 - w2 * x2;
        float x3 = x + 0.5f*h*dx2, v3 = v + 0.5f*h*dv2;
        float dx3 = v3,            dv3 = -tzw * v3 - w2 * x3;
        float x4 = x + h*dx3,      v4 = v + h*dv3;
        float dx4 = v4,            dv4 = -tzw * v4 - w2 * x4;

        s.x = x + (h / 6.0f) * (dx1 + 2.0f*dx2 + 2.0f*dx3 + dx4);
        s.v = v + (h / 6.0f) * (dv1 + 2.0f*dv2 + 2.0f*dv3 + dv4);
    }
}

// --- Host wrapper: the malloc -> copy -> launch -> copy-back -> free dance,
//     shared by both integrators. `launch` runs the chosen kernel; if
//     kernel_ms != nullptr we time just the kernel with CUDA events. ---
template <class Launch>
static void run_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float* kernel_ms, Launch launch) {
    size_t states_bytes = n * sizeof(OscillatorState);
    size_t params_bytes = n * sizeof(OscillatorParams);

    OscillatorState*  d_states;
    OscillatorParams* d_params;
    cudaMalloc(&d_states, states_bytes);
    cudaMalloc(&d_params, params_bytes);

    cudaMemcpy(d_states, states, states_bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_params, params, params_bytes, cudaMemcpyHostToDevice);

    int threads = 256;                          // threads per block (see notes)
    int blocks  = (n + threads - 1) / threads;  // enough blocks to cover all n

    // Optionally time ONLY the kernel (not the transfers) with GPU events.
    cudaEvent_t t0, t1;
    if (kernel_ms) {
        cudaEventCreate(&t0);
        cudaEventCreate(&t1);
        cudaEventRecord(t0);
    }

    launch(blocks, threads, d_states, d_params);

    if (kernel_ms) {
        cudaEventRecord(t1);
        cudaEventSynchronize(t1);               // wait for the kernel to finish
        cudaEventElapsedTime(kernel_ms, t0, t1);
        cudaEventDestroy(t0);
        cudaEventDestroy(t1);
    }

    cudaMemcpy(states, d_states, states_bytes, cudaMemcpyDeviceToHost);
    cudaFree(d_states);
    cudaFree(d_params);
}

void integrate_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps, float* kernel_ms) {
    run_gpu(states, params, n, kernel_ms,
            [=](int blocks, int threads, OscillatorState* ds, OscillatorParams* dp) {
                integrate_kernel<<<blocks, threads>>>(ds, dp, n, dt, num_steps);
            });
}

void integrate_gpu_rk4(OscillatorState* states, const OscillatorParams* params,
                        int n, float dt, int num_steps, float* kernel_ms) {
    run_gpu(states, params, n, kernel_ms,
            [=](int blocks, int threads, OscillatorState* ds, OscillatorParams* dp) {
                integrate_kernel_rk4<<<blocks, threads>>>(ds, dp, n, dt, num_steps);
            });
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
