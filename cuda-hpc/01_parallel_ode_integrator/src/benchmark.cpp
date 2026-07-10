#include <cstdio>
#include <vector>

#include "ode_solver.h"

int main() {
    // TODO:
    //   1. For batch sizes n in {1e3, 1e4, 1e5, 1e6}:
    //      - Fill n OscillatorState/OscillatorParams with some fixed seed data.
    //      - Time integrate_cpu(...) (e.g. std::chrono::steady_clock).
    //      - Time integrate_gpu(...) on a copy of the same input.
    //      - Compare CPU vs GPU final states within a tolerance (e.g. 1e-4);
    //        print PASS/FAIL.
    //   2. Print a table: n | cpu_ms | gpu_ms | speedup | correctness.
    std::printf("benchmark scaffold — fill in main() per the TODOs\n");
    return 0;
}
