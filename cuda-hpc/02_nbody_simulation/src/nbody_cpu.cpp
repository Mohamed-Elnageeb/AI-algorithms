#include <vector>
#include <cmath>

#include "nbody.h"

// CPU reference: all-pairs gravity, one time step at a time.
//
// >>> YOU WRITE THIS <<<
//
// For each of num_steps steps:
//   1. Compute the acceleration on EVERY body from EVERY other body, using the
//      *current* positions. The gravitational acceleration on body i from body j:
//        dx = bodies[j].x - bodies[i].x     (same for dy, dz)
//        distSqr = dx*dx + dy*dy + dz*dz + p.softening*p.softening
//        invDist  = 1.0f / sqrtf(distSqr)
//        invDist3 = invDist * invDist * invDist
//        ax += p.G * bodies[j].mass * dx * invDist3   (same for ay, az)
//      (Summing j over all bodies including j==i is fine: dx=0 there, so it
//       contributes nothing thanks to the softening term.)
//   2. Only AFTER all accelerations are known, update velocities and positions:
//        v += a * dt;   pos += v * dt      (semi-implicit Euler)
//
// KEY correctness point: compute all accelerations from the OLD positions first
// (store them in a temporary array), THEN move the bodies. If you update
// positions while still looping, later bodies feel forces from already-moved
// ones and the simulation is wrong.
void integrate_cpu(Body* bodies, int n, SimParams p, int num_steps) {
    std::vector<float> ax(n), ay(n), az(n);   // scratch for accelerations

    for (int step = 0; step < num_steps; step++) {
        // TODO 1: fill ax/ay/az from current positions (double loop over i, j).

        // TODO 2: update each body's velocity (v += a*dt) then position (pos += v*dt).
    }
}
