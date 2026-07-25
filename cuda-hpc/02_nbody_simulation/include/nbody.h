#pragma once

// One body in the gravitational N-body simulation.
struct Body {
    float x, y, z;      // position
    float vx, vy, vz;   // velocity
    float mass;
};

// Simulation constants.
struct SimParams {
    float G;          // gravitational constant (1.0 for a toy sim)
    float softening;  // eps: avoids infinite force when two bodies overlap
    float dt;         // timestep
};

// Advance n bodies by num_steps of all-pairs O(n^2) gravity, in place.
// Single-threaded CPU reference.
void integrate_cpu(Body* bodies, int n, SimParams p, int num_steps);

// Same on the GPU (one thread per body). If kernel_ms != nullptr, it receives
// the kernel-only time in ms (CUDA events), excluding host<->device transfers.
void integrate_gpu(Body* bodies, int n, SimParams p, int num_steps,
                   float* kernel_ms = nullptr);
