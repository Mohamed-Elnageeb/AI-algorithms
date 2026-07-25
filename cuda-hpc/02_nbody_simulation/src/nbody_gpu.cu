#include "nbody.h"

// One time step is split into TWO kernels on purpose:
//   1. update velocities  — every thread READS all positions (never writes
//      them), computes its body's acceleration, and updates only its own
//      velocity. Because no thread moves a body here, there is no race.
//   2. update positions   — every thread moves its own body by v*dt.
// Doing both in a single kernel would race: a thread reading position j while
// thread j is writing it would see a half-updated body.

// >>> YOU WRITE THE BODY OF THIS KERNEL <<<
// Same math as integrate_cpu's acceleration step, but for one body i (this
// thread). Loop over all j, accumulate ax/ay/az, then do: v += a * dt.
__global__ void update_velocities(Body* bodies, int n, SimParams p) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;

    // TODO: read bodies[i], loop j = 0..n-1 accumulating acceleration from
    //       bodies[j] (softened gravity), then update bodies[i].vx/vy/vz.
}

// Provided: trivially move each body by its (already updated) velocity.
__global__ void update_positions(Body* bodies, int n, SimParams p) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= n) return;
    bodies[i].x += bodies[i].vx * p.dt;
    bodies[i].y += bodies[i].vy * p.dt;
    bodies[i].z += bodies[i].vz * p.dt;
}

// Provided: the host wrapper (memory dance + step loop + optional timing).
void integrate_gpu(Body* bodies, int n, SimParams p, int num_steps,
                   float* kernel_ms) {
    size_t bytes = n * sizeof(Body);
    Body* d_bodies;
    cudaMalloc(&d_bodies, bytes);
    cudaMemcpy(d_bodies, bodies, bytes, cudaMemcpyHostToDevice);

    int threads = 256;
    int blocks  = (n + threads - 1) / threads;

    cudaEvent_t t0, t1;
    if (kernel_ms) { cudaEventCreate(&t0); cudaEventCreate(&t1); cudaEventRecord(t0); }

    for (int step = 0; step < num_steps; step++) {
        update_velocities<<<blocks, threads>>>(d_bodies, n, p);
        update_positions<<<blocks, threads>>>(d_bodies, n, p);
    }

    if (kernel_ms) {
        cudaEventRecord(t1);
        cudaEventSynchronize(t1);
        cudaEventElapsedTime(kernel_ms, t0, t1);
        cudaEventDestroy(t0); cudaEventDestroy(t1);
    }

    cudaMemcpy(bodies, d_bodies, bytes, cudaMemcpyDeviceToHost);
    cudaFree(d_bodies);
}
