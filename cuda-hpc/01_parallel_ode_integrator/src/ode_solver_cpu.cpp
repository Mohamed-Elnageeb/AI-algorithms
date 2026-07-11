#include "ode_solver.h"

// Semi-implicit (symplectic) Euler: update v from the current state, then use
// the new v to update x. One derivative evaluation per step.
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

// Classic 4th-order Runge-Kutta on the system y = (x, v), with
//   dx/dt = v,   dv/dt = -2*zeta*omega*v - omega^2*x.
// Four derivative evaluations per step -> more accurate, ~4x the arithmetic.
void integrate_cpu_rk4(OscillatorState* states, const OscillatorParams* params,
                        int n, float dt, int num_steps) {
    for (int i = 0; i < n; i++)
    {
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
}
