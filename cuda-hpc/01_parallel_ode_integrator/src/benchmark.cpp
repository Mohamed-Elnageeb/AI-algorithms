#include <cstdio>
#include <cstdlib>   // system()
#include <string>
#include <vector>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <thread>    // hardware_concurrency (for the info line only)

#ifdef _WIN32
#include <windows.h>  // GetModuleFileNameA
#endif

#include "ode_solver.h"

// Directory this executable lives in, so results.csv and the plot script are
// found no matter which folder the program is launched from.
static std::string exe_dir(const char* argv0) {
    std::string path;
#ifdef _WIN32
    char buf[1024];
    DWORD len = GetModuleFileNameA(NULL, buf, sizeof(buf));
    path.assign(buf, len);
#else
    path = argv0 ? argv0 : "";
#endif
    size_t slash = path.find_last_of("/\\");
    return (slash == std::string::npos) ? std::string(".") : path.substr(0, slash);
}

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

// Run `run` K times (calling `reset` before each, un-timed) and return the
// median elapsed time in ms. Median throws away the occasional slow run caused
// by the OS scheduler, which matters a lot for the tiny-n cases.
template <class Reset, class Run>
static double median_ms(Reset reset, Run run, int K) {
    std::vector<double> times;
    for (int k = 0; k < K; k++) {
        reset();
        auto a = std::chrono::steady_clock::now();
        run();
        auto b = std::chrono::steady_clock::now();
        times.push_back(std::chrono::duration<double, std::milli>(b - a).count());
    }
    std::sort(times.begin(), times.end());
    return times[times.size() / 2];
}

int main(int argc, char** argv) {
    const float dt = 0.001f;
    const int num_steps = 1000;
    // Log-spaced (~3x) sweep, tiny -> 1 million, so we see both the CPU->GPU
    // crossover and the GPU's flat region.
    const int sizes[] = {1, 3, 10, 30, 100, 300, 1000, 3000,
                         10000, 30000, 100000, 300000, 1000000};

    const std::string dir = exe_dir(argv[0]);

    // --- hardware info ---
    DeviceInfo dev;
    get_device_info(&dev);
    unsigned cpu_threads = std::thread::hardware_concurrency();

    printf("GPU: %s  |  %d SMs x %d = %d CUDA cores  |  %.1f GB\n",
           dev.name, dev.sms, dev.cores_per_sm, dev.total_cores, dev.mem_gb);
    printf("CPU baseline: single-threaded (machine has %u logical cores)\n", cpu_threads);
    printf("steps per run: %d\n\n", num_steps);

    // Warm-up: the very first CUDA call pays a one-time setup cost (creating the
    // GPU context). Do one throwaway GPU run so it doesn't pollute the timings.
    {
        std::vector<OscillatorState> ws;
        std::vector<OscillatorParams> wp;
        make_data(ws, wp, 1000);
        integrate_gpu(ws.data(), wp.data(), 1000, dt, num_steps);
    }

    // Write results.csv next to the executable. The leading "# key,value" lines
    // carry the hardware specs so the graph can label itself.
    std::string csv_path = dir + "/results.csv";
    FILE* csv = fopen(csv_path.c_str(), "w");
    fprintf(csv, "# gpu_name,%s\n", dev.name);
    fprintf(csv, "# gpu_cores,%d\n", dev.total_cores);
    fprintf(csv, "# gpu_sms,%d\n", dev.sms);
    fprintf(csv, "# cpu_threads,%u\n", cpu_threads);
    fprintf(csv, "# num_steps,%d\n", num_steps);
    fprintf(csv, "n,cpu_ms,gpu_ms,speedup,match\n");

    printf("%12s %12s %12s %12s %10s\n", "n", "cpu_ms", "gpu_ms", "speedup", "match");
    printf("------------------------------------------------------------\n");

    for (int n : sizes) {
        std::vector<OscillatorState> s0;
        std::vector<OscillatorParams> p;
        make_data(s0, p, n);

        // More repeats for small n (noisy, cheap); fewer for big n (stable, slow).
        int K = (n <= 1000) ? 9 : (n <= 100000 ? 3 : 1);

        std::vector<OscillatorState> work;
        double cpu_ms = median_ms(
            [&]() { work = s0; },
            [&]() { integrate_cpu(work.data(), p.data(), n, dt, num_steps); }, K);
        std::vector<OscillatorState> cpu_result = work;  // reference answer

        double gpu_ms = median_ms(
            [&]() { work = s0; },
            [&]() { integrate_gpu(work.data(), p.data(), n, dt, num_steps); }, K);
        std::vector<OscillatorState> gpu_result = work;

        // Correctness: GPU result must match the single-core reference.
        double max_err = 0.0;
        for (int i = 0; i < n; i++) {
            max_err = fmax(max_err, fabs(cpu_result[i].x - gpu_result[i].x));
            max_err = fmax(max_err, fabs(cpu_result[i].v - gpu_result[i].v));
        }
        const char* match = (max_err < 1e-3) ? "OK" : "FAIL";

        printf("%12d %12.3f %12.3f %11.1fx %10s\n",
               n, cpu_ms, gpu_ms, cpu_ms / gpu_ms, match);
        fprintf(csv, "%d,%.4f,%.4f,%.3f,%s\n",
                n, cpu_ms, gpu_ms, cpu_ms / gpu_ms, match);
    }

    fclose(csv);
    printf("\nWrote %s\n", csv_path.c_str());

    // Automatically render and open the graph. Invoke the script by its full
    // path (next to this exe) so it works from any working directory. Needs
    // Python + matplotlib; if missing, this just prints a message and the run
    // still counts as successful.
    printf("Plotting results...\n");
    std::string script = "\"" + dir + "/plot_results.py\"";
    if (system(("python " + script).c_str()) != 0)
        system(("python3 " + script).c_str());

    return 0;
}
