#pragma once

// State of a single damped harmonic oscillator: x'' + 2*zeta*omega*x' + omega^2*x = 0
struct OscillatorState {
    float x;   // position
    float v;   // velocity
};

struct OscillatorParams {
    float omega;  // natural frequency
    float zeta;   // damping ratio
};

// --- semi-implicit (symplectic) Euler: 1 derivative evaluation per step ---

// Advance `n` independent oscillators by `num_steps` of size `dt`, in place.
// Single-threaded CPU reference implementation.
void integrate_cpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps);

// Same contract as integrate_cpu, but runs on the GPU. If kernel_ms != nullptr,
// it is filled with the kernel-only time in milliseconds (measured with CUDA
// events), i.e. excluding the host<->device memory transfers.
void integrate_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps, float* kernel_ms = nullptr);

// --- classic 4th-order Runge-Kutta: 4 derivative evaluations per step ---
// Same interface as the Euler versions; ~4x the arithmetic per step, so a more
// accurate integrator and a higher arithmetic intensity (more compute per byte).

void integrate_cpu_rk4(OscillatorState* states, const OscillatorParams* params,
                        int n, float dt, int num_steps);

void integrate_gpu_rk4(OscillatorState* states, const OscillatorParams* params,
                        int n, float dt, int num_steps, float* kernel_ms = nullptr);

// Hardware description of the active CUDA device, filled by get_device_info.
// Lives here (and is implemented in the .cu) so benchmark.cpp can print the
// specs without needing to include any CUDA headers itself.
struct DeviceInfo {
    char   name[256];    // e.g. "NVIDIA GeForce RTX 2080"
    int    sms;          // number of streaming multiprocessors
    int    cores_per_sm; // CUDA cores per SM (depends on architecture)
    int    total_cores;  // sms * cores_per_sm
    double mem_gb;       // total device memory in GB
};

void get_device_info(DeviceInfo* info);
