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

// Advance `n` independent oscillators by `num_steps` of size `dt`, in place.
// CPU reference implementation. TODO: implement in ode_solver_cpu.cpp.
void integrate_cpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps);

// Same contract as integrate_cpu, but runs on the GPU.
// TODO: implement in ode_solver_gpu.cu (host wrapper that launches the kernel).
void integrate_gpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps);
