#include "ode_solver.h"

void integrate_cpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
    // TODO: for each of the n oscillators, run num_steps of explicit Euler:
    //   a = -2*zeta*omega*v - omega^2*x
    //   v += a * dt
    //   x += v * dt
    // Start here — this is the reference implementation the GPU version
    // must match.
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < num_steps; j++)
        {
            float a = -2*params[i].zeta*params[i].omega*states[i].v - params[i].omega*params[i].omega*states[i].x;
            states[i].v += a*dt ;
            states[i].x += states[i].v*dt;
        }
        
    }
}
