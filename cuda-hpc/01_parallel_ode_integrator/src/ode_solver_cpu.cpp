#include "ode_solver.h"

void integrate_cpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
    // TODO: for each of the n oscillators, run num_steps of explicit Euler:
    //   a = -2*zeta*omega*v - omega^2*x
    //   v += a * dt
    //   x += v * dt
    // Start here — this is the reference implementation the GPU version
    // must match.
}
