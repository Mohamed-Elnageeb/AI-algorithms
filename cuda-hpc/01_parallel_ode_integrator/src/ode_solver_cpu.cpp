#include "ode_solver.h"

void integrate_cpu(OscillatorState* states, const OscillatorParams* params,
                    int n, float dt, int num_steps) {
                        
    for (int i = 0; i < n; i++)
    {
        OscillatorState& s = states[i];
        const OscillatorParams& p = params[i];
        const float two_zeta_omega = 2.0f * p.zeta * p.omega;
        const float omega_sq =  p.omega * p.omega;
        
        for (int j = 0; j < num_steps; j++)
        {
            float a = -two_zeta_omega * s.v - omega_sq * s.x;
            s.v += a * dt;
            s.x += s.v * dt;
        }
        
    }
}
