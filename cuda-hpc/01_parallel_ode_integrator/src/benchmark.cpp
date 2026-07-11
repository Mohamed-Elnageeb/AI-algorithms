#include <cstdio>
#include <vector>
#include <chrono>
#include <cmath>

#include "ode_solver.h"

// Fill n oscillators with simple, repeatable test data (no randomness so the
// CPU and GPU runs start from identical inputs and must produce identical output).
static void make_data(std::vector<OscillatorState>& states,
                      std::vector<OscillatorParams>& params, int n) {
    states.resize(n);
    params.resize(n);
    for (int i = 0; i < n; i++) {
        states[i].x = 1.0f + (i % 10) * 0.1f;  // some spread of start positions
        states[i].v = 0.0f;                     // start at rest
        params[i].omega = 1.0f + (i % 5) * 0.05f;
        params[i].zeta  = 0.05f;                // lightly damped
    }
}

int main() {
    const float dt = 0.001f;
    const int num_steps = 1000;
    const int sizes[] = {1000, 10000, 100000, 1000000};

    // Warm-up: the very first CUDA call pays a one-time setup cost (creating the
    // GPU context). Do one throwaway GPU run first so it doesn't pollute the
    // timing of the real n=1000 case.
    {
        std::vector<OscillatorState> ws;
        std::vector<OscillatorParams> wp;
        make_data(ws, wp, 1000);
        integrate_gpu(ws.data(), wp.data(), 1000, dt, num_steps);
    }

    printf("%12s %12s %12s %12s %10s\n", "n", "cpu_ms", "gpu_ms", "speedup", "match");
    printf("------------------------------------------------------------\n");

    for (int n : sizes) {
        // Same starting data for both, so we can compare their results.
        std::vector<OscillatorState> s_cpu, s_gpu;
        std::vector<OscillatorParams> p;
        make_data(s_cpu, p, n);
        s_gpu = s_cpu;  // exact copy of the initial states

        // --- time the CPU version ---
        auto t0 = std::chrono::steady_clock::now();
        integrate_cpu(s_cpu.data(), p.data(), n, dt, num_steps);
        auto t1 = std::chrono::steady_clock::now();
        double cpu_ms = std::chrono::duration<double, std::milli>(t1 - t0).count();

        // --- time the GPU version ---
        // Note: integrate_gpu ends with a Device->Host cudaMemcpy, which blocks
        // until the GPU has finished, so by the time it returns the work is done
        // and the timing is accurate (no extra synchronize needed).
        auto g0 = std::chrono::steady_clock::now();
        integrate_gpu(s_gpu.data(), p.data(), n, dt, num_steps);
        auto g1 = std::chrono::steady_clock::now();
        double gpu_ms = std::chrono::duration<double, std::milli>(g1 - g0).count();

        // --- correctness: largest difference between CPU and GPU results ---
        double max_err = 0.0;
        for (int i = 0; i < n; i++) {
            max_err = fmax(max_err, fabs(s_cpu[i].x - s_gpu[i].x));
            max_err = fmax(max_err, fabs(s_cpu[i].v - s_gpu[i].v));
        }
        const char* match = (max_err < 1e-3) ? "OK" : "FAIL";

        printf("%12d %12.2f %12.2f %11.1fx %10s\n",
               n, cpu_ms, gpu_ms, cpu_ms / gpu_ms, match);
    }
    return 0;
}
