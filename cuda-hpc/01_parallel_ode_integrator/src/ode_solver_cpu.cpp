#include <algorithm>
#include <thread>
#include <vector>

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

// Multi-core baseline: cut the oscillator array into num_threads slices and
// run integrate_cpu on each slice in its own thread. Safe because every
// oscillator is independent — no two threads ever touch the same element.
void integrate_cpu_parallel(OscillatorState* states, const OscillatorParams* params,
                            int n, float dt, int num_steps, int num_threads) {
    if (num_threads <= 0) num_threads = (int)std::thread::hardware_concurrency();
    if (num_threads < 1) num_threads = 1;

    int chunk = (n + num_threads - 1) / num_threads;  // ceil(n / num_threads)
    std::vector<std::thread> workers;
    for (int t = 0; t < num_threads; t++) {
        int begin = t * chunk;
        int end   = std::min(n, begin + chunk);
        if (begin >= end) break;  // more threads than work
        // states + begin is pointer arithmetic: "the array starting at
        // element begin" — so each thread sees its slice as a small array.
        workers.emplace_back(integrate_cpu, states + begin, params + begin,
                             end - begin, dt, num_steps);
    }
    for (auto& w : workers) w.join();  // wait for all slices to finish
}
