#include <cstdio>
#include <vector>
#include <chrono>
#include <cmath>

#include "nbody.h"

// Deterministic pseudo-random bodies (no <random> needed): a tiny hash of the
// index, so CPU and GPU start from identical data.
static void make_bodies(std::vector<Body>& b, int n) {
    b.resize(n);
    for (int i = 0; i < n; i++) {
        unsigned h = i * 2654435761u;           // Knuth multiplicative hash
        auto f = [&](int shift) {               // -> roughly [-1, 1)
            return ((h >> shift) & 1023) / 512.0f - 1.0f;
        };
        b[i].x = f(0);  b[i].y = f(10); b[i].z = f(20);
        b[i].vx = 0; b[i].vy = 0; b[i].vz = 0;
        b[i].mass = 1.0f;
    }
}

int main() {
    SimParams p{ /*G*/ 1.0f, /*softening*/ 0.1f, /*dt*/ 0.001f };
    const int num_steps = 10;
    const int sizes[] = {128, 256, 512, 1024, 2048, 4096, 8192, 16384};

    // Warm-up so CUDA context creation doesn't pollute the first timing.
    { std::vector<Body> w; make_bodies(w, 256); integrate_gpu(w.data(), 256, p, 1); }

    printf("%10s %12s %12s %12s %10s\n", "n", "cpu_ms", "gpu_ms", "speedup", "match");
    printf("------------------------------------------------------------\n");

    for (int n : sizes) {
        std::vector<Body> b0; make_bodies(b0, n);

        std::vector<Body> cpu = b0;
        auto c0 = std::chrono::steady_clock::now();
        integrate_cpu(cpu.data(), n, p, num_steps);
        auto c1 = std::chrono::steady_clock::now();
        double cpu_ms = std::chrono::duration<double, std::milli>(c1 - c0).count();

        std::vector<Body> gpu = b0;
        auto g0 = std::chrono::steady_clock::now();
        integrate_gpu(gpu.data(), n, p, num_steps);
        auto g1 = std::chrono::steady_clock::now();
        double gpu_ms = std::chrono::duration<double, std::milli>(g1 - g0).count();

        // Loose tolerance: CPU and GPU sum the forces in different orders, and
        // float addition isn't associative, so exact equality isn't expected.
        double max_err = 0.0;
        for (int i = 0; i < n; i++) {
            max_err = fmax(max_err, fabs(cpu[i].x - gpu[i].x));
            max_err = fmax(max_err, fabs(cpu[i].y - gpu[i].y));
            max_err = fmax(max_err, fabs(cpu[i].z - gpu[i].z));
        }
        const char* match = (max_err < 1e-2) ? "OK" : "FAIL";

        printf("%10d %12.3f %12.3f %11.1fx %10s\n",
               n, cpu_ms, gpu_ms, cpu_ms / gpu_ms, match);
    }
    return 0;
}
